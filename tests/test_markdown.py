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

from big.test import raises

import big.markdown
from big.markdown import *
from big.template import StyleSheet, plain_stylesheet, join_styles


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

def test_all_exports_resolve():
    for name in big.markdown.__all__:
        assert hasattr(big.markdown, name), name


#
# Block parser
#

def test_heading():
    assert parse("# Title\n") == Document([Heading(1, [Text('Title')])])
    assert parse("###### Six\n") == Document([Heading(6, [Text('Six')])])
    # a closing run of hashes is stripped
    assert parse("## Two ##\n") == Document([Heading(2, [Text('Two')])])

def test_setext_headings():
    assert parse("Big Title\n=========\n") == Document([Heading(1, [Text('Big Title')])])
    assert parse("Sub Heading\n---\n") == Document([Heading(2, [Text('Sub Heading')])])
    # the underline applies to the whole preceding paragraph
    assert parse("one\ntwo\n===\n") == Document([Heading(1, [Text('one\ntwo')])])

def test_dashes_context_disambiguates():
    # under a paragraph line -> setext H2
    assert parse("text\n---\n") == Document([Heading(2, [Text('text')])])
    # after a blank line -> thematic break
    assert parse("p\n\n---\n") == Document([Paragraph([Text('p')]), ThematicBreak()])
    # spaced (not a contiguous run) -> thematic break, not setext
    assert parse("text\n- - -\n") == Document([Paragraph([Text('text')]), ThematicBreak()])

def test_heading_requires_space_and_at_most_six():
    # no space after the hashes -> not a heading
    assert parse("#nope\n") == Document([Paragraph([Text('#nope')])])
    # seven hashes -> not a heading
    assert parse("####### seven\n") == Document([Paragraph([Text('####### seven')])])

def test_paragraph_keeps_its_soft_breaks():
    got = parse("Hello world\nsecond line\n")
    assert got == Document([Paragraph([Text('Hello world\nsecond line')])])

def test_thematic_break():
    assert parse("---\n") == Document([ThematicBreak()])
    assert parse("***\n") == Document([ThematicBreak()])
    assert parse("___\n") == Document([ThematicBreak()])

def test_fenced_code():
    got = parse("```python\nx = 1\n  y = 2\n```\n")
    assert got == Document([CodeBlock('x = 1\n  y = 2', 'python')])
    # tilde fence, no info string
    assert parse("~~~\ncode\n~~~\n") == Document([CodeBlock('code', '')])

def test_indented_code():
    assert parse("    exec foo -v\n") == Document([CodeBlock('exec foo -v', '')])

def test_tabs_expand_to_four_column_stops():
    # a single leading tab reaches column 4 -> indented code block
    assert parse("\tcode\n") == Document([CodeBlock('code', '')])
    # after a one-char marker, a tab reaches column 4, so the item's
    # content column is 4 and a tab-indented continuation folds in
    assert parse("-\tfoo\n\tbar\n") == Document([
        BulletList([ListItem([Paragraph([Text('foo\nbar')])])], True)])

def test_indented_code_does_not_interrupt_paragraph():
    got = parse("ordinary paragraph\n    indented continuation\n")
    assert got == Document([
        Paragraph([Text('ordinary paragraph\nindented continuation')]),
    ])

