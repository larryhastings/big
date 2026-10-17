#!/usr/bin/env python3
#
# tests/test_cmdline.py
# Tests for big's cmdline, the artisanal mini-Appeal.
# Codename: "arglet"
#
# These tests specify the SEMANTICS--the header comment's option
# menagerie, the annotation/default converter rules, the exception
# taxonomy (UsageError for the user's mistakes, ConfigurationError
# for the programmer's), and the precommand/default_mappings
# design--not the current implementation.  Tests marked
# "CURRENTLY FAILS" encode known bugs; they should start red and
# go green as cmdline grows up.  (TDD: the human writes the code,
# the tests hold the line.)
#
# Style note: every test is standalone--helpers like quiet_run and
# setup are copied into each test as local functions--so you can
# paste an individual test into its own file and run it in
# isolation with little ceremony.

import bigtestlib
bigtestlib.preload_local_big()

import contextlib
import io
import os
import subprocess
import sys


# importing cmdline currently runs its module-level test drive and
# then app.main(), which sys.exit()s--and Python evicts a module
# whose import raised, so a plain import leaves nothing behind.
# Exec the source ourselves and keep whatever got defined; when
# the demo drive moves under `if __name__ == '__main__':` this
# degenerates to an ordinary full import.  test_import_is_quiet
# pins the real fix.
import types
import big.cmdline as cmdline


UsageError = cmdline.UsageError
ConfigurationError = cmdline.ConfigurationError



# ----------------------------------------------------------------
# the option menagerie (the header's spec)
# ----------------------------------------------------------------

def test_menagerie_equals_spellings():
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    def setup():
        calls = []
        app = cmdline.App()
        @app.command()
        def testo(*, x=False, y='', color='', indent=4):
            calls.append(dict(x=x, y=y, color=color, indent=indent))
        return app, calls

    app, calls = setup()
    quiet_run(app, ['testo', '-y=STEVE'])       # = stripped
    assert calls[-1]['y'] == 'STEVE'
    quiet_run(app, ['testo', '-y==STEVE'])      # value starts with =
    assert calls[-1]['y'] == '=STEVE'
    quiet_run(app, ['testo', '--color=a=b'])    # split at FIRST =
    assert calls[-1]['color'] == 'a=b'
    quiet_run(app, ['testo', '--color='])       # empty value passes
    assert calls[-1]['color'] == ''


def test_menagerie_next_component_unconditionally():
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    def setup():
        calls = []
        app = cmdline.App()
        @app.command()
        def testo(*, x=False, y='', color='', indent=4):
            calls.append(dict(x=x, y=y, color=color, indent=indent))
        return app, calls

    app, calls = setup()
    quiet_run(app, ['testo', '-y', '-c'])       # even if it starts with -
    assert calls[-1]['y'] == '-c'
    quiet_run(app, ['testo', '--color', '--x'])
    assert calls[-1]['color'] == '--x'


def test_menagerie_concatenation_and_bundles():
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    def setup():
        calls = []
        app = cmdline.App()
        @app.command()
        def testo(*, x=False, y='', color='', indent=4):
            calls.append(dict(x=x, y=y, color=color, indent=indent))
        return app, calls

    app, calls = setup()
    quiet_run(app, ['testo', '-yCONCAT'])       # bundle of one
    assert calls[-1]['y'] == 'CONCAT'
    quiet_run(app, ['testo', '-xyFOO'])         # first oparg-taker
    assert calls[-1]['x'] is True               # ends the bundle,
    assert calls[-1]['y'] == 'FOO'              # rest is its oparg


def test_menagerie_bundle_with_equals():
    # CURRENTLY FAILS (the acknowledged goof): the bundling path
    # re-splits option[1:] and drops the partitioned = value.
    # -xy=FOO means -x, then -y=FOO.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    def setup():
        calls = []
        app = cmdline.App()
        @app.command()
        def testo(*, x=False, y='', color='', indent=4):
            calls.append(dict(x=x, y=y, color=color, indent=indent))
        return app, calls

    app, calls = setup()
    quiet_run(app, ['testo', '-xy=FOO'])
    assert calls[-1]['x'] is True
    assert calls[-1]['y'] == 'FOO'


def test_menagerie_bundle_equals_oparg_taker_must_be_last():
    # in "-yx=FOO", the = value belongs to the bundle's oparg-taker
    # --but 'y' takes the oparg and 'x' is still in the bundle
    # after it.  There's no sensible reading; UsageError.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    def setup():
        calls = []
        app = cmdline.App()
        @app.command()
        def testo(*, x=False, y='', color='', indent=4):
            calls.append(dict(x=x, y=y, color=color, indent=indent))
        return app, calls

    app, calls = setup()
    try:
        quiet_run(app, ['testo', '-yx=FOO'])
        assert False, 'expected UsageError'
    except UsageError:
        pass


def test_menagerie_double_dash():
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    calls = []
    @app.command()
    def grab(a, b='B'):
        calls.append((a, b))
    quiet_run(app, ['grab', '--', '-x'])        # -x is an operand now
    assert calls[-1] == ('-x', 'B')


