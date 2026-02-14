#!/usr/bin/env python3

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

##
## If you have a class with an inner class inside,
## decorate the inner class with the BoundInnerClass
## decorator defined below and it'll automatically
## get the parent instance passed in as a *second*
## positional parameter!
## _______________________________________
##
## class Outer:
##   @BoundInnerClass
##   class Inner:
##       def __init__(self, outer):
##           global o
##           print(outer = o)
## o = Outer()
## i = o.Inner()
## _______________________________________
##
## This program prints True.  The "outer" parameter
## to Inner.__init__ was filled in automatically by
## the BoundInnerClass decorator.
##
## Thanks, BoundInnerClass, you've saved the day!
##
## -----
##
## Infinite extra-special thanks to Alex Martelli for
## showing me how this could be done in the first place--
## all the way back in 2010!
##
## https://stackoverflow.com/questions/2278426/inner-classes-how-can-i-get-the-outer-class-object-at-construction-time
##
## Thanks, Alex, you've saved the day!
##


import inspect
import sys
import threading
import weakref

_python_3_7_plus = (sys.version_info.major > 3) or ((sys.version_info.major == 3) and (sys.version_info.minor >= 7))


from . import builtin
mm = builtin.ModuleManager()
export = mm.export


# BOUNDINNERCLASS_OUTER_ATTR is stored in the outer *instance*,
BOUNDINNERCLASS_OUTER_ATTR = '__boundinnerclass_outer__'
# which is why you might need to add it to __slots__.
BOUNDINNERCLASS_OUTER_SLOTS = (BOUNDINNERCLASS_OUTER_ATTR,)

export('BOUNDINNERCLASS_OUTER_ATTR')
export('BOUNDINNERCLASS_OUTER_SLOTS')


# _BOUNDINNERCLASS_INNER_ATTR is stored in the inner *class*,
# and classes always have a __dict__.  They never use __slots__.
# So we don't have to worry about slots.
_BOUNDINNERCLASS_INNER_ATTR = '__boundinnerclass_inner__'



if _python_3_7_plus: # pragma: nocover
    @export
    def bound_inner_base(o): # pragma: nocover
        """
        Returns the base class for declaring a subclass of a
        bound inner class while still in the outer class scope.
        Only needed for Python 3.6 compatibility.

        Example:

            class Outer:
                @BoundInnerClass
                class InnerParent:
                    ...
                @BoundInnerClass
                class InnerChild(InnerParent):
                    ...

        This would fail in Python 3.6.  If you change the
        declaration of "InnerChild" to this:

                class InnerChild(bound_inner_base(InnerParent)):

        then it works.

        Unnecessary in Python 3.7+, or when the child class
        is defined after exiting the outer class scope.
        """
        return o
else: # pragma: nocover
    @export
    def bound_inner_base(o): # pragma: nocover
        """
        Returns the base class for declaring a subclass of a
        bound inner class while still in the outer class scope.
        Only needed for Python 3.6 compatibility.

        Example:

            class Outer:
                @BoundInnerClass
                class InnerParent:
                    ...
                @BoundInnerClass
                class InnerChild(InnerParent):
                    ...

        This would fail in Python 3.6.  If you change the
        declaration of "InnerChild" to this:

                class InnerChild(bound_inner_base(InnerParent)):

        then it works.

        Unnecessary in Python 3.7+, or when the child class
        is defined after exiting the outer class scope.
        """
        return o.cls



