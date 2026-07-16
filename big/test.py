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

"""
big.test -- a tiny, low-ceremony test harness.

You can test the way you write code, not the way unittest insists:

  * bare "assert a == b", never self.assertWhicheverOne(),
  * "with raises(ValueError):" instead of self.assertRaises,
  * no mandatory base class, no mandatory methods, no mandatory main(),
  * plain "def test_foo(): ..." functions are first-class,
  * on a failing assert you get the SAME rich, type-aware diff
    unittest's assertEqual gives you (we reuse unittest's own
    machinery),
  * and you get that diff even with *zero* ceremony -- a file that
    just does "import big.test" and then bare module-level asserts
    gets it, because importing big.test installs an excepthook.

A test file looks like this:

    import big.test
    big.test.preload('mypackage')     # local checkout beats installed
    from big.test import raises

    import mypackage

    def test_frobnicate():
        got = mypackage.frobnicate('a', 'b')
        assert got == 'ab'

    def test_bad_input_rejected():
        with raises(ValueError):
            mypackage.frobnicate('a', None)

    if __name__ == '__main__':
        big.test.main()

and a multi-module test driver looks like this:

    import big.test
    big.test.preload('mypackage')

    import test_basics, test_parsing

    with big.test.suite() as run:
        run(name='mypackage.basics',  module=test_basics)
        run(name='mypackage.parsing', module=test_parsing)

Leaving the "with" block prints the summary and exits nonzero if
anything failed.

One habit makes the rich diffs work: bind, then assert.

    got = mypackage.frobnicate('a', 'b')
    assert got == expected

The explainer reads operand values out of the dead frame; it never
re-evaluates the asserted expression (so no side effects fire).
That means it can only show operands that are *names* or
*literals* -- a call expression inside the assert can't be safely
shown.

big.test is stdlib-only.  unittest.TestCase classes still work if
you want them -- run() runs plain test functions and TestCase
subclasses in one tally.
"""

import ast
import importlib
import inspect
import io
import linecache
import pathlib
import sys
import time
import traceback as _traceback
import unittest

__all__ = [
    "TestCase", "skip", "skipIf", "skipUnless", "expectedFailure",
    "raises", "raises_regex", "preload", "run", "suite", "subtest",
    "finish", "main", "stats", "register_type_equality", "explain",
    "ExplainResult",
]

# re-exports, so a test file needn't also "import unittest"
TestCase = unittest.TestCase
skip = unittest.skip
skipIf = unittest.skipIf
skipUnless = unittest.skipUnless
expectedFailure = unittest.expectedFailure


def preload(package):
    """
    Puts the local checkout of `package` on sys.path, so the tests
    run against the source tree instead of an installed copy.

    Searches for `package`/__init__.py in the directory containing
    the running script (sys.argv[0]), then in each parent directory.
    Raises FileNotFoundError if it's not found.  Imports `package`
    and confirms it came from the checkout.  Returns the directory
    added to sys.path, as a pathlib.Path.

    (big's own test suite can't use this to find big--it lives in
    the very package being located--so it bootstraps with its own
    copy of this logic, in tests/bigtestlib.py.  Every *other*
    package is paradox-free.)
    """
    argv_0 = pathlib.Path(sys.argv[0])
    directory = starting_dir = argv_0.resolve().parent
    while True:
        init = directory / package / "__init__.py"
        if init.is_file():
            break
        if directory == directory.parent:
            import errno
            raise FileNotFoundError(
                errno.ENOENT,
                f"not found in {starting_dir} or any parent directory",
                f"{package}/__init__.py")
        directory = directory.parent

    if str(directory) not in sys.path:
        sys.path.insert(1, str(directory))

    module = importlib.import_module(package)
    assert module.__file__.startswith(str(directory))
    return directory


##
## The explainer.  Given a traceback whose deepest frame raised an
## AssertionError from a bare `assert`, print the operands' values
## and, for an `==` assertion, unittest's rich type-aware diff.
##
## Everything is read from the failed frame or handed to unittest; we
## never re-evaluate the asserted expression, so no side effects fire.
##

