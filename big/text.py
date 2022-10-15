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

import enum
import itertools
from itertools import zip_longest
from .itertools import PushbackIterator
import operator
import re
import struct
import sys


__all__ = []

def _export_name(s):
    __all__.append(s)

def _export(o):
    _export_name(o.__name__)
    return o


@_export
def re_partition(s, pattern, count=1, *, flags=0, reverse=False):
    """
    Like str.partition, but pattern is matched as a regular expression.

    s can be a string or a bytes object.

    pattern can be a string, bytes, or an re.Pattern object.

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

    Passing in an explicit "count" lets you control how many times
    re_partition partitions the string.  re_partition will always
    return a tuple containing (2*count)+1 elements, and
    odd-numbered elements will be either re.Match objects or None.
    Passing in a count of 0 will always return a tuple containing s.

    If pattern is a string or bytes, flags is passed in
    as the flags argument to re.compile.

    If reverse is true, partitions starting at the right,
    like re_rpartition.
    """
    if reverse:
        return re_rpartition(s, pattern, count, flags=flags)
    if not isinstance(pattern, re.Pattern):
        pattern = re.compile(pattern, flags=flags)
    if not (isinstance(s, (str, bytes)) and
        (type(s) == type(pattern.pattern))):
        raise ValueError("s must be str or int, and string used in pattern must be the same type")
    as_bytes = isinstance(s, bytes)
    empty = b'' if as_bytes else ''

    if count < 0:
        raise ValueError("count must be >= 0")

    result = [s]
    if count == 0:
        return result

    if count == 1:
        # much cheaper for the general case
        match = pattern.search(s)
        if match:
            matches = [match]
        else:
            matches = ()
    else:
        matches = list(pattern.finditer(s))
        matches.reverse()

    for _ in range(count):
        if not matches:
            result.extend((None, empty))
            continue

        match = matches.pop()
        s = result.pop()

        before, separator, after = s.partition(match.group(0))
        result.extend((before, match, after))

    return tuple(result)


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

    If pattern appears in s multiple times,
    re_partition will match against the last (rightmost)
    appearance.

    If pattern is not found in s, returns a tuple
        ('', None, s)
    where the empty string is str or bytes as appropriate.

    Passing in an explicit "count" lets you control how many times
    re_rpartition partitions the string.  re_rpartition will always
    return a tuple containing (2*count)+1 elements, and
    odd-numbered elements will be either re.Match objects or None.
    Passing in a count of 0 will always return a tuple containing s.

    If pattern is a string, flags is passed in
    as the flags argument to re.compile.
    """
    if not isinstance(pattern, re.Pattern):
        pattern = re.compile(pattern, flags=flags)
    if not (isinstance(s, (str, bytes)) and
        (type(s) == type(pattern.pattern))):
        raise ValueError("s must be str or int, and string used in pattern must be the same type")

    if count < 0:
        raise ValueError("count must be >= 0")

    result = [s]
    if count == 0:
        return result

    as_bytes = not isinstance(s, str)
    empty = b'' if as_bytes else ''
    matches = list(pattern.finditer(s))

    for i in range(count):
        if not matches:
            r = [empty, None]
        else:
            match = matches.pop()
            s = result.pop(0)
            before, separator, after = list(s.rpartition(match.group(0)))
            r = [before, match, after]
        r.extend(result)
        result = r
    return tuple(result)


# a list of all unicode whitespace characters
_export_name('whitespace')
whitespace = [
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

    '\r\n'  , # the classic DOS newline sequence
    ]

# this omits the DOS convention '\r\n'
_export_name('whitespace_without_dos')
whitespace_without_dos = [s for s in whitespace if s != '\r\n']

_export_name('newlines')
newlines = [
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

    # '\n\r' sorry, Acorn and RISC OS, you have to add this yourselves.
    # I'm worried this would cause bugs with a malformed DOS newline.
    ]

# this omits the DOS convention '\r\n'
_export_name('newlines_without_dos')
newlines_without_dos = [s for s in newlines if s != '\r\n']

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
ascii_whitespace_without_dos = [s for s in ascii_whitespace if s != b'\r\n']
_export_name('ascii_newlines')
ascii_newlines   = _cheap_encode_iterable_of_strings(newlines,   "ascii")
_export_name('ascii_newlines_without_dos')
ascii_newlines_without_dos = [s for s in ascii_newlines if s != b'\r\n']

# use these with multisplit if your bytes strings are encoded as utf-8.
_export_name('utf8_whitespace')
utf8_whitespace = _cheap_encode_iterable_of_strings(whitespace, "utf-8")
_export_name('utf8_whitespace_without_dos')
utf8_whitespace_without_dos = [s for s in utf8_whitespace if s != b'\r\n']
_export_name('utf8_newlines')
utf8_newlines   = _cheap_encode_iterable_of_strings(newlines,   "utf-8")
_export_name('utf8_newlines_without_dos')
utf8_newlines_without_dos =  [s for s in utf8_newlines if s != b'\r\n']


def _re_quote(s):
    # don't bother escaping whitespace.
    # re.escape escapes whitespace because of VERBOSE mode,
    # which we're not using.  (escaping the whitespace doesn't
    # hurt anything really, but it makes the patterns harder
    # to read for us humans.)
    if not s.isspace():
        s = re.escape(s)
    if len(s) > 1:
        if isinstance(s, bytes):
            s = b"(?:" + s + b")"
        else:
            s = f"(?:{s})"
    return s

def _separators_to_re(separators, as_bytes, separate=False, keep=False):
    if as_bytes:
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
    # print(f"  P1 {pattern!r}")
    if not separate:
        pattern = separate_start + pattern + separate_end
    # print(f"  P2 {pattern!r}")
    if keep:
        pattern = keep_start + pattern + keep_end
    # print(f"  P3 {pattern!r}")
    return pattern

@_export
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

    Processing always stops at the first character that
    doesn't match one of the separators.

    Returns a copy of s with the leading and/or trailing
    separators stripped.  (If left and right are both
    false, returns s unchanged.)
    """
    if not (left or right):
        return s
    as_bytes = isinstance(s, bytes)
    if as_bytes:
        head = b'^'
        tail = b'$'
        if isinstance(separators, bytes):
            # not iterable of bytes, literally a bytes string.
            # split it ourselves.
            separators = [separators[i:i+1] for i in range(len(separators))]
    else:
        head = '^'
        tail = '$'
    pattern = _separators_to_re(separators, as_bytes, separate=False, keep=False)

    start = 0
    end = len(s)
    if left:
        left_match = re.match(head + pattern, s)
        if left_match:
            start = left_match.end(0)
    if right:
        right_match = re.search(pattern + tail, s)
        if right_match:
            end = right_match.start(0)
    return s[start:end]


