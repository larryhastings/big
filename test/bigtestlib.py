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

import io
import unittest

stats = {
    "failures": 0,
    "errors": 0,
    "expected failures": 0,
    "unexpected successes": 0,
    "skipped": 0,
    }

attribute_names = {
    "failures": "failures",
    "errors": "errors",
    "expected failures": "expectedFailures",
    "unexpected successes": "unexpectedSuccesses",
    "skipped": "skipped",
    }

def run(name, module, permutations=None):
    if name:
        print(f"Testing {name}...")

    # this is a lot of work to suppress the "\nOK"!
    sio = io.StringIO()
    runner = unittest.TextTestRunner(stream=sio)
    t = unittest.main(module=module, exit=False, testRunner=runner)
    result = t.result
    for name in stats:
        value = getattr(result, attribute_names[name], ())
        stats[name] += len(value)

    for line in sio.getvalue().split("\n"):
        if not line.startswith("Ran"):
            print(line)
            continue

        if permutations:
            fields = line.split()
            assert fields[2] == "tests"
            fields[2] = f"tests, with {permutations()} total permutations,"
            line = " ".join(fields)
        print(line)
        print()
        # prevent printing the  \n and OK
        break

def finish():
    if not (stats['failures'] or stats['errors']):
        result = "OK"
    else: # pragma: no cover
        result = "FAILED"

    fields = [f"{name}={value}" for name, value in stats.items() if value]
    if fields: # pragma: no cover
        addendum = ", ".join(fields)
        result = f"{result} ({addendum})"
    print(result)
