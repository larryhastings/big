#!/usr/bin/env python3

_license = """
big
Copyright 2022-2023 Larry Hastings
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
from big.boundinnerclass import *
import itertools
import re
import unittest


class Outer(object):
    @BoundInnerClass
    class Inner(object):
        def __init__(self, outer):
            self.outer = outer

    @BoundInnerClass
    class SubclassOfInner(Inner.cls):
        def __init__(self, outer):
            super().__init__()
            assert self.outer == outer

    @BoundInnerClass
    class SubsubclassOfInner(SubclassOfInner.cls):
        def __init__(self, outer):
            super().__init__()
            assert self.outer == outer

    @BoundInnerClass
    class Subclass2OfInner(Inner.cls):
        def __init__(self, outer):
            super().__init__()
            assert self.outer == outer

    class RandomUnboundInner(object):
        def __init__(self):
            super().__init__()
            pass

    @BoundInnerClass
    class MultipleInheritanceTest(SubclassOfInner.cls,
                 RandomUnboundInner,
                 Subclass2OfInner.cls):
        def __init__(self, outer, unittester):
            super().__init__()
            unittester.assertEqual(self.outer, outer)

    @UnboundInnerClass
    class UnboundSubclassOfInner(Inner.cls):
        pass

    @UnboundInnerClass
    class SubclassOfUnboundSubclassOfInner(UnboundSubclassOfInner.cls):
        pass


class BigBoundInnerClassesTests(unittest.TestCase):

    def test_cached(self):
        outer = Outer()
        inner1 = outer.Inner
        inner2 = outer.Inner
        self.assertIs(inner1, inner2)

    def test_permutations(self):
        def test_permutation(ordering):
            outer = Outer()
            # This strange "for" statement lets us test every possible order of
            # initialization for the "inner" / "subclass" / "subsubclass" objects.
            # We always iterate over all three numbers, but in a different order each time.
            for which in ordering:
                if   which == 1: inner = outer.Inner()
                elif which == 2: subclass = outer.SubclassOfInner()
                elif which == 3: subsubclass = outer.SubsubclassOfInner()

            self.assertEqual(outer.Inner, outer.Inner)
            self.assertIsInstance(inner, outer.Inner)
            self.assertIsInstance(inner, Outer.Inner)

            self.assertIsInstance(subclass, Outer.SubclassOfInner)
            self.assertIsInstance(subclass, outer.SubclassOfInner)
            self.assertIsInstance(subclass, Outer.Inner)
            self.assertIsInstance(subclass, outer.Inner)

            self.assertIsInstance(subsubclass, Outer.SubsubclassOfInner)
            self.assertIsInstance(subsubclass, outer.SubsubclassOfInner)
            self.assertIsInstance(subsubclass, Outer.SubclassOfInner)
            self.assertIsInstance(subsubclass, outer.SubclassOfInner)
            self.assertIsInstance(subsubclass, Outer.Inner)
            self.assertIsInstance(subsubclass, outer.Inner)

        for ordering in itertools.permutations([1, 2, 3]):
            test_permutation(ordering)

    def test_multiple_inheritance(self):
        outer = Outer()
        multiple_inheritance_test = outer.MultipleInheritanceTest(self)
        self.assertEqual(outer.MultipleInheritanceTest.mro(),
            [
            # bound inner class, notice lowercase-o "outer"
            outer.MultipleInheritanceTest,
            # unbound inner class, notice uppercase-o "Outer"
            Outer.MultipleInheritanceTest,
            outer.SubclassOfInner, # bound
            Outer.SubclassOfInner, # unbound
            Outer.RandomUnboundInner, # etc.
            outer.Subclass2OfInner,
            Outer.Subclass2OfInner,
            outer.Inner,
            Outer.Inner,
            object
            ]
            )

    def test_unbound_subclass_of_inner_class(self):
        outer = Outer()
        UnboundSubclassOfInner = outer.UnboundSubclassOfInner
        self.assertEqual(UnboundSubclassOfInner.mro(),
            [
            outer.UnboundSubclassOfInner,
            Outer.UnboundSubclassOfInner,
            outer.Inner,
            Outer.Inner,
            object
            ]
            )

        SubclassOfUnboundSubclassOfInner = outer.SubclassOfUnboundSubclassOfInner
        self.assertEqual(SubclassOfUnboundSubclassOfInner.mro(),
            [
            outer.SubclassOfUnboundSubclassOfInner,
            Outer.SubclassOfUnboundSubclassOfInner,
            outer.UnboundSubclassOfInner,
            Outer.UnboundSubclassOfInner,
            outer.Inner,
            Outer.Inner,
            object,
            ]
            )

    def test_inner_child(self):
        outer = Outer()
        class InnerChild(outer.Inner):
            pass

        inner_child = InnerChild()

        self.assertIsInstance(inner_child, Outer.Inner)
        self.assertIsInstance(inner_child, InnerChild)
        self.assertIsInstance(inner_child, outer.Inner)

        repr_re = re.compile(r"^<[A-Za-z0-9_]+\.InnerChild object bound to <[A-Za-z0-9_]+\.Outer object at 0x")
        match = repr_re.match(repr(inner_child))
        self.assertTrue(match)

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


def run_tests():
    bigtestlib.run(name="big.boundinnerclass", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
