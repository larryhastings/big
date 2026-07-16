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

from big import test
from big.test import raises, raises_regex

import big.all as big
import random
import sys


V = Version = big.Version


def test_parsing():
    def fail(s):
        with raises(ValueError):
            Version(s)

    fail("!")
    fail("-3")
    fail("3.")
    fail("3.-4")
    fail("3.14.")
    fail("3.14.-15")
    fail("3.14.15alpha!0")
    fail("3.14.15alpha/0")
    fail("3.14.15alpha0!")
    fail("3.14.15alpha0.")
    fail("3.14.15alpha0x")
    fail("3.14.15alphax0")
    fail("3.14.15blah")
    fail("3.14.15final")
    fail("3.14.15x")
    fail("3.14x")
    fail("3x")
    fail("x")
    fail("x3")

    def work(s):
        assert isinstance(Version(s), Version)

    work("0")
    work("03")
    work("3")
    work("3.0")
    work("3.04")
    work("3.14.15")
    work("3.14.15alpha")
    work("3.14.15alpha0")
    work("3.14.15alpha022")
    work("3.14.15alpha05")
    work("3.14.15alpha22")
    work("3.14.15alpha5")
    work("3.14.15beta")
    work("3.14.15rc")
    work("3.4")

def test_version_info():
    # compute a version object from Python's version the easy way
    easy = V(sys.version_info)
    assert easy == sys.version_info

    less = V(f"{sys.version_info.major}.{sys.version_info.minor - 1}")
    assert less < sys.version_info

    greater = V(f"{sys.version_info.major}.{sys.version_info.minor + 1}")
    assert greater > sys.version_info

    # now do it the hard way
    release = [sys.version_info.major, sys.version_info.minor]
    if sys.version_info.micro: # pragma: nocover
        release.append(sys.version_info.micro)
    release = tuple(release)

    kwargs = {}
    release_level = big.version._sys_version_info_release_level_normalize.get(sys.version_info.releaselevel, sys.version_info.releaselevel)
    if release_level: # pragma: nocover
        kwargs['release_level'] = release_level
    if sys.version_info.serial: # pragma: nocover
        kwargs['serial'] = sys.version_info.serial

    hard = V(release=release, **kwargs)

    assert easy == hard

def test_packaging_version():
    try: # pragma: nocover
        from packaging.version import Version as PV

        pv135 = PV('1.3.5')
        v = V(pv135)
        assert v == pv135
        pv136 = PV('1.3.6')
        assert v < pv136

    except ImportError: # pragma: nocover
        pass


def test_normalize():
    def test(v1, v2):
        v1 = Version(v1)
        v2 = Version(v2)
        assert v1 == v2
    test('1.0.1', '1.0.1.0')
    test('1.0.1', '1.0.1.0.0.0.0.0.0')
    test('01.0.1', '1.0.1.0.0')
    test('01.0.0001.0', '1.0.1')

    test('15.23alpha1', '15.23a1')
    test('15.23beta1', '15.23beta1')
    test('15.23rc1', '15.23c1')

    parsed = V('1!2.3rc45.post67.dev89+i.am.the.eggman')
    constructed = V(epoch=1, release=(2, 3), release_level='rc', serial=45, post=67, dev=89, local=('i', 'am', 'the', 'eggman'))
    assert parsed == constructed

    parsed = V('4.5.0b6')
    constructed = V(release=(4, 5), release_level='beta', serial=6)
    assert parsed == constructed

    parsed = V('88')
    constructed = V(release=(88,))
    assert parsed == constructed


def test_comparison_foreign_types():
    # regression: __lt__ used to raise directly, with an
    # f-string missing its f (the message literally printed
    # '{type(other)}'), and __eq__ returned False for foreign
    # types.  both now return NotImplemented: Python raises
    # the standard, correctly-formatted TypeError for
    # unhandled ordering, and reflected comparisons get their
    # chance, per the data model.
    with raises(TypeError) as cm:
        V("1.0") < "1.0"
    assert "{type(other)}" not in str(cm.exception)
    assert "str" in str(cm.exception)

    assert not (V("1.0") == "1.0")
    assert V("1.0") != "1.0"
    assert V("1.0").__eq__("1.0") is NotImplemented
    assert V("1.0").__lt__("1.0") is NotImplemented

    class VersionLike:
        def __eq__(self, other):
            return True
        def __gt__(self, other):
            return True
    assert V("1.0") == VersionLike()   # reflected __eq__
    assert V("1.0") < VersionLike()    # reflected __gt__