def test_flags_store_not_default():
    # presence stores `not default`, idempotently
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    calls = []
    @app.command()
    def t(*, on=False, off=True):
        calls.append((on, off))
    quiet_run(app, ['t', '--on', '--off'])
    assert calls[-1] == (True, False)
    quiet_run(app, ['t', '--on', '--on'])       # idempotent
    assert calls[-1] == (True, True)


def test_bool_refuses_equals():
    # your design: no --flag=true zoo in cmdline.  But the user
    # typed it, so it's a UsageError, not a bare ValueError.
    # CURRENTLY FAILS: raises ValueError.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    def setup():
        calls = []
        app = cmdline.App()
        @app.command()
        def testo(*, x=False, y='', color='', indent=4):
            calls.append(dict(x=x, y=y, color=color, indent=indent))
        return app, calls

    app, calls = setup()
    try:
        quiet_run(app, ['testo', '-x=1'])
        assert False, 'expected UsageError'
    except UsageError:
        pass


# ----------------------------------------------------------------
# converters and positionals
# ----------------------------------------------------------------

def test_converter_priority():
    # annotation > type(default) > str; default None -> str
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    calls = []
    @app.command()
    def c(a: float, b=7, c_=None, *, opt: int = None):
        calls.append((a, b, c_, opt))
    quiet_run(app, ['c', '1.5', '2', 'raw', '--opt', '9'])
    assert calls[-1] == (1.5, 2, 'raw', 9)


def test_positional_counts():
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    calls = []
    @app.command()
    def c(a, b='B'):
        calls.append((a, b))
    quiet_run(app, ['c', 'x'])
    assert calls[-1] == ('x', 'B')
    quiet_run(app, ['c', 'x', 'y'])
    assert calls[-1] == ('x', 'y')


def test_too_few_arguments_is_usage_error():
    # CURRENTLY FAILS: raises ValueError, not UsageError.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    @app.command()
    def c(a, b):
        pass
    try:
        quiet_run(app, ['c', 'only'])
        assert False, 'expected UsageError'
    except UsageError:
        pass


def test_leftover_arguments_are_an_error():
    # CURRENTLY FAILS: extra operands are re-inserted and then
    # silently dropped (repeat=False) or misdispatched as command
    # words (repeat=True).  v1 Appeal's "leftover cmdline
    # arguments!" is the semantic to keep.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    @app.command()
    def c(a):
        pass
    try:
        quiet_run(app, ['c', 'x', 'EXTRA'])
        assert False, 'expected UsageError'
    except UsageError:
        pass


def test_var_positional():
    # CURRENTLY FAILS: the header promises "args works"; today
    # VAR_POSITIONAL raises ConfigurationError('unhandled kind').
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    calls = []
    @app.command()
    def c(a, *rest: int):
        calls.append((a, rest))
    quiet_run(app, ['c', 'x', '1', '2', '3'])
    assert calls[-1] == ('x', (1, 2, 3))


def test_too_few_arguments_with_var_positional():
    # with *args the maximum is infinite, so the error message
    # switches to "at least N"
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    @app.command()
    def c(a, b, *rest):
        pass
    try:
        quiet_run(app, ['c', 'only'])
        assert False, 'expected UsageError'
    except UsageError as e:
        assert 'at least' in str(e), e


def test_var_keyword_is_a_configuration_error():
    # **kwargs has no command-line spelling
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    @app.command()
    def c(**kw):
        pass
    try:
        quiet_run(app, ['c'])
        assert False, 'expected ConfigurationError'
    except ConfigurationError:
        pass


def test_stdin_dash_is_an_operand():
    # CURRENTLY FAILS: '-' is appended raw without consuming a
    # positional slot, so the NEXT operand gets THIS position's
    # converter (desync).
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    calls = []
    @app.command()
    def c(path, n: int):
        calls.append((path, n))
    quiet_run(app, ['c', '-', '5'])
    assert calls[-1] == ('-', 5)


# ----------------------------------------------------------------
# unknown options and malformed lines
# ----------------------------------------------------------------

def test_unknown_long_option_is_a_usage_error():
    # CURRENTLY FAILS: an unknown --long re-inserts, breaks, and
    # is silently dropped.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    def setup():
        calls = []
        app = cmdline.App()
        @app.command()
        def testo(*, x=False, y='', color='', indent=4):
            calls.append(dict(x=x, y=y, color=color, indent=indent))
        return app, calls

    app, calls = setup()
    try:
        quiet_run(app, ['testo', '--nope'])
        assert False, 'expected UsageError'
    except UsageError:
        pass


def test_unknown_short_option_is_a_usage_error():
    # CURRENTLY FAILS: same silent drop; and an unknown short
    # MID-bundle raises bare ValueError.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    def setup():
        calls = []
        app = cmdline.App()
        @app.command()
        def testo(*, x=False, y='', color='', indent=4):
            calls.append(dict(x=x, y=y, color=color, indent=indent))
        return app, calls

    app, calls = setup()
    for argv in (['testo', '-q'], ['testo', '-xq']):
        try:
            quiet_run(app, list(argv))
            assert False, f'expected UsageError for {argv}'
        except UsageError:
            pass


