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

from . import text
from .text import _iterate_over_bytes, __separators_to_re
from .itertools import PushbackIterator

import re


__all__ = []

def _export_name(s):
    __all__.append(s)

def _export(o):
    _export_name(o.__name__)
    return o



# Before 10.1, big used the word "newlines" instead of "linebreaks"
# in the names of these tuples.  I realized in September 2023 that
# "linebreaks" was a better name; Unicode uses the term "line breaks"
# for these characters.
#
# Similarly, "_without_crlf" used to be "_without_dos".  As much
# as we might dream about a world without DOS, _without_crlf is
# far more accurate.
#
# Here's some backwards-compatibility for you.
# I promise to keep the old names around until at least September 2024.
_export_name('whitespace_without_dos')
whitespace_without_dos = text.str_whitespace_without_crlf

_export_name('ascii_whitespace_without_dos')
ascii_whitespace_without_dos = text.bytes_whitespace_without_crlf

_export_name('newlines')
newlines = text.str_linebreaks
_export_name('newlines_without_dos')
newlines_without_dos = text.str_linebreaks_without_crlf

_export_name('ascii_newlines')
ascii_newlines = text.bytes_linebreaks
_export_name('ascii_newlines_without_dos')
ascii_newlines_without_dos = text.bytes_linebreaks_without_crlf

# These old tuples are deprecated, because it's easy to make
# them yourself (and a million other variants) with encode_strings().
# They'll be removed when I remove the backwards-compatibility
# names above.
_export_name('utf8_whitespace')
utf8_whitespace = text.encode_strings(text.str_whitespace, "utf-8")
_export_name('utf8_whitespace_without_dos')
utf8_whitespace_without_dos = tuple(b for b in utf8_whitespace if b != b'\r\n')

_export_name('utf8_newlines')
utf8_newlines   = text.encode_strings(text.str_linebreaks, "utf-8")
_export_name('utf8_newlines_without_dos')
utf8_newlines_without_dos =  tuple(b for b in utf8_newlines if b != b'\r\n')




@_export
def split_quoted_strings(s, quotes=None, *, triple_quotes=True, backslash=None):
    """
    This function is deprecated.  Please use the new version, big.text.split_quoted_strings.

    Splits s into quoted and unquoted segments.

    s can be either str or bytes.

    quotes is an iterable of quote separators, either str or bytes matching s.
    Note that split_quoted_strings only supports quote *characters*, as in,
    each quote separator must be exactly one character long.

    Returns an iterator yielding 2-tuples:
        (is_quoted, segment)
    where segment is a substring of s, and is_quoted is true if the segment is
    quoted.  Joining all the segments together recreates s.  (The segment
    strings include the quote marks.)

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

def parse_delimiters(s, delimiters, backslash_character, closers, empty):
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

_parse_delimiters = parse_delimiters

@_export
def parse_delimiters(s, delimiters=None):
    """
    Note: This function is deprecated.  Please switch to
    the modern version, big.text.split_delimiters.

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

    return _parse_delimiters(s, delimiters, backslash_character, closers, empty)

@_export
def lines_strip_comments(li, comment_separators, *, quotes=('"', "'"), backslash='\\', rstrip=True, triple_quotes=True):
    """
    NOTE: This function is deprecated.  Please use the new version,
    big.text.lines_strip_line_comments.

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
                # note: uses the deprecated version in this file!
                i = split_quoted_strings(line, quotes, backslash=backslash, triple_quotes=triple_quotes)
            else:
                i = ((False, line),)

            # iterate over the line until we either hit the end or find a comment.
            segments = []
            append = segments.append
            for is_quoted, segment in i:
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
                break

            keeping = sum(len(s) for s in segments)
            removing = len(line) - keeping
            if removing:
                line = info.clip_trailing(line, removing)
            yield (info, line)
    return lines_strip_comments(li, split, quotes, backslash, rstrip, triple_quotes)


# old, deprecated name.
# will eventually be deleted, but not before September 2025.
lines_filter_comment_lines = text.lines_filter_line_comment_lines
_export_name("lines_filter_comment_lines")