def test_comparison():

    # here's a list of version, already in sorted order.
    sorted_versions = [
        V('1.0a1'),
        V('1.0a2.dev456'),
        V('1.0a2'),
        V('1.0a2-456'), # post
        V('1.0b1.dev456'),
        V('1.0b2'),
        V('1.0b2.post345'),
        V('1.0c1.dev456'),
        V('1.0rc1'),
        V('1.0.dev456'),
        V('1.0'),
        V('1.0.post456.dev34'),
        V('1.0.post456.dev34+abc.123'),
        V('1.0.post456.dev34+abc.124'),
        V('1.0.post456.dev34+abd'),
        V('1.0.post456.dev34+abd.123'),
        V('1.0.post456.dev34+1'),
        V('1.0.post456'),
        V('1.0.1'),
        V('1.0.1.1'),
        V('1.0.2'),
        V('1!0.0.0.0.1'),
        V('2!0.0.0.0.0.1'),
        ]

    # first--let's test round-tripping through repr!
    for v in sorted_versions:
        r = repr(v)
        v2 = eval(r)
        assert v == v2

    # check that the first version is < every other version in the list
    v1 = sorted_versions[0]
    for v2 in sorted_versions[1:]:
        assert v1 < v2

    # check transitivity: every version is < the entry that is <delta> ahead in the list
    for delta in (1, 2, 3, 5, 7):
        for i in range(len(sorted_versions) - delta):
            assert sorted_versions[i] < sorted_versions[i + delta]

    # scramble a copy of the array, using a couple fixed seeds,
    # then sort it and confirm that the array is identical to the original (sorted) array
    for seed in (
        'seed1',
        'seed2',
        "T'was brillig, and the slithey toves",
        "Lookin' over their shoulder for me", # Stan Ridgway, "Newspapers"
        "And I've tasted the strongest meats / And laid them down in golden sheets", # Peter Gabriel, "Back In NYC"
        "And if I want more love in the world / I must show more love to myself / 'Cause I want to change the world", # Todd Rundgren, "Change Myself"
        "My momma tells me every day, not to move so fast across the room", # "Shorty And The EZ Mouse"
        ):
        r = random.Random(seed)
        scrambled = sorted_versions.copy()
        r.shuffle(scrambled)
        got = list(scrambled)
        got.sort()

        assert sorted_versions == got

    v = sorted_versions[0]
    assert v != 1.3
    assert v != "abc"

    with raises(TypeError):
        v < 1.3
    with raises(TypeError):
        v < "abc"


def test_convert_to_string():
    # test everything
    s = '8!1.0.3rc5.post456.dev34+apple.cart.123'
    v = V(s)
    got = str(v)
    assert s == got
    got = repr(v)
    assert got == "Version('" + s + "')"

def test_format():
    v = V('8!1.0.3rc5.post456.dev34+apple.cart.123')
    assert v.format('{release}') == '1.0.3'
    assert v.format('{epoch}') == '8'
    assert v.format('{release_level}') == 'rc'