def test_missing_oparg_is_a_usage_error():
    # CURRENTLY FAILS: args.pop(0) on an empty list -> IndexError.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    def setup():
        calls = []
        app = cmdline.App()
        @app.command()
        def testo(*, x=False, y='', color='', indent=4):
            calls.append(dict(x=x, y=y, color=color, indent=indent))
        return app, calls

    app, calls = setup()
    try:
        quiet_run(app, ['testo', '--color'])
        assert False, 'expected UsageError'
    except UsageError:
        pass


def test_negative_numbers_are_operands():
    # The rule: if a token exactly matches a declared short
    # option, it's that option.  Otherwise, any token starting
    # with '-' + ASCII digit is classified by float()--throwing
    # away the result; the converter does the real conversion--
    # with underscores and non-ASCII rejected.  float() likes it:
    # operand.  float() doesn't: UsageError, right away, never
    # the bundle walk.
    # CURRENTLY FAILS: '-5' isn't a declared option, so the bundle
    # walk gives up and ends option parsing--and the leftover-drop
    # bug eats it.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    calls = []
    @app.command()
    def c(n: int, *, offset: int = 0):
        calls.append((n, offset))
    quiet_run(app, ['c', '-5'])
    assert calls[-1] == (-5, 0)
    quiet_run(app, ['c', '-o', '-3', '-5'])     # oparg unconditional,
    assert calls[-1] == (-5, -3)                # operand negative
    # ...but a DECLARED -digit short wins over the operand reading
    app2 = cmdline.App()
    calls2 = []
    @app2.command()
    def d(n: int = 0, *, jobs=False):
        calls2.append((n, jobs))
    app2.option('jobs', '-5')(d)
    quiet_run(app2, ['d', '-5'])
    assert calls2[-1] == (0, True)
    # floats and scientific notation are operands too
    app3 = cmdline.App()
    calls3 = []
    @app3.command()
    def f(x: float):
        calls3.append(x)
    quiet_run(app3, ['f', '-3.14'])
    assert calls3[-1] == -3.14
    quiet_run(app3, ['f', '-1e5'])
    assert calls3[-1] == -1e5
    # -digit tokens float() doesn't like (or with _ or non-ASCII
    # digits) are a UsageError--immediately, not "unknown option"
    for argv in (['f', '-3x'], ['f', '-1_000'], ['f', '-1٥']):
        try:
            quiet_run(app3, list(argv))
            assert False, f'expected UsageError for {argv}'
        except UsageError:
            pass


def test_dash_equals_junk_does_not_vanish():
    # CURRENTLY FAILS: '-=x' partitions to option '-', the empty
    # bundle walk inserts nothing, and the token just disappears.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    def setup():
        calls = []
        app = cmdline.App()
        @app.command()
        def testo(*, x=False, y='', color='', indent=4):
            calls.append(dict(x=x, y=y, color=color, indent=indent))
        return app, calls

    app, calls = setup()
    try:
        quiet_run(app, ['testo', '-=x'])
        assert False, 'expected UsageError'
    except UsageError:
        pass


def test_unknown_leading_option_is_a_usage_error():
    # an unknown option BEFORE any command word: the precommand
    # passes on it, and the command dispatch loop refuses to treat
    # it as a command word.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    @app.command()
    def c():
        pass
    try:
        quiet_run(app, ['--nope', 'c'])
        assert False, 'expected UsageError'
    except UsageError:
        pass


def test_unknown_command_is_a_usage_error():
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    @app.command()
    def c():
        pass
    try:
        quiet_run(app, ['zork'])
        assert False, 'expected UsageError'
    except UsageError:
        pass


# ----------------------------------------------------------------
# registration: options, commands, taxonomy
# ----------------------------------------------------------------

def test_auto_option_shapes():
    # long + short for multi-char; short only for single-char
    # ("foo(*, x) should map -x but not --x"); underscores map
    # nothing; underscore-to-dash in longs.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    calls = []
    @app.command()
    def c(*, verbose=False, x=False, dry_run=False, _secret=False):
        calls.append((verbose, x, dry_run, _secret))
    quiet_run(app, ['c', '-v', '-x', '--dry-run'])
    assert calls[-1] == (True, True, True, False)
    try:
        quiet_run(app, ['c', '--x'])
        assert False, '--x must not be mapped'
    except UsageError:
        pass
    try:
        quiet_run(app, ['c', '--_secret'])
        assert False, '_secret must not be mapped'
    except UsageError:
        pass


def test_explicit_option_and_converter():
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    last_level = -1
    def c(*, level=0):
        nonlocal last_level
        last_level = level
    app.option('level', '-L', '--loud', annotation=int)(c)
    app.command()(c)
    quiet_run(app, ['c', '-L', '3'])
    assert last_level == 3
    quiet_run(app, ['c', '--loud=4'])
    assert last_level == 4


