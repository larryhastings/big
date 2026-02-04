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

import builtins
from .types import string
from .text import split_quoted_strings
import token

# TODO
# test all unclosed open delimiters
# close delimiter inside a quoted string?
# if no quotes defined, don't use split quoted strings


from . import builtin
mm = builtin.ModuleManager()
export = mm.export


_TOKEN_OP = token.OP

_delimiter_map = {
    '{': '}',
    '(': ')',
    '[': ']',
    }

@export
class Interpolation:
    """
    Represents a {{ }} expression interpolation
    in a parsed template.  See big.parse_template_string.

    The expression attribute contains the text of the
    expression.  The filters attribute is a list, containing
    the text of all filter expressions (if any).  If the
    expression ended with '=', the debug attribute will contain
    the text of the expression along with the '=' and all
    whitespace, otherwise it will be an empty string.
    """
    def __init__(self, expression, *filters, debug=''):
        self.expression = expression
        self.filters = filters
        self.debug = debug

    def __repr__(self):
        l = [repr(self.expression)]
        l.extend(repr(f) for f in self.filters)
        s = ', '.join(l)
        return f'Interpolation({s}, debug={self.debug!r})'

    def __eq__(self, other):
        return (
            isinstance(other, Interpolation)
            and (self.expression == other.expression)
            and (self.filters == other.filters)
            and (self.debug == other.debug)
            )

@export
class Statement:
    """
    Represents a {% %} statement interpolation
    in a parsed template.  See big.parse_template_string.

    The statement attribute contains the text of the
    statement, including all leading and trailing
    whitespace.
    """

    def __init__(self, statement):
        self.statement = statement

    def __repr__(self):
        return f'Statement({self.statement!r})'

    def __eq__(self, other):
        return (
            isinstance(other, Statement)
            and (self.statement == other.statement)
            )


def parse_template_string(s, parse_expressions, parse_comments, parse_statements, parse_whitespace_eater, quotes, multiline_quotes, escape):
    "internal iterator for public big.parse_template_string"
    if not s:
        yield s

    original_s = s
    length = len(original_s)

    stack = []
    stack_push = stack.append
    stack_pop = stack.pop

    text = []
    text_append = text.append
    text_clear = text.clear
    empty_join = "".join

    expression = []
    expression_append = expression.append
    expression_clear = expression.clear
    debug = None

    statement = []
    statement_append = statement.append
    statement_clear = statement.clear

    split_statement = bool(quotes) or bool(multiline_quotes)

    while s:
        before, delimiter, after = s.partition('{')
        # print(f">> {before=} {delimiter=} {after=} {text=}")
        if before:
            text_append(before)

        if not delimiter:
            break

        if not after:
            text_append(delimiter)
            break

        after0 = after[0]
        after = after[1:]

        if parse_comments and (after0 == '#'):
            # comment
            comment, delimiter, s2 = after.partition('#}')
            if not delimiter:
                raise SyntaxError(f"{delimiter.where}: unterminated comment")
            s = s2
            continue

        if parse_whitespace_eater and (after0 == '>') and (after.startswith('}')):
            s = after[1:].lstrip()
            continue

        is_statement = parse_statements and (after0 == '%')
        is_expression = parse_expressions and (after0 == '{')

        if not (is_statement or is_expression):
            if delimiter:
                text_append(delimiter)
                text_append(after0)
            s = after
            continue

        # flush text
        if text:
            length = len(text)
            if length == 1:
                yield text[0]
            else:
                yield empty_join(text)
            text_clear()

        if is_statement:
            where = delimiter
            if after:
                if split_statement:
                    iterator = split_quoted_strings(after, quotes=quotes, multiline_quotes=multiline_quotes, escape=escape)
                else:
                    iterator = (('', after, ''),)
                for opening_quote, t, closing_quote in iterator:
                    # print(f">> {opening_quote=} {t=} {closing_quote=}")
                    if opening_quote:
                        if not closing_quote:
                            # this is going to be the last thing yielded,
                            # and we don't have a close quote.  nerts!
                            raise SyntaxError(f'unterminated quoted string at {opening_quote.where}')
                        statement_append(opening_quote)
                        if t:
                            statement_append(t)
                        statement_append(closing_quote)
                        continue

                    # opening_quote is false, ergo so is closing quote, we only care about t
                    before, delimiter, after = t.partition('%}')
                    if before:
                        statement_append(before)
                    if delimiter:
                        break
                else:
                    raise SyntaxError(f'unterminated statement at {where.where}')
            s = after
            st = empty_join(statement)
            statement_clear()
            yield Statement(st)
            continue

        # it's an expression
        assert is_expression
        stack = []
        # Top Of Stack
        tos = previous_was_rcurly = None
        start_offset = after.offset

        for t in after.generate_tokens():
            if t.type != _TOKEN_OP:
                continue
            t_string = t.string
            offset = t_string.offset
            is_rcurly = t_string == '}'
            if is_rcurly:
                if previous_was_rcurly:
                    s = original_s[offset + 1:]
                    offset -= 1
                    break
            else:
                previous_was_rcurly = None

            right = _delimiter_map.get(t_string)
            if right:
                if tos:
                    stack_push(tos)
                tos = right
                continue
            if tos:
                if t_string == tos:
                    tos = stack_pop() if stack else None
                continue
            if t_string == '|':
                x = original_s[start_offset:offset]
                if not x.strip():
                    noun = 'filter' if expression else 'expression'
                    raise SyntaxError(f'empty {noun} at {x.where}')
                expression_append(x)
                start_offset = offset + 1
                continue
            previous_was_rcurly = is_rcurly
        else:
            noun = 'filter' if expression else 'expression'
            raise SyntaxError(f'unterminated {noun} at {after.where}')
        expression_append(original_s[start_offset:offset])

        # handle trailing =
        x = expression[0]
        before, equals, after = x.partition('=')
        if equals and (not after.rstrip()):
            debug = x
            expression[0] = before
        else:
            l = len(x)
            debug = x[l:l]
        stripped = [x.strip() for x in expression]
        yield Interpolation(*stripped, debug=debug)
        expression_clear()
        debug = None

    # flush text
    if text:
        length = len(text)
        if length == 1:
            yield text[0]
        else:
            yield empty_join(text)

