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
bigtestlib.preload_local_big()

from big.test import raises, raises_regex, subtest

import big.all as big
from big.text import toy_multisplit
from big.all import lines, Pattern, python_delimiters, read_python_file, split_delimiters, string
import copy
import io
import itertools
import math
import os.path
import pathlib
import re
import sys
import textwrap
import types
import warnings

# this test file deliberately exercises multisplit's deprecated
# keep=ALTERNATING and keep=AS_PAIRS forms--they're supported until
# at least August 2027, so their behavior stays
# tested.  silence the DeprecationWarnings here; the warnings
# themselves are tested explicitly in test_multisplit_keep_deprecations.
warnings.filterwarnings('ignore', message="multisplit's keep=")
# likewise the deprecated lines pipeline: it ships until at least
# March 2027, so its behavior stays tested.  its warning is tested
# explicitly in test_lines_deprecation_warning.
warnings.filterwarnings('ignore', message="big's lines, LineInfo")



try:
    import inflect
    engine = inflect.engine()
except ImportError: # pragma: no cover
    engine = None


# Pattern and Match are Python 3.7+
try:
    from re import Pattern as re_Pattern
except ImportError: # pragma: no cover
    re_Pattern = re._pattern_type

try:
    from re import Match as re_Match
except ImportError: # pragma: no cover
    re_Match = type(re.match("x", "x"))

try:
    import regex
    have_regex = True
except ImportError: # pragma: no cover
    have_regex = False


_sentinel = object()


def dedent(text):
    # textwrap.dedent doesn't support bytes strings, LAME
    is_bytes = isinstance(text, bytes)
    if is_bytes:
        text = text.decode('utf-8')
    text = textwrap.dedent(text)
    if is_bytes:
        text = text.encode('utf-8')
    return text


def unchanged(o):
    return o

def to_bytes(o, memo=None): # pragma: no cover
    if o is None:
        return None
    if isinstance(o, bytes):
        return o
    if isinstance(o, str):
        return o.encode('ascii')
    if isinstance(o, list):
        return [to_bytes(x, memo) for x in o]
    if isinstance(o, tuple):
        return tuple(to_bytes(x, memo) for x in o)
    if isinstance(o, set):
        return set(to_bytes(x, memo) for x in o)
    if isinstance(o, dict):
        return {to_bytes(k, memo): to_bytes(v, memo) for k, v in o.items()}
    if isinstance(o, re_Pattern):
        flags = o.flags
        if flags & re.UNICODE:
            flags = flags - re.UNICODE
        return re.compile(to_bytes(o.pattern), flags=flags)
    if isinstance(o, big.Delimiter):
        # nested and change can contain reference cycles, so
        # convert the way you'd construct a cyclic grammar:
        # build the shell, remember it, then close the loop
        # by assigning nested and change.
        if memo is None:
            memo = {}
        converted = memo.get(id(o))
        if converted is not None:
            return converted
        converted = big.Delimiter(
            close=to_bytes(o.close),
            escape=to_bytes(o.escape),
            multiline=o.multiline,
            quoting=o.quoting,
            literal=to_bytes(o.literal),
            )
        memo[id(o)] = converted
        if o.nested:
            converted.nested = {to_bytes(k): to_bytes(v, memo) for k, v in o.nested.items()}
        if o.change:
            converted.change = {to_bytes(k): to_bytes(v, memo) for k, v in o.change.items()}
        return converted
    if isinstance(o, big.SplitDelimitersValue):
        return big.SplitDelimitersValue(to_bytes(o.text), to_bytes(o.open), to_bytes(o.close), to_bytes(o.change))
    return o


_iterate_over_bytes = big.text._iterate_over_bytes


#
# known_separators & printable_separators lets error messages
# print a symbolic name for a set of separators, instead of
# printing the actual value of the separators... which can be
# pretty freakin' unreadable.
#
known_separators = []

for symbol in """

    big.str_whitespace
    big.str_whitespace_without_crlf
    big.str_linebreaks
    big.str_linebreaks_without_crlf

    big.unicode_whitespace
    big.unicode_whitespace_without_crlf
    big.unicode_linebreaks
    big.unicode_linebreaks_without_crlf

    big.ascii_whitespace
    big.ascii_whitespace_without_crlf
    big.ascii_linebreaks
    big.ascii_linebreaks_without_crlf

""".strip().split('\n'):
    symbol = symbol.strip()
    if (not symbol) or symbol.startswith('#'):
        continue
    value = eval(symbol)
    known_separators.append((value, symbol))

def printable_separators(separators): # pragma: no cover
    # only called while rendering a failure message--and unlike
    # unittest msg= arguments, bare-assert messages are evaluated
    # lazily, so a green run never calls this
    for known, name in known_separators:
        if separators == known:
            return f"{name}"
    return separators


class StrSubclass(str):
    def __repr__(self): # pragma: no cover
        return "StrSubclass(" + super().__repr__() + ")"

    def __getitem__(self, index): # pragma: no cover
        return StrSubclass(super().__getitem__(index))

    def partition(self, sep): # pragma: no cover
        return StrSubclass(super().partition(sep))

    def rpartition(self, sep): # pragma: no cover
        return StrSubclass(super().rpartition(sep))

    def split(self, sep): # pragma: no cover
        return StrSubclass(super().split(sep))

    def rsplit(self, sep): # pragma: no cover
        return StrSubclass(super().rsplit(sep))

    def strip(self): # pragma: no cover
        return StrSubclass(super().strip())

    def lstrip(self): # pragma: no cover
        return StrSubclass(super().strip())

    def rstrip(self): # pragma: no cover
        return StrSubclass(super().strip())

    def join(self, iterable): # pragma: no cover
        return StrSubclass(super().join(iterable))




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



def pair_up(flat):
    """
    Converts a flat alternating list (segment, separator, segment,
    ..., segment) into the keep=True 2-tuple form the toys return.
    Lets test call sites keep their readable flat literals.
    """
    flat = list(flat)
    flat.append(flat[0][:0])    # typed always-empty trailing separator
    return list(zip(flat[::2], flat[1::2]))


def toy_multisplit_reverse(s, separators):
    """
    A toy version of multisplit in reverse mode.
    (A slightly-hacked version of toy_multisplit.)
    Like toy_multisplit, used by the test suite
    to verify that multisplit is working correctly.

    s is a str or bytes.
    separators is a str or iterable of str,
      or bytes or iterable of bytes.

    Returns a list equivalent to
        list(big.multisplit(s, separators, keep=True, separate=True, reverse=True))
    which is to say, the keep=True 2-tuple form.

    (Doesn't support any other arguments--maxsplit etc.)

    Forward splitting and reverse splitting *usually* produce the same
    results--but not always! See the docs:
        https://github.com/larryhastings/big#reverse
    """
    if not isinstance(separators, (list, tuple)):
        separators = [separators[i:i+1] for i in range(len(separators))]
    # assert separators
    if isinstance(s, bytes):
        empty = b''
    else:
        empty = ''
    # assert empty not in separators

    def as_pairs(segments):
        # same postlude as toy_multisplit: pair up the alternating
        # segments and separators into the keep=True 2-tuple form.
        segments.append(empty)
        return list(zip(segments[::2], segments[1::2]))

    # special-cased only one separator,
    # for PEDAL TO THE MEDAL HYPER-SPEED
    if len(separators) == 1:
        segments = []
        sep = separators[0]
        length = len(sep)
        while s:
            index = s.rfind(sep)
            if index == -1:
                segments.append(s)
                s = None
                break
            segments.append(s[index + length:])
            segments.append(sep)
            s = s[:index]
        if s is not None:
            segments.append(s)
        segments.reverse()
        return as_pairs(segments)

    # separators_by_length is a list of tuples:
    #    (length, bucket_of_separators_of_that_length)
    #
    # we add a bucket for every length, including 0.
    # (makes the algorithm easier.)
    longest_separator = max([len(sep) for sep in separators])
    separators_by_length = []
    for i in range(longest_separator, -1, -1):
        separators_by_length.append((-i, set()))

    # store each separator in the correct bucket,
    # for separators of that length.
    for sep in separators:
        separators_by_length[longest_separator - len(sep)][1].add(sep)

    # strip out empty buckets.
    # there may not be any separators in every length bucket.
    # for example, if your separators are
    #     ['X', 'Y', 'ABC', 'XYZ', ]
    # then you don't have any separators of length 2.
    # (also, we should never have any separators of length 0).
    s2 = [t for t in separators_by_length if t[1]]
    separators_by_length = s2

    # confirm: we shouldn't have any separators of length 0.
    # separators_by_length is sorted, with buckets containing
    # longer separators appearing earlier.  so the bucket with
    # the shortest separators is last.  the length of those
    # separators should be > 0.

    # assert separators_by_length[-1][0]

    segments = []
    word = []

    def flush_word():
        if not word:
            segments.append(empty)
            return
        word.reverse()
        segments.append(empty.join(word))
        word.clear()

    longest_separator_length = separators_by_length[0][0]
    while s:
        substring = s
        for negative_length, separators_set in separators_by_length:
            substring = substring[negative_length:]
            # print(f"substring={substring!r} separators_set={separators_set!r}")
            if substring in separators_set:
                flush_word()
                segments.append(substring)
                s = s[:negative_length]
                break
        else:
            # slice on a bytes object gives you back a bytes object.
            # s[0] on a bytes object gives you back an int.
            word.append(s[-1:])
            s = s[:-1]
    flush_word()

    segments.reverse()
    return as_pairs(segments)


def toy_multisplit_original(s, separators): # pragma: no cover
    """
    The original toy version of multisplit.
    I keep it around as a *third* implementation of multisplit,
    to make sure all three agree.  (The new toy_multisplit
    is usually faster though.)

    s is str or bytes.
    separators is str or bytes, or an iterable of str or bytes.

    Returns a list equivalent to
        list(big.multisplit(s, separators, keep=True, separate=True))
    which is to say, the keep=True 2-tuple form.

    (Doesn't support any other arguments--maxsplit etc.)
    """

    segments = []
    word = []

    if isinstance(s, bytes):
        empty = b''
    else:
        empty = ''

    if isinstance(separators, (str, bytes)):
        separators = (separators,)
    # assert empty not in separators

    def flush_word():
        segments.append(empty.join(word))
        word.clear()

    while s:
        longest_separator_length = 0
        longest_separator = None
        for sep in separators:
            length = len(sep)
            if s.startswith(sep) and (length > longest_separator_length):
                longest_separator = sep
                longest_separator_length = length
        if longest_separator:
            flush_word()
            segments.append(longest_separator)
            s = s[longest_separator_length:]
            continue
        word.append(s[:1])
        s = s[1:]
    flush_word()

    # same postlude as toy_multisplit: the original *algorithm* is
    # preserved for posterity, but its return value is packaged in
    # the keep=True 2-tuple form, like its siblings.
    segments.append(empty)
    return list(zip(segments[::2], segments[1::2]))


def test_whitespace_and_linebreaks():
    # ensure that big.whitespace and big.linebreaks
    # correctly matches the list of characters that
    # Python considers whitespace / line breaks.

    # the default versions should match the Python str versions
    assert big.whitespace == big.str_whitespace
    assert big.linebreaks == big.str_linebreaks

    # interrogate Python, to find out what *it*
    # thinks are whitespace characters.
    #
    # Python whitespace only considers individual
    # whitespace charcters, and doesn't include the
    # DOS end-of-line sequence '\r\n'.  so technically
    # what we're producing below is what big calls
    # the "without DOS" versions.
    observed_str_whitespace_without_crlf = set()
    observed_str_linebreaks_without_crlf = set()

    # skip over the surrogate pair code points, they don't represent glyphs.
    for i in itertools.chain(range(0, 0xd7ff), range(0xdfff, 2**16 + 2**20)):
        c = chr(i)
        if c.isspace():
            observed_str_whitespace_without_crlf.add(c)
            # all line-breaking characters are whitespace.
            # therefore, don't bother with the linebreaks test
            # unless this character passes the whitespace text.
            #
            # if c is a linebreak, then splitlines returns a list
            # containing only an empty string.  otherwise it returns
            # a list containing c.
            if not c.splitlines()[0]:
                observed_str_linebreaks_without_crlf.add(c)

    assert '\r' in observed_str_whitespace_without_crlf
    assert '\n' in observed_str_whitespace_without_crlf

    assert '\r' in observed_str_linebreaks_without_crlf
    assert '\n' in observed_str_linebreaks_without_crlf

    crlf = set(('\r\n',))
    observed_str_whitespace = observed_str_whitespace_without_crlf | crlf
    observed_str_linebreaks = observed_str_linebreaks_without_crlf | crlf

    assert set(big.str_whitespace) == observed_str_whitespace
    assert set(big.str_whitespace_without_crlf) == observed_str_whitespace_without_crlf
    assert set(big.str_linebreaks) == observed_str_linebreaks
    assert set(big.str_linebreaks_without_crlf) == observed_str_linebreaks_without_crlf

    assert set(big.whitespace) == set(observed_str_whitespace)
    assert set(big.whitespace_without_crlf) == set(observed_str_whitespace_without_crlf)
    assert set(big.linebreaks) == set(observed_str_linebreaks)
    assert set(big.linebreaks_without_crlf) == set(observed_str_linebreaks_without_crlf)

    # corrected--to match the Unicode standard, that is.  (unlike PYTHON!)
    ascii_record_separators = set('\x1c\x1d\x1e\x1f')
    corrected_str_whitespace_without_crlf = set(observed_str_whitespace_without_crlf) - ascii_record_separators
    corrected_str_whitespace = corrected_str_whitespace_without_crlf | crlf

    corrected_str_linebreaks_without_crlf = set(observed_str_linebreaks_without_crlf) - ascii_record_separators
    corrected_str_linebreaks = corrected_str_linebreaks_without_crlf | crlf

    assert set(big.unicode_whitespace) == corrected_str_whitespace
    assert set(big.unicode_whitespace_without_crlf) == corrected_str_whitespace_without_crlf
    assert set(big.unicode_linebreaks) == corrected_str_linebreaks
    assert set(big.unicode_linebreaks_without_crlf) == corrected_str_linebreaks_without_crlf

    # now do this all over again, but for bytes objects in ASCII.
    #
    # this is a different list than you'd get if you simply converted
    # observed_whitespace encoded to ASCII.  Python str thinks code points
    # '\x1c' through '\x1f' are whitespace... but Python bytes does not!
    # (Python also thinks '\x1c' through '\x1e' are line-breaks.)
    observed_bytes_whitespace_without_crlf = set()
    observed_bytes_linebreaks_without_crlf = set()
    for i in range(128):
        c = chr(i).encode('ascii')
        if c.isspace():
            observed_bytes_whitespace_without_crlf.add(c)
            if not c.splitlines()[0]:
                observed_bytes_linebreaks_without_crlf.add(c)

    bytes_crlf = set((b'\r\n',))
    observed_bytes_whitespace = observed_bytes_whitespace_without_crlf | bytes_crlf
    observed_bytes_linebreaks = observed_bytes_linebreaks_without_crlf | bytes_crlf
    assert set(big.bytes_whitespace) == observed_bytes_whitespace
    assert set(big.bytes_whitespace_without_crlf) == observed_bytes_whitespace_without_crlf
    assert set(big.bytes_linebreaks) == observed_bytes_linebreaks
    assert set(big.bytes_linebreaks_without_crlf) == observed_bytes_linebreaks_without_crlf

    def decode_byteses(o):
        return set(b.decode('ascii') for b in o)
    assert set(big.ascii_whitespace) == decode_byteses(observed_bytes_whitespace)
    assert set(big.ascii_whitespace_without_crlf) == decode_byteses(observed_bytes_whitespace_without_crlf)
    form_feed_and_vertical_tab = set('\f\v')
    assert set(big.ascii_linebreaks) == decode_byteses(observed_bytes_linebreaks) | form_feed_and_vertical_tab
    assert set(big.ascii_linebreaks_without_crlf) == decode_byteses(observed_bytes_linebreaks_without_crlf) | form_feed_and_vertical_tab

def test_reversed_re_finditer():
    # Cribbed off the test suite from the 'regex' package
    def test(pattern, string, expected, check_regex=True):
        pattern = c(pattern)
        string = c(string)
        expected = c(expected)
        got = finditer_group0(big.reversed_re_finditer(pattern, string))

        if check_regex and have_regex:
            # confirm first that we match regex's output
            if isinstance(pattern, re_Pattern):
                p = pattern.pattern
            else:
                p = pattern
            p = regex.compile(p, regex.REVERSE)
            regex_result = finditer_group0(p.finditer(string))
            # print(f"pattern={pattern!r} string={string!r} regex_result={regex_result!r} got={got!r}")
            assert regex_result == got

        assert expected == got

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
            check_regex = False
        else:
            # correct
            result = ('bar', 'foo', '')
            check_regex = True
        test(r'^|\w+', 'foo bar', result, check_regex=False)

        # regression test: the initial implementation of multisplit got this wrong.
        # it never truncated
        test(r'cdefghijk|bcd|fgh|jkl', 'abcdefghijklmnopqrstuvwxyz', ('jkl', 'fgh', 'bcd'))

def test_re_partition():
    def test_re_partition(s, pattern, count, expected):
        assert group0(big.re_partition(c(s), c(pattern), count)) == c(expected)

    def test_re_rpartition(s, pattern, count, expected):
        s = c(s)
        pattern = c(pattern)
        expected = c(expected)

        assert group0(big.re_rpartition(s, pattern, count)) == expected
        assert group0(big.re_partition(s, pattern, count, reverse=True)) == expected

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
            assert regex_result == big_result


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
            assert group0(result) == c(("Let's find the ", "number 89", " in this string"))
            match = result[1]
            assert match.group(0) == c("number 89")
            assert match.group(1) == c("89")

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
        # the rightmost overlapping matches all end with 'j',
        # and 'abcdefghij' is longest.
        test_re_rpartition('abcdefghijkl', '(abcdefghij|abcde|abcd|abc|ab|bc|cd|de|ef|fg|gh|hi|ij)', 1, ('', 'abcdefghij', 'kl') )

        # but if we add 'jk' to the list of separators,
        # that becomes the best match, because it's the rightmost.
        test_re_rpartition('abcdefghijkl', '(abcdefghij|abcde|abcd|abc|ab|bc|cd|de|ef|fg|gh|hi|ij|jk)', 1, ('abcdefghi', 'jk', 'l') )

        test_re_rpartition('abcdefgh', '(bcd|cdefgh|de)', 1, ('ab', 'cdefgh', '') )
        test_re_rpartition('abcdefgh', '(abcdef|efg|fb|b|c|d)', 4, ('a', 'b', '', 'c', '', 'd', '', 'efg', 'h') )
        test_re_rpartition('abcdefgh', '(abcdef|efg|ab|b|c|d)', 4, ('', 'ab', '', 'c', '', 'd', '', 'efg', 'h') )

    # do bytes vs str testing
    s = "abc123def456ghi"
    bytes_pattern = b"[0-9]+"
    with raises(TypeError):
        big.re_partition(s, bytes_pattern)
    with raises(TypeError):
        big.re_rpartition(s, bytes_pattern)

    bytes_pattern = re.compile(bytes_pattern)
    with raises(TypeError):
        big.re_partition(s, bytes_pattern)
    with raises(TypeError):
        big.re_rpartition(s, bytes_pattern)

    with raises(ValueError):
        big.re_partition('a:b', ':', -1)
    with raises(ValueError):
        big.re_partition(b'a:b', b':', -1)

    assert group0(big.re_partition(StrSubclass("a:b:c:d"), StrSubclass(":"))) == ("a", ":", "b:c:d")
    assert group0(big.re_partition(StrSubclass("a:b:c:d"), DifferentStrSubclass(":"))) == ("a", ":", "b:c:d")

    assert group0(big.re_partition(BytesSubclass(b"a:b:c:d"), BytesSubclass(b":"))) == (b"a", b":", b"b:c:d")
    assert group0(big.re_partition(BytesSubclass(b"a:b:c:d"), DifferentBytesSubclass(b":"))) == (b"a", b":", b"b:c:d")

    with raises(ValueError):
        big.re_partition('ab c de', ' ', count=-1)

    with raises(ValueError):
        big.re_rpartition('ab c de', ' ', count=-1)


def test_multistrip():
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
                    separators = big.bytes_whitespace
                elif original_separators == big.linebreaks:
                    separators = big.bytes_linebreaks
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

            assert big.multistrip(s, separators, left=False, right=False) == s
            assert big.multistrip(s, separators, left=False, right=True ) == s
            assert big.multistrip(s, separators, left=True,  right=False) == s
            assert big.multistrip(s, separators, left=True,  right=True ) == s

            ls = left + s
            assert big.multistrip(ls, separators, left=False, right=False) == ls
            assert big.multistrip(ls, separators, left=False, right=True ) == ls
            assert big.multistrip(ls, separators, left=True,  right=False) == s
            assert big.multistrip(ls, separators, left=True,  right=True ) == s

            sr = s + right
            assert big.multistrip(sr, separators, left=False, right=False) == sr
            assert big.multistrip(sr, separators, left=False, right=True ) == s
            assert big.multistrip(sr, separators, left=True,  right=False) == sr
            assert big.multistrip(sr, separators, left=True,  right=True ) == s

            lsr = left + s + right
            assert big.multistrip(lsr, separators, left=False, right=False) == lsr
            assert big.multistrip(lsr, separators, left=False, right=True ) == ls
            assert big.multistrip(lsr, separators, left=True,  right=False) == sr
            assert big.multistrip(lsr, separators, left=True,  right=True ) == s

    test_multistrip(" \t \n ", "abcde", " \n \t ", " \t\n")
    test_multistrip(" \t \n ", "abcde", " \n \t ", big.whitespace)
    test_multistrip("\r\n\n\r", "abcde", "\n\r\r\n", big.linebreaks)
    test_multistrip("\r\n\n\r", "abcde", "\n\r\r\n", big.whitespace)
    test_multistrip("xXXxxxXx", "iiiiiii", "yyYYYyyyyy", "xyXY")

    # test mixed subclasses of str and bytes
    assert big.multistrip(StrSubclass('  abcde  '), DifferentStrSubclass(' ')) == 'abcde'
    assert big.multistrip(BytesSubclass(b'  abcde  '), DifferentBytesSubclass(b' ')) == b'abcde'

    # this should be covered in the loop above,
    # but we'll explicitly check it anyway:
    # multistrip preserves string/bytes subclasses even
    # when it doesn't strip anything.
    assert big.multistrip(StrSubclass('abcde'), StrSubclass(' ')) == 'abcde'
    assert type(big.multistrip(StrSubclass('abcde'), StrSubclass(' '))) == StrSubclass
    assert big.multistrip(BytesSubclass(b'abcde'), BytesSubclass(b' ')) == b'abcde'
    assert type(big.multistrip(BytesSubclass(b'abcde'), BytesSubclass(b' '))) == BytesSubclass

    # regression: if separators is an iterator or generator,
    # multistrip should still validate it correctly and use it.
    assert big.multistrip('xaayx', iter(('x', 'y'))) == 'aa'
    assert big.multistrip(b'xaayx', iter((b'x', b'y'))) == b'aa'

    with raises(ValueError):
        big.multistrip('s', iter(()))
    with raises(ValueError):
        big.multistrip(b's', iter(()))

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
    assert big.multistrip(' x x ', (' x ',)) == 'x '

    # regression: multistrip didn't used to verify
    # that s was either str or bytes.
    with raises(TypeError):
        big.multistrip(3.1415)
    with raises(TypeError):
        big.multistrip(3.1415, 'abc')
    with raises(TypeError):
        big.multistrip(['a', 'b', 'c'])
    with raises(TypeError):
        big.multistrip([b'a', b'b', b'c'])
    with raises(TypeError):
        big.multistrip(['a', 'b', 'c'], 'a')
    with raises(TypeError):
        big.multistrip([b'a', b'b', b'c'], b'a')

    with raises(TypeError):
        big.multistrip('s', ['a', b'b', 'c'])
    with raises(TypeError):
        big.multistrip('s', ['a', 1234, 'c'])
    with raises(TypeError):
        big.multistrip(b's', [b'a', 'b', b'c'])
    with raises(TypeError):
        big.multistrip(b's', [b'a', 1234, b'c'])

    with raises(TypeError):
        big.multistrip('s', b'abc')
    with raises(TypeError):
        big.multistrip(b's', 'abc')

    with raises(TypeError):
        big.multistrip(StrSubclass(b'  abcde  '), BytesSubclass(b' '))

    with raises(ValueError):
        big.multistrip('s', '')
    with raises(ValueError):
        big.multistrip('s', [])
    with raises(ValueError):
        big.multistrip('s', [])
    with raises(ValueError):
        big.multistrip(b's', b'')
    with raises(ValueError):
        big.multistrip(b's', [])
    with raises(ValueError):
        big.multistrip(b's', ())


    with raises(ValueError):
        big.multistrip('abcde', ('c', ''))


def test_reversed_builtin_separators_cache():
    # the comment on _reversed_builtin_separators promises the
    # test suite validates the precomputed reversals.  now it
    # does: every cached value must be semantically equal to
    # actually reversing its key (order doesn't matter for
    # separators, so compare as sets), with no duplicates.
    from big.text import _reversed_builtin_separators, _multisplit_reversed
    for key, cached in _reversed_builtin_separators.items():
        computed = _multisplit_reversed(key)
        assert set(cached) == set(computed)
        assert len(cached) == len(set(cached))

    # and the table covers every builtin whitespace/linebreak
    # tuple, in both flavors.  (bytes_whitespace and
    # ascii_linebreaks used to be missing--reverse-mode
    # multisplit recomputed their reversals on every call.)
    for name in (
        'str_whitespace', 'unicode_whitespace', 'ascii_whitespace',
        'bytes_whitespace',
        'str_linebreaks', 'unicode_linebreaks', 'ascii_linebreaks',
        'bytes_linebreaks',
        ):
        assert getattr(big, name) in _reversed_builtin_separators, name
        assert getattr(big, name + '_without_crlf') in _reversed_builtin_separators, name