def test_registration_errors_are_configuration_errors():
    # programmer mistakes are ConfigurationError, never bare
    # ValueError/KeyError.  CURRENTLY FAILS on all three counts.
    app = cmdline.App()
    def c(*, x=False):
        pass
    app.option('x', '-x')(c)
    try:
        app.option('x', '-x')(c)           # same string twice
        assert False, 'expected ConfigurationError'
    except ConfigurationError:
        pass
    try:
        app.option('nope', '-n')(c)        # no such parameter
        assert False, 'expected ConfigurationError'
    except ConfigurationError:
        pass
    app.command()(c)
    try:
        app.command()(c)                   # same word twice
        assert False, 'expected ConfigurationError'
    except ConfigurationError:
        pass


def test_unmappable_single_char_parameter():
    # a single-char parameter maps only its short option; if
    # another parameter already claimed that string, there's
    # nothing left to map--the programmer's mistake, so
    # ConfigurationError.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    def c(*, xylophone='', x=False):
        pass
    app.option('xylophone', '-x')(c)
    app.command()(c)
    try:
        quiet_run(app, ['c'])
        assert False, 'expected ConfigurationError'
    except ConfigurationError:
        pass


def test_usage_renders_value_for_mixed_converters():
    # one parameter reachable through options with DIFFERENT
    # converters: usage can't name a single type, so it renders
    # the generic "value".  (Reworked 2026-07-25: this is a
    # question about the usage RENDERER, so it asks
    # Command.usage() directly--a successful process() prints
    # nothing (ruling 7d), and a failing one raises.)
    app = cmdline.App()
    def c(*, level=0):
        pass
    app.option('level', '-L', annotation=int)(c)
    app.option('level', '--loud', annotation=str)(c)
    app.command()(c)
    u = app.commands['c'].usage()
    assert '-L' in u and '--loud' in u and 'value' in u, u


def test_usage_error_carries_usage():
    # parity with Appeal's DataError: a UsageError CARRIES the
    # usage text as an attribute--main() renders it to stderr,
    # while process()'s callers (tests, embedders, wrappers) get
    # the structured object.  The natural home for the
    # precommand+global+command usage assembly (ruling 7d).
    app = cmdline.App()
    @app.command()
    def c(a, *, zebra=False):
        pass
    try:
        app.process(['c'])              # missing argument
        raise AssertionError('expected UsageError')
    except UsageError as e:
        assert getattr(e, 'usage', None), 'UsageError.usage is empty'
        assert '-z' in e.usage or '--zebra' in e.usage, e.usage


def test_default_and_precommand_set_twice():
    # both are set-once; the second registration is the
    # programmer's mistake
    app = cmdline.App()
    @app.default()
    def d():
        pass
    try:
        @app.default()
        def d2():
            pass
        assert False, 'expected ConfigurationError'
    except ConfigurationError:
        pass
    @app.precommand()
    def g():
        pass
    try:
        @app.precommand()
        def g2():
            pass
        assert False, 'expected ConfigurationError'
    except ConfigurationError:
        pass


def test_default():
    # CURRENTLY FAILS three ways: the decorator returns an
    # undefined name, the "can't set twice" guard is pre-armed by
    # __init__, and run([]) calls a Command with no args.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    calls = []
    @app.default()
    def dee():
        calls.append('default')
    quiet_run(app, [])
    assert calls == ['default']


def test_precommand():
    # CURRENTLY FAILS: the decorator returns an undefined name.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    calls = []
    @app.precommand()
    def g(*, debug=False):
        calls.append(('g', debug))
    @app.command()
    def c():
        calls.append('c')
    quiet_run(app, ['--debug', 'c'])
    assert calls == [('g', True), 'c']


def test_repeat():
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App(repeat=True)
    calls = []
    @app.command()
    def a():
        calls.append('a')
    @app.command()
    def b():
        calls.append('b')
    quiet_run(app, ['a', 'b', 'a'])
    assert calls == ['a', 'b', 'a']
    # a nonzero result halts the chain
    calls.clear()
    @app.command()
    def stop():
        calls.append('stop')
        return 3
    result, _ = quiet_run(app, ['a', 'stop', 'b'])
    assert calls == ['a', 'stop'] and result == 3


# ----------------------------------------------------------------
# precommand, default mappings, help, version
# ----------------------------------------------------------------

def test_version_option_and_command():
    # --version prints the version and exit 0 (metadata, the
    # Appeal ruling); the `version` command word prints it too.
    # (-V is not stock: -h, --help, and --version are the standard.)
    def quiet_run_exit(app, argv):
        # like quiet_run, but catches SystemExit (help/version);
        # returns (exit_code, stdout), exit_code None if no exit.
        out = io.StringIO()
        code = None
        with contextlib.redirect_stdout(out):
            try:
                app.process(list(argv))
            except SystemExit as e:
                code = e.code
        return code, out.getvalue()

    app = cmdline.App(version='9.9')
    @app.command()
    def c():
        pass
    for argv in (['--version'],):
        code, out = quiet_run_exit(app, argv)
        assert code is not None, f'expected SystemExit for {argv}'
        assert (code or 0) == 0, (argv, code)
        assert '9.9' in out, (argv, out)
    code, out = quiet_run_exit(app, ['version'])
    assert '9.9' in out


