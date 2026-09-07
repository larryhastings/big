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

import bigtestlib
bigtestlib.preload_local_big()

from big.test import raises, raises_regex, subtest

import big.all as big
import unittest





# ---------------------------------------------------------------
# StyleSheet (the inline character-style markup, 2026-07)
# ---------------------------------------------------------------

from big.stylesheet import (StyleSheet, style as fmt, plain,
                          plain_stylesheet, style_delimiters)


def test_stylesheet_tag_authoring():
    assert fmt('bold', 'x') == '\u2983bold\u2999x\u2984'
    assert fmt('b2', 'x') == '\u2983b2\u2999x\u2984'
    assert plain('x') == '\u2983_plain\u2999x\u2984'
    # composition: fields may contain well-formed markup
    assert fmt('bold', fmt('red', 'x'))
    # junk refused noisily
    with raises(ValueError):
        fmt('2bold', 'x')               # leading digit
    with raises(ValueError):
        fmt('bo ld', 'x')               # not alnum
    with raises(ValueError):
        fmt('bold', '\u2983oops')      # malformed markup in field
    with raises(TypeError):
        fmt('bold', 3)


def test_stylesheet_paint_and_nesting():
    ansi = StyleSheet({'bold': ('T', '\x1b[1mT\x1b[0m'),
                    'red':  ('T', '\x1b[31mT\x1b[0m')})
    # per-run painting: nested spans never damage enclosing paint
    out = ansi.render(fmt('bold', 'a ' + fmt('red', 'b') + ' c'))
    assert out == ('\x1b[1ma \x1b[0m'
                   '\x1b[1m\x1b[31mb\x1b[0m\x1b[0m'
                   '\x1b[1m c\x1b[0m')


def test_stylesheet_plain_island():
    ansi = StyleSheet({'bold': ('T', '<B>T</B>')})
    out = ansi.render(fmt('bold', 'b ' + plain('c') + ' d'))
    # the island is boring: no enclosing paint, then paint resumes
    assert out == '<B>b </B>c<B> d</B>'
    # nested paint inside the island strips too
    out = ansi.render(fmt('bold', plain(fmt('bold', 'x'))))
    assert out == 'x'


def test_stylesheet_opaque_rewrite():
    p = StyleSheet({'link': ('URL', 'TEXT', "<a href='URL'>TEXT</a>")})
    out = p.render(fmt('link', 'http://x', 'y'))
    assert out == "<a href='http://x'>y</a>"
    # single-pass substitution: a URL containing the OTHER token's
    # spelling must not be re-substituted
    out = p.render(fmt('link', 'http://TEXT.example', 'y'))
    assert out == "<a href='http://TEXT.example'>y</a>"
    # arg order in the replacement is free
    p2 = StyleSheet({'swap': ('A', 'B', 'B then A')})
    assert p2.render(fmt('swap', 'x', 'y')) == 'y then x'
    # repeated token: still one arg, but opaque (not undoable)
    p3 = StyleSheet({'twice': ('X', 'X and X')})
    assert p3.render(fmt('twice', 'q')) == 'q and q'

def test_best_palette():
    import io
    # a non-tty file -> can't colorize -> plain text, no escapes at all
    assert big.best_palette(file=io.StringIO()) is big.plain_stylesheet
    # best_palette(file=...) matches what can_colorize/ansi_color_depth prescribe
    for f in (io.StringIO(),):
        if not big.can_colorize(file=f):
            expected = big.plain_stylesheet
        else:
            expected = {'truecolor': big.ansi_truecolor_palette,
                        '256color': big.ansi_256_color_palette,
                        '16color': big.ansi_16_color_palette}.get(big.ansi_color_depth(),
                                                     big.ansi_truecolor_palette)
        assert big.best_palette(file=f) is expected
    # it's always plain_stylesheet or one of the three colored maps
    assert any(big.best_palette() is p for p in
               (big.plain_stylesheet, big.ansi_truecolor_palette, big.ansi_256_color_palette, big.ansi_16_color_palette))