_parse_template_string = parse_template_string


@export
def parse_template_string(s, *,
    parse_expressions=True,
    parse_comments=False,
    parse_statements=False,
    parse_whitespace_eater=False,
    quotes=('"', "'"),
    multiline_quotes=(),
    escape='\\',
    ):
    """
    Parses a string containing simple markup, yielding its components.

    The markup is patterened after Django Templates and Jinja.
    parse_template_string supports the following delimiters:
        * {{ ... }} represents an "expression", a Python expression.
          A template library generally calls eval() on this string
          and replaces the text of the expression with the resulting
          value.
            * The expression can also specify "filters".
        * {% ... %} represents a "statement", a Python (or other)
          statement.  A template library generally parses the text
          of the statement and performs the action specified, like
          "iterate over this for loop" or "apply html.escape to all
          expressions after this statement".
            * When parsing statements, parse_template_string can
              optionally preserve quoted strings.  You may specify
              quote delimiters, multi-line quote delimiters, and
              the escape character.  Quoted strings only have two
              effects on parsing:
                * The close delimiter ( %} ) is ignored when
                    present in a quoted string.
                * Quote marks must be balanced; every quoted string
                  must be closed before the end of the statement.
        * {# #} represents a "comment".  The delimiters and all text
          between them is discarded.
        * {>} is the "whitespace eater".  Those three characters, and
          all subsequent whitespace, are discarded, stopping when reaching
          either a non-whitespace character or the end of the string.

    Each of these delimiters can be individually enabled or disabled
    with boolean keyword-only parameters, e.g. "parse_expression",
    "parse_whitespace_eater".  By default only parse_expression is true.

    Returns a generator yielding the components of s.  These components
    can be:
        * a str object, representing literal text in the template,
        * an Expression object, representing a parsed expression, or
        * a Statement object, representing a parsed statement.
    """
    if not isinstance(s, str):
        raise TypeError('s must be a str')

    if not isinstance(s, string):
        s = string(s)

    return _parse_template_string(s, parse_expressions, parse_comments, parse_statements, parse_whitespace_eater, quotes, multiline_quotes, escape)


@export
def eval_template_string(s, globals, locals=None, *,
    parse_expressions=True,
    parse_comments=False,
    parse_whitespace_eater=False,
    ):
    """
    Reformats a string, replacing {{}}-delimited Python expressions with their values.

    s should be a string.  It's parsed using big's
    parse_template_string function, then evaluates the
    Interpolation objects using eval(text, globals).
    This means eval_template_string supports {{ ... }}
    to specify expressions, including supporting filters.
    Optionally you may also enable parsing "comments" and
    the "whitespace eater"; parsing these are disabled by
    default.

    globals and locals (if specified) should be dictionaries
    containing the namespace in which the expressions will
    be evaluated.

    Uses Python's built-in function eval() to evaluate the
    expressions, which means the expressions are full Python
    expressions. Note that eval() has special support for
    builtins; see the documentation for eval() for more information.

    Returns s with all interpolations evaluated and replaced.
    """
    result = []
    append = result.append

    for o in parse_template_string(s,
        parse_expressions=parse_expressions,
        parse_comments=parse_comments,
        parse_statements=False,
        parse_whitespace_eater=parse_whitespace_eater,
        ):
        if isinstance(o, str):
            append(o)
            continue

        if o.debug:
            append(o.debug)

        # interpolation
        value = eval(o.expression, globals, locals)
        for f in o.filters:
            filter = eval(f, globals, locals)
            value = filter(value)
        append(str(value))

    return ''.join(result)


mm()
