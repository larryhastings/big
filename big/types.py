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
import copy
from itertools import zip_longest
import re

from .text import linebreaks, multipartition, multisplit, Pattern
from .tokens import generate_tokens


__all__ = []
def export(o):
    __all__.append(o.__name__)
    return o


##
## String conforms to Python's rules about where to split a line.
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
## includes '\r\n'.  So we sort linebreaks by length, longest
## first, and build the regular expression out of that.
##

_re_linebreaks = "|".join(sorted(linebreaks, key=lambda s: -len(s)))
_re_linebreaks_finditer = re.compile(_re_linebreaks).finditer


@export
class String(str):
    "String(str, *, source=None, origin=None, offset=0, line_number=1, column_number=1, first_line_number=1, first_column_number=1, tab_width=8) -> String\nCreates a new String object.  String is a subclass of str that maintains line, column, and offset information."

    __slots__ = ('_source', '_origin', '_offset', '_line_number', '_column_number', '_first_line_number', '_first_column_number', '_tab_width', '_linebreak_offsets', '_line')

    def __new__(cls, s, *, source=None, origin=None, offset=0, line_number=1, column_number=1, first_line_number=1, first_column_number=1, tab_width=8):
        if isinstance(s, String):
            return s
        if not isinstance(s, str):
            raise TypeError("String: s must be a str or String object")

        if not ((origin is None) or isinstance(origin, String)):
            raise TypeError(f"String: origin must be String or None, not {type(origin)}")

        if isinstance(source, str):
            if isinstance(source, String):
                source = str(source)
        elif source == None:
            if origin is not None:
                source = origin.source
        else:
            raise TypeError(f"String: source must be str or None, not {type(source)}")

        ex = None

        if not isinstance(offset, int):
            ex = TypeError
        elif offset < 0:
            ex = ValueError
        if ex:
            raise ex(f"String: offset must be an int >= 0, not {offset}")

        if not isinstance(first_line_number, int):
            ex = TypeError
        elif first_line_number < 0:
            ex = ValueError
        if ex:
            raise ex("String: first_line_number must be an int >= 0")

        if not isinstance(first_column_number, int):
            ex = TypeError
        elif first_column_number < 0:
            ex = ValueError
        if ex:
            raise ex("String: first_column_number must be an int >= 0")

        # secret API: if you pass in None for line_number and column_number,
        # it's lazy-calculated
        if not (line_number == column_number == None):
            if not isinstance(line_number, int):
                ex = TypeError
            elif line_number < 0:
                ex = ValueError
            if ex:
                raise ex("String: line_number must be an int >= 0")

            if not isinstance(column_number, int):
                ex = TypeError
            elif column_number < 0:
                ex = ValueError
            if ex:
                raise ex(f"String: column_number must be an int >= 0, not {column_number}")

            if line_number < first_line_number:
                raise ValueError("String: line_number can't be less than first_line_number")

            if column_number < first_column_number:
                raise ValueError("String: column_number can't be less than first_column_number")

        if not isinstance(tab_width, int):
            ex = TypeError
        elif tab_width < 1:
            ex = ValueError
        if ex:
            raise ex("String: tab_width must be an int >= 1")

        self = super().__new__(cls, s)
        self._source = source
        if origin is None:
            self._origin = self
        else:
            self._origin = origin
        self._offset = offset
        self._line_number = line_number
        self._column_number = column_number
        self._first_line_number = first_line_number
        self._first_column_number = first_column_number
        self._tab_width = tab_width
        self._linebreak_offsets = self._line = None

        return self

    # OK?
    # comparisons behave like str for the purposes of comparison
    # if l is a String, l == str(l), l < str(l) + 'x', l + 'x' > str(l), etc

    @property
    def source(self):
        return self._source

    @property
    def origin(self):
        return self._origin

    def _compute_linebreak_offsets(self):
        #     self._linebreak_offsets[line_number_offset]
        # is the offset of the first character of the line after
        #     self.line_number + line_number_offset
        #
        # e.g. "abcde\nfghij"
        # self._linebreak_offsets = (6,)
        #
        # assuming first_line_number is 1:
        # line 1 always starts at offset 0, we don't write it down
        # line 2 starts at self._linebreak_offsets[0]
        self._linebreak_offsets = offsets = tuple(match.end() for match in _re_linebreaks_finditer(str(self)))
        if 0:
            print()
            print(repr(str(self)))
            print(list(_re_linebreaks_finditer(str(self))))
            print(offsets)
            print()
        return offsets

    def _calculate_line_and_column_numbers(self):
        assert self._line_number == self._column_number == None
        origin = self._origin

        linebreak_offsets = origin._linebreak_offsets or origin._compute_linebreak_offsets()

        linebreak_index = bisect_right(linebreak_offsets, self._offset)
        self._line_number = self._first_line_number + linebreak_index

        # either 0 or the offset of the previous line
        line_start_offset = linebreak_index and linebreak_offsets[linebreak_index - 1]

        column_number = first_column_number = self._first_column_number
        tab_width = self._tab_width

        s = str(origin)

        for offset in range(line_start_offset, self._offset):
            c = s[offset]
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
        self._column_number = column_number

    @property
    def line_number(self):
        if self._line_number is None:
            self._calculate_line_and_column_numbers()
        return self._line_number

    @property
    def column_number(self):
        if self._column_number is None:
            self._calculate_line_and_column_numbers()
        return self._column_number

    @property
    def offset(self):
        return self._offset

    @property
    def first_line_number(self):
        return self._first_line_number

    @property
    def first_column_number(self):
        return self._first_column_number

    @property
    def tab_width(self):
        return self._tab_width

    @property
    def where(self):
        if self._line_number is None:
            self._calculate_line_and_column_numbers()
        if self._source:
            return f'"{self._source}" line {self._line_number} column {self._column_number}'
        return f'line {self._line_number} column {self._column_number}'


    def is_followed_by(self, other):
        if not isinstance(other, String):
            return False

        if self.origin != other.origin:
            return False

        return self._offset + len(self) == other._offset

    def __add__(self, other):
        if not isinstance(other, str):
            raise TypeError(f'can only concatenate str (not "{type(other)}") to String')
        if not other:
            return self

        s = str(self) + str(other)

        if self.is_followed_by(other):
            origin = self.origin
            offset = self._offset
        else:
            origin = None
            offset = 0

        result = self.__class__(s,
            source = self._source,
            origin = origin,
            offset = offset,
            line_number = self._line_number,
            column_number = self._column_number,
            first_line_number = self._first_line_number,
            first_column_number = self._first_column_number,
            tab_width = self._tab_width,
            )
        if origin is None:
            result._origin = result
        return result

    def __radd__(self, other):
        if not isinstance(other, str):
            raise TypeError(f'unsupported operand type(s) for +: "{type(other)}" and String')
        if not other:
            return self

        # if other were a String, then we'd be in other.__add__, not self.__radd__
        assert not isinstance(other, String)

        s = other + str(self)

        left_lines = other.splitlines()

        # if we're prepending with a string that contains a tab on the same line,
        # we literally don't know what the resulting starting column should be.
        # with a tab_width of 8, it could be one of eight values.
        # and, faced with ambiguity, we decline to guess.
        # so we just return a str, not a String.
        if '\t' in left_lines[-1]:
            return s

        if self._line_number is None:
            self._calculate_line_and_column_numbers()

        if len(left_lines) > 1:
            last_segment = left_lines[-1]
            if (self._column_number - len(last_segment)) != self._first_column_number:
                return s
            line_number = self._line_number - (len(left_lines) - 1)
            if line_number < self._first_line_number:
                return s
            column_number = self._first_column_number
        else:
            line_number = self._line_number
            column_number = self._column_number - len(other)
            if column_number < self._first_column_number:
                return s

        result = self.__class__(s,
            source = self._source,
            origin = None,
            offset = 0,
            line_number = line_number,
            column_number = column_number,
            first_line_number = self._first_line_number,
            first_column_number = self._first_column_number,
            tab_width = self._tab_width,
            )
        result._origin = result
        return result

    def __getitem__(self, index):
        s = str(self)
        length = len(s)

        # if index is illegal, this will raise for us
        result = s[index]
        # if we reached here, index must be a legal value!

        result_length = len(result)

        if isinstance(index, slice):
            if (result_length > 1) and (index.step not in (1, None)):
                # this slice of the original can't be a viable String
                return result
            index = index.start or 0

            # slicing *clamps* to an acceptable range!
            if index < 0:
                index += length
                if index < 0:
                    index = 0
            elif index > length:
                index -= length
                if index > length:
                    index = length
        else:
            # indexing *raises an exception* if the index is out of range.
            if index < 0:
                index += length

        o = self.__class__(result,
            offset=self._offset + index,
            origin=self.origin,
            source=self._source,
            line_number=None,
            column_number=None,
            first_line_number=self._first_line_number,
            first_column_number=self._first_column_number,
            tab_width=self._tab_width,
            )
        return o

    # this is all we need to implement to support pickle!
    def __getnewargs_ex__(self):
        if self._origin == self:
            origin = None
        else:
            origin = self._origin
        return (
            (str(self),),
            {
                'source': self._source,
                'origin': origin,
                'offset': self._offset,
                'line_number': self._line_number,
                'column_number': self._column_number,
                'first_line_number': self._first_line_number,
                'first_column_number': self._first_column_number,
                'tab_width': self._tab_width,
            },
            )

    def __iter__(self):
        "also computes linebreak offsets if they haven't been cached yet"
        if self._line_number is None:
            self._calculate_line_and_column_numbers()

        klass = self.__class__
        origin = self._origin
        source = self._source
        line_number = self._line_number
        column_number = self._column_number
        offset = self._offset
        first_line_number = self._first_line_number
        first_column_number = self._first_column_number
        tab_width = self._tab_width

        compute_linebreak_offsets = (self._origin == self) and (self._linebreak_offsets is None)
        if compute_linebreak_offsets:
            linebreak_offsets = []

        waiting = None
        for s in str(self):
            if waiting:
                assert waiting == '\r'
                is_crlf = s == '\n'

                o = klass(waiting,
                    source=source,
                    origin=origin,
                    offset=offset,
                    line_number=line_number,
                    column_number=column_number,
                    first_line_number=first_line_number,
                    first_column_number=first_column_number,
                    tab_width=tab_width,
                    )
                yield o

                offset += 1

                if is_crlf:
                    # don't end the line until after s
                    column_number += 1
                else:
                    # end the line after waiting and before s
                    if compute_linebreak_offsets:
                        linebreak_offsets.append(offset)
                    line_number += 1
                    column_number = first_column_number

                o = klass(s,
                    source=source,
                    origin=origin,
                    offset=offset,
                    line_number=line_number,
                    column_number=column_number,
                    first_line_number=first_line_number,
                    first_column_number=first_column_number,
                    tab_width=tab_width,
                    )
                yield o
                offset += 1

                if s in linebreaks:
                    # new line for s
                    if compute_linebreak_offsets:
                        linebreak_offsets.append(offset)
                    line_number += 1
                    column_number = first_column_number
                else:
                    # advance normally for s
                    if s != '\t':
                        column_number += 1
                    else:
                        remainder = (column_number - first_column_number) % tab_width
                        distance_to_next_tab_stop = tab_width - remainder
                        column_number += distance_to_next_tab_stop

                waiting = None
            elif s == '\r':
                waiting = s
            else:
                o = klass(s,
                    source=source,
                    origin=origin,
                    offset=offset,
                    line_number=line_number,
                    column_number=column_number,
                    first_line_number=first_line_number,
                    first_column_number=first_column_number,
                    tab_width=tab_width,
                    )
                yield o
                offset += 1

                if s in linebreaks:
                    # new line for s
                    if compute_linebreak_offsets:
                        linebreak_offsets.append(offset)
                    line_number += 1
                    column_number = first_column_number
                else:
                    if s != '\t':
                        column_number += 1
                    else:
                        remainder = (column_number - first_column_number) % tab_width
                        distance_to_next_tab_stop = tab_width - remainder
                        column_number += distance_to_next_tab_stop

        if compute_linebreak_offsets:
            if waiting:
                # last character is a linebreak, add that offset
                linebreak_offsets.append(offset + 1)
            self._linebreak_offsets = tuple(linebreak_offsets)

        if waiting:
            o = klass(s,
                source=source,
                origin=origin,
                offset=offset,
                line_number=line_number,
                column_number=column_number,
                first_line_number=first_line_number,
                first_column_number=first_column_number,
                tab_width=tab_width,
                )
            yield o



    # these functions might return the same string,
    # or they might return a mutated string.
    # if the string doesn't change, return self.
    # otherwise return a str.
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

    def ljust(self, width, fillchar=' '):
        s = str(self)
        mutated = s.ljust(width, fillchar)
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
        s = str(self)
        mutated = s.replace(old, new, count)
        if s == mutated:
            return self
        return mutated

    def rjust(self, width, fillchar=' '):
        s = str(self)
        mutated = s.rjust(width, fillchar)
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

    def zfill(self, width):
        s = str(self)
        mutated = s.zfill(width)
        if s == mutated:
            return self
        return mutated

    #
    # if lstrip/rstrip/strip doesn't remove anything, return self.
    # otherwise, we can still return a String!
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
        # but String will support it all the way back to 3.6.
        s = str(self)
        if not s.startswith(prefix):
            return self
        return self[len(prefix):]

    def removesuffix(self, suffix):
        # new in Python 3.11 (I think?)
        # but String will support it all the way back to 3.6.
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
            return String.cat(*iterable)
        return str(self).join(iterable)

    def __repr__(self):
        if self._line_number is None:
            self._calculate_line_and_column_numbers()

        extras = []
        append = extras.append
        if self._source != None:
            append(f"source={self._source!r}")
        append(f"line_number={self._line_number}")
        append(f"column_number={self._column_number}")
        o = self._origin
        assert o != None
        if o != self:
            o = repr(str(o))
            if len(o) > 20:
                o = o[:15] + "[...]" + o[-1]
            append(f"origin=String({o})")
        if self._offset:
            append(f"offset={self._offset}")
        if self._first_line_number != 1:
            append(f"first_line_number={self._first_line_number}")
        if self._first_column_number != 1:
            append(f"first_column_number={self._first_column_number}")

        s = ", ".join(extras)

        return f"String({repr(str(self))}, {s})"

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

    def _calculate_line(self, line_number):
        origin = self._origin
        linebreak_offsets = origin._linebreak_offsets or origin._compute_linebreak_offsets()
        line_offset = line_number - self._first_line_number
        # print("\nLINE", line_number, linebreak_offsets)
        if not line_offset:
            starting_offset = 0
        else:
            starting_offset = linebreak_offsets[line_offset - 1]
        if line_offset == len(linebreak_offsets):
            ending_offset = len(origin)
        else:
            ending_offset = linebreak_offsets[line_offset]
        # print(f"{self=} {len(self)=}")
        # print(f"{line_offset=} {starting_offset=} {ending_offset=}")
        return origin[starting_offset:ending_offset]

    @property
    def line(self):
        if self._line is None:
            if self._line_number is None:
                self._calculate_line_and_column_numbers()
            line = self._calculate_line(self._line_number)
            if self:
                last_character = self[-1]
                if last_character._line_number is None:
                    last_character._calculate_line_and_column_numbers()
            else:
                last_character = self
            if last_character._line_number != self._line_number:
                ending_line = self._calculate_line(last_character._line_number)
                origin = self._origin
                line = origin[line._offset:ending_line._offset + len(ending_line)]
            self._line = line
        return self._line

    @property
    def previous_line(self):
        if self._line_number is None:
            self._calculate_line_and_column_numbers()
        if self._line_number == self._first_line_number:
            raise ValueError("self is already the first line")
        return self._calculate_line(self._line_number - 1)

    @property
    def next_line(self):
        if self._line is None:
            line = self.line
        else:
            line = self._line
        last_character = line[-1]
        origin = self._origin
        linebreak_offsets = origin._linebreak_offsets or origin._compute_linebreak_offsets()
        if last_character._line_number is None:
            last_character._calculate_line_and_column_numbers()
        last_character_line_number = last_character._line_number
        if (last_character_line_number - self._first_line_number) >= len(linebreak_offsets):
            raise ValueError("self is already the last line")
        return self._calculate_line(last_character_line_number + 1)


    def bisect(self, index):
        return self[:index], self[index:]

    @staticmethod
    def cat(*strings, metadata=None, line_number=None, column_number=None):
        if not strings:
            return ''

        first = strings[0]
        if metadata is None:
            if not isinstance(first, String):
                raise ValueError(f"if the first argument is not a String, you must explicitly specify metadata")
            # if they only specify one String to concatenate,
            # and don't specify metadata,
            # all we're gonna return is the first String, unmodified.
            if len(strings) == 1:
                return first
            metadata = first
        elif not isinstance(metadata, String):
            raise TypeError("metadata must be either String or None")
        elif metadata._line_number is None:
            metadata._calculate_line_and_column_numbers()

        origin = None

        if len(strings) == 1:
            s = first
            origin = metadata.origin
        else:
            s = "".join(strings)

            previous = None
            for l in strings:
                if not (isinstance(l, String) and ((previous is None) or previous.is_followed_by(l))):
                    break
                previous = l
            else:
                # contiguous!
                origin = first.origin

        ex = None
        if line_number == None:
            line_number = metadata._line_number
        else:
            if not isinstance(line_number, int):
                ex = TypeError
            elif line_number < metadata._first_line_number:
                ex = ValueError
            if ex:
                raise ex(f"line_number must be an int >= first_line_number ({metadata._first_line_number}), not {line_number}")

        if column_number == None:
            column_number = metadata._column_number
        else:
            if not isinstance(column_number, int):
                ex = TypeError
            elif column_number < metadata._first_column_number:
                ex = ValueError
            if ex:
                raise ex(f"column_number must be an int >= first_column_number ({metadata._first_column_number}), not {column_number}")

        o = String(s,
            source=metadata._source,
            offset=metadata._offset,
            origin=origin,
            line_number=line_number,
            column_number=column_number,
            first_line_number=metadata._first_line_number,
            first_column_number=metadata._first_column_number,
            tab_width=metadata._tab_width,
            )
        return o

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




