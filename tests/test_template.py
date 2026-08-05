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

from big.test import raises, raises_regex, subtest

import builtins
import big.all as big
from big.template import Interpolation, Statement
from big.template import parse_template_string, eval_template_string
from big.template import Formatter
import sys
import unittest


def test_parse_template_expression():
    l = list(parse_template_string('{{x}}'))
    assert len(l) == 1
    assert l[0] == Interpolation('x', debug='')
    assert repr(l[0]) == "Interpolation('x', debug='', format=None)"

    def t(s, expected):
        got = list(parse_template_string(s))
        assert expected == got

    t('', [''])
    t('hello there 1 2 3', ['hello there 1 2 3'])
    t('{{x}}', [Interpolation('x', debug='')])
    t('{{x = }}', [Interpolation('x', debug='x = ')])
    t('try a filter {{a|times3}} and another {{foo(3 | 5, "bar") = | filter1 | filters[2]}} it worked?!',
        [
        'try a filter ',
        Interpolation('a', 'times3', debug=''),
        ' and another ',
        Interpolation('foo(3 | 5, "bar")', 'filter1', 'filters[2]', debug='foo(3 | 5, "bar") = '),
        ' it worked?!',
        ])

    with raises(SyntaxError):
        t('{{a', None)

    with raises(TypeError):
        t(3.14156, None)
    with raises(TypeError):
        t(['a', 'b', 'c'], None)


def test_parse_template_format_specification():
    def t(s, expected):
        got = list(parse_template_string(s))
        assert expected == got

    # a top-level ':' introduces the format specification,
    # analogous to an f-string's
    t('{{x:>10}}', [Interpolation('x', debug='', format='>10')])
    t('{{ a | foo | bar : something }}',
        [Interpolation('a', 'foo', 'bar', debug='', format=' something ')])

    # the format spec is verbatim: whitespace and further '|' and ':'
    # characters are preserved, not parsed
    t('{{ a : x | y }}', [Interpolation('a', debug='', format=' x | y ')])
    t('{{ a : b:c }}', [Interpolation('a', debug='', format=' b:c ')])
    t('{{a:}}', [Interpolation('a', debug='', format='')])

    # nested ':' characters don't count: slices, dict displays,
    # lambdas in parentheses, and string literals keep theirs
    t('{{ a[1:2] }}', [Interpolation('a[1:2]', debug='')])
    t("{{ {'k': 1} }}", [Interpolation("{'k': 1}", debug='')])
    t('{{ (lambda x: x)(5) }}', [Interpolation('(lambda x: x)(5)', debug='')])
    t('{{ ":" }}', [Interpolation('":"', debug='')])
    t('{{ a[1:2] : ^8 }}', [Interpolation('a[1:2]', debug='', format=' ^8 ')])

    # no colon: format is None (and None != '')
    t('{{x}}', [Interpolation('x', debug='')])
    assert Interpolation('x', debug='') != Interpolation('x', debug='', format='')

    # debug '=' still works alongside a format spec
    # (debug keeps the expression text verbatim, leading space and all)
    t('{{ x = :>10}}', [Interpolation('x', debug=' x = ', format='>10')])

    # nested braces inside the spec, like f-string nested specs
    t('{{ x : {width} }}', [Interpolation('x', debug='', format=' {width} ')])

    # an empty expression is still an error, format spec or no
    with raises(SyntaxError):
        t('{{ : x }}', None)


def test_eval_template_string():
    def upper(s): return s.upper()

    globals = {
        'x': 55,
        'upper' : upper,
        'a': 23,
        'times3': lambda i: i * 3,
        'foo': lambda *a: 'abc',
        'filter1': lambda s: ''.join(reversed(s)),
        'filters': [None, None, upper, None],
    }

    locals = {
        'a': 65,
        'bar': lambda *a: 'xyz',
    }

    def t(s, expected, *, locals=None):
        got = eval_template_string(s, globals, locals)
        assert expected == got

    t('hello there 1 2 3', 'hello there 1 2 3')
    t('{{x}}', '55')
    t('{{x = }}', 'x = 55')
    t('x{{"abc" | upper }}y', 'xABCy')
    t('try a filter {{a|times3}} and another {{foo(3 | 5, "bar") = | filter1 | filters[2]}} it worked?!',
        'try a filter 69 and another foo(3 | 5, "bar") = CBA it worked?!')

    t('oh noes we need a quoted version {{ "{{"}} BUT WAIT WHAT ABOUT THE TOHER ONE HUH???!!!1 {{ "}}" }} OH OKAY',
        'oh noes we need a quoted version {{ BUT WAIT WHAT ABOUT THE TOHER ONE HUH???!!!1 }} OH OKAY')

    # format specifications apply exactly like an f-string's:
    # format(value, spec), spec verbatim
    t('{{x:>6}}', '    55')
    t('{{x:06}}', '000055')
    t('{{ a | times3 :^7}}', '  69   ')
    t('{{x = :>6}}', 'x =     55')
    # slice colons aren't format specs
    t('{{ "abcdef"[1:3] }}', 'bc')

    t('wait we need a boolean or {{ (0 | 5) }}', 'wait we need a boolean or 5')

    t('{{[1, 2, [3, 4, [5, 6]]]}}', '[1, 2, [3, 4, [5, 6]]]')

    t('{{len("abcde") = }}', 'len("abcde") = 5')

    my_builtins = {'len': lambda o: 88}
    globals['__builtins__'] = my_builtins
    t('{{len("abcde") = }}', 'len("abcde") = 88')

    my_builtins.clear()
    with raises(NameError):
        t('{{len("abcde") = }}', '')

    with raises(SyntaxError):
        t('{{a|}}', '')
    with raises(SyntaxError):
        t('{{|a}}', '')

    t('{{a}}', '65', locals=locals)
    t('{{a|bar}}', 'xyz', locals=locals)