def test_multisplit():
    """
    The first of *seven* multisplit test suites.
    (multisplit has the biggest test suite in all of big.  it's called 105k times!)

    This test suite tests basic functionality and type safety.
    """

    def list_multisplit(*a, **kw): return list(big.multisplit(*a, **kw))

    for c in (unchanged, to_bytes):
        not_c = to_bytes if (c == unchanged) else unchanged
        assert list_multisplit(c('aaaXaaaYaaa'), c('abc'), strip=True ) == c(['X', 'Y'])
        assert list_multisplit(c('aaaXaaaYaaa'), c('abc'), strip=False) == c(['', 'X', 'Y', ''])
        assert list_multisplit(c('abcXbcaYcba'), c('abc'), strip=True ) == c(['X', 'Y'])
        assert list_multisplit(c('abcXbcaYcba'), c('abc'), strip=False) == c(['', 'X', 'Y', ''])

        assert list_multisplit(c(''), c('abcde'), maxsplit=None) == c([''])
        assert list_multisplit(c('abcde'), c('fghij')) == c(['abcde'])
        assert list_multisplit(c('abcde'), c('fghijc')) == c(['ab', 'de'])
        assert list_multisplit(c('1a2b3c4d5e6'), c('abcde')) == c(['1', '2', '3', '4', '5', '6'])

        assert list_multisplit(c('ab:cd,ef'),   c(':,'), strip=True ) == c(["ab", "cd", "ef"])
        assert list_multisplit(c('ab:cd,ef'),   c(':,'), strip=False) == c(["ab", "cd", "ef"])
        assert list_multisplit(c('ab:cd,ef:'),  c(':,'), strip=True ) == c(["ab", "cd", "ef"])
        assert list_multisplit(c('ab:cd,ef:'),  c(':,'), strip=False) == c(["ab", "cd", "ef", ""])
        assert list_multisplit(c(',ab:cd,ef:'), c(':,'), strip=True ) == c(["ab", "cd", "ef"])
        assert list_multisplit(c(',ab:cd,ef:'), c(':,'), strip=False) == c(["", "ab", "cd", "ef", ""])
        assert list_multisplit(c(':ab:cd,ef'),  c(':,'), strip=True ) == c(["ab", "cd", "ef"])
        assert list_multisplit(c(':ab:cd,ef'),  c(':,'), strip=False) == c(["", "ab", "cd", "ef"])
        assert list_multisplit(c('WWabXXcdYYabZZ'),   c(('ab', 'cd')), strip=True ) == c(['WW', 'XX', 'YY', 'ZZ'])
        assert list_multisplit(c('WWabXXcdYYabZZ'),   c(('ab', 'cd')), strip=False) == c(['WW', 'XX', 'YY', 'ZZ'])
        assert list_multisplit(c('WWabXXcdYYabZZab'), c(('ab', 'cd')), strip=True ) == c(['WW', 'XX', 'YY', 'ZZ'])
        assert list_multisplit(c('WWabXXcdYYabZZab'), c(('ab', 'cd')), strip=False) == c(['WW', 'XX', 'YY', 'ZZ', ''])
        assert list_multisplit(c('abWWabXXcdYYabZZ'), c(('ab', 'cd')), strip=True ) == c(['WW', 'XX', 'YY', 'ZZ'])
        assert list_multisplit(c('abWWabXXcdYYabZZ'), c(('ab', 'cd')), strip=False) == c(['','WW', 'XX', 'YY', 'ZZ'])
        assert list_multisplit(c('WWabXXcdYYabZZcd'), c(('ab', 'cd')), strip=True ) == c(['WW', 'XX', 'YY', 'ZZ'])
        assert list_multisplit(c('WWabXXcdYYabZZcd'), c(('ab', 'cd')), strip=False) == c(['WW', 'XX', 'YY', 'ZZ', ''])
        assert list_multisplit(c('XXabcdYY'), c(('a', 'abcd'))) == c(['XX', 'YY'])
        assert list_multisplit(c('XXabcdabcdYY'), c(('ab', 'cd'))) == c(['XX', 'YY'])
        assert list_multisplit(c('abcdXXabcdabcdYYabcd'), c(('ab', 'cd')), strip=True ) == c(['XX', 'YY'])
        assert list_multisplit(c('abcdXXabcdabcdYYabcd'), c(('ab', 'cd')), strip=False) == c(['', 'XX', 'YY', ''])
        assert list_multisplit(c('abcdXXabcdabcdYYabcd'), c(('ab', 'cd')), separate=True, strip=False) == c(['', '', 'XX', '', '', '', 'YY', '', ''])

        assert list_multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=0) == c(['xaxbxcxdxex'])
        assert list_multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=1) == c(['x', 'xbxcxdxex'])
        assert list_multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=2) == c(['x', 'x', 'xcxdxex'])
        assert list_multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=3) == c(['x', 'x', 'x', 'xdxex'])
        assert list_multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=4) == c(['x', 'x', 'x', 'x', 'xex'])
        assert list_multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=5) == c(['x', 'x', 'x', 'x', 'x', 'x'])
        assert list_multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=6) == c(['x', 'x', 'x', 'x', 'x', 'x'])

        # test: greedy separators
        assert list_multisplit(c('-abcde-abc-a-abc-abcde-'),
            c([
                'a', 'ab', 'abc', 'abcd', 'abcde',
                'b', 'bc', 'bcd', 'bcde',
                'c', 'cd', 'cde',
                'd', 'de',
                'e'
            ])) == c(['-', '-', '-', '-', '-', '-'])
        # greedy works the same when reverse=True, even if it maybe feels a little strange
        assert list_multisplit(c('-abcde-abc-a-abc-abcde-'),
            c([
                'a', 'ab', 'abc', 'abcd', 'abcde',
                'b', 'bc', 'bcd', 'bcde',
                'c', 'cd', 'cde',
                'd', 'de',
                'e'
            ]), reverse=True) == c(['-', '-', '-', '-', '-', '-'])

        # regression test: *YES*, if the string you're splitting ends with a separator,
        # and keep=big.AS_PAIRS, the result ends with a tuple containing two empty strings.
        assert list_multisplit(c('\na\nb\nc\n'), c(('\n',)), keep=big.AS_PAIRS, strip=False) == c([ ('', '\n'), ('a', '\n'), ('b', '\n'), ('c', '\n'), ('', '') ])

        # test: progressive strip
        assert list_multisplit(c('   a b c   '), c((' ',)), maxsplit=1, strip=big.PROGRESSIVE) == c([ 'a', 'b c   '])

        # regression: PROGRESSIVE + maxsplit=None should behave like
        # unlimited splitting in both directions.
        assert list_multisplit(c('^apple^banana_cookie_'), c(('^', '_')), maxsplit=None, strip=big.PROGRESSIVE) == c(['apple', 'banana', 'cookie'])
        assert list_multisplit(c('^apple^banana_cookie_'), c(('^', '_')), maxsplit=None, strip=big.PROGRESSIVE, reverse=True) == c(['apple', 'banana', 'cookie'])

        # regression test: when there are *overlapping* separators,
        # multisplit prefers the leftmost one(s), but passing in
        # reverse=True makes it prefer the *rightmost* ones.
        assert list_multisplit(c(' x x '), c((' x ',)), keep=big.ALTERNATING) == c([ '', ' x ', 'x '])
        assert list_multisplit(c(' x x '), c((' x ',)), keep=big.ALTERNATING, reverse=True) == c([ ' x', ' x ', ''])
        # also use this opportunity to test toy_multisplit etc
        assert list_multisplit(c(' x x '), c((' x ',)), keep=big.ALTERNATING, separate=True) == c([ '', ' x ', 'x '])
        assert list_multisplit(c(' x x '), c((' x ',)), keep=big.ALTERNATING, separate=True, reverse=True) == c([ ' x', ' x ', ''])
        assert toy_multisplit(c(' x x '), c((' x ',))) == c([ ('', ' x '), ('x ', '')])
        assert toy_multisplit_original(c(' x x '), c((' x ',))) == c([ ('', ' x '), ('x ', '')])
        assert toy_multisplit_reverse(c(' x x '), c((' x ',))) == c([ (' x', ' x '), ('', '')])

        # ''.split() returns an empty list.
        # multisplit intentionally does *not* reproduce this ill-concieved behavior.
        # multisplit(s, list-of-separators-that-don't-appear-in-s) always returns [s].
        # (or, rather, an iterator that yields only s).
        assert list_multisplit(c('')) == c([''])
        assert list_multisplit(c(''), reverse=True) == c([''])
        # similarly, '    '.split() also returns an empty list,
        # and multisplit does not.
        assert list_multisplit(c('   ')) == c(['', ''])
        assert list_multisplit(c('   '), reverse=True) == c(['', ''])
        assert list_multisplit(c('   '), strip=True) == c([''])
        assert list_multisplit(c('   '), strip=True, reverse=True) == c([''])

        # regression: if separators is an iterator or generator,
        # multisplit should materialize it before validating and using it.
        assert list_multisplit(c('a,b'), iter((c(','),))) == c(['a', 'b'])
        assert list_multisplit(c('a,b'), iter((c(','),)), reverse=True) == c(['a', 'b'])
        with raises(ValueError):
            list_multisplit(c('s'), iter(()))

        class Indexable:
            def __init__(self, value):
                self.value = value
            def __index__(self):
                return self.value

        assert list_multisplit(c('xaxbxc'), c('abc'), maxsplit=Indexable(2)) == c(['x', 'x', 'xc'])

        with raises(TypeError):
            list_multisplit(c('s'), 3.1415)
        with raises(ValueError):
            list_multisplit(c('s'), [])
        with raises(ValueError):
            list_multisplit(c('s'), ())
        with raises(TypeError):
            list_multisplit(c('s'), not_c(''))
        with raises(TypeError):
            list_multisplit(c('s'), [c('a'), not_c('b'), c('c')])
        with raises(TypeError):
            list_multisplit(c('s'), [c('a'), 1234, c('c')])

    for str_type_1 in (str, StrSubclass, DifferentStrSubclass):
        for str_type_2 in (str, StrSubclass, DifferentStrSubclass):
            assert list_multisplit(str_type_1('abcde'), str_type_2('c')) == ['ab', 'de']

    for bytes_type_1 in (bytes, BytesSubclass, DifferentBytesSubclass):
        for bytes_type_2 in (bytes, BytesSubclass, DifferentBytesSubclass):
            assert list_multisplit(bytes_type_1(b'abcde'), bytes_type_2(b'c')) == [b'ab', b'de']

    for str_type in (str, StrSubclass, DifferentStrSubclass):
        for bytes_type in (bytes, BytesSubclass, DifferentBytesSubclass):
            with raises(TypeError):
                list_multisplit(str_type('s'), bytes_type(b'abc'))
            with raises(TypeError):
                list_multisplit(bytes_type(b's'), str_type('abc'))

            # just making sure!
            with raises(TypeError):
                list_multisplit(str_type('s'), [str_type('a'), bytes_type(b'b'), str_type('c')])
            with raises(TypeError):
                list_multisplit(bytes_type(b's'), [bytes_type(b'a'), str_type('b'), bytes_type(b'c')])

    # regression: multisplit didn't used to verify
    # that s was either str or bytes.
    with raises(TypeError):
        list_multisplit(3.1415)
    with raises(TypeError):
        list_multisplit(3.1415, 'abc')
    with raises(TypeError):
        list_multisplit(['a', 'b', 'c'])
    with raises(TypeError):
        list_multisplit(['a', 'b', 'c'], 'a')
    with raises(TypeError):
        list_multisplit('abcde', ('b', 'd', ''))

    # regression: if reverse=True and separators was not hashable,
    # multisplit would crash.  fixed in 0.6.17.
    assert list_multisplit('axbyczd', ['x', 'y', 'z'], maxsplit=2, reverse=True) == ['axb', 'c', 'd']
    assert list_multisplit(b'axbyczd', [b'x', b'y', b'z'], maxsplit=2, reverse=True) == [b'axb', b'c', b'd']

    # test that multisplit honors string subclasses
    SS = StrSubclass
    for s in big.multisplit(SS('1a2b3c4d5e6'), SS('abcde')):
        assert isinstance(s, SS)

    for s in big.multisplit(SS('abcdXXabcdabcdYYabcd'), (SS('ab'), SS('cd')), separate=True, strip=False):
        assert isinstance(s, SS)

    for s, sep in big.multisplit(SS('abcdXXabcdabcdYYabcd'), (SS('ab'), SS('cd')), separate=True, strip=False, keep=big.AS_PAIRS):
        assert isinstance(s, SS)
        assert isinstance(sep, SS)

def test_reimplemented_multisplit():
    """
    The second of *seven* multisplit test suites.
    (multisplit has the biggest test suite in all of big.  it's called 105k times!)

    This tests that multisplit(reverse=False), toy_multisplit, and
    toy_multisplit_original all agree, and that
    multisplit(reverse=True) and toy_multisplit_reverse also agree.

    (In a later test suite, we use the toy_multisplit*
    functions to predict the output multisplit should give us.)
    """
    want_prints = False
    # want_prints = True

    if want_prints: # pragma: no cover
        import time
        if hasattr(time, 'perf_counter_ns'):
            time_perf_counter_ns = time.perf_counter_ns
        else:
            def time_perf_counter_ns():
                return int(time.perf_counter() * 1000000000)

    def t(s, seps, expected, reverse_expected=None):
        reverse_expected = reverse_expected or expected
        for which in ('str', 'bytes'):
            # call sites pass readable flat literals (which the
            # bytes conversion at the bottom of this loop relies
            # on); the toys, and multisplit with keep=True,
            # speak 2-tuples.
            expected_pairs = pair_up(expected)
            reverse_expected_pairs = pair_up(reverse_expected)
            if want_prints: # pragma: no cover
                times = {}
                print(f"{which}:")
                print(f"       s={s!r}")
                print(f"    seps={seps!r}")
                print(f"  result={expected!r}")
                if reverse_expected != expected:
                    print(f"  reverse result={reverse_expected!r}")
                start = time_perf_counter_ns()
            result = toy_multisplit_original(s, seps)
            if want_prints: # pragma: no cover
                end = time_perf_counter_ns()
                delta = str(end - start)
                times[f'toy multisplit original ({which})'] = delta
                # print(f'  toy_multisplit_original(s={s!r}, seps={seps!r}) -> {result!r}')
            assert result == expected_pairs, f"toy_multisplit_original:\n  result={result!r}\n!=\nexpected={expected_pairs!r}"

            if want_prints: # pragma: no cover
                start = time_perf_counter_ns()
            result = toy_multisplit(s, seps)
            if want_prints: # pragma: no cover
                end = time_perf_counter_ns()
                delta = str(end - start)
                times[f'toy multisplit ({which})'] = delta
                # print(f'  toy_multisplit(s={s!r}, seps={seps!r}) -> {result!r}')
            assert result == expected_pairs, f"toy_multisplit:\n  result={result!r}\n!=\nexpected={expected_pairs!r}"

            if want_prints: # pragma: no cover
                start = time_perf_counter_ns()
            result = list(big.multisplit(s, seps, keep=True, separate=True))
            if want_prints: # pragma: no cover
                end = time_perf_counter_ns()
                delta = str(end - start)
                times[f'multisplit ({which})'] = delta
                # print(f'multisplit(s={s!r}, seps={seps!r}, keep=True, separate=True) -> {result!r}')
            assert result == expected_pairs, f"multisplit:\n  result={result!r}\n!=\nexpected={expected_pairs!r}"

            if want_prints: # pragma: no cover
                start = time_perf_counter_ns()
            result = toy_multisplit_reverse(s, seps)
            if want_prints: # pragma: no cover
                end = time_perf_counter_ns()
                delta = str(end - start)
                times[f'toy reverse multisplit ({which})'] = delta
                # print(f'  toy_multisplit(s={s!r}, seps={seps!r}) -> {result!r}')
            assert result == reverse_expected_pairs, f"toy_multisplit_reverse:\n  result={result!r}\n!=\nreverse_expected={reverse_expected_pairs!r}"

            if want_prints: # pragma: no cover
                start = time_perf_counter_ns()
            result = list(big.multisplit(s, seps, keep=True, separate=True, reverse=True))
            if want_prints: # pragma: no cover
                end = time_perf_counter_ns()
                delta = str(end - start)
                times[f'reverse multisplit ({which})'] = delta
                # print(f'multisplit(s={s!r}, seps={seps!r}, keep=True, separate=True, reverse=True) -> {result!r}')
            assert result == reverse_expected_pairs, f"multisplit:\n  result={result!r}\n!=\reverse_expected={reverse_expected_pairs!r}"

            if want_prints: # pragma: no cover
                max_name_length = max(len(key) for key in times)
                max_time_length = max(len(str(t)) for t in times.values())

                for name, t in times.items():
                    print(f"{name:>{max_name_length}}: {t:>{max_time_length}}ns")
                print()
                print()

            if which == 'bytes':
                break

            s = s.encode('ascii')
            if seps == big.whitespace:
                seps = big.bytes_whitespace
            else:
                seps = [b.encode('ascii') for b in seps]
            expected = [b.encode('ascii') for b in expected]
            reverse_expected = [b.encode('ascii') for b in reverse_expected]


    t('aXbXcXd', 'X', list('aXbXcXd'))
    t(' a b c ', ' ', ['', ' ', 'a', ' ', 'b', ' ', 'c', ' ', ''])
    t('XXaXbYcXdX', ('X', 'Y',), ['', 'X', '', 'X', 'a', 'X', 'b', 'Y', 'c', 'X', 'd', 'X', ''])
    t('XYabcXbdefYghiXjkl', ('X', 'Y',), ['', 'X', '', 'Y', 'abc', 'X', 'bdef', 'Y', 'ghi', 'X', 'jkl'])
    t('XYabcXbdefYghiXjkXYZl', ('XY', 'X', 'XYZ', 'Y', 'Z'), ['', 'XY', 'abc', 'X', 'bdef', 'Y', 'ghi', 'X', 'jk', 'XYZ', 'l'])
    t('XYabcXbdefYZghiXjkXYZlY', ('XY', 'X', 'XYZ', 'Y', 'Z'), ['', 'XY', 'abc', 'X', 'bdef', 'Y', '', 'Z', 'ghi', 'X', 'jk', 'XYZ', 'l', 'Y', ''])
    t('qXYZXYXXYXYZabcXb', ('XY', 'X', 'XYZ', 'Y', 'Z'), ['q', 'XYZ', '', 'XY', '', 'X', '', 'XY', '', 'XYZ', 'abc', 'X', 'b'])

    t('  \t abc de  fgh \n\tijk    lm  ', big.whitespace,
        ['', ' ', '', ' ', '', '\t', '', ' ', 'abc', ' ', 'de', ' ', '', ' ', 'fgh', ' ', '', '\n', '', '\t', 'ijk', ' ', '', ' ', '', ' ', '', ' ', 'lm', ' ', '', ' ', ''])

    # overlapping separators
    t('xa0bx', ('a0', '0b'), ['x', 'a0', 'bx'], reverse_expected=['xa', '0b', 'x'] )


def test_advanced_multisplit():
    """
    The third of *seven* multisplit test suites.
    (multisplit has the biggest test suite in all of big.  it's called 105k times!)

    This test suite tests some funny boundary cases.
    """
    toy_compatible_kwargs = { 'keep': big.ALTERNATING, 'separate': True }
    toy_reverse_compatible_kwargs = { 'keep': big.ALTERNATING, 'separate': True, 'reverse': True }

    def simple_test_multisplit(s, separators, expected, **kwargs):
        for _ in range(2):
            if _ == 1:
                # encode!
                s = s.encode('ascii')
                if separators == big.whitespace:
                    separators = big.bytes_whitespace
                elif separators == big.linebreaks:
                    separators = big.bytes_linebreaks
                else:
                    separators = to_bytes(separators)
                expected = to_bytes(expected)
            # print()
            # print(f"s={s} expected={expected}\nseparators={separators}")
            result = list(big.multisplit(s, separators, **kwargs))
            assert result == expected

            if kwargs == toy_compatible_kwargs:
                # the flat ALTERNATING expected, paired up,
                # is exactly what the toys return.
                toy_expected = pair_up(expected)
                result = toy_multisplit_original(s, separators)
                assert result == toy_expected
                result = toy_multisplit(s, separators)
                assert result == toy_expected
            elif kwargs == toy_reverse_compatible_kwargs:
                result = toy_multisplit_reverse(s, separators)
                assert result == pair_up(expected)

    for i in range(8):
        spaces = " " * i
        simple_test_multisplit(spaces + "a  b  c" + spaces, (" ",), ['a', 'b', 'c'], strip=True)
        simple_test_multisplit(spaces + "a  b  c" + spaces, big.whitespace, ['a', 'b', 'c'], strip=True)


    simple_test_multisplit("first line!\nsecond line.\nthird line.", big.linebreaks,
        ["first line!", "second line.", "third line."])
    simple_test_multisplit("first line!\nsecond line.\nthird line.\n", big.linebreaks,
        [("first line!", "\n"), ("second line.", "\n"), ("third line.", "")], keep=True, strip=True)
    simple_test_multisplit("first line!\nsecond line.\nthird line.\n", big.linebreaks,
        [("first line!", "\n"), ("second line.", "\n"), ("third line.", "\n"), ("", "")], keep=True, strip=False)
    simple_test_multisplit("first line!\n\nsecond line.\n\n\nthird line.", big.linebreaks,
        ["first line!", '', "second line.", '', '', "third line."], separate=True)
    simple_test_multisplit("first line!\n\nsecond line.\n\n\nthird line.", big.linebreaks,
        [("first line!", "\n"), ("", "\n"), ("second line.", "\n"), ("", "\n"), ("", "\n"), ("third line.", "")], keep=True, separate=True)
    simple_test_multisplit("first line!\n\nsecond line.\n\n\nthird line.", big.linebreaks,
        ["first line!", "\n", '', '\n', "second line.", "\n", '', '\n', '', '\n', "third line."], keep=big.ALTERNATING, separate=True)
    simple_test_multisplit("first line!\n\nsecond line.\n\n\nthird line.", big.linebreaks,
        ["first line!", "\n", '', '\n', "second line.", "\n", '', '\n', '', '\n', "third line."], keep=big.ALTERNATING, separate=True, reverse=True)


    simple_test_multisplit("a,b,,,c", ",", ['a', 'b', '', '', 'c'], separate=True)

    simple_test_multisplit("a,b,,,c", (",",), ['a', 'b', ',,c'], separate=True, maxsplit=2)

    simple_test_multisplit("a,b,,,c", (",",), ['a,b,', '', 'c'], separate=True, maxsplit=2, reverse=True)

    simple_test_multisplit("a,b,,,c", ",", ['a', ',', 'b', ',', '', ',', '', ',', 'c'], keep=big.ALTERNATING, separate=True)
    simple_test_multisplit("a,b,,,c", ",", ['a', ',', 'b', ',', '', ',', '', ',', 'c'], keep=big.ALTERNATING, separate=True, reverse=True)

def test_multisplit_keep_deprecations():
    # 0.14 changed keep=True to mean the 2-tuple form (what
    # 0.13 called AS_PAIRS).  the old constants still work,
    # deprecated, until at least August 2027.
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        as_pairs = list(big.multisplit('a b', keep=big.AS_PAIRS))
        alternating = list(big.multisplit('a b', keep=big.ALTERNATING))
        joined = list(big.multisplit('a b', keep=big.JOINED))
    assert len(w) == 3
    for warning in w:
        assert warning.category is DeprecationWarning
    assert 'keep=AS_PAIRS' in str(w[0].message)
    assert 'keep=ALTERNATING' in str(w[1].message)
    assert 'keep=JOINED' in str(w[2].message)

    # the deprecated forms still behave correctly.
    # JOINED is the old (0.13) meaning of keep=True.
    assert as_pairs == [('a', ' '), ('b', '')]
    assert alternating == ['a', ' ', 'b']
    assert joined == ['a ', 'b']

    # keep=True and keep=False are silent, and True means pairs
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        pairs = list(big.multisplit('a b', keep=True))
        discarded = list(big.multisplit('a b'))
    assert [x for x in w if issubclass(x.category, DeprecationWarning)] == []
    assert pairs == [('a', ' '), ('b', '')]
    assert discarded == ['a', 'b']

    # the documented migration recipes: old keep=True (now
    # named JOINED) is a+b over the pairs, old ALTERNATING is
    # the flattened pairs minus the always-empty trailing
    # separator.
    assert [a + b for a, b in pairs] == joined
    flattened = list(itertools.chain.from_iterable(pairs))
    assert flattened[:-1] == alternating
    assert flattened[-1] == ''

    # big's own machinery never trips the keep deprecation.
    # (lines() emits its own pipeline deprecation--that one's
    # deliberate, and tested in test_lines_deprecation_warning--
    # so we filter to multisplit's messages here.)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        big.multipartition('aXbYc', ('X', 'Y'), count=2)
        big.format_map('{a}', {'a': 1})
        list(big.split_delimiters('f(x)'))
        list(big.split_quoted_strings("a 'b' c"))
        list(big.lines("a\nb\n"))
        string("a\nb\n").splitlines(True)
    keep_warnings = [x for x in w
        if issubclass(x.category, DeprecationWarning)
        and "multisplit" in str(x.message)]
    assert keep_warnings == []

def test_regression_unhashable_separator_iterables():
    assert big.multistrip('xyhelloxy', ['xy']) == 'hello'
    assert list(big.multisplit('a,b,c', [','])) == ['a', 'b', 'c']
    assert big.multipartition('a,b,c', [','], 1) == ('a', ',', 'b,c')
    assert list(big.multisplit(b'a,b,c', [b','])) == [b'a', b'b', b'c']

def test_reimplemented_str_split():
    """
    The fourth of *seven* multisplit test suites.
    (multisplit has the biggest test suite in all of big.  it's called 105k times!)

    This test suite reimplements str.split and str.rsplit
    using multisplit, and confirms that the reimplentations
    and the originals produce identical output.
    """
    def _multisplit_to_split(s, sep, maxsplit, reverse):
        separate = sep != None
        if separate:
            strip = False
        else:
            sep = big.bytes_whitespace if isinstance(s, bytes) else big.whitespace
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

            for sep2 in (sep, None):
                a = s.split(sep2, maxsplit)
                b = str_split(s, sep2, maxsplit)
                assert a == b, f"reimplemented str_split fails: {s!r}.split({sep2!r}, {maxsplit}) == {a}, str_split version gave us {b}"

                if (maxsplit == -1) and sep2:
                    # the toys' 2-tuples pair each segment with its
                    # subsequent separator; str.split's output is
                    # exactly the segments.
                    b = [segment for segment, separator in toy_multisplit(s, sep2)]
                    assert a == b, f"toy_multisplit fails: {s!r}.split({sep2!r}, {maxsplit}) == {a}, toy_multisplit gave us {b}"
                    b = [segment for segment, separator in toy_multisplit_original(s, sep2)]
                    assert a == b, f"toy_multisplit_original fails: {s!r}.split({sep2!r}, {maxsplit}) == {a}, toy_multisplit_original gave us {b}"

                a = s.rsplit(sep2, maxsplit)
                b = str_rsplit(s, sep2, maxsplit)
                assert a == b, f"reimplemented str_rsplit fails: {s!r}.rsplit({sep2!r}, {maxsplit}) == {a}, str_split version gave us {b}"

                if (maxsplit == -1) and sep2:
                    b = [segment for segment, separator in toy_multisplit_original(s, sep2)]
                    assert a == b, f"toy_multisplit_original fails: {s!r}.split({sep2!r}, {maxsplit}) == {a}, toy_multisplit_original gave us {b}"


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

    assert str_split('') == []
    test('')

    # test greedy behavior.
    # str.split isn't greedy, but multisplit is.
    # (well, str.split *might* be? there's no way to call it
    # that demonstrates whether or not it's greedy.)
    # anyway, ensure multisplit's greedy behavior doesn't
    # mess up our emulation of str.split.
    test('a\rb\nc\r\nd')

    test('a b c ', ' ')

def test_reimplemented_str_splitlines():
    """
    The fifth of *seven* multisplit test suites.
    (multisplit has the biggest test suite in all of big.  it's called 105k times!)

    This test suite reimplements str.splitlines
    using multisplit, and confirms that the original and
    the reimplementation produce identical output.
    """
    def str_splitlines(s, keepends=False):
        linebreaks = big.bytes_linebreaks if isinstance(s, bytes) else big.linebreaks
        if keepends:
            # keep=True yields (line, end) 2-tuples;
            # keepends means gluing each end back on.
            l = [line + end for line, end in big.multisplit(s, linebreaks,
                keep=True, separate=True, strip=False)]
        else:
            l = list(big.multisplit(s, linebreaks,
                keep=False, separate=True, strip=False))
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
                assert a == b, f"reimplemented str_splitlines fails: {s!r}.splitlines({keepends}) == {a}, multisplit gave us {b}"

                if s and (not keepends):
                    def toy_splitlines(s, fn):
                        linebreaks = big.bytes_linebreaks if isinstance(s, bytes) else big.linebreaks
                        # the toys speak 2-tuples; keepends=False
                        # means we want just the segments.
                        l = [line for line, end in fn(s, linebreaks)]
                        if l and not l[-1]:
                            # yes, "".splitlines() returns an empty list
                            l.pop()
                        return l
                    b = toy_splitlines(s, toy_multisplit)
                    assert a == b, f"toy_multisplit fails: {s!r}.splitlines({keepends}) == {a}, toy_multisplit gave us {b}"
                    b = toy_splitlines(s, toy_multisplit_original)
                    assert a == b, f"toy_multisplit_original fails: {s!r}.splitlines({keepends}) == {a}, toy_multisplit_original gave us {b}"

    test('')
    test('\n')
    test('One line')
    test('One line\n')
    test('Two lines\nTwo lines')
    test('Two lines\nTwo lines\n')
    test('Two lines\nTwo lines\n\n\n')
    test('\nTwo lines\nTwo lines\n\n\n')
    test('\nTwo lines\n\nTwo lines')

