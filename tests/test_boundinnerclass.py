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

import copy
import gc
import inspect
import pickle
import sys
import threading
import types
import unittest
import weakref

import bigtestlib
bigtestlib.preload_local_big()

from big.test import raises

from big.boundinnerclass import *

from big.boundinnerclass import (
    _BoundInnerClassBase,
    _BoundInnerClassCache,
    _BOUNDINNERCLASS_INNER_ATTR,
    _ClassProxy,
    _get_outer,
    _bound_class_new_or_init_signature,
    _unbound,
    )


class Node:
    # module-level on purpose: test_namesake_plain_base defines an inner
    # class Node(Node), and a name assigned in a class body resolves
    # via locals-then-GLOBALS, skipping enclosing function scope--just
    # like the real-world "from elsewhere import Node" pattern.
    def marker(self):
        return 'plain'


class PickleableOuter:
    # module-level so pickle can find it by name
    @BoundInnerClass
    class Inner:
        def __init__(self, outer):
            self.outer = outer


def make_bound_outer():
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

    o = Outer()
    o.Inner()      # populate the cache
    return o

def test_copy_rebinds_to_the_copy():
    o = make_bound_outer()
    o2 = copy.copy(o)
    assert o2.Inner().outer is o2
    # and the original is unharmed
    assert o.Inner().outer is o

def test_deepcopy_rebinds_to_the_copy():
    # regression: this used to raise TypeError, deepcopy can't
    # copy the threading.Lock inside the cache
    o = make_bound_outer()
    o2 = copy.deepcopy(o)
    assert o2.Inner().outer is o2
    assert o.Inner().outer is o

def test_cache_copy_protocol():
    # copying the cache object itself--__copy__ and __deepcopy__
    # both--produces a fresh, empty, unowned cache.  cheaper than
    # copying (the ownership check would only throw the copy
    # away), and it keeps copy/deepcopy away from the cache's
    # threading.Lock.
    o = make_bound_outer()
    cache = getattr(o, BOUNDINNERCLASS_OUTER_ATTR)
    for duplicate in (copy.copy(cache), copy.deepcopy(cache)):
        assert isinstance(duplicate, type(cache))
        assert duplicate is not cache
        # unowned: it doesn't believe it belongs to o
        assert not (duplicate._belongs_to(o))

def test_pickle_roundtrip_rebinds():
    # regression: this used to raise PicklingError on the cached
    # dynamically-created bound class
    o = PickleableOuter()
    o.Inner()
    o2 = pickle.loads(pickle.dumps(o))
    assert o2.Inner().outer is o2
    assert o.Inner().outer is o

def test_naive_user_deepcopy_sharing_dict():
    """A user __deepcopy__ that shares __dict__ transplants the
    cache onto the copy; ownership validation must heal it."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

        def __deepcopy__(self, memo):
            dupe = Outer.__new__(Outer)
            dupe.__dict__.update(self.__dict__)   # shares the cache!
            return dupe

    o = Outer()
    o.Inner()
    o2 = copy.deepcopy(o)
    assert o2.Inner().outer is o2
    assert o.Inner().outer is o

def test_caching_still_effective_after_duplication():
    o = make_bound_outer()
    o2 = copy.copy(o)
    assert o2.Inner is o2.Inner
    assert o.Inner is o.Inner
    assert o.Inner is not o2.Inner


def test_basic_binding():
    """Inner class receives outer instance automatically."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

    o = Outer()
    i = o.Inner()
    assert i.outer is o

def test_class_access_returns_unwrapped():
    """Accessing via class returns the original unwrapped class."""
    class Outer:
        @BoundInnerClass
        class Inner:
            pass

    assert isinstance(Outer.Inner, type)

def test_instance_access_returns_bound():
    """Accessing via instance returns a bound subclass."""
    class Outer:
        @BoundInnerClass
        class Inner:
            pass

    o = Outer()
    BoundInner = o.Inner
    assert issubclass(BoundInner, Outer.Inner)

def test_different_instances_different_bound_classes():
    """Different outer instances produce different bound classes."""
    class Outer:
        @BoundInnerClass
        class Inner:
            pass

    o1 = Outer()
    o2 = Outer()
    assert o1.Inner is not o2.Inner

def test_bound_class_is_cached():
    """Repeated access returns the same bound class."""
    class Outer:
        @BoundInnerClass
        class Inner:
            pass

    o = Outer()
    assert o.Inner is o.Inner

def test_additional_args():
    """Additional arguments are passed through."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer, x, y=None):
                self.outer = outer
                self.x = x
                self.y = y

    o = Outer()
    i = o.Inner(42, y='hello')
    assert i.outer is o
    assert i.x == 42
    assert i.y == 'hello'

def test_isinstance_with_unbound():
    """Instances are isinstance of the unbound class."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

    o = Outer()
    i = o.Inner()
    assert isinstance(i, Outer.Inner)

def test_isinstance_with_bound():
    """Instances are isinstance of their bound class."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

    o = Outer()
    i = o.Inner()
    assert isinstance(i, o.Inner)

def test_custom_repr():
    """Bound instances get a custom repr."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

    o = Outer()
    i = o.Inner()
    r = repr(i)
    assert 'Inner' in r
    assert 'bound to' in r

def test_no_custom_repr_if_defined():
    """Custom repr is not added if class defines its own."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

            def __repr__(self):
                return 'custom repr'

    o = Outer()
    i = o.Inner()
    assert repr(i) == 'custom repr'


def test_new_only_receives_outer():
    """A BoundInnerClass with only __new__ receives outer after cls."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __new__(cls, outer, x, y=None):
                self = super().__new__(cls)
                self.outer_from_new = outer
                self.x = x
                self.y = y
                return self

    o = Outer()
    i = o.Inner(42, y='hello')

    assert i.outer_from_new is o
    assert i.x == 42
    assert i.y == 'hello'
    assert isinstance(i, Outer.Inner)
    assert isinstance(i, o.Inner)

def test_new_and_init_both_receive_outer():
    """A BoundInnerClass defining both __new__ and __init__ gets outer in both."""
    calls = []

    class Outer:
        @BoundInnerClass
        class Inner:
            def __new__(cls, outer, x):
                self = super().__new__(cls)
                self.outer_from_new = outer
                self.x_from_new = x
                calls.append(('new', outer, x))
                return self

            def __init__(self, outer, x):
                self.outer_from_init = outer
                self.x_from_init = x
                calls.append(('init', outer, x))

    o = Outer()
    i = o.Inner(7)

    assert i.outer_from_new is o
    assert i.outer_from_init is o
    assert i.x_from_new == 7
    assert i.x_from_init == 7
    assert calls == [('new', o, 7), ('init', o, 7)]

def test_new_signature_hides_outer():
    """Bound class signatures hide outer for __new__ as well as __init__."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __new__(cls, outer, x, y=None):
                self = super().__new__(cls)
                self.outer = outer
                self.x = x
                self.y = y
                return self

    o = Outer()

    sig = inspect.signature(o.Inner)
    assert list(sig.parameters.keys()) == ['x', 'y']

    sig = inspect.signature(o.Inner.__new__)
    assert list(sig.parameters.keys()) == ['x', 'y']

    i = o.Inner(1, y=2)
    assert i.outer is o
    assert i.x == 1
    assert i.y == 2

def test_new_signature_preferred_when_new_and_init_both_exist():
    """Class signature follows Python's convention and prefers __new__."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __new__(cls, outer, x, y=None):
                self = super().__new__(cls)
                self.outer_from_new = outer
                return self

            def __init__(self, outer, z):
                self.outer_from_init = outer
                self.z = z

    o = Outer()
    i = o.Inner(3)
    sig = inspect.signature(o.Inner)
    assert list(sig.parameters.keys()) == ['x', 'y']

    init_sig = inspect.signature(o.Inner.__init__)
    assert list(init_sig.parameters.keys()) == ['z']

