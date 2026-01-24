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


__all__ = []

def export_name(s):
    __all__.append(s)

def export(o):
    export_name(o.__name__)
    return o


export_name('default_clock')


@export
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

    def write(self, elapsed, thread, message):
        raise RuntimeError("virtual write method called on", self)

    def flush(self):
        pass

    def close(self):
        pass

    def reset(self):
        pass



@export
class Callable(Destination):
    "A Destination wrapping a callable."
    def __init__(self, callable):
        super().__init__()
        self.callable = callable

    def write(self, elapsed, thread, message):
        self.callable(message)



@export
class Print(Destination):
    "A Destination wrapping builtins.print."
    def __init__(self):
        super().__init__()
        self.print = builtins.print

    def write(self, elapsed, thread, message):
        self.print(message, end='', flush=True)




@export
class List(Destination):
    "A Destination wrapping a Python list."
    def __init__(self, list):
        super().__init__()
        self.array = list


    def write(self, elapsed, thread, message):
        self.array.append(message)



@export
class Buffer(Destination):
    "A Destination that buffers log messages, printing them with builtins.print when flushed."
    def __init__(self):
        super().__init__()
        self.array = []

    def write(self, elapsed, thread, message):
        self.array.append(message)

    def flush(self):
        if self.array:
            contents = "".join(self.array)
            self.array.clear()
            print(contents, end='')


@export
class File(Destination):
    "A Destination wrapping a file in the filesystem."
    def __init__(self, path, mode="at", *, flush=False):
        super().__init__()

        assert mode in ("at", "wt", "xt", "a", "w", "x")

        self.array = array = []
        self.path = Path(path)
        self.mode = mode
        self.always_flush = flush

        self.reset()

    def reset(self):
        super().reset()
        self.f = self.path.open(self.mode) if self.always_flush else None

    def write(self, elapsed, thread, message):
        if self.always_flush:
            self.f.write(message)
            self.f.flush()
        else:
            self.array.append(message)

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



@export
class FileHandle(Destination):
    "A Destination wrapping a Python file handle."
    def __init__(self, handle, *, flush=False):
        super().__init__()
        if not isinstance(handle, TextIOBase):
            raise TypeError(f"invalid file handle {handle}")
        self.handle = handle
        self.immediate = flush

    def write(self, elapsed, thread, message):
        self.handle.write(message)
        if self.immediate:
            self.handle.flush()

    def flush(self):
        self.handle.flush()


