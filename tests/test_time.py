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

from big.test import raises

import big.all as big
import datetime
import re
import time


def test_timestamp_human():
    human_re = re.compile(r"^(\d\d\d\d)/\d\d/\d\d \d\d:\d\d:\d\d(\.\d\d\d\d\d\d)? [A-Z]+$")
    for t in (
        big.timestamp_human(),
        big.timestamp_human(None),
        ):
        assert t
        match = human_re.match(t)
        assert match
        assert int(match.group(1)) >= 2022

    with raises(TypeError):
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
    utc = datetime.timezone.utc
    zero = 0
    aware = datetime.datetime(1970, 1, 1).astimezone(utc)
    if aware.tzinfo:
        zero -= int(aware.utcoffset().total_seconds())
        float_zero = float(zero)

        epoch = "1970/01/01 00:00:00 UTC"
        epoch_with_microseconds = epoch.replace(":00 ", ":00.000000 ")
        assert big.timestamp_human(zero, tzinfo=utc) == epoch
        assert big.timestamp_human(float_zero, tzinfo=utc) == epoch_with_microseconds
        assert big.timestamp_human(time.gmtime(float_zero), tzinfo=utc) == epoch
        assert big.timestamp_human(time.localtime(float_zero), tzinfo=utc) == epoch
        assert big.timestamp_human(datetime.datetime.fromtimestamp(zero), tzinfo=utc) == epoch_with_microseconds
        assert big.timestamp_human(datetime.datetime.fromtimestamp(zero, utc), tzinfo=utc) == epoch_with_microseconds

        est = datetime.timezone(datetime.timedelta(hours=-5), "EST")

        # rendering in the datetime's own zone still works--by
        # asking for that zone.
        assert big.timestamp_human(datetime.datetime(1234, 5, 6, 7, 8, 9, microsecond=123456, tzinfo=est), tzinfo=est) == "1234/05/06 07:08:09.123456 EST"

        # regression: aware datetimes are *converted* to the
        # requested timezone, as the docstring always promised.
        # (they used to be rendered in their own zone--only
        # naive datetimes were converted.)
        midnight_est = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=est)
        assert big.timestamp_human(midnight_est, want_microseconds=False, tzinfo=utc) == "1970/01/01 05:00:00 UTC"

def test_timestamp_3339Z():
    re_3339z = re.compile(r"^(\d\d\d\d)-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d\d\d\d\d\d)?Z$")
    for t in (
        big.timestamp_3339Z(),
        big.timestamp_3339Z(None),
        ):
        assert t
        match = re_3339z.match(t)
        assert match
        assert int(match.group(1)) >= 2022

    epoch = "1970-01-01T00:00:00Z"
    epoch_with_microseconds = epoch.replace('Z', ".000000Z")
    assert big.timestamp_3339Z(0) == epoch
    # regression: a float gets microseconds, as the docstring
    # always promised.  (the type check used to run *after*
    # t was replaced with a datetime, so it never fired, and
    # this test used to pin the broken no-microseconds output.)
    assert big.timestamp_3339Z(0.0) == epoch_with_microseconds
    assert big.timestamp_3339Z(1.5) == "1970-01-01T00:00:01.500000Z"
    # explicit want_microseconds still overrides in both directions
    assert big.timestamp_3339Z(0.0, want_microseconds=False) == epoch
    assert big.timestamp_3339Z(0, want_microseconds=True) == epoch_with_microseconds
    assert big.timestamp_3339Z(time.gmtime(0.0)) == epoch
    assert big.timestamp_3339Z(time.localtime(0.0)) == epoch
    assert big.timestamp_3339Z(datetime.datetime.fromtimestamp(0)) == epoch_with_microseconds
    assert big.timestamp_3339Z(datetime.datetime.fromtimestamp(0, datetime.timezone.utc)) == epoch_with_microseconds


    assert big.timestamp_3339Z(datetime.datetime(1234, 5, 6, 7, 8, 9, tzinfo=datetime.timezone.utc, microsecond=123456)) == "1234-05-06T07:08:09.123456Z"

    with raises(TypeError):
        big.timestamp_3339Z('abcde')

