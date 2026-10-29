#!/usr/bin/env python3
#
# tests/test_cmdline.py
# Tests for big's cmdline, the artisanal mini-Appeal.
#
# Style note: every test is standalone--helpers like quiet_run and
# setup are copied into each test as local functions--so you can
# hoist an individual test into its own file and run it in
# isolation with little ceremony.

import bigtestlib
bigtestlib.preload_local_big()

import contextlib
import io
import os.path
import subprocess
import sys

import types
import big.cmdline as cmdline


UsageError = cmdline.UsageError
ConfigurationError = cmdline.ConfigurationError



def test_equals_spellings():
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

    # getopt-pure (the Appeal ruling of 2026-08-27): = is a
    # separator for LONG options only.  For a short option the rest
    # of the token binds verbatim, = and all.
    app, calls = setup()
    quiet_run(app, ['testo', '-y=STEVE'])       # oparg is '=STEVE'
    assert calls[-1]['y'] == '=STEVE'
    quiet_run(app, ['testo', '-yNAME=1'])       # think -DNAME=1
    assert calls[-1]['y'] == 'NAME=1'
    quiet_run(app, ['testo', '--color=a=b'])    # split at FIRST =
    assert calls[-1]['color'] == 'a=b'
    quiet_run(app, ['testo', '--color='])       # empty value passes
    assert calls[-1]['color'] == ''
    try:
        quiet_run(app, ['testo', '-i=5'])       # int('=5') fails
        raise AssertionError('expected UsageError')
    except UsageError as e:
        assert '=5' in str(e), str(e)


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
    quiet_run(app, ['testo', '-xy=FOO'])        # y binds '=FOO' verbatim
    assert calls[-1]['x'] is True
    assert calls[-1]['y'] == '=FOO'


def test_menagerie_bundle_oparg_taker_ends_the_bundle():
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

    # the first oparg-taker in a bundle takes the REST of the token,
    # so -yx=FOO is y='x=FOO' and x is untouched--not an error
    app, calls = setup()
    quiet_run(app, ['testo', '-yx=FOO'])
    assert calls[-1]['y'] == 'x=FOO'
    assert calls[-1]['x'] is False


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


def test_double_dash_lasts_until_the_next_command_word():
    # the Appeal rule: `--` ends option recognition for the command
    # being parsed, and the next command word turns it back on.
    # The preprecommand and the user's precommand share the region
    # before the word, so a `--` seen there carries across both of
    # them--but not into the command.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    calls = []
    app = cmdline.App()
    @app.precommand()
    def g(host):
        calls.append(('g', host))
    @app.command()
    def c(*, verbose=False):
        calls.append(('c', verbose))

    # -q is g's operand because of --; -v is c's option again
    quiet_run(app, ['--', '-q', 'c', '-v'])
    assert calls == [('g', '-q'), ('c', True)], calls

    # a dangling dash-word after -- is not an option, so the
    # diagnosis is "unknown command", not "unknown option"
    del calls[:]
    try:
        quiet_run(app, ['--', '-q', '-c'])
        raise AssertionError('expected UsageError')
    except UsageError as e:
        assert 'command' in str(e) and 'option' not in str(e), str(e)

    # -- inside a command is local to it: with repeat, the next
    # command word sees options again
    calls = []
    app = cmdline.App(repeat=True)
    @app.command()
    def a(*rest):
        calls.append(('a', rest))
    @app.command()
    def b(*, verbose=False):
        calls.append(('b', verbose))
    quiet_run(app, ['a', '--', '-x', 'b', '-v'])
    assert calls == [('a', ('-x', 'b', '-v'))], calls   # *rest is greedy
    del calls[:]
    quiet_run(app, ['b', '--', 'b', '-v'])
    assert calls == [('b', False), ('b', True)], calls


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
    # ValueError/KeyError.
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