def test_plain_palette():
    # plain_palette renders everything plain, but enumerates all 33 roles
    # explicitly -- no _default (so it composes with sheets that forbid one)
    assert '_default' not in big.plain_palette
    assert len(big.plain_palette) == 33
    assert big.plain_palette.render('⦃bold⦙⦃red⦙x⦄⦄') == 'x'
    # unlike uncolored_palette, even the attributes are no-ops
    assert big.plain_palette.render('⦃bold⦙x⦄') == 'x'
    assert big.uncolored_palette.render('⦃bold⦙x⦄') != 'x'
    # unlike plain_stylesheet, an unknown role raises (no _default catch-all)
    with raises(KeyError):
        big.plain_palette.render('⦃nonesuch⦙x⦄')

def test_stylesheet_verbatim_role_is_cheap():
    # a do-nothing role ('T', 'T') paints nothing: classified verbatim,
    # it renders its text with no added output (and no empty paint pair)
    sheet = StyleSheet({'plain': ('T', 'T'), 'bold': ('T', '[b]T[/b]')})
    assert sheet['plain'].verbatim is True
    assert sheet['bold'].verbatim is False
    assert sheet.render('⦃plain⦙hello⦄') == 'hello'
    # nested verbatim roles collapse to the text; painting roles still fire
    assert sheet.render('⦃plain⦙⦃plain⦙x⦄⦄') == 'x'
    assert sheet.render('⦃plain⦙⦃bold⦙x⦄⦄') == '[b]x[/b]'
    # a verbatim role inside a painting one doesn't disturb the paint
    assert sheet.render('⦃bold⦙⦃plain⦙x⦄⦄') == '[b]x[/b]'


def test_stylesheet_default_and_plain_stylesheet():
    assert plain_stylesheet.render(fmt('bold', 'x')) == 'x'
    # unknown multi-field format: _default gets the LAST field
    assert plain_stylesheet.render(fmt('link', 'u', 'desc')) == 'desc'
    assert plain_stylesheet.render(plain('x')) == 'x'
    # a debugging _default
    dbg = StyleSheet({'_default': ('T', '<<T>>')})
    assert dbg.render(fmt('zork', 'x')) == '<<x>>'
    # no _default: unknown name raises KeyError
    with raises(KeyError):
        StyleSheet({}).render(fmt('zork', 'x'))
    # visible width is just len of the plain rendering
    assert len(plain_stylesheet.render(fmt('bold', 'abc'))) == 3


def test_stylesheet_conceptual_layering():
    # a conceptual format's replacement uses OTHER formats:
    # merge the conceptual dict over a style dict
    conceptual = {'usage': ('T', fmt('bold', 'T'))}
    styles = {'bold': ('T', '<B>T</B>'), 'red': ('T', '<R>T</R>')}
    p = StyleSheet(styles) | conceptual
    assert isinstance(p, StyleSheet)
    assert p.render(fmt('usage', 'x')) == '<B>x</B>'
    # "usage in red, not bold" is one entry away
    p['usage'] = ('T', fmt('red', 'T'))
    assert p.render(fmt('usage', 'x')) == '<R>x</R>'

def test_split_styles():
    # every whitespace-delimited word gets its own balanced span, and
    # all whitespace (the double space included) is preserved verbatim
    assert big.split_styles('⦃bold⦙This is important.  Very important.⦄') == \
        '⦃bold⦙This⦄ ⦃bold⦙is⦄ ⦃bold⦙important.⦄  ⦃bold⦙Very⦄ ⦃bold⦙important.⦄'
    # a word with no internal whitespace stays whole (mixed styling ok)
    assert big.split_styles('a⦃bold⦙b⦄c') == 'a⦃bold⦙b⦄c'
    # nested spans re-wrap per word
    assert big.split_styles('⦃bold⦙⦃italic⦙x y⦄⦄') == '⦃bold⦙⦃italic⦙x⦄⦄ ⦃bold⦙⦃italic⦙y⦄⦄'
    # plain text is untouched, whitespace and all
    assert big.split_styles('no markup  here') == 'no markup  here'

