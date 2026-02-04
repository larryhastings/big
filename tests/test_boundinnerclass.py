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


import inspect
import types
import unittest
import weakref

import bigtestlib

from big.boundinnerclass import *

from big.boundinnerclass import (
    _BoundInnerClassBase,
    _ClassProxy,
    _make_bound_signature,
    )


class TestBoundInnerClass(unittest.TestCase):
    """Tests for basic BoundInnerClass functionality."""

    def test_basic_binding(self):
        """Inner class receives outer instance automatically."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):
                    self.outer = outer

        o = Outer()
        i = o.Inner()
        self.assertIs(i.outer, o)

    def test_class_access_returns_unwrapped(self):
        """Accessing via class returns the original unwrapped class."""
        class Outer:
            @BoundInnerClass
            class Inner:
                pass

        # Outer.Inner returns the raw class (no proxy wrapper)
        self.assertTrue(isinstance(Outer.Inner, type))

    def test_instance_access_returns_bound(self):
        """Accessing via instance returns a bound subclass."""
        class Outer:
            @BoundInnerClass
            class Inner:
                pass

        o = Outer()
        BoundInner = o.Inner
        self.assertTrue(issubclass(BoundInner, Outer.Inner))

    def test_different_instances_different_bound_classes(self):
        """Different outer instances produce different bound classes."""
        class Outer:
            @BoundInnerClass
            class Inner:
                pass

        o1 = Outer()
        o2 = Outer()
        self.assertIsNot(o1.Inner, o2.Inner)

    def test_bound_class_is_cached(self):
        """Repeated access returns the same bound class."""
        class Outer:
            @BoundInnerClass
            class Inner:
                pass

        o = Outer()
        self.assertIs(o.Inner, o.Inner)

    def test_additional_args(self):
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
        self.assertIs(i.outer, o)
        self.assertEqual(i.x, 42)
        self.assertEqual(i.y, 'hello')


    def test_isinstance_with_unbound(self):
        """Instances are isinstance of the unbound class."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):
                    self.outer = outer

        o = Outer()
        i = o.Inner()
        self.assertIsInstance(i, Outer.Inner)

    def test_isinstance_with_bound(self):
        """Instances are isinstance of their bound class."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):
                    self.outer = outer

        o = Outer()
        i = o.Inner()
        self.assertIsInstance(i, o.Inner)

    def test_custom_repr(self):
        """Bound instances get a custom repr."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):
                    self.outer = outer

        o = Outer()
        i = o.Inner()
        r = repr(i)
        self.assertIn('Inner', r)
        self.assertIn('bound to', r)

    def test_no_custom_repr_if_defined(self):
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
        self.assertEqual(repr(i), 'custom repr')



class TestUnboundInnerClass(unittest.TestCase):
    """Tests for UnboundInnerClass decorator."""

    def test_unbound_does_not_inject_outer(self):
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
        # The outer is still passed via the MRO to Parent
        self.assertIs(c.outer, o)


