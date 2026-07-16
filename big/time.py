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

# I'm on my way, I'm making it


import calendar
from datetime import date, datetime, timedelta, timezone
import importlib.util
import time

# whether parse_timestamp_3339Z gets defined depends on dateutil
# being available--but *importing* dateutil.parser costs ~4ms, so
# we only probe for it here (find_spec doesn't execute the module)
# and defer the real import to the first parse_timestamp_3339Z call.
try: # pragma: no cover
    have_dateutils = importlib.util.find_spec('dateutil.parser') is not None
except (ImportError, ModuleNotFoundError, ValueError): # pragma: no cover
    have_dateutils = False


from . import builtin
mm = builtin.ModuleManager()
export = mm.export


_timestamp_human_format_with_us = "%Y/%m/%d %H:%M:%S.%f %Z"
_timestamp_human_format_without_us = _timestamp_human_format_with_us.replace('.%f', '')

@export
def timestamp_human(t=None, want_microseconds=None, *, tzinfo=None):
    """
    Return a timestamp string formatted in a pleasing way
    using the currently-set local timezone.  This format
    is intended for human readability; for computer-parsable
    time, use timestamp_3339Z().

    Example timestamp:
        '2021/05/24 23:42:49.099437 PST'

    t can be one of several types:
        If t is None, timestamp_human uses the current local time.

        If t is an int or float, it's interpreted as seconds
          since the epoch.

        If t is a time.struct_time or datetime.datetime object,
          it's converted to the local timezone.

    If want_microseconds is true, the timestamp will end with
    the microseconds, represented as ".######".  If want_microseconds
    is false, the timestamp will not include the microseconds.
    If want_microseconds is None (the default), the timestamp
    ends in microseconds if t is a type that can represent
    fractional seconds (which is any accepted type except int).

    tzinfo is the timezone the timestamp is rendered in; it should
    be a datetime.tzinfo object or None.  None (the default) means
    the currently-set local timezone.
    """
    if isinstance(t, time.struct_time):
        if t.tm_zone == "GMT":
            t = calendar.timegm(t)
        else:
            t = time.mktime(t)
        # force None to False
        want_microseconds = bool(want_microseconds)

    if t is None:
        t = datetime.now()
    elif isinstance(t, (int, float)):
        if want_microseconds is None:
            want_microseconds = isinstance(t, float)
        t = datetime.fromtimestamp(t)
    elif not isinstance(t, datetime):
        raise TypeError(f"unrecognized type {type(t)}")
    # astimezone handles naive and aware datetimes alike: naive
    # datetimes are assumed to be local time, and aware datetimes
    # are *converted*--which is what the docstring promises.
    # (this used to be guarded with "if t.tzinfo is None", so
    # aware datetimes were never converted to the local timezone.)
    t = t.astimezone(tzinfo)

    if want_microseconds is None:
        # if it's still None, t must be a type that supports microseconds
        want_microseconds = True

    if want_microseconds:
        format = _timestamp_human_format_with_us
    else:
        format = _timestamp_human_format_without_us
    s = t.strftime(format)
    return s


_timestamp_3339Z_format_with_us =  "%Y-%m-%dT%H:%M:%S.%fZ"
_timestamp_3339Z_format_without_us = _timestamp_3339Z_format_with_us.replace('.%f', '')

@export
def timestamp_3339Z(t=None, want_microseconds=None):
    """
    Return a timestamp string in RFC 3339 format, in the UTC
    time zone.  This format is intended for computer-parsable
    timestamps; for human-readable timestamps, use timestamp_human().

    Example timestamp:
        '2021-05-25T06:46:35.425327Z'

    t may be one of several types:
      If t is None, timestamp_3339Z uses the current time in UTC.

      If t is an int or a float, it's interpreted as seconds
      since the epoch in the UTC time zone.

      If t is a time.struct_time object or datetime.datetime
      object, and it's not in UTC, it's converted to UTC.
      (Technically, time.struct_time objects are converted to GMT,
      using time.gmtime.  Sorry, pedants!)

    If want_microseconds is true, the timestamp ends with
    microseconds, represented as a period and six digits between
    the seconds and the 'Z'.  If want_microseconds
    is false, the timestamp will not include this text.
    If want_microseconds is None (the default), the timestamp
    ends with microseconds if t is a type that can represent
    fractional seconds: a float, a datetime object, or the
    value None.
    """
    if isinstance(t, time.struct_time):
        if t.tm_zone == "GMT":
            t = calendar.timegm(t)
        else:
            t = time.mktime(t)
        want_microseconds = bool(want_microseconds)

    if t is None:
        t = datetime.now(timezone.utc)
    elif isinstance(t, (int, float)):
        # check t's type *before* replacing it with a datetime!
        # (this check used to come after, so it was always False:
        # floats never got their promised microseconds.)
        if want_microseconds is None:
            want_microseconds = isinstance(t, float)
        t = datetime.fromtimestamp(t, timezone.utc)
    elif isinstance(t, datetime):
        if t.tzinfo != timezone.utc:
            t = t.astimezone(timezone.utc)
    else:
        raise TypeError(f"unrecognized type {type(t)}")

    if want_microseconds is None:
        # if want_microseconds is *still* None,
        # t must be a type that supports microseconds
        want_microseconds = True

    if want_microseconds:
        format = _timestamp_3339Z_format_with_us
    else:
        format = _timestamp_3339Z_format_without_us
    s = t.strftime(format)
    return s