def test_join_styles():
    # split_styles then join_styles round-trips within a line
    for x in ('⦃bold⦙This is important.  Very important.⦄',
              'a ⦃bold⦙b c⦄ d', '⦃bold⦙⦃italic⦙x y⦄⦄'):
        assert big.join_styles(big.split_styles(x)) == x, x
    # merges adjacent identical spans, absorbing the space
    assert big.join_styles('⦃bold⦙This⦄ ⦃bold⦙is⦄') == '⦃bold⦙This is⦄'
    # but NEVER across a newline (each line stays self-contained)
    assert big.join_styles('⦃bold⦙a⦄ ⦃bold⦙b⦄\n⦃bold⦙c⦄') == '⦃bold⦙a b⦄\n⦃bold⦙c⦄'
    # a non-whitespace gap, or a differing stack, is a boundary
    assert big.join_styles('⦃bold⦙a⦄, ⦃bold⦙b⦄') == '⦃bold⦙a⦄, ⦃bold⦙b⦄'
    assert big.join_styles('⦃bold⦙a⦄ ⦃italic⦙b⦄') == '⦃bold⦙a⦄ ⦃italic⦙b⦄'
    # span_linebreaks=True absorbs the newline too, so a span may straddle it
    assert big.join_styles('⦃bold⦙a⦄\n⦃bold⦙b⦄', span_linebreaks=True) == '⦃bold⦙a\nb⦄'
    # still bounded by a differing stack
    assert big.join_styles('⦃bold⦙a⦄\n⦃italic⦙b⦄', span_linebreaks=True) == '⦃bold⦙a⦄\n⦃italic⦙b⦄'
    # a BLANK line is always a boundary: a wrapped heading (one newline)
    # rejoins into one heading, two headings (a blank line) stay two --
    # so a per-block decoration like an underline fires twice, not once
    wrapped = '⦃heading2⦙First part⦄\n⦃heading2⦙of one⦄'
    assert big.join_styles(wrapped, span_linebreaks=True) == '⦃heading2⦙First part\nof one⦄'
    two = '⦃heading2⦙First⦄\n\n⦃heading2⦙Second⦄'
    assert big.join_styles(two, span_linebreaks=True) == two
    # factor out a shared outer span, nesting the differences inside a
    # single toggle (the gap joins the common prefix, not the top level)
    assert big.join_styles('⦃heading1⦙with⦄ ⦃heading1⦙⦃code⦙x⦄⦄ ⦃heading1⦙z⦄') == '⦃heading1⦙with ⦃code⦙x⦄ z⦄'
    # adjacent runs share the outer span but differ within
    assert big.join_styles('⦃a⦙⦃b⦙x⦄⦄⦃a⦙⦃c⦙y⦄⦄') == '⦃a⦙⦃b⦙x⦄⦃c⦙y⦄⦄'
    # a zero-argument span rides along as a character
    assert big.join_styles('⦃marker⦙⦃bullet⦄⦄ a') == '⦃marker⦙⦃bullet⦄⦄ a'

def test_escape_styles():
    # each delimiter is quoted by a leading open delimiter
    assert big.escape_styles('a⦃b⦙c⦄d') == 'a⦃⦃b⦃⦙c⦃⦄d'
    # parsing (rendering) turns the quoted forms back into literals
    assert big.plain_stylesheet.render(big.escape_styles('a⦃b⦙c⦄d')) == 'a⦃b⦙c⦄d'
    # style() accepts text once its delimiters are quoted
    assert big.style('bold', big.escape_styles('has ⦄ here')) == '⦃bold⦙has ⦃⦄ here⦄'
    # a quoted literal survives the split/join round-trip inside a span
    assert big.join_styles(big.split_styles('⦃bold⦙x ⦃⦄ y⦄')) == '⦃bold⦙x ⦃⦄ y⦄'