# a throwaway TestCase instance, only so we can borrow assertEqual's
# beautiful difflib-based, type-aware failure messages.
class _Helper(unittest.TestCase):
    def runTest(self): # pragma: no cover
        pass
_helper = _Helper()
_helper.maxDiff = None

# "with raises(ValueError):" -- the bare-function spelling of
# self.assertRaises.  (It IS assertRaises, borrowed from the helper,
# so it also works in the callable form: raises(ValueError, fn, arg),
# and "with raises(ValueError) as cm:" still gives you cm.exception.)
raises = _helper.assertRaises
raises_regex = _helper.assertRaisesRegex


def register_type_equality(type, function):
    """
    Teach the explainer how to diff your own type, exactly like
    unittest's TestCase.addTypeEqualityFunc.  `function(a, b, msg=None)`
    should raise an AssertionError (with a nice message) when a != b.
    After this, a failing `assert a == b` on two of your objects
    prints that message.
    """
    _helper.addTypeEqualityFunc(type, function)


if sys.version_info >= (3, 8):
    def _literal(node):
        "(ok, value) if node is a literal."
        if isinstance(node, ast.Constant):
            return True, node.value
        return False, None
else: # pragma: no cover
    # 3.6 and 3.7 parse literals into per-type nodes,
    # not ast.Constant.  (and 3.12 deprecates isinstance
    # checks against these old classes, hence the fork.)
    def _literal(node):
        "(ok, value) if node is a literal."
        for klass, attribute in (
            (ast.Num, 'n'),
            (ast.Str, 's'),
            (ast.Bytes, 's'),
            (ast.NameConstant, 'value'),
            ):
            if isinstance(node, klass):
                return True, getattr(node, attribute)
        return False, None


def _safe_value(node, frame):
    """(ok, value) for a side-effect-free operand -- a name, a
    literal, or a literal collection (a list/tuple/dict/set of
    literals).  Anything else (a call, a subscript, ...) returns
    (False, None) so we don't re-run it."""
    if isinstance(node, ast.Name):
        for scope in (frame.f_locals, frame.f_globals):
            if node.id in scope:
                return True, scope[node.id]
        return False, None
    ok, value = _literal(node)
    if ok:
        return True, value
    # a display literal like [1, 2, 3] or {'a': 1}: side-effect
    # free, so ast.literal_eval can read it (and it raises for
    # anything non-literal, which we treat as unreadable).
    if isinstance(node, (ast.List, ast.Tuple, ast.Set, ast.Dict)):
        try:
            return True, ast.literal_eval(node)
        except Exception:
            return False, None
    return False, None


def _rich_diff(test, frame):
    """If `test` is `a == b` and both sides are safely readable,
    return unittest's rich diff string; else None."""
    if not (isinstance(test, ast.Compare)
            and (len(test.ops) == 1)
            and isinstance(test.ops[0], ast.Eq)):
        return None
    ok_l, left = _safe_value(test.left, frame)
    ok_r, right = _safe_value(test.comparators[0], frame)
    if not (ok_l and ok_r):
        return None
    try:
        _helper.assertEqual(left, right)
    except AssertionError as e:
        return str(e)
    except Exception:
        return None
    return None  # they compared equal after all; nothing to say


def explain(tb, write):
    """Print an explanation of a failed bare-assert to `write`
    (a callable taking a string)."""
    try:
        while tb.tb_next:
            tb = tb.tb_next
        frame = tb.tb_frame
        src = linecache.getline(frame.f_code.co_filename, tb.tb_lineno).strip()
        node = ast.parse(src).body[0]
        if not isinstance(node, ast.Assert):
            return
        diff = _rich_diff(node.test, frame)
        if diff:
            write("    " + diff.replace("\n", "\n    ") + "\n")
            return
        # fall back to showing the values of the names in the assert
        shown = []
        seen = set()
        for n in ast.walk(node.test):
            if isinstance(n, ast.Name) and (n.id not in seen):
                seen.add(n.id)
                ok, value = _safe_value(n, frame)
                if ok:
                    shown.append((n.id, value))
        if shown:
            write("    where:\n")
            for name, value in shown:
                write("        %s = %r\n" % (name, value))
    except Exception:
        pass


