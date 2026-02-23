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
import itertools
import token

from .types import string
from .text import split_quoted_strings, split_delimiters, Delimiter

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
    Represents a {{ }} expression interpolation from a parsed template.

    The expression attribute contains the text of the
    expression.  The filters attribute is a list, containing
    the text of each filter expression (if any).  If the
    expression ended with '=', the debug attribute will contain
    the text of the expression along with the '=' and all
    whitespace, otherwise it will be an empty string.

    See big.template.parse_template_string.
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
    Represents a {% %} statement interpolation from a parsed template.

    The statement attribute contains the text of the
    statement, including all leading and trailing
    whitespace.

    See big.template.parse_template_string.
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

    The markup is patterned after Django Templates and Jinja.
    parse_template_string supports the following delimiters:
        * {{ ... }} represents an "expression", a Python expression.
          A template library generally calls eval() on this string
          and replaces the text of the expression with the resulting
          value.  The expression can also specify "filters".
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


_curly_brace_delimiters = {'{': Delimiter('}')}


@export
class Formatter:
    """
    A sophisticated template formatter, similar to str.format.

    Example:

        fmt = Formatter('{line*}\\n{name} start\\n{double*}{line*}',
            {'line*': '-', 'double*': '=', 'name': 'Log'},
            width=20)
        print(fmt())

    This prints:

        --------------------
        Log start
        ==========----------

    The template string is split on newlines into template lines.
    Template lines are classified into three groups:

        prologue: lines before any {message} line
        body: contiguous lines containing {message}
        epilogue: lines after the last {message} line

    When the message is formatted, the lines of the message are
    zipped together with the "body".  If the message has more lines
    than body template lines, Formatter repeats the last body
    template line.

    Substitution values in the template use str.format_map syntax.
    Values whose keys end with * (e.g. "{line*}") are "starred
    interpolations": their value is repeated to fill the line to
    the target width.  Starred interpolations must not use a
    conversion or format spec.
    """

    def __init__(self, template, map=None, *, width=79, **kwargs):
        if not isinstance(template, str):
            raise TypeError(f"template must be str, not {type(template).__name__}")
        if not isinstance(width, int):
            raise TypeError(f"width must be int, not {type(width).__name__}")

        if map is not None:
            if not isinstance(map, dict):
                raise TypeError(f"map must be dict or None, not {type(map).__name__}")
            if "message" in map:
                raise ValueError(f"map must not contain 'message'")

            for k, v in map.items():
                if not isinstance(k, str):
                    raise TypeError(f"map keys must be str, not {type(k).__name__}")
            map = dict(map)
            map.update(kwargs)
        else:
            map = dict(kwargs)

        # pre str-ize all starred interpolation values
        for key, value in map.items():
            if key.endswith('*'):
                map[key] = str(value)

        self._template = template
        self._width = width
        self._map = map

        prologue = []
        body = []
        epilogue = []
        state = prologue

        for template_line in template.split('\n'):
            cleaned = template_line.replace('{{', '').replace('}}', '')

            contains_message = in_interpolation = False
            starred_interpolations = []

            for text, open, close, change in split_delimiters(cleaned, _curly_brace_delimiters, yields=4):
                if open and in_interpolation:
                    raise ValueError("template does not support nested curly braces")
                if close:
                    # strip conversion and format spec first
                    bare, _, _ = text.partition('!')
                    bare, _, _ = bare.partition(':')
                    if bare.endswith('*'):
                        # it's a starred interpolation
                        if bare != text:
                            raise ValueError(f"starred interpolation {{{text}}} must not use a conversion or format spec")
                        if bare == '*':
                            raise ValueError(f"starred interpolation {{{text}}} must have a name")
                        if text not in map:
                            raise ValueError(f"template uses {{{text}}} but {text!r} is not defined in map")
                        starred_interpolations.append(text)
                    else:
                        if bare == 'message':
                            contains_message = True
                in_interpolation = bool(open)

            if state is prologue:
                if contains_message:
                    state = body
            elif state is body:
                if not contains_message:
                    state = epilogue
            else:
                assert state is epilogue
                if contains_message:
                    raise ValueError("all {message} lines in template must be contiguous")

            if not starred_interpolations:
                if template_line:
                    state.append((template_line, 0, (), None, None))
                continue

            original_last_key = starred_interpolations[-1]
            count = len(starred_interpolations)

            # Generate a unique key for the last starred interpolation
            # on each line, so it can expand to share + remainder characters
            # while all other occurrences expand to share characters.
            # Maybe a little silly, but: try "last line*",
            # then "last line* 2", "last line* 3", etc.
            all_keys = set(starred_interpolations) | set(map)
            last_key = "last " + original_last_key
            if last_key in all_keys:
                n = 2
                base = last_key
                while last_key in all_keys:
                    last_key = f"{base} {n}"
                    n += 1

            starred_interpolations[-1] = last_key

            before, sep, after = template_line.rpartition(f'{{{original_last_key}}}')
            assert sep
            template_line = f'{before}{{{last_key}}}{after}'

            # unique_keys: deduplicated list preserving order, last_key always last
            seen = set()
            unique_keys = []
            for key in starred_interpolations:
                if key not in seen:
                    seen.add(key)
                    unique_keys.append(key)

            test_starred_interpolations_map = dict.fromkeys(starred_interpolations, '')

            state.append((template_line, count, unique_keys, original_last_key, test_starred_interpolations_map))

        self._prologue = prologue
        self._body = body
        self._epilogue = epilogue

    @property
    def template(self):
        """The original template string."""
        return self._template

    @property
    def width(self):
        """The target line width for starred interpolations."""
        return self._width

    @property
    def map(self):
        """A copy of the substitution dict."""
        return dict(self._map)

    def __repr__(self):
        return f"Formatter({self._template!r}, {self._map!r}, width={self._width!r})"

    def __call__(self, message='', **kwargs):
        """Alias for format."""
        return self.format_map(message, kwargs)

    def format(self, message='', **kwargs):
        """
        Format the template with the given message and kwargs.

        message must be str.
        kwargs override the map for this call only.
        Raises TypeError if message is not str.
        Raises ValueError if message is non-empty but the
        template has no {message} lines.
        Returns the formatted string.
        """
        return self.format_map(message, kwargs)

    def format_map(self, message='', map={}):
        """
        Format the template with the given message and map.

        message must be str.
        map overrides the stored map for this call only.
        Raises TypeError if message is not str.
        Raises ValueError if message is non-empty but the
        template has no {message} lines.
        Returns the formatted string.
        """
        if not isinstance(message, str):
            raise TypeError(f"message must be str, not {type(message).__name__}")
        if message and not self._body:
            raise ValueError("message is non-empty but template has no {message} lines")

        extra = self._map
        if map:
            if "message" in map:
                raise ValueError(f"map must not contain 'message'")
            extra = dict(extra)
            for key, value in map.items():
                if key.endswith('*'):
                    value = str(value)
                extra[key] = value

        message_lines = message.split('\n')
        width = self._width

        if not self._body:
            body_iter = ()
        elif len(self._body) > len(message_lines):
            body_iter = zip(self._body, message_lines)
        else:
            body_iter = itertools.zip_longest(self._body, message_lines, fillvalue=self._body[-1])

        prologue_iter = ((entry, None) for entry in self._prologue)
        epilogue_iter = ((entry, None) for entry in self._epilogue)

        buffer = []
        append = buffer.append

        for template_entry, message_line in itertools.chain(prologue_iter, body_iter, epilogue_iter):
            template, starred_interpolations, unique_keys, original_last_key, test_starred_interpolations_map = template_entry

            line_map = dict(extra)
            if message_line is not None:
                line_map['message'] = message_line

            line = None
            if starred_interpolations:
                line_map.update(test_starred_interpolations_map)
                test_line = template.format_map(line_map)
                delta = width - len(test_line)
                if delta <= 0:
                    line = test_line
                else:
                    share, remainder = divmod(delta, starred_interpolations)

                    last_key = unique_keys[-1]
                    for key in unique_keys:
                        if key is not last_key:
                            fill_value = extra[key]
                        else:
                            share += remainder
                            fill_value = extra[original_last_key]
                        repeated = fill_value * ((share // len(fill_value)) + 1)
                        line_map[key] = repeated[:share]

            if line is None:
                line = template.format_map(line_map)
            append(line)

        return "\n".join(buffer)

mm()
