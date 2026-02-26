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

import builtins
import big.all as big
from big.template import Interpolation, Statement
from big.template import parse_template_string, eval_template_string
from big.template import Formatter
import sys
import unittest


class BigTestTemplate(unittest.TestCase):

    maxDiff=None

    def test_parse_template_expression(self):
        l = list(parse_template_string('{{x}}'))
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0], Interpolation('x', debug=''))
        self.assertEqual(repr(l[0]), "Interpolation('x', debug='')")

        def t(s, expected):
            got = list(parse_template_string(s))
            self.assertEqual(expected, got)

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

        with self.assertRaises(SyntaxError):
            t('{{a', None)

        with self.assertRaises(TypeError):
            t(3.14156, None)
        with self.assertRaises(TypeError):
            t(['a', 'b', 'c'], None)


    def test_eval_template_string(self):
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
            self.assertEqual(expected, got)

        t('hello there 1 2 3', 'hello there 1 2 3')
        t('{{x}}', '55')
        t('{{x = }}', 'x = 55')
        t('x{{"abc" | upper }}y', 'xABCy')
        t('try a filter {{a|times3}} and another {{foo(3 | 5, "bar") = | filter1 | filters[2]}} it worked?!',
            'try a filter 69 and another foo(3 | 5, "bar") = CBA it worked?!')

        t('oh noes we need a quoted version {{ "{{"}} BUT WAIT WHAT ABOUT THE TOHER ONE HUH???!!!1 {{ "}}" }} OH OKAY',
            'oh noes we need a quoted version {{ BUT WAIT WHAT ABOUT THE TOHER ONE HUH???!!!1 }} OH OKAY')

        t('wait we need a boolean or {{ (0 | 5) }}', 'wait we need a boolean or 5')

        t('{{[1, 2, [3, 4, [5, 6]]]}}', '[1, 2, [3, 4, [5, 6]]]')

        t('{{len("abcde") = }}', 'len("abcde") = 5')

        my_builtins = {'len': lambda o: 88}
        globals['__builtins__'] = my_builtins
        t('{{len("abcde") = }}', 'len("abcde") = 88')

        my_builtins.clear()
        with self.assertRaises(NameError):
            t('{{len("abcde") = }}', '')

        with self.assertRaises(SyntaxError):
            t('{{a|}}', '')
        with self.assertRaises(SyntaxError):
            t('{{|a}}', '')

        t('{{a}}', '65', locals=locals)
        t('{{a|bar}}', 'xyz', locals=locals)

    def test_parse_template_everything(self):

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
            self.assertEqual(expected, got)
            return got

        t('{{a }}{>}   {% be kind, rewind %}{>}{{z|upper}}',
            [
            Interpolation('a'),
            Statement(' be kind, rewind '),
            Interpolation('z', 'upper'),
            ]
            )

        l = t('{%hello world!%}', [Statement('hello world!')])
        self.assertEqual(repr(l[0]), "Statement('hello world!')")

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

        with self.assertRaises(SyntaxError):
            t("empty expression {{}}", None)

        with self.assertRaises(SyntaxError):
            t("empty expression except for whitespace {{  }}", None)

        with self.assertRaises(SyntaxError):
            t("Unterminated comment {# argle bargle", None)
        t("Unterminated comment {# argle bargle",
            ["Unterminated comment {# argle bargle",],
            parse_comments=False)
        # regression test: improved 'where' printing for unterminated comment
        try:
            t("Unterminated comment {# argle bargle", None)
        except SyntaxError as e:
            self.assertIn("line 1 column 22", str(e))

        with self.assertRaises(SyntaxError):
            t("Unterminated expansion {{ jibber_jabber ", None)
        t("Unterminated expansion {{ jibber_jabber ",
            ["Unterminated expansion {{ jibber_jabber ",],
            parse_expressions=False)

        with self.assertRaises(SyntaxError):
            t("Unterminated expansion with filter {{ fiddle | faddle ", None)
        t("Unterminated expansion with filter {{ fiddle | faddle ",
            ["Unterminated expansion with filter {{ fiddle | faddle ",],
            parse_expressions=False)

        with self.assertRaises(SyntaxError):
            t("Unterminated statement {% bishi bashi ", None)
        t("Unterminated statement {% bishi bashi ",
            ["Unterminated statement {% bishi bashi ",],
            parse_statements=False)

        with self.assertRaises(SyntaxError):
            t("Unterminated statement with quotes disabled {% splish splash ", None, quotes=())
        t("Unterminated statement with quotes disabled {% splish splash ",
            ["Unterminated statement with quotes disabled {% splish splash ",],
            parse_statements=False,
            quotes=(),)

        with self.assertRaises(SyntaxError):
            t("Unterminated quote in statement {% 'beep boop %}", None)
        t("Unterminated quote in statement {% 'beep boop %}",
            ["Unterminated quote in statement {% 'beep boop %}",],
            parse_statements=False)

        # regression: turn TokenError into SyntaxError.
        # these only raise
        try:
            t('{{   """ }}', None)
        except SyntaxError as e:
            self.assertEqual('line 1 column 6', str(e).partition(':')[0])

        try:
            t('{{\n\n """ }}', None)
        except SyntaxError as e:
            self.assertEqual('line 3 column 2', str(e).partition(':')[0])

    @unittest.skipIf(sys.version_info < (3, 11), "old tokenizer doesn't raise for these")
    def tests_syntax_errors_on_new_peg_parser(self): # pragma: nocover
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
            self.assertEqual('line 1 column 9', str(e).partition(':')[0])

        try:
            t('{{ 0x }}')
        except SyntaxError as e:
            # yup, Python reports the error as happening at the 'x'
            self.assertEqual('line 1 column 5', str(e).partition(':')[0])



