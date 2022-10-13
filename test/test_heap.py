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

import big
import unittest


original_values = [
    5,
    1,
    10,
    2,
    20,
    7,
    15,
    25,
    ]


class BigTests(unittest.TestCase):
    def test_heap_basics(self):
        h = big.Heap()
        for value in original_values:
            h.append(value)
        values = []
        while h:
            values.append(h.popleft())
        sorted_values = list(sorted(values))
        self.assertEqual(values, sorted_values)

    def test_heap_preinitialize_and_iteration(self):
        h2 = big.Heap(original_values)
        self.assertEqual(len(h2), len(original_values))
        values = list(h2)
        sorted_values = list(sorted(values))
        self.assertEqual(values, sorted_values)

    def test_dont_modify_during_iteration(self):
        h = big.Heap(original_values)
        with self.assertRaises(RuntimeError):
            for value in h:
                h.append(45)
        with self.assertRaises(RuntimeError):
            for value in h:
                h.extend([44, 55, 66])
        with self.assertRaises(RuntimeError):
            for value in h:
                h.remove(20)
        with self.assertRaises(RuntimeError):
            for value in h:
                h.popleft()
        with self.assertRaises(RuntimeError):
            for value in h:
                h.popleft_and_append(33)
        with self.assertRaises(RuntimeError):
            for value in h:
                h.append_and_popleft(33)
        with self.assertRaises(RuntimeError):
            for value in h:
                h.clear()

    def test_random_one_liner_methods(self):
        h = big.Heap()
        self.assertEqual(len(h), 0)
        self.assertFalse(h)
        h.extend(original_values)
        self.assertEqual(len(h), len(original_values))
        self.assertTrue(h)
        self.assertTrue(5 in h)
        self.assertFalse(6 in h)

        self.assertEqual(h[:3], [1, 2, 5])
        self.assertEqual(h[:-5], [1, 2, 5])
        self.assertEqual(h[-3:], [15, 20, 25])
        self.assertEqual(h[5:], [15, 20, 25])
        self.assertEqual(h[::2], [1, 5, 10, 20])

        h2 = h.copy()
        self.assertEqual(h, h2)
        self.assertEqual(h.queue, h2.queue)
        h2 = big.Heap(original_values)
        self.assertEqual(h, h2)
        self.assertEqual(h.queue, h2.queue)

        h.clear()
        self.assertEqual(len(h), 0)
        self.assertFalse(h)

        h2 = big.Heap()
        self.assertEqual(h, h2)

        h.extend((3, 1, 2))
        self.assertEqual(list(h), [1, 2, 3])
        h.remove(2)
        self.assertEqual(list(h), [1, 3])
        o = h.append_and_popleft(4)
        self.assertEqual(o, 1)
        self.assertEqual(list(h), [3, 4])
        o = h.append_and_popleft(2)
        self.assertEqual(o, 2)
        self.assertEqual(list(h), [3, 4])
        o = h.popleft_and_append(2)
        self.assertEqual(o, 3)
        self.assertEqual(list(h), [2, 4])

        with self.assertRaises(TypeError):
            h[1.5]
        with self.assertRaises(TypeError):
            h['abc']



    def test_getitem(self):
        h = big.Heap(original_values)
        self.assertEqual(h[0], 1)
        self.assertEqual(h[1], 2)
        self.assertEqual(h[-1], 25)
        self.assertEqual(h[-2], 20)
        self.assertEqual(h[0:4], [1, 2, 5, 7])
        self.assertEqual(h[-4:], [10, 15, 20, 25])
        sorted_values = sorted(original_values)
        self.assertEqual(h[:], sorted_values)
        self.assertEqual(h[:], h.queue)

    def test_reprs(self):
        h = big.Heap(original_values)
        self.assertEqual(repr(h)[:6], '<Heap ')
        self.assertEqual(repr(iter(h))[:20], '<HeapIterator <Heap ')



import bigtestlib

def run_tests():
    bigtestlib.run(name="big.heap", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
