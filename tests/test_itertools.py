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

from big.itertools import *

import big.all as big
import copy
import math
import pickle
import re
import unittest


def test_conventional_iteration():
    pbi = big.PushbackIterator(range(10))
    pbi = iter(pbi)
    values = []
    for i in pbi:
        values.append(i)
        if isinstance(i, str):
            continue
        if i % 2 == 0:
            pbi.push(str(i))
    assert values == [0, '0', 1, 2, '2', 3, 4, '4', 5, 6, '6', 7, 8, '8', 9]


def test_next_and_bool():
    for test_bool in range(2):
        pbi = big.PushbackIterator(range(1))
        expected = 0
        sentinel = object()
        for i in range(2):
            if test_bool:
                assert bool(pbi)
            assert pbi.next(sentinel) == expected
            if test_bool:
                assert not (bool(pbi))
            assert pbi.next(sentinel) == sentinel
            if test_bool:
                assert not (bool(pbi))
            assert pbi.next(sentinel) == sentinel
            if test_bool:
                assert not (bool(pbi))
            # now push something and do it all over again
            expected = 'a'
            pbi.push(expected)


def test_repr():
    pbi = big.PushbackIterator()
    pbi.push(3)
    assert repr(pbi) == "<PushbackIterator i=None stack=[3]>"

def test_dunder_next_raising_stop_iteration():
    # A little white-box testing here to make coverage happy.
    # In order to get __next__ to specifically raise StopIteration,
    # we have to use pbi.next to empty out the iterator.
    pbi = big.PushbackIterator((0,))
    sentinel = object()
    assert pbi.next(sentinel) == 0
    assert pbi.next(sentinel) == sentinel
    for i in pbi:
        assert True == False, "shouldn't reach here! pbi is exhausted!" # pragma: no cover

def test_dunder_next_only_catches_stop_iteration():
    # Regression test.  __next__ used to have a bare except:,
    # which swallowed *any* exception raised by the wrapped
    # iterator--converting it into silent early exhaustion.
    def angry():
        yield 1
        raise ValueError('propagate me')
    pbi = big.PushbackIterator(angry())
    assert next(pbi) == 1
    with raises(ValueError):
        next(pbi)



# --8<-- start big iterator context and filter tests --8<--

def test_length_and_countdown_undefined_means_attributeerror():
    # "undefined" means the same thing for every ctx attribute:
    # AttributeError on access, hasattr() as the capability probe.
    # (length/countdown used to leak TypeError from len().)
    def gen():
        yield 1
        yield 2

    for ctx, o in iterator_context(gen()):
        assert not (hasattr(ctx, 'length'))
        assert not (hasattr(ctx, 'countdown'))
        with raises(AttributeError):
            ctx.length
        with raises(AttributeError):
            ctx.countdown

    # with a sized iterable they work as documented
    for ctx, o in iterator_context([10, 20, 30]):
        assert ctx.length == 3
        assert ctx.countdown == 2 - ctx.index

def test_undefined_survives_pickle_and_copy():
    # regression: pickle and deepcopy reconstruct via __new__,
    # bypassing the singleton guard in __init__--so round-trips
    # minted impostor Undefined instances and "is undefined"
    # tests silently failed downstream.
    assert pickle.loads(pickle.dumps(undefined)) is undefined
    assert copy.copy(undefined) is undefined
    assert copy.deepcopy(undefined) is undefined
    # ...including inside structures
    roundtripped = copy.deepcopy({'x': undefined})
    assert roundtripped['x'] is undefined
    # and the front-door guard still works
    with raises(TypeError):
        Undefined()

def test_iterator_context_promiscuous_eq():
    # regression: the end-of-iteration check compared the lookahead
    # against a sentinel with !=, letting any value with a
    # promiscuous __eq__ (like unittest.mock.ANY) claim to BE the
    # sentinel--silently swallowing the final value.
    class AlwaysEqual:
        def __eq__(self, other): return True
        def __ne__(self, other): return False

    # as the only (and therefore final) value
    results = list(iterator_context([AlwaysEqual()]))
    assert len(results) == 1
    ctx, o = results[0]
    assert ctx.is_first
    assert ctx.is_last

    # in the middle and at the end of a longer sequence
    values = ['a', AlwaysEqual(), 'b', AlwaysEqual()]
    results = list(iterator_context(values))
    assert len(results) == 4
    assert results[1][1] is values[1]
    assert results[3][1] is values[3]
    assert results[3][0].is_last

    # and a HOSTILE __eq__ must not crash the epilogue
    class HostileEq:
        def __eq__(self, other): # pragma: no cover
            # never called--that's what this test proves
            raise RuntimeError("nobody expects the hostile __eq__")

    results = list(iterator_context([HostileEq()]))
    assert len(results) == 1

