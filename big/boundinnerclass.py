#!/usr/bin/env python3

"""
boundinnerclass - Bind inner classes to outer instances.

If you have a class with an inner class inside, decorate the inner class
with @BoundInnerClass and it will automatically receive the outer instance
as a second parameter to __init__ (after self).

    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

    o = Outer()
    i = o.Inner()  # outer is passed automatically!

Thanks to Alex Martelli for showing how this could be done back in 2010:
https://stackoverflow.com/questions/2278426/inner-classes-how-can-i-get-the-outer-class-object-at-construction-time
"""

_license = """
big
Copyright 2022-2026 Larry Hastings
All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import inspect
import weakref

import sys
_python_3_7_plus = (sys.version_info.major > 3) or ((sys.version_info.major == 3) and (sys.version_info.minor >= 7))

__all__ = []

def export_name(name):
    __all__.append(name)

def export(o):
    export_name(o.__name__)
    return o



def _make_bound_signature(original_init):
    """
    Create a signature for a bound class's __init__, removing 'outer'.

    The bound wrapper injects 'outer' automatically,
    so the user-facing signature should not include it.
    """
    try:
        sig = inspect.signature(original_init)
    except (ValueError, TypeError):
        return None

    params = list(sig.parameters.values())

    # Remove 'self' (first param) and 'outer' (second param)
    # Keep everything else
    if len(params) >= 2:
        bound_params = params[2:]  # Skip self and outer
    else:
        bound_params = []

    return inspect.Signature(bound_params, return_annotation=sig.return_annotation)


class _ClassProxy:
    """
    A minimal transparent proxy for class objects.

    Forwards attribute access to the wrapped class while allowing
    the proxy itself to act as a descriptor.

    Inspired by wrapt.ObjectProxy, but much simpler--we only need to
    proxy classes, not arbitrary objects with arithmetic operators, etc.

    Note: __qualname__ and __annotations__ can't be properties in Python,
    so we copy them as actual attributes and handle them explicitly in
    __getattr__/__setattr__.
    """

    if _python_3_7_plus:
        __slots__ = ( '__annotations__', '__qualname__', '__wrapped__' )
    else: # pragma: nocover
        __slots__ = ( '__annotations__', '__wrapped__' )

    def __init__(self, wrapped):
        object.__setattr__(self, '__wrapped__', wrapped)
        # These must be actual attributes, not properties
        try:
            object.__setattr__(self, '__qualname__', wrapped.__qualname__)
        except AttributeError:
            pass
        try:
            object.__setattr__(self, '__annotations__', wrapped.__annotations__)
        except AttributeError:
            pass

    # Forward class identity attributes as properties (read-only via property,
    # write via __setattr__ which forwards to wrapped)
    # Note: __qualname__ and __annotations__ are handled as slots since Python
    # doesn't allow them to be properties.

    @property
    def __name__(self):
        return self.__wrapped__.__name__

    @property
    def __module__(self):
        return self.__wrapped__.__module__

    @property
    def __doc__(self):
        return self.__wrapped__.__doc__

    # Proxy behavior

    def __repr__(self):
        return f"<{type(self).__name__} for {self.__wrapped__!r}>"

    def __getattr__(self, name):
        return getattr(self.__wrapped__, name)

    def __setattr__(self, name, value):
        if name == '__wrapped__':
            object.__setattr__(self, name, value)
            # Update cached copies
            try:
                object.__setattr__(self, '__qualname__', value.__qualname__)
            except AttributeError:
                pass
            try:
                object.__setattr__(self, '__annotations__', value.__annotations__)
            except AttributeError:
                pass
        elif name == '__annotations__':
            object.__setattr__(self, name, value)
            self.__wrapped__.__annotations__ = value
        elif _python_3_7_plus and (name == '__qualname__'):
            object.__setattr__(self, name, value)
            self.__wrapped__.__qualname__ = value
        else:
            # Forward to wrapped object (handles __name__, __module__, __doc__, etc.)
            setattr(self.__wrapped__, name, value)

    def __delattr__(self, name):
        delattr(self.__wrapped__, name)

    # Make subclassing work: class Child(Outer.Inner) should use the wrapped class
    def __mro_entries__(self, bases):
        return (self.__wrapped__,)

    # Backward compatibility: .cls returns the wrapped class
    # Used when subclassing inside the outer class: class Child(Parent.cls)
    @property
    def cls(self):
        return self.__wrapped__

    # isinstance/issubclass support
    def __instancecheck__(self, instance):
        return isinstance(instance, self.__wrapped__)

    def __subclasscheck__(self, subclass):
        if hasattr(subclass, '__wrapped__'):
            return issubclass(subclass.__wrapped__, self.__wrapped__)
        return issubclass(subclass, self.__wrapped__)


# Storage attribute name for bound inner classes cache.
# If you use bound inner classes inside a class using slots,
# add BOUNDINNERCLASS_SLOTS to your slots declaration:
#
# class Foo:
#     __slots__ = ('x', 'y', 'z') + BOUNDINNERCLASS_SLOTS
BOUNDINNERCLASS_ATTR = '__bound_inner_classes__'
export_name('BOUNDINNERCLASS_ATTR')
BOUNDINNERCLASS_SLOTS = (BOUNDINNERCLASS_ATTR,)
export_name('BOUNDINNERCLASS_SLOTS')


def _get_cache(outer):
    """Get or create the bound inner classes cache dict on outer."""
    cache = getattr(outer, BOUNDINNERCLASS_ATTR, None)
    if cache is None:
        cache = {}
        # Try to set it - will fail if outer uses __slots__ without this attr
        try:
            object.__setattr__(outer, BOUNDINNERCLASS_ATTR, cache)
        except AttributeError:
            # outer uses __slots__ and doesn't have __bound_inner_classes__
            # (If outer had __dict__, object.__setattr__ would have succeeded)
            raise TypeError(
                f"Cannot cache bound inner class on {type(outer).__name__}. "
                f"Add '{BOUNDINNERCLASS_ATTR}' to __slots__ or include '__dict__'."
            ) from None
    return cache


class _BoundInnerClassBase(_ClassProxy):
    """
    Base descriptor for bound inner classes.

    Subclasses implement _wrap() to define how the wrapper class is created.
    """

    __slots__ = ()

    def __get__(self, outer, outer_class):
        # Accessed via class (Outer.Inner) - return unwrapped class
        if outer is None:
            return self.__wrapped__

        # Accessed via instance (o.Inner) - return bound version
        name = self.__wrapped__.__name__
        cache = _get_cache(outer)

        # Check cache
        cached = cache.get(name)
        if cached is not None:
            return cached

        # Build wrapper bases, handling inheritance from other BoundInnerClasses
        # The wrapper inherits from self.__wrapped__ first (for __init__ signature),
        # then from bound versions of parent BoundInnerClasses (for MRO chaining)
        wrapper_bases = [self.__wrapped__]

        for base in self.__wrapped__.__bases__:
            # Skip if same name as us (would cause infinite recursion)
            if base.__name__ == name:
                continue

            bound_inner_base = getattr(outer, base.__name__, None)
            if bound_inner_base:
                bases = getattr(bound_inner_base, '__bases__', (None,))
                # The unbound class is always the first base of bound inner class
                if bases[0] == base:
                    # Add bound version for MRO chaining
                    wrapper_bases.append(bound_inner_base)

        # Create the wrapper - always use self.__wrapped__ as base
        Wrapper = self._wrap(outer, self.__wrapped__)
        Wrapper.__name__ = name

        # Set bases if we have bound parents to include
        if len(wrapper_bases) > 1:
            Wrapper.__bases__ = tuple(wrapper_bases)

        # Cache and return
        cache[name] = Wrapper
        return Wrapper

    def _wrap(self, outer, base):
        """Create the wrapper class. Override in subclasses."""
        raise NotImplementedError


@export
class BoundInnerClass(_BoundInnerClassBase):
    """
    Class decorator for an inner class.  When accessing the inner class
    through an instance of the outer class, this decorator "binds" the
    inner class to that instance. This changes the signature of the inner
    class's __init__ from

        def __init__(self, *args, **kwargs):

    to

        def __init__(self, outer, *args, **kwargs):

    where "outer" is the instance of the outer class.

    Note that this has implications for all subclasses. If class B is
    decorated with BoundInnerClass, and class S is a subclass of B,
    such that issubclass(S, B) returns True, class S must be decorated
    with either @BoundInnerClass or @UnboundInnerClass.

    How does it work?  The decorator returns a proxy for the class
    that implements the descriptor protocol; when you access this
    proxy through an instance, the descriptor creates a custom subclass
    with a custom __init__.  This __init__ is a closure with a reference
    to the instance, and it passes that instance in as an argument to
    the base class's __init__.
    """

    __slots__ = ()

    def _wrap(self, outer, base):
        outer_weakref = weakref.ref(outer)
        cls = self.__wrapped__

        class Wrapper(base):
            def __init__(self, *args, **kwargs):
                # Call cls.__init__ directly, not super().__init__
                # This avoids multiple outer injections when inheriting
                # from other BoundInnerClasses
                cls.__init__(self, outer_weakref(), *args, **kwargs)

            # Custom repr if the wrapped class doesn't have one
            if cls.__repr__ is object.__repr__:
                def __repr__(self):
                    return "".join([
                        "<",
                        cls.__module__,
                        ".",
                        self.__class__.__name__,
                        " object bound to ",
                        repr(outer_weakref()),
                        " at ",
                        hex(id(self)),
                        ">",
                    ])

        Wrapper.__name__ = cls.__name__
        Wrapper.__module__ = cls.__module__
        Wrapper.__qualname__ = cls.__qualname__
        Wrapper.__doc__ = cls.__doc__
        if hasattr(cls, '__annotations__'):
            Wrapper.__annotations__ = cls.__annotations__

        # Set proper signature (without 'outer' param since it's injected)
        bound_signature = _make_bound_signature(cls.__init__)
        if bound_signature is not None:
            Wrapper.__signature__ = bound_signature
            Wrapper.__init__.__signature__ = bound_signature

        return Wrapper


@export
class UnboundInnerClass(_BoundInnerClassBase):
    """
    Class decorator for an inner class that prevents binding
    the inner class to an instance of the outer class.  In short,
    undoes the effect of @BoundInnerClass for a subclass.

    If class B is decorated with BoundInnerClass,
    and class S is a subclass of B, such that issubclass(S, B)
    returns True, class S must be decorated with either
    @BoundInnerClass or @UnboundInnerClass.
    """

    __slots__ = ()

    def _wrap(self, outer, base):
        cls = self.__wrapped__

        class Wrapper(base):
            pass

        Wrapper.__name__ = cls.__name__
        Wrapper.__module__ = cls.__module__
        Wrapper.__qualname__ = cls.__qualname__
        Wrapper.__doc__ = cls.__doc__
        if hasattr(cls, '__annotations__'):
            Wrapper.__annotations__ = cls.__annotations__

        return Wrapper

if _python_3_7_plus:
    @export
    def bound_inner_base(o): # pragma: nocover
        return o
else:
    @export
    def bound_inner_base(o): # pragma: nocover
        return o.cls

@export
def rebind(child, bound_parent):
    """
    Create a subclass of child that inherits from bound_parent.

    child should be a class that inherits from an *unbound*
    inner class (e.g. Outer.Inner).  bound_parent should be
    a *bound* version of that same class (outer_instance.Inner).

    Returns a new class: a subclass of child that subclasses
    from the *bound* version of that inner class--as if it was
    an inner class decorated with @BoundInnerClass.  When it's
    instantiated, the outer instance will be automatically passed
    in to this new class's __init__ method.

    Example:
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):
                    self.outer = outer

        # Child inherits from Outer.Parent,
        # the *unbound* version of Parent
        class Child(Outer.Parent):
            def __init__(self, outer):
                super().__init__(outer)
                self.child_attr = 'set by child'

        o = Outer()
        # We rebind Child to o.Parent,
        # a *bound* version of Parent--
        # it's bound to o
        Rebound = rebind(Child, o.Parent)

        instance = Rebound()  # o is passed in to Child.__init__ as "outer"
        assert instance.outer is o
        assert instance.child_attr == 'set by child'
    """
    # Get the outer reference from bound_parent's wrapper
    # bound_parent is a Wrapper class that has outer captured in closure
    # We need to extract it and create a new wrapper that calls child.__init__

    # The bound_parent's __init__ has outer_weakref in its closure
    outer_weakref = None
    for cell in bound_parent.__init__.__closure__ or ():
        val = cell.cell_contents
        if isinstance(val, weakref.ref):
            outer_weakref = val
            break

    if outer_weakref is None:
        raise ValueError("bound_parent isn't a bound inner class")

    class Rebound(bound_parent, child):
        def __init__(self, *args, **kwargs):
            # Call child's __init__ with outer injected
            child.__init__(self, outer_weakref(), *args, **kwargs)

    Rebound.__name__ = child.__name__
    Rebound.__module__ = child.__module__
    Rebound.__qualname__ = child.__qualname__

    return Rebound


@export
def class_bound_to(cls, outer):
    """
    Return True if cls is a BoundInnerClass bound to outer.

    This checks if cls was created by accessing a BoundInnerClass-decorated
    inner class through that specific outer instance.

    cls should be the class to check, and outer should be an instance
    of an outer class.

    Returns True if cls is an inner class bound to outer, False otherwise.

    Note: this is NOT transitive. If cls is bound to x,
    and x is bound to y, class_bound_to(cls, y) returns False.
    """
    cache = getattr(outer, BOUNDINNERCLASS_ATTR, None)
    if cache is None:
        return False
    name = getattr(cls, '__name__', None)
    if name is None:
        return False
    return cache.get(name) is cls


@export
def instance_bound_to(instance, outer):
    """
    Return True if instance is an instance of a class bound to outer.

    instance should be the object to check, and outer should be an
    instance of an outer class.

    Returns True if instance is an instance of an inner class
    bound to outer, False otherwise.

    Note: this is NOT transitive. If instance is an instance of a class
    bound to x, and x is bound to y, instance_bound_to(instance, y)
    returns False.
    """
    return class_bound_to(type(instance), outer)

