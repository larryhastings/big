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

import builtins
import os
import pathlib
import re


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
    have their newlines stripped but preserve all other whitespace.

    If enumerate is true, returns a list of tuples of (line_number, line).
    The first line of the file is line number 1.

    For simplicity of implementation, the entire file is read in to memory
    at one time.  If `case_insensitive` is True, a lowercased copy is also used.
    """
    if isinstance(text, bytes):
        if encoding is not None:
            raise ValueError("encoding must be None when text is bytes")
        mode = 'rb'
        separator = b'\n'
    else:
        mode = 'rt'
        separator = '\n'
    if isinstance(path, pathlib.Path):
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
    The lines have their newlines stripped but preserve all other whitespace.

    If enumerate is true, returns a list of tuples of (line_number, line).
    The first line of the file is line number 1.

    For simplicity of implementation, the entire file is read in to memory
    at one time.

    (Tip: to perform a case-insensitive pattern match, pass in the
    re.IGNORECASE flag into flags for this function (if pattern is a string
    or bytes) or when creating your regular expression object (if pattern is
    an re.Pattern object).
    """
    if not isinstance(pattern, re.Pattern):
        pattern = re.compile(pattern, flags)
    if isinstance(pattern.pattern, bytes):
        if encoding is not None:
            raise ValueError("encoding must be None when pattern uses bytes")
        mode = 'rb'
        separator = b'\n'
    else:
        mode = 'rt'
        separator = '\n'
    if isinstance(path, pathlib.Path):
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
    s = s.replace(":", "-")
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