def test_parse_template_everything():

    def t(s, expected, *,
        parse_expressions=True,
        parse_comments=True,
        parse_statements=True,
        parse_whitespace_eater=True,
        quotes=('"', "'"),
        multiline_quotes=(),
        escape="\\",
        ):

        got = list(parse_template_string(s,
            parse_expressions=parse_expressions,
            parse_comments=parse_comments,
            parse_statements=parse_statements,
            parse_whitespace_eater=parse_whitespace_eater,
            quotes=quotes,
            multiline_quotes=multiline_quotes,
            escape=escape,
            ))
        assert expected == got
        return got

    t('{{a }}{>}   {% be kind, rewind %}{>}{{z|upper}}',
        [
        Interpolation('a'),
        Statement(' be kind, rewind '),
        Interpolation('z', 'upper'),
        ]
        )

    l = t('{%hello world!%}', [Statement('hello world!')])
    assert repr(l[0]) == "Statement('hello world!')"

    t('{>}   bcf {% now from the high timberline to the deserts dry %} qqq {>}  zqf',
        [
        'bcf ',
        Statement(' now from the high timberline to the deserts dry '),
        ' qqq zqf',
        ]
        )

    t("force {# x #} multiple strings before {{ expr }}",
        [
        'force  multiple strings before ',
        Interpolation('expr'),
        ]
        )

    # quoted delimiters are ignored in statements
    t(" clear {%close now? '%}' nope, chuck testa %} ",
        [
        ' clear ',
        Statement("close now? '%}' nope, chuck testa "),
        ' ',
        ]
        )

    # don't process quotes in statements
    t("I {%was%} out of options",
        [
        'I ',
        Statement("was"),
        ' out of options',
        ],
        quotes=(),
        )
    t("Hard {%Rock'%}' cafe",
        [
        'Hard ',
        Statement("Rock'"),
        "' cafe",
        ],
        quotes=(),
        )

    # comment
    t("I wish I was a lit{# HARK HARK #}tle bit taller, I wish I was a bal{# FOO BAR #}{>}  ler",
        [
        "I wish I was a little bit taller, I wish I was a baller",
        ]
        )

    # not a delimiter!
    t("I guess I {x can't {[ complain",
        [
        "I guess I {x can't {[ complain",
        ]
        )

    # unterminated stuff

    # ending with { is fine
    t("Closing curly {", ["Closing curly {"])

    with raises(SyntaxError):
        t("empty expression {{}}", None)

    with raises(SyntaxError):
        t("empty expression except for whitespace {{  }}", None)

    with raises(SyntaxError):
        t("Unterminated comment {# argle bargle", None)
    t("Unterminated comment {# argle bargle",
        ["Unterminated comment {# argle bargle",],
        parse_comments=False)
    # regression test: improved 'where' printing for unterminated comment
    try:
        t("Unterminated comment {# argle bargle", None)
    except SyntaxError as e:
        assert "line 1 column 22" in str(e)

    with raises(SyntaxError):
        t("Unterminated expansion {{ jibber_jabber ", None)
    t("Unterminated expansion {{ jibber_jabber ",
        ["Unterminated expansion {{ jibber_jabber ",],
        parse_expressions=False)

    with raises(SyntaxError):
        t("Unterminated expansion with filter {{ fiddle | faddle ", None)
    t("Unterminated expansion with filter {{ fiddle | faddle ",
        ["Unterminated expansion with filter {{ fiddle | faddle ",],
        parse_expressions=False)

    with raises(SyntaxError):
        t("Unterminated statement {% bishi bashi ", None)
    t("Unterminated statement {% bishi bashi ",
        ["Unterminated statement {% bishi bashi ",],
        parse_statements=False)

    with raises(SyntaxError):
        t("Unterminated statement with quotes disabled {% splish splash ", None, quotes=())
    t("Unterminated statement with quotes disabled {% splish splash ",
        ["Unterminated statement with quotes disabled {% splish splash ",],
        parse_statements=False,
        quotes=(),)

    with raises(SyntaxError):
        t("Unterminated quote in statement {% 'beep boop %}", None)
    t("Unterminated quote in statement {% 'beep boop %}",
        ["Unterminated quote in statement {% 'beep boop %}",],
        parse_statements=False)

    # regression: a bare {% at end-of-string is unterminated,
    # not a phantom empty statement.  (it used to yield
    # Statement('') because the whole find-the-%} scan --
    # including its unterminated-statement error -- was skipped
    # when nothing followed the '{%'.)
    with raises(SyntaxError):
        t("{%", None)
    try:
        t("trailing fat-finger {%", None)
    except SyntaxError as e:
        assert "unterminated statement" in str(e)
        assert "line 1 column 21" in str(e)
    t("trailing fat-finger {%",
        ["trailing fat-finger {%",],
        parse_statements=False)
    # ...while a genuinely empty statement is still legal.
    t("{%%}", [Statement('')])

    # every kind of unclosed open delimiter inside an expression
    # is an unterminated expression: the }} that would close the
    # interpolation is consumed by the delimiter stack instead.
    for template in (
        "{{ a( }}",
        "{{ a[ }}",
        "{{ {'k': 1 }}",
        "{{ a(b[c }}",      # nested and unclosed
        ):
        with raises(SyntaxError) as cm:
            t(template, None)
        assert "unterminated expression" in str(cm.exception)

    # a close delimiter inside a quoted string doesn't close:
    # }} inside a quoted string in an expression is just text...
    t("{{ 'a}}b' }}", [Interpolation("'a}}b'")])
    t('{{ "close: }}" | repr }}', [Interpolation('"close: }}"', 'repr')])
    # ...and %} inside a quoted string in a statement is too.
    t("{% echo '%}' done %}", [Statement(" echo '%}' done ")])

    # regression: turn TokenError into SyntaxError.
    # these only raise
    try:
        t('{{   """ }}', None)
    except SyntaxError as e:
        assert 'line 1 column 6' == str(e).partition(':')[0]

    try:
        t('{{\n\n """ }}', None)
    except SyntaxError as e:
        assert 'line 3 column 2' == str(e).partition(':')[0]

