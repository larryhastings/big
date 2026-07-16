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

import re
import sys

from types import MethodType


class ModuleManager:
    """
    A class that manages your module namespace, including __all__.

    ModuleManager manages the namespace of your module, making
    it easy to only export the symbols you want to, and to
    delete any temporary symbols you don't want to leave around.

    Simply instantiate a ModuleManager object at module scope
    in your module, then call it at the end of your module.
    (ModuleManager works at module scope and class scope; it relies
    on the calling frame's namespace being a real, writable dict, so
    it doesn't work inside a function body.)

        import big.all as big
        mm = big.ModuleManager()
        ...
        mm()
        # eof

    What does that do?
        * If your module doesn't have an __all__ list, it adds one.
        * If you call mm.export('a', 'b', ...) it adds all those
          strings to __all__.
        * If you decorate a function or class with @mm.export
          it adds that symbol to __all__.
        * Exporting a name that's already in __all__ raises
          ValueError--it's nearly always a bug (a stale hand-rolled
          __all__, or a stray decorator on an internal function).
          If the redundancy is intentional, pass force=True:
          mm.export('a', force=True) never raises, and __all__
          still only lists each name once.
        * If you call mm.delete('x', 'y', ...), or decorate a
          function or class with @mm.delete, it adds those symbols
          to an internal "deletions" list.  Deleting a name that's
          already scheduled for deletion raises ValueError, with
          the same force=True escape hatch.
        * When you call the mm instance, it deletes all the symbols
          on the deletions list.  It also detects and removes
          *itself*, along with any names bound to its own export
          and delete methods.  (Other ModuleManager instances in
          the same namespace are left alone--each manager cleans
          up only after itself.)

    Example:

        mm = big.ModuleManager()  # creates __all__
        export = mm.export
        delete = mm.delete

        @export
        def externally_visible_symbol():
            ...

        TEMP_VALUE = 83
        delete('TEMP_VALUE')

        @delete
        def temporary_fn():
            ...
        temporary_fn()

        ...

        # deletes "mm", "export", "delete", 'TEMP_VALUE', and "temporary_fn"
        mm()
    """

    def __init__(self):
        self.parent_locals = parent_locals = sys._getframe(1).f_locals
        existing_all = parent_locals.get('__all__', None)
        if existing_all is None:
            parent_locals['__all__'] = existing_all = []
        self.all = existing_all
        self.deletions = []

    def export(self, *args, force=False):
        all = self.all
        for o in args:
            name = getattr(o, '__name__', None)
            if not name:
                if not isinstance(o, str):
                    raise TypeError(f"{o!r} isn't a string and doesn't have a __name__")
                name = o
            if name in all:
                # exporting an already-exported name is a bug--
                # unless you pass force=True, which quietly
                # permits the redundancy.  either way, __all__
                # only ever lists a name once.
                if force:
                    continue
                raise ValueError(f"can't export {name!r}, it's already in __all__")
            all.append(name)
        if len(args) == 1:
            return args[0]

    def delete(self, *args, force=False):
        deletions = self.deletions
        for o in args:
            name = getattr(o, '__name__', None)
            if not name:
                if not isinstance(o, str):
                    raise TypeError(f"{o!r} isn't a string and doesn't have a __name__")
                name = o
            if name in deletions:
                # same rule as export: a redundant delete is a
                # bug unless force=True says otherwise.
                if force:
                    continue
                raise ValueError(f"can't delete {name!r}, it's already scheduled for deletion")
            deletions.append(name)
        if len(args) == 1:
            return args[0]

    def __call__(self):
        parent_locals = self.parent_locals

        append = self.deletions.append
        methods = [self.export, self.delete]
        already_added = set(self.deletions)

        # automatically clean up after ourselves--and *only* ourselves.
        # other ModuleManager instances in the namespace are their
        # own responsibility.
        #
        # Note: our bound methods must be found by *equality*, not
        # identity--bound method objects are created fresh on every
        # attribute access, so "value is self.export" can never be
        # true for a stored "export = mm.export" alias.  Method
        # equality compares __self__ and __func__, so it only ever
        # matches *our* methods.  But == must only run between actual
        # bound methods; comparing arbitrary module globals invites
        # exotic __eq__ methods (e.g. numpy arrays) to blow up the
        # cleanup.  Hence the MethodType gate.
        for name, value in parent_locals.items():
            if name in already_added:
                continue
            if (value is self) or (isinstance(value, MethodType) and (value in methods)):
                append(name)
                already_added.add(name)

        for name in self.deletions:
            del parent_locals[name]

