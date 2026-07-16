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

#
# The bootstrap for big's own test suite.
#
# big's tests are run with big.test--which lives inside the very
# package under test.  big.test.preload() can't locate big before
# big is importable, so this module breaks the cycle: it puts the
# checkout on sys.path *first*, using its own copy of the search
# logic.  After preload_local_big() returns, "from big import test"
# resolves to the checkout, and everything else comes from there.
#
# run() and finish() are kept as delegates so a test module works
# the same whether it goes through big.test directly or through
# here.  (They import big.test lazily: at the time bigtestlib is
# imported, the checkout isn't on the path yet.)
#

import pathlib
import sys


def preload_local_big():
    """
    Pre-load the local "big" module, to preclude finding
    an already-installed one on the path.
    """
    argv_0 = pathlib.Path(sys.argv[0])
    big_dir = starting_dir = argv_0.resolve().parent
    while True:
        big_init = big_dir / "big" / "__init__.py"
        if big_init.is_file():
            break
        if big_dir == big_dir.parent:
            import errno
            raise FileNotFoundError(
                errno.ENOENT,
                f"not found in {starting_dir} or any parent directory",
                "big/__init__.py")
        big_dir = big_dir.parent

    # this almost certainly *is* a git checkout
    # ... but that's not required, so don't assert it.
    # assert (big_dir / ".git" / "config").is_file()

    if big_dir not in sys.path:
        sys.path.insert(1, str(big_dir))

    import big
    assert big.__file__.startswith(str(big_dir))
    return big_dir


def run(name, module, permutations=None):
    from big import test
    return test.run(name=name, module=module, permutations=permutations)


def finish():
    from big import test
    test.finish()