_undefined = object()

class SpecialNodeError(LookupError):
    pass

# implementation detail, no public APIs expose nodes
class LinkedListNode:
    def __init__(self, value):
        self.value = value
        self.special = None # None, 'deleted', 'head', or 'tail'
        self.next = self.previous = None
        self.iterator_refcount = 0

    def insert_before(self, value):
        "inserts value into the linked list in front of self."

        # should never attempt to insert before head
        assert self.previous
        assert self.special != 'head'

        node = self.__class__(value)
        previous = self.previous

        node.next = self
        node.previous = previous
        previous.next = self.previous = node

    def clear(self):
        self.special = self.previous = self.next = self.value = self.iterator_refcount = None

    def unlink(self):
        # don't bother checking if self.special == 'deleted' or whatnot.
        # we might get called during shutdown while the GC is trying to
        # break cycles.  all we should do is--carefully--unlink the node.

        previous = self.previous
        next = self.next

        if previous:
            previous.next = next
        if next:
            next.previous = previous

        self.clear()

    def remove(self):
        assert not self.special

        value = self.value

        if not self.iterator_refcount:
            self.unlink()
        else:
            self.special = 'deleted'
            self.value = None
        return value

    def __repr__(self):
        special = f" ({self.special})" if self.special else ''
        return f"LinkedListNode({self.value!r}{special})"


