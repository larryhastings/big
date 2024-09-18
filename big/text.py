#!/usr/bin/env python3

_license = """
big
Copyright 2022-2024 Larry Hastings
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

import enum
import functools
import heapq
import itertools
from itertools import zip_longest
from .itertools import PushbackIterator
from . import state
import math
import operator
import re
import struct
import sys


try:
    from re import Pattern as re_Pattern
except ImportError: # pragma: no cover
    re_Pattern = re._pattern_type

try:
    import regex
    regex_Pattern = regex.Pattern
    def isinstance_re_pattern(o):
        return isinstance(o, (re_Pattern, regex_Pattern))
except ImportError: # pragma: no cover
    regex_Pattern = re_Pattern
    def isinstance_re_pattern(o):
        return isinstance(o, re_Pattern)


__all__ = []

def _export_name(s):
    __all__.append(s)

def _export(o):
    _export_name(o.__name__)
    return o


def _iterate_over_bytes(b):
    # this may not actually iterate over bytes.
    # for example, we iterate over apostrophes and double_quotes
    # for gently_title, and those might be strings or bytes,
    # or iterables of strings or bytes.
    if isinstance(b, bytes):
        return (b[i:i+1] for i in range(len(b)))
    return iter(b)


def _recursive_encode_strings(o, encoding):
    if isinstance(o, bytes):
        return o
    if isinstance(o, str):
        return o.encode(encoding)

    type_o = type(o)
    if isinstance(o, dict):
        return type_o({
            _recursive_encode_strings(k, encoding):
             _recursive_encode_strings(v, encoding)
             for k, v in o.items()
             })
    if isinstance(o, (list, tuple)):
        return type_o(_recursive_encode_strings(e, encoding) for e in o)
    if isinstance(o, set):
        return type_o({
             _recursive_encode_strings(v, encoding)
             for v in o
             })
    raise TypeError(f"unhandled type for o {o!r}")


@_export
def encode_strings(o, encoding='ascii'):
    """
    Converts an object o from str to bytes.
    If o is a container, recursively converts
    all objects and containers inside.

    o and all objects inside o must be either
    bytes, str, dict, set, list, tuple, or a subclass
    of one of those.

    Encodes every string inside using the encoding
    specified in the 'encoding' parameter, default
    is 'ascii'.

    Handles nested containers.

    If o is of, or contains, a type not listed above,
    raises TypeError.
    """
    return _recursive_encode_strings(o, encoding)


# Tuples enumerating all the whitespace and newline characters,
# for use with big functions taking "separators" arguments
# (e.g. lines, multisplit).  For an explanation of what they
# represent, please see the "Whitespace and line-breaking
# characters in Python and big" deep-dive in big's README.

_export_name('str_whitespace')
str_whitespace = (
    # char    decimal   hex      identity
    ##########################################
    '\t'    , #     9 - 0x0009 - tab
    '\n'    , #    10 - 0x000a - newline
    '\v'    , #    11 - 0x000b - vertical tab
    '\f'    , #    12 - 0x000c - form feed
    '\r'    , #    13 - 0x000d - carriage return
    '\r\n'  , # bonus! the classic DOS newline sequence!

    ###################################################
    ## Note: Unicode doesn't consider these next four
    ## ASCII "separator" characters to be whitespace!
    ## (I agree, I think this is a Python bug.)
    ###################################################
    '\x1c'  , #    28 - 0x001c - file separator
    '\x1d'  , #    29 - 0x001d - group separator
    '\x1e'  , #    30 - 0x001e - record separator
    '\x1f'  , #    31 - 0x001f - unit separator

    ' '     , #    32 - 0x0020 - space
    '\x85'  , #   133 - 0x0085 - next line
    '\xa0'  , #   160 - 0x00a0 - non-breaking space
    '\u1680', #  5760 - 0x1680 - ogham space mark
    '\u2000', #  8192 - 0x2000 - en quad
    '\u2001', #  8193 - 0x2001 - em quad
    '\u2002', #  8194 - 0x2002 - en space
    '\u2003', #  8195 - 0x2003 - em space
    '\u2004', #  8196 - 0x2004 - three-per-em space
    '\u2005', #  8197 - 0x2005 - four-per-em space
    '\u2006', #  8198 - 0x2006 - six-per-em space
    '\u2007', #  8199 - 0x2007 - figure space
    '\u2008', #  8200 - 0x2008 - punctuation space
    '\u2009', #  8201 - 0x2009 - thin space
    '\u200a', #  8202 - 0x200a - hair space
    '\u2028', #  8232 - 0x2028 - line separator
    '\u2029', #  8233 - 0x2029 - paragraph separator
    '\u202f', #  8239 - 0x202f - narrow no-break space
    '\u205f', #  8287 - 0x205f - medium mathematical space
    '\u3000', # 12288 - 0x3000 - ideographic space
    )
_export_name('str_whitespace_without_crlf')
str_whitespace_without_crlf = tuple(s for s in str_whitespace if s != '\r\n')

_export_name('whitespace')
whitespace = str_whitespace
_export_name('whitespace_without_crlf')
whitespace_without_crlf = str_whitespace_without_crlf

# Whitespace as defined by Unicode.  The same as Python's definition,
# except we remove the four ASCII separator characters.
_export_name('unicode_whitespace')
unicode_whitespace = tuple(s for s in str_whitespace if not ('\x1c' <= s <= '\x1f'))
_export_name('unicode_whitespace_without_crlf')
unicode_whitespace_without_crlf = tuple(s for s in unicode_whitespace if s != '\r\n')

# Whitespace as defined by ASCII.  The same as Unicode,
# but only within the first 128 code points.
# Note: these are still *str* objects.
_export_name('ascii_whitespace')
ascii_whitespace = tuple(s for s in unicode_whitespace if (s < '\x80'))
_export_name('ascii_whitespace_without_crlf')
ascii_whitespace_without_crlf = tuple(s for s in ascii_whitespace if s != '\r\n')

# Whitespace as defined by the Python bytes object.
# Bytes objects, using the ASCII encoding.
_export_name('bytes_whitespace')
bytes_whitespace = encode_strings(ascii_whitespace)
_export_name('bytes_whitespace_without_crlf')
bytes_whitespace_without_crlf = tuple(s for s in bytes_whitespace if s != b'\r\n')


_export_name('str_linebreaks')
str_linebreaks = (
    # char    decimal   hex      identity
    ##########################################
    '\n'    , #   10 - 0x000a - newline
    '\v'    , #   11 - 0x000b - vertical tab
    '\f'    , #   12 - 0x000c - form feed
    '\r'    , #   13 - 0x000d - carriage return
    '\r\n'  , # bonus! the classic DOS newline sequence!
    '\x1c'  , #   28 - 0x001c - file separator
    '\x1d'  , #   29 - 0x001d - group separator
    '\x1e'  , #   30 - 0x001e - record separator
    '\x85'  , #  133 - 0x0085 - next line
    '\u2028', # 8232 - 0x2028 - line separator
    '\u2029', # 8233 - 0x2029 - paragraph separator

    # What about '\n\r'?
    # Sorry, Acorn and RISC OS users, you'll have to add this yourselves.
    # I'm worried it would cause bugs with a malformed DOS string,
    # or maybe when operating in reverse mode.
    #
    # Also: welcome, Acorn and RISC OS users!
    # What are you doing here?  You can't run Python 3.6+!
    )
_export_name('str_linebreaks_without_crlf')
str_linebreaks_without_crlf = tuple(s for s in str_linebreaks if s != '\r\n')

_export_name('linebreaks')
linebreaks = str_linebreaks
_export_name('linebreaks_without_crlf')
linebreaks_without_crlf = str_linebreaks_without_crlf

# Whitespace as defined by Unicode.  The same as Python's definition,
# except we again remove the four ASCII separator characters.
_export_name('unicode_linebreaks')
unicode_linebreaks = tuple(s for s in str_linebreaks if not ('\x1c' <= s <= '\x1f'))
_export_name('unicode_linebreaks_without_crlf')
unicode_linebreaks_without_crlf = tuple(s for s in unicode_linebreaks if s != '\r\n')

# Linebreaks as defined by ASCII.  The same as Unicode,
# but only within the first 128 code points.
# Note: these are still *str* objects.
_export_name('ascii_linebreaks')
ascii_linebreaks = tuple(s for s in unicode_linebreaks if s < '\x80')
_export_name('ascii_linebreaks_without_crlf')
ascii_linebreaks_without_crlf = tuple(s for s in ascii_linebreaks if s != '\r\n')

# Whitespace as defined by the Python bytes object.
# Bytes objects, using the ASCII encoding.
#
# Notice that bytes_linebreaks doesn't contain \v or \f.
# That's because the Python bytes object doesn't consider those
# to be linebreak characters.
#
#    >>> define is_newline_str(c): return len( ("a"+c+"x").splitlines() ) > 1
#    >>> is_newline_str('\n')
#    True
#    >>> is_newline_str('\r')
#    True
#    >>> is_newline_str('\f')
#    True
#    >>> is_newline_str('\v')
#    True
#
#    >>> define is_newline_byte(c): return len( (b"a"+c+b"x").splitlines() ) > 1
#    >>> is_newline_byte(b'\n')
#    True
#    >>> is_newline_byte(b'\r')
#    True
#    >>> is_newline_byte(b'\f')
#    False
#    >>> is_newline_byte(b'\v')
#    False
#
# However! with defensive programming, in case this changes in the future
# (as it should!), big will automatically still agree with Python.
#
# p.s. in the above code examples, you have to put characters around the
# linebreak character, because str.splitlines (and bytes.splitlines)
# rstrips the string of linebreak characters before it splits lines, sigh.

_export_name('bytes_linebreaks')
bytes_linebreaks = (
    b'\n'    , #   10 0x000a - newline
    )

if len(b'x\vx'.splitlines()) == 2: # pragma: nocover
    bytes_linebreaks += (
        '\v'    , #   11 - 0x000b - vertical tab
        )

if len(b'x\fx'.splitlines()) == 2: # pragma: nocover
    bytes_linebreaks += (
        '\f'    , #   12 - 0x000c - form feed
        )

bytes_linebreaks += (
    b'\r'    , #   13 0x000d - carriage return
    b'\r\n'  , # bonus! the classic DOS newline sequence!
    )

_export_name('bytes_linebreaks_without_crlf')
bytes_linebreaks_without_crlf = tuple(s for s in bytes_linebreaks if s != b'\r\n')



# reverse an iterable thing.
# o must be str, bytes, list, tuple, set, or frozenset.
# if o is a collection (not str or bytes),
# the elements of o are recursively reversed.
# value returned is the same type as o.
#
# we don't need to bother checking the type of o.
# _multisplit_reversed is an internal function
# and I've manually checked every call site.
def _multisplit_reversed(o, name='s'):
    if isinstance(o, str):
        if len(o) <= 1:
            return o
        return "".join(reversed(o))
    if isinstance(o, bytes):
        if len(o) <= 1:
            return o
        return b"".join(o[i:i+1] for i in range(len(o)-1, -1, -1))
    # assert isinstance(o, (list, tuple, set, frozenset))
    t = type(o)
    return t(_multisplit_reversed(p) for p in o)


# _reversed_builtin_separators precalculates the reversed versions
# of the builtin separators.  we use the reversed versions when
# reverse=True.  this is a minor speed optimization, particularly
# as it helps with the lrucache for _separators_to_re.
#
# we test that these cached versions are correct in tests/test_text.py.
#

_reversed_builtin_separators = {
    str_whitespace: str_whitespace_without_crlf + ('\n\r',),
    str_whitespace_without_crlf: str_whitespace_without_crlf,

    unicode_whitespace: unicode_whitespace_without_crlf + ('\n\r',),
    unicode_whitespace_without_crlf: unicode_whitespace_without_crlf,

    ascii_whitespace: ascii_whitespace_without_crlf + ("\n\r",),
    ascii_whitespace_without_crlf: ascii_whitespace_without_crlf,

    str_linebreaks: str_linebreaks_without_crlf + ("\n\r",),
    str_linebreaks_without_crlf: str_linebreaks_without_crlf,

    unicode_linebreaks: unicode_linebreaks_without_crlf + ("\n\r",),
    unicode_linebreaks_without_crlf: unicode_linebreaks_without_crlf,

    bytes_linebreaks: bytes_linebreaks_without_crlf + (b"\n\r",),
    bytes_linebreaks_without_crlf: bytes_linebreaks_without_crlf,
    }


def _re_quote(s):
    # don't bother escaping whitespace.
    # re.escape escapes whitespace because of VERBOSE mode,
    # which we're not using.  (escaping the whitespace doesn't
    # hurt anything really, but it makes the patterns harder
    # to read for us humans.)
    if not s.isspace():
        return re.escape(s)
    if len(s) > 1:
        if isinstance(s, bytes):
            return b"(?:" + s + b")"
        return f"(?:{s})"
    return s


@_export
def re_partition(s, pattern, count=1, *, flags=0, reverse=False):
    """
    Like str.partition, but pattern is matched as a regular expression.

    s can be either a str or bytes object.

    pattern can be a str, bytes, or re.Pattern object.

    s and pattern (or pattern.pattern) must be the same type.

    If pattern is found in s, returns a tuple
        (before, match, after)
    where before is the text before the match,
    match is the re.Match object resulting from the match, and
    after is the text after the match.

    If pattern appears in s multiple times,
    re_partition will match against the first (leftmost)
    appearance.

    If pattern is not found in s, returns a tuple
        (s, None, '')
    where the empty string is str or bytes as appropriate.

    To convert the output into a tuple of strings like str.partition,
    use
        t = re_partition(...)
        t2 = (t[0], t[1].group(0) if t[1] else '', t[2])

    Passing in an explicit "count" lets you control how many times
    re_partition partitions the string.  re_partition will always
    return a tuple containing (2*count)+1 elements, and
    odd-numbered elements will be either re.Match objects or None.
    Passing in a count of 0 will always return a tuple containing s.

    If pattern is a string or bytes, flags is passed in
    as the flags argument to re.compile.

    If reverse is true, partitions starting at the right,
    like re_rpartition.

    You can pass in an instance of a subclass of bytes or str
    for s and pattern (or pattern.pattern), but the base class
    for both must be the same (str or bytes).  re_partition will
    only return str or bytes objects.

    (In older versions of Python, re.Pattern was a private type called
    re._pattern_type.)
    """
    if reverse:
        return re_rpartition(s, pattern, count, flags=flags)

    # writing it this way means the extension tuples are precompiled constants
    if isinstance(s, bytes):
        empty = b''
        extension = (None, b'')
    else:
        empty = ''
        extension = (None, '')

    if not isinstance_re_pattern(pattern):
        pattern = re.compile(pattern, flags=flags)

    # optimized fast path for the most frequent use case
    if count == 1:
        match = pattern.search(s)
        if not match:
            return (s, None, empty)
        before, separator, after = s.partition(match.group(0))
        return (before, match, after)

    if count == 0:
        return (s,)

    if count < 0:
        raise ValueError("count must be >= 0")

    result = []
    extend = result.extend
    matches_iterator = pattern.finditer(s)

    try:
        for remaining in range(count, 0, -1):
            match = next(matches_iterator)
            before, separator, s = s.partition(match.group(0))
            extend((before, match))
        extension = ()
    except StopIteration:
        extension *= remaining

    result.append(s)
    return tuple(result) + extension


# internal generator function
def reversed_re_finditer(pattern, string):
    # matches are found by re.search *going forwards.*
    # but what we need here is the *reverse* matches.
    #
    # consider this call:
    #    re_rpartition('abcdefgh', '(abcdef|efg|ab|b|c|d)', count=4)
    #
    # re.finditer with that string and pattern yields one match:
    #    'abcdef'
    # but reverse searching, e.g. with
    # regex.finditer(flags=regex.REVERSE), yields four matches:
    #    'efg', 'd', 'c', 'ab'
    #
    # so what we do is: we ask re.finditer for all the forward
    # matches.  then, for every match it found, we check every
    # overlapping character to see if there's a different match
    # there that we might prefer.  if we prefer one of those,
    # we yield that--but we keep around the other matches,
    # because one of those (or a truncated version of it) might
    # also work.


    # matches and overlapping_matches are lists of 3-tuples of:
    #    (end_pos, -start_pos, match)
    # If we sort one of those lists, the last element will be
    # the correct last match in "reverse" order.  See
    #    https://en.wikipedia.org/wiki/Schwartzian_transform
    #
    # matches contains the list of matches we got directly from
    # re.finditer(), reversed.  since this was found using re in
    # "forward" order, we need to check every match in this list
    # for potential overlapping matches.
    matches = [(match.end(), -match.start(), match) for match in pattern.finditer(string)]
    if not matches:
        # print(f"no matches at all! exiting immediately.")
        return

    # Does this pattern match zero-length strings?
    zero_length_match = pattern.match(string, 0, 0)
    if zero_length_match:
        # This pattern matches zero-length strings.
        # Since the rules are a little different for
        # zero-length strings when in reverse mode,
        # we need to doctor the match results a little.

        # These seem to be the rules:
        #
        # In forwards mode, we consider two matches to overlap
        # if they start at the same position, or if they have
        # any characters in common.  There's an implicit
        # zero-length string at the beginning and end of every
        # string, so if the pattern matches against a zero-length
        # string at the start or end, and there isn't another
        # (longer) match that starts at that position, we'll
        # yield these matches too.  Since only a zero-length
        # match can start at position len(string), we'll always
        # yield a zero-length match starting and ending at
        # position length(string) if the pattern matches there.
        #
        # In reverse mode, we consider two matches to overlap
        # if they end at the same position, or if they have any
        # characters in common with any other match.  There's an
        # implicit zero-length string at the beginning and end of
        # every string, so if the pattern matches a zero-length
        # string at the start or end, and there isn't another
        # (longer) match that ends at that position, we'll yield
        # these matches too.  Since only a zero-length match can
        # end at position 0, we'll always yield a zero-length
        # match starting and ending at position 0 if the pattern
        # matches there.

        # We need to ensure that, for every non-zero-length match,
        # if the pattern matches a zero-length string starting at
        # the same position, we have that zero-length match in
        # matches too.
        #
        # So specifically we're going to do this:
        #
        # for every match m in matches:
        #   if m has nonzero length,
        #     and the pattern matches a zero-length string
        #       starting at m,
        #     ensure that the zero-length match is also in matches.
        #   elif m has zero length,
        #     if we've already ensured that a zero-length
        #     match starting at m.start() is in matches,
        #     discard m.

        zeroes = set()
        new_matches = []
        append = new_matches.append
        last_start = -1
        for t in matches:
            match = t[2]
            start, end = match.span()

            if start not in zeroes:
                if (start == end):
                    append(t)
                    zeroes.add(start)
                    continue

                zero_match = pattern.match(string, start, start)
                if zero_match:
                    t_zero_length = (start, -start, zero_match)
                    append(t_zero_length)
                zeroes.add(start)
            append(t)
        # del zeroes
        matches = new_matches

    matches.sort()

    # overlapping_matches is a list of the possibly-viable
    # overlapping matches we found from checking a match
    # we got from "matches".
    overlapping_matches = []

    result = []
    match = None

    # We truncate each match at the start
    # of the previously yielded match.
    #
    # The initial value allows the initial match
    # to extend all the way to the end of the string.
    previous_match_start = len(string)

    # cache some method lookups
    pattern_match = pattern.match
    append = overlapping_matches.append

    while True:
        if overlapping_matches:
            # overlapping_matches contains the overlapping
            # matches found *last* time around, before we
            # yielded the most recent match.
            #
            # The thing is, some of these matches might overlap that match.
            # But we only yield *non*-overlapping matches.  So we need to
            # filter the matches in overlapping_matches accordingly.

            truncated_matches = []
            # (overlapping_matches will be set to truncated_matches in a few lines)
            append = truncated_matches.append

            for t in overlapping_matches:
                end, negated_start, match = t
                start = -negated_start
                if start > previous_match_start:
                    # This match starts *after* the previous match started.
                    # All matches starting at this position are no longer
                    # viable.  Throw away the match.
                    continue
                if end <= previous_match_start:
                    # This match ends *before* the previous match started.
                    # In other words, this match is still 100% viable.
                    # Keep it, we don't need to change it at all.
                    append(t)
                    continue

                # This match starts before the previous match started,
                # but ends after the previous match start.
                # In other words, it overlaps the previous match.
                #
                # So this match is itself no longer viable.  But!
                # There might be a *different* match starting at this
                # position in the string.  So we do a fresh re.match here,
                # stopping at the start of the previously yielded match.
                # (That's the third parameter, "endpos".)

                match = pattern_match(string, start, previous_match_start)
                if match:
                    append((match.end(), -start, match))

            overlapping_matches = truncated_matches

        if (not overlapping_matches) and matches:
            # We don't currently have any pre-screened
            # overlapping matches we can use.
            #
            # But we *do* have a match (or matches) found in forwards mode.
            # Grab the next one that's still viable.

            scan_for_overlapping_matches = False
            while matches:
                t = matches.pop()
                end, negated_start, match = t
                start = -negated_start
                if end <= previous_match_start:
                    assert start <= previous_match_start
                    append(t)
                    start += 1
                    scan_for_overlapping_matches = True
                    break

            if scan_for_overlapping_matches:
                # We scan every** position inside the match for an
                # overlapping match.  All the matches we find go in
                # overlapping_matches, then we sort it and yield
                # the last one.
                #
                # ** We don't actually need to check the *first* position,
                #    "start", because we already know what we'll find:
                #    the match that we got from re.finditer() and
                #    scanned for overlaps.
                #
                # As mentioned, the match we got from finditer
                # is viable here, so add it to the list.

                end = min(end, previous_match_start)
                for pos in range(start, end):
                    match = pattern_match(string, pos, previous_match_start)
                    if match:
                        # print(f"  found {match=}")
                        append((match.end(), -pos, match))

        if not overlapping_matches:
            # matches and overlapping matches are both empty.
            # We've exhausted the matches.  Stop iterating.
            return

        # overlapping_matches is now guaranteed current and non-empty.
        # We sort it so the rightmost match is last, and yield that.
        overlapping_matches.sort()
        match = overlapping_matches.pop()[2]
        previous_match_start = match.start()
        yield match

_reversed_re_finditer = reversed_re_finditer

@_export
def reversed_re_finditer(pattern, string, flags=0):
    """
    A generator function.  Behaves almost identically to the Python
    standard library function re.finditer, yielding non-overlapping
    matches of "pattern" in "string".  The difference is,
    reversed_re_finditer searches "string" from right to left.

    pattern can be str, bytes, or a precompiled re.Pattern object.
    If it's str or bytes, it'll be compiled with re.compile using
    the flags you passed in.

    string should be the same type as pattern (or pattern.pattern).
    """
    if not isinstance_re_pattern(pattern):
        pattern = re.compile(pattern, flags=flags)

    return _reversed_re_finditer(pattern, string)


@_export
def re_rpartition(s, pattern, count=1, *, flags=0):
    """
    Like str.rpartition, but pattern is matched as a regular expression.

    s can be a string or a bytes object.

    pattern can be a string, bytes, or an re.Pattern object.

    s and pattern (or pattern.pattern) must be the same type.

    If pattern is found in s, returns a tuple
        (before, match, after)
    where before is the text before the match,
    match is the re.Match object resulting from the match, and
    after is the text after the match.

    re_rpartition searches for pattern in s from right
    to left, and partitions at the non-overlapping
    matches it finds.

    If pattern matches multiple substrings of s, re_partition
    will match against the last (rightmost) appearance.

    If pattern is not found in s, returns a tuple
        ('', None, s)
    where the empty string is str or bytes as appropriate.

    To convert the output into a tuple of strings like str.rpartition,
    use
        t = re_rpartition(...)
        t2 = (t[0], t[1].group(0) if t[1] else '', t[2])

    Passing in an explicit "count" lets you control how many times
    re_rpartition partitions the string.  re_rpartition will always
    return a tuple containing (2*count)+1 elements, and
    odd-numbered elements will be either re.Match objects or None.
    Passing in a count of 0 will always return a tuple containing s.

    If pattern is a string, flags is passed in
    as the flags argument to re.compile.

    You can pass in an instance of a subclass of bytes or str
    for s and pattern (or pattern.pattern), but the base class
    for both must be the same (str or bytes).  re_rpartition will
    only return str or bytes objects.

    You can pass in a regex Pattern object (see the PyPi 'regex'
    package).  Patterns using the "Reverse Searching" feature
    of 'regex' (the REVERSE flag or the '(?r)' token) are unsupported.

    (In older versions of Python, re.Pattern was a private type called
    re._pattern_type.)
    """

    # writing it this way means the extension tuples are precompiled constants
    if isinstance(s, bytes):
        empty = b''
        extension = (b'', None)
    else:
        empty = ''
        extension = ('', None)

    # optimized fast path for the most frequent use case
    if count == 1:
        matches_iterator = reversed_re_finditer(pattern, s, flags)
        try:
            match = next(matches_iterator)
            before, separator, after = s.rpartition(match.group(0))
            return (before, match, after)
        except StopIteration:
            return (empty, None, s)

    if count == 0:
        return (s,)

    if count < 0:
        raise ValueError("count must be >= 0")

    result = []
    extend = result.extend
    matches_iterator = reversed_re_finditer(pattern, s, flags)

    try:
        for remaining in range(count, 0, -1):
            match = next(matches_iterator)
            s, separator, after = s.rpartition(match.group(0))
            extend((after, match))
        extension = ()
    except StopIteration:
        extension *= remaining

    result.append(s)
    result.reverse()
    return extension + tuple(result)


@functools.lru_cache(re._MAXCACHE)
def __separators_to_re(separators, separators_is_bytes, separate=False, keep=False):
    if separators_is_bytes:
        pipe = b'|'
        separate_start = b'(?:'
        separate_end = b')+'
        keep_start = b'('
        keep_end = b')'
    else:
        pipe = '|'
        separate_start = '(?:'
        separate_end = ')+'
        keep_start = '('
        keep_end = ')'

    # sort longer separator strings earlier.
    # re processes | operator from left-to-right,
    # so you want to match against longer strings first.
    separators = list(separators)
    separators.sort(key=lambda o: -len(o))
    pattern = pipe.join(_re_quote(o) for o in separators)
    if not separate:
        pattern = separate_start + pattern + separate_end
    if keep:
        pattern = keep_start + pattern + keep_end
    return pattern

def _separators_to_re(separators, separators_is_bytes, separate=False, keep=False):
    # this ensures that separators is hashable,
    # which will keep functools.lru_cache happy.
    try:
        hash(separators)
    except TypeError:
        separators = tuple(separators)
    return __separators_to_re(separators, separators_is_bytes, separate=bool(separate), keep=bool(keep))



@_export
def multistrip(s, separators, left=True, right=True):
    """
    Like str.strip, but supports stripping multiple strings.

    Strips from the string "s" all leading and trailing
    instances of strings found in "separators".

    Returns a copy of s with the leading and/or trailing
    separators stripped.  (If left and right are both false,
    the contents are unchanged.)

    s should be str or bytes.
    separators should be an iterable of either str or bytes
    objects matching the type of s.

    If left is a true value, strips all leading separators
    from s.

    If right is a true value, strips all trailing separators
    from s.

    multistrip first removes leading separators, until the
    string does not start with a separator (or is empty).
    Then it removes trailing separators, until the string
    until the string does not end with a separator (or is
    empty).

    multistrip is "greedy"; if more than one separator
    matches, multistrip will strip the longest one.

    You can pass in an instance of a subclass of bytes or str
    for s and elements of separators, but the base class
    for both must be the same (str or bytes).  multistrip will
    only return str or bytes objects, even if left and right
    are both false.
    """

    is_bytes = isinstance(s, bytes)
    if is_bytes:
        s_type = bytes
        head = b'^'
        tail = b'$'

        if isinstance(separators, str):
            raise TypeError("separators must be an iterable of non-empty objects the same type as s")
        if isinstance(separators, bytes):
            # not iterable of bytes, literally a bytes string.
            # split it ourselves.  otherwise, _separators_to_re will
            # iterate over it, which... yields integers! oops!
            separators = tuple(_iterate_over_bytes(separators))
            check_separators = False
        else:
            check_separators = True
    else:
        s_type = str
        head = '^'
        tail = '$'

        if isinstance(separators, bytes):
            raise TypeError("separators must be an iterable of non-empty objects the same type as s")
        if isinstance(separators, str):
            separators = tuple(separators)
            check_separators = False
        else:
            check_separators = True

    if not separators:
        raise ValueError("separators must be an iterable of non-empty objects the same type as s")
    if check_separators:
        s2 = []
        for o in separators:
            if not isinstance(o, s_type):
                raise TypeError("separators must be an iterable of non-empty objects the same type as s")
            if not o:
                raise ValueError("separators must be an iterable of non-empty objects the same type as s")
            s2.append(o)
        separators = tuple(s2)

    # deliberately do this *after* checking types,
    # so we complain about bad types even if this is a do-nothing call.
    if not (left or right):
        return s

    # We can sidestep the hashability test of _separators_to_re.
    # separators is always guaranteed to be a tuple at this point.
    pattern = __separators_to_re(separators, is_bytes, separate=False, keep=False)

    if left:
        left_match = re.match(head + pattern, s)
        if left_match:
            start = left_match.end(0)
            s = s[start:]
    if right:
        right_match = re.search(pattern + tail, s)
        if right_match:
            end = right_match.start(0)
            s = s[:end]
    return s


# for keep
AS_PAIRS="AS_PAIRS"
_export_name(AS_PAIRS)
ALTERNATING="ALTERNATING"
_export_name(ALTERNATING)

# for strip
LEFT = "LEFT"
_export_name(LEFT)
RIGHT = "RIGHT"
_export_name(RIGHT)
PROGRESSIVE = "PROGRESSIVE"
_export_name(PROGRESSIVE)

def multisplit(s, separators, keep, maxsplit, reverse, separate, strip, empty, is_bytes, separators_to_re_keep):
    if maxsplit == None:
        maxsplit = -1
    elif maxsplit == 0:
        if keep == ALTERNATING:
            yield s
        elif keep == AS_PAIRS:
            yield (s, empty)
        else:
            yield s
        return

    # convert maxsplit for use with re.split.
    #
    # re.split interprets maxsplit slightly differently:
    #   its maxsplit==0 means "allow all splits".
    #   its maxsplit==1 means "only allow one split".
    #
    # (re.split doesn't have a way to express
    #  "don't split" with its maxsplit parameter,
    #  which is why we handled it already.)
    re_split_maxsplit = 0 if maxsplit == -1 else maxsplit

    if reverse:
        # if reverse is true, when separators overlap,
        # we need to prefer the rightmost one rather than
        # the leftmost one.  how do we do *that*?
        # Eric Smith had the brainstorm: reverse the string
        # and the separators, split, and reverse the output
        # and the strings in the output.
        s = _multisplit_reversed(s, 's')
        separators = tuple(separators)
        s2 = _reversed_builtin_separators.get(separators, None)
        if s2 != None:
            separators = s2
        else:
            separators = _multisplit_reversed(separators, 'separators')

    pattern = _separators_to_re(separators, is_bytes, keep=separators_to_re_keep, separate=separate)

    l = re.split(pattern, s, re_split_maxsplit)

    if strip == PROGRESSIVE:
        # l alternates nonsep and sep strings.
        # it's always an odd length, starting and ending with nonsep.
        length = len(l)
        assert length & 1

        desired_length = 1 + (2*maxsplit)

        # dang! this is complicated!
        # maxsplit has to extend *past* the last nonsep
        # for us to strip on the far side.
        #  ' a b c   '.split(None, maxsplit=2) => ['a', 'b', 'c   ']
        #  ' a b c   '.split(None, maxsplit=3) => ['a', 'b', 'c']
        for i in range(length - 1, 0, -2):
            nonsep = l[i]
            if nonsep:
                last_non_empty_nonsep = i
                break
        else:
            last_non_empty_nonsep = 0

        if desired_length > (last_non_empty_nonsep + 2):
            # strip!
            l = l[:last_non_empty_nonsep + 1]
            desired_length = length = last_non_empty_nonsep

        if not keep:
            for i in range(len(l) - 2, 0, -2):
                del l[i]

    # we used to reverse the list three times in reverse mode!
    # _multisplit_reversed returns a reversed list.
    # then we'd reverse it to make it forwards-y.
    # then we'd reverse it again to pop elements off.
    # insane, right?
    #
    # now we observe and preserve the reversed-ness of the list
    # as appropriate.

    if reverse:
        l = _multisplit_reversed(l, 'l')

    if not keep:
        if not reverse:
            l.reverse()
        while l:
            yield l.pop()
        return

    # from here on out, we're 'keep'-ing the separator strings.
    # (we're returning the separator strings in one form or another.)

    if keep == ALTERNATING:
        if not reverse:
            l.reverse()
        while l:
            yield l.pop()
        return

    append_empty = (len(l) % 2) == 1
    if reverse:
        if append_empty:
            l.insert(0, empty)
    else:
        if append_empty:
            l.append(empty)
        l.reverse()

    previous = None
    while l:
        o = l.pop()
        if previous is None:
            previous = o
            continue
        if keep == AS_PAIRS:
            yield (previous, o)
        else:
            yield previous + o
        previous = None

_multisplit = multisplit


@_export
def multisplit(s, separators=None, *,
    keep=False,
    maxsplit=-1,
    reverse=False,
    separate=False,
    strip=False,
    ):
    """
    Splits strings like str.split, but with multiple separators and options.

    s can be str or bytes.

    separators should either be None (the default),
    or an iterable of str or bytes, matching s.

    If separators is None and s is str, multisplit will
    use big.whitespace as the list of separators.
    If separators is None and s is bytes, multisplit will
    use big.ascii_whitespace as the list of separators.

    Returns an iterator yielding the strings split from s.  If keep
    is true (or ALTERNATING), and strip is false, joining these strings
    together will recreate s.

    multisplit is "greedy": if two or more separators start at the same
    location in "s", multisplit splits using the longest matching separator.
    For example:
        big.multisplit('wxabcyz', ('a', 'abc'))
    yields 'wx' then 'yz'.

    "keep" indicates whether or not multisplit should keep the separator
    strings.  It supports four values:
        false (the default)
            Discard the separators.
        true (apart from ALTERNATING and AS_PAIRS)
            Append the separators to the end of the split strings.
            You can recreate the original string by passing the
            list returned in to ''.join.
        ALTERNATING
            Yield alternating strings in the output: strings consisting
            of separators, alternating with strings consisting of
            non-separators.  If "separate" is true, separator strings
            will contain exactly one separator, and non-separator strings
            may be empty; if "separate" is false, separator strings will
            contain one or more separators, and non-separator strings
            will never be empty.
            You can recreate the original string by passing the
            list returned in to ''.join.
        AS_PAIRS
            Yield 2-tuples containing a non-separator string and its
            subsequent separator string.  Either string may be empty;
            the separator string in the last 2-tuple will always be
            empty, and if `s` ends with a separator string, *both*
            strings in the final 2-tuple will be empty.

    "separate" indicates whether multisplit should consider adjacent
    separator strings in s as one separator or as multiple separators
    each separated by a zero-length string.  It supports two values:
        false (the default)
            Multiple adjacent separators should be considered one
            separator.
        true
            Don't group separators together.  Each separator should
            split the string individually, even if there are no
            characters between two separators.

    "strip" indicates whether multisplit should strip separators from
    the beginning and/or end of s, a la multistrip.  It supports
    six values:
        false (the default)
            Don't strip separators from the beginning or end of s.
        true (apart from LEFT, RIGHT, and PROGRESSIVE)
            Strip separators from the beginning and end of s
            (a la str.strip).
        LEFT
            Strip separators only from the beginning of s
            (a la str.lstrip).
        RIGHT
            Strip separators only from the end of s
            (a la str.rstrip).
        PROGRESSIVE
            Strip from the beginning and end of s, unless maxsplit
            is nonzero and the entire string is not split.  If
            splitting stops due to maxsplit before the entire string
            is split, and reverse is false, don't strip the end of
            the string. If splitting stops due to maxsplit before
            the entire string is split, and reverse is true, don't
            strip the beginning of the string.  (This is how str.strip
            and str.rstrip behave when sep=None.)

    "maxsplit" should be either an integer or None.  If maxsplit is an
    integer greater than -1, multisplit will split s no more than
    maxsplit times.

    "reverse" controls whether multisplit splits starting from the
    beginning or from the end of the string.  It supports two values:
        false (the default)
            Start splitting from the beginning of the string
            and scanning right.
        true
            Start splitting from the end of the string and
            scanning left.
    Splitting from the end of the string and scanning left has two
    effects.  First, if maxsplit is a number greater than 0,
    the splits will start at the end of the string rather than
    the beginning.  Second, if there are overlapping instances of
    separators in the string, multisplit will prefer the rightmost
    separator rather than the left.  For example:
        multisplit("A x x Z", (" x ",), keep=big.ALTERNATING)
    will split on the leftmost instance of " x ", yielding
        "A", " x ", "x Z"
    whereas
        multisplit("A x x Z", (" x ",), keep=big.ALTERNATING, reverse=True)
    will split on the rightmost instance of " x ", yielding
        "A x", " x ", "Z"

    You can pass in an instance of a subclass of bytes or str
    for s and elements of separators, but the base class
    for both must be the same (str or bytes).  multisplit will
    only return str or bytes objects.
    """
    is_bytes = isinstance(s, bytes)
    separators_is_bytes = isinstance(separators, bytes)
    separators_is_str = isinstance(separators, str)

    if is_bytes:
        if separators_is_bytes:
            # not iterable of bytes, literally a bytes string.
            # split it ourselves.
            separators = tuple(_iterate_over_bytes(separators))
            check_separators = False
        else:
            if separators_is_str:
                raise TypeError(f"separators must be either None or an iterable of objects the same type as s; s is {type(s).__name__}, separators is {separators!r}")
            check_separators = True
        empty = b''
        s_type = bytes
    else:
        if separators_is_bytes:
            raise TypeError(f"separators must be either None or an iterable of objects the same type as s; s is {type(s).__name__}, separators is {separators!r}")
        check_separators = True
        empty = ''
        s_type = str

    if separators is None:
        separators = bytes_whitespace if is_bytes else whitespace
        check_separators = False
    elif not separators:
        raise ValueError(f"separators must be either None or an iterable of objects the same type as s; s is {type(s).__name__}, separators is {separators!r}")

    # check_separators is True if separators isn't str or bytes
    # or something we split ourselves.
    if check_separators:
        if not hasattr(separators, '__iter__'):
            raise TypeError(f"separators must be either None or an iterable of objects the same type as s; s is {type(s).__name__}, separators is {separators!r}")
        for o in separators:
            if not isinstance(o, s_type):
                raise TypeError(f"separators must be either None or an iterable of objects the same type as s; s is {type(s).__name__}, separators is {separators!r}")

    separators_to_re_keep = keep

    if strip:
        if strip == PROGRESSIVE:
            if maxsplit == -1:
                strip = left = right = True
            else:
                left = not reverse
                right = reverse
                separators_to_re_keep = True
        else:
            left = strip != RIGHT
            right = strip != LEFT
        s = multistrip(s, separators, left=left, right=right)
        if not s:
            # oops! all separators!
            # this will make us exit the iterator early.
            maxsplit = 0

    return _multisplit(s, separators, keep, maxsplit, reverse, separate, strip, empty, is_bytes, separators_to_re_keep)


@_export
def multipartition(s, separators, count=1, *, reverse=False, separate=True):
    """
    Like str.partition, but supports partitioning based on multiple separator
    strings, and can partition more than once.

    "s" can be str or bytes.

    "separators" should be an iterable of objects of the same type as "s".

    By default, if any of the strings in "separators" are found in "s",
    returns a tuple of three strings: the portion of "s" leading up to
    the earliest separator, the separator, and the portion of "s" after
    that separator.  Example:

        multipartition('aXbYz', ('X', 'Y')) => ('a', 'X', 'bYz')

    If none of the separators are found in the string, returns
    a tuple containing `s` unchanged followed by two empty strings.

    multipartition is *greedy*: if two or more separators appear at
    the leftmost location in `s`, multipartition partitions using
    the longest matching separator.  For example:

        big.multipartition('wxabcyz', ('a', 'abc')) => ('wx', 'abc', 'yz')

    Passing in an explicit "count" lets you control how many times
    multipartition partitions the string.  multipartition will always
    return a tuple containing (2*count)+1 elements.  Passing in a
    count of 0 will always return a tuple containing s.

    If `separate` is true, multiple adjacent separator strings behave
    like one separator.  Example:

        big.text.multipartition('aXYbYXc', ('X', 'Y',), count=2, separate=False) => ('a', 'XY', 'b', 'YX', 'c')
        big.text.multipartition('aXYbYXc', ('X', 'Y',), count=2, separate=True ) => ('a', 'X', '', 'Y', 'bYXc')

    If reverse is true, multipartition behaves like str.rpartition.
    It partitions starting on the right, scanning backwards through
    s looking for separators.

    You can pass in an instance of a subclass of bytes or str
    for s and elements of separators, but the base class
    for both must be the same (str or bytes).  multipartition
    will only yield str or bytes objects.
    """
    if count < 0:
        raise ValueError("count must be positive")
    result = list(multisplit(s, separators,
        keep=ALTERNATING,
        reverse=reverse,
        separate=separate,
        strip=False,
        maxsplit=count))
    desired_length = (2 * count) + 1
    result_length = len(result)
    if result_length < desired_length:
        if isinstance(s, bytes):
            empty = (b'',)
        else:
            empty = ('',)
        extension = empty * (desired_length - result_length)
        if reverse:
            result = list(extension) + result
        else:
            result.extend(extension)
    return tuple(result)

@_export
def multirpartition(s, separators, count=1, *, reverse=False, separate=True):
    return multipartition(s, separators, count=count, reverse=not reverse, separate=separate)


# I declare that, for our purposes,
#     ` (the "back-tick" character U+0060)
# is *not* an apostrophe.  it's a diacritical
# used to modify a letter, rather than a
# separator used to separate letters.
# It's been (ab)used as an apostrophe historically,
# but that's because ASCII had a limited number of
# punctuation characters.
apostrophes = unicode_apostrophes = "'‘’‚‛"
_export_name('apostrophes')
double_quotes = unicode_double_quotes = '"“”„‟«»‹›'
_export_name('double_quotes')

ascii_apostrophes = b"'"
_export_name('ascii_apostrophes')
ascii_double_quotes = b'"'
_export_name('ascii_double_quotes')

utf8_apostrophes = apostrophes.encode('utf-8')
_export_name('utf8_apostrophes')
utf8_double_quotes = double_quotes.encode('utf-8')
_export_name('utf8_double_quotes')


@_export
def split_title_case(s, *, split_allcaps=True):
    """
    Splits s into words, assuming that
    upper-case characters start new words.
    Returns an iterator yielding the split words.

    Example:
        list(split_title_case('ThisIsATitleCaseString'))
    is equal to
        ['This', 'Is', 'A', 'Title', 'Case', 'String']

    If split_allcaps is a true value (the default),
    runs of multiple uppercase characters will also
    be split before the last character.  This is
    needed to handle splitting single-letter words.
    Consider:
        list(split_title_case('WhenIWasATeapot', split_allcaps=True))
    returns
        ['When', 'I', 'Was', 'A', 'Teapot']
    but
        list(split_title_case('WhenIWasATeapot', split_allcaps=False))
    returns
        ['When', 'IWas', 'ATeapot']

    Note: uses the 'isupper' and 'islower' methods
    to determine what are upper- and lower-case
    characters.  This means it only recognizes the ASCII
    upper- and lower-case letters for bytes strings.
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

    for c in i:
        break
    assert c

    word = []
    append = word.append
    pop = word.pop
    clear = word.clear

    multiple_uppers = False

    while True:
        if c.islower():
            append(c)
            for c in i:
                if c.isupper():
                    yield empty_join(word)
                    clear()
                    break
                if c.islower():
                    append(c)
                    continue
                break
            else:
                break

        elif c.isupper():
            append(c)
            multiple_uppers = False
            for c in i:
                if c.isupper():
                    multiple_uppers = split_allcaps
                    append(c)
                    continue
                if c.islower():
                    if multiple_uppers:
                        previous = pop()
                        yield empty_join(word)
                        clear()
                        append(previous)
                break
            else:
                break
        else:
            append(c)
            for c in i:
                break
            else:
                break

    if word:
        yield empty_join(word)