def test_ansi_low_level_maps():
    E = '\x1b'
    # each map defines the 4 attributes + the 29-color vocabulary
    hues = ['red', 'orange', 'amber', 'yellow', 'green', 'cyan', 'blue', 'purple', 'gray']
    vocab = {'bold', 'italic', 'underline', 'strikethrough', 'white', 'black'}
    for hue in hues:
        vocab |= {hue, 'light_' + hue, 'dark_' + hue}
    for sheet in (big.ansi_truecolor_palette, big.ansi_256_color_palette, big.ansi_16_color_palette, big.uncolored_palette):
        assert vocab <= set(sheet), sorted(vocab - set(sheet))

    r = lambda sheet, role: sheet.render('⦃' + role + '⦙x⦄')
    # attributes are identical across every map
    for sheet in (big.ansi_truecolor_palette, big.ansi_256_color_palette, big.ansi_16_color_palette, big.uncolored_palette):
        assert r(sheet, 'bold') == f'{E}[1mx{E}[22m'
        assert r(sheet, 'strikethrough') == f'{E}[9mx{E}[29m'
    # 24-bit uses the master hex verbatim (normal red is BA0000)
    assert r(big.ansi_truecolor_palette, 'red') == f'{E}[38;2;186;0;0mx{E}[39m'
    # 16-color: normal red -> 31, light red -> 91, orange leans bright-red
    assert r(big.ansi_16_color_palette, 'red') == f'{E}[31mx{E}[39m'
    assert r(big.ansi_16_color_palette, 'light_red') == f'{E}[91mx{E}[39m'
    assert r(big.ansi_16_color_palette, 'orange') == f'{E}[91mx{E}[39m'
    # 256: an indexed color, red nearest-matches to 124
    assert r(big.ansi_256_color_palette, 'red') == f'{E}[38;5;124mx{E}[39m'
    # uncolored keeps attributes but drops color
    assert r(big.uncolored_palette, 'red') == 'x'
    assert r(big.uncolored_palette, 'bold') == f'{E}[1mx{E}[22m'

def test_ansi_map_composes_under_a_theme():
    # a conceptual role resolves through the theme down to a real escape
    theme = StyleSheet({'heading': ('T', big.style('bold', big.style('light_gray', 'T')))})
    sheet = big.ansi_truecolor_palette | theme
    assert sheet.render(big.style('heading', 'Hi')) == \
        '\x1b[1m\x1b[38;2;179;179;179mHi\x1b[39m\x1b[22m'


def test_stylesheet_validation():
    with raises(ValueError):
        StyleSheet({'bold': ('T', 'no token here')})    # unused arg
    with raises(ValueError):
        StyleSheet({'_plain': ('T', 'T')})              # reserved
    with raises(ValueError):
        StyleSheet({'2fast': ('T', 'T')})               # bad name
    with raises(ValueError):
        StyleSheet({'bold': 'notatuple'})
    with raises(ValueError):
        StyleSheet({'_default': ('A', 'B', 'A B')})     # must take 1
    with raises(ValueError):
        StyleSheet({}, delimiters='ab')                 # need 3
    # arity mismatch at render
    p = StyleSheet({'link': ('U', 'D', 'U D')})
    with raises(ValueError):
        p.render(fmt('link', 'only-one'))
    # cycles refuse by name
    c = StyleSheet({'a': ('T', fmt('b', 'T')),
                 'b': ('T', fmt('a', 'T'))})
    with raises(ValueError):
        c.render(fmt('a', 'x'))


def test_stylesheet_parse_errors_have_positions():
    p = plain_stylesheet
    with raises(ValueError):
        p.render('\u2983bold\u2999oops')       # unclosed
    with raises(ValueError):
        p.render('stray \u2984 close')          # stray close
    with raises(ValueError):
        p.render('stray \u2999 sep')            # stray separator
    with raises(ValueError):
        p.render('\u2983\u2999x\u2984')       # empty name


def test_stylesheet_callable_escape_hatch():
    p = StyleSheet({'osc8': (lambda url, text:
                          f'\x1b]8;;{url}\x07{text}\x1b]8;;\x07')})
    # a 1-tuple of a callable?  no--callables are bare values
    p2 = StyleSheet()
    p2['shout'] = lambda text: text.upper()
    assert p2.render(fmt('shout', 'hi')) == 'HI'


