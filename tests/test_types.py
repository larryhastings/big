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
big_dir = bigtestlib.preload_local_big()

import collections
import copy
import itertools
from itertools import zip_longest
import pickle
from string import ascii_letters, punctuation, whitespace
import sys
from threading import Lock
import unittest

import big.all as big
from big.types import string, Pattern
from big.types import linked_list, SpecialNodeError, UndefinedIndexError
from big.types import linked_list_base_iterator, linked_list_iterator, linked_list_reverse_iterator
from big.tokens import *
from big.version import Version

python_version = Version(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

source = '"C:\\AUTOEXEC.BAT"'
source2 = '"C:\\HIMEM.SYS"'
first_line_number = 1
first_column_number = 1

alphabet = string('abcdefghijklmnopqrstuvwxyz', source=source)
abcde = alphabet[:5]
fghij = alphabet[5:10]
himem = string('QEMM\n', source=source2)
line1 = string('line 1!\n', source=source)
line2 = string('line 2.\n', source=source, line_number=2)
words = string('this is a series of words.', source=source)
tabs  = string('this\tis\ta\tseries\tof\twords\twith\ttabs', source=source)
leading_and_trailing  = string('            a b c                  ', source=source)
leading_only  = string('            a b c', source=source)
trailing_only  = string('a b c            ', source=source)
all_uppercase  = string("HELLO WORLD!", source=source)
title_case  = string("Hello World!", source=source)
kooky1 = string("kooky land 1", line_number=44)
kooky2 = string("kooky land 2",                 column_number=33, first_column_number=33)
kooky3 = string("kooky land 3", line_number=44, column_number=33, first_column_number=33)

splitlines_demo = string(' a \n b \r c \r\n d \n\r e ', source='Z')

l2 = string("ab\ncd\nef", source='xz')


chipmunk = string('🐿️', source='tic e tac')

numbers_only = string('12345', source='letterman')

l = abcde

values = {
    "abcde" : abcde,
    "himem" : himem,
    "line1" : line1,
    "line2" : line2,
    "tabs" : tabs,
    "words" : words,
    "splitlines_demo" : splitlines_demo,
    "leading_and_trailing" : leading_and_trailing,
    "leading_only" : leading_only,
    "trailing_only" : trailing_only,
    "all_uppercase" : all_uppercase,
    "title_case" : title_case,
    "kooky1" : kooky1,
    "kooky2" : kooky2,
    "kooky3" : kooky3,
    'numbers_only': numbers_only,
    }


class BigStringTests(unittest.TestCase):

    maxDiff = None

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
        self.assertIsInstance(got, string)
        self.assertEqual(got, expected)

    def assertStr(self, got, expected):
        self.assertIsInstance(got, str)
        self.assertNotIsInstance(got, string)
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
        self.assertString(string('abc'), 'abc')

        self.assertEqual(string(abcde), abcde)

        ar = self.assertRaises

        with ar(TypeError):
            string(54321)
        with ar(TypeError):
            string(33.4)
        with ar(TypeError):
            string(['x', 'y'])

        self.assertString(string('abc', source=None), 'abc')
        self.assertString(string('abc', source='xyz'), 'abc')
        s = string('abc')
        self.assertString(string('abc', source=None), 'abc')
        self.assertString(string('abc', source='xyz'), 'abc')

        with ar(TypeError):
            string('abc', source=33.5)
        with ar(TypeError):
            string('abc', source=-2)
        with ar(TypeError):
            string('abc', source=['x'])

        with ar(TypeError):
            string('abc', line_number=33.5)
        with ar(ValueError):
            string('abc', line_number=-2)

        with ar(TypeError):
            string('abc', column_number=33.5)
        with ar(ValueError):
            string('abc', column_number=-2)
        with ar(ValueError):
            string('abc', column_number=2, first_column_number=3)

        with ar(TypeError):
            string('abc', first_column_number=33.5)
        with ar(ValueError):
            string('abc', first_column_number=-2)

        with ar(TypeError):
            string('abc', tab_width=33.5)
        with ar(ValueError):
            string('abc', tab_width=-2)
        with ar(ValueError):
            string('abc', tab_width=0)


    def test_attributes(self):
        s_origin = "abcde"
        s = string(s_origin, source='"source"', line_number=3, column_number=4, first_column_number=2, tab_width=4)
        self.assertString(s, "abcde")
        self.assertStr(s.source, '"source"')
        self.assertInt(s.line_number, 3)
        self.assertInt(s.column_number, 4)
        self.assertInt(s.first_column_number, 2)
        self.assertInt(s.tab_width, 4)
        self.assertIs(s.origin, s)
        self.assertStr(s.where, '"source" line 3 column 4')

        s = string(s_origin, line_number=3, column_number=4, first_column_number=2, tab_width=4)
        self.assertString(s, "abcde")
        self.assertEqual(s.source, None)
        self.assertInt(s.line_number, 3)
        self.assertInt(s.column_number, 4)
        self.assertInt(s.first_column_number, 2)
        self.assertInt(s.tab_width, 4)
        self.assertIs(s.origin, s)
        self.assertStr(s.where, 'line 3 column 4')

        slice = s[1:-1]
        self.assertString(slice, "bcd")
        self.assertString(slice.origin, s)

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

        # whitebox testing: _append_ranges joins contiguous ranges, and rhs has >1 subsequent ranges
        s = fghij + abcde + himem
        result = abcde + s
        self.assertString(result, 'abcdefghijabcdeQEMM\n')

        # whitebox testing: radd on an empty string just returns the lhs, but *as a string*
        s = string()
        t = 'abcd' + s
        self.assertString(t, 'abcd')


    def test___radd__(self):
        with self.assertRaises(TypeError):
            x = 1 + abcde

        s_line_number = 55
        s_column_number = 22
        s_source = 'marianas trench'
        s = string("abcde", line_number=s_line_number, column_number=s_column_number, source=s_source)

        # if it works out like magic, you can get a string out
        # but the line and column numbers have to work.
        str_x = "wxyz" + str(s)
        x = "wxyz" + s
        self.assertIsInstance(x, string)
        self.assertEqual(x, str_x)
        self.assertEqual(x.line_number, 1)
        self.assertEqual(x.column_number, 1)
        self.assertEqual(x.source, None)
        self.assertEqual(x[4].line_number, s_line_number)
        self.assertEqual(x[4].column_number, s_column_number)
        self.assertEqual(x[4].source, s_source)

        str_x = "123\nwxyz" + str(s)
        x = "123\nwxyz" + s
        self.assertIsInstance(x, string)
        self.assertEqual(x, str_x)
        self.assertEqual(x.line_number, 1)
        self.assertEqual(x.column_number, 1)
        self.assertEqual(x.source, None)
        self.assertEqual(x[4].line_number, 2)
        self.assertEqual(x[4].column_number, 1)
        self.assertEqual(x[9].line_number, s_line_number)
        self.assertEqual(x[8].column_number, s_column_number)
        self.assertEqual(x[8].source, s_source)


    def test___class__(self):
        self.assertEqual(l.__class__, string)

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

        letters = set(ascii_letters) | set(punctuation) | set(whitespace)
        for value_name, value in values.items():
            in_value = set(str(value))
            not_in_value = letters - in_value
            for letter in in_value:
                with self.subTest(value=value_name, letter=letter):
                    self.assertTrue(letter in value)
                    self.assertGreaterEqual(value.find(letter), 0)
                    self.assertGreaterEqual(value.rfind(letter), 0)
                    self.assertGreaterEqual(value.index(letter), 0)
                    self.assertGreaterEqual(value.rindex(letter), 0)
            for letter in not_in_value:
                with self.subTest(value=value_name, letter=letter):
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
        str_dir = list(dir(''))
        str_dir.extend(
            (
            '__module__',
            '__radd__',
            '__reversed__',
            '__slots__',
            '_append_ranges',
            '_cat',
            '_clamp_index',
            '_column_number',
            '_compute_line_and_column',
            '_isascii',
            '_length',
            '_line_number',
            '_offset',
            '_origin',
            '_partition',
            '_ranges',
            '_source',
            '_split',
            'bisect',
            'cat',
            'column_number',
            'compile',
            'first_column_number',
            'generate_tokens',
            'line_number',
            'multipartition',
            'multisplit',
            'offset',
            'origin',
            'source',
            'tab_width',
            'where',
            )
        )

        if python_version < Version("3.7"): # pragma: nocover
            str_dir.append('isascii')
        if python_version < Version("3.9"): # pragma: nocover
            str_dir.append('removeprefix')
            str_dir.append('removesuffix')
        if python_version >= Version("3.13"): # pragma: nocover
            str_dir.append('__firstlineno__')
            str_dir.append('__static_attributes__')

        str_dir.sort()

        string_dir = dir(abcde)
        string_dir.sort()
        self.assertEqual(str_dir, string_dir)

    def test___doc__(self):
        self.assertIsInstance(l.__doc__, str)
        self.assertTrue(l.__doc__)

    def test___eq__(self):
        self.assertEqual(l, str(l))
        self.assertEqual(l + 'x', str(l) + 'x')

    def test___format__(self):
        f = string('{abcde} {line1} {line2}', source=source)
        got = f.format(abcde=abcde, line1=line1, line2=line2)
        self.assertStr(got, 'abcde line 1!\n line 2.\n')
        got = f.format_map({'abcde': abcde, 'line1': line1, 'line2': line2})
        self.assertStr(got, 'abcde line 1!\n line 2.\n')

        # if the string is unchanged, return the string!
        f = string("{abcde}", source=source)
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
            self.assertString(abcde[i], string(s[i], source=source, column_number=first_column_number + (i % length)))

        self.assertString(abcde[1:4], string('bcd', source=source, column_number=first_column_number + 1))

        self.assertString(abcde[1:-1:2], 'bd')

        # regression!
        last_zero = abcde[len(abcde):len(abcde)]
        self.assertEqual(last_zero.line_number, 1)
        self.assertEqual(last_zero.column_number, abcde.first_column_number + len(abcde))

        # index must be slice or int
        with self.assertRaises(TypeError):
            abcde[33.55]

        # *indexing* out of range raises IndexError.
        with self.assertRaises(IndexError):
            abcde[-20]
        with self.assertRaises(IndexError):
            abcde[33]

        # *slicing* out of range clamps to allowed range.
        self.assertString(abcde[-20:], abcde)
        self.assertString(abcde[448:], '')
        self.assertString(abcde[:10_000], abcde)
        self.assertString(abcde[:-8724], '')
        self.assertString(abcde[1:-50], '')

        with self.assertRaises(TypeError):
            abcde[1.5:]
        with self.assertRaises(TypeError):
            abcde[:1.5]
        with self.assertRaises(TypeError):
            abcde[::1.5]
        with self.assertRaises(ValueError):
            abcde[::0]

        # regression: if the string ended with a linebreak,
        # getting the zero-length string after that linebreak
        # would increment the line number
        s = string("x\n")
        endo = s[len(s):len(s)]
        self.assertEqual(endo.line_number, 2)
        self.assertEqual(endo[0:0].line_number, 2) # used to be 3!
        self.assertEqual(endo[0:0][0:0].line_number, 2) # used to be 4!
        self.assertEqual(endo[0:0][0:0][0:0].line_number, 2) # used to be 5!

    def test___getnewargs__(self):
        # string implements __getnewargs__, it's pickling machinery.
        for value_name, value in values.items():
            with self.subTest(value=value_name):
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
        for value_name, value in values.items():
            with self.subTest(value=value_name):
                s = str(value)
                self.assertEqual(hash(value), hash(s))

    def test___init__(self):
        # don't need to test this special
        pass

    def test___init_subclass__(self):
        # oh golly, idk.  don't subclass string, mkay?
        pass

    def test___iter__(self):
        for value_name, value in values.items():
            s = str(value)
            for i, (a, b) in enumerate(zip_longest(value, s)):
                with self.subTest(value=value_name, i=i, a=a, b=b):
                    self.assertEqual(a, b, f'failed on value={value!r} i={i!r} a={a!r} != b={b!r}')
                    self.assertStr(b, s[i])
                    self.assertString(a, value[i])

        # and now, a cool string feature
        l = string('a\nb\ncde\nf', source='s1')
        expected = [
            string('a',  source='s1', line_number=1, column_number=1),
            string('\n', source='s1', line_number=1, column_number=2),
            string('b',  source='s1', line_number=2, column_number=1),
            string('\n', source='s1', line_number=2, column_number=2),
            string('c',  source='s1', line_number=3, column_number=1),
            string('d',  source='s1', line_number=3, column_number=2),
            string('e',  source='s1', line_number=3, column_number=3),
            string('\n', source='s1', line_number=3, column_number=4),
            string('f',  source='s1', line_number=4, column_number=1),
            ]
        for a, b in zip_longest(l, expected):
            self.assertString(a, b)

        l = string('a\nb\ncde\nf', source='s2', line_number=10, column_number=2, first_column_number=2)
        expected = [
            string('a',  source='s2', line_number=10, column_number=2),
            string('\n', source='s2', line_number=10, column_number=3),
            string('b',  source='s2', line_number=11, column_number=2),
            string('\n', source='s2', line_number=11, column_number=3),
            string('c',  source='s2', line_number=12, column_number=2),
            string('d',  source='s2', line_number=12, column_number=3),
            string('e',  source='s2', line_number=12, column_number=4),
            string('\n', source='s2', line_number=12, column_number=5),
            string('f',  source='s2', line_number=13, column_number=2),
            ]
        for a, b in zip_longest(l, expected):
            self.assertString(a, b)

        # test tab
        l = string('ab\tc', source='s2')
        expected = [
            string('a',  source='s2', line_number=1, column_number=1),
            string('b',  source='s2', line_number=1, column_number=2),
            string('\t', source='s2', line_number=1, column_number=3),
            string('c',  source='s2', line_number=1, column_number=9),
            ]
        for a, b in zip_longest(l, expected):
            self.assertString(a, b)

        # also test tab immediately after \r, because, reasons.
        l = string('ab\r\tc', source='s2')
        expected = [
            string('a',  source='s2', line_number=1, column_number=1),
            string('b',  source='s2', line_number=1, column_number=2),
            string('\r', source='s2', line_number=1, column_number=3),
            string('\t', source='s2', line_number=2, column_number=1),
            string('c',  source='s2', line_number=2, column_number=9),
            ]
        for a, b in zip_longest(l, expected):
            self.assertString(a, b)

        # regression: at one point there was a bug, if the string ends with \r,
        # it wouldn't get yielded.  __next__ buffers \r in case it's followed
        # by \n, in which case we only break the line after the \n.
        l = string('a\nb\r\nc\r', source='s2')
        expected = [
            string('a',  source='s2', line_number=1, column_number=1),
            string('\n', source='s2', line_number=1, column_number=2),
            string('b',  source='s2', line_number=2, column_number=1),
            string('\r', source='s2', line_number=2, column_number=2),
            string('\n', source='s2', line_number=2, column_number=3),
            string('c',  source='s2', line_number=3, column_number=1),
            string('\r', source='s2', line_number=3, column_number=2),
            ]
        for a, b in zip_longest(l, expected):
            self.assertString(a, b)


    def test___le__(self):
        self.assertLessEqual(l, str(l))
        self.assertLessEqual(l, str(l) + 'x')
        self.assertLessEqual(str(l), l + 'x')

    def test___len__(self):
        for value_name, value in values.items():
            with self.subTest(value=value_name):
                self.assertInt(len(value), len(str(value)))

    def test___lt__(self):
        self.assertLess(l, str(l) + 'x')
        self.assertLess(str(l), l + 'x')

    def test___mod__(self):
        # wow!  crack a window, will ya?
        f = string('%s %d %f', source=source)
        got = f % (abcde, 33, 35.5)
        self.assertStr(got, 'abcde 33 35.500000')

    def test___mul__(self):
        for value_name, value in values.items():
            for i in range(6):
                with self.subTest(value=value_name, i=i):
                    self.assertStr(value * i, str(value) * i)

    def test___ne__(self):
        self.assertNotEqual(l, str(l) + 'x')
        self.assertNotEqual(l + 'x', str(l))
        self.assertNotEqual(l, 3)
        self.assertNotEqual(string('3', source='x'), 3)

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
        for value_name, value in values.items():
            with self.subTest(value=value_name):
                self.assertStr(repr(value), repr(str(value)))

    def test___rmul__(self):
        for value_name, value in values.items():
            for i in range(6):
                with self.subTest(value=value_name, i=i):
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
        value = sys.getsizeof(string(''))
        self.assertIsInstance(value, int)
        # the size varies from one Python version to the next
        self.assertGreaterEqual(value, 40)

    def test___str__(self):
        self.assertString(abcde, 'abcde')

    def test___subclasshook__(self):
        # don't need to test this (I hope)
        pass

    def test_capitalize(self):
        for value_name, value in values.items():
            with self.subTest(value=value_name):
                self.assertEqual(value.capitalize(), str(value).capitalize())

    def test_casefold(self):
        for value_name, value in values.items():
            with self.subTest(value=value_name):
                self.assertEqual(value.casefold(), str(value).casefold())

    def test_count(self):
        for value_name, value in values.items():
            with self.subTest(value=value_name):
                self.assertInt(value.count('e'), str(value).count('e'))

    def test_encode(self):
        for value_name, value in values.items():
            with self.subTest(value=value_name):
                self.assertBytes(value.encode('utf-8'),     str(value).encode('utf-8'))
                self.assertBytes(value.encode('ascii'),     str(value).encode('ascii'))
                self.assertBytes(value.encode('utf-16'),    str(value).encode('utf-16'))
                self.assertBytes(value.encode('utf-16-be'), str(value).encode('utf-16-be'))
                self.assertBytes(value.encode('utf-16-le'), str(value).encode('utf-16-le'))
                self.assertBytes(value.encode('utf-32'),    str(value).encode('utf-32'))
                self.assertBytes(value.encode('utf-32-be'), str(value).encode('utf-32-be'))
                self.assertBytes(value.encode('utf-32-le'), str(value).encode('utf-32-le'))

    def test_endswith(self):
        for value_name, value in values.items():
            with self.subTest(value=value_name):
                self.assertBool(value.endswith('f'), str(value).endswith('f'))
                self.assertBool(value.endswith('.'), str(value).endswith('.'))

    def test_expandtabs(self):
        for value_name, value in values.items():
            with self.subTest(value=value_name):
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
        for value_name, value in values.items():
            for i in range(len(value)):
                with self.subTest(value=value_name, i=i):
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
        self.assertString(result, 'aabacadae')

    def test_center(self):
        for value_name, value in values.items():
            with self.subTest(value=value_name):
                self.assertString(value.center(30), str(value).center(30))
                self.assertString(value.center(30, 'Z'), str(value).center(30, 'Z'))
                self.assertString(value.center(31), str(value).center(31))
                self.assertString(value.center(31, 'Z'), str(value).center(31, 'Z'))
                self.assertString(value.center(1), str(value).center(1))
                self.assertString(value.center(1, 'Z'), str(value).center(1, 'Z'))

        with self.assertRaises(TypeError):
            abcde.center(33, 352)
        with self.assertRaises(TypeError):
            abcde.center(33, 'xyz')
        with self.assertRaises(TypeError):
            abcde.center(5.5)
        with self.assertRaises(TypeError):
            abcde.center([3], 'x')


    def test_ljust(self):
        got = abcde.ljust(10)
        self.assertString(got, 'abcde     ')
        got = abcde.ljust(10, 'x')
        self.assertString(got, 'abcdexxxxx')

        # if the string doesn't change, return the string
        got = abcde.ljust(5)
        self.assertString(got, abcde)
        got = abcde.ljust(5, 'x')
        self.assertString(got, abcde)

        with self.assertRaises(TypeError):
            abcde.ljust(5, 352)
        with self.assertRaises(TypeError):
            abcde.ljust(5, 'xyz')
        with self.assertRaises(TypeError):
            abcde.ljust(5.5)
        with self.assertRaises(TypeError):
            abcde.ljust([3], 'x')


    def test_lower(self):
        for method in "lower upper title".split():
            for value_name, value in values.items():
                with self.subTest(value=value_name, method=method):
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
        for value_name, value in values.items():
            with self.subTest(value=value_name):
                s = str(value)
                table = value.maketrans(map)
                self.assertEqual(table, s.maketrans(map))
                self.assertStr(value.translate(table), s.translate(table))

    def test_partition(self):
        for value_name, value in values.items():
            # get rid of repeated values
            chars = []
            for c in value:
                if c in chars:
                    continue
                chars.append(c)
            value = string("".join(chars), source="PQ")

            for i, middle in enumerate(value):
                before = value[:i]
                after  = value[i+len(middle):]
                with self.subTest(value=value_name, i=i, middle=middle):
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
                            with self.subTest(which=which):
                                self.assertEqual(got.source,              expected.source,              f'failed on value={value!r} {which}: got={got!r} expected={expected!r}')
                                self.assertEqual(got.line_number,         expected.line_number,         f'failed on value={value!r} {which}: got={got!r} expected={expected!r}')
                                self.assertEqual(got.column_number,       expected.column_number,       f'failed on value={value!r} {which}: got={got!r} expected={expected!r}')
                                self.assertEqual(got.first_column_number, expected.first_column_number, f'failed on value={value!r} {which}: got={got!r} expected={expected!r}')

            with self.subTest(value=value_name):
                before, s, after = value.partition('🐛') # generic bug!
                self.assertString(before, value)
                self.assertFalse(s)
                self.assertFalse(after)

                before, s, after = value.rpartition('🪳') # cockroach!
                self.assertFalse(before)
                self.assertFalse(s)
                self.assertString(after, value)

        # test overlapping
        l = string('a . . b . . c . . d . . e', source='smith')
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
        self.assertEqual(string.cat(*partitions), l)

        self.assertEqual(l.rpartition(sep),
            (
            l[:21],
            l[21:24],
            l[24:]
            )
            )
        self.assertEqual(partitions[0] + partitions[1] + partitions[2], l)
        self.assertEqual(string.cat(*partitions), l)

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
        self.assertEqual(string.cat(*partitions), l)

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
        self.assertEqual(string.cat(*partitions), l)

        with self.assertRaises(TypeError):
            abcde.partition(33.5)
        with self.assertRaises(TypeError):
            abcde.partition('abc', 33.5)



    def test_removeprefix(self):
        # smoke test for 3.6-3.8
        self.assertString(abcde.removeprefix('ab'), abcde[2:])
        self.assertString(abcde.removeprefix('xx'), abcde)
        self.assertString(abcde.removesuffix('de'), abcde[:-2])
        self.assertString(abcde.removesuffix('xx'), abcde)

        # don't bother with the test for 3.6-3.8
        if not hasattr('', 'removeprefix'):  # pragma: no cover
            return

        for value_name, value in values.items():
            for i in range(len(value)):
                with self.subTest(value=value_name, i=i):
                    prefix = value[:i]
                    self.assertString(value.removeprefix(prefix), str(value).removeprefix(prefix))
                    suffix = value[i:]
                    self.assertString(value.removesuffix(suffix), str(value).removesuffix(suffix))
            with self.subTest(value=value_name):
                self.assertIs(value.removeprefix(chipmunk), value)
                self.assertIs(value.removesuffix(chipmunk), value)

        with self.assertRaises(TypeError):
            abcde.removeprefix(33.5)
        with self.assertRaises(TypeError):
            abcde.removesuffix(33.5)

    def test_removesuffix(self):
        # see test_removeprefix
        pass

    def test_replace(self):
        for value_name, value in values.items():
            for src in "abcde":
                with self.subTest(value=value_name, src=src):
                    result = value.replace(src, str(chipmunk))
                    if src in value:
                        self.assertString(result, str(value).replace(src, chipmunk))
                    else:
                        self.assertString(result, value)

        self.assertString(abcde.replace('c', 'x', 0), abcde)
        wackyland_ampersand = string('wackyland ampersand')
        self.assertString(wackyland_ampersand.replace('a', 'AAA', 3), 'wAAAckylAAAnd AAAmpersand')

        with self.assertRaises(TypeError):
            abcde.replace(33, 'x')
        with self.assertRaises(TypeError):
            abcde.replace('x', 33)
        with self.assertRaises(TypeError):
            abcde.replace('x', 'y', 55.5)

    def test_reversed(self):
        for i, (s, c) in enumerate(zip(reversed(abcde), reversed(str(abcde)))):
            self.assertEqual(s, c)
            self.assertEqual(s.column_number, 5 - i)

        s = string()
        self.assertEqual(list(s), list(reversed(s)))
        s = string('x')
        self.assertEqual(list(s), list(reversed(s)))

    def test_rfind(self):
        # see test___contains__
        pass

    def test_rindex(self):
        # see test___contains__
        pass

    def test_rjust(self):
        self.assertEqual(himem.rstrip().rjust(8), "    QEMM")
        self.assertString(himem.rstrip().rjust(4), "QEMM")
        with self.assertRaises(TypeError):
            abcde.rjust(5, 352)
        with self.assertRaises(TypeError):
            abcde.rjust(5, 'xyz')
        with self.assertRaises(TypeError):
            abcde.rjust(5.5)
        with self.assertRaises(TypeError):
            abcde.rjust([3], 'x')


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
        for i, (s, sep, result) in enumerate([
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
            ]):
            with self.subTest(i=i, s=s, sep=sep):
                source = 'toe'
                l2 = string(s, source=source)
                list_split = list(l2.split(sep))
                list_rsplit = list(l2.rsplit(sep))
                for line, rline, r in zip_longest(list_split, list_rsplit, result):
                    with self.subTest(line=line):
                        s2, offset, line_number, column_number = r
                        self.assertEqual(line, s2, f"{line!r} != {r}")
                        self.assertEqual(rline, s2, f"{rline!r} != {r}")
                        self.assertEqual(line.offset, offset, f"{line!r} != {r}")
                        self.assertEqual(rline.offset, offset, f"{rline!r} != {r}")
                        self.assertEqual(line.line_number, line_number, f"{line!r} != {r}")
                        self.assertEqual(rline.line_number, line_number, f"{rline!r} != {r}")
                        self.assertEqual(line.column_number, column_number, f"{line!r} != {r}")
                        self.assertEqual(rline.column_number, column_number, f"{rline!r} != {r}")

                axxb = string("a x x b")
                list_split = axxb.split(' x ')
                self.assertString(list_split[0], 'a')
                self.assertString(list_split[1], 'x b')
                list_rsplit = axxb.rsplit(' x ')
                self.assertString(list_rsplit[0], 'a x')
                self.assertString(list_rsplit[1], 'b')

        with self.assertRaises(TypeError):
            abcde.split(33.5)
        with self.assertRaises(TypeError):
            abcde.split('x', 33.5)

        with self.assertRaises(TypeError):
            abcde.rsplit(33.5)
        with self.assertRaises(TypeError):
            abcde.rsplit('x', 33.5)


    def test_splitlines(self):
        # splitlines_demo = string(' a \n b \r c \r\n d \n\r e ', source='Z')
        self.assertEqual(list(splitlines_demo.splitlines()), [' a ', ' b ', ' c ', ' d ', '', ' e '])
        self.assertEqual(list(splitlines_demo.splitlines(True)), [' a \n', ' b \r', ' c \r\n', ' d \n', '\r', ' e '])

        assert splitlines_demo in values.values()

        for value_name, value in values.items():
            with self.subTest(value=value_name):
                splitted = value.splitlines(True)
                reconstituted = string.cat(*splitted)
                self.assertString(reconstituted, value)

    def test_startswith(self):
        pass

    def test_strip(self):
        methods = ("strip", "lstrip", "rstrip")
        for value_name, value in values.items():
            s = str(value)
            for method in methods:
                with self.subTest(value=value_name, method=method):
                    s_mutated = getattr(s, method)()
                    value_mutated = getattr(value, method)()
                    if s_mutated == s:
                        self.assertIs(value_mutated, value)
                    else:
                        # print(f"{value=!r} {method} -> {value_mutated=!r}")
                        self.assertString(value_mutated, s_mutated)
                with self.subTest(method=method):
                    with self.assertRaises(TypeError):
                        getattr(abcde, method)(33.5)

    def test_swapcase(self):
        for value_name, value in values.items():
            with self.subTest(value=value_name):
                self.assertEqual(value.swapcase(), str(value).swapcase())

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
        def test(name, s, columns):
            for (i, c), expected in zip_longest(enumerate(s), columns):
                c2 = s[i]
                with self.subTest(s=name, i=i, c=c, c2=c2):
                    self.assertEqual(c.column_number, expected)
                    self.assertEqual(c2.column_number, expected)


        s1 = string('ab\tcde\tfg')
        s1_columns = [1, 2, 3, 9, 10, 11, 12, 17, 18]
        test('s1', s1, s1_columns)

        s2 = string('ab\tcde\tfg', tab_width=4)
        s2_columns = [1, 2, 3, 5, 6, 7, 8, 9, 10]
        test('s2', s2, s2_columns)

        # now add 'em together!
        s3 = s1 + s2
        s3_columns = s1_columns + s2_columns
        test('s3', s3, s3_columns)


    def test_bisect(self):
        for i in range(1, len(alphabet) - 1):
            a, b = alphabet.bisect(i)
            self.assertIsInstance(a, string)
            self.assertIsInstance(b, string)
            self.assertEqual(len(a), i)
            self.assertTrue(alphabet.startswith(a))
            self.assertEqual(a + b, alphabet)

        with self.assertRaises(TypeError):
            alphabet.bisect(33.5)

    def test_cat(self):
        self.assertString(string.cat(), '')
        self.assertString(string.cat(abcde), abcde)
        self.assertString(string.cat(abcde, 'xyz'), 'abcdexyz')
        self.assertString(string.cat(abcde[:2], abcde[2:]), abcde)
        self.assertString(string.cat(abcde[:2], abcde[:2]), 'abab')

        with self.assertRaises(TypeError):
            string.cat(3, 4, 5)
        with self.assertRaises(TypeError):
            string.cat('a', 'b', 5.2)

        t = string.cat('a')
        self.assertString(t, 'a')

        t = string.cat('', '', '', string(), '')
        self.assertString(t, '')


    def test_generate_tokens(self):
        lines = [
        "import big\n",
        "print(big)\n",
        "'''abc\n",
        "def\n",
        "ghi'''\n",
        ''
        ]
        text = string("".join(lines))

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
        p = string(":+").compile()
        s = string('a:b::c::d:')
        l = p.split(s)
        self.assertEqual(l,
            [
            s[0],
            s[2],
            s[5],
            s[8],
            s[10:10],
            ])

    def test_lazy_line_and_column(self):
        # line and column numbers are now lazy-computed
        # when we wouldn't otherwise get 'em for free.

        # .where
        segment = alphabet[5:10]
        self.assertIsNone(segment._line_number)
        self.assertIsNone(segment._column_number)
        self.assertEqual(segment.where, '"C:\\AUTOEXEC.BAT" line 1 column 6')

        # .__iter__
        segment = alphabet[5:10]
        self.assertIsNone(segment._line_number)
        self.assertIsNone(segment._column_number)
        l = list(segment)
        s = l[0]
        self.assertEqual(s.line_number, 1)
        self.assertEqual(s.column_number, 6)

        # cat
        segment = alphabet[5:10]
        self.assertIsNone(segment._line_number)
        self.assertIsNone(segment._column_number)
        s = string.cat(line1, line2)
        self.assertEqual(s.line_number, 1)
        self.assertEqual(s.column_number, 1)
        self.assertEqual(s, line1 + line2)



class BigLinkedListTests(unittest.TestCase):

    maxDiff = None

    def lock_fns(self):
        def return_none():
            return None

        def return_new_lock():
            return Lock()

        lock = Lock()
        def return_one_lock():
            return lock

        return [return_none, return_new_lock, return_one_lock]


    def assertLength(self, o, length):
        self.assertEqual(len(o), length)

    def assertLinkedListEqual(self, t, expected):
        self.assertIsInstance(t, linked_list)
        expected = list(expected)
        got = list(t)
        self.assertEqual(expected, got)
        self.assertEqual(len(t), len(expected))

    def assertNoSpecialNodes(self, t):
        # white box testing
        head = t._head
        tail = t._tail

        cursor = head.next
        while cursor != tail:
            self.assertIsNone(cursor.special)
            cursor = cursor.next

    def assertIsSpecial(self, it):
        self.assertIsNotNone(it)
        self.assertTrue(it.is_special)
        self.assertEqual(it.special, 'special')

    def assertIsHead(self, it):
        self.assertIsNotNone(it)
        self.assertTrue(it.is_special)
        self.assertEqual(it.special, 'head')

    def assertIsTail(self, it):
        self.assertIsNotNone(it)
        self.assertTrue(it.is_special)
        self.assertEqual(it.special, 'tail')

    def assertIsNormalNode(self, it):
        self.assertIsNotNone(it)
        self.assertFalse(it.is_special)
        self.assertEqual(it.special, None)


    def test_list_basics(self):
        for _lock in self.lock_fns():
            self.list_basics_tests(_lock)

    def list_basics_tests(self, _lock):
        t = linked_list(lock=_lock())
        self.assertFalse(t)
        self.assertLinkedListEqual(t, [])

        t = linked_list((1, 2, 3, 4, 5), lock=_lock())
        self.assertTrue(t)
        self.assertLinkedListEqual(t, [1, 2, 3, 4, 5])

        t = linked_list([1, 2, 4, 8, 16], lock=_lock())
        self.assertTrue(t)
        self.assertLinkedListEqual(t, [1, 2, 4, 8, 16])

        t = linked_list('abcde', lock=_lock())
        self.assertTrue(t)
        self.assertLinkedListEqual(t, ['a', 'b', 'c', 'd', 'e'])

        t = linked_list(iter((1, 1, 2, 3, 5, 8)), lock=_lock())
        self.assertTrue(t)
        self.assertLinkedListEqual(t, [1, 1, 2, 3, 5, 8])


    def test_iterator_basics(self):
        for _lock in self.lock_fns():
            self.iterator_basics_tests(_lock)

    def iterator_basics_tests(self, _lock):
        t = linked_list(lock=_lock())
        self.assertNoSpecialNodes(t)

        with self.assertRaises(TypeError):
            # white box testing
            linked_list_base_iterator(t._head)

        # an iterator on a linked list always starts out at head
        it = iter(t)
        self.assertIsHead(it)
        self.assertFalse(it)
        with self.assertRaises(UndefinedIndexError):
            it[0]
        with self.assertRaises(UndefinedIndexError):
            it.pop()
        with self.assertRaises(UndefinedIndexError):
            it.rpop()
        # iterator only returns True if you can call next and it doesn't raise.
        # so, when pointing to either head or tail of an empty list, it returns false.
        self.assertFalse(it)
        it.exhaust()
        self.assertFalse(it)
        with self.assertRaises(UndefinedIndexError):
            it.pop()
        with self.assertRaises(UndefinedIndexError):
            it.rpop()
        it.reset()
        self.assertFalse(it)

        # and you can't go past head
        with self.assertRaises(UndefinedIndexError):
            before = it.before()
        self.assertNoSpecialNodes(t)

        # an reverse iterator on a linked list always starts out at tail
        rit = reversed(t)
        self.assertIsTail(rit)
        self.assertFalse(rit)
        with self.assertRaises(UndefinedIndexError):
            rit[0]
        with self.assertRaises(UndefinedIndexError):
            rit.pop()
        with self.assertRaises(UndefinedIndexError):
            rit.rpop()

        # iterator only returns True if you can call next and it doesn't raise.
        # so, when pointing to either head or tail of an empty list, it returns false.
        self.assertFalse(rit)
        rit.exhaust() # rit, exhaust goes to head
        self.assertFalse(rit)
        with self.assertRaises(UndefinedIndexError):
            rit.pop()
        with self.assertRaises(UndefinedIndexError):
            rit.rpop()
        rit.reset()   # rit, reset goes to tail
        self.assertFalse(rit)

        # and you can't go past tail
        with self.assertRaises(UndefinedIndexError):
            before = rit.before()

        self.assertNoSpecialNodes(t)

        initial = [1, 2, 3, 4, 5]
        t = linked_list(initial, lock=_lock())
        self.assertLength(t, 5)
        it = iter(t)
        result = list(it)
        self.assertEqual(initial, result)

        reversed_initial = list(reversed(initial))
        rit = reversed(t)
        result = list(rit)
        self.assertEqual(reversed_initial, result)
        self.assertNoSpecialNodes(t)

        # you can't make your own iterators
        with self.assertRaises(TypeError):
            big.types.linked_list_base_iterator()
        with self.assertRaises(TypeError):
            big.types.linked_list_base_iterator(t)
        with self.assertRaises(TypeError):
            big.types.linked_list_base_iterator(it)

        with self.assertRaises(TypeError):
            linked_list_iterator()
        with self.assertRaises(TypeError):
            linked_list_iterator(t)
        with self.assertRaises(TypeError):
            linked_list_iterator(it)

        with self.assertRaises(TypeError):
            linked_list_reverse_iterator()
        with self.assertRaises(TypeError):
            linked_list_reverse_iterator(t)
        with self.assertRaises(TypeError):
            linked_list_reverse_iterator(it)

        # pop and popleft with indexing,
        # forwards and backwards
        def setup():
            t = linked_list([0, 1, 2, 3, 4, 5, 6, 7, 8], lock=_lock())
            it = t.find(4)
            return t, it

        for index, expected in(
            (0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5),
            (6, 6),
            (7, 7),
            (8, 8),

            (-1, 8),
            (-2, 7),
            (-3, 6),
            (-4, 5),
            (-5, 4),
            (-6, 3),
            (-7, 2),
            (-8, 1),
            (-9, 0),
            ):
            with self.subTest(index=index, expected=expected):
                t, it_4 = setup()
                got = t.pop(index)
                self.assertEqual(expected, got)

                t, it_4 = setup()
                got = t.rpop(index)
                self.assertEqual(expected, got)

                if index >= 0:
                    t, it_4 = setup()
                    it_0 = t.find(0)
                    got = it_0.pop(index)
                    self.assertEqual(expected, got)

                    t, it_4 = setup()
                    it_0 = t.find(0)
                    got = it_0.rpop(index)
                    self.assertEqual(expected, got)

                    t, it_4 = setup()
                    got = it_4.pop(index - 4)
                    self.assertEqual(expected, got)

                    t, it_4 = setup()
                    got = it_4.rpop(index - 4)
                    self.assertEqual(expected, got)

                    t, it_4 = setup()
                    rit_4 = reversed(it_4)
                    got = rit_4.pop(4 - index)
                    self.assertEqual(expected, got)

                    t, it_4 = setup()
                    rit_4 = reversed(it_4)
                    got = rit_4.pop(4 - index)
                    self.assertEqual(expected, got)

                else:
                    t, it_4 = setup()
                    tail = t.tail()
                    got = tail.pop(index)
                    self.assertEqual(expected, got)

                    t, it_4 = setup()
                    tail = t.tail()
                    got = tail.rpop(index)
                    self.assertEqual(expected, got)

        t, it_4 = setup()
        value = it_4.pop()
        self.assertEqual(value, 4)
        self.assertEqual(it_4[0], 3)

        t, it_4 = setup()
        value = it_4.rpop()
        self.assertEqual(value, 4)
        self.assertEqual(it_4[0], 5)

        t, it_4 = setup()
        rit_4 = reversed(it_4)
        value = rit_4.pop()
        self.assertEqual(value, 4)
        self.assertEqual(rit_4[0], 5)

        t, it_4 = setup()
        rit_4 = reversed(it_4)
        value = rit_4.rpop()
        self.assertEqual(value, 4)
        self.assertEqual(rit_4[0], 3)

        t, it_4 = setup()
        with self.assertRaises(UndefinedIndexError):
            t.pop(100)
        with self.assertRaises(UndefinedIndexError):
            t.rpop(100)
        with self.assertRaises(UndefinedIndexError):
            it_4.pop(100)
        with self.assertRaises(UndefinedIndexError):
            it_4.rpop(100)
        with self.assertRaises(UndefinedIndexError):
            t.pop(-100)
        with self.assertRaises(UndefinedIndexError):
            t.rpop(-100)
        with self.assertRaises(UndefinedIndexError):
            it_4.pop(-100)
        with self.assertRaises(UndefinedIndexError):
            it_4.rpop(-100)



    def test_method_superset(self):
        for _lock in self.lock_fns():
            self.method_superset_tests(_lock)

    def method_superset_tests(self, _lock):
        # check that linked_list furnishes every
        # method (dunder and otherwise) provided
        # by both list and collections.deque

        def dir_without_sunder(o):
            # return dir,
            # but omit names that start with a *single* underscore.
            # (we still want names that start with *two* underscores.)
            return list(name for name in dir(o) if not (name.startswith('_') and not (name.startswith('__'))))

        list_dir = set(dir_without_sunder([]))
        deque_dir = set(dir_without_sunder(collections.deque()))
        list_and_deque_dir = list(list_dir | deque_dir)
        list_and_deque_dir.sort()

        linked_list_dir = dir_without_sunder(linked_list(lock=_lock()))
        linked_list_dir.sort()

        def words(s):
            for line in s.strip().split('\n'):
                line = line.partition('#')[0].strip()
                if not line:
                    continue
                for name in line.split():
                    yield name

        for name in words("""
            ##
            ## This is stuff in linked_list that isn't found
            ## in either list or collections.deque.
            ##

            ##
            ## __dunder__ stuff
            ##

            __deepcopy__            # feature for copy.deepcopy
            __setstate__
            __slots__

            ##
            ## new method calls
            ##

            head tail

            find rfind
            match rmatch

            rextend  # which is different from extendleft!
            rpop
            rremove

            cut rcut
            splice rsplice

            ##
            ## aliases for appendleft
            ##

            rappend
            prepend

            """):
            linked_list_dir.remove(name)
            assert name not in list_and_deque_dir, f"name {name} is in list_and_deque_dir !!!"

        for name in words("""
            ##
            ## This is stuff that Python added to user types
            ## in versions after 3.6, so they're not always there.
            ## (We just remove 'em from linked_list if they're not in list/deque.)
            ##

            __bool__                # deque has bool in 3.6 but removed it?!
            __class_getitem__       # supported in 3.7, list didn't add until 3.9
            __firstlineno__         # added to user types
            __static_attributes__   # added to user types
            __module__              # always added to user types, shows up in deque > 3.6

            __getstate__            # deque added this at some? point > 3.6

            """):
            if (name in linked_list_dir) and (name not in list_and_deque_dir):
                linked_list_dir.remove(name)

        # for name in linked_list_dir:
        #     if name not in list_and_deque_dir:
        #         print(f"{name} in linked_list_dir but not in list_and_deque_dir")

        # for name in list_and_deque_dir:
        #     if name not in linked_list_dir:
        #         print(f"{name} in list_and_deque_dir but not in linked_list_dir")

        self.assertEqual(linked_list_dir, list_and_deque_dir)

    def test_empty_list(self):
        for _lock in self.lock_fns():
            self.empty_list_tests(_lock)

    def empty_list_tests(self, _lock):
        # if the list is empty:
        t = linked_list(lock=_lock())
        self.assertFalse(t)

        # "after" head is tail
        it = iter(t)
        self.assertIsHead(it)
        self.assertFalse(it)

        after = it.after()
        self.assertIsTail(after)
        self.assertFalse(after)

        # if you run next on it, it goes to tail and stays there
        result = next(it, 5)
        self.assertEqual(result, 5)
        self.assertIsTail(it)
        result = next(it, 5)
        self.assertEqual(result, 5)
        self.assertIsTail(it)

        it.reset()
        self.assertIsHead(it)
        it.exhaust()
        self.assertIsTail(it)

        # after tail (reversed) is head
        rit = reversed(t)
        self.assertIsTail(rit)
        self.assertFalse(rit)
        after = rit.after()
        self.assertIsHead(after)
        self.assertFalse(after)

        # if you run next on it, it goes to head and stays there
        result = next(rit, 5)
        self.assertEqual(result, 5)
        self.assertIsHead(rit)
        result = next(rit, 5)
        self.assertEqual(result, 5)
        self.assertIsHead(rit)

        rit.reset()
        self.assertIsTail(rit)
        rit.exhaust()
        self.assertIsHead(rit)

        # can't pop from an empty list
        with self.assertRaises(ValueError):
            t.pop()
        with self.assertRaises(ValueError):
            t.popleft()

        self.assertNoSpecialNodes(t)

    def test_extend(self):
        for _lock in self.lock_fns():
            self.extend_tests(_lock)

    def extend_tests(self, _lock):
        def setup():
            t = linked_list((1, 2, 3), lock=_lock())
            self.assertLength(t, 3)
            it = iter(t)
            return t, it

        t, it = setup()
        t.extend('ABC')
        self.assertLinkedListEqual(t, [1, 2, 3, 'A', 'B', 'C'])
        self.assertLength(t, 6)
        self.assertNoSpecialNodes(t)

        with self.assertRaises(ValueError):
            t.extend(t)

        t, it = setup()
        t.rextend('ABC')
        self.assertLinkedListEqual(t, ['A', 'B', 'C', 1, 2, 3])
        self.assertLength(t, 6)
        self.assertNoSpecialNodes(t)

        with self.assertRaises(ValueError):
            t.rextend(t)

        t, it = setup()
        it = it.find(1)
        it.extend('ABC')
        self.assertLinkedListEqual(t, [1, 'A', 'B', 'C', 2, 3])
        self.assertLength(t, 6)
        self.assertNoSpecialNodes(t)

        t, it = setup()
        it = it.find(3)
        it.rextend('ABC')
        self.assertLinkedListEqual(t, [1, 2, 'A', 'B', 'C', 3])
        self.assertLength(t, 6)
        self.assertNoSpecialNodes(t)

        with self.assertRaises(ValueError):
            it.extend(t)
        with self.assertRaises(ValueError):
            it.rextend(t)
        rit = reversed(it)
        with self.assertRaises(ValueError):
            rit.extend(t)
        with self.assertRaises(ValueError):
            rit.rextend(t)


        # surprise! extending and rextending on a *reverse iterator*
        # inserts the nodes in *reverse order*.
        #
        # sorry!  but
        #   i.extend(iterable)
        # and
        #   for o in iterable:
        #       i.append(o)
        # must always produce the same result, for both forwards
        # and reverse iterators.

        def setup2():
            t = linked_list((1, 2, 3), lock=_lock())
            rit = reversed(t)
            return t, rit

        t, rit = setup2()
        self.assertIsInstance(rit, linked_list_reverse_iterator)
        rit = rit.find(2)
        self.assertIsInstance(rit, linked_list_reverse_iterator)
        rit.extend('ABC')
        self.assertLinkedListEqual(t, [1, 'C', 'B', 'A', 2, 3])
        self.assertLength(t, 6)
        self.assertNoSpecialNodes(t)

        t, rit = setup2()
        self.assertIsInstance(rit, linked_list_reverse_iterator)
        rit = rit.find(2)
        self.assertIsInstance(rit, linked_list_reverse_iterator)
        rit.rextend('ABC')
        self.assertLinkedListEqual(t, [1, 2, 'C', 'B', 'A', 3])
        self.assertLength(t, 6)
        self.assertNoSpecialNodes(t)


    def test_linked_list_methods(self):
        for _lock in self.lock_fns():
            self.linked_list_methods_tests(_lock)

    def linked_list_methods_tests(self, _lock):
        def setup():
            t = linked_list((1, 2, 3), lock=_lock())
            it = t.find(2)
            return t, it

        t, it = setup()
        copy = t.copy()
        self.assertEqual(t, copy)

        copy.remove(2)
        self.assertNotEqual(t, copy)
        self.assertNotEqual(t, (1, 2, 4))
        self.assertNoSpecialNodes(t)
        self.assertNoSpecialNodes(copy)

        with self.assertRaises(ValueError):
            t.remove('abcde')
        got = t.remove('abcde', 'not found')
        self.assertEqual(got, 'not found')

        t, it = setup()
        t.append('xyz')
        self.assertLinkedListEqual(t, (1, 2, 3, 'xyz'))
        self.assertNoSpecialNodes(t)

        t, it = setup()
        t.prepend('abc')
        self.assertLinkedListEqual(t, ('abc', 1, 2, 3))
        self.assertNoSpecialNodes(t)


    def test_with_deleted_nodes(self):
        for _lock in self.lock_fns():
            self.deleted_nodes_tests(_lock)

    def deleted_nodes_tests(self, _lock):
        def setup():
            # returns t, it, iterators
            #
            #   deleted nodes! ---+--+--+-----+--+--+
            #                     |  |  |     |  |  |
            #                     v  v  v     v  v  v
            # t = linked_list((0, 1, 2, 3, 4, 5, 6, 7, 8))
            #                              ^
            #                              |
            # it = iter pointing at 4 -----+
            #
            # iterators, array of iterators pointing at each node
            t = linked_list((0, 1, 2, 3, 4, 5, 6, 7, 8), lock=_lock())
            iterators = [t.find(i) for i in range(9)]
            for i in (1, 2, 3, 5, 6, 7):
                it = t.find(i)
                it.pop()
            it = t.find(4)
            return t, it, iterators

        t, it, iterators = setup()
        copy = it.copy()
        got = copy.previous()
        self.assertEqual(got, 0)
        self.assertEqual(copy[0], 0)
        before = it.before()
        self.assertEqual(before[0], 0)

        copy = it.copy()
        got = copy.next()
        self.assertEqual(got, 8)
        self.assertEqual(copy[0], 8)
        after = it.after()
        self.assertEqual(after[0], 8)

        t, it, iterators = setup()
        value = it.pop()
        self.assertEqual(value, 4)
        self.assertEqual(it[0], 0)

        t, it, iterators = setup()
        value = it.rpop()
        self.assertEqual(value, 4)
        self.assertEqual(it[0], 8)

        t, it, iterators = setup()
        it2 = iterators[2]
        value = it2.previous()
        self.assertEqual(value, 0)
        self.assertEqual(it2[0], 0)

        t, it, iterators = setup()
        it6 = iterators[6]
        value = it6.next()
        self.assertEqual(value, 8)
        self.assertEqual(it6[0], 8)

        # try t.popleft when the node after head is deleted
        t, it, iterators = setup()
        t.remove(0)
        value = t.popleft()
        self.assertEqual(value, 4)
        it = iter(t)
        value = next(it)
        self.assertEqual(value, 8)

        # and pop when the node before tail is deleted
        t, it, iterators = setup()
        t.remove(8)
        value = t.pop()
        self.assertEqual(value, 4)
        it = reversed(t)
        value = next(it)
        self.assertEqual(value, 0)

        t = linked_list(range(10), lock=_lock())
        with self.assertRaises(UndefinedIndexError):
            t[10] = 'abc'
        with self.assertRaises(UndefinedIndexError):
            del t[10]


    def test_iterator_methods(self):
        for _lock in self.lock_fns():
            self.iterator_methods_tests(_lock)

    def iterator_methods_tests(self, _lock):
        def setup():
            t = linked_list([1, 2, 3, 4, 5], lock=_lock())
            it = t.find(3)
            return t, it

        t, it = setup()
        self.assertEqual(it[0], 3)
        self.assertEqual(repr(it), f"<linked_list_iterator {hex(id(it))} cursor=linked_list_node(3)>")
        copy = it.copy()
        del(copy)
        self.assertEqual(it[0], 3)
        self.assertNoSpecialNodes(t)

        got = it.next()
        self.assertEqual(got, 4)
        self.assertEqual(it[0], 4)

        got = it.next()
        self.assertEqual(got, 5)
        self.assertEqual(it[0], 5)

        with self.assertRaises(StopIteration):
            got = it.next()
        got = it.next(None)
        self.assertIsNone(got)
        self.assertIsTail(it)

        got = it.next(None)
        self.assertIsNone(got)
        self.assertIsTail(it)
        self.assertNoSpecialNodes(t)

        t, it = setup()
        self.assertEqual(it[0], 3)
        got = it.previous()
        self.assertEqual(got, 2)
        self.assertEqual(it[0], 2)

        got = it.previous()
        self.assertEqual(got, 1)
        self.assertEqual(it[0], 1)

        with self.assertRaises(StopIteration):
            got = it.previous()
        got = it.previous(None)
        self.assertIsNone(got)
        self.assertIsHead(it)

        got = it.previous(None)
        self.assertIsNone(got)
        self.assertIsHead(it)
        self.assertNoSpecialNodes(t)

        t, it = setup()
        before = it.before()
        self.assertEqual(it[0], 3)
        self.assertEqual(before[0], 2)
        copy = before.copy()
        copy.pop() # before now points at a deleted node
        before2 = it.before() # skips over deleted node
        self.assertEqual(before2[0], 1)

        got = before2.remove(5)
        self.assertEqual(got, 5)
        with self.assertRaises(ValueError):
            got = before2.remove('qemm')
        got = before2.remove('quarterdeck', 'not found')
        self.assertEqual(got, 'not found')


        t, it = setup()
        after = it.after()
        self.assertEqual(it[0], 3)
        self.assertEqual(after[0], 4)
        copy = after.copy()
        copy.pop() # after now points at a deleted node
        after2 = it.after() # skips over deleted node
        self.assertEqual(after2[0], 5)

        t, it = setup()
        rit = reversed(it)
        it2 = reversed(rit)
        self.assertEqual(it, it2)
        self.assertEqual(it[0], it2[0])

        # test del!
        # white box testing.
        t, it = setup()
        del it

        t, it = setup()
        node = it._cursor
        del node.iterator_refcount
        del it

        t, it = setup()
        node = it._cursor
        del it._cursor
        del it

        t, it = setup()
        with self.assertRaises(UndefinedIndexError):
            it[-3]
        self.assertEqual(it[-2], 1)
        self.assertEqual(it[-1], 2)

        self.assertEqual(it[ 0], 3)

        self.assertEqual(it[ 1], 4)
        self.assertEqual(it[ 2], 5)
        with self.assertRaises(IndexError):
            it[3]

        t, it = setup()
        self.assertLinkedListEqual(it[-2: 3: 2], [1, 3, 5])
        self.assertLinkedListEqual(it[ 2:-3:-2], [5, 3, 1])
        with self.assertRaises(ValueError):
            it[-6: 2: 3]
        with self.assertRaises(ValueError):
            it[ 2:-6: 3]
        with self.assertRaises(ValueError):
            it[ 2:-3: 0]
        self.assertLinkedListEqual(it[ 2:-3: 2], [])
        self.assertLinkedListEqual(it[-2: 3:-2], [])
        self.assertNoSpecialNodes(t)

    def test_prepend_and_append_and_extend_and_rextend(self):
        for _lock in self.lock_fns():
            self.prepend_and_append_and_extend_and_rextend_tests(_lock)

    def prepend_and_append_and_extend_and_rextend_tests(self, _lock):
        #
        # test all our verbs in the middle of the list
        #
        def setup():
            t = linked_list((1, 2, 3), lock=_lock())
            it = t.find(2)
            self.assertIsNormalNode(it)
            return t, it

        t, it = setup()
        it.prepend(1.5)
        self.assertLinkedListEqual(t, [1, 1.5, 2, 3])
        self.assertIsNormalNode(it)
        self.assertEqual(it[0], 2)
        self.assertNoSpecialNodes(t)

        t, it = setup()
        it.append(2.5)
        self.assertLinkedListEqual(t, [1, 2, 2.5, 3])
        self.assertIsNormalNode(it)
        self.assertEqual(it[0], 2)
        self.assertNoSpecialNodes(t)

        t, it = setup()
        it.rextend((1.25, 1.5, 1.75))
        self.assertLinkedListEqual(t, [1, 1.25, 1.5, 1.75, 2, 3])
        self.assertIsNormalNode(it)
        self.assertEqual(it[0], 2)
        self.assertNoSpecialNodes(t)

        t, it = setup()
        it.extend((2.25, 2.5, 2.75))
        self.assertLinkedListEqual(t, [1, 2, 2.25, 2.5, 2.75, 3])
        self.assertIsNormalNode(it)
        self.assertEqual(it[0], 2)
        self.assertNoSpecialNodes(t)

        #
        # now test when we're pointed at head
        #
        def setup():
            t = linked_list((1, 2, 3), lock=_lock())
            it = iter(t)
            self.assertIsHead(it)
            return t, it
        t, it = setup()

        t, it = setup()
        it.append('A')
        self.assertLinkedListEqual(t, ['A', 1, 2, 3])
        self.assertIsHead(it)
        self.assertNoSpecialNodes(t)

        t, it = setup()
        with self.assertRaises(UndefinedIndexError):
            it.prepend('B')

        t, it = setup()
        it.extend('CDE')
        self.assertLinkedListEqual(t, ['C', 'D', 'E', 1, 2, 3])
        self.assertIsHead(it)
        self.assertNoSpecialNodes(t)

        t, it = setup()
        with self.assertRaises(UndefinedIndexError):
            it.rextend('FGH')


        #
        # now test when we're pointed at tail
        #
        def setup():
            t = linked_list((1, 2, 3), lock=_lock())
            it = iter(t)
            it.exhaust()
            return t, it
        t, it = setup()

        t, it = setup()
        it.prepend('I')
        self.assertLinkedListEqual(t, [1, 2, 3, 'I'])
        self.assertIsTail(it)
        self.assertNoSpecialNodes(t)

        t, it = setup()
        with self.assertRaises(UndefinedIndexError):
            it.append('J')

        t, it = setup()
        it.rextend('KLM')
        self.assertLinkedListEqual(t, [1, 2, 3, 'K', 'L', 'M'])
        self.assertIsTail(it)
        self.assertNoSpecialNodes(t)

        t, it = setup()
        with self.assertRaises(UndefinedIndexError):
            it.extend('NOP')


        #
        # now test all of the above with empty lists!
        #

        def setup_at_head():
            t = linked_list(lock=_lock())
            it = iter(t)
            self.assertIsHead(it)
            return t, it

        def setup_at_tail():
            t = linked_list(lock=_lock())
            it = iter(t)
            it.exhaust()
            return t, it

        # appending to head obviously works
        t, it = setup_at_head()
        it.append('W')
        self.assertLinkedListEqual(t, ['W'])
        self.assertIsHead(it)
        self.assertNoSpecialNodes(t)

        t, it = setup_at_head()
        with self.assertRaises(UndefinedIndexError):
            it.prepend('X')

        # prepending before tail obviously works
        t, it = setup_at_tail()
        it.prepend('Y')
        self.assertLinkedListEqual(t, ['Y'])
        self.assertIsTail(it)
        self.assertNoSpecialNodes(t)

        t, it = setup_at_tail()
        with self.assertRaises(UndefinedIndexError):
            it.append('Z')

        # now with extend and rextend

        # appending to head obviously works
        t, it = setup_at_head()
        it.extend('uvw')
        self.assertLinkedListEqual(t, ['u', 'v', 'w'])
        self.assertIsHead(it)
        self.assertNoSpecialNodes(t)

        t, it = setup_at_head()
        with self.assertRaises(UndefinedIndexError):
            it.rextend('vwx')

        # prepending before tail obviously works
        t, it = setup_at_tail()
        it.rextend('wxy')
        self.assertLinkedListEqual(t, ['w', 'x', 'y'])
        self.assertIsTail(it)
        self.assertNoSpecialNodes(t)

        t, it = setup_at_tail()
        with self.assertRaises(UndefinedIndexError):
            it.extend('xyz')


    def test_special_nodes(self):
        for _lock in self.lock_fns():
            self.special_nodes_tests(_lock)

    def special_nodes_tests(self, _lock):
        t = linked_list('a')
        self.assertEqual(repr(t), "linked_list(['a'])")

        t = linked_list('a', lock=_lock())
        self.assertTrue(t)

        it = iter(t).after()
        copy = it.copy()
        copy.pop()
        # white box testing: remove lock, just so we can examine the repr
        t._lock = None
        # test repr with a deleted node
        self.assertEqual(repr(t), "linked_list([])")
        self.assertFalse(t)

        with self.assertRaises(UndefinedIndexError):
            iter(t).pop()
        with self.assertRaises(UndefinedIndexError):
            reversed(t).pop()
        with self.assertRaises(SpecialNodeError):
            it.pop()

        # white box test of repr
        self.assertEqual(repr(t._head), "linked_list_node(None, special='head')")



    def test_deleted_node(self):
        for _lock in self.lock_fns():
            self.deleted_node_tests(_lock)

    def deleted_node_tests(self, _lock):
        # "dit" == "deleted iterator"
        # points to the deleted node in the center of the list,
        # between 3 and 4
        def setup():
            t = linked_list([1, 2, 3, 'X', 4, 5, 6], lock=_lock())
            dit = t.find('X')
            copy = dit.copy()
            copy.pop()
            del copy
            return t, dit

        t, dit = setup()
        self.assertEqual(list(    iter(t)), [1, 2, 3, 4, 5, 6])
        self.assertEqual(list(reversed(t)), [6, 5, 4, 3, 2, 1])
        self.assertLength(t, 6)
        self.assertIsSpecial(dit)
        self.assertIsInstance(dit, linked_list_iterator)
        with self.assertRaises(SpecialNodeError):
            dit[0]
        with self.assertRaises(SpecialNodeError):
            dit.pop()
        with self.assertRaises(SpecialNodeError):
            dit.rpop()

        # you also can't include a deleted node in a slice
        with self.assertRaises(SpecialNodeError):
            dit[-1:2]
        with self.assertRaises(SpecialNodeError):
            dit[-2:4:2]
        with self.assertRaises(SpecialNodeError):
            dit[1:-2:-1]
        with self.assertRaises(SpecialNodeError):
            dit[2:-4:-2]
        # ... but if you carefully step over it, it's fine!
        self.assertLinkedListEqual(dit[-3:4:2], [1, 3, 4, 6])

        copy = dit.copy()
        value = copy.previous()
        self.assertIsNormalNode(copy)
        self.assertEqual(value, 3)
        self.assertEqual(copy[0], 3)

        copy = dit.copy()
        value = next(copy)
        self.assertIsNormalNode(copy)
        self.assertEqual(value, 4)
        self.assertEqual(copy[0], 4)

        before = dit.before()
        self.assertIsNormalNode(before)
        self.assertEqual(before[0], 3)
        after = dit.after()
        self.assertIsNormalNode(after)
        self.assertEqual(after[0], 4)

        five = dit.find(5)
        self.assertIsNormalNode(five)
        self.assertEqual(five[0], 5)
        self.assertIsNone(dit.find(333))

        two = dit.rfind(2)
        self.assertIsNormalNode(two)
        self.assertEqual(two[0], 2)
        self.assertIsNone(dit.rfind(333))

        six = dit.match(lambda value: value == 6)
        self.assertIsNormalNode(six)
        self.assertEqual(six[0], 6)
        self.assertIsNone(dit.match(lambda value: value == 888))

        one = dit.rmatch(lambda value: value == 1)
        self.assertIsNormalNode(one)
        self.assertEqual(one[0], 1)
        self.assertIsNone(dit.rmatch(lambda value: value == 999))


        rdit = reversed(dit)
        self.assertIsSpecial(rdit)
        self.assertIsInstance(rdit, linked_list_reverse_iterator)
        self.assertTrue(rdit)
        with self.assertRaises(SpecialNodeError):
            rdit[0]
        with self.assertRaises(SpecialNodeError):
            rdit.pop()
        with self.assertRaises(SpecialNodeError):
            rdit.rpop()

        copy = rdit.copy()
        value = next(copy)
        self.assertIsNormalNode(copy)
        self.assertEqual(value, 3)
        self.assertEqual(copy[0], 3)

        copy = rdit.copy()
        value = copy.previous()
        self.assertIsNormalNode(copy)
        self.assertEqual(value, 4)
        self.assertEqual(copy[0], 4)

        before = rdit.before()
        self.assertIsNormalNode(before)
        self.assertEqual(before[0], 4)
        after = rdit.after()
        self.assertIsNormalNode(after)
        self.assertEqual(after[0], 3)

        five = rdit.rfind(5)
        self.assertEqual(five[0], 5)
        self.assertIsNormalNode(five)
        self.assertIsNone(rdit.rfind(333))
        two = rdit.find(2)
        self.assertIsNormalNode(two)
        self.assertEqual(two[0], 2)
        self.assertIsNone(rdit.find(333))

        six = rdit.rmatch(lambda value: value == 6)
        self.assertIsNormalNode(six)
        self.assertEqual(six[0], 6)
        self.assertIsNone(rdit.rmatch(lambda value: value == 888))

        one = rdit.match(lambda value: value == 1)
        self.assertIsNormalNode(one)
        self.assertEqual(one[0], 1)
        self.assertIsNone(rdit.match(lambda value: value == 999))

        t, dit = setup()
        dit.prepend('Z')
        self.assertLinkedListEqual(t, [1, 2, 3, 'Z', 4, 5, 6])
        self.assertLength(t, 7)

        t, dit = setup()
        dit.append('Q')
        self.assertLinkedListEqual(t, [1, 2, 3, 'Q', 4, 5, 6])
        self.assertLength(t, 7)

        t, dit = setup()
        rdit = reversed(dit)
        rdit.prepend('J')
        self.assertLinkedListEqual(t, [1, 2, 3, 'J', 4, 5, 6])
        self.assertLength(t, 7)

        t, dit = setup()
        rdit = reversed(dit)
        rdit.append('K')
        self.assertLinkedListEqual(t, [1, 2, 3, 'K', 4, 5, 6])
        self.assertLength(t, 7)


        #
        # test navigating past deleted nodes
        #

        def setup():
            t = linked_list(('a', 1, 'b', 2, 'c', 'd', 'e', 3, 4, 5, 'f', 'g', 'h', 6, 'i', 7, 'j'), lock=_lock())
            it = iter(t)
            def delete_str_nodes():
                it = iter(t)
                for value in it:
                    if isinstance(value, str):
                        it.pop()

            self.assertLength(t, 17)
            return t, it, delete_str_nodes

        # smoke-check: we can delete nodes in a loop, right?
        t, it, delete_str_nodes = setup()
        delete_str_nodes()
        self.assertLinkedListEqual(t, [1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(list(reversed(t)), [7, 6, 5, 4, 3, 2, 1])

        # test removing each individual character
        # and make sure find and match all work
        for c in 'abcdefghij':
            with self.subTest(c=c):
                for variant in ('t remove', 't rremove', 'it remove', 'it rremove'):
                    with self.subTest(variant=variant):
                        t, it, delete_str_nodes = setup()
                        if variant.endswith('rremove'):
                            if variant.startswith('it'):
                                it = t.tail()
                                it.rremove(c)
                            else:
                                t.rremove(c)
                        else:
                            if variant.startswith('it'):
                                it = t.head()
                                it.remove(c)
                            else:
                                t.remove(c)
                        self.assertLength(t, 16)
                        self.assertIsNone(t.find(c))
                        self.assertIsNone(t.rfind(c))
                        for i in range(1, 8):
                            with self.subTest(i=i):
                                it = t.find(i)
                                self.assertIsNormalNode(it)
                                self.assertEqual(it[0], i)
                                rit = t.rfind(i)
                                self.assertIsNormalNode(rit)
                                self.assertEqual(rit[0], i)

                                it = t.match(lambda value: value==i)
                                self.assertIsNormalNode(it)
                                self.assertEqual(it[0], i)
                                rit = t.rmatch(lambda value: value==i)
                                self.assertIsNormalNode(rit)
                                self.assertEqual(rit[0], i)

        t, it, delete_str_nodes = setup()

        # keep references to every node, to keep the deleted nodes alive
        iterators = []
        while it:
            iterators.append(it)
            it = it.after()

        delete_str_nodes()
        self.assertLinkedListEqual(t, [1, 2, 3, 4, 5, 6, 7])
        self.assertLength(t, 7)

        # now, starting from the center:
        it = t.find(3)

        seven = it.find(7)
        self.assertIsNormalNode(seven)
        self.assertEqual(seven[0], 7)
        one = it.rfind(1)
        self.assertIsNormalNode(one)
        self.assertEqual(one[0], 1)

        def raise_if_str(value):
            if isinstance(value, str): # pragma: nocover
                raise ValueError('str found, {value!r}')
            return False

        self.assertIsNone(it.match(raise_if_str))
        self.assertIsNone(it.rmatch(raise_if_str))
        self.assertIsNone(t.match(raise_if_str))
        self.assertIsNone(t.rmatch(raise_if_str))

        seven2 = it.match(lambda value: value == 7)
        self.assertIsNormalNode(seven2)
        self.assertEqual(seven2[0], 7)
        one2 = it.rmatch(lambda value: value == 1)
        self.assertIsNormalNode(one2)
        self.assertEqual(one2[0], 1)

        # prepend and append from two different deleted nodes
        # in any order should always produce the same result
        expected = [0, 1, 2, 3, 4, 5]
        for ordering in itertools.permutations([0, 1, 2, 3]):
            with self.subTest(ordering=ordering):
                t = linked_list([0, 'a', 'b', 5])
                it1 = t.find('a')
                copy = it1.copy();
                copy.pop()
                it2 = t.find('b')
                copy = it2.copy();
                copy.pop()

                operations = [
                    lambda: it1.prepend(1),
                    lambda: it1.append(2),
                    lambda: it2.prepend(3),
                    lambda: it2.append(4),
                    ]
                for index in ordering:
                    operations[index]()
                self.assertLength(t, 6)
                self.assertLinkedListEqual(t, expected)

        # test clear
        t, it, delete_str_nodes = setup()
        self.assertLength(t, 17)
        t.clear()
        self.assertLength(t, 0)
        self.assertFalse(t)
        # white box testing: remove lock, just so we can examine the repr
        t._lock = None
        self.assertEqual(repr(t), 'linked_list([])')
        for value in t: # pragma: nocover
            self.assertTrue(False) # shouldn't reach here!


        t, it, delete_str_nodes = setup()
        # keep references to every node, to keep the deleted nodes alive
        iterators = []
        while it:
            iterators.append(it)
            it = it.after()
        delete_str_nodes()
        t.clear()
        self.assertFalse(t)
        # white box testing: remove lock, just so we can examine the repr
        t._lock = None
        self.assertEqual(repr(t), 'linked_list([])')
        for value in t: # pragma: nocover
            self.assertTrue(False) # shouldn't reach here!


        t, it, delete_str_nodes = setup()
        self.assertLength(t, 17)
        self.assertEqual(t.pop(), 'j')
        self.assertLength(t, 16)
        self.assertEqual(t.pop(), 7)
        self.assertLength(t, 15)
        self.assertEqual(t.pop(), 'i')
        self.assertLength(t, 14)

        self.assertEqual(t.popleft(), 'a')
        self.assertLength(t, 13)
        self.assertEqual(t.popleft(), 1)
        self.assertLength(t, 12)
        self.assertEqual(t.popleft(), 'b')
        self.assertLength(t, 11)

        def setup():
            t = linked_list(range(10), lock=_lock())
            it = t.find(5)
            return t, it

        for i in range(10):
            with self.subTest(i=i):
                t, it = setup()
                self.assertEqual(t.pop(i), i)
                t, it = setup()
                self.assertEqual(t.popleft(i), i)

        for i in range(-5, 5):
            with self.subTest(i=i):
                t, it = setup()
                self.assertEqual(it.pop(i), i + 5)
                t, it = setup()
                self.assertEqual(it.rpop(i), i + 5)

        t, it = setup()
        with self.assertRaises(TypeError):
            t.pop('abc')
        with self.assertRaises(TypeError):
            t.popleft('abc')
        with self.assertRaises(TypeError):
            it.pop('abc')
        with self.assertRaises(TypeError):
            it.rpop('abc')

        t, it = setup()
        del it[0]
        with self.assertRaises(SpecialNodeError):
            it.pop(0)
        with self.assertRaises(SpecialNodeError):
            it.rpop(0)
        with self.assertRaises(SpecialNodeError):
            t.pop(len(t))
        with self.assertRaises(SpecialNodeError):
            t.popleft(-(len(t) + 1))



    def test_rich_compare(self):
        for _lock in self.lock_fns():
            self.rich_compare_tests(_lock)

    def rich_compare_tests(self, _lock):
        a        = linked_list([1, 2, 2], lock=_lock())
        b        = linked_list([1, 2, 3], lock=_lock())
        b_longer = linked_list([1, 2, 3, 4], lock=_lock())
        c        = linked_list([1, 2, 4], lock=_lock())
        pi       = 3.14159


        # __eq__

        self.assertTrue (a == a)
        self.assertFalse(a == b)
        self.assertFalse(a == b_longer)
        self.assertFalse(a == c)

        self.assertFalse(b == a)
        self.assertTrue (b == b)
        self.assertFalse(b == b_longer)
        self.assertFalse(b == c)

        self.assertFalse(b_longer == a)
        self.assertFalse(b_longer == b)
        self.assertTrue (b_longer == b_longer)
        self.assertFalse(b_longer == c)

        self.assertFalse(c == a)
        self.assertFalse(c == b)
        self.assertFalse(c == b_longer)
        self.assertTrue (c == c)

        self.assertFalse(a == pi)

        # __ne__
        self.assertFalse(a != a)
        self.assertTrue (a != b)
        self.assertTrue (a != b_longer)
        self.assertTrue (a != c)

        self.assertTrue (b != a)
        self.assertFalse(b != b)
        self.assertTrue (b != b_longer)
        self.assertTrue (b != c)

        self.assertTrue (b_longer != a)
        self.assertTrue (b_longer != b)
        self.assertFalse(b_longer != b_longer)
        self.assertTrue (b_longer != c)

        self.assertTrue (c != a)
        self.assertTrue (c != b)
        self.assertTrue (c != b_longer)
        self.assertFalse(c != c)

        self.assertTrue (a != pi)


        # __lt__
        self.assertFalse(a < a)
        self.assertTrue (a < b)
        self.assertTrue (a < b_longer)
        self.assertTrue (a < c)

        self.assertFalse(b < a)
        self.assertFalse(b < b)
        self.assertTrue (b < b_longer)
        self.assertTrue (b < c)

        self.assertFalse(b_longer < a)
        self.assertFalse(b_longer < b)
        self.assertFalse(b_longer < b_longer)
        self.assertTrue (b_longer < c)

        self.assertFalse(c < a)
        self.assertFalse(c < b)
        self.assertFalse(c < b_longer)
        self.assertFalse(c < c)

        with self.assertRaises(TypeError):
            a < pi


        # __le__
        self.assertTrue (a <= a)
        self.assertTrue (a <= b)
        self.assertTrue (a <= b_longer)
        self.assertTrue (a <= c)

        self.assertFalse(b <= a)
        self.assertTrue (b <= b)
        self.assertTrue (b <= b_longer)
        self.assertTrue (b <= c)

        self.assertFalse(b_longer <= a)
        self.assertFalse(b_longer <= b)
        self.assertTrue (b_longer <= b_longer)
        self.assertTrue (b_longer <= c)

        self.assertFalse(c <= a)
        self.assertFalse(c <= b)
        self.assertFalse(c <= b_longer)
        self.assertTrue (c <= c)

        with self.assertRaises(TypeError):
            a <= pi

        # __ge__
        self.assertTrue (a >= a)
        self.assertFalse(a >= b)
        self.assertFalse(a >= b_longer)
        self.assertFalse(a >= c)

        self.assertTrue (b >= a)
        self.assertTrue (b >= b)
        self.assertFalse(b >= b_longer)
        self.assertFalse(b >= c)

        self.assertTrue (b_longer >= a)
        self.assertTrue (b_longer >= b)
        self.assertTrue (b_longer >= b_longer)
        self.assertFalse(b_longer >= c)

        self.assertTrue (c >= a)
        self.assertTrue (c >= b)
        self.assertTrue (c >= b_longer)
        self.assertTrue (c >= c)

        with self.assertRaises(TypeError):
            a >= pi

        # __gt__
        self.assertFalse(a > a)
        self.assertFalse(a > b)
        self.assertFalse(a > b_longer)
        self.assertFalse(a > c)

        self.assertTrue (b > a)
        self.assertFalse(b > b)
        self.assertFalse(b > b_longer)
        self.assertFalse(b > c)

        self.assertTrue (b_longer > a)
        self.assertTrue (b_longer > b)
        self.assertFalse(b_longer > b_longer)
        self.assertFalse(b_longer > c)

        self.assertTrue (c > a)
        self.assertTrue (c > b)
        self.assertTrue (c > b_longer)
        self.assertFalse(c > c)

        with self.assertRaises(TypeError):
            a > pi

    def test___getitem__(self):
        for _lock in self.lock_fns():
            self.getitem_tests(_lock)

    def getitem_tests(self, _lock):
        # __getitem__ and slicing
        def setup():
            return linked_list((1, 2, 3, 4, 5), lock=_lock())

        a = setup()

        self.assertEqual(a[0], 1)
        self.assertEqual(a[1], 2)
        self.assertEqual(a[2], 3)
        self.assertEqual(a[3], 4)
        self.assertEqual(a[4], 5)

        self.assertEqual(a[-1], 5)
        self.assertEqual(a[-2], 4)
        self.assertEqual(a[-3], 3)
        self.assertEqual(a[-4], 2)
        self.assertEqual(a[-5], 1)

        with self.assertRaises(UndefinedIndexError):
            a[6]
        with self.assertRaises(UndefinedIndexError):
            a[-6]

        self.assertLinkedListEqual(a[0:3],      [1, 2, 3])
        self.assertLinkedListEqual(a[0:5:2],    [1, 3, 5])
        self.assertLinkedListEqual(a[-4:-1],    [2, 3, 4])
        self.assertLinkedListEqual(a[-1:-4:-1], [5, 4, 3])
        # rules are different for slices!
        # Python lists just clamps 'em for you.
        # so linked_list does too! YOU'RE WELCOME
        self.assertLinkedListEqual(a[9999:999999], [])
        self.assertLinkedListEqual(a[9999:999999:-1], [])

        copy_a = a.copy()
        copy_a[5:1:-2] = 'ab'
        self.assertLinkedListEqual(copy_a, [1, 2, 'b', 4, 'a'])

        copy_a = a.copy()
        copy_a[10000000000:-3239879817998:-2] = 'abc'
        self.assertLinkedListEqual(copy_a, ['c', 2, 'b', 4, 'a'])

        with self.assertRaises(TypeError):
            a[1.5:]
        with self.assertRaises(TypeError):
            a[:1.5]
        with self.assertRaises(TypeError):
            a[::1.5]
        with self.assertRaises(ValueError):
            a[::0]

        # Test linked_list slicing using a brute-force exhaustive test.
        # Construct a Python list of the numbers [1...count].
        # Construct a linked_list containing the same values.
        # Now slice into both objects with start, stop, and step
        # testing *every* combination of these values:
        #     [-23456789, -12345678, -(count + 1), ..., count + 1, 12345678, 23456789, None]
        # Confirm that the list and the linked_list produce identical results.
        for count in (0, 1, 3, 4, 8, 9):
            l = list(range(1, count + 1))
            t = linked_list(l, lock=_lock())

            values = (-23456789, -12345678,) + tuple(range(-(count + 1), count + 2)) + (12345678, 23456789, None)

            # Well... just one exception.
            # step can never be 0.
            # So, remove 0, just for step.
            # (But don't remove None!)
            values_without_zero = tuple(o for o in values if o != 0)

            for index in values:
                with self.subTest(index=index):
                    try:
                        l_value = l[index]
                        passed = True
                    except IndexError:
                        with self.assertRaises(IndexError):
                            t[index]
                        passed = False
                    except TypeError:
                        # reminder: None is in values
                        with self.assertRaises(TypeError):
                            t[index]
                        passed = False

                    if passed:
                        # don't merge this into the "try" block above,
                        # we want to notice if this raises IndexError
                        # but a list doesn't.
                        t_value = t[index]
                        self.assertEqual(l_value, t_value)

            for step in values_without_zero:
                for stop in values:
                    for start in values:
                        with self.subTest(count=count, start=start, stop=stop, step=step):
                            l_slice = l[start:stop:step]
                            t_slice = t[start:stop:step]

                            self.assertLinkedListEqual(t_slice, l_slice)

                            if (None not in (start, stop, step)) and (abs(stop - start) < 26):
                                elements = list(range(start, stop, step))
                                replacement = alphabet[:len(elements)]

                                l_copy = l.copy()
                                t_copy = t.copy()
                                try:
                                    l_copy[start:stop:step] = replacement
                                    t_copy[start:stop:step] = replacement
                                    self.assertLinkedListEqual(t_copy, l_copy)
                                except ValueError:
                                    pass

                            if step in (1, None):
                                l_copy = l.copy()
                                t_copy = t.copy()
                                l_copy[start:stop:step] = ('a', 'b', 'c')
                                t_copy[start:stop:step] = ('a', 'b', 'c')
                                self.assertLinkedListEqual(t_copy, l_copy)

        # __setitem__
        t = setup()
        t[2] = 'rem lezar'
        self.assertLinkedListEqual(t, (1, 2, 'rem lezar', 4, 5))
        self.assertNoSpecialNodes(t)

        # assign to slice with same number of elements
        t = setup()
        t[1:4] = 'abc'
        self.assertLinkedListEqual(t, (1, 'a', 'b', 'c', 5))
        self.assertNoSpecialNodes(t)

        # ... and with an iterator
        t = setup()
        t[1:4] = iter('abc')
        self.assertLinkedListEqual(t, (1, 'a', 'b', 'c', 5))
        self.assertNoSpecialNodes(t)

        # assign to slice with fewer elements
        t = setup()
        t = linked_list((1, 2, 3, 4, 5, 6, 7, 8, 9), lock=_lock())
        t[1:7] = 'ab'
        self.assertLinkedListEqual(t, (1, 'a', 'b', 8, 9))
        self.assertNoSpecialNodes(t)

        # ... and with an iterator
        t = setup()
        t = linked_list((1, 2, 3, 4, 5, 6, 7, 8, 9), lock=_lock())
        t[1:7] = iter('ab')
        self.assertLinkedListEqual(t, (1, 'a', 'b', 8, 9))
        self.assertNoSpecialNodes(t)

        # assign to slice with surplus elements
        t = setup()
        t[1:4] = 'abcdef'
        self.assertLinkedListEqual(t, (1, 'a', 'b', 'c', 'd', 'e', 'f', 5))
        self.assertNoSpecialNodes(t)

        # ... and with an iterator
        t = setup()
        t[1:4] = iter('abcdef')
        self.assertLinkedListEqual(t, (1, 'a', 'b', 'c', 'd', 'e', 'f', 5))
        self.assertNoSpecialNodes(t)

        t = setup()
        t[3:0:-1] = 'abc'
        self.assertLinkedListEqual(t, (1, 'c', 'b', 'a', 5))
        self.assertNoSpecialNodes(t)

        t = setup()
        t[3:0:-1] = iter('abc')
        self.assertLinkedListEqual(t, (1, 'c', 'b', 'a', 5))
        self.assertNoSpecialNodes(t)

        t = setup()
        t[0:5:2] = 'abc'
        self.assertLinkedListEqual(t, ('a', 2, 'b', 4, 'c'))
        self.assertNoSpecialNodes(t)

        t = setup()
        t[0:5:2] = iter('abc')
        self.assertLinkedListEqual(t, ('a', 2, 'b', 4, 'c'))
        self.assertNoSpecialNodes(t)

        t = setup()
        with self.assertRaises(TypeError):
            t[1:4] = 55
        with self.assertRaises(TypeError):
            t[1:4:2] = 55

        with self.assertRaises(ValueError):
            t[1:4:2] = 'abcdefgh'

        with self.assertRaises(ValueError):
            t[1:4] = t

        # overwrite a zero-length slice!
        t = setup()
        t[3:3] = []
        self.assertLinkedListEqual(t, [1, 2, 3, 4, 5])
        self.assertNoSpecialNodes(t)

        # __delitem__
        t = setup()
        del t[2]
        self.assertLinkedListEqual(t, (1, 2, 4, 5))
        self.assertNoSpecialNodes(t)

        t = setup()
        del t[1:4]
        self.assertLinkedListEqual(t, (1, 5))
        self.assertNoSpecialNodes(t)

        # none as initializer in slice
        t = setup()
        self.assertLinkedListEqual(t[:3], (1, 2, 3))
        self.assertLinkedListEqual(t[2:], (3, 4, 5))
        self.assertNoSpecialNodes(t)

        # and now--the iterator!
        def setup():
            t = linked_list(range(1, 10), lock=_lock())
            it = t.find(5)
            rit = reversed(it)
            return t, it, rit

        t, it, rit = setup()
        self.assertEqual(it[-1], 4)
        self.assertEqual(it[ 0], 5)
        self.assertEqual(it[ 1], 6)
        self.assertEqual(it[ 2], 7)
        self.assertLinkedListEqual(it[-1:3], [4, 5, 6, 7])

        # remove node pointed at by it
        rit.pop()
        # and now it raises
        with self.assertRaises(SpecialNodeError):
            it[-1:3]

        t, it, rit = setup()
        self.assertEqual(rit[-1], 6)
        self.assertEqual(rit[ 0], 5)
        self.assertEqual(rit[ 1], 4)
        self.assertEqual(rit[ 2], 3)
        self.assertLinkedListEqual(rit[-1:3], [6, 5, 4, 3])

        # remove node pointed at by rit
        it.pop()
        # and now it raises
        with self.assertRaises(SpecialNodeError):
            rit[-1:3]

        # the rules are different for slices *on iterators*.
        # for example--I *don't* clamp!  YOU'RE WELCOME.
        with self.assertRaises(ValueError):
            it[1:100]
        with self.assertRaises(ValueError):
            it[1000:2000]
        with self.assertRaises(ValueError):
            it[-100:2]
        with self.assertRaises(ValueError):
            it[-500:-100]

        with self.assertRaises(ValueError):
            rit[1:100]
        with self.assertRaises(ValueError):
            rit[1000:2000]
        with self.assertRaises(ValueError):
            rit[-100:2]
        with self.assertRaises(ValueError):
            rit[-500:-100]

        # when indexing into an *iterator*,
        # it[0] ALWAYS ALWAYS ALWAYS refers to the node
        # the iterator is currently pointing at.
        #
        # q: but what if it's pointing at a special node?
        # a: we raise an exception at you.
        t = linked_list(range(1, 10), lock=_lock())
        it = t.find(5)
        del it[0]

        with self.assertRaises(SpecialNodeError):
            it[0]
        with self.assertRaises(SpecialNodeError):
            it[0:1]
        with self.assertRaises(SpecialNodeError):
            it[-1:3]

        # regression: I had a bug where this returned [2, 4, 7, 9].
        # it should return [2, 4, 6, 8] as per the below.
        # note that it *doesn't* examine it[0], so it works fine.
        sl = it[-3:5:2]
        self.assertLinkedListEqual(it[-3:5:2], [2, 4, 6, 8])

        # iterator setitem too
        t, it, rit = setup()
        it[-1] = 'a'
        it[ 0] = 'b'
        it[ 1] = 'c'
        self.assertLinkedListEqual(t, [1, 2, 3, 'a', 'b', 'c', 7, 8, 9])
        self.assertNoSpecialNodes(t)

        t, it, rit = setup()
        rit[-1] = 'a'
        rit[ 0] = 'b'
        rit[ 1] = 'c'
        self.assertLinkedListEqual(t, [1, 2, 3, 'c', 'b', 'a', 7, 8, 9])
        self.assertNoSpecialNodes(t)

        # assign to slice with the same number of values as items in the slice
        t, it, rit = setup()
        it[-1:3] = 'abcd'
        self.assertLinkedListEqual(t, [1, 2, 3, 'a', 'b', 'c', 'd', 8, 9])
        self.assertNoSpecialNodes(t)

        # assign to slice with the same number of values as items in the slice
        t, it, rit = setup()
        it[-1:4] = 'ab'
        self.assertLinkedListEqual(t, [1, 2, 3, 'a', 'b', 9])
        self.assertNoSpecialNodes(t)

        # assign to slice with more values than items in the slice
        t, it, rit = setup()
        it[-1:1] = 'abcde'
        self.assertLinkedListEqual(t, [1, 2, 3, 'a', 'b', 'c', 'd', 'e', 6, 7, 8, 9])
        self.assertNoSpecialNodes(t)

        # white box testing:
        # also do it with an iterator, rather than a string,
        # because that forces us internally to cast to a list
        t, it, rit = setup()
        it[-1:1] = iter('abcde')
        self.assertLinkedListEqual(t, [1, 2, 3, 'a', 'b', 'c', 'd', 'e', 6, 7, 8, 9])
        self.assertNoSpecialNodes(t)

        # assign correctly to "extended slice"
        t, it, rit = setup()
        it2 = t.find(2)
        it4 = t.find(4)
        it6 = t.find(6)
        it2[0:6:2] = 'abc'
        self.assertLinkedListEqual(t, [1, 'a', 3, 'b', 5, 'c', 7, 8, 9])
        # and the iterators don't move
        self.assertEqual(it2[0], 'a')
        self.assertEqual(it4[0], 'b')
        self.assertEqual(it6[0], 'c')
        self.assertNoSpecialNodes(t)

        # assign too many values to an "extended slice"
        t, it, rit = setup()
        it = t.find(1)
        with self.assertRaises(ValueError):
            it[0:6:2] = 'abcdefghijkl'
        # and too few
        with self.assertRaises(ValueError):
            it[0:6:2] = 'ab'

        # now... reversed!
        # assign to slice with the same number of values as items in the slice
        t, it, rit = setup()
        rit[-1:3] = 'abcd'
        self.assertLinkedListEqual(t, [1, 2, 'd', 'c', 'b', 'a', 7, 8, 9])
        self.assertNoSpecialNodes(t)

        # assign to slice with the same number of values as items in the slice
        t, it, rit = setup()
        rit[-1:4] = 'ab'
        self.assertLinkedListEqual(t, [1, 'b', 'a', 7, 8, 9])
        self.assertNoSpecialNodes(t)

        # assign to slice with more values than items in the slice
        t, it, rit = setup()
        rit[-1:1] = 'abcde'
        self.assertLinkedListEqual(t, [1, 2, 3, 4, 'e', 'd', 'c', 'b', 'a', 7, 8, 9])
        self.assertNoSpecialNodes(t)

        t, it, rit = setup()
        with self.assertRaises(ValueError):
            it[0:8:2] = 'abcdefghijkl'

        # assign correctly to "extended slice"
        t, it, rit = setup()
        it8 = reversed(t.find(8))
        it6 = reversed(t.find(6))
        it4 = reversed(t.find(4))
        it8[0:6:2] = 'abc'
        self.assertLinkedListEqual(t, [1, 2, 3, 'c', 5, 'b', 7, 'a', 9])
        # and the iterators don't move
        self.assertEqual(it8[0], 'a')
        self.assertEqual(it6[0], 'b')
        self.assertEqual(it4[0], 'c')
        self.assertNoSpecialNodes(t)

        # assign too many values to an "extended slice"
        t, it, rit = setup()
        it = t.find(8)
        rit = reversed(it)
        with self.assertRaises(ValueError):
            rit[0:6:2] = 'abcdefghijkl'
        # and too few
        with self.assertRaises(ValueError):
            rit[0:6:2] = 'ab'

        # test zero-length slices of iterators
        # len t is 9, it points to 5.
        # confirm the invariants for these tests:
        t, it, rit = setup()
        self.assertEqual(len(t), 9)
        self.assertEqual(it[0], 5)
        for i in range(-4, 5):
            with self.subTest(i=i):
                t, it, rit = setup()
                self.assertLinkedListEqual(it[i:i], [])
                self.assertLinkedListEqual(it[i:i:-1], [])
                self.assertLinkedListEqual(rit[i:i], [])
                self.assertLinkedListEqual(rit[i:i:-1], [])

                t, it, rit = setup()
                l = list(t)
                it[i:i] = ['a', 'b', 'c']
                l[i+5:i+5] = ['a', 'b', 'c']
                self.assertLinkedListEqual(t, l)

                t, it, rit = setup()
                l = list(t)
                rit[i:i] = ['a', 'b', 'c']
                l[4-i:4-i] = ['c', 'b', 'a']
                self.assertLinkedListEqual(t, l)

        # you can't assign slices to head or tail, neither
        t, it, rit = setup()
        it = t.head()
        rit = reversed(it)
        with self.assertRaises(UndefinedIndexError):
            rit[0:0] = 'abc'
        with self.assertRaises(UndefinedIndexError):
            it[0:0] = 'abc'

        t, it, rit = setup()
        it = t.tail()
        rit = reversed(it)
        with self.assertRaises(UndefinedIndexError):
            it[0:0] = 'abc'
        with self.assertRaises(UndefinedIndexError):
            rit[0:0] = 'abc'

        # you can't assign self to a slice of self
        with self.assertRaises(ValueError):
            it[1:3] = t
        with self.assertRaises(ValueError):
            rit[1:3] = t

        # indices must be, y'know, __index__-icies
        with self.assertRaises(TypeError):
            t['abc']
        with self.assertRaises(TypeError):
            it['abc']
        with self.assertRaises(TypeError):
            rit['abc']
        with self.assertRaises(TypeError):
            t['abc'] = 5
        with self.assertRaises(TypeError):
            it['abc'] = 6
        with self.assertRaises(TypeError):
            rit['abc'] = 7
        with self.assertRaises(TypeError):
            del t['abc']
        with self.assertRaises(TypeError):
            del it['abc']
        with self.assertRaises(TypeError):
            del rit['abc']
        with self.assertRaises(TypeError):
            t['abc':1]
        with self.assertRaises(TypeError):
            it['abc':1]
        with self.assertRaises(TypeError):
            rit['abc':1]
        with self.assertRaises(TypeError):
            t[1:'abc']
        with self.assertRaises(TypeError):
            it[1:'abc']
        with self.assertRaises(TypeError):
            rit[1:'abc']
        with self.assertRaises(TypeError):
            t[1:2:'abc']
        with self.assertRaises(TypeError):
            it[1:2:'abc']
        with self.assertRaises(TypeError):
            rit[1:2:'abc']
        with self.assertRaises(TypeError):
            t['abc':'def'] = [1, 2, 3]
        with self.assertRaises(TypeError):
            it['abc':'def'] = [1, 2, 3]
        with self.assertRaises(TypeError):
            rit['abc':'def'] = [1, 2, 3]
        with self.assertRaises(TypeError):
            del t['abc':'def']
        with self.assertRaises(TypeError):
            del it['abc':'def']
        with self.assertRaises(TypeError):
            del rit['abc':'def']

        with self.assertRaises(ValueError):
            t[1:2:0]
        with self.assertRaises(ValueError):
            it[1:2:0]
        with self.assertRaises(ValueError):
            rit[1:2:0]
        with self.assertRaises(ValueError):
            t[1:2:0] = 'abc'
        with self.assertRaises(ValueError):
            it[1:2:0] = 'abc'
        with self.assertRaises(ValueError):
            rit[1:2:0] = 'abc'
        with self.assertRaises(ValueError):
            del t[1:2:0]
        with self.assertRaises(ValueError):
            del it[1:2:0]
        with self.assertRaises(ValueError):
            del rit[1:2:0]

        # finally, iterator delitem, with slices
        t, it, rit = setup()
        del it[-1]
        self.assertLinkedListEqual(t, [1, 2, 3,    5, 6, 7, 8, 9])
        self.assertNoSpecialNodes(t)
        t, it, rit = setup()
        del it[ 0]
        self.assertLinkedListEqual(t, [1, 2, 3, 4,    6, 7, 8, 9])
        t, it, rit = setup()
        del it[ 1]
        self.assertLinkedListEqual(t, [1, 2, 3, 4, 5,    7, 8, 9])
        self.assertNoSpecialNodes(t)
        t, it, rit = setup()
        del it[-1:3]
        self.assertLinkedListEqual(t, [1, 2, 3,             8, 9])

        t, it, rit = setup()
        del rit[-1]
        self.assertLinkedListEqual(t, [1, 2, 3, 4, 5,    7, 8, 9])
        self.assertNoSpecialNodes(t)
        t, it, rit = setup()
        del rit[ 0]
        self.assertLinkedListEqual(t, [1, 2, 3, 4,    6, 7, 8, 9])
        t, it, rit = setup()
        del rit[ 1]
        self.assertLinkedListEqual(t, [1, 2, 3,    5, 6, 7, 8, 9])
        self.assertNoSpecialNodes(t)
        t, it, rit = setup()
        del rit[-1:3]
        self.assertLinkedListEqual(t, [1, 2,             7, 8, 9])


    def test_misc_methods(self):
        for _lock in self.lock_fns():
            self.misc_methods_tests(_lock)

    def misc_methods_tests(self, _lock):
        # sort
        l = [5, 20, -3, 3, 44, 4, 3, 6, 8, 3, 8]
        t = linked_list(l, lock=_lock())
        l.sort()
        t.sort()
        self.assertLinkedListEqual(t, l)

        # reverse
        l.reverse()
        t.reverse()
        self.assertLinkedListEqual(t, l)

        l.append(88)
        t.append(88)
        l.reverse()
        t.reverse()
        self.assertLinkedListEqual(t, l)


        # count
        for v in l:
            self.assertEqual(t.count(v), l.count(v))

        # insert
        for index in range(-7, 7):
            with self.subTest(index=index):
                a = [1, 2, 3, 4, 5]
                a.insert(index, 'x')
                t = linked_list((1, 2, 3, 4, 5), lock=_lock())
                t.insert(index, 'x')
                self.assertLinkedListEqual(t, a)

        with self.assertRaises(TypeError):
            t.insert('this is not a valid index', 'abc')

        with self.assertRaises(TypeError):
            t.insert(0, )

        # regression: reverse crashed if t was empty
        t = linked_list(lock=_lock())
        t.reverse()
        self.assertLinkedListEqual(t, [])

        l = []
        for i in range(1, 10):
            t.append(i)
            l.append(i)
            t.reverse()
            l.reverse()
            self.assertLinkedListEqual(t, l)

        # rotate
        initializer = ('x', 2, 3, 4, 5, 6, 7, 8, 9)
        d = collections.deque(initializer)
        t = linked_list(d, lock=_lock())

        for i in range(-10, 11):
            t_copy = t.copy()
            t_copy.rotate(i)
            d_copy = d.copy()
            d_copy.rotate(i)
            self.assertEqual(list(t_copy), list(d_copy))

        with self.assertRaises(TypeError):
            t.rotate(3.14159)

        # rremove
        t2 = t * 2
        t2.rremove(2)
        self.assertLinkedListEqual(t2, ('x', 2, 3, 4, 5, 6, 7, 8, 9, 'x', 3, 4, 5, 6, 7, 8, 9))
        with self.assertRaises(ValueError):
            t2.rremove('abx')
        self.assertEqual(t2.rremove('abz', 45), 45)

        # iterator rremove
        it = reversed(reversed(t2)) # it is a forwards iterator pointed at tail!
        it.rremove(4)
        self.assertLinkedListEqual(t2, ('x', 2, 3, 4, 5, 6, 7, 8, 9, 'x', 3, 5, 6, 7, 8, 9))
        with self.assertRaises(ValueError):
            it.rremove('abx')
        self.assertEqual(it.rremove('abz', 77), 77)

        # by using the one in big.types,
        # we get the real one in 3.9+
        # and the fake one for 3.7-3.8
        linked_list_int = big.types.GenericAlias(linked_list, (int,))
        if python_version >= Version("3.7"): # pragma: nocover
            self.assertEqual(linked_list[int], linked_list_int)
        else: # pragma: nocover
            self.assertEqual(linked_list_int, 'linked_list[int]')

    def test_misc_dunder_methods(self):
        for _lock in self.lock_fns():
            self.misc_dunder_methods_test(_lock)

        t = linked_list('a')
        self.assertEqual(repr(t), "linked_list(['a'])")

        class FakeLock:
            def ignore(self, *a, **kw):
                pass
            acquire = release = __enter__ = __exit__ = ignore
            def __repr__(self):
                return '<FakeLock>'
        t = linked_list('a', lock=FakeLock())
        self.assertEqual(repr(t), "linked_list(['a'], lock=<FakeLock>)")

    def misc_dunder_methods_test(self, _lock):
        t = linked_list((1, 2, 3, 4, 5), lock=_lock())

        # __deepcopy__
        t1 = linked_list(({1:2}, {3:4}))
        t2 = copy.deepcopy(t1)
        self.assertEqual(t1, t2)
        for v1, v2 in zip(t1, t2):
            self.assertEqual(v1, v2)
            self.assertFalse(v1 is v2)

        # __add__
        t1 = linked_list((1, 2, 3))
        t2 = linked_list((4, 5, 6))
        t3 = t1 + t2
        self.assertLinkedListEqual(t3, (1, 2, 3, 4, 5, 6))

        # __iadd__
        t1 = linked_list((1, 2, 3))
        t2 = linked_list((4, 5, 6))
        t2 += t1
        self.assertLinkedListEqual(t2, (4, 5, 6, 1, 2, 3))

        # __mul__
        t4 = t1 * 3
        self.assertLinkedListEqual(t4, (1, 2, 3, 1, 2, 3, 1, 2, 3))
        with self.assertRaises(TypeError):
            t1 * [3,4]
        with self.assertRaises(TypeError):
            t1 * 2+1j
        t4 = t1 * 0
        self.assertLinkedListEqual(t4, [])

        # __imul__
        t5 = t1
        t5 *= 4
        self.assertLinkedListEqual(t5, (1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3))
        with self.assertRaises(TypeError):
            t5 *= [3,4]
        with self.assertRaises(TypeError):
            t5 *= 2+1j
        t5 *= 0
        self.assertLinkedListEqual(t5, [])

        # __contains__
        self.assertIn(3, t)
        self.assertNotIn('x', t)

    def test_misc_iterator_methods(self):
        for _lock in self.lock_fns():
            self.misc_iterator_methods_test(_lock)

    def misc_iterator_methods_test(self, _lock):
        def setup():
            t = linked_list(range(1, 11), lock=_lock())
            it = t.find(5)
            return t, it

        # __contains__
        t, it = setup()
        self.assertIn(7, it)
        self.assertNotIn(3, it)
        self.assertNotIn('x', it)

        # __copy__
        it2 = it.copy()
        self.assertEqual(it, it2)
        it3 = copy.copy(it)
        self.assertEqual(it, it3)

        self.assertIs(t, it.linked_list)

        # next and previous
        with self.assertRaises(TypeError):
            it.next(count=5.5)
        with self.assertRaises(ValueError):
            it.next(count=-5)
        with self.assertRaises(TypeError):
            it.previous(count=5.5)
        with self.assertRaises(ValueError):
            it.previous(count=-5)

        it = t.find(5)
        self.assertEqual(it[0], 5)
        it.next(count=0)
        self.assertEqual(it[0], 5)
        it.next(count=3)
        self.assertEqual(it[0], 8)
        it = t.find(5)
        it.next(None, count=3)
        self.assertEqual(it[0], 8)

        it = t.find(5)
        self.assertEqual(it[0], 5)
        it.previous(count=0)
        self.assertEqual(it[0], 5)
        it.previous(count=3)
        self.assertEqual(it[0], 2)
        it = t.find(5)
        it.previous(None, count=3)
        self.assertEqual(it[0], 2)

        it = t.tail()
        self.assertIsTail(it)
        with self.assertRaises(StopIteration):
            it.next()
        self.assertIsTail(it)
        got = it.next('abc')
        self.assertIsTail(it)
        self.assertEqual(got, 'abc')

        it = t.head()
        self.assertIsHead(it)
        with self.assertRaises(StopIteration):
            it.previous()
        self.assertIsHead(it)
        got = it.previous('xyz')
        self.assertIsHead(it)
        self.assertEqual(got, 'xyz')

        t, it = setup()
        self.assertEqual(it[0], 5)

        with self.assertRaises(TypeError):
            it2 = it.before(3.14159)
        with self.assertRaises(ValueError):
            it2 = it.before(-1)
        it2 = it.before(4)
        self.assertEqual(it2[0], 1)
        it3 = it.before(5)
        self.assertIsHead(it3)

        with self.assertRaises(TypeError):
            it2 = it.after(3.14159)
        with self.assertRaises(ValueError):
            it2 = it.after(-1)
        it4 = it.after(4)
        self.assertEqual(it4[0], 9)
        it5 = it.after(6)
        self.assertIsTail(it5)

        t, it = setup()
        self.assertLinkedListEqual(t, [1, 2, 3, 4,   5,  6,   7, 8, 9, 10])
        it[0] = 'x'
        self.assertLinkedListEqual(t, [1, 2, 3, 4, 'x',  6,   7, 8, 9, 10])
        del it[0]
        self.assertLinkedListEqual(t, [1, 2, 3, 4,       6,   7, 8, 9, 10])
        it[2] = 'z'
        self.assertLinkedListEqual(t, [1, 2, 3, 4,       6, 'z', 8, 9, 10])
        del it[2]
        self.assertLinkedListEqual(t, [1, 2, 3, 4,       6,      8, 9, 10])

        t = linked_list((1, 'x', 2, 'x', 3, 'x', 4, 'x', 5, 'x', 6, 'x', 7, 'x', 8), lock=_lock())
        it = t.find(5)
        self.assertEqual(it.count('x'), 3)
        self.assertEqual(it.rcount('x'), 4)

        t, it = setup()
        it.insert(3, 'zz')
        self.assertLinkedListEqual(t, [1, 2, 3, 4, 5, 6, 7, 'zz', 8, 9, 10])
        it.insert(-2, 'qq')
        self.assertLinkedListEqual(t, [1, 2, 'qq', 3, 4, 5, 6, 7, 'zz', 8, 9, 10])
        it = t.head()
        with self.assertRaises(UndefinedIndexError):
            it.insert(0, 'xx')
        it = t.tail()
        it.insert(0, 'yy')
        self.assertLinkedListEqual(t, [1, 2, 'qq', 3, 4, 5, 6, 7, 'zz', 8, 9, 10, 'yy'])
        it = t.find(10)
        it.insert(0, 'oo')
        self.assertLinkedListEqual(t, [1, 2, 'qq', 3, 4, 5, 6, 7, 'zz', 8, 9, 'oo', 10, 'yy'])

    def test_truncate(self):
        for _lock in self.lock_fns():
            self.truncate_tests(_lock)

    def truncate_tests(self, _lock):
        def setup():
            t = linked_list(range(1, 11), lock=_lock())
            it_5 = t.find(5)
            t2 = linked_list('abcde', lock=_lock())
            return t, it_5, t2

        # truncate no nodes
        t, it_5, t2 = setup()
        self.assertEqual(len(t), 10)
        it = t.tail()
        it.truncate()
        self.assertLinkedListEqual(t, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(len(t), 10)
        self.assertTrue(t)
        self.assertIsTail(it)

        t, it_5, t2 = setup()
        it = t.head()
        it.rtruncate()
        self.assertLinkedListEqual(t, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(len(t), 10)
        self.assertTrue(t)
        self.assertIsHead(it)

        # truncate all the nodes!
        t, it_5, t2 = setup()
        it = t.find(1)
        it.truncate()
        self.assertLinkedListEqual(t, [])
        self.assertEqual(len(t), 0)
        self.assertFalse(t)
        self.assertIsTail(it)

        t, it_5, t2 = setup()
        it = t.find(10)
        it.rtruncate()
        self.assertLinkedListEqual(t, [])
        self.assertEqual(len(t), 0)
        self.assertFalse(t)
        self.assertIsHead(it)

        # can't truncate head
        t, it_5, t2 = setup()
        it = t.head()
        with self.assertRaises(SpecialNodeError):
            it.truncate()
        # can't rtruncate a reverse iterator pointing at head.
        # (say *that* three times fast!)
        rit = reversed(it)
        with self.assertRaises(SpecialNodeError):
            rit.rtruncate()

        # rtruncating at "tail" is the same as truncating at the last data node.
        t, it_5, t2 = setup()
        it = t.tail()
        with self.assertRaises(SpecialNodeError):
            it.rtruncate()
        # can't truncate a reverse iterator pointing at tail.
        rit = reversed(it)
        with self.assertRaises(SpecialNodeError):
            rit.truncate()

        # truncate some nodes, ensuring we have an iterator
        # pointing to one of the nodes we throw away
        t, it_5, t2 = setup()
        it_7 = t.find(7)
        it_5.truncate()
        self.assertLinkedListEqual(t, [1, 2, 3, 4])
        self.assertEqual(len(t), 4)
        self.assertTrue(t)
        self.assertIsTail(it_5)

        t, it_5, t2 = setup()
        it_2 = t.find(2)
        it_5.rtruncate()
        self.assertLinkedListEqual(t, [6, 7, 8, 9, 10])
        self.assertEqual(len(t), 5)
        self.assertTrue(t)
        self.assertIsHead(it_5)


    def test_cut_and_splice(self):
        for _lock in self.lock_fns():
            self.cut_and_splice_tests(_lock)

        # splicing from a list WITH a lock
        # into a list WITHOUT a lock
        t = linked_list([1, 2, 3, 4, 5])
        it = t.find(3)
        t2 = linked_list('abc', lock=Lock())

        it.splice(t2)
        self.assertLinkedListEqual(t, [1, 2, 3, 'a', 'b', 'c', 4, 5])
        self.assertLinkedListEqual(t2, [])

        # splice has special code to ensure
        # we always lock the locks in increasing
        # order of id.  we gotta ensure we test
        # both orderings.
        lock1 = Lock()
        lock2 = Lock()
        def setup(lock1, lock2):
            t = linked_list([1, 2, 3, 4, 5], lock=lock1)
            it = t.find(3)
            t2 = linked_list('abc', lock=lock2)
            return t, it, t2
        for (lock1, lock2) in (
            (lock1, lock2),
            (lock2, lock1),
            ):
            with self.subTest(lock1=lock1, lock2=lock2):
                t, it, t2 = setup(lock1, lock2)
                t.splice(t2)
                self.assertLinkedListEqual(t, [1, 2, 3, 4, 5, 'a', 'b', 'c'])

                t, it, t2 = setup(lock1, lock2)
                t.splice(t2, where=it)
                self.assertLinkedListEqual(t, [1, 2, 3, 'a', 'b', 'c', 4, 5])

                t, it, t2 = setup(lock1, lock2)
                it.splice(t2)
                self.assertLinkedListEqual(t, [1, 2, 3, 'a', 'b', 'c', 4, 5])


    def cut_and_splice_tests(self, _lock):
        def setup():
            t = linked_list(range(1, 11), lock=_lock())
            it_5 = t.find(5)
            t2 = linked_list('abcde', lock=_lock())
            return t, it_5, t2

        def check_linked_list_was_set(t):
            it = iter(t)
            self.assertIsHead(it)
            self.assertIs(it.linked_list, t, "failed on t.head")
            for _ in it:
                self.assertIs(it.linked_list, t, f"failed on it={it!r}")
            self.assertIsTail(it)
            self.assertIs(it.linked_list, t, "failed on t.tail")

        # splicing an empty linked_list does nothing
        t, it_5, t2 = setup()
        t_list = list(t)

        t2 = linked_list()
        t.splice(t2)
        self.assertLinkedListEqual(t, t_list)
        it_5.splice(t2)
        self.assertLinkedListEqual(t, t_list)
        rit = reversed(it_5)
        rit.splice(t2)
        self.assertLinkedListEqual(t, t_list)

        t2 = linked_list()
        t.rsplice(t2)
        self.assertLinkedListEqual(t, t_list)
        it_5.rsplice(t2)
        self.assertLinkedListEqual(t, t_list)
        rit = reversed(it_5)
        rit.rsplice(t2)
        self.assertLinkedListEqual(t, t_list)

        # can't splice t into t
        with self.assertRaises(ValueError):
            t.splice(t)
        with self.assertRaises(ValueError):
            t.rsplice(t)
        with self.assertRaises(ValueError):
            it_5.splice(t)
        with self.assertRaises(ValueError):
            it_5.rsplice(t)


        # on a forward iterator, can't cut head
        t, it_5, t2 = setup()
        it_head = iter(t)
        with self.assertRaises(SpecialNodeError):
            it_head.cut()
        with self.assertRaises(SpecialNodeError):
            t.cut(it_head, None)

        # on a reversed iterator, can't cut tail
        rit_tail = reversed(t)
        with self.assertRaises(SpecialNodeError):
            rit_tail.cut()
        with self.assertRaises(SpecialNodeError):
            t.cut(rit_tail)

        # on a forward iterator, can't rcut tail
        t, it_5, t2 = setup()
        it_tail = t.tail()
        with self.assertRaises(SpecialNodeError):
            it_tail.rcut()
        with self.assertRaises(SpecialNodeError):
            t.rcut(it_tail, None)

        # on a reverse iterator, can't rcut head
        t, it_5, t2 = setup()
        rit_head = reversed(t.head())
        with self.assertRaises(SpecialNodeError):
            rit_head.rcut()
        with self.assertRaises(SpecialNodeError):
            t.rcut(rit_head, None)

        with self.assertRaises(TypeError):
            t.cut(5, None)
        with self.assertRaises(TypeError):
            t.cut(None, 5)
        with self.assertRaises(TypeError):
            t.rcut(5, None)
        with self.assertRaises(TypeError):
            t.rcut(None, 5)

        # if start and stop both point to head,
        # cut returns an empty list.
        unchanged_t = list(t)
        head = t.head()

        got = t.cut(head, head, lock=_lock())
        self.assertLinkedListEqual(t, unchanged_t)
        self.assertLinkedListEqual(got, [])

        got = head.cut(head, lock=_lock())
        self.assertLinkedListEqual(t, unchanged_t)
        self.assertLinkedListEqual(got, [])

        head = reversed(head)
        got = t.cut(head, head, lock=_lock())
        self.assertLinkedListEqual(t, unchanged_t)
        self.assertLinkedListEqual(got, [])

        got = head.cut(head, lock=_lock())
        self.assertLinkedListEqual(t, unchanged_t)
        self.assertLinkedListEqual(got, [])

        # if start and stop both point to tail,
        # cut returns an empty list.
        tail = t.tail()

        got = t.cut(tail, tail, lock=_lock())
        self.assertLinkedListEqual(t, unchanged_t)
        self.assertLinkedListEqual(got, [])

        got = tail.cut(tail, lock=_lock())
        self.assertLinkedListEqual(t, unchanged_t)
        self.assertLinkedListEqual(got, [])

        tail = reversed(tail)
        got = t.cut(tail, tail, lock=_lock())
        self.assertLinkedListEqual(t, unchanged_t)
        self.assertLinkedListEqual(got, [])

        got = tail.cut(tail, lock=_lock())
        self.assertLinkedListEqual(t, unchanged_t)
        self.assertLinkedListEqual(got, [])


        t, it_5, t2 = setup()
        snippet = it_5.cut(lock=_lock())
        self.assertIsInstance(snippet, linked_list)
        self.assertLinkedListEqual(t,       [1, 2, 3, 4])
        self.assertEqual(len(t), 4)
        self.assertLinkedListEqual(snippet,             [5, 6, 7, 8, 9, 10])
        self.assertEqual(len(snippet), 6)
        check_linked_list_was_set(t)
        check_linked_list_was_set(snippet)

        for test_reversed in (False, True):
            for splice_at_tail in (False, True):
                with self.subTest(test_reversed=test_reversed, splice_at_tail=splice_at_tail):
                    t, it_5, t2 = setup()
                    it_7 = t.find(7)

                    snippet = it_5.cut(stop=it_7, lock=_lock())
                    self.assertIsInstance(snippet, linked_list)
                    self.assertLinkedListEqual(snippet, [5, 6])
                    self.assertEqual(len(snippet), 2)
                    self.assertLinkedListEqual(t, [1, 2, 3, 4, 7, 8, 9, 10])
                    self.assertEqual(len(t), 8)
                    check_linked_list_was_set(t)
                    check_linked_list_was_set(snippet)

                    if splice_at_tail:
                        if test_reversed:
                            splice_here = reversed(t2)
                        else:
                            splice_here = iter(t2)
                        splice_here.exhaust()
                    else:
                        splice_here = t2.find('c')
                        if test_reversed:
                            splice_here = reversed(splice_here)
                        self.assertEqual(splice_here[0], 'c')

                    splice_here.splice(snippet)
                    self.assertLinkedListEqual(snippet, [])

                    if splice_at_tail:
                        if test_reversed:
                            self.assertLinkedListEqual(t2, [5, 6, 'a', 'b', 'c', 'd', 'e'])
                        else:
                            self.assertLinkedListEqual(t2, ['a', 'b', 'c', 'd', 'e', 5, 6])

                        self.assertIsSpecial(splice_here)
                    else:
                        if test_reversed:
                            self.assertLinkedListEqual(t2, ['a', 'b', 5, 6, 'c', 'd', 'e'])
                        else:
                            self.assertLinkedListEqual(t2, ['a', 'b', 'c', 5, 6, 'd', 'e'])
                    check_linked_list_was_set(t)
                    check_linked_list_was_set(t2)
                    self.assertEqual(len(t2), 7)
                    self.assertEqual(len(snippet), 0)


        t, it_5, t2 = setup()
        rit_5 = reversed(it_5)
        snippet = rit_5.cut(lock=_lock())
        self.assertIsInstance(snippet, linked_list)
        self.assertLinkedListEqual(snippet, [1, 2, 3, 4,  5])
        self.assertEqual(len(snippet), 5)
        self.assertLinkedListEqual(t,                       [6, 7, 8, 9, 10])
        self.assertEqual(len(t), 5)
        check_linked_list_was_set(t)
        check_linked_list_was_set(snippet)

        t2.splice(snippet)
        self.assertLinkedListEqual(snippet, [])
        self.assertEqual(len(snippet), 0)
        self.assertLinkedListEqual(t2, ['a', 'b', 'c', 'd', 'e', 1, 2, 3, 4, 5])
        self.assertEqual(len(t2), 10)
        check_linked_list_was_set(t)
        check_linked_list_was_set(t2)
        check_linked_list_was_set(snippet)

        t, it_5, t2 = setup()
        rit_5 = reversed(it_5)
        it_2 = t.find(2)
        with self.assertRaises(ValueError):
            rit_5.cut(it_2)
        rit_2 = reversed(it_2)
        snippet = rit_5.cut(rit_2, lock=_lock())
        self.assertLinkedListEqual(t,       [1, 2,         6, 7, 8, 9, 10])
        self.assertEqual(len(t), 7)
        self.assertLinkedListEqual(snippet,       [3, 4, 5])
        self.assertEqual(len(snippet), 3)
        check_linked_list_was_set(t)
        check_linked_list_was_set(snippet)

        # rit moved to snippet when the nodes were cut.  which means
        # these calls raise an exception! which means NOTHING CHANGED, RIGHT?
        with self.assertRaises(ValueError):
            t.cut(rit_5)
        with self.assertRaises(ValueError):
            t.cut(stop=rit_5)
        self.assertLinkedListEqual(t,       [1, 2,         6, 7, 8, 9, 10])
        self.assertEqual(len(t), 7)
        self.assertLinkedListEqual(snippet,       [3, 4, 5])
        self.assertEqual(len(snippet), 3)
        check_linked_list_was_set(t)
        check_linked_list_was_set(snippet)

        it = t.head().after()
        t2 = t.cut(stop=it, lock=_lock())
        self.assertEqual(len(t), 7)
        self.assertLinkedListEqual(t2, [])
        self.assertEqual(len(t2), 0)

        t, it_5, t2 = setup()
        it_2 = t.find(2)
        with self.assertRaises(ValueError):
            # end comes before start
            t.cut(it_5, it_2)
        rit_5 = reversed(it_5)
        rit_2 = reversed(it_2)
        with self.assertRaises(ValueError):
            # end comes before start
            t.cut(rit_2, rit_5)

        t, it_5, t2 = setup()
        snippet = it_5.rcut(lock=_lock())
        self.assertLinkedListEqual(t,       [6, 7, 8, 9, 10])
        self.assertEqual(len(t), 5)
        self.assertLinkedListEqual(snippet, [1, 2, 3, 4, 5])
        self.assertEqual(len(snippet), 5)
        self.assertIs(it_5.linked_list, snippet)
        check_linked_list_was_set(t)
        check_linked_list_was_set(snippet)

        t, it_5, t2 = setup()
        it = t.tail().before()
        snippet = it.rcut(lock=_lock())
        self.assertLinkedListEqual(t,       [])
        self.assertEqual(len(t), 0)
        self.assertLinkedListEqual(snippet, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(len(snippet), 10)
        self.assertIs(it.linked_list, snippet)
        check_linked_list_was_set(t)
        check_linked_list_was_set(snippet)

        with self.assertRaises(TypeError):
            t.splice([1, 2, 3])
        with self.assertRaises(TypeError):
            t.splice('abcde')
        with self.assertRaises(TypeError):
            t.splice(8675309)
        with self.assertRaises(TypeError):
            t.splice(3.14159)

        with self.assertRaises(TypeError):
            t.splice(t2, where=1234567890)
        with self.assertRaises(TypeError):
            t.splice(t2, where=t2)
        with self.assertRaises(ValueError):
            t.splice(t2, where=t2.head())

        with self.assertRaises(TypeError):
            it.splice([1, 2, 3])
        with self.assertRaises(TypeError):
            it.splice('abcde')
        with self.assertRaises(TypeError):
            it.splice(8675309)
        with self.assertRaises(TypeError):
            it.splice(3.14159)

        t, it_5, t2 = setup()
        t2_tail = t2.tail()
        t.splice(t2)
        check_linked_list_was_set(t)
        self.assertEqual(len(t), 15)
        self.assertEqual(len(t2), 0)

        with self.assertRaises(ValueError):
            t.splice(t)

        # rsplice without where
        t, it_5, t2 = setup()
        t.rsplice(t2)
        self.assertLinkedListEqual(t, ['a', 'b', 'c', 'd', 'e', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        # reverse iterator splice and rsplice
        t, it_5, t2 = setup()
        rit = reversed(it_5)
        rit.splice(t2)
        self.assertLinkedListEqual(t, [1, 2, 3, 4, 'a', 'b', 'c', 'd', 'e', 5, 6, 7, 8, 9, 10])

        t, it_5, t2 = setup()
        rit = reversed(it_5)
        rit.rsplice(t2)
        self.assertLinkedListEqual(t, [1, 2, 3, 4, 5, 'a', 'b', 'c', 'd', 'e', 6, 7, 8, 9, 10])

        # splice does NOT move head and tail.
        t = linked_list(lock=_lock())
        t2 = linked_list('abcde', lock=_lock())
        head = t2.head()
        tail = t2.tail()
        t.splice(t2)
        self.assertLinkedListEqual(t, ['a', 'b', 'c', 'd', 'e'])
        self.assertLinkedListEqual(t2, [])
        t2.append('X')
        head.next()
        tail.previous()
        self.assertEqual(head[0], 'X')
        self.assertEqual(tail[0], 'X')


        def setup():
            t = linked_list((1, 2, 3, 4, 5), lock=_lock())
            middle = t.find(3)
            return t, t.head(), middle, t.tail()

        t, head, middle, tail = setup()
        snippet = t.cut(start=None, stop=middle, lock=_lock())
        self.assertIs(head.linked_list, t)
        self.assertIs(tail.linked_list, t)
        check_linked_list_was_set(t)
        check_linked_list_was_set(snippet)

        t, head, middle, tail = setup()
        snippet = t.cut(start=head.after(), stop=middle, lock=_lock())
        self.assertIs(head.linked_list, t)
        self.assertIs(tail.linked_list, t)


        t, head, middle, tail = setup()
        snippet = t.cut(start=middle, stop=None, lock=_lock())
        self.assertIs(head.linked_list, t)
        self.assertIs(tail.linked_list, t)

        t, head, middle, tail = setup()
        snippet = t.cut(start=middle, stop=tail, lock=_lock())
        self.assertIs(head.linked_list, t)
        self.assertIs(tail.linked_list, t)

        # test rcut with start=None!
        t, head, middle, tail = setup()
        snippet = t.rcut(None, middle, lock=_lock())
        self.assertLinkedListEqual(snippet, [4, 5])
        self.assertLinkedListEqual(t, [1, 2, 3])

        # test cutting only special nodes!
        def setup():
            t = linked_list((1,), lock=_lock())
            it = t.find(1)
            del it[0]
            return t, it

        t, it = setup()
        t2 = t.cut(lock=_lock())
        self.assertEqual(it.linked_list, t2)

        t, it = setup()
        t2 = it.cut(lock=_lock())
        self.assertEqual(it.linked_list, t2)

        t, it = setup()
        t2 = t.rcut(lock=_lock())
        self.assertEqual(it.linked_list, t2)

        t, it = setup()
        t2 = it.rcut(lock=_lock())
        self.assertEqual(it.linked_list, t2)


    def test_reverse_iterators(self):
        for _lock in self.lock_fns():
            self.reverse_iterators_tests(_lock)

    def reverse_iterators_tests(self, _lock):
        def setup():
            t = linked_list((1, 2, 3, 4, 5, 6, 7, 8, 9), lock=_lock())
            it = t.find(5)
            rit = reversed(it)
            return t, it, rit

        t, it, rit = setup()
        self.assertEqual(it, reversed(rit))
        self.assertEqual(rit, reversed(reversed(rit)))

        self.assertEqual(rit[0], 5)
        self.assertEqual(len(rit), 5)
        next(rit)
        self.assertEqual(rit[0], 4)
        self.assertEqual(len(rit), 4)
        rit.previous()
        self.assertEqual(rit[0], 5)
        self.assertEqual(len(rit), 5)

        before = rit.before()
        self.assertEqual(before[0], 6)
        self.assertEqual(len(before), 6)
        after = rit.after()
        self.assertEqual(after[0], 4)
        self.assertEqual(len(after), 4)


        self.assertTrue(rit)
        rit.reset()
        self.assertIsTail(rit)
        self.assertTrue(rit)
        rit.exhaust()
        self.assertIsHead(rit)
        self.assertFalse(rit)

        t, it, rit = setup()
        self.assertEqual(rit.count(2), 1)
        self.assertEqual(rit.count(7), 0)
        self.assertEqual(rit.rcount(2), 0)
        self.assertEqual(rit.rcount(7), 1)
        r2 = reversed(t.find(2))
        r7 = reversed(t.find(7))
        self.assertEqual(rit.find(2), r2)
        self.assertEqual(rit.find(7), None)
        self.assertEqual(rit.rfind(2), None)
        self.assertEqual(rit.rfind(7), r7)

        self.assertEqual(rit.match(lambda v: v == 2), r2)
        self.assertEqual(rit.match(lambda v: v == 7), None)
        self.assertEqual(rit.rmatch(lambda v: v == 2), None)
        self.assertEqual(rit.rmatch(lambda v: v == 7), r7)

        t, it, rit = setup()
        rit.append('x')
        self.assertLinkedListEqual(t, [1, 2, 3, 4, 'x', 5, 6, 7, 8, 9])

        t, it, rit = setup()
        rit.prepend('x')
        self.assertLinkedListEqual(t, [1, 2, 3, 4, 5, 'x', 6, 7, 8, 9])

        t, it, rit = setup()
        rit.extend('abc')
        self.assertLinkedListEqual(t, [1, 2, 3, 4, 'c', 'b', 'a', 5, 6, 7, 8, 9])

        t, it, rit = setup()
        rit.rextend('abc')
        self.assertLinkedListEqual(t, [1, 2, 3, 4, 5, 'c', 'b', 'a', 6, 7, 8, 9])

        t, it, rit = setup()
        value = rit.pop()
        self.assertEqual(value, 5)
        self.assertLinkedListEqual(t, [1, 2, 3, 4, 6, 7, 8, 9])
        self.assertEqual(rit[0], 6)

        t, it, rit = setup()
        value = rit.rpop()
        self.assertEqual(value, 5)
        self.assertLinkedListEqual(t, [1, 2, 3, 4, 6, 7, 8, 9])
        self.assertEqual(rit[0], 4)

        t, it, rit = setup()
        rit.truncate()
        self.assertLinkedListEqual(t, [6, 7, 8, 9])

        t, it, rit = setup()
        rit.rtruncate()
        self.assertLinkedListEqual(t, [1, 2, 3, 4])

    def test_list_compatibility(self):
        for _lock in self.lock_fns():
            self.list_compatibility_tests(_lock)

    def list_compatibility_tests(self, _lock):
        def setup():
            return linked_list(range(1, 10), lock=_lock())

        t = setup()
        for i in range(1, 10):
            with self.subTest(i=i):
                self.assertEqual(t.index(i), i - 1)

        with self.assertRaises(ValueError):
            t.index('abc')
        with self.assertRaises(ValueError):
            t.index(4.5)
        with self.assertRaises(ValueError):
            t.index(None)
        with self.assertRaises(TypeError):
            t.index(1, start=1.5)
        with self.assertRaises(TypeError):
            t.index(1, stop=1.5)

        self.assertEqual(t.index(4, start=1, stop=5), 3)
        self.assertEqual(t.index(4, start=-9, stop=-1), 3)
        with self.assertRaises(ValueError):
            t.index(1, start=1, stop=5)
        with self.assertRaises(ValueError):
            t.index(1, start=-8, stop=-5)
        with self.assertRaises(ValueError):
            t.index(9, start=1, stop=5)
        with self.assertRaises(ValueError):
            t.index(9, start=-10, stop=-5)

        with self.assertRaises(ValueError):
            t.index(9, start=3, stop=2)
        with self.assertRaises(ValueError):
            t.index(9, start=12)

        t = linked_list(lock=_lock())
        with self.assertRaises(ValueError):
            t.index('empty list')

    def test_deque_compatibility(self):
        for _lock in self.lock_fns():
            self.deque_compatibility_tests(_lock)

    def deque_compatibility_tests(self, _lock):
        def setup():
            return linked_list(range(1, 10), lock=_lock())
        t = setup()
        t.extendleft('abc')
        self.assertLinkedListEqual(t, ['c', 'b', 'a', 1, 2, 3, 4, 5, 6, 7, 8, 9])
        with self.assertRaises(ValueError):
            t.extendleft(t)

    def test_pickle(self):
        for _lock in self.lock_fns():
            self.pickle_tests(_lock)

    def pickle_tests(self, _lock):
        def setup():
            t = linked_list((1, 2, 3, 4, 5, 6, 7, 8, 9), lock=_lock())
            it = t.find(5)
            rit = reversed(it)
            return t, it, rit
        t, it, rit = setup()

        p = pickle.dumps(t)
        t2 = pickle.loads(p)
        self.assertIsInstance(t, linked_list)
        self.assertEqual(t, t2)

        p = pickle.dumps(it)
        it2 = pickle.loads(p)
        self.assertIsInstance(it, linked_list_iterator)
        self.assertEqual(it[0], it2[0])
        self.assertEqual(t, it2.linked_list)

        p = pickle.dumps(rit)
        rit2 = pickle.loads(p)
        self.assertIsInstance(rit, linked_list_reverse_iterator)
        self.assertEqual(rit[0], rit2[0])
        self.assertEqual(t, rit2.linked_list)

    def test_coverage(self):
        self.assertEqual(repr(big.types._undefined), '<Undefined>')
        self.assertEqual(repr(big.types._inert_context_manager), '<inert_context_manager>')


        with self.assertRaises(TypeError):
            linked_list([1, 2, 3], lock=object())

        # has acquire and release, but isn't a context manager
        class FakeLock:
            def acquire(self): # pragma: nocover
                pass
            def release(self): # pragma: nocover
                pass

        with self.assertRaises(TypeError):
            linked_list([1, 2, 3], lock=FakeLock())

        # has acquire and release, is a context manager, but is false
        class FakeLock2:
            def acquire(self): # pragma: nocover
                pass
            def release(self): # pragma: nocover
                pass
            def __enter__(self): # pragma: nocover
                pass
            def __exit__(self): # pragma: nocover
                pass
            def __bool__(self): # pragma: nocover
                return False

        with self.assertRaises(ValueError):
            linked_list([1, 2, 3], lock=FakeLock2())



def run_tests():
    bigtestlib.run(name="big.types", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