def combine_splits(s, split_lengths):
    "The generator function returned by the public combine_splits function."
    split_lengths_pop = split_lengths.pop

    pops = 0

    heap_pop = heapq.heappop
    heap_push = heapq.heappush

    if len(split_lengths) >= 2:
        while True:
            smallest = split_lengths[0]
            index = smallest[0]

            snippet = s[:index]
            if snippet == s:
                # check, did they try to split past the end?
                if index > len(s):
                    raise ValueError("split array is longer than the original string")

            yield snippet
            s = s[index:]
            if not s:
                return

            # decrement the first value in every split array
            # by index.
            # (if every entry in a heapq is a list of integers, decrementing
            # the first integer in every list by the same amount maintains
            # the heap invariants.)
            for lengths in split_lengths:
                length = lengths[0]

                new_value = length - index
                # assert new_value >= 0
                if not new_value:
                    pops += 1

                # we write the zeros here, even though we're about to pop them off,
                # because otherwise we might break the heapq invariants.
                lengths[0] = new_value

            while pops:
                pops -= 1
                splits = heap_pop(split_lengths)
                if len(splits) > 1:
                    splits.pop(0)
                    heap_push(split_lengths, splits)

            if len(split_lengths) < 2:
                break

    if split_lengths:
        start = end = 0
        length = len(s)
        for index in split_lengths[0]:
            end += index
            if end > length:
                raise ValueError("split array is longer than the original string")
            yield s[start:end]
            start += index
        s = s[end:]

    if s:
        yield s

