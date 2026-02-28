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


import atexit
import builtins
from io import TextIOBase
from itertools import zip_longest
import os
from pathlib import Path
from queue import Queue
import tempfile
from threading import current_thread, Lock, Thread
import time

from . import time as big_time
from . import file as big_file
from . import template as big_template


from . import builtin
mm = builtin.ModuleManager()
export = mm.export

base = builtin.ClassRegistry()

try:
    # 3.7+
    from time import monotonic_ns as default_clock
except ImportError: # pragma: no cover
    # 3.6 compatibility
    from time import monotonic
    def default_clock():
        return int(monotonic() * 1_000_000_000.0)

export('default_clock')



@export
class SinkEvent(tuple):
    """
    Abstract base class for Log events stored by the Sink destination.

    SinkEvent is a tuple subclass.  Subclasses are immutable
    and define only the fields relevant to their event type.
    """

    __slots__ = ()

    def __repr__(self):
        fields = []
        for name in self._field_names:
            value = getattr(self, name)
            fields.append(f"{name}={value!r}")
        return f"{self.__class__.__name__}({', '.join(fields)})"

    def __lt__(self, other):
        if not isinstance(other, SinkEvent):
            raise TypeError(f"'<' not supported between instances of SinkEvent and {type(other)}")
        return (
                (self.session  <= other.session)
            and (self.elapsed <  other.elapsed)
            )


@export
class SinkStartEvent(SinkEvent):

    __slots__ = ()

    type = 'start'

    _field_names = ('session', 'ns', 'epoch', 'configuration', 'duration')

    def __new__(cls, session, ns, epoch, configuration, duration=0):
        return tuple.__new__(cls, (session, ns, epoch, configuration, duration))

    @property
    def session(self):
        return self[0]

    @property
    def ns(self):
        return self[1]

    @property
    def epoch(self):
        return self[2]

    @property
    def configuration(self):
        return self[3]

    @property
    def duration(self):
        return self[4]

    @property
    def elapsed(self):
        return 0

    @property
    def depth(self):
        return 0

    def __hash__(self):
        return hash((self.session, self.ns, self.epoch))

    def _calculate_duration(self, next_event):
        return SinkStartEvent(
            self.session, self.ns, self.epoch, self.configuration,
            next_event.elapsed - self.elapsed,
            )


@export
class SinkEndEvent(SinkEvent):

    __slots__ = ()

    type = 'end'

    _field_names = ('session', 'elapsed')

    def __new__(cls, session, elapsed):
        return tuple.__new__(cls, (session, elapsed))

    @property
    def session(self):
        return self[0]

    @property
    def elapsed(self):
        return self[1]

    @property
    def depth(self):
        return 0


@export
class SinkWriteEvent(SinkEvent):

    __slots__ = ()

    type = 'write'

    _field_names = ('session', 'depth', 'elapsed', 'thread', 'formatted', 'duration')

    def __new__(cls, session, depth, elapsed, thread, formatted, duration=0):
        return tuple.__new__(cls, (session, depth, elapsed, thread, formatted, duration))

    @property
    def session(self):
        return self[0]

    @property
    def depth(self):
        return self[1]

    @property
    def elapsed(self):
        return self[2]

    @property
    def thread(self):
        return self[3]

    @property
    def formatted(self):
        return self[4]

    @property
    def duration(self):
        return self[5]

    def _calculate_duration(self, next_event):
        return SinkWriteEvent(
            self.session, self.depth, self.elapsed,
            self.thread, self.formatted,
            next_event.elapsed - self.elapsed,
            )


@export
class SinkLogEvent(SinkEvent):

    __slots__ = ()

    type = 'log'

    _field_names = ('session', 'depth', 'elapsed', 'thread', 'format', 'message', 'formatted', 'duration')

    def __new__(cls, session, depth, elapsed, thread, format, message, formatted, duration=0):
        return tuple.__new__(cls, (session, depth, elapsed, thread, format, message, formatted, duration))

    @property
    def session(self):
        return self[0]

    @property
    def depth(self):
        return self[1]

    @property
    def elapsed(self):
        return self[2]

    @property
    def thread(self):
        return self[3]

    @property
    def format(self):
        return self[4]

    @property
    def message(self):
        return self[5]

    @property
    def formatted(self):
        return self[6]

    @property
    def duration(self):
        return self[7]

    def _calculate_duration(self, next_event):
        return SinkLogEvent(
            self.session, self.depth, self.elapsed,
            self.thread, self.format, self.message, self.formatted,
            next_event.elapsed - self.elapsed,
            )


@export
class SinkEnterEvent(SinkEvent):

    __slots__ = ()

    type = 'enter'

    _field_names = ('session', 'depth', 'elapsed', 'thread', 'message', 'duration')

    def __new__(cls, session, depth, elapsed, thread, message, duration=0):
        return tuple.__new__(cls, (session, depth, elapsed, thread, message, duration))

    @property
    def session(self):
        return self[0]

    @property
    def depth(self):
        return self[1]

    @property
    def elapsed(self):
        return self[2]

    @property
    def thread(self):
        return self[3]

    @property
    def message(self):
        return self[4]

    @property
    def duration(self):
        return self[5]

    def _calculate_duration(self, next_event):
        return SinkEnterEvent(
            self.session, self.depth, self.elapsed,
            self.thread, self.message,
            next_event.elapsed - self.elapsed,
            )


@export
class SinkExitEvent(SinkEvent):

    __slots__ = ()

    type = 'exit'

    _field_names = ('session', 'depth', 'elapsed', 'thread', 'duration')

    def __new__(cls, session, depth, elapsed, thread, duration=0):
        return tuple.__new__(cls, (session, depth, elapsed, thread, duration))

    @property
    def session(self):
        return self[0]

    @property
    def depth(self):
        return self[1]

    @property
    def elapsed(self):
        return self[2]

    @property
    def thread(self):
        return self[3]

    @property
    def duration(self):
        return self[4]

    def _calculate_duration(self, next_event):
        return SinkExitEvent(
            self.session, self.depth, self.elapsed,
            self.thread,
            next_event.elapsed - self.elapsed,
            )


_sep = " "
_end = "\n"

_spaces = _sep * 1024


@export
def prefix_format(time_seconds_width, time_fractional_width, thread_name_width=12):
    """
    Formats a "prefix" string for use with a Log object.

    The format it returns is in the form:
        "[{elapsed} {thread.name}] "
    formatted with these widths:
         "[{time_seconds_width}.{time_fractional_width} {thread_name_width}]"
    For example, the default value for Log.prefix is prefix_format(3, 10, 12),
    which looks like this in the final log:
        "[003.0706368860   MainThread]"
    """
    # the +1 is for the dot between seconds and fractional seconds
    time_width = time_seconds_width + 1 + time_fractional_width
    return f'[{{elapsed:0{time_width}.{time_fractional_width}f}} {{thread.name:>{thread_name_width}}}] '


class _EmptyThread:
    name = ''
    ident = ''
    native_id = ''
    daemon = ''
    def __repr__(self):
        return ''
    def __str__(self):
        return ''

_empty_thread = _EmptyThread()

def _none_format(*args):
    return ''


##
## It's better than bad, it's good!
##

