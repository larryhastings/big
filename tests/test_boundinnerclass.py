#!/usr/bin/env python3

import inspect
import sys
import types
import unittest
import weakref

import bigtestlib
bigtestlib.preload_local_big()

from big.boundinnerclass import *

from big.boundinnerclass import (
    _BoundInnerClassBase,
    _BoundInnerClassCache,
    _BOUNDINNERCLASS_INNER_ATTR,
    _ClassProxy,
    _get_outer_weakref,
    _make_bound_signature,
    _unbound,
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

        class Child(BoundParent):
            def __init__(self, outer):  # pragma: nocover
                super().__init__()

        with self.assertRaises(ValueError) as cm:
            unbound(Child)
        self.assertIn("inherits from a bound class", str(cm.exception))
        self.assertIn("has no unbound version", str(cm.exception))


class TestBoundToFunctions(unittest.TestCase):
    """Tests for bound_to and type_bound_to functions."""

    def test_bound_to(self):
        """bound_to returns the instance for bound inner class, or None for unbound."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):
                    self.outer = outer

        self.assertIsNone(bound_to(Outer.Inner))

        o = Outer()
        BoundInner = o.Inner
        self.assertIs(o, bound_to(BoundInner))
        instance = BoundInner()
        self.assertIs(instance.outer, o)

    def test_bound_to_false_no_cache(self):
        """bound_to returns None on classes not using BoundInnerClass."""
        self.assertIsNone(bound_to(str))

    def test_type_bound_to(self):
        """type_bound_to returns outer for instance of bound class."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):
                    self.outer = outer

        o = Outer()
        i = o.Inner()
        self.assertIs(o, type_bound_to(i))
        self.assertIs(i.outer, o)

    def test_bound_to_with_non_class(self):
        """bound_to returns None for non-class arguments."""
        self.assertIsNone(bound_to(42))
        self.assertIsNone(bound_to("string"))
        self.assertIsNone(bound_to(None))


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
        self.assertIs(o, bound_to(BoundInner))

        del o
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

        sig = inspect.signature(Outer.Inner)
        params = list(sig.parameters.keys())
        self.assertEqual(params, ['outer', 'x', 'y'])

        o = Outer()
        sig = inspect.signature(o.Inner)
        params = list(sig.parameters.keys())
        self.assertEqual(params, ['x', 'y'])

        sig = inspect.signature(o.Inner.__init__)
        params = list(sig.parameters.keys())
        self.assertEqual(params, ['x', 'y'])

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

        self.assertEqual(Outer.Inner.__doc__, 'Inner class docstring.')
        descriptor = Outer.__dict__['Inner']
        self.assertEqual(descriptor.__wrapped__.__doc__, 'Inner class docstring.')

    def test_proxy_module(self):
        """Proxy forwards __module__ when accessed through class."""
        class Outer:
            @BoundInnerClass
            class Inner:
                pass

        self.assertEqual(Outer.Inner.__module__, __name__)
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
                super().__init__(outer)  # Must pass outer - not using bind()
                self.child_flag = True

        self.assertTrue(issubclass(Child, Outer.Inner))

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
        self.assertIs(c.outer, o)
        self.assertTrue(c.child)

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

    @unittest.skipIf(sys.version_info < (3, 7), "__qualname__ not in slots on 3.6")
    def test_proxy_setattr_qualname(self):
        """Setting __qualname__ updates both proxy and wrapped."""
        class Inner:
            pass

        proxy = _ClassProxy(Inner)
        original_qualname = proxy.__qualname__
        proxy.__qualname__ = 'NewQualname'
        self.assertEqual(proxy.__qualname__, 'NewQualname')
        self.assertEqual(Inner.__qualname__, 'NewQualname')
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
        BoundInner = o.Inner
        self.assertIsNotNone(BoundInner)
        self.assertTrue(issubclass(BoundInner, int))

    def test_signature_with_minimal_params(self):
        """Signature handling when __init__ has fewer than 2 params."""
        sig = _make_bound_signature(lambda self: None)
        self.assertIsNotNone(sig)
        self.assertEqual(len(list(sig.parameters)), 0)

    def test_make_bound_signature_exception(self):
        """Test _make_bound_signature when inspect.signature raises."""
        result = _make_bound_signature(42)
        self.assertIsNone(result)

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

        Inner.__name__ = original_name
        Inner.__module__ = original_module
        Inner.__doc__ = original_doc

    def test_class_proxy_getattr_forwarding(self):
        """_ClassProxy __getattr__ forwards to wrapped."""
        class Inner:
            custom_attr = 'hello'

        proxy = _ClassProxy(Inner)
        self.assertEqual(proxy.custom_attr, 'hello')

    def test_stale_cache_entry_detected(self):
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
        self.assertIsNotNone(BoundInner2)
        instance = BoundInner2()
        self.assertIs(instance.outer, o)


class TestNewEdgeCases(unittest.TestCase):
    """Tests for edge cases in the fixed boundinnerclass."""

    def test_same_name_base_skipped(self):
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
        self.assertIs(i.outer, o)
        self.assertIsInstance(i, Base)


class TestRegressions(unittest.TestCase):
    """Regression tests for bugs that have been fixed."""

    def test_outer_evaluates_to_false(self):
        """Regression: outer instance that evaluates to false still works."""
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
            def __init__(self, outer):  # pragma: nocover
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
                    def __init__(self, outer):  # pragma: nocover
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


class TestIsBindable(unittest.TestCase):
    """Tests for is_bindable() function."""

    def test_is_bindable_with_boundinnerclass(self):
        """is_bindable returns True for @BoundInnerClass decorated classes."""
        class Outer:
            @BoundInnerClass
            class Inner:
                pass

        self.assertTrue(is_bindable(Outer.Inner))


    def test_is_bindable_with_regular_class(self):
        """is_bindable returns False for regular classes."""
        class Regular:
            pass

        self.assertFalse(is_bindable(Regular))

    def test_is_bindable_with_non_class(self):
        """is_bindable returns False for non-class arguments."""
        self.assertFalse(is_bindable(42))
        self.assertFalse(is_bindable("string"))
        self.assertFalse(is_bindable(None))


class TestIsBound(unittest.TestCase):
    """Tests for is_bound() function."""

    def test_is_bound_with_bound_class(self):
        """is_bound returns True for bound classes."""
        class Outer:
            @BoundInnerClass
            class Inner:
                def __init__(self, outer):  # pragma: nocover
                    self.outer = outer

        o = Outer()
        BoundInner = o.Inner
        self.assertTrue(is_bound(BoundInner))

    def test_is_bound_with_unbound_class(self):
        """is_bound returns False for unbound classes."""
        class Outer:
            @BoundInnerClass
            class Inner:
                pass

        self.assertFalse(is_bound(Outer.Inner))

    def test_is_bound_with_regular_class(self):
        """is_bound returns False for regular classes."""
        class Regular:
            pass

        self.assertFalse(is_bound(Regular))

    def test_is_bound_with_non_class(self):
        """is_bound returns False for non-class arguments."""
        self.assertFalse(is_bound(42))
        self.assertFalse(is_bound("string"))
        self.assertFalse(is_bound(None))


class TestRenamedBICSlowPaths(unittest.TestCase):
    """Tests for slow paths when BICs are renamed/aliased."""

    def test_get_renamed_parent_bic(self):
        """Accessing a child BIC works when its parent BIC has been renamed."""
        # Create Parent BIC
        @BoundInnerClass
        class Parent:
            def __init__(self, outer):
                self.outer = outer
                self.parent_flag = True

        parent_cls = Parent.__wrapped__

        # Create Child BIC that inherits from parent_cls
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
        self.assertIs(instance.outer, o)
        self.assertTrue(instance.parent_flag)
        self.assertTrue(instance.child_flag)

        # Verify the MRO includes the bound parent
        self.assertIn(o.RenamedParent, o.Child.__mro__)


class TestMROInheritance(unittest.TestCase):
    """Tests that BIC finds descriptors on parent classes via MRO."""

    def test_bic_on_parent_class_found_via_mro(self):
        """Child outer class inherits a BIC from parent outer class."""
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
        self.assertIs(c.outer, o)
        self.assertTrue(c.child_flag)
        self.assertIsInstance(c, ParentOuter.Inner)

    def test_renamed_bic_on_parent_class_found_via_mro(self):
        """Slow path finds a renamed BIC on a parent outer class via MRO."""
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
        self.assertIs(c.outer, o)
        self.assertTrue(c.child_flag)


class TestMissingBaseClassError(unittest.TestCase):
    """Tests that BIC raises when a parent BIC is removed from the outer class."""

    def test_deleted_parent_bic_raises(self):
        """Accessing child BIC raises when parent BIC is deleted from outer class."""
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
        with self.assertRaises(RuntimeError) as cm:
            o.Child
        self.assertIn("Parent", str(cm.exception))
        self.assertIn("Every BoundInnerClass base must be", str(cm.exception))

    def test_deleted_all_aliases_of_parent_bic_raises(self):
        """Accessing child BIC raises when all aliases of parent BIC are deleted."""
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
        with self.assertRaises(RuntimeError) as cm:
            o.Child
        self.assertIn("Parent", str(cm.exception))

    def test_non_bindable_base_is_not_an_error(self):
        """Bases that aren't bindable are silently skipped (not an error)."""
        class RegularBase:
            pass

        class Outer:
            @BoundInnerClass
            class Inner(RegularBase):
                def __init__(self, outer):
                    self.outer = outer

        o = Outer()
        # RegularBase isn't a BIC, so it's silently skipped -- no error
        i = o.Inner()
        self.assertIs(i.outer, o)
        self.assertIsInstance(i, RegularBase)


class TestMediumPathAliasCache(unittest.TestCase):
    """Tests for the medium path alias cache in _BoundInnerClassBase."""

    def setUp(self):
        # Clear the alias cache before each test so tests are independent
        _BoundInnerClassBase._alias_cache.clear()

    def test_medium_path_caches_alias(self):
        """After slow path finds a renamed BIC, the medium path is used next time."""
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
        self.assertIs(c1.outer, o1)
        self.assertTrue(c1.parent_flag)
        self.assertTrue(c1.child_flag)

        # Verify alias was cached
        alias_key = (id(parent_cls), id(Outer))
        self.assertIn(alias_key, _BoundInnerClassBase._alias_cache)
        self.assertEqual(_BoundInnerClassBase._alias_cache[alias_key], 'RenamedParent')

        # Second bind on a different instance: medium path should find it
        o2 = Outer()
        c2 = o2.Child()
        self.assertIs(c2.outer, o2)
        self.assertTrue(c2.parent_flag)
        self.assertTrue(c2.child_flag)

    def test_medium_path_stale_alias_falls_to_slow_path(self):
        """When cached alias becomes stale, slow path re-discovers the new name."""
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
        self.assertIs(c1.outer, o1)

        alias_key = (id(parent_cls), id(Outer))
        self.assertEqual(_BoundInnerClassBase._alias_cache[alias_key], 'FirstName')

        # Rename: delete FirstName, add SecondName
        del Outer.FirstName
        Outer.SecondName = BoundInnerClass(parent_cls)

        # Second bind on new instance: medium path finds "FirstName" is stale,
        # falls through to slow path which discovers "SecondName"
        o2 = Outer()
        c2 = o2.Child()
        self.assertIs(c2.outer, o2)
        self.assertTrue(c2.parent_flag)
        self.assertTrue(c2.child_flag)

        # Verify alias cache was updated
        self.assertEqual(_BoundInnerClassBase._alias_cache[alias_key], 'SecondName')

    def test_medium_path_stale_alias_and_no_replacement_raises(self):
        """When cached alias becomes stale and no replacement exists, raises error."""
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
        self.assertEqual(_BoundInnerClassBase._alias_cache[alias_key], 'AliasedParent')

        # Delete the alias entirely
        del Outer.AliasedParent

        # Now try again: medium path finds stale alias, slow path finds nothing, error
        o2 = Outer()
        with self.assertRaises(RuntimeError) as cm:
            o2.Child
        self.assertIn("Parent", str(cm.exception))
        self.assertIn("Every BoundInnerClass base must be", str(cm.exception))


class TestBoundInnerBaseFunction(unittest.TestCase):
    """Tests for bound_inner_base() helper function."""

    def test_bound_inner_base_with_proxy(self):
        """Test that bound_inner_base works (in all versions)"""
        class Outer:
            @BoundInnerClass
            class Inner:
                pass

        # Get the proxy (descriptor) directly from __dict__
        proxy = Outer.__dict__['Inner']
        result = bound_inner_base(proxy)

        self.assertTrue(isinstance(result, _ClassProxy) or (result is Outer.Inner))
        self.assertEqual(result.__name__, "Inner")


class TestGetOuterWeakrefInternal(unittest.TestCase):
    """Tests for _get_outer_weakref internal function."""

    def test_get_outer_weakref_with_regular_class(self):
        """_get_outer_weakref returns None for regular classes."""
        class Regular:
            pass

        result = _get_outer_weakref(Regular)
        self.assertIsNone(result)

    def test_get_outer_weakref_with_bound_class(self):
        """_get_outer_weakref returns the weakref for bound classes."""
        class Outer:
            @BoundInnerClass
            class Inner: # pragma: nocover
                def __init__(self, outer):
                    self.outer = outer

        o = Outer()
        BoundInner = o.Inner

        result = _get_outer_weakref(BoundInner)
        self.assertIsNotNone(result)
        self.assertIs(result(), o)


class TestUnboundInternal(unittest.TestCase):
    """Tests for _unbound internal function."""

    def test_unbound_with_non_class(self):
        """_unbound returns None for non-class values."""
        result = _unbound("not a class")
        self.assertIsNone(result)

        result = _unbound(123)
        self.assertIsNone(result)

    def test_unbound_with_non_bindable_class(self):
        """_unbound returns None for non-bindable classes."""
        class Regular:
            pass

        result = _unbound(Regular)
        self.assertIsNone(result)

    def test_unbound_with_bound_class(self):
        """_unbound returns the unbound class for bound classes."""
        class Outer:
            @BoundInnerClass
            class Inner: # pragma: nocover
                def __init__(self, outer):
                    self.outer = outer

        o = Outer()
        BoundInner = o.Inner

        result = _unbound(BoundInner)
        self.assertIs(result, Outer.Inner)


class TestCacheThreadSafety(unittest.TestCase):
    """Tests for thread-safety of the cache."""

    def test_cache_set_returns_existing_value(self):
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
        self.assertIs(result1, BoundClass1)

        # Second set with different bound class should return BoundClass1 (the existing one)
        result2 = cache.set(TestClass, BoundClass2)
        self.assertIs(result2, BoundClass1)

        # Get should also return BoundClass1
        result3 = cache.get(TestClass)
        self.assertIs(result3, BoundClass1)


def run_tests():
    bigtestlib.run(name="big.boundinnerclass", module=__name__)


if __name__ == "__main__":  # pragma: no cover
    run_tests()
    bigtestlib.finish()
