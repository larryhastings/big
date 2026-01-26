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


from bisect import bisect_right
from collections import deque
import copy
from itertools import zip_longest
import re
import sys
import threading
try:
    from types import NoneType
except ImportError: # pragma: nocover
    NoneType = type(None)


try: # pragma nocover
    # new in 3.9
    from types import GenericAlias
except ImportError: # pragma nocover
    # backwards compatibility for 3.7 and 3.8
    # (3.6 doesn't support __class_getitem__ so we don't need it there)
    def GenericAlias(origin, args):
        s = ", ".join(t.__name__ for t in args)
        return f'{origin.__name__}[{s}]'

from .builtin import ModuleManager
from .text import linebreaks, multipartition, multisplit, Pattern
from .tokens import generate_tokens


mm = ModuleManager()
export = mm.export
delete = mm.delete
clean  = mm.clean
delete('mm', 'export', 'delete', 'clean')

__all__ = mm.__all__


_python_3_7_plus = (sys.version_info.major > 3) or ((sys.version_info.major == 3) and (sys.version_info.minor >= 7))



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

    def _clamp_index(self, index, default, name):
        if index is None:
            return default

        if not hasattr(index, '__index__'):
            raise TypeError(f'{name} must be an int, not {type(index).__name__}')
        index = index.__index__()

        length = self._length
        if index < 0:
            index += length
            if index <= 0:
                return 0
        elif index >= length:
            return length
        return index

    def __getitem__(self, index):
        if isinstance(index, slice):
            # slice clamps >:(
            clamp = self._clamp_index
            start = clamp(index.start, 0, 'start')
            stop = clamp(index.stop, self._length, 'stop')
            step = index.step

            if stop < start:
                stop = start

            if step is None:
                step = 1
            else:
                if not hasattr(step, '__index__'):
                    raise TypeError(f'step must be an int, not {type(index).__name__}')
                step = step.__index__()
                if step <= 0:
                    raise ValueError('step must be 1 or more')

            if step == 1:
                start_stops = ((start, stop),)
                length = stop - start
            else:
                start_stops = tuple((x, x+1) for x in list(range(start, stop, step)))
                length = len(start_stops)

        else:
            if not hasattr(index, '__index__'):
                raise TypeError('string index must be slice or integer (or index type)')
            index = index.__index__()
            if index < 0:
                index += self._length
                if index < 0:
                    raise IndexError("string index out of range")
            if index >= self._length:
                raise IndexError("string index out of range")
            start_stops = ((index, index+1),)
            length = 1

        ranges = []
        strings = []
        for start, stop in start_stops:
            for r in self._ranges:
                r_length = r.stop - r.start
                if (start > r_length) or (stop > r_length):
                    start -= r_length
                    stop -= r_length
                    continue

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

    def __reversed__(self):
        length = len(self)
        if length == 0:
            return

        if length == 1:
            yield self
            return

        for i in range(len(self) -1, -1, -1):
            yield self[i]

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
        if not isinstance(width, int):
            raise TypeError(f"'{type(width).__name__}' cannot be interpreted as an integer")

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
        if not isinstance(width, int):
            raise TypeError(f"'{type(width).__name__}' cannot be interpreted as an integer")

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
        if not isinstance(width, int):
            raise TypeError(f"'{type(width).__name__}' cannot be interpreted as an integer")

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

        if not isinstance(count, int):
            raise TypeError(f"'{type(count).__name__}' cannot be interpreted as an integer")
        if not isinstance(old, str):
            raise TypeError(f"replace() argument 1 must be str, not {type(count).__name__}")
        if not isinstance(new, str):
            raise TypeError(f"replace() argument 2 must be str, not {type(count).__name__}")

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
        if not isinstance(chars, (str, NoneType)):
            raise TypeError(f"lstrip arg must be str or None")
        s = str(self)
        lstripped = s.lstrip(chars)
        index = len(s) - len(lstripped)
        if not index:
            return self

        return self[index:]

    def rstrip(self, chars=None):
        if not isinstance(chars, (str, NoneType)):
            raise TypeError(f"rstrip arg must be str or None")
        s = str(self)
        rstripped = s.rstrip()
        reverse_index = len(s) - len(rstripped)
        if not reverse_index:
            return self

        return self[:-reverse_index]

    def strip(self, chars=None):
        if not isinstance(chars, (str, NoneType)):
            raise TypeError(f"strip arg must be str or None")
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
        if not isinstance(prefix, str):
            raise TypeError(f"removeprefix argument must be str, not {type(prefix).__name__}")
        s = str(self)
        if not s.startswith(prefix):
            return self
        return self[len(prefix):]

    def removesuffix(self, suffix):
        # new in Python 3.11 (I think?)
        # but string will support it all the way back to 3.6.
        if not isinstance(suffix, str):
            raise TypeError(f"removeprefix argument must be str, not {type(suffix).__name__}")
        s = str(self)
        if not s.endswith(suffix):
            return self
        return self[:-len(suffix)]


    def _partition(self, sep, count, reversed):
        if not isinstance(sep, str):
            raise TypeError(f"sep must be str, not {type(sep).__name__}")
        if not isinstance(count, int):
            raise TypeError(f"count must be int, not {type(count).__name__}")

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

        if not isinstance(sep, (str, NoneType)):
            raise TypeError(f"sep must be str, not {type(sep).__name__}")
        if not isinstance(maxsplit, int):
            raise TypeError(f"'{type(maxsplit).__name__}' object cannot be interpreted as an integer")

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
        if not hasattr(index, '__index__'):
            raise TypeError('index must be an integer (or index)')
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


class Undefined:
    def __repr__(self):
        return '<Undefined>'

    def __eq__(self, other):
        return other is self

_undefined = Undefined()

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

    def __getstate__(self):
        return (None, {
            'value': self.value,
            'special': self.special,
            'next': self.next,
            'previous': self.previous,
            'linked_list': self.linked_list,
            'iterator_refcount': self.iterator_refcount,
            })

    def insert_before(self, value, special=None):
        "inserts value into the linked list in front of self."

        assert self.special != 'head'
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


class _inert_context_manager_cls:
    def __repr__(self):
        return '<inert_context_manager>'
    def __enter__(self):
        return self
    def __exit__(self, et, ev, tr):
        return None

_inert_context_manager = _inert_context_manager_cls()

