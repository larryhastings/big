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

from big.test import raises

import ast
import big.builtin as big
from big.builtin import ClassRegistry
from big.types import string
import decimal
import fractions
import math


class HostileEq:
    "__eq__ raises.  Nobody expects the hostile __eq__."
    def __eq__(self, other): # pragma: no cover
        # never called--that's what the tests using this prove
        raise RuntimeError("nobody expects the hostile __eq__")

class VectorizedEq:
    "numpy-style: __eq__ returns an object whose truth value raises."
    def __eq__(self, other): # pragma: no cover
        # never called--that's what the tests using this prove
        return self
    def __bool__(self): # pragma: no cover
        raise ValueError("truth value is ambiguous")


def test_try_int():
    assert big.try_int(0)
    assert big.try_int(0.0)
    assert big.try_int("0")

    assert not (big.try_int(3j))
    assert not (big.try_int(None))
    assert not (big.try_int(()))
    assert not (big.try_int({}))
    assert not (big.try_int([]))
    assert not (big.try_int(set()))
    assert not (big.try_int("0.0"))
    assert not (big.try_int("abc"))
    assert not (big.try_int("3j"))
    assert not (big.try_int("None"))

def test_try_float():
    assert big.try_float(0)
    assert big.try_float(0.0)
    assert big.try_float("0")
    assert big.try_float("0.0")

    assert not (big.try_float(3j))
    assert not (big.try_float(None))
    assert not (big.try_float(()))
    assert not (big.try_float({}))
    assert not (big.try_float([]))
    assert not (big.try_float(set()))
    assert not (big.try_float("abc"))
    assert not (big.try_float("3j"))
    assert not (big.try_float("None"))

def test_get_int():
    sentinel = object()
    assert big.get_int(0,      sentinel) == 0
    assert big.get_int(0.0,    sentinel) == 0
    assert big.get_int("0",    sentinel) == 0

    assert big.get_int(35,     sentinel) == 35
    assert big.get_int(35.1,   sentinel) == 35

    assert big.get_int(3j,     sentinel) == sentinel
    assert big.get_int(None,   sentinel) == sentinel
    assert big.get_int((),     sentinel) == sentinel
    assert big.get_int({},     sentinel) == sentinel
    assert big.get_int([],     sentinel) == sentinel
    assert big.get_int(set(),  sentinel) == sentinel
    assert big.get_int("",     sentinel) == sentinel
    assert big.get_int("0.0",  sentinel) == sentinel
    assert big.get_int("abc",  sentinel) == sentinel
    assert big.get_int("3j",   sentinel) == sentinel
    assert big.get_int("None", sentinel) == sentinel

    d = {}
    assert big.get_int(d) == d
    assert big.get_int(3j) == 3j
    assert big.get_int(None) == None
    assert big.get_int("abc") == "abc"

def test_get_float():
    sentinel = object()
    assert big.get_float(0,      sentinel) == 0.0
    assert big.get_float(0.0,    sentinel) == 0.0
    assert big.get_float("0",    sentinel) == 0.0
    assert big.get_float("0.0",  sentinel) == 0.0

    assert big.get_float(35,     sentinel) == 35.0
    assert big.get_float(35.1,   sentinel) == 35.1

    assert big.get_float(3j,     sentinel) == sentinel
    assert big.get_float(None,   sentinel) == sentinel
    assert big.get_float((),     sentinel) == sentinel
    assert big.get_float({},     sentinel) == sentinel
    assert big.get_float([],     sentinel) == sentinel
    assert big.get_float(set(),  sentinel) == sentinel
    assert big.get_float("",     sentinel) == sentinel
    assert big.get_float("abc",  sentinel) == sentinel
    assert big.get_float("3j",   sentinel) == sentinel
    assert big.get_float("None", sentinel) == sentinel

    d = {}
    assert big.get_float(d) == d
    assert big.get_float(3j) == 3j
    assert big.get_float(None) == None
    assert big.get_float("abc") == "abc"