def test_reimplemented_str_partition():
    """
    The sixth of *seven* multisplit test suites.
    (multisplit has the biggest test suite in all of big.  it's called 105k times!)

    This test suite reimplements str.partition and str.rpartition
    using multisplit, and confirms that the originals and the
    reimplementations produce identical output.
    """
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
            assert a == b, f"reimplemented str_partition fails: {s!r}.partition({sep!r}) == {a}, multisplit gave us {b}"

            # while we're at it, throw in some multipartition tests here too
            b = big.multipartition(s, (sep,))
            assert a == b, f"multipartition fails: {s!r}.partition({sep!r}) == {a}, multipartition gave us {b}"

            a = s.rpartition(sep)
            b = str_rpartition(s, sep)
            assert a == b, f"reimplemented str_rpartition fails: {s!r}.rpartition({sep!r}) == {a}, multisplit gave us {b}"

            b = big.multipartition(s, (sep,), reverse=True)
            assert a == b, f"multipartition(reverse=True) fails: {s!r}.rpartition({sep!r}) == {a}, multipartition(reverse=True) gave us {b}"

            b = big.multirpartition(s, (sep,))
            assert a == b, f"multirpartition fails: {s!r}.rpartition({sep!r}) == {a}, multirpartition gave us {b}"

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

    with raises(ValueError):
        " a b c ".partition('')
    with raises(ValueError):
        str_partition(" a b c ", '')

    with raises(ValueError):
        " a b c ".rpartition('')
    with raises(ValueError):
        str_rpartition(" a b c ", '')


