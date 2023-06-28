#!/usr/bin/env python3

_license = """
big
Copyright 2022-2023 Larry Hastings
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

import big.all as big
import unittest
import time

class BigTestLog(unittest.TestCase):

    maxDiff=None

    def test_smoke_test_log(self):
        sleep = time.sleep

        # perform all the lookups first
        # so that the actual logging is as efficient as possible
        log = big.Log()
        log_enter = log.enter
        log_exit = log.exit
        log_print = log.print
        got = []
        got_append = got.append

        log.reset()
        log_enter("subsystem")
        sleep(0.01)
        log('event 1')
        sleep(0.02)
        log('event 2')
        sleep(0.03)
        log_exit()
        log_print(print=got_append, fractional_width=3)

        expected = """
[event log]
  start   elapsed  event
  ------  ------  ---------------
  00.000  00.000  log start
  00.000  00.010  subsystem start
  00.010  00.020    event 1
  00.030  00.030    event 2
  00.060  00.000  subsystem end
        """.strip().split('\n')

        # we can't simply compare text strings.
        # maybe your computer is slow!
        # maybe the scheduler paused the test program for a moment!
        # the final time might be 00.061!
        #
        # so, do this the hard way.

        i_got = iter(got)
        i_expected = iter(expected)

        self.assertEqual(next(i_expected), next(i_got), "error on log line 1: [event log] line didn't match!")
        self.assertEqual(next(i_expected), next(i_got), "error on log line 2: column heading text line didn't match!")
        self.assertEqual(next(i_expected), next(i_got), "error on log line 3: column heading dashes line didn't match!")

        # time should pass by *at least* this much.
        per_line_elapsed = [
            0,
            0.01,
            0.02,
            0.03,
            0.0
            ]

        def split_line(s):
            s = s.strip()
            start_time, _, s = s.partition("  ")
            assert _
            elapsed_time, _, s = s.partition("  ")
            assert _
            return (float(start_time), float(elapsed_time), s)

        expected_start_time = 0
        for line_number, (expected, got, expected_elapsed_time) in enumerate(zip(i_expected, i_got, per_line_elapsed), 4):
            _, _, expected_event = split_line(expected)
            got_start_time, got_elapsed_time, got_event = split_line(got)
            self.assertEqual(got_start_time, expected_start_time, f"error on log line {line_number}: start time didn't match! expected {expected_start_time}, got {got_start_time}")
            self.assertGreaterEqual(got_elapsed_time, expected_elapsed_time, f"error on log line {line_number}: elapsed time didn't match! expected {expected_elapsed_time}, got {got_elapsed_time}")
            self.assertEqual(got_event, expected_event, f"error on log line {line_number}: event didn't match! expected {expected_event!r}, got {got_event!r}")
            expected_start_time += got_elapsed_time



def run_tests():
    bigtestlib.run(name="big.log", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
