#!/usr/bin/env python3

_license = """
big
Copyright 2022-2024 Larry Hastings
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

__all__ = ['Regulator', 'SingleThreadedRegulator', 'ThreadSafeRegulator', 'Scheduler']


from abc import abstractmethod
import threading
from .heap import Heap
import sys
import time



class InertContextManager:
    def __enter__(self):
        pass

    def __exit__(self, exception_type, exception, traceback):
        pass

inert_context_manager = InertContextManager()

class Regulator:
    """
    An abstract base class for Scheduler regulators.

    A "regulator" handles all the details about time
    for a Scheduler.  Scheduler objects don't actually
    understand time; it's all abstracted away by the
    Regulator.

    You can implement your own Regulator and use it
    with Scheduler.  Your Regulator subclass needs to
    implement a minimum of three methods: 'now',
    'sleep', and 'wake'.  It must also provide an
    attribute called 'lock'.  The lock must implement
    the context manager protocol, and should lock
    the Regulator as needed.

    Normally a Regulator represents time using a
    floating-point number, representing a fractional
    number of seconds since some epoch.  But this
    isn't strictly necessary.  Any Python object
    that fulfills these requirements will work:

    * The time class must implement `__le__`, `__eq__`, `__add__`,
      and `__sub__`, and these operations must be consistent in the
      same way they are for number objects.
    * If `a` and `b` are instances of the time class,
      and `a.__le__(b)` is true, then `a` must either be
      an earlier time, or a smaller interval of time.
    * The time class must also implement rich comparison
      with numbers (integers and floats), and `0` must
      represent both the earliest time and a zero-length
      interval of time.
    """

    # A context manager that provides thread-safety
    # as appropriate.  The Schedule will never recursively
    # enter the lock (it doesn't need to be a threading.RLock).
    lock = inert_context_manager

    @abstractmethod
    def now(self): # pragma: no cover
        """
        Returns the current time in local units.
        Must be monotonically increasing; for any
        two calls to now during the course of the
        program, the later call must *never*
        have a lower value than the earlier call.

        A Scheduler will only call this method while
        holding this regulator's lock.
        """
        pass

    @abstractmethod
    def sleep(self, interval): # pragma: no cover
        """
        Sleeps for some amount of time, in local units.
        Must support an interval of 0, which should
        represent not sleeping.  (Though it's preferable
        that an interval of 0 yields the rest of the
        current thread's remaining time slice back to
        the operating system.)

        If wake is called on this Regulator object while a
        different thread has called this function to sleep,
        sleep must abandon the rest of the sleep interval
        and return immediately.

        A Scheduler will only call this method while
        *not* holding this regulator's lock.
        """
        pass

    @abstractmethod
    def wake(self): # pragma: no cover
        """
        Aborts all current calls to sleep on this
        Regulator, across all threads.

        A Scheduler will only call this method while
        holding this regulator's lock.
        """
        pass


class SingleThreadedRegulator(Regulator):
    """
    An implementation of Regulator designed for
    use in single-threaded programs.  It provides
    no thread safety, but is much higher performance
    than thread-safe Regulator implementations.
    """

    def __repr__(self): # pragma: no cover
        return f"<SingleThreadedRegulator>"

    def now(self):
        return time.monotonic()

    def wake(self):
        pass

    def sleep(self, interval):
        time.sleep(interval)


default_regulator = SingleThreadedRegulator()


class ThreadSafeRegulator(Regulator):
    """
    A thread-safe Regulator object designed
    for use in multithreaded programs.
    It uses Python's threading.Event and
    threading.Lock.
    """

    def __init__(self):
        self.event = threading.Event()
        self.lock = threading.Lock()

    def __repr__(self): # pragma: no cover
        return f"<ThreadSafeRegulator event={self.event} lock={self.lock}>"

    def now(self):
        return time.monotonic()

    def wake(self):
        self.event.set()
        self.event.clear()

    def sleep(self, interval):
        self.event.wait(interval)


DEFAULT_PRIORITY = 100

class Event:
    """
    Wraps event objects in a Scheduler's queue.

    Only supports one method: cancel(), which cancels
    the event.  (If the event isn't currently scheduled,
    raises ValueError.)
    """
    def __init__(self, scheduler, event, time, priority, sequence):
        self.scheduler = scheduler
        self.event = event
        self.time = time
        self.priority = priority
        self.sequence = sequence

    def __lt__(self, other):
        if self.time < other.time:
            return True
        if self.time > other.time:
            return False

        if self.priority < other.priority:
            return True
        if self.priority > other.priority:
            return False

        if self.sequence < other.sequence:
            return True

        return False

    def __repr__(self): # pragma: no cover
        return f"<Event event={self.event} time={self.time} priority={self.priority} sequence={self.sequence} scheduler={self.scheduler}>"

    def cancel(self):
        self.scheduler.cancel(self)


class Scheduler:
    """
    A replacement for Python's sched.scheduler object,
    adding full threading support and a modern Python interface.

    Python's sched.scheduler object is unfixable; its interface
    means it cannot correctly handle some scenarios:
        * If one thread has called sched.scheduler.run,
          and the next scheduled event will occur at time T,
          and a second thread schedules a new event which
          occurs at a time < T, sched.scheduler.run won't
          return any events to the first thread until time T.
        * If one thread has called sched.scheduler.run,
          and the next scheduled event will occur at time T,
          and a second thread cancels all events,
          sched.scheduler.run won't exit until time T.

    Also, sched.scheduler is thirty years behind the times in
    Python API design.  Its events are callbacks, which it
    calls.  Scheduler fixes this: its events are objects,
    and you iterate over the Scheduler object to receive
    events as they become due.

    Scheduler also benefits from thirty years of improvements
    to sched.scheduler.  In particular, big reimplements the
    bulk of the sched.scheduler test suite, to ensure that
    Scheduler never repeats the historical problems discovered
    over the lifetime of sched.scheduler.

    The only argument to Scheduler is an instance of Regulator,
    that provides time and thread-safety to the Scheduler.
    By default Scheduler uses an instance of
    SingleThreadedRegulator, which is not thread-safe.

    (If you need the scheduler to be thread-safe, pass in
    an instance of a thread-safe Regulator class like
    ThreadSafeRegulator.)
    """

    def __init__(self, regulator=default_regulator):
        self.regulator = regulator
        self.heap = Heap()
        self.event_id_counter = 0

    def schedule(self, o, time, *, absolute=False, priority=DEFAULT_PRIORITY):
        """Schedule a new event to be yielded at a specific future time.

        By default, "time" is relative to the current time.
        If absolute is true, "time" is an absolute time.

        "priority" represents the importance of the event. Lower numbers
        are more important.  There are no predefined priorities; you may
        assign priorities however you like.

        Returns an object which can be used to remove the event from the queue:
           o = scheduler.schedule(my_event, 5)
           o.cancel()  # cancels the event
        Alternately you can pass in this object to the scheduler's cancel method:
           o = scheduler.schedule(my_event, 5)
           scheduler.cancel(o)  # also cancels the event
        """
        with self.regulator.lock:
            if not absolute:
                time += self.regulator.now()
            self.event_id_counter += 1
            event = Event(self, o, time, priority, self.event_id_counter)
            self.heap.append(event)
            self.regulator.wake()
        return event

    def cancel(self, event):
        """
        Cancel a scheduled event.

        event must be a value returned by add().
        If the event is not in the queue, raises ValueError.
        """
        with self.regulator.lock:
            self.heap.remove(event)
            self.regulator.wake()

    def __bool__(self):
        """
        Returns True if the scheduler contains any scheduled events.
        This includes both events scheduled for the future,
        as well as events that have already expired but have
        yet to be yielded by the Scheduler.
        """
        with self.regulator.lock:
            return bool(self.heap)

    @property
    def queue(self):
        """
        A list of the currently scheduled Event objects,
        in the order they will be yielded.
        """

        # Note: In many places I refer to the scheduler's "queue".
        # This isn't a "queue" as in Python's built-in "queue" module.
        # The Scheduler's "queue" is a conceptual ordered list of
        # events in the order they'll be yielded.   (It actually uses
        # a "heap", as in Python's built-in "heap" module.)  The
        # Python scheduler uses the term "queue" a lot, including
        # having this exact property, so I kept it.

        with self.regulator.lock:
            return self.heap.queue

    def _next(self, blocking=True):
        # Why a loop?  In case we get woken up early.
        # That can happen when the queue changes.
        #
        # Also, I swear that back in my early Win32 days,
        # timers weren't perfect, and the Sleep call would
        # occasionally wake up slightly early.

        while True:

            with self.regulator.lock:
                if not self.heap:
                    raise StopIteration

                now = self.regulator.now()
                ev = self.heap[0]
                time_to_next_event = ev.time - now

                if time_to_next_event <= 0:
                    self.heap.popleft()
                    return ev.event

                # Don't sleep while holding the lock!
                #
                # Do this instead:
                #   * Fetch the sleep method while
                #     holding the lock, then
                #   * Release the lock, then
                #   * Sleep.
                sleep = self.regulator.sleep

            if not blocking:
                raise StopIteration

            # assert time_to_next_event > 0
            sleep(time_to_next_event)

    def __iter__(self):
        return self

    def __next__(self):
        return self._next()


    class NonBlockingSchedulerIterator:
        def __init__(self, scheduler):
            self.s = scheduler

        def __iter__(self):
            return self

        def __next__(self):
            return self.s._next(blocking=False)

    def non_blocking(self):
        """
        A non-blocking iterator.  Yields all events
        that are currently ready, then stops iteration.
        """
        return self.NonBlockingSchedulerIterator(self)
