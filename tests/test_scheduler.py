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

import big.scheduler as big
from big.all import BoundInnerClass
from itertools import zip_longest
import queue
import sys
import threading
import time
import unittest


class MockRegulator:
    """
    Thread-safe Regulator object.
    Doesn't use the actual time; instead,
    you must manually advance the Regulator's
    time using the advance method.
    """
    def __init__(self):
        self.t = 0
        self.lock = threading.Lock()

        # if this number changes, you should wake.
        # writes are protected by explicit_wake_lock.
        # (we can't use lock, it's not recursive.)
        self.explicit_wake_counter = 0
        self.explicit_wake_lock = threading.Lock()

        # count of threads currently sleeping.
        # writes are protected by lock.
        self.sleeping = 0

    def __repr__(self): # pragma: no cover
        tid = hex(threading.get_ident())[2:]
        return f"<MockRegulator t={self.t} tid={tid}>"

    def advance(self, t):
        with self.lock:
            self.t += t

    def now(self):
        return self.t

    def sleep(self, t):
        with self.lock:
            delta_t = t
            t += self.t
            ignore_wake = self.explicit_wake_counter
            self.sleeping += 1

        # actually a busywait.
        # it's fine, this is just for testing.
        while True:
            with self.lock:
                now = self.t
                if ignore_wake != self.explicit_wake_counter:
                    self.sleeping -= 1
                    return
                if t <= now:
                    self.sleeping -= 1
                    return
            time.sleep(0.01)

    def wake(self):
        with self.explicit_wake_lock:
            self.explicit_wake_counter += 1



class ExitThread:
    pass

class MockTimeThread:
    """
        This object facilitates testing the Scheduler object
        with a MockRegulator.  MockRegulator uses simulated
        time rather than actual wall clock time.  That's good
        for testing; it helps prevent race conditions during
        testing, and the test can run at full CPU speed rather
        than waiting for arbitrary amounts.

        The problem is: how do you advance the clock of the
        MockRegulator?  MockTimeThread will do that for you.
        It creates your test Scheduler object for you, configured
        to use a MockRegulator for time.  It also creates a worker
        thread which injects time into the Scheduler for you.

        You send the worker thread instructions on what to do,
        then run your tests with the Scheduler on the "main"
        thread.

        Start and stop the worker thread with the "start" and
        "stop" methods.  Queue work for the worker thread with
        the "wait", "schedule", and "advance" methods.  The
        main thread can wait until the worker thread has finished
        all its work with the "flush" method.

        The only methods on this object called from the worker
        thread are those that start with a single underscore
        ("_thread" and "_wait").  All other methods are called
        from the main thread.
        """

    def __init__(self):

        self.regulator = MockRegulator()
        self.scheduler = big.Scheduler(self.regulator)

        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._thread)

        self._running = True
        self.thread.start()

    def __enter__(self):
        return self

    def __exit__(self, t, v, tb):
        self.stop()

    def stop(self):
        "Stop the worker thread."
        assert self._running
        if self._running:
            self._running = False
            self.queue.put(ExitThread)
            if self.thread:
                self.thread.join()

    def _wait(self):
        """
            Called by the worker thread.

            Block until the main thread is running the Scheduler object
            and waiting for the next event.

            (Technically, this method blocks until at least one thread
            has called sleep on our mock regulator.)

            Uses a busy-wait rather than properly sleeping.
            This is only test code--and this version was easy
            to get right.
            """
        r = self.scheduler.regulator
        while self._running and (not r.sleeping): # pragma: nocover
            time.sleep(0.001)

    def wait(self):
        "Tell the worker thread to block until the main thread is asleep."
        self.queue.put(self._wait)

    def flush(self):
        "Block until all tasks currently in the worker thread queue have been completed."
        event = threading.Event()
        self.queue.put(event.set)
        event.wait()

    def schedule(self, event, time, *, absolute=False, priority=big.DEFAULT_PRIORITY):
        "Tell the worker thread to schedule a new event."

        e = (event, time, absolute, priority)
        self.queue.put(e)

    def advance(self, t):
        "Tell the worker thread to advance the scheduler's MockRegulator by time t."
        self.queue.put(t)

    def assert_ready(self, *events):
        """
            Asserts that a list of events are currently ready, and are yielded
            by the Schedule object in a specific order.

            Pass in one or more events; assert_ready will block until one event
            is ready, then assert that all events passed in are ready, in that order.

            It's legal to call assert_ready with no arguments,
            in which case it asserts that no events are waiting.

            Uses unittest.assertEqual.
            """

        # if we expect at least one event,
        # block in the scheduler until at least one event is ready.
        # this helps with synchronization between the two threads;
        # if the main thread tells the worker thread "add some events",
        # then *immediately* does a non-blocking check to see if there
        # are events waiting, we're creating a race that we frequently lose.
        blocking = iter(self.scheduler)
        non_blocking = self.scheduler.non_blocking()

        if events:
            # only block the first time
            i = blocking
            for expected, got in zip(events, i):
                assert expected == got
                i = non_blocking
        for unexpected in non_blocking: # pragma: nocover
            raise ValueError(f"no events should have been ready now, but we got {unexpected}")

    def _thread(self):
        q = self.queue
        s = self.scheduler
        r = s.regulator

        o = None

        while self._running:
            if o:
                q.task_done()

            o = q.get()

            if o == ExitThread:
                break

            if callable(o):
                o()
                continue

            if isinstance(o, (int, float)):
                # a time interval, advance the regulator
                r.advance(o)
                continue

            if isinstance(o, tuple):
                event, t, absolute, priority = o
                s.schedule(event, t, absolute=absolute, priority=priority)
                continue

        self._running = False
        t = self.thread
        self.thread = None
        q.task_done()