class TestInheritance(unittest.TestCase):
    """Tests for inheritance with bound inner classes."""

    def test_inherit_without_cls_hack(self):
        """Subclassing works without .cls - __mro_entries__ handles it."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):
                    self.outer = outer

            # No .cls needed!
            @BoundInnerClass
            class Child(bound_inner_base(Parent)):
                def __init__(self, outer):
                    super().__init__()
                    self.child = True

        o = Outer()
        c = o.Child()
        self.assertIs(c.outer, o)
        self.assertTrue(c.child)
        self.assertIsInstance(c, Outer.Parent)

    def test_inherit_from_bound_inner_class(self):
        """Subclass of BIC inside outer class works correctly."""
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
        self.assertIs(c.outer, o)
        self.assertEqual(c.x, 42)

    def test_unbound_child_of_bound_parent(self):
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
        self.assertIs(c.outer, o)
        self.assertIsInstance(c, Outer.Parent)
        self.assertIsInstance(c, o.Parent)


class TestReparent(unittest.TestCase):
    """Tests for the reparent() function."""

    def test_reparent_basic(self):
        """reparent() creates working rebound class."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):
                    self.outer = outer

        class Child(Outer.Parent):
            def __init__(self, outer):
                super().__init__(outer)
                self.child_attr = 'set by child init'

            def method(self):
                return 'CHILD'

        o1 = Outer()
        o2 = Outer()

        # First bind Child to o1
        BoundChild = bind(Child, o1)

        # Now reparent to o2
        ReboundChild = reparent(BoundChild, o2.Parent)
        rechild = ReboundChild()

        self.assertEqual(rechild.method(), 'CHILD')
        self.assertEqual(rechild.child_attr, 'set by child init')
        self.assertIs(rechild.outer, o2)  # Now bound to o2!
        self.assertIsInstance(rechild, Child)
        self.assertIsInstance(rechild, o2.Parent)
        self.assertIsInstance(rechild, Outer.Parent)

    def test_reparent_different_instances(self):
        """reparent() with different outer instances."""
        class Outer:
            def __init__(self, name):
                self.name = name

            @BoundInnerClass
            class Inner:
                def __init__(self, outer):
                    self.outer = outer

        class Child(Outer.Inner):
            def __init__(self, outer):
                super().__init__(outer)

        o1 = Outer('first')
        o2 = Outer('second')

        # First bind Child to o1
        BoundChild = bind(Child, o1)

        # Now reparent to o2
        Child2 = reparent(BoundChild, o2.Inner)

        c1 = BoundChild()
        c2 = Child2()

        self.assertIs(c1.outer, o1)
        self.assertIs(c2.outer, o2)
        self.assertEqual(c1.outer.name, 'first')
        self.assertEqual(c2.outer.name, 'second')

    def test_reparent_bound_to_unbound_noop(self):
        """reparent(bound_class, unbound_parent) is a no-op when base is already unbound."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        o = Outer()
        BoundParent = o.Parent
        # BoundParent's base is already Outer.Parent (unbound), so this is a no-op
        result = reparent(BoundParent, Outer.Parent)
        self.assertIs(result, BoundParent)

    def test_reparent_bound_to_different_bound(self):
        """reparent(bound_to_o1, o2.Parent) rebinds to o2."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):
                    self.outer = outer

        o1 = Outer()
        o2 = Outer()
        BoundToO1 = o1.Parent

        Rebound = reparent(BoundToO1, o2.Parent)
        instance = Rebound()
        self.assertIs(instance.outer, o2)

    def test_reparent_with_replace_parameter(self):
        """reparent with replace parameter works."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):
                    self.outer = outer

        class Child(Outer.Parent):
            def __init__(self, outer):
                super().__init__(outer)

        o1 = Outer()
        o2 = Outer()
        BoundChild = bind(Child, o1)

        # BoundChild's bases include o1.Parent, so we can replace it with o2.Parent
        Rebound = reparent(BoundChild, o2.Parent, replace=o1.Parent)
        instance = Rebound()
        self.assertIs(instance.outer, o2)

    def test_reparent_replace_not_in_bases_raises(self):
        """reparent raises if replace is not in child's bases."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

            @BoundInnerClass
            class Other:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        class Child(Outer.Parent):
            def __init__(self, outer):  # pragma: nocover
                super().__init__(outer)

        o = Outer()
        BoundChild = bind(Child, o)
        with self.assertRaises(ValueError) as cm:
            reparent(BoundChild, o.Parent, replace=Outer.Other)
        self.assertIn("is not a direct base of", str(cm.exception))

    def test_reparent_replace_mismatch_raises(self):
        """reparent raises if unbound(parent) != unbound(replace)."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

            @BoundInnerClass
            class Other:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        o1 = Outer()
        o2 = Outer()

        # Start with class inheriting from unbound Parent
        class Child(Outer.Parent):
            def __init__(self, outer):  # pragma: nocover
                super().__init__(outer)

        # Bind to o1 - BoundChild.__bases__ is (o1.Parent, Child)
        BoundChild = bind(Child, o1)

        # Try to reparent to o2.Other but specify o1.Parent as replace
        # unbound(o2.Other) is Outer.Other, unbound(o1.Parent) is Outer.Parent - mismatch!
        with self.assertRaises(ValueError) as cm:
            reparent(BoundChild, o2.Other, replace=o1.Parent)
        self.assertIn("doesn't match", str(cm.exception))

    def test_reparent_parent_not_a_class_raises(self):
        """reparent raises TypeError if parent is not a class."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        o = Outer()
        BoundParent = o.Parent

        with self.assertRaises(TypeError) as cm:
            reparent(BoundParent, None)
        self.assertIn("must be a class", str(cm.exception))

        with self.assertRaises(TypeError) as cm:
            reparent(BoundParent, 42)
        self.assertIn("must be a class", str(cm.exception))

    def test_reparent_child_inherits_from_bound_cannot_reparent(self):
        """reparent raises ValueError if child inherits from bound class."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        o = Outer()
        BoundParent = o.Parent

        # Child inherits from a BOUND class (o.Parent), not the unbound Outer.Parent
        class Child(BoundParent):
            def __init__(self, outer):  # pragma: nocover
                super().__init__()

        # Trying to reparent at all should fail - Child has no unbound version
        with self.assertRaises(ValueError) as cm:
            reparent(Child, Outer.Parent)
        self.assertIn("inherits from a bound class", str(cm.exception))
        self.assertIn("cannot be reparented", str(cm.exception))

    def test_reparent_replace_not_a_class_raises(self):
        """reparent raises TypeError if replace is not a class."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        o = Outer()
        BoundParent = o.Parent
        with self.assertRaises(TypeError) as cm:
            reparent(BoundParent, o.Parent, replace="not a class")
        self.assertIn("replace must be a class", str(cm.exception))

    def test_reparent_noop_with_replace_both_unbound(self):
        """reparent with replace specified, both unbound, is a no-op."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        o = Outer()
        BoundParent = o.Parent

        # Both parent and replace are unbound, this is a no-op
        result = reparent(BoundParent, Outer.Parent, replace=Outer.Parent)
        self.assertIs(result, BoundParent)

    def test_reparent_unbound_parent_bound_target_base(self):
        """reparent with unbound parent where target base is bound returns unbound child."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        o = Outer()

        class Child(Outer.Parent):
            def __init__(self, outer):  # pragma: nocover
                super().__init__(outer)

        BoundChild = bind(Child, o)
        result = reparent(BoundChild, Outer.Parent)
        self.assertIs(result, Child)

    def test_reparent_parent_not_a_base_raises(self):
        """reparent raises if parent is not a base of child."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

            @BoundInnerClass
            class Other:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        o = Outer()
        BoundParent = o.Parent
        with self.assertRaises(ValueError) as cm:
            reparent(BoundParent, o.Other)
        self.assertIn("is not a base of", str(cm.exception))


class TestBind(unittest.TestCase):
    """Tests for the bind() function."""

    def test_bind_basic(self):
        """bind() creates working bound class."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):
                    self.outer = outer

        class Child(Outer.Parent):
            def __init__(self, outer):
                super().__init__(outer)
                self.child_attr = 'set by child'

        o = Outer()
        Bound = bind(Child, o)
        instance = Bound()
        self.assertIs(instance.outer, o)
        self.assertEqual(instance.child_attr, 'set by child')

    def test_bind_different_instances(self):
        """bind() with different outer instances."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):
                    self.outer = outer

        class Child(Outer.Parent):
            def __init__(self, outer):
                super().__init__(outer)

        o1 = Outer()
        o2 = Outer()
        Bound1 = bind(Child, o1)
        Bound2 = bind(Child, o2)
        self.assertIs(Bound1().outer, o1)
        self.assertIs(Bound2().outer, o2)

    def test_bind_no_boundinnerclass_parent_raises(self):
        """bind() raises if child doesn't inherit from a BoundInnerClass."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        class Unrelated:
            pass

        class Child(Unrelated):
            pass

        o = Outer()
        with self.assertRaises(ValueError) as cm:
            bind(Child, o)
        self.assertIn("Child", str(cm.exception))
        self.assertIn("doesn't inherit from any BoundInnerClass", str(cm.exception))
        self.assertIn("Outer", str(cm.exception))

    def test_bind_multiple_boundinnerclass_parents_raises(self):
        """bind() raises if child inherits from multiple BoundInnerClasses."""
        class Outer:
            @BoundInnerClass
            class Parent1:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

            @BoundInnerClass
            class Parent2:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        class Child(Outer.Parent1, Outer.Parent2):
            def __init__(self, outer):  # pragma: nocover
                super().__init__(outer)

        o = Outer()
        with self.assertRaises(ValueError) as cm:
            bind(Child, o)
        self.assertIn("Child", str(cm.exception))
        self.assertIn("multiple BoundInnerClasses", str(cm.exception))
        self.assertIn("reparent()", str(cm.exception))

    def test_bind_none_returns_unbound_base(self):
        """bind(child, None) returns the unbound base class."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        o = Outer()
        BoundParent = o.Parent

        # bind with None returns the unbound version
        result = bind(BoundParent, None)
        self.assertIs(result, Outer.Parent)

    def test_bind_none_with_unbound_class_returns_unchanged(self):
        """bind(child, None) with unbound class returns child unchanged."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        # Outer.Parent is not a bound class, so it returns unchanged
        result = bind(Outer.Parent, None)
        self.assertIs(result, Outer.Parent)

    def test_bind_none_with_regular_class_returns_unchanged(self):
        """bind(child, None) with regular class returns child unchanged."""
        class Regular:
            pass

        # Regular class returns unchanged
        result = bind(Regular, None)
        self.assertIs(result, Regular)

    def test_bind_child_inherits_from_bound_raises(self):
        """bind() raises if child inherits directly from a bound class."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        o = Outer()
        BoundParent = o.Parent

        # Child inherits from a BOUND class (o.Parent), not the unbound Outer.Parent
        class Child(BoundParent):
            def __init__(self, outer):  # pragma: nocover
                super().__init__()

        o2 = Outer()
        with self.assertRaises(ValueError) as cm:
            bind(Child, o2)
        self.assertIn("inherits from a bound class", str(cm.exception))


class TestUnbound(unittest.TestCase):
    """Tests for the unbound() function."""

    def test_unbound_bound_class(self):
        """unbound() returns unbound version of bound class."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        o = Outer()
        BoundInner = o.Inner
        result = unbound(BoundInner)
        self.assertIs(result, Outer.Inner)

    def test_unbound_unbound_class(self):
        """unbound() returns unbound class unchanged."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        result = unbound(Outer.Inner)
        self.assertIs(result, Outer.Inner)

    def test_unbound_regular_class(self):
        """unbound() returns regular class unchanged."""
        class Regular:
            pass

        result = unbound(Regular)
        self.assertIs(result, Regular)

    def test_unbound_equivalent_to_bind_none(self):
        """unbound(cls) is equivalent to bind(cls, None)."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        o = Outer()
        BoundInner = o.Inner
        self.assertIs(unbound(BoundInner), bind(BoundInner, None))

    def test_unbound_requires_a_class(self):
        """unbound() raises TypeError for non-class argument."""
        with self.assertRaises(TypeError) as cm:
            unbound(3.14)
        self.assertIn("must be a class", str(cm.exception))
        self.assertIn("float", str(cm.exception))

    def test_unbound_child_inherits_from_bound_raises(self):
        """unbound() raises if child inherits directly from a bound class."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        o = Outer()
        BoundParent = o.Parent

        # Child inherits from a BOUND class (o.Parent), not the unbound Outer.Parent
        class Child(BoundParent):
            def __init__(self, outer):  # pragma: nocover
                super().__init__()

        with self.assertRaises(ValueError) as cm:
            unbound(Child)
        self.assertIn("inherits from a bound class", str(cm.exception))
        self.assertIn("has no unbound version", str(cm.exception))


class TestCaching(unittest.TestCase):
    """Tests for caching behavior of bind and reparent."""

    def test_bind_returns_same_object(self):
        """bind() returns the same object on repeated calls."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):
                    self.outer = outer

        class Child(Outer.Parent):
            def __init__(self, outer):
                super().__init__(outer)

        o = Outer()
        Bound1 = bind(Child, o)
        Bound2 = bind(Child, o)
        self.assertIs(Bound1, Bound2)
        # Verify the bound class works
        instance = Bound1()
        self.assertIs(instance.outer, o)

    def test_reparent_returns_same_object(self):
        """reparent() returns the same object on repeated calls."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):
                    self.outer = outer

        class Child(Outer.Parent):
            def __init__(self, outer):
                super().__init__(outer)

        o1 = Outer()
        o2 = Outer()
        BoundChild = bind(Child, o1)

        # Reparent to o2 twice - should get same object
        Reparented1 = reparent(BoundChild, o2.Parent)
        Reparented2 = reparent(BoundChild, o2.Parent)
        self.assertIs(Reparented1, Reparented2)

        # Verify the reparented class works
        instance = Reparented1()
        self.assertIs(instance.outer, o2)

    def test_different_outers_get_different_classes(self):
        """bind() with different outer instances returns different classes."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):
                    self.outer = outer

        class Child(Outer.Parent):
            def __init__(self, outer):
                super().__init__(outer)

        o1 = Outer()
        o2 = Outer()
        Bound1 = bind(Child, o1)
        Bound2 = bind(Child, o2)
        self.assertIsNot(Bound1, Bound2)
        self.assertIs(Bound1().outer, o1)
        self.assertIs(Bound2().outer, o2)

    def test_different_children_get_different_classes(self):
        """bind() with different child classes returns different classes."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):
                    self.outer = outer

        class Child1(Outer.Parent):
            def __init__(self, outer):
                super().__init__(outer)
                self.which = 'child1'

        class Child2(Outer.Parent):
            def __init__(self, outer):
                super().__init__(outer)
                self.which = 'child2'

        o = Outer()
        Bound1 = bind(Child1, o)
        Bound2 = bind(Child2, o)
        self.assertIsNot(Bound1, Bound2)
        self.assertEqual(Bound1().which, 'child1')
        self.assertEqual(Bound2().which, 'child2')

    def test_stale_cache_entry_removed(self):
        """Stale cache entries are detected and removed."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):
                    self.outer = outer

        o = Outer()

        # Create a child class and bind it
        class Child(Outer.Parent):
            def __init__(self, outer):
                super().__init__(outer)
                self.child_attr = 'original'

        Bound1 = bind(Child, o)
        instance1 = Bound1()
        self.assertIs(instance1.outer, o)
        self.assertEqual(instance1.child_attr, 'original')

        # Now simulate a stale cache entry by replacing the weakref with a dead one
        cache = getattr(o, BOUNDINNERCLASS_OUTER_ATTR)
        child_id = id(Child)
        cache_key = (child_id, 'Parent')

        # Get the cached class
        cached_class, _ = cache[cache_key]

        # Create a dead weakref
        class Temp:
            pass
        temp = Temp()
        dead_ref = weakref.ref(temp)
        del temp
        # Now dead_ref() returns None

        # Replace cache entry with dead weakref
        cache[cache_key] = (cached_class, dead_ref)

        # Now call bind again with the SAME Child
        # The weakref check will fail (dead_ref() is not Child), triggering stale removal
        Bound2 = bind(Child, o)
        instance2 = Bound2()
        self.assertIs(instance2.outer, o)
        self.assertEqual(instance2.child_attr, 'original')

        # Verify we got a fresh class stored in the cache
        self.assertIs(Bound2, cache[cache_key][0])