def test_help_option_and_command():
    def quiet_run_exit(app, argv):
        # like quiet_run, but catches SystemExit (help/version);
        # returns (exit_code, stdout), exit_code None if no exit.
        out = io.StringIO()
        code = None
        with contextlib.redirect_stdout(out):
            try:
                app.process(list(argv))
            except SystemExit as e:
                code = e.code
        return code, out.getvalue()

    app = cmdline.App()
    @app.command()
    def encabulate():
        "Prefabulates the amulite."
    for argv in (['-h'], ['--help']):
        code, out = quiet_run_exit(app, argv)
        assert code is not None, f'expected SystemExit for {argv}'
        assert (code or 0) == 0, (argv, code)
    code, out = quiet_run_exit(app, ['help'])
    assert 'encabulate' in out
    assert 'Prefabulates the amulite.' in out


def test_help_and_version_yield_to_user_options():
    # the default mappings map -h only if the user's precommand
    # didn't claim it (and the user's -V is simply the user's).
    def quiet_run_exit(app, argv):
        # like quiet_run, but catches SystemExit (help/version);
        # returns (exit_code, stdout), exit_code None if no exit.
        out = io.StringIO()
        code = None
        with contextlib.redirect_stdout(out):
            try:
                app.process(list(argv))
            except SystemExit as e:
                code = e.code
        return code, out.getvalue()

    app = cmdline.App(version='9.9')
    calls = []
    @app.precommand()
    def g(*, hostname='', Verbose=False):
        calls.append((hostname, Verbose))
    @app.command()
    def c():
        calls.append('c')
    code, _ = quiet_run_exit(app, ['-h', 'HOST', 'c'])  # user's -h (hostname)
    assert code is None, "user's -h must not trigger help"
    assert calls[0] == ('HOST', False)
    code, _ = quiet_run_exit(app, ['-V', 'c'])          # user's -V (Verbose)
    assert code is None, "user's -V must not trigger version"
    assert calls[-2] == ('', True)


def test_stock_commands_have_proper_names():
    def quiet_run_exit(app, argv):
        # like quiet_run, but catches SystemExit (help/version);
        # returns (exit_code, stdout), exit_code None if no exit.
        out = io.StringIO()
        code = None
        with contextlib.redirect_stdout(out):
            try:
                app.process(list(argv))
            except SystemExit as e:
                code = e.code
        return code, out.getvalue()

    app = cmdline.App(version='1.0')
    @app.command()
    def c():
        "Does c."
    _, out = quiet_run_exit(app, ['help'])
    assert '_help_command' not in out and '_version_command' not in out


def test_usage_is_right_before_first_call():
    # (Reworked for ruling 7d, 2026-07-25: process() no longer
    # prints usage on successful dispatch, so the original
    # assertion surface is gone.  The INTENT stands: usage must
    # be complete--options included--before the command has ever
    # been CALLED, i.e. Command.usage() introspects on demand.)
    # "zebra", not "verbose": -v would false-match inside a
    # precommand's --version.
    app = cmdline.App()
    @app.command()
    def c(a, b='B', *, zebra=False):
        pass
    u = app.commands['c'].usage()
    assert '-z' in u and '--zebra' in u, u
    assert 'a [b]' in u, u


def test_processor_repr():
    # white-box: the debug repr shows the remaining args and the
    # ignore_options flag
    p = cmdline.Processor(['a', '-b'])
    r = repr(p)
    assert 'a' in r and '-b' in r, r
    assert 'ignore_options=False' in r, r


def test_main_exits_with_run_result():
    # main() defaults to sys.argv[1:] and sys.exit()s with
    # process()'s result
    app = cmdline.App()
    @app.command()
    def c():
        return 3
    out = io.StringIO()
    saved_argv = sys.argv
    sys.argv = ['prog', 'c']
    try:
        with contextlib.redirect_stdout(out):
            try:
                app.main()
                assert False, 'expected SystemExit'
            except SystemExit as e:
                assert e.code == 3, e.code
    finally:
        sys.argv = saved_argv


def test_main_renders_usage_errors():
    # the layering (ruled 2026-07-25): main = process +
    # politeness + exit.  process() RAISES UsageError; main()
    # catches it, renders `error: ...` plus the usage line to
    # STDERR (stdout stays clean--it may be piped), and exits 2.
    app = cmdline.App()
    @app.command()
    def c(a, *, zebra=False):
        pass
    for argv in (['c'],                  # missing argument
                 ['zork'],               # unknown command
                 ['c', 'x', '-q']):      # unknown option
        out, err = io.StringIO(), io.StringIO()
        code = None
        with contextlib.redirect_stdout(out), \
             contextlib.redirect_stderr(err):
            try:
                app.main(list(argv))
                raise AssertionError(f'expected SystemExit for {argv}')
            except SystemExit as e:
                code = e.code
            except UsageError:
                raise AssertionError(
                    f'main() must catch UsageError ({argv})')
        assert code == 2, (argv, code)
        assert 'error:' in err.getvalue(), (argv, err.getvalue())
        assert 'usage:' in err.getvalue(), (argv, err.getvalue())
        assert out.getvalue() == '', (argv, out.getvalue())


