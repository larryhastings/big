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


from bisect import bisect_right
from collections import deque
import copy
from itertools import zip_longest
import re
try: # pragma nocover
    # new in 3.9
    from types import GenericAlias
except ImportError: # pragma nocover
    # backwards compatibility for 3.7 and 3.8
    # (3.6 doesn't support __class_getitem__ so we don't need it there)
    def GenericAlias(origin, args):
        s = ", ".join(t.__name__ for t in args)
        return f'{origin.__name__}[{s}]'


from .text import linebreaks, multipartition, multisplit, Pattern
from .tokens import generate_tokens


__all__ = []
def export(o):
    __all__.append(o.__name__)
    return o



#####################################################################################################
#####################################################################################################
###
###
###                  .             o8o
###                .o8             `"'
###      .oooo.o .o888oo oooo d8b oooo  ooo. .oo.    .oooooooo
###     d88(  "8   888   `888""8P `888  `888P"Y88b  888' `88b
###     `"Y88b.    888    888      888   888   888  888   888
###     o.  )88b   888 .  888      888   888   888  `88bod8P
###     8""888P'   "888" d888b    o888o o888o o888o `8oooooo
###                                                 d"     YD
###                                                 "Y88888P
###
###
#####################################################################################################
#####################################################################################################


## string uses _re_linebreaks_finditer to split lines by linebreaks.
## string obeys Python's rules about where to split a line, and
## Python recognizes the DOS '\r\n' sequence as *one linebreak*.
##
##    >>> ' a \n b \r c \r\n d \n\r e '.splitlines(True)
##    [' a \n', ' b \r', ' c \r\n', ' d \n', '\r', ' e ']
##
## So the rule is, expressed in pseudocode:
##
##     for s in string:
##         if s == '\r':
##             if s + 1 == '\n':
##                 continue
##             break_line_here()
##         elif s == '\n':
##             break_line_here()
##
## But we want to handle the other funny Unicode linebreaks too.
## big's "linebreaks" iterable contains all of 'em, and it
## includes '\r\n'.  So: sort linebreaks by length, longest
## first, and build the regular expression out of that.
## (Python's re engine, like all good regular expression engines,
## keeps the *first* match.  So, sort longest substring first.)
##

_re_linebreaks = "|".join(sorted(linebreaks, key=lambda s: -len(s)))
_re_linebreaks_finditer = re.compile(_re_linebreaks).finditer
del _re_linebreaks

_linebreaks_and_tab_set = set(linebreaks) | set('\t')


class Origin:
    """
    An Origin object is the building block of big.string objects.
    It contains an original Python string with some extra metadata.
    """
    __slots__ = ('s', 'string', 'source', 'line_number', 'column_number', 'first_column_number', 'tab_width', 'linebreak_offsets', )

    def __init__(self, s, source, line_number, column_number, first_column_number, tab_width):
        self.s = s
        self.source = source
        self.line_number = line_number
        self.column_number = column_number
        self.first_column_number = first_column_number
        self.tab_width = tab_width
        self.linebreak_offsets = None
        # this is a reference to the big.string which contains just this Origin.
        # we have to set this manually later.
        self.string = None

    def compute_linebreak_offsets(self):
        #     self.linebreak_offsets[line_number_offset]
        # is the offset of the first character of the line after
        #     self.line_number + line_number_offset
        #
        # e.g. "abcde\nfghij"
        # self._linebreak_offsets = (6,)
        #
        # assuming first_line_number is 1:
        # line 1 always starts at offset 0, we don't write it down
        # line 2 starts at self._linebreak_offsets[0]
        self.linebreak_offsets = linebreak_offsets = tuple(match.end() for match in _re_linebreaks_finditer(self.s))
        if 0:
            print()
            print(repr(str(self)))
            print(list(_re_linebreaks_finditer(str(self))))
            print(linebreak_offsets)
            print()
        return linebreak_offsets

    def compute_line_and_column(self, offset):
        linebreak_offsets = self.linebreak_offsets
        if linebreak_offsets is None:
            linebreak_offsets = self.compute_linebreak_offsets()
        linebreak_index = bisect_right(linebreak_offsets, offset)
        line_number = self.line_number + linebreak_index
        # either 0 or the offset of the previous line
        line_start_offset = linebreak_index and linebreak_offsets[linebreak_index - 1]

        s = self.s
        first_column_number = self.first_column_number
        if not linebreak_index:
            column_number = self.column_number
        else:
            column_number = first_column_number
        tab_width = self.tab_width

        for o in range(line_start_offset, offset):
            c = s[o]
            # print(f"{line_start_offset=} {offset=} {s=} {o=} {c=}")
            # assert c not in linebreaks

            if c != '\t':
                column_number += 1
                continue

            # handle tab:
            # when your first column is 1, your tabs are at 9, 17, 25, etc.
            # you have to deduct the first column number to do the math.
            remainder = (column_number - first_column_number) % tab_width
            distance_to_next_tab_stop = tab_width - remainder
            column_number += distance_to_next_tab_stop
        return line_number, column_number

    def __repr__(self): # pragma: nocover
        return f"<Origin s={self.s!r} source={self.source}>"


class Range:
    """
    A Range is a reference to a range of characters in an Origin.
    A big.string is mainly a sequence of Range objects.
    """
    __slots__ = ('origin', 'start', 'stop')

    def __init__(self, origin, start, stop):
        assert start <= stop
        self.origin = origin
        self.start = start
        self.stop = stop

    def __repr__(self): # pragma: nocover
        return f"<Range origin={self.origin!r} start={self.start} stop={self.stop}>"