def test_input_validation():
    # regression: a nonzero serial with a (defaulted or
    # explicit) 'final' release_level used to construct
    # happily, then blow an assert in __str__ (and under
    # python -O, silently print a wrong version).
    with raises_regex(ValueError, "serial requires a non-final release_level"):
        V(release=(1, 2), serial=3)
    with raises_regex(ValueError, "serial requires a non-final release_level"):
        V(release=(1, 2), release_level='final', serial=3)
    # serial=0 carries no information and stays legal
    assert str(V(release=(1, 2), serial=0)) == "1.2"
    # and a serial with a pre-release level round-trips
    assert str(V(release=(1, 2), release_level='rc', serial=3)) == "1.2rc3"

    with raises(ValueError):
        V()
    with raises(ValueError):
        V((1, 3, 5))
    with raises(ValueError):
        V(5)
    with raises(ValueError):
        V(3.2)
    with raises(ValueError):
        V(4+3j)
    with raises(ValueError):
        V({1, 2, 3})
    with raises(ValueError):
        V(b"1.3.5")

    with raises(ValueError):
        V(epoch='4', release=(1, 3, 5))
    with raises(ValueError):
        V(epoch=-1, release=(1, 3, 5))

    with raises(ValueError):
        V(release=1)
    with raises(ValueError):
        V(release=1.3)
    with raises(ValueError):
        V(release=1+3j)
    with raises(ValueError):
        V(release="1.3.5")
    with raises(ValueError):
        V(release=[1, 3, 5])
    with raises(ValueError):
        V(release=('1', '3', '5'))
    with raises(ValueError):
        V(release=(1.0, 3.0, 5.0))

    with raises(ValueError):
        V(release_level='', release=(1, 3, 5))
    with raises(ValueError):
        V(release_level='abc', release=(1, 3, 5))
    with raises(ValueError):
        V(release_level=24, release=(1, 3, 5))
    with raises(ValueError):
        V(release_level=-1, release=(1, 3, 5))

    with raises(ValueError):
        V(release_level='rc', serial='7', release=(1, 3, 5))
    with raises(ValueError):
        V(release_level='rc', serial='', release=(1, 3, 5))
    with raises(ValueError):
        V(release_level='rc', serial=-1, release=(1, 3, 5))

    with raises(ValueError):
        V(post='334', release=(1, 3, 5))
    with raises(ValueError):
        V(post='', release=(1, 3, 5))
    with raises(ValueError):
        V(post=-1, release=(1, 3, 5))

    with raises(ValueError):
        V(dev='556', release=(1, 3, 5))
    with raises(ValueError):
        V(dev='', release=(1, 3, 5))
    with raises(ValueError):
        V(dev=-1, release=(1, 3, 5))

    with raises(ValueError):
        V(local='abc', release=(1, 3, 5))
    with raises(ValueError):
        V(local=1, release=(1, 3, 5))
    with raises(ValueError):
        V(local=1.3, release=(1, 3, 5))
    with raises(ValueError):
        V(local=["a", "33"], release=(1, 3, 5))
    with raises(ValueError):
        V(local=("a", 33), release=(1, 3, 5))
    with raises(ValueError):
        V(local=("a", '', 'c'), release=(1, 3, 5))
    with raises(ValueError):
        V(local=("a", '33!', 'c'), release=(1, 3, 5))
    with raises(ValueError):
        V(local=("a", ' 33', 'c'), release=(1, 3, 5))

    with raises(ValueError):
        V("1.3.5", epoch=1)
    with raises(ValueError):
        V("1.3.5", release=(1, 3, 5))
    with raises(ValueError):
        V("1.3.5", release_level='rc')
    with raises(ValueError):
        V("1.3.5", serial=1)
    with raises(ValueError):
        V("1.3.5", post=1)
    with raises(ValueError):
        V("1.3.5", dev=1)
    with raises(ValueError):
        V("1.3.5", local="one.apple.3")

def test_hashability():
    versions = set()
    for s in """
        1.1.22
        2.5.post88
        2.4.0
        2.4.1
        2.2.1.dev24
        2.3.5rc3
        2.4
        2.3.5rc3
        2.4.0.0.0
        02.04.000
        3!0.5

    """.strip().split():
        v = V(s)
        versions.add(v)

    got = list(versions)
    got.sort()

    expected = [
        V("1.1.22"),
        V("2.2.1.dev24"),
        V("2.3.5rc3"),
        V("2.4.0"),
        V("2.4.1"),
        V("2.5.post88"),
        V("3!0.5")
        ]
    assert expected == got

def test_equal_versions_hash_equal():
    # regression: __hash__ used to hash the raw attributes,
    # where None != 0, while __eq__ compares the normalized
    # comparison tuple--so these pairs were equal but hashed
    # differently, breaking set and dict membership.
    pairs = (
        ("1.0", "0!1.0"),       # implicit vs explicit epoch 0
        ("1.0a", "1.0a0"),      # implicit vs explicit pre-release number
        ("1.0.dev", "1.0.dev0"),# implicit vs explicit dev number
        ("1.0", "v1.0"),
        ("1.0", "1.0.0.0"),
        )
    for a, b in pairs:
        va, vb = V(a), V(b)
        assert va == vb, (a, b)
        assert hash(va) == hash(vb), (a, b)
        assert len({va, vb}) == 1, (a, b)
        assert vb in {va: 1}, (a, b)

def test_accessors():
    v = V('7!22.33.44rc1.post77.dev22+apple.dumpling_gang-l33t')
    assert v.epoch == 7
    assert v.release == (22, 33, 44)
    assert v.major == 22
    assert v.minor == 33
    assert v.micro == 44
    assert v.release_level == "rc"
    assert v.releaselevel == "rc"
    assert v.serial == 1
    assert v.dev == 22
    assert v.post == 77
    assert v.local == ("apple", "dumpling", "gang", "l33t")

    v = V('1.2')
    assert v.epoch is None
    assert v.release == (1, 2)
    assert v.major == 1
    assert v.minor == 2
    assert v.micro == 0
    assert v.release_level == "final"
    assert v.releaselevel == "final"
    assert v.serial is None
    assert v.dev is None
    assert v.post is None
    assert v.local is None

    v = V('73')
    assert v.major == 73
    assert v.minor == 0