# ----------------------------------------------------------------
# the 2026-07-25 rulings (the App<->Appeal parity walk)
# ----------------------------------------------------------------

def test_version_is_the_string():
    # ruling: app.version is the version STRING (or None)--the
    # implementations live in print_version()/help(), and shared
    # default_mappings policies test `if app.version is not None`.
    app = cmdline.App(version='9.9')
    assert app.version == '9.9', app.version
    assert cmdline.App().version is None


def test_no_version_means_no_version_mappings():
    # ruling: version tokens map only if app.version is not None.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    @app.command()
    def c():
        pass
    try:
        quiet_run(app, ['--version'])
        raise AssertionError('--version mapped despite no version=')
    except UsageError:
        pass
    except SystemExit:
        raise AssertionError('--version mapped despite no version=')
    try:
        quiet_run(app, ['version'])
        raise AssertionError('version command despite no version=')
    except UsageError:
        pass


def test_print_version_prints_and_returns():
    # ruling: app.print_version() prints self.version and RETURNS
    # (argparse print_help precedent).  The exit lives in the
    # precommand; the `version` command word must NOT exit, or
    # repeat-chains die.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App(version='4.2', repeat=True)
    calls = []
    @app.command()
    def c():
        calls.append('c')
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        assert app.print_version() is None
    assert out.getvalue() == '4.2\n', out.getvalue()
    # through the command word: prints, returns, chain continues
    try:
        _, out = quiet_run(app, ['version', 'c'])
    except SystemExit:
        raise AssertionError('version COMMAND must not exit')
    assert '4.2' in out and calls == ['c']


def test_help_command_is_app_help():
    # ruling: the help command is implemented by app.help(topic='')
    # --bare prints the listing, topic prints that command's page.
    # A subclass override speaks through BOTH the word and -h.
    def quiet_run_exit(app, argv):
        out = io.StringIO()
        code = None
        with contextlib.redirect_stdout(out):
            try:
                app.process(list(argv))
            except SystemExit as e:
                code = e.code
        return code, out.getvalue()

    class Chatty(cmdline.App):
        def help(self, topic=''):
            print(f'CUSTOM[{topic}]')
    app = Chatty()
    @app.command()
    def c():
        pass
    _, out = quiet_run_exit(app, ['help'])
    assert 'CUSTOM[]' in out, out
    _, out = quiet_run_exit(app, ['help', 'c'])
    assert 'CUSTOM[c]' in out, out
    code, out = quiet_run_exit(app, ['-h', 'c'])
    assert (code or 0) == 0 and 'CUSTOM[c]' in out, (code, out)


def test_help_topic_prints_command_page():
    # the stock help(topic): the named command's page (usage line
    # at least), not the listing
    def quiet_run_exit(app, argv):
        out = io.StringIO()
        code = None
        with contextlib.redirect_stdout(out):
            try:
                app.process(list(argv))
            except SystemExit as e:
                code = e.code
        return code, out.getvalue()

    app = cmdline.App()
    @app.command()
    def encabulate(count: int = 1, *, reverse=False):
        "Prefabulates the amulite."
    _, by_word = quiet_run_exit(app, ['help', 'encabulate'])
    code, by_option = quiet_run_exit(app, ['-h', 'encabulate'])
    assert (code or 0) == 0
    assert by_word == by_option, (by_word, by_option)
    assert 'encabulate' in by_word
    assert '--reverse' in by_word, by_word


def test_default_global_mappings_is_the_stock_policy():
    # the stock policy is a plain module-scope function of the app,
    # mirroring Appeal's default_global_mappings: four map_* calls
    # plus map_default.  Passing it explicitly is the constructor's
    # default spelling.
    def quiet_run_exit(app, argv):
        out = io.StringIO()
        code = None
        with contextlib.redirect_stdout(out):
            try:
                app.process(list(argv))
            except SystemExit as e:
                code = e.code
        return code, out.getvalue()

    assert callable(cmdline.default_global_mappings)
    app = cmdline.App(version='1.0',
                     default_mappings=cmdline.default_global_mappings)
    @app.command()
    def c():
        "Does c."
    code, out = quiet_run_exit(app, ['--version'])
    assert code is not None and '1.0' in out, (code, out)
    _, out = quiet_run_exit(app, ['help'])
    assert 'Does c.' in out, out


def test_map_help_options_custom_strings():
    # a user policy picks its own help strings; the stock ones
    # are then NOT mapped
    def quiet_run_exit(app, argv):
        out = io.StringIO()
        code = None
        with contextlib.redirect_stdout(out):
            try:
                app.process(list(argv))
            except SystemExit as e:
                code = e.code
        return code, out.getvalue()

    def policy(app):
        app.map_help_options('-H', '--halp')
    app = cmdline.App(default_mappings=policy)
    @app.command()
    def c():
        "Does c."
    for argv in (['-H'], ['--halp']):
        code, out = quiet_run_exit(app, argv)
        assert (code or 0) == 0 and 'Does c.' in out, (argv, code, out)
    try:
        quiet_run_exit(app, ['-h'])
        raise AssertionError('-h mapped but was not requested')
    except UsageError:
        pass