##
## Zero-ceremony mode: importing big.test installs an excepthook, so
## even a file that just does bare module-level asserts (no TestCase,
## no main) gets the explanation printed after the traceback.
##

_prev_excepthook = sys.excepthook
def _excepthook(etype, value, tb):
    _prev_excepthook(etype, value, tb)
    if issubclass(etype, AssertionError):
        explain(tb, sys.stderr.write)
sys.excepthook = _excepthook


##
## unittest integration: a TextTestResult that explains failures,
## made the default so unittest.TestCase classes run through run()
## (or a plain unittest.main()) get the diff on bare asserts too.
##

class ExplainResult(unittest.TextTestResult):
    def addFailure(self, test, err):
        super().addFailure(test, err)
        explain(err[2], self.stream.write)
unittest.runner.TextTestRunner.resultclass = ExplainResult


##
## The runner: runs plain "def test_*()" functions (no base class
## needed) *and* any unittest.TestCase subclasses in the module,
## in one tally.
##

stats = {
    "failures": 0,
    "errors": 0,
    "expected failures": 0,
    "unexpected successes": 0,
    "skipped": 0,
    }

_separator = "-" * 70
_double_separator = "=" * 70

def run(name=None, module=None, permutations=None):
    """
    Runs the tests in `module`.  Discovers:

        * plain "def test_*()" functions that take no required
          arguments (a function with required parameters is yours
          to call by hand, so discovery skips it), and
        * unittest.TestCase subclasses.

    `module` may be a module object, a module name (test files
    pass __name__), or None for the __main__ module.

    `name`, if given, is printed in a "Testing {name}..." banner.
    `permutations`, if given, is a zero-argument callable returning
    a number to report in the "Ran N tests" line.

    Adds the counts to big.test.stats, for finish().
    Returns (tests_run, failures_and_errors).
    """
    if module is None:
        module = sys.modules['__main__']
    elif isinstance(module, str):
        module = sys.modules[module]

    if name:
        print(f"Testing {name}...")

    started = time.perf_counter()
    total = failures = errors = skips = 0
    expected_failures = unexpected_successes = 0
    markers = []
    reports = []

    members = [(n, getattr(module, n)) for n in sorted(vars(module))]

    # plain test_* functions
    for function_name, function in members:
        if not (function_name.startswith("test_") and inspect.isfunction(function)):
            continue
        parameters = inspect.signature(function).parameters.values()
        required = [p for p in parameters
                    if (p.default is p.empty)
                    and (p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD))]
        if required:
            continue  # parametrized: you call it yourself
        total += 1
        expecting_failure = getattr(function, "__unittest_expecting_failure__", False)
        try:
            function()
        except unittest.SkipTest:
            skips += 1
            markers.append('s')
        except Exception:
            if expecting_failure:
                expected_failures += 1
                markers.append('x')
            else:
                failures += 1
                markers.append('F')
                buffer = io.StringIO()
                buffer.write(f"{_double_separator}\n")
                buffer.write(f"FAIL: {function_name} ({module.__name__})\n")
                buffer.write(f"{_separator}\n")
                _traceback.print_exc(file=buffer)
                explain(sys.exc_info()[2], buffer.write)
                reports.append(buffer.getvalue())
        else:
            if expecting_failure:
                unexpected_successes += 1
                markers.append('u')
            else:
                markers.append('.')

    # unittest.TestCase subclasses
    test_cases = [obj for n, obj in members
        if isinstance(obj, type) and issubclass(obj, unittest.TestCase) and (obj is not unittest.TestCase)]
    if test_cases:
        loader = unittest.TestLoader()
        test_suite = unittest.TestSuite()
        for test_case in test_cases:
            test_suite.addTests(loader.loadTestsFromTestCase(test_case))
        stream = io.StringIO()
        runner = unittest.TextTestRunner(stream=stream)
        result = runner.run(test_suite)
        total += result.testsRun
        failures += len(result.failures)
        errors += len(result.errors)
        skips += len(result.skipped)
        expected_failures += len(result.expectedFailures)
        unexpected_successes += len(result.unexpectedSuccesses)
        markers.append(stream.getvalue().split("\n")[0])
        # everything between the dots line and the "Ran N tests"
        # line is the failure reports
        text = stream.getvalue().partition("\n")[2]
        report = text.partition("\nRan ")[0].rstrip("-\n ")
        if report.strip():
            reports.append(report.strip("\n"))

    print("".join(markers))
    for report in reports:
        print(report)
    print(_separator)
    ran = f"Ran {total} test{'' if total == 1 else 's'}"
    if permutations:
        ran = f"{ran}, with {permutations()} total permutations,"
    print(f"{ran} in {time.perf_counter() - started:.3f}s")
    print()

    stats["failures"] += failures
    stats["errors"] += errors
    stats["skipped"] += skips
    stats["expected failures"] += expected_failures
    stats["unexpected successes"] += unexpected_successes

    return total, failures + errors