@export
class Log:
    """
    A lightweight text-based thread-safe log, suitable for debugging.

    Log is a logging object, intended for debugging.
    It's not a full-fledged application logger like
    Python's "logging" module; instead, it's intended
    for debug-print-style use.  It's high performance,
    adding as little overhead to your program as possible,
    and offers a great deal of flexibility in where the
    log is written, and when.

    To use, simply create a Log instance, then call it:
        j = Log()
        j("Hello, world!")
    By default, Log writes its log to stdout, using builtins.print.

    As shown in the above example, calling the Log instance as a
    function logs a message to the log.  The signature of this
    function is identical to Log.print; both have a signature
    similar to builtins.print.

    Log supports these methods to write to the log:

        Log.print(*a, sep=' ', end='\n', flush=False, format='print')
            Identical to calling the Log object.

        Log.box(s)
            Logs s to the log, with a three-sided box around it to
            call attention to this particular message.

        Log.enter(s)
        Log.exit()
            Log.enter logs s to the log, formatted with a box around
            it, and then indents the log.  exit outdents the log and
            prints a trailing box marking the end of the indented
            section.  Log.enter also returns a "context manager";
            if you use this as the argument to a "with" statement,
            exiting the "with" block will call Log.exit().

        Log.write(formatted)
            Writes "formatted" directly to the log with no
            further formatting or modification.

    Log also supports these method calls, which don't directly
    log a message:

        Log.flush()
            Flush all internal buffers currently in use by the log,
            if any formatted text has been written to the log since
            the last time it was flushed (or since the start of the log).

        Log.close()
            Close the log, which writes an "end" event to the log.
            When a log is closed, you can no longer write to it;
            all writes are silently ignored, and no error is reported.

        Log.reset()
            Resets the log to its initial state.  Log.reset() is the
            only way to reopen a "closed" log, although you may reset
            a log at any time.

    If you pass one or more positional arguments to the Log
    constructor, these define "destinations" for log messages.
    The log will send logged messages to every destination
    after every logging call.  Destination objects can be
    any of the following types / objects:

        print (the Python builtin function)
            Log messages are printed using print(s, end='').
            This is the default.  Equivalent to
            big.log.Log.Print().
        str, bytes, or pathlib.Path object
            Log messages are buffered locally,
            and dumped to the file named by the string.
            Equivalent to big.log.Log.File(pathlib.Path(destination)).
            (If the destination is a bytes object, it's encoded
            using os.fsencode.)
        list object
            Log messages are appended to the list.  Equivalent
            to big.log.Log.List(destination).
        io.TextIOBase object
            Log messages are written to the file-like object
            using its write method.  Equivalent to
            big.log.Log.FileHandle(destination).
        callable object
            The callable object is called with every log message.
            Equivalent to big.log.Log.Callable(destination).
        big.log.TMPFILE
            A special precreated sentinel value. Log messages will be
            logged to a temporary file with a dynamically-computed path.
            The file is created in your designated temporary directory;
            it starts with the Log name, followed by the start time of
            the log, then the PID of the process, and ends with ".txt".
        Destination object
            Log messages are passed on to the Destination object.

    If you don't pass in any explicit destinations, Log behaves
    as if you'd passed in "print".

    The following are all keyword-only parameters to the
    Log constructor, used to adjust the behavior of the log,
    and they are all available as read-only properties of
    the log:

    "name" is the desired name for this log (default 'Log').

    If "threading" is true (the default), log messages aren't logged
    immediately; they're minimally processed, then sent to a logging
    thread maintained internally by the Log object which fully formats
    and logs the message.  This reduces the overhead for logging a
    message resulting in faster logging performance.  If threading is
    false, log messages are formatted and logged immediately in the
    Log call, using a threading.Lock() object to ensure thread safety.
    (Log is always thread-safe, whether or not "threading" is true.)

    "indent" should be an integer, the number of spaces to indent by
    when indenting the log (using Log.enter).  Default is 4.

    "width" should be an integer, default is 79.  This is only used
    with {line} in a "template" in a format dict.

    "clock" should be a function returning nanoseconds since some
    arbitrary past event. The default value is time.monotonic_ns
    for Python 3.7, and a locally-defined compatibility function
    for Python 3.6 (returning time.monotonic() * one billion).

    "timestamp_clock" should be a function returning seconds since the
    UNIX epoch, as a floating-point number with fractional seconds.
    The default value is time.time.

    "timestamp_format" should be a function that formats
    float-seconds-since-epoch into a pleasant human-readable format.
    Default is big.time.timestamp_human.

    "prefix" should be a string used to format text inserted
    at the beginning of every log message.  Default is
    big.Log.prefix_format(3, 10, 12).

    "formats" should be a dict mapping strings to format dicts.
    A "format dict" is itself a dict with two supported values:
    "template", and optionally "line", both strings.  "template"
    specifies a string that will be used to format log messages;
    if you call Log.print(foo, format="peanut"), this will use
    the format dict specified by Log(format={"peanut": {...}}).

    The "template" string in the format dict is processed using
    the ".format" method on a string, with the following values defined:

        elapsed
            The elapsed time since the log was started,
            as float-seconds.
        line
            The value of the "line" value from the format dict.
            If this is the last thing on a line inside the format
            (immediately before a '\n', or is the last character
            in the format string), the "line" value will be repeated
            until the line is >= Log.width, and the line will then
            be truncated at Log.width characters.
        message
            The message that was logged.
        name
            The "name" of the log passed in to the Log constructor.
        prefix
            A string pre-formatted using the "prefix" format
            string passed in to the Log constructor.
        thread
            A handle to the thread that logged this message.
        time
            The time of the log message, as float-seconds-since-epoch.
        timestamp
            The "time" value, formatted using the "timestamp_format"
            callable passed in to the Log constructor.

    Log has six pre-defined formats:
        print
            the default format, used by log.print() and log()
        box
            used by log.box()
        enter
            used by log.enter()
        exit
            used by log.exit()
        start
            used for the initial log message when the log is opened
        end
            used for the final log message when the log is closed

    You may also add your own user-defined formats; simply add these
    to the dict you pass in as the format parameter.  The Log instance
    will add a method with the name of format which logs using this
    format, if the format name passes an .isinstance() check, and
    there isn't already an attribute on Log with that name;
    this is how log.box() is implemented.

    To suppress the banners printed for "start", "end", "enter",
    or "exit" messages, pass in a dict to the formats parameter
    with that format name set to None.  To suppress both the start
    and end banners:
        Log(formats={"start": None, "end": None})
    """

    def __init__(self, *destinations,
            name='Log',
            threading=True,
            paused=False,

            indent=4,
            width=79,

            clock=default_clock,
            timestamp_clock=time.time,
            timestamp_format=big_time.timestamp_human,

            prefix=prefix_format(3, 10, 12),
            formats={},
            ):

        t1 = clock()
        start_time_epoch = timestamp_clock()
        t2 = clock()
        start_time_ns = (t1 + t2) // 2

        if not isinstance(name, str):
            raise TypeError('name must be a non-empty str')
        if not name:
            raise ValueError('name must be a non-empty str')

        self._name = name
        self._threading = threading
        self.paused_on_reset = bool(paused)
        self._paused_counter = int(self.paused_on_reset)

        self._clock = clock
        self._timestamp_clock = timestamp_clock

        self._indent = indent
        self._width = width

        self._prefix = prefix
        self._spaces = ''
        self._timestamp_format = timestamp_format

        self._formats_parameter = formats

        self._nesting = []

        # "_original_destinations" is literally what the user passed in.
        # (if they didn't pass in any, it behaves like they passed in [print].)
        # this contains None if they specified None.
        #
        # "_unwrapped_destinations" is just "original" with None stripped out.
        #
        # "_destinations" is "original", but any non-Destination value
        #     has been map_destination'd.  It's "wrapped destinations".
        self._original_destinations = []
        self._unwrapped_destinations = []
        self._destinations = []
        self._dormant = set()
        self._logging = set()
        self._dirty = set()

        self._parse_formats(formats)

        self._reset(start_time_ns, start_time_epoch)

        # if threading is True, _lock is only used for close and reset (and shutdown)
        self._lock = Lock()

        self._reroute(destinations)

        self._manage_thread()

        atexit.register(self._atexit)


    @classmethod
    def base_destination_mapper(cls, o):
        "Implements the default mapping of objects to Destination objects."

        if o is None:
            return None
        if isinstance(o, cls.Destination):
            return o
        if o is print:
            return cls.Print()
        if isinstance(o, (bytes, str, Path)):
            return cls.File(o)
        if isinstance(o, list):
            return cls.List(o)
        if isinstance(o, TextIOBase):
            return cls.FileHandle(o)
        if callable(o):
            return cls.Callable(o)
        raise TypeError(f"don't know how to log to destination {o!r}")

    destination_mappers = []

    @classmethod
    def map_destination(cls, o):
        """
        Wraps objects of various supported types
        with appropriate Destination objects.

        This is extensible with the class attribute
        Log.destination_mappers, a list.  Append your
        own mapper function(s) to this list and they'll
        be called by map_destination.  The function should
        take a single object, the destination, and return
        either the correct Destination object to handle
        that object or None.
        """
        for mapper in cls.destination_mappers:
            result = mapper(o)
            if result is not None:
                return result

        return cls.base_destination_mapper(o)

    def _reroute(self, destinations):
        old = set(self._destinations)

        original_destinations = list(destinations)

        print = builtins.print
        if not destinations:
            unwrapped_destinations = [print]
        else:
            unwrapped_destinations = [o for o in original_destinations if o is not None]
        wrapped_destinations = []
        destinations_append = wrapped_destinations.append
        new = set()
        new_add = new.add

        for d in unwrapped_destinations:
            assert d is not None
            wrapped = Log.map_destination(d)
            if wrapped in new:
                raise ValueError(f"duplicate destination {d!r}")
            new_add(wrapped)
            destinations_append(wrapped)

        added = new - old
        for d in wrapped_destinations:
            if d in added:
                d.register(self)
        self._dormant.update(added)

        removed = old - new
        # not ready yet!
        assert not removed

        unchanged = old & new

        self._original_destinations = original_destinations
        self._unwrapped_destinations = unwrapped_destinations
        self._destinations = wrapped_destinations

    @property
    def destinations(self):
        with self._lock:
            return list(self._original_destinations)

    @destinations.setter
    def destinations(self, destinations):
        if not isinstance(destinations, (list, tuple)):
            raise TypeError(f"destinations must be list or tuple, not {type(destinations).__name__}")

        try:
            blocker = Lock()
            blocker.acquire()
            notify = blocker.release

            self._dispatch([(self._reroute, (destinations,))], notify=notify)

        finally:
            if notify:
                blocker.acquire()


    @property
    def clock(self):
        return self._clock

    @property
    def indent(self):
        return self._indent

    @property
    def name(self):
        return self._name

    @property
    def prefix(self):
        return self._prefix

    @property
    def formats(self):
        return self._formats_parameter

    @property
    def threading(self):
        return self._threading

    @property
    def timestamp_format(self):
        return self._timestamp_format

    @property
    def timestamp_clock(self):
        return self._timestamp_clock

    @property
    def width(self):
        return self._width

    @property
    def dirty(self):
        return bool(self._dirty)

    def _closed(self):
        return self._state in ('closed', 'exited')

    @property
    def closed(self):
        with self._lock:
            return self._closed()

    @property
    def start_time_ns(self):
        with self._lock:
            return self._start_time_ns

    @property
    def start_time_epoch(self):
        with self._lock:
            return self._start_time_epoch

    @property
    def end_time_epoch(self):
        with self._lock:
            return self._end_time_epoch

    @property
    def nesting(self):
        with self._lock:
            return tuple(self._nesting)

    @property
    def depth(self):
        with self._lock:
            return len(self._nesting)

    class _ResumeContextManager:
        """
        The context manager returned by Log.pause().  Calls Log.resume() on exit.
        """
        def __init__(self, log):
            assert log
            self._log = log

        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_value, traceback):
            self._log.resume()

    class _ExitContextManager:
        """
        The context manager returned by Log.enter().  Calls Log.exit() on exit.
        """
        def __init__(self, log):
            assert log
            self._log = log

        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_value, traceback):
            self._log.exit()

    class _InertContextManager:
        """
        The context manager returned by Log.enter() when the log is paused.  Does nothing.
        """
        def __init__(self, log):
            assert log

        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    @property
    def paused(self):
        "Returns True if the log is paused, None if the log is closed, and otherwise False."
        with self._lock:
            if self._closed():
                return None
            return bool(self._paused_counter)

    def pause(self):
        """
        Pauses the log if it's not closed.

        If the log is not closed, this pauses the log
        (if it's not already paused), and returns a context
        manage that calls Log.resume().

        A paused log ignores calls to log methods
        (write, print, __call__, enter, and exit).

        Pause state is internally stored as an integer;
        pause increments it, resume decrements it (but not below zero),
        and if it's greater than zero the log is paused.

        If the log is closed, this function does nothing,
        and it returns a context manager that also does nothing.
        """
        # modifications of _paused_counter are always under lock
        # so we don't have race conditions with incr/decr
        with self._lock:
            if self._closed():
                return self._InertContextManager(self)

            self._paused_counter += 1
            return self._ResumeContextManager(self)

    def resume(self):
        """
        Resumes the log if it's not closed.

        If the log is not closed, and is currently paused,
        this resumes (un-pauses) the log.

        A paused log ignores calls to log methods
        (write, print, __call__, enter, and exit).

        Pause state is internally stored as an integer;
        pause increments it, resume decrements it (but not below zero),
        and if it's greater than zero the log is paused.

        If the log is closed, this function does nothing.
        """
        # modifications of _paused_counter are always under lock
        # so we don't have race conditions with incr/decr
        with self._lock:
            if self._closed():
                return

            if self._paused_counter <= 1:
                # clamp to zero
                self._paused_counter = 0
                return

            self._paused_counter -= 1

    def _elapsed(self, t):
        # t should be a value returned by _clock.
        # returns t converted to elapsed time
        # since self.start_time_ns, as integer nanoseconds.
        return t - self._start_time_ns

    def _ns_to_float(self, ns):
        return ns / 1_000_000_000.0

    def _parse_formats(self, formats):
        base_formats = {
            "box" : {
                "template": '{prefix}+{line*}\n{prefix}| {message}\n{prefix}+{line*}',
                "line*": '-',
            },
            "end" : {
                "template": '{double*}\n{name} finish at {timestamp}\n{double*}',
                "double*": '=',
            },
            "enter": {
                "template": '{prefix}+-----+{line*}\n{prefix}|enter| {message}\n{prefix}|     | {message}\n{prefix}+-----+{line*}',
                "line*": '-',
            },
            "exit": {
                "template": '{prefix}+-----+{line*}\n{prefix}|exit | {message}\n{prefix}|     | {message}\n{prefix}+-----+{line*}',
                "line*": '-',
            },
            "print": {
                "template": '{prefix}{message}',
                "line*": '',
            },
            "start": {
                "template": '{double*}\n{name} start at {timestamp}\n{double*}',
                "double*": '=',
            },
        }

        result = {}

        for key, value in formats.items():
            if not isinstance(key, str):
                raise TypeError(f"formats dict contains {key!r}, formats dict keys must be str")

            if value is None:
                if key not in ("start", "end", 'enter', 'exit'):
                    raise ValueError("None is only a valid value for 'start', 'end', 'enter', and 'exit' formats")
                base_formats.pop(key, None)
                result[key] = _none_format
            else:
                if not isinstance(value, dict):
                    raise TypeError(f"format values must be dict or None, but formats[{key!r}] is type {type(value).__name__}")
                if 'message' in value:
                    raise ValueError(f"format dict for {key!r} must not contain 'message'")
                if 'template' not in value:
                    raise ValueError(f"format dict for {key!r} must contain 'template'")
                template = value['template']
                if not isinstance(template, str):
                    raise TypeError(f"format dict template values must be str, but formats[{key!r}]['template'] is type {type(template).__name__}")
                base_formats[key] = dict(value)

        for key, d in base_formats.items():
            template = d.pop('template')
            result[key] = big_template.Formatter(template, d, width=self._width).format_map

            if isinstance(key, str) and key.isidentifier() and (not hasattr(self, key)):
                def make_method(key):
                    def method(message=''):
                        time = self._clock()
                        thread = current_thread()
                        if not self._paused_counter:
                            self._dispatch([(self._log, (time, thread, key, str(message)))])
                    method.__doc__ = f"Writes a message to the log using the {key!r} format."
                    return method
                setattr(self, key, make_method(key))

        self._formats = result


    def _format_message(self, elapsed, thread, format, message, *, nesting=None):
        epoch = elapsed + self._start_time_epoch

        if nesting is None:
            spaces = self._spaces
        else:
            spaces = self._compute_spaces(nesting)

        map = {
            "elapsed": self._ns_to_float(elapsed),
            "name": self._name,
            "spaces": spaces,
            "thread": thread if thread is not None else _empty_thread,
            "time": epoch,
            "timestamp": self._timestamp_format(epoch),
            }

        prefix = self._prefix.format_map(map) + spaces
        map['prefix'] = prefix

        format = self._formats[format]
        formatted = format(message, map)
        if not formatted:
            return formatted
        # rstrip all lines before returning
        return "\n".join(s.rstrip() for s in formatted.split('\n')) + "\n"


    def _compute_spaces(self, nesting):
        return _spaces[:len(nesting) * self._indent]

    def _cache_spaces(self):
        self._spaces = self._compute_spaces(self._nesting)

    def _append_nesting(self, message):
        self._nesting.append(message)
        self._cache_spaces()

    def _pop_nesting(self):
        message = self._nesting.pop()
        self._cache_spaces()
        return message

    def _clear_nesting(self):
        self._nesting.clear()
        self._spaces = ''


    def _execute(self, work):
        for job in work:
            if job is None:
                return True
            fn, args = job
            fn(*args)
        return False

    def _worker_thread(self, q):
        get = q.get

        while True:
            work = get()
            if self._execute(work):
                return

    def _manage_thread(self):
        if not self._threading:
            self._queue = self._thread = None
            return

        self._queue = Queue()
        self._thread = Thread(target=self._worker_thread, args=(self._queue,), daemon=True)
        self._thread.start()

    def _stop_thread(self):
        if self._threading:
            with self._lock:
                if self._thread:
                    thread = self._thread
                    queue = self._queue
                    self._thread = self._queue = None
                    if thread is not None:
                        queue.put([None])
                        thread.join()

    def _atexit(self):
        clock = self._clock
        ns1 = clock()
        epoch = self._timestamp_clock()
        ns2 = clock()
        ns = (ns1 + ns2) // 2

        self._ensure_state('exited', ns, epoch)
        self._stop_thread()


    def _dispatch(self, work, *, notify=None):
        """
        Causes the log to execute "work", in threaded or non-threaded mode.

        All methods on a Log object that interact with the log are
        implemented using "work" objects.  A "work" object is a
        list of jobs:
            [job, job2, ...]
        These "job" objects are 2-tuples:
             (callable, args)

        The work is executed like so:

            for callable, args in work:
                callable(*args)

        If threaded is True, the work is sent to the worker
        thread.  If threaded is False, the work is executed
        immediately, in the current thread, while holding self._lock.

        None is also a legal "job"; it must be the last "job"
        in a work list.  If threaded is True, this causes the
        worker thread to exit; if threaded is False, it causes
        the dispatch call to return immediately.

        Why send sequences of jobs?  Why not queue jobs
        individually?  The sequence ensures that jobs from
        multiple threads don't get interleaved.  For example,
        Log.enter() logs the "enter" message and indents the log.
        If we queued them separately, we could have a race with
        another thread trying to log something; that other thread
        could get its message logged after the "enter" message but
        before the indent!  By sending both jobs in a list all at
        once, we guarantee that no job from another thread gets
        queued between these two jobs.

        _dispatch also takes a notify argument.  If it's true,
        it must be a callable; barring catastrophe, _dispatch
        guarantees the notify callable will be called at some
        point after the work has been completed.
        """
        if not self._thread:
            try:
                self._execute(work)
            finally:
                if notify:
                    notify()
            return

        lock = None
        try:
            if notify:
                lock = self._lock
                lock.acquire()

                # what if there's a race between this dispatch call
                # and _atexit closing the thread?  _atexit will only
                # set self._thread to None while holding the lock.
                # now that we hold the lock, we know for certain.
                # if self._thread is now false, recursively call
                # ourselves, which will now execute the work directly.
                # (it's all on one line to make coverage happy; this
                # situation is devilishly hard to reproduce.  if only
                # there were some library that made it easy to reproduce
                # race conditions...!)
                if not self._thread: lock.release() ; lock = None ; self._dispatch(work, notify=notify); return

                work.append( (notify, ()) )

            self._queue.put(work)

        finally:
            if lock:
                lock.release()


    def _log_banner(self, format, time):
        elapsed = self._elapsed(time)
        formatted = self._format_message(elapsed, None, format, '')

        if not formatted:
            return

        for destination in self._destinations:
            destination.log(elapsed, None, format, '', formatted)
        self._dirty.update(self._destinations)

    def _log_end_banner(self):
        self._log_banner('end', self._end_time_ns)

    def _start(self):
        for destination in self._destinations:
            destination.start(self._start_time_ns, self._start_time_epoch)
        self._log_banner('start', self._start_time_ns)

    class _StartEvents:
        """
        An object used to track the starting events for a log, e.g.
            * "start" event
            * the start banner "log" event
            * however-many "enter" events

        Log guarantees that it sends a "start" event to the destinations
        before it sends them any formatted text (via "log" or "write").
        However, if we *never* send any formatted text, we don't want
        to send that "start" event, either.

        Log starts in 'initial' state, and automatically transitions
        to 'logged' state once we send *any* formatted text to the
        destinations.  So Log uses this _StartEvents object to buffer
        up initial events that we want to send ONLY if we ever log some
        formatted text.  At the moment we have confirmed formatted text
        to send, if we're still in 'initial' state, we flush all the
        events we buffered inside _StartEvents.

        Specifically, we use this object to buffer up
            * the "start" event
            * the "start banner" log event
            * any number of "enter" events

        (It's unlikely, but possible, for the format for "enter" to
        produce no text.  That's the only scenario in which we'd buffer
        "enter" events.)
        """
        def __init__(self, log):
            self.log = log
            self.works = []

        def append(self, work):
            self.works.append(work)

        def pop(self):
            return self.works.pop()

        def send(self, destination):
            for work in self.works:
                for job in work:
                    name, args = job
                    method = getattr(destination, name)
                    method(*args)


    def _reset(self, start_time_ns, start_time_epoch):
        self._state = 'initial'

        self._start_time_ns = start_time_ns
        self._start_time_epoch = start_time_epoch
        self._end_time_ns = None
        self._end_time_epoch = None

        self._dirty.clear()

        self._start_events = start_events = self._StartEvents(self)

        work = [ ( 'start', (self._start_time_ns, self._start_time_epoch) )]

        elapsed = self._elapsed(self._start_time_ns)
        formatted = self._format_message(elapsed, None, 'start', '')
        if formatted:
            work.append( ( 'log', (elapsed, None, 'start', '', formatted) ))
        start_events.append(work)


    def _ensure_logging(self, destination):
        in_dormant = destination in self._dormant
        in_logging = destination in self._logging
        assert (int(in_dormant) + int(in_logging)) == 1
        if in_logging:
            return False

        self._dormant.remove(destination)
        self._logging.add(destination)
        self._start_events.send(destination)
        return True

    def _ensure_dormant(self, destination, time, thread, cache=None):
        in_dormant = destination in self._dormant
        in_logging = destination in self._logging
        assert (int(in_dormant) + int(in_logging)) == 1
        if in_dormant:
            return False

        self._logging.remove(destination)
        self._dormant.add(destination)

        # if you're calling _ensure_dormant in a loop,
        # you are gonna use the same time each time,
        # so the events will all be the same,
        # so pass in cache=a_list (initially empty)
        # and we'll cache the work in the "cache".

        if cache is None:
            work = []
        else:
            work = cache
        append = work.append

        if not work:
            faux_nesting = list(self._nesting)

            elapsed = self._elapsed(time)
            force_flush = False

            while faux_nesting:
                # exit out of all entered subsystems
                append(( 'exit', (elapsed, thread) ))

                message = faux_nesting.pop()

                formatted = self._format_message(elapsed, thread, 'exit', message, nesting=faux_nesting)
                if formatted:
                    append(( 'log', (elapsed, thread, 'exit', message, formatted) ))
                    force_flush = True


            # send end banner
            formatted = self._format_message(elapsed, None, 'end', '', nesting=faux_nesting)
            if formatted:
                append(( 'log', (elapsed, thread, 'end', '', formatted) ))
                force_flush = True

            # we'll handle the optionality when we run the work
            append( force_flush )

            append(( 'end', (elapsed,) ))

        for job in work:
            if (job is False) or (job is True):
                if job or (destination in self._dirty):
                    destination.flush()
                    self._dirty.discard(destination)
                continue

            name, args = job
            method = getattr(destination, name)
            method(*args)

        return True



    def _ensure_closed(self, ns, epoch, state):
        """
        Ensure the Log is in its closed state, regardless of current state.

        Always called from a thread holding self._lock,
        though that probably isn't necessary for correctness.
        (It's only in case the _atexit handler gets called
        while we're already executing a state transition.)
        """

        if self._state in ('closed', 'exited'):
            return

        self._end_time_ns = ns
        self._end_time_epoch = epoch

        work_cache = []
        if self._logging:
            for destination in self._destinations:
                self._ensure_dormant(destination, self._end_time_ns, None, work_cache)

        self._clear_nesting()

        self._state = state
        assert self._closed()


    def _ensure_state(self, state, ns=None, epoch=None):
        # four states:
        #
        #     initial
        #        The initial state.  Log starts out in initial,
        #        and Log.reset() returns to initial.
        #        Reachable from closed and logged.
        #
        #     logged
        #        We have ever logged formatted text.
        #        Only reachable from initial.
        #
        #     closed
        #        Log has been closed.  Reachable from initial
        #        and logged.
        #
        #     exited
        #        Log's _atexit handler has been called;
        #        the process is shutting down.
        #        Only reachable from closed.
        #        Is a terminal state; you can't transition
        #        out of it.
        #
        assert state in ('initial', 'logged', 'closed', 'exited')

        # fast path: we're already in the correct state
        if self._state == state:
            return True

        # exited is a terminal state.
        if self._state == 'exited':
            return False

        # always hold the lock while changing state.
        # (just in case the _atexit handler gets called
        # while we're doing a state transition.)
        if not self._threading:
            lock = None
        else:
            lock = self._lock
            lock.acquire()
            # this should be impossible; it could only happen
            # if two threads were in a race to simultaneously
            # ensure state 'exited', and that could never happen...
            # right?  only the _atexit handler attempts to ensure
            # state 'exited', and you should never get _atexit
            # handler calls from any thread except the main thread.
            assert self._state != 'exited'

        try:

            if state == 'initial':
                # because of the above ifs, we already know
                # we're not in 'initial' or 'exited'.
                # that means we're in 'logged' or 'closed'.
                # we're transitioning backwards!
                assert ns is not None
                assert epoch is not None

                if self._state == 'logged':
                    self._ensure_closed(ns, epoch, 'closed')
                self._reset(ns, epoch)
                return True

            # we're not in the correct state,
            # and we're not trying to get to 'initial'.
            # therefore we're making a forwards transition.
            if self._state == 'initial':
                if state in ('closed', 'exited'):
                    # we're transitioning directly from 'initial' to 'closed' or 'exited'.
                    # we don't need to do any intermediary stuff.
                    self._ensure_closed(ns, epoch, state)
                    return True

                # transition to 'logged':
                # flush buffered initial events.
                self._state = 'logged'

                if state == 'logged':
                    assert ns is None
                    assert epoch is None
                    return True

            if self._state == 'logged':
                self._ensure_closed(ns, epoch, 'closed')

                if state == 'closed':
                    return True

            assert self._state == 'closed'
            if state == 'logged':
                # it's illegal to transition directly from closed to logged,
                # you have to go through initial first (by resetting)
                return False

            assert state == 'exited'
            # transition to exited
            self._state = 'exited'

            return True

        finally:
            if lock:
                lock.release()


    def reset(self):
        """
        Resets the log to 'initial' state.

        If the log is currently in "initial" state,
        this is a no-op.

        If the log is currently in "closed" state,
        resets it.

        If the log is currently in "logged" state,
        closes it, then resets it.

        If the log is currently in "exited" state,
        reset silently fails--the Log doesn't change state.
        """
        clock = self._clock
        ns1 = clock()
        epoch = self._timestamp_clock()
        ns2 = clock()
        ns = (ns1 + ns2) // 2

        # do this immediately, don't wait for the thread to do it.
        # otherwise, user might observe a delay between reset()
        # and paused state changing.
        #
        # modifications of _paused_counter are always under lock
        # so we don't have race conditions with incr/decr
        with self._lock:
            self._paused_counter = int(bool(self.paused_on_reset))

        self._dispatch( [(self._ensure_state, ('initial', ns, epoch)),] )

    def _flush(self, blocker=None):
        if self._dirty:
            for destination in self._destinations:
                if destination in self._dirty:
                    destination.flush()
            self._dirty.clear()

    def flush(self, wait=True):
        """
        Flushes the log, if it's open and dirty.

        If the log is in "logged" state, and it's
        "dirty" (any formatted text has been logged
        to the log since either the log was started
        or since the last flush), flushes the log.

        If wait=True (the default), flush won't
        return until the log is flushed.  If wait=False,
        the log may be flushed asynchronously.
        """
        try:
            if not wait:
                notify = None
            else:
                blocker = Lock()
                blocker.acquire()
                notify = blocker.release

            self._dispatch([(self._flush, ())], notify=notify)

        finally:
            if notify:
                blocker.acquire()

    def close(self, wait=True):
        """
        Closes the log, if it's open.

        This ensures the log is in "closed" state.
        When the log is in "closed" state, it ignores
        all writes to the log; if you want to write
        to the log after it has been closed, you must
        call the reset() method to reset the log.

        If the log is currently in "closed" state,
        this is a no-op.

        If the log is currently in "logged" state,
        closes the log.

        If the log is currently in "initial" state,
        opens then closes the log.

        If wait=True (the default), close won't
        return until the log is closed.  If wait=False,
        the log may be closed asynchronously.
        """
        try:
            ns1 = self._clock()
            epoch = self._timestamp_clock()
            ns2 = self._clock()
            ns = (ns1 + ns2) // 2

            if not wait:
                notify = None
            else:
                blocker = Lock()
                blocker.acquire()
                notify = blocker.release

            self._dispatch([(self._ensure_state, ('closed', ns, epoch))], notify=notify)

        finally:
            if notify:
                blocker.acquire()


    def _write(self, time, thread, formatted):
        # we should only call _write if we have formatted text.
        assert formatted

        if not self._ensure_state('logged'):
            return

        elapsed = self._elapsed(time)

        dormant = self._dormant
        any_dormant = bool(dormant)

        for destination in self._destinations:
            if any_dormant and (destination in dormant):
                self._ensure_logging(destination)
            destination.write(elapsed, thread, formatted)
        self._dirty.update(self._destinations)

    def write(self, formatted):
        """
        Writes a pre-formatted message directly to the log.

        The "formatted" string is written directly to the
        log; it isn't formatted or modified in any way.
        """

        time = self._clock()
        thread = current_thread()

        if not isinstance(formatted, str):
            raise TypeError('formatted must be str')

        if formatted and (not self._paused_counter):
            self._dispatch( [(self._write, (time, thread, formatted)),] )

    def _log(self, time, thread, format, message):
        """
        Reformats a message and writes it to the log.

        If the user calls this:
            log.print("abc", "def\nghi", sep='\n\n')

        This is lightly pre-formatted (all *args arguments
        are converted to str), then dispatched using _dispatch
        to log._print.  log._print handles combining the args,
        sep, and end, and calls _log with the resulting string:
            _log(time, thread, format, "abc\n\ndef\nghi")

        _log applies the format to the "message" (the fourth parameter).
        It splits the "format" by lines, and also splits the message
        by lines.  Every line of the "format" gets formatted using
        _format_s.  If the line doesn't contain "{message}", it's logged
        once; if the line contains "{message}", it is re-formatted
        with each line of the message and each of these is logged.

        Thus, if the format was "++ START\n// {message}\n-- END",
        this would eventually call every destination D with:
            D.log(elapsed, thread, "++ START")
            D.log(elapsed, thread, "// abc")   # <-- the middle line of
            D.log(elapsed, thread, "//")       # <-- "format", which contains
            D.log(elapsed, thread, "// def")   # <-- "{message}", once for each
            D.log(elapsed, thread, "// ghi")   # <-- line in the message string
            D.log(elapsed, thread, "-- END")
        """

        elapsed = self._elapsed(time)
        formatted = self._format_message(elapsed, thread, format, message)
        if not (formatted and self._ensure_state('logged')):
            return

        dormant = self._dormant
        any_dormant = bool(dormant)

        for destination in self._destinations:
            if any_dormant and (destination in dormant):
                self._ensure_logging(destination)
            destination.log(elapsed, thread, format, message, formatted)
        self._dirty.update(self._destinations)


    def _print(self, time, thread, args, sep, end, flush, format):
        joined = sep.join(args).rstrip()
        if end is _end:
            end = ''
        elif end.endswith('\n'):
            end = end[:-1]
        message = f"{joined}{end}"

        self._log(time, thread, format, message)


    def __call__(self, *args, sep=_sep, end=_end, flush=False, format='print'):
        """
        Logs a message, with the interface of builtins.print.

        The arguments are formatted into a string as follows:
            formatted = sep.join(str(a) for a in args) + end
        This "formatted" string is then logged,
        using the "format" specified.

        If "flush" is a true value, the log is flushed after logging
        this message.
        """

        time = self._clock()
        thread = current_thread()

        str_args = [str(a) for a in args]
        if (sep is not _sep) and (not isinstance(sep, str)):
            raise TypeError(f"sep must be str, not {type(sep).__name__}")
        if (end is not _end) and (not isinstance(end, str)):
            raise TypeError(f"end must be str, not {type(end).__name__}")
        flush = bool(flush)
        if format not in self._formats:
            raise ValueError(f"undefined format {format!r}")
        if format in ('start', 'end', 'enter', 'exit'):
            raise ValueError(f"system format {format!r} can't be used with log.print or log.__call__")

        if not self._paused_counter:
            self._dispatch([(self._print, (time, thread, str_args, sep, end, flush, format))])

    def print(self, *args, end=_end, sep=_sep, flush=False, format='print'):
        """
        Logs a message, with the interface of builtins.print.

        The arguments are formatted into a string as follows:
            formatted = sep.join(str(a) for a in args) + end
        This "formatted" string is then logged,
        using the "format" specified.

        If "flush" is a true value, the log is flushed after logging
        this message.
        """
        return self(*args, end=end, sep=sep, flush=flush, format=format)


    # "with log:" simply flushes the log on exit.
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.flush()


    def _enter(self, time, thread, message):
        # race condition: enter() checks that we're not closed.
        # if we're not closed, it dispatches _enter.
        # we could close the log between that check and here.
        # hard to reproduce! but if I make it a one-liner,
        # coverage considered it visited and I can still get 100%.
        if self._closed(): return

        in_logged_state = self._ensure_state('logged')
        assert in_logged_state

        elapsed = self._elapsed(time)
        formatted = self._format_message(elapsed, thread, 'enter', message)
        formatted_is_nonempty = bool(formatted)

        self._append_nesting(message)

        work = []
        if formatted_is_nonempty:
            work.append( ('log', (elapsed, thread, 'enter', message, formatted) ))
        work.append( ('enter', (elapsed, thread, message) ))
        self._start_events.append(work)

        dormant = self._dormant
        any_dormant = bool(dormant)

        for destination in self._destinations:
            if any_dormant and (destination in dormant):
                if formatted_is_nonempty:
                    self._ensure_logging(destination)
                continue
            if formatted_is_nonempty:
                destination.log(elapsed, thread, 'enter', message, formatted)
            destination.enter(elapsed, thread, message)

        if formatted_is_nonempty:
            self._dirty.update(self._destinations)

    def enter(self, message):
        """
        Logs a message, then indents the log.
        """
        time = self._clock()
        thread = current_thread()

        with self._lock:
            if self._closed() or self._paused_counter:
                return self._InertContextManager(self)

        self._dispatch([(self._enter, (time, thread, str(message)))])
        return self._ExitContextManager(self)


    def _exit(self, time, thread):
        in_logged_state = self._ensure_state('logged')
        assert in_logged_state
        if not self._nesting:
            return

        message = self._pop_nesting()

        elapsed = self._elapsed(time)
        formatted = self._format_message(elapsed, thread, 'exit', message)
        formatted_is_nonempty = bool(formatted)
        formatted_is_empty = not formatted_is_nonempty

        dormant = self._dormant
        any_dormant = bool(dormant)

        for destination in self._destinations:
            if any_dormant and (destination in dormant):
                if formatted_is_empty:
                    continue
                self._ensure_logging(destination)

            destination.exit(elapsed, thread)
            if formatted_is_nonempty:
                destination.log(elapsed, thread, 'exit', message, formatted)

        if formatted_is_nonempty:
            self._dirty.update(self._destinations)

        self._start_events.pop()

    def exit(self):
        """
        Outdents the log from the most recent Log.enter() indent.
        """
        time = self._clock()
        thread = current_thread()

        if not self._paused_counter:
            self._dispatch([(self._exit, (time, thread))])


    class Destination:
        """
        Base class for objects that do the actual logging for a big.Log.

        A Destination object is "owned" by a Log, and the Log sends it
        "events" by calling named methods.  All Destination objects *must*
        support the "write" event, by implementing a write method:

            write(elapsed, thread, formatted)

        In addition, Destination subclasses may optionally override
        the following six events / methods:

            log(self, elapsed, thread, format, message, formatted)
            flush()
            start(start_time_ns, start_time_epoch)
            end(elapsed)
            enter(elapsed, thread, message)
            exit(elapsed, thread)

        For all these methods, Destination subclasses need not
        call the base class method.  The last six are do-nothing
        functions (just "pass").  log is the only one where the
        default implementation does something:

            def log(self, elapsed, thread, format, message, formatted):
                self.write(elapsed, thread, formatted)

        If you don't want this behavior, simply override log
        and *don't* super().log.

        Finally, Destination subclasses may also override these methods:

            register(owner)
            unregister()

        But for these two methods, Destination subclasses are *required*
        to call the base class implementation ("super().register(owner)",
        "super().unregister()"). Destination subclasses that implement
        __super__ must also call the base class __init__; the base class
        __init__ takes no arguments.

        The meaning of each argument to the above Destination methods:

        * elapsed is the elapsed time since the log was
          started/reset, in nanoseconds.
        * thread is the threading.Thread handle for the thread
          that logged the message.  This is None when the message
          isn't associated with a thread, for example the "start"
          and "end" banner messages.
        * formatted is the formatted log message.
        * format is the name of the "format" applied to "message"
          to produce "formatted".
        * message is the original message passed in to the Log
          method that sent this event.
        * owner is the Log object that owns this Destination.
          (A Destination can't be shared between multiple Log
          objects.)

        Log guarantees that the following events will be called in this
        order:

           register
              |
              +
              |
              v
            start<- - - - - - - - - - - - - - - - - - +
              |                                       :
              +<---------------------------------+    :
              |                                  |    :
              v                                  |    :
            write | log | enter | exit | flush   |    :
              |                                  |    :
              |                                  |    :
              +----------------------------------+    :
              |                                       :
              v                                       :
           [flush]                                    :
              |                                       :
              v                                       :
             end- - - - - - - - - - - - - - - - - - - +
              :
              :
              v
          unregister

        The "register" event is sent while the log is still in
        its "initial" state; all other events are sent while the
        log is in "logged" state.  (The log transitions to
        "closed" state only *after* sending the "end" event.)
        "register" will only ever be sent once, and it is always
        the first event received by a Destination.

        The log transitions from "initial" to "logged" only
        after it's logged to for the first time.  It transitions
        to its "logged" state, sends a "start" event, then
        sends the actual logged message.  Once the log has been
        started in this way, it can send any number of "write",
        "log", "enter", "exit", or "flush" events, in any order.

        When the user closes the log, it will send an "end" event
        to the destination.  If the destination is "dirty", Log
        will send the destination a "flush" before the "end".

        If the log is reset, and the destination has been sent
        "start", it will close the destination ("end" optionally
        preceded by "flush").  The destination should be prepared
        for a second "start" event and the resumption of logging.

        If a Log object is created, and literally never logged
        to before it's closed, it won't send *any* events to its
        destinations besides the initial "register".  (If the log
        is never started, then we never need to end it either,
        and there were never any events to send to the destinations.)
        """
        def __init__(self):
            self._owner = None
            self._hash_cache = None

        @property
        def owner(self):
            return self._owner

        def __eq__(self, other):
            raise NotImplementedError()

        def _hash(self):
            raise NotImplementedError()

        @base('destination_hash')
        def __hash__(self):
            if self._hash_cache is None:
                self._hash_cache = h = self._hash()
                return h
            return self._hash_cache

        def register(self, owner):
            if self.owner is not None:
                raise RuntimeError(f"can't register owner {owner}, already registered with {self.owner}")
            self._owner = owner

        def start(self, start_time_ns, start_time_epoch):
            pass

        def write(self, elapsed, thread, formatted):
            raise RuntimeError("pure virtual Destination.write called")

        def log(self, elapsed, thread, format, message, formatted):
            self.write(elapsed, thread, formatted)

        def enter(self, elapsed, thread, message):
            pass

        def exit(self, elapsed, thread):
            pass

        def flush(self):
            pass

        def end(self, elapsed):
            pass

        def unregister(self):
            self._owner = None



    class Callable(Destination):
        """
        A Destination wrapping a callable.

        Calls the callable for every formatted log message.
        """
        def __init__(self, callable):
            super().__init__()
            self._callable = callable

        @property
        def callable(self):
            return self._callable

        def __eq__(self, other):
            return isinstance(other, Log.Callable) and (other._callable is self._callable)

        def _hash(self):
            return hash(Log.Callable) ^ hash(self._callable)
        __hash__ = base.destination_hash

        def write(self, elapsed, thread, formatted):
            self._callable(formatted)




    class Print(Destination):
        """
        A Destination wrapping builtins.print.

        Calls
            builtins.print(formatted, end='', flush=True)
        for every formatted log message.
        """
        def __eq__(self, other):
            return isinstance(other, Log.Print)

        def _hash(self):
            return hash(Log.Print) ^ hash(object)
        __hash__ = base.destination_hash

        def write(self, elapsed, thread, formatted):
            builtins.print(formatted, end='', flush=True)


    class List(Destination):
        """
        A Destination wrapping a Python list.

        Appends every formatted log message to the list.
        """
        def __init__(self, list):
            super().__init__()
            self._list = list

        @property
        def list(self):
            return self._list

        def __eq__(self, other):
            return isinstance(other, Log.List) and (other._list is self._list)

        def _hash(self):
            return hash(Log.List) ^ id(self._list)
        __hash__ = base.destination_hash

        def write(self, elapsed, thread, formatted):
            self._list.append(formatted)



    class Buffer(Destination):
        """
        A Destination that buffers log messages before sending them to another Destination.

        This Destination wraps another arbitrary
        Destination, referred to as the "underlying"
        Destination.

        Every time a formatted log message is logged,
        Buffer appends it to an internal buffer (a Python list).
        When the log is flushed, Buffer will concatentate
        all the log messages into one giant string, then
        writes that string to the underlying Destination,
        and also flushes the underlying Destination.

        By default, Buffer wraps a Print destination,
        but you may supply your own Destination as a
        positional argument to the constructor.
        """
        def __init__(self, destination=None):
            super().__init__()
            self._buffer = []
            self._original_destination = destination
            self._destination = Log.map_destination(destination) if destination is not None else Log.Print()
            self._last_elapsed = self._last_thread = None

        @property
        def buffer(self):
            return self._buffer

        @property
        def destination(self):
            return self._original_destination

        @property
        def last_elapsed(self):
            return self._last_elapsed

        @property
        def last_thread(self):
            return self._last_thread

        def __eq__(self, other):
            return isinstance(other, Log.Buffer) and (other._destination == self._destination)

        def _hash(self):
            return hash(Log.Buffer) ^ hash(self._destination)
        __hash__ = base.destination_hash

        def write(self, elapsed, thread, formatted):
            self._last_elapsed = elapsed
            self._last_thread = thread
            self._buffer.append(formatted)

        def flush(self):
            if self._buffer:
                contents = "".join(self._buffer)
                self._buffer.clear()
                self._destination.write(self._last_elapsed, self._last_thread, contents)
                self._destination.flush()


    class File(Destination):
        """
        A Destination wrapping a file in the filesystem.

        This Destination writes to a file in the filesystem,
        using the path you specify (either a str or a pathlib.Path
        object).

        If flush=False (the default), when a formatted log message
        is written to the destination, it's buffered internally.
        Then, when the log is flushed, File concatenates all the
        buffered messages, opens the file, writes to it with one
        write call, and closes it.

        If flush=True, the file is opened and kept open.  Every
        time it receives a formatted log message, it writes the
        message immediately and flushes the file handle.  If File
        receives an "end" message, it closes the file; if it
        receives a subsequent "start" message, it reopens the file.

        The first time the file is opened, it's opened using the
        "initial_mode" passed in, by default "at".  After the first
        time, File always uses mode "at".
        """
        def __init__(self, path, initial_mode="at", *, buffering=True, encoding=None):
            super().__init__()

            original_path = path

            is_bytes = isinstance(path, bytes)
            is_str = isinstance(path, str)
            is_path = isinstance(path, Path)

            if not (is_bytes or is_str or is_path):
                raise TypeError("path must be str, bytes, or Path, and non-empty")
            if not path:
                raise ValueError("path must be str, bytes, or Path, and non-empty")

            if is_bytes:
                path = os.fsdecode(path)
                is_str = True
            if is_str:
                path = Path(path)

            path = path.resolve()

            if not isinstance(initial_mode, str):
                raise TypeError("initial_mode must be str, and can only be one of these values: 'a', 'at', 'w', 'wt', 'x', or 'xt'")
            if initial_mode not in ("at", "wt", "xt", "a", "w", "x"):
                raise ValueError("initial_mode must be str, and can only be one of these values: 'a', 'at', 'w', 'wt', 'x', or 'xt'")

            self._buffer = buffer = []
            self._buffering = buffering
            self._original_path = original_path
            self._path = path
            self._mode = initial_mode
            self._encoding = encoding
            self._f = None

        @property
        def path(self):
            return self._original_path

        @property
        def mode(self):
            return self._mode

        @property
        def encoding(self):
            return self._encoding

        @property
        def buffering(self):
            return self._buffering

        def __eq__(self, other):
            return isinstance(other, Log.File) and (other._path == self._path)

        def _hash(self):
            return hash(Log.File) ^ hash(self._path)
        __hash__ = base.destination_hash

        def start(self, start_time_ns, start_time_epoch):
            super().start(start_time_ns, start_time_epoch)
            self._f = None if self._buffering else self._path.open(self._mode, encoding=self._encoding)

        def end(self, elapsed):
            super().end(elapsed)
            assert not self._buffer
            if self._f:
                assert not self._buffering
                f = self._f
                self._f = None
                f.close()
                self._mode = "at"

        def write(self, elapsed, thread, formatted):
            if not formatted:
                return
            if self._buffering:
                self._buffer.append(formatted)
                return

            self._f.write(formatted)
            self._f.flush()

        def flush(self):
            if not (self._buffering and self._buffer):
                return

            assert not self._f
            contents = "".join(self._buffer)
            self._buffer.clear()
            with self._path.open(self._mode, encoding=self._encoding) as f:
                f.write(contents)
            self._mode = "at"



    class TmpFile(File):
        """
        A Destination that writes to a timestamped temporary file.

        This is a subclass of File that computes a temporary
        filename.  The filename is approximately in this format:
            tempfile.gettempdir() / "{Log.name}.{start timestamp}.{os.getpid()}.txt"
        (If the computed filename contains illegal or inconvenient characters,
        they may be replaced with other characters; for example ':' is replaced with '-'.)

        The filename is recomputed whenever TmpFile receives a "start" event.
        Thus, if a Log is reset, TmpFile will close the old temporary log;
        if that Log is subsequently logged to, TmpFile will open a new temporary
        log with a freshly recalculated name.
        """

        def __init__(self, prefix='{name}', *, buffering=True, encoding=None):
            # use a fake path for now,
            # we'll compute a proper one when we get the "start" event
            path = Path(tempfile.gettempdir()) / f"Log-init.{os.getpid()}.tmp"
            super().__init__(path, buffering=buffering, encoding=encoding)
            if not (isinstance(prefix, str) and prefix):
                raise TypeError("prefix must be str, and cannot be empty")
            self._prefix = prefix
            self._rendered_prefix = None

        @property
        def prefix(self):
            return self._prefix

        @property
        def path(self):
            return self._path

        def __eq__(self, other):
            return isinstance(other, Log.TmpFile) and (other._prefix == self._prefix)

        def _hash(self):
            return hash(Log.TmpFile) ^ hash(self._prefix)
        __hash__ = base.destination_hash

        def register(self, owner):
            super().register(owner)
            self._rendered_prefix = self._prefix.format(name=owner._name)

        def start(self, start_time_ns, start_time_epoch):
            assert self._owner
            log_timestamp = self._owner._timestamp_format(start_time_epoch)
            log_timestamp = log_timestamp.replace("/", "-").replace(":", "-").replace(" ", ".")
            thread = current_thread()
            tmpfile = f"{self._rendered_prefix}.{log_timestamp}.{os.getpid()}.{thread.name}.txt"
            tmpfile = big_file.translate_filename_to_exfat(tmpfile)
            tmpfile = tmpfile.replace(" ", '_')
            self._path = Path(tempfile.gettempdir()) / tmpfile
            super().start(start_time_ns, start_time_epoch)


    class FileHandle(Destination):
        """
        A Destination wrapping an open Python file handle.

        This Destination writes to an already-open file handle.
        It will never close the file handle; it will only ever
        write to it, and flush it.

        Every time a formatted log message is received,
        FileHandle writes it immediately to the file handle.
        If autoflush=True, FileHandle will immediately flush the
        file handle after writing; by default autoflush is False.
        """
        def __init__(self, handle, *, autoflush=False):
            super().__init__()
            if not isinstance(handle, TextIOBase):
                raise TypeError(f"invalid file handle {handle}")
            self._handle = handle
            self._autoflush = autoflush

        @property
        def handle(self):
            return self._handle

        @property
        def autoflush(self):
            return self._autoflush

        def __eq__(self, other):
            return isinstance(other, Log.FileHandle) and (other._handle is self._handle)

        def _hash(self):
            return hash(Log.FileHandle) ^ hash(self._handle)
        __hash__ = base.destination_hash

        def write(self, elapsed, thread, formatted):
            self._handle.write(formatted)
            if self._autoflush:
                self._handle.flush()

        def flush(self):
            self._handle.flush()


    class Sink(Destination):
        """
        A Destination retaining all log messages, in order, using SinkEvents.

        Every time Sink receives a formatted log message,
        it appends a SinkEvent object to an internal list of events.
        See SinkEvent and its subclasses for more.

        You may iterate over a Sink, which yields all events
        logged so far.

        Sink.print() formats the events and prints them using
        builtins.print.
        """

        def __init__(self):
            super().__init__()
            self._session = 0
            self._events = []
            self._longest_message = 0
            self._depth = 0

        def __eq__(self, other):
            return other is self

        def _hash(self):
            return hash(Log.Sink) ^ id(self)
        __hash__ = base.destination_hash

        def _event(self, event):
            if hasattr(event, 'message') and (event.message is not None):
                self._longest_message = max(self._longest_message, len(event.message))

            if self._events:
                previous = self._events[-1]
                if not isinstance(previous, SinkEndEvent):
                    assert event.elapsed >= previous.elapsed, \
                        f"duration should be >= 0 but it's {event.elapsed - previous.elapsed} ({previous})"
                    self._events[-1] = previous._calculate_duration(event)

            self._events.append(event)

        def start(self, start_time_ns, start_time_epoch):
            self._session += 1

            configuration = {
                "name" : self._owner._name,
                "threading" : self._owner._threading,
                "indent" : self._owner._indent,
                "width" : self._owner._width,
                "clock" : self._owner._clock,
                "timestamp_clock" : self._owner._timestamp_clock,
                "timestamp_format" : self._owner._timestamp_format,
                "prefix" : self._owner._prefix,
                "formats" : dict(self._owner._formats),
            }
            self._event(SinkStartEvent(self._session, start_time_ns, start_time_epoch, configuration))


        def end(self, elapsed):
            self._event(SinkEndEvent(self._session, elapsed))
            self._depth = 0

        def write(self, elapsed, thread, formatted):
            self._event(SinkWriteEvent(self._session, self._depth, elapsed, thread, formatted))

        def log(self, elapsed, thread, format, message, formatted):
            self._event(SinkLogEvent(self._session, self._depth, elapsed, thread, format, message, formatted))

        def enter(self, elapsed, thread, message):
            self._event(SinkEnterEvent(self._session, self._depth, elapsed, thread, message))
            self._depth += 1

        def exit(self, elapsed, thread):
            self._depth -= 1
            self._event(SinkExitEvent(self._session, self._depth, elapsed, thread))

        def __iter__(self):
            for e in self._events:
                yield e

        def print(self, *,
                enter='',
                exit='',
                indent=2,
                prefix='[{elapsed:>014.10f} {thread.name:>12} {duration:>014.10f} {format:>8} {type:>5}] {indent}',
                print=None,
                timestamp=big_time.timestamp_human,
                width=None,
                ):
            if not self._events:
                return

            # start_time_epoch will always have a valid value
            assert isinstance(self._events[0], SinkStartEvent)

            if not print:
                print = builtins.print

            if width is None:
                width = self._longest_message

            start_time_epoch = None

            for e in self._events:
                if isinstance(e, SinkStartEvent):
                    start_time_epoch = e.epoch

                elapsed = e.elapsed / 1_000_000_000.0
                duration = getattr(e, 'duration', 0) / 1_000_000_000.0
                epoch = elapsed + start_time_epoch
                ts = timestamp(epoch)
                indent_str = ' ' * (e.depth * indent)
                thread = getattr(e, 'thread', _empty_thread)

                fields = {
                    'elapsed': elapsed,
                    'duration': duration,
                    'format': getattr(e, 'format', ''),
                    'timestamp': ts,
                    'thread': thread,
                    'type': e.type,
                    'depth': e.depth,
                    'indent': indent_str,
                }
                prefix_str = prefix.format_map(fields)
                space_str = " " * len(prefix_str)
                message = getattr(e, 'message', '')
                for line in message.split('\n'):
                    print(prefix_str + line)
                    prefix_str = space_str

