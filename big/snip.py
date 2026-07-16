#!/usr/bin/env python3

"""
Snippets: marked regions of text files that other files borrow.
extract_snippets pulls snippets out of a file; apply_snippets
applies them to another file, like a patch.  Run
"python -m big.snip" for the command-line version.
"""

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

import pathlib
import sys

from . import builtin
from . import types

mm = builtin.ModuleManager()
export = mm.export


# the default comment leader for marker lines.  a real value, so
# introspected signatures read informatively (comment='#'), but
# also a sentinel: when s is bytes and comment is this exact
# object, it quietly becomes b'#'.
_default_comment = '#'


def _safe_where(text):
    # the error-message position prefix, for when text knows
    # where it lives (big.string); empty when it doesn't.
    where = getattr(text, 'where', None)
    return f"{where}: " if where else ""


def _cat(s, *pieces):
    # concatenates pieces, typed like s: when s is a big.string,
    # big.string.cat preserves its provenance; plain str and
    # bytes join as themselves.
    if isinstance(s, types.string):
        return type(s).cat(*pieces)
    return s[:0].join(pieces)


def _as_big_string(text, source=None):
    # a big.string knows its line and column numbers; reparsing
    # with one turns a vague error into one that says where.
    if isinstance(text, types.string):
        return text
    return types.string(text, source=source)


def _split_snippets(s, comment):
    # The one parser for snippets.  Splits s into a list of
    # [name, requires, body, trailing_linebreak] entries, and
    # every character of s lives in exactly one field of exactly
    # one entry:
    #
    #     s == empty.join(entry[2] + entry[3] for entry in entries)
    #
    # A snippet entry: name is the snippet's name, requires is a
    # tuple of the names its body requires, body runs from its
    # start marker line through its end marker line, and
    # trailing_linebreak is the linebreak ending the end marker
    # line--owned by the snippet, split out of the body so a
    # snippet can be dropped into new surroundings without one.
    # It's empty if the end marker line had no linebreak (end of
    # file).
    #
    # A non-snippet entry--the text before, between, and after
    # snippets--has an empty name, an empty requires tuple, and
    # an empty trailing_linebreak: blobs keep all their text,
    # linebreaks included, in the body.  Empty non-snippet
    # entries are omitted.
    #
    # All the marker-line grammar lives here.  A directive line
    # is "COMMENT --8<-- VERB [NAME] --8<--"; it may be indented
    # and may have trailing whitespace.  The space after the
    # second "--8<--" is reserved for future use; for now,
    # anything there is an error.
    #
    # comment is the comment leader directive lines start with:
    # always a real str or bytes value, never None.  when s is
    # bytes and comment is _default_comment itself (identity,
    # not equality), it quietly becomes b'#'.
    if isinstance(s, bytes):
        if comment is _default_comment:
            comment = b'#'
        elif not (isinstance(comment, bytes) and comment):
            raise TypeError(f"comment must be nonempty bytes, not {comment!r}")
        scissors = b"--8<--"
        space = b" "
        empty = b''
        start_directive = b"start"
        end_directive = b"end"
        requires_directive = b"requires"
    else:
        if not (isinstance(comment, str) and comment):
            raise TypeError(f"comment must be a nonempty str, not {comment!r}")
        scissors = "--8<--"
        space = " "
        empty = ''
        start_directive = "start"
        end_directive = "end"
        requires_directive = "requires"

    directive_prefix = comment + space + scissors + space
    entries = []
    seen = set()
    cursor = 0
    offset = 0
    open_name = open_start = None
    requires = []

    for line in s.splitlines(keepends=True):
        line_start = offset
        offset += len(line)
        stripped = line.strip()
        if not stripped.startswith(directive_prefix):
            continue
        rest = stripped[len(directive_prefix):]
        content, found, after = rest.partition(scissors)
        if not found:
            continue
        if after.strip():
            raise ValueError(f"{_safe_where(stripped)}unexpected trailing text on snippet marker line: {line!r}")
        directive, _, name = content.rstrip().partition(space)
        name = name.strip()

        if (not name) and (directive in (start_directive, end_directive, requires_directive)):
            raise ValueError(f"{_safe_where(stripped)}snippet marker line has no name: {line!r}")

        if directive == start_directive:
            if open_name is not None:
                raise ValueError(f"{_safe_where(name)}snippet {name!r} is nested inside snippet {open_name!r}, nested snippets are unsupported")
            if name in seen:
                raise ValueError(f"{_safe_where(name)}snippet {name!r} is already defined")
            seen.add(name)
            if cursor != line_start:
                entries.append([empty, (), s[cursor:line_start], empty])
            open_name = name
            open_start = line_start
            requires = []
        elif directive == end_directive:
            if open_name is None:
                raise ValueError(f"{_safe_where(name)}snippet {name!r} is not open (end before start?)")
            if name != open_name:
                raise ValueError(f"{_safe_where(name)}mismatched end marker {name!r}, should be {open_name!r}")
            # the snippet owns the linebreak ending its
            # end-marker line, split out of its body.  line came
            # from splitlines(keepends=True), so splitting it
            # again recovers the terminator--whatever splitlines
            # thinks a terminator is, which is the one true
            # definition around here.
            body_end = line_start + len(line.splitlines()[0])
            entries.append([open_name, tuple(requires), s[open_start:body_end], s[body_end:offset]])
            cursor = offset
            open_name = open_start = None
        elif directive == requires_directive:
            # requires is only legal inside a snippet.  a stray
            # one is probably debris from a hand-edit--say so.
            if open_name is None:
                raise ValueError(f"{_safe_where(directive)}requires {name!r} used outside a snippet")
            requires.append(name)
        else:
            raise ValueError(f"{_safe_where(directive)}unrecognized snippet directive {directive!r}")

    if open_name is not None:
        raise ValueError(f"{_safe_where(open_name)}snippet {open_name!r} has no end marker")
    if cursor < len(s):
        entries.append([empty, (), s[cursor:], empty])
    return entries


