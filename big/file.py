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

import builtins
import fnmatch
import glob
import os.path
from pathlib import Path
import re
from stat import S_ISDIR, S_ISREG


try:
    from re import Pattern as re_Pattern
except ImportError: # pragma: no cover
    re_Pattern = re._pattern_type

from .text import decode_python_script


__all__ = []

def export(o):
    __all__.append(o.__name__)
    return o


import shutil
which = export(shutil.which)


@export
def fgrep(path, text, *, encoding=None, enumerate=False, case_insensitive=False):
    """
    Find the lines of a file that match some text, like the UNIX "fgrep"
    utility program.

    path should be an object representing a path to an existing file, one of:
      * a string,
      * a bytes object, or
      * a pathlib.Path object.

    text should be either string or bytes.

    encoding is used as the file encoding when opening the file.

    if text is a str, the file is opened in text mode.
    if text is a bytes object, the file is opened in binary mode.
    encoding must be None when the file is opened in binary mode.

    If case_insensitive is true, perform the search in a case-insensitive
    manner.

    Returns a list of lines in the file containing text.  The lines are either
    strings or bytes objects, depending on the type of text.  The lines
    have their line-breaks stripped but preserve all other whitespace.

    If enumerate is true, returns a list of tuples of (line_number, line).
    The first line of the file is line number 1.

    For simplicity of implementation, the entire file is read in to memory
    at one time.  If `case_insensitive` is True, fgrep also makes a
    lowercased copy.
    """
    if isinstance(text, bytes):
        if encoding is not None:
            raise ValueError("encoding must be None when text is bytes")
        mode = 'rb'
        separator = b'\n'
    else:
        mode = 'rt'
        separator = '\n'
    if isinstance(path, Path):
        f = path.open(mode, encoding=encoding)
    else:
        f = open(path, mode, encoding=encoding)
    with f:
        contents = f.read()
        split = contents.split(separator)
        if not case_insensitive:
            if enumerate:
                return [t for t in builtins.enumerate(split, 1) if text in t[1]]
            return [line for line in split if text in line]

        lower_contents = contents.lower()
        lower_split = lower_contents.split(separator)
        text = text.lower()
        if enumerate:
            return [(line_number, line) for line_number, (line, lower_line) in builtins.enumerate(zip(split, lower_split), 1) if text in lower_line]
        return [line for line, lower_line in zip(split, lower_split) if text in lower_line]


@export
def grep(path, pattern, *, encoding=None, enumerate=False, flags=0):
    """
    Look for matches to a regular expression pattern in the lines of a file,
    like the UNIX "grep" utility program.

    path should be an object representing a path to an existing file, one of:
      * a string,
      * a bytes object, or
      * a pathlib.Path object.

    pattern should be an object containing a regular expression, one of:
      * a string,
      * a bytes object, or
      * an re.Pattern, initialized with either str or bytes.

    encoding is used as the file encoding when opening the file.

    if pattern uses a str, the file is opened in text mode.
    if pattern uses a bytes object, the file is opened in binary mode.
    encoding must be None when the file is opened in binary mode.

    flags is passed in as the flags argument to re.compile if pattern
    is a string.

    Returns a list of lines in the file matching the pattern.  The lines
    are either strings or bytes objects, depending on the type of pattern.
    The lines have their line-breaks stripped but preserve all other whitespace.

    If enumerate is true, returns a list of tuples of (line_number, line).
    The first line of the file is line number 1.

    For simplicity of implementation, the entire file is read in to memory
    at one time.

    Tip: to perform a case-insensitive pattern match, pass in the
    re.IGNORECASE flag into flags for this function (if pattern is a string
    or bytes) or when creating your regular expression object (if pattern is
    an re.Pattern object.

    (In older versions of Python, re.Pattern was a private type called
    re._pattern_type.)
    """
    if not isinstance(pattern, re_Pattern):
        pattern = re.compile(pattern, flags)
    if isinstance(pattern.pattern, bytes):
        if encoding is not None:
            raise ValueError("encoding must be None when pattern uses bytes")
        mode = 'rb'
        separator = b'\n'
    else:
        mode = 'rt'
        separator = '\n'
    if isinstance(path, Path):
        f = path.open(mode, encoding=encoding)
    else:
        f = open(path, mode, encoding=encoding)
    with f:
        text = f.read()
        split = text.split(separator)
        if enumerate:
            return [t for t in builtins.enumerate(split, 1)
                    if pattern.search(t[1])]
        return [line for line in split if pattern.search(line)]