def test_whitespace_eaters():
    def t(s, expected, **kwargs):
        kwargs.setdefault('parse_whitespace_eater', True)
        kwargs.setdefault('parse_statements', True)
        got = list(parse_template_string(s, **kwargs))
        assert expected == got

    # note: an eater doesn't split text into components--the
    # text on both sides coalesces.  ({>} always worked this
    # way; the new eaters inherit it.)

    # {>} eats after (shipped behavior, for contrast)
    t("a{>}   b", ['ab'])
    # {<} eats before
    t("a   {<}b", ['ab'])
    # {<>} eats both directions
    t("a   {<>}   b", ['ab'])

    # nothing to eat is fine, on any side
    t("a{<}b", ['ab'])
    t("a{<>}b", ['ab'])
    # start of string, end of string
    t("{<}b", ['b'])
    t("a   {<}", ['a'])
    t("{<>}", [])

    # {<} eats newlines and tabs too--all whitespace
    t("a\n\t \n  {<}b", ['ab'])

    # eats between components: the whitespace after a yielded
    # interpolation is still in the text buffer
    t("{{x}}   {<}!", [Interpolation('x'), '!'])
    t("{% s %}   {<}!", [Statement(' s '), '!'])

    # multi-segment buffer: the comment splits the whitespace
    # into two text segments; {<} eats through both, back to
    # the 'a'
    t("a {# c #}  {<}b", ['ab'], parse_comments=True)

    # only *adjacent* whitespace is eaten
    t("a b  {<}c", ['a bc'])

    # chains and mixtures
    t("a {>}  b {<} c", ['a b c'])
    t("a   {<>}{<>}   b", ['ab'])

    # flag off: they're just text
    t("a {<} b", ['a {<} b'], parse_whitespace_eater=False)
    t("a {<>} b", ['a {<>} b'], parse_whitespace_eater=False)

    # eval_template_string inherits them through the passthrough
    assert eval_template_string("x = {{ x }}   {<>}   !", {'x': 1},
            parse_whitespace_eater=True) == "x = 1!"

@unittest.skipIf(sys.version_info < (3, 11), "old tokenizer doesn't raise for these")
def test_syntax_errors_on_new_peg_parser(): # pragma: nocover
    # old Python parser raises a lot fewer token errors.
    # only run these tests on the new PEG parser, 3.11+.

    def t(s, *,
        parse_expressions=True,
        parse_comments=True,
        parse_statements=True,
        parse_whitespace_eater=True,
        quotes=('"', "'"),
        multiline_quotes=(),
        escape="\\",
        ):

        list(parse_template_string(s,
            parse_expressions=parse_expressions,
            parse_comments=parse_comments,
            parse_statements=parse_statements,
            parse_whitespace_eater=parse_whitespace_eater,
            quotes=quotes,
            multiline_quotes=multiline_quotes,
            escape=escape,
            ))

    try:
        t("{{      'unterminated }}")
    except SyntaxError as e:
        assert 'line 1 column 9' == str(e).partition(':')[0]

    try:
        t('{{ 0x }}')
    except SyntaxError as e:
        # yup, Python reports the error as happening at the 'x'
        assert 'line 1 column 5' == str(e).partition(':')[0]



def test_basic():
    """Basic template with no starred interpolation."""
    fmt = Formatter('{greeting}, {name}!', greeting='hello', name='world')
    assert fmt() == 'hello, world!'

def test_empty_template():
    """Empty template produces empty string."""
    fmt = Formatter('')
    assert fmt() == ''

def test_star_fill():
    """Single starred interpolation fills to width."""
    fmt = Formatter('{line*}', map={'line*': '='}, width=20)
    assert fmt() == '===================='

def test_center():
    """Two starred interpolations center text."""
    fmt = Formatter('{eq*} HELLO {eq*}', map={'eq*': '='}, width=20)
    assert fmt() == '====== HELLO ======='

def test_thirds():
    """Three starred interpolations position at 1/3."""
    fmt = Formatter('{d*}{d*}X{d*}', map={'d*': '-'}, width=20)
    assert fmt() == '------------X-------'

def test_message():
    """Template with {message}."""
    fmt = Formatter('[{prefix}] {message}', prefix='INFO')
    assert fmt('hello') == '[INFO] hello'

def test_multiline_message():
    """Multi-line message repeats the body template."""
    fmt = Formatter('> {message}')
    assert fmt('line1\nline2\nline3') == '> line1\n> line2\n> line3'

def test_prologue_body_epilogue():
    """Template with all three sections."""
    fmt = Formatter('{line*}\n| {message}\n{line*}', map={'line*': '-'}, width=20)
    result = fmt('hello')
    assert result == """
--------------------
| hello
--------------------
""".strip()

def test_no_message_raises_on_nonempty():
    """Template without {message} raises on non-empty message."""
    fmt = Formatter('{line*}', map={'line*': '='}, width=20)
    with raises(ValueError):
        fmt('oops')

def test_empty_message_no_body():
    """Template without {message} works with empty message."""
    fmt = Formatter('{line*}', map={'line*': '='}, width=20)
    assert fmt() == '=' * 20

def test_message_type_error():
    """Non-str message raises TypeError."""
    fmt = Formatter('{message}')
    with raises(TypeError):
        fmt(42)

def test_format_map():
    """format_map overrides map."""
    fmt = Formatter('{greeting}, {name}!', greeting='hello', name='world')
    assert fmt.format_map('', {'name': 'Larry'}) == 'hello, Larry!'

def test_format_map_non_dict_raises():
    """format_map raises TypeError for non-dict map."""
    fmt = Formatter('{message}')
    with raises(TypeError):
        fmt.format_map('hello', 'not a dict')

def test_message_in_format_map_raises():
    """Passing 'message' as a key in format_map raises ValueError."""
    f = Formatter('X {message} X')
    with raises(ValueError):
        f.format_map("hello!", {"message": "oopsie"})

def test_format_kwargs_override():
    """format kwargs override map."""
    fmt = Formatter('{greeting}, {name}!', greeting='hello', name='world')
    assert fmt.format('', name='Larry') == 'hello, Larry!'

def test_call_is_format():
    """__call__ is alias for format."""
    fmt = Formatter('{message}!')
    assert fmt('hi') == fmt.format('hi')

def test_repr():
    """repr is eval-roundtrippable."""
    fmt = Formatter('{line*}', {'line*': '='}, width=40)
    assert repr(fmt) == "Formatter('{line*}', {'line*': '='}, width=40)"