def test_usage_leads_with_the_program_name():
    # the usage line that rides on a UsageError (and that main()
    # prints) starts with the program name--App('tool'), else
    # basename(sys.argv[0])--never with the name of the internal
    # method that happens to hold the stock options.
    app = cmdline.App('tool')
    @app.command()
    def c(a, *, zebra=False):
        pass
    try:
        app.process(['c'])
        raise AssertionError('expected UsageError')
    except UsageError as e:
        assert e.usage.startswith('tool '), e.usage
        assert 'preprecommand' not in e.usage, e.usage
        assert ' c ' in e.usage, e.usage

    saved = sys.argv
    try:
        sys.argv = ['/opt/bin/frob.py']
        app = cmdline.App()
        @app.command()
        def c(a):
            pass
        try:
            app.process(['c'])
            raise AssertionError('expected UsageError')
        except UsageError as e:
            assert e.usage.startswith('frob.py '), e.usage
    finally:
        sys.argv = saved


def test_usage_renders_an_optional_oparg_in_brackets():
    # a required oparg renders bare (-f str); an optional[T]
    # oparg renders bracketed (-j [int]), the make -j spelling.
    # The stock help option is optional[str], so it shows up on
    # every usage line.
    app = cmdline.App('tool')
    @app.command()
    def c(*, jobs: cmdline.optional[int] = 1, file=''):
        pass
    u = app.commands['c'].usage()
    assert '[int]' in u, u
    assert '[str]' not in u and ' str' in u, u
    try:
        app.process(['c', 'extra'])
        raise AssertionError('expected UsageError')
    except UsageError as e:
        assert '[-h|--help [str]]' in e.usage, e.usage


def test_listing_leads_with_the_program_name():
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    app = cmdline.App('tool')
    @app.command()
    def c():
        "Does c."
    _, out = quiet_run(app, ['help'])
    assert 'Usage: tool ' in out, out


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
    # and returns 0; map_default installs the stock default (a
    # "no command specified" UsageError, ruled 2026-10-17); a
    # user's @app.default() runs instead.
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
    try:
        quiet_run(app, [])
        raise AssertionError('expected UsageError')
    except UsageError as e:
        assert str(e) == 'no command specified', str(e)

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
    assert cmdline.App().name == os.path.basename(sys.argv[0])


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




# ----------------------------------------------------------------
# the bare command line, Appeal-style (todo item 1)
# ----------------------------------------------------------------

def test_bare_line_is_a_usage_error_with_a_hint():
    # parity with Appeal: the stock default raises "no command
    # specified"; main() renders error, blank line, usage with
    # <command> ..., and a hint pointing at the help command.
    def quiet_main(app, argv):
        out, err = io.StringIO(), io.StringIO()
        code = None
        with contextlib.redirect_stdout(out), \
             contextlib.redirect_stderr(err):
            try:
                app.main(list(argv))
            except SystemExit as e:
                code = e.code
        return code, out.getvalue(), err.getvalue()

    app = cmdline.App('tool')
    @app.command()
    def add(a, b):
        pass
    code, out, err = quiet_main(app, [])
    assert code == 2, code
    assert out == '', out
    assert err.startswith('error: no command specified\n\nusage: tool '), err
    lines = err.splitlines()
    assert lines[2].endswith(' <command> ...'), lines[2]
    assert lines[3] == "(run 'tool help' for a list of commands)", lines[3]
    assert len(lines) == 4, err

    # process() raises the structured object, no printing
    try:
        app.process([])
        raise AssertionError('expected UsageError')
    except UsageError as e:
        assert str(e) == 'no command specified', str(e)
        assert e.command is None
        assert e.usage.endswith(' <command> ...'), e.usage


def test_hint_falls_back_to_the_help_option():
    # no `help` command: the hint names --help; no --help: -h;
    # nothing mapped: no hint line at all
    def quiet_main(app, argv):
        out, err = io.StringIO(), io.StringIO()
        code = None
        with contextlib.redirect_stdout(out), \
             contextlib.redirect_stderr(err):
            try:
                app.main(list(argv))
            except SystemExit as e:
                code = e.code
        return code, out.getvalue(), err.getvalue()

    def build(policy):
        app = cmdline.App('tool', default_mappings=policy)
        @app.command()
        def add(a, b):
            pass
        return app

    def long_only(app):
        app.map_help_options()
        app.map_default()
    _, _, err = quiet_main(build(long_only), [])
    assert err.splitlines()[-1] == "(run 'tool --help' for a list of commands)", err

    def short_only(app):
        app.map_help_options('-h')
        app.map_default()
    _, _, err = quiet_main(build(short_only), [])
    assert err.splitlines()[-1] == "(run 'tool -h' for a list of commands)", err

    def nothing(app):
        app.map_default()
    _, _, err = quiet_main(build(nothing), [])
    assert err.splitlines()[-1].startswith('usage: tool'), err
    assert 'run ' not in err, err