@export
class string(str):
    """
    A subclass of str that maintains line, column, and offset information.

    string is a drop-in replacement for Python's str that knows its own
    line and column number.  It's a subclass of str and implements every
    str method.  Every operation that returns a substring, like partition
    or split or [], returns a big.string that knows *its* line and column
    information too.

    Additional features of string:
    * Every string knows its line number, column number, and offset from the
      beginning of the original string.
    * You may also specify a "source" parameter to the constructor,
      which should indicate where the text came from (e.g. the filename).
    * If you add big.string objects together, the substrings remember their
      original line / column / offset.

    Parameters:
    * source is a human-readable string describing where this string
      came from.  It's presented unquoted, so if you want quote marks
      around it (e.g. "C:\\AUTOEXEC.BAT") you should add those yourself.
    * line_number and column_number are the line and column numbers
      of the first character of the string.
    * first_column_number is what the column number is reset to when
      big.string encounters a linebreak in the string.
    * tab_width is the distance between tab columns used for calculating
      column numbers.  It's the same as the "tabsize" parameter for
      str.expandtabs.

    Additional attributes of string:
    * s.line_number and s.column_number are the line and column numbers
      of this string.
    * s.origin is the original big.string object this string was extracted from.
    * s.offset is the index of the first character of this string from where it
      came from in the s.offset string.  (s.origin[s.offset] == s[0])
    * s.where is a string designed for error messages.  If the original string
      was initialized with a source, this will be in the format
          <source> line <line_number> column <column_number>
      If no source was supplied, this will be in the format
          line <line_number> column <column_number>
      This makes writing error messages easy.  Let's say you're parsing a file
      and you hit a syntax error.  token is a big.string containing the bad
      token.  Simply raise
          SyntaxError(f"{token.where}: {token}")
    * s.source, s.first_column_number, and s.tab_width are the values passed
      in to big.string when this string was created.  (s.origin.source == s.source,
      etc.)

    If you pass a big.string into certain Python modules (implemented in C),
    it will return substrings as str objects and not big.string objects.
    big.string provides wrappers for two of these:
        * string.generate_tokens wraps tokenizer.generate_tokens, and
        * string.compile wraps re.compile.

    If you add two big.string objects together that came from different origins:
        a = big.string('abcde', source='foo')
        b = big.string('vwxyz', source='bar')
        c = a + b
    the resulting big.string remembers the line, column, source, origin, and
    offset for each individual character in the result:
        >>> print(c.where)
        "foo line 1 column 1"
        >>> print(c[5].where)
        "bar line 1 column 1"
    """

    __slots__ = (
        '_ranges',
        '_length',
        '_line_number',
        '_column_number',
        '_source',
        '_origin',
        '_offset',
        )

    def __new__(cls, s='', *, source=None, line_number=1, column_number=1, first_column_number=1, tab_width=8):
        if isinstance(s, string):
            return s

        if not isinstance(s, str):
            raise TypeError(f"unhandled type {type(s).__name__} for initializer s")

        if not ((source is None) or isinstance(source, str)):
            raise TypeError(f"source must be str, not {type(source).__name__}")

        if not isinstance(line_number, int):
            raise TypeError(f"line_number must be int, not {type(line_number).__name__}")
        if line_number < 0:
            raise ValueError(f"line_number must be >= 0, not {line_number}")

        if not isinstance(column_number, int):
            raise TypeError(f"column_number must be int, not {type(column_number).__name__}")
        if column_number < 0:
            raise ValueError(f"column_number must be >= 0, not {column_number}")

        if not isinstance(first_column_number, int):
            raise TypeError(f"first_column_number must be int, not {type(first_column_number).__name__}")
        if first_column_number < 0:
            raise ValueError(f"first_column_number must be >= 0, not {first_column_number}")
        if column_number < first_column_number:
            raise ValueError(f"column_number is {column_number}, must be >= first_column_number which is {first_column_number}")


        if not isinstance(tab_width, int):
            raise TypeError(f"tab_width must be int, not {type(tab_width).__name__}")
        if tab_width < 1:
            raise ValueError(f"tab_width must be >= 1, not {tab_width}")

        origin = Origin(s, source, line_number, column_number, first_column_number, tab_width)
        length = len(s)
        ranges = [Range(origin, 0, length)]

        self = super().__new__(cls, s)
        self._ranges = ranges
        self._length = length

        self._line_number = line_number
        self._column_number = column_number
        self._source = source

        self._origin = self
        self._offset = 0

        origin.string = self

        return self

    def __repr__(self):
        # return f"<string {str(self)!r} _ranges={self._ranges} _length={self._length}, _line_number={self._line_number}, _column_number={self._column_number}>"
        # sorry--but if the repr doesn't look *exactly* like str's repr, it breaks too much code.
        return repr(str(self))

    def _compute_line_and_column(self):
        r = self._ranges[0]
        self._line_number, self._column_number = r.origin.compute_line_and_column(r.start)

    @property
    def line_number(self):
        if self._line_number is None:
            self._compute_line_and_column()
        return self._line_number

    @property
    def column_number(self):
        if self._line_number is None:
            self._compute_line_and_column()
        return self._column_number

    @property
    def offset(self):
        return self._offset

    @property
    def origin(self):
        return self._origin

    @property
    def source(self):
        return self._source

    # these are rarely used, so don't cache them in the string
    @property
    def first_column_number(self):
        return self._ranges[0].origin.first_column_number

    @property
    def tab_width(self):
        return self._ranges[0].origin.tab_width

    @property
    def where(self):
        if self._line_number is None:
            self._compute_line_and_column()
        source = self._source
        if source:
            prefix = f'{source} '
        else:
            prefix = ''
        return f'{prefix}line {self._line_number} column {self._column_number}'

    def __getitem__(self, index):
        if isinstance(index, slice):
            start = index.start
            stop = index.stop
            step = index.step

            length = self._length

            # slice clamps >:(
            if start is None:
                start = 0
            else:
                if start < 0:
                    start += length
                    if start < 0:
                        start = 0
                elif start > length:
                    start = length

            if stop is None:
                stop = length
            else:
                if stop < 0:
                    stop += length
                    if stop < 0:
                        stop = 0
                elif stop > length:
                    stop = length

            if stop < start:
                stop = start

            if step is None:
                step = 1
            else:
                assert step > 0

            if step == 1:
                start_stops = ((start, stop),)
                length = stop - start
            else:
                start_stops = tuple((x, x+1) for x in list(range(start, stop, step)))
                length = len(start_stops)

        else:
            if index < 0:
                index += self._length
                if index < 0:
                    raise IndexError("string index out of range")
            if index >= self._length:
                raise IndexError("string index out of range")
            start_stops = ((index, index+1),)
            length = 1

        # print()
        # print(f">> {start_stops=}")
        ranges = []
        strings = []
        for start, stop in start_stops:
            # print(f"{start=} {stop=}")
            for r in self._ranges:
                r_length = r.stop - r.start
                if (start > r_length) or (stop > r_length):
                    start -= r_length
                    stop -= r_length
                    continue

                    # print(f">> {start=} {stop=}")
                    # print(f">> r length {r_length} {r}")

                last_one = length <= r_length
                if last_one:
                    stop_at = stop + r.start
                else:
                    stop_at = r.stop

                new_range = Range(r.origin, start + r.start, stop_at)
                ranges.append(new_range)
                strings.append(r.origin.s[start + r.start:stop_at])

                if last_one:
                    break
                start = 0
                stop -= r_length
                length -= r_length

        # print(f">> {len(ranges)=} {ranges=}")
        range0 = ranges[0]
        origin = range0.origin

        new = super().__new__(self.__class__, ''.join(strings))
        new._ranges = ranges
        new._length = length

        new._line_number = new._column_number = None
        new._source = origin.source

        new._offset = range0.start
        new._origin = origin.string

        return new

    def __iter__(self):
        new_call = super().__new__
        cls = self.__class__
        for r in self._ranges:
            origin = r.origin
            s = origin.s
            source = origin.source
            first_column_number = origin.first_column_number
            tab_width = origin.tab_width
            origin_string = origin.string

            compute_line_and_column_counter = 1

            for start in range(r.start, r.stop):
                c = s[start]

                new = new_call(cls, c)
                new._ranges = [Range(origin, start, start+1)]
                new._length = 1

                # origin.compute_line_and_column is slow,
                # only call it for tricky characters
                if (c == '\t') or (c in _linebreaks_and_tab_set):
                    compute_line_and_column_counter = 2

                if compute_line_and_column_counter:
                    compute_line_and_column_counter -= 1
                    new._line_number = new._column_number = None
                    # this causes a call to origin.compute_line_and_column,
                    # and we cache the results
                    line_number = new.line_number
                    column_number = new.column_number
                else:
                    new._line_number = line_number
                    new._column_number = column_number
                column_number += 1

                new._source = source

                new._offset = start
                new._origin = origin_string

                yield new

    @staticmethod
    def _append_ranges(r, r2):
        # if we're contiguous, simply extend the range
        r_last = r[-1]
        r2_first = r2[0]
        if (r_last.origin == r2_first.origin) and (r_last.stop == r2_first.start):
            contiguous = Range(r_last.origin, r_last.start, r2_first.stop)
            r[-1] = contiguous
            if len(r2) > 1:
                r.extend(r2[1:])
        else:
            r.extend(r2)

    def __add__(self, other):
        other_is_str =    isinstance(other, str)
        other_is_string = isinstance(other, string)
        if not (other_is_str or other_is_string):
            raise TypeError(f'can only concatenate str or string (not "{type(other)}") to string')

        if not other:
            return self

        if other_is_str:
            other = string(other)
        if not self._length:
            return other

        s = str(self) + str(other)

        ranges = list(self._ranges)
        self._append_ranges(ranges, other._ranges)

        range0 = ranges[0]
        origin = range0.origin

        new = super().__new__(self.__class__, s)
        new._ranges = ranges
        new._length = self._length + other._length

        # if they cached it, we get their cached copies.
        # otherwise, we're no worse off.
        new._line_number = self._line_number
        new._column_number = self._column_number

        new._source = origin.source

        new._offset = range0.start
        new._origin = origin.string

        return new

    def __radd__(self, other):
        if not isinstance(other, str):
            return NotImplemented
            # raise TypeError(f'unsupported operand type(s) for +: "{type(other)}" and string')

        # if other were a string, then we'd be in other.__add__, not self.__radd__
        assert not isinstance(other, string)

        left = string(other)
        if not self:
            return left
        return left.__add__(self)

    #
    # these pad the string.  so, we can just add stuff,
    # but contain the original string too.
    #
    def ljust(self, width, fillchar=' '):
        if not isinstance(fillchar, str):
            raise TypeError(f"The fill character must be a unicode character, not {type(fillchar).__name__}")
        if len(fillchar) != 1:
            # why is it TypeError?  blame str.
            raise TypeError("The fill character must be exactly one character long")

        length = len(self)
        if length >= width:
            return self

        needed = width - length
        spacer = fillchar * needed

        return self + spacer

    def rjust(self, width, fillchar=' '):
        if not isinstance(fillchar, str):
            raise TypeError(f"The fill character must be a unicode character, not {type(fillchar).__name__}")
        if len(fillchar) != 1:
            # why is it TypeError?  blame str.
            raise TypeError("The fill character must be exactly one character long")

        length = len(self)
        if length >= width:
            return self

        needed = width - length
        spacer = fillchar * needed

        return spacer + self

    def zfill(self, width):
        return self.rjust(width, '0')

    def center(self, width, fillchar=' '):
        if not isinstance(fillchar, str):
            raise TypeError(f"The fill character must be a unicode character, not {type(fillchar).__name__}")
        if len(fillchar) != 1:
            # why is it TypeError?  blame str.
            raise TypeError("The fill character must be exactly one character long")

        if self._length >= width:
            return self

        width -= self._length
        left_width = right_width = width // 2
        if width != (left_width + right_width):
            # we need an extra space on either left or right.
            assert width == (left_width + right_width) + 1
            # if self is an odd number of characters, add the extra char on the right
            if self._length % 2:
                right_width += 1
            else:
                left_width += 1
        left_padding = fillchar * left_width
        if left_width == right_width:
            right_padding = left_padding
        else:
            right_padding = fillchar * right_width
        return left_padding + self + right_padding



    #
    # these functions might return the same string,
    # or they might return a mutated string.
    # if the string doesn't change, return self.
    # otherwise return a new string.
    #
    def capitalize(self):
        s = str(self)
        mutated = s.capitalize()
        if s == mutated:
            return self
        return mutated

    def casefold(self):
        s = str(self)
        mutated = s.casefold()
        if s == mutated:
            return self
        return mutated

    def expandtabs(self, tabsize=8):
        s = str(self)
        mutated = s.expandtabs(tabsize)
        if s == mutated:
            return self
        return mutated

    def format(self, *args, **kwargs):
        s = str(self)
        mutated = s.format(*args, **kwargs)
        if s == mutated:
            return self
        return mutated

    def format_map(self, mapping):
        s = str(self)
        mutated = s.format_map(mapping)
        if s == mutated:
            return self
        return mutated

    def lower(self):
        s = str(self)
        mutated = s.lower()
        if s == mutated:
            return self
        return mutated

    def replace(self, old, new, count=-1):
        # big.string++!
        # preserve the substrings of the original.

        if count == 0:
            return self
        s = str(self)
        if s.find(old) == -1:
            return self

        old_length = len(old)
        start = 0
        result = []
        append = result.append

        while True:
            index = s.find(old, start)
            if (count == 0) or (index == -1):
                append(self[start:])
                break
            append(self[start:index])
            append(new)
            count -= 1
            start = index + old_length
        return self._cat(result)

    def swapcase(self):
        s = str(self)
        mutated = s.swapcase()
        if s == mutated:
            return self
        return mutated

    def title(self):
        s = str(self)
        mutated = s.title()
        if s == mutated:
            return self
        return mutated

    def upper(self):
        s = str(self)
        mutated = s.upper()
        if s == mutated:
            return self
        return mutated

    #
    # these return substrings of the original string.
    # we can always return string objects!
    #
    def lstrip(self, chars=None):
        s = str(self)
        lstripped = s.lstrip(chars)
        index = len(s) - len(lstripped)
        if not index:
            return self

        return self[index:]

    def rstrip(self, chars=None):
        s = str(self)
        rstripped = s.rstrip()
        reverse_index = len(s) - len(rstripped)
        if not reverse_index:
            return self

        return self[:-reverse_index]

    def strip(self, chars=None):
        s = str(self)
        s_length = len(s)

        lstripped = s.lstrip(chars)
        lstripped_length = len(lstripped)

        rstripped = s.rstrip(chars)
        rstripped_length = len(rstripped)

        if s_length == lstripped_length == rstripped_length:
            return self
        start = s_length - lstripped_length
        end = rstripped_length - s_length
        if not end:
            end = s_length

        return self[start:end]

    def removeprefix(self, prefix):
        # new in Python 3.11 (I think?)
        # but string will support it all the way back to 3.6.
        s = str(self)
        if not s.startswith(prefix):
            return self
        return self[len(prefix):]

    def removesuffix(self, suffix):
        # new in Python 3.11 (I think?)
        # but string will support it all the way back to 3.6.
        s = str(self)
        if not s.endswith(suffix):
            return self
        return self[:-len(suffix)]


    def _partition(self, sep, count, reversed):
        self_length = len(self)

        if reversed:
            find = self.rfind
            start = self[0:0]
        else:
            find = self.find
            end = self[self_length:self_length]

        # fast path for most common case
        if count == 1:
            match_offset = find(sep)

            if match_offset == -1:
                if reversed:
                    return (start, start, self)
                return (self, end, end)

            after_offset = match_offset + len(sep)

            before = self[:match_offset]
            match =  self[match_offset:after_offset]
            after  = self[after_offset:]

            return (before, match, after)

        # special case for 0, ensure we return self
        if count == 0:
            return (self,)

        result = []
        append = result.append
        extend = result.extend

        no_more_matches = False

        if reversed:
            padding = (start, start)
        else:
            padding = (end, end)
        find_starting_offset = 0
        find_ending_offset = self_length

        for _ in range(count):
            if no_more_matches:
                extend(padding)
                continue

            match_offset = find(sep, find_starting_offset, find_ending_offset)
            no_more_matches = match_offset == -1
            if no_more_matches:
                if reversed:
                    append(self[:find_ending_offset])
                    append(start)
                else:
                    append(self[find_starting_offset:])
                    append(end)
                continue

            after_offset = match_offset + len(sep)
            match = self[match_offset:after_offset]

            if reversed:
                after = self[after_offset:find_ending_offset]
                append(after)
                find_ending_offset = match_offset
            else:
                before = self[find_starting_offset:match_offset]
                append(before)
                find_starting_offset = after_offset
            append(match)

        if reversed:
            if no_more_matches:
                append(start)
            else:
                append(self[:find_ending_offset])
            result.reverse()
        else:
            if no_more_matches:
                append(end)
            else:
                append(self[find_starting_offset:])

        return tuple(result)


    def partition(self, sep, count=1):
        return self._partition(sep, count, False)

    def rpartition(self, sep, count=1):
        return self._partition(sep, count, True)


    def _split(self, sep, maxsplit, reverse):
        # for now, just worry about correctness.
        # we can make this faster later.
        # (that said, this seems like it's okay.)
        #
        # this splits the string using split/rsplit,
        # then finds those segments in the original string

        result = []
        append = result.append

        s = str(self)
        find = s.find
        sep_length = len(sep) if sep else 0
        offset = 0

        if reverse:
            substrings = s.rsplit(sep, maxsplit)
        else:
            substrings = s.split(sep, maxsplit)

        for substring in substrings:
            substring_length = len(substring)

            if not sep_length:
                # splitting by whitespace
                assert substring
                offset = find(substring, offset)

            end_of_slice = offset + substring_length
            l = self[offset:end_of_slice]
            result.append(l)

            offset = end_of_slice + sep_length

        return result

    def split(self, sep=None, maxsplit=-1):
        return self._split(sep,  maxsplit, False)

    def rsplit(self, sep=None, maxsplit=-1):
        return self._split(sep,  maxsplit, True)

    def splitlines(self, keepends=False, *, separators=linebreaks):
        l = list(multisplit(self, separators, keep=keepends, separate=True))
        if l and not l[-1]:
            l.pop()
        return l

    def join(self, iterable):
        l = list(iterable)
        if not self:
            return string._cat(l)
        l2 = list()
        append = l2.append
        for o in l:
            append(o)
            append(self)
        l2.pop()
        return string._cat(l2)

    ##
    ## isascii was added in 3.7.
    ## if we have a real isascii, use that, it's faster.
    ## but keep around _isascii for testing.
    ## (why do it this convoluted way? I wanted __name__ to be "isascii", not "_isascii".)
    ##
    def isascii(self):
        for c in self:
            if ord(c) > 127:
                return False
        return True
    _isascii = isascii
    if hasattr(str, 'isascii'):
        del isascii

    ##
    ## extensions
    ##

    def bisect(self, index):
        return self[:index], self[index:]

    @classmethod
    def _cat(cls, strings):
        if not strings:
            return string()

        for s in strings:
            if not isinstance(s, str):
                raise TypeError("arguments to cat must be str or string objects")

        if len(strings) == 1:
            s = strings[0]
            if not isinstance(s, string):
                s = string(s)
            return s

        ranges = None
        length = 0
        first_s = None
        first_range = None
        first_origin = None
        for s in strings:
            if not s:
                continue
            if isinstance(s, str):
                s = string(s)
            length += len(s)
            r = s._ranges
            if ranges is None:
                first_s = s
                first_range = r[0]
                first_origin = first_range.origin
                ranges = list(r)
            else:
                cls._append_ranges(ranges, r)

        if not length:
            return string()

        s = ''.join(str(_) for _ in strings)

        new = cls.__new__(cls, s)
        new._ranges = ranges
        new._length = length
        new._line_number = first_s._line_number
        new._column_number = first_s._column_number

        new._source = first_origin.source

        new._offset = first_range.start
        new._origin = first_origin.string

        return new

    @classmethod
    def cat(cls, *strings):
        """
        Concatenates the str / big.string objects passed in.
        Roughly equivalent to big.string('').join().
        Always returns a big.string.
        """
        return cls._cat(strings)

    def multisplit(self, separators, *,
        keep=False,
        maxsplit=-1,
        reverse=False,
        separate=False,
        strip=False,
        ):
        return multisplit(self, separators, keep=keep, maxsplit=maxsplit, reverse=reverse, separate=separate, strip=strip)

    def multipartition(self, separators, count=1, *,
        reverse=False,
        separate=False,
        ):
        return multipartition(self, separators, count=count, reverse=reverse, separate=separate)

    def generate_tokens(self):
        return generate_tokens(self)

    def compile(self, flags=0):
        return Pattern(self, flags)


