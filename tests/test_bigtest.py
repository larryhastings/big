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

# big.test's own tests--written, naturally, in big.test style.
#
# The interesting wrinkle: these tests run *failing* tests through
# the runner on purpose, to test the failure display.  Two rules
# keep that from contaminating the real suite:
#
#   * synthetic test functions are attached to synthetic modules
#     (never named test_* at this module's top level, where the
#     runner would discover them), and
#   * the stats sandbox below saves and restores big.test.stats
#     around every synthetic run.

import bigtestlib
bigtestlib.preload_local_big()

from big import test
from big.test import raises, raises_regex

import ast
import contextlib
import io
import os
import pathlib
import sys
import tempfile
import types
import unittest


class stats_sandbox:
    "Zeroes big.test.stats for the block; restores the real tally after."
    def __enter__(self):
        self.saved = dict(test.stats)
        for key in test.stats:
            test.stats[key] = 0
        return test.stats

    def __exit__(self, exc_type, exc_value, traceback):
        test.stats.clear()
        test.stats.update(self.saved)


def synthetic_module(name="synthetic", **attributes):
    "Builds a module object with the given attributes."
    module = types.ModuleType(name)
    for attribute, value in attributes.items():
        setattr(module, attribute, value)
    return module


def run_quietly(**kwargs):
    """Runs big.test.run in a stats sandbox with stdout captured.
    Returns (captured_output, (total, failed))."""
    buffer = io.StringIO()
    with stats_sandbox():
        with contextlib.redirect_stdout(buffer):
            result = test.run(**kwargs)
        tally = dict(test.stats)
    return buffer.getvalue(), result, tally


##
## the explainer
##

def test_explain_rich_diff():
    # a failing "assert got == expected" explains with unittest's
    # type-aware diff
    got = ['alpha', 'beta', 'gamma']
    expected = ['alpha', 'BETA', 'gamma']
    try:
        assert got == expected
    except AssertionError:
        tb = sys.exc_info()[2]
    buffer = io.StringIO()
    test.explain(tb, buffer.write)
    explanation = buffer.getvalue()
    assert "Lists differ" in explanation
    assert "'beta'" in explanation
    assert "'BETA'" in explanation

def test_explain_rich_diff_with_literal():
    # one side a name, the other a literal
    got = 3
    try:
        assert got == 4
    except AssertionError:
        tb = sys.exc_info()[2]
    buffer = io.StringIO()
    test.explain(tb, buffer.write)
    assert "3 != 4" in buffer.getvalue()

def test_explain_literal_collection_operand():
    # a display literal ([...], (...), {...}) is side-effect free,
    # so it's a readable operand and gets a diff
    got = [1, 2, 3]
    try:
        assert got == [1, 99, 3]
    except AssertionError:
        tb = sys.exc_info()[2]
    buffer = io.StringIO()
    test.explain(tb, buffer.write)
    explanation = buffer.getvalue()
    assert "Lists differ" in explanation
    assert "99" in explanation

    # a dict display too
    got = {'a': 1}
    try:
        assert got == {'a': 2}
    except AssertionError:
        tb = sys.exc_info()[2]
    buffer = io.StringIO()
    test.explain(tb, buffer.write)
    explanation = buffer.getvalue()
    assert ("{'a': 1}" in explanation) and ("{'a': 2}" in explanation)

    # a NON-literal collection (contains a call) is not readable;
    # the fallback shows the safe name instead
    values = [1]
    try:
        assert values == [len('xx')]
    except AssertionError:
        tb = sys.exc_info()[2]
    buffer = io.StringIO()
    test.explain(tb, buffer.write)
    assert "values = [1]" in buffer.getvalue()

def test_explain_where_fallback():
    # a non-== assert falls back to showing the names' values
    v = (1, 2)
    try:
        assert v is None
    except AssertionError:
        tb = sys.exc_info()[2]
    buffer = io.StringIO()
    test.explain(tb, buffer.write)
    explanation = buffer.getvalue()
    assert "where:" in explanation
    assert "v = (1, 2)" in explanation

