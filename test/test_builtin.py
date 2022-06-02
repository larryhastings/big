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

class BigTests(unittest.TestCase):

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

    def test_prefer_int_to_float(self):
        sentinel = object()
        self.assertEqual(big.get_int_or_float(0,      sentinel), 0)
        self.assertEqual(big.get_int_or_float("0",    sentinel), 0)

        self.assertEqual(big.get_int_or_float(0.0,    sentinel), 0.0)
        self.assertEqual(big.get_int_or_float("0.0",  sentinel), 0.0)

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


import bigtestlib

def run_tests():
    bigtestlib.run(name="big.__init__", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
