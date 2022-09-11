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

import big
import re
import unittest


def unchanged(o):
    return o

def to_bytes(o): # pragma: no cover
    if isinstance(o, str):
        return o.encode('ascii')
    if isinstance(o, list):
        return [to_bytes(x) for x in o]
    if isinstance(o, tuple):
        return tuple(to_bytes(x) for x in o)
    return o


class BigTextTests(unittest.TestCase):

    def test_re_partition(self):
        def group0(re_partition_result):
            before, match, after = re_partition_result
            if match is not None:
                return (before, match.group(0), after)
            return (before, match, after)

        for c in (unchanged, to_bytes):
            pattern = c("[0-9]+")

            s = c("abc123def456ghi")
            self.assertEqual(group0(big.re_partition(s, pattern)),
                c(("abc", "123", "def456ghi")) )
            self.assertEqual(group0(big.re_rpartition(s, pattern)),
                c(("abc123def", "456", "ghi")) )

            s = c("abc12345def67890ghi")
            self.assertEqual(group0(big.re_partition(s, pattern)),
                c(("abc", "12345", "def67890ghi")) )
            self.assertEqual(group0(big.re_rpartition(s, pattern)),
                c(("abc12345def", "67890", "ghi")) )

            pattern = re.compile(pattern)
            self.assertEqual(group0(big.re_partition(s, pattern)),
                c(("abc", "12345", "def67890ghi")) )
            self.assertEqual(group0(big.re_rpartition(s, pattern)),
                c(("abc12345def", "67890", "ghi")) )

            pattern = c("fa+rk")
            self.assertEqual(group0(big.re_partition(s, pattern)),
                c(("abc12345def67890ghi", None, "")) )
            self.assertEqual(group0(big.re_rpartition(s, pattern)),
                c(("", None, "abc12345def67890ghi")) )

            # test overlapping matches
            pattern = c("thisANDthis")
            s = c("thisANDthisANDthis")
            self.assertEqual(group0(big.re_partition(s, pattern)),
                c(("", "thisANDthis", "ANDthis")) )
            self.assertEqual(group0(big.re_rpartition(s, pattern)),
                c(("thisAND", "thisANDthis", "")) )

            for fn in (big.re_partition, big.re_rpartition):
                s = c("Let's find the number 89 in this string")
                pattern = c(r"number ([0-9]+)")
                result = fn(s, pattern)
                # print(result)
                # print(group0(result))
                self.assertEqual(group0(result), c(("Let's find the ", "number 89", " in this string")))
                match = result[1]
                self.assertEqual(match.group(0), c("number 89"))
                self.assertEqual(match.group(1), c("89"))

        s = "abc123def456ghi"
        pattern = b"[0-9]+"
        with self.assertRaises(ValueError):
            big.re_partition(s, pattern)
        with self.assertRaises(ValueError):
            big.re_rpartition(s, pattern)
        pattern = re.compile(pattern)
        with self.assertRaises(ValueError):
            big.re_partition(s, pattern)
        with self.assertRaises(ValueError):
            big.re_rpartition(s, pattern)

    def test_multisplit(self):
        for c in (unchanged, to_bytes):
            self.assertEqual(big.multisplit(c(''), c('abcde')), c(['']))
            self.assertEqual(big.multisplit(c('abcde'), c('fghij')), c(['abcde']))
            self.assertEqual(big.multisplit(c('abcde'), c('fghijc')), c(['ab', 'de']))
            self.assertEqual(big.multisplit(c('xaxbxcxdxex'), c('abcde')), c(['x', 'x', 'x', 'x', 'x', 'x']))

            self.assertEqual(big.multisplit(c('ab:cd,ef'), c(':,')), c(["ab", "cd", "ef"]))
            self.assertEqual(big.multisplit(c('ab:cd,ef:'), c(':,')), c(["ab", "cd", "ef", '']))
            self.assertEqual(big.multisplit(c(',ab:cd,ef:'), c(':,')), c(['', "ab", "cd", "ef", '']))
            self.assertEqual(big.multisplit(c(':ab:cd,ef'), c(':,')), c(['', "ab", "cd", "ef"]))
            self.assertEqual(big.multisplit(c('WWabXXcdYYabZZ'), c(('ab', 'cd'))), c(['WW', 'XX', 'YY', 'ZZ']))
            self.assertEqual(big.multisplit(c('WWabXXcdYYabZZab'), c(('ab', 'cd'))), c(['WW', 'XX', 'YY', 'ZZ', '']))
            self.assertEqual(big.multisplit(c('abWWabXXcdYYabZZ'), c(('ab', 'cd'))), c(['', 'WW', 'XX', 'YY', 'ZZ']))
            self.assertEqual(big.multisplit(c('WWabXXcdYYabZZcd'), c(('ab', 'cd'))), c(['WW', 'XX', 'YY', 'ZZ', '']))
            self.assertEqual(big.multisplit(c('XXabcdYY'), c(('a', 'abcd'))), c(['XX', 'YY']))
            self.assertEqual(big.multisplit(c('XXabcdabcdYY'), c(('ab', 'cd'))), c(['XX', 'YY']))
            self.assertEqual(big.multisplit(c('abcdXXabcdabcdYYabcd'), c(('ab', 'cd'))), c(['', 'XX', 'YY', '']))

            self.assertEqual(big.multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=0), c(['xaxbxcxdxex']))
            self.assertEqual(big.multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=1), c(['x', 'xbxcxdxex']))
            self.assertEqual(big.multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=2), c(['x', 'x', 'xcxdxex']))
            self.assertEqual(big.multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=3), c(['x', 'x', 'x', 'xdxex']))
            self.assertEqual(big.multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=4), c(['x', 'x', 'x', 'x', 'xex']))
            self.assertEqual(big.multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=5), c(['x', 'x', 'x', 'x', 'x', 'x']))
            self.assertEqual(big.multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=6), c(['x', 'x', 'x', 'x', 'x', 'x']))

        with self.assertRaises(TypeError):
            big.multisplit('s', None)
        with self.assertRaises(ValueError):
            big.multisplit('s', b'abc')

    def test_wrap_words(self):
        def test(words, expected, margin=79):
            got = big.wrap_words(words, margin)
            self.assertEqual(got, expected)

        test(
            "hello there. how are you? i am fine! so there's that.".split(),
            "hello there.  how are you?  i am fine!  so there's that.")
        test(
            "hello there. how are you? i am fine! so there's that.".split(),
            "hello there.  how\nare you?  i am fine!\nso there's that.",
            20)
        test(
            ["these are all long lines that must be by themselves.",
            "   more stuff goes here and stuff.",
            " know what i'm talkin' about?  yeah, that's what i'm talking about."],
            "these are all long lines that must be by themselves.\n   more stuff goes here and stuff.\n know what i'm talkin' about?  yeah, that's what i'm talking about.",
            20)
        test(
            ["a", 'b', '\n\n', 'c', 'd', 'e.'],
            "a b\n\nc d\ne.",
            4)

    def test_split_text_with_code(self):
        def test(s, expected, **kwargs):
            got = big.split_text_with_code(s, **kwargs)
            if 0:
                print()
                print("s:")
                print("   ", repr(s))
                print("got:")
                print("   ", repr(got))
                print("expected:")
                print("   ", repr(expected))
                print()
            self.assertEqual(expected, got)
        def xtest(*a, **kw): pass

        test(
            "hey there party people",
            ['hey', 'there', 'party', 'people'],
            )
        test(
            "hey there party people\n\na second paragraph!\n\nand a third.",
            ['hey', 'there', 'party', 'people', '\n\n', 'a', 'second', 'paragraph!', '\n\n', 'and', 'a', 'third.'],
            )
        test(
            "hey there party people\n\nhere, we have a second paragraph.\nwith an internal newline.\n\n    for i in code:\n        print(i)\n\nmore text here? sure seems like it.",
            ['hey', 'there', 'party', 'people', '\n\n', 'here,', 'we', 'have', 'a', 'second', 'paragraph.', 'with', 'an', 'internal', 'newline.', '\n\n', '    for i in code:', '\n', '        print(i)', '\n\n', 'more', 'text', 'here?', 'sure', 'seems', 'like', 'it.']
            )
        test(
            "text paragraphs separated by infinite newlines get collapsed to just two newlines.\n\n\n\n\nsee? just two.\n\n\n\n\n\n\n\n\nqed!",
            ['text', 'paragraphs', 'separated', 'by', 'infinite', 'newlines', 'get', 'collapsed', 'to', 'just', 'two', 'newlines.', '\n\n', 'see?', 'just', 'two.', '\n\n', 'qed!']
            )
        test(
            "here's some code with a tab.\n\tfor x in range(3):\n\t\tprint(x)\nwelp! that's it for the code.",
            ["here's", 'some', 'code', 'with', 'a', 'tab.', '\n\n', '        for x in range(3):', '\n', '                print(x)', '\n\n', 'welp!', "that's", 'it', 'for', 'the', 'code.']
            )
        test(
            "here's some code with a tab.\n\tfor x in range(3):\n\t\tprint(x)\nwelp! that's it for the code.",
            ["here's", 'some', 'code', 'with', 'a', 'tab.', '\n\n', '\tfor x in range(3):', '\n', '\t\tprint(x)', '\n\n', 'welp!', "that's", 'it', 'for', 'the', 'code.'],
            convert_tabs_to_spaces=False)
        test(
            "this is text, but next is a code paragraph with a lot of internal newlines and stuff.\n\tfor x in range(3):\n\n   \n\n    \t\n\t\tprint(x)\n\t\t\n\n\t\tprint(x*x)\nwelp! that's it for the code.",
            ['this', 'is', 'text,', 'but', 'next', 'is', 'a', 'code', 'paragraph', 'with', 'a', 'lot', 'of', 'internal', 'newlines', 'and', 'stuff.', '\n\n',
            '        for x in range(3):', '\n', '\n', '\n', '\n', '\n', '                print(x)', '\n', '\n', '\n', '                print(x*x)', '\n\n', 'welp!', "that's", 'it', 'for', 'the', 'code.']
            )
        with self.assertRaises(RuntimeError):
            big.split_text_with_code("howdy.\n\vwhat's this?")
        with self.assertRaises(RuntimeError):
            big.split_text_with_code("howdy.\n    for a in \v range(30):\n        print(a)")

    def test_merge_columns(self):
        def test(columns, expected, **kwargs):
            got = big.merge_columns(*columns, **kwargs)
            if 0:
                print("_"*70)
                print("columns")
                print(repr(columns))
                print("expected:")
                print()
                print(repr(expected))
                print(expected)
                print()
                print("got:")
                print()
                print(repr(got))
                print(got)
                print()
                print()
            self.assertEqual(got, expected)

        with self.assertRaises(OverflowError):
            test([("1\n2\n3 4 5 6 7 8", 4, 4), ("howdy\nhello\nhi, how are you?\ni'm fine.", 5, 16), ("ending\ntext!".split("\n"), 79, 79)],
                "1    howdy            ending\n2    hello            text!\n3    hi, how are you?\n     i'm fine.",
                overflow_strategy=big.OverflowStrategy.RAISE)

        test([("1\n2\n3", 4, 4), ("howdy\nhello\nhi, how are you?\ni'm fine.", 5, 16), ("ending\ntext!".split("\n"), 79, 79)],
            "1    howdy            ending\n2    hello            text!\n3    hi, how are you?\n     i'm fine.",
            overflow_strategy=big.OverflowStrategy.INTRUDE_ALL)

        test([("super long lines here\nI mean, they just go on and on.\n(text)\nshort now\nhowever.\nthank\nthe maker!", 5, 15), ("this is the second column.\ndoes it have to wait?  it should.", 20, 60)],
            'super long lines here\nI mean, they just go on and on.\n(text)\nshort now\nhowever.        this is the second column.\nthank           does it have to wait?  it should.\nthe maker!',
            overflow_after=2,
            overflow_strategy=big.OverflowStrategy.INTRUDE_ALL)

        # merge overflows due to overflow_before and overflow_after being large
        test([
            ("overflow line 1\na\nb\nc\nd\noverflow line 2\n", 4, 8),
            ("this is the second column.\ndoes it have to wait?  it should.", 20, 60),
            ],
            'overflow line 1\na\nb\nc\nd\noverflow line 2\n         this is the second column.\n         does it have to wait?  it should.',
            overflow_before=2,
            overflow_after=3,
            overflow_strategy=big.OverflowStrategy.INTRUDE_ALL)

        test([
            ("overflow line 1\na\nb\nc\nd\ne\nf\noverflow line 2\n", 4, 8),
            ("this is the second column.\ndoes it have to wait?  not this time.", 20, 60),
            ],
            'overflow line 1\na        this is the second column.\nb        does it have to wait?  not this time.\nc\nd\ne\nf\noverflow line 2',
            overflow_strategy=big.OverflowStrategy.INTRUDE_ALL)
        # test pause until final
        test([
            ("overflow line 1\na\nb\nc\nd\ne\nf\noverflow line 2\n", 4, 8),
            ("this is the second column.\ndoes it have to wait?  it should.", 20, 60),
            ],
            'overflow line 1\na\nb\nc\nd\ne\nf\noverflow line 2\n         this is the second column.\n         does it have to wait?  it should.',
            overflow_strategy = big.OverflowStrategy.DELAY_ALL,
            )

        results = [
            '1 | aaa | what | aaa\n2 | bbb | ho   | bbb\n3 | ccc | too-long\n4 | ddd | column\n5 | eee | here | ccc\n6 | fff | my   | ddd\n7 | ggg | oh   | eee\n8 | hhh | my   | fff\n  |     | what | ggg\n  |     | tweedy\n  |     | fun  | hhh',
            '1 | aaa | what | aaa\n2 | bbb | ho   | bbb\n3 | ccc | too-long\n4 | ddd | column\n5 | eee | here\n6 | fff | my   | ccc\n7 | ggg | oh   | ddd\n8 | hhh | my   | eee\n  |     | what | fff\n  |     | tweedy\n  |     | fun\n  |     |      | ggg\n  |     |      | hhh',
            '1 | aaa | what | aaa\n2 | bbb | ho\n3 | ccc | too-long\n4 | ddd | column\n5 | eee | here | bbb\n6 | fff | my   | ccc\n7 | ggg | oh   | ddd\n8 | hhh | my   | eee\n  |     | what\n  |     | tweedy\n  |     | fun  | fff\n  |     |      | ggg\n  |     |      | hhh',
            '1 | aaa | what | aaa\n2 | bbb | ho\n3 | ccc | too-long\n4 | ddd | column\n5 | eee | here\n6 | fff | my   | bbb\n7 | ggg | oh   | ccc\n8 | hhh | my   | ddd\n  |     | what\n  |     | tweedy\n  |     | fun\n  |     |      | eee\n  |     |      | fff\n  |     |      | ggg\n  |     |      | hhh',
            ]

        results_iterator = iter(results)
        for overflow_before in range(2):
            for overflow_after in range(2):
                test((
                    ("1\n2\n3\n4\n5\n6\n7\n8", 1, 1),
                    ("aaa\nbbb\nccc\nddd\neee\nfff\nggg\nhhh", 3, 3),
                    ("what\nho\ntoo-long\ncolumn\nhere\nmy\noh\nmy\nwhat\ntweedy\nfun\n", 2, 4),
                    ("aaa\nbbb\nccc\nddd\neee\nfff\nggg\nhhh", 3, 3),
                    ),
                    next(results_iterator),
                    column_separator=" | ",
                    overflow_before=overflow_before,
                    overflow_after=overflow_after,
                    overflow_strategy=big.OverflowStrategy.INTRUDE_ALL)

        test((
            ("1\n2\n3\n4\n5\n6\n7\n8", 1, 1),
            ("aaa\nbbb\nccc\nddd\neee\nfff\nggg\nhhh", 3, 3),
            ("what\nho\ntoo-long\ncolumn\nhere\nmy\noh\nmy\nwhat\ntweedy\nfun\n", 2, 4),
            ("aaa\nbbb\nccc\nddd\neee\nfff\nggg\nhhh", 3, 3),
            ),
            '1 | aaa | what\n2 | bbb | ho\n3 | ccc | too-long\n4 | ddd | column\n5 | eee | here\n6 | fff | my\n7 | ggg | oh\n8 | hhh | my\n  |     | what\n  |     | tweedy\n  |     | fun\n  |     |      | aaa\n  |     |      | bbb\n  |     |      | ccc\n  |     |      | ddd\n  |     |      | eee\n  |     |      | fff\n  |     |      | ggg\n  |     |      | hhh',
            column_separator=" | ",
            overflow_strategy=big.OverflowStrategy.DELAY_ALL,
            overflow_before=0,
            overflow_after=1,
            )



    def test_text_pipeline(self):
        def test(columns, expected):
            splits = [(big.split_text_with_code(column), min, max) for column, min, max in columns]
            wrapped = [(big.wrap_words(split, margin=max), min, max) for split, min, max in splits]
            got = big.merge_columns(*wrapped, overflow_strategy=big.OverflowStrategy.INTRUDE_ALL)
            if 0:
                print("_"*70)
                print("columns")
                print(repr(columns))
                print("expected:")
                print()
                print(expected)
                print()
                print("got:")
                print()
                print(got)
                print()
                print()
            self.assertEqual(got, expected)

        test(
            (
                (
                "-v|--verbose",
                19,
                19,
                ),
                (
                "Causes the program to produce more output.  Specifying it multiple times raises the volume of output.",
                0,
                60,
                ),
            ),
            '-v|--verbose        Causes the program to produce more output.  Specifying it\n                    multiple times raises the volume of output.'
        )

        test(
            (
                (
                "-v|--verbose",
                9,
                9,
                ),
                (
                "Causes the program to produce more output.  Specifying it multiple times raises the volume of output.",
                0,
                60,
                ),
            ),
            '-v|--verbose\n          Causes the program to produce more output.  Specifying it\n          multiple times raises the volume of output.'
        )

        # an empty column just adds space.  so, to indent everything, add an empty initial column.
        # note that it'll be min_width wide and *then* you'll get the column_separator.
        test(
            (
                (
                "",
                3,
                3,
                ),
                (
                "-v|--verbose",
                19,
                19,
                ),
                (
                "Causes the program to produce more output.  Specifying it multiple times raises the volume of output.",
                0,
                60,
                ),
            ),
            '    -v|--verbose        Causes the program to produce more output.  Specifying it\n                        multiple times raises the volume of output.'
        )

    def test_gently_title(self):
        def test(s, expected):
            result = big.gently_title(s)
            self.assertEqual(result, expected)

        test("", "")
        test("abcde fgh", "Abcde Fgh")
        test("peter o'toole", "Peter O'Toole")
        test("lord d'arcy", "Lord D'Arcy")
        test("multiple   spaces", "Multiple   Spaces")
        test("'twas the night before christmas", "'Twas The Night Before Christmas")
        test("don't sleep on the subway", "Don't Sleep On The Subway")
        test("everybody's thinking they couldn't've had a v-8", "Everybody's Thinking They Couldn't've Had A V-8")
        test("""i said "no, i didn't", you idiot""", """I Said "No, I Didn't", You Idiot""")
        test('multiple «"“quote marks”"»', 'Multiple «"“Quote Marks”"»')

    def test_normalize_whitespace(self):
        def test(s, expected):
            result = big.normalize_whitespace(s)
            self.assertEqual(result, expected)

        test("   a    b    c", " a b c")
        test("d     e  \t\n  f ", "d e f ")
        test("ghi", "ghi")
        test("   j     kl   mnop    ", " j kl mnop ")
        test("", "")
        test("   \n\n\t \t     ", " ")

    def test_stripped_lines(self):
        def test(s, sep=None):
            if sep is None:
                test_sep = '\n'
            else:
                test_sep = sep

            rstrip_result = list(big.rstripped_lines(s, sep=sep))
            rstrip_expected = [line.rstrip() for line in s.split(test_sep)]
            self.assertEqual(rstrip_result, rstrip_expected)

            strip_result = list(big.stripped_lines(s, sep=sep))
            strip_expected = [line.strip() for line in s.split(test_sep)]
            self.assertEqual(strip_result, strip_expected)

            # re-test using bytes
            s = s.encode('ascii')
            if sep is not None:
                sep = sep.encode('ascii')
            test_sep = test_sep.encode('ascii')

            b_rstrip_result = list(big.rstripped_lines(s, sep=sep))
            b_rstrip_expected = [line.rstrip() for line in s.split(test_sep)]
            self.assertEqual(b_rstrip_result, b_rstrip_expected)

            b_strip_result = list(big.stripped_lines(s, sep=sep))
            b_strip_expected = [line.strip() for line in s.split(test_sep)]
            self.assertEqual(b_strip_result, b_strip_expected)

        test("  a b \n c=d\n    e = f   \n  g = h   \n i = j")

        s = "\n  \n  a b \n c=d\n    e = f   \n  g = h   \n\n   "
        test(s)
        test(s.strip())

        test("  a b X c=dX    e = f   X  g = h   X i = j", sep='X')



import bigtestlib

def run_tests():
    bigtestlib.run(name="big.text", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
