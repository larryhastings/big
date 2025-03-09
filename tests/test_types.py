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
big_dir = bigtestlib.preload_local_big()

from itertools import zip_longest
import pickle
import string
import sys
import unittest

from big.types import String, Pattern
from big.tokens import *


source = "C:\\AUTOEXEC.BAT"
source2 = "C:\\HIMEM.SYS"
first_line_number = 1
first_column_number = 1

alphabet = String('abcdefghijklmnopqrstuvwxyz', source=source)
abcde = alphabet[:5]
fghij = alphabet[5:10]
himem = String('QEMM\n', source=source2)
line1 = String('line 1!\n', source=source)
line2 = String('line 2.\n', source=source, line_number=2)
words = String('this is a series of words.', source=source)
tabs  = String('this\tis\ta\tseries\tof\twords\twith\ttabs', source=source)
leading_and_trailing  = String('            a b c                  ', source=source)
leading_only  = String('            a b c', source=source)
trailing_only  = String('a b c            ', source=source)
all_uppercase  = String("HELLO WORLD!", source=source)
title_case  = String("Hello World!", source=source)
kooky1 = String("kooky land 1", line_number=44,                   first_line_number=44                        )
kooky2 = String("kooky land 2",                 column_number=33,                       first_column_number=33)
kooky3 = String("kooky land 3", line_number=44, column_number=33, first_line_number=44, first_column_number=33)

splitlines_demo = String(' a \n b \r c \r\n d \n\r e ', source='Z')

l2 = String("ab\ncd\nef", source='xz')


chipmunk = String('🐿️', source='tic e tac')


l = abcde

values = [abcde, himem, line1, line2, tabs, words, splitlines_demo, leading_and_trailing, leading_only, trailing_only, all_uppercase, title_case, kooky1, kooky2, kooky3]


