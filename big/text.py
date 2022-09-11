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
import operator
import re
import struct
import sys


__all__ = []

def export(o):
    __all__.append(o.__name__)
    return o


@export
def re_partition(text, pattern, *, flags=0):
    """
    Like str.partition, but pattern is matched as a regular expression.

    text can be a string or a bytes object.

    pattern can be a string, bytes, or an re.Pattern object.

    text and pattern (or pattern.pattern) must be the same type.

    If pattern is found in text, returns a tuple
        (before, match, after)
    where before is the text before the matched text,
    match is the re.Match object resulting from the match, and
    after is the text after the matched text.

    If pattern appears in text multiple times,
    re_partition will match against the first (leftmost)
    appearance.

    If pattern is not found in text, returns a tuple
        (text, None, '')
    where the empty string is str or bytes as appropriate.

    If pattern is a string or bytes, flags is passed in
    as the flags argument to re.compile.
    """
    if not isinstance(pattern, re.Pattern):
        pattern = re.compile(pattern, flags=flags)
    if not (isinstance(text, (str, bytes)) and
        (type(text) == type(pattern.pattern))):
        raise ValueError("text must be str or int, and string used in pattern must be the same type")
    match = pattern.search(text)
    if not match:
        empty = '' if isinstance(text, str) else b''
        return (text, None, empty)
    before, separator, after = text.partition(match.group(0))
    return (before, match, after)


@export
def re_rpartition(text, pattern, *, flags=0):
    """
    Like str.rpartition, but pattern is matched as a regular expression.

    text can be a string or a bytes object.

    pattern can be a string, bytes, or an re.Pattern object.

    text and pattern (or pattern.pattern) must be the same type.

    If pattern is found in text, returns a tuple
        (before, match, after)
    where before is the text before the matched text,
    match is the re.Match object resulting from the match, and
    after is the text after the matched text.

    If pattern appears in text multiple times,
    re_partition will match against the last (rightmost)
    appearance.

    If pattern is not found in text, returns a tuple
        ('', None, text)
    where the empty string is str or bytes as appropriate.

    If pattern is a string, flags is passed in
    as the flags argument to re.compile.
    """
    if not isinstance(pattern, re.Pattern):
        pattern = re.compile(pattern, flags=flags)
    if not (isinstance(text, (str, bytes)) and
        (type(text) == type(pattern.pattern))):
        raise ValueError("text must be str or int, and string used in pattern must be the same type")
    match = None
    for match in pattern.finditer(text):
        pass
    if not match:
        empty = '' if isinstance(text, str) else b''
        return (empty, None, text)
    before, separator, after = text.rpartition(match.group(0))
    return (before, match, after)


