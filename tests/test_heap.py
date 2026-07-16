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

import big.all as big
import random


original_values = [
    5,
    1,
    10,
    2,
    20,
    7,
    15,
    25,
    ]


def test_heap_basics():
    h = big.Heap()
    for value in original_values:
        h.append(value)
    values = []
    while h:
        values.append(h.popleft())
    sorted_values = list(sorted(values))
    assert values == sorted_values

def test_heap_preinitialize_and_iteration():
    h2 = big.Heap(original_values)
    assert len(h2) == len(original_values)
    values = list(h2)
    sorted_values = list(sorted(values))
    assert values == sorted_values

def test_dont_modify_during_iteration():
    h = big.Heap(original_values)
    with raises(RuntimeError):
        for value in h:
            h.append(45)
    with raises(RuntimeError):
        for value in h:
            h.extend([44, 55, 66])
    with raises(RuntimeError):
        for value in h:
            h.remove(20)
    with raises(RuntimeError):
        for value in h:
            h.popleft()
    with raises(RuntimeError):
        for value in h:
            h.popleft_and_append(33)
    with raises(RuntimeError):
        for value in h:
            h.append_and_popleft(33)
    with raises(RuntimeError):
        for value in h:
            h.clear()

def test_random_one_liner_methods():
    h = big.Heap()
    assert len(h) == 0
    assert not (h)
    h.extend(original_values)
    assert len(h) == len(original_values)
    assert h
    assert 5 in h
    assert not (6 in h)

    assert h[:3] == [1, 2, 5]
    assert h[:-5] == [1, 2, 5]
    assert h[-3:] == [15, 20, 25]
    assert h[5:] == [15, 20, 25]
    assert h[::2] == [1, 5, 10, 20]

    h2 = h.copy()
    assert h == h2
    assert h.queue == h2.queue
    h2 = big.Heap(original_values)
    assert h == h2
    assert h.queue == h2.queue

    h.clear()
    assert len(h) == 0
    assert not (h)

    h2 = big.Heap()
    assert h == h2

    h.extend((3, 1, 2))
    assert list(h) == [1, 2, 3]
    h.remove(2)
    assert list(h) == [1, 3]
    o = h.append_and_popleft(4)
    assert o == 1
    assert list(h) == [3, 4]
    o = h.append_and_popleft(2)
    assert o == 2
    assert list(h) == [3, 4]
    o = h.popleft_and_append(2)
    assert o == 3
    assert list(h) == [2, 4]

    with raises(TypeError):
        h[1.5]
    with raises(TypeError):
        h['abc']



def test_getitem():
    h = big.Heap(original_values)
    assert h[0] == 1
    assert h[1] == 2
    assert h[-1] == 25
    assert h[-2] == 20
    assert h[0:4] == [1, 2, 5, 7]
    assert h[-4:] == [10, 15, 20, 25]
    sorted_values = sorted(original_values)
    assert h[:] == sorted_values
    assert h[:] == h.queue

def test_eq_returns_notimplemented_for_foreign_types():
    # regression: __eq__ returned False for non-Heap operands,
    # blocking the reflected comparison--a foreign type that
    # knows how to compare against Heap never got asked.
    h = big.Heap([1, 2, 3])

    class KnowsHeaps:
        def __eq__(self, other):
            return isinstance(other, big.Heap)

    assert h == KnowsHeaps()     # reflected __eq__ honored
    assert KnowsHeaps() == h

    # ordinary non-Heap comparisons are unchanged
    assert not (h == [1, 2, 3])
    assert h != [1, 2, 3]
    assert h == big.Heap([3, 2, 1])

def test_iterator_is_itself_iterable():
    # regression: HeapIterator had no __iter__, so holding the
    # iterator broke: "for x in iter(heap)" raised TypeError,
    # as did zip(iter(heap), ...) and anything else that
    # re-iter()s an iterator.
    h = big.Heap([3, 1, 2])

    it = iter(h)
    assert iter(it) is it      # the protocol's literal rule

    collected = list(it)
    assert collected == [1, 2, 3]

    # partial consumption, then a for loop picks up the remainder
    it = iter(h)
    assert next(it) == 1
    assert list(it) == [2, 3]

    # and zip re-iter()s its arguments
    assert list(zip(iter(h), iter(h))) == [(1, 1), (2, 2), (3, 3)]

def test_getitem_matches_sorted_list_everywhere():
    # regression: heap[-3] through heap[-9] returned wrong values--
    # the small-negative fast path indexed nlargest's *descending*
    # list with the original negative index.  (heap[-2] was
    # accidentally correct, which is how this survived.)
    # So: sweep EVERY valid index, positive and negative, across
    # sizes spanning all the fast paths and the sorted fallback.
    r = random.Random(83)
    for size in (1, 2, 3, 9, 10, 11, 25):
        data = [r.randrange(1000) for _ in range(size)]
        h = big.Heap(data)
        expected = sorted(data)
        for i in range(-size, size):
            assert h[i] == expected[i], f'heap[{i}] wrong for size {size}'
        # out-of-range raises IndexError, like a list
        with raises(IndexError):
            h[size]
        with raises(IndexError):
            h[-size - 1]

    # empty heaps raise IndexError for every int index, like a list
    # (regression: empty[-1] raised ValueError, from max())
    empty = big.Heap()
    for i in (0, 1, -1, -2, 15, -15):
        with raises(IndexError):
            empty[i]

def test_reprs():
    h = big.Heap(original_values)
    assert repr(h)[:6] == '<Heap '
    assert 'first=1' in repr(h)
    assert repr(iter(h))[:20] == '<HeapIterator <Heap '

    # regression: repr of an empty heap raised IndexError
    empty = big.Heap()
    assert 'len=0' in repr(empty)
    assert 'first=' not in repr(empty)
    # first= uses repr, so strings are quoted
    assert "first='a'" in repr(big.Heap(['a', 'b']))

def run_tests(run=None):
    (run or bigtestlib.run)(name="big.heap", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
