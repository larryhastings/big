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

#
# big.tokens is designed to be safe for "from big.tokens import *"
#


# Note to self, since Python doesn't bother to document this
# except as a comment in Lib/tokenize.py :
#
# token[0] = token type (a la token.py, TOKEN_NL TOKEN_OP etc)
# token[1] = string (value of token, '\n' '=' etc)
# token[2] = start tuple (row, column)
# token[3] = end tuple (row, column)
# token[4] = line
#
# The values in start and end tuple are both integers.
# The line number is 1-based, the column number is 0-based.
# (The first byte of the file is at start tuple (1, 0).)


import token
import tokenize
from tokenize import TokenInfo
import sys


# define a TOKEN_X for every token.X in any supported version of Python.
# if TOKEN_X isn't defined in the current version of Python, it'll be set to -1.
# this lets you safely write
#     if token[0] == TOKEN_X:
# because token[0] will never be -1.

TOKEN_AMPER = token.AMPER
TOKEN_AMPEREQUAL = token.AMPEREQUAL
TOKEN_AT = token.AT
TOKEN_ATEQUAL = token.ATEQUAL
TOKEN_CIRCUMFLEX = token.CIRCUMFLEX
TOKEN_CIRCUMFLEXEQUAL = token.CIRCUMFLEXEQUAL
TOKEN_COLON = token.COLON
TOKEN_COMMA = token.COMMA
TOKEN_DEDENT = token.DEDENT
TOKEN_DOT = token.DOT
TOKEN_DOUBLESLASH = token.DOUBLESLASH
TOKEN_DOUBLESLASHEQUAL = token.DOUBLESLASHEQUAL
TOKEN_DOUBLESTAR = token.DOUBLESTAR
TOKEN_DOUBLESTAREQUAL = token.DOUBLESTAREQUAL
TOKEN_ELLIPSIS = token.ELLIPSIS
TOKEN_ENDMARKER = token.ENDMARKER
TOKEN_EQEQUAL = token.EQEQUAL
TOKEN_EQUAL = token.EQUAL
TOKEN_ERRORTOKEN = token.ERRORTOKEN
TOKEN_GREATER = token.GREATER
TOKEN_GREATEREQUAL = token.GREATEREQUAL
TOKEN_INDENT = token.INDENT
TOKEN_LBRACE = token.LBRACE
TOKEN_LEFTSHIFT = token.LEFTSHIFT
TOKEN_LEFTSHIFTEQUAL = token.LEFTSHIFTEQUAL
TOKEN_LESS = token.LESS
TOKEN_LESSEQUAL = token.LESSEQUAL
TOKEN_LPAR = token.LPAR
TOKEN_LSQB = token.LSQB
TOKEN_MINEQUAL = token.MINEQUAL
TOKEN_MINUS = token.MINUS
TOKEN_NAME = token.NAME
TOKEN_NEWLINE = token.NEWLINE
TOKEN_NOTEQUAL = token.NOTEQUAL
TOKEN_NUMBER = token.NUMBER
TOKEN_OP = token.OP
TOKEN_PERCENT = token.PERCENT
TOKEN_PERCENTEQUAL = token.PERCENTEQUAL
TOKEN_PLUS = token.PLUS
TOKEN_PLUSEQUAL = token.PLUSEQUAL
TOKEN_RARROW = token.RARROW
TOKEN_RBRACE = token.RBRACE
TOKEN_RIGHTSHIFT = token.RIGHTSHIFT
TOKEN_RIGHTSHIFTEQUAL = token.RIGHTSHIFTEQUAL
TOKEN_RPAR = token.RPAR
TOKEN_RSQB = token.RSQB
TOKEN_SEMI = token.SEMI
TOKEN_SLASH = token.SLASH
TOKEN_SLASHEQUAL = token.SLASHEQUAL
TOKEN_STAR = token.STAR
TOKEN_STAREQUAL = token.STAREQUAL
TOKEN_STRING = token.STRING
TOKEN_TILDE = token.TILDE
TOKEN_VBAR = token.VBAR
TOKEN_VBAREQUAL = token.VBAREQUAL

TOKEN_N_TOKENS = token.N_TOKENS


