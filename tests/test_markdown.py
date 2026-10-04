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
Tests for big.markdown: the IR nodes, the block parser, the inline
parser, and the plain-text renderer.
"""

import bigtestlib
bigtestlib.preload_local_big()

from big.test import raises, raises_regex

import big.markdown
from big.markdown import *
from big.stylesheet import StyleSheet, plain_stylesheet, join_styles, strip_styles
from big.text import wrap_words


# The terminal pipeline: parse -> style -> split -> layout_document ->
# wrap_words -> join_styles -> a StyleSheet.  These helpers drive it the
# way callers do; width=0 means "no maximum" (an enormous margin).  The
# glyphs layout draws are markup (⦃bullet⦄, ...), so the wrap-time raw=
# resolves them through the SAME sheet that will paint, to measure
# visible width; plain output is that sheet over plain_stylesheet, so
# glyphs and the list pad (a fill) resolve while paint drops out.
_NO_MAX = 2 ** 31

def _pipeline(md, width, sheet=markdown_defaults):
    layout = layout_document(split_styles_document(style_document(parse(md))))
    if not layout:
        return ''
    margin = _NO_MAX if width == 0 else width
    glyphs = glyphs_from_stylesheet(sheet)
    raw = lambda w: strip_styles(glyphs(w))
    return join_styles(wrap_words(layout, margin=margin, raw=raw))

def _rstrip(text):
    return '\n'.join(line.rstrip() for line in text.split('\n'))

def markup(md, width=79):
    "the laid-out span markup, before glyphs are resolved or a sheet paints it"
    return _rstrip(_pipeline(md, width))

def render(md, width=79, sheet=markdown_defaults):
    "plain terminal text: rendered through `sheet` with all paint dropped"
    return _rstrip((sheet | plain_stylesheet).render(_pipeline(md, width, sheet)))


#
# IR nodes
#

def test_node_fields_and_equality():
    h = Heading(1, [Text('x')])
    assert h.level == 1
    assert h.children == [Text('x')]
    assert Heading(1, [Text('x')]) == Heading(1, [Text('x')])
    assert Heading(1, [Text('x')]) != Heading(2, [Text('x')])
    # different types are never equal, even with equal field values
    assert Paragraph([Text('x')]) != Term([Text('x')])
    # a no-field node
    assert ThematicBreak() == ThematicBreak()

def test_node_hash_and_repr():
    assert hash(ThematicBreak()) == hash(ThematicBreak())
    assert hash(Code('x')) == hash(Code('x'))
    r = repr(Heading(2, [Text('hi')]))
    assert r.startswith('Heading(')
    assert 'level=2' in r

def test_node_arity_is_checked():
    with raises(TypeError):
        Heading(1)               # too few
    with raises(TypeError):
        Heading(1, [], 'extra')  # too many

def test_document_kinds():
    # Document is abstract; parse and style_document each return their kind
    with raises(TypeError):
        Document([])
    raw = parse("some **b**\n")
    assert type(raw) is MarkdownDocument
    styled = style_document(raw)
    assert type(styled) is StyledDocument
    assert type(split_styles_document(styled)) is StyledDocument
    # the kinds never compare equal, even with equal blocks
    assert MarkdownDocument([]) != StyledDocument([])
    # each stage demands its kind, naming the mistake
    with raises_regex(TypeError, 'applied twice'):
        style_document(styled)                   # would have double-escaped
    with raises_regex(TypeError, 'render_document needs a MarkdownDocument'):
        render_document(styled, 'gfm')           # would have leaked markup
    with raises_regex(TypeError, 'call style_document first'):
        layout_document(raw)                     # would have laid out unstyled text

def test_all_exports_resolve():
    for name in big.markdown.__all__:
        assert hasattr(big.markdown, name), name


#
# Block parser
#

def test_heading():
    assert parse("# Title\n") == MarkdownDocument([Heading(1, [Text('Title')])])
    assert parse("###### Six\n") == MarkdownDocument([Heading(6, [Text('Six')])])
    # a closing run of hashes is stripped
    assert parse("## Two ##\n") == MarkdownDocument([Heading(2, [Text('Two')])])

def test_setext_headings():
    assert parse("Big Title\n=========\n") == MarkdownDocument([Heading(1, [Text('Big Title')])])
    assert parse("Sub Heading\n---\n") == MarkdownDocument([Heading(2, [Text('Sub Heading')])])
    # the underline applies to the whole preceding paragraph
    assert parse("one\ntwo\n===\n") == MarkdownDocument([Heading(1, [Text('one\ntwo')])])

def test_dashes_context_disambiguates():
    # under a paragraph line -> setext H2
    assert parse("text\n---\n") == MarkdownDocument([Heading(2, [Text('text')])])
    # after a blank line -> thematic break
    assert parse("p\n\n---\n") == MarkdownDocument([Paragraph([Text('p')]), ThematicBreak()])
    # spaced (not a contiguous run) -> thematic break, not setext
    assert parse("text\n- - -\n") == MarkdownDocument([Paragraph([Text('text')]), ThematicBreak()])

def test_heading_requires_space_and_at_most_six():
    # no space after the hashes -> not a heading
    assert parse("#nope\n") == MarkdownDocument([Paragraph([Text('#nope')])])
    # seven hashes -> not a heading
    assert parse("####### seven\n") == MarkdownDocument([Paragraph([Text('####### seven')])])

def test_paragraph_keeps_its_soft_breaks():
    got = parse("Hello world\nsecond line\n")
    assert got == MarkdownDocument([Paragraph([Text('Hello world\nsecond line')])])

def test_thematic_break():
    assert parse("---\n") == MarkdownDocument([ThematicBreak()])
    assert parse("***\n") == MarkdownDocument([ThematicBreak()])
    assert parse("___\n") == MarkdownDocument([ThematicBreak()])

def test_fenced_code():
    got = parse("```python\nx = 1\n  y = 2\n```\n")
    assert got == MarkdownDocument([CodeBlock('x = 1\n  y = 2', 'python')])
    # tilde fence, no info string
    assert parse("~~~\ncode\n~~~\n") == MarkdownDocument([CodeBlock('code', '')])

def test_indented_code():
    assert parse("    exec foo -v\n") == MarkdownDocument([CodeBlock('exec foo -v', '')])

def test_tabs_expand_to_four_column_stops():
    # a single leading tab reaches column 4 -> indented code block
    assert parse("\tcode\n") == MarkdownDocument([CodeBlock('code', '')])
    # after a one-char marker, a tab reaches column 4, so the item's
    # content column is 4 and a tab-indented continuation folds in
    assert parse("-\tfoo\n\tbar\n") == MarkdownDocument([
        BulletList([ListItem([Paragraph([Text('foo\nbar')])])], True)])

def test_indented_code_does_not_interrupt_paragraph():
    got = parse("ordinary paragraph\n    indented continuation\n")
    assert got == MarkdownDocument([
        Paragraph([Text('ordinary paragraph\nindented continuation')]),
    ])

def test_bullet_list_tight():
    got = parse("- one\n- two\n")
    assert got == MarkdownDocument([BulletList([
        ListItem([Paragraph([Text('one')])]),
        ListItem([Paragraph([Text('two')])]),
    ], True)])

def test_ordered_list_verbatim_start():
    j = parse("3. c\n4. d\n").blocks[0]
    assert isinstance(j, OrderedList)
    assert j.start == 3          # rendered verbatim, never resequenced
    assert j.tight is True
    assert len(j.items) == 2

def test_ordered_list_delimiter_preserved():
    # `.` and `)` are both kept and rendered as typed
    dot = parse("1. a\n2. b\n").blocks[0]
    assert dot.delimiter == '.'
    assert render("1) a\n2) b\n") == "1) a\n2) b"
    # switching the delimiter starts a NEW list (CommonMark)
    blocks = parse("1. a\n2) b\n").blocks
    assert [b.delimiter for b in blocks] == ['.', ')']

def test_list_tight_vs_loose():
    assert parse("- a\n- b\n").blocks[0].tight is True
    # a blank between items makes the list loose
    assert parse("- a\n\n- b\n").blocks[0].tight is False
    # so does an item that spans a blank (multiple blocks)
    assert parse("- a\n\n  still a\n- b\n").blocks[0].tight is False

def test_list_loose_blank_stays_in_nested_list():
    # a blank INSIDE a sublist loosens only the sublist; the outer
    # list stays tight (CommonMark counts only blanks that DIRECTLY
    # separate an item's own blocks)
    outer = parse("- a\n  - x\n\n  - y\n").blocks[0]
    assert outer.tight is True
    inner = outer.items[0].blocks[1]
    assert inner.tight is False

def test_nested_list():
    outer = parse("- outer\n  - inner\n- outer2\n").blocks[0]
    assert len(outer.items) == 2
    inner = outer.items[0].blocks[1]
    assert isinstance(inner, BulletList)
    assert inner.items[0].blocks[0] == Paragraph([Text('inner')])

def test_list_item_with_five_space_marker_gap_starts_with_code():
    got = parse("-     indented code\n")
    assert got == MarkdownDocument([
        BulletList([
            ListItem([CodeBlock('indented code', '')]),
        ], True),
    ])

def test_blockquote_contains_blocks():
    bq = parse("> a note\n> - point\n").blocks[0]
    assert isinstance(bq, BlockQuote)
    assert bq.blocks[0] == Paragraph([Text('a note')])
    assert isinstance(bq.blocks[1], BulletList)

def test_blockquote_lazy_continuation():
    got = parse("> quoted first line\nlazy second line\n")
    assert got == MarkdownDocument([
        BlockQuote([
            Paragraph([Text('quoted first line\nlazy second line')]),
        ]),
    ])

def test_definition_list_single():
    got = parse("verbose\n: Controls verbosity.\n")
    assert got == MarkdownDocument([DefinitionList([
        DefinitionEntry(
            Term([Text('verbose')]),
            [Definition([Paragraph([Text('Controls verbosity.')])])]),
    ])])

def test_definition_list_multiple_entries():
    dl = parse("a\n: one\n\nb\n: two\n").blocks[0]
    assert isinstance(dl, DefinitionList)
    assert len(dl.entries) == 2
    assert dl.entries[0].term == Term([Text('a')])
    assert dl.entries[1].term == Term([Text('b')])

def test_definition_continuation_lines():
    dl = parse("term\n: first line\n  second line\n").blocks[0]
    defn = dl.entries[0].definitions[0]
    assert defn == Definition([Paragraph([Text('first line\nsecond line')])])

def test_number_at_line_start_is_a_list():
    # the chosen CommonMark quirk: "1980." opens an ordered list
    j = parse("1980. was a good year\n").blocks[0]
    assert isinstance(j, OrderedList)
    assert j.start == 1980

def test_ordered_list_start_other_than_one_does_not_interrupt_paragraph():
    got = parse("ordinary paragraph\n2. still ordinary prose\n")
    assert got == MarkdownDocument([
        Paragraph([Text('ordinary paragraph\n2. still ordinary prose')]),
    ])

def test_empty_input():
    assert parse("") == MarkdownDocument([])
    assert parse("\n\n\n") == MarkdownDocument([])


#
# Inline parser
#

def test_inline_emphasis():
    p = parse("a **bold** and *italic* c\n").blocks[0]
    assert p == Paragraph([
        Text('a '), Strong([Text('bold')]),
        Text(' and '), Emph([Text('italic')]), Text(' c')])

def test_inline_nested_emphasis():
    p = parse("**a *b* c**\n").blocks[0]
    assert p == Paragraph([Strong([Text('a '), Emph([Text('b')]), Text(' c')])])

def test_underscore_emphasis():
    assert parse("_italic_\n").blocks[0] == Paragraph([Emph([Text('italic')])])
    assert parse("__bold__\n").blocks[0] == Paragraph([Strong([Text('bold')])])
    # the intra-word rule protects identifiers
    for src in ("snake_case_name", "CONST_NAME", "a_b_c"):
        assert parse(src + "\n").blocks[0] == Paragraph([Text(src)]), src

def test_emphasis_flanking_and_rule_of_three():
    # CommonMark's opener/closer rule and "rule of three".  Serialize
    # the inline tree to a compact string so the intent is legible.
    def ser(nodes):
        out = []
        for n in nodes:
            if isinstance(n, Text):
                out.append(n.text)
            elif isinstance(n, Emph):
                out.append('<em>' + ser(n.children) + '</em>')
            elif isinstance(n, Strong):
                out.append('<st>' + ser(n.children) + '</st>')
        return ''.join(out)

    cases = {
        'foo*bar*baz':      'foo<em>bar</em>baz',      # intraword * opens
        'foo_bar_baz':      'foo_bar_baz',             # intraword _ stays literal
        '5_6_78':           '5_6_78',                  # digits count as word
        'a * foo*':         'a * foo*',                # space after opener
        '*(*foo*)*':        '<em>(<em>foo</em>)</em>', # punctuation-adjacent nesting
        'a**"foo"**b':      'a**"foo"**b',             # punct boundary blocks pairing
        '***foo***':        '<em><st>foo</st></em>',
        '*foo**bar***':     '<em>foo<st>bar</st></em>',
        '**foo*bar*baz**':  '<st>foo<em>bar</em>baz</st>',
    }
    for src, want in cases.items():
        got = ser(parse(src + '\n').blocks[0].children)
        assert got == want, (src, got, want)

def test_strikethrough():
    # GFM two-tilde strikethrough, and it composes with emphasis
    assert parse("~~gone~~\n").blocks[0] == Paragraph([Strikethrough([Text('gone')])])
    assert parse("~~**x**~~\n").blocks[0] == Paragraph([Strikethrough([Strong([Text('x')])])])
    assert parse("**~~x~~**\n").blocks[0] == Paragraph([Strong([Strikethrough([Text('x')])])])
    # only the two-tilde form strikes; singles/triples and stray `~`
    # (e.g. `~/path` in prose) stay literal
    for src in ("~one~", "a ~~~three~~~ b", "rm ~/a and ~/b"):
        assert parse(src + "\n").blocks[0] == Paragraph([Text(src)]), src

def test_hard_break_nodes():
    # two trailing spaces, or a backslash, make a HardBreak node
    assert parse("a  \nb\n").blocks[0] == Paragraph([Text('a'), HardBreak(), Text('b')])
    assert parse("a\\\nb\n").blocks[0] == Paragraph([Text('a'), HardBreak(), Text('b')])
    # a plain newline is a soft break (stays as text, reflows)
    assert parse("a\nb\n").blocks[0] == Paragraph([Text('a\nb')])

def test_hard_break_rendering():
    assert render("a  \nb\n", 40) == "a\nb"       # hard: forced
    assert render("a\nb\n", 40) == "a b"          # soft: reflowed

def test_backslash_escapes():
    assert parse(r"\*not italic\*" + "\n").blocks[0] == Paragraph([Text('*not italic*')])
    assert parse(r"a \[b\]" + "\n").blocks[0] == Paragraph([Text('a [b]')])
    assert parse("\\\\\n").blocks[0] == Paragraph([Text('\\')])   # \\ -> one backslash
    # backslash before a non-punctuation char stays literal
    assert parse(r"C:\path" + "\n").blocks[0] == Paragraph([Text(r'C:\path')])
    # an escaped star is literal while a real one still emphasizes
    assert parse(r"\* but *real*" + "\n").blocks[0] == Paragraph([
        Text('* but '), Emph([Text('real')])])

def test_inline_nested_strong_inside_emphasis():
    p = parse("*a **b** c*\n").blocks[0]
    assert p == Paragraph([Emph([Text('a '), Strong([Text('b')]), Text(' c')])])

def test_inline_code_span():
    assert parse("`a`\n").blocks[0] == Paragraph([Code('a')])
    # a single leading and trailing space is stripped
    assert parse("` a `\n").blocks[0] == Paragraph([Code('a')])

def test_inline_code_suppresses_markup():
    p = parse("see `**x**` please\n").blocks[0]
    assert p == Paragraph([Text('see '), Code('**x**'), Text(' please')])

def test_inline_link():
    p = parse("see [docs](http://x) now\n").blocks[0]
    assert p == Paragraph([
        Text('see '), Link([Text('docs')], 'http://x', ''), Text(' now')])

def test_inline_link_with_title_and_markup():
    p = parse('[**bold** text](u "t")\n').blocks[0]
    assert p == Paragraph([Link([Strong([Text('bold')]), Text(' text')], 'u', 't')])

def test_inline_link_destination_with_balanced_parentheses():
    p = parse("[docs](https://example.test/a_(b))\n").blocks[0]
    assert p == Paragraph([
        Link([Text('docs')], 'https://example.test/a_(b)', ''),
    ])

def test_link_angle_bracket_destination():
    # <...> destinations may hold spaces; the brackets are stripped
    assert parse("[t](<a b>)\n").blocks[0] == Paragraph([Link([Text('t')], 'a b', '')])
    assert parse("[t](<>)\n").blocks[0] == Paragraph([Link([Text('t')], '', '')])
    # and in a reference definition, with a title
    d = parse("[t]\n\n[t]: <my url> \"T\"\n")
    assert d.blocks[0] == Paragraph([Link([Text('t')], 'my url', 'T')])

def test_inline_link_label_with_balanced_brackets():
    # the label runs to the MATCHING ']', so brackets may nest inside
    p = parse("see [the [advanced] mode](u) now\n").blocks[0]
    assert p == Paragraph([
        Text('see '),
        Link([Text('the [advanced] mode')], 'u', ''),
        Text(' now'),
    ]), p
    # a backslash-escaped bracket doesn't count toward nesting
    p = parse(r"[a \[b c](u)" + "\n").blocks[0]
    assert p == Paragraph([Link([Text('a [b c')], 'u', '')]), p

def test_bracketed_span():
    # Pandoc's bracketed_spans: [text]{.class} is a Span whose classes
    # are style roles
    p = parse("see [foo]{.argument} now\n").blocks[0]
    assert p == Paragraph([Text('see '), Span([Text('foo')], ('argument',)), Text(' now')])
    # the label is inline content; several classes are all kept, in order
    p = parse("[**b** x]{.a .b}\n").blocks[0]
    assert p == Paragraph([Span([Strong([Text('b')]), Text(' x')], ('a', 'b'))])
    # no span ATTEMPT (no '{' right after ']') -> literal, fail-soft
    for src in ("[foo]", "[foo] {.a}", "[foo]{.a}{.b}"):
        p = parse(src + "\n").blocks[0]
        assert not (src == "[foo] {.a}" and any(isinstance(n, Span) for n in p.children)), src
    assert parse("[foo] {.a}\n").blocks[0] == Paragraph([Text('[foo] {.a}')])
    # a span attempt with a bad attribute block RAISES -- the author
    # meant a span, so a silent pass-through would hide the mistake:
    # an id, a key=value, an invalid role name, empty braces, unclosed
    for src, why in (("[foo]{#id}", "only .class"), ("[foo]{.a key=v}", "only .class"),
                     ("[foo]{.no-hyphens}", "not a valid role name"),
                     ("[foo]{}", "no class"), ("[foo]{.a", "unclosed")):
        with raises_regex(ValueError, why):
            parse(src + "\n")
    # an explicit class beats a shortcut reference link of the same label
    doc = parse("[foo]{.c}\n\n[foo]: http://x\n")
    assert doc.blocks[0] == Paragraph([Span([Text('foo')], ('c',))])
    # a link is still a link
    assert isinstance(parse("[foo](http://x)\n").blocks[0].children[0], Link)

def test_bracketed_span_renders():
    # style_document: the class is the role; classes nest outermost first
    assert style_document(parse("[foo]{.argument}\n")).blocks[0] == \
        Paragraph([Text('⦃argument⦙foo⦄')])
    assert style_document(parse("[x]{.a .b}\n")).blocks[0] == \
        Paragraph([Text('⦃a⦙⦃b⦙x⦄⦄')])
    # through the terminal pipeline, a sheet that defines the role paints it
    sheet = markdown_defaults | StyleSheet({'argument': ('T', '<T>')})
    assert render("use [host]{.argument} here\n", 40, sheet=sheet) == "use <host> here"
    # the other renderers can't carry a class: the content survives, bare
    doc = parse("a [b]{.c} d\n")
    assert render_document(doc, 'gfm') == "a b d"
    assert render_document(doc, 'commonmark') == "a b d"
    assert render_document(doc, 'troff') == ".PP\na b d"

def test_autolinks():
    # a URI autolink: the URL is both destination and visible text
    p = parse("see <https://x.io/a?b=1> ok\n").blocks[0]
    assert p == Paragraph([
        Text('see '),
        Link([Text('https://x.io/a?b=1')], 'https://x.io/a?b=1', ''),
        Text(' ok'),
    ]), p
    # an email autolink gets a mailto: destination
    assert parse("<me@example.com>\n").blocks[0] == Paragraph([
        Link([Text('me@example.com')], 'mailto:me@example.com', '')])
    # angle brackets that aren't a valid autolink stay literal
    for src in ("<not a url>", "<foo>"):
        assert parse(src + "\n").blocks[0] == Paragraph([Text(src)]), src

def test_inline_identifiers_stay_literal():
    # openers with no closer, stars against whitespace, and snake_case
    # never turn into emphasis
    for src in ("*args", "**kwargs", "snake_case_name", "a * b"):
        p = parse(src + "\n").blocks[0]
        assert p == Paragraph([Text(src)]), src

def test_reference_link_all_three_forms():
    full = parse("[docs][d]\n\n[d]: http://x \"T\"\n").blocks[0]
    assert full == Paragraph([Link([Text('docs')], 'http://x', 'T')])
    collapsed = parse("[docs][]\n\n[docs]: http://x\n").blocks[0]
    assert collapsed == Paragraph([Link([Text('docs')], 'http://x', '')])
    shortcut = parse("[docs]\n\n[docs]: http://x\n").blocks[0]
    assert shortcut == Paragraph([Link([Text('docs')], 'http://x', '')])

def test_reference_link_undefined_stays_literal():
    assert parse("[nope]\n").blocks[0] == Paragraph([Text('[nope]')])

def test_reference_definition_is_invisible_and_case_insensitive():
    # the `[docs]: ...` line renders nothing; `[Docs]` still resolves
    d = parse("A [Docs] link.\n\n[docs]: http://x\n")
    assert d == MarkdownDocument([Paragraph([
        Text('A '), Link([Text('Docs')], 'http://x', ''), Text(' link.')])])

def test_reference_definition_title_styles():
    # a definition's title may be double-, single-, or paren-quoted
    for defn, title in (('"dq"', 'dq'), ("'sq'", 'sq'), ('(par)', 'par')):
        src = "[x]\n\n[x]: /u " + defn + "\n"
        assert parse(src).blocks[0] == Paragraph([Link([Text('x')], '/u', title)]), defn

def test_reference_definition_spans_lines():
    # destination and title may each wrap onto a following line
    src = "[x]\n\n[x]:\n   /u\n   \"the title\"\n"
    assert parse(src).blocks[0] == Paragraph([Link([Text('x')], '/u', 'the title')]), src
    # a title that fails to parse on a LATER line leaves a dest-only
    # definition, and the stray line becomes ordinary content
    src = "[x]: /u\nnot a title\n\n[x]\n"
    doc = parse(src)
    assert doc.blocks[-1] == Paragraph([Link([Text('x')], '/u', '')]), doc
    # junk after the destination on the SAME line voids the definition
    assert parse("[x]: /u junk\n").blocks[0] == Paragraph([Text('[x]: /u junk')])




#
# Further parser bugs (Claude, 2026-08-03).  Like the six above
# these tests encode the CORRECT behavior and fail against the
# current parser, each demonstrating a distinct defect.
#

def test_stray_opener_does_not_capture_identifiers():
    # A closer pairs with the NEAREST opener (CommonMark), not the
    # first one seen.  The current _find_span keeps the FIRST
    # opener forever, so the stray `*` of `*args` captures the
    # later real span and `*args` -- the very identifier the
    # flanking guards exist to protect -- is swallowed INTO the
    # emphasis: Emph('args to *foo').
    p = parse("pass *args to *foo* now\n").blocks[0]
    assert p == Paragraph([
        Text('pass *args to '), Emph([Text('foo')]), Text(' now')]), p
    # the minimal form of the same defect
    p = parse("*a *b*\n").blocks[0]
    assert p == Paragraph([Text('*a '), Emph([Text('b')])]), p


def test_emphasis_wraps_inline_structures():
    # Emphasis whose content contains a link or code span: the
    # current pass runs _emph only on the GAPS between structures,
    # so delimiters that straddle one can never pair and render as
    # literal stars.
    p = parse("*[docs](u)*\n").blocks[0]
    assert p == Paragraph([Emph([Link([Text('docs')], 'u', '')])]), p
    p = parse("*a `b` c*\n").blocks[0]
    assert p == Paragraph([Emph([Text('a '), Code('b'), Text(' c')])]), p


def test_adjacent_list_of_other_marker_does_not_loosen():
    # `- a` then a blank then `* b` is TWO lists (marker change),
    # and list one -- a single single-block item with no internal
    # blank -- is tight.  The trailing-blank sibling check matches
    # ANY bullet marker, so the `*` that opens the SECOND list
    # falsely loosens the first.
    d = parse("- a\n\n* b\n")
    assert len(d.blocks) == 2
    first, second = d.blocks
    assert isinstance(first, BulletList) and isinstance(second, BulletList)
    assert first.tight is True, first
    assert second.tight is True, second


def test_empty_list_items():
    # a bare marker is an EMPTY list item (CommonMark), not prose
    assert parse("-\n") == MarkdownDocument([
        BulletList([ListItem([])], True)]), parse("-\n")
    # and between siblings it must not be lazily JOINED into the
    # previous item's paragraph text (the current parser mangles
    # this into Text('x\n-'))
    j = parse("- x\n-\n- y\n").blocks[0]
    assert isinstance(j, BulletList)
    assert len(j.items) == 3, j
    assert j.items[0].blocks == [Paragraph([Text('x')])]
    assert j.items[1].blocks == []
    assert j.items[2].blocks == [Paragraph([Text('y')])]


def test_definition_gap_is_structural():
    # ruled 2026-08-03: `:` is a list-family marker, so section 5.2
    # applies -- a 2-space gap sets the content column to 3, and the
    # continuation aligns there (structural, like `-`), NOT to a
    # fixed colon+1.
    dl = parse("term\n:  first\n   second\n").blocks[0]
    assert dl.entries[0].definitions[0] == Definition([
        Paragraph([Text('first\nsecond')])])

def test_definition_blocks_attach_at_the_content_column():
    # a FURTHER block (after a blank line) belongs to the definition when
    # it's indented to the content column -- wherever the text starts
    # after the colon -- and is a new top-level block otherwise.  So the
    # "four spaces" of the conventional `:   text` is just that form's
    # column; `: text` puts it at two.
    two = parse("term\n: first\n\n  second\n").blocks
    assert len(two) == 1 and len(two[0].entries[0].definitions[0].blocks) == 2
    four = parse("term\n:   first\n\n    second\n").blocks
    assert len(four) == 1 and len(four[0].entries[0].definitions[0].blocks) == 2
    # short of the column: the paragraph is NOT the definition's
    short = parse("term\n:   first\n\n  second\n").blocks
    assert [type(b).__name__ for b in short] == ['DefinitionList', 'Paragraph']
    bare = parse("term\n:   first\n\nsecond\n").blocks
    assert [type(b).__name__ for b in bare] == ['DefinitionList', 'Paragraph']

def test_definition_lazy_continuation():
    # like any list item, an unindented continuation line still joins
    # the definition's paragraph lazily.
    dl = parse("term\n: first\nlazy line\n").blocks[0]
    assert dl.entries[0].definitions[0] == Definition([
        Paragraph([Text('first\nlazy line')])])



#
# Renderer: plain-text layout
#

def test_render_paragraph_wraps():
    assert render("one two three four five\n", 13) == "one two three\nfour five"

def test_render_paragraphs_separated():
    assert render("a\n\nb\n", 20) == "a\n\nb"

def test_render_bullet_list():
    assert render("- a\n- b\n", 20) == "• a\n• b"

def test_render_ordered_from_start():
    assert render("3. c\n4. d\n", 20) == "3. c\n4. d"

def test_render_ordered_right_aligned():
    # markers right-align within the list so the periods share a
    # column and the text shares the next-but-one column
    assert render("9. nine\n10. ten\n", 20) == " 9. nine\n10. ten"

def test_render_nested_tight():
    assert render("- outer\n  - inner\n", 20) == "• outer\n  • inner"

def test_render_loose_has_blanks():
    assert render("- a\n\n- b\n", 20) == "• a\n\n• b"

def test_render_code_block_indented():
    assert render("```\nx = 1\n```\n", 20) == "    x = 1"

def test_render_blockquote_prefixed():
    assert render("> hi there\n", 20) == "│ hi there"

def test_render_thematic_break():
    # a thematic break spans the line: its one-character glyph is tiled
    # by wrap_words to the width that's left past the prefix
    assert render("---\n", 5) == "─────"
    assert render("---\n", 12) == "────────────"
    assert render("a\n\n---\n\nb\n", 8) == "a\n\n────────\n\nb"
    # inside a quote or list it spans the remaining ribbon, not the margin
    assert render("> ---\n", 8) == "│ ──────"
    # (`- ---` is itself a thematic break -- spaced dashes -- so the
    # list case needs a real item with the break as a later block)
    assert render("- foo\n\n  ---\n", 12) == "• foo\n\n  ──────────"
    # a heading's rule is still hugged to its text, not the margin
    assert render("## Hi\n", 12) == "Hi\n--"
    # Tight lists need no blank line to identify a full-width divider.
    assert render("- a\n  ***\n", 20) == "• a\n  " + "─" * 18
    assert render("> - a\n>   ***\n", 20) == "│ • a\n│   " + "─" * 16

def test_render_definition_list():
    # narrow terminal (thin ribbon) -> tall: term on its own line
    assert render("term\n: def here\n", 20) == "term\n    def here"
    # roomy terminal -> compact: the term shares its line with the details,
    # all aligned at the detail column
    compact = render("serve\n: Start it.\n\nstop\n: Stop it.\n", 60)
    assert compact == "serve  Start it.\nstop   Stop it."
    # a nested bullet list in the details lands at the detail column
    nested = render("term\n: intro\n\n    - one\n    - two\n", 60)
    assert nested == "term  intro\n\n      • one\n      • two"
    # a nested definition list is its own table inside the detail column:
    # its terms neither widen the outer column nor become outer entries
    md = "outer\n: intro\n\n    inner\n    : detail\n\n    after\n"
    assert render(md, 60) == ("outer  intro\n"
                              "\n"
                              "       inner  detail\n"
                              "\n"
                              "       after")

def test_render_hanging_wrap():
    # continuation of a wrapped item hangs under the item's text
    out = render("- word word word word\n", 12)
    assert out == "• word word\n  word word"


#
# Styling pipeline: parse -> style -> split -> layout -> wrap -> join -> render
#

def test_style_bakes_role_markup():
    # style() wraps inline runs and headings in their roles
    assert style_document(parse("# Hi\n")).blocks[0] == Heading(1, [Text('⦃heading1⦙Hi⦄')])
    para = style_document(parse("a **b** *c* `d` ~~e~~ [f](u)\n")).blocks[0]
    assert para == Paragraph([Text(
        'a ⦃bold⦙b⦄ ⦃italic⦙c⦄ ⦃code⦙d⦄ ⦃strikethrough⦙e⦄ ⦃link⦙u⦙f⦄')])
    # plain_stylesheet strips it all back to the plain text
    assert plain_stylesheet.render(para.children[0].text) == 'a b c d e f'

def test_split_styles_document():
    # the IR->IR pass runs split_styles over every node's text, so a
    # multi-word span becomes per-word (wrapping won't tear it)
    doc = split_styles_document(style_document(parse("**one two three**\n")))
    assert doc.blocks[0] == Paragraph([Text('⦃bold⦙one⦄ ⦃bold⦙two⦄ ⦃bold⦙three⦄')])
    # an unstyled document is refused: this stage needs a StyledDocument
    with raises(TypeError):
        split_styles_document(parse("one two three\n"))
    # code is verbatim: never word-split, so its whole line stays one span
    code = split_styles_document(style_document(parse("```\na b c\n```\n")))
    assert code.blocks[0] == CodeBlock('⦃codeblock⦙a b c⦄', '')

def test_code_block_styled_per_line():
    # each code line is its own `code` span, with its own indentation
    # INSIDE the span; only the block-render indent stays plain
    doc = style_document(parse("```\n    x = 1\ny = 2\n```\n"))
    assert doc.blocks[0] == CodeBlock('⦃codeblock⦙    x = 1⦄\n⦃codeblock⦙y = 2⦄', '')
    out = markup("```\n    x = 1\ny = 2\n```\n", 0)
    assert out == "    ⦃codeblock⦙    x = 1⦄\n    ⦃codeblock⦙y = 2⦄"
    # stripped back to plain, the block-render indent survives, the markup doesn't
    assert render("```\nx = 1\n```\n") == "    x = 1"

def test_stylesheet_delimiters_in_markdown_are_safe():
    # a docstring containing the StyleSheet delimiters must not crash the
    # styling pipeline -- style_document quotes them in the IR text
    assert style_document(parse("x⦃y\n")).blocks[0] == Paragraph([Text('x⦃⦃y')])
    # and they round-trip back to themselves through the whole pipeline
    src = "use ⦃a⦙b⦄ here and **x ⦄ y**\n"
    painted = render(src, 0)               # never raises on the literal delimiter
    assert '⦃a⦙b⦄' in painted

def test_styled_text_passes_through_style_document():
    # a StyledText carries already-valid markup structurally: style_document
    # does NOT escape it (unlike Text), and the enclosing role still wraps it
    entry = DefinitionEntry(
        Term([StyledText('⦃argument⦙<HOST>⦄')]),
        [Definition([Paragraph([Text('the host to ⦃connect⦄ to')])])])
    styled = style_document(MarkdownDocument([DefinitionList([entry])]))
    dl = styled.blocks[0]
    # the term wears `term` with the pre-styled `argument` nested, unescaped
    assert dl.entries[0].term.children[0] == Text('⦃term⦙⦃argument⦙<HOST>⦄⦄')
    assert strip_styles(dl.entries[0].term.children[0].text) == '<HOST>'
    # ordinary Text alongside it still escapes its literal delimiters
    prose = dl.entries[0].definitions[0].blocks[0].children[0]
    assert prose == Text('the host to ⦃⦃connect⦃⦄ to')
    # the layout node is ('term', …) whose stripped text is <HOST>
    layout = layout_document(split_styles_document(styled))
    terms = [t for t in layout if isinstance(t, tuple) and t and t[0] == 'term']
    assert terms == [('term', '⦃term⦙⦃argument⦙<HOST>⦄⦄')]
    # malformed markup is refused at the source, naming the node
    with raises(ValueError):
        style_document(MarkdownDocument([Paragraph([StyledText('⦃argument⦙oops')])]))

def test_styled_text_degrades_in_render_document():
    # render_document can't honor style roles; like Raw, it degrades a
    # StyledText to its stripped text (never dropping it silently)
    doc = MarkdownDocument([DefinitionList([DefinitionEntry(
        Term([StyledText('⦃argument⦙<HOST>⦄')]),
        [Definition([Paragraph([Text('the host to use')])])])])])
    for fmt in ('gfm', 'commonmark', 'troff'):
        out = render_document(doc, fmt)
        assert '<HOST>' in out, (fmt, out)
        assert '⦃term⦙' not in out and '⦃argument⦙' not in out, (fmt, out)

def test_styled_link_carries_url():
    # the URL rides as a leading field; the label is the text
    para = style_document(parse("see [the docs](http://x/y) now\n")).blocks[0]
    assert para == Paragraph([Text('see ⦃link⦙http://x/y⦙the docs⦄ now')])
    markup = para.children[0].text
    # the default sheet shows the label only; plain text is the label
    assert markdown_defaults.render(markup) == 'see the docs now'
    assert strip_styles(markup) == 'see the docs now'
    # a sheet that wants the URL can show it
    shown = markdown_defaults | StyleSheet({'link': ('URL', 'T', 'T <URL>')})
    assert shown.render(markup) == 'see the docs <http://x/y> now'
    # an autolink: the URL is both the destination and the label
    auto = style_document(parse("<https://x>\n")).blocks[0]
    assert auto == Paragraph([Text('⦃link⦙https://x⦙https://x⦄')])
    # a delimiter in a URL is quoted, so it can't break the markup
    odd = style_document(parse("[t](<a⦙b>)\n")).blocks[0]
    assert strip_styles(odd.children[0].text) == 't'
    assert shown.render(odd.children[0].text) == 't <a⦙b>'
    # through the whole terminal path -- split, wrap, join -- the URL
    # survives and is shown once for the link, not once per word
    doc = split_styles_document(style_document(parse("read [the style guide](u) now\n")))
    wrapped = wrap_words(layout_document(doc), margin=79, raw=strip_styles)
    assert shown.render(join_styles(wrapped)) == 'read the style guide <u> now'

def test_list_indent_follows_the_bullet_width():
    # the continuation pad is sized when painted, so a sheet may give the
    # bullet any width and the item text still lines up under itself --
    # and, measured through that same sheet, nothing wraps past the margin
    md = "- alpha beta gamma delta epsilon zeta\n"
    assert render(md, 18) == ("• alpha beta gamma\n"
                              "  delta epsilon\n"
                              "  zeta")
    wide = markdown_defaults | StyleSheet({'bullet': ('-->',)})
    out = render(md, 18, sheet=wide)
    assert out == ("--> alpha beta\n"
                   "    gamma delta\n"
                   "    epsilon zeta")
    assert all(len(line) <= 18 for line in out.split('\n'))
    # ordered lists are unchanged: markers right-align, text lines up
    assert render("9. a b c d e f\n10. g\n", 12) == (" 9. a b c d\n"
                                                   "    e f\n"
                                                   "10. g")

def test_heading_rule_is_indented_inside_a_block():
    # a heading's rule is drawn by wrap_words (the heading{n}_rule hook),
    # so it lands at the heading's own indent -- a definition's detail
    # column, a list item, a block quote's bar -- never flush left
    underlined = markdown_defaults | StyleSheet({'heading3_rule': ('-',)})
    md = ("--text <S>\n"
          ":   Some text.\n"
          "\n"
          "    ### Arguments\n"
          "\n"
          "    <S>\n"
          "    :   The string.\n")
    assert render(md, 50, sheet=underlined) == (
        "--text <S>  Some text.\n"
        "\n"
        "            Arguments\n"
        "            ---------\n"
        "\n"
        "            <S>  The string.")
    # a heading as the FIRST block of a compact entry shares the term's
    # line; its rule still lands at the detail column, not under the term
    assert render("term\n:   ### Head\n\n    body\n", 50, sheet=underlined) == (
        "term  Head\n"
        "      ----\n"
        "\n"
        "      body")
    # a list item: rule under the item text, at the continuation indent
    assert render("- item\n\n  ### Inside\n", 50, sheet=underlined) == (
        "• item\n"
        "\n"
        "  Inside\n"
        "  ------")
    # a block quote: the rule wears the bar, which the old renderer-column
    # inference could not do
    assert render("> ### Quoted\n>\n> after\n", 40, sheet=underlined) == (
        "│ Quoted\n"
        "│ ------\n"
        "\n"
        "│ after")

def test_heading_rule_can_be_painted_without_mis_sizing():
    # a rule glyph is a BARE character wrapped by the layout in a
    # per-level paint role (heading{n}_rule_ink) -- like the bullet in
    # marker -- so a sheet paints the rule via that role and the glyph
    # alone sets the width.  Painting the glyph itself would make it
    # measure its escape bytes and tile to the wrong width.
    from big.stylesheet import ansi_16_color_palette, transforms
    sheet = (markdown_defaults | StyleSheet(transforms) | ansi_16_color_palette
             | StyleSheet({'heading1_rule': ('=',),
                           'heading1_rule_ink': ('T', '⦃blue⦙T⦄')}))
    glyphs = glyphs_from_stylesheet(sheet)
    # the wrapped glyph measures its VISIBLE width (1), not its paint
    assert len(strip_styles(glyphs('⦃heading1_rule_ink⦙⦃heading1_rule⦄⦄'))) == 1
    layout = layout_document(split_styles_document(style_document(parse("# Boxed heading\n"))))
    out = sheet.render(join_styles(wrap_words(layout, margin=40,
                       raw=lambda w: strip_styles(glyphs(w))), span_linebreaks=True))
    import re
    plain = re.sub('\x1b' + r'\[[0-9;]*m', '', out)
    # the rule is as wide as the heading (15), not ceil(15 / escape-width)
    assert plain == "Boxed heading\n=============", repr(plain)
    assert '\x1b[34m' in out                    # and it's actually painted blue

def test_wrapped_heading_gets_one_rule():
    # D08: a heading that WRAPS -- in a list, so a fill pad sits between
    # its lines -- gets ONE rule under the whole block, not one per line
    sheet = markdown_defaults | StyleSheet({'heading2_rule': ('-',)})
    out = render("- ## A heading with many words that wraps", 24, sheet=sheet)
    assert out == ("• A heading with many\n"
                   "  words that wraps\n"
                   "  -------------------")
    rules = [line for line in out.split('\n') if set(line.strip()) == {'-'}]
    assert len(rules) == 1, out
    # H1 over-and-under (Appeal's style): both rules, both sized to the
    # heading's widest line, both at the block's indent
    over_under = markdown_defaults | StyleSheet(
        {'heading1_rule': ('=',), 'heading1_rule_next': ('=',)})
    assert render("- # Boxed heading here that wraps", 20, sheet=over_under) == (
        "  ==================\n"
        "• Boxed heading here\n"
        "  that wraps\n"
        "  ==================")

def test_styled_wrapping_measures_visible_width():
    # a styled run wraps at the same columns as the unstyled text,
    # because width is measured past the markup
    assert render("The **quick** brown fox jumps\n", 15) == \
           render("The quick brown fox jumps\n", 15)

def test_glyphs_wear_their_roles():
    # a heading is its styled text with a rule hook on each side; by
    # default H1/H2 get a setext underline sized to the text, H3-H6 none
    assert render("# Hi\n\n- a\n") == "Hi\n==\n\n• a"
    assert render("### Sub\n\n- a\n") == "Sub\n\n• a"       # H3: bare
    out = markup("# Hi\n\n- a\n")
    assert '⦃heading1⦙Hi⦄' in out                      # heading text wears heading1
    assert '⦃heading1_rule⦄' in out                    # the below-rule hook
    assert '⦃marker⦙⦃bullet⦄⦄' in out                 # bullet under marker

def test_structural_roles():
    # code blocks wear `codeblock` (distinct from inline `code`)
    cb = style_document(parse("```\nx\n```\n")).blocks[0]
    assert cb == CodeBlock('⦃codeblock⦙x⦄', '')
    assert style_document(parse("`x`\n")).blocks[0] == Paragraph([Text('⦃code⦙x⦄')])
    # a definition-list term wears `term`
    term = style_document(parse("word\n: a def\n")).blocks[0].entries[0].term
    assert term == Term([Text('⦃term⦙word⦄')])
    # the quote bar and the thematic break wear their roles, as glyphs
    assert markup("> hi\n", 20) == "⦃blockquote⦙⦃quote_bar⦄⦄hi"
    assert markup("a\n\n---\n", 6) == "a\n\n" + "⦃rule⦙" + "⦃thematic_break⦄" * 6 + "⦄"
    # and they resolve to their characters (the break is a fixed 5-char rule)
    assert render("> hi\n", 20) == "│ hi"
    assert render("a\n\n---\n", 6) == "a\n\n──────"

def test_render_troff():
    # inline: strong -> \fB, inline code -> \fB, hyphens -> \- for man
    out = render_document(parse("# NAME\n\nfoozle - a **tool** with `--flag`\n"), 'troff')
    assert '.SH NAME' in out
    assert '\\fBtool\\fP' in out
    assert '\\fB\\-\\-flag\\fP' in out
    # definition lists become .TP tagged paragraphs (ideal for options)
    t = render_document(parse("-v, --verbose\n: Print more.\n"), 'troff')
    assert '.TP' in t and '\\fB\\-v, \\-\\-verbose\\fP' in t and 'Print more.' in t
    # blocks map to man macros
    assert '.SS' in render_document(parse("## Sub\n"), 'troff')
    assert '.IP \\(bu' in render_document(parse("- a\n"), 'troff')
    assert '.EX' in render_document(parse("```\ncode\n```\n"), 'troff')
    assert '.RS 4' in render_document(parse("> quoted\n"), 'troff')

def test_render_document_gfm():
    gfm = lambda md: render_document(parse(md), 'gfm')
    # ordinary CommonMark round-trips
    assert gfm("# Hi\n\nsome **b** and `c`\n") == "# Hi\n\nsome **b** and `c`"
    assert gfm("- a\n- b\n") == "- a\n- b"
    # GFM keeps strikethrough and native alerts
    assert gfm("~~gone~~\n") == "~~gone~~"
    assert gfm("> [!WARNING]\n> Careful.\n") == "> [!WARNING]\n> Careful."
    # definition lists become inline-HTML <dl>, blank-line trick so the
    # term and details are still parsed as Markdown
    assert gfm("term\n: A **bold** detail.\n") == (
        "<dl>\n<dt>\n\nterm\n\n</dt>\n<dd>\n\nA **bold** detail.\n\n</dd>\n</dl>")

def test_render_document_commonmark():
    cm = lambda md: render_document(parse(md), 'commonmark')
    # strikethrough has no CommonMark form -> drops to plain text
    assert cm("~~gone~~\n") == "gone"
    # an alert degrades to a blockquote with a bold title
    assert cm("> [!WARNING]\n> Careful.\n") == "> **Warning**\n> Careful."
    # a definition list degrades to a bold term + blockquoted details
    assert cm("term\n: The detail.\n") == "**term**  \n> The detail."

def test_render_document_troff_definition_bodies():
    # a body's further blocks sit inside a bare .RS/.RE, at the tag's
    # body column: a .PP alone would fall back to the tag's column, and
    # .TP inside .TP doesn't nest on its own.  A nested definition list's
    # tags indent under the outer body; the paragraph after it stays there
    md = "outer\n: intro\n\n    inner\n    : detail\n\n    after\n"
    assert render_document(parse(md), 'troff') == (
        '.TP\n\\fBouter\\fP\nintro\n'
        '.RS\n.TP\n\\fBinner\\fP\ndetail\n.PP\nafter\n.RE')
    # a heading inside a body can't be a .SS (that ends the entry wherever
    # it sits): it degrades to a bold paragraph, still under the entry
    md = "term\n: Intro.\n\n    ### Sub\n\n    After.\n"
    assert render_document(parse(md), 'troff') == (
        '.TP\n\\fBterm\\fP\nIntro.\n'
        '.RS\n.PP\n\\fBSub\\fP\n.PP\nAfter.\n.RE')
    # the same for a list item's further blocks
    assert render_document(parse("- a\n\n  b\n"), 'troff') == (
        '.IP \\(bu 3\na\n.RS\n.PP\nb\n.RE')
    # a top-level heading is still a section
    assert '.SS Sub' in render_document(parse("## Sub\n"), 'troff')

def test_render_document_unknown_format():
    with raises(ValueError):
        render_document(parse("hi\n"), 'html')

def test_alerts():
    # a [!KIND] first line turns a block quote into an Alert
    assert parse("> [!NOTE]\n> Useful info.\n").blocks[0] == \
        Alert('note', [Paragraph([Text('Useful info.')])])
    # STRICT: the kind must be UPPERCASE, and unknown kinds stay quotes
    assert isinstance(parse("> [!Note]\n> x\n").blocks[0], BlockQuote)
    assert isinstance(parse("> [!warning]\n> hi\n").blocks[0], BlockQuote)
    assert isinstance(parse("> [!FOO]\n> hi\n").blocks[0], BlockQuote)
    # styled: a heading_<kind> title (emoji + kind) + a per-line <kind> bar,
    # the bar and emoji as glyph roles
    out = markup("> [!TIP]\n> do this\n", 40)
    assert out == ("⦃tip⦙⦃quote_bar⦄⦄⦃heading_tip⦙⦃tip_emoji⦄ ⦃tip_title⦄⦄\n"
                   "⦃tip⦙⦃quote_bar⦄⦄do this")
    # resolved to plain
    assert render("> [!TIP]\n> do this\n", 40) == "│ 💡 Tip\n│ do this"
    # ascii glyphs, if that's what you resolve with
    ascii = markdown_defaults | markdown_ascii_glyphs
    assert render("> [!TIP]\n> do this\n", 40, sheet=ascii) == "| (*) Tip\n| do this"

def test_alert_role_defaults():
    sheet = markdown_defaults | StyleSheet({
        'blue': ('T', '[b]T[/b]'), 'red': ('T', '[r]T[/r]'),
        'heading2': ('T', '[h]T[/h]')})
    assert sheet.render('⦃note⦙x⦄') == '[b]x[/b]'              # note -> blue
    # title = heading2 over the kind's color (caution -> red)
    assert sheet.render('⦃heading_caution⦙x⦄') == '[h][r]x[/r][/h]'

def test_markdown_defaults_stylesheet():
    # codeblock inherits code; blockquote/rule/term/unknown -> plain
    sheet = markdown_defaults | StyleSheet({'code': ('T', '[c]T[/c]')})
    assert sheet.render('⦃codeblock⦙x⦄') == '[c]x[/c]'
    assert sheet.render('⦃blockquote⦙│ ⦄') == '│ '
    assert sheet.render('⦃rule⦙───⦄') == '───'
    assert sheet.render('⦃term⦙word⦄') == 'word'

def test_style_pipeline_two_layer_theme():
    # low level: formatting -> backend tokens (stand-ins for ANSI)
    low = StyleSheet({
        'bold':         ('T', '[b]T[/b]'),
        'underline':    ('T', '[u]T[/u]'),
        'header_color': ('T', '[c]T[/c]'),
    })
    # high level: concept -> formatting, resolved recursively
    theme = StyleSheet({
        'heading1': ('T', '⦃bold⦙⦃header_color⦙T⦄⦄'),
        'heading1_rule_ink': ('T', 'T'),             # the rule hook's paint role
        'marker':   ('T', '⦃header_color⦙T⦄'),
        'code':     ('T', 'T'),
        'link':     ('URL', 'T', '⦃underline⦙T⦄'),   # the URL is luggage
    })
    sheet = low | theme
    md = "# Hi\n\nsome **bold** and `c` and [x](u)\n\n- a\n"

    # the whole pipeline: parse -> style -> split -> layout -> wrap -> join
    # -> resolve glyphs -> paint (the theme doesn't define glyph roles, so
    # resolve them to characters first)
    def paint(with_sheet):
        return with_sheet.render(unicode_glyphs(_pipeline(md, 0)))

    out = paint(sheet)
    assert '[b][c]Hi[/c][/b]' in out                 # heading: bold + color
    assert '[c]•[/c] a' in out                        # marker: color
    assert 'some [b]bold[/b] and c and [u]x[/u]' in out
    # the payoff: overwrite header_color ONCE, every heading AND marker
    # recolors -- because the high-level roles compose onto it
    recolored = paint(sheet | StyleSheet({'header_color': ('T', '[C]T[/C]')}))
    assert '[b][C]Hi[/C][/b]' in recolored and '[C]•[/C] a' in recolored

def test_glyph_swappers():
    # unicode_glyphs / ascii_glyphs swap glyph markup for characters, and
    # leave everything else (including other markup) alone
    assert unicode_glyphs('⦃bullet⦄ ⦃note_emoji⦄ ⦃quote_bar⦄') == '• ℹ️ │ '
    assert ascii_glyphs('⦃bullet⦄ ⦃note_emoji⦄ ⦃quote_bar⦄') == '* (i) | '
    assert unicode_glyphs('⦃bold⦙x⦄') == '⦃bold⦙x⦄'
    # they're just glyphs_from_stylesheet applied to the two stock sheets
    assert unicode_glyphs('⦃bullet⦄') == markdown_defaults.render('⦃bullet⦄')
    assert ascii_glyphs('⦃bullet⦄') == markdown_ascii_glyphs.render('⦃bullet⦄')
    # alert titles are roles too, so they can be localized
    assert unicode_glyphs('⦃tip_title⦄') == 'Tip'
    # glyphs_from_stylesheet derives a swapper from any sheet
    swap = glyphs_from_stylesheet(markdown_ascii_glyphs)
    assert swap('⦃thematic_break⦄') == '-'


def run_tests(run=None):
    (run or bigtestlib.run)(name="big.markdown", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
