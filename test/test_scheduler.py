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

import big
import queue
import unittest
import threading
import time


class MockRegulator:
    def __init__(self):
        self.t = 0
        self.explicit_wake_counter = 0
        self.event = threading.Event()
        self.lock = threading.Lock()

    def __repr__(self): # pragma: no cover
        return f"<MockRegulator t={self.t}>"

    def advance(self, t):
        tid = hex(threading.get_ident())[2:]
        # print(f"  {self} {tid} advance +{t}")
        with self.lock:
            self.t += t
        self.wake()

    def now(self):
        with self.lock:
            return self.t

    def sleep(self, t):
        tid = hex(threading.get_ident())[2:]
        with self.lock:
            t += self.t
            ignore_wake = self.explicit_wake_counter
        # print(f"  {self} {tid} sleep until {t}")
        while True:
            with self.lock:
                now = self.t
                if ignore_wake != self.explicit_wake_counter:
                    # print(f"  {self} {tid} waking, via wake")
                    return
                if t <= now:
                    # print(f"  {self} {tid} waking, timed out")
                    return
            self.event.wait()
            time.sleep(0.01)

    def wake(self):
        tid = hex(threading.get_ident())[2:]
        with self.lock:
            # print(f"  {self} {tid} wake at time {self.t}")
            self.explicit_wake_counter += 1
        self.event.set()
        self.event.clear()



class ScheduleTester(unittest.TestCase):

    def test_basics(self):
        s = big.Scheduler()
        self.assertFalse(s)
        s.schedule(0.01, 0.01)
        self.assertTrue(s)
        s.schedule(0, 0)
        s.schedule(0.03, 0.03)
        s.schedule(0.02, 0.02)

        values = [e.event for e in s.queue]
        self.assertEqual(values, [0, 0.01, 0.02, 0.03])

        objects = list(s)
        sorted_objects = sorted(objects)
        self.assertEqual(objects, sorted_objects)


        with self.assertRaises(ValueError):
            s.schedule(big.scheduler.invalid_event, 5)


    def test_add_event_after_blocking(self):
        s = big.Scheduler()
        s.schedule(0, 0)
        s.schedule(0.05, 0.05)

        def add_0_02():
            time.sleep(0.02)
            s.schedule(0.02, 0.02)

        t = threading.Thread(target=add_0_02)
        t.start()

        events = list(s)
        sorted = list(events)
        sorted.sort()
        self.assertEqual(events, sorted)


    def test_clear_after_blocking(self):
        s = big.Scheduler()
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

        self.assertTrue((end - start) < 1)


    def test_non_blocking(self):
        s = big.Scheduler()
        s.schedule(0, 0)
        s.schedule('', 0)
        s.schedule('5', 5)

        ready = list(s.non_blocking())
        self.assertEqual(ready, [0, ''])


    def test_two_threads_one_array(self):
        # actually three threads.
        # demonstrates that you can have multiple
        # threads all consuming events.
        # that's dumb.  don't do that.
        # but it works the way it should.

        events = []
        lock = threading.Lock()

        s = big.Scheduler()

        times = [0.02, 0.08, 0.01, 0.06, 0.04, 0.03, 0.05, 0.07]
        for t in times:
            s.schedule(t, t)

        def harvest_two_events():
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
            t = threading.Thread(target=harvest_two_events)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        harvest_two_events()

        sorted_times = sorted(times)
        self.assertEqual(events, sorted_times)