def test_multisplit_exhaustively():
    """
    The seventh of *seven* multisplit test suites.
    (multisplit has the biggest test suite in all of big.  it's called 105k times!)

    This is the big one.  The final boss.
    It's gigantic, exhaustive, and (comparatively) slow.

    multisplit_tester() accepts a string to split and a set of separators.
    It splits the string using toy_multisplit and toy_multisplit_reverse,
    then calls multisplit using those same two arguments, adding a
    *bewildering* combination of test inputs:
            * as strings and encoded to bytes (ascii)
            * with and without the leading left separator(s)
            * with and without the trailing right separator(s)
            * with every combination of every value of
                * keep
                * maxsplit (all values that produce different results, plus a couple extra Just In Case)
                * reverse
                * separate
                * strip

    This tests *every* combination of keyword arguments that will
    produce distinct output.

    multisplit_tester() then independently computes what the output
    *should* be, given those inputs, and confirms that multisplit()
    indeed returned that output.
    """

    def multisplit_tester(s, separators=None):
        """
        s is the test string you want split.
        (must be str; multisplit_tester will convert it
        to bytes too, don't worry.)

        I *think* s has to start and end with one or more
        separators... sorry, it's been a minute since
        I wrote it, and I forgot to document that fact
        (if true).

        separators is the list of separators.

        tests Every. Possible. Unique. Permutation. of inputs to multisplit(),
        based on the segments you pass in.  this includes
            * as strings and encoded to bytes (ascii)
            * with and without the leading left separator(s)
            * with and without the trailing right separator(s)
            * with every combination of every value of
                * keep
                * maxsplit (all values that produce different results, plus a couple extra Just In Case)
                * reverse
                * separate
                * strip

        p.s it's a little slow!  but gee whiz it's doing a lot.
        """

        want_prints = False
        # want_prints = True

        if want_prints: # pragma: no cover
            print("_" * 69)
            print()
            print("test exhaustively")
            print("_" * 69)

        original_separators = separators
        original_s = s

        separators = original_separators if (original_separators is not None) else big.whitespace

        # split s by hand into alternating separator and non-separator strings.
        #
        # the toys return the keep=True 2-tuple form; flatten it back
        # into the alternating form this test is built on.  note that
        # the flattened form may contain empty strings--empty segments
        # between adjacent separators, and the always-empty trailing
        # separator.  we don't want those.  so, throw 'em away.
        #
        # split both forwards and backwards, in case there are overlapping separators.
        forwards_segments = [x for pair in toy_multisplit(s, separators) for x in pair if x]
        reverse_segments = [x for pair in toy_multisplit_reverse(s, separators) for x in pair if x]

        for reverse in (False, True):
            segments = reverse_segments if reverse else forwards_segments
            segments = segments.copy()

            # Don't worry, we'll pass the separators argument
            # in to multisplit *exactly* how you passed it in
            # to multisplit_tester.
            default_separators = big.bytes_whitespace if isinstance(original_s, bytes) else big.whitespace
            separators = original_separators if (original_separators is not None) else default_separators
            separators_as_passed_in = original_separators

            separators_set = set(big.text._iterate_over_bytes(separators))
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
                assert (not split) or (split[-1] in separators_set), f"split={split} last element should be in separators_set={separators_set}"
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

            # invariant: if you join leading, splits, and trailing
            # together into one big string, it is our original input string.
            # that must never change.
            #
            # let's confirm it's true!
            t = leading.copy()
            for o in splits:
                t.extend(o)
            t.extend(trailing)
            reconstituted_s = "".join(t)
            assert reconstituted_s == original_s

            originals = leading, splits, trailing

            for as_bytes in (False, True):
                if want_prints: # pragma: no cover
                    print(f"[loop 0] as_bytes={as_bytes}")
                if as_bytes:
                    leading, splits, trailing = copy.deepcopy(originals)
                    leading = big.encode_strings(leading)
                    splits = [big.encode_strings(split) for split in splits]
                    trailing = big.encode_strings(trailing)
                    originals = [leading, splits, trailing]
                    empty = b''
                    if separators_as_passed_in is None:
                        separators_set = set(big.bytes_whitespace)
                    else:
                        if isinstance(separators, str):
                            separators = separators_as_passed_in = separators.encode('ascii')
                            separators_set = set(big.text._iterate_over_bytes(separators))
                        else:
                            separators = separators_as_passed_in = big.encode_strings(separators)
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

                                # expected can be a whole weird mix of things at this point.
                                # let's sanity-check it, that every element either
                                #     * contains *only* separators, or
                                #     * doesn't contain *any* separators.
                                #
                                # we do that by using toy_multisplit to split every segment.
                                # every segment should either contain only separators
                                # (but maybe more than one), or no separators.
                                # which means when toy_multisplit splits it, either we get back
                                #    * one element which contains no separators, or
                                #    * one element which is in separators, or
                                #    * multiple elements which are all in separators.
                                #
                                # if we only get one element back, we can't do any further
                                # testing, because either it's in separators or it isn't,
                                # we can't tell anything further.
                                #
                                # if we get back multiple elements, they must all be in
                                # separators.
                                for e in expected:
                                    if not e:
                                        assert e in ('', b'')
                                        continue
                                    # flatten the toy's 2-tuples back into the
                                    # alternating form this check reasons about
                                    _segments = [x for pair in toy_multisplit(e, list(separators_set)) for x in pair if x]
                                    if len(_segments) == 1:
                                        assert _segments[0] == e
                                        continue
                                    for _segment in _segments:
                                        assert _segment in separators_set

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
                                    for keep in (False, True, big.ALTERNATING, big.AS_PAIRS, big.JOINED):
                                        expected = list(expected_original2)
                                        if want_prints: # pragma: no cover
                                            print(f"[loop 7] keep={keep} // expected={expected}")
                                        if not keep:
                                            expected = [s.replace(non_sep_marker, empty) for i, s in enumerate(expected) if i % 2 == 0]
                                        elif keep == big.ALTERNATING:
                                            # strip non_sep_marker hack
                                            expected = [s.replace(non_sep_marker, empty) for s in expected]
                                        elif keep == big.JOINED:
                                            # the old (0.13) keep=True form:
                                            # separators appended to their
                                            # preceding strings.
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
                                        else:
                                            # keep=True, and its deprecated alias
                                            # AS_PAIRS, both mean the 2-tuple form.
                                            # (the old 0.13 keep=True form--separators
                                            # appended to their preceding strings--is
                                            # gone from multisplit, and from this test.)
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

                                        result = list(big.multisplit(input_string, separators_as_passed_in,
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
                                        assert result == expected, f"as_bytes={as_bytes} use_leading={use_leading} use_trailing={use_trailing} multisplit(input_string={input_string}, separators={printable_separators(separators)}, keep={keep}, separate={separate}, strip={strip}, reverse={reverse}, maxsplit={maxsplit})"

    test_string = ' a b c '

    multisplit_tester(
        test_string,
        ' ',
        )

    multisplit_tester(
        test_string,
        None,
        )


    multisplit_tester(
        ' \t \n a \t \nb\t \nc  \n',
        big.ascii_whitespace,
        )


    multisplit_tester(
        'xyxyaxyxyxbycxyxyxydyxeyyyyfxxxxxx',
        'xy',
        )

    # test overlapping
    multisplit_tester(
        'oqaxaaXbbqXbo',
        ('aX', 'Xb', 'o'),
        )

    multisplit_tester(
        'oqaXaaXbbqXbo',
        ('aX', 'Xb', 'o'),
        )


def test_multipartition():
    def test_multipartition(s, separator, count, expected, *, reverse=False):
         for _ in range(2):
            if _ == 1:
                # encode!
                s = s.encode('ascii')
                # if separator == big.whitespace:
                #     separator = big.bytes_whitespace
                if isinstance(separator, str):
                    separator = separator.encode('ascii')
                else:
                    separator = big.encode_strings(separator)
                expected = big.encode_strings(expected)

            # print()
            if isinstance(separator, (str, bytes)):
                separators = (separator,)
            else:
                separators = separator

            got = big.multipartition(s, separators, count, reverse=reverse)
            # print(f"    {got!r}")
            assert expected == got

            got2 = big.multirpartition(s, separators, count, reverse=not reverse)
            # print(f"    {got2!r}")
            assert expected == got2

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

    # test overlapping separators
    test_multipartition("a x x b", " x ", 1, ("a", " x ", "x b"))
    test_multipartition("a x x b", " x ", 1, ("a x", " x ", "b"), reverse=True)

    # test actually using multiple separators, and just for fun--overlapping!
    test_multipartition("a x x b y y c", (" x ", " y "), 2, ("a", " x ", "x b", " y ", "y c"))
    test_multipartition("a x x b y y c", (" x ", " y "), 2, ("a x", " x ", "b y", " y ", "c"), reverse=True)

    # test greedy
    test_multipartition("VWabcWXabXYbcYZ", ('a', 'ab', 'abc', 'b', 'bc', 'c'), 3, ('VW', 'abc', 'WX', 'ab', 'XY', 'bc', 'YZ'))
    test_multipartition("VWabcWXabXYbcYZ", ('a', 'ab', 'abc', 'b', 'bc', 'c'), 3, ('VW', 'abc', 'WX', 'ab', 'XY', 'bc', 'YZ'), reverse=True)

    # regression: multipartition should preserve subclasses by
    # returning slices of the original.
    SS = StrSubclass
    result = big.multipartition(SS('a:b:c'), (SS(':'),), 2)
    assert ('a', ':', 'b', ':', 'c') == result
    for s in result:
        assert isinstance(s, SS)
    assert ''.join(result) == 'a:b:c'

    # regression: if separators is an iterator or generator,
    # multipartition should materialize and validate it.
    assert big.multipartition('a,b', iter((',',)), 1) == ('a', ',', 'b')
    assert big.multipartition(b'a,b', iter((b',',)), 1) == (b'a', b',', b'b')
    with raises(ValueError):
        big.multipartition('abc', iter(()), 1)
    with raises(ValueError):
        big.multipartition(b'abc', iter(()), 1)

    class Indexable:
        def __init__(self, value):
            self.value = value
        def __index__(self):
            return self.value

    assert big.multipartition('a:b:c:d', (':',), Indexable(2)) == ('a', ':', 'b', ':', 'c:d')
    assert big.multirpartition('a:b:c:d', (':',), Indexable(2)) == ('a:b', ':', 'c', ':', 'd')

    with raises(ValueError):
        big.multipartition("a x x b y y c", (" x ", " y "), -1)


def test_multireplace():
    def test(s, replacements, expected, count=-1, *, reverse=False):
        for _ in range(2):
            if _ == 1:
                # encode!
                s = s.encode('ascii')
                replacements = {key.encode('ascii'): value.encode('ascii') for key, value in replacements.items()}
                expected = expected.encode('ascii')

            got = big.multireplace(s, replacements, count, reverse=reverse)
            assert expected == got

    # a single pass: replaced text is never itself re-replaced
    test('ab', {'a': 'b', 'b': 'a'}, 'ba')
    test('x', {'x': 'xx'}, 'xx')
    test('xxx', {'x': 'xx'}, 'xxxxxx')

    # greedy: longest matching key wins
    test('a category', {'cat': 'dog', 'category': 'taxonomy'}, 'a taxonomy')
    test('VWabcWXabXYbcYZ', {'a': '1', 'ab': '2', 'abc': '3', 'b': '4', 'bc': '5', 'c': '6'}, 'VW3WX2XY5YZ')

    # count, with and without reverse
    test('aaa', {'a': 'b'}, 'bba', 2)
    test('aaa', {'a': 'b'}, 'abb', 2, reverse=True)
    test('aaa', {'a': 'b'}, 'aaa', 0)
    test('aaa', {'a': 'b'}, 'bbb', None)

    # overlapping keys: reverse prefers the rightmost match
    test('xa0bx', {'a0': 'A', '0b': 'B'}, 'xAbx')
    test('xa0bx', {'a0': 'A', '0b': 'B'}, 'xaBx', reverse=True)

    # no matches, empty string
    test('no matches here', {'q': 'r'}, 'no matches here')
    test('', {'q': 'r'}, '')

    # adjacent matches
    test('abab', {'ab': 'X'}, 'XX')
    test(':a::b:', {':': '!', '::': '?'}, '!a?b!')

    # empty values delete
    test('a-b-c', {'-': ''}, 'abc')

    # subclasses of str work, in s and in replacements
    SS = StrSubclass
    assert 'a-b' == big.multireplace(SS('a:b'), {SS(':'): SS('-')})
    assert 'a-b' == big.multireplace(SS('a:b'), {':': '-'})

    # multireplace supports big.string: the result is
    # reassembled with big.string.cat, so it's a big.string
    # too, and every unchanged segment still knows its
    # original file, line, and column
    src = string('the cat sat on the cat mat', source='pets.txt')
    got = big.multireplace(src, {'cat': 'dog'})
    assert isinstance(got, string)
    assert str(got) == 'the dog sat on the dog mat'
    middle = ' sat on the '
    segment = got[str(got).index(middle) : str(got).index(middle) + len(middle)]
    assert str(segment) == middle
    assert segment.source == 'pets.txt'
    assert segment.column_number == src.index(middle) + 1
    # it's also a method on string
    got = src.multireplace({'cat': 'dog'}, 1, reverse=True)
    assert isinstance(got, string)
    assert str(got) == 'the cat sat on the dog mat'

    with raises(TypeError):
        big.multireplace('abc', [('a', 'b')])   # not a mapping
    with raises(TypeError):
        big.multireplace('abc', {b'a': b'b'})   # key/value type doesn't match s
    with raises(TypeError):
        big.multireplace(b'abc', {'a': 'b'})
    with raises(TypeError):
        big.multireplace('abc', {'a': b'b'})    # value type doesn't match s
    with raises(ValueError):
        big.multireplace('abc', {'': 'b'})      # empty key
    with raises(ValueError):
        big.multireplace('abc', {})             # empty replacements


def test_wrap_words():
    def test(words, expected, margin=79):
        got = big.wrap_words(words, margin)
        assert got == expected
        got = big.wrap_words(to_bytes(words), margin)
        assert got == to_bytes(expected)

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

    # an empty word stream is a caller bug: the pipeline
    # can't produce one (split_text_with_code returns ['']
    # for empty input), so only a hand-built stream gets here.
    with raises(ValueError):
        big.wrap_words([])
    with raises(ValueError):
        big.wrap_words(iter(()))
    # ...and the pipeline's actual empty case wraps fine.
    assert big.wrap_words(big.split_text_with_code('')) == ''

def test_wrap_words_two_spaces_false():
    # Regression test.  The two_spaces parameter used to be
    # clobbered by a local variable, so two_spaces=False was
    # silently ignored.
    words = "i like pie. so there!".split()
    got = big.wrap_words(iter(words), two_spaces=False)
    assert got == "i like pie. so there!"
    got = big.wrap_words(to_bytes(words), two_spaces=False)
    assert got == b"i like pie. so there!"

    # The clobbering recurred once (2026), in a form the test
    # above is blind to: the emitted space was correct, but col
    # over-counted by one after sentence-enders, so lines wrapped
    # early.  Only visible at a tight margin, so also pin the
    # wrap decision right at the margin's edge:
    # 'aa. bb' is exactly 6 columns--it fits iff two_spaces=False.
    got = big.wrap_words(['aa.', 'bb'], 6, two_spaces=False)
    assert got == "aa. bb"
    got = big.wrap_words([b'aa.', b'bb'], 6, two_spaces=False)
    assert got == b"aa. bb"
    # ...and the two_spaces=True twin wraps, proving the flag,
    # not the punctuation, decides.
    got = big.wrap_words(['aa.', 'bb'], 6, two_spaces=True)
    assert got == "aa.\nbb"

def test_wrap_words_indent():
    def test(words, expected, margin=79, indent='', tab_width=8):
        got = big.wrap_words(words, margin, indent=indent, tab_width=tab_width)
        assert got == expected
        got = big.wrap_words(to_bytes(words), margin, indent=to_bytes(indent), tab_width=tab_width)
        assert got == to_bytes(expected)

    # a single string indents every line
    test(
        "one two three four five six".split(),
        "    one two\n    three four\n    five six",
        15,
        "    ")

    # a tuple: first line gets indent[0], then indent[1],
    # and the last indent repeats when they run out
    test(
        ['serve', '[-v|--verbose]', '[-t|--times <int>]',
         '[--color <red|green|blue>]', 'host', '[port]', '[path]...'],
        "usage: serve [-v|--verbose]\n"
        "       [-t|--times <int>]\n"
        "       [--color <red|green|blue>] host\n"
        "       [port] [path]...",
        44,
        ('usage: ', '       '))
    test(
        ['a', '\n', 'b', '\n', 'c', '\n', 'd'],
        "1 a\n2 b\n3 c\n3 d",
        20,
        ('1 ', '2 ', '3 '))

    # a hard line break advances the indent sequence...
    test(
        ['aa', '\n', 'bb'],
        "* aa\n  bb",
        20,
        ('* ', '  '))
    # ...but a paragraph break resets it, and the blank
    # line in between is never indented
    test(
        ['aa', '\n\n', 'bb'],
        "* aa\n\n* bb",
        20,
        ('* ', '  '))
    # note that a paragraph break must be two '\n' in one s,
    # '\n\n', two separate '\n's don't constitute a paragraph break
    test(
        ['aa', '\n', '\n', 'bb'],
        "* aa\n\n  bb",
        20,
        ('* ', '  '))

    # a code paragraph is a paragraph: it resets the
    # sequence, and its lines are indented like any others
    test(
        big.split_text_with_code("intro text\n\n    x = 1\n    y = 2\n\noutro"),
        "    intro text\n\n        x = 1\n        y = 2\n\n    outro",
        40,
        "    ")

    # by default (code_indent=None) code lines get no separate
    # treatment: they consume from indent like any other line,
    # and a paragraph that opens with a code line gets indent[0]
    got = big.wrap_words(
        big.split_text_with_code("intro text\n\n    x = 1\n\noutro"),
        40, indent=('* ', '  '))
    assert got == "* intro text\n\n*     x = 1\n\n* outro"

    # ...including counting against the sequence mid-paragraph
    # (only a hand-built stream can mix code into a paragraph)
    got = big.wrap_words(
        ['text', '\n', '    code', '\n', 'more'],
        40, indent=('1 ', '2 ', '3 '))
    assert got == "1 text\n2     code\n3 more"

    # with a code_indent, code lines draw from its own sequence
    # and no longer consume from indent
    got = big.wrap_words(
        ['text', 'text', '\n\n', '    code', '\n\n', 'more', 'more'],
        8, indent=('1 ', '2 ', '3 '), code_indent='| ')
    expected = "1 text\n2 text\n\n|     code\n\n1 more\n2 more"
    assert got == expected



    # code_indent='' means code lines get no indent at all
    got = big.wrap_words(
        big.split_text_with_code("intro text\n\n    x = 1\n\noutro"),
        40, indent=('* ', '  '), code_indent='')
    assert got == "* intro text\n\n    x = 1\n\n* outro"

    # code_indent has the same shape and rules as indent,
    # including reset-per-paragraph for a list
    got = big.wrap_words(
        big.split_text_with_code("intro\n\n    x = 1\n    y = 2\n\noutro"),
        40, indent='  ', code_indent='>>> ')
    assert got == "  intro\n\n>>>     x = 1\n>>>     y = 2\n\n  outro"
    got = big.wrap_words(
        big.split_text_with_code("text\n\n    a\n    b\n\nmore\n\n    c\n    d"),
        40, code_indent=('1)', '2)'))
    assert got == "text\n\n1)    a\n2)    b\n\nmore\n\n1)    c\n2)    d"
    got = big.wrap_words(
        [b'aa', b'\n\n', b'    c = 1'], 20, indent=b'* ', code_indent=b'  ')
    expected = b'* aa\n\n      c = 1'
    assert got == expected

    # every linebreak character is forbidden in an indent,
    # as defined by big's linebreaks / bytes_linebreaks
    for ch in set(big.linebreaks):
        with subtest(ch=ch):
            with raises(ValueError):
                big.wrap_words(['a'], 20, indent=f'x{ch}')
            with raises(ValueError):
                big.wrap_words(['a'], 20, code_indent=f'x{ch}')
    for b in set(big.bytes_linebreaks):
        with subtest(b=b):
            with raises(ValueError):
                big.wrap_words([b'a'], 20, indent=b'x' + b)

    # code_indent shares indent's validation, and errors
    # name the offending parameter
    with raises(TypeError):
        big.wrap_words(['a'], 20, code_indent=5)
    with raises(TypeError):
        big.wrap_words(['a'], 20, code_indent=b'  ')
    with raises(ValueError) as cm:
        big.wrap_words(['a'], 4, code_indent='    ')
    assert 'code_indent' in str(cm.exception)

    # indents count against margin.  a tab in an indent is
    # expanded to spaces at the indent's true position (the
    # start of the line), using tab_width.
    got = big.wrap_words("one two three four five six seven".split(), 12, indent='\t', tab_width=4)
    expected = "    one two\n    three\n    four\n    five six\n    seven"
    assert got == expected
    for line in got.split('\n'):
        assert len(line) <= 12

    # the empty-pipeline case still wraps to the empty
    # string--no dangling indent
    assert big.wrap_words(big.split_text_with_code(''), indent='  ') == ''

    # empty indents mean "don't indent", in both flavors
    plain = big.wrap_words(['a', 'b'], 20)
    for indent in ('', (), []):
        assert big.wrap_words(['a', 'b'], 20, indent=indent) == plain
    assert big.wrap_words([b'a', b'b'], 20, indent='') == b'a b'

    # indent must be str/bytes matching words, or a list
    # or tuple of same--nothing else
    with raises(TypeError):
        big.wrap_words(['a'], 20, indent=5)
    with raises(TypeError):
        big.wrap_words(['a'], 20, indent=('* ', 5))
    with raises(TypeError):
        big.wrap_words(['a'], 20, indent={'* '})
    with raises(TypeError):
        big.wrap_words(['a'], 20, indent=b'  ')
    with raises(TypeError):
        big.wrap_words([b'a'], 20, indent='  ')

    # linebreak characters in an indent are forbidden
    with raises(ValueError):
        big.wrap_words(['a'], 20, indent='  \n')
    with raises(ValueError):
        big.wrap_words(['a'], 20, indent='  \r')
    with raises(ValueError):
        big.wrap_words([b'a'], 20, indent=b'  \n')

    # an indent as wide as margin leaves no room for words
    with raises(ValueError):
        big.wrap_words(['a'], 4, indent='    ')
    with raises(ValueError):
        big.wrap_words(['a'], 4, indent='\t', tab_width=8)

def test_expand_tabs():
    # tab stops sit at 1-based columns 9, 17, 25...
    assert big.expand_tabs('x\ty') == 'x       y'
    assert big.expand_tabs('\t\ty') == '                y'
    # column says where s starts; a tab's width depends on it
    assert big.expand_tabs('x\ty', column=8) == 'x        y'
    assert big.expand_tabs('x\ty', column=9) == 'x       y'
    assert big.expand_tabs(b'x\ty', column=8, tab_width=4) == b'x    y'
    # a linebreak resets the count to first_column; column
    # only positions the FIRST line
    assert big.expand_tabs('x\ty\n\tz') == 'x       y\n        z'
    assert big.expand_tabs('x\ty\n\tz', column=5) == 'x   y\n        z'
    # linebreaks split as str.splitlines splits them,
    # and are preserved in the result
    assert big.expand_tabs('a\tb\r\nc\td') == 'a       b\r\nc       d'
    # first_column anchors the tab-stop grid, exactly as it
    # does in big.string: first_column=5 puts stops at
    # columns 5, 13, 21...
    assert big.expand_tabs('\tz', column=5, first_column=5) == '        z'
    # ...and a 0-based world works too
    assert big.expand_tabs('\tz', column=0, first_column=0) == '        z'
    # no tabs: returns s unchanged, the same object
    s = 'no tabs\nhere'
    assert big.expand_tabs(s) is s
    # column >= first_column >= 0, ints only--the same
    # validation big.string applies to its column numbers
    with raises(ValueError):
        big.expand_tabs('x', column=0)
    with raises(ValueError):
        big.expand_tabs('x', column='1')
    with raises(ValueError):
        big.expand_tabs('x', column=3, first_column=-1)

def test_wrap_words_tabs():
    def test(words, expected, margin=79, **kwargs):
        got = big.wrap_words(iter(words), margin, **kwargs)
        assert got == expected
        got = big.wrap_words(to_bytes(words), margin,
            **{k: (to_bytes(v) if isinstance(v, str) else v)
               for k, v in kwargs.items()})
        assert got == to_bytes(expected)

    # a '\t' word places the next word at the next tab stop.
    # columns are 1-based: with tab_width=8 the stops are at
    # columns 9, 17, 25...  a tab renders as spaces--wrap_words
    # is the final rendering, and its output contains no tabs.
    test(['x', '\t', 'abc'], 'x       abc')
    # consecutive tabs advance consecutive stops
    test(['x', '\t', '\t', 'abc'], 'x               abc')
    # no space is inserted around a tab--the tab IS the
    # separation--and sentence-ending punctuation doesn't
    # double-space across one
    test(['end.', '\t', 'x'], 'end.    x')
    # left_column phases the stops: text starting at column 5
    # reaches the column-9 stop after four characters
    test(['x', '\t', 'abc'], 'x   abc', left_column=5)
    # if the word after a tab doesn't fit, the word wraps and
    # the tab dies with the line, just like a space would
    test(['aaaa', '\t', 'bbbb'], 'aaaa\nbbbb', 10)
    # a trailing tab dies; a tab before a line break dies
    test(['a', '\t'], 'a')
    test(['a', '\t', '\n', 'b'], 'a\nb')
    # tabs count against the margin like everything else
    test(['x', '\t', 'abcd', 'efgh'], 'x       abcd\nefgh', 12)
    # a tab at the *start* of a line (a hand-built stream:
    # split_text_with_code never emits one there) advances
    # from the line's start...
    test(['a', '\n', '\t', 'x'], 'a\n        x')
    test(['\t', 'x'], '        x')
    # ...with no wrap check: like an over-long word, an
    # over-margin stop just overflows
    test(['a', '\n', '\t', '\t', 'xx'], 'a\n                xx', 6)
    # tabs work within an indented block; the indent's width
    # counts toward the stop
    test(['x', '\t', 'abc'], '   x    abc', indent='   ')

    # a code line's tabs expand at render time.  unshifted,
    # that's exactly what the source looked like:
    words = big.split_text_with_code("text\n\n    x\ty = 1")
    test(list(words), 'text\n\n    x   y = 1')
    # ...and under an indent, they expand where they actually
    # land: the four-wide prefix pushes the tab past the
    # column-9 stop, so it advances to column 17.  (rigidly
    # shifting a block instead is format_definition_list's
    # definition_relative_tabs.)
    got = big.wrap_words(iter(words), 79, indent='####')
    assert got == '####text\n\n####    x       y = 1'

    # left_column must be a positive int
    with raises(ValueError):
        big.wrap_words(['a'], 20, left_column=0)
    with raises(ValueError):
        big.wrap_words(['a'], 20, left_column='1')

def test_format_definition_list():
    # the showpiece: computed column, wrapped definitions,
    # a wide term hanging, a multi-paragraph definition with
    # a code line, and an empty definition
    pairs = [
        ('-v, --verbose', 'Print more output.  Repeat for even more.'),
        ('--color <red|green|blue>', 'Sets the output color.'),
        ('-q', 'Quiet mode.\n\nOverrides every -v:\n\n    tool -q -vvv'),
        ('--legacy', ''),
    ]
    expected = (
        "  -v, --verbose  Print more output.  Repeat\n"
        "                 for even more.\n"
        "  --color <red|green|blue>\n"
        "                 Sets the output color.\n"
        "  -q             Quiet mode.\n"
        "\n"
        "                 Overrides every -v:\n"
        "\n"
        "                     tool -q -vvv\n"
        "  --legacy"
    )
    got = big.format_definition_list(pairs, 44)
    assert got == expected
    # every line fits the margin
    for line in got.split('\n'):
        assert len(line) <= 44
    # bytes, with the defaults adapting
    got = big.format_definition_list(
        [(to_bytes(term), to_bytes(defn)) for term, defn in pairs], 44)
    assert got == to_bytes(expected)

    # the hang threshold: a term no wider than a third of the
    # usable width (margin - indent) participates in column
    # sizing; one character wider hangs.  margin 32, indent 2:
    # usable 30, threshold 10.
    ten = 'x' * 10
    eleven = 'x' * 11
    got = big.format_definition_list([(ten, 'aa'), ('y', 'bb')], 32)
    assert got == f"  {ten}  aa\n  y           bb"
    got = big.format_definition_list([(eleven, 'aa'), ('y', 'bb')], 32)
    assert got == f"  {eleven}\n     aa\n  y  bb"

    # the spacer is fill material, tiled TeX-leaders style:
    # phase-locked to the term column, clipped at the front,
    # filling the whole span on lines with no term
    pairs = [('x', 'abcde'),
             ('y so long', 'this is the text for y no fooling'),
             ('but z is longer still', 'zzz...')]
    got = big.format_definition_list(pairs, 32, indent='||| ', spacer=':')
    expected = (
        "||| x:::::::::abcde\n"
        "||| y so long:this is the text\n"
        "||| ::::::::::for y no fooling\n"
        "||| but z is longer still\n"
        "||| ::::::::::zzz...")
    assert got == expected
    # a multi-character spacer tiles; the repeats line up
    # vertically no matter how wide each term is
    got = big.format_definition_list(pairs, 32, indent='||| ', spacer=':--')
    expected = (
        "||| x--:--:--:--abcde\n"
        "||| y so long:--this is the text\n"
        "||| :--:--:--:--for y no fooling\n"
        "||| but z is longer still\n"
        "||| :--:--:--:--zzz...")
    assert got == expected

    # tabs are legal in terms and in the indent; they expand
    # to spaces.  by default a term's tabs expand in the term's
    # own coordinates (term_relative_tabs=True), and the ribbon
    # picks up where the expanded term leaves off
    got = big.format_definition_list([('a\tb', 'D'), ('cc', 'E')], 40, indent='')
    assert got == 'a       b  D\ncc         E'
    # term_relative_tabs=False expands at the term's true
    # position on the page, after the indent
    got = big.format_definition_list([('a\tb', 'D'), ('cc', 'E')], 40,
        indent='..', term_relative_tabs=False)
    assert got == '..a     b  D\n..cc       E'
    # the indent's tabs expand at ITS true position: column 1
    got = big.format_definition_list([('x', 'D')], 40, indent='\t', tab_width=4)
    assert got == '    x  D'

    # empty pairs is an empty table, not an error;
    # whitespace-only definitions count as empty (and don't
    # leave trailing whitespace after the term)
    assert big.format_definition_list([], 40) == ''
    assert big.format_definition_list([('-x', '   ')], 40) == '  -x'

    # terms, indent, and spacer reject linebreak characters,
    # and everything type-checks against the pairs
    with raises(ValueError):
        big.format_definition_list([('a\nb', 'x')], 40)
    with raises(ValueError):
        big.format_definition_list([('a', 'x')], 40, indent='\r')
    with raises(ValueError):
        big.format_definition_list([('a', 'x')], 40, spacer=' \n')
    with raises(TypeError):
        big.format_definition_list([(5, 'x')], 40)
    with raises(TypeError):
        big.format_definition_list([(b'a', b'x')], 40, indent='  ')
    with raises(TypeError):
        big.format_definition_list([('a', 'x')], 40, spacer=7)
    # the spacer is fill material: it can't be empty, and it
    # can't contain tabs (it repeats and shifts around, and a
    # tab's width depends on where it lands)
    with raises(ValueError):
        big.format_definition_list([('a', 'x')], 40, spacer='')
    with raises(ValueError):
        big.format_definition_list([('a', 'x')], 40, spacer=' \t')
    # a definition column too wide for the margin is an error
    with raises(ValueError):
        big.format_definition_list([('aaaa', 'x')], 8, spacer=' ' * 8)

    # definition_left_column: the fussy user names the exact
    # 1-based column (indent included) where definitions start
    got = big.format_definition_list(
        [('wwwwwwwww', 'DEF one'), ('x', 'DEF two')], 30,
        indent='', definition_left_column=12)
    assert got == 'wwwwwwwww  DEF one\nx          DEF two'
    # the hang rule is purely geometric under an explicit
    # column: a term hangs iff it can't fit with a full
    # spacer after it
    got = big.format_definition_list(
        [('wwwwwwwwww', 'DEF'), ('x', 'D')], 30,
        indent='', definition_left_column=12)
    assert got == 'wwwwwwwwww\n           DEF\nx          D'
    # an explicit column with no room for the spacer, or no
    # room for definitions, is an error; so is a bogus column
    with raises(ValueError):
        big.format_definition_list([('a', 'b')], 30, definition_left_column=3)
    with raises(ValueError):
        big.format_definition_list([('a', 'b')], 12, definition_left_column=13)
    with raises(ValueError):
        big.format_definition_list([('a', 'b')], 30, definition_left_column=0)

    # definition_relative_tabs=True (the default): a definition
    # is laid out in its author's own coordinates and shifted
    # rigidly into place, so the author's tab alignment
    # survives at ANY definition column.  =False lands its tabs
    # on the tab stops of the page.  code lines make the
    # difference visible: in source, both these Zs sit at
    # column 9; shifted to definition column 11, page stops
    # split them apart.
    d = "T:\n\n    a\tZ\n    ab\tZ"
    got = big.format_definition_list(
        [('t', d)], 60, indent='', definition_left_column=11)
    assert got == "t         T:\n\n              a   Z\n              ab  Z"
    got = big.format_definition_list(
        [('t', d)], 60, indent='', definition_left_column=11,
        definition_relative_tabs=False)
    assert got == "t         T:\n\n              a Z\n              ab        Z"

def test_merge_columns_relative_tabs():
    # a column tuple's optional fourth member governs tab
    # expansion (always to spaces).  True, the default: tabs
    # expand in the column's own coordinates, so its internal
    # alignment survives wherever the column lands.  False:
    # tabs land on the tab stops of the page (the column's
    # nominal position).
    c2 = "x\ty\nxx\ty"
    got = big.merge_columns(("a\nb", 4, 4), (c2, 12, 12))
    assert got == 'a    x       y\nb    xx      y'
    got = big.merge_columns(("a\nb", 4, 4), (c2, 12, 12, False))
    assert got == 'a    x  y\nb    xx y'

def test_split_text_with_code_unusual_whitespace():
    # Regression test.  Unusual whitespace characters
    # (\r, \v, \f, nbsp, ...) used as line-leading indentation
    # used to raise RuntimeError.  Now they count as width 1.
    for ws in ('\xa0', '\r', '\x0b', '\x0c'):
        got = big.split_text_with_code(f"hello\n{ws}world")
        assert got == ['hello', 'world']

def test_split_text_with_code_code_text_code():
    # Regression test.  A code paragraph, then a text paragraph,
    # then another code paragraph.  The old character-at-a-time
    # splitter left stale blank-line state behind when a code
    # paragraph ended; the next code paragraph either crashed
    # with AssertionError or, if blank lines separated the
    # paragraphs, polluted the output with stray '\n' words.
    def test(s, expected, **kwargs):
        assert big.split_text_with_code(s, **kwargs) == expected
        assert big.split_text_with_code(to_bytes(s), **kwargs) == to_bytes(expected)

    test("    a\nx\n    b\n",
        ['    a', '\n\n', 'x', '\n\n', '    b'])
    test("    a\n\nx\n\n    b\n",
        ['    a', '\n\n', 'x', '\n\n', '    b'])
    # interior blank lines of a code paragraph survive...
    test("    a\n\n    b\n",
        ['    a', '\n', '\n', '    b'])
    # ...but blank lines trailing the last code paragraph don't.
    test("    a\n\n\n",
        ['    a'])
    # a code line at EOF doesn't need a trailing linebreak.
    test("    a\nx\n    b",
        ['    a', '\n\n', 'x', '\n\n', '    b'])
    # code lines are emitted verbatim, tabs included--
    # wrap_words expands them at render time.
    test("\ta\n", ['\ta'])
    # code_indent=0 means there are no code lines: it's all
    # just text.  code_indent uses the index protocol--any
    # __index__-bearing type works--but bools are refused
    # (no None, no False: we must remain strong), floats are
    # refused, and negative is meaningless.
    test("    a\nx\n    b\n", ['a', 'x', 'b'], code_indent=0)
    class Four:
        def __index__(self):
            return 4
    assert big.split_text_with_code("    a\nx\n", code_indent=Four()) == ['    a', '\n\n', 'x']
    for bad in (None, False, True, 4.0):
        with raises(TypeError):
            big.split_text_with_code("x", code_indent=bad)
    with raises(ValueError):
        big.split_text_with_code("x", code_indent=-1)
    # in text, each tab survives as its own '\t' word: a run
    # of whitespace containing k tabs becomes exactly k '\t'
    # words, in order, however the run is spelled.
    test("a \t   \tb\n", ['a', '\t', '\t', 'b'])
    test("a\t  \t       b\n", ['a', '\t', '\t', 'b'])
    test("a\tb c\n", ['a', '\t', 'b', 'c'])

def test_merge_columns_default_overflow_strategy():
    # the default overflow strategy is RAISE: overflow is an
    # error, and it doesn't pass silently unless you silence
    # it by picking another strategy.
    columns = (("this-line-is-way-too-wide\nshort", 5, 5), ("aaa\nbbb", 3, 3))
    with raises(OverflowError):
        big.merge_columns(*columns)

def test_merge_columns_input_validation_raises():
    # regression: these guards used to be asserts, which vanish
    # under python -O--OverflowStrategy.INVALID (a real, exported
    # enum member!) silently behaved as INTRUDE_ALL there, and
    # zero columns gave a bare IndexError.  now they raise
    # ValueError under any interpreter.
    columns = (("aaa\nbbb", 3, 3),)
    with raises_regex(ValueError, "invalid overflow_strategy"):
        big.merge_columns(*columns, overflow_strategy=big.OverflowStrategy.INVALID)
    with raises_regex(ValueError, "invalid overflow_strategy"):
        big.merge_columns(*columns, overflow_strategy="RAISE")
    with raises_regex(ValueError, "no columns"):
        big.merge_columns()

def test_merge_columns_trailing_whitespace():
    # Regression test.  Per-line trailing whitespace used to
    # fool the padding math, misaligning subsequent columns.
    got = big.merge_columns(("alpha   \nbeta", 6, 6), ("one\ntwo", 5, 5))
    assert got == "alpha  one\nbeta   two"

def test_merge_columns_overflow_after_at_end_of_column():
    # Regression test.  The overflow_after padding lines for an
    # overflow at the very end of a column used to be lost,
    # making overflow_after a silent no-op there.
    got = big.merge_columns(
        ("short\nthis-line-is-way-too-wide", 5, 5),
        ("aaa\nbbb\nccc", 3, 3),
        overflow_strategy=big.OverflowStrategy.INTRUDE_ALL,
        overflow_after=1)
    assert got == "short aaa\nthis-line-is-way-too-wide\n\n      bbb\n      ccc"


def test_split_text_with_code():
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
        assert expected == got
        got = big.split_text_with_code(to_bytes(s), **kwargs)
        assert to_bytes(expected) == got

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
        "hey there party people\n\nhere, we have a second paragraph.\nwith an internal linebreak.\n\n    for i in code:\n        print(i)\n\nmore text here? sure seems like it.",
        ['hey', 'there', 'party', 'people', '\n\n', 'here,', 'we', 'have', 'a', 'second', 'paragraph.', 'with', 'an', 'internal', 'linebreak.', '\n\n', '    for i in code:', '\n', '        print(i)', '\n\n', 'more', 'text', 'here?', 'sure', 'seems', 'like', 'it.']
        )
    test(
        "text paragraphs separated by infinite linebreaks get collapsed to just two linebreaks.\n\n\n\n\nsee? just two.\n\n\n\n\n\n\n\n\nqed!",
        ['text', 'paragraphs', 'separated', 'by', 'infinite', 'linebreaks', 'get', 'collapsed', 'to', 'just', 'two', 'linebreaks.', '\n\n', 'see?', 'just', 'two.', '\n\n', 'qed!']
        )
    test(
        "here's some code with a tab.\n\tfor x in range(3):\n\t\tprint(x)\nwelp! that's it for the code.",
        ["here's", 'some', 'code', 'with', 'a', 'tab.', '\n\n', '\tfor x in range(3):', '\n', '\t\tprint(x)', '\n\n', 'welp!', "that's", 'it', 'for', 'the', 'code.']
        )
    test(
        "this is text, but next is a code paragraph with a lot of internal linebreaks and stuff.\n\tfor x in range(3):\n\n   \n\n    \t\n\t\tprint(x)\n\t\t\n\n\t\tprint(x*x)\nwelp! that's it for the code.",
        ['this', 'is', 'text,', 'but', 'next', 'is', 'a', 'code', 'paragraph', 'with', 'a', 'lot', 'of', 'internal', 'linebreaks', 'and', 'stuff.', '\n\n',
        '\tfor x in range(3):', '\n', '\n', '\n', '\n', '\n', '\t\tprint(x)', '\n', '\n', '\n', '\t\tprint(x*x)', '\n\n', 'welp!', "that's", 'it', 'for', 'the', 'code.']
        )
    # unusual whitespace characters (\v, \f, \r, nbsp...)
    # used to raise RuntimeError; now they count as width 1
    # (and are preserved verbatim inside code lines).
    test(
        "howdy.\n\vwhat's this?",
        ['howdy.', "what's", 'this?'],
        )
    test(
        "howdy.\n    for a in \v range(30):\n        print(a)",
        ['howdy.', '\n\n', '    for a in \v range(30):', '\n', '        print(a)'],
        )
    # regression test: a code paragraph ending at EOF *without*
    # a trailing linebreak used to lose its final line.
    test(
        "text here.\n    code1\n    code2",
        ['text', 'here.', '\n\n', '    code1', '\n', '    code2'],
        )


def test_merge_columns():
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
        assert got == expected
        bytes_columns = [(to_bytes(c[0]), c[1], c[2]) for c in columns]
        if 'column_separator' in kwargs:
            kwargs['column_separator'] = to_bytes(kwargs['column_separator'])
        got = big.merge_columns(*bytes_columns, **kwargs)
        assert got == to_bytes(expected)

    with raises(OverflowError):
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
        'overflow line 1\na\nb\nc\nd\noverflow line 2\n\n\n\n         this is the second column.\n         does it have to wait?  it should.',
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


def test_text_pipeline():
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
            assert got == expected
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


def test_split_title_case():

    def alternate_split_title_case(s, *, split_allcaps=True):
        """
        Alternate implementation of split_title_case,
        used for testing.
        """
        if not s:
            yield s
            return

        if isinstance(s, bytes):
            empty_join = b''.join
            i = _iterate_over_bytes(s)
        else:
            empty_join = ''.join
            i = iter(s)

        word = []
        append = word.append
        pop = word.pop
        clear = word.clear

        previous_was_lower = False
        upper_counter = 0

        for c in i:
            is_upper = c.isupper()
            is_lower = c.islower()
            # print(f"{c=} {is_upper=} {is_lower=} {upper_counter=} {previous_was_lower=} {split_allcaps=}")
            if is_upper:
                if previous_was_lower:
                    if word:
                        yield empty_join(word)
                        clear()
                    previous_was_lower = False
                if split_allcaps:
                    upper_counter += 1
            else:
                if is_lower:
                    if upper_counter > 1:
                        assert word
                        popped = pop()
                        if word:
                            yield empty_join(word)
                            clear()
                        append(popped)
                upper_counter = 0
                previous_was_lower = is_lower
            append(c)
            continue
        if word:
            yield empty_join(word)
            clear()

    def test(s, **kw):
        expected = list(alternate_split_title_case(s, **kw))
        got = list(big.split_title_case(s, **kw))
        assert expected == got

        b = s.encode('ascii')
        bytes_expected = list(alternate_split_title_case(b, **kw))
        bytes_got = list(big.split_title_case(b, **kw))
        assert bytes_expected == bytes_got

    assert isinstance(big.split_title_case('HowdyFolks'), types.GeneratorType)

    test('')
    test('ThisIsATitleCaseString')
    test('     ')
    test(' 333    ')
    test('YoursTrulyJohnnyDollar_1975-03-15 - TheMysteriousMaynardMatter.MP3')

    test('oneOfTheGoodOnes')
    test('aRoadLessTraveled')

    test("Can'tComplain")

    test("NOTHINGInTheWORLD")
    test("NOTHINGInTheWORLD", split_allcaps=False)

    test("WhenIWasATeapot", split_allcaps=False)
    test("WhenIWasATeapot", split_allcaps=True)

    # regression: a single-character final word used to be
    # silently dropped ('WhenIWasA' -> ['When', 'I', 'Was'],
    # and 'A' -> []).  the alternate implementation always got
    # these right; they'd just never been fed to the pair.
    test('A')
    test('a')
    test('aA')
    test('WhenIWasA')
    test('WhenIWasA', split_allcaps=False)

    # exhaustive sweep: the two implementations must agree on
    # every short string, and joining the split must always
    # reconstruct s--split_title_case never loses characters.
    for length in range(0, 5):
        for chars in itertools.product('aAbB', repeat=length):
            s = ''.join(chars)
            for split_allcaps in (False, True):
                expected = list(alternate_split_title_case(s, split_allcaps=split_allcaps))
                got = list(big.split_title_case(s, split_allcaps=split_allcaps))
                assert expected == got, f"implementations disagree on {s!r}"
                assert ''.join(got) == s, f"split_title_case lost characters from {s!r}"


def test_combine_splits():

    # that's right! this is the maximum possible integer.
    # there are literally no integers greater than this number.
    INT_MAX = 2**256
    # p.s. shhhhh, don't tell him

    def original_combine_splits(s, *splits):
        "Alternate implementation of combine_splits, used for testing."
        # Measure the strings in the split arrays.
        # (Ignore empty split arrays, and ignore empty splits.)
        split_lengths = [ [ len(_) for _ in split  if _ ] for split in splits  if split ]

        def combine_splits(s, split_lengths):
            split_lengths_pop = split_lengths.pop

            drops = []
            drops_append = drops.append
            drops_pop = drops.pop

            while len(split_lengths) >= 2:
                # print(combined, s)
                # for _ in split_lengths:
                #     print("   ", _)
                smallest = INT_MAX
                smallest_index = None

                for i, lengths in enumerate(split_lengths):
                    length = lengths[0]
                    if smallest > length:
                        smallest = length
                        smallest_index = i

                assert smallest != INT_MAX

                yield s[:smallest]
                s = s[smallest:]

                for i, lengths in enumerate(split_lengths):
                    length = lengths[0]
                    if length == smallest:
                        lengths.pop(0)
                        if not lengths:
                            drops_append(i)
                    else:
                        lengths[0] = length - smallest

                while drops:
                    x = split_lengths_pop(drops_pop())
                    assert not x

            if split_lengths:
                start = end = 0
                for index in split_lengths[0]:
                    end += index
                    yield s[start:end]
                    start += index
                s = s[end:]

            if s:
                yield s

        return combine_splits(s, split_lengths)


    def sorting_combine_splits(s, *splits):
        "Alternate implementation of combine_splits, used for testing."

        index_0 = lambda x: x[0]

        # In case an entry in the split arrays is a generator, convert it to a list.
        split_lengths = [ list(split) for split in splits ]
        # Measure the strings in the split arrays.
        # (Remove empty split arrays, and ignore empty splits.)
        split_lengths = [ [ len(_) for _ in split  if _ ] for split in splits  if split ]
        split_lengths.sort(key=index_0)

        def combine_splits(s, split_lengths, index_0):
            split_lengths_pop = split_lengths.pop
            # split_lengths_remove = split_lengths.remove

            drops = []
            drops_append = drops.append
            drops_pop = drops.pop

            if len(split_lengths) >= 2:
                while True:
                    smallest = split_lengths[0]
                    index = smallest[0]

                    yield s[:index]
                    s = s[index:]

                    re_sort = False
                    for i, lengths in enumerate(split_lengths):
                        length = lengths[0]
                        # print("  >>", length, lengths)
                        if length == index:
                            re_sort = True
                            lengths.pop(0)
                            if not lengths:
                                drops_append(i)
                        else:
                            lengths[0] = length - index

                    while drops:
                        x = split_lengths_pop(drops_pop())
                        assert not x
                    if len(split_lengths) < 2:
                        break
                    if re_sort:
                        split_lengths.sort(key=index_0)

            if split_lengths:
                start = end = 0
                for index in split_lengths[0]:
                    end += index
                    yield s[start:end]
                    start += index
                s = s[end:]

            if s:
                yield s

        return combine_splits(s, split_lengths, index_0)

    def test(s, *split_arrays):
        # convert split_arrays into lists, just in case one is an iterator
        # (we'll test an iterator by hand later)
        split_arrays = [list(_) for _ in split_arrays]

        original_result = list(original_combine_splits(s, *split_arrays))
        sorting_result = list(sorting_combine_splits(s, *split_arrays))
        assert original_result == sorting_result
        expected = original_result

        got = list(big.combine_splits(s, *split_arrays))
        assert expected == got

        bytes_s = s.encode('ascii')
        bytes_split_arrays = [ [_.encode('ascii') for _ in l] for l in split_arrays ]
        bytes_expected = [_.encode('ascii') for _ in expected]

        bytes_got = list(big.combine_splits(bytes_s, *bytes_split_arrays))
        assert bytes_expected == bytes_got

    assert isinstance(big.combine_splits('abc', ['a', 'bc'], ['ab', 'c']), types.GeneratorType)

    s  = 'abcdefghijklmnopq'
    s1 = [ 'ab', 'cde', 'fghi', 'jklmnop', 'q' ]
    s2 = [ 'abcde', 'fghi', 'jk', 'lmnopq' ]
    s3 = [ 'abcdefghi', 'jklmn', 'opq' ]

    # should split after B E I K N P
    test(s, s1, s2, s3)

    test(s + "rstuvwxyz", s1, s2, s3)

    s = "aa bb cc dd ee"
    test(s,
        big.multisplit(s, keep=big.ALTERNATING),
        ["aa b", "b cc d", "d ee"],
        )

    s = "aa bb cc dd ee ff"
    test(s,
        s.split(),
        ["aa bb cc dd ee f", "f"],
        )

    with raises(ValueError):
        list(big.combine_splits("a b c d e",
            ["a ", "b "],
            ["a b c d ", "e f g ", "h "],
            ))

    with raises(ValueError):
        list(big.combine_splits("a b c d e",
            ["a ", "b "],
            ["a b c d ", "e f g ", "h "],
            ["a b c ", "d e f ", "g h "],
            ))


def test_gently_title():
    def test(s, expected, test_ascii=True, apostrophes=None, double_quotes=None):
        result = big.gently_title(s, apostrophes=apostrophes, double_quotes=double_quotes)
        assert result == expected
        result = big.gently_title(StrSubclass(s), apostrophes=apostrophes, double_quotes=double_quotes)
        assert result == expected
        if test_ascii:
            if apostrophes:
                apostrophes = apostrophes.encode('ascii')
            if double_quotes:
                double_quotes = double_quotes.encode('ascii')
            result = big.gently_title(s.encode('ascii'), apostrophes=apostrophes, double_quotes=double_quotes)
            assert result == expected.encode('ascii')
            result = big.gently_title(BytesSubclass(s.encode('ascii')), apostrophes=apostrophes, double_quotes=double_quotes)
            assert result == expected.encode('ascii')

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

    with raises(TypeError):
        big.gently_title("the \"string's\" the thing", apostrophes=big.ascii_apostrophes)
    with raises(TypeError):
        big.gently_title("the \"string's\" the thing", double_quotes=big.ascii_double_quotes)
    with raises(TypeError):
        big.gently_title("the \"string's\" the thing", apostrophes=big.ascii_apostrophes, double_quotes=big.ascii_double_quotes)

    with raises(TypeError):
        big.gently_title("the \"string's\" the thing", apostrophes=(b"'",))
    with raises(TypeError):
        big.gently_title("the \"string's\" the thing", double_quotes=(b'"',))
    with raises(TypeError):
        big.gently_title("the \"string's\" the thing", apostrophes=(b"'",), double_quotes=(b'"',))

    with raises(TypeError):
        big.gently_title(b"the \"string's\" the thing", apostrophes=big.apostrophes)
    with raises(TypeError):
        big.gently_title(b"the \"string's\" the thing", double_quotes=big.double_quotes)
    with raises(TypeError):
        big.gently_title(b"the \"string's\" the thing", apostrophes=big.apostrophes, double_quotes=big.double_quotes)

    with raises(TypeError):
        big.gently_title(b"the \"string's\" the thing", apostrophes=("'",))
    with raises(TypeError):
        big.gently_title(b"the \"string's\" the thing", double_quotes=('"',))
    with raises(TypeError):
        big.gently_title(b"the \"string's\" the thing", apostrophes=("'",), double_quotes=('"',))

    with raises(TypeError):
        big.gently_title(StrSubclass("the \"string's\" the thing"), apostrophes=BytesSubclass(big.ascii_apostrophes))
    with raises(TypeError):
        big.gently_title(StrSubclass("the \"string's\" the thing"), double_quotes=BytesSubclass(big.ascii_double_quotes))

    with raises(TypeError):
        big.gently_title(BytesSubclass(b"the \"string's\" the thing"), apostrophes=StrSubclass(big.apostrophes))
    with raises(TypeError):
        big.gently_title(BytesSubclass(b"the \"string's\" the thing"), double_quotes=StrSubclass(big.double_quotes))

    assert big.gently_title(StrSubclass("peter o'toole"), apostrophes=DifferentStrSubclass(big.apostrophes)) == "Peter O'Toole"
    assert big.gently_title(BytesSubclass(b"peter o'toole"), apostrophes=DifferentBytesSubclass(big.ascii_apostrophes)) == b"Peter O'Toole"

    with raises(ValueError):
        big.gently_title("the \"string's\" the thing", apostrophes='')
    with raises(ValueError):
        big.gently_title("the \"string's\" the thing", apostrophes=("'", ''))
    with raises(ValueError):
        big.gently_title("the \"string's\" the thing", double_quotes='')
    with raises(ValueError):
        big.gently_title("the \"string's\" the thing", double_quotes=('"', ''))

    with raises(ValueError):
        big.gently_title(b"the \"string's\" the thing", apostrophes=b'')
    with raises(ValueError):
        big.gently_title(b"the \"string's\" the thing", apostrophes=(b"'", b''))
    with raises(ValueError):
        big.gently_title(b"the \"string's\" the thing", double_quotes=b'')
    with raises(ValueError):
        big.gently_title(b"the \"string's\" the thing", double_quotes=(b'"', b''))


def test_normalize_whitespace():
    def test(s, expected, *, separators=None, replacement=" "):
        for i in range(2):
            result = big.normalize_whitespace(s, separators=separators, replacement=replacement)
            assert result == expected
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

    with raises(TypeError):
        big.normalize_whitespace("abc", "b", -1)
    with raises(TypeError):
        big.normalize_whitespace("abc", -1, "b")
    with raises(ValueError):
        big.normalize_whitespace("abc", "", "c")
    with raises(ValueError):
        big.normalize_whitespace("abc", ('a', "", 'b'), "c")
    with raises(TypeError):
        big.normalize_whitespace(b"abc", "b", "c")
    with raises(TypeError):
        big.normalize_whitespace("abc", b"b", "c")
    with raises(TypeError):
        big.normalize_whitespace("abc", "b", b"c")

    # test that we didn't accidentally use the "fast path"
    # with bytes objects
    string_with_em_space = "ab\u2003cd"
    result = "ab cd"
    assert big.normalize_whitespace("ab\u2003cd") == result
    assert big.normalize_whitespace("ab\u2003cd".encode('utf-8'), big.encode_strings(big.unicode_whitespace, 'utf-8')) == result.encode('utf-8')

    with raises(ValueError):
        big.normalize_whitespace("a b c d   e", separators='')
    with raises(ValueError):
        big.normalize_whitespace("a b c d   e", separators=[])
    with raises(ValueError):
        big.normalize_whitespace(b"a b c d   e", separators=b'')
    with raises(ValueError):
        big.normalize_whitespace(b"a b c d   e", separators=[])


def test_split_quoted_strings():
    def test(s, expected, **kwargs):
        got = list(big.split_quoted_strings(s, **kwargs))

        if 0:
            import pprint
            print("\n\n")
            print("-"*72)
            print("expected:")
            pprint.pprint(expected)
            print("\n\n")
            print("got:")
            pprint.pprint(got)
            print("\n\n")

        assert expected == got

        # if all arguments are str, let's convert to bytes and run another
        if not (isinstance(s, str) and all(isinstance(value, str) for value in kwargs.values())):
            return

        # convert everybody to ascii
        kwargs = {k: to_bytes(v) for k, v in kwargs.items()}

        got = list(big.split_quoted_strings(to_bytes(s), **kwargs))
        expected = to_bytes(expected)
        assert expected == got

    test("""hey there "this is quoted" an empty quote: '' this is not quoted 'this is more quoted' "here's quoting a quote mark: \\" wow!" this is working!""",
        [
            ('',  'hey there ',                             ''),
            ('"', 'this is quoted',                         '"'),
            ('',  ' an empty quote: ',                      ''),
            ("'", "",                                       "'"),
            ('',  ' this is not quoted ',                   ''),
            ("'", "this is more quoted",                    "'"),
            ('',  ' ',                                      ''),
            ('"', 'here\'s quoting a quote mark: \\" wow!', '"'),
            ('',  ' this is working!',                      ''),
        ])

    test('''here is triple quoted: """i am triple quoted.""" wow!  again: """triple quoted here. "quotes in quotes" empty: "" quoted triple quote: \\""" done.""" phew!''',
        [
            ('',    'here is triple quoted: ',                                ''),
            ('"""', 'i am triple quoted.',                                    '"""'),
            ('',    ' wow!  again: ',                                         ''),
            ('"""', 'triple quoted here. "quotes in quotes" empty: "" quoted triple quote: \\""" done.', '"""'),
            ('',    ' phew!',                                                 ''),
        ],
        quotes = ('"', "'", '"""',))

    test('''test without multiline quotes.  """howdy doodles""" it kinda works anyway!''',
        [
            ('',  'test without multiline quotes.  ', ''),
            ('"', '',                                   '"'),
            ('"', 'howdy doodles',                      '"'),
            ('"', '',                                   '"'),
            ('',  ' it kinda works anyway!',            ''),
        ],
        )

    test("a b c' x y z 'd e f'",
        [
            ("",  'a b c', "'"),
            ("",  ' x y z ', ""),
            ("'", 'd e f', "'"),
        ],
        state="'"
        )

    # let's get weird!
    test("abc\ndef\nghi",
        [
            ("",   'abc', ""),
            ("\n", 'def', "\n"),
            ("",   'ghi', ""),
        ],
        quotes=("\n",)
        )

    test("abc'qxqqxx'qqq'def",
        [
            ("",   'abc',        ""),
            ("'",  "qxqqxx'qqq", "'"),
            ("",   'def',        ""),
        ],
        escape="xx"
        )

    test("abc^Sqxqq^X^Sqqq^Sdef^Qghi^Q",
        [
            ("",    'abc',         ""),
            ("^S",  "qxqq^X^Sqqq", "^S"),
            ("",    'def',         ""),
            ("^Q",  'ghi',         "^Q"),
        ],
        quotes=('^S', '^Q',), escape="^X"
        )

    test("abc'qxqqxx\\'qqq'def",
        [
            ("",   'abc',        ""),
            ("'",  "qxqqxx\\",   "'"),
            ("",   'qqq',        ""),
            ("'",  'def',        ""),
        ],
        escape=""
        )

    test("abcd' efg 'hgi",
        [
            ("",   'abcd',  "'"),
            ("",   " efg ", ""),
            ("'",  'hgi',   ""),
        ],
        state="'"
        )

    # test auto-converting _sqs_quotes_str
    test(b"abcd",
        [
            (b"",  b'abcd',  b""),
        ],
        quotes=big.text._sqs_quotes_str
        )

    # test auto-converting _sqs_quotes_bytes
    test("abcd",
        [
            ("",  'abcd',  ""),
        ],
        quotes=big.text._sqs_quotes_bytes
        )

    # test auto-converting _sqs_escape_str
    test(b"abcd",
        [
            (b"",  b'abcd',  b""),
        ],
        escape=big.text._sqs_escape_str,
        multiline_quotes=None,
        )

    # test auto-converting _sqs_escape_bytes
    test("abcd",
        [
            ("",  'abcd',  ""),
        ],
        escape=big.text._sqs_escape_bytes
        )

    # quotes and multiline_quotes are both empty
    with raises(ValueError):
        test("a b c' x y z 'd e f'",
            [],
            quotes=(),
            multiline_quotes=(),
            )

    # type mismatch, s is str and quotes are bytes
    with raises(TypeError):
        test("a b c' x y z 'd e f'",
            [],
            quotes=(b'"', b"'", b"'''"),
            )

    # type mismatch, s is bytes and quotes are str
    with raises(TypeError):
        test(b"a b c' x y z 'd e f'",
            [],
            quotes=('"', "'", "'''"),
            )

    # type mismatch, s is str and multiline_quotes are bytes
    with raises(TypeError):
        test("a b c' x y z 'd e f'",
            [],
            multiline_quotes=(b'<<', b">>", b"^^^"),
            )

    # type mismatch, s is bytes and multiline_quotes are str
    with raises(TypeError):
        test(b"a b c' x y z 'd e f'",
            [],
            multiline_quotes=('<<', ">>", "^^^"),
            )

    # type mismatch, s is str and escape is bytes
    with raises(TypeError):
        test("a b c' x y z 'd e f'",
            [],
            escape=b'x'
            )

    # type mismatch, s is bytes and escape is str
    with raises(TypeError):
        test(b"a b c' x y z 'd e f'",
            [],
            escape='x'
            )

    # value error, empty quotes str
    with raises(ValueError):
        test("a b c' x y z 'd e f'",
            [],
            quotes=('"', "'", ""),
            )

    # value error, empty quotes bytes
    with raises(ValueError):
        test(b"a b c' x y z 'd e f'",
            [],
            quotes=(b'"', b"'", b""),
            )

    # empty string in multiline_quotes str
    with raises(ValueError):
        test("a b c' x y z 'd e f'",
            [],
            multiline_quotes=('<<', ">>", ""),
            )

    # empty string in multiline_quotes bytes
    with raises(ValueError):
        test(b"a b c' x y z 'd e f'",
            [],
            multiline_quotes=(b'<<', b">>", b""),
            )

    with raises(ValueError):
        test("a b c' x y z 'd e f'",
            [],
            state='"""'
            )

    with raises(ValueError):
        test("a b c' x y z 'd e f'",
            [],
            state='Q'
            )

    with raises(TypeError):
        test("a b c' x y z 'd e f'",
            [],
            state=b"'"
            )

    # repeated markers in quotes
    with raises(ValueError):
        test("a b c' x y z 'd e f'",
            [],
            quotes=('"', "'", '"'),
            )

    # repeated markers in multiline_quotes
    with raises(ValueError):
        test("a b c' x y z 'd e f'",
            [],
            multiline_quotes=('<<', ">>", '<<'),
            )

    # marker appears in both quotes and multiline_quotes
    with raises(ValueError):
        test("a b c' x y z 'd e f'",
            [],
            multiline_quotes=('<<', ">>", '"'),
            )

    # marker appears in both quotes and multiline_quotes
    with raises(ValueError):
        test("a b c' x y z 'd e f'",
            [],
            multiline_quotes=('<<', "'", '"'),
            )

    # initial state is not a quote marker
    with raises(ValueError):
        test("a b c' x y z 'd e f'",
            [],
            state="Z"
            )

    # linebreaks and multiline_quotes
    with raises(SyntaxError):
        test('abc "def\nghi" jkl',
            [],
            )
    with raises(SyntaxError):
        test('abc "defghi" "jk\nl',
            [],
            )

    # regression: the mid-stream unterminated-string error was
    # missing its f-prefix, so the message literally said
    # "{s!r}" instead of showing the offending string.  (the
    # end-of-string twin always had the f.)
    with raises(SyntaxError) as cm:
        list(big.split_quoted_strings('abc "def\nghi" jkl'))
    assert '{s!r}' not in str(cm.exception)
    assert repr('abc "def\nghi" jkl') in str(cm.exception)
    with raises(SyntaxError) as cm:
        list(big.split_quoted_strings('abc "defghi" "jk\nl'))
    assert '{s!r}' not in str(cm.exception)
    assert repr('abc "defghi" "jk\nl') in str(cm.exception)

    test('abc """def\nghi""" jkl',
        [('', 'abc ', ''), ('"""', 'def\nghi', '"""'), ('', ' jkl', '')],
        multiline_quotes=('"""',)
        )

    test('abc """def\vghi""" jkl',
        [('', 'abc ', ''), ('"""', 'def\vghi', '"""'), ('', ' jkl', '')],
        multiline_quotes=('"""',)
        )

    # regression: escape didn't protect multiline_quotes--an
    # escaped multiline delimiter closed the string.  ('''/"""
    # worked only by accident: the '"' in quotes contributed a
    # \" separator that happened to shield \""".)  escape now
    # works in both quotes and multiline_quotes, and shields
    # exactly one following character, like backslash in Python.
    test('say <<<x \\<<< y<<< end',
        [('', 'say ', ''), ('<<<', 'x \\<<< y', '<<<'), ('', ' end', '')],
        quotes=('"',), multiline_quotes=('<<<',)
        )
    # pure multiline, no regular quotes contributing separators
    test('"""ab\\""" cd""" end',
        [('"""', 'ab\\""" cd', '"""'), ('', ' end', '')],
        quotes=(), multiline_quotes=('"""',)
        )
    # the shared-prefix accident still works, now on purpose
    test('say """x \\""" y""" end',
        [('', 'say ', ''), ('"""', 'x \\""" y', '"""'), ('', ' end', '')],
        multiline_quotes=('"""',)
        )
    # first-character semantics with a multi-character regular
    # quote: inside a << string, \< escapes one character, so
    # \<<< is an escaped < followed by a live << close--just
    # like Python's \""" inside a """ string.
    test('a <<x \\<< y\\<<< b<< c',
        [('', 'a ', ''), ('<<', 'x \\<< y\\<', '<<'), ('', ' b', ''), ('<<', ' c', '')],
        quotes=('<<',)
        )

    # the exotic Unicode paragraph separator!
    # note: this test will automatically skip trying the bytes version.
    test('abc """def\u2029ghi""" jkl',
        [('', 'abc ', ''), ('"""', 'def\u2029ghi', '"""'), ('', ' jkl', '')],
        multiline_quotes=('"""',)
        )

    test('abc "def ghi" jkl',
        [('', 'abc ', ''), ('"', 'def ghi', '"'), ('', ' jkl', '')],
        multiline_quotes=('"""',)
        )

    # can't have the same mark in both quotes and multiline_quotes
    with raises(ValueError):
        test('abc "def\nghi" jkl',
            [],
            multiline_quotes=('"',)
            )


def test_split_delimiters():

    D = big.Delimiter
    def SDV(t, o, cl, ch):  return big.SplitDelimitersValue(t, o, cl, ch)

    assert repr(SDV('t', 'o', 'cl', 'ch')) == "SplitDelimitersValue(text='t', open='o', close='cl', change='ch')"

    def test(s, expected, *, delimiters=big.split_delimiters_default_delimiters, state=()):
        empty = ''
        for i in range(2):
            got = tuple(big.split_delimiters(s, delimiters=delimiters, state=state))

            flattened = []
            for t in got:
                flattened.extend(t)
            s2 = empty.join(flattened)
            assert s == s2

            if 0:
                import pprint
                print("\n\n")
                print("-"*72)
                print("expected:")
                pprint.pprint(expected)
                print("\n\n")
                print("got:")
                pprint.pprint(got)
                print("\n\n")

            assert expected == got

            if not i:
                s = to_bytes(s)
                expected = to_bytes(expected)
                empty = b''
                if state:
                    state = to_bytes(state)
                if delimiters == big.split_delimiters_default_delimiters:
                    delimiters = big.split_delimiters_default_delimiters_bytes
                elif delimiters:
                    delimiters = to_bytes(delimiters)

    test('a[x] = foo("howdy (folks)\\n", {1:2, 3:4})',
        (
            SDV('a',                '[',  '', ''),
            SDV('x',                 '', ']', ''),
            SDV(' = foo',           '(',  '', ''),
            SDV('',                 '"',  '', ''),
            SDV('howdy (folks)\\n',  '', '"', ''),
            SDV(', ',               '{',  '', ''),
            SDV('1:2, 3:4',          '', '}', ''),
            SDV('',                  '', ')', ''),
        ),
        )

    with raises(TypeError):
        test('a[x] = foo("howdy (folks)\\n", {1:2, 3:4})',
            (
                SDV('a',                '[',  '', ''),
                SDV('x',                 '', ']', ''),
                SDV(' = foo',           '(',  '', ''),
                SDV('',                 '"',  '', ''),
                SDV('howdy (folks)\\n',  '', '"', ''),
                SDV(', ',               '{',  '', ''),
                SDV('1:2, 3:4',          '', '}', ''),
                SDV('',                  '', ')', ''),
            ),
            delimiters=big.split_delimiters_default_delimiters_bytes,
            )

    test('a[[[z]]]{{{{q}}}}[{[{[{[{z}]}]}]}]!',
        (
            SDV('a', '[',  '', ''),
            SDV('',  '[',  '', ''),
            SDV('',  '[',  '', ''),
            SDV('z',  '', ']', ''),
            SDV('',   '', ']', ''),
            SDV('',   '', ']', ''),
            SDV('',  '{',  '', ''),
            SDV('',  '{',  '', ''),
            SDV('',  '{',  '', ''),
            SDV('',  '{',  '', ''),
            SDV('q',  '', '}', ''),
            SDV('',   '', '}', ''),
            SDV('',   '', '}', ''),
            SDV('',   '', '}', ''),
            SDV('',  '[',  '', ''),
            SDV('',  '{',  '', ''),
            SDV('',  '[',  '', ''),
            SDV('',  '{',  '', ''),
            SDV('',  '[',  '', ''),
            SDV('',  '{',  '', ''),
            SDV('',  '[',  '', ''),
            SDV('',  '{',  '', ''),
            SDV('z',  '', '}', ''),
            SDV('',   '', ']', ''),
            SDV('',   '', '}', ''),
            SDV('',   '', ']', ''),
            SDV('',   '', '}', ''),
            SDV('',   '', ']', ''),
            SDV('',   '', '}', ''),
            SDV('',   '', ']', ''),
            SDV('!',  '',  '', ''),
        ),
        delimiters=None,
        )

    # test state
    test('x"], foo);}',
        (
            SDV('x',     '', '"', ''),
            SDV('',      '', ']', ''),
            SDV(', foo', '', ')', ''),
            SDV(';',     '', '}', ''),
        ), state='{(["')

    with raises(ValueError):
        test('abc', None, state='[{"(')

    with raises(ValueError):
        test('abc', None, state='{(x[')

    # test escapes
    test(r"foo('ab\'cd')",
        (
            SDV( 'foo',    '(', '' , ''),
            SDV( '',       "'", '' , ''),
            SDV(r"ab\'cd", '',  "'", ''),
            SDV( '',       '',  ')', ''),
        ),
        )

    test(r'foo("ab\"cd")',
        (
            SDV( 'foo',    '(', '' , ''),
            SDV( '',       '"', '' , ''),
            SDV(r'ab\"cd', '',  '"', ''),
            SDV( '',       '',  ')', ''),
        ),
        )

    # single-quoted strings by default don't allow linebreaks inside
    with raises(SyntaxError):
        test('foo("ab\ncd")', [])
    with raises(SyntaxError):
        test("foo('ab\ncd')", [])
    # but the others delimiters permit it
    test('foo([{ab\ncd}])',
        (
            SDV('foo',    '(', '' , ''),
            SDV('',       '[', '' , ''),
            SDV('',       '{', '' , ''),
            SDV('ab\ncd', '',  '}', ''),
            SDV('',       '',  ']', ''),
            SDV('',       '',  ')', ''),
        ))

    # test multi-character delimiters and escape
    test('abc^Sdef<<gh><i>>klm^Xno**^Xp*^Xqrs^Qtuv<<wxy>>z',
        (
            SDV('abc',      '^S', '',   ''),
            SDV('def',      '<<', '',   ''),
            SDV('gh><i',    '',   '>>', ''),
            SDV('klm',      '^X', '',   ''),
            SDV('no**^Xp*', '',   '^X', ''),
            SDV('qrs',      '',   '^Q', ''),
            SDV('tuv',      '<<', '',   ''),
            SDV('wxy',      '',   '>>', ''),
            SDV('z',        '',   '',   ''),
            ),
        delimiters = {
            '^S': D('^Q'),
            '<<': D('>>'),
            '^X': D('^X', escape='**', quoting=True),
            },
        )

    # torture test time!
    # split_delimiters uses multisplit, which always returns
    # the largest delimiter.  but what if we have delimiters
    # that are substrings of other delimiters?  what if we
    # have delimiters that overlap?  multisplit is greedy,
    # it will always want to split on the larger string.

    # torture test #1:
    # current close delimiter is a prefix of another delimiter.
    cruel_delimiters_1 = {
        '(': D(')'),
        '[': D(']'),
        '[(': D(')]'),
    }
    #          vv -- multisplit will split here
    test('a[b(c)]',
        #      ^ --- but really we want to split here
        #       ^ -- and here
        (
            SDV('a', '[', '',   ''),
            SDV('b', '(', '',   ''),
            SDV('c', '',  ')', ''),
            SDV('',  '',  ']', ''),
            ),
        delimiters = cruel_delimiters_1,
        )

    # torture test #2:
    # current escape string is a prefix of another delimiter.
    cruel_delimiters_2 = {
        '(': D(')', escape=']', quoting=True),
        '[': D(']'),
        '[(': D(')]'),
    }
    #          vv -- multisplit will split here
    test('a[b(c]))]',
        #      ^ --- but really we want to split here
        #       ^ -- and here
        (
            SDV('a',   '[', '',  ''),  # now in '['
            SDV('b',   '(', '',  ''),  # now in '('
            SDV('c])', '',  ')', ''), # ] escapes ), and then second ) closes
            SDV('',    '',  ']', ''), # final ] closes
            ),
        delimiters = cruel_delimiters_2,
        )

    # torture test #3:
    # we have a set of quoting delimiters, and
    # random garbage that happens to combine with
    # our close delimiter to form another overlapping
    # delimiter.
    cruel_delimiters_3 = {
        '(': D(')'),
        '[(': D(')]'),
        '<[': D(']>', quoting=True, escape='**'),
    }
    #         vv --- multisplit will split here
    test('a<[b)]>',
        #     ^ ---- but really we want to split here
        #      ^^ -- and here
        (
            SDV('a',  '<[', '',   ''),
            SDV('b)', '',   ']>', ''),
            ),
        delimiters = cruel_delimiters_3,
        )

    # torture test #4:
    # we want to escape our ending quote mark,
    # followed by another
    cruel_delimiters_4 = {
        '<': D('>', quoting=True, escape='\\'),
        '<<': D('>>'),
    }
    #          vv --- multisplit will split here
    test('a<b\\>>',
        #      ^ --- but really we want to split here
        #       ^ -- and here
        (
            SDV('a',    '<',  '',  ''),
            SDV('b\\>', '',   '>', ''),
            ),
        delimiters = cruel_delimiters_4,
        )

    # torture test #5:
    # our current escape string is the prefix of
    # another delimiter
    cruel_delimiters_5 = {
        '<': D('>', quoting=True, escape='\\'),
        'Q': D('\\>'),
    }
    #        vvv --- multisplit will split here
    test('a<b\\>>',
        #    ^^ ---- but really we want to split here
        #      ^ -- and here
        (
            SDV('a',    '<', '',   ''),
            SDV('b\\>', '',   '>', ''),
            ),
        delimiters = cruel_delimiters_5,
        )

    with raises(SyntaxError):
        test('a[3)', None)
    with raises(SyntaxError):
        test('a{3]', None)
    with raises(SyntaxError):
        test('a(3}', None)

    with raises(ValueError):
        test('delimiters is empty', None, delimiters={})
    with raises(TypeError):
        test('delimiter is abc (huh!)', None, delimiters={'a': 'abc'})
    with raises(TypeError):
        test('str/bytes mismatch', None, delimiters={'a': big.Delimiter(close=b'b')})
    with raises(TypeError):
        test('str/bytes mismatch', None, delimiters={'a': big.Delimiter(close='x', escape=b'b', quoting=True)})
    with raises(TypeError):
        test('bytes/str mismatch', None, delimiters={b'a': big.Delimiter(close='b')})
    with raises(TypeError):
        test('bytes/str mismatch', None, delimiters={b'a': big.Delimiter(close=b'x', escape='b', quoting=True)})
    with raises(ValueError):
        test('no delimiters?!', None, delimiters={})
    with raises(ValueError):
        test(b'no delimiters?!', None, delimiters={})
    with raises(ValueError):
        test('open delimiters is a <backslash>', None, delimiters={'\\': big.Delimiter(close='z')})
    with raises(ValueError):
        test(b'open delimiters is a bytes <backslash>', None, delimiters={b'\\': big.Delimiter(close=b'z')})
    with raises(ValueError):
        test('close delimiter is a <backslash>', None, delimiters={'z': big.Delimiter(close='\\')})
    with raises(ValueError):
        test('delimiters contains <angle> <brackets> as both open and close delimiters', None, delimiters={'<': big.Delimiter(close='x'), '>': big.Delimiter(close='<')})
    with raises(ValueError):
        test('delimiters contains <angle> <brackets> as both open and close delimiters', None, delimiters={'<': big.Delimiter(close='>'), 'x': big.Delimiter(close='<'), '{': big.Delimiter(close='}'), 'q': big.Delimiter(close='{')})
    with raises(ValueError):
        test('if quoting is false, escape must be false', None, delimiters={'<': big.Delimiter(close='x', quoting=False, escape='z')})

    with raises(SyntaxError):
        test('by default quote marks are now single-line only "ab\n", test 1, complete quoted string', None, )
    with raises(SyntaxError):
        test('by default quote marks are now single-line only "ab\n, test 2, unterminated quoted string', None, )
    with raises(SyntaxError):
        test('text ends with "escape string\\', None, )

    # the yields transition promised in the 0.12.5 release
    # notes completed in 0.14: split_delimiters always yields
    # four values.  the yields parameter survives for one more
    # year, deprecated, accepting only 4--so code that
    # dutifully migrated to yields=4 keeps working.
    got = tuple(big.split_delimiters('ab[c]', yields=4))
    assert got == tuple(big.split_delimiters('ab[c]'))
    for bad in (3, None, 48, '4'):
        with raises(ValueError):
            big.split_delimiters('ab[c(3)]', yields=bad)

    # the value's deprecated "yields" attribute likewise survives
    # for one more year; it now always reports 4.
    for value in got:
        assert value.yields == 4

    # regression: a foreign token that *starts with* a valid
    # open delimiter used to raise SyntaxError instead of
    # opening the delimiter.  here 'xz' (the close of 'a') is
    # a token; in the initial state it should be handled as
    # 'x' (which opens a delimiter) followed by a resplit.
    test('qxzy',
        (
            SDV('q', 'x',  '', ''),
            SDV('z',  '', 'y', ''),
        ),
        delimiters={'x': D(close='y'), 'a': D(close='xz')},
        )
    # same collision against the *close* of the current state:
    # inside 'a', the foreign token 'xz' starts with 'x',
    # which pops.  (this case always worked--it's the original
    # truncate-and-resplit fixup--pinned here for symmetry.)
    test('a b xz c',
        (
            SDV('',     'a',  '', ''),
            SDV(' b ',   '', 'x', ''),
            SDV('z c',   '',  '', ''),
        ),
        delimiters={'a': D(close='x'), 'q': D(close='xz')},
        )

    # close may be a tuple of alternatives: any one of them
    # closes the delimiter.  (new in 0.14; how line comments
    # end at either '\n' or '\r'.)
    for s, closer in (('a<b|c', '|'), ('a<b>c', '>')):
        test(s,
            (
                SDV('a', '<',    '', ''),
                SDV('b',  '', closer, ''),
                SDV('c',  '',    '', ''),
            ),
            delimiters={'<': D(close=('|', '>'))},
            )

    # a single close and a 1-tuple close mean the same thing,
    # and compare (and hash) equal
    assert D('x') == D(('x',))
    assert hash(D('x')) == hash(D(('x',)))
    assert D(('|', '>')).closes == ('|', '>')
    assert D('x').closes == ('x',)

    with raises(ValueError):
        D(())                # no alternatives
    with raises(ValueError):
        D(('x', 'x'))        # repeated alternative
    with raises(TypeError):
        D(('x', b'y'))       # mixed types
    with raises(ValueError):
        D(('x', ''))         # empty alternative
    with raises(TypeError):
        D(42)                # not a string or iterable

    # testing on the Delimiter class itself
    d = big.Delimiter(close='x')
    assert d == big.Delimiter(d)
    d = big.Delimiter(close='q', quoting=True, escape='>')
    assert d == d.copy()

    assert repr(big.Delimiter(close='x', escape='y', multiline=False, quoting=True)) == "Delimiter(close='x', escape='y', multiline=False, quoting=True)"

    with raises(ValueError):
        D(close='x', escape='z', quoting=False, multiline=True)
    with raises(ValueError):
        D(close='x', escape='z', quoting=False, multiline=False)
    with raises(ValueError):
        D(close='\\')
    with raises(ValueError):
        D(close=b'\\')
    # invariant: one of multiline or quoting must be true.
    with raises(ValueError):
        D(close=')', multiline=False, quoting=False)
    with raises(ValueError):
        test('abcde', [],
        delimiters={'\\': D(close='x')},
        )

    # Delimiter objects are now read-only
    d = D(close='x')
    with raises(AttributeError):
        d.close = 'y'
    with raises(AttributeError):
        d.escape = '\\'
    with raises(AttributeError):
        d.quoting = True
    with raises(AttributeError):
        d.quoting = True

    # test that split_delimiters honors string subclasses
    SS = StrSubclass
    for segment, open, close, change in big.split_delimiters(SS('a[x] = foo("howdy (folks)\\n", {1:2, 3:4})'), big.python_delimiters):
        assert isinstance(segment, SS)
        assert isinstance(open, SS)
        assert isinstance(close, SS)
        assert isinstance(change, SS)


def test_delimiter_nested_literal_change():
    # the Delimiter parameters that make grammars like
    # python_delimiters expressible as pure data (new in 0.14):
    #   nested  - delimiters live *inside* this one
    #   literal - tokens that are plain text inside this one
    #   change  - tokens that change what the inside means,
    #             without pushing a new delimiter
    D = big.Delimiter
    def SDV(t, o, cl, ch):  return big.SplitDelimitersValue(t, o, cl, ch)

    def test(s, expected, *, delimiters):
        for i in range(2):
            got = tuple(big.split_delimiters(s, delimiters=delimiters))
            assert expected == got
            if not i:
                s = to_bytes(s)
                expected = to_bytes(expected)
                delimiters = to_bytes(delimiters)

    # a miniature f-string-alike: a quoting delimiter with a
    # live nested delimiter, a literal token, and a two-phase
    # change chain inside the nested delimiter.
    def build_mini_grammar():
        spec = D('>', quoting=True)
        tag = D('>', change={':': spec})
        quoted = D('"', quoting=True, nested={'<': tag}, literal=('<<',))
        return {'"': quoted, '(': D(')')}

    # inside the quotes: '<' opens a tag (the exception to
    # quoting), ':' inside the tag changes to the spec
    # sub-language, and one '>' ends both.  '(' stays inert
    # inside the quotes--quoting still quotes.
    test('a"b<c:d>e(f"g',
        (
            SDV('a',   '"',  '', ''),
            SDV('b',   '<',  '', ''),
            SDV('c',    '',  '', ':'),
            SDV('d',    '', '>', ''),
            SDV('e(f',  '', '"', ''),
            SDV('g',    '',  '', ''),
        ),
        delimiters=build_mini_grammar(),
        )

    # '<<' is literal text inside the quotes, even though '<'
    # is meaningful there
    test('a"b<<c"d',
        (
            SDV('a',     '"',  '', ''),
            SDV('b<<c',   '', '"', ''),
            SDV('d',      '',  '', ''),
        ),
        delimiters=build_mini_grammar(),
        )

    # nested on a *non-quoting* delimiter overrides the
    # grammar's top-level definition: inside '<', '(' closes
    # with ']' instead of ')'
    test('a(b)c<d(e]f>g',
        (
            SDV('a', '(',  '', ''),
            SDV('b',  '', ')', ''),
            SDV('c', '<',  '', ''),
            SDV('d', '(',  '', ''),
            SDV('e',  '', ']', ''),
            SDV('f',  '', '>', ''),
            SDV('g',  '',  '', ''),
        ),
        delimiters={'<': D('>', nested={'(': D(']')}), '(': D(')')},
        )

    # a cyclic grammar: two quoting delimiters, each the
    # exception to the other's quoting.  built by assignment,
    # after construction--the reason nested and change are
    # assignable.
    def build_cyclic_grammar():
        x = D('>', quoting=True)
        y = D(']', quoting=True, nested={'<': x})
        x.nested = {'[': y}
        return {'<': x}

    test('<a[b<c>d]e>',
        (
            SDV('',  '<',  '', ''),
            SDV('a', '[',  '', ''),
            SDV('b', '<',  '', ''),
            SDV('c',  '', '>', ''),
            SDV('d',  '', ']', ''),
            SDV('e',  '', '>', ''),
        ),
        delimiters=build_cyclic_grammar(),
        )

    # equality is deep, and cycle-safe: two independently
    # built copies of the cyclic grammar compare equal...
    assert build_cyclic_grammar() == build_cyclic_grammar()
    # ...and hash equal (hashing is shallow, which is
    # consistent: deep-equal implies shallow-equal)
    a = build_cyclic_grammar()['<']
    b = build_cyclic_grammar()['<']
    assert hash(a) == hash(b)
    # a deep difference is detected through the cycle
    c = build_cyclic_grammar()['<']
    c.nested['['].nested = {'<': c, 'q': D('x')}
    assert a != c

    # compiling a grammar freezes its Delimiters--all of them,
    # nested ones included
    x = build_cyclic_grammar()['<']
    y = x.nested['[']
    list(big.split_delimiters('<a>', {'<': x}))
    for d in (x, y):
        with raises(ValueError):
            d.nested = {}
        with raises(ValueError):
            d.literal = ()
        with raises(ValueError):
            d.change = {}
    # ...but a copy is unfrozen
    unfrozen = x.copy()
    unfrozen.literal = ('<<',)
    assert unfrozen.literal == ('<<',)

    # nested and change are read-only views; you modify them
    # by assignment (so validation always runs)
    d = D('>', nested={'(': D(']')})
    with raises(TypeError):
        d.nested['['] = D(']')
    with raises(TypeError):
        d.change[':'] = D('>')

    # validation
    with raises(ValueError):
        # None values in nested are reserved for future use
        D('>', nested={'(': None})
    with raises(TypeError):
        D('>', nested={'(': ']'})           # not a Delimiter
    with raises(ValueError):
        D('>', nested={'>': D(']')})        # nested open == close
    with raises(TypeError):
        D('>', nested={b'(': D(']')})       # type mismatch
    with raises(ValueError):
        # a change target must share its host's close
        D('>', change={':': D(']')})
    with raises(ValueError):
        D('>', change={'>': D('>')})        # change token == close
    with raises(TypeError):
        D('>', change={':': 'spec'})        # not a Delimiter
    # like close, literal accepts a single token or an
    # iterable of them, and normalizes to a tuple
    assert D('"', quoting=True, literal='<<').literal == ('<<',)
    assert D('"', quoting=True, literal='<<') == D('"', quoting=True, literal=('<<',))
    with raises(ValueError):
        D('"', quoting=True, literal=('<', '<'))    # repeated token
    with raises(ValueError):
        D('"', quoting=True, literal=('"',))    # literal == close
    with raises(ValueError):
        D('"', quoting=True, escape='\\', literal=('\\',))  # literal == escape

    # tokens can't be empty, anywhere
    with raises(ValueError):
        D('>', nested={'': D(']')})
    with raises(ValueError):
        D('"', quoting=True, literal=('',))
    with raises(ValueError):
        D('>', change={'': D('>')})

    # assigning None to nested or change clears them
    d = D('>', nested={'(': D(']')}, change={':': D('>')})
    d.nested = None
    d.change = None
    assert dict(d.nested) == {}
    assert dict(d.change) == {}

    # identity is the equality fast path
    d = D('>')
    assert d == d

    # equality descends into change targets
    def build_changer(spec_quoting):
        return D('>', change={':': D('>', quoting=spec_quoting)})
    assert build_changer(True) == build_changer(True)
    assert build_changer(True) != build_changer(False)

    # equality returns NotImplemented for foreign types,
    # so == falls back to identity
    assert D('>') != 5


def test_lines_deprecation_warning():
    # the lines pipeline is deprecated (removal no sooner than
    # March 2027) and, as of 0.14, says so at runtime: one
    # DeprecationWarning from the lines constructor covers the
    # whole pipeline.  (warnings.warn doesn't halt anything.)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        list(big.lines("a\nb\n"))
    deprecations = [x for x in w if issubclass(x.category, DeprecationWarning)]
    assert len(deprecations) == 1
    assert "Migrating from lines to string" in str(deprecations[0].message)

def test_lines():

    def L(li, line_number, column_number, line, end=_sentinel, *, leading=None, trailing=None, original=None, **kwargs):
        is_bytes = isinstance(line, bytes)
        empty = b'' if is_bytes else ''

        if end is _sentinel:
            end = b'\n' if is_bytes else '\n'

        if leading is None:
            leading = empty

        if trailing is None:
            trailing = empty

        if original is None:
            original = leading + line + trailing + end

        return (big.text.LineInfo(li, original, line_number, column_number, end=end, leading=leading, trailing=trailing, **kwargs), line)

    def test(li, expected):

        got = list(li)

        if 0:
            import pprint
            print("\n\n")
            print("-"*72)
            print("expected:")
            pprint.pprint(expected)
            print("\n\n")
            print("got:")
            pprint.pprint(got)
            print("\n\n")
            for e, g in zip(expected, got):
                print(e==g)
            print("\n\n")

        assert expected == got

        for info, line in got:
            copy = info.copy()
            assert info == copy

    i = li = big.lines("a\nb\nc\nd\ne\n")
    test(i,
        [
        L(li, 1, 1, 'a'),
        L(li, 2, 1, 'b'),
        L(li, 3, 1, 'c'),
        L(li, 4, 1, 'd'),
        L(li, 5, 1, 'e'),
        L(li, 6, 1, '', end=''),
        ])


    i = li = big.lines("a\nb\nc\nd\ne\n", clip_linebreaks=False)
    def fix_linebreak(info_and_line):
        info, line = info_and_line
        info.line = info.line[:-1]
        return info_and_line

    test(i,
        [
        fix_linebreak(L(li, 1, 1, 'a\n')),
        fix_linebreak(L(li, 2, 1, 'b\n')),
        fix_linebreak(L(li, 3, 1, 'c\n')),
        fix_linebreak(L(li, 4, 1, 'd\n')),
        fix_linebreak(L(li, 5, 1, 'e\n')),
                      L(li, 6, 1, '', end=''),
        ])

    # you can give lines an iterable of strings,
    # in which case we don't populate "end".
    list_of_lines = [
        'first line',
        '\tsecond line',
        'third line',
        '         ',
        ''
        ]
    i = li = big.lines(list_of_lines)
    i = big.lines_strip(i)
    test(i,
        [
        L(li, 1, 1, 'first line',                        end=''),
        L(li, 2, 9, 'second line', leading='\t',         end=''),
        L(li, 3, 1, 'third line',                        end=''),
        L(li, 4, 1, '',            trailing='         ', end=''),
        L(li, 5, 1, '',                                  end=''),
        ])

    # or! you can give lines an iterable of 2-tuples of strings,
    # in which case the first string is the line and the second is the end.
    list_of_lines_and_eols = [
        ('line 1', '\n'),
        ('hey!  line 2.', '\n'),
        ('the only line with the word eggplant! line 3!', '\n'),
        ('the final line, line 4.', '')
        ]
    i = li = big.lines(list_of_lines_and_eols)
    i = big.lines_grep(i, 'eggplant', invert=True)
    test(i,
        [
        L(li, 1, 1, 'line 1'),
        L(li, 2, 1, 'hey!  line 2.'),
        L(li, 4, 1, 'the final line, line 4.', end=''),
        ])

    # test lines_filter_line_comment_lines
    # note, slight white box testing here:
    # lines_filter_line_comment_lines has different approaches
    # for one comment marker vs more than one.  so, test both.

    i = li = big.lines(b"a\n# ignored\n  # also ignored\n d")
    i = big.lines_filter_line_comment_lines(i, b'#')
    test(i,
        [
        L(li, 1, 1, b'a'),
        L(li, 4, 1, b' d', end=b''),
        ]
        )

    i = li = big.lines(dedent("""
            # comment
            a = b
            // another comment
            c = d
            / not a comment
            /// is a comment!
        ## another comment!
            #! a third comment!
        """).lstrip('\n'))
    i = big.lines_filter_line_comment_lines(i, ('#', '//'))
    test(i,
        [
        L(li, 2, 1, '    a = b'          ),
        L(li, 4, 1, '    c = d'          ),
        L(li, 5, 1, '    / not a comment'),
        L(li, 9, 1, '',                    end=''),
        ])

    # minor regression test--
    # I noticed this was broken right before release
    i = li = big.lines(dedent(b"""
            # comment
            a = b
            // another comment
            c = d
            / not a comment
            /// is a comment!
        ## another comment!
            #! a third comment!
        """).lstrip(b'\n'))
    i = big.lines_filter_line_comment_lines(i, (b'#', b'//'))
    test(i,
        [
        L(li, 2, 1, b'    a = b'          ),
        L(li, 4, 1, b'    c = d'          ),
        L(li, 5, 1, b'    / not a comment'),
        L(li, 9, 1, b'',                    end=b''),
        ])

    i = li = big.lines(dedent("""
        hello yolks
        what do you have to say, champ?
        i like eggs.
        they don't have to be fancy.
        simple scrambled eggs are just fine.
        neggatory!
        whoops, I meant, negatory.
        """).lstrip('\n'))
    i = big.lines_containing(i, "egg")
    test(i,
        [
            L(li, 3, 1, 'i like eggs.'),
            L(li, 5, 1, 'simple scrambled eggs are just fine.'),
            L(li, 6, 1, 'neggatory!'),
        ]
        )

    i = li = big.lines(dedent("""
        hello yolks
        what do you have to say, champ?
        i like eggs.
        they don't have to be fancy.
        simple scrambled eggs are just fine.
        neggatory!
        whoops, I meant, negatory.
        """).lstrip('\n'))
    i = big.lines_containing(i, "egg", invert=True)
    test(i,
        [
            L(li, 1, 1, 'hello yolks'),
            L(li, 2, 1, 'what do you have to say, champ?'),
            L(li, 4, 1, "they don't have to be fancy."),
            L(li, 7, 1, 'whoops, I meant, negatory.'),
            L(li, 8, 1, '', end=''),
        ]
        )

    # it's hard to create an re.Match object in advance
    # that will match the one returned by re.match.
    # so, test for it separately, then remove it from the LineInfo object(s).
    # (we confirm the line should have a match by testing for the presence of a substring.)
    def test_and_remove_lineinfo_match(i, substring, *, invert=False, match='match'):
        l = []
        for t in i:
            info, line = t

            m = getattr(info, match, _sentinel)
            assert m != _sentinel

            if invert:
                assert m is None
                assert substring not in line
            else:
                assert isinstance(m, re_Match)
                assert substring in line

            # now remove the match object for easier testing
            setattr(info, match, None)
            l.append(t)
        return l

    i = li = big.lines(dedent("""
        hello yolks
        what do you have to say, champ?
        i like eggs.
        they don't have to be fancy.
        simple scrambled eggs are just fine.
        neggatory!
        whoops, I meant, negatory.
        """).lstrip('\n'))
    i = big.lines_grep(i, "eg+")
    got = test_and_remove_lineinfo_match(i, "eg")
    test(got,
        [
            L(li, 3, 1, 'i like eggs.'),
            L(li, 5, 1, 'simple scrambled eggs are just fine.'),
            L(li, 6, 1, 'neggatory!'),
            L(li, 7, 1, 'whoops, I meant, negatory.'),
        ]
    )

    i = li = big.lines(dedent("""
        hello yolks
        what do you have to say, champ?
        i like eggs.
        they don't have to be fancy.
        simple scrambled eggs are just fine.
        neggatory!
        whoops, I meant, negatory.
        """).lstrip('\n'))
    i = big.lines_grep(i, "eg+", invert=True, match='quixote')
    got = test_and_remove_lineinfo_match(i, "eg", invert=True, match='quixote')
    test(got,
        [
            L(li, 1, 1, 'hello yolks', quixote=None),
            L(li, 2, 1, 'what do you have to say, champ?', quixote=None),
            L(li, 4, 1, "they don't have to be fancy.", quixote=None),
            L(li, 8, 1, '', end='', quixote=None),
        ]
        )

    with raises(ValueError):
        i = li = big.lines(dedent("""
            hello yolks
            what do you have to say, champ?
            i like eggs.
            they don't have to be fancy.
            simple scrambled eggs are just fine.
            neggatory!
            whoops, I meant, negatory.
            """).lstrip('\n'))
        big.lines_grep(i, "eg+", invert=True, match='not a valid identifier')

    i = li = big.lines(dedent("""
        cormorant
        firefox
        alligator
        diplodocus
        elephant
        giraffe
        barracuda
        hummingbird
        """).strip('\n'))
    i = big.lines_sort(i)
    test(i,
        [
            L(li, 3, 1, 'alligator'),
            L(li, 7, 1, 'barracuda'),
            L(li, 1, 1, 'cormorant'),
            L(li, 4, 1, 'diplodocus'),
            L(li, 5, 1, 'elephant'),
            L(li, 2, 1, 'firefox'),
            L(li, 6, 1, 'giraffe'),
            L(li, 8, 1, 'hummingbird', end=''),
        ]
        )

    i = li = big.lines(dedent("""
        cormorant
        firefox
        alligator
        diplodocus
        elephant
        giraffe
        barracuda
        hummingbird
        """).strip('\n'))
    i = big.lines_sort(i, reverse=True)
    test(i,
        [
            L(li, 8, 1, 'hummingbird', end=''),
            L(li, 6, 1, 'giraffe'),
            L(li, 2, 1, 'firefox'),
            L(li, 5, 1, 'elephant'),
            L(li, 4, 1, 'diplodocus'),
            L(li, 1, 1, 'cormorant'),
            L(li, 7, 1, 'barracuda'),
            L(li, 3, 1, 'alligator'),
        ]
        )

    i = li = big.lines(dedent("""
        cormorant
        firefox
        alligator
        diplodocus
        elephant
        giraffe
        barracuda
        hummingbird
        """).strip('\n'))
    i = big.lines_sort(li, key=lambda t:t[1][1:]) # sort by second letter onward
    test(i,
        [
            L(li, 7, 1, 'barracuda'),
            L(li, 4, 1, 'diplodocus'),
            L(li, 6, 1, 'giraffe'),
            L(li, 2, 1, 'firefox'),
            L(li, 5, 1, 'elephant'),
            L(li, 3, 1, 'alligator'),
            L(li, 1, 1, 'cormorant'),
            L(li, 8, 1, 'hummingbird', end=''),
        ]
        )

    i = li = big.lines(
        "    a = b  \n"
        "    c = d     \n"
        )
    i = big.lines_rstrip(i)
    test(i,
        [
        L(li, 1, 1, '    a = b', trailing='  '),
        L(li, 2, 1, '    c = d', trailing='     '),
        L(li, 3, 1, '',          end=''),
        ])

    i = li = big.lines(
        "QXYXYQa = bXY\n"
        "XYQQXYXYc = dQQQQ\n"
        )
    i = big.lines_rstrip(i, separators=('Q', 'XY'))
    test(i,
        [
        L(li, 1, 1, 'QXYXYQa = b',   trailing='XY'),
        L(li, 2, 1, 'XYQQXYXYc = d', trailing='QQQQ'),
        L(li, 3, 1, '',              end=''),
        ])

    i = li = big.lines(
        "    a = b  \n"
        "      c = d     \n"
        "   \n"
        )
    i = big.lines_strip(i)
    test(i,
        [
        L(li, 1, 5, 'a = b', leading='    ',   trailing='  '),
        L(li, 2, 7, 'c = d', leading='      ', trailing='     '),
        L(li, 3, 1, '',                        trailing='   '),
        L(li, 4, 1, '', end=''),
        ])

    i = li = big.lines(
        "QXYXYQa = bXY\n"
        "XYQQXYXYc = dQQQQ\n"
        'QXYQQXYXYQ\n'
        )
    i = big.lines_strip(i, separators=('Q', 'XY'))
    test(i,
        [
        L(li, 1, 7, 'a = b', leading='QXYXYQ',   trailing='XY'),
        L(li, 2, 9, 'c = d', leading='XYQQXYXY', trailing='QQQQ'),
        L(li, 3, 1, '',                          trailing='QXYQQXYXYQ'),
        L(li, 4, 1, '',      end=''),
        ])

    # test funny separators for lines_strip,
    # *and* multiple calls to clip_leading and clip_trailing
    i = li = lines = big.text.lines('xxxA B C Dyyy\nyyyE F G Hzzz\nxyzI J K Lyzx')
    i = big.text.lines_strip(i, ('x', '?'))
    i = big.text.lines_strip(i, ('y', '!'))
    i = big.text.lines_strip(i, ('z', '.'))
    test(i,
        [
        L(li, 1, 4, 'A B C D',  leading='xxx', trailing='yyy'),
        L(li, 2, 4, 'E F G H',  leading='yyy', trailing='zzz'),
        L(li, 3, 4, 'I J K Ly', leading='xyz', trailing='zx', end=''),
        ]
        )

    # note: dedent is doing us a favor, ensuring that the whitespace-only lines are empty
    i = li = big.lines(
        "\n"
        "    a = b\n"
        "\n"
        "\n"
        "    c = d\n"
        "\n"
        )
    i = big.lines_filter_empty_lines(i)
    test(i,
        [
        L(li, 2, 1, '    a = b'),
        L(li, 5, 1, '    c = d'),
        ])

    i = li = big.lines(
        "\tfirst line\n"
        "\t\tsecond line\n"
        "  \tthird line\n",
        tab_width=8)
    i = big.lines_convert_tabs_to_spaces(i)
    test(i,
        [
            L(li, 1, 1, "        first line",          original="\tfirst line\n"),
            L(li, 2, 1, "                second line", original="\t\tsecond line\n"),
            L(li, 3, 1, "        third line",          original="  \tthird line\n"),
            L(li, 4, 1, "",                            end=''),
        ])

    # no quote marks defined (the default)
    i = li = big.lines(dedent("""
        for x in range(5): # this is a comment
            print("# this is quoted", x)
            print("") # this "comment" is useless
            print(no_comments_or_quotes_on_this_line)
            both//on this line#dawg
            and#also on this//line
          torture////1
         tort-ture######2
        """).lstrip('\n'))
    i = big.lines_strip_line_comments(i, ("#", "//"))
    test(i,
        [
            L(li, 1, 1, 'for x in range(5): ', trailing='# this is a comment',),
            L(li, 2, 1, '    print("',         trailing='# this is quoted", x)'),
            L(li, 3, 1, '    print("") ',      trailing='# this "comment" is useless',),
            L(li, 4, 1, '    print(no_comments_or_quotes_on_this_line)'),
            L(li, 5, 1, '    both',            trailing='//on this line#dawg'),
            L(li, 6, 1, '    and',             trailing='#also on this//line'),
            L(li, 7, 1, '  torture',           trailing='////1'),
            L(li, 8, 1, ' tort-ture',          trailing='######2'),
            L(li, 9, 1, '', end=''),
        ])

    # test specifying quotes as a string
    i = li = big.lines(dedent("""
        for x in range(5): # this is my exciting comment
            print("# this is quoted", x)
            print("") # this "comment" is useless
            print(no_comments_or_quotes_on_this_line)
        """).lstrip('\n'))
    i = big.lines_strip_line_comments(i, ("#", "//"), quotes='"\'')
    test(i,
        [
            L(li, 1, 1, 'for x in range(5): ', trailing='# this is my exciting comment'),
            L(li, 2, 1, '    print("# this is quoted", x)'),
            L(li, 3, 1, '    print("") ', trailing='# this "comment" is useless'),
            L(li, 4, 1, '    print(no_comments_or_quotes_on_this_line)'),
            L(li, 5, 1, '', end=''),
        ])

    i = li = big.lines(dedent("""
        for x in range(5): # this is my exciting comment
            print("# this is quoted", x)
            print("") # this "comment" is useless
            print(no_comments_or_quotes_on_this_line)
            print("#which is the comment?", w #z )
            print("//which is the comment?", x // 4Q2 )
            print("test without whitespace, and extra comment chars 1", y####artie deco )
            print("test without whitespace, and extra comment chars 2", z///////chinchilla the wookie monster )
        """).lstrip('\n'))
    i = big.lines_strip_line_comments(i, ("#", "//"), quotes=('"', "'",))
    i = big.lines_rstrip(i)
    test(i,
        [
            L(li, 1, 1, 'for x in range(5):', trailing=' # this is my exciting comment'),
            L(li, 2, 1, '    print("# this is quoted", x)'),
            L(li, 3, 1, '    print("")', trailing=' # this "comment" is useless'),
            L(li, 4, 1, '    print(no_comments_or_quotes_on_this_line)'),
            L(li, 5, 1, '    print("#which is the comment?", w', trailing=' #z )'),
            L(li, 6, 1, '    print("//which is the comment?", x', trailing=' // 4Q2 )'),
            L(li, 7, 1, '    print("test without whitespace, and extra comment chars 1", y', trailing='####artie deco )'),
            L(li, 8, 1, '    print("test without whitespace, and extra comment chars 2", z', trailing='///////chinchilla the wookie monster )'),
            L(li, 9, 1, '', end=''),
        ])

    # test multiline
    # test specifying line comment markers as a string, and only one quote mark
    i = li = big.lines(dedent("""
        for x in range(5): # this is my exciting comment
            print('''
            this is a multiline string
            does this line have a comment? # no!
            ''') > but here's a comment
            print("just checking, # here too") # here is another comment
        """).lstrip('\n'))
    i = big.lines_strip_line_comments(i, "#>", quotes='"', multiline_quotes=("'''",))
    test(i,
        [
            L(li, 1, 1, 'for x in range(5): ',                     trailing='# this is my exciting comment',),
            L(li, 2, 1, "    print('''"),
            L(li, 3, 1, "    this is a multiline string"),
            L(li, 4, 1, "    does this line have a comment? # no!"),
            L(li, 5, 1, "    ''') ",                               trailing="> but here's a comment"),
            L(li, 6, 1, '    print("just checking, # here too") ', trailing="# here is another comment"),
            L(li, 7, 1, '', end=''),
        ])

    # invalid comment characters
    with raises(ValueError):
        test(big.lines_strip_line_comments(big.lines("a\nb\n"), None), [])

    # unterminated single-quotes across lines
    with raises(SyntaxError):
        test(big.lines_strip_line_comments(big.lines("foo 'bar\n' bat 'zzz'"), ("#", '//',), quotes="'"), [])

    # check that the exception has the right column number
    sentinel = object()
    result = sentinel
    try:
        # this should throw an exception, result should not be written to here.
        result = list(big.lines_strip_line_comments(big.lines("\nfoo\nbar 'bat' baz 'cinco\n' doodle 'zzz'"), ("#", '//',), quotes="'"))
    except SyntaxError as e:
        assert str(e).startswith("Line 3 column 15:")
        assert str(e).endswith("'")
    assert result == sentinel

    # unterminated single-quotes at the end
    with raises(SyntaxError):
        test(big.lines_strip_line_comments(big.lines("foo 'bar' bat 'zzz"), ("#", '//',), quotes=("'",)), [])

    # unterminated triple-quotes at the end
    with raises(SyntaxError):
        test(big.lines_strip_line_comments(big.lines("foo 'bar' bat '''zzz\nmore lines here\nwait what's happening?"), ("#", '//',), multiline_quotes=("'''",)), [])

    i = li = big.lines(b"a\nb# clipped\n c")
    i = big.lines_strip_line_comments(i, b'#')
    test(i,
        [
        L(li, 1, 1, b'a',),
        L(li, 2, 1, b'b',  trailing=b'# clipped'),
        L(li, 3, 1, b' c', end=b''),
        ]
        )

    i = li = big.lines(b'a\nb"# ignored"\n c')
    i = big.lines_strip_line_comments(i, (b'#',), quotes=(b'"',))
    test(i,
        [
        L(li, 1, 1, b'a'),
        L(li, 2, 1, b'b"# ignored"'),
        L(li, 3, 1, b' c', end=b''),
        ]
        )

    i = li = big.lines(b'a\nb"# ignored"\n c#lipped')
    i = big.lines_strip_line_comments(i, b'#', quotes=b'"')
    test(i,
        [
        L(li, 1, 1, b'a'),
        L(li, 2, 1, b'b"# ignored"'),
        L(li, 3, 1, b' c', trailing=b'#lipped', end=b''),
        ]
        )

    i = li = big.lines(b'a\nb"# ignored\n" c#lipped')
    i = big.lines_strip_line_comments(i, b'#', multiline_quotes=b'"')
    test(i,
        [
        L(li, 1, 1, b'a'),
        L(li, 2, 1, b'b"# ignored'),
        L(li, 3, 1, b'" c', trailing=b'#lipped', end=b''),
        ]
        )

    i = li = big.lines(
        "   \n"
        "    a = b \n"
        "   \n"
        "    # comment line \n"
        "    \n"
        "    \n"
        "    c = d  \n"
        "     \n"
        )
    i = big.lines_strip(i)
    i = big.lines_filter_line_comment_lines(i, '#')
    i = big.lines_filter_empty_lines(i)
    test(i,
        [
        L(li, 2, 5, 'a = b',  leading='    ', trailing=' '),
        L(li, 7, 5, 'c = d', leading='    ', trailing='  '),
        ])

def test_python_delimiters_on_big_source_tree():
    big_root = pathlib.Path(sys.argv[0]).absolute().resolve().parent.parent
    python_delimiters = big.python_delimiters
    for root, dirs, files in os.walk(big_root):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with subtest(path=path):
                    expect_decode_failure = file.startswith("invalid_")
                    try:
                        text = read_python_file(path)
                        assert not (expect_decode_failure), f"failed on {file}"
                    except UnicodeDecodeError as e:
                        assert expect_decode_failure, f"failed on {file}"
                        continue
                    state = []
                    for info, line in lines(text, clip_linebreaks=False):
                        for _, open, close, change in split_delimiters(line, python_delimiters, state=state):
                            if open:
                                state.append(open)
                            elif close:
                                state.pop()

                    # if the file ends with a line that ends with a comment,
                    # we'll "open" a comment and not close it.  therefore,
                    # the only time we should see junk in "state" is if it's
                    # a terminal comment, which means it was on the last line,
                    # which means--
                    if state == ['#']:
                        # the last line we saw ended with the comment.
                        assert line.endswith('#' + _)
                        # open and close and change are all empty.
                        # (we don't get a close='\n' because the file doesn't have one.)
                        assert not (open)
                        assert not (close)
                        assert not (change)
                    else:
                        assert not (state)

                    # also, all the test files in test_encodings
                    # contain either a Unicode chipmunk or an ASCII squirrel
                    if "test_encodings" in str(path):
                        if "ascii" in str(path):
                            assert "Squirrel &o" in text, f"Squirrel not found in {path}!"
                        else:
                            assert "Chipmunk 🐿️" in text, f"Chipmunk not found in {path}!"


def test_python_delimiters_regressions():
    def SDV(t, o, cl, ch): return big.SplitDelimitersValue(t, o, cl, ch)

    def test(s, expected):
        empty = ''
        got = tuple(big.split_delimiters(s, python_delimiters))

        flattened = []
        for t in got:
            flattened.extend(t)
        s2 = empty.join(flattened)
        assert s == s2

        if 0:
            import pprint
            print("\n\n")
            print("-"*72)
            print("expected:")
            pprint.pprint(expected)
            print("\n\n")
            print("got:")
            pprint.pprint(got)
            print("\n\n")

        assert expected == got

    # regression test!  this was broken in 0.12.3 and 0.12.4.
    # it was fixed in 0.12.5.
    #
    # the problem: the ACTION_FLUSH action inside split_delimiters
    # forgot to add the length of the flushed delimiter to consumed.
    # so if we had to resplit, we wouldn't resplit where we should--
    # we'd start a few characters early.
    #
    # I'm writing inline comments below to describe what happened
    # while this was broken.  To recreate the broken behavior,
    # change the code that handles _ACTION_FLUSH so it *doesn't*
    # add the length of the flushed delimiter to consumed.
    # Currently that's done by a line that looks like this:
    #       consumed += len(delimiter)
    test("'{}' 'b'\n",
        (
            # we see the ' and push the dict that handles single-quote state.
            # we add the length of open to consumed.
            SDV('',    "'", '', ''),
            # consumed=1
            # stack = [ "'" ]

            # we see the { and say, oh, we ignore that delimiter, flush it.
            #
            # we append { to the text but DON'T add len(delimiter) to consumed!
            # we've already hit our bug!  consumed is now 1 less than it should be.
            # it should be 2 but it's only 1.
            # still looking for our close delimiter.
            #
            # we see the } and do the same thing--it's a delimiter,
            # we ignore and flush it, we DON'T add its length to consumed.
            # consumed is now 2 less than it should be.
            # it should be 3 but it's only 1.
            # still looking for our close delimiter.
            #
            # we see the ' which is our close delimiter.
            # we pop back to the default state dict.
            # we (correctly, for once!) add len(open) to consumed.
            SDV('{}',  '',  "'", ''),
            # consumed = 2   BUT IT SHOULD BE 4
            # stack = []

            # we see the ' and push the dict that handles single-quote state.
            # we add len(text) and len(open) to consumed.
            SDV(' ',  "'",  '', ''),
            # consumed = 4   BUT IT SHOULD BE 6
            # stack = [ "'" ]

            # we see the b' and oh! we ignore that delimiter, flush it.
            # since it's a multiple character delimiter, we FLUSH 1 AND RESPLIT.
            # we flush the first character of the delimiter, "b",
            # and we return close="'", and we add 2 to consumed.
            SDV('b',  '',     "'", ''),
            # consumed = 6   BUT IT SHOULD BE 8
            # stack = []

            # And here's where we crash.
            # We resplit, starting at offset 6, which is here
            #       v
            # '{}' 'b'\n
            #         ^
            # but it SHOULD be here at offset 8.
            #
            # So, when we had the bug, here we'd erroneously yield
            #     ('', "b'", '')
            # and stack would be [ "b'"]
            #
            # And *then* we'd see the newline, and complain because
            # newline is illegal inside a single-quoted string, kerblam.
            #
            # Thank goodness we fixed the bug!  So now we yield the
            # final, correct value:

            SDV('\n', '', '', ''),
            ),
        )

    # regression: the no-linebreaks-inside-single-quoted-strings
    # rule (documented since 0.12.5!) was only half-enforced:
    # '\r' raised SyntaxError, but '\n' was silently flushed.
    # (the f-string surgery blanketed '\n'-to-flush into every
    # string state, clobbering the single-line rule.)  now both
    # linebreaks raise:
    with raises(SyntaxError):
        list(big.split_delimiters("x = 'abc\ndef'", python_delimiters))
    with raises(SyntaxError):
        list(big.split_delimiters("x = 'abc\rdef'", python_delimiters))
    with raises(SyntaxError):
        list(big.split_delimiters("x = f'abc\ndef'", python_delimiters))
    # triple-quoted strings still allow linebreaks, of course.
    test("x = '''abc\ndef'''",
        (
            SDV('x = ',      "'''", '',    ''),
            SDV('abc\ndef',  '',    "'''", ''),
        ),
        )

    # comments end at '\n' or '\r', whichever comes first.
    # (this used to be state-machine surgery; now the comment
    # delimiter just declares both closers.)
    for linebreak in ('\n', '\r'):
        test(f"x = 3 # comment{linebreak}y",
            (
                SDV('x = 3 ',    '#', '',        ''),
                SDV(' comment',  '',  linebreak, ''),
                SDV('y',         '',  '',        ''),
            ),
            )

    # and the same asymmetry existed inside f-string format
    # specs, in the other direction: the spec state is shared
    # by single- and triple-quoted f-strings, so it permits
    # linebreaks--but only '\n' was reset to legal, so '\r'
    # in a format spec raised.  now both are permitted:
    for linebreak in ('\n', '\r'):
        got = list(big.split_delimiters(f"f'{{x:a{linebreak}b}}'", python_delimiters))
        assert got[2].change == ':'
        assert got[3].text == f"a{linebreak}b"

    # regression: Python's tokenizer only recognizes '\n' and
    # '\r' as line boundaries.  big's *other* linebreaks--
    # vertical tab, form feed, U+2028, and friends--are plain
    # text inside strings and comments, as far as Python is
    # concerned, and python_delimiters used to reject them
    # there.  the grammar declares them literal now: they're
    # still linebreaks to big, just text to Python.
    for exotic in ('\x0b', '\x0c', '\x1c', '\x85', ' '):
        got = list(big.split_delimiters("x = 'a" + exotic + "b'\n", python_delimiters))
        assert got[1].text == 'a' + exotic + 'b'
        got = list(big.split_delimiters("x = f'a" + exotic + "b{q}'\n", python_delimiters))
        assert got[1].text == 'a' + exotic + 'b'
        got = list(big.split_delimiters("pass # a" + exotic + "b\ny", python_delimiters))
        assert got[1].text == ' a' + exotic + 'b'
        assert got[1].close == '\n'

    # regression: '!=' inside an {interpolation} is the
    # not-equals operator, not a '!' conversion field followed
    # by junk.  (real python's rule: a conversion is '!' not
    # followed by '='.  multisplit's greedy tokenization gives
    # us the same rule for free once '!=' is a literal token.)
    test("f'{a != b}'",
        (
            SDV('',        "f'", '', ''),
            SDV('',        '{',  '', ''),
            SDV('a != b',  '',  '}', ''),
            SDV('',        '',  "'", ''),
        ),
        )
    # ...and a real conversion after an expression containing
    # '!=' still works
    test("f'{a != b!r}'",
        (
            SDV('',        "f'", '', ''),
            SDV('',        '{',  '', ''),
            SDV('a != b',  '',   '', '!'),
            SDV('r',       '',  '}', ''),
            SDV('',        '',  "'", ''),
        ),
        )

    # {{ and }} are literal text inside an f-string body...
    test("f'a{{b}}c'",
        (
            SDV('',            "f'", '', ''),
            SDV('a{{b}}c',     '',  "'", ''),
        ),
        )
    # ...but immediately inside an {interpolation}, {{ really
    # is two open braces--it's an expression, where {{1}} is a
    # set containing a set.  (the surgery used to flush it as
    # inert text there.)
    test("f'{ {{1}} }'",
        (
            SDV('',      "f'", '', ''),
            SDV('',      '{',  '', ''),
            SDV(' ',     '{',  '', ''),
            SDV('',      '{',  '', ''),
            SDV('1',     '',  '}', ''),
            SDV('',      '',  '}', ''),
            SDV(' ',     '',  '}', ''),
            SDV('',      '',  "'", ''),
        ),
        )

def test_python_delimiters_version():
    # python_delimiters_version maps every supported Python
    # version to *that version's* grammar, independent of the
    # running interpreter.  (it used to map 3.6-3.13--no
    # 3.14--and every key mapped to the same object, whose
    # contents depended on the running interpreter.)
    pdv = big.python_delimiters_version

    expected_keys = {f"3.{minor}" for minor in range(6, 15)}
    assert set(pdv) == expected_keys

    # 3.6 through 3.13 share one t-free grammar...
    for minor in range(6, 14):
        assert pdv[f"3.{minor}"] is pdv["3.6"]
        assert 't"' not in pdv[f"3.{minor}"]
    # ...and 3.14 has its own, with t-string prefixes.
    assert pdv["3.14"] is not pdv["3.6"]
    for prefix in ('t', 'T', 'rt', 'tR'):
        assert prefix + '"' in pdv["3.14"]
        assert prefix + "'''" in pdv["3.14"]

    # python_delimiters is the running interpreter's grammar.
    if sys.version_info[:2] >= (3, 14): # pragma: nocover
        assert big.python_delimiters is pdv["3.14"]
    else: # pragma: nocover
        assert big.python_delimiters is pdv["3.6"]

    # in the 3.14 grammar, t-strings get the same brace
    # surgery as f-strings: {interpolations} open and close.
    # (on 3.14 interpreters this used to be broken even in
    # python_delimiters: the surgery only recognized f-string
    # states, so t-string braces were flushed as inert text.)
    got = list(big.split_delimiters("t'hi {name}!'", pdv["3.14"]))
    opens = [v.open for v in got if v.open]
    closes = [v.close for v in got if v.close]
    assert opens == ["t'", '{']
    assert closes == ['}', "'"]
    # every value unpacks to four fields, from any grammar
    # (the yields-3 transition period ended in 0.14)
    for v in got:
        text, open, close, change = v
    got = list(big.split_delimiters("x = 3 # comment\n", pdv["3.8"]))
    for v in got:
        text, open, close, change = v

    # in the 3.13-and-earlier grammar, t isn't a string prefix:
    # it parses as an ordinary name followed by a plain string.
    got = list(big.split_delimiters("t'hi {name}!'", pdv["3.13"]))
    opens = [v.open for v in got if v.open]
    assert opens == ["'"]

def test_lines_strip_indent():

    def test(li, expected):
        got = list(li)

        if 0:
            import pprint
            print("\n\n")
            print("-"*72)
            print("expected:")
            pprint.pprint(expected)
            print("\n\n")
            print("got:")
            pprint.pprint(got)
            print("\n\n")

        assert expected == got

    def L(li, line_number, column_number, line, end=_sentinel, *, leading=None, trailing=None, original=None, **kwargs):
        is_bytes = isinstance(line, bytes)
        empty = b'' if is_bytes else ''

        if end is _sentinel:
            end = b'\n' if is_bytes else '\n'

        if leading is None:
            leading = empty

        if trailing is None:
            trailing = empty

        if original is None:
            original = leading + line + trailing + end

        return (big.text.LineInfo(li, original, line_number, column_number, end=end, leading=leading, trailing=trailing, **kwargs), line)


    lines = dedent("""
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
        qoutdent
        """)

    i = li = big.text.lines(lines)
    i = big.text.lines_strip_indent(li)

    expected = [
        L(li,  1,  1, '',                 indent=0),
        L(li,  2,  1, 'left margin',      indent=0),
        L(li,  3,  1, 'if 3:',            indent=0),
        L(li,  4,  5, 'text',             indent=1, leading='    '),
        L(li,  5,  1, 'else:',            indent=0),
        L(li,  6,  5, 'if 1:',            indent=1, leading='    '),
        L(li,  7, 11, 'other text',       indent=2, leading='          '),
        L(li,  8, 11, 'other text',       indent=2, leading='          '),
        L(li,  9,  5, 'more text',        indent=1, leading='    '),
        L(li, 10,  7, 'different indent', indent=2, leading='      '),
        L(li, 11,  5, 'outdent',          indent=1, leading='    '),
        L(li, 12,  1, 'outdent',          indent=0),
        L(li, 13,  3, 'new indent',       indent=1, leading='  '),
        L(li, 14,  1, 'qoutdent',         indent=0),
        L(li, 15,  1, '',                 indent=0, end=''),
        ]
    test(i, expected)


    ##
    ## test tab to spaces
    ##

    lines = (
        "left margin\n"
        "\teight\n"
        "  \t    twelve\n"
        "        eight is enough\n"
        "    \n"
        )
    i = li = big.lines(lines)
    i = big.lines_strip_indent(i)

    expected = [
        L(li, 1,  1, 'left margin',     indent=0, leading=''),
        L(li, 2,  9, 'eight',           indent=1, leading='\t'),
        L(li, 3, 13, 'twelve',          indent=2, leading='  \t    '),
        L(li, 4,  9, 'eight is enough', indent=1, leading='        '),
        L(li, 5,  1, '',                indent=0, trailing='    '), # regression test!
        L(li, 6,  1, '',                indent=0, leading='', end=''),
        ]

    test(i, expected)

    lines = (
        b"left margin\n"
        b"\tfour\n"
        b"  \t    eight\n"
        b"  \t\tfigure eight is double four\n"
        b"    figure four is half of eight\n"
        )

    i = li = big.lines(lines, tab_width=4)
    i = big.lines_strip_indent(i)

    expected = [
        L(li, 1, 1, b'left margin',                  indent=0, leading=b''),
        L(li, 2, 5, b'four',                         indent=1, leading=b'\t'),
        L(li, 3, 9, b'eight',                        indent=2, leading=b'  \t    '),
        L(li, 4, 9, b'figure eight is double four',  indent=2, leading=b'  \t\t'),
        L(li, 5, 5, b'figure four is half of eight', indent=1, leading=b'    '),
        L(li, 6, 1, b'',                             indent=0, leading=b'', end=b''),
        ]

    test(i, expected)

    ##
    ## test raising for illegal outdents
    ##

    # when it's between two existing indents
    i = li = big.lines(
        "left margin\n"
        "\tfour\n"
        "  \t    eight\n"
        "      six?!\n"
        "left margin again\n",
        tab_width=4)
    i = big.lines_strip_indent(i)

    with raises(IndentationError):
        test(i, [])


    # when it's less than the first indent
    i = li = big.lines(
        "left margin\n"
        "\tfour\n"
        "  \t    eight\n"
        "  two?!\n"
        "left margin again\n",
        tab_width=4)
    i = big.lines_strip_indent(i)

    with raises(IndentationError):
        test(i, [])

    # ensure that lines_strip_indent is an iterator
    i = li = big.lines("a\nb\nc\nd")
    i = big.lines_strip_indent(i)
    try:
        info, line = next(i)
    except TypeError: # pragma: nocover
        assert False, "line_strip_indent did not return an iterator"



def test_lines_misc():
    ## error handling
    with raises(TypeError):
        next(big.lines([ (1, 2)]))
    with raises(ValueError):
        next(big.lines([ ('a', 'b', 'c')]))

    with raises(ValueError):
        next(big.lines([ 'x', 'y', 'z' ], separators=('y',)))

    with raises(TypeError):
        next(big.lines("", line_number=math.pi))
    with raises(TypeError):
        next(big.lines("", column_number=math.pi))
    with raises(TypeError):
        next(big.lines("", tab_width=math.pi))

    with raises(ValueError):
        list(big.lines_filter_line_comment_lines("", []))
    with raises(TypeError):
        list(big.lines_filter_line_comment_lines("", math.pi))


    li = big.lines('')
    with raises(TypeError):
        big.LineInfo(li, math.pi, 1, 1)
    with raises(TypeError):
        big.LineInfo(li, '', math.pi, 1)
    with raises(TypeError):
        big.LineInfo(li, '', 1, math.pi)
    with raises(TypeError):
        next(big.LineInfo(li, '', 1, 1, leading=math.pi))
    with raises(TypeError):
        next(big.LineInfo(li, '', 1, 1, trailing=math.pi))
    with raises(TypeError):
        next(big.LineInfo(li, '', 1, 1, end=math.pi))
    with raises(TypeError):
        next(big.LineInfo(li, '', 1, 1, indent=math.pi))
    with raises(TypeError):
        next(big.LineInfo(li, '', 1, 1, indent=None))
    with raises(TypeError):
        next(big.LineInfo(li, '', 1, 1, indent='    '))
    with raises(TypeError):
        next(big.LineInfo(li, '', 1, 1, match=3))

    ## test kwargs
    lines = big.lines('', quark=22)
    assert hasattr(lines, 'quark')
    assert getattr(lines, 'quark') == 22

    info = big.LineInfo(lines, '', 1, 1, quark=35)
    assert hasattr(info, 'quark')
    assert getattr(info, 'quark') == 35

    ## repr
    info = big.LineInfo(lines, '', 1, 1, indent=0)
    lines_repr = repr(lines)
    assert repr(info) == f"LineInfo(lines={lines_repr}, line_number=1, column_number=1)"

    ## clip
    def test_clip_leading(line):
        l_original, end = list(big.multisplit(line, big.linebreaks, keep=big.AS_PAIRS))[0]
        l = l_original
        info = big.LineInfo(lines, line, 5, 1, end=end)
        copy = info.copy()
        assert info == copy
        l = info.clip_leading(l, l_original[:-1])
        assert l
        assert info.column_number != 1
        assert info != copy
        copy = info.copy()
        l = info.clip_leading(l, l_original[-1])
        assert l == ''
        assert info.column_number == 1
        assert info.trailing == l_original
        assert info != copy
    test_clip_leading('     ')
    test_clip_leading('         \n')


def test_strip_indents_blank_line_linebreak_preservation():
    # regression: three bugs in blank-line linebreak preservation.
    # 1. a line that was 100% linebreak characters lost its
    #    linebreak (the counter was enumerate's index, off by one
    #    exactly when the scan never broke).
    # 2. bytes lines NEVER preserved linebreaks (iterating a
    #    bytes yields ints, never found in a set of bytes).
    # 3. the linebreaks parameter's default is the str set, and
    #    for bytes lines it never swapped to bytes_linebreaks
    #    (the dance strip_line_comments already did).
    assert list(big.strip_indents(['a\n', '\n', '  \n', '\r\n', '\v', 'b\n'])) == [(0, 'a\n'), (0, '\n'), (0, '\n'), (0, '\r\n'), (0, '\v'), (0, 'b\n')]
    assert list(big.strip_indents([b'a\n', b'\n', b'  \n', b'\r\n', b'b\n'])) == [(0, b'a\n'), (0, b'\n'), (0, b'\n'), (0, b'\r\n'), (0, b'b\n')]
    # linebreaks=None disables preservation
    assert list(big.strip_indents(['a\n', '\n', '  \n', 'b\n'], linebreaks=None)) == [(0, 'a\n'), (0, ''), (0, ''), (0, 'b\n')]
    # trailing blank lines flush at depth 0, linebreaks intact
    assert list(big.strip_indents(['    a\n', '\n', '  \n'])) == [(1, 'a\n'), (0, '\n'), (0, '\n')]

def test_strip_indent():

    def test(li, expected):
        got = list(li)

        if 0:
            import pprint
            print("\n\n")
            print("-"*72)
            print("expected:")
            pprint.pprint(expected)
            print("\n\n")
            print("got:")
            pprint.pprint(got)
            print("\n\n")

        assert expected == got

    def L(indent, line, line_number, column_number, offset, origin):
        if isinstance(line, str):
        # origin=origin, 
            return (indent, string(line, source=origin, line_number=line_number, column_number=column_number))
        return (indent, line)

    #                                                                                                                     11111111111111111111111 111111111111 11111111 1111111111111 111111111 1
    #                   111 111111 122222222 223333 3333334444 444444555555555566666 666667777777777888888 88889999999999 00000000001111111111222 222222233333 33333444 4444444555555 555566666 6
    #        0 123456789012 345678 901234567 890123 4567890123 456789012345678901234 567890123456789012345 67890123456789 01234567890123456789012 345678901234 56789012 3456789012345 678901234 5
    lines = "\nleft margin\nif 3:\n    text\nelse:\n    if 1:\n          other text\n          other text\n    more text\n      different indent\n    outdent\noutdent\n  new indent\nqoutdent\n"

    s = string(lines)
    i = string(lines).split('\n')
    i = big.text.strip_indents(i)

    expected = [
        (0, s[0:0]),
        (0, s[1:12]),
        (0, s[13:18]),
        (1, s[23:27]),
        (0, s[28:33]),
        (1, s[38:43]),
        (2, s[54:64]),
        (2, s[75:85]),
        (1, s[90:99]),
        (2, s[106:122]),
        (1, s[127:134]),
        (0, s[135:142]),
        (1, s[145:155]),
        (0, s[156:164]),
        (0, s[165:165]),
        ]
    test(i, expected)


    ##
    ## test tab to spaces
    ##

    lines = (
        "left margin\n"
        "\teight\n"
        "  \t    twelve\n"
        "        eight is enough\n"
        "    \n"
        )
    s = string(lines)
    i = s.split('\n')
    i = big.strip_indents(i, linebreaks=None)

    expected = [
        L(0, 'left margin',     1,  1,  0, s),
        L(1, 'eight',           2,  9, 11, s),
        L(2, 'twelve',          3, 13, 11, s),
        L(1, 'eight is enough', 4,  9, 11, s),
        L(0, '',                5,  1, 11, s),
        L(0, '',                6,  1, 11, s),
        ]

    test(i, expected)

    lines = (
        b"left margin\n"
        b"\tfour\n"
        b"  \t    eight\n"
        b"  \t\tfigure eight is double four\n"
        b"    figure four is half of eight\n"
        )

    s = lines
    i = s.split(b'\n')
    i = big.strip_indents(i, tab_width=4)

    expected = [
        L(0, b'left margin',                  1, 1, 1, s),
        L(1, b'four',                         2, 5, 1, s),
        L(2, b'eight',                        3, 9, 1, s),
        L(2, b'figure eight is double four',  4, 9, 1, s),
        L(1, b'figure four is half of eight', 5, 5, 1, s),
        L(0, b'',                             6, 1, 1, s),
        ]

    test(i, expected)

    ##
    ## test preserving linebreak characters
    ##

    lines = (
        "left margin\n"
        " \n"
        "   \n"
        "        eight is enough\n"
        "    \n"
        "  "
        )
    s = string(lines)
    i = s.splitlines(True)
    i = big.strip_indents(i)

    expected = [
        L(0, 'left margin\n',     1,  1,  0, s),
        L(1, '\n',                2,  2, 13, s),
        L(1, '\n',                3,  4, 17, s),
        L(1, 'eight is enough\n', 4,  9, 26, s),
        L(0, '\n',                5,  5, 46, s),
        L(0, '',                  6,  1, 47, s),
        ]

    test(i, expected)

    ##
    ## test raising for illegal outdents
    ##

    # when it's between two existing indents
    s = string(
        "left margin\n"
        "\tfour\n"
        "  \t    eight\n"
        "      six?!\n"
        "left margin again\n")
    i = s.splitlines()
    i = big.strip_indents(i, tab_width=4)

    with raises(IndentationError):
        test(i, [])


    # when it's less than the first indent
    s = string(
        "left margin\n"
        "\tfour\n"
        "  \t    eight\n"
        "  two?!\n"
        "left margin again\n")
    i = s.splitlines()
    i = big.strip_indents(i, tab_width=4)

    with raises(IndentationError):
        test(i, [])

    # ensure that lines_strip_indent is an iterator
    s = string("a\nb\nc\nd")
    i = s.splitlines()
    i = big.strip_indents(i, tab_width=4)
    try:
        info, line = next(i)
    except TypeError: # pragma: nocover
        assert False, "strip_indent did not return an iterator"




def test_int_to_words():
    # confirm that flowery has a default of True
    assert big.int_to_words(12345678) == big.int_to_words(12345678, flowery=True)

    # confirm that ordinal has a default of False
    assert big.int_to_words(12345678) == big.int_to_words(12345678, ordinal=False)

    # wrong types raise TypeError (0.13 raised ValueError)
    with raises(TypeError):
        big.int_to_words(3.14159)
    with raises(TypeError):
        big.int_to_words('hello sailor')
    with raises(TypeError):
        big.int_to_words({1:2, 3:4})

    def test(i, normal, flowery):
        # independently compute the ordinal version
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
                ("twelve", "twelfth"),
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
            assert big.int_to_words(i, flowery=False) == result
            result = cardinal_to_ordinal(result)
            assert big.int_to_words(i, flowery=False, ordinal=True) == result

            result = prefix + flowery
            assert big.int_to_words(i, flowery=True) == result
            result = cardinal_to_ordinal(result)
            assert big.int_to_words(i, flowery=True, ordinal=True) == result

            # if inflect is available, confirm that int_to_words
            # produces identical output to inflect.number_to_words.
            # well, except, they prefer prepending the word "minus"
            # for negative numbers, and I prefer prepending "negative".

            if engine:
                try:
                    minus_fixed_flowery = big.int_to_words(i, flowery=True).replace("negative ", "minus ")
                    assert engine.number_to_words(i) == minus_fixed_flowery
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

    # regression: the middle magnitudes.  "twelveth",
    # "qindecillion", and "septdecillion" were misspelled
    # ("twelfth", "quindecillion", "septendecillion"), and the
    # quantity table's alignment padding leaked into the output
    # for sextillion through decillion ("one   decillion").
    # inflect handles some of these magnitudes, so where it
    # does, the parity check below now actually exercises them.
    test(10**21 + 3,
        'one sextillion three',
        'one sextillion and three')
    test(10**24 + 1,
        'one septillion one',
        'one septillion and one')
    test(10**27 + 2,
        'one octillion two',
        'one octillion and two')
    test(10**30 + 4,
        'one nonillion four',
        'one nonillion and four')
    test(10**33 + 5,
        'one decillion five',
        'one decillion and five')
    test(10**48 + 6,
        'one quindecillion six',
        'one quindecillion and six')
    test(10**54 + 8,
        'one septendecillion eight',
        'one septendecillion and eight')

    # test the top end
    test(10**75 - 1,
        'nine hundred ninety-nine billion nine hundred ninety-nine million nine hundred ninety-nine thousand nine hundred ninety-nine vigintillion nine hundred ninety-nine novemdecillion nine hundred ninety-nine octodecillion nine hundred ninety-nine septendecillion nine hundred ninety-nine sexdecillion nine hundred ninety-nine quindecillion nine hundred ninety-nine quattuordecillion nine hundred ninety-nine tredecillion nine hundred ninety-nine duodecillion nine hundred ninety-nine undecillion nine hundred ninety-nine decillion nine hundred ninety-nine nonillion nine hundred ninety-nine octillion nine hundred ninety-nine septillion nine hundred ninety-nine sextillion nine hundred ninety-nine quintillion nine hundred ninety-nine quadrillion nine hundred ninety-nine trillion nine hundred ninety-nine billion nine hundred ninety-nine million nine hundred ninety-nine thousand nine hundred ninety-nine',
        'nine hundred and ninety-nine billion, nine hundred and ninety-nine million, nine hundred and ninety-nine thousand, nine hundred and ninety-nine vigintillion, nine hundred and ninety-nine novemdecillion, nine hundred and ninety-nine octodecillion, nine hundred and ninety-nine septendecillion, nine hundred and ninety-nine sexdecillion, nine hundred and ninety-nine quindecillion, nine hundred and ninety-nine quattuordecillion, nine hundred and ninety-nine tredecillion, nine hundred and ninety-nine duodecillion, nine hundred and ninety-nine undecillion, nine hundred and ninety-nine decillion, nine hundred and ninety-nine nonillion, nine hundred and ninety-nine octillion, nine hundred and ninety-nine septillion, nine hundred and ninety-nine sextillion, nine hundred and ninety-nine quintillion, nine hundred and ninety-nine quadrillion, nine hundred and ninety-nine trillion, nine hundred and ninety-nine billion, nine hundred and ninety-nine million, nine hundred and ninety-nine thousand, nine hundred and ninety-nine',
        )

    test(10**75,
        '1000000000000000000000000000000000000000000000000000000000000000000000000000',
        '1000000000000000000000000000000000000000000000000000000000000000000000000000',
        )


def test_encode_strings():
    sentinel = object()
    def test(o, expected, *, encoding=sentinel):
        if encoding == sentinel:
            got = big.encode_strings(o)
        else:
            got = big.encode_strings(o, encoding)
        assert got == expected

    test(['a', 'b', 'c'], [b'a', b'b', b'c']) # list
    test(('x', 'y', 'z'), (b'x', b'y', b'z')) # tuple
    test({'x', 'y', 'z'}, {b'x', b'y', b'z'}) # set
    test({'ab': 'cd', 'ef': 'gh'}, {b'ab': b'cd', b'ef': b'gh'}) # dict

    test([{ 'ab': ( 'cd',  'ef'),  'gh': { 'ij',  'kl'},  'mn': [ 'op', b'qr', { 'st':  'uv'}, ( 'wx',), { 'yz',} ]}],
         [{b'ab': (b'cd', b'ef'), b'gh': {b'ij', b'kl'}, b'mn': [b'op', b'qr', {b'st': b'uv'}, (b'wx',), {b'yz',} ]}],
         ) # super bombad nested stuffs


    class SubclassOfList(list):
        pass

    test(SubclassOfList(('ab', 'cd')), SubclassOfList((b'ab', b'cd')))

    test(('x', 'y', 'z', "\N{PILE OF POO}"), (b'x', b'y', b'z', b'\xf0\x9f\x92\xa9'), encoding='utf-8')

    test('abcde', b'abcde')
    test('ijklm 🐿️', b'ijklm \xf0\x9f\x90\xbf\xef\xb8\x8f', encoding="utf-8")
    with raises(UnicodeEncodeError):
        test('ijklm 🐿️', b'')
    test(b'wxyz', b'wxyz')

    with raises(TypeError):
        class Foo:
            def __init__(self, x):
                self.x = x
        foo = Foo('abc')
        test(foo, None)

def test_format_map():
    d = {'encoding': 'mp3', 'mp3 size': 8228}
    assert big.format_map("x={{encoding} size}", d) == 'x=8228'
    assert big.format_map("abcde", d) == 'abcde'
    assert big.format_map("a\\{b\\\\cd\\}e", {}) == 'a{b\\cd}e'
    assert big.format_map("j\\\\\\\\\\\\k", {}) == 'j\\\\\\k'
    assert big.format_map("d\\e\\g\\h{q}", {'q':'q'}) == 'd\\e\\g\\hq'
    assert big.format_map("\\{q\\}", {'q':'q'}) == '{q}'
    assert big.format_map("{q\\x}", {'q\\x':'z'}) == 'z'

def test_decode_python_script():
    # Note: decode_python_script also gets a workout from the
    # tests for read_python_file.  Which... are actually in this file, tests/test_text.py.
    # (We test split_delimiters(python_delimiters) by splitting all the Python
    # scripts that ship with big.)

    # test without either a bom or SCE (source code encoding)
    script = b"print('Hello, world!')\n"
    assert big.decode_python_script(script) == script.decode('ascii')

    # an unknown encoding in the coding comment raises
    # UnicodeDecodeError, like tokenize
    with raises(UnicodeDecodeError):
        big.decode_python_script(b"# coding: bogus-encoding\nx = 1\n")
    # ...including when there's also a BOM (the cookie is
    # checked against the BOM's encoding, and an unknown
    # cookie can't even be looked up)
    with raises(UnicodeDecodeError):
        big.decode_python_script(b"\xef\xbb\xbf# coding: bogus-encoding\nx = 1\n")

    # turn off bom and SCE
    assert big.decode_python_script(script, use_bom=False, use_source_code_encoding=False) == script.decode('ascii')

    # test universal newlines
    line = b's' * 3072
    script = line + b'\r\n' + line
    assert big.decode_python_script(script) == script.decode('ascii').replace('\r\n', '\n')

    script = b'first_line=3\r\nsecond_line=4\rthird_line=5\nfourth_line=6\n'
    decoded = 'first_line=3\nsecond_line=4\nthird_line=5\nfourth_line=6\n'
    assert big.decode_python_script(script) == decoded
    assert big.decode_python_script(script, newline='') == script.decode('ascii')
    assert big.decode_python_script(script, newline='\n') == script.decode('ascii')
    assert big.decode_python_script(script, newline='\r\n') == script.decode('ascii')
    assert big.decode_python_script(script, newline='\r') == script.decode('ascii')

    # we should ignore the inaccurate SCE because we shouldn't break the line there
    script = b'first_line=3\r# -*- coding: utf-16 -*-\r\nthird_line=5\nfourth_line=6\n'
    assert big.decode_python_script(script, newline='\n') == script.decode('ascii')

    with raises(ValueError):
        big.decode_python_script(script, newline='x')

    # PEP 263, as implemented by CPython's tokenize.detect_encoding:
    # the magic coding comment must be on line 1 or line 2, the
    # first match wins, and line 2 only counts if line 1 is blank
    # or a comment.  (it used to accept a comment on line 3, and
    # last-match-wins.)  the \xff probe byte on line 3+ decodes
    # under iso8859-1 and raises under utf-8, revealing which
    # encoding was chosen.
    LATIN = b"# -*- coding: iso8859-1 -*-\n"
    PROBE = b"z = b'\xff'\n"

    def uses_latin(script):
        try:
            return '\xff' in big.decode_python_script(script)
        except UnicodeDecodeError:
            return False

    assert uses_latin(LATIN + PROBE)                              # line 1
    assert uses_latin(b"#!/usr/bin/env python\n" + LATIN + PROBE) # line 2, line 1 comment
    assert uses_latin(b"\n" + LATIN + PROBE)                      # line 2, line 1 blank
    assert not (uses_latin(b"x = 1\n" + LATIN + PROBE))                # line 1 is code: line 2 ignored
    assert not (uses_latin(b"#!x\n#!y\n" + LATIN + PROBE))             # line 3: ignored
    assert not (uses_latin(b"# coding: utf-8\n" + LATIN + PROBE))      # first match wins

    # and wherever tokenize.detect_encoding renders a verdict,
    # big agrees.  (detect_encoding only reads two lines, so the
    # probe byte never bothers it.)
    import io
    import tokenize
    for pep263_script in (
        LATIN + PROBE,
        b"#!/usr/bin/env python\n" + LATIN + PROBE,
        b"\n" + LATIN + PROBE,
        b"x = 1\n" + LATIN + PROBE,
        b"#!x\n#!y\n" + LATIN + PROBE,
        b"# coding: utf-8\n" + LATIN + PROBE,
        ):
        cpython = tokenize.detect_encoding(io.BytesIO(pep263_script).readline)[0]
        assert uses_latin(pep263_script) == (cpython == 'iso8859-1'), pep263_script

    # BOM + magic-comment agreement is normalized through codecs:
    # every spelling of the BOM's encoding is accepted...
    bom = b'\xef\xbb\xbf'
    for cookie in (b"# coding: utf-8\n", b"# coding: utf8\n", b"# coding: UTF_8\n"):
        body = cookie + b"x = 1\n"
        assert big.decode_python_script(bom + body) == body.decode('utf-8')
    # ...a genuinely different encoding still raises...
    with raises(UnicodeDecodeError):
        big.decode_python_script(bom + LATIN + b"x = 1\n")
    # ...and an endianness-unqualified comment agrees with an
    # endian BOM (supplying the endianness is the BOM's job).
    text16 = "# coding: utf-16\nx = 1\n"
    assert big.decode_python_script(b'\xff\xfe' + text16.encode('utf-16-le')) == text16


def test_strip_line_comments():

    def test(origin, line_comment_markers, *segments, keepends=False, **kwargs):
        is_bytes = isinstance(origin, bytes)
        if is_bytes:
            linebreak = b'\n'
        else:
            linebreak = '\n'

        origin = original = dedent(origin).lstrip(linebreak)

        if not is_bytes:
            origin = string(origin)
        i = li = origin.splitlines(keepends)
        got = list(big.strip_line_comments(i, line_comment_markers, **kwargs))


        expected = []
        offset = 0
        for s in segments:
            append_linebreak = keepends and linebreak in s
            substring = s.rstrip(linebreak)
            offset = origin.find(substring, offset)
            assert offset != -1, f"couldn't find substring={substring!r} in origin={origin!r}"
            slice = origin[offset:offset+len(substring)]
            if append_linebreak:
                slice += '\n'
            offset += len(substring)
            expected.append(slice)

        if 0:
            import pprint
            print("\n\n")
            print("-"*72)
            print("expected:")
            pprint.pprint(expected)
            print("\n\n")
            print("got:")
            pprint.pprint(got)
            print("\n\n")
            for e, g in zip(expected, got):
                print(e==g)
            print("\n\n")

        assert expected == got

        if is_bytes:
            return

        origin = original.encode('utf-8')
        line_comment_markers = big.encode_strings(line_comment_markers, 'utf-8')
        bytes_kwargs = {}
        for k, v in kwargs.items():
            v = big.encode_strings(v, 'utf-8')
            bytes_kwargs[k] = v
        bytes_expected = big.encode_strings(expected, 'utf-8')
        i = li = origin.splitlines(keepends)
        bytes_got = list(big.strip_line_comments(i, line_comment_markers, **bytes_kwargs))

        if 0:
            import pprint
            print("\n\n")
            print("-"*72)
            print("bytes input:")
            pprint.pprint(li)
            print("bytes expected:")
            pprint.pprint(bytes_expected)
            print("\n\n")
            print("bytes got:")
            pprint.pprint(bytes_got)
            print("\n\n")
            for e, g in zip(bytes_expected, bytes_got):
                print(e==g)
            print("\n\n")

        assert bytes_expected == bytes_got

    # no quote marks defined (the default)
    test("""
        for x in range(5): # this is a comment
            print("# this is quoted", x)
            print("") # this "comment" is useless
            print(no_comments_or_quotes_on_this_line)
            both//on this line#dawg
            and#also on this//line
          torture////1
         tort-ture######2
        zzzz""",
        ("#", "//"),

        'for x in range(5): ',
        '    print("',
        '    print("") ',
        '    print(no_comments_or_quotes_on_this_line)',
        '    both',
        '    and',
        '  torture',
        ' tort-ture',
        'zzzz',
        )

    # test specifying quotes as a string
    test("""
        for x in range(5): # this is my exciting comment
            print("# this is quoted", x)
            print("") # this "comment" is useless
            print(no_comments_or_quotes_on_this_line)
        qqq""",
        ("#", "//"),

        'for x in range(5): ',
        '    print("# this is quoted", x)',
        '    print("") ',
        '    print(no_comments_or_quotes_on_this_line)',
        'qqq',

        quotes='"\'')

    test("""
        for x in range(5): # this is my exciting comment
            print("# this is quoted", x)
            print("") # this "comment" is useless
            print(no_comments_or_quotes_on_this_line)
            print("#which is the comment?", w #z )
            print("//which is the comment?", x // 4Q2 )
            print("test without whitespace, and extra comment chars 1", y####artie deco )
            print("test without whitespace, and extra comment chars 2", z///////chinchilla the wookie monster )
        zucker""",
        ("#", "//"),

        'for x in range(5): ',
        '    print("# this is quoted", x)',
        '    print("") ',
        '    print(no_comments_or_quotes_on_this_line)',
        '    print("#which is the comment?", w ',
        '    print("//which is the comment?", x ',
        '    print("test without whitespace, and extra comment chars 1", y',
        '    print("test without whitespace, and extra comment chars 2", z',
        'zucker',

        quotes=('"', "'"))

    # test multiline
    # test specifying line comment markers as a string, and only one quote mark
    test("""
        for x in range(5): # this is my exciting comment
            print('''
            this is a multiline string
            does this line have a comment? # no!
            ''') > but here's a comment
            print("just checking, # here too") # here is another comment
        pizzapaperpantry""",
        "#>",

        'for x in range(5): ',
        "    print('''",
        "    this is a multiline string",
        "    does this line have a comment? # no!",
        "    ''') ",
        '    print("just checking, # here too") ',
        'pizzapaperpantry',

        quotes='"', multiline_quotes=("'''",))

    # invalid comment characters
    with raises(ValueError):
        list(big.strip_line_comments("a\nb\n".splitlines(), None))

    # unterminated single-quotes across lines
    with raises(SyntaxError):
        list(big.strip_line_comments(("foo 'bar", "' bat 'zzz'"), ("#", '//',), quotes="'"))

    # unterminated single-quotes at the end
    with raises(SyntaxError):
        list(big.strip_line_comments(("foo 'bar' bat 'zzz",), ("#", '//',), quotes=("'",)))

    # unterminated triple-quotes at the end
    with raises(SyntaxError):
        list(big.strip_line_comments(("foo 'bar' bat '''zzz", 'more lines here', "wait what's happening?"), ("#", '//',), multiline_quotes=("'''",)))

    test(b"a\nb# clipped\n c", b'#',
        b'a',
        b'b',
        b' c',
        )

    test(b'a\nb"# ignored"\n c', (b'#',),
        b'a',
        b'b"# ignored"',
        b' c',
        quotes=(b'"',),
        )

    test(b'a\nb"# ignored"\n c#lipped', b'#',
         b'a',
         b'b"# ignored"',
         b' c',
        quotes=b'"',
        )

    test(b'a\nb"# ignored\n" c#lipped', b'#',
        b'a',
        b'b"# ignored',
        b'" c',
        multiline_quotes=b'"',
        )

    # test preserving linebreaks at the end
    s = test("""
        for x in range(5): # this is a comment
            # blank line with comment
        x
        zzzz""",
        "#",

        'for x in range(5): \n',
        '    \n',
        'x\n',
        'zzzz',

        keepends=True,
        )

    # line comment markers may be any iterable--sets and
    # generators included.  (the validation used to index
    # markers[0], so these raised TypeError.)
    for markers in ({'#', ';'}, (m for m in ('#', ';'))):
        got = list(big.strip_line_comments(iter(['a ; b # c\n']), markers))
        assert got == ['a \n']

    # non-string markers get the friendly error too.
    with raises(ValueError):
        list(big.strip_line_comments(iter(['a\n']), (0,)))

    # DOS linebreaks survive comment stripping...
    got = list(big.strip_line_comments(iter(['code # comment\r\n']), ('#',)))
    assert got == ['code \r\n']

    # ...and passing falsy linebreaks turns preservation off.
    got = list(big.strip_line_comments(iter(['code # comment\n']), ('#',), linebreaks=()))
    assert got == ['code ']

def assertTypedEqual(actual, expect, msg=None):
    assert actual == expect, msg
    def recurse(actual, expect):
        if isinstance(expect, (tuple, list)):
            for x, y in zip(actual, expect):
                recurse(x, y)
        else:
            assert type(actual) is type(expect), msg
    recurse(actual, expect)

def test_match_group():
    pattern = string("a(:+)b").compile()
    m = pattern.search(string("xxa:::byy"))
    assert m
    assert m.group() == "a:::b"
    assert isinstance(m.group(), string)
    assert m[1] == ":::"
    assert isinstance(m.group(1), string)
    groups = m.group(0, 1)
    assert groups == ("a:::b", ":::")
    assert isinstance(groups[0], string)
    assert isinstance(groups[1], string)

    pattern = string(r"(a+)(b+)?(c+)?").compile()
    m = pattern.search(string("xxaaabbyy"))
    groups = m.groups()
    assert groups == ('aaa', 'bb', None)
    assert isinstance(groups[0], string)
    assert isinstance(groups[1], string)
    groups = m.group(1, 2, 3)
    assert groups == ('aaa', 'bb', None)
    assert isinstance(groups[0], string)
    assert isinstance(groups[1], string)

def test_match_groupdict():
    pattern = string(r'(?P<aye>a+)|(?P<bee>b+)').compile()
    text = string("xxxaxxxbbx")
    l = list(pattern.finditer(text))
    for m, expected in zip(l, [
        {'aye': text[3:4], 'bee': None},
        {'aye': None, 'bee': text[7:9]},
        ]):
        with subtest(expected):
            got = m.groupdict()
            assert got == expected

def test_passthroughs():
    # These Pattern methods are just one-line pass-throughs for
    # re.Pattern methods.  Smoke testing seems sufficient.

    pattern = string(":+").compile()
    m = pattern.search(string("a b ::: c"))
    assert m
    assert m.group() == ":::"
    assert isinstance(m.group(), string)

    m = pattern.match(string(":::: xyz"))
    assert m
    assert m.group() == "::::"
    assert isinstance(m.group(), string)

    s = string(":::::")
    m = pattern.fullmatch(s)
    assert m
    assert m.group() == s
    assert isinstance(m.group(), string)

    assert repr(pattern) == repr(pattern.pattern)
    assert repr(m) == repr(m.match)

    s = string("a ::: b :: c :::: d")
    result = pattern.sub("X", s)
    assert result == "a X b X c X d"
    assert isinstance(result, str)

    result = pattern.subn("X", s)
    assert result[0] == "a X b X c X d"
    assert isinstance(result[0], str)
    assert result[1] == 3
    assert isinstance(result[1], int)

    pattern = string(r'(a+)|(b+)').compile()
    m = pattern.search("xxaaayyyy")
    result = m.expand(r"__\1--")
    assert result == "__aaa--"

def test_pattern():
    with raises(TypeError):
        Pattern(3.5)
    with raises(TypeError):
        Pattern('x', 3.5)

def test_pattern_findall():
    pattern = string(":+").compile()
    l = pattern.findall(string("a :: b ::: c"))
    assert len(l) == 2
    assert l == ["::", ":::"]
    assert isinstance(l[0], string)
    assert isinstance(l[1], string)

    pattern = string(r'\bf[a-z]*').compile()
    l = pattern.findall(string('which foot or hand fell fastest'))
    assert l == ['foot', 'fell', 'fastest']
    assert all(isinstance(o, string) for o in l)

    pattern = string(r'(\w+)=(\d+)').compile()
    l = pattern.findall(string('set width=20 and height=10'))
    assert l == [('width', '20'), ('height', '10')]
    assert all(isinstance(o, tuple) for o in l)
    assert all(isinstance(q, string)  for o in l  for q in o )

    pattern = string(r'(a+)|(b+)').compile()
    l = pattern.findall(string("xxxaxxxbbxxaabb"))
    assert l == [('a', None), (None, 'bb'), ('aa', None), (None, 'bb')]
    assert all((isinstance(q, string) or (q is None))  for o in l  for q in o )

    pattern = string(r'a(x+)b').compile()
    l = pattern.findall(string("___aaxxxbb___axxb__"))
    assert l == ['xxx', 'xx']
    assert all(isinstance(o, string) for o in l)

def test_pattern_split():

    def re_split(pattern, string):
        p = Pattern(pattern)
        return p.split(string)

    pattern = string(":+").compile()
    s = string("a :: b ::: c")
    l = pattern.split(s, 1)
    assert len(l) == 2
    assert l[0] == "a "
    assert isinstance(l[0], string)
    assert l[1] == " b ::: c"
    assert isinstance(l[1], string)

    for s in ":a:b::c", string(":a:b::c"):
        assertTypedEqual(re_split(":", s),
                              [s[0:0], s[1], s[3], s[5:5], s[6]])
        assertTypedEqual(re_split(":+", s),
                              [s[0:0], s[1], s[3], s[6]])
        assertTypedEqual(re_split("(:+)", s),
                              [s[0:0], s[0], s[1], s[2], s[3], s[4:6], s[6]])
    for s in (b":a:b::c",):
                   #memoryview(b":a:b::c")):
        assertTypedEqual(re_split(b":", s),
                              [b'', b'a', b'b', b'', b'c'])
        assertTypedEqual(re_split(b":+", s),
                              [b'', b'a', b'b', b'c'])
        assertTypedEqual(re_split(b"(:+)", s),
                              [b'', b':', b'a', b':', b'b', b'::', b'c'])
    for a, b, c in (
            ("\xe0", "\xdf", "\xe7"),
            ("\u0430", "\u0431", "\u0432"),
            ("\U0001d49c", "\U0001d49e", "\U0001d4b5"),
        ):
        s = f":{a}:{b}::{c}"
        assert re_split(":", s) == ['', a, b, '', c]
        assert re_split(":+", s) == ['', a, b, c]
        assert re_split("(:+)", s) == ['', ':', a, ':', b, '::', c]

    assert re_split("(?::+)", ":a:b::c") == ['', 'a', 'b', 'c']
    assert re_split("(:)+", ":a:b::c") == ['', ':', 'a', ':', 'b', ':', 'c']
    assert re_split("([b:]+)", ":a:b::c") == ['', ':', 'a', ':b::', 'c']
    assert re_split("(b)|(:+)", ":a:b::c") == ['', None, ':', 'a', None, ':', '', 'b', None, '',
                      None, '::', 'c']
    assert re_split("(?:b)|(?::+)", ":a:b::c") == ['', 'a', '', '', 'c']

    for sep, expected in [
        (':*',     ['', '', 'a', '', 'b', '', 'c', '']),
        ('(?::*)', ['', '', 'a', '', 'b', '', 'c', '']),
        ('(:*)',   ['', ':', '', '', 'a', ':', '', '', 'b', '::', '', '', 'c', '', '']),
        ('(:)*',   ['', ':', '', None, 'a', ':', '', None, 'b', ':', '', None, 'c', None, '']),
    ]:
        with subtest(sep=sep):
            assertTypedEqual(re_split(sep, ':a:b::c'), expected)

    for sep, expected in [
        ('',        ['', ':', 'a', ':', 'b', ':', ':', 'c', '']),
        (r'\b',     [':', 'a', ':', 'b', '::', 'c', '']),
        (r'(?=:)',  ['', ':a', ':b', ':', ':c']),
        (r'(?<=:)', [':', 'a:', 'b:', ':', 'c']),
    ]:
        with subtest(sep=sep):
            assertTypedEqual(re_split(sep, ':a:b::c'), expected)





def test_regression__separators_to_re_unhashable_iterables():
    direct = big.text._separators_to_re([',', ';'], False)
    expected = big.text._separators_to_re((',', ';'), False)
    assert direct == expected
    # direct helper coverage: unhashable iterables are normalized to tuples.
    assert direct == expected
    direct_bytes = big.text._separators_to_re([b',', b';'], True)
    expected_bytes = big.text._separators_to_re((b',', b';'), True)
    assert direct_bytes == expected_bytes

def run_tests(run=None):
    (run or bigtestlib.run)(name="big.text", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
