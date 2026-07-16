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

from big.test import raises

import big.all as big
import contextlib
import glob
import os.path
from pathlib import Path
import re
import shutil
import tempfile
import time


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

def test_grep():
    test_dir = os.path.dirname(__file__)
    grepfile = os.path.join(test_dir, "grepfile")
    for c in (unchanged, to_bytes):
        assert big.grep(c(grepfile), c("b")) == c(['bbbb', 'abc'])
        assert big.grep(c(grepfile), c("b"), enumerate=True) == c([(2, 'bbbb'), (3, 'abc')])

        assert big.grep(c(grepfile), c("[bc]")) == c(['bbbb', 'abc', 'cccc'])
        assert big.grep(c(grepfile), re.compile(c("[bc]"))) == c(['bbbb', 'abc', 'cccc'])

        assert big.grep(c(grepfile), c("b"), flags=re.I) == c(['bbbb', 'abc', 'BBBB', 'ABC'])
        assert big.grep(c(grepfile), c("B"), flags=re.I) == c(['bbbb', 'abc', 'BBBB', 'ABC'])
        assert big.grep(c(grepfile), c("b"), flags=re.I, enumerate=True) == c([(2, 'bbbb'), (3, 'abc'), (7, 'BBBB'), (8, 'ABC')])

        # case_insensitive=True is the convenience knob, symmetric with fgrep
        assert big.grep(c(grepfile), c("b"), case_insensitive=True) == c(['bbbb', 'abc', 'BBBB', 'ABC'])
        assert big.grep(c(grepfile), c("B"), case_insensitive=True) == c(['bbbb', 'abc', 'BBBB', 'ABC'])
        assert big.grep(c(grepfile), c("b"), case_insensitive=True, enumerate=True) == c([(2, 'bbbb'), (3, 'abc'), (7, 'BBBB'), (8, 'ABC')])

        # case_insensitive=None (the default) makes no effort either way
        assert big.grep(c(grepfile), c("b"), case_insensitive=None) == c(['bbbb', 'abc'])

        # a precompiled pattern: None leaves its flags alone, True adds
        # IGNORECASE, False strips it (even though it was compiled with it)
        assert big.grep(c(grepfile), re.compile(c("b"), re.I)) == c(['bbbb', 'abc', 'BBBB', 'ABC'])
        assert big.grep(c(grepfile), re.compile(c("b"), re.I), case_insensitive=None) == c(['bbbb', 'abc', 'BBBB', 'ABC'])
        assert big.grep(c(grepfile), re.compile(c("b")), case_insensitive=True) == c(['bbbb', 'abc', 'BBBB', 'ABC'])
        assert big.grep(c(grepfile), re.compile(c("b"), re.I), case_insensitive=False) == c(['bbbb', 'abc'])

        # case_insensitive wins over a conflicting flags argument
        assert big.grep(c(grepfile), c("b"), flags=re.I, case_insensitive=False) == c(['bbbb', 'abc'])

        p = Path(grepfile)
        assert big.grep(p, c("b")) == c(['bbbb', 'abc'])

    with raises(ValueError):
        big.grep(p, b"b", encoding="utf-8")

def test_fgrep():
    test_dir = os.path.dirname(__file__)
    grepfile = os.path.join(test_dir, "grepfile")
    for c in (unchanged, to_bytes):
        assert big.fgrep(c(grepfile), c("b")) == c(['bbbb', 'abc'])
        assert big.fgrep(c(grepfile), c("b"), case_insensitive=True) == c(['bbbb', 'abc', 'BBBB', 'ABC'])
        assert big.fgrep(c(grepfile), c("B"), case_insensitive=True) == c(['bbbb', 'abc', 'BBBB', 'ABC'])
        assert big.fgrep(c(grepfile), c("b"), enumerate=True) == c([(2, 'bbbb'), (3, 'abc')])
        assert big.fgrep(c(grepfile), c("b"), case_insensitive=True, enumerate=True) == c([(2, 'bbbb'), (3, 'abc'), (7, 'BBBB'), (8, 'ABC')])
        p = Path(grepfile)
        assert big.fgrep(p, c("b")) == c(['bbbb', 'abc'])

    with raises(ValueError):
        big.fgrep(p, b"b", encoding="utf-8")