def test_version_info_synthetic():
    # Version supports sys.version_info--but which of its branches
    # run depends on the interpreter you happen to be running: a
    # release build never has a truthy releaselevel, a beta build
    # always does.  sys.version_info's type refuses instantiation,
    # so, white-box: temporarily swap the module's
    # _sys_version_info_type for a namedtuple workalike and test
    # every flavor deterministically, on every interpreter.
    import collections
    fake_type = collections.namedtuple('fake_version_info',
        ('major', 'minor', 'micro', 'releaselevel', 'serial'))
    saved = big.version._sys_version_info_type
    big.version._sys_version_info_type = fake_type
    try:
        # candidate + serial; candidate without serial; final
        assert V(fake_type(3, 12, 0, 'candidate', 1)) == V('3.12.0rc1')
        assert V(fake_type(3, 12, 0, 'candidate', 0)) == V('3.12.0rc')
        assert V(fake_type(3, 12, 0, 'final', 0)) == V('3.12.0')
        # a releaselevel the normalize table doesn't know passes
        # through to the parser as-is
        assert V(fake_type(3, 15, 0, 'beta', 3)) == V('3.15.0b3')
        # the comparison methods recognize the type too
        assert V('3.12.0rc1') == fake_type(3, 12, 0, 'candidate', 1)
        assert V('3.12.0rc1') < fake_type(3, 12, 0, 'final', 0)
    finally:
        big.version._sys_version_info_type = saved

def test_packaging_version_interop():
    # Version interoperates with packaging.version.Version objects,
    # found via sys.modules--never imported.  Inject a stand-in
    # module, so this works on every interpreter without installing
    # packaging.  The stand-in Version deliberately is NOT a str
    # subclass: neither is the real one, and the constructor's
    # packaging branch is guarded by "not isinstance(s, str)"--an
    # is-a-str fake would sail past it and parse as an ordinary
    # string.  All big relies on is str(version_object).
    import types as stdlib_types

    class FakeVersion:
        def __init__(self, s):
            self.s = s
        def __str__(self):
            return self.s

    # save and remove any real packaging.version--the full suite may
    # have imported it, a standalone run hasn't.  (branch-free save
    # and restore: whether it was there mustn't affect coverage.)
    saved = {k: v for k, v in sys.modules.items() if k == 'packaging.version'}
    sys.modules.pop('packaging.version', None)
    try:
        # with packaging.version absent from sys.modules, foreign
        # objects are simply not versions: __eq__ offers the
        # reflected comparison, ordering raises
        assert not (V('1.2.3') == FakeVersion('1.2.3'))
        with raises(TypeError):
            V('1.2.3') < FakeVersion('1.2.3')

        module = stdlib_types.ModuleType('packaging.version')
        module.Version = FakeVersion
        sys.modules['packaging.version'] = module

        v = FakeVersion('1.2.3')
        assert V(v) == V('1.2.3')          # the constructor accepts it
        assert V('1.2.3') == v             # __eq__ recognizes it
        assert V('1.2.2') < v              # __lt__ recognizes it
        assert not (V('9') == v)
    finally:
        sys.modules.pop('packaging.version', None)
        sys.modules.update(saved)

# the stand-in above proves the mechanics on every interpreter; this
# proves them against the genuine article, when it's installed.
# ("packaging" is one of big's test dependencies, so it should be--
# but the suite still passes without it, this test simply isn't
# defined.  find_spec instead of try/import: it returns None for a
# missing module rather than raising, so no-packaging environments
# don't leave an uncoverable except branch.)
import importlib.util
_have_packaging = importlib.util.find_spec('packaging') is not None

if _have_packaging:
    def test_real_packaging_version_interop():
        import packaging.version
        v = packaging.version.Version('1.2.3rc1')
        assert V(v) == V('1.2.3rc1')       # the constructor accepts it
        assert V('1.2.3rc1') == v          # __eq__ recognizes it
        assert V('1.2.3rc0') < v           # __lt__ recognizes it
        assert not (V('9') == v)
        # the exotic PEP 440 fields survive the round-trip too
        v = packaging.version.Version('1!2.3.post4.dev5+local.6')
        assert V(v) == V('1!2.3.post4.dev5+local.6')


def run_tests(run=None):
    (run or test.run)(name="big.version", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    test.finish()