@export
def multisplit(text, separators, *, maxsplit=-1):
    """
    Like str.split, but separators is an iterable of separator strings.

    s can be str or bytes.

    separators should be an iterable.  Each element of separators
    should be the same type as s.  If separators is a string or bytes
    object, multisplit behaves as if separators is a tuple containing
    each individual character.

    Returns a list of the substrings split from s.

    maxsplit should be either an integer or None.  If maxsplit is an
    integer greater than -1, multisplit will split s no more than
    maxsplit times.

    Example:
        multisplit('ab:cd,:ef', ':,')
    returns
        ["ab", "cd", "ef"]

    Example:
        multisplit('\tthis is a\n\tbunch of words', (' ', '\t', '\n'))
    would produce the same result as
        '\tthis is a\n\tbunch of words'.split()
    """

    if isinstance(separators, bytes):
        # this tiresome old Python 3 wart.
        # if you index into a bytes string, you get integers, not bytes strings.
        # so if separators is a bytes string, use fast magic gunk to convert it
        # into a tuple of individual bytes strings.
        length = len(separators)
        separators = tuple(struct.unpack(str(length) + 'c', separators))

    try:
        separators[0]
    except TypeError:
        raise TypeError("separators must be iterable")

    if not(isinstance(text, (str, bytes)) and (type(text) == type(separators[0]))):
        raise ValueError("text and separators elements must be the same type, either str or bytes")
    if not (text and separators):
        return [text]

    # candidates is a sorted list of lists.  each sub-list contains:
    #   [ first_appearance_index, negative_separator_length, separator_string, len_separator ]
    # since the lowest appearance is sorted first, you simply split
    # off based on candidates[0], shift all the first_appearance_indexes
    # down by how much you lopped off, recompute the first_appearance_index
    # of candidate[0]'s separator_string, re-sort, and do it again.
    # (you remove a candidate when there are no more appearances in
    # the string--when "".find returns -1.)
    #
    # negative_separator_length is there so that larger separator strings
    # sort first.  if you call
    #         multisplit("xxxABCDxxxx", ("A", "ABCD"))
    # either separator would work, but you want multisplit to use the
    # longer one.
    candidates = []
    for separator in separators:
        index = text.find(separator)
        if index != -1:
            candidates.append([index, -len(separator), separator, len(separator)])

    if not (candidates and maxsplit):
        return [text]
    if len(candidates) == 1:
        return text.split(candidates[0][2])

    candidates.sort()
    segments = []
    empty = '' if isinstance(text, str) else b''

    # edge case: if the string you're splitting
    # *starts* with a separator, the result needs
    # to start with an empty string.
    if not candidates[0][0]:
        segments.append(empty)

    while True:
        assert text
        # print(f"\n{s=}\n{candidates=}\n{splits=}")
        index, _, separator, len_separator = candidates[0]
        segment = text[:index]
        if segment:
            segments.append(segment)
        new_start = index + len_separator
        text = text[new_start:]
        maxsplit -= 1
        if not maxsplit:
            segments.append(text)
            break

        # print(f"{new_start=} new {s=}")
        for candidate in candidates:
            candidate[0] -= new_start
        index = text.find(separator)
        if index < 0:
            # there aren't any more appearances of candidate[0].
            if len(candidates) == 2:
                # once we remove candidate[0],
                # we'll only have one candidate separator left.
                # so just split normally on that separator and exit.
                #
                # note: this is the only way to exit the loop
                # (without maxsplit).
                # we always reach it, because at some point
                # there's only one candidate left.

                # edge case:
                # we're about to call split() using the final
                # separator.  but if the string *starts* with
                # the separator, the array split returns will
                # start with an empty string, which we don't want.
                index, _, separator, len_separator = candidates[1]
                final_segments = text.split(separator)
                if not index:
                    final_segments.pop(0)
                segments.extend(final_segments)
                break
            candidates.pop(0)
        else:
            candidates[0][0] = index
            candidates.sort()

    # print(f"\nfinal {splits=}")
    return segments



_invalid_state = 0
_in_word = 1
_after_whitespace = 2
_after_whitespace_then_apostrophe_or_quote_mark = 3
_after_whitespace_then_D_or_O = 4
_after_whitespace_then_D_or_O_then_apostrophe = 5

@export
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
            'Twas The Night Before christmas
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


@export
def normalize_whitespace(s):
    """
    Returns s, but with every run of consecutive
    whitespace characters turned into a single space.
    Preserves leading and trailing whitespace.

    normalize_whitespace("   a    b   c") returns " a b c".
    """
    if not s:
        return ''
    if not s.strip():
        return ' '
    words = s.split()
    cleaned = " ".join(words)
    del words
    if s[0].isspace():
        cleaned = " " + cleaned
    if s[-1].isspace():
        cleaned = cleaned + " "
    return cleaned


@export
def rstripped_lines(s, *, sep=None):
    """
    Splits s at line boundaries, then "rstrips"
    (strips trailing whitespace) from each line.

    Returns an iterator yielding lines.

    sep specifies an alternate separator string.
    If provided, it should match the type of s.
    """
    if sep is None:
        if isinstance(s, bytes):
            sep = b'\n'
        else:
            sep = '\n'
    for line in s.split(sep):
        yield line.rstrip()


@export
def stripped_lines(s, *, sep=None):
    """
    Splits s at line boundaries, then strips
    whitespace from each line.

    Returns an iterator yielding lines.

    sep specifies an alternate separator string.
    If provided, it should match the type of s.
    """
    if sep is None:
        if isinstance(s, bytes):
            sep = b'\n'
        else:
            sep = '\n'
    for line in s.split(sep):
        yield line.strip()


@export
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



@export
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


@export
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

@export
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