def test_explain_assert_with_message():
    # "assert a == b, msg" still explains
    a = 'x'
    b = 'y'
    try:
        assert a == b, "the message"
    except AssertionError:
        tb = sys.exc_info()[2]
    buffer = io.StringIO()
    test.explain(tb, buffer.write)
    assert "'x' != 'y'" in buffer.getvalue()

def test_explain_unsafe_operands():
    # a call inside the assert can't be safely shown; the names
    # that ARE safe still get shown by the fallback
    values = [3]
    try:
        assert min(values) == 4
    except AssertionError:
        tb = sys.exc_info()[2]
    buffer = io.StringIO()
    test.explain(tb, buffer.write)
    explanation = buffer.getvalue()
    assert "values = [3]" in explanation

def test_explain_ignores_explicit_raise():
    # an AssertionError raised by hand isn't a bare assert;
    # explain says nothing
    try:
        raise AssertionError("hand-rolled")
    except AssertionError:
        tb = sys.exc_info()[2]
    buffer = io.StringIO()
    test.explain(tb, buffer.write)
    assert buffer.getvalue() == ''

def test_explain_survives_missing_source():
    # code compiled from a string has no source for linecache;
    # explain quietly says nothing (it must never raise)
    namespace = {}
    exec(compile("def boom():\n    assert False\n", "<nowhere>", "exec"), namespace)
    try:
        namespace['boom']()
    except AssertionError:
        tb = sys.exc_info()[2]
    buffer = io.StringIO()
    test.explain(tb, buffer.write)
    assert buffer.getvalue() == ''

def test_rich_diff_odd_cases():
    frame = sys._getframe()

    # operands that compare equal by explain time: nothing to say
    a = b = 1
    node = ast.parse("assert a == b").body[0]
    assert test._rich_diff(node.test, frame) is None

    # not an == comparison
    node = ast.parse("assert a < b").body[0]
    assert test._rich_diff(node.test, frame) is None

    # an operand that isn't a name or literal
    node = ast.parse("assert a() == b").body[0]
    assert test._rich_diff(node.test, frame) is None

    # comparing raises something that isn't AssertionError:
    # nothing to say (the diff must never raise)
    class Grumpy:
        def __eq__(self, other):
            raise RuntimeError("no comparisons")
    grumpy_a = Grumpy()
    grumpy_b = Grumpy()
    node = ast.parse("assert grumpy_a == grumpy_b").body[0]
    assert test._rich_diff(node.test, sys._getframe()) is None

def test_safe_value_unknown_name():
    frame = sys._getframe()
    node = ast.parse("no_such_name_anywhere").body[0].value
    ok, value = test._safe_value(node, frame)
    assert not ok
    assert value is None

def test_register_type_equality():
    class Currency:
        def __init__(self, amount):
            self.amount = amount
        def __eq__(self, other):
            return isinstance(other, Currency) and (other.amount == self.amount)

    def assert_currency_equal(a, b, msg=None):
        if a != b:
            raise AssertionError(f"Currency mismatch! {a.amount} != {b.amount}")

    test.register_type_equality(Currency, assert_currency_equal)

    got = Currency(199)
    expected = Currency(200)
    try:
        assert got == expected
    except AssertionError:
        tb = sys.exc_info()[2]
    buffer = io.StringIO()
    test.explain(tb, buffer.write)
    assert "Currency mismatch! 199 != 200" in buffer.getvalue()


##
## raises and raises_regex
##

def test_raises():
    with raises(ValueError):
        raise ValueError("yep")

    # the context manager result carries the exception
    with raises(ValueError) as cm:
        raise ValueError("carried")
    assert str(cm.exception) == "carried"

    # the callable form works too
    def thrower(x):
        raise TypeError(f"no thanks, {x}")
    raises(TypeError, thrower, 'pal')

    # a non-raising block fails the test (with AssertionError,
    # which is what a test failure is)
    with raises(AssertionError):
        with raises(ValueError):
            pass

def test_raises_regex():
    with raises_regex(ValueError, "colour: (red|blue)"):
        raise ValueError("colour: red")
    with raises(AssertionError):
        with raises_regex(ValueError, "colour: (red|blue)"):
            raise ValueError("colour: mauve")


##
## the runner
##