def test_properties():
    """Properties return correct values."""
    fmt = Formatter('{line*}', {'line*': '='}, width=40)
    assert fmt.template == '{line*}'
    assert fmt.width == 40
    assert fmt.map == {'line*': '='}
    # map returns a copy
    fmt.map['line*'] = 'X'
    assert fmt.map == {'line*': '='}

    fmt = Formatter('{greeting}, {name}!')
    assert fmt(greeting="hello", name="world") == 'hello, world!'
    assert fmt.stretch
    assert fmt.width == 79
    assert fmt.map == {}
    assert fmt.template == '{greeting}, {name}!'
    assert fmt.supported == {'greeting', 'name'}

    fmt = Formatter('{greeting}, {name}!', {'greeting': 'hello', 'name': 'Floyd'}, stretch=False, width=55, name='world')
    assert not (fmt.stretch)
    assert fmt.width == 55
    assert fmt.map == {'greeting': 'hello', 'name': 'world'}


def test_empty_starred_value_rejected():
    # an empty starred value used to construct happily and then
    # crash at format time with a bare ZeroDivisionError from
    # the fill arithmetic.  now it's rejected, by name, at both
    # entry points: construction and format_map override.
    with raises_regex(ValueError, "'x\\*' must not be empty"):
        big.Formatter('{x*}', {'x*': ''}, width=10)

    # indirectly empty--the constructor str-izes starred values.
    class Empty:
        def __str__(self):
            return ''
    with raises_regex(ValueError, "'x\\*' must not be empty"):
        big.Formatter('{x*}', {'x*': Empty()}, width=10)

    # the per-call override is the other way in.
    f = big.Formatter('{x*}', {'x*': '-'}, width=10)
    with raises_regex(ValueError, "'x\\*' must not be empty"):
        f.format_map('', {'x*': ''})
    # and the formatter still works afterwards.
    assert f() == '-' * 10

def test_wider_than_width():
    """Line already wider than width: starred interpolations become empty."""
    fmt = Formatter('{d*}XXXXXXXXXXXXXXXXXXXX{d*}', map={'d*': '-'}, width=10)
    assert fmt() == 'XXXXXXXXXXXXXXXXXXXX'

def test_exact_width():
    """Line exactly at width: starred interpolations become empty."""
    fmt = Formatter('{d*}12345{d*}', map={'d*': '-'}, width=5)
    assert fmt() == '12345'

def test_multi_char_fill():
    """Fill value longer than 1 char."""
    fmt = Formatter('{d*}', map={'d*': '-='}, width=20)
    assert fmt() == '-=-=-=-=-=-=-=-=-=-='

def test_escaped_braces():
    """Escaped braces don't trigger message detection."""
    fmt = Formatter('{{message}}')
    assert fmt() == '{message}'

def test_message_with_format_spec():
    """Message with format spec is still detected."""
    fmt = Formatter('{message:>20}')
    assert fmt('hi') == '                  hi'

def test_message_with_conversion():
    """Message with conversion is still detected."""
    fmt = Formatter('{message!s}')
    assert fmt('hi') == 'hi'

def test_message_with_conversion_and_format_spec():
    """Message with conversion and format spec is still detected."""
    fmt = Formatter('{message!s:>20}')
    assert fmt('hi') == '                  hi'

def test_star_with_format_spec_raises():
    """Starred interpolation with format spec raises."""
    with raises(ValueError):
        Formatter('{line*:>20}', map={'line*': '='})

def test_star_with_conversion_raises():
    """Starred interpolation with conversion raises."""
    with raises(ValueError):
        Formatter('{line*!r}', map={'line*': '='})

def test_undefined_star_key_raises():
    """Starred interpolation referencing undefined key raises."""
    with raises(ValueError):
        Formatter('{line*}')

def test_noncontiguous_message_raises():
    """Non-contiguous message lines raise."""
    with raises(ValueError):
        Formatter('{message}\nbreak\n{message}')

def test_map_constructor():
    """Constructor map parameter works, allowing reserved kwarg names."""
    fmt = Formatter('{width}', map={'width': 'the word width'}, width=40)
    assert fmt() == 'the word width'
    assert fmt.width == 40

def test_map_with_kwargs_override():
    """Constructor kwargs override map."""
    fmt = Formatter('{a} {b}', map={'a': '1', 'b': '2'}, a='X')
    assert fmt() == 'X 2'

def test_nested_braces_raises():
    """Nested braces raise ValueError."""
    with raises(ValueError):
        Formatter('{ {foo*}bar*}', map={'foo*': '-', 'bar*': '='})

def test_bare_star_outside_braces():
    """'foo *' outside braces is not treated as a starred interpolation."""
    fmt = Formatter('foo *{bar*}', map={'bar*': '-'}, width=20)
    assert fmt() == 'foo *---------------'

def test_no_trailing_newline():
    """Single-line template produces no trailing newline."""
    fmt = Formatter('hello {name}', name='world')
    assert fmt() == 'hello world'

def test_preserves_newlines():
    """Newlines in template are exactly preserved."""
    fmt = Formatter('a\nb\nc')
    assert fmt() == 'a\nb\nc'

def test_no_rstrip():
    """Trailing whitespace in template is preserved."""
    fmt = Formatter('hello   ')
    assert fmt() == 'hello   '

def test_multiple_different_star_keys_same_line():
    """Different starred interpolations on the same line."""
    fmt = Formatter('{line*}@{double*}@{line*}',
        map={'line*': '-', 'double*': '='}, width=18)
    assert fmt() == '-----@=====@------'

def test_multiple_same_star_key_last_unique():
    """Multiple starred interpolations, last key is different."""
    fmt = Formatter('{d*}{double*}{d*}', map={'d*': '-', 'double*': '='}, width=20)
    assert fmt() == '------=======-------'

def test_multiple_same_star_key_last_not_unique():
    """Two of the same starred interpolation."""
    fmt = Formatter('{d*}X{d*}', map={'d*': '-'}, width=11)
    assert fmt() == '-----X-----'

def test_single_star_key():
    """Single starred interpolation on a line."""
    fmt = Formatter('hello {line*}', map={'line*': '.'}, width=20)
    assert fmt() == 'hello ..............'

def test_pretty_mixed_star_keys():
    """Pretty format with mixed starred interpolations on different lines."""
    pretty = Formatter(
        "{line*}@{line*}\n{message}\n{line*}@{double*}@{line*}",
        {'line*': '-', 'double*': '='}, width=18)
    assert pretty("hello there!") == """
--------@---------
hello there!
-----@=====@------
""".strip()

