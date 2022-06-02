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
import datetime
import re
import time
import unittest

class BigTests(unittest.TestCase):

    def test_timestamp_human(self):
        human_re = re.compile(r"^(\d\d\d\d)/\d\d/\d\d \d\d:\d\d:\d\d(\.\d\d\d\d\d\d)?$")
        for t in (
            big.timestamp_human(),
            big.timestamp_human(None),
            ):
            self.assertTrue(t)
            match = human_re.match(t)
            self.assertTrue(match)
            self.assertGreaterEqual(int(match.group(1)), 2022)

        with self.assertRaises(TypeError):
            big.timestamp_human('abcde')

        # Q: timestamp_human deliberately uses the local time zone.
        # but specifying the time using an int or float (in any of
        # a number of ways) is in UTC.  how do we figure out the
        # correct UTC time so that we can get a consistent time
        # (e.g. Jan 1st 1970)
        #
        # A: pick a time, e.g. the epoch.  create a datetime object
        # set at that time, and ask it what the UTC offset is for
        # that moment.  then subtract that offset from the UTC int/float
        # time.  that gives you the UTC int/float time that renders
        # in the local timezone for the value you want.
        zero = 0
        aware = datetime.datetime(1970, 1, 1).astimezone()
        if aware.tzinfo:
            zero -= int(aware.utcoffset().total_seconds())
            float_zero = float(zero)

            epoch = "1970/01/01 00:00:00"
            epoch_with_microseconds = f"{epoch}.000000"
            self.assertEqual(big.timestamp_human(zero), epoch)
            self.assertEqual(big.timestamp_human(float_zero), epoch_with_microseconds)
            self.assertEqual(big.timestamp_human(time.gmtime(float_zero)), epoch)
            self.assertEqual(big.timestamp_human(time.localtime(float_zero)), epoch)
            self.assertEqual(big.timestamp_human(datetime.datetime.fromtimestamp(zero)), epoch_with_microseconds)
            self.assertEqual(big.timestamp_human(datetime.datetime.fromtimestamp(zero, datetime.timezone.utc)), epoch_with_microseconds)

            self.assertEqual(big.timestamp_human(datetime.datetime(1234, 5, 6, 7, 8, 9, microsecond=123456)), "1234/05/06 07:08:09.123456")

    def test_timestamp_3339Z(self):
        re_3339z = re.compile(r"^(\d\d\d\d)-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d\d\d\d\d\d)?Z$")
        for t in (
            big.timestamp_3339Z(),
            big.timestamp_3339Z(None),
            ):
            self.assertTrue(t)
            match = re_3339z.match(t)
            self.assertTrue(match)
            self.assertGreaterEqual(int(match.group(1)), 2022)

        epoch = "1970-01-01T00:00:00Z"
        epoch_with_microseconds = epoch.replace('Z', ".000000Z")
        self.assertEqual(big.timestamp_3339Z(0), epoch)
        self.assertEqual(big.timestamp_3339Z(0.0), epoch)
        self.assertEqual(big.timestamp_3339Z(time.gmtime(0.0)), epoch)
        self.assertEqual(big.timestamp_3339Z(time.localtime(0.0)), epoch)
        self.assertEqual(big.timestamp_3339Z(datetime.datetime.fromtimestamp(0)), epoch_with_microseconds)
        self.assertEqual(big.timestamp_3339Z(datetime.datetime.fromtimestamp(0, datetime.timezone.utc)), epoch_with_microseconds)

        self.assertEqual(big.timestamp_3339Z(datetime.datetime(1234, 5, 6, 7, 8, 9, tzinfo=datetime.timezone.utc, microsecond=123456)), "1234-05-06T07:08:09.123456Z")

        with self.assertRaises(TypeError):
            big.timestamp_3339Z('abcde')

    def test_parse_timestamp_3339Z(self):
        datetimes = []
        for seconds in range(2):
            datetimes.append(datetime.datetime(1970, 1, 1, 0, 0, seconds, tzinfo=datetime.timezone.utc))
        self.assertEqual(big.parse_timestamp_3339Z("1970-01-01T00:00:00Z"), datetimes[0])
        self.assertEqual(big.parse_timestamp_3339Z("1970-01-01T00:00:00.000000Z"), datetimes[0])
        self.assertEqual(big.parse_timestamp_3339Z("1970-01-01T00:00:01.000000Z"), datetimes[1])
        self.assertEqual(big.parse_timestamp_3339Z("2022-05-29T05:40:24Z"), datetime.datetime(2022, 5, 29, 5, 40, 24, tzinfo=datetime.timezone.utc))


import bigtestlib

def run_tests():
    bigtestlib.run(name="big.time", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