def test_stylesheet_custom_delimiters():
    p = StyleSheet({'bold': ('T', '<B>T</B>')}, delimiters='{|}')
    assert p.render('{bold|x}') == '<B>x</B>'
    assert p.delimiters == '{|}'
    # merge keeps the left operand's delimiters and the class
    q = p | {'red': ('T', '<R>T</R>')}
    assert isinstance(q, StyleSheet) and q.delimiters == '{|}'
    assert q.render('{red|x}') == '<R>x</R>'




def test_stylesheet_escape():
    import html
    # literal source text passes through escape; replacement
    # strings are trusted backend syntax and never escaped
    p = StyleSheet({'b': ('T', '<b>T</b>')}, escape=html.escape)
    assert p.render('1 < 2 ' + fmt('b', 'a & b')) == \
        '1 &lt; 2 <b>a &amp; b</b>'
    # the Rich-markup backend: escape [ in real text
    rich = StyleSheet({'option': ('T', '[cyan]T[/cyan]')},
                   escape=lambda s: s.replace('[', '\\['))
    out = rich.render('usage: p ' + fmt('option', '-v')
                      + ' [file]')
    assert out == 'usage: p [cyan]-v[/cyan] \\[file]'
    # escape survives merge and copy
    q = rich | {'x': ('T', 'T')}
    assert q.escape is rich.escape
    assert rich.copy().escape is rich.escape
    with raises(ValueError):
        StyleSheet({}, escape='not callable')




def test_stylesheet_transforms_and_heading_hook():
    from big.stylesheet import transforms
    hdr = '\u2983headingstyle\u2999\u2983headingtext\u2999TEXT\u2984\u2984'
    p = StyleSheet(transforms)
    p.update({
        'heading':      ('TEXT', hdr),
        'headingtext':  ('TEXT', 'TEXT:'),
        'headingstyle': ('TEXT', '<H>TEXT</H>'),
    })
    assert p.render(fmt('heading', 'Arguments')) == '<H>Arguments:</H>'
    # the hook: one override reshapes every heading, paint untouched
    cool = p | {'headingtext': ('TEXT', fmt('lower', 'TEXT'))}
    assert cool.render(fmt('heading', 'Arguments')) == '<H>arguments</H>'
    shout = p | {'headingtext': ('TEXT', fmt('upper', 'TEXT') + ':')}
    # per-run painting: the transform output and the literal ':'
    # are separate runs, each painted--seamless on a terminal,
    # visible as two spans in tag-shaped backends
    assert shout.render(fmt('heading', 'Arguments')) == \
        '<H>ARGUMENTS</H><H>:</H>'
    # title uses big's gently_title
    t2 = StyleSheet(transforms)
    assert t2.render(fmt('title', 'the quick brown fox')) == \
        'The Quick Brown Fox'

