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

import builtins
import big.all as big
import unittest
import time

def fake_clock():
    def fake_clock():
        time = 0
        while True:
            yield time
            time += 12_000_000 # add twelve milliseconds
    return fake_clock().__next__

class BigTestLog(unittest.TestCase):

    maxDiff=None

    def test_smoke_test_log(self):
        clock = fake_clock()
        log = big.Log(clock=clock)

        log.reset()
        log.enter("subsystem")
        log('event 1')
        clock()
        log('event 2')
        log.exit()
        got = []
        log.print(print=got.append, fractional_width=3)

        expected = """
[event log]
  start   elapsed  event
  ------  ------  ---------------
  00.000  00.012  log start
  00.012  00.012  subsystem start
  00.024  00.024    event 1
  00.048  00.012    event 2
  00.060  00.000  subsystem end
        """.strip().split('\n')

        self.assertEqual(expected, got)

        i_got = iter(got)
        i_expected = iter(expected)

        per_line_elapsed = [
            0.012,
            0.012,
            0.024,
            0.012,
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
        for line_number, (expected, got, expected_elapsed_time) in enumerate(zip(i_expected, i_got, per_line_elapsed)):
            if line_number < 3:
                self.assertEqual(expected, got)
                continue
            _, _, expected_event = split_line(expected)
            got_start_time, got_elapsed_time, got_event = split_line(got)
            self.assertEqual(got_start_time, expected_start_time, f"error on log line {line_number}: start time didn't match! expected {expected_start_time}, got {got_start_time}")
            self.assertGreaterEqual(got_elapsed_time, expected_elapsed_time, f"error on log line {line_number}: elapsed time didn't match! expected {expected_elapsed_time}, got {got_elapsed_time}")
            self.assertEqual(got_event, expected_event, f"error on log line {line_number}: event didn't match! expected {expected_event!r}, got {got_event!r}")
            expected_start_time += got_elapsed_time

    def test_default_settings(self):
        log = big.Log()
        log('event 1')
        buffer = []
        real_print = builtins.print
        builtins.print = buffer.append
        log.print()
        builtins.print = real_print
        got = "\n".join(buffer)
        self.assertIn("event 1", got)


def run_tests():
    bigtestlib.run(name="big.log", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