class TestBoundToFunctions(unittest.TestCase):
    """Tests for class_bound_to and instance_bound_to functions."""

    def test_class_bound_to_true(self):
        """class_bound_to returns True for bound inner class."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):
                    self.outer = outer

        o = Outer()
        BoundInner = o.Inner
        self.assertTrue(class_bound_to(BoundInner, o))
        # Verify the class works
        instance = BoundInner()
        self.assertIs(instance.outer, o)

    def test_class_bound_to_false_different_outer(self):
        """class_bound_to returns False for different outer."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        o1 = Outer()
        o2 = Outer()
        BoundInner = o1.Inner
        self.assertFalse(class_bound_to(BoundInner, o2))
        # Verify the class is bound to o1
        self.assertTrue(class_bound_to(BoundInner, o1))

    def test_class_bound_to_false_no_cache(self):
        """class_bound_to returns False when no cache exists."""
        class Outer:
            pass

        o = Outer()
        self.assertFalse(class_bound_to(str, o))

    def test_instance_bound_to_true(self):
        """instance_bound_to returns True for instance of bound class."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):
                    self.outer = outer

        o = Outer()
        i = o.Inner()
        self.assertTrue(instance_bound_to(i, o))
        self.assertIs(i.outer, o)

    def test_instance_bound_to_false(self):
        """instance_bound_to returns False for different outer."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):
                    self.outer = outer

        o1 = Outer()
        o2 = Outer()
        i = o1.Inner()
        self.assertFalse(instance_bound_to(i, o2))
        self.assertTrue(instance_bound_to(i, o1))

    def test_not_transitive(self):
        """Bound-to relationship is not transitive."""
        class A:
            @BoundInnerClass
            class B:
                def __init__(self, a):
                    self.a = a

        class C:
            def __init__(self, b_instance):
                self.b_instance = b_instance

        a = A()
        b = a.B()

        self.assertTrue(class_bound_to(a.B, a))
        self.assertTrue(instance_bound_to(b, a))
        self.assertIs(b.a, a)

        c = C(b)
        # c is not bound to a (no transitive relationship)
        self.assertFalse(instance_bound_to(c, a))