def test_bullet_list_tight():
    got = parse("- one\n- two\n")
    assert got == Document([BulletList([
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
    assert render_terminal(parse("1) a\n2) b\n")) == "1) a\n2) b"
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
    assert got == Document([
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
    assert got == Document([
        BlockQuote([
            Paragraph([Text('quoted first line\nlazy second line')]),
        ]),
    ])

def test_definition_list_single():
    got = parse("verbose\n: Controls verbosity.\n")
    assert got == Document([DefinitionList([
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
    assert got == Document([
        Paragraph([Text('ordinary paragraph\n2. still ordinary prose')]),
    ])

def test_empty_input():
    assert parse("") == Document([])
    assert parse("\n\n\n") == Document([])


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
    assert render_terminal(parse("a  \nb\n"), width=40) == "a\nb"       # hard: forced
    assert render_terminal(parse("a\nb\n"), width=40) == "a b"          # soft: reflowed

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
    assert d == Document([Paragraph([
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
    assert parse("-\n") == Document([
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
    assert render_terminal(parse("one two three four five\n"), width=13) == "one two three\nfour five"

def test_render_paragraphs_separated():
    assert render_terminal(parse("a\n\nb\n"), width=20) == "a\n\nb"

def test_render_bullet_list():
    assert render_terminal(parse("- a\n- b\n"), width=20) == "• a\n• b"

def test_render_ordered_from_start():
    assert render_terminal(parse("3. c\n4. d\n"), width=20) == "3. c\n4. d"

def test_render_ordered_right_aligned():
    # markers right-align within the list so the periods share a
    # column and the text shares the next-but-one column
    assert render_terminal(parse("9. nine\n10. ten\n"), width=20) == " 9. nine\n10. ten"

def test_render_nested_tight():
    assert render_terminal(parse("- outer\n  - inner\n"), width=20) == "• outer\n  • inner"

def test_render_loose_has_blanks():
    assert render_terminal(parse("- a\n\n- b\n"), width=20) == "• a\n\n• b"

def test_render_code_block_indented():
    assert render_terminal(parse("```\nx = 1\n```\n"), width=20) == "    x = 1"

def test_render_blockquote_prefixed():
    assert render_terminal(parse("> hi there\n"), width=20) == "│ hi there"

def test_render_thematic_break():
    assert render_terminal(parse("---\n"), width=5) == "─────"

def test_render_definition_list():
    assert render_terminal(parse("term\n: def here\n"), width=20) == "term\n    def here"

def test_render_hanging_wrap():
    # continuation of a wrapped item hangs under the item's text
    out = render_terminal(parse("- word word word word\n"), width=12)
    assert out == "• word word\n  word word"


#
# Styling pipeline: parse -> style -> render_terminal -> StyleSheet.render
#

def test_style_bakes_role_markup():
    # style() wraps inline runs and headings in their roles
    assert style_document(parse("# Hi\n")).blocks[0] == Heading(1, [Text('⦃heading1⦙Hi⦄')])
    para = style_document(parse("a **b** *c* `d` ~~e~~ [f](u)\n")).blocks[0]
    assert para == Paragraph([Text(
        'a ⦃bold⦙b⦄ ⦃italic⦙c⦄ ⦃code⦙d⦄ ⦃strikethrough⦙e⦄ ⦃link⦙f⦄')])
    # plain_stylesheet strips it all back to the plain text
    assert plain_stylesheet.render(para.children[0].text) == 'a b c d e f'

def test_split_styles_document():
    # the IR->IR pass runs split_styles over every node's text, so a
    # multi-word span becomes per-word (render_terminal won't tear it)
    doc = split_styles_document(style_document(parse("**one two three**\n")))
    assert doc.blocks[0] == Paragraph([Text('⦃bold⦙one⦄ ⦃bold⦙two⦄ ⦃bold⦙three⦄')])
    # it's a no-op on an unstyled document
    plain = parse("one two three\n")
    assert split_styles_document(plain) == plain
    # code is verbatim: never word-split, so its whole line stays one span
    code = split_styles_document(style_document(parse("```\na b c\n```\n")))
    assert code.blocks[0] == CodeBlock('⦃code⦙a b c⦄', '')

def test_code_block_styled_per_line():
    # each code line is its own `code` span, with its own indentation
    # INSIDE the span; only the block-render indent stays plain
    doc = style_document(parse("```\n    x = 1\ny = 2\n```\n"))
    assert doc.blocks[0] == CodeBlock('⦃code⦙    x = 1⦄\n⦃code⦙y = 2⦄', '')
    out = render_terminal(split_styles_document(doc), width=0)
    assert out == "    ⦃code⦙    x = 1⦄\n    ⦃code⦙y = 2⦄"
    # unstyled code stays plain (no markup)
    assert render_terminal(parse("```\nx = 1\n```\n")) == "    x = 1"

def test_stylesheet_delimiters_in_markdown_are_safe():
    # a docstring containing the StyleSheet delimiters must not crash the
    # styling pipeline -- style_document quotes them in the IR text
    assert style_document(parse("x⦃y\n")).blocks[0] == Paragraph([Text('x⦃⦃y')])
    # and they round-trip back to themselves through the whole pipeline
    src = "use ⦃a⦙b⦄ here and **x ⦄ y**\n"
    doc = split_styles_document(style_document(parse(src)))
    painted = plain_stylesheet.render(join_styles(render_terminal(doc, width=0)))
    assert '⦃a⦙b⦄' in painted
    # the unstyled path handles a literal delimiter without raising, too
    assert painted == render_terminal(parse(src), width=0)

def test_styled_wrapping_measures_visible_width():
    # a styled run wraps at the same columns as the unstyled text,
    # because width is measured past the markup
    src = "The quick brown fox jumps\n"
    doc = split_styles_document(style_document(parse(src)))
    styled = render_terminal(doc, width=15)
    assert plain_stylesheet.render(styled) == render_terminal(parse(src), width=15)

def test_render_terminal_glyphs_styled_only_when_document_is():
    # unstyled IR -> no markup anywhere (markers/rules stay plain)
    assert render_terminal(parse("# Hi\n\n- a\n")) == "==\nHi\n==\n\n• a"
    # styled IR -> heading rule and list marker wear their roles
    out = render_terminal(split_styles_document(style_document(parse("# Hi\n\n- a\n"))))
    assert '⦃heading1⦙==⦄' in out and '⦃marker⦙•⦄' in out

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
        'marker':   ('T', '⦃header_color⦙T⦄'),
        'code':     ('T', 'T'),
        'link':     ('T', '⦃underline⦙T⦄'),
    })
    sheet = low | theme
    md = "# Hi\n\nsome **bold** and `c` and [x](u)\n\n- a\n"

    # the whole pipeline: parse -> style -> split -> render -> join -> paint
    def paint(with_sheet):
        doc = split_styles_document(style_document(parse(md)))
        return with_sheet.render(join_styles(render_terminal(doc, width=0)))

    out = paint(sheet)
    assert '[b][c]Hi[/c][/b]' in out                 # heading: bold + color
    assert '[b][c]==[/c][/b]' in out                 # rule matches 'Hi' width
    assert '[c]•[/c] a' in out                        # marker: color
    assert 'some [b]bold[/b] and c and [u]x[/u]' in out
    # the payoff: overwrite header_color ONCE, every heading AND marker
    # recolors -- because the high-level roles compose onto it
    recolored = paint(sheet | StyleSheet({'header_color': ('T', '[C]T[/C]')}))
    assert '[b][C]Hi[/C][/b]' in recolored and '[C]•[/C] a' in recolored


def run_tests(run=None):
    (run or bigtestlib.run)(name="big.markdown", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