@export
class linked_list:
    """
    A Python linked list.

    linked_list objects have an interface similar to
    list or collections.deque.  You can
    prepend() or append() nodes, or insert() at any index.
    (You can also extend() or rextend() an iterable.)

    You can also extract ranges of nodes using cut(),
    and merge one linked list into another using splice().

    In addition, an *iterator* over a linked list object
    is something like a database cursor.  It behaves like
    a list object, relative to the node it's pointing to.
    (When a linked_list iterator yields the value N, it
    continues pointing to the node containing N
    until you advance it.)
    """

    __slots__ = ('_head', '_tail', '_lock', '_lock_parameter', '_length')

    def _analyze_lock(self, lock, prototype):
        # returns (lock_parameter, lock)
        if lock is True:
            return threading.Lock()
        if lock is False:
            return None
        if lock is None:
            if prototype is not None:
                return self._analyze_lock(prototype._lock_parameter, None)
            return None
        # duck-typed lock
        if (hasattr(lock, 'acquire')
            and hasattr(lock, 'release')
            and hasattr(lock, '__enter__')
            and hasattr(lock, '__exit__')
            and bool(lock)
            ):
            return lock
        raise TypeError(f"lock parameter must be bool, None, or a lock, not {type(lock).__name__}")

    def __init__(self, iterable=(), *, lock=None):
        self._head = head = linked_list_node(self, None, 'head')
        head.next = self._tail = tail = linked_list_node(self, None, 'tail')
        tail.previous = self._head

        self._length = 0

        # append the values *before* setting the lock.
        # (why bother locking before any other thread can see the list?)
        self._lock = None
        self._extend(iterable)

        self._lock_parameter = lock
        self._lock = self._analyze_lock(lock, None)

    def _repr(self):
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
        append("]")
        if self._lock:
            append(f", lock={self._lock!r}")
        append(")")
        return ''.join(buffer)

    def __repr__(self):
        with self._lock or _inert_context_manager:
            return self._repr()

    ##
    ## internal APIs for internal use by linked list objects.
    ##
    ## __eq__ and the other rich compare methods
    ## need to examine "other".  How do we proceed?
    ##
    ##    * If we only call public APIs, then if other
    ##      has a lock, we'll lock and unlock on every
    ##      method call (e.g. __next__).  This means
    ##      our __eq__ test won't be atomic, which is bad.
    ##
    ##    * If we examine internal data structures, like
    ##      _lock and _head, then we force all subclasses
    ##      to use these same attributes for the same things.
    ##      A subclass linked list might want to use a very
    ##      different implementation but would be unable to.
    ##
    ## So instead we do it the third way: we define internal-only APIs,
    ## not for public consumption, that let us interact with "other"
    ## in a safe, well-defined, performant way.  These method names
    ## all start with "_internal".
    ##
    ## There's a similar internal API for linked list iterators,
    ## with just two methods: _internal_lock and _internal_linked_list.

    def _internal_cut(self):
        ## Cuts all nodes internally.  List will be empty afterwards.
        ## Returns a tuple containing (first_node last_node).
        ##
        ## list must contain nodes.  Behavior is undefined if list is empty.
        assert self._length
        head = self._head.next
        head.previous = None
        tail = self._tail.previous
        tail.next = None

        self._head.next = self._tail
        self._tail.previous = self._head
        self._length = 0

        return (head, tail)

    def _internal_iter(self):
        ## Iterator, yields all *data nodes* in forward order.
        ## (Yields *nodes*, not *values*.  Never yields special nodes.)
        ## Does not lock!  Assumes you have already locked the list.
        cursor = self._head.next
        stop = self._tail
        while cursor is not stop:
            if cursor.special is None:
                yield cursor
            cursor = cursor.next

    def _internal_reversed(self):
        ## Iterator, yields all *data nodes* in reverse order.
        ## (Yields *nodes*, not *values*.  Never yields special nodes.)
        ## Does not lock!  Assumes you have already locked the list.
        cursor = self._tail.previous
        stop = self._head
        while cursor is not stop:
            if cursor.special is None:
                yield cursor
            cursor = cursor.previous

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

    def _two_locks(self, other):
        "Returns a list containing two context managers, in the order you should acquire them."
        self_lock = self._lock
        other_lock = other._lock
        if self_lock is None:
            return [other_lock or _inert_context_manager, _inert_context_manager]
        if other_lock in (self_lock, None):
            return [self_lock, _inert_context_manager]
        self_id = id(self_lock)
        other_id = id(other_lock)
        assert other_id != self_id
        if other_id < self_id:
            return [other_lock, self_lock]
        return [self_lock, other_lock]

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, linked_list):
            return False
        locks = self._two_locks(other)
        with locks[0], locks[1]:
            for self_node, other_node in zip(self._internal_iter(), other._internal_iter()):
                if self_node.value == other_node.value:
                    continue
                return False
            return self._length == other._length

    def __ne__(self, other):
        if self is other:
            return False
        if not isinstance(other, linked_list):
            return True
        locks = self._two_locks(other)
        with locks[0], locks[1]:
            for self_node, other_node in zip(self._internal_iter(), other._internal_iter()):
                if self_node.value != other_node.value:
                    return True
            return self._length != other._length

    def __lt__(self, other):
        if self is other:
            return False
        if not isinstance(other, linked_list):
            return NotImplemented
        locks = self._two_locks(other)
        with locks[0], locks[1]:
            for self_node, other_node in zip(self._internal_iter(), other._internal_iter()):
                if self_node.value < other_node.value:
                    return True
                if self_node.value == other_node.value:
                    continue
                # self_node > other_node
                return False
            return self._length < other._length

    def __le__(self, other):
        if self is other:
            return True
        if not isinstance(other, linked_list):
            return NotImplemented
        locks = self._two_locks(other)
        with locks[0], locks[1]:
            for self_node, other_node in zip(self._internal_iter(), other._internal_iter()):
                if self_node.value <= other_node.value:
                    if self_node.value == other_node.value:
                        continue
                    return True
                # self_node > other_node
                return False
            return self._length <= other._length

    def __ge__(self, other):
        if self is other:
            return True
        if not isinstance(other, linked_list):
            return NotImplemented
        locks = self._two_locks(other)
        with locks[0], locks[1]:
            for self_node, other_node in zip(self._internal_iter(), other._internal_iter()):
                if self_node.value >= other_node.value:
                    if self_node.value == other_node.value:
                        continue
                    return True
                # self_node < other_node
                return False
            return self._length >= other._length

    def __gt__(self, other):
        if self is other:
            return False
        if not isinstance(other, linked_list):
            return NotImplemented
        locks = self._two_locks(other)
        with locks[0], locks[1]:
            for self_node, other_node in zip(self._internal_iter(), other._internal_iter()):
                if self_node.value > other_node.value:
                    return True
                if self_node.value == other_node.value:
                    continue
                # self_node < other_node
                return False
            return self._length > other._length


    def __copy__(self):
        with self._lock or _inert_context_manager:
            return linked_list((node.value for node in self._internal_iter()), lock=self._lock_parameter)

    def copy(self, *, lock=None):
        with self._lock or _inert_context_manager:
            t = linked_list((node.value for node in self._internal_iter()), lock=False)
            t._lock_parameter = lock
            t._lock = t._analyze_lock(lock, self)
        return t

    def __deepcopy__(self, memo):
        t = linked_list(lock=self._lock_parameter)
        append = t.append
        with self._lock or _inert_context_manager:
            for node in self._internal_iter():
                append(copy.deepcopy(node.value, memo))
        return t

    def __getstate__(self):
        with self._lock or _inert_context_manager:
            if self._lock_parameter not in (False, True, None):
                raise ValueError("can't pickle linked_list with a user-supplied lock")
            return (None, {
                '_head': self._head,
                '_tail': self._tail,
                '_lock': self._lock_parameter,
                '_length': self._length,
                })

    def __setstate__(self, state):
        d = state[1]
        self._head = d['_head']
        self._tail = d['_tail']
        self._length = d['_length']
        self._lock_parameter = lock_parameter = d['_lock']
        self._lock = self._analyze_lock(lock_parameter, None)

    # new in 3.7
    if _python_3_7_plus:
        def __class_getitem__(cls, item):
            return GenericAlias(cls, (item,))

    def __add__(self, other):
        with self._lock or _inert_context_manager:
            t = linked_list((node.value for node in self._internal_iter()), lock=False)
            lock_parameter = self._lock_parameter

        if isinstance(other, linked_list):
            with other._lock or _inert_context_manager:
                t.extend((node.value for node in other._internal_iter()))
        else:
            t.extend(other)

        t._lock_parameter = lock_parameter
        t._lock = t._analyze_lock(lock_parameter, None)
        return t

    def __iadd__(self, other):
        self.extend(other)
        return self

    def __mul__(self, other):
        if not hasattr(other, '__index__'):
            raise TypeError(f"can't multiply sequence by non-int of type {type(other)!r}")
        multiplicand = other.__index__()
        t = linked_list(lock=False)
        with self._lock or _inert_context_manager:
            if multiplicand > 0:
                for _ in range(multiplicand):
                    t.extend((node.value for node in self._internal_iter()))
            lock_parameter = self._lock_parameter

        t._lock_parameter = lock_parameter
        t._lock = t._analyze_lock(lock_parameter, None)
        return t

    __rmul__ = __mul__

    def __imul__(self, other):
        if not hasattr(other, '__index__'):
            raise TypeError(f"can't multiply sequence by non-int of type {type(other)!r}")
        multiplicand = other.__index__()
        with self._lock or _inert_context_manager:
            if multiplicand <= 0:
                self._clear()
            else:
                elements = list((node.value for node in self._internal_iter()))
                for _ in range(multiplicand - 1):
                    self.extend(elements)
        return self

    def __iter__(self):
        # no locking needed! self._head and self._lock never change.
        return _secret_iterator_fun_factory(linked_list_iterator, self._head)

    head = __iter__

    def tail(self):
        # no locking needed! self._tail and self._lock never change.
        return _secret_iterator_fun_factory(linked_list_iterator, self._tail)

    def __reversed__(self):
        # no locking needed! self._tail and self._lock never change.
        return _secret_iterator_fun_factory(linked_list_reverse_iterator, self._tail)

    def __bool__(self):
        if self._lock is None:
            return self._length > 0
        with self._lock:
            return self._length > 0

    def __len__(self):
        if self._lock is None:
            return self._length
        with self._lock:
            return self._length

    def __contains__(self, value):
        return self.find(value) is not None

    def _cursor_at_list_index(self, index, clamp=False):
        """
        Returns a cursor at the node requested.

        If the list contains the five values a b c d and e,
        here's how the indexing works:
            head  a  b  c  d  e  tail
                  0  1  2  3  4  5
              -6 -5 -4 -3 -2 -1

        This is to accommodate slicing semantics copied from list.
        """
        if not hasattr(index, '__index__'):
            raise TypeError("linked_list indices must be integers or slices")
        index = index.__index__()

        length = self._length
        if index < 0:
            index += length

        # allow -1 and length
        if not (-1 <= index <= length):
            if not clamp:
                raise UndefinedIndexError(f"linked_list index out of range")
            if index < -1:
                index = -1
            else:
                index = length

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
            if not hasattr(step, '__index__'):
                raise TypeError('slice indices must be integers or None or have an __index__ method')
            step = step.__index__()
            if step == 0:
                raise ValueError("slice step cannot be zero")
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
        else:
            if not hasattr(start, '__index__'):
                raise TypeError('slice indices must be integers or None or have an __index__ method')
            start = start.__index__()
            if start < 0:
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
        else:
            if not hasattr(stop, '__index__'):
                raise TypeError('slice indices must be integers or None or have an __index__ method')
            stop = stop.__index__()
            if stop < 0:
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
        it should be in the range 0 <= start < length,
        but sometimes it might return -1 or length,
        because we're duplicating slicing rules on lists
        and the list object has really tiresome slicing
        semantics (see complaints about clamping).

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
            for new_value in extra_values:
                node.append(new_value)
                node = next(node)
        In the circumstance where it never yields any values,
        node will be pointing at the correct place to start
        appending.

        if key is not a slice, it, stop, step, and slice_length
        will all be None.  node will point at the node.
        "if stop is None" is a solid way of discriminating
        between "we parsed a slice" and "we got an index".

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
            # it should be impossible to get a None here.
            # we only get None for an iterator if start/stop is out of range,
            # and we already clamped 'em.
            assert it is not None
            # test start stop step, does it yield anything?
            for _ in range(start, stop, step):
                calculate_node = False
                break
            else:
                calculate_node = True
            if calculate_node:
                node = self._cursor_at_list_index(stop)
            else:
                node = None
        else:
            start = key
            stop = step = slice_length = None
            it = None
            node = self._cursor_at_list_index(start)

        return it, node, start, stop, step, slice_length

    def _getitem(self, key):
        it, node, start, stop, step, slice_length = self._parse_key(key)

        if stop is None: # then key is not a slice
            if node.special:
                raise UndefinedIndexError()
            return node.value

        return self.__class__(o.value for o in it)

    def __getitem__(self, key):
        if not self._lock:
            return self._getitem(key)
        with self._lock:
            return self._getitem(key)

    def _setitem(self, key, value):
        it, node, start, stop, step, slice_length = self._parse_key(key, for_assignment=True)

        if stop is None: # then key is not a slice
            if node.special:
                raise UndefinedIndexError()
            node.value = value
            return

        if value is self:
            raise ValueError("can't assign self to slice of self")

        # print(f"{it=} {node=} {start=} {stop=} {step=} {slice_length=}")

        if step == 1:
            sentinel = object()
            previous_node = node
            advance_previous = False
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
                        next_node = previous_node
                        if advance_previous:
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
                previous_node = node
                advance_previous = True

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

    def __setitem__(self, key, value):
        if not self._lock:
            return self._setitem(key, value)
        with self._lock:
            return self._setitem(key, value)


    def _delitem(self, key):
        it, node, start, stop, step, slice_length = self._parse_key(key)

        if stop is None: # then key is not a slice
            if node.special:
                raise UndefinedIndexError()
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

    def __delitem__(self, key):
        if not self._lock:
            return self._delitem(key)
        with self._lock:
            return self._delitem(key)

    def _insert(self, index, object):
        cursor = self._cursor_at_list_index(index, clamp=True)
        if cursor.special == 'head':
            cursor = cursor.next
        cursor.insert_before(object)

    def insert(self, index, object):
        if not self._lock:
            return self._insert(index, object)
        with self._lock:
            return self._insert(index, object)


    def append(self, object):
        if not self._lock:
            self._tail.insert_before(object)
            return
        with self._lock:
            self._tail.insert_before(object)

    def prepend(self, object):
        if not self._lock:
            self._head.next.insert_before(object)
            return
        with self._lock:
            self._head.next.insert_before(object)

    # some aliases for you
    rappend = prepend

    def _extend(self, iterable):
        insert_before = self._tail.insert_before
        for value in iterable:
            insert_before(value)

    def extend(self, iterable):
        if iterable is self:
            raise ValueError("can't extend self with self")
        if not self._lock:
            return self._extend(iterable)
        with self._lock:
            return self._extend(iterable)

    def _rextend(self, iterable):
        insert_before = self._head.next.insert_before
        for value in iterable:
            insert_before(value)

    def rextend(self, iterable):
        if iterable is self:
            raise ValueError("can't rextend self with self")
        if not self._lock:
            return self._rextend(iterable)
        with self._lock:
            return self._rextend(iterable)

    def _clear(self):
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

    def clear(self):
        if not self._lock:
            return self._clear()
        with self._lock:
            return self._clear()

    def _pop(self, index):
        if not self._length:
            raise ValueError('pop from empty linked_list')
        if index == -1:
            # speical case
            node = self._tail.previous
            while node.special == 'special':
                node = node.previous
        else:
            node = self._cursor_at_list_index(index)
            if node.special:
                raise SpecialNodeError()

        return node.remove()

    def pop(self, index=-1):
        if not hasattr(index, '__index__'):
            raise TypeError("pop indices must be integers")
        index = index.__index__()
        if not self._lock:
            return self._pop(index)
        with self._lock:
            return self._pop(index)

    def _rpop(self, index):
        if not self._length:
            raise ValueError('rpop from empty linked_list')
        if index == 0:
            node = self._head.next
            while node.special == 'special':
                node = node.next
        else:
            node = self._cursor_at_list_index(index)
            if node.special:
                raise SpecialNodeError()

        return node.remove()

    def rpop(self, index=0):
        if not hasattr(index, '__index__'):
            raise TypeError("pop indices must be integers")
        index = index.__index__()
        if not self._lock:
            return self._rpop(index)
        with self._lock:
            return self._rpop(index)

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
        with self._lock or _inert_context_manager:
            it = self.head()
            value = it._remove(value, default)
            it._del()
            return value

    def rremove(self, value, default=_undefined):
        with self._lock or _inert_context_manager:
            it = self.tail()
            value = it._rremove(value, default)
            it._del()
            return value

    def reverse(self):
        with self._lock or _inert_context_manager:
            if self._length < 2:
                # reverse is a no-op for lists of length 0 or 1
                return self.__iter__()

            previous_r = None
            fit = self._internal_iter()
            rit = self._internal_reversed()

            while True:
                f = next(fit)
                r = next(rit)
                if ((f == r) # odd number of nodes
                    or (f == previous_r)): # even number of nodes (or no nodes)
                    break

                tmp = f.value
                f.value = r.value
                r.value = tmp

                previous_r = r

    def sort(self, key=None, reverse=False):
        # copy to list, sort, then write back in-place
        # if the list has special nodes, this might be very exciting!

        with self._lock or _inert_context_manager:
            values = list((node.value for node in self._internal_iter()))
            values.sort(key=key, reverse=reverse)

            for node, value in zip(self._internal_iter(), values):
                node.value = value


    def _cut(self, start, stop, lock, _lock, is_rcut):
        """
        _cut is our mega worker function.
        it implements both cut and rcut,
        for both forward and reverse iterators.
        (sadly this was the best approach, as there are
        so many little if statements sprinkled within.)

        if is_rcut is true, then start comes after stop.
        start and stop are still both inclusive.
        """

        try:
            start_is_none = start is None
            stop_is_none = stop is None

            # compute this now, before we potentially invert is_rcut
            verb = "rcut" if is_rcut else "cut"

            # {name}_directions is a bitfield indicating supported iterator directions:
            #   1 means "forward"
            #   2 means "reverse"
            #   3 means both "forward" and "reverse"

            if start_is_none:
                start_directions = 3
            else:
                if not isinstance(start, linked_list_base_iterator):
                    ex_type = TypeError
                elif not (
                    (start._internal_lock() is self._lock)
                    and (start._internal_linked_list() is self)
                    ):
                    ex_type = ValueError
                else:
                    ex_type = None
                if ex_type is not None:
                    if _lock:
                        _lock.release()
                        _lock = None
                    raise ex_type(f"start is not an iterator over this linked_list, start={start!r}")

                start_directions = 2 if isinstance(start, linked_list_reverse_iterator) else 1

            if stop_is_none:
                stop_directions = 3
            else:
                if not isinstance(stop, linked_list_base_iterator):
                    ex_type = TypeError
                elif not (
                    (stop._internal_lock() is self._lock)
                    and (stop._internal_linked_list() is self)
                    ):
                    ex_type = ValueError
                else:
                    ex_type = None
                if ex_type is not None:
                    if _lock:
                        _lock.release()
                        _lock = None
                    raise ex_type(f"stop is not an iterator over this linked_list, stop={stop!r}")
                stop_directions = 2 if isinstance(stop, linked_list_reverse_iterator) else 1

            if not (start_directions & stop_directions):
                if _lock:
                    _lock.release()
                    _lock = None
                raise ValueError("mismatched forward and reverse iterators for start and stop, start={start!r}, stop={stop!r}")

            if (start_directions == 2) or (stop_directions == 2):
                # if the user is cutting with reverse iterators,
                # negate is_rcut *here*
                is_rcut = not is_rcut

            t2 = linked_list(lock=False)

            start_iterator = start
            stop_iterator = stop

            if not is_rcut:
                # cut
                if start_is_none:
                    start = self._head.next
                else:
                    if start._cursor is self._head:
                        # only permissible if stop is also _head
                        if start is stop:
                            return t2
                        raise SpecialNodeError(f"can't {verb} head")
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
                        if start is stop:
                            return t2
                        raise SpecialNodeError(f"can't {verb} tail")
                    start = start._cursor

                # convert stop to a cursor, and make it inclusive
                if stop_is_none:
                    stop = self._head
                else:
                    stop = stop._cursor

                if start is stop:
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
            # since start can't be head, and stop can't be tail, we know
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

            t2._lock_parameter = lock
            t2._lock = t2._analyze_lock(lock, self)

            if not start_is_none:
                start_iterator._lock = t2._lock
            if not stop_is_none:
                stop_iterator._lock = t2._lock

            return t2
        finally:
            if _lock:
                _lock.release()


    def cut(self, start=None, stop=None, *, lock=None):
        """
        Cuts a range of nodes from start to stop.
        The range of nodes includes start but excludes
        stop.

        Returns a new linked_list containing the cut nodes.

        After the cut, the start and stop iterators
        will still point at the same nodes, however
        they will have been moved to the new list.

        If start is None, it defaults to the first node
        after head.  (If the list is empty, this will be tail.)
        If stop is None, it defaults to tail.

        If specified, start and stop must be iterators
        over the current linked list.  start must not
        be after stop.

        This function won't cut head; it's an error
        if start points to head.

        start and stop may be reverse iterators, however the
        linked list resulting from a cut will have the elements
        in forward order.  If either start or stop is a reverse
        iterator, then:

        * start defaults to the last node before tail,
        * stop defaults to head,
        * start must not be after stop, and
        * start must not point to tail.
        """
        _lock = self._lock
        if _lock:
            _lock.acquire()
        return self._cut(start, stop, lock, _lock, False)

    def rcut(self, start=None, stop=None, *, lock=None):
        _lock = self._lock
        if _lock:
            _lock.acquire()
        return self._cut(start, stop, lock, _lock, True)

    def _splice(self, other, where, is_rsplice):
        """
        moves nodes from other (a linked list) to after cursor (a node).
        """
        # print(f">> splice {self=} {other=} {where=} {is_rsplice=}")

        special = None

        if is_rsplice:
            if where is None:
                cursor = self._head
            else:
                self._splice_check_where(where)
                cursor = where._cursor
                if cursor is self._head:
                    special = cursor.next.insert_before(None, 'special')
                    cursor = special
                else:
                    cursor = cursor.previous
        else:
            if where is None:
                cursor = self._tail.previous
            else:
                self._splice_check_where(where)
                cursor = where._cursor
                if cursor is self._tail:
                    special = cursor.insert_before(None, 'special')
                    cursor = special

        assert cursor

        after = cursor.next
        assert after

        other_length = other._length
        assert other_length
        self._length += other_length

        other_first, other_last = other._internal_cut()
        assert other_first != None
        assert other_last != None

        cursor.next = other_first
        other_first.previous = cursor

        after.previous = other_last
        other_last.next = after

        while cursor != after:
            cursor.linked_list = self
            cursor = cursor.next

        if (where is not None) and (special is not None):
            where._cursor = special

    def _splice_check_other(self, other):
        if not isinstance(other, linked_list):
            raise TypeError('other must be a linked_list')
        if other is self:
            raise ValueError("other and self are the same")

    def _splice_check_where(self, where):
        if where is not None:
            if not isinstance(where, linked_list_base_iterator):
                raise TypeError('where must be a linked_list iterator over self')
            if not (
                (where._internal_lock() is self._lock)
                and (where._internal_linked_list() is self)
                ):
                raise ValueError("where must be a linked_list iterator over self")

    def splice(self, other, *, where=None):
        """
        Moves nodes from other into self, at where.

        other must be a linked_list.  If successful,
        other will be empty.  (The head and tail from
        other don't move, but all other nodes move,
        including special nodes.)

        where must be an iterator over self, or None.
        If where is an iterator, the nodes are inserted
        *after* the node pointed to by where.  If where
        is None, the nodes are appended to the list (as if
        you had called extend).
        """
        self._splice_check_other(other)

        if not other:
            return

        locks = self._two_locks(other)
        with locks[0], locks[1]:
            self._splice(other, where, False)

    def rsplice(self, other, *, where=None):
        self._splice_check_other(other)

        if not other:
            return

        locks = self._two_locks(other)
        with locks[0], locks[1]:
            self._splice(other, where, True)

    ##
    ## special list compatibility layer
    ##
    def _clamp_index(self, index, name):
        if not hasattr(index, '__index__'):
            raise TypeError(f'{name} must be an int, not {type(index).__name__}')
        index = index.__index__()

        length = self._length
        if index < 0:
            index += length
            if index <= 0:
                return 0
        elif index >= length:
            return length
        return index

    def index(self, value, start=0, stop=sys.maxsize):
        """
        Returns the first index of value.

        Raises ValueError if the value is not present.

        The value returned will be greater than or equal
        to start, and less than stop.
        """
        with self._lock or _inert_context_manager:
            clamp = self._clamp_index
            start = clamp(start, 'start')
            stop = clamp(stop, 'stop')
            if stop < start:
                raise ValueError("stop can't be less than start")

            def exp():
                return ValueError(f'{value!r} is not in linked_list')

            cursor = self._head.next
            tail = self._tail
            index = -1

            while cursor != tail:
                index += 1
                if index >= start:
                    if index >= stop:
                        raise exp()
                    if (not cursor.special) and (cursor.value == value):
                        return index
                cursor = cursor.next
            raise exp()


    ##
    ## special deque compatibility layer
    ##
    def extendleft(self, iterable):
        """
        Prepend the elements from the iterable to the linked_list, helpfully in reverse order.
        """
        if iterable is self:
            raise ValueError("can't extendleft self with self")
        self.rextend(reversed(iterable))

    def rotate(self, n):
        if not hasattr(n, '__index__'):
            raise TypeError(f'{type(n).__name__} object cannot be interpreted as integer')

        n = n.__index__()
        n_is_negative = (n < 0)
        n = abs(n) % self._length
        if (not n) or (self._length < 2):
            return

        with self._lock or _inert_context_manager:
            if n_is_negative:
                cursor = self._head
                for _ in range(n + 1):
                    cursor = cursor.next
            else:
                cursor = self._tail
                for _ in range(n):
                    cursor = cursor.previous

            segment_1_head = self._head.next
            segment_1_tail = cursor.previous

            segment_2_head = cursor
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

    appendleft = prepend
    maxlen = None
    popleft = rpop


