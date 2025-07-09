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



#############################################
#############################################
##         _        _
##     ___| |_ _ __(_)_ __   __ _
##    / __| __| '__| | '_ \ / _` |
##    \__ \ |_| |  | | | | | (_| |
##    |___/\__|_|  |_|_| |_|\__, |
##                          |___/
##
#############################################
#############################################

##
## string uses _re_linebreaks_finditer to split lines by linebreaks.
## string implements Python's rules about where to split a line,
## and Python recognizes the DOS '\r\n' sequence as *one linebreak*.
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


@export
class string(str):
    """
    A subclass of str that maintains line, column, and offset information.

    string is a drop-in replacement for Python's str that automatically
    computes the line, column, and offset of any substring.  It's a subclass
    of str, and implements every str method.

    Additional features of string:
    * Every string knows its line number, column number, and offset from the
      beginning of the original string.
    * You may also specify a "source" parameter to the constructor,
      which should indicate where the text came from (e.g. the filename).

    Additional attributes of string:
    * s.line_number is the line number of the first character of this string.
    * s.column_number is the column number of the first character of this string.
    * s.offset is the index of the first character of this string from where it
      came from in the original string.  (e.g. if the original string was 'abcde',
      'e' would have an offset of 4.)
    * s.where is a string designed for error messages.  if the original string
      was initialized with a source, this will be in the format
          "<source>" line <line_number> column <column_number>
      If no source was supplied, this will be in the format
          line <line_number> column <column_number>
      This makes writing error messages easy.  If err contains a syntax error,
      you can raise
          SyntaxError(f"{err.where}: {err}")
    """

    __slots__ = ('_source', '_origin', '_offset', '_line_number', '_column_number', '_first_line_number', '_first_column_number', '_tab_width', '_linebreak_offsets', '_line')

    def __new__(cls, s, *, source=None, origin=None, offset=0, line_number=1, column_number=1, first_line_number=1, first_column_number=1, tab_width=8):
        if isinstance(s, string):
            return s
        if not isinstance(s, str):
            raise TypeError("string: s must be a str or string object")

        if not ((origin is None) or isinstance(origin, string)):
            raise TypeError(f"string: origin must be string or None, not {type(origin)}")

        if isinstance(source, str):
            if isinstance(source, string):
                source = str(source)
        elif source == None:
            if origin is not None:
                source = origin.source
        else:
            raise TypeError(f"string: source must be str or None, not {type(source)}")

        ex = None

        if not isinstance(offset, int):
            ex = TypeError
        elif offset < 0:
            ex = ValueError
        if ex:
            raise ex(f"string: offset must be an int >= 0, not {offset}")

        if not isinstance(first_line_number, int):
            ex = TypeError
        elif first_line_number < 0:
            ex = ValueError
        if ex:
            raise ex("string: first_line_number must be an int >= 0")

        if not isinstance(first_column_number, int):
            ex = TypeError
        elif first_column_number < 0:
            ex = ValueError
        if ex:
            raise ex("string: first_column_number must be an int >= 0")

        # secret API: if you pass in None for line_number and column_number,
        # it's lazy-calculated
        if not (line_number == column_number == None):
            if not isinstance(line_number, int):
                ex = TypeError
            elif line_number < 0:
                ex = ValueError
            if ex:
                raise ex("string: line_number must be an int >= 0")

            if not isinstance(column_number, int):
                ex = TypeError
            elif column_number < 0:
                ex = ValueError
            if ex:
                raise ex(f"string: column_number must be an int >= 0, not {column_number}")

            if line_number < first_line_number:
                raise ValueError("string: line_number can't be less than first_line_number")

            if column_number < first_column_number:
                raise ValueError("string: column_number can't be less than first_column_number")

        if not isinstance(tab_width, int):
            ex = TypeError
        elif tab_width < 1:
            ex = ValueError
        if ex:
            raise ex("string: tab_width must be an int >= 1")

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
    # if l is a string, l == str(l), l < str(l) + 'x', l + 'x' > str(l), etc

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
        if not isinstance(other, string):
            return False

        if self.origin != other.origin:
            return False

        return self._offset + len(self) == other._offset

    def __add__(self, other):
        if not isinstance(other, str):
            raise TypeError(f'can only concatenate str (not "{type(other)}") to string')
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
            raise TypeError(f'unsupported operand type(s) for +: "{type(other)}" and string')
        if not other:
            return self

        # if other were a string, then we'd be in other.__add__, not self.__radd__
        assert not isinstance(other, string)

        s = other + str(self)

        left_lines = other.splitlines()

        # if we're prepending with a string that contains a tab on the same line,
        # we literally don't know what the resulting starting column should be.
        # with a tab_width of 8, it could be one of eight values.
        # and, faced with ambiguity, we decline to guess.
        # so we just return a str, not a string.
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
                # this slice of the original can't be a viable string
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
    # otherwise, we can still return a string!
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
            return string.cat(*iterable)
        return str(self).join(iterable)

    def serialized(self):
        """
        Returns a string that, if executed in Python, recreates this string object.

        Traditionally this is what repr would produce; however, it's simply too
        inconvenient for repr(string_object) to produce anything except the
        traditional str repr.
        """
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
            # elide origin if it's more than 20 characters? ... naah.
            # if len(o) > 20:
            #     o = o[:15] + "[...]" + o[-1]
            append(f"origin=string({o})")
        if self._offset:
            append(f"offset={self._offset}")
        if self._first_line_number != 1:
            append(f"first_line_number={self._first_line_number}")
        if self._first_column_number != 1:
            append(f"first_column_number={self._first_column_number}")
        if self._tab_width != 8:
            append(f"tab_width={self._tab_width}")

        s = ", ".join(extras)

        return f"string({repr(str(self))}, {s})"

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
            if not isinstance(first, string):
                raise ValueError(f"if the first argument is not a string, you must explicitly specify metadata")
            # if they only specify one string to concatenate,
            # and don't specify metadata,
            # all we're gonna return is the first string, unmodified.
            if len(strings) == 1:
                return first
            metadata = first
        elif not isinstance(metadata, string):
            raise TypeError("metadata must be either string or None")
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
                if not (isinstance(l, string) and ((previous is None) or previous.is_followed_by(l))):
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

        o = string(s,
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



######################################################
######################################################
##
##      _ _       _            _     _ _     _
##     | (_)_ __ | | _____  __| |   | (_)___| |_
##     | | | '_ \| |/ / _ \/ _` |   | | / __| __|
##     | | | | | |   <  __/ (_| |   | | \__ \ |_
##     |_|_|_| |_|_|\_\___|\__,_|   |_|_|___/\__|
##
##
######################################################
######################################################


_undefined = object()

class SpecialNodeError(LookupError):
    pass

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

        # should never attempt to insert before head
        assert self.previous
        assert self.special != 'head'

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

    def index(self, index, allow_head_and_tail=False, clamp=False):
        # return a cursor (pointer to a node),
        # starting at the current position,
        # relative to index.  ignores special nodes.
        # if we attempt to iterate past the end of the list
        # in either direction, return None--
        # except if clamp is False, in which case we return the last node before the end.

        index = index.__index__()
        cursor = self

        if index < 0:
            while index:
                c = cursor.previous
                if c is None:
                    return cursor if clamp else None
                cursor = c
                if c.special:
                    if (not allow_head_and_tail) or (c.special != 'head'):
                        continue
                index += 1
            return cursor

        while index:
            c = cursor.next
            if c is None:
                return cursor if clamp else None
            cursor = c
            if c.special:
                if (not allow_head_and_tail) or (c.special != 'tail'):
                    continue
            index -= 1
        return cursor


    def nodes(self, start, first, stop, last, step):
        cursor = first
        index = start
        for i in range(start, stop, step):
            if i == 0:
                # index 0 is *always* self.
                # if self is deleted, we just skip over it.
                cursor = self
                index = 0
                if not self.special:
                    yield self
                continue

            if (index + 1) == i:
                # (hopefully) fast path
                cursor = cursor.next
                index = i
                yield cursor
                continue

            while index < i:
                cursor = cursor.next
                index += 1
            while index > i:
                cursor = cursor.previous
                index -= 1
            yield cursor

    nodes_iterator = nodes

    def nodes(self, start, stop, step, *, clamp=False):
        """
        Returns None if either start or stop is out of range.
        Iterator, yields nodes.
        """

        step = step.__index__()
        if not step:
            raise ValueError("step must not be 0")

        start = start.__index__()
        stop = stop.__index__()

        first = self.index(start, clamp=clamp)
        last = self.index(stop, allow_head_and_tail=True, clamp=clamp)
        if (first is None) or (last is None):
            return None

        if step < 0:
            if start <= stop:
                return iter(())
        elif start >= stop:
            return iter(())

        return self.nodes_iterator(start, first, stop, last, step)


    def __repr__(self):
        if self.special:
            special = f', special={self.special!r}'
        else:
            special = ''
        return f"linked_list_node({self.value!r}{special})"


@export
class linked_list:
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
    ## implement rich compare using *only*
    ## the relevant operator and ==:
    ##
    ##     * in __lt__, use <  and ==
    ##     * in __le__, use <= and ==
    ##     * in __ge__, use >= and ==
    ##     * in __gt__, use >  and ==
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

    def __add__(self, other):
        t = self.__copy__()
        t.extend(other)
        return t

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
            step_is_positive = 1
            step_is_negative = 0
        else:
            assert step != 0
            step_is_positive = step > 0
            step_is_negative = not step_is_positive

        length = self._length
        negative_length = -length

        if start is None:
            # start = sys.maxsize * step_is_negative
            start = length * step_is_negative
        elif start < 0:
            if start >= negative_length:
                start += length
            else:
                # 0 if step is positive, -1 if step is negative
                start = -step_is_negative
        elif start >= length:
            start = length - step_is_negative

        if stop is None:
            # stop = sys.maxsize * (1 - (step_is_negative * 2))
            stop = length if step_is_positive else -1
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

        assert -1 <= start <= length, f"failed: 0 <= {start} <= {length}"
        assert -1 <= stop <= length, f"failed: -1 <= {stop} <= {length}"

        return start, stop, step, slice_length

    def _parse_key(self, key, *, for_assignment=False):
        """
        Parses the "key" argument from a __{get,set,del}item__ call,
        which must be either an index or a slice object.

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
                raise IndexError(f'linked_list index {original_start} out of range')
            stop = step = slice_length = None

        it = self._it_at_index(start)

        return it, start, stop, step, slice_length

    def __getitem__(self, key):
        it, start, stop, step, slice_length = self._parse_key(key)

        if stop is None:
            return it._cursor.value

        stop -= start
        return it.slice(0, stop, step)

    def __setitem__(self, key, value):
        it, start, stop, step, slice_length = self._parse_key(key, for_assignment=True)
        if stop is None:
            it.replace(value)
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
            # overwrite a zero-length slice with a zero-length iterable? okay!
            return

        index = start
        advance = it.next
        retreat = it.previous
        indices = range(start, stop, step)

        for i, v in zip(indices, values):
            # I think it's impossible to overshoot
            # try:
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
            # except StopIteration:
            #     raise IndexError("linked_list index out of range") from None

    def __delitem__(self, key):
        it, start, stop, step, slice_length = self._parse_key(key)
        if stop is None:
            it.pop()
            return

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
        it._cursor.insert_before(object)

    def append(self, object):
        self._tail.insert_before(object)

    def extend(self, iterable):
        insert_before = self._tail.insert_before
        for value in iterable:
            insert_before(value)

    def appendleft(self, object):
        self._head.next.insert_before(object)

    def extendleft(self, iterable):
        insert_before = self._head.next.insert_before
        for value in iterable:
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
            raise IndexError('pop from empty linked_list')
        return node_before_tail.remove()

    def popleft(self):
        node_after_head = self._head.next
        while node_after_head.special == 'special':
            node_after_head = node_after_head.next
        if node_after_head == self._tail:
            raise IndexError('pop from empty linked_list')
        return node_after_head.remove()

    def count(self, value):
        return iter(self).count(value)

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
            raise ValueError('linked_list.remove(x): x not in linked list')
        assert not it._cursor.special # find should never return a special node
        return it._cursor.remove()

    def rremove(self, value, default=_undefined):
        it = reversed(self).find(value)
        if it is None:
            if default is not _undefined:
                return default
            raise ValueError('linked_list.remove(x): x not in linked list')
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

    def cut(self, start=None, end=None):
        # first, check that start and end are legal values,
        # while also converting them to be pointers to nodes,
        # and changing end so it points to the last node to cut.

        start_is_none = start is None
        end_is_none = end is None

        start_is_reversed = None if start_is_none else isinstance(start, linked_list_reverse_iterator)
        end_is_reversed = None if end_is_none else isinstance(end, linked_list_reverse_iterator)

        if start_is_reversed or end_is_reversed:
            if (start_is_reversed is False) or (end_is_reversed is False):
                raise ValueError("mismatched forward and reverse iterators")

            tmp = start
            start = end
            end = tmp

            if start:
                if start._cursor == self._tail:
                    start = None
                else:
                    tmp = iter(self)
                    tmp._cursor = start._cursor.next
                    start = tmp
            if end:
                if end._cursor == self._tail:
                    end = None
                else:
                    tmp = iter(self)
                    tmp._cursor = end._cursor.next
                    end = tmp

        if start_is_none:
            start = self._head
        else:
            start = start._cursor
            if start.linked_list is not self:
                raise ValueError("start is not an iterator on this linked_list")

        if end_is_none:
            end = self._tail
        else:
            # convert end so it points to the last node to cut.
            # (rather than one node past it, at the first node not cut.)
            end = end._cursor.previous
            if end.linked_list is not self:
                raise ValueError("end is not an iterator on this linked_list")

        if start_is_none or end_is_none:
            cursor = start
            while cursor and (cursor != end):
                cursor = cursor.next
            if not cursor:
                raise ValueError("end points to a node before start")

        # everything checks out, and we can cut.
        # do all our memory allocation before changing anything,
        # so that if an allocation fails we don't change anything.

        cls = type(self)
        t2 = cls()

        new_head = linked_list_node(self, None, 'head') if start is self._head else None
        new_tail = linked_list_node(self, None, 'tail') if end is self._tail else None

        # all our allocations are done! modify self.
        print(f"{start=} {end=}\n{new_head=} {new_tail=}")

        if new_head:
            # start is currently self._head.
            # set t2._head to be start, and
            # give self a new _head.
            print("start is _head, swap heads around")
            self._head = new_head
            t2._head = start
            previous = new_head
        else:
            # splice in start after t2._head
            print("splice in start after t2._head")
            head = t2._head
            head.next = start
            previous = start.previous
            start.previous = head

        if new_tail:
            # end is currently self._tail.
            # set t2._tail to be end, and
            # give self a new _tail.
            print("end is _tail, swap tails around")
            self._tail = new_tail
            t2._tail = end
            next = new_tail
        else:
            # splice in end before t2._tail
            print("splice in end before t2._tail")
            tail = t2._tail
            tail.previous = end
            next = end.next
            end.next = tail

        print(f"{previous=} {next=}")

        # at this point,
        # previous points to the node in t just before the cut,
        # and next points to the node in t just after the cut.
        previous.next = next
        next.previous = previous

        while start != end:
            start.linked_list = t2
            start = start.next

        return t2

    def splice(self, other, where=None):
        if not isinstance(other, linked_list):
            raise ValueError('other must be a linked_list')

        if where is None:
            where = self._tail.previous
        else:
            if not isinstance(where, linked_list_base_iterator):
                raise ValueError('where must be a linked_list iterator')
            reversed = isinstance(where, linked_list_reverse_iterator)
            where = where._cursor
            if where.linked_list != self:
                raise ValueError("where must be an iterator over self")
            if reversed:
                where = where.previous

        # do allocations first
        new_head = linked_list_node(other, None, 'head')
        new_tail = linked_list_node(other, None, 'tail')

        if (where is self._tail) or (where is None):
            # insert new special node
            where = linked_list_node(self, None, 'special')

            if where is self._tail:
                where.previous = self._tail.previous
                where.previous.next = where
                where.next = self._tail
                self._tail.previous = where
            else:
                # where was a reversed iterator pointing at _head.
                where = linked_list_node(self, None, 'special')
                where.next = self._head.next
                where.next.previous = where
                where.previous = self._head
                self._head.next = where

        after = where.next
        assert after

        where.next = other._head
        other._head.previous = where

        after.previous = other._tail
        other._tail.next = after

        other._head = new_head
        other._tail = new_tail
        new_head.next = new_tail
        new_tail.previous = new_head

        while where != after:
            where.linked_list = self
            where = where.next



_sentinel = object()

@export
class linked_list_base_iterator:
    __slots__ = ('_cursor',)

    def __init__(self, node):
        if type(self) == linked_list_base_iterator:
            raise TypeError("instances of linked_list_base_iterator are not permitted")
        node.iterator_refcount += 1
        self._cursor = node

        self._filtering = False
        self._stop_at_cursor = None
        self._find_value = _sentinel
        self._match_predicate = None

    def __repr__(self):
        return f"<{self.__class__.__name__} cursor={self._cursor!r}>"

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
        return self._cursor.special != 'tail'

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
        return self.copy()

    def __len__(self):
        length = 0
        cursor = self._cursor
        while cursor is not None:
            if not cursor.special:
                length += 1
            cursor = cursor.next

    def _cursor_at_index(self, index, clamp=False):
        # return a cursor (pointer to a node),
        # starting at the current position,
        # relative to index.  ignores special nodes.

        cursor = self._cursor
        index = index.__index__()

        if not index:
            return cursor

        if index < 0:
            while index:
                c = cursor.previous
                if c is None:
                    if clamp:
                        break
                    raise ValueError("went past head")
                if c.special:
                    continue
                cursor = c
                index += 1
            return cursor

        while index:
            c = cursor.next
            if c is None:
                if clamp:
                    break
                raise ValueError("went past tail")
            if c.special:
                continue
            cursor = c
            index -= 1
        return cursor

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

        for _ in range(index):
            advance()

    def linked_list(self):
        return self._cursor.linked_list

    def set_filters(self, *, stop_at=None, find=_sentinel, match=None):
        """
        If find and match are both specified, they combine with 'and'.
        (This iterator will only yield values that satisfy both find AND match.)
        Every set_filters call resets the filter for any argument not supplied.
        (Calling set_filters with no arguments resets all filters.)
        """
        if stop_at is not None:
            self._stop_at_cursor = stop_at._cursor
        else:
            self._stop_at_cursor = None
        self._find_value = find
        self._match_predicate = match
        self._filtering = (self._stop_at_cursor != None) or (self._find_value != _sentinel) or (self._match_predicate != None)

    def __next__(self):
        cursor = self._cursor
        special = cursor.special

        if (special == 'tail') or (cursor is self._stop_at_cursor):
            raise StopIteration

        cursor.iterator_refcount = iterator_refcount = cursor.iterator_refcount - 1
        next = cursor.next
        if (not iterator_refcount) and (special == 'special'):
            cursor.unlink()

        stop_iteration = False
        if not self._filtering:
            # fast path
            cursor = next
            special = cursor.special
            while special == 'special':
                cursor = cursor.next
                special = cursor.special
        else:
            # slow path
            stop_at_cursor = self._stop_at_cursor
            find_value = self._find_value
            sentinel = _sentinel
            match_predicate = self._match_predicate
            while True:
                cursor = next
                next = cursor.next
                special = cursor.special
                value = cursor.value

                if cursor is stop_at_cursor:
                    stop_iteration = True
                    break

                if special:
                    if special == 'special':
                        continue
                    assert special in ('head', 'tail')
                    break

                if not ((find_value is sentinel) or (value == find_value)):
                    continue
                if not ((match_predicate is None) or match_predicate(value)):
                    continue
                break

        self._cursor = cursor
        cursor.iterator_refcount += 1

        if special == 'tail':
            stop_iteration = True
        if stop_iteration:
            raise StopIteration
        return cursor.value

    def next(self, default=_undefined, *, count=1):
        if count < 0:
            raise ValueError("next count can't be negative")
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

        if (special == 'head') or (cursor is self._stop_at_cursor):
            raise StopIteration

        cursor.iterator_refcount = iterator_refcount = cursor.iterator_refcount - 1
        previous = cursor.previous
        if (not iterator_refcount) and (special == 'special'):
            cursor.unlink()

        stop_iteration = False
        if not self._filtering:
            # fast path
            cursor = previous
            special = cursor.special
            while special == 'special':
                cursor = cursor.previous
                special = cursor.special
        else:
            # slow path
            stop_at_cursor = self._stop_at_cursor
            find_value = self._find_value
            sentinel = _sentinel
            match_predicate = self._match_predicate
            while True:
                cursor = previous
                previous = cursor.previous
                special = cursor.special
                value = cursor.value

                if cursor is stop_at_cursor:
                    stop_iteration = True
                    break

                if special:
                    if special == 'special':
                        continue
                    assert special in ('head', 'tail')
                    break

                if not ((find_value is sentinel) or (value == find_value)):
                    continue
                if not ((match_predicate is None) or match_predicate(value)):
                    continue
                break

        self._cursor = cursor
        cursor.iterator_refcount += 1

        if special == 'head':
            stop_iteration = True
        if stop_iteration:
            raise StopIteration
        return cursor.value

    def previous(self, default=_undefined, *, count=1):
        if count < 0:
            raise ValueError("previous count can't be negative")
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

    def copy(self):
        it = self.__class__(self._cursor)
        it._filtering = self._filtering
        it._stop_at_cursor = self._stop_at_cursor
        it._find_value = self._find_value
        it._match_predicate = self._match_predicate
        return it

    def before(self, count=1):
        if count < 0:
            return self.after(-count)
        cursor = self._cursor
        while count:
            cursor = cursor.previous
            if cursor is None:
                return None
            if cursor.special == 'special':
                continue
            count -= 1
        return self.__class__(cursor)

    def after(self, count=1):
        if count < 0:
            return self.before(-count)
        cursor = self._cursor
        while count:
            cursor = cursor.next
            if cursor is None:
                return None
            if cursor.special == 'special':
                continue
            count -= 1
        return self.__class__(cursor)

    def to_head(self):
        self._cursor = self._cursor.linked_list._head

    def to_tail(self):
        self._cursor = self._cursor.linked_list._tail

    @property
    def is_head(self):
        return self._cursor.special == 'head'

    @property
    def is_tail(self):
        return self._cursor.special == 'tail'

    @property
    def is_special(self):
        return self._cursor.special is not None

    def _item_lookup(self, key):
        """
        Only returns a valid data node.
        If key indexes to a special node, or overshoots head/tail,
        raises an exception.
        """
        key = key.__index__()
        cursor = self._cursor
        if key == 0:
            if cursor.special:
                raise SpecialNodeError()
        else:
            cursor = cursor.index(key)
            if (cursor is None) or cursor.special:
                raise IndexError()
        return cursor

    def _slice_lookup(self, key):
        cursor = self._cursor
        start = key.start
        start = 0 if start is None else start.__index__()
        stop = key.stop
        stop = 0 if stop is None else stop.__index__()
        step = key.step
        step = 1 if step is None else step.__index__()
        cursor = self._cursor
        it = cursor.nodes(start, stop, step)
        if it is None:
            raise IndexError()
        return it

    def __getitem__(self, key):
        if isinstance(key, slice):
            it = self._slice_lookup(key)
            return type(self._cursor.linked_list)(o.value for o in it)
        cursor = self._item_lookup(key)
        return cursor.value

    def __setitem__(self, key, value):
        cursor = self._item_lookup(key)
        cursor.value = value

    def __delitem__(self, key):
        cursor = self._item_lookup(key)
        cursor.remove()

    def insert(self, index, object):
        cursor = self._item_lookup(key)
        # support for sloppy insert here:
        # if you have an iterator IT pointed at head,
        # you can call IT.prepend(value)
        # and that creates the special node etc etc.
        # therefore, inserting a node before head is ok.
        # therefore, it should be okay here, and do the same thing.
        if cursor.special == 'head':
            cursor = cursor.next
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
        return value

    def pop(self):
        cursor = self._cursor
        if cursor.special:
            raise SpecialNodeError
        cursor = cursor.previous
        while cursor.special == 'special':
            cursor = cursor.previous
        return self._pop(cursor)

    def popleft(self):
        cursor = self._cursor
        if cursor.special:
            raise SpecialNodeError
        cursor = cursor.next
        while cursor.special == 'special':
            cursor = cursor.next
        return self._pop(cursor)

    def _slice(self, start, stop, step, pop):

        # deliberately not the same as list slicing mechanics.
        # in particular, this does not clamp for you.

        linked_list = self._cursor.linked_list

        step = step.__index__()
        if not step:
            raise ValueError("step must not be 0")

        start = start.__index__()

        if stop is not None:
            stop = stop.__index__()
        else:
            if start >= 0:
                # slice(0), slice(5), etc
                # start at it[0] and grab N values
                stop = start
                start = 0
            else:
                # slice(-1), slice(-5)
                # start at (1+N) and grab N values
                # so that the last value is it[0]
                start += 1
                stop = 1

        # at this point stop is guaranteed to not be None
        result = self._cursor.linked_list.__class__()
        step_is_negative = step < 0


        # print(f">> {start=} {stop=} {step=}")

        if step_is_negative:
            if start <= stop:
                return result
        elif start >= stop:
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

        # print(">>", it, start, stop, step)

        popped_zero = False

        for i in range(start, stop, step):
            if i == 0:
                # index 0 is *always* self,
                # and it's always an error if self is a special node.
                if self._cursor.special:
                    raise SpecialNodeError()
                append(self._cursor.value)

                # fast path to update it and index
                index = 0
                it._cursor = self._cursor

                if pop:
                    pop()
                    popped_zero = True

                continue

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
                    append(it._cursor.value)
                if pop:
                    pop()
            except StopIteration:
                raise IndexError(f"linked_list index {index} out of range") from None

        # don't do this until after we're done popping nodes,
        # we want to skip over all deleted nodes here.
        if popped_zero:
            self.previous(None)

        return result

    def slice(self, start, stop=None, step=1):
        """
        Returns a slice of the linked list, relative to the current node.

        The rules for handling arguments and default values:
          * step must be an integer, and defaults to 1.
          * start is required, and stop defaults to None.
          * start and stop cannot both be None.
          * if stop is a value and start is None, it swaps
            stop and start, then returns the value described
            in the next bullet point.
          * if start is a value and stop is None, slice returns
            abs(start) values, either starting or ending with index 0.
            if start is greater than 0, it returns values from
            range(0, start - 1, step). if start is less than 0,
            it returns values from indices range(start + 1, 1, step).

        Raises SpecialNodeError if the slice crosses index 0
        and the iterator is pointing at a special node.
        """
        return self._slice(start, stop, step, False)

    def popslice(self, start, stop=None, step=1):
        """
        Pops a slice of the linked list, relative to the current node.

        This removes the slice from the linked list.  If this pops the
        node the iterator is currently pointing at, the cursor is moved
        to the previous node (which may be 'head').

        The rules for handling arguments and default values:
          * step must be an integer, and defaults to 1.
          * start is required, and stop defaults to None.
          * start and stop cannot both be None.
          * if stop is a value and start is None, it swaps
            stop and start, then returns the value described
            in the next bullet point.
          * if start is a value and stop is None, slice returns
            abs(start) values, either starting or ending with index 0.
            if start is greater than 0, it returns values from
            range(0, start - 1, step). if start is less than 0,
            it returns values from indices range(start + 1, 1, step).

        Raises SpecialNodeError if the slice crosses index 0
        and the iterator is pointing at a special node.
        """
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
        # -- handle self pointing at head, or not --
        cursor = self._cursor
        if cursor.special == 'head':
            cursor.iterator_refcount -= 1
            cursor = cursor.next
            self._cursor = cursor = cursor.insert_before(None, 'special')
            cursor.iterator_refcount += 1
        # -- actually append value --
        cursor.insert_before(value)

    def append(self, value):
        # -- handle self pointing at tail, or not --
        cursor = self._cursor
        if cursor.special == 'tail':
            cursor.iterator_refcount -= 1
            self._cursor = special_node = cursor.insert_before(None, 'special')
            special_node.iterator_refcount += 1
        else:
            cursor = cursor.next
        # -- actually append value --
        cursor.insert_before(value)

    def extend(self, iterable):
        # -- handle self pointing at tail, or not --
        cursor = self._cursor
        if cursor.special == 'tail':
            cursor.iterator_refcount -= 1
            self._cursor = special_node = cursor.insert_before(None, 'special')
            special_node.iterator_refcount += 1
        else:
            cursor = cursor.next
        # -- actually extend from iterator --
        counter = 0
        insert_before = cursor.insert_before
        for value in iterable:
            counter += 1
            insert_before(value)

    def extendleft(self, iterable):
        # handle self pointing at head, or not --
        cursor = self._cursor
        if cursor.special == 'head':
            cursor.iterator_refcount -= 1
            cursor = cursor.next
            self._cursor = cursor = cursor.insert_before(None, 'special')
            cursor.iterator_refcount += 1
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
        Truncates the linked_list at the current node, discarding all data in subsequent nodes.

        If the current node is a data node (not a special node), it will become the last data
        node in the list.
        """
        cursor = self._cursor
        t = cursor.linked_list
        tail = t._tail

        if cursor == tail:
            return

        previous = cursor
        cursor = cursor.next

        while cursor != tail:
            next = cursor.next
            cursor.value = None
            if cursor.iterator_refcount:
                previous.next = cursor
                cursor.previous = previous
                previous = cursor
            else:
                cursor.previous = cursor.next = None
            cursor = next
        tail.previous = previous
        previous.next = tail

    def rtruncate(self):
        """
        Reverse-truncates the linked_list at the current node, discarding all data in previous nodes.

        If the current node is a data node (not a special node), it will become the first data
        node in the list.
        """
        cursor = self._cursor
        t = cursor.linked_list
        head = t._head

        if cursor == head:
            return

        next = cursor
        cursor = cursor.previous

        while cursor != head:
            previous = cursor.previous
            cursor.value = None
            if cursor.iterator_refcount:
                next.previous = cursor
                cursor.next = next
                next = cursor
            else:
                cursor.previous = cursor.next = None
            cursor = previous
        head.next = next
        next.previous = head


    def cut(self, end=None):
        """
        Bisects the list at the current node.  Returns the new list.

        Creates a new linked_list, and moves the node pointed to by this iterator
        and all subsequent nodes (including "tail") to the new linked_list.
        All iterators pointing at nodes moved to the new list continue to point
        to those nodes, meaning that they also move to the new list.

        The current node becomes the first node after 'head' of this new linked_list;
        the previous node becomes the last node before 'tail' of the existing linked_list.
        """
        return self._cursor.linked_list.cut(self, end)


    def rcut(self):
        """
        Bisects the list at the current node.  Returns the new list.

        Creates a new linked_list, and moves the node pointed to by this iterator
        and all previous nodes (including "head") to the new linked_list.
        All iterators pointing at nodes moved to the new list continue to point
        to those nodes, meaning that they also move to the new list.

        The current node becomes the last node before 'tail' of this new linked_list;
        the next node becomes the first node after 'head' of the existing linked_list.
        """
        return self._cursor.linked_list.cut(start, self)

    def splice(self, other):
        self._cursor._linked_list.splice(other, self)



@export
class linked_list_iterator(linked_list_base_iterator):
    def __reversed__(self):
        return linked_list_reverse_iterator(self._cursor)



@export
class linked_list_reverse_iterator(linked_list_base_iterator):
    def __reversed__(self):
        return linked_list_iterator(self._cursor)

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

    def count(self, value):
        return super().rcount(value)

    def rcount(self, value):
        return super().count(value)

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

    def truncate(self):
        return super().rtruncate()

    def rtruncate(self):
        return super().truncate()

    def __len__(self):
        length = 0
        cursor = self._cursor
        while cursor is not None:
            if not cursor.special:
                length += 1
            cursor = cursor.previous



del export
