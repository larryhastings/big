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


# note: inspect is deliberately NOT imported at module level.
# it's expensive (~13ms--it drags in dis, typing, and more), and
# it's only needed for lazy signature computation.  the one
# function that needs it imports it locally.
import sys
import threading
import types
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
        "Placeholder docstring, overwritten with the real documentation (shared by both version-specific variants) right after this symbol gets bound."
        return o
else: # pragma: nocover
    @export
    def bound_inner_base(o): # pragma: nocover
        "Placeholder docstring, overwritten with the real documentation (shared by both version-specific variants) right after this symbol gets bound."
        return o.cls

bound_inner_base.__doc__ = """
Simple wrapper for Python 3.6 compatibility for bound inner classes.

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



def _bound_class_new_or_init_signature(new_or_init):
    """
    Computes the correct signature for a bound class's __new__ and __init__.

    The __new__ and __init__ methods on a bound inner class start with two
    extra leading parameters that shouldn't be passed in when calling
    the method directly--from, say, the equivalent method in a subclass.
    The first is "cls" for __new__ or "self" for __init__; the second is
    "outer".  This function returns a signature for such a function with
    these two parameters elided.

    Returns None if signature cannot be determined.
    """
    import inspect

    try:
        signature = inspect.signature(new_or_init)
    except (ValueError, TypeError):
        return None

    # Elide the two leading implicit arguments the same way a call
    # with two leading positional arguments would consume them.
    # Note that a *args parameter absorbs leading positional arguments
    # without being consumed itself, so it must survive the elision:
    # for
    #     def __init__(self, *args, **kwargs)
    # "outer" is absorbed by *args at call time, and the correct
    # bound signature is (*args, **kwargs).
    remaining = 2 # == len(["cls/self", "outer"])
    bound_parameters = []
    for parameter in signature.parameters.values():
        if remaining:
            if parameter.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                remaining -= 1
                continue
            if parameter.kind == inspect.Parameter.VAR_POSITIONAL:
                remaining = 0
        bound_parameters.append(parameter)

    return inspect.Signature(bound_parameters, return_annotation=signature.return_annotation)



class _ClassProxy:
    """
    A minimal transparent proxy for class objects.

    Forwards attribute access to the wrapped class while allowing
    the proxy itself to act as a descriptor.

    Inspired by wrapt.ObjectProxy, but much simpler--we only need to
    proxy classes, not arbitrary objects with arithmetic operators, etc.

    Note: __qualname__, __annotations__, __doc__, and __module__ are
    copied from the wrapped class into instance attributes, and handled
    explicitly in __setattr__.  __qualname__ and __annotations__ *can't*
    be properties in Python.  __doc__ and __module__ *could* be... but
    the properties would never run: every subclass's class body
    implicitly defines '__doc__' (its docstring) and '__module__' in
    its class dict, and those plain-string entries shadow properties
    inherited from _ClassProxy.  Instance attributes, however, beat
    plain (non-descriptor) class attributes.  Which is also why
    _ClassProxy and its subclasses must not declare __slots__: the
    proxy needs an instance __dict__ for these attributes to live in.
    (There's one proxy per decorated class, so the memory cost of
    __dict__ is irrelevant.)
    """

    _COPIED_ATTRIBUTES = ('__annotations__', '__doc__', '__module__', '__qualname__')

    def _copy_wrapped_attributes(self, wrapped):
        for name in self._COPIED_ATTRIBUTES:
            try:
                object.__setattr__(self, name, getattr(wrapped, name))
            except AttributeError:
                pass

    def __init__(self, wrapped):
        object.__setattr__(self, '__wrapped__', wrapped)
        self._copy_wrapped_attributes(wrapped)

    @property
    def __name__(self):
        return self.__wrapped__.__name__

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
            self._copy_wrapped_attributes(value)
        elif name in self._COPIED_ATTRIBUTES:
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

    A cache belongs to exactly one outer instance, remembered by weak
    reference.  _get_cache validates ownership on every access, so a
    cache that gets transplanted onto some *other* instance--by
    copy.copy, by a user-defined __deepcopy__ or __getstate__ that
    naively shares __dict__, by __dict__.update, by whatever--is
    detected and replaced with a fresh cache on first use.

    Additionally, the copy and pickle protocol methods below duplicate
    a cache as a fresh empty unowned cache.  That's cheaper than
    actually copying it (the ownership check would only throw the
    copy away), and it keeps deepcopy and pickle away from our
    threading.Lock and our dynamically-created bound classes, neither
    of which they can process.

    This has reassuring redundancy: either mechanism alone covers
    most of the ways an outer instance can be duplicated; together
    they mean a duplicated outer always lazily re-binds its inner
    classes, no matter how it was duplicated.
    """

    __slots__ = ('_cache', '_lock', '_outer_ref')

    def __init__(self, outer=None):
        self._cache = {}
        self._lock = threading.Lock()
        self._outer_ref = weakref.ref(outer) if (outer is not None) else None

    def _belongs_to(self, outer):
        return (self._outer_ref is not None) and (self._outer_ref() is outer)

    def __copy__(self):
        return type(self)()

    def __deepcopy__(self, memo):
        return type(self)()

    def __reduce__(self):
        return (type(self), ())

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
    if (cache is not None) and cache._belongs_to(outer):
        return cache

    with _get_cache_lock:
        # Double-check after acquiring lock
        cache = getattr(outer, BOUNDINNERCLASS_OUTER_ATTR, None)
        if (cache is None) or (not cache._belongs_to(outer)):
            try:
                # Creating the cache raises TypeError if outer doesn't
                # support weak references; storing it raises AttributeError
                # if outer has __slots__ without our slot.  Either way the
                # advice to the user is the same.
                cache = _BoundInnerClassCache(outer)
                object.__setattr__(outer, BOUNDINNERCLASS_OUTER_ATTR, cache)
            except (AttributeError, TypeError):
                raise TypeError(
                    f"Cannot cache bound inner class on {type(outer).__name__}. "
                    f"Add '{BOUNDINNERCLASS_OUTER_ATTR}' to __slots__, and "
                    f"'__weakref__' too if no base class provides it "
                    f"(or remove '__slots__')."
                ) from None
        return cache


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


