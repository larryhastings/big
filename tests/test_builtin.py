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

import big.all as big
from big.all import ClassRegistry
import unittest


class BigBuiltinTests(unittest.TestCase):

    def test_try_int(self):
        self.assertTrue(big.try_int(0))
        self.assertTrue(big.try_int(0.0))
        self.assertTrue(big.try_int("0"))

        self.assertFalse(big.try_int(3j))
        self.assertFalse(big.try_int(None))
        self.assertFalse(big.try_int(()))
        self.assertFalse(big.try_int({}))
        self.assertFalse(big.try_int([]))
        self.assertFalse(big.try_int(set()))
        self.assertFalse(big.try_int("0.0"))
        self.assertFalse(big.try_int("abc"))
        self.assertFalse(big.try_int("3j"))
        self.assertFalse(big.try_int("None"))

    def test_try_float(self):
        self.assertTrue(big.try_float(0))
        self.assertTrue(big.try_float(0.0))
        self.assertTrue(big.try_float("0"))
        self.assertTrue(big.try_float("0.0"))

        self.assertFalse(big.try_float(3j))
        self.assertFalse(big.try_float(None))
        self.assertFalse(big.try_float(()))
        self.assertFalse(big.try_float({}))
        self.assertFalse(big.try_float([]))
        self.assertFalse(big.try_float(set()))
        self.assertFalse(big.try_float("abc"))
        self.assertFalse(big.try_float("3j"))
        self.assertFalse(big.try_float("None"))

    def test_get_int(self):
        sentinel = object()
        self.assertEqual(big.get_int(0,      sentinel), 0)
        self.assertEqual(big.get_int(0.0,    sentinel), 0)
        self.assertEqual(big.get_int("0",    sentinel), 0)

        self.assertEqual(big.get_int(35,     sentinel), 35)
        self.assertEqual(big.get_int(35.1,   sentinel), 35)

        self.assertEqual(big.get_int(3j,     sentinel), sentinel)
        self.assertEqual(big.get_int(None,   sentinel), sentinel)
        self.assertEqual(big.get_int((),     sentinel), sentinel)
        self.assertEqual(big.get_int({},     sentinel), sentinel)
        self.assertEqual(big.get_int([],     sentinel), sentinel)
        self.assertEqual(big.get_int(set(),  sentinel), sentinel)
        self.assertEqual(big.get_int("",     sentinel), sentinel)
        self.assertEqual(big.get_int("0.0",  sentinel), sentinel)
        self.assertEqual(big.get_int("abc",  sentinel), sentinel)
        self.assertEqual(big.get_int("3j",   sentinel), sentinel)
        self.assertEqual(big.get_int("None", sentinel), sentinel)

        d = {}
        self.assertEqual(big.get_int(d), d)
        self.assertEqual(big.get_int(3j), 3j)
        self.assertEqual(big.get_int(None), None)
        self.assertEqual(big.get_int("abc"), "abc")

    def test_get_float(self):
        sentinel = object()
        self.assertEqual(big.get_float(0,      sentinel), 0.0)
        self.assertEqual(big.get_float(0.0,    sentinel), 0.0)
        self.assertEqual(big.get_float("0",    sentinel), 0.0)
        self.assertEqual(big.get_float("0.0",  sentinel), 0.0)

        self.assertEqual(big.get_float(35,     sentinel), 35.0)
        self.assertEqual(big.get_float(35.1,   sentinel), 35.1)

        self.assertEqual(big.get_float(3j,     sentinel), sentinel)
        self.assertEqual(big.get_float(None,   sentinel), sentinel)
        self.assertEqual(big.get_float((),     sentinel), sentinel)
        self.assertEqual(big.get_float({},     sentinel), sentinel)
        self.assertEqual(big.get_float([],     sentinel), sentinel)
        self.assertEqual(big.get_float(set(),  sentinel), sentinel)
        self.assertEqual(big.get_float("",     sentinel), sentinel)
        self.assertEqual(big.get_float("abc",  sentinel), sentinel)
        self.assertEqual(big.get_float("3j",   sentinel), sentinel)
        self.assertEqual(big.get_float("None", sentinel), sentinel)

        d = {}
        self.assertEqual(big.get_float(d), d)
        self.assertEqual(big.get_float(3j), 3j)
        self.assertEqual(big.get_float(None), None)
        self.assertEqual(big.get_float("abc"), "abc")

    def test_get_int_or_float(self):
        sentinel = object()
        self.assertEqual(     big.get_int_or_float(0,       sentinel), 0)
        self.assertIsInstance(big.get_int_or_float(0,       sentinel), int)
        self.assertEqual(     big.get_int_or_float("0",     sentinel), 0)
        self.assertIsInstance(big.get_int_or_float("0",     sentinel), int)

        self.assertEqual(     big.get_int_or_float(12345,   sentinel), 12345)
        self.assertIsInstance(big.get_int_or_float(12345,   sentinel), int)
        self.assertEqual(     big.get_int_or_float("12345", sentinel), 12345)
        self.assertIsInstance(big.get_int_or_float("12345", sentinel), int)

        self.assertEqual(     big.get_int_or_float(0.0,     sentinel), 0)
        self.assertIsInstance(big.get_int_or_float("0.0",   sentinel), int)
        self.assertEqual(     big.get_int_or_float(3.5,     sentinel), 3.5)
        self.assertIsInstance(big.get_int_or_float("3.5",   sentinel), float)
        self.assertEqual(     big.get_int_or_float(123.0,   sentinel), 123)
        self.assertIsInstance(big.get_int_or_float("123.0", sentinel), int)

        self.assertEqual(big.get_int_or_float("abc",  sentinel), sentinel)
        self.assertEqual(big.get_int_or_float("3j",   sentinel), sentinel)
        self.assertEqual(big.get_int_or_float("None", sentinel), sentinel)
        self.assertEqual(big.get_int_or_float("",     sentinel), sentinel)
        self.assertEqual(big.get_int_or_float(3j,     sentinel), sentinel)
        self.assertEqual(big.get_int_or_float(None,   sentinel), sentinel)
        self.assertEqual(big.get_int_or_float({},     sentinel), sentinel)
        self.assertEqual(big.get_int_or_float((),     sentinel), sentinel)
        self.assertEqual(big.get_int_or_float(set(),  sentinel), sentinel)

        d = {}
        self.assertEqual(big.get_int_or_float(d), d)
        self.assertEqual(big.get_int_or_float(3j), 3j)
        self.assertEqual(big.get_int_or_float(None), None)
        self.assertEqual(big.get_int_or_float("abc"), "abc")

    def test_pure_virtual(self):
        @big.pure_virtual()
        def uncallable(a): # pragma: no cover
            print(f"hey, look! we wuz called! and a={a}, just ask Ayn Rand!")

        with self.assertRaises(NotImplementedError):
            uncallable('a')

    def test_ModuleManager(self):
        ##
        ## ModuleManager.clean only works properly
        ## at module scope and class scope.
        ## (Maybe it works in function scope in 3.13+?)
        ##
        ## So, let's test it inside class scope.
        class PointlessClass:
            mm = big.ModuleManager()
            mm.delete('mm')

            with self.assertRaises(TypeError):
                mm.export(35)
            with self.assertRaises(TypeError):
                mm.delete(35)

            def foo(): pass
            result = mm.export(foo)
            self.assertIs(result, foo)
            result = mm.delete(foo)
            self.assertIs(result, foo)

            mm.export("bar", "bat", "zip")
            mm.delete("bar", "bat", "zoo")

            self.assertEqual(mm.__all__, ['foo', 'bar', 'bat', 'zip'])
            self.assertEqual(mm.deletions, ['mm', 'foo', 'bar', 'bat', 'zoo'])

            bar = bat = zoo = 3
            mm.clean()

        self.assertFalse(hasattr(PointlessClass, 'mm'))
        self.assertFalse(hasattr(PointlessClass, 'foo'))
        self.assertFalse(hasattr(PointlessClass, 'bar'))
        self.assertFalse(hasattr(PointlessClass, 'bat'))
        self.assertFalse(hasattr(PointlessClass, 'zoo'))



