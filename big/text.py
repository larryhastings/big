#!/usr/bin/env python3

# --8<-- start big license --8<--
_big_license = """
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
# --8<-- end big license --8<--

from .boundinnerclass import BoundInnerClass
import functools
import heapq
import itertools
from itertools import zip_longest
from .itertools import PushbackIterator
import math
import codecs
import re
import struct
import types
import warnings

# --8<-- start big word wrap trio imports --8<--
import enum
import operator
import sys
# --8<-- end big word wrap trio imports --8<--


try: # pragma: no cover
    from re import Pattern as re_Pattern
except ImportError: # pragma: no cover
    re_Pattern = re._pattern_type

def _isinstance_re_pattern(o):
    # big supports patterns from the PyPI 'regex' package too--but
    # importing regex costs ~5ms, just to recognize its Pattern
    # type.  so we don't import it; we check sys.modules instead.
    # this is lossless, not approximate: a regex.Pattern instance
    # can only exist if *somebody* already imported regex, and
    # importing it put it in sys.modules.  if it's not there, no
    # regex.Pattern exists anywhere in the process, and False is
    # a theorem, not a guess.
    if isinstance(o, re_Pattern):
        return True
    regex = sys.modules.get('regex')
    return (regex is not None) and isinstance(o, regex.Pattern)

from . import builtin
mm = builtin.ModuleManager()
export = mm.export


# --8<-- start big _iterate_over_bytes --8<--
# --8<-- requires big license --8<--

def _iterate_over_bytes(b):
    # this may not actually iterate over bytes.
    # for example, we iterate over apostrophes and double_quotes
    # for gently_title, and those might be strings or bytes,
    # or iterables of strings or bytes.
    if isinstance(b, bytes):
        return (b[i:i+1] for i in range(len(b)))
    return iter(b)

# --8<-- end big _iterate_over_bytes --8<--


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


@export
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


# Tuples enumerating all the whitespace and linebreak characters,
# for use with big functions taking "separators" arguments
# (e.g. lines, multisplit).  For an explanation of what they
# represent, please see the "Whitespace and line-breaking
# characters in Python and big" deep-dive in big's README.

export('str_whitespace')
str_whitespace = (
    # character string
    # |       ordinal number
    # |        |    c in decimal
    # |        |     |    c in hex
    # |        |     |      |      name
    # |        |     |      |        |
    #vvvv-----vvv---vvv---vvvvvv---vvvvvvvvvvv
    '\t'    , #01     9 - 0x0009 - tab
    '\n'    , #02    10 - 0x000a - linebreak
    '\v'    , #03    11 - 0x000b - vertical tab
    '\f'    , #04    12 - 0x000c - form feed
    '\r'    , #05    13 - 0x000d - carriage return
    '\r\n'  , # bonus! the classic DOS linebreak sequence!

    ###################################################
    ## Note: Unicode doesn't consider these next four
    ## ASCII "separator" characters to be whitespace!
    ## (I agree, I think this is a Python bug.)
    ###################################################
    '\x1c'  , #06    28 - 0x001c - file separator
    '\x1d'  , #07    29 - 0x001d - group separator
    '\x1e'  , #08    30 - 0x001e - record separator
    '\x1f'  , #09    31 - 0x001f - unit separator

    ' '     , #10    32 - 0x0020 - space
    '\x85'  , #11   133 - 0x0085 - next line
    '\xa0'  , #12   160 - 0x00a0 - non-breaking space
    '\u1680', #13  5760 - 0x1680 - ogham space mark
    '\u2000', #14  8192 - 0x2000 - en quad
    '\u2001', #15  8193 - 0x2001 - em quad
    '\u2002', #16  8194 - 0x2002 - en space
    '\u2003', #17  8195 - 0x2003 - em space
    '\u2004', #18  8196 - 0x2004 - three-per-em space
    '\u2005', #19  8197 - 0x2005 - four-per-em space
    '\u2006', #20  8198 - 0x2006 - six-per-em space
    '\u2007', #21  8199 - 0x2007 - figure space
    '\u2008', #22  8200 - 0x2008 - punctuation space
    '\u2009', #23  8201 - 0x2009 - thin space
    '\u200a', #24  8202 - 0x200a - hair space
    '\u2028', #25  8232 - 0x2028 - line separator
    '\u2029', #26  8233 - 0x2029 - paragraph separator
    '\u202f', #27  8239 - 0x202f - narrow no-break space
    '\u205f', #28  8287 - 0x205f - medium mathematical space
    '\u3000', #29 12288 - 0x3000 - ideographic space
    )
export('str_whitespace_without_crlf')
str_whitespace_without_crlf = tuple(s for s in str_whitespace if s != '\r\n')

export('whitespace')
whitespace = str_whitespace
export('whitespace_without_crlf')
whitespace_without_crlf = str_whitespace_without_crlf

# Whitespace as defined by Unicode.  The same as Python's definition,
# except we remove the four ASCII separator characters.
export('unicode_whitespace')
unicode_whitespace = tuple(s for s in str_whitespace if not ('\x1c' <= s <= '\x1f'))
export('unicode_whitespace_without_crlf')
unicode_whitespace_without_crlf = tuple(s for s in unicode_whitespace if s != '\r\n')

# Whitespace as defined by ASCII.  The same as Unicode,
# but only within the first 128 code points.
# Note: these are still *str* objects.
export('ascii_whitespace')
ascii_whitespace = tuple(s for s in unicode_whitespace if (s < '\x80'))
export('ascii_whitespace_without_crlf')
ascii_whitespace_without_crlf = tuple(s for s in ascii_whitespace if s != '\r\n')

# Whitespace as defined by the Python bytes object.
# Bytes objects, using the ASCII encoding.
export('bytes_whitespace')
bytes_whitespace = encode_strings(ascii_whitespace)
export('bytes_whitespace_without_crlf')
bytes_whitespace_without_crlf = tuple(s for s in bytes_whitespace if s != b'\r\n')


# --8<-- start big linebreaks --8<--
# --8<-- requires big license --8<--
str_linebreaks = (
    # char    decimal   hex      identity
    ##########################################
    '\n'    , #   10 - 0x000a - linebreak
    '\v'    , #   11 - 0x000b - vertical tab
    '\f'    , #   12 - 0x000c - form feed
    '\r'    , #   13 - 0x000d - carriage return
    '\r\n'  , # bonus! the classic DOS linebreak sequence!
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
    # Also: welcome to big, Acorn and RISC OS users!
    # What are you doing here?  You can't run Python 3.6+!
    )
str_linebreaks_without_crlf = tuple(s for s in str_linebreaks if s != '\r\n')

linebreaks = str_linebreaks
linebreaks_without_crlf = str_linebreaks_without_crlf

# Whitespace as defined by Unicode.  The same as Python's definition,
# except we again remove the four ASCII separator characters.
unicode_linebreaks = tuple(s for s in str_linebreaks if not ('\x1c' <= s <= '\x1f'))
unicode_linebreaks_without_crlf = tuple(s for s in unicode_linebreaks if s != '\r\n')

# Linebreaks as defined by ASCII.  The same as Unicode,
# but only within the first 128 code points.
# Note: these are still *str* objects.
ascii_linebreaks = tuple(s for s in unicode_linebreaks if s < '\x80')
ascii_linebreaks_without_crlf = tuple(s for s in ascii_linebreaks if s != '\r\n')

# Whitespace as defined by the Python bytes object.
# Bytes objects, using the ASCII encoding.
#
# Notice that bytes_linebreaks doesn't contain \v or \f.
# That's because the Python bytes object doesn't consider those
# to be linebreak characters.
#
#    >>> define is_linebreak_str(c): return len( ("a"+c+"x").splitlines() ) > 1
#    >>> is_linebreak_str('\n')
#    True
#    >>> is_linebreak_str('\r')
#    True
#    >>> is_linebreak_str('\f')
#    True
#    >>> is_linebreak_str('\v')
#    True
#
#    >>> define is_linebreak_byte(c): return len( (b"a"+c+b"x").splitlines() ) > 1
#    >>> is_linebreak_byte(b'\n')
#    True
#    >>> is_linebreak_byte(b'\r')
#    True
#    >>> is_linebreak_byte(b'\f')
#    False
#    >>> is_linebreak_byte(b'\v')
#    False
#
# However! with defensive programming, in case this changes in the future
# (as it should!), big will automatically still agree with Python.
#
# p.s. in the above code examples, you have to put characters around the
# linebreak character, because str.splitlines (and bytes.splitlines)
# rstrips the string of linebreak characters before it splits lines, sigh.

bytes_linebreaks = (
    b'\n'    , #   10 0x000a - linebreak
    )

if len(b'x\vx'.splitlines()) == 2: # pragma: nocover
    bytes_linebreaks += (
        b'\v'    , #   11 - 0x000b - vertical tab
        )

if len(b'x\fx'.splitlines()) == 2: # pragma: nocover
    bytes_linebreaks += (
        b'\f'    , #   12 - 0x000c - form feed
        )

bytes_linebreaks += (
    b'\r'    , #   13 0x000d - carriage return
    b'\r\n'  , # bonus! the classic DOS linebreak sequence!
    )

bytes_linebreaks_without_crlf = tuple(s for s in bytes_linebreaks if s != b'\r\n')
# --8<-- end big linebreaks --8<--

export('str_linebreaks')
export('str_linebreaks_without_crlf')
export('linebreaks')
export('linebreaks_without_crlf')
export('unicode_linebreaks')
export('unicode_linebreaks_without_crlf')
export('ascii_linebreaks')
export('ascii_linebreaks_without_crlf')
export('bytes_linebreaks')
export('bytes_linebreaks_without_crlf')


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
    if isinstance(o, int):
        return -o # the reverse index!
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
    return t(_multisplit_reversed(p, name) for p in reversed(o))


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

    bytes_whitespace: bytes_whitespace_without_crlf + (b"\n\r",),
    bytes_whitespace_without_crlf: bytes_whitespace_without_crlf,

    str_linebreaks: str_linebreaks_without_crlf + ("\n\r",),
    str_linebreaks_without_crlf: str_linebreaks_without_crlf,

    unicode_linebreaks: unicode_linebreaks_without_crlf + ("\n\r",),
    unicode_linebreaks_without_crlf: unicode_linebreaks_without_crlf,

    ascii_linebreaks: ascii_linebreaks_without_crlf + ("\n\r",),
    ascii_linebreaks_without_crlf: ascii_linebreaks_without_crlf,

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


@export
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
    empty = s[-1:-1]
    extension = (None, empty)

    if not _isinstance_re_pattern(pattern):
        pattern = re.compile(pattern, flags=flags)

    # optimized fast path for the most frequent use case
    if count == 1:
        match = pattern.search(s)
        if not match:
            return (s, None, empty)
        return (s[:match.start(0)], match, s[match.end(0):])

    if count == 0:
        return (s,)

    if count < 0:
        raise ValueError("count must be >= 0")

    result = []
    extend = result.extend
    matches_iterator = pattern.finditer(s)

    try:
        previous_end = 0
        for remaining in range(count, 0, -1):
            match = next(matches_iterator)
            extend((s[previous_end:match.start(0)], match))
            previous_end = match.end(0)
        extension = ()
    except StopIteration:
        extension *= remaining

    result.append(s[previous_end:])
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

@export
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
    if not _isinstance_re_pattern(pattern):
        pattern = re.compile(pattern, flags=flags)

    return _reversed_re_finditer(pattern, string)


@export
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

    empty = s[0:0]
    extension = (empty, None)

    # optimized fast path for the most frequent use case
    if count == 1:
        matches_iterator = reversed_re_finditer(pattern, s, flags)
        try:
            match = next(matches_iterator)
            return (s[:match.start(0)], match, s[match.end(0):])
        except StopIteration:
            return (empty, None, s)

    if count == 0:
        return (s,)

    if count < 0:
        raise ValueError("count must be >= 0")

    result = []
    extend = result.extend
    matches_iterator = reversed_re_finditer(pattern, s, flags)

    previous_start = len(s)
    try:
        for remaining in range(count, 0, -1):
            match = next(matches_iterator)
            # s, separator, after = s.rpartition(match.group(0))
            after = s[match.end(0):previous_start]
            extend((after, match))
            previous_start = match.start(0)
        extension = ()
    except StopIteration:
        extension *= remaining

    result.append(s[:previous_start])
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



@export
def multistrip(s, separators, left=True, right=True):
    """
    Like str.strip, but supports stripping multiple strings.

    Strips from the string "s" all leading and trailing
    instances of strings found in "separators".

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
    string does not end with a separator (or is empty).

    multistrip is "greedy"; if more than one separator
    matches, multistrip will strip the longest one.

    You can pass in an instance of a subclass of bytes or str
    for s and elements of separators, but the base class
    for both must be the same (str or bytes).

    Returns s unchanged, or a slice of s, with the leading
    and/or trailing separators stripped.
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

    if check_separators:
        s2 = []
        for o in separators:
            if not isinstance(o, s_type):
                raise TypeError("separators must be an iterable of non-empty objects the same type as s")
            if not o:
                raise ValueError("separators must be an iterable of non-empty objects the same type as s")
            s2.append(o)
        separators = tuple(s2)
    if not separators:
        raise ValueError("separators must be an iterable of non-empty objects the same type as s")

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


# --8<-- start big toy_multisplit --8<--
# --8<-- requires big license --8<--

def _toy_multisplit_as_pairs(segments, empty):
    # segments alternates non-separator and separator strings,
    # always starting and ending with a (possibly empty)
    # non-separator string.  pair each non-separator string
    # with its subsequent separator--appending the always-empty
    # trailing separator--to make the keep=True 2-tuple form.
    segments.append(empty)
    return list(zip(segments[::2], segments[1::2]))


def toy_multisplit(s, separators):
    """
    A toy version of multisplit.

    s should be str or bytes.  separators should be a list or
    tuple of str (or bytes, matching s); if separators is itself
    a single str or bytes, every character (or byte) in it is a
    separator.  separators must be non-empty and must not contain
    the empty string.

    Returns a list of 2-tuples of

        (string, separator)

    where string is a (possibly empty) substring of s containing
    no separators, and separator is the separator that followed
    it.  The final 2-tuple's separator is always the empty string.
    Splitting is greedy: at each position, the longest matching
    separator wins.  The result is identical to

        list(multisplit(s, separators, keep=True, separate=True))

    Why use this instead of multisplit?  It has no startup time.
    It's also available as a snippet.
    """
    if not isinstance(separators, (list, tuple)):
        separators = [separators[i:i+1] for i in range(len(separators))]
    # assert separators
    if isinstance(s, bytes):
        empty = b''
    else:
        empty = ''
    # assert empty not in separators

    # special-cased only one separator,
    # for PEDAL TO THE MEDAL HYPER-SPEED
    if len(separators) == 1:
        segments = []
        sep = separators[0]
        length = len(sep)
        while s:
            index = s.find(sep)
            if index == -1:
                segments.append(s)
                s = None
                break
            segments.append(s[:index])
            segments.append(sep)
            index2 = index + length
            s = s[index2:]
        if s is not None:
            segments.append(s)
        return _toy_multisplit_as_pairs(segments, empty)

    # separators_by_length is a list of tuples:
    #    (length, bucket_of_separators_of_that_length)
    #
    # we add a bucket for every length, including 0.
    # (makes the algorithm easier.)
    longest_separator = max([len(sep) for sep in separators])
    separators_by_length = []
    for i in range(longest_separator, -1, -1):
        separators_by_length.append((i, set()))

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
        segments.append(empty.join(word))
        word.clear()

    longest_separator_length = separators_by_length[0][0]
    while s:
        substring = s
        for length, separators_set in separators_by_length:
            substring = substring[:length]
            # print(f"substring={substring!r} separators_set={separators_set!r}")
            if substring in separators_set:
                flush_word()
                segments.append(substring)
                s = s[length:]
                break
        else:
            # slice on a bytes object gives you back a bytes object.
            # s[0] on a bytes object gives you back an int.
            word.append(s[:1])
            s = s[1:]
    flush_word()

    return _toy_multisplit_as_pairs(segments, empty)

# --8<-- end big toy_multisplit --8<--

export(toy_multisplit)


# Constants supported by multisplit keep... FOR NOW.
# As of 0.14, all three constants are deprecated.  No sooner
# than August 2027, keep will only be a boolean.
#    keep=false will be "throw away the separators".
#    keep=true will be the AS_PAIRS form, the 2-tuple of (text, separator).
#
# Internally, big only ever used keep=False and keep=True anyway;
# the only internal users of these constants are the tests.
AS_PAIRS="AS_PAIRS"
export(AS_PAIRS)
ALTERNATING="ALTERNATING"
export(ALTERNATING)
JOINED="JOINED"
export(JOINED)

# for strip
LEFT = "LEFT"
export(LEFT)
RIGHT = "RIGHT"
export(RIGHT)
PROGRESSIVE = "PROGRESSIVE"
export(PROGRESSIVE)


def multisplit(s, separators, keep, maxsplit, reverse, separate, strip, is_bytes, internally_keep_separators):
    "Internal generator function for multisplit."
    # by the time we're called, keep is always False,
    # ALTERNATING, AS_PAIRS, or JOINED--the public multisplit
    # translated keep=True into AS_PAIRS.
    if maxsplit is None:
        maxsplit = -1
    elif maxsplit == 0:
        if keep == AS_PAIRS:
            yield (s, s[-1:-1])
        else:
            yield s
        return

    if reverse:
        # if reverse is true, when separators overlap,
        # we need to prefer the rightmost one rather than
        # the leftmost one.  how do we do *that*?
        # Eric Smith had the brainstorm: reverse the string
        # and the separators, split, and reverse the output
        # and the strings in the output.
        original_s = s
        s = _multisplit_reversed(s, 's')

        separators = tuple(separators)
        s2 = _reversed_builtin_separators.get(separators, None)
        if s2 is not None:
            separators = s2
        else:
            separators = _multisplit_reversed(separators, 'separators')

    pattern = _separators_to_re(separators, is_bytes, keep=internally_keep_separators, separate=separate)

    # we write down the lengths, it's easier if we're reversing
    splits_remaining = maxsplit
    l = []
    append = l.append
    len_s = len(s)
    zero_replacement = -len_s # this reverses properly, 0 doesn't
    previous_match_end = zero_replacement
    for match in re.finditer(pattern, s):
        if not splits_remaining:
            break
        start = match.start() or zero_replacement
        end = match.end() or zero_replacement
        # segment
        append((previous_match_end, start))
        if internally_keep_separators:
            # separator
            append((start, end))
        splits_remaining -= 1
        previous_match_end = end

    # final segment
    append((previous_match_end, len_s))

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
            if nonsep[0] != nonsep[1]:
                last_non_empty_nonsep = i
                break
        else:
            last_non_empty_nonsep = 0

        if desired_length > (last_non_empty_nonsep + 2):
            # strip!
            l = l[:last_non_empty_nonsep + 1]

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

    # but wait! there's more!
    # now that we use re.finditer, we just write down the offsets.
    # _multisplit_reversed has us covered.
    #
    # let's say we write down the tuple (5, 8), meaning we want to
    # yield the value s[5:8].  but we're in reverse mode, so we
    # reverse everything with _multisplit_reversed.  well, it
    # reverses the tuple, but it also *negates the ints*.  so the
    # tuple becomes (-8, -5), which means we yield s[-8:-5], which
    # is perfectly the reverse of the offset we wrote down!

    if reverse:
        l = _multisplit_reversed(l, 'l')
        s = original_s

    l.reverse()

    if (not keep) or (keep == ALTERNATING):
        while l:
            offsets = l.pop()

            o = s[ offsets[0] : offsets[1] ]
            yield o
        return

    # from here on out, keep is AS_PAIRS or JOINED: pair up
    # each segment with its following separator, and yield
    # either the 2-tuple or the concatenation.

    append_empty = (len(l) % 2) == 1
    if append_empty:
        l.insert(0, (len_s, len_s))

    previous = None
    while l:
        offsets = l.pop()

        o = s[ offsets[0] : offsets[1] ]

        if previous is None:
            previous = o
            continue
        if keep == AS_PAIRS:
            yield (previous, o)
        else:
            # keep == JOINED
            yield previous + o
        previous = None

