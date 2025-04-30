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



# --8<-- start loop_context tests --8<--

class LoopContextTests(unittest.TestCase):
    def test_loop_context(self):
        self.assertEqual(repr(undefined), '<Undefined>')
        with self.assertRaises(TypeError):
            x = Undefined()

        # iterator yields zero things:
        # loop_context should also never yield.
        for ctx, i in loop_context( [] ): # pragma: nocover
            self.assertTrue(False)

        # iterator yields one thing:
        # loop_context should be is_first *and* is_last.
        for start in range(-2, 5):
            with self.subTest(start=start):
                first_time = True
                for ctx, o in loop_context(('abc',), start):
                    self.assertTrue(first_time)
                    first_time = False

                    self.assertIsInstance(ctx, big.LoopContext)
                    self.assertTrue(ctx.is_first)
                    self.assertTrue(ctx.is_last)

                    # the length and countdown properties both cache _length.
                    # so, examine length first this time...
                    self.assertEqual(ctx.length, 1)

                    self.assertEqual(ctx.index, start)
                    self.assertEqual(ctx.countdown, start)

                    self.assertEqual(ctx.previous, big.undefined)
                    self.assertEqual(ctx.current, o)
                    self.assertEqual(ctx.next, big.undefined)


        # iterator yields four things
        for start in range(-2, 5):
            with self.subTest(start=start):
                i = start
                items = 'abcd'
                is_first = True

                my_items = list(items)
                my_items.append(big.undefined)
                my_iterator = iter(my_items)
                buffer = [big.undefined, big.undefined, next(my_iterator)]

                countdowns = []
                indices = []

                for ctx, o in loop_context(items, start):
                    self.assertIsInstance(ctx, big.LoopContext)
                    self.assertEqual(ctx.is_first, is_first)
                    is_last = (o == items[-1])
                    self.assertEqual(ctx.is_last, is_last)

                    self.assertEqual(ctx.index, i)
                    # ... and examine countdown first this time.
                    self.assertEqual(ctx.countdown, start + len(items) - (1 + i - start))

                    buffer.pop(0)
                    buffer.append(next(my_iterator))

                    self.assertEqual(ctx.previous, buffer[0])
                    self.assertEqual(ctx.current, buffer[1])
                    self.assertEqual(ctx.next, buffer[2])

                    self.assertEqual(ctx.length, len(items))

                    countdowns.append(ctx.countdown)
                    indices.append(ctx.index)

                    i += 1
                    is_first = False

                reversed_countdowns = list(countdowns)
                reversed_countdowns.reverse()
                self.assertEqual(reversed_countdowns, indices)

# --8<-- end loop_context tests --8<--

def run_tests():
    bigtestlib.run(name="big.itertools", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
