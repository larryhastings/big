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

from big.all import CycleError, TopologicalSorter
import itertools


def _parse(nodes_and_dependencies):
    args = []
    for line in nodes_and_dependencies.strip().split("\n"):
        line = line.strip()
        if (not line) or line.startswith("#"):
            continue
        a = line.split()
        args.append(a)
    return args

def parse(nodes_and_dependencies):
    args = _parse(nodes_and_dependencies)
    graph = TopologicalSorter()
    for a in args:
        graph.add(*a)
    return graph

tests_run = 0

def permute_tests(nodes_and_dependencies, result, *, remove="", cycle=None):
    global tests_run

    args = _parse(nodes_and_dependencies)

    # we try every ordering of adding the nodes
    # and, if there are removals, for each of those
    #    we try every ordering of the removals
    for args in itertools.permutations(args):
        if remove:
            remove_iterator = itertools.permutations(remove)
        else:
            remove_iterator = (None,)
        for removals in remove_iterator:
            graph = TopologicalSorter()
            for a in args:
                graph.add(*a)
            if removals:
                for s in removals:
                    graph.remove(s)

            if cycle:
                c = graph.cycle()
                assert set(graph.cycle()) == set(cycle), f"{graph.cycle()} != {cycle}"
                return

            assert not (graph.cycle())
            yielded = []
            while graph:
                ready = graph.ready()
                assert ready
                yielded.extend(ready)
                graph.done(*ready)
            got = "".join(sorted(yielded))
            assert got == result, f"expected result={result} is not equal to got={got!r}"
            tests_run += 1


def test_simple_cycle():
    permute_tests("A A", cycle="A", result="A")

nodes_and_dependencies = """
    A
    B   A
    C   A
    D   B C
    X   A B C D
    E   C D X
    Y   C D X E
    """

def test_basic_graph():
    permute_tests(nodes_and_dependencies, result="ABCDEXY")

def test_with_removal():
    permute_tests(nodes_and_dependencies, remove="XY", result="ABCDE")

nodes_and_dependencies_with_cycle = nodes_and_dependencies + """
    F   B
    A   F
    """
def test_complex_cycle():
    permute_tests(nodes_and_dependencies_with_cycle, cycle="ABF", result="ABCDE")

def test_complex_cycle_with_removal():
    permute_tests(nodes_and_dependencies_with_cycle, remove="CDX", cycle="ABF", result="ABCDE")

def test_removals():
    permute_tests("""
        A
        B   A
        C   B A
        D   C B A
        E   D C B A
        """, remove="DBC", result="AE")

def test_incoherence():
    # test view incoherence:
    # if you add an edge A-1, where 1 depends on A,
    # the view is coherent only if one of these statements is true:
    #   * 1 has not been yielded, or
    #   * A has been marked as done.
    global tests_run

    for predecessor_state in range(3):
        for successor_state in range(3):
            for delete_predecessor in (False, True):
                g = TopologicalSorter()

                if predecessor_state != 0:
                    g.add("A")
                if successor_state != 0:
                    g.add("1")

                v = g.view()
                ready = v.ready()
                if predecessor_state != 0:
                    assert 'A' in ready
                if successor_state != 0:
                    assert '1' in ready

                if predecessor_state == 2:
                    v.done("A")
                if successor_state == 2:
                    v.done("1")

                if predecessor_state == 0:
                    g.add("A")
                if successor_state == 0:
                    g.add("1")

                g.add('1', "A")

                should_be_coherent = (
                    (predecessor_state == 2)
                    or
                    (successor_state == 0)
                    )

                try:
                    bool(v)
                    coherent = True
                except RuntimeError:
                    coherent = False

                # print(f"predecessor_state={predecessor_state} successor_state={successor_state} should_be_coherent={should_be_coherent} coherent={coherent}")
                # g._default_view.print()
                # print()

                assert should_be_coherent == coherent, f"test 1 predecessor_state={predecessor_state} successor_state={successor_state} should_be_coherent={should_be_coherent} coherent={coherent}"
                tests_run += 1

                if coherent:
                    continue

                # now delete one of the two nodes and assert that the graph is returned to coherence
                g.remove("A" if delete_predecessor else '1')
                bool(v)
                v.close()
                tests_run += 1

def generate_groups():
    # first, build a list of the groups we get from an iterator
    g = parse(nodes_and_dependencies)
    g_groups = []
    while g:
        r = g.ready()
        g_groups.append(r)
        g.done(*r)
    return g, g_groups

def test_reset():
    global tests_run
    g, g_groups = generate_groups()
    # test reset()
    g.reset()
    for i, r in enumerate(g_groups, 1):
        r2 = g.ready()
        assert r == r2, f"failed at step {i}: r={r!r} != r2={r2}"
        g.done(*r2)
        tests_run += 1

