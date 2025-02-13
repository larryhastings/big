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

import bigtestlib
big_dir = bigtestlib.preload_local_big()


import big.all as big
from big.tokens import aggregate_delimiter_tokens, generate_tokens
import unittest


class BigTokenTests(unittest.TestCase):

    maxDiff = 2**32

    def test_definitions(self):
        for id in """
            TOKEN_AMPER
            TOKEN_AMPEREQUAL
            TOKEN_ASYNC
            TOKEN_AT
            TOKEN_ATEQUAL
            TOKEN_AWAIT
            TOKEN_CIRCUMFLEX
            TOKEN_CIRCUMFLEXEQUAL
            TOKEN_COLON
            TOKEN_COLONEQUAL
            TOKEN_COMMA
            TOKEN_COMMENT
            TOKEN_DEDENT
            TOKEN_DOT
            TOKEN_DOUBLESLASH
            TOKEN_DOUBLESLASHEQUAL
            TOKEN_DOUBLESTAR
            TOKEN_DOUBLESTAREQUAL
            TOKEN_ELLIPSIS
            TOKEN_ENCODING
            TOKEN_ENDMARKER
            TOKEN_EQEQUAL
            TOKEN_EQUAL
            TOKEN_ERRORTOKEN
            TOKEN_EXCLAMATION
            TOKEN_FSTRING_END
            TOKEN_FSTRING_MIDDLE
            TOKEN_FSTRING_START
            TOKEN_GREATER
            TOKEN_GREATEREQUAL
            TOKEN_INDENT
            TOKEN_LBRACE
            TOKEN_LEFTSHIFT
            TOKEN_LEFTSHIFTEQUAL
            TOKEN_LESS
            TOKEN_LESSEQUAL
            TOKEN_LPAR
            TOKEN_LSQB
            TOKEN_MINEQUAL
            TOKEN_MINUS
            TOKEN_N_TOKENS
            TOKEN_NAME
            TOKEN_NEWLINE
            TOKEN_NL
            TOKEN_NOTEQUAL
            TOKEN_NUMBER
            TOKEN_OP
            TOKEN_PERCENT
            TOKEN_PERCENTEQUAL
            TOKEN_PLUS
            TOKEN_PLUSEQUAL
            TOKEN_RARROW
            TOKEN_RBRACE
            TOKEN_RIGHTSHIFT
            TOKEN_RIGHTSHIFTEQUAL
            TOKEN_RPAR
            TOKEN_RSQB
            TOKEN_SEMI
            TOKEN_SLASH
            TOKEN_SLASHEQUAL
            TOKEN_SOFT_KEYWORD
            TOKEN_STAR
            TOKEN_STAREQUAL
            TOKEN_STRING
            TOKEN_TILDE
            TOKEN_TYPE_COMMENT
            TOKEN_TYPE_IGNORE
            TOKEN_VBAR
            TOKEN_VBAREQUAL
            """.strip().split():
            with self.subTest(id):
                self.assertTrue(hasattr(big.tokens, id))

    def test_functions(self):
        text = """
def foo(a, b):
    return [1, 2, 3]
""".strip()
        tokens = list(generate_tokens(text))
        strings = [t[1] for t in tokens if t[1]]
        self.assertEqual(strings,
            [
            'def', 'foo', '(', 'a', ',', 'b', ')', ':', '\n',
            '    ', 'return', '[', '1', ',', '2', ',', '3', ']',
            ]
            )

        tokens2 = list(aggregate_delimiter_tokens(tokens))
        tup = [t[1] for t in tokens2[2]]
        self.assertEqual(tup, ['(', 'a', ',', 'b', ')'])
        lst = [t[1] for t in tokens2[7]]
        self.assertEqual(lst, ['[', '1', ',', '2', ',', '3', ']'])

        text = """
def foo(a, b]:
    return mismatched
"""
        tokens = list(generate_tokens(text))
        with self.assertRaises(ValueError):
            list(aggregate_delimiter_tokens(tokens))


def run_tests():
    bigtestlib.run(name="big.tokens", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
