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

from big.test import raises, subtest

import big.all as big
from big import snip as big_snip
import ast
import contextlib
import io
import os.path
import re
import tempfile

from test_text import to_bytes, unchanged


haystack = (
    "before\n"
    "# --8<-- start alpha --8<--\n"
    "alpha line 1\n"
    "  alpha line 2, indented\n"
    "# --8<-- end alpha --8<--\n"
    "middle\n"
    "    # --8<-- start beta two words --8<--   \n"
    "    beta body\n"
    "    # --8<-- end beta two words --8<--\n"
    "after\n"
    )

def test_extract_snippets():
    def t(s, name, expected, **kwargs):
        for c in (unchanged, to_bytes):
            bytes_kwargs = {k: to_bytes(v) if c is to_bytes else v for k, v in kwargs.items()}
            assert big.extract_snippets(c(s), c(name), **bytes_kwargs) == c(expected)

    # you get the whole snippet, marker lines and all.
    t(haystack, 'alpha',
        "# --8<-- start alpha --8<--\n"
        "alpha line 1\n"
        "  alpha line 2, indented\n"
        "# --8<-- end alpha --8<--\n")
    # marker lines keep their indentation and trailing whitespace.
    t(haystack, 'beta two words',
        "    # --8<-- start beta two words --8<--   \n"
        "    beta body\n"
        "    # --8<-- end beta two words --8<--\n")
    # a snippet that ends the file without a trailing linebreak
    # extracts without one--end-of-line discipline is preserved.
    t("# --8<-- start x --8<--\nbody\n# --8<-- end x --8<--", 'x',
        "# --8<-- start x --8<--\nbody\n# --8<-- end x --8<--")
    # an empty snippet extracts as its two marker lines.
    t("# --8<-- start x --8<--\n# --8<-- end x --8<--\n", 'x',
        "# --8<-- start x --8<--\n# --8<-- end x --8<--\n")
    # a different comment leader.
    t("// --8<-- start x --8<--\nbody\n// --8<-- end x --8<--\n", 'x',
        "// --8<-- start x --8<--\nbody\n// --8<-- end x --8<--\n",
        comment='//')

def test_extract_snippets_requires():
    # extracting a snippet brings along everything it
    # requires, transitively, in SOURCE order, with no blank
    # lines between snippets.  loose lines and snippets
    # nothing requires stay behind.  this chain ping-pongs:
    # extract b; b requires d; d requires e and c; c requires
    # a; e requires f.  z is required by nothing.
    source = (
        "loose prologue line, never extracted\n"
        "# --8<-- start a --8<--\n"
        "body a\n"
        "# --8<-- end a --8<--\n"
        "loose line between snippets, never extracted\n"
        "# --8<-- start b --8<--\n"
        "# --8<-- requires d --8<--\n"
        "body b\n"
        "# --8<-- end b --8<--\n"
        "# --8<-- start z --8<--\n"
        "body z\n"
        "# --8<-- end z --8<--\n"
        "# --8<-- start c --8<--\n"
        "# --8<-- requires a --8<--\n"
        "body c\n"
        "# --8<-- end c --8<--\n"
        "# --8<-- start d --8<--\n"
        "# --8<-- requires e --8<--\n"
        "# --8<-- requires c --8<--\n"
        "body d\n"
        "# --8<-- end d --8<--\n"
        "# --8<-- start e --8<--\n"
        "# --8<-- requires f --8<--\n"
        "body e\n"
        "# --8<-- end e --8<--\n"
        "# --8<-- start f --8<--\n"
        "body f\n"
        "# --8<-- end f --8<--\n"
        "loose epilogue line, never extracted\n"
        )
    expected = (
        "# --8<-- start a --8<--\n"
        "body a\n"
        "# --8<-- end a --8<--\n"
        "# --8<-- start b --8<--\n"
        "# --8<-- requires d --8<--\n"
        "body b\n"
        "# --8<-- end b --8<--\n"
        "# --8<-- start c --8<--\n"
        "# --8<-- requires a --8<--\n"
        "body c\n"
        "# --8<-- end c --8<--\n"
        "# --8<-- start d --8<--\n"
        "# --8<-- requires e --8<--\n"
        "# --8<-- requires c --8<--\n"
        "body d\n"
        "# --8<-- end d --8<--\n"
        "# --8<-- start e --8<--\n"
        "# --8<-- requires f --8<--\n"
        "body e\n"
        "# --8<-- end e --8<--\n"
        "# --8<-- start f --8<--\n"
        "body f\n"
        "# --8<-- end f --8<--\n"
        )
    for c in (unchanged, to_bytes):
        assert big.extract_snippets(c(source), c('b')) == c(expected)

    # a diamond is NOT a cycle: b requires c and d, both of
    # which require e.  everything extracts, each snippet once.
    diamond = (
        "# --8<-- start b --8<--\n"
        "# --8<-- requires c --8<--\n"
        "# --8<-- requires d --8<--\n"
        "body b\n"
        "# --8<-- end b --8<--\n"
        "# --8<-- start c --8<--\n"
        "# --8<-- requires e --8<--\n"
        "body c\n"
        "# --8<-- end c --8<--\n"
        "# --8<-- start d --8<--\n"
        "# --8<-- requires e --8<--\n"
        "body d\n"
        "# --8<-- end d --8<--\n"
        "# --8<-- start e --8<--\n"
        "body e\n"
        "# --8<-- end e --8<--\n"
        )
    for c in (unchanged, to_bytes):
        assert big.extract_snippets(c(diamond), c('b')) == c(diamond)

    # ...but an actual requirements cycle raises, naming the loop.
    cyclic = (
        "# --8<-- start x --8<--\n"
        "# --8<-- requires y --8<--\n"
        "body x\n"
        "# --8<-- end x --8<--\n"
        "# --8<-- start y --8<--\n"
        "# --8<-- requires x --8<--\n"
        "body y\n"
        "# --8<-- end y --8<--\n"
        )
    for c in (unchanged, to_bytes):
        with raises(ValueError) as cm:
            big.extract_snippets(c(cyclic), c('x'))
        assert "cycle" in str(cm.exception)

    # a snippet requiring itself is the smallest cycle.
    selfish = (
        "# --8<-- start x --8<--\n"
        "# --8<-- requires x --8<--\n"
        "body x\n"
        "# --8<-- end x --8<--\n"
        )
    with raises(ValueError) as cm:
        big.extract_snippets(selfish, 'x')
    assert "cycle" in str(cm.exception)