_multisplit = multisplit


@export
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

    Returns an iterator yielding values split from s.  The values
    yielded are slices of the original object, or in some cases
    adjacent slices joined with +.  All slices are yielded in
    left-to-right order; this even includes zero-length strings,
    which are sliced from the contextually correct spot.

    If keep is true and strip is false, joining all the strings
    yielded together will recreate s.

    multisplit is "greedy": if two or more separators start at the same
    location in "s", multisplit splits using the longest matching separator.
    For example:
        big.multisplit('wxabcyz', ('a', 'abc'))
    yields 'wx' then 'yz'.

    "keep" indicates whether or not multisplit should keep the separator
    strings.  It supports two values:
        false (the default)
            Yield just the split strings, discarding the separators.
        true
            Yield 2-tuples containing a non-separator string and its
            subsequent separator string.  Either string may be empty;
            the separator string in the last 2-tuple will always be
            empty, and if `s` ends with a separator string, *both*
            strings in the final 2-tuple will be empty.

    "keep" also supports three symbolic values.  These values
    are *deprecated,* and will be removed no sooner than one
    year after the release of 0.14; passing any of them emits
    a DeprecationWarning:

        AS_PAIRS
            The old name for what is now keep=True, the 2-tuple
            (string, separator) form.

        ALTERNATING
            Yield alternating strings in the output: strings consisting
            of separators, alternating with strings consisting of
            non-separators.  The first and last will be non-separators,
            which means this always yields an *odd* number of substrings.
            If separate is true, separator strings will contain exactly
            one separator, and non-separator strings may be empty;
            if separate is false, separator strings will contain one or
            more separators, and non-separator strings will never be empty,
            unless s was empty.

            You can recreate the original string by using "".join to join
            the strings yielded.

            You can recreate this format using keep=True with the following:
                flat = list(itertools.chain.from_iterable(big.multisplit(s, seps, keep=True)))
                flat.pop()

        JOINED
            Each separator is appended to its preceding string.

            You can recreate this format using keep=True with the following:
                (a + b  for (a, b) in big.multisplit(s, seps, keep=True))

    *NOTE:* In big 0.13 and earlier, keep=True meant what JOINED
    now means: separators appended to their preceding strings.  0.14
    changed its meaning to the 2-tuple form.  (Why?  The 2-tuple form
    can be mechanically converted into any other form, making it the
    ur-form that's useful in every situation.  It's just a better API
    this way--you don't need any of that other junk, I promise.)

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
        multisplit("A x x Z", (" x ",), keep=True)
    will split on the leftmost instance of " x ", yielding
        ("A", " x "), ("x Z", "")
    whereas
        multisplit("A x x Z", (" x ",), keep=True, reverse=True)
    will split on the rightmost instance of " x ", yielding
        ("A x", " x "), ("Z", "")

    You can pass in an instance of a subclass of bytes or str
    for s and elements of separators, but the base class
    for both must be the same (str or bytes).
    """
    if keep:
        # keep=True means the 2-tuple form (what 0.13 called
        # AS_PAIRS).  the constants still work, deprecated;
        # they'll be removed no sooner than August 2027.
        if keep == ALTERNATING:
            warnings.warn(
                "multisplit's keep=ALTERNATING is deprecated, and will be"
                " removed no sooner than August 2027.  Transform the 2-tuples"
                " yielded by keep=True instead.",
                DeprecationWarning, stacklevel=2)
        elif keep == JOINED:
            warnings.warn(
                "multisplit's keep=JOINED is deprecated, and will be"
                " removed no sooner than August 2027. "
                " It exists to ease migration from 0.13's"
                " keep=True, which meant what JOINED means; going"
                " forward, use keep=True and join each 2-tuple.",
                DeprecationWarning, stacklevel=2)
        else:
            if keep == AS_PAIRS:
                warnings.warn(
                    "multisplit's keep=AS_PAIRS is deprecated, and will be"
                    " removed no sooner than August 2027. "
                    " It's now spelled keep=True.",
                    DeprecationWarning, stacklevel=2)
            keep = AS_PAIRS

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
        s_type = bytes
    else:
        if separators_is_bytes:
            raise TypeError(f"separators must be either None or an iterable of objects the same type as s; s is {type(s).__name__}, separators is {separators!r}")
        check_separators = True
        s_type = str

    if separators is None:
        separators = bytes_whitespace if is_bytes else whitespace
        check_separators = False

    # check_separators is True if separators isn't str or bytes
    # or something we split ourselves.
    if check_separators:
        if not hasattr(separators, '__iter__'):
            raise TypeError(f"separators must be either None or an iterable of objects the same type as s; s is {type(s).__name__}, separators is {separators!r}")
        s2 = []
        for o in separators:
            if not isinstance(o, s_type):
                raise TypeError(f"separators must be either None or an iterable of objects the same type as s; s is {type(s).__name__}, separators is {separators!r}")
            if not o:
                raise TypeError(f"separators cannot contain an empty str/bytes object")
            s2.append(o)
        separators = tuple(s2)

    # separators can't be None here--None was replaced with the
    # default separators above--so we only need the emptiness check.
    if not separators:
        raise ValueError(f"separators must be either None or an iterable of objects the same type as s; s is {type(s).__name__}, separators is {separators!r}")

    if maxsplit is not None:
        maxsplit = operator.index(maxsplit)

    internally_keep_separators = keep

    if strip:
        if strip == PROGRESSIVE:
            if (maxsplit is None) or (maxsplit == -1):
                strip = left = right = True
            else:
                left = not reverse
                right = reverse
                internally_keep_separators = True
        else:
            left = strip != RIGHT
            right = strip != LEFT
        s = multistrip(s, separators, left=left, right=right)
        if not s:
            # oops! all separators!
            # this will make us exit the iterator early.
            maxsplit = 0

    return _multisplit(s, separators, keep, maxsplit, reverse, separate, strip, is_bytes, internally_keep_separators)


@export
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

        >>> multipartition('aXbYz', ('X', 'Y'))
        ('a', 'X', 'bYz')

    If none of the separators are found in the string, returns
    a tuple containing `s` unchanged followed by two empty strings.

    Returns a tuple of slices of s—including zero-length boundary
    slices when needed—so concatenating the returned values
    reconstitutes the original s.

    multipartition is *greedy*: if two or more separators appear at
    the leftmost location in `s`, multipartition partitions using
    the longest matching separator.  For example:

        >>> multipartition('wxabcyz', ('a', 'abc'))
        ('wx', 'abc', 'yz')

    Passing in an explicit "count" lets you control how many times
    multipartition partitions the string.  multipartition will always
    return a tuple containing (2*count)+1 elements.  Passing in a
    count of 0 will always return a tuple containing s.

    If `separate` is false, multiple adjacent separator strings get joined
    together, behaving like one big separator.  If `separate` is true,
    they're kept separate.  Example:

        >>> multipartition('aXYbYXc', ('X', 'Y',), count=2, separate=False)
        ('a', 'XY', 'b', 'YX', 'c')
        >>> multipartition('aXYbYXc', ('X', 'Y',), count=4, separate=True )
        ('a', 'X', '', 'Y', 'b', 'Y', '', 'X', 'c')
        >>> multipartition('aXYbYXc', ('X', 'Y',), count=2, separate=True )
        ('a', 'X', '', 'Y', 'bYXc')

    If reverse is true, multipartition behaves like str.rpartition.
    It partitions starting on the right, scanning backwards through
    s looking for separators.

    You can pass in an instance of a subclass of bytes or str
    for s and elements of separators, but the base class
    for both must be the same (str or bytes).
    """
    count = operator.index(count)
    if count < 0:
        raise ValueError("count must be positive")
    # flatten the keep=True 2-tuples into the alternating form
    # this function is built on, then drop the always-empty
    # trailing separator.
    result = []
    for segment_and_separator in multisplit(s, separators,
        keep=True,
        reverse=reverse,
        separate=separate,
        strip=False,
        maxsplit=count):
        result.extend(segment_and_separator)
    result.pop()
    desired_length = (2 * count) + 1
    result_length = len(result)
    if result_length < desired_length:
        if reverse:
            empty = (s[0:0],)
        else:
            empty = (s[-1:-1],)
        extension = empty * (desired_length - result_length)
        if reverse:
            result = list(extension) + result
        else:
            result.extend(extension)
    return tuple(result)

@export
def multirpartition(s, separators, count=1, *, reverse=False, separate=True):
    "Like big.multipartition, but partitions from the right by default, like str.rpartition."
    return multipartition(s, separators, count=count, reverse=not reverse, separate=separate)

@export
def multireplace(s, replacements, count=-1, *, reverse=False):
    """
    Like str.replace, but supports multiple replacement strings,
    and replaces them all in a single pass.

    s can be str or bytes.

    replacements should be a mapping (e.g. a dict) mapping
    old strings to the new strings replacing them.  Every key
    and every value must be the same type as s, keys cannot
    be empty, and replacements cannot itself be empty.

    Returns a copy of s with every occurrence of every key
    replaced by that key's value.  multireplace makes only one
    pass over s: text that has already been replaced is never
    itself examined for further replacements.  For example:

        big.multireplace('ab', {'a': 'b', 'b': 'a'})

    returns 'ba'.  (Calling str.replace repeatedly gets this
    wrong: 'ab'.replace('a', 'b').replace('b', 'a') returns
    'aa', because the second replace re-replaces the output
    of the first.)

    multireplace is "greedy": if two or more keys match at the
    same location in s, multireplace replaces using the longest
    matching key.  For example:

        big.multireplace('a category', {'cat': 'dog', 'category': 'taxonomy'})

    returns 'a taxonomy', not 'a dogegory'.

    "count" should be either an integer or None.  If count is an
    integer greater than -1, multireplace will replace no more
    than count times, like the "count" parameter to str.replace.

    "reverse" controls the direction multireplace scans in.
    It supports two values:
        false (the default)
            Scan starting from the beginning of the string,
            moving right.
        true
            Scan starting from the end of the string,
            moving left.
    Scanning from the end of the string has two effects.  First,
    if count is a number greater than 0, the replacements start
    at the end of the string rather than the beginning.  Second,
    if there are overlapping instances of keys in the string,
    multireplace will prefer the rightmost key rather than the
    leftmost.  For example:

        big.multireplace('xa0bx', {'a0': 'A', '0b': 'B'})

    returns 'xAbx', whereas

        big.multireplace('xa0bx', {'a0': 'A', '0b': 'B'}, reverse=True)

    returns 'xaBx'.

    You can pass in instances of subclasses of bytes or str
    for s and the keys and values of replacements, but the
    base class for all of them must be the same (str or bytes).

    multireplace supports big.string: if s is a big.string
    object, the result is reassembled with big.string.cat,
    so it's a big.string too, and every unchanged segment
    still knows its original file, line, and column.
    """
    if not hasattr(replacements, 'items'):
        raise TypeError(f"replacements must be a mapping of keys and values the same type as s; s is {type(s).__name__}, replacements is {replacements!r}")

    if isinstance(s, bytes):
        s_type = bytes
        empty = b''
    else:
        s_type = str
        empty = ''

    keys = []
    for key, value in replacements.items():
        if not (isinstance(key, s_type) and isinstance(value, s_type)):
            raise TypeError(f"replacements must be a mapping of keys and values the same type as s; s is {type(s).__name__}, replacements contains {key!r}: {value!r}")
        if not key:
            raise ValueError("replacements keys cannot be empty")
        keys.append(key)
    if not keys:
        raise ValueError(f"replacements cannot be empty")

    # multisplit hands us (segment, separator) 2-tuples, always
    # in left-to-right order, even when reverse is true.  every
    # non-empty separator is an exact match for one of our keys;
    # map it through replacements and reassemble.  greediness,
    # count, reverse, and the str/bytes discipline all come
    # from multisplit.
    result = []
    for segment, separator in multisplit(s, tuple(keys),
        keep=True,
        maxsplit=count,
        reverse=reverse,
        separate=True,
        strip=False):
        result.append(segment)
        if separator:
            result.append(replacements[separator])

    big_types = sys.modules.get('big.types')
    if (big_types is not None) and isinstance(s, big_types.string):
        return type(s).cat(*result)

    return empty.join(result)

@export
def format_map(s, mapping):
    """
    An implementation of str.format_map supporting nested replacements.

    Unlike str.format_map, big.format_map allows you to perform string
    replacements inside of other string replacements:

        big.format_map("{{extension} size}",
            {'extension': 'mp3', 'mp3 size': 8555})

    returns the string '8555'.

    Another difference between str.format_map and big's format_map
    is how you escape curly braces.  To produce a '{' or '}' in the
    output string, add '\\{' or '\\}' respectively.  (To produce a
    backslash, '\\', you must put *four* backslashes, '\\\\'.)

    See the documentation for str.format_map for more.
    """
    if '{' not in s:
        return s.replace("\\\\", "\\")
    stack = []
    words = []
    append = words.append
    pop = words.pop
    empty_join = ''.join
    saw_backslash = False

    for s, delimiter in multisplit(s, '{}\\', separate=True, keep=True):
        append(s)
        if not delimiter:
            continue
        if delimiter == '{':
            if saw_backslash:
                saw_backslash = False
                if not s:
                    append('{')
                    continue
                _ = pop()
                append('\\')
                append(_)
            stack.append((words, append, pop))
            words = []
            append = words.append
            pop = words.pop
        elif delimiter == '}':
            if saw_backslash:
                saw_backslash = False
                if not s:
                    append('}')
                    continue
                _ = pop()
                append('\\')
                append(_)
            e = empty_join(words)
            expression = f'{{{e}}}'
            value = expression.format_map(mapping)
            words, append, pop = stack.pop()
            append(value)
        else:
            # delimiter == \\
            if saw_backslash:
                if not s:
                    append('\\')
                    saw_backslash = False
                else:
                    words.pop()
                    append('\\')
                    append(s)
                    # saw_backslash = True
            else:
                saw_backslash = True

    return ''.join(words)



# I declare that, for our purposes,
#     `
# (the "back-tick" character, U+0060)
# is *not* an apostrophe.  it's a diacritical
# used to modify a letter, rather than a
# separator used to separate letters.
# It's been (ab)used as an apostrophe historically,
# but that's because ASCII had a limited number of
# punctuation characters.
#
# ("our purposes" are specifically gently_title.)
# --8<-- start big apostrophes and double quotes --8<--
# --8<-- requires big license --8<--

apostrophes = unicode_apostrophes = "'‘’‚‛"
double_quotes = unicode_double_quotes = '"“”„‟«»‹›'

ascii_apostrophes = b"'"
ascii_double_quotes = b'"'

# --8<-- end big apostrophes and double quotes --8<--

export('apostrophes')
export('double_quotes')
export('ascii_apostrophes')
export('ascii_double_quotes')

utf8_apostrophes = apostrophes.encode('utf-8')
export('utf8_apostrophes')
utf8_double_quotes = double_quotes.encode('utf-8')
export('utf8_double_quotes')




@export
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
    i = enumerate(i)

    for offset, c in i:
        break
    assert c

    word_start = 0
    multiple_uppers = False

    while True:
        if c.islower():
            for offset, c in i:
                if c.isupper():
                    yield s[word_start:offset]
                    word_start = offset
                    break
                if c.islower():
                    continue
                break
            else:
                break

        elif c.isupper():
            multiple_uppers = False
            for offset, c in i:
                if c.isupper():
                    multiple_uppers = split_allcaps
                    continue
                if c.islower():
                    if multiple_uppers:
                        offset -= 1
                        yield s[word_start:offset]
                        word_start = offset
                break
            else:
                break
        else:
            for offset, c in i:
                break
            else:
                break

    # careful: offset is the index of the last character enumerate
    # yielded, not one past it--comparing word_start against offset
    # here used to silently drop a single-character final word.
    if word_start < len(s):
        yield s[word_start:]


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

@export
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
    method to split; use big's multisplit with keep=True, and
    flatten the 2-tuples it yields.)
    """
    # Convert every entry in split_arrays to a list.
    # Measure the strings in the split arrays, ignoring empty splits.
    split_lengths = [ [ len(_) for _ in split  if _ ] for split in split_arrays ]

    # Throw away empty entries in split arrays.  (If one array was ['', '', ''], it would now be empty.)
    split_lengths = [ split  for split in split_lengths  if split ]

    heapq.heapify(split_lengths)

    return _combine_splits(s, split_lengths)


# --8<-- start big gently_title --8<--
# --8<-- requires big license --8<--
# --8<-- requires big apostrophes and double quotes --8<--
# --8<-- requires big _iterate_over_bytes --8<--

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
            D'Artagnan

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
        big.text.ascii_double_quotes, which is the string b'"'.
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

    result = empty.join(result)
    if result == s:
        return s
    return result

# --8<-- end big gently_title --8<--

export('gently_title')


@export
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
        return s

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
    else:
        words = list(multisplit(s, separators, keep=False, separate=False, strip=False, reverse=False, maxsplit=-1))
        cleaned = replacement.join(words)
        del words
    if s == cleaned:
        return s
    return cleaned



##
## A short treatise on detecting linebreaks.
##
## What's the fastest way to detect if a string contains linebreaks?
##
## I experimented with several approaches, including re.compile(linebreaks-separated-by-|).search
## and brute-force checking with s.find.  These are fast, but there's something even faster.
##
## Before I answer, let me back up a little.  In big, I want to detect if a string contains
## linebreaks in several places--and in every one of these places, I raise an exception if the
## string contains linebreaks.  This means that, if the string contains linebreaks, performance
## is now out the window; we're gonna raise an exception, processing is over, etc etc etc.
## Therefore, the only scenario that's relevant to performance is when the string *doesn't*
## contain linebreaks.  And what's the fastest way to confirm that a string contains no linebreaks?
##         contains_linebreaks = len( s.splitlines() ) > 1
## In the case that s doesn't contain any linebreaks, this allocates a list, then examines every
## character in s to see if it's a linebreak.  Once it reaches the end of the list, nope, no linebreak
## characters detected, so it adds a reference to s to its list and returns the list.  All that
## work is done in C.  The only extraneous bit is the list, but that's not really a big deal.
##
## In the case where s does contain linebreaks, this is going to allocate N strings, where the sum
## of their lengths is the same as len(s), etc etc.  That's slow.  But we only do that when we're
## gonna throw an exception anyway.
##
## One added benefit of this approach: it works on both str and bytes objects, you don't need to
## handle them separately.
##
## Update: OOOOPS! s.splitlines() implicitly does an s.rstrip(linebreak-characters) before splitting!
## Hooray for special cases breaking the rules!
##
## So now I have to do this more complicated version:
##         contains_linebreaks = (len( s.splitlines() ) > 1) or (len( ( s[-1:] + 'x' ').splitlines() ) > 1)
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
    text = s[0:0]

    quote = state
    for pair in multisplit(s, separators, keep=True, separate=True):
        literal, separator = pair

        if literal:
            if text:
                text += literal
            else:
                text = literal
        if not quote:
            # not currently quoted
            if separator not in all_quotes_set:
                if text:
                    text += separator
                else:
                    text = separator
                continue
            if text:
                length = len(text)
                leading_empty = text[0:0]
                trailing_empty = text[length:length]
                yield (leading_empty, text, trailing_empty)
                text = trailing_empty
            quote = separator
            continue
        # in quote
        if separator != quote:
            if text:
                text += separator
            else:
                text = separator
            continue
        # separator == quote
        # (and quote is always truthy here--if it were false,
        # the "not currently quoted" branch above would have
        # handled this separator.)
        if text and (quote not in multiline_quotes):
            # see treatise above
            if (len(text.splitlines()) > 1) or (len( (text[-1:] + laden).splitlines()) > 1):
                raise SyntaxError(f"unterminated quoted string, {s!r}")
        if state:
            state = None
            yield (text[0:0], text, separator)
        else:
            yield (quote, text, separator)
        length = len(text)
        text = text[length:length]
        quote = text

    if text or quote:
        if quote and text and (quote not in multiline_quotes):
            # see treatise above
            if (len(text.splitlines()) > 1) or (len( (text[-1:] + laden).splitlines()) > 1):
                raise SyntaxError(f"unterminated quoted string, {s!r}")
        if state:
            # state = None
            quote = text[0:0]
        length = len(text)
        yield (quote, text, text[length:length])

_split_quoted_strings = split_quoted_strings


@export
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
    to (b'"', b"'").)  If a linebreak character appears inside a
    quoted string, split_quoted_strings will raise SyntaxError.

    multiline_quotes is like quotes, except quoted strings
    using multiline quotes are permitted to contain linebreaks.
    By default split_quoted_strings doesn't define any
    multiline quote marks.

    escape is a string of any length.  If escape is not
    an empty string, the string will "escape" (quote)
    quote delimiters inside a quoted string, like the
    backslash ('\\') character inside strings in Python.
    By default, escape is '\\'.  (If s is bytes, escape
    defaults to b'\\'.)
    escape works inside both quotes and multiline_quotes,
    and shields exactly one following character, like
    backslash in Python.  So inside a '\"\"\"' string,
    '\\\"\"\"' is an escaped quote mark followed by two
    live quote marks--just like Python--and doesn't
    close the string.

    multiline_quotes is like quotes, except text inside
    multiline quotes is permitted to contain linebreaks.
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
    into state.  When a non-empty string is passed in
    to state, the leading_quote in the first 3-tuple
    yielded by split_quoted_strings will be an empty string.
    For example:

        list(split_quoted_strings("a b c'", state="'"))

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
        state = s[0:0]
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

    # and also all escaped quote marks--for *every* kind of quote,
    # multiline quotes included.  escape shields exactly one
    # following character, like backslash in Python, so the
    # separator we need is escape + the quote's first character.
    if escape:
        for first_character in {q[0:1] for q in all_quotes_set}:
            separators.append(escape + first_character)
        separators.append(escape + escape)

    # help multisplit work better--it memoizes the conversion to a regular expression
    separators.sort()

    return _split_quoted_strings(s, separators, all_quotes_set, quotes_set, multiline_quotes_set, empty, laden, state)


@export
class Delimiter:
    """
    Class representing a delimiter for split_delimiters.

    close is the closing delimiter, either a str or bytes string,
        or a tuple of them: alternatives, any one of which closes
        the delimiter.  (For example, a line comment can end at
        '\\n' or '\\r'.)  Every close must be the same type as open.
    quoting is a boolean: does this set of delimiters "quote" the text inside?
        When an open delimiter enables quoting, split_delimiters will ignore all
        other delimiters in the text until it encounters the matching close delimiter.
        (Single- and double-quotes set this to True.)
    escape is a string of maximum length 1: if true, when inside this pair of delimiters,
        you can escape the closing delimiter using this string.  escape can only be true
        when quoting is true, although escape may always be false (for example,
        Python's raw strings).
    multiline is a boolean: are linebreak characters permitted inside these delimiters?
        multiline may only be false when quoting is true.

    Three parameters define what the text *inside* the delimiter
    means.  They can also be assigned to as attributes, until the
    first time the Delimiter is used in a compiled grammar--after
    that the Delimiter is frozen, and you'd need to work with a
    copy.  (Assignment exists so you can construct cyclic grammars:
    build the Delimiters, then close the loop by assigning at the
    end.)

    nested is a mapping of open delimiter strings to Delimiter
        objects: delimiters that are live *inside* this delimiter.
        For a quoting delimiter, nested delimiters are the
        exceptions to the quoting--how a Python f-string, which
        quotes, still opens an {interpolation}.  For a non-quoting
        delimiter, every top-level delimiter of the grammar is
        already live inside, and nested adds to (or overrides)
        those.  (A None value is reserved for future use and
        currently rejected.)
    literal is a token, or an iterable of tokens (like close),
        that are plain text inside this delimiter, even if they'd
        otherwise collide with a meaningful token--how '{{' inside
        an f-string means a literal '{' rather than two
        interpolations.  The literal property always presents the
        tokens as a tuple.
    change is a mapping of tokens to Delimiter objects: seeing the
        token *changes* what the inside of the current delimiter
        means, without opening a nested delimiter.  The current
        delimiter continues, and its close still closes it--so a
        change target must have the same close as its host.  This
        is how the ':' inside an f-string {interpolation} switches
        the text after it into the format-spec sub-language.  The
        token is reported in the "change" field of the values
        yielded by split_delimiters.

    You may not specify backslash ('\\') as an open or close delimiter.
    """
    def __init__(self, close, *, escape='', multiline=True, quoting=False,
        nested=None, literal=(), change=None):
        # you can pass in a Delimiter instance and we'll clone it
        if isinstance(close, Delimiter):
            d = close
            self._close = d._close
            self._closes = d._closes
            self._escape = d._escape
            self._quoting = d._quoting
            self._multiline = d._multiline
            self._nested = dict(d._nested)
            self._literal = d._literal
            self._change = dict(d._change)
            # a copy is always unfrozen--that's the escape hatch
            # for modifying a delimiter after it's been compiled.
            self._frozen = False
            return

        # close may be a single string, or an iterable of
        # alternatives.  normalize to a tuple.
        if isinstance(close, (str, bytes)):
            closes = (close,)
        else:
            try:
                closes = tuple(close)
            except TypeError:
                raise TypeError(f"close must be str, bytes, or an iterable of str or bytes, not {close!r}")
            if not closes:
                raise ValueError("close must contain at least one delimiter")
            if len(set(closes)) != len(closes):
                raise ValueError("close contains a repeated delimiter")

        is_bytes = isinstance(closes[0], bytes)
        if is_bytes:
            s_type = bytes
            empty = b''
            backslash = b'\\'
        else:
            s_type = str
            empty = ''
            backslash = '\\'

        for c in closes:
            if not isinstance(c, s_type):
                raise TypeError(f"close delimiters must all be the same type (str or bytes), not {c!r}")
            if not c:
                raise ValueError("close delimiter must not be an empty string")
            if c == backslash:
                raise ValueError(f"close delimiter must not be {backslash!r}")

        # they can't both be false, and they can't both be true
        # if bool(escape) != bool(quoting):
        #     raise ValueError("quoting and escape mismatch; they must either both be true, or both be false")
        if bool(escape) and not bool(quoting):
            raise ValueError("quoting and escape mismatch; if escape is true, quoting must be true")

        # if quoting=False, you can only have multiline=True
        if not (quoting or multiline):
            raise ValueError(f"multiline=False unsupported when quoting=False")

        self._close = close
        self._closes = closes
        self._escape = escape or empty
        self._quoting = quoting
        self._multiline = multiline

        self._frozen = False
        self._nested = {}
        self._literal = ()
        self._change = {}
        # route through the setters, so construction and
        # assignment validate identically
        if nested is not None:
            self.nested = nested
        if literal:
            self.literal = literal
        if change is not None:
            self.change = change

    def _s_type(self):
        return bytes if isinstance(self._closes[0], bytes) else str

    def _check_unfrozen(self):
        if self._frozen:
            raise ValueError("this Delimiter has been used in a compiled grammar and can no longer be modified; modify a copy() instead")

    def _check_token(self, token, description):
        if not isinstance(token, self._s_type()):
            raise TypeError(f"{description} must be the same type as close ({self._s_type().__name__}), not {token!r}")
        if not token:
            raise ValueError(f"{description} must not be an empty string")

    @property
    def close(self):
        return self._close

    @property
    def closes(self):
        "All the delimiter's close alternatives, as a tuple, even if close was a single string."
        return self._closes

    @property
    def escape(self):
        return self._escape

    @property
    def quoting(self):
        return self._quoting

    @property
    def multiline(self):
        return self._multiline

    @property
    def nested(self):
        return types.MappingProxyType(self._nested)

    @nested.setter
    def nested(self, value):
        self._check_unfrozen()
        if value is None:
            value = {}
        value = dict(value)
        for open, delimiter in value.items():
            self._check_token(open, "nested open delimiters")
            if delimiter is None:
                raise ValueError(f"nested value for {open!r} is None; None values are reserved for future use")
            if not isinstance(delimiter, Delimiter):
                raise TypeError(f"nested values must be Delimiter objects, not {delimiter!r}")
            if open in self._closes:
                raise ValueError(f"nested open delimiter {open!r} is also a close delimiter of this Delimiter")
        self._nested = value

    @property
    def literal(self):
        return self._literal

    @literal.setter
    def literal(self, value):
        self._check_unfrozen()
        # like close: either a single token, or an iterable of them.
        if isinstance(value, (str, bytes)):
            value = (value,)
        else:
            value = tuple(value)
            if len(set(value)) != len(value):
                raise ValueError("literal contains a repeated token")
        for token in value:
            self._check_token(token, "literal tokens")
            if token in self._closes:
                raise ValueError(f"literal token {token!r} is also a close delimiter of this Delimiter")
            if token == self._escape:
                raise ValueError(f"literal token {token!r} is also the escape string of this Delimiter")
        self._literal = value

    @property
    def change(self):
        return types.MappingProxyType(self._change)

    @change.setter
    def change(self, value):
        self._check_unfrozen()
        if value is None:
            value = {}
        value = dict(value)
        for token, delimiter in value.items():
            self._check_token(token, "change tokens")
            if not isinstance(delimiter, Delimiter):
                raise TypeError(f"change values must be Delimiter objects, not {delimiter!r}")
            if delimiter._closes != self._closes:
                raise ValueError(f"change target for {token!r} must have the same close as this Delimiter; {delimiter._closes!r} != {self._closes!r}")
            if token in self._closes:
                raise ValueError(f"change token {token!r} is also a close delimiter of this Delimiter")
        self._change = value

    def __repr__(self): # pragma: no cover
        # nested and change can contain reference cycles,
        # so render just their keys.
        s = f"Delimiter(close={self._close!r}, escape={self._escape!r}, multiline={self._multiline!r}, quoting={self._quoting!r}"
        if self._nested:
            s += f", nested=<{{{', '.join(repr(k) for k in self._nested)}}}>"
        if self._literal:
            s += f", literal={self._literal!r}"
        if self._change:
            s += f", change=<{{{', '.join(repr(k) for k in self._change)}}}>"
        return s + ")"

    def __eq__(self, other):
        return self._eq(other, set())

    def _eq(self, other, memo):
        if self is other:
            return True
        if not isinstance(other, Delimiter):
            return NotImplemented
        # nested and change can contain reference cycles.
        # memo remembers the pairs we're already comparing;
        # if we meet a pair again on a back-edge, assume equal
        # (if they differ, some *other* field along the cycle
        # differs, and that comparison returns the False).
        key = (id(self), id(other))
        if key in memo:
            return True
        memo.add(key)
        if not ((self._closes  == other._closes)
            and (self._escape  == other._escape)
            and (self._quoting == other._quoting)
            and (self._multiline == other._multiline)
            and (self._literal == other._literal)
            and (set(self._nested) == set(other._nested))
            and (set(self._change) == set(other._change))):
            return False
        for open, delimiter in self._nested.items():
            if delimiter._eq(other._nested[open], memo) is not True:
                return False
        for token, delimiter in self._change.items():
            if delimiter._eq(other._change[token], memo) is not True:
                return False
        return True

    def __hash__(self):
        # only hash the flat fields.  nested and change can
        # contain reference cycles, which an ordinary recursive
        # hash would never escape.  (perfectly legal: objects
        # that compare equal still hash equal, because deep
        # equality implies flat equality.)
        return hash("Delimiter") ^ hash(self._closes) ^ hash(self._escape) ^ hash(self._quoting) ^ hash(self._multiline) ^ hash(self._literal)

    def copy(self):
        return Delimiter(self)


delimiter_parentheses = Delimiter(")")
export('delimiter_parentheses')

delimiter_square_brackets = Delimiter("]")
export('delimiter_square_brackets')

delimiter_curly_braces = Delimiter("}")
export('delimiter_curly_braces')

delimiter_angle_brackets = Delimiter(">")
export('delimiter_angle_brackets')

delimiter_single_quote = Delimiter("'", escape='\\', multiline=False, quoting=True)
export('delimiter_single_quote')

delimiter_double_quotes = Delimiter('"', escape='\\', multiline=False, quoting=True)
export('delimiter_double_quotes')

split_delimiters_default_delimiters = {
    '(': delimiter_parentheses,
    '[': delimiter_square_brackets,
    '{': delimiter_curly_braces,
    "'": delimiter_single_quote,
    '"': delimiter_double_quotes,
    }
export('split_delimiters_default_delimiters')


split_delimiters_default_delimiters_bytes = {
    b'(': Delimiter(b')'),
    b'[': Delimiter(b']'),
    b'{': Delimiter(b'}'),
    b"'": Delimiter(b"'", escape=b'\\', multiline=False, quoting=True),
    b'"': Delimiter(b'"', escape=b'\\', multiline=False, quoting=True),
    }
export('split_delimiters_default_delimiters_bytes')

_ACTION_POP = "<action: pop>"
# _ACTION_2POP = "<action: pop twice>"
_ACTION_ESCAPE = "<action: escape>"
_ACTION_ILLEGAL = "<action: illegal>"
_ACTION_ILLEGAL_LINEBREAK = "<action: illegal linebreak>"
_ACTION_FLUSH = "<action: flush>"
_ACTION_FLUSH_1_AND_RESPLIT = "<action: flush 1 and resplit>"
_ACTION_PROCESS_1_AND_RESPLIT = "<action: process 1 and resplit>"

class _ACTION_TRUNCATE_TO_S_AND_RESPLIT:
    pass

class _ACTION_TRUNCATE_TO_S_AND_RESPLIT_STR(str, _ACTION_TRUNCATE_TO_S_AND_RESPLIT):
    def __repr__(self): # pragma: nocover
        return f"_ACTION_TRUNCATE_TO_S_AND_RESPLIT({str(self)!r})"

class _ACTION_TRUNCATE_TO_S_AND_RESPLIT_BYTES(bytes, _ACTION_TRUNCATE_TO_S_AND_RESPLIT):
    def __repr__(self): # pragma: nocover
        return f"_ACTION_TRUNCATE_TO_S_AND_RESPLIT({bytes(self)!r})"

class _ACTION_CHANGE_STATE:
    # switch the current state to self.state, *without* pushing.
    # this is how a Delimiter's "change" tokens are implemented:
    # the current delimiter continues (its close still pops),
    # but the text inside now means something different.
    __slots__ = ('state',)
    def __init__(self, state):
        self.state = state
    def __repr__(self): # pragma: nocover
        return f"_ACTION_CHANGE_STATE(<state with {len(self.state)} tokens>)"


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

    Because the compiler is memoized (using functools.lru_cache)
    you must convert delimiters from a dict into a tuple of
    2-tuples.  (dicts aren't hashable.)  Instead of passing
    in "delimiters", pass in:

         tuple(delimiters.items())

    The state is consumed by the split_delimiters generator, below.
    See that for details.
    """
    result = _compile_delimiters(delimiters, is_bytes)

    # freeze every Delimiter in the grammar--and do it *here*,
    # outside the memoized compiler.  the compiler memoizes by
    # *equality*, so compiling a grammar deep-equal to an earlier
    # one is a cache hit and the compiler body never runs--but
    # these particular Delimiter objects are compiled now too,
    # and mutating one couldn't change the cached states, it
    # could only lie about them.
    seen = set()
    worklist = [delimiter for open, delimiter in delimiters]
    while worklist:
        delimiter = worklist.pop()
        if id(delimiter) in seen:
            continue
        seen.add(id(delimiter))
        delimiter._frozen = True
        worklist.extend(delimiter.nested.values())
        worklist.extend(delimiter.change.values())

    return result


@functools.lru_cache(maxsize=None)
def _compile_delimiters(delimiters, is_bytes):
    # the memoized compiler core.  always call it through
    # _delimiters_to_state_and_tokens, which also freezes the
    # grammar's Delimiters--even on a cache hit.
    delimiters = list(delimiters)

    if is_bytes:
        s_type = bytes
        s_type_description = "bytes"
        not_s_type_description = "str"
        linebreaks = bytes_linebreaks_without_crlf
        iterate_over_delimiter = _iterate_over_bytes
    else:
        s_type = str
        s_type_description = "str"
        not_s_type_description = "bytes"
        linebreaks = str_linebreaks_without_crlf
        iterate_over_delimiter = iter

    all_closers = set()
    all_openers = set()
    all_escapes = set()
    all_literal_tokens = set()
    all_change_tokens = set()
    nested_closers = set()
    all_linebreaks = set(linebreaks)

    # discover every Delimiter reachable from the top level: the
    # grammar's own values, plus everything reachable through
    # nested and change, recursively.  each distinct *object*
    # (by identity) compiles to one state--which is also what
    # makes reference cycles fine.
    all_delimiters = []
    seen_delimiters = set()
    worklist = [delimiter for open, delimiter in delimiters]
    while worklist:
        delimiter = worklist.pop()
        if id(delimiter) in seen_delimiters:
            continue
        seen_delimiters.add(id(delimiter))
        if not isinstance(delimiter, Delimiter):
            raise TypeError(f"delimiter values must be Delimiter objects, not {delimiter!r}")
        all_delimiters.append(delimiter)
        worklist.extend(delimiter.nested.values())
        worklist.extend(delimiter.change.values())

    for open, delimiter in delimiters:
        if not isinstance(open, s_type):
            raise TypeError(f"open delimiter {open!r} must be {s_type_description}, not {not_s_type_description}")
        all_openers.add(open)

    for delimiter in all_delimiters:
        for close in delimiter.closes:
            if not isinstance(close, s_type):
                raise TypeError(f"close delimiter {close!r} must be {s_type_description}, not {not_s_type_description}")
        if not isinstance(delimiter.escape, s_type):
            raise TypeError(f"Delimiter: escape {delimiter.escape!r} must be {s_type_description}, not {not_s_type_description}")
        # no type checks needed for nested keys, literal tokens,
        # or change tokens: the Delimiter setters guarantee they
        # match that delimiter's own closes--so checking closes
        # against the grammar (above) covers everything.
        all_openers.update(delimiter.nested)

        all_closers.update(delimiter.closes)
        all_literal_tokens.update(delimiter.literal)
        all_change_tokens.update(delimiter.change)
        if delimiter.quoting:
            if delimiter.escape:
                all_escapes.add(delimiter.escape)
        else:
            assert not delimiter.escape
            nested_closers.update(delimiter.closes)

    in_both_openers_and_closers = all_openers & nested_closers
    if in_both_openers_and_closers:
        in_both_openers_and_closers = list(in_both_openers_and_closers)
        if len(in_both_openers_and_closers) == 1:
            in_both_openers_and_closers = in_both_openers_and_closers[0]
            prefix = ''
        else:
            prefix = 'these characters '
        raise ValueError(f"{prefix}{in_both_openers_and_closers!r} cannot be both an opening and closing delimiter")

    all_delimiter_tokens = all_openers | all_closers
    all_tokens = all_delimiter_tokens | all_escapes | all_literal_tokens | all_change_tokens | all_linebreaks

    # all the non-quoting states reuse the same open dictionary.
    # initial_state = _DelimiterState(open={}, close=None, illegal=all_closers, single_line_only=False)

    delimiters_that_push_a_new_state = {}

    # "non_quoting_state_with_default_actions" is a base used for
    # states representing a non-quoting delimiter, where all the
    # usual state transitions happen.
    non_quoting_state_with_default_actions = {token: _ACTION_ILLEGAL for token in all_delimiter_tokens }
    make_linebreaks_illegal = {c: _ACTION_ILLEGAL_LINEBREAK for c in linebreaks}
    ignore_linebreaks = {c: _ACTION_FLUSH for c in linebreaks}

    # list of states that want all the default openers after processing
    states_to_update_with_all_delimiters_that_push = []

    # the initial state contains all the open delimiters,
    # isn't quoting, allows multiline, and doesn't have
    # a close delimiter or an escape string.
    initial_state = non_quoting_state_with_default_actions.copy()
    initial_state.update(ignore_linebreaks)
    states_to_update_with_all_delimiters_that_push.append(initial_state)

    # for every state, representing a delimiter d:
    #
    # multisplit tokenizes the entire text using *every* token in
    # the grammar, but any individual state only cares about *some*
    # of those tokens.  a "foreign" token--one with no meaningful
    # action in this state--can still collide with tokens this
    # state cares about, two ways:
    #
    # 1. the foreign token can *start with* a meaningful token.
    #
    #    e.g. imagine d.open = '(', d.close =')', and d.quoting = False
    #    and another state has delimiters '[(' and ')]'
    #    if we parse
    #            x[foo( a b c )])
    #    multisplit will      ^^ split here
    #    but we want to split ^ here.
    #
    #    the fix: react as if we'd received the meaningful token
    #    instead, then "resplit" (re-run multisplit) starting after
    #    it.  this is handled uniformly, for every state and every
    #    meaningful token--close, escape, or open--by
    #    _resolve_foreign_tokens, below.  (it used to be handled
    #    here, but only for d.close and d.escape; a foreign token
    #    starting with a valid *open* delimiter raised SyntaxError.)
    #
    # 2. in quoting states only: a meaningful token might be
    #    *buried inside* an otherwise flushed foreign token.
    #
    #        e.g. imagine d.open = d.close ='"', and d.quoting = True
    #        and another state has delimiters '<"<' '>">'
    #        if we parse
    #              a b c " d e f <"<"< goo goo >">
    #        multisplit will     ^^^ split here
    #        but we should flush ^ this
    #                        and  ^ handle this.
    #
    #    the fix: snip off the first character, flush it, then
    #    resplit starting after that first character.
    #
    # if the same foreign token qualifies for both, rule 1 (startswith)
    # takes priority:
    #
    #       e.g. imagine d.open = '(', d.close=')', d.escape = '[', d.quoting=True
    #       and another state has delimiters '([' '])'
    #       for state d, we want '])' to map to "TRUNCATE TO ]", not "FLUSH 1 AND RESPLIT"
    #
    # (that priority is enforced by ordering: rule 2 is assigned here,
    # and _resolve_foreign_tokens overwrites it with rule 1 afterward.)

    state_for_delimiter = {}

    for delimiter in all_delimiters:
        if delimiter.quoting:
            state = {}
            all_delimiter_characters = set()
            for close in delimiter.closes:
                all_delimiter_characters |= set(iterate_over_delimiter(close))
            if delimiter.escape:
                all_delimiter_characters |= set(iterate_over_delimiter(delimiter.escape))

            for t in all_tokens:
                t_characters = set(iterate_over_delimiter(t))
                if t_characters & all_delimiter_characters:
                    state[t] = _ACTION_FLUSH_1_AND_RESPLIT
        else:
            # non-quoting delimiter
            state = non_quoting_state_with_default_actions.copy()
            states_to_update_with_all_delimiters_that_push.append(state)

        if delimiter.quoting and (not delimiter.multiline):
            state.update(make_linebreaks_illegal)
        else:
            state.update(ignore_linebreaks)

        for close in delimiter.closes:
            state[close] = _ACTION_POP

        if delimiter.escape:
            state[delimiter.escape] = _ACTION_ESCAPE

        state_for_delimiter[id(delimiter)] = state

    for open, delimiter in delimiters:
        assert open not in delimiters_that_push_a_new_state
        delimiters_that_push_a_new_state[open] = state_for_delimiter[id(delimiter)]

    for state in states_to_update_with_all_delimiters_that_push:
        state.update(delimiters_that_push_a_new_state)

    # wire in nested, literal, and change--*after* the top-level
    # update, so a delimiter's own declarations override the
    # grammar-wide defaults.
    for delimiter in all_delimiters:
        state = state_for_delimiter[id(delimiter)]
        for open, nested_delimiter in delimiter.nested.items():
            state[open] = state_for_delimiter[id(nested_delimiter)]
        for token in delimiter.literal:
            state[token] = _ACTION_FLUSH
        for token, change_delimiter in delimiter.change.items():
            state[token] = _ACTION_CHANGE_STATE(state_for_delimiter[id(change_delimiter)])

    _resolve_foreign_tokens(initial_state, all_tokens, is_bytes)

    return initial_state, all_tokens


def _resolve_foreign_tokens(initial_state, all_tokens, is_bytes):
    """
    Walks every state reachable from initial_state and resolves
    "foreign" token collisions: a token with no meaningful action
    in some state, which *starts with* a token that does have a
    meaningful action there.  multisplit tokenizes greedily using
    every token in the grammar, so without this fixup the longer
    foreign token would swallow the meaningful one.

    For each such token, in each such state, installs a
    "truncate and resplit" action: react as if we'd received the
    meaningful prefix token instead, then re-run multisplit
    starting after it.  When several meaningful tokens are
    prefixes of the same foreign token, the longest one wins.

    "Meaningful" means the prefix token opens a delimiter, closes
    this one, escapes, changes state, or is explicitly illegal
    here--anything but flushed text.  (Truncating to an illegal
    token matters too: inside '(', the input '}}' should produce
    the same SyntaxError a bare '}' does, not silently flush.)
    A token with its own meaning in a state is never rewritten
    (if 'x' and 'xy' both open delimiters, 'xy' really is 'xy'),
    and neither is a token explicitly declared literal
    (an f-string's '{{').

    This runs as the last step of compiling a grammar.
    """
    if is_bytes:
        truncate_to_s_type = _ACTION_TRUNCATE_TO_S_AND_RESPLIT_BYTES
    else:
        truncate_to_s_type = _ACTION_TRUNCATE_TO_S_AND_RESPLIT_STR

    # map each multi-character token to its proper prefixes
    # that are also tokens, longest first.
    prefixes = {}
    for t in all_tokens:
        if len(t) <= 1:
            continue
        found = [m for m in all_tokens if (m != t) and t.startswith(m)]
        if found:
            found.sort(key=len, reverse=True)
            prefixes[t] = found

    if not prefixes:
        return

    # a token is resolvable if the state doesn't map it at all
    # (the runtime default is flush), or maps it to one of these
    # fixup-able actions.  any *other* explicit mapping is a
    # declaration--including an explicit _ACTION_FLUSH, which is
    # how a state declares a token to be literal text (e.g. '{{'
    # inside an f-string)--and we must leave it alone.
    resolvable = (_ACTION_ILLEGAL, _ACTION_FLUSH_1_AND_RESPLIT)

    seen = set()
    states = [initial_state]
    while states:
        state = states.pop()
        if id(state) in seen:
            continue
        seen.add(id(state))

        for action in state.values():
            if isinstance(action, dict):
                states.append(action)
            elif isinstance(action, _ACTION_CHANGE_STATE):
                states.append(action.state)

        for t, candidates in prefixes.items():
            if (t in state) and (state[t] not in resolvable):
                continue
            for m in candidates:
                m_action = state.get(m, _ACTION_FLUSH)
                if (isinstance(m_action, (dict, _ACTION_CHANGE_STATE))
                    or (m_action is _ACTION_POP)
                    or (m_action is _ACTION_ESCAPE)
                    or (m_action is _ACTION_ILLEGAL)):
                    state[t] = truncate_to_s_type(m)
                    break


_delimiters_cache = []


"""
python_delimiters is a dict of delimiters, suitable for use with split_delimiters,
implementing *all* relevant Python delimiters.  This includes all possible string
delimiters, including all possible prefixes.

According to the Python documentation:

    https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals

Python supports four letters as prefixes for strings, in certain combinations.
Those letters are:

    b - means "bytes string"
    f - means "f-string"
    r - means "raw string"
    u - means "unicode string"

'u' was added in Python 3.2, 'f' was added in Python 3.6,
and 't' was added in Python 3.14 (PEP 750).

What combinations are valid?  There are some rules:
    * u cannot be used with any other prefix character.
    * f cannot be used with b.

Rather than work it out, the easiest way is to just ask Python.
Here's a short program that tests all possible combinations and
tells you which ones are valid:

----------------------------------------------------------------------------

alphabet = "abcdefghijklmnopqrstuvwxyz"
alphabet = alphabet + alphabet.upper()

worked1 = []
worked2 = []
worked3 = []
worked4 = []
worked5 = []

for prefix in alphabet:
    for s in (f'{prefix}"foo"', f"{prefix}'bar'"):
        try:
            eval(s)
        except SyntaxError:
            break
    else:
        worked1.append(prefix)


# could use itertools here,
# but level 3 we have to do by hand,
# so let's just do it all by hand and copy&paste
for c1 in worked1:
    for c2 in worked1:
        if c1.lower() == c2.lower():
            continue
        prefix = f'{c1}{c2}'
        for s in (f'{prefix}"foo"', f"{prefix}'bar'"):
            try:
                eval(s)
            except SyntaxError:
                break
        else:
            worked2.append(prefix)

assert worked2

for c1 in worked1:
    for c2 in worked2:
        if c1.lower() in c2.lower():
            continue
        prefix = f'{c1}{c2}'
        for s in (f'{prefix}"foo"', f"{prefix}'bar'"):
            try:
                eval(s)
            except SyntaxError:
                break
        else:
            worked3.append(prefix)

if worked3:
    for c1 in worked1:
        for c2 in worked3:
            if c1.lower() in c2.lower():
                continue
            prefix = f'{c1}{c2}'
            for s in (f'{prefix}"foo"', f"{prefix}'bar'"):
                try:
                    eval(s)
                except SyntaxError:
                    break
            else:
                worked4.append(prefix)


if worked4:
    for c1 in worked1:
        for c2 in worked4:
            if c1.lower() in c2.lower():
                continue
            prefix = f'{c1}{c2}'
            for s in (f'{prefix}"foo"', f"{prefix}'bar'"):
                try:
                    eval(s)
                except SyntaxError:
                    break
            else:
                worked5.append(prefix)

all_prefixes = ['']
all_prefixes.extend(worked1)
all_prefixes.extend(worked2)
all_prefixes.extend(worked3)
all_prefixes.extend(worked4)
all_prefixes.extend(worked5)

print(f"{all_prefixes=}")

----------------------------------------------------------------------------

The list is short, here it is, for Python 3.6 - 3.13 anyway:

prefixes = [
    '',
    'b',
    'f',
    'r',
    'u',
    'br',
    'fr',
    'rb',
    'rf',
    ]

However, Python allows you to use the upper-case version of
any letter, in any combination.  So the actual list is longer,
as you can uppercase any letter and get a new prefix.

Also, Python 3.14 adds the 't' prefix for t-strings.
Big supports all the new prefixes that adds, too.

"""

# This "workspace" is just a convenient way of creating
# a namespace we can do some work in without cluttering
# the module's namespace.  We get to use all the symbols
# we want, and when we're done we just export the symbols
# we want to keep and throw the rest away.
class Workspace:
    # string prefixes valid on every version of Python big supports.
    all_string_prefixes = [
        '',
        'b',
        'B',
        'br',
        'bR',
        'Br',
        'BR',
        'f',
        'F',
        'fr',
        'fR',
        'Fr',
        'FR',
        'r',
        'R',
        'rb',
        'rB',
        'Rb',
        'RB',
        'rf',
        'rF',
        'Rf',
        'RF',
        'u',
        'U',
        ]

    # Python 3.14 added t-strings (PEP 750), and with them these
    # prefixes.  big builds both grammar *dicts* eagerly--they're
    # small and cheap--then picks the right one for the running
    # interpreter (python_delimiters), and maps every version to
    # its own grammar (python_delimiters_version).  Compiling a
    # grammar into its state machine is the expensive part, so
    # that's deferred until the first split_delimiters call that
    # needs it; see _make_python_grammar_cache below.
    t_string_prefixes = [
        'rt',
        'rT',
        'Rt',
        'RT',
        't',
        'T',
        'tr',
        'tR',
        'Tr',
        'TR',
        ]

    assert sys.version_info.major >= 3

    # In Python "raw" strings, backslash still escapes a quote character.  This is legal:
    #     r'abc\'def'
    # So, for our purposes, the raw prefix doesn't matter.  All we care about is whether or not
    # it quotes the closing quote mark, and it does.  The same is true for triple-quoted strings;
    # even in a raw triple-quoted string, you can escape single-quote marks.

    # Python's tokenizer only recognizes '\n' and '\r' as line
    # boundaries.  The rest of big's linebreaks--vertical tab,
    # form feed, '\x85', ' ', and friends--are plain text
    # inside Python's strings and comments, as far as Python is
    # concerned.  Declaring them literal in those delimiters
    # matches Python's actual behavior, while leaving big's
    # definition of "linebreak" intact: they're still linebreaks,
    # this grammar just declares them literal text here.
    exotic_linebreaks = tuple(c for c in str_linebreaks_without_crlf if c not in ('\n', '\r'))

    # single-line strings declare the exotic linebreaks literal
    # (multiline=False would otherwise reject them, and real
    # Python doesn't); triple-quoted strings are multiline, where
    # linebreaks are already plain text.
    all_quote_delimiters = []
    for quotes in ("'", '"', "'''", '"""'):
        multiline = len(quotes) == 3
        all_quote_delimiters.append(
            Delimiter(quotes, escape='\\', multiline=multiline, quoting=True,
                literal=(() if multiline else exotic_linebreaks),
                ))

    # -- f-strings, through the front door --
    #
    # an f-string is a quoting delimiter, except '{' still opens
    # an {interpolation} inside it--and '{{' and '}}' are literal
    # text.  inside the interpolation:
    #
    #        +-- inside an f-string,
    #        |
    #        |   +-- inside curly braces,
    #        |   |
    #        |   |   +-- ':' *changes* to the format-spec
    #        |   |   |   sub-language...
    #       vv   v   v
    # print(f'foo{abc:xyz}')
    #             ^^^ ^^^
    #              |   |
    #              |   +-- ...where most delimiters are inert,
    #              |       but '{' opens a nested field.
    #              |
    #              +-- ...and before it, this is an ordinary
    #                  expression: every delimiter works.
    #
    # '!' likewise changes to the conversion field ("!r"); a ':'
    # after that changes to the format spec.  the interpolation,
    # the conversion, and the format spec are all ended by the
    # same '}', so they're "change" targets, not nested
    # delimiters.
    #
    # (technically, after '!' the only legal characters are "a",
    # "s", and "r", followed by ':' or '}'.  but we're lazy, so
    # the conversion field just acts like a quoted single-line
    # string.)
    #
    # the format spec is shared by single- and triple-quoted
    # f-strings, so it must be multiline.

    curly_braces = split_delimiters_default_delimiters['{']

    fstring_format_spec = Delimiter('}', quoting=True, escape='\\',
        nested={'{': curly_braces})

    fstring_conversion = Delimiter('}', quoting=True, escape='\\', multiline=False,
        change={':': fstring_format_spec})

    # '!=' is declared literal so the != operator survives:
    # in f'{a != b}', the '!' must not start a conversion field.
    # (multisplit tokenizes greedily, so '!=' wins over '!'.
    # real python uses the same rule: a conversion is '!' not
    # followed by '='.)
    fstring_interpolation = Delimiter('}',
        literal='!=',
        change={':': fstring_format_spec, '!': fstring_conversion})

    # (a plain loop, not a comprehension: comprehensions can't
    # see class-body names like fstring_interpolation.)
    all_fstring_quote_delimiters = []
    for quotes in ("'", '"', "'''", '"""'):
        multiline = len(quotes) == 3
        all_fstring_quote_delimiters.append(
            Delimiter(quotes, escape='\\', multiline=multiline, quoting=True,
                nested={'{': fstring_interpolation},
                literal=('{{', '}}') + (() if multiline else exotic_linebreaks),
                ))
    del quotes
    del multiline

    def build_python_delimiters(prefixes, brace_prefix_characters,
        all_quote_delimiters=all_quote_delimiters,
        all_fstring_quote_delimiters=all_fstring_quote_delimiters,
        exotic_linebreaks=exotic_linebreaks,
        ):
        python_delimiters = split_delimiters_default_delimiters.copy()

        for prefix in prefixes:
            lowered = prefix.lower()
            if any((c in lowered) for c in brace_prefix_characters):
                # f-string (or t-string, in the t-aware grammar):
                # braces are live inside.
                quote_delimiters = all_fstring_quote_delimiters
            else:
                quote_delimiters = all_quote_delimiters
            for d in quote_delimiters:
                python_delimiters[prefix + d.close] = d

        # this only works if the lines you parse include the trailing newline characters.
        # (a comment ends at '\n' or '\r', whichever comes first;
        # the exotic linebreaks are comment text, like Python says.)
        python_delimiters['#'] = Delimiter(('\n', '\r'), escape=None, multiline=False, quoting=True,
            literal=exotic_linebreaks)

        return python_delimiters

    # t-strings (3.14+) have the same brace semantics as
    # f-strings--that's the second argument.
    python_delimiters_3_6 = build_python_delimiters(all_string_prefixes, 'f')
    python_delimiters_3_14 = build_python_delimiters(all_string_prefixes + t_string_prefixes, 'ft')



python_delimiters_3_6 = Workspace.python_delimiters_3_6
python_delimiters_3_14 = Workspace.python_delimiters_3_14
del Workspace


def _make_python_grammar_cache(delimiters):
    # compiling a python grammar into its state machine costs
    # real time--several milliseconds per grammar--so we don't
    # do it at import.  this returns a zero-argument callable
    # that builds the cache on first call and returns the
    # memoized result thereafter.  (the entries for the small
    # default-delimiters grammars just wrap their prebuilt
    # caches in a lambda; see below.)
    cache = None
    def get_cache():
        nonlocal cache
        if cache is None:
            cache = _delimiters_to_state_and_tokens(tuple(delimiters.items()), False)
        return cache
    return get_cache

_delimiters_cache.append(
    (python_delimiters_3_6, _make_python_grammar_cache(python_delimiters_3_6))
    )
_delimiters_cache.append(
    (python_delimiters_3_14, _make_python_grammar_cache(python_delimiters_3_14))
    )

# python_delimiters is the grammar of the *running* interpreter.
if (sys.version_info.major, sys.version_info.minor) >= (3, 14): # pragma: nocover
    python_delimiters = python_delimiters_3_14
else: # pragma: nocover
    python_delimiters = python_delimiters_3_6

export('python_delimiters')

# python_delimiters_version maps a Python version string to the
# delimiters for *that version's* grammar, independent of the
# running interpreter.  the only grammar fork in big's supported
# range is t-strings, added in 3.14.
python_delimiters_version = { f"3.{minor}": python_delimiters_3_6 for minor in range(6, 14) }
python_delimiters_version["3.14"] = python_delimiters_3_14
export('python_delimiters_version')

@export
class SplitDelimitersValue:
    __slots__ = ['text', 'open', 'close', 'change']

    def __init__(self, text, open, close, change):
        self.text = text
        self.open = open
        self.close = close
        self.change = change

    @property
    def yields(self):
        # Deprecated.  In big 0.13, split_delimiters could yield
        # objects that iterated as either three or four values,
        # and .yields told you which.  As of 0.14 it's always four,
        # so this always returns 4.  Kept for backwards
        # compatibility; it will be removed at the same time as the
        # deprecated "yields" parameter to split_delimiters, no
        # sooner than August 2027.
        return 4

    def __repr__(self):
        return f"SplitDelimitersValue(text={self.text!r}, open={self.open!r}, close={self.close!r}, change={self.change!r})"

    def __eq__(self, other):
        return (
            isinstance(other, SplitDelimitersValue)
            and (self.text == other.text)
            and (self.open == other.open)
            and (self.close == other.close)
            and (self.change == other.change)
            )

    def __iter__(self):
        yield self.text
        yield self.open
        yield self.close
        yield self.change


def split_delimiters(text, all_tokens, current, stack, empty, str_or_bytes):
    """
    Internal generator function returned by the real split_delimiters.

    This function operates by iterating over "text" and reacting to
    tokens found in "all_tokens".  It splits text using multisplit(),
    using all_tokens as the separator list, and specifying keep=True
    so we can examine the string we split on.  We'll refer to that
    separator string as the "token" below.

    "current" is a dict mapping tokens to actions.
        * a dictionary, which indicates "push this dict"
          (entering new delimiter),
        * one of the _ACTION_* constants above, or
        * an instance of _ACTION_TRUNCATE_TO_S_AND_RESPLIT.
        * an instance of _ACTION_CHANGE_STATE, which wraps a
          state dict.

    The _ACTION_* constants above dictate:
        * _ACTION_POP means pop the current state.
        * _ACTION_2POP means pop two states.
        * _ACTION_ESCAPE means escape the next character yielded
          by multisplit.
        * _ACTION_ILLEGAL_LINEBREAK means the token is an illegal
          linebreak character.  (The current delimiter doesn't permit
          embedded linebreaks.)
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

    If the entry is an instance of _ACTION_CHANGE_STATE, we *switch to*
    the state it wraps, we don't *push* it.  This implements a
    Delimiter's "change" tokens: e.g. the : inside { inside an
    f-string.  Inside { inside an f-string, before the :, #
    means "line comment", and after the : it's ignored.  The
    current delimiter continues--its close still pops.

    If the entry is an instance of _ACTION_TRUNCATE_TO_S_AND_RESPLIT,
    then this token starts with one of our current delimiters (close or escape).
    The _ACTION_TRUNCATE_TO_S_AND_RESPLIT class is a subclass of either str or
    bytes, and str(action) or bytes(action) (as appropriate) will convert it back
    into the relevant delimiter token.  We react as if we received *that* token
    instead, then "resplit" starting after the delimiter.

    Linebreaks are also handled using this mechanism.  If the current state
    is allergic to linebreak characters, all linebreak characters will be
    mapped to _ACTION_ILLEGAL_LINEBREAK.  If the current state doesn't care
    about linebreak characters, linebreak characters will be unmapped,
    which means they get the default action _ACTION_FLUSH.
    (And, if literally no delimiters have multiline=False in this run,
    we won't even add the linebreaks to the list of all tokens!  You don't
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

    buffer = []
    append = buffer.append
    clear = buffer.clear

    join = empty.join

    escaped = empty

    consumed = 0

    i = multisplit(text, all_tokens, keep=True, separate=True)
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
                    i = multisplit(text[consumed:], all_tokens, keep=True, separate=True)
                    break

            if s:
                append(s)
                consumed += len(s)

            if not delimiter:
                # we're done!
                # on the next iteration, i will be exhausted,
                # we'll hit the else clause on the for-else loop,
                # and we'll exit the outer loop too.
                break

            action = current.get(delimiter, _ACTION_FLUSH)

            # if want_debug:
            #     if isinstance(action, _ACTION_GOTO_STATE):
            #         print(f"    action is _ACTION_GOTO_STATE (goto dict)")
            #     elif isinstance(action, dict):
            #         print(f"    action is <action: push dict>")
            #     else:
            #         print(f"    {action=}")

            if isinstance(action, _ACTION_TRUNCATE_TO_S_AND_RESPLIT):
                # convert the action back into the startswith delimiter we want,
                # being careful to use the original text,
                delimiter_length = len(str_or_bytes(action))
                delimiter = delimiter[:delimiter_length]
                # look up the actual action we should use to handle that delimiter,
                action = current.get(delimiter, _ACTION_FLUSH)
                # assert action is not _ACTION_FLUSH, f"{action!r} is not {_ACTION_FLUSH}, delimiter={delimiter}"
                # activate resplit,
                resplit = True
                # and fall through to the appropriate _ACTION handler.
                # if want_debug:
                #     print(f"    new {action=}")

            if isinstance(action, _ACTION_CHANGE_STATE):
                # don't "push" the state, just switch to this state.
                # (used for colon inside curly braces inside an f-string.)
                s = join(buffer)
                clear()
                s_length = len(s)
                s_empty = s[s_length:]
                yield SplitDelimitersValue(s, s_empty, s_empty, delimiter)
                consumed += len(delimiter)
                current = action.state
                stack[-1] = (stack[-1][0], delimiter)
            elif isinstance(action, dict):
                # action is a new state, push it.
                # flush open delimiter
                s = join(buffer)
                clear()
                delimiter_length = len(delimiter)
                delimiter_empty = delimiter[delimiter_length:]
                yield SplitDelimitersValue(s, delimiter, delimiter_empty, delimiter_empty)
                consumed += len(delimiter)
                # and push
                push((current, delimiter))
                current = action
            elif action is _ACTION_POP:
                # flush close delimiter
                s = join(buffer)
                clear()
                s_length = len(s)
                s_empty = s[s_length:]
                delimiter_length = len(delimiter)
                delimiter_empty = delimiter[delimiter_length:]
                yield SplitDelimitersValue(s, s_empty, delimiter, delimiter_empty)
                consumed += len(delimiter)
                # and pop
                current, _ = pop()
            # elif action is _ACTION_2POP:
            #     # flush close delimiter
            #     s = join(buffer)
            #     clear()
            #     s_length = len(s)
            #     s_empty = s[s_length:]
            #     delimiter_length = len(delimiter)
            #     delimiter_empty = delimiter[delimiter_length:]
            #     yield SplitDelimitersValue(s, s_empty, delimiter, delimiter_empty)
            #     consumed += len(delimiter)
            #     # and pop twice
            #     current, _ = pop()
            #     current, _ = pop()
            elif action is _ACTION_ESCAPE:
                # escape
                append(delimiter)
                escaped = delimiter
                consumed += len(delimiter)
            elif action is _ACTION_FLUSH:
                append(delimiter)
                consumed += len(delimiter)
            elif action is _ACTION_FLUSH_1_AND_RESPLIT:
                # flush first character of delimiter, and resplit.
                append(delimiter[0:1])
                consumed += 1
                resplit = True
            elif action is _ACTION_ILLEGAL:
                # illegal character
                raise SyntaxError(f"index {consumed}: illegal string {delimiter!r}")
            elif action is _ACTION_ILLEGAL_LINEBREAK:
                # illegal linebreak character
                assert stack
                raise SyntaxError(f"index {consumed}: linebreak character {delimiter!r} is illegal inside delimiter {stack[-1][1]!r}")
            else: # pragma: nocover
                # unhandled
                raise RuntimeError(f"index {consumed}: unhandled action {action!r}")

            if resplit:
                i = multisplit(text[consumed:], all_tokens, keep=True, separate=True)
                resplit = False
                break
        else:
            break

    if buffer:
        if escaped:
            raise SyntaxError(f"text ends with escape string {escaped!r}")
        s = join(buffer)
        if s:
            s_length = len(s)
            s_empty = s[s_length:]
            yield SplitDelimitersValue(s, s_empty, s_empty, s_empty)


_split_delimiters = split_delimiters

_split_delimiters_default_delimiters_cache = _delimiters_to_state_and_tokens(tuple(split_delimiters_default_delimiters.items()), False)
_delimiters_cache.append(
    (split_delimiters_default_delimiters, (lambda cache=_split_delimiters_default_delimiters_cache: cache))
    )

_split_delimiters_default_delimiters_bytes_cache = _delimiters_to_state_and_tokens(tuple(split_delimiters_default_delimiters_bytes.items()), True)
_delimiters_cache.append(
    (split_delimiters_default_delimiters_bytes, (lambda cache=_split_delimiters_default_delimiters_bytes_cache: cache))
    )


@export
def split_delimiters(s, delimiters=split_delimiters_default_delimiters, *, state=(), yields=4):
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
    whenever you see a close delimiter.  Since split_delimiters ensures
    that open and close delimiters match, you don't need to check them
    yourself!)

    Yields a object of type SplitDelimitersValue.  This object
    contains four fields:

        text
            The text before the next opening, closing, or changing
            delimiter.

        open
            The trailing opening delimiter.

        close
            The trailing closing delimiter.

        change
            The trailing change delimiter.

    Iterating over a SplitDelimitersValue object yields these four
    values in that order, so you can unpack it directly:

        for text, open, close, change in big.split_delimiters(s):
            ...

    A "change" delimiter changes the semantics of the *current*
    delimiter, without entering a new nested delimiter.  The
    canonical example is the colon inside curly braces inside a
    Python f-string: before the colon, '#' means "line comment";
    after it, '#' is just another character.

    At least one of text, open, close, and change will always be
    non-empty.  (Only one of open, close, and change will ever be
    non-empty in a single SplitDelimitersValue object.)  If s
    doesn't end with an opening, closing, or changing delimiter,
    the final value yielded will have empty strings for open,
    close, and change.

    The yields parameter is deprecated, and will be removed no
    sooner than August 2027.

    In big 0.12.5 through 0.13 it selected between yielding three
    values--the pre-0.12.5 behavior--and yielding all four.  As
    promised in the 0.12.5 release notes, that transition period
    is over: split_delimiters always yields four values now, and
    the only permitted value for yields is 4.  (Code that
    dutifully migrated to yields=4 keeps working; simply remove
    the argument at your leisure.)  Relatedly, the SplitDelimitersValue
    object has a deprecated "yields" attribute, which likewise
    told you whether the object iterated as three or four values;
    it now always returns 4, and will be removed at the same time
    as the yields parameter.

    You may not specify backslash ('\\\\') as an open delimiter.

    Multiple Delimiter objects specified in delimiters may use
    the same close delimiter string.

    split_delimiters doesn't react if the string ends with
    unterminated delimiters.

    See the Delimiter object for how delimiters are defined, and how
    you can define your own delimiters.
    """
    if yields != 4:
        raise ValueError("as of big 0.14, split_delimiters always yields four values, so yields must be 4.  (The parameter is deprecated, and will be removed no sooner than August 2027.)")

    initial_state = all_tokens = None

    is_bytes = isinstance(s, bytes)
    if is_bytes:
        str_or_bytes = bytes
        if delimiters is None:
            delimiters = split_delimiters_default_delimiters_bytes
        elif not delimiters:
            raise ValueError("invalid delimiters")
        elif b'\\' in delimiters:
            raise ValueError("open delimiter must not be b'\\'")
    else:
        str_or_bytes = str
        if delimiters is None:
            delimiters = split_delimiters_default_delimiters
        elif not delimiters:
            raise ValueError("invalid delimiters")
        elif '\\' in delimiters:
            raise ValueError("open delimiter must not be '\\'")

    s_length = len(s)
    empty = s[s_length:]

    for d, get_cache in _delimiters_cache:
        # identity first: the overwhelmingly common case is being
        # handed the exported grammar object itself, and == on a
        # grammar dict compares every Delimiter, deeply.
        if (delimiters is d) or (delimiters == d):
            initial_state, all_tokens = get_cache()
            break

    if not initial_state:
        initial_state, all_tokens = _delimiters_to_state_and_tokens(tuple(delimiters.items()), is_bytes)
    assert initial_state
    assert all_tokens

    stack = []
    push = stack.append

    current = initial_state
    open = None

    if state:
        for i, delimiter in enumerate(_iterate_over_bytes(state)):
            action = current.get(delimiter, _ACTION_FLUSH)
            if isinstance(action, dict):
                push((current, delimiter))
                current = action
                continue

            raise ValueError(f"delimiter #{i} specified in state is invalid: {delimiter!r}")

    return _split_delimiters(s, all_tokens, current, stack, empty, str_or_bytes)



@export
class LineInfo:
    """
    The first object in the 2-tuple yielded by a
    lines iterator, containing metadata about the line.
    Every parameter to the constructor is stored as an
    attribute of the new LineInfo object using the
    same identifier.

    line is the original unmodified line, split
    from the original s input to lines.  Note
    that line includes the trailing linebreak character,
    if any.

    line_number is the line number of this line.

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

    Note: lines, LineInfo, and all the lines modifier
    functions are now deprecated, and will be removed
    no sooner than March 2027.
    """
    def __init__(self, lines, line, line_number, column_number, *, leading=None, trailing=None, end=None, indent=0, match=None, source='', **kwargs):
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

        if leading is None:
            leading = empty
        elif not isinstance(leading, line_type):
            raise TypeError(f"leading must be same type as line or None, not {leading!r}")

        if trailing is None:
            trailing = empty
        elif not isinstance(trailing, line_type):
            raise TypeError(f"trailing must be same type as line or None, not {trailing!r}")

        if end is None:
            end = empty
        elif not isinstance(end, line_type):
            raise TypeError(f"end must be same type as line or None, not {end!r}")

        if not ((match is None) or _isinstance_re_pattern(match)):
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
        self.source = source
        self._is_bytes = is_bytes
        self._empty = empty
        self.__dict__.update(kwargs)

    def copy(self):
        copy = LineInfo('', '', 0, 0)
        copy.__dict__ = self.__dict__.copy()
        return copy

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
        if not isinstance(s, int):
            # assert line.startswith(s), f"line {line!r} doesn't start with s {s!r}"
            i = len(s)
        else:
            # assert -len(line) <= s < len(line), f"clip_leading s={s!r} index is larger than the length of line={line!r}"
            i = s
            s = None
            l = line
        line = line[i:]
        if not line:
            # if you clip the entire line, we move the entire line into trailing
            # (minus end)
            assert self.line.endswith(self.end)
            empty = self._empty
            self.column_number -= len(self.leading)
            if self.end:
                self.trailing = self.line[:-len(self.end)]
            else:
                self.trailing = self.line
            self.leading = empty
            return empty
        if s is None:
            s = l[:i]
        self.leading += s
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
        if not isinstance(s, int):
            # assert line.endswith(s), f"line {line!r} doesn't end with s {s!r}"
            i = len(s)
        else:
            # assert -len(line) <= s < len(line), f"clip_trailing s={s!r} index is larger than the length of line={line!r}"
            i = s
            s = None
            l = line
        line = line[:-i]
        if not line:
            # if you clip the entire line, we move the entire line into trailing (minus end)
            assert self.line.endswith(self.end)
            empty = self._empty
            self.column_number -= len(self.leading)
            if self.end:
                self.trailing = self.line[:-len(self.end)]
            else:
                self.trailing = self.line
            self.leading = empty
            return empty
        if s is None:
            s = l[-i:]
        self.trailing = s + self.trailing
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


@export
class lines:
    def __init__(self, s, separators=None, *, clip_linebreaks=True, line_number=1, column_number=1, source='', tab_width=8, **kwargs):
        """
        A "lines iterator" object.  Splits s into lines, and iterates yielding those lines.

        When iterated over, yields 2-tuples:
            (info, line)
        where info is a LineInfo object, and line is a str or bytes object.

        s can be str, bytes, or an iterable.

        If s is neither str nor bytes, s must be an iterable.
        The iterable should either yield individual strings, which is the
        line, or it should yield a tuple containing two strings, in which case
        the strings should be the line and the line-terminating linebreak respectively.
        All "string" objects yielded by this iterable should be homogeneous,
        either str or bytes.

        separators should either be None or an iterable of separator strings,
        as per the separators argument to multisplit.  If s is str or bytes,
        it will be split using multisplit, using these separators.  If
        separators is None--the default--and s is str or bytes, s will be
        split at linebreak characters.  (If s is neither str nor bytes,
        separators must be None.)

        line_number is the starting line number given to the first LineInfo
        object.  This number is then incremented for every subsequent line.

        column_number is the starting column number given to every LineInfo
        object.  This number represents the leftmost column of every line.

        tab_width isn't used by lines itself, but is stored internally and
        may be used by other lines modifier functions (e.g. lines_strip_indent,
        lines_convert_tabs_to_spaces). Similarly, all keyword arguments passed
        in via kwargs are stored internally and can be accessed by user-defined
        lines modifier functions.

        lines copies the line-breaking character (usually \\n) from each line
        to info.end. If clip_linebreaks is true (the default), lines will clip
        the linebreak off the end of each line.  If clip_linebreaks is false,
        lines will leave the linebreak in place.

        You can pass in an instance of a subclass of bytes or str
        for s and elements of separators, but the base class
        for both must be the same (str or bytes).  lines will
        only yield str or bytes objects for line.

        Composable with all the lines_ modifier functions in the big.text module.

        Note: lines, LineInfo, and all the lines modifier
        functions are now deprecated, and will be removed
        no sooner than March 2027.
        """
        # one warning covers the whole pipeline: every lines_*
        # modifier consumes an iterator that started here.
        # (warnings.warn doesn't halt anything--by default Python
        # doesn't even *show* DeprecationWarnings outside __main__.)
        warnings.warn(
            "big's lines, LineInfo, and the lines_* modifier functions"
            " are deprecated, and will be removed no sooner than"
            " March 2027.  Use big.string instead; see 'Migrating from"
            " lines to string' in big's README.",
            DeprecationWarning, stacklevel=2)

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
        self.clip_linebreaks = clip_linebreaks
        self.source = source

        is_bytes = isinstance(s, bytes)
        is_str = isinstance(s, str)
        if is_bytes or is_str:
            if not separators:
                separators = linebreaks if is_str else bytes_linebreaks
            self.i = multisplit(s, separators, keep=True, separate=True, strip=False)
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
            if not self.clip_linebreaks:
                line = original_line
        else:
            original_line = line
        return_value = (LineInfo(self, original_line, self.line_number, self.column_number, end=end, source=self.source), line)
        self.line_number += 1
        return return_value

@export
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

    Note: lines, LineInfo, and all the lines modifier
    functions are now deprecated, and will be removed
    no sooner than March 2027.
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


@export
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

    Note: lines, LineInfo, and all the lines modifier
    functions are now deprecated, and will be removed
    no sooner than March 2027.
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

@export
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

    Note: lines, LineInfo, and all the lines modifier
    functions are now deprecated, and will be removed
    no sooner than March 2027.
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


@export
def lines_containing(li, s, *, invert=False):
    """
    A lines modifier function.  Only yields lines
    that contain s.  (Filters out lines that
    don't contain s.)

    If invert is true, returns the opposite:
    filters out lines that contain s.

    Composable with all the lines_ modifier functions in the big.text module.

    Note: lines, LineInfo, and all the lines modifier
    functions are now deprecated, and will be removed
    no sooner than March 2027.
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

@export
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

    (In older versions of Python, re.Pattern was a private type called
    re._pattern_type.)

    Composable with all the lines_ functions from the big.text module.

    Note: lines, LineInfo, and all the lines modifier
    functions are now deprecated, and will be removed
    no sooner than March 2027.
    """
    if not match.isidentifier():
        raise ValueError('match must be a valid identifier')

    if not _isinstance_re_pattern(pattern):
        pattern = re.compile(pattern, flags=flags)
    search = pattern.search

    return _lines_grep(li, search, match, invert)


@export
def lines_sort(li, *, key=None, reverse=False):
    """
    A lines modifier function.  Sorts all input lines before yielding them.

    If key is specified, it's used as the key parameter to list.sort.
    The key function will be called with the (info, line) tuple yielded
    by the lines iterator.  If key is a false value, lines_sort sorts the
    lines lexicographically, from lowest to highest.

    If reverse is true, lines are sorted from highest to lowest.

    Composable with all the lines_ modifier functions in the big.text module.

    Note: lines, LineInfo, and all the lines modifier
    functions are now deprecated, and will be removed
    no sooner than March 2027.
    """
    lines = list(li)
    if key is None:
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

@export
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

    Note: lines, LineInfo, and all the lines modifier
    functions are now deprecated, and will be removed
    no sooner than March 2027.
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




@export
def lines_convert_tabs_to_spaces(li):
    """
    A lines modifier function.  Converts tabs to spaces for the lines
    of a "lines iterator", using the tab_width passed in to lines.

    Composable with all the lines_ modifier functions in the big.text module.

    Note: lines, LineInfo, and all the lines modifier
    functions are now deprecated, and will be removed
    no sooner than March 2027.
    """
    for info, line in li:
        yield (info, info.detab(line))


@export
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

    Note: lines, LineInfo, and all the lines modifier
    functions are now deprecated, and will be removed
    no sooner than March 2027.
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

        if new_indent:
            leadings.append(column_number)
            indent += 1

        if blank_lines:
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

@export
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

    Note: lines, LineInfo, and all the lines modifier
    functions are now deprecated, and will be removed
    no sooner than March 2027.
    """
    for t in li:
        if not t[1]:
            continue
        yield t



# --8<-- start big word wrap trio --8<--
# --8<-- requires big license --8<--
# --8<-- requires big word wrap trio imports --8<--
# --8<-- requires big _iterate_over_bytes --8<--
# --8<-- requires big linebreaks --8<--

def _expand_tabs(s, column, tab_width, tab, space, first_column=1):
    """
    Expands the tabs in s to spaces and returns the result.
    s is assumed to be a single line, starting at 'column';
    linebreak characters don't reset the column here (that's
    expand_tabs's job).

    Tab stops sit every tab_width columns, counted from
    first_column: with a first_column of 1 and the default
    tab_width of 8, a tab advances to column 9, 17, 25, ...
    (This is the same arithmetic big.string uses for its
    column numbers.)

    tab and space supply the correct type of those two characters
    ('\\t' and ' ', or b'\\t' and b' ').
    """
    segments = s.split(tab)
    if len(segments) == 1:
        return s
    result = []
    append = result.append
    for i, segment in enumerate(segments):
        if i:
            delta = tab_width - ((column - first_column) % tab_width)
            append(space * delta)
            column += delta
        append(segment)
        column += len(segment)
    return s[:0].join(result)


def expand_tabs(s, *, column=1, first_column=1, tab_width=8):
    """
    Expands the tabs in s to spaces and returns the result.
    If s contains no tabs, returns s unchanged.

    s may be str or bytes, and may contain multiple lines.

    'column' is the column of the first character of s.
    'first_column' is the column the count resets to after a
    linebreak--the column your lines start at.  (These follow
    big.string, which uses column_number and first_column_number
    the same way.)  column may not be less than first_column,
    and first_column may not be negative.

    Tab stops sit every tab_width columns, counted from
    first_column: with the default first_column of 1 and the
    default tab_width of 8, a tab advances to column 9, 17, 25...
    This too matches big.string's arithmetic.  A tab's width
    depends on the column where it lands, so if s is going to be
    placed anywhere other than the left edge of the page,
    expanding its tabs correctly requires knowing where it
    starts.

    Lines are separated as str.splitlines splits them
    (for bytes, bytes.splitlines); the linebreak characters
    are preserved in the result.
    """
    if (not isinstance(first_column, int)) or (first_column < 0):
        raise ValueError(f"first_column must be a non-negative int, not {first_column!r}")
    if (not isinstance(column, int)) or (column < first_column):
        raise ValueError(f"column must be an int >= first_column ({first_column}), not {column!r}")
    if isinstance(s, bytes):
        tab = b'\t'
        space = b' '
    else:
        tab = '\t'
        space = ' '
    if tab not in s:
        return s
    result = []
    append = result.append
    for line in s.splitlines(keepends=True):
        append(_expand_tabs(line, column, tab_width, tab, space, first_column))
        column = first_column
    return s[:0].join(result)


def _normalize_indents(indent, name, margin, tab_width, left_column, indent_type):
    """
    Validates, normalizes, and measures an "indent" argument for wrap_words.

    indent is an indent argument to wrap_words (either indent or code_indent).
    name is a string identifying which indent argument this is (used for
      error messages).
    margin is the word wrap margin--we confirm the longest indent fits.
    tab_width and left_column govern tab expansion: tabs in an indent
      are expanded to spaces, at the indent's true position (an indent
      always starts its line, at left_column).
    indent_type is the type (str or bytes) indent should be.

    Returns a 2-tuple:
        (indents, columns)
    indents is a tuple of strings: indent, normalized as a tuple,
        with any tabs expanded.
    columns is a list of ints, the same length as indents,
        with the measured width of each one.
    """
    if isinstance(indent, indent_type):
        indents = (indent,)
    elif isinstance(indent, (list, tuple)):
        indents = indent
        for i in indents:
            if not isinstance(i, indent_type):
                raise TypeError(f"{name} must be {indent_type.__name__}, or a list or tuple of {indent_type.__name__}, not {i!r}")
    else:
        raise TypeError(f"{name} must be {indent_type.__name__}, or a list or tuple of {indent_type.__name__}, not {indent!r}")

    # forbidden is a membership-testable object containing
    # characters forbidden to be in the indent--linebreaks.
    # for str, forbidden is a set, as that's cheapest.
    # for bytes it's the joined bytes object--iterating a bytes yields ints, and
    # int-in-bytes membership tests the byte value
    if indent_type is bytes:
        indent_iter = _iterate_over_bytes
        forbidden = set(bytes_linebreaks)
        tab = b'\t'
        space = b' '
    else:
        indent_iter = iter
        forbidden = set(linebreaks)
        tab = '\t'
        space = ' '

    expanded = []
    columns = []
    append = columns.append
    for i in indents:
        characters = set(indent_iter(i))
        intersection = characters & forbidden
        if intersection:
            raise ValueError(f"{name} {i!r} contains linebreak characters {intersection!r}")

        i = _expand_tabs(i, left_column, tab_width, tab, space)
        expanded.append(i)
        column = len(i)
        if column >= margin:
            raise ValueError(f"{name} {i!r} leaves no room for words inside margin {margin}")
        append(column)

    return tuple(expanded), columns


def wrap_words(words, margin=79, *, code_indent=None, indent='', left_column=1, tab_width=8, two_spaces=True):
    """
    Combines 'words' into lines and returns the result as a string.
    Similar to textwrap.wrap.

    'words' should be an iterator yielding str or bytes strings, and
    these strings should already be split at word boundaries.
    Here's an example of a valid argument for 'words':
        ["this", "is", "an", "example", "of",
         "text", "split", "at", "word", "boundaries"]

    A single '\n' indicates a line break.
    A double '\n\n' indicates a paragraph break.
    Two line breaks in a row ('\n', '\n') doesn't count as
    a paragraph break ('\n\n').
    A single '\t' indicates a tab: the next word is placed at the
    next tab stop, as governed by tab_width and left_column.  A tab
    renders as spaces--wrap_words is the final rendering, and it
    knows what column everything lands at, so its output contains
    no tabs.  No space is added around a tab (the tab IS the
    separation); consecutive tabs advance consecutive stops; if
    the word after a tab doesn't fit on the line, the word wraps
    and the tab dies with the line, just like a space would.
    Any other whitespace-only strings are unsupported, and if
    you pass in a "words" array to wrap_words containing one,
    its behavior is undefined.

    Implicitly supports "code lines" as defined by split_text_with_code.
    (A "code line" just shows up in words as one unbroken word surrounded
    by line breaks.)  Tabs inside a code line are expanded to spaces
    when the line is rendered, at the column where they actually land.

    'margin' specifies the maximum length of each line. The length of
    every line will be less than or equal to 'margin', unless the length
    of an individual element inside 'words' is greater than 'margin'.

    'left_column' is the 1-based "virtual left column": the column
    your output will start at, if you're going to place it somewhere
    other than the left edge of the page.  It only affects how tabs
    are rendered--tab stops live at fixed columns of the page
    (9, 17, 25, ... with the default tab_width of 8), so text that
    starts at column 5 reaches its first tab stop after four
    characters, not eight.  'margin' is unaffected: it's the width
    of the block wrap_words produces, wherever you put it.

    If 'two_spaces' is true, elements from 'words' that end in
    sentence-ending punctuation ('.', '?', and '!') will be followed
    by two spaces, not one.

    'indent' is a value used to prefix every line in the wrapped
    paragraphs.  It may be a single string, in which case every line
    gets prefixed with 'indent'.  It may also be a list or tuple of
    strings, in which case the first line of a paragraph gets indent[0],
    the second indent[1], etc; once we run out, we use indent[-1] for
    all subsequent lines in the paragraph.  The line counter resets
    every time we start a new paragraph.  Blank lines separating
    paragraphs never get indented.  'indent' strings may not contain
    linebreak characters.

    'code_indent' is an indent used only for paragraphs made up of
    code lines.  If code_indent is None, code lines and normal lines
    both use the 'indent' prefix string(s).  Otherwise, code_indent
    accepts the same sorts of values as 'indent', and uses them the
    same way--but 'code_indent' only applies to paragraphs made up
    of code lines.  ('indent' will still be used for paragraphs made
    up of text.)

    An indent string reduces the space available for the paragraph;
    if your margin is 70, and your indent string is 5 characters,
    you effectively have a margin of only 65.  Tabs inside an indent
    are expanded to spaces at the indent's true position (an indent
    always starts its line, at left_column).  If the length of your
    indent is equal to or greater than your margin, wrap_words raises
    ValueError.

    Elements in 'words' are not modified--except for tab expansion;
    any leading or trailing whitespace will be preserved.  You can
    use this to preserve whitespace where necessary; this is the
    mechanism used to preserve code lines.

    The objects yielded by words can be a subclass of either
    str or bytes, though wrap_words will only return str or bytes.
    All the objects yielded by words must have the same base class
    (str or bytes).  If they're bytes, indent and code_indent must
    be bytes too (or lists or tuples of bytes).

    If 'words' is empty, raises ValueError.
    (Note that split_text_with_code('') returns [''].)
    """
    if (not isinstance(left_column, int)) or (left_column < 1):
        raise ValueError(f"left_column must be a positive int, not {left_column!r}")

    words = iter(words)
    col = 0
    empty = None
    lastword = None
    text = []
    append = text.append
    first_word = True

    indents = widths = code_indents = None
    last_indent = 0
    line_number = 0
    pending_tabs = 0

    new_paragraph = True
    new_line = True
    code_paragraph = False

    def next_tab_stops(col, tabs):
        # the 0-based line offset of the next word, after
        # advancing 'tabs' tab stops from the offset 'col'.
        # tab stops live at fixed 1-based columns of the page:
        # 1 + (k * tab_width).
        absolute = left_column + col
        for _ in range(tabs):
            absolute += tab_width - ((absolute - 1) % tab_width)
        return absolute - left_column

    for word in words:
        if first_word:
            first_word = False
            if isinstance(word, bytes):
                empty = lastword = b''
                sentence_ending_punctuation = (b'.', b'?', b'!')
                space1 = b' '
                space2 = b'  '
                linebreak = b'\n'
                tab = b'\t'
            else:
                empty = lastword = ''
                sentence_ending_punctuation = ('.', '?', '!')
                space1 = ' '
                space2 = '  '
                linebreak = '\n'
                tab = '\t'
            if indent or (code_indent is not None):
                indent_type = bytes if isinstance(word, bytes) else str
                if indent:
                    indents, widths = _normalize_indents(
                        indent, 'indent', margin, tab_width, left_column, indent_type)
                else:
                    indents, widths = (empty,), (0,)
                last_indent = len(indents) - 1

                if code_indent is None:
                    code_indents = indents
                    code_widths = widths
                    last_code_indent = last_indent
                else:
                    code_indents, code_widths = _normalize_indents(
                        code_indent, 'code_indent', margin, tab_width, left_column, indent_type)
                    last_code_indent = len(code_indents) - 1

        if word.isspace():
            if word == tab:
                # a tab word: not a line break, not a paragraph
                # break--column advancement, resolved when we
                # place the next word.
                pending_tabs += 1
                continue
            lastword = word
            append(word)

            pending_tabs = 0
            new_line = True
            col = 0

            new_paragraph = len(word) > 1
            if not new_paragraph:
                line_number += 1
            continue

        if new_paragraph:
            new_paragraph = False
            code_paragraph = word[:1].isspace()
            line_number = 0
            lastword = empty

        if code_paragraph:
            pending_tabs = 0
            if code_indents:
                index = min(line_number, last_code_indent)
                append(code_indents[index])
                col = code_widths[index]
            else:
                col = 0
            if tab in word:
                # a code line's tabs expand at render time, at the
                # columns where they actually land.
                word = _expand_tabs(word, left_column + col, tab_width, tab, space1)
            append(word)
            continue

        # text paragraph
        l = len(word)
        if not l:
            continue

        tabs = pending_tabs
        pending_tabs = 0

        if not new_line:
            if tabs:
                # tab(s) glue this word to the line at a tab
                # stop--if it fits.  if it doesn't, the word
                # wraps, and the tabs die with the line, just
                # like a space would.
                target = next_tab_stops(col, tabs)
                if (target + l) > margin:
                    append(linebreak)
                    new_line = True
                    line_number += 1
                    tabs = 0
                else:
                    append(space1 * (target - col))
                    col = target
            elif col:
                if two_spaces and lastword.endswith(sentence_ending_punctuation):
                    space = space2
                    len_space = 2
                else:
                    space = space1
                    len_space = 1

                wrap = (col + len_space + l) > margin
                if wrap:
                    append(linebreak)
                    new_line = True
                    line_number += 1
                else:
                    append(space)
                    col += len_space

        if new_line:
            new_line = False
            if not indents:
                col = 0
            else:
                index = min(line_number, last_indent)
                prefix = indents[index]
                append(prefix)
                col = widths[index]
            if tabs:
                # tabs at the start of a line (only a hand-built
                # stream gets here): advance from the line's
                # start.  no wrap check--like an over-long word,
                # an over-margin stop just overflows.
                target = next_tab_stops(col, tabs)
                append(space1 * (target - col))
                col = target

        append(word)
        col += len(word)
        lastword = word

    if first_word:
        raise ValueError("no words to wrap")

    s = empty.join(text)
    return s


def split_text_with_code(s, *, code_indent=4, tab_width=8):
    """
    Splits the string s into individual words,
    suitable for feeding into wrap_words.

    s may be either str or bytes.

    Paragraphs indented by less than code_indent will be
    broken up into individual words.

    code_indent must be an int.  If it's nonzero, lines indented
    by at least code_indent columns are "code lines": paragraphs
    of them preserve their whitespace, internal and leading, and
    their linebreaks.  (This preserves the formatting of code
    examples, when these words are rejoined into lines by
    wrap_words.)  Code lines are emitted verbatim, tabs included;
    wrap_words expands their tabs at render time, when it knows
    what column the line lands at.  If code_indent is 0, there
    are no code lines: everything is just text.

    In text, a tab survives as its own '\\t' word: a run of
    whitespace containing k tabs becomes exactly k '\\t' words,
    in order--the rest of the whitespace is just separation,
    and is thrown away as usual.  wrap_words renders a '\\t'
    word by placing the next word at the next tab stop.

    s can be str, bytes, or a subclass of either, though
    split_text_with_code will only return str or bytes.

    The only whitespace-only words split_text_with_code will
    ever emit are '\\n' (line break), '\\n\\n' (paragraph break),
    and '\\t' (tab).

    split_text_with_code is inflexible about line endings;
    it only recognizes '\\n' (or b'\\n') as ending a line.

    if s is empty, returns a list containing an empty string.
    """

    if isinstance(code_indent, bool):
        # bool sneaks through the index protocol; "we must
        # remain strong."
        raise TypeError(f"code_indent must be an int, not {code_indent!r}")
    code_indent = operator.index(code_indent)
    if code_indent < 0:
        raise ValueError(f"code_indent must be non-negative, not {code_indent!r}")

    if isinstance(s, bytes):
        empty = b''
        tab = b'\t'
        linebreak = b'\n'
        paragraph_break = b'\n\n'
        iterate_over_characters = _iterate_over_bytes
    else:
        empty = ''
        tab = '\t'
        linebreak = '\n'
        paragraph_break = '\n\n'
        iterate_over_characters = iter

    linebreak_tuple = (linebreak,)
    code_paragraph = "code paragraph"
    text_paragraph = "text paragraph"

    # the kind of paragraph the previous nonblank line belonged to:
    # code_paragraph, text_paragraph, or None (haven't seen one yet).
    previous_paragraph = None

    # how many blank lines we've seen since the previous nonblank line.
    blank_lines = 0

    words = []

    # only '\n' ends a line.  every other whitespace character--
    # including '\r'--is just whitespace, width 1.
    for line in s.split(linebreak):
        line = line.rstrip()
        if not line:
            blank_lines += 1
            continue

        if code_indent:
            # measure the line's indent, expanding tabs.
            stripped = line.lstrip()
            col = 0
            len_indent = len(line) - len(stripped)
            for i, c in enumerate(iterate_over_characters(line)):
                if i == len_indent:
                    break
                if c == tab:
                    col += tab_width - (col % tab_width)
                else:
                    # space, and any unusual whitespace
                    # (\r, \v, \f, nbsp...), counts as width 1.
                    col += 1

            if col >= code_indent:
                # it's a code line.
                if previous_paragraph is text_paragraph:
                    words.append(paragraph_break)
                elif previous_paragraph is code_paragraph:
                    # in a code paragraph, linebreaks are just that--
                    # line breaks.  if you want to finish the current
                    # code line, emit a line break.  if you want an
                    # empty line in the middle of a code paragraph,
                    # emit two linebreaks in a row.  (if you want two
                    # empty lines, emit three linebreaks.)
                    #
                    # as a rule, code paragraphs start with a code line,
                    # then have one or more line breaks before the next
                    # code line.  you never have two code lines in a row.
                    # the paragraph break that ends a code paragraph can
                    # come after either a code line or a linebreak.
                    words.extend(linebreak_tuple * (blank_lines + 1))

                # reproduce the line as a single word, verbatim--
                # tabs included.  wrap_words expands them at render
                # time, when it knows what column the line lands at.
                words.append(empty + line)
                previous_paragraph = code_paragraph
                blank_lines = 0
                continue

        # not a code line.
        if ((previous_paragraph is code_paragraph)
            or ((previous_paragraph is text_paragraph) and blank_lines)):
            words.append(paragraph_break)
        # split the line into words.  each tab survives as its own
        # '\t' word, in order: a run of whitespace containing k tabs
        # becomes exactly k '\t' words.
        first_segment = True
        for segment in line.split(tab):
            if not first_segment:
                words.append(tab)
            first_segment = False
            words.extend(segment.split())
        previous_paragraph = text_paragraph
        blank_lines = 0

    if not words:
        words.append(empty)
    return words


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

def merge_columns(*columns, column_separator=None,
    overflow_strategy=OverflowStrategy.RAISE,
    overflow_before=0,
    overflow_after=0,
    tab_width=8,
    ):
    """
    Merge n column tuples, with each column tuple being
    formatted into its own column in the resulting string.
    Returns a string.

    columns should be an iterable of column tuples.
    Each column tuple should contain three items:
        (text, min_width, max_width)
    text should be a single string, either str or bytes,
    with linebreak characters separating lines. min_width
    and max_width are the minimum and maximum permissible
    widths for that column, not including the column
    separator (if any).

    A column tuple may carry an optional fourth member,
    relative_tabs, governing how tabs in that column's text are
    expanded (they're always expanded to spaces, using tab_width).
    If true (the default), each line's tabs expand in the column's
    own coordinates--as if the line started at column 1--and the
    expanded text shifts rigidly into place, so the column's
    internal alignment survives wherever the column lands.  If
    false, tabs expand at the column's position on the page (its
    nominal position: an overflow strategy that shifts lines
    doesn't move their tab stops).

    Note that this function doesn't text-wrap the lines.

    column_separator is printed between every column.

    overflow_strategy tells merge_columns how to handle a column
    with one or more lines that are wider than that column's max_width.
    The supported values are:

        OverflowStrategy.RAISE

            Raise an OverflowError.  The default: overflow is
            an error, and it shouldn't pass silently unless you
            explicitly silence it by picking another strategy.

        OverflowStrategy.INTRUDE_ALL

           Intrude into all subsequent columns on all lines
           where the overflowed column is wider than its max_width.

        OverflowStrategy.DELAY_ALL

           Delay all columns after the overflowed column,
           not beginning any until after the last overflowed line
           in the overflowed column.  (Help-style tables with an
           occasional overlong label usually want this one.)

    When overflow_strategy is INTRUDE_ALL or DELAY_ALL, and
    either overflow_before or overflow_after is nonzero, these
    specify the number of extra lines before or after
    the overflowed lines in a column.

    text and column_separator can be str, bytes, or a subclass
    of either, though merge_columns will only return str or bytes.
    All these objects (text and column_separator) must have the
    same baseclass, str or bytes.
    """
    # real raises, not asserts: these guard user input, and
    # asserts vanish under python -O.  (OverflowStrategy.INVALID
    # used to silently behave as INTRUDE_ALL under -O!)
    if overflow_strategy not in (OverflowStrategy.INTRUDE_ALL, OverflowStrategy.DELAY_ALL, OverflowStrategy.RAISE):
        raise ValueError(f"invalid overflow_strategy {overflow_strategy!r}")
    raise_overflow_error = overflow_strategy == OverflowStrategy.RAISE
    delay_all = overflow_strategy == OverflowStrategy.DELAY_ALL

    if not columns:
        raise ValueError("no columns")
    is_bytes = isinstance(columns[0][0], bytes)

    if is_bytes:
        empty = b''
        space = b' '
        linebreak = b'\n'
        tab = b'\t'
    else:
        empty = ''
        space = ' '
        linebreak = '\n'
        tab = '\t'

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

    # the 1-based column each column starts at, nominally
    # (as if nothing overflowed)--the phase for expanding
    # tabs with relative_tabs=False.
    nominal_left = 1

    for column_number, column in enumerate(_columns):
        s, min_width, max_width = column[:3]
        relative_tabs = column[3] if len(column) > 3 else True

        # check types, let them raise exceptions as needed
        operator.index(min_width)
        operator.index(max_width)

        empty_columns.append(max_width * space)

        if isinstance(s, (str, bytes)):
            lines = s.rstrip().split(linebreak)
        else:
            lines = s
        max_lines = max(max_lines, len(lines))

        tab_phase = 1 if relative_tabs else nominal_left
        nominal_left += max_width + column_spacing

        # loop 1:
        # measure each line length, determining
        #  * maximum line length, and
        #  * all overflow lines
        rstripped_lines = []
        overflows = []
        max_line_length = -1
        in_overflow = False

        for line_number, line in enumerate(lines):
            if tab in line:
                line = _expand_tabs(line, tab_phase, tab_width, tab, space)
            line = line.rstrip()
            assert not linebreak in line
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

        # loop 2 must consume the rstripped lines--both so that
        # per-line trailing whitespace can't fool the padding math,
        # and so the overflow_after padding lines appended above
        # actually make it into the output.
        lines = rstripped_lines

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

    text = linebreak.join(lines)
    return text.rstrip()

# --8<-- end big word wrap trio --8<--

export('expand_tabs')
export('wrap_words')
export('split_text_with_code')
export('OverflowStrategy')
export('merge_columns')


# --8<-- start big format_definition_list --8<--
# --8<-- requires big license --8<--
# --8<-- requires big word wrap trio --8<--

_default_definition_list_indent = '  '
_default_definition_list_spacer = '  '

def format_definition_list(pairs, margin=79, *,
        definition_left_column=None,
        definition_relative_tabs=True,
        indent=_default_definition_list_indent,
        spacer=_default_definition_list_spacer,
        tab_width=8,
        term_relative_tabs=True):
    """
    Formats a "definition list" and returns it as a string:
    terms on the left, definitions on the right, definitions
    wrapped to fit and aligned in a column.  Sample output:

        -v, --verbose  Print more output.  Repeat
                       for even more.
        --color <red|green|blue>
                       Sets the output color.

    'pairs' is an iterable of (term, definition) pairs of strings.
    Terms are never wrapped, and may not contain linebreak
    characters.  Definitions are text: each one is split with
    split_text_with_code and wrapped with wrap_words, so paragraph
    breaks, code lines, and tabs work as they do there.
    A pair with an empty definition is just the term on a line
    by itself.

    'margin' is the target width, as per wrap_words.

    'indent' is a string prefixed to every line.  Counts towards
    the margin (if your margin is 70, and your indent is 5 characters,
    your "effective margin" is 65).

    'spacer' is the fill material between a term and its definition,
    in the manner of TeX's leaders: conceptually the spacer repeats,
    phase-locked to the start of the term column, from the end of
    each term to the definition column--so the repeats line up
    vertically from line to line, and a line with no term (a wrapped
    continuation line, or a code line) fills the whole span.  The
    default spacer is two spaces, which renders as the classic help
    table above.  A visible spacer renders leaders, like a table of
    contents: spacer=':' gives you

        x:::::::::abcde
        y so long:this is the text
        ::::::::::for y no fooling

    A multi-character spacer tiles, clipped at the front so the
    columns still line up.  The spacer may not be empty: it's the
    fill material, and there's no such thing as filling with
    nothing.

    The indent for the definitions on the right (the "definition
    column") is computed dynamically.  It's one 'spacer' past the
    widest "term" that's no wider than a third of the effective
    margin.  A term wider than that "hangs": it gets the line
    to itself, and its definition starts on the next line, in the
    definition column.  Either way, a term on the same line as its
    definition always has at least one full spacer after it.

    'definition_left_column' overrides the computed column: it's
    the 1-based column (indent included) where the first character
    of every definition goes.  Fussy users may know exactly what
    they want.  The hang rule still applies, now purely geometric:
    a term hangs iff it can't fit on the line with a full spacer
    after it.  A definition_left_column that leaves no room for
    the spacer, or no room for definitions inside the margin,
    raises ValueError.

    Tabs are permitted in the terms and the indent; they're
    expanded to spaces, using 'tab_width'.  Tabs in the indent
    expand at the indent's true position (it starts every line,
    at column 1).  Tabs in a term expand in the term's own
    coordinates--as if the term started at column 1--and the
    expanded term shifts rigidly into place, so the term's
    internal alignment survives wherever the term lands; pass
    term_relative_tabs=False to expand them at the term's true
    position on the page instead.  definition_relative_tabs works
    the same way for the definitions: by default (True) each
    definition is laid out in its author's own coordinates--tab
    stops counted from the definition column, exactly as the
    author saw them--and shifts rigidly into place; pass False
    to land the definition's tabs on the tab stops of the page.
    Tabs are disallowed in the spacer: the spacer repeats and
    shifts around, and a tab's width depends on where it lands.

    You may use either str or bytes, but all arguments must be
    consistently either str or bytes.

    If pairs is empty, returns an empty str.
    """
    pairs = list(pairs)
    if not pairs:
        return ''

    if isinstance(pairs[0][0], bytes):
        str_type = bytes
        empty = b''
        tab = b'\t'
        linebreak = b'\n'
        forbidden = set(bytes_linebreaks)
        characters = _iterate_over_bytes
        if indent is _default_definition_list_indent:
            indent = b'  '
        if spacer is _default_definition_list_spacer:
            spacer = b'  '
    else:
        str_type = str
        empty = ''
        tab = '\t'
        linebreak = '\n'
        forbidden = set(linebreaks)
        characters = iter

    for name, s in (('indent', indent), ('spacer', spacer)):
        if not isinstance(s, str_type):
            raise TypeError(f"{name} must be {str_type.__name__}, not {s!r}")
        if set(characters(s)) & forbidden:
            raise ValueError(f"{name} {s!r} contains linebreak characters")
    if not spacer:
        raise ValueError("spacer must not be empty")
    if tab in spacer:
        raise ValueError(f"spacer {spacer!r} contains tabs")

    space = b' ' if str_type is bytes else ' '

    # an indent starts every line, at column 1: expand its
    # tabs there.
    indent = _expand_tabs(indent, 1, tab_width, tab, space)
    indent_width = len(indent)

    # validate the terms, and expand their tabs: in their own
    # coordinates (term_relative_tabs, the default), or at the
    # column where they actually land, right after the indent.
    term_column = 1 if term_relative_tabs else 1 + indent_width
    expanded = []
    widths = []
    for term, definition in pairs:
        if not isinstance(term, str_type):
            raise TypeError(f"terms must be {str_type.__name__}, not {term!r}")
        if set(characters(term)) & forbidden:
            raise ValueError(f"term {term!r} contains linebreak characters")
        term = _expand_tabs(term, term_column, tab_width, tab, space)
        expanded.append((term, definition))
        widths.append(len(term))
    pairs = expanded

    if definition_left_column is None:
        # the widest term no wider than a third of the effective
        # margin decides the definition column; wider terms hang.
        hang_threshold = (margin - indent_width) // 3
        column = 0
        for width in widths:
            if (width <= hang_threshold) and (width > column):
                column = width
        ribbon_width = column + len(spacer)
    else:
        # the fussy user knows exactly where they want the
        # definitions.  1-based, indent included.
        if (not isinstance(definition_left_column, int)) or (definition_left_column < 1):
            raise ValueError(f"definition_left_column must be a positive int, not {definition_left_column!r}")
        ribbon_width = definition_left_column - 1 - indent_width
        if ribbon_width < len(spacer):
            raise ValueError(f"definition_left_column {definition_left_column} leaves no room for the spacer")

    # a term fits on the same line as its definition iff at least
    # one full spacer separates them; wider terms hang.
    fit_limit = ribbon_width - len(spacer)

    definition_width = margin - indent_width - ribbon_width
    if definition_width < 1:
        raise ValueError(f"the definition column leaves no room for definitions inside margin {margin}")

    # the ribbon: the spacer tiled across the span from the start
    # of the term column to the definition column.  a term line
    # shows the ribbon from its own width onward, so the repeats
    # line up vertically no matter how wide the term is.
    # (the spacer contains no tabs, so its len is its width.)
    ribbon = (spacer * ((ribbon_width // len(spacer)) + 1))[:ribbon_width]

    definition_indent = indent + ribbon
    len_definition_indent = len(definition_indent)

    lines = []
    append = lines.append
    for (term, definition), width in zip(pairs, widths):
        if definition:
            if definition_relative_tabs:
                # lay the definition out in its author's own
                # coordinates--virtual column 1--and shift the
                # resulting lines rigidly into the definition
                # column.  (they're tab-free, so the shift is
                # safe.)  the author's tabs line up the way they
                # did when the author wrote them.
                wrapped = wrap_words(
                    split_text_with_code(definition, tab_width=tab_width),
                    definition_width, tab_width=tab_width)
                if wrapped:
                    wrapped = linebreak.join(
                        (definition_indent + line) if line.strip() else line
                        for line in wrapped.split(linebreak))
            else:
                # the definition's tabs land on the tab stops of
                # the *page*: render it in place.
                wrapped = wrap_words(
                    split_text_with_code(definition, tab_width=tab_width),
                    margin, indent=definition_indent, tab_width=tab_width)
        else:
            wrapped = empty
        if not wrapped:
            append(indent + term)
            continue
        if width > fit_limit:
            append(indent + term)
            append(wrapped)
            continue
        # the first wrapped line starts with definition_indent,
        # which renders exactly as wide as indent + term + the
        # rest of the ribbon.  slice those off and put these there
        # instead.
        append(indent + term + ribbon[width:] + wrapped[len_definition_indent:])
    return linebreak.join(lines)

# --8<-- end big format_definition_list --8<--

export('format_definition_list')


@export
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

    Numbers >= 10**75 (one trillion vigintillion)
    are only converted using str(i).  Sorry!
    """
    if not isinstance(i, int):
        raise TypeError(f"i must be int, not {type(i).__name__}")

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
            "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth",
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
            # note!            v  exactly ONE leading space--it's the separator!
            # (the alignment padding lives *outside* the quotes.  it
            # used to live inside for the shorter names, and leaked
            # into the output: "one   decillion".)
            (10**63,      " vigintillion"),
            (10**60,    " novemdecillion"),
            (10**57,     " octodecillion"),
            (10**54,   " septendecillion"),
            (10**51,      " sexdecillion"),
            (10**48,     " quindecillion"),
            (10**45, " quattuordecillion"),
            (10**42,      " tredecillion"),
            (10**39,      " duodecillion"),
            (10**36,       " undecillion"),
            (10**33,         " decillion"),
            (10**30,         " nonillion"),
            (10**27,         " octillion"),
            (10**24,        " septillion"),
            (10**21,        " sextillion"),
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


# as per PEP 263
_python_source_code_encoding_line_bytes_re = re.compile(b"^[ \t\f]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)")
_python_source_code_encoding_line_str_re   = re.compile( "^[ \t\f]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)")

# a "blank" line for PEP 263 purposes: whitespace, a comment, or
# nothing.  identical to tokenize.blank_re, which tokenize uses to
# decide whether line 2 may carry the magic coding comment.
_python_source_blank_line_bytes_re = re.compile(br'^[ \t\f]*(?:[#\r\n]|$)')
_python_source_blank_line_str_re   = re.compile( r'^[ \t\f]*(?:[#\r\n]|$)')


# BOMs were harvested from
#     https://en.wikipedia.org/wiki/Byte_order_mark#Byte-order_marks_by_encoding
# Some of these aren't supported (yet?) by Python.
# It's fine, we'll just flunk the encode lookup and fail.
#
# The signatures are sorted by length, longest first,
# because a shorter signature might be a prefix of a longer one.
# For example, the first two bytes of the BOM for utf-32-le
# are the same as the BOM for utf-16-le.

_bom_to_encoding = (
#   (BOM,                 length, encoding)

    (b"\x00\x00\xfe\xff", 4,      "utf-32-be"),
    (b"\x84\x31\x95\x33", 4,      "gb18030"),
    (b"\xdd\x73\x66\x73", 4,      "utf-ebcdic"),
    (b"\xff\xfe\x00\x00", 4,      "utf-32-le"),

    (b"\x0e\xfe\xff",     3,      "scsu"),
    (b"\x2b\x2f\x76",     3,      "utf-7"),
    (b"\xef\xbb\xbf",     3,      "utf-8"),
    (b"\xf7\x64\x4c",     3,      "utf-1"),
    (b"\xfb\xee\x28",     3,      "bocu-1"),

    (b"\xfe\xff",         2,      "utf-16-be"),
    (b"\xff\xfe",         2,      "utf-16-le"),
)


_valid_newline_values = {
    None:   None,
    '':     b'',
    '\n':   b'\n',
    '\r':   b'\r',
    '\r\n': b'\r\n',
    }

@export
def decode_python_script(script, *,
    newline=None,
    use_bom=True,
    use_source_code_encoding=True):
    """
    Correctly decodes a Python script from a bytes string.

    script should be a bytes object containing an encoded Python script.

    Returns a str containing the decoded Python script.

    By default, Python 3 scripts must be encoded using UTF-8.
    (This was established by PEP 3120.)

        https://en.wikipedia.org/wiki/UTF-8

    Python scripts are allowed to use other encodings, but when they do so
    they must explicitly specify what encoding they used.  Python defines
    two methods for scripts to specify their encoding; decode_python_script
    supports both.

    The first method uses a "byte order mark", aka "BOM". This is a sequence
    of bytes at the beginning of the file that indicate the file's encoding.

        https://en.wikipedia.org/wiki/Byte_order_mark

    If use_bom is true (the default), decode_python_script will
    recognize a BOM if present, and decode the file using the encoding
    specified by the BOM.  Note that decode_python_script removes the BOM
    when it decodes the file.

    The second method is called a "source code encoding", and it was defined
    in PEP 263.  This is a "magic comment" that must be one of the first two
    lines of the file:

        https://peps.python.org/pep-0263/

    If use_source_code_encoding is true (the default), decode_python_script
    will recognize a source code encoding magic comment, and use that to decode
    the file.  (decode_python_script leaves the magic comment in place.)

    If both these "use_" keyword-only parameters are true (the default),
    decode_python_script can handle either, both, or neither.  In this case,
    if script contains both a BOM and a source code encoding magic comment,
    the script will be decoded using the encoding specified by the BOM, and the
    source code encoding must agree with the BOM.

    decode_python_script also supports Python's "universal newlines" feature,
    using the same interface as Python's open() function.  decode_python_script
    accepts a newlines parameter, which may be None, '\\n', '\\r', or '\\r\\n'.
    If newlines is None (the default), b'\\r\\n' and b'\\r' in the script are
    converted to '\\n'.  If newlines is not None, no newline conversion is done.
    """
    s = script
    encoded = True

    if not newline in _valid_newline_values:
        raise ValueError(f"newline must be one of None, '', '\\n', '\\r', or '\\r\\n', not {newline!r}")

    ##
    ## stage 1: use_bom
    ##
    if use_bom:
        # the BOM comparison code relies on _bom_to_encoding
        # being sorted by length with longer BOMs first.
        candidate = script
        candidate_length = len(candidate)

        for bom, bom_length, bom_encoding in _bom_to_encoding:
            if candidate_length != bom_length:
                candidate = candidate[:bom_length]
            if candidate == bom:
                break
        else:
            candidate = bom_encoding = None

        assert (bom_encoding is None) or (isinstance(bom_encoding, str) and bom_encoding)
    else:
        bom_encoding = None

    if bom_encoding:
        try:
            s = script[len(bom):].decode(bom_encoding)
        except LookupError as e:
            message = str(e)
            assert "unknown encoding" in message
            raise UnicodeDecodeError(bom_encoding, script, 0, len(script), "unknown encoding") from None
        encoded = False

        encoding_re = _python_source_code_encoding_line_str_re
    else:
        encoding_re = _python_source_code_encoding_line_bytes_re
        newline = _valid_newline_values[newline]


    ##
    ## stage 2: source_code_encoding
    ##
    source_code_encoding = None

    if use_source_code_encoding:
        # speed tech:
        #   try to avoid splitting *all* the lines.
        #   we only care about the first two.
        for size in (128, 1024, 4096, None):
            if size is None:
                chunk = s
            else:
                chunk = s[:size]

            if newline:
                lines = chunk.split(newline, 2)
            else:
                lines = chunk.splitlines()
                lines = lines[:3]

            if len(lines) > 2:
                break

        # PEP 263, exactly as CPython's tokenize.detect_encoding
        # implements it: the magic comment must be on line 1 or
        # line 2; the first match wins; and line 2 is only
        # consulted if line 1 is blank or a comment line.
        if encoded:
            blank_re = _python_source_blank_line_bytes_re
        else:
            blank_re = _python_source_blank_line_str_re
        for line_number, line in enumerate(lines[:2]):
            match = encoding_re.match(line)
            if match:
                source_code_encoding = match.group(1)
                break
            if (not line_number) and (not blank_re.match(line)):
                # line 1 is real code: line 2 doesn't count.
                break

    if source_code_encoding is not None:
        assert source_code_encoding # the regular expression should ensure it's never empty
        if encoded:
            source_code_encoding = source_code_encoding.decode('ascii')

    if bom_encoding:
        # script used both a BOM and a source code encoding!  they better agree!
        # normalize both names through codecs, so spelling variants
        # agree ("utf8", "UTF_8", and "utf-8" are all the same
        # encoding)--and accept an endianness-unqualified magic
        # comment for an endian BOM (a "utf-16" comment agrees
        # with a utf-16-le BOM; the BOM's *job* is supplying the
        # endianness).
        if source_code_encoding:
            try:
                cookie_name = codecs.lookup(source_code_encoding).name
            except LookupError:
                raise UnicodeDecodeError(source_code_encoding, script, 0, len(script), "unknown encoding") from None
            bom_name = codecs.lookup(bom_encoding).name
            if not ((cookie_name == bom_name) or bom_name.startswith(cookie_name + '-')):
                raise UnicodeDecodeError(source_code_encoding, script, 0, len(script), "source code encoding line doesn't match BOM encoding")
        encoding = bom_encoding
    elif source_code_encoding:
        encoding = source_code_encoding
    else:
        encoding = "utf-8"

    # the moment of truth!
    # (well, unless we already decoded because of a BOM.)
    if encoded:
        try:
            s = script.decode(encoding)
        except LookupError as e:
            message = str(e)
            assert "unknown encoding" in message
            raise UnicodeDecodeError(encoding, script, 0, len(script), "unknown encoding") from None

    # all we need to do for universal newlines support:
    # convert \r\n and \r into \n
    if (newline is None) and ('\r' in s):
        s = s.replace('\r\n', '\n').replace('\r', '\n')

    return s


@export
class Pattern:
    """
    A drop-in replacement for re.Pattern that preserves str
    subclasses.

    Python's re module converts str subclasses to plain str when
    returning matched strings.  Pattern preserves the subclass:
    its methods return Pattern.Match objects whose strings are
    slices of the *original* string, so if you search or match
    against a big.string, the strings you get back are big.string
    slices, retaining their line and column information.

    Pattern supports the same interface as re.Pattern; see the
    Python documentation for the full API.  (Exceptions: sub,
    subn, and Match.expand construct new strings, so they return
    plain str/bytes.)
    """
    def __init__(self, s, flags=0):
        if not isinstance(s, (str, bytes)):
            raise TypeError(f's must be str or bytes, not {type(s).__name__}')
        if not isinstance(flags, int):
            raise TypeError(f'flags must be an int, not {type(flags).__name__}')
        self.s = s
        self.flags = flags

        self.pattern = re.compile(s, flags)

    def search(self, string, pos=0, endpos=sys.maxsize):
        m = self.pattern.search(string, pos, endpos)
        return m and self.Match(m, string)

    def match(self, string, pos=0, endpos=sys.maxsize):
        m = self.pattern.match(string, pos, endpos)
        return m and self.Match(m, string)

    def fullmatch(self, string, pos=0, endpos=sys.maxsize):
        m = self.pattern.fullmatch(string, pos, endpos)
        return m and self.Match(m, string)

    def split(self, string, maxsplit=sys.maxsize):
        result = []
        start = 0
        for count, m in enumerate(self.finditer(string), 1):
            end = m.start()
            result.append(string[start:end])

            # if the group doesn't exist, we get IndexError.
            # if the group exists but didn't match anything, m.group returns None.
            # if the group exists and matched something, we can get a span and
            #    fill from the original string object.
            try:
                i = 1
                while True:
                    group = m.group(i)
                    if group is None:
                        result.append(None)
                    else:
                        group_start, group_end = m.span(i)
                        result.append(string[group_start:group_end])
                    i += 1
            except IndexError:
                pass

            start = m.end()

            if count == maxsplit:
                break

        end = len(string)
        result.append(string[start:end])

        return result

    def finditer(self, string, pos=0, endpos=sys.maxsize):
        for m in self.pattern.finditer(string, pos, endpos):
            yield self.Match(m, string)

    def findall(self, string, pos=0, endpos=sys.maxsize):
        results = []
        for m in self.finditer(string, pos=pos, endpos=endpos):
            groups = []
            try:
                i = 1
                while True:
                    group = m.group(i)
                    if group is None:
                        groups.append(None)
                    else:
                        group_start, group_end = m.span(i)
                        groups.append(string[group_start:group_end])
                    i += 1
            except IndexError:
                pass
            if len(groups) == 0:
                groups = m.group(0)
            elif len(groups) == 1:
                groups = groups[0]
            else:
                groups = tuple(groups)
            results.append(groups)
        return results

    def sub(self, repl, string, count=0):
        # sorry, we can't honor the substring here
        return self.pattern.sub(repl, string, count)

    def subn(self, repl, string, count=0):
        # sorry, we can't honor the substring here
        return self.pattern.subn(repl, string, count)

    def __repr__(self):
        return self.pattern.__repr__()


    @BoundInnerClass
    class Match:
        """
        The Match object returned by Pattern's methods.  Wraps an
        re.Match; every matched string it returns is a slice of
        the original string, preserving str subclasses (like
        big.string).  Supports the same interface as re.Match.
        (Exception: expand constructs a new string, so it returns
        plain str/bytes.)
        """
        def __init__(self, pattern, match, string):
            self.pattern = self.re = pattern
            self.match = match
            self.string = string

            self.pos = match.pos
            self.endpos = match.endpos
            self.lastindex = match.lastindex
            self.lastgroup = match.lastgroup

        def __bool__(self):
            return True

        def expand(self, template):
            # sorry, can't honor the subclass here
            return self.match.expand(template)

        def group(self, *groups):
            if not groups:
                groups = (0,)

            results = self.match.group(*groups)
            if results is None:
                return results
            if len(groups) == 1:
                start, end = self.match.span(groups[0])
                return self.string[start:end]

            results2 = []
            for group, result in zip(groups, results):
                if result is None:
                    results2.append(None)
                    continue
                start, end = self.match.span(group)
                results2.append(self.string[start:end])

            return tuple(results2)

        def __getitem__(self, item):
            return self.group(item)

        def groups(self, default=None):
            results = []
            try:
                i = 1
                while True:
                    value = self.group(i)
                    if value is None:
                        value = default
                    results.append(value)
                    i += 1
            except IndexError:
                pass
            return tuple(results)

        def groupdict(self, default=None):
            result = {}
            for name, value in self.match.groupdict().items():
                if value is None:
                    value = default
                else:
                    value = self.group(name)
                result[name] = value
            return result

        def start(self, group=0):
            return self.match.start(group)

        def end(self, group=0):
            return self.match.end(group)

        def span(self, group=0):
            return self.match.span(group)

        def __repr__(self):
            return self.match.__repr__()


@export
def strip_indents(lines, *, tab_width=8, linebreaks=linebreaks):
    """
    Takes an iterable of lines, with or without linebreaks; strips
    the leading whitespace from each line and tracks the indent level.
    Yields 2-tuples of (depth, lstripped_line).

    depth is an integer, the ordinal number of times the lines
    were indented to reach the current indent.  Text at the leftmost
    column is at depth 0; if the line was indented three times,
    depth will be 3.

    Uses an intentionally simple algorithm.  Only understands tab and
    space characters as indent characters.  Internally detabs to spaces
    for consistency, using the tab_width passed in.

    Text can only dedent out to a previous indent.
    Raises IndentationError if there's an illegal dedent.

    Blank lines and empty lines have the indent level of the
    *next* non-blank line, or 0 if there are no subsequent
    non-blank lines.  If the line contains only whitespace,
    any trailing string of characters found in "linebreaks"
    will be preserved.  (If you don't want linebreak characters
    preserved, pass in None or an empty sequence for "linebreaks".)
    """
    depth = 0
    leadings = []

    # a "blank line" is either empty or only has whitespace.
    # blank lines get the indent of the *next* non-blank line,
    # or 0 if there are no following non-blank lines... which
    # means we need to buffer blank lines until we learn which
    # of those two cases this is.
    blank_lines = []

    first_line = True

    for line in lines:
        if first_line:
            first_line = False
            if isinstance(line, bytes):
                tab = b'\t'
                # we occluded the global "linebreaks" with our
                # parameter, so we test whether we still have the
                # default value by comparing to str_linebreaks,
                # which is the same object.  for bytes lines, the
                # default means the *bytes* linebreaks.  (this is
                # the same dance strip_line_comments does.)
                if linebreaks is str_linebreaks:
                    linebreaks = bytes_linebreaks
            else:
                tab = '\t'
            if linebreaks:
                linebreaks = frozenset(linebreaks)
        lstripped = line.lstrip()
        if not lstripped:
            if not linebreaks:
                line = line[0:0]
            else:
                # count the linebreak characters at the end of line,
                # and preserve them if any.  otherwise use line[0:0]
                # to represent the empty line.
                #
                # scan backwards by one-character *slices*: works
                # for both str and bytes (indexing a bytes yields
                # ints, which would never be in a set of bytes
                # strings), and counts a tally rather than an
                # index (an enumerate here used to be off by one
                # when the line was 100% linebreak characters,
                # emptying it instead of preserving it).
                count = 0
                for i in range(len(line) - 1, -1, -1):
                    if line[i:i+1] not in linebreaks:
                        break
                    count += 1
                if not count:
                    line = line[0:0]
                else:
                    line = line[len(line) - count:]

            blank_lines.append(line)
            continue

        # if we reach here, lstripped is not empty.
        if tab in line:
            line = line.expandtabs(tab_width)
        column_number = line.index(lstripped[0])

        if not column_number:
            # this line doesn't start with whitespace; text is at column 0.
            # outdent to zero.
            depth = 0
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
            depth -= 1
            while leadings:
                l = leadings[-1]
                if l >= column_number:
                    if l > column_number:
                        leadings.clear()
                    break
                leadings.pop()
                depth -= 1
            if not leadings:
                raise IndentationError(f"unindent doesn't match any outer indentation level")
            new_indent = False

        if new_indent:
            leadings.append(column_number)
            depth += 1

        if blank_lines:
            for line in blank_lines:
                yield (depth, line)
            blank_lines.clear()

        yield (depth, lstripped)

    # flush trailing blank lines
    if blank_lines:
        for line in blank_lines:
            yield 0, line


def strip_line_comments(lines, line_comment_splitter, quotes, multiline_quotes, escape, linebreaks, is_bytes):
    "The generator function returned by the public strip_line_comments function."
    state = None

    if is_bytes:
        def line_reverser(line):
            l = list(_iterate_over_bytes(line))
            l.reverse()
            return l
        empty = b''
    else:
        line_reverser = reversed
        empty = ''

    for line in lines:
        if quotes or multiline_quotes:
            i = split_quoted_strings(line, quotes, escape=escape, multiline_quotes=multiline_quotes, state=state)
        else:
            i = iter( ((empty, line, empty),) )

        # initialize these in case i never yields anything
        leading_quote = segment = trailing_quote = empty

        previous_lengths = 0
        offset = 0

        for leading_quote, segment, trailing_quote in i:
            offset += previous_lengths

            previous_lengths = len(leading_quote) + len(segment) + len(trailing_quote)

            if leading_quote:
                # this can be only one of two cases:
                # * quotes are balanced, in which case trailing_quote is true, and we might loop again
                # * quotes aren't balanced, in which case this is the last iteration and we handle it
                continue

            if state:
                # we're still in a quote from a previous line.
                # assert not leading_quote
                if trailing_quote:
                    state = None
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
            offset += len(leading)
            segment = line[:offset]

            if linebreaks:
                # preserve the linebreak characters
                # at the end of the original line, if any.
                count = 0
                for c in line_reverser(line):
                    if c not in linebreaks:
                        break
                    count += 1
                if count:
                    segment += line[len(line) - count:]

            line = segment
            break
        else:
            # we exhausted the loop.
            if leading_quote and not trailing_quote:
                if leading_quote not in multiline_quotes:
                    raise SyntaxError(f"unterminated quote marker {leading_quote}")
                state = leading_quote

        yield line

    if state:
        raise SyntaxError(f"unterminated quote marker {state}")

_strip_line_comments = strip_line_comments

@export
def strip_line_comments(lines, line_comment_markers, *,
    escape='\\', quotes=(), multiline_quotes=(), linebreaks=linebreaks):
    """
    Strips line comments from a sequence of lines.

    Line comments are substrings beginning with a special marker
    that mean the rest of the line should be ignored;
    strip_line_comments truncates the line at the
    beginning of the leftmost line comment marker.

    line_comment_markers should be an iterable of line comment
    marker strings.  These are strings that denote a "line comment",
    which is to say, a comment that starts at that marker and
    extends to the end of the line.

    lines should be an iterator of str (or big.string) objects
    representing each line.  If the lines end with linebreak
    characters, they will be preserved, even if a comment is
    stripped from the line.

    By default, quotes and multiline_quotes are both false,
    in which case strip_line_comments will truncate each
    line, starting at the leftmost comment marker, and yield
    the resulting line.  If the line doesn't contain any unquoted
    comment markers, strip_line_comments yields it unchanged.

    However, the syntax of the text you're parsing might support
    quoted strings, and comment marks in those quoted strings
    should be ignored.  strip_quoted_strings supports this
    too, with its escape, quotes, and multiline_quotes parameters.

    If quotes is true, it must be an iterable of quote marker
    strings, length 1 or more.  strip_line_comments will
    parse the line using big's split_quoted_strings function
    and ignore comment characters inside quoted strings.  Quoted
    strings may not span lines; if a line ends with an unterminated
    quoted string, strip_line_comments will raise a SyntaxError.

    If multiline_quotes is true, it must be an iterable of
    quote marker strings, length 1 or more.  Quoted strings
    enclosed in multiline quotes may span multiple lines;
    quoted strings enclosed in (conventional) quotes are not
    permitted to.  If the last line yielded by the upstream
    iterator ends with an unterminated multiline string,
    strip_line_comments will raise a SyntaxError.

    There must be no quote markers in common between quotes and
    multiline_quotes.

    If escape is true, it must be a string.  This string
    will "escape" (quote) quote markers, either multiline
    or non-multiline, as per backslash inside strings in Python.
    The default value for escape is "\\".

    strip_line_comments handles comment characters anywhere
    in the line, although it can ignore comments inside quoted
    strings.  It may truncate the line, but still always yields
    the line.
    """

    # check line_comment_markers.  normalize to a tuple first,
    # so any iterable works--sets, generators, etc.
    original_line_comment_markers = line_comment_markers
    if isinstance(line_comment_markers, bytes):
        line_comment_markers = tuple(_iterate_over_bytes(line_comment_markers))
    elif line_comment_markers is not None:
        line_comment_markers = tuple(line_comment_markers)
    if not line_comment_markers:
        bad_value = True
    else:
        first = line_comment_markers[0]
        is_bytes = isinstance(first, bytes)
        bad_value = not (is_bytes or isinstance(first, str))
    if bad_value:
        raise ValueError(f"line comment markers must be str, bytes, or a non-empty iterable of str or bytes, not {original_line_comment_markers!r}")

    # call split_quoted_string to validate quotes, multiline_quotes, and escape, if specified.
    not_empty = quotes or multiline_quotes
    if not_empty:
        # if not_empty is not bytes, it's safe to index into
        if isinstance(not_empty, bytes) or isinstance(not_empty[0], bytes):
            test_text = b'x'
        else:
            test_text = 'x'

        # don't iterate! just throw the iterator away.
        # split_quoted_strings validates the inputs immediately,
        # and there's no point in calling the iterator.
        split_quoted_strings(test_text, quotes=quotes, multiline_quotes=multiline_quotes, escape=escape)

    # we occluded the global "linebreaks", so we test here
    # to see if we have the default value by comparing to "str_linebreaks"
    # which is the same object.
    if is_bytes and (linebreaks is str_linebreaks):
        linebreaks = bytes_linebreaks

    line_comment_pattern = __separators_to_re(line_comment_markers, separators_is_bytes=is_bytes, separate=True, keep=True)
    line_comment_splitter = re.compile(line_comment_pattern).split

    return _strip_line_comments(lines, line_comment_splitter, quotes, multiline_quotes, escape, linebreaks, is_bytes)


mm()
