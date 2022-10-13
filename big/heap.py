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

__all__ = ['Heap']

from heapq import (
    heapify,
    heappop,
    heappush,
    heappushpop,
    heapreplace,
    nlargest,
    nsmallest,
    )

class Heap:
    """
    An object-oriented wrapper around the heapq library, designed to be
    easy to use--and easy to remember how to use.
    The Heap API mimics the list and collections.deque objects; this way,
    all you need to remember is "it works kinda like a list object".

    Specifics:
        * Use Heap.append to add a value to the heap.
        * Use Heap.extend to add multiple values to the heap.
        * Use Heap.popleft to remove the earliest value from the heap.
        * Use Heap[0] to peek at the earliest value on the heap.
    """
    def __init__(self, i=None):
        if not i:
            self._queue = []
        else:
            self._queue = list(i)
            heapify(self._queue)
        self._version = 0

    def __repr__(self):
        id_string = hex(id(self))[-6:]
        return f"<Heap {id_string} len={len(self._queue)} first={self._queue[0]}>"

    def append(self, o):
        heappush(self._queue, o)
        self._version += 1

    def clear(self):
        self._queue.clear()
        self._version += 1

    def copy(self):
        copy = self.__class__()
        copy._queue = self._queue.copy()
        return copy

    def extend(self, i):
        self._queue.extend(i)
        heapify(self._queue)
        self._version += 1

    def remove(self, o):
        self._queue.remove(o)
        heapify(self._queue)
        self._version += 1

    def popleft(self):
        o = heappop(self._queue)
        self._version += 1
        return o

    def append_and_popleft(self, o):
        o = heappushpop(self._queue, o)
        self._version += 1
        return o

    def popleft_and_append(self, o):
        o = heapreplace(self._queue, o)
        self._version += 1
        return o

    @property
    def queue(self):
        queue = list(self._queue)
        queue.sort()
        return queue

    def __bool__(self):
        return bool(self._queue)

    def __contains__(self, o):
        return o in self._queue

    def __eq__(self, other):
        return isinstance(other, self.__class__) and (self.queue == other.queue)

    def __len__(self):
        return len(self._queue)

    def __getitem__(self, item):
        if not isinstance(item, (int, slice)):
            raise TypeError(f"Heap only supports int and slice indices")
        if isinstance(item, slice):
            if item.step in (None, 1):
                length = len(self._queue)
                start = item.start or 0
                stop = item.stop if item.stop is not None else length
                if start < 0:
                    start += length
                if stop < 0:
                    stop += length
                if start == 0:
                    return nsmallest(stop, self._queue)
                if stop == length:
                    # nlargest returns the largest... IN REVERSE ORDER.  *smh*
                    result = nlargest(length - start, self._queue)
                    result.reverse()
                    return result
            # fall through! it'll work!
        elif item == 0:
            return self._queue[0]
        elif item == -1:
            return max(self._queue)
        elif 0 < item < 10:
            l = nsmallest(item + 1, self._queue)
            return l[item]
        elif -10 < item < 0:
            l = nlargest((-item) + 1, self._queue)
            return l[item]
        l = sorted(self._queue)
        # __getitem__ on a list handles ints and slices!
        return l[item]

    class HeapIterator:
        def __init__(self, heap):
            self._heap = heap
            self._copy = heap._queue.copy()
            self._version = heap._version

        def __next__(self):
            if self._version != self._heap._version:
                raise RuntimeError("Heap changed during iteration")
            if not self._copy:
                raise StopIteration
            return heappop(self._copy)

        def __repr__(self):
            return f"<HeapIterator {self._heap!r} {bool(self._heap)}>"

    def __iter__(self):
        return self.HeapIterator(self)