_combine_splits = combine_splits

@_export
def combine_splits(s, *split_arrays):
    """
    Takes a string, and one or more "split arrays",
    and applies all the splits to the string.  Returns
    an iterator of the resulting string segments.

    A "split array" is an array containing the original
    string, but split into multiple pieces.  For example,
    the string "a b c d e" could be split into the
    split array ["a ", "b ", "c ", "d ", "e"]

    For example,
        combine_splits('abcde', ['abcd', 'e'], ['a', 'bcde'])
    returns ['a', 'bcd', 'e'].

    Note that the split arrays *must* contain all the
    characters from s.  ''.join(split_array) must recreate s.
    combine_splits only examines the lengths of the strings
    in the split arrays, and makes no attempt to infer
    stripped characters.  (So, don't use the string's .split
    method to split, use big's multisplit with keep=True or
    keep=ALTERNATING.)
    """
    # Convert every entry in split_arrays to a list.
    # Measure the strings in the split arrays, ignoring empty splits.
    split_lengths = [ [ len(_) for _ in split  if _ ] for split in split_arrays ]

    # Throw away empty entries in split arrays.  (If one array was ['', '', ''], it would now be empty.)
    split_lengths = [ split  for split in split_lengths  if split ]

    heapq.heapify(split_lengths)

    return _combine_splits(s, split_lengths)


_in_word = "_in_word"
_after_whitespace = "_after_whitespace"
_after_whitespace_then_apostrophe_or_double_quote = "_after_whitespace_then_apostrophe_or_double_quote"
_after_whitespace_then_D_or_O = "_after_whitespace_then_D_or_O"
_after_whitespace_then_D_or_O_then_apostrophe = "_after_whitespace_then_D_or_O_then_apostrophe"

_default_str_is_apostrophe = frozenset(unicode_apostrophes).__contains__
_default_str_is_double_quote = frozenset(unicode_double_quotes).__contains__
_default_bytes_is_apostrophe = ascii_apostrophes.__eq__
_default_bytes_is_double_quote = ascii_double_quotes.__eq__
_str_do_contains = 'DO'.__contains__
_bytes_do_contains = b'DO'.__contains__

@_export
def gently_title(s, *, apostrophes=None, double_quotes=None):
    """
    Uppercase the first character of every word in s,
    and leave all other characters alone.

    (For the purposes of this algorithm, words are
    any blob of non-whitespace characters.)

    Capitalize the letter after an apostrophe if
        a) the apostrophe is after whitespace or a
           left parenthesis character ('(')
           (or is the first letter of the string), or
        b) if the apostrophe is after a letter O or D,
           and that O or D is after whitespace (or is
           the first letter of the string).  The O or D
           here will also be capitalized.
    Rule a) handles internally quoted strings:
            He Said 'No I Did Not'
        and contractions that start with an apostrophe
            'Twas The Night Before Christmas
    Rule b) handles certain Irish, French, and Italian
        names.
            Peter O'Toole
            Lord D'Arcy

    Capitalize the letter after a quote mark if
    the quote mark is after whitespace (or is the
    first letter of a string).

    A run of consecutive apostrophes and/or
    quote marks is considered one quote mark for
    the purposes of capitalization.

    s should be a str or bytes object.  s can also
    be an instance of a subclass of str or bytes,
    however, gently_title will only ever return a
    str or bytes object.

    If specified, apostrophes and double_quotes should
    an string, or iterable of strings, of the same type
    as s (or a conformant type).

    If apostrophes is false, gently_title will use a
    default value for apostrophes:
        If s is str, the default value is big.text.apostrophes,
        a string containing all Unicode code points that
        represent apostrophes.

        If s is bytes, the default value is
        big.text.ascii_apostrophes, which is the string b"'".

    If double_quotes is false, gently_title will use a
    default value for double_quotes:
        If s is str, the default value is big.text.double_quotes,
        a string containing all Unicode code points representing
        double-quote marks.

        If s is bytes, the default value is
        big.text.ascii_double_quotes, which is the string b"'".
    """
    if isinstance(s, bytes):
        s_type = bytes
        empty = b""
        _is_d_or_o = _bytes_do_contains
        lparen = b'('
        iterator = _iterate_over_bytes
        default_is_apostrophe = _default_bytes_is_apostrophe
        default_is_double_quote = _default_bytes_is_double_quote
    else:
        s_type = str
        empty = ""
        default_is_apostrophe = _default_str_is_apostrophe
        default_is_double_quote = _default_str_is_double_quote
        _is_d_or_o = _str_do_contains
        lparen = '('
        iterator = iter

    if apostrophes is None:
        _is_apostrophe = default_is_apostrophe
    else:
        cast_apostrophes = []
        for o in iterator(apostrophes):
            if not isinstance(o, s_type):
                raise TypeError(f"apostrophes must be an iterable of non-empty objects the same type as s, or None")
            if not o:
                raise ValueError("apostrophes must be an iterable of non-empty objects the same type as s, or None")
            cast_apostrophes.append(o)
        if not apostrophes:
            raise ValueError("apostrophes must be an iterable of non-empty objects the same type as s")
        _is_apostrophe = frozenset(cast_apostrophes).__contains__

    if double_quotes is None:
        _is_double_quote = default_is_double_quote
    else:
        cast_double_quotes = []
        for o in iterator(double_quotes):
            if not isinstance(o, s_type):
                raise TypeError("double_quotes must be an iterable of non-empty objects the same type as s, or None")
            if not o:
                raise ValueError("double_quotes must be an iterable of non-empty objects the same type as s, or None")
            cast_double_quotes.append(o)
        if not double_quotes:
            raise ValueError("double_quotes must be an iterable of non-empty objects the same type as s")
        _is_double_quote = frozenset(cast_double_quotes).__contains__

    result = []
    state = _after_whitespace
    for c in iterator(s):
        original_c = c
        original_state = state
        is_space = c.isspace() or (c == lparen)
        is_apostrophe = _is_apostrophe(c)
        is_double_quote = _is_double_quote(c)
        if state == _in_word:
            if is_space:
                state = _after_whitespace
        elif state == _after_whitespace:
            if not is_space:
                c = c.upper()
                if (is_apostrophe or is_double_quote):
                    state = _after_whitespace_then_apostrophe_or_double_quote
                elif _is_d_or_o(c):
                    state = _after_whitespace_then_D_or_O
                else:
                    state = _in_word
        elif state == _after_whitespace_then_apostrophe_or_double_quote:
            if not (is_apostrophe or is_double_quote):
                c = c.upper()
                state = _in_word
        elif state == _after_whitespace_then_D_or_O:
            if is_apostrophe:
                state = _after_whitespace_then_D_or_O_then_apostrophe
            else:
                state = _in_word
        elif state == _after_whitespace_then_D_or_O_then_apostrophe:
            c = c.upper()
            state = _in_word
        result.append(c)
    return empty.join(result)