_sentinel = object()

@export
class linked_list_base_iterator:
    __slots__ = ('_cursor', '_lock')

    def __init__(self, node):
        raise TypeError("cannot create linked_list_base_iterator instances")

    def __getstate__(self):
        return (None, {
            '_cursor': self._cursor,
            })

    def __setstate__(self, state):
        d = state[1]
        self._cursor = d['_cursor']
        self._lock = self._cursor.linked_list._lock

    def _internal_lock(self):
        """
        Internal API for use by linked_list
        and linked_list iterator objects.
        Returns a reference to the linked list's
        lock, or None if the linked list has no lock.
        """

        ## Note that in most cases the caller will often
        ## already hold the iterator's lock. Which means:
        ## this function *must* be unsynchronized!
        ##
        ## However, the function must also *not* return
        ## stale data.  Which means it must fetch the
        ## correct lock without benefit of synchronization.
        ##
        ## In practice this should be fine.  _internal_lock
        ## is only used as part of a two-step process to confirm
        ## that an iterator is valid for an operation.  If you
        ## perform an operation on list J using iterator K,
        ## we first confirm that K and J have the same lock;
        ## if they don't, K can't be an iterator over J.
        ##
        ## * If K is an iterator over J, then the code calling
        ##   K._internal_lock already holds the lock, and so
        ##   this is safe.
        ## * If K is *not* an iterator over J, but J and K
        ##   have the same lock anyway, again the code already
        ##   holds the lock and this is safe.
        ## * If K is not an iterator over J, and K and J
        ##   have *different* locks, then we fetched the lock
        ##   in an unsychronized way, but "self._cursor" and
        ##   "self._cursor.linked_list" and
        ##   "self._cursor.linked_list._lock" should always
        ##   be defined, and then the operation on K will
        ##   discover the locks don't match and give up.
        self._lock = lock = self._cursor.linked_list._lock
        return lock

    def _internal_linked_list(self):
        """
        Internal API for use by linked_list
        and linked_list iterator objects.
        Returns a reference to the linked list
        being iterated over.
        """
        return self._cursor.linked_list

    @property
    def linked_list(self):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            return self._cursor.linked_list
        finally:
            if _lock:
                _lock.release()

    # new in 3.7
    def __class_getitem__(cls, item): # pragma nocover
        return GenericAlias(cls, (item,))

    def _repr(self):
        return f"<{self.__class__.__name__} {hex(id(self))} cursor={self._cursor!r}>"

    def __repr__(self):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            return self._repr()
        finally:
            if _lock:
                _lock.release()


    def _del(self):
        cursor = getattr(self, '_cursor', None)
        if cursor is None:
            return
        setattr(self, '_cursor', None)
        setattr(self, '_lock', None)
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

    def __del__(self):
        # drop our reference to the current node.
        # that means decrementing node.iterator_refcount.
        # and if node.iterator_refcount reaches 0,
        # we *gotta* call unlink.
        lock = None
        try:
            while True:
                lock = getattr(self, '_lock', None)
                if lock:
                    lock.acquire()
                    if lock is not getattr(self, '_lock', None): lock.release() ; continue
                break
            self._del()
        finally:
            if lock:
                lock.release()

    def __bool__(self):
        "Returns True if this iterator isn't currently exhausted."

        # If this iterator points at the next-to-last node,
        # bool still returns True.
        #
        # An alternate proposed API for bool: return True if you can currently
        # call next() on the iterator without it raising StopIteration.
        #
        # But consider this code:
        #       t = linked_list([1, 2, 3, 4, 5])
        #       it = t.find(5)
        #       if it:
        #          ...
        #
        # With the current semantics, it is true, so we enter the if block.
        # If we returned False if next(it) would raise, here it would be false,
        # so we wouldn't go inside the if block.
        #
        # It's more useful if it is true in the above scenario.  So, the current
        # semantics stay.
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            cursor = self._cursor
            tail = cursor.linked_list._tail
            while True:
                if cursor is tail:
                    return False
                if cursor.special is None:
                    return True
                cursor = cursor.next
        finally:
            if _lock:
                _lock.release()



    def __eq__(self, other):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            return (
                (self.__class__ == other.__class__)
                and (self._cursor == other._cursor)
                )
        finally:
            if _lock:
                _lock.release()

    def __iter__(self):
        return self

    def __contains__(self, value):
        return self.find(value) is not None

    def __copy__(self):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            return _secret_iterator_fun_factory(self.__class__, self._cursor)
        finally:
            if _lock:
                _lock.release()

    def copy(self):
        return self.__copy__()

    def __len__(self):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            length = 0
            cursor = self._cursor
            while cursor is not None:
                if not cursor.special:
                    length += 1
                cursor = cursor.next
            return length
        finally:
            if _lock:
                _lock.release()

    def _next(self):
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

    def __next__(self):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            return self._next()
        finally:
            if _lock:
                _lock.release()

    def next(self, default=_undefined, *, count=1):
        if not hasattr(count, '__index__'):
            raise TypeError(f'count must be an int, not {type(count).__name__}')
        count = count.__index__()
        if count < 0:
            raise ValueError("count can't be negative")
        if count == 0:
            return None

        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            next = self._next

            if default == _undefined:
                while count > 1:
                    next()
                    count -= 1
                return next()

            try:
                while count > 1:
                    next()
                    count -= 1
                return next()
            except StopIteration:
                return default

        finally:
            if _lock:
                _lock.release()

    def _previous(self):
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
        if not hasattr(count, '__index__'):
            raise TypeError(f'count must be an int, not {type(count).__name__}')
        count = count.__index__()
        if count < 0:
            raise ValueError("count can't be negative")
        if count == 0:
            return None

        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            previous = self._previous
            if default == _undefined:
                while count > 1:
                    previous()
                    count -= 1
                return previous()
            try:
                while count > 1:
                    previous()
                    count -= 1
                return previous()
            except StopIteration:
                return default
        finally:
            if _lock:
                _lock.release()

    def before(self, count=1):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            if not hasattr(count, '__index__'):
                raise TypeError(f'count must be an int, not {type(count).__name__}')
            count = count.__index__()
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
            return _secret_iterator_fun_factory(self.__class__, cursor)
        finally:
            if _lock:
                _lock.release()

    def after(self, count=1):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            if not hasattr(count, '__index__'):
                raise TypeError(f'count must be an int, not {type(count).__name__}')
            count = count.__index__()
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
            return _secret_iterator_fun_factory(self.__class__, cursor)
        finally:
            if _lock:
                _lock.release()

    def reset(self):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            self._cursor = self._cursor.linked_list._head
        finally:
            if _lock:
                _lock.release()

    def exhaust(self):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            self._cursor = self._cursor.linked_list._tail
        finally:
            if _lock:
                _lock.release()

    @property
    def special(self):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            return self._cursor.special
        finally:
            if _lock:
                _lock.release()

    @property
    def is_special(self):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            return self._cursor.special is not None
        finally:
            if _lock:
                _lock.release()

    def _cursor_at_iterator_index(self, key, allow_head_and_tail=False):
        """
        Only returns a valid data node, head, or tail.
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
                if not allow_head_and_tail:
                    raise UndefinedIndexError()
        else:
            c2 = cursor.index(key)
            if (c2 is None) or (c2.special and not allow_head_and_tail):
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
                raise TypeError("slice indices must be integers or None or have an __index__ method")
            else:
                append(value.__index__())
        if not result[2]:
            raise ValueError("slice step cannot be zero")
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
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break

            if isinstance(key, slice):
                it = self._slice_iterator(key)
                cls = type(self._cursor.linked_list)
                return cls(node.value for node in it)
            cursor = self._cursor_at_iterator_index(key)
            return cursor.value
        finally:
            if _lock:
                _lock.release()

    def __setitem__(self, key, value):
        if value is self.linked_list:
            raise ValueError("can't assign self to slice of self")

        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break

            if not isinstance(key, slice):
                cursor = self._cursor_at_iterator_index(key)
                cursor.value = value
                return

            start, stop, step = self._unpack_slice(key)
            it = self._slice_iterator(key)
            nodes_list = list(it)
            nodes_list_length = len(nodes_list)

            values_list = list(value)
            values_list_length = len(values_list)

            delete_me = insert_me = None

            is_reverse = isinstance(self, linked_list_reverse_iterator)
            if is_reverse:
                value = reversed(value)

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
                    last_node = self._cursor_at_iterator_index(stop, allow_head_and_tail=True)
                if last_node.special in ('head', 'tail'):
                    raise UndefinedIndexError()
                if is_reverse:
                    # last_node is actually the earliest node in the list!
                    while insert_me:
                        last_node.insert_before(insert_me.pop())
                else:
                    node = last_node.next
                    for v in insert_me:
                        node.insert_before(v)
        finally:
            if _lock:
                _lock.release()

    def __delitem__(self, key):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            if not isinstance(key, slice):
                cursor = self._cursor_at_iterator_index(key)
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
        finally:
            if _lock:
                _lock.release()

    def insert(self, index, object):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            cursor = self._cursor_at_iterator_index(index, allow_head_and_tail=True)
            if cursor.special == 'head':
                raise UndefinedIndexError()
            cursor.insert_before(object)
        finally:
            if _lock:
                _lock.release()

    def count(self, value):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            cursor = self._cursor
            tail = cursor.linked_list._tail
            counter = 0
            while cursor != tail:
                if (cursor.special is None) and (cursor.value == value):
                    counter += 1
                cursor = cursor.next
            return counter
        finally:
            if _lock:
                _lock.release()

    def rcount(self, value):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            cursor = self._cursor
            head = cursor.linked_list._head
            counter = 0
            while cursor != head:
                if (cursor.special is None) and (cursor.value == value):
                    counter += 1
                cursor = cursor.previous
            return counter
        finally:
            if _lock:
                _lock.release()

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

    def pop(self, index=0):
        if not hasattr(index, '__index__'):
            raise TypeError(f'index must be an int, not {type(index).__name__}')
        index = index.__index__()
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            if index != 0:
                cursor = self._cursor_at_iterator_index(index)
                value = cursor.value
                cursor.remove()
                return value
            # cursor is where we'll retreat to after we pop
            cursor = self._cursor
            if cursor.special == 'head':
                raise UndefinedIndexError()
            cursor = cursor.previous
            while cursor.special == 'special':
                cursor = cursor.previous
            return self._pop(cursor)
        finally:
            if _lock:
                _lock.release()

    def rpop(self, index=0):
        """
        The difference between pop and rpop is the direction the
        iterator moves after popping.  pop retreats to the previous
        node, rpop advances to the next node.
        """
        if not hasattr(index, '__index__'):
            raise TypeError(f'index must be an int, not {type(index).__name__}')
        index = index.__index__()
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            if index != 0:
                cursor = self._cursor_at_iterator_index(index)
                value = cursor.value
                cursor.remove()
                return value
            # cursor is where we'll advance to after we pop
            cursor = self._cursor
            if cursor.special == 'tail':
                raise UndefinedIndexError()
            cursor = cursor.next
            while cursor.special == 'special':
                cursor = cursor.next
            return self._pop(cursor)
        finally:
            if _lock:
                _lock.release()

    def _remove(self, value, default):
        cursor = self._find(value)
        if cursor is not None:
            value = cursor.value
            cursor.remove()
            return value
        if default is not _undefined:
            return default
        raise ValueError(f'value {value!r} not found')

    def remove(self, value, default=_undefined):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            return self._remove(value, default)
        finally:
            if _lock:
                _lock.release()

    def _rremove(self, value, default):
        cursor = self._rfind(value)
        if cursor is not None:
            value = cursor.value
            cursor.remove()
            return value
        if default is not _undefined:
            return default
        raise ValueError(f'value {value!r} not found')

    def rremove(self, value, default=_undefined):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            return self._rremove(value, default)
        finally:
            if _lock:
                _lock.release()

    def append(self, value):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            # -- handle self pointing at tail, or not --
            cursor = self._cursor
            if cursor.special == 'tail':
                raise UndefinedIndexError("can't append to tail")
            cursor = cursor.next
            # -- actually append value --
            cursor.insert_before(value)
        finally:
            if _lock:
                _lock.release()

    def prepend(self, value):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            # -- handle self pointing at head, or not --
            cursor = self._cursor
            if cursor.special == 'head':
                raise UndefinedIndexError("can't insert before head")
            # -- actually append value --
            cursor.insert_before(value)
        finally:
            if _lock:
                _lock.release()

    rappend = prepend

    def _extend(self, other, iterable, verb):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            cursor = self._cursor
            if other is cursor.linked_list:
                raise ValueError(f"can't {verb} self with self")
            # -- handle self pointing at tail, or not --
            if cursor.special == 'tail':
                raise UndefinedIndexError(f"can't {verb} tail")
            cursor = cursor.next
            # -- actually extend from iterator --
            insert_before = cursor.insert_before
            for value in iterable:
                insert_before(value)
        finally:
            if _lock:
                _lock.release()

    def extend(self, iterable):
        return self._extend(iterable, iterable, "extend")

    def _rextend(self, other, iterable, verb):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            cursor = self._cursor
            if other is cursor.linked_list:
                raise ValueError(f"can't {verb} self with self")
            # handle self pointing at head, or not --
            if cursor.special == 'head':
                raise UndefinedIndexError(f"can't {verb} head")
            # -- actually extend from iterator --
            insert_before = cursor.insert_before
            for value in iterable:
                insert_before(value)
        finally:
            if _lock:
                _lock.release()

    def rextend(self, iterable):
        return self._rextend(iterable, iterable, "rextend")

    def _find(self, value):
        cursor = self._cursor

        while True:
            special = cursor.special
            if (not special) and (cursor.value == value):
                return cursor
            if special == 'tail':
                return None
            cursor = cursor.next

    def find(self, value):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            cursor = self._find(value)
            if not cursor:
                return None
            return _secret_iterator_fun_factory(self.__class__, cursor)
        finally:
            if _lock:
                _lock.release()

    def _rfind(self, value):
        cursor = self._cursor

        while True:
            special = cursor.special
            if (not special) and (cursor.value == value):
                return cursor
            if special == 'head':
                return None
            cursor = cursor.previous


    def rfind(self, value):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            cursor = self._rfind(value)
            if cursor is None:
                return None
            return _secret_iterator_fun_factory(self.__class__, cursor)
        finally:
            if _lock:
                _lock.release()

    def match(self, predicate):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            cursor = self._cursor

            while True:
                special = cursor.special
                if (not special) and predicate(cursor.value):
                    break
                if special == 'tail':
                    return None
                cursor = cursor.next

            return _secret_iterator_fun_factory(self.__class__, cursor)
        finally:
            if _lock:
                _lock.release()

    def rmatch(self, predicate):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            cursor = self._cursor

            while True:
                special = cursor.special
                if (not special) and predicate(cursor.value):
                    break
                if special == 'head':
                    return None
                cursor = cursor.previous

            return _secret_iterator_fun_factory(self.__class__, cursor)
        finally:
            if _lock:
                _lock.release()

    def truncate(self):
        """
        Truncates the linked_list at the current node,
        discarding the current node and all subsequent nodes.

        After this operation, the iterator will point to the linked list's tail.
        """
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break

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

        finally:
            if _lock:
                _lock.release()

    def rtruncate(self):
        """
        Truncates the linked_list at the current node,
        discarding the current node and all previous nodes.

        After this operation, the iterator will point to the linked list's head.
        """
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
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

        finally:
            if _lock:
                _lock.release()

    def cut(self, stop=None, *, lock=None):
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
        while True:
            _lock = self._lock
            if _lock:
                _lock.acquire()
                if _lock is not self._lock: _lock.release() ; continue
            break
        return self._cursor.linked_list._cut(self, stop, lock, _lock, False)


    def rcut(self, stop=None, *, lock=None):
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
        while True:
            _lock = self._lock
            if _lock:
                _lock.acquire()
                if _lock is not self._lock: _lock.release() ; continue
            break
        return self._cursor.linked_list._cut(self, stop, lock, _lock, True)


    def _splice(self, other, is_rsplice):
        if not isinstance(other, linked_list):
            raise TypeError('other must be a linked_list')

        locks = []
        append = locks.append
        def clear_locks(locks):
            while locks:
                locks.pop().release()

        try:
            other_lock = other._lock

            while True:
                self_lock = self._lock

                if self_lock is None:
                    if other_lock is None:
                        break
                    other_lock.acquire()
                    append(other_lock)
                    break

                if (other_lock is self_lock) or (other_lock is None):
                    self_lock.acquire()
                    append(self_lock)
                    if self_lock is not self._lock: clear_locks(locks) ; continue
                    break

                lock_other_first = id(other_lock) < id(self_lock)
                if lock_other_first:
                    other_lock.acquire()
                    append(other_lock)

                self_lock.acquire()
                append(self_lock)
                if self_lock is not self._lock: clear_locks(locks) ; continue

                if not lock_other_first:
                    other_lock.acquire()
                    append(other_lock)
                break

            list = self._cursor.linked_list
            if other is list:
                raise ValueError("other and self are the same list")
            if not other._length:
                return
            return list._splice(other, self, is_rsplice)

        finally:
            clear_locks(locks)

    def splice(self, other):
        return self._splice(other, False)

    def rsplice(self, other):
        return self._splice(other, True)


# not for you! don't touch!
class _secret_iterator_fun_factory(linked_list_base_iterator):
    def __init__(self, cls, node):
        node.iterator_refcount += 1
        self._cursor = node
        self._lock = lock = node.linked_list._lock

        self.__class__ = cls


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

    def __init__(self):
        raise TypeError("cannot create linked_list_iterator instances")

    def __reversed__(self):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            return _secret_iterator_fun_factory(linked_list_reverse_iterator, self._cursor)

        finally:
            if _lock:
                _lock.release()


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

    def __init__(self):
        raise TypeError("cannot create linked_list_reverse_iterator instances")

    def __reversed__(self):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            return _secret_iterator_fun_factory(linked_list_iterator, self._cursor)
        finally:
            if _lock:
                _lock.release()

    _next     = linked_list_base_iterator._previous
    _previous = linked_list_base_iterator._next

    @staticmethod
    def _reverse_index(index):
        if not isinstance(index, slice):
            if not hasattr(index, '__index__'):
                raise TypeError("linked_list indices must be integers or slices")
            return -(index.__index__())

        result = []
        append = result.append
        for value, default in (
            (index.start, 0),
            (index.stop, 0),
            (index.step, -1),
            ):
            if value is None:
                append(default)
            elif not hasattr(value, '__index__'):
                raise TypeError(f"slice indices must be integers or None or have an __index__ method")
            else:
                append(-(value.__index__()))
        if not result[2]:
            raise ValueError("slice step cannot be zero")
        return slice(result[0], result[1], result[2])

    def __getitem__(self, index):
        return super().__getitem__(self._reverse_index(index))

    def __setitem__(self, index, value):
        # if this is a slice, we need to reverse
        # but, sadly, we do that in __setitem__.
        return super().__setitem__(self._reverse_index(index), value)

    def __delitem__(self, index):
        return super().__delitem__(self._reverse_index(index))

    def reset(self):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            self._cursor = self._cursor.linked_list._tail
        finally:
            if _lock:
                _lock.release()

    def exhaust(self):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            self._cursor = self._cursor.linked_list._head
        finally:
            if _lock:
                _lock.release()

    def before(self, count=1):
        return super().after(count)

    def after(self, count=1):
        return super().before(count)

    def __bool__(self):
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            cursor = self._cursor
            head = cursor.linked_list._head
            while True:
                if cursor is head:
                    return False
                if cursor.special is None:
                    return True
                cursor = cursor.previous
        finally:
            if _lock:
                _lock.release()

    def count(self, value):
        return super().rcount(value)

    def rcount(self, value):
        return super().count(value)

    def prepend(self, value):
        super().append(value)

    def append(self, value):
        super().prepend(value)

    def extend(self, iterable):
        return super()._rextend(iterable, reversed(iterable), "extend")

    def rextend(self, iterable):
        return super()._extend(iterable, reversed(iterable), "rextend")

    def pop(self, index=0):
        return super().rpop(-index)

    def rpop(self, index=0):
        return super().pop(-index)

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
        try:
            while True:
                _lock = self._lock
                if _lock:
                    _lock.acquire()
                    if _lock is not self._lock: _lock.release() ; continue
                break
            length = 0
            cursor = self._cursor
            while cursor is not None:
                if not cursor.special:
                    length += 1
                cursor = cursor.previous
            return length
        finally:
            if _lock:
                _lock.release()


clean()