def test_bound_innerclass_inheritance_new_super():
    """super().__new__(cls) works in a BoundInnerClass hierarchy."""
    class Outer:
        @BoundInnerClass
        class Parent:
            def __new__(cls, outer):
                self = super().__new__(cls)
                self.parent_outer = outer
                self.parent_called = True
                return self

        @BoundInnerClass
        class Child(bound_inner_base(Parent)):
            def __new__(cls, outer, x):
                self = super().__new__(cls)
                self.child_outer = outer
                self.child_called = True
                self.x = x
                return self

    o = Outer()
    c = o.Child(99)

    assert c.parent_outer is o
    assert c.child_outer is o
    assert c.parent_called
    assert c.child_called
    assert c.x == 99
    assert isinstance(c, o.Parent)

def test_child_inherits_bound_parent_new():
    """A child without __new__ can inherit the bound parent's __new__."""
    class Outer:
        @BoundInnerClass
        class Parent:
            def __new__(cls, outer, x):
                self = super().__new__(cls)
                self.outer = outer
                self.x = x
                return self

        @BoundInnerClass
        class Child(bound_inner_base(Parent)):
            pass

    o = Outer()
    c = o.Child(123)

    assert c.outer is o
    assert c.x == 123
    assert isinstance(c, o.Parent)

def test_regular_inherited_new_is_not_given_outer():
    """Inherited non-BoundInnerClass __new__ methods receive the normal user args only."""
    class RegularBase:
        def __new__(cls, value):
            self = super().__new__(cls)
            self.value_from_new = value
            return self

    class Outer:
        @BoundInnerClass
        class Inner(RegularBase):
            def __init__(self, outer, value):
                self.outer = outer
                self.value_from_init = value

    o = Outer()
    i = o.Inner('value')

    assert i.value_from_new == 'value'
    assert i.outer is o
    assert i.value_from_init == 'value'

def test_regular_inherited_init_is_not_given_outer():
    """Inherited non-BoundInnerClass __init__ methods receive the normal user args only."""
    class RegularBase:
        def __init__(self, value="default"):
            self.value_from_init = value

    class Outer:
        @BoundInnerClass
        class Inner(RegularBase):
            pass

    o = Outer()

    i = o.Inner('value')
    assert i.value_from_init == 'value'

    i = o.Inner()
    assert i.value_from_init == 'default'

@unittest.skipIf(sys.version_info < (3, 7), "bare inner subclassing needs __mro_entries__ (3.7+); 3.6 spells it bound_inner_base(Parent)")
def test_child_inherits_bound_parent_init():
    """A child without __init__ can inherit the bound parent's __init__."""
    class Outer:
        @BoundInnerClass
        class Parent:
            def __init__(self, outer, value):
                self.outer = outer
                self.value_from_init = value

        @BoundInnerClass
        class Child(Parent):
            pass

    o = Outer()
    i = o.Child('value')

    assert i.outer is o
    assert i.value_from_init == 'value'

def test_bound_class_keeps_outer_alive():
    """A bound class holds its outer strongly, like a bound method
    holds __self__--dropping every other reference to the outer
    must not break construction."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

    o = Outer()
    ref = weakref.ref(o)
    Bound = o.Inner

    del o
    gc.collect()
    assert ref() is not None            # Bound keeps it alive
    i = Bound()                            # ...so this just works
    assert i.outer is ref()
    assert bound_to(Bound) is ref()

    # and once the wrapper and instance are gone, the cycle
    # collector reclaims the outer
    del Bound, i
    gc.collect()
    assert ref() is None

def test_bound_class_keeps_outer_alive_new_path():
    """Same strong-reference guarantee through __new__."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __new__(cls, outer):
                self = super().__new__(cls)
                self.outer_from_new = outer
                return self

    o = Outer()
    Bound = o.Inner
    del o
    gc.collect()
    assert isinstance(Bound().outer_from_new, Outer)

def test_temporary_outer_idiom():
    """Outer().Inner(...)--outer as an unbound temporary--works:
    the bound class pins the temporary, exactly as obj.method(...)
    pins obj.  (Regression: with a weakref, this idiom's success
    depended on garbage collector timing.)"""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

    for _ in range(100):
        i = Outer().Inner()
        assert isinstance(i.outer, Outer)

def test_builtin_new_is_not_given_outer():
    """Builtin/C-level __new__ methods don't receive outer."""
    class Outer:
        @BoundInnerClass
        class Inner(int):
            pass

    o = Outer()
    i = o.Inner(5)

    assert i == 5
    assert isinstance(i, int)
    assert isinstance(i, o.Inner)

def test_empty_inner_class_is_constructible():
    """A BoundInnerClass with object.__init__ should not receive outer there."""
    class Outer:
        @BoundInnerClass
        class Inner:
            pass

    o = Outer()
    i = o.Inner()

    assert isinstance(i, Outer.Inner)
    assert isinstance(i, o.Inner)




def test_unbound_does_not_inject_outer():
    """UnboundInnerClass does not inject outer parameter."""
    class Outer:
        @BoundInnerClass
        class Parent:
            def __init__(self, outer):
                self.outer = outer

        @UnboundInnerClass
        class Child(bound_inner_base(Parent)):
            def __init__(self):
                super().__init__()

    o = Outer()
    c = o.Child()
    assert c.outer is o


def test_inherit_without_cls_hack():
    """Subclassing works without .cls - __mro_entries__ handles it."""
    class Outer:
        @BoundInnerClass
        class Parent:
            def __init__(self, outer):
                self.outer = outer

        @BoundInnerClass
        class Child(bound_inner_base(Parent)):
            def __init__(self, outer):
                super().__init__()
                self.child = True

    o = Outer()
    c = o.Child()
    assert c.outer is o
    assert c.child
    assert isinstance(c, Outer.Parent)

def test_inherit_from_bound_inner_class():
    """Subclass of BoundInnerClass inside outer class works correctly."""
    class Outer:
        @BoundInnerClass
        class Parent:
            def __init__(self, outer):
                self.outer = outer

        @BoundInnerClass
        class Child(bound_inner_base(Parent)):
            def __init__(self, outer, x):
                super().__init__()
                self.x = x

    o = Outer()
    c = o.Child(42)
    assert c.outer is o
    assert c.x == 42

def test_namesake_inner_class_across_outer_hierarchy():
    """Outer2(Outer) defining Node(Outer.Node)--same name--chains correctly."""
    class Outer:
        @BoundInnerClass
        class Node:
            def __init__(self, outer):
                self.outer = outer

    class Outer2(Outer):
        @BoundInnerClass
        class Node(Outer.Node):
            def __init__(self, outer):
                self.outer2 = outer
                super().__init__()

    o2 = Outer2()
    n = o2.Node()
    assert n.outer is o2
    assert n.outer2 is o2

    # same, but the child inner class has no __init__ of its own
    class Outer3(Outer):
        @BoundInnerClass
        class Node(Outer.Node):
            pass

    o3 = Outer3()
    n = o3.Node()
    assert n.outer is o3

    # sanity: the parent outer class is unaffected
    o = Outer()
    assert o.Node().outer is o