def test_extract_snippets_multiple_names():
    # names are positional arguments.  the result is the union of
    # every name's closure, in SOURCE order--extract D (which
    # requires B) and C (which requires A and E) from a file
    # holding A B C D E, and you get A B C D E, regardless of
    # the order you asked in.
    source = (
        "# --8<-- start a --8<--\n"
        "body a\n"
        "# --8<-- end a --8<--\n"
        "# --8<-- start b --8<--\n"
        "body b\n"
        "# --8<-- end b --8<--\n"
        "# --8<-- start c --8<--\n"
        "# --8<-- requires a --8<--\n"
        "# --8<-- requires e --8<--\n"
        "body c\n"
        "# --8<-- end c --8<--\n"
        "# --8<-- start d --8<--\n"
        "# --8<-- requires b --8<--\n"
        "body d\n"
        "# --8<-- end d --8<--\n"
        "# --8<-- start e --8<--\n"
        "body e\n"
        "# --8<-- end e --8<--\n"
        )
    for names in (['d', 'c'], ['c', 'd'], ('d', 'c')):
        for c in (unchanged, to_bytes):
            got = big.extract_snippets(c(source), *c(list(names)))
            assert got == c(source)

    # ...and the result applies as one ordered patch.  fresh
    # snippets land with blank lines between them.
    spaced = source.replace("--8<--\n# --8<-- start",
                            "--8<--\n\n# --8<-- start")
    for c in (unchanged, to_bytes):
        patch = big.extract_snippets(c(source), *c(['d', 'c']))
        assert big.apply_snippets(c(''), patch) == c(spaced)

    # one name works like it always did.
    got = big.extract_snippets(source, 'b')
    assert got == ("# --8<-- start b --8<--\n"
        "body b\n"
        "# --8<-- end b --8<--\n")

    # no names is an error.
    with raises(ValueError):
        big.extract_snippets(source)

def test_error_positions():
    # the perky trick: parse plain str fast; if that raises,
    # reparse as big.string so the error says where.
    bad = "# --8<-- start x --8<--\nbody\n# --8<-- end x --8<-- key=v\n"
    with raises(ValueError) as cm:
        big.extract_snippets(bad, 'x')
    assert "line 3 column 1" in str(cm.exception)

    # a big.string input keeps its source name in the error.
    with raises(ValueError) as cm:
        big.extract_snippets(big.string(bad, source='warehouse.py'), 'x')
    assert "warehouse.py line 3" in str(cm.exception)

    # apply enriches too, whichever argument is malformed.
    good = "# --8<-- start x --8<--\nbody\n# --8<-- end x --8<--\n"
    with raises(ValueError) as cm:
        big.apply_snippets("file\n", bad)
    assert "line 3" in str(cm.exception)

    # bytes parse once; no positions, same error.
    with raises(ValueError) as cm:
        big.extract_snippets(bad.encode('ascii'), b'x')
    assert "line 3" not in str(cm.exception)
    assert "unexpected trailing text" in str(cm.exception)

    # a big.string parses with its positions on the FIRST
    # pass, and provenance survives into the result: extract
    # a big.string and you get a big.string that still knows
    # where it came from.
    got = big.extract_snippets(big.string(good, source='w.py'), 'x')
    assert got == good
    assert isinstance(got, big.string)
    assert 'w.py' in got.where

    # apply, from one big.string to another, likewise.
    merged = big.apply_snippets(big.string("file\n", source='dst.py'),
                                big.string(good, source='src.py'))
    assert merged == "file\n" + good
    assert isinstance(merged, big.string)

def test_sync_snippets():
    source = (
        "# --8<-- start big a --8<--\n"
        "# --8<-- requires big helper --8<--\n"
        "new a\n"
        "# --8<-- end big a --8<--\n"
        "# --8<-- start big helper --8<--\n"
        "new helper\n"
        "# --8<-- end big helper --8<--\n"
        "# --8<-- start big unborrowed --8<--\n"
        "never synced\n"
        "# --8<-- end big unborrowed --8<--\n"
        )
    destination = (
        "# --8<-- start appeal local --8<--\n"
        "appeal's own code, untouched\n"
        "# --8<-- end appeal local --8<--\n"
        "# --8<-- start big a --8<--\n"
        "old a\n"
        "# --8<-- end big a --8<--\n"
        )

    # the destination is its own manifest: 'big a' updates,
    # its newly-required helper installs, the unborrowed
    # snippet stays home, and the filter protects snippets
    # borrowed from elsewhere.
    for c in (unchanged, to_bytes):
        def approve(name, prefix=c('big ')):
            return name.startswith(prefix)
        got = big.sync_snippets(c(source), c(destination), approve)
        assert c("new a") in got
        assert c("new helper") in got
        assert c("appeal's own code, untouched") in got
        assert c("never synced") not in got
        # idempotent: syncing the result again changes nothing.
        assert big.sync_snippets(c(source), got, approve) == got

    # no filter: every destination snippet must exist in the
    # source--'appeal local' doesn't, and the error names it.
    with raises(ValueError) as cm:
        big.sync_snippets(source, destination)
    assert "appeal local" in str(cm.exception)

    # a destination with nothing to sync is an error.
    with raises(ValueError):
        big.sync_snippets(source, "no snippets here\n")
    with raises(ValueError):
        big.sync_snippets(source, destination, lambda name: False)

def test_coverage_odds_and_ends():
    # a directive prefix without a second "--8<--" isn't a
    # marker line at all; it's ignored.
    s = ("# --8<-- dangling prose, no second scissors\n"
         "# --8<-- start x --8<--\n"
         "body\n"
         "# --8<-- end x --8<--\n")
    got = big.extract_snippets(s, 'x')
    assert "dangling" not in got

    # a whitespace-only patch has nothing to apply.
    with raises(ValueError):
        big.apply_snippets("file\n", "\n")

    # apply's promote-and-retry, with a big.string patch in
    # the mix: s (plain str) is malformed, so the retry
    # promotes s and passes the already-big snippets through.
    patch = "# --8<-- start x --8<--\nbody\n# --8<-- end x --8<--\n"
    bad = "# --8<-- start y --8<--\nnever closed\n"
    with raises(ValueError) as cm:
        big.apply_snippets(bad, big.string(patch))
    assert "line 1" in str(cm.exception)

    # sync's promote-and-retry: a malformed plain-str
    # destination reports its position...
    source = patch
    with raises(ValueError) as cm:
        big.sync_snippets(source, bad)
    assert "line 1" in str(cm.exception)
    # ...and a malformed bytes destination raises plain.
    with raises(ValueError) as cm:
        big.sync_snippets(source.encode('ascii'), bad.encode('ascii'))
    assert "line 1" not in str(cm.exception)

