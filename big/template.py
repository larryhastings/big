import builtins
from .types import string
from .text import split_quoted_strings
import token

# TODO
# test all unclosed open delimiters
# close delimiter inside a quoted string?
# if no quotes defined, don't use split quoted strings

__all__ = []

def export(o):
    __all__.append(o.__name__)
    return o



_TOKEN_OP = token.OP

_delimiter_map = {
    '{': '}',
    '(': ')',
    '[': ']',
    }

@export
class Interpolation:
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

    Returns a generator yielding the components of s.
    parse_template_string always yields an odd number of
    items, alternating between str objects and Interpolation
    objects.  The first and last items yielded are always str
    objects.

    If an interpolation ends with a single '=' (optionally
    followed by whitespace), the 'debug' attribute of that
    Interpolation will contain the full text of the expression,
    including the equals sign, and the expression will contain
    the expression with the equals sign stripped.
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
    Reformats a string, replacing {{}}-delimited expressions with their values.

    s should be a string.  It's parsed using big's
    parse_template_string function, then evaluates the
    Interpolation objects using eval(text, globals).

    globals should be a dictionary containing the namespace
    in which the expressions will be evaluated.

    Note that eval() has special support for builtins;
    see the documentation for eval for more information.

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

        # interpolation
        value = eval(o.expression, globals, locals)
        for f in o.filters:
            filter = eval(f, globals, locals)
            value = filter(value)
        if o.debug:
            append(o.debug)
        if not isinstance(value, str):
            value = str(value)
        append(value)

    return ''.join(result)


del export