class TestSlotsCompatibility(unittest.TestCase):
    """Tests for __slots__ compatibility."""

    def test_outer_with_dict(self):
        """Works with normal class (has __dict__)."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):
                    self.outer = outer

        o = Outer()
        i = o.Inner()
        self.assertIs(i.outer, o)
        self.assertIn(BOUNDINNERCLASS_OUTER_ATTR, o.__dict__)

    def test_outer_with_slots_and_cache_slot(self):
        """Works with __slots__ that includes cache slot and __weakref__."""
        class Outer:
            __slots__ = ('__weakref__', 'x') + BOUNDINNERCLASS_OUTER_SLOTS

            @BoundInnerClass
            class Inner:
                def __init__(self, outer):
                    self.outer = outer

        o = Outer()
        i = o.Inner()
        self.assertIs(i.outer, o)

    def test_outer_with_slots_no_cache_slot_raises(self):
        """Raises TypeError if __slots__ without cache slot or __dict__."""
        class Outer:
            __slots__ = ('x',)

            @BoundInnerClass
            class Inner:
                pass

        o = Outer()
        with self.assertRaises(TypeError) as cm:
            o.Inner
        self.assertIn(BOUNDINNERCLASS_OUTER_ATTR, str(cm.exception))


class TestWeakref(unittest.TestCase):
    """Tests for weakref behavior."""

    def test_outer_not_prevented_from_gc(self):
        """Bound inner class doesn't prevent outer from being collected."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        o = Outer()
        ref = weakref.ref(o)
        BoundInner = o.Inner
        # Verify it's the right class
        self.assertTrue(class_bound_to(BoundInner, o))

        del o
        # The bound inner class holds a weakref, so outer should be collected
        self.assertIsNone(ref())