def test_mutation():
    # test mutating the graph while iterating over it.
    # we add unrelated nodes at each step while walking the graph
    # and see that they're returned in proper order.
    global tests_run
    g, g_groups = generate_groups()

    # adding this empty tuple lets the test work even after we run out
    # of the original nodes we added (when we add 1 and 2 right at the end).
    g_groups.append(())

    for step in range(len(g_groups)):
        g = parse(nodes_and_dependencies)
        i = 0
        while g:
            if i == step:
                g.add("2", "1")
            r = g.ready()
            assert set(g_groups[i]) <= set(r), f"set(g_groups[i])={set(g_groups[i])} isn't <= set(r){set(r)}"
            if i == step:
                assert '1' in r, f"1 not in r={r}"
            elif i == (step + 1):
                assert '2' in r, f"2 not in r={r}"
            g.done(*r)
            i += 1
        tests_run += 1

def test_copy():
    g, g_groups = generate_groups()
    g2 = g.copy()
    order1 = g.static_order()
    order2 = g2.static_order()
    assert list(order1) == list(order2)

def test_view_copy():
    # a view's copy duplicates the view's current state
    g = TopologicalSorter()
    g.add('b', 'a')
    g.add('c', 'b')
    v = g.view()
    ready = v.ready()
    assert set(ready) == {'a'}
    v.done('a')

    v2 = v.copy()
    # both views agree on what's ready now...
    assert set(v2.ready()) == {'b'}
    assert set(v.ready()) == {'b'}
    # ...and advance independently afterward
    v2.done('b')
    assert set(v2.ready()) == {'c'}
    assert set(v.ready()) == set()

def test_copy_views_are_independent():
    # regression: copy() used to register the clone's views on the
    # original graph (and leave two orphaned views on the clone),
    # so mutating either graph after a copy corrupted the other's views.
    g = TopologicalSorter()
    g.add('b', 'a')
    clone = g.copy()

    # adds to the clone must be visible to views the clone hands out
    clone.add('z')
    v = clone.view()
    assert 'z' in v.ready()
    v.close()

    # adds to the original must NOT leak into the clone
    g.add('q')
    assert 'q' not in clone.ready()
    assert 'q' in g.ready()

    # every view registered on a graph must point back at that graph
    for graph in (g, clone):
        for view in graph.views:
            assert view.graph is graph

def test_copy_preserves_dirty_flag():
    # regression: copy() didn't copy the dirty flag, so a copy of a
    # graph containing a cycle skipped cycle detection--ready()
    # returned () forever instead of raising CycleError.
    g = TopologicalSorter()
    g.add('a', 'b')
    g.add('b', 'a')          # cycle
    clone = g.copy()
    assert clone.dirty
    with raises(CycleError):
        clone.ready()

    # and copying a clean graph keeps the clone clean
    g2 = TopologicalSorter()
    g2.add('b', 'a')
    list(g2.static_order())  # clears any dirt via cycle check
    clone2 = g2.copy()
    assert clone2.dirty == g2.dirty

def test_done_rejects_duplicate_nodes():
    # regression: done('a', 'a') used to mark 'a' done twice,
    # double-decrementing its successors' predecessor counts--on a
    # diamond, c came ready while b was still outstanding.
    g = TopologicalSorter()
    g.add('c', 'a', 'b')
    assert set(g.ready()) == {'a', 'b'}
    with raises(ValueError) as cm:
        g.done('a', 'a')
    assert 'more than once' in str(cm.exception)

    # the failed call must not have changed anything: 'a' is still
    # yielded, and c only comes ready after BOTH a and b are done
    g.done('a')
    assert g.ready() == ()
    g.done('b')
    assert g.ready() == ('c',)

def test_done_invalid_node_is_atomic():
    # a validation failure anywhere in the call must leave the
    # view untouched (validation happens before any mutation)
    g = TopologicalSorter()
    g.add('b', 'a')
    assert g.ready() == ('a',)
    with raises(ValueError):
        g.done('a', 'never-added')
    g.done('a')                        # 'a' must still be doable
    assert g.ready() == ('b',)

def test_static_order_closes_its_view():
    # regression: static_order never closed its view, so every call
    # left a zombie view registered on the graph--memory that never
    # went away, and every future add() paid to notify it.
    g = TopologicalSorter()
    g.add('b', 'a')
    baseline = len(g.views)

    # fully-consumed run
    list(g.static_order())
    assert len(g.views) == baseline

    # abandoned mid-iteration
    gen = g.static_order()
    next(gen)
    gen.close()
    assert len(g.views) == baseline

    # escaped via CycleError
    g.add('a', 'b')     # cycle
    with raises(CycleError):
        list(g.static_order())
    assert len(g.views) == baseline