@_export
def normalize_whitespace(s, separators=None, replacement=None):
    """
    Returns s, but with every run of consecutive
    separator characters turned into a replacement string.
    By default turns all runs of consecutive whitespace
    characters into a single space character.

    s may be str or bytes.
    separators should be an iterable of either str or bytes objects,
    matching s.
    replacement should be either a str or bytes object,
    also matching s, or None (the default).
    If replacement is None, normalize_whitespace will use
    a replacement string consisting of a single space character,
    matching the type of s (str or bytes).

    Leading or trailing runs of separator characters will
    be replaced with the replacement string, e.g.:

       normalize_whitespace("   a    b   c") == " a b c".

    You can pass in an instance of a subclass of bytes or str
    for s and elements of separators, but the base class
    for both must be the same (str or bytes).
    normalize_whitespace will only return str or bytes objects.
    """

    if isinstance(s, bytes):
        empty = b''
        default_replacement = b' '
        default_separators = bytes_whitespace_without_crlf
        s_type = bytes
    else:
        empty = ''
        default_replacement = ' '
        default_separators = whitespace_without_crlf
        s_type = str

    if separators is None:
        separators = default_separators
    elif isinstance(separators, s_type):
        if s_type == bytes:
            # not iterable of bytes, literally a bytes string.
            # split it ourselves.  otherwise, _separators_to_re will
            # iterate over it, which... yields integers! oops!
            separators = _iterate_over_bytes(separators)
        separators = tuple(separators)
    else:
        cast_separators = []
        for o in separators:
            if not isinstance(o, s_type):
                raise TypeError("separators must be an iterable of non-empty objects the same type as s, or None")
            if not o:
                raise ValueError("separators must be an iterable of non-empty objects the same type as s, or None")
            cast_separators.append(o)
        if not cast_separators:
            raise ValueError("separators must be an iterable of non-empty objects the same type as s, or None")
        separators = tuple(cast_separators)

    if replacement is None:
        replacement = default_replacement
    elif not isinstance(replacement, s_type):
        raise TypeError("replacement must be the same type as s, or None")

    if not s:
        return empty

    # normalize_whitespace has a fast path for
    # normalizing whitespace on str objects.
    # if your "separators" qualifies,
    # it'll automatically use the fast path.
    #
    # we can't use the fast path for bytes objects,
    # because it won't work with encoded whitespace
    # characters > chr(127).
    #
    # (it'd *usually* work, sure.
    # but "usually" isn't good enough for big!)
    if (   (separators is whitespace_without_crlf)
        or (separators is whitespace)
        ):
        if not s.strip():
            return replacement
        words = s.split()
        if s[:1].isspace():
            words.insert(0, empty)
        if s[-1:].isspace():
            words.append(empty)
        cleaned = replacement.join(words)
        return cleaned

    words = list(multisplit(s, separators, keep=False, separate=False, strip=False, reverse=False, maxsplit=-1))
    cleaned = replacement.join(words)
    del words
    return cleaned



##
## A short treatise on detecting newlines.
##
## What's the fastest way to detect if a string contains newlines?
##
## I experimented with several approaches, including re.compile(newlines-separated-by-|).search
## and brute-force checking with s.find.  These are fast, but there's something even faster.
##
## Before I answer, let me back up a little.  In big, I want to detect if a string contains
## newlines in several places--and in every one of these places, I raise an exception if the
## string contains newlines.  This means that, if the string contains newlines, performance
## is now out the window; we're gonna raise an exception, processing is over, etc etc etc.
## Therefore, the only scenario that's relevant to performance is when the string *doesn't*
## contain newlines.  And what's the fastest way to confirm that a string contains no newlines?
##         contains_newlines = len( s.splitlines() ) > 1
## In the case that s doesn't contain any newlines, this allocates a list, then examines every
## character in s to see if it's a newline.  Once it reaches the end of the list, nope, no newline
## characters detected, so it adds a reference to s to its list and returns the list.  All that
## work is done in C.  The only extraneous bit is the list, but that's not really a big deal.
##
## In the case where s does contain newlines, this is going to allocate N strings, where the sum
## of their lengths is the same as len(s), etc etc.  That's slow.  But we only do that when we're
## gonna throw an exception anyway.
##
## One added benefit of this approach: it works on both str and bytes objects, you don't need to
## handle them separately.
##
## Update: OOOOPS! s.splitlines() implicitly does an s.rstrip(newline-characters) before splitting!
## Hooray for special cases breaking the rules!
##
## So now I have to do this more complicated version:
##         contains_newlines = (len( s.splitlines() ) > 1) or (len( ( s[-1:] + 'x' ').splitlines() ) > 1)
## (Why the colon in [-1:] ?  So it works on bytes strings.  yes, we also have to use b'x' then.)
##

_sqs_quotes_str   = ( '"',  "'")
_sqs_quotes_bytes = (b'"', b"'")

_sqs_escape_str   =  '\\'
_sqs_escape_bytes = b'\\'


def split_quoted_strings(s, separators, all_quotes_set, quotes, multiline_quotes, empty, laden, state):
    """
    This is the generator function implementing the split_quoted_strings
    iterator.  The public split_quoted_strings analyzes its arguments,
    ensuring that they're valid (or raising an exception if they're not).
    If the inputs are valid, it calls this generator and returns the
    resulting iterator.
    """
    buffer = []

    quote = state
    # print(f"    >> {state=}")
    for pair in multisplit(s, separators, keep=AS_PAIRS, separate=True):
        # print(f"    >> {pair}  -- {quote=}")
        literal, separator = pair

        if literal:
            buffer.append(literal)
        if not quote:
            # not currently quoted
            if separator not in all_quotes_set:
                buffer.append(separator)
                continue
            if buffer:
                yield (empty, empty.join(buffer), empty)
                buffer.clear()
            quote = separator
            continue
        # in quote
        if separator != quote:
            buffer.append(separator)
            continue
        # separator == quote
        text = empty.join(buffer)
        if quote or text:
            if quote and text and (quote not in multiline_quotes):
                # see treatise above
                if (len(text.splitlines()) > 1) or (len( (text[-1:] + laden).splitlines()) > 1):
                    raise SyntaxError("unterminated quoted string, {s!r}")
            if state:
                state = None
                # print(f"    <<1 empty, {text=}, {quote=}")
                yield (empty, text, quote)
            else:
                # print(f"    <<2 {quote=}, {text=}, {quote=}")
                yield (quote, text, quote)
        buffer.clear()
        quote = empty

    if buffer:
        text = empty.join(buffer)
        if text or quote:
            if quote and text and (quote not in multiline_quotes):
                # see treatise above
                if (len(text.splitlines()) > 1) or (len( (text[-1:] + laden).splitlines()) > 1):
                    raise SyntaxError("unterminated quoted string, {s!r}")
            if state:
                state = None
                quote = empty
            # print(f"    <<3 {quote=}, {text=}, empty")
            yield (quote, text, empty)

_split_quoted_strings = split_quoted_strings


@_export
def split_quoted_strings(s, quotes=_sqs_quotes_str, *, escape=_sqs_escape_str, multiline_quotes=(), state=''):
    """
    Splits s into quoted and unquoted segments.

    Returns an iterator yielding 3-tuples:

        (leading_quote, segment, trailing_quote)

    where leading_quote and trailing_quote are either
    empty strings or quote delimiters from quotes,
    and segment is a substring of s.  Joining together
    all strings yielded recreates s.

    s can be either str or bytes.

    quotes is an iterable of unique quote delimiters.
    Quote delimiters may be any string of 1 or more characters.
    They must be the same type as s, either str or bytes.
    When one of these quote delimiters is encountered in s,
    it begins a quoted section, which only ends at the
    next occurance of that quote delimiter.  By default,
    quotes is ('"', "'").  (If s is bytes, quotes defaults
    to (b'"', b"'").)  If a newline character appears inside a
    quoted string, split_quoted_strings will raise SyntaxError.

    multiline_quotes is like quotes, except quoted strings
    using multiline quotes are permitted to contain newlines.
    By default split_quoted_strings doesn't define any
    multiline quote marks.

    escape is a string of any length.  If escape is not
    an empty string, the string will "escape" (quote)
    quote delimiters inside a quoted string, like the
    backslash ('\\') character inside strings in Python.
    By default, escape is '\\'.  (If s is bytes, escape
    defaults to b'\\'.)

    multiline_quotes is like quotes, except text inside
    multiline quotes is permitted to contain newlines.
    multiline_quotes and quotes must not both contain the
    same string.  By default there are no multiline quotes
    defined.

    state is a string.  It sets the initial state of
    the function.  The default is an empty string (str
    or bytes, matching s); this means the parser starts
    parsing the string in an unquoted state.  If you
    want parsing to start as if it had already encountered
    a quote delimiter--for example, if you were parsing
    multiple lines individually, and you wanted to begin
    a new line continuing the state from the previous line--
    pass in the appropriate quote delimiter from quotes
    into initial.  When a non-empty string is passed in
    to state, the leading_quote in the first 3-tuple
    yielded by split_quoted_strings will be an empty string.
    For example:

        list(split_quoted_string("a b c'", state="'"))

    evaluates to

        [("", "a b c", "'"),]

    Note:
    * split_quoted_strings is agnostic about the length
      of quoted strings.  If you're using split_quoted_strings
      to parse a C-like language, and you want to enforce
      C's requirement that single-quoted strings only contain
      one character, you'll have to do that yourself.
    * split_quoted_strings doesn't raise an error
      if s ends with an unterminated quoted string.  In
      that case, the last tuple yielded will have a non-empty
      leading_quote and an empty trailing_quote.  (If you
      consider this an error, you'll need to raise SyntaxError
      in your own code.)
    * split_quoted_strings only supports the opening and
      closing marker for a string being the same string.
      If you need the opening and closing markers to be
      different strings, use split_delimiters.
    """

    # print(f"split_quoted_strings({s=}, {quotes=}, *, {escape=}, {multiline_quotes=}, {state=})")

    if multiline_quotes is None:
        multiline_quotes = ()

    is_bytes = isinstance(s, bytes)
    if is_bytes:
        s_type = bytes
        empty = b''
        laden = b'x'
        if quotes in (_sqs_quotes_str, None):
            quotes = _sqs_quotes_bytes
        else:
            if isinstance(quotes, bytes):
                quotes = tuple(_iterate_over_bytes(quotes))
            for q in quotes:
                if not isinstance(q, s_type):
                    raise TypeError(f"values in quotes must match s (str or bytes), not {q!r}")
                if not q:
                    raise ValueError("quotes cannot contain an empty string")
        if escape in (_sqs_escape_str, None):
            escape = _sqs_escape_bytes
        if multiline_quotes:
            if isinstance(multiline_quotes, bytes):
                multiline_quotes = tuple(_iterate_over_bytes(multiline_quotes))
            for q in multiline_quotes:
                if not isinstance(q, s_type):
                    raise TypeError(f"values in multiline_quotes must match s (str or bytes), not {q!r}")
                if not q:
                    raise ValueError("multiline_quotes cannot contain an empty string")
        elif not isinstance(escape, s_type):
            raise TypeError(f"escape must match s (str or bytes), not {escape!r}")
    else:
        s_type = str
        empty = ""
        laden = 'x'
        if quotes in (_sqs_quotes_bytes, None):
            quotes = _sqs_quotes_str
        else:
            for q in quotes:
                if not isinstance(q, s_type):
                    raise TypeError(f"values in quotes must match s (str or bytes), not {q!r}")
                if not q:
                    raise ValueError("quotes cannot contain an empty string")
        if escape in (_sqs_escape_bytes, None):
            escape = _sqs_escape_str
        if multiline_quotes:
            for q in multiline_quotes:
                if not isinstance(q, s_type):
                    raise TypeError(f"values in multiline_quotes must match s (str or bytes), not {q!r}")
                if not q:
                    raise ValueError("multiline_quotes cannot contain an empty string")
        elif not isinstance(escape, s_type):
            raise TypeError(f"escape must match s (str or bytes), not {escape!r}")

    quotes_set = set(quotes)
    multiline_quotes_set = set(multiline_quotes)
    all_quotes_set = quotes_set | multiline_quotes_set

    if not all_quotes_set:
        raise ValueError("either quotes or multiline_quotes must be non-empty")

    if state in (None, '', b''):
        state = empty
    else:
        if not isinstance(state, s_type):
            raise TypeError("state must match s (str or bytes), not {state!r}")
        if state not in all_quotes_set:
            raise ValueError(f"state must be be one of the delimiters listed in the quotes or multiline_quotes arguments, not {state!r}")

    if len(quotes_set) != len(quotes):
        repeated = set()
        seen = set()
        for q in quotes:
            if q in seen:
                repeated.add(q)
            seen.add(q)
        repeated = list(repeated)
        repeated.sort()
        raise ValueError("quotes contains repeated quote markers: " + ", ".join(repr(q) for q in repeated))

    if len(multiline_quotes_set) != len(multiline_quotes):
        repeated = set()
        seen = set()
        for q in multiline_quotes:
            if q in seen:
                repeated.add(q)
            seen.add(q)
        repeated = list(repeated)
        repeated.sort()
        raise ValueError("multiline_quotes contains repeated quote markers: " + ", ".join(repr(q) for q in repeated))

    in_both_quotes_sets = quotes_set & multiline_quotes_set
    if in_both_quotes_sets:
        in_both_quotes_sets = list(in_both_quotes_sets)
        if len(in_both_quotes_sets) == 1:
            s = repr(list(in_both_quotes_sets)[0])
        else:
            in_both_quotes_sets.sort()
            s = ', '.join(repr(_) for _ in in_both_quotes_sets)
        raise ValueError(f"{s} appears in both quotes and multiline_quotes")

    # separators is a list containing all quote marks,
    separators = list(quotes_set)
    separators.extend(multiline_quotes_set)

    # and also all escaped quote marks.
    if escape:
        for first_character in {q[0:] for q in quotes}:
            separators.append(escape + first_character)
        separators.append(escape + escape)

    # help multisplit work better--it memoizes the conversion to a regular expression
    separators.sort()

    return _split_quoted_strings(s, separators, all_quotes_set, quotes_set, multiline_quotes_set, empty, laden, state)