def test_map_version_options_requires_a_version():
    # map_version_options is a no-op on a versionless app (parity
    # with Appeal: --version only where there's a version string)
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    def policy(app):
        app.map_version_options()
        app.map_version_command()
    app = cmdline.App(default_mappings=policy)
    @app.command()
    def c():
        pass
    for argv in (['--version'], ['version']):
        try:
            quiet_run(app, argv)
            raise AssertionError(f'{argv} mapped despite no version=')
        except UsageError:
            pass
        except SystemExit:
            raise AssertionError(f'{argv} mapped despite no version=')


def test_map_help_command_custom_word():
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    def policy(app):
        app.map_help_command('halp')
    app = cmdline.App(default_mappings=policy)
    @app.command()
    def c():
        "Does c."
    _, out = quiet_run(app, ['halp'])
    assert 'Does c.' in out, out
    try:
        quiet_run(app, ['help'])
        raise AssertionError('help mapped but was not requested')
    except UsageError:
        pass


def test_user_policy_selects():
    # help stuff without version stuff, even though version= is set
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    def policy(app):
        app.map_help_options()
        app.map_help_command()
    app = cmdline.App(version='1.0', default_mappings=policy)
    @app.command()
    def c():
        pass
    for argv in (['--version'], ['version']):
        try:
            quiet_run(app, argv)
            raise AssertionError(f'{argv} mapped but was not requested')
        except UsageError:
            pass
        except SystemExit:
            raise AssertionError(f'{argv} mapped but was not requested')


def test_map_methods_yield_to_user_registrations():
    # map_help_command never overwrites a user's `help` command,
    # and map_default never overwrites a user's default
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    calls = []
    app = cmdline.App()
    @app.command('help')
    def my_help():
        calls.append('help')
    @app.default()
    def my_default():
        calls.append('default')
    quiet_run(app, ['help'])
    quiet_run(app, [])
    assert calls == ['help', 'default'], calls


def test_map_default_and_the_bare_line():
    # with no default and no mappings, a bare line does nothing
    # and returns 0; map_default installs the stock default (the
    # listing, returning 1); a user's @app.default() runs instead.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App(default_mappings=None)
    @app.command()
    def c():
        "Does c."
    result, out = quiet_run(app, [])
    assert result == 0, result
    assert out == '', out

    def policy(app):
        app.map_default()
    app = cmdline.App(default_mappings=policy)
    @app.command()
    def c():
        "Does c."
    result, out = quiet_run(app, [])
    assert result == 1, result
    assert 'Does c.' in out, out

    calls = []
    app = cmdline.App()
    @app.command()
    def c():
        pass
    @app.default()
    def d():
        calls.append('d')
    result, out = quiet_run(app, [])
    assert calls == ['d'] and out == '', (calls, out)


def test_map_options_validate_strings():
    # map_* refuses malformed option strings by name, at mapping
    # time (which is the first process() call)
    app = cmdline.App(default_mappings=lambda app: app.map_help_options('help'))
    @app.command()
    def c():
        pass
    try:
        app.process(['c'])
        raise AssertionError("'help' is not an option string")
    except ConfigurationError:
        pass
    for bad in ('-', '-ab', '--x', '-?'):
        try:
            cmdline.validate_option_string(bad)
            raise AssertionError(f'{bad!r} must refuse')
        except ConfigurationError:
            pass
    for good in ('-h', '-V', '--help', '--version'):
        assert cmdline.validate_option_string(good) == good


def test_default_mappings_none_banishes():
    # parity with Appeal: default_mappings=None means NO default
    # semantics at all
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App(version='1.0', default_mappings=None)
    @app.command()
    def c():
        pass
    for argv in (['help'], ['version'], ['-h'], ['--version']):
        try:
            quiet_run(app, list(argv))
            raise AssertionError(f'{argv} mapped despite banishment')
        except UsageError:
            pass
        except SystemExit:
            raise AssertionError(f'{argv} mapped despite banishment')


def test_command_positional_name():
    # ruling: command(name=None), positional-or-keyword, None
    # sentinel--@app.command('mv') is the canonical rename
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    calls = []
    @app.command('mv')
    def move_(src, dst):
        calls.append((src, dst))
    quiet_run(app, ['mv', 'a', 'b'])
    assert calls == [('a', 'b')]
    assert 'mv' in app.commands and 'move_' not in app.commands


def test_process_defaults_to_sys_argv():
    # ruling: process(args=None) reads sys.argv[1:], like main()
    app = cmdline.App()
    calls = []
    @app.command()
    def c():
        calls.append('c')
    saved = sys.argv
    sys.argv = ['prog', 'c']
    try:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            app.process()
    finally:
        sys.argv = saved
    assert calls == ['c']


def test_app_name_positional():
    # ruling: App('tool')--the program name, positional-first,
    # spelled and stored like Appeal's
    app = cmdline.App('tool')
    assert app.name == 'tool'
    assert cmdline.App().name is None