def test_box_format():
    """Simulates Log's box format."""
    fmt = Formatter(
        '{prefix}+{line*}\n{prefix}| {message}\n{prefix}+{line*}',
        map={'line*': '-'}, prefix='[pfx] ',
        width=40)
    result = fmt('test message')
    assert result == """
[pfx] +---------------------------------
[pfx] | test message
[pfx] +---------------------------------
""".strip()

def test_start_format():
    """Simulates Log's start format."""
    fmt = Formatter(
        '{line*}\n{name} start at {timestamp}\n{line*}',
        map={'line*': '='}, name='Log', timestamp='2026/01/01')
    result = fmt()
    assert result == """
===============================================================================
Log start at 2026/01/01
===============================================================================
""".strip()

def test_docstring_example():
    """The example from the class docstring produces correct output."""
    fmt = Formatter('{line*}\n{name} start\n{double*}{line*}',
        {'line*': '-', 'double*': '=', 'name': 'Log'},
        width=20)
    result = fmt()
    assert result == """
--------------------
Log start
==========----------
""".strip()

def test_non_str_map_value():
    f = Formatter('hello {key} {message}', map={'key': 42})
    assert f('bartholomew') == 'hello 42 bartholomew'

def test_non_str_kwarg_value():
    f = Formatter('hello {message} {key}', key=36)
    assert f('ratfink') == 'hello ratfink 36'

def test_non_str_starred_interpolation_map_in_constructor():
    """Non-str keyword argument value raises TypeError."""
    f = Formatter('hello {message} {line*}', map={'line*': 45}, width=20)
    assert f('bessie') == 'hello bessie 4545454'

def test_non_str_starred_interpolation_in_format_map():
    """Non-str keyword argument value raises TypeError."""
    f = Formatter('hello {message} {cow*}', map={'cow*': 45}, width=20)
    assert f.format_map('myrtle', {'cow*': 86}) == 'hello myrtle 8686868'

def test_non_str_template_raises():
    """Non-str template raises TypeError."""
    with raises(TypeError):
        Formatter(42)

def test_non_int_width_raises():
    """Non-int width raises TypeError."""
    with raises(TypeError):
        Formatter('hello', width='big')

def test_zero_width_raises():
    with raises(ValueError):
        Formatter('hello', width=0)

def test_non_dict_map_raises():
    """Non-dict map raises TypeError."""
    with raises(TypeError):
        Formatter('hello', map='not a dict')

def test_non_str_map_key_raises():
    """Non-str key in map raises TypeError."""
    with raises(TypeError):
        Formatter('hello', map={42: 'value'})

def test_message_in_map_raises():
    """Non-str key in map raises TypeError."""
    with raises(ValueError):
        Formatter('hello', map={'message': 'value'})

def test_bare_star_interpolation_raises():
    """Starred interpolation with no name ({*}) raises."""
    with raises(ValueError):
        Formatter('{*}', map={'*': '-'})

def test_unrelated_map_key_doesnt_interfere():
    """A map key like 'last d*' doesn't interfere with starred interpolation."""
    fmt = Formatter('{d*}X{d*}',
        map={'d*': '-', 'last d*': 'unused'}, width=20)
    assert fmt() == '---------X----------'

def test_body_more_lines_than_message():
    """Body has more template lines than message lines: zip truncates."""
    fmt = Formatter('A {message}\nB {message}\nC {message}')
    result = fmt('only one')
    assert result == 'A only one'

def test_star_in_middle_of_key_not_starred():
    """Key like 'a * b' is not a starred interpolation."""
    fmt = Formatter('hello {a * b}', map={'a * b': 'world'})
    assert fmt() == 'hello world'

def test_message_with_trailing_space_not_detected():
    """{message } is not the same as {message}."""
    fmt = Formatter('{message }', map={'message ': 'literal'})
    # no body lines, so empty message is fine
    assert fmt() == 'literal'
    # but non-empty message should raise since there are no body lines
    with raises(ValueError):
        fmt('oops')

def test_even_remainder_distribution_across_widths():
    """Remainder is distributed evenly across expansions via Bresenham."""
    expected_results = [
        'a-b-c-d--e',
        'a-b--c-d--e',
        'a-b--c--d--e',
        'a--b--c--d--e',
        'a--b--c--d---e',
        'a--b---c--d---e',
        'a--b---c---d---e',
        'a---b---c---d---e',
        'a---b---c---d----e',
        'a---b----c---d----e',
    ]
    for width, expected in zip(range(10, 20), expected_results):
        with subtest(width=width, expected=expected):
            fmt = Formatter('a{line*}b{line*}c{line*}d{line*}e',
                map={'line*': '-'}, width=width)
            assert fmt() == expected

def test_many_starred_interpolations_balanced():
    """15 starred interpolations distribute remainder evenly."""
    fmt = Formatter(
        '{line*}{line*}{line*}{line*}{line*}{line*}{line*}our{line*}heading{line*}{line*}{line*}{line*}{line*}{line*}{line*}',
        map={'line*': '-'}, width=84)
    assert fmt() == '----------------------------------our-----heading-----------------------------------'

def test_starred_interpolation_override_at_call_time():
    """Overriding a starred interpolation value at call time changes the fill."""
    fmt = Formatter('{line*} hello {line*}', map={'line*': '-'}, width=20)
    assert fmt() == '------ hello -------'
    assert fmt.format_map('', {'line*': '='}) == '====== hello ======='

def test_zero_remainder():
    """When delta divides evenly, all expansions get equal portion."""
    # 4 expansions, width = 5 + 8 = 13, delta = 8, portion = 2, remainder = 0
    fmt = Formatter('a{d*}b{d*}c{d*}d{d*}e', map={'d*': '-'}, width=13)
    assert fmt() == 'a--b--c--d--e'

def test_delta_less_than_count():
    """When delta < count, Bresenham spreads the extra evenly."""
    # 4 expansions, width = 5 + 2 = 7, delta = 2, Bresenham distributes evenly
    fmt = Formatter('a{d*}b{d*}c{d*}d{d*}e', map={'d*': '-'}, width=7)
    assert fmt() == 'ab-cd-e'

def test_different_star_keys_remainder_distribution():
    """Different star keys still get even remainder distribution."""
    fmt = Formatter('{a*}{b*}{a*}{b*}{a*}', map={'a*': '-', 'b*': '='}, width=12)
    assert fmt() == '--==---==---'

