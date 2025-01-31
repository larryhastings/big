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


from .text import linebreaks, multipartition, multisplit
from bisect import bisect_right
import re
import tokenize

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

# _re_linebreaks_keepends = '(' + _re_linebreaks + ')'
# _re_linebreaks_splitlines = re.compile(_re_linebreaks_keepends).split

@export
class String(str):
    "String(str, *, source=None, offset=0, line_number=1, column_number=1, first_line_number=1, first_column_number=1) -> String\nCreates a new String object.  String is a subclass of str that maintains line, column, and offset information."

    __slots__ = ('_source', '_offset', '_line_number', '_column_number', '_first_line_number', '_first_column_number', '_linebreak_offsets')

    def __new__(cls, s, *, source=None, offset=0, line_number=1, column_number=1, first_line_number=1, first_column_number=1):
        if isinstance(s, String):
            return s
        if not isinstance(s, str):
            raise TypeError("String: s must be a str or String object")

        if source is None:
            source = s
        if not isinstance(source, str):
            raise TypeError("String: source must be a str or String object, or None")

        ex = None

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

        if line_number < first_line_number:
            raise ValueError("String: line_number can't be less than first_line_number")

        if not isinstance(first_column_number, int):
            ex = TypeError
        elif first_column_number < 0:
            ex = ValueError
        if ex:
            raise ex("String: first_column_number must be an int >= 0")

        if column_number < first_column_number:
            raise ValueError("String: column_number can't be less than first_column_number")

        self = super().__new__(cls, s)
        self._source = source
        self._offset = offset
        self._line_number = line_number
        self._column_number = column_number
        self._first_line_number = first_line_number
        self._first_column_number = first_column_number
        self._linebreak_offsets = None

        return self

    # OK?
    # comparisons behave like str for the purposes of comparison
    # if l is a String, l == str(l), l < str(l) + 'x', l + 'x' > str(l), etc

    @property
    def source(self):
        return self._source

    @property
    def line_number(self):
        return self._line_number

    @property
    def column_number(self):
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

    def _compute_linebreak_offsets(self):
        # self._linebreak_offsets[line_number_offset] is the offset of the first character of the line after
        # self.line_number + line_number_offset
        # e.g. "abcde\nfghij"
        # self._linebreak_offsets = (6,)
        self._linebreak_offsets = offsets = tuple(match.end() for match in _re_linebreaks_finditer(str(self)))
        if 0:
            print()
            print(repr(str(self)))
            print(list(_re_linebreaks_finditer(str(self))))
            print(offsets)
            print()
        return offsets

    def is_followed_by(self, other):
        if not isinstance(other, String):
            return False

        if self.source != other.source:
            return False

        return self.offset + len(self) == other.offset

    def __add__(self, other):
        if not (isinstance(other, String) and self.is_followed_by(other)):
            return str(self) + other

        if not other:
            return self
        if not self:
            return other

        s = str(self) + str(other)
        result = self.__class__(s,
            offset = self._offset,
            source = self._source,
            line_number = self._line_number,
            column_number = self._column_number,
            first_line_number = self._first_line_number,
            first_column_number = self._first_column_number,
            )
        return result

    # We don't need to implement __radd__, we can just inherit the str one.
    # def __radd__(self, other):
    #     # Assertion 1: self is a String object.  (Pretty safe assertion.)
    #     # Assertion 2: Python must already have called other.__add__(self).
    #     #     (Python doesn't call __radd__ unless __add__ returns NotImplemented.)
    #     # Assertion 3: If self is a String, and other is a String, then
    #     #     we wouldn't have gotten here, because other.__add__ would have
    #     #     happily handled adding us together already.
    #     # Therefore: other is not a String, QED.
    #     assert not isinstance(other, String)
    #     if not (isinstance(other, String) and other.is_followed_by(self)):
    #         return other + str(self)
    #     return other.__add__(self)

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
            # indexing raises an exception if the index is out of range.
            if index < 0:
                index += length

        line_number = self._line_number
        column_number = self._column_number
        first_column_number = self._first_column_number

        linebreak_offsets = self._linebreak_offsets
        if linebreak_offsets is None:
            linebreak_offsets = self._compute_linebreak_offsets()

        if self._linebreak_offsets:
            linebreak_index = bisect_right(linebreak_offsets, index)
            new_line_number = self._line_number + linebreak_index
            if line_number == new_line_number:
                column_number += index
            else:
                line_number = new_line_number
                # either 0 or the offset of the previous line
                line_start_index = linebreak_index and linebreak_offsets[linebreak_index - 1]
                column_number = first_column_number + (index - line_start_index)
        else:
            column_number += index

        o = self.__class__(result,
            offset=self._offset + index,
            source=self._source,
            line_number=line_number,
            column_number=column_number,
            first_line_number=self._first_line_number,
            first_column_number=first_column_number)
        return o

    # this is all we need to implement to support pickle!
    def __getnewargs_ex__(self):
        return (
            (str(self),),
            {
                'source': self._source,
                'offset': self._offset,
                'line_number': self._line_number,
                'column_number': self._column_number,
                'first_line_number': self._first_line_number,
                'first_column_number': self._first_column_number,
            },
            )

    def __iter__(self):
        "also computes linebreak offsets if they haven't been cached yet"
        klass = self.__class__
        source = self._source
        line_number = self._line_number
        column_number = self._column_number
        offset = self._offset
        first_line_number = self._first_line_number
        first_column_number = self._first_column_number
        compute_linebreak_offsets = self._linebreak_offsets is None
        if compute_linebreak_offsets:
            linebreak_offsets = []

        waiting = None
        for s in str(self):
            if waiting:
                is_crlf = (waiting == '\r') and (s == '\n')

                o = klass(waiting,
                    source=source,
                    offset=offset,
                    line_number=line_number,
                    column_number=column_number,
                    first_line_number=first_line_number,
                    first_column_number=first_column_number,
                    )
                yield o

                offset += 1

                if is_crlf:
                    # advance normally for waiting
                    column_number += 1
                else:
                    # start a new line for waiting
                    if compute_linebreak_offsets:
                        linebreak_offsets.append(offset)
                    line_number += 1
                    column_number = first_column_number

                o = klass(s,
                    source=source,
                    offset=offset,
                    line_number=line_number,
                    column_number=column_number,
                    first_line_number=first_line_number,
                    first_column_number=first_column_number,
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
                    column_number += 1

                waiting = None
            elif s in linebreaks:
                waiting = s
            else:
                o = klass(s,
                    source=source,
                    offset=offset,
                    line_number=line_number,
                    column_number=column_number,
                    first_line_number=first_line_number,
                    first_column_number=first_column_number,
                    )
                yield o
                offset += 1
                column_number += 1

        if compute_linebreak_offsets:
            if waiting:
                # last character is a linebreak, add that offset
                linebreak_offsets.append(offset + 1)
            self._linebreak_offsets = tuple(linebreak_offsets)


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
        # print(f"_split({repr(str(self))}, {sep=}, {maxsplit=}, {reverse=})")
        klass = self.__class__
        source = self._source
        offset = self._offset
        line_number = self._line_number
        column_number = self._column_number
        first_line_number = self._first_line_number
        first_column_number = self._first_column_number

        # for now, just worry about correctness.
        # we can make this *fast* later.
        # (that said, this seems like it's pretty good.)
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
        if not self:
            return String.cat(iterable)
        return str(self).join(iterable)

    def __repr__(self):
        extras = []
        append = extras.append
        if self._source != None:
            s = self._source
            if len(s) > 20:
                s = s[:17] + "..."
            append(f"source={s!r}")
        if self._offset:
            append(f"offset={self._offset}")
        append(f"line_number={self._line_number}")
        append(f"column_number={self._column_number}")
        if self._first_line_number != 1:
            append(f"first_line_number={self._first_line_number}")
        if self._first_column_number != 1:
            append(f"first_column_number={self._first_column_number}")

        s = ", ".join(extras)

        return f"String({repr(str(self))}, {s})"

    # if 1:
    #     def print_linebreak_offsets(self):
    #         start = 0
    #         print(repr(str(self)))
    #         print("    (")
    #         if self._linebreak_offsets is None:
    #             self._compute_linebreak_offsets()
    #         if self._linebreak_offsets:
    #             for i, offset in enumerate(self._linebreak_offsets):
    #                 end = offset
    #                 print(f"    [{i:3}] {offset:3} {str(self)[start:end]!r}")
    #                 start = end
    #         print("    )")

    ##
    ## support all modern methods
    ##

    ## 3.6 lacked isascii and removeprefix
    if not hasattr(str, 'isascii'):
        def isascii(self):
            for c in self:
                if ord(c) > 127:
                    return False
            return True

    if not hasattr(str, 'removeprefix'):
        def removeprefix(self, prefix):
            if not self.startswith(prefix):
                return self
            return self[len(prefix):]

    ##
    ## extensions
    ##

    def bisect(self, index):
        return self[:index], self[index:]

    @staticmethod
    def cat(strings):
        if not strings:
            return ''

        first = strings[0]
        if len(strings) == 1:
            return first

        s = "".join(strings)

        first_time = True
        for l in strings:
            if not isinstance(l, String):
                return s
            if first_time:
                first_time = False
            else:
                if not previous.is_followed_by(l):
                    return s
            previous = l

        o = String(s,
            source=first._source,
            offset=first._offset,
            line_number=first._line_number,
            column_number=first._column_number,
            first_line_number=first._first_line_number,
            first_column_number=first._first_column_number,
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
        line_number_to_line = {}
        lines_read = 0
        lines_tokenized = 0
        last_line = None
        TokenInfo = tokenize.TokenInfo

        lines = self.splitlines(True)
        lines.reverse()

        def readline():
            nonlocal lines_read
            nonlocal last_line
            if lines:
                line = lines.pop()
            else:
                length = len(self)
                line = self[length:]
            lines_read += 1
            line_number_to_line[lines_read] = line
            last_line = line
            return line

        for t in tokenize.generate_tokens(readline):
            # token[0] = token type (a la token.py, TOKEN_NL TOKEN_OP etc)
            # token[1] = string (value of token, '\n' '=' etc)
            # token[2] = start tuple (row, column)
            # token[3] = end tuple (row, column)
            # token[4] = line

            # if the token spans multiple lines, both string and line will contain \n

            start_line, start_column = t[2]
            end_line, end_column = t[3]
            while lines_tokenized < start_line:
                line_number_to_line.pop(lines_tokenized, None)
                lines_tokenized += 1
            line = line_number_to_line[start_line]
            if start_line == end_line:
                string = line[start_column:end_column]
            else:
                string_buffer = []
                string_append = string_buffer.append
                line_buffer = []
                line_append = line_buffer.append
                string_append(line[start_column:])
                line_append(line)
                for i in range(start_line + 1, end_line):
                    line = line_number_to_line[i]
                    string_append(line)
                    line_append(line)
                line = line_number_to_line[end_line]
                string_append(line[:end_column])
                line_append(line)

                length = len(line)
                empty = line[length:]
                string = empty.join(string_buffer)
                line = empty.join(line_buffer)

            yield TokenInfo(t[0], string, t[2], t[3], line)



del export