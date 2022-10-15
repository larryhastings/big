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

import copy
import big
import big.text
import math
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


known_separators = [
    (big.whitespace, "big.whitespace"),
    (big.whitespace_without_dos, "big.whitespace_without_dos"),
    (big.newlines,   "big.newlines"),
    (big.newlines_without_dos,   "big.newlines_without_dos"),

    (big.ascii_whitespace, "big.ascii_whitespace"),
    (big.ascii_whitespace_without_dos, "big.ascii_whitespace_without_dos"),
    (big.ascii_newlines,   "big.ascii_newlines"),
    (big.ascii_newlines_without_dos,   "big.ascii_newlines_without_dos"),

    (big.utf8_whitespace, "big.utf8_whitespace"),
    (big.utf8_whitespace_without_dos, "big.utf8_whitespace_without_dos"),
    (big.utf8_newlines,   "big.utf8_newlines"),
    (big.utf8_newlines_without_dos,   "big.utf8_newlines_without_dos"),
]

def printable_separators(separators):
    for known, name in known_separators:
        if separators == known:
            return f"{name}"
    return separators

class BigTextTests(unittest.TestCase):

    def test_whitespace_and_newlines(self):
        # ensure that big.whitespace and big.newlines
        # correctly matches the list of characters that
        # Python considers whitespace / newlines.

        # Python whitespace only considers individual
        # whitespace charcters, and doesn't include the
        # DOS end-of-line sequence '\r\n'.  so what we're
        # going to produce in the below list is technically
        # the "without DOS" versions.
        python_whitespace_without_dos = []
        python_newlines_without_dos = []

        # technically we don't need to check the surrogate pair characters.
        # but it's faster to leave them in.
        unicode_code_points = 2**16 + 2**20

        for i in range(unicode_code_points):
            c = chr(i)
            s = f"a{c}b"
            if len(s.split()) == 2:
                python_whitespace_without_dos.append(c)
                if len(s.splitlines()) == 2:
                    python_newlines_without_dos.append(c)

        self.assertEqual(set(big.whitespace_without_dos), set(python_whitespace_without_dos))
        self.assertEqual(set(big.newlines_without_dos), set(python_newlines_without_dos))

        python_whitespace = list(python_whitespace_without_dos)
        python_whitespace.append("\r\n")
        python_newlines = list(python_newlines_without_dos)
        python_newlines.append("\r\n")
        self.assertEqual(set(big.whitespace), set(python_whitespace))
        self.assertEqual(set(big.newlines), set(python_newlines))

        # now test the utf-8 and ascii variants!

        python_ascii_whitespace = big.text._cheap_encode_iterable_of_strings(python_whitespace, 'ascii')
        self.assertEqual(set(big.ascii_whitespace), set(python_ascii_whitespace))
        python_ascii_whitespace_without_dos = big.text._cheap_encode_iterable_of_strings(python_whitespace_without_dos, 'ascii')
        self.assertEqual(set(big.ascii_whitespace_without_dos), set(python_ascii_whitespace_without_dos))
        python_ascii_newlines = big.text._cheap_encode_iterable_of_strings(python_newlines, 'ascii')
        self.assertEqual(set(big.ascii_newlines), set(python_ascii_newlines))
        python_ascii_newlines_without_dos = big.text._cheap_encode_iterable_of_strings(python_newlines_without_dos, 'ascii')
        self.assertEqual(set(big.ascii_newlines_without_dos), set(python_ascii_newlines_without_dos))

        python_utf8_whitespace = big.text._cheap_encode_iterable_of_strings(python_whitespace, 'utf8')
        self.assertEqual(set(big.utf8_whitespace), set(python_utf8_whitespace))
        python_utf8_whitespace_without_dos = big.text._cheap_encode_iterable_of_strings(python_whitespace_without_dos, 'utf8')
        self.assertEqual(set(big.utf8_whitespace_without_dos), set(python_utf8_whitespace_without_dos))
        python_utf8_newlines = big.text._cheap_encode_iterable_of_strings(python_newlines, 'utf8')
        self.assertEqual(set(big.utf8_newlines), set(python_utf8_newlines))
        python_utf8_newlines_without_dos = big.text._cheap_encode_iterable_of_strings(python_newlines_without_dos, 'utf8')
        self.assertEqual(set(big.utf8_newlines_without_dos), set(python_utf8_newlines_without_dos))


    def test_re_partition(self):
        def group0(re_partition_result):
            result = []
            for i, o in enumerate(re_partition_result):
                if (i % 2) and (o is not None):
                    o = o.group(0)
                result.append(o)
            return tuple(result)

        for c in (unchanged, to_bytes):
            pattern = c("[0-9]+")

            s = c("abc123def456ghi")
            self.assertEqual(group0(big.re_partition(s, pattern)),
                c(("abc", "123", "def456ghi")) )
            self.assertEqual(group0(big.re_rpartition(s, pattern)),
                c(("abc123def", "456", "ghi")) )
            self.assertEqual(group0(big.re_partition(s, pattern, reverse=True)),
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

            def test_re_partition(s, pattern, count, expected):
                self.assertEqual(group0(big.re_partition(s, pattern, count)),
                    expected )

            test_re_partition("a:b:c:d", ":", 0, ("a:b:c:d",))
            test_re_partition("a:b:c:d", ":", 1, ("a", ":", "b:c:d"))
            test_re_partition("a:b:c:d", ":", 2, ("a", ":", "b", ":", "c:d"))
            test_re_partition("a:b:c:d", ":", 3, ("a", ":", "b", ":", "c", ":", "d"))
            test_re_partition("a:b:c:d", ":", 4, ("a", ":", "b", ":", "c", ":", "d", None, ''))
            test_re_partition("a:b:c:d", ":", 5, ("a", ":", "b", ":", "c", ":", "d", None, '', None, ''))

            def test_re_rpartition(s, pattern, count, expected):
                self.assertEqual(group0(big.re_rpartition(s, pattern, count)),
                    expected )
                self.assertEqual(group0(big.re_partition(s, pattern, count, reverse=True)),
                    expected )

            test_re_rpartition("a:b:c:d", ":", 0, ("a:b:c:d",))
            test_re_rpartition("a:b:c:d", ":", 1, ("a:b:c", ':' ,"d"))
            test_re_rpartition("a:b:c:d", ":", 2, ("a:b", ":", "c", ':' ,"d"))
            test_re_rpartition("a:b:c:d", ":", 3, ("a", ":", "b", ":", "c", ':' ,"d"))
            test_re_rpartition("a:b:c:d", ":", 4, ("", None, "a", ":", "b", ":", "c", ':' ,"d"))
            test_re_rpartition("a:b:c:d", ":", 5, ("", None, "", None, "a", ":", "b", ":", "c", ':' ,"d"))



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

        with self.assertRaises(ValueError):
            big.re_partition('a:b', ':', -1)
        with self.assertRaises(ValueError):
            big.re_partition(b'a:b', b':', -1)
        with self.assertRaises(ValueError):
            big.re_rpartition('a:b', ':', -1)
        with self.assertRaises(ValueError):
            big.re_rpartition(b'a:b', b':', -1)

    def test_multistrip(self):
        def test_multistrip(left, s, right, separators):
            for _ in range(2):
                if _ == 1:
                    left = left.encode('ascii')
                    s = s.encode('ascii')
                    right = right.encode('ascii')
                    if separators == big.whitespace:
                        separators = big.ascii_whitespace
                    elif separators == big.newlines:
                        separators = big.ascii_newlines
                    else:
                        assert isinstance(separators, str)
                        separators = separators.encode('ascii')

                self.assertEqual(big.multistrip(s, separators, left=False, right=False), s)
                self.assertEqual(big.multistrip(s, separators, left=False, right=True ), s)
                self.assertEqual(big.multistrip(s, separators, left=True,  right=False), s)
                self.assertEqual(big.multistrip(s, separators, left=True,  right=True ), s)

                ls = left + s
                self.assertEqual(big.multistrip(ls, separators, left=False, right=False), ls)
                self.assertEqual(big.multistrip(ls, separators, left=False, right=True ), ls)
                self.assertEqual(big.multistrip(ls, separators, left=True,  right=False), s)
                self.assertEqual(big.multistrip(ls, separators, left=True,  right=True ), s)

                sr = s + right
                self.assertEqual(big.multistrip(sr, separators, left=False, right=False), sr)
                self.assertEqual(big.multistrip(sr, separators, left=False, right=True ), s)
                self.assertEqual(big.multistrip(sr, separators, left=True,  right=False), sr)
                self.assertEqual(big.multistrip(sr, separators, left=True,  right=True ), s)

                lsr = left + s + right
                self.assertEqual(big.multistrip(lsr, separators, left=False, right=False), lsr)
                self.assertEqual(big.multistrip(lsr, separators, left=False, right=True ), ls)
                self.assertEqual(big.multistrip(lsr, separators, left=True,  right=False), sr)
                self.assertEqual(big.multistrip(lsr, separators, left=True,  right=True ), s)

        test_multistrip(" \t \n ", "abcde", " \n \t ", " \t\n")
        test_multistrip(" \t \n ", "abcde", " \n \t ", big.whitespace)
        test_multistrip("\r\n\n\r", "abcde", "\n\r\r\n", big.newlines)
        test_multistrip("\r\n\n\r", "abcde", "\n\r\r\n", big.whitespace)
        test_multistrip("xXXxxxXx", "iiiiiii", "yyYYYyyyyy", "xyXY")

    def test_multisplit(self):
        for c in (unchanged, to_bytes):
            def multisplit(*a, **kw): return list(big.multisplit(*a, **kw))
            self.assertEqual(multisplit(c('aaaXaaaYaaa'), c('abc')), c(['X', 'Y']))
            self.assertEqual(multisplit(c('abcXbcaYcba'), c('abc')), c(['X', 'Y']))

            self.assertEqual(multisplit(c(''), c('abcde'), maxsplit=None), c(['']))
            self.assertEqual(multisplit(c('abcde'), c('fghij')), c(['abcde']))
            self.assertEqual(multisplit(c('abcde'), c('fghijc')), c(['ab', 'de']))
            self.assertEqual(multisplit(c('1a2b3c4d5e6'), c('abcde')), c(['1', '2', '3', '4', '5', '6']))

            self.assertEqual(multisplit(c('ab:cd,ef'), c(':,')), c(["ab", "cd", "ef"]))
            self.assertEqual(multisplit(c('ab:cd,ef:'), c(':,')), c(["ab", "cd", "ef"]))
            self.assertEqual(multisplit(c(',ab:cd,ef:'), c(':,')), c(["ab", "cd", "ef"]))
            self.assertEqual(multisplit(c(':ab:cd,ef'), c(':,')), c(["ab", "cd", "ef"]))
            self.assertEqual(multisplit(c('WWabXXcdYYabZZ'), c(('ab', 'cd'))), c(['WW', 'XX', 'YY', 'ZZ']))
            self.assertEqual(multisplit(c('WWabXXcdYYabZZab'), c(('ab', 'cd'))), c(['WW', 'XX', 'YY', 'ZZ']))
            self.assertEqual(multisplit(c('abWWabXXcdYYabZZ'), c(('ab', 'cd'))), c(['WW', 'XX', 'YY', 'ZZ']))
            self.assertEqual(multisplit(c('WWabXXcdYYabZZcd'), c(('ab', 'cd'))), c(['WW', 'XX', 'YY', 'ZZ']))
            self.assertEqual(multisplit(c('XXabcdYY'), c(('a', 'abcd'))), c(['XX', 'YY']))
            self.assertEqual(multisplit(c('XXabcdabcdYY'), c(('ab', 'cd'))), c(['XX', 'YY']))
            self.assertEqual(multisplit(c('abcdXXabcdabcdYYabcd'), c(('ab', 'cd'))), c(['XX', 'YY']))

            self.assertEqual(multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=0), c(['xaxbxcxdxex']))
            self.assertEqual(multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=1), c(['x', 'xbxcxdxex']))
            self.assertEqual(multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=2), c(['x', 'x', 'xcxdxex']))
            self.assertEqual(multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=3), c(['x', 'x', 'x', 'xdxex']))
            self.assertEqual(multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=4), c(['x', 'x', 'x', 'x', 'xex']))
            self.assertEqual(multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=5), c(['x', 'x', 'x', 'x', 'x', 'x']))
            self.assertEqual(multisplit(c('xaxbxcxdxex'), c('abcde'), maxsplit=6), c(['x', 'x', 'x', 'x', 'x', 'x']))

            # test greedy separators
            self.assertEqual(multisplit(c('-abcde-abc-a-abc-abcde-'), c(['a', 'abc', 'abcde'])), c(['-', '-', '-', '-', '-', '-']))

            # regression test: *YES*, if the string you're splitting ends with a separator,
            # and keep=big.AS_PAIRS, the result ends with a tuple containing two empty strings.
            self.assertEqual(multisplit(c('\na\nb\nc\n'), c(('\n',)), keep=big.AS_PAIRS, strip=False), c([ ('', '\n'), ('a', '\n'), ('b', '\n'), ('c', '\n'), ('', '') ]))

        with self.assertRaises(TypeError):
            multisplit('s', 3.1415)
        with self.assertRaises(ValueError):
            multisplit('s', b'abc')

    def test_advanced_multisplit(self):
        def simple_test_multisplit(s, separators, expected, **kwargs):
            for _ in range(2):
                if _ == 1:
                    # encode!
                    s = s.encode('ascii')
                    if separators == big.whitespace:
                        separators = big.ascii_whitespace
                    elif isinstance(separators, str):
                        separators = separators.encode('ascii')
                    else:
                        separators = big.text._cheap_encode_iterable_of_strings(separators)
                    expected = list(big.text._cheap_encode_iterable_of_strings(expected))
                # print()
                # print(f"{s=} {expected=}\n{separators=}")
                result = list(big.multisplit(s, separators, **kwargs))
                self.assertEqual(result, expected)

        for i in range(8):
            spaces = " " * i
            simple_test_multisplit(spaces + "a  b  c" + spaces, (" ",), ['a', 'b', 'c'])
            simple_test_multisplit(spaces + "a  b  c" + spaces, big.whitespace, ['a', 'b', 'c'])


        simple_test_multisplit("first line!\nsecond line.\nthird line.", big.newlines,
            ["first line!", "second line.", "third line."])
        simple_test_multisplit("first line!\nsecond line.\nthird line.\n", big.newlines,
            ["first line!\n", "second line.\n", "third line."], keep=True, strip=True)
        simple_test_multisplit("first line!\nsecond line.\nthird line.\n", big.newlines,
            ["first line!\n", "second line.\n", "third line.\n", ""], keep=True, strip=False)
        simple_test_multisplit("first line!\n\nsecond line.\n\n\nthird line.", big.newlines,
            ["first line!", '', "second line.", '', '', "third line."], separate=True)
        simple_test_multisplit("first line!\n\nsecond line.\n\n\nthird line.", big.newlines,
            ["first line!\n", '\n', "second line.\n", '\n', '\n', "third line."], keep=True, separate=True)


        simple_test_multisplit("a,b,,,c", ",", ['a', 'b', '', '', 'c'], separate=True)

        simple_test_multisplit("a,b,,,c", (",",), ['a', 'b', ',,c'], separate=True, maxsplit=2)

        simple_test_multisplit("a,b,,,c", (",",), ['a,b,', '', 'c'], separate=True, maxsplit=2, reverse=True)

    def test_multisplit_against_split(self):
        # can't test against split(None), we don't have strip=STR_SPLIT yet
        def test_split_with_separator(s, separator, maxsplit):
            expected = s.split(separator, maxsplit)
            result = list(big.multisplit(s, separator, keep=False, separate=True, strip=False, reverse=False, maxsplit=maxsplit))
            self.assertEqual(expected, result)

        def test_rsplit_with_separator(s, separator, maxsplit):
            expected = s.rsplit(separator, maxsplit)
            result = list(big.multisplit(s, separator, keep=False, separate=True, strip=False, reverse=True, maxsplit=maxsplit))
            self.assertEqual(expected, result)

        for base_s in (
            "",
            "a",
            "a b c",
            "a b  c d   e",
            ):
            for leading in range(10):
                for trailing in range(10):
                    s = (" " * leading) + base_s + (" " * trailing)
                    for maxsplit in range(-1, 8):
                        test_split_with_separator(s, " ", maxsplit)
                        test_rsplit_with_separator(s, " ", maxsplit)


    def test_multisplit_exhaustively(self):
        def multisplit_tester(*segments):
            """
            segments represent split-up text segments.
            each segment is either
              a) in separators, or
              b) contains no separators at all.
            you don't need to start or end with empty strings.

            and, the last positional argument is actually "separators".
            as in, the separators argument for multisplit.

            tests Every. Possible. Permutation. of inputs to multisplit()
            based on the segments you pass in.  this includes
                * as strings and encoded to bytes (ascii)
                * with and without the left separators
                * with and without the right separators
                * with every combination of every value of
                    * keep
                    * maxsplit (all values that produce different results, plus a couple extra Just In Case)
                    * reverse
                    * separate
                    * strip

            p.s it takes a minute to run!
            """

            # want_prints = True
            want_prints = False

            if want_prints: # pragma: no cover
                print("_" * 69)
                print()
                print("test exhaustively")
                print("_" * 69)

            segments = list(segments)
            separators = segments.pop()

            if separators is not None:
                separators_set = set(separators)
            else:
                separators_set = set(big.whitespace)
            assert '' not in separators_set

            # strip off the leading and trailing separators.

            # leading looks like this:
            #   [ '', separator, separator, separator, ... ]
            # yes, that is always an empty string, you'll see why
            # in a moment.

            leading = ['']
            while True:
                if segments[0] not in separators_set:
                    break
                leading.append(segments.pop(0))

            # trailing contains just the trailing (right)
            # separators, as individual strings.
            # trailing just looks like this:
            #   [ separator, separator, ... ]

            trailing = []
            while True:
                if want_prints: # pragma: no cover
                    print(f"splitting segments: {segments[-1]=} {separators_set=} not in? {segments[-1] not in separators_set}")
                if segments[-1] not in separators_set:
                    break
                trailing.append(segments.pop())
            trailing.reverse()

            # splits is a list of lists.  each sublist, or "split",
            # inside splits, looks like this:
            #   [ non-separator-string, separator, separator, ... ]
            # (yes, leading and an individual split list look identical, that's why.)
            # every split in splits is has at least one separator
            # EXCEPT the last one which only has the non-sep string.
            #
            # this is only an intermediate form, we'll massage this
            # into a more useful form in a minute.
            splits = []
            split = []
            def flush():
                nonlocal split
                if split:
                    splits.append(split)
                    split = []

            for segment in segments:
                if segment in separators_set:
                    assert split
                    split.append(segment)
                    continue
                assert (not split) or (split[-1] in separators_set), f"{split=} {split[-1]=} {separators_set=}"
                flush()
                split.append(segment)
            flush()

            if want_prints: # pragma: no cover
                print(f"{leading=}")
                print(f"{splits=}")
                print(f"{trailing=}")
            assert splits[-1][-1] not in separators_set, f"{splits[-1][-1]=} is in {separators_set=}!"

            # leading and trailing must both have at least
            # one sep string.
            assert (len(leading) >= 2) and trailing

            # note one invariant: if you join leading, splits, and trailing
            # together into one big string, it is our original input string.
            # that will never change.

            originals = leading, splits, trailing

            for as_bytes in (False, True):
                if want_prints: # pragma: no cover
                    print(f"[loop 0] {as_bytes=}")
                if as_bytes:
                    leading, splits, trailing = copy.deepcopy(originals)
                    leading = big.text._cheap_encode_iterable_of_strings(leading)
                    splits = [big.text._cheap_encode_iterable_of_strings(split) for split in splits]
                    trailing = big.text._cheap_encode_iterable_of_strings(trailing)
                    originals = [leading, splits, trailing]
                    empty = b''
                    if separators is None:
                        separators_set = set(big.ascii_whitespace)
                    else:
                        separators = big.text._cheap_encode_iterable_of_strings(separators)
                        separators_set = set(separators)
                    non_sep_marker = b"&NONSEP&"
                else:
                    empty = ''
                    non_sep_marker = "&NONSEP&"

                for use_leading in (False, True):
                    for use_trailing in (False, True):
                        # we're going to hack up these lists,
                        # so start with copies.
                        leading, splits, trailing = copy.deepcopy(originals)

                        if want_prints: # pragma: no cover
                            print(f"[loop 1,2] {use_leading=} {use_trailing=}")
                            print(f"         {leading=} {split=} {trailing=}")

                        input_strings = []
                        if use_leading:
                            input_strings.extend(leading)
                        for split in splits:
                            input_strings.extend(split)
                        if use_trailing:
                            input_strings.extend(trailing)

                        input_string = empty.join(input_strings)

                        for separate in (False, True):
                            leading, splits, trailing = copy.deepcopy(originals)
                            # now we're going to change leading / splits / trailing
                            # so that they collectively alternate
                            #    nonsep, sep

                            if want_prints: # pragma: no cover
                                print(f"[loop 3] {separate=}")
                                print(f"    {leading=} {splits=} {trailing=}")

                            if not separate:
                                # blob the separators together
                                l2 = [empty]
                                if want_prints: # pragma: no cover
                                    print(f"    blob together {empty=} {leading=}")
                                l2.append(empty.join(leading))
                                leading = l2
                                if want_prints: # pragma: no cover
                                    print(f"    blobbed {leading=}")

                                for split in splits:
                                    if len(split) > 1:
                                        joined = empty.join(split[1:])
                                        del split[1:]
                                        split.append(joined)

                                trailing = [empty.join(trailing), empty]
                            else:
                                # turn leading, splits, and trailing
                                # into suitable form for testing with "separate".
                                #   * every list is a list of alternating sep and nonsep.
                                #   * splits now has empty strings between sep and nonsep.
                                assert len(leading) >= 2
                                separate_leading = list(leading[:2])
                                for s in leading[2:]:
                                    separate_leading.append(empty)
                                    separate_leading.append(s)
                                leading = separate_leading
                                if want_prints: # pragma: no cover
                                    print(f"    {leading=}")

                                separate_splits = []
                                for split in splits:
                                    if len(split) == 1:
                                        assert split == splits[-1]
                                        separate_splits.append(split)
                                        break
                                    assert len(split) >= 2
                                    separate_splits.append(list(split[:2]))
                                    for s in split[2:]:
                                        separate_splits.append([empty, s])
                                splits = separate_splits
                                if want_prints: # pragma: no cover
                                    print(f"    {splits=}")

                                separate_trailing = []
                                for s in trailing:
                                    if s: # skip the trailing empty
                                        separate_trailing.append(s)
                                        separate_trailing.append(empty)
                                trailing = separate_trailing
                                if want_prints: # pragma: no cover
                                    print(f"    {trailing=}")

                            # time to check!  every list or sublist
                            # should now have an even length,
                            # EXCEPT splits[-1] which is length 1.
                            assert len(leading) % 2 == 0
                            for split in splits[:-1]:
                                assert len(split) % 2 == 0
                            assert len(splits[-1]) == 1
                            assert len(trailing) % 2 == 0

                            for strip in (False, big.LEFT, big.RIGHT, True):
                                expected = []
                                if want_prints: # pragma: no cover
                                    print(f"[loop 4] {strip=}")
                                    print(f"         {leading=} {splits=} {trailing=}")

                                if use_leading and (strip in (False, big.RIGHT)):
                                    expected.extend(leading)
                                if want_prints: # pragma: no cover
                                    print(f"     leading: {expected=}")

                                for split in splits:
                                    expected.extend(split)
                                if want_prints: # pragma: no cover
                                    print(f"      splits: {expected=}")

                                if use_trailing and (strip in (False, big.LEFT)):
                                    expected.extend(trailing)
                                if want_prints: # pragma: no cover
                                    print(f"    trailing: {expected=}")

                                # expected now looks like this:
                                #   * it has an odd number of items
                                #   * even numbered items are nonsep
                                #   * odd numbered items are sep
                                assert len(expected) % 2 == 1, f"{expected=} doesn't have an odd # of elements!"
                                for i in range(0, len(expected), 2):
                                    assert expected[i] not in separators_set
                                for i in range(1, len(expected), 2):
                                    assert not big.multistrip(expected[i], separators_set), f"expected[{i}]={expected[i]!r} not in {separators_set=} !"

                                # how many splits can we have?
                                # Technically the maximum number of splits possible
                                # is
                                #    (len(expected) // 2) - 1
                                # 'a b c d e' would split by whitespace into 9 elements,
                                # only using four splits.
                                # Anyway we test a couple supernumerary maxsplit values.
                                max_maxsplit = (len(expected) // 2) + 1

                                expected_original = expected

                                if want_prints: # pragma: no cover
                                    print(f"    {expected_original=}")

                                for reverse in (False, True):
                                    for maxsplit in range(-1, max_maxsplit):
                                        expected = list(expected_original)
                                        if want_prints: # pragma: no cover
                                            print(f"[loop 5,6] {reverse=} {maxsplit=} // {expected=}")
                                        if maxsplit == 0:
                                            joined = empty.join(expected)
                                            expected = [joined]
                                        elif maxsplit > 0:
                                            if not reverse:
                                                # we're in "alternating" mode,
                                                # so odd-numbered indexes are
                                                # splits
                                                #
                                                # length 7
                                                #  0    1    2    3    4    5    6   index
                                                # ['a', ' ', 'b', ' ', 'c', ' ', 'd']
                                                #  0         1          2        3   maxsplit
                                                start = maxsplit * 2
                                                end = len(expected)
                                                if start < end:
                                                    if want_prints: # pragma: no cover
                                                        print(f"    not reverse: expected[{start}:{end}] = {expected[start:end]}")
                                                    joined = non_sep_marker + empty.join(expected[start:end])
                                                    del expected[start:end]
                                                    if want_prints: # pragma: no cover
                                                        print(f"    {expected=} {joined=} {empty=}")
                                                    expected.append(joined)
                                            else:
                                                # reverse and maxsplit
                                                #
                                                # length 7
                                                #  0    1    2    3    4    5    6   index
                                                # ['a', ' ', 'b', ' ', 'c', ' ', 'd',  ]
                                                #       3         2         1         0   maxsplit
                                                start = 0
                                                end = len(expected) - (maxsplit * 2)
                                                joined = non_sep_marker + empty.join(expected[start:end])
                                                if want_prints: # pragma: no cover
                                                    print(f"    reverse: expected[{start}:{end}] = {expected[start:end]}  /// {joined=}")
                                                del expected[start:end]
                                                if want_prints: # pragma: no cover
                                                    print(f"    {expected=} {joined=}")
                                                expected.insert(0, joined)
                                        expected_original2 = expected
                                        for keep in (False, True, big.ALTERNATING, big.AS_PAIRS):
                                            expected = list(expected_original2)
                                            if want_prints: # pragma: no cover
                                                print(f"[loop 7] {keep=} // {expected=}")
                                            if not keep:
                                                expected = [s.replace(non_sep_marker, empty) for i, s in enumerate(expected) if i % 2 == 0]
                                            elif keep == big.AS_PAIRS:
                                                new_expected = []
                                                waiting = None
                                                def append(s):
                                                    nonlocal waiting
                                                    s = s.replace(non_sep_marker, empty)
                                                    if waiting is None:
                                                        waiting = s
                                                        return
                                                    new_expected.append((waiting, s))
                                                    waiting = None
                                                for s in expected:
                                                    append(s)
                                                # manual flush
                                                if waiting is not None:
                                                    append(empty)
                                                expected = new_expected
                                            elif keep == big.ALTERNATING:
                                                # strip non_sep_marker hack
                                                expected = [s.replace(non_sep_marker, empty) for s in expected]
                                            elif keep:
                                                new_expected = []
                                                waiting = None
                                                def append(s):
                                                    nonlocal waiting
                                                    is_sep = s in separators_set
                                                    s = s.replace(non_sep_marker, empty)
                                                    if (waiting is None) and (not is_sep):
                                                        waiting = s
                                                        return
                                                    if waiting is not None:
                                                        s = waiting + s
                                                    new_expected.append(s)
                                                    waiting = None
                                                for s in expected:
                                                    append(s)
                                                # manual flush
                                                if waiting is not None:
                                                    new_expected.append(waiting)
                                                expected = new_expected
                                                if want_prints: # pragma: no cover
                                                    print(f"    now {expected=}")

                                            result = list(big.multisplit(input_string, separators,
                                                keep=keep,
                                                maxsplit=maxsplit,
                                                reverse=reverse,
                                                separate=separate,
                                                strip=strip,
                                                ))
                                            if want_prints: # pragma: no cover
                                                print(f"{as_bytes=} {use_leading=} {use_trailing=}")
                                                print(f"multisplit({input_string!r}, separators={printable_separators(separators)}, {keep=}, {separate=}, {strip=}, {reverse=}, {maxsplit=})")
                                                print(f"  {result=}")
                                                print(f"{expected=}")
                                                print("________")
                                                print()
                                            self.assertEqual(result, expected, f"{as_bytes=} {use_leading=} {use_trailing=} multisplit({input_string=}, separators={printable_separators(separators)}, {keep=}, {separate=}, {strip=}, {reverse=}, {maxsplit=})")


        test_string = [
            ' ',
            'a',
            ' ',
            'b',
            ' ',
            'c',
            ' ',
            ]

        multisplit_tester(
            *test_string,
            (' ',),
            )

        multisplit_tester(
            *test_string,
            None,
            )


        multisplit_tester(
            ' ',
            '\t',
            ' ',
            '\n',
            ' ',

            'a',

            ' ',
            '\t',
            ' ',
            '\n',

            'b',

            '\t',
            ' ',
            '\n',

            'c',

            ' ',
            ' ',
            '\n',

            big.whitespace,
            )


        multisplit_tester(
            'x',
            'y',
            'x',
            'y',

            'a',

            'x',
            'y',
            'x',
            'y',
            'x',

            'b',

            'y',

            'c',

            'x',
            'y',
            'x',
            'y',
            'x',
            'y',

            'd',

            'y',
            'x',

            'e',

            'y',
            'y',
            'y',
            'y',

            'f',

            'x',
            'x',
            'x',
            'x',
            'x',
            'x',

            ('x', 'y'),
            )

    def test_multipartition(self):
        def test_multipartition(s, separator, count, expected, *, reverse=False):
            for _ in range(2):
                if _ == 1:
                    # encode!
                    s = s.encode('ascii')
                    separator = separator.encode('ascii')
                    expected = big.text._cheap_encode_iterable_of_strings(expected)

                # print()
                separators = (separator,)
                # print(f"multipartition({s=}, {separators=}, {count=}, *, {reverse=}):")
                # print(f"    {expected=}")
                got = big.multipartition(s, separators, count, reverse=reverse)
                # print(f"    {got!r}")
                self.assertEqual(expected, got)

        test_multipartition("a:b:c:d", ":", 0, ("a:b:c:d",))
        test_multipartition("a:b:c:d", ":", 1, ("a", ":", "b:c:d"))
        test_multipartition("a:b:c:d", ":", 2, ("a", ":", "b", ":", "c:d"))
        test_multipartition("a:b:c:d", ":", 3, ("a", ":", "b", ":", "c", ":", "d"))
        test_multipartition("a:b:c:d", ":", 4, ("a", ":", "b", ":", "c", ":", "d", '', ''))
        test_multipartition("a:b:c:d", ":", 5, ("a", ":", "b", ":", "c", ":", "d", '', '', '', ''))

        test_multipartition("a:b:c:d", ":", 0, ("a:b:c:d",), reverse=True)
        test_multipartition("a:b:c:d", ":", 1, ("a:b:c", ':' ,"d"), reverse=True)
        test_multipartition("a:b:c:d", ":", 2, ("a:b", ":", "c", ':' ,"d"), reverse=True)
        test_multipartition("a:b:c:d", ":", 3, ("a", ":", "b", ":", "c", ':' ,"d"), reverse=True)
        test_multipartition("a:b:c:d", ":", 4, ("", "", "a", ":", "b", ":", "c", ':' ,"d"), reverse=True)
        test_multipartition("a:b:c:d", ":", 5, ("", "", "", "", "a", ":", "b", ":", "c", ':' ,"d"), reverse=True)

        test_multipartition("a:b:c:d", "x", 1, ("a:b:c:d", "", ""))
        test_multipartition("a:b:c:d", "x", 0, ("a:b:c:d",))
        test_multipartition("a:b:c:d", "x", 2, ("a:b:c:d", "", "", "", ""))
        test_multipartition("a:b:c:d", "x", 3, ("a:b:c:d", "", "", "", "", "", ""))

        test_multipartition("a:b:c:d", "x", 0, ("a:b:c:d",), reverse=True)
        test_multipartition("a:b:c:d", "x", 1, ("", "", "a:b:c:d"), reverse=True)
        test_multipartition("a:b:c:d", "x", 2, ("", "", "", "", "a:b:c:d"), reverse=True)
        test_multipartition("a:b:c:d", "x", 3, ("", "", "", "", "", "", "a:b:c:d"), reverse=True)

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
        test("don't come home if you don't get 1st", "Don't Come Home If You Don't Get 1st")
        test("""i said "no, i didn't", you idiot""", """I Said "No, I Didn't", You Idiot""")
        test('multiple «"“quote marks”"»', 'Multiple «"“Quote Marks”"»')

    def test_normalize_whitespace(self):
        def test(s, expected, *, separators=None, replacement=" "):
            result = big.normalize_whitespace(s, separators=separators, replacement=replacement)
            self.assertEqual(result, expected)

            s = s.encode('ascii')
            expected = expected.encode('ascii')
            if separators:
                separators = [s.encode('ascii') for s in separators]
            if replacement:
                replacement = replacement.encode('ascii')

            result = big.normalize_whitespace(s, separators=separators, replacement=replacement)
            self.assertEqual(result, expected)

        test("   a    b    c", " a b c")

        test("d     e  \t\n  f ", "d e f ")
        test("ghi", "ghi", replacement=None)
        test("   j     kl   mnop    ", " j kl mnop ")
        test("", "")
        test("   \n\n\t \t     ", " ")

        test("   j     kl   mnop    ", "XjXklXmnopX", replacement="X")
        test("   j     kl   mnop    ", "QQjQQklQQmnopQQ", replacement="QQ")

        test("abcDEFabacabGHIaaa", "+DEF+GHI+", separators=("a", "b", "c"), replacement="+")

        with self.assertRaises(ValueError):
            big.multipartition("abc", "b", -1)

    def test_split_quoted_strings(self):
        def test(s, expected, **kwargs):
            got = list(big.split_quoted_strings(s, **kwargs))
            self.assertEqual(got, expected)

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


    def test_lines(self):
        def test(i, expected):
            got = list(i)
            self.assertEqual(got, expected)

        LI = big.LineInfo

        test(big.lines("a\nb\nc\nd\ne\n"),
            [
            (LI('a', 1, 1), 'a'),
            (LI('b', 2, 1), 'b'),
            (LI('c', 3, 1), 'c'),
            (LI('d', 4, 1), 'd'),
            (LI('e', 5, 1), 'e'),
            (LI('',  6, 1), ''),
            ])

        lines = ['first line', '\tsecond line', 'third line']
        test(big.lines_strip(big.lines(lines)),
            [
            (LI('first line', 1, 1), 'first line'),
            (LI('\tsecond line', 2, 9, leading='\t'), 'second line'),
            (LI('third line', 3, 1), 'third line'),
            ])

        test(big.lines_filter_comment_lines(big.lines("""
    # comment
    a = b
    // another comment
    c = d
    / not a comment
    /// is a comment!
    ## another comment!
    #! a third comment!
""".lstrip('\n')), ('#', '//')),
            [
            (LI('    a = b',           2, 1), '    a = b'),
            (LI('    c = d',           4, 1), '    c = d'),
            (LI('    / not a comment', 5, 1), '    / not a comment'),
            (LI('',                    9, 1), ''),
            ])

        test(big.lines_rstrip(big.lines(
"    a = b  \n"
"    c = d     \n"
)),
            [
            (LI('    a = b  ',    1, 1), '    a = b'),
            (LI('    c = d     ', 2, 1), '    c = d'),
            (LI('',               3, 1), ''),
            ])

        test(big.lines_strip(big.lines(
"    a = b  \n"
"    c = d     \n"
)),
            [
            (LI('    a = b  ',    1, 5, leading='    '), 'a = b'),
            (LI('    c = d     ', 2, 5, leading='    '), 'c = d'),
            (LI('',               3, 1), ''),
            ])

        test(big.lines_filter_empty_lines(big.lines("""

    a = b


    c = d

"""[1:])),
            [
            (LI('    a = b', 2, 1), '    a = b'),
            (LI('    c = d', 5, 1), '    c = d'),
            ])

        test(big.lines_convert_tabs_to_spaces(big.lines(
            "\tfirst line\n"
            "\t\tsecond line\n"
            "  \tthird line\n",
            tab_width=8)),
            [
                (LI("\tfirst line", 1, 1), "        first line"),
                (LI("\t\tsecond line", 2, 1), "                second line"),
                (LI("  \tthird line", 3, 1), "        third line"),
                (LI("", 4, 1), ""),
            ])

        test(big.lines_strip_comments(big.lines("""
for x in range(5): # this is a comment
    print("# this is quoted", x)
    print("") # this "comment" is useless
    print(no_comments_or_quotes_on_this_line)
"""[1:]), ("#", "//")),
            [
                (LI(line='for x in range(5): # this is a comment', line_number=1, column_number=1, comment='# this is a comment'),
                    'for x in range(5):'),
                (LI(line='    print("# this is quoted", x)', line_number=2, column_number=1, comment=''),
                    '    print("# this is quoted", x)'),
                (LI(line='    print("") # this "comment" is useless', line_number=3, column_number=1, comment='# this "comment" is useless'),
                    '    print("")'),
                (LI(line='    print(no_comments_or_quotes_on_this_line)', line_number=4, column_number=1, comment=''),
                    '    print(no_comments_or_quotes_on_this_line)'),
                (LI(line='', line_number=5, column_number=1, comment=''),
                    '')
            ])

        test(big.lines_strip_comments(big.lines("""
for x in range(5): # this is a comment
    print("# this is quoted", x)
    print("") # this "comment" is useless
    print(no_comments_or_quotes_on_this_line)
"""[1:]), ("#", "//"), quotes=None),
            [
                (LI(line='for x in range(5): # this is a comment', line_number=1, column_number=1, comment='# this is a comment'),
                  'for x in range(5):'),
                (LI(line='    print("# this is quoted", x)', line_number=2, column_number=1, comment='# this is quoted", x)'),
                    '    print("'),
                (LI(line='    print("") # this "comment" is useless', line_number=3, column_number=1, comment='# this "comment" is useless'),
                    '    print("")'),
                (LI(line='    print(no_comments_or_quotes_on_this_line)', line_number=4, column_number=1, comment=''),
                    '    print(no_comments_or_quotes_on_this_line)'),
                (LI(line='', line_number=5, column_number=1, comment=''),
                    ''),
            ])

        with self.assertRaises(ValueError):
            test(big.lines_strip_comments(big.lines("a\nb\n"), None), [])



        test(big.lines_filter_empty_lines(big.lines_filter_comment_lines(big.lines_strip(big.lines(
"   \n" +
"    a = b \n" +
"   \n" +
"    # comment line \n" +
"    \n" +
"    \n" +
"    c = d  \n" +
"     \n")), '#')),
            [
            (LI('    a = b ',  2, 5, leading='    '), 'a = b'),
            (LI('    c = d  ', 7, 5, leading='    '), 'c = d'),
            ])


    def test_lines_strip_indent(self):
        def test(lines, expected, *, tab_width=8):
            got = list(big.lines_strip_indent(big.lines(lines, tab_width=tab_width)))
            self.assertEqual(got, expected)


        from big import LineInfo

        lines = """
left margin
if 3:
    text
else:
    if 1:
          other text
          other text
    more text
      different indent
    outdent
outdent
  new indent
outdent
"""

        expected = [
            (LineInfo(line='', line_number=1, column_number=1, indent=0, leading=''),
                ''),
            (LineInfo(line='left margin', line_number=2, column_number=1, indent=0, leading=''),
                'left margin'),
            (LineInfo(line='if 3:', line_number=3, column_number=1, indent=0, leading=''),
                'if 3:'),
            (LineInfo(line='    text', line_number=4, column_number=5, indent=1, leading='    '),
                'text'),
            (LineInfo(line='else:', line_number=5, column_number=1, indent=0, leading=''),
                'else:'),
            (LineInfo(line='    if 1:', line_number=6, column_number=5, indent=1, leading='    '),
                'if 1:'),
            (LineInfo(line='          other text', line_number=7, column_number=11, indent=2, leading='          '),
                'other text'),
            (LineInfo(line='          other text', line_number=8, column_number=11, indent=2, leading='          '),
                'other text'),
            (LineInfo(line='    more text', line_number=9, column_number=5, indent=1, leading='    '),
                'more text'),
            (LineInfo(line='      different indent', line_number=10, column_number=7, indent=2, leading='      '),
                'different indent'),
            (LineInfo(line='    outdent', line_number=11, column_number=5, indent=1, leading='    '),
                'outdent'),
            (LineInfo(line='outdent', line_number=12, column_number=1, indent=0, leading=''),
                'outdent'),
            (LineInfo(line='  new indent', line_number=13, column_number=3, indent=1, leading='  '),
                'new indent'),
            (LineInfo(line='outdent', line_number=14, column_number=1, indent=0, leading=''),
                'outdent'),
            (LineInfo(line='', line_number=15, column_number=1, indent=0, leading=''),
                ''),
            ]

        test(lines, expected)


        ##
        ## test tab to spaces
        ##

        lines = (
        "left margin\n"
        "\teight\n"
        "  \t    twelve\n"
        "        eight is enough\n"
        )

        expected = [
            (LineInfo(line='left margin', line_number=1, column_number=1, indent=0, leading=''),
                'left margin'),
            (LineInfo(line='\teight', line_number=2, column_number=9, indent=1, leading='\t'),
                'eight'),
            (LineInfo(line='  \t    twelve', line_number=3, column_number=13, indent=2, leading='  \t    '),
                'twelve'),
            (LineInfo(line='        eight is enough', line_number=4, column_number=9, indent=1, leading='        '),
                'eight is enough'),
            (LineInfo(line='', line_number=5, column_number=1, indent=0, leading=''),
                '')
            ]

        test(lines, expected)

        lines = (
            "left margin\n"
            "\tfour\n"
            "  \t    eight\n"
            "  \t\tfigure eight is double four\n"
            "    figure four is half of eight\n"
            )

        expected = [
            (LineInfo(line='left margin', line_number=1, column_number=1, indent=0, leading=''),
                'left margin'),
            (LineInfo(line='\tfour', line_number=2, column_number=5, indent=1, leading='\t'),
                'four'),
            (LineInfo(line='  \t    eight', line_number=3, column_number=9, indent=2, leading='  \t    '),
                'eight'),
            (LineInfo(line='  \t\tfigure eight is double four', line_number=4, column_number=9, indent=2, leading='  \t\t'),
                'figure eight is double four'),
            (LineInfo(line='    figure four is half of eight', line_number=5, column_number=5, indent=1, leading='    '),
                'figure four is half of eight'),
            (LineInfo(line='', line_number=6, column_number=1, indent=0, leading=''),
                '')]

        test(lines, expected, tab_width=4)

        ##
        ## test raising for illegal outdents
        ##

        # when it's between two existing indents
        lines = (
            "left margin\n"
            "\tfour\n"
            "  \t    eight\n"
            "      six?!\n"
            "left margin again\n"
            )

        with self.assertRaises(IndentationError):
            test(lines, [], tab_width=4)


        # when it's less than the first indent
        lines = (
            "left margin\n"
            "\tfour\n"
            "  \t    eight\n"
            "  two?!\n"
            "left margin again\n"
            )

        with self.assertRaises(IndentationError):
            test(lines, [], tab_width=4)

        with self.assertRaises(ValueError):
            test("first line\n  \u3000  second line\nthird line\n", [])

    def test_lines_misc(self):
        ## repr
        li = big.LineInfo('', 1, 1, indent=0)
        self.assertEqual(repr(li), "LineInfo(line='', line_number=1, column_number=1, indent=0)")

        ## error handling
        with self.assertRaises(TypeError):
            big.lines("", line_number=math.pi)
        with self.assertRaises(TypeError):
            big.lines("", column_number=math.pi)
        with self.assertRaises(TypeError):
            big.lines("", tab_width=math.pi)

        with self.assertRaises(TypeError):
            big.LineInfo(math.pi, 1, 1)
        with self.assertRaises(TypeError):
            big.LineInfo('', math.pi, 1)
        with self.assertRaises(TypeError):
            big.LineInfo('', 1, math.pi)

        with self.assertRaises(ValueError):
            list(big.lines_filter_comment_lines("", []))
        with self.assertRaises(TypeError):
            list(big.lines_filter_comment_lines("", math.pi))

        ## test kwargs
        i = big.lines('', quark=22)
        self.assertTrue(hasattr(i, 'quark'))
        self.assertEqual(getattr(i, 'quark'), 22)

        info = big.LineInfo('', 1, 1, quark=35)
        self.assertTrue(hasattr(info, 'quark'))
        self.assertEqual(getattr(info, 'quark'), 35)



import bigtestlib

def run_tests():
    bigtestlib.run(name="big.text", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
