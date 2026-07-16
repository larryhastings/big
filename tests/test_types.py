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

from big import test
from big.test import raises, subtest

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


# module-level shims for two former self.assertTrue/False uses
# (test_isprintable picks one by name, so we can't inline them)
def assert_true(value):
    assert value

def assert_false(value):
    assert not value

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


def assertBool(got, expected):
    assert isinstance(got, bool)
    assert got is expected

def assertBytes(got, expected):
    assert isinstance(got, bytes)
    assert got == expected

def assertInt(got, expected):
    assert isinstance(got, int)
    assert got == expected

def assertString(got, expected):
    assert isinstance(got, string)
    assert got == expected

def assertStr(got, expected):
    assert isinstance(got, str)
    assert not isinstance(got, string)
    assert got == expected

##
## below this comment is a test_ method
## for *every* attribute of a str object,
## as reported by dir('').
##
## if we don't need to test it, I left it
## in, with a comment and a pass statement.
##

def test_constructor():
    assertString(string('abc'), 'abc')

    assert string(abcde) == abcde

    ar = raises

    with ar(TypeError):
        string(54321)
    with ar(TypeError):
        string(33.4)
    with ar(TypeError):
        string(['x', 'y'])

    assertString(string('abc', source=None), 'abc')
    assertString(string('abc', source='xyz'), 'abc')
    s = string('abc')
    assertString(string('abc', source=None), 'abc')
    assertString(string('abc', source='xyz'), 'abc')

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


def test_attributes():
    s_origin = "abcde"
    s = string(s_origin, source='"source"', line_number=3, column_number=4, first_column_number=2, tab_width=4)
    assertString(s, "abcde")
    assertStr(s.source, '"source"')
    assertInt(s.line_number, 3)
    assertInt(s.column_number, 4)
    assertInt(s.first_column_number, 2)
    assertInt(s.tab_width, 4)
    assert s.origin is s
    assertStr(s.where, '"source" line 3 column 4')

    s = string(s_origin, line_number=3, column_number=4, first_column_number=2, tab_width=4)
    assertString(s, "abcde")
    assert s.source == None
    assertInt(s.line_number, 3)
    assertInt(s.column_number, 4)
    assertInt(s.first_column_number, 2)
    assertInt(s.tab_width, 4)
    assert s.origin is s
    assertStr(s.where, 'line 3 column 4')

    slice = s[1:-1]
    assertString(slice, "bcd")
    assertString(slice.origin, s)

def test_regression_constructor_accepts_index_types():
    class Indexable:
        def __init__(self, value):
            self.value = value
        def __index__(self):
            return self.value

    s = string('abc', line_number=Indexable(2), column_number=Indexable(3), first_column_number=Indexable(1), tab_width=Indexable(4))
    assert s.line_number == 2
    assert s.column_number == 3
    assert s.first_column_number == 1
    assert s.tab_width == 4

    same = string(s, line_number=Indexable(1), column_number=Indexable(1), first_column_number=Indexable(1), tab_width=Indexable(8))
    assert same is s


def test___add__():
    assertString(l + " xyz", 'abcde xyz')
    assertString("boogie " + alphabet[22:], 'boogie wxyz')

    assertString(abcde + fghij, alphabet[:10])

    with raises(TypeError):
        x = abcde + 35
    with raises(TypeError):
        x = abcde + 55.0
    with raises(TypeError):
        x = abcde + (1, 2)

    # whitebox testing: _append_ranges joins contiguous ranges, and rhs has >1 subsequent ranges
    s = fghij + abcde + himem
    result = abcde + s
    assertString(result, 'abcdefghijabcdeQEMM\n')

    # whitebox testing: radd on an empty string just returns the lhs, but *as a string*
    s = string()
    t = 'abcd' + s
    assertString(t, 'abcd')

    class S(string):
        pass
    class T(string):
        pass

    assert isinstance(S('') + T('abc'), S)
    assert S('') + T('abc') == 'abc'


def test___radd__():
    assert abcde.__radd__(123) is NotImplemented

    with raises(TypeError):
        x = 1 + abcde

    s_line_number = 55
    s_column_number = 22
    s_source = 'marianas trench'
    s = string("abcde", line_number=s_line_number, column_number=s_column_number, source=s_source)

    # if it works out like magic, you can get a string out
    # but the line and column numbers have to work.
    str_x = "wxyz" + str(s)
    x = "wxyz" + s
    assert isinstance(x, string)
    assert x == str_x
    assert x.line_number == 1
    assert x.column_number == 1
    assert x.source == None
    assert x[4].line_number == s_line_number
    assert x[4].column_number == s_column_number
    assert x[4].source == s_source

    str_x = "123\nwxyz" + str(s)
    x = "123\nwxyz" + s
    assert isinstance(x, string)
    assert x == str_x
    assert x.line_number == 1
    assert x.column_number == 1
    assert x.source == None
    assert x[4].line_number == 2
    assert x[4].column_number == 1
    assert x[9].line_number == s_line_number
    assert x[8].column_number == s_column_number
    assert x[8].source == s_source


def test_regression_string_new_respects_exact_class():
    class S(string):
        pass

    base = string('abc')
    sub = S('abc')

    assert string(base) is base
    assert S(sub) is sub

    sub_from_base = S(base)
    assert type(sub_from_base) is S
    assert sub_from_base == 'abc'
    assert sub_from_base._ranges == base._ranges
    assert sub_from_base._length == base._length
    assert sub_from_base._line_number == base._line_number
    assert sub_from_base._column_number == base._column_number
    assert sub_from_base._source == base._source
    assert sub_from_base._origin == base._origin
    assert sub_from_base._offset == base._offset

    base_from_sub = string(sub)
    assert type(base_from_sub) is string
    assert base_from_sub == 'abc'
    assert base_from_sub._ranges == sub._ranges
    assert base_from_sub._length == sub._length
    assert base_from_sub._line_number == sub._line_number
    assert base_from_sub._column_number == sub._column_number
    assert base_from_sub._source == sub._source
    assert base_from_sub._origin == sub._origin
    assert base_from_sub._offset == sub._offset


def test___class__():
    assert l.__class__ == string

def test___contains__():
    # also tests .find and .index and .rfind and .rindex

    for s in ("b", "bc"):
        assert s in abcde
        assert abcde.find(s) >= 0
        assert abcde.rfind(s) >= 0
        assert abcde.index(s) >= 0
        assert abcde.rindex(s) >= 0
    for s in ("q", "funk"):
        assert not (s in abcde)
        assert abcde.find(s) == -1
        assert abcde.rfind(s) == -1
        with raises(ValueError):
            abcde.index(s)
        with raises(ValueError):
            abcde.rindex(s)

    letters = set(ascii_letters) | set(punctuation) | set(whitespace)
    for value_name, value in values.items():
        in_value = set(str(value))
        not_in_value = letters - in_value
        for letter in in_value:
            with subtest(value=value_name, letter=letter):
                assert letter in value
                assert value.find(letter) >= 0
                assert value.rfind(letter) >= 0
                assert value.index(letter) >= 0
                assert value.rindex(letter) >= 0
        for letter in not_in_value:
            with subtest(value=value_name, letter=letter):
                assert not (letter in value)
                assert value.find(letter) == -1
                assert value.rfind(letter) == -1
                with raises(ValueError):
                    value.index(letter)
                with raises(ValueError):
                    value.rindex(letter)

def test___delattr__():
    with raises(AttributeError):
        del l.source