#####################################################################################################
#####################################################################################################
###
###
###     oooo   o8o              oooo                        .o8       oooo   o8o               .
###     `888   `"'              `888                       "888       `888   `"'             .o8
###      888  oooo  ooo. .oo.    888  oooo   .ooooo.   .oooo888        888  oooo   .oooo.o .o888oo
###      888  `888  `888P"Y88b   888 .8P'   d88' `88b d88' `888        888  `888  d88(  "8   888
###      888   888   888   888   888888.    888ooo888 888   888        888   888  `"Y88b.    888
###      888   888   888   888   888 `88b.  888    .o 888   888        888   888  o.  )88b   888 .
###     o888o o888o o888o o888o o888o o888o `Y8bod8P' `Y8bod88P"      o888o o888o 8""888P'   "888
###
###
###  Terminology:
###      * a "cursor" is a moveable pointer into the linked list.  Really it's just
###        a reference to a node.  But I call such variables "cursor" instead of "node"
###        to communicate intent, that they by design can move around the list.
###
#####################################################################################################
#####################################################################################################


_undefined = object()

@export
class SpecialNodeError(LookupError):
    "Special nodes don't support this operation."

@export
class UndefinedIndexError(IndexError):
    "You accessed an undefined index in a linked_list (before head or after tail)."