@export
class pushd:
    """
    A context manager that temporarily changes the directory.
    Example:

    with big.pushd('x'):
        pass

    This would change into the `'x'` subdirectory before
    executing the nested block, then change back to
    the original directory after the nested block.

    You can change directories in the nested block;
    this won't affect pushd restoring the original current
    working directory upon exiting the nested block.
    """
    def __init__(self, path):
        self.path = path
        self.cwd = os.getcwd()
    def __enter__(self):
        os.chdir(self.path)
    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.cwd)


@export
def safe_mkdir(path):
    """
    Ensures that a directory exists at 'path'.
    If this function returns and doesn't raise,
    it guarantees that a directory exists at 'path'.

    If a directory already exists at 'path',
    does nothing.

    If a file exists at 'path', unlinks it
    then creates the directory.

    If the parent directory doesn't exist,
    creates it, then creates 'path'.

    This function can still fail:
      * 'path' could be on a read-only filesystem.
      * You might lack the permissions to create 'path'.
      * You could ask to create the directory 'x/y'
        and 'x' is a file (not a directory).
    """
    if os.path.isfile(path):
        os.unlink(path)
    os.makedirs(path, exist_ok=True)

@export
def safe_unlink(path):
    """
    Unlinks path, if path exists and is a file.
    """
    if os.path.isfile(path):
        os.unlink(path)

@export
def file_size(path):
    """
    Returns the size of the file at `path`, as an integer
    representing the number of bytes.
    """
    st = os.stat(path)
    return st.st_size

@export
def file_mtime(path):
    """
    Returns the modification time of path, in seconds since the epoch.
    Note that seconds is a float, indicating the sub-second with some
    precision.
    """
    st = os.stat(path)
    return st.st_mtime

@export
def file_mtime_ns(path):
    """
    Returns the modification time of path, in nanoseconds since the epoch.
    """
    st = os.stat(path)
    return st.st_mtime_ns

@export
def touch(path):
    """
    Ensures that path exists, and its modification time is the current time.

    If path does not exist, creates an empty file.

    If path exists, updates its modification time to the current time.
    """
    if os.path.exists(path):
        os.utime(path)
    else:
        with open(path, "wb") as f:
            pass

# exfat allowed characters:
#
# all Unicode characters except
#     U+0000 (NUL) through U+001F (US)
#     / (slash)
#     \ (backslash)
#     : (colon)
#     * (asterisk)
#     ? (question mark)
#     " (quote)
#     < (less than)
#     > (greater than)
# and | (pipe)
#
# https://en.wikipedia.org/wiki/ExFAT
_exfat_translation_dict = {
    "\x00": "@",
    "\x01": "?01",
    "\x02": "?02",
    "\x03": "?03",
    "\x04": "?04",
    "\x05": "?05",
    "\x06": "?06",
    "\x07": "?07",
    "\x08": "?08",
    "\x09": "?09",
    "\x0a": "?0a",
    "\x0b": "?0b",
    "\x0c": "?0c",
    "\x0d": "?0d",
    "\x0e": "?0e",
    "\x0f": "?0f",

    "\x10": "?10",
    "\x11": "?11",
    "\x12": "?12",
    "\x13": "?13",
    "\x14": "?14",
    "\x15": "?15",
    "\x16": "?16",
    "\x17": "?17",
    "\x18": "?18",
    "\x19": "?19",
    "\x1a": "?1a",
    "\x1b": "?1b",
    "\x1c": "?1c",
    "\x1d": "?1d",
    "\x1e": "?1e",
    "\x1f": "?1f",

    "/": "-",
    "\\": "-",
    "*": "@",
    "?": ".",
    '"': "'",
    '<': "{",
    '>': "}",
    '|': "!",
    }

