#!/usr/bin/env python3

_license = """
big
Copyright 2022-2024 Larry Hastings
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

import big.all as big
import pprint
import random
import sys
import unittest


V = Version = big.Version


class BigTestVersion(unittest.TestCase):

    def test_parsing(self):
        def fail(s):
            with self.assertRaises(ValueError):
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
            self.assertIsInstance(Version(s), Version)

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

    def test_version_info(self):
        kwargs = {}
        c = sys.version_info.releaselevel[0]
        if c in 'abc': # pragma: nocover
            kwargs['release_level'] = c
            if sys.version_info.serial:
                kwargs['serial'] = sys.version_info.serial
        self.assertEqual(
            V(sys.version_info),
            V(release=(sys.version_info.major, sys.version_info.minor, sys.version_info.micro), **kwargs)
            )

    def test_normalize(self):
        def test(v1, v2):
            v1 = Version(v1)
            v2 = Version(v2)
            self.assertEqual(v1, v2)
        test('1.0.1', '1.0.1.0')
        test('1.0.1', '1.0.1.0.0.0.0.0.0')
        test('01.0.1', '1.0.1.0.0')
        test('01.0.0001.0', '1.0.1')

        test('15.23alpha1', '15.23a1')
        test('15.23beta1', '15.23beta1')
        test('15.23rc1', '15.23c1')

        self.assertEqual(
            V('1!2.3rc45.post67.dev89+i.am.the.eggman'),
            V(epoch=1, release=(2, 3), release_level='rc', serial=45, post=67, dev=89, local=('i', 'am', 'the', 'eggman'))
            )

        self.assertEqual(
            V('4.5.0b6'),
            V(release=(4, 5), release_level='beta', serial=6)
            )

        self.assertEqual(
            V('88'),
            V(release=(88,))
            )


    def test_comparison(self):

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
            self.assertEqual(v, v2)

        # check that the first version is < every other version in the list
        v1 = sorted_versions[0]
        for v2 in sorted_versions[1:]:
            self.assertLess(v1, v2)

        # check transitivity: every version is < the entry that is <delta> ahead in the list
        for delta in (1, 2, 3, 5, 7):
            for i in range(len(sorted_versions) - delta):
                self.assertLess(sorted_versions[i], sorted_versions[i + delta])

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

            if 0:
                print()
                print("-" * 79)
                print("[scrambled]")
                pprint.pprint(scrambled)
                print()
                print("[expected]")
                pprint.pprint(sorted_versions)
                print()
                print("[got]")
                pprint.pprint(got)

            self.assertEqual(sorted_versions, got)

        v = sorted_versions[0]
        self.assertNotEqual(v, 1.3)
        self.assertNotEqual(v, "abc")

        with self.assertRaises(TypeError):
            v < 1.3
        with self.assertRaises(TypeError):
            v < "abc"


    def test_convert_to_string(self):
        # test everything
        s = '8!1.0.3rc5.post456.dev34+apple.cart.123'
        v = V(s)
        self.assertEqual(s, str(v))
        self.assertEqual("Version('" + s + "')", repr(v))


    def test_input_validation(self):
        with self.assertRaises(ValueError):
            V()
        with self.assertRaises(ValueError):
            V((1, 3, 5))
        with self.assertRaises(ValueError):
            V(5)
        with self.assertRaises(ValueError):
            V(3.2)
        with self.assertRaises(ValueError):
            V(4+3j)
        with self.assertRaises(ValueError):
            V({1, 2, 3})
        with self.assertRaises(ValueError):
            V(b"1.3.5")

        with self.assertRaises(ValueError):
            V(epoch='4', release=(1, 3, 5))
        with self.assertRaises(ValueError):
            V(epoch=-1, release=(1, 3, 5))

        with self.assertRaises(ValueError):
            V(release=1)
        with self.assertRaises(ValueError):
            V(release=1.3)
        with self.assertRaises(ValueError):
            V(release=1+3j)
        with self.assertRaises(ValueError):
            V(release="1.3.5")
        with self.assertRaises(ValueError):
            V(release=[1, 3, 5])
        with self.assertRaises(ValueError):
            V(release=('1', '3', '5'))
        with self.assertRaises(ValueError):
            V(release=(1.0, 3.0, 5.0))

        with self.assertRaises(ValueError):
            V(release_level='', release=(1, 3, 5))
        with self.assertRaises(ValueError):
            V(release_level='abc', release=(1, 3, 5))
        with self.assertRaises(ValueError):
            V(release_level=24, release=(1, 3, 5))
        with self.assertRaises(ValueError):
            V(release_level=-1, release=(1, 3, 5))

        with self.assertRaises(ValueError):
            V(release_level='rc', serial='7', release=(1, 3, 5))
        with self.assertRaises(ValueError):
            V(release_level='rc', serial='', release=(1, 3, 5))
        with self.assertRaises(ValueError):
            V(release_level='rc', serial=-1, release=(1, 3, 5))

        with self.assertRaises(ValueError):
            V(post='334', release=(1, 3, 5))
        with self.assertRaises(ValueError):
            V(post='', release=(1, 3, 5))
        with self.assertRaises(ValueError):
            V(post=-1, release=(1, 3, 5))

        with self.assertRaises(ValueError):
            V(dev='556', release=(1, 3, 5))
        with self.assertRaises(ValueError):
            V(dev='', release=(1, 3, 5))
        with self.assertRaises(ValueError):
            V(dev=-1, release=(1, 3, 5))

        with self.assertRaises(ValueError):
            V(local='abc', release=(1, 3, 5))
        with self.assertRaises(ValueError):
            V(local=1, release=(1, 3, 5))
        with self.assertRaises(ValueError):
            V(local=1.3, release=(1, 3, 5))
        with self.assertRaises(ValueError):
            V(local=["a", "33"], release=(1, 3, 5))
        with self.assertRaises(ValueError):
            V(local=("a", 33), release=(1, 3, 5))
        with self.assertRaises(ValueError):
            V(local=("a", '', 'c'), release=(1, 3, 5))
        with self.assertRaises(ValueError):
            V(local=("a", '33!', 'c'), release=(1, 3, 5))
        with self.assertRaises(ValueError):
            V(local=("a", ' 33', 'c'), release=(1, 3, 5))

        with self.assertRaises(ValueError):
            V("1.3.5", epoch=1)
        with self.assertRaises(ValueError):
            V("1.3.5", release=(1, 3, 5))
        with self.assertRaises(ValueError):
            V("1.3.5", release_level='rc')
        with self.assertRaises(ValueError):
            V("1.3.5", serial=1)
        with self.assertRaises(ValueError):
            V("1.3.5", post=1)
        with self.assertRaises(ValueError):
            V("1.3.5", dev=1)
        with self.assertRaises(ValueError):
            V("1.3.5", local="one.apple.3")

    def test_hashability(self):
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
        if 0:
            print(">> expected")
            pprint.pprint(expected)
            print()
            print(">> got")
            pprint.pprint(got)
            print()
        self.assertEqual(expected, got)

    def test_accessors(self):
        v = V('7!22.33.44rc1.post77.dev22+apple.dumpling_gang-l33t')
        self.assertEqual(v.epoch, 7)
        self.assertEqual(v.release, (22, 33, 44))
        self.assertEqual(v.major, 22)
        self.assertEqual(v.minor, 33)
        self.assertEqual(v.micro, 44)
        self.assertEqual(v.release_level, "rc")
        self.assertEqual(v.releaselevel, "rc")
        self.assertEqual(v.serial, 1)
        self.assertEqual(v.dev, 22)
        self.assertEqual(v.post, 77)
        self.assertEqual(v.local, ("apple", "dumpling", "gang", "l33t"))

        v = V('1.2')
        self.assertEqual(v.epoch, None)
        self.assertEqual(v.release, (1, 2))
        self.assertEqual(v.major, 1)
        self.assertEqual(v.minor, 2)
        self.assertEqual(v.micro, 0)
        self.assertEqual(v.release_level, "final")
        self.assertEqual(v.releaselevel, "final")
        self.assertEqual(v.serial, None)
        self.assertEqual(v.dev, None)
        self.assertEqual(v.post, None)
        self.assertEqual(v.local, None)

        v = V('73')
        self.assertEqual(v.major, 73)
        self.assertEqual(v.minor, 0)


def run_tests():
    bigtestlib.run(name="big.version", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
