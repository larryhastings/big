#!/usr/bin/env python3

_license = """
big
Copyright 2022 Larry Hastings
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
import big
import big.text
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



import bigtestlib

def run_tests():
    bigtestlib.run(name="big.itertools", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
