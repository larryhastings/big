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
import unittest

from big import TopologicalSorter


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

class TopologicalSortTests(unittest.TestCase):

    def permute_tests(self, nodes_and_dependencies, result, *, remove="", cycle=None):
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
                    self.assertSetEqual(set(graph.cycle()), set(cycle), msg=f"{graph.cycle()} != {cycle}")
                    return

                self.assertFalse(graph.cycle())
                yielded = []
                while graph:
                    ready = graph.ready()
                    self.assertTrue(ready)
                    yielded.extend(ready)
                    graph.done(*ready)
                got = "".join(sorted(yielded))
                self.assertEqual(got, result, msg=f"expected {result=} is not equal to {got!r}")
                tests_run += 1


    def test_simple_cycle(self):
        self.permute_tests("A A", cycle="A", result="A")

    nodes_and_dependencies = """
        A
        B   A
        C   A
        D   B C
        X   A B C D
        E   C D X
        Y   C D X E
        """

    def test_basic_graph(self):
        self.permute_tests(self.nodes_and_dependencies, result="ABCDEXY")

    def test_with_removal(self):
        self.permute_tests(self.nodes_and_dependencies, remove="XY", result="ABCDE")

    nodes_and_dependencies_with_cycle = nodes_and_dependencies + """
        F   B
        A   F
        """
    def test_complex_cycle(self):
        self.permute_tests(self.nodes_and_dependencies_with_cycle, cycle="ABF", result="ABCDE")

    def test_complex_cycle_with_removal(self):
        self.permute_tests(self.nodes_and_dependencies_with_cycle, remove="CDX", cycle="ABF", result="ABCDE")

    def test_removals(self):
        self.permute_tests("""
            A
            B   A
            C   B A
            D   C B A
            E   D C B A
            """, remove="DBC", result="AE")

    def test_incoherence(self):
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
                        self.assertIn('A', ready)
                    if successor_state != 0:
                        self.assertIn('1', ready)

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

                    # print(f"{predecessor_state=} {successor_state=} {should_be_coherent=} {coherent=}")
                    # g._default_view.print()
                    # print()

                    self.assertEqual(should_be_coherent, coherent, msg=f"test 1 {predecessor_state=} {successor_state=} {should_be_coherent=} {coherent=}")
                    tests_run += 1

                    if coherent:
                        continue

                    # now delete one of the two nodes and assert that the graph is returned to coherence
                    g.remove("A" if delete_predecessor else '1')
                    bool(v)
                    v.close()
                    tests_run += 1

    def generate_groups(self):
        # first, build a list of the groups we get from an iterator
        g = parse(self.nodes_and_dependencies)
        g_groups = []
        while g:
            r = g.ready()
            g_groups.append(r)
            g.done(*r)
        return g, g_groups

    def test_reset(self):
        global tests_run
        g, g_groups = self.generate_groups()
        # test reset()
        g.reset()
        for i, r in enumerate(g_groups, 1):
            r2 = g.ready()
            self.assertEqual(r, r2, msg=f"failed at step {i}: {r=} != {r2=}")
            g.done(*r2)
            tests_run += 1

    def test_mutation(self):
        # test mutating the graph while iterating over it.
        # we add unrelated nodes at each step while walking the graph
        # and see that they're returned in proper order.
        global tests_run
        g, g_groups = self.generate_groups()

        # adding this empty tuple lets the test work even after we run out
        # of the original nodes we added (when we add 1 and 2 right at the end).
        g_groups.append(())

        for step in range(len(g_groups)):
            g = parse(self.nodes_and_dependencies)
            i = 0
            while g:
                if i == step:
                    g.add("2", "1")
                r = g.ready()
                self.assertLessEqual(set(g_groups[i]), set(r), f"{set(g_groups[i])=} isn't <= {set(r)=}")
                if i == step:
                    self.assertIn('1', r, msg=f"1 not in {r=}")
                elif i == (step + 1):
                    self.assertIn('2', r, msg=f"2 not in {r=}")
                g.done(*r)
                i += 1
            tests_run += 1

    def test_copy(self):
        g, g_groups = self.generate_groups()
        g2 = g.copy()
        order1 = g.static_order()
        order2 = g2.static_order()
        self.assertEqual(list(order1), list(order2))

    def test_len(self):
        g, g_groups = self.generate_groups()
        self.assertEqual(len(g), 7)

    def test_empty_graph_is_false(self):
        g = TopologicalSorter()
        self.assertFalse(g)

    def test_empty_graph_is_empty(self):
        g = TopologicalSorter()
        self.assertEqual(list(g.static_order()), [])

    def test_copying_incoherent_view(self):
        g = TopologicalSorter()
        g.add('B', 'A')
        g.add('C', 'A')
        g.add('D', 'B', 'C')
        ready = g.ready()
        self.assertEqual(ready, ('A',))
        g.add('A', 'D')
        with self.assertRaises(RuntimeError):
            bool(g)
        g2 = g.copy()
        with self.assertRaises(RuntimeError):
            bool(g2)
        with self.assertRaises(RuntimeError):
            g2.ready()
        with self.assertRaises(RuntimeError):
            g2.done('A')

    def test_cycle(self):
        g = TopologicalSorter()
        g.add('B', 'A')
        g.add('C', 'A')
        g.add('D', 'B', 'C')
        self.assertEqual(g.cycle(), None)
        # coverage test, we return when the dirty bit isn't set
        self.assertEqual(g.cycle(), None)

    def test_remove(self):
        g = TopologicalSorter()
        g.add('B', 'A')
        g.add('C', 'A')
        g.add('D', 'B', 'C')
        self.assertEqual(list(g.static_order()), ['A', 'B', 'C', 'D'])
        g.remove('D')
        self.assertEqual(list(g.static_order()), ['A', 'B', 'C'])
        with self.assertRaises(ValueError):
            g.remove('Q')


    def test_close(self):
        g = TopologicalSorter()
        v = g.view()
        v.close()
        with self.assertRaises(ValueError):
            bool(v)
        with self.assertRaises(ValueError):
            bool(v.ready())
        with self.assertRaises(ValueError):
            bool(v.done('A'))
        with self.assertRaises(ValueError):
            bool(v.reset())
        with self.assertRaises(ValueError):
            bool(v.close())

    def test_print(self):
        output = ""
        def print(*a, end="\n", sep=" "):
            nonlocal output
            output += sep.join(str(o) for o in a) + end

        g, g_groups = self.generate_groups()
        v = g.view()
        v.print(print=print)
        self.assertIn('nodes', output)
        self.assertIn('ready', output)
        self.assertIn('yielded', output)
        self.assertIn('done', output)
        self.assertIn('conflict', output)

    def test_manually_constructed_graph(self):
        # this isn't a supported API
        # but this test will make coverage happy.
        g = TopologicalSorter()
        v = TopologicalSorter.View(g)
        self.assertFalse(v)
        with self.assertRaises(ValueError):
            v2 = TopologicalSorter.View({})




#
# Reusing graphlib tests
#
import big.graph
graphlib = big.graph

import sys
sys.modules['graphlib'] = graphlib

import test
from test import test_graphlib
# the API has changed and they are now invalid.
for fn_name in """
    test_calls_before_prepare
    test_prepare_multiple_times
    """.strip().split():
    delattr(test.test_graphlib.TestTopologicalSort, fn_name)

import bigtestlib

def run_tests(exit=False):
    bigtestlib.run(name="big.graph", module=__name__, permutations=lambda: tests_run)
    print("Testing big.graph using test.test_graphlib...")
    bigtestlib.run(name=None, module="test.test_graphlib")


if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