def _extract_snippets(s, names, comment):
    entries = _split_snippets(s, comment)
    by_name = {entry[0]: entry for entry in entries if entry[0]}

    seen = set()
    in_progress = []    # the current requires chain, for cycle reporting
    def visit(name, required_by):
        if name in in_progress:
            cycle = in_progress[in_progress.index(name):] + [name]
            chain = " -> ".join(repr(n) for n in cycle)
            raise ValueError(f"snippet requirements form a cycle: {chain}")
        if name in seen:
            return
        entry = by_name.get(name)
        if entry is None:
            if required_by is None:
                raise ValueError(f"snippet {name!r} not found")
            raise ValueError(f"{_safe_where(name)}snippet {name!r} not found (required by snippet {required_by!r})")
        in_progress.append(name)
        for required in entry[1]:
            visit(required, name)
        in_progress.pop()
        seen.add(name)
    for name in names:
        visit(name, None)

    # emit in source order.  each snippet keeps its own
    # end-of-line discipline: its terminator is the linebreak
    # its end-marker line had in s--so a snippet that ended s
    # without a trailing linebreak still does.
    pieces = []
    for name, requires, body, trailing in entries:
        if name in seen:
            pieces.append(body)
            pieces.append(trailing)
    return _cat(s, *pieces)