@_export
class Delimiter:
    """
    Class representing a delimiter for split_delimiters.

    close is the closing delimiter character, must be the same type as open, and length 1.
    quoting is a boolean: does this set of delimiters "quote" the text inside?
        When an open delimiter enables quoting, split_delimiters will ignore all
        other delimiters in the text until it encounters the matching close delimiter.
        (Single- and double-quotes set this to True.)
    escape is a string of maximum length 1: if true, when inside this pair of delimiters,
        you can escape the closing delimiter using this string.  When quoting is true,
        escape may not be empty, and when quoting is false escape must be empty.
    multiline is a boolean: are newline characters permitted inside these delimiters?
        multiline may only be false when quoting is true.

    You may not specify backslash ('\\') as an open or close delimiter.
    """
    def __init__(self, close, *, escape='', multiline=True, quoting=False):
        # you can pass in a Delimiter instance and we'll clone it
        if isinstance(close, Delimiter):
            d = close
            self._close = d._close
            self._escape = d._escape
            self._quoting = d._quoting
            self._multiline = d._multiline
            return

        is_bytes = isinstance(close, bytes)
        if is_bytes:
            t = bytes
            empty = b''
            if close == b'\\':
                raise ValueError("close delimiter must not be '\\'")
        else:
            t = str
            empty = ''
            if close == '\\':
                raise ValueError("close delimiter must not be b'\\'")

        # they can't both be false, and they can't both be true
        if bool(escape) != bool(quoting):
            raise ValueError("quoting and escape mismatch; they must either both be true, or both be false")

        # if quoting=False, you can only have multiline=True
        if not (quoting or multiline):
            raise ValueError(f"multiline=False unsupported when quoting=False")

        self._close = close
        self._escape = escape or empty
        self._quoting = quoting
        self._multiline = multiline

    @property
    def close(self):
        return self._close

    @property
    def escape(self):
        return self._escape

    @property
    def quoting(self):
        return self._quoting

    @property
    def multiline(self):
        return self._multiline

    def __repr__(self): # pragma: no cover
        return f"Delimiter(close={self._close!r}, escape={self._escape!r}, multiline={self._multiline!r}, quoting={self._quoting!r})"

    def __eq__(self, other):
        return (isinstance(other, Delimiter)
            and (self._close   == other._close)
            and (self._escape  == other._escape)
            and (self._quoting == other._quoting)
            and (self._multiline == other._multiline)
            )

    def __hash__(self):
        return hash(self._close) ^ hash(self._escape) ^ hash(self._quoting) ^ hash(self._multiline)

    def copy(self):
        return Delimiter(self)


delimiter_parentheses = Delimiter(")")
_export_name('delimiter_parentheses')

delimiter_square_brackets = Delimiter("]")
_export_name('delimiter_square_brackets')

delimiter_curly_braces = Delimiter("}")
_export_name('delimiter_curly_braces')

delimiter_angle_brackets = Delimiter(">")
_export_name('delimiter_angle_brackets')

delimiter_single_quote = Delimiter("'", escape='\\', multiline=False, quoting=True)
_export_name('delimiter_single_quote')

delimiter_double_quotes = Delimiter('"', escape='\\', multiline=False, quoting=True)
_export_name('delimiter_double_quotes')

split_delimiters_default_delimiters = {
    '(': delimiter_parentheses,
    '[': delimiter_square_brackets,
    '{': delimiter_curly_braces,
    "'": delimiter_single_quote,
    '"': delimiter_double_quotes,
    }
_export_name('split_delimiters_default_delimiters')


split_delimiters_default_delimiters_bytes = {
    b'(': Delimiter(b')'),
    b'[': Delimiter(b']'),
    b'{': Delimiter(b'}'),
    b"'": Delimiter(b"'", escape=b'\\', multiline=False, quoting=True),
    b'"': Delimiter(b'"', escape=b'\\', multiline=False, quoting=True),
    }
_export_name('split_delimiters_default_delimiters_bytes')


_ACTION_POP = "<action: pop>"
_ACTION_ESCAPE = "<action: escape>"
_ACTION_ILLEGAL = "<action: illegal>"
_ACTION_ILLEGAL_NEWLINE = "<action: illegal newline>"
_ACTION_FLUSH = "<action: flush>"
_ACTION_FLUSH_1_AND_RESPLIT = "<action: flush 1 and resplit>"

class _ACTION_TRUNCATE_TO_S_AND_RESPLIT:
    pass

class _ACTION_TRUNCATE_TO_S_AND_RESPLIT_STR(str, _ACTION_TRUNCATE_TO_S_AND_RESPLIT):
    def __repr__(self): # pragma: nocover
        return f"_ACTION_TRUNCATE_TO_S_AND_RESPLIT({str(self)!r})"

class _ACTION_TRUNCATE_TO_S_AND_RESPLIT_BYTES(bytes, _ACTION_TRUNCATE_TO_S_AND_RESPLIT):
    def __repr__(self): # pragma: nocover
        return f"_ACTION_TRUNCATE_TO_S_AND_RESPLIT({bytes(self)!r})"

@functools.lru_cache(maxsize=None)
def _delimiters_to_state_and_tokens(delimiters, is_bytes):
    """
    Converts delimiters into data used by the split_delimiters
    generator function: a graph of interconnected dicts, and a
    set containing all tokens (suitable for use as a "separators"
    list for multisplit).  Returns a 2-tuple:

        (initial_state, all_tokens)

    where initial_state is the dict for the initial state and
    all_tokens is an iterable of all the token strings needed
    to parse, including open delimimeters, close delimiters,
    and escape strings.

    Because this function is memoized (using functools.lru_cache)
    you must convert delimiters from a dict into a tuple of
    2-tuples.  (dicts aren't hashable.)  Instead of passing
    in "delimiters", pass in:

         tuple(delimiters.items())

    The state is consumed by the split_delimiters generator, below.
    See that for details.
    """
    if is_bytes:
        s_type = bytes
        s_type_description = "bytes"
        not_s_type_description = "str"
        newlines = bytes_linebreaks_without_crlf
        truncate_to_s_type = _ACTION_TRUNCATE_TO_S_AND_RESPLIT_BYTES
        iterate_over_delimiter = _iterate_over_bytes
    else:
        s_type = str
        s_type_description = "str"
        not_s_type_description = "bytes"
        newlines = str_linebreaks_without_crlf
        truncate_to_s_type = _ACTION_TRUNCATE_TO_S_AND_RESPLIT_STR
        iterate_over_delimiter = iter

    all_closers = set()
    all_openers = set()
    all_escapes = set()
    nested_closers = set()
    all_newlines = set()

    for k, v in delimiters:
        if not isinstance(k, s_type):
            raise TypeError(f"open delimiter {k!r} must be {s_type_description}, not {not_s_type_description}")
        if not isinstance(v, Delimiter):
            raise TypeError(f"delimiter values must be Delimiter, not {v!r}")
        if not isinstance(v.close, s_type):
            raise TypeError(f"close delimiter {v.close!r} must be {s_type_description}, not {not_s_type_description}")
        all_openers.add(k)
        all_closers.add(v.close)
        if not isinstance(v.escape, s_type):
            raise TypeError(f"Delimiter: escape {v.escape!r} must be {s_type_description}, not {not_s_type_description}")
        if v.quoting:
            assert v.escape
            all_escapes.add(v.escape)
        else:
            assert not v.escape
            nested_closers.add(v.close)

        # if any delimiter disallows newlines, add all newlines to the set of tokens
        if not (v.multiline or all_newlines):
            all_newlines = set(newlines)


    in_both_openers_and_closers = all_openers & nested_closers
    if in_both_openers_and_closers:
        in_both_openers_and_closers = list(in_both_openers_and_closers)
        if len(in_both_openers_and_closers) == 1:
            in_both_openers_and_closers = in_both_openers_and_closers[0]
            prefix = ''
        else:
            prefix = 'these characters '
        raise ValueError(f"{prefix}{in_both_openers_and_closers!r} cannot be both an opening and closing delimiter")

    all_delimiter_tokens = all_openers | all_closers | all_escapes
    all_tokens = all_delimiter_tokens | all_newlines

    # all the non-quoting states reuse the same open dictionary.
    # initial_state = _DelimiterState(open={}, close=None, illegal=all_closers, single_line_only=False)

    push_delimiters = {}

    non_quoting_default_actions = {token: _ACTION_ILLEGAL for token in all_delimiter_tokens }

    if all_newlines:
        newlines_are_illegal = {c: _ACTION_ILLEGAL_NEWLINE for c in newlines}

    # list of states that want all the default openers after processing
    states_that_want_push_delimiters = []

    # the initial state contains all the open delimiters,
    # isn't quoting, allows multiline, and doesn't have
    # a close delimiter or an escape string.
    initial_state = non_quoting_default_actions.copy()
    states_that_want_push_delimiters.append(initial_state)

    # for every state, representing a delimiter d:
    #
    # non-quoting delimiter pairs have illegal strings, invalid delimiters.
    # e.g. imagine d.open = '(', d.close =')', and d.quoting = False
    # and another state has delimiters '[(' and ')]'
    # if we parse
    #         x[foo( a b c )])
    # multisplit will      ^^ split here
    # but we want to split ^ here. so.
    # for every illegal token t
    #    for s in (d.close, d.escape) # if d.escape is defined, that is
    #        if len(t) > len(s) and t.startswith(s)
    #            action = _ACTION_FLUSH_{CLOSE, ESCAPE}_AND_RESPLIT
    #            # this behaves like we got delimiter s instead of t from multisplit
    #            # we re-multisplit after the end of s
    #
    # if d.quoting:
    #    first of all, we still have the same problem as with the previous
    #    paragraph, except quoting delimiters would flush them, they aren't illegal.
    #    but we still need to split
    #
    #    but also!
    #    proper markers might be completely *buried inside* otherwise flushed delimiters.
    #
    #        e.g. imagine d.open = d.close ='"', and d.quoting = True
    #        and another state has delimiters '<"<' '>">'
    #        if we parse
    #              a b c " d e f <"<"< goo goo >">
    #        multisplit will     ^^^ split here
    #        but we should flush ^ this
    #                        and  ^ handle this.
    #
    #    also, the *start* of a proper marker might be consumed by an otherwise flushed delimiter.
    #
    #        e.g. imagine d.open = '<(' d.close =')>', and d.quoting = True
    #        and another state has delimiters '([' '])'
    #        if we parse
    #              a b c <( d e f ])>
    #        multisplit will      ^^^ split here
    #        but we want to flush ^ this
    #                         and  ^^ handle this.
    #
    #   what we do in these cases is snip off the first character, flush it,
    #   then re-split (using multisplit) starting after that first character.
    #
    #   note that if the same multi-character delimiter *starts with* one delimiter,
    #   but also contains any overlap with another delimiter, the startswith has
    #   to take priority.
    #
    #       e.g. imagine d.open = '(', d.close=')', d.escape = '[', d.quoting=True
    #       and another state has delimiters '([' '])'
    #       for state d, we want '])' to map to "TRUNCATE TO ]", not "FLUSH 1 AND RESPLIT"
    #

    for open, delimiter in delimiters:
        if delimiter.quoting:
            state = {}
            all_delimiter_characters = set(iterate_over_delimiter(delimiter.close))
            if delimiter.escape:
                all_delimiter_characters |= set(iterate_over_delimiter(delimiter.escape))

        else:
            # non-quoting delimiter
            state = non_quoting_default_actions.copy()
            states_that_want_push_delimiters.append(state)
            all_delimiter_characters = None

        delimiters_and_startswith_actions = [ (delimiter.close, truncate_to_s_type(delimiter.close)) ]
        if delimiter.escape:
            delimiters_and_startswith_actions.append((delimiter.escape, truncate_to_s_type(delimiter.escape)))

        for t in all_tokens:
            for s, startswith_action in delimiters_and_startswith_actions:
                if t != s:
                    if t.startswith(s):
                        state[t] = startswith_action
                        break # breaking here ensures priority of startswith
                    elif all_delimiter_characters:
                        t_characters = set(iterate_over_delimiter(t))
                        if t_characters & all_delimiter_characters:
                            state[t] = _ACTION_FLUSH_1_AND_RESPLIT

        if delimiter.quoting and (not delimiter.multiline):
            state.update(newlines_are_illegal)

        state[delimiter.close] = _ACTION_POP

        if delimiter.escape:
            state[delimiter.escape] = _ACTION_ESCAPE

        assert open not in push_delimiters
        push_delimiters[open] = state

    for state in states_that_want_push_delimiters:
        state.update(push_delimiters)

    return initial_state, all_tokens


def split_delimiters(text, all_tokens, current, stack, empty, laden, str_or_bytes):
    """
    Internal generator function returned by the real split_delimiters.

    This function operates by iterating over "text" and reacting to
    tokens found in "all_tokens".  It splits text using multisplit(),
    using all_tokens as the separator list, and specifying keep=AS_PAIRS
    so we can examine the string we split on.  We'll refer to that
    separator string as the "token" below.

    "current" is a dict mapping tokens to actions.
        * a dictionary, which indicates "push this dict"
          (entering new delimiter),
        * one of the _ACTION_* constants above, or
        * an instance of _ACTION_TRUNCATE_TO_S_AND_RESPLIT.

    The _ACTION_* constants above dictate:
        * _ACTION_POP means pop the current state.
        * _ACTION_ESCAPE means escape the next character yielded
          by multisplit.
        * _ACTION_ILLEGAL_NEWLINE means the token is an illegal
          newline character.  (The current delimiter doesn't permit
          embedded newlines.)
        * _ACTION_ILLEGAL means the token isn't legal here.
          example: 'foo(abc ] )', the ] is illegal
        * _ACTION_FLUSH means we are ignoring this token completely,
          just flush it out as part of the non-separator text.
        * _ACTION_FLUSH_1_AND_RESPLIT means this token isn't itself
          one of our current separators, but it contains relevant
          separator characters.  It might have consumed part or all
          of an actual token we want to parse.  The easy way to
          handle this: chop off the first character, flush that out
          as part of the non-separator text, then "resplit": rerun
          multisplit() starting at the second character of this
          separator and proceed from there.  (_ACTION_FLUSH_1_AND_RESPLIT
          is only used for delimiters with quoting=True.)

    If the entry an instance is an instance of _ACTION_TRUNCATE_TO_S_AND_RESPLIT,
    then this token starts with one of our current delimiters (close or escape).
    The _ACTION_TRUNCATE_TO_S_AND_RESPLIT class is a subclass of either str or
    bytes, and str(action) or bytes(action) (as appropriate) will convert it back
    into the relevant delimiter token.  We react as if we received *that* token
    instead, then "resplit" starting after the delimiter.

    Newlines are also handled using this mechanism.  If the current state
    is allergic to newline characters, all newline characters will be mapped
    to _ACTION_ILLEGAL_NEWLINE.  If the current state doesn't care about
    newline characters, newline characters will be unmapped, which means
    they get the default action _ACTION_FLUSH.
    (And, if literally no delimiters have multiline=False in this run,
    we won't even add the newlines to the list of all tokens!  You don't
    pay for what you don't use.)

    Why do we have all this _ACTION_*_AND_RESPLIT nonsense?  The
    straightforward way to implement this would be to "resplit"
    (re-run multisplit) every time we pushed or popped, changing
    the separators to just the ones recognized by that state.  But
    running multisplit has a lot of overhead.  It's cheaper to
    let multisplit recognize *all* tokens and just cook along
    yielding everything.  In practice this implementation rarely
    actually resplits; it's only needed for correctness, to handle
    ambiguous circumstances with overlapping delimiters.  Which
    people don't actually do in the real world.  (Do they?)

    (I admit, I haven't tried the straightforward implementation.
    But I'm pretty convinced multisplit overhead would quickly eat
    up any performance benefits from the more straightforward
    implementation and from using a simpler regex with re.split
    under the covers.  And, as mentioned, in practice we never
    resplit anyway.)
    """

    push = stack.append
    pop = stack.pop

    open = None

    buffer = []
    append = buffer.append
    clear = buffer.clear

    join = empty.join

    escaped = empty

    consumed = 0

    i = multisplit(text, all_tokens, keep=AS_PAIRS, separate=True)
    resplit = False

    while True:
        for s, delimiter in i:
            if not (s or delimiter):
                continue
            if escaped:
                # either s or delimiter is true
                escaped = empty
                if not s:
                    # must be delimiter.
                    # always flush exactly 1 character of it.
                    consumed += 1

                    if len(delimiter) == 1:
                        append(delimiter)
                        continue

                    # if delimiter is longer than 1 character, resplit.
                    append(delimiter[0:1])
                    i = multisplit(text[consumed:], all_tokens, keep=AS_PAIRS, separate=True)
                    break

            append(s)
            consumed += len(s)

            if not delimiter:
                # we're done!
                # on the next iteration, i will be exhausted,
                # we'll hit the else clause on the for-else loop,
                # and we'll exit the outer loop too.
                break

            action = current.get(delimiter, _ACTION_FLUSH)

            if isinstance(action, dict):
                # action is a new state, push it.
                # flush open delimiter
                s = join(buffer)
                clear()
                yield s, delimiter, empty
                consumed += len(delimiter)
                # and push
                push((current, open))
                open = delimiter
                current = action
                continue

            if isinstance(action, _ACTION_TRUNCATE_TO_S_AND_RESPLIT):
                # convert the action back into the startswith delimiter we want,
                delimiter = str_or_bytes(action)
                # look up the actual action we should use to handle that delimiter,
                action = current.get(delimiter, _ACTION_FLUSH)
                # assert action is not _ACTION_FLUSH, f"{action!r} is not {_ACTION_FLUSH}, delimiter={delimiter}"
                # activate resplit,
                resplit = True
                # and fall through to the appropriate _ACTION handler.

            if action is _ACTION_POP:
                # flush close delimiter
                s = join(buffer)
                clear()
                yield s, empty, delimiter
                consumed += len(delimiter)
                # and pop
                current, open = pop()
            elif action is _ACTION_ESCAPE:
                # escape
                append(delimiter)
                escaped = delimiter
                consumed += len(delimiter)
            elif action is _ACTION_FLUSH:
                append(delimiter)
            elif action is _ACTION_FLUSH_1_AND_RESPLIT:
                # flush first character of delimiter, and resplit.
                append(delimiter[0:1])
                consumed += 1
                resplit = True
            elif action is _ACTION_ILLEGAL:
                # illegal character
                raise SyntaxError(f"index {consumed}: illegal string {delimiter!r}")
            elif action is _ACTION_ILLEGAL_NEWLINE:
                # illegal newline character
                raise SyntaxError(f"index {consumed}: newline character {delimiter!r} is illegal inside delimiter {open!r}")
            else: # pragma: nocover
                # unhandled
                raise RuntimeError(f"index {consumed}: unhandled action {action!r}")

            if resplit:
                i = multisplit(text[consumed:], all_tokens, keep=AS_PAIRS, separate=True)
                resplit = False
                break
        else:
            break

    if buffer:
        if escaped:
            raise SyntaxError(f"text ends with escape string {escaped!r}")
        s = join(buffer)
        if s:
            yield s, empty, empty