def test_get_int_or_float():
    sentinel = object()
    assert big.get_int_or_float(0,       sentinel) == 0
    assert isinstance(big.get_int_or_float(0,       sentinel), int)
    assert big.get_int_or_float("0",     sentinel) == 0
    assert isinstance(big.get_int_or_float("0",     sentinel), int)

    assert big.get_int_or_float(12345,   sentinel) == 12345
    assert isinstance(big.get_int_or_float(12345,   sentinel), int)
    assert big.get_int_or_float("12345", sentinel) == 12345
    assert isinstance(big.get_int_or_float("12345", sentinel), int)

    assert big.get_int_or_float(0.0,     sentinel) == 0
    assert isinstance(big.get_int_or_float("0.0",   sentinel), int)
    assert big.get_int_or_float(3.5,     sentinel) == 3.5
    assert isinstance(big.get_int_or_float("3.5",   sentinel), float)
    assert big.get_int_or_float(123.0,   sentinel) == 123
    assert isinstance(big.get_int_or_float("123.0", sentinel), int)

    assert big.get_int_or_float("abc",  sentinel) == sentinel
    assert big.get_int_or_float("3j",   sentinel) == sentinel
    assert big.get_int_or_float("None", sentinel) == sentinel
    assert big.get_int_or_float("",     sentinel) == sentinel
    assert big.get_int_or_float(3j,     sentinel) == sentinel
    assert big.get_int_or_float(None,   sentinel) == sentinel
    assert big.get_int_or_float({},     sentinel) == sentinel
    assert big.get_int_or_float((),     sentinel) == sentinel
    assert big.get_int_or_float(set(),  sentinel) == sentinel

    d = {}
    assert big.get_int_or_float(d) == d
    assert big.get_int_or_float(3j) == 3j
    assert big.get_int_or_float(None) == None
    assert big.get_int_or_float("abc") == "abc"

    # bytes and bytearrays work like str
    assert big.get_int_or_float(b"12345", sentinel) == 12345
    assert isinstance(big.get_int_or_float(b"12345", sentinel), int)
    assert big.get_int_or_float(b"3.5",   sentinel) == 3.5
    assert big.get_int_or_float(bytearray(b"123.0"), sentinel) == 123
    assert big.get_int_or_float(b"abc",   sentinel) == sentinel

    # actual float infinities and NaNs pass through unchanged
    inf = float("inf")
    assert big.get_int_or_float( inf, sentinel) == inf
    assert big.get_int_or_float(-inf, sentinel) == -inf
    assert math.isnan(big.get_int_or_float(float("nan"), sentinel))

    # strings that read as infinities and NaNs convert
    assert big.get_int_or_float("inf",       sentinel) == inf
    assert big.get_int_or_float("-Infinity", sentinel) == -inf
    assert math.isnan(big.get_int_or_float("nan", sentinel))

    # number-like objects that aren't int or float are outside
    # get_int_or_float's purview--in particular, they must not
    # be truncated by int()
    assert big.get_int_or_float(decimal.Decimal("3.5"),   sentinel) == sentinel
    assert big.get_int_or_float(fractions.Fraction(7, 2), sentinel) == sentinel

    # big integer strings convert exactly, with no float round-trip
    big_number = (10 ** 40) + 1
    assert big.get_int_or_float(str(big_number), sentinel) == big_number

def test_pluralize():
    def test(expected, *args):
        assert big.pluralize(*args) == expected

    # exactly 1 is singular; everything else--zero, many,
    # negative, fractional--is plural, per English convention
    test('1 apple', 1, 'apple')
    test('0 apples', 0, 'apple')
    test('2 apples', 2, 'apple')
    test('-1 apples', -1, 'apple')
    test('1.5 apples', 1.5, 'apple')

    # a float equal to 1 is singular (1.0 == 1)
    test('1.0 apple', 1.0, 'apple')

    # irregular plurals are passed in explicitly
    test('1 box', 1, 'box', 'boxes')
    test('2 boxes', 2, 'box', 'boxes')
    test('1 goose', 1, 'goose', 'geese')
    test('7 geese', 7, 'goose', 'geese')

def test_pure_virtual():
    @big.pure_virtual()
    def uncallable(a): # pragma: no cover
        print(f"hey, look! we wuz called! and a={a}, just ask Ayn Rand!")

    with raises(NotImplementedError):
        uncallable('a')

