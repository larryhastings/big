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
import copy
import math
import re
import sys
import unittest


try:
    import inflect
    engine = inflect.engine()
except ImportError: # pragma: no cover
    engine = None


try:
    from re import Pattern as re_Pattern
except ImportError: # pragma: no cover
    re_Pattern = re._pattern_type

try:
    import regex
    have_regex = True
except ImportError: # pragma: no cover
    have_regex = False

def unchanged(o):
    return o

def to_bytes(o): # pragma: no cover
    if o is None:
        return None
    if isinstance(o, str):
        return o.encode('ascii')
    if isinstance(o, list):
        return [to_bytes(x) for x in o]
    if isinstance(o, tuple):
        return tuple(to_bytes(x) for x in o)
    if isinstance(o, re_Pattern):
        flags = o.flags
        if flags & re.UNICODE:
            flags = flags - re.UNICODE
        o = re.compile(to_bytes(o.pattern), flags=flags)
    return o


known_separators = [
    (big.whitespace, "big.whitespace"),
    (big.whitespace_without_dos, "big.whitespace_without_dos"),
    (big.newlines,   "big.newlines"),
    (big.newlines_without_dos,   "big.newlines_without_dos"),

    (big.ascii_whitespace, "big.ascii_whitespace"),
    (big.ascii_whitespace_without_dos, "big.ascii_whitespace_without_dos"),
    (big.ascii_newlines,   "big.ascii_newlines"),
    (big.ascii_newlines_without_dos,   "big.ascii_newlines_without_dos"),

    (big.utf8_whitespace, "big.utf8_whitespace"),
    (big.utf8_whitespace_without_dos, "big.utf8_whitespace_without_dos"),
    (big.utf8_newlines,   "big.utf8_newlines"),
    (big.utf8_newlines_without_dos,   "big.utf8_newlines_without_dos"),
]

def printable_separators(separators):
    for known, name in known_separators:
        if separators == known:
            return f"{name}"
    return separators

class StrSubclass(str):
    def __repr__(self): # pragma: no cover
        return f"<StrSubclass {str(self)!r}>"

class DifferentStrSubclass(str):
    def __repr__(self): # pragma: no cover
        return f"<DifferentStrSubclass {str(self)!r}>"

class BytesSubclass(bytes):
    def __repr__(self): # pragma: no cover
        return f"<BytesSubclass {bytes(self)!r}>"

class DifferentBytesSubclass(bytes):
    def __repr__(self): # pragma: no cover
        return f"<DifferentBytesSubclass {bytes(self)!r}>"


def group0(re_partition_result):
    result = []
    for i, o in enumerate(re_partition_result):
        if (i % 2) and (o is not None):
            o = o.group(0)
        result.append(o)
    return tuple(result)

def finditer_group0(i):
    return tuple(match.group(0) for match in i)