def test_stylesheet_fill_and_strip_transforms():
    from big.stylesheet import transforms
    p = StyleSheet(transforms)
    # fill: repeat the pattern to the length of the model, clipped
    assert p.render(fmt('fill', '=', 'string')) == '======'        # len('string') == 6
    assert p.render(fmt('fill', '-=-', 'abcdefgh')) == '-=--=--='
    assert p.render(fmt('fill', '', 'abc')) == ''                   # empty pattern
    # strip / lstrip / rstrip
    assert p.render(fmt('strip', ' x y ')) == 'x y'
    assert p.render(fmt('lstrip', ' x y ')) == 'x y '
    assert p.render(fmt('rstrip', ' x y ')) == ' x y'
    # clip: cut text to the length of the model
    assert p.render(fmt('clip', 'abcde', 'abcdefgh')) == 'abcde'
    assert p.render(fmt('clip', 'abcde', 'xyz')) == 'xyz'          # shorter stays
    # fill then clip: a rule sized to the text, capped at the model width
    assert p.render('⦃clip⦙xxxxx⦙⦃fill⦙=⦙⦃strip⦙ heading ⦄⦄⦄') == '====='
    # center / ljust / rjust: pad text to the width of the model, space by default
    assert p.render(fmt('center', 'abcdefg', 'xyz')) == '  xyz  '
    assert p.render(fmt('ljust', 'abcdefg', 'xyz')) == 'xyz    '
    assert p.render(fmt('rjust', 'abcdefg', 'xyz')) == '    xyz'
    # an optional fill string rides in the middle, keeping text last
    assert p.render(fmt('center', 'abcdefg', '.', 'xyz')) == '..xyz..'
    assert p.render(fmt('ljust', 'abcdefg', '.', 'xyz')) == 'xyz....'
    assert p.render(fmt('rjust', 'abcdefg', '-', 'xyz')) == '----xyz'
    # the fill is a string, tiled and clipped to length like fill
    assert p.render(fmt('center', 'MMMMMMM', '-=-', 'xyz')) == '-=xyz-='
    assert p.render(fmt('ljust', 'MMMMMMMM', '-=-', 'xyz')) == 'xyz-=--='
    assert p.render(fmt('rjust', 'MMMMMMMM', '-=-', 'xyz')) == '-=--=xyz'
    # text at or over the model width comes back unchanged
    assert p.render(fmt('rjust', 'MM', '-=-', 'xyzzy')) == 'xyzzy'


def test_transform_fields_are_visible_text():
    # a transform's fields render with painting OFF: nested spans
    # resolve to their text and glyphs, but nothing pushes paint, so
    # str.upper never touches an escape code and fill never counts one
    from big.stylesheet import transforms
    p = StyleSheet(transforms) | StyleSheet({
        'bold': ('T', '\x1b[1mT\x1b[22m'),
        'heading2_rule': ('-',),
        'twice': ('X', 'X and X'),
    })
    assert p.render(fmt('upper', fmt('bold', 'abc'))) == 'ABC'
    # the transform's OUTPUT is painted by whatever encloses it
    assert p.render(fmt('bold', fmt('upper', 'abc'))) == '\x1b[1mABC\x1b[22m'
    # geometry measures visible text, not escape bytes
    assert p.render(fmt('fill', '=', fmt('bold', 'ab') + 'cd')) == '===='
    # glyphs and opaque rewrites still resolve inside a field
    assert p.render(fmt('fill', fmt('heading2_rule'), 'abcdef')) == '------'
    assert p.render(fmt('upper', fmt('twice', 'ab'))) == 'AB AND AB'
    # nested transforms compose
    assert p.render(fmt('fill', '=', fmt('upper', 'abc'))) == '==='


def test_split_join_carry_leading_fields():
    # only a span's LAST field is text; fields before it are luggage
    # that rides whole on every word, so a two-field span survives
    link = '⦃link⦙https://example.com⦙read more⦄'
    split = big.split_styles(link)
    assert split == '⦃link⦙https://example.com⦙read⦄ ⦃link⦙https://example.com⦙more⦄'
    assert big.join_styles(split) == link
    # and the split form RENDERS, word by word, through a two-field role
    sheet = StyleSheet({'link': ('URL', 'TEXT', 'TEXT <URL>')})
    assert sheet.render(split) == 'read <https://example.com> more <https://example.com>'
    # join merges only words whose luggage matches: two URLs stay two links
    two = '⦃link⦙u1⦙a⦄ ⦃link⦙u2⦙b⦄'
    assert big.join_styles(two) == two
    # luggage may itself be markup, and survives the round trip
    fancy = '⦃x⦙⦃bold⦙u⦄⦙a b⦄'
    assert big.join_styles(big.split_styles(fancy)) == fancy
    # a fill-of-spaces pad -- ⦃fill⦙ ⦙model⦄, the runtime bullet indent --
    # passes through join untouched, trailing space in the model included
    pad = '⦃fill⦙ ⦙⦃marker⦙⦃bullet⦄⦄ ⦄'
    assert big.join_styles(pad + 'alpha') == pad + 'alpha'


def run_tests(run=None):
    (run or bigtestlib.run)(name="big.stylesheet", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