def test_fgrep_and_grep_binary_crlf():
    # regression: binary mode split only on b'\n', so CRLF files
    # yielded lines with trailing \r (and a phantom empty final
    # "line" after the trailing newline)
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        p = os.path.join(tmpdir, "crlf.txt")
        with open(p, "wb") as f:
            f.write(b"alpha\r\nbeta\r\ngamma\r\n")
        assert big.fgrep(p, b"a") == [b"alpha", b"beta", b"gamma"]
        assert big.fgrep(p, b"alph") == [b"alpha"]
        assert big.grep(p, rb"^beta$") == [b"beta"]
        # old CR-only files work too
        p2 = os.path.join(tmpdir, "cr.txt")
        with open(p2, "wb") as f:
            f.write(b"one\rtwo\r")
        assert big.fgrep(p2, b"o") == [b"one", b"two"]

        # text mode splits on big's full definition of linebreaks
        # (str.splitlines' set): \v, \f, etc. count too
        p3 = os.path.join(tmpdir, "vtab.txt")
        with open(p3, "wt", newline='') as f:
            f.write("one\vtwo\nthree\n")
        assert big.fgrep(p3, "o") == ["one", "two"]
        assert big.fgrep(p3, "t") == ["two", "three"]
        assert big.grep(p3, r"^t") == ["two", "three"]

def test_fgrep_case_insensitive_casefolds():
    # str.casefold, not str.lower: 'ß' folds to 'ss'
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        p = os.path.join(tmpdir, "eszett.txt")
        with open(p, "wt", encoding="utf-8") as f:
            f.write("die stra\N{LATIN SMALL LETTER SHARP S}e\nnothing here\n")
        matches = big.fgrep(p, "STRASSE", encoding="utf-8", case_insensitive=True)
        assert matches == ["die stra\N{LATIN SMALL LETTER SHARP S}e"]

def test_pushd():
    cwd = os.getcwd()
    with big.pushd(".."):
        assert os.getcwd() == os.path.dirname(cwd)
    assert os.getcwd() == cwd

def test_pushd_captures_cwd_at_enter():
    # the original directory is captured when the block is
    # entered, not when the pushd object is constructed
    cwd = os.getcwd()
    parent = os.path.dirname(cwd)
    grandparent = os.path.dirname(parent)
    try:
        p = big.pushd(grandparent)   # constructed HERE...
        os.chdir(parent)             # ...but entered from parent
        with p:
            assert os.getcwd() == grandparent
        assert os.getcwd() == parent   # restored to entry point

        # and a pushd object is reusable
        os.chdir(cwd)
        with p:
            assert os.getcwd() == grandparent
        assert os.getcwd() == cwd
    finally:
        os.chdir(cwd)


@contextlib.contextmanager
def setup():
    tmpdir = tempfile.mkdtemp(prefix="bigtest")
    try:
        yield tmpdir
    finally:
        shutil.rmtree(tmpdir)

def test_safe_mkdir():
    with setup() as tmpdir:
        # newdir points to a directory that doesn't exist yet
        newdir = os.path.join(tmpdir, "newdir")
        assert not (os.path.isdir(newdir))

        # mkdir and check that it worked
        big.safe_mkdir(newdir)
        assert os.path.isdir(newdir)

        # doing it a second time does nothing
        big.safe_mkdir(newdir)
        assert os.path.isdir(newdir)

        # test unlinking a file
        y = os.path.join(tmpdir, "y")
        with open(y, "wt") as f:
            f.write("x")
        big.safe_mkdir(y)
        assert os.path.isdir(y)

        # make a file named 'x', then ask to
        # safe_mkdir 'x/y'
        newfile = os.path.join(tmpdir, "newfile")
        with open(newfile, "wt") as f:
            f.write("x")
        newsubfile = os.path.join(newfile, 'y')
        with raises(NotADirectoryError):
            big.safe_mkdir(newsubfile)

