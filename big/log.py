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
class SinkBaseEvent:
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

    def __init__(self, number, elapsed, type, duration=0, depth=0, epoch=None, format='', formatted='', message='', ns=None, thread=None):
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
        return f"{self.__class__.__name__}(number={self._number}, elapsed={self._elapsed}, type={self._type!r}, message={self._message!r}, duration={self._duration}, depth={self._depth}, epoch={self._epoch}, formatted={self._formatted!r}, ns={self._ns!r}, thread={self._thread})"

    def __eq__(self, other):
        return (isinstance(other, SinkBaseEvent)
            and (self._number == other._number)
            and (self._elapsed == other._elapsed)
            and (self._type == other._type)
            and (self._message == other._message)
            and (self._thread == other._thread)
            and (self._epoch == other._epoch)
            and (self._depth == other._depth)
            )

    def __lt__(self, other):
        if not isinstance(other, SinkBaseEvent):
            raise TypeError(f"'<' not supported between instances of SinkBaseEvent and {type(other)}")
        return (
                (self._number  <= other._number)
            and (self._elapsed <  other._elapsed)
            )


@export
class SinkEvent(SinkBaseEvent):
    def __init__(self, number, elapsed, type, thread, format, message, formatted, depth, **kwargs):
        super().__init__(
            number=number,
            elapsed=elapsed,
            type=type,
            format=format,
            message=message,
            depth=depth,
            formatted=formatted,
            thread=thread,
            **kwargs
            )

@export
class SinkStartEvent(SinkBaseEvent):
    def __init__(self, number, start_time_ns, start_time_epoch, formatted):
        super().__init__(
            number=number,
            elapsed=0,
            type=Log.Sink.START,
            ns=start_time_ns,
            epoch=start_time_epoch,
            formatted=formatted,
            )

@export
class SinkEndEvent(SinkBaseEvent):
    def __init__(self, number, elapsed, formatted):
        super().__init__(
            number=number,
            type=Log.Sink.END,
            elapsed=elapsed,
            formatted=formatted,
            )




_spaces = " " * 1024