# implementation detail, no public APIs expose nodes
_legal_special_values = set((None, 'special', 'head', 'tail'))
class linked_list_node:
    __slots__ = ('value', 'special', 'next', 'previous', 'linked_list', 'iterator_refcount')

    def __init__(self, linked_list, value, special):
        self.linked_list = linked_list
        self.value = value
        assert special in _legal_special_values
        self.special = special
        self.next = self.previous = None
        self.iterator_refcount = 0

    def insert_before(self, value, special=None):
        "inserts value into the linked list in front of self."

        if self.special == 'head':
            raise UndefinedIndexError("can't insert before head")
        assert self.previous

        linked_list = self.linked_list

        node = self.__class__(linked_list, value, special)
        previous = self.previous

        node.next = self
        node.previous = previous
        previous.next = self.previous = node

        if special is None:
            linked_list._length += 1

        return node

    def clear(self):
        self.special = self.previous = self.next = self.value = self.iterator_refcount = None

    def unlink(self):
        # don't bother checking if self.special == 'special' or whatnot.
        # we might get called during shutdown while the GC is trying to
        # break cycles.  all we should do is--carefully--unlink the node.

        previous = self.previous
        next = self.next

        if previous:
            previous.next = next
        if next:
            next.previous = previous

        if self.special is None:
            linked_list = getattr(self, 'linked_list', None)
            if linked_list is not None:
                length = getattr(linked_list, '_length', None)
                if length is not None:
                    linked_list._length = length - 1

        self.clear()

    def remove(self):
        assert not self.special

        value = self.value

        if not self.iterator_refcount:
            self.unlink()
        else:
            self.special = 'special'
            self.value = None
            self.linked_list._length -= 1

        return value

    def index(self, index, allow_head_and_tail=False):
        # return a cursor (pointer to a node),
        # starting at the current position,
        # relative to index.  ignores special nodes.
        # if we attempt to iterate past the end of the list
        # in either direction, return None.
        #
        # if index==0, returns self, even if self is a special node.

        if not hasattr(index, '__index__'):
            raise TypeError("linked_list indices must be integers or slices")
        index = index.__index__()
        cursor = self

        if index < 0:
            while index:
                c = cursor.previous
                if c is None:
                    # went off the end
                    return None
                cursor = c
                if c.special:
                    if (not allow_head_and_tail) or (c.special != 'head'):
                        continue
                index += 1
            return cursor

        while index:
            c = cursor.next
            if c is None:
                # went off the end
                return None
            cursor = c
            if c.special:
                if (not allow_head_and_tail) or (c.special != 'tail'):
                    continue
            index -= 1
        return cursor


    def nodes(self, start, first, stop, last, step):
        """
        This is a generator.
        BUT.  It's never returned to the user.
        Which means the user can never delete a node while we've yielded to them.
        So, this function is deliberately written in an "unsafe" way, where it
        doesn't incref/decref iterator_refcount, and it doesn't check to see if a
        node's iterator_refcount drops to 0.
        """
        # print(f">> nodes {start=} {stop=} {step=} {first=} {last=}")

        cursor = first
        index = start

        for i in range(start, stop, step):
            if i == 0:
                # index 0 is *always* self.
                # if self is deleted, we *just skip over it.*
                cursor = self
                index = 0
                if self.special:
                    raise SpecialNodeError()

            elif index < i:
                while index < i:
                    # we pre-measured, we should never be tail
                    assert cursor.special != 'tail'
                    cursor = cursor.next
                    # regression: if cursor is self,
                    # we don't simply skip past it.
                    # it's always counted as index 0.
                    if (cursor is self) or (not cursor.special):
                        index += 1
            elif index > i:
                while index > i:
                    # we pre-measured, we should never be head
                    assert cursor.special != 'head'
                    cursor = cursor.previous
                    # regression: if cursor is self,
                    # we don't simply skip past it.
                    # it's always counted as index 0.
                    if (cursor is self) or (not cursor.special):
                        index -= 1

            assert index == i
            # print(">> yield", cursor)
            yield cursor

    nodes_iterator = nodes

    def nodes(self, start, stop, step):
        """
        Returns None if either start or stop is out of range.
        Iterator, yields nodes.
        """
        # print(f"nodes {start=} {stop=} {step=}")

        if not hasattr(step, '__index__'):
            raise TypeError("linked_list indices must be integers or slices")
        step = step.__index__()
        if not step:
            raise ValueError("step must not be 0")

        if not hasattr(start, '__index__'):
            raise TypeError("linked_list indices must be integers or slices")
        if not hasattr(stop, '__index__'):
            raise TypeError("linked_list indices must be integers or slices")
        start = start.__index__()
        stop = stop.__index__()

        first = self.index(start, allow_head_and_tail=True)
        last = self.index(stop, allow_head_and_tail=True)
        if (first is None) or (last is None):
            return None

        if step < 0:
            if start <= stop:
                return iter(())
        elif start >= stop:
            return iter(())

        # print("returning an iterator")
        return self.nodes_iterator(start, first, stop, last, step)


    def __repr__(self):
        if self.special:
            special = f', special={self.special!r}'
        else:
            special = ''
        return f"linked_list_node({self.value!r}{special})"