mm = ModuleManager()
export = mm.export

export(ModuleManager)

from functools import update_wrapper
# (inspect.signature is imported lazily, inside pure_virtual--
# inspect costs ~13ms to import and decoration is rare.)

from types import SimpleNamespace as namespace
export('namespace')


@export
def try_float(o):
    """
    Returns True if o can be converted into a float,
    and False if it can't.
    """
    try:
        float(o)
        return True
    except (TypeError, ValueError):
        return False

@export
def try_int(o):
    """
    Returns True if o can be converted into an int,
    and False if it can't.

    Note that int() truncates floats, so try_int(3.9)
    is True--while try_int("3.9") is False, because
    int() won't parse a string representing a
    non-integer number.
    """
    try:
        int(o)
        return True
    except (TypeError, ValueError):
        return False

_sentinel = object()

@export
def get_float(o, default=_sentinel):
    """
    Returns float(o), unless that conversion fails,
    in which case returns the default value.  If
    you don't pass in an explicit default value,
    the default value is o.
    """
    try:
        return float(o)
    except (TypeError, ValueError):
        if default is not _sentinel:
            return default
        return o

@export
def get_int(o, default=_sentinel):
    """
    Returns int(o), unless that conversion fails,
    in which case returns the default value.  If
    you don't pass in an explicit default value,
    the default value is o.
    """
    try:
        return int(o)
    except (TypeError, ValueError):
        if default is not _sentinel:
            return default
        return o

@export
def get_int_or_float(o, default=_sentinel):
    """
    Converts o into a number, preferring an int to a float.

    get_int_or_float is designed for converting strings:
    it's a sort of poor man's ast.literal_eval.  If o is a
    string (str, bytes, or bytearray) that reads as an int,
    returns that int; if it reads as a float instead, returns
    that float.  (Anything float() accepts "reads as a float",
    including "inf" and "nan".)

    If o is already an int, returns o unchanged.
    If o is already a float, if int(o) == o, returns int(o),
      otherwise returns o.  (Infinities and NaNs are returned
      unchanged.)

    Anything else--including number-like objects such as
    decimal.Decimal and fractions.Fraction--is outside
    get_int_or_float's purview: it returns the default value.
    If you don't pass in an explicit default value, the
    default value is o.
    """
    if isinstance(o, int):
        return o
    if isinstance(o, float):
        try:
            int_o = int(o)
        except (ValueError, OverflowError):
            # o is a NaN or an infinity.
            # it's already a float, return it unchanged.
            return o
        if int_o == o:
            return int_o
        return o
    if isinstance(o, (str, bytes, bytearray)):
        try:
            return int(o)
        except ValueError:
            try:
                # if you pass in the *string* "0.0",
                # this will return 0, not 0.0.
                return get_int_or_float(float(o))
            except ValueError:
                pass
    if default is not _sentinel:
        return default
    return o

# matches one escape sequence in a (non-raw) Python string literal:
# a line continuation, or a named / u16 / u32 / hex / octal escape,
# or a single escaped character.
_literal_eval_escape_re = re.compile(
    r'\\(?:\n|N\{[^}]*\}|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8}|x[0-9a-fA-F]{2}|[0-7]{1,3}|.)',
    re.DOTALL)

_literal_eval_quotes = frozenset(("'", '"'))
_literal_eval_prefixes = frozenset('rRuUbBfF')