def test_safe_mkdir_and_unlink_with_symlinks():
    with setup() as tmpdir:
        # regression: os.path.isfile is False for a dangling symlink,
        # so safe_mkdir raised FileExistsError and safe_unlink silently
        # left the debris in place
        dangling = os.path.join(tmpdir, "dangling")
        os.symlink(os.path.join(tmpdir, "no-such-target"), dangling)
        big.safe_mkdir(dangling)
        assert os.path.isdir(dangling)
        assert not (os.path.islink(dangling))

        dangling2 = os.path.join(tmpdir, "dangling2")
        os.symlink(os.path.join(tmpdir, "no-such-target"), dangling2)
        big.safe_unlink(dangling2)
        assert not (os.path.lexists(dangling2))

        # a symlink to a file counts as a file: safe_unlink removes
        # the link itself, never the target
        target = os.path.join(tmpdir, "target")
        with open(target, "wt") as f:
            f.write("x")
        filelink = os.path.join(tmpdir, "filelink")
        os.symlink(target, filelink)
        big.safe_unlink(filelink)
        assert not (os.path.lexists(filelink))
        assert os.path.isfile(target)

        # a symlink leading to a directory is left alone by both
        realdir = os.path.join(tmpdir, "realdir")
        os.mkdir(realdir)
        dirlink = os.path.join(tmpdir, "dirlink")
        os.symlink(realdir, dirlink)
        big.safe_mkdir(dirlink)
        assert os.path.islink(dirlink)
        big.safe_unlink(dirlink)
        assert os.path.islink(dirlink)

def test_safe_unlink():
    with setup() as tmpdir:
        newfile = os.path.join(tmpdir, "newfile")
        assert not (os.path.isfile(newfile))
        big.safe_unlink(newfile)
        with open(newfile, "wt") as f:
            f.write("x")
        assert os.path.isfile(newfile)
        big.safe_unlink(newfile)
        assert not (os.path.isfile(newfile))
        big.safe_unlink(newfile)
        assert not (os.path.isfile(newfile))

def test_file_size():
    with setup() as tmpdir:
        newfile = os.path.join(tmpdir, "newfile")
        with raises(FileNotFoundError):
            big.file_size(newfile)
        with open(newfile, "wt") as f:
            f.write("abcdefgh")
        assert big.file_size(newfile) == 8

def test_file_mtime():
    with setup() as tmpdir:
        newfile = os.path.join(tmpdir, "newfile")
        with raises(FileNotFoundError):
            big.file_mtime(newfile)
        with open(newfile, "wt") as f:
            f.write("abcdefgh")
        assert big.file_mtime(newfile) > big.file_mtime(__file__)

def test_file_mtime_ns():
    with setup() as tmpdir:
        newfile = os.path.join(tmpdir, "newfile")
        with raises(FileNotFoundError):
            big.file_mtime_ns(newfile)
        with open(newfile, "wt") as f:
            f.write("abcdefgh")
        assert big.file_mtime_ns(newfile) > big.file_mtime_ns(__file__)

def test_touch():
    with setup() as tmpdir:
        firstfile = os.path.join(tmpdir, "firstfile")
        with open(firstfile, "wt") as f:
            f.write("abcdefgh")
        st = os.stat(firstfile)
        newfile = os.path.join(tmpdir, "newfile")
        assert not (os.path.isfile(newfile))
        big.touch(newfile)
        assert os.path.isfile(newfile)
        assert big.file_mtime_ns(newfile) > big.file_mtime_ns(__file__)
        newfile2 = newfile + "2"
        big.touch(newfile2)
        time_in_the_past = big.file_mtime_ns(newfile) - 2**32
        os.utime(newfile2, ns=(time_in_the_past, time_in_the_past))
        assert big.file_mtime_ns(newfile) >= big.file_mtime_ns(newfile2)
        time.sleep(0.01)
        big.touch(newfile2)
        assert big.file_mtime_ns(newfile2) > big.file_mtime_ns(newfile)