def _make_exciting_module():
    # one of everything the runner understands
    def passes():
        assert 1 == 1
    def fails():
        got = 'lion'
        assert got == 'tiger'
    def skips():
        raise unittest.SkipTest('not today')
    @test.expectedFailure
    def fails_as_expected():
        assert False
    @test.expectedFailure
    def passes_unexpectedly():
        pass
    def parametrized(argument):
        raise RuntimeError("discovery must never call me") # pragma: no cover

    class OldSchool(unittest.TestCase):
        def test_case_passes(self):
            self.assertEqual(2, 2)

    return synthetic_module(
        test_passes=passes,
        test_fails=fails,
        test_skips=skips,
        test_fails_as_expected=fails_as_expected,
        test_passes_unexpectedly=passes_unexpectedly,
        test_parametrized=parametrized,
        test_not_a_function="just a string",
        OldSchoolTests=OldSchool,
        )

def test_run_one_of_everything():
    module = _make_exciting_module()
    output, (total, failed), tally = run_quietly(name="exciting", module=module)

    # 5 discovered functions (parametrized and the string skipped)
    # + 1 TestCase method
    assert total == 6
    assert failed == 1

    assert "Testing exciting..." in output
    # the markers: dot, F, x, u, s for the functions (alphabetical
    # by name), then the TestCase's own dot
    assert "F" in output
    assert "s" in output
    assert "x" in output
    assert "u" in output

    # the failure report explains the failed assert
    assert "FAIL: test_fails" in output
    assert "'lion' != 'tiger'" in output

    # the tally went to stats
    assert tally["failures"] == 1
    assert tally["skipped"] == 1
    assert tally["expected failures"] == 1
    assert tally["unexpected successes"] == 1
    assert tally["errors"] == 0

def test_run_module_by_name():
    module = synthetic_module("by_name_module", test_fine=lambda: None)
    # a lambda has no required parameters, so it's discovered
    sys.modules["by_name_module"] = module
    try:
        output, (total, failed), tally = run_quietly(module="by_name_module")
    finally:
        del sys.modules["by_name_module"]
    assert total == 1
    assert failed == 0
    assert "Ran 1 test in" in output

def test_run_testcase_failure_report():
    class Sad(unittest.TestCase):
        def test_sad(self):
            got = 11
            assert got == 22

    module = synthetic_module(SadTests=Sad)
    output, (total, failed), tally = run_quietly(module=module)
    assert total == 1
    assert failed == 1
    assert tally["failures"] == 1
    # the TestCase failure report came through, explained
    assert "11 != 22" in output

def test_run_permutations():
    module = synthetic_module(test_fine=lambda: None)
    output, result, tally = run_quietly(module=module, permutations=lambda: 8128)
    assert "with 8128 total permutations," in output

def test_run_defaults_to_main_module():
    # module=None means __main__.  point __main__ at a synthetic
    # module for the duration.
    module = synthetic_module("fake_main", test_fine=lambda: None)
    saved = sys.modules['__main__']
    sys.modules['__main__'] = module
    try:
        output, (total, failed), tally = run_quietly()
    finally:
        sys.modules['__main__'] = saved
    assert total == 1
    assert failed == 0


##
## suite and finish
##

def test_finish_ok():
    with stats_sandbox():
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            test.finish()
        assert buffer.getvalue() == "OK\n"

def test_finish_ok_with_addendum():
    with stats_sandbox():
        test.stats["skipped"] = 2
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            test.finish()
        assert buffer.getvalue() == "OK (skipped=2)\n"

def test_finish_failed_exits_nonzero():
    with stats_sandbox():
        test.stats["failures"] = 1
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            with raises(SystemExit) as cm:
                test.finish()
        assert cm.exception.code == 1
        assert buffer.getvalue() == "FAILED (failures=1)\n"

def test_suite():
    # entering hands you run; a clean exit calls finish
    with stats_sandbox():
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            with test.suite() as run:
                assert run is test.run
        assert buffer.getvalue().endswith("OK\n")