@export
def extract_snippets(s, *names, comment=_default_comment):
    """
    Extracts the named snippets from s and returns them--
    together with every snippet they require, transitively, in
    source order, marker lines and all, with no blank lines
    between them.  The result is ready to feed to
    apply_snippets, which preserves that order.

    Pass the snippet names as positional arguments:

        extract_snippets(source, 'B', 'D')

    A "snippet" is a run of lines in s bracketed by two
    scissors marker lines:

        {comment} --8<-- start NAME --8<--
        ...the body of the snippet...
        {comment} --8<-- end NAME --8<--

    A marker line may be indented, and may have trailing
    whitespace, but after stripping whitespace from both ends
    it must match its marker exactly.  Snippet names can't be
    empty and can't contain "--8<--".  The space on a marker
    line after the second "--8<--" is reserved for future
    use: anything there (except trailing whitespace)
    raises ValueError.

    A snippet's body may declare that it requires another
    snippet in the same file, with a "requires" directive line:

        {comment} --8<-- requires NAME --8<--

    The directive is ordinary body text and travels with the
    snippet; extract_snippets is the layer that interprets it.
    Requirements resolve transitively, local file only, and
    can't form a cycle.

    comment is the comment leader the marker lines start with;
    it defaults to '#'.  Pass a different comment string to
    work with snippets in other languages, e.g. comment='//'
    for the C family.

    s may be str or bytes.  The names and comment must be the
    same type as s, and the return value is the same type as s.

    Snippets can't nest.

    Raises ValueError if the snippet (or any snippet it
    requires) isn't in s, if the requirements form a cycle, or
    if s's snippet structure is malformed: nested snippets, an
    unterminated snippet, mismatched or out-of-order markers,
    or two snippets with the same name.
    """
    if isinstance(s, bytes):
        name_type = bytes
        scissors = b"--8<--"
    else:
        name_type = str
        scissors = "--8<--"

    if not names:
        raise ValueError("no snippet names given")
    for name in names:
        if not isinstance(name, name_type):
            raise TypeError(f"names must be {name_type.__name__}, not {type(name).__name__}")
        if not name:
            raise ValueError("snippet names can't be empty")
        if scissors in name:
            raise ValueError(f"snippet names can't contain {scissors!r}")

    try:
        return _extract_snippets(s, names, comment)
    except ValueError as error:
        if type(s) is not str:
            # bytes get no positions; a big.string was parsed
            # with its positions on the first (only) pass.
            raise
        # the perky trick: plain str parses fast; when it fails,
        # reparse as big.string--which knows its line and column
        # numbers--purely to raise an error that says where.
        _extract_snippets(_as_big_string(s), names, comment)
        raise error # pragma: no cover -- the reparse always raises


def _apply_snippets(s, snippets, comment):
    linebreak = b"\n" if isinstance(s, bytes) else "\n"

    target = _split_snippets(s, comment)
    patches = _split_snippets(snippets, comment)

    # snippets must contain only snippets; the text between them
    # is just their linebreaks.
    for name, requires, body, trailing in patches:
        if not name and body.strip():
            raise ValueError(f"{_safe_where(body)}unexpected text among the snippets: {body.strip()!r}")
    patches = [entry for entry in patches if entry[0]]
    if not patches:
        raise ValueError("no snippets to apply")

    by_name = {entry[0]: entry for entry in target if entry[0]}

    # iterate in reverse, so a snippet s lacks can be inserted
    # before the entry we processed last time--its successor.
    previous = None
    for name, requires, body, trailing in reversed(patches):
        existing = by_name.get(name)
        if existing is not None:
            # overwrite in place; s's surroundings (and its
            # end-of-line discipline) are preserved.
            existing[1] = requires
            existing[2] = body
            previous = existing
            continue
        if previous is None:
            # the last snippet: append at the end of s.  never
            # glue our start marker onto the end of a file that
            # doesn't end with a linebreak.
            if target:
                tail = target[-1]
                end = tail[3] or tail[2]
                if not end.endswith(linebreak):
                    tail[3] = _cat(s, tail[3], linebreak)
            entry = [name, requires, body, trailing]
            target.append(entry)
        else:
            # a fresh snippet gets a blank line between itself
            # and the snippet it's inserted in front of: its
            # trailing linebreak, twice.
            separator = trailing or linebreak
            entry = [name, requires, body, _cat(s, separator, separator)]
            target.insert(target.index(previous), entry)
        by_name[name] = entry
        previous = entry

    pieces = []
    for entry in target:
        pieces.append(entry[2])
        pieces.append(entry[3])
    return _cat(s, *pieces)


@export
def apply_snippets(s, snippets, comment=_default_comment):
    """
    Applies snippets to s, like a patch: returns a copy of s
    with every snippet in snippets applied.  snippets is a
    string of marker-bracketed snippets, one after another--
    the value returned by extract_snippets.  (See
    extract_snippets for what a snippet is, and what comment
    is.)

    A snippet s already carries is overwritten in place,
    wherever s keeps it; everything around it, and the order
    of the snippets in s, is preserved.  A snippet s lacks is
    inserted: immediately before the snippet that follows it
    in snippets--with a blank line between them--or, if it's
    the last one, appended at the end of s.  (A deliberately
    simple placement rule.  Rearrange the snippets in s however
    you like; apply_snippets honors your ordering forever
    after.)

    End-of-line discipline is preserved: a snippet appended at
    the end of s ends with a linebreak only if it ended with
    one in snippets.

    s, snippets, and comment must all be the same type, str or
    bytes, and the return value is the same type as s.

    Raises ValueError if snippets contains anything besides
    snippets, or if either argument's snippet structure is
    malformed (nested snippets, unterminated snippets,
    mismatched markers--see extract_snippets).
    """
    if isinstance(s, bytes):
        if not isinstance(snippets, bytes):
            raise TypeError(f"snippets must be bytes, not {type(snippets).__name__}")
    else:
        if not isinstance(snippets, str):
            raise TypeError(f"snippets must be str, not {type(snippets).__name__}")

    try:
        return _apply_snippets(s, snippets, comment)
    except ValueError as error:
        if type(s) is not str:
            raise
        _apply_snippets(_as_big_string(s), _as_big_string(snippets), comment)
        raise error # pragma: no cover -- the reparse always raises


