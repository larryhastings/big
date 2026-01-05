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

import bigtestlib
big_dir = bigtestlib.preload_local_big()


import big.all as big
from big.tokens import generate_tokens
from big.all import string
import unittest
import sys



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
                self.assertIsInstance(getattr(big.tokens, id), int)

    def test_functions(self):
        # white box testing
        saved = big.tokens._use_splitlines_for_tokenizer

        def extract_strings_from_tokens(tokens):
            result = []
            result_append = result.append
            for t in tokens:
                value = t[1]
                result_append(value)
            return result

        for text, token_strings in (
            (
                "def foo(a, b):\n    return [1, 2, 3]",
                [
                'def', 'foo', '(', 'a', ',', 'b', ')', ':', '\n',
                '    ', 'return', '[', '1', ',', '2', ',', '3', ']',
                '', '', '',
                ],
            ),

            (
                "'''\nline 1\nline 2\nline 3\n'''",
                [
                "'''\nline 1\nline 2\nline 3\n'''", '', '',
                ],
            ),

            ):

            # Python 3.6 tokenizer generates an extra NL token at the end
            # of these token streams.  Not present in 3.7+.  So, we just
            # remove one empty-quote from these just-the-strings lists for 3.6.
            remove_nl_token = (sys.version_info.major == 3) and (sys.version_info.minor == 6)
            if remove_nl_token: # pragma: no cover
                token_strings.pop()

            with self.subTest(text):
                for use_splitlines in (False, True):
                    with self.subTest(use_splitlines):
                        big.tokens._use_splitlines_for_tokenizer = use_splitlines
                        tokens = list(generate_tokens(text))
                        got_token_strings = extract_strings_from_tokens(tokens)
                        self.assertEqual(got_token_strings, token_strings)

        big.tokens._use_splitlines_for_tokenizer = saved

        text = string("def foo(a, b):\n")
        expected_token_strings = [text[0:3], text[4:7], text[7:8], text[8:9], text[9:10], text[11:12], text[12:13], text[13:14], text[14:15], text[15:15]]
        tokens = list(generate_tokens(text))
        got_token_strings = extract_strings_from_tokens(tokens)
        self.assertEqual(got_token_strings, expected_token_strings)
        for got, expected in zip(got_token_strings, expected_token_strings):
            with self.subTest(got):
                self.assertIsInstance(got, string)
                self.assertEqual(got.line_number, expected.line_number)
                self.assertEqual(got.column_number, expected.column_number)
                self.assertEqual(got.offset, expected.offset)

def run_tests():
    bigtestlib.run(name="big.tokens", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