def test_hint_rides_on_every_command_less_error():
    # the hint belongs to errors about the line as a whole (no
    # command, unknown command), not to errors inside a command
    def quiet_main(app, argv):
        out, err = io.StringIO(), io.StringIO()
        code = None
        with contextlib.redirect_stdout(out), \
             contextlib.redirect_stderr(err):
            try:
                app.main(list(argv))
            except SystemExit as e:
                code = e.code
        return code, out.getvalue(), err.getvalue()

    app = cmdline.App('tool')
    @app.command()
    def add(a, b):
        pass
    _, _, err = quiet_main(app, ['zork'])
    assert "unknown command 'zork'" in err, err
    assert err.splitlines()[-1] == "(run 'tool help' for a list of commands)", err
    _, _, err = quiet_main(app, ['add', '1'])
    assert 'requires' in err, err
    assert 'for a list of commands' not in err, err
    assert err.splitlines()[-1].startswith('usage: tool '), err
    assert ' add ' in err and '<command>' not in err, err


def test_no_commands_program_hints_at_full_usage():
    # a program with no commands never has a listing to point at;
    # the hint offers the help option "for full usage" instead
    def quiet_main(app, argv):
        out, err = io.StringIO(), io.StringIO()
        code = None
        with contextlib.redirect_stdout(out), \
             contextlib.redirect_stderr(err):
            try:
                app.main(list(argv))
            except SystemExit as e:
                code = e.code
        return code, out.getvalue(), err.getvalue()

    app = cmdline.App('tsort')
    @app.precommand()
    def tsort(file='-', *, reverse=False):
        pass
    code, _, err = quiet_main(app, ['a', 'b'])     # one operand too many
    assert code == 2, (code, err)
    assert '<command>' not in err, err
    # no commands means no dispatch: the leftover is "extra
    # arguments", never a bogus "unknown command"
    assert 'extra arguments' in err and 'unknown command' not in err, err
    assert err.splitlines()[-1] == "(run 'tsort --help' for full usage)", err


def test_no_commands_program_refuses_a_default():
    # ruled 2026-10-29: the default is what runs in place of a
    # command word; with no commands it would just be a second body
    # after the precommand.  Loud subset refusal, at the first
    # process() (when the commands are known), pointing at the fix.
    app = cmdline.App('tsort')
    @app.precommand()
    def tsort(file='-'):
        pass
    @app.default()
    def oops():
        pass
    try:
        app.process([])
        raise AssertionError('expected ConfigurationError')
    except ConfigurationError as e:
        assert 'precommand' in str(e), str(e)


def test_precommand_runs_on_a_bare_line():
    # Appeal: the precommand is called even when nothing was given
    # for it, BEFORE the default is consulted.  So a no-commands
    # program with a precommand simply runs on a bare line.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    calls = []
    app = cmdline.App('tsort')
    @app.precommand()
    def tsort(file='-', *, reverse=False):
        calls.append((file, reverse))
    result, out = quiet_run(app, [])
    assert calls == [('-', False)], calls
    assert (not result) and out == '', (result, out)   # the precommand's own return

    # with commands, the precommand still runs first, then the
    # stock default raises
    calls = []
    app = cmdline.App('tool')
    @app.precommand()
    def g(*, verbose=False):
        calls.append(verbose)
    @app.command()
    def add(a, b):
        pass
    try:
        quiet_run(app, ['-v'])
        raise AssertionError('expected UsageError')
    except UsageError as e:
        assert str(e) == 'no command specified', str(e)
    assert calls == [True], calls

    # default_mappings=None: a bare line is still a quiet 0
    calls = []
    app = cmdline.App('tool', default_mappings=None)
    @app.precommand()
    def g(*, verbose=False):
        calls.append(verbose)
    @app.command()
    def add(a, b):
        pass
    result, out = quiet_run(app, [])
    assert result == 0 and out == '' and calls == [False], (result, out, calls)


# ----------------------------------------------------------------
# optional opargs observe dashes (ruled 2026-10-20, rule A)
# ----------------------------------------------------------------

