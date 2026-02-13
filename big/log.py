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
from functools import partial
from io import TextIOBase
import os
from pathlib import Path
from queue import Queue
import tempfile
from threading import current_thread, Lock, Thread
from .boundinnerclass import BoundInnerClass
from . import time as big_time
from . import file as big_file
import time


from . import builtin
mm = builtin.ModuleManager()
export = mm.export


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
class SinkEvent:
    """
    Base class for Log events stored by the Sink destination.
    """
    __slots__ = (
        '_depth',
        '_duration',
        '_elapsed',
        '_epoch',
        '_format',
        '_formatted',
        '_message',
        '_ns',
        '_number',
        '_thread',
        '_type',
        )

    _DEFAULT_DEPTH = 0
    _DEFAULT_DURATION = 0
    _DEFAULT_ELAPSED = 0
    _DEFAULT_EPOCH = None
    _DEFAULT_FORMAT = None
    _DEFAULT_FORMATTED = None
    _DEFAULT_MESSAGE = None
    _DEFAULT_NS = None
    _DEFAULT_NUMBER = 0
    _DEFAULT_THREAD = None
    _DEFAULT_TYPE = None

    TYPE_RESET = "reset"
    TYPE_START = 'start'
    TYPE_END   = 'end'
    TYPE_FLUSH = "flush"
    TYPE_CLOSE = "close"
    TYPE_WRITE = 'write'
    TYPE_LOG   = 'log'
    TYPE_ENTER = 'enter'
    TYPE_EXIT  = 'exit'

    def __init__(self, *,
        depth=_DEFAULT_DEPTH,
        duration=_DEFAULT_DURATION,
        elapsed=_DEFAULT_ELAPSED,
        epoch=_DEFAULT_EPOCH,
        format=_DEFAULT_FORMAT,
        formatted=_DEFAULT_FORMATTED,
        message=_DEFAULT_MESSAGE,
        ns=_DEFAULT_NS,
        number=_DEFAULT_NUMBER,
        thread=_DEFAULT_THREAD,
        type=_DEFAULT_TYPE,
        ):
        self._depth = depth
        self._duration = duration
        self._elapsed = elapsed
        self._epoch = epoch
        self._format = format
        self._formatted = formatted
        self._message = message
        self._ns = ns
        self._number = number
        self._thread = thread
        self._type = type

    @property
    def depth(self):
        return self._depth

    @property
    def duration(self):
        return self._duration

    @property
    def elapsed(self):
        return self._elapsed

    @property
    def epoch(self):
        return self._epoch

    @property
    def format(self):
        return self._format

    @property
    def formatted(self):
        return self._formatted

    @property
    def message(self):
        return self._message

    @property
    def ns(self):
        return self._ns

    @property
    def number(self):
        return self._number

    @property
    def thread(self):
        return self._thread

    @property
    def type(self):
        return self._type


    def __repr__(self):
        buffer = []
        append = buffer.append
        for name in (
            "depth",
            "duration",
            "elapsed",
            "epoch",
            "format",
            "formatted",
            "message",
            "ns",
            "number",
            "thread",
            ):
            value = getattr(self, name)
            default = getattr(self, "_DEFAULT_" + name.upper())
            if value != default:
                append(f"{name}={value!r}")

        text = ", ".join(buffer)
        return f"{self.__class__.__name__}({text})"

    def __eq__(self, other):
        return (isinstance(other, SinkEvent)
            and (self._number == other._number)
            and (self._elapsed == other._elapsed)
            and (self._type == other._type)
            and (self._message == other._message)
            and (self._thread == other._thread)
            and (self._epoch == other._epoch)
            and (self._depth == other._depth)
            )

    def __lt__(self, other):
        if not isinstance(other, SinkEvent):
            raise TypeError(f"'<' not supported between instances of SinkEvent and {type(other)}")
        return (
                (self._number  <= other._number)
            and (self._elapsed <  other._elapsed)
            )


@export
class SinkStartEvent(SinkEvent):
    def __init__(self, number, start_time_ns, start_time_epoch, formatted):
        super().__init__(
            type=self.TYPE_START,
            number=number,
            ns=start_time_ns,
            epoch=start_time_epoch,
            formatted=formatted,
            )