def test_atomic_write():
    with setup() as tmpdir:
        target = os.path.join(tmpdir, "target")

        def read(path=target, mode="rt"):
            with open(path, mode) as f:
                return f.read()

        def directory_entries():
            return sorted(os.listdir(tmpdir))

        # creating a new file
        with big.atomic_write(target) as f:
            f.write("hello\n")
        assert read() == "hello\n"

        # replacing an existing file
        with big.atomic_write(target) as f:
            f.write("goodbye\n")
        assert read() == "goodbye\n"

        # an exception in the block leaves the old contents
        # untouched, and cleans up the temporary file
        with raises(RuntimeError):
            with big.atomic_write(target) as f:
                f.write("partial")
                raise RuntimeError("boom")
        assert read() == "goodbye\n"
        assert directory_entries() == ["target"]

        # an exception when the target doesn't exist yet
        # creates nothing
        never = os.path.join(tmpdir, "never")
        with raises(RuntimeError):
            with big.atomic_write(never) as f:
                f.write("partial")
                raise RuntimeError("boom")
        assert not (os.path.exists(never))
        assert directory_entries() == ["target"]

        # binary mode, and Path and bytes objects for path
        with big.atomic_write(Path(target), "wb") as f:
            f.write(b"\x00\x01\x02")
        assert read(mode="rb") == b"\x00\x01\x02"
        with big.atomic_write(os.fsencode(target), "wb") as f:
            f.write(b"bytes path")
        assert read(mode="rb") == b"bytes path"

        # 'wt' is a synonym for 'w', and encoding/errors/newline
        # pass through to open
        with big.atomic_write(target, "wt", encoding="utf-8", newline="\r\n") as f:
            f.write("café\n")
        assert read(mode="rb") == "café\r\n".encode('utf-8')

        # closing the yielded file yourself is harmless
        with big.atomic_write(target) as f:
            f.write("closed early")
            f.close()
        assert read() == "closed early"

        # two simultaneous writers to the same target don't
        # collide; last one to exit wins
        cm1 = big.atomic_write(target)
        cm2 = big.atomic_write(target)
        f1 = cm1.__enter__()
        f2 = cm2.__enter__()
        try:
            f1.write("first to enter")
            f2.write("second to enter")
        finally:
            cm2.__exit__(None, None, None)
            cm1.__exit__(None, None, None)
        assert read() == "first to enter"
        assert directory_entries() == ["target"]

        if os.name == 'posix':
            # replacing a file preserves its permissions
            os.chmod(target, 0o600)
            with big.atomic_write(target) as f:
                f.write("still private")
            assert os.stat(target).st_mode & 0o777 == 0o600

            # a new file gets ordinary open permissions,
            # respecting the umask--not mkstemp-style 0o600
            fresh = os.path.join(tmpdir, "fresh")
            old_umask = os.umask(0o027)
            try:
                with big.atomic_write(fresh) as f:
                    f.write("x")
            finally:
                os.umask(old_umask)
            assert os.stat(fresh).st_mode & 0o777 == 0o640

        # if opening the temporary file's fd fails (say, a bogus
        # encoding), the fd is closed and the temporary file is
        # removed--no litter, the target is untouched, and the
        # error propagates
        before = read()
        with raises(LookupError):
            with big.atomic_write(target, encoding='bogus-encoding') as f:
                pass # pragma: no cover
        assert read() == before
        assert all(not entry.endswith('.tmp') for entry in directory_entries())

        # append: the old contents are preserved, new contents follow
        with big.atomic_write(target) as f:
            f.write("first\n")
        with big.atomic_write(target, "a") as f:
            f.write("second\n")
        assert read() == "first\nsecond\n"

        # append is atomic: a failing append leaves the old file intact
        # (and cleans up its temporary file)
        with raises(RuntimeError):
            with big.atomic_write(target, "a") as f:
                f.write("doomed\n")
                raise RuntimeError("boom")
        assert read() == "first\nsecond\n"
        assert all(not entry.endswith('.tmp') for entry in directory_entries())

        # appending to a nonexistent path just creates it
        appendfresh = os.path.join(tmpdir, "appendfresh")
        with big.atomic_write(appendfresh, "at") as f:
            f.write("brand new\n")
        assert read(appendfresh) == "brand new\n"

        # append in binary mode
        with big.atomic_write(target, "ab") as f:
            f.write(b"\xff")
        assert read(mode="rb") == "first\nsecond\n".encode('utf-8') + b"\xff"

        # update in place ('r+'): read the old contents and rewrite them
        with big.atomic_write(target, "wb") as f:
            f.write(b"AAAABBBB")
        with big.atomic_write(target, "r+b") as f:
            assert f.read(4) == b"AAAA"
            f.seek(0)
            f.write(b"xxxx")
        assert read(mode="rb") == b"xxxxBBBB"

        # 'r+' requires the file to already exist, like open--and
        # creates nothing when it doesn't
        missing = os.path.join(tmpdir, "missing")
        with raises(FileNotFoundError):
            big.atomic_write(missing, "r+").__enter__()
        assert not (os.path.exists(missing))

        # update is atomic too: a failing edit rolls back
        with raises(RuntimeError):
            with big.atomic_write(target, "r+b") as f:
                f.write(b"ZZZZ")
                raise RuntimeError("boom")
        assert read(mode="rb") == b"xxxxBBBB"

        # write, append, and update in place are the supported modes;
        # anything else is a ValueError
        for mode in ('r', 'w+', 'x', 'rb', 'a+', 'rb+'):
            with raises(ValueError):
                big.atomic_write(target, mode).__enter__()

        # binary mode rejects text-mode arguments, like open
        for kwargs in ({'encoding': 'utf-8'}, {'errors': 'strict'}, {'newline': '\n'}):
            with raises(ValueError):
                big.atomic_write(target, 'wb', **kwargs).__enter__()

        # atomic_write refuses to replace anything but a regular file,
        # rather than let os.replace do something surprising
        adir = os.path.join(tmpdir, "adir")
        os.mkdir(adir)
        with raises(IsADirectoryError):
            big.atomic_write(adir).__enter__()
        assert os.path.isdir(adir)   # untouched

        if os.name == 'posix':
            # a symlink: os.replace would replace the link itself, not
            # its target, so atomic_write refuses--and leaves it be
            link = os.path.join(tmpdir, "link")
            os.symlink(target, link)
            with raises(OSError):
                big.atomic_write(link).__enter__()
            assert os.path.islink(link)

            # a fifo--a "special file"--is refused too
            fifo = os.path.join(tmpdir, "fifo")
            os.mkfifo(fifo)
            with raises(OSError):
                big.atomic_write(fifo).__enter__()