def _make_bound_signature(original_init):
    """
    Create a signature for a bound class by removing the first parameter (outer).

    Returns None if signature cannot be determined.
    """
    try:
        sig = inspect.signature(original_init)
    except (ValueError, TypeError):
        return None

    params = list(sig.parameters.values())
    # Remove 'self' and 'outer' (first two params)
    bound_params = params[2:] if len(params) >= 2 else []

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

    @property
    def __name__(self):
        return self.__wrapped__.__name__

    @property
    def __doc__(self):
        return self.__wrapped__.__doc__

    @property
    def __module__(self):
        return self.__wrapped__.__module__

    @property
    def cls(self):
        """Return the wrapped class. For backward compatibility."""
        return self.__wrapped__

    def __repr__(self):
        return f"<{self.__class__.__name__} for {self.__wrapped__!r}>"

    def __getattr__(self, name):
        return getattr(self.__wrapped__, name)

    def __setattr__(self, name, value):
        if name == '__wrapped__':
            object.__setattr__(self, name, value)
            # Update cached attributes
            wrapped = value
            try:
                object.__setattr__(self, '__qualname__', wrapped.__qualname__)
            except AttributeError:
                pass
            try:
                object.__setattr__(self, '__annotations__', wrapped.__annotations__)
            except AttributeError:
                pass
        elif name in ('__qualname__', '__annotations__'):
            # Set on both proxy and wrapped
            object.__setattr__(self, name, value)
            setattr(self.__wrapped__, name, value)
        else:
            setattr(self.__wrapped__, name, value)

    def __delattr__(self, name):
        delattr(self.__wrapped__, name)

    def __mro_entries__(self, bases):
        return (self.__wrapped__,)

    def __instancecheck__(cls, instance):
        return isinstance(instance, cls.__wrapped__)

    def __subclasscheck__(cls, subclass):
        if hasattr(subclass, '__wrapped__'):
            subclass = subclass.__wrapped__
        return issubclass(subclass, cls.__wrapped__)


class _BoundInnerClassCache:
    """
    Cache for bound inner classes, stored on outer instances.

    Handles key management and stale entry detection internally.
    Thread-safe: all operations are protected by an internal lock.
    """

    __slots__ = ('_cache', '_lock')

    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()

    def get(self, cls):
        """
        Get cached bound class for cls, or None if not cached or stale.

        cls should be the unbound class being bound.
        """
        key = (id(cls), cls.__name__)
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            bound_class, cls_ref = entry
            if cls_ref() is not cls:
                # Stale entry - cls was GC'd and id reused
                del self._cache[key]
                return None
            return bound_class

    def set(self, cls, bound_class):
        """
        Cache bound_class for cls, or return existing cached value.

        cls should be the unbound class being bound.

        If cls is already cached (and not stale), returns the existing
        cached value instead of storing the new one. This ensures that
        concurrent threads will all get the same bound class.

        Returns the cached bound class (either the existing one or the
        newly stored one).
        """
        key = (id(cls), cls.__name__)
        with self._lock:
            # Check if already cached (double-check pattern for thread safety)
            entry = self._cache.get(key)
            if entry is not None:
                existing_class, cls_ref = entry
                if cls_ref() is cls:
                    # Already cached and not stale - return existing
                    return existing_class
                # Stale entry - will be replaced below

            self._cache[key] = (bound_class, weakref.ref(cls))
            return bound_class


_get_cache_lock = threading.Lock()

def _get_cache(outer):
    """Get or create the bound inner classes cache on outer."""
    cache = getattr(outer, BOUNDINNERCLASS_OUTER_ATTR, None)
    if cache is not None:
        return cache

    with _get_cache_lock:
        # Double-check after acquiring lock
        cache = getattr(outer, BOUNDINNERCLASS_OUTER_ATTR, None)
        if cache is None:
            cache = _BoundInnerClassCache()
            try:
                object.__setattr__(outer, BOUNDINNERCLASS_OUTER_ATTR, cache)
            except AttributeError:
                raise TypeError(
                    f"Cannot cache bound inner class on {type(outer).__name__}. "
                    f"Add '{BOUNDINNERCLASS_OUTER_ATTR}' to __slots__ (or remove '__slots__')."
                ) from None
        return cache


