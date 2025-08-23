#!/usr/bin/env python3

_license = """
big
Copyright 2022-2025 Larry Hastings
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

from big.itertools import *

import big.all as big
import copy
import math
import re
import unittest


class BigItertoolsTests(unittest.TestCase):

    def test_conventional_iteration(self):
        pbi = big.PushbackIterator(range(10))
        pbi = iter(pbi)
        values = []
        for i in pbi:
            values.append(i)
            if isinstance(i, str):
                continue
            if i % 2 == 0:
                pbi.push(str(i))
        self.assertEqual(values, [0, '0', 1, 2, '2', 3, 4, '4', 5, 6, '6', 7, 8, '8', 9])


    def test_next_and_bool(self):
        for test_bool in range(2):
            pbi = big.PushbackIterator(range(1))
            expected = 0
            sentinel = object()
            for i in range(2):
                if test_bool:
                    self.assertTrue(bool(pbi))
                self.assertEqual(pbi.next(sentinel), expected)
                if test_bool:
                    self.assertFalse(bool(pbi))
                self.assertEqual(pbi.next(sentinel), sentinel)
                if test_bool:
                    self.assertFalse(bool(pbi))
                self.assertEqual(pbi.next(sentinel), sentinel)
                if test_bool:
                    self.assertFalse(bool(pbi))
                # now push something and do it all over again
                expected = 'a'
                pbi.push(expected)


    def test_repr(self):
        pbi = big.PushbackIterator()
        pbi.push(3)
        self.assertEqual(repr(pbi), "<PushbackIterator i=None stack=[3]>")

    def test_dunder_next_raising_stop_iteration(self):
        # A little white-box testing here to make coverage happy.
        # In order to get __next__ to specifically raise StopIteration,
        # we have to use pbi.next to empty out the iterator.
        pbi = big.PushbackIterator((0,))
        sentinel = object()
        self.assertEqual(pbi.next(sentinel), 0)
        self.assertEqual(pbi.next(sentinel), sentinel)
        for i in pbi:
            self.assertEqual(True, False, "shouldn't reach here! pbi is exhausted!") # pragma: no cover



# --8<-- start tidy itertools tests --8<--

class TidyItertoolsTests(unittest.TestCase):
    def test_iterator_context(self):
        self.assertEqual(repr(undefined), '<Undefined>')
        with self.assertRaises(TypeError):
            x = Undefined()

        self.assertFalse(undefined)

        # iterator yields zero things:
        # iterator_context should also never yield.
        for ctx, i in iterator_context( [] ): # pragma: nocover
            self.assertTrue(False)

        # iterator yields one thing:
        # iterator_context should be is_first *and* is_last.
        for start in range(-2, 5):
            with self.subTest(start=start):
                first_time = True
                for ctx, o in iterator_context((('abc',)), start):
                    self.assertTrue(first_time)
                    first_time = False

                    self.assertIsInstance(ctx, IteratorContext)
                    self.assertTrue(ctx.is_first)
                    self.assertTrue(ctx.is_last)

                    # the length and countdown properties both cache _length.
                    # so, examine length first this time...
                    self.assertEqual(ctx.length, 1)

                    self.assertEqual(ctx.index, start)
                    self.assertEqual(ctx.countdown, start)

                    with self.assertRaises(AttributeError):
                        print(ctx.previous)
                    self.assertEqual(ctx.current, o)
                    with self.assertRaises(AttributeError):
                        print(ctx.next)

                    self.assertEqual(repr(ctx), f"IteratorContext(iterator=('abc',), start={start}, index={start}, is_first=True, is_last=True, current='abc')")


        # iterator yields four things
        for start in range(-2, 5):
            with self.subTest(start=start):
                i = start
                items = 'abcd'
                is_first = True

                my_items = list(items)
                my_items.append(undefined)
                my_iterator = iter(my_items)
                buffer = [undefined, undefined, next(my_iterator)]

                countdowns = []
                indices = []

                for ctx, o in iterator_context(items, start):
                    self.assertIsInstance(ctx, IteratorContext)
                    self.assertEqual(ctx.is_first, is_first)
                    is_last = (o == items[-1])
                    self.assertEqual(ctx.is_last, is_last)

                    self.assertEqual(ctx.index, i)
                    # ... and examine countdown first this time.
                    self.assertEqual(ctx.countdown, start + len(items) - (1 + i - start))

                    buffer.pop(0)
                    buffer.append(next(my_iterator))

                    if is_first:
                        with self.assertRaises(AttributeError):
                            print(ctx.previous)
                    else:
                        self.assertEqual(ctx.previous, buffer[0])
                    self.assertEqual(ctx.current, buffer[1])
                    if is_last:
                        with self.assertRaises(AttributeError):
                            print(ctx.next)
                    else:
                        self.assertEqual(ctx.next, buffer[2])

                    self.assertEqual(ctx.length, len(items))

                    countdowns.append(ctx.countdown)
                    indices.append(ctx.index)

                    i += 1
                    is_first = False

                reversed_countdowns = list(countdowns)
                reversed_countdowns.reverse()
                self.assertEqual(reversed_countdowns, indices)

    def test_iterator_filter(self):
        l = [1, 'a', 2, 'b', 3, 'c', 4, 'd', 5]

        def test(expected, **kwargs):
            got = list(iterator_filter(l, **kwargs))
            self.assertEqual(expected, got)

        test([1, 'a', 2, 'b'],         stop_at_value=3)
        test([1, 'a', 2, 'b', 3],      stop_at_in=set(('c', 4, 'd')))
        test([1, 'a', 2, 'b', 3, 'c'], stop_at_predicate=lambda o: o==4)

        test([1, 'a', 2, 'b'], stop_at_count= 4)
        test([1, 'a', 2],      stop_at_count= 3)
        test([1, 'a'],         stop_at_count= 2)
        test([],               stop_at_count= 0)
        test([],               stop_at_count=-1)

        test([1, 'a', 2, 'b', 'c', 4, 'd', 5], reject_value=3)
        test([1, 'a', 2, 'b', 3, 5],           reject_in=set(('c', 4, 'd')))
        test([1, 'a', 2, 'b', 3, 'c', 'd', 5], reject_predicate=lambda o: o==4)

        test([3,],          only_value=3)
        test(['c', 4, 'd'], only_in=set(('c', 4, 'd')))
        test([2, 3, 4, 5],  only_predicate=lambda o: isinstance(o, int) and o > 1)

        seven_threes = (3, 33, 333, 3333, 33333, 333333, 3333333)
        six_threes   = (3, 33, 333, 3333, 33333, 333333)
        five_threes  = (3, 33, 333, 3333, 33333)
        four_threes  = (3, 33, 333, 3333)
        three_threes = (3, 33, 333)
        two_threes   = (3, 33)
        one_three    = (3,)

        class OnlyFourThrees(int):
            def __ne__(self, other):
                return other not in four_threes

        only_four_threes = OnlyFourThrees()

        # now test with all nine rules in play
        def test(l, expected):
            got = list(iterator_filter(l,
                stop_at_value='stop1',
                stop_at_in=set(('stop2', 'stop3', 'stop4')),
                stop_at_predicate=lambda o: o=='stop5',
                stop_at_count=4,

                reject_value=3333333,                 # seven threes
                reject_in=set((333333,)),             # six threes
                reject_predicate=lambda o: o ==33333, # five threes

                only_value=only_four_threes,
                only_in=three_threes,
                only_predicate=lambda o: o in two_threes,
                ))
            self.assertEqual(expected, got)

        test([33, 3, 'stop1', 3, 33], [33, 3])
        test([33, 3, 'stop3', 3, 33], [33, 3])
        test([33, 3, 'stop5', 3, 33], [33, 3])

        test([33, 3, 3333333, 3, 33], [33, 3, 3, 33])
        test([33, 3,  333333, 3, 33], [33, 3, 3, 33])
        test([33, 3,   33333, 3, 33], [33, 3, 3, 33])

        test([33, 3,    3333, 3, 33], [33, 3, 3, 33])
        test([33, 3,     333, 3, 33], [33, 3, 3, 33])
        test([33, 3,      33, 3, 33], [33, 3, 33, 3])

        # test exhaustion
        it = filterator(l, stop_at_value=2)
        got = list(it)
        self.assertEqual(got, [1, 'a'])
        got = list(it)
        self.assertEqual(got, [])
        got = list(it)
        self.assertEqual(got, [])

        # regression:
        #       iterator_filter(i, stop_at_count=0)
        #   should *not* iterate over i!
        #   it should start out in an "exhausted" state and never touch i.
        def fail_immediately(): # pragma: nocover
            raise RuntimeError('you should not call next on me!')
            yield 1

        for stop_value in range(-20, 1):
            with self.subTest(stop_value=stop_value):
                for i in f8r(fail_immediately(), stop_at_count=stop_value): # pragma: nocover
                    raise RuntimeError(f"we shouldn't have entered the body of this for loop! i={i!r}")




# --8<-- end tidy itertools tests --8<--

def run_tests():
    bigtestlib.run(name="big.itertools", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