# for keep
AS_PAIRS="AS_PAIRS"
_export_name(AS_PAIRS)
ALTERNATING="ALTERNATING"
_export_name(ALTERNATING)

# for strip
NOT_SEPARATE = "NOT_SEPARATE"
_export_name(NOT_SEPARATE)
LEFT = "LEFT"
_export_name(LEFT)
RIGHT = "RIGHT"
_export_name(RIGHT)
STR_SPLIT = "STR_SPLIT"  # not implemented yet
_export_name(STR_SPLIT)

@_export
def multisplit(s, separators=None, *,
    keep=False,
    maxsplit=-1,
    reverse=False,
    separate=False,
    strip=NOT_SEPARATE,
    ):
    """
    Like str.split, supporting multiple separator strings and tunable behavior.

    s can be str or bytes.

    separators should be an iterable of str or bytes, matching s.

    Returns an iterator yielding the strings split from s.  If keep
    is not false, and strip is false, joining these strings together
    will recreate s.

    multisplit is greedy; if two (or more) separator strings match at a
    particular index in "s", it splits using the largest one.

    "keep" indicates whether or not multisplit should keep the separator
    strings.  It supports four values:
        false (the default)
            Discard the separators.
        true (apart from ALTERNATING or AS_PAIRS)
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
        NOT_SEPARATE (the default)
            Use the opposite value specified for "separate"
            If separate=True, behaves as if strip=False.
            If separate=False, behaves as if strip=True.
        false
            Don't strip separators from the beginning or end of s.
        LEFT
            Strip separators only from the beginning of s
            (a la str.lstrip).
        RIGHT
            Strip separators only from the end of s
            (a la str.rstrip).
        true
            Strip separators from the beginning and end of s
            (a la str.strip).
        STR_SPLIT (currently unimplemented, equivalent to true)
            Strip the way str.split does when splitting on whitespace.
            Strip from the beginning and end of s, unless maxsplit
            is nonzero and the entire string is not split.  If
            splitting stops due to maxsplit before the entire string
            is split, and reverse is false, don't strip the end of
            the string. If splitting stops due to maxsplit before
            the entire string is split, and reverse is true, don't
            strip the beginning of the string.

    "maxsplit" should be either an integer or None.  If maxsplit is an
    integer greater than -1, multisplit will split s no more than
    maxsplit times.

    "reverse" affects whether the "maxsplit" splits start at the
    beginning or the end of the string.  It supports two values:
        false (the default)
            Start splitting at the beginning of the string.
        true
            Start splitting at the end of the string.
    "reverse" has no effect when maxsplit is 0, -1, or None.
    """

    as_bytes = isinstance(s, bytes)
    if separators is None:
        separators = ascii_whitespace if as_bytes else whitespace
    if as_bytes:
        if isinstance(separators, bytes):
            # not iterable of bytes, literally a bytes string.
            # split it ourselves.
            separators = [separators[i:i+1] for i in range(len(separators))]
        separators_type = bytes
        empty = b''
    else:
        separators_type = str
        empty = ''
    for o in separators:
        if not isinstance(o, separators_type):
            raise ValueError("separators must be an iterable of objects the same type as s")

    if strip == NOT_SEPARATE:
        strip = not separate

    if strip:
        s = multistrip(s, separators, left=(strip != RIGHT), right=(strip != LEFT))

    if maxsplit == None:
        maxsplit = -1
    if maxsplit == 0:
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
    # maxsplit==0 means "allow all splits".
    # maxsplit==1 means "only allow one split".
    #
    # (re.split doesn't have a way to express
    #  "don't split" with its maxsplit parameter,
    #  which is why we handled it already.)
    if maxsplit == -1:
        maxsplit = 0

    # we may change the values of keep and maxsplit
    # we pass in to subfunctions, depending.
    # these are the original values.
    original_keep = keep
    original_maxsplit = maxsplit

    if reverse and (maxsplit > 0):
        # we have to handle reverse maxsplit by hand.
        # we completely split, then rejoin strings
        # together to simulate the maxsplit value.
        # this means that inside the function we have
        # to keep separators; if the user didn't specify
        # keep, we'll throw the un-joined ones away.
        maxsplit = 0
        keep = True
    else:
        # we're not maxsplitting, so reverse is unused.
        reverse = False

    pattern = _separators_to_re(separators, as_bytes, keep=keep, separate=separate)

    l = re.split(pattern, s, maxsplit)
    assert l

    if reverse:
        maxsplit = original_maxsplit
        keep = original_keep
        # alternating nonsep, sep strings
        desired_length = 1 + (2*maxsplit)
        length = len(l)
        join_count = length - desired_length + 1
        if join_count > 1:
            s = empty.join(l[:join_count])
            del l[:join_count]
            l.insert(0, s)
        if not keep:
            for i in range(len(l) - 2, 0, -2):
                del l[i]

    if not keep:
        for o in l:
            yield o
        return

    # from here on out, we're 'keep'-ing the separator strings.
    # (we're returning the separator strings in one form or another.)

    if keep == ALTERNATING:
        for o in l:
            yield o
        return

    if (len(l) % 2) == 1:
        l.append(empty)

    previous = None
    for o in l:
        if previous is None:
            previous = o
            continue
        if keep == AS_PAIRS:
            yield (previous, o)
        else:
            yield previous + o
        previous = None