@export
class linked_list:
    """
    A Python linked list.

    linked_list objects have an interface similar to
    the list or collections.deque objects.  You can
    prepend() or append() nodes, or insert() at any index.
    (You can also extend() or rextend() an iterable.)

    You can also extract ranges of nodes using cut(),
    and merge one linked list into another using splice().

    In addition, an *iterator* over a linked list object
    is something like a database cursor.  It behaves like
    a list object, relative to the node it's pointing to.
    (When a linked_list iterator yields the value N, it
    continues to point to the node containing the value N
    until you call next on it.)
    """

    __slots__ = ('_head', '_tail', '_length')

    def __init__(self, iterable=()):
        self._head = head = linked_list_node(self, None, 'head')
        head.next = self._tail = tail = linked_list_node(self, None, 'tail')
        tail.previous = self._head
        self._length = 0
        for value in iterable:
            self.append(value)

    def __repr__(self):
        buffer = ["linked_list(["]
        append = buffer.append
        cursor = self._head.next
        tail = self._tail
        separator = ''
        while cursor != tail:
            if not cursor.special:
                append(separator)
                separator = ', '
                append(repr(cursor.value))
            cursor = cursor.next
        append("])")
        return ''.join(buffer)

    ##
    ## implement the six rich comparison methods
    ## using *only* the relevant operator and ==:
    ##
    ##     * in __lt__, only use <  and ==
    ##     * in __le__, only use <= and ==
    ##     * in __ge__, only use >= and ==
    ##     * in __gt__, only use >  and ==
    ##     * in __eq__, only use ==
    ##     * in __ne__, only use !=
    ##
    ## (well, also len() on the list itself.)
    ##
    ## why?  trying to honor this statement from
    ## the Python docs:
    ##
    ##     There are no other implied relationships
    ##     among the comparison operators or default
    ##     implementations; for example, the truth of
    ##     (x<y or x==y) does not imply x<=y.
    ##

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        for value1, value2 in zip(iter(self), iter(other)):
            if value1 == value2:
                continue
            return False
        return len(self) == len(other)

    def __ne__(self, other):
        if self.__class__ != other.__class__:
            return True
        for value1, value2 in zip(iter(self), iter(other)):
            if value1 != value2:
                return True
        return len(self) != len(other)

    def __lt__(self, other):
        if self.__class__ != other.__class__:
            return NotImplemented
        for value1, value2 in zip(iter(self), iter(other)):
            if value1 < value2:
                return True
            if value1 == value2:
                continue
            # value1 > value2
            return False
        return len(self) < len(other)

    def __le__(self, other):
        if self.__class__ != other.__class__:
            return NotImplemented
        for value1, value2 in zip(iter(self), iter(other)):
            if value1 <= value2:
                if value1 == value2:
                    continue
                return True
            # value1 > value2
            return False
        return len(self) <= len(other)

    def __ge__(self, other):
        if self.__class__ != other.__class__:
            return NotImplemented
        for value1, value2 in zip(iter(self), iter(other)):
            if value1 >= value2:
                if value1 == value2:
                    continue
                return True
            # value1 < value2
            return False
        return len(self) >= len(other)

    def __gt__(self, other):
        if self.__class__ != other.__class__:
            return NotImplemented
        for value1, value2 in zip(iter(self), iter(other)):
            if value1 > value2:
                return True
            if value1 == value2:
                continue
            # value1 < value2
            return False
        return len(self) > len(other)


    def __copy__(self):
        return linked_list(self)

    def copy(self):
        return self.__copy__()

    def __deepcopy__(self, memo):
        t = linked_list()
        for value in self:
            t.append(copy.deepcopy(value, memo))
        return t

    # new in 3.7
    def __class_getitem__(cls, item): # pragma nocover
        return GenericAlias(cls, (item,))

    def __add__(self, other):
        t = self.__copy__()
        t.extend(other)
        return t

    def __iadd__(self, other):
        self.extend(other)
        return self

    def __mul__(self, other):
        if not hasattr(other, '__index__'):
            raise TypeError(f"can't multiply sequence by non-int of type {type(other)!r}")
        index = other.__index__()
        if other <= 0:
            return linked_list()
        t = self.__copy__()
        for _ in range(index - 1):
            t.extend(self)
        return t

    __rmul__ = __mul__

    def __imul__(self, other):
        if not hasattr(other, '__index__'):
            raise TypeError(f"can't multiply sequence by non-int of type {type(other)!r}")
        index = other.__index__()
        if other <= 0:
            return linked_list()
        t = self.__copy__()
        for _ in range(index - 1):
            self.extend(t)
        return self

    def __iter__(self):
        return linked_list_iterator(self._head)

    head = __iter__

    def tail(self):
        return linked_list_iterator(self._tail)

    def __reversed__(self):
        return linked_list_reverse_iterator(self._tail)

    def __bool__(self):
        return self._length > 0

    def __len__(self):
        return self._length

    def __contains__(self, value):
        return self.find(value) is not None

    def _cursor_at_index(self, index):
        """
        Returns a cursor at the node requested.
        index can be -1, in which case it returns head.
        index can be length, in which case it returns tail.
        (This is to accommodate slicing semantics copied from list.)
        """
        # index = index.__index__()
        length = self._length
        assert -1 <= index <= length, f"index should be >= -1 and < {length} but it's {index}"

        if index == -1:
            return self._head
        if index == length:
            return self._tail

        halfway = self._length // 2
        if index > halfway:
            # faster to start at tail and work backwards.
            # if t is 'abcdefg', length is 7.
            # if we want 'e', index is 4, 7 - 4 is 3,
            # and that's how many times we need to retreat from tail.
            #
            #              v
            # HEAD a b c d e f g TAIL
            #      0 1 2 3 4 5 6       index
            #      7 6 5 4 3 2 1 0     offset from tail
            #
            cursor = self._tail
            countdown = length - index
            for _ in range(countdown):
                cursor = cursor.previous
        else:
            cursor = self._head.next
            for _ in range(index):
                cursor = cursor.next

        return cursor

    def _it_at_index(self, index):
        """
        Indexes into a linked list.  Returns an iterator.

        index can be -1, in which case it points to head.
        index can be length, in which case it points to tail.
        This is to accommodate slicing semantics copied from 'list'.
        """
        cursor = self._cursor_at_index(index)

        it = iter(self)
        it._cursor = cursor
        return it


    def _unpack_and_adjust_slice(self, slice, *, for_assignment=False):
        """
        Unpacks slice, and clamps slice values in the same way list does.
        Returns a 4-tuple:
            (start, stop, step, slice_length)
        """

        # this is harder to get right than you might think,
        # because it's emulating foolish garbage comprised
        # of bewildering bad ideas committed against
        # the list object decades ago.
        #
        # (slicing should *not clamp*.  that's a staggering
        # misfeature.  linked_list emulates the behavior
        # simply because backwards compatibility is so important.)

        start = slice.start
        stop = slice.stop
        step = slice.step

        if step is None:
            step = 1
            step_is_positive = 1
            step_is_negative = 0
        else:
            assert step != 0
            step_is_positive = step > 0
            step_is_negative = not step_is_positive

        length = self._length
        negative_length = -length

        last_element = length - 1

        if start is None:
            if step_is_positive:
                start = 0
            else:
                start = last_element
        elif start < 0:
            if start >= negative_length:
                start += length
            elif step_is_negative:
                start = -1
            else:
                start = 0
        elif start >= length:
            if step_is_negative:
                start = last_element
            else:
                start = length

        if stop is None:
            if step_is_positive:
                stop = length
            else:
                stop = -1
        elif stop < 0:
            if stop >= negative_length:
                stop += length
            else:
                if step_is_negative:
                    stop = -1
                else:
                    stop = 0
        elif stop >= length:
            if step_is_negative:
                stop = last_element
            else:
                stop = length

        if step_is_negative and (stop < start):
            slice_length = ((start - stop - 1) // -step) + 1
        elif (not step_is_negative) and (start < stop):
            slice_length = ((stop - start - 1) // step) + 1
        else:
            slice_length = 0
            stop = start

        if slice_length:
            assert  0 <= start <= last_element, f"failed:  0 <= start={start} <= {last_element}  isn't true (slice_length={slice_length})"
        else:
            assert -1 <= start <= length, f"failed: -1 <= start={start} <= {length}  isn't true (slice_length={slice_length})"
        assert -1 <=  stop <= length, f"failed: -1 <= stop={stop} <= {length}  isn't true"

        # print(f">> [start {start:>2}] [stop {stop:>2}] [step {step:>2}] {slice_length=} [slice {slice}]")

        return start, stop, step, slice_length

    def _parse_key(self, key, *, for_assignment=False):
        """
        Parses the "key" argument from a __{get,set,del}item__ call,
        which must be either an index or a slice object.

        Returns a 6-tuple:
            (it, node, start, stop, step, slice_length)

        start is the index of the first element we want;
        it will be in the range 0 <= start < length.

        If key is a slice, stop, step, and slice_length
        will be integers.  stop will be in the same range
        as start, and step will not be zero.  slice_length
        will be how many numbers would be in the list
        if you called list(range(start, stop, step)).

        And then there's it and node!  If key is a slice,
        we're gonna try and return an iterator.  If we're
        doing something illegal, it might be none.  Otherwise
        it'll be an iterator yielding just the nodes specified.
        But maybe... that's zero nodes!  Like for a zero-length
        slice.  In which case we also return a valid node, which
        represents the end of the slice.  Again: if it is an iterator
        that yields one or more nodes, node will be None.  Otherwise
        node will be the last node from the slice.

        The API idea here is this: if it's a non-extended slice,
        then we might insert more values than we originally had
        nodes.  You can handle that effortlessly like this:
            it, node, ... = self._parse_key(...)
            for node in it:
                ...

        if key is not a slice, it, stop, step, and slice_length
        will all be None.  node will point at the node.

        it is an iterator pointing at the start'th entry.

        Emulates Python list semantics for indexing with ints vs
        slices. for example, if a has 3 elements, a[5] raises
        IndexError, but a[5:1000] evaluates to an empty list.
        (sigh.)  So, _parse_key will raise the IndexError for
        you in the first case, but will clamp the slice values
        like list does in the second case.
        """
        if isinstance(key, slice):
            start, stop, step, slice_length = self._unpack_and_adjust_slice(key, for_assignment=for_assignment)
            node_after_head = self._head.next
            it = node_after_head.nodes(start, stop, step)
            if it is None:
                calculate_node = True
            else:
                # test start stop step, does it yield anything?
                for _ in range(start, stop, step):
                    calculate_node = False
                    break
                else:
                    calculate_node = True
            if calculate_node:
                # print("START", start, "STOP", stop)
                node = self._cursor_at_index(stop)
            else:
                node = None
        else:
            length = self._length
            original_start = key
            if not hasattr(key, '__index__'):
                raise TypeError("linked_list indices must be integers or slices")
            start = key.__index__()
            if start < 0:
                start += length
            if not (0 <= start < length):
                raise UndefinedIndexError(f'index {original_start} out of range')
            stop = step = slice_length = None
            it = None
            node = self._cursor_at_index(start)

        return it, node, start, stop, step, slice_length

    def __getitem__(self, key):
        it, node, start, stop, step, slice_length = self._parse_key(key)

        if it is None: # then key is not a slice
            return node.value

        return self.__class__(o.value for o in it)

    def __setitem__(self, key, value):
        it, node, start, stop, step, slice_length = self._parse_key(key, for_assignment=True)

        if it is None: # then key is not a slice
            node.value = value
            return

        if value is self:
            raise ValueError("can't assign self to slice of self")

        # print(f"{it=} {node=} {start=} {stop=} {step=} {slice_length=}")

        if step == 1:
            # in case we don't ever iterate, pre-initialize node
            # to point to start
            sentinel = object()
            last = node
            advance_last = False
            next_node = None
            remove_me = None
            try:
                values = iter(value)
            except TypeError:
                raise TypeError('must assign iterable to slice') from None

            for node, value in zip_longest(it, values, fillvalue=sentinel):
                # print(f">> {node=} {value=} {sentinel=}")
                if node == sentinel:
                    if next_node is None:
                        next_node = last
                        if advance_last:
                            next_node = next_node.next
                    next_node.insert_before(value)
                    continue
                if value == sentinel:
                    # linked_list_node.nodes is the nodes iterator here.
                    # it doesn't handle removing the node it just yielded.
                    # So, add a one-node delay to removing the nodes.
                    if remove_me is not None:
                        remove_me.remove()
                    remove_me = node
                    continue

                node.value = value
                last = node
                advance_last = True

            if remove_me is not None:
                remove_me.remove()
            return

        try:
            values = value
            values_length = len(value)
        except TypeError:
            try:
                values = list(value)
                values_length = len(values)
            except TypeError:
                raise TypeError('must assign iterable to extended slice') from None

        if slice_length != values_length:
            raise ValueError(f"attempt to assign sequence of size {values_length} to extended slice of size {slice_length}")

        for node, v in zip(it, values):
            node.value = v

    def __delitem__(self, key):
        it, node, start, stop, step, slice_length = self._parse_key(key)

        if it is None: # then key is not a slice
            node.remove()
            return

        # linked_list_node.nodes is the nodes iterator here.
        # it doesn't handle removing the node it just yielded.
        # So, add a one-node delay to removing the nodes.
        remove_me = None
        for node in it:
            if remove_me is not None:
                remove_me.remove()
            remove_me = node

        if remove_me is not None:
            remove_me.remove()

    def insert(self, index, object):
        length = self._length
        # convert index to range 0 <= index <= length
        if not hasattr(index, '__index__'):
            raise TypeError("linked_list indices must be integers or slices")
        index = index.__index__()
        if index <= -length:
            index = 0
        elif index < 0:
            index += length
        elif index > length:
            index = length
        it = self._it_at_index(index)
        it._cursor.insert_before(object)

    def append(self, object):
        self._tail.insert_before(object)

    def prepend(self, object):
        self._head.next.insert_before(object)

    # some aliases for you
    appendleft = prepend
    rappend = prepend

    def extend(self, iterable):
        if iterable is self:
            raise ValueError("can't extend self with self")
        insert_before = self._tail.insert_before
        for value in iterable:
            insert_before(value)

    def rextend(self, iterable):
        if iterable is self:
            raise ValueError("can't rextend self with self")
        insert_before = self._head.next.insert_before
        for value in iterable:
            insert_before(value)

    # don't alias "rextend" as "appendleft", they have different semantics!
    # collections.deque.appendleft inserts the items in reverse order,
    #   which is dumb and is behavior nobody wants.
    # linked_list.rextend inserts the items in forwards order,
    #   which is smart and is the behavior everybody actually wants.


    def clear(self):
        head = self._head
        tail = self._tail

        previous = head
        # point cursor at the first node *after* head.
        # (if that's tail, this will be quick!)
        cursor = head.next

        # iterate through all nodes,
        # keep nodes with a >0 iterator_refcount,
        # manually re-linking them into the list.
        while cursor != tail:
            next = cursor.next
            if cursor.iterator_refcount:
                # keep node, but demote to 'special'
                previous.special = 'special'
                previous.value = None

                previous.next = cursor
                cursor.previous = previous

                previous = cursor
            else:
                # drop node
                cursor.clear()
            cursor = next

        tail.previous = previous
        previous.next = tail
        self._length = 0

    def pop(self):
        node_before_tail = self._tail.previous
        while node_before_tail.special == 'special':
            node_before_tail = node_before_tail.previous
        if node_before_tail == self._head:
            raise ValueError('pop from empty linked_list')
        return node_before_tail.remove()

    def popleft(self):
        node_after_head = self._head.next
        while node_after_head.special == 'special':
            node_after_head = node_after_head.next
        if node_after_head == self._tail:
            raise ValueError('pop from empty linked_list')
        return node_after_head.remove()

    def count(self, value):
        return self.head().count(value)

    def find(self, value):
        return self.head().find(value)

    def rfind(self, value):
        return self.tail().rfind(value)

    def match(self, predicate):
        return self.head().match(predicate)

    def rmatch(self, predicate):
        return self.tail().rmatch(predicate)

    def remove(self, value, default=_undefined):
        it = self.head().find(value)
        if it is None:
            if default is not _undefined:
                return default
            raise ValueError('{value!r} not in linked list')
        assert not it._cursor.special # find should never return a special node
        return it._cursor.remove()

    def rremove(self, value, default=_undefined):
        it = self.tail().rfind(value)
        if it is None:
            if default is not _undefined:
                return default
            raise ValueError(f'{value!r} not in linked list')
        assert not it._cursor.special # find should never return a special node
        return it._cursor.remove()

    def reverse(self):
        # reverse in-place

        previous_fit_cursor = None
        fit = iter(self)
        rit = reversed(self)

        while True:
            next(fit)
            next(rit)
            if ((rit._cursor == fit._cursor) # odd # of nodes
                or (rit._cursor == previous_fit_cursor)): # even # of nodes
                break

            tmp = fit._cursor.value
            fit._cursor.value = rit._cursor.value
            rit._cursor.value = tmp

            previous_fit_cursor = fit._cursor

    def sort(self, key=None, reverse=False):
        # copy to list, sort, then write back in-place

        l = list(self)
        l.sort(key=key, reverse=reverse)

        it = iter(self)
        for v in l:
            next(it)
            it._cursor.value = v

    def rotate(self, n):
        n_is_negative = (n < 0)
        n = abs(n) % self._length
        if (not n) or (self._length < 2):
            return

        it = (iter if n_is_negative else reversed)(self)
        for _ in range(n + n_is_negative):
            it.next()

        segment_1_head = self._head.next
        segment_1_tail = it._cursor.previous

        segment_2_head = it._cursor
        segment_2_tail = self._tail.previous

        assert isinstance(segment_1_head, linked_list_node)
        assert isinstance(segment_1_tail, linked_list_node)
        assert isinstance(segment_2_head, linked_list_node)
        assert isinstance(segment_2_tail, linked_list_node)

        self._head.next = segment_2_head
        segment_2_head.previous = self._head

        self._tail.previous = segment_1_tail
        segment_1_tail.next = self._tail

        segment_2_tail.next = segment_1_head
        segment_1_head.previous = segment_2_tail


    def _cut(self, start, stop, is_rcut):
        """
        if is_rcut is true, then start comes after stop.
            start is still inclusive.
            stop is still exclusive.
        """
        start_is_none = start is None
        stop_is_none = stop is None

        # compute this now, before we potentially invert is_rcut
        _cut = "rcut" if is_rcut else "cut"

        # {name}_directions is a bitfield indicating supported iterator directions:
        #   1 means "forward"
        #   2 means "reverse"
        #   3 means both "forward" and "reverse"

        if start_is_none:
            start_directions = 3
        else:
            if start._cursor.linked_list is not self:
                raise ValueError(f"start is not an iterator over this linked_list, start={start!r}")
            start_directions = 2 if isinstance(start, linked_list_reverse_iterator) else 1

        if stop_is_none:
            stop_directions = 3
        else:
            if stop._cursor.linked_list is not self:
                raise ValueError(f"stop is not an iterator over this linked_list, stop={stop!r}")
            stop_directions = 2 if isinstance(stop, linked_list_reverse_iterator) else 1

        if not (start_directions & stop_directions):
            raise ValueError("mismatched forward and reverse iterators for start and stop, start={start!r}, stop={stop!r}")

        if (start_directions == 2) or (stop_directions == 2):
            # if the user is cutting using reverse iterators,
            # negate is_rcut *here*
            is_rcut = not is_rcut

        t2 = self.__class__()

        if not is_rcut:
            # cut
            if start_is_none:
                start = self._head.next
            else:
                if start._cursor is self._head:
                    # only permissible if stop is also _head
                    if start == stop:
                        return t2
                    raise SpecialNodeError(f"can't {_cut} head")
                start = start._cursor

            # convert stop to a cursor, and make it inclusive
            if stop_is_none:
                stop = self._tail
            else:
                stop = stop._cursor

            if start == stop:
                return t2

            stop = stop.previous
        else:
            # rcut
            if start_is_none:
                start = self._tail.previous
            else:
                if start._cursor is self._tail:
                    # only permissible if stop is also _tail
                    if start == stop:
                        return t2
                    raise SpecialNodeError(f"can't {_cut} tail")
                start = start._cursor

            # convert stop to a cursor, and make it inclusive
            if stop_is_none:
                stop = self._head
            else:
                stop = stop._cursor

            if start == stop:
                return t2

            stop = stop.next

            # now swap start and stop
            tmp = start
            start = stop
            stop = tmp

        if not (start_is_none or stop_is_none):
            # if the user specified both ends of the range,
            # confirm that start comes before stop
            cursor = start
            while cursor and (cursor is not stop):
                cursor = cursor.next
            if not cursor:
                raise ValueError(f"stop points to a node before start")

        # everything checks out, and everything is prepared--we can cut!
        # start and stop are now cursors (direct references to nodes),
        # and are inclusive.
        #
        # and, we've already done all our memory allocation, before changing anything.
        # (in case an allocation fails, we won't leave the original linked list
        # in an incomplete state.)

        # "previous" points to the node in self just before the cut, and
        # "next" points to the node in self just after the cut.
        # since first can't be head, and last can't be tail, we know
        # previous and next are both defined.

        previous = start.previous
        next = stop.next

        new_head = t2._head
        new_tail = t2._tail

        new_head.next = start
        start.previous = new_head
        new_tail.previous = stop
        stop.next = new_tail

        previous.next = next
        next.previous = previous

        count = 0
        while start is not new_tail:
            assert start is not None
            start.linked_list = t2
            if start.special is None:
                count += 1
            start = start.next

        self._length -= count
        t2._length = count

        return t2


    def cut(self, start=None, stop=None):
        """
        If start is None or head, this will cut head,
        and self will grow a new head.
        If stop is None, this will cut tail, and self
        will grow a new tail.

        After the cut, start and stop will still point at
        the same nodes; however, start will point at the
        first node in the returned linked list, and stop
        won't move.

        start and stop may be reverse iterators, however the
        linked list resulting from a cut will have the elements
        in forward order.  (In general, you just swap "head"
        and "tail" in all of the descriptions above.  For
        example, if start is None and stop is specified,
        start will default to "tail".)
        """
        return self._cut(start, stop, is_rcut=False)


        # make stop inclusive.
        #
        # this is confusing enough that I had to draw a diagram to make sure I got it right.
        # in both diagrams, we have a linked list containing [1, 2, 3, 4, 5], and
        # start and stop both point to the first and last nodes.
        if not start_is_reversed:
            # both are forward iterators:
            #
            #                            next->
            #                        <-previous
            #               head - 1 - 2 - 3 - 4 - 5 - tail
            #                      ^           ^   ^
            #                      |           :   |
            #                     start        :  stop
            #                      :           :
            #  first actual node cut           :
            #                                  last actual node cut
            #
            #     * start is already inclusive.  it can't be head.
            #       but we check that in _cut, so skip it here.
            #     * stop *retreats* one node to 4 (stop = stop.previous)
            #       to make it inclusive.
            #     * if stop points to head, this is only legal if start
            #       points to head too.  but we already handled start = stop,
            #       so that can't be true here.  therefore, if we reach here
            #       and stop is head, then it's an error.
            #       (_cut checks this too, but we're about to advance stop,
            #       so we have to redundantly check it here.)
            #
            if stop is self._head:
                raise ValueError(f"stop points to a node before start")

            if stop is not None:
                stop = stop.previous
        else:
            # both are reverse iterators:
            #
            #                          <-next
            #                          previous->
            #               tail - 5 - 4 - 3 - 2 - 1 - head
            #                      ^           ^   ^
            #                      |           :   |
            #                     start        :  stop
            #                      :           :
            #  first actual node cut           :
            #                                  last actual node cut
            #
            #     * start is already inclusive.  it can't be tail.
            #       but we check that in _cut, so skip it here.
            #     * stop *advances* one node to 2 (stop = stop.next)
            #       to make it inclusive.
            #     * if stop points to tail, this is only legal if start
            #       points to tail too.  but we already handled start = stop,
            #       so that can't be true here.  therefore, if we reach here
            #       and stop is tail, then it's an error.
            #       (_cut checks this too, but we're about to advance stop,
            #       so we have to redundantly check it here.)
            #
            if stop is self._tail:
                raise ValueError(f"stop points to a node after start (and they're both reverse iterators)")
            if stop is not None:
                stop = stop.next

            # and *now* we swap start and stop.
            # (why not swap first?  it makes the error messages confusing.
            # if start is tail, raise "stop can't be tail". feh.)
            #
            tmp = start
            start = stop
            stop = tmp


        # print(f"CALLING  _CUT {start=} {stop=} {start_is_reversed=}")
        return self._cut(start, stop, start_is_reversed)

    def rcut(self, start=None, stop=None):
        return self._cut(start, stop, is_rcut=True)

    def _splice(self, other, where, cursor, special):
        """
        moves nodes from other (a linked list) to after cursor (a node).
        """

        after = cursor.next
        assert after

        other_first = other._head.next
        other_last = other._tail.previous

        cursor.next = other_first
        other_first.previous = cursor

        after.previous = other_last
        other_last.next = after

        other._head.next = other._tail
        other._tail.previous = other._head

        while cursor != after:
            cursor.linked_list = self
            cursor = cursor.next

        self._length += other._length
        other._length = 0

        if (where is not None) and (special is not None):
            where._cursor = special

    def _splice_preflight_checks(self, other, where):
        if not isinstance(other, linked_list):
            raise TypeError('other must be a linked_list')
        if other is self:
            raise ValueError("other and self are the same")

        if where is not None:
            if not isinstance(where, linked_list_base_iterator):
                raise TypeError('where must be a linked_list iterator over self')
            if where._cursor.linked_list != self:
                raise ValueError("where must be a linked_list iterator over self")

    def splice(self, other, *, where=None):
        """
        Moves nodes from other into self, at where.

        other must be a linked_list.  If successful,
        other will be empty.  (The head and tail from
        other don't move, but all other nodes move,
        including special nodes.)

        where must be an iterator over self, or None.
        if where is an iterator, the nodes are inserted
        *after* the node pointed to by where.  if where
        is None, the nodes are appended to self.
        """
        self._splice_preflight_checks(other, where)

        if not other:
            return

        special = None

        if where is None:
            cursor = self._tail.previous
        else:
            cursor = where._cursor
            if cursor is self._tail:
                special = cursor.insert_before(None, 'special')
                cursor = special

        self._splice(other, where, cursor, special)

    def rsplice(self, other, *, where=None):
        self._splice_preflight_checks(other, where)

        if not other:
            return

        special = None

        if where is None:
            cursor = self._head
        else:
            cursor = where._cursor
            if cursor.special == 'head':
                special = cursor.next.insert_before(None, 'special')
                cursor = special
            else:
                cursor = cursor.previous

        self._splice(other, where, cursor, special)

    # special list compatibility layer
    def index(self, value, start=None, stop=None):
        def exp():
            return ValueError(f'{value!r} is not in linked_list')

        it = iter(self)
        # slightly clever: pass in it as "default".
        # we know it can't be in the list, we just created it.
        v = it.next(it)
        if v is it:
            raise exp()

        if start is None:
            start = index = 0
        else:
            v = it.next(it, count=start)
            if v is it:
                raise exp()
            index = start

        if stop is not None:
            delta = stop - start
            if delta <= 0:
                raise exp()
            stop = it.copy()
            stop.next(None, count=delta)

        while it != stop:
            if it[0] == value:
                return index
            index += 1
            result = it.next(it)
            if result is it:
                raise exp()
        raise exp()


    # special deque compatibility layer
    def extendleft(self, iterable):
        if iterable is self:
            raise ValueError("can't extendleft self with self")
        self.rextend(reversed(iterable))

    maxlen = None


_sentinel = object()

@export
class linked_list_base_iterator:
    __slots__ = ('_cursor',)

    def __init__(self, node):
        if type(self) == linked_list_base_iterator:
            raise TypeError("linked_list_base_iterator is an abstract base class")
        node.iterator_refcount += 1
        self._cursor = node

    @property
    def linked_list(self):
        return self._cursor.linked_list

    # new in 3.7
    def __class_getitem__(cls, item): # pragma nocover
        return GenericAlias(cls, (item,))

    def __repr__(self):
        return f"<{self.__class__.__name__} {hex(id(self))} cursor={self._cursor!r}>"

    def __del__(self):
        # drop our reference to the current node.
        # that means decrementing node.iterator_refcount.
        # and if node.iterator_refcount reaches 0,
        # we *gotta* call unlink.
        cursor = getattr(self, '_cursor', None)
        if cursor is None:
            return
        setattr(self, '_cursor', None)
        iterator_refcount = getattr(cursor, 'iterator_refcount', None)
        if iterator_refcount is None:
            return
        iterator_refcount -= 1
        setattr(cursor, 'iterator_refcount', iterator_refcount)
        special = getattr(cursor, 'special', None)
        if (not iterator_refcount) and (special == 'special'):
            unlink = getattr(cursor, 'unlink', None)
            if unlink is not None:
                unlink()

    def __bool__(self):
        cursor = self._cursor
        while True:
            special = cursor.special
            if special == 'tail':
                return False
            if special is None:
                return True
            cursor = cursor.next

    def __eq__(self, other):
        return (
            (self.__class__ == other.__class__)
            and (self._cursor == other._cursor)
            )

    def __iter__(self):
        return self

    def __contains__(self, value):
        return self.find(value) is not None

    def __copy__(self):
        return self.__class__(self._cursor)

    def copy(self):
        return self.__copy__()

    def __len__(self):
        length = 0
        cursor = self._cursor
        while cursor is not None:
            if not cursor.special:
                length += 1
            cursor = cursor.next

    def __next__(self):
        cursor = self._cursor
        special = cursor.special

        if special == 'tail':
            raise StopIteration

        cursor.iterator_refcount = iterator_refcount = cursor.iterator_refcount - 1
        next = cursor.next
        if (not iterator_refcount) and (special == 'special'):
            cursor.unlink()
        cursor = next
        special = cursor.special

        while special == 'special':
            cursor = cursor.next
            special = cursor.special

        self._cursor = cursor
        cursor.iterator_refcount += 1

        if special == 'tail':
            raise StopIteration
        return cursor.value

    def next(self, default=_undefined, *, count=1):
        if count < 0:
            raise ValueError("count can't be negative")
        if count == 0:
            return None

        if default == _undefined:
            while count > 1:
                self.__next__()
                count -= 1

            return self.__next__()

        try:
            while count > 1:
                self.__next__()
                count -= 1
            return self.__next__()
        except StopIteration:
            return default

    def __previous__(self):
        cursor = self._cursor
        special = cursor.special

        if special == 'head':
            raise StopIteration

        cursor.iterator_refcount = iterator_refcount = cursor.iterator_refcount - 1
        previous = cursor.previous
        if (not iterator_refcount) and (special == 'special'):
            cursor.unlink()
        cursor = previous
        special = cursor.special

        while special == 'special':
            cursor = cursor.previous
            special = cursor.special

        self._cursor = cursor
        cursor.iterator_refcount += 1

        if special == 'head':
            raise StopIteration
        return cursor.value

    def previous(self, default=_undefined, *, count=1):
        if count < 0:
            raise ValueError("count can't be negative")
        if count == 0:
            return None

        if default == _undefined:
            while count > 1:
                self.__previous__()
                count -= 1

            return self.__previous__()

        try:
            while count > 1:
                self.__previous__()
                count -= 1
            return self.__previous__()
        except StopIteration:
            return default

    def before(self, count=1):
        original_count = count
        if count < 0:
            raise ValueError("count can't be negative")
        cursor = self._cursor
        while count:
            cursor = cursor.previous
            if cursor is None:
                raise UndefinedIndexError("can't go past head")
            if cursor.special == 'special':
                continue
            count -= 1
        return self.__class__(cursor)

    def after(self, count=1):
        if count < 0:
            raise ValueError("count can't be negative")
        cursor = self._cursor
        while count:
            cursor = cursor.next
            if cursor is None:
                raise UndefinedIndexError("can't go past tail")
            if cursor.special == 'special':
                continue
            count -= 1
        return self.__class__(cursor)

    def reset(self):
        self._cursor = self._cursor.linked_list._head

    def exhaust(self):
        self._cursor = self._cursor.linked_list._tail

    @property
    def special(self):
        return self._cursor.special

    @property
    def is_special(self):
        return self._cursor.special is not None

    def _cursor_at_index(self, key):
        """
        Only returns a valid data node.
        If key indexes to a special node, or overshoots head/tail,
        raises an exception.
        """
        if not hasattr(key, '__index__'):
            raise TypeError("linked_list indices must be integers or slices")
        key = key.__index__()
        cursor = self._cursor
        if key == 0:
            if cursor.special:
                if cursor.special == 'special':
                    raise SpecialNodeError()
                raise UndefinedIndexError()
        else:
            c2 = cursor.index(key)
            if (c2 is None) or c2.special:
                raise UndefinedIndexError()
            cursor = c2
        return cursor

    @staticmethod
    def _unpack_slice(slice):
        result = []
        append = result.append
        for value, default in (
            (slice.start, 0),
            (slice.stop, 0),
            (slice.step, 1),
            ):
            if value is None:
                append(default)
            elif not hasattr(value, '__index__'):
                raise TypeError("linked_list indices must be integers or slices")
            else:
                append(value.__index__())
        return result

    def _slice_iterator(self, slice):
        """
        Takes a slice object.  Returns an iterator
        that yields the nodes indicated by the slice indices,
        relative to self (a linked_list iterator).
        """
        start, stop, step = self._unpack_slice(slice)
        it = self._cursor.nodes(start, stop, step)
        if it is None:
            raise ValueError(f'{slice} out of range for {self.__class__.__name__}')
        return it

    def __getitem__(self, key):
        if isinstance(key, slice):
            it = self._slice_iterator(key)
            cls = type(self._cursor.linked_list)
            return cls(node.value for node in it)
        cursor = self._cursor_at_index(key)
        return cursor.value


    def __setitem__(self, key, value):
        if not isinstance(key, slice):
            cursor = self._cursor_at_index(key)
            cursor.value = value
            return

        if value is self.linked_list:
            raise ValueError("can't assign self to slice of self")

        start, stop, step = self._unpack_slice(key)
        it = self._slice_iterator(key)
        nodes_list = list(it)
        nodes_list_length = len(nodes_list)

        values_list = list(value)
        values_list_length = len(values_list)

        delete_me = insert_me = None

        is_reverse = isinstance(self, linked_list_reverse_iterator)

        if nodes_list_length != values_list_length:
            allowable_step = -1 if is_reverse else 1
            if step != allowable_step:
                raise ValueError(f"attempt to assign sequence of size {values_list_length} to extended slice of size {nodes_list_length}")
            if nodes_list_length > values_list_length:
                # more nodes than values
                delete_me = nodes_list[values_list_length:]
            else:
                # more values than nodes
                insert_me = values_list[nodes_list_length:]

        # zip stops at the shorter of the two
        for n, v in zip(nodes_list, values_list):
            n.value = v

        if delete_me:
            for n in delete_me:
                n.remove()
        elif insert_me:
            if nodes_list:
                last_node = nodes_list[-1]
            else:
                last_node = self._cursor_at_index(stop)
            if is_reverse:
                # last_node is actually the earliest node in the list!
                while insert_me:
                    last_node.insert_before(insert_me.pop())
            else:
                node = last_node
                node = node.next
                for v in insert_me:
                    node.insert_before(v)

    def __delitem__(self, key):
        if not isinstance(key, slice):
            cursor = self._cursor_at_index(key)
            cursor.remove()
            return

        # be gentle on our lovely little list.
        # don't remove a node while the iterator is
        # pointing at it.
        waiting = None
        for n in self._slice_iterator(key):
            if waiting:
                waiting.remove()
            waiting = n

        if waiting:
            waiting.remove()

    def insert(self, index, object):
        index = index.__index__()
        if index != 0:
            cursor = self._cursor_at_index(index)
        else:
            cursor = self._cursor
        if cursor.special == 'head':
            raise UndefinedIndexError("can't insert before head")
        cursor.insert_before(object)

    def count(self, value):
        cursor = self._cursor
        tail = cursor.linked_list._tail
        counter = 0
        while cursor != tail:
            if (cursor.special is None) and (cursor.value == value):
                counter += 1
            cursor = cursor.next
        return counter

    def rcount(self, value):
        cursor = self._cursor
        head = cursor.linked_list._head
        counter = 0
        while cursor != head:
            if (cursor.special is None) and (cursor.value == value):
                counter += 1
            cursor = cursor.previous
        return counter

    def replace(self, value):
        cursor = self._cursor
        if cursor.special:
            raise SpecialNodeError()
        cursor.value = value

    def _pop(self, destination):
        # removes the node we're pointing at,
        # moves to destination, and returns the popped node's value.
        cursor = self._cursor
        if cursor.special:
            if cursor.special == 'special':
                raise SpecialNodeError()
            raise UndefinedIndexError()
        cursor.iterator_refcount -= 1
        value = cursor.remove()
        self._cursor = destination
        destination.iterator_refcount += 1
        return value

    def pop(self):
        cursor = self._cursor
        if cursor.special == 'head':
            raise UndefinedIndexError()
        cursor = cursor.previous
        while cursor.special == 'special':
            cursor = cursor.previous
        return self._pop(cursor)

    def popleft(self):
        cursor = self._cursor
        if cursor.special == 'tail':
            raise UndefinedIndexError()
        cursor = cursor.next
        while cursor.special == 'special':
            cursor = cursor.next
        return self._pop(cursor)

    def remove(self, value, default=_undefined):
        it = self.find(value)
        if it:
            return it.pop()
        if default is not _undefined:
            return default
        raise ValueError(f'value {value!r} not found')

    def rremove(self, value, default=_undefined):
        it = self.rfind(value)
        if it:
            return it.pop()
        if default is not _undefined:
            return default
        raise ValueError(f'value {value!r} not found')

    def append(self, value):
        # -- handle self pointing at tail, or not --
        cursor = self._cursor
        if cursor.special == 'tail':
            raise UndefinedIndexError("can't append to tail")
        cursor = cursor.next
        # -- actually append value --
        cursor.insert_before(value)

    def prepend(self, value):
        # -- handle self pointing at head, or not --
        cursor = self._cursor
        if cursor.special == 'head':
            raise UndefinedIndexError("can't insert before head")
        # -- actually append value --
        cursor.insert_before(value)

    appendleft = rappend = prepend

    def extend(self, iterable):
        cursor = self._cursor
        if iterable is cursor.linked_list:
            raise ValueError("can't extend self with self")
        # -- handle self pointing at tail, or not --
        if cursor.special == 'tail':
            raise UndefinedIndexError("can't append to tail")
        cursor = cursor.next
        # -- actually extend from iterator --
        counter = 0
        insert_before = cursor.insert_before
        for value in iterable:
            counter += 1
            insert_before(value)

    def rextend(self, iterable):
        cursor = self._cursor
        if iterable is cursor.linked_list:
            raise ValueError("can't rextend self with self")
        # handle self pointing at head, or not --
        if cursor.special == 'head':
            raise UndefinedIndexError("can't insert before head")
        # -- actually extend from iterator --
        counter = 0
        insert_before = cursor.insert_before
        for value in iterable:
            counter += 1
            insert_before(value)

    def find(self, value):
        cursor = self._cursor

        while True:
            special = cursor.special
            if (not special) and (cursor.value == value):
                break
            if special == 'tail':
                return None
            cursor = cursor.next

        return self.__class__(cursor)

    def rfind(self, value):
        cursor = self._cursor

        while True:
            special = cursor.special
            if (not special) and (cursor.value == value):
                break
            if special == 'head':
                return None
            cursor = cursor.previous

        return self.__class__(cursor)

    def match(self, predicate):
        cursor = self._cursor

        while True:
            special = cursor.special
            if (not special) and predicate(cursor.value):
                break
            if special == 'tail':
                return None
            cursor = cursor.next

        return self.__class__(cursor)

    def rmatch(self, predicate):
        cursor = self._cursor

        while True:
            special = cursor.special
            if (not special) and predicate(cursor.value):
                break
            if special == 'head':
                return None
            cursor = cursor.previous

        return self.__class__(cursor)

    def truncate(self):
        """
        Truncates the linked_list at the current node,
        discarding the current node and all subsequent nodes.

        After this operation, the iterator will point to the linked list's tail.
        """
        cursor = self._cursor
        t = cursor.linked_list
        tail = t._tail

        if cursor is tail:
            return

        if cursor is t._head:
            raise SpecialNodeError("can't truncate head")

        previous = cursor.previous
        count = 0
        while cursor is not tail:
            if cursor.special is None:
                count += 1
            next = cursor.next
            cursor.value = None
            if cursor.iterator_refcount:
                cursor.special = 'special'
                cursor.value = None
                previous.next = cursor
                cursor.previous = previous
                previous = cursor
            else:
                cursor.previous = cursor.next = None
            cursor = next
        tail.previous = previous
        previous.next = tail

        self._cursor = tail
        t._length -= count

    def rtruncate(self):
        """
        Truncates the linked_list at the current node,
        discarding the current node and all previous nodes.

        After this operation, the iterator will point to the linked list's head.
        """
        cursor = self._cursor
        t = cursor.linked_list
        head = t._head

        if cursor is head:
            return
        if cursor is t._tail:
            raise SpecialNodeError("can't rtruncate tail")

        next = cursor.next

        count = 0
        while cursor is not head:
            if cursor.special is None:
                count += 1
            previous = cursor.previous
            cursor.value = None
            if cursor.iterator_refcount:
                cursor.special = 'special'
                cursor.value = None
                next.previous = cursor
                cursor.next = next
                next = cursor
            else:
                cursor.previous = cursor.next = None
            cursor = previous
        head.next = next
        next.previous = head

        self._cursor = head
        t._length -= count


    def cut(self, stop=None):
        """
        Bisects the list at the current node.  Returns a new list.

        Cuts nodes from the linked list being iterated over.  Creates
        a new linked list, moves all cut nodes to this new linked_list,
        and returns this new linked list.

        If end is not None, it must be an iterator pointing to either
        the same node or a subsequent node in the same linked list;
        it's an error if end points to a preceding node, or to a node
        in a different list.  The node pointed at by end and all
        subsequent nodes are not cut.

        If end is None, all subsequent nodes are cut, including "tail".
        (The linked list is given a new "tail".)

        If cut cuts any nodes, it always cuts the node pointed to by
        self.

        All iterators pointing at nodes moved to the new list continue to
        point to those nodes.  This means they also move to the new list.
        """
        return self._cursor.linked_list.cut(self, stop)

    def rcut(self, stop=None):
        """
        Bisects the list at the current node.  Returns a new list.

        Cuts nodes from the linked list being iterated over.  Creates
        a new linked list, moves all cut nodes to this new linked_list,
        and returns this new linked list.

        If end is not None, it must be an iterator pointing to either
        the same node or a preceding node in the same linked list;
        it's an error if end points to a preceding node, or to a node
        in a different list.  The node pointed at by end and all
        preceding nodes are not cut.

        If end is None, all preceding nodes are cut, including "head".
        (The linked list is given a new "head".)

        If cut cuts any nodes, it always cuts the node pointed to by
        self.

        All iterators pointing at nodes moved to the new list continue to
        point to those nodes.  This means they also move to the new list.
        """
        return self._cursor.linked_list.rcut(self, stop)

    def splice(self, other):
        self._cursor.linked_list.splice(other, where=self)

    def rsplice(self, other):
        self._cursor.linked_list.rsplice(other, where=self)



@export
class linked_list_iterator(linked_list_base_iterator):
    """
    Iterates over the nodes of a linked list, yielding its data in order.

    Note that indexing and slicing into a linked_list iterator behaves
    differently from how slicing into a linked_list (or list) behaves.
    If i is a linked_list iterator over the linked_list j:
        * Negative indices access previous values, instead of starting
          at the end of the list and working backwards.  i[-1] returns
          the *previous* data item, not the *last* data item in the list.
        * Slicing (e.g. i[-3:5]) doesn't "clamp".  If j contains 5
          items, and i points to the middle item, you can say
              j[-9999:9999]
          without an error, but
              i[-9999:9999]
          raises a ValueError.
    """
    def __reversed__(self):
        return linked_list_reverse_iterator(self._cursor)



@export
class linked_list_reverse_iterator(linked_list_base_iterator):
    """
    Iterates over the nodes of a linked list in reverse order.

    Behaves like an iter(linked_list) object, except it yields
    the nodes

    Note that inserting or extracting a range of nodes
    (e.g. extend, rextend, )
    """
    ##
    ## the super() methods that return iterators instantiate them
    ## using self.__class__.  so, we don't need to reverse the
    ## iterators they return; they're already reverse iterators.
    ##

    def __reversed__(self):
        return linked_list_iterator(self._cursor)

    def __next__(self):
        return super().__previous__()

    def __previous__(self):
        return super().__next__()

    @staticmethod
    def _reverse_index(index):
        if not isinstance(index, slice):
            return -index
        return slice(
            None if index.start is None else -index.start,
            None if index.stop  is None else -index.stop,
              -1 if index.step  is None else -index.step,
            )

    def __getitem__(self, index):
        return super().__getitem__(self._reverse_index(index))

    def __setitem__(self, index, value):
        return super().__setitem__(self._reverse_index(index), value)

    def __delitem__(self, index):
        return super().__delitem__(self._reverse_index(index))

    def reset(self):
        self._cursor = self._cursor.linked_list._tail

    def exhaust(self):
        self._cursor = self._cursor.linked_list._head

    def before(self, count=1):
        return super().after(count)

    def after(self, count=1):
        return super().before(count)

    def __bool__(self):
        cursor = self._cursor
        while True:
            special = cursor.special
            if special == 'head':
                return False
            if special is None:
                return True
            cursor = cursor.previous

    def count(self, value):
        return super().rcount(value)

    def rcount(self, value):
        return super().count(value)

    def prepend(self, value):
        super().append(value)

    def append(self, value):
        super().prepend(value)

    def extend(self, iterable):
        if iterable is self._cursor.linked_list:
            raise ValueError("can't rextend self with self")
        super().rextend(reversed(iterable))

    def rextend(self, iterable):
        if iterable is self._cursor.linked_list:
            raise ValueError("can't rextend self with self")
        super().extend(reversed(iterable))

    def pop(self):
        return self._pop(self._cursor.next)

    def popleft(self):
        return self._pop(self._cursor.previous)

    def find(self, value):
        return super().rfind(value)

    def rfind(self, value):
        return super().find(value)

    def match(self, predicate):
        return super().rmatch(predicate)

    def rmatch(self, predicate):
        return super().match(predicate)

    def truncate(self):
        super().rtruncate()

    def rtruncate(self):
        super().truncate()

    # cut/rcut logic is sufficiently complicated, we handle all the reverse-iterator
    # and reversing stuff inside linked_list itself.  we don't even need to
    # swap them here, linked_list.cut/rcut will handle it.

    def splice(self, other):
        super().rsplice(other)

    def rsplice(self, other):
        super().splice(other)

    def __len__(self):
        length = 0
        cursor = self._cursor
        while cursor is not None:
            if not cursor.special:
                length += 1
            cursor = cursor.previous
        return length


del export