class TestSignature(unittest.TestCase):
    """Tests for signature propagation on bound classes."""

    def test_unbound_and_bound_signatures(self):
        """Test signature behavior for both unbound and bound access."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer, x, y=None):
                    self.outer = outer
                    self.x = x
                    self.y = y

        # Unbound has original signature
        sig = inspect.signature(Outer.Inner)
        params = list(sig.parameters.keys())
        self.assertEqual(params, ['outer', 'x', 'y'])

        # Bound omits 'outer'
        o = Outer()
        sig = inspect.signature(o.Inner)
        params = list(sig.parameters.keys())
        self.assertEqual(params, ['x', 'y'])

        # __init__ signature also correct
        sig = inspect.signature(o.Inner.__init__)
        params = list(sig.parameters.keys())
        self.assertEqual(params, ['x', 'y'])

        # And it actually works
        i = o.Inner(42, y='hello')
        self.assertIs(i.outer, o)
        self.assertEqual(i.x, 42)
        self.assertEqual(i.y, 'hello')

    def test_signature_with_args_kwargs(self):
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
        self.assertEqual(params, ['x', 'args', 'kwargs'])

        # And it works
        i = o.Inner(1, 2, 3, foo='bar')
        self.assertIs(i.outer, o)
        self.assertEqual(i.x, 1)
        self.assertEqual(i.args, (2, 3))
        self.assertEqual(i.kwargs, {'foo': 'bar'})

    def test_signature_preserves_defaults(self):
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
        self.assertEqual(sig.parameters['y'].default, 42)
        self.assertEqual(sig.parameters['z'].default, 'hello')

        # Defaults work
        i = o.Inner(1)
        self.assertIs(i.outer, o)
        self.assertEqual(i.y, 42)
        self.assertEqual(i.z, 'hello')


class TestClassProxyBehavior(unittest.TestCase):
    """Tests for _ClassProxy transparent forwarding."""

    def test_proxy_name(self):
        """Proxy forwards __name__."""
        class Outer:
            @BoundInnerClass
            class Inner:
                pass

        descriptor = Outer.__dict__['Inner']
        self.assertEqual(descriptor.__name__, 'Inner')
        self.assertEqual(Outer.Inner.__name__, 'Inner')

    def test_proxy_doc(self):
        """Proxy forwards __doc__ when accessed through class."""
        class Outer:
            @BoundInnerClass
            class Inner:
                """Inner class docstring."""
                pass

        # When accessed through Outer.Inner (triggers __get__), we get the wrapped class
        self.assertEqual(Outer.Inner.__doc__, 'Inner class docstring.')

        # The descriptor itself has BoundInnerClass's docstring, but __wrapped__ has the right one
        descriptor = Outer.__dict__['Inner']
        self.assertEqual(descriptor.__wrapped__.__doc__, 'Inner class docstring.')

    def test_proxy_module(self):
        """Proxy forwards __module__ when accessed through class."""
        class Outer:
            @BoundInnerClass
            class Inner:
                pass

        # When accessed through Outer.Inner (triggers __get__), we get the wrapped class
        self.assertEqual(Outer.Inner.__module__, __name__)

        # The descriptor's __wrapped__ has the right module
        descriptor = Outer.__dict__['Inner']
        self.assertEqual(descriptor.__wrapped__.__module__, __name__)

    def test_proxy_getattr(self):
        """Proxy forwards attribute access."""
        class Outer:
            @BoundInnerClass
            class Inner:
                class_attr = 'hello'

        descriptor = Outer.__dict__['Inner']
        self.assertEqual(descriptor.class_attr, 'hello')
        self.assertEqual(Outer.Inner.class_attr, 'hello')

    def test_subclass_from_proxy(self):
        """Can subclass from the proxy (uses __mro_entries__)."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):
                    self.outer = outer

        class Child(Outer.Inner):
            def __init__(self, outer):
                super().__init__(outer)
                self.child_flag = True

        self.assertTrue(issubclass(Child, Outer.Inner))

        # Also instantiate to cover the __init__ bodies
        o = Outer()
        c = Child(o)
        self.assertIs(c.outer, o)
        self.assertTrue(c.child_flag)

    def test_proxy_cls_property(self):
        """Proxy .cls property returns wrapped class."""
        class Outer:
            @BoundInnerClass
            class Inner:
                pass

        descriptor = Outer.__dict__['Inner']
        self.assertIs(descriptor.cls, Outer.Inner)

    def test_cls_backward_compatibility_for_inheritance(self):
        """The .cls property works for inheritance (backward compatibility)."""
        class Outer:
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):
                    self.outer = outer

            # Old-style using .cls still works
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

        # BoundInnerClass with .cls works
        c = o.Child()
        self.assertIs(c.outer, o)
        self.assertTrue(c.child)

        # UnboundInnerClass with .cls works
        uc = o.UnboundChild()
        self.assertIs(uc.outer, o)

    def test_proxy_repr(self):
        """Proxy has informative repr."""
        class Outer:
            @BoundInnerClass
            class Inner:
                pass

        descriptor = Outer.__dict__['Inner']
        r = repr(descriptor)
        self.assertIn('BoundInnerClass', r)
        self.assertIn('Inner', r)

    def test_proxy_delattr(self):
        """Proxy forwards delattr to wrapped."""
        class Inner:
            custom = 'value'

        proxy = _ClassProxy(Inner)
        self.assertEqual(proxy.custom, 'value')
        del proxy.custom
        self.assertFalse(hasattr(proxy, 'custom'))
        self.assertFalse(hasattr(Inner, 'custom'))

    def test_proxy_setattr_qualname(self):
        """Setting __qualname__ updates both proxy and wrapped."""
        class Inner:
            pass

        proxy = _ClassProxy(Inner)
        original_qualname = proxy.__qualname__
        proxy.__qualname__ = 'NewQualname'
        self.assertEqual(proxy.__qualname__, 'NewQualname')
        self.assertEqual(Inner.__qualname__, 'NewQualname')
        # Restore
        proxy.__qualname__ = original_qualname

    def test_proxy_setattr_annotations(self):
        """Setting __annotations__ updates both proxy and wrapped."""
        class Inner:
            pass

        proxy = _ClassProxy(Inner)
        proxy.__annotations__ = {'x': int}
        self.assertEqual(proxy.__annotations__, {'x': int})
        self.assertEqual(Inner.__annotations__, {'x': int})


