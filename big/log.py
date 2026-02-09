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

try:
    # 3.7+
    from time import monotonic_ns as default_clock
except ImportError: # pragma: no cover
    # 3.6 compatibility
    from time import monotonic
    def default_clock():
        return int(monotonic() * 1_000_000_000.0)


from . import builtin
mm = builtin.ModuleManager()
export = mm.export


export('default_clock')


@export
class SinkEvent:
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
    # 1 for the dot
    time_width = time_seconds_width + 1 + time_fractional_width
    return f'[{{elapsed:0{time_width}.{time_fractional_width}f}} {{thread.name:>{thread_name_width}}}] '


@export
class Log:
    """
    A lightweight text-based log suitable for debugging.

    Calling the Log instance as a function logs a message to
    the log.  The signature of this function is identical
    to builtins.print, except the Log instance doesn't support
    the "file" keyword-only parameter.

    Log supports a header(s) method.  This logs a string
    preceded and followed by a "separator line", which makes
    it stand out in the log.

    Log supports enter(s) and exit() methods.

    If you pass positional arguments to the Log constructor,
    these define "destinations" for log messages.  Destination
    objects can be any of the following types / objects:

        print (the Python builtin function)
            Log messages are printed using print(s, end='').
        str or pathlib.Path object
            Log messages are buffered locally,
            and dumped to the file named by the string.
            Equivalent to big.log.File(pathlib.Path(argument)).
        list object
            Log messages are appended to the list.  Equivalent
            to big.log.List(argument).
        io.TextIOBase object
            Log messages are written to the file-like object
            using its write method.  Equivalent to
            big.log.FileHandle(argument).
        callable object
            The callable object is called with every log message.
            Equivalent to big.log.Callable(argument).
        Destination object
            Method calls to the Log are passed through to the
            Destination object.  If the Destination doesn't define
            a high-level logging function (log, header, enter, exit)
            the message is formatted and logged to that Destination
            using its write method.

    If you don't pass in any explicit destinations, Log behaves
    as if you'd passed in "print".


    The following are all keyword-only parameters to the
    Log constructor, used to adjust the behavior of the log:

    "name" is the desired name for this log (default 'Log').

    If "threading" is true (the default), log messages aren't logged
    immediately; they're minimally processed then sent to a logging
    thread maintained by the Log object which fully formats and logs
    the message.  This reduces the overhead for logging a message,
    resulting in faster logging performance.  If threading is false,
    log messages are formatted and logged immediately in the Log call,
    using a threading.Lock() object to ensure thread safety.

    "indent" should be an integer, the number of spaces to indent by
    when indenting the log (using Log.start).  Default is 4.

    "width" should be an integer, default is 79.  This is only used
    to format separator lines (see "separator" and "banner_separator").

    "clock" should be a function returning nanoseconds since some event.
    The default value is time.monotonic_ns for Python 3.7, and a
    locally-defined compatibility function for Python 3.6
    (returning time.monotonic() * one billion).

    "clock" should be a function returning seconds since the UNIX epoch,
    as a floating-point number with fractional seconds. The default value
    is time.time.

    "timestamp" should be a function that formats
    float-seconds-since-epoch into a pleasant human-readable format.
    Default is big.time.timestamp_human.

    "separator" is a string that will be repeated to create
    "separator lines" in the log, setting off headers.

    "banner_separator" is also a string, a special "separator"
    string only used for the "initial" and "final" log messages.

    "prefix" should be a string used to format text inserted
    at the beginning of every log message.  Default is
    "[{elapsed:014.10} :: {thread.name:8}] ".

    "initial" should be a string used as an initial log message when the
    log is started.  If initial is false, there is no automatic initial
    log message. The default value is '{name} start at {timestamp}',

    "final" should be a string used as a final log message when the log is
    closed.  If final is false, there is no automatic final log message.
    The default value is '{name} finish at {timestamp}\n'.

    "initial", "final", and "prefix" are formatted using str.format()
    with the following values defined:

        elapsed
            the elapsed time since log start, as float seconds
        name
            the name of the log
        thread
            a handle to the thread that logged this message
        time
            the time of the log message, as float-seconds-since-epoch
        timestamp - the time of the log message,
            formatted with the Log timestamp argument

    """

    def __init__(self, *destinations,
            name='Log',
            threading=True,

            clock=default_clock,
            timestamp_clock=time.time,

            indent=4,
            width=79,

            formats = {},
            prefix=prefix_format(3, 10, 12),
            timestamp_format=big_time.timestamp_human,
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
                    return method
                setattr(self, key, make_method(key))

        print = builtins.print
        if not destinations:
            destinations = [print]

        self._destinations = []
        append = self._destinations.append

        for destination in destinations:
            destination = Log.destination(destination)

            if destination is not None:
                append(destination)
                destination.register(self)

        self._manage_thread()



    @classmethod
    def destination(cls, destination):
        if destination is None:
            return None
        if isinstance(destination, cls.Destination):
            return destination
        if destination is print:
            return cls.Print()
        if isinstance(destination, str):
            return cls.File(Path(destination))
        if isinstance(destination, Path):
            return cls.File(destination)
        if isinstance(destination, list):
            return cls.List(destination)
        if isinstance(destination, TextIOBase):
            return cls.FileHandle(destination)
        if callable(destination):
            return cls.Callable(destination)
        raise ValueError(f"don't know how to log to destination {destination!r}")

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
            "start_timestamp": self._start_timestamp,
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


    ##
    ## In Log, all logging methods are implemented using "work"
    ## objects.  work is a list of jobs:
    ##     [job, job2, ...]
    ## The jobs are 2-tuples:
    ##      (callable, args)
    ## They're called simply as
    ##      callable(*args)
    ##
    ## You call _dispatch(work) to get some work done.
    ## If threaded is True, the work is sent to the worker
    ## thread; if threaded is False the work is executed
    ## immediately, in-thread.
    ##
    ## None is also a legal "job"; it must be the last "job"
    ## in a work list.  If threaded is True, this causes the
    ## worker thread to exit; if threaded is False it causes
    ## the dispatch call to return immediately.
    ##
    ## Why send sequences of jobs--why not queue jobs
    ## individually?  If you call into the log from
    ## multiple threads, and one thread calls close(),
    ## we want the [flush, close, None] work to run
    ## atomically.  If we queued them separately,
    ## we could have a race with another thread trying
    ## to log something.  We guarantee to the destinations
    ## that "close" will always be immediately preceded
    ## by a "flush", and if they get a "close" they won't
    ## get any more messages unless they first receive
    ## a "reset".
    ##
    ## _dispatch also takes a notify argument.  If it's true,
    ## it must be a callable; _dispatch will take care to
    ## ensure that the callable is *always* called, and
    ## is called *after* the work has been executed.

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
                thread = self._thread
                queue = self._queue
                self._thread = self._queue = None
                if thread is not None:
                    queue.put([None])
                    thread.join()

                self._threading = False

    def _atexit(self):
        self.close()
        self._stop_thread()


    def _dispatch(self, work, *, notify=None):
        if not self._threading:
            self._execute(work)
            if notify:
                notify()
            return

        lock = None
        try:
            if notify:
                lock = self._lock
                lock.acquire()
                if not self._threading: lock.release() ; lock = None ; return self._dispatch(work, notify=notify)

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

        Only three states are supported:
            initial
            logging
            closed

        You can always transition from any state to any other
        state, with one exception: you can't transition from
        "closed" to "logging".  (The only way to escape "closed"
        state is to reset the log, which transitions to "initial".)

        This means you can in some circumstances make two state
        transitions at once:
             from "initial" to "closed", and
             from "logging" to "initial".
        When you do, you pass through the intermediary state.
        (e.g. if you transition from "initial" to "closed",
        you'll enter and exit "logging" state on the way.)

        If you're in "initial" and transition to "logging",
        you open the log (send a start event).

        If you're in "logging" and transition to "closed",
        you close the log (send end, flush, and close events).

        If you're in "closed" and transition to "initial",
        you'll reset the log (send a reset event).

        If ns and epoch are specified, those are used as start time
        for the log (if we transition from "initial" to "logging"
        and/or end time of the log (if we transition from "logging"
        to "closed").  It's an error to transition from another state
        to "closed" or "initial" without specifying ns and epoch.
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
        self._start_timestamp = self._timestamp_format(start_time_epoch)
        self._dirty = False

    def reset(self):
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

    def flush(self, block=False):
        if not block:
            notify = None
        else:
            blocker = Lock()
            blocker.acquire()
            notify = blocker.release

        self._dispatch([(self._flush, ())], notify=notify)

        if notify:
            blocker.acquire()

    def _close(self):
        for destination in self._destinations:
            destination.close()

    def close(self, block=True):
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
        time = self._clock()
        thread = current_thread()

        if not isinstance(formatted, str):
            raise TypeError('formatted must be str')

        if formatted:
            self._dispatch( [(self._write, (time, thread, formatted)),] )

    def _log(self, time, thread, format, message):
        ## If you call
        ##     log("abc", "def\nghi", sep='\n')
        ## then here's what happens at the destinations:
        ##
        ## If the destination is a Log, it calls
        ##     destination.log("abc", "def\nghi", sep='\n')
        ## If the destination is a Destination with log defined, it calls
        ##     destination.log(elapsed, thread, "abc")
        ##     destination.log(elapsed, thread, "def")
        ##     destination.log(elapsed, thread, "ghi")
        ## If the destination is a Destination without log defined,
        ## assuming prefix='[prefix] ', it calls
        ##     destination.write(elapsed, thread, "[prefix] abc\n[prefix] def\n[prefix] ghi\n")

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
        ## If you call
        ##     log("abc", "def\nghi", sep='\n')
        ## then here's what happens at the destinations:
        ##
        ## If the destination is a Log, it calls
        ##     destination.log("abc", "def\nghi", sep='\n')
        ## If the destination is a Destination with log defined, it calls
        ##     destination.log(elapsed, thread, "abc")
        ##     destination.log(elapsed, thread, "def")
        ##     destination.log(elapsed, thread, "ghi")
        ## If the destination is a Destination without log defined,
        ## assuming prefix='[prefix] ', it calls
        ##     destination.write(elapsed, thread, "[prefix] abc\n[prefix] def\n[prefix] ghi\n")

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
        """
        return self(*args, end=end, sep=sep, flush=flush, format=format)


    # "with log:" simply flushes the log on exit.
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.flush()

    class SubsystemContextManager:
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
        time = self._clock()
        thread = current_thread()

        self._dispatch([
            (self._enter_exit, ('enter', time, thread, message)),
            (self._append_nesting, (message,)),
            ])
        return self.SubsystemContextManager(self)

    def _exit(self, time, thread):
        if not self._nesting:
            return

        message = self._pop_nesting()
        self._enter_exit('exit', time, thread, message)

    def exit(self):
        time = self._clock()
        thread = current_thread()

        self._dispatch([(self._exit, (time, thread))])



    class Destination:
        """
        Base class for objects that receive messages from a big.Log.

        All Destination objects must define:

            write(elapsed, thread, formatted)

        In addition, Destination subclasses may optionally override
        the following methods:

            flush()
            close()
            reset()
            start(start_time_ns, start_time_epoch, formatted)
            end(elapsed, formatted)
            write(elapsed, thread, message, format, formatted)
            enter(elapsed, thread, message, formatted)
            exit(elapsed, thread, message, formatted)

        For all these methods, Destination subclasses need not
        call the base class method.  Note that the base class
        method for the last five of these--the methods that take
        "formatted"--all call self.write, like so:
            self.write(elapsed, thread, formatted)

        Finally, Destination subclasses may also override this method:
            register(owner)
        For this method, Destination subclasses are *required*
        to call the base class implementation
        ("super().register(owner)").

        The meaning of each argument to a Destination methods:

        * elapsed is the elapsed time since the log was
          started/reset, in nanoseconds.
        * thread is the threading.Thread handle for the thread
          that logged the message.  thread may be None if the
          event isn't associated with any particular thread
          (start and end events).
        * formatted is the formatted log message.
        * format is the name of the "format" (predefined or passed in to
          the constructor) applied to "message" to produce "formatted".
        * message is the original message passed in to a Log method.
        * owner is the Log object that owns this Destination.
          (A Destination cannot be shared between multiple Log objects.)
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

        def write(self, elapsed, thread, formatted):
            raise RuntimeError("pure virtual Destination.write called")

        def start(self, start_time_ns, start_time_epoch, formatted):
            self.write(0, None, formatted)

        def end(self, elapsed, formatted):
            self.write(elapsed, None, formatted)

        def log(self, elapsed, thread, format, message, formatted):
            self.write(elapsed, thread, formatted)

        def enter(self, elapsed, thread, message, formatted):
            self.write(elapsed, thread, formatted)

        def exit(self, elapsed, thread, message, formatted):
            self.write(elapsed, thread, formatted)



    class Callable(Destination):
        "A Destination wrapping a callable."
        def __init__(self, callable):
            super().__init__()
            self.callable = callable

        def write(self, elapsed, thread, formatted):
            self.callable(formatted)



    class Print(Destination):
        "A Destination wrapping builtins.print."
        def __init__(self):
            super().__init__()
            self.print = builtins.print

        def write(self, elapsed, thread, formatted):
            self.print(formatted, end='', flush=True)



    class List(Destination):
        "A Destination wrapping a Python list."
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
        "A Destination that buffers log messages, printing them with builtins.print when flushed."
        def __init__(self, destination=None):
            super().__init__()
            self.array = []
            self.destination = Log.destination(destination) or Log.Print()
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


    class File(Destination):
        "A Destination wrapping a file in the filesystem."
        def __init__(self, path, mode="at", *, flush=False):
            super().__init__()

            assert mode in ("at", "wt", "xt", "a", "w", "x")

            self.array = array = []
            self.path = Path(path)
            self.mode = mode
            self.always_flush = flush
            self.f = None

        def register(self, owner):
            super().register(owner)
            self.reset()

        def reset(self):
            super().reset()
            self.f = self.path.open(self.mode) if self.always_flush else None

        def write(self, elapsed, thread, formatted):
            if self.always_flush:
                self.f.write(formatted)
                self.f.flush()
            elif formatted:
                self.array.append(formatted)

        def flush(self):
            if self.array:
                assert not self.always_flush
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
        "A Destination that writes to a timestamped temporary file."
        def __init__(self, *, flush=False):
            # use a fake path for now
            path = Path(tempfile.gettempdir()) / f"{os.getpid()}.tmp"
            super().__init__(path)
            self.always_flush = flush

        def reset(self):
            assert self.owner
            log_timestamp = self.owner.timestamp_format(self.owner.start_time_epoch)
            log_timestamp = log_timestamp.replace("/", "-").replace(":", "-").replace(" ", ".")
            tmpfile = f"{self.owner.name}.{log_timestamp}.{os.getpid()}.txt"
            tmpfile = big_file.translate_filename_to_exfat(tmpfile)
            tmpfile = tmpfile.replace(" ", '_')
            self.path = Path(tempfile.gettempdir()) / tmpfile
            super().reset()



    class FileHandle(Destination):
        "A Destination wrapping a Python file handle."
        def __init__(self, handle, *, flush=False):
            super().__init__()
            if not isinstance(handle, TextIOBase):
                raise TypeError(f"invalid file handle {handle}")
            self.handle = handle
            self.immediate = flush

        def write(self, elapsed, thread, formatted):
            self.handle.write(formatted)
            if self.immediate:
                self.handle.flush()

        def flush(self):
            self.handle.flush()


    class Sink(Destination):
        """
        A Destination that accumulates log messages for later iteration or printing.

        Events include thread information and raw timestamps.

        You may iterate over the Sink; this yields 6-tuples:
            [type, thread, elapsed, duration, depth, message]
        elapsed and duration are in nanoseconds.  thread is the
        threading.Thread handle for the thread that logged the message.
        depth is the current enter/exit depth, as an integer,
        starting at 0. type is the thread type, one of
        Sink.{WRITE, LOG, HEADER, FOOTER, HEADING, ENTER, EXIT}.
        message is the string that was logged.

        You may also call print(), which formats the events
        and prints them using builtins.print.
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
    Creates a Log with an OldDestination and exposes the old interface.
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