def test_iterator_context():
    assert repr(undefined) == '<Undefined>'
    with raises(TypeError):
        x = Undefined()

    assert not (undefined)

    # iterator yields zero things:
    # iterator_context should also never yield.
    for ctx, i in iterator_context( [] ): # pragma: nocover
        assert False

    # iterator yields one thing:
    # iterator_context should be is_first *and* is_last.
    for start in range(-2, 5):
        with subtest(start=start):
            first_time = True
            for ctx, o in iterator_context((('abc',)), start):
                assert first_time
                first_time = False

                assert isinstance(ctx, IteratorContext)
                assert ctx.is_first
                assert ctx.is_last

                # the length and countdown properties both cache _length.
                # so, examine length first this time...
                assert ctx.length == 1

                assert ctx.index == start
                assert ctx.countdown == start

                with raises(AttributeError):
                    print(ctx.previous)
                assert ctx.current == o
                with raises(AttributeError):
                    print(ctx.next)

                assert repr(ctx) == f"IteratorContext(iterator=('abc',), start={start}, index={start}, is_first=True, is_last=True, current='abc')"


    for start in range(-2, 5):
        for items in ('abc', 'abcd'):
            with subtest(start=start, items=items):
                buffer = [undefined]
                buffer.extend(items)
                buffer.append(undefined)

                countdowns = []
                indices = []

                is_first = True
                computed_index = start
                computed_countdown = start + len(items) - 1

                for ctx, o in iterator_context(items, start):
                    assert isinstance(ctx, IteratorContext)
                    assert ctx.is_first == is_first
                    is_last = (o == items[-1])
                    assert ctx.is_last == is_last

                    assert ctx.index == computed_index
                    assert ctx.countdown == computed_countdown

                    previous, current, next = buffer[:3]

                    if not is_first:
                        assert ctx.previous == previous
                    else:
                        with raises(AttributeError):
                            print(ctx.previous)
                        assert previous == undefined

                    assert ctx.current == current

                    if not is_last:
                        assert ctx.next == next
                    else:
                        with raises(AttributeError):
                            print(ctx.next)
                        assert next == undefined

                    assert ctx.length == len(items)

                    countdowns.append(ctx.countdown)
                    indices.append(ctx.index)

                    is_first = False
                    computed_index += 1
                    computed_countdown -= 1
                    buffer.pop(0)

                reversed_countdowns = list(countdowns)
                reversed_countdowns.reverse()
                assert reversed_countdowns == indices

def test_stop_at_count_consumes_exactly_count():
    # regression: the quota check ran before yield on the NEXT
    # accepted value, so the source got pulled at least one value
    # past the quota (more, with rejection rules hunting for an
    # accepted value that would then be refused).
    consumed = []
    def source():
        for i in range(100):
            consumed.append(i)
            yield i

    values = list(iterator_filter(source(), stop_at_count=3))
    assert values == [0, 1, 2]
    assert len(consumed) == 3

    # with a whitelist rule: pre-quota rejections are inherent
    # to filtering, but there's no post-quota hunting
    consumed.clear()
    values = list(iterator_filter(source(),
                                  only_predicate=lambda o: o % 2 == 0,
                                  stop_at_count=3))
    assert values == [0, 2, 4]
    assert len(consumed) == 5   # 0,1,2,3,4 -- and not 5,6,...

def test_call_every_timing():
    # regression, twice over: the callback used to fire only while
    # processing the (N+1)th value--so it waited for the SOURCE to
    # produce another value--and when the total was an exact
    # multiple of N, the final call never happened at all.

    # each callback records how many values the source has
    # produced so far; it must be exactly the group boundary,
    # proving the callback didn't wait for value N+1
    produced = []
    calls = []
    def tracking_source():
        for i in range(1, 5):
            produced.append(i)
            yield i

    for v in iterator_filter(tracking_source(),
                             call_every=(lambda: calls.append(len(produced)), 2)):
        pass
    # calls after values 2 and 4 (exact multiple: final call
    # included), each before the source produced anything further
    assert calls == [2, 4]

    # a callback landing exactly on the stop_at_count boundary fires
    calls = []
    list(iterator_filter(iter(range(100)),
                         stop_at_count=4,
                         call_every=(lambda: calls.append(1), 2)))
    assert len(calls) == 2