_split_delimiters = split_delimiters

_split_delimiters_default_delimiters_cache = _delimiters_to_state_and_tokens(tuple(split_delimiters_default_delimiters.items()), False)
_split_delimiters_default_delimiters_bytes_cache = _delimiters_to_state_and_tokens(tuple(split_delimiters_default_delimiters_bytes.items()), True)


@_export
def split_delimiters(s, delimiters=split_delimiters_default_delimiters, *, state=()):
    """
    Splits a string s at delimiter substrings.

    s may be str or bytes.

    delimiters may be either None or a mapping of open delimiter
    strings to Delimiter objects.  The open delimiter strings,
    close delimiter strings, and escape strings must match the type
    of s (either str or bytes).

    If delimiters is None, split_delimiters uses a default
    value matching these pairs of delimiters:

        () [] {} "" ''

    The first three delimiters allow multiline, disable
    quoting, and have no escape string.  The quote mark
    delimiters enable quoting, disallow multiline, and
    specify their escape string as a single backslash.
    (This default value automatically supports both str
    and bytes.)

    state specifies the initial state of parsing. It's an iterable
    of open delimiter strings specifying the initial nested state of
    the parser, with the innermost nesting level on the right.
    If you wanted `split_delimiters` to behave as if it'd already seen
    a '(' and a '[', in that order, pass in ['(', '['] to state.

    (Tip: Use a list as a stack to track the state of split_delimiters.
    Push open delimiters with .append, and pop them with .pop
    when you encounter the matching close delimiter.)

    Yields 3-tuples containing strings:

        (text, open, close)

    where text is the text before the next opening or closing delimiter,
    open is the trailing opening delimiter,
    and close is the trailing closing delimiter.
    At least one of these three strings will always be non-empty.
    (If open is non-empty, close will be empty, and vice-versa.)
    If s doesn't end with an opening or closing delimiter, the final tuple
    yielded will have empty strings for both open and close.

    You may not specify backslash ('\\\\') as an open delimiter.

    Multiple Delimiters may use the same close delimiter string.

    split_delimiters doesn't complain if the string ends with
    unterminated delimiters.

    See the Delimiter object for how delimiters are defined, and how
    you can define your own delimiters.
    """
    initial_state = all_tokens = None

    if delimiters in (split_delimiters_default_delimiters, split_delimiters_default_delimiters_bytes):
        delimiters = None

    is_bytes = isinstance(s, bytes)
    if is_bytes:
        str_or_bytes = bytes
        empty = b''
        laden = b'x'
        if delimiters is None:
            initial_state, all_tokens = _split_delimiters_default_delimiters_bytes_cache
        elif not delimiters:
            raise ValueError("invalid delimiters")
        elif b'\\' in delimiters:
            raise ValueError("open delimiter must not be b'\\'")
    else:
        str_or_bytes = str
        empty = ''
        laden = 'x'
        if delimiters is None:
            initial_state, all_tokens = _split_delimiters_default_delimiters_cache
        elif not delimiters:
            raise ValueError("invalid delimiters")
        elif '\\' in delimiters:
            raise ValueError("open delimiter must not be '\\'")

    if not initial_state:
        initial_state, all_tokens = _delimiters_to_state_and_tokens(tuple(delimiters.items()), is_bytes)

    stack = []
    push = stack.append

    current = initial_state
    open = None

    if state:
        for i, delimiter in enumerate(_iterate_over_bytes(state)):
            action = current.get(delimiter, _ACTION_FLUSH)
            if isinstance(action, dict):
                push((current, open))
                current = action
                continue

            raise ValueError(f"delimiter #{i} specified in state is invalid: {delimiter!r}")

    return _split_delimiters(s, all_tokens, current, stack, empty, laden, str_or_bytes)






@_export
class LineInfo:
    """
    The first object in the 2-tuple yielded by a
    lines iterator, containing metadata about the line.
    Every parameter to the constructor is stored as an
    attribute of the new LineInfo object using the
    same identifier.

    line is the original unmodified line, split
    from the original s input to lines.  Note
    that line includes the trailing newline character,
    if any.

    line_number is the line number of this line.
    `
    column_number is the starting column of the
    accompanying line string (the second entry
    in the 2-tuple yielded by lines).

    leading and trailing are strings that have
    been stripped from the beginning or end of the
    original line, if any.  (Not counting the
    line-terminating linebreak character.)

    end is the linebreak character that terminated
    the current line, if any.

    indent is the indent level of the current line,
    represented as an integer.  See lines_strip_indent.
    If the indent level hasn't been measured yet this
    should be 0.

    match is the re.Match object that matched this
    line, if any.  See lines_grep.

    You can add your own fields by passing them in
    via `**kwargs`; you can also add new attributes
    or modify existing attributes as needed from
    inside a "lines modifier" function.
    """
    def __init__(self, lines, line, line_number, column_number, *, leading=None, trailing=None, end=None, indent=0, match=None, **kwargs):
        is_str = isinstance(line, str)
        is_bytes = isinstance(line, bytes)
        if is_bytes:
            empty = b''
        elif is_str:
            empty = ''
        else:
            raise TypeError(f"line must be str or bytes, not {line!r}")

        if not isinstance(line_number, int):
            raise TypeError(f"line_number must be int, not {line_number!r}")
        if not isinstance(column_number, int):
            raise TypeError(f"column_number must be int, not {column_number!r}")

        line_type = type(line)

        if not isinstance(indent, int):
            raise TypeError("indent must be int")

        if leading == None:
            leading = empty
        elif not isinstance(leading, line_type):
            raise TypeError(f"leading must be same type as line or None, not {leading!r}")

        if trailing == None:
            trailing = empty
        elif not isinstance(trailing, line_type):
            raise TypeError(f"trailing must be same type as line or None, not {trailing!r}")

        if end == None:
            end = empty
        elif not isinstance(end, line_type):
            raise TypeError(f"end must be same type as line or None, not {end!r}")

        if not ((match == None) or isinstance_re_pattern(match)):
            raise TypeError("match must be None or re.Pattern")

        self.lines = lines
        self.line = line
        self.line_number = line_number
        self.column_number = column_number
        self.leading = leading
        self.trailing = trailing
        self.end = end
        self.indent = indent
        self.match = match
        self._is_bytes = is_bytes
        self.__dict__.update(kwargs)

    def detab(self, s):
        return self.lines.detab(s)

    def clip_leading(self, line, s):
        """
        Clip the leading substring s from line.

        s may be either a string (str or bytes) or an int.
        If s is a string, it must match the leading substring
        of line you wish clipped.  If s is an int, it should
        representing the number of characters you want clipped
        from the beginning of s.

        Returns line with s clipped; also appends
        the clipped portion to self.leading, and updates
        self.column_number to represent the column number
        where line now starts.  (If the clipped portion of
        line contains tabs, it's detabbed using lines.tab_width
        and the detab method on the clipped substring before it
        is measured.)
        """
        if isinstance(s, int):
            assert -len(line) <= s < len(line), f"clip_leading s={s!r} index is larger than the length of line={line!r}"
            s = line[:s]
        else:
            assert line.startswith(s), f"line {line!r} doesn't start with s {s!r}"
            pass
        self.leading += s
        line = line[len(s):]
        detabbed = self.detab(s)
        length = len(detabbed)
        self.column_number += length
        return line

    def clip_trailing(self, line, s):
        """
        Clip the trailing substring s from line.

        s may be either a string (str or bytes) or an int.
        If s is a string, it must match the trailing substring
        of line you wish clipped.  If s is an int, it should
        representing the number of characters you want clipped
        from the end of s.

        Returns line with s clipped; also prepends
        the clipped portion to self.trailing.
        """
        if isinstance(s, int):
            assert -len(line) <= s < len(line), f"clip_trailing s={s!r} index is larger than the length of line={line!r}"
            s = line[-s:]
        else:
            assert line.endswith(s), f"line {line!r} doesn't end with s {s!r}"
            pass
        self.trailing = s + self.trailing
        line = line[:-len(s)]
        return line

    def __repr__(self):
        names = list(self.__dict__)
        priority_names = ['lines', 'line', 'line_number', 'column_number', 'leading', 'trailing', 'end']
        fields = []
        for name in priority_names:
            names.remove(name)
        names.sort()
        names = priority_names + names
        for name in names:
            value = getattr(self, name)
            if value:
                fields.append(f"{name}={value!r}")
        text = ", ".join(fields)
        return f"LineInfo({text})"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and (other.__dict__ == self.__dict__)


@_export
class lines:
    def __init__(self, s, separators=None, *, line_number=1, column_number=1, tab_width=8, **kwargs):
        """
        A "lines iterator" object.  Splits s into lines, and iterates yielding those lines.

        When iterated over, yields 2-tuples:
            (info, line)
        where info is a LineInfo object, and line is a str or bytes object.

        s can be str, bytes, or an iterable.

        If s is neither str nor bytes, s must be an iterable.
        The iterable should either yield individual strings, which is the
        line, or it should yield a tuple containing two strings, in which case
        the strings should be the line and the line-terminating newline respectively.
        All "string" objects yielded by this iterable should be homogeneous,
        either str or bytes.

        `separators` should either be `None` or an iterable of separator strings,
        as per the `separators` argument to `multisplit`.  If `s` is `str` or `bytes`,
        it will be split using `multisplit`, using these separators.  If
        `separators` is `None`--which is the default value--and `s` is `str` or `bytes`,
        `s` will be split at linebreak characters.  (If `s` is neither `str` nor `bytes`,
        `separators` must be `None`.)

        separators is either None or an iterable of separator strings,
        as per the separators argument to multisplit.  If s is str or bytes,
        it will be split using multisplit, using these separators.  If
        separators is None--which is the default value--and s is str or bytes,
        s will be split at linebreak characters.

        line_number is the starting line number given to the first LineInfo
        object.  This number is then incremented for every subsequent line.

        column_number is the starting column number given to every LineInfo
        object.  This number represents the leftmost column of every line.

        tab_width isn't used by lines itself, but is stored internally and
        may be used by other lines modifier functions (e.g. lines_strip_indent,
        lines_convert_tabs_to_spaces). Similarly, all keyword arguments passed
        in via kwargs are stored internally and can be accessed by user-defined
        lines modifier functions.

        You can pass in an instance of a subclass of bytes or str
        for s and elements of separators, but the base class
        for both must be the same (str or bytes).  lines will
        only yield str or bytes objects for line.

        Composable with all the lines_ modifier functions in the big.text module.
        """
        if not isinstance(line_number, int):
            raise TypeError("line_number must be int")
        if not isinstance(column_number, int):
            raise TypeError("column_number must be int")
        if not isinstance(tab_width, int):
            raise TypeError("tab_width must be int")

        self.s = s
        self.separators = separators
        self.line_number = line_number
        self.column_number = column_number
        self.tab_width = tab_width

        is_bytes = isinstance(s, bytes)
        is_str = isinstance(s, str)
        if is_bytes or is_str:
            if not separators:
                separators = linebreaks if is_str else bytes_linebreaks
            self.i = multisplit(s, separators, keep=AS_PAIRS, separate=True, strip=False)
            self.is_pairs = True
            self.s_is_bytes = is_bytes
        else:
            if separators is not None:
                raise ValueError("separators must be None when s is not str or bytes")
            self.i = iter(s)
            is_bytes = None
            self.is_pairs = None # sentinel initial value
            self.s_is_bytes = None # sentinel initial value

        self.__dict__.update(kwargs)

    def __iter__(self):
        return self

    def detab(self, s):
        return s.expandtabs(self.tab_width)

    def __next__(self):
        value = next(self.i)

        # self.is_pairs is slightly wacky:
        #
        # If self.is_pairs is true, our iterator yields iterables of 2 objects,
        #     line and end.
        # If self.is_pairs is a false value besides None, it contains the
        #     appropriate empty string ('' or b'') that should be used for
        #     LineInfo.end when iteration is done.
        # If self.is_pairs is None, it's our first time iterating, we need
        #     to analyze the value we got back from the iterator and determine
        #     what we're working with.

        is_pairs = self.is_pairs
        if is_pairs:
            line, end = value
        else:
            if is_pairs is not None:
                line = value
                end = is_pairs
            else:
                # first time: analyze value, set self.is_pairs etc.
                is_pairs = self.is_pairs = isinstance(value, (tuple, list))
                if is_pairs:
                    if not len(value) == 2:
                        raise ValueError("s passed into lines must be either str, bytes, an iterable of str or bytes, or an iterable of pairs of str or bytes")
                    line, end = value
                else:
                    line = value

                if self.s_is_bytes is None:
                    self.s_is_bytes = isinstance(line, bytes)

                if not is_pairs:
                    self.is_pairs = end = b'' if self.s_is_bytes else ''

        if self.is_pairs and end:
            original_line = line + end
        else:
            original_line = line
        return_value = (LineInfo(self, original_line, self.line_number, self.column_number, end=end), line)
        self.line_number += 1
        return return_value

@_export
def lines_rstrip(li, separators=None):
    """
    A lines modifier function.  Strips trailing whitespace from the
    lines of a "lines iterator".

    separators is an iterable of separators, like the argument
    to multistrip.  The default value is None, which means
    lines_rstrip strips all trailing whitespace characters.

    All characters removed are clipped to info.trailing
    as appropriate.  If the line is non-empty before stripping, and
    empty after stripping, the entire line is clipped to info.trailing.

    Composable with all the lines_ modifier functions in the big.text module.
    """
    if separators is None:
        for info, line in li:
            rstripped = line.rstrip()
            if rstripped != line:
                line = info.clip_trailing(line, -len(rstripped))
            yield (info, line)
        return

    for info, line in li:
        rstripped = multistrip(line, separators, left=False, right=True)
        if rstripped != line:
            line = info.clip_trailing(line, -len(rstripped))
        yield (info, rstripped)


@_export
def lines_strip(li, separators=None):
    """
    A lines modifier function.  Strips leading and trailing strings
    from the lines of a "lines iterator".

    separators is an iterable of separators, like the argument
    to multistrip.  The default value is None, which means
    lines_strip strips all leading and trailing whitespace characters.

    All characters are clipped to info.leading and info.trailing
    as appropriate.  If the line is non-empty before stripping, and
    empty after stripping, the entire line is clipped to info.trailing.

    Composable with all the lines_ modifier functions in the big.text module.
    """
    if separators is not None:

        for info, line in li:
            leading = trailing = None
            if line:
                stripped = multistrip(line, separators)
                if stripped:
                    leading, _, trailing = line.partition(stripped)
                else:
                    trailing = line

                if leading:
                    line = info.clip_leading(line, leading)

                if trailing:
                    line = info.clip_trailing(line, trailing)

            yield (info, line)

        return

    # separators is None, strip whitespace
    for info, line in li:

        leading = trailing = None

        # if not line, line is empty, we don't change anything.
        if line:
            lstripped = line.lstrip()
            if not lstripped:
                # line was all whitespace.
                trailing = line
            else:
                if len(line) != len(lstripped):
                    # we stripped leading whitespace, preserve it
                    leading = line[:len(line) - len(lstripped)]

                rstripped = lstripped.rstrip()
                if len(lstripped) != len(rstripped):
                    trailing = lstripped[len(rstripped):]

            if leading:
                line = info.clip_leading(line, leading)

            if trailing:
                line = info.clip_trailing(line, trailing)

        yield (info, line)


def lines_filter_line_comment_lines(li, match):
    "The generator function returned by the public lines_filter_line_comment_lines function."
    for info, line in li:
        if match(line):
            continue
        yield (info, line)

_lines_filter_line_comment_lines = lines_filter_line_comment_lines