def test_namesake_bound_base_from_other_outer():
    """Inheriting another outer INSTANCE's bound namesake class:
    the bound base injects its own outer, as it always did."""
    class Outer1:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

    o1 = Outer1()

    class Outer2:
        @BoundInnerClass
        class Inner(o1.Inner):
            def __init__(self, outer):
                self.outer2 = outer
                super().__init__()

    o2 = Outer2()
    i = o2.Inner()
    assert i.outer2 is o2
    assert i.outer is o1     # the bound base keeps ITS outer

def test_renamed_bound_base_from_other_outer():
    """Inheriting another instance's bound class works under ANY name.
    (Regression: it used to raise RuntimeError unless the subclass
    happened to share the base's name.)"""
    class Outer1:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

    o1 = Outer1()

    class Outer2:
        @BoundInnerClass
        class Renamed(o1.Inner):
            def __init__(self, outer):
                self.outer2 = outer
                super().__init__()

    o2 = Outer2()
    i = o2.Renamed()
    assert i.outer is o1     # the bound base keeps ITS outer
    assert i.outer2 is o2

@unittest.skipIf(sys.version_info < (3, 7), "bare inner subclassing needs __mro_entries__ (3.7+); 3.6 spells it bound_inner_base(B)")
def test_sibling_name_collision_cannot_recurse():
    """A foreign base merely NAMED like a sibling inner class must not
    send binding into infinite recursion.  (Regression: resolving a
    base by name could re-enter a mid-bind descriptor--RecursionError.)"""
    class ForeignA:
        pass
    ForeignA.__name__ = 'A'

    class Outer:
        @BoundInnerClass
        class B(ForeignA):
            def __init__(self, outer):
                self.outer = outer

        @BoundInnerClass
        class A(B):
            def __init__(self, outer):
                self.a_outer = outer
                super().__init__()

    o = Outer()
    a = o.A()
    assert a.outer is o
    assert a.a_outer is o

def test_namesake_new_chaining():
    """__new__ chains across a namesake outer-hierarchy pair too."""
    class Outer:
        @BoundInnerClass
        class Node:
            def __new__(cls, outer):
                self = super().__new__(cls)
                self.outer_from_new = outer
                return self

    class Outer2(Outer):
        @BoundInnerClass
        class Node(Outer.Node):
            def __new__(cls, outer):
                self = super().__new__(cls)
                self.outer2_from_new = outer
                return self

    o2 = Outer2()
    n = o2.Node()
    assert n.outer_from_new is o2
    assert n.outer2_from_new is o2

def test_namesake_plain_base():
    """An unrelated plain base sharing the inner class's name
    is treated exactly like a plain base of any other name.
    (The plain Node base is defined at module level.)"""
    class Outer:
        @BoundInnerClass
        class Node(Node):
            def __init__(self, outer):
                self.outer = outer

    o = Outer()
    n = o.Node()
    assert n.outer is o
    assert n.marker() == 'plain'

def test_namesake_unresolvable_bic_base_raises():
    """A decorated namesake base not on the outer's MRO raises,
    same as the differently-named case."""
    class Elsewhere:
        @BoundInnerClass
        class Node:
            def __init__(self, outer): # pragma: no cover
                # never called--this test asserts binding raises
                self.outer = outer

    class Outer:
        @BoundInnerClass
        class Node(Elsewhere.Node):
            pass

    o = Outer()
    with raises(RuntimeError) as cm:
        o.Node
    assert "Can't find a BoundInnerClass descriptor" in str(cm.exception)

def test_unbound_child_of_bound_parent():
    """UnboundInnerClass child of BoundInnerClass parent."""
    class Outer:
        @BoundInnerClass
        class Parent:
            def __init__(self, outer):
                self.outer = outer

        @UnboundInnerClass
        class Child(bound_inner_base(Parent)):
            def __init__(self):
                super().__init__()

    o = Outer()
    c = o.Child()
    assert c.outer is o
    assert isinstance(c, Outer.Parent)
    assert isinstance(c, o.Parent)


def test_unbound_bound_class():
    """unbound() returns unbound version of bound class."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):  # pragma: nocover
                self.outer = outer

    o = Outer()
    BoundInner = o.Inner
    result = unbound(BoundInner)
    assert result is Outer.Inner

def test_unbound_unbound_class():
    """unbound() returns unbound class unchanged."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):  # pragma: nocover
                self.outer = outer

    result = unbound(Outer.Inner)
    assert result is Outer.Inner

def test_unbound_regular_class():
    """unbound() returns regular class unchanged."""
    class Regular:
        pass

    result = unbound(Regular)
    assert result is Regular


def test_unbound_requires_a_class():
    """unbound() raises TypeError for non-class argument."""
    with raises(TypeError) as cm:
        unbound(3.14)
    assert "must be a class" in str(cm.exception)
    assert "float" in str(cm.exception)

def test_unbound_child_inherits_from_bound_raises():
    """unbound() raises if child inherits directly from a bound class."""
    class Outer:
        @BoundInnerClass
        class Parent:
            def __init__(self, outer):  # pragma: nocover
                self.outer = outer

    o = Outer()
    BoundParent = o.Parent

    class Child(BoundParent):
        def __init__(self, outer):  # pragma: nocover
            super().__init__()

    with raises(ValueError) as cm:
        unbound(Child)
    assert "inherits from a bound class" in str(cm.exception)
    assert "has no unbound version" in str(cm.exception)


def test_bound_to():
    """bound_to returns the instance for bound inner class, or None for unbound."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

    assert bound_to(Outer.Inner) is None

    o = Outer()
    BoundInner = o.Inner
    assert o is bound_to(BoundInner)
    instance = BoundInner()
    assert instance.outer is o

def test_bound_to_false_no_cache():
    """bound_to returns None on classes not using BoundInnerClass."""
    assert bound_to(str) is None

def test_type_bound_to():
    """type_bound_to returns outer for instance of bound class."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

    o = Outer()
    i = o.Inner()
    assert o is type_bound_to(i)
    assert i.outer is o

def test_bound_to_with_non_class():
    """bound_to returns None for non-class arguments."""
    with raises(TypeError):
        bound_to(42)
    with raises(TypeError):
        bound_to("string")
    with raises(TypeError):
        bound_to(None)


def test_outer_with_dict():
    """Works with normal class (has __dict__)."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

    o = Outer()
    i = o.Inner()
    assert i.outer is o
    assert BOUNDINNERCLASS_OUTER_ATTR in o.__dict__

def test_outer_with_slots_and_cache_slot():
    """Works with __slots__ that includes cache slot and __weakref__."""
    class Outer:
        __slots__ = ('__weakref__', 'x') + BOUNDINNERCLASS_OUTER_SLOTS

        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

    o = Outer()
    i = o.Inner()
    assert i.outer is o

def test_outer_with_slots_no_cache_slot_raises():
    """Raises TypeError if __slots__ without cache slot or __dict__."""
    class Outer:
        __slots__ = ('x',)

        @BoundInnerClass
        class Inner:
            pass

    o = Outer()
    with raises(TypeError) as cm:
        o.Inner
    assert BOUNDINNERCLASS_OUTER_ATTR in str(cm.exception)
    assert '__weakref__' in str(cm.exception)


def test_outer_lifetime_follows_bound_class():
    """The outer lives exactly as long as something needs it:
    pinned while a bound class exists, reclaimed (by the cycle
    collector) once the last wrapper is gone."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):  # pragma: nocover
                self.outer = outer

    o = Outer()
    ref = weakref.ref(o)
    BoundInner = o.Inner
    assert o is bound_to(BoundInner)

    del o
    gc.collect()
    assert ref() is not None    # pinned by BoundInner

    del BoundInner
    gc.collect()                   # outer -> cache -> wrapper -> outer
    assert ref() is None       # ...is a cycle; gc reclaims it


