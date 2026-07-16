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

import errno
import pathlib
import sys
import tempfile

import bigtestlib
bigtestlib.preload_local_big()

from big.test import raises

import big


def preload_with_argv(argv_0):
    """Call preload_local_big with a temporary sys.argv[0]."""
    saved = sys.argv[0]
    sys.argv[0] = str(argv_0)
    try:
        return bigtestlib.preload_local_big()
    finally:
        sys.argv[0] = saved

def test_finds_checkout_from_test_directory():
    """Walking up from this test file finds the big checkout."""
    big_dir = preload_with_argv(__file__)
    assert (big_dir / "big" / "__init__.py").is_file()
    assert big.__file__.startswith(str(big_dir))

def test_raises_when_no_checkout_above():
    """Regression: with no big/__init__.py between the start directory
    and the filesystem root, preload_local_big raises FileNotFoundError
    instead of looping forever."""
    directory = pathlib.Path(tempfile.mkdtemp()) / "a" / "b"
    directory.mkdir(parents=True)
    for parent in (directory, *directory.parents):
        assert not ((parent / "big" / "__init__.py").is_file()), (f"a big checkout exists at {parent}, "
            "so the no-checkout condition can't be arranged")
    with raises(FileNotFoundError) as raised:
        preload_with_argv(directory / "fake_test.py")
    assert raised.exception.errno == errno.ENOENT
    assert raised.exception.filename == "big/__init__.py"
    assert str(directory) in raised.exception.strerror


def test_run_and_finish_delegate_to_big_test():
    # bigtestlib.run and .finish forward to big.test, so a
    # test module behaves the same whichever one it calls
    import contextlib
    import io
    import types
    from big import test

    module = types.ModuleType("delegated")
    module.test_fine = lambda: None

    saved = dict(test.stats)
    for key in test.stats:
        test.stats[key] = 0
    try:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            bigtestlib.run(name="delegated", module=module)
            bigtestlib.finish()
        output = buffer.getvalue()
    finally:
        test.stats.clear()
        test.stats.update(saved)

    assert "Testing delegated..." in output
    assert "Ran 1 test in" in output
    assert output.endswith("OK\n")


def run_tests(run=None):
    (run or bigtestlib.run)(name="bigtestlib", module=__name__)


if __name__ == "__main__":  # pragma: no cover
    run_tests()
    bigtestlib.finish()