def test_supported():
    """supported returns frozenset of all interpolation keys."""
    fmt = Formatter('{line*}\n{prefix}{message:>20}\n{line*}',
        map={'line*': '-'}, prefix='>> ')
    assert fmt.supported == frozenset({'line*', 'prefix', 'message'})

def test_supported_empty_template():
    """Empty template has empty supported set."""
    fmt = Formatter('')
    assert fmt.supported == frozenset()

def test_supported_no_message():
    """Template without {message} doesn't include 'message' in supported."""
    fmt = Formatter('{greeting}, {name}!', greeting='hello', name='world')
    assert fmt.supported == frozenset({'greeting', 'name'})

def test_supported_is_frozenset():
    """supported returns a frozenset."""
    fmt = Formatter('{message}')
    assert isinstance(fmt.supported, frozenset)

def test_empty_interpolation_raises():
    """Empty interpolation {} raises."""
    with raises(ValueError):
        Formatter('{}')

def test_positional_argument_raises():
    """Positional argument {0} raises."""
    with raises(ValueError):
        Formatter('{0}')

def test_empty_template_lines_preserved():
    """Empty lines in the template are preserved."""
    fmt = Formatter('hello\n\nworld')
    assert fmt() == 'hello\n\nworld'

def test_prefix_character_is_hash_by_default():
    """When no interpolation starts with #, the prefix character is #."""
    fmt = Formatter('{line*} {name}', map={'line*': '-'}, name='hello', width=20)
    prefix_char = fmt._prologue[0][1][0][0][0]
    assert prefix_char == '#'

def test_prefix_character_skips_collision():
    """When a key starts with #, prefix advances to $."""
    fmt = Formatter('{#1} {line*}', map={'#1': 'hello', 'line*': '-'}, width=20)
    assert fmt() == 'hello --------------'
    prefix_char = fmt._prologue[0][1][0][0][0]
    assert prefix_char == '$'

def test_prefix_character_probes_to_question_mark():
    """Prefix probes past all ASCII from # to > to land on ?."""
    keys = {}
    template_parts = []
    value = ord('a')
    for c in range(0x23, 0x3F):  # # through >
        ch = chr(c)
        if ch in '.:':
            continue
        key = f'{ch}x'
        keys[key] = chr(value)
        template_parts.append('{' + key + '}')
        value += 1
    keys['line*'] = '-'
    template_parts.insert(1, '{line*}')
    template = ''.join(template_parts)
    fmt = Formatter(template, map=keys, width=40)
    assert fmt() == 'a--------------bcdefghijklmnopqrstuvwxyz'
    prefix_char = fmt._prologue[0][1][0][0][0]
    assert prefix_char == '?'

def test_dotted_expression_detected_as_message():
    """{message.foo} is still detected as a {message} interpolation."""
    fmt = Formatter('{message.upper}')
    assert 'message' in fmt.supported
    assert bool(fmt._body)

def test_indexed_expression_detected_as_message():
    """{message[0]} is still detected as a {message} interpolation."""
    fmt = Formatter('{message[0]}')
    assert 'message' in fmt.supported
    assert bool(fmt._body)

def test_dotted_and_indexed_expression():
    """{message.foo[0]} is still detected as a {message} interpolation."""
    fmt = Formatter('{message.foo[0]}')
    assert 'message' in fmt.supported
    assert bool(fmt._body)

def test_starred_with_dot_raises():
    """Starred interpolation with dot raises."""
    with raises(ValueError):
        Formatter('{line*.foo}', map={'line*': '-'})

def test_starred_with_bracket_raises():
    """Starred interpolation with bracket raises."""
    with raises(ValueError):
        Formatter('{line*[0]}', map={'line*': '-'})

def test_supported_with_dotted_key():
    """Dotted expression has the base key in supported, not the full expression."""
    fmt = Formatter('{foo.bar} {baz[0]}', foo='x', baz='y')
    assert fmt.supported == frozenset({'foo', 'baz'})

def test_stretch():
    """Dotted expression has the base key in supported, not the full expression."""
    template = '+-before-{line*}+\n| {message} |\n+-after--{line*}+\n'

    fmt = Formatter(template, {'line*': '-'}, stretch=False, width=12)
    expected = """
+-before---+
| long message |
+-after----+
""".lstrip()
    got = fmt("long message")
    assert expected == got

    fmt = Formatter(template, {'line*': '-'}, stretch=True,  width=12)
    expected = """
+-before-------+
| long message |
+-after--------+
""".lstrip()
    got = fmt("long message")
    assert expected == got

def test_relaxed():
    fmt = Formatter('{line*}\n', {'line*': '-'}, width=12)
    with raises(ValueError):
        fmt('abcde')
    fmt = Formatter('{line*}\n', {'line*': '-'}, relaxed=True, width=12)
    got = fmt('abcde')
    assert got == '------------\n'




# ---------------------------------------------------------------
# StyleSheet (the inline character-style markup, 2026-07)
# ---------------------------------------------------------------

from big.template import (StyleSheet, style as fmt, plain,
                          plain_stylesheet, style_delimiters)


def test_stylesheet_tag_authoring():
    assert fmt('bold', 'x') == '\u2983bold\u2999x\u2984'
    assert fmt('b2', 'x') == '\u2983b2\u2999x\u2984'
    assert plain('x') == '\u2983_plain\u2999x\u2984'
    # composition: fields may contain well-formed markup
    assert fmt('bold', fmt('red', 'x'))
    # junk refused noisily
    with raises(ValueError):
        fmt('2bold', 'x')               # leading digit
    with raises(ValueError):
        fmt('bo ld', 'x')               # not alnum
    with raises(ValueError):
        fmt('bold', '\u2983oops')      # malformed markup in field
    with raises(TypeError):
        fmt('bold', 3)


def test_stylesheet_paint_and_nesting():
    ansi = StyleSheet({'bold': ('T', '\x1b[1mT\x1b[0m'),
                    'red':  ('T', '\x1b[31mT\x1b[0m')})
    # per-run painting: nested spans never damage enclosing paint
    out = ansi.render(fmt('bold', 'a ' + fmt('red', 'b') + ' c'))
    assert out == ('\x1b[1ma \x1b[0m'
                   '\x1b[1m\x1b[31mb\x1b[0m\x1b[0m'
                   '\x1b[1m c\x1b[0m')


