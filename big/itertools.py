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

import collections


from . import builtin
mm = builtin.ModuleManager()
export = mm.export


@export
class PushbackIterator:
    """
    Wraps any iterator, letting you push items to be yielded first.

    The PushbackIterator constructor accepts one argument, any iterable.
    When you iterate over the PushbackIterator instance, it yields values
    from that iterable.  You may also pass in None, in which case the
    PushbackIterator is created in an "exhausted" state.

    PushbackIterator also supports a push(o) method, which "pushes"
    values onto the iterator.  If any objects have been pushed onto
    the iterator, they're yielded first, before attempting to yield
    from the wrapped iterator.  Pushed values are yielded in
    first-in-first-out order, like a stack.

    Example: you have a pushback iterator J, and you call J.push(3)
    followed by J.push('x').  The next two times you iterate over
    J, it will yield 'x', followed by 3.

    When the wrapped iterable is exhausted--or if you passed in None to
    the constructor--you can still call push to add new items, at which
    point the PushbackIterator can be iterated over again.

    PushbackIterator also supports a next(default=None) method,
    like Python's builtin next function.  It also supports __bool__,
    returning True if it's exhausted.

    It's explicitly supported to push values that were never yielded by
    the wrapped iterator.  If you create J = PushbackIterator(range(1, 20)),
    you may still call J.push(33), or J.push('xyz'), or J.push(None), etc.
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


@export
class IteratorContext:
    "Context object yielded by big.iterator_context."

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


@export
def iterator_context(iterator, start=0):
    """
    Wraps any iterator, yielding values with a helpful context object.

    Wraps any iterator.  Yields (ctx, o), where o is a value
    yielded by iterable, and ctx is a "context" variable
    containing metadata about the iteration.

    ctx will always have these six attributes:

    * ctx.is_first is true for the first value yielded
      and false otherwise.
    * ctx.is_last is true for the last value yielded
      and false otherwise.  (If the iterator only yields
      one value, is_first and is_last will both be true.)
    * ctx.current contains the current value yielded by the
      iterator.   (The same as the 'o' value in the
      yielded tuple).
    * ctx.previous contains the previous value yielded, if
      is_first is false.  If is_first is true, ctx.previous
      will be undefined, and accessing it will raise
      AttributeError.
    * ctx.next contains the next value to be yielded by this
      iterator if is_last is False.  If is_last is True,
      ctx.previous will be undefined, and accessing it will
      raise AttributeError.
    * ctx.index contains the index of this value.  The first
      time the iterator yields a value, this will be "start";
      the second time, it will be start + 1, etc.

    ctx also supports two more attributes, ctx.length and
    ctx.countdown, but these require the "iterator" object
    to support __len__.  If the iterator doesn't support
    __len__, these two attributes are not defined, and
    accessing them will raise an exception.

    * ctx.countdown contains the "opposite" value of ctx.index.
      The values yielded by ctx.countdown are the same as
      ctx.index but in reversed order.  If start is 0,
      and the iterator yields four items, ctx.index will
      be 0, 1, 2, and 3 in that order, and ctx.countdown
      will be 3, 2, 1, and 0 in that order.  If start is 3,
      and the iterator yields four items, ctx.index will
      be 3, 4, 5, and 6 in that order, and ctx.countdown
      will be 6, 5, 4, and 3 in that order.
    * ctx.length contains the total number of items that
      will be yielded.
    """
    index = start

    previous = current = next = undefined = object()
    is_first = True
    is_last = False

    i = iter(iterator)

    # what's *this* doing here?
    # this saves us an "if" statement in the main loop.
    # also, I suspect using a for loop that you immediately
    # break out of is cheaper than "try: next = next(i)".
    for next in i:
        break

    for o in i:
        previous = current
        current = next
        next = o

        ctx = IteratorContext(iterator, start, index, is_first, False, previous, current, next)

        yield (ctx, current)
        index += 1
        is_first = False

    # if the iterator yielded *any* values, yield the final one
    if next != undefined:
        ctx = IteratorContext(iterator, start, index, is_first, True, current, next, undefined)
        yield (ctx, next)


undefined = None

@export
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
export("undefined")


@export
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
    Wraps any iterator, filtering the values yielded.

    iterator_filter accepts one positional parameter, "iterator", and
    ten keyword-only parameters collectively called "rules" which
    constitute tests applied to the values yielded by the iterator.
    iterator_filter is itself an iterator; it yields the values
    yielded by the iterator you pass in, but only if they pass
    all the "rules" you specified as arguments to the constructor.

    The rules are generally formed from three prefixes: "stop_at",
    "reject", and "only", as well as three suffixes, "_value", "_in",
    and "_predicate".  Here's a list of all the "rule" parameters:

        stop_at_value
        stop_at_in
        stop_at_predicate
        stop_at_count

        reject_value
        reject_in
        reject_predicate

        only_value
        only_in
        only_predicate

    There are three categories of rule actions, differentiated by the
    prefix of the rule's name.  They're examined in the order
    "stop_at", "reject", and finally "only":

        "stop_at" rules cause iterator_filter to become exhausted.
        If a value yielded by iterator passes a "stop_at" rule,
        the iterator immediately goes into its "exhausted" state.
        (It doesn't yield the value that caused it to become exhausted.)

        "reject" rules cause iterator_filter to reject matching
        values--a "blacklist" for values.  If a value passes any
        "reject" rule, it's discarded and the iterator continues
        to the next value.

        "only" rules cause iterator_filter to reject non-matching
        values--a "whitelist" for values.  If a value doesn't pass
        all "only" rules, it's discarded and the iterator continues
        to the next value.

    To "pass" a rule means "the test using this rule returned
    a true value".  There are three varieties of tests, differentiated
    with the suffix at the end of the rule's name.

        A rule ending in "_value" means "pass if the value == this argument".
        For example, stop_at_value=5 would mean "if the inner iterator
        ever yields the value 5, immediately become exhausted".  The test
        is performed using the "==" operator (__eq__).  The value that
        exhausts the iterator is not yielded.

        A rule ending in "_in" means "pass if the value is in this argument".
        The test is performed using the "in" operator; the value passed in
        must therefore support the "in" operator (__contains__). For example,
        "reject_in={1, 2, 3}" would reject the value if it's 1, 2, or 3.

        A rule that ends in "_predicate" means "pass if calling this argument
        and passing in the value returns a true value".  The argument to this
        parameter must be callable.  For example,
        "only_predicate=lambda o: isinstance(o, str)" would only accept values
        that were instances of str.

    There's one additional rule not described in the above:
    "stop_at_count", an number.  This exhausts the iterator after
    yielding "stop_at_count" items.  If you pass in stop_at_count=5,
    the iterator becomes exhausted after yielding five values.
    If "stop_at_count" is initially <= 0, the iterator is initialized
    in an exhausted state, and will never yield any values.
    """

    stop_at_value_active     = stop_at_value     is not undefined
    stop_at_in_active        = stop_at_in        is not None
    stop_at_predicate_active = stop_at_predicate is not None
    stop_at_count_active     = stop_at_count     is not None
    stop_at = stop_at_value_active or stop_at_in_active or stop_at_predicate_active or stop_at_count_active

    reject_value_active     = reject_value     is not undefined
    reject_in_active        = reject_in        is not None
    reject_predicate_active = reject_predicate is not None
    reject  = reject_value_active or reject_in_active or reject_predicate_active

    only_value_active     = only_value     is not undefined
    only_in_active        = only_in        is not None
    only_predicate_active = only_predicate is not None
    only    = only_value_active or only_in_active or only_predicate_active

    # the only rule we can apply *before* iterating over the wrapped iterator
    if stop_at_count_active and (stop_at_count <= 0):
        return

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

# --8<-- end tidy itertools --8<--

mm()
