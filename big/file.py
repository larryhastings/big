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

import builtins
import contextlib
import errno
import fnmatch
import glob
import os.path
from pathlib import Path
import re
from stat import S_ISDIR, S_ISLNK, S_ISREG


try:
    from re import Pattern as re_Pattern
except ImportError: # pragma: no cover
    re_Pattern = re._pattern_type

from .text import decode_python_script


from . import builtin
mm = builtin.ModuleManager()
export = mm.export


import shutil
which = export(shutil.which)


@export
def fgrep(path, text, *, case_insensitive=False, encoding=None, enumerate=False):
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
    Lines are split according to big's own definition of linebreaks
    (see big.text.linebreaks and big.text.bytes_linebreaks)--which is
    exactly what str.splitlines and bytes.splitlines split on.  In
    particular, binary-mode lines may end in '\\r\\n', '\\r', or '\\n',
    and all three are recognized and stripped.

    If enumerate is true, returns a list of tuples of (line_number, line).
    The first line of the file is line number 1.

    For simplicity of implementation, the entire file is read in to memory
    at one time.  If `case_insensitive` is True, fgrep also makes a
    case-folded copy.
    """
    if isinstance(text, bytes):
        if encoding is not None:
            raise ValueError("encoding must be None when text is bytes")
        mode = 'rb'
        # bytes have no casefold; ASCII lowercasing is the best we can do
        def fold(s):
            return s.lower()
    else:
        mode = 'rt'
        def fold(s):
            return s.casefold()
    if isinstance(path, Path):
        f = path.open(mode, encoding=encoding)
    else:
        f = open(path, mode, encoding=encoding)
    with f:
        contents = f.read()
        # splitlines recognizes exactly what big considers linebreaks
        # (see big.text.linebreaks and big.text.bytes_linebreaks):
        # \r\n and \r in binary files, \v \f \x85 \u2028 etc. in text.
        split = contents.splitlines()
        if not case_insensitive:
            if enumerate:
                return [t for t in builtins.enumerate(split, 1) if text in t[1]]
            return [line for line in split if text in line]

        # folded per line, so folding can't possibly change the line count
        folded_split = [fold(line) for line in split]
        text = fold(text)
        if enumerate:
            return [(line_number, line) for line_number, (line, folded_line) in builtins.enumerate(zip(split, folded_split), 1) if text in folded_line]
        return [line for line, folded_line in zip(split, folded_split) if text in folded_line]


@export
def grep(path, pattern, *, case_insensitive=None, encoding=None, enumerate=False, flags=0):
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

    case_insensitive controls case sensitivity explicitly, and may be
    None (the default), True, or False:

      * None means make no effort in either direction.  A string or
        bytes pattern is compiled with flags exactly as given; flags
        is 0 by default, which means case-sensitive.  A precompiled
        pattern keeps whatever flags it already has.
      * True forces a case-insensitive search, adding re.IGNORECASE.
      * False forces a case-sensitive search, removing re.IGNORECASE.

    When case_insensitive is True or False, the pattern is (re)compiled
    to honor it--even a precompiled re.Pattern.  (One limitation: an
    inline "(?i)" flag baked into the pattern text itself isn't
    affected by case_insensitive=False; it lives in the pattern,
    not the flags.)  Passing case_insensitive=True is equivalent to
    adding re.IGNORECASE to flags yourself, if pattern is str or bytes.

    Returns a list of lines in the file matching the pattern.  The lines
    are either strings or bytes objects, depending on the type of pattern.
    The lines have their line-breaks stripped but preserve all other whitespace.
    Lines are split according to big's own definition of linebreaks
    (see big.text.linebreaks and big.text.bytes_linebreaks)--which is
    exactly what str.splitlines and bytes.splitlines split on.  In
    particular, binary-mode lines may end in '\\r\\n', '\\r', or '\\n',
    and all three are recognized and stripped.

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
    if isinstance(pattern, re_Pattern):
        pattern_source = pattern.pattern
        pattern_flags = pattern.flags
    else:
        pattern_source = pattern
        pattern_flags = flags

    if case_insensitive is None:
        # make no effort in either direction: use the pattern as-is.
        # a str/bytes pattern is compiled with flags exactly as given;
        # a precompiled pattern keeps its own flags (never recompiled).
        if not isinstance(pattern, re_Pattern):
            pattern = re.compile(pattern_source, pattern_flags)
    else:
        # force case sensitivity one way or the other, (re)compiling
        # as needed--even a precompiled pattern.
        if case_insensitive:
            pattern_flags |= re.IGNORECASE
        else:
            pattern_flags &= ~re.IGNORECASE
        pattern = re.compile(pattern_source, pattern_flags)

    if isinstance(pattern.pattern, bytes):
        if encoding is not None:
            raise ValueError("encoding must be None when pattern uses bytes")
        mode = 'rb'
    else:
        mode = 'rt'
    if isinstance(path, Path):
        f = path.open(mode, encoding=encoding)
    else:
        f = open(path, mode, encoding=encoding)
    with f:
        text = f.read()
        # splitlines recognizes exactly what big considers linebreaks
        # (see big.text.linebreaks and big.text.bytes_linebreaks):
        # \r\n and \r in binary files, \v \f \x85 \u2028 etc. in text.
        split = text.splitlines()
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

    The original directory is captured when the block is
    *entered*, not when the pushd object is constructed.
    (Like the shell builtin: pushd pushes the directory
    you're in right now.)  This also means a single pushd
    object can be reused.
    """
    def __init__(self, path):
        self.path = path
    def __enter__(self):
        self.cwd = os.getcwd()
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

    A symlink at 'path' that doesn't lead to a directory--a
    symlink to a file, or a dangling symlink--counts as a file:
    it's unlinked.  A symlink that leads to a directory is left
    alone; a directory exists at 'path', which is the goal.

    This function can still fail:
      * 'path' could be on a read-only filesystem.
      * You might lack the permissions to create 'path'.
      * You could ask to create the directory 'x/y'
        and 'x' is a file (not a directory).
    """
    if os.path.isfile(path) or (os.path.islink(path) and not os.path.isdir(path)):
        os.unlink(path)
    os.makedirs(path, exist_ok=True)

@export
def safe_unlink(path):
    """
    Unlinks path, if path exists and is a file.

    A symlink at path that doesn't lead to a directory--a
    symlink to a file, or a dangling symlink--counts as a file.
    (Unlinking it removes the symlink itself, never its target.)
    A symlink that leads to a directory is left alone.
    """
    if os.path.isfile(path) or (os.path.islink(path) and not os.path.isdir(path)):
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


@export
@contextlib.contextmanager
def atomic_write(path, mode='w', *, encoding=None, errors=None, newline=None):
    """
    A context manager that writes a file atomically: readers of
    'path' see either the old contents or the new contents, never
    a mixture, no matter when the writer crashes or the machine
    loses power.

    Returns a context manager.  Entering the context manage returns
    a file object open for writing.  Write the new contents to it as usual:

        with big.atomic_write(path) as f:
            f.write(everything)

    If the nested block exits normally, the new contents atomically
    replace the old file at 'path' (or create 'path' if it didn't
    alreadyexist).  If the nested block raises, the file at 'path'
    is completely untouched, and the partially-written new contents
    are removed.

    How it works: atomic_write writes to a temporary file in the
    same directory as 'path'.  On success, the temporary file is
    flushed, fsync'ed, and renamed over 'path' with os.replace
    (which is atomic).  "The same directory" matters: rename is
    only atomic within one filesystem.  On failure, the temporary
    file is unlinked.

    'path' should be a str, bytes, or os.PathLike object.

    'mode' selects how you write the new contents:

      * 'w', 'wt', or 'wb' -- write.  The new file starts empty;
        you write it from scratch.
      * 'a', 'at', or 'ab' -- append.  The old contents (if any)
        are preserved, and you write additional contents after
        them.
      * 'r+', 'r+t', or 'r+b' -- update in place.  The old contents
        are preserved and the file is positioned at the start, so
        you can read and rewrite them; like open, 'r+' requires
        'path' to already exist.

    For append and update, atomic_write copies the existing file
    into the temporary file before handing it to you, so that even
    an append or an in-place edit is atomic: readers see the whole
    old file or the whole new file, never a mixture.  Note the cost:
    this copy is O(size of the existing file), so atomic append is a
    poor fit for a hot path (e.g. appending one line at a time to a
    large log)--each call recopies the entire file.

    'encoding', 'errors', and 'newline' work as they do for open,
    and like open, they're only permitted in text mode.

    Permissions: if a file already exists at 'path', the new file
    inherits its permissions.  If 'path' is new, it gets the same
    default permissions an ordinary open would give it (respecting
    the umask)--not the private permissions temporary files
    usually get.

    Closing the yielded file object yourself is harmless, though
    it means atomic_write can't fsync the contents (close already
    flushed them; the rename is still atomic).

    If 'path' exists it must be a regular file.  atomic_write raises
    if it's a directory (`IsADirectoryError`), a symbolic link, or
    another special file (`OSError`)--rather than let os.replace do
    something surprising, like replace a symlink with the new file
    (detaching the link from its target).  This check samples the
    path, so it's necessarily racy: if the path is swapped for a
    directory or symlink after the check, the final rename simply
    fails on its own.  The check just turns the common mistake into
    a clear error up front.

    Caveat: the hard link count isn't preserved--replacing one name
    of a multiply-linked file detaches it from the other names.
    """

    # mode_flags[mode] -> (binary, copy_old, updating).
    # "updating" means update in place ('r+'): the one mode that
    # both reads the old contents and, like open, requires the
    # file to already exist--so it feeds both require_existing
    # and readable below.
    mode_flags = {
        'w':   (False, False, False),
        'wt':  (False, False, False),
        'wb':  (True,  False, False),
        'a':   (False, True,  False),
        'at':  (False, True,  False),
        'ab':  (True,  True,  False),
        'r+':  (False, True,  True),
        'r+t': (False, True,  True),
        'r+b': (True,  True,  True),
    }
    flags = mode_flags.get(mode)
    if flags is None:
        raise ValueError(
            f"mode must be one of 'w'/'wt'/'wb' (write), 'a'/'at'/'ab' "
            f"(append), or 'r+'/'r+t'/'r+b' (update in place), not {mode!r}"
            )
    binary, copy_old, updating = flags
    require_existing = readable = updating
    if binary and not ((encoding is None) and (errors is None) and (newline is None)):
        raise ValueError("binary mode doesn't take an encoding, errors, or newline argument")

    path = os.fspath(path)

    # Sample the path.  We lstat rather than stat, so a symlink shows
    # up as a symlink instead of as whatever it points at.  If path
    # exists it must be a regular file: replacing anything else is
    # either impossible (a directory) or a footgun (os.replace onto a
    # symlink replaces the *link*, not its target).  Refuse now, with
    # a clear error.  (This samples the path, so it's racy--but a swap
    # after the check only means the final rename fails with a worse
    # message; it never clobbers something surprising.)
    #
    # A replaced regular file's permissions are inherited.  A new file
    # keeps the temporary file's permissions, which we create as mode
    # 0o666 for the umask to filter, exactly like an ordinary open.
    try:
        st_mode = os.lstat(path).st_mode
    except FileNotFoundError:
        permissions = None
        source_exists = False
    else:
        source_exists = True
        if not S_ISREG(st_mode):
            if S_ISDIR(st_mode):
                raise IsADirectoryError(errno.EISDIR, os.strerror(errno.EISDIR), path)
            what = "a symbolic link" if S_ISLNK(st_mode) else "a special file"
            raise OSError(errno.EINVAL,
                f"atomic_write can only replace a regular file, not {what}", path)
        permissions = st_mode & 0o7777

    # updating in place ('r+') needs the file to already exist,
    # exactly like open().  (appending happily creates a new file.)
    if require_existing and not source_exists:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)

    flags = (os.O_CREAT | os.O_EXCL | (os.O_RDWR if readable else os.O_WRONLY)
        | getattr(os, 'O_BINARY', 0)     # Windows: the io module wants an untranslated fd
        | getattr(os, 'O_CLOEXEC', 0))   # don't leak the fd to subprocesses

    # can't use tempfile, we need to control permissions:
    # mkstemp hardcodes mode 0600, and fixing that up afterward
    # for a new target means reading the umask, which Python can
    # only do by *setting* it--a process-global race.  passing
    # 0o666 to os.open lets the kernel apply the umask for us.
    #
    # O_EXCL guarantees we never open somebody else's file,
    # so a name collision just means "try the next counter".
    template = b'%s.%d.%d.tmp' if isinstance(path, bytes) else '%s.%d.%d.tmp'
    pid = os.getpid()
    counter = 0
    while True:
        temporary_path = template % (path, pid, counter)
        try:
            fd = os.open(temporary_path, flags, 0o666)
            break
        except FileExistsError:
            counter += 1

    try:
        # append and update in place operate on the *old* contents, so
        # copy them into the temporary file first, as raw bytes, before
        # we wrap the fd in text mode.  (this is what makes append and
        # update atomic--we build the whole new file, then rename it
        # over the old one.  it also makes atomic append an O(size of
        # file) operation: fine occasionally, pathological as a
        # hot-path logger.)
        if copy_old and source_exists:
            with open(path, 'rb') as source:
                while True:
                    chunk = source.read(65536)
                    if not chunk:
                        break
                    os.write(fd, chunk)
            # append writes at the end, where the copy left the fd;
            # update rewinds so the caller sees the file from the top.
            if require_existing:
                os.lseek(fd, 0, os.SEEK_SET)

        f = open(fd, mode, encoding=encoding, errors=errors, newline=newline)
    except:
        # a failed copy leaves the fd open; a failed open() may or may
        # not have closed it already--it closes it if the failure came
        # *after* it built the raw FileIO (a bogus encoding, say), and
        # doesn't if it never got that far.  close it ourselves if it's
        # still open.
        try:
            os.close(fd)
        except OSError:
            pass
        os.unlink(temporary_path)
        raise

    try:
        yield f
        if not f.closed:
            f.flush()
            os.fsync(f.fileno())
            f.close()
        if permissions is not None:
            os.chmod(temporary_path, permissions)
        os.replace(temporary_path, path)
    except:
        f.close()
        try:
            os.unlink(temporary_path)
        except FileNotFoundError: # pragma: no cover
            pass
        raise

    # make the rename itself durable: fsync the directory.
    # best effort--not every platform or filesystem can.
    if hasattr(os, 'O_DIRECTORY'): # pragma: no branch
        directory = os.path.dirname(path) or (b'.' if isinstance(path, bytes) else '.')
        try:
            directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
        except OSError: # pragma: no cover
            pass
        else:
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)


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
    if not isinstance(s, str):
        raise TypeError(f"filename must be str, not {type(s).__name__}")
    if not s:
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
    if not isinstance(s, str):
        raise TypeError(f"filename must be str, not {type(s).__name__}")
    if not s:
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

_case_sensitive_platform = os.path.normcase('FOo') != os.path.normcase('foo')

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

    Returns a function:
        search(filename)
    which returns either a pathlib.Path object on success (it found a
    matching file) or None on failure (it couldn't find a matching file).

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

    (Caveat: on Windows, the underlying filesystem globbing is
    itself case-insensitive, and search_path doesn't attempt to
    compensate.  case_sensitive=True on Windows still finds files
    whose names match case-insensitively.)

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

    not_str = []
    empty_count = 0
    doesnt_start_with_extsep = []
    for ext in extensions:
        if not isinstance(ext, str):
            not_str.append(ext)
        elif not ext:
            empty_count += 1
        elif not ext.startswith(extsep):
            doesnt_start_with_extsep.append(ext)

    if not_str:
        failures = " ".join(repr(ext) for ext in not_str)
        raise ValueError(f"search_path: every extension must be a str, not {failures}")
    if empty_count > 1:
        raise ValueError(f"search_path: extensions may contain at most one empty string, not {empty_count}")
    if doesnt_start_with_extsep:
        failures = " ".join(repr(ext) for ext in doesnt_start_with_extsep)
        raise ValueError(f"search_path: every extension must start with {extsep!r}, not {failures}")


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


mm()