def test___dir__():
    str_dir = list(dir(''))
    str_dir.extend(
        (
        '__module__',
        '__radd__',
        '__reversed__',
        '__slots__',
        '__weakref__',
        '_append_ranges',
        '_cat',
        '_clamp_index',
        '_column_number',
        '_compute_line_and_column',
        '_context',
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
        'context',
        'compile',
        'detab',
        'first_column_number',
        'generate_tokens',
        'line_number',
        'literal_eval',
        'multipartition',
        'multireplace',
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
    assert str_dir == string_dir

def test___doc__():
    assert isinstance(l.__doc__, str)
    assert l.__doc__

def test___eq__():
    assert l == str(l)
    assert l + 'x' == str(l) + 'x'

def test___format__():
    f = string('{abcde} {line1} {line2}', source=source)
    got = f.format(abcde=abcde, line1=line1, line2=line2)
    assertStr(got, 'abcde line 1!\n line 2.\n')
    got = f.format_map({'abcde': abcde, 'line1': line1, 'line2': line2})
    assertStr(got, 'abcde line 1!\n line 2.\n')

    # if the string is unchanged, return the string!
    f = string("{abcde}", source=source)
    got = f.format(abcde='{abcde}')
    assertString(f, got)
    got = f.format_map({'abcde': '{abcde}'})
    assertString(f, got)

def test___ge__():
    assert l >= str(l)
    assert l + 'x' >= str(l)
    assert str(l) + 'x' >= l

def test___getattribute__():
    assert l.source == source
    assert l.line_number == first_line_number
    assert l.column_number == first_column_number

    assert line2.source == source
    assert line2.line_number == first_line_number + 1
    assert line2.column_number == first_column_number

    assert himem.source == source2
    assert himem.line_number == first_line_number
    assert himem.column_number == first_column_number

    with raises(AttributeError):
        print(l.attribute_which_does_not_exist)

def test___getitem__():
    s = str(abcde)
    length = len(s)
    for i in range(-length, length):
        assertString(abcde[i], string(s[i], source=source, column_number=first_column_number + (i % length)))

    assertString(abcde[1:4], string('bcd', source=source, column_number=first_column_number + 1))

    assertString(abcde[1:-1:2], 'bd')

    # regression!
    last_zero = abcde[len(abcde):len(abcde)]
    assert last_zero.line_number == 1
    assert last_zero.column_number == abcde.first_column_number + len(abcde)

    # regression: negative-step slicing with far out-of-range bounds
    for value_name, value in values.items():
        s = str(value)
        with subtest(value=value_name):
            assertString(value[:-100:-1], s[:-100:-1])
            assertString(value[-100::-1], s[-100::-1])
            assertString(value[100::-1], s[100::-1])
            assertString(value[::-3], s[::-3])
            assertString(value[-3::-3], s[-3::-3])

    empty = string('')
    assertString(empty[-3::-3], '')
    assertString(empty[:-100:-1], '')

    # index must be slice or int
    with raises(TypeError):
        abcde[33.55]

    # *indexing* out of range raises IndexError.
    with raises(IndexError):
        abcde[-20]
    with raises(IndexError):
        abcde[33]

    # *slicing* out of range clamps to allowed range.
    assertString(abcde[-20:], abcde)
    assertString(abcde[448:], '')
    assertString(abcde[:10_000], abcde)
    assertString(abcde[:-8724], '')
    assertString(abcde[1:-50], '')

    assert abcde._clamp_index(None, 7, 'start') == 7
    assert abcde._clamp_index(-20, 0, 'start') == 0
    assert abcde._clamp_index(2, 0, 'start') == 2
    assert abcde._clamp_index(999, 0, 'start') == len(abcde)
    with raises(TypeError):
        abcde._clamp_index(1.5, 0, 'start')

    with raises(TypeError):
        abcde[1.5:]
    with raises(TypeError):
        abcde[:1.5]
    with raises(TypeError):
        abcde[::1.5]
    with raises(ValueError):
        abcde[::0]

    class Indexable:
        def __init__(self, value):
            self.value = value
        def __index__(self):
            return self.value

    assertString(abcde.__getitem__(slice(None, None, Indexable(-2))), str(abcde)[::-2])
    assertString(abcde.__getitem__(slice(Indexable(-20), Indexable(10_000), Indexable(1))), abcde)
    with raises(TypeError):
        abcde.__getitem__(slice(None, None, object()))
    with raises(ValueError):
        abcde.__getitem__(slice(None, None, Indexable(0)))

    # regression: if the string ended with a linebreak,
    # getting the zero-length string after that linebreak
    # would increment the line number
    s = string("x\n")
    endo = s[len(s):len(s)]
    assert endo.line_number == 2
    assert endo[0:0].line_number == 2 # used to be 3!
    assert endo[0:0][0:0].line_number == 2 # used to be 4!
    assert endo[0:0][0:0][0:0].line_number == 2 # used to be 5!

    # regression: slicing using negative indices used to raise ValueError!
    # but str object supports slicing with negative indices.  fixed in 0.13.1.
    for value_name, value in values.items():
        with subtest(value=value_name):
            assertString(value[::-1], "".join(reversed(str(value))))
            assertString(value[4:1:-1], str(value)[4:1:-1])
            assertString(value[::-2], str(value)[::-2])
            assertString(value[4:0:-2], str(value)[4:0:-2])

    abc = string('abc')
    xyz = string('xyz')
    abcxyz = abc + xyz
    zyxcba = abcxyz[::-1]
    assertString(zyxcba, 'zyxcba')
    assertString(zyxcba[0].origin, xyz)
    assertString(zyxcba[-1].origin, abc)

    # regression: the internal cached _length used to be
    # miscalculated for __getitem__ when using a slice
    # with a abs(range) > 1.
    #
    # the bug was there for range in (1,-1), but the code
    # accidentally worked anyway.

    # test with one-character ranges from the two ranges
    cx = abcxyz[2:4]
    assert cx._length == 2
    assert len(cx) == 2
    assertString(cx, 'cx')

    xc = zyxcba[2:4]
    assert xc._length == 2
    assert len(xc) == 2
    assertString(xc, 'xc')

    # test with two-character ranges from the two ranges
    bcxy = abcxyz[1:5]
    assert bcxy._length == 4
    assert len(bcxy) == 4
    assertString(bcxy, 'bcxy')

    yxcb = zyxcba[1:5]
    assert yxcb._length == 4
    assert len(yxcb) == 4
    assertString(yxcb, 'yxcb')



def test___getnewargs__():
    # string implements __getnewargs__, it's pickling machinery.
    for value_name, value in values.items():
        with subtest(value=value_name):
            p = pickle.dumps(value)
            value2 = pickle.loads(p)
            assertString(value2, value)

def test___getstate__():
    # __getstate__ is part of the pickling machinery.
    # we don't override str.__getstate__, pickling seems to work anyway.
    pass

def test___gt__():
    assert l + 'x' >= str(l)
    assert str(l) + 'x' >= l

def test___hash__():
    # we reuse str.__hash__
    for value_name, value in values.items():
        with subtest(value=value_name):
            s = str(value)
            assert hash(value) == hash(s)

def test___init__():
    # if you pass in a string to the string constructor,
    # and try to overwrite some metadata, we raise at you.
    # it doesn't really make sense to support this; the
    # string might be cobbled together from multiple
    # origins, and there's just no sensible way to
    # impose a different value for something like "source".
    #
    # If you really want to do this: as the exception suggests,
    # just cast the s argument to str first, e.g.:
    #
    #     string(str(s), source='xyz')
    #
    too_cool_for_school = 'too cool for school.py'
    with raises(ValueError):
        string(abcde, source=too_cool_for_school)
    with raises(ValueError):
        string(abcde, line_number=88)
    with raises(ValueError):
        string(abcde, column_number=236)
    with raises(ValueError):
        string(abcde, first_column_number=1236)
    with raises(ValueError):
        string(abcde, tab_width=2)

    # this of course works
    clone = string(str(abcde), source=too_cool_for_school)
    assert clone.source == too_cool_for_school


def test___init_subclass__():
    # oh golly, idk.  don't subclass string, mkay?
    pass

def test___iter__():
    for value_name, value in values.items():
        s = str(value)
        for i, (a, b) in enumerate(zip_longest(value, s)):
            with subtest(value=value_name, i=i, a=a, b=b):
                assert a == b, f'failed on value={value!r} i={i!r} a={a!r} != b={b!r}'
                assertStr(b, s[i])
                assertString(a, value[i])

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
        assertString(a, b)

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
        assertString(a, b)

    # test tab
    l = string('ab\tc', source='s2')
    expected = [
        string('a',  source='s2', line_number=1, column_number=1),
        string('b',  source='s2', line_number=1, column_number=2),
        string('\t', source='s2', line_number=1, column_number=3),
        string('c',  source='s2', line_number=1, column_number=9),
        ]
    for a, b in zip_longest(l, expected):
        assertString(a, b)

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
        assertString(a, b)

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
        assertString(a, b)


def test___le__():
    assert l <= str(l)
    assert l <= str(l) + 'x'
    assert str(l) <= l + 'x'

def test___len__():
    for value_name, value in values.items():
        with subtest(value=value_name):
            assertInt(len(value), len(str(value)))

def test___lt__():
    assert l < str(l) + 'x'
    assert str(l) < l + 'x'

def test___mod__():
    # wow!  crack a window, will ya?
    f = string('%s %d %f', source=source)
    got = f % (abcde, 33, 35.5)
    assertStr(got, 'abcde 33 35.500000')

def test___mul__():
    for value_name, value in values.items():
        for i in range(6):
            with subtest(value=value_name, i=i):
                assertStr(value * i, str(value) * i)

def test___ne__():
    assert l != str(l) + 'x'
    assert l + 'x' != str(l)
    assert l != 3
    assert string('3', source='x') != 3

def test___new__():
    with raises(ValueError):
        string(abcde, line_number=object())

def test___reduce__():
    # part of the pickling machinery, don't touch it!
    pass

def test___reduce_ex__():
    # part of the pickling machinery, don't touch it!
    pass

def test___repr__():
    for value_name, value in values.items():
        with subtest(value=value_name):
            assertStr(repr(value), repr(str(value)))

def test___rmul__():
    for value_name, value in values.items():
        for i in range(6):
            with subtest(value=value_name, i=i):
                assertStr(i * value, i * str(value))

def test___setattr__():
    with raises(AttributeError):
        l.source = '329872389'
    with raises(AttributeError):
        l.line_number = 329872389
    with raises(AttributeError):
        l.column_number = 329872389
    with raises(AttributeError):
        l.first_column_number = 329872389

def test___sizeof__():
    value = sys.getsizeof(string(''))
    assert isinstance(value, int)
    # the size varies from one Python version to the next
    assert value >= 40

def test___str__():
    assertString(abcde, 'abcde')

def test___subclasshook__():
    # don't need to test this (I hope)
    pass

def test_capitalize():
    for value_name, value in values.items():
        with subtest(value=value_name):
            assert value.capitalize() == str(value).capitalize()

def test_casefold():
    for value_name, value in values.items():
        with subtest(value=value_name):
            assert value.casefold() == str(value).casefold()

def test_count():
    for value_name, value in values.items():
        with subtest(value=value_name):
            assertInt(value.count('e'), str(value).count('e'))

def test_encode():
    for value_name, value in values.items():
        with subtest(value=value_name):
            assertBytes(value.encode('utf-8'),     str(value).encode('utf-8'))
            assertBytes(value.encode('ascii'),     str(value).encode('ascii'))
            assertBytes(value.encode('utf-16'),    str(value).encode('utf-16'))
            assertBytes(value.encode('utf-16-be'), str(value).encode('utf-16-be'))
            assertBytes(value.encode('utf-16-le'), str(value).encode('utf-16-le'))
            assertBytes(value.encode('utf-32'),    str(value).encode('utf-32'))
            assertBytes(value.encode('utf-32-be'), str(value).encode('utf-32-be'))
            assertBytes(value.encode('utf-32-le'), str(value).encode('utf-32-le'))

def test_endswith():
    for value_name, value in values.items():
        with subtest(value=value_name):
            assertBool(value.endswith('f'), str(value).endswith('f'))
            assertBool(value.endswith('.'), str(value).endswith('.'))

def test_expandtabs():
    # expandtabs is deliberately just str.expandtabs:
    # big.string starts as "a str that knows its own
    # provenance", and a shadowed str method must never
    # produce different text than str would.  (The improved,
    # origin-aware expansion is opt-in: detab, below.)
    for value_name, value in values.items():
        with subtest(value=value_name):
            tester = assertStr if '\t' in value else assertString
            tester(value.expandtabs(), str(value).expandtabs())
    # ...even for a string whose origin coordinates would
    # give a different answer.
    x = string('\tz', column_number=5)
    assert x.expandtabs() == str(x).expandtabs()

def test_detab():
    # the opt-in improvement: each tab expands according to
    # its own origin's coordinates--the same arithmetic
    # where() uses--and the characters around the synthesized
    # spaces keep their provenance.
    x = string('a\tb', source=source)
    y = x.detab()
    assert isinstance(y, string)
    assert str(y) == 'a       b'
    # 'b' still knows it came from column 9 of the source
    assert y[-1].column_number == 9
    assert y[-1].source == source

    # a string that starts at column 5 reaches the column-9
    # stop after four characters--not str.expandtabs's
    # context-free eight
    x = string('\tz', column_number=5)
    assert str(x.detab()) == '    z'
    # first_column_number anchors the tab-stop grid, exactly
    # as it does for where(): first column 5 puts stops at
    # columns 5, 13, 21...
    x = string('\tz', column_number=5, first_column_number=5)
    assert str(x.detab()) == '        z'
    # a linebreak resets the column to first_column_number
    x = string('ab\tc\n\td')
    assert str(x.detab()) == 'ab      c\n        d'

    # tabsize=None (the default) honors each tab's origin's
    # tab_width; an explicit tabsize overrides it
    x = string('\tz', tab_width=4)
    assert str(x.detab()) == '    z'
    assert str(x.detab(2)) == '  z'
    # in a multi-origin concatenation, each tab uses its own
    # origin's tab_width
    c = string('a\t', tab_width=4) + string('b\t', tab_width=8)
    assert str(c.detab()) == 'a   b       '

    # no tabs: returns self, the same object
    x = string('plain')
    assert x.detab() is x
    # tabsize <= 0 removes tabs, as with str
    x = string('a\tb')
    assert str(x.detab(0)) == 'ab'
    assert str(x.detab(-3)) == 'ab'

def test_find():
    # see test___contains__
    pass

def test_format():
    # see test___format__
    pass

def test_format_map():
    # see test___format__
    pass

def test_index():
    # see test___contains__
    pass

def test_isalnum():
    # smoke test for 3.6
    assert abcde.isascii()
    assert abcde._isascii()
    assert not (chipmunk.isascii())
    assert not (chipmunk._isascii())

    testers = "isalnum isalpha isascii isdecimal isdigit isidentifier islower isnumeric isprintable isspace istitle isupper".split()
    for value_name, value in values.items():
        for i in range(len(value)):
            with subtest(value=value_name, i=i):
                prefix = value[:i]
                for tester in testers:
                    if hasattr(str, tester):
                        assertInt(getattr(prefix, tester)(), getattr(str(prefix), tester)())
    for tester in testers:
        # if not hasattr(str, tester):
        #     continue
        fn = assert_true if tester == 'isprintable' else assert_false
        fn(getattr(chipmunk, tester)())

def test_isalpha():
    # see test_isalnum
    pass

def test_isascii():
    # see test_isalnum
    pass

def test_isdecimal():
    # see test_isalnum
    pass

def test_isdigit():
    # see test_isalnum
    pass

def test_isidentifier():
    # see test_isalnum
    pass

def test_islower():
    # see test_isalnum
    pass

def test_isnumeric():
    # see test_isalnum
    pass

def test_isprintable():
    # see test_isalnum
    pass

def test_isspace():
    # see test_isalnum
    pass

def test_istitle():
    # see test_isalnum
    pass

def test_isupper():
    # see test_isalnum
    pass

def test_join():
    empty = abcde[0:0]
    result = empty.join(list(abcde))
    assertString(result, abcde)

    a = abcde[0]
    result = a.join(list(abcde))
    assertString(result, 'aabacadae')

    for sep in (empty, a, abcde):
        with subtest(sep=sep):
            assertString(sep.join([]), str(sep).join([]))
            assertString(sep.join(iter(())), str(sep).join(iter(())))

def test_center():
    for value_name, value in values.items():
        with subtest(value=value_name):
            assertString(value.center(30), str(value).center(30))
            assertString(value.center(30, 'Z'), str(value).center(30, 'Z'))
            assertString(value.center(31), str(value).center(31))
            assertString(value.center(31, 'Z'), str(value).center(31, 'Z'))
            assertString(value.center(1), str(value).center(1))
            assertString(value.center(1, 'Z'), str(value).center(1, 'Z'))

    with raises(TypeError):
        abcde.center(33, 352)
    with raises(TypeError):
        abcde.center(33, 'xyz')
    with raises(TypeError):
        abcde.center(5.5)
    with raises(TypeError):
        abcde.center([3], 'x')


def test_regression_indexable_integer_arguments():
    class Indexable:
        def __init__(self, value):
            self.value = value
        def __index__(self):
            return self.value

    idx5 = Indexable(5)
    idx1 = Indexable(1)
    idx2 = Indexable(2)
    idxm1 = Indexable(-1)

    assertString(abcde.ljust(idx5), str(abcde).ljust(idx5))
    assertString(abcde.rjust(idx5), str(abcde).rjust(idx5))
    assertString(abcde.center(idx5), str(abcde).center(idx5))
    assertString(string('+42').zfill(Indexable(5)), '+0042')

    assertString(abcde.replace('a', 'x', idx1), str(abcde).replace('a', 'x', idx1))

    assert abcde.partition('b', idx2) == abcde.partition('b', 2)
    assert abcde.rpartition('b', idx2) == abcde.rpartition('b', 2)

    assert abcde.split('b', idx1) == str(abcde).split('b', idx1)
    assert abcde.rsplit('b', idx1) == str(abcde).rsplit('b', idx1)
    assert abcde.split('b', idxm1) == str(abcde).split('b', idxm1)
    assert abcde.rsplit('b', idxm1) == str(abcde).rsplit('b', idxm1)


def test_ljust():
    got = abcde.ljust(10)
    assertString(got, 'abcde     ')
    got = abcde.ljust(10, 'x')
    assertString(got, 'abcdexxxxx')

    # if the string doesn't change, return the string
    got = abcde.ljust(5)
    assertString(got, abcde)
    got = abcde.ljust(5, 'x')
    assertString(got, abcde)

    with raises(TypeError):
        abcde.ljust(5, 352)
    with raises(TypeError):
        abcde.ljust(5, 'xyz')
    with raises(TypeError):
        abcde.ljust(5.5)
    with raises(TypeError):
        abcde.ljust([3], 'x')


def test_lower():
    for method in "lower upper title".split():
        for value_name, value in values.items():
            with subtest(value=value_name, method=method):
                s = str(value)
                s_mutated = getattr(s, method)()
                value_mutated = getattr(value, method)()
                if s == s_mutated:
                    assert value_mutated is value
                else:
                    assertStr(value_mutated, s_mutated)


def test_lstrip():
    s = string('   xyz', source='test.py')
    stripped = s.lstrip()
    assert str(stripped) == 'xyz'
    assert stripped.source == 'test.py'
    assert stripped.offset == 3
    assert stripped.column_number == 4

    unchanged = string('xyz', source='test.py')
    assert unchanged.lstrip() is unchanged

def test_maketrans():
    map = {'a': 'x', 'b': 'y', 'c': 'z', 'd': '1', 'e': '2'}
    for value_name, value in values.items():
        with subtest(value=value_name):
            s = str(value)
            table = value.maketrans(map)
            assert table == s.maketrans(map)
            assertStr(value.translate(table), s.translate(table))

def test_partition():
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
            with subtest(value=value_name, i=i, middle=middle):
                for result in (
                    value.partition(middle),
                    value.rpartition(middle),
                    ):
                    assert result == (before, middle, after)
                    b, m, a = result
                    for which, got, expected in (
                        ('before', b, before),
                        ('middle', m, middle),
                        ('after',  a, after),
                        ):
                        with subtest(which=which):
                            assert got.source == expected.source, f'failed on value={value!r} {which}: got={got!r} expected={expected!r}'
                            assert got.line_number == expected.line_number, f'failed on value={value!r} {which}: got={got!r} expected={expected!r}'
                            assert got.column_number == expected.column_number, f'failed on value={value!r} {which}: got={got!r} expected={expected!r}'
                            assert got.first_column_number == expected.first_column_number, f'failed on value={value!r} {which}: got={got!r} expected={expected!r}'

        with subtest(value=value_name):
            before, s, after = value.partition('🐛') # generic bug!
            assertString(before, value)
            assert not (s)
            assert not (after)

            before, s, after = value.rpartition('🪳') # cockroach!
            assert not (before)
            assert not (s)
            assertString(after, value)

    # test overlapping
    l = string('a . . b . . c . . d . . e', source='smith')
    sep = ' . '

    partitions = l.partition(sep)
    assert partitions == ((
        l[:1],
        l[1:4],
        l[4:],
        ))
    assert partitions[0] + partitions[1] + partitions[2] == l
    assert string.cat(*partitions) == l

    assert l.rpartition(sep) == ((
        l[:21],
        l[21:24],
        l[24:]
        ))
    assert partitions[0] + partitions[1] + partitions[2] == l
    assert string.cat(*partitions) == l

    # test Eric Smith's extension

    assert l.partition(sep, 0) == (l,)
    assert l.partition(sep, 0)[0] is l
    assert l.rpartition(sep, 0) == (l,)
    assert l.rpartition(sep, 0)[0] is l

    partitions = l.partition(sep, 2)
    assert partitions == ((
        l[0:1],   # 'a'
        l[1:4],   # sep     - split 1
        l[4:7],   # '. b'
        l[7:10],  # sep     - split 2
        l[10:],   # ... and the rest
        ))

    partitions = l.rpartition(sep, 2)
    assert partitions == ((
        l[:15],   # 'a . b . c'
        l[15:18], # sep     - split 2
        l[18:21], # '. d'
        l[21:24], # sep     - split 1
        l[24:25], # '. e'
        ))

    partitions = l.partition(sep, 6)
    assert partitions == ((
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
        ))
    assert string.cat(*partitions) == l

    partitions = l.rpartition(sep, 6)
    assert partitions == ((
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
        ))
    assert string.cat(*partitions) == l

    for count in (1, 0, 2, -1):
        with subtest(count=count):
            with raises(ValueError):
                abcde.partition('', count)
            with raises(ValueError):
                abcde.rpartition('', count)

    with raises(TypeError):
        abcde.partition('x', 33.5)
    with raises(TypeError):
        abcde.rpartition('x', 33.5)

    with raises(TypeError):
        abcde.partition(33.5)
    with raises(TypeError):
        abcde.partition('abc', 33.5)



def test_removeprefix_and_removesuffix():
    # smoke test for 3.6-3.8
    assertString(abcde.removeprefix('ab'), abcde[2:])
    assertString(abcde.removeprefix('xx'), abcde)
    assertString(abcde.removesuffix('de'), abcde[:-2])
    assertString(abcde.removesuffix('xx'), abcde)

    # don't bother with the test for 3.6-3.8
    if not hasattr('', 'removeprefix'):  # pragma: no cover
        return

    for value_name, value in values.items():
        for i in range(len(value)):
            with subtest(value=value_name, i=i):
                prefix = value[:i]
                assertString(value.removeprefix(prefix), str(value).removeprefix(prefix))
                suffix = value[i:]
                assertString(value.removesuffix(suffix), str(value).removesuffix(suffix))
        with subtest(value=value_name):
            assert value.removeprefix(chipmunk) is value
            assert value.removesuffix(chipmunk) is value

    with raises(TypeError):
        abcde.removeprefix(33.5)
    with raises(TypeError):
        abcde.removesuffix(33.5)
    # regression test: exception used to say "removeprefix"
    try:
        abcde.removesuffix(33.5)
    except TypeError as e:
        assert str(e).startswith("removesuffix")

@unittest.skipIf(sys.version_info < (3, 9), "str.removesuffix is 3.9+")
def test_regression_removesuffix_empty_string():
    values_to_test = (
        '',
        'a',
        'abc',
        'abcabc',
    )

    suffixes = (
        '',
        'a',
        'bc',
        'x',
    )

    for raw in values_to_test:
        s = string(raw)
        for suffix in suffixes:
            with subtest(s=raw, suffix=suffix):
                assertString(s.removesuffix(suffix), raw.removesuffix(suffix))


def test_replace():
    for value_name, value in values.items():
        for src in "abcde":
            with subtest(value=value_name, src=src):
                result = value.replace(src, str(chipmunk))
                if src in value:
                    assertString(result, str(value).replace(src, chipmunk))
                else:
                    assertString(result, value)

    assertString(abcde.replace('c', 'x', 0), abcde)
    wackyland_ampersand = string('wackyland ampersand')
    assertString(wackyland_ampersand.replace('a', 'AAA', 3), 'wAAAckylAAAnd AAAmpersand')

    with raises(TypeError):
        abcde.replace(33, 'x')
    with raises(TypeError):
        abcde.replace('x', 33)
    with raises(TypeError):
        abcde.replace('x', 'y', 55.5)

    # regression test: exception raised by replace for a bad type passed in to old or new
    # used to use type(count) instead of type(old) or type(new)
    try:
        abcde.replace(123, 'x')
    except TypeError as e:
        assert "int" in str(e)
    try:
        abcde.replace('x', 456)
    except TypeError as e:
        assert "int" in str(e)

def test_regression_replace_empty_old_matches_str():
    cases = (
        ('', '-', 0),
        ('', '-', 1),
        ('', '-', -1),
        ('a', '-', 0),
        ('a', '-', 1),
        ('a', '-', 2),
        ('a', '-', -1),
        ('ab', '-', 1),
        ('ab', '-', 2),
        ('ab', '-', 3),
        ('ab', '-', -1),
        ('ab', '', 2),
        ('ab', '', -1),
    )

    for raw, new, count in cases:
        s = string(raw)
        with subtest(s=s, new=new, count=count):
            string_result = s.replace('', new, count)
            str_result = raw.replace('', new, count)

            assert string_result == str_result

            if not count:
                assert isinstance(string_result, type(s))
            elif not s:
                assert isinstance(string_result, type(new))
            else:
                assert isinstance(string_result, string)

    old = big.types._python_3_9_plus
    try:
        big.types._python_3_9_plus = False
        s = string('')
        assert s.replace('', '-', 1) is s
    finally:
        big.types._python_3_9_plus = old


def test_reversed():
    for i, (s, c) in enumerate(zip(reversed(abcde), reversed(str(abcde)))):
        assert s == c
        assert s.column_number == 5 - i

    s = string()
    assert list(s) == list(reversed(s))
    s = string('x')
    assert list(s) == list(reversed(s))

def test_rfind():
    # see test___contains__
    pass

def test_rindex():
    # see test___contains__
    pass

def test_rjust():
    with raises(TypeError):
        abcde.rjust(5, 352)
    with raises(TypeError):
        abcde.rjust(5, 'xyz')
    with raises(TypeError):
        abcde.rjust(5.5)
    with raises(TypeError):
        abcde.rjust([3], 'x')


def test_rpartition():
    # see test_partitino
    pass

def test_rsplit():
    # see split
    pass

def test_rstrip():
    assert himem.rstrip().rjust(8) == "    QEMM"
    assertString(himem.rstrip().rjust(4), "QEMM")

    # regression test: rstrip used to IGNORE the chars argument! of all the NERVE.
    xxhowdyxx = string("xxhowdyxx")
    assertString(xxhowdyxx.rstrip('x'), "xxhowdy")
    assertString(xxhowdyxx.rstrip('xy'), "xxhowd")
    assertString(xxhowdyxx.rstrip('xyz'), "xxhowd")

    xxhowdxyzyxx = string("xxhowdxyzyxx")
    assertString(xxhowdxyzyxx.rstrip('xyz'), "xxhowd")

def test_split():
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
        with subtest(i=i, s=s, sep=sep):
            source = 'toe'
            l2 = string(s, source=source)
            list_split = list(l2.split(sep))
            list_rsplit = list(l2.rsplit(sep))
            for line, rline, r in zip_longest(list_split, list_rsplit, result):
                with subtest(line=line):
                    s2, offset, line_number, column_number = r
                    assert line == s2, f"{line!r} != {r}"
                    assert rline == s2, f"{rline!r} != {r}"
                    assert line.offset == offset, f"{line!r} != {r}"
                    assert rline.offset == offset, f"{rline!r} != {r}"
                    assert line.line_number == line_number, f"{line!r} != {r}"
                    assert rline.line_number == line_number, f"{rline!r} != {r}"
                    assert line.column_number == column_number, f"{line!r} != {r}"
                    assert rline.column_number == column_number, f"{rline!r} != {r}"

            axxb = string("a x x b")
            list_split = axxb.split(' x ')
            assertString(list_split[0], 'a')
            assertString(list_split[1], 'x b')
            list_rsplit = axxb.rsplit(' x ')
            assertString(list_rsplit[0], 'a x')
            assertString(list_rsplit[1], 'b')

    with raises(TypeError):
        abcde.split(33.5)
    with raises(TypeError):
        abcde.split('x', 33.5)

    with raises(TypeError):
        abcde.rsplit(33.5)
    with raises(TypeError):
        abcde.rsplit('x', 33.5)

    class Indexable:
        def __init__(self, value):
            self.value = value
        def __index__(self):
            return self.value

    idx1 = Indexable(1)
    idxm1 = Indexable(-1)
    assert abcde.split('b', idx1) == str(abcde).split('b', idx1)
    assert abcde.rsplit('b', idx1) == str(abcde).rsplit('b', idx1)
    assert abcde.split('b', idxm1) == str(abcde).split('b', idxm1)
    assert abcde.rsplit('b', idxm1) == str(abcde).rsplit('b', idxm1)


def test_splitlines():
    # splitlines_demo = string(' a \n b \r c \r\n d \n\r e ', source='Z')
    assert list(splitlines_demo.splitlines()) == [' a ', ' b ', ' c ', ' d ', '', ' e ']
    assert list(splitlines_demo.splitlines(True)) == [' a \n', ' b \r', ' c \r\n', ' d \n', '\r', ' e ']

    assert splitlines_demo in values.values()

    for value_name, value in values.items():
        with subtest(value=value_name):
            splitted = value.splitlines(True)
            reconstituted = string.cat(*splitted)
            assertString(reconstituted, value)

def test_startswith():
    pass

def test_strip():
    methods = ("strip", "lstrip", "rstrip")
    for value_name, value in values.items():
        s = str(value)
        for method in methods:
            with subtest(value=value_name, method=method):
                s_mutated = getattr(s, method)()
                value_mutated = getattr(value, method)()
                if s_mutated == s:
                    assert value_mutated is value
                else:
                    # print(f"{value=!r} {method} -> {value_mutated=!r}")
                    assertString(value_mutated, s_mutated)
            with subtest(method=method):
                with raises(TypeError):
                    getattr(abcde, method)(33.5)

def test_swapcase():
    for value_name, value in values.items():
        with subtest(value=value_name):
            assert value.swapcase() == str(value).swapcase()

def test_title():
    # see test_lower
    pass

def test_translate():
    # see test_maketrans
    pass

def test_upper():
    # see test_lower
    pass

def test_zfill():
    assert himem.zfill(8) == "000QEMM\n"
    assertString(himem.zfill(5), "QEMM\n")

    values_to_test = (
        '',
        '42',
        '+42',
        '-42',
        '+',
        '-',
        '--42',
    )

    for raw in values_to_test:
        for width in range(-1, 8):
            with subtest(s=raw, width=width):
                s = string(raw)
                assertString(s.zfill(width), raw.zfill(width))

def test___radd___notimplemented():
    assert abcde.__radd__(123) is NotImplemented

def test_lstrip_removes_prefix_characters():
    s = string('   xyz', source='test.py')
    stripped = s.lstrip()
    assertString(stripped, 'xyz')
    assert stripped.line_number == s.line_number
    assert stripped.column_number == s.column_number + 3

def test_extended_slices():
    samples = (
        (abcde, slice(1, 5, 2)),
        (abcde, slice(None, None, -1)),
        (abcde, slice(4, 0, -2)),
        (himem, slice(None, None, 2)),
    )
    for value, sl in samples:
        with subtest(value=value, sl=sl):
            assertString(value[sl], str(value)[sl])

def test_context_zero_length_without_linebreak():
    s = string('hello world', source='test.py')
    sub = s[5:5]
    ctx = sub.context
    assert ctx
    assert str(ctx) == 'hello world\n     ^'
    assert ctx.parts.string.linebreak == ''
    assert ctx.parts.highlight.linebreak == ''

#######
## our additions
#######

def test_tab_width():
    def test(name, s, columns):
        for (i, c), expected in zip_longest(enumerate(s), columns):
            c2 = s[i]
            with subtest(s=name, i=i, c=c, c2=c2):
                assert c.column_number == expected
                assert c2.column_number == expected


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


def test_bisect():
    for i in range(1, len(alphabet) - 1):
        a, b = alphabet.bisect(i)
        assert isinstance(a, string)
        assert isinstance(b, string)
        assert len(a) == i
        assert alphabet.startswith(a)
        assert a + b == alphabet

    with raises(TypeError):
        alphabet.bisect(33.5)

def test_cat():
    assertString(string.cat(), '')
    assertString(string.cat(abcde), abcde)
    assertString(string.cat(abcde, 'xyz'), 'abcdexyz')
    assertString(string.cat(abcde[:2], abcde[2:]), abcde)
    assertString(string.cat(abcde[:2], abcde[:2]), 'abab')

    with raises(TypeError):
        string.cat(3, 4, 5)
    with raises(TypeError):
        string.cat('a', 'b', 5.2)

    t = string.cat('a')
    assertString(t, 'a')

    t = string.cat('', '', '', string(), '')
    assertString(t, '')


def test_generate_tokens():
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
    assert expected == got

def test_multipassthroughs():
    l = list(tabs.multisplit('\t'))
    l2 = list(tabs.split('\t'))
    assert l == l2

    before, c, after = abcde.multipartition('c')
    assertString(before, 'ab')
    assertString(c, 'c')
    assertString(after, 'de')

def test_compile():
    p = string(":+").compile()
    s = string('a:b::c::d:')
    l = p.split(s)
    assert l == [
        s[0],
        s[2],
        s[5],
        s[8],
        s[10:10],
        ]

def test_lazy_line_and_column():
    # line and column numbers are now lazy-computed
    # when we wouldn't otherwise get 'em for free.

    # .where
    segment = alphabet[5:10]
    assert segment._line_number is None
    assert segment._column_number is None
    assert segment.where == '"C:\\AUTOEXEC.BAT" line 1 column 6'

    # .__iter__
    segment = alphabet[5:10]
    assert segment._line_number is None
    assert segment._column_number is None
    l = list(segment)
    s = l[0]
    assert s.line_number == 1
    assert s.column_number == 6

    # cat
    segment = alphabet[5:10]
    assert segment._line_number is None
    assert segment._column_number is None
    s = string.cat(line1, line2)
    assert s.line_number == 1
    assert s.column_number == 1
    assert s == line1 + line2


def test_context_single_line():
    s = string('elif funky_socks in blast:\n  pass\n', source='foo.py')
    sub = s[20:25]  # 'blast'
    ctx = sub.context

    assert ctx
    assert str(ctx) == ('elif funky_socks in blast:\n'
        '                    ^^^^^')

    # single-line: parts == all_parts[0], str(ctx) == ctx.all
    assert len(ctx.all_parts) == 1
    assert ctx.parts == ctx.all_parts[0]
    assert str(ctx) == ctx.all

    p = ctx.parts
    assert isinstance(p.string.before, string)
    assert isinstance(p.string.span, string)
    assert isinstance(p.string.after, string)
    assert isinstance(p.string.linebreak, string)

    assert p.string.before == 'elif funky_socks in '
    assert p.string.span == 'blast'
    assert p.string.after == ':'
    assert p.string.linebreak == '\n'

    assert p.highlight.before == '                    '
    assert p.highlight.span == '^^^^^'
    assert p.highlight.after == ' '
    assert p.highlight.linebreak == ''

def test_context_multi_line():
    s = string('hello world\nsecond line\nthird line\n', source='test.py')
    sub = s[14:25]  # 'cond line\nt'
    ctx = sub.context

    assert ctx

    # __str__ shows first line only
    assert str(ctx) == ('second line\n'
        '  ^^^^^^^^^')

    # .all shows all lines
    assert ctx.all == ('second line\n'
        '  ^^^^^^^^^\n'
        'third line\n'
        '^')

    assert len(ctx.all_parts) == 2

    # parts has highlight linebreak forced to ''
    assert ctx.parts.highlight.linebreak == ''
    assert ctx.all_parts[0].highlight.linebreak == '\n'
    # but the string lines match
    assert ctx.parts.string == ctx.all_parts[0].string
    # and parts != all_parts[0] because of the linebreak difference
    assert ctx.parts != ctx.all_parts[0]

    # first line
    p0 = ctx.all_parts[0]
    assert p0.string.before == 'se'
    assert p0.string.span == 'cond line'
    assert p0.string.after == ''
    assert p0.string.linebreak == '\n'
    assert p0.highlight.before == '  '
    assert p0.highlight.span == '^^^^^^^^^'
    assert p0.highlight.after == ''
    assert p0.highlight.linebreak == '\n'

    # second line
    p1 = ctx.all_parts[1]
    assert p1.string.before == ''
    assert p1.string.span == 't'
    assert p1.string.after == 'hird line'
    assert p1.string.linebreak == '\n'
    assert p1.highlight.before == ''
    assert p1.highlight.span == '^'
    assert p1.highlight.after == '         '
    assert p1.highlight.linebreak == ''

def test_context_three_lines():
    s = string('aaa\nbbb\nccc\nddd\n', source='test.py')
    sub = s[2:11]  # 'a\nbbb\nccc'
    ctx = sub.context

    assert ctx

    assert str(ctx) == ('aaa\n'
        '  ^')

    assert ctx.all == ('aaa\n'
        '  ^\n'
        'bbb\n'
        '^^^\n'
        'ccc\n'
        '^^^')

    assert len(ctx.all_parts) == 3

def test_context_zero_length():
    s = string('hello world\n', source='test.py')
    sub = s[5:5]
    ctx = sub.context

    assert ctx

    # zero-length string gets a single ^ as insertion point
    assert str(ctx) == ('hello world\n'
        '     ^')

    p = ctx.parts
    assert p.string.before == 'hello'
    assert p.string.span == ''
    assert p.string.after == ' world'
    assert p.highlight.span == '^'

def test_context_zero_length_at_start():
    s = string('hello world\n', source='test.py')
    sub = s[0:0]
    ctx = sub.context

    assert ctx

    assert str(ctx) == ('hello world\n'
        '^')

    assert ctx.parts.string.before == ''
    assert ctx.parts.string.span == ''
    assert ctx.parts.string.after == 'hello world'

def test_context_zero_length_at_end_of_line():
    s = string('hello world\n', source='test.py')
    sub = s[11:11]
    ctx = sub.context

    assert ctx

    assert str(ctx) == ('hello world\n'
        '           ^')

    assert ctx.parts.string.before == 'hello world'
    assert ctx.parts.string.span == ''
    assert ctx.parts.string.after == ''

def test_context_invalid_multi_range():
    a = string('abc', source='x')
    b = string('xyz', source='y')
    chimera = a + b
    ctx = chimera.context

    assert not (ctx)

    with raises(ValueError):
        str(ctx)
    with raises(ValueError):
        ctx.parts
    with raises(ValueError):
        ctx.all_parts
    with raises(ValueError):
        ctx.all

def test_context_invalid_multi_range_same_origin():
    # two non-contiguous ranges from the same origin
    s = string('abcdef', source='x')
    chimera = s[:2] + s[4:]  # 'ab' + 'ef', skipping 'cd'
    ctx = chimera.context
    assert not (ctx)

def test_context_with_tabs():
    s = string('\t\thello world\n', source='test.py')
    sub = s[2:7]  # 'hello'
    ctx = sub.context

    assert ctx

    assert str(ctx) == ('\t\thello world\n'
        '                ^^^^^')

    # two tabs at width 8 = 16 spaces indent
    assert ctx.parts.highlight.before == ' ' * 16
    assert ctx.parts.highlight.span == '^^^^^'

def test_context_with_tab_in_span():
    s = string('before\tspan\tafter\n', source='test.py')
    sub = s[6:12]  # '\tspan\t'
    ctx = sub.context

    assert ctx

    assert str(ctx) == ('before\tspan\tafter\n'
        '      ^^^^^^^^^^')

    # 'before' = 6 chars visual width
    assert ctx.parts.highlight.before == '      '
    # '\tspan\t' from visual col 6: tab to 8 (2), 'span' (4), tab to 16 (4) = 10
    assert len(ctx.parts.highlight.span) == 10

def test_context_custom_tab_width():
    s = string('\thello', tab_width=4)
    sub = s[1:6]  # 'hello'
    ctx = sub.context

    assert ctx

    assert str(ctx) == ('\thello\n'
        '    ^^^^^')

    assert ctx.parts.highlight.before == '    '
    assert ctx.parts.highlight.span == '^^^^^'

def test_context_no_trailing_linebreak():
    s = string('no newline here')
    sub = s[3:10]  # 'newline'
    ctx = sub.context

    assert ctx

    # __str__ inserts a \n even though the source has none
    assert str(ctx) == ('no newline here\n'
        '   ^^^^^^^')

    # but the parts accurately report no linebreak
    assert ctx.parts.string.linebreak == ''

def test_context_zero_length_without_trailing_linebreak():
    s = string('hello world', source='test.py')
    sub = s[5:5]
    ctx = sub.context

    assert ctx
    assert str(ctx) == 'hello world\n     ^'
    assert len(ctx.all_parts) == 1

    string_line, highlight_line = ctx.parts
    assert string_line.before == 'hello'
    assert string_line.span == ''
    assert string_line.after == ' world'
    assert string_line.linebreak == ''
    assert highlight_line.before == ' ' * 5
    assert highlight_line.span == '^'
    assert highlight_line.after == ' ' * 5 ; assert highlight_line.linebreak == ''

def test_context_crlf_linebreak():
    s = string('first line\r\nsecond line\r\n', source='dos.txt')
    sub = s[12:18]  # 'second'
    ctx = sub.context

    assert ctx

    assert str(ctx) == ('second line\r\n'
        '^^^^^^')

    assert ctx.parts.string.linebreak == '\r\n'
    assert ctx.parts.string.span == 'second'
    assert ctx.parts.string.after == ' line'

def test_context_entire_line_is_span():
    s = string('first\nsecond\nthird\n')
    sub = s[6:12]  # 'second'
    ctx = sub.context

    assert ctx

    assert str(ctx) == ('second\n'
        '^^^^^^')

    p = ctx.parts
    assert p.string.before == ''
    assert p.string.span == 'second'
    assert p.string.after == ''
    assert p.highlight.before == ''
    assert p.highlight.span == '^^^^^^'
    assert p.highlight.after == ''

def test_context_first_character():
    s = string('hello world\n')
    sub = s[0:1]  # 'h'
    ctx = sub.context

    assert ctx

    assert str(ctx) == ('hello world\n'
        '^')

    assert ctx.parts.string.before == ''
    assert ctx.parts.string.span == 'h'
    assert ctx.parts.string.after == 'ello world'

def test_context_last_character_before_linebreak():
    s = string('hello world\n')
    sub = s[10:11]  # 'd'
    ctx = sub.context

    assert ctx

    assert str(ctx) == ('hello world\n'
        '          ^')

    assert ctx.parts.string.before == 'hello worl'
    assert ctx.parts.string.span == 'd'
    assert ctx.parts.string.after == ''

def test_context_delegated_properties():
    s = string('hello\nworld\n', source='test.py', line_number=5)
    sub = s[6:11]  # 'world'
    ctx = sub.context

    assert ctx.line_number == 6
    assert ctx.column_number == 1
    assert ctx.source == 'test.py'
    assert ctx.where == 'test.py line 6 column 1'
    assert ctx.offset == 6

def test_context_string_property():
    s = string('hello world\n')
    sub = s[6:11]  # 'world'
    ctx = sub.context

    assert ctx.string is sub
    assert str(ctx.string) == 'world'

def test_context_is_cached():
    s = string('hello\n')
    sub = s[0:5]
    ctx1 = sub.context
    ctx2 = sub.context
    assert ctx1 is ctx2

def test_context_repr():
    s = string('hello\n', source='test.py')
    sub = s[0:5]
    ctx = sub.context
    assert 'test.py' in repr(ctx)

    # invalid context
    a = string('abc', source='x')
    b = string('xyz', source='y')
    chimera = a + b
    ctx = chimera.context
    assert 'invalid' in repr(ctx)

def test_context_tuple_structure():
    s = string('hello world\n')
    sub = s[6:11]  # 'world'
    ctx = sub.context
    p = ctx.parts

    # parts is a 2-tuple
    assert len(p) == 2
    s_line, h_line = p
    assert s_line is p.string
    assert h_line is p.highlight

    # each line is a 4-tuple
    assert len(s_line) == 4
    before, span, after, linebreak = s_line
    assert before == s_line.before
    assert span == s_line.span
    assert after == s_line.after
    assert linebreak == s_line.linebreak

    assert len(h_line) == 4
    h_before, h_span, h_after, h_linebreak = h_line
    assert h_before == h_line.before
    assert h_span == h_line.span
    assert h_after == h_line.after
    assert h_linebreak == h_line.linebreak

def test_context_provenance_preserved():
    # the string parts in context should be big.string objects
    # with correct provenance back to the origin
    s = string('hello world\n', source='test.py', line_number=5, column_number=3)
    sub = s[6:11]  # 'world'
    ctx = sub.context
    p = ctx.parts

    assert isinstance(p.string.before, string)
    assert p.string.before.source == 'test.py'
    assert p.string.before == 'hello '

    assert isinstance(p.string.span, string)
    assert p.string.span.source == 'test.py'
    assert p.string.span.line_number == 5
    assert p.string.span.column_number == 9  # 3 + len('hello ')

    assert isinstance(p.string.after, string)
    assert isinstance(p.string.linebreak, string)

def test_context_multi_line_provenance():
    s = string('hello world\nsecond line\nthird line\n', source='test.py')
    sub = s[14:25]  # 'cond line\nt' spanning lines 2-3
    ctx = sub.context

    for part in ctx.all_parts:
        assert isinstance(part.string.before, string)
        assert isinstance(part.string.span, string)
        assert isinstance(part.string.after, string)
        assert part.string.span.source == 'test.py'

def test_context_str_and_all_return_string_type():
    # str(ctx) and ctx.all use _cat, so they return big.string objects
    s = string('hello world\n', source='test.py')
    sub = s[6:11]
    ctx = sub.context

    result_str = str(ctx)
    assert isinstance(result_str, string)

    result_all = ctx.all
    assert isinstance(result_all, string)

def test_regression_stateless_string_subclasses():
    class S(string):
        pass

    class T(string):
        pass

    s = S('abc')
    t = T('xyz')

    result = S.cat()
    assert type(result) is S
    assert result == ''

    result = S.cat('abc')
    assert type(result) is S
    assert result == 'abc'

    result = S.cat(t)
    assert type(result) is S
    assert result == 'xyz'
    assert result.origin is t

    result = S('') + 'abc'
    assert type(result) is S
    assert result == 'abc'

    result = 'abc' + S('')
    assert type(result) is S
    assert result == 'abc'

    result = S(',').join([])
    assert type(result) is S
    assert result == ''

    result = S('').join(['a'])
    assert type(result) is S
    assert result == 'a'

    result = S('').join([t])
    assert type(result) is S
    assert result == 'xyz'
    assert result.origin is t

    sub = S('hello')[1:4]
    ctx = sub.context
    rendered = ctx.all
    assert type(rendered) is S
    assert 'ell' in rendered


def test_context_coverage():
    s = string('hello world\n', source='test.py')
    sub = s[6:11]
    ctx = sub.context
    p = ctx.parts

    # string_context_line.__repr__
    repr(p.string)
    # string_context_parts.__repr__
    repr(p)
    # ctx.origin
    assert ctx.origin is sub.origin

def test_context_weakref_expired():
    s = string('hello world\n', source='test.py')
    sub = s[6:11]
    ctx = sub.context
    del s, sub
    with raises(ReferenceError):
        ctx.string

def test_str_fast_path():
    # str() of a full-origin string hands back the origin's
    # plain str--the very same object, zero copies
    text = 'hello world\n'
    s = string(text, source='test.py')
    assert str(s) is text
    # str() of a slice is a copy, but an exact str
    sub = str(s[0:5])
    assert sub == 'hello'
    assert type(sub) is str
    # multi-range strings fall back to the copy too
    c = string('abc', source='a') + string('def', source='b')
    assert str(c) == 'abcdef'
    assert type(str(c)) is str
    # an origin built from a str *subclass* is never handed back raw
    class WeirdStr(str):
        pass
    w = string(WeirdStr('xyz'))
    assert str(w) == 'xyz'
    assert type(str(w)) is str

def test_undefined_sentinel_equality_is_identity():
    # the module's _undefined sentinel compares equal only to
    # itself--even against promiscuous-equality objects like
    # mock.ANY.  (internal comparisons all use `is`; __eq__ is
    # armor for anyone who compares with ==.)
    import big.types
    u = big.types._undefined
    assert u == u
    assert not (u == object())
    assert not (u == big.types.Undefined())

def test_linked_list_type_equality_differ():
    # the registered linked_list differ turns a failing
    # linked_list == linked_list into an element-wise diff
    import io
    a = linked_list([1, 2, 3])
    b = linked_list([1, 99, 3])
    try:
        assert a == b
    except AssertionError:
        tb = sys.exc_info()[2]
    buffer = io.StringIO()
    test.explain(tb, buffer.write)
    explanation = buffer.getvalue()
    assert "Lists differ" in explanation
    assert "99" in explanation

def lock_fns(one_lock=False):
    def return_none():
        return None

    yield return_none

    def return_True():
        return True

    yield return_True

    def return_new_lock():
        return Lock()

    yield return_new_lock

    if not one_lock:
        return

    lock = Lock()
    def return_one_lock():
        return lock

    yield return_one_lock


def assertLength(o, length):
    assert len(o) == length

def assertLinkedListEqual(t, expected):
    assert isinstance(t, linked_list)
    expected = list(expected)
    got = list(t)
    assert expected == got
    assert len(t) == len(expected)

# teach the explainer to diff two linked_lists element-wise, so a
# bare failing "assert linked_list_a == linked_list_b" prints a
# real list diff.  (unittest's type-equality dispatch only fires
# when both operands are the same type, so this is linked_list vs
# linked_list; the assertLinkedListEqual helper handles
# linked_list vs list by converting first.)
def _diff_linked_list(a, b, msg=None):
    test._helper.assertEqual(list(a), list(b), msg)

test.register_type_equality(linked_list, _diff_linked_list)

def assertNoSpecialNodes(t):
    # white box testing
    head = t._head
    tail = t._tail

    cursor = head.next
    while cursor != tail:
        assert cursor.special is None
        cursor = cursor.next

def assertIsSpecial(it):
    assert it is not None
    assert it.is_special
    assert it.special == 'special'

def assertIsHead(it):
    assert it is not None
    assert it.is_special
    assert it.special == 'head'

def assertIsTail(it):
    assert it is not None
    assert it.is_special
    assert it.special == 'tail'

def assertIsNormalNode(it):
    assert it is not None
    assert not (it.is_special)
    assert it.special == None


def test_list_basics():
    for _lock in lock_fns():
        list_basics_tests(_lock)

def list_basics_tests(_lock):
    t = linked_list(lock=_lock())
    assert not (t)
    assertLinkedListEqual(t, [])

    t = linked_list((1, 2, 3, 4, 5), lock=_lock())
    assert t
    assertLinkedListEqual(t, [1, 2, 3, 4, 5])

    t = linked_list([1, 2, 4, 8, 16], lock=_lock())
    assert t
    assertLinkedListEqual(t, [1, 2, 4, 8, 16])

    t = linked_list('abcde', lock=_lock())
    assert t
    assertLinkedListEqual(t, ['a', 'b', 'c', 'd', 'e'])

    t = linked_list(iter((1, 1, 2, 3, 5, 8)), lock=_lock())
    assert t
    assertLinkedListEqual(t, [1, 1, 2, 3, 5, 8])


def test_comparison_foreign_types():
    # regression: __eq__/__ne__ returned False/True for foreign
    # types (and iterator __eq__ returned False); all return
    # NotImplemented now, so reflected comparisons get their
    # chance, per the data model.  (the ordering methods always
    # did this--the class was internally inconsistent.)
    t = linked_list([1, 2])
    assert t.__eq__(5) is NotImplemented
    assert t.__ne__(5) is NotImplemented
    assert not (t == 5)
    assert t != 5
    it = iter(t)
    assert it.__eq__(5) is NotImplemented
    assert not (it == 5)

    class Anything:
        def __eq__(self, other):
            return True
    assert t == Anything()    # reflected __eq__
    assert it == Anything()

def test_indexing_skips_tombstones():
    # regression: _cursor_at_list_index and linked_list.index()
    # counted 'special' (tombstone) nodes, so a list with a live
    # tombstone disagreed with len() and list() about which index
    # held which value--t[0] could even land ON a tombstone and
    # raise UndefinedIndexError while list(t) worked fine.
    # tombstones don't occupy an index now, at both sites, in
    # both the from-head and from-tail walks.
    t = linked_list(['a', 'b', 'c'])
    it = t.find('a')            # parked iterator => tombstone
    t.remove('a')
    assert len(t) == 2
    assert list(t) == ['b', 'c']
    assert [t[i] for i in range(len(t))] == ['b', 'c']
    assert t.index('b') == 0
    assert t.index('c') == 1

    # torture: tombstones at front, middle, and back
    t = linked_list(['a', 'b', 'c', 'd', 'e'])
    parked = [t.find('a'), t.find('c'), t.find('e')]
    for v in ('a', 'c', 'e'):
        t.remove(v)
    assert list(t) == ['b', 'd']
    assert [t[i] for i in range(len(t))] == list(t)
    assert [t[-1], t[-2]] == ['d', 'b']
    for v in ('b', 'd'):
        assert t[t.index(v)] == v
    # mutation via indexes lands on data nodes, not tombstones
    del t[0]
    assert list(t) == ['d']
    t.insert(0, 'x')
    assert list(t) == ['x', 'd']
    t[1] = 'D'
    assert list(t) == ['x', 'D']

    # pop(i) through a trailing tombstone (the from-tail walk)
    t = linked_list(['a', 'b', 'c'])
    parked2 = t.find('c')
    t.remove('c')
    assert t.pop(1) == 'b'
    assert list(t) == ['a']

    # keep the parked iterators alive to the end, so the
    # tombstones stay live throughout
    del parked, parked2, it

def test_reverse_iterator_extend_accepts_any_iterable():
    # regression: reverse-iterator extend/rextend called
    # reversed() directly on the iterable, so generators (and
    # any non-reversible iterable) raised TypeError--while every
    # other extend in the class accepts any iterable.  they're
    # materialized first now, and produce exactly the same
    # result as a list would.
    def build(extend_name, iterable_factory):
        t = linked_list([1, 2, 3])
        rit = reversed(t)
        rit.next()      # point at 3
        getattr(rit, extend_name)(iterable_factory())
        return list(t)

    for extend_name in ('extend', 'rextend'):
        expected = build(extend_name, lambda: [8, 9])
        assert build(extend_name, lambda: (x for x in (8, 9))) == expected
        assert build(extend_name, lambda: iter((8, 9))) == expected
        assert build(extend_name, lambda: (8, 9)) == expected

    # the can't-extend-self-with-self guard still works
    t = linked_list([1, 2, 3])
    rit = reversed(t)
    rit.next()
    with raises(ValueError):
        rit.extend(t)

def test_iterator_next_previous_promiscuous_default():
    # regression: next(default=...) and previous(default=...)
    # tested the internal sentinel with ==, so a default with a
    # promiscuous __eq__ (unittest.mock.ANY is the everyday
    # example) was mistaken for "no default supplied", and an
    # exhausted iterator raised StopIteration instead of
    # returning the caller's explicit default.  (a hostile
    # __eq__ crashed instead.)  the sentinel test is "is" now.
    import unittest.mock

    class Hostile:
        def __eq__(self, other): # pragma: no cover
            # never called--that's what this test proves
            raise RuntimeError("don't compare me")

    for default in (unittest.mock.ANY, Hostile()):
        t = linked_list([1, 2])
        it = iter(t)
        assert it.next(default) == 1
        assert it.next(default) == 2
        assert it.next(default) is default

        rit = reversed(t)
        assert rit.next(default) == 2
        assert rit.next(default) == 1
        assert rit.next(default) is default

        it = t.tail()
        assert it.previous(default) == 2
        assert it.previous(default) == 1
        assert it.previous(default) is default

def test_iterator_basics():
    for _lock in lock_fns():
        iterator_basics_tests(_lock)

def iterator_basics_tests(_lock):
    t = linked_list(lock=_lock())
    assertNoSpecialNodes(t)

    with raises(TypeError):
        # white box testing
        linked_list_base_iterator(t._head)

    # an iterator on a linked list always starts out at head
    it = iter(t)
    assertIsHead(it)
    assert not (it)
    with raises(UndefinedIndexError):
        it[0]
    with raises(UndefinedIndexError):
        it.pop()
    with raises(UndefinedIndexError):
        it.rpop()
    # iterator only returns True if you can call next and it doesn't raise.
    # so, when pointing to either head or tail of an empty list, it returns false.
    assert not (it)
    it.exhaust()
    assert not (it)
    with raises(UndefinedIndexError):
        it.pop()
    with raises(UndefinedIndexError):
        it.rpop()
    it.reset()
    assert not (it)

    # and you can't go past head
    with raises(UndefinedIndexError):
        before = it.before()
    assertNoSpecialNodes(t)

    # an reverse iterator on a linked list always starts out at tail
    rit = reversed(t)
    assertIsTail(rit)
    assert not (rit)
    with raises(UndefinedIndexError):
        rit[0]
    with raises(UndefinedIndexError):
        rit.pop()
    with raises(UndefinedIndexError):
        rit.rpop()

    # iterator only returns True if you can call next and it doesn't raise.
    # so, when pointing to either head or tail of an empty list, it returns false.
    assert not (rit)
    rit.exhaust() # rit, exhaust goes to head
    assert not (rit)
    with raises(UndefinedIndexError):
        rit.pop()
    with raises(UndefinedIndexError):
        rit.rpop()
    rit.reset()   # rit, reset goes to tail
    assert not (rit)

    # and you can't go past tail
    with raises(UndefinedIndexError):
        before = rit.before()

    assertNoSpecialNodes(t)

    initial = [1, 2, 3, 4, 5]
    t = linked_list(initial, lock=_lock())
    assertLength(t, 5)
    it = iter(t)
    result = list(it)
    assert initial == result

    reversed_initial = list(reversed(initial))
    rit = reversed(t)
    result = list(rit)
    assert reversed_initial == result
    assertNoSpecialNodes(t)

    # you can't make your own iterators
    with raises(TypeError):
        big.types.linked_list_base_iterator()
    with raises(TypeError):
        big.types.linked_list_base_iterator(t)
    with raises(TypeError):
        big.types.linked_list_base_iterator(it)

    with raises(TypeError):
        linked_list_iterator()
    with raises(TypeError):
        linked_list_iterator(t)
    with raises(TypeError):
        linked_list_iterator(it)

    with raises(TypeError):
        linked_list_reverse_iterator()
    with raises(TypeError):
        linked_list_reverse_iterator(t)
    with raises(TypeError):
        linked_list_reverse_iterator(it)


def test_pop_and_rpop():
    for _lock in lock_fns():
        pop_and_rpop_tests(_lock)

def pop_and_rpop_tests(_lock):
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
        with subtest(index=index, expected=expected):
            t, it_4 = setup()
            got = t.pop(index)
            assert expected == got

            t, it_4 = setup()
            got = t.rpop(index)
            assert expected == got

            if index >= 0:
                t, it_4 = setup()
                it_0 = t.find(0)
                got = it_0.pop(index)
                assert expected == got

                t, it_4 = setup()
                it_0 = t.find(0)
                got = it_0.rpop(index)
                assert expected == got

                t, it_4 = setup()
                rit_0 = reversed(t.find(0))
                got = rit_0.pop(-index)
                assert expected == got

                t, it_4 = setup()
                rit_0 = reversed(t.find(0))
                got = rit_0.rpop(-index)
                assert expected == got

                t, it_4 = setup()
                got = it_4.pop(index - 4)
                assert expected == got

                t, it_4 = setup()
                got = it_4.rpop(index - 4)
                assert expected == got

                t, it_4 = setup()
                rit_4 = reversed(it_4)
                got = rit_4.pop(4 - index)
                assert expected == got

                t, it_4 = setup()
                rit_4 = reversed(it_4)
                got = rit_4.pop(4 - index)
                assert expected == got

            else:
                t, it_4 = setup()
                tail = t.tail()
                got = tail.pop(index)
                assert expected == got

                t, it_4 = setup()
                tail = t.tail()
                got = tail.rpop(index)
                assert expected == got

                t, it_4 = setup()
                rit_8 = reversed(t.find(8))
                got = rit_8.pop(-1 - index)
                assert expected == got

                t, it_4 = setup()
                rit_8 = reversed(t.find(8))
                got = rit_8.rpop(-1 - index)
                assert expected == got

                t, it_4 = setup()
                rit_4 = reversed(it_4)
                got = rit_4.pop(-5 - index)
                assert expected == got

                t, it_4 = setup()
                rit_4 = reversed(it_4)
                got = rit_4.rpop(-5 - index)
                assert expected == got


    # test directionality of iterator pop/rpop
    t, it_4 = setup()
    value = it_4.pop()
    assert value == 4
    assert it_4[0] == 3

    t, it_4 = setup()
    value = it_4.rpop()
    assert value == 4
    assert it_4[0] == 5

    t, it_4 = setup()
    rit_4 = reversed(it_4)
    value = rit_4.pop()
    assert value == 4
    assert rit_4[0] == 5

    t, it_4 = setup()
    rit_4 = reversed(it_4)
    value = rit_4.rpop()
    assert value == 4
    assert rit_4[0] == 3

    # pop/rpop don't clamp
    t, it_4 = setup()
    rit_4 = reversed(it_4)
    with raises(UndefinedIndexError):
        t.pop(100)
    with raises(UndefinedIndexError):
        t.rpop(100)
    with raises(UndefinedIndexError):
        it_4.pop(100)
    with raises(UndefinedIndexError):
        it_4.rpop(100)
    with raises(UndefinedIndexError):
        rit_4.pop(100)
    with raises(UndefinedIndexError):
        rit_4.rpop(100)
    with raises(UndefinedIndexError):
        t.pop(-100)
    with raises(UndefinedIndexError):
        t.rpop(-100)
    with raises(UndefinedIndexError):
        it_4.pop(-100)
    with raises(UndefinedIndexError):
        it_4.rpop(-100)
    with raises(UndefinedIndexError):
        rit_4.pop(-100)
    with raises(UndefinedIndexError):
        rit_4.rpop(-100)

    head = t.head()
    tail = t.tail()
    rhead = reversed(head)
    rtail = reversed(tail)

    with raises(UndefinedIndexError):
        head.pop()
    with raises(UndefinedIndexError):
        head.rpop()
    with raises(UndefinedIndexError):
        tail.pop()
    with raises(UndefinedIndexError):
        tail.rpop()
    with raises(UndefinedIndexError):
        rhead.pop()
    with raises(UndefinedIndexError):
        rhead.rpop()
    with raises(UndefinedIndexError):
        rtail.pop()
    with raises(UndefinedIndexError):
        rtail.rpop()



def test_method_superset():
    for _lock in lock_fns():
        method_superset_tests(_lock)

def method_superset_tests(_lock):
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
        move rmove
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

    assert linked_list_dir == list_and_deque_dir

def test_empty_list():
    for _lock in lock_fns():
        empty_list_tests(_lock)

def empty_list_tests(_lock):
    # if the list is empty:
    t = linked_list(lock=_lock())
    assert not (t)

    # "after" head is tail
    it = iter(t)
    assertIsHead(it)
    assert not (it)

    after = it.after()
    assertIsTail(after)
    assert not (after)

    # if you run next on it, it goes to tail and stays there
    result = next(it, 5)
    assert result == 5
    assertIsTail(it)
    result = next(it, 5)
    assert result == 5
    assertIsTail(it)

    it.reset()
    assertIsHead(it)
    it.exhaust()
    assertIsTail(it)

    # after tail (reversed) is head
    rit = reversed(t)
    assertIsTail(rit)
    assert not (rit)
    after = rit.after()
    assertIsHead(after)
    assert not (after)

    # if you run next on it, it goes to head and stays there
    result = next(rit, 5)
    assert result == 5
    assertIsHead(rit)
    result = next(rit, 5)
    assert result == 5
    assertIsHead(rit)

    rit.reset()
    assertIsTail(rit)
    rit.exhaust()
    assertIsHead(rit)

    # can't pop from an empty list.
    # IndexError, matching list.pop and deque.popleft.
    # (regression: this used to be ValueError, breaking the
    # "superset of list and deque" interface promise.)
    with raises(IndexError):
        t.pop()
    with raises(IndexError):
        t.popleft()
    with raises(IndexError):
        t.rpop()

    assertNoSpecialNodes(t)

def test_extend():
    for _lock in lock_fns():
        extend_tests(_lock)

def extend_tests(_lock):
    def setup():
        t = linked_list((1, 2, 3), lock=_lock())
        assertLength(t, 3)
        it = iter(t)
        return t, it

    t, it = setup()
    t.extend('ABC')
    assertLinkedListEqual(t, [1, 2, 3, 'A', 'B', 'C'])
    assertLength(t, 6)
    assertNoSpecialNodes(t)

    with raises(ValueError):
        t.extend(t)

    t, it = setup()
    t.rextend('ABC')
    assertLinkedListEqual(t, ['A', 'B', 'C', 1, 2, 3])
    assertLength(t, 6)
    assertNoSpecialNodes(t)

    with raises(ValueError):
        t.rextend(t)

    t, it = setup()
    it = it.find(1)
    it.extend('ABC')
    assertLinkedListEqual(t, [1, 'A', 'B', 'C', 2, 3])
    assertLength(t, 6)
    assertNoSpecialNodes(t)

    t, it = setup()
    it = it.find(3)
    it.rextend('ABC')
    assertLinkedListEqual(t, [1, 2, 'A', 'B', 'C', 3])
    assertLength(t, 6)
    assertNoSpecialNodes(t)

    with raises(ValueError):
        it.extend(t)
    with raises(ValueError):
        it.rextend(t)
    rit = reversed(it)
    with raises(ValueError):
        rit.extend(t)
    with raises(ValueError):
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
    assert isinstance(rit, linked_list_reverse_iterator)
    rit = rit.find(2)
    assert isinstance(rit, linked_list_reverse_iterator)
    rit.extend('ABC')
    assertLinkedListEqual(t, [1, 'C', 'B', 'A', 2, 3])
    assertLength(t, 6)
    assertNoSpecialNodes(t)

    t, rit = setup2()
    assert isinstance(rit, linked_list_reverse_iterator)
    rit = rit.find(2)
    assert isinstance(rit, linked_list_reverse_iterator)
    rit.rextend('ABC')
    assertLinkedListEqual(t, [1, 2, 'C', 'B', 'A', 3])
    assertLength(t, 6)
    assertNoSpecialNodes(t)


def test_linked_list_methods():
    for _lock in lock_fns():
        linked_list_methods_tests(_lock)

def linked_list_methods_tests(_lock):
    def setup():
        t = linked_list((1, 2, 3), lock=_lock())
        it = t.find(2)
        return t, it

    t, it = setup()
    t_copy = t.copy()
    assert t == t_copy
    t_copy = copy.copy(t)
    assert t == t_copy


    t_copy.remove(2)
    assert t != t_copy
    assert t != (1, 2, 4)
    assertNoSpecialNodes(t)
    assertNoSpecialNodes(t_copy)

    with raises(ValueError):
        t.remove('abcde')
    got = t.remove('abcde', 'not found')
    assert got == 'not found'

    t, it = setup()
    t.append('xyz')
    assertLinkedListEqual(t, (1, 2, 3, 'xyz'))
    assertNoSpecialNodes(t)

    t, it = setup()
    t.prepend('abc')
    assertLinkedListEqual(t, ('abc', 1, 2, 3))
    assertNoSpecialNodes(t)


def test_with_deleted_nodes():
    for _lock in lock_fns():
        deleted_nodes_tests(_lock)

def deleted_nodes_tests(_lock):
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
    it_copy = it.copy()
    got = it_copy.previous()
    assert got == 0
    assert it_copy[0] == 0
    before = it.before()
    assert before[0] == 0

    it_copy = it.copy()
    got = it_copy.next()
    assert got == 8
    assert it_copy[0] == 8
    after = it.after()
    assert after[0] == 8

    t, it, iterators = setup()
    value = it.pop()
    assert value == 4
    assert it[0] == 0

    t, it, iterators = setup()
    value = it.rpop()
    assert value == 4
    assert it[0] == 8

    t, it, iterators = setup()
    it2 = iterators[2]
    value = it2.previous()
    assert value == 0
    assert it2[0] == 0

    t, it, iterators = setup()
    it6 = iterators[6]
    value = it6.next()
    assert value == 8
    assert it6[0] == 8

    # try t.popleft when the node after head is deleted
    t, it, iterators = setup()
    t.remove(0)
    value = t.popleft()
    assert value == 4
    it = iter(t)
    value = next(it)
    assert value == 8

    # and pop when the node before tail is deleted
    t, it, iterators = setup()
    t.remove(8)
    value = t.pop()
    assert value == 4
    it = reversed(t)
    value = next(it)
    assert value == 0

    t = linked_list(range(10), lock=_lock())
    with raises(UndefinedIndexError):
        t[10] = 'abc'
    with raises(UndefinedIndexError):
        del t[10]


def test_iterator_methods():
    for _lock in lock_fns():
        iterator_methods_tests(_lock)

def iterator_methods_tests(_lock):
    def setup():
        t = linked_list([1, 2, 3, 4, 5], lock=_lock())
        it = t.find(3)
        return t, it

    t, it = setup()
    assert it[0] == 3
    assert repr(it) == f"<linked_list_iterator {hex(id(it))} cursor=<_linked_list_node 3 iterator_refcount=1>>"
    it_copy = it.copy()
    del(it_copy)
    assert it[0] == 3
    assertNoSpecialNodes(t)

    got = it.next()
    assert got == 4
    assert it[0] == 4

    got = it.next()
    assert got == 5
    assert it[0] == 5

    with raises(StopIteration):
        got = it.next()
    got = it.next(None)
    assert got is None
    assertIsTail(it)

    got = it.next(None)
    assert got is None
    assertIsTail(it)
    assertNoSpecialNodes(t)

    t, it = setup()
    assert it[0] == 3
    got = it.previous()
    assert got == 2
    assert it[0] == 2

    got = it.previous()
    assert got == 1
    assert it[0] == 1

    with raises(StopIteration):
        got = it.previous()
    got = it.previous(None)
    assert got is None
    assertIsHead(it)

    got = it.previous(None)
    assert got is None
    assertIsHead(it)
    assertNoSpecialNodes(t)

    t, it = setup()
    before = it.before()
    assert it[0] == 3
    assert before[0] == 2
    before_copy = before.copy()
    before_copy.pop() # before now points at a deleted node
    before2 = it.before() # skips over deleted node
    assert before2[0] == 1

    got = before2.remove(5)
    assert got == 5
    with raises(ValueError):
        got = before2.remove('qemm')
    got = before2.remove('quarterdeck', 'not found')
    assert got == 'not found'


    t, it = setup()
    after = it.after()
    assert it[0] == 3
    assert after[0] == 4
    after_copy = after.copy()
    after_copy.pop() # after now points at a deleted node
    after2 = it.after() # skips over deleted node
    assert after2[0] == 5

    t, it = setup()
    rit = reversed(it)
    it2 = reversed(rit)
    assert it == it2
    assert it[0] == it2[0]

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
    with raises(UndefinedIndexError):
        it[-3]
    assert it[-2] == 1
    assert it[-1] == 2

    assert it[ 0] == 3

    assert it[ 1] == 4
    assert it[ 2] == 5
    with raises(IndexError):
        it[3]

    t, it = setup()
    assertLinkedListEqual(it[-2: 3: 2], [1, 3, 5])
    assertLinkedListEqual(it[ 2:-3:-2], [5, 3, 1])
    with raises(ValueError):
        it[-6: 2: 3]
    with raises(ValueError):
        it[ 2:-6: 3]
    with raises(ValueError):
        it[ 2:-3: 0]
    assertLinkedListEqual(it[ 2:-3: 2], [])
    assertLinkedListEqual(it[-2: 3:-2], [])
    assertNoSpecialNodes(t)

def test_prepend_and_append_and_extend_and_rextend():
    for _lock in lock_fns():
        prepend_and_append_and_extend_and_rextend_tests(_lock)

def prepend_and_append_and_extend_and_rextend_tests(_lock):
    #
    # test all our verbs in the middle of the list
    #
    def setup():
        t = linked_list((1, 2, 3), lock=_lock())
        it = t.find(2)
        assertIsNormalNode(it)
        return t, it

    t, it = setup()
    it.prepend(1.5)
    assertLinkedListEqual(t, [1, 1.5, 2, 3])
    assertIsNormalNode(it)
    assert it[0] == 2
    assertNoSpecialNodes(t)

    t, it = setup()
    it.append(2.5)
    assertLinkedListEqual(t, [1, 2, 2.5, 3])
    assertIsNormalNode(it)
    assert it[0] == 2
    assertNoSpecialNodes(t)

    t, it = setup()
    it.rextend((1.25, 1.5, 1.75))
    assertLinkedListEqual(t, [1, 1.25, 1.5, 1.75, 2, 3])
    assertIsNormalNode(it)
    assert it[0] == 2
    assertNoSpecialNodes(t)

    t, it = setup()
    it.extend((2.25, 2.5, 2.75))
    assertLinkedListEqual(t, [1, 2, 2.25, 2.5, 2.75, 3])
    assertIsNormalNode(it)
    assert it[0] == 2
    assertNoSpecialNodes(t)

    #
    # now test when we're pointed at head
    #
    def setup():
        t = linked_list((1, 2, 3), lock=_lock())
        it = iter(t)
        assertIsHead(it)
        return t, it
    t, it = setup()

    t, it = setup()
    it.append('A')
    assertLinkedListEqual(t, ['A', 1, 2, 3])
    assertIsHead(it)
    assertNoSpecialNodes(t)

    t, it = setup()
    with raises(UndefinedIndexError):
        it.prepend('B')

    t, it = setup()
    it.extend('CDE')
    assertLinkedListEqual(t, ['C', 'D', 'E', 1, 2, 3])
    assertIsHead(it)
    assertNoSpecialNodes(t)

    t, it = setup()
    with raises(UndefinedIndexError):
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
    assertLinkedListEqual(t, [1, 2, 3, 'I'])
    assertIsTail(it)
    assertNoSpecialNodes(t)

    t, it = setup()
    with raises(UndefinedIndexError):
        it.append('J')

    t, it = setup()
    it.rextend('KLM')
    assertLinkedListEqual(t, [1, 2, 3, 'K', 'L', 'M'])
    assertIsTail(it)
    assertNoSpecialNodes(t)

    t, it = setup()
    with raises(UndefinedIndexError):
        it.extend('NOP')


    #
    # now test all of the above with empty lists!
    #

    def setup_at_head():
        t = linked_list(lock=_lock())
        it = iter(t)
        assertIsHead(it)
        return t, it

    def setup_at_tail():
        t = linked_list(lock=_lock())
        it = iter(t)
        it.exhaust()
        return t, it

    # appending to head obviously works
    t, it = setup_at_head()
    it.append('W')
    assertLinkedListEqual(t, ['W'])
    assertIsHead(it)
    assertNoSpecialNodes(t)

    t, it = setup_at_head()
    with raises(UndefinedIndexError):
        it.prepend('X')

    # prepending before tail obviously works
    t, it = setup_at_tail()
    it.prepend('Y')
    assertLinkedListEqual(t, ['Y'])
    assertIsTail(it)
    assertNoSpecialNodes(t)

    t, it = setup_at_tail()
    with raises(UndefinedIndexError):
        it.append('Z')

    # now with extend and rextend

    # appending to head obviously works
    t, it = setup_at_head()
    it.extend('uvw')
    assertLinkedListEqual(t, ['u', 'v', 'w'])
    assertIsHead(it)
    assertNoSpecialNodes(t)

    t, it = setup_at_head()
    with raises(UndefinedIndexError):
        it.rextend('vwx')

    # prepending before tail obviously works
    t, it = setup_at_tail()
    it.rextend('wxy')
    assertLinkedListEqual(t, ['w', 'x', 'y'])
    assertIsTail(it)
    assertNoSpecialNodes(t)

    t, it = setup_at_tail()
    with raises(UndefinedIndexError):
        it.extend('xyz')


def test_special_nodes():
    for _lock in lock_fns():
        special_nodes_tests(_lock)

def special_nodes_tests(_lock):
    t = linked_list('a')
    assert repr(t) == "linked_list(['a'])"

    t = linked_list('a', lock=_lock())
    assert t

    it = iter(t).after()
    it_copy = it.copy()
    it_copy.pop()
    # white box testing: remove lock, just so we can examine the repr
    t._lock = None
    # test repr with a deleted node
    assert repr(t) == "linked_list([])"
    assert not (t)

    with raises(UndefinedIndexError):
        iter(t).pop()
    with raises(UndefinedIndexError):
        reversed(t).pop()
    with raises(SpecialNodeError):
        it.pop()

    # white box test of repr
    t = linked_list('ab')
    it_a = t.find('a')
    it_b = t.find('b')
    it_special = it_b.copy()
    it_b.pop()

    data_node_a = it_a._cursor
    assert repr(data_node_a) == "<_linked_list_node 'a' iterator_refcount=2>"

    special_node = it_special._cursor
    assert repr(special_node) == "<_linked_list_node None, special='special' iterator_refcount=1>"

    head_node = t.head()._cursor
    assert repr(head_node) == "<_head_node iterator_refcount=0>"
    assert head_node.special == "head"
    assert head_node.value == None
    assert head_node.previous == None

    tail_node = t.tail()._cursor
    assert repr(tail_node) == "<_tail_node iterator_refcount=0>"
    assert tail_node.special == "tail"
    assert tail_node.value == None
    assert tail_node.next == None




def test_deleted_node():
    for _lock in lock_fns():
        deleted_node_tests(_lock)

def deleted_node_tests(_lock):
    # "dit" == "deleted iterator"
    # points to the deleted node in the center of the list,
    # between 3 and 4
    def setup():
        t = linked_list([1, 2, 3, 'X', 4, 5, 6], lock=_lock())
        dit = t.find('X')
        dit_copy = dit.copy()
        dit_copy.pop()
        del dit_copy
        return t, dit

    t, dit = setup()
    assert list(    iter(t)) == [1, 2, 3, 4, 5, 6]
    assert list(reversed(t)) == [6, 5, 4, 3, 2, 1]
    assertLength(t, 6)
    assertIsSpecial(dit)
    assert isinstance(dit, linked_list_iterator)
    with raises(SpecialNodeError):
        dit[0]
    with raises(SpecialNodeError):
        dit.pop()
    with raises(SpecialNodeError):
        dit.rpop()

    # you also can't include a deleted node in a slice
    with raises(SpecialNodeError):
        dit[-1:2]
    with raises(SpecialNodeError):
        dit[-2:4:2]
    with raises(SpecialNodeError):
        dit[1:-2:-1]
    with raises(SpecialNodeError):
        dit[2:-4:-2]
    # ... but if you carefully step over it, it's fine!
    assertLinkedListEqual(dit[-3:4:2], [1, 3, 4, 6])

    dit_copy = dit.copy()
    value = dit_copy.previous()
    assertIsNormalNode(dit_copy)
    assert value == 3
    assert dit_copy[0] == 3

    dit_copy = dit.copy()
    value = next(dit_copy)
    assertIsNormalNode(dit_copy)
    assert value == 4
    assert dit_copy[0] == 4

    before = dit.before()
    assertIsNormalNode(before)
    assert before[0] == 3
    after = dit.after()
    assertIsNormalNode(after)
    assert after[0] == 4

    five = dit.find(5)
    assertIsNormalNode(five)
    assert five[0] == 5
    assert dit.find(333) is None

    two = dit.rfind(2)
    assertIsNormalNode(two)
    assert two[0] == 2
    assert dit.rfind(333) is None

    six = dit.match(lambda value: value == 6)
    assertIsNormalNode(six)
    assert six[0] == 6
    assert dit.match(lambda value: value == 888) is None

    one = dit.rmatch(lambda value: value == 1)
    assertIsNormalNode(one)
    assert one[0] == 1
    assert dit.rmatch(lambda value: value == 999) is None


    rdit = reversed(dit)
    assertIsSpecial(rdit)
    assert isinstance(rdit, linked_list_reverse_iterator)
    assert rdit
    with raises(SpecialNodeError):
        rdit[0]
    with raises(SpecialNodeError):
        rdit.pop()
    with raises(SpecialNodeError):
        rdit.rpop()

    rdit_copy = rdit.copy()
    value = next(rdit_copy)
    assertIsNormalNode(rdit_copy)
    assert value == 3
    assert rdit_copy[0] == 3

    rdit_copy = rdit.copy()
    value = rdit_copy.previous()
    assertIsNormalNode(rdit_copy)
    assert value == 4
    assert rdit_copy[0] == 4

    before = rdit.before()
    assertIsNormalNode(before)
    assert before[0] == 4
    after = rdit.after()
    assertIsNormalNode(after)
    assert after[0] == 3

    five = rdit.rfind(5)
    assert five[0] == 5
    assertIsNormalNode(five)
    assert rdit.rfind(333) is None
    two = rdit.find(2)
    assertIsNormalNode(two)
    assert two[0] == 2
    assert rdit.find(333) is None

    six = rdit.rmatch(lambda value: value == 6)
    assertIsNormalNode(six)
    assert six[0] == 6
    assert rdit.rmatch(lambda value: value == 888) is None

    one = rdit.match(lambda value: value == 1)
    assertIsNormalNode(one)
    assert one[0] == 1
    assert rdit.match(lambda value: value == 999) is None

    t, dit = setup()
    dit.prepend('Z')
    assertLinkedListEqual(t, [1, 2, 3, 'Z', 4, 5, 6])
    assertLength(t, 7)

    t, dit = setup()
    dit.append('Q')
    assertLinkedListEqual(t, [1, 2, 3, 'Q', 4, 5, 6])
    assertLength(t, 7)

    t, dit = setup()
    rdit = reversed(dit)
    rdit.prepend('J')
    assertLinkedListEqual(t, [1, 2, 3, 'J', 4, 5, 6])
    assertLength(t, 7)

    t, dit = setup()
    rdit = reversed(dit)
    rdit.append('K')
    assertLinkedListEqual(t, [1, 2, 3, 'K', 4, 5, 6])
    assertLength(t, 7)


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

        assertLength(t, 17)
        return t, it, delete_str_nodes

    # smoke-check: we can delete nodes in a loop, right?
    t, it, delete_str_nodes = setup()
    delete_str_nodes()
    assertLinkedListEqual(t, [1, 2, 3, 4, 5, 6, 7])
    assert list(reversed(t)) == [7, 6, 5, 4, 3, 2, 1]

    # test removing each individual character
    # and make sure find and match all work
    for c in 'abcdefghij':
        with subtest(c=c):
            for variant in ('t remove', 't rremove', 'it remove', 'it rremove'):
                with subtest(variant=variant):
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
                    assertLength(t, 16)
                    assert t.find(c) is None
                    assert t.rfind(c) is None
                    for i in range(1, 8):
                        with subtest(i=i):
                            it = t.find(i)
                            assertIsNormalNode(it)
                            assert it[0] == i
                            rit = t.rfind(i)
                            assertIsNormalNode(rit)
                            assert rit[0] == i

                            it = t.match(lambda value: value==i)
                            assertIsNormalNode(it)
                            assert it[0] == i
                            rit = t.rmatch(lambda value: value==i)
                            assertIsNormalNode(rit)
                            assert rit[0] == i

    t, it, delete_str_nodes = setup()

    # keep references to every node, to keep the deleted nodes alive
    iterators = []
    while it:
        iterators.append(it)
        it = it.after()

    delete_str_nodes()
    assertLinkedListEqual(t, [1, 2, 3, 4, 5, 6, 7])
    assertLength(t, 7)

    # now, starting from the center:
    it = t.find(3)

    seven = it.find(7)
    assertIsNormalNode(seven)
    assert seven[0] == 7
    one = it.rfind(1)
    assertIsNormalNode(one)
    assert one[0] == 1

    def raise_if_str(value):
        if isinstance(value, str): # pragma: nocover
            raise ValueError(f'str found, {value!r}')
        return False

    assert it.match(raise_if_str) is None
    assert it.rmatch(raise_if_str) is None
    assert t.match(raise_if_str) is None
    assert t.rmatch(raise_if_str) is None

    seven2 = it.match(lambda value: value == 7)
    assertIsNormalNode(seven2)
    assert seven2[0] == 7
    one2 = it.rmatch(lambda value: value == 1)
    assertIsNormalNode(one2)
    assert one2[0] == 1

    # prepend and append from two different deleted nodes
    # in any order should always produce the same result
    expected = [0, 1, 2, 3, 4, 5]
    for ordering in itertools.permutations([0, 1, 2, 3]):
        with subtest(ordering=ordering):
            t = linked_list([0, 'a', 'b', 5])
            it1 = t.find('a')
            it1_copy = it1.copy()
            it1_copy.pop()
            it2 = t.find('b')
            it2_copy = it2.copy()
            it2_copy.pop()

            operations = [
                lambda: it1.prepend(1),
                lambda: it1.append(2),
                lambda: it2.prepend(3),
                lambda: it2.append(4),
                ]
            for index in ordering:
                operations[index]()
            assertLength(t, 6)
            assertLinkedListEqual(t, expected)

    # test clear
    t, it, delete_str_nodes = setup()
    assertLength(t, 17)
    t.clear()
    assertLength(t, 0)
    assert not (t)
    # white box testing: remove lock, just so we can examine the repr
    t._lock = None
    assert repr(t) == 'linked_list([])'
    for value in t: # pragma: nocover
        assert False # shouldn't reach here!


    t, it, delete_str_nodes = setup()
    # keep references to every node, to keep the deleted nodes alive
    iterators = []
    while it:
        iterators.append(it)
        it = it.after()
    delete_str_nodes()
    t.clear()
    assert not (t)
    # white box testing: remove lock, just so we can examine the repr
    t._lock = None
    assert repr(t) == 'linked_list([])'
    for value in t: # pragma: nocover
        assert False # shouldn't reach here!


    t, it, delete_str_nodes = setup()
    assertLength(t, 17)
    assert t.pop() == 'j'
    assertLength(t, 16)
    assert t.pop() == 7
    assertLength(t, 15)
    assert t.pop() == 'i'
    assertLength(t, 14)

    assert t.popleft() == 'a'
    assertLength(t, 13)
    assert t.popleft() == 1
    assertLength(t, 12)
    assert t.popleft() == 'b'
    assertLength(t, 11)

    def setup():
        t = linked_list(range(10), lock=_lock())
        it = t.find(5)
        return t, it

    for i in range(10):
        with subtest(i=i):
            t, it = setup()
            assert t.pop(i) == i
            t, it = setup()
            assert t.popleft(i) == i

    for i in range(-5, 5):
        with subtest(i=i):
            t, it = setup()
            assert it.pop(i) == i + 5
            t, it = setup()
            assert it.rpop(i) == i + 5

    t, it = setup()
    with raises(TypeError):
        t.pop('abc')
    with raises(TypeError):
        t.popleft('abc')
    with raises(TypeError):
        it.pop('abc')
    with raises(TypeError):
        it.rpop('abc')

    t, it = setup()
    del it[0]
    with raises(SpecialNodeError):
        it.pop(0)
    with raises(SpecialNodeError):
        it.rpop(0)
    with raises(SpecialNodeError):
        t.pop(len(t))
    with raises(SpecialNodeError):
        t.popleft(-(len(t) + 1))



def test_rich_compare():
    for _lock in lock_fns():
        rich_compare_tests(_lock)

def rich_compare_tests(_lock):
    a        = linked_list([1, 2, 2], lock=_lock())
    b        = linked_list([1, 2, 3], lock=_lock())
    b_longer = linked_list([1, 2, 3, 4], lock=_lock())
    c        = linked_list([1, 2, 4], lock=_lock())
    pi       = 3.14159


    # __eq__

    assert a == a
    assert not (a == b)
    assert not (a == b_longer)
    assert not (a == c)

    assert not (b == a)
    assert b == b
    assert not (b == b_longer)
    assert not (b == c)

    assert not (b_longer == a)
    assert not (b_longer == b)
    assert b_longer == b_longer
    assert not (b_longer == c)

    assert not (c == a)
    assert not (c == b)
    assert not (c == b_longer)
    assert c == c

    assert not (a == pi)

    # __ne__
    assert not (a != a)
    assert a != b
    assert a != b_longer
    assert a != c

    assert b != a
    assert not (b != b)
    assert b != b_longer
    assert b != c

    assert b_longer != a
    assert b_longer != b
    assert not (b_longer != b_longer)
    assert b_longer != c

    assert c != a
    assert c != b
    assert c != b_longer
    assert not (c != c)

    assert a != pi


    # __lt__
    assert not (a < a)
    assert a < b
    assert a < b_longer
    assert a < c

    assert not (b < a)
    assert not (b < b)
    assert b < b_longer
    assert b < c

    assert not (b_longer < a)
    assert not (b_longer < b)
    assert not (b_longer < b_longer)
    assert b_longer < c

    assert not (c < a)
    assert not (c < b)
    assert not (c < b_longer)
    assert not (c < c)

    with raises(TypeError):
        a < pi


    # __le__
    assert a <= a
    assert a <= b
    assert a <= b_longer
    assert a <= c

    assert not (b <= a)
    assert b <= b
    assert b <= b_longer
    assert b <= c

    assert not (b_longer <= a)
    assert not (b_longer <= b)
    assert b_longer <= b_longer
    assert b_longer <= c

    assert not (c <= a)
    assert not (c <= b)
    assert not (c <= b_longer)
    assert c <= c

    with raises(TypeError):
        a <= pi

    # __ge__
    assert a >= a
    assert not (a >= b)
    assert not (a >= b_longer)
    assert not (a >= c)

    assert b >= a
    assert b >= b
    assert not (b >= b_longer)
    assert not (b >= c)

    assert b_longer >= a
    assert b_longer >= b
    assert b_longer >= b_longer
    assert not (b_longer >= c)

    assert c >= a
    assert c >= b
    assert c >= b_longer
    assert c >= c

    with raises(TypeError):
        a >= pi

    # __gt__
    assert not (a > a)
    assert not (a > b)
    assert not (a > b_longer)
    assert not (a > c)

    assert b > a
    assert not (b > b)
    assert not (b > b_longer)
    assert not (b > c)

    assert b_longer > a
    assert b_longer > b
    assert not (b_longer > b_longer)
    assert not (b_longer > c)

    assert c > a
    assert c > b
    assert c > b_longer
    assert not (c > c)

    with raises(TypeError):
        a > pi

def test_linked_list___getitem__():
    for _lock in lock_fns():
        getitem_tests(_lock)

def getitem_tests(_lock):
    # __getitem__ and slicing
    def setup():
        return linked_list((1, 2, 3, 4, 5), lock=_lock())

    a = setup()

    assert a[0] == 1
    assert a[1] == 2
    assert a[2] == 3
    assert a[3] == 4
    assert a[4] == 5

    assert a[-1] == 5
    assert a[-2] == 4
    assert a[-3] == 3
    assert a[-4] == 2
    assert a[-5] == 1

    with raises(UndefinedIndexError):
        a[6]
    with raises(UndefinedIndexError):
        a[-6]

    assertLinkedListEqual(a[0:3],      [1, 2, 3])
    assertLinkedListEqual(a[0:5:2],    [1, 3, 5])
    assertLinkedListEqual(a[-4:-1],    [2, 3, 4])
    assertLinkedListEqual(a[-1:-4:-1], [5, 4, 3])
    # rules are different for slices!
    # Python lists just clamps 'em for you.
    # so linked_list does too! YOU'RE WELCOME
    assertLinkedListEqual(a[9999:999999], [])
    assertLinkedListEqual(a[9999:999999:-1], [])

    copy_a = a.copy()
    copy_a[5:1:-2] = 'ab'
    assertLinkedListEqual(copy_a, [1, 2, 'b', 4, 'a'])

    copy_a = a.copy()
    copy_a[10000000000:-3239879817998:-2] = 'abc'
    assertLinkedListEqual(copy_a, ['c', 2, 'b', 4, 'a'])

    with raises(TypeError):
        a[1.5:]
    with raises(TypeError):
        a[:1.5]
    with raises(TypeError):
        a[::1.5]
    with raises(ValueError):
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
            with subtest(index=index):
                try:
                    l_value = l[index]
                    passed = True
                except IndexError:
                    with raises(IndexError):
                        t[index]
                    passed = False
                except TypeError:
                    # reminder: None is in values
                    with raises(TypeError):
                        t[index]
                    passed = False

                if passed:
                    # don't merge this into the "try" block above,
                    # we want to notice if this raises IndexError
                    # but a list doesn't.
                    t_value = t[index]
                    assert l_value == t_value

        for step in values_without_zero:
            for stop in values:
                for start in values:
                    with subtest(count=count, start=start, stop=stop, step=step):
                        l_slice = l[start:stop:step]
                        t_slice = t[start:stop:step]

                        assertLinkedListEqual(t_slice, l_slice)

                        if (None not in (start, stop, step)) and (abs(stop - start) < 26):
                            elements = list(range(start, stop, step))
                            replacement = alphabet[:len(elements)]

                            l_copy = l.copy()
                            t_copy = t.copy()
                            try:
                                l_copy[start:stop:step] = replacement
                                t_copy[start:stop:step] = replacement
                                assertLinkedListEqual(t_copy, l_copy)
                            except ValueError:
                                pass

                        if step in (1, None):
                            l_copy = l.copy()
                            t_copy = t.copy()
                            l_copy[start:stop:step] = ('a', 'b', 'c')
                            t_copy[start:stop:step] = ('a', 'b', 'c')
                            assertLinkedListEqual(t_copy, l_copy)

    # __setitem__
    t = setup()
    t[2] = 'rem lezar'
    assertLinkedListEqual(t, (1, 2, 'rem lezar', 4, 5))
    assertNoSpecialNodes(t)

    # assign to slice with same number of elements
    t = setup()
    t[1:4] = 'abc'
    assertLinkedListEqual(t, (1, 'a', 'b', 'c', 5))
    assertNoSpecialNodes(t)

    # ... and with an iterator
    t = setup()
    t[1:4] = iter('abc')
    assertLinkedListEqual(t, (1, 'a', 'b', 'c', 5))
    assertNoSpecialNodes(t)

    # assign to slice with fewer elements
    t = setup()
    t = linked_list((1, 2, 3, 4, 5, 6, 7, 8, 9), lock=_lock())
    t[1:7] = 'ab'
    assertLinkedListEqual(t, (1, 'a', 'b', 8, 9))
    assertNoSpecialNodes(t)

    # ... and with an iterator
    t = setup()
    t = linked_list((1, 2, 3, 4, 5, 6, 7, 8, 9), lock=_lock())
    t[1:7] = iter('ab')
    assertLinkedListEqual(t, (1, 'a', 'b', 8, 9))
    assertNoSpecialNodes(t)

    # assign to slice with surplus elements
    t = setup()
    t[1:4] = 'abcdef'
    assertLinkedListEqual(t, (1, 'a', 'b', 'c', 'd', 'e', 'f', 5))
    assertNoSpecialNodes(t)

    # ... and with an iterator
    t = setup()
    t[1:4] = iter('abcdef')
    assertLinkedListEqual(t, (1, 'a', 'b', 'c', 'd', 'e', 'f', 5))
    assertNoSpecialNodes(t)

    t = setup()
    t[3:0:-1] = 'abc'
    assertLinkedListEqual(t, (1, 'c', 'b', 'a', 5))
    assertNoSpecialNodes(t)

    t = setup()
    t[3:0:-1] = iter('abc')
    assertLinkedListEqual(t, (1, 'c', 'b', 'a', 5))
    assertNoSpecialNodes(t)

    t = setup()
    t[0:5:2] = 'abc'
    assertLinkedListEqual(t, ('a', 2, 'b', 4, 'c'))
    assertNoSpecialNodes(t)

    t = setup()
    t[0:5:2] = iter('abc')
    assertLinkedListEqual(t, ('a', 2, 'b', 4, 'c'))
    assertNoSpecialNodes(t)

    t = setup()
    with raises(TypeError):
        t[1:4] = 55
    with raises(TypeError):
        t[1:4:2] = 55

    with raises(ValueError):
        t[1:4:2] = 'abcdefgh'

    with raises(ValueError):
        t[1:4] = t

    # overwrite a zero-length slice!
    t = setup()
    t[3:3] = []
    assertLinkedListEqual(t, [1, 2, 3, 4, 5])
    assertNoSpecialNodes(t)

    # __delitem__
    t = setup()
    del t[2]
    assertLinkedListEqual(t, (1, 2, 4, 5))
    assertNoSpecialNodes(t)

    t = setup()
    del t[1:4]
    assertLinkedListEqual(t, (1, 5))
    assertNoSpecialNodes(t)

    # none as initializer in slice
    t = setup()
    assertLinkedListEqual(t[:3], (1, 2, 3))
    assertLinkedListEqual(t[2:], (3, 4, 5))
    assertNoSpecialNodes(t)

    # and now--the iterator!
    def setup():
        t = linked_list(range(1, 10), lock=_lock())
        it = t.find(5)
        rit = reversed(it)
        return t, it, rit

    t, it, rit = setup()
    assert it[-1] == 4
    assert it[ 0] == 5
    assert it[ 1] == 6
    assert it[ 2] == 7
    assertLinkedListEqual(it[-1:3], [4, 5, 6, 7])

    # remove node pointed at by it
    rit.pop()
    # and now it raises
    with raises(SpecialNodeError):
        it[-1:3]

    t, it, rit = setup()
    assert rit[-1] == 6
    assert rit[ 0] == 5
    assert rit[ 1] == 4
    assert rit[ 2] == 3
    assertLinkedListEqual(rit[-1:3], [6, 5, 4, 3])

    # remove node pointed at by rit
    it.pop()
    # and now it raises
    with raises(SpecialNodeError):
        rit[-1:3]

    # the rules are different for slices *on iterators*.
    # for example--I *don't* clamp!  YOU'RE WELCOME.
    with raises(ValueError):
        it[1:100]
    with raises(ValueError):
        it[1000:2000]
    with raises(ValueError):
        it[-100:2]
    with raises(ValueError):
        it[-500:-100]

    with raises(ValueError):
        rit[1:100]
    with raises(ValueError):
        rit[1000:2000]
    with raises(ValueError):
        rit[-100:2]
    with raises(ValueError):
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

    with raises(SpecialNodeError):
        it[0]
    with raises(SpecialNodeError):
        it[0:1]
    with raises(SpecialNodeError):
        it[-1:3]

    # regression: I had a bug where this returned [2, 4, 7, 9].
    # it should return [2, 4, 6, 8] as per the below.
    # note that it *doesn't* examine it[0], so it works fine.
    sl = it[-3:5:2]
    assertLinkedListEqual(it[-3:5:2], [2, 4, 6, 8])

    # iterator setitem too
    t, it, rit = setup()
    it[-1] = 'a'
    it[ 0] = 'b'
    it[ 1] = 'c'
    assertLinkedListEqual(t, [1, 2, 3, 'a', 'b', 'c', 7, 8, 9])
    assertNoSpecialNodes(t)

    t, it, rit = setup()
    rit[-1] = 'a'
    rit[ 0] = 'b'
    rit[ 1] = 'c'
    assertLinkedListEqual(t, [1, 2, 3, 'c', 'b', 'a', 7, 8, 9])
    assertNoSpecialNodes(t)

    # assign to slice with the same number of values as items in the slice
    t, it, rit = setup()
    it[-1:3] = 'abcd'
    assertLinkedListEqual(t, [1, 2, 3, 'a', 'b', 'c', 'd', 8, 9])
    assertNoSpecialNodes(t)

    # assign to slice with the same number of values as items in the slice
    t, it, rit = setup()
    it[-1:4] = 'ab'
    assertLinkedListEqual(t, [1, 2, 3, 'a', 'b', 9])
    assertNoSpecialNodes(t)

    # assign to slice with more values than items in the slice
    t, it, rit = setup()
    it[-1:1] = 'abcde'
    assertLinkedListEqual(t, [1, 2, 3, 'a', 'b', 'c', 'd', 'e', 6, 7, 8, 9])
    assertNoSpecialNodes(t)

    # white box testing:
    # also do it with an iterator, rather than a string,
    # because that forces us internally to cast to a list
    t, it, rit = setup()
    it[-1:1] = iter('abcde')
    assertLinkedListEqual(t, [1, 2, 3, 'a', 'b', 'c', 'd', 'e', 6, 7, 8, 9])
    assertNoSpecialNodes(t)

    # assign correctly to "extended slice"
    t, it, rit = setup()
    it2 = t.find(2)
    it4 = t.find(4)
    it6 = t.find(6)
    it2[0:6:2] = 'abc'
    assertLinkedListEqual(t, [1, 'a', 3, 'b', 5, 'c', 7, 8, 9])
    # and the iterators don't move
    assert it2[0] == 'a'
    assert it4[0] == 'b'
    assert it6[0] == 'c'
    assertNoSpecialNodes(t)

    # assign too many values to an "extended slice"
    t, it, rit = setup()
    it = t.find(1)
    with raises(ValueError):
        it[0:6:2] = 'abcdefghijkl'
    # and too few
    with raises(ValueError):
        it[0:6:2] = 'ab'

    # now... reversed!
    # assign to slice with the same number of values as items in the slice
    t, it, rit = setup()
    rit[-1:3] = 'abcd'
    assertLinkedListEqual(t, [1, 2, 'd', 'c', 'b', 'a', 7, 8, 9])
    assertNoSpecialNodes(t)

    # assign to slice with the same number of values as items in the slice
    t, it, rit = setup()
    rit[-1:4] = 'ab'
    assertLinkedListEqual(t, [1, 'b', 'a', 7, 8, 9])
    assertNoSpecialNodes(t)

    # assign to slice with more values than items in the slice
    t, it, rit = setup()
    rit[-1:1] = 'abcde'
    assertLinkedListEqual(t, [1, 2, 3, 4, 'e', 'd', 'c', 'b', 'a', 7, 8, 9])
    assertNoSpecialNodes(t)

    t, it, rit = setup()
    with raises(ValueError):
        it[0:8:2] = 'abcdefghijkl'

    # assign correctly to "extended slice"
    t, it, rit = setup()
    it8 = reversed(t.find(8))
    it6 = reversed(t.find(6))
    it4 = reversed(t.find(4))
    it8[0:6:2] = 'abc'
    assertLinkedListEqual(t, [1, 2, 3, 'c', 5, 'b', 7, 'a', 9])
    # and the iterators don't move
    assert it8[0] == 'a'
    assert it6[0] == 'b'
    assert it4[0] == 'c'
    assertNoSpecialNodes(t)

    # assign too many values to an "extended slice"
    t, it, rit = setup()
    it = t.find(8)
    rit = reversed(it)
    with raises(ValueError):
        rit[0:6:2] = 'abcdefghijkl'
    # and too few
    with raises(ValueError):
        rit[0:6:2] = 'ab'

    # test zero-length slices of iterators
    # len t is 9, it points to 5.
    # confirm the invariants for these tests:
    t, it, rit = setup()
    assert len(t) == 9
    assert it[0] == 5
    for i in range(-4, 5):
        with subtest(i=i):
            t, it, rit = setup()
            assertLinkedListEqual(it[i:i], [])
            assertLinkedListEqual(it[i:i:-1], [])
            assertLinkedListEqual(rit[i:i], [])
            assertLinkedListEqual(rit[i:i:-1], [])

            t, it, rit = setup()
            l = list(t)
            it[i:i] = ['a', 'b', 'c']
            l[i+5:i+5] = ['a', 'b', 'c']
            assertLinkedListEqual(t, l)

            t, it, rit = setup()
            l = list(t)
            rit[i:i] = ['a', 'b', 'c']
            l[4-i:4-i] = ['c', 'b', 'a']
            assertLinkedListEqual(t, l)

    # you can't assign slices to head or tail, neither
    t, it, rit = setup()
    it = t.head()
    rit = reversed(it)
    with raises(UndefinedIndexError):
        rit[0:0] = 'abc'
    with raises(UndefinedIndexError):
        it[0:0] = 'abc'

    t, it, rit = setup()
    it = t.tail()
    rit = reversed(it)
    with raises(UndefinedIndexError):
        it[0:0] = 'abc'
    with raises(UndefinedIndexError):
        rit[0:0] = 'abc'

    # you can't assign self to a slice of self
    with raises(ValueError):
        it[1:3] = t
    with raises(ValueError):
        rit[1:3] = t

    # indices must be, y'know, __index__-icies
    with raises(TypeError):
        t['abc']
    with raises(TypeError):
        it['abc']
    with raises(TypeError):
        rit['abc']
    with raises(TypeError):
        t['abc'] = 5
    with raises(TypeError):
        it['abc'] = 6
    with raises(TypeError):
        rit['abc'] = 7
    with raises(TypeError):
        del t['abc']
    with raises(TypeError):
        del it['abc']
    with raises(TypeError):
        del rit['abc']
    with raises(TypeError):
        t['abc':1]
    with raises(TypeError):
        it['abc':1]
    with raises(TypeError):
        rit['abc':1]
    with raises(TypeError):
        t[1:'abc']
    with raises(TypeError):
        it[1:'abc']
    with raises(TypeError):
        rit[1:'abc']
    with raises(TypeError):
        t[1:2:'abc']
    with raises(TypeError):
        it[1:2:'abc']
    with raises(TypeError):
        rit[1:2:'abc']
    with raises(TypeError):
        t['abc':'def'] = [1, 2, 3]
    with raises(TypeError):
        it['abc':'def'] = [1, 2, 3]
    with raises(TypeError):
        rit['abc':'def'] = [1, 2, 3]
    with raises(TypeError):
        del t['abc':'def']
    with raises(TypeError):
        del it['abc':'def']
    with raises(TypeError):
        del rit['abc':'def']

    with raises(ValueError):
        t[1:2:0]
    with raises(ValueError):
        it[1:2:0]
    with raises(ValueError):
        rit[1:2:0]
    with raises(ValueError):
        t[1:2:0] = 'abc'
    with raises(ValueError):
        it[1:2:0] = 'abc'
    with raises(ValueError):
        rit[1:2:0] = 'abc'
    with raises(ValueError):
        del t[1:2:0]
    with raises(ValueError):
        del it[1:2:0]
    with raises(ValueError):
        del rit[1:2:0]

    # finally, iterator delitem, with slices
    t, it, rit = setup()
    del it[-1]
    assertLinkedListEqual(t, [1, 2, 3,    5, 6, 7, 8, 9])
    assertNoSpecialNodes(t)
    t, it, rit = setup()
    del it[ 0]
    assertLinkedListEqual(t, [1, 2, 3, 4,    6, 7, 8, 9])
    t, it, rit = setup()
    del it[ 1]
    assertLinkedListEqual(t, [1, 2, 3, 4, 5,    7, 8, 9])
    assertNoSpecialNodes(t)
    t, it, rit = setup()
    del it[-1:3]
    assertLinkedListEqual(t, [1, 2, 3,             8, 9])

    t, it, rit = setup()
    del rit[-1]
    assertLinkedListEqual(t, [1, 2, 3, 4, 5,    7, 8, 9])
    assertNoSpecialNodes(t)
    t, it, rit = setup()
    del rit[ 0]
    assertLinkedListEqual(t, [1, 2, 3, 4,    6, 7, 8, 9])
    t, it, rit = setup()
    del rit[ 1]
    assertLinkedListEqual(t, [1, 2, 3,    5, 6, 7, 8, 9])
    assertNoSpecialNodes(t)
    t, it, rit = setup()
    del rit[-1:3]
    assertLinkedListEqual(t, [1, 2,             7, 8, 9])


def test_regressions():
    for _lock in lock_fns():
        regressions_tests(_lock)

def regressions_tests(_lock):
    ##################################
    # regression test 1:
    #
    # reported by Claude Opus 4.6
    #
    # the "head stomping" bug:
    # head.special was getting stomped on!
    #
    # if you had an iterator pointing at a node
    # when you cleared the list, linked_list._clear
    # would demote it to "special".  The code was
    # actually applied to previous:
    #     previous.special = "special"
    #
    # The bug: this happened even if previous
    # already WAS a special node, like head.
    #
    # The fix: only "demote" previous to "special"
    # if it's a data node.
    for value in (1, 2, 3):
        with subtest(value=value):
            ll = linked_list([1, 2, 3], lock=_lock())
            head = ll.head()
            it = ll.find(value)
            ll.clear()
            assert head.special == 'head'
            assertLinkedListEqual(ll, [])
            assertIsSpecial(it)


    ##################################
    # regression test 2:
    #
    # reported by Claude Opus 4.6
    #
    # this raised ZeroDivisonError!
    # this was because len(ll) is zero.
    # which we did check for--but only
    # AFTER doing n % self._length, oops!
    #
    # the fix: bail out earlier if self._length < 2.
    # (if zero nodes: nothing to rotate:
    #  if one node: nothing changes.)

    ll = linked_list()
    ll.rotate(1)


def test_regression_reset_and_exhaust_relocate_iterators():
    for _lock in lock_fns():
        with subtest(_lock=_lock):
            ll = linked_list([1, 2, 3], lock=_lock())
            it = ll.find(2)
            it_copy = it.copy()
            it_copy.pop()
            it_copy._del()
            assertIsSpecial(it)
            it.reset()
            assertIsHead(it)
            assertNoSpecialNodes(ll)
            assert ll._head.iterator_refcount == 1
            it._del()
            assert ll._head.iterator_refcount == 0

            ll = linked_list([1, 2, 3], lock=_lock())
            it = ll.find(2)
            it_copy = it.copy()
            it_copy.pop()
            it_copy._del()
            assertIsSpecial(it)
            it.exhaust()
            assertIsTail(it)
            assertNoSpecialNodes(ll)
            assert ll._tail.iterator_refcount == 1
            it._del()
            assert ll._tail.iterator_refcount == 0

            ll = linked_list([1, 2, 3], lock=_lock())
            dit = ll.find(2)
            dit_copy = dit.copy()
            dit_copy.pop()
            dit_copy._del()
            rit = reversed(dit)
            dit._del()
            assertIsSpecial(rit)
            rit.reset()
            assertIsTail(rit)
            assertNoSpecialNodes(ll)
            assert ll._tail.iterator_refcount == 1
            rit._del()
            assert ll._tail.iterator_refcount == 0

            ll = linked_list([1, 2, 3], lock=_lock())
            dit = ll.find(2)
            dit_copy = dit.copy()
            dit_copy.pop()
            dit_copy._del()
            rit = reversed(dit)
            dit._del()
            assertIsSpecial(rit)
            rit.exhaust()
            assertIsHead(rit)
            assertNoSpecialNodes(ll)
            assert ll._head.iterator_refcount == 1
            rit._del()
            assert ll._head.iterator_refcount == 0

def test_regression_imul_uses_private_extend_inside_lock():
    class NoReenterLock:
        def __init__(self):
            self._lock = Lock()
            self._held = False

        def acquire(self):
            if self._held:
                raise RuntimeError('recursive acquire attempted')
            self._lock.acquire()
            self._held = True
            return True

        def release(self):
            self._held = False
            self._lock.release()

        def __enter__(self):
            self.acquire()
            return self

        def __exit__(self, exc_type, exc, tb):
            self.release()
            return False

        def __bool__(self):
            return True

    ll = linked_list([1, 2, 3], lock=NoReenterLock())
    ll *= 2
    assertLinkedListEqual(ll, [1, 2, 3, 1, 2, 3])

    lock = NoReenterLock()
    lock.acquire()
    try:
        with raises(RuntimeError):
            lock.acquire()
    finally:
        lock.release()

def test_regression_reverse_short_lists_return_none_without_iterators():
    for _lock in lock_fns():
        with subtest(_lock=_lock):
            ll = linked_list(lock=_lock())
            assert ll.reverse() is None
            assert ll._head.iterator_refcount == 0
            assert ll._tail.iterator_refcount == 0

            ll = linked_list([1], lock=_lock())
            assert ll.reverse() is None
            assertLinkedListEqual(ll, [1])
            assert ll._head.iterator_refcount == 0
            assert ll._tail.iterator_refcount == 0

def test_regression_cut_and_splice_refresh_iterator_lock_caches():
    class RecordingLock:
        def __init__(self, name, events):
            self.name = name
            self.events = events
            self._lock = Lock()

        def acquire(self):
            self.events.append(f'acquire {self.name}')
            self._lock.acquire()
            return True

        def release(self):
            self.events.append(f'release {self.name}')
            self._lock.release()

        def __enter__(self):
            self.acquire()
            return self

        def __exit__(self, exc_type, exc, tb):
            self.release()
            return False

        def __bool__(self):
            return True

    events = []
    old_lock = RecordingLock('old', events)
    new_lock = RecordingLock('new', events)
    ll = linked_list([1, 2, 3, 4, 5], lock=old_lock)
    start = ll.find(2)
    mid = ll.find(3)
    stop = ll.find(4)

    snippet = ll.cut(start, stop, lock=new_lock)
    assertLinkedListEqual(ll, [1, 4, 5])
    assertLinkedListEqual(snippet, [2, 3])
    assert start._lock is new_lock
    assert stop._lock is old_lock
    assert mid._lock is old_lock

    events.clear()
    probe = mid.after(0)
    probe._del()
    assert 'acquire new' in events
    assert 'release new' in events
    assert mid._lock is new_lock

    events.clear()
    probe = stop.after(0)
    probe._del()
    assert events == ['acquire old', 'release old']

    lock_a = RecordingLock('A', events)
    lock_b = RecordingLock('B', events)
    lock_c = RecordingLock('C', events)
    source = linked_list([1, 2, 3, 4], lock=lock_a)
    start = source.find(1)
    middle = source.find(2)
    stop = source.find(4)
    snippet = source.cut(start, stop, lock=lock_b)
    other = linked_list([9], lock=lock_c)

    events.clear()
    middle.splice(other)
    assert 'acquire B' in events
    assert 'acquire C' in events
    assert middle._lock is lock_b
    assertLinkedListEqual(snippet, [1, 2, 9, 3])
    assertLinkedListEqual(other, [])

def test_regression_extendleft_accepts_plain_iterators():
    for _lock in lock_fns():
        with subtest(_lock=_lock):
            ll = linked_list([1, 2, 3], lock=_lock())
            ll.extendleft(iter('abc'))
            assertLinkedListEqual(ll, ['c', 'b', 'a', 1, 2, 3])

def test_regression_reverse_and_sort_move_nodes_not_values():
    for _lock in lock_fns():
        with subtest(operation='reverse', _lock=_lock):
            ll = linked_list([1, 'X', 2, 3], lock=_lock())
            it1 = ll.find(1)
            it2 = ll.find(2)
            it3 = ll.find(3)
            special = ll.find('X')
            special_copy = special.copy()
            special_copy.pop()
            special_copy._del()
            node1 = it1._cursor
            node2 = it2._cursor
            node3 = it3._cursor

            assert ll.reverse() is None
            assertLinkedListEqual(ll, [3, 2, 1])
            assert it1._cursor is node1
            assert it1[0] == 1
            assert it2._cursor is node2
            assert it2[0] == 2
            assert it3._cursor is node3
            assert it3[0] == 3
            assert special.before()[0] == 2
            assert special.after()[0] == 1

        with subtest(operation='sort', _lock=_lock):
            ll = linked_list([2, 'X', 'Y', 3, 1], lock=_lock())
            it1 = ll.find(1)
            it2 = ll.find(2)
            it3 = ll.find(3)
            special_x = ll.find('X')
            special_y = ll.find('Y')
            special_x_copy = special_x.copy()
            special_x_copy.pop()
            special_x_copy._del()
            special_y_copy = special_y.copy()
            special_y_copy.pop()
            special_y_copy._del()
            node1 = it1._cursor
            node2 = it2._cursor
            node3 = it3._cursor

            assert ll.sort() is None
            assertLinkedListEqual(ll, [1, 2, 3])
            assert it1._cursor is node1
            assert it1[0] == 1
            assert it2._cursor is node2
            assert it2[0] == 2
            assert it3._cursor is node3
            assert it3[0] == 3
            assert special_x.before()[0] == 2
            assert special_x.after()[0] == 3
            assert special_y.before()[0] == 2
            assert special_y.after()[0] == 3


def test_misc_methods():
    for _lock in lock_fns():
        misc_methods_tests(_lock)

def misc_methods_tests(_lock):
    # sort
    l = [5, 20, -3, 3, 44, 4, 3, 6, 8, 3, 8]
    t = linked_list(l, lock=_lock())
    l.sort()
    t.sort()
    assertLinkedListEqual(t, l)

    # reverse
    l.reverse()
    t.reverse()
    assertLinkedListEqual(t, l)

    l.append(88)
    t.append(88)
    l.reverse()
    t.reverse()
    assertLinkedListEqual(t, l)


    # count
    for v in l:
        assert t.count(v) == l.count(v)

    # insert
    for index in range(-7, 7):
        with subtest(index=index):
            a = [1, 2, 3, 4, 5]
            a.insert(index, 'x')
            t = linked_list((1, 2, 3, 4, 5), lock=_lock())
            t.insert(index, 'x')
            assertLinkedListEqual(t, a)

    with raises(TypeError):
        t.insert('this is not a valid index', 'abc')

    # regression: reverse crashed if t was empty
    t = linked_list(lock=_lock())
    t.reverse()
    assertLinkedListEqual(t, [])

    l = []
    for i in range(1, 10):
        t.append(i)
        l.append(i)
        t.reverse()
        l.reverse()
        assertLinkedListEqual(t, l)

    # rotate
    initializer = ('x', 2, 3, 4, 5, 6, 7, 8, 9)
    d = collections.deque(initializer)
    t = linked_list(d, lock=_lock())

    for i in range(-10, 11):
        with subtest(i=i):
            t_copy = t.copy()
            t_copy.rotate(i)
            d_copy = d.copy()
            d_copy.rotate(i)
            assert list(t_copy) == list(d_copy)

    with raises(TypeError):
        t.rotate(3.14159)

    # rremove
    t2 = t * 2
    t2.rremove(2)
    assertLinkedListEqual(t2, ('x', 2, 3, 4, 5, 6, 7, 8, 9, 'x', 3, 4, 5, 6, 7, 8, 9))
    with raises(ValueError):
        t2.rremove('abx')
    assert t2.rremove('abz', 45) == 45

    # iterator rremove
    it = reversed(reversed(t2)) # it is a forwards iterator pointed at tail!
    it.rremove(4)
    assertLinkedListEqual(t2, ('x', 2, 3, 4, 5, 6, 7, 8, 9, 'x', 3, 5, 6, 7, 8, 9))
    with raises(ValueError):
        it.rremove('abx')
    assert it.rremove('abz', 77) == 77

    # by using the one in big.types,
    # we get the real one in 3.9+
    # and the fake one for 3.7-3.8
    linked_list_int = big.types.GenericAlias(linked_list, (int,))
    if python_version >= Version("3.7"): # pragma: nocover
        assert linked_list[int] == linked_list_int
    else: # pragma: nocover
        assert linked_list_int == 'linked_list[int]'

def test_misc_dunder_methods():
    for _lock in lock_fns():
        misc_dunder_methods_test(_lock)

    t = linked_list('a')
    assert repr(t) == "linked_list(['a'])"

    class FakeLock:
        def ignore(self, *a, **kw):
            pass
        acquire = release = __enter__ = __exit__ = ignore
        def __repr__(self):
            return '<FakeLock>'
    t = linked_list('a', lock=FakeLock())
    assert repr(t) == "linked_list(['a'], lock=<FakeLock>)"

def misc_dunder_methods_test(_lock):
    t = linked_list((1, 2, 3, 4, 5), lock=_lock())

    # __deepcopy__
    t1 = linked_list(({1:2}, {3:4}))
    t2 = copy.deepcopy(t1)
    assert t1 == t2
    for v1, v2 in zip(t1, t2):
        assert v1 == v2
        assert not (v1 is v2)

    # __add__
    t1 = linked_list((1, 2, 3))
    t2 = linked_list((4, 5, 6))
    t3 = t1 + t2
    assertLinkedListEqual(t3, (1, 2, 3, 4, 5, 6))

    # __iadd__
    t1 = linked_list((1, 2, 3))
    t2 = linked_list((4, 5, 6))
    t2 += t1
    assertLinkedListEqual(t2, (4, 5, 6, 1, 2, 3))

    # __mul__
    t4 = t1 * 3
    assertLinkedListEqual(t4, (1, 2, 3, 1, 2, 3, 1, 2, 3))
    with raises(TypeError):
        t1 * [3,4]
    with raises(TypeError):
        t1 * 2+1j
    t4 = t1 * 0
    assertLinkedListEqual(t4, [])

    # __imul__
    t5 = t1
    t5 *= 4
    assertLinkedListEqual(t5, (1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3))
    with raises(TypeError):
        t5 *= [3,4]
    with raises(TypeError):
        t5 *= 2+1j
    t5 *= 0
    assertLinkedListEqual(t5, [])

    # __contains__
    assert 3 in t
    assert 'x' not in t

def test_misc_iterator_methods():
    for _lock in lock_fns():
        misc_iterator_methods_test(_lock)

def misc_iterator_methods_test(_lock):
    def setup():
        t = linked_list(range(1, 11), lock=_lock())
        it = t.find(5)
        return t, it

    # __contains__
    t, it = setup()
    assert 7 in it
    assert 3 not in it
    assert 'x' not in it

    # __copy__
    it2 = it.copy()
    assert it == it2
    it3 = copy.copy(it)
    assert it == it3

    assert t is it.linked_list

    # next and previous
    with raises(TypeError):
        it.next(count=5.5)
    with raises(ValueError):
        it.next(count=-5)
    with raises(TypeError):
        it.previous(count=5.5)
    with raises(ValueError):
        it.previous(count=-5)

    it = t.find(5)
    assert it[0] == 5
    it.next(count=0)
    assert it[0] == 5
    it.next(count=3)
    assert it[0] == 8
    it = t.find(5)
    it.next(None, count=3)
    assert it[0] == 8

    it = t.find(5)
    assert it[0] == 5
    it.previous(count=0)
    assert it[0] == 5
    it.previous(count=3)
    assert it[0] == 2
    it = t.find(5)
    it.previous(None, count=3)
    assert it[0] == 2

    it = t.tail()
    assertIsTail(it)
    with raises(StopIteration):
        it.next()
    assertIsTail(it)
    got = it.next('abc')
    assertIsTail(it)
    assert got == 'abc'

    it = t.head()
    assertIsHead(it)
    with raises(StopIteration):
        it.previous()
    assertIsHead(it)
    got = it.previous('xyz')
    assertIsHead(it)
    assert got == 'xyz'

    t, it = setup()
    assert it[0] == 5

    with raises(TypeError):
        it2 = it.before(3.14159)
    with raises(ValueError):
        it2 = it.before(-1)
    it2 = it.before(4)
    assert it2[0] == 1
    it3 = it.before(5)
    assertIsHead(it3)

    with raises(TypeError):
        it2 = it.after(3.14159)
    with raises(ValueError):
        it2 = it.after(-1)
    it4 = it.after(4)
    assert it4[0] == 9
    it5 = it.after(6)
    assertIsTail(it5)

    t, it = setup()
    assertLinkedListEqual(t, [1, 2, 3, 4,   5,  6,   7, 8, 9, 10])
    it[0] = 'x'
    assertLinkedListEqual(t, [1, 2, 3, 4, 'x',  6,   7, 8, 9, 10])
    del it[0]
    assertLinkedListEqual(t, [1, 2, 3, 4,       6,   7, 8, 9, 10])
    it[2] = 'z'
    assertLinkedListEqual(t, [1, 2, 3, 4,       6, 'z', 8, 9, 10])
    del it[2]
    assertLinkedListEqual(t, [1, 2, 3, 4,       6,      8, 9, 10])

    t = linked_list((1, 'x', 2, 'x', 3, 'x', 4, 'x', 5, 'x', 6, 'x', 7, 'x', 8), lock=_lock())
    it = t.find(5)
    assert it.count('x') == 3
    assert it.rcount('x') == 4

    t, it = setup()
    it.insert(3, 'zz')
    assertLinkedListEqual(t, [1, 2, 3, 4, 5, 6, 7, 'zz', 8, 9, 10])
    it.insert(-2, 'qq')
    assertLinkedListEqual(t, [1, 2, 'qq', 3, 4, 5, 6, 7, 'zz', 8, 9, 10])
    it = t.head()
    with raises(UndefinedIndexError):
        it.insert(0, 'xx')
    it = t.tail()
    it.insert(0, 'yy')
    assertLinkedListEqual(t, [1, 2, 'qq', 3, 4, 5, 6, 7, 'zz', 8, 9, 10, 'yy'])
    it = t.find(10)
    it.insert(0, 'oo')
    assertLinkedListEqual(t, [1, 2, 'qq', 3, 4, 5, 6, 7, 'zz', 8, 9, 'oo', 10, 'yy'])

def test_truncate():
    for _lock in lock_fns():
        truncate_tests(_lock)

def truncate_tests(_lock):
    def setup():
        t = linked_list(range(1, 11), lock=_lock())
        it_5 = t.find(5)
        t2 = linked_list('abcde', lock=_lock())
        return t, it_5, t2

    # truncate no nodes
    t, it_5, t2 = setup()
    assert len(t) == 10
    it = t.tail()
    it.truncate()
    assertLinkedListEqual(t, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert len(t) == 10
    assert t
    assertIsTail(it)

    t, it_5, t2 = setup()
    it = t.head()
    it.rtruncate()
    assertLinkedListEqual(t, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert len(t) == 10
    assert t
    assertIsHead(it)

    # truncate all the nodes!
    t, it_5, t2 = setup()
    it = t.find(1)
    it.truncate()
    assertLinkedListEqual(t, [])
    assert len(t) == 0
    assert not (t)
    assertIsTail(it)

    t, it_5, t2 = setup()
    it = t.find(10)
    it.rtruncate()
    assertLinkedListEqual(t, [])
    assert len(t) == 0
    assert not (t)
    assertIsHead(it)

    # can't truncate head
    t, it_5, t2 = setup()
    it = t.head()
    with raises(SpecialNodeError):
        it.truncate()
    # can't rtruncate a reverse iterator pointing at head.
    # (say *that* three times fast!)
    rit = reversed(it)
    with raises(SpecialNodeError):
        rit.rtruncate()

    # rtruncating at "tail" is the same as truncating at the last data node.
    t, it_5, t2 = setup()
    it = t.tail()
    with raises(SpecialNodeError):
        it.rtruncate()
    # can't truncate a reverse iterator pointing at tail.
    rit = reversed(it)
    with raises(SpecialNodeError):
        rit.truncate()

    # truncate some nodes, ensuring we have an iterator
    # pointing to one of the nodes we throw away
    t, it_5, t2 = setup()
    it_7 = t.find(7)
    it_5.truncate()
    assertLinkedListEqual(t, [1, 2, 3, 4])
    assert len(t) == 4
    assert t
    assertIsTail(it_5)

    t, it_5, t2 = setup()
    it_2 = t.find(2)
    it_5.rtruncate()
    assertLinkedListEqual(t, [6, 7, 8, 9, 10])
    assert len(t) == 5
    assert t
    assertIsHead(it_5)


def test_cut_and_splice():
    for _lock in lock_fns(True):
        cut_and_splice_tests(_lock)

    # splicing from a list WITH a lock
    # into a list WITHOUT a lock
    t = linked_list([1, 2, 3, 4, 5])
    it = t.find(3)
    t2 = linked_list('abc', lock=Lock())

    it.splice(t2)
    assertLinkedListEqual(t, [1, 2, 3, 'a', 'b', 'c', 4, 5])
    assertLinkedListEqual(t2, [])

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
        with subtest(lock1=lock1, lock2=lock2):
            t, it, t2 = setup(lock1, lock2)
            t.splice(t2)
            assertLinkedListEqual(t, [1, 2, 3, 4, 5, 'a', 'b', 'c'])

            t, it, t2 = setup(lock1, lock2)
            t.splice(t2, where=it)
            assertLinkedListEqual(t, [1, 2, 3, 'a', 'b', 'c', 4, 5])

            t, it, t2 = setup(lock1, lock2)
            it.splice(t2)
            assertLinkedListEqual(t, [1, 2, 3, 'a', 'b', 'c', 4, 5])


def cut_and_splice_tests(_lock):
    def setup():
        t = linked_list(range(1, 11), lock=_lock())
        it_5 = t.find(5)
        t2 = linked_list('abcde', lock=_lock())
        return t, it_5, t2

    def check_linked_list_was_set(t):
        it = iter(t)
        assertIsHead(it)
        assert it.linked_list is t, "failed on t.head"
        for _ in it:
            assert it.linked_list is t, f"failed on it={it!r}"
        assertIsTail(it)
        assert it.linked_list is t, "failed on t.tail"

    # splicing an empty linked_list does nothing
    t, it_5, t2 = setup()
    t_list = list(t)

    t2 = linked_list()
    t.splice(t2)
    assertLinkedListEqual(t, t_list)
    it_5.splice(t2)
    assertLinkedListEqual(t, t_list)
    rit = reversed(it_5)
    rit.splice(t2)
    assertLinkedListEqual(t, t_list)

    t2 = linked_list()
    t.rsplice(t2)
    assertLinkedListEqual(t, t_list)
    it_5.rsplice(t2)
    assertLinkedListEqual(t, t_list)
    rit = reversed(it_5)
    rit.rsplice(t2)
    assertLinkedListEqual(t, t_list)

    # can't splice t into t
    with raises(ValueError):
        t.splice(t)
    with raises(ValueError):
        t.rsplice(t)
    with raises(ValueError):
        it_5.splice(t)
    with raises(ValueError):
        it_5.rsplice(t)


    # on a forward iterator, can't cut head
    t, it_5, t2 = setup()
    it_head = iter(t)
    with raises(SpecialNodeError):
        it_head.cut()
    with raises(SpecialNodeError):
        t.cut(it_head, None)

    # on a reversed iterator, can't cut tail
    rit_tail = reversed(t)
    with raises(SpecialNodeError):
        rit_tail.cut()
    with raises(SpecialNodeError):
        t.cut(rit_tail)

    # on a forward iterator, can't rcut tail
    t, it_5, t2 = setup()
    it_tail = t.tail()
    with raises(SpecialNodeError):
        it_tail.rcut()
    with raises(SpecialNodeError):
        t.rcut(it_tail, None)

    # on a reverse iterator, can't rcut head
    t, it_5, t2 = setup()
    rit_head = reversed(t.head())
    with raises(SpecialNodeError):
        rit_head.rcut()
    with raises(SpecialNodeError):
        t.rcut(rit_head, None)

    with raises(TypeError):
        t.cut(5, None)
    with raises(TypeError):
        t.cut(None, 5)
    with raises(TypeError):
        t.rcut(5, None)
    with raises(TypeError):
        t.rcut(None, 5)

    # if start and stop both point to head,
    # cut returns an empty list.
    unchanged_t = list(t)
    head = t.head()

    got = t.cut(head, head, lock=_lock())
    assertLinkedListEqual(t, unchanged_t)
    assertLinkedListEqual(got, [])

    got = head.cut(head, lock=_lock())
    assertLinkedListEqual(t, unchanged_t)
    assertLinkedListEqual(got, [])

    head = reversed(head)
    got = t.cut(head, head, lock=_lock())
    assertLinkedListEqual(t, unchanged_t)
    assertLinkedListEqual(got, [])

    got = head.cut(head, lock=_lock())
    assertLinkedListEqual(t, unchanged_t)
    assertLinkedListEqual(got, [])

    # if start and stop both point to tail,
    # cut returns an empty list.
    tail = t.tail()

    got = t.cut(tail, tail, lock=_lock())
    assertLinkedListEqual(t, unchanged_t)
    assertLinkedListEqual(got, [])

    got = tail.cut(tail, lock=_lock())
    assertLinkedListEqual(t, unchanged_t)
    assertLinkedListEqual(got, [])

    tail = reversed(tail)
    got = t.cut(tail, tail, lock=_lock())
    assertLinkedListEqual(t, unchanged_t)
    assertLinkedListEqual(got, [])

    got = tail.cut(tail, lock=_lock())
    assertLinkedListEqual(t, unchanged_t)
    assertLinkedListEqual(got, [])


    t, it_5, t2 = setup()
    snippet = it_5.cut(lock=_lock())
    assert isinstance(snippet, linked_list)
    assertLinkedListEqual(t,       [1, 2, 3, 4])
    assert len(t) == 4
    assertLinkedListEqual(snippet,             [5, 6, 7, 8, 9, 10])
    assert len(snippet) == 6
    check_linked_list_was_set(t)
    check_linked_list_was_set(snippet)

    for test_reversed in (False, True):
        for splice_at_the_end in (False, True):
            with subtest(test_reversed=test_reversed, splice_at_the_end=splice_at_the_end):
                t, it_5, t2 = setup()
                it_7 = t.find(7)

                snippet = it_5.cut(stop=it_7, lock=_lock())
                assert isinstance(snippet, linked_list)
                assertLinkedListEqual(snippet, [5, 6])
                assert len(snippet) == 2
                assertLinkedListEqual(t, [1, 2, 3, 4, 7, 8, 9, 10])
                assert len(t) == 8
                check_linked_list_was_set(t)
                check_linked_list_was_set(snippet)

                if splice_at_the_end:
                    if test_reversed:
                        splice_here = reversed(t2)
                    else:
                        splice_here = iter(t2)
                    splice_here.exhaust()
                    splice_here.previous()
                else:
                    splice_here = t2.find('c')
                    if test_reversed:
                        splice_here = reversed(splice_here)
                    assert splice_here[0] == 'c'

                splice_here.splice(snippet)
                assertLinkedListEqual(snippet, [])

                if splice_at_the_end:
                    if test_reversed:
                        assertLinkedListEqual(t2, [5, 6, 'a', 'b', 'c', 'd', 'e'])
                    else:
                        assertLinkedListEqual(t2, ['a', 'b', 'c', 'd', 'e', 5, 6])
                else:
                    if test_reversed:
                        assertLinkedListEqual(t2, ['a', 'b', 5, 6, 'c', 'd', 'e'])
                    else:
                        assertLinkedListEqual(t2, ['a', 'b', 'c', 5, 6, 'd', 'e'])
                check_linked_list_was_set(t)
                check_linked_list_was_set(t2)
                assert len(t2) == 7
                assert len(snippet) == 0


    t, it_5, t2 = setup()
    rit_5 = reversed(it_5)
    snippet = rit_5.cut(lock=_lock())
    assert isinstance(snippet, linked_list)
    assertLinkedListEqual(snippet, [1, 2, 3, 4,  5])
    assert len(snippet) == 5
    assertLinkedListEqual(t,                       [6, 7, 8, 9, 10])
    assert len(t) == 5
    check_linked_list_was_set(t)
    check_linked_list_was_set(snippet)

    t2.splice(snippet)
    assertLinkedListEqual(snippet, [])
    assert len(snippet) == 0
    assertLinkedListEqual(t2, ['a', 'b', 'c', 'd', 'e', 1, 2, 3, 4, 5])
    assert len(t2) == 10
    check_linked_list_was_set(t)
    check_linked_list_was_set(t2)
    check_linked_list_was_set(snippet)

    t, it_5, t2 = setup()
    rit_5 = reversed(it_5)
    it_2 = t.find(2)
    with raises(ValueError):
        rit_5.cut(it_2)
    rit_2 = reversed(it_2)
    snippet = rit_5.cut(rit_2, lock=_lock())
    assertLinkedListEqual(t,       [1, 2,         6, 7, 8, 9, 10])
    assert len(t) == 7
    assertLinkedListEqual(snippet,       [3, 4, 5])
    assert len(snippet) == 3
    check_linked_list_was_set(t)
    check_linked_list_was_set(snippet)

    # rit moved to snippet when the nodes were cut.  which means
    # these calls raise an exception! which means NOTHING CHANGED, RIGHT?
    with raises(ValueError):
        t.cut(rit_5)
    with raises(ValueError):
        t.cut(stop=rit_5)
    assertLinkedListEqual(t,       [1, 2,         6, 7, 8, 9, 10])
    assert len(t) == 7
    assertLinkedListEqual(snippet,       [3, 4, 5])
    assert len(snippet) == 3
    check_linked_list_was_set(t)
    check_linked_list_was_set(snippet)

    it = t.head().after()
    t2 = t.cut(stop=it, lock=_lock())
    assert len(t) == 7
    assertLinkedListEqual(t2, [])
    assert len(t2) == 0

    t, it_5, t2 = setup()
    it_2 = t.find(2)
    with raises(ValueError):
        # end comes before start
        t.cut(it_5, it_2)
    rit_5 = reversed(it_5)
    rit_2 = reversed(it_2)
    with raises(ValueError):
        # end comes before start
        t.cut(rit_2, rit_5)

    t, it_5, t2 = setup()
    snippet = it_5.rcut(lock=_lock())
    assertLinkedListEqual(t,       [6, 7, 8, 9, 10])
    assert len(t) == 5
    assertLinkedListEqual(snippet, [1, 2, 3, 4, 5])
    assert len(snippet) == 5
    assert it_5.linked_list is snippet
    check_linked_list_was_set(t)
    check_linked_list_was_set(snippet)

    t, it_5, t2 = setup()
    it = t.tail().before()
    snippet = it.rcut(lock=_lock())
    assertLinkedListEqual(t,       [])
    assert len(t) == 0
    assertLinkedListEqual(snippet, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert len(snippet) == 10
    assert it.linked_list is snippet
    check_linked_list_was_set(t)
    check_linked_list_was_set(snippet)

    with raises(TypeError):
        t.splice([1, 2, 3])
    with raises(TypeError):
        t.splice('abcde')
    with raises(TypeError):
        t.splice(8675309)
    with raises(TypeError):
        t.splice(3.14159)

    with raises(TypeError):
        t.splice(t2, where=1234567890)
    with raises(TypeError):
        t.splice(t2, where=t2)
    with raises(ValueError):
        t.splice(t2, where=t2.head())

    with raises(TypeError):
        it.splice([1, 2, 3])
    with raises(TypeError):
        it.splice('abcde')
    with raises(TypeError):
        it.splice(8675309)
    with raises(TypeError):
        it.splice(3.14159)

    t, it_5, t2 = setup()
    # you can't splice after tail
    with raises(UndefinedIndexError):
        t.splice(t2, where=t.tail())
    with raises(UndefinedIndexError):
        t.tail().splice(t2)

    # you can't rsplice before head
    with raises(UndefinedIndexError):
        t.rsplice(t2, where=t.head())
    with raises(UndefinedIndexError):
        t.head().rsplice(t2)


    t, it_5, t2 = setup()
    t2_tail = t2.tail()
    t.splice(t2)
    check_linked_list_was_set(t)
    assert len(t) == 15
    assert len(t2) == 0

    with raises(ValueError):
        t.splice(t)

    # rsplice without where
    t, it_5, t2 = setup()
    t.rsplice(t2)
    assertLinkedListEqual(t, ['a', 'b', 'c', 'd', 'e', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # reverse iterator splice and rsplice
    t, it_5, t2 = setup()
    rit = reversed(it_5)
    rit.splice(t2)
    assertLinkedListEqual(t, [1, 2, 3, 4, 'a', 'b', 'c', 'd', 'e', 5, 6, 7, 8, 9, 10])

    t, it_5, t2 = setup()
    rit = reversed(it_5)
    rit.rsplice(t2)
    assertLinkedListEqual(t, [1, 2, 3, 4, 5, 'a', 'b', 'c', 'd', 'e', 6, 7, 8, 9, 10])

    # splice does NOT move head and tail.
    t = linked_list(lock=_lock())
    t2 = linked_list('abcde', lock=_lock())
    head = t2.head()
    tail = t2.tail()
    t.splice(t2)
    assertLinkedListEqual(t, ['a', 'b', 'c', 'd', 'e'])
    assertLinkedListEqual(t2, [])
    t2.append('X')
    head.next()
    tail.previous()
    assert head[0] == 'X'
    assert tail[0] == 'X'


    def setup():
        t = linked_list((1, 2, 3, 4, 5), lock=_lock())
        middle = t.find(3)
        return t, t.head(), middle, t.tail()

    t, head, middle, tail = setup()
    snippet = t.cut(start=None, stop=middle, lock=_lock())
    assert head.linked_list is t
    assert tail.linked_list is t
    check_linked_list_was_set(t)
    check_linked_list_was_set(snippet)

    t, head, middle, tail = setup()
    snippet = t.cut(start=head.after(), stop=middle, lock=_lock())
    assert head.linked_list is t
    assert tail.linked_list is t


    t, head, middle, tail = setup()
    snippet = t.cut(start=middle, stop=None, lock=_lock())
    assert head.linked_list is t
    assert tail.linked_list is t

    t, head, middle, tail = setup()
    snippet = t.cut(start=middle, stop=tail, lock=_lock())
    assert head.linked_list is t
    assert tail.linked_list is t

    # test rcut with start=None!
    t, head, middle, tail = setup()
    snippet = t.rcut(None, middle, lock=_lock())
    assertLinkedListEqual(snippet, [4, 5])
    assertLinkedListEqual(t, [1, 2, 3])

    # test cutting only special nodes!
    def setup():
        t = linked_list((1,), lock=_lock())
        it = t.find(1)
        del it[0]
        return t, it

    t, it = setup()
    t2 = t.cut(lock=_lock())
    assert it.linked_list == t2

    t, it = setup()
    t2 = it.cut(lock=_lock())
    assert it.linked_list == t2

    t, it = setup()
    t2 = t.rcut(lock=_lock())
    assert it.linked_list == t2

    t, it = setup()
    t2 = it.rcut(lock=_lock())
    assert it.linked_list == t2


def test_move_and_rmove():
    for _lock in lock_fns():
        move_and_rmove_tests(_lock)

def move_and_rmove_tests(_lock):
    def setup():
        t = linked_list(range(1, 8), lock=_lock())
        return t, t.head(), t.tail()

    t, head, tail = setup()
    t.move(t.find(6), t.find(2), t.find(5))
    assertLinkedListEqual(t, [1, 5, 6, 2, 3, 4, 7])

    t, head, tail = setup()
    start = t.find(2)
    stop = t.find(5)
    where = t.find(6)
    start.move(where, stop)
    assertLinkedListEqual(t, [1, 5, 6, 2, 3, 4, 7])
    assert start[0] == 2
    assert start.linked_list is t

    # always illegal to move nodes after tail
    t, head, tail = setup()
    with raises(UndefinedIndexError):
        t.move(tail, t.find(1), t.find(3))
    # ... even if the range is empty
    with raises(UndefinedIndexError):
        t.move(tail, t.find(1), t.find(1))

    # always illegal to rmove nodes before head
    t, head, tail = setup()
    with raises(UndefinedIndexError):
        t.rmove(head, t.find(3), t.find(1))
    # ... even if the range is empty
    with raises(UndefinedIndexError):
        t.rmove(head, t.find(1), t.find(1))


    t, head, tail = setup()
    t.move(t.find(7), t.find(2), t.find(4))
    assertLinkedListEqual(t, [1, 4, 5, 6, 7, 2, 3])

    t, head, tail = setup()
    t.rmove(t.find(1), t.find(5), t.find(2))
    assertLinkedListEqual(t, [3, 4, 5, 1, 2, 6, 7])

    t, head, tail = setup()
    t.rmove(t.find(2), t.find(6), t.find(3))
    assertLinkedListEqual(t, [1, 4, 5, 6, 2, 3, 7])

    t, head, tail = setup()
    start = t.find(6)
    stop = t.find(3)
    where = t.find(2)
    start.rmove(where, stop)
    assertLinkedListEqual(t, [1, 4, 5, 6, 2, 3, 7])
    assert start[0] == 6
    assert start.linked_list is t

    t, head, tail = setup()
    rit_start = reversed(t.find(6))
    rit_stop = reversed(t.find(3))
    where = t.find(2)
    t.move(where, rit_start, rit_stop)
    assertLinkedListEqual(t, [1, 4, 5, 6, 2, 3, 7])
    assert rit_start[0] == 6
    assert rit_start.linked_list is t

    t, head, tail = setup()
    rit_start = reversed(t.find(6))
    rit_stop = reversed(t.find(3))
    where = t.find(2)
    rit_start.move(where, rit_stop)
    assertLinkedListEqual(t, [1, 4, 5, 6, 2, 3, 7])
    assert rit_start[0] == 6
    assert rit_start.linked_list is t

    t, head, tail = setup()
    rit_start = reversed(t.find(2))
    rit_stop = reversed(t.find(5))
    where = t.find(6)
    rit_start.rmove(where, rit_stop)
    assertLinkedListEqual(t, [1, 5, 6, 2, 3, 4, 7])
    assert rit_start[0] == 2
    assert rit_start.linked_list is t

    t, head, tail = setup()
    unchanged = list(t)
    t.move(t.find(6), t.find(4), t.find(4))
    assertLinkedListEqual(t, unchanged)

    t, head, tail = setup()
    with raises(ValueError):
        t.move(t.find(3), t.find(2), t.find(5))
    with raises(ValueError):
        t.rmove(t.find(5), t.find(6), t.find(3))

    t, head, tail = setup()
    t2, _, _ = setup()
    t.move(t.find(1), head, head)
    assertLinkedListEqual(t, t2)
    t.rmove(t.find(1), head, head)
    assertLinkedListEqual(t, t2)
    t.move(t.find(1), tail, tail)
    assertLinkedListEqual(t, t2)
    t.rmove(t.find(1), tail, tail)
    assertLinkedListEqual(t, t2)

    # move special nodes too.
    t = linked_list([1, 2, 3, 4], lock=_lock())
    it_2 = t.find(2)
    del it_2[0]
    t.move(t.head(), it_2, t.find(4))
    assertLinkedListEqual(t, [3, 1, 4])
    assertIsSpecial(it_2)
    assert it_2.after()[0] == 3


def test_reverse_iterators():
    for _lock in lock_fns():
        reverse_iterators_tests(_lock)

def reverse_iterators_tests(_lock):
    def setup():
        t = linked_list((1, 2, 3, 4, 5, 6, 7, 8, 9), lock=_lock())
        it = t.find(5)
        rit = reversed(it)
        return t, it, rit

    t, it, rit = setup()
    assert it == reversed(rit)
    assert rit == reversed(reversed(rit))

    assert rit[0] == 5
    assert len(rit) == 5
    next(rit)
    assert rit[0] == 4
    assert len(rit) == 4
    rit.previous()
    assert rit[0] == 5
    assert len(rit) == 5

    before = rit.before()
    assert before[0] == 6
    assert len(before) == 6
    after = rit.after()
    assert after[0] == 4
    assert len(after) == 4


    assert rit
    rit.reset()
    assertIsTail(rit)
    assert rit
    rit.exhaust()
    assertIsHead(rit)
    assert not (rit)

    t, it, rit = setup()
    assert rit.count(2) == 1
    assert rit.count(7) == 0
    assert rit.rcount(2) == 0
    assert rit.rcount(7) == 1
    r2 = reversed(t.find(2))
    r7 = reversed(t.find(7))
    assert rit.find(2) == r2
    assert rit.find(7) == None
    assert rit.rfind(2) == None
    assert rit.rfind(7) == r7

    assert rit.match(lambda v: v == 2) == r2
    assert rit.match(lambda v: v == 7) == None
    assert rit.rmatch(lambda v: v == 2) == None
    assert rit.rmatch(lambda v: v == 7) == r7

    t, it, rit = setup()
    rit.append('x')
    assertLinkedListEqual(t, [1, 2, 3, 4, 'x', 5, 6, 7, 8, 9])

    t, it, rit = setup()
    rit.prepend('x')
    assertLinkedListEqual(t, [1, 2, 3, 4, 5, 'x', 6, 7, 8, 9])

    t, it, rit = setup()
    rit.extend('abc')
    assertLinkedListEqual(t, [1, 2, 3, 4, 'c', 'b', 'a', 5, 6, 7, 8, 9])

    t, it, rit = setup()
    rit.rextend('abc')
    assertLinkedListEqual(t, [1, 2, 3, 4, 5, 'c', 'b', 'a', 6, 7, 8, 9])

    t, it, rit = setup()
    value = rit.pop()
    assert value == 5
    assertLinkedListEqual(t, [1, 2, 3, 4, 6, 7, 8, 9])
    assert rit[0] == 6

    t, it, rit = setup()
    value = rit.rpop()
    assert value == 5
    assertLinkedListEqual(t, [1, 2, 3, 4, 6, 7, 8, 9])
    assert rit[0] == 4

    t, it, rit = setup()
    rit.truncate()
    assertLinkedListEqual(t, [6, 7, 8, 9])

    t, it, rit = setup()
    rit.rtruncate()
    assertLinkedListEqual(t, [1, 2, 3, 4])

def test_list_compatibility():
    for _lock in lock_fns():
        list_compatibility_tests(_lock)

def list_compatibility_tests(_lock):
    def setup():
        return linked_list(range(1, 10), lock=_lock())

    t = setup()
    for i in range(1, 10):
        with subtest(i=i):
            assert t.index(i) == i - 1

    with raises(ValueError):
        t.index('abc')
    with raises(ValueError):
        t.index(4.5)
    with raises(ValueError):
        t.index(None)
    with raises(TypeError):
        t.index(1, start=1.5)
    with raises(TypeError):
        t.index(1, stop=1.5)

    assert t.index(4, start=1, stop=5) == 3
    assert t.index(4, start=-9, stop=-1) == 3
    with raises(ValueError):
        t.index(1, start=1, stop=5)
    with raises(ValueError):
        t.index(1, start=-8, stop=-5)
    with raises(ValueError):
        t.index(9, start=1, stop=5)
    with raises(ValueError):
        t.index(9, start=-10, stop=-5)

    with raises(ValueError):
        t.index(9, start=3, stop=2)
    with raises(ValueError):
        t.index(9, start=12)

    t = linked_list(lock=_lock())
    with raises(ValueError):
        t.index('empty list')

def test_index_edge_cases():
    t = linked_list([1, 2, 3, 4, 5])
    assert t.index(3, -999, 4) == 2
    with raises(ValueError):
        t.index(3, 4, 3)
    with raises(ValueError):
        t.index(5, 0, 4)
    assert t.__lt__(1) is NotImplemented
    assert not (t.__lt__(t))
    assert t != linked_list([1, 2, 3])

def test_cut_mismatched_iterators_and_head_head():
    t = linked_list([1, 2, 3])
    head = t.head()
    empty = t.cut(head, head)
    assertLinkedListEqual(empty, [])
    it = t.find(2)
    rit = reversed(t.find(3))
    with raises(ValueError):
        t.cut(it, rit)

def test_iterator_lock_refresh_paths():
    t = linked_list([1, 2, 3])
    it = t.find(2)

    class ChangingLock:
        def __init__(self, iterator, replacement):
            self.iterator = iterator
            self.replacement = replacement
            self.acquired = 0
            self.released = 0
        def acquire(self):
            self.acquired += 1
            self.iterator._lock = self.replacement
        def release(self):
            self.released += 1

    lock = ChangingLock(it, None)
    it._lock = lock
    it.reset()
    assert lock.acquired == 1
    assert lock.released == 1
    assertIsHead(it)

    it = t.find(2)
    lock = ChangingLock(it, None)
    it._lock = lock
    it.exhaust()
    assert lock.acquired == 1
    assert lock.released == 1
    assertIsTail(it)

    it = t.find(2)
    lock = ChangingLock(it, None)
    it._lock = lock
    assert not (it.is_special)
    assert lock.acquired == 1
    assert lock.released == 1

def test_iterator_after_past_tail_and_setstate():
    t = linked_list([1, 2, 3], lock=True)
    it = t.find(3)
    with raises(UndefinedIndexError):
        it.after(2)
    state = it.__getstate__()
    it2 = object.__new__(type(it))
    it2.__setstate__(state)
    assert it2._lock is t._lock
    assert it2[0] == 3

def test_rotate_and_extendleft_coverage():
    t = linked_list([1])
    assert t.maxlen is None
    t.rotate(-1)
    assertLinkedListEqual(t, [1])

    t = linked_list([1, 2, 3, 4])
    t.rotate(-1)
    assertLinkedListEqual(t, [2, 3, 4, 1])
    t.rotate(0)
    assertLinkedListEqual(t, [2, 3, 4, 1])

    class Iterable:
        def __iter__(self):
            return iter(('a', 'b', 'c'))
    t = linked_list([1, 2, 3])
    t.extendleft(Iterable())
    assertLinkedListEqual(t, ['c', 'b', 'a', 1, 2, 3])

def test_deque_compatibility():
    for _lock in lock_fns():
        deque_compatibility_tests(_lock)

def deque_compatibility_tests(_lock):
    def setup():
        return linked_list(range(1, 10), lock=_lock())
    t = setup()
    t.extendleft('abc')
    assertLinkedListEqual(t, ['c', 'b', 'a', 1, 2, 3, 4, 5, 6, 7, 8, 9])
    with raises(ValueError):
        t.extendleft(t)

def test_pickle():
    def pickle_lock_iterator():
        yield lambda: False
        yield lambda: True
        yield lambda: None

    for _lock in pickle_lock_iterator():
        pickle_tests(_lock)

    t = linked_list([1, 2, 3], lock=Lock())
    with raises(ValueError):
        p = pickle.dumps(t)

def pickle_tests(_lock):
    def setup():
        t = linked_list((1, 2, 3, 4, 5, 6, 7, 8, 9), lock=_lock())
        it = t.find(5)
        rit = reversed(it)
        return t, it, rit
    t, it, rit = setup()

    p = pickle.dumps(t)
    t2 = pickle.loads(p)
    assert isinstance(t, linked_list)
    assert t == t2

    p = pickle.dumps(it)
    it2 = pickle.loads(p)
    assert isinstance(it, linked_list_iterator)
    assert it[0] == it2[0]
    assert t == it2.linked_list

    p = pickle.dumps(rit)
    rit2 = pickle.loads(p)
    assert isinstance(rit, linked_list_reverse_iterator)
    assert rit[0] == rit2[0]
    assert t == rit2.linked_list

def test_coverage():
    assert repr(big.types._undefined) == '<Undefined>'
    assert repr(big.types._inert_context_manager) == '<inert_context_manager>'


    with raises(TypeError):
        linked_list([1, 2, 3], lock=object())

    # has acquire and release, but isn't a context manager
    class FakeLock:
        def acquire(self): # pragma: nocover
            pass
        def release(self): # pragma: nocover
            pass

    with raises(TypeError):
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

    with raises(TypeError):
        linked_list([1, 2, 3], lock=FakeLock2())





def test_string_additional_coverage_cases():
    assert abcde.__radd__(123) is NotImplemented

    s = string('   xyz', source='test.py')
    stripped = s.lstrip()
    assert str(stripped) == 'xyz'
    assert stripped.source == 'test.py'
    assert stripped.offset == 3

    samples = [
        (abcde, slice(None, None, -1)),
        (abcde, slice(4, 0, -2)),
        (abcde, slice(-20, None, 2)),
        (abcde, slice(1, -1, 2)),
    ]
    for value, sl in samples:
        with subtest(value=value, sl=sl):
            assert str(value[sl]) == str(value)[sl]

    s = string('hello world', source='test.py')
    sub = s[5:5]
    ctx = sub.context
    assert str(ctx) == 'hello world\n     ^'
    assert ctx.parts.string.linebreak == ''
    assert ctx.parts.highlight.linebreak == ''

def test_linked_list_internal_reverse_and_sort_coverage():
    t = linked_list([1, 'X', 2, 3])
    special = t.find('X')
    special_copy = special.copy()
    special_copy.pop()
    special_copy._del()
    with t._lock or big.types._inert_context_manager:
        assert [node.value for node in t._internal_reversed()] == [3, 2, 1]

    empty = linked_list()
    assert empty.sort() is None
    singleton = linked_list([5])
    assert singleton.sort() is None
    t2 = linked_list([3, 1, 2])
    t2.sort(key=lambda value: -value)
    assertLinkedListEqual(t2, [3, 2, 1])

def test_linked_list_move_error_and_edge_coverage():
    t = linked_list(range(1, 8), lock=Lock())
    foreign = linked_list(range(10, 13), lock=Lock())
    where = t.find(4)

    with raises(TypeError):
        t.move(object(), t.find(2), t.find(5))
    with raises(ValueError):
        t.move(foreign.find(11), t.find(2), t.find(5))
    with raises(TypeError):
        t.move(where, object(), t.find(5))
    with raises(ValueError):
        t.move(where, foreign.find(11), t.find(5))
    with raises(TypeError):
        t.move(where, t.find(2), object())
    with raises(ValueError):
        t.move(where, t.find(2), foreign.find(11))

    with raises(ValueError):
        t.move(where, t.find(2), reversed(t.find(5)))

    t2 = linked_list(range(1, 8))
    unchanged = list(t2)
    t2.move(t2.head())
    assertLinkedListEqual(t2, unchanged)

    t3 = linked_list(range(1, 8))
    t3.rmove(t3.tail())
    assertLinkedListEqual(t3, [1, 2, 3, 4, 5, 6, 7])

    t4 = linked_list(range(1, 8))
    with raises(ValueError):
        t4.move(t4.find(1), t4.find(5), t4.find(3))
    with raises(ValueError):
        t4.move(t4.find(3), t4.find(2), t4.find(5))

    t5 = linked_list(range(1, 8))
    t5.move(t5.find(6), t5.find(7), t5.tail())
    assertLinkedListEqual(t5, [1, 2, 3, 4, 5, 6, 7])

    t6 = linked_list(range(1, 8))
    t6.rmove(t6.find(2), t6.find(1), t6.head())
    assertLinkedListEqual(t6, [1, 2, 3, 4, 5, 6, 7])

    t7 = linked_list(range(1, 8))
    with raises(SpecialNodeError):
        t7.move(t7.find(3), t7.head(), t7.find(5))
    with raises(SpecialNodeError):
        t7.rmove(t7.find(3), t7.tail(), t7.find(2))

def test_linked_list_iterator_cleanup_and_misc_coverage():
    t = linked_list([1, 2, 3])
    it = t.find(2)
    state = it.__getstate__()
    it2 = object.__new__(type(it))
    it2.__setstate__(state)
    assert it2._lock is t._lock
    assert it2[0] == 2

    assert it2._internal_lock() is t._lock
    assert it2.linked_list == t

    it2._relocate(it2._cursor)
    assert it2[0] == 2

    it2._del()
    it2._del()
    assert it2._cursor is None

    class SneakyLock:
        def __init__(self, iterator):
            self.iterator = iterator
        def acquire(self):
            self.iterator._cursor = None
            return True
        def release(self):
            return None
        def __bool__(self):
            return True

    t3 = linked_list([1])
    it3 = t3.find(1)
    t3._lock = SneakyLock(it3)
    it3._lock = t3._lock
    it3.__del__()
    assert it3._cursor is None

    t4 = linked_list([1, 2, 3])
    it4 = t4.find(3)
    assert bool(it4)
    assert it4.special == None

    assert linked_list([1]).__lt__(object()) is NotImplemented

def test_regression_imul_lock_coverage():
    class NoReenterLock:
        def __init__(self):
            self._lock = Lock()
            self._held = False

        def acquire(self):
            if self._held:
                raise RuntimeError('recursive acquire attempted')
            self._lock.acquire()
            self._held = True
            return True

        def release(self):
            self._held = False
            self._lock.release()

        def __enter__(self):
            self.acquire()
            return self

        def __exit__(self, exc_type, exc, tb):
            self.release()
            return False

        def __bool__(self):
            return True

    lock = NoReenterLock()
    assert lock
    with lock:
        assert lock._held
    lock.acquire()
    try:
        with raises(RuntimeError):
            lock.acquire()
    finally:
        lock.release()

def run_tests(run=None):
    (run or bigtestlib.run)(name="big.types", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