def test_exotic_linebreak_terminators():
    # what's a linebreak?  whatever splitlines says it is--
    # the same answer big.text gives.  the parser used to
    # split lines with splitlines but recover the end-marker
    # terminator with rstrip('\r\n'), so a terminator from
    # splitlines' wider set (\v, \f, U+2028, ...) stayed
    # glued inside the body and trailing_linebreak came back
    # empty--quietly breaking the body/terminator split that
    # extract and apply's end-of-line discipline stand on.
    for linebreak in ('\v', '\f', '\u2028', '\u2029', '\x85'):
        with subtest(linebreak=linebreak):
            s = ("# --8<-- start a --8<--\n"
                 "alpha\n"
                 "# --8<-- end a --8<--" + linebreak +
                 "# --8<-- start b --8<--\n"
                 "beta\n"
                 "# --8<-- end b --8<--\n")
            entries = big_snip._split_snippets(s, '#')
            assert entries[0][3] == linebreak
            assert entries[0][2].endswith("end a --8<--")
            # the terminator travels as the snippet's
            # trailing linebreak, not inside its body.
            assert big.extract_snippets(s, 'a') == ("# --8<-- start a --8<--\n"
                "alpha\n"
                "# --8<-- end a --8<--" + linebreak)

    # bytes linebreaks are unchanged: bytes.splitlines only
    # splits on \r, \n, and \r\n.
    b = b"# --8<-- start a --8<--\nalpha\n# --8<-- end a --8<--\r\n"
    assert big_snip._split_snippets(b, b'#')[0][3] == b'\r\n'

def test_empty_snippet_names():
    # NAME is mandatory on start, end, and requires markers,
    # enforced by the parser.  (it used to be enforced only on
    # the names *requested* from extract_snippets--so an
    # anonymous snippet parsed fine but was unreachable:
    # extract couldn't ask for it, sync couldn't see it, and
    # apply reported it as "unexpected text".)  the error
    # says where.
    for marker in ("# --8<-- start --8<--\n",
                   "# --8<-- end --8<--\n",
                   "# --8<-- requires --8<--\n"):
        for c in (unchanged, to_bytes):
            with subtest(marker=marker, converter=c):
                with raises(ValueError) as cm:
                    big.extract_snippets(c(marker), c('x'))
                assert "has no name" in str(cm.exception)
                if c is unchanged:
                    # str input gets the perky-trick reparse:
                    # the error knows its position.
                    assert "line 1" in str(cm.exception)

    # a marker with no directive at all is still an
    # unrecognized directive, not a nameless one.
    with raises(ValueError) as cm:
        big.extract_snippets("# --8<--  --8<--\n", 'x')
    assert "unrecognized" in str(cm.exception)

def test_default_comment_introspection():
    # the comment default is a real, informative '#'--not an
    # opaque sentinel--visible in the signatures.
    import inspect
    for fn in (big.extract_snippets, big.apply_snippets):
        assert inspect.signature(fn).parameters['comment'].default == '#'

def test_extract_snippets_errors():
    start = "# --8<-- start x --8<--\n"
    end = "# --8<-- end x --8<--\n"

    def e(s, name, fragment):
        for c in (unchanged, to_bytes):
            with raises(ValueError) as cm:
                big.extract_snippets(c(s), c(name))
            assert fragment in str(cm.exception)

    e("no markers here\n", 'x', "not found")
    e(haystack, 'gamma', "not found")
    e(start + "body\n", 'x', "no end marker")
    e(end + start, 'x', "is not open")
    e(start + end + start + end, 'x', "is already defined")
    e(start + "# --8<-- start y --8<--\n" + end, 'x', "is nested inside")
    e(start + "# --8<-- end y --8<--\n" + end, 'x', "mismatched end marker")
    # requires is only legal inside a snippet...
    e("# --8<-- requires ghost --8<--\n" + start + end, 'x', "used outside a snippet")
    # ...and start/end/requires are the only directives.
    e("# --8<-- frobnicate z --8<--\n" + start + end, 'x', "unrecognized snippet directive")
    e(start + "# --8<-- requires ghost --8<--\n" + end, 'x', "not found (required by snippet")

    # the space after a marker line's second "--8<--" is
    # reserved for future extension: anything there raises,
    # even when the malformed marker belongs to some OTHER
    # snippet.  (trailing whitespace is fine--see haystack.)
    polluted = (
        "# --8<-- start alpha --8<-- key=value\n"
        "alpha body\n"
        "# --8<-- end alpha --8<--\n"
        "# --8<-- start beta --8<--\n"
        "beta body\n"
        "# --8<-- end beta --8<--\n"
        )
    e(polluted, 'beta', "unexpected trailing text")

    # name must match the type of s, be nonempty, and can't
    # contain the scissors token.
    with raises(TypeError):
        big.extract_snippets(haystack, b'alpha')
    with raises(TypeError):
        big.extract_snippets(to_bytes(haystack), 'alpha')
    for c in (unchanged, to_bytes):
        with raises(ValueError):
            big.extract_snippets(c(haystack), c(''))
        with raises(ValueError):
            big.extract_snippets(c(haystack), c('evil --8<-- name'))
        with raises(TypeError):
            big.extract_snippets(c(haystack), c('alpha'), comment=c(''))

