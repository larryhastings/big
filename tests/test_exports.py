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
bigtestlib.preload_local_big()

from big.test import subtest

import collections

import big.all


# the submodules big.all splats into its namespace
# (deprecated and metadata are deliberately not splatted)
SPLATTED_MODULES = """
    boundinnerclass
    builtin
    file
    graph
    heap
    itertools
    log
    scheduler
    snip
    state
    template
    text
    time
    tokens
    types
    version
""".strip().split()


# Known offenders, tolerated until their modules are fixed.
# These sets should only ever SHRINK; fixing a module without
# removing its entry here fails the test, on purpose.
# (Empty since 2026-07-09: scheduler's stale hand-rolled __all__
# and text's @export'ed internal generator were the only two.)
KNOWN_DUPLICATES_WITHIN_ALL = {}

KNOWN_CROSS_MODULE_COLLISIONS = set()


def modules():
    for name in SPLATTED_MODULES:
        yield name, __import__(f'big.{name}', fromlist=['x'])

def test_no_duplicates_within_module_all():
    for name, module in modules():
        with subtest(module=name):
            counter = collections.Counter(module.__all__)
            duplicates = {symbol for symbol, count in counter.items() if count > 1}
            expected = KNOWN_DUPLICATES_WITHIN_ALL.get(name, set())
            assert duplicates == expected, (f"big.{name}.__all__ duplicate entries changed: "
                f"update KNOWN_DUPLICATES_WITHIN_ALL (it should only shrink)")

def test_no_cross_module_collisions():
    owners = {}
    collisions = set()
    for name, module in modules():
        for symbol in set(module.__all__):
            if symbol in owners and owners[symbol] != name:
                collisions.add(symbol) # pragma: no cover -- only runs when the tripwire fires
            owners.setdefault(symbol, name)
    assert collisions == KNOWN_CROSS_MODULE_COLLISIONS, ("two splatted modules export the same public name--"
        "in big.all, whichever imports last wins, by accident")

def test_big_all_serves_every_export():
    for name, module in modules():
        with subtest(module=name):
            for symbol in module.__all__:
                assert getattr(big.all, symbol) is getattr(module, symbol), f"big.all.{symbol} is not big.{name}.{symbol}"


def run_tests(run=None):
    (run or bigtestlib.run)(name="big export hygiene", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
