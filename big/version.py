#!/usr/bin/env python3

"""
The big package is a grab-bag of cool code for use in your programs.

Think big!
"""

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

#
# This is based on reading PEP 440:
#        https://peps.python.org/pep-0440/
# and the updated version at PyPI, the "version-specifiers" doc:
#        https://packaging.python.org/en/latest/specifications/version-specifiers/


import itertools
import math
import re
import sys


_release_level_allowed_values = ('alpha', 'beta', 'rc', 'final')
_release_level_normalize = {'a': 'alpha', 'b': 'beta', 'c': 'rc', 'pre': 'rc', 'preview': 'rc'}
_release_level_to_integer = {'alpha': -3, 'beta': -2, 'rc': -1, 'final': 0}
_release_level_to_str = {'alpha': 'a', 'beta': 'b', 'rc': 'rc', 'final': ''}

_sys_version_info_type = type(sys.version_info)
_sys_version_info_release_level_normalize = { 'alpha': 'a', 'beta': 'b', 'candidate': 'rc', 'final': ''}

#
# regular expression is straight out of PEP 440.
#

VERSION_PATTERN = r"^\s*" + r"""
    v?
    (?:
        (?:(?P<epoch>[0-9]+)!)?                           # epoch
        (?P<release>[0-9]+(?:\.[0-9]+)*)                  # release segment
        (?P<pre>                                          # pre-release
            [-_\.]?
            (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))
            [-_\.]?
            (?P<pre_n>[0-9]+)?
        )?
        (?P<post>                                         # post release
            (?:-(?P<post_n1>[0-9]+))
            |
            (?:
                [-_\.]?
                (?P<post_l>post|rev|r)
                [-_\.]?
                (?P<post_n2>[0-9]+)?
            )
        )?
        (?P<dev>                                          # dev release
            [-_\.]?
            (?P<dev_l>dev)
            [-_\.]?
            (?P<dev_n>[0-9]+)?
        )?
    )
    (?:\+(?P<local>[a-z0-9]+(?:[-_\.][a-z0-9]+)*))?       # local version
""" + r"\s*$"

_re_parse_version = re.compile(VERSION_PATTERN, re.VERBOSE | re.IGNORECASE).match

del VERSION_PATTERN

_re_is_valid_local_segment = re.compile("^[A-Za-z0-9]+$").match