class BigStringTests(unittest.TestCase):

    maxDiff = 2**32

    ##
    ## these methods with a type-sounding name
    ## assert that the value you pass in for "got"
    ## is of that specific type, as well as ensuring
    ## that the value == "expected".
    ##

    def assertBool(self, got, expected):
        self.assertIsInstance(got, bool)
        self.assertIs(got, expected)

    def assertBytes(self, got, expected):
        self.assertIsInstance(got, bytes)
        self.assertEqual(got, expected)

    def assertInt(self, got, expected):
        self.assertIsInstance(got, int)
        self.assertEqual(got, expected)

    def assertString(self, got, expected):
        self.assertIsInstance(got, String)
        self.assertEqual(got, expected)

    def assertStr(self, got, expected):
        self.assertIsInstance(got, str)
        self.assertNotIsInstance(got, String)
        self.assertEqual(got, expected)

    ##
    ## below this comment is a test_ method
    ## for *every* attribute of a str object,
    ## as reported by dir('').
    ##
    ## if we don't need to test it, I left it
    ## in, with a comment and a pass statement.
    ##

    def test_constructor(self):
        self.assertString(String('abc'), 'abc')

        self.assertEqual(String(abcde), abcde)

        ar = self.assertRaises

        with ar(TypeError):
            String(54321)
        with ar(TypeError):
            String(33.4)
        with ar(TypeError):
            String(['x', 'y'])

        self.assertString(String('abc', source=None, origin=None), 'abc')
        self.assertString(String('abc', source='xyz', origin=None), 'abc')
        s = String('abc')
        self.assertString(String('abc', source=None, origin=s), 'abc')
        self.assertString(String('abc', source='xyz', origin=s), 'abc')

        with ar(TypeError):
            String('abc', source=33.5)
        with ar(TypeError):
            String('abc', source=-2)
        with ar(TypeError):
            String('abc', source=['x'])

        with ar(TypeError):
            String('abc', origin=33.5)
        with ar(TypeError):
            String('abc', origin=-2)
        with ar(TypeError):
            String('abc', origin=['x'])

        with ar(TypeError):
            String('abc', line_number=33.5)
        with ar(ValueError):
            String('abc', line_number=-2)
        with ar(ValueError):
            String('abc', line_number=0)
        with ar(ValueError):
            String('abc', line_number=2, first_line_number=3)

        with ar(TypeError):
            String('abc', column_number=33.5)
        with ar(ValueError):
            String('abc', column_number=-2)
        with ar(ValueError):
            String('abc', column_number=0)
        with ar(ValueError):
            String('abc', column_number=2, first_column_number=3)

        with ar(TypeError):
            String('abc', offset=33.5)
        with ar(ValueError):
            String('abc', offset=-2)

        with ar(TypeError):
            String('abc', first_line_number=33.5)
        with ar(ValueError):
            String('abc', first_line_number=-2)

        with ar(TypeError):
            String('abc', first_column_number=33.5)
        with ar(ValueError):
            String('abc', first_column_number=-2)

        with ar(TypeError):
            String('abc', tab_width=33.5)
        with ar(ValueError):
            String('abc', tab_width=-2)
        with ar(ValueError):
            String('abc', tab_width=0)


    def test_attributes(self):
        s = String("abcde", source="source", line_number=3, column_number=4, first_line_number=1, first_column_number=2, tab_width=4)
        self.assertString(s, "abcde")
        self.assertStr(s.source, "source")
        self.assertInt(s.line_number, 3)
        self.assertInt(s.column_number, 4)
        self.assertInt(s.first_line_number, 1)
        self.assertInt(s.first_column_number, 2)
        self.assertInt(s.tab_width, 4)
        self.assertStr(s.where, '"source" line 3 column 4')

        s = String("abcde", line_number=3, column_number=4, first_line_number=1, first_column_number=2, tab_width=4)
        self.assertString(s, "abcde")
        self.assertEqual(s.source, None)
        self.assertInt(s.line_number, 3)
        self.assertInt(s.column_number, 4)
        self.assertInt(s.first_line_number, 1)
        self.assertInt(s.first_column_number, 2)
        self.assertInt(s.tab_width, 4)
        self.assertStr(s.where, 'line 3 column 4')

    def test___add__(self):
        self.assertString(l + " xyz", 'abcde xyz')
        self.assertString("boogie " + alphabet[22:], 'boogie wxyz')

        self.assertString(abcde + fghij, alphabet[:10])

        with self.assertRaises(TypeError):
            x = abcde + 35
        with self.assertRaises(TypeError):
            x = abcde + 55.0
        with self.assertRaises(TypeError):
            x = abcde + (1, 2)

    def test___radd__(self):
        with self.assertRaises(TypeError):
            x = 1 + abcde

        s = String("abcde", line_number=5, column_number=5)

        # if it works out like magic, you can get a String out
        # but the line and column numbers have to work.
        str_x = "wxyz" + str(s)
        x = "wxyz" + s
        self.assertIsInstance(x, String)
        self.assertEqual(x, str_x)
        self.assertEqual(x.line_number, 5)
        self.assertEqual(x.column_number, 1)

        str_x = "123\nwxyz" + str(s)
        x = "123\nwxyz" + s
        self.assertIsInstance(x, String)
        self.assertEqual(x, str_x)
        self.assertEqual(x.line_number, 4)
        self.assertEqual(x.column_number, 1)

        # prepending a String with a str might return a str, if:
        # too many columns
        self.assertStr("xyzxyzxyzxyzxyz" + s, "xyzxyzxyzxyzxyz" + str(s))
        # too many lines
        self.assertStr("abc\n\n\n\n\n\nwxyz" + s, "abc\n\n\n\n\n\nwxyz" + str(s))
        # not enough columns before a linebreak
        self.assertStr("abc\nx" + s, "abc\nx" + str(s))

        # if the string you prepend with contains a tab, you always get a str
        self.assertStr('x\ty' + s, 'x\tyabcde')
        # ... unless it's before a linebreak
        self.assertString('x\ty\nxxxx' + s, 'x\ty\nxxxxabcde')


    def test___class__(self):
        self.assertEqual(l.__class__, String)

    def test___contains__(self):
        # also tests .find and .index and .rfind and .rindex

        for s in ("b", "bc"):
            self.assertTrue(s in abcde)
            self.assertGreaterEqual(abcde.find(s), 0)
            self.assertGreaterEqual(abcde.rfind(s), 0)
            self.assertGreaterEqual(abcde.index(s), 0)
            self.assertGreaterEqual(abcde.rindex(s), 0)
        for s in ("q", "funk"):
            self.assertFalse(s in abcde)
            self.assertEqual(abcde.find(s), -1)
            self.assertEqual(abcde.rfind(s), -1)
            with self.assertRaises(ValueError):
                abcde.index(s)
            with self.assertRaises(ValueError):
                abcde.rindex(s)

        letters = set(string.ascii_letters) | set(string.punctuation) | set(string.whitespace)
        for value in values:
            in_value = set(str(value))
            not_in_value = letters - in_value
            for letter in in_value:
                self.assertTrue(letter in value)
                self.assertGreaterEqual(value.find(letter), 0)
                self.assertGreaterEqual(value.rfind(letter), 0)
                self.assertGreaterEqual(value.index(letter), 0)
                self.assertGreaterEqual(value.rindex(letter), 0)
            for letter in not_in_value:
                self.assertFalse(letter in value)
                self.assertEqual(value.find(letter), -1)
                self.assertEqual(value.rfind(letter), -1)
                with self.assertRaises(ValueError):
                    value.index(letter)
                with self.assertRaises(ValueError):
                    value.rindex(letter)

    def test___delattr__(self):
        with self.assertRaises(AttributeError):
            del l.source

    def test___dir__(self):
        # disabled again, until the interface stabilizes
        return
        str_dir = dir('')
        str_dir.extend(
            (
            '__module__',
            '__radd__',
            '__slots__',
            '_add',
            '_are_contiguous',
            '_column_number',
            '_compute_linebreak_offsets',
            '_first_column_number',
            '_first_line_number_delta',
            '_line_number',
            '_linebreak_offsets',
            '_source',
            '_partition',
            '_split',
            'bisect',
            'column_number',
            'first_column_number',
            'first_line_number',
            'line_number',
            'source',
            )
        )
        str_dir.sort()

        Line_dir = dir(l)
        Line_dir.sort()
        self.assertEqual(str_dir, Line_dir)

    def test___doc__(self):
        self.assertIsInstance(l.__doc__, str)
        self.assertTrue(l.__doc__)

    def test___eq__(self):
        self.assertEqual(l, str(l))
        self.assertEqual(l + 'x', str(l) + 'x')

    def test___format__(self):
        f = String('{abcde} {line1} {line2}', source=source)
        got = f.format(abcde=abcde, line1=line1, line2=line2)
        self.assertStr(got, 'abcde line 1!\n line 2.\n')
        got = f.format_map({'abcde': abcde, 'line1': line1, 'line2': line2})
        self.assertStr(got, 'abcde line 1!\n line 2.\n')

        # if the String is unchanged, return the String!
        f = String("{abcde}", source=source)
        got = f.format(abcde='{abcde}')
        self.assertString(f, got)
        got = f.format_map({'abcde': '{abcde}'})
        self.assertString(f, got)

    def test___ge__(self):
        self.assertGreaterEqual(l, str(l))
        self.assertGreaterEqual(l + 'x', str(l))
        self.assertGreaterEqual(str(l) + 'x', l)

    def test___getattribute__(self):
        self.assertEqual(l.source, source)
        self.assertEqual(l.line_number, first_line_number)
        self.assertEqual(l.column_number, first_column_number)

        self.assertEqual(line2.source, source)
        self.assertEqual(line2.line_number, first_line_number + 1)
        self.assertEqual(line2.column_number, first_column_number)

        self.assertEqual(himem.source, source2)
        self.assertEqual(himem.line_number, first_line_number)
        self.assertEqual(himem.column_number, first_column_number)

        with self.assertRaises(AttributeError):
            print(l.attribute_which_does_not_exist)

    def test___getitem__(self):
        s = str(abcde)
        length = len(s)
        for i in range(-length, length):
            self.assertString(abcde[i], String(s[i], source=source, column_number=first_column_number + (i % length)))

        self.assertString(abcde[1:4], String('bcd', source=source, column_number=first_column_number + 1))

        self.assertStr(abcde[1:-1:2], 'bd')

        # regression!
        last_zero = abcde[len(abcde):len(abcde)]
        self.assertEqual(last_zero.line_number, 1)
        self.assertEqual(last_zero.column_number, abcde.first_column_number + len(abcde))

        # *indexing* out of range raises IndexError.
        with self.assertRaises(IndexError):
            abcde[-20]
        with self.assertRaises(IndexError):
            abcde[33]

        # *sliciing* out of range clamps to allowed range.
        self.assertString(abcde[-20:], abcde)
        self.assertString(abcde[448:], abcde[length:length])

        # regression: if the string ended with a linebreak,
        # getting the zero-length string after that linebreak
        # would increment the line number
        s = String("x\n")

        endo = s[len(s):len(s)]
        self.assertEqual(endo.line_number, 2)
        self.assertEqual(endo[0:0].line_number, 2) # used to be 3!
        self.assertEqual(endo[0:0][0:0].line_number, 2) # used to be 4!
        self.assertEqual(endo[0:0][0:0][0:0].line_number, 2) # used to be 5!

    def test___getnewargs__(self):
        # String implements __getnewargs__, it's pickling machinery.
        for value in values:
            p = pickle.dumps(value)
            value2 = pickle.loads(p)
            self.assertString(value2, value)

    def test___getstate__(self):
        # __getstate__ is part of the pickling machinery.
        # we don't override str.__getstate__, pickling seems to work anyway.
        pass

    def test___gt__(self):
        self.assertGreaterEqual(l + 'x', str(l))
        self.assertGreaterEqual(str(l) + 'x', l)

    def test___hash__(self):
        # we reuse str.__hash__
        for value in values:
            s = str(value)
            self.assertEqual(hash(value), hash(s))

    def test___init__(self):
        # don't need to test this special
        pass

    def test___init_subclass__(self):
        # oh golly, idk.  don't subclass String, mkay?
        pass

    def test___iter__(self):
        for value in values:
            s = str(value)
            for i, (a, b) in enumerate(zip_longest(value, s)):
                self.assertEqual(a, b, f'failed on value={value!r} i={i!r} a={a!r} != b={b!r}')
                self.assertStr(b, s[i])
                self.assertString(a, value[i])

        # and now, a cool String feature
        l = String('a\nb\ncde\nf', source='s1')
        expected = [
            String('a',  source='s1', line_number=1, column_number=1, offset=0),
            String('\n', source='s1', line_number=1, column_number=2, offset=1),
            String('b',  source='s1', line_number=2, column_number=1, offset=2),
            String('\n', source='s1', line_number=2, column_number=2, offset=3),
            String('c',  source='s1', line_number=3, column_number=1, offset=4),
            String('d',  source='s1', line_number=3, column_number=2, offset=5),
            String('e',  source='s1', line_number=3, column_number=3, offset=6),
            String('\n', source='s1', line_number=3, column_number=4, offset=7),
            String('f',  source='s1', line_number=4, column_number=1, offset=8),
            ]
        for a, b in zip_longest(l, expected):
            self.assertString(a, b)

        l = String('a\nb\ncde\nf', source='s2', line_number=10, column_number=2, first_column_number=2, offset=99)
        expected = [
            String('a',  source='s2', line_number=10, column_number=2, offset=99),
            String('\n', source='s2', line_number=10, column_number=3, offset=100),
            String('b',  source='s2', line_number=11, column_number=2, offset=101),
            String('\n', source='s2', line_number=11, column_number=3, offset=102),
            String('c',  source='s2', line_number=12, column_number=2, offset=103),
            String('d',  source='s2', line_number=12, column_number=3, offset=104),
            String('e',  source='s2', line_number=12, column_number=4, offset=105),
            String('\n', source='s2', line_number=12, column_number=5, offset=106),
            String('f',  source='s2', line_number=13, column_number=2, offset=107),
            ]
        for a, b in zip_longest(l, expected):
            self.assertString(a, b)

        # test tab
        l = String('ab\tc', source='s2')
        expected = [
            String('a',  source='s2', line_number=1, column_number=1, offset=0),
            String('b',  source='s2', line_number=1, column_number=2, offset=1),
            String('\t', source='s2', line_number=1, column_number=3, offset=2),
            String('c',  source='s2', line_number=1, column_number=9, offset=3),
            ]
        for a, b in zip_longest(l, expected):
            self.assertString(a, b)

        # also test tab immediately after \r, because, reasons.
        l = String('ab\r\tc', source='s2')
        expected = [
            String('a',  source='s2', line_number=1, column_number=1, offset=0),
            String('b',  source='s2', line_number=1, column_number=2, offset=1),
            String('\r', source='s2', line_number=1, column_number=3, offset=2),
            String('\t', source='s2', line_number=2, column_number=1, offset=3),
            String('c',  source='s2', line_number=2, column_number=9, offset=4),
            ]
        for a, b in zip_longest(l, expected):
            self.assertString(a, b)

        # regression: at one point there was a bug, if the string ends with \r,
        # it wouldn't get yielded.  __next__ buffers \r in case it's followed
        # by \n, in which case we only break the line after the \n.
        l = String('a\nb\r\nc\r', source='s2')
        expected = [
            String('a',  source='s2', line_number=1, column_number=1, offset=0),
            String('\n', source='s2', line_number=1, column_number=2, offset=1),
            String('b',  source='s2', line_number=2, column_number=1, offset=2),
            String('\r', source='s2', line_number=2, column_number=2, offset=3),
            String('\n', source='s2', line_number=2, column_number=3, offset=4),
            String('c',  source='s2', line_number=3, column_number=1, offset=5),
            String('\r', source='s2', line_number=3, column_number=2, offset=6),
            ]
        for a, b in zip_longest(l, expected):
            self.assertString(a, b)


    def test___le__(self):
        self.assertLessEqual(l, str(l))
        self.assertLessEqual(l, str(l) + 'x')
        self.assertLessEqual(str(l), l + 'x')

    def test___len__(self):
        for value in values:
            self.assertInt(len(value), len(str(value)))

    def test___lt__(self):
        self.assertLess(l, str(l) + 'x')
        self.assertLess(str(l), l + 'x')

    def test___mod__(self):
        # wow!  crack a window, will ya?
        f = String('%s %d %f', source=source)
        got = f % (abcde, 33, 35.5)
        self.assertStr(got, 'abcde 33 35.500000')

    def test___mul__(self):
        for value in values:
            for i in range(6):
                self.assertStr(value * i, str(value) * i)

    def test___ne__(self):
        self.assertNotEqual(l, str(l) + 'x')
        self.assertNotEqual(l + 'x', str(l))
        self.assertNotEqual(l, 3)
        self.assertNotEqual(String('3', source='x'), 3)

    def test___new__(self):
        # don't need to test this
        pass

    def test___reduce__(self):
        # part of the pickling machinery, don't touch it!
        pass

    def test___reduce_ex__(self):
        # part of the pickling machinery, don't touch it!
        pass

    def test___repr__(self):
        for value in values:
            self.assertStr(repr(value)[:11], f"String({repr(str(value))}"[:11])
            self.assertTrue(f"line_number={value.line_number}, " in repr(value))
        long_source = String('x' * 90)
        s = String('abcde', source=long_source, line_number=2, column_number=3, first_line_number=2, first_column_number=3)
        self.assertEqual(repr(s), "String('abcde', source='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', line_number=2, column_number=3, first_line_number=2, first_column_number=3)")


    # def test___rmod__(self):
    #     # I don't know what rmod does.
    #     # I mean, I know it's right-side modulus.
    #     # but what object X and string S can you define
    #     # such that X % S gives you a value?!
    #     # it's *not* printf-style formatting.
    #     pass

    def test___rmul__(self):
        for value in values:
            for i in range(6):
                self.assertStr(i * value, i * str(value))

    def test___setattr__(self):
        with self.assertRaises(AttributeError):
            l.source = '329872389'
        with self.assertRaises(AttributeError):
            l.line_number = 329872389
        with self.assertRaises(AttributeError):
            l.column_number = 329872389
        with self.assertRaises(AttributeError):
            l.first_column_number = 329872389

    def test___sizeof__(self):
        value = sys.getsizeof(String(''))
        self.assertIsInstance(value, int)
        # the size varies from one Python version to the next
        self.assertGreaterEqual(value, 40)

    def test___str__(self):
        self.assertString(abcde, 'abcde')

    def test___subclasshook__(self):
        # don't need to test this (I hope)
        pass

    def test_capitalize(self):
        for value in values:
            self.assertStr(value.capitalize(), str(value).capitalize())

    def test_casefold(self):
        for value in values:
            self.assertStr(value.casefold(), str(value).casefold())

    def test_center(self):
        for value in values:
            self.assertStr(value.center(30), str(value).center(30))
            self.assertStr(value.center(30, 'Z'), str(value).center(30, 'Z'))

    def test_count(self):
        for value in values:
            self.assertInt(value.count('e'), str(value).count('e'))

    def test_encode(self):
        for value in values:
            self.assertBytes(value.encode('utf-8'),     str(value).encode('utf-8'))
            self.assertBytes(value.encode('ascii'),     str(value).encode('ascii'))
            self.assertBytes(value.encode('utf-16'),    str(value).encode('utf-16'))
            self.assertBytes(value.encode('utf-16-be'), str(value).encode('utf-16-be'))
            self.assertBytes(value.encode('utf-16-le'), str(value).encode('utf-16-le'))
            self.assertBytes(value.encode('utf-32'),    str(value).encode('utf-32'))
            self.assertBytes(value.encode('utf-32-be'), str(value).encode('utf-32-be'))
            self.assertBytes(value.encode('utf-32-le'), str(value).encode('utf-32-le'))

    def test_endswith(self):
        for value in values:
            self.assertBool(value.endswith('f'), str(value).endswith('f'))
            self.assertBool(value.endswith('.'), str(value).endswith('.'))

    def test_expandtabs(self):
        for value in values:
            tester = self.assertStr if '\t' in value else self.assertString
            tester(value.expandtabs(), str(value).expandtabs())

    def test_find(self):
        # see test___contains__
        pass

    def test_format(self):
        # see test___format__
        pass

    def test_format_map(self):
        # see test___format__
        pass

    def test_index(self):
        # see test___contains__
        pass

    def test_isalnum(self):
        # smoke test for 3.6
        self.assertTrue(abcde.isascii())
        self.assertTrue(abcde._isascii())
        self.assertFalse(chipmunk.isascii())
        self.assertFalse(chipmunk._isascii())

        testers = "isalnum isalpha isascii isdecimal isdigit isidentifier islower isnumeric isprintable isspace istitle isupper".split()
        for value in values:
            for i in range(len(value)):
                prefix = value[:i]
                for tester in testers:
                    if hasattr(str, tester):
                        self.assertInt(getattr(prefix, tester)(), getattr(str(prefix), tester)())
        for tester in testers:
            # if not hasattr(str, tester):
            #     continue
            fn = self.assertTrue if tester == 'isprintable' else self.assertFalse
            fn(getattr(chipmunk, tester)())

    def test_isalpha(self):
        # see test_isalnum
        pass

    def test_isascii(self):
        # see test_isalnum
        pass

    def test_isdecimal(self):
        # see test_isalnum
        pass

    def test_isdigit(self):
        # see test_isalnum
        pass

    def test_isidentifier(self):
        # see test_isalnum
        pass

    def test_islower(self):
        # see test_isalnum
        pass

    def test_isnumeric(self):
        # see test_isalnum
        pass

    def test_isprintable(self):
        # see test_isalnum
        pass

    def test_isspace(self):
        # see test_isalnum
        pass

    def test_istitle(self):
        # see test_isalnum
        pass

    def test_isupper(self):
        # see test_isalnum
        pass

    def test_join(self):
        empty = abcde[0:0]
        result = empty.join(list(abcde))
        self.assertString(result, abcde)

        a = abcde[0]
        result = a.join(list(abcde))
        self.assertStr(result, 'aabacadae')

    def test_ljust(self):
        got = abcde.ljust(10)
        self.assertStr(got, 'abcde     ')
        got = abcde.ljust(10, 'x')
        self.assertStr(got, 'abcdexxxxx')

        # if the String doesn't change, return the String
        got = abcde.ljust(5)
        self.assertString(got, abcde)
        got = abcde.ljust(5, 'x')
        self.assertString(got, abcde)


    def test_lower(self):
        for method in "lower upper title".split():
            for value in values:
                s = str(value)
                s_mutated = getattr(s, method)()
                value_mutated = getattr(value, method)()
                if s == s_mutated:
                    self.assertIs(value_mutated, value)
                else:
                    self.assertStr(value_mutated, s_mutated)


    def test_lstrip(self):
        # see test_strip
        pass

    def test_maketrans(self):
        map = {'a': 'x', 'b': 'y', 'c': 'z', 'd': '1', 'e': '2'}
        for value in values:
            s = str(value)
            table = value.maketrans(map)
            self.assertEqual(table, s.maketrans(map))
            self.assertStr(value.translate(table), s.translate(table))

    def test_partition(self):
        for value in values:
            # get rid of repeated values
            chars = []
            for c in value:
                if c in chars:
                    continue
                chars.append(c)
            value = String("".join(chars), source="PQ")

            for i, middle in enumerate(value):
                before = value[:i]
                after  = value[i+len(middle):]
                for result in (
                    value.partition(middle),
                    value.rpartition(middle),
                    ):
                    self.assertEqual(result, (before, middle, after))
                    b, m, a = result
                    for which, got, expected in (
                        ('before', b, before),
                        ('middle', m, middle),
                        ('after',  a, after),
                        ):
                        self.assertEqual(got.source,              expected.source,              f'failed on value={value!r} {which}: got={got!r} expected={expected!r}')
                        self.assertEqual(got.line_number,         expected.line_number,         f'failed on value={value!r} {which}: got={got!r} expected={expected!r}')
                        self.assertEqual(got.column_number,       expected.column_number,       f'failed on value={value!r} {which}: got={got!r} expected={expected!r}')
                        self.assertEqual(got.first_column_number, expected.first_column_number, f'failed on value={value!r} {which}: got={got!r} expected={expected!r}')

            before, s, after = value.partition('🐛') # generic bug!
            self.assertString(before, value)
            self.assertFalse(s)
            self.assertFalse(after)

            before, s, after = value.rpartition('🪳') # cockroach!
            self.assertFalse(before)
            self.assertFalse(s)
            self.assertString(after, value)

        # test overlapping
        l = String('a . . b . . c . . d . . e', source='smith')
        sep = ' . '

        partitions = l.partition(sep)
        self.assertEqual(partitions,
            (
            l[:1],
            l[1:4],
            l[4:],
            )
            )
        self.assertEqual(partitions[0] + partitions[1] + partitions[2], l)
        self.assertEqual(String.cat(*partitions), l)

        self.assertEqual(l.rpartition(sep),
            (
            l[:21],
            l[21:24],
            l[24:]
            )
            )
        self.assertEqual(partitions[0] + partitions[1] + partitions[2], l)
        self.assertEqual(String.cat(*partitions), l)

        # test Eric Smith's extension

        self.assertEqual(l.partition(sep, 0), (l,))
        self.assertIs(l.partition(sep, 0)[0], l)
        self.assertEqual(l.rpartition(sep, 0), (l,))
        self.assertIs(l.rpartition(sep, 0)[0], l)

        partitions = l.partition(sep, 2)
        self.assertEqual(partitions,
            (
            l[0:1],   # 'a'
            l[1:4],   # sep     - split 1
            l[4:7],   # '. b'
            l[7:10],  # sep     - split 2
            l[10:],   # ... and the rest
            )
            )

        partitions = l.rpartition(sep, 2)
        self.assertEqual(partitions,
            (
            l[:15],   # 'a . b . c'
            l[15:18], # sep     - split 2
            l[18:21], # '. d'
            l[21:24], # sep     - split 1
            l[24:25], # '. e'
            )
            )

        partitions = l.partition(sep, 6)
        self.assertEqual(partitions,
            (
            l[0:1],   # 'a'
            l[1:4],   # sep     - split 1
            l[4:7],   # '. b'
            l[7:10],  # sep     - split 2
            l[10:13], # '. c'
            l[13:16], # sep     - split 3
            l[16:19], # '. d'
            l[19:22], # sep     - split 4
            l[22:25], # '. e'
            l[25:25], # empty!  - split 5
            l[25:25], # empty!
            l[25:25], # empty!  - split 6
            l[25:25], # empty!
            )
            )
        self.assertEqual(String.cat(*partitions), l)

        partitions = l.rpartition(sep, 6)
        self.assertEqual(partitions,
            (
            l[0:0],   # empty!
            l[0:0],   # empty!  - split 6
            l[0:0],   # empty!
            l[0:0],   # empty!  - split 5
            l[0:3],   # 'a'
            l[3:6],   # sep     - split 4
            l[6:9],   # '. b'
            l[9:12],  # sep     - split 3
            l[12:15], # '. c'
            l[15:18], # sep     - split 2
            l[18:21], # '. d'
            l[21:24], # sep     - split 1
            l[24:25], # '. e'
            )
            )
        self.assertEqual(String.cat(*partitions), l)



    def test_removeprefix(self):
        # smoke test for 3.6
        self.assertString(abcde.removeprefix('ab'), abcde[2:])
        self.assertString(abcde.removeprefix('xx'), abcde)

        # don't bother with the test for 3.6-3.8
        if not hasattr('', 'removeprefix'):  # pragma: no cover
            return

        for value in values:
            for i in range(len(value)):
                prefix = value[:i]
                self.assertString(value.removeprefix(prefix), str(value).removeprefix(prefix))
                suffix = value[i:]
                self.assertString(value.removesuffix(suffix), str(value).removesuffix(suffix))
            self.assertIs(value.removeprefix(chipmunk), value)
            self.assertIs(value.removesuffix(chipmunk), value)

    def test_removesuffix(self):
        # see test_removeprefix
        pass

    def test_replace(self):
        for value in values:
            for src in "abcde":
                result = value.replace(src, str(chipmunk))
                if src in value:
                    self.assertStr(result, str(value).replace(src, chipmunk))
                else:
                    self.assertIs(result, value)

    def test_rfind(self):
        # see test___contains__
        pass

    def test_rindex(self):
        # see test___contains__
        pass

    def test_rjust(self):
        self.assertEqual(himem.rstrip().rjust(8), "    QEMM")
        self.assertString(himem.rstrip().rjust(4), "QEMM")

    def test_rpartition(self):
        # see test_partitino
        pass

    def test_rsplit(self):
        # see split
        pass

    def test_rstrip(self):
        # see test_strip
        pass

    def test_split(self):
        for s, sep, result in (
            ("ab cd ef",                None, [('ab', 0, 1, 1), ('cd', 3, 1, 4), ('ef', 6, 1, 7)]),
            ("ab\ncd\nef",              None, [('ab', 0, 1, 1), ('cd', 3, 2, 1), ('ef', 6, 3, 1)]),
            (" ab  \n  cd \n \n    ef", None, [('ab', 1, 1, 2), ('cd', 8, 2, 3), ('ef', 18, 4, 5)]),
            (" ab x \n x cd\n xx x \n\n \n xef", 'x',
                [
                (' ab ',       0, 1, 1),
                (' \n ',       5, 1, 6),
                (' cd\n ',     9, 2, 3),
                ('',          15, 3, 3),
                (' ',         16, 3, 4),
                (' \n\n \n ', 18, 3, 6),
                ('ef',        25, 6, 3),
                ]),
            ('XooXoooXoooXoooXoo', 'Xooo', [('Xoo', 0, 1, 1), ('', 7, 1, 8), ('', 11, 1, 12), ('Xoo', 15, 1, 16)]),
            ):
            source = 'toe'
            l2 = String(s, source=source)
            list_split = list(l2.split(sep))
            list_rsplit = list(l2.rsplit(sep))
            for line, rline, r in zip_longest(list_split, list_rsplit, result):
                s2, offset, line_number, column_number = r
                self.assertEqual(line, s2, f"{line!r} != {r}")
                self.assertEqual(rline, s2, f"{rline!r} != {r}")
                self.assertEqual(line.offset, offset, f"{line!r} != {r}")
                self.assertEqual(rline.offset, offset, f"{rline!r} != {r}")
                self.assertEqual(line.line_number, line_number, f"{line!r} != {r}")
                self.assertEqual(rline.line_number, line_number, f"{rline!r} != {r}")
                self.assertEqual(line.column_number, column_number, f"{line!r} != {r}")
                self.assertEqual(rline.column_number, column_number, f"{rline!r} != {r}")

            axxb = String("a x x b")
            list_split = axxb.split(' x ')
            self.assertString(list_split[0], 'a')
            self.assertString(list_split[1], 'x b')
            list_rsplit = axxb.rsplit(' x ')
            self.assertString(list_rsplit[0], 'a x')
            self.assertString(list_rsplit[1], 'b')


    def test_splitlines(self):
        # splitlines_demo = String(' a \n b \r c \r\n d \n\r e ', source='Z')
        self.assertEqual(list(splitlines_demo.splitlines()), [' a ', ' b ', ' c ', ' d ', '', ' e '])
        self.assertEqual(list(splitlines_demo.splitlines(True)), [' a \n', ' b \r', ' c \r\n', ' d \n', '\r', ' e '])

        assert splitlines_demo in values

        for value in values:
            with self.subTest(repr(value)):
                splitted = value.splitlines(True)
                reconstituted = String.cat(*splitted)
                self.assertString(reconstituted, value)

    def test_startswith(self):
        pass

    def test_strip(self):
        methods = ("strip", "lstrip", "rstrip")
        for value in values:
            s = str(value)
            for method in methods:
                s_mutated = getattr(s, method)()
                value_mutated = getattr(value, method)()
                if s_mutated == s:
                    self.assertIs(value_mutated, value)
                else:
                    # print(f"{value=!r} {method} -> {value_mutated=!r}")
                    self.assertString(value_mutated, s_mutated)

    def test_swapcase(self):
        for value in values:
            self.assertStr(value.swapcase(), str(value).swapcase())

    def test_title(self):
        # see test_lower
        pass

    def test_translate(self):
        # see test_maketrans
        pass

    def test_upper(self):
        # see test_lower
        pass

    def test_zfill(self):
        self.assertEqual(himem.zfill(8), "000QEMM\n")
        self.assertString(himem.zfill(5), "QEMM\n")

    #######
    ## our additions
    #######

    def test_tab_width(self):

        s = String('ab\tcde\tfg')
        for (i, c), expected in zip_longest(enumerate(s), [1, 2, 3, 9, 10, 11, 12, 17, 18]):
            c2 = s[i]
            self.assertEqual(c.column_number, expected)
            self.assertEqual(c2.column_number, expected)

        s = String('ab\tcde\tfg', tab_width=4)
        for (i, c), expected in zip_longest(enumerate(s), [1, 2, 3, 5, 6, 7, 8, 9, 10]):
            c2 = s[i]
            self.assertEqual(c.column_number, expected)
            self.assertEqual(c2.column_number, expected)

    def test_bisect(self):
        for i in range(1, len(alphabet) - 1):
            a, b = alphabet.bisect(i)
            self.assertIsInstance(a, String)
            self.assertIsInstance(b, String)
            self.assertEqual(len(a), i)
            self.assertTrue(alphabet.startswith(a))
            self.assertEqual(a + b, alphabet)

    def test_is_followed_by(self):
        a = abcde[0]
        b = abcde[1]
        c = abcde[2]

        self.assertTrue(a.is_followed_by(b))
        self.assertFalse(a.is_followed_by('b'))
        self.assertFalse(a.is_followed_by(c))
        self.assertFalse(b.is_followed_by(a))

        xbcde = String('xbcde')
        fake_b = xbcde[1]
        self.assertFalse(a.is_followed_by(fake_b))

    def test_cat(self):
        self.assertStr(String.cat(), '')
        self.assertString(String.cat(abcde), abcde)
        self.assertString(String.cat(abcde, 'xyz'), 'abcdexyz')
        self.assertString(String.cat(abcde[:2], abcde[2:]), abcde)
        self.assertString(String.cat(abcde[:2], abcde[:2]), 'abab')

        xyz = String.cat('xyz', metadata=abcde)
        self.assertString(xyz, 'xyz')
        self.assertEqual(xyz.source, abcde.source)
        self.assertEqual(xyz.line_number, abcde.line_number)
        self.assertEqual(xyz.column_number, abcde.column_number)

        xyz = String.cat('xyz', metadata=abcde, line_number=77, column_number=88)
        self.assertString(xyz, 'xyz')
        self.assertEqual(xyz.source, abcde.source)
        self.assertEqual(xyz.line_number, 77)
        self.assertEqual(xyz.column_number, 88)

        with self.assertRaises(ValueError):
            String.cat('xyz', 'zooo')

        with self.assertRaises(TypeError):
            String.cat('xyz', metadata=3.5)

        with self.assertRaises(TypeError):
            String.cat('xyz', metadata=xyz, line_number=33.5)
        with self.assertRaises(ValueError):
            String.cat('xyz', metadata=xyz, line_number=-20)

        with self.assertRaises(TypeError):
            String.cat('xyz', metadata=xyz, column_number=33.5)
        with self.assertRaises(ValueError):
            String.cat('xyz', metadata=xyz, column_number=-20)


    def test_linebreak_offsets_generation(self):
        # a String can generate and cache linebreak offsets two different ways:
        #     * iterating over a String
        #     * calling split or partition, which call __compute_linebreak_offsets
        for value in values:
            s = str(value)

            l_iter = String(s, source="z")
            self.assertEqual(l_iter._linebreak_offsets, None)
            [c for c in l_iter]
            self.assertNotEqual(l_iter._linebreak_offsets, None)


            l_compute = String(s, source="z")
            self.assertEqual(l_compute._linebreak_offsets, None)
            l_compute._compute_linebreak_offsets()
            self.assertNotEqual(l_compute._linebreak_offsets, None)

            if 0:
                print("l_iter")
                l_iter.print_linebreak_offsets()
                print("")
                print("l_compute")
                l_compute.print_linebreak_offsets()
                print()

            self.assertEqual(l_iter._linebreak_offsets, l_compute._linebreak_offsets, f"{s!r}")

    def test_line_etc(self):
        s = String("a b c\nd e f\ng h i\nj k l\nm n o")

        h = s[14]

        self.assertString(h.line, s[12:18])
        self.assertString(h.line.line, h.line)
        self.assertString(h.line.line.line, h.line)
        self.assertString(h.previous_line, s[6:12])
        self.assertString(h.previous_line.previous_line, s[0:6])
        self.assertString(h.next_line, s[18:24])
        self.assertString(h.next_line.next_line, s[24:])

        with self.assertRaises(ValueError):
            print(repr(h.previous_line.previous_line.previous_line))
        with self.assertRaises(ValueError):
            print(repr(h.next_line.next_line.next_line))

        # if s is a String, and x = s[i:j], and there are linebreaks in x,
        # x.line extends from the beginning of the first line in x
        # to the linebreak that ends the last line in x.
        hijk = s[14:21] # "h i\nj k"
        self.assertString(hijk.line, s[12:24]) # "g h i\nj k l\n"
        self.assertString(hijk.previous_line, s[6:12]) # previous to the first line in hijk, "d e f\n"
        self.assertString(hijk.next_line, s[24:]) # next after the last line in hijk, "m n o"

        almost_everything = s[1:-1]
        self.assertString(almost_everything.line, s)

        # regression! if we have a zero-length slice of a String named x,
        # x.line used to crash.
        s_end = s[len(s):]
        self.assertEqual(s_end.line, "m n o")


    def test_generate_tokens(self):
        lines = [
        "import big\n",
        "print(big)\n",
        "'''abc\n",
        "def\n",
        "ghi'''\n",
        ''
        ]
        text = String("".join(lines))

        lines_2_3_4 = lines[2] + lines[3] + lines[4]
        s = lines_2_3_4.rstrip()

        expected = [
            (TOKEN_NAME,      'import', (1, 0),  (1, 6),  lines[0]),
            (TOKEN_NAME,      'big',    (1, 7),  (1, 10), lines[0]),
            (TOKEN_NEWLINE,   '\n',     (1, 10), (1, 11), lines[0]),
            (TOKEN_NAME,      'print',  (2, 0),  (2, 5),  lines[1]),
            (TOKEN_OP,        '(',      (2, 5),  (2, 6),  lines[1]),
            (TOKEN_NAME,      'big',    (2, 6),  (2, 9),  lines[1]),
            (TOKEN_OP,        ')',      (2, 9),  (2, 10), lines[1]),
            (TOKEN_NEWLINE,   '\n',     (2, 10), (2, 11), lines[1]),
            (TOKEN_STRING,    s,        (3, 0),  (5, 6),  lines_2_3_4),
            (TOKEN_NEWLINE,   '\n',     (5, 6),  (5, 7),  lines[4]),
            (TOKEN_ENDMARKER, '',       (6, 0),  (6, 0),  lines[5]),
            ]

        got = list(text.generate_tokens())
        self.assertEqual(expected, got)

    def test_multipassthroughs(self):
        l = list(tabs.multisplit('\t'))
        l2 = list(tabs.split('\t'))
        self.assertEqual(l, l2)

        before, c, after = abcde.multipartition('c')
        self.assertString(before, 'ab')
        self.assertString(c, 'c')
        self.assertString(after, 'de')

    def test_compile(self):
        p = String(":+").compile()
        s = String('a:b::c::d:')
        l = p.split(s)
        self.assertEqual(l,
            [
            s[0],
            s[2],
            s[5],
            s[8],
            s[10:10],
            ])


def run_tests():
    bigtestlib.run(name="big.types", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