@export
class LinkedList:
    def __init__(self, iterable=()):
        self._head = head = LinkedListNode(None)
        head.special = 'head'
        head.next = self._tail = tail = LinkedListNode(None)
        tail.special = 'tail'
        tail.previous = self._head
        self._length = 0
        for value in iterable:
            self.append(value)

    def __repr__(self):
        buffer = ["LinkedList(["]
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
    ## implement rich compare using *only*
    ## the relevant operator and ==:
    ##
    ##     * in __lt__, use <  and ==
    ##     * in __ge__, use >= and ==
    ##     * in __eq__, only use ==
    ##     * in __ne__, only use !=
    ##
    ## well, also len() on the list itself.
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
        return LinkedList(self)

    def copy(self):
        return self.__copy__()

    def __deepcopy__(self, memo):
        t = LinkedList()
        for value in self:
            t.append(copy.deepcopy(value, memo))
        return t

    def __add__(self, other):
        t = self.__copy__()
        t.extend(other)
        return t

    def __mul__(self, other):
        if not hasattr(other, '__index__'):
            raise TypeError(f"can't multiply sequence by non-int of type {type(other)!r}")
        index = other.__index__()
        if other <= 0:
            return LinkedList()
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
            return LinkedList()
        t = self.__copy__()
        for _ in range(index - 1):
            self.extend(t)
        return self

    def __iter__(self):
        return LinkedListIterator(self)

    def __reversed__(self):
        return LinkedListReverseIterator(self)

    def __bool__(self):
        return self._length > 0

    def __len__(self):
        return self._length

    def __contains__(self, value):
        return self.find(value) != None

    def _it_at_index(self, index):
        """
        index can be -1, in which case it points to head.
        index can be length, in which case it points to tail.
        this is to accommodate slicing semantics copied from list.
        """
        length = self._length
        assert -1 <= index <= length, f"index should be >= 0 and < {length} but it's {index}"

        it = iter(self)
        if index == -1:
            return it

        halfway = self._length // 2
        if index > halfway:
            it._cursor = self._tail
            index -= length
        else:
            it._cursor = self._head.next

        it._to_index(index)
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

        start = slice.start
        stop = slice.stop
        step = slice.step

        if step is None:
            step = 1
            step_is_negative = 0
        else:
            assert step != 0
            step_is_negative = step < 0

        length = self._length
        negative_length = -length

        if start is None:
            start = sys.maxsize * step_is_negative
        elif start < 0:
            if start >= negative_length:
                start += length
            else:
                # 0 if step is positive, -1 if step is negative
                start = -step_is_negative
        elif start >= length:
            start = length - step_is_negative

        if stop is None:
            stop = sys.maxsize * (1 - (step_is_negative * 2))
        elif stop < 0:
            if stop >= negative_length:
                stop += length
            else:
                # 0 if step is positive, -1 if step is negative
                stop = -step_is_negative
        elif stop >= length:
            stop = length - step_is_negative

        if step_is_negative and (stop < start):
            slice_length = ((start - stop - 1) // -step) + 1
        elif (not step_is_negative) and (start < stop):
            slice_length = ((stop - start - 1) // step) + 1
        else:
            slice_length = 0
            if for_assignment:
                # Make sure s[5:2] = [..] inserts at the right place:
                # before 5, not before 2.
                stop = start

        return start, stop, step, slice_length


    def _parse_key(self, key, *, for_assignment=False):
        """
        Parses key, which must be either an index or a slice object.

        Returns a 5-tuple:
            (it, start, stop, step, slice_length)
        it is an iterator pointing at the start'th entry.
        start is the index of the first element we want;
        it will be in the range 0 <= start < length.

        if key is a slice, stop, step, and slice_length
        will be integers.  stop will be in the same range
        as start, and step will not be zero.  slice_length
        will be how many numbers would be in the list
        if you called list(range(start, stop, step)).

        if key is not a slice, stop, step, and slice_length
        will all be None.

        enforces Python semantics for indexing with ints vs slices.
        for example, if a has 3 elements, a[5] is an IndexError,
        but a[5:1000] evaluates to an empty list.  (sigh.)
        so, _parse_key will raise the IndexError for you in
        the first case, but will clamp the slice values
        like list does in the second case.
        """
        if isinstance(key, slice):
            start, stop, step, slice_length = self._unpack_and_adjust_slice(key, for_assignment=for_assignment)
        else:
            length = self._length
            original_start = key
            start = key.__index__()
            if start < 0:
                start += length
            if not (0 <= start < length):
                raise IndexError(f'LinkedList index {original_start} out of range')
            stop = step = slice_length = None

        it = self._it_at_index(start)

        return it, start, stop, step, slice_length

    def __getitem__(self, key):
        it, start, stop, step, slice_length = self._parse_key(key)

        if stop is None:
            return it.value

        stop -= start
        return it.slice(0, stop, step)

    def __setitem__(self, key, value):
        it, start, stop, step, slice_length = self._parse_key(key, for_assignment=True)
        if stop is None:
            it.value = value
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

        if slice_length == 0:
            it.popslice(0, stop, step)
            return

        index = start
        advance = it.next
        retreat = it.previous
        indices = range(start, stop, step)

        for i, v in zip(indices, values):
            try:
                if (index + 1) == i:
                    # (hopefully) fast path
                    index = i
                    advance()
                else:
                    # slow path
                    while i > index:
                        advance()
                        index += 1
                    while i < index:
                        retreat()
                        index -= 1
                it.replace(v)
            except StopIteration:
                raise IndexError("LinkedList index out of range") from None

    def __delitem__(self, key):
        it, start, stop, step, slice_length = self._parse_key(key)
        if stop is None:
            it.pop()

        stop -= start
        it.popslice(0, stop, step)

    def insert(self, index, object):
        length = self._length
        # convert index to range 0 <= index <= length
        if index <= -length:
            index = 0
        elif index < 0:
            index += length
        elif index > length:
            index = length
        it = self._it_at_index(index)
        it.insert(object)

    def append(self, object):
        self._length += 1
        self._tail.insert_before(object)

    def extend(self, iterable):
        insert_before = self._tail.insert_before
        for value in iterable:
            self._length += 1
            insert_before(value)

    def appendleft(self, object):
        self._length += 1
        self._head.next.insert_before(object)

    def extendleft(self, iterable):
        insert_before = self._head.next.insert_before
        for value in iterable:
            self._length += 1
            insert_before(value)

    prepend = appendleft

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
                # keep node, but demote to "deleted"
                previous.special = 'deleted'
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
        while node_before_tail.special == 'deleted':
            node_before_tail = node_before_tail.previous
        if node_before_tail == self._head:
            raise IndexError('pop from empty LinkedList')
        self._length -= 1
        return node_before_tail.remove()

    def popleft(self):
        node_after_head = self._head.next
        while node_after_head.special == 'deleted':
            node_after_head = node_after_head.next
        if node_after_head == self._tail:
            raise IndexError('pop from empty LinkedList')
        self._length -= 1
        return node_after_head.remove()

    def count(self, value):
        counter = 0
        for v in self:
            if v == value:
                counter += 1
        return counter

    def find(self, value):
        return iter(self).find(value)

    def rfind(self, value):
        return reversed(self).find(value)

    def match(self, predicate):
        return iter(self).match(predicate)

    def rmatch(self, predicate):
        return reversed(self).match(predicate)

    def remove(self, value, default=_undefined):
        it = iter(self).find(value)
        if it is None:
            if default is not _undefined:
                return default
            raise ValueError('LinkedList.remove(x): x not in linked list')
        assert not it._cursor.special # find should never return a special node
        self._length -= 1
        return it._cursor.remove()

    def rremove(self, value, default=_undefined):
        it = reversed(self).find(value)
        if it is None:
            if default is not _undefined:
                return default
            raise ValueError('LinkedList.remove(x): x not in linked list')
        assert not it._cursor.special # find should never return a special node
        self._length -= 1
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

    def sort(self, key=None, reverse=None):
        # copy to list, sort, then write back in-place

        l = list(self)
        l.sort(key=key, reverse=reverse)

        it = iter(self)
        for v in l:
            next(it)
            it._cursor.value = v


@export
class LinkedListIterator:
    def __init__(self, linked_list):
        self._linked_list = linked_list
        self._cursor = cursor = linked_list._head
        cursor.iterator_refcount += 1

    def __repr__(self):
        return f"<{self.__class__.__name__} cursor={self._cursor!r}>"

    def __del__(self):
        # drop our reference to the current node.
        # that means decrementing node.iterator_refcount.
        # and if node.iterator_refcount reaches 0,
        # we *gotta* call unlink.
        _linked_list = getattr(self, "_linked_list", None)
        if _linked_list:
            setattr(self, "_linked_list", None)
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
        if (not iterator_refcount) and (special == 'deleted'):
            unlink = getattr(cursor, 'unlink', None)
            if unlink is not None:
                unlink()

    def __bool__(self):
        return self._cursor.special != 'tail'

    def __eq__(self, other):
        return (
            (self.__class__ == other.__class__)
            and (self._linked_list == other._linked_list)
            and (self._cursor == other._cursor)
            )

    def __iter__(self):
        return self

    def __reversed__(self):
        cursor = self._cursor
        copy = LinkedListReverseIterator(self._linked_list)
        copy._cursor = cursor
        cursor.iterator_refcount += 1
        return copy

    def _to_index(self, index):
        # starting at the current position,
        # advances or rewinds by index nodes.

        index = index.__index__()

        if not index:
            return

        if index < 0:
            advance = self.previous
            index = -index
        else:
            advance = self.next

        try:
            for _ in range(index):
                advance()
        except StopIteration:
            raise IndexError('LinkedList index out of range') from None

    def __next__(self):
        cursor = self._cursor
        special = cursor.special

        if special == 'tail':
            raise StopIteration

        cursor.iterator_refcount = iterator_refcount = cursor.iterator_refcount - 1
        next = cursor.next
        if (not iterator_refcount) and (special == 'deleted'):
            cursor.unlink()
        cursor = next
        special = cursor.special

        while special == 'deleted':
            cursor = cursor.next
            special = cursor.special

        self._cursor = cursor
        cursor.iterator_refcount += 1

        if special == 'tail':
            raise StopIteration
        return cursor.value

    def next(self, default=_undefined):
        if default == _undefined:
            return self.__next__()

        try:
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
        if (not iterator_refcount) and (special == 'deleted'):
            cursor.unlink()
        cursor = previous
        special = cursor.special

        while special == 'deleted':
            cursor = cursor.previous
            special = cursor.special

        self._cursor = cursor
        cursor.iterator_refcount += 1

        if special == 'head':
            raise StopIteration
        return cursor.value

    def previous(self, default=_undefined):
        if default == _undefined:
            return self.__previous__()

        try:
            return self.__previous__()
        except StopIteration:
            return default

    def copy(self):
        cursor = self._cursor
        copy = self.__class__(self._linked_list)
        copy._cursor = self._cursor
        cursor.iterator_refcount += 1
        return copy

    def before(self):
        cursor = self._cursor.previous
        if not cursor:
            return None
        while cursor.special == 'deleted':
            cursor = cursor.previous
        it = self.__class__(self._linked_list)
        it._cursor = cursor
        cursor.iterator_refcount += 1
        return it

    def after(self):
        cursor = self._cursor.next
        if not cursor:
            return None
        while cursor.special == 'deleted':
            cursor = cursor.next
        it = self.__class__(self._linked_list)
        it._cursor = cursor
        cursor.iterator_refcount += 1
        return it

    @property
    def special(self):
        return self._cursor.special

    @property
    def value(self):
        cursor = self._cursor
        if cursor.special:
            raise SpecialNodeError
        return cursor.value

    def replace(self, value):
        cursor = self._cursor
        if cursor.special:
            raise SpecialNodeError
        cursor.value = value

    def _pop(self, destination):
        # removes the node we're pointing at,
        # moves to destination, and returns the popped node's value.
        cursor = self._cursor
        if cursor.special:
            raise SpecialNodeError
        cursor.iterator_refcount -= 1
        value = cursor.remove()
        self._cursor = destination
        destination.iterator_refcount += 1
        self._linked_list._length -= 1
        return value

    def pop(self):
        cursor = self._cursor
        if cursor.special:
            raise SpecialNodeError
        cursor = cursor.previous
        while cursor.special == 'deleted':
            cursor = cursor.previous
        return self._pop(cursor)

    def popleft(self):
        cursor = self._cursor
        if cursor.special:
            raise SpecialNodeError
        cursor = cursor.next
        while cursor.special == 'deleted':
            cursor = cursor.next
        return self._pop(cursor)

    def _slice(self, start, stop, step, pop):
        if isinstance(start, slice):
            if (start != _undefined) or (step != _undefined):
                raise ValueError('if start is a slice object, you cannot supply arguments for stop and step')
            stop = start.stop.__index__()
            step = 1 if (start.step is None) else start.step.__index__()
            start = _undefined if (start.start is None) else start.start.__index__()
        else:
            start = start.__index__()

            if stop == _undefined:
                stop = start
                start = _undefined
            else:
                stop = stop.__index__()

            if step == _undefined:
                step = 1
            else:
                step = step.__index__()

        if start == _undefined:
            if stop >= 0:
                # slice(0), slice(5), etc
                # start at it[0] and grab N values
                start = 0
            else:
                # slice(-1), slice(-5)
                # start at (1+N) and grab N values
                # so that the last value is it[0]
                start = stop + 1
                stop = 1

        if not step:
            raise ValueError("step must not be 0")

        result = self._linked_list.__class__()
        if start == stop:
            return result
        append = result.append

        it = self.copy()
        index = 0
        advance = it.next
        retreat = it.previous
        if pop:
            if step > 0:
                pop = it.pop
            else:
                pop = it.popleft

        for i in range(start, stop, step):
            try:
                if (index + 1) == i:
                    # (hopefully) fast path
                    index = i
                    append(advance())
                else:
                    # slow path
                    while i > index:
                        advance()
                        index += 1
                    while i < index:
                        retreat()
                        index -= 1
                    append(it.value)
                if pop:
                    pop()
            except StopIteration:
                raise IndexError("LinkedList index out of range") from None

        return result

    def slice(self, start, stop=_undefined, step=_undefined):
        return self._slice(start, stop, step, False)

    def popslice(self, start, stop=_undefined, step=_undefined):
        return self._slice(start, stop, step, True)

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

    def prepend(self, value):
        cursor = self._cursor
        if cursor.special == 'head':
            # API affordance: allow "sloppy insert" *before* 'head'
            cursor = cursor.next
        # it's okay if cursor is a deleted node here.
        self._linked_list._length += 1
        cursor.insert_before(value)

    insert = prepend

    def extend(self, iterable):
        cursor = self._cursor
        if cursor.special != 'tail':
            cursor = cursor.next
        linked_list = self._linked_list
        insert_before = cursor.insert_before
        for value in iterable:
            linked_list._length += 1
            insert_before(value)

    def append(self, value):
        cursor = self._cursor
        # API affordance: allow "sloppy append" *after* 'tail'
        if cursor.special != 'tail':
            cursor = cursor.next
        # it's okay if cursor is a deleted node here.
        self._linked_list._length += 1
        cursor.insert_before(value)

    def extendleft(self, iterable):
        linked_list = self._linked_list
        insert_before = self._cursor.insert_before
        for value in iterable:
            linked_list._length += 1
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

        result = self.__class__(self._linked_list)
        result._cursor = cursor
        cursor.iterator_refcount += 1
        return result

    def rfind(self, value):
        cursor = self._cursor

        while True:
            special = cursor.special
            if (not special) and (cursor.value == value):
                break
            if special == 'head':
                return None
            cursor = cursor.previous

        result = self.__class__(self._linked_list)
        result._cursor = cursor
        cursor.iterator_refcount += 1
        return result

    def match(self, predicate):
        cursor = self._cursor

        while True:
            special = cursor.special
            if (not special) and predicate(cursor.value):
                break
            if special == 'tail':
                return None
            cursor = cursor.next

        result = self.__class__(self._linked_list)
        result._cursor = cursor
        cursor.iterator_refcount += 1
        return result

    def rmatch(self, predicate):
        cursor = self._cursor

        while True:
            special = cursor.special
            if (not special) and predicate(cursor.value):
                break
            if special == 'head':
                return None
            cursor = cursor.previous

        result = self.__class__(self._linked_list)
        result._cursor = cursor
        cursor.iterator_refcount += 1
        return result



@export
class LinkedListReverseIterator(LinkedListIterator):
    def __init__(self, linked_list):
        super().__init__(linked_list)
        self._cursor = linked_list._tail

    def __reversed__(self):
        cursor = self._cursor
        copy = LinkedListIterator(self._linked_list)
        copy._cursor = cursor
        cursor.iterator_refcount += 1
        return copy

    def __next__(self):
        return super().__previous__()

    def __previous__(self):
        return super().__next__()

    def before(self):
        return super().after()

    def after(self):
        return super().before()

    def __bool__(self):
        return self._cursor.special != 'head'

    def prepend(self, value):
        return super().append(value)

    def append(self, value):
        return super().prepend(value)

    def extend(self, value):
        return super().extendleft(value)

    def extendleft(self, value):
        return super().extend(value)

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


del export