@export
def duration_human(t, *, long=True, want_microseconds=None):
    """
    Return an elapsed time formatted as a human-readable string,
    breaking it into days, hours, minutes, and seconds.  The long
    format reads like prose, joined with Oxford comma rules--two
    units get a bare 'and', three or more get commas with ', and'
    before the last:

        >>> duration_human(90)
        '1 minute and 30 seconds'
        >>> duration_human(90061)
        '1 day, 1 hour, 1 minute, and 1 second'

    Pass in a false value for long to get the short format:

        >>> duration_human(90, long=False)
        '1m 30s'
        >>> duration_human(90061, long=False)
        '1d 1h 1m 1s'

    t should be a number of seconds, either int or float,
    or a datetime.timedelta object.

    Days are the largest unit; a long duration is a large
    number of days ('365 days and 6 hours').  Units are included
    starting at the largest nonzero unit and stopping at the
    last nonzero unit; zero units in the middle are included,
    so every rendered duration reads unambiguously:

        >>> duration_human(3600, long=False)
        '1h'
        >>> duration_human(3601, long=False)
        '1h 0m 1s'

    A zero duration is '0 seconds' (or '0s').  A negative
    duration is formatted like a positive one, with a
    leading '-'.

    want_microseconds controls sub-second precision, and may be
    None (the default), True, or False:

      * True means seconds are rendered with microsecond
        precision.  Fractional seconds appear only when nonzero,
        rounded to microsecond precision, with trailing zeroes
        removed ('1.5 seconds', never '1.500000 seconds').
      * False means seconds are rendered as whole seconds: the
        duration is rounded to the nearest second, ties rounding
        up (away from zero).
      * None means want_microseconds decides for itself: it's
        True if the total duration is less than one minute, and
        False otherwise.  While a duration is short enough that
        fractions of a second matter, you get them; once it
        grows a minutes column, you don't:

        >>> duration_human(1.5)
        '1.5 seconds'
        >>> duration_human(90061.5)
        '1 day, 1 hour, 1 minute, and 2 seconds'
        >>> duration_human(90061.5, want_microseconds=True)
        '1 day, 1 hour, 1 minute, and 1.5 seconds'

    The integer arithmetic is exact, so rounding can never
    produce a nonsense duration like '59.9999999 seconds' or
    '60 seconds': 59.9999999 seconds renders as '1 minute'.
    """
    if isinstance(t, timedelta):
        t = t.total_seconds()
    elif not isinstance(t, (int, float)):
        raise TypeError(f"unrecognized type {type(t)}")

    if t < 0:
        sign = '-'
        t = -t
    else:
        sign = ''

    if want_microseconds is None:
        want_microseconds = t < 60

    microseconds = round(t * 1000000)
    seconds, microseconds = divmod(microseconds, 1000000)
    if not want_microseconds:
        # round to the nearest whole second; ties round up.
        seconds += microseconds >= 500000
        microseconds = 0
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    if microseconds:
        fraction = format(microseconds, '06').rstrip('0')
        # a string, but that's fine: pluralize formats it with
        # {}, and a fractional count is never equal to 1, so
        # it's always correctly plural.
        seconds_value = f"{seconds}.{fraction}"
    else:
        seconds_value = seconds

    if long:
        rendered = [
            (days,                       builtin.pluralize(days, 'day')),
            (hours,                      builtin.pluralize(hours, 'hour')),
            (minutes,                    builtin.pluralize(minutes, 'minute')),
            (seconds or microseconds,    builtin.pluralize(seconds_value, 'second')),
            ]
        zero = '0 seconds'
    else:
        rendered = [
            (days,                       f"{days}d"),
            (hours,                      f"{hours}h"),
            (minutes,                    f"{minutes}m"),
            (seconds or microseconds,    f"{seconds_value}s"),
            ]
        zero = '0s'

    # strip leading and trailing zero units; keep interior zeros.
    while rendered and (not rendered[0][0]):
        del rendered[0]
    while rendered and (not rendered[-1][0]):
        del rendered[-1]

    if not rendered:
        return zero
    strings = [s for value, s in rendered]
    if long:
        # the long format joins like prose, Oxford comma rules:
        # two units get a bare 'and', three or more get commas
        # with ', and' before the last.
        trailing = strings.pop()
        if len(strings) > 1:
            leading = ', '.join(strings)
            joined = f'{leading}, and {trailing}'
        elif strings:
            joined = f'{strings[0]} and {trailing}'
        else:
            joined = trailing
    else:
        joined = ' '.join(strings)
    return sign + joined


@export
def datetime_set_timezone(d, timezone):
    """
    Returns a new datetime.datetime object identical
    to d but with its tzinfo set to timezone.
    """
    # replace copies every field (fold included), swapping tzinfo.
    return d.replace(tzinfo=timezone)

@export
def datetime_ensure_timezone(d, timezone):
    """
    Ensures that a datetime.datetime object has
    a timezone set.

    If d has a timezone set, returns d.
    Otherwise, returns a new datetime.datetime
    object equivalent to d with its tzinfo set
    to timezone.
    """
    if d.tzinfo:
        return d
    return datetime_set_timezone(d, timezone)

if have_dateutils:
    @export
    def parse_timestamp_3339Z(s, *, timezone=None):
        """
        Parses a timestamp string returned by timestamp_3339Z.
        Returns a datetime.datetime object.

        timezone is an optional default timezone, and should
        be a datetime.tzinfo object (or None).  If provided,
        and the time represented in the string doesn't specify
        a timezone, the 'tzinfo' attribute of the returned object
        will be explicitly set to timezone.
        """
        import dateutil.parser
        d = dateutil.parser.parse(s)
        d = datetime_ensure_timezone(d, timezone)
        return d

mm()
