#!/usr/bin/env python3

_license = """
big
Copyright 2022-2025 Larry Hastings
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
from big.time import timestamp_human
import builtins
from functools import partial
from io import TextIOBase
from pathlib import Path
from queue import Queue
from threading import current_thread, Lock, Thread
from time import perf_counter, time


try:
    # new in 3.7
    from time import monotonic_ns as _default_clock
except ImportError: # pragma: no cover
    from time import perf_counter
    def _default_clock():
        return int(perf_counter() * 1_000_000_000.0)


__all__ = []

def export(o):
    __all__.append(o.__name__)
    return o


@export
class Logger:
    def __init__(self):
        self.owner = None
        self.register(0, None, None)

    def register(self, time, thread, owner):
        if self.owner is not None:
            raise RuntimeError(f"can't register owner {owner}, already registered with {self.owner}")

        self.owner = owner
        self.start = time

    def write(self, time, thread, s):
        raise RuntimeError("virtual write method called on", self)

    def flush(self, time, thread):
        pass

    def close(self, time, thread):
        pass

    def reset(self, time, thread):
        self.start = time

    if 0:

        def log(self, time, thread, s, *, flush=False):
            pass

        def heading(self, time, thread, s, marker):
            pass

        def enter(self, time, thread, s):
            pass

        def exit(self, time, thread, s):
            pass


@export
class Wrapper(Logger):
    def __init__(self, callable):
        super().__init__()
        self.callable = callable

    def write(self, time, thread, s):
        self.callable(s)



@export
class Print(Logger):
    def __init__(self):
        super().__init__()
        self.print = builtins.print

    def write(self, time, thread, s):
        self.print(s, end='', flush=True)




@export
class List(Logger):
    def __init__(self, list):
        super().__init__()
        self.array = list


    def write(self, time, thread, s):
        self.array.append(s)



@export
class Buffer(Logger):
    def __init__(self):
        super().__init__()
        self.array = []

    def write(self, time, thread, s):
        self.array.append(s)

    def flush(self, time, thread):
        if self.array:
            contents = "".join(self.array)
            self.array.clear()
            print(contents, end='')


@export
class File(Logger):
    def __init__(self, path, mode="at", *, flush=False):
        super().__init__()

        assert mode in ("at", "wt", "xt", "a", "w", "x")

        self.array = array = []
        self.path = Path(path)
        self.mode = mode
        self.immediate = flush

        self.reset(0, None)

    def reset(self, time, thread):
        super().reset(time, thread)
        self.f = self.path.open(self.mode) if self.immediate else None

    def write(self, time, thread, s):
        if self.immediate:
            self.f.write(s)
            self.f.flush()
        else:
            self.array.append(s)

    def flush(self, time, thread):
        if self.array:
            assert not self.immediate
            assert not self.f
            contents = "".join(self.array)
            self.array.clear()
            with self.path.open(self.mode) as f:
                f.write(contents)
            self.mode = "at"

    def close(self, time, thread):
        assert not self.array

        if self.f:
            f = self.f
            self.f = None
            f.close()
            self.mode = "at"


@export
class FileHandle(Logger):
    def __init__(self, handle, *, flush=False):
        super().__init__()
        self.handle = handle
        self.immediate = flush

    def write(self, time, thread, s):
        self.handle.write(s)
        if self.immediate:
            self.handle.flush()

    def flush(self, time, thread):
        if self.handle:
            self.handle.flush()

    def close(self, time, thread):
        if self.handle:
            self.handle = None

@export
class Sink(Logger):
    """
    A Logger that accumulates events for later iteration or printing.
    Events include thread information and raw timestamps.
    """

    EVENT = 'event'
    HEADING = 'heading'
    ENTER = 'enter'
    EXIT = 'exit'

    def __init__(self):
        super().__init__()
        self.reset(0, None)

    def register(self, time, thread, owner):
        super().register(time, thread, owner)
        self.reset(time, thread)

    def reset(self, time, thread):
        super().reset(time, thread)
        self.depth = 0
        self.events = []
        self.longest_event = 0

    def _event(self, time, thread, event_type, event):
        events = self.events
        start = self.owner._elapsed(time)
        if events:
            previous = events[-1]
            previous[1] = start - previous[0]
        events.append([start, 0, thread, event_type, event, self.depth])
        self.longest_event = max(self.longest_event, len(event))

    def write(self, time, thread, s):
        self._event(time, thread, self.EVENT, s.rstrip('\n'))

    def log(self, time, thread, s, *, flush=False):
        self._event(time, thread, self.EVENT, s.rstrip('\n'))

    def heading(self, time, thread, s, marker):
        self._event(time, thread, self.HEADING, s)

    def enter(self, time, thread, s):
        self._event(time, thread, self.ENTER, s)
        self.depth += 1

    def exit(self, time, thread):
        self.depth -= 1
        self._event(time, thread, self.EXIT, '')

    def __iter__(self):
        return iter(self.events)

    def print(self, *,
            prefix='[{start:12.9f}  {elapsed:12.9f}  {thread.name:12}]  {indent}',
            format='{event}',
            heading='{separator}\n{event}\n{separator}',
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
            width = self.longest_event

        formats = {
            self.EVENT: format,
            self.HEADING: heading or format,
            self.ENTER: enter or heading or format,
            self.EXIT: exit or heading or format,
        }

        for start, elapsed, thread, event_type, event, depth in self.events:
            epoch = start + self.owner._start_time_epoch
            timestamp = timestamp_human(epoch, want_microseconds=False)
            indent_str = ' ' * (depth * indent)
            separator_str = (separator * ((width // len(separator)) + 1))[:width] if separator else ''

            fmt = formats[event_type]

            fields = {
                'start': start,
                'elapsed': elapsed,
                'timestamp': timestamp,
                'thread': thread,
                'event': event,
                'type': event_type,
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
    return f'[{{elapsed:0{time_width}.0{time_fractional_width}f}} :: {{thread.name:{thread_name_width}}}] '


@export
class Log(Logger):

    def __init__(self, *loggers,
            threading=True,
            name='Log',
            start='{name} start at {timestamp}',
            prefix=prefix_format(3, 10, 8),
            finish='{name} finish at {timestamp}\n',
            delimiter='=',
            separator='-',
            indent=4,
            width=79,
            clock=None,
            ):

        if clock is None:
            clock = _default_clock
        self._clock = clock

        atexit.register(self._atexit)

        t1 = clock()
        start_time_epoch = time()
        t2 = clock()
        start_time_ns = (t1 + t2) // 2

        array = []
        append = array.append

        self._name = name
        self._start = start
        self._finish = finish
        self._delimiter = delimiter
        self._separator = separator

        self._width = width
        self._prefix = prefix
        self._nesting = 0
        self._indent = indent
        self._spaces = ''

        self._loggers = array

        self._queue = None

        self._threading = threading
        self._thread = None
        self._closed = True

        # if threading is True, _lock is only used for close and reset
        self._lock = Lock()

        thread = current_thread()
        self._reset_worker(start_time_ns, start_time_epoch, thread)
        self._reset(start_time_ns, start_time_epoch, thread)

        print = builtins.print
        if not loggers:
            loggers = [print]

        for logger in loggers:
            if logger is None:
                continue

            if isinstance(logger, Log):
                append((logger, True))
                continue

            if isinstance(logger, Logger):
                pass
            elif logger == print:
                logger = Print()
            elif isinstance(logger, str):
                logger = File(Path(logger))
            elif isinstance(logger, Path):
                logger = File(logger)
            elif isinstance(logger, list):
                logger = List(logger)
            elif isinstance(logger, TextIOBase):
                logger = FileHandle(logger)
            elif callable(logger):
                logger = Wrapper(logger)
            else:
                raise ValueError(f"don't know how to log to logger {logger!r}")

            append((logger, False))
            logger.register(start_time_ns, thread, self)

    def _atexit(self):
        self.close()

    def _elapsed(self, t):
        # t should be the current time reported by _clock.
        # returns elapsed time since start_time_ns, as float seconds.
        return (t - self._start_time_ns) / 1_000_000_000.0

    def _reset_worker(self, start_time_ns, start_time_epoch, thread):
        self._nesting = 0
        self._spaces = ''
        self._closed = False
        self._start_time_epoch = start_time_epoch
        self._start_time_ns = start_time_ns
        self._reset_thread = thread
        self._print_header = True

    def _reset_job(self, start_time_ns, start_time_epoch, thread, signal):
        self._reset_worker(start_time_ns, start_time_epoch, thread)

        for logger, is_log in self._loggers:
            if is_log:
                logger.reset()
                continue
            logger.reset(start_time_ns, thread)

        if self._threading and (self._thread is None):
            self._queue = Queue()
            self._thread = Thread(target=self._worker_thread, args=(self._queue,), daemon=True)
            self._thread.start()

        if signal:
            signal()

    def _reset(self, start_time_ns, start_time_epoch, thread):
        with self._lock:
            args = [start_time_ns, start_time_epoch, thread, None]

            if self._threading and (self._thread is not None):
                blocker = Lock()
                blocker.acquire()
                args[-1] = blocker.release

                work = [(self._reset_job, args)]
                self._queue.put(work)

                blocker.acquire()

                return

            self._reset_job(*args)

    def reset(self):
        clock = self._clock
        t1 = clock()
        start_time_epoch = time()
        t2 = clock()
        start_time_ns = (t1 + t2) // 2
        thread = current_thread()
        self._reset(start_time_ns, start_time_epoch, thread)

    def _format(self, time, thread, format):
        if not format:
            return ''

        elapsed = self._elapsed(time)
        epoch = elapsed + self._start_time_epoch
        timestamp = timestamp_human(epoch, want_microseconds=False)
        return format.format(
            timestamp=timestamp,
            elapsed=elapsed,
            thread=thread,
            time=time,
            name=self._name,
            ) + self._spaces

    def _line(self, prefix, marker):
        line = prefix

        if not marker:
            marker = self._separator or ''
        if marker:
            length = len(marker)
            marker = marker * ((self._width + length) // length)
            line = line + marker
        return line[:self._width] + '\n'

    def _header(self):
        self._print_header = False

        if self._start:
            start = self._format(self._start_time_ns, self._reset_thread, self._start)
            self._heading(self._start_time_ns, self._reset_thread, start, self._delimiter)


    def _log(self, time, thread, args, sep, end, flush):
        if self._print_header: self._header()

        s = f"{sep.join(args)}{end}"

        prefix = self._format(time, thread, self._prefix)
        formatted = f"{prefix}{s}"

        for logger, is_log in self._loggers:
            if is_log:
                logger.log(*args, sep=sep, end=end, flush=flush)
                continue

            log = getattr(logger, 'log', None)
            if log:
                log(time, thread, s, flush=flush)
                continue

            logger.write(time, thread, formatted)
            if flush:
                logger.flush(time, thread)


    def __call__(self, *args, sep=_sep, end=_end, flush=False):
        time = self._clock()
        thread = current_thread()

        if self._closed:
            raise RuntimeError("Log is closed")

        if end is not _end:
            end = str(end)
        if sep is not _sep:
            sep = str(sep)
        args = [str(a) for a in args]


        if self._threading:
            work = [(self._log, (time, thread, args, sep, end, flush))]
            self._queue.put(work)
            return

        with self._lock:
            self._log(time, thread, args, sep, end, flush)

    def log(self, *args, end=_end, sep=_sep, flush=False):
        return self(*args, end=end, sep=sep, flush=flush)


    def _dispatch_s(self, time, s, method):
        thread = current_thread()

        if not isinstance(s, str):
            raise TypeError('s must be str')
        if self._closed:
            raise RuntimeError("Log is closed")

        work = [(method, (time, thread, s))]

        if self._threading:
            self._queue.put(work)
            return

        with self._lock:
            fn, args = work[0]
            fn(*args)


    def _write(self, time, thread, s):
        if self._print_header: self._header()

        for logger, is_log in self._loggers:
            if is_log:
                logger.write(s)
                continue
            logger.write(time, thread, s)

    def write(self, s):
        time = self._clock()
        self._dispatch_s(time, s, self._write)


    def _heading(self, time, thread, s, marker):
        if self._print_header: self._header()

        prefix = self._format(time, thread, self._prefix)

        separator = self._line(prefix, marker)
        formatted = separator + prefix + s + '\n' + separator

        for logger, is_log in self._loggers:
            if is_log:
                logger.heading(s, marker=marker)
                continue

            heading = getattr(logger, 'heading', None)
            if heading:
                heading(time, thread, s, marker)
                continue
            logger.write(time, thread, formatted)

    def heading(self, s, marker=None):
        time = self._clock()
        thread = current_thread()

        if not isinstance(s, str):
            raise TypeError('s must be str')
        if self._closed:
            raise RuntimeError("Log is closed")

        work = [(self._heading, (time, thread, s, marker))]

        if self._threading:
            self._queue.put(work)
            return

        with self._lock:
            fn, args = work[0]
            fn(*args)


    class SubsystemContextManager:
        def __init__(self, log):
            self.log = log

        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_value, traceback):
            self.log.exit()

    def _enter(self, time, thread, s):
        if self._print_header: self._header()

        prefix = self._format(time, thread, self._prefix)

        separator = self._line(prefix, self._separator)
        formatted = separator + prefix + s + '\n' + separator

        for logger, is_log in self._loggers:
            if is_log:
                logger.enter(s)
                continue

            enter = getattr(logger, 'enter', None)
            if enter:
                enter(time, thread, s)
                continue
            logger.write(time, thread, formatted)

        self._nesting += 1
        self._spaces = _spaces[:self._nesting * self._indent]

    def enter(self, s):
        time = self._clock()
        self._dispatch_s(time, s, self._enter)
        return self.SubsystemContextManager(self)

    def _dispatch_0(self, time, thread, method):
        if self._closed:
            raise RuntimeError("Log is closed")

        if self._threading:
            work = [(method, (time, thread))]
            self._queue.put(work)
            return

        with self._lock:
            method(time, thread)


    def _exit(self, time, thread):
        if self._nesting < 1:
            raise RuntimeError('unbalanced enter/exit calls')

        self._nesting -= 1
        self._spaces = _spaces[:self._nesting * self._indent]

        prefix = self._format(time, thread, self._prefix)
        separator = self._line(prefix, self._separator)

        for logger, is_log in self._loggers:
            if is_log:
                logger.exit()
                continue

            exit = getattr(logger, 'exit', None)
            if exit:
                exit(time, thread)
                continue
            logger.write(time, thread, separator)

    def exit(self):
        time = self._clock()
        thread = current_thread()
        self._dispatch_0(time, thread, self._exit)


    def _flush(self, time, thread):
        for logger, is_log in self._loggers:
            if is_log:
                logger.flush()
                continue

            logger.flush(time, thread)

    def flush(self):
        time = self._clock()
        thread = current_thread()
        self._dispatch_0(time, thread, self._flush)


    def _close(self, time, thread):
        for logger, is_log in self._loggers:
            if is_log:
                logger.close()
                continue

            logger.close(time, thread)

    def closed(self):
        with self._lock:
            return self._closed

    def close(self):
        time = self._clock()
        thread = current_thread()

        with self._lock:
            if self._closed:
                return

            self._closed = True

            work = []
            append = work.append

            if self._finish:
                finish = self._format(time, thread, self._finish)
                stripped = finish.rstrip('\n')
                newlines = finish[len(stripped):]

                append((self._heading, (time, thread, stripped, self._delimiter)))
                if newlines:
                    append((self._write, (time, thread, newlines)))

            append((self._flush, (time, thread)))
            append((self._close, (time, thread)))
            append(None)

            if self._threading:
                assert self._thread is not None
                self._queue.put(work)
                self._thread.join()
                self._thread = None
                return

            for job in work:
                if job is None:
                    break
                fn, args = job
                fn(*args)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.flush()

    def _worker_thread(self, q):
        get = q.get

        while True:
            work = get()
            for job in work:
                if job is None:
                    return
                fn, args = job
                fn(*args)


@export
class OldLogger(Logger):
    """
    A Logger providing backwards compatibility with the old big.log.Log interface.
    Accumulates events for later iteration or printing.
    """

    def __init__(self):
        super().__init__()
        self.longest_event = 0
        self.reset(0, None)

    def reset(self, time, thread):
        super().reset(time, thread)
        self.stack = []
        self.events = []
        self._event(time, 'log start')

    def _event(self, time, event):
        t = time - self.start
        events = self.events
        if events:
            previous = events[-1]
            previous[1] = t - previous[0]
        events.append([t, 0, event, len(self.stack)])
        self.longest_event = max(self.longest_event, len(event))

    def write(self, time, thread, s):
        self._event(time, s.rstrip('\n'))

    def log(self, time, thread, s, *, flush=False):
        self._event(time, s.rstrip('\n'))

    def enter(self, time, thread, s):
        self._event(time, s + " start")
        self.stack.append(s)

    def exit(self, time, thread):
        subsystem = self.stack.pop()
        self._event(time, subsystem + " end")

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
    Creates a Log with an OldLogger and exposes the old interface.
    """

    def __init__(self, clock=None):
        self._logger = OldLogger()
        self._log = Log(self._logger, threading=False, start='', finish='', prefix='', clock=clock)

    def reset(self):
        self._log.reset()

    def __call__(self, event):
        self._log(event)

    def enter(self, subsystem):
        self._log.enter(subsystem)

    def exit(self):
        self._log.exit()

    def __iter__(self):
        return iter(self._logger)

    def print(self, *, print=None, title="[event log]", headings=True, indent=2, seconds_width=2, fractional_width=9):
        self._logger.print(print=print, title=title, headings=headings, indent=indent, seconds_width=seconds_width, fractional_width=fractional_width)