class TestFormatter(unittest.TestCase):

    maxDiff = None

    def test_basic(self):
        """Basic template with no starred interpolation."""
        fmt = Formatter('{greeting}, {name}!', greeting='hello', name='world')
        self.assertEqual(fmt(), 'hello, world!')

    def test_empty_template(self):
        """Empty template produces empty string."""
        fmt = Formatter('')
        self.assertEqual(fmt(), '')

    def test_star_fill(self):
        """Single starred interpolation fills to width."""
        fmt = Formatter('{line*}', map={'line*': '='}, width=20)
        self.assertEqual(fmt(), '====================')

    def test_center(self):
        """Two starred interpolations center text."""
        fmt = Formatter('{eq*} HELLO {eq*}', map={'eq*': '='}, width=20)
        self.assertEqual(fmt(), '====== HELLO =======')

    def test_thirds(self):
        """Three starred interpolations position at 1/3."""
        fmt = Formatter('{d*}{d*}X{d*}', map={'d*': '-'}, width=20)
        self.assertEqual(fmt(), '------------X-------')

    def test_message(self):
        """Template with {message}."""
        fmt = Formatter('[{prefix}] {message}', prefix='INFO')
        self.assertEqual(fmt('hello'), '[INFO] hello')

    def test_multiline_message(self):
        """Multi-line message repeats the body template."""
        fmt = Formatter('> {message}')
        self.assertEqual(fmt('line1\nline2\nline3'), '> line1\n> line2\n> line3')

    def test_prologue_body_epilogue(self):
        """Template with all three sections."""
        fmt = Formatter('{line*}\n| {message}\n{line*}', map={'line*': '-'}, width=20)
        result = fmt('hello')
        self.assertEqual(result, """
--------------------
| hello
--------------------
""".strip())

    def test_no_message_raises_on_nonempty(self):
        """Template without {message} raises on non-empty message."""
        fmt = Formatter('{line*}', map={'line*': '='}, width=20)
        with self.assertRaises(ValueError):
            fmt('oops')

    def test_empty_message_no_body(self):
        """Template without {message} works with empty message."""
        fmt = Formatter('{line*}', map={'line*': '='}, width=20)
        self.assertEqual(fmt(), '=' * 20)

    def test_message_type_error(self):
        """Non-str message raises TypeError."""
        fmt = Formatter('{message}')
        with self.assertRaises(TypeError):
            fmt(42)

    def test_format_map(self):
        """format_map overrides map."""
        fmt = Formatter('{greeting}, {name}!', greeting='hello', name='world')
        self.assertEqual(fmt.format_map('', {'name': 'Larry'}), 'hello, Larry!')

    def test_format_map_non_dict_raises(self):
        """format_map raises TypeError for non-dict map."""
        fmt = Formatter('{message}')
        with self.assertRaises(TypeError):
            fmt.format_map('hello', 'not a dict')

    def test_message_in_format_map_raises(self):
        """Passing 'message' as a key in format_map raises ValueError."""
        f = Formatter('X {message} X')
        with self.assertRaises(ValueError):
            f.format_map("hello!", {"message": "oopsie"})

    def test_format_kwargs_override(self):
        """format kwargs override map."""
        fmt = Formatter('{greeting}, {name}!', greeting='hello', name='world')
        self.assertEqual(fmt.format('', name='Larry'), 'hello, Larry!')

    def test_call_is_format(self):
        """__call__ is alias for format."""
        fmt = Formatter('{message}!')
        self.assertEqual(fmt('hi'), fmt.format('hi'))

    def test_repr(self):
        """repr is eval-roundtrippable."""
        fmt = Formatter('{line*}', {'line*': '='}, width=40)
        self.assertEqual(repr(fmt), "Formatter('{line*}', {'line*': '='}, width=40)")

    def test_properties(self):
        """Properties return correct values."""
        fmt = Formatter('{line*}', {'line*': '='}, width=40)
        self.assertEqual(fmt.template, '{line*}')
        self.assertEqual(fmt.width, 40)
        self.assertEqual(fmt.map, {'line*': '='})
        # map returns a copy
        fmt.map['line*'] = 'X'
        self.assertEqual(fmt.map, {'line*': '='})

    def test_wider_than_width(self):
        """Line already wider than width: starred interpolations become empty."""
        fmt = Formatter('{d*}XXXXXXXXXXXXXXXXXXXX{d*}', map={'d*': '-'}, width=10)
        self.assertEqual(fmt(), 'XXXXXXXXXXXXXXXXXXXX')

    def test_exact_width(self):
        """Line exactly at width: starred interpolations become empty."""
        fmt = Formatter('{d*}12345{d*}', map={'d*': '-'}, width=5)
        self.assertEqual(fmt(), '12345')

    def test_multi_char_fill(self):
        """Fill value longer than 1 char."""
        fmt = Formatter('{d*}', map={'d*': '-='}, width=20)
        self.assertEqual(fmt(), '-=-=-=-=-=-=-=-=-=-=')

    def test_escaped_braces(self):
        """Escaped braces don't trigger message detection."""
        fmt = Formatter('{{message}}')
        self.assertEqual(fmt(), '{message}')

    def test_message_with_format_spec(self):
        """Message with format spec is still detected."""
        fmt = Formatter('{message:>20}')
        self.assertEqual(fmt('hi'), '                  hi')

    def test_message_with_conversion(self):
        """Message with conversion is still detected."""
        fmt = Formatter('{message!s}')
        self.assertEqual(fmt('hi'), 'hi')

    def test_message_with_conversion_and_format_spec(self):
        """Message with conversion and format spec is still detected."""
        fmt = Formatter('{message!s:>20}')
        self.assertEqual(fmt('hi'), '                  hi')

    def test_star_with_format_spec_raises(self):
        """Starred interpolation with format spec raises."""
        with self.assertRaises(ValueError):
            Formatter('{line*:>20}', map={'line*': '='})

    def test_star_with_conversion_raises(self):
        """Starred interpolation with conversion raises."""
        with self.assertRaises(ValueError):
            Formatter('{line*!r}', map={'line*': '='})

    def test_undefined_star_key_raises(self):
        """Starred interpolation referencing undefined key raises."""
        with self.assertRaises(ValueError):
            Formatter('{line*}')

    def test_noncontiguous_message_raises(self):
        """Non-contiguous message lines raise."""
        with self.assertRaises(ValueError):
            Formatter('{message}\nbreak\n{message}')

    def test_map_constructor(self):
        """Constructor map parameter works, allowing reserved kwarg names."""
        fmt = Formatter('{width}', map={'width': 'the word width'}, width=40)
        self.assertEqual(fmt(), 'the word width')
        self.assertEqual(fmt.width, 40)

    def test_map_with_kwargs_override(self):
        """Constructor kwargs override map."""
        fmt = Formatter('{a} {b}', map={'a': '1', 'b': '2'}, a='X')
        self.assertEqual(fmt(), 'X 2')

    def test_nested_braces_raises(self):
        """Nested braces raise ValueError."""
        with self.assertRaises(ValueError):
            Formatter('{ {foo*}bar*}', map={'foo*': '-', 'bar*': '='})

    def test_bare_star_outside_braces(self):
        """'foo *' outside braces is not treated as a starred interpolation."""
        fmt = Formatter('foo *{bar*}', map={'bar*': '-'}, width=20)
        self.assertEqual(fmt(), 'foo *---------------')

    def test_no_trailing_newline(self):
        """Single-line template produces no trailing newline."""
        fmt = Formatter('hello {name}', name='world')
        self.assertEqual(fmt(), 'hello world')

    def test_preserves_newlines(self):
        """Newlines in template are exactly preserved."""
        fmt = Formatter('a\nb\nc')
        self.assertEqual(fmt(), 'a\nb\nc')

    def test_no_rstrip(self):
        """Trailing whitespace in template is preserved."""
        fmt = Formatter('hello   ')
        self.assertEqual(fmt(), 'hello   ')

    def test_multiple_different_star_keys_same_line(self):
        """Different starred interpolations on the same line."""
        fmt = Formatter('{line*}@{double*}@{line*}',
            map={'line*': '-', 'double*': '='}, width=18)
        self.assertEqual(fmt(), '-----@=====@------')

    def test_multiple_same_star_key_last_unique(self):
        """Multiple starred interpolations, last key is different."""
        fmt = Formatter('{d*}{double*}{d*}', map={'d*': '-', 'double*': '='}, width=20)
        self.assertEqual(fmt(), '------=======-------')

    def test_multiple_same_star_key_last_not_unique(self):
        """Two of the same starred interpolation."""
        fmt = Formatter('{d*}X{d*}', map={'d*': '-'}, width=11)
        self.assertEqual(fmt(), '-----X-----')

    def test_single_star_key(self):
        """Single starred interpolation on a line."""
        fmt = Formatter('hello {line*}', map={'line*': '.'}, width=20)
        self.assertEqual(fmt(), 'hello ..............')

    def test_pretty_mixed_star_keys(self):
        """Pretty format with mixed starred interpolations on different lines."""
        pretty = Formatter(
            "{line*}@{line*}\n{message}\n{line*}@{double*}@{line*}",
            {'line*': '-', 'double*': '='}, width=18)
        self.assertEqual(pretty("hello there!"), """
--------@---------
hello there!
-----@=====@------
""".strip())

    def test_box_format(self):
        """Simulates Log's box format."""
        fmt = Formatter(
            '{prefix}+{line*}\n{prefix}| {message}\n{prefix}+{line*}',
            map={'line*': '-'}, prefix='[pfx] ',
            width=40)
        result = fmt('test message')
        self.assertEqual(result, """
[pfx] +---------------------------------
[pfx] | test message
[pfx] +---------------------------------
""".strip())

    def test_start_format(self):
        """Simulates Log's start format."""
        fmt = Formatter(
            '{line*}\n{name} start at {timestamp}\n{line*}',
            map={'line*': '='}, name='Log', timestamp='2026/01/01')
        result = fmt()
        self.assertEqual(result, """
===============================================================================
Log start at 2026/01/01
===============================================================================
""".strip())

    def test_docstring_example(self):
        """The example from the class docstring produces correct output."""
        fmt = Formatter('{line*}\n{name} start\n{double*}{line*}',
            {'line*': '-', 'double*': '=', 'name': 'Log'},
            width=20)
        result = fmt()
        self.assertEqual(result, """
--------------------
Log start
==========----------
""".strip())

    def test_non_str_map_value(self):
        f = Formatter('hello {key} {message}', map={'key': 42})
        self.assertEqual(f('bartholomew'), 'hello 42 bartholomew')

    def test_non_str_kwarg_value(self):
        f = Formatter('hello {message} {key}', key=36)
        self.assertEqual(f('ratfink'), 'hello ratfink 36')

    def test_non_str_starred_interpolation_map_in_constructor(self):
        """Non-str keyword argument value raises TypeError."""
        f = Formatter('hello {message} {line*}', map={'line*': 45}, width=20)
        self.assertEqual(f('bessie'), 'hello bessie 4545454')

    def test_non_str_starred_interpolation_in_format_map(self):
        """Non-str keyword argument value raises TypeError."""
        f = Formatter('hello {message} {cow*}', map={'cow*': 45}, width=20)
        self.assertEqual(f.format_map('myrtle', {'cow*': 86}), 'hello myrtle 8686868')

    def test_non_str_template_raises(self):
        """Non-str template raises TypeError."""
        with self.assertRaises(TypeError):
            Formatter(42)

    def test_non_int_width_raises(self):
        """Non-int width raises TypeError."""
        with self.assertRaises(TypeError):
            Formatter('hello', width='big')

    def test_non_dict_map_raises(self):
        """Non-dict map raises TypeError."""
        with self.assertRaises(TypeError):
            Formatter('hello', map='not a dict')

    def test_non_str_map_key_raises(self):
        """Non-str key in map raises TypeError."""
        with self.assertRaises(TypeError):
            Formatter('hello', map={42: 'value'})

    def test_message_in_map_raises(self):
        """Non-str key in map raises TypeError."""
        with self.assertRaises(ValueError):
            Formatter('hello', map={'message': 'value'})

    def test_bare_star_interpolation_raises(self):
        """Starred interpolation with no name ({*}) raises."""
        with self.assertRaises(ValueError):
            Formatter('{*}', map={'*': '-'})

    def test_unrelated_map_key_doesnt_interfere(self):
        """A map key like 'last d*' doesn't interfere with starred interpolation."""
        fmt = Formatter('{d*}X{d*}',
            map={'d*': '-', 'last d*': 'unused'}, width=20)
        self.assertEqual(fmt(), '---------X----------')

    def test_body_more_lines_than_message(self):
        """Body has more template lines than message lines: zip truncates."""
        fmt = Formatter('A {message}\nB {message}\nC {message}')
        result = fmt('only one')
        self.assertEqual(result, 'A only one')

    def test_star_in_middle_of_key_not_starred(self):
        """Key like 'a * b' is not a starred interpolation."""
        fmt = Formatter('hello {a * b}', map={'a * b': 'world'})
        self.assertEqual(fmt(), 'hello world')

    def test_message_with_trailing_space_not_detected(self):
        """{message } is not the same as {message}."""
        fmt = Formatter('{message }', map={'message ': 'literal'})
        # no body lines, so empty message is fine
        self.assertEqual(fmt(), 'literal')
        # but non-empty message should raise since there are no body lines
        with self.assertRaises(ValueError):
            fmt('oops')

    def test_even_remainder_distribution_across_widths(self):
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
            with self.subTest(width=width, expected=expected):
                fmt = Formatter('a{line*}b{line*}c{line*}d{line*}e',
                    map={'line*': '-'}, width=width)
                self.assertEqual(fmt(), expected)

    def test_many_starred_interpolations_balanced(self):
        """15 starred interpolations distribute remainder evenly."""
        fmt = Formatter(
            '{line*}{line*}{line*}{line*}{line*}{line*}{line*}our{line*}heading{line*}{line*}{line*}{line*}{line*}{line*}{line*}',
            map={'line*': '-'}, width=84)
        self.assertEqual(fmt(),
            '----------------------------------our-----heading-----------------------------------')

    def test_starred_interpolation_override_at_call_time(self):
        """Overriding a starred interpolation value at call time changes the fill."""
        fmt = Formatter('{line*} hello {line*}', map={'line*': '-'}, width=20)
        self.assertEqual(fmt(), '------ hello -------')
        self.assertEqual(fmt.format_map('', {'line*': '='}), '====== hello =======')

    def test_zero_remainder(self):
        """When delta divides evenly, all expansions get equal portion."""
        # 4 expansions, width = 5 + 8 = 13, delta = 8, portion = 2, remainder = 0
        fmt = Formatter('a{d*}b{d*}c{d*}d{d*}e', map={'d*': '-'}, width=13)
        self.assertEqual(fmt(), 'a--b--c--d--e')

    def test_delta_less_than_count(self):
        """When delta < count, Bresenham spreads the extra evenly."""
        # 4 expansions, width = 5 + 2 = 7, delta = 2, Bresenham distributes evenly
        fmt = Formatter('a{d*}b{d*}c{d*}d{d*}e', map={'d*': '-'}, width=7)
        self.assertEqual(fmt(), 'ab-cd-e')

    def test_different_star_keys_remainder_distribution(self):
        """Different star keys still get even remainder distribution."""
        fmt = Formatter('{a*}{b*}{a*}{b*}{a*}', map={'a*': '-', 'b*': '='}, width=12)
        self.assertEqual(fmt(), '--==---==---')

    def test_supported(self):
        """supported returns frozenset of all interpolation keys."""
        fmt = Formatter('{line*}\n{prefix}{message:>20}\n{line*}',
            map={'line*': '-'}, prefix='>> ')
        self.assertEqual(fmt.supported, frozenset({'line*', 'prefix', 'message'}))

    def test_supported_empty_template(self):
        """Empty template has empty supported set."""
        fmt = Formatter('')
        self.assertEqual(fmt.supported, frozenset())

    def test_supported_no_message(self):
        """Template without {message} doesn't include 'message' in supported."""
        fmt = Formatter('{greeting}, {name}!', greeting='hello', name='world')
        self.assertEqual(fmt.supported, frozenset({'greeting', 'name'}))

    def test_supported_is_frozenset(self):
        """supported returns a frozenset."""
        fmt = Formatter('{message}')
        self.assertIsInstance(fmt.supported, frozenset)

    def test_empty_interpolation_raises(self):
        """Empty interpolation {} raises."""
        with self.assertRaises(ValueError):
            Formatter('{}')

    def test_positional_argument_raises(self):
        """Positional argument {0} raises."""
        with self.assertRaises(ValueError):
            Formatter('{0}')

    def test_empty_template_lines_preserved(self):
        """Empty lines in the template are preserved."""
        fmt = Formatter('hello\n\nworld')
        self.assertEqual(fmt(), 'hello\n\nworld')

    def test_prefix_character_is_hash_by_default(self):
        """When no interpolation starts with #, the prefix character is #."""
        fmt = Formatter('{line*} {name}', map={'line*': '-'}, name='hello', width=20)
        prefix_char = fmt._prologue[0][1][0][0][0]
        self.assertEqual(prefix_char, '#')

    def test_prefix_character_skips_collision(self):
        """When a key starts with #, prefix advances to $."""
        fmt = Formatter('{#1} {line*}', map={'#1': 'hello', 'line*': '-'}, width=20)
        self.assertEqual(fmt(), 'hello --------------')
        prefix_char = fmt._prologue[0][1][0][0][0]
        self.assertEqual(prefix_char, '$')

    def test_prefix_character_probes_to_question_mark(self):
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
        self.assertEqual(fmt(), 'a--------------bcdefghijklmnopqrstuvwxyz')
        prefix_char = fmt._prologue[0][1][0][0][0]
        self.assertEqual(prefix_char, '?')

    def test_dotted_expression_detected_as_message(self):
        """{message.foo} is still detected as a {message} interpolation."""
        fmt = Formatter('{message.upper}')
        self.assertIn('message', fmt.supported)
        self.assertTrue(bool(fmt._body))

    def test_indexed_expression_detected_as_message(self):
        """{message[0]} is still detected as a {message} interpolation."""
        fmt = Formatter('{message[0]}')
        self.assertIn('message', fmt.supported)
        self.assertTrue(bool(fmt._body))

    def test_dotted_and_indexed_expression(self):
        """{message.foo[0]} is still detected as a {message} interpolation."""
        fmt = Formatter('{message.foo[0]}')
        self.assertIn('message', fmt.supported)
        self.assertTrue(bool(fmt._body))

    def test_starred_with_dot_raises(self):
        """Starred interpolation with dot raises."""
        with self.assertRaises(ValueError):
            Formatter('{line*.foo}', map={'line*': '-'})

    def test_starred_with_bracket_raises(self):
        """Starred interpolation with bracket raises."""
        with self.assertRaises(ValueError):
            Formatter('{line*[0]}', map={'line*': '-'})

    def test_supported_with_dotted_key(self):
        """Dotted expression has the base key in supported, not the full expression."""
        fmt = Formatter('{foo.bar} {baz[0]}', foo='x', baz='y')
        self.assertEqual(fmt.supported, frozenset({'foo', 'baz'}))


def run_tests():
    bigtestlib.run(name="big.template", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