def test_ModuleManager():
    ##
    ## ModuleManager.clean only works properly
    ## at module scope and class scope.
    ## (Maybe it works in function scope in 3.13+?)
    ##
    ## So, let's test it inside class scope.
    class PointlessClass:
        mm = big.ModuleManager()

        export = mm.export
        delete = mm.delete

        with raises(TypeError) as cm:
            export(35)
        assert '35' in str(cm.exception)
        with raises(TypeError) as cm:
            delete(35)
        assert '35' in str(cm.exception)

        def foo(): pass
        result = export(foo)
        assert result is foo
        result = delete(foo)
        assert result is foo

        mm.export("bar", "bat", "zip")
        mm.delete("bar", "bat", "zoo")

        assert mm.all == ['foo', 'bar', 'bat', 'zip']
        assert mm.all is __all__
        assert mm.deletions == ['foo', 'bar', 'bat', 'zoo']

        # globals with exotic __eq__ must not blow up (or be
        # swept away by) the cleanup scan in mm()
        hostile = HostileEq()
        vectorized = VectorizedEq()

        bar = bat = zoo = 3
        mm()

    assert hasattr(PointlessClass, 'hostile')
    assert hasattr(PointlessClass, 'vectorized')
    assert not (hasattr(PointlessClass, 'mm'))
    assert not (hasattr(PointlessClass, 'foo'))
    assert not (hasattr(PointlessClass, 'bar'))
    assert not (hasattr(PointlessClass, 'bat'))
    assert not (hasattr(PointlessClass, 'zoo'))
    assert not (hasattr(PointlessClass, 'export'))
    assert not (hasattr(PointlessClass, 'delete'))

def test_ModuleManager_sweeps_only_itself():
    # each manager cleans up only after itself: calling mm1()
    # must not delete mm2, nor mm2's stored bound methods
    class PointlessClass:
        mm1 = big.ModuleManager()
        export1 = mm1.export

        mm2 = big.ModuleManager()
        export2 = mm2.export

        mm1()

        # mm2 and its method survive mm1's cleanup...
        still_here = (mm2, export2)

        mm2()

    assert not (hasattr(PointlessClass, 'mm1'))
    assert not (hasattr(PointlessClass, 'export1'))
    assert not (hasattr(PointlessClass, 'mm2'))
    assert not (hasattr(PointlessClass, 'export2'))
    assert hasattr(PointlessClass, 'still_here')

def test_ModuleManager_use_existing_all():
    class PointlessClass:
        __all__ = ['abc']
        mm = big.ModuleManager()

        assert mm.all is __all__

def test_ModuleManager_export_raises_on_duplicates():
    # exporting an already-exported name raises: it's nearly
    # always a bug.  both real-world fingerprints are covered:
    # a stale hand-rolled __all__ that ModuleManager adopted
    # (big.scheduler's bug), and exporting the same name twice
    # (big.text's bug--a stray @export on an internal function).
    # force=True quietly permits the redundancy, and __all__
    # still lists each name once.  delete gets the same rule.
    class PointlessClass:
        mm = big.ModuleManager()
        export = mm.export
        delete = mm.delete

        # same name twice, string form
        export('spam')
        with raises(ValueError) as cm:
            export('spam')
        assert "'spam'" in str(cm.exception)

        # same name twice, decorator form
        @export
        def eggs(): pass
        with raises(ValueError):
            export(eggs)
        # string-then-decorator collides too
        with raises(ValueError):
            export('eggs')

        # force=True permits, and never duplicates
        export('spam', force=True)
        export(eggs, force=True)
        assert mm.all == ['spam', 'eggs']
        # ...and still returns the single argument (decorator
        # protocol preserved)
        assert export(eggs, force=True) is eggs

        # a mid-batch duplicate leaves the earlier names in
        assert mm.all == ['spam', 'eggs']
        with raises(ValueError):
            export('toast', 'spam')
        assert mm.all == ['spam', 'eggs', 'toast']

        # delete: same rule
        delete('spam')
        with raises(ValueError) as cm:
            delete('spam')
        assert "'spam'" in str(cm.exception)
        delete('spam', force=True)
        assert mm.deletions == ['spam']

        spam = 1    # deletions must exist when mm() runs
        mm()

def test_ModuleManager_adopted_all_collision_raises():
    # big.scheduler's exact fingerprint: a hand-rolled __all__
    # survives a conversion to ModuleManager, and @export of a
    # name on that list must raise instead of doubling it.
    class PointlessClass:
        __all__ = ['legacy']
        mm = big.ModuleManager()

        with raises(ValueError) as cm:
            mm.export('legacy')
        assert "'legacy'" in str(cm.exception)

        mm.export('legacy', force=True)
        assert __all__ == ['legacy']


def test_register_and_access_by_attribute():
    """Classes can be registered and accessed as attributes."""


    registry = ClassRegistry()

    @registry()
    class Foo:
        pass

    assert registry.Foo is Foo

def test_register_with_custom_name():
    """Classes can be registered with a custom name."""


    registry = ClassRegistry()

    @registry('CustomName')
    class Foo:
        pass

    assert registry.CustomName is Foo
    assert 'Foo' not in registry