# present in 3.6, removed in 3.7, restored in 3.8
try: # pragma: nocover
    TOKEN_AWAIT = token.AWAIT
    TOKEN_ASYNC = token.ASYNC
except AttributeError: # pragma: nocover
    TOKEN_AWAIT = -1
    TOKEN_ASYNC = -1

# these three are defined in 3.6, but in the "tokenize" module
# instead of the "token" module
assert sys.version_info.major >= 3
if sys.version_info.major == 3: # pragma: nocover
    assert sys.version_info.minor >= 6

if (sys.version_info.major == 3) and (sys.version_info.minor == 6): # pragma: nocover
    _ = tokenize
else: # pragma: nocover
    _ = token

TOKEN_COMMENT  = _.COMMENT
TOKEN_NL       = _.NL
TOKEN_ENCODING = _.ENCODING


# new in 3.8
try: # pragma: nocover
    TOKEN_COLONEQUAL = token.COLONEQUAL
    TOKEN_TYPE_IGNORE = token.TYPE_IGNORE
    TOKEN_TYPE_COMMENT = token.TYPE_COMMENT
except AttributeError: # pragma: nocover
    TOKEN_COLONEQUAL = -1
    TOKEN_TYPE_IGNORE = -1
    TOKEN_TYPE_COMMENT = -1


# new in 3.10
try: # pragma: nocover
    TOKEN_SOFT_KEYWORD = token.SOFT_KEYWORD
except AttributeError: # pragma: nocover
    TOKEN_SOFT_KEYWORD = -1


# new in 3.12
try: # pragma: nocover
    TOKEN_EXCLAMATION = token.EXCLAMATION
    TOKEN_FSTRING_START = token.FSTRING_START
    TOKEN_FSTRING_MIDDLE = token.FSTRING_MIDDLE
    TOKEN_FSTRING_END = token.FSTRING_END
except AttributeError: # pragma: nocover
    TOKEN_EXCLAMATION = -1
    TOKEN_FSTRING_START = -1
    TOKEN_FSTRING_MIDDLE = -1
    TOKEN_FSTRING_END = -1


# new in 3.14
try: # pragma: nocover
    TOKEN_TSTRING_START = token.TSTRING_START
    TOKEN_TSTRING_MIDDLE = token.TSTRING_MIDDLE
    TOKEN_TSTRING_END = token.TSTRING_END
except AttributeError: # pragma: nocover
    TOKEN_TSTRING_START = -1
    TOKEN_TSTRING_MIDDLE = -1
    TOKEN_TSTRING_END = -1

__all__ = [name for name in globals() if name.startswith('TOKEN_')]

def export(fn):
    __all__.append(fn.__name__)
    return fn


if sys.version_info.major == 3: # pragma: nocover
    # In CPython 3.11 and before, the tokenizer
    # only recognizes \r, \n, and \r\n as linebreaks.
    # The new tokenizer that shipped in CPython 3.12
    # properly recognizes all linebreak charactres.
    _use_splitlines_for_tokenizer = sys.version_info.minor >= 12
else: # pragma: nocover
    # This is for hypothetical Python 4.0 and beyond.
    # (big doesn't support Python 1 or Python 2.)
    _use_splitlines_for_tokenizer = True

# _re_tokenizer_splitlines is only used for Python 3.11 and before.
# but we always create it anyway, for the sake of testing.
from big.text import Pattern
_re_tokenizer_splitlines = Pattern("((?:\r\n)|\r|\n)").split


@export
def generate_tokens(s):
    line_number_to_line = {}
    lines_read = 0
    lines_tokenized = 0
    last_line = None
    TokenInfo = tokenize.TokenInfo

    if _use_splitlines_for_tokenizer:
        lines = s.splitlines(True)
        lines.reverse()
    else:
        lines = _re_tokenizer_splitlines(s)
        lines.reverse()
        joined_lines = []
        while lines:
            if len(lines) > 2:
                text = lines.pop()
                nl = lines.pop()
                joined_lines.append(text + nl)
                continue
            joined_lines.extend(lines)
            break
        joined_lines.reverse()
        lines = joined_lines

    def readline():
        nonlocal lines_read
        nonlocal last_line
        if lines:
            line = lines.pop()
        else:
            length = len(s)
            line = s[length:]
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