@export
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
    HEADER = 'header'
    FOOTER = 'footer'
    HEADING = 'heading'
    ENTER = 'enter'
    EXIT = 'exit'

    def __init__(self, *, timestamp=big_time.timestamp_human):
        super().__init__()
        self.timestamp = timestamp
        self.reset()

    def reset(self):
        super().reset()
        self.depth = 0
        self.events = []
        self.longest_message = 0

    def _event(self, type, elapsed, thread, message):
        events = self.events
        if events:
            previous = events[-1]
            previous[3] = elapsed - previous[2]
        events.append([type, thread, elapsed, 0, self.depth, message])
        self.longest_message = max(self.longest_message, len(message))

    def write(self, elapsed, thread, message):
        self._event(self.WRITE, elapsed, thread, message)

    def log(self, elapsed, thread, message, *, flush=False):
        self._event(self.LOG, elapsed, thread, message)

    def header(self, elapsed, thread, message, separator):
        self._event(self.HEADER, elapsed, thread, message)

    def footer(self, elapsed, thread, message, separator):
        self._event(self.FOOTER, elapsed, thread, message)

    def heading(self, elapsed, thread, message, separator):
        self._event(self.HEADING, elapsed, thread, message)

    def enter(self, elapsed, thread, message):
        self._event(self.ENTER, elapsed, thread, message)
        self.depth += 1

    def exit(self, elapsed, thread):
        self.depth -= 1
        self._event(self.EXIT, elapsed, thread, '')

    def __iter__(self):
        for e in self.events:
            yield tuple(e)

    def print(self, *,
            prefix='[{elapsed:>014.10f} {thread.name:>12} {duration:>014.10f}] {indent}',
            format='{message}',
            heading='{separator}\n{message}\n{separator}',
            enter='',
            exit='',
            print=None,
            indent=2,
            width=None,
            separator='-',
            ):
        if not print:
            print = builtins.print

        if width is None:
            width = self.longest_message

        formats = {
            self.WRITE: format,
            self.LOG: format,
            self.HEADER: heading or format,
            self.FOOTER: heading or format,
            self.HEADING: heading or format,
            self.ENTER: enter or heading or format,
            self.EXIT: exit or heading or format,
        }

        for type, thread, elapsed, duration, depth, message in self.events:
            elapsed /= 1_000_000_000.0
            duration /= 1_000_000_000.0
            epoch = elapsed + self.owner._start_time_epoch
            timestamp = self.timestamp(epoch)
            indent_str = ' ' * (depth * indent)
            separator_str = (separator * ((width // len(separator)) + 1))[:width] if separator else ''

            fmt = formats[type]

            fields = {
                'elapsed': elapsed,
                'duration': duration,
                'timestamp': timestamp,
                'thread': thread,
                'message': message,
                'type': type,
                'depth': depth,
                'indent': indent_str,
                'separator': separator_str,
            }
            rendered = fmt.format_map(fields)
            prefix_str = prefix.format_map(fields)
            for line in rendered.split('\n'):
                print(prefix_str + line)


_spaces = " " * 1024

_sep = " "
_end = "\n"

def prefix_format(time_seconds_width, time_fractional_width, thread_name_width=8):
    # 1 for the dot
    time_width = time_seconds_width + 1 + time_fractional_width
    return f'[{{elapsed:0{time_width}.{time_fractional_width}f}} :: {{thread.name:{thread_name_width}}}] '


tmpfile = "{tmpfile}"
export_name("tmpfile")

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
            banner_separator='=',
            footer='{name} finish at {timestamp}\n',
            header='{name} start at {timestamp}',
            indent=4,
            name='Log',
            prefix=prefix_format(3, 10, 8),
            separator='-',
            threading=True,
            timestamp=big_time.timestamp_human,
            timestamp_clock=time.time,
            width=79,
            ):

        self._clock = clock
        self._timestamp_clock = timestamp_clock

        atexit.register(self._atexit)

        t1 = clock()
        start_time_epoch = timestamp_clock()
        t2 = clock()
        start_time_ns = (t1 + t2) // 2

        array = []
        append = array.append

        self._name = name
        self._header = header
        self._footer = footer
        self._banner_separator = banner_separator
        self._separator = separator

        self._width = width
        self._prefix = prefix
        self._nesting = 0
        self._indent = indent
        self._spaces = ''
        self._timestamp = timestamp

        tmpfile = f"{name}.{timestamp(start_time_epoch).replace("/", "-").replace(":", "-").replace(" ", ".")}.{os.getpid()}.txt"
        tmpfile = big_file.translate_filename_to_exfat(tmpfile)
        tmpfile = tmpfile.replace(" ", '_')
        self._tmpfile = tmpfile = Path(tempfile.gettempdir()) / tmpfile

        self._destinations = array

        self._threading = threading
        self._queue = None
        self._thread = None
        self._closed = True

        # if threading is True, _lock is only used for close and reset
        self._lock = Lock()
        self._blocker = blocker = Lock()
        blocker.acquire()

        self._reset(start_time_ns, start_time_epoch, None)

        print = builtins.print
        if not destinations:
            destinations = [print]

        thread = current_thread()

        for destination in destinations:
            if destination is None:
                continue

            if isinstance(destination, Log):
                append((destination, True))
                continue

            if isinstance(destination, (Destination, Log)):
                pass
            elif destination == print:
                destination = Print()
            elif destination == "{tmpfile}":
                destination = File(self._tmpfile)
            elif isinstance(destination, str):
                destination = File(Path(self._format(0, thread, destination)))
            elif isinstance(destination, Path):
                destination = File(destination)
            elif isinstance(destination, list):
                destination = List(destination)
            elif isinstance(destination, TextIOBase):
                destination = FileHandle(destination)
            elif callable(destination):
                destination = Callable(destination)
            else:
                raise ValueError(f"don't know how to use destination {destination!r}")

            append((destination, False))
            destination.register(self)

    def _atexit(self):
        self.close()

    def _elapsed(self, t):
        # t should be a value returned by _clock.
        # returns t converted to elapsed time
        # since self.start_time_ns, as integer nanoseconds.
        return t - self._start_time_ns

    def _ns_to_float(self, ns):
        return ns / 1_000_000_000.0

    def _reset_worker(self, start_time_ns, start_time_epoch):
        self._nesting = 0
        self._spaces = ''
        self._closed = False
        self._start_time_epoch = start_time_epoch
        self._start_time_ns = start_time_ns
        self._want_header = bool(self._header)

    def _reset(self, start_time_ns, start_time_epoch, signal):
        # if we're not closed, flush before we reset
        if not self._closed:
            self._flush()

        self._reset_worker(start_time_ns, start_time_epoch)

        for destination, is_log in self._destinations:
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
                args = [start_time_ns, start_time_epoch, blocker.release]

                work = [(self._reset, args)]
                self._queue.put(work)

                blocker.acquire()

                return

            self._reset(start_time_ns, start_time_epoch, None)

    def _format(self, elapsed, thread, format):
        if not format:
            return ''

        elapsed = self._ns_to_float(elapsed)
        epoch = elapsed + self._start_time_epoch
        timestamp = self._timestamp(epoch)
        start_timestamp = self._timestamp(self._start_time_epoch)
        return format.format(
            elapsed=elapsed,
            name=self._name,
            start_timestamp=start_timestamp,
            thread=thread,
            time=epoch,
            timestamp=timestamp,
            ) + self._spaces

    def _line(self, prefix, separator):
        line = prefix

        if not separator:
            separator = self._separator or ''
        if separator:
            length = len(separator)
            separator = separator * ((self._width + length) // length)
            line = line + separator
        return line[:self._width] + '\n'

    def _print_banner(self, name, time, thread, format, newlines):
        elapsed = self._elapsed(time)
        prefix = self._format(elapsed, thread, self._prefix)
        message = self._format(elapsed, thread, format)

        separator = self._banner_separator or self._separator
        separator_line = self._line(prefix, separator)
        formatted = separator_line + prefix + message + '\n' + separator_line + newlines

        for destination, is_log in self._destinations:
            if is_log:
                continue

            handler = getattr(destination, name, None)
            if handler:
                handler(elapsed, thread, message, separator)
                continue
            destination.write(elapsed, thread, formatted)

    def _print_header(self, thread):
        self._want_header = False
        self._print_banner('header', self._start_time_ns, thread, self._header, '')

    def _print_footer(self, time, thread):
        footer = self._footer
        stripped = footer.rstrip('\n')
        newlines = footer[len(stripped):]
        self._print_banner('footer', time, thread, stripped, newlines)


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


    def _log(self, time, thread, args, sep, end, flush):
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

        if self._want_header:
            self._print_header(thread)

        message = f"{sep.join(args)}{end}"

        messages = message.split('\n')
        if (len(messages) > 1) and (not messages[-1]):
            messages.pop()

        elapsed = self._elapsed(time)
        prefix = self._format(elapsed, thread, self._prefix)
        formatted = prefix + f"\n{prefix}".join(messages) + "\n"

        messages_and_flush = [[message, False] for message in messages]
        messages_and_flush[-1][-1] = flush

        for destination, is_log in self._destinations:
            if is_log:
                destination.log(*args, sep=sep, end=end, flush=flush)
                continue

            log = getattr(destination, 'log', None)
            if log:
                for message, _flush in messages_and_flush:
                    log(elapsed, thread, message, flush=_flush)
                continue

            destination.write(elapsed, thread, formatted)
            if flush:
                destination.flush()


    def __call__(self, *args, sep=_sep, end=_end, flush=False):
        "Alias for Log.log()."

        time = self._clock()
        thread = current_thread()

        if end is not _end:
            end = str(end)
        if sep is not _sep:
            sep = str(sep)
        args = [str(a) for a in args]

        self._dispatch( [(self._log, (time, thread, args, sep, end, flush))] )

    def log(self, *args, end=_end, sep=_sep, flush=False):
        """
        Logs a message, with the interface of builtins.print.
        """
        return self(*args, end=end, sep=sep, flush=flush)


    def _write(self, time, thread, s):
        if self._want_header:
            self._print_header(thread)

        elapsed = self._elapsed(time)

        for destination, is_log in self._destinations:
            if is_log:
                destination.write(s)
                continue
            destination.write(elapsed, thread, s)

    def write(self, s):
        time = self._clock()
        thread = current_thread()

        if not isinstance(s, str):
            raise TypeError('s must be str')

        self._dispatch( [(self._write, (time, thread, s))] )

    def _heading(self, time, thread, message, separator):
        if self._want_header:
            self._print_header(thread)

        elapsed = self._elapsed(time)
        prefix = self._format(elapsed, thread, self._prefix)

        separator = self._line(prefix, separator)
        formatted = separator + prefix + message + '\n' + separator

        for destination, is_log in self._destinations:
            if is_log:
                destination.heading(message, separator=separator)
                continue

            heading = getattr(destination, 'heading', None)
            if heading:
                heading(elapsed, thread, message, separator)
                continue
            destination.write(elapsed, thread, formatted)

    def heading(self, message, separator=None):
        time = self._clock()
        thread = current_thread()

        if not isinstance(message, str):
            raise TypeError('message must be str')

        self._dispatch( [(self._heading, (time, thread, message, separator))] )


    class SubsystemContextManager:
        def __init__(self, log):
            self.log = log

        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_value, traceback):
            if self.log:
                self.log.exit()

    def _set_nesting(self, nesting):
        self._nesting = nesting
        self._spaces = _spaces[:self._nesting * self._indent]

    def _enter(self, time, thread, message, separator):
        if self._want_header:
            self._print_header(thread)

        elapsed = self._elapsed(time)
        prefix = self._format(elapsed, thread, self._prefix)

        separator = self._line(prefix, separator)
        formatted = separator + prefix + message + '\n' + separator

        for destination, is_log in self._destinations:
            if is_log:
                destination.enter(message)
                continue

            enter = getattr(destination, 'enter', None)
            if enter:
                enter(elapsed, thread, message)
                continue
            destination.write(elapsed, thread, formatted)

        self._set_nesting(self._nesting + 1)

    def enter(self, message, *, separator=None):
        time = self._clock()
        thread = current_thread()
        log = None

        work = [(self._enter, (time, thread, message, separator))]

        if self._threading:
            if not self._closed:
                self._queue.put(work)
                log = self
        else:
            with self._lock:
                if not self._closed:
                    self._execute(work)
                    log = self

        return self.SubsystemContextManager(log)


    def _exit(self, time, thread, separator):
        assert not self._want_header

        if not self._nesting:
            return

        self._set_nesting(self._nesting - 1)

        elapsed = self._elapsed(time)
        prefix = self._format(elapsed, thread, self._prefix)
        separator = self._line(prefix, separator)

        for destination, is_log in self._destinations:
            if is_log:
                destination.exit()
                continue

            exit = getattr(destination, 'exit', None)
            if exit:
                exit(elapsed, thread)
                continue
            destination.write(elapsed, thread, separator)

    def exit(self, *, separator=None):
        time = self._clock()
        thread = current_thread()
        self._dispatch( [(self._exit, (time, thread, separator))] )


    def _flush(self):
        for destination, is_log in self._destinations:
            if is_log:
                destination.flush()
                continue

            destination.flush()

    def flush(self):
        self._dispatch( [(self._flush, ())] )

    @property
    def tmpfile(self):
        return self._tmpfile

    @property
    def closed(self):
        with self._lock:
            return self._closed

    def _close(self):
        for destination, is_log in self._destinations:
            destination.close()

    def close(self):
        time = self._clock()
        thread = current_thread()

        with self._lock:
            if self._closed:
                return

            self._closed = True

            work = []
            append = work.append

            if self._footer:
                append((self._set_nesting, (0,)))
                append((self._print_footer, (time, thread)))
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


@export
class OldDestination(Destination):
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

    def write(self, elapsed, thread, message):
        self._event(elapsed, message.rstrip('\n'))

    def log(self, elapsed, thread, message, *, flush=False):
        self._event(elapsed, message.rstrip('\n'))

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
        self._log = Log(self._destination, threading=False, header='', footer='', prefix='', clock=clock)

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

