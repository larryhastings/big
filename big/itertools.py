import collections

__all__ = ['PushbackIterator', 'LoopContext', 'loop_context', 'Undefined', 'undefined']

class PushbackIterator:
    """
    Wraps any iterator, allowing you to push items back on the iterator.
    This allows you to "peek" at the next item (or items); you can get the
    next item, examine it, and then push it back.  If any objects have
    been pushed onto the iterator, they are yielded first, before attempting
    to yield from the wrapped iterator.

    Pass in any iterable to the constructor.  Passing in an iterable of None
    means the PushbackIterator is created in an exhausted state.

    When the wrapped iterable is exhausted (or if you passed in None to
    the constructor) you can still call push to add new items, at which
    point the PushBackIterator can be iterated over again.
    """

    __slots__ = ('i', 'stack')

    def __init__(self, iterable=None):
        if (iterable != None) and (not hasattr(iterable, '__next__')):
            iterable = iter(iterable)
        self.i = iterable
        self.stack = []

    def __iter__(self):
        return self

    def push(self, o):
        """
        Pushes a value into the iterator's internal stack.
        When a PushbackIterator is iterated over, and there are
        any pushed values, the top value on the stack will be popped
        and yielded.  PushbackIterator only yields from the
        iterator it wraps when this internal stack is empty.
        """
        self.stack.append(o)

    def __next__(self):
        if self.stack:
            return self.stack.pop()
        if self.i is not None:
            try:
                return next(self.i)
            except:
                self.i = None
        raise StopIteration

    def next(self, default=None):
        """
        Equivalent to next(PushbackIterator),
        but won't raise StopIteration.
        If the iterator is exhausted, returns
        the "default" argument.
        """
        if self.stack:
            return self.stack.pop()
        if self.i is not None:
            try:
                return next(self.i)
            except StopIteration:
                self.i = None
        return default

    def __bool__(self):
        if self.stack:
            return True
        if self.i is not None:
            try:
                o = next(self.i)
                self.push(o)
                return True
            except StopIteration:
                self.i = None
        return False

    def __repr__(self):
        return f"<{self.__class__.__name__} i={self.i} stack={self.stack}>"


# --8<-- start loop_context --8<--

undefined = None

class Undefined:
    def __init__(self):
        global undefined
        if undefined is not None:
            raise TypeError('only one instance of Undefined is allowed')

    def __repr__(self):
        return "<Undefined>"

undefined = Undefined()

class LoopContext:
    def __init__(self, iterator, start, index, is_first, is_last, previous, current, _next):
        self._iterator = iterator
        self._start = start
        self._length = None

        self.index = index

        self.is_first = is_first
        self.is_last = is_last

        self.previous = previous
        self.current =current
        self.next = _next

    @property
    def length(self):
        if self._length is None:
            self._length = len(self._iterator)
        return self._length

    @property
    def countdown(self):
        if self._length is None:
            self._length = len(self._iterator)
        return self._start + self._length - (1 + self.index - self._start)


def loop_context(iterator, start=0):
    """
    Iterates over iterable.  Yields (ctx, o) where o
    is each value yielded by iterable, and ctx is a
    "loop context" variable containing metadata
    about the iteration.

    ctx.is_first is true only for the first value yielded,
      and false otherwise.
    ctx.is_last is true only for the last value yielded,
      and false otherwise.  (If the iterator only yields
      one value, is_first and is_last will both be true.)
    ctx.current contains the current value yielded by the
      iterator ('o' as described above).
    ctx.previous contains the previous value yielded if
      this is the second or subsequent time this iterator
      has yielded a value.  (If this is the first time
      the iterator has yielded, ctx.previous will be
      an "undefined" value.)
    ctx.next contains the next value to be yielded by
      this iterator if there is one.  (If 'o' is the last
      value yielded by the iterator, ctx.previous will be
      an "undefined" value.)
    ctx.index contains the index of this value.  The first
      time the iterator yields a value, this will be "start";
      the second time, it will be start + 1, etc.
    ctx.countdown contains the "opposite" value of ctx.index.
      The values yielded by ctx.countdown ar ethe same as
      ctx.index, but in reversed order.  (If start is 0,
      and the iterator yields four items, ctx.index will
      be 0, 1, 2, and 3 in that order, and ctx.countdown
      will be 3, 2, 1, and 0 in that order.)
    ctx.length contain the total number of items that will
      be yielded.

    ctx.length and ctx.countdown depend on iterable
    supporting __len__.
    """
    index = start

    # next is a keyword, we'll call ours _next
    # (it's okay to have an attribute called 'next',
    # just not a local)
    previous = current = _next = undefined
    is_first = True
    is_last = False

    i = iter(iterator)

    # what's *this* doing here?
    # this saves us an "if" statement
    # in the main loop.  also, I suspect using a
    # for loop that you break immediately out of
    # is cheaper than "try: _next = next(i)".
    for _next in i:
        break

    for o in i:
        previous = current
        current = _next
        _next = o

        ctx = LoopContext(iterator, start, index, is_first, False, previous, current, _next)

        yield (ctx, current)
        index += 1
        is_first = False

    # if the iterator yielded *any* values, yield the final one
    if _next != undefined:
        ctx = LoopContext(iterator, start, index, is_first, True, current, _next, undefined)
        yield (ctx, _next)

# --8<-- end loop_context --8<--