class SchedModuleTests(unittest.TestCase):

    # These tests are reimplementations of
    # the sched.scheduler test suite from Python.
    # I want my scheduler to benefit from the
    # 30-year-old mature test suite and avoid
    # all the regressions.
    #
    # (I didn't copy & paste the tests,
    # I rewrote them by hand.)

    def test_enter(self):
        s = big.Scheduler()
        times = [0.05, 0.04, 0.03, 0.02, 0.01]
        for t in times:
            s.schedule(t, t)
        results = []
        for event in s:
            results.append(event)
        sorted_times = sorted(times)
        self.assertEqual(results, sorted_times)


    def test_enterabs(self):
        s = big.Scheduler()
        times = [0.05, 0.04, 0.03, 0.02, 0.01]
        start_time = time.monotonic()
        for t in times:
            s.schedule(t, start_time + t, absolute=True)
        results = []
        for event in s:
            results.append(event)
        sorted_times = sorted(times)
        self.assertEqual(results, sorted_times)


    def test_enter_concurrent(self):
        q = queue.Queue()
        r = MockRegulator()
        s = big.Scheduler(r)
        s.schedule(1, 1)
        s.schedule(3, 3)

        exit_event = object()

        def queue_events():
            # print("  queue_events starting")
            while True:
                for event in s:
                    if event == exit_event:
                        return
                    # print(f"  q.put({event})")
                    q.put(event)
                time.sleep(0.01)

        thread = threading.Thread(target=queue_events)
        thread.start()

        r.advance(1)
        def q_get(): return q.get(timeout=1)
        self.assertEqual(q_get(), 1)
        self.assertTrue(q.empty())
        for t in [4, 5, 2]:
            s.schedule(t, t - r.now())
        r.advance(2)
        self.assertEqual(q_get(), 2)
        self.assertEqual(q_get(), 3)
        self.assertTrue(q.empty())
        r.advance(1)
        self.assertEqual(q_get(), 4)
        self.assertTrue(q.empty())
        r.advance(1)
        self.assertEqual(q_get(), 5)
        self.assertTrue(q.empty())

        s.schedule(exit_event, 1)
        r.advance(100)

        thread.join()
        self.assertTrue(q.empty())

    def test_priority(self):
        s = big.Scheduler()
        for priorities, expected in [
            ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
            ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
            ([2, 5, 3, 1, 4], [1, 2, 3, 4, 5]),
            ([1, 2, 3, 2, 1], [1, 1, 2, 2, 3]),
            ]:
            t = time.monotonic() + 0.01
            for p in priorities:
                s.schedule(p, t, priority=p, absolute=True)
            events = [o for o in s]
            self.assertEqual(events, expected)
            self.assertFalse(s)

    def test_cancel(self):
        s = big.Scheduler()
        t = time.monotonic()
        events = []
        for delta in [0.01, 0.02, 0.03, 0.04, 0.05]:
            events.append(s.schedule(delta, t+delta, absolute=True))
        events[0].cancel()
        events[-1].cancel()
        events = list(s)
        self.assertEqual(events, [0.02, 0.03, 0.04])

    def test_cancel_concurrent(self):
        q = queue.Queue()
        r = MockRegulator()
        s = big.Scheduler(regulator=r)
        now = r.now()
        events = {}
        for delta in [1, 2, 4, 5, 3]:
            events[delta] = s.schedule(delta, now + delta, absolute=True)

        def run():
            for event in s:
                q.put(event)

        t = threading.Thread(target=run)
        t.start()
        r.advance(1)
        def q_get(): return q.get(timeout=1)
        self.assertEqual(q_get(), 1)
        self.assertTrue(q.empty())
        s.cancel(events[2])
        s.cancel(events[5])
        r.advance(1)
        self.assertTrue(q.empty())
        r.advance(1)
        self.assertEqual(q_get(), 3)
        self.assertTrue(q.empty())
        r.advance(1)
        self.assertEqual(q_get(), 4)
        self.assertTrue(q.empty())
        r.advance(1000)
        self.assertTrue(q.empty())
        t.join()
        self.assertTrue(q.empty())

    def test_cancel_correct_event(self):
        # https://github.com/python/cpython/issues/63469
        # (previously https://bugs.python.org/issue19270 )
        for cancel_using_method_on_handle in (False, True):
            s = big.Scheduler()
            handle = {}
            for c in 'abc':
                handle[c] = s.schedule(c, 0.01, priority=1)
            b = handle['b']
            if cancel_using_method_on_handle:
                b.cancel()
            else:
                s.cancel(b)
            self.assertEqual(list(s), ['a', 'c'])

    def test_empty(self):
        # Scheduler doesn't have an empty method.
        # Instead it supports __bool__.
        s = big.Scheduler()
        self.assertFalse(s)
        for t in [0.05, 0.04, 0.03, 0.02, 0.01]:
            s.schedule(t, t, absolute=True)
        self.assertTrue(s)
        events = list(s)
        self.assertFalse(s)

    def test_queue(self):
        s = big.Scheduler()
        now = time.monotonic()
        events = []
        for delta in [0.05, 0.01, 0.02, 0.04, 0.03]:
            events.append(s.schedule(delta, delta))
        events.sort()
        self.assertEqual(s.queue, events)

    # don't bother with test_args_kwargs,
    # big.Scheduler doesn't use callbacks.

    def test_run_non_blocking(self):
        s = big.Scheduler()
        for t in [10, 9, 8, 7, 6]:
            s.schedule(t, t)
        events = []
        for event in s.non_blocking():
            events.append(event) # pragma: no cover
        self.assertEqual(events, [])





import bigtestlib

def run_tests():
    bigtestlib.run(name="big.scheduler", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