def test_attribute_assignment_writes_through():
    """Attribute assignment/deletion store into the dict,
    for symmetry with attribute access."""
    registry = ClassRegistry()

    class Foo:
        pass

    registry.Thing = Foo
    assert registry['Thing'] is Foo
    assert registry.Thing is Foo

    del registry.Thing
    assert 'Thing' not in registry
    with raises(AttributeError):
        del registry.Thing

def test_decorating_without_parentheses_raises():
    """@registry (no parens) must fail loudly, not silently
    replace the class with an internal function."""
    registry = ClassRegistry()

    with raises(TypeError) as cm:
        @registry
        class Foo:
            pass
    assert 'parentheses' in str(cm.exception)

def test_attribute_error_for_missing():
    """Accessing missing attribute raises AttributeError."""


    registry = ClassRegistry()

    with raises(AttributeError) as cm:
        registry.NonExistent
    assert str(cm.exception) == 'NonExistent'

def test_use_for_inheritance():
    """Registry can be used for cross-scope inheritance."""


    base = ClassRegistry()

    @base()
    class Parent:
        x = 1

    class Child(base.Parent):
        y = 2

    assert issubclass(Child, Parent)
    assert Child.x == 1
    assert Child.y == 2

def test_dict_operations_still_work():
    """Registry still works as a dict."""


    registry = ClassRegistry()

    @registry()
    class Foo:
        pass

    assert 'Foo' in registry
    assert len(registry) == 1
    assert list(registry.keys()) == ['Foo']
    assert list(registry.values()) == [Foo]


def test_literal_eval_plain_str():
    # plain str in, plain result out--identical to ast.literal_eval
    for text in ('"abc"', "'abc'", '123', '3.5', '(1, 2)', '[1, 2]',
                 "{'a': 1}", 'None', 'True', "b'bytes'", '"a\\tb"'):
        value = big.literal_eval(text)
        assert value == ast.literal_eval(text)
        assert type(value) is not string

def test_literal_eval_non_str_results():
    # big.string in, non-str result out: returned untouched
    for text, expected in (('123', 123), ('3.5', 3.5), ('(1, 2)', (1, 2)),
                           ('None', None), ("b'xy'", b'xy')):
        value = big.literal_eval(string(text, source='test.pky'))
        assert value == expected
        assert type(value) is not string

def test_literal_eval_verbatim_slice():
    # no escapes: the result is a true slice of the source
    s = string('key = "hello world"\n', source='test.pky')
    token = s[6:19]     # '"hello world"'
    value = token.literal_eval()
    assert value == 'hello world'
    assert type(value) is string
    assert value.where == 'test.pky line 1 column 8'
    assert str(value.context) == ('key = "hello world"\n'
        '       ^^^^^^^^^^^')

def test_literal_eval_empty_string():
    s = string('x = ""\n', source='test.pky')
    value = s[4:6].literal_eval()
    assert value == ''
    assert type(value) is string

def test_literal_eval_raw_string():
    # raw string: contents are verbatim, tier 1 applies
    s = string(r"a = r'\n'" + "\n", source='test.pky')
    value = s[4:9].literal_eval()
    assert value == '\\n'
    assert type(value) is string
    assert value.where == 'test.pky line 1 column 7'

def test_literal_eval_triple_quoted():
    s = string('"""two\nlines"""', source='test.pky')
    value = big.literal_eval(s)
    assert value == 'two\nlines'
    assert type(value) is string
    assert value.where == 'test.pky line 1 column 4'
    assert value[4:].where == 'test.pky line 2 column 1'

def test_literal_eval_escapes():
    # escapes: spliced result, every character reports a true position
    s = string('greeting = "hi\\tthere"\n', source='test.pky')
    token = s[11:22]    # '"hi\tthere"'
    value = token.literal_eval()
    assert value == 'hi\tthere'
    assert type(value) is string
    # the whole value starts at the 'h'
    assert value.where == 'test.pky line 1 column 13'
    # the decoded tab reports the position of its escape sequence
    assert value[2].where == 'test.pky line 1 column 15'
    # 't' of 'there' follows the two-character escape sequence
    assert value[3].where == 'test.pky line 1 column 17'
    # spliced result is not contiguous: context is unavailable
    assert not (value.context)