def test_apply_snippets():
    def t(s, snippets, expected):
        for c in (unchanged, to_bytes):
            assert big.apply_snippets(c(s), c(snippets)) == c(expected)

    patch = (
        "# --8<-- start x --8<--\n"
        "new body\n"
        "# --8<-- end x --8<--\n"
        )

    # a snippet s already carries is overwritten in place;
    # everything around it is preserved.
    t("prologue\n"
      "# --8<-- start x --8<--\n"
      "old body\n"
      "# --8<-- end x --8<--\n"
      "epilogue\n",
      patch,
      "prologue\n"
      "# --8<-- start x --8<--\n"
      "new body\n"
      "# --8<-- end x --8<--\n"
      "epilogue\n")

    # a snippet s lacks is appended at the end...
    t("just a file\n", patch,
      "just a file\n" + patch)
    # ...growing a linebreak first if the file lacked one...
    t("just a file", patch,
      "just a file\n" + patch)
    # ...and an empty file is fine too.
    t("", patch, patch)

    # end-of-line discipline: a patch without a trailing
    # linebreak appends without one.
    t("just a file\n", patch.rstrip("\n"),
      "just a file\n" + patch.rstrip("\n"))

    # applying a snippet's own extraction is a no-op...
    for c in (unchanged, to_bytes):
        s = c(haystack)
        assert big.apply_snippets(s, big.extract_snippets(s, c('alpha'))) == s

    # ...even when the file doesn't end with a linebreak.
    eof = "# --8<-- start x --8<--\nbody\n# --8<-- end x --8<--"
    assert big.apply_snippets(eof, big.extract_snippets(eof, 'x')) == eof

def test_apply_snippets_placement():
    # a missing snippet is inserted immediately before the
    # snippet that follows it in the patch, wherever s keeps
    # that one.
    patch = (
        "# --8<-- start helper --8<--\n"
        "helper body\n"
        "# --8<-- end helper --8<--\n"
        "# --8<-- start main --8<--\n"
        "main body\n"
        "# --8<-- end main --8<--\n"
        )
    s = (
        "top\n"
        "# --8<-- start main --8<--\n"
        "old main\n"
        "# --8<-- end main --8<--\n"
        "bottom\n"
        )
    # a freshly inserted snippet gets a blank line between
    # itself and the snippet it's inserted in front of.
    expected = (
        "top\n"
        "# --8<-- start helper --8<--\n"
        "helper body\n"
        "# --8<-- end helper --8<--\n"
        "\n"
        "# --8<-- start main --8<--\n"
        "main body\n"
        "# --8<-- end main --8<--\n"
        "bottom\n"
        )
    for c in (unchanged, to_bytes):
        assert big.apply_snippets(c(s), c(patch)) == c(expected)

    # s may keep its snippets in any order; apply overwrites
    # in place and only inserts what's missing.
    s = (
        "# --8<-- start main --8<--\n"
        "old main\n"
        "# --8<-- end main --8<--\n"
        "# --8<-- start helper --8<--\n"
        "old helper\n"
        "# --8<-- end helper --8<--\n"
        )
    expected = (
        "# --8<-- start main --8<--\n"
        "main body\n"
        "# --8<-- end main --8<--\n"
        "# --8<-- start helper --8<--\n"
        "helper body\n"
        "# --8<-- end helper --8<--\n"
        )
    for c in (unchanged, to_bytes):
        assert big.apply_snippets(c(s), c(patch)) == c(expected)

def test_apply_snippets_errors():
    patch = "# --8<-- start x --8<--\nbody\n# --8<-- end x --8<--\n"
    # snippets must contain only snippets.
    for c in (unchanged, to_bytes):
        with raises(ValueError):
            big.apply_snippets(c("file\n"), c("junk before\n" + patch))
        with raises(ValueError):
            big.apply_snippets(c("file\n"), c("no snippets at all\n"))
    # snippets must match the type of s.
    with raises(TypeError):
        big.apply_snippets("file\n", to_bytes(patch))
    with raises(TypeError):
        big.apply_snippets(to_bytes("file\n"), patch)



class SnipEnv:
    "A fresh snip working directory with source/destination files."
    source_text = (
        b"# --8<-- start alpha --8<--\n"
        b"new alpha body\n"
        b"# --8<-- end alpha --8<--\n"
        b"# --8<-- start beta --8<--\n"
        b"new beta body\n"
        b"# --8<-- end beta --8<--\n"
        )
    destination_text = (
        b"top\n"
        b"# --8<-- start alpha --8<--\n"
        b"old alpha body\n"
        b"# --8<-- end alpha --8<--\n"
        b"# --8<-- start beta --8<--\n"
        b"old beta body\n"
        b"# --8<-- end beta --8<--\n"
        b"bottom\n"
        )
    requires_source = (
        b"# --8<-- start helper --8<--\n"
        b"new helper body\n"
        b"# --8<-- end helper --8<--\n"
        b"# --8<-- start main --8<--\n"
        b"# --8<-- requires helper --8<--\n"
        b"new main body\n"
        b"# --8<-- end main --8<--\n"
        )
    requires_destination = (
        b"# --8<-- start helper --8<--\n"
        b"old helper body\n"
        b"# --8<-- end helper --8<--\n"
        b"# --8<-- start main --8<--\n"
        b"old main body\n"
        b"# --8<-- end main --8<--\n"
        )

    def __init__(self, directory):
        self.directory = directory
        self.source_path = os.path.join(directory, "source.py")
        self.destination_path = os.path.join(directory, "destination.py")
        with open(self.source_path, 'wb') as f:
            f.write(self.source_text)
        with open(self.destination_path, 'wb') as f:
            f.write(self.destination_text)

    def snip(self, *args):
        # runs big.snip's main in-process,
        # returning (exit_code, stdout as bytes, stderr as str).
        stdout = io.TextIOWrapper(io.BytesIO(), encoding='utf-8')
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = big_snip.main(list(args))
        stdout.flush()
        return (exit_code, stdout.buffer.getvalue(), stderr.getvalue())

    def read_destination(self):
        with open(self.destination_path, 'rb') as f:
            return f.read()

    def read_destination_at(self, path):
        with open(path, 'rb') as f:
            return f.read()

    requires_source = (
        b"# --8<-- start helper --8<--\n"
        b"new helper body\n"
        b"# --8<-- end helper --8<--\n"
        b"# --8<-- start main --8<--\n"
        b"# --8<-- requires helper --8<--\n"
        b"new main body\n"
        b"# --8<-- end main --8<--\n"
        )

    requires_destination = (
        b"# --8<-- start helper --8<--\n"
        b"old helper body\n"
        b"# --8<-- end helper --8<--\n"
        b"# --8<-- start main --8<--\n"
        b"old main body\n"
        b"# --8<-- end main --8<--\n"
        )

    def write_requires_fixture(self):
        source_path = os.path.join(self.directory, "requires_source.py")
        destination_path = os.path.join(self.directory, "requires_destination.py")
        with open(source_path, 'wb') as f:
            f.write(self.requires_source)
        with open(destination_path, 'wb') as f:
            f.write(self.requires_destination)
        return source_path, destination_path

