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

__all__ = ["Scheduler"]


from dataclasses import dataclass
import threading
from .heap import Heap
import time



invalid_event = object()

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
    to sched.scheduler, and in particular reimplements the
    entire (relevant portion of the) sched.scheduler test suite.
    """

    DEFAULT_PRIORITY = 100

    @dataclass(order=True)
    class Event:
        time: object
        priority: object
        sequence: int
        event: object
        scheduler: object

        def cancel(self):
            self.scheduler.cancel(self)

    class Regulator:
        """
        Regulator encapsulates all the Scheduler's needs
        for interacting with time.
        The Scheduler has no knowledge about time itself;
        it uses a Regulator object for all its time-related
        needs.

        You can implement your own Regulator and use it
        with Scheduler; the only methods it needs are
        now, sleep, and wake.
        """

        def __init__(self, scheduler):
            self.event = threading.Event()

        def __repr__(self): # pragma: no cover
            return f"<Regulator {event}>"

        def now(self):
            """
            Returns the current time in local units.
            Must be monotonically increasing; for any
            two calls to now during the course of the
            program, the later call must *never*
            have a lower value than the earlier call.

            (The same Scheduler object will never call
            now twice simulaneously on the same Regulator
            object, as all access to the Regulator object
            is done under a lock.)
            """
            return time.time()

        def wake(self):
            """
            Aborts all current calls to sleep,
            across all threads.
            """
            self.event.set()
            self.event.clear()

        def sleep(self, interval):
            """
            Sleeps for some amount of time, in local units.
            Must support an interval of 0.
            It's preferable that an interval of 0 yields the rest
            of the current thread's current time slice.

            If wake is called on this Regulator object while a
            different thread has called this function to sleep,
            sleep must abandon the rest of the sleep interval
            and return immediately.
            """
            self.event.wait(interval)

    def __init__(self, regulator=None):
        if regulator is None:
            regulator = self.Regulator(self)
        self.regulator = regulator
        self.heap = Heap()
        self.lock = threading.Lock()
        self.counter = 0

    def schedule(self, o, time, *, absolute=False, priority=DEFAULT_PRIORITY):
        """Schedule a new event to be yielded at a specific future time.

        By default, "time" is relative to the current time.
        If absolute is true, "time" is an absolute time.

        "priority" represents the importance of the event.
        Lower numbers are more important.
        There are no predefined priorities; you may use it however you like.

        Returns an object which can be used to remove the event from the queue:
           o = scheduler.schedule(my_event, 5)
           o.cancel() # cancels the event
        Alternately you can pass in this object to the scheduler's cancel method:
           o = scheduler.schedule(my_event, 5)
           scheduler.cancel(o)
        """
        if o == invalid_event:
            raise ValueError('invalid event')
        if not absolute:
            time += self.regulator.now()
        with self.lock:
            self.counter += 1
            event = self.Event(time, priority, self.counter, o, self)
            self.heap.append(event)
            self.regulator.wake()
        return event

    def cancel(self, event):
        """
        Cancel a scheduled event.

        event must be a value returned by add().
        If the event is not in the queue, raises ValueError.
        """
        with self.lock:
            self.heap.remove(event)
            self.regulator.wake()

    def __bool__(self):
        """
        Returns True if the queue is not empty.
        """
        with self.lock:
            return bool(self.heap)

    @property
    def queue(self):
        """
        An ordered list of upcoming events.

        The entries in the list are big.scheduler.Event objects.
        """
        with self.lock:
            return self.heap.queue

    def _next(self, blocking=True):
        # why loop here? in case we get awakened by the queue changing.
        #
        # also, I swear that back in my early Windows days, sleeping on
        # timers wasn't perfect and would often return slightly early.
        while True:
            # print(f"{self._regulator.now()}  {self.heap=}")
            # don't sleep while holding the lock!
            # we write down what we need to do in
            # local variables, then do it after releasing
            # the lock.
            sleep_interval = 0
            event = invalid_event

            with self.lock:
                if not self.heap:
                    # print(" empty queue DONE")
                    raise StopIteration

                sleep = self.regulator.sleep

                ev = self.heap[0]

                now = self.regulator.now()
                interval = ev.time - now
                ready = interval <= 0

                if not ready:
                    if not blocking:
                        # print(" wouldblock DONE")
                        raise StopIteration
                    sleep_interval = max(interval, 0)
                else:
                    self.heap.popleft()
                    event = ev.event

            # we always delay here.
            # if sleep_interval is 0,
            # this still yields the remainder of our timeslice
            # and lets other threads run.
            # print(f"  sleeping {sleep_interval}")
            sleep(sleep_interval)
            if event is not invalid_event:
                # print(f"  returning {event}")
                return event

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
        A non-blocking iterator over the queue.
        Only yields events that are currently ready,
        then stops iteration.
        """
        return self.NonBlockingSchedulerIterator(self)