@_export
def lines_filter_line_comment_lines(li, comment_markers):
    """
    A lines modifier function.  Filters out comment lines from the
    lines of a "lines iterator".  Comment lines are lines whose first
    non-whitespace characters appear in the iterable of
    comment_markers strings passed in.

    What's the difference between lines_strip_line_comments and
    lines_filter_line_comment_lines?
      * lines_filter_line_comment_lines only recognizes lines that
        *start* with a comment separator (ignoring leading
        whitespace).  Also, it filters out those lines
        completely, rather than modifying the line.
      * lines_strip_line_comments handles comment characters
        anywhere in the line, although it can ignore
        comments inside quoted strings.  It truncates the
        line but still always yields the line.

    Composable with all the lines_ modifier functions in the big.text module.
    """
    if not comment_markers:
        raise ValueError("illegal comment_markers")

    comment_markers_is_bytes = isinstance(comment_markers, bytes) or isinstance(comment_markers[0], bytes)
    if comment_markers_is_bytes:
        comment_markers = _iterate_over_bytes(comment_markers)
        skip_whitespace = b"\\s*"
    else:
        skip_whitespace = "\\s*"

    # in case comment_markers is an iterator
    # (for example, we just called _iterate_over_bytes on a bytes string)
    comment_markers = tuple(comment_markers)

    if len(comment_markers) == 1:
        comment_marker = comment_markers[0]
        def match(s):
            return s.lstrip().startswith(comment_marker)
    else:
        comment_pattern = _separators_to_re(comment_markers, comment_markers_is_bytes, separate=False, keep=False)
        comment_re = re.compile(skip_whitespace + comment_pattern)
        match = comment_re.match

    return _lines_filter_line_comment_lines(li, match)


@_export
def lines_containing(li, s, *, invert=False):
    """
    A lines modifier function.  Only yields lines
    that contain s.  (Filters out lines that
    don't contain s.)

    If invert is true, returns the opposite:
    filters out lines that contain s.

    Composable with all the lines_ modifier functions in the big.text module.
    """
    if invert:
        for t in li:
            if not s in t[1]:
                yield t
        return

    for t in li:
        if s in t[1]:
            yield t


def lines_grep(li, search, match, invert):
    if invert:
        for t in li:
            info, line = t
            m = search(line)
            if not m:
                setattr(info, match, None)
                yield t
        return

    for t in li:
        info, line = t
        m = search(line)
        if m:
            setattr(info, match, m)
            yield t

_lines_grep = lines_grep

@_export
def lines_grep(li, pattern, *, invert=False, flags=0, match='match'):
    """
    A lines modifier function.  Only yields lines
    that match the regular expression pattern.
    (Filters out lines that don't match pattern.)
    Stores the resulting re.Match object in info.match.

    pattern can be str, bytes, or an re.Pattern object.
    If pattern is not an re.Pattern object, it's compiled
    with re.compile(pattern, flags=flags).

    If invert is true, lines_grep only yields lines that
    *don't* match pattern, and sets info.match to None.

    The match parameter specifies the LineInfo attribute name to
    write to.  By default it writes to info.match; you can specify
    any valid identifier, and it will instead write the re.Match
    object (or None) to the identifier you specify.

    Composable with all the lines_ functions from the big.text module.

    (In older versions of Python, re.Pattern was a private type called
    re._pattern_type.)
    """
    if not match.isidentifier():
        raise ValueError('match must be a valid identifier')

    if not isinstance_re_pattern(pattern):
        pattern = re.compile(pattern, flags=flags)
    search = pattern.search

    return _lines_grep(li, search, match, invert)


@_export
def lines_sort(li, *, key=None, reverse=False):
    """
    A lines modifier function.  Sorts all input lines before yielding them.

    If key is specified, it's used as the key parameter to list.sort.
    The key function will be called with the (info, line) tuple yielded
    by the lines iterator.  If key is a false value, lines_sort sorts the
    lines lexicographically, from lowest to highest.

    If reverse is true, lines are sorted from highest to lowest.

    Composable with all the lines_ modifier functions in the big.text module.
    """
    lines = list(li)
    if key == None:
        fn = lambda t: t[1]
    else:
        fn = lambda t: key(t)
    lines.sort(key=fn, reverse=reverse)
    yield from iter(lines)


def lines_strip_line_comments(li, line_comment_splitter, quotes, multiline_quotes, escape, empty_join):
    "The generator function returned by the public lines_strip_line_comments function."
    state = None
    starting_pair_for_state = None

    for info, line in li:
        # print(f"[!!!] {info=}\n[!!!] {line=}\n[!!!] {state=}\n")

        if quotes or multiline_quotes:
            i = split_quoted_strings(line, quotes, escape=escape, multiline_quotes=multiline_quotes, state=state)
        else:
            i = iter( (('', line, ''),) )

        line_comment_segments = None

        column_number = info.column_number

        leading_quote = segment = trailing_quote = ''
        for leading_quote, segment, trailing_quote in i:
            # it's easier to proactively add the length, and remove it if we raise
            length_yielded = len(leading_quote) + len(segment) + len(trailing_quote)
            column_number += length_yielded

            if leading_quote:
                continue

            if state:
                # we're still in a quote from a previous line.
                # assert not leading_quote
                if trailing_quote:
                    state = None
                    starting_pair_for_state = None
                else:
                    # we didn't find the ending quote from the previous line,
                    # so this should be the entire line
                    assert segment == line
                continue

            fields = line_comment_splitter(segment, maxsplit=1)
            if len(fields) == 1:
                continue

            # found a comment marker in an unquoted segment!
            leading = fields[0]
            line_comment_segments = fields[1:]

            # exhaust i, draining it to line_comment_segments
            for triplet in i:
                line_comment_segments.extend(triplet)
            assert line_comment_segments
            line = info.clip_trailing(line, empty_join(line_comment_segments))

            break

        if not line_comment_segments:
            if leading_quote and not trailing_quote:
                if leading_quote not in multiline_quotes:
                    column_number -= length_yielded
                    raise SyntaxError(f"Line {info.line_number} column {column_number}: unterminated quoted marker {leading_quote}")
                state = leading_quote
                starting_pair_for_state = info, line

        yield (info, line)

    if state:
        info, line = starting_pair_for_state
        column_number -= length_yielded
        raise SyntaxError(f"Line {info.line_number} column {column_number}: unterminated quoted marker {state}")

_lines_strip_line_comments = lines_strip_line_comments

@_export
def lines_strip_line_comments(li, line_comment_markers, *,
    escape='\\', quotes=(), multiline_quotes=()):
    """
    A lines modifier function.  Strips line comments from the lines
    of a "lines iterator".  Line comments are substrings beginning
    with a special marker that mean the rest of the line should be
    ignored; lines_strip_line_comments truncates the line at the
    beginning of the leftmost line comment marker.

    line_comment_markers should be an iterable of line comment
    marker strings.  These are strings that denote a "line comment",
    which is to say, a comment that starts at that marker and
    extends to the end of the line.

    By default, quotes and multiline_quotes are both false,
    in which case lines_strip_line_comments will truncate each
    line, starting at the leftmost comment marker, and yield
    the resulting line.  If the line doesn't contain any comment
    markers, lines_strip_line_comments will yield it unchanged.

    However, the syntax of the text you're parsing might support
    quoted strings, and if so, comment marks in those quoted strings
    should be ignored.  lines_strip_quoted_strings supports this
    too, with its escape, quotes, and multiline_quotes parameters.

    If quotes is true, it must be an iterable of quote marker
    strings, length 1 or more.  lines_strip_line_comments will
    parse the line using big's split_quoted_strings function
    and ignore comment characters inside quoted strings.  Quoted
    strings may not span lines; if a line ends with an unterminated
    quoted string, lines_strip_line_comments will raise a SyntaxError.

    If multiline_quotes is true, it must be an iterable of
    quote marker strings, length 1 or more.  Quoted strings
    enclosed in multiline quotes may span multiple lines;
    quoted strings enclosed in (conventional) quotes are not
    permitted to.  If the last line yielded by the upstream
    iterator ends with an unterminated multiline string,
    lines_strip_line_comments will raise a SyntaxError.

    There must be no quote markers in common between quotes and
    multiline_quotes.

    If escape is true, it must be a string.  This string
    will "escape" (quote) quote markers, either multiline
    or non-multiline, as per backslash inside strings in Python.
    The default value for escape is "\\".

    What's the difference between lines_strip_line_comments and
    lines_filter_line_comment_lines?
      * lines_filter_line_comment_lines only recognizes lines that
        *start* with a comment separator (ignoring leading
        whitespace).  Also, it filters out those lines
        completely, rather than modifying the line.
      * lines_strip_line_comments handles comment characters
        anywhere in the line, although it can ignore
        comments inside quoted strings.  It truncates the
        line but still always yields the line.

    Composable with all the lines_ modifier functions in the big.text module.
    """

    # check line_comment_markers
    if not line_comment_markers:
        bad_value = True
    elif isinstance(line_comment_markers, bytes):
        bad_value = False
        line_comment_markers = _iterate_over_bytes(line_comment_markers)
        is_bytes = True
        empty = b''
    else:
        is_bytes = isinstance(line_comment_markers[0], bytes)
        if is_bytes:
            bad_value = False
            empty = b''
        else:
            bad_value = not isinstance(line_comment_markers[0], str)
            empty = ''
    if bad_value:
        raise ValueError(f"line comment markers must be str, bytes, or an non-empty iterable of str or bytes, not {line_comment_markers!r}")

    # use split_quoted_string to validate quotes, multiline_quotes, and escape, if specified
    not_empty = quotes or multiline_quotes
    if not_empty:
        if isinstance(not_empty, bytes):
            test_text = b'x'
        # if not_empty is not bytes, it's safe to index into
        elif isinstance(not_empty[0], bytes):
            test_text = b'x'
        else:
            test_text = 'x'

        # don't iterate! just throw the iterator away.
        # split_quoted_strings validates the inputs immediately,
        # and there's no point in calling the iterator.
        split_quoted_strings(test_text, quotes=quotes, multiline_quotes=multiline_quotes, escape=escape)

    line_comment_pattern = __separators_to_re(tuple(line_comment_markers), separators_is_bytes=is_bytes, separate=True, keep=True)
    line_comment_splitter = re.compile(line_comment_pattern).split

    return _lines_strip_line_comments(li, line_comment_splitter, quotes, multiline_quotes, escape, empty.join)




@_export
def lines_convert_tabs_to_spaces(li):
    """
    A lines modifier function.  Converts tabs to spaces for the lines
    of a "lines iterator", using the tab_width passed in to lines.

    Composable with all the lines_ modifier functions in the big.text module.
    """
    for info, line in li:
        yield (info, info.detab(line))


@_export
def lines_strip_indent(li):
    """
    A lines modifier function.  Strips leading whitespace and tracks
    the indent level.

    The indent level is stored in the LineInfo object's attribute
    "indent".  indent is an integer, the ordinal number of the current
    indent; if the text has been indented three times, indent will be 3.

    Strips any leading whitespace from the line, updating the LineInfo
    attributes "leading" and "column_number" as needed.

    Uses an intentionally simple algorithm.  Only understands tab and
    space characters as indent characters.  Internally detabs to spaces
    for consistency, using the tab_width passed in to lines.

    Text can only dedent out to a previous indent.
    Raises IndentationError if there's an illegal dedent.

    Blank lines and empty lines have the indent level of the
    *next* non-blank line, or 0 if there are no subsequent
    non-blank lines.

    Composable with all the lines_ functions from the big.text module.
    """
    indent = 0
    leadings = []
    empty = None
    first_time = True

    # a "blank line" is either empty or only has whitespace.
    # blank lines get the indent of the *next* non-blank line,
    # or 0 if there are no following non-blank lines.
    # this is *regardless* of the actual whitespace on the line.
    # all whitespace goes in to "leading", line is empty.
    blank_lines = []

    for info, line in li:
        if first_time:
            first_time = False
            if isinstance(line, bytes):
                space = b' '
                empty = b''
            else:
                space = ' '
                empty = ''

        lstripped = line.lstrip()
        if not lstripped:
            # yes, clip *TRAILING*.
            # When a line is 100% whitespace,
            # always clip to trailing.
            # That way you don't change column_number nonsensically.
            line = info.clip_trailing(line, line)
            blank_lines.append((info, line))
            # print(f"BL+ {info=} {lstripped=}")
            continue

        line = info.clip_leading(line, len(line) - len(lstripped))
        column_number = info.column_number

        if column_number == info.lines.column_number:
            # this line doesn't start with whitespace; text is at column 0.
            # outdent to zero.
            assert not info.leading
            indent = 0
            leadings.clear()
            new_indent = False
        # in all the remaining else cases, the line starts with whitespace.   and...
        elif not leadings:
            # this is the first indent.
            new_indent = True
        elif leadings[-1] == column_number:
            # indent is unchanged.
            new_indent = False
        elif column_number > leadings[-1]:
            # we are indented further than the previously observed indent.
            new_indent = True
        else:
            # we're outdenting.
            # ensure that this line's indent is one we've seen before.
            assert leadings
            leadings.pop()
            indent -= 1
            while leadings:
                l = leadings[-1]
                if l >= column_number:
                    if l > column_number:
                        leadings.clear()
                    break
                leadings.pop()
                indent -= 1
            if not leadings:
                raise IndentationError(f"Line {info.line_number} column {column_number}: unindent doesn't match any outer indentation level")
            new_indent = False

        # print(f"  >> {leadings=} {new_indent=}")
        if new_indent:
            leadings.append(column_number)
            indent += 1

        if blank_lines:
            # print(f"BL+ {blank_lines=}")
            for pair in blank_lines:
                pair[0].indent = indent # don't overwrite "info" or "line"! derp!
                yield pair
            blank_lines.clear()

        info.indent = indent
        yield (info, line)

    # flush trailing blank lines
    if blank_lines:
        for pair in blank_lines:
            info, line = pair
            info.indent = 0
            yield pair

@_export
def lines_filter_empty_lines(li):
    """
    A lines modifier function.  Filters out the empty lines
    of a "lines iterator".

    Preserves the line numbers.  If lines 0 through 2 are empty,
    line 3 is "a", line 4 is empty, and line 5 is "b", this will yield:
        (line_number=3, "a")
        (line_number=5, "b")

    Doesn't strip whitespace (or anything else).  If you want to filter
    out lines that only contain whitespace, add lines_rstrip to the chain
    of lines modifiers before lines_filter_empty_lines.

    Composable with all the lines_ modifier functions in the big.text module.
    """
    for t in li:
        if not t[1]:
            continue
        yield t



@_export
def wrap_words(words, margin=79, *, two_spaces=True):
    """
    Combines 'words' into lines and returns the result as a string.
    Similar to textwrap.wrap.

    'words' should be an iterator yielding str or bytes strings, and
    these strings should already be split at word boundaries.
    Here's an example of a valid argument for words:
        "this is an example of text split at word boundaries".split()

    A single '\n' indicates a line break.
    If you want a paragraph break, embed two '\n' characters in a row.

    'margin' specifies the maximum length of each line. The length of
    every line will be less than or equal to 'margin', unless the length
    of an individual element inside 'words' is greater than 'margin'.

    If 'two_spaces' is true, elements from 'words' that end in
    sentence-ending punctuation ('.', '?', and '!') will be followed
    by two spaces, not one.

    Elements in 'words' are not modified; any leading or trailing
    whitespace will be preserved.  You can use this to preserve
    whitespace where necessary, like in code examples.

    The objects yielded by words can be a subclass of either
    str or bytes, though wrap_words will only return str or bytes.
    All the objects yielded by words must have the same base class
    (str or bytes).
    """
    words = iter(words)
    col = 0
    empty = None
    lastword = None
    text = []
    first_word = True

    for word in words:
        if first_word:
            first_word = False
            if isinstance(word, bytes):
                empty = lastword = b''
                sentence_ending_punctuation = (b'.', b'?', b'!')
                two_spaces = b'  '
                one_space = b' '
                newline = b'\n'
            else:
                empty = lastword = ''
                sentence_ending_punctuation = ('.', '?', '!')
                two_spaces = '  '
                one_space = ' '
                newline = '\n'

        if word.isspace():
            lastword = word
            col = 0
            text.append(word)
            continue

        l = len(word)

        if two_spaces and lastword.endswith(sentence_ending_punctuation):
            space = two_spaces
            len_space = 2
        else:
            space = one_space
            len_space = 1

        if (l + len_space + col) > margin:
            if col:
                text.append(newline)
                col = 0
        elif col:
            text.append(space)
            col += len_space

        text.append(word)
        col += len(word)
        lastword = word

    if first_word:
        raise ValueError("no words to wrap")
    return empty.join(text)



_code_paragraph = "code paragraph"
_text_paragraph = "text paragraph"

