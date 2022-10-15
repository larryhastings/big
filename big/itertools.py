import collections

__all__ = ['PushbackIterator']
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
        if self.i:
            return next(self.i)
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
        if not self.i:
            return default
        try:
            return next(self.i)
        except StopIteration:
            self.i = None
            return default

    def __bool__(self):
        if self.stack:
            return True
        if not self.i:
            return False
        try:
            o = next(self.i)
            self.push(o)
            return True
        except StopIteration:
            return False

    def __repr__(self):
        return f"<{self.__class__.__name__} i={self.i} stack={self.stack}>"