def test_optional_oparg_observes_dashes():
    # a REQUIRED oparg takes the next token unconditionally.  An
    # OPTIONAL oparg looks at the next token like a positional
    # would: an option-looking token or -- means the oparg is
    # absent.  Mirrors Appeal's make corpus.
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    calls = []
    app = cmdline.App()
    @app.command()
    def make(*targets, jobs: cmdline.optional[int] = None, verbose=False):
        calls.append((targets, jobs, verbose))

    for argv, expected in (
            (['make', '-j', '5'],         ((), 5, False)),
            (['make', '-j', '-5'],        ((), -5, False)),      # negative number
            (['make', '-j5'],             ((), 5, False)),       # attached
            (['make', '-j'],              ((), 0, False)),       # bare at the end
            (['make', '-j', '-v'],        ((), 0, True)),        # bare, then a known flag
            (['make', '-j', '-x'],        None),                 # bare, then an unknown option
            (['make', '-j', '--', '5'],   (('5',), 0, False)),   # -- ends the run; 5 is a target
            (['make', '-vj', '5'],        ((), 5, True)),        # last in a bundle, then greedy
            (['make', 'all', '-j', '2'],  (('all',), 2, False)),
            ):
        del calls[:]
        if expected is None:
            try:
                quiet_run(app, argv)
                raise AssertionError(f'{argv}: expected UsageError')
            except UsageError:
                continue
        quiet_run(app, argv)
        assert calls[-1] == expected, (argv, calls[-1])

    # never a silent reinterpretation: the greedy grab of a
    # non-option token fails loudly, it does not fall back to bare
    try:
        quiet_run(app, ['make', '-j', 'clean'])
        raise AssertionError('expected UsageError')
    except UsageError as e:
        assert 'clean' in str(e), str(e)
    try:
        quiet_run(app, ['make', '-j', '-'])       # '-' is a value; int('-') fails
        raise AssertionError('expected UsageError')
    except UsageError as e:
        assert "'-'" in str(e), str(e)


def test_optional_str_oparg_takes_dash_and_attached_dash_values():
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    calls = []
    app = cmdline.App()
    @app.command()
    def c(*, log: cmdline.optional[str] = None):
        calls.append(log)
    quiet_run(app, ['c', '-l', '-'])          # lone dash is a value
    assert calls[-1] == '-', calls
    quiet_run(app, ['c', '-l-x'])             # attached binds verbatim: the only
    assert calls[-1] == '-x', calls           # way to give a dash-leading value
    quiet_run(app, ['c', '--log=-x'])
    assert calls[-1] == '-x', calls
    quiet_run(app, ['c', '-l'])
    assert calls[-1] == '', calls


def test_required_oparg_ignores_dashes():
    # the POSIX half of the rule: a required oparg is the next
    # token no matter what it looks like
    def quiet_run(app, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = app.process(list(argv))
        return result, out.getvalue()

    calls = []
    app = cmdline.App()
    @app.command()
    def c(*, file='', verbose=False):
        calls.append((file, verbose))
    quiet_run(app, ['c', '-f', '-v'])
    assert calls[-1] == ('-v', False), calls
    quiet_run(app, ['c', '-f', '--'])
    assert calls[-1] == ('--', False), calls
    quiet_run(app, ['c', '-f', '-5'])
    assert calls[-1] == ('-5', False), calls


def test_help_option_yields_to_a_following_option():
    # -h --version: help's optional topic sees an option, so the
    # topic is absent and the listing prints (help exits first)
    def quiet_run_exit(app, argv):
        out = io.StringIO()
        code = None
        with contextlib.redirect_stdout(out):
            try:
                app.process(list(argv))
            except SystemExit as e:
                code = e.code
        return code, out.getvalue()

    app = cmdline.App('tool', version='1.0')
    @app.command()
    def encabulate():
        "Prefabulates the amulite."
    code, out = quiet_run_exit(app, ['-h', '--version'])
    assert (code or 0) == 0, code
    assert 'encabulate' in out and '1.0' not in out, out


def run_tests(run=None):
    (run or bigtestlib.run)(name='big.cmdline', module=__name__)


if __name__ == '__main__':   # pragma: no cover
    run_tests()
    bigtestlib.finish()
