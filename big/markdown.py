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
big.markdown -- a parser for a subset of standards-compliant
CommonMark syntax.

Two halves:

  * parse(text) turns Markdown into an intermediate representation
    (the node classes below);
  * style_document(document) bakes `⦃role⦙…⦄` markup into the IR's text;
  * split_styles_document(document) splits each span to word granularity
    (so wrapping can't tear one);
  * layout_document(document) lays the IR out as a width-independent
    "layout" for wrap_words; and
  * render_document(document, format) renders the IR to GitHub-flavored
    Markdown, CommonMark, or groff `man`-macro troff.

For the terminal path, wrap_words fits the layout to a width, join_styles
coalesces the per-line markup, and a big.stylesheet StyleSheet paints it
(or plain_stylesheet strips it):

    parse -> style_document -> split_styles_document -> layout_document
          -> wrap_words -> join_styles -> stylesheet.render

render_document is a separate family of back ends over the raw parse() IR.

The IR carries what the renderer draws, plus a Raw node so anything
outside the subset (a table, raw HTML) survives to be degraded
rather than dropped.  Stdlib-only, and Python 3.6-clean.
"""

import re

from big.stylesheet import style as _style_span
from big.stylesheet import style_delimiters as _style_delims
from big.stylesheet import split_styles as _split_styles
from big.stylesheet import _parse_markup as _parse_styles
from big.stylesheet import escape_styles as _escape
from big.stylesheet import strip_styles as _strip_styles
from big.stylesheet import StyleSheet as _StyleSheet

# The glyphs layout_document draws -- bullet, quote bar, rules, alert
# emoji -- are emitted as zero-arg style roles (⦃bullet⦄, ⦃note_emoji⦄,
# ...), NOT baked characters.  A StyleSheet that defines these roles
# resolves them: markdown_defaults gives the Unicode glyphs,
# markdown_ascii_glyphs the ASCII ones.  unicode_glyphs / ascii_glyphs
# (built from those sheets, below) swap the markup for characters when
# you aren't rendering against such a sheet.
# --8<-- start big glyphs from stylesheet --8<--
# (a snippet consumer supplies _style_span -- big.stylesheet.style.)
_glyph_roles = ('bullet', 'quote_bar', 'thematic_break',
                'heading1_rule', 'heading2_rule',
                'note_emoji', 'tip_emoji', 'important_emoji',
                'warning_emoji', 'caution_emoji',
                'note_title', 'tip_title', 'important_title',
                'warning_title', 'caution_title')


def glyphs_from_stylesheet(stylesheet):
    """
    Return a function that replaces big.markdown's glyph markup with
    whatever `stylesheet` renders each glyph role to.

    Use it to measure glyph widths (as wrap_words' raw=) against the very
    sheet you'll render with, or to bake a custom glyph set.  The sheet
    must define the glyph roles (markdown_defaults does).
    """
    swaps = {_style_span(role): stylesheet.render(_style_span(role))
             for role in _glyph_roles}
    def swap(s):
        for markup, glyph in swaps.items():
            s = s.replace(markup, glyph)
        return s
    return swap
# --8<-- end big glyphs from stylesheet --8<--


def _visible(markup):
    "The visible width of glyph/style markup: glyphs resolved, styling stripped."
    return len(_strip_styles(unicode_glyphs(markup)))


#
# Node base.
#
# Every IR node is a small __slots__ class over a fixed tuple of
# fields (`_fields`).  The base supplies a positional __init__,
# a structural __eq__, and a readable __repr__ -- the last matters
# because the tests compare and print whole trees.
#

class Node:
    __slots__ = ()
    _fields = ()

    def __init__(self, *args):
        fields = self._fields
        if len(args) != len(fields):
            plural = "" if len(fields) == 1 else "s"
            raise TypeError(
                f"{type(self).__name__} takes {len(fields)} "
                f"argument{plural} ({len(args)} given)")
        for name, value in zip(fields, args):
            setattr(self, name, value)

    def _values(self):
        return tuple(getattr(self, name) for name in self._fields)

    def __eq__(self, other):
        return (type(self) is type(other)) and (self._values() == other._values())

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((type(self),) + self._values())

    def __repr__(self):
        inside = ", ".join(f"{name}={getattr(self, name)!r}"
                           for name in self._fields)
        return f"{type(self).__name__}({inside})"


#
# Block nodes.
#
# `children` always means a list of INLINE nodes; `blocks` always
# means a list of BLOCK nodes.  Keeping those two words disjoint is
# a small invariant the parser and renderer both lean on.
#

class Document(Node):
    "The whole parsed document: a list of block nodes."
    __slots__ = ('blocks',)
    _fields = ('blocks',)


class Heading(Node):
    "An ATX heading.  `level` is 1..6; `children` is inline."
    __slots__ = ('level', 'children')
    _fields = ('level', 'children')


class Paragraph(Node):
    "A paragraph; `children` is inline."
    __slots__ = ('children',)
    _fields = ('children',)


class BulletList(Node):
    """
    A `*`/`-`/`+` bullet list.  `items` is a list of ListItem.
    `tight` (bool) is CommonMark's tight-vs-loose distinction: a
    tight list renders its items without blank lines between them.
    """
    __slots__ = ('items', 'tight')
    _fields = ('items', 'tight')


class OrderedList(Node):
    """
    A numbered list.  `items` is a list of ListItem; `start` is the
    first item's number (rendered verbatim, never resequenced);
    `delimiter` is the character after the number, `.` or `)` (a
    change of delimiter starts a new list); `tight` as for BulletList.
    """
    __slots__ = ('items', 'start', 'delimiter', 'tight')
    _fields = ('items', 'start', 'delimiter', 'tight')


class ListItem(Node):
    "One item of a bullet or ordered list; `blocks` is block-level."
    __slots__ = ('blocks',)
    _fields = ('blocks',)


class DefinitionList(Node):
    "A definition list: `entries` is a list of DefinitionEntry."
    __slots__ = ('entries',)
    _fields = ('entries',)


class DefinitionEntry(Node):
    """
    One term and its definitions.  `term` is a Term; `definitions`
    is a list of Definition (a term may have more than one).
    """
    __slots__ = ('term', 'definitions')
    _fields = ('term', 'definitions')


class Term(Node):
    "A definition-list term; `children` is inline."
    __slots__ = ('children',)
    _fields = ('children',)


class Definition(Node):
    "A definition-list definition; `blocks` is block-level."
    __slots__ = ('blocks',)
    _fields = ('blocks',)


class CodeBlock(Node):
    """
    A fenced or indented code block.  `text` is the literal content
    (verbatim, tabs and all); `info` is the fence info string
    (language hint) or '' for an indented block.
    """
    __slots__ = ('text', 'info')
    _fields = ('text', 'info')


class BlockQuote(Node):
    "A `>` block quote; `blocks` is block-level."
    __slots__ = ('blocks',)
    _fields = ('blocks',)


class Alert(Node):
    """
    A GitHub alert -- a block quote whose first line is `[!KIND]`.
    `kind` is one of note/tip/important/warning/caution; `blocks` is
    the body (block-level).  Renders as a titled, colored callout.
    """
    __slots__ = ('kind', 'blocks')
    _fields = ('kind', 'blocks')


class ThematicBreak(Node):
    "A horizontal rule (`---`, `***`, `___`).  No fields."
    __slots__ = ()
    _fields = ()


class Raw(Node):
    """
    An escape hatch for a construct outside big's rendered subset --
    a table, raw HTML, a footnote.  `text` is the original Markdown
    source, preserved verbatim.  The renderer DEGRADES it (plain
    text, escaped, or alt text -- never silently dropped); the GHFM
    serializer passes it straight through, so GitHub renders it
    natively.  This is how the private IR avoids being a ceiling:
    what it can't model, it carries.
    """
    __slots__ = ('text',)
    _fields = ('text',)


#
# Inline nodes.
#

class Text(Node):
    "A run of literal text."
    __slots__ = ('text',)
    _fields = ('text',)


class StyledText(Node):
    """
    A run of text that is ALREADY well-formed ⦃role⦙…⦄ style markup.
    Where Text is escaped by style_document (a literal ⦃ in a docstring
    is quoted), StyledText is passed through verbatim -- letting a
    caller carry a role structurally rather than have the renderer
    re-derive it.  For example, a definition-list term of
    StyledText('⦃argument⦙<HOST>⦄') styles to ⦃term⦙⦃argument⦙<HOST>⦄⦄.
    style_document validates the markup (refusing an unbalanced string
    at the source) and collapses it into a Text, so the later terminal
    stages never see it.  The other renderers (render_document's GFM,
    CommonMark, troff) can't honor the roles, so -- like Raw -- they
    degrade it to its stripped text.
    """
    __slots__ = ('text',)
    _fields = ('text',)


class Strong(Node):
    "Strong emphasis (`**...**`); `children` is inline."
    __slots__ = ('children',)
    _fields = ('children',)


class Emph(Node):
    "Emphasis (`*...*`); `children` is inline."
    __slots__ = ('children',)
    _fields = ('children',)


class Strikethrough(Node):
    "Strikethrough (`~~...~~`); `children` is inline."
    __slots__ = ('children',)
    _fields = ('children',)


class Code(Node):
    "An inline code span (`` `...` ``); `text` is literal."
    __slots__ = ('text',)
    _fields = ('text',)


class Link(Node):
    """
    A link.  `children` is the inline link text; `url` is the
    destination; `title` is the optional title (or '').
    """
    __slots__ = ('children', 'url', 'title')
    _fields = ('children', 'url', 'title')


class HardBreak(Node):
    "A hard line break inside a paragraph (two trailing spaces or `\\`)."
    __slots__ = ()
    _fields = ()


#
# The block parser.
#
# Markdown text -> Document of block nodes.  Leaf inline content
# (paragraph / heading / term text) is run through _parse_inline.
#
# The parser implements the documented subset; where it doesn't
# implement a construct it degrades rather than raises, so any
# prose is accepted.
#

_atx_re        = re.compile(r' {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$')
_fence_re      = re.compile(r'( {0,3})(`{3,}|~{3,})[ \t]*(.*?)[ \t]*$')
_thematic_re   = re.compile(r' {0,3}(?:(?:\*[ \t]*){3,}|(?:-[ \t]*){3,}|(?:_[ \t]*){3,})$')
_blockquote_re = re.compile(r' {0,3}>[ ]?(.*)$')
# a GitHub alert marker on a block quote's first line: `[!NOTE]` etc.
# STRICT: the kind must be uppercase -- `[!NOTE]` matches, `[!Note]` doesn't.
_alert_re = re.compile(r'[ \t]*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\][ \t]*$')
_bullet_re     = re.compile(r'( {0,3})([*+-])(?:([ \t]+)(.*))?$')
_ordered_re    = re.compile(r'( {0,3})([0-9]{1,9})([.)])(?:([ \t]+)(.*))?$')
_defdef_re     = re.compile(r'( {0,3}):([ \t]+)(.*)$')
_indent_code_re = re.compile(r'(?: {4}|\t)')
# a setext underline: a run of only '=' (H1) or only '-' (H2).
_setext_re     = re.compile(r' {0,3}(=+|-+)[ \t]*$')


def _blank(line):
    return not line.strip()


def _dedent(line, n):
    "Strip up to n leading spaces (only spaces, never past them)."
    j = 0
    while (j < n) and (j < len(line)) and (line[j] == ' '):
        j += 1
    return line[j:]


def _trim_blanks(lines):
    "Drop leading and trailing blank lines."
    lines = list(lines)
    while lines and _blank(lines[0]):
        lines.pop(0)
    while lines and _blank(lines[-1]):
        lines.pop()
    return lines


def _is_block_start(line):
    "True if line opens a block other than a paragraph/def-list."
    return bool(_atx_re.match(line) or (_fence_re.match(line) and _fence_re.match(line).group(2))
                or _thematic_re.match(line) or _blockquote_re.match(line)
                or _bullet_re.match(line) or _ordered_re.match(line)
                or _indent_code_re.match(line))


def _interrupts_paragraph(line):
    """
    True if `line` starts a block that may INTERRUPT a paragraph.
    Narrower than _is_block_start: indented code never interrupts a
    paragraph (a 4-space line continues it), an ordered list only
    interrupts when it starts at 1, and an empty list marker never
    interrupts.  (CommonMark's paragraph-interruption rules.)
    """
    if _atx_re.match(line):
        return True
    m = _fence_re.match(line)
    if m and m.group(2):
        return True
    if _thematic_re.match(line):
        return True
    if _blockquote_re.match(line):
        return True
    m = _bullet_re.match(line)
    if m and (m.group(4) or '').strip():
        return True
    m = _ordered_re.match(line)
    if m and (int(m.group(2)) == 1) and (m.group(5) or '').strip():
        return True
    return False


#
# Inline parser.
#
# Precedence: code spans win over everything (they suppress markup
# inside), then links, then emphasis.  Emphasis uses `*`/`**` and
# `_`/`__`, with flanking guards so `*args`/`**kwargs` stay literal;
# `_` additionally can't open or close INSIDE a word, so snake_case
# identifiers never italicize (the CommonMark intra-word rule).
# Emphasis is paired with a delimiter stack (each closer to its
# nearest opener of the same character), so it nests correctly and
# can wrap code spans and links, not just plain text.
#

# the opening `[label]:` of a link reference definition.  The label
# runs to the first unescaped `]`; the destination and optional title
# that follow may spill onto later lines, so the rest is parsed by
# _parse_linkdef, not this regex.
_linkdef_open_re = re.compile(r' {0,3}\[((?:[^\]\\]|\\.)+)\]:(.*)$')

_title_close = {'"': '"', "'": "'", '(': ')'}


def _normalize_label(label):
    "CommonMark label normalization: trim, collapse whitespace, fold case."
    return re.sub(r'\s+', ' ', label.strip()).lower()


def _parse_linkdef(lines, idx):
    """
    Try to read a link reference definition beginning at lines[idx].
    A definition is `[label]: destination` with an optional title, and
    the destination and title may each wrap onto a following line, so
    this consumes as many lines as the definition spans.  The title
    may be double-quoted, single-quoted, or parenthesized.

    Returns (label, destination, title, next_index) on success, or
    None -- fail-soft, never raises, so a line that merely looks like
    a definition falls through to ordinary block parsing.
    """
    m = _linkdef_open_re.match(lines[idx])
    if not m:
        return None
    label = m.group(1)
    if not _normalize_label(label):
        return None
    # `phys[0]` is the label line's tail (after the colon); phys[1:]
    # are candidate continuation lines.  A blank line stops the scan.
    phys = [m.group(2)] + lines[idx + 1:]

    def skip_ws(li, ci):
        "Skip spaces/tabs, crossing at most one newline.  -> (li, ci, crossed)."
        line = phys[li] if li < len(phys) else ''
        while ci < len(line) and line[ci] in ' \t':
            ci += 1
        if ci < len(line):
            return li, ci, False
        # end of line: cross one newline only onto a non-blank line
        if (li + 1) < len(phys) and phys[li + 1].strip():
            li += 1
            ci = 0
            line = phys[li]
            while ci < len(line) and line[ci] in ' \t':
                ci += 1
            return li, ci, True
        return li, ci, False

    def read_dest(li, ci):
        "A destination on one line: bare (balanced parens) or <...>.  -> (dest, ci) or None."
        line = phys[li]
        return _link_destination(line, ci, len(line))

    def read_title(li, ci):
        "A quoted/parenthesized title, possibly multi-line.  -> (title, li, ci) or None."
        opener = phys[li][ci]
        closer = _title_close[opener]
        depth = 0
        buf = []
        ci += 1
        while li < len(phys):
            line = phys[li]
            if (buf and buf[-1] == '\n') and not line.strip():
                return None                      # a blank line breaks a title
            while ci < len(line):
                ch = line[ci]
                if ch == '\\' and (ci + 1) < len(line):
                    buf.append(line[ci + 1])
                    ci += 2
                    continue
                if opener == '(' and ch == '(':
                    depth += 1
                elif ch == closer:
                    if depth == 0:
                        return ''.join(buf), li, ci + 1
                    depth -= 1
                buf.append(ch)
                ci += 1
            buf.append('\n')
            li += 1
            ci = 0
        return None                              # unterminated title

    li, ci, _ = skip_ws(0, 0)
    if li >= len(phys) or ci >= len(phys[li]):
        return None
    result = read_dest(li, ci)
    if result is None:
        return None
    dest, ci = result
    if not dest:
        return None
    dest_end_li = li

    # an optional title follows, after spaces/tabs and up to one newline.
    li, ci, crossed = skip_ws(li, ci)
    if (li < len(phys)) and (ci < len(phys[li])) and (phys[li][ci] in _title_close):
        result = read_title(li, ci)
        if result is not None:
            title, tli, tci = result
            if not phys[tli][tci:].strip():      # nothing but space after title
                return label, dest, title, idx + 1 + tli
        # a title that fails on the SAME line as the destination voids the
        # whole definition; on a LATER line it just isn't part of it.
        if not crossed:
            return None
    elif (li < len(phys)) and (ci < len(phys[li])) and not crossed:
        return None                              # junk after destination

    return label, dest, '', idx + 1 + dest_end_li


# a backslash escapes only these (ASCII punctuation); before anything
# else -- a letter, digit, space -- the backslash stays literal.
_ASCII_PUNCT = set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")

# CommonMark autolinks, both spellings.  A URI autolink is a scheme
# (2-32 chars) plus anything up to '>' with no spaces or controls; an
# email autolink is an address.  Both are anchored at a leading '<'.
_uri_autolink_re = re.compile(r'<([A-Za-z][A-Za-z0-9+.\-]{1,31}:[^<>\x00-\x20]*)>')
_email_autolink_re = re.compile(
    r"<([A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*)>")


def _char_class(ch):
    """
    Classify the character on one side of a `*`/`_` run.  The start
    and end of the string, and any whitespace, count as 'space';
    ASCII punctuation is 'punct'; everything else is 'word'.  This
    is the input CommonMark's opener/closer rule looks at.
    """
    if (ch == '') or ch.isspace():
        return 'space'
    if ch in _ASCII_PUNCT:
        return 'punct'
    return 'word'


def _parse_inline(text, refs=None):
    return _inline(text, refs or {}) if text else []


def _inline(text, refs):
    """
    Parse inline Markdown into a list of nodes.

    Phase 1 scans out code spans and links as opaque nodes and
    tokenizes `*` runs into delimiter records; phase 2 pairs the
    delimiters into Strong/Emph.  Because emphasis runs over the
    WHOLE token sequence (nodes included), a `*...*` can wrap a
    link or code span, not just plain text.

    The internal item shapes are:
        ['text', str]
        ['delim', char, count, can_open, can_close]  (count mutable)
        ['node', Node]
    """
    items = []
    buf = []
    n = len(text)
    i = 0

    def flush():
        if buf:
            items.append(['text', ''.join(buf)])
            del buf[:]

    while i < n:
        c = text[i]
        if c == '\\' and (i + 1 < n) and text[i + 1] in _ASCII_PUNCT:
            # escaped punctuation: emit it as SETTLED text (its own item)
            # so it can't act as a delimiter, and so a trailing escaped
            # backslash isn't mistaken for a hard-break backslash.
            flush()
            items.append(['text', text[i + 1]])
            i += 2
            continue
        if c == '`':
            run = _run_length(text, i, '`')
            close = _find_backtick_close(text, i + run, run)
            if close != -1:
                flush()
                content = text[i + run:close].replace('\n', ' ')
                if (len(content) >= 2 and content[0] == ' '
                        and content[-1] == ' ' and content.strip()):
                    content = content[1:-1]
                items.append(['node', Code(content)])
                i = close + run
                continue
            buf.append(text[i:i + run])
            i += run
            continue
        if c == '<':
            um = _uri_autolink_re.match(text, i)
            if um:
                flush()
                url = um.group(1)
                items.append(['node', Link([Text(url)], url, '')])
                i = um.end()
                continue
            em = _email_autolink_re.match(text, i)
            if em:
                flush()
                addr = em.group(1)
                items.append(['node', Link([Text(addr)], 'mailto:' + addr, '')])
                i = em.end()
                continue
            buf.append(c)
            i += 1
            continue
        if c == '[':
            link = _try_link(text, i)
            if link:
                flush()
                label, dest, title, end = link
                items.append(['node', Link(_inline(label, refs), dest, title)])
                i = end
                continue
            ref = _try_ref_link(text, i, refs)
            if ref:
                flush()
                shown_nodes, dest, title, end = ref
                items.append(['node', Link(shown_nodes, dest, title)])
                i = end
                continue
            buf.append(c)
            i += 1
            continue
        if c == '*' or c == '_' or c == '~':
            run = _run_length(text, i, c)
            flush()
            after = text[i + run] if (i + run) < n else ''
            before = text[i - 1] if i > 0 else ''
            # CommonMark's opener/closer rule.  A run is "left-flanking"
            # (may open) when it isn't followed by space and isn't a
            # punctuation-to-word boundary; "right-flanking" (may close)
            # is the mirror.  For `_`, opening/closing additionally
            # requires a non-word neighbor on the far side, which is what
            # keeps snake_case identifiers from ever italicizing.  `*` and
            # `~` (GFM strikethrough) use the plain rule.
            b, a = _char_class(before), _char_class(after)
            left = (a != 'space') and not (a == 'punct' and b == 'word')
            right = (b != 'space') and not (b == 'punct' and a == 'word')
            if c == '_':
                can_open = left and ((not right) or (b == 'punct'))
                can_close = right and ((not left) or (a == 'punct'))
            else:
                can_open, can_close = left, right
            items.append(['delim', c, run, can_open, can_close, run])
            i += run
            continue
        if c == '\n':
            # a line ending in two+ spaces, or a backslash, is a HARD
            # break; any other newline is a soft break (a space that
            # reflows at render time), kept in the text as '\n'.
            s = ''.join(buf)
            if s.endswith('\\') or s.endswith('  '):
                del buf[:]
                shown = s[:-1] if s.endswith('\\') else s.rstrip(' ')
                if shown:
                    items.append(['text', shown])
                items.append(['node', HardBreak()])
            else:
                buf.append('\n')
            i += 1
            continue
        buf.append(c)
        i += 1
    flush()
    _pair_emphasis(items)
    return _items_to_nodes(items)


def _match_bracket(text, i):
    """
    text[i] is '['; return the index of the matching ']', where inner
    `[ ]` pairs nest and a backslash-escaped bracket doesn't count.
    Returns -1 if there is no match.
    """
    n = len(text)
    depth = 0
    k = i
    while k < n:
        c = text[k]
        if c == '\\':
            k += 2
            continue
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                return k
        k += 1
    return -1


def _link_destination(text, k, n):
    """
    Read a link destination at text[k].  Two forms: `<...>` (may hold
    spaces, but no unescaped `<`, `>`, or newline; backslash escapes
    allowed), or a bare run up to whitespace with balanced parentheses.
    Returns (destination, index_after) -- the angle form returns None
    if it's malformed (no closing `>`, or a stray `<`/newline inside).
    """
    if k < n and text[k] == '<':
        k += 1
        out = []
        while k < n:
            c = text[k]
            if c == '>':
                return ''.join(out), k + 1
            if c == '\n' or c == '<':
                return None
            if c == '\\' and (k + 1) < n and text[k + 1] in _ASCII_PUNCT:
                out.append(text[k + 1])
                k += 2
                continue
            out.append(c)
            k += 1
        return None                    # no closing '>'
    depth = 0
    start = k
    while k < n:
        c = text[k]
        if c in ' \t':
            break
        if c == '\\' and (k + 1) < n:
            k += 2
            continue
        if c == '(':
            depth += 1
        elif c == ')':
            if depth == 0:
                break
            depth -= 1
        k += 1
    return text[start:k], k


def _try_link(text, i):
    """
    Parse `[label](dest)` or `[label](dest "title")` at text[i]=='['.
    The label may contain BALANCED brackets; the destination is bare
    (balanced parens) or `<...>`.  Returns (label, dest, title, end)
    or None.
    """
    n = len(text)
    close = _match_bracket(text, i)
    if close == -1:
        return None
    label = text[i + 1:close]
    k = close + 1
    if k >= n or text[k] != '(':
        return None
    k += 1
    while k < n and text[k] in ' \t':
        k += 1
    result = _link_destination(text, k, n)
    if result is None:
        return None
    dest, k = result
    title = ''
    while k < n and text[k] in ' \t':
        k += 1
    if k < n and text[k] in '"\'':
        quote = text[k]
        k += 1
        t_start = k
        while k < n and text[k] != quote:
            k += 1
        title = text[t_start:k]
        if k < n:
            k += 1
        while k < n and text[k] in ' \t':
            k += 1
    if k >= n or text[k] != ')':
        return None
    return (label, dest, title, k + 1)


def _try_ref_link(text, i, refs):
    """
    Parse a reference link at text[i]=='[' -- full `[text][label]`,
    collapsed `[text][]`, or shortcut `[text]` -- resolving `label`
    against the collected definitions.  Returns
    (shown_nodes, dest, title, end) or None.
    """
    n = len(text)
    close = _match_bracket(text, i)
    if close == -1:
        return None
    shown = text[i + 1:close]
    k = close + 1
    if k < n and text[k] == '[':
        close2 = text.find(']', k + 1)
        if close2 == -1:
            return None
        inner = text[k + 1:close2]
        label = inner if inner.strip() else shown   # `[text][]` collapses
        end = close2 + 1
    else:
        label = shown                               # `[text]` shortcut
        end = close + 1
    entry = refs.get(_normalize_label(label))
    if entry is None:
        return None
    dest, title = entry
    return (_inline(shown, refs), dest, title, end)


def _pair_emphasis(items):
    """
    Pair delimiter records into nodes, matching each closer to its
    NEAREST preceding opener (left to right): `*`/`_` give Strong/Emph,
    a `~~` pair gives Strikethrough.  A stray unmatched opener -- the `*` of
    `*args` -- is left literal.  Mutates `items` in place; paired
    regions collapse to ['node', ...].
    """
    changed = True
    while changed:
        changed = False
        for ci in range(len(items)):
            it = items[ci]
            if not (it[0] == 'delim' and it[4]):        # can_close
                continue
            oi = None
            for k in range(ci - 1, -1, -1):
                ot = items[k]
                if not (ot[0] == 'delim' and ot[3] and ot[1] == it[1]):
                    continue                            # can_open, same char
                # strikethrough is the two-tilde form only: a `~` run that
                # isn't exactly a pair never strikes (it stays literal).
                if it[1] == '~' and not (ot[2] == 2 and it[2] == 2):
                    continue
                # CommonMark's "rule of three" (emphasis only): when either
                # run can both open and close, a match whose two ORIGINAL
                # run lengths sum to a multiple of 3 is forbidden -- unless
                # both are themselves multiples of 3.  Skip and look back.
                if it[1] != '~' and (ot[4] or it[3]) \
                        and (((ot[5] + it[5]) % 3) == 0) \
                        and ((ot[5] % 3) or (it[5] % 3)):
                    continue
                oi = k
                break
            if oi is None:
                continue
            ot = items[oi]
            inner = _items_to_nodes(items[oi + 1:ci])
            if it[1] == '~':
                use = 2
                node = Strikethrough(inner)
            else:
                use = 2 if (it[2] >= 2 and ot[2] >= 2) else 1
                node = (Strong if use == 2 else Emph)(inner)
            ot[2] -= use
            it[2] -= use
            middle = []
            if ot[2] > 0:
                middle.append(ot)
            middle.append(['node', node])
            if it[2] > 0:
                middle.append(it)
            items[oi:ci + 1] = middle
            changed = True
            break
    return items


def _items_to_nodes(items):
    "Flatten items to inline nodes, merging adjacent text and stray stars."
    out = []
    buf = []

    def flush():
        if buf:
            out.append(Text(''.join(buf)))
            del buf[:]

    for it in items:
        if it[0] == 'text':
            buf.append(it[1])
        elif it[0] == 'delim':
            buf.append(it[1] * it[2])
        else:
            flush()
            out.append(it[1])
    flush()
    return out


def _run_length(text, i, ch):
    run = 1
    while (i + run < len(text)) and (text[i + run] == ch):
        run += 1
    return run


def _find_backtick_close(text, start, run):
    "Index of the next run of EXACTLY `run` backticks, or -1."
    n = len(text)
    i = start
    while i < n:
        if text[i] == '`':
            r = _run_length(text, i, '`')
            if r == run:
                return i
            i += r
            continue
        i += 1
    return -1


def parse(text):
    "Parse a Markdown string into a Document (the big.markdown IR)."
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Expand tabs to spaces at 4-column tab stops (str.expandtabs resets
    # at every newline), which is exactly CommonMark's rule for tabs in
    # indentation -- so all the indent math downstream can count spaces.
    # (The one deviation: a literal tab INSIDE code becomes spaces here,
    # rather than surviving verbatim.  On a terminal that's invisible.)
    text = text.expandtabs(4)
    # First pass: pull out link reference definitions so references
    # resolve regardless of where the definition sits.  A definition is
    # only harvested at a block-start position (it cannot interrupt a
    # paragraph); it renders nothing.
    refs = {}
    kept = []
    at_block_start = True
    all_lines = text.split('\n')
    i = 0
    n = len(all_lines)
    while i < n:
        line = all_lines[i]
        if _blank(line):
            kept.append(line)
            at_block_start = True
            i += 1
            continue
        if at_block_start:
            result = _parse_linkdef(all_lines, i)
            if result is not None:
                label, dest, title, next_i = result
                refs.setdefault(_normalize_label(label), (dest, title))
                i = next_i                      # skip every line the def spanned
                continue                        # still at a block start
        kept.append(line)
        at_block_start = False
        i += 1
    return Document(_parse_blocks(kept, refs))


# Each _parse_<block> helper consumes one block that begins at lines[i]
# and returns (block_node, index_of_next_unconsumed_line).  The
# dispatcher below picks a helper by looking at lines[i], and moves
# the cursor forward by whatever the helper consumed.

def _parse_blocks(lines, refs=None):
    "Parse block-level lines; discard the tight/loose signal."
    return _parse_blocks_tracked(lines, refs)[0]


def _parse_blocks_tracked(lines, refs=None):
    """
    Like _parse_blocks, but also returns whether a blank line fell
    BETWEEN two top-level blocks -- CommonMark's "directly contains
    two blocks with a blank between" test for list looseness.  A blank
    interior to a nested block is consumed by that block's own parser
    and never reaches this loop, so it doesn't count here.  Returns
    (blocks, interblock_blank).
    """
    refs = refs or {}
    blocks = []
    i = 0
    n = len(lines)
    interblock_blank = False
    pending_blank = False
    while i < n:
        line = lines[i]
        if _blank(line):
            if blocks:                  # a blank after real content...
                pending_blank = True    # ...pending until the next block confirms it
            i += 1
            continue
        if pending_blank:
            interblock_blank = True
            pending_blank = False

        m = _fence_re.match(line)
        if m and m.group(2):
            block, i = _parse_fence(lines, i, m)
            blocks.append(block)
            continue

        m = _atx_re.match(line)
        if m and m.group(1):
            content = re.sub(r'[ \t]+#+$', '', m.group(2) or '').strip()
            blocks.append(Heading(len(m.group(1)), _parse_inline(content, refs)))
            i += 1
            continue

        if _thematic_re.match(line):
            blocks.append(ThematicBreak())
            i += 1
            continue

        if _blockquote_re.match(line):
            block, i = _parse_blockquote(lines, i, refs)
            blocks.append(block)
            continue

        if _bullet_re.match(line) or _ordered_re.match(line):
            block, i = _parse_list(lines, i, refs)
            blocks.append(block)
            continue

        if _indent_code_re.match(line):
            block, i = _parse_indented_code(lines, i)
            blocks.append(block)
            continue

        if (i + 1 < n) and _defdef_re.match(lines[i + 1]) and not _is_block_start(line):
            block, i = _parse_deflist(lines, i, refs)
            blocks.append(block)
            continue

        block, i = _parse_paragraph(lines, i, refs)
        blocks.append(block)
    return blocks, interblock_blank


def _parse_fence(lines, i, m):
    indent = len(m.group(1))
    fence_char = m.group(2)[0]
    fence_len = len(m.group(2))
    info = m.group(3) or ''
    close_re = re.compile(
        rf' {{0,3}}{re.escape(fence_char)}{{{fence_len},}}[ \t]*$')
    body = []
    i += 1
    n = len(lines)
    while i < n:
        if close_re.match(lines[i]):
            i += 1
            break
        body.append(_dedent(lines[i], indent))
        i += 1
    return CodeBlock('\n'.join(body), info), i


def _parse_blockquote(lines, i, refs):
    inner = []
    n = len(lines)
    while i < n:
        m = _blockquote_re.match(lines[i])
        if m:
            inner.append(m.group(1))
            i += 1
            continue
        # lazy continuation: a non-blank, non-block-start line with no
        # `>` continues the quote's current paragraph.
        if (inner and not _blank(inner[-1])
                and not _blank(lines[i]) and not _interrupts_paragraph(lines[i])):
            inner.append(lines[i])
            i += 1
            continue
        break
    # a `[!KIND]` on the first line turns the quote into a GitHub alert
    if inner:
        alert = _alert_re.match(inner[0])
        if alert:
            return Alert(alert.group(1).lower(), _parse_blocks(inner[1:], refs)), i
    return BlockQuote(_parse_blocks(inner, refs)), i


def _parse_indented_code(lines, i):
    body = []
    n = len(lines)
    while i < n:
        line = lines[i]
        if _indent_code_re.match(line):
            body.append(line[1:] if line[:1] == '\t' else line[4:])
            i += 1
        elif _blank(line):
            body.append('')
            i += 1
        else:
            break
    while body and _blank(body[-1]):
        body.pop()
    return CodeBlock('\n'.join(body), ''), i


def _parse_list(lines, i, refs):
    n = len(lines)
    ordered = bool(_ordered_re.match(lines[i]))
    if ordered:
        marker_key = _ordered_re.match(lines[i]).group(3)
        start = int(_ordered_re.match(lines[i]).group(2))
    else:
        marker_key = _bullet_re.match(lines[i]).group(2)
        start = None
    items = []
    loose = False
    while i < n:
        m = _ordered_re.match(lines[i]) if ordered else _bullet_re.match(lines[i])
        if not m:
            break
        if ordered:
            if m.group(3) != marker_key:
                break
            lead, marker = len(m.group(1)), m.group(2) + m.group(3)
            gap, first = m.group(4) or '', m.group(5) or ''
        else:
            if m.group(2) != marker_key:
                break
            lead, marker = len(m.group(1)), m.group(2)
            gap, first = m.group(3) or '', m.group(4) or ''
        # a marker followed by 5+ spaces caps the gap at 1: the rest
        # becomes the item's content indent, so `-      foo` holds an
        # indented code block, not a paragraph.
        if len(gap) > 4:
            first = gap[1:] + first
            gap = ' '
        content_col = lead + len(marker) + len(gap)
        item_lines = [first]
        i += 1
        in_gap = False
        while i < n:
            l = lines[i]
            if _blank(l):
                item_lines.append('')
                in_gap = True
                i += 1
                continue
            indent = len(l) - len(l.lstrip(' '))
            if indent >= content_col:
                item_lines.append(l[content_col:])
                in_gap = False
                i += 1
                continue
            if (_ordered_re if ordered else _bullet_re).match(l):
                break
            if (not in_gap) and (not _is_block_start(l)):
                item_lines.append(l.strip())
                i += 1
                continue
            break
        trimmed = _trim_blanks(item_lines)
        # loose if an item DIRECTLY contains two blocks split by a blank
        # (a blank buried in a nested block doesn't count -- that's the
        # nested list's business), or if a blank sits between this item
        # and a following sibling.  A blank merely trailing the whole
        # list (e.g. the final newline) does NOT make it loose.
        item_blocks, item_interblank = _parse_blocks_tracked(trimmed, refs)
        if item_interblank:
            loose = True
        if item_lines and _blank(item_lines[-1]) and (i < n):
            sm = _ordered_re.match(lines[i]) if ordered else _bullet_re.match(lines[i])
            # only a blank before a SAME-marker sibling loosens; a
            # different marker starts a new list and must not.
            if sm and ((sm.group(3) if ordered else sm.group(2)) == marker_key):
                loose = True
        items.append(ListItem(item_blocks))
    tight = not loose
    if ordered:
        return OrderedList(items, start, marker_key, tight), i
    return BulletList(items, tight), i


def _parse_deflist(lines, i, refs):
    n = len(lines)
    entries = []
    while i < n:
        term_line = lines[i]
        if _blank(term_line) or _is_block_start(term_line):
            break
        if not ((i + 1 < n) and _defdef_re.match(lines[i + 1])):
            break
        term = Term(_parse_inline(term_line.strip(), refs))
        i += 1
        definitions = []
        while i < n:
            dm = _defdef_re.match(lines[i])
            if not dm:
                break
            # `:` is a list-family marker, so the section 5.2 content
            # column applies exactly as for `-`/`1.`: 1-4 spaces set
            # the column, 5+ tips the first line into indented code.
            gap, content = dm.group(2), dm.group(3)
            if len(gap) > 4:
                content = gap[1:] + content
                gap = ' '
            content_col = len(dm.group(1)) + 1 + len(gap)
            def_lines = [content]
            i += 1
            in_gap = False
            while i < n:
                l = lines[i]
                if _blank(l):
                    def_lines.append('')
                    in_gap = True
                    i += 1
                    continue
                indent = len(l) - len(l.lstrip(' '))
                if indent >= content_col:
                    def_lines.append(l[content_col:])
                    in_gap = False
                    i += 1
                    continue
                if _defdef_re.match(l):
                    break
                # lazy paragraph continuation -- but a line that is
                # itself a term (a following `:`) starts a new entry
                # and must not be swallowed here.
                if (not in_gap) and (not _interrupts_paragraph(l)):
                    if (i + 1 < n) and _defdef_re.match(lines[i + 1]):
                        break
                    def_lines.append(l.strip())
                    i += 1
                    continue
                break
            definitions.append(Definition(_parse_blocks(_trim_blanks(def_lines), refs)))
        entries.append(DefinitionEntry(term, definitions))
    return DefinitionList(entries), i


def _parse_paragraph(lines, i, refs):
    n = len(lines)
    paragraph = []
    while i < n:
        line = lines[i]
        # a setext underline (=/-) directly under paragraph text turns
        # the whole collected paragraph into a heading.  Checked BEFORE
        # the thematic-break interrupt, so `text` over `---` is an H2,
        # while `---` after a blank line stays a thematic break.
        if paragraph:
            sm = _setext_re.match(line)
            if sm:
                level = 1 if sm.group(1)[0] == '=' else 2
                return Heading(level, _parse_inline('\n'.join(paragraph).rstrip(), refs)), i + 1
        if _blank(line) or _interrupts_paragraph(line):
            break
        if paragraph and (i + 1 < n) and _defdef_re.match(lines[i + 1]):
            break
        # keep TRAILING whitespace (it may signal a hard break); strip
        # only leading (insignificant, reflowed away).
        paragraph.append(line.lstrip())
        i += 1
    return Paragraph(_parse_inline('\n'.join(paragraph).rstrip(), refs)), i


#
# Styling: bake role markup into the IR's text.
#
# style_document(document) returns a copy of the IR whose inline text carries
# `⦃role⦙…⦄` markup: Strong -> bold, Emph -> italic, Strikethrough ->
# strikethrough, Code -> code, Link -> link, and a Heading's text is
# wrapped in heading1..heading6 by level.  The block STRUCTURE is
# preserved (it's still a Document), so layout_document can lay it
# out; the generated glyphs it draws (list markers, heading rules)
# are styled there, not here, since they aren't text of any node.
#

def _validate_styled_markup(text):
    "Refuse a StyledText whose markup isn't well-formed, at the source."
    try:
        _parse_styles(text, _style_delims)
    except ValueError as e:
        raise ValueError(
            f'StyledText markup is malformed: {text!r} ({e})') from e


def _styled_text(nodes):
    "Inline nodes -> one markup string (bold/italic/strike/code/link)."
    out = []
    for node in nodes:
        if isinstance(node, Text):
            out.append(_escape(node.text))       # literal delimiters -> quoted
        elif isinstance(node, StyledText):
            _validate_styled_markup(node.text)   # refuse imbalance, noisily
            out.append(node.text)                # already valid markup: verbatim
        elif isinstance(node, Strong):
            out.append(_style_span('bold', _styled_text(node.children)))
        elif isinstance(node, Emph):
            out.append(_style_span('italic', _styled_text(node.children)))
        elif isinstance(node, Strikethrough):
            out.append(_style_span('strikethrough', _styled_text(node.children)))
        elif isinstance(node, Code):
            out.append(_style_span('code', _escape(node.text)))
        elif isinstance(node, Link):
            out.append(_style_span('link', _styled_text(node.children)))
        elif isinstance(node, HardBreak):
            out.append('\n')     # only reached if a break nests inside a span
    return ''.join(out)


def _styled_inline(nodes):
    "Inline nodes -> [Text(markup) | HardBreak], hard breaks kept as nodes."
    result = []
    run = []
    for node in nodes:
        if isinstance(node, HardBreak):
            if run:
                result.append(Text(_styled_text(run)))
                run = []
            result.append(HardBreak())
        else:
            run.append(node)
    if run:
        result.append(Text(_styled_text(run)))
    return result


def _style_blocks(blocks):
    return [_style_block(block) for block in blocks]


def _style_block(block):
    if isinstance(block, Heading):
        text = _style_span(f'heading{block.level}', _styled_text(block.children))
        return Heading(block.level, [Text(text)])
    if isinstance(block, Paragraph):
        return Paragraph(_styled_inline(block.children))
    if isinstance(block, BulletList):
        return BulletList(
            [ListItem(_style_blocks(item.blocks)) for item in block.items],
            block.tight)
    if isinstance(block, OrderedList):
        return OrderedList(
            [ListItem(_style_blocks(item.blocks)) for item in block.items],
            block.start, block.delimiter, block.tight)
    if isinstance(block, BlockQuote):
        return BlockQuote(_style_blocks(block.blocks))
    if isinstance(block, Alert):
        # title + bar are render-generated glyphs; just style the body
        return Alert(block.kind, _style_blocks(block.blocks))
    if isinstance(block, DefinitionList):
        return DefinitionList([_style_entry(entry) for entry in block.entries])
    if isinstance(block, CodeBlock):
        # style each line on its own -- layout_document splits the block
        # at newlines to indent it, so a whole-block span would tear.
        # The whole line (its own indentation included) rides in `code`.
        lines = [_style_span('codeblock', _escape(line)) if line else line
                 for line in block.text.split('\n')]
        return CodeBlock('\n'.join(lines), block.info)
    # ThematicBreak, Raw: no inline text to style
    return block


def _style_entry(entry):
    # the whole term wears the `term` role, so it can read as a label
    term = Term([Text(_style_span('term', _styled_text(entry.term.children)))])
    definitions = [Definition(_style_blocks(d.blocks)) for d in entry.definitions]
    return DefinitionEntry(term, definitions)


def style_document(document):
    """
    Return a copy of `document` with styling markup baked into its
    text -- each inline run wrapped in its role and each heading in
    heading1..heading6.  The result is still an IR; feed it to
    layout_document to lay out, then to a StyleSheet to paint (or
    to plain_stylesheet to strip the markup back out).
    """
    return Document(_style_blocks(document.blocks))


def _map_style_text(node):
    "Rebuild an IR node, running split_styles over every string field."
    if isinstance(node, CodeBlock):
        return node                    # code is verbatim: never word-split
    if isinstance(node, Node):
        return type(node)(*(_map_style_text(getattr(node, f)) for f in node._fields))
    if isinstance(node, list):
        return [_map_style_text(child) for child in node]
    if isinstance(node, str):
        return _split_styles(node)
    return node                        # ints and the like pass through


def split_styles_document(document):
    """
    Return a copy of a styled document with every span split to word
    granularity (see big.stylesheet.split_styles) -- built on top of it,
    applied to each node's text.  This lets wrap_words wrap lines
    without tearing a span; run it after style_document, before
    the layout.  join_styles undoes it on the laid-out text.
    """
    return _map_style_text(document)


# Default definitions for every high-level role big.markdown emits, so
# a document paints before any theme touches it and an UNDEFINED role
# is a loud error, not a silent pass-through (no _default here on
# purpose).  All do-nothing except `codeblock`, which inherits `code`.
# The low-level attribute/color roles (bold, red, ...) come from a
# backend map.  Compose UNDER a theme:  markdown_defaults | theme | ansi_256_color_palette
# --8<-- start big markdown defaults --8<--
markdown_defaults = _StyleSheet({
    'heading1':   ('T', 'T'),
    'heading2':   ('T', 'T'),
    'heading3':   ('T', 'T'),
    'heading4':   ('T', 'T'),
    'heading5':   ('T', 'T'),
    'heading6':   ('T', 'T'),
    'code':       ('T', 'T'),
    'codeblock':  ('T', '⦃code⦙T⦄'),
    'link':       ('T', 'T'),
    'marker':     ('T', 'T'),
    'blockquote': ('T', 'T'),
    'rule':       ('T', 'T'),
    'term':       ('T', 'T'),
    # GitHub alerts: each kind wears a color; the title is that color
    # over heading2 (do-nothing by default, a theme's heading style if
    # set).  note=blue, tip=green, important=purple, warning=orange,
    # caution=red.
    'note':              ('T', '⦃blue⦙T⦄'),
    'heading_note':      ('T', '⦃heading2⦙⦃blue⦙T⦄⦄'),
    'tip':               ('T', '⦃green⦙T⦄'),
    'heading_tip':       ('T', '⦃heading2⦙⦃green⦙T⦄⦄'),
    'important':         ('T', '⦃purple⦙T⦄'),
    'heading_important': ('T', '⦃heading2⦙⦃purple⦙T⦄⦄'),
    'warning':           ('T', '⦃orange⦙T⦄'),
    'heading_warning':   ('T', '⦃heading2⦙⦃orange⦙T⦄⦄'),
    'caution':           ('T', '⦃red⦙T⦄'),
    'heading_caution':   ('T', '⦃heading2⦙⦃red⦙T⦄⦄'),
    # the glyphs layout_document draws, as zero-arg roles (Unicode by
    # default; ascii_glyphs()/unicode_glyphs() swap them without a sheet).
    # heading{1,2}_rule are the rule characters, for a width-aware renderer
    # to fill; layout_document itself draws no heading rules.
    'bullet':          ('•',),
    'quote_bar':       ('│ ',),
    'thematic_break':  ('─────',),
    'heading1_rule':   ('=',),
    'heading2_rule':   ('-',),
    'note_emoji':      ('ℹ️',),
    'tip_emoji':       ('💡',),
    'important_emoji': ('✴',),
    'warning_emoji':   ('⚠️',),
    'caution_emoji':   ('🛑',),
    # the alert title words, as roles -- override for another language
    'note_title':      ('Note',),
    'tip_title':       ('Tip',),
    'important_title': ('Important',),
    'warning_title':   ('Warning',),
    'caution_title':   ('Caution',),
})

# the same glyph roles, in ASCII -- for terminals (or pipes) that can't
# show the Unicode glyphs.  Only the glyph roles; compose over a palette
# for the rest, or resolve with ascii_glyphs().
markdown_ascii_glyphs = _StyleSheet({
    'bullet':          ('*',),
    'quote_bar':       ('| ',),
    'thematic_break':  ('-----',),
    'heading1_rule':   ('=',),
    'heading2_rule':   ('-',),
    'note_emoji':      ('(i)',),
    'tip_emoji':       ('(*)',),
    'important_emoji': ('(!)',),
    'warning_emoji':   ('/!\\',),
    'caution_emoji':   ('(x)',),
    'note_title':      ('Note',),
    'tip_title':       ('Tip',),
    'important_title': ('Important',),
    'warning_title':   ('Warning',),
    'caution_title':   ('Caution',),
})
# --8<-- end big markdown defaults --8<--

# the two stock glyph swappers, built from the sheets above (these are
# big-side helpers, deliberately NOT in the snippet).
unicode_glyphs = glyphs_from_stylesheet(markdown_defaults)
ascii_glyphs = glyphs_from_stylesheet(markdown_ascii_glyphs)


#
# The terminal layout: IR -> a "layout" for wrap_words.
#
# layout_document lays the block structure out as a flat tuple of
# words and instructions -- markers, quote bars, and code indents
# become ('indent', ...) prefixes -- WITHOUT committing to a width, and
# hard-coding nothing: every glyph, alert title, and the thematic break
# is a role resolved by the StyleSheet.  It's the width-independent
# half; wrap_words fits it to a terminal later, then join_styles and a
# StyleSheet paint or strip it:
#
#     wrap_words(layout, margin=width, raw=strip_styles)
#         -> join_styles -> stylesheet.render
#
# The structural glyphs it draws always carry their role markup (a
# marker, a bar, a rule); painting them plain is plain_stylesheet's
# job, not a mode here.
#

_CODE_INDENT = '    '


def _flow_words(children):
    "Styled inline nodes -> words, with '\\n' for each hard break."
    words = []
    for node in children:
        if isinstance(node, HardBreak):
            words.append('\n')
        elif isinstance(node, Text):
            words.extend(node.text.split())
    return words


def layout_document(document):
    """
    Lay a styled, split Document out as a "layout": a flat tuple of
    words and wrap_words instructions, ready to fit to any width.

    The document must have been through style_document (so its text
    carries `⦃role⦙…⦄` markup) and split_styles_document (so a line
    break can't tear a span).  The layout is width-independent -- build
    it once, then at render time:

        wrap_words(layout, margin=width, raw=strip_styles)

    and pass the result through join_styles and a StyleSheet's render
    (or plain_stylesheet, to strip the markup back to plain text).
    """
    out = []
    _layout_blocks(document.blocks, '', '', False, out)
    return tuple(out)


def _layout_blocks(blocks, lead, rest, tight, out):
    # Lay a run of blocks into `out`.  The first block wears `lead` on
    # its first line (a list marker, say); every other block, and every
    # continuation line, wears `rest`.  Blocks are separated by a blank
    # line unless the enclosing list is tight.
    separator = '\n' if tight else '\n\n'
    for index, block in enumerate(blocks):
        if index:
            out.append(separator)
        _layout_block(block, lead if (index == 0) else rest, rest, out)


def _layout_block(block, lead, rest, out):
    if isinstance(block, Paragraph):
        out.append(('indent', lead, rest))
        out.extend(_flow_words(block.children))
        return
    if isinstance(block, Heading):
        # every heading is just its styled text (it already wears its
        # heading{n} role).  A rule under it depends on the line width,
        # so layout_document draws none; a width-aware renderer can add
        # one from the heading{n}_rule role.
        out.append(('indent', lead, rest))
        out.extend(_flow_words(block.children))
        return
    if isinstance(block, ThematicBreak):
        out.append(('indent', lead, rest))
        out.append(_style_span('rule', _style_span('thematic_break')))
        return
    if isinstance(block, CodeBlock):
        out.append(('indent', lead + _CODE_INDENT, rest + _CODE_INDENT))
        for index, line in enumerate(block.text.split('\n')):
            if index:
                out.append('\n')
            out.append(line)                 # a code line is one verbatim word
        return
    if isinstance(block, BlockQuote):
        bar = _style_span('blockquote', _style_span('quote_bar'))
        _layout_blocks(block.blocks, lead + bar, rest + bar, False, out)
        return
    if isinstance(block, Alert):
        bar = _style_span(block.kind, _style_span('quote_bar'))
        title = _style_span(block.kind + '_emoji') + ' ' + _style_span(block.kind + '_title')
        out.append(('indent', lead + bar, rest + bar))
        out.append(_style_span('heading_' + block.kind, title))
        out.append('\n')
        _layout_blocks(block.blocks, rest + bar, rest + bar, False, out)
        return
    if isinstance(block, BulletList):
        _layout_list(block, False, lead, rest, out)
        return
    if isinstance(block, OrderedList):
        _layout_list(block, True, lead, rest, out)
        return
    if isinstance(block, DefinitionList):
        _layout_deflist(block, lead, rest, out)
        return
    if isinstance(block, Raw):
        out.append(('indent', lead, rest))
        for index, line in enumerate(block.text.split('\n')):
            if index:
                out.append('\n')
            out.append(line)
        return


def _layout_list(list_node, ordered, lead, rest, out):
    # Right-align the markers so their bullets/periods share a column,
    # then one space; every item's text -- first line and continuations
    # -- starts at the next column.
    if ordered:
        markers = [f'{list_node.start + index}{list_node.delimiter}'
                   for index in range(len(list_node.items))]
    else:
        markers = [_style_span('bullet')] * len(list_node.items)
    widths = [_visible(marker) for marker in markers]
    marker_width = max(widths, default=0)
    pad = rest + (' ' * (marker_width + 1))
    separator = '\n' if list_node.tight else '\n\n'
    for index, item in enumerate(list_node.items):
        if index:
            out.append(separator)
        marker = markers[index]
        align = ' ' * (marker_width - widths[index])
        glyph = _style_span('marker', marker)
        if not item.blocks:                  # empty item: just the marker
            out.append(('indent', lead + align, pad))
            out.append(glyph)
            continue
        item_lead = lead + align + glyph + ' '
        _layout_blocks(item.blocks, item_lead, pad, list_node.tight, out)


def _flatten(nodes):
    "Inline nodes -> plain text (color and bold dropped)."
    out = []
    for node in nodes:
        if isinstance(node, (Text, Code)):
            out.append(node.text)
        elif isinstance(node, (Strong, Emph, Strikethrough, Link)):
            out.append(_flatten(node.children))
        elif isinstance(node, HardBreak):
            out.append(' ')       # collapses to a space outside a paragraph
    return ''.join(out)


def _layout_deflist(dl, lead, rest, out):
    # A definition list can't be laid out here: its detail column
    # depends on the runtime width (see deflist.layout.proposal.md), so
    # it rides into wrap_words structurally, bracketed by 'def start'
    # and 'def end', one ('term', ...) per entry followed by the words
    # and blocks of its details.  wrap_words measures the terms, picks
    # the column, and lays each entry out against the real width.
    out.append(('indent', lead, rest))
    out.append(('def start',))
    for entry in dl.entries:
        out.append(('term', *_flow_words(entry.term.children)))
        definitions = []
        for definition in entry.definitions:
            definitions.extend(definition.blocks)
        _layout_blocks(definitions, '', '', False, out)
    out.append(('def end',))


#
# The troff renderer: IR -> groff `man` macros, for a man page.
#
# A back end alongside layout_document, but simpler: troff does its own
# line-filling and font handling, so there's no width math and no
# StyleSheet -- it walks the (unstyled) parse() IR and emits macros.
# It produces the man-page BODY (the .SH sections); the caller supplies
# the `.TH name section date ...` header.
#

def _troff_escape(text):
    "Escape troff specials in a run of text: backslash, and hyphen->minus."
    return text.replace('\\', '\\e').replace('-', '\\-')


def _troff_protect(line):
    "Guard a line that would otherwise look like a macro (leading . or ')."
    return ('\\&' + line) if line[:1] in ('.', "'") else line


def _troff_text(text):
    "Escape a possibly-multi-line run, protecting each line's first column."
    return '\n'.join(_troff_protect(_troff_escape(line))
                     for line in text.split('\n'))


def _troff_inline(nodes):
    "Inline nodes -> a troff string (font escapes; no line macros)."
    out = []
    for node in nodes:
        if isinstance(node, Text):
            out.append(_troff_text(node.text))
        elif isinstance(node, StyledText):
            out.append(_troff_text(_strip_styles(node.text)))   # roles can't survive troff
        elif isinstance(node, Strong):
            out.append('\\fB' + _troff_inline(node.children) + '\\fP')
        elif isinstance(node, Emph):
            out.append('\\fI' + _troff_inline(node.children) + '\\fP')
        elif isinstance(node, Code):
            out.append('\\fB' + _troff_text(node.text) + '\\fP')
        elif isinstance(node, Strikethrough):
            out.append(_troff_inline(node.children))   # no troff strike
        elif isinstance(node, Link):
            text = _troff_inline(node.children)
            if node.url and node.url != _flatten(node.children):
                out.append(text + ' <' + _troff_text(node.url) + '>')
            else:
                out.append(text)
    return ''.join(out)


def _troff_paragraph(children, lead='.PP'):
    "A paragraph, splitting at hard breaks into `.br`-separated lines."
    out = [lead] if lead else []
    segment = []
    for node in children:
        if isinstance(node, HardBreak):
            out.append(_troff_inline(segment))
            out.append('.br')
            segment = []
        else:
            segment.append(node)
    out.append(_troff_inline(segment))
    return out


def _troff_item_blocks(blocks):
    "An item/definition body: first paragraph inline, the rest as blocks."
    out = []
    for index, block in enumerate(blocks):
        if index == 0 and isinstance(block, Paragraph):
            out.append(_troff_inline(block.children))   # sits under the .IP/.TP
        else:
            out.extend(_troff_block(block))
    return out


def _troff_block(block):
    if isinstance(block, Heading):
        macro = '.SH' if block.level == 1 else '.SS'
        return [macro + ' ' + _troff_inline(block.children)]
    if isinstance(block, Paragraph):
        return _troff_paragraph(block.children)
    if isinstance(block, (BulletList, OrderedList)):
        ordered = isinstance(block, OrderedList)
        out = []
        for index, item in enumerate(block.items):
            if ordered:
                out.append(f'.IP "{block.start + index}{block.delimiter}" 4')
            else:
                out.append('.IP \\(bu 3')
            out.extend(_troff_item_blocks(item.blocks))
        return out
    if isinstance(block, DefinitionList):
        out = []
        for entry in block.entries:
            out.append('.TP')
            out.append('\\fB' + _troff_inline(entry.term.children) + '\\fP')
            for definition in entry.definitions:
                out.extend(_troff_item_blocks(definition.blocks))
        return out
    if isinstance(block, CodeBlock):
        return ['.EX'] + [_troff_text(line) for line in block.text.split('\n')] + ['.EE']
    if isinstance(block, BlockQuote):
        return ['.RS 4'] + _troff_blocks(block.blocks) + ['.RE']
    if isinstance(block, Alert):
        title = block.kind.capitalize()
        return (['.PP', '\\fB' + title + ':\\fP', '.RS 4']
                + _troff_blocks(block.blocks) + ['.RE'])
    if isinstance(block, ThematicBreak):
        return ['.sp']
    if isinstance(block, Raw):
        return [_troff_text(block.text)]
    return []


def _troff_blocks(blocks):
    out = []
    for block in blocks:
        out.extend(_troff_block(block))
    return out


#
# The Markdown back ends: IR -> GitHub-flavored or CommonMark Markdown.
#
# One serializer, parameterized by `gfm`.  The flavors differ only
# where big's extensions have no native form in the target:
#
#   strikethrough   gfm: ~~x~~        commonmark: dropped to plain text
#   alert           gfm: > [!KIND]    commonmark: > **Kind** blockquote
#   definition list gfm: <dl> HTML    commonmark: **term** + > details
#
# Everything else is ordinary CommonMark, which GFM is a superset of.
#

def _md_code_span(text):
    "Wrap inline code in the shortest backtick run that clears its content."
    ticks = '`'
    while ticks in text:
        ticks += '`'
    if text and (text[0] == '`' or text[-1] == '`'):
        return f'{ticks} {text} {ticks}'      # pad, so an edge backtick reads
    return f'{ticks}{text}{ticks}'


def _md_inline(nodes, gfm):
    "Inline nodes -> a Markdown string."
    out = []
    for node in nodes:
        if isinstance(node, Text):
            out.append(node.text)
        elif isinstance(node, StyledText):
            out.append(_strip_styles(node.text))   # roles can't survive Markdown
        elif isinstance(node, Strong):
            out.append('**' + _md_inline(node.children, gfm) + '**')
        elif isinstance(node, Emph):
            out.append('*' + _md_inline(node.children, gfm) + '*')
        elif isinstance(node, Code):
            out.append(_md_code_span(node.text))
        elif isinstance(node, Strikethrough):
            inner = _md_inline(node.children, gfm)
            out.append(f'~~{inner}~~' if gfm else inner)   # commonmark: drop it
        elif isinstance(node, Link):
            inner = _md_inline(node.children, gfm)
            if node.title:
                out.append(f'[{inner}]({node.url} "{node.title}")')
            else:
                out.append(f'[{inner}]({node.url})')
        elif isinstance(node, HardBreak):
            out.append('  \n')
    return ''.join(out)


def _md_prefix(text, first, rest):
    "Prefix the first line with `first` and every other line with `rest`."
    lines = text.split('\n')
    out = []
    for index, line in enumerate(lines):
        prefix = first if (index == 0) else rest
        # a blank line keeps only the trimmed prefix (e.g. '>' not '> ')
        out.append((prefix + line) if line else prefix.rstrip())
    return '\n'.join(out)


def _md_blocks(blocks, gfm):
    "A run of blocks -> Markdown, a blank line between them."
    return '\n\n'.join(_md_block(block, gfm) for block in blocks)


def _md_deflist(dl, gfm):
    if gfm:
        # inline HTML, with a blank line after each open tag so the term
        # and details are still parsed as Markdown ("the blank-line trick").
        parts = ['<dl>']
        for entry in dl.entries:
            parts.append('<dt>\n\n' + _md_inline(entry.term.children, gfm) + '\n\n</dt>')
            for definition in entry.definitions:
                parts.append('<dd>\n\n' + _md_blocks(definition.blocks, gfm) + '\n\n</dd>')
        parts.append('</dl>')
        return '\n'.join(parts)
    # CommonMark: a bold term, a hard break, then the details as a blockquote.
    entries = []
    for entry in dl.entries:
        term = '**' + _md_inline(entry.term.children, gfm) + '**'
        blocks = []
        for definition in entry.definitions:
            blocks.extend(definition.blocks)
        entries.append(term + '  \n' + _md_prefix(_md_blocks(blocks, gfm), '> ', '> '))
    return '\n\n'.join(entries)


def _md_block(block, gfm):
    if isinstance(block, Heading):
        return '#' * block.level + ' ' + _md_inline(block.children, gfm)
    if isinstance(block, Paragraph):
        return _md_inline(block.children, gfm)
    if isinstance(block, ThematicBreak):
        return '---'
    if isinstance(block, CodeBlock):
        fence = '```'
        while fence in block.text:
            fence += '`'
        return fence + block.info + '\n' + block.text + '\n' + fence
    if isinstance(block, BlockQuote):
        return _md_prefix(_md_blocks(block.blocks, gfm), '> ', '> ')
    if isinstance(block, Alert):
        body = _md_blocks(block.blocks, gfm)
        if gfm:
            head = f'[!{block.kind.upper()}]\n' + body
            return _md_prefix(head, '> ', '> ')
        title = '**' + block.kind.capitalize() + '**\n' + body
        return _md_prefix(title, '> ', '> ')
    if isinstance(block, (BulletList, OrderedList)):
        ordered = isinstance(block, OrderedList)
        pieces = []
        for index, item in enumerate(block.items):
            marker = f'{block.start + index}{block.delimiter} ' if ordered else '- '
            pieces.append(_md_prefix(_md_blocks(item.blocks, gfm), marker, ' ' * len(marker)))
        return ('\n' if block.tight else '\n\n').join(pieces)
    if isinstance(block, DefinitionList):
        return _md_deflist(block, gfm)
    if isinstance(block, Raw):
        return block.text
    return ''


def render_document(document, format):
    """
    Render a Document to text in one of three formats (no default):

        'gfm'         GitHub-Flavored Markdown
        'commonmark'  CommonMark (big's extensions degraded to plain
                      CommonMark: no strikethrough, alert -> blockquote,
                      definition list -> bold term + blockquote)
        'troff'       groff `man`-macro troff, the BODY of a man page
                      (`.SH`/`.SS`, `.TP`, `.IP`, `.EX`/`.EE`, `\\fB`);
                      the caller prepends the `.TH ...` header.

    Call it on the raw parse() IR, not on style_document output -- it
    reads the structured inline nodes, not role markup.
    """
    if format == 'gfm':
        return _md_blocks(document.blocks, True)
    if format == 'commonmark':
        return _md_blocks(document.blocks, False)
    if format == 'troff':
        return '\n'.join(_troff_blocks(document.blocks))
    raise ValueError(
        f"unknown format {format!r}; use 'gfm', 'commonmark', or 'troff'")


# The full node vocabulary, for the parser/renderer to import and
# for tests to introspect.
__all__ = [
    'Node',
    # block
    'Document', 'Heading', 'Paragraph',
    'BulletList', 'OrderedList', 'ListItem',
    'DefinitionList', 'DefinitionEntry', 'Term', 'Definition',
    'CodeBlock', 'BlockQuote', 'Alert', 'ThematicBreak', 'Raw',
    # inline
    'Text', 'StyledText', 'Strong', 'Emph', 'Strikethrough', 'Code', 'Link', 'HardBreak',
    # parser + renderers
    'parse', 'style_document', 'split_styles_document', 'layout_document',
    'render_document', 'markdown_defaults', 'markdown_ascii_glyphs',
    'unicode_glyphs', 'ascii_glyphs', 'glyphs_from_stylesheet',
]