class BigTextTests(unittest.TestCase):

    def test_whitespace_and_newlines(self):
        # ensure that big.whitespace and big.newlines
        # correctly matches the list of characters that
        # Python considers whitespace / newlines.

        # Python whitespace only considers individual
        # whitespace charcters, and doesn't include the
        # DOS end-of-line sequence '\r\n'.  so what we're
        # going to produce in the below list is technically
        # the "without DOS" versions.
        python_whitespace_without_dos = []
        python_newlines_without_dos = []

        # technically we don't need to check the surrogate pair characters.
        # but it's faster to leave them in.
        unicode_code_points = 2**16 + 2**20

        for i in range(unicode_code_points):
            c = chr(i)
            s = f"a{c}b"
            if len(s.split()) == 2:
                python_whitespace_without_dos.append(c)
                if len(s.splitlines()) == 2:
                    python_newlines_without_dos.append(c)

        self.assertEqual(set(big.whitespace_without_dos), set(python_whitespace_without_dos))
        self.assertEqual(set(big.newlines_without_dos), set(python_newlines_without_dos))

        python_whitespace = list(python_whitespace_without_dos)
        python_whitespace.append("\r\n")
        python_newlines = list(python_newlines_without_dos)
        python_newlines.append("\r\n")
        self.assertEqual(set(big.whitespace), set(python_whitespace))
        self.assertEqual(set(big.newlines), set(python_newlines))

        # now test the utf-8 and ascii variants!

        python_ascii_whitespace = big.text._cheap_encode_iterable_of_strings(python_whitespace, 'ascii')
        self.assertEqual(set(big.ascii_whitespace), set(python_ascii_whitespace))
        python_ascii_whitespace_without_dos = big.text._cheap_encode_iterable_of_strings(python_whitespace_without_dos, 'ascii')
        self.assertEqual(set(big.ascii_whitespace_without_dos), set(python_ascii_whitespace_without_dos))
        python_ascii_newlines = big.text._cheap_encode_iterable_of_strings(python_newlines, 'ascii')
        self.assertEqual(set(big.ascii_newlines), set(python_ascii_newlines))
        python_ascii_newlines_without_dos = big.text._cheap_encode_iterable_of_strings(python_newlines_without_dos, 'ascii')
        self.assertEqual(set(big.ascii_newlines_without_dos), set(python_ascii_newlines_without_dos))

        python_utf8_whitespace = big.text._cheap_encode_iterable_of_strings(python_whitespace, 'utf8')
        self.assertEqual(set(big.utf8_whitespace), set(python_utf8_whitespace))
        python_utf8_whitespace_without_dos = big.text._cheap_encode_iterable_of_strings(python_whitespace_without_dos, 'utf8')
        self.assertEqual(set(big.utf8_whitespace_without_dos), set(python_utf8_whitespace_without_dos))
        python_utf8_newlines = big.text._cheap_encode_iterable_of_strings(python_newlines, 'utf8')
        self.assertEqual(set(big.utf8_newlines), set(python_utf8_newlines))
        python_utf8_newlines_without_dos = big.text._cheap_encode_iterable_of_strings(python_newlines_without_dos, 'utf8')
        self.assertEqual(set(big.utf8_newlines_without_dos), set(python_utf8_newlines_without_dos))

        # now test the cached reversed builtin separators!
        for forwards, backwards in big.text._reversed_builtin_separators.items():
            self.assertEqual(set(backwards), set(big.text._multisplit_reversed(forwards)), f"failed on {printable_separators(forwards)}")

    def test_reversed_re_finditer(self):
        # Cribbed off the test suite from the 'regex' package
        def test(pattern, string, expected):
            pattern = c(pattern)
            string = c(string)
            expected = c(expected)
            got = finditer_group0(big.reversed_re_finditer(pattern, string))

            if have_regex:
                # confirm first that we match regex's output
                if isinstance(pattern, re_Pattern):
                    p = pattern.pattern
                else:
                    p = pattern
                p = regex.compile(p, regex.REVERSE)
                regex_result = finditer_group0(p.finditer(string))
                # print(f"{pattern=} {string=} {regex_result=} {got=}")
                self.assertEqual(regex_result, got)

            self.assertEqual(expected, got)

        for c in (unchanged, to_bytes):
            test(r'abcdef', 'abcdef', ('abcdef',))
            test('.', 'abc', ('c', 'b', 'a'))
            test('..', 'abcde', ('de', 'bc'))
            test('.-.', 'a-b-c', ('b-c',))
            test('a|b', '111a222', ('a',))
            test(re.compile('b|a'), '111a222', ('a',))
            test('x|X', 'xaxbXcxd', ('x', 'X', 'x', 'x',))
            test(r'estonia\w', 'fine estonian workers', ('estonian',))
            test(r'\westonia', 'fine nestonian workers', ('nestonia',))

            # this zero-length match stuff is blowing my mind
            test(r'q*', 'qqwe',   ('', '', 'qq', ''))
            test(r'q*', 'xyqqwe', ('', '', 'qq', '', '', ''))
            test(r'q*', 'xyqq',   ('qq', '', '', ''))
            test(r'q*', 'qq',     ('qq', ''))
            test(r'q*', 'q-qqwe',   ('', '', 'qq', '', 'q', ''))
            test(r'q*', 'xyq-qqwe', ('', '', 'qq', '', 'q', '', '', ''))
            test(r'q*', 'xyq-qq',   ('qq', '', 'q', '', '', ''))
            test(r'q*', 'q-qq',     ('qq', '', 'q', ''))

            test(r'bcd|cde', 'abcdefg',     ('cde',))

            # force a zero-length match to have the same start as a
            # test(r'q*', 'aqqwe',   ('', '', 'qq', '', ''))

            test(r'.{2}', 'abc', ('bc',))
            test(r'\w+ \w+', 'first second third fourth fifth', ('fourth fifth', 'second third'))

            # Python 3.7 fixed a long-standing bug with zero-width matching.
            # See https://github.com/python/cpython/issues/44519
            assert sys.version_info.major >= 3
            if (sys.version_info.major == 3) and (sys.version_info.minor <= 6):  # pragma: no cover
                # wrong, but consistent
                result = ('bar', 'oo', '')
            else:
                # correct
                result = ('bar', 'foo', '')
            test(r'^|\w+', 'foo bar', result)

            # regression test: the initial implementation got this wrong.
            # it never truncated
            test(r'cdefghijk|bcd|fgh|jkl', 'abcdefghijklmnopqrstuvwxyz', ('jkl', 'fgh', 'bcd'))

    def test_re_partition(self):
        def test_re_partition(s, pattern, count, expected):
            self.assertEqual(group0(big.re_partition(c(s), c(pattern), count)), c(expected))

        def test_re_rpartition(s, pattern, count, expected):
            s = c(s)
            pattern = c(pattern)
            expected = c(expected)

            self.assertEqual(group0(big.re_rpartition(s, pattern, count)), expected)
            self.assertEqual(group0(big.re_partition(s, pattern, count, reverse=True)), expected)

            # We implicitly test reversed_re_finditer
            # every time we test re_rpartition.
            #
            # But, if regex is installed, let's throw
            # in an explicit test for reversed_re_finditer too.
            # We run it directly on the pattern & string
            # inputs we use to test re_rpartition,
            # then compare its output with the output of
            # the regex library with REVERSE mode turned on.
            if have_regex:
                if isinstance(pattern, re_Pattern):
                    p = pattern.pattern
                else:
                    p = pattern
                p = regex.compile(p, regex.REVERSE)
                regex_result = finditer_group0(p.finditer(s))
                big_result = finditer_group0(big.reversed_re_finditer(pattern, s))
                self.assertEqual(regex_result, big_result)


        for c in (unchanged, to_bytes):

            pattern = c("[0-9]+")

            s = "abc123def456ghi"
            test_re_partition( s, pattern, 1, ("abc", "123", "def456ghi") )
            test_re_rpartition(s, pattern, 1, ("abc123def", "456", "ghi") )

            s = "abc12345def67890ghi"
            test_re_partition( s, pattern, 1, ("abc", "12345", "def67890ghi") )
            test_re_rpartition(s, pattern, 1, ("abc12345def", "67890", "ghi") )

            pattern = re.compile(pattern)
            test_re_partition( s, pattern, 1, ("abc", "12345", "def67890ghi") )
            test_re_rpartition(s, pattern, 1, ("abc12345def", "67890", "ghi") )

            pattern = c("fa+rk")
            test_re_partition( s, pattern, 1, ("abc12345def67890ghi", None, "") )
            test_re_rpartition(s, pattern, 1, ("", None, "abc12345def67890ghi") )

            # test overlapping matches
            pattern = c("thisANDthis")
            s = c("thisANDthisANDthis")
            test_re_partition( s, pattern, 1, ("", "thisANDthis", "ANDthis") )
            test_re_rpartition(s, pattern, 1, ("thisAND", "thisANDthis", "") )

            for fn in (big.re_partition, big.re_rpartition):
                s = c("Let's find the number 89 in this string")
                pattern = c(r"number ([0-9]+)")
                result = fn(s, pattern)
                # print(result)
                # print(group0(result))
                self.assertEqual(group0(result), c(("Let's find the ", "number 89", " in this string")))
                match = result[1]
                self.assertEqual(match.group(0), c("number 89"))
                self.assertEqual(match.group(1), c("89"))

            test_re_partition("a:b:c:d", ":", 0, ("a:b:c:d",) )
            test_re_partition("a:b:c:d", ":", 1, ("a",       ":",  "b:c:d" ) )
            test_re_partition("a:b:c:d", ":", 2, ("a",       ":",  "b", ":",  "c:d" ) )
            test_re_partition("a:b:c:d", ":", 3, ("a",       ":",  "b", ":",  "c", ":",  "d" ) )
            test_re_partition("a:b:c:d", ":", 4, ("a",       ":",  "b", ":",  "c", ":",  "d", None, '') )
            test_re_partition("a:b:c:d", ":", 5, ("a",       ":",  "b", ":",  "c", ":",  "d", None, '', None, '') )
            test_re_partition("a:b:c:d", "x", 5, ("a:b:c:d", None, '',  None, '',  None, '',  None, '', None, '') )

            test_re_rpartition("a:b:c:d", ":", 0, ("a:b:c:d",) )
            test_re_rpartition("a:b:c:d", ":", 1, ("a:b:c", ':',  "d") )
            test_re_rpartition("a:b:c:d", ":", 2, ("a:b",   ":",  "c", ":",  "d") )
            test_re_rpartition("a:b:c:d", ":", 3, ("a",     ":",  "b", ":",  "c", ":",  "d") )
            test_re_rpartition("a:b:c:d", ":", 4, ("",      None, "a", ":",  "b", ":",  "c", ":",  "d") )
            test_re_rpartition("a:b:c:d", ":", 5, ("",      None, '',  None, "a", ":",  "b", ":",  "c", ":",  "d") )
            test_re_rpartition("a:b:c:d", "x", 5, ('',      None, '',  None, '',  None, '',  None, '',  None, "a:b:c:d") )

            # reverse mode, overlapping matches tests
            test_re_rpartition('abcdefgh', '(abcdef|efg|ab|b|c|d)', 4, ('', 'ab', '', 'c', '', 'd', '', 'efg', 'h') )
            test_re_rpartition('abcdefgh', '(abcdef|efg|a|b|c|d)', 4,  ('a', 'b', '', 'c', '', 'd', '', 'efg', 'h') )

            test_re_rpartition('abcdef', '(bcd|cde|cd)', 1, ('ab', 'cde', 'f') )
            test_re_rpartition('abcdef', '(bcd|cd)',     1, ('a', 'bcd', 'ef') )

            # add x's to the beginning and end of s 100 times
            pattern = '(bcdefghijklmn|nop)'
            s = 'abcdefghijklmnopq'
            before = 'abcdefghijklm'
            after = 'q'
            for i in range(100):
                test_re_rpartition(s, pattern, 1, (before, 'nop', after) )
                s = 'x' + s + 'x'
                before = 'x' + before
                after += 'x'

            # match against xyz and a long string, we should always prefer xyz,
            # progressively truncate characters from the *front* of the long string
            s = 'abcdefghijklmnopqrstuvwxyz'
            first_pattern = s[:-1]
            while first_pattern:
                if len(first_pattern) >= 3:
                    pattern = f'({first_pattern}|xyz)'
                else:
                    pattern = f'(xyz|{first_pattern})'
                test_re_rpartition(s, pattern, 1, ('abcdefghijklmnopqrstuvw', 'xyz', ''))
                first_pattern = first_pattern[1:]

            # match against xyz and a long string, we should always prefer xyz,
            # progressively truncate characters from the *end* of the long string
            s = 'abcdefghijklmnopqrstuvwxyz'
            first_pattern = s[:-1]
            while first_pattern:
                if len(first_pattern) >= 3:
                    pattern = f'({first_pattern}|xyz)'
                else:
                    pattern = f'(xyz|{first_pattern})'
                test_re_rpartition(s, pattern, 1, ('abcdefghijklmnopqrstuvw', 'xyz', ''))
                first_pattern = first_pattern[:-1]

            # 'abcdefghij' is the best match!
            # all the overlapping matches are worse!
            test_re_rpartition('abcdefghijk', '(abcdefghij|abcde|abcd|abc|ab|bc|cd|de|ef|fg|gh|hi|ij)', 1, ('', 'abcdefghij', 'k') )

            # okay, now jk is the best match.
            test_re_rpartition('abcdefghijkl', '(abcdefghij|abcde|abcd|abc|ab|bc|cd|de|ef|fg|gh|hi|ij|jk)', 1, ('abcdefghi', 'jk', 'l') )

            test_re_rpartition('abcdefgh', '(bcd|cdefgh|de)', 1, ('ab', 'cdefgh', '') )
            test_re_rpartition('abcdefgh', '(abcdef|efg|fb|b|c|d)', 4, ('a', 'b', '', 'c', '', 'd', '', 'efg', 'h') )
            test_re_rpartition('abcdefgh', '(abcdef|efg|ab|b|c|d)', 4, ('', 'ab', '', 'c', '', 'd', '', 'efg', 'h') )

        # do bytes vs str testing
        s = "abc123def456ghi"
        bytes_pattern = b"[0-9]+"
        with self.assertRaises(TypeError):
            big.re_partition(s, bytes_pattern)
        with self.assertRaises(TypeError):
            big.re_rpartition(s, bytes_pattern)

        bytes_pattern = re.compile(bytes_pattern)
        with self.assertRaises(TypeError):
            big.re_partition(s, bytes_pattern)
        with self.assertRaises(TypeError):
            big.re_rpartition(s, bytes_pattern)

        with self.assertRaises(ValueError):
            big.re_partition('a:b', ':', -1)
        with self.assertRaises(ValueError):
            big.re_partition(b'a:b', b':', -1)

        self.assertEqual(group0(big.re_partition(StrSubclass("a:b:c:d"), StrSubclass(":"))),
            ("a", ":", "b:c:d") )
        self.assertEqual(group0(big.re_partition(StrSubclass("a:b:c:d"), DifferentStrSubclass(":"))),
            ("a", ":", "b:c:d") )

        self.assertEqual(group0(big.re_partition(BytesSubclass(b"a:b:c:d"), BytesSubclass(b":"))),
            (b"a", b":", b"b:c:d") )
        self.assertEqual(group0(big.re_partition(BytesSubclass(b"a:b:c:d"), DifferentBytesSubclass(b":"))),
            (b"a", b":", b"b:c:d") )

        with self.assertRaises(ValueError):
            big.re_partition('ab c de', ' ', count=-1)

        with self.assertRaises(ValueError):
            big.re_rpartition('ab c de', ' ', count=-1)



    def test_multistrip(self):
        def test_multistrip(original_left, original_s, original_right, original_separators):
            for round in range(4):
                if round == 0:
                    left = original_left
                    s = original_s
                    right = original_right
                    separators = original_separators
                elif round == 1:
                    left = StrSubclass(left)
                    s = StrSubclass(s)
                    right = StrSubclass(right)
                    if isinstance(separators, str):
                        separators = StrSubclass(separators)
                    else:
                        separators = [StrSubclass(o) for o in separators]
                elif round == 2:
                    left = original_left.encode('ascii')
                    s = original_s.encode('ascii')
                    right = original_right.encode('ascii')
                    if original_separators == big.whitespace:
                        separators = big.ascii_whitespace
                    elif original_separators == big.newlines:
                        separators = big.ascii_newlines
                    else:
                        assert isinstance(original_separators, str)
                        separators = original_separators.encode('ascii')
                elif round == 3:
                    left = BytesSubclass(left)
                    s = BytesSubclass(s)
                    right = BytesSubclass(right)
                    if isinstance(separators, bytes):
                        separators = BytesSubclass(separators)
                    else:
                        separators = tuple((BytesSubclass(o) for o in separators))

                self.assertEqual(big.multistrip(s, separators, left=False, right=False), s)
                self.assertEqual(big.multistrip(s, separators, left=False, right=True ), s)
                self.assertEqual(big.multistrip(s, separators, left=True,  right=False), s)
                self.assertEqual(big.multistrip(s, separators, left=True,  right=True ), s)

                ls = left + s
                self.assertEqual(big.multistrip(ls, separators, left=False, right=False), ls)
                self.assertEqual(big.multistrip(ls, separators, left=False, right=True ), ls)
                self.assertEqual(big.multistrip(ls, separators, left=True,  right=False), s)
                self.assertEqual(big.multistrip(ls, separators, left=True,  right=True ), s)

                sr = s + right
                self.assertEqual(big.multistrip(sr, separators, left=False, right=False), sr)
                self.assertEqual(big.multistrip(sr, separators, left=False, right=True ), s)
                self.assertEqual(big.multistrip(sr, separators, left=True,  right=False), sr)
                self.assertEqual(big.multistrip(sr, separators, left=True,  right=True ), s)

                lsr = left + s + right
                self.assertEqual(big.multistrip(lsr, separators, left=False, right=False), lsr)
                self.assertEqual(big.multistrip(lsr, separators, left=False, right=True ), ls)
                self.assertEqual(big.multistrip(lsr, separators, left=True,  right=False), sr)
                self.assertEqual(big.multistrip(lsr, separators, left=True,  right=True ), s)

        test_multistrip(" \t \n ", "abcde", " \n \t ", " \t\n")
        test_multistrip(" \t \n ", "abcde", " \n \t ", big.whitespace)
        test_multistrip("\r\n\n\r", "abcde", "\n\r\r\n", big.newlines)
        test_multistrip("\r\n\n\r", "abcde", "\n\r\r\n", big.whitespace)
        test_multistrip("xXXxxxXx", "iiiiiii", "yyYYYyyyyy", "xyXY")

        # test mixed subclasses of str and bytes
        self.assertEqual(big.multistrip(StrSubclass('  abcde  '), DifferentStrSubclass(' ')), 'abcde')
        self.assertEqual(big.multistrip(BytesSubclass(b'  abcde  '), DifferentBytesSubclass(b' ')), b'abcde')

        # this should be covered in the loop above,
        # but we'll explicitly check it anyway:
        # multistrip *always* returns either str or bytes
        # objects, even when it doesn't strip anything.
        self.assertEqual(big.multistrip(StrSubclass('abcde'), StrSubclass(' ')), 'abcde')
        self.assertEqual(type(big.multistrip(StrSubclass('abcde'), StrSubclass(' '))), StrSubclass)
        self.assertEqual(big.multistrip(BytesSubclass(b'abcde'), BytesSubclass(b' ')), b'abcde')
        self.assertEqual(type(big.multistrip(BytesSubclass(b'abcde'), BytesSubclass(b' '))), BytesSubclass)

        # regression test:
        # the old approach had a bug that had to do with overlapping separators.
        # what if you strip the string ' x x ' with the separator ' x '?
        # It should eat the initial separator, which leaves behind "x ", which doesn't match
        # the separator, so it shouldn't be stripped.

        # we used to separately measure "where does the beginning run of separators end"
        # and "where does the ending run of separators start", then only keep
        # the part of the string in the middle.  but if your string was " x x "
        # and your separators were (" x ",), then they overlapped:
        #
        #    vvv   run of ending separators
        # " x x "
        #  ^^^     run of beginning separators
        #
        # and, who knows, maybe that's what you want? but that's not what you're gonna get.
        # multi-* functions prefer the leftmost instance of a separator (unless reverse
        # is true).  so this should eat the left overlapping separator and leave what
        # remains of the right one.
        self.assertEqual(big.multistrip(' x x ', (' x ',)), 'x ')

        # regression: multistrip didn't used to verify
        # that s was either str or bytes.
        with self.assertRaises(TypeError):
            big.multistrip(3.1415)
        with self.assertRaises(TypeError):
            big.multistrip(3.1415, 'abc')
        with self.assertRaises(TypeError):
            big.multistrip(['a', 'b', 'c'])
        with self.assertRaises(TypeError):
            big.multistrip([b'a', b'b', b'c'])
        with self.assertRaises(TypeError):
            big.multistrip(['a', 'b', 'c'], 'a')
        with self.assertRaises(TypeError):
            big.multistrip([b'a', b'b', b'c'], b'a')

        with self.assertRaises(TypeError):
            big.multistrip('s', ['a', b'b', 'c'])
        with self.assertRaises(TypeError):
            big.multistrip('s', ['a', 1234, 'c'])
        with self.assertRaises(TypeError):
            big.multistrip(b's', [b'a', 'b', b'c'])
        with self.assertRaises(TypeError):
            big.multistrip(b's', [b'a', 1234, b'c'])

        with self.assertRaises(TypeError):
            big.multistrip('s', b'abc')
        with self.assertRaises(TypeError):
            big.multistrip(b's', 'abc')

        with self.assertRaises(TypeError):
            big.multistrip(StrSubclass(b'  abcde  '), BytesSubclass(b' '))

        with self.assertRaises(ValueError):
            big.multistrip('s', '')
        with self.assertRaises(ValueError):
            big.multistrip('s', [])
        with self.assertRaises(ValueError):
            big.multistrip('s', [])
        with self.assertRaises(ValueError):
            big.multistrip(b's', b'')
        with self.assertRaises(ValueError):
            big.multistrip(b's', [])
        with self.assertRaises(ValueError):
            big.multistrip(b's', ())


        with self.assertRaises(ValueError):
            big.multistrip('abcde', ('c', ''))

    def test_multisplit(self):
        for c in (unchanged, to_bytes):
            not_c = to_bytes if (c == unchanged) else unchanged
            def list_multisplit(*a, **kw): return list(big.multisplit(*a, **kw))
            self.assertEqual(list_multisplit(c('aaaXaaaYaaa'), c('abc'), strip=True ), c(['X', 'Y']))
            self.assertEqual(list_multisplit(c('aaaXaaaYaaa'), c('abc'), strip=False), c(['', 'X', 'Y', '']))
            self.assertEqual(list_multisplit(c('abcXbcaYcba'), c('abc'), strip=True ), c(['X', 'Y']))
            self.assertEqual(list_multisplit(c('abcXbcaYcba'), c('abc'), strip=False), c(['', 'X', 'Y', '']))

            self.assertEqual(list_multisplit(c(''), c('abcde'), maxsplit=None), c(['']))
            self.assertEqual(list_multisplit(c('abcde'), c('fghij')), c(['abcde']))
            self.assertEqual(list_multisplit(c('abcde'), c('fghijc')), c(['ab', 'de']))
            self.assertEqual(list_multisplit(c('1a2b3c4d5e6'), c('abcde')), c(['1', '2', '3', '4', '5', '6']))

            self.assertEqual(list_multisplit(c('ab:cd,ef'),   c(':,'), strip=True ), c(["ab", "cd", "ef"]))
            self.assertEqual(list_multisplit(c('ab:cd,ef'),   c(':,'), strip=False), c(["ab", "cd", "ef"]))
            self.assertEqual(list_multisplit(c('ab:cd,ef:'),  c(':,'), strip=True ), c(["ab", "cd", "ef"]))
            self.assertEqual(list_multisplit(c('ab:cd,ef:'),  c(':,'), strip=False), c(["ab", "cd", "ef", ""]))
            self.assertEqual(list_multisplit(c(',ab:cd,ef:'), c(':,'), strip=True ), c(["ab", "cd", "ef"]))
            self.assertEqual(list_multisplit(c(',ab:cd,ef:'), c(':,'), strip=False), c(["", "ab", "cd", "ef", ""]))
            self.assertEqual(list_multisplit(c(':ab:cd,ef'),  c(':,'), strip=True ), c(["ab", "cd", "ef"]))
            self.assertEqual(list_multisplit(c(':ab:cd,ef'),  c(':,'), strip=False), c(["", "ab", "cd", "ef"]))
            self.assertEqual(list_multisplit(c('WWabXXcdYYabZZ'),   c(('ab', 'cd')), strip=True ), c(['WW', 'XX', 'YY', 'ZZ']))
            self.assertEqual(list_multisplit(c('WWabXXcdYYabZZ'),   c(('ab', 'cd')), strip=False), c(['WW', 'XX', 'YY', 'ZZ']))
            self.assertEqual(list_multisplit(c('WWabXXcdYYabZZab'), c(('ab', 'cd')), strip=True ), c(['WW', 'XX', 'YY', 'ZZ']))
            self.assertEqual(list_multisplit(c('WWabXXcdYYabZZab'), c(('ab', 'cd')), strip=False), c(['WW', 'XX', 'YY', 'ZZ', '']))
            self.assertEqual(list_multisplit(c('abWWabXXcdYYabZZ'), c(('ab', 'cd')), strip=True ), c(['WW', 'XX', 'YY', 'ZZ']))
            self.assertEqual(list_multisplit(c('abWWabXXcdYYabZZ'), c(('ab', 'cd')), strip=False), c(['','WW', 'XX', 'YY', 'ZZ']))
            self.assertEqual(list_multisplit(c('WWabXXcdYYabZZcd'), c(('ab', 'cd')), strip=True ), c(['WW', 'XX', 'YY', 'ZZ']))
            self.assertEqual(list_multisplit(c('WWabXXcdYYabZZcd'), c(('ab', 'cd')), strip=False), c(['WW', 'XX', 'YY', 'ZZ', '']))
            self.assertEqual(list_multisplit(c('XXabcdYY'), c(('a', 'abcd'))), c(['XX', 'YY']))
            self.assertEqual(list_multisplit(c('XXabcdabcdYY'), c(('ab', 'cd'))), c(['XX', 'YY']))
            self.assertEqual(list_multisplit(c('abcdXXabcdabcdYYabcd'), c(('ab', 'cd')), strip=True ), c(['XX', 'YY']))
            self.assertEqual(list_multisplit(c('abcdXXabcdabcdYYabcd'), c(('ab', 'cd')), strip=False), c(['', 'XX', 'YY', '']))
            self.assertEqual(list_multisplit(c('abcdXXabcdabcdYYabcd'), c(('ab', 'cd')), separate=True, strip=False), c(['', '', 'XX', '', '', '', 'YY', '', '']))

            self.assertEqual(list_multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=0), c(['xaxbxcxdxex']))
            self.assertEqual(list_multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=1), c(['x', 'xbxcxdxex']))
            self.assertEqual(list_multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=2), c(['x', 'x', 'xcxdxex']))
            self.assertEqual(list_multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=3), c(['x', 'x', 'x', 'xdxex']))
            self.assertEqual(list_multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=4), c(['x', 'x', 'x', 'x', 'xex']))
            self.assertEqual(list_multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=5), c(['x', 'x', 'x', 'x', 'x', 'x']))
            self.assertEqual(list_multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=6), c(['x', 'x', 'x', 'x', 'x', 'x']))

            # test: greedy separators
            self.assertEqual(list_multisplit(c('-abcde-abc-a-abc-abcde-'),
                c([
                    'a', 'ab', 'abc', 'abcd', 'abcde',
                    'b', 'bc', 'bcd', 'bcde',
                    'c', 'cd', 'cde',
                    'd', 'de',
                    'e'
                ])),
                c(['-', '-', '-', '-', '-', '-']))
            # greedy works the same when reverse=True, even if it maybe feels a little strange
            self.assertEqual(list_multisplit(c('-abcde-abc-a-abc-abcde-'),
                c([
                    'a', 'ab', 'abc', 'abcd', 'abcde',
                    'b', 'bc', 'bcd', 'bcde',
                    'c', 'cd', 'cde',
                    'd', 'de',
                    'e'
                ]), reverse=True),
                c(['-', '-', '-', '-', '-', '-']))

            # regression test: *YES*, if the string you're splitting ends with a separator,
            # and keep=big.AS_PAIRS, the result ends with a tuple containing two empty strings.
            self.assertEqual(list_multisplit(c('\na\nb\nc\n'), c(('\n',)), keep=big.AS_PAIRS, strip=False), c([ ('', '\n'), ('a', '\n'), ('b', '\n'), ('c', '\n'), ('', '') ]))

            # test: progressive strip
            self.assertEqual(list_multisplit(c('   a b c   '), c((' ',)), maxsplit=1, strip=big.PROGRESSIVE), c([ 'a', 'b c   ']))

            # regression test: when there are *overlapping* separators,
            # multisplit prefers the leftmost one(s), but passing in
            # reverse=True makes it prefer the *rightmost* ones.
            self.assertEqual(list_multisplit(c(' x x '), c((' x ',)), keep=big.ALTERNATING),
                c([ '', ' x ', 'x ']))
            self.assertEqual(list_multisplit(c(' x x '), c((' x ',)), keep=big.ALTERNATING, reverse=True),
                c([ ' x', ' x ', '']))

            # ''.split() returns an empty list.
            # multisplit intentionally does *not* reproduce this ill-concieved behavior.
            # multisplit(s, list-of-separators-that-don't-appear-in-s) always returns [s].
            # (or, rather, an iterator that yields only s).
            self.assertEqual(list_multisplit(c('')), c(['']))
            self.assertEqual(list_multisplit(c(''), reverse=True), c(['']))
            # similarly, '    '.split() also returns an empty list,
            # and multisplit does not.
            self.assertEqual(list_multisplit(c('   ')), c(['', '']))
            self.assertEqual(list_multisplit(c('   '), reverse=True), c(['', '']))
            self.assertEqual(list_multisplit(c('   '), strip=True), c(['']))
            self.assertEqual(list_multisplit(c('   '), strip=True, reverse=True), c(['']))

            with self.assertRaises(TypeError):
                list_multisplit(c('s'), 3.1415)
            with self.assertRaises(ValueError):
                list_multisplit(c('s'), [])
            with self.assertRaises(ValueError):
                list_multisplit(c('s'), ())
            with self.assertRaises(TypeError):
                list_multisplit(c('s'), not_c(''))
            with self.assertRaises(TypeError):
                list_multisplit(c('s'), [c('a'), not_c('b'), c('c')])
            with self.assertRaises(TypeError):
                list_multisplit(c('s'), [c('a'), 1234, c('c')])

        for str_type_1 in (str, StrSubclass, DifferentStrSubclass):
            for str_type_2 in (str, StrSubclass, DifferentStrSubclass):
                self.assertEqual(list_multisplit(str_type_1('abcde'), str_type_2('c')), ['ab', 'de'])

        for bytes_type_1 in (bytes, BytesSubclass, DifferentBytesSubclass):
            for bytes_type_2 in (bytes, BytesSubclass, DifferentBytesSubclass):
                self.assertEqual(list_multisplit(bytes_type_1(b'abcde'), bytes_type_2(b'c')), [b'ab', b'de'])

        for str_type in (str, StrSubclass, DifferentStrSubclass):
            for bytes_type in (bytes, BytesSubclass, DifferentBytesSubclass):
                with self.assertRaises(TypeError):
                    list_multisplit(str_type('s'), bytes_type(b'abc'))
                with self.assertRaises(TypeError):
                    list_multisplit(bytes_type(b's'), str_type('abc'))

                # just making sure!
                with self.assertRaises(TypeError):
                    list_multisplit(str_type('s'), [str_type('a'), bytes_type(b'b'), str_type('c')])
                with self.assertRaises(TypeError):
                    list_multisplit(bytes_type(b's'), [bytes_type(b'a'), str_type('b'), bytes_type(b'c')])

        # regression: multisplit didn't used to verify
        # that s was either str or bytes.
        with self.assertRaises(TypeError):
            list_multisplit(3.1415)
        with self.assertRaises(TypeError):
            list_multisplit(3.1415, 'abc')
        with self.assertRaises(TypeError):
            list_multisplit(['a', 'b', 'c'])
        with self.assertRaises(TypeError):
            list_multisplit(['a', 'b', 'c'], 'a')

        # regression: if reverse=True and separators was not hashable,
        # multisplit would crash.  fixed in 0.6.17.
        self.assertEqual(list_multisplit('axbyczd', ['x', 'y', 'z'], maxsplit=2, reverse=True), ['axb', 'c', 'd'])
        self.assertEqual(list_multisplit(b'axbyczd', [b'x', b'y', b'z'], maxsplit=2, reverse=True), [b'axb', b'c', b'd'])

    def test_advanced_multisplit(self):
        def simple_test_multisplit(s, separators, expected, **kwargs):
            for _ in range(2):
                if _ == 1:
                    # encode!
                    s = s.encode('ascii')
                    if separators == big.whitespace:
                        separators = big.ascii_whitespace
                    elif separators == big.newlines:
                        separators = big.ascii_newlines
                    else:
                        separators = to_bytes(separators)
                    expected = to_bytes(expected)
                # print()
                # print(f"s={s} expected={expected}\nseparators={separators}")
                result = list(big.multisplit(s, separators, **kwargs))
                self.assertEqual(result, expected)

        for i in range(8):
            spaces = " " * i
            simple_test_multisplit(spaces + "a  b  c" + spaces, (" ",), ['a', 'b', 'c'], strip=True)
            simple_test_multisplit(spaces + "a  b  c" + spaces, big.whitespace, ['a', 'b', 'c'], strip=True)


        simple_test_multisplit("first line!\nsecond line.\nthird line.", big.newlines,
            ["first line!", "second line.", "third line."])
        simple_test_multisplit("first line!\nsecond line.\nthird line.\n", big.newlines,
            ["first line!\n", "second line.\n", "third line."], keep=True, strip=True)
        simple_test_multisplit("first line!\nsecond line.\nthird line.\n", big.newlines,
            ["first line!\n", "second line.\n", "third line.\n", ""], keep=True, strip=False)
        simple_test_multisplit("first line!\n\nsecond line.\n\n\nthird line.", big.newlines,
            ["first line!", '', "second line.", '', '', "third line."], separate=True)
        simple_test_multisplit("first line!\n\nsecond line.\n\n\nthird line.", big.newlines,
            ["first line!\n", '\n', "second line.\n", '\n', '\n', "third line."], keep=True, separate=True)


        simple_test_multisplit("a,b,,,c", ",", ['a', 'b', '', '', 'c'], separate=True)

        simple_test_multisplit("a,b,,,c", (",",), ['a', 'b', ',,c'], separate=True, maxsplit=2)

        simple_test_multisplit("a,b,,,c", (",",), ['a,b,', '', 'c'], separate=True, maxsplit=2, reverse=True)

    def test_multisplit_exhaustively(self):
        def multisplit_tester(*segments):
            """
            segments represent split-up text segments.
            each segment is either
              a) a string appearing in separators, or
              b) contains no separators at all.
            segments *must* alternate between a) and b).
            segments doesn't need to start or end with empty strings.

            the last positional argument is actually "separators".
            as in, the separators argument for multisplit.

            tests Every. Possible. Permutation. of inputs to multisplit(),
            based on the segments you pass in.  this includes
                * as strings and encoded to bytes (ascii)
                * with and without the left separators
                * with and without the right separators
                * with every combination of every value of
                    * keep
                    * maxsplit (all values that produce different results, plus a couple extra Just In Case)
                    * reverse
                    * separate
                    * strip

            p.s it's a little slow!  but it's doing a lot.
            """

            # want_prints = True
            want_prints = False

            if want_prints: # pragma: no cover
                print("_" * 69)
                print()
                print("test exhaustively")
                print("_" * 69)

            segments = list(segments)
            separators = segments.pop()

            if separators is not None:
                separators_set = set(separators)
            else:
                separators_set = set(big.whitespace)
            assert '' not in separators_set

            # strip off the leading and trailing separators.

            # leading looks like this:
            #   [ '', separator, separator, separator, ... ]
            # yes, that is always an empty string, you'll see why
            # in a moment.

            leading = ['']
            while True:
                if segments[0] not in separators_set:
                    break
                leading.append(segments.pop(0))

            # trailing contains just the trailing (right)
            # separators, as individual strings.
            # trailing just looks like this:
            #   [ separator, separator, ... ]

            trailing = []
            while True:
                if want_prints: # pragma: no cover
                    print(f"splitting segments: segments[-1]={segments[-1]} separators_set={separators_set} not in? {segments[-1] not in separators_set}")
                if segments[-1] not in separators_set:
                    break
                trailing.append(segments.pop())
            trailing.reverse()

            # splits is a list of lists.  each sublist, or "split",
            # inside splits, looks like this:
            #   [ non-separator-string, separator, separator, ... ]
            # (yes, leading and an individual split list look identical, that's why.)
            # every split in splits is has at least one separator
            # EXCEPT the last one which only has the non-sep string.
            #
            # this is only an intermediate form, we'll massage this
            # into a more useful form in a minute.
            splits = []
            split = []
            def flush():
                nonlocal split
                if split:
                    splits.append(split)
                    split = []

            for segment in segments:
                if segment in separators_set:
                    assert split
                    split.append(segment)
                    continue
                assert (not split) or (split[-1] in separators_set), f"split={split} split[-1]={split[-1]} separators_set={separators_set}"
                flush()
                split.append(segment)
            flush()

            if want_prints: # pragma: no cover
                print(f"leading={leading}")
                print(f"splits={splits}")
                print(f"trailing={trailing}")
            assert splits[-1][-1] not in separators_set, f"splits[-1][-1]={splits[-1][-1]} is in separators_set={separators_set}!"

            # leading and trailing must both have at least
            # one sep string.
            assert (len(leading) >= 2) and trailing

            # note one invariant: if you join leading, splits, and trailing
            # together into one big string, it is our original input string.
            # that will never change.

            originals = leading, splits, trailing

            for as_bytes in (False, True):
                if want_prints: # pragma: no cover
                    print(f"[loop 0] as_bytes={as_bytes}")
                if as_bytes:
                    leading, splits, trailing = copy.deepcopy(originals)
                    leading = big.text._cheap_encode_iterable_of_strings(leading)
                    splits = [big.text._cheap_encode_iterable_of_strings(split) for split in splits]
                    trailing = big.text._cheap_encode_iterable_of_strings(trailing)
                    originals = [leading, splits, trailing]
                    empty = b''
                    if separators is None:
                        separators_set = set(big.ascii_whitespace)
                    else:
                        separators = big.text._cheap_encode_iterable_of_strings(separators)
                        separators_set = set(separators)
                    non_sep_marker = b"&NONSEP&"
                else:
                    empty = ''
                    non_sep_marker = "&NONSEP&"

                for use_leading in (False, True):
                    for use_trailing in (False, True):
                        # we're going to hack up these lists,
                        # so start with copies.
                        leading, splits, trailing = copy.deepcopy(originals)

                        if want_prints: # pragma: no cover
                            print(f"[loop 1,2] use_leading={use_leading} use_trailing={use_trailing}")
                            print(f"         leading={leading} split={split} trailing={trailing}")

                        input_strings = []
                        if use_leading:
                            input_strings.extend(leading)
                        for split in splits:
                            input_strings.extend(split)
                        if use_trailing:
                            input_strings.extend(trailing)

                        input_string = empty.join(input_strings)

                        for separate in (False, True):
                            leading, splits, trailing = copy.deepcopy(originals)
                            # now we're going to change leading / splits / trailing
                            # so that they collectively alternate
                            #    nonsep, sep

                            if want_prints: # pragma: no cover
                                print(f"[loop 3] separate={separate}")
                                print(f"    leading={leading} splits={splits} trailing={trailing}")

                            if not separate:
                                # blob the separators together
                                l2 = [empty]
                                if want_prints: # pragma: no cover
                                    print(f"    blob together empty={empty} leading={leading}")
                                l2.append(empty.join(leading))
                                leading = l2
                                if want_prints: # pragma: no cover
                                    print(f"    blobbed leading={leading}")

                                for split in splits:
                                    if len(split) > 1:
                                        joined = empty.join(split[1:])
                                        del split[1:]
                                        split.append(joined)

                                trailing = [empty.join(trailing), empty]
                            else:
                                # turn leading, splits, and trailing
                                # into suitable form for testing with "separate".
                                #   * every list is a list of alternating sep and nonsep.
                                #   * splits now has empty strings between sep and nonsep.
                                assert len(leading) >= 2
                                separate_leading = list(leading[:2])
                                for s in leading[2:]:
                                    separate_leading.append(empty)
                                    separate_leading.append(s)
                                leading = separate_leading
                                if want_prints: # pragma: no cover
                                    print(f"    leading={leading}")

                                separate_splits = []
                                for split in splits:
                                    if len(split) == 1:
                                        assert split == splits[-1]
                                        separate_splits.append(split)
                                        break
                                    assert len(split) >= 2
                                    separate_splits.append(list(split[:2]))
                                    for s in split[2:]:
                                        separate_splits.append([empty, s])
                                splits = separate_splits
                                if want_prints: # pragma: no cover
                                    print(f"    splits={splits}")

                                separate_trailing = []
                                for s in trailing:
                                    if s: # skip the trailing empty
                                        separate_trailing.append(s)
                                        separate_trailing.append(empty)
                                trailing = separate_trailing
                                if want_prints: # pragma: no cover
                                    print(f"    trailing={trailing}")

                            # time to check!  every list or sublist
                            # should now have an even length,
                            # EXCEPT splits[-1] which is length 1.
                            assert len(leading) % 2 == 0
                            for split in splits[:-1]:
                                assert len(split) % 2 == 0
                            assert len(splits[-1]) == 1
                            assert len(trailing) % 2 == 0

                            for strip in (False, big.LEFT, big.RIGHT, True):
                                expected = []
                                if want_prints: # pragma: no cover
                                    print(f"[loop 4] strip={strip}")
                                    print(f"         leading={leading} splits={splits} trailing={trailing}")

                                if use_leading and (strip in (False, big.RIGHT)):
                                    expected.extend(leading)
                                if want_prints: # pragma: no cover
                                    print(f"     leading: expected={expected}")

                                for split in splits:
                                    expected.extend(split)
                                if want_prints: # pragma: no cover
                                    print(f"      splits: expected={expected}")

                                if use_trailing and (strip in (False, big.LEFT)):
                                    expected.extend(trailing)
                                if want_prints: # pragma: no cover
                                    print(f"    trailing: expected={expected}")

                                # expected now looks like this:
                                #   * it has an odd number of items
                                #   * even numbered items are nonsep
                                #   * odd numbered items are sep
                                assert len(expected) % 2 == 1, f"expected={expected} doesn't have an odd # of elements!"
                                for i in range(0, len(expected), 2):
                                    assert expected[i] not in separators_set
                                for i in range(1, len(expected), 2):
                                    assert not big.multistrip(expected[i], separators_set), f"expected[{i}]={expected[i]!r} not in separators_set={separators_set} !"

                                # how many splits can we have?
                                # Technically the maximum number of splits possible
                                # is
                                #    (len(expected) // 2) - 1
                                # 'a b c d e' would split by whitespace into 9 elements,
                                # only using four splits.
                                # Anyway we test a couple supernumerary maxsplit values.
                                max_maxsplit = (len(expected) // 2) + 1

                                expected_original = expected

                                if want_prints: # pragma: no cover
                                    print(f"    expected_original={expected_original}")

                                for reverse in (False, True):
                                    for maxsplit in range(-1, max_maxsplit):
                                        expected = list(expected_original)
                                        if want_prints: # pragma: no cover
                                            print(f"[loop 5,6] reverse={reverse} maxsplit={maxsplit} // expected={expected}")
                                        if maxsplit == 0:
                                            joined = empty.join(expected)
                                            expected = [joined]
                                        elif maxsplit > 0:
                                            if not reverse:
                                                # we're in "alternating" mode,
                                                # so odd-numbered indexes are
                                                # splits
                                                #
                                                # length 7
                                                #  0    1    2    3    4    5    6   index
                                                # ['a', ' ', 'b', ' ', 'c', ' ', 'd']
                                                #  0         1          2        3   maxsplit
                                                start = maxsplit * 2
                                                end = len(expected)
                                                if start < end:
                                                    if want_prints: # pragma: no cover
                                                        print(f"    not reverse: expected[{start}:{end}] = {expected[start:end]}")
                                                    joined = non_sep_marker + empty.join(expected[start:end])
                                                    del expected[start:end]
                                                    if want_prints: # pragma: no cover
                                                        print(f"    expected={expected} joined={joined} empty={empty}")
                                                    expected.append(joined)
                                            else:
                                                # reverse and maxsplit
                                                #
                                                # length 7
                                                #  0    1    2    3    4    5    6   index
                                                # ['a', ' ', 'b', ' ', 'c', ' ', 'd',  ]
                                                #       3         2         1         0   maxsplit
                                                start = 0
                                                end = len(expected) - (maxsplit * 2)
                                                joined = non_sep_marker + empty.join(expected[start:end])
                                                if want_prints: # pragma: no cover
                                                    print(f"    reverse: expected[{start}:{end}] = {expected[start:end]}  /// joined={joined}")
                                                del expected[start:end]
                                                if want_prints: # pragma: no cover
                                                    print(f"    expected={expected} joined={joined}")
                                                expected.insert(0, joined)
                                        expected_original2 = expected
                                        for keep in (False, True, big.ALTERNATING, big.AS_PAIRS):
                                            expected = list(expected_original2)
                                            if want_prints: # pragma: no cover
                                                print(f"[loop 7] keep={keep} // expected={expected}")
                                            if not keep:
                                                expected = [s.replace(non_sep_marker, empty) for i, s in enumerate(expected) if i % 2 == 0]
                                            elif keep == big.AS_PAIRS:
                                                new_expected = []
                                                waiting = None
                                                def append(s):
                                                    nonlocal waiting
                                                    s = s.replace(non_sep_marker, empty)
                                                    if waiting is None:
                                                        waiting = s
                                                        return
                                                    new_expected.append((waiting, s))
                                                    waiting = None
                                                for s in expected:
                                                    append(s)
                                                # manual flush
                                                if waiting is not None:
                                                    append(empty)
                                                expected = new_expected
                                            elif keep == big.ALTERNATING:
                                                # strip non_sep_marker hack
                                                expected = [s.replace(non_sep_marker, empty) for s in expected]
                                            elif keep:
                                                new_expected = []
                                                waiting = None
                                                def append(s):
                                                    nonlocal waiting
                                                    is_sep = s in separators_set
                                                    s = s.replace(non_sep_marker, empty)
                                                    if (waiting is None) and (not is_sep):
                                                        waiting = s
                                                        return
                                                    if waiting is not None:
                                                        s = waiting + s
                                                    new_expected.append(s)
                                                    waiting = None
                                                for s in expected:
                                                    append(s)
                                                # manual flush
                                                if waiting is not None:
                                                    new_expected.append(waiting)
                                                expected = new_expected
                                                if want_prints: # pragma: no cover
                                                    print(f"    now expected={expected}")

                                            result = list(big.multisplit(input_string, separators,
                                                keep=keep,
                                                maxsplit=maxsplit,
                                                reverse=reverse,
                                                separate=separate,
                                                strip=strip,
                                                ))
                                            if want_prints: # pragma: no cover
                                                print(f"as_bytes={as_bytes} use_leading={use_leading} use_trailing={use_trailing}")
                                                print(f"multisplit({input_string!r}, separators={printable_separators(separators)}, keep={keep}, separate={separate}, strip={strip}, reverse={reverse}, maxsplit={maxsplit})")
                                                print(f"  result={result}")
                                                print(f"expected={expected}")
                                                print("________")
                                                print()
                                            self.assertEqual(result, expected, f"as_bytes={as_bytes} use_leading={use_leading} use_trailing={use_trailing} multisplit(input_string={input_string}, separators={printable_separators(separators)}, keep={keep}, separate={separate}, strip={strip}, reverse={reverse}, maxsplit={maxsplit})")


        test_string = [
            ' ',
            'a',
            ' ',
            'b',
            ' ',
            'c',
            ' ',
            ]

        multisplit_tester(
            *test_string,
            (' ',),
            )

        multisplit_tester(
            *test_string,
            None,
            )


        multisplit_tester(
            ' ',
            '\t',
            ' ',
            '\n',
            ' ',

            'a',

            ' ',
            '\t',
            ' ',
            '\n',

            'b',

            '\t',
            ' ',
            '\n',

            'c',

            ' ',
            ' ',
            '\n',

            big.whitespace,
            )


        multisplit_tester(
            'x',
            'y',
            'x',
            'y',

            'a',

            'x',
            'y',
            'x',
            'y',
            'x',

            'b',

            'y',

            'c',

            'x',
            'y',
            'x',
            'y',
            'x',
            'y',

            'd',

            'y',
            'x',

            'e',

            'y',
            'y',
            'y',
            'y',

            'f',

            'x',
            'x',
            'x',
            'x',
            'x',
            'x',

            ('x', 'y'),
            )

    def test_multipartition(self):
        def test_multipartition(s, separator, count, expected, *, reverse=False):
            for _ in range(2):
                if _ == 1:
                    # encode!
                    s = s.encode('ascii')
                    # if separator == big.whitespace:
                    #     separator = big.ascii_whitespace
                    if isinstance(separator, str):
                        separator = separator.encode('ascii')
                    else:
                        separator = big.text._cheap_encode_iterable_of_strings(separator)
                    expected = big.text._cheap_encode_iterable_of_strings(expected)

                # print()
                if isinstance(separator, (str, bytes)):
                    separators = (separator,)
                else:
                    separators = separator

                got = big.multipartition(s, separators, count, reverse=reverse)
                # print(f"    {got!r}")
                self.assertEqual(expected, got)

                got2 = big.multirpartition(s, separators, count, reverse=not reverse)
                # print(f"    {got2!r}")
                self.assertEqual(expected, got2)

        test_multipartition("a:b:c:d", ":", 0, ("a:b:c:d",))
        test_multipartition("a:b:c:d", ":", 1, ("a", ":", "b:c:d"))
        test_multipartition("a:b:c:d", ":", 2, ("a", ":", "b", ":", "c:d"))
        test_multipartition("a:b:c:d", ":", 3, ("a", ":", "b", ":", "c", ":", "d"))
        test_multipartition("a:b:c:d", ":", 4, ("a", ":", "b", ":", "c", ":", "d", '', ''))
        test_multipartition("a:b:c:d", ":", 5, ("a", ":", "b", ":", "c", ":", "d", '', '', '', ''))

        test_multipartition("a:b:c:d", ":", 0, ("a:b:c:d",), reverse=True)
        test_multipartition("a:b:c:d", ":", 1, ("a:b:c", ':' ,"d"), reverse=True)
        test_multipartition("a:b:c:d", ":", 2, ("a:b", ":", "c", ':' ,"d"), reverse=True)
        test_multipartition("a:b:c:d", ":", 3, ("a", ":", "b", ":", "c", ':' ,"d"), reverse=True)
        test_multipartition("a:b:c:d", ":", 4, ("", "", "a", ":", "b", ":", "c", ':' ,"d"), reverse=True)
        test_multipartition("a:b:c:d", ":", 5, ("", "", "", "", "a", ":", "b", ":", "c", ':' ,"d"), reverse=True)

        test_multipartition("a:b:c:d", "x", 1, ("a:b:c:d", "", ""))
        test_multipartition("a:b:c:d", "x", 0, ("a:b:c:d",))
        test_multipartition("a:b:c:d", "x", 2, ("a:b:c:d", "", "", "", ""))
        test_multipartition("a:b:c:d", "x", 3, ("a:b:c:d", "", "", "", "", "", ""))

        test_multipartition("a:b:c:d", "x", 0, ("a:b:c:d",), reverse=True)
        test_multipartition("a:b:c:d", "x", 1, ("", "", "a:b:c:d"), reverse=True)
        test_multipartition("a:b:c:d", "x", 2, ("", "", "", "", "a:b:c:d"), reverse=True)
        test_multipartition("a:b:c:d", "x", 3, ("", "", "", "", "", "", "a:b:c:d"), reverse=True)

        # test overlapping separator behavior
        test_multipartition("a x x b", " x ", 1, ("a", " x ", "x b"))
        test_multipartition("a x x b", " x ", 1, ("a x", " x ", "b"), reverse=True)

        # test actually using multiple separators, and just for fun--overlapping!
        test_multipartition("a x x b y y c", (" x ", " y "), 2, ("a", " x ", "x b", " y ", "y c"))
        test_multipartition("a x x b y y c", (" x ", " y "), 2, ("a x", " x ", "b y", " y ", "c"), reverse=True)

        # test greedy
        test_multipartition("VWabcWXabXYbcYZ", ('a', 'ab', 'abc', 'b', 'bc', 'c'), 3, ('VW', 'abc', 'WX', 'ab', 'XY', 'bc', 'YZ'))
        test_multipartition("VWabcWXabXYbcYZ", ('a', 'ab', 'abc', 'b', 'bc', 'c'), 3, ('VW', 'abc', 'WX', 'ab', 'XY', 'bc', 'YZ'), reverse=True)

        # I don't bother to test the str / subclass of str / etc stuff
        # with multipartition, because it literally uses multisplit
        # to do the splitting.  so multisplit handles it.

        with self.assertRaises(ValueError):
            big.multipartition("a x x b y y c", (" x ", " y "), -1)

    def test_reimplemented_str_split(self):
        def _multisplit_to_split(s, sep, maxsplit, reverse):
            separate = sep != None
            if separate:
                strip = False
            else:
                sep = big.ascii_whitespace if isinstance(s, bytes) else big.whitespace
                strip = big.PROGRESSIVE
            result = list(big.multisplit(s, sep,
                maxsplit=maxsplit, reverse=reverse,
                separate=separate, strip=strip))
            if not separate:
                # ''.split() == '   '.split() == []
                if result and (not result[-1]):
                    result.pop()
            return result

        def str_split(s, sep=None, maxsplit=-1):
            return _multisplit_to_split(s, sep, maxsplit, False)

        def str_rsplit(s, sep=None, maxsplit=-1):
            return _multisplit_to_split(s, sep, maxsplit, True)

        def test(s, sep=None, maxsplit=-1):
            # automatically test with (str, bytes) x (sep=sep, sep=None)
            for as_bytes in (False, True):
                if as_bytes:
                    s = s.encode('ascii')
                    if sep is not None:
                        sep = sep.encode('ascii')
                for sep_none in (False, True):
                    sep2 = None if sep_none else sep
                    a = s.split(sep2, maxsplit)
                    b = str_split(s, sep2, maxsplit)
                    self.assertEqual(a, b, f"reimplemented str_split fails: {s!r}.split({sep2!r}, {maxsplit}) == {a}, str_split version gave us {b}")

                    a = s.rsplit(sep2, maxsplit)
                    b = str_rsplit(s, sep2, maxsplit)
                    self.assertEqual(a, b, f"reimplemented str_rsplit fails: {s!r}.rsplit({sep2!r}, {maxsplit}) == {a}, str_split version gave us {b}")


        for maxsplit in range(-1, 10):
            test('a b   c       d \t\t\n e', None, maxsplit)
            test('   a b c   ', ' ', maxsplit)

        for base_s in (
            "",
            "a",
            "a b c",
            "a b  c d   e",
            ):
            for leading in range(10):
                for trailing in range(10):
                    s = (" " * leading) + base_s + (" " * trailing)
                    s_with_commas = s.replace(' ', ',')
                    for maxsplit in range(-1, 8):
                        test(s, None, maxsplit)
                        test(s, " ", maxsplit)
                        test(s_with_commas, ',', maxsplit)

        self.assertEqual(str_split(''), [])
        test('')

        # test greedy behavior.
        # str.split isn't greedy, but multisplit is.
        # (well, str.split *might* be? there's no way to call it
        # that demonstrates whether or not it's greedy.)
        # anyway, ensure multisplit's greedy behavior doesn't
        # mess up our emulation of str.split.
        test('a\rb\nc\r\nd')

        test('a b c ', ' ')

    def test_reimplemented_str_splitlines(self):
        def str_splitlines(s, keepends=False):
            newlines = big.ascii_newlines if isinstance(s, bytes) else big.newlines
            l = list(big.multisplit(s, newlines,
                keep=keepends, separate=True, strip=False))
            if l and not l[-1]:
                # yes, "".splitlines() returns an empty list
                l.pop()
            return l

        def test(s):
            # automatically test with (str, bytes) x (keepends=False,keepends=True,)
            for as_bytes in (False, True):
                if as_bytes:
                    s = s.encode('ascii')
                for keepends in (False, True):
                    a = s.splitlines(keepends)
                    b = str_splitlines(s, keepends)
                    self.assertEqual(a, b, f"reimplemented str_splitlines fails: {s!r}.splitlines({keepends}) == {a}, multisplit gave us {b}")

        test('')
        test('One line')
        test('One line\n')
        test('Two lines\nTwo lines')
        test('Two lines\nTwo lines\n')
        test('Two lines\nTwo lines\n\n\n')

    def test_reimplemented_str_partition(self):
        def _partition_to_multisplit(s, sep, reverse):
            if not sep:
                raise ValueError("empty separator")
            l = tuple(big.multisplit(s, (sep,),
                keep=big.ALTERNATING, maxsplit=1, reverse=reverse, separate=True))
            if len(l) == 1:
                empty = b'' if isinstance(s, bytes) else ''
                if reverse:
                    l = (empty, empty) + l
                else:
                    l = l + (empty, empty)
            return l

        def str_partition(s, sep):
            return _partition_to_multisplit(s, sep, False)

        def str_rpartition(s, sep):
            return _partition_to_multisplit(s, sep, True)

        def test(s, sep):
            # automatically test with (str, bytes)
            for as_bytes in (False, True):
                if as_bytes:
                    s = s.encode('ascii')
                    if sep is not None:
                        sep = sep.encode('ascii')

                a = s.partition(sep)
                b = str_partition(s, sep)
                self.assertEqual(a, b, f"reimplemented str_partition fails: {s!r}.partition({sep!r}) == {a}, multisplit gave us {b}")

                a = s.rpartition(sep)
                b = str_rpartition(s, sep)
                self.assertEqual(a, b, f"reimplemented str_rpartition fails: {s!r}.rpartition({sep!r}) == {a}, multisplit gave us {b}")

        test('', ' ')
        test(' ', ' ')

        s = "  a b b c d d e  "
        test(s, " ")
        test(s, "b ")
        test(s, " b ")
        test(s, " b")
        test(s, " c ")
        test(s, " d")
        test(s, " d ")
        test(s, "d ")
        test(s, "e")
        test(s, "honk")
        test(s, "squonk")

        with self.assertRaises(ValueError):
            " a b c ".partition('')
        with self.assertRaises(ValueError):
            str_partition(" a b c ", '')

        with self.assertRaises(ValueError):
            " a b c ".rpartition('')
        with self.assertRaises(ValueError):
            str_rpartition(" a b c ", '')


    def test_wrap_words(self):
        def test(words, expected, margin=79):
            got = big.wrap_words(words, margin)
            self.assertEqual(got, expected)
            got = big.wrap_words(to_bytes(words), margin)
            self.assertEqual(got, to_bytes(expected))

        test(
            "hello there. how are you? i am fine! so there's that.".split(),
            "hello there.  how are you?  i am fine!  so there's that.")
        test(
            "hello there. how are you? i am fine! so there's that.".split(),
            "hello there.  how\nare you?  i am fine!\nso there's that.",
            20)
        test(
            ["these are all long lines that must be by themselves.",
            "   more stuff goes here and stuff.",
            " know what i'm talkin' about?  yeah, that's what i'm talking about."],
            "these are all long lines that must be by themselves.\n   more stuff goes here and stuff.\n know what i'm talkin' about?  yeah, that's what i'm talking about.",
            20)
        test(
            ["a", 'b', '\n\n', 'c', 'd', 'e.'],
            "a b\n\nc d\ne.",
            4)

        with self.assertRaises(ValueError):
            big.wrap_words([])

    def test_split_text_with_code(self):
        def test(s, expected, **kwargs):
            got = big.split_text_with_code(s, **kwargs)
            if 0:
                print()
                print("s:")
                print("   ", repr(s))
                print("got:")
                print("   ", repr(got))
                print("expected:")
                print("   ", repr(expected))
                print()
            self.assertEqual(expected, got)
            got = big.split_text_with_code(to_bytes(s), **kwargs)
            self.assertEqual(to_bytes(expected), got)

        def xtest(*a, **kw): pass

        test(
            "hey there party people",
            ['hey', 'there', 'party', 'people'],
            )
        test(
            "hey there party people\n\na second paragraph!\n\nand a third.",
            ['hey', 'there', 'party', 'people', '\n\n', 'a', 'second', 'paragraph!', '\n\n', 'and', 'a', 'third.'],
            )
        test(
            "hey there party people\n\nhere, we have a second paragraph.\nwith an internal newline.\n\n    for i in code:\n        print(i)\n\nmore text here? sure seems like it.",
            ['hey', 'there', 'party', 'people', '\n\n', 'here,', 'we', 'have', 'a', 'second', 'paragraph.', 'with', 'an', 'internal', 'newline.', '\n\n', '    for i in code:', '\n', '        print(i)', '\n\n', 'more', 'text', 'here?', 'sure', 'seems', 'like', 'it.']
            )
        test(
            "text paragraphs separated by infinite newlines get collapsed to just two newlines.\n\n\n\n\nsee? just two.\n\n\n\n\n\n\n\n\nqed!",
            ['text', 'paragraphs', 'separated', 'by', 'infinite', 'newlines', 'get', 'collapsed', 'to', 'just', 'two', 'newlines.', '\n\n', 'see?', 'just', 'two.', '\n\n', 'qed!']
            )
        test(
            "here's some code with a tab.\n\tfor x in range(3):\n\t\tprint(x)\nwelp! that's it for the code.",
            ["here's", 'some', 'code', 'with', 'a', 'tab.', '\n\n', '        for x in range(3):', '\n', '                print(x)', '\n\n', 'welp!', "that's", 'it', 'for', 'the', 'code.']
            )
        test(
            "here's some code with a tab.\n\tfor x in range(3):\n\t\tprint(x)\nwelp! that's it for the code.",
            ["here's", 'some', 'code', 'with', 'a', 'tab.', '\n\n', '\tfor x in range(3):', '\n', '\t\tprint(x)', '\n\n', 'welp!', "that's", 'it', 'for', 'the', 'code.'],
            convert_tabs_to_spaces=False)
        test(
            "this is text, but next is a code paragraph with a lot of internal newlines and stuff.\n\tfor x in range(3):\n\n   \n\n    \t\n\t\tprint(x)\n\t\t\n\n\t\tprint(x*x)\nwelp! that's it for the code.",
            ['this', 'is', 'text,', 'but', 'next', 'is', 'a', 'code', 'paragraph', 'with', 'a', 'lot', 'of', 'internal', 'newlines', 'and', 'stuff.', '\n\n',
            '        for x in range(3):', '\n', '\n', '\n', '\n', '\n', '                print(x)', '\n', '\n', '\n', '                print(x*x)', '\n\n', 'welp!', "that's", 'it', 'for', 'the', 'code.']
            )
        with self.assertRaises(RuntimeError):
            big.split_text_with_code("howdy.\n\vwhat's this?")
        with self.assertRaises(RuntimeError):
            big.split_text_with_code("howdy.\n    for a in \v range(30):\n        print(a)")

    def test_merge_columns(self):
        def test(columns, expected, **kwargs):
            got = big.merge_columns(*columns, **kwargs)
            if 0:
                print("_"*70)
                print("columns")
                print(repr(columns))
                print("expected:")
                print()
                print(repr(expected))
                print(expected)
                print()
                print("got:")
                print()
                print(repr(got))
                print(got)
                print()
                print()
            self.assertEqual(got, expected)
            bytes_columns = [(to_bytes(c[0]), c[1], c[2]) for c in columns]
            if 'column_separator' in kwargs:
                kwargs['column_separator'] = to_bytes(kwargs['column_separator'])
            got = big.merge_columns(*bytes_columns, **kwargs)
            self.assertEqual(got, to_bytes(expected))

        with self.assertRaises(OverflowError):
            test([("1\n2\n3 4 5 6 7 8", 4, 4), ("howdy\nhello\nhi, how are you?\ni'm fine.", 5, 16), ("ending\ntext!".split("\n"), 79, 79)],
                "1    howdy            ending\n2    hello            text!\n3    hi, how are you?\n     i'm fine.",
                overflow_strategy=big.OverflowStrategy.RAISE)

        test([("1\n2\n3", 4, 4), ("howdy\nhello\nhi, how are you?\ni'm fine.", 5, 16), ("ending\ntext!".split("\n"), 79, 79)],
            "1    howdy            ending\n2    hello            text!\n3    hi, how are you?\n     i'm fine.",
            overflow_strategy=big.OverflowStrategy.INTRUDE_ALL)

        test([("super long lines here\nI mean, they just go on and on.\n(text)\nshort now\nhowever.\nthank\nthe maker!", 5, 15), ("this is the second column.\ndoes it have to wait?  it should.", 20, 60)],
            'super long lines here\nI mean, they just go on and on.\n(text)\nshort now\nhowever.        this is the second column.\nthank           does it have to wait?  it should.\nthe maker!',
            overflow_after=2,
            overflow_strategy=big.OverflowStrategy.INTRUDE_ALL)

        # merge overflows due to overflow_before and overflow_after being large
        test([
            ("overflow line 1\na\nb\nc\nd\noverflow line 2\n", 4, 8),
            ("this is the second column.\ndoes it have to wait?  it should.", 20, 60),
            ],
            'overflow line 1\na\nb\nc\nd\noverflow line 2\n         this is the second column.\n         does it have to wait?  it should.',
            overflow_before=2,
            overflow_after=3,
            overflow_strategy=big.OverflowStrategy.INTRUDE_ALL)

        test([
            ("overflow line 1\na\nb\nc\nd\ne\nf\noverflow line 2\n", 4, 8),
            ("this is the second column.\ndoes it have to wait?  not this time.", 20, 60),
            ],
            'overflow line 1\na        this is the second column.\nb        does it have to wait?  not this time.\nc\nd\ne\nf\noverflow line 2',
            overflow_strategy=big.OverflowStrategy.INTRUDE_ALL)
        # test pause until final
        test([
            ("overflow line 1\na\nb\nc\nd\ne\nf\noverflow line 2\n", 4, 8),
            ("this is the second column.\ndoes it have to wait?  it should.", 20, 60),
            ],
            'overflow line 1\na\nb\nc\nd\ne\nf\noverflow line 2\n         this is the second column.\n         does it have to wait?  it should.',
            overflow_strategy = big.OverflowStrategy.DELAY_ALL,
            )

        results = [
            '1 | aaa | what | aaa\n2 | bbb | ho   | bbb\n3 | ccc | too-long\n4 | ddd | column\n5 | eee | here | ccc\n6 | fff | my   | ddd\n7 | ggg | oh   | eee\n8 | hhh | my   | fff\n  |     | what | ggg\n  |     | tweedy\n  |     | fun  | hhh',
            '1 | aaa | what | aaa\n2 | bbb | ho   | bbb\n3 | ccc | too-long\n4 | ddd | column\n5 | eee | here\n6 | fff | my   | ccc\n7 | ggg | oh   | ddd\n8 | hhh | my   | eee\n  |     | what | fff\n  |     | tweedy\n  |     | fun\n  |     |      | ggg\n  |     |      | hhh',
            '1 | aaa | what | aaa\n2 | bbb | ho\n3 | ccc | too-long\n4 | ddd | column\n5 | eee | here | bbb\n6 | fff | my   | ccc\n7 | ggg | oh   | ddd\n8 | hhh | my   | eee\n  |     | what\n  |     | tweedy\n  |     | fun  | fff\n  |     |      | ggg\n  |     |      | hhh',
            '1 | aaa | what | aaa\n2 | bbb | ho\n3 | ccc | too-long\n4 | ddd | column\n5 | eee | here\n6 | fff | my   | bbb\n7 | ggg | oh   | ccc\n8 | hhh | my   | ddd\n  |     | what\n  |     | tweedy\n  |     | fun\n  |     |      | eee\n  |     |      | fff\n  |     |      | ggg\n  |     |      | hhh',
            ]

        results_iterator = iter(results)
        for overflow_before in range(2):
            for overflow_after in range(2):
                test((
                    ("1\n2\n3\n4\n5\n6\n7\n8", 1, 1),
                    ("aaa\nbbb\nccc\nddd\neee\nfff\nggg\nhhh", 3, 3),
                    ("what\nho\ntoo-long\ncolumn\nhere\nmy\noh\nmy\nwhat\ntweedy\nfun\n", 2, 4),
                    ("aaa\nbbb\nccc\nddd\neee\nfff\nggg\nhhh", 3, 3),
                    ),
                    next(results_iterator),
                    column_separator=" | ",
                    overflow_before=overflow_before,
                    overflow_after=overflow_after,
                    overflow_strategy=big.OverflowStrategy.INTRUDE_ALL)

        test((
            ("1\n2\n3\n4\n5\n6\n7\n8", 1, 1),
            ("aaa\nbbb\nccc\nddd\neee\nfff\nggg\nhhh", 3, 3),
            ("what\nho\ntoo-long\ncolumn\nhere\nmy\noh\nmy\nwhat\ntweedy\nfun\n", 2, 4),
            ("aaa\nbbb\nccc\nddd\neee\nfff\nggg\nhhh", 3, 3),
            ),
            '1 | aaa | what\n2 | bbb | ho\n3 | ccc | too-long\n4 | ddd | column\n5 | eee | here\n6 | fff | my\n7 | ggg | oh\n8 | hhh | my\n  |     | what\n  |     | tweedy\n  |     | fun\n  |     |      | aaa\n  |     |      | bbb\n  |     |      | ccc\n  |     |      | ddd\n  |     |      | eee\n  |     |      | fff\n  |     |      | ggg\n  |     |      | hhh',
            column_separator=" | ",
            overflow_strategy=big.OverflowStrategy.DELAY_ALL,
            overflow_before=0,
            overflow_after=1,
            )



    def test_text_pipeline(self):
        def test(columns, expected):
            for i in range(2):
                splits = [(big.split_text_with_code(column), min, max) for column, min, max in columns]
                wrapped = [(big.wrap_words(split, margin=max), min, max) for split, min, max in splits]
                got = big.merge_columns(*wrapped, overflow_strategy=big.OverflowStrategy.INTRUDE_ALL)
                if 0:
                    print("_"*70)
                    print("columns")
                    print(repr(columns))
                    print("expected:")
                    print()
                    print(expected)
                    print()
                    print("got:")
                    print()
                    print(got)
                    print()
                    print()
                self.assertEqual(got, expected)
                if i:
                    break
                columns = [(to_bytes(t[0]), t[1], t[2]) for t in columns]
                expected = to_bytes(expected)


        test(
            (
                (
                "-v|--verbose",
                19,
                19,
                ),
                (
                "Causes the program to produce more output.  Specifying it multiple times raises the volume of output.",
                0,
                60,
                ),
            ),
            '-v|--verbose        Causes the program to produce more output.  Specifying it\n                    multiple times raises the volume of output.'
        )

        test(
            (
                (
                "-v|--verbose",
                9,
                9,
                ),
                (
                "Causes the program to produce more output.  Specifying it multiple times raises the volume of output.",
                0,
                60,
                ),
            ),
            '-v|--verbose\n          Causes the program to produce more output.  Specifying it\n          multiple times raises the volume of output.'
        )

        # an empty column just adds space.  so, to indent everything, add an empty initial column.
        # note that it'll be min_width wide and *then* you'll get the column_separator.
        test(
            (
                (
                "",
                3,
                3,
                ),
                (
                "-v|--verbose",
                19,
                19,
                ),
                (
                "Causes the program to produce more output.  Specifying it multiple times raises the volume of output.",
                0,
                60,
                ),
            ),
            '    -v|--verbose        Causes the program to produce more output.  Specifying it\n                        multiple times raises the volume of output.'
        )

    def test_gently_title(self):
        def test(s, expected, test_ascii=True, apostrophes=None, double_quotes=None):
            result = big.gently_title(s, apostrophes=apostrophes, double_quotes=double_quotes)
            self.assertEqual(result, expected)
            result = big.gently_title(StrSubclass(s), apostrophes=apostrophes, double_quotes=double_quotes)
            self.assertEqual(result, expected)
            if test_ascii:
                if apostrophes:
                    apostrophes = apostrophes.encode('ascii')
                if double_quotes:
                    double_quotes = double_quotes.encode('ascii')
                result = big.gently_title(s.encode('ascii'), apostrophes=apostrophes, double_quotes=double_quotes)
                self.assertEqual(result, expected.encode('ascii'))
                result = big.gently_title(BytesSubclass(s.encode('ascii')), apostrophes=apostrophes, double_quotes=double_quotes)
                self.assertEqual(result, expected.encode('ascii'))

        test("", "")
        test("abcde fgh", "Abcde Fgh")
        test("peter o'toole", "Peter O'Toole")
        test("lord d'arcy", "Lord D'Arcy")
        test("multiple   spaces", "Multiple   Spaces")
        test("'twas the night before christmas", "'Twas The Night Before Christmas")
        test("don't sleep on the subway", "Don't Sleep On The Subway")
        test("everybody's thinking they couldn't've had a v-8", "Everybody's Thinking They Couldn't've Had A V-8")
        test("don't come home if you don't get 1st", "Don't Come Home If You Don't Get 1st")
        test("""i said "no, i didn't", you idiot""", """I Said "No, I Didn't", You Idiot""")
        test('multiple «"“quote marks”"»', 'Multiple «"“Quote Marks”"»', test_ascii=False)
        test('my head is my only house (when it rains)', 'My Head Is My Only House (When It Rains)')

        test("""i said ZdonXt touch that, oXconnell!Z, you 2nd rate idiot!""", """I Said ZDonXt Touch That, OXConnell!Z, You 2nd Rate Idiot!""", apostrophes='X', double_quotes='Z')

        with self.assertRaises(TypeError):
            big.gently_title("the \"string's\" the thing", apostrophes=big.ascii_apostrophes)
        with self.assertRaises(TypeError):
            big.gently_title("the \"string's\" the thing", double_quotes=big.ascii_double_quotes)
        with self.assertRaises(TypeError):
            big.gently_title("the \"string's\" the thing", apostrophes=big.ascii_apostrophes, double_quotes=big.ascii_double_quotes)

        with self.assertRaises(TypeError):
            big.gently_title("the \"string's\" the thing", apostrophes=(b"'",))
        with self.assertRaises(TypeError):
            big.gently_title("the \"string's\" the thing", double_quotes=(b'"',))
        with self.assertRaises(TypeError):
            big.gently_title("the \"string's\" the thing", apostrophes=(b"'",), double_quotes=(b'"',))


        with self.assertRaises(TypeError):
            big.gently_title(b"the \"string's\" the thing", apostrophes=big.apostrophes)
        with self.assertRaises(TypeError):
            big.gently_title(b"the \"string's\" the thing", double_quotes=big.double_quotes)
        with self.assertRaises(TypeError):
            big.gently_title(b"the \"string's\" the thing", apostrophes=big.apostrophes, double_quotes=big.double_quotes)

        with self.assertRaises(TypeError):
            big.gently_title(b"the \"string's\" the thing", apostrophes=("'",))
        with self.assertRaises(TypeError):
            big.gently_title(b"the \"string's\" the thing", double_quotes=('"',))
        with self.assertRaises(TypeError):
            big.gently_title(b"the \"string's\" the thing", apostrophes=("'",), double_quotes=('"',))

        with self.assertRaises(TypeError):
            big.gently_title(StrSubclass("the \"string's\" the thing"), apostrophes=BytesSubclass(big.ascii_apostrophes))
        with self.assertRaises(TypeError):
            big.gently_title(StrSubclass("the \"string's\" the thing"), double_quotes=BytesSubclass(big.ascii_double_quotes))

        with self.assertRaises(TypeError):
            big.gently_title(BytesSubclass(b"the \"string's\" the thing"), apostrophes=StrSubclass(big.apostrophes))
        with self.assertRaises(TypeError):
            big.gently_title(BytesSubclass(b"the \"string's\" the thing"), double_quotes=StrSubclass(big.double_quotes))

        self.assertEqual(
            big.gently_title(StrSubclass("peter o'toole"), apostrophes=DifferentStrSubclass(big.apostrophes)),
             "Peter O'Toole"
             )
        self.assertEqual(
            big.gently_title(BytesSubclass(b"peter o'toole"), apostrophes=DifferentBytesSubclass(big.ascii_apostrophes)),
             b"Peter O'Toole"
             )

        with self.assertRaises(ValueError):
            big.gently_title("the \"string's\" the thing", apostrophes='')
        with self.assertRaises(ValueError):
            big.gently_title("the \"string's\" the thing", apostrophes=("'", ''))
        with self.assertRaises(ValueError):
            big.gently_title("the \"string's\" the thing", double_quotes='')
        with self.assertRaises(ValueError):
            big.gently_title("the \"string's\" the thing", double_quotes=('"', ''))

        with self.assertRaises(ValueError):
            big.gently_title(b"the \"string's\" the thing", apostrophes=b'')
        with self.assertRaises(ValueError):
            big.gently_title(b"the \"string's\" the thing", apostrophes=(b"'", b''))
        with self.assertRaises(ValueError):
            big.gently_title(b"the \"string's\" the thing", double_quotes=b'')
        with self.assertRaises(ValueError):
            big.gently_title(b"the \"string's\" the thing", double_quotes=(b'"', b''))


    def test_normalize_whitespace(self):
        def test(s, expected, *, separators=None, replacement=" "):
            for i in range(2):
                result = big.normalize_whitespace(s, separators=separators, replacement=replacement)
                self.assertEqual(result, expected)
                if i:
                    break

                s = to_bytes(s)
                expected = to_bytes(expected)
                separators = to_bytes(separators)
                replacement = to_bytes(replacement)

        test("   a    b    c", " a b c")

        test("d     e  \t\n  f ", "d e f ")
        test("ghi", "ghi", replacement=None)
        test("   j     kl   mnop    ", " j kl mnop ")
        test("", "")
        test("   \n\n\t \t     ", " ")

        test("   j     kl   mnop    ", "XjXklXmnopX", replacement="X")
        test("   j     kl   mnop    ", "QQjQQklQQmnopQQ", replacement="QQ")
        test("   j     kl   mnop    ", "jklmnop", replacement="")

        test('DEFabacabGHI',        'DEF+GHI',  separators=('a', 'b', 'c'), replacement='+')
        test('DEFabacabGHIaaa',     'DEF+GHI+', separators=('a', 'b', 'c'), replacement='+')
        test('abcDEFabacabGHI',    '+DEF+GHI',  separators=('a', 'b', 'c'), replacement='+')
        test('abcDEFabacabGHIaaa', '+DEF+GHI+', separators=('a', 'b', 'c'), replacement='+')
        test('abcDEFabacabGHIaaa', '+DEF+GHI+', separators='abc', replacement='+')

        with self.assertRaises(TypeError):
            big.normalize_whitespace("abc", "b", -1)
        with self.assertRaises(TypeError):
            big.normalize_whitespace("abc", -1, "b")
        with self.assertRaises(ValueError):
            big.normalize_whitespace("abc", "", "c")
        with self.assertRaises(ValueError):
            big.normalize_whitespace("abc", ('a', "", 'b'), "c")
        with self.assertRaises(TypeError):
            big.normalize_whitespace(b"abc", "b", "c")
        with self.assertRaises(TypeError):
            big.normalize_whitespace("abc", b"b", "c")
        with self.assertRaises(TypeError):
            big.normalize_whitespace("abc", "b", b"c")

        # test that we didn't accidentally use the "fast path"
        # with bytes objects
        string_with_em_space = "ab\u2003cd"
        result = "ab cd"
        self.assertEqual(big.normalize_whitespace("ab\u2003cd"), result)
        self.assertEqual(big.normalize_whitespace("ab\u2003cd".encode('utf-8'), big.utf8_whitespace), result.encode('utf-8'))

        with self.assertRaises(ValueError):
            big.normalize_whitespace("a b c d   e", separators='')
        with self.assertRaises(ValueError):
            big.normalize_whitespace("a b c d   e", separators=[])
        with self.assertRaises(ValueError):
            big.normalize_whitespace(b"a b c d   e", separators=b'')
        with self.assertRaises(ValueError):
            big.normalize_whitespace(b"a b c d   e", separators=[])

    def test_split_quoted_strings(self):
        def test(s, expected, **kwargs):
            got = list(big.split_quoted_strings(s, **kwargs))
            self.assertEqual(got, expected)

            got = list(big.split_quoted_strings(s.encode('ascii'), **kwargs))
            self.assertEqual(got, [(b, s.encode('ascii')) for b, s in expected])

        test("""hey there "this is quoted" an empty quote: '' this is not quoted 'this is more quoted' "here's quoting a quote mark: \\" wow!" this is working!""",
            [
                (False, 'hey there '),
                (True, '"this is quoted"'),
                (False, ' an empty quote: '),
                (True, "''"),
                (False, ' this is not quoted '),
                (True, "'this is more quoted'"),
                (False, ' '),
                (True, '"here\'s quoting a quote mark: \\" wow!"'),
                (False, ' this is working!'),
            ])

        test('''here is triple quoted: """i am triple quoted.""" wow!  again: """triple quoted here. "quotes in quotes" empty: "" done.""" phew!''',
            [
                (False, 'here is triple quoted: '),
                (True, '"""i am triple quoted."""'),
                (False, ' wow!  again: '),
                (True, '"""triple quoted here. "quotes in quotes" empty: "" done."""'),
                (False, ' phew!'),
            ])

        test('''test turning off quoted strings.  """howdy doodles""" it kinda works anyway!''',
            [
                (False, 'test turning off quoted strings.  '),
                (True, '""'),
                (True, '"howdy doodles"'),
                (True, '""'),
                (False, ' it kinda works anyway!'),
            ],
            triple_quotes=False)

    def test_parse_delimiters(self):

        def test(s, expected, *, delimiters=None):
            empty = ''
            for i in range(2):
                got = tuple(big.parse_delimiters(s, delimiters=delimiters))

                flattened = []
                for t in got:
                    flattened.extend(t)
                s2 = empty.join(flattened)
                self.assertEqual(s, s2)

                self.assertEqual(expected, got)

                if not i:
                    s = to_bytes(s)
                    expected = to_bytes(expected)
                    empty = b''

        test('a[x] = foo("howdy (folks)\\n", {1:2, 3:4})',
            (
                ('a',                '[',  ''),
                ('x',                 '', ']'),
                (' = foo',           '(',  ''),
                ('',                 '"',  ''),
                ('howdy (folks)\\n',  '', '"'),
                (', ',               '{',  ''),
                ('1:2, 3:4',          '', '}'),
                ('',                  '', ')'),
            ),
            )

        test('a[[[z]]]{{{{q}}}}[{[{[{[{z}]}]}]}]!',
            (
                ('a', '[',  ''),
                ('',  '[',  ''),
                ('',  '[',  ''),
                ('z',  '', ']'),
                ('',   '', ']'),
                ('',   '', ']'),
                ('',  '{',  ''),
                ('',  '{',  ''),
                ('',  '{',  ''),
                ('',  '{',  ''),
                ('q',  '', '}'),
                ('',   '', '}'),
                ('',   '', '}'),
                ('',   '', '}'),
                ('',  '[',  ''),
                ('',  '{',  ''),
                ('',  '[',  ''),
                ('',  '{',  ''),
                ('',  '[',  ''),
                ('',  '{',  ''),
                ('',  '[',  ''),
                ('',  '{',  ''),
                ('z',  '', '}'),
                ('',   '', ']'),
                ('',   '', '}'),
                ('',   '', ']'),
                ('',   '', '}'),
                ('',   '', ']'),
                ('',   '', '}'),
                ('',   '', ']'),
                ('!',  '',  ''),
            ),
            )

        with self.assertRaises(ValueError):
            test('a[3)', None)
        with self.assertRaises(ValueError):
            test('a{3]', None)
        with self.assertRaises(ValueError):
            test('a(3}', None)

        with self.assertRaises(ValueError):
            test('delimiters is empty', None, delimiters=[])
        with self.assertRaises(ValueError):
            test('delimiter is abc (huh!)', None, delimiters=['()', 'abc'])
        with self.assertRaises(TypeError):
            test('delimiters contains 3', None, delimiters=['{}', 3])
        with self.assertRaises(ValueError):
            test('delimiters contains a <backslash>', None, delimiters=['<>', '\\/'])
        with self.assertRaises(ValueError):
            test('delimiters contains <angle> <brackets> <twice>', None, delimiters=['<>', '<>'])

        with self.assertRaises(ValueError):
            test('unclosed_paren(a[3]', None)
        with self.assertRaises(ValueError):
            test('x[3] = unclosed_curly{', None)
        with self.assertRaises(ValueError):
            test('foo(a[1], {a[2]: 33}) = unclosed_square[55', None)
        with self.assertRaises(ValueError):
            test('"unterminated string\\', None)
        with self.assertRaises(ValueError):
            test('open_everything( { a[35 "foo', None)

        with self.assertRaises(TypeError):
            big.Delimiter('(', b')')
        with self.assertRaises(TypeError):
            big.Delimiter(b'(', ')')

    def test_lines(self):
        def test(i, expected):
            got = list(i)
            self.assertEqual(got, expected)

        LI = big.LineInfo

        def L(line, line_number, column_number=1, **kwargs):
            info = big.LineInfo(line, line_number, column_number, **kwargs)
            return (info, line)

        test(big.lines("a\nb\nc\nd\ne\n"),
            [
            (LI('a', 1, 1), 'a'),
            (LI('b', 2, 1), 'b'),
            (LI('c', 3, 1), 'c'),
            (LI('d', 4, 1), 'd'),
            (LI('e', 5, 1), 'e'),
            (LI('',  6, 1), ''),
            ])

        lines = ['first line', '\tsecond line', 'third line']
        test(big.lines_strip(big.lines(lines)),
            [
            (LI('first line', 1, 1), 'first line'),
            (LI('\tsecond line', 2, 9, leading='\t'), 'second line'),
            (LI('third line', 3, 1), 'third line'),
            ])

        test(big.lines_filter_comment_lines(big.lines("""
    # comment
    a = b
    // another comment
    c = d
    / not a comment
    /// is a comment!
    ## another comment!
    #! a third comment!
""".lstrip('\n')), ('#', '//')),
            [
            (LI('    a = b',           2, 1), '    a = b'),
            (LI('    c = d',           4, 1), '    c = d'),
            (LI('    / not a comment', 5, 1), '    / not a comment'),
            (LI('',                    9, 1), ''),
            ])

        test(big.lines_filter_comment_lines(big.lines(b"a\n# ignored\n c"), b'#'),
            [
            L(b'a', 1),
            L(b' c', 3),
            ]
            )

        test(big.lines_containing(big.lines("""
hello yolks
what do you have to say, champ?
i like eggs.
they don't have to be fancy.
simple scrambled eggs are just fine.
neggatory!
whoops, I meant, negatory.
"""[1:]), "egg"),
            [
                (LI('i like eggs.', 3, 1), 'i like eggs.'),
                (LI('simple scrambled eggs are just fine.', 5, 1), 'simple scrambled eggs are just fine.'),
                (LI('neggatory!', 6, 1), 'neggatory!'),
            ]
            )

        test(big.lines_containing(big.lines("""
hello yolks
what do you have to say, champ?
i like eggs.
they don't have to be fancy.
simple scrambled eggs are just fine.
neggatory!
whoops, I meant, negatory.
"""[1:]), "egg", invert=True),
            [
                (LI('hello yolks', 1, 1), 'hello yolks'),
                (LI('what do you have to say, champ?', 2, 1), 'what do you have to say, champ?'),
                (LI("they don't have to be fancy.", 4, 1), "they don't have to be fancy."),
                (LI('whoops, I meant, negatory.', 7, 1), 'whoops, I meant, negatory.'),
                (LI('', 8, 1), ''),
            ]
            )

        test(big.lines_grep(big.lines("""
hello yolks
what do you have to say, champ?
i like eggs.
they don't have to be fancy.
simple scrambled eggs are just fine.
neggatory!
whoops, I meant, negatory.
"""[1:]), "eg+"),
            [
                (LI('i like eggs.', 3, 1), 'i like eggs.'),
                (LI('simple scrambled eggs are just fine.', 5, 1), 'simple scrambled eggs are just fine.'),
                (LI('neggatory!', 6, 1), 'neggatory!'),
                (LI('whoops, I meant, negatory.', 7, 1), 'whoops, I meant, negatory.'),
            ]
            )

        test(big.lines_grep(big.lines("""
hello yolks
what do you have to say, champ?
i like eggs.
they don't have to be fancy.
simple scrambled eggs are just fine.
neggatory!
whoops, I meant, negatory.
"""[1:]), "eg+", invert=True),
            [
                (LI('hello yolks', 1, 1), 'hello yolks'),
                (LI('what do you have to say, champ?', 2, 1), 'what do you have to say, champ?'),
                (LI("they don't have to be fancy.", 4, 1), "they don't have to be fancy."),
                (LI('', 8, 1), ''),
            ]
            )

        test(big.lines_sort(big.lines("""
cormorant
firefox
alligator
diplodocus
elephant
giraffe
barracuda
hummingbird
"""[1:-1])),
            [
                L('alligator', 3),
                L('barracuda', 7),
                L('cormorant', 1),
                L('diplodocus', 4),
                L('elephant', 5),
                L('firefox', 2),
                L('giraffe', 6),
                L('hummingbird', 8),
            ]
            )

        test(big.lines_sort(big.lines("""
cormorant
firefox
alligator
diplodocus
elephant
giraffe
barracuda
hummingbird
"""[1:-1]), reverse=True),
            [
                L('hummingbird', 8),
                L('giraffe', 6),
                L('firefox', 2),
                L('elephant', 5),
                L('diplodocus', 4),
                L('cormorant', 1),
                L('barracuda', 7),
                L('alligator', 3),
            ]
            )

        test(big.lines_rstrip(big.lines(
"    a = b  \n"
"    c = d     \n"
)),
            [
            (LI('    a = b  ',    1, 1), '    a = b'),
            (LI('    c = d     ', 2, 1), '    c = d'),
            (LI('',               3, 1), ''),
            ])

        test(big.lines_strip(big.lines(
"    a = b  \n"
"    c = d     \n"
)),
            [
            (LI('    a = b  ',    1, 5, leading='    '), 'a = b'),
            (LI('    c = d     ', 2, 5, leading='    '), 'c = d'),
            (LI('',               3, 1), ''),
            ])

        test(big.lines_filter_empty_lines(big.lines("""

    a = b


    c = d

"""[1:])),
            [
            (LI('    a = b', 2, 1), '    a = b'),
            (LI('    c = d', 5, 1), '    c = d'),
            ])

        test(big.lines_convert_tabs_to_spaces(big.lines(
            "\tfirst line\n"
            "\t\tsecond line\n"
            "  \tthird line\n",
            tab_width=8)),
            [
                (LI("\tfirst line", 1, 1), "        first line"),
                (LI("\t\tsecond line", 2, 1), "                second line"),
                (LI("  \tthird line", 3, 1), "        third line"),
                (LI("", 4, 1), ""),
            ])

        test(big.lines_strip_comments(big.lines("""
for x in range(5): # this is a comment
    print("# this is quoted", x)
    print("") # this "comment" is useless
    print(no_comments_or_quotes_on_this_line)
"""[1:]), ("#", "//")),
            [
                (LI(line='for x in range(5): # this is a comment', line_number=1, column_number=1, comment='# this is a comment'),
                    'for x in range(5):'),
                (LI(line='    print("# this is quoted", x)', line_number=2, column_number=1, comment=''),
                    '    print("# this is quoted", x)'),
                (LI(line='    print("") # this "comment" is useless', line_number=3, column_number=1, comment='# this "comment" is useless'),
                    '    print("")'),
                (LI(line='    print(no_comments_or_quotes_on_this_line)', line_number=4, column_number=1, comment=''),
                    '    print(no_comments_or_quotes_on_this_line)'),
                (LI(line='', line_number=5, column_number=1, comment=''),
                    '')
            ])

        test(big.lines_strip_comments(big.lines("""
for x in range(5): # this is a comment
    print("# this is quoted", x)
    print("") # this "comment" is useless
    print(no_comments_or_quotes_on_this_line)
"""[1:]), ("#", "//"), quotes=None),
            [
                (LI(line='for x in range(5): # this is a comment', line_number=1, column_number=1, comment='# this is a comment'),
                  'for x in range(5):'),
                (LI(line='    print("# this is quoted", x)', line_number=2, column_number=1, comment='# this is quoted", x)'),
                    '    print("'),
                (LI(line='    print("") # this "comment" is useless', line_number=3, column_number=1, comment='# this "comment" is useless'),
                    '    print("")'),
                (LI(line='    print(no_comments_or_quotes_on_this_line)', line_number=4, column_number=1, comment=''),
                    '    print(no_comments_or_quotes_on_this_line)'),
                (LI(line='', line_number=5, column_number=1, comment=''),
                    ''),
            ])

        with self.assertRaises(ValueError):
            test(big.lines_strip_comments(big.lines("a\nb\n"), None), [])

        test(big.lines_strip_comments(big.lines(b"a\nb# ignored\n c"), b'#'),
            [
            L(b'a', 1, comment=b''),
            (LI(b'b# ignored', 2, 1, comment=b'# ignored'), b'b'),
            L(b' c', 3, comment=b''),
            ]
            )


        test(big.lines_filter_empty_lines(big.lines_filter_comment_lines(big.lines_strip(big.lines(
"   \n" +
"    a = b \n" +
"   \n" +
"    # comment line \n" +
"    \n" +
"    \n" +
"    c = d  \n" +
"     \n")), '#')),
            [
            (LI('    a = b ',  2, 5, leading='    '), 'a = b'),
            (LI('    c = d  ', 7, 5, leading='    '), 'c = d'),
            ])


    def test_lines_strip_indent(self):
        def test(lines, expected, *, tab_width=8):
            got = list(big.lines_strip_indent(big.lines(lines, tab_width=tab_width)))
            self.assertEqual(got, expected)


        LineInfo = big.text.LineInfo

        lines = """
left margin
if 3:
    text
else:
    if 1:
          other text
          other text
    more text
      different indent
    outdent
outdent
  new indent
outdent
"""

        expected = [
            (LineInfo(line='', line_number=1, column_number=1, indent=0, leading=''),
                ''),
            (LineInfo(line='left margin', line_number=2, column_number=1, indent=0, leading=''),
                'left margin'),
            (LineInfo(line='if 3:', line_number=3, column_number=1, indent=0, leading=''),
                'if 3:'),
            (LineInfo(line='    text', line_number=4, column_number=5, indent=1, leading='    '),
                'text'),
            (LineInfo(line='else:', line_number=5, column_number=1, indent=0, leading=''),
                'else:'),
            (LineInfo(line='    if 1:', line_number=6, column_number=5, indent=1, leading='    '),
                'if 1:'),
            (LineInfo(line='          other text', line_number=7, column_number=11, indent=2, leading='          '),
                'other text'),
            (LineInfo(line='          other text', line_number=8, column_number=11, indent=2, leading='          '),
                'other text'),
            (LineInfo(line='    more text', line_number=9, column_number=5, indent=1, leading='    '),
                'more text'),
            (LineInfo(line='      different indent', line_number=10, column_number=7, indent=2, leading='      '),
                'different indent'),
            (LineInfo(line='    outdent', line_number=11, column_number=5, indent=1, leading='    '),
                'outdent'),
            (LineInfo(line='outdent', line_number=12, column_number=1, indent=0, leading=''),
                'outdent'),
            (LineInfo(line='  new indent', line_number=13, column_number=3, indent=1, leading='  '),
                'new indent'),
            (LineInfo(line='outdent', line_number=14, column_number=1, indent=0, leading=''),
                'outdent'),
            (LineInfo(line='', line_number=15, column_number=1, indent=0, leading=''),
                ''),
            ]

        test(lines, expected)


        ##
        ## test tab to spaces
        ##

        lines = (
        "left margin\n"
        "\teight\n"
        "  \t    twelve\n"
        "        eight is enough\n"
        )

        expected = [
            (LineInfo(line='left margin', line_number=1, column_number=1, indent=0, leading=''),
                'left margin'),
            (LineInfo(line='\teight', line_number=2, column_number=9, indent=1, leading='\t'),
                'eight'),
            (LineInfo(line='  \t    twelve', line_number=3, column_number=13, indent=2, leading='  \t    '),
                'twelve'),
            (LineInfo(line='        eight is enough', line_number=4, column_number=9, indent=1, leading='        '),
                'eight is enough'),
            (LineInfo(line='', line_number=5, column_number=1, indent=0, leading=''),
                '')
            ]

        test(lines, expected)

        lines = (
            "left margin\n"
            "\tfour\n"
            "  \t    eight\n"
            "  \t\tfigure eight is double four\n"
            "    figure four is half of eight\n"
            )

        expected = [
            (LineInfo(line='left margin', line_number=1, column_number=1, indent=0, leading=''),
                'left margin'),
            (LineInfo(line='\tfour', line_number=2, column_number=5, indent=1, leading='\t'),
                'four'),
            (LineInfo(line='  \t    eight', line_number=3, column_number=9, indent=2, leading='  \t    '),
                'eight'),
            (LineInfo(line='  \t\tfigure eight is double four', line_number=4, column_number=9, indent=2, leading='  \t\t'),
                'figure eight is double four'),
            (LineInfo(line='    figure four is half of eight', line_number=5, column_number=5, indent=1, leading='    '),
                'figure four is half of eight'),
            (LineInfo(line='', line_number=6, column_number=1, indent=0, leading=''),
                '')]

        test(lines, expected, tab_width=4)

        ##
        ## test raising for illegal outdents
        ##

        # when it's between two existing indents
        lines = (
            "left margin\n"
            "\tfour\n"
            "  \t    eight\n"
            "      six?!\n"
            "left margin again\n"
            )

        with self.assertRaises(IndentationError):
            test(lines, [], tab_width=4)


        # when it's less than the first indent
        lines = (
            "left margin\n"
            "\tfour\n"
            "  \t    eight\n"
            "  two?!\n"
            "left margin again\n"
            )

        with self.assertRaises(IndentationError):
            test(lines, [], tab_width=4)

        with self.assertRaises(ValueError):
            test("first line\n  \u3000  second line\nthird line\n", [])

    def test_lines_misc(self):
        ## repr
        li = big.LineInfo('', 1, 1, indent=0)
        self.assertEqual(repr(li), "LineInfo(line='', line_number=1, column_number=1, indent=0)")

        ## error handling
        with self.assertRaises(TypeError):
            big.lines("", line_number=math.pi)
        with self.assertRaises(TypeError):
            big.lines("", column_number=math.pi)
        with self.assertRaises(TypeError):
            big.lines("", tab_width=math.pi)

        with self.assertRaises(TypeError):
            big.LineInfo(math.pi, 1, 1)
        with self.assertRaises(TypeError):
            big.LineInfo('', math.pi, 1)
        with self.assertRaises(TypeError):
            big.LineInfo('', 1, math.pi)

        with self.assertRaises(ValueError):
            list(big.lines_filter_comment_lines("", []))
        with self.assertRaises(TypeError):
            list(big.lines_filter_comment_lines("", math.pi))

        ## test kwargs
        i = big.lines('', quark=22)
        self.assertTrue(hasattr(i, 'quark'))
        self.assertEqual(getattr(i, 'quark'), 22)

        info = big.LineInfo('', 1, 1, quark=35)
        self.assertTrue(hasattr(info, 'quark'))
        self.assertEqual(getattr(info, 'quark'), 35)

    def test_int_to_words(self):
        # confirm that flowery has a default of True
        self.assertEqual(big.int_to_words(12345678), big.int_to_words(12345678, flowery=True))

        with self.assertRaises(ValueError):
            big.int_to_words(3.14159)
        with self.assertRaises(ValueError):
            big.int_to_words('hello sailor')
        with self.assertRaises(ValueError):
            big.int_to_words({1:2, 3:4})

        def test(i, normal, flowery):
            def cardinal_to_ordinal(s):
                for old, new in (
                    ("zero", "zeroth"),
                    ("one", "first"),
                    ("two", "second"),
                    ("three", "third"),
                    ("four", "fourth"),
                    ("five", "fifth"),
                    ("six", "sixth"),
                    ("seven", "seventh"),
                    ("eight", "eighth"),
                    ("nine", "ninth"),
                    ("ten", "tenth"),
                    ("eleven", "eleventh"),
                    ("twelve", "twelveth"),
                    ("thirteen", "thirteenth"),
                    ("fourteen", "fourteenth"),
                    ("fifteen", "fifteenth"),
                    ("sixteen", "sixteenth"),
                    ("seventeen", "seventeenth"),
                    ("eighteen", "eighteenth"),
                    ("nineteen", "nineteenth"),
                    ("twenty", "twentieth"),
                    ("thirty", "thirtieth"),
                    ("forty", "fortieth"),
                    ("fifty", "fiftieth"),
                    ("sixty", "sixtieth"),
                    ("seventy", "seventieth"),
                    ("eighty", "eightieth"),
                    ("ninety", "ninetieth"),

                    ("hundred", "hundredth"),
                    ("thousand", "thousandth"),
                    ("million", "millionth"),
                    ):
                    if s.endswith(old):
                        s = s[:-len(old)] + new
                return s

            for multiplier, prefix, inflected_prefix in (
                (1, "", ""),
                (-1, "negative ", "minus ")
                ):

                if (i >= 10**75) and prefix:
                    prefix = "-"

                i *= multiplier

                result = prefix + normal
                self.assertEqual(big.int_to_words(i, flowery=False), result)
                result = cardinal_to_ordinal(result)
                self.assertEqual(big.int_to_words(i, flowery=False, ordinal=True), result)

                result = prefix + flowery
                self.assertEqual(big.int_to_words(i, flowery=True), result)
                result = cardinal_to_ordinal(result)
                self.assertEqual(big.int_to_words(i, flowery=True, ordinal=True), result)

                # if inflect is available, confirm that int_to_words
                # produces identical output to inflect.number_to_words.
                # well, except, they prefer prepending the word "minus"
                # for negative numbers, and I prefer prepending "negative".

                if engine:
                    try:
                        minus_fixed_flowery = big.int_to_words(i, flowery=True).replace("negative ", "minus ")
                        self.assertEqual(engine.number_to_words(i), minus_fixed_flowery)
                    except inflect.NumOutOfRangeError:
                        pass

                # don't test "-0".  this dumb test harness isn't smart enough.
                if not i:
                    break

        test(                    0,
            'zero',
            'zero')

        test(                    1,
            'one',
            'one')

        test(                    2,
            'two',
            'two')

        test(                    3,
            'three',
            'three')

        test(                    4,
            'four',
            'four')

        test(                    5,
            'five',
            'five')

        test(                    6,
            'six',
            'six')

        test(                    7,
            'seven',
            'seven')

        test(                    8,
            'eight',
            'eight')

        test(                    9,
            'nine',
            'nine')

        test(                   10,
            'ten',
            'ten')

        test(                   11,
            'eleven',
            'eleven')

        test(                   12,
            'twelve',
            'twelve')

        test(                   13,
            'thirteen',
            'thirteen')

        test(                   14,
            'fourteen',
            'fourteen')

        test(                   15,
            'fifteen',
            'fifteen')

        test(                   16,
            'sixteen',
            'sixteen')

        test(                   17,
            'seventeen',
            'seventeen')

        test(                   18,
            'eighteen',
            'eighteen')

        test(                   19,
            'nineteen',
            'nineteen')

        test(                   20,
            'twenty',
            'twenty')

        test(                   21,
            'twenty-one',
            'twenty-one')

        test(                   22,
            'twenty-two',
            'twenty-two')

        test(                   23,
            'twenty-three',
            'twenty-three')

        test(                   24,
            'twenty-four',
            'twenty-four')

        test(                   25,
            'twenty-five',
            'twenty-five')

        test(                   26,
            'twenty-six',
            'twenty-six')

        test(                   27,
            'twenty-seven',
            'twenty-seven')

        test(                   28,
            'twenty-eight',
            'twenty-eight')

        test(                   29,
            'twenty-nine',
            'twenty-nine')

        test(                   30,
            'thirty',
            'thirty')

        test(                   40,
            'forty',
            'forty')

        test(                   41,
            'forty-one',
            'forty-one')

        test(                   42,
            'forty-two',
            'forty-two')

        test(                   50,
            'fifty',
            'fifty')

        test(                   51,
            'fifty-one',
            'fifty-one')

        test(                   52,
            'fifty-two',
            'fifty-two')

        test(                   60,
            'sixty',
            'sixty')

        test(                   61,
            'sixty-one',
            'sixty-one')

        test(                   62,
            'sixty-two',
            'sixty-two')

        test(                   70,
            'seventy',
            'seventy')

        test(                   71,
            'seventy-one',
            'seventy-one')

        test(                   72,
            'seventy-two',
            'seventy-two')

        test(                   80,
            'eighty',
            'eighty')

        test(                   81,
            'eighty-one',
            'eighty-one')

        test(                   82,
            'eighty-two',
            'eighty-two')

        test(                   90,
            'ninety',
            'ninety')

        test(                   91,
            'ninety-one',
            'ninety-one')

        test(                   92,
            'ninety-two',
            'ninety-two')

        test(                  100,
            'one hundred',
            'one hundred')

        test(                  101,
            'one hundred one',
            'one hundred and one')

        test(                  102,
            'one hundred two',
            'one hundred and two')

        test(                  200,
            'two hundred',
            'two hundred')

        test(                  201,
            'two hundred one',
            'two hundred and one')

        test(                  202,
            'two hundred two',
            'two hundred and two')

        test(                  211,
            'two hundred eleven',
            'two hundred and eleven')

        test(                  222,
            'two hundred twenty-two',
            'two hundred and twenty-two')

        test(                  300,
            'three hundred',
            'three hundred')

        test(                  301,
            'three hundred one',
            'three hundred and one')

        test(                  302,
            'three hundred two',
            'three hundred and two')

        test(                  311,
            'three hundred eleven',
            'three hundred and eleven')

        test(                  322,
            'three hundred twenty-two',
            'three hundred and twenty-two')

        test(                  400,
            'four hundred',
            'four hundred')

        test(                  401,
            'four hundred one',
            'four hundred and one')

        test(                  402,
            'four hundred two',
            'four hundred and two')

        test(                  411,
            'four hundred eleven',
            'four hundred and eleven')

        test(                  422,
            'four hundred twenty-two',
            'four hundred and twenty-two')

        test(                  500,
            'five hundred',
            'five hundred')

        test(                  501,
            'five hundred one',
            'five hundred and one')

        test(                  502,
            'five hundred two',
            'five hundred and two')

        test(                  511,
            'five hundred eleven',
            'five hundred and eleven')

        test(                  522,
            'five hundred twenty-two',
            'five hundred and twenty-two')

        test(                  600,
            'six hundred',
            'six hundred')

        test(                  601,
            'six hundred one',
            'six hundred and one')

        test(                  602,
            'six hundred two',
            'six hundred and two')

        test(                  611,
            'six hundred eleven',
            'six hundred and eleven')

        test(                  622,
            'six hundred twenty-two',
            'six hundred and twenty-two')

        test(                  700,
            'seven hundred',
            'seven hundred')

        test(                  701,
            'seven hundred one',
            'seven hundred and one')

        test(                  702,
            'seven hundred two',
            'seven hundred and two')

        test(                  711,
            'seven hundred eleven',
            'seven hundred and eleven')

        test(                  722,
            'seven hundred twenty-two',
            'seven hundred and twenty-two')

        test(                  800,
            'eight hundred',
            'eight hundred')

        test(                  801,
            'eight hundred one',
            'eight hundred and one')

        test(                  802,
            'eight hundred two',
            'eight hundred and two')

        test(                  811,
            'eight hundred eleven',
            'eight hundred and eleven')

        test(                  822,
            'eight hundred twenty-two',
            'eight hundred and twenty-two')

        test(                  900,
            'nine hundred',
            'nine hundred')

        test(                  901,
            'nine hundred one',
            'nine hundred and one')

        test(                  902,
            'nine hundred two',
            'nine hundred and two')

        test(                  911,
            'nine hundred eleven',
            'nine hundred and eleven')

        test(                  922,
            'nine hundred twenty-two',
            'nine hundred and twenty-two')

        test(                 1000,
            'one thousand',
            'one thousand')

        test(                 1001,
            'one thousand one',
            'one thousand and one')

        test(                 1002,
            'one thousand two',
            'one thousand and two')

        test(                 1023,
            'one thousand twenty-three',
            'one thousand and twenty-three')

        test(                 1034,
            'one thousand thirty-four',
            'one thousand and thirty-four')

        test(                 1456,
            'one thousand four hundred fifty-six',
            'one thousand, four hundred and fifty-six')

        test(                 1567,
            'one thousand five hundred sixty-seven',
            'one thousand, five hundred and sixty-seven')

        test(                 2000,
            'two thousand',
            'two thousand')

        test(                 2001,
            'two thousand one',
            'two thousand and one')

        test(                 2002,
            'two thousand two',
            'two thousand and two')

        test(                 2023,
            'two thousand twenty-three',
            'two thousand and twenty-three')

        test(                 2034,
            'two thousand thirty-four',
            'two thousand and thirty-four')

        test(                 2456,
            'two thousand four hundred fifty-six',
            'two thousand, four hundred and fifty-six')

        test(                 2567,
            'two thousand five hundred sixty-seven',
            'two thousand, five hundred and sixty-seven')

        test(                 3000,
            'three thousand',
            'three thousand')

        test(                 3001,
            'three thousand one',
            'three thousand and one')

        test(                 3002,
            'three thousand two',
            'three thousand and two')

        test(                 3023,
            'three thousand twenty-three',
            'three thousand and twenty-three')

        test(                 3034,
            'three thousand thirty-four',
            'three thousand and thirty-four')

        test(                 3456,
            'three thousand four hundred fifty-six',
            'three thousand, four hundred and fifty-six')

        test(                 3567,
            'three thousand five hundred sixty-seven',
            'three thousand, five hundred and sixty-seven')

        test(                 4000,
            'four thousand',
            'four thousand')

        test(                 4001,
            'four thousand one',
            'four thousand and one')

        test(                 4002,
            'four thousand two',
            'four thousand and two')

        test(                 4023,
            'four thousand twenty-three',
            'four thousand and twenty-three')

        test(                 4034,
            'four thousand thirty-four',
            'four thousand and thirty-four')

        test(                 4456,
            'four thousand four hundred fifty-six',
            'four thousand, four hundred and fifty-six')

        test(                 4567,
            'four thousand five hundred sixty-seven',
            'four thousand, five hundred and sixty-seven')

        test(                 5000,
            'five thousand',
            'five thousand')

        test(                 5001,
            'five thousand one',
            'five thousand and one')

        test(                 5002,
            'five thousand two',
            'five thousand and two')

        test(                 5023,
            'five thousand twenty-three',
            'five thousand and twenty-three')

        test(                 5034,
            'five thousand thirty-four',
            'five thousand and thirty-four')

        test(                 5456,
            'five thousand four hundred fifty-six',
            'five thousand, four hundred and fifty-six')

        test(                 5567,
            'five thousand five hundred sixty-seven',
            'five thousand, five hundred and sixty-seven')

        test(                 6000,
            'six thousand',
            'six thousand')

        test(                 6001,
            'six thousand one',
            'six thousand and one')

        test(                 6002,
            'six thousand two',
            'six thousand and two')

        test(                 6023,
            'six thousand twenty-three',
            'six thousand and twenty-three')

        test(                 6034,
            'six thousand thirty-four',
            'six thousand and thirty-four')

        test(                 6456,
            'six thousand four hundred fifty-six',
            'six thousand, four hundred and fifty-six')

        test(                 6567,
            'six thousand five hundred sixty-seven',
            'six thousand, five hundred and sixty-seven')

        test(                 7000,
            'seven thousand',
            'seven thousand')

        test(                 7001,
            'seven thousand one',
            'seven thousand and one')

        test(                 7002,
            'seven thousand two',
            'seven thousand and two')

        test(                 7023,
            'seven thousand twenty-three',
            'seven thousand and twenty-three')

        test(                 7034,
            'seven thousand thirty-four',
            'seven thousand and thirty-four')

        test(                 7456,
            'seven thousand four hundred fifty-six',
            'seven thousand, four hundred and fifty-six')

        test(                 7567,
            'seven thousand five hundred sixty-seven',
            'seven thousand, five hundred and sixty-seven')

        test(                 8000,
            'eight thousand',
            'eight thousand')

        test(                 8001,
            'eight thousand one',
            'eight thousand and one')

        test(                 8002,
            'eight thousand two',
            'eight thousand and two')

        test(                 8023,
            'eight thousand twenty-three',
            'eight thousand and twenty-three')

        test(                 8034,
            'eight thousand thirty-four',
            'eight thousand and thirty-four')

        test(                 8456,
            'eight thousand four hundred fifty-six',
            'eight thousand, four hundred and fifty-six')

        test(                 8567,
            'eight thousand five hundred sixty-seven',
            'eight thousand, five hundred and sixty-seven')

        test(                 9000,
            'nine thousand',
            'nine thousand')

        test(                 9001,
            'nine thousand one',
            'nine thousand and one')

        test(                 9002,
            'nine thousand two',
            'nine thousand and two')

        test(                 9023,
            'nine thousand twenty-three',
            'nine thousand and twenty-three')

        test(                 9034,
            'nine thousand thirty-four',
            'nine thousand and thirty-four')

        test(                 9456,
            'nine thousand four hundred fifty-six',
            'nine thousand, four hundred and fifty-six')

        test(                 9567,
            'nine thousand five hundred sixty-seven',
            'nine thousand, five hundred and sixty-seven')

        test(                10000,
            'ten thousand',
            'ten thousand')

        test(                10001,
            'ten thousand one',
            'ten thousand and one')

        test(                10002,
            'ten thousand two',
            'ten thousand and two')

        test(                10023,
            'ten thousand twenty-three',
            'ten thousand and twenty-three')

        test(                10034,
            'ten thousand thirty-four',
            'ten thousand and thirty-four')

        test(                10456,
            'ten thousand four hundred fifty-six',
            'ten thousand, four hundred and fifty-six')

        test(                10567,
            'ten thousand five hundred sixty-seven',
            'ten thousand, five hundred and sixty-seven')

        test(                11000,
            'eleven thousand',
            'eleven thousand')

        test(                11001,
            'eleven thousand one',
            'eleven thousand and one')

        test(                11002,
            'eleven thousand two',
            'eleven thousand and two')

        test(                11023,
            'eleven thousand twenty-three',
            'eleven thousand and twenty-three')

        test(                11034,
            'eleven thousand thirty-four',
            'eleven thousand and thirty-four')

        test(                11456,
            'eleven thousand four hundred fifty-six',
            'eleven thousand, four hundred and fifty-six')

        test(                11567,
            'eleven thousand five hundred sixty-seven',
            'eleven thousand, five hundred and sixty-seven')

        test(                 1234,
            'one thousand two hundred thirty-four',
            'one thousand, two hundred and thirty-four')

        test(                 2468,
            'two thousand four hundred sixty-eight',
            'two thousand, four hundred and sixty-eight')

        test(           1234567890,
            'one billion two hundred thirty-four million five hundred sixty-seven thousand eight hundred ninety',
            'one billion, two hundred and thirty-four million, five hundred and sixty-seven thousand, eight hundred and ninety')

        test(        1234567890123,
            'one trillion two hundred thirty-four billion five hundred sixty-seven million eight hundred ninety thousand one hundred twenty-three',
            'one trillion, two hundred and thirty-four billion, five hundred and sixty-seven million, eight hundred and ninety thousand, one hundred and twenty-three')

        test(     1234567890123456,
            'one quadrillion two hundred thirty-four trillion five hundred sixty-seven billion eight hundred ninety million one hundred twenty-three thousand four hundred fifty-six',
            'one quadrillion, two hundred and thirty-four trillion, five hundred and sixty-seven billion, eight hundred and ninety million, one hundred and twenty-three thousand, four hundred and fifty-six')

        test(  1234567890123456789,
            'one quintillion two hundred thirty-four quadrillion five hundred sixty-seven trillion eight hundred ninety billion one hundred twenty-three million four hundred fifty-six thousand seven hundred eighty-nine',
            'one quintillion, two hundred and thirty-four quadrillion, five hundred and sixty-seven trillion, eight hundred and ninety billion, one hundred and twenty-three million, four hundred and fifty-six thousand, seven hundred and eighty-nine')

        test(451234567890123456789,
            'four hundred fifty-one quintillion two hundred thirty-four quadrillion five hundred sixty-seven trillion eight hundred ninety billion one hundred twenty-three million four hundred fifty-six thousand seven hundred eighty-nine',
            'four hundred and fifty-one quintillion, two hundred and thirty-four quadrillion, five hundred and sixty-seven trillion, eight hundred and ninety billion, one hundred and twenty-three million, four hundred and fifty-six thousand, seven hundred and eighty-nine')

        # test the top end
        test(10**75 - 1,
            'nine hundred ninety-nine billion nine hundred ninety-nine million nine hundred ninety-nine thousand nine hundred ninety-nine vigintillion nine hundred ninety-nine novemdecillion nine hundred ninety-nine octodecillion nine hundred ninety-nine septdecillion nine hundred ninety-nine sexdecillion nine hundred ninety-nine qindecillion nine hundred ninety-nine quattuordecillion nine hundred ninety-nine tredecillion nine hundred ninety-nine duodecillion nine hundred ninety-nine undecillion nine hundred ninety-nine   decillion nine hundred ninety-nine   nonillion nine hundred ninety-nine   octillion nine hundred ninety-nine  septillion nine hundred ninety-nine  sextillion nine hundred ninety-nine quintillion nine hundred ninety-nine quadrillion nine hundred ninety-nine trillion nine hundred ninety-nine billion nine hundred ninety-nine million nine hundred ninety-nine thousand nine hundred ninety-nine',
            'nine hundred and ninety-nine billion, nine hundred and ninety-nine million, nine hundred and ninety-nine thousand, nine hundred and ninety-nine vigintillion, nine hundred and ninety-nine novemdecillion, nine hundred and ninety-nine octodecillion, nine hundred and ninety-nine septdecillion, nine hundred and ninety-nine sexdecillion, nine hundred and ninety-nine qindecillion, nine hundred and ninety-nine quattuordecillion, nine hundred and ninety-nine tredecillion, nine hundred and ninety-nine duodecillion, nine hundred and ninety-nine undecillion, nine hundred and ninety-nine   decillion, nine hundred and ninety-nine   nonillion, nine hundred and ninety-nine   octillion, nine hundred and ninety-nine  septillion, nine hundred and ninety-nine  sextillion, nine hundred and ninety-nine quintillion, nine hundred and ninety-nine quadrillion, nine hundred and ninety-nine trillion, nine hundred and ninety-nine billion, nine hundred and ninety-nine million, nine hundred and ninety-nine thousand, nine hundred and ninety-nine',
            )

        test(10**75,
            '1000000000000000000000000000000000000000000000000000000000000000000000000000',
            '1000000000000000000000000000000000000000000000000000000000000000000000000000',
            )

def run_tests():
    bigtestlib.run(name="big.text", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
