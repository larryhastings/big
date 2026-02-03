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


from .builtin import ModuleManager
mm = ModuleManager()
export = mm.export
delete = mm.delete
clean  = mm.clean
delete('ModuleManager', 'mm', 'export', 'delete', 'clean')
__all__ = mm.__all__


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
# add BOUNDINNERCLASS_OUTER_SLOTS to your slots declaration:
#
# class Foo:
#     __slots__ = ('x', 'y', 'z') + BOUNDINNERCLASS_OUTER_SLOTS
BOUNDINNERCLASS_OUTER_ATTR = '__bound_inner_class_outer__'
export('BOUNDINNERCLASS_OUTER_ATTR')
BOUNDINNERCLASS_OUTER_SLOTS = (BOUNDINNERCLASS_OUTER_ATTR,)
export('BOUNDINNERCLASS_OUTER_SLOTS')

BOUNDINNERCLASS_INNER_ATTR = '__bound_inner_class_inner__'
export('BOUNDINNERCLASS_INNER_ATTR')


def _get_cache(outer):
    """Get or create the bound inner classes cache dict on outer."""
    cache = getattr(outer, BOUNDINNERCLASS_OUTER_ATTR, None)
    if cache is None:
        cache = {}
        # Try to set it - will fail if outer uses __slots__ without this attr
        try:
            object.__setattr__(outer, BOUNDINNERCLASS_OUTER_ATTR, cache)
        except AttributeError:
            # outer uses __slots__ and doesn't have __bound_inner_classes__
            # (If outer had __dict__, object.__setattr__ would have succeeded)
            raise TypeError(
                f"Cannot cache bound inner class on {type(outer).__name__}. "
                f"Add '{BOUNDINNERCLASS_OUTER_ATTR}' to __slots__ (or remove '__slots__')."
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

    def __call__(self, *args, **kwargs):
        raise TypeError(
            f"@{self.__class__.__name__} can only decorate a class nested inside another class"
        )

@export
class BoundInnerClass(_BoundInnerClassBase):
    """
    Class decorator for an inner class, binding them similarly to methods.

    In Python, if you access a function defined inside a class via an
    instance of that class, you get a "method", and the instance of the
    class is passed in automatically:

        class Outer:
            def fn(self):
                ...

        o = Outer()
        o.fn()

    Here, o.fn is a "method", a bound function, and "o" is automatically
    passed in to fn when o.fn is called.

    The BoundInnerClass decorator adds this for classes.  When accessing
    an inner class via an instance of the outer class, this decorator "binds"
    the inner class to that instance.  This changes the signature of the
    inner class's __init__; now the "outer" class's instance is passed
    in automatically:

        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):
                    ...

        o = Outer()
        i = o.Inner()

    Here, o.Inner is a "bound inner class", and "o" (the instance of the
    Outer class) is automatically passed in to Inner.__init__ when o.Inner
    is instantiated.  Since the first positional parameter is already
    "self", "o" is passed in as the *second* positional parameter, which
    by convention is called "outer".

    Note that this has implications for all subclasses. If class B is
    decorated with BoundInnerClass, and class S is a subclass of B,
    such that issubclass(S, B) returns True, class S must be decorated
    with either @BoundInnerClass or @UnboundInnerClass.

    Internally, o.Inner is constructed once, and cached; this is necessary
    for stable subclassing and isinstance checks.

    The implementation of BoundInnerClass is a class decorator.  It
    returns a "proxy" for the decorated class implementing the descriptor
    protocol; when you access this proxy through an instance, the descriptor
    creates a custom subclass with a custom __init__.  This __init__ is a closure with a reference to the instance, and it passes
    that instance in as an argument to the base class's __init__.

    BoundInnerClass caches the bound inner classes in the outer class,
    in an attribute called "__bound_inner_class_outer__".  If you use
    BoundInnerClass on an inner class, and the outer class uses slots,
    you must add this attribute to your __slots__ declaration.  Instead
    of hard-coding this, please use the symbolic value
    BOUNDINNERCLASS_OUTER_SLOTS, like so:

        class Foo:
            __slots__ = ('x', 'y', 'z') + BOUNDINNERCLASS_SLOTS

            @BoundInnerClass
            class Bar:
                ...

    Bound classes themselves also have a __bound_inner_class_inner__
    attribute containing a 2-tuple of (unbound_class, outer_weakref).

    See also big.ClassRegistry.
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

        # Mark as a bound inner class with info about its binding
        setattr(Wrapper, BOUNDINNERCLASS_INNER_ATTR, (cls, outer_weakref))

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


if _python_3_7_plus: # pragma: nocover
    @export
    def bound_inner_base(o): # pragma: nocover
        """
        Returns the base class for declaring a subclass
        of a bound inner class while still in the outer
        class scope. Unnecessary in Python 3.7+, or when
        the child class is defined outside the outer
        class scope.

        class Outer:
            @BoundInnerClass
            class InnerParent:
                ...
            @BoundInnerClass
            class InnerChild(bound_inner_base(InnerParent)):
                ...
        """
        return o
else: # pragma: nocover
    @export
    def bound_inner_base(o): # pragma: nocover
        """
        Returns the base class for declaring a subclass
        of a bound inner class while still in the outer
        class scope. Unnecessary in Python 3.7+, or when
        the child class is defined outside the outer
        class scope.

        class Outer:
            @BoundInnerClass
            class InnerParent:
                ...
            @BoundInnerClass
            class InnerChild(bound_inner_base(InnerParent)):
                ...
        """
        return o.cls


@export
def unbound(cls):
    """
    Return the unbound version of a bound inner class.

    If cls is a bound inner class (created by accessing a @BoundInnerClass
    through an instance), returns the original unbound class.

    If cls is already unbound or is not a bound inner class, returns cls
    unchanged.

    Example:
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):
                    self.outer = outer

        o = Outer()
        BoundInner = o.Inner
        assert unbound(BoundInner) is Outer.Inner
        assert unbound(Outer.Inner) is Outer.Inner  # already unbound
    """
    # Check cls.__dict__ directly, not inherited attributes
    if not isinstance(cls, type):
        raise TypeError(f"unbound() argument must be a class, not {type(cls).__name__}")
    info = cls.__dict__.get(BOUNDINNERCLASS_INNER_ATTR)
    if info is not None:
        return info[0]
    return cls


def _get_outer_weakref(cls):
    """
    Extract the outer weakref from a bound class.

    Returns None if cls is not a bound class.
    """
    # Check cls.__dict__ directly, not inherited attributes
    info = cls.__dict__.get(BOUNDINNERCLASS_INNER_ATTR)
    if info is None: # pragma: nocover
        return None
    return info[1]


def _is_bound(cls):
    """Return True if cls is a bound inner class."""
    return BOUNDINNERCLASS_INNER_ATTR in cls.__dict__


@export
def reparent(child, parent, *, replace=None):
    """
    Create a subclass of child that inherits from parent.

    child should be a class that inherits from a BoundInnerClass (bound or
    unbound).  parent should be a bound or unbound version of a base class
    that child inherits from.

    If parent is bound, returns a new class that inherits from the bound
    version, so when instantiated, the outer instance is automatically
    passed to __init__.

    If parent is unbound, returns the unbound version of child's base.

    The optional replace parameter specifies which of child's bases to
    replace.  This is required when child inherits from multiple
    BoundInnerClasses and there would otherwise be ambiguity.

    Example:
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):
                    self.outer = outer

        class Child(Outer.Parent):
            def __init__(self, outer):
                super().__init__(outer)

        o = Outer()
        Bound = reparent(Child, o.Parent)
        instance = Bound()  # o is passed automatically
        assert instance.outer is o

        # Reparenting to unbound returns the unbound base
        assert reparent(Bound, Outer.Parent) is Outer.Parent
    """
    # Validate parent is a class
    if not isinstance(parent, type):
        raise TypeError(
            f"parent must be a class, not {type(parent).__name__}"
        )

    unbound_parent = unbound(parent)
    parent_is_bound = _is_bound(parent)

    # Handle replace parameter
    if replace is not None:
        if not isinstance(replace, type):
            raise TypeError(
                f"replace must be a class, not {type(replace).__name__}"
            )
        unbound_replace = unbound(replace)

        # Validate replace is in child's bases
        if replace not in child.__bases__:
            raise ValueError(
                f"{replace.__name__} is not a direct base of {child.__name__}"
            )

        # Validate unbound(parent) == unbound(replace)
        if unbound_parent is not unbound_replace:
            raise ValueError(
                f"unbound version of parent ({unbound_parent.__name__}) doesn't match "
                f"unbound version of replace ({unbound_replace.__name__})"
            )

        # Check for no-op (both unbound and equal)
        if not parent_is_bound and not _is_bound(replace):
            # Both unbound, and we validated they're the same - no-op
            return child

        target_base = unbound_replace
    else:
        # No replace specified - find the base to replace
        # unbound_parent must be in child's MRO
        matching_bases = []
        for base in child.__bases__:
            if unbound(base) is unbound_parent:
                matching_bases.append(base)

        if not matching_bases:
            raise ValueError(
                f"{unbound_parent.__name__} is not a base of {child.__name__}"
            )

        if len(matching_bases) > 1:
            raise ValueError(
                f"{child.__name__} has multiple bases matching {unbound_parent.__name__}, "
                f"use replace= to specify which one"
            )

        target_base = matching_bases[0]

        # Check for no-op
        if not parent_is_bound and not _is_bound(target_base):
            return child

    # If parent is unbound, return the unbound base
    if not parent_is_bound:
        return unbound_parent

    # parent is bound - check cache first
    outer_weakref = _get_outer_weakref(parent)
    outer = outer_weakref()

    # Cache key uses id(child) to avoid strong reference to child class
    cache_key = (id(child), unbound_parent.__name__)
    cache = _get_cache(outer)

    cached_entry = cache.get(cache_key)
    if cached_entry is not None:
        cached_class, child_ref = cached_entry
        if child_ref() is child:
            # Weakref still valid and points to same object
            return cached_class
        # Stale entry - child class was GC'd and id reused
        del cache[cache_key]

    # Get the unbound version of child for __init__ call
    # This prevents double-injection when child is also bound
    unbound_child = unbound(child)

    class reparented(parent, child):
        def __init__(self, *args, **kwargs):
            unbound_child.__init__(self, outer_weakref(), *args, **kwargs)

    reparented.__name__ = child.__name__
    reparented.__module__ = child.__module__
    reparented.__qualname__ = child.__qualname__

    # Mark as a bound inner class with info about its binding
    setattr(reparented, BOUNDINNERCLASS_INNER_ATTR, (unbound_child, outer_weakref))

    # Cache the result with a weakref to child for validation
    cache[cache_key] = (reparented, weakref.ref(child))

    return reparented


@export
def bind(child, outer):
    """
    Bind an external child class to an outer instance.

    child should be a class that inherits from an *unbound*
    inner class (e.g. Outer.Inner).  outer should be an instance
    of the outer class containing that inner class, or None.

    If outer is an instance, returns a new class that, when instantiated,
    automatically receives outer as its first argument (after self).

    If outer is None, returns the unbound base class (equivalent to
    calling unbound(child)).

    This is a convenience wrapper around reparent() that finds
    the appropriate bound parent class.  If child inherits from
    multiple BoundInnerClasses from the same outer class,
    bind declines to guess which one you meant.  In this case
    you should use reparent(), which lets you explicitly specify
    the correct parent.

    Example:
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):
                    self.outer = outer

        class Child(Outer.Parent):
            def __init__(self, outer):
                super().__init__(outer)

        o = Outer()
        Bound = bind(Child, o)

        instance = Bound()  # o is passed in automatically
        assert instance.outer is o

        # Unbind by passing None
        assert bind(Bound, None) is Outer.Parent
    """
    # Handle unbinding (outer is None)
    if outer is None:
        return unbound(child)

    outer_class = type(outer)
    bound_parents = []

    for base in child.__bases__:
        name = base.__name__
        descriptor = outer_class.__dict__.get(name)
        if isinstance(descriptor, _BoundInnerClassBase):
            if descriptor.__wrapped__ is base:
                bound_parents.append(name)

    if not bound_parents:
        raise ValueError(
            f"{child.__name__} doesn't inherit from any BoundInnerClass of {outer_class.__name__}"
        )

    if len(bound_parents) > 1:
        raise ValueError(
            f"{child.__name__} inherits from multiple BoundInnerClasses "
            f"({', '.join(bound_parents)}), use reparent() instead"
        )

    bound_parent = getattr(outer, bound_parents[0])
    return reparent(child, bound_parent)


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
    cache = getattr(outer, BOUNDINNERCLASS_OUTER_ATTR, None)
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


clean()
