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
from big.all import Interpolation, parse_template_string, eval_template_string
import unittest


class BigTestTemplate(unittest.TestCase):

    maxDiff=None

    def test_parse_template_string(self):
        def t(s, expected):
            got = list(parse_template_string(s))
            self.assertEqual(expected, got)

        t('hello there 1 2 3', ['hello there 1 2 3'])
        t('{{x}}', ['', Interpolation('x', debug=''), ''])
        t('{{x = }}', ['', Interpolation('x', debug='x = '), ''])
        t('try a filter {{a|times3}} and another {{foo(3 | 5, "bar") = | filter1 | filters[2]}} it worked?!',
            [
            'try a filter ',
            Interpolation('a', 'times3', debug=''),
            ' and another ',
            Interpolation('foo(3 | 5, "bar")', 'filter1', 'filters[2]', debug='foo(3 | 5, "bar") = '),
            ' it worked?!',
            ])

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

        def t(s, expected):
            got = eval_template_string(s, globals)
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

        t('{{len("abcde") = }}', 'len("abcde") = 5')

        my_builtins = {'len': lambda o: 88}
        globals['__builtins__'] = my_builtins
        t('{{len("abcde") = }}', 'len("abcde") = 88')

        my_builtins.clear()
        with self.assertRaises(NameError):
            t('{{len("abcde") = }}', '')



def run_tests():
    bigtestlib.run(name="big.template", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