def test_unbound_and_bound_signatures():
    """Test signature behavior for both unbound and bound access."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer, x, y=None):
                self.outer = outer
                self.x = x
                self.y = y

    sig = inspect.signature(Outer.Inner)
    params = list(sig.parameters.keys())
    assert params == ['outer', 'x', 'y']

    o = Outer()
    sig = inspect.signature(o.Inner)
    params = list(sig.parameters.keys())
    assert params == ['x', 'y']

    sig = inspect.signature(o.Inner.__init__)
    params = list(sig.parameters.keys())
    assert params == ['x', 'y']

    i = o.Inner(42, y='hello')
    assert i.outer is o
    assert i.x == 42
    assert i.y == 'hello'

def test_signature_with_args_kwargs():
    """Signature works with *args and **kwargs."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer, x, *args, **kwargs):
                self.outer = outer
                self.x = x
                self.args = args
                self.kwargs = kwargs

    o = Outer()
    sig = inspect.signature(o.Inner)
    params = list(sig.parameters.keys())
    assert params == ['x', 'args', 'kwargs']

    i = o.Inner(1, 2, 3, foo='bar')
    assert i.outer is o
    assert i.x == 1
    assert i.args == (2, 3)
    assert i.kwargs == {'foo': 'bar'}

def test_signature_forwarding_init():
    """Regression test.  An __init__ that receives outer via *args--
        like the generic forwarding __init__(self, *args, **kwargs)--
        used to have its *args elided from the reported signature,
        as though it were the "outer" parameter."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

    o = Outer()
    sig = inspect.signature(o.Inner)
    assert list(sig.parameters) == ['args', 'kwargs']

    i = o.Inner(1, 2, foo='bar')
    assert i.args[0] is o   # outer arrives via *args
    assert i.args[1:] == (1, 2)
    assert i.kwargs == {'foo': 'bar'}

def test_signature_forwarding_new():
    """Regression test.  The __new__ flavor of
        test_signature_forwarding_init."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __new__(cls, *args, **kwargs):
                instance = super().__new__(cls)
                instance.new_args = args
                return instance

    o = Outer()
    sig = inspect.signature(o.Inner)
    assert list(sig.parameters) == ['args', 'kwargs']

    i = o.Inner(3, 4)
    assert i.new_args[0] is o   # outer arrives via *args
    assert i.new_args[1:] == (3, 4)

def test_signature_preserves_defaults():
    """Signature preserves default values."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer, x, y=42, z='hello'):
                self.outer = outer
                self.x = x
                self.y = y
                self.z = z

    o = Outer()
    sig = inspect.signature(o.Inner)
    assert sig.parameters['y'].default == 42
    assert sig.parameters['z'].default == 'hello'

    i = o.Inner(1)
    assert i.outer is o
    assert i.y == 42
    assert i.z == 'hello'


def test_proxy_name():
    """Proxy forwards __name__."""
    class Outer:
        @BoundInnerClass
        class Inner:
            pass

    descriptor = Outer.__dict__['Inner']
    assert descriptor.__name__ == 'Inner'
    assert Outer.Inner.__name__ == 'Inner'

def test_proxy_doc():
    """Proxy forwards __doc__ when accessed through class."""
    class Outer:
        @BoundInnerClass
        class Inner:
            """Inner class docstring."""
            pass

    assert Outer.Inner.__doc__ == 'Inner class docstring.'
    descriptor = Outer.__dict__['Inner']
    assert descriptor.__wrapped__.__doc__ == 'Inner class docstring.'
    # the proxy itself must forward too--it must NOT report
    # BoundInnerClass's own docstring (regression: the forwarding
    # was shadowed by the decorator's class-dict entries)
    assert descriptor.__doc__ == 'Inner class docstring.'

def test_proxy_doc_of_undocumented_class():
    """Proxy of an undocumented class reports None, not the decorator's docstring."""
    class Outer:
        @BoundInnerClass
        class Inner:
            pass

    descriptor = Outer.__dict__['Inner']
    assert descriptor.__doc__ is None

def test_proxy_module():
    """Proxy forwards __module__ when accessed through class."""
    class Outer:
        @BoundInnerClass
        class Inner:
            pass

    assert Outer.Inner.__module__ == __name__
    descriptor = Outer.__dict__['Inner']
    assert descriptor.__wrapped__.__module__ == __name__
    # the proxy itself must forward too--it must NOT report
    # 'big.boundinnerclass' (regression: the forwarding was
    # shadowed by the decorator's class-dict entries)
    assert descriptor.__module__ == __name__

def test_proxy_getattr():
    """Proxy forwards attribute access."""
    class Outer:
        @BoundInnerClass
        class Inner:
            class_attr = 'hello'

    descriptor = Outer.__dict__['Inner']
    assert descriptor.class_attr == 'hello'
    assert Outer.Inner.class_attr == 'hello'

def test_subclass_from_proxy():
    """Can subclass from the proxy (uses __mro_entries__)."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

    class Child(Outer.Inner):
        def __init__(self, outer):
            super().__init__(outer)  # Must pass outer - not using bind()
            self.child_flag = True

    assert issubclass(Child, Outer.Inner)

    o = Outer()
    c = Child(o)
    assert c.outer is o
    assert c.child_flag

def test_proxy_cls_property():
    """Proxy .cls property returns wrapped class."""
    class Outer:
        @BoundInnerClass
        class Inner:
            pass

    descriptor = Outer.__dict__['Inner']
    assert descriptor.cls is Outer.Inner

def test_cls_backward_compatibility_for_inheritance():
    """The .cls property works for inheritance (backward compatibility)."""
    class Outer:
        @BoundInnerClass
        class Parent:
            def __init__(self, outer):
                self.outer = outer

        @BoundInnerClass
        class Child(Parent.cls):
            def __init__(self, outer):
                super().__init__()
                self.child = True

        @UnboundInnerClass
        class UnboundChild(Parent.cls):
            def __init__(self):
                super().__init__()

    o = Outer()

    c = o.Child()
    assert c.outer is o
    assert c.child

    uc = o.UnboundChild()
    assert uc.outer is o

def test_proxy_repr():
    """Proxy has informative repr."""
    class Outer:
        @BoundInnerClass
        class Inner:
            pass

    descriptor = Outer.__dict__['Inner']
    r = repr(descriptor)
    assert 'BoundInnerClass' in r
    assert 'Inner' in r

def test_proxy_delattr():
    """Proxy forwards delattr to wrapped."""
    class Inner:
        custom = 'value'

    proxy = _ClassProxy(Inner)
    assert proxy.custom == 'value'
    del proxy.custom
    assert not (hasattr(proxy, 'custom'))
    assert not (hasattr(Inner, 'custom'))

@unittest.skipIf(sys.version_info < (3, 7), "__qualname__ not in slots on 3.6")
def test_proxy_setattr_qualname():
    """Setting __qualname__ updates both proxy and wrapped."""
    class Inner:
        pass

    proxy = _ClassProxy(Inner)
    original_qualname = proxy.__qualname__
    proxy.__qualname__ = 'NewQualname'
    assert proxy.__qualname__ == 'NewQualname'
    assert Inner.__qualname__ == 'NewQualname'
    proxy.__qualname__ = original_qualname

def test_proxy_setattr_annotations():
    """Setting __annotations__ updates both proxy and wrapped."""
    class Inner:
        pass

    proxy = _ClassProxy(Inner)
    proxy.__annotations__ = {'x': int}
    assert proxy.__annotations__ == {'x': int}
    assert Inner.__annotations__ == {'x': int}


def test_instancecheck():
    """Proxy supports isinstance checks."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

    o = Outer()
    i = o.Inner()
    descriptor = Outer.__dict__['Inner']
    assert isinstance(i, descriptor)
    assert i.outer is o

