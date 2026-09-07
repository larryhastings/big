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

"""
big.stylesheet -- inline character-style markup and the StyleSheet
renderer.  The markup language ({style_delimiters!r} spans), the
*_styles codec (split/join/escape/strip), the StyleSheet class, the
stock ANSI stylesheets, and the low-level color palette all live here.
"""

from .text import multisplit as _multisplit

from . import builtin
mm = builtin.ModuleManager()
export = mm.export

# best_palette (in the ansi-stylesheets snippet below) picks a palette
# with these; imported as free names so a snippet consumer can supply them.
from .builtin import can_colorize, ansi_color_depth


style_delimiters = '⦃⦙⦄'
export('style_delimiters')

# the stock text transforms: merge into your StyleSheet and use as
# tags--'usage': ('T', '⦃heading⦙⦃upper⦙T⦄⦄')--or reference
# them from hook entries.  Pure text shaping, no paint.
from .text import gently_title as _gently_title


# --8<-- start big stylesheet transforms --8<--
# (a snippet consumer supplies _gently_title -- big.text.gently_title --
#  and an export() shim.)
def _tile(pattern, length):
    "Repeat `pattern` up to `length` characters, then clip (empty if either is empty)."
    if length <= 0 or not pattern:
        return ''
    return (pattern * (length // len(pattern) + 1))[:length]


def _fill(pattern, model):
    "Repeat `pattern` up to the length of `model`, then clip: ⦃fill⦙pattern⦙model⦄."
    return _tile(pattern, len(model))


def _clip(model, text):
    "Clip `text` to the length of `model`: ⦃clip⦙model⦙text⦄."
    return text[:len(model)]


def _center(model, *args):
    "Center `text` in a field the width of `model`, padding with `fill`: ⦃center⦙model[⦙fill]⦙text⦄."
    *fill, text = args
    pattern = fill[0] if fill else ' '
    margin = len(model) - len(text)
    if margin <= 0:
        return text
    left = margin // 2 + (margin & len(model) & 1)   # str.center's split
    return _tile(pattern, left) + text + _tile(pattern, margin - left)


def _ljust(model, *args):
    "Left-justify `text` in a field the width of `model`, padding with `fill`: ⦃ljust⦙model[⦙fill]⦙text⦄."
    *fill, text = args
    pattern = fill[0] if fill else ' '
    return text + _tile(pattern, len(model) - len(text))


def _rjust(model, *args):
    "Right-justify `text` in a field the width of `model`, padding with `fill`: ⦃rjust⦙model[⦙fill]⦙text⦄."
    *fill, text = args
    pattern = fill[0] if fill else ' '
    return _tile(pattern, len(model) - len(text)) + text


transforms = {
    'upper':  str.upper,
    'lower':  str.lower,
    'title':  _gently_title,
    'strip':  str.strip,
    'lstrip': str.lstrip,
    'rstrip': str.rstrip,
    'fill':   _fill,
    'clip':   _clip,
    'center': _center,
    'ljust':  _ljust,
    'rjust':  _rjust,
}
export('transforms')
# --8<-- end big stylesheet transforms --8<--


# --8<-- start big stylesheet render core --8<--
# (The render half of the module: the span parser, the codec's
# runtime members, _Definition, StyleSheet, plain_stylesheet.
# The authoring helpers ride along until a render-only core is
# factored.  Snippet consumers supply style_delimiters, an
# export() shim, and a _multisplit stub--split_styles needs it,
# nothing else does.)
def _validate_format(name):
    if not isinstance(name, str):
        raise TypeError(f"format must be str, not {type(name).__name__}")
    if (not name) or name[:1].isdigit() or not all(
            c.isalnum() or c == '_' for c in name):
        raise ValueError(
            f"illegal format name {name!r}: must be alphanumeric "
            f"or underscore, and must not start with a digit")


def _refuse_delimiters(s, what, delimiters=style_delimiters):
    for c in delimiters:
        if c in s:
            raise ValueError(
                f"{what} contains the delimiter character {c!r}: {s!r}")


@export
def style(name, *fields):
    """
    Returns the markup for one span: '⦃name⦙field...⦄'.
    name must be alphanumeric or underscore, and must not start
    with a digit.
    Fields must not contain delimiter characters (raises
    ValueError--noisily, never silently altered).
    """
    _validate_format(name)
    parts = [name]
    for field in fields:
        if not isinstance(field, str):
            raise TypeError(
                f"style field must be str, not {type(field).__name__}")
        # fields may CONTAIN well-formed markup (composition:
        # style('bold', style('link', ...)) must work); junk
        # delimiters refuse noisily via the parse
        _parse_markup(field, style_delimiters)
        parts.append(field)
    return f'⦃{"⦙".join(parts)}⦄'


@export
def plain(text):
    """
    Returns the markup for a boring island: text renders with NO
    paint--enclosing paint is suspended, nested paint is stripped.
    """
    if not isinstance(text, str):
        raise TypeError(f"text must be str, not {type(text).__name__}")
    _parse_markup(text, style_delimiters)
    return f'⦃_plain⦙{text}⦄'


@export
def escape_styles(text):
    """
    Quote any style delimiter characters in `text` so it can be
    dropped into markup as literal text -- each delimiter is preceded
    by the open delimiter (⦃ -> ⦃⦃, ⦙ -> ⦃⦙, ⦄ -> ⦃⦄).  Rendering
    (or plain_stylesheet) turns them back into the literal character.
    Call this on raw text before wrapping it in a span.
    """
    open_c = style_delimiters[0]
    out = []
    for ch in text:
        if ch in style_delimiters:
            out.append(open_c)
        out.append(ch)
    return ''.join(out)


class _Span:
    "A parsed markup span: a name and its fields (lists of nodes)."
    __slots__ = ('name', 'fields', 'where')
    def __init__(self, name, fields, where):
        self.name = name
        self.fields = fields
        self.where = where


def _escape_nodes(nodes, escape):
    # source text runs pass through the escape; spans recurse.
    # Definition replacements never come through here--they parse
    # at insertion and stay trusted.
    result = []
    for node in nodes:
        if isinstance(node, str):
            result.append(escape(node))
        else:
            node.fields = [_escape_nodes(f, escape)
                           for f in node.fields]
            result.append(node)
    return result


class _Hole:
    """
    A field spliced into a replacement, as an unrendered node
    tree: it renders at its FINAL position (so it's painted by
    whatever surrounds it there), under the cycle-set captured at
    the call site (a field's own spans aren't part of the
    definition-expansion chain).
    """
    __slots__ = ('nodes', 'active')
    def __init__(self, nodes, active):
        self.nodes = nodes
        self.active = active


def _parse_markup(s, delimiters):
    """
    Parse s into a list of nodes: str (literal text) or _Span.
    Iterative, so malformed input fails with a POSITION, not a
    recursion error.  Unbalanced or stray delimiters raise
    ValueError--the noisy contract.
    """
    open_c, sep_c, close_c = delimiters
    root = []
    out = root
    stack = []              # list of _Span being built
    text_start = 0
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c not in delimiters:
            i += 1
            continue
        if text_start < i:
            out.append(s[text_start:i])
        if c == open_c:
            if (i + 1 < n) and (s[i + 1] in delimiters):
                # the open delimiter before ANY delimiter quotes it: a
                # literal delimiter character, not the start of a span.
                # (A span name can't be empty, so these three sequences
                # were parse errors before -- free to repurpose.)
                out.append(s[i + 1])
                i += 2
                text_start = i
                continue
            # scan the name: up to the next delimiter
            j = i + 1
            while j < n and s[j] not in delimiters:
                j += 1
            if j >= n:
                raise ValueError(
                    f"unclosed {open_c!r} at index {i}")
            name = s[i + 1:j]
            if not name:
                raise ValueError(f"empty format name at index {i}")
            span = _Span(name, [], i)
            out.append(span)
            stack.append(span)
            if s[j] == sep_c:
                field = []
                span.fields.append(field)
                out = field
                i = j + 1
            elif s[j] == close_c:
                stack.pop()
                out = stack[-1].fields[-1] if stack else root
                i = j + 1
            else:
                raise ValueError(
                    f"nested {open_c!r} in format name at index {j}")
            text_start = i
            continue
        if c == sep_c:
            if not stack:
                raise ValueError(
                    f"stray {sep_c!r} outside any span at index {i}")
            field = []
            stack[-1].fields.append(field)
            out = field
        else:   # close_c
            if not stack:
                raise ValueError(
                    f"stray {close_c!r} outside any span at index {i}")
            stack.pop()
            out = stack[-1].fields[-1] if stack else root
        i += 1
        text_start = i
    if stack:
        raise ValueError(
            f"unclosed {open_c!r} at index {stack[-1].where}")
    if text_start < n:
        out.append(s[text_start:])
    return root


def _markup(nodes):
    "Parsed nodes back to markup: text re-escaped, spans re-wrapped."
    out = []
    for node in nodes:
        if isinstance(node, str):
            out.append(escape_styles(node))
        else:
            out.append(style(node.name, *(_markup(f) for f in node.fields)))
    return ''.join(out)


def _collect_style_runs(nodes, stack, acc):
    """
    Flatten parsed markup to (piece, stack).  A piece is a str text
    run, or a zero-arg _Span (a span with no fields) -- treated as a
    single character, so it survives split and join like ordinary
    content instead of vanishing (it has no text).

    The stack is a tuple of (name, luggage) for the enclosing spans.
    Only a span's LAST field is text to be split; any fields before
    it are luggage -- a link's URL, a fill's pattern -- serialized to
    markup and carried whole on the stack, so every split-off word
    rebuilds with them intact and join merges only words whose
    luggage matches.
    """
    for node in nodes:
        if isinstance(node, str):
            acc.append((node, tuple(stack)))
        elif not node.fields:          # a zero-arg span: one character
            acc.append((node, tuple(stack)))
        else:                          # a _Span: descend its last field
            luggage = tuple(_markup(f) for f in node.fields[:-1])
            stack.append((node.name, luggage))
            _collect_style_runs(node.fields[-1], stack, acc)
            stack.pop()


def _inner_markup(piece):
    "A collected run as final inner markup: text re-escaped, a zero-arg span verbatim."
    if isinstance(piece, str):
        return escape_styles(piece)    # _parse_markup unquoted it
    return style(piece.name)           # ⦃name⦄, a character, kept as-is


def _common_prefix(a, b):
    "The longest common prefix of two span stacks."
    out = []
    for x, y in zip(a, b):
        if x != y:
            break
        out.append(x)
    return tuple(out)


def _join_emit(runs, depth):
    """
    Serialize (markup, stack) runs -- all sharing stack[:depth] -- back
    to markup, factoring the span at `depth` shared by a consecutive run
    and recursing on the rest.  So '⦃a⦙x⦄⦃a⦙⦃b⦙y⦄⦄' collapses to
    '⦃a⦙x⦃b⦙y⦄⦄' -- one 'a' toggle, the differing 'b' nested inside.
    """
    out = []
    i = 0
    n = len(runs)
    while i < n:
        text, stack = runs[i]
        if len(stack) == depth:            # this run's text lives at this level
            out.append(text)
            i += 1
            continue
        span = stack[depth]                # a nested span: gather its consecutive run
        j = i + 1
        while j < n and len(runs[j][1]) > depth and runs[j][1][depth] == span:
            j += 1
        name, luggage = span               # same name AND same luggage
        out.append(style(name, *luggage, _join_emit(runs[i:j], depth + 1)))
        i = j
    return ''.join(out)


@export
def split_styles(s):
    """
    Rewrite style markup so every whitespace-delimited word carries
    its own balanced span:

        '⦃bold⦙This is important.⦄'
        -> '⦃bold⦙This⦄ ⦃bold⦙is⦄ ⦃bold⦙important.⦄'

    All whitespace is preserved verbatim, runs included, so a two-space
    gap stays two spaces.  This lets a downstream consumer split the
    text at whitespace -- to wrap it, lay it in columns, whatever --
    and get self-contained styled words, since a span never straddles
    a break.  Pure markup in, markup out.

    Only a span's LAST field is text; any fields before it are luggage
    (a link's URL, say) and ride along whole on every word:

        '⦃link⦙URL⦙read more⦄' -> '⦃link⦙URL⦙read⦄ ⦃link⦙URL⦙more⦄'
    """
    acc = []
    _collect_style_runs(_parse_markup(s, style_delimiters), [], acc)
    out = []
    for run, stack in acc:
        if not isinstance(run, str):           # a zero-arg span: one verbatim word
            word = style(run.name)
            for name, luggage in reversed(stack):
                word = style(name, *luggage, word)
            out.append(word)
            continue
        for word, gap in _multisplit(run, keep=True, separate=False, strip=False):
            if word:
                word = escape_styles(word)     # _parse_markup unquoted it
                for name, luggage in reversed(stack):   # inner span first
                    word = style(name, *luggage, word)
                out.append(word)
            out.append(gap)
    return ''.join(out)


@export
def join_styles(s, span_linebreaks=False):
    """
    Factor out the span stack shared by adjacent runs, wrapping each
    shared span once and nesting the differences, and absorb the
    whitespace between them:

        '⦃bold⦙This⦄ ⦃bold⦙is⦄'                    -> '⦃bold⦙This is⦄'
        '⦃a⦙with⦄ ⦃a⦙⦃code⦙x⦄⦄ ⦃a⦙z⦄'             -> '⦃a⦙with ⦃code⦙x⦄ z⦄'

    This is the inverse of split_styles, used to minimize a backend's
    output (fewer style on/off toggles) after layout.  By default it
    never merges across a newline, so every line's markup stays balanced
    and self-contained -- important for per-line consumers like columns.
    A separator that isn't pure spaces/tabs (a comma, a newline) is a
    boundary.

    Pass span_linebreaks=True to also absorb a single newline, so a span
    may straddle a line break (a wrapped heading is still one heading)
    -- fewer toggles still, at the cost of per-line balance.  A BLANK
    line -- two newlines -- is always a boundary: two blocks are never
    fused into one span.  Pure markup in, markup out; works for any
    backend.

    A span's leading fields are luggage (see split_styles); adjacent
    words merge only when their luggage matches, so two links to
    different URLs stay two links.
    """
    gap_whitespace = ' \t\n' if span_linebreaks else ' \t'
    runs = []
    _collect_style_runs(_parse_markup(s, style_delimiters), [], runs)
    # normalize each piece to final inner markup up front (escape literal
    # text, keep a zero-arg span verbatim), so a zero-arg span rides along
    # as a character.
    runs = [[_inner_markup(piece), stack] for piece, stack in runs]
    # promote a whitespace-only plain gap to the longest common stack
    # prefix of its neighbors, so it joins the surrounding group instead
    # of stranding at the top level and splitting it.
    for i, run in enumerate(runs):
        text, stack = run
        if stack or not text or text.strip(gap_whitespace):
            continue                   # not a pure whitespace plain gap
        if text.count('\n') > 1:
            continue                   # a blank line: two blocks, never one span
        left = runs[i - 1][1] if i > 0 else ()
        right = runs[i + 1][1] if (i + 1) < len(runs) else ()
        run[1] = _common_prefix(left, right)
    return _join_emit(runs, 0)


def _iter_arg_refs(segments):
    for seg in segments:
        if isinstance(seg, int):
            yield seg
        elif isinstance(seg, _Span):
            for f in seg.fields:
                yield from _iter_arg_refs(f)


class _Definition:
    """
    A validated, precompiled StyleSheet entry.  segments is the
    replacement parsed into markup nodes, with literal text
    further split at arg tokens: str nodes are literals, int
    nodes are arg indices, _Span nodes recurse.  undoable means
    "pure paint": exactly one arg, used exactly once, in a
    replacement with no nested markup--split into (before, after)
    and painted per text RUN, so nesting and _plain islands are
    correct by construction.
    """
    __slots__ = ('args', 'replacement', 'segments',
                 'undoable', 'before', 'after', 'verbatim')

    def __init__(self, name, value, delimiters):
        *args, replacement = value
        for a in args:
            if not isinstance(a, str) or not a:
                raise ValueError(
                    f"format {name!r}: args must be non-empty "
                    f"strings, got {a!r}")
            _refuse_delimiters(a, f"format {name!r} arg")
        if not isinstance(replacement, str):
            raise ValueError(
                f"format {name!r}: replacement must be str, "
                f"not {type(replacement).__name__}")
        self.args = args
        self.replacement = replacement
        nodes = _parse_markup(replacement, delimiters)
        # split literal text at arg tokens, longest token first
        order = sorted(range(len(args)),
                       key=lambda k: -len(args[k]))
        def split_text(text):
            pieces = [text]
            for k in order:
                token = args[k]
                next_pieces = []
                for piece in pieces:
                    if not isinstance(piece, str):
                        next_pieces.append(piece)
                        continue
                    parts = piece.split(token)
                    for m, part in enumerate(parts):
                        if m:
                            next_pieces.append(k)
                        if part:
                            next_pieces.append(part)
                next_pieces_or_empty = next_pieces
                pieces = next_pieces_or_empty
            return pieces
        segments = []
        def walk(nodes):
            result = []
            for node in nodes:
                if isinstance(node, str):
                    result.extend(split_text(node))
                else:
                    node.fields = [walk(f) for f in node.fields]
                    result.append(node)
            return result
        self.segments = walk(nodes)
        used = {seg for seg in _iter_arg_refs(self.segments)}
        for k, a in enumerate(args):
            if k not in used:
                raise ValueError(
                    f"format {name!r}: arg {a!r} never appears "
                    f"in the replacement")
        # classification: pure paint?
        self.undoable = False
        self.before = self.after = None
        if len(args) == 1:
            flat = self.segments
            refs = [k for k in range(len(flat))
                    if isinstance(flat[k], int)]
            spans = [seg for seg in flat if isinstance(seg, _Span)]
            if len(refs) == 1 and not spans:
                self.undoable = True
                r = refs[0]
                self.before = ''.join(flat[:r])
                self.after = ''.join(flat[r + 1:])
        # a verbatim role (like ('T', 'T')) paints nothing: it emits its
        # text and nothing else, so rendering can skip it entirely rather
        # than push an empty (before, after) pair and emit empties per run.
        self.verbatim = bool(self.undoable and not self.before and not self.after)


@export
class StyleSheet(dict):
    """
    Maps format names to definitions; .render(s) paints marked-up
    text.  A definition is a tuple of one or more strings--
    (*args, replacement), the B shape--or a callable(*fields)
    accepting the rendered fields and returning text (the escape
    hatch; its output is emitted verbatim).

    '_default', if present, catches unknown format names: it must
    take exactly one arg, and receives the unknown span's LAST
    field (the display text).  '_plain' is hard-coded--the boring
    island--and can't be an entry.

    Merging Painters (|) composes vocabularies; the left
    operand's delimiters win.
    """

    def __init__(self, formats=(), *, delimiters=style_delimiters,
                 escape=None):
        if (not isinstance(delimiters, str) or len(delimiters) != 3
                or len(set(delimiters)) != 3):
            raise ValueError(
                f"delimiters must be three distinct characters, "
                f"got {delimiters!r}")
        if escape is not None and not callable(escape):
            raise ValueError(
                f"escape must be callable or None, got {escape!r}")
        self.delimiters = delimiters
        # applied to LITERAL SOURCE text runs at render time--
        # never to definitions' replacement strings, which are
        # trusted backend syntax.  For backends whose syntax can
        # collide with real text: html.escape for HTML,
        # lambda s: s.replace('[', r'\\[') for Rich markup.
        self.escape = escape
        super().__init__()
        self.update(formats)

    def __setitem__(self, name, value):
        _validate_format(name) if name != '_default' else None
        if name == '_plain':
            raise ValueError(
                "'_plain' is hard-coded behavior, not an entry")
        if callable(value):
            super().__setitem__(name, value)
            return
        if (not isinstance(value, tuple) or not value):
            raise ValueError(
                f"format {name!r}: definition must be a tuple of "
                f"strings (*args, replacement) or a callable, "
                f"got {value!r}")
        definition = _Definition(name, value, self.delimiters)
        if name == '_default' and len(definition.args) != 1:
            raise ValueError(
                "'_default' must take exactly one arg "
                "(it receives the unknown span's display text)")
        super().__setitem__(name, definition)

    def update(self, other=(), **kwargs):
        items = other.items() if hasattr(other, 'items') else other
        for k, v in items:
            self[k] = v
        for k, v in kwargs.items():
            self[k] = v

    def __or__(self, other):
        if not isinstance(other, dict):
            return NotImplemented
        merged = StyleSheet(delimiters=self.delimiters,
                         escape=self.escape)
        merged.update(self._raw_items())
        merged.update(other._raw_items() if isinstance(other, StyleSheet)
                      else other)
        return merged

    def __ror__(self, other):
        if not isinstance(other, dict):
            return NotImplemented
        merged = StyleSheet(delimiters=self.delimiters,
                         escape=self.escape)
        merged.update(other)
        merged.update(self._raw_items())
        return merged

    def copy(self):
        fresh = StyleSheet(delimiters=self.delimiters,
                        escape=self.escape)
        fresh.update(self._raw_items())
        return fresh

    def _raw_items(self):
        # re-validation is cheap and keeps update() single-path;
        # hand back author-shaped values
        for k, v in self.items():
            if isinstance(v, _Definition):
                yield k, (*v.args, v.replacement)
            else:
                yield k, v

    def render(self, s):
        """
        Parse and paint s.  Malformed markup and arity mismatches
        raise ValueError; an unknown format with no '_default'
        raises KeyError.
        """
        nodes = _parse_markup(s, self.delimiters)
        if self.escape is not None:
            nodes = _escape_nodes(nodes, self.escape)
        out = []
        self._render(nodes, (), False, frozenset(), out.append)
        return ''.join(out)

    def _render(self, nodes, paint, strip, active, emit):
        # paint: tuple of (before, after) pairs of the enclosing
        # undoable spans.  Every text RUN is painted with the full
        # stack--nesting needs no undo, and islands simply paint
        # with an empty stack.  None means painting is OFF: inside a
        # transform's fields, definitions still resolve (glyphs,
        # rewrites, nested transforms) but nothing pushes paint, so
        # the transform sees visible text and never an escape code.
        for node in nodes:
            if isinstance(node, _Hole):
                self._render(node.nodes, paint, strip,
                             node.active, emit)
                continue
            if isinstance(node, str):
                if paint and not strip:
                    for b, a in paint:
                        emit(b)
                    emit(node)
                    for b, a in reversed(paint):
                        emit(a)
                else:
                    emit(node)
                continue
            self._render_span(node, paint, strip, active, emit)

    def _render_span(self, span, paint, strip, active, emit):
        name = span.name
        fields = span.fields
        if name == '_plain':
            # the boring island: no enclosing paint, nested
            # formats stripped to their display text
            island = fields[-1] if fields else []
            self._render(island, (), True, active, emit)
            return
        if strip:
            # inside an island (or plain rendering): every span
            # reduces to its display text
            display = fields[-1] if fields else []
            self._render(display, (), True, active, emit)
            return
        definition = self.get(name)
        display_only = False
        if definition is None:
            definition = self.get('_default')
            if definition is None:
                raise KeyError(name)
            display_only = True
        if name in active:
            raise ValueError(
                f"format reference cycle involving {name!r}")
        if callable(definition):
            # a transform: it receives its fields as VISIBLE text--
            # painting off, so nested spans resolve to their text and
            # glyphs (str.upper on an escape code, or fill counting
            # its bytes, is nobody's wish)--and its output is ordinary
            # text, painted like any run at this position.  Never
            # re-parsed.
            rendered = [self._subrender(f, None, strip, active)
                        for f in fields]
            result = definition(*rendered)
            if paint and not strip:
                for b_, a_ in paint:
                    emit(b_)
                emit(result)
                for b_, a_ in reversed(paint):
                    emit(a_)
            else:
                emit(result)
            return
        if display_only:
            fields = [fields[-1] if fields else []]
        if len(fields) != len(definition.args):
            raise ValueError(
                f"format {name!r} takes {len(definition.args)} "
                f"field(s), got {len(fields)}")
        if definition.undoable:
            if definition.verbatim or (paint is None):
                # paints nothing (a verbatim role, or painting is off):
                # render the text with the paint stack unchanged, no
                # before/after to push and undo.
                self._render(fields[0], paint, strip, active, emit)
                return
            emit_paint = paint + ((definition.before,
                                   definition.after),)
            self._render(fields[0], emit_paint, strip, active, emit)
            return
        # opaque rewrite: substitute the RAW field node trees
        # into the precompiled segments and render in place--each
        # field is painted by whatever surrounds its final
        # position, and the cycle set grows only through
        # definition expansion (fields carry the call site's set)
        def substitute(segments):
            nodes = []
            for seg in segments:
                if isinstance(seg, int):
                    nodes.append(_Hole(fields[seg], active))
                elif isinstance(seg, _Span):
                    sub = _Span(seg.name,
                                [substitute(f) for f in seg.fields],
                                seg.where)
                    nodes.append(sub)
                else:
                    nodes.append(seg)
            return nodes
        self._render(substitute(definition.segments), paint,
                     strip, active | {name}, emit)

    def _subrender(self, nodes, paint, strip, active):
        out = []
        self._render(nodes, paint, strip, active, out.append)
        return ''.join(out)


plain_stylesheet = StyleSheet({'_default': ('T', 'T')})
export('plain_stylesheet')


# strip every style span from text, leaving the visible characters.
# it's the last of the *_styles family, but it lives down here because
# it renders through plain_stylesheet.  fail-soft: text that carries an
# unquoted literal delimiter isn't markup, so return it unchanged rather
# than letting the parser raise.
@export
def strip_styles(text):
    try:
        return plain_stylesheet.render(text)
    except ValueError:
        return text
# --8<-- end big stylesheet render core --8<--


# --8<-- start big ansi stylesheets --8<--
# ---------------------------------------------------------------------
# Stock low-level ANSI maps: role -> escape sequence.  Merge one under
# a high-level theme (`theme | ansi_256_color_palette`) so the theme's conceptual
# roles resolve all the way to escapes.  The 29-color vocabulary
# (red/orange/yellow/green/cyan/blue/purple/gray, each light_/dark_/
# normal, plus white/black) is rendered at four color depths.
#
# HARD-CODED, generated from the 29-color palette by
# resources/stylesheet/palettes.py -- edit the palette and regenerate
# there rather than hand-editing the dicts below.
# ---------------------------------------------------------------------

# Generated by resources/stylesheet/palettes.py
# at 2026-09-07T08:34:49; sha256(palettes.py) = 69ada79372cfcb515bc847a337de3b7eb80db1e713babc5b9a3fff4ab2b19bd4
# Do not hand-edit -- edit palettes.py and regenerate.

ansi_truecolor_palette = StyleSheet({
    'bold': ('T', '\x1b[1mT\x1b[22m'),
    'italic': ('T', '\x1b[3mT\x1b[23m'),
    'underline': ('T', '\x1b[4mT\x1b[24m'),
    'strikethrough': ('T', '\x1b[9mT\x1b[29m'),
    'red': ('T', '\x1b[38;2;186;0;0mT\x1b[39m'),
    'light_red': ('T', '\x1b[38;2;224;0;0mT\x1b[39m'),
    'dark_red': ('T', '\x1b[38;2;133;0;0mT\x1b[39m'),
    'orange': ('T', '\x1b[38;2;199;72;0mT\x1b[39m'),
    'light_orange': ('T', '\x1b[38;2;255;92;0mT\x1b[39m'),
    'dark_orange': ('T', '\x1b[38;2;173;62;0mT\x1b[39m'),
    'amber': ('T', '\x1b[38;2;178;140;66mT\x1b[39m'),
    'light_amber': ('T', '\x1b[38;2;215;175;95mT\x1b[39m'),
    'dark_amber': ('T', '\x1b[38;2;139;101;38mT\x1b[39m'),
    'yellow': ('T', '\x1b[38;2;227;192;0mT\x1b[39m'),
    'light_yellow': ('T', '\x1b[38;2;245;222;0mT\x1b[39m'),
    'dark_yellow': ('T', '\x1b[38;2;168;144;0mT\x1b[39m'),
    'green': ('T', '\x1b[38;2;47;166;90mT\x1b[39m'),
    'light_green': ('T', '\x1b[38;2;95;208;136mT\x1b[39m'),
    'dark_green': ('T', '\x1b[38;2;30;122;60mT\x1b[39m'),
    'cyan': ('T', '\x1b[38;2;26;160;176mT\x1b[39m'),
    'light_cyan': ('T', '\x1b[38;2;79;206;220mT\x1b[39m'),
    'dark_cyan': ('T', '\x1b[38;2;14;107;120mT\x1b[39m'),
    'blue': ('T', '\x1b[38;2;47;114;192mT\x1b[39m'),
    'light_blue': ('T', '\x1b[38;2;107;166;230mT\x1b[39m'),
    'dark_blue': ('T', '\x1b[38;2;14;46;136mT\x1b[39m'),
    'purple': ('T', '\x1b[38;2;144;64;184mT\x1b[39m'),
    'light_purple': ('T', '\x1b[38;2;184;122;216mT\x1b[39m'),
    'dark_purple': ('T', '\x1b[38;2;99;16;138mT\x1b[39m'),
    'gray': ('T', '\x1b[38;2;128;128;128mT\x1b[39m'),
    'light_gray': ('T', '\x1b[38;2;179;179;179mT\x1b[39m'),
    'dark_gray': ('T', '\x1b[38;2;77;77;77mT\x1b[39m'),
    'white': ('T', '\x1b[38;2;255;255;255mT\x1b[39m'),
    'black': ('T', '\x1b[38;2;0;0;0mT\x1b[39m'),
})
export('ansi_truecolor_palette')

ansi_256_color_palette = StyleSheet({
    'bold': ('T', '\x1b[1mT\x1b[22m'),
    'italic': ('T', '\x1b[3mT\x1b[23m'),
    'underline': ('T', '\x1b[4mT\x1b[24m'),
    'strikethrough': ('T', '\x1b[9mT\x1b[29m'),
    'red': ('T', '\x1b[38;5;124mT\x1b[39m'),
    'light_red': ('T', '\x1b[38;5;160mT\x1b[39m'),
    'dark_red': ('T', '\x1b[38;5;88mT\x1b[39m'),
    'orange': ('T', '\x1b[38;5;166mT\x1b[39m'),
    'light_orange': ('T', '\x1b[38;5;202mT\x1b[39m'),
    'dark_orange': ('T', '\x1b[38;5;130mT\x1b[39m'),
    'amber': ('T', '\x1b[38;5;137mT\x1b[39m'),
    'light_amber': ('T', '\x1b[38;5;179mT\x1b[39m'),
    'dark_amber': ('T', '\x1b[38;5;94mT\x1b[39m'),
    'yellow': ('T', '\x1b[38;5;178mT\x1b[39m'),
    'light_yellow': ('T', '\x1b[38;5;220mT\x1b[39m'),
    'dark_yellow': ('T', '\x1b[38;5;136mT\x1b[39m'),
    'green': ('T', '\x1b[38;5;35mT\x1b[39m'),
    'light_green': ('T', '\x1b[38;5;78mT\x1b[39m'),
    'dark_green': ('T', '\x1b[38;5;29mT\x1b[39m'),
    'cyan': ('T', '\x1b[38;5;37mT\x1b[39m'),
    'light_cyan': ('T', '\x1b[38;5;80mT\x1b[39m'),
    'dark_cyan': ('T', '\x1b[38;5;24mT\x1b[39m'),
    'blue': ('T', '\x1b[38;5;25mT\x1b[39m'),
    'light_blue': ('T', '\x1b[38;5;74mT\x1b[39m'),
    'dark_blue': ('T', '\x1b[38;5;18mT\x1b[39m'),
    'purple': ('T', '\x1b[38;5;97mT\x1b[39m'),
    'light_purple': ('T', '\x1b[38;5;140mT\x1b[39m'),
    'dark_purple': ('T', '\x1b[38;5;54mT\x1b[39m'),
    'gray': ('T', '\x1b[38;5;244mT\x1b[39m'),
    'light_gray': ('T', '\x1b[38;5;249mT\x1b[39m'),
    'dark_gray': ('T', '\x1b[38;5;239mT\x1b[39m'),
    'white': ('T', '\x1b[38;5;231mT\x1b[39m'),
    'black': ('T', '\x1b[38;5;16mT\x1b[39m'),
})
export('ansi_256_color_palette')

ansi_16_color_palette = StyleSheet({
    'bold': ('T', '\x1b[1mT\x1b[22m'),
    'italic': ('T', '\x1b[3mT\x1b[23m'),
    'underline': ('T', '\x1b[4mT\x1b[24m'),
    'strikethrough': ('T', '\x1b[9mT\x1b[29m'),
    'red': ('T', '\x1b[31mT\x1b[39m'),
    'light_red': ('T', '\x1b[91mT\x1b[39m'),
    'dark_red': ('T', '\x1b[31mT\x1b[39m'),
    'orange': ('T', '\x1b[91mT\x1b[39m'),
    'light_orange': ('T', '\x1b[93mT\x1b[39m'),
    'dark_orange': ('T', '\x1b[91mT\x1b[39m'),
    'amber': ('T', '\x1b[33mT\x1b[39m'),
    'light_amber': ('T', '\x1b[33mT\x1b[39m'),
    'dark_amber': ('T', '\x1b[33mT\x1b[39m'),
    'yellow': ('T', '\x1b[33mT\x1b[39m'),
    'light_yellow': ('T', '\x1b[93mT\x1b[39m'),
    'dark_yellow': ('T', '\x1b[33mT\x1b[39m'),
    'green': ('T', '\x1b[32mT\x1b[39m'),
    'light_green': ('T', '\x1b[92mT\x1b[39m'),
    'dark_green': ('T', '\x1b[32mT\x1b[39m'),
    'cyan': ('T', '\x1b[36mT\x1b[39m'),
    'light_cyan': ('T', '\x1b[96mT\x1b[39m'),
    'dark_cyan': ('T', '\x1b[36mT\x1b[39m'),
    'blue': ('T', '\x1b[34mT\x1b[39m'),
    'light_blue': ('T', '\x1b[94mT\x1b[39m'),
    'dark_blue': ('T', '\x1b[34mT\x1b[39m'),
    'purple': ('T', '\x1b[35mT\x1b[39m'),
    'light_purple': ('T', '\x1b[95mT\x1b[39m'),
    'dark_purple': ('T', '\x1b[35mT\x1b[39m'),
    'gray': ('T', '\x1b[90mT\x1b[39m'),
    'light_gray': ('T', '\x1b[37mT\x1b[39m'),
    'dark_gray': ('T', '\x1b[90mT\x1b[39m'),
    'white': ('T', '\x1b[97mT\x1b[39m'),
    'black': ('T', '\x1b[30mT\x1b[39m'),
})
export('ansi_16_color_palette')

uncolored_palette = StyleSheet({
    'bold': ('T', '\x1b[1mT\x1b[22m'),
    'italic': ('T', '\x1b[3mT\x1b[23m'),
    'underline': ('T', '\x1b[4mT\x1b[24m'),
    'strikethrough': ('T', '\x1b[9mT\x1b[29m'),
    'red': ('T', 'T'),
    'light_red': ('T', 'T'),
    'dark_red': ('T', 'T'),
    'orange': ('T', 'T'),
    'light_orange': ('T', 'T'),
    'dark_orange': ('T', 'T'),
    'amber': ('T', 'T'),
    'light_amber': ('T', 'T'),
    'dark_amber': ('T', 'T'),
    'yellow': ('T', 'T'),
    'light_yellow': ('T', 'T'),
    'dark_yellow': ('T', 'T'),
    'green': ('T', 'T'),
    'light_green': ('T', 'T'),
    'dark_green': ('T', 'T'),
    'cyan': ('T', 'T'),
    'light_cyan': ('T', 'T'),
    'dark_cyan': ('T', 'T'),
    'blue': ('T', 'T'),
    'light_blue': ('T', 'T'),
    'dark_blue': ('T', 'T'),
    'purple': ('T', 'T'),
    'light_purple': ('T', 'T'),
    'dark_purple': ('T', 'T'),
    'gray': ('T', 'T'),
    'light_gray': ('T', 'T'),
    'dark_gray': ('T', 'T'),
    'white': ('T', 'T'),
    'black': ('T', 'T'),
})
export('uncolored_palette')

plain_palette = StyleSheet({
    'bold': ('T', 'T'),
    'italic': ('T', 'T'),
    'underline': ('T', 'T'),
    'strikethrough': ('T', 'T'),
    'red': ('T', 'T'),
    'light_red': ('T', 'T'),
    'dark_red': ('T', 'T'),
    'orange': ('T', 'T'),
    'light_orange': ('T', 'T'),
    'dark_orange': ('T', 'T'),
    'amber': ('T', 'T'),
    'light_amber': ('T', 'T'),
    'dark_amber': ('T', 'T'),
    'yellow': ('T', 'T'),
    'light_yellow': ('T', 'T'),
    'dark_yellow': ('T', 'T'),
    'green': ('T', 'T'),
    'light_green': ('T', 'T'),
    'dark_green': ('T', 'T'),
    'cyan': ('T', 'T'),
    'light_cyan': ('T', 'T'),
    'dark_cyan': ('T', 'T'),
    'blue': ('T', 'T'),
    'light_blue': ('T', 'T'),
    'dark_blue': ('T', 'T'),
    'purple': ('T', 'T'),
    'light_purple': ('T', 'T'),
    'dark_purple': ('T', 'T'),
    'gray': ('T', 'T'),
    'light_gray': ('T', 'T'),
    'dark_gray': ('T', 'T'),
    'white': ('T', 'T'),
    'black': ('T', 'T'),
})
export('plain_palette')


@export
def best_palette(*, file=None):
    """
    The stock low-level palette best suited to `file` (default
    sys.stdout).  If we can't colorize `file`, it's plain_stylesheet --
    fully plain text, no escapes at all; otherwise it's the deepest map
    the terminal advertises (see can_colorize and ansi_color_depth).
    """
    if not can_colorize(file=file):
        return plain_stylesheet
    return {
        'truecolor': ansi_truecolor_palette,
        '256color':  ansi_256_color_palette,
        '16color':   ansi_16_color_palette,
    }.get(ansi_color_depth(), ansi_truecolor_palette)
# --8<-- end big ansi stylesheets --8<--



mm()