class TestClassProxyChecks(unittest.TestCase):
    """Tests for isinstance/issubclass with proxy."""

    def test_instancecheck(self):
        """Proxy supports isinstance checks."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):
                    self.outer = outer

        o = Outer()
        i = o.Inner()
        descriptor = Outer.__dict__['Inner']
        self.assertTrue(isinstance(i, descriptor))
        self.assertIs(i.outer, o)

    def test_subclasscheck(self):
        """Proxy supports issubclass checks."""
        class Outer:
            @BoundInnerClass
            class Inner:
                pass

        class Child(Outer.Inner):
            pass

        descriptor = Outer.__dict__['Inner']
        self.assertTrue(issubclass(Child, descriptor))
        self.assertTrue(issubclass(Child, Outer.Inner))

    def test_subclasscheck_with_wrapped_subclass(self):
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
        self.assertTrue(issubclass(child_desc, parent_desc))
        self.assertTrue(issubclass(Outer.Child, Outer.Parent))


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and error paths."""

    def test_signature_with_builtin_init(self):
        """Signature handling when __init__ has no inspectable signature."""
        class Outer:
            @BoundInnerClass
            class Inner(int):
                pass

        o = Outer()
        # Should not raise
        BoundInner = o.Inner
        self.assertIsNotNone(BoundInner)
        self.assertTrue(issubclass(BoundInner, int))

    def test_signature_with_minimal_params(self):
        """Signature handling when __init__ has fewer than 2 params."""
        # We test _make_bound_signature with a function that has only 'self'
        sig = _make_bound_signature(lambda self: None)
        self.assertIsNotNone(sig)
        self.assertEqual(len(list(sig.parameters)), 0)

    def test_make_bound_signature_exception(self):
        """Test _make_bound_signature when inspect.signature raises."""
        # Pass a non-callable - inspect.signature raises TypeError
        result = _make_bound_signature(42)
        self.assertIsNone(result)

    def test_class_bound_to_with_no_name(self):
        """class_bound_to handles objects without __name__."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        o = Outer()
        _ = o.Inner

        self.assertFalse(class_bound_to(42, o))
        self.assertFalse(class_bound_to(None, o))

    def test_get_cache_with_slots_and_dict(self):
        """Works with __slots__ that includes __dict__."""
        class Outer:
            __slots__ = ('__dict__', '__weakref__')

            @BoundInnerClass
            class Inner:
                def __init__(self, outer):
                    self.outer = outer

        o = Outer()
        i = o.Inner()
        self.assertIs(i.outer, o)

    def test_mro_entries_used_in_subclassing(self):
        """__mro_entries__ is called when subclassing from proxy."""
        class Outer:
            @BoundInnerClass
            class Inner:
                pass

        descriptor = Outer.__dict__['Inner']
        entries = descriptor.__mro_entries__((descriptor,))
        self.assertEqual(entries, (Outer.Inner,))

    def test_base_wrap_not_implemented(self):
        """_BoundInnerClassBase._wrap raises NotImplementedError."""
        class Inner:
            pass

        base = _BoundInnerClassBase(Inner)
        o = object()

        with self.assertRaises(NotImplementedError):
            base._wrap(o, Inner)

    def test_proxy_with_object_lacking_qualname(self):
        """Proxy handles wrapped objects without __qualname__."""
        obj = types.SimpleNamespace()
        obj.__name__ = 'FakeClass'

        proxy = _ClassProxy(obj)
        self.assertIs(proxy.__wrapped__, obj)
        self.assertEqual(proxy.__name__, 'FakeClass')

    def test_proxy_with_object_lacking_annotations(self):
        """Proxy handles wrapped objects without __annotations__."""
        obj = types.SimpleNamespace()
        obj.__name__ = 'FakeClass'

        proxy = _ClassProxy(obj)
        self.assertIs(proxy.__wrapped__, obj)
        self.assertEqual(proxy.__name__, 'FakeClass')

    def test_setattr_wrapped_updates_qualname_and_annotations(self):
        """Setting __wrapped__ updates cached __qualname__ and __annotations__."""
        class Original:
            x: int

        class Replacement:
            y: str

        proxy = _ClassProxy(Original)
        self.assertIn('Original', proxy.__qualname__)

        proxy.__wrapped__ = Replacement
        self.assertIn('Replacement', proxy.__qualname__)
        self.assertEqual(proxy.__annotations__, {'y': str})

    def test_setattr_wrapped_with_missing_attrs(self):
        """Setting __wrapped__ to object without __qualname__/__annotations__."""
        class Original:
            pass

        replacement = types.SimpleNamespace()
        replacement.__name__ = 'Replacement'

        proxy = _ClassProxy(Original)
        # Should not raise
        proxy.__wrapped__ = replacement
        self.assertIs(proxy.__wrapped__, replacement)

    def test_class_proxy_setattr_forwarding(self):
        """_ClassProxy forwards setattr to wrapped for normal attributes."""
        class Inner:
            pass

        original_name = Inner.__name__
        original_module = Inner.__module__
        original_doc = Inner.__doc__

        proxy = _ClassProxy(Inner)

        proxy.__name__ = 'NewName'
        self.assertEqual(proxy.__name__, 'NewName')
        self.assertEqual(Inner.__name__, 'NewName')

        proxy.__module__ = 'new.module'
        self.assertEqual(proxy.__module__, 'new.module')
        self.assertEqual(Inner.__module__, 'new.module')

        proxy.__doc__ = 'New doc.'
        self.assertEqual(proxy.__doc__, 'New doc.')
        self.assertEqual(Inner.__doc__, 'New doc.')

        # Restore
        Inner.__name__ = original_name
        Inner.__module__ = original_module
        Inner.__doc__ = original_doc

    def test_class_proxy_getattr_forwarding(self):
        """_ClassProxy __getattr__ forwards to wrapped."""
        class Inner:
            custom_attr = 'hello'

        proxy = _ClassProxy(Inner)
        self.assertEqual(proxy.custom_attr, 'hello')


class TestNewEdgeCases(unittest.TestCase):
    """Tests for edge cases in the fixed boundinnerclass."""

    def test_same_name_base_skipped(self):
        """When a base has the same name as the inner class, it's skipped."""
        # Create a base class and rename it to match the inner class name
        class Base:
            pass
        Base.__name__ = 'Inner'  # Same name as the inner class

        class Outer:
            @BoundInnerClass
            class Inner(Base):
                def __init__(self, outer):
                    self.outer = outer

        # This triggers the same-name skip in __get__
        o = Outer()
        i = o.Inner()
        self.assertIs(i.outer, o)
        self.assertIsInstance(i, Base)