def test_subclasscheck():
    """Proxy supports issubclass checks."""
    class Outer:
        @BoundInnerClass
        class Inner:
            pass

    class Child(Outer.Inner):
        pass

    descriptor = Outer.__dict__['Inner']
    assert issubclass(Child, descriptor)
    assert issubclass(Child, Outer.Inner)

def test_subclasscheck_with_wrapped_subclass():
    """issubclass works when subclass also has __wrapped__."""
    class Outer:
        @BoundInnerClass
        class Parent:
            pass

        @BoundInnerClass
        class Child(bound_inner_base(Parent)):
            pass

    parent_desc = Outer.__dict__['Parent']
    child_desc = Outer.__dict__['Child']
    assert issubclass(child_desc, parent_desc)
    assert issubclass(Outer.Child, Outer.Parent)


def test_signature_with_builtin_init():
    """Signature handling when __init__ has no inspectable signature."""
    class Outer:
        @BoundInnerClass
        class Inner(int):
            pass

    o = Outer()
    BoundInner = o.Inner
    assert BoundInner is not None
    assert issubclass(BoundInner, int)

def test_signature_with_minimal_params():
    """Signature handling when __init__ has fewer than 2 params."""
    sig = _bound_class_new_or_init_signature(lambda self: None)
    assert sig is not None
    assert len(list(sig.parameters)) == 0

def test_bound_signature_exception():
    """Test _bound_signature when inspect.signature raises."""
    result = _bound_class_new_or_init_signature(42)
    assert result is None

def test_get_cache_with_slots_and_dict():
    """Works with __slots__ that includes __dict__."""
    class Outer:
        __slots__ = ('__dict__', '__weakref__')

        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

    o = Outer()
    i = o.Inner()
    assert i.outer is o

def test_mro_entries_used_in_subclassing():
    """__mro_entries__ is called when subclassing from proxy."""
    class Outer:
        @BoundInnerClass
        class Inner:
            pass

    descriptor = Outer.__dict__['Inner']
    entries = descriptor.__mro_entries__((descriptor,))
    assert entries == (Outer.Inner,)

def test_base_wrap_not_implemented():
    """_BoundInnerClassBase._wrap raises NotImplementedError."""
    class Inner:
        pass

    base = _BoundInnerClassBase(Inner, True)
    o = object()

    with raises(NotImplementedError):
        base._wrap(o, Inner)

def test_proxy_with_object_lacking_qualname():
    """Proxy handles wrapped objects without __qualname__."""
    obj = types.SimpleNamespace()
    obj.__name__ = 'FakeClass'

    proxy = _ClassProxy(obj)
    assert proxy.__wrapped__ is obj
    assert proxy.__name__ == 'FakeClass'

def test_proxy_with_object_lacking_annotations():
    """Proxy handles wrapped objects without __annotations__."""
    obj = types.SimpleNamespace()
    obj.__name__ = 'FakeClass'

    proxy = _ClassProxy(obj)
    assert proxy.__wrapped__ is obj
    assert proxy.__name__ == 'FakeClass'

def test_setattr_wrapped_updates_qualname_and_annotations():
    """Setting __wrapped__ updates cached __qualname__ and __annotations__."""
    class Original:
        x: int

    class Replacement:
        y: str

    proxy = _ClassProxy(Original)
    assert 'Original' in proxy.__qualname__

    proxy.__wrapped__ = Replacement
    assert 'Replacement' in proxy.__qualname__
    assert proxy.__annotations__ == {'y': str}

def test_setattr_wrapped_with_missing_attrs():
    """Setting __wrapped__ to object without __qualname__/__annotations__."""
    class Original:
        pass

    replacement = types.SimpleNamespace()
    replacement.__name__ = 'Replacement'

    proxy = _ClassProxy(Original)
    proxy.__wrapped__ = replacement
    assert proxy.__wrapped__ is replacement

def test_class_proxy_setattr_forwarding():
    """_ClassProxy forwards setattr to wrapped for normal attributes."""
    class Inner:
        pass

    original_name = Inner.__name__
    original_module = Inner.__module__
    original_doc = Inner.__doc__

    proxy = _ClassProxy(Inner)

    proxy.__name__ = 'NewName'
    assert proxy.__name__ == 'NewName'
    assert Inner.__name__ == 'NewName'

    proxy.__module__ = 'new.module'
    assert proxy.__module__ == 'new.module'
    assert Inner.__module__ == 'new.module'

    proxy.__doc__ = 'New doc.'
    assert proxy.__doc__ == 'New doc.'
    assert Inner.__doc__ == 'New doc.'

    Inner.__name__ = original_name
    Inner.__module__ = original_module
    Inner.__doc__ = original_doc

def test_class_proxy_getattr_forwarding():
    """_ClassProxy __getattr__ forwards to wrapped."""
    class Inner:
        custom_attr = 'hello'

    proxy = _ClassProxy(Inner)
    assert proxy.custom_attr == 'hello'

def test_stale_cache_entry_detected():
    """Stale cache entries are detected and removed on get()."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

    o = Outer()
    # First access populates the cache
    BoundInner1 = o.Inner

    # Access cache internals
    cache = getattr(o, BOUNDINNERCLASS_OUTER_ATTR)
    inner_cls = Outer.Inner
    cache_key = (id(inner_cls), inner_cls.__name__)
    cached_class, _ = cache._cache[cache_key]

    # Create a dead weakref
    class Temp:
        pass
    temp = Temp()
    dead_ref = weakref.ref(temp)
    del temp

    # Replace cache entry with dead weakref
    cache._cache[cache_key] = (cached_class, dead_ref)

    # Now access again - the stale entry should be detected and removed
    BoundInner2 = o.Inner
    assert BoundInner2 is not None
    instance = BoundInner2()
    assert instance.outer is o


def test_same_name_base_skipped():
    """When a base has the same name as the inner class, it's skipped."""
    class Base:
        pass
    Base.__name__ = 'Inner'

    class Outer:
        @BoundInnerClass
        class Inner(Base):
            def __init__(self, outer):
                self.outer = outer

    o = Outer()
    i = o.Inner()
    assert i.outer is o
    assert isinstance(i, Base)


def test_outer_evaluates_to_false():
    """Regression: outer instance that evaluates to false still works."""
    class Outer:
        def __bool__(self):
            return False

        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

    o = Outer()
    assert not (o)
    assert Outer.Inner != o.Inner
    i = o.Inner()
    assert o == i.outer

def test_nested_boundinnerclass_inheritance_single_outer_injection():
    """Regression: nested BoundInnerClass inheritance injects outer only once."""
    class Outer:
        @BoundInnerClass
        class GrandParent:
            def __init__(self, outer):
                self.outer = outer
                self.grandparent_called = True

        @BoundInnerClass
        class Parent(bound_inner_base(GrandParent)):
            def __init__(self, outer):
                super().__init__()
                self.parent_called = True

        @BoundInnerClass
        class Child(bound_inner_base(Parent)):
            def __init__(self, outer):
                super().__init__()
                self.child_called = True

    o = Outer()
    c = o.Child()

    assert c.outer is o
    assert c.grandparent_called
    assert c.parent_called
    assert c.child_called