@contextlib.contextmanager
def setup():
    with tempfile.TemporaryDirectory() as directory:
        yield SnipEnv(directory)

def test_list():
    with setup() as env:
        exit_code, stdout, stderr = env.snip('list', env.source_path)
        assert exit_code == 0
        assert stdout == b"alpha\nbeta\n"
        assert stderr == ""

def test_extract():
    with setup() as env:
        exit_code, stdout, stderr = env.snip('extract', env.source_path, 'alpha')
        assert exit_code == 0
        assert stdout == (b"# --8<-- start alpha --8<--\n"
            b"new alpha body\n"
            b"# --8<-- end alpha --8<--\n")
        assert stderr == ""

        # extract accepts several names: one patch, source order.
        exit_code, stdout, stderr = env.snip('extract', env.source_path, 'beta', 'alpha')
        assert exit_code == 0
        assert stdout == env.source_text

def test_apply():
    with setup() as env:
        exit_code, stdout, stderr = env.snip('apply',
            env.source_path, env.destination_path, 'alpha', 'beta')
        assert exit_code == 0
        assert "updated" in stdout.decode('utf-8')
        expected = env.destination_text.replace(b"old", b"new")
        assert env.read_destination() == expected

        # a second update finds nothing to do and doesn't rewrite the file.
        exit_code, stdout, stderr = env.snip('apply',
            env.source_path, env.destination_path, 'alpha', 'beta')
        assert exit_code == 0
        assert "unchanged" in stdout.decode('utf-8')
        assert env.read_destination() == expected

def test_apply_one_of_two():
    with setup() as env:
        exit_code, stdout, stderr = env.snip('apply',
            env.source_path, env.destination_path, 'beta')
        assert exit_code == 0
        assert b"old alpha body" in env.read_destination()
        assert b"new beta body" in env.read_destination()

def test_sync_verb():
    with setup() as env:
        # sync: the destination is its own manifest.
        mixed_source = (
            b"# --8<-- start big alpha --8<--\n"
            b"new alpha\n"
            b"# --8<-- end big alpha --8<--\n"
            )
        mixed_destination = (
            b"# --8<-- start appeal mine --8<--\n"
            b"local\n"
            b"# --8<-- end appeal mine --8<--\n"
            b"# --8<-- start big alpha --8<--\n"
            b"old alpha\n"
            b"# --8<-- end big alpha --8<--\n"
            )
        source_path = os.path.join(env.directory, "mixed_source.py")
        destination_path = os.path.join(env.directory, "mixed_destination.py")
        with open(source_path, 'wb') as f:
            f.write(mixed_source)
        with open(destination_path, 'wb') as f:
            f.write(mixed_destination)

        # with a prefix, only that project's snippets sync.
        exit_code, stdout, stderr = env.snip('sync', source_path, destination_path, 'big ')
        assert exit_code == 0, stderr
        assert "'big alpha' synced" in stdout.decode('utf-8')
        with open(destination_path, 'rb') as f:
            result = f.read()
        assert b"new alpha" in result
        assert b"local" in result

        # a second sync is a no-op.
        exit_code, stdout, stderr = env.snip('sync', source_path, destination_path, 'big ')
        assert exit_code == 0
        assert "unchanged" in stdout.decode('utf-8')

        # without a prefix, every destination snippet must exist
        # in the source; 'appeal mine' doesn't.
        exit_code, stdout, stderr = env.snip('sync', source_path, destination_path)
        assert exit_code == 1
        assert "appeal mine" in stdout.decode('utf-8')
        assert stderr == ""

        # prefixes that match nothing: nothing to sync.
        exit_code, stdout, stderr = env.snip('sync', source_path, destination_path, 'nonesuch ')
        assert exit_code == 1
        assert "no snippets to sync" in stdout.decode('utf-8')

        # too few arguments is a usage error.
        exit_code, stdout, stderr = env.snip('sync', source_path)
        assert exit_code == 2

def test_cli_error_positions():
    with setup() as env:
        # tool errors say where: file, line, and column.
        polluted_path = os.path.join(env.directory, "where.py")
        with open(polluted_path, 'wb') as f:
            f.write(
                b"fine\n"
                b"# --8<-- start x --8<--\n"
                b"body\n"
                b"# --8<-- end x --8<-- junk\n")
        for args in (
            ('list', polluted_path),
            ('extract', polluted_path, 'x'),
            ('apply', polluted_path, env.destination_path, 'x'),
            ):
            with subtest(args=args):
                exit_code, stdout, stderr = env.snip(*args)
                assert exit_code == 1
                text = stdout.decode('utf-8')
                assert "line 4 column 1" in text
                assert "where.py" in text
                assert stderr == ""

def test_runtime_errors():
    with setup() as env:
        # a missing file or a missing snippet: exit code 1, an
        # error message--and the usage text too, since
        # every input this tool touches came from the command
        # line, so every error is plausibly a command-line
        # mistake (a mistyped path, a mistyped name).
        missing_file = os.path.join(env.directory, "no.such.file")
        for args in (
            ('extract', missing_file, 'alpha'),
            ('extract', env.source_path, 'gamma'),
            ('list', missing_file),
            ('apply', env.source_path, env.destination_path, 'gamma'),
            ('sync', missing_file, env.destination_path),
            ):
            with subtest(args=args):
                exit_code, stdout, stderr = env.snip(*args)
                assert exit_code == 1
                text = stdout.decode('utf-8')
                assert "error:" in text
                assert "usage:" in text
                assert stderr == ""

def test_usage_errors():
    with setup() as env:
        # each of these is a command-line mistake: exit code 2,
        # an error message and the usage text.  nothing ever
        # goes to stderr--Larry doesn't like it.
        for args in (
            (),
            ('frobnicate', env.source_path),
            ('list',),
            ('list', env.source_path, 'extra'),
            ('extract', env.source_path),
            ('apply', env.source_path, env.destination_path),
            ):
            with subtest(args=args):
                exit_code, stdout, stderr = env.snip(*args)
                assert exit_code == 2
                text = stdout.decode('utf-8')
                assert "error:" in text
                assert "usage:" in text
                assert stderr == ""