def test_literal_eval_escape_flavors():
    for literal, expected in (
        (r'"a\x41b"',    'aAb'),
        ('"a\\u0041b"',  'aAb'),
        (r'"a\U00000041b"', 'aAb'),
        (r'"a\N{LATIN SMALL LETTER A}b"', 'aab'),
        (r'"a\101b"',    'aAb'),        # octal
        (r'"a\'b"',      "a'b"),
        (r"'a\"b'",      'a"b'),
        ('"a\\\nb"',     'ab'),         # line continuation
        (r'"a\\b"',      'a\\b'),       # escaped backslash
    ):
        s = string(literal, source='test.pky')
        value = big.literal_eval(s)
        assert value == expected, f"literal: {literal!r}"
        assert type(value) is string, f"literal: {literal!r}"
        assert value.source == 'test.pky', f"literal: {literal!r}"

def test_literal_eval_escape_first():
    # value starting with an escape: position comes from the escape
    s = string('"\\tx"', source='test.pky')
    value = big.literal_eval(s)
    assert value == '\tx'
    assert value.where == 'test.pky line 1 column 2'

def test_literal_eval_declines_provenance():
    # when the decoded value can't be honestly mapped back onto the
    # source, literal_eval returns a plain str: no provenance beats
    # false provenance.

    # implicit concatenation: the value 'ab' appears nowhere in the
    # source, and there's no position it could truthfully claim
    s = string('"a" "b"', source='test.pky', line_number=5, column_number=9)
    value = big.literal_eval(s)
    assert value == 'ab'
    assert type(value) is str

    # an *escaped* literal with a trailing comment: ast.literal_eval
    # accepts it, but the comment blocks the splice tier, and the
    # quoted-rescue tier requires the contents to match the value
    # exactly--which escapes prevent.  test with the decoded value
    # both present in and absent from the source text; they guard
    # against different mistakes.

    # here the ö is spelled \u00f6 in the literal, but the decoded
    # value 'foö' *does* appear in the source--in the comment!
    # rescuing provenance from there would be a lie.
    s = string(r'"fo\u00f6" # foö', source='foo.py', line_number=2)
    value = big.literal_eval(s)
    assert value == 'foö'
    assert type(value) is str

    # and here the decoded value appears nowhere in the source:
    # any big.string result would necessarily lie about at least
    # one character's position.
    s = string(r'"fo\u00f6" # nope', source='foo.py', line_number=2)
    value = big.literal_eval(s)
    assert value == 'foö'
    assert type(value) is str

    # ordinary escapes get the same treatment: the comment blocks
    # the splice, the escape blocks the rescue
    s = string(r'"a\tb" # c', source='test.pky')
    value = big.literal_eval(s)
    assert value == 'a\tb'
    assert type(value) is str

def test_literal_eval_quoted_rescue():
    # the third tier: if the source opens with a quoted string whose
    # contents are *exactly* the decoded value, that segment--parsed
    # by big's own split_quoted_strings--is a true slice of the
    # source, even with trailing text after the literal.  the
    # comparison is the proof: this can't be confidently wrong.

    # an escape-free literal with a trailing comment: provenance
    # rescued, with true positions and working context
    s = string(r'"foö" # foö', source='foo.py', line_number=2)
    value = big.literal_eval(s)
    assert value == 'foö'
    assert type(value) is string
    assert value.where == 'foo.py line 2 column 2'
    assert [str(c.where) for c in value] == [
        'foo.py line 2 column 2',
        'foo.py line 2 column 3',
        'foo.py line 2 column 4',
        ]
    assert value.context   # a contiguous slice, so context works

    # triple-quoted, spanning lines, still rescued
    s = string('"""two\nlines""" # c', source='t.pky')
    value = big.literal_eval(s)
    assert value == 'two\nlines'
    assert type(value) is string
    assert value.where == 't.pky line 1 column 4'

    # the other delimiter inside the value is fine
    s = string('\'a"b\' # c', source='t.pky')
    value = big.literal_eval(s)
    assert value == 'a"b'
    assert type(value) is string

    # an unpaired quote in the comment doesn't confuse the rescue
    # (split_quoted_strings is lazy; the first segment is complete
    # before the parser ever reaches the comment)
    s = string('"a" # don\'t', source='t.pky')
    value = big.literal_eval(s)
    assert value == 'a'
    assert type(value) is string
    assert value.where == 't.pky line 1 column 2'

def test_literal_eval_leading_whitespace():
    s = string('   "abc"', source='test.pky')
    value = big.literal_eval(s)
    assert value == 'abc'
    assert value.where == 'test.pky line 1 column 5'

def test_literal_eval_errors_propagate():
    for bad in ('not a literal', '"unterminated', 'f"x{1}"', ''):
        with raises((ValueError, SyntaxError)):
            big.literal_eval(string(bad, source='test.pky'))


def run_tests(run=None):
    (run or bigtestlib.run)(name="big.builtin", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