@export
class SinkEndEvent(SinkEvent):
    def __init__(self, number, elapsed, formatted):
        super().__init__(
            type=self.TYPE_END,
            number=number,
            elapsed=elapsed,
            formatted=formatted,
            )

@export
class SinkWriteEvent(SinkEvent):
    def __init__(self, number, depth, elapsed, thread, formatted):
        super().__init__(
            type=self.TYPE_WRITE,
            number=number,
            elapsed=elapsed,
            thread=thread,
            formatted=formatted,
            depth=depth,
            )

@export
class SinkLogEvent(SinkEvent):
    def __init__(self, number, depth, elapsed, thread, format, message, formatted):
        super().__init__(
            type=self.TYPE_LOG,
            number=number,
            elapsed=elapsed,
            thread=thread,
            format=format,
            message=message,
            formatted=formatted,
            depth=depth,
            )

@export
class SinkEnterEvent(SinkEvent):
    def __init__(self, number, depth, elapsed, thread, message, formatted):
        super().__init__(
            type=self.TYPE_ENTER,
            format='enter',
            number=number,
            elapsed=elapsed,
            thread=thread,
            message=message,
            formatted=formatted,
            depth=depth,
            )

@export
class SinkExitEvent(SinkEvent):
    def __init__(self, number, depth, elapsed, thread, message, formatted):
        super().__init__(
            type=self.TYPE_EXIT,
            format='exit',
            number=number,
            elapsed=elapsed,
            thread=thread,
            message=message,
            formatted=formatted,
            depth=depth,
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


@export
class Log:
    """
    A lightweight text-based log suitable for debugging.

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
        str or pathlib.Path object
            Log messages are buffered locally,
            and dumped to the file named by the string.
            Equivalent to big.log.Log.File(pathlib.Path(destination)).
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
    when indenting the log (using Log.start).  Default is 4.

    "width" should be an integer, default is 79.  This is only used
    to format separator lines (see "separator" and "banner_separator").

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

    "formats" should be a dict mapping strings (for which s.isidentifier()
    is True) to format dicts.  A "format dict" is itself a dict with two
    supported values: "format", and optionally "line", both strings.
    "format" specifies a string that will be used to format log messages;
    if you call Log.print(foo, format="peanut"), this will use the format
    dict specified by Log(format={"peanut": {...}}).

    The "format" string in the format dict is processed using the ".format"
    method on a string, with the following values defined:

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
    format; this is how log.box() is implemented.

    To suppress the initial and/or final log messages, pass in a dict
    to the format parameter with "start" or "end" respectively set to
    None.  To suppress both:
        Log(format={"start": None, "end": None})
    """

    def __init__(self, *destinations,
            name='Log',
            threading=True,

            indent=4,
            width=79,

            clock=default_clock,
            timestamp_clock=time.time,
            timestamp_format=big_time.timestamp_human,

            prefix=prefix_format(3, 10, 12),
            formats = {},
            ):

        t1 = clock()
        start_time_epoch = timestamp_clock()
        t2 = clock()
        start_time_ns = (t1 + t2) // 2

        self._name = name
        self._threading = threading

        self._clock = clock
        self._timestamp_clock = timestamp_clock

        self._indent = indent
        self._width = width

        self._prefix = prefix
        self._spaces = ''
        self._timestamp_format = timestamp_format

        self._reset(start_time_ns, start_time_epoch)

        self._nesting = []

        self._state = 'initial'

        # if threading is True, _lock is only used for close and reset (and shutdown)
        self._lock = Lock()
        self._blocker = blocker = Lock()
        blocker.acquire()


        base_formats = {
            "box" : {
                "format": '{prefix}+{line}\n{prefix}| {message}\n{prefix}+{line}',
                "line": '-',
            },
            "end" : {
                "format": '{line}\n{name} finish at {timestamp}\n{line}',
                "line": '=',
            },
            "enter": {
                "format": '{prefix}+-----+{line}\n{prefix}|start| {message}\n{prefix}+-----+{line}',
                "line": '-',
            },
            "exit": {
                "format": '{prefix}+-----+{line}\n{prefix}| end | {message}\n{prefix}+-----+{line}',
                "line": '-',
            },
            "print": {
                "format": '{prefix}{message}',
                "line": '',
            },
            "start": {
                "format": '{line}\n{name} start at {timestamp}\n{line}',
                "line": '=',
            },
        }

        for key, value in formats.items():
            if value is None:
                if key not in ("start", "end"):
                    raise ValueError("None is only a valid value for keys 'start' and 'end'")
                base_formats.pop(key, None)
            else:
                if not isinstance(value, dict):
                    raise TypeError(f"format values must be dict or None, not {type(value)}")
                d = base_formats.setdefault(key, {})
                d.update(value)

        self._formats = {}

        for key, value in base_formats.items():
            if not isinstance(key, str):
                raise TypeError(f"format keys must be str, not {type(key)}")
            if not key.isidentifier():
                raise ValueError(f"format key strings must be valid Python identifiers, not {key!r}")
            assert isinstance(value, dict)
            if not (isinstance(value.get('format', None), str) and isinstance(value.get('line', None), str)):
                raise ValueError(f"format dicts must contain 'format' and 'line' keys with value str, not {value!r}")

            attribute_exists = hasattr(self, key)
            predefined_key = key in ("enter", "exit", "start", "end", "print")
            if (not predefined_key) and attribute_exists:
                raise ValueError(f'format {key} attribute is already in use')

            format = value['format']
            line = value['line']
            if line:
                repeated_line = line * ((width // len(line)) + 1)
            else:
                repeated_line = ''

            format_lines = []
            for format_line in format.split('\n'):
                s = format_line.replace("{{", "")
                contains_message = "{message}" in s
                append_repeated_line = s.endswith("{line}")
                if append_repeated_line:
                    assert line
                    format_line = format_line[:-6]
                    append_repeated_line = repeated_line
                format_lines.append((format_line, line, contains_message, append_repeated_line))
            self._formats[key] = format_lines

            if not attribute_exists:
                def make_method(key):
                    def method(message):
                        time = self._clock()
                        thread = current_thread()

                        if not isinstance(message, str):
                            raise TypeError('message must be str')

                        self._dispatch([(self._log, (time, thread, key, message))])
                    method.__doc__ = f"Writes a message to the log using the {key!r} format."
                    return method
                setattr(self, key, make_method(key))

        print = builtins.print
        if not destinations:
            destinations = [print]

        self._destinations = []
        append = self._destinations.append

        for destination in destinations:
            destination = Log.map_destination(destination)

            if destination is not None:
                append(destination)
                destination.register(self)

        self._manage_thread()


    @classmethod
    def base_destination_mapper(cls, o):
        "Implements the default mapping of objects to Destination objects."

        if o is None:
            return None
        if isinstance(o, cls.Destination):
            return o
        if o is print:
            return cls.Print()
        if isinstance(o, str):
            return cls.File(Path(o))
        if isinstance(o, Path):
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


    @property
    def clock(self):
        return self._clock

    @property
    def destinations(self):
        for d in self._destinations:
            yield d

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
        return self._dirty

    @property
    def closed(self):
        with self._lock:
            return self._state == 'closed'

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

    def _elapsed(self, t):
        # t should be a value returned by _clock.
        # returns t converted to elapsed time
        # since self.start_time_ns, as integer nanoseconds.
        return t - self._start_time_ns

    def _ns_to_float(self, ns):
        return ns / 1_000_000_000.0


    def _format_s(self, elapsed, thread, format, *, message=None, line=None, prefix=None):
        if not format:
            return ''

        elapsed = self._ns_to_float(elapsed)
        epoch = elapsed + self._start_time_epoch
        timestamp = self._timestamp_format(epoch)

        substitutions = {
            "elapsed": elapsed,
            "name": self._name,
            "thread": thread,
            "time": epoch,
            "timestamp": timestamp,
            }
        if message is not None:
            substitutions['message'] = message
        if line is not None:
            substitutions['line'] = line
        if prefix is not None:
            substitutions['prefix'] = prefix

        return format.format_map(substitutions)

    def _format_message(self, time, thread, format, message):
        elapsed = self._elapsed(time)
        if thread:
            prefix = self._format_s(elapsed, thread, self._prefix) + self._spaces
        else:
            prefix = ''

        if message:
            message_lines = message.split('\n')
        else:
            message_lines = ('',)

        buffer = []
        append = buffer.append
        line_buffer = []
        line_append = line_buffer.append
        for t in self._formats[format]:
            line_buffer.clear()
            f, l, contains_message, append_repeated_line = t
            if contains_message:
                iterable = message_lines
            else:
                iterable = [None]
            for ml in iterable:
                formatted = self._format_s(elapsed, thread, f, message=ml, line=l, prefix=prefix)
                line_append(formatted)
                if append_repeated_line:
                    length = len(formatted)
                    delta = self._width - length
                    if delta > 0:
                        line_append(append_repeated_line[:delta])
                line = "".join(line_buffer).rstrip()
                append(line)
                append("\n")
        return "".join(buffer)

    def _cache_spaces(self):
        self._spaces = _spaces[:len(self._nesting) * self._indent]

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
        atexit.register(self._atexit)

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
        self.close()
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
        once, we guarantee that no job from aother thread gets
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



    def _ensure_state(self, state, ns=None, epoch=None):
        """
        Attempt to ensure we're in state "state".

        If we're not in state "state", attempt to transition to it.
        Returns True if we're in state "state" when _ensure_state
        returns, False otherwise.

        Only three states are supported; they exist in a loop:
              +-------+
              |       |
              v       |
            initial   |
              |       |
              v       |
            logging   |
              |       |
              v       |
            closed    |
              |       |
              +-------+

        You can always transition from any state to any other
        state, with one exception: you can't transition directly
        from "closed" to "logging".  (The only way to escape
        "closed" state is to reset the log, which transitions
        to "initial".)

        This means you can in some circumstances make two state
        transitions at once:
             from "initial" to "closed", and
             from "logging" to "initial".
        When you do, you pass through the intermediary state.
        (e.g. if you transition from "initial" to "closed",
        you'll enter and exit "logging" state on the way.)

        If you're in "initial" and transition to "logging",
        you open the log, which sends a "start" event.

        If you're in "logging" and transition to "closed",
        you close the log, which sends "end", "flush", and
        "close" events.

        If you're in "closed" and transition to "initial",
        you'll reset the log, which sends a "reset" event.

        If ns and epoch are specified, those are used as
        the ns and epoch times for any events that send times.
        If you transition from "initial" to "logging", the
        start event will use ns and epoch as the start time
        of the log.  If you transition from "logging" to "closed",
        the end event will use ns as the end time of the log.

        It's an error to transition from another state
        to "closed" or "initial" without specifying
        ns and epoch.
        """
        while True:
            if state == self._state:
                return True

            if self._state == 'initial':
                # transition to "logging":

                # send start event.
                if self._formats.get('start') is not None:
                    formatted = self._format_message(self._start_time_ns, None, 'start', None)
                    dirty = self._dirty or bool(formatted)
                else:
                    formatted = ''
                    dirty = self._dirty

                for destination in self._destinations:
                    destination.start(self._start_time_ns, self._start_time_epoch, formatted)

                self._dirty = dirty

                self._state = 'logging'
                continue

            if self._state == 'logging':
                # transition to "closed"

                assert ns is not None
                assert epoch is not None

                self._clear_nesting()

                self._end_time_ns = ns
                self._end_time_epoch = epoch

                # send end event.
                elapsed = self._elapsed(self._end_time_ns)
                if self._formats.get('end') is not None:
                    formatted = self._format_message(self._end_time_ns, None, 'end', None)
                    dirty = self._dirty or bool(formatted)
                else:
                    formatted = ''
                    dirty = self._dirty

                for destination in self._destinations:
                    destination.end(elapsed, formatted)

                self._dirty = dirty

                # send flush.
                self._flush()

                # send close.
                self._close()

                self._state = 'closed'
                continue

            if self._state == 'closed':
                if state != 'initial':
                    return False

                assert ns is not None
                assert epoch is not None

                self._reset(ns, epoch)

                # send reset event.
                for destination in self._destinations:
                    destination.reset()

                self._state = 'initial'
                continue

    def _reset(self, start_time_ns, start_time_epoch):
        self._start_time_ns = start_time_ns
        self._start_time_epoch = start_time_epoch
        self._end_time_ns = None
        self._end_time_epoch = None
        self._dirty = False

    def reset(self):
        """
        Resets the log to 'initial' state.

        If the log is currently in "initial" state,
        this is a no-op.

        If the log is currently in "closed" state,
        resets it.

        If the log is currently in "logging" state,
        closes it, then resets it.
        """
        clock = self._clock
        ns1 = clock()
        epoch = self._timestamp_clock()
        ns2 = clock()
        ns = (ns1 + ns2) // 2

        self._dispatch( [(self._ensure_state, ('initial', ns, epoch)),] )

    def _flush(self, blocker=None):
        if not self._ensure_state('logging'):
            return
        if self._dirty:
            for destination in self._destinations:
                destination.flush()
            self._dirty = False

    def flush(self, block=True):
        """
        Flushes the log, if it's open and dirty.

        If the log is in "logging" state, and it's
        "dirty" (any formatted text has been logged
        to the log since either the log was started
        or since the last flush), flushes the log.

        If block=True (the default), flush won't
        return until the log is flushed.  If block=False,
        the log may be flushed asynchronously.
        """
        try:
            if not block:
                notify = None
            else:
                blocker = Lock()
                blocker.acquire()
                notify = blocker.release

            self._dispatch([(self._flush, ())], notify=notify)

        finally:
            if notify:
                blocker.acquire()

    def _close(self):
        for destination in self._destinations:
            destination.close()

    def close(self, block=True):
        """
        Closes the log, if it's logging.

        This ensures the log is in "closed" state.
        When the log is in "closed" state, it ignores
        all writes to the log; if you want to write
        to the log after it has been closed, you must
        call the reset() method to reset the log.

        If the log is currently in "closed" state,
        this is a no-op.

        If the log is currently in "logging" state,
        closes the log.

        If the log is currently in "initial" state,
        opens then closes the log.

        If block=True (the default), close won't
        return until the log is closed.  If block=False,
        the log may be closed asynchronously.
        """
        try:
            ns1 = self._clock()
            epoch = self._timestamp_clock()
            ns2 = self._clock()
            ns = (ns1 + ns2) / 2

            if not block:
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
        if not self._ensure_state('logging'):
            return

        elapsed = self._elapsed(time)

        for destination in self._destinations:
            destination.write(elapsed, thread, formatted)

        self._dirty = True

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

        if formatted:
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

        if not self._ensure_state('logging'):
            return

        elapsed = self._elapsed(time)
        formatted = self._format_message(time, thread, format, message)

        formatted_true = bool(formatted)
        if message or formatted_true:
            for destination in self._destinations:
                destination.log(elapsed, thread, format, message, formatted)
        self._dirty = self._dirty or formatted_true


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
        if format and (format not in self._formats):
            raise ValueError(f"undefined format {format!r}")

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

    class LogEnterAndExitContextManager:
        """
        The context manage returned by Log.enter().  Calls Log.exit() on exit.
        """
        def __init__(self, log):
            self.exit = log.exit

        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_value, traceback):
            self.exit()


    def _enter_exit(self, verb, time, thread, message):
        if not self._ensure_state('logging'):
            return

        elapsed = self._elapsed(time)
        formatted = self._format_message(time, thread, verb, message)

        for destination in self._destinations:
            getattr(destination, verb)(elapsed, thread, message, formatted)
        self._dirty = self._dirty or bool(formatted)

    def enter(self, message):
        """
        Logs a message, then indents the log.
        """
        time = self._clock()
        thread = current_thread()

        self._dispatch([
            (self._enter_exit, ('enter', time, thread, message)),
            (self._append_nesting, (message,)),
            ])
        return self.LogEnterAndExitContextManager(self)

    def _exit(self, time, thread):
        if not self._nesting:
            return

        message = self._pop_nesting()
        self._enter_exit('exit', time, thread, message)

    def exit(self):
        """
        Outdents the log from the most recent Log.enter() indent.
        """
        time = self._clock()
        thread = current_thread()

        self._dispatch([(self._exit, (time, thread))])



    class Destination:
        """
        Base class for objects that do the actual logging for a big.Log.

        A Destination object is "owned" by a Log, and the Log sends it
        "events" by calling named methods.  All Destination objects *must*
        support the "write" event, by implementing a write method:

            write(elapsed, thread, formatted)

        In addition, Destination subclasses may optionally override
        the following events / methods:

            flush()
            close()
            reset()
            start(start_time_ns, start_time_epoch, formatted)
            end(elapsed, formatted)
            write(elapsed, thread, message, format, formatted)
            enter(elapsed, thread, message, formatted)
            exit(elapsed, thread, message, formatted)

        For all these methods, Destination subclasses need not
        call the base class method.  Note that the default
        implementation for the last five--the methods that take
        a "formatted" parameter--all call self.write, like so:

            self.write(elapsed, thread, formatted)

        If you don't want this behavior, override the method and
        don't call the base class method (via super).

        Finally, Destination subclasses may also override this method:
            register(owner)
        For this method, Destination subclasses are *required*
        to call the base class implementation
        ("super().register(owner)").

        The meaning of each argument to the above Destination methods:

        * elapsed is the elapsed time since the log was
          started/reset, in nanoseconds.
        * thread is the threading.Thread handle for the thread
          that logged the message.
        * formatted is the formatted log message.
        * format is the name of the "format" applied to "message"
          to produce "formatted".
        * message is the original message passed in to a Log method.
        * owner is the Log object that owns this Destination.
          (A Destination can't be shared between multiple Log objects.)

        Log guarantees that the following events will be called in this
        order:

            register
              |
              v
            start
              |
              +----------------------------------+
              |                                  |
              v                                  |
            write | log | enter | exit | flush   |
              |                                  |
              |                                  |
              +----------------------------------+
              |
              v
            end
              |
              v
            [flush]
              |
              v
            close

        The "register" event is sent while the log is still in
        its "initial" state; all other events are sent while the
        log is in "logging" state.  (The log transitions to
        "closed" state only *after* sending the "close" event.)
        "register" will only ever be sent once, and it is always
        the first event received by a Destination.

        The log transitions from "initial" to "logging" only
        after it's logged to for the first time.  It transitions
        to its "logging" state, sends a "start" event, then
        sends the actual logged message.  Once the log has been
        started in this way, it can send any number of "write",
        "log", "enter", "exit", or "flush" events, in any order.

        "flush" is only sent if the log is "dirty".  If the log
        is dirty after an "end" event, it will *always* be flushed
        before the "close" event.

        If the log is closed, the Log will always send "end",
        followed by an optional "flush" (only if dirty),
        followed by "close".

        If the log is reset, if the log is not in "initial" state,
        it will close the log (sending end / [flush] / close),
        then send a "reset" event, at which time the log will be
        back in "initial" state.
        """
        def __init__(self):
            self.owner = None

        def register(self, owner):
            if self.owner is not None:
                raise RuntimeError(f"can't register owner {owner}, already registered with {self.owner}")
            self.owner = owner

        def reset(self):
            pass

        def flush(self):
            pass

        def close(self):
            pass

        def start(self, start_time_ns, start_time_epoch, formatted):
            self.write(0, None, formatted)

        def end(self, elapsed, formatted):
            self.write(elapsed, None, formatted)

        def write(self, elapsed, thread, formatted):
            raise RuntimeError("pure virtual Destination.write called")

        def log(self, elapsed, thread, format, message, formatted):
            self.write(elapsed, thread, formatted)

        def enter(self, elapsed, thread, message, formatted):
            self.write(elapsed, thread, formatted)

        def exit(self, elapsed, thread, message, formatted):
            self.write(elapsed, thread, formatted)



    class Callable(Destination):
        """
        A Destination wrapping a callable.

        Calls the callable for every formatted log message.
        """
        def __init__(self, callable):
            super().__init__()
            self.callable = callable

        def write(self, elapsed, thread, formatted):
            self.callable(formatted)



    class Print(Destination):
        """
        A Destination wrapping a callable.

        Calls
            builtins.print(formatted, end='', flush=True)
        for every formatted log message.
        """
        "A Destination wrapping builtins.print."
        def __init__(self):
            super().__init__()
            self.print = builtins.print

        def write(self, elapsed, thread, formatted):
            self.print(formatted, end='', flush=True)



    class List(Destination):
        """
        A Destination wrapping a Python list.

        Appends every formatted log message to the list.
        """
        def __init__(self, list):
            super().__init__()
            self.array = list

        def write(self, elapsed, thread, formatted):
            self.array.append(formatted)

        def start(self, start_time_ns, start_time_epoch, formatted):
            if formatted:
                self.write(start_time_ns, None, formatted)

        def end(self, elapsed, formatted):
            if formatted:
                self.write(elapsed, None, formatted)



    class Buffer(Destination):
        """
        A Destination that buffers log messages before sending them to another Destination.

        This Destination wraps another arbitrary
        Destination, referred to as the "underlying"
        Destination.

        Every time a formatted log message is logged,
        it's stored in an internal buffer (a Python list).
        When the log is flushed, Buffer will concatentate
        all the log messages into one giant string, then
        writes that string to the underlying Destination,
        and also flushes the underlying Destination.

        By default, Buffer wraps a Print destination,
        but you may supply your own Destination as a
        positional argument to the constructor.
        """
        ""
        def __init__(self, destination=None):
            super().__init__()
            self.array = []
            self.destination = Log.map_destination(destination) if destination is not None else Log.Print()
            self.last_elapsed = self.last_thread = None

        def write(self, elapsed, thread, formatted):
            self.last_elapsed = elapsed
            self.last_thread = thread
            self.array.append(formatted)

        def flush(self):
            if self.array:
                contents = "".join(self.array)
                self.array.clear()
                self.destination.write(self.last_elapsed, self.last_thread, contents)
                self.destination.flush()


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
        receives a "close" message, it closes the file; if it
        receives a "reset" message, it reopens the file.

        The first time the file is opened, it's opened using the
        "initial_mode" passed in, by default "at".  After the first
        time, File always uses mode "at".
        """
        def __init__(self, path, initial_mode="at", *, flush=False):
            super().__init__()

            assert initial_mode in ("at", "wt", "xt", "a", "w", "x")

            self.array = array = []
            self.path = Path(path)
            self.mode = initial_mode
            self._flush = flush
            self.f = None

        def register(self, owner):
            super().register(owner)
            self.reset()

        def reset(self):
            super().reset()
            self.f = self.path.open(self.mode) if self._flush else None

        def write(self, elapsed, thread, formatted):
            if self._flush:
                self.f.write(formatted)
                self.f.flush()
            elif formatted:
                self.array.append(formatted)

        def flush(self):
            if self.array:
                assert not self._flush
                assert not self.f
                contents = "".join(self.array)
                self.array.clear()
                with self.path.open(self.mode) as f:
                    f.write(contents)
                self.mode = "at"

        def close(self):
            assert not self.array
            if self.f:
                f = self.f
                self.f = None
                f.close()
                self.mode = "at"



    class TmpFile(File):
        """
        A Destination that writes to a timestamped temporary file.

        This is a subclass of File that computes a temporary
        filename.  The filename is approximately in this format:
            tempfile.gettempdir() / "{Log.name}.{start timestamp}.{os.getpid()}.txt"
        (If the computed filename contains illegal or inconvenient characters,
        they may be replaced with other characters; for example ':' is replaced with '-'.)

        The filename is recomputed whenever TmpFile receives a "register"
        or "reset" event.  Thus, if the Log is reset, TmpFile will close
        the old temporary log, and open a new one.
        """

        def __init__(self, *, flush=False):
            # use a fake path for now,
            # we'll compute a proper one when they call reset()
            path = Path(tempfile.gettempdir()) / f"{os.getpid()}.tmp"
            super().__init__(path, flush=flush)

        def reset(self):
            # File() calls self.reset for register() or reset(),
            # so this is the right place to dynamically (re-)compute
            # the path to the temporary file.
            assert self.owner
            log_timestamp = self.owner.timestamp_format(self.owner.start_time_epoch)
            log_timestamp = log_timestamp.replace("/", "-").replace(":", "-").replace(" ", ".")
            tmpfile = f"{self.owner.name}.{log_timestamp}.{os.getpid()}.txt"
            tmpfile = big_file.translate_filename_to_exfat(tmpfile)
            tmpfile = tmpfile.replace(" ", '_')
            self.path = Path(tempfile.gettempdir()) / tmpfile
            super().reset()


    class FileHandle(Destination):
        """
        A Destination wrapping an open Python file handle.

        This Destination writes to an already-open file handle.
        It will never close the file handle; it will only ever
        write to it, and flush it.

        Every time a formatted log message is received,
        FileHandle writes it immediately to the file handle.
        If flush=True, FileHandle will immediately flush the
        file handle after writing; by default flush is False.
        """
        def __init__(self, handle, *, flush=False):
            super().__init__()
            if not isinstance(handle, TextIOBase):
                raise TypeError(f"invalid file handle {handle}")
            self.handle = handle
            self._flush = flush

        def write(self, elapsed, thread, formatted):
            self.handle.write(formatted)
            if self._flush:
                self.handle.flush()

        def flush(self):
            self.handle.flush()


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
            self.number = 1
            self.events = []
            self.longest_message = 0
            self._reset()

        def _reset(self):
            self.depth = 0
            self.previous_message_elapsed = 0

        def _event(self, event):
            if event.message is not None:
                duration = event.elapsed - self.previous_message_elapsed
                assert duration >= 0, f"duration should be >= 0 but it's {duration}"
                event._duration = duration
                self.previous_message_elapsed = event.elapsed
                self.longest_message = max(self.longest_message, len(event.message))
            self.events.append(event)

        def reset(self):
            assert self.owner
            super().reset()
            self.number += 1
            self._reset()

        def start(self, start_time_ns, start_time_epoch, formatted):
            self._event(SinkStartEvent(self.number, start_time_ns, start_time_epoch, formatted))

        def end(self, elapsed, formatted):
            self._event(SinkEndEvent(self.number, elapsed, formatted))

        def write(self, elapsed, thread, formatted):
            self._event(SinkWriteEvent(self.number, self.depth, elapsed, thread, formatted))

        def log(self, elapsed, thread, format, message, formatted):
            self._event(SinkLogEvent(self.number, self.depth, elapsed, thread, format, message, formatted))

        def enter(self, elapsed, thread, message, formatted):
            self._event(SinkEnterEvent(self.number, self.depth, elapsed, thread, message, formatted))
            self.depth += 1

        def exit(self, elapsed, thread, message, formatted):
            self.depth -= 1
            self._event(SinkExitEvent(self.number, self.depth, elapsed, thread, message, formatted))

        def __iter__(self):
            for e in self.events:
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
            if not print:
                print = builtins.print

            if width is None:
                width = self.longest_message

            for e in self.events:
                elapsed = e.elapsed / 1_000_000_000.0
                duration = e.duration / 1_000_000_000.0
                epoch = elapsed + self.owner._start_time_epoch
                ts = timestamp(epoch)
                indent_str = ' ' * (e.depth * indent)
                thread = e.thread or current_thread()

                fields = {
                    'elapsed': elapsed,
                    'duration': duration,
                    'format': e.format or '',
                    'timestamp': ts,
                    'thread': thread,
                    'type': e.type,
                    'depth': e.depth,
                    'indent': indent_str,
                }
                prefix_str = prefix.format_map(fields)
                space_str = " " * len(prefix_str)
                message = e.message or ''
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

    def reset(self):
        super().reset()
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

    def end(self, elapsed, formatted):
        pass

    def write(self, elapsed, thread, formatted):
        self._event(elapsed, formatted.rstrip('\n'))

    def log(self, elapsed, thread, format, message, formatted):
        self._event(elapsed, message.rstrip('\n'))

    def enter(self, elapsed, thread, message, formatted):
        self._event(elapsed, message + " start")
        self.stack.append(message)

    def exit(self, elapsed, thread, message, formatted):
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
            indent2 = indent_str * depth
            print(f"{indent_str}{format_time(start)}  {format_time(elapsed)}  {indent2}{event}".rstrip())


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
        self._log = Log(self._destination, threading=False, formats={"start": {"format": "log start"}, "end": None}, prefix='', clock=clock)

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