def test_basics():
    s = big.Scheduler()
    assert not (s)
    s.schedule(0.01, 0.01)
    assert s
    s.schedule(0, 0)
    s.schedule(0.03, 0.03)
    s.schedule(0.02, 0.02)

    values = [e.event for e in s.queue]
    assert values == [0, 0.01, 0.02, 0.03]

    objects = list(s)
    sorted_objects = sorted(objects)
    assert objects == sorted_objects


def test_add_event_after_blocking():
    def test(delta):
        with MockTimeThread() as mtt:
            s = mtt.scheduler
            s.schedule(0.01, 0.01)
            s.schedule(0.05, 0.05)
            assert len(s.queue) == 2

            mtt.wait()
            mtt.schedule(0.03, 0.03)
            for _ in range(10):
                mtt.advance(0.01)

            mtt.assert_ready(0.01, 0.03, 0.05)

    test(0.01)
    test(1)


def test_clear_after_blocking():
    s = big.Scheduler(big.ThreadSafeRegulator())
    e1 = s.schedule(object(), 10)
    e2 = s.schedule(object(), 11)
    e3 = s.schedule(object(), 12)

    def cancel_events():
        time.sleep(0.02)
        e1.cancel()
        e2.cancel()
        e3.cancel()

    t = threading.Thread(target=cancel_events)
    t.start()

    start = time.time()
    for event in s: # pragma: no cover
        event()
    end = time.time()

    assert (end - start) < 1
    t.join()


def test_non_blocking():
    with MockTimeThread() as mtt:
        mtt.schedule(0, 0)
        mtt.schedule('', 0)
        mtt.schedule('5', 5)
        mtt.flush()

        mtt.assert_ready(0, '')

def test_four_threads_sleeping():
    # demonstrates that you can have multiple
    # threads all consuming events.
    #
    # sure... it's's dumb!  don't do it!
    # but it works the way it should.

    r = big.ThreadSafeRegulator()
    events = []
    lock = threading.Lock()

    s = big.Scheduler(r)

    times = [0.02, 0.08, 0.01, 0.06, 0.04, 0.03, 0.05, 0.07]
    for t in times:
        s.schedule(t, t)

    def harvest_two_events(array):
        flag = False
        for event in s:
            with lock:
                events.append(event)
            if flag:
                break
            else:
                flag = True

    threads = []
    for _ in range(3):
        array = []
        t = threading.Thread(target=harvest_two_events, args=(array,))
        array.append(t)
        threads.append(t)
        t.start()

    harvest_two_events(None)

    for t in threads:
        t.join()

    sorted_times = sorted(times)
    assert events == sorted_times

