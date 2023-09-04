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

import enum
import functools
import itertools
from itertools import zip_longest
from .itertools import PushbackIterator
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

    if isinstance(s, bytes):
        empty_string = b''
        extension = (None, b'')
    else:
        empty_string = ''
        extension = (None, '')

    if not isinstance_re_pattern(pattern):
        pattern = re.compile(pattern, flags=flags)

    # optimized fast path for the most frequent use case
    if count == 1:
        match = pattern.search(s)
        if not match:
            return (s, None, empty_string)
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

@_export
def reversed_re_finditer(pattern, string, flags=0):
    """
    An iterator.  Behaves almost identically to the Python
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
        # if we sort the list, the last element will be the correct
        # last match in "reverse" order.  see
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
    return reversed_re_finditer(pattern, string)


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
    if isinstance(s, bytes):
        empty_string = b''
        extension = (b'', None)
    else:
        empty_string = ''
        extension = ('', None)

    # optimized fast path for the most frequent use case
    if count == 1:
        matches_iterator = reversed_re_finditer(pattern, s, flags)
        try:
            match = next(matches_iterator)
            before, separator, after = s.rpartition(match.group(0))
            return (before, match, after)
        except StopIteration:
            return (empty_string, None, s)

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


# a list of all unicode whitespace characters known to Python
# (note: we check this list is correct and complete in a unit test)
_export_name('whitespace')
whitespace = (
    '\t'    , #     9 0x0009 - tab
    '\n'    , #    10 0x000a - newline
    '\x0b'  , #    11 0x000b - vertical tab
    '\x0c'  , #    12 0x000c - form feed
    '\r'    , #    13 0x000d - carriage return
    '\x1c'  , #    28 0x001c - file separator
    '\x1d'  , #    29 0x001d - group separator
    '\x1e'  , #    30 0x001e - record separator
    '\x1f'  , #    31 0x001f - unit separator
    ' '     , #    32 0x0020 - space
    '\x85'  , #   133 0x0085 - next line
    '\xa0'  , #   160 0x00a0 - non-breaking space
    '\u1680', #  5760 0x1680 - ogham space mark
    '\u2000', #  8192 0x2000 - en quad
    '\u2001', #  8193 0x2001 - em quad
    '\u2002', #  8194 0x2002 - en space
    '\u2003', #  8195 0x2003 - em space
    '\u2004', #  8196 0x2004 - three-per-em space
    '\u2005', #  8197 0x2005 - four-per-em space
    '\u2006', #  8198 0x2006 - six-per-em space
    '\u2007', #  8199 0x2007 - figure space
    '\u2008', #  8200 0x2008 - punctuation space
    '\u2009', #  8201 0x2009 - thin space
    '\u200a', #  8202 0x200a - hair space
    '\u2028', #  8232 0x2028 - line separator
    '\u2029', #  8233 0x2029 - paragraph separator
    '\u202f', #  8239 0x202f - narrow no-break space
    '\u205f', #  8287 0x205f - medium mathematical space
    '\u3000', # 12288 0x3000 - ideographic space

    '\r\n'  , # bonus! the classic DOS newline sequence!
    )

# this omits the DOS newline sequence '\r\n'
_export_name('whitespace_without_dos')
whitespace_without_dos = tuple(s for s in whitespace if s != '\r\n')

_export_name('newlines')
newlines = (
    '\n'    , #   10 0x000a - newline
    '\x0b'  , #   11 0x000b - vertical tab
    '\x0c'  , #   12 0x000c - form feed
    '\r'    , #   13 0x000d - carriage return
    '\x1c'  , #   28 0x001c - file separator
    '\x1d'  , #   29 0x001d - group separator
    '\x1e'  , #   30 0x001e - record separator
    '\x85'  , #  133 0x0085 - next line
    '\u2028', # 8232 0x2028 - line separator
    '\u2029', # 8233 0x2029 - paragraph separator

    '\r\n'  , # the classic DOS newline sequence

    # what about '\n\r'?
    # sorry, Acorn and RISC OS users, you'll have to add this yourselves.
    # I'm worried it would cause bugs with a malformed DOS newline.
    )

# this omits the DOS convention '\r\n'
_export_name('newlines_without_dos')
newlines_without_dos = tuple(s for s in newlines if s != '\r\n')

def _cheap_encode_iterable_of_strings(iterable, encoding='ascii'):
    a = []
    # all I'm really doing with the try/accept
    # block is stopping the loop for the ascii
    # encoding once we hit characters > 127.
    # since we're sorted, by the time we hit it,
    # we'll have already handled all the ascii
    # characters (if we're encoding for ascii).
    try:
        for c in iterable:
            a.append(c.encode(encoding))
    except UnicodeEncodeError:
        pass
    return type(iterable)(a)

# use these with multisplit if your bytes strings are encoded as ascii.
_export_name('ascii_whitespace')
ascii_whitespace = _cheap_encode_iterable_of_strings(whitespace, "ascii")
_export_name('ascii_whitespace_without_dos')
ascii_whitespace_without_dos = tuple(s for s in ascii_whitespace if s != b'\r\n')
_export_name('ascii_newlines')
ascii_newlines   = _cheap_encode_iterable_of_strings(newlines,   "ascii")
_export_name('ascii_newlines_without_dos')
ascii_newlines_without_dos = tuple(s for s in ascii_newlines if s != b'\r\n')

# use these with multisplit if your bytes strings are encoded as utf-8.
_export_name('utf8_whitespace')
utf8_whitespace = _cheap_encode_iterable_of_strings(whitespace, "utf-8")
_export_name('utf8_whitespace_without_dos')
utf8_whitespace_without_dos = tuple(s for s in utf8_whitespace if s != b'\r\n')
_export_name('utf8_newlines')
utf8_newlines   = _cheap_encode_iterable_of_strings(newlines,   "utf-8")
_export_name('utf8_newlines_without_dos')
utf8_newlines_without_dos =  tuple(s for s in utf8_newlines if s != b'\r\n')

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
# reverse=True.  this is a minor speed optimization, but also it
# helps a lot with the lrucache for _separators_to_re.
#
# we test that these cached versions are correct in tests/test_text.py.
#
_reversed_utf8_whitespace_without_dos = _multisplit_reversed(utf8_whitespace_without_dos)
_reversed_utf8_newlines_without_dos =   _multisplit_reversed(utf8_newlines_without_dos)

_reversed_builtin_separators = {
    whitespace: whitespace_without_dos + ('\n\r',),
    whitespace_without_dos: whitespace_without_dos,

    newlines: newlines_without_dos + ("\n\r",),
    newlines_without_dos: newlines_without_dos,

    ascii_whitespace: ascii_whitespace_without_dos + (b"\n\r",),
    ascii_whitespace_without_dos: ascii_whitespace_without_dos,

    ascii_newlines: ascii_newlines_without_dos + (b"\n\r",),
    ascii_newlines_without_dos: ascii_newlines_without_dos,

    utf8_whitespace: _reversed_utf8_whitespace_without_dos + (b"\n\r",),
    utf8_whitespace_without_dos: _reversed_utf8_whitespace_without_dos,

    utf8_newlines: _reversed_utf8_newlines_without_dos + (b"\n\r",),
    utf8_newlines_without_dos: _reversed_utf8_newlines_without_dos,
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

    # we can sidestep the hashability test of _separators_to_re,
    # separators is guaranteed to always a tuple at this point
    pattern = __separators_to_re(separators, is_bytes, separate=False, keep=False)

    start = 0
    end = len(s)
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

    separators should be an iterable of str or bytes, matching s.

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
                raise TypeError("separators must be either None or an iterable of objects the same type as s")
            check_separators = True
        empty = b''
        s_type = bytes
    else:
        if separators_is_bytes:
            raise TypeError("separators must be either None or an iterable of objects the same type as s")
        check_separators = True
        empty = ''
        s_type = str

    if separators is None:
        separators = ascii_whitespace if is_bytes else whitespace
        check_separators = False
    elif not separators:
        raise ValueError("separators must be either None or an iterable of objects the same type as s")

    # check_separators is True if separators isn't str or bytes
    # or something we split ourselves.
    if check_separators:
        if not hasattr(separators, '__iter__'):
            raise TypeError("separators must be either None or an iterable of objects the same type as s")
        for o in separators:
            if not isinstance(o, s_type):
                raise TypeError("separators must be either None or an iterable of objects the same type as s")

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
            # this will make us exit early, just a few lines down from here.
            maxsplit = 0

    def multisplit(s, separators, keep, maxsplit, reverse, separate, strip):
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
        # print("PATTERN", pattern, f"{separators_to_re_keep=} {separate=}")

        l = re.split(pattern, s, re_split_maxsplit)
        assert l
        # print("S", repr(s), "L", l, f"{re_split_maxsplit=}")

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

        if reverse:
            l = _multisplit_reversed(l, 'l')
            l.reverse()

        if not keep:
            l.reverse()
            while l:
                yield l.pop()
            return

        # from here on out, we're 'keep'-ing the separator strings.
        # (we're returning the separator strings in one form or another.)

        if keep == ALTERNATING:
            l.reverse()
            while l:
                yield l.pop()
            return

        if (len(l) % 2) == 1:
            l.append(empty)

        previous = None
        l.reverse()
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

    return multisplit(s, separators, keep, maxsplit, reverse, separate, strip)


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


# I think that, for our purposes,
#     ` (the "back-tick" character U+0060)
# is *not* an apostrophe.  it's a diacritical
# used to modify a letter, rather than a
# separator used to separate letters.
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


_invalid_state = "_invalid_state"
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
    a replacement string consisting of a single space character.

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
        default_separators = ascii_whitespace_without_dos
        s_type = bytes
    else:
        empty = ''
        default_replacement = ' '
        default_separators = whitespace_without_dos
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
    if (   (separators is whitespace_without_dos)
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


@_export
def split_quoted_strings(s, quotes=None, *, triple_quotes=True, backslash=None):
    """
    Splits s into quoted and unquoted segments.

    s can be either str or bytes.

    quotes is an iterable of quote separators, either str or bytes matching s.
    Note that split_quoted_strings only supports quote *characters*, as in,
    each quote separator must be exactly one character long.

    Returns an iterator yielding 2-tuples:
        (is_quoted, segment)
    where segment is a substring of s, and is_quoted is true if the segment is
    quoted.  Joining all the segments together recreates s.

    If triple_quotes is true, supports "triple-quoted" strings like Python.

    If backslash is a character, this character will quoting characters inside
    a quoted string, like the backslash character inside strings in Python.

    You can pass in an instance of a subclass of bytes or str
    for s and quotes, but the base class for both must be
    the same (str or bytes).  split_quoted_strings will only
    return str or bytes objects.
    """
    if isinstance(s, bytes):
        empty = b''
        if quotes is None:
            quotes=(b'"', b"'")
        if backslash is None:
            backslash = b'\\'
        i = _iterate_over_bytes(s)
    else:
        empty = ''
        if quotes is None:
            quotes=('"', "'")
        if backslash is None:
            backslash = '\\'
        i = s
    empty_join = empty.join

    i = PushbackIterator(i)
    in_quote = None
    in_triple_quote = False
    in_backslash = False
    text = []
    for c in i:
        if not in_quote:
            # encountered character while not in quoted string.
            if c not in quotes:
                # general case. append unquoted character to our unquoted string.
                text.append(c)
                continue
            if not triple_quotes:
                # triple quotes are off, encountered quote.
                # flush unquoted string, start quoted string.
                if text:
                    yield False, empty_join(text)
                    text.clear()
                text.append(c)
                in_quote = c
                continue
            # scan for triple quotes.
            c2 = next(i)
            if c2 != c:
                # only a single quote mark. flush unquoted string, start quoted string.
                i.push(c2)
                if text:
                    yield False, empty_join(text)
                    text.clear()
                text.append(c)
                in_quote = c
                continue
            c3 = i.next(None)
            if c3 != c:
                # two quotes in a row, but not three.
                # flush unquoted string, emit empty quoted string.
                if text:
                    yield False, empty_join(text)
                    text.clear()
                yield True, c*2
                if c3 is not None:
                    i.push(c3)
                continue
            # triple quoted string.
            # flush unquoted string, start triple quoted string.
            if text:
                yield False, empty_join(text)
                text.clear()
            text.append(c*3)
            in_quote = c
            in_triple_quote = c
            continue

        # handle quoted string
        if in_backslash:
            # previous character was a backslash.
            # append this character no matter what it is.
            text.append(c)
            in_backslash = False
            continue
        if c == backslash:
            # encountered backslash character.
            # set flag so we append the next character,
            # no matter what it is.
            in_backslash = True
            text.append(c)
            continue
        if c != in_quote:
            # character doesn't match our quote marker.
            # append to our quoted string.
            text.append(c)
            continue
        if not in_triple_quote:
            # we found our quote mark, and we're only
            # in single quotes (not triple quotes).
            # finish and emit the quoted string,
            # and return to unquoted mode.
            text.append(c)
            yield True, empty_join(text)
            text.clear()
            in_quote = False
            continue
        # we're in a triple-quoted string,
        # and found one of our quote marks.
        # scan to see if we got three in a row.
        c2 = i.next(None)
        c3 = i.next(None)
        if c == c2 == c3:
            # we found triple quotes.
            # finish and emit the triple-quoted string,
            # and return to unquoted mode.
            text.append(c*3)
            yield True, empty_join(text)
            text.clear()
            in_triple_quote = in_quote = False
            continue
        # didn't find triple quotes.  append the single
        # quote mark to our quoted string and push the
        # other two characters back onto the iterator.
        text.append(c)
        if c2 is not None:
            if c3 is not None:
                i.push(c3)
            i.push(c2)

    # flush the remainder of the string we were building,
    # in whatever condition it's in.
    if text:
        yield in_quote, empty_join(text)


@_export
class Delimiter:
    """
    Class representing a delimiter for parse_delimiters.

    open is the opening delimiter character, can be str or bytes, must be length 1.
    close is the closing delimiter character, must be the same type as open, and length 1.
    backslash is a boolean: when inside this delimiter, can you escape delimiters
       with a backslash?  (You usually can inside single or double quotes.)
    nested is a boolean: must other delimiters nest in this delimiter?
       (Delimiters don't usually need to be nested inside single and double quotes.)
    """
    def __init__(self, open, close, *, backslash=False, nested=True):
        if isinstance(open, bytes):
            t = bytes
        else:
            t = str
        if not (isinstance(open, t) and isinstance(close, t)):
            raise TypeError(f"open={open!r} and close={close!r}, they must be the same type, either str or bytes")

        self.open = open
        self.close = close
        self.backslash = backslash
        self.nested = nested

    def __repr__(self): # pragma: no cover
        return f"Delimiter(open={self.open!r}, close={self.close!r}, backslash={self.backslash}, nested={self.nested})"

delimiter_parentheses = "()"
_export_name('delimiter_parentheses')

delimiter_square_brackets = "[]"
_export_name('delimiter_square_brackets')

delimiter_curly_braces = "{}"
_export_name('delimiter_curly_braces')

delimiter_angle_brackets = "<>"
_export_name('delimiter_angle_brackets')

delimiter_single_quote = Delimiter("'", "'", backslash=True, nested=False)
_export_name('delimiter_single_quote')

delimiter_double_quotes = Delimiter('"', '"', backslash=True, nested=False)
_export_name('delimiter_double_quotes')

parse_delimiters_default_delimiters = (
    delimiter_parentheses,
    delimiter_square_brackets,
    delimiter_curly_braces,
    delimiter_single_quote,
    delimiter_double_quotes,
    )
_export_name('parse_delimiters_default_delimiters')

parse_delimiters_default_delimiters_bytes = (
    b'()',
    b'[]',
    b'{}',
    Delimiter(b"'", b"'", backslash=True, nested=False),
    Delimiter(b'"', b'"', backslash=True, nested=False),
    )
_export_name('parse_delimiters_default_delimiters_bytes')


# break the rules
_base_delimiter = Delimiter('a', 'b')
_base_delimiter.open = _base_delimiter.close = None

@_export
def parse_delimiters(s, delimiters=None):
    """
    Parses a string containing nesting delimiters.
    Raises an exception if mismatched delimiters are detected.

    s may be str or bytes.

    delimiters may be either None or an iterable containing
    either Delimiter objects or objects matching s (str or bytes).
    Entries in the delimiters iterable which are str or bytes
    should be exactly two characters long; these will be used
    as the open and close arguments for a new Delimiter object.

    If delimiters is None, parse_delimiters uses a default
    value matching these pairs of delimiters:
        () [] {} "" ''
    The quote mark delimiters enable backslash quoting and disable nesting.

    Yields 3-tuples containing strings:
        (text, open, close)
    where text is the text before the next opening or closing delimiter,
    open is the trailing opening delimiter,
    and close is the trailing closing delimiter.
    At least one of these three strings will always be non-empty.
    If open is non-empty, close will be empty, and vice-versa.
    If s does not end with a closing delimiter, in the final tuple
    yielded, both open and close will be empty strings.

    You can only specify a particular character as an opening delimiter
    once, though you may reuse a particular character as a closing
    delimiter multiple times.
    """
    if isinstance(s, bytes):
        s_type = bytes
        if delimiters is None:
            delimiters = parse_delimiters_default_delimiters_bytes
        backslash_character = b'\\'
        disallowed_delimiters = backslash_character
        empty = b''
    else:
        s_type = str
        if delimiters is None:
            delimiters = parse_delimiters_default_delimiters
        backslash_character = '\\'
        disallowed_delimiters = backslash_character
        empty = ''

    if not delimiters:
        raise ValueError("invalid delimiters")
    # convert
    delimiters2 = []
    for d in delimiters:
        if isinstance(d, Delimiter):
            delimiters2.append(d)
            continue
        if isinstance(d, s_type):
            if not len(d) == 2:
                raise ValueError(f"illegal delimiter string {d!r}, must be 2 characters long")
            delimiters2.append(Delimiter(d[0:1], d[1:2]))
            continue
        raise TypeError(f"invalid delimiter {d!r}")

    delimiters = delimiters2
    # early-detect errors

    # scan for disallowed
    delimiter_characters = {d.open for d in delimiters} | {d.close for d in delimiters}
    disallowed = {disallowed_delimiters}
    illegal_delimiters = disallowed & delimiter_characters
    if illegal_delimiters:
        raise ValueError("illegal delimiters used: " + "".join(illegal_delimiters))

    # closers is a set of closing delimiters *only*.
    # if open and close delimiters are the same (e.g. quote marks)
    # it shouldn't go in closers.
    seen = set()
    repeated = []
    closers = set()
    for d in delimiters:
        if d.open in seen:
            repeated.append(d.open)
        seen.add(d.open)
        if d.close != d.open:
            closers.add(d.close)

    if repeated:
        raise ValueError("these opening delimiters were used multiple times: " + " ".join(repeated))

    def parse_delimiters(s, delimiters):
        open_to_delimiter = {d.open: d for d in delimiters}

        text = []
        append = text.append
        def flush(open, close):
            s = empty.join(text)
            text.clear()
            assert s or open or close
            return s, open, close

        # d stores the *current* delimiter
        # d is not in stack.
        d = _base_delimiter
        stack = []
        backslash = d.backslash
        nested = d.nested
        close = None
        quoted = False

        for i, c in enumerate(_iterate_over_bytes(s)):
            if quoted:
                append(c)
                quoted = False
                continue
            if c == close:
                yield flush(empty, c)
                d = stack.pop()
                backslash = d.backslash
                nested = d.nested
                close = d.close
                continue
            if nested:
                if c in closers:
                    # this is a closing delimiter,
                    # but it doesn't match.
                    # (if it did, we'd have handled it
                    #  in "if c == close" above.)
                    raise ValueError(f"mismatched closing delimiter at s[{i}]: expected {close}, got {c}")
                next_d = open_to_delimiter.get(c)
                if next_d:
                    yield flush(c, empty)
                    stack.append(d)
                    d = next_d
                    backslash = d.backslash
                    nested = d.nested
                    close = d.close
                    continue
            if backslash and (c == backslash_character):
                quoted = True
            append(c)

        if len(stack):
            stack.pop(0)
            stack.append(d)
            raise ValueError("s does not close all opened delimiters, needs " + " ".join(d.close for d in reversed(stack)))

        if text:
            yield flush(empty, empty)

    return parse_delimiters(s, delimiters)



@_export
class LineInfo:
    """
    The second object yielded by a lines iterator,
    containing metadata about the line.
    You can add your own fields by passing them in
    via **kwargs; you can also add new attributes
    or modify existing attributes as needed from
    inside a "lines modifier" function.
    """
    def __init__(self, line, line_number, column_number, **kwargs):
        if not isinstance(line, (str, bytes)):
            raise TypeError("line must be str or bytes")
        if not isinstance(line_number, int):
            raise TypeError("line_number must be int")
        if not isinstance(column_number, int):
            raise TypeError("column_number must be int")
        self.line = line
        self.line_number = line_number
        self.column_number = column_number
        self.__dict__.update(kwargs)

    def __repr__(self):
        names = list(self.__dict__)
        priority_names = ['line', 'line_number', 'column_number']
        fields = []
        for name in priority_names:
            names.remove(name)
        names.sort()
        names = priority_names + names
        for name in names:
            fields.append(f"{name}={getattr(self, name)!r}")
        text = ", ".join(fields)
        return f"LineInfo({text})"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and (other.__dict__ == self.__dict__)


@_export
class lines:
    def __init__(self, s, separators=None, *, line_number=1, column_number=1, tab_width=8, **kwargs):
        """
        A "lines iterator" object.  Splits s into lines, and iterates yielding those lines.

        "s" can be str, bytes, or any iterable of str or bytes.

        If s is neither str nor bytes, s must be an iterable;
        lines yields successive elements of s as lines.  All objects
        yielded by this iterable should be homogeneous, either str or bytes.

        If s is str or bytes, and separators is None, lines
        will split s at line boundaries and yield those lines,
        including empty lines.  If separators is not None,
        it must be an iterable of strings of the same type as s;
        lines will split s using multisplit.

        When iterated over, yields 2-tuples:
            (info, line)

        info is a LineInfo object, which contains three fields by default:
            * line - the original line, never modified
            * line_number - the line number of this line, starting at the
              line_number passed in and adding 1 for each successive line
            * column_number - the column this line starts on,
              starting at the column_number passed in, and adjusted when
              characters are removed from the beginning of line

        tab_width is not used by lines itself, but is stored internally and
        may be used by other lines modifier functions
        (e.g. lines_convert_tabs_to_spaces, lines_strip_indent). Similarly,
        all keyword arguments passed in via kwargs are stored internally
        and can be accessed by user-defined lines modifier functions.

        You can pass in an instance of a subclass of bytes or str
        for s and elements of separators, but the base class
        for both must be the same (str or bytes).  lines will
        only yield str or bytes objects.

        Composable with all the lines_ modifier functions in the big.text module.
        """
        if not isinstance(line_number, int):
            raise TypeError("line_number must be int")
        if not isinstance(column_number, int):
            raise TypeError("column_number must be int")
        if not isinstance(tab_width, int):
            raise TypeError("tab_width must be int")

        is_bytes = isinstance(s, bytes)
        is_str = isinstance(s, str)
        if is_bytes or is_str:
            if not separators:
                separators = newlines if is_str else ascii_newlines
            i = multisplit(s, separators, keep=False, separate=True, strip=False)
        else:
            i = iter(s)
            is_bytes = None

        self.s = s
        self.separators = separators
        self.line_number = line_number
        self.column_number = column_number
        self.tab_width = tab_width
        self.s_is_bytes = is_bytes

        self.i = i

        self.__dict__.update(kwargs)

    def __iter__(self):
        return self

    def __next__(self):
        line = next(self.i)
        if self.s_is_bytes is None:
            self.s_is_bytes = isinstance(line, bytes)
        return_value = (LineInfo(line, self.line_number, self.column_number), line)
        self.line_number += 1
        return return_value

@_export
def lines_rstrip(li):
    """
    A lines modifier function.  Strips trailing whitespace from the
    lines of a "lines iterator".

    Composable with all the lines_ modifier functions in the big.text module.
    """
    for info, line in li:
        yield (info, line.rstrip())

@_export
def lines_strip(li):
    """
    A lines modifier function.  Strips leading and trailing whitespace
    from the lines of a "lines iterator".

    If lines_strip removes leading whitespace from a line, it adds
    a field to the associated LineInfo object:
      * leading - the leading whitespace string that was removed

    Composable with all the lines_ modifier functions in the big.text module.
    """
    for info, line in li:
        lstripped = line.lstrip()
        if not lstripped:
            line = lstripped
        else:
            original_leading = line[:len(line) - len(lstripped)]
            if original_leading:
                leading = original_leading.expandtabs(li.tab_width)
                info.column_number += len(leading)
                line = lstripped.rstrip()
                info.leading = original_leading

        yield (info, line)

@_export
def lines_filter_comment_lines(li, comment_separators):
    """
    A lines modifier function.  Filters out comment lines from the
    lines of a "lines iterator".  Comment lines are lines whose first
    non-whitespace characters appear in the iterable of
    comment_separators strings passed in.

    What's the difference between lines_strip_comments and
    lines_filter_comment_lines?
      * lines_filter_comment_lines only recognizes lines that
        *start* with a comment separator (ignoring leading
        whitespace).  Also, it filters out those lines
        completely, rather than modifying the line.
      * lines_strip_comments handles comment characters
        anywhere in the line, although it can ignore
        comments inside quoted strings.  It truncates the
        line but still always yields the line.

    Composable with all the lines_ modifier functions in the big.text module.
    """
    if not comment_separators:
        raise ValueError("illegal comment_separators")

    if isinstance(comment_separators, bytes):
        comment_separators = _iterate_over_bytes(comment_separators)
        comment_separators_is_bytes = True
    else:
        comment_separators_is_bytes = isinstance(comment_separators[0], bytes)
    comment_separators = tuple(comment_separators)

    comment_pattern = _separators_to_re(comment_separators, comment_separators_is_bytes, separate=False, keep=False)
    comment_re = re.compile(comment_pattern)

    def lines_filter_comment_lines(li, comment_re):
        for info, line in li:
            s = line.lstrip()
            if comment_re.match(s):
                continue
            yield (info, line)
    return lines_filter_comment_lines(li, comment_re)


@_export
def lines_containing(li, s, *, invert=False):
    """
    A lines modifier function.  Only yields lines
    that contain s.  (Filters out lines that
    don't contain s.)

    If invert is true, returns the opposite--
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

@_export
def lines_grep(li, pattern, *, invert=False, flags=0):
    """
    A lines modifier function.  Only yields lines
    that match the regular expression pattern.
    (Filters out lines that don't match pattern.)

    pattern can be str, bytes, or an re.Pattern object.
    If pattern is not an re.Pattern object, it's compiled
    with re.compile(pattern, flags=flags).

    If invert is true, returns the opposite--
    filters out lines that match pattern.

    Composable with all the lines_ functions from the big.text module.

    (In older versions of Python, re.Pattern was a private type called
    re._pattern_type.)
    """
    if not isinstance_re_pattern(pattern):
        pattern = re.compile(pattern, flags=flags)
    search = pattern.search

    if invert:
        def lines_grep(li, search):
            for t in li:
                if not search(t[1]):
                    yield t
            return
        return lines_grep(li, search)

    def lines_grep(li, search):
        for t in li:
            if search(t[1]):
                yield t
    return lines_grep(li, search)

@_export
def lines_sort(li, *, reverse=False):
    """
    A lines modifier function.  Sorts all
    input lines before yielding them.

    Lines are sorted lexicographically,
    from lowest to highest.
    If reverse is true, lines are sorted
    from highest to lowest.

    Composable with all the lines_ modifier functions in the big.text module.
    """
    lines = list(li)
    lines.sort(key=lambda t:t[1], reverse=reverse)
    yield from iter(lines)

@_export
def lines_strip_comments(li, comment_separators, *, quotes=('"', "'"), backslash='\\', rstrip=True, triple_quotes=True):
    """
    A lines modifier function.  Strips comments from the lines
    of a "lines iterator".  Comments are substrings that indicate
    the rest of the line should be ignored; lines_strip_comments
    truncates the line at the beginning of the leftmost comment
    separator.

    If rstrip is true (the default), lines_strip_comments calls
    the rstrip() method on line after it truncates the line.

    If quotes is true, it must be an iterable of quote characters.
    (Each quote character MUST be a single character.)
    lines_strip_comments will parse the line and ignore comment
    characters inside quoted strings.  If quotes is false,
    quote characters are ignored and line_strip_comments will
    truncate anywhere in the line.

    backslash and triple_quotes are passed in to
    split_quoted_string, which is used internally to detect
    the quoted strings in the line.

    Sets a new field on the associated LineInfo object for every line:
      * comment - the comment stripped from the line, if any.
        if no comment was found, "comment" will be an empty string.

    What's the difference between lines_strip_comments and
    lines_filter_comment_lines?
      * lines_filter_comment_lines only recognizes lines that
        *start* with a comment separator (ignoring leading
        whitespace).  Also, it filters out those lines
        completely, rather than modifying the line.
      * lines_strip_comments handles comment characters
        anywhere in the line, although it can ignore
        comments inside quoted strings.  It truncates the
        line but still always yields the line.

    Composable with all the lines_ modifier functions in the big.text module.
    """
    if not comment_separators:
        raise ValueError("illegal comment_separators")

    if isinstance(comment_separators, bytes):
        comment_separators = _iterate_over_bytes(comment_separators)
        comment_separators_is_bytes = True
    else:
        comment_separators_is_bytes = isinstance(comment_separators[0], bytes)
    comment_separators = tuple(comment_separators)

    if comment_separators_is_bytes:
        empty = b''
    else:
        empty = ''
    empty_join = empty.join

    comment_pattern = __separators_to_re(comment_separators, separators_is_bytes=comment_separators_is_bytes, separate=True, keep=True)
    re_comment = re.compile(comment_pattern)
    split = re_comment.split


    def lines_strip_comments(li, split, quotes, backslash, rstrip, triple_quotes):
        for info, line in li:
            if quotes:
                i = split_quoted_strings(line, quotes, backslash=backslash, triple_quotes=triple_quotes)
            else:
                i = ((False, line),)
            segments = []
            append = segments.append
            comment = []
            for is_quoted, segment in i:
                if comment:
                    comment.append(segment)
                    continue
                if is_quoted:
                    append(segment)
                    continue
                fields = split(segment, maxsplit=1)
                leading = fields[0]
                if len(fields) == 1:
                    append(leading)
                    continue
                # found a comment marker in an unquoted segment!
                if rstrip:
                    leading = leading.rstrip()
                append(leading)
                comment = fields[1:]

            info.comment = empty_join(comment)
            line = empty_join(segments)
            yield (info, line)
    return lines_strip_comments(li, split, quotes, backslash, rstrip, triple_quotes)

@_export
def lines_convert_tabs_to_spaces(li):
    """
    A lines modifier function.  Converts tabs to spaces for the lines
    of a "lines iterator", using the tab_width passed in to lines.

    Composable with all the lines_ modifier functions in the big.text module.
    """
    for info, line in li:
        yield (info, line.expandtabs(li.tab_width))


@_export
def lines_strip_indent(li):
    """
    A lines modifier function.  Automatically measures and strips indents.

    Sets two new fields on the associated LineInfo object for every line:
      * indent - an integer indicating how many indents it's observed
      * leading - the leading whitespace string that was removed
    Also updates LineInfo.column_number as needed.

    Uses an intentionally simple algorithm.
    Only understands tab and space characters as indent characters.
    Internally detabs to spaces first for consistency, using the
    tab_width passed in to lines.

    You can only dedent out to a previous indent.
    Raises IndentationError if there's an illegal dedent.

    Composable with all the lines_ functions from the big.text module.
    """
    indent = 0
    leadings = []
    for info, line in li:
        lstripped = line.lstrip()
        original_leading = line[:len(line) - len(lstripped)]
        leading = original_leading.expandtabs(li.tab_width)
        len_leading = len(leading)
        # print(f"{leadings=} {line=} {leading=} {len_leading=}")
        if leading.rstrip(' '):
            raise ValueError(f"lines_strip_indent can't handle leading whitespace character {leading[0]!r}")
        if not leading:
            indent = 0
            leadings.clear()
            new_indent = False
        elif not leadings:
            new_indent = True
        elif leadings[-1] == len_leading:
            new_indent = False
        elif len_leading > leadings[-1]:
            new_indent = True
        else:
            # not equal, not greater than... must be less than!
            new_indent = False
            assert leadings
            leadings.pop()
            indent -= 1
            while leadings:
                if leadings[-1] == len_leading:
                    break
                if leadings[-1] > len_leading:
                    new_indent = None
                    break
                leadings.pop()
                indent -= 1
            if not leadings:
                new_indent = None

        # print(f"  >> {leadings=} {new_indent=}")
        if new_indent:
            leadings.append(len_leading)
            indent += 1
        elif new_indent is None:
            raise IndentationError(f"line {info.line_number} column {len_leading + info.column_number}: unindent does not match any outer indentation level")
        info.leading = original_leading
        info.indent = indent
        if len_leading:
            info.column_number += len_leading
            line = lstripped

        yield (info, line)

@_export
def lines_filter_empty_lines(li):
    """
    A lines modifier function.  Filters out the empty lines
    of a "lines iterator".

    Preserves the line numbers.  If lines 0 through 2 are empty,
    line 3 is "a", line 4 is empty, and line 5 is "b",
    will yield:
        (3, "a")
        (5, "b")

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

        self.init()

    def init(self):
        self.words = []

        self.leading = []
        self.word = []
        self.code = []

        # used to regulate line and paragraph breaks.
        # can be _code_paragraph, _text_paragraph, or None.
        # (if None, we've already handled the appropriate break.)
        self.previous_paragraph = None

        self.state = self.state_initial

    def emit(self, c):
        # print(f" [emit]", repr(c))
        self.words.append(c)

    def line_break(self):
        # print(f" [  \\n]")
        self.words.append(self.newline_string)

    def paragraph_break(self):
        # print(f" [\\n\\n]")
        self.words.append(self.paragraph_string)

    def next(self, state, leading=None, word=None):
        # print(f" [  ->]", state.__name__, repr(leading), repr(word))
        self.state = state
        assert ((leading is None) and (word is None)) or ((leading is not None) and (word is not None))
        if word is not None:
            self.state(leading, word)

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
        self.next(self.state_line_start, leading, word)

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

            self.next(self.state_paragraph_start)
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

                self.next(self.state_code_line_start, leading, word)
                return

        if self.previous_paragraph == _code_paragraph:
            self.paragraph_break()
        self.next(self.state_text_line_start, leading, word)

    def state_text_line_start(self, leading, word):
        self.previous_paragraph = _text_paragraph
        self.next(self.state_in_text_line, leading, word)

    def state_in_text_line(self, leading, word):
        if word == self.newline_string:
            self.next(self.state_line_start)
            return
        self.emit(word)

    def state_code_line_start(self, leading, word):
        self.previous_paragraph = _code_paragraph
        self.col = 0
        self.next(self.state_in_code_line, leading, word)

    def state_in_code_line(self, leading, word):
        if word == self.newline_string:
            self.emit(self.empty.join(self.code))
            self.code.clear()
            self.next(self.state_line_start, self.empty, word)
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
        def next_overflow():
            nonlocal overflow_start
            nonlocal overflow_end
            if overflows:
                overflow_start, overflow_end = overflows.pop()
            else:
                overflow_start = overflow_end = sys.maxsize

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

