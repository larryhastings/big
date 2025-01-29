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
try:
    TOKEN_AWAIT = token.AWAIT
    TOKEN_ASYNC = token.ASYNC
except AttributeError:
    TOKEN_AWAIT = -1
    TOKEN_ASYNC = -1

# these three are defined in 3.6, but in the "tokenize" module
# instead of the "token" module
assert sys.version_info.major >= 3
if sys.version_info.major == 3:
    assert sys.version_info.minor >= 6

if (sys.version_info.major == 3) and (sys.version_info.minor == 6):
    _ = tokenize
else:
    _ = token

TOKEN_COMMENT  = _.COMMENT
TOKEN_NL       = _.NL
TOKEN_ENCODING = _.ENCODING


# new in 3.8
try:
    TOKEN_COLONEQUAL = token.COLONEQUAL
    TOKEN_TYPE_IGNORE = token.TYPE_IGNORE
    TOKEN_TYPE_COMMENT = token.TYPE_COMMENT
except AttributeError:
    TOKEN_COLONEQUAL = -1
    TOKEN_TYPE_IGNORE = -1
    TOKEN_TYPE_COMMENT = -1


# new in 3.10
try:
    TOKEN_SOFT_KEYWORD = token.SOFT_KEYWORD
except AttributeError:
    TOKEN_SOFT_KEYWORD = -1


# new in 3.12
try:
    TOKEN_EXCLAMATION = token.EXCLAMATION
    TOKEN_FSTRING_START = token.FSTRING_START
    TOKEN_FSTRING_MIDDLE = token.FSTRING_MIDDLE
    TOKEN_FSTRING_END = token.FSTRING_END
except AttributeError:
    TOKEN_EXCLAMATION = -1
    TOKEN_FSTRING_START = -1
    TOKEN_FSTRING_MIDDLE = -1
    TOKEN_FSTRING_END = -1

__all__ = [name for name in globals() if name.isupper()]

def export(fn):
    __all__.append(fn.__name__)
    return fn


@export
def aggregate_delimiter_tokens(tokens):
    """
    Transforms a token stream.  Aggregates a sequence

    If you pass in these tokens:
        [
            'def', 'foo', '(', 'a', ',', 'b', ')', ':',
            'return', '[', '1', ',', '2', ',', '3', ']',
        ]

    You get this back:
        [
            'def', 'foo', ['(', 'a', ',', 'b', ')',], ':',
            'return', [ '[', '1', ',', '2', ',', '3', ']', ],
        ]

    Nested delimiters create nested lists.
    """
    stack = []
    push = stack.append
    pop = stack.pop

    output = []
    append = output.append

    current_close_delimiter = None

    for t in tokens:
        if t[0] == TOKEN_OP:
            s = t[1]
            if s == current_close_delimiter:
                # pop
                append(t)
                output, append, current_close_delimiter = pop()
                continue
            if s in _aggregated_close_delimiters:
                raise ValueError("mismatched close delimiter: expecting {current_close_delimiter!r}, got {s!r}")
            closing_delimiter = _aggregated_delimiters.get(s)
            if closing_delimiter:
                # s is an open delimiter
                # push
                new_output = []
                append(new_output)
                push( (output, append, current_close_delimiter) )
                output = new_output
                append = output.append
                current_close_delimiter = closing_delimiter
                # don't continue! append our token.
        append(t)
    return output



del export