class Version:
    def __init__(self, s=None, *, epoch=None, release=None, release_level=None, serial=None, post=None, dev=None, local=None):
        """
        Constructs a `Version` object, which represents a version number.

        You may define the version one of two ways:

        * by passing in a string to the `s` positional parameter specifying the version.
          Example: `Version("1.3.5rc3")`
        * by passing in keyword-only arguments setting the specific fields of the version.
          Example: `Version(release=(1, 3, 5), release_level="rc", serial=3)`

        This object conforms to the PEP 440 version scheme,
        parsing version strings using the PEP's official regular
        expression.

        For more detailed information, see big's README file.
        """
        if s is None:
            if release is None:
                raise ValueError("you must specify either a version string or explicit keyword arguments")

            if epoch is None:
                epoch = 0
            elif not (isinstance(epoch, int) and (epoch >= 0)):
                raise ValueError(f"epoch must be non-negative int or None, not {epoch!r}")

            if not (isinstance(release, tuple) and release and all(isinstance(element, int) for element in release)):
                raise ValueError(f"release must be a tuple of length 1+ containing only ints, not {release!r}")

            original_release_level = release_level
            if release_level is None:
                release_level = 'final'
            if not (release_level in _release_level_allowed_values):
                raise ValueError(f"release_level {release_level!r} must be one of 'alpha', 'beta', 'rc', 'final', or None")

            if serial is None:
                serial = 0
            elif not (isinstance(serial, int) and (serial >= 0)):
                raise ValueError(f"serial must be non-negative int or None, not {serial!r}")

            if not ((post is None) or (isinstance(post, int) and (post >= 0))):
                raise ValueError(f"post must be non-negative int or None, not {post!r}")

            if not ((dev is None) or (isinstance(dev, int) and (dev >= 0))):
                raise ValueError(f"dev must be non-negative int or None, not {dev!r}")

            if not ((local is None) or (isinstance(local, tuple) and local and all(isinstance(element, str) and element and _re_is_valid_local_segment(element) for element in local))):
                raise ValueError(f"local must be None or a tuple of length 1+ containing only non-empty strings of letters and digits, not {local!r}")

        else:
            if (
                   (epoch != None)
                or (release != None)
                or (release_level != None)
                or (serial != None)
                or (post != None)
                or (dev != None)
                or (local != None)
                ):
                raise ValueError('you cannot specify both a version string and keyword arguments')

            if isinstance(s, _sys_version_info_type):
                # support the Python sys.version_info object!
                s2 = f"{s.major}.{s.minor}.{s.micro}"
                rl = _sys_version_info_release_level_normalize[s.releaselevel]
                if rl: # pragma: nocover
                    s2 += rl
                    if s.serial:
                        s2 += f"{s.serial}"
                s = s2

            if not isinstance(s, str):
                raise ValueError("you must specify either a version string or explicit keyword arguments")

            match = _re_parse_version(s)
            if not match:
                raise ValueError(f"invalid version initializer {s!r}") from None

            # groups furnished by the version-parsing regular expression
            # "epoch"
            # "release", release segment
            # "pre", pre-release
            #    also split up into "pre_l" (pre label, must be 'a'|'b'|'c'|'rc'|'alpha'|'beta'|'pre'|'preview', a==alpha, b==beta, c/pre/review==rc) and "pre_n" (pre number)
            # "post", post release
            #    also split up into "post_n1" (post first number), "post_l" (post label, must be 'post'|'rev'|'r' which are all equivalent), and "post_n2" (post second number)
            #    either "post_n1" is set, or "post_l" and "post_n2" are set.
            # "dev", dev release
            #    also split up into "dev_l" (must be 'dev') and "dev_n" (dev number)
            # "local", local version

            d = match.groupdict()
            get = d.get

            # if an optional value is not None, and we expect it to be an int,
            # the regular expression guarantees that it's a parsable int,
            # so we don't need to guard against ValueError etc.

            # if they didn't supply a value, e.g. there's no epoch in the string,
            # I go ahead and store a None for the attribute.

            epoch = get('epoch')
            epoch = int(epoch) if epoch is not None else None

            release = [int(_) for _ in get('release').split('.')]
            # if S is a release string, and T is S+".0",
            # S and T represent the same version.
            # so, let's clip off all trailing zero elements on release.
            while (len(release) > 1) and (not release[-1]):
                release.pop()
            release = tuple(release)

            release_level = get('pre_l')
            if release_level is None:
                release_level = 'final'
            release_level = _release_level_normalize.get(release_level, release_level)
            # don't need to validate this, it's constrained by the regex
            # if release_level not in _release_level_allowed_values:
            #     raise ValueError(f"release_level string must be 'alpha' or 'a', 'beta' or 'b', 'rc' or 'c' or 'pre' or 'preview', or 'final', or unspecified, not {release_level!r}")
            assert release_level in _release_level_allowed_values

            serial = get('pre_n')
            if (release_level == 'final'):
                assert serial is None
            serial = int(serial) if serial is not None else None

            post_l = get('post_l')
            post_n1 = get('post_n1')
            post_n2 = get('post_n2')
            if post_n1 is not None:
                assert (post_l is None) and (post_n2 is None)
                post = post_n1
            elif post_n2 is not None:
                assert post_l is not None
                post = post_n2
            else:
                post = None

            post = int(post) if post is not None else None

            dev_l = get('dev_l')
            dev = get('dev_n')
            if dev is not None:
                assert dev_l is not None
            dev = int(dev) if dev is not None else None

            local = original_local = get('local')
            if local is not None:
                local = tuple(local.replace('-', '.').replace('_', '.').split('.'))

        if local:
            # if local is true, it's an iterable of strings.
            # convert elements to ints where possible, leave as strings otherwise.
            compare_local = tuple((2, int(element)) if element.isdigit() else (1, element) for element in local)
        else:
            local = None
            compare_local = ()

        self._epoch = epoch
        self._release = release
        self._str_release = ".".join(str(element) for element in release)
        self._release_level = release_level
        self._serial = serial
        self._post = post
        self._dev = dev
        self._local = local

        # when ordering:
        #     epoch
        #     release
        #     alpha < beta < rc < final
        #     post, if you have no post you are < a release that has a post
        #     dev, if you have no dev you are > a release that has a dev
        #     local, which is... complicated
        #
        # The version-specifiers document says basically everywhere
        # (epoch, serial, post, dev) that if they don't specify a number,
        # the number is implicitly 0.  see these sections:
        #     "Version epochs"
        #     "Implicit pre-release number" (what I'm calling "serial")
        #     "Implicit development release number"
        #     "Implicit post release number"
        #
        # I infer that to mean that "1.0.dev" and "1.0.dev0" are the same version.
        # But!  "1.0" is *definitely* later than "1.0.dev0".
        #
        # Here's how I handle that: if they didn't specify "field",
        # I'll have a None for that attribute.  I substitute the following value
        # in the comparison tuple.  Ready?
        #
        #       field  |  tuple value
        #       -------+-------
        #       epoch  |  0
        #       serial |  0
        #       dev    |  math.inf
        #       post   | -1
        #
        # What's going on with "dev"?  Any "dev" version is earlier than any
        # non-"dev" version, but ".dev33" < ".dev34".
        #
        # And, with "post", any release with a "post" is later than any
        # release with no "post".

        if epoch is None:
            epoch = 0
        release_level = _release_level_to_integer[release_level]
        if serial is None:
            serial = 0
        if dev is None:
            dev = math.inf
        if post is None:
            post = -1
        self._tuple = (epoch, release, release_level, serial, post, dev, compare_local)

    def __repr__(self):
        return f"Version({str(self)!r})"

    def __str__(self):
        text = []
        append = text.append

        if self._epoch:
            append(f"{self._epoch}!")
        append(self._str_release)

        release_level = _release_level_to_str.get(self._release_level)
        if not release_level:
            assert not self._serial
        else:
            append(release_level)
            if self._serial:
                append(str(self._serial))

        if self._post is not None:
            append(f".post{self._post}")

        if self._dev is not None:
            append(f".dev{self._dev}")

        if self._local:
            append("+")
            append(".".join(self._local))

        return "".join(text)

    def __eq__(self, other):
        if not isinstance(other, Version):
            return False
        return self._tuple == other._tuple

    def __lt__(self, other):
        if not isinstance(other, Version):
            raise TypeError("'<' not supported between instances of 'Version' and '{type(other)}'")
        return self._tuple < other._tuple


    def __hash__(self):
        return (
            hash(self._epoch)
            ^ hash(self._release)
            ^ hash(self._release_level)
            ^ hash(self._serial)
            ^ hash(self._post)
            ^ hash(self._dev)
            ^ hash(self._local)
            )

    @property
    def epoch(self):
        return self._epoch

    @property
    def release(self):
        return self._release

        self._release_level = release_level
        self._serial = serial
        self._post = post
        self._dev = dev or 0
        self._local = local

    @property
    def major(self):
        return self._release[0]

    @property
    def minor(self):
        if len(self._release) <= 1:
            return 0
        return self._release[1]

    @property
    def micro(self):
        if len(self._release) <= 2:
            return 0
        return self._release[2]

    @property
    def release_level(self):
        return self._release_level

    # alias for python's stinky non-PEP8 spelling
    @property
    def releaselevel(self):
        return self._release_level

    @property
    def serial(self):
        return self._serial

    @property
    def post(self):
        return self._post

    @property
    def dev(self):
        return self._dev

    @property
    def local(self):
        return self._local

__all__ = ['Version']