def test_cycle_locator_is_linear():
    # regression: the cycle-locating DFS had no "finished" set, so
    # acyclic diamond regions were re-explored once per distinct
    # path--exponential.  (This 79-node graph took ~40 seconds.)
    # We count descents instead of timing: the DFS calls iter() on
    # a node's successors dict once per descent.
    class CountingDict(dict):
        iterations = 0
        def __iter__(self):
            CountingDict.iterations += 1
            return super().__iter__()

    g = TopologicalSorter()
    g.add('cyc1', 'cyc2')
    g.add('cyc2', 'cyc1')          # 2-cycle feeding the ladder
    g.add('L0a', 'cyc1')
    g.add('L0b', 'cyc1')
    prev = ('L0a', 'L0b')
    for i in range(1, 26):         # diamond ladder, ~2**26 paths
        join = f'J{i}'
        g.add(join, *prev)
        a, b = f'L{i}a', f'L{i}b'
        g.add(a, join)
        g.add(b, join)
        prev = (a, b)

    for value in g.nodes.values():
        value[1] = CountingDict(value[1])

    found = g.cycle()
    assert set(found) == {'cyc1', 'cyc2'}
    # linear: on the order of one descent per node--not one per path
    assert CountingDict.iterations < len(g.nodes) * 4

def test_internal_views_cannot_be_closed():
    # the graph depends on its default view and stock view; closing
    # them used to be allowed, permanently crippling the graph with
    # baffling errors.  they're _InternalView now: close() raises.
    g = TopologicalSorter()
    g.add('b', 'a')
    for view in (g._default_view, g._stock_view):
        with raises(ValueError) as cm:
            view.close()
        assert "internal view" in str(cm.exception)

    # a defensive "close all my views" sweep can't break the graph
    for view in list(g.views):
        try:
            view.close()
        except ValueError:
            pass
    assert g.ready() == ('a',)
    g.done('a')
    assert g.ready() == ('b',)

    # but views the graph hands out are ordinary and closable,
    # even though they're copied from the internal stock view
    v = g.view()
    assert v.ready() == ('a',)
    v.close()
    with raises(ValueError):
        v.ready()

def test_len():
    g, g_groups = generate_groups()
    assert len(g) == 7

def test_empty_graph_is_false():
    g = TopologicalSorter()
    assert not (g)

def test_empty_graph_is_empty():
    g = TopologicalSorter()
    assert list(g.static_order()) == []

def test_copying_incoherent_view():
    g = TopologicalSorter()
    g.add('B', 'A')
    g.add('C', 'A')
    g.add('D', 'B', 'C')
    ready = g.ready()
    assert ready == ('A',)
    g.add('A', 'D')
    with raises(RuntimeError):
        bool(g)
    g2 = g.copy()
    with raises(RuntimeError):
        bool(g2)
    with raises(RuntimeError):
        g2.ready()
    with raises(RuntimeError):
        g2.done('A')

def test_cycle():
    g = TopologicalSorter()
    g.add('B', 'A')
    g.add('C', 'A')
    g.add('D', 'B', 'C')
    assert g.cycle() == None
    # coverage test, we return when the dirty bit isn't set
    assert g.cycle() == None

def test_remove():
    g = TopologicalSorter()
    g.add('B', 'A')
    g.add('C', 'A')
    g.add('D', 'B', 'C')
    assert list(g.static_order()) == ['A', 'B', 'C', 'D']
    g.remove('D')
    assert list(g.static_order()) == ['A', 'B', 'C']
    with raises(ValueError):
        g.remove('Q')


def test_close():
    g = TopologicalSorter()
    v = g.view()
    v.close()
    with raises(ValueError):
        bool(v)
    with raises(ValueError):
        bool(v.ready())
    with raises(ValueError):
        bool(v.done('A'))
    with raises(ValueError):
        bool(v.reset())
    with raises(ValueError):
        bool(v.close())

def test_print():
    output = ""
    def print(*a, end="\n", sep=" "):
        nonlocal output
        output += sep.join(str(o) for o in a) + end

    g, g_groups = generate_groups()
    v = g.view()
    v.print(print=print)
    assert 'nodes' in output
    assert 'ready' in output
    assert 'yielded' in output
    assert 'done' in output
    assert 'conflict' in output

def test_manually_constructed_graph():
    # this isn't a supported API
    # but this test will make coverage happy.
    g = TopologicalSorter()
    v = TopologicalSorter.View(g)
    assert not (v)
    with raises(ValueError):
        v2 = TopologicalSorter.View({})




#
# Reusing graphlib tests
#
import big.graph
graphlib = big.graph

import sys
sys.modules['graphlib'] = graphlib

try:
    import test
    from test import test_graphlib
    # the API has changed and they are now invalid.
    t = test.test_graphlib.TestTopologicalSort
    for fn_name in """
        test_calls_before_prepare
        test_prepare_multiple_times
        test_prepare_after_pass_out
        """.strip().split():
        if hasattr(t, fn_name):
            delattr(t, fn_name)
    have_test_graphlib = True
except ImportError: # pragma: no cover
    have_test_graphlib = False


def run_tests(run=None):
    run = run or bigtestlib.run
    run(name="big.graph", module=__name__, permutations=lambda: tests_run)
    if have_test_graphlib:
        print("Testing big.graph using test.test_graphlib...")
        run(name=None, module="test.test_graphlib")


if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