_exfat_translation_table = ''.maketrans(_exfat_translation_dict)

@export
def translate_filename_to_exfat(s):
    """
    Ensures that all characters in s are legal for a FAT filesystem.

    Returns a copy of s where every character not allowed in a FAT
    filesystem filename has been replaced with a character (or characters)
    that are permitted.
    """
    if not (isinstance(s, str) and s):
        raise ValueError("filename can't be empty")
    s = s.translate(_exfat_translation_table)
    s = s.replace(": ", " - ")
    s = s.replace(":", ".")
    return s


# unix filesystem allowed characters:
# everything except a zero byte and '/'
_unix_translation_dict = {
        "\x00": "@",
        "/":    "-",
    }

_unix_translation_table = ''.maketrans(_unix_translation_dict)

@export
def translate_filename_to_unix(s):
    """
    Ensures that all characters in s are legal for a UNIX filesystem.

    Returns a copy of s where every character not allowed in a UNIX
    filesystem filename has been replaced with a character (or characters)
    that are permitted.
    """
    if not (isinstance(s, str) and s):
        raise ValueError("filename can't be empty")
    return s.translate(_unix_translation_table)


@export
def read_python_file(path, *,
    newline=None,
    use_bom=True,
    use_source_code_encoding=True):
    """
    Opens, reads, and correctly decodes a Python script from a file.

    path should specify the filesystem path to the file; it can
    be any object accepted by builtins.open (a "path-like object").

    Returns the script as a Unicode string.

    Decodes the script using big's decode_python_script function.
    The newline, use_bom, and use_source_code_encoding parameters
    are passed through to that function.
    """
    with open(path, "rb") as f:
        script = f.read()

    return decode_python_script(script,
        newline=newline,
        use_bom=use_bom,
        use_source_code_encoding=use_source_code_encoding)



if os.altsep: # pragma: nocover
    _os_seps = os.sep + os.altsep
else:
    _os_seps = os.sep

_case_sensitive_platform = os.path.normcase('FOo') != os.path.normpath('foo')