def _no_descriptor_error(base, outer_class):
    return RuntimeError(
        f"Can't find a BoundInnerClass descriptor for "
        f"{base.__qualname__!r} on {outer_class.__qualname__!r} "
        f"or any of its bases.  "
        f"Every BoundInnerClass base must be an inner class "
        f"of the outer class or one of its ancestors."
    )


class _BoundInnerClassBase(_ClassProxy):
    """
    Base descriptor for bound inner classes.

    Subclasses implement _wrap() to define how the wrapper class is created.
    """

    # _signatures caches bound signatures on the descriptor.  Either
    # None ("nothing cached") or a 2-tuple:
    #     ((__new__, __init__), (__new__signature, __init__signature))
    # The function pair is the validation key: the cached signatures are
    # used only while the wrapped class still resolves __new__ / __init__
    # to those exact function objects, so reassigning either -- or
    # reassigning __wrapped__ itself -- transparently recomputes.

    # Class-level cache mapping an (unbound_class, outer_class) pair to
    # a weakref of the descriptor the slow path discovered on the outer
    # class's MRO.  Shared across all instances, since which descriptor
    # serves a base is a property of the outer *class*, not any
    # particular outer instance.
    #
    # Keyed on (id(target_class), id(outer_class)).  If a class is GC'd
    # and its id reused, we might get a stale hit, but the medium path
    # always verifies (weakref alive, descriptor still wraps target)
    # before using the cached value, so a stale hit is harmless -- it
    # just falls through to the slow path.
    #
    # Entries are never evicted, so the cache grows monotonically for
    # the life of the process.  This is a deliberate tradeoff: entries
    # are tiny (an int pair -> a weakref, keeping nothing alive), and
    # they only accumulate for inner classes that inherit from other
    # inner classes, per outer class.  If some heroic workload ever
    # makes this a real leak, eviction can be arbitrarily dumb (even
    # clear() at a size cap), because correctness comes from the
    # verification on every hit; an evicted entry just costs one extra
    # slow-path scan.
    _alias_cache = {}
    _alias_cache_lock = threading.Lock()

    def __init__(self, wrapped, is_boundinnerclass):
        super().__init__(wrapped)

        # Must bypass _ClassProxy.__setattr__, which forwards unknown
        # attribute writes to the wrapped class.
        object.__setattr__(self, '_signatures', None)

        # Mark the wrapped class as participating in the bound inner class system.
        # Tuple: (unbound_class, outer, is_boundinnerclass)
        # outer is the instance a bound wrapper is bound to (held
        # strongly, like a bound method's __self__); None for
        # unbound (decorated but not yet bound) classes.
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
    def _resolve_descriptor(cls, outer, outer_class, target, cache):
        """
        Resolve the bound version of target on outer.

        target must be a decorated, unbound inner class (it carries
        the fingerprint, and the fingerprint's outer slot is None).
        Returns the bound version, or None if no descriptor wrapping
        target exists anywhere on outer_class's MRO.

        Three tiers, all keyed on identity--never on names:
          1. Fast: outer's own bind cache.  If target was already
             bound on this instance, that's the twin.
          2. Medium: the alias cache, which maps (target, outer_class)
             to a weakref of the descriptor a previous slow scan found.
          3. Slow: scan outer_class's MRO for a descriptor wrapping
             target, and remember it for next time.

        Identity resolution cannot recurse: it only ever invokes
        __get__ on descriptors of true ancestors, descending the
        inheritance DAG, which is acyclic.  (The name-based resolution
        this replaced could jump *sideways* through a coincidental
        name onto a descriptor that was mid-bind, and recurse.)
        """
        # Fast path: already bound on this instance?
        bound_result = cache.get(target)
        if bound_result is not None:
            return bound_result

        alias_key = (id(target), id(outer_class))

        # Medium path: do we remember which descriptor serves target?
        with cls._alias_cache_lock:
            descriptor_ref = cls._alias_cache.get(alias_key)
        if descriptor_ref is not None:
            descriptor = descriptor_ref()
            if (descriptor is not None) and (descriptor.__wrapped__ is target):
                return descriptor.__get__(outer, outer_class)
            # dead weakref, or recycled ids: fall through to the scan

        # Slow path: search outer_class's MRO by identity.
        _, descriptor = cls._find_descriptor_by_identity(outer_class, target)
        if descriptor is not None:
            with cls._alias_cache_lock:
                cls._alias_cache[alias_key] = weakref.ref(descriptor)
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
            # Build the bound version's bases: cls itself first (it
            # carries all its original bases along), then the bound
            # twin of every decorated-but-unbound base, so the MRO
            # visits bound wrappers before the classes they wrap.
            #
            # Bases are triaged by their fingerprint--the marker every
            # participating class carries in its own __dict__--never
            # by name.  Names can collide, and resolving a base by
            # name from inside a descriptor that owns that very name
            # re-enters __get__ mid-bind and recurses forever.
            wrapper_bases = [cls]

            for base in cls.__bases__:
                info = base.__dict__.get(_BOUNDINNERCLASS_INNER_ATTR)

                if info is None:
                    # A plain base, never decorated.  No descriptor
                    # wraps it, so it provably has no bound twin; it
                    # rides along inside cls like any normal base.
                    # (This is also object's exit, every time.)
                    continue

                if info[1] is not None:
                    # An already-bound wrapper--e.g. we inherit from
                    # o1.Inner, another outer instance's bound class.
                    # It's self-sufficient: its methods inject its own
                    # outer.  Hands off.
                    continue

                # A decorated, unbound base--the normal case.  Find
                # its twin bound to this outer, or die trying: a
                # decorated base with no descriptor anywhere on the
                # outer class's MRO is a configuration error.
                resolved = self._resolve_descriptor(outer, outer_class, base, cache)
                if resolved is None:
                    raise _no_descriptor_error(base, outer_class)
                wrapper_bases.append(resolved)

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

    If the inner class defines __new__, the same binding happens there:
    the outer instance is passed automatically as the *second* argument,
    immediately after "cls".  If the inner class defines both __new__
    and __init__, both methods receive the same outer instance:

        class Outer:
            @BoundInnerClass
            class Inner:
                def __new__(cls, outer, value):
                    self = super().__new__(cls)
                    return self

                def __init__(self, outer, value):
                    ...

    BoundInnerClass only binds __new__ and __init__ methods the
    decorated class *itself* defines.  Methods inherited from base
    classes are left alone: a regular base class's methods receive
    only the arguments you pass in, and a bound parent class (see
    below) injects outer into its own methods itself.

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

    The same rule applies to __new__ in a bound inner class hierarchy:
    call super().__new__(cls) and the bound parent class will receive
    outer automatically.

    This chaining works across an outer class hierarchy too, even when
    the inner classes share a name:

        class BaseApp:
            @BoundInnerClass
            class Config:
                def __init__(self, outer):
                    self.app = outer

        class MyApp(BaseApp):
            @BoundInnerClass
            class Config(BaseApp.Config):
                def __init__(self, outer):
                    super().__init__()

    Base classes are recognized by class *identity*, never by name.

    Note for pickle users: you can't pickle instances of bound inner classes.
    Bound inner classes are dynamically-created subclasses bound to specific
    outer instances, and there's no module/name lookup path to any particular
    bound subclass.  You get one by accessing the inner class through the outer
    instance, using the descriptor protocol.  Meanwhile, by default pickle only
    knows how to locate a class by inspecting the module object and looking up
    attributes by *name*.  So pickle just can't cope with bound inner classes;
    it looks up the class by name and finds the unbound version, which doesn't
    work.  Making BoundInnerClass support pickle would be ambitious, and it
    would require custom code in the bound class--it couldn't be made to work
    "automatically".  So as of now pickle is simply unsupported.

    The *outer* instance, though, copies, deepcopies, and pickles just
    fine: BoundInnerClass's internal cache doesn't travel with it.  The
    duplicate simply re-binds its inner classes, lazily, on first access,
    exactly like a fresh instance.

    A bound inner class holds a *strong* reference to its outer
    instance--exactly like a bound method holds __self__.  The
    tempting one-liner Outer().Inner() therefore just works: the
    bound class keeps the temporary outer alive.  Two consequences
    worth knowing: a bound class (or any instance of one, via its
    class) keeps its outer instance alive as long as it lives; and
    the resulting outer -> cache -> bound class -> outer reference
    cycle means outer instances that ever bound an inner class are
    reclaimed by the cycle collector, not by reference counting.

    Note for slots users: The "outer" class of a BoundInnerClass
    caches its bound inner classes in a special attribute, and must
    be weakly referenceable.  If that outer class uses __slots__, add
    a slot for BoundInnerClass's special attribute--use the predefined
    constant BOUNDINNERCLASS_OUTER_SLOTS--and, unless a base class
    already provides one, a '__weakref__' slot.  Example:

        class Foo:
            __slots__ = ('x', 'y', 'z', '__weakref__') + BOUNDINNERCLASS_OUTER_SLOTS

            @BoundInnerClass
            class Bar:
                ...

    If you support Python 3.6, please see the bound_inner_base
    function.

    See also big.ClassRegistry.
    """

    def __init__(self, wrapped):
        super().__init__(wrapped, True)

    def _wrap(self, outer, base):
        wrapped = self.__wrapped__

        # Cache the corrected bound signatures for __new__ and __init__
        # on the descriptor.  (inspect.signature is slow, ~15µs on a
        # mid-2020s processor.)
        #
        # The cache is naturally safe against races: the cache key is
        # the pair of function objects themselves, the Wrapper closes
        # over those same objects, and the entire cache entry (key and
        # payload together) is written with a single store.  So a
        # Wrapper's signature can never disagree with its behavior;
        # the worst a race can do is make two threads both recompute
        # the same signatures, which is harmless.
        #
        # The one change the cache genuinely can't detect: mutating a
        # cached function *in place* in a way that changes its
        # signature--assigning to its __signature__, __defaults__,
        # __annotations__, etc.--after a bind.  The function's identity
        # doesn't change, so the cache can't notice.  (*Replacing* the
        # method is detected the next time the class is bound--though
        # classes already bound keep the methods they closed over.)
        #
        # My sincere advice: don't mutate function signatures in
        # place.  (If you *must*--do it early, before BoundInnerClass
        # caches the signature.)
        #
        # Like __new__ below, only wrap an __init__ the decorated class
        # *itself* defines.  An __init__ inherited from a regular base
        # class doesn't expect outer; an __init__ inherited from a bound
        # parent gets outer injected by that parent's own wrapper, found
        # later in the MRO.
        init = wrapped.__dict__.get('__init__')
        class_defines_init = isinstance(init, types.FunctionType)
        if not class_defines_init:
            init = None

        new = wrapped.__dict__.get('__new__')
        if new and isinstance(new, (staticmethod, classmethod)):
            new = new.__func__
        class_defines_new = new and isinstance(new, types.FunctionType)
        if not class_defines_new:
            new = None

        new_and_init = (new, init)

        signatures_cache = self._signatures
        if (signatures_cache is not None) and (signatures_cache[0] == new_and_init):
            bound_signatures = signatures_cache[1]
            bound_new_signature, bound_init_signature = bound_signatures
        else:
            bound_new_signature = None if new is None else _bound_class_new_or_init_signature(new)
            bound_init_signature = None if init is None else _bound_class_new_or_init_signature(init)
            bound_signatures = (bound_new_signature, bound_init_signature)
            object.__setattr__(self, '_signatures', (new_and_init, bound_signatures))

        # The wrapper holds outer *strongly*--exactly like a bound
        # method holds __self__--so the tempting Outer().Inner()
        # one-liner just works: the bound class keeps the temporary
        # alive.
        #
        # The downside: this makes outer -> cache -> Wrapper -> outer
        # a strong reference cycle.  Sadly we now rely on the cycle
        # collector to collect these objects.  We tried weakrefs here;
        # that removed the cycle, but added a failure mode during
        # construction of temporaries where the outer reference could
        # go away first--it became a race against the garbage collector
        # that you would sporadically lose.  An infrequent but
        # catastrophic failure.
        class Wrapper(base):
            if class_defines_new:
                def __new__(cls, *args, **kwargs):
                    return new(cls, outer, *args, **kwargs)

            if class_defines_init:
                def __init__(self, *args, **kwargs):
                    init(self, outer, *args, **kwargs)

            # Custom repr if the wrapped class doesn't have one
            if wrapped.__repr__ is object.__repr__:
                def __repr__(self):
                    return "".join([
                        "<",
                        wrapped.__module__,
                        ".",
                        self.__class__.__name__,
                        " object bound to ",
                        repr(outer),
                        " at ",
                        hex(id(self)),
                        ">",
                    ])

        Wrapper.__name__ = wrapped.__name__
        Wrapper.__module__ = wrapped.__module__
        Wrapper.__qualname__ = wrapped.__qualname__
        Wrapper.__doc__ = wrapped.__doc__
        if hasattr(wrapped, '__annotations__'):
            Wrapper.__annotations__ = wrapped.__annotations__

        setattr(Wrapper, _BOUNDINNERCLASS_INNER_ATTR, (wrapped, outer, True))

        if bound_new_signature is not None:
            Wrapper.__new__.__signature__ = bound_new_signature

        if bound_init_signature is not None:
            Wrapper.__init__.__signature__ = bound_init_signature

        bound_Wrapper_signature = bound_new_signature or bound_init_signature
        if bound_Wrapper_signature is not None:
            Wrapper.__signature__ = bound_Wrapper_signature

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

    Accessing an UnboundInnerClass through an instance of the
    outer class still gives you a "bound" class; although this
    specific class won't get "outer" passed in automatically,
    base classes that are decorated with BoundInnerClass *will*.
    """

    def __init__(self, wrapped):
        super().__init__(wrapped, False)

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

        # Mark as an unbound inner class with info about its binding
        setattr(Wrapper, _BOUNDINNERCLASS_INNER_ATTR, (cls, outer, False))

        return Wrapper