@state.accessor()
class _column_wrapper_splitter:
    def __init__(self, is_bytes, tab_width, allow_code, code_indent, convert_tabs_to_spaces):
        # print(f"\n_column_wrapper_splitter({tab_width=}, {allow_code=}, {convert_tabs_to_spaces=})")
        self.is_bytes = is_bytes
        if is_bytes:
            self.empty = b''
            self.tab_string = b'\t'
            self.space_string = b' '
            self.newline_string = b'\n'
            self.paragraph_string = b'\n\n'
            self.make_iterator = _iterate_over_bytes
        else:
            self.empty = ''
            self.tab_string = '\t'
            self.space_string = ' '
            self.newline_string = '\n'
            self.paragraph_string = '\n\n'
            self.make_iterator = iter
        self.tab_width = tab_width
        self.allow_code = allow_code
        self.code_indent = code_indent
        self.convert_tabs_to_spaces = convert_tabs_to_spaces

        self.words = []

        self.leading = []
        self.word = []
        self.code = []

        # used to regulate line and paragraph breaks.
        # can be _code_paragraph, _text_paragraph, or None.
        # (if None, we've already handled the appropriate break.)
        self.previous_paragraph = None

        self.state_manager = state.StateManager(self.state_initial)

    def emit(self, c):
        # print(f" [emit]", repr(c))
        self.words.append(c)

    def line_break(self):
        # print(f" [  \\n]")
        self.words.append(self.newline_string)

    def paragraph_break(self):
        # print(f" [\\n\\n]")
        self.words.append(self.paragraph_string)

    def write(self, c):
        # write consumes c and makes calls as appropriate to
        # self.state().
        #
        # first, write aggregates together all consecutive
        # non-line-breaking whitespace characters, which it
        # stores in 'leading'.  if the next character is
        # a newline, it passes that single newline as 'word'.
        # otherwise it aggregates all consecutive non-whitespace
        # characters together, and passes those in as 'word'.
        #
        # thus we only call self.state() with two types of 'word':
        #     * a word, which is non-whitespace, and
        #     * a single '\n'.
        # all other whitespace is passed in as 'leading'.
        #
        # so for example, this input:
        #
        #   'hello there\nhow are you?\n\n  \n\ti am fine.\n  so there!'
        #
        # will result in self.state being called with these words,
        # and with whitespace being set to these values:
        #    leading   word
        #    -------   ------
        #    ''        'hello'
        #    ' '       'there'
        #    ''        '\n'
        #    ''        'how'
        #    ' '       'are'
        #    ' '       'you?'
        #    ''        '\n'
        #    ''        '\n'
        #    '  '      '\n'
        #    '\t'      'i'
        #    ' '       'am'
        #    ' '       'fine.'
        #    ''        '\n'
        #    '  '      'so'
        #    ' '       'there!'
        #
        # consecutive calls to write() behave the same as calling write()
        # once with both inputs concatenated together.  this:
        #     self.write('abc')
        #     self.write('def')
        # is the same as calling
        #     self.write('abcdef')
        #
        # you should call close() after the last write() call.

        leading = self.leading
        word = self.word
        write_word = None
        write_newline = False
        append_c_to_leading = False
        empty = self.empty
        newline_string = self.newline_string

        # print(f"<{c!r}> ", end='')

        if not c.isspace():
            word.append(c)
            return

        if word:
            write_word = empty.join(word)
            word.clear()

        if c == newline_string:
            if write_word:
                write_newline = True
            else:
                write_word = c
        else:
            append_c_to_leading = True

        if write_word:
            if leading:
                l = empty.join(leading)
                leading.clear()
            else:
                l = empty

            self.state(l, write_word)
            write_word = None

            if write_newline:
                self.state(empty, newline_string)
                write_newline = False

        if append_c_to_leading:
            leading.append(c)
            append_c_to_leading = False

    def close(self):
        # flush the current word, if any.
        if self.word:
            empty = self.empty
            self.state(empty.join(self.leading), empty.join(self.word))
            self.leading.clear()
            self.word.clear()

    def state_paragraph_start(self, leading, word):
        """
        Initial state.  Also the state we return to
        after encountering two '\n's in a row after
        a text line.
        """
        if word == self.newline_string:
            return
        if self.previous_paragraph:
            self.paragraph_break()
            self.previous_paragraph = None
        self.state = self.state_line_start
        self.state(leading, word)

    state_initial = state_paragraph_start

    def state_line_start(self, leading, word):
        if word == self.newline_string:
            # two '\n's in a row.
            if self.previous_paragraph == _code_paragraph:
                # we could still be in a code block.
                # remember the whitespace and continue.
                # we don't need to save the leading whitespace.
                self.code.append(word)
                return

            self.state = self.state_paragraph_start
            return

        if self.allow_code:
            col = 0
            tab_width = self.tab_width
            for c in self.make_iterator(leading):
                if c == self.tab_string:
                    col = col + tab_width - (col % tab_width)
                elif c == self.space_string:
                    col += 1
                else:
                    raise RuntimeError("unhandled whitespace character " + repr(c))
            if col >= self.code_indent:
                # code line!
                if self.previous_paragraph == _text_paragraph:
                    self.paragraph_break()
                    assert not self.code
                else:
                    if self.code:
                        for c in self.code:
                            self.line_break()
                        self.code.clear()

                self.state = self.state_code_line_start
                self.state(leading, word)
                return

        if self.previous_paragraph == _code_paragraph:
            self.paragraph_break()
        self.state = self.state_text_line_start
        self.state(leading, word)

    def state_text_line_start(self, leading, word):
        self.previous_paragraph = _text_paragraph
        self.state = self.state_in_text_line
        self.state(leading, word)

    def state_in_text_line(self, leading, word):
        if word == self.newline_string:
            self.state = self.state_line_start
            return
        self.emit(word)

    def state_code_line_start(self, leading, word):
        self.previous_paragraph = _code_paragraph
        self.col = 0
        self.state = self.state_in_code_line
        self.state(leading, word)

    def state_in_code_line(self, leading, word):
        if word == self.newline_string:
            self.emit(self.empty.join(self.code))
            self.code.clear()
            self.state = self.state_line_start
            self.state(self.empty, word)
            return

        tab_width = self.tab_width
        convert_tabs_to_spaces = self.convert_tabs_to_spaces
        col = self.col
        tab_string = self.tab_string
        space_string = self.space_string
        for c in self.make_iterator(leading):
            if c == tab_string:
                delta = tab_width - (col % tab_width)
                col += delta
                if convert_tabs_to_spaces:
                    self.code.append(space_string * delta)
                else:
                    self.code.append(c)
            elif c == space_string:
                col += 1
                self.code.append(c)
            else:
                raise RuntimeError("unhandled whitespace character " + repr(c))
        self.code.append(word)
        self.col = col + len(word)



@_export
def split_text_with_code(s, *, tab_width=8, allow_code=True, code_indent=4, convert_tabs_to_spaces=True):
    """
    Splits the string s into individual words,
    suitable for feeding into wrap_words.

    s may be either str or bytes.

    Paragraphs indented by less than code_indent will be
    broken up into individual words.

    If `allow_code` is true, paragraphs indented by at least
    code_indent spaces will preserve their whitespace:
    internal whitespace is preserved, and the newline is
    preserved.  (This will preserve the formatting of code
    examples, when these words are rejoined into lines
    by wrap_words.)

    s can be str, bytes, or a subclass of either, though
    split_text_with_code will only return str or bytes.

    if s is empty, returns a list containing an empty string.
    """
    is_bytes = isinstance(s, bytes)
    if is_bytes:
        iterable = _iterate_over_bytes(s)
        empty = b''
    else:
        iterable = s
        empty = ''

    cws = _column_wrapper_splitter(is_bytes, tab_width, allow_code, code_indent, convert_tabs_to_spaces)

    for c in iterable:
        cws.write(c)
    cws.close()
    return_value = cws.words
    if not return_value:
        return [empty]
    return return_value


@_export
class OverflowStrategy(enum.Enum):
    """
    Enum providing constants to specify how merge_columns
    handles overflow in columns.
    """
    INVALID = enum.auto()
    RAISE = enum.auto()
    INTRUDE_ALL = enum.auto()
    # INTRUDE_MINIMUM = enum.auto()  # not implemented yet
    DELAY_ALL = enum.auto()
    # DELAY_MINIMUM = enum.auto()  # not implemented yet

@_export
def merge_columns(*columns, column_separator=None,
    overflow_strategy=OverflowStrategy.RAISE,
    overflow_before=0,
    overflow_after=0,
    ):
    """
    Merge n column tuples, with each column tuple being
    formatted into its own column in the resulting string.
    Returns a string.

    columns should be an iterable of column tuples.
    Each column tuple should contain three items:
        (text, min_width, max_width)
    text should be a single string, either str or bytes,
    with newline characters separating lines. min_width
    and max_width are the minimum and maximum permissible
    widths for that column, not including the column
    separator (if any).

    Note that this function doesn't text-wrap the lines.

    column_separator is printed between every column.

    overflow_strategy tells merge_columns how to handle a column
    with one or more lines that are wider than that column's max_width.
    The supported values are:

        OverflowStrategy.RAISE

            Raise an OverflowError.  The default.

        OverflowStrategy.INTRUDE_ALL

           Intrude into all subsequent columns on all lines
           where the overflowed column is wider than its max_width.

        OverflowStrategy.DELAY_ALL

           Delay all columns after the overflowed column,
           not beginning any until after the last overflowed line
           in the overflowed column.

    When overflow_strategy is INTRUDE_ALL or DELAY_ALL, and
    either overflow_before or overflow_after is nonzero, these
    specify the number of extra lines before or after
    the overflowed lines in a column.

    text and column_separator can be str, bytes, or a subclass
    of either, though merge_columns will only return str or bytes.
    All these objects (text and column_separator) must have the
    same baseclass, str or bytes.
    """
    assert overflow_strategy in (OverflowStrategy.INTRUDE_ALL, OverflowStrategy.DELAY_ALL, OverflowStrategy.RAISE)
    raise_overflow_error = overflow_strategy == OverflowStrategy.RAISE
    delay_all = overflow_strategy == OverflowStrategy.DELAY_ALL

    assert columns
    is_bytes = isinstance(columns[0][0], bytes)

    if is_bytes:
        empty = b''
        space = b' '
        newline = b'\n'
    else:
        empty = ''
        space = ' '
        newline = '\n'

    if column_separator is None:
        column_separator = space

    _columns = columns
    columns = []
    empty_columns = []
    last_too_wide_lines = []
    max_lines = -1

    column_spacing = len(column_separator)

    overflows = []
    in_overflow = False
    def add_overflow():
        nonlocal in_overflow
        in_overflow = False
        if overflows:
            last_overflow = overflows[-1]
            if last_overflow[1] >= (overflow_start - 1):
                overflows.pop()
                overflows.append((last_overflow[0], overflow_end))
                return
        overflows.append((overflow_start, overflow_end))

    overflow_start = overflow_end = None
    def next_overflow():
        nonlocal overflow_start
        nonlocal overflow_end
        if overflows:
            overflow_start, overflow_end = overflows.pop()
        else:
            overflow_start = overflow_end = sys.maxsize

    for column_number, (s, min_width, max_width) in enumerate(_columns):

        # check types, let them raise exceptions as needed
        operator.index(min_width)
        operator.index(max_width)

        empty_columns.append(max_width * space)

        if isinstance(s, (str, bytes)):
            lines = s.rstrip().split(newline)
        else:
            lines = s
        max_lines = max(max_lines, len(lines))

        # loop 1:
        # measure each line length, determining
        #  * maximum line length, and
        #  * all overflow lines
        rstripped_lines = []
        overflows = []
        max_line_length = -1
        in_overflow = False

        for line_number, line in enumerate(lines):
            line = line.rstrip()
            assert not newline in line
            rstripped_lines.append(line)

            length = len(line)
            max_line_length = max(max_line_length, length)

            line_overflowed = length > max_width
            if (not in_overflow) and line_overflowed:
                # starting new overflow
                if raise_overflow_error:
                    raise OverflowError(f"overflow in column {column_number}: {line!r} is {length} characters, column max_width is {max_width}")
                overflow_start = max(line_number - overflow_before, 0)
                in_overflow = True
            elif in_overflow and (not line_overflowed):
                # ending current overflow
                overflow_end = line_number - 1 + overflow_after
                add_overflow()

        if in_overflow:
            overflow_end = line_number + overflow_after
            add_overflow()
            for i in range(overflow_after):
                rstripped_lines.append(empty)

        if delay_all and overflows:
            overflows.clear()
            overflows.append((0, overflow_end))

        # loop 2:
        # compute padded lines and in_overflow for every line
        padded_lines = []
        overflows.reverse()
        overflow_start = overflow_end = None

        in_overflow = False
        next_overflow()
        for line_number, line in enumerate(lines):
            if line_number > overflow_end:
                in_overflow = False
                next_overflow()
            if line_number >= overflow_start:
                in_overflow = True
            if not in_overflow:
                line = line.ljust(max_width)
            padded_lines.append((line, in_overflow))

        columns.append(padded_lines)


    column_iterators = [iter(c) for c in columns]
    lines = []

    while True:
        line = []
        all_iterators_are_exhausted = True
        add_separator = False
        in_overflow = False
        for column_iterator, empty_column in zip(column_iterators, empty_columns):
            if add_separator:
                line.append(column_separator)
            else:
                add_separator = True

            try:
                column, in_overflow = next(column_iterator)
                all_iterators_are_exhausted = False
            except StopIteration:
                column = empty_column
            line.append(column)
            if in_overflow:
                break
        if all_iterators_are_exhausted:
            break
        line = empty.join(line).rstrip()
        lines.append(line)

    text = newline.join(lines)
    return text.rstrip()

@_export
def int_to_words(i, flowery=True, ordinal=False):
    """
    Converts an integer into the equivalent English string.

    int_to_words(2) -> "two"
    int_to_words(35) -> "thirty-five"

    If the keyword-only parameter "flowery" is true,
    you also get commas and the word "and" where you'd expect them.
    (When "flowery" is True, int_to_words(i) produces identical
    output to inflect.engine().number_to_words(i).)

    If the keyword-only parameter "ordinal" is true,
    the string produced describes that *ordinal* number
    (instead of that *cardinal* number).  Ordinal numbers
    describe position, e.g. where a competitor placed in a
    competition.  int_to_words(1) returns the string 'one',
    but int_to_words(1, ordinal=True) returns the string 'first'.

    Numbers >= 10*75 (one quadrillion vigintillion)
    are only converted using str(i).  Sorry!
    """
    if not isinstance(i, int):
        raise ValueError("i must be int")

    if (i >= 10**75) or (i <= -10**75):
        return str(i)

    is_negative = i < 0
    if is_negative:
        i = -i

    if ordinal:
        first_twenty = (
            "zeroth",
            "first", "second", "third", "fourth", "fifth",
            "sixth", "seventh", "eighth", "ninth", "tenth",
            "eleventh", "twelveth", "thirteenth", "fourteenth", "fifteenth",
            "sixteenth", "seventeenth", "eighteenth", "nineteenth",
            )
    else:
        first_twenty = (
            "zero",
            "one", "two", "three", "four", "five",
            "six", "seven", "eight", "nine", "ten",
            "eleven", "twelve", "thirteen", "fourteen", "fifteen",
            "sixteen", "seventeen", "eighteen", "nineteen",
            )

    tens = (
        None, None, "twenty", "thirty", "forty", "fifty",
        "sixty", "seventy", "eighty", "ninety",
        )

    strings = []
    append = strings.append
    spacer = ''

    # go-faster stripes shortcut:
    # most numbers are small.
    # the fastest route is for numbers < 100.
    # the next-fastest is for numbers < 1 trillion.
    # the slow route handles numbers < 10**66.
    if i >= 100:
        if i >= 10**12:
            quantities = (
            # note!        v  leading spaces!
            (10**63,      " vigintillion"),
            (10**60,    " novemdecillion"),
            (10**57,     " octodecillion"),
            (10**54,     " septdecillion"),
            (10**51,      " sexdecillion"),
            (10**48,      " qindecillion"),
            (10**45, " quattuordecillion"),
            (10**42,      " tredecillion"),
            (10**39,      " duodecillion"),
            (10**36,       " undecillion"),
            (10**33,       "   decillion"),
            (10**30,       "   nonillion"),
            (10**27,       "   octillion"),
            (10**24,       "  septillion"),
            (10**21,       "  sextillion"),
            (10**18,       " quintillion"),
            (10**15,       " quadrillion"),
            (10**12,          " trillion"),
            (10** 9,           " billion"),
            (10** 6,           " million"),
            (10** 3,          " thousand"),
            (10** 2,           " hundred"),
            )
        else:
            quantities = (
            # note!             v  leading spaces!
            (10** 9,           " billion"),
            (10** 6,           " million"),
            (10** 3,          " thousand"),
            (10** 2,           " hundred"),
            )

        for threshold, english in quantities:
            if i >= threshold:
                upper = i // threshold
                i = i % threshold
                append(spacer)
                append(int_to_words(upper, flowery=flowery))
                append(english)
                spacer = ', ' if flowery else ' '

    if strings:
        spacer = " and " if flowery else " "

    if i >= 20:
        t = i // 10
        append(spacer)
        append(tens[t])
        spacer = '-'
        i = i % 10

    # don't add "zero" to the end if we already have strings
    if i or (not strings):
        append(spacer)
        append(first_twenty[i])
    elif ordinal and strings:
        if strings[-1][-1] == 'y':
            s = strings.pop()
            strings.append(s[:-1] + "ie")
        strings.append("th")

    if is_negative:
        strings.insert(0, "negative ")

    return "".join(strings)