class TestClassRegistry(unittest.TestCase):
    """Tests for ClassRegistry."""

    def test_register_and_access_by_attribute(self):
        """Classes can be registered and accessed as attributes."""


        registry = ClassRegistry()

        @registry()
        class Foo:
            pass

        self.assertIs(registry.Foo, Foo)

    def test_register_with_custom_name(self):
        """Classes can be registered with a custom name."""


        registry = ClassRegistry()

        @registry('CustomName')
        class Foo:
            pass

        self.assertIs(registry.CustomName, Foo)
        self.assertNotIn('Foo', registry)

    def test_attribute_error_for_missing(self):
        """Accessing missing attribute raises AttributeError."""


        registry = ClassRegistry()

        with self.assertRaises(AttributeError) as cm:
            registry.NonExistent
        self.assertEqual(str(cm.exception), 'NonExistent')

    def test_use_for_inheritance(self):
        """Registry can be used for cross-scope inheritance."""


        base = ClassRegistry()

        @base()
        class Parent:
            x = 1

        class Child(base.Parent):
            y = 2

        self.assertTrue(issubclass(Child, Parent))
        self.assertEqual(Child.x, 1)
        self.assertEqual(Child.y, 2)

    def test_dict_operations_still_work(self):
        """Registry still works as a dict."""


        registry = ClassRegistry()

        @registry()
        class Foo:
            pass

        self.assertIn('Foo', registry)
        self.assertEqual(len(registry), 1)
        self.assertEqual(list(registry.keys()), ['Foo'])
        self.assertEqual(list(registry.values()), [Foo])


def run_tests():
    bigtestlib.run(name="big.builtin", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
