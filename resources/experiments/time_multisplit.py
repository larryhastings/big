#!/usr/bin/env python3

_license = """
big
Copyright 2022 Larry Hastings
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


import itertools
from itertools import zip_longest
import re


#
# Two different implementations of multisplit.
# Both produce the same results (though maybe would need work
# to pass the latest version of the test suite).
# multisplit1 is cheap and easy, but wasteful.
# multisplit2 is a more complicated algorithm but
#   does a lot less work.
#
# result: for trivial inputs, multisplit1 can be slightly
# faster.  but once the workload rises even slightly,
# multisplit2 becomes faster.  and the more work you throw
# at it, the wider the performance gap.  since trivial
# inputs are already fast enough, obviously we go with
# the multisplit2 approach.
#

def multisplit1(s, separators):
    """
    Like str.split(), but separators is an iterable
    of strings to separate on.  (separators can be a
    string, in which case multisplit separates on each
    character.)

    multisplit('ab:cd,ef', ':,') => ["ab", "cd", "ef"]
    """
    if not s or not separators:
        return [s]
    if len(separators) == 1:
        return s.split(separators[0])
    splits = []
    while s:
        candidates = []
        for separator in separators:
            split, found, trailing = s.partition(separator)
            if found:
                candidates.append((len(split), split, trailing))
        if not candidates:
            break
        candidates.sort()
        _, fragment, s = candidates[0]
        splits.append(fragment)
    splits.append(s)
    return splits


def multisplit2(s, separators):
    """
    Like str.split(), but separators is an iterable of strings to separate on.
    (If separators is a string, multisplit separates on each character
    separately in the string.)

    Returns a list of the substrings, split by the separators.

    Example:
        multisplit('ab:cd,ef', ':,')
    returns
        ["ab", "cd", "ef"]
    """
    if not s or not separators:
        return [s]

    # candidates is a sorted list of lists.  each sub-list contains:
    #   [ first_appearance_index, separator_string, len_separator ]
    # since the lowest appearance is sorted first, you simply split
    # off based on candidates[0], shift all the first_appearance_indexes
    # down by how much you lopped off, recompute the first_appearance_index
    # of candidate[0]'s separator_string, re-sort, and do it again.
    # (you remove a candidate when there are no more appearances in
    # the string--when "".find returns -1.)
    candidates = []
    for separator in separators:
        index = s.find(separator)
        if index != -1:
            candidates.append([index, separator, len(separator)])

    if not candidates:
        return [s]
    if len(candidates) == 1:
        return s.split(candidates[0])

    candidates.sort()
    splits = []

    while True:
        assert s
        # print(f"\n{s=}\n{candidates=}\n{splits=}")
        index, separator, len_separator = candidates[0]
        segment = s[:index]
        splits.append(segment)
        new_start = index + len_separator
        s = s[new_start:]
        # print(f"{new_start=} new {s=}")
        for candidate in candidates:
            candidate[0] -= new_start
        index = s.find(separator)
        if index < 0:
            # there aren't any more appearances of candidate[0].
            if len(candidates) == 2:
                # once we remove candidate[0],
                # we'll only have one candidate separator left.
                # so just split normally on that separator and exit.
                #
                # note: this is the only way to exit the loop.
                # we always reach it, because at some point
                # there's only one candidate left.
                splits.extend(s.split(candidates[1][1]))
                break
            candidates.pop(0)
        else:
            candidates[0][0] = index
            candidates.sort()

    # print(f"\nfinal {splits=}")
    return splits



with open("alice.in.wonderland.txt", "rt", encoding="utf-8") as f:
    text = f.read()

separators = " ,:\n"
result1 = multisplit1(text, separators)
result2 = multisplit2(text, separators)

assert result1==result2

import timeit

for text, separators, number in (
    ('ab:cd,ef', ':,', 1000000),
    ('abWWcdXXcdYYabZZab', ('ab', 'cd'), 1000000),
    (text[:5000], separators, 1000),
    ):
    result1 = multisplit1(text, separators)
    result2 = multisplit2(text, separators)
    assert result1==result2

    if len(text) > 30:
        summary = repr(text[:25] + "[...]")
    else:
        summary = repr(text)
    print(f"text={summary} {separators=}")
    result1 = timeit.timeit("multisplit1(text, separators)", globals=globals(), number=number)
    result2 = timeit.timeit("multisplit2(text, separators)", globals=globals(), number=number)
    print(f"    multisplit1: {number} executions took {result1}s")
    print(f"    multisplit2: {number} executions took {result2}s")
    print()