def test_boundinnerclass_at_module_scope():
    """@BoundInnerClass on a non-nested class raises clear error."""
    @BoundInnerClass
    class NotNested:
        def __init__(self, outer):  # pragma: nocover
            self.outer = outer

    with raises(TypeError) as cm:
        NotNested()
    assert "@BoundInnerClass" in str(cm.exception)
    assert "nested inside another class" in str(cm.exception)

def test_boundinnerclass_inside_method():
    """@BoundInnerClass on a class defined inside a method raises clear error."""
    class Outer:
        def make_inner(self):
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer
            return Inner()

    o = Outer()
    with raises(TypeError) as cm:
        o.make_inner()
    assert "@BoundInnerClass" in str(cm.exception)
    assert "nested inside another class" in str(cm.exception)

def test_unboundinnerclass_at_module_scope():
    """@UnboundInnerClass on a non-nested class raises clear error."""
    @UnboundInnerClass
    class NotNested:
        pass

    with raises(TypeError) as cm:
        NotNested()
    assert "@UnboundInnerClass" in str(cm.exception)
    assert "nested inside another class" in str(cm.exception)


def test_is_boundinnerclass_with_boundinnerclass():
    """is_boundinnerclass returns True for @BoundInnerClass decorated classes."""
    class Outer:
        @BoundInnerClass
        class Inner:
            pass

    assert is_boundinnerclass(Outer.Inner)

def test_is_boundinnerclass_with_unboundinnerclass():
    """is_boundinnerclass returns False for @UnboundInnerClass decorated classes."""
    class Outer:
        @BoundInnerClass
        class Parent:
            pass

        @UnboundInnerClass
        class Child(bound_inner_base(Parent)):
            pass

    assert not (is_boundinnerclass(Outer.Child))

def test_is_boundinnerclass_with_regular_class():
    """is_boundinnerclass returns False for regular classes."""
    class Regular:
        pass

    assert not (is_boundinnerclass(Regular))

def test_is_boundinnerclass_with_non_class():
    """is_boundinnerclass raises TypeError for non-class arguments."""
    with raises(TypeError):
        is_boundinnerclass(42)
    with raises(TypeError):
        is_boundinnerclass("string")
    with raises(TypeError):
        is_boundinnerclass(None)


def test_is_unboundinnerclass_with_unboundinnerclass():
    """is_unboundinnerclass returns True for @UnboundInnerClass decorated classes."""
    class Outer:
        @BoundInnerClass
        class Parent:
            pass

        @UnboundInnerClass
        class Child(bound_inner_base(Parent)):
            pass

    assert is_unboundinnerclass(Outer.Child)

def test_is_unboundinnerclass_with_boundinnerclass():
    """is_unboundinnerclass returns False for @BoundInnerClass decorated classes."""
    class Outer:
        @BoundInnerClass
        class Inner:
            pass

    assert not (is_unboundinnerclass(Outer.Inner))

def test_is_unboundinnerclass_with_regular_class():
    """is_unboundinnerclass returns False for regular classes."""
    class Regular:
        pass

    assert not (is_unboundinnerclass(Regular))

def test_is_unboundinnerclass_with_non_class():
    """is_unboundinnerclass raises TypeError for non-class arguments."""
    with raises(TypeError):
        is_unboundinnerclass(42)
    with raises(TypeError):
        is_unboundinnerclass("string")
    with raises(TypeError):
        is_unboundinnerclass(None)


def test_is_bound_with_bound_class():
    """is_bound returns True for bound classes."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):  # pragma: nocover
                self.outer = outer

    o = Outer()
    BoundInner = o.Inner
    assert is_bound(BoundInner)

def test_is_bound_with_unbound_class():
    """is_bound returns False for unbound classes."""
    class Outer:
        @BoundInnerClass
        class Inner:
            pass

    assert not (is_bound(Outer.Inner))

def test_is_bound_with_regular_class():
    """is_bound returns False for regular classes."""
    class Regular:
        pass

    assert not (is_bound(Regular))

def test_is_bound_with_non_class():
    """is_bound returns False for non-class arguments."""
    with raises(TypeError):
        is_bound(42)
    with raises(TypeError):
        is_bound("string")
    with raises(TypeError):
        is_bound(None)


def test_get_renamed_parent_bic():
    """Accessing a child BoundInnerClass works when its parent BoundInnerClass has been renamed."""
    # Create Parent BoundInnerClass
    @BoundInnerClass
    class Parent:
        def __init__(self, outer):
            self.outer = outer
            self.parent_flag = True

    parent_cls = Parent.__wrapped__

    # Create Child BoundInnerClass that inherits from parent_cls
    @BoundInnerClass
    class Child(parent_cls):
        def __init__(self, outer):
            super().__init__()
            self.child_flag = True

    child_cls = Child.__wrapped__

    # Create Outer with Parent under a DIFFERENT name
    class Outer:
        pass

    Outer.RenamedParent = BoundInnerClass(parent_cls)
    Outer.Child = BoundInnerClass(child_cls)

    o = Outer()

    # Accessing o.Child should:
    # 1. Look at child_cls.__bases__, find parent_cls
    # 2. Fast path: getattr(o, 'Parent', None) returns None
    # 3. Slow path: search descriptors, find RenamedParent wraps parent_cls
    # 4. Add o.RenamedParent to wrapper_bases

    instance = o.Child()
    assert instance.outer is o
    assert instance.parent_flag
    assert instance.child_flag

    # Verify the MRO includes the bound parent
    assert o.RenamedParent in o.Child.__mro__


def test_bic_on_parent_class_found_via_mro():
    """Child outer class inherits a BoundInnerClass from parent outer class."""
    class ParentOuter:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer):
                self.outer = outer

    class ChildOuter(ParentOuter):
        @BoundInnerClass
        class ChildInner(ParentOuter.Inner):
            def __init__(self, outer):
                super().__init__()
                self.child_flag = True

    o = ChildOuter()
    c = o.ChildInner()
    assert c.outer is o
    assert c.child_flag
    assert isinstance(c, ParentOuter.Inner)

def test_renamed_bic_on_parent_class_found_via_mro():
    """Slow path finds a renamed BoundInnerClass on a parent outer class via MRO."""
    @BoundInnerClass
    class Inner:
        def __init__(self, outer):
            self.outer = outer

    inner_cls = Inner.__wrapped__

    class ParentOuter:
        pass

    # Store under a different name on the parent
    ParentOuter.RenamedInner = BoundInnerClass(inner_cls)

    @BoundInnerClass
    class Child(inner_cls):
        def __init__(self, outer):
            super().__init__()
            self.child_flag = True

    child_cls = Child.__wrapped__

    class ChildOuter(ParentOuter):
        pass

    ChildOuter.Child = BoundInnerClass(child_cls)

    o = ChildOuter()
    c = o.Child()
    assert c.outer is o
    assert c.child_flag


def test_deleted_parent_bic_raises():
    """Accessing child BoundInnerClass raises when parent BoundInnerClass is deleted from outer class."""
    @BoundInnerClass
    class Parent:
        def __init__(self, outer):  # pragma: nocover
            self.outer = outer

    parent_cls = Parent.__wrapped__

    @BoundInnerClass
    class Child(parent_cls):
        def __init__(self, outer):  # pragma: nocover
            super().__init__()

    child_cls = Child.__wrapped__

    class Outer:
        pass

    Outer.Parent = BoundInnerClass(parent_cls)
    Outer.Child = BoundInnerClass(child_cls)

    # Delete the parent -- now child can't bind
    del Outer.Parent

    o = Outer()
    with raises(RuntimeError) as cm:
        o.Child
    assert "Parent" in str(cm.exception)
    assert "Every BoundInnerClass base must be" in str(cm.exception)

def test_deleted_all_aliases_of_parent_bic_raises():
    """Accessing child BoundInnerClass raises when all aliases of parent BoundInnerClass are deleted."""
    @BoundInnerClass
    class Parent:
        def __init__(self, outer):  # pragma: nocover
            self.outer = outer

    parent_cls = Parent.__wrapped__

    @BoundInnerClass
    class Child(parent_cls):
        def __init__(self, outer):  # pragma: nocover
            super().__init__()

    child_cls = Child.__wrapped__

    class Outer:
        pass

    Outer.Parent = BoundInnerClass(parent_cls)
    Outer.Alias = Outer.Parent
    Outer.Child = BoundInnerClass(child_cls)

    # Delete both references to the parent
    del Outer.Parent
    del Outer.Alias

    o = Outer()
    with raises(RuntimeError) as cm:
        o.Child
    assert "Parent" in str(cm.exception)

def test_non_bindable_base_is_not_an_error():
    """Bases that aren't bindable are silently skipped (not an error)."""
    class RegularBase:
        pass

    class Outer:
        @BoundInnerClass
        class Inner(RegularBase):
            def __init__(self, outer):
                self.outer = outer

    o = Outer()
    # RegularBase isn't a BoundInnerClass, so it's silently skipped -- no error
    i = o.Inner()
    assert i.outer is o
    assert isinstance(i, RegularBase)