@export
def sync_snippets(source, destination, filter=None, *, comment=_default_comment):
    """
    Updates destination's borrowed snippets from source, and
    returns the updated destination.  The destination is its own
    manifest: sync_snippets reads the names of the snippets
    destination already carries, extracts those snippets from
    source--together with every snippet they require--and
    applies them back to destination.  (A required snippet
    destination doesn't carry yet gets installed by the apply.)

    filter, if not None, is a callable: it's called with each of
    destination's snippet names, and only names it approves are
    synced.  Use it to whitelist by project prefix when
    destination folds together snippets borrowed from several
    sources:

        sync_snippets(big_text, warehouse,
                      (lambda name: name.startswith('big ')))

    source, destination, and comment must all be the same type,
    str or bytes, and the return value is the same type.

    Raises ValueError if destination carries no snippets to sync
    (after filtering), plus everything extract_snippets and
    apply_snippets raise.
    """
    try:
        entries = _split_snippets(destination, comment)
    except ValueError as error:
        if type(destination) is not str:
            raise
        _split_snippets(_as_big_string(destination), comment)
        raise error # pragma: no cover -- the reparse always raises
    names = [entry[0] for entry in entries if entry[0]]
    if filter is not None:
        names = [name for name in names if filter(name)]
    if not names:
        raise ValueError("destination has no snippets to sync")
    return apply_snippets(destination, extract_snippets(source, *names, comment=comment), comment=comment)


def usage(error):
    print(f"error: {error}")
    print("""
usage: python -m big.snip [-c COMMENT] <command> ...

Commands:

    list FILE
        Prints the names of the snippets in FILE, one per line.

    extract FILE NAME [NAME2 ...]
        Prints the named snippets from FILE, with all their
        required snippets, in source file order.

    apply SOURCE DESTINATION NAME [NAME2 ...]
        Extracts the named snippet(s)--and every snippet they
        require--from file SOURCE, and applies them to DESTINATION.
        For every snippet S applied to DESTINATION, if DESTINATION
        already contains S, it's overwritten, otherwise S is
        inserted immediately before the subsequent snippet being
        applied.  Only writes DESTINATION if something changed.

    check SOURCE DESTINATION NAME [NAME2 ...]
        Like apply, but only reports: prints a line for every
        snippet that's missing or differs in DESTINATION, and
        exits nonzero if apply would change anything.

    sync SOURCE DESTINATION [PREFIX ...]
        Like apply, but DESTINATION is its own manifest: every
        snippet DESTINATION already carries is updated with the
        version in SOURCE.  With PREFIXes, only the snippets
        whose names start with one of them--use project prefixes
        ("big ", "appeal ") when DESTINATION folds together
        snippets borrowed from several sources.

    -c COMMENT
        The comment leader the marker lines start with;
        defaults to "#".  Use "-c //" for the C family, etc.
        May appear anywhere on the command line.

A "snippet" is a run of lines bracketed by two scissors marker
lines:

    # --8<-- start NAME --8<--
    ...the body of the snippet...
    # --8<-- end NAME --8<--

Snippets can't nest.  Snippet names can't be empty and can't
contain "--8<--", but they can contain whitespace.  Snippet
names must be unique per-file.  For now, you can't have anything but whitespace after
the second "--8<--"; that space is reserved for future use.

A snippet's body may declare that it depends on one or more
other snippets with a "requires" directive line:

    # --8<-- requires NAME --8<--

Requirements resolve transitively, local file only--there is no
cross-file mechanism.  The directive line is ordinary body text;
it travels with the snippet, so borrowed copies keep their
dependency information.  "requires" cycles are an error.

Files are read and written as UTF-8 text.  When a file is
malformed, the error says where: file, line, and column.""")
    return 2


