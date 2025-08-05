import collections

__all__ = ['PushbackIterator', 'IteratorContext', 'iterator_context', 'ix', 'Undefined', 'undefined', 'iterator_filter', 'filterator', 'f8r']

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


# --8<-- start tidy itertools --8<--


class IteratorContext:
    def __init__(self, iterator, start, index, is_first, is_last, previous, current, next):
        self._iterator = iterator
        self._length = None

        self.start = start
        self.index = index
        self.is_first = is_first
        self.is_last = is_last

        if not is_first:
            self.previous = previous
        self.current =current
        if not is_last:
            self.next = next

    @property
    def length(self):
        if self._length is None:
            self._length = len(self._iterator)
        return self._length

    @property
    def countdown(self):
        if self._length is None:
            self._length = len(self._iterator)
        return self.start + self._length - (1 + self.index - self.start)

    def __repr__(self):
        fields = []
        for name in ('previous', 'current', 'next'):
            if hasattr(self, name):
                fields.append(f"{name}={getattr(self, name)!r}")
        s = ", ".join(fields)
        return f'IteratorContext(iterator={self._iterator!r}, start={self.start!r}, index={self.index!r}, is_first={self.is_first!r}, is_last={self.is_last!r}, {s})'


def iterator_context(iterator, start=0):
    """
    Iterates over iterable.  Yields (ctx, o) where o
    is each value yielded by iterable, and ctx is a
    "context" variable containing metadata about
    the iteration.

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
      the iterator has yielded, ctx.previous won't be set,
      and accessing it will raise AttributeError.)
    ctx.next contains the next value to be yielded by
      this iterator if there is one.  (If 'o' is the last
      value yielded by the iterator, ctx.previous won't be
      set, and accessing it will raise AttributeError.)
    ctx.index contains the index of this value.  The first
      time the iterator yields a value, this will be "start";
      the second time, it will be start + 1, etc.
    ctx.countdown contains the "opposite" value of ctx.index.
      The values yielded by ctx.countdown are the same as
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

        ctx = IteratorContext(iterator, start, index, is_first, False, previous, current, _next)

        yield (ctx, current)
        index += 1
        is_first = False

    # if the iterator yielded *any* values, yield the final one
    if _next != undefined:
        ctx = IteratorContext(iterator, start, index, is_first, True, current, _next, undefined)
        yield (ctx, _next)

ix = iterator_context


undefined = None

class Undefined:
    def __init__(self):
        global undefined
        if undefined is not None:
            raise TypeError('only one instance of Undefined is allowed')

    def __repr__(self):
        return "<Undefined>"

    def __bool__(self):
        return False

undefined = Undefined()


def iterator_filter(iterator,
    *,
    stop_at_value=undefined,
    stop_at_in=None,
    stop_at_predicate=None,
    stop_at_count=None,
    reject_value=undefined,
    reject_in=None,
    reject_predicate=None,
    only_value=undefined,
    only_in=None,
    only_predicate=None,
    ):
    """
    iterator_filter accepts one positional parameter, iterator, and
    nine keyword-only parameters which constitute the "rules".
    The rules are formed from three prefixes: "stop_at", "reject",
    and "only", and three suffixes, "_value", "_in", and "_predicate".
    So for example, filterator accepts arguments with names like
    "stop_at_value", "reject_in", and "only_predicate".

    iterator_filter is itself an iterator.  It yields values from the
    iterator you pass in, but only values that are acceptable to
    all the rules you supply.

    To "pass" a rule means "the test using this rule returned
    a true value".  There are three varieties of tests, specified
    with the end of the rule's name.

        A rule that ends in _value means "pass if the value == this value".
        For example, stop_at_value=5 would mean "if the inner iterator
        ever yields the value 5, immediately become exhausted".

        A rule that ends in _in means "pass if the value is in this value".
        This value must support the "in" operator.  For example,
        "reject_in=(1, 2, 3)" would reject the value if it was 1, 2, or 3.

        A rule that ends in _predicate means "pass if calling this value
        and passing in the value returns a true value".  This value must
        be callable.  For example, "only_predicate=lambda o: isinstance(o, str)"
        would only accept str values.

    There are three categories of rule actions, specified by the start
    of the rule's name.  They're examined in this order:
    "stop_at", "reject", "only".

        "stop_at" rules cause filterator to become exhausted.
        If a value yielded by iterator passes a "stop_at" rule,
        the iterator immediately goes into its "exhausted" state.

        "reject" rules cause filterator to reject values--a
        "blacklist" for values.  If a value passes any "reject" rule,
        it's discarded and the iterator continues to the next value.

        "only" rules are required for filterator to accept a
        value--a "whitelist" for values.  A value must pass all
        "only" rules, otherwise it's rejected.

    There's one extra rule not described in the above: "stop_at_count",
    an number.  This exhausts the iterator after yielding
    "stop_at_count" items.  If "stop_at_count" is initially <= 0,
    the iterator is immediately exhausted.
    """

    un = undefined

    stop_at_value_active     = stop_at_value     is not un
    stop_at_in_active        = stop_at_in        is not None
    stop_at_predicate_active = stop_at_predicate is not None
    stop_at_count_active     = stop_at_count     is not None
    stop_at = stop_at_value_active or stop_at_in_active or stop_at_predicate_active or stop_at_count_active

    reject_value_active     = reject_value     is not un
    reject_in_active        = reject_in        is not None
    reject_predicate_active = reject_predicate is not None
    reject  = reject_value_active or reject_in_active or reject_predicate_active

    only_value_active     = only_value     is not un
    only_in_active        = only_in        is not None
    only_predicate_active = only_predicate is not None
    only    = only_value_active or only_in_active or only_predicate_active

    for o in iterator:
        if stop_at and (
                (stop_at_value_active and (o == stop_at_value))
                or
                (stop_at_in_active and (o in stop_at_in))
                or
                (stop_at_predicate_active and stop_at_predicate(o))
            ):
            return

        if reject and (
                (reject_value_active and (o == reject_value))
                or
                (reject_in_active and (o in reject_in))
                or
                (reject_predicate_active and reject_predicate(o))
            ):
            continue

        if only and (
                (only_value_active and (o != only_value))
                or
                (only_in_active and (o not in only_in))
                or
                (only_predicate_active and (not only_predicate(o)))
            ):
            continue

        if stop_at_count_active:
            if stop_at_count <= 0:
                return
            stop_at_count -= 1

        yield o

f8r = filterator = iterator_filter

# --8<-- end tidy itertools --8<--
