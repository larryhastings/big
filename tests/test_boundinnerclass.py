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

import bigtestlib
bigtestlib.preload_local_big()


import inspect
import types
import unittest
import weakref

from big.boundinnerclass import *

from big.boundinnerclass import (
    _BoundInnerClassBase,
    _ClassProxy,
    _make_bound_signature,
    )

from big.builtin import ClassRegistry


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

    def test_with_ClassRegistry(self):
        """test using ClassRegistry with BoundInnerClass."""

        base = ClassRegistry()

        class Outer:
            @base()
            @BoundInnerClass
            class Parent:
                def __init__(self, outer):
                    self.outer = outer

            @BoundInnerClass
            class Child(bound_inner_base(base.Parent)):
                def __init__(self, outer):
                    super().__init__()
                    self.child = True

        o = Outer()
        c = o.Child()
        self.assertIs(c.outer, o)
        self.assertTrue(c.child)



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


class TestRebind(unittest.TestCase):
    """Tests for the rebind() function."""

    def test_rebind_basic(self):
        """rebind() creates working rebound class."""
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

        o = Outer()
        Rechild = rebind(Child, o.Parent)
        rechild = Rechild()

        self.assertEqual(rechild.method(), 'CHILD')
        self.assertEqual(rechild.child_attr, 'set by child init')
        self.assertIs(rechild.outer, o)
        self.assertIsInstance(rechild, Child)
        self.assertIsInstance(rechild, o.Parent)
        self.assertIsInstance(rechild, Outer.Parent)

    def test_rebind_different_instances(self):
        """rebind() with different outer instances."""
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

        Child1 = rebind(Child, o1.Inner)
        Child2 = rebind(Child, o2.Inner)

        c1 = Child1()
        c2 = Child2()

        self.assertIs(c1.outer, o1)
        self.assertIs(c2.outer, o2)
        self.assertEqual(c1.outer.name, 'first')
        self.assertEqual(c2.outer.name, 'second')


class TestBoundToFunctions(unittest.TestCase):
    """Tests for class_bound_to and instance_bound_to functions."""

    def test_class_bound_to_true(self):
        """class_bound_to returns True for bound inner class."""
        class Outer:
            @BoundInnerClass
            class Inner:
                pass

        o = Outer()
        BoundInner = o.Inner
        self.assertTrue(class_bound_to(BoundInner, o))

    def test_class_bound_to_false_different_outer(self):
        """class_bound_to returns False for different outer."""
        class Outer:
            @BoundInnerClass
            class Inner:
                pass

        o1 = Outer()
        o2 = Outer()
        BoundInner = o1.Inner
        self.assertFalse(class_bound_to(BoundInner, o2))

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
        b = a.B()  # Instantiate to cover __init__

        self.assertTrue(class_bound_to(a.B, a))
        self.assertTrue(instance_bound_to(b, a))

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
        self.assertIn(BOUNDINNERCLASS_ATTR, o.__dict__)

    def test_outer_with_slots_and_cache_slot(self):
        """Works with __slots__ that includes __bound_inner_classes__ and __weakref__."""
        class Outer:
            __slots__ = ('__weakref__', 'x') + BOUNDINNERCLASS_SLOTS

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
        self.assertIn('__bound_inner_classes__', str(cm.exception))


class TestWeakref(unittest.TestCase):
    """Tests for weakref behavior."""

    def test_outer_not_prevented_from_gc(self):
        """Bound inner class doesn't prevent outer from being collected."""
        class Outer:
            @BoundInnerClass
            class Inner:
                pass

        o = Outer()
        ref = weakref.ref(o)
        BoundInner = o.Inner

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
        self.assertEqual(i.x, 1)
        self.assertEqual(i.args, (2, 3))
        self.assertEqual(i.kwargs, {'foo': 'bar'})

    def test_signature_preserves_defaults(self):
        """Signature preserves default values."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer, x, y=42, z='hello'):
                    self.x = x
                    self.y = y
                    self.z = z

        o = Outer()
        sig = inspect.signature(o.Inner)
        self.assertEqual(sig.parameters['y'].default, 42)
        self.assertEqual(sig.parameters['z'].default, 'hello')

        # Defaults work
        i = o.Inner(1)
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

        self.assertEqual(Outer.Inner.__name__, 'Inner')

    def test_proxy_doc(self):
        """Proxy forwards __doc__."""
        class Outer:
            @BoundInnerClass
            class Inner:
                """Inner class docstring."""
                pass

        self.assertEqual(Outer.Inner.__doc__, 'Inner class docstring.')

    def test_proxy_module(self):
        """Proxy forwards __module__."""
        class Outer:
            @BoundInnerClass
            class Inner:
                pass

        self.assertEqual(Outer.Inner.__module__, __name__)

    def test_proxy_getattr(self):
        """Proxy forwards attribute access."""
        class Outer:
            @BoundInnerClass
            class Inner:
                class_attr = 'hello'

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

    def test_proxy_delattr(self):
        """Proxy forwards delattr to wrapped."""
        class Inner:
            custom = 'value'

        proxy = _ClassProxy(Inner)
        self.assertEqual(proxy.custom, 'value')
        del proxy.custom
        self.assertFalse(hasattr(proxy, 'custom'))

    def test_proxy_setattr_qualname(self):
        """Setting __qualname__ updates both proxy and wrapped."""
        class Inner:
            pass

        proxy = _ClassProxy(Inner)
        proxy.__qualname__ = 'NewQualname'
        self.assertEqual(proxy.__qualname__, 'NewQualname')
        self.assertEqual(Inner.__qualname__, 'NewQualname')

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

    def test_signature_with_minimal_params(self):
        """Signature handling when __init__ has fewer than 2 params."""
        # We test _make_bound_signature with a function that has only 'self'
        # The function body doesn't matter since we're only inspecting the signature
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
                pass

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

    def test_proxy_with_object_lacking_annotations(self):
        """Proxy handles wrapped objects without __annotations__."""
        obj = types.SimpleNamespace()
        obj.__name__ = 'FakeClass'

        proxy = _ClassProxy(obj)
        self.assertIs(proxy.__wrapped__, obj)

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

    def test_setattr_wrapped_with_missing_attrs(self):
        """Setting __wrapped__ to object without __qualname__/__annotations__."""
        class Original:
            pass

        replacement = types.SimpleNamespace()
        replacement.__name__ = 'Replacement'

        proxy = _ClassProxy(Original)
        # Should not raise
        proxy.__wrapped__ = replacement

    def test_class_proxy_setattr_forwarding(self):
        """_ClassProxy forwards setattr to wrapped for normal attributes."""
        class Inner:
            pass

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

    def test_rebind_with_non_bound_class_raises(self):
        """rebind raises ValueError if bound_parent isn't a bound inner class."""
        class Parent:
            def __init__(self):  # pragma: nocover
                pass

        class Child(Parent):
            def __init__(self):  # pragma: nocover
                super().__init__()

        # Create a class that looks like a bound inner class but isn't
        class FakeBound:
            def __init__(self):  # pragma: nocover
                pass

        with self.assertRaises(ValueError) as cm:
            rebind(Child, FakeBound)
        self.assertIn("doesn't appear to be a bound inner class", str(cm.exception))


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


def run_tests():
    bigtestlib.run(name="big.boundinnerclass", module=__name__)


if __name__ == "__main__":  # pragma: no cover
    run_tests()
    bigtestlib.finish()