def main(argv):
    def _snippet_names(data, comment):
        return [entry[0] for entry in _split_snippets(data, comment) if entry[0]]

    # -c COMMENT may appear anywhere on the command line.
    comment = None
    args = []
    i = iter(argv)
    for arg in i:
        if arg == '-c':
            if comment is not None:
                return usage("-c specified more than once")
            comment = next(i, None)
            if not comment:
                return usage("-c requires a nonempty comment string")
        else:
            args.append(arg)
    comment = comment or '#'

    if not args:
        return usage("no command given")
    command, *args = args

    # the perky trick, tool edition: the first pass reads and
    # parses plain str--fast.  if a parse fails, the second pass
    # rereads with big.string, which knows its file, line, and
    # column, so the error can say where.
    for continue_on_error in (True, False):
        if continue_on_error:
            def read(filename):
                return pathlib.Path(filename).read_text(encoding='utf-8')
        else:
            def read(filename):
                text = pathlib.Path(filename).read_text(encoding='utf-8')
                return _as_big_string(text, source=filename)

        try:
            if command == 'list':
                if len(args) != 1:
                    return usage("list takes exactly one argument, a file")
                for name in _snippet_names(read(args[0]), comment):
                    print(name)
                return 0

            if command == 'extract':
                if len(args) < 2:
                    return usage("extract takes a file and at least one snippet name")
                filename, *names = args
                sys.stdout.write(extract_snippets(read(filename), *names, comment=comment))
                sys.stdout.flush()
                return 0

            if command == 'sync':
                if len(args) < 2:
                    return usage("sync takes a source file, a destination file, and optional name prefixes")
                source_filename, destination_filename, *prefixes = args
                source = read(source_filename)
                destination = original = read(destination_filename)
                if prefixes:
                    def filter(name):
                        return any(name.startswith(p) for p in prefixes)
                else:
                    filter = None
                destination = sync_snippets(source, destination, filter, comment=comment)
                # report which snippets changed.
                before = {entry[0]: entry[2] for entry in _split_snippets(original, comment) if entry[0]}
                for name, requires, body, trailing in _split_snippets(destination, comment):
                    if name and before.get(name) != body:
                        print(f"{destination_filename}: snippet {name!r} synced.")
                if destination == original:
                    print(f"{destination_filename} unchanged.")
                else:
                    pathlib.Path(destination_filename).write_text(destination, encoding='utf-8')
                    print(f"{destination_filename} updated.")
                return 0

            if command in ('apply', 'check'):
                if len(args) < 3:
                    return usage(f"{command} takes a source file, a destination file, and at least one snippet name")
                source_filename, destination_filename, *names = args
                source = read(source_filename)
                destination = original = read(destination_filename)
                changes = 0
                patch = extract_snippets(source, *names, comment=comment)
                carried = {entry[0]: entry[2] for entry in _split_snippets(destination, comment) if entry[0]}
                # extract output contains only snippet entries--
                # their linebreaks are owned, not blobs between.
                for name, requires, body, trailing in _split_snippets(patch, comment):
                    if name not in carried:
                        changes += 1
                        verbed = "missing" if command == 'check' else "applied"
                        print(f"{destination_filename}: snippet {name!r} {verbed}.")
                    elif carried[name] != body:
                        changes += 1
                        verbed = "differs" if command == 'check' else "applied"
                        print(f"{destination_filename}: snippet {name!r} {verbed}.")
                if command == 'check':
                    return 1 if changes else 0
                destination = apply_snippets(destination, patch, comment=comment)
                if destination == original:
                    print(f"{destination_filename} unchanged.")
                else:
                    pathlib.Path(destination_filename).write_text(destination, encoding='utf-8')
                    print(f"{destination_filename} updated.")
                return 0

            return usage(f"unknown command {command!r}")
        except ValueError as error:
            if continue_on_error:
                continue
            usage(error)
            return 1
        except OSError as error:
            usage(error)
            return 1


mm()

if __name__ == '__main__': # pragma: no cover
    sys.exit(main(sys.argv[1:]))