@export
def unbound(cls):
    """
    Return the unbound version of a bound class.

    If cls is a bound inner class, returns the original unbound class.
    If cls is already unbound (or not a bindable inner class), returns cls.

    Raises ValueError if cls inherits *directly* from a bound class
    (e.g. "class Child(o.Inner)"), since such classes have no unbound
    version.  Raises TypeError if cls is not a class object.

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


def _get_outer(cls):
    """
    Extract the outer instance from a bound class.

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
    Raises TypeError if cls is not a class object.
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
    Raises TypeError if cls is not a class object.
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
    Raises TypeError if cls is not a class object.
    """
    if not isinstance(cls, type):
        raise TypeError(f"is_bound() argument must be a class, not {type(cls).__name__}")
    info = cls.__dict__.get(_BOUNDINNERCLASS_INNER_ATTR)
    if info is None:
        return False
    return info[1] is not None


@export
def bound_to(cls):
    """
    Return the outer instance that cls is bound to, or None.

    If cls is a bindable inner class that was bound to an outer
    instance, returns that outer instance.  If cls is any other
    variety of type object, returns None.  Raises TypeError if
    cls is not a class object.

    A bound class holds a strong reference to its outer instance,
    so this is guaranteed to be a live reference.
    """
    if not isinstance(cls, type):
        raise TypeError(f"bound_to() argument must be a class, not {type(cls).__name__}")
    info = cls.__dict__.get(_BOUNDINNERCLASS_INNER_ATTR)
    if info is None:
        return None
    return info[1]


@export
def type_bound_to(instance):
    """
    Return the outer instance that instance's type is bound to, or None.

    If type(instance) is a bindable inner class that was bound to an
    outer instance, returns that outer instance.  Otherwise returns None.

    A bound class holds a strong reference to its outer instance--
    so an instance of a bound inner class implies a live outer.
    """
    return bound_to(type(instance))


mm()