def test_requires_directive_apply():
    with setup() as env:
        # updating a snippet also updates the snippets it requires.
        source_path, destination_path = env.write_requires_fixture()
        exit_code, stdout, stderr = env.snip('apply', source_path, destination_path, 'main')
        assert exit_code == 0, stderr
        with open(destination_path, 'rb') as f:
            result = f.read()
        assert b"new helper body" in result
        assert b"new main body" in result
        # the directive line itself travels with the body.
        assert b"# --8<-- requires helper --8<--\nnew main body" in result

def test_requires_directive_extract():
    with setup() as env:
        # copying a snippet prints its requirements along with it,
        # in SOURCE FILE ORDER.  here helper precedes main in the
        # source, so it precedes main in the output.
        source_path, destination_path = env.write_requires_fixture()
        exit_code, stdout, stderr = env.snip('extract', source_path, 'main')
        assert exit_code == 0, stderr
        assert stdout == env.requires_source

def test_requires_directive_extract_preserves_source_order():
    with setup() as env:
        # ...and here the required snippet FOLLOWS its requirer in
        # the source, so it follows it in the output too.  the
        # source file's definition order is proven to work; the
        # tool must not invent its own.
        content = (
            b"# --8<-- start main --8<--\n"
            b"# --8<-- requires helper --8<--\n"
            b"main body\n"
            b"# --8<-- end main --8<--\n"
            b"# --8<-- start helper --8<--\n"
            b"helper body\n"
            b"# --8<-- end helper --8<--\n")
        source_path = os.path.join(env.directory, "follows_source.py")
        with open(source_path, 'wb') as f:
            f.write(content)
        exit_code, stdout, stderr = env.snip('extract', source_path, 'main')
        assert exit_code == 0, stderr
        assert stdout == content

def test_requires_directive_ping_pong_order():
    with setup() as env:
        # a requirement chain that ping-pongs across the file:
        # copy b; b requires d; d requires e and c; c requires a;
        # e requires f.  all six get clipped, and the output is
        # in source file order: a b c d e f.  the file also
        # contains a snippet nothing requires (z) and loose lines
        # between the snippets; none of that gets copied.
        source_path = os.path.join(env.directory, "ping_pong_source.py")
        with open(source_path, 'wb') as f:
            f.write(
                b"loose prologue line, never copied\n"
                b"# --8<-- start a --8<--\n"
                b"body a\n"
                b"# --8<-- end a --8<--\n"
                b"loose line between snippets, never copied\n"
                b"# --8<-- start b --8<--\n"
                b"# --8<-- requires d --8<--\n"
                b"body b\n"
                b"# --8<-- end b --8<--\n"
                b"# --8<-- start z --8<--\n"
                b"body z: nothing requires this snippet\n"
                b"# --8<-- end z --8<--\n"
                b"# --8<-- start c --8<--\n"
                b"# --8<-- requires a --8<--\n"
                b"body c\n"
                b"# --8<-- end c --8<--\n"
                b"# --8<-- start d --8<--\n"
                b"# --8<-- requires e --8<--\n"
                b"# --8<-- requires c --8<--\n"
                b"body d\n"
                b"# --8<-- end d --8<--\n"
                b"# --8<-- start e --8<--\n"
                b"# --8<-- requires f --8<--\n"
                b"body e\n"
                b"# --8<-- end e --8<--\n"
                b"# --8<-- start f --8<--\n"
                b"body f\n"
                b"# --8<-- end f --8<--\n"
                b"loose epilogue line, never copied\n")
        exit_code, stdout, stderr = env.snip('extract', source_path, 'b')
        assert exit_code == 0, stderr
        assert stdout == (b"# --8<-- start a --8<--\n"
            b"body a\n"
            b"# --8<-- end a --8<--\n"
            b"# --8<-- start b --8<--\n"
            b"# --8<-- requires d --8<--\n"
            b"body b\n"
            b"# --8<-- end b --8<--\n"
            b"# --8<-- start c --8<--\n"
            b"# --8<-- requires a --8<--\n"
            b"body c\n"
            b"# --8<-- end c --8<--\n"
            b"# --8<-- start d --8<--\n"
            b"# --8<-- requires e --8<--\n"
            b"# --8<-- requires c --8<--\n"
            b"body d\n"
            b"# --8<-- end d --8<--\n"
            b"# --8<-- start e --8<--\n"
            b"# --8<-- requires f --8<--\n"
            b"body e\n"
            b"# --8<-- end e --8<--\n"
            b"# --8<-- start f --8<--\n"
            b"body f\n"
            b"# --8<-- end f --8<--\n")

def test_requires_directive_transitive_and_cyclic():
    with setup() as env:
        # requirements resolve transitively...
        source = (
            b"# --8<-- start a --8<--\n"
            b"# --8<-- requires b --8<--\n"
            b"new a\n"
            b"# --8<-- end a --8<--\n"
            b"# --8<-- start b --8<--\n"
            b"# --8<-- requires c --8<--\n"
            b"new b\n"
            b"# --8<-- end b --8<--\n"
            b"# --8<-- start c --8<--\n"
            b"new c\n"
            b"# --8<-- end c --8<--\n"
            )
        destination = source.replace(b"new", b"old")
        source_path = os.path.join(env.directory, "transitive_source.py")
        destination_path = os.path.join(env.directory, "transitive_destination.py")
        with open(source_path, 'wb') as f:
            f.write(source)
        with open(destination_path, 'wb') as f:
            f.write(destination)
        exit_code, stdout, stderr = env.snip('apply', source_path, destination_path, 'a')
        assert exit_code == 0, stderr
        with open(destination_path, 'rb') as f:
            result = f.read()
        assert b"old" not in result

        # ...and a requirements cycle is an error, for every command
        # that resolves requirements.
        cyclic = source + b"# --8<-- start z --8<--\n# --8<-- requires z --8<--\nz\n# --8<-- end z --8<--\n"
        cyclic_path = os.path.join(env.directory, "cyclic_source.py")
        with open(cyclic_path, 'wb') as f:
            f.write(cyclic)
        for args in (
            ('extract', cyclic_path, 'z'),
            ('apply', cyclic_path, destination_path, 'z'),
            ('check', cyclic_path, destination_path, 'z'),
            ):
            with subtest(args=args):
                exit_code, stdout, stderr = env.snip(*args)
                assert exit_code == 1
                assert "cycle" in stdout.decode('utf-8')
                assert stderr == ""