@_export
def multipartition(s, separators, count=1, *, reverse=False, separate=True):
    """
    Like str.partition, but supports partitioning based on multiple separator
    strings, and can partition more than once.

    "s" can be str or bytes.

    "separators" should be an iterable of str or bytes, matching "s".

    By default, if any of the strings in "separators" are found in "s",
    returns a tuple of three strings: the portion of "s" leading up to
    the earliest separator, the separator, and the portion of "s" after
    that separator.  Example:

    multipartition('aXbYz', ('X', 'Y')) => ('a', 'X', 'bYz')

    If none of the separators are found in the string, returns
    a tuple containing `s` unchanged followed by two empty strings.

    Passing in an explicit "count" lets you control how many times
    multipartition partitions the string.  multipartition will always
    return a tuple containing (2*count)+1 elements.  Passing in a
    count of 0 will always return a tuple containing s.

    If separate is true, multiple adjacent separator strings behave
    like one separator.  Example:

    multipartition('aXYbXYc', ('X', 'Y',), separate=True) => ('a', 'XY', 'bXYc')

    If reverse is true, multipartition behaves like str.rpartition.
    It partitions starting on the right, scanning backwards through
    s looking for separators.
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
        as_bytes = isinstance(s, bytes)
        if as_bytes:
            empty = b''
        else:
            empty = ''
        extension = [empty] * (desired_length - result_length)
        if reverse:
            result = extension + result
        else:
            result.extend(extension)
    return tuple(result)


_invalid_state = 0
_in_word = 1
_after_whitespace = 2
_after_whitespace_then_apostrophe_or_quote_mark = 3
_after_whitespace_then_D_or_O = 4
_after_whitespace_then_D_or_O_then_apostrophe = 5

@_export
def gently_title(s):
    """
    Uppercase the first character of every word in s.
    Leave the other letters alone.

    (For the purposes of this algorithm, words are
    any blob of non-whitespace characters.)

    Capitalize the letter after an apostrophe if
        a) the apostrophe is after whitespace
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

    Each of these Unicode code points is considered
    an apostrophe:
        '‘’‚‛

    Each of these Unicode code points is considered
    a quote mark:
        "“”„‟«»‹›
    """
    result = []
    state = _after_whitespace
    for c in s:
        is_space = c.isspace()
        is_apostrophe = c in "'‘’‚‛"
        is_quote_mark = c in '"“”„‟«»‹›'
        if state == _in_word:
            if is_space:
                state = _after_whitespace
        elif state == _after_whitespace:
            if not is_space:
                c = c.upper()
                if (is_apostrophe or is_quote_mark):
                    state = _after_whitespace_then_apostrophe_or_quote_mark
                elif c in "DO":
                    state = _after_whitespace_then_D_or_O
                else:
                    state = _in_word
        elif state == _after_whitespace_then_apostrophe_or_quote_mark:
            if not (is_apostrophe or is_quote_mark):
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
    return "".join(result)


@_export
def normalize_whitespace(s, separators=None, replacement=None):
    """
    Returns s, but with every run of consecutive
    separator characters turned into a replacement string.
    By default turns all runs of consecutive whitespace
    characters into a single space character.

    "s" may be str or bytes.
    "separators" should be an iterable of either str or bytes,
    matching "s".
    "replacement" should be str or bytes, also matching "s".

    Leading or trailing runs of separator characters will
    be replaced with the replacement string, e.g.:

       normalize_whitespace("   a    b   c") == " a b c".
    """
    as_bytes = isinstance(s, bytes)
    if as_bytes:
        empty = b''
        default_replacement = b' '
        default_separators = ascii_whitespace
    else:
        empty = ''
        default_replacement = ' '
        default_separators = whitespace

    if not s:
        return empty

    if separators is None:
        separators = default_separators
    if replacement is None:
        replacement = default_replacement

    if separators in (whitespace, ascii_whitespace, utf8_whitespace, None):
        if not s.strip():
            return replacement
        words = s.split()
        cleaned = replacement.join(words)
        del words
        if s[:1].isspace():
            cleaned = replacement + cleaned
        if s[-1:].isspace():
            cleaned = cleaned + replacement
        return cleaned

    words = list(multisplit(s, separators, keep=False, separate=False, strip=True, reverse=False, maxsplit=-1))
    cleaned = replacement.join(words)
    del words
    stripped_left = multistrip(s, separators, left=True, right=False) != s
    if stripped_left:
        cleaned = replacement + cleaned
    stripped_right = multistrip(s, separators, left=False, right=True) != s
    if stripped_right:
        cleaned = cleaned + replacement
    return cleaned


@_export
def split_quoted_strings(s, quotes=('"', "'"), *, triple_quotes=True, backslash='\\'):
    """
    Splits s into quoted and unquoted segments.  Returns an iterator yielding
    2-tuples:
        (is_quoted, segment)
    where segment is a substring of s, and is_quoted is true if the segment is
    quoted.  Joining all the segments together recreates s.

    quotes is an iterable of quote separators.  Note that split_quoted_strings
    only supports quote *characters*, as in, each quote separator must be exactly
    one character long.

    If triple_quotes is true, supports "triple-quoted" strings like Python.

    If backslash is a character, this character will quoting characters inside
    a quoted string, like the backslash character inside strings in Python.
    """
    i = PushbackIterator(s)
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
                    yield False, "".join(text)
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
                    yield False, "".join(text)
                    text.clear()
                text.append(c)
                in_quote = c
                continue
            c3 = i.next(None)
            if c3 != c:
                # two quotes in a row, but not three.
                # flush unquoted string, emit empty quoted string.
                if text:
                    yield False, "".join(text)
                    text.clear()
                yield True, c*2
                if c3 is not None:
                    i.push(c3)
                continue
            # triple quoted string.
            # flush unquoted string, start triple quoted string.
            if text:
                yield False, "".join(text)
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
            yield True, "".join(text)
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
            yield True, "".join(text)
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
        yield in_quote, "".join(text)


@_export
class LineInfo:
    """
    The info object yielded by a lines iterator.
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

        "s" can be str, bytes, or any iterable.

        By default, if "s" is str, splits "s" by all Unicode line break characters.
        If "s" is bytes, splits "s" by all ASCII line break characters.

        If "s" is neither str nor bytes, "s" must be an iterable;
        lines yields successive elements of "s" as lines.

        "separators", if not None, must be an iterable of strings of the
        same type as "s".  lines will split "s" using those strings as
        separator strings (using big.multisplit).

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
        (e.g. lines_convert_tabs_to_spaces). Similarly, all keyword
        arguments passed in via kwargs are stored internally and can be
        accessed by user-defined lines modifier functions.

        Composable with all the lines_ functions from the big.text module.
        """
        if not isinstance(line_number, int):
            raise TypeError("line_number must be int")
        if not isinstance(column_number, int):
            raise TypeError("column_number must be int")
        if not isinstance(tab_width, int):
            raise TypeError("tab_width must be int")

        as_bytes = isinstance(s, bytes)
        as_str = isinstance(s, str)
        if as_bytes or as_str:
            if not separators:
                separators = newlines if as_str else ascii_newlines
            i = multisplit(s, separators, keep=False, separate=True, strip=False)
        else:
            i = iter(s)
            as_bytes = None

        self.s = s
        self.separators = separators
        self.line_number = line_number
        self.column_number = column_number
        self.tab_width = tab_width
        self.as_bytes = as_bytes

        self.i = i

        self.__dict__.update(kwargs)

    def __iter__(self):
        return self

    def __next__(self):
        line = next(self.i)
        if self.as_bytes is None:
            self.as_bytes = isinstance(line, bytes)
        return_value = (LineInfo(line, self.line_number, self.column_number), line)
        self.line_number += 1
        return return_value

@_export
def lines_rstrip(li):
    """
    A lines modifier function.  Strips trailing whitespace from the
    lines of a "lines iterator".

    Composable with all the lines_ functions
    from the big text module.
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

    Composable with all the lines_ functions from the big.text module.
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

    Composable with all the lines_ functions from the big.text module.
    """
    if not comment_separators:
        raise ValueError("illegal comment_separators")
    as_bytes = isinstance(comment_separators[0], bytes)
    comment_pattern = _separators_to_re(tuple(comment_separators), as_bytes, separate=False, keep=False)
    comment_re = re.compile(comment_pattern)
    for info, line in li:
        s = line.lstrip()
        if comment_re.match(s):
            continue
        yield (info, line)

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

    Composable with all the lines_ functions from the big.text module.
    """
    if not comment_separators:
        raise ValueError("illegal comment_separators")
    as_bytes = isinstance(comment_separators[0], bytes)

    comment_pattern = _separators_to_re(comment_separators, as_bytes=as_bytes, separate=True, keep=True)
    re_comment = re.compile(comment_pattern)
    split = re_comment.split
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

        info.comment = "".join(comment)
        line = "".join(segments)
        yield (info, line)