@export
def search_path(paths, extensions=('',),
    *,
    case_sensitive=None,
    preserve_extension=True,
    want_directories=False,
    want_files=True,
    ):
    """
    Search a list of directories for a file.  Given a sequence
    of directories, an optional list of file extensions, and a
    filename, searches those directories for a file with that
    name and possibly one of those file extensions.

    search_path accepts the paths and extensions as parameters and
    returns a "search" function.  The search function accepts one
    filename parameter and performs the search, returning either the
    path to the file it found (as a pathlib.Path object) or None.
    You can reuse the search function to perform as many searches
    as you like.

    paths should be an iterable of str or pathlib.Path objects
    representing directories.  These may be relative or absolute
    paths; relative paths will be relative to the current directory
    at the time the search function is run.  Specifying a directory
    that doesn't exist is not an error.

    extensions should be an iterable of str objects representing
    extensions.  Every non-empty extension specified should start
    with a period ('.') character (technically "os.extsep").  You
    may specify at most one empty string in extensions, which
    represents testing the filename without an additional
    extension.  By default extensions is the tuple ('',).
    Extension strings may contain additional period characters
    after the initial one.

    Shell-style "globbing" isn't supported for any parameter.  Both
    the filename and the extension strings may contain filesystem
    globbing characters, but they will only match those literal
    characters themselves.  ('*' won't match any character, it'll
    only match a literal '*' in the filename or extension.)

    case_sensitive works like the parameter to pathlib.Path.glob.
    If case_sensitive is true, files found while searching must
    match the filename and extension exactly.  If case_sensitive
    is false, the comparison is done in a case-insensitive manner.
    If case_sensitive is None (the default), case sensitivity obeys
    the platform default (as per os.path.normcase).  In practice,
    only Windows platforms are case-insensitive by convention;
    all other platforms that support Python are case-sensitive
    by convention.

    If preserve_extension is true (the default), the search function
    checks the filename to see if it already ends with one of the
    extensions.  If it does, the search is restricted to only files
    with that extension--the other extensions are ignored.  This
    check obeys the case_sensitive flag; if case_sensitive is None,
    this comparison is case-insensitive only on Windows.

    want_files and want_directories are boolean values; the search
    functino will only return that type of file if the corresponding
    "want_" parameter is true.  You can request files, directories,
    or both.  (want_files and want_directories can't both be false.)
    By default, want_files is true and want_directories is false.

    paths and extensions are both tried in order, and the search
    function returns the first match it finds.  All extensions are
    tried in a path entry before considering the next path.

    Returns a function:
        search(filename)
    which returns either a pathlib.Path object on success or None on
    failure.
    """

    if not (want_files or want_directories):
        raise ValueError("search_path: want_files and want_directories can't both be false")

    paths = [Path(path) for path in paths]
    if not paths:
        raise ValueError("search_path: paths must be an iterable of str or pathlib.Path objects")

    extensions = list(extensions)
    if not extensions:
        raise ValueError("search_path: extensions must be an iterable of str objects")

    extsep = os.extsep

    cleaned = []
    not_str = []
    empty_count = 0
    doesnt_start_with_extsep = []
    for ext in extensions:
        if not isinstance(ext, str):
            not_str.append(ext)
            continue
        if not ext:
            empty_count += 1
            continue
        if not ext.startswith(extsep):
            doesnt_start_with_extsep.append(ext)
            continue
        cleaned.append(ext)

    if empty_count > 1:
        raise ValueError(f"search_path: extension may contain at most one empty string, not {empty_count}")

    failures = [ext for ext in extensions if (ext and ((not isinstance(ext, str)) or (not ext.startswith(extsep))))]
    if failures:
        failures = " ".join(repr(ext) for ext in failures)
        raise ValueError(f"search_path: every extension must start with {extsep}, not {failures}")


    glob_escape = glob.escape
    if case_sensitive is None:
        case_sensitive = _case_sensitive_platform
    else:
        case_sensitive = bool(case_sensitive)
        if not case_sensitive:
            def case_insensitive_glob_escape(s):
                buffer = []
                append = buffer.append
                for c in glob.escape(s):
                    if not c.isalpha():
                        append(c)
                        continue
                    append('[')
                    append(c.upper())
                    append(c.lower())
                    append(']')
                return ''.join(buffer)
            glob_escape = case_insensitive_glob_escape



    def no_change(s): return s
    def lower(s): return s.lower()
    normcase = no_change if case_sensitive else lower

    extensions = [(ext, glob_escape(ext)) if ext else ('', '') for ext in extensions]

    def search(filename):
        nonlocal extensions

        if filename.endswith(_os_seps):
            raise ValueError(f'search_path: filename {filename!r} ends with {filename[-1]!r}')

        use_extensions = extensions
        if preserve_extension:
            for t in extensions:
                ext, escaped_ext = t
                if not ext:
                    continue
                if fnmatch.fnmatch(normcase(filename), normcase('*' + escaped_ext)):
                    # matched! only use this extension.
                    use_extensions = [t]
                    assert normcase(filename[-len(ext):]) == normcase(ext), f"{normcase(filename[-len(ext):])!r} != {normcase(ext)!r}"
                    filename = filename[:-len(ext)]
                    break

        escaped_filename = glob_escape(str(filename))

        for dir in paths:
            if not dir.is_dir():
                continue
            for ext, escaped_ext in use_extensions:
                if ext:
                    filename_glob = escaped_filename + escaped_ext
                else:
                    filename_glob = escaped_filename
                matches = list(dir.glob(filename_glob))
                if not matches:
                    continue
                valid = []
                for match in matches:
                    stat = match.stat()
                    mode = stat.st_mode
                    if want_files and S_ISREG(mode):
                        valid.append(match)
                    elif want_directories and S_ISDIR(mode):
                        valid.append(match)
                if len(valid) > 1: # pragma: nocover
                    # can't test this unless we have a case-sensitive filesystem
                    valid = ", ".join([repr(str(_)) for _ in valid])
                    raise ValueError(f"search_path: can't choose between multiple matching paths {valid}")
                elif valid:
                    return valid[0]
        return None
    return search
