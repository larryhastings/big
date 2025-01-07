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
big_dir = bigtestlib.preload_local_big()

import big.all as big
import glob
import os.path
from pathlib import Path
import re
import shutil
import tempfile
import time
import unittest


def unchanged(o):
    return o

def to_bytes(o):
    if isinstance(o, str):
        return o.encode('ascii')
    if isinstance(o, list):
        return [to_bytes(x) for x in o]
    if isinstance(o, tuple):
        return tuple(to_bytes(x) for x in o)
    return o

class BigFileTests(unittest.TestCase):

    def test_grep(self):
        test_dir = os.path.dirname(__file__)
        grepfile = os.path.join(test_dir, "grepfile")
        for c in (unchanged, to_bytes):
            self.assertEqual(big.grep(c(grepfile), c("b")), c(['bbbb', 'abc']))
            self.assertEqual(big.grep(c(grepfile), c("b"), enumerate=True), c([(2, 'bbbb'), (3, 'abc')]))

            self.assertEqual(big.grep(c(grepfile), c("[bc]")), c(['bbbb', 'abc', 'cccc']))
            self.assertEqual(big.grep(c(grepfile), re.compile(c("[bc]"))), c(['bbbb', 'abc', 'cccc']))

            self.assertEqual(big.grep(c(grepfile), c("b"), flags=re.I), c(['bbbb', 'abc', 'BBBB', 'ABC']))
            self.assertEqual(big.grep(c(grepfile), c("B"), flags=re.I), c(['bbbb', 'abc', 'BBBB', 'ABC']))
            self.assertEqual(big.grep(c(grepfile), c("b"), flags=re.I, enumerate=True), c([(2, 'bbbb'), (3, 'abc'), (7, 'BBBB'), (8, 'ABC')]))

            p = Path(grepfile)
            self.assertEqual(big.grep(p, c("b")), c(['bbbb', 'abc']))

        with self.assertRaises(ValueError):
            self.assertEqual(big.grep(p, b"b", encoding="utf-8"))

    def test_fgrep(self):
        test_dir = os.path.dirname(__file__)
        grepfile = os.path.join(test_dir, "grepfile")
        for c in (unchanged, to_bytes):
            self.assertEqual(big.fgrep(c(grepfile), c("b")), c(['bbbb', 'abc']))
            self.assertEqual(big.fgrep(c(grepfile), c("b"), case_insensitive=True), c(['bbbb', 'abc', 'BBBB', 'ABC']))
            self.assertEqual(big.fgrep(c(grepfile), c("B"), case_insensitive=True), c(['bbbb', 'abc', 'BBBB', 'ABC']))
            self.assertEqual(big.fgrep(c(grepfile), c("b"), enumerate=True), c([(2, 'bbbb'), (3, 'abc')]))
            self.assertEqual(big.fgrep(c(grepfile), c("b"), case_insensitive=True, enumerate=True), c([(2, 'bbbb'), (3, 'abc'), (7, 'BBBB'), (8, 'ABC')]))
            p = Path(grepfile)
            self.assertEqual(big.fgrep(p, c("b")), c(['bbbb', 'abc']))

        with self.assertRaises(ValueError):
            self.assertEqual(big.fgrep(p, b"b", encoding="utf-8"))

    def test_pushd(self):
        cwd = os.getcwd()
        with big.pushd(".."):
            self.assertEqual(os.getcwd(), os.path.dirname(cwd))
        self.assertEqual(os.getcwd(), cwd)

class BigFileTmpdirTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="bigtest")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_safe_mkdir(self):
        # newdir points to a directory that doesn't exist yet
        newdir = os.path.join(self.tmpdir, "newdir")
        self.assertFalse(os.path.isdir(newdir))

        # mkdir and check that it worked
        big.safe_mkdir(newdir)
        self.assertTrue(os.path.isdir(newdir))

        # doing it a second time does nothing
        big.safe_mkdir(newdir)
        self.assertTrue(os.path.isdir(newdir))

        # test unlinking a file
        y = os.path.join(self.tmpdir, "y")
        with open(y, "wt") as f:
            f.write("x")
        big.safe_mkdir(y)
        self.assertTrue(os.path.isdir(y))

        # make a file named 'x', then ask to
        # safe_mkdir 'x/y'
        newfile = os.path.join(self.tmpdir, "newfile")
        with open(newfile, "wt") as f:
            f.write("x")
        newsubfile = os.path.join(newfile, 'y')
        with self.assertRaises(NotADirectoryError):
            big.safe_mkdir(newsubfile)

    def test_safe_unlink(self):
        newfile = os.path.join(self.tmpdir, "newfile")
        self.assertFalse(os.path.isfile(newfile))
        big.safe_unlink(newfile)
        with open(newfile, "wt") as f:
            f.write("x")
        self.assertTrue(os.path.isfile(newfile))
        big.safe_unlink(newfile)
        self.assertFalse(os.path.isfile(newfile))
        big.safe_unlink(newfile)
        self.assertFalse(os.path.isfile(newfile))


    def test_file_size(self):
        newfile = os.path.join(self.tmpdir, "newfile")
        with self.assertRaises(FileNotFoundError):
            big.file_size(newfile)
        with open(newfile, "wt") as f:
            f.write("abcdefgh")
        self.assertEqual(big.file_size(newfile), 8)

    def test_file_mtime(self):
        newfile = os.path.join(self.tmpdir, "newfile")
        with self.assertRaises(FileNotFoundError):
            big.file_mtime(newfile)
        with open(newfile, "wt") as f:
            f.write("abcdefgh")
        self.assertGreater(big.file_mtime(newfile), big.file_mtime(__file__))

    def test_file_mtime_ns(self):
        newfile = os.path.join(self.tmpdir, "newfile")
        with self.assertRaises(FileNotFoundError):
            big.file_mtime_ns(newfile)
        with open(newfile, "wt") as f:
            f.write("abcdefgh")
        self.assertGreater(big.file_mtime_ns(newfile), big.file_mtime_ns(__file__))

    def test_touch(self):
        firstfile = os.path.join(self.tmpdir, "firstfile")
        with open(firstfile, "wt") as f:
            f.write("abcdefgh")
        st = os.stat(firstfile)
        newfile = os.path.join(self.tmpdir, "newfile")
        self.assertFalse(os.path.isfile(newfile))
        big.touch(newfile)
        self.assertTrue(os.path.isfile(newfile))
        self.assertGreater(big.file_mtime_ns(newfile), big.file_mtime_ns(__file__))
        newfile2 = newfile + "2"
        big.touch(newfile2)
        time_in_the_past = big.file_mtime_ns(newfile) - 2**32
        os.utime(newfile2, ns=(time_in_the_past, time_in_the_past))
        self.assertGreaterEqual(big.file_mtime_ns(newfile), big.file_mtime_ns(newfile2))
        time.sleep(0.01)
        big.touch(newfile2)
        self.assertGreater(big.file_mtime_ns(newfile2), big.file_mtime_ns(newfile))

    def test_translate_filename_to_exfat(self):
        self.assertEqual(big.translate_filename_to_exfat("abcde"), "abcde")
        before = 'abc\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f/\\:*?": <>|xyz'
        after = "abc@?01?02?03?04?05?06?07?08?09?0a?0b?0c?0d?0e?0f?10?11?12?13?14?15?16?17?18?19?1a?1b?1c?1d?1e?1f--.@.' - {}!xyz"
        self.assertEqual(big.translate_filename_to_exfat(before), after)

        with self.assertRaises(ValueError):
            big.translate_filename_to_exfat(35)

    def test_translate_filename_to_unix(self):
        self.assertEqual(big.translate_filename_to_unix("abcde"), "abcde")
        self.assertEqual(big.translate_filename_to_unix('ab\x00de/fg'), 'ab@de-fg')

        with self.assertRaises(ValueError):
            big.translate_filename_to_unix(35)

    def test_read_python_file(self):
        """
        I don't need to write any read_python_file tests here.
        It's given a thorough workout elsewhere in the unit test suite:
                file tests/test_text.py
            function test_python_delimiters_on_big_source_tree()

        Also, it's a thin wrapper around decode_python_script,
        which also gets a nice workout:
                file tests/test_text.py
            function test_decode_python_script()
        """
        pass

    def test_search_path(self):
        # ensure that glob.escape and normcase are composable in either order
        # (they should be)
        self.assertEqual(
            os.path.normcase( glob.escape("AbC*") ),
            glob.escape( os.path.normcase("AbC*") ),
            )

        with big.pushd(big_dir / "tests"):

            foo_d   = Path("test_search_path/foo_d_path/foo.d")
            foo_h   = Path("test_search_path/foo_h_path/foo.h")
            foo_hpp = Path("test_search_path/foo_h_path/foo.hpp")
            foobar  = Path("test_search_path/file_without_extension/foobar")
            mydir   = Path("test_search_path/want_directories/mydir")

            search = big.search_path(
                ["test_search_path/foo_h_path", "test_search_path/foo_d_path"],
                ('.D',),
                preserve_extension=False,
                case_sensitive=False,
                want_directories=True,
                )
            self.assertEqual(search('nonexists'), None)
            self.assertEqual(search('foo'), foo_d)
            self.assertEqual(search('foo.d'), None)

            search = big.search_path(
                ["test_search_path/foo_h_path", "test_search_path/foo_d_path"],
                ('', '.D'),
                preserve_extension=True,
                case_sensitive=False,
                want_directories=True,
                )
            self.assertEqual(search('foo'), foo_d)
            self.assertEqual(search('foo.d'), foo_d)

            search = big.search_path(
                ["test_search_path/foo_h_path", "test_search_path/foo_d_path"],
                ('.D',),
                preserve_extension=True,
                case_sensitive=False,
                want_directories=True,
                )
            self.assertEqual(search('foo'), foo_d)
            self.assertEqual(search('foo.d'), foo_d)

            search = big.search_path(
                ["test_search_path/foo_h_path", "test_search_path/foo_d_path"],
                ('.D',),
                preserve_extension=True,
                case_sensitive=False,
                want_directories=False,
                )
            self.assertEqual(search('foo'), None)
            self.assertEqual(search('foo.d'), None)

            search = big.search_path(
                ["test_search_path/foo_d_path", "test_search_path/foo_h_path"],
                ('.H',),
                preserve_extension=True,
                case_sensitive=False,
                want_directories=False,
                )
            self.assertEqual(search('foo'), foo_h)
            self.assertEqual(search('foo.h'), foo_h)

            foo_h = Path("test_search_path/foo_h_path/foo.h")
            search = big.search_path(
                ["test_search_path/foo_d_path", "test_search_path/foo_h_path"],
                ('.H',),
                preserve_extension=False,
                case_sensitive=False,
                want_directories=False,
                )
            self.assertEqual(search('foo'), foo_h)
            self.assertEqual(search('foo.h'), None)

            search = big.search_path(
                ["test_search_path/foo_d_path", "test_search_path/foo_h_path"],
                ('.H',),
                preserve_extension=True,
                case_sensitive=True,
                want_directories=False,
                )
            self.assertEqual(search('foo'), None)
            self.assertEqual(search('foo.h'), None)

            search = big.search_path(
                ["test_search_path/foo_d_path", "test_search_path/foo_h_path"],
                ('.h',),
                preserve_extension=True,
                want_directories=False,
                )
            self.assertEqual(search('foo'), foo_h)
            self.assertEqual(search('foo.h'), foo_h)

            search = big.search_path(
                ["nonexistent_dir", "test_search_path/foo_d_path", "test_search_path/foo_h_path"],
                ('.h',),
                preserve_extension=True,
                want_directories=True,
                want_files=False,
                )
            self.assertEqual(search('foo'), None)
            self.assertEqual(search('foo.h'), None)

            search = big.search_path(
                ["test_search_path/this_file_doesnt_match_anything", "test_search_path/foo_d_path", "test_search_path/foo_h_path"],
                ('.h', '.hpp'),
                preserve_extension=True,
                )
            self.assertEqual(search('foo'), foo_h)
            self.assertEqual(search('foo.h'), foo_h)
            self.assertEqual(search('foo.hpp'), foo_hpp)

            search = big.search_path(
                ["test_search_path/foo_d_path", "test_search_path/foo_h_path", "test_search_path/file_without_extension"],
                ('.x', '.xyz', '',),
                preserve_extension=True,
                )
            self.assertEqual(search('foobar'), foobar)
            self.assertEqual(search('foo.h'), foo_h)
            self.assertEqual(search('foo.hpp'), foo_hpp)

            search = big.search_path(
                ["test_search_path/foo_d_path", "test_search_path/want_directories"],
                ('.x', '.xyz', '',),
                preserve_extension=True,
                want_directories=True,
                want_files=False
                )
            self.assertEqual(search('mydir'), mydir)
            self.assertEqual(search('yourdir'), None)

            with self.assertRaises(ValueError):
                big.search_path(("a", "b", "c"), want_files=False, want_directories=False)
            with self.assertRaises(ValueError):
                big.search_path([])
            with self.assertRaises(ValueError):
                big.search_path(("a", "b", "c"), [])
            with self.assertRaises(ValueError):
                big.search_path(("a", "b", "c"), ('.a', 33))
            with self.assertRaises(ValueError):
                big.search_path(("a", "b", "c"), ('.a', 'bcd'))
            with self.assertRaises(ValueError):
                big.search_path(("a", "b", "c"), ('.a', '', '.bcd', ''))

            with self.assertRaises(ValueError):
                search("foobar/")

            with tempfile.TemporaryDirectory() as tmp:
                tmp = Path(tmp)
                lower = tmp / "filename.h"
                upper = tmp / "FILENAME.h"
                big.touch(lower)
                if not upper.exists():
                    big.touch(upper)

                    search = big.search_path([tmp], ['.h', ''], case_sensitive=False)
                    with self.assertRaises(ValueError):
                        search("fIlEnAmE")
                    search = big.search_path([tmp], case_sensitive=False)
                    with self.assertRaises(ValueError):
                        search("fIlEnAmE.h")

def run_tests():
    bigtestlib.run(name="big.file", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