def test_duration_human():
    def test(t, long, short):
        # long format is the default
        assert big.duration_human(t) == long
        assert big.duration_human(t, long=True) == long
        assert big.duration_human(t, long=False) == short

    # zero, in every accepted type
    test(0, '0 seconds', '0s')
    test(0.0, '0 seconds', '0s')
    test(-0.0, '0 seconds', '0s')
    test(datetime.timedelta(0), '0 seconds', '0s')

    # single units; exactly 1 is singular
    test(1, '1 second', '1s')
    test(60, '1 minute', '1m')
    test(3600, '1 hour', '1h')
    test(86400, '1 day', '1d')
    test(2, '2 seconds', '2s')

    # leading and trailing zero units are stripped,
    # interior zero units are kept
    test(90, '1 minute and 30 seconds', '1m 30s')
    test(3601, '1 hour, 0 minutes, and 1 second', '1h 0m 1s')
    test(3660, '1 hour and 1 minute', '1h 1m')
    test(86402, '1 day, 0 hours, 0 minutes, and 2 seconds', '1d 0h 0m 2s')
    test(90061, '1 day, 1 hour, 1 minute, and 1 second', '1d 1h 1m 1s')

    # days are the largest unit
    test(31557600, '365 days and 6 hours', '365d 6h')

    # fractional seconds appear only when nonzero, with
    # trailing zeroes removed--and a fractional count is
    # always plural
    test(1.0, '1 second', '1s')
    test(1.5, '1.5 seconds', '1.5s')
    test(0.5, '0.5 seconds', '0.5s')
    test(0.000001, '0.000001 seconds', '0.000001s')
    # float noise is rounded away at microsecond precision
    test(0.1 + 0.2, '0.3 seconds', '0.3s')
    # rounding is exact and carries: never '59.9999999s', never '60s'
    test(59.9999999, '1 minute', '1m')
    test(59.999999, '59.999999 seconds', '59.999999s')

    # negative durations
    test(-1, '-1 second', '-1s')
    test(-75, '-1 minute and 15 seconds', '-1m 15s')
    test(-0.5, '-0.5 seconds', '-0.5s')

    # timedelta objects
    test(datetime.timedelta(days=2, hours=3, seconds=4), '2 days, 3 hours, 0 minutes, and 4 seconds', '2d 3h 0m 4s')
    test(-datetime.timedelta(hours=1), '-1 hour', '-1h')

    with raises(TypeError):
        big.duration_human('90')
    with raises(TypeError):
        big.duration_human(None)

def test_duration_human_want_microseconds():
    t = big.duration_human

    # want_microseconds=None (the default): microsecond precision
    # while the total duration is under one minute, whole seconds
    # once it isn't
    assert t(59.5) == '59.5 seconds'
    assert t(60.5) == '1 minute and 1 second'                 # 60.5 rounds up
    assert t(60.4) == '1 minute'                          # rounds to a bare minute
    assert t(90061.5) == '1 day, 1 hour, 1 minute, and 2 seconds'
    assert t(90061.5, long=False) == '1d 1h 1m 2s'
    # the threshold is on the total duration's magnitude
    assert t(-59.5) == '-59.5 seconds'
    assert t(-60.5) == '-1 minute and 1 second'

    # want_microseconds=True: microsecond precision at any scale
    assert t(90061.5, want_microseconds=True) == '1 day, 1 hour, 1 minute, and 1.5 seconds'
    assert t(90061.5, long=False, want_microseconds=True) == '1d 1h 1m 1.5s'
    assert t(datetime.timedelta(minutes=1, milliseconds=500), want_microseconds=True) == '1 minute and 0.5 seconds'
    # ...but a whole-number duration still renders without a fraction
    assert t(90.0, want_microseconds=True) == '1 minute and 30 seconds'

    # want_microseconds=False: whole seconds at any scale;
    # ties round up, away from zero
    assert t(1.5, want_microseconds=False) == '2 seconds'
    assert t(1.4, want_microseconds=False) == '1 second'
    assert t(0.5, want_microseconds=False) == '1 second'
    assert t(0.4, want_microseconds=False) == '0 seconds'
    assert t(-1.5, want_microseconds=False) == '-2 seconds'
    assert t(0.4, long=False, want_microseconds=False) == '0s'
    # rounding carries into the minutes column exactly
    assert t(59.5, want_microseconds=False) == '1 minute'

try:
    from big.time import parse_timestamp_3339Z
    def test_parse_timestamp_3339Z():
        utc = datetime.timezone.utc
        datetimes = []
        for seconds in range(2):
            datetimes.append(datetime.datetime(1970, 1, 1, 0, 0, seconds, tzinfo=utc))
        assert big.parse_timestamp_3339Z("1970-01-01T00:00:00Z") == datetimes[0]
        assert big.parse_timestamp_3339Z("1970-01-01T00:00:00.000000Z") == datetimes[0]
        assert big.parse_timestamp_3339Z("1970-01-01T00:00:01.000000Z") == datetimes[1]
        assert big.parse_timestamp_3339Z("2022-05-29T05:40:24Z") == datetime.datetime(2022, 5, 29, 5, 40, 24, tzinfo=datetime.timezone.utc)

        naive = datetime.datetime(1970, 1, 1, 0, 0, 0)
        assert big.parse_timestamp_3339Z("1970-01-01T00:00:00.000000") == naive
        aware = big.datetime_set_timezone(naive, utc)
        assert big.parse_timestamp_3339Z("1970-01-01T00:00:00.000000Z") == aware
        assert aware == big.datetime_ensure_timezone(naive, utc)
        assert aware == big.datetime_ensure_timezone(aware, utc)
except ImportError: # pragma: no cover
    pass


def run_tests(run=None):
    (run or bigtestlib.run)(name="big.time", module=__name__)

if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