def _make_bound_class(unbound_cls, outer, base):
    """
    Create a bound wrapper class.

    unbound_cls: the original unbound class being bound
    outer: the outer instance to bind to
    base: the primary base class for the wrapper

    Returns a new class that inherits from base
    and injects outer into __init__.
    """
    outer_weakref = weakref.ref(outer)

    class Wrapper(base):
        def __init__(self, *args, **kwargs):
            unbound_cls.__init__(self, outer_weakref(), *args, **kwargs)

        # Custom repr if the wrapped class doesn't have one
        if unbound_cls.__repr__ is object.__repr__:
            def __repr__(self):
                return "".join([
                    "<",
                    unbound_cls.__module__,
                    ".",
                    self.__class__.__name__,
                    " object bound to ",
                    repr(outer_weakref()),
                    " at ",
                    hex(id(self)),
                    ">",
                ])

    Wrapper.__name__ = unbound_cls.__name__
    Wrapper.__module__ = unbound_cls.__module__
    Wrapper.__qualname__ = unbound_cls.__qualname__
    Wrapper.__doc__ = unbound_cls.__doc__
    if hasattr(unbound_cls, '__annotations__'):
        Wrapper.__annotations__ = unbound_cls.__annotations__

    # Mark as a bound inner class with info about its binding
    setattr(Wrapper, _BOUNDINNERCLASS_INNER_ATTR, (unbound_cls, outer_weakref, True))

    # Set proper signature (without 'outer' param since it's injected)
    bound_signature = _make_bound_signature(unbound_cls.__init__)
    if bound_signature is not None:
        Wrapper.__signature__ = bound_signature
        Wrapper.__init__.__signature__ = bound_signature

    return Wrapper


def _unbound(cls):
    """
    Internal version of unbound() that doesn't raise on non-bindable classes.
    Returns None if cls is not bindable.
    """
    if not isinstance(cls, type):
        return None
    info = cls.__dict__.get(_BOUNDINNERCLASS_INNER_ATTR)
    if info is not None:
        return info[0]
    return None