class TestRegressions(unittest.TestCase):
    """Regression tests for bugs that have been fixed."""

    def test_outer_evaluates_to_false(self):
        """
        Regression test for a bugfix!

        The behavior:

            If you have an outer class Outer, and it contains an
            inner class Inner decorated with @BoundInnerClass,
            and o is an instance of Outer, and o evaluates to
            false in a boolean context,
            o.Inner would be the *unbound* version of Inner.

        The bug:
            When you access a class descriptor--an object that
            implements __get__--the parameters are contingent
            on how you were accessed.

            If you access Inner through an instance, e.g. o.Inner,
            the descriptor is called with the instance:
                __get__(self, o, Outer)

            If you access Inner through the class itself,
            e.g. Outer.Inner, the descriptor is called with None
            instead of the instance:
                __get__(self, None, Outer)

            See
                https://docs.python.org/3/howto/descriptor.html#invocation-from-an-instance
            vs.
                https://docs.python.org/3/howto/descriptor.html#invocation-from-a-class

            The bug was, I wasn't checking to see if obj was None,
            I was checking to see if obj was false.  Oops.

        The fix:
            Easy.  Use "if obj is None" instead of "if not obj".

        -----

        This bug is thirteen years old!
        It's in the second revision of the Bound Inner Classes
        recipe I posted to the good ol' cookbook:

            https://code.activestate.com/recipes/577070-bound-inner-classes/history/2/

        Before I made "big", it was inconvenient for me
        to use BoundInnerClasses.  So I rarely used them.
        I guess I just didn't put enough CPU seconds
        through the class to stumble over this bug before.
        """

        class Outer:
            def __bool__(self):
                return False

            @BoundInnerClass
            class Inner:
                def __init__(self, outer):
                    self.outer = outer

        o = Outer()
        self.assertFalse(o)
        self.assertNotEqual(Outer.Inner, o.Inner)
        i = o.Inner()
        self.assertEqual(o, i.outer)

    def test_nested_boundinnerclass_inheritance_single_outer_injection(self):
        """
        Regression test: nested BoundInnerClass inheritance should inject outer only once.

        Bug: When class C inherits from class B which inherits from class A,
        and all three are BoundInnerClasses, each wrapper's __init__ was calling
        super().__init__(outer, *args), causing outer to be passed multiple times.
        This resulted in "takes N arguments but N+M were given" errors.

        Fix: Changed wrappers to call cls.__init__ directly instead of super().__init__.
        """
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

        # This used to raise: "takes 2 positional arguments but 4 were given"
        c = o.Child()

        # Verify all __init__ methods were called correctly
        self.assertIs(c.outer, o)
        self.assertTrue(c.grandparent_called)
        self.assertTrue(c.parent_called)
        self.assertTrue(c.child_called)