def test_requires_directive_errors():
    with setup() as env:
        # requiring a snippet the source doesn't have:
        # a runtime error naming the snippet.
        source_path, destination_path = env.write_requires_fixture()

        bad_source_path = os.path.join(env.directory, "bad_source.py")
        with open(bad_source_path, 'wb') as f:
            f.write(
                b"# --8<-- start main --8<--\n"
                b"# --8<-- requires no such snippet --8<--\n"
                b"body\n"
                b"# --8<-- end main --8<--\n")
        exit_code, stdout, stderr = env.snip('apply', bad_source_path, destination_path, 'main')
        assert exit_code == 1
        assert "no such snippet" in stdout.decode('utf-8')
        assert stderr == ""

def test_apply_installs_missing_before_first_requirer():
    with setup() as env:
        # a destination that lacks a required snippet gets it
        # installed, markers and all, immediately before the
        # first snippet in the destination that requires it.
        source_path, destination_path = env.write_requires_fixture()
        bare_destination_path = os.path.join(env.directory, "bare_destination.py")
        with open(bare_destination_path, 'wb') as f:
            f.write(
                b"top of file, untouched\n"
                b"# --8<-- start main --8<--\n"
                b"old main body\n"
                b"# --8<-- end main --8<--\n"
                b"bottom of file, untouched\n")
        exit_code, stdout, stderr = env.snip('apply', source_path, bare_destination_path, 'main')
        assert exit_code == 0, stderr
        assert "applied" in stdout.decode('utf-8')
        with open(bare_destination_path, 'rb') as f:
            result = f.read()
        assert result == (b"top of file, untouched\n"
            b"# --8<-- start helper --8<--\n"
            b"new helper body\n"
            b"# --8<-- end helper --8<--\n"
            b"\n"
            b"# --8<-- start main --8<--\n"
            b"# --8<-- requires helper --8<--\n"
            b"new main body\n"
            b"# --8<-- end main --8<--\n"
            b"bottom of file, untouched\n")

def test_apply_installs_at_end_when_nothing_requires():
    with setup() as env:
        # bootstrapping into a file with no markers at all:
        # snippets append at the end, in source order.
        source_path, destination_path = env.write_requires_fixture()
        empty_destination_path = os.path.join(env.directory, "empty_destination.py")
        with open(empty_destination_path, 'wb') as f:
            f.write(b"just a file, no markers")   # note: no trailing linebreak
        exit_code, stdout, stderr = env.snip('apply', source_path, empty_destination_path, 'main')
        assert exit_code == 0, stderr
        with open(empty_destination_path, 'rb') as f:
            result = f.read()
        assert result == (b"just a file, no markers\n"
            b"# --8<-- start helper --8<--\n"
            b"new helper body\n"
            b"# --8<-- end helper --8<--\n"
            b"\n"
            b"# --8<-- start main --8<--\n"
            b"# --8<-- requires helper --8<--\n"
            b"new main body\n"
            b"# --8<-- end main --8<--\n")

def test_apply_obeys_destination_ordering():
    with setup() as env:
        # the destination may keep its snippets in any order it
        # likes; update replaces each in place and never reorders.
        source_path, destination_path = env.write_requires_fixture()
        reordered_destination_path = os.path.join(env.directory, "reordered_destination.py")
        with open(reordered_destination_path, 'wb') as f:
            f.write(
                b"# --8<-- start main --8<--\n"
                b"old main body\n"
                b"# --8<-- end main --8<--\n"
                b"# --8<-- start helper --8<--\n"
                b"old helper body\n"
                b"# --8<-- end helper --8<--\n")
        exit_code, stdout, stderr = env.snip('apply', source_path, reordered_destination_path, 'main')
        assert exit_code == 0, stderr
        with open(reordered_destination_path, 'rb') as f:
            result = f.read()
        assert result == (b"# --8<-- start main --8<--\n"
            b"# --8<-- requires helper --8<--\n"
            b"new main body\n"
            b"# --8<-- end main --8<--\n"
            b"# --8<-- start helper --8<--\n"
            b"new helper body\n"
            b"# --8<-- end helper --8<--\n")

def test_check():
    with setup() as env:
        # check reports what update would do, without writing.
        source_path, destination_path = env.write_requires_fixture()

        # out of sync: one line per problem, exit code 1,
        # destination untouched.
        exit_code, stdout, stderr = env.snip('check', source_path, destination_path, 'main')
        assert exit_code == 1
        text = stdout.decode('utf-8')
        assert "'helper' differs" in text
        assert "'main' differs" in text
        assert env.read_destination_at(destination_path) == env.requires_destination

        # a missing snippet reports as missing.
        bare_destination_path = os.path.join(env.directory, "bare_destination.py")
        with open(bare_destination_path, 'wb') as f:
            f.write(
                b"# --8<-- start main --8<--\n"
                b"old main body\n"
                b"# --8<-- end main --8<--\n")
        exit_code, stdout, stderr = env.snip('check', source_path, bare_destination_path, 'main')
        assert exit_code == 1
        text = stdout.decode('utf-8')
        assert "'helper' missing" in text
        assert "'main' differs" in text

        # in sync: silent, exit code 0.
        exit_code, stdout, stderr = env.snip('apply', source_path, destination_path, 'main')
        assert exit_code == 0
        exit_code, stdout, stderr = env.snip('check', source_path, destination_path, 'main')
        assert exit_code == 0
        assert stdout == b""