def test_wake_during_the_window():
    # Regression test for a lost-wakeup race in the old
    # ThreadSafeRegulator.  Scheduler._next releases the lock
    # and THEN calls sleep(), so there's a window in which a
    # wake() can fire after a thread has committed to sleeping
    # but before it actually sleeps.  The old wake() was a
    # set-then-clear pulse on a threading.Event: a wake inside
    # the window evaporated, and an event scheduled to occur
    # earlier than the current sleep was delivered late--the
    # exact sched.scheduler bug Scheduler exists to fix.
    #
    # This regulator holds that window open deterministically,
    # exactly as if the OS preempted the consumer there.  The
    # blocker-based regulator passes because wake is a level,
    # not a pulse: the parked release survives the window.

    class WindowedRegulator(big.ThreadSafeRegulator):
        def __init__(self):
            super().__init__()
            self.in_window = threading.Event()
            self.proceed = threading.Event()

        def sleep(self, interval):
            self.in_window.set()
            self.proceed.wait()
            super().sleep(interval)

    regulator = WindowedRegulator()
    s = big.Scheduler(regulator)

    LONG = 1.0
    s.schedule("long", LONG)

    received = []
    def consume():
        for event in s:
            received.append((event, time.monotonic()))
            if len(received) == 2:
                return

    t = threading.Thread(target=consume)
    start = time.monotonic()
    t.start()

    regulator.in_window.wait()      # consumer committed to sleep(~LONG)
    s.schedule("early", 0.01)       # wake fires inside the window
    regulator.proceed.set()
    t.join()

    assert [event for event, when in received] == ["early", "long"]
    early_delivered_at = received[0][1] - start
    assert early_delivered_at < LONG / 2, ("lost wakeup: the early event wasn't delivered "
        "until the original sleep interval expired")

def test_wake_is_a_level_not_a_pulse():
    # A wake with no sleeper parks: the next sleep returns
    # immediately, and its acquire re-arms the blocker.
    # Multiple parked wakes collapse into one, without
    # complaint.
    regulator = big.ThreadSafeRegulator()
    regulator.wake()
    regulator.wake()    # already parked: must not raise

    start = time.monotonic()
    regulator.sleep(5.0)
    assert time.monotonic() - start < 1.0, "a parked wake didn't make sleep return immediately"

    # the gate re-armed: sleeping again really sleeps.
    interval = 0.1
    start = time.monotonic()
    regulator.sleep(interval)
    assert time.monotonic() - start >= interval * 0.5, "the blocker didn't re-arm after a parked wake was consumed"


def test_enter():
    s = big.Scheduler()
    times = [0.05, 0.04, 0.03, 0.02, 0.01]
    for t in times:
        s.schedule(t, t)
    results = []
    for event in s:
        results.append(event)
    sorted_times = sorted(times)
    assert results == sorted_times



def test_enterabs():
    s = big.Scheduler()
    times = [0.05, 0.04, 0.03, 0.02, 0.01]
    start_time = s.regulator.now()
    for t in times:
        s.schedule(t, start_time + t, absolute=True)
    results = []
    for event in s:
        results.append(event)
    sorted_times = sorted(times)
    assert results == sorted_times


def test_enter_concurrent():
    with MockTimeThread() as mtt:

        s = mtt.scheduler
        r = s.regulator

        s.schedule(1, 1)
        s.schedule(3, 3)

        mtt.wait()
        mtt.advance(1)
        mtt.assert_ready(1)

        for t in [4, 5, 2]:
            mtt.schedule(t, t - r.now())

        mtt.wait()
        mtt.advance(2)
        mtt.assert_ready(2, 3)

        mtt.wait()
        mtt.advance(1)
        mtt.assert_ready(4)

        mtt.wait()
        mtt.advance(1)
        mtt.assert_ready(5)

        assert s.queue == []