def _literal_eval_splice(inner, value):
    import ast
    from .types import string
    # Rebuild the decoded string as verbatim slices of inner,
    # splicing in a synthesized character for each escape sequence.
    # The synthesized characters are positioned at their escape
    # sequences, so every character reports a true line and column.
    # Returns None if the result doesn't match value (some exotic
    # literal we don't understand)--the caller falls back.
    raw = str(inner)
    pieces = []
    append = pieces.append
    pos = 0
    for match in _literal_eval_escape_re.finditer(raw):
        start = match.start()
        if start > pos:
            append(inner[pos:start])
        escape = match.group()
        try:
            decoded = ast.literal_eval(f'"{escape}"')
        except (ValueError, SyntaxError): # pragma: nocover
            # defensive: an escape sequence that survived the
            # *original* parse always decodes re-wrapped in double
            # quotes.  (an escaped double quote is still just \".)
            return None
        if decoded:
            position = inner[start:start+1]
            append(string(decoded,
                source=position.source,
                line_number=position.line_number,
                column_number=position.column_number,
                first_column_number=position.first_column_number,
                tab_width=position.tab_width,
                ))
        pos = match.end()
    if pos < len(raw):
        append(inner[pos:])
    result = string.cat(*pieces)
    if str(result) != value:
        return None
    return result

@export
def literal_eval(s):
    """
    Wrapper around ast.literal_eval that preserves big.string provenance.

    literal_eval(s) evaluates s exactly like Python's ast.literal_eval.
    If s is an ordinary str, or the result isn't a str, the result is
    exactly ast.literal_eval's result.

    If s is a big.string and the result is a str, literal_eval
    tries to preserve provenance, in one of three ways, best-first:

    * If the decoded value appears verbatim in s--there are no escape
      sequences--the result is a true slice of s.  Both "where" and
      "context" work, and every character knows its true position.
    * If the literal contains escape sequences, the result is assembled
      from verbatim slices of s, splicing in a synthesized character for
      each escape sequence.  Every character still reports a true line
      and column--a decoded escape reports the position of its escape
      sequence--but "context" is unavailable, as the result is no
      longer one contiguous slice of the original.
    * If s opens with a quoted string whose contents are exactly the
      decoded value--an escape-free literal followed by trailing text
      ast.literal_eval tolerates, like a comment--the result is that
      true slice.  "where" and "context" both work.

    If the decoded value can't be honestly mapped back onto the
    source--implicit string concatenation ("a" "b"), or a literal
    whose escape sequences make the value differ from the source
    text, followed by trailing text--literal_eval returns a plain
    str.  A big.string position is a promise; rather than fabricate
    positions that are confidently wrong, literal_eval declines to
    provide provenance at all.

    In every case the value is character-for-character identical to
    ast.literal_eval's result; only the type and metadata vary.
    """
    # ast costs ~1.5ms to import, and only literal_eval uses
    # it.  and big.types imports big.builtin--everything does;
    # it's the bottom of the stack--so the import of big.string
    # must be lazy too, to dodge the circular import.
    import ast
    from .types import string

    is_big = isinstance(s, string)
    text = str(s) if is_big else s
    if isinstance(text, str):
        # ast.literal_eval in 3.10+ strips leading spaces and tabs
        # itself (only those two--a leading newline is an error on
        # every version).  strip them here too, so 3.6-3.9 match.
        text = text.lstrip(' \t')
    value = ast.literal_eval(text)
    if not (is_big and isinstance(value, str)):
        return value

    stripped = s.strip()
    raw = str(stripped)

    if raw and (raw[-1] in _literal_eval_quotes):
        prefix_length = 0
        while raw[prefix_length] in _literal_eval_prefixes:
            prefix_length += 1
        quote = raw[prefix_length]
        if quote == raw[-1]:
            triple = quote * 3
            if (raw.startswith(triple, prefix_length)
                and raw.endswith(triple)
                and (len(raw) >= (prefix_length + 6))):
                quote_length = 3
            else:
                quote_length = 1
            inner = stripped[prefix_length + quote_length : len(stripped) - quote_length]
            if str(inner) == value:
                # no escape sequences: the value is a verbatim slice
                return inner
            result = _literal_eval_splice(inner, value)
            if result is not None:
                return result

    # the extracurricular rescue: parse the source with big's own
    # split_quoted_strings.  if the (stripped) source opens with a
    # quoted string whose contents are *exactly* the decoded value--
    # a literal with no consequential escapes, followed by trailing
    # text ast.literal_eval tolerates, like a comment--then the value
    # sits verbatim between the delimiters, and the segment is a true
    # slice of the source, provenance intact.  the comparison IS the
    # proof, so this can't be confidently wrong--only cautiously
    # silent.  (next() can't raise here: ast.literal_eval already
    # succeeded, so the source is nonempty and any string literal it
    # opens with is well-formed.)
    from .text import split_quoted_strings
    leading_quote, segment, trailing_quote = next(split_quoted_strings(
        stripped, multiline_quotes=('"""', "'''")))
    if leading_quote and trailing_quote and (str(segment) == value):
        return segment

    # the decoded value can't be honestly mapped back onto the
    # source--implicit string concatenation, an escaped literal with
    # trailing text, etc.  no provenance beats false provenance:
    # return a plain str.
    return value