def finish():
    """
    Prints the final "OK"/"FAILED" summary from big.test.stats,
    with the nonzero counts ("OK (skipped=2)").  If there were
    failures or errors, exits with status 1.
    """
    if not (stats['failures'] or stats['errors']):
        result = "OK"
    else:
        result = "FAILED"

    fields = [f"{name}={value}" for name, value in stats.items() if value]
    if fields:
        addendum = ", ".join(fields)
        result = f"{result} ({addendum})"
    print(result)

    if stats['failures'] or stats['errors']:
        sys.exit(1)


class suite:
    """
    A context manager for a multi-module test driver.  Entering
    returns the run() callable; leaving the block calls finish():

        with big.test.suite() as run:
            run(name='mypackage.basics',  module=test_basics)
            run(name='mypackage.parsing', module=test_parsing)

    If the block raises, the exception propagates and finish()
    isn't called.
    """
    def __enter__(self):
        return run

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            finish()
        return False


class subtest:
    """
    Labels a block of a test, in the spirit of unittest's subTest:

        for value in interesting_values:
            with subtest(value=value):
                assert frobnicate(value)

    When an AssertionError escapes the block, the label (an
    optional positional message, like unittest's) and the labels
    (keyword arguments) are appended to its message, so you can
    tell *which* iteration failed.  (Unlike unittest's subTest,
    a failure still ends the test immediately; the labels are
    purely for the report.)
    """
    def __init__(self, *label, **labels):
        if len(label) > 1:
            raise TypeError(f"subtest takes at most one positional argument, not {len(label)}")
        self.label = label[0] if label else None
        self.labels = labels

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if ((exc_type is not None)
            and issubclass(exc_type, AssertionError)
            and ((self.label is not None) or self.labels)):
            pieces = []
            if self.label is not None:
                pieces.append(repr(self.label))
            pieces.extend(f"{name}={value!r}" for name, value in self.labels.items())
            rendered = f"[subtest: {', '.join(pieces)}]"
            if exc_value.args and exc_value.args[0]:
                exc_value.args = (f"{exc_value.args[0]}  {rendered}",) + exc_value.args[1:]
            else:
                exc_value.args = (rendered,)
        return False


def main(): # pragma: no cover
    """
    The standalone-file entry point: put big.test.main() at the
    bottom of a test file, under "if __name__ == '__main__':".
    Runs the file's tests and exits nonzero on failure.

    (main() deliberately does no command-line processing yet.
    When big grows its command-line argument processing module,
    main() will use it.)
    """
    run(module=sys.modules['__main__'])
    finish()