class _BoundInnerClassBase(_ClassProxy):
    """
    Base descriptor for bound inner classes.

    Subclasses implement _wrap() to define how the wrapper class is created.
    """

    __slots__ = ()

    # Class-level cache mapping an (unbound_class, outer_class) pair to
    # the attribute name the slow path discovered on the outer class.
    # Shared across all instances, since renaming is a property of the
    # outer *class*, not any particular outer instance.
    #
    # Keyed on (id(target_class), id(outer_class)).  If a class is GC'd
    # and its id reused, we might get a stale hit, but the medium path
    # always verifies via identity check before using the cached value,
    # so a stale hit is harmless -- it just falls through to the slow path.
    _alias_cache = {}
    _alias_cache_lock = threading.Lock()

    def __init__(self, wrapped, is_boundinnerclass):
        super().__init__(wrapped)
        # Mark the wrapped class as participating in the bound inner class system.
        # Tuple: (unbound_class, outer_weakref, is_boundinnerclass)
        # outer_weakref is None for unbound classes.
        # is_boundinnerclass is True for @BoundInnerClass, False for @UnboundInnerClass.
        setattr(wrapped, _BOUNDINNERCLASS_INNER_ATTR, (wrapped, None, is_boundinnerclass))

    @staticmethod
    def _find_descriptor_by_identity(outer_class, target):
        """
        Search outer_class's MRO for a _BoundInnerClassBase descriptor
        wrapping target.  Returns (attr_name, descriptor) or (None, None).
        """
        for klass in outer_class.__mro__:
            for attr_name, descriptor in klass.__dict__.items():
                if isinstance(descriptor, _BoundInnerClassBase):
                    if descriptor.__wrapped__ is target:
                        return (attr_name, descriptor)
        return (None, None)

    @classmethod
    def _resolve_descriptor(cls, outer, outer_class, target):
        """
        Resolve the bound version of target on outer.

        target is an unbound class that may be registered as a
        BoundInnerClass on outer_class (either as a base class
        being looked up during __get__, or a child class being
        looked up during bind()/rebase()).

        Uses a three-tier lookup:
          1. Fast path: getattr(outer, target.__name__), verify identity.
          2. Medium path: check _alias_cache for a previously-discovered
             alias name, verify it still points to the right descriptor.
          3. Slow path: iterate outer_class.__mro__ by identity.
             On success, updates _alias_cache for future medium-path hits.

        Returns the bound class, or None if target is not a
        BoundInnerClass anywhere in outer_class's MRO.
        """
        # Fast path: look up by name, verify by identity
        bound_result = getattr(outer, target.__name__, None)
        if bound_result is not None and _unbound(bound_result) is target:
            return bound_result

        alias_key = (id(target), id(outer_class))

        # Medium path: check alias cache
        with cls._alias_cache_lock:
            cached_alias = cls._alias_cache.get(alias_key)
        if cached_alias is not None:
            bound_result = getattr(outer, cached_alias, None)
            if bound_result is not None and _unbound(bound_result) is target:
                return bound_result
            # Cached alias is stale; fall through to slow path

        # Slow path: search all descriptors in MRO by identity (for renamed BICs)
        attr_name, descriptor = cls._find_descriptor_by_identity(outer_class, target)
        if descriptor is not None:
            # Cache the discovered alias for future lookups
            with cls._alias_cache_lock:
                cls._alias_cache[alias_key] = attr_name
            return descriptor.__get__(outer, outer_class)

        return None

    def __get__(self, outer, outer_class):
        # Accessed via class (Outer.Inner) - return unwrapped class
        if outer is None:
            return self.__wrapped__

        # Accessed via instance (o.Inner) - return bound version
        cls = self.__wrapped__
        cache = _get_cache(outer)

        bound_class = cache.get(cls)
        if bound_class is None:
            # Build wrapper bases, handling inheritance from other BoundInnerClasses
            # The wrapper inherits from cls first (for __init__ signature),
            # then from bound versions of parent BoundInnerClasses (for MRO chaining)
            wrapper_bases = [cls]

            for base in cls.__bases__:
                # Skip if same name as us (would cause infinite recursion)
                if base.__name__ == cls.__name__:
                    continue

                resolved = self._resolve_descriptor(outer, outer_class, base)
                if resolved is not None:
                    wrapper_bases.append(resolved)
                elif _BOUNDINNERCLASS_INNER_ATTR in getattr(base, '__dict__', {}):
                    raise RuntimeError(
                        f"Can't find a BoundInnerClass descriptor for "
                        f"{base.__qualname__!r} on {outer_class.__qualname__!r} "
                        f"or any of its bases.  "
                        f"Every BoundInnerClass base must be an inner class "
                        f"of the outer class or one of its ancestors."
                    )

            # Create the wrapper - always use cls as base
            bound_class = self._wrap(outer, cls)

            # Set bases if we have bound parents to include
            if len(wrapper_bases) > 1:
                bound_class.__bases__ = tuple(wrapper_bases)

            bound_class = cache.set(cls, bound_class)

        return bound_class

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

    In Python, if you access a function defined inside a class via
    an instance of that class, this "binds" the function to that
    instance, and the object you get back is called a "method".
    When you call the method, that instance is passed in automatically
    as the first parameter, which by convention we call "self":

        class Outer:
            def fn(self):
                ...

        o = Outer()
        o.fn()

    Here, o.fn is a bound function, and "o" is automatically
    passed in to fn when o.fn is called.

    The BoundInnerClass decorator adds this feature for classes.
    When accessing an inner class via an instance of the outer
    class, this decorator "binds" the inner class to that instance.
    This changes the signature of the inner class's __init__;
    now the "outer" class's instance is passed in automatically,
    as the *second* parameter:

        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):
                    ...

        o = Outer()
        i = o.Inner()

    Here, i is an instance of Inner.  It was passed automatically
    as the first argument to Inner.__init__, which by convention we
    call "self".  But "o" was *also* passed in automatically as the
    *second* argument to Inner.__init__, which by convention we
    call "outer".

    @BoundInnerClass also lets an inner class inherit from another
    bound inner class.  These classes will be bound to the same
    outer instance, and they can simply call super().__init__() without
    passing any additional arguments.

    Example:

        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):
                    self.outer = outer

            @BoundInnerClass
            class Child(Parent):
                def __init__(self, outer):
                    # "outer" is passed to Parent.__init__ for us,
                    # all we need to do is call super().__init__()
                    super().__init__()

    Note for slots users: The "outer" class of a BIC uses a special
    attribute to cache bound inner classes.  If that outer class
    uses __slots__, it must add a slot for BIC's special attribute.
    We provide a predefined constant you can simply "add" to your
    slots tuple, BOUNDINNERCLASS_OUTER_SLOTS.  Example:

        class Foo:
            __slots__ = ('x', 'y', 'z') + BOUNDINNERCLASS_SLOTS

            @BoundInnerClass
            class Bar:
                ...

    If you support Python 3.6, please see the bound_inner_base
    function.

    See also big.ClassRegistry.
    """

    __slots__ = ()

    def __init__(self, wrapped):
        super().__init__(wrapped, True)

    def _wrap(self, outer, base):
        return _make_bound_class(self.__wrapped__, outer, base)


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

    Accessing an UnboundInnerClass through an instance of the
    outer class still gives you a "bound" class; although this
    specific class won't get "outer" passed in automatically,
    base classes that are decorated with BoundInnerClass *will*.
    """

    __slots__ = ()

    def __init__(self, wrapped):
        super().__init__(wrapped, False)

    def _wrap(self, outer, base):
        outer_weakref = weakref.ref(outer)
        cls = self.__wrapped__

        class Wrapper(base):
            pass

        Wrapper.__name__ = cls.__name__
        Wrapper.__module__ = cls.__module__
        Wrapper.__qualname__ = cls.__qualname__
        Wrapper.__doc__ = cls.__doc__
        if hasattr(cls, '__annotations__'):
            Wrapper.__annotations__ = cls.__annotations__

        # Mark as an unbound inner class with info about its binding
        setattr(Wrapper, _BOUNDINNERCLASS_INNER_ATTR, (cls, outer_weakref, False))

        return Wrapper


