#!/usr/bin/env python3

_license = """
big
Copyright 2022-2025 Larry Hastings
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

        def t(s, expected, *, quotes=('"', "'")):

            got = list(parse_template_string(s,
                parse_expressions=True,
                parse_comments=True,
                parse_statements=True,
                parse_whitespace_eater=True,
                quotes=quotes,
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

        with self.assertRaises(SyntaxError):
            t("Unterminated expansion {{ jibber_jabber ", None)

        with self.assertRaises(SyntaxError):
            t("Unterminated expansion with filter {{ fiddle | faddle ", None)

        with self.assertRaises(SyntaxError):
            t("Unterminated statement {% bishi bashi ", None)

        with self.assertRaises(SyntaxError):
            t("Unterminated statement {% splish splash ", None, quotes=())



def run_tests():
    bigtestlib.run(name="big.template", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