TMPFILE = Log.TmpFile()
export("TMPFILE")


@export
class OldDestination(Log.Destination):
    """
    A Destination providing backwards compatibility with the old big.log.Log interface.
    Accumulates events for later iteration or printing.
    """

    def __init__(self):
        super().__init__()
        self.longest_event = 0
        self.reset()

    def __eq__(self, other):
        return other is self

    def _hash(self):
        return hash(OldDestination) ^ id(self)
    __hash__ = base.destination_hash

    def reset(self):
        self.stack = []
        self.events = []
        self.previous_event = None

    def _event(self, elapsed, event):
        if self.previous_event:
            previous_event = self.previous_event
            previous_event[1] = elapsed - previous_event[0]
        e = self.previous_event = [elapsed, 0, event, len(self.stack)]
        self.events.append(e)

        self.longest_event = max(self.longest_event, len(event))

    def start(self, start_time_ns, start_time_epoch):
        self.reset()
        self._event(0, "log start")

    def write(self, elapsed, thread, formatted):
        self._event(elapsed, formatted.rstrip('\n'))

    def log(self, elapsed, thread, format, message, formatted):
        if format not in ('start', 'end', 'enter', 'exit'):
            self._event(elapsed, formatted.rstrip('\n'))

    def enter(self, elapsed, thread, message):
        self._event(elapsed, message + " start")
        self.stack.append(message)

    def exit(self, elapsed, thread):
        subsystem = self.stack.pop()
        self._event(elapsed, subsystem + " end")

    def __iter__(self):
        return iter(self.events)

    def print(self, *, print=None, title="[event log]", headings=True, indent=2, seconds_width=2, fractional_width=9):
        if not print:
            print = builtins.print

        indent_str = " " * indent
        column_width = seconds_width + 1 + fractional_width

        def format_time(t):
            seconds = t // 1_000_000_000
            nanoseconds = f"{t % 1_000_000_000:>09}"[:fractional_width]
            return f"{seconds:0{seconds_width}}.{nanoseconds}"

        if title:
            print(title)

        if headings:
            print(f"{indent_str}{'start':{column_width}}  {'elapsed':{column_width}}  event")
            column_dashes = '-' * column_width
            print(f"{indent_str}{column_dashes}  {column_dashes}  {'-' * self.longest_event}".rstrip())

        for start, elapsed, event, depth in self:
            print(f"{indent_str}{format_time(start)}  {format_time(elapsed)}  {event}".rstrip())


@export
class OldLog:
    """
    A drop-in replacement for the old big.log.Log class.

    This creates a Log, populates it with an OldDestination
    and exposes the old big.log.Log interface.  Provided
    for backwards compatibility, as a stepping-stone for
    users of the old Log, to make it easier to transition
    to the new Log.
    """

    def __init__(self, clock=None):
        self._destination = OldDestination()
        clock=clock or default_clock
        self._log = Log(self._destination, threading=False, formats={"start": {"template": "log start"}, "end": None}, prefix='', clock=clock, indent=2)

    def reset(self):
        self._log.reset()

    def __call__(self, event):
        self._log(event)

    def enter(self, subsystem):
        self._log.enter(subsystem)

    def exit(self):
        self._log.exit()

    def __iter__(self):
        return iter(self._destination)

    def print(self, *, print=None, title="[event log]", headings=True, indent=2, seconds_width=2, fractional_width=9):
        self._destination.print(print=print, title=title, headings=headings, indent=indent, seconds_width=seconds_width, fractional_width=fractional_width)


mm()