# @export
# def Bindable(cls):
#     """
#     Mark a class as participating in the bound inner class system.
#
#     Use this decorator for classes defined outside a class body that
#     inherit from a @BoundInnerClass class.  Unlike @BoundInnerClass,
#     this doesn't create a descriptor--the class remains a normal class.
#
#     To bind a @Bindable class to an outer instance, use the bind() function.
#
#     Example:
#         class Outer:
#             @BoundInnerClass
#             class Inner:
#                 def __init__(self, outer):
#                     self.outer = outer
#
#         @Bindable
#         class Child(Outer.Inner):
#             def __init__(self, outer):
#                 super().__init__()
#                 assert self.outer is outer
#
#         o = Outer()
#         BoundChild = bind(Child, o)
#         instance = BoundChild()
#         assert instance.outer is o
#     """
#     # Mark the class as participating in the bound inner class system
#     # (unbound_class, outer_weakref) - outer_weakref is None for unbound
#     setattr(cls, _BOUNDINNERCLASS_INNER_ATTR, (cls, None))
#     return cls


@export
def unbound(cls):
    """
    Return the unbound version of a bound class.

    If cls is a bound inner class, returns the original unbound class.
    If cls is already unbound (or not a bindable inner class), returns cls.

    Raises ValueError if cls inherits *directly* from a bound class
    (e.g. "class Child(o.Inner)"), since such classes have no unbound
    version.

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
    if not isinstance(cls, type):
        raise TypeError(f"unbound() argument must be a class, not {type(cls).__name__}")
    info = cls.__dict__.get(_BOUNDINNERCLASS_INNER_ATTR)
    if info is not None:
        return info[0]
    # Check if cls inherits directly from a bound class
    for base in cls.__bases__:
        if is_bound(base):
            raise ValueError(
                f"{cls.__name__} inherits from a bound class and has no unbound version"
            )
    return cls


def _get_outer_weakref(cls):
    """
    Extract the outer weakref from a bound class.

    cls must be a bound class (is_bound(cls) returns True).
    Returns None if cls is not a bound class.
    """
    # Check cls.__dict__ directly, not inherited attributes
    info = cls.__dict__.get(_BOUNDINNERCLASS_INNER_ATTR)
    if info is None:
        return None
    return info[1]


@export
def is_boundinnerclass(cls):
    """
    Return True if cls was decorated with @BoundInnerClass,
    or is a bound wrapper class created from one.

    Returns False for @UnboundInnerClass classes and regular classes.
    Raises TypeError for non-class arguments.
    """
    if not isinstance(cls, type):
        raise TypeError(f"is_boundinnerclass() argument must be a class, not {type(cls).__name__}")
    info = cls.__dict__.get(_BOUNDINNERCLASS_INNER_ATTR)
    if info is None:
        return False
    return info[2]


@export
def is_unboundinnerclass(cls):
    """
    Return True if cls was decorated with @UnboundInnerClass,
    or is a wrapper class created from one.

    Returns False for @BoundInnerClass classes and regular classes.
    Raises TypeError for non-class arguments.
    """
    if not isinstance(cls, type):
        raise TypeError(f"is_unboundinnerclass() argument must be a class, not {type(cls).__name__}")
    info = cls.__dict__.get(_BOUNDINNERCLASS_INNER_ATTR)
    if info is None:
        return False
    return not info[2]


@export
def is_bound(cls):
    """
    Return True if cls is a bound inner class.

    A class is bound if it's a bindable inner class
    that has been bound to a specific outer instance.
    (Said another way: is_bound(cls) returns True if
    bound_to(cls) returns non-None.)

    Returns False for non-participating classes.
    """
    if not isinstance(cls, type):
        return False
    info = cls.__dict__.get(_BOUNDINNERCLASS_INNER_ATTR)
    if info is None:
        return False
    outer_weakref = info[1]
    return outer_weakref is not None


# @export
# def rebase(child, base):
#     """
#     Rebases a child class so it inherits from a particular base class.
#
#     base must be a bindable inner class, either bound or unbound.
#     unbound(child) must directly inherit from unbound(base).  Returns a
#     variant of child that's been "rebased" so it inherits from base.
#
#     If base is bound, returns a new variant of child that inherits
#     from base.  When the returned class is instantiated, base.__init__
#     will be called with the outer instance that base is bound to.
#
#     If base is unbound, returns the unbound version of child.
#
#     If child already inherits from base, returns child unchanged.
#
#     Example:
#         class Outer:
#             @BoundInnerClass
#             class Parent:
#                 def __init__(self, outer):
#                     self.outer = outer
#
#             @BoundInnerClass
#             class Child(Parent):
#                 def __init__(self, outer):
#                     super().__init__()
#
#         o1 = Outer()
#         o2 = Outer()
#
#         # Rebase o1.Child to inherit from o2.Parent
#         RebasedChild = rebase(o1.Child, o2.Parent)
#         instance = RebasedChild()
#         assert instance.outer is o2
#         assert RebasedChild is o2.Child
#
#         # Rebasing to unbound returns the unbound child
#         assert rebase(o1.Child, Outer.Parent) is Outer.Child
#     """
#     if not isinstance(base, type):
#         raise TypeError(
#             f"base must be a class, not {type(base).__name__}"
#         )
#
#     # Both child and base must participate in the binding system
#     if not is_bindable(child):
#         raise ValueError(
#             f"{child.__name__} is not a bindable inner class"
#         )
#     if not is_bindable(base):
#         raise ValueError(
#             f"{base.__name__} is not a bindable inner class"
#         )
#
#     unbound_base = unbound(base)
#     unbound_child = unbound(child)
#
#     current_base = None
#     for b in child.__bases__:
#         if _unbound(b) is unbound_base:
#             if current_base is not None:
#                 raise ValueError(
#                     f"{child.__name__} inherits from {unbound_base.__name__} multiple times"
#                 )
#             current_base = b
#     if current_base is None:
#         raise ValueError(
#             f"{unbound_base.__name__} is not a base of {child.__name__}"
#         )
#
#     if not is_bound(base):
#         # If both base and current_base are unbound, no-op
#         if not is_bound(current_base):
#             return child
#
#         # base is unbound, current_base is bound
#         return unbound_child
#
#     # base is bound - get the outer instance
#     outer_weakref = _get_outer_weakref(base)
#     outer = outer_weakref()
#     outer_class = type(outer)
#
#     # Check if child is a BoundInnerClass in outer's class
#     # If so, return the bound version directly (e.g., o2.Child)
#     resolved = _BoundInnerClassBase._resolve_descriptor(outer, outer_class, unbound_child)
#     if resolved is not None:
#         return resolved
#
#     # Not a BIC in outer_class - create bound class using cache
#     # This is a @Bindable class, so include unbound_child as extra_base for proper MRO
#     cache = _get_cache(outer)
#     bound_class = cache.get(unbound_child)
#     if bound_class is None:
#         bound_class = _make_bound_class(unbound_child, outer, base, extra_base=unbound_child)
#         bound_class = cache.set(unbound_child, bound_class)
#     return bound_class


