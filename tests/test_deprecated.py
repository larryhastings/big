#!/usr/bin/env python3

_license = """
big
Copyright 2022-2024 Larry Hastings
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
bigtestlib.preload_local_big()

import big.all as big
import unittest

class BigDeprecatedTests(unittest.TestCase):

    def test_old_separators(self):
        # now test the deprecated utf-8 variants!
        # they should match... python str, sigh.
        # (principle of least surprise.)
        utf8_whitespace = big.encode_strings(big.str_whitespace, 'utf-8')
        self.assertEqual(set(big.deprecated.utf8_whitespace), set(utf8_whitespace))
        utf8_whitespace_without_dos = big.encode_strings(big.str_whitespace_without_crlf, 'utf-8')
        self.assertEqual(set(big.deprecated.utf8_whitespace_without_dos), set(utf8_whitespace_without_dos))
        utf8_newlines = big.encode_strings(big.str_linebreaks, 'utf-8')
        self.assertEqual(set(big.deprecated.utf8_newlines), set(utf8_newlines))
        utf8_newlines_without_dos = big.encode_strings(big.str_linebreaks_without_crlf, 'utf-8')
        self.assertEqual(set(big.deprecated.utf8_newlines_without_dos), set(utf8_newlines_without_dos))

        # test that the compatibility layer for the old "newlines" names is correct
        self.assertEqual(big.deprecated.newlines, big.str_linebreaks)
        self.assertEqual(big.deprecated.newlines_without_dos, big.str_linebreaks_without_crlf)
        self.assertEqual(big.deprecated.ascii_newlines, big.bytes_linebreaks)
        self.assertEqual(big.deprecated.ascii_newlines_without_dos, big.bytes_linebreaks_without_crlf)
        self.assertEqual(big.deprecated.utf8_newlines, big.encode_strings(big.linebreaks, 'utf-8'))
        self.assertEqual(big.deprecated.utf8_newlines_without_dos, big.encode_strings(big.linebreaks_without_crlf, 'utf-8'))


    def test_split_quoted_strings(self):
        def test(s, expected, **kwargs):
            got = list(big.deprecated.split_quoted_strings(s, **kwargs))
            self.assertEqual(got, expected)

            got = list(big.deprecated.split_quoted_strings(s.encode('ascii'), **kwargs))
            self.assertEqual(got, [(b, s.encode('ascii')) for b, s in expected])

        test("""hey there "this is quoted" an empty quote: '' this is not quoted 'this is more quoted' "here's quoting a quote mark: \\" wow!" this is working!""",
            [
                (False, 'hey there '),
                (True, '"this is quoted"'),
                (False, ' an empty quote: '),
                (True, "''"),
                (False, ' this is not quoted '),
                (True, "'this is more quoted'"),
                (False, ' '),
                (True, '"here\'s quoting a quote mark: \\" wow!"'),
                (False, ' this is working!'),
            ])

        test('''here is triple quoted: """i am triple quoted.""" wow!  again: """triple quoted here. "quotes in quotes" empty: "" done.""" phew!''',
            [
                (False, 'here is triple quoted: '),
                (True, '"""i am triple quoted."""'),
                (False, ' wow!  again: '),
                (True, '"""triple quoted here. "quotes in quotes" empty: "" done."""'),
                (False, ' phew!'),
            ])

        test('''test turning off quoted strings.  """howdy doodles""" it kinda works anyway!''',
            [
                (False, 'test turning off quoted strings.  '),
                (True, '""'),
                (True, '"howdy doodles"'),
                (True, '""'),
                (False, ' it kinda works anyway!'),
            ],
            triple_quotes=False)

    def test_parse_delimiters(self):

        self.maxDiff = 2**32

        def test(s, expected, *, delimiters=None):
            empty = ''
            for i in range(2):
                got = tuple(big.deprecated.parse_delimiters(s, delimiters=delimiters))

                flattened = []
                for t in got:
                    flattened.extend(t)
                s2 = empty.join(flattened)
                self.assertEqual(s, s2)

                self.assertEqual(expected, got)

                if not i:
                    s = big.encode_strings(s)
                    expected = big.encode_strings(expected)
                    empty = b''

        test('a[x] = foo("howdy (folks)\\n", {1:2, 3:4})',
            (
                ('a',                '[',  ''),
                ('x',                 '', ']'),
                (' = foo',           '(',  ''),
                ('',                 '"',  ''),
                ('howdy (folks)\\n',  '', '"'),
                (', ',               '{',  ''),
                ('1:2, 3:4',          '', '}'),
                ('',                  '', ')'),
            ),
            )

        test('a[[[z]]]{{{{q}}}}[{[{[{[{z}]}]}]}]!',
            (
                ('a', '[',  ''),
                ('',  '[',  ''),
                ('',  '[',  ''),
                ('z',  '', ']'),
                ('',   '', ']'),
                ('',   '', ']'),
                ('',  '{',  ''),
                ('',  '{',  ''),
                ('',  '{',  ''),
                ('',  '{',  ''),
                ('q',  '', '}'),
                ('',   '', '}'),
                ('',   '', '}'),
                ('',   '', '}'),
                ('',  '[',  ''),
                ('',  '{',  ''),
                ('',  '[',  ''),
                ('',  '{',  ''),
                ('',  '[',  ''),
                ('',  '{',  ''),
                ('',  '[',  ''),
                ('',  '{',  ''),
                ('z',  '', '}'),
                ('',   '', ']'),
                ('',   '', '}'),
                ('',   '', ']'),
                ('',   '', '}'),
                ('',   '', ']'),
                ('',   '', '}'),
                ('',   '', ']'),
                ('!',  '',  ''),
            ),
            )

        with self.assertRaises(ValueError):
            test('a[3)', None)
        with self.assertRaises(ValueError):
            test('a{3]', None)
        with self.assertRaises(ValueError):
            test('a(3}', None)

        with self.assertRaises(ValueError):
            test('delimiters is empty', None, delimiters=[])
        with self.assertRaises(ValueError):
            test('delimiter is abc (huh!)', None, delimiters=['()', 'abc'])
        with self.assertRaises(TypeError):
            test('delimiters contains 3', None, delimiters=['{}', 3])
        with self.assertRaises(ValueError):
            test('delimiters contains a <backslash>', None, delimiters=['<>', '\\/'])
        with self.assertRaises(ValueError):
            test('delimiters contains <angle> <brackets> <twice>', None, delimiters=['<>', '<>'])

        with self.assertRaises(ValueError):
            test('unclosed_paren(a[3]', None)
        with self.assertRaises(ValueError):
            test('x[3] = unclosed_curly{', None)
        with self.assertRaises(ValueError):
            test('foo(a[1], {a[2]: 33}) = unclosed_square[55', None)
        with self.assertRaises(ValueError):
            test('"unterminated string\\', None)
        with self.assertRaises(ValueError):
            test('open_everything( { a[35 "foo', None)

        D = big.deprecated.Delimiter
        with self.assertRaises(TypeError):
            D('(', b')')
        with self.assertRaises(TypeError):
            D(b'(', ')')


    def test_lines_strip_comments(self):
        self.maxDiff = 2**32
        def test(i, expected):
            # print("I", i)
            got = list(i)
            # print("GOT", got)
            # print(f"{i == got=}")
            # print(f"{got == expected=}")
            # import pprint
            # print("\n\n")
            # pprint.pprint(got)
            # print("\n\n")
            # pprint.pprint(expected)
            # print("\n\n")
            self.assertEqual(got, expected)

        def L(line, line_number, column_number=1, end='\n', final=None, **kwargs):
            if final is None:
                final = line
            if isinstance(end, str) and isinstance(line, bytes):
                end = end.encode('ascii')
            info = big.LineInfo(lines, line + end, line_number, column_number, end=end, **kwargs)
            return (info, final)

        lines = big.lines("""
for x in range(5): # this is a comment
    print("# this is quoted", x)
    print("") # this "comment" is useless
    print(no_comments_or_quotes_on_this_line)
"""[1:])
        test(big.deprecated.lines_strip_comments(lines, ("#", "//")),
            [
                L(line='for x in range(5): # this is a comment', line_number=1, column_number=1, trailing=' # this is a comment', final='for x in range(5):'),
                L(line='    print("# this is quoted", x)', line_number=2, column_number=1),
                L(line='    print("") # this "comment" is useless', line_number=3, column_number=1, trailing=' # this "comment" is useless', final='    print("")'),
                L(line='    print(no_comments_or_quotes_on_this_line)', line_number=4, column_number=1),
                L(line='', line_number=5, column_number=1, end=''),
            ])

        # don't get alarmed!  we intentionally break quote characters in this test.
        lines = big.lines("""
for x in range(5): # this is a comment
    print("# this is quoted", x)
    print("") # this "comment" is useless
    print(no_comments_or_quotes_on_this_line)
"""[1:])
        test(big.deprecated.lines_strip_comments(lines, ("#", "//"), quotes=None),
            [
                L(line='for x in range(5): # this is a comment', line_number=1, column_number=1, trailing=' # this is a comment', final='for x in range(5):'),
                L(line='    print("# this is quoted", x)', line_number=2, column_number=1, trailing='# this is quoted", x)', final='    print("'),
                L(line='    print("") # this "comment" is useless', line_number=3, column_number=1, trailing=' # this "comment" is useless', final='    print("")'),
                L(line='    print(no_comments_or_quotes_on_this_line)', line_number=4, column_number=1),
                L(line='', line_number=5, column_number=1, end=''),
            ])

        with self.assertRaises(ValueError):
            test(big.deprecated.lines_strip_comments(big.lines("a\nb\n"), None), [])

        lines = big.lines(b"a\nb# ignored\n c")
        test(big.deprecated.lines_strip_comments(lines, b'#'),
            [
            L(b'a', 1, ),
            L(b'b# ignored', 2, 1, trailing=b'# ignored', final=b'b'),
            L(b' c', 3, end=b''),
            ]
            )



def run_tests():
    bigtestlib.run(name="big.deprecated", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