def test_priority():
    with MockTimeThread() as mtt:
        for priorities, expected in [
            ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
            ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
            ([2, 5, 3, 1, 4], [1, 2, 3, 4, 5]),
            ([1, 2, 3, 2, 1], [1, 1, 2, 2, 3]),
            ]:
            t = 1
            for p in priorities:
                mtt.schedule(p, t, priority=p, absolute=True)
            mtt.advance(10)
            mtt.flush()
            mtt.assert_ready(*expected)

def test_cancel():
    with MockTimeThread() as mtt:
        s = mtt.scheduler
        r = s.regulator
        now = r.now()
        events = []
        for delta in [1, 2, 3, 4, 5]:
            events.append(s.schedule(delta, now+delta, absolute=True))
        events[0].cancel()
        events[-1].cancel()
        r.advance(10)
        mtt.assert_ready(2, 3, 4)

def test_cancel_concurrent():
    with MockTimeThread() as mtt:
        s = mtt.scheduler
        r = s.regulator

        now = r.now()
        events = {}
        for delta in [2, 4, 8, 10, 6]:
            events[delta] = s.schedule(delta, now + delta, absolute=True)

        mtt.wait()
        mtt.advance(2.5) # t=2.5
        mtt.assert_ready(2)

        # cancel 4 and 10
        s.cancel(events[4])
        events[10].cancel()

        mtt.wait()
        mtt.advance(1) # t=3.5
        mtt.assert_ready()

        mtt.wait()
        mtt.advance(1) # t=3.5
        mtt.assert_ready()

        mtt.wait()
        mtt.advance(1) # t=4.5
        mtt.assert_ready()

        mtt.wait()
        mtt.advance(1) # t=5.5
        mtt.assert_ready()

        mtt.wait()
        mtt.advance(1) # t=6.5
        mtt.assert_ready(6)

        mtt.wait()
        mtt.advance(1) # t=7.5
        mtt.assert_ready()

        mtt.wait()
        mtt.advance(1) # t=8.5
        mtt.assert_ready(8)

        assert not (s.queue)


def test_cancel_correct_event():
    # https://github.com/python/cpython/issues/63469
    # (previously https://bugs.python.org/issue19270 )
    for cancel_using_event_method_call in (False, True):
        with MockTimeThread() as mtt:
            s = mtt.scheduler
            events = {}
            for c in 'zdabqc':
                events[c] = s.schedule(c, 0.01, priority=1)
            b = events['b']
            if cancel_using_event_method_call:
                b.cancel()
            else:
                s.cancel(b)
            # Scheduler guarantees that, if two events are
            # scheduled for the same time and have the same
            # priority, they'll be yielded in the order
            # they were added.
            s.regulator.advance(1)
            assert list(s) == list('zdaqc')

def test_empty():
    # Scheduler doesn't have an empty method.
    # Instead it supports __bool__.
    with MockTimeThread() as mtt:
        s = mtt.scheduler
        assert not (s)
        for t in [0.05, 0.04, 0.03, 0.02, 0.01]:
            s.schedule(t, t, absolute=True)
        assert s
        s.regulator.advance(1)
        events = list(s)
        assert not (s)

def test_queue():
    with MockTimeThread() as mtt:
        s = mtt.scheduler
        events = []
        for delta in [0.05, 0.01, 0.02, 0.04, 0.03]:
            events.append(s.schedule(delta, delta))
        events.sort()
        assert s.queue == events

# don't bother with test_args_kwargs,
# big.Scheduler doesn't use callbacks.

def test_run_non_blocking():
    with MockTimeThread() as mtt:
        for t in [10, 9, 8, 7, 6]:
            mtt.schedule(t, t)
        mtt.flush()
        mtt.assert_ready()


def run_tests(run=None):
    (run or bigtestlib.run)(name="big.scheduler", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
