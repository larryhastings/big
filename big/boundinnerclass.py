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


from . import builtin
mm = builtin.ModuleManager()
export = mm.export


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
# add BOUNDINNERCLASS_OUTER_SLOTS to your slots declaration,
# like so:
#
# class Foo:
#     __slots__ = ('x', 'y', 'z') + BOUNDINNERCLASS_OUTER_SLOTS
#
#     @BoundInnerClass
#     class Whatnot:
#         ...
#
BOUNDINNERCLASS_OUTER_ATTR = '__boundinnerclass_outer__'
export('BOUNDINNERCLASS_OUTER_ATTR')
BOUNDINNERCLASS_OUTER_SLOTS = (BOUNDINNERCLASS_OUTER_ATTR,)
export('BOUNDINNERCLASS_OUTER_SLOTS')

BOUNDINNERCLASS_INNER_ATTR = '__boundinnerclass_inner__'
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
    Class decorator for nested classes, binding them like methods.

    In Python, if you access a function defined inside a class via an
    instance of that class, you get a "method", which means the instance
    of the class is passed in automatically:

        class Outer:
            def fn(self):
                ...

        o = Outer()
        o.fn()

    Here, o.fn is a bound function, and "o" is automatically
    passed in to fn when o.fn is called.  We call that a "method".

    The BoundInnerClass decorator adds this feature for classes.  When
    accessing an inner class via an instance of the outer class,
    this decorator "binds" the inner class to that instance.
    This changes the signature of the inner class's __init__;
    now the "outer" class's instance is passed in automatically:

        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):
                    ...

        o = Outer()
        i = o.Inner()

    Here, o.Inner is a "bound inner class".  When you instantiate o.Inner,
    "o" (the instance of the Outer class) is automatically passed in to
    Inner.__init__.  Since the first positional parameter is already
    "self", "o" is passed in as the *second* positional parameter.
    (By convention we call this "outer".)

    Note that this has implications for subclassing. If class B is
    decorated with BoundInnerClass, and class S is a subclass of B,
    such that issubclass(S, B) returns True, class S must be decorated
    with either @BoundInnerClass or @UnboundInnerClass.

    Internally, o.Inner--Inner bound to o--is constructed once,
    and cached; this is necessary for stable subclassing and
    isinstance checks.

    BoundInnerClass is implemented as a class decorator.  It returns a
    "proxy" for the decorated class implementing the descriptor protocol;
    when you access this proxy through an instance, the descriptor creates
    a custom subclass with a custom __init__.  This __init__ is a closure
    with a reference to the instance, and it passes that instance in as
    an argument to the base class's __init__.

    BoundInnerClass caches these bound inner class subclasses in the
    outer class, in an attribute called "__bound_inner_class_outer__".
    If you use BoundInnerClass on an inner class, and the outer class
    uses slots, you must add this attribute to your __slots__ declaration.
    Instead of hard-coding this, please use the symbolic value
    BOUNDINNERCLASS_OUTER_SLOTS, like so:

        class Foo:
            __slots__ = ('x', 'y', 'z') + BOUNDINNERCLASS_SLOTS

            @BoundInnerClass
            class Bar:
                ...

    Bound classes themselves have a __bound_inner_class_inner__
    attribute containing a 2-tuple of (unbound_class, outer_weakref).

    If you support Python 3.6, please see the bound_inner_base
    function.

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

    If class B is decorated with BoundInnerClass, and class S
    is a subclass of B, such that issubclass(S, B) returns True,
    class S must be decorated with either @BoundInnerClass
    or @UnboundInnerClass.
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

    If cls is a bound inner class (created by accessing an inner
    class decorated with @BoundInnerClass through an instance)
    returns the original unbound class.

    If cls is already unbound, or is not a bound inner class,
    returns cls unchanged.

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
    # Check if cls inherits from a bound class - if so, there's no unbound version
    if _inherits_from_bound(cls):
        raise ValueError(
            f"{cls.__name__} inherits from a bound class and has no unbound version"
        )
    return cls


def _inherits_from_bound(cls):
    """
    Return True if cls inherits directly from a bound inner class.

    This detects classes like:
        class Child(o.Parent):  # o.Parent is bound
            pass

    Such classes have no unbound version and cannot be rebaseed.
    """
    for base in cls.__bases__:
        if is_bound(base):
            return True
    return False


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


@export
def is_bound(cls):
    """Return True if cls is a bound inner class."""
    return BOUNDINNERCLASS_INNER_ATTR in cls.__dict__