def test_translate_filename_to_exfat():
    with setup() as tmpdir:
        assert big.translate_filename_to_exfat("abcde") == "abcde"
        before = 'abc\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f/\\:*?": <>|xyz'
        after = "abc@?01?02?03?04?05?06?07?08?09?0a?0b?0c?0d?0e?0f?10?11?12?13?14?15?16?17?18?19?1a?1b?1c?1d?1e?1f--.@.' - {}!xyz"
        assert big.translate_filename_to_exfat(before) == after

        with raises(TypeError):
            big.translate_filename_to_exfat(35)
        with raises(ValueError):
            big.translate_filename_to_exfat("")

def test_translate_filename_to_unix():
    with setup() as tmpdir:
        assert big.translate_filename_to_unix("abcde") == "abcde"
        assert big.translate_filename_to_unix('ab\x00de/fg') == 'ab@de-fg'

        with raises(TypeError):
            big.translate_filename_to_unix(35)
        with raises(ValueError):
            big.translate_filename_to_unix("")

def test_read_python_file():
    with setup() as tmpdir:
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

def test_search_path():
    with setup() as tmpdir:
        # ensure that glob.escape and normcase are composable in either order
        # (they should be)
        assert os.path.normcase( glob.escape("AbC*") ) == glob.escape( os.path.normcase("AbC*") )

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
            assert search('nonexists') == None
            assert search('foo') == foo_d
            assert search('foo.d') == None

            search = big.search_path(
                ["test_search_path/foo_h_path", "test_search_path/foo_d_path"],
                ('', '.D'),
                preserve_extension=True,
                case_sensitive=False,
                want_directories=True,
                )
            assert search('foo') == foo_d
            assert search('foo.d') == foo_d

            search = big.search_path(
                ["test_search_path/foo_h_path", "test_search_path/foo_d_path"],
                ('.D',),
                preserve_extension=True,
                case_sensitive=False,
                want_directories=True,
                )
            assert search('foo') == foo_d
            assert search('foo.d') == foo_d

            search = big.search_path(
                ["test_search_path/foo_h_path", "test_search_path/foo_d_path"],
                ('.D',),
                preserve_extension=True,
                case_sensitive=False,
                want_directories=False,
                )
            assert search('foo') == None
            assert search('foo.d') == None

            search = big.search_path(
                ["test_search_path/foo_d_path", "test_search_path/foo_h_path"],
                ('.H',),
                preserve_extension=True,
                case_sensitive=False,
                want_directories=False,
                )
            assert search('foo') == foo_h
            assert search('foo.h') == foo_h

            foo_h = Path("test_search_path/foo_h_path/foo.h")
            search = big.search_path(
                ["test_search_path/foo_d_path", "test_search_path/foo_h_path"],
                ('.H',),
                preserve_extension=False,
                case_sensitive=False,
                want_directories=False,
                )
            assert search('foo') == foo_h
            assert search('foo.h') == None

            search = big.search_path(
                ["test_search_path/foo_d_path", "test_search_path/foo_h_path"],
                ('.H',),
                preserve_extension=True,
                case_sensitive=True,
                want_directories=False,
                )
            assert search('foo') == None
            assert search('foo.h') == None

            search = big.search_path(
                ["test_search_path/foo_d_path", "test_search_path/foo_h_path"],
                ('.h',),
                preserve_extension=True,
                want_directories=False,
                )
            assert search('foo') == foo_h
            assert search('foo.h') == foo_h

            search = big.search_path(
                ["nonexistent_dir", "test_search_path/foo_d_path", "test_search_path/foo_h_path"],
                ('.h',),
                preserve_extension=True,
                want_directories=True,
                want_files=False,
                )
            assert search('foo') == None
            assert search('foo.h') == None

            search = big.search_path(
                ["test_search_path/this_file_doesnt_match_anything", "test_search_path/foo_d_path", "test_search_path/foo_h_path"],
                ('.h', '.hpp'),
                preserve_extension=True,
                )
            assert search('foo') == foo_h
            assert search('foo.h') == foo_h
            assert search('foo.hpp') == foo_hpp

            search = big.search_path(
                ["test_search_path/foo_d_path", "test_search_path/foo_h_path", "test_search_path/file_without_extension"],
                ('.x', '.xyz', '',),
                preserve_extension=True,
                )
            assert search('foobar') == foobar
            assert search('foo.h') == foo_h
            assert search('foo.hpp') == foo_hpp

            search = big.search_path(
                ["test_search_path/foo_d_path", "test_search_path/want_directories"],
                ('.x', '.xyz', '',),
                preserve_extension=True,
                want_directories=True,
                want_files=False
                )
            assert search('mydir') == mydir
            assert search('yourdir') == None

            with raises(ValueError):
                big.search_path(("a", "b", "c"), want_files=False, want_directories=False)
            with raises(ValueError):
                big.search_path([])
            with raises(ValueError):
                big.search_path(("a", "b", "c"), [])
            with raises(ValueError):
                big.search_path(("a", "b", "c"), ('.a', 33))
            with raises(ValueError):
                big.search_path(("a", "b", "c"), ('.a', 'bcd'))
            with raises(ValueError):
                big.search_path(("a", "b", "c"), ('.a', '', '.bcd', ''))

            with raises(ValueError):
                search("foobar/")

            with tempfile.TemporaryDirectory() as tmp:
                tmp = Path(tmp)
                lower = tmp / "filename.h"
                upper = tmp / "FILENAME.h"
                big.touch(lower)
                if not upper.exists():
                    big.touch(upper)

                    search = big.search_path([tmp], ['.h', ''], case_sensitive=False)
                    with raises(ValueError):
                        search("fIlEnAmE")
                    search = big.search_path([tmp], case_sensitive=False)
                    with raises(ValueError):
                        search("fIlEnAmE.h")


def run_tests(run=None):
    (run or bigtestlib.run)(name="big.file", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
