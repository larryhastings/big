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


#
# TODO
#
# * change _default_view to lazily initialize from _stock_view?
#

from collections import defaultdict

try:
    from graphlib import CycleError
except ImportError: # pragma: no cover
    class CycleError(ValueError):
        """
        Exception thrown by TopologicalSorter when it detects a cycle.
        """
        pass

__all__ = ["TopologicalSorter", "CycleError"]



nodes_dict_default = lambda: [0, {}]

class TopologicalSorter:
    """
    An object representing a directed graph of nodes.

    See Python's graphlib.TopologicalSorter for concepts
    and the basic API.

    https://docs.python.org/3/library/graphlib.html#graphlib.TopologicalSorter
    """

    class View:
        """
        A view on a TopologicalSorter graph object.
        Allows iterating over the nodes of the graph
        in dependency order.
        """
        def __init__(self, graph, *, original=None):
            if not isinstance(graph, TopologicalSorter):
                raise ValueError("invalid graph")

            self.graph = graph
            self.graph.views.append(self)

            self._conflicts = defaultdict(set)
            self._reverse_conflicts = defaultdict(set)

            if original is not None:
                self._predecessors = original._predecessors.copy()
                self._ready = original._ready.copy()
                self._yielded = original._yielded.copy()
                self._done = original._done.copy()

                for n, v in original._conflicts.items():
                    self._conflicts[n] = v.copy()
                for n, v in original._reverse_conflicts.items():
                    self._reverse_conflicts[n] = v.copy()
                return

            # self._predecessors maps nodes to their
            # predecessor count in the local view.
            # we use this to discover ready nodes.
            self._predecessors = {}

            # self._ready is the set of currently-ready nodes.
            # they haven't been returned by ready() yet.
            self._ready = []

            # _yielded and _done are sets, because
            # they're definitely faster as sets,
            # and their ordering (or lack thereof)
            # doesn't affect the behavior of the view.

            # self._yielded is the set of nodes
            # yielded to the user by ready().
            self._yielded = set()

            # self._done is the set of nodes
            # returned from the user by done().
            self._done = set()

        def __repr__(self):
            return f"<View {hex(id(self))} on graph={hex(id(self.graph))} {self._ready=} yielded={len(self._yielded)} done={len(self._done)} conflicts={bool(self._conflicts)}>"

        def copy(self):
            """
            Returns a shallow copy of the view, duplicating its current state.
            """
            return self.__class__(self.graph, original=self)

        def reset(self):
            """
            Resets the view to its initial state,
            forgetting all "ready" and "done" state.
            """
            if self.graph is None:
                raise ValueError("TopologicalSorter view is already closed")
            self._predecessors.clear()
            self._predecessors.update(self.graph._stock_view._predecessors)
            self._ready.clear()
            self._ready.extend(self.graph._stock_view._ready)
            self._yielded.clear()
            self._done.clear()
            self._conflicts.clear()
            self._reverse_conflicts.clear()

        def close(self):
            """
            Closes the view.  A closed view can no longer be used.
            """
            if self.graph is None:
                raise ValueError("TopologicalSorter view is already closed")

            self.graph.views.remove(self)
            self.graph = None

            del self._predecessors
            del self._ready
            del self._yielded
            del self._done
            del self._conflicts
            del self._reverse_conflicts

        def __bool__(self):
            """
            Returns `True` if more work can be done in the
            view--if there are nodes waiting to be yielded by
            `get_ready`, or waiting to be returned by `done`.
            """
            if self.graph is None:
                raise ValueError("TopologicalSorter view has already been closed")
            if self._conflicts:
                raise RuntimeError("TopologicalSorter view is incoherent to the graph")
            return len(self._done) < len(self.graph.nodes)

        def ready(self):
            """
            Returns an iterable of all the nodes that
            currently have no dependencies.
            """
            if self.graph is None:
                raise ValueError("TopologicalSorter view has already been closed")
            if self._conflicts:
                raise RuntimeError("TopologicalSorter view is incoherent to the graph")
            if self.graph.dirty:
                self.graph.check_for_cycles()
            self._yielded.update(self._ready)
            ready = list(self._ready)
            self._ready.clear()
            return tuple(ready)

        def done(self, *nodes):
            """
            Marks nodes returned by ready as "done",
            possibly allowing additional nodes to be available
            from ready.
            """
            if self.graph is None:
                raise ValueError("TopologicalSorter view has already been closed")
            if self._conflicts:
                raise RuntimeError("TopologicalSorter view is incoherent to the graph")
            for node in nodes:
                if node not in self.graph.nodes:
                    raise ValueError(f"node {node!r} was not added using add()")
                if node not in self._yielded:
                    raise ValueError(f"node {node!r} was not passed out")
                # print("CALL _mark_node_done", node, self.graph.nodes[node])
                self._mark_node_done(node, self.graph.nodes[node][1])
            nodes = set(nodes)
            self._done |= nodes
            self._yielded -= nodes

        #
        # These functions are internal only.
        # They're a private API between the graph
        # and the views on the graph, or just internal
        # to the view itself.
        #
        # They're not public APIs, and it's not
        # supported for anyone but the graph to call them.
        #
        # In particular, they are optimized for exactly what
        # the graph needs to communicate to the views.
        # They aren't good general-purpose APIs and shouldn't
        # be used by any code outside this file.
        #
        # That enough warnings for you?  Don't touch!  I mean it!
        #
        def _add_nodes(self, nodes):
            """
            event: nodes have been added to the graph.
            "nodes" is an iterable of newly added nodes.

            Called *after* the nodes are initially added to the graph.
            All these nodes have already been added to the graph,
            and already have all their initial successors.

            We call _add_successor after this to notify about new successors.
            """
            for node in nodes:
                self._predecessors[node] = 0
                self._ready.append(node)

        def _add_successor(self, node, successor):
            """
            Called *after* the graph is updated.
            successor is guaranteed to be a new successor to node.
            """

            # CAPITAL LETTER is the predecessor node
            # single digit is the successor node
            # lowercase letter is the result
            #
            # so, A-1, 1 depends on A
            #
            # ---------
            # A  1  not yet yielded by ready (not ready, or waiting to be yielded by ready)
            # B  2  yielded by ready but not yet marked done
            # C  3  done
            # ---------
            #
            #   1__2__3
            # A|o* x  x
            # B|o* x  x
            # C|o* o  o
            #
            # o = ok!
            # x = not ok, view is incoherent.
            # * = if 1 was previously waiting in "ready", it's removed.

            conflicted = not (
                (node in self._done)
                or ((successor not in self._done)
                    and (successor not in self._yielded)) )
            if conflicted:
                # print("CONFLICT", node, successor, self._done)
                self._conflicts[node].add(successor)
                self._reverse_conflicts[successor].add(node)

            if successor not in self._done:
                self._predecessors[successor] += 1
                if self._predecessors[successor] == 1:
                    try:
                        # why "try" here?
                        # successor might be yielded or done.
                        # (in which case we must be conflicted.)
                        self._ready.remove(successor)
                    except ValueError:
                        pass
        def _remove_node(self, node, successors):
            """
            Called *after* the node is removed from the graph.
            The node is guaranteed to have been added to the view,
            either with _add_nodes, or was brought over by copy().
            """
            # print(f"{self=} _remove_node {node=} {successors=}")
            if (node in self._conflicts) or (node in self._reverse_conflicts):
                # print("REMOVE vYHS", node)
                for this, other in (
                    (self._conflicts, self._reverse_conflicts),
                    (self._reverse_conflicts, self._conflicts)
                    ):
                    values = this.get(node, ())
                    if values:
                        del this[node]
                        for v in values:
                            other[v].discard(node)
                            if not other[v]:
                                del other[v]

            if node in self._done:
                self._done.remove(node)
                return

            if node in self._ready:
                self._ready.remove(node)
            self._yielded.discard(node)

            self._predecessors.pop(node)

            self._mark_node_done(node, successors)

        def _mark_node_done(self, node, successors):
            """
            Does *not* update _done or _yielded.
            """
            # print(f"{self=} _mark_node_done {node=} {successors=}")

            # this "for" statement is why successors is a dict, not a set.
            # when iterating over a dict, you see the elements in insertion order.
            # when iterating over a set, you see the elements in random order.
            # by using a dict, the object's behavior is more stable,
            # which can definitely make debugging easier.
            for successor in successors:
                if (successor in self._yielded) or (successor in self._done):
                    continue
                self._predecessors[successor] -= 1
                if not self._predecessors[successor]:
                    self._ready.append(successor)
            # print(f"_mark_node_done done. {self=}")

        def print(self, print=print):
            """
            Prints the internal state of the view, and its graph.
            Used for debugging.

            print is the function used for printing;
            it should behave identically to the builtin print function.
            """
            print(self)
            print("      _ready:", sorted(self._ready))
            print("    _yielded:", sorted(self._yielded))
            print("       _done:", sorted(self._done))
            print("  _conflicts:", dict(self._conflicts))
            self.graph.print(print=print)
            print()

    def __bool__(self):
        """
        Returns True if more work can be done in the
        default view--if there are nodes waiting to be yielded
        by get_ready, or waiting to be returned by done.

        Aliased to is_active for compatibility
        with graphlib.
        """
        return bool(self._default_view)

    def __len__(self):
        """
        Returns the number of nodes in the graph.
        """
        return len(self.nodes)

    def ready(self):
        """
        Returns a tuple of "ready" nodes--nodes with no
        predecessors, or nodes whose predecessors have all
        been marked "done".

        Aliased to get_ready for compatibility with graphlib.
        """
        return self._default_view.ready()

    def done(self, *nodes):
        """
        Marks nodes returned by ready as "done",
        possibly allowing additional nodes to be available
        from ready.
        """
        return self._default_view.done(*nodes)

    def reset(self):
        """
        Resets the default view to its initial state,
        forgetting all "ready" and "done" state.
        """
        return self._default_view.reset()

    def __init__(self, graph=None):
        # the graph argument is a mapping of nodes to dependencies.

        # self.nodes maps node -> [count-of-predecessors, list-of-successors].
        # the first element of the list is the number of nodes *we* depend on.
        # the second element of the list is a set of nodes that depend on *us*.
        #
        # nodes added to the graph are always listed in self.nodes, even
        # if they've been given to the user by ready() or returned by done().
        self.nodes = {}

        # If the "dirty" attribute is true, we need to check for cycles.
        #
        # we're slightly smart about this:
        # we only set the dirty flag when we add an edge between
        # two nodes that were already in the graph.
        self.dirty = False

        self.views = []
        self._default_view = self.View(self)
        self._stock_view = self.View(self)

        if graph is not None:
            for node, dependencies in graph.items():
                self.add(node, *dependencies)

    def __repr__(self):
        return f"<TopologicalSorter {hex(id(self))} {len(self.nodes)} nodes>"

    def view(self):
        """
        Returns a new View object on this graph.
        """
        return self._stock_view.copy()

    def add(self, node, *dependencies):
        """
        Add a node to the graph if it isn't already there.
        All arguments are nodes of the graph; the first is
        the "node" added, and it will depend on all subsequent
        arguments.

        If add() is called multiple times with the same node
        argument, the set of dependencies will be the union of
        all dependencies passed in.

        It's legal to add a node with no dependencies.

        It's legal to depend on a node the graph hasn't otherwise
        seen yet.  It will be automatically added (and will have no
        dependencies).

        You can only add a dependency once;
        any further attempts are ignored.
        Calling K.add('a', 'b') twice is the same as
        calling K.add('a', 'b') once, or
        calling K.add('a', 'b', 'b', 'b', 'b') once.
        """
        # print(f"{node:3} depends on {dependencies!r}")

        new_nodes = []
        new_successors = []

        if not node in self.nodes:
            new_nodes.append(node)
            self.nodes[node] = nodes_dict_default()

        pc_s = self.nodes[node]
        predecessors_count, successors = pc_s

        for d in dependencies:
            if d not in self.nodes:
                new_nodes.append(d)
                self.nodes[d] = nodes_dict_default()
            d_pc, d_s = self.nodes[d]
            if node not in d_s:
                self.dirty = True
                d_s[node] = None
                predecessors_count += 1
                new_successors.append(d)

        pc_s[0] = predecessors_count

        if new_nodes:
            for v in self.views:
                v._add_nodes(new_nodes)
        if new_successors:
            for v in self.views:
                for s in new_successors:
                    v._add_successor(s, node)

    def remove(self, node):
        """
        Remove node from the graph.

        If any node P depends on a node N, this dependency
        is also removed, but P is not removed from the graph.

        remove() works but it's slow (O(N)).
        TopologicalSorter is optimized for fast adds and fast views.
        """

        # print("remove!", node)
        # print(f"    before {self.nodes=}")
        if node not in self.nodes:
            raise ValueError("node not in graph")

        predecessors = []
        predecessor_count, successors = self.nodes[node]
        if predecessor_count:
            # we have to iterate over all nodes in the graph
            # until we find all predecessors.
            for n, pc_s in self.nodes.items():
                pc, s = pc_s
                if node in s:
                    predecessor_count -= 1
                    predecessors.append(n)
                    # early exit! on average, O(N * 0.5) ;-)
                    # phew!
                    if not predecessor_count:
                        break

        # print(f"    {predecessors=}")
        # print(f"    {successors=}")

        for n in predecessors:
            _, s = self.nodes[n]
            del s[node]

        for n in successors:
            p_s = self.nodes[n]
            p_s[0] -= 1

        del self.nodes[node]
        # print(f"    after {self.nodes=}")
        # print()

        for v in self.views:
            v._remove_node(node, successors)

        # we never need to set the dirty flag here.
        # dirty is only used for detecting cycles.
        # you can't add a cycle by removing nodes or edges.

    def copy(self):
        """
        Returns a shallow copy of the graph.  The copy also
        duplicates the state of get_ready and done.
        """
        clone = self.__class__()
        for node, p_s in self.nodes.items():
            p, s = p_s
            clone.nodes[node] = [p, s.copy()]

        clone._default_view = self._default_view.copy()
        clone._default_view.graph = clone
        clone._stock_view = self._stock_view.copy()
        clone._stock_view.graph = clone

        return clone

    def cycle(self):
        """
        Cycle detector.
        If the graph has no cycles, returns None.
        If the graph has a cycle, returns a tuple containing
          nodes in a cycle.
        """
        if not self.dirty:
            # dirty bit is only cleared when we don't have a cycle.
            # ergo, if dirty bit isn't set, we have no cycles.
            return None
        self.dirty = False

        counts = {node: value[0] for node, value in self.nodes.items()}
        done = set()
        _ready = {node for node, count in counts.items() if not count}
        while _ready:
            done |= _ready
            _ready2 = set()
            for node in _ready:
                successors = self.nodes[node][1]
                for successor in successors:
                    counts[successor] -= 1
                    if not counts[successor]:
                        _ready2.add(successor)
            _ready = _ready2

        if len(done) == len(counts):
            # no cycles!
            return None

        # cycle detected.
        # start with all nodes that are aren't done yet.
        nodes = set(self.nodes) - done

        # pick a node at random and see if we can find a cycle.
        # note that this node may not participate in a cycle!
        # e:g:
        #   A -> B
        #   B -> A
        #   B -> C
        # C is not in a cycle, but it isn't done yet either.

        # the classic algorithm here is Depth First Search.
        # DFS is most clearly written recursively,
        # but this is Python and we could blow our stack.
        iterators = [iter(nodes)]
        seen = set()
        cycle = []

        while iterators:
            top = iterators[-1]
            try:
                node = next(top)
                # it's impossible for 'node' to be marked done.
                # we started with the list of nodes that weren't
                # marked 'done' yet, and the only thing we ever
                # add to 'iterators' are successor nodes.
                assert node not in done
                if node in seen:
                    # found a cycle
                    index = cycle.index(node)
                    self.dirty = True
                    return tuple(cycle[index:])
                # descend
                seen.add(node)
                cycle.append(node)
                iterators.append(iter(self.nodes[node][1]))
            except StopIteration:
                # ascend
                node = cycle.pop()
                seen.remove(node)
                iterators.pop()

    def check_for_cycles(self):
        """
        Checks for cycles.  If any cycles exist, raises CycleError.

        Aliased to prepare for compatibility with graphlib.
        """
        if self.dirty:
            cycle = self.cycle()
            if cycle:
                raise CycleError(f"nodes are in a cycle", cycle)

    def static_order(self):
        """
        Returns an iterator object that yields the
        graph's nodes in topological order.
        """
        v = self.view()
        while v:
            ready = v.ready()
            yield from ready
            v.done(*ready)

    def print(self, print=print):
        """
        Prints the internal state of the graph.  Used for debugging.

        print is the function used for printing;
        it should behave identically to the builtin print function.
        """
        print(self)
        print(f"  {len(self.nodes)} nodes:".rjust(13))
        for node, p_s in sorted(self.nodes.items()):
            print("         ", node, p_s)

    # graphlib 1.0 compatibility
    is_active = __bool__
    prepare = check_for_cycles
    get_ready = ready



if __name__ == "__main__": # pragma: no cover
    #
    # A simple "tsort" utility.
    #     https://en.wikipedia.org/wiki/Tsort
    #
    # reads stdin (or a file) containing pairs
    # of strings, e.g.:
    #    A B
    # That line would indicate that B comes after A
    # (B depends on A).

    import sys

    file = sys.stdin
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if filename != "-":
            file = open(filename, "rt")

    g = TopologicalSorter()
    for line in file:
        line = line.strip()
        if not line:
            continue
        fields = line.split()
        if len(fields) != 2:
            sys.exit("invalid input: " + repr(line))
        g.add(fields[1], fields[0])

    nodes = list(g.static_order())
    for s in nodes:
        print(s)

    if file != sys.stdin:
        file.close()
