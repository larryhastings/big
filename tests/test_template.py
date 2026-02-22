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

        t('oh noes we need a quoted version {{ "{{"}} BUT WAIT WHAT ABOUT THE TOHER ONE HUH? {{ "}}" }} OH OKAY',
            'oh noes we need a quoted version {{ BUT WAIT WHAT ABOUT THE TOHER ONE HUH? }} OH OKAY')

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
            t("Unterminated comment {# argle bargle", None)
        t("Unterminated comment {# argle bargle",
            ["Unterminated comment {# argle bargle",],
            parse_comments=False)

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


class TestFormatter(unittest.TestCase):

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
        result = fmt()
        self.assertEqual(result, "====== HELLO =======")

    def test_thirds(self):
        """Three starred interpolations position at 1/3."""
        fmt = Formatter('{d*}{d*}X{d*}', map={'d*': '-'}, width=20)
        result = fmt()
        self.assertEqual(result, "------------X-------")

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
        result = fmt()
        self.assertEqual(len(result), 20)

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
        result = fmt()
        self.assertTrue(result.startswith('foo *'))
        self.assertEqual(len(result), 20)

    def test_escaped_open_brace_star(self):
        """Nested braces after escaped brace raises."""
        with self.assertRaises(ValueError):
            Formatter('{ {foo*}bar*}', map={'foo*': '-', 'bar*': '='})

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
        result = fmt()
        self.assertEqual(result, "-----@=====@------")

    def test_multiple_same_star_key_last_unique(self):
        """Multiple same starred interpolation, last gets remainder."""
        fmt = Formatter('{d*}{d*}{d*}', map={'d*': '-'}, width=20)
        result = fmt()
        self.assertEqual(len(result), 20)
        self.assertEqual(result, '-' * 20)

    def test_multiple_same_star_key_last_not_unique(self):
        """Two of the same starred interpolation."""
        fmt = Formatter('{d*}X{d*}', map={'d*': '-'}, width=11)
        result = fmt()
        self.assertEqual(len(result), 11)
        self.assertIn('X', result)

    def test_single_star_key(self):
        """Single starred interpolation on a line."""
        fmt = Formatter('hello {line*}', map={'line*': '.'}, width=20)
        result = fmt()
        self.assertEqual(len(result), 20)
        self.assertTrue(result.startswith('hello '))

    def test_pretty_mixed_star_keys(self):
        """Pretty format with mixed starred interpolations on different lines."""
        pretty = Formatter(
            "{line*}@{line*}\n{message}\n{line*}@{double*}@{line*}",
            {'line*': '-', 'double*': '='}, width=18)
        result = pretty("hello there!")
        self.assertEqual(result, """
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

    def test_non_str_map_value_raises(self):
        """Non-str value in map raises TypeError."""
        with self.assertRaises(TypeError):
            Formatter('hello', map={'key': 42})

    def test_non_str_kwarg_value_raises(self):
        """Non-str keyword argument value raises TypeError."""
        with self.assertRaises(TypeError):
            Formatter('hello', staple=3)

    def test_bare_star_interpolation_raises(self):
        """Starred interpolation with no name ({*}) raises."""
        with self.assertRaises(ValueError):
            Formatter('{*}', map={'*': '-'})

    def test_last_key_collision(self):
        """Last key collision resolution works."""
        # 'last d*' is already a key, so collision resolution kicks in
        fmt = Formatter('{d*}X{d*}',
            map={'d*': '-', 'last d*': 'unused'}, width=20)
        result = fmt()
        self.assertEqual(result, '---------X----------')

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


def run_tests():
    bigtestlib.run(name="big.template", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