def test_stylesheet_plain_island():
    ansi = StyleSheet({'bold': ('T', '<B>T</B>')})
    out = ansi.render(fmt('bold', 'b ' + plain('c') + ' d'))
    # the island is boring: no enclosing paint, then paint resumes
    assert out == '<B>b </B>c<B> d</B>'
    # nested paint inside the island strips too
    out = ansi.render(fmt('bold', plain(fmt('bold', 'x'))))
    assert out == 'x'


def test_stylesheet_opaque_rewrite():
    p = StyleSheet({'link': ('URL', 'TEXT', "<a href='URL'>TEXT</a>")})
    out = p.render(fmt('link', 'http://x', 'y'))
    assert out == "<a href='http://x'>y</a>"
    # single-pass substitution: a URL containing the OTHER token's
    # spelling must not be re-substituted
    out = p.render(fmt('link', 'http://TEXT.example', 'y'))
    assert out == "<a href='http://TEXT.example'>y</a>"
    # arg order in the replacement is free
    p2 = StyleSheet({'swap': ('A', 'B', 'B then A')})
    assert p2.render(fmt('swap', 'x', 'y')) == 'y then x'
    # repeated token: still one arg, but opaque (not undoable)
    p3 = StyleSheet({'twice': ('X', 'X and X')})
    assert p3.render(fmt('twice', 'q')) == 'q and q'


def test_stylesheet_default_and_plain_stylesheet():
    assert plain_stylesheet.render(fmt('bold', 'x')) == 'x'
    # unknown multi-field format: _default gets the LAST field
    assert plain_stylesheet.render(fmt('link', 'u', 'desc')) == 'desc'
    assert plain_stylesheet.render(plain('x')) == 'x'
    # a debugging _default
    dbg = StyleSheet({'_default': ('T', '<<T>>')})
    assert dbg.render(fmt('zork', 'x')) == '<<x>>'
    # no _default: unknown name raises KeyError
    with raises(KeyError):
        StyleSheet({}).render(fmt('zork', 'x'))
    # visible width is just len of the plain rendering
    assert len(plain_stylesheet.render(fmt('bold', 'abc'))) == 3


def test_stylesheet_conceptual_layering():
    # a conceptual format's replacement uses OTHER formats:
    # merge the conceptual dict over a style dict
    conceptual = {'usage': ('T', fmt('bold', 'T'))}
    styles = {'bold': ('T', '<B>T</B>'), 'red': ('T', '<R>T</R>')}
    p = StyleSheet(styles) | conceptual
    assert isinstance(p, StyleSheet)
    assert p.render(fmt('usage', 'x')) == '<B>x</B>'
    # "usage in red, not bold" is one entry away
    p['usage'] = ('T', fmt('red', 'T'))
    assert p.render(fmt('usage', 'x')) == '<R>x</R>'

def test_split_styles():
    # every whitespace-delimited word gets its own balanced span, and
    # all whitespace (the double space included) is preserved verbatim
    assert big.split_styles('⦃bold⦙This is important.  Very important.⦄') == \
        '⦃bold⦙This⦄ ⦃bold⦙is⦄ ⦃bold⦙important.⦄  ⦃bold⦙Very⦄ ⦃bold⦙important.⦄'
    # a word with no internal whitespace stays whole (mixed styling ok)
    assert big.split_styles('a⦃bold⦙b⦄c') == 'a⦃bold⦙b⦄c'
    # nested spans re-wrap per word
    assert big.split_styles('⦃bold⦙⦃italic⦙x y⦄⦄') == '⦃bold⦙⦃italic⦙x⦄⦄ ⦃bold⦙⦃italic⦙y⦄⦄'
    # plain text is untouched, whitespace and all
    assert big.split_styles('no markup  here') == 'no markup  here'

def test_join_styles():
    # split_styles then join_styles round-trips within a line
    for x in ('⦃bold⦙This is important.  Very important.⦄',
              'a ⦃bold⦙b c⦄ d', '⦃bold⦙⦃italic⦙x y⦄⦄'):
        assert big.join_styles(big.split_styles(x)) == x, x
    # merges adjacent identical spans, absorbing the space
    assert big.join_styles('⦃bold⦙This⦄ ⦃bold⦙is⦄') == '⦃bold⦙This is⦄'
    # but NEVER across a newline (each line stays self-contained)
    assert big.join_styles('⦃bold⦙a⦄ ⦃bold⦙b⦄\n⦃bold⦙c⦄') == '⦃bold⦙a b⦄\n⦃bold⦙c⦄'
    # a non-whitespace gap, or a differing stack, is a boundary
    assert big.join_styles('⦃bold⦙a⦄, ⦃bold⦙b⦄') == '⦃bold⦙a⦄, ⦃bold⦙b⦄'
    assert big.join_styles('⦃bold⦙a⦄ ⦃italic⦙b⦄') == '⦃bold⦙a⦄ ⦃italic⦙b⦄'

def test_escape_styles():
    # each delimiter is quoted by a leading open delimiter
    assert big.escape_styles('a⦃b⦙c⦄d') == 'a⦃⦃b⦃⦙c⦃⦄d'
    # parsing (rendering) turns the quoted forms back into literals
    assert big.plain_stylesheet.render(big.escape_styles('a⦃b⦙c⦄d')) == 'a⦃b⦙c⦄d'
    # style() accepts text once its delimiters are quoted
    assert big.style('bold', big.escape_styles('has ⦄ here')) == '⦃bold⦙has ⦃⦄ here⦄'
    # a quoted literal survives the split/join round-trip inside a span
    assert big.join_styles(big.split_styles('⦃bold⦙x ⦃⦄ y⦄')) == '⦃bold⦙x ⦃⦄ y⦄'