def test_comment_option():
    with setup() as env:
        # -c changes the comment leader the markers start with,
        # and may appear anywhere on the command line.
        c_source_path = os.path.join(env.directory, "c_source.c")
        with open(c_source_path, 'wb') as f:
            f.write(
                b"// --8<-- start helper --8<--\n"
                b"int helper;\n"
                b"// --8<-- end helper --8<--\n"
                b"// --8<-- start main --8<--\n"
                b"// --8<-- requires helper --8<--\n"
                b"int main;\n"
                b"// --8<-- end main --8<--\n")

        for args in (
            ('-c', '//', 'extract', c_source_path, 'main'),
            ('extract', '-c', '//', c_source_path, 'main'),
            ('extract', c_source_path, 'main', '-c', '//'),
            ):
            with subtest(args=args):
                exit_code, stdout, stderr = env.snip(*args)
                assert exit_code == 0, stderr
                assert stdout == (b"// --8<-- start helper --8<--\n"
                    b"int helper;\n"
                    b"// --8<-- end helper --8<--\n"
                    b"// --8<-- start main --8<--\n"
                    b"// --8<-- requires helper --8<--\n"
                    b"int main;\n"
                    b"// --8<-- end main --8<--\n")

        # bootstrap honors the comment string too.
        c_destination_path = os.path.join(env.directory, "c_destination.c")
        with open(c_destination_path, 'wb') as f:
            f.write(b"")
        exit_code, stdout, stderr = env.snip('apply', '-c', '//', c_source_path, c_destination_path, 'main')
        assert exit_code == 0, stderr
        with open(c_destination_path, 'rb') as f:
            result = f.read()
        assert result.startswith(b"// --8<-- start helper --8<--\n"), result

        # -c mistakes are command-line mistakes: exit code 2.
        for args in (
            ('extract', c_source_path, 'main', '-c'),
            ('-c', '//', '-c', '//', 'extract', c_source_path, 'main'),
            ):
            with subtest(args=args):
                exit_code, stdout, stderr = env.snip(*args)
                assert exit_code == 2




SNIPPET_PUBLISHING_MODULES = (big.text, big.itertools)


def _snippet_code(body):
    "The snippet's body with its marker/directive lines removed."
    return "\n".join(line for line in body.split("\n")
                     if not line.lstrip().startswith("# --8<--"))


def _is_import_only(body):
    "True if the snippet's body is nothing but import statements."
    code = _snippet_code(body).strip()
    if not code:
        return False
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    return all(isinstance(node, (ast.Import, ast.ImportFrom)) for node in tree.body)


def test_big_source_snippets_require_license():
    # Every snippet big publishes must carry big's license along
    # when it's borrowed.  The mechanism: each source file that
    # publishes snippets defines a "big license" snippet (wrapping
    # its own license text), and every other snippet in that file
    # declares "requires big license".  This test enforces the
    # convention on big's own source, so a future snippet can't
    # quietly ship without the license attached.  (Import-only
    # snippets--trivial import shims carrying no big code--are
    # exempt; the code snippets that require them carry the license
    # themselves, so borrowing real code always brings it along.)
    for module in SNIPPET_PUBLISHING_MODULES:
        with subtest(module=module.__name__):
            with open(module.__file__, encoding="utf-8") as f:
                source = f.read()
            entries = big_snip._split_snippets(source, "#")
            names = [name for name, requires, body, trailing in entries if name]
            assert "big license" in names, (
                f"{module.__name__} publishes snippets but has no 'big license' snippet")
            for name, requires, body, trailing in entries:
                if (not name) or (name == "big license") or _is_import_only(body):
                    continue
                assert "big license" in requires, (
                    f"snippet {name!r} in {module.__name__} doesn't 'requires big license'")


def test_big_source_snippets_carry_their_imports():
    # A borrowed snippet must be self-contained: if its code uses a
    # module, it must pull that module's import along via an import
    # snippet.  This extracts each publishable snippet with all its
    # requirements resolved and checks that every stdlib module the
    # extracted code references is actually imported within the
    # extraction--so a future snippet can't use a module without
    # wiring up the "requires" for its import.
    for module in SNIPPET_PUBLISHING_MODULES:
        with open(module.__file__, encoding="utf-8") as f:
            source = f.read()
        # plain "import foo" modules available at the file's top level
        file_imports = {m.group(1) for m in
                        re.finditer(r'(?m)^import (\w+)$', source)}
        entries = big_snip._split_snippets(source, "#")
        for name, requires, body, trailing in entries:
            if (not name) or (name == "big license") or _is_import_only(body):
                continue
            with subtest(module=module.__name__, snippet=name):
                extracted = big.extract_snippets(source, name)
                code = _snippet_code(extracted)
                tree = ast.parse(code)
                used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
                imported = set()
                for n in ast.walk(tree):
                    if isinstance(n, ast.Import):
                        imported.update(a.name.split(".")[0] for a in n.names)
                for mod in sorted(file_imports & used):
                    assert mod in imported, (
                        f"snippet {name!r} uses module {mod!r} but the extraction "
                        f"doesn't import it--add 'requires big import {mod}'")


def test_documented_snippets_are_real():
    # README's "Borrowable snippets" section is a *curated* catalog:
    # it needn't list every snippet--the plumbing (the license and
    # import snippets, internal helpers) is deliberately omitted.  but
    # every snippet name it *does* list, as a "`big ...`" term on its
    # own line, must be a real published snippet--so the catalog can't
    # rot when a snippet is renamed or removed.
    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    with open(readme_path, encoding="utf-8") as f:
        readme = f.read()
    start = readme.index("## Borrowable snippets")
    # the catalog ends at the next heading of level 1 or 2--its own
    # per-module subsections are ###, so they don't terminate it.
    # (don't anchor on the next section's exact title; headings get
    # reworded and re-leveled.)
    match = re.compile(r'(?m)^#{1,2} ').search(readme, start + 1)
    end = match.start() if match else len(readme)
    catalog = readme[start:end]

    real = set()
    for module in SNIPPET_PUBLISHING_MODULES:
        with open(module.__file__, encoding="utf-8") as f:
            source = f.read()
        for name, requires, body, trailing in big_snip._split_snippets(source, "#"):
            if name:
                real.add(name)

    documented = re.findall(r'(?m)^`(big [^`]+)`$', catalog)
    assert documented, "found no snippet names in the catalog--did its format change?"
    for name in documented:
        with subtest(snippet=name):
            assert name in real, (
                f"the 'Borrowable snippets' catalog lists {name!r}, "
                f"which isn't a published snippet")


def test_is_import_only_helper():
    # import-only bodies (directive lines are ignored)
    assert _is_import_only("import os")
    assert _is_import_only(
        "# --8<-- requires big license --8<--\nimport enum\nfrom sys import argv")
    # anything with a non-import statement is not import-only
    assert not _is_import_only("import os\nx = 1")
    # an empty body isn't import-only either
    assert not _is_import_only("")
    assert not _is_import_only("# --8<-- requires x --8<--\n")
    # a body that doesn't parse is not import-only (and doesn't raise)
    assert not _is_import_only("def f(:")


def run_tests(run=None):
    (run or bigtestlib.run)(name="big.snip", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