class TestMisuseDetection(unittest.TestCase):
    """Tests for detecting incorrect @BoundInnerClass usage."""

    def test_boundinnerclass_at_module_scope(self):
        """@BoundInnerClass on a non-nested class raises clear error."""
        @BoundInnerClass
        class NotNested:
            def __init__(self, outer): # pragma: nocover
                self.outer = outer

        with self.assertRaises(TypeError) as cm:
            NotNested()
        self.assertIn("@BoundInnerClass", str(cm.exception))
        self.assertIn("nested inside another class", str(cm.exception))

    def test_boundinnerclass_inside_method(self):
        """@BoundInnerClass on a class defined inside a method raises clear error."""
        class Outer:
            def make_inner(self):
                @BoundInnerClass
                class Inner:
                    def __init__(self, outer): # pragma: nocover
                        self.outer = outer
                return Inner()

        o = Outer()
        with self.assertRaises(TypeError) as cm:
            o.make_inner()
        self.assertIn("@BoundInnerClass", str(cm.exception))
        self.assertIn("nested inside another class", str(cm.exception))

    def test_unboundinnerclass_at_module_scope(self):
        """@UnboundInnerClass on a non-nested class raises clear error."""
        @UnboundInnerClass
        class NotNested:
            pass

        with self.assertRaises(TypeError) as cm:
            NotNested()
        self.assertIn("@UnboundInnerClass", str(cm.exception))
        self.assertIn("nested inside another class", str(cm.exception))


def run_tests():  # pragma: nocover
    bigtestlib.run(name="big.boundinnerclass", module=__name__)


if __name__ == "__main__":  # pragma: no cover
    run_tests()
    bigtestlib.finish()
