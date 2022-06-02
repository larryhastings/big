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

import calendar
from datetime import datetime, timezone
import dateutil.parser
import time

# I'm on my way, I'm making it

__all__ = []

def export(o):
    __all__.append(o.__name__)
    return o



_timestamp_human_format = "%Y/%m/%d %H:%M:%S"

@export
def timestamp_human(t=None, want_microseconds=None):
    """
    Return a timestamp string formatted in a pleasing way
    using the currently-set local timezone.  This format
    is intended for human readability; for computer-parsable
    time, use timestamp_3339Z().

    Example timestamp:
        '2022/05/24 23:42:49.099437'

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
    ends with microseconds if t is a type that can represent
    fractional seconds: a float, a datetime object, or the
    value None.
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
        if want_microseconds == None:
            want_microseconds = isinstance(t, float)
        t = datetime.fromtimestamp(t)
    elif isinstance(t, datetime):
        if t.tzinfo != None:
            t = t.astimezone(None)
    else:
        raise TypeError(f"unrecognized type {type(t)}")

    if want_microseconds == None:
        # if it's still None, t must be a type that supports microseconds
        want_microseconds = True

    s = t.strftime(_timestamp_human_format)
    if want_microseconds:
        s = f"{s}.{t.microsecond:06d}"
    return s


_timestamp_3339Z_format_base = "%Y-%m-%dT%H:%M:%S"
_timestamp_3339Z_format = f"{_timestamp_3339Z_format_base}Z"
_timestamp_3339Z_microseconds_format = f"{_timestamp_3339Z_format_base}.%fZ"

@export
def timestamp_3339Z(t=None, want_microseconds=None):
    """
    Return a timestamp string in RFC 3339 format, in the UTC
    time zone.  This format is intended for computer-parsable
    timestamps; for human-readable timestamps, use timestamp_human().

    Example timestamp:
        '2022-05-25T06:46:35.425327Z'

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
        t = datetime.fromtimestamp(t, timezone.utc)
        if want_microseconds == None:
            want_microseconds = isinstance(t, float)
    elif isinstance(t, datetime):
        if t.tzinfo != timezone.utc:
            t = t.astimezone(timezone.utc)
    else:
        raise TypeError(f"unrecognized type {type(t)}")

    if want_microseconds == None:
        # if want_microseconds is *still* None,
        # t must be a type that supports microseconds
        want_microseconds = True

    if want_microseconds:
        f = _timestamp_3339Z_microseconds_format
    else:
        f = _timestamp_3339Z_format

    return t.strftime(f)


_parse_timestamp_3339Z_format = "%Y-%m-%dT%H:%M:%S*%z"

@export
def parse_timestamp_3339Z(s):
    """
    Parses a timestamp string returned by timestamp_3339Z.
    Returns a datetime.datetime object.
    """
    return dateutil.parser.parse(s)