def test_medium_path_caches_alias():
    """After slow path finds a renamed BoundInnerClass, the medium path is used next time."""
    _BoundInnerClassBase._alias_cache.clear()
    @BoundInnerClass
    class Parent:
        def __init__(self, outer):
            self.outer = outer
            self.parent_flag = True

    parent_cls = Parent.__wrapped__

    @BoundInnerClass
    class Child(parent_cls):
        def __init__(self, outer):
            super().__init__()
            self.child_flag = True

    child_cls = Child.__wrapped__

    class Outer:
        pass

    Outer.RenamedParent = BoundInnerClass(parent_cls)
    Outer.Child = BoundInnerClass(child_cls)

    # First bind: slow path discovers "RenamedParent"
    o1 = Outer()
    c1 = o1.Child()
    assert c1.outer is o1
    assert c1.parent_flag
    assert c1.child_flag

    # Verify the descriptor was cached (as a weakref)
    alias_key = (id(parent_cls), id(Outer))
    assert alias_key in _BoundInnerClassBase._alias_cache
    assert _BoundInnerClassBase._alias_cache[alias_key]() is Outer.__dict__['RenamedParent']

    # Second bind on a different instance: medium path should find it
    o2 = Outer()
    c2 = o2.Child()
    assert c2.outer is o2
    assert c2.parent_flag
    assert c2.child_flag

def test_medium_path_stale_alias_falls_to_slow_path():
    """When cached alias becomes stale, slow path re-discovers the new name."""
    _BoundInnerClassBase._alias_cache.clear()
    @BoundInnerClass
    class Parent:
        def __init__(self, outer):
            self.outer = outer
            self.parent_flag = True

    parent_cls = Parent.__wrapped__

    @BoundInnerClass
    class Child(parent_cls):
        def __init__(self, outer):
            super().__init__()
            self.child_flag = True

    child_cls = Child.__wrapped__

    class Outer:
        pass

    Outer.FirstName = BoundInnerClass(parent_cls)
    Outer.Child = BoundInnerClass(child_cls)

    # First bind: slow path discovers "FirstName"
    o1 = Outer()
    c1 = o1.Child()
    assert c1.outer is o1

    alias_key = (id(parent_cls), id(Outer))
    assert _BoundInnerClassBase._alias_cache[alias_key]() is Outer.__dict__['FirstName']

    # Rename: delete FirstName, add SecondName (a NEW descriptor)
    del Outer.FirstName
    Outer.SecondName = BoundInnerClass(parent_cls)

    # Second bind on new instance: the cached weakref is dead (the
    # FirstName descriptor was collected), so the medium path falls
    # through to the slow path, which discovers the SecondName
    # descriptor
    o2 = Outer()
    c2 = o2.Child()
    assert c2.outer is o2
    assert c2.parent_flag
    assert c2.child_flag

    # Verify the cache was updated to the new descriptor
    assert _BoundInnerClassBase._alias_cache[alias_key]() is Outer.__dict__['SecondName']

def test_medium_path_stale_alias_and_no_replacement_raises():
    """When cached alias becomes stale and no replacement exists, raises error."""
    _BoundInnerClassBase._alias_cache.clear()
    @BoundInnerClass
    class Parent:
        def __init__(self, outer):  # pragma: nocover
            self.outer = outer

    parent_cls = Parent.__wrapped__

    @BoundInnerClass
    class Child(parent_cls):
        def __init__(self, outer):  # pragma: nocover
            super().__init__()

    child_cls = Child.__wrapped__

    class Outer:
        pass

    Outer.AliasedParent = BoundInnerClass(parent_cls)
    Outer.Child = BoundInnerClass(child_cls)

    # First bind: slow path discovers "AliasedParent"
    o1 = Outer()
    _ = o1.Child

    alias_key = (id(parent_cls), id(Outer))
    assert _BoundInnerClassBase._alias_cache[alias_key]() is Outer.__dict__['AliasedParent']

    # Delete the alias entirely
    del Outer.AliasedParent

    # Now try again: medium path finds stale alias, slow path finds nothing, error
    o2 = Outer()
    with raises(RuntimeError) as cm:
        o2.Child
    assert "Parent" in str(cm.exception)
    assert "Every BoundInnerClass base must be" in str(cm.exception)


def test_bound_inner_base_with_proxy():
    """Test that bound_inner_base works (in all versions)"""
    class Outer:
        @BoundInnerClass
        class Inner:
            pass

    # Get the proxy (descriptor) directly from __dict__
    proxy = Outer.__dict__['Inner']
    result = bound_inner_base(proxy)

    assert isinstance(result, _ClassProxy) or (result is Outer.Inner)
    assert result.__name__ == "Inner"


def test_get_outer_with_regular_class():
    """_get_outer returns None for regular classes."""
    class Regular:
        pass

    result = _get_outer(Regular)
    assert result is None

def test_get_outer_with_bound_class():
    """_get_outer returns the outer instance for bound classes."""
    class Outer:
        @BoundInnerClass
        class Inner: # pragma: nocover
            def __init__(self, outer):
                self.outer = outer

    o = Outer()
    BoundInner = o.Inner

    assert _get_outer(BoundInner) is o


def test_unbound_with_non_class():
    """_unbound returns None for non-class values."""
    result = _unbound("not a class")
    assert result is None

    result = _unbound(123)
    assert result is None

def test_unbound_with_non_bindable_class():
    """_unbound returns None for non-bindable classes."""
    class Regular:
        pass

    result = _unbound(Regular)
    assert result is None

def test_unbound_with_bound_class():
    """_unbound returns the unbound class for bound classes."""
    class Outer:
        @BoundInnerClass
        class Inner: # pragma: nocover
            def __init__(self, outer):
                self.outer = outer

    o = Outer()
    BoundInner = o.Inner

    result = _unbound(BoundInner)
    assert result is Outer.Inner


def test_cache_set_returns_existing_value():
    """cache.set returns existing value if already cached."""
    cache = _BoundInnerClassCache()

    class TestClass:
        pass

    class BoundClass1:
        pass

    class BoundClass2:
        pass

    # First set should store and return BoundClass1
    result1 = cache.set(TestClass, BoundClass1)
    assert result1 is BoundClass1

    # Second set with different bound class should return BoundClass1 (the existing one)
    result2 = cache.set(TestClass, BoundClass2)
    assert result2 is BoundClass1

    # Get should also return BoundClass1
    result3 = cache.get(TestClass)
    assert result3 is BoundClass1