def test_ansi_low_level_maps():
    E = '\x1b'
    # each map defines the 4 attributes + the 26-color vocabulary
    hues = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'purple', 'gray']
    vocab = {'bold', 'italic', 'underline', 'strikethrough', 'white', 'black'}
    for hue in hues:
        vocab |= {hue, 'light' + hue, 'dark' + hue}
    for sheet in (big.ansi_truecolor, big.ansi_256, big.ansi_16, big.ansi_uncolored):
        assert vocab <= set(sheet), sorted(vocab - set(sheet))

    r = lambda sheet, role: sheet.render('⦃' + role + '⦙x⦄')
    # attributes are identical across every map
    for sheet in (big.ansi_truecolor, big.ansi_256, big.ansi_16, big.ansi_uncolored):
        assert r(sheet, 'bold') == f'{E}[1mx{E}[22m'
        assert r(sheet, 'strikethrough') == f'{E}[9mx{E}[29m'
    # 24-bit uses the master hex verbatim (normal red is BA0000)
    assert r(big.ansi_truecolor, 'red') == f'{E}[38;2;186;0;0mx{E}[39m'
    # 16-color: normal red -> 31, light red -> 91, orange leans bright-red
    assert r(big.ansi_16, 'red') == f'{E}[31mx{E}[39m'
    assert r(big.ansi_16, 'lightred') == f'{E}[91mx{E}[39m'
    assert r(big.ansi_16, 'orange') == f'{E}[91mx{E}[39m'
    # 256: an indexed color, red nearest-matches to 124
    assert r(big.ansi_256, 'red') == f'{E}[38;5;124mx{E}[39m'
    # uncolored keeps attributes but drops color
    assert r(big.ansi_uncolored, 'red') == 'x'
    assert r(big.ansi_uncolored, 'bold') == f'{E}[1mx{E}[22m'

def test_ansi_map_composes_under_a_theme():
    # a conceptual role resolves through the theme down to a real escape
    theme = StyleSheet({'heading': ('T', big.style('bold', big.style('lightgray', 'T')))})
    sheet = big.ansi_truecolor | theme
    assert sheet.render(big.style('heading', 'Hi')) == \
        '\x1b[1m\x1b[38;2;179;179;179mHi\x1b[39m\x1b[22m'


def test_stylesheet_validation():
    with raises(ValueError):
        StyleSheet({'bold': ('T', 'no token here')})    # unused arg
    with raises(ValueError):
        StyleSheet({'_plain': ('T', 'T')})              # reserved
    with raises(ValueError):
        StyleSheet({'2fast': ('T', 'T')})               # bad name
    with raises(ValueError):
        StyleSheet({'bold': 'notatuple'})
    with raises(ValueError):
        StyleSheet({'_default': ('A', 'B', 'A B')})     # must take 1
    with raises(ValueError):
        StyleSheet({}, delimiters='ab')                 # need 3
    # arity mismatch at render
    p = StyleSheet({'link': ('U', 'D', 'U D')})
    with raises(ValueError):
        p.render(fmt('link', 'only-one'))
    # cycles refuse by name
    c = StyleSheet({'a': ('T', fmt('b', 'T')),
                 'b': ('T', fmt('a', 'T'))})
    with raises(ValueError):
        c.render(fmt('a', 'x'))


def test_stylesheet_parse_errors_have_positions():
    p = plain_stylesheet
    with raises(ValueError):
        p.render('\u2983bold\u2999oops')       # unclosed
    with raises(ValueError):
        p.render('stray \u2984 close')          # stray close
    with raises(ValueError):
        p.render('stray \u2999 sep')            # stray separator
    with raises(ValueError):
        p.render('\u2983\u2999x\u2984')       # empty name


def test_stylesheet_callable_escape_hatch():
    p = StyleSheet({'osc8': (lambda url, text:
                          f'\x1b]8;;{url}\x07{text}\x1b]8;;\x07')})
    # a 1-tuple of a callable?  no--callables are bare values
    p2 = StyleSheet()
    p2['shout'] = lambda text: text.upper()
    assert p2.render(fmt('shout', 'hi')) == 'HI'


def test_stylesheet_custom_delimiters():
    p = StyleSheet({'bold': ('T', '<B>T</B>')}, delimiters='{|}')
    assert p.render('{bold|x}') == '<B>x</B>'
    assert p.delimiters == '{|}'
    # merge keeps the left operand's delimiters and the class
    q = p | {'red': ('T', '<R>T</R>')}
    assert isinstance(q, StyleSheet) and q.delimiters == '{|}'
    assert q.render('{red|x}') == '<R>x</R>'




def test_stylesheet_escape():
    import html
    # literal source text passes through escape; replacement
    # strings are trusted backend syntax and never escaped
    p = StyleSheet({'b': ('T', '<b>T</b>')}, escape=html.escape)
    assert p.render('1 < 2 ' + fmt('b', 'a & b')) == \
        '1 &lt; 2 <b>a &amp; b</b>'
    # the Rich-markup backend: escape [ in real text
    rich = StyleSheet({'option': ('T', '[cyan]T[/cyan]')},
                   escape=lambda s: s.replace('[', '\\['))
    out = rich.render('usage: p ' + fmt('option', '-v')
                      + ' [file]')
    assert out == 'usage: p [cyan]-v[/cyan] \\[file]'
    # escape survives merge and copy
    q = rich | {'x': ('T', 'T')}
    assert q.escape is rich.escape
    assert rich.copy().escape is rich.escape
    with raises(ValueError):
        StyleSheet({}, escape='not callable')




def test_stylesheet_transforms_and_heading_hook():
    from big.template import transforms
    hdr = '\u2983headingstyle\u2999\u2983headingtext\u2999TEXT\u2984\u2984'
    p = StyleSheet(transforms)
    p.update({
        'heading':      ('TEXT', hdr),
        'headingtext':  ('TEXT', 'TEXT:'),
        'headingstyle': ('TEXT', '<H>TEXT</H>'),
    })
    assert p.render(fmt('heading', 'Arguments')) == '<H>Arguments:</H>'
    # the hook: one override reshapes every heading, paint untouched
    cool = p | {'headingtext': ('TEXT', fmt('lower', 'TEXT'))}
    assert cool.render(fmt('heading', 'Arguments')) == '<H>arguments</H>'
    shout = p | {'headingtext': ('TEXT', fmt('upper', 'TEXT') + ':')}
    # per-run painting: the transform output and the literal ':'
    # are separate runs, each painted--seamless on a terminal,
    # visible as two spans in tag-shaped backends
    assert shout.render(fmt('heading', 'Arguments')) == \
        '<H>ARGUMENTS</H><H>:</H>'
    # title uses big's gently_title
    t2 = StyleSheet(transforms)
    assert t2.render(fmt('title', 'the quick brown fox')) == \
        'The Quick Brown Fox'


def run_tests(run=None):
    (run or bigtestlib.run)(name="big.template", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