def test_node_callable():
    # ruling: the function behind a command is spelled .callable
    # in both libraries (matches plan.callable one layer down)
    app = cmdline.App()
    @app.command()
    def c():
        pass
    assert app.commands['c'].callable is c


def test_leftover_option_error_names_the_option():
    # ruling 7a: the post-command leftover check reports the
    # OPTION token, not the command word that just ran
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    @app.command()
    def testo():
        pass
    try:
        quiet_run(app, ['testo', '-q'])
        raise AssertionError('expected UsageError')
    except UsageError as e:
        assert '-q' in str(e), e
        assert 'testo' not in str(e), e


def test_no_usage_print_on_success():
    # ruling 7d: a successful dispatch prints NOTHING but the
    # command's own output--usage belongs to errors and help
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App(version='1.0')
    @app.command()
    def c():
        print('payload')
    _, out = quiet_run(app, ['c'])
    assert out == 'payload\n', out


def test_optional_oparg_subscript():
    # Ruled 2026-08-03 (the make precedent): opargs are REQUIRED
    # by default -- `--log` with log=None demands a value, as
    # 0.6.4 did -- and the optional oparg is the MARKED spelling,
    # cmdline.optional[T]: absent -> the parameter default, bare
    # -> T() (str '', int 0), given -> T(value).  optional_str
    # stays deleted.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    assert not hasattr(cmdline, 'optional_str')
    app = cmdline.App()
    calls = []
    @app.command()
    def c(*, log=None, jobs: cmdline.optional[int] = 1):
        calls.append((log, jobs))
    quiet_run(app, ['c'])
    assert calls[-1] == (None, 1)
    quiet_run(app, ['c', '--jobs'])
    assert calls[-1] == (None, 0)
    quiet_run(app, ['c', '--jobs', '3'])
    assert calls[-1] == (None, 3)
    quiet_run(app, ['c', '--log', 'x'])
    assert calls[-1] == ('x', 1)
    try:
        quiet_run(app, ['c', '--log'])
        raise AssertionError('bare --log must require a value')
    except UsageError:
        pass


def test_option_derives_from_parameter():
    # ruling (item 1): @app.option maps STRINGS; the converter
    # comes from the parameter unless annotation= overrides
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    calls = []
    @app.command()
    def c(*, level: int = 0, loud=False):
        calls.append((level, loud))
    app.option('level', '-L')(c)
    quiet_run(app, ['c', '-L', '3'])
    assert calls[-1] == (3, False), calls[-1]


def test_shared_default_options_policy():
    # ruling (item 3): the policy signature is (app, callable,
    # name) in both libraries--one policy function, two constructors
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    def shouty(app, callable, name):
        if name.startswith('_'):
            return
        app.option(name, '--' + name.upper())(callable)
    app = cmdline.App(default_options=shouty)
    calls = []
    @app.command()
    def c(*, loud=False):
        calls.append(loud)
    quiet_run(app, ['c', '--LOUD'])
    assert calls[-1] is True
    try:
        quiet_run(app, ['c', '--loud'])
        raise AssertionError('stock long must not exist under a custom policy')
    except UsageError:
        pass


def test_option_no_strings_unmaps():
    # Ruled 2026-07-25 (and cmdline needed it first, for the
    # precommand): @app.option('foo') with zero strings means
    # "foo is a keyword-only parameter and we don't map any
    # options to it".  The explicit per-parameter unmap; the
    # default always fills.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    calls = []
    @app.command()
    def c(*, loud=False, quiet=False):
        calls.append((loud, quiet))
    app.option('quiet')(c)
    quiet_run(app, ['c', '--loud'])
    assert calls[-1] == (True, False)
    for argv in (['c', '--quiet'], ['c', '-q']):
        try:
            quiet_run(app, argv)
            raise AssertionError(f'{argv} must be unmapped')
        except UsageError:
            pass

def test_conversion_failures_raise_UsageError():
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App()
    @app.command()
    def c(a:int):
        pass

    try:
        quiet_run(app, ['c', 'xyz'])
        raise AssertionError("should have failed to convert 'xyz' to an int")
    except UsageError as e:
        assert str(e).startswith("invalid value 'xyz'")


    app = cmdline.App()
    @app.command()
    def c(*, option:int):
        pass

    try:
        quiet_run(app, ['c', '--option', 'xyz'])
        raise AssertionError("should have failed to convert 'xyz' to an int")
    except UsageError as e:
        assert str(e).startswith("invalid value 'xyz'")


    app = cmdline.App()
    @app.command()
    def c(*args:int):
        pass

    try:
        quiet_run(app, ['c', 'xyz'])
        raise AssertionError("should have failed to convert 'xyz' to an int")
    except UsageError as e:
        assert str(e).startswith("invalid value 'xyz'")




def run_tests(run=None):
    (run or bigtestlib.run)(name='big.cmdline', module=__name__)


if __name__ == '__main__':   # pragma: no cover
    run_tests()
    bigtestlib.finish()