# @export
# def bind(cls, outer):
#     """
#     Bind a class to an outer instance.
#
#     cls must be a bindable inner class--a class decorated with
#     @BoundInnerClass, @UnboundInnerClass, or @Bindable.
#     outer should be an instance of the outer class, or None.
#
#     If outer is an instance, returns the bound version
#     of cls for that instance.
#
#     If outer is None, returns the unbound version of cls.
#
#     Example:
#         class Outer:
#             @BoundInnerClass
#             class Inner:
#                 def __init__(self, outer):
#                     self.outer = outer
#
#         o = Outer()
#         BoundInner = bind(Outer.Inner, o)
#
#         instance = BoundInner()  # o is passed in automatically
#         assert instance.outer is o
#
#         # Unbind by passing in None
#         assert bind(BoundInner, None) is Outer.Inner
#         assert bind(BoundInner, None) is unbound(BoundInner)
#     """
#     if outer is None:
#         return unbound(cls)
#
#     if not is_bindable(cls):
#         raise ValueError(
#             f"{cls.__name__} is not a bindable inner class"
#         )
#
#     unbound_cls = unbound(cls)
#     outer_class = type(outer)
#     cache = _get_cache(outer)
#
#     # Check cache first
#     bound_class = cache.get(unbound_cls)
#     if bound_class is not None:
#         return bound_class
#
#     # Try to find cls itself as a BoundInnerClass on outer_class
#     resolved = _BoundInnerClassBase._resolve_descriptor(outer, outer_class, unbound_cls)
#     if resolved is not None:
#         return resolved
#
#     # cls is a @Bindable class - search its bases for a BoundInnerClass
#     bound_base = None
#     for base in unbound_cls.__bases__:
#         if not is_bindable(base):
#             continue
#
#         resolved = _BoundInnerClassBase._resolve_descriptor(outer, outer_class, base)
#         if resolved is not None:
#             bound_base = resolved
#             break
#
#     if bound_base is None:
#         raise ValueError(
#             f"{cls.__name__} doesn't inherit from any BoundInnerClass of {outer_class.__name__}"
#         )
#
#     # Create bound class using cache
#     # Include unbound_cls as extra_base for proper MRO so super() works
#     bound_class = _make_bound_class(unbound_cls, outer, bound_base, extra_base=unbound_cls)
#     bound_class = cache.set(unbound_cls, bound_class)
#     return bound_class


@export
def bound_to(cls):
    """
    Return the outer instance that cls is bound to, or None.

    If cls is a bindable inner class that was bound to an outer
    instance, returns that outer instance.  Otherwise returns None.

    BoundInnerClass doesn't keep strong references to outer instances.
    If cls was bound to an object that has since been destroyed,
    bound_to(cls) will return None.
    """
    if not isinstance(cls, type):
        return None
    info = cls.__dict__.get(_BOUNDINNERCLASS_INNER_ATTR)
    if info is None:
        return None
    outer_weakref = info[1]
    if outer_weakref is None:
        return None
    return outer_weakref()


@export
def type_bound_to(instance):
    """
    Return the outer instance that instance's type is bound to, or None.

    If type(instance) is a bindable inner class that was bound to an
    outer instance, returns that outer instance.  Otherwise returns None.

    BoundInnerClass doesn't keep strong references to outer instances.
    If type(instance) was bound to an object that has since been
    destroyed, type_bound_to(instance) will return None.
    """
    return bound_to(type(instance))


mm()
