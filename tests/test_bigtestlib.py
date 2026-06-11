#!/usr/bin/env python3

import errno
import pathlib
import sys
import tempfile
import unittest

import bigtestlib
bigtestlib.preload_local_big()

import big


class TestPreloadLocalBig(unittest.TestCase):
    """Tests for bigtestlib.preload_local_big."""

    def preload_with_argv(self, argv_0):
        """Call preload_local_big with a temporary sys.argv[0]."""
        saved = sys.argv[0]
        sys.argv[0] = str(argv_0)
        try:
            return bigtestlib.preload_local_big()
        finally:
            sys.argv[0] = saved

    def test_finds_checkout_from_test_directory(self):
        """Walking up from this test file finds the big checkout."""
        big_dir = self.preload_with_argv(__file__)
        self.assertTrue((big_dir / "big" / "__init__.py").is_file())
        self.assertTrue(big.__file__.startswith(str(big_dir)))

    def test_raises_when_no_checkout_above(self):
        """Regression: with no big/__init__.py between the start directory
        and the filesystem root, preload_local_big raises FileNotFoundError
        instead of looping forever."""
        directory = pathlib.Path(tempfile.mkdtemp()) / "a" / "b"
        directory.mkdir(parents=True)
        for parent in (directory, *directory.parents):
            self.assertFalse((parent / "big" / "__init__.py").is_file(),
                f"a big checkout exists at {parent}, "
                "so the no-checkout condition can't be arranged")
        with self.assertRaises(FileNotFoundError) as raised:
            self.preload_with_argv(directory / "fake_test.py")
        self.assertEqual(raised.exception.errno, errno.ENOENT)
        self.assertEqual(raised.exception.filename, "big/__init__.py")
        self.assertIn(str(directory), raised.exception.strerror)


def run_tests():
    bigtestlib.run(name="bigtestlib", module=__name__)


if __name__ == "__main__":  # pragma: no cover
    run_tests()
    bigtestlib.finish()