def test_suite_failure_exits_nonzero():
    module = synthetic_module(test_boom=lambda: exec("assert False"))
    with stats_sandbox():
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            with raises(SystemExit) as cm:
                with test.suite() as run:
                    run(module=module)
        assert cm.exception.code == 1
        assert "FAILED (failures=1)" in buffer.getvalue()

def test_suite_propagates_exceptions_without_finishing():
    # an exception in the block propagates; finish() is NOT called
    # (no summary, no SystemExit)
    with stats_sandbox():
        test.stats["failures"] = 1
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            with raises(RuntimeError):
                with test.suite() as run:
                    raise RuntimeError("the driver itself broke")
        assert buffer.getvalue() == ''


def test_subtest():
    # labels are appended to a failing assert's message...
    with raises(AssertionError) as cm:
        with test.subtest(flavor='lime', batch=3):
            assert False
    assert "[subtest: flavor='lime', batch=3]" in str(cm.exception)

    # ...including an assert that already had a message
    with raises(AssertionError) as cm:
        with test.subtest(flavor='lime'):
            assert False, "the custard collapsed"
    assert str(cm.exception) == "the custard collapsed  [subtest: flavor='lime']"

    # a passing block is a no-op
    with test.subtest(flavor='lime'):
        pass

    # non-AssertionError exceptions pass through untouched
    with raises(ValueError) as cm:
        with test.subtest(flavor='lime'):
            raise ValueError("unrelated")
    assert str(cm.exception) == "unrelated"

    # a positional message works, like unittest's subTest
    with raises(AssertionError) as cm:
        with test.subtest('the lime one', batch=3):
            assert False
    assert "[subtest: 'the lime one', batch=3]" in str(cm.exception)

    # at most one positional
    with raises(TypeError):
        test.subtest('one', 'two')

    # no labels, no decoration
    with raises(AssertionError) as cm:
        with test.subtest():
            assert False
    assert str(cm.exception) == ""


##
## preload
##

def test_preload():
    with tempfile.TemporaryDirectory() as tmpdir:
        # a fake project: checkout/mypackage/__init__.py,
        # with the "script" in checkout/tests/
        checkout = pathlib.Path(tmpdir) / "checkout"
        package = checkout / "olfactory"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("scent = 'petrichor'\n")
        tests_dir = checkout / "tests"
        tests_dir.mkdir()

        saved_argv0 = sys.argv[0]
        saved_path = list(sys.path)
        sys.argv[0] = str(tests_dir / "test_nose.py")
        try:
            directory = test.preload("olfactory")
            assert directory == checkout
            assert str(checkout) in sys.path
            import olfactory
            assert olfactory.scent == 'petrichor'

            # preloading again doesn't add a second path entry
            test.preload("olfactory")
            assert sys.path.count(str(checkout)) == 1
        finally:
            sys.argv[0] = saved_argv0
            sys.path[:] = saved_path
            sys.modules.pop("olfactory", None)

def test_preload_not_found():
    with tempfile.TemporaryDirectory() as tmpdir:
        saved_argv0 = sys.argv[0]
        sys.argv[0] = str(pathlib.Path(tmpdir) / "test_nothing.py")
        try:
            with raises(FileNotFoundError):
                test.preload("no_such_package_anywhere_honest")
        finally:
            sys.argv[0] = saved_argv0


##
## the hooks
##

def test_excepthook():
    # the installed excepthook prints the normal traceback, then
    # the explanation, for uncaught AssertionErrors...
    got = 'north'
    try:
        assert got == 'south'
    except AssertionError as e:
        error = e
        tb = sys.exc_info()[2]
    buffer = io.StringIO()
    with contextlib.redirect_stderr(buffer):
        test._excepthook(AssertionError, error, tb)
    output = buffer.getvalue()
    assert "Traceback" in output
    assert "'north' != 'south'" in output

    # ...and doesn't explain other exception types
    try:
        raise ValueError("no explaining this")
    except ValueError as e:
        error = e
        tb = sys.exc_info()[2]
    buffer = io.StringIO()
    with contextlib.redirect_stderr(buffer):
        test._excepthook(ValueError, error, tb)
    assert "where:" not in buffer.getvalue()


def run_tests(run=None):
    (run or test.run)(name="big.test", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    test.finish()
