import builtins
from .types import string
import token


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


def parse_template_string(s):
    if not s:
        yield s

    original_s = s
    length = len(original_s)

    stack = []
    expression = []
    debug = None
    yielded_str = True

    while s:
        before, delimiter, after = s.partition('{{')
        yield before
        yielded_str = True

        if not delimiter:
            return

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
                    stack.append(tos)
                tos = right
                continue
            if tos:
                if t_string == tos:
                    tos = stack.pop() if stack else None
                continue
            if t_string == '|':
                x = original_s[start_offset:offset]
                if not x.strip():
                    noun = 'filter' if expression else 'expression'
                    raise SyntaxError(f'empty {noun} at {x.where}')
                expression.append(x)
                start_offset = offset + 1
                continue
            previous_was_rcurly = is_rcurly
        else:
            noun = 'filter' if expression else 'expression'
            raise SyntaxError(f'unterminated {noun} at {after.where}')
        expression.append(original_s[start_offset:offset])

        # handle trailing =
        x = expression[0]
        before, equals, after = x.partition('=')
        if equals and (not after.rstrip()):
            debug = x
            expression[0] = before
        else:
            l = len(x)
            debug = x[l:l]
        expression = [x.strip() for x in expression]
        yield Interpolation(*expression, debug=debug)
        expression = []
        debug = None
        yielded_str = False

    if not yielded_str:
        yield original_s[length:length]

_parse_template_string = parse_template_string


@export
def parse_template_string(s):
    """
    Parses a string containing templates, yields its components.

    Returns a generator that yields the components of s.
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

    return _parse_template_string(s)


@export
def eval_template_string(s, globals):
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

    for o in parse_template_string(s):
        if isinstance(o, str):
            append(o)
            continue

        # interpolation
        value = eval(o.expression, globals)
        for f in o.filters:
            filter = eval(f, globals)
            value = filter(value)
        if o.debug:
            append(o.debug)
        if not isinstance(value, str):
            value = str(value)
        append(value)

    return ''.join(result)


del export