@_export
def lines_convert_tabs_to_spaces(li):
    """
    A lines modifier function.  Converts tabs to spaces for the lines
    of a "lines iterator", using the tab_width passed in to lines.

    Composable with all the lines_ functions from the big.text module.
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

    Composable with all the lines_ functions from the big.text module.
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

    'words' should be an iterator containing text split at word
    boundaries.  Example:
        "this is an example of text split at word boundaries".split()
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
    """
    words = iter(words)
    col = 0
    lastword = ''
    text = []

    for word in words:
        if word.isspace():
            lastword = word
            col = 0
            text.append(word)
            continue

        l = len(word)

        if two_spaces and lastword.endswith(('.', '?', '!')):
            space = "  "
            len_space = 2
        else:
            space = " "
            len_space = 1

        if (l + len_space + col) > margin:
            if col:
                text.append('\n')
                col = 0
        elif col:
            text.append(space)
            col += len_space

        text.append(word)
        col += len(word)
        lastword = word

    return "".join(text)



_code_paragraph = "code paragraph"
_text_paragraph = "text paragraph"

class _column_wrapper_splitter:

    def __init__(self, tab_width, allow_code, code_indent, convert_tabs_to_spaces):
        # print(f"\n_column_wrapper_splitter({tab_width=}, {allow_code=}, {convert_tabs_to_spaces=})")
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
        self.words.append('\n')

    def paragraph_break(self):
        # print(f" [\\n\\n]")
        self.words.append('\n\n')

    def next(self, state, leading=None, word=None):
        # print(f" [  ->]", state.__name__, repr(leading), repr(word))
        self.state = state
        assert ((leading is None) and (word is None)) or ((leading is not None) and (word is not None))
        if word is not None:
            self.state(leading, word)

    def write(self, s):
        # write consumes s and makes calls as appropriate to
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

        for c in s:
            # print(f"<{c!r}> ", end='')

            if not c.isspace():
                word.append(c)
                continue

            if word:
                w = "".join(word)
                word.clear()
                if leading:
                    l = ''.join(leading)
                else:
                    l = ''
                leading.clear()
                self.state(l, w)
            if c == '\n':
                if leading:
                    l = ''.join(leading)
                else:
                    l = ''
                leading.clear()
                self.state(l, c)
            else:
                leading.append(c)

    def close(self):
        # flush the current word, if any.
        if self.word:
            self.state("".join(self.leading), "".join(self.word))
            self.leading.clear()
            self.word.clear()

    def state_paragraph_start(self, leading, word):
        """
        Initial state.  Also the state we return to
        after encountering two '\n's in a row after
        a text line.
        """
        if word == '\n':
            return
        if self.previous_paragraph:
            self.paragraph_break()
            self.previous_paragraph = None
        self.next(self.state_line_start, leading, word)

    state_initial = state_paragraph_start

    def state_line_start(self, leading, word):
        if word == '\n':
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
            for c in leading:
                if c == '\t':
                    col = col + tab_width - (col % tab_width)
                elif c == ' ':
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
        if word == '\n':
            self.next(self.state_line_start)
            return
        self.emit(word)

    def state_code_line_start(self, leading, word):
        self.previous_paragraph = _code_paragraph
        self.col = 0
        self.next(self.state_in_code_line, leading, word)

    def state_in_code_line(self, leading, word):
        if word == '\n':
            self.emit("".join(self.code))
            self.code.clear()
            self.next(self.state_line_start, '', word)
            return

        tab_width = self.tab_width
        convert_tabs_to_spaces = self.convert_tabs_to_spaces
        col = self.col
        for c in leading:
            if c == '\t':
                delta = tab_width - (col % tab_width)
                col += delta
                if convert_tabs_to_spaces:
                    self.code.append(' ' * delta)
                else:
                    self.code.append(c)
            elif c == ' ':
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

    Paragraphs indented by less than code_indent will be
    broken up into individual words.

    If `allow_code` is true, paragraphs indented by at least
    code_indent spaces will preserve their whitespace:
    internal whitespace is preserved, and the newline is
    preserved.  (This will preserve the formatting of code
    examples, when these words are rejoined into lines
    by wrap_words.)
    """
    cws = _column_wrapper_splitter(tab_width, allow_code, code_indent, convert_tabs_to_spaces)
    for c in s:
        cws.write(c)
    cws.close()
    return cws.words


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
def merge_columns(*columns, column_separator=" ",
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
    text should be a single text string, with newline
    characters separating lines. min_width and max_width
    are the minimum and maximum permissible widths for that
    column, not including the column separator (if any).

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
    """
    assert overflow_strategy in (OverflowStrategy.INTRUDE_ALL, OverflowStrategy.DELAY_ALL, OverflowStrategy.RAISE)
    raise_overflow_error = overflow_strategy == OverflowStrategy.RAISE
    delay_all = overflow_strategy == OverflowStrategy.DELAY_ALL

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

        empty_columns.append(max_width * " ")

        if isinstance(s, str):
            lines = s.rstrip().split('\n')
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
            assert not "\n" in line
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
                rstripped_lines.append('')

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
        line = "".join(line).rstrip()
        lines.append(line)

    text = "\n".join(lines)
    return text.rstrip()