@export
def rebase(child, base):
    """
    Rebases a child class so it inherits from a particular base class.

    child must be a class which directly inherits from a base
    class we'll call "T".  T must be a bindable inner class,
    either bound or unbound.  base must be a variant of T,
    either bound or unbound.  Returns a variant of child
    that has been "rebased" so it inherits from base
    instead of from T.

    If base is bound, returns a new class that inherits from the
    bound version--so, when instantiated, that outer instance is
    automatically passed to base.__init__ when child.__init__
    calls super().__init__.

    If base is unbound, returns the unbound version of child.

    Example:
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):
                    self.outer = outer

        # subclass of the *unbound* Outer.Parent
        class Child(Outer.Parent):
            def __init__(self, outer):
                super().__init__(outer)

        o = Outer()
        # BoundChild is Child, bound to o
        BoundChild = rebase(Child, o.Parent)
        bound_child = BoundChild()  # o is passed automatically
        assert bound_child.outer is o

        # Rebasing to unbound returns the unbound child
        assert rebase(BoundChild, Outer.Parent) is Child
    """
    if not isinstance(base, type):
        raise TypeError(
            f"base must be a class, not {type(base).__name__}"
        )

    # Check if child inherits directly from a bound class,
    # like "class child(o.Parent):".  A class like this
    # can't be rebased.
    if not is_bound(child) and _inherits_from_bound(child):
        raise ValueError(
            f"{child.__name__} inherits from a bound class and can't be rebased"
        )

    unbound_base = unbound(base)
    unbound_child = unbound(child)

    matching_bases = []
    for b in child.__bases__:
        if unbound(b) is unbound_base:
            matching_bases.append(b)

    if len(matching_bases) != 1:
        if not matching_bases:
            raise ValueError(
                f"{unbound_base.__name__} is not a base of {child.__name__}"
            )

    current_base = matching_bases[0]

    if base is unbound_base:
        # If both base and current_base are unbound, no-op
        if not is_bound(current_base):
            return child

        # base is unbound, current_base is bound
        return unbound_child

    # base is bound - check cache first
    outer_weakref = _get_outer_weakref(base)
    outer = outer_weakref()

    # Cache key uses id(child) to avoid strong reference to child class
    cache_key = (id(child), unbound_base.__name__)
    cache = _get_cache(outer)

    cached_entry = cache.get(cache_key)
    if cached_entry is not None:
        cached_class, child_ref = cached_entry
        if child_ref() is child:
            # Weakref still valid and points to same object
            return cached_class
        # Stale entry - child class was GC'd and id reused
        del cache[cache_key]

    # use the unbound version of child for __init__ call
    # This prevents double-injection when child is also bound

    class rebased(base, child):
        def __init__(self, *args, **kwargs):
            unbound_child.__init__(self, outer_weakref(), *args, **kwargs)

    rebased.__name__ = child.__name__
    rebased.__module__ = child.__module__
    rebased.__qualname__ = child.__qualname__

    # Mark as a bound inner class with info about its binding
    setattr(rebased, BOUNDINNERCLASS_INNER_ATTR, (unbound_child, outer_weakref))

    # Cache the result with a weakref to child for validation
    cache[cache_key] = (rebased, weakref.ref(child))

    return rebased


@export
def bind(child, outer):
    """
    Bind an external child class to an outer instance.

    child should be a class that inherits from an *unbound*
    inner class (e.g. Outer.Inner).  outer should be an instance
    of the outer class containing that inner class, or None.

    If outer is an instance, returns a new class that
    when instantiated automatically receives outer as
    its "outer" argument.

    If outer is None, returns the unbound base class
    (equivalent to calling unbound(child)).

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
        BoundChild = bind(Child, o)

        bound_child = BoundChild()  # o is passed in automatically
        assert bound_child.outer is o

        # Unbind by passing None as the outer instance
        assert bind(BoundChild, None) is Outer.Parent
    """
    # Handle unbinding (outer is None)
    if outer is None:
        return unbound(child)

    # Check if child inherits directly from a bound class
    # Such classes cannot be bound at all
    if not is_bound(child) and _inherits_from_bound(child):
        raise ValueError(
            f"{child.__name__} inherits from a bound class and cannot be bound"
        )

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
            f"({', '.join(bound_parents)}), use rebase() instead"
        )

    bound_parent = getattr(outer, bound_parents[0])
    return rebase(child, bound_parent)


@export
def bound_to(cls):
    """
    Return the outer instance that cls is bound to, or None.

    If cls is an inner class decorated with BoundInnerClass,
    and was bound to an outer instance, returns that outer
    instance.  Otherwise returns None.

    BoundInnerClass doesn't itself keep strong references.
    If cls was bound to an object X, but X has been destroyed
    (GC'd, etc), bound_to(cls) will return None.
    """
    info = cls.__dict__.get(BOUNDINNERCLASS_INNER_ATTR)
    if info is None:
        return None
    outer_weakref = info[1]
    return outer_weakref()


@export
def type_bound_to(instance):
    """
    Return the "outer" object that instance's type is bound to, or None.

    If type(instance) is an inner class decorated with
    BoundInnerClass, and was bound to an outer instance,
    returns that outer instance. Otherwise returns None.

    BoundInnerClass doesn't itself keep strong references.
    If type(instance) was bound to an object X,
    but X is destroyed (GC'd, etc), type_bound_to(cls)
    will return None.
    """
    return bound_to(type(instance))


mm()