@export
def pluralize(i, singular, plural=None):
    """
    Returns a string counting i things, using the correct
    English grammatical number: '1 apple', '3 apples'.

    i should be a number.  singular should be the singular
    form of the noun.  If plural is None (the default), the
    plural form is the singular form plus 's'; for a noun
    with an irregular plural, pass it in explicitly:

        >>> pluralize(2, 'box', 'boxes')
        '2 boxes'

    Uses the plural form for every count except exactly 1.
    (Zero is '0 apples', 1.5 is '1.5 apples'.)
    """
    if i == 1:
        return f"{i} {singular}"

    if plural is not None:
        return f"{i} {plural}"
    return f"{i} {singular}s"

@export
def pure_virtual():
    """
    Decorator for pure virtual methods.  Calling a method
    decorated with this raises a NotImplementedError exception.
    """
    def pure_virtual(fn):
        from inspect import signature
        def wrapper(self, *args, **kwargs):
            raise NotImplementedError(f"pure virtual method {fn.__name__} called")
        update_wrapper(wrapper, fn)
        wrapper.__signature__ = signature(fn)
        return wrapper
    return pure_virtual


@export
class ClassRegistry(dict):
    """
    A dict subclass with attribute-style access, useful as a class decorator.

    big's BoundInnerClass decorator encourages heavily-nested classes,
    but Python's scoping rules make them clumsy to work with. ClassRegistry
    makes it easy to reference base classes in a different class scope
    for easier subclassing.

    To use:
        1. Create a ClassRegistry object.
        2. Decorate the base classes you need with a call to that instance.
        3. Access those base classes as attributes on the ClassRegistry.

    By default the name of the class is used as the name of the attribute.
    You can specify a custom name by passing it in an argument to the instance
    when you decorate the class.

    Example:
        # Step 1: Create a registry, here named "base"
        base = ClassRegistry()

        # Step 2: Register a class by using "base" as a decorator
        @base()
        class Dingus:
            pass

        # Step 3: Access the class defined in step 2, as an attribute on "base"
        class Doodad(base.Dingus):
            pass

        # Step 4: Register a class using a custom name
        @base('MyName')
        class SomeClass:
            pass

        # Step 5: Access the class created in step 4, via that custom name
        class Other(base.MyName):
            pass

    When using with BoundInnerClass, put @base() *above* @BoundInnerClass:

        @base()
        @BoundInnerClass
        class Transaction(base.Signaling):
            pass
    """

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name) from None

    # attribute assignment and deletion write through to the dict,
    # for symmetry with attribute access
    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name) from None

    def __call__(self, name=None):
        """Decorator factory to register a class."""
        if isinstance(name, type):
            raise TypeError(
                f"missing parentheses: to register class {name.__name__!r}, "
                f"decorate with @registry(), not @registry"
            )
        def decorator(cls):
            key = name if name is not None else cls.__name__
            self[key] = cls
            return cls
        return decorator


mm()