def cached_signatures(outer_class, name):
    """Return the descriptor's _signatures slot for inspection."""
    descriptor = outer_class.__dict__[name]
    return descriptor._signatures

def test_signatures_cached_on_descriptor_and_reused():
    """First bind populates the cache; later binds reuse the same tuple."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer, x, y=3):
                self.outer = outer

    assert cached_signatures(Outer, 'Inner') is None

    o1 = Outer()
    _ = o1.Inner
    cached1 = cached_signatures(Outer, 'Inner')
    assert cached1 is not None
    functions, signatures = cached1
    assert functions[0] is None
    assert functions[1] is Outer.Inner.__init__
    assert list(signatures[1].parameters) == ['x', 'y']

    o2 = Outer()
    sig = inspect.signature(o2.Inner)
    assert list(sig.parameters) == ['x', 'y']
    i = o2.Inner(1)
    assert i.outer is o2
    cached2 = cached_signatures(Outer, 'Inner')
    assert cached1 is cached2

def test_plain_class_caches_signature_pair_of_nones():
    """A class with no __init__/__new__ caches (None, None) -- the
        slot's None means "uncomputed", a cached tuple of Nones means
        "computed, nothing to expose"."""
    class Outer:
        @BoundInnerClass
        class Plain:
            pass

    o1 = Outer()
    _ = o1.Plain()
    cached1 = cached_signatures(Outer, 'Plain')
    functions, signatures = cached1
    assert functions == (None, None)
    assert signatures == (None, None)

    o2 = Outer()
    _ = o2.Plain()
    assert cached1 is cached_signatures(Outer, 'Plain')

def test_replaced_init_is_reflected_on_next_bind():
    """Regression (stale signature cache): replacing __init__ after a
        bind must update both behavior and signature on the next bind."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer, x):
                self.got = ('old', x)

    o1 = Outer()
    _ = o1.Inner(1)
    assert list(inspect.signature(o1.Inner).parameters) == ['x']

    def replacement(self, outer, p, q):
        self.got = ('new', p, q)
    Outer.Inner.__init__ = replacement

    o2 = Outer()
    i = o2.Inner(1, 2)
    assert i.got == ('new', 1, 2)
    assert list(inspect.signature(o2.Inner).parameters) == ['p', 'q']
    assert list(inspect.signature(o2.Inner.__init__).parameters) == ['p', 'q']

def test_replaced_new_is_reflected_on_next_bind():
    """Regression (stale signature cache): replacing __new__ after a
        bind must update the signature on the next bind."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __new__(cls, outer, v):
                instance = super().__new__(cls)
                instance.v = v
                return instance

    o1 = Outer()
    assert list(inspect.signature(o1.Inner).parameters) == ['v']
    i = o1.Inner(7)
    assert i.v == 7

    def replacement(cls, outer, r, s):
        instance = object.__new__(cls)
        instance.rs = (r, s)
        return instance
    Outer.Inner.__new__ = replacement

    o2 = Outer()
    i = o2.Inner(1, 2)
    assert i.rs == (1, 2)
    assert list(inspect.signature(o2.Inner).parameters) == ['r', 's']

def test_deleted_init_drops_stale_signature():
    """Regression (stale signature cache): deleting __init__ after a
        bind must not leave the old signature on the next bound class."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer, x):
                pass

    o1 = Outer()
    assert list(inspect.signature(o1.Inner).parameters) == ['x']
    _ = o1.Inner(1)

    del Outer.Inner.__init__

    o2 = Outer()
    bound = o2.Inner
    assert '__signature__' not in bound.__dict__
    assert list(inspect.signature(bound).parameters) != ['x']
    _ = bound()

def test_deleted_new_falls_back_to_init_signature():
    """Regression (stale signature cache): deleting __new__ after a
        bind demotes the class signature to __init__'s on the next bind."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __new__(cls, outer, v=None):
                return super().__new__(cls)
            def __init__(self, outer, x=None, y=None):
                pass

    o1 = Outer()
    assert list(inspect.signature(o1.Inner).parameters) == ['v']
    _ = o1.Inner(1)

    del Outer.Inner.__new__

    o2 = Outer()
    assert list(inspect.signature(o2.Inner).parameters) == ['x', 'y']
    # no-args instantiation: a class that ever had a Python __new__
    # keeps the slot dispatcher in tp_new after deletion, so excess
    # constructor args reach object.__new__ and raise -- a CPython
    # quirk, nothing to do with BoundInnerClass
    _ = o2.Inner()

def test_added_init_gains_signature():
    """Regression (stale signature cache): adding __init__ to a class
        bound while plain must inject outer and expose the new signature."""
    class Outer:
        @BoundInnerClass
        class Plain:
            pass

    o1 = Outer()
    _ = o1.Plain()

    def added(self, outer, w):
        self.outer = outer
        self.w = w
    Outer.Plain.__init__ = added

    o2 = Outer()
    i = o2.Plain(9)
    assert i.outer is o2
    assert i.w == 9
    assert list(inspect.signature(o2.Plain).parameters) == ['w']

def test_rewrapped_descriptor_recomputes_signatures():
    """Regression (stale signature cache): reassigning __wrapped__
        must not reuse the old class's cached signatures."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer, x):
                pass

    o1 = Outer()
    assert list(inspect.signature(o1.Inner).parameters) == ['x']
    _ = o1.Inner(1)

    class Replacement:
        def __init__(self, outer, a, b, c):
            pass
    Outer.__dict__['Inner'].__wrapped__ = Replacement

    o2 = Outer()
    assert list(inspect.signature(o2.Inner).parameters) == ['a', 'b', 'c']
    _ = o2.Inner(1, 2, 3)

def test_existing_outer_keeps_consistent_wrapper_after_mutation():
    """An outer that bound before a mutation keeps its old wrapper --
        old behavior and old signature together, never mixed."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer, x):
                self.got = ('old', x)

    o = Outer()
    bound_before = o.Inner

    def replacement(self, outer, p, q):
        self.got = ('new', p, q)
    Outer.Inner.__init__ = replacement

    bound_after = o.Inner
    assert bound_before is bound_after
    i = bound_after(1)
    assert i.got == ('old', 1)
    assert list(inspect.signature(bound_after).parameters) == ['x']

    fresh = Outer()
    i2 = fresh.Inner(1, 2)
    assert i2.got == ('new', 1, 2)

def test_concurrent_first_bindings_are_correct():
    """Concurrent first binds may race to fill the cache; every thread
        must still observe a correct signature."""
    class Outer:
        @BoundInnerClass
        class Inner:
            def __init__(self, outer, x, y=3):
                self.outer = outer

    count = 8
    barrier = threading.Barrier(count)
    results = [None] * count
    def bind(index):
        barrier.wait()
        outer = Outer()
        instance = outer.Inner(index)
        results[index] = (list(inspect.signature(outer.Inner).parameters),
                          instance.outer is outer)
    threads = [threading.Thread(target=bind, args=(i,)) for i in range(count)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)
        assert not (t.is_alive())
    assert results == [(['x', 'y'], True)] * count
    assert cached_signatures(Outer, 'Inner') is not None



def run_tests(run=None):
    (run or bigtestlib.run)(name="big.boundinnerclass", module=__name__)


if __name__ == "__main__":  # pragma: no cover
    run_tests()
    bigtestlib.finish()