def test_iterator_filter():
    l = [1, 'a', 2, 'b', 3, 'c', 4, 'd', 5]

    def test(expected, **kwargs):
        got = list(iterator_filter(l, **kwargs))
        assert expected == got

    test([1, 'a', 2, 'b'],         stop_at_value=3)
    test([1, 'a', 2, 'b', 3],      stop_at_in=set(('c', 4, 'd')))
    test([1, 'a', 2, 'b', 3, 'c'], stop_at_predicate=lambda o: o==4)

    test([1, 'a', 2, 'b'], stop_at_count= 4)
    test([1, 'a', 2],      stop_at_count= 3)
    test([1, 'a'],         stop_at_count= 2)
    test([],               stop_at_count= 0)
    test([],               stop_at_count=-1)

    test([1, 'a', 2, 'b', 'c', 4, 'd', 5], reject_value=3)
    test([1, 'a', 2, 'b', 3, 5],           reject_in=set(('c', 4, 'd')))
    test([1, 'a', 2, 'b', 3, 'c', 'd', 5], reject_predicate=lambda o: o==4)

    test([3,],          only_value=3)
    test(['c', 4, 'd'], only_in=set(('c', 4, 'd')))
    test([2, 3, 4, 5],  only_predicate=lambda o: isinstance(o, int) and o > 1)

    seven_threes = (3, 33, 333, 3333, 33333, 333333, 3333333)
    six_threes   = (3, 33, 333, 3333, 33333, 333333)
    five_threes  = (3, 33, 333, 3333, 33333)
    four_threes  = (3, 33, 333, 3333)
    three_threes = (3, 33, 333)
    two_threes   = (3, 33)
    one_three    = (3,)

    class OnlyFourThrees(int):
        def __ne__(self, other):
            return other not in four_threes

    only_four_threes = OnlyFourThrees()

    # now test with all nine rules in play
    def test(l, expected):
        got = list(iterator_filter(l,
            stop_at_value='stop1',
            stop_at_in=set(('stop2', 'stop3', 'stop4')),
            stop_at_predicate=lambda o: o=='stop5',
            stop_at_count=4,

            reject_value=3333333,                 # seven threes
            reject_in=set((333333,)),             # six threes
            reject_predicate=lambda o: o ==33333, # five threes

            only_value=only_four_threes,
            only_in=three_threes,
            only_predicate=lambda o: o in two_threes,
            ))
        assert expected == got

    test([33, 3, 'stop1', 3, 33], [33, 3])
    test([33, 3, 'stop3', 3, 33], [33, 3])
    test([33, 3, 'stop5', 3, 33], [33, 3])

    test([33, 3, 3333333, 3, 33], [33, 3, 3, 33])
    test([33, 3,  333333, 3, 33], [33, 3, 3, 33])
    test([33, 3,   33333, 3, 33], [33, 3, 3, 33])

    test([33, 3,    3333, 3, 33], [33, 3, 3, 33])
    test([33, 3,     333, 3, 33], [33, 3, 3, 33])
    test([33, 3,      33, 3, 33], [33, 3, 33, 3])

    # test exhaustion
    it = iterator_filter(l, stop_at_value=2)
    got = list(it)
    assert got == [1, 'a']
    got = list(it)
    assert got == []
    got = list(it)
    assert got == []

    # regression:
    #       iterator_filter(i, stop_at_count=0)
    #   should *not* iterate over i!
    #   it should start out in an "exhausted" state and never touch i.
    def fail_immediately(): # pragma: nocover
        raise RuntimeError('you should not call next on me!')
        yield 1

    for stop_value in range(-20, 1):
        with subtest(stop_value=stop_value):
            for i in iterator_filter(fail_immediately(), stop_at_count=stop_value): # pragma: nocover
                raise RuntimeError(f"we shouldn't have entered the body of this for loop! i={i!r}")

    values = []
    def append_x():
        values.append('x')

    for i in iterator_filter(range(14), call_every=(append_x, 4)):
        values.append(i)
    assert values == [0, 1, 2, 3, 'x', 4, 5, 6, 7, 'x', 8, 9, 10, 11, 'x', 12, 13]

    with raises(TypeError):
        list(iterator_filter(range(14), call_every=(append_x, 4.5)))
    with raises(ValueError):
        list(iterator_filter(range(14), call_every=(append_x, 0)))
    with raises(ValueError):
        list(iterator_filter(range(14), call_every=(append_x, -1)))


# --8<-- end big iterator context and filter tests --8<--

def run_tests(run=None):
    (run or bigtestlib.run)(name="big.itertools", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