_sep = " "
_end = "\n"

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
            clock=default_clock,

            formats = {},

            indent=4,
            name='Log',
            prefix=prefix_format(3, 10, 12),
            threading=True,
            timestamp=big_time.timestamp_human,
            timestamp_clock=time.time,
            width=79,
            ):

        self._clock = clock
        self._timestamp_clock = timestamp_clock

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

                        self._dispatch( [(self._log, (time, thread, key, message))] )
                    return method
                setattr(self, key, make_method(key))


        atexit.register(self._atexit)

        t1 = clock()
        start_time_epoch = timestamp_clock()
        t2 = clock()
        start_time_ns = (t1 + t2) // 2

        array = []
        append = array.append

        self._name = name

        self._width = width
        self._prefix = prefix
        self._nesting = []
        self._indent = indent
        self._spaces = ''
        self._timestamp = timestamp

        self._destinations = array

        self._threading = threading
        self._queue = None
        self._thread = None
        self._closed = True

        # if threading is True, _lock is only used for close and reset
        self._lock = Lock()
        self._blocker = blocker = Lock()
        blocker.acquire()

        self._reset(start_time_ns, start_time_epoch, False, None)

        print = builtins.print
        if not destinations:
            destinations = [print]

        thread = current_thread()

        for destination in destinations:
            destination = Log.destination(destination)

            if destination is not None:
                append(destination)
                destination.register(self)

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
    def timestamp(self):
        return self._timestamp

    @property
    def timestamp_clock(self):
        return self._timestamp_clock

    @property
    def width(self):
        return self._width

    @property
    def closed(self):
        with self._lock:
            return self._closed

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


    def _atexit(self):
        self.close()

    def _elapsed(self, t):
        # t should be a value returned by _clock.
        # returns t converted to elapsed time
        # since self.start_time_ns, as integer nanoseconds.
        return t - self._start_time_ns

    def _ns_to_float(self, ns):
        return ns / 1_000_000_000.0

    def _reset(self, start_time_ns, start_time_epoch, send_reset, signal):
        # if we're not closed, flush before we reset
        if not self._closed:
            self._flush()

        self._nesting = []
        self._spaces = ''
        self._closed = False
        self._start_time_ns = start_time_ns
        self._start_time_epoch = start_time_epoch
        self._end_time_epoch = None
        self._want_start = "start" in self._formats
        self._want_end = "end" in self._formats

        for destination in self._destinations:
            if send_reset:
                destination.reset()

        if self._threading and (self._thread is None):
            self._queue = Queue()
            self._thread = Thread(target=self._worker_thread, args=(self._queue,), daemon=True)
            self._thread.start()

        if signal:
            signal()

    def reset(self):
        with self._lock:

            clock = self._clock
            t1 = clock()
            start_time_epoch = self._timestamp_clock()
            t2 = clock()
            start_time_ns = (t1 + t2) // 2

            if self._threading and (self._thread is not None):
                blocker = self._blocker
                args = [start_time_ns, start_time_epoch, True, blocker.release]

                work = [(self._reset, args)]
                self._queue.put(work)

                blocker.acquire()

                return

            self._reset(start_time_ns, start_time_epoch, True, None)

    def _format_s(self, elapsed, thread, format, *, message=None, line=None, prefix=None):
        if not format:
            return ''

        elapsed = self._ns_to_float(elapsed)
        epoch = elapsed + self._start_time_epoch
        timestamp = self._timestamp(epoch)
        start_timestamp = self._timestamp(self._start_time_epoch)

        substitutions = {
            "elapsed": elapsed,
            "name": self._name,
            "start_timestamp": start_timestamp,
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
        prefix = self._format_s(elapsed, thread, self._prefix) + self._spaces

        if message:
            message_lines = message.split('\n')
        else:
            message_lines = ('',)

        buffer = []
        append = buffer.append
        for t in self._formats[format]:
            f, l, contains_message, append_repeated_line = t
            if contains_message:
                iterable = message_lines
            else:
                iterable = [None]
            for ml in iterable:
                formatted = self._format_s(elapsed, thread, f, message=ml, line=l, prefix=prefix)
                append(formatted)
                if append_repeated_line:
                    length = len(formatted)
                    delta = self._width - length
                    if delta > 0:
                        append(append_repeated_line[:delta])
                append("\n")
        return "".join(buffer)


    ##
    ## The worker queue is used to send sequences of "jobs":
    ##     [job, job2, ...]
    ##
    ## The jobs are 2-tuples:
    ##      (callable, args)
    ## They're called simply as
    ##      callable(*args)
    ##
    ## None is also a legal "job",
    ## which tells the worker thread to exit.
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

    def _dispatch(self, work):
        if self._threading:
            if not self._closed:
                self._queue.put(work)
            return

        with self._lock:
            if not self._closed:
                self._execute(work)


    def _write(self, time, thread, s):
        if self._want_start:
            self._log_start(thread)

        elapsed = self._elapsed(time)

        for destination in self._destinations:
            destination.write(elapsed, thread, s)

    def write(self, s):
        time = self._clock()
        thread = current_thread()

        if not isinstance(s, str):
            raise TypeError('s must be str')

        self._dispatch( [(self._write, (time, thread, s))] )

    def _log_banner(self, time, thread, format, args):
        assert format in self._formats
        formatted = self._format_message(time, thread, format, None)
        args.append(formatted)

        for destination in self._destinations:
            getattr(destination, format)(*args)

    def _log_start(self, thread):
        self._want_start = False
        self._log_banner(self._start_time_ns, thread, 'start', [self._start_time_ns, self._start_time_epoch])

    def _log_end(self, time, thread):
        self._clear_nesting()
        elapsed = self._elapsed(time)
        self._log_banner(time, thread, 'end', [elapsed])

    def _log(self, time, thread, format, message, method='log'):
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

        if self._want_start:
            self._log_start(thread)

        elapsed = self._elapsed(time)
        formatted = self._format_message(time, thread, format, message)

        for destination in self._destinations:
            getattr(destination, method)(elapsed, thread, format, message, formatted)


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
        if end is _end:
            end = ''
        elif end.endswith('\n'):
            end = end[:-1]
        message = f"{sep.join(args)}{end}"
        self._log(time, thread, format, message)


    def __call__(self, *args, sep=_sep, end=_end, flush=False, format='print'):
        "Alias for Log.print()."

        time = self._clock()
        thread = current_thread()

        if format and (format not in self._formats):
            raise ValueError(f"undefined format {format!r}")

        if end is not _end:
            end = str(end)
        if sep is not _sep:
            sep = str(sep)
        args = [str(a) for a in args]

        self._dispatch( [(self._print, (time, thread, args, sep, end, flush, format))] )

    def print(self, *args, end=_end, sep=_sep, flush=False, format='print'):
        """
        Logs a message, with the interface of builtins.print.
        """
        return self(*args, end=end, sep=sep, flush=flush, format=format)

    class SubsystemContextManager:
        def __init__(self, log):
            self.log = log

        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_value, traceback):
            if self.log:
                self.log.exit()

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
        self._cache_spaces()


    def _enter_exit(self, verb, time, thread, message):
        if self._want_start:
            self._log_start(thread)

        elapsed = self._elapsed(time)
        formatted = self._format_message(time, thread, verb, message)

        for destination in self._destinations:
            getattr(destination, verb)(elapsed, thread, message, formatted)

    def enter(self, message):
        time = self._clock()
        thread = current_thread()

        self._dispatch([
                    (self._enter_exit, ('enter', time, thread, message)),
                    (self._append_nesting, (message,)),
                    ])
        return self.SubsystemContextManager(self)


    def _exit(self, time, thread):
        assert not self._want_start

        if not self._nesting:
            return

        message = self._pop_nesting()
        self._enter_exit('exit', time, thread, message)

    def exit(self):
        time = self._clock()
        thread = current_thread()

        self._dispatch([(self._exit, (time, thread))])


    def _flush(self):
        for destination in self._destinations:
            destination.flush()

    def flush(self):
        self._dispatch( [(self._flush, ())] )

    def _close(self):
        for destination in self._destinations:
            destination.close()

    def close(self):
        t1 = self._clock()
        end_time_epoch = self._timestamp_clock()
        t2 = self._clock()
        time = (t1 + t2) / 2

        thread = current_thread()

        with self._lock:
            if self._closed:
                return

            self._closed = True
            self._end_time_epoch = end_time_epoch

            work = []
            append = work.append

            if self._want_end:
                append((self._log_end, (time, thread)))
            append((self._flush, ()))
            append((self._close, ()))
            append(None)

            if self._threading:
                assert self._thread is not None
                self._queue.put(work)
                self._thread.join()
                self._thread = None
            else:
                self._execute(work)


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.flush()


    class Destination:
        """
        Base class for objects that receive messages from a big.Log.

        All Destination objects must define:

            write(elapsed, thread, s)

        The arguments to write and all other Destination methods:

        * elapsed is the elapsed time since the log was
          started/reset, in nanoseconds.
        * thread is the
          threading.Thread handle for the thread
          that logged the message.
        * s is the formatted log message.

        In addition, Destination objects may optionally define the
        following methods:

            flush()
            close()
            reset()
            start(start_time_epoch)
            end(end_time_epoch)

        Destination objects may also define any of these methods:

            log(elapsed, thread, message, *, flush=False)
            heading(elapsed, thread, message, separator)
            enter(elapsed, thread, message, separator)
            exit(elapsed, thread, separator)

        * message is the original message passed in to a Log method.
        * separator is the separator string to use, or None if the
          default separator should be used.

        If these are defined, high-level calls to those
        methods will turn into calls to the equivalent
        method on the Destination, otherwise the message will
        be formatted into a string and logged to the Destination
        using its write() method.

        For example, if a Destination defines log(), then
        calls to log() on the Log object will call
        log() on the Destination.  Otherwise, the message
        will be formatted, and the Log will call the
        Destination's write() method.

        (The log() method only takes a message string; the
        positional arguments to Log.log() are formatted
        (using sep and end) before they're passed in to
        Destination.log().)
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

        def write(self, elapsed, thread, s):
            raise RuntimeError("pure virtual Destination.write called")

        def log(self, elapsed, thread, format, message, formatted):
            self.write(elapsed, thread, formatted)

        def start(self, start_time_ns, start_time_epoch, formatted):
            self.write(0, None, formatted)

        def end(self, elapsed, formatted):
            self.write(elapsed, None, formatted)

        def enter(self, elapsed, thread, message, formatted):
            self.write(elapsed, thread, formatted)

        def exit(self, elapsed, thread, message, formatted):
            self.write(elapsed, thread, formatted)



    class Callable(Destination):
        "A Destination wrapping a callable."
        def __init__(self, callable):
            super().__init__()
            self.callable = callable

        def write(self, elapsed, thread, s):
            self.callable(s)



    class Print(Destination):
        "A Destination wrapping builtins.print."
        def __init__(self):
            super().__init__()
            self.print = builtins.print

        def write(self, elapsed, thread, s):
            self.print(s, end='', flush=True)




    class List(Destination):
        "A Destination wrapping a Python list."
        def __init__(self, list):
            super().__init__()
            self.array = list

        def write(self, elapsed, thread, s):
            self.array.append(s)



    class Buffer(Destination):
        "A Destination that buffers log messages, printing them with builtins.print when flushed."
        def __init__(self, destination=None):
            super().__init__()
            self.array = []
            self.destination = Log.destination(destination) or Log.Print()
            self.last_elapsed = self.last_thread = None

        def write(self, elapsed, thread, s):
            self.last_elapsed = elapsed
            self.last_thread = thread
            self.array.append(s)

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

        def write(self, elapsed, thread, s):
            if self.always_flush:
                self.f.write(s)
                self.f.flush()
            else:
                self.array.append(s)

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
            log_timestamp = self.owner.timestamp(self.owner.start_time_epoch).replace("/", "-").replace(":", "-").replace(" ", ".")
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

        def write(self, elapsed, thread, s):
            self.handle.write(s)
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

        WRITE = 'write'
        LOG = 'log'
        START = 'start'
        # HEADER = 'header'
        # FOOTER = 'footer'
        # HEADING = 'heading'
        ENTER = 'enter'
        EXIT = 'exit'
        END = 'end'

        def __init__(self):
            super().__init__()
            self.number = 0
            self._reset()

        def register(self, owner):
            super().register(owner)
            self.reset()

        def _reset(self):
            self.depth = 0
            self.events = []
            self.longest_message = 0

        def reset(self):
            assert self.owner
            super().reset()
            self.number += 1
            self._reset()

        def _event(self, event):
            events = self.events
            if events:
                previous = events[-1]
                duration = event.elapsed - previous.elapsed
                assert duration >= 0, f"duration should be >= 0 but it's {duration}"
                previous._duration = duration
            events.append(event)
            self.longest_message = max(self.longest_message, len(event.message))

        def start(self, start_time_ns, start_time_epoch, formatted):
            self._event(SinkStartEvent(self.number, start_time_ns, start_time_epoch, formatted))

        def end(self, elapsed, formatted):
            self._event(SinkEndEvent(self.number, elapsed, formatted))

        def write(self, elapsed, thread, s):
            self._event(SinkEvent(self.number, elapsed, self.WRITE, thread, '', s, None, self.depth))

        def log(self, elapsed, thread, format, message, formatted):
            self._event(SinkEvent(self.number, elapsed, self.LOG, thread, format, message, formatted, self.depth))

        # def header(self, elapsed, thread, formatted, message, separator):
        #     self._event(SinkEvent(self.number, elapsed, self.HEADER, thread, message, formatted, self.depth, separator=separator))

        # def footer(self, elapsed, thread, formatted, message, separator):
        #     self._event(SinkEvent(self.number, elapsed, self.FOOTER, thread, message, formatted, self.depth, separator=separator))

        # def heading(self, elapsed, thread, formatted, message, separator):
        #     self._event(SinkEvent(self.number, elapsed, self.HEADING, thread, message, formatted, self.depth, separator=separator))

        def enter(self, elapsed, thread, message, formatted):
            self._event(SinkEvent(self.number, elapsed, self.ENTER, thread, 'enter', message, formatted, self.depth))
            self.depth += 1

        def exit(self, elapsed, thread, message, formatted):
            self.depth -= 1
            self._event(SinkEvent(self.number, elapsed, self.EXIT, thread, 'exit', message, formatted, self.depth))

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
                    'format': e.format,
                    'timestamp': ts,
                    'thread': thread,
                    'type': e.type,
                    'depth': e.depth,
                    'indent': indent_str,
                }
                prefix_str = prefix.format_map(fields)
                space_str = " " * len(prefix_str)
                message = e.message
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
        self._event(0, 'log start')

    def _event(self, elapsed, event):
        events = self.events
        if events:
            previous = events[-1]
            previous[1] = elapsed - previous[0]
        events.append([elapsed, 0, event, len(self.stack)])
        self.longest_event = max(self.longest_event, len(event))

    def write(self, elapsed, thread, s):
        self._event(elapsed, s.rstrip('\n'))

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
            print(f"{indent_str}{column_dashes}  {column_dashes}  {'-' * self.longest_event}")

        for start, elapsed, event, depth in self:
            indent2 = indent_str * depth
            print(f"{indent_str}{format_time(start)}  {format_time(elapsed)}  {indent2}{event}")


@export
class OldLog:
    """
    A drop-in replacement for the old big.log.Log class.
    Creates a Log with an OldDestination and exposes the old interface.
    """

    def __init__(self, clock=None):
        self._destination = OldDestination()
        clock=clock or default_clock
        self._log = Log(self._destination, threading=False, formats={"start": None, "end": None }, prefix='', clock=clock)

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
