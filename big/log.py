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
import io
import os
import pathlib
import queue
import sys
import tempfile
import threading
import time
import types

from . import template as big_template

from .builtin import ModuleManager
from .file import translate_filename_to_exfat
from .time import timestamp_human
from .types import linked_list


mm = ModuleManager()
export = mm.export

try:
    # 3.7+
    from time import monotonic_ns as default_clock
except ImportError: # pragma: no cover
    # 3.6 compatibility
    from time import monotonic
    def default_clock():
        return int(monotonic() * 1_000_000_000.0)


Queue = getattr(queue, "SimpleQueue", queue.Queue)


class FormatterTypeError(TypeError):
    pass

class FormatterValueError(ValueError):
    pass


@export
class LogEvent(tuple):
    """
    Abstract base class for Log events sent to a Formatter.
    """

    __slots__ = ()

    def __repr__(self):
        fields = []
        for name in self._field_names:
            value = getattr(self, name)
            fields.append(f"{name}={value!r}")
        return f"{self.__class__.__name__}({', '.join(fields)})"

    def __lt__(self, other):
        if not isinstance(other, LogEvent):
            raise TypeError(f"'<' not supported between instances of LogEvent and {type(other)}")
        return (
                (self.session  <= other.session)
            and (self.elapsed <  other.elapsed)
            )




@export
class LogStartEvent(LogEvent):

    __slots__ = ()

    _field_names = ('session', 'ns', 'epoch', 'nesting', 'configuration', 'duration')

    def              __new__(cls,  session, ns, epoch, nesting, configuration, duration=0):
        return tuple.__new__(cls, (session, ns, epoch, nesting, configuration, duration))

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
    def nesting(self):
        return self[3]

    @property
    def configuration(self):
        return self[4]

    @property
    def duration(self):
        return self[5]

    @property
    def elapsed(self):
        return 0

    @property
    def depth(self):
        return 0


    def __hash__(self):
        return hash((self.session, self.ns, self.epoch))

    def _calculate_duration(self, next_event):
        return LogStartEvent(
            self.session, self.ns, self.epoch,
            self.nesting, self.configuration,
            next_event.elapsed - self.elapsed,
            )



@export
class LogEndEvent(LogEvent):

    __slots__ = ()

    _field_names = ('session', 'elapsed')

    def              __new__(cls,  session, elapsed):
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
class LogLogEvent(LogEvent):

    __slots__ = ()

    _field_names = ('session', 'elapsed', 'thread', 'format', 'message', 'data', 'depth', 'duration')

    def              __new__(cls,  session, elapsed, thread, format, message, data, depth, duration=0):
        return tuple.__new__(cls, (session, elapsed, thread, format, message, data, depth, duration))

    @property
    def session(self):
        return self[0]

    @property
    def elapsed(self):
        return self[1]

    @property
    def thread(self):
        return self[2]

    @property
    def format(self):
        return self[3]

    @property
    def message(self):
        return self[4]

    @property
    def data(self):
        return self[5]

    @property
    def depth(self):
        return self[6]

    @property
    def duration(self):
        return self[7]

    def _calculate_duration(self, next_event):
        return LogLogEvent(
            self.session, self.elapsed, self.thread,
            self.format, self.message, self.data, self.depth,
            next_event.elapsed - self.elapsed,
            )


@export
class LogEnterEvent(LogEvent):

    __slots__ = ()

    _field_names = ('session', 'elapsed', 'thread', 'format', 'message', 'depth', 'duration')

    def              __new__(cls,  session, elapsed, thread, format, message, depth, duration=0):
        return tuple.__new__(cls, (session, elapsed, thread, format, message, depth, duration))

    @property
    def session(self):
        return self[0]

    @property
    def elapsed(self):
        return self[1]

    @property
    def thread(self):
        return self[2]

    @property
    def format(self):
        return self[3]

    @property
    def message(self):
        return self[4]

    @property
    def depth(self):
        return self[5]

    @property
    def duration(self):
        return self[6]

    def _calculate_duration(self, next_event):
        return LogEnterEvent(
            self.session, self.elapsed, self.thread,
            self.format, self.message, self.depth,
            next_event.elapsed - self.elapsed,
            )



@export
class LogExitEvent(LogEvent):

    __slots__ = ()

    _field_names = ('session', 'elapsed', 'thread', 'format', 'context', 'depth', 'duration')

    def              __new__(cls,  session, elapsed, thread, format, context, depth, duration=0):
        return tuple.__new__(cls, (session, elapsed, thread, format, context, depth, duration))

    @property
    def session(self):
        return self[0]

    @property
    def elapsed(self):
        return self[1]

    @property
    def thread(self):
        return self[2]

    @property
    def format(self):
        return self[3]

    @property
    def context(self):
        return self[4]

    @property
    def depth(self):
        return self[5]

    @property
    def duration(self):
        return self[6]

    def _calculate_duration(self, next_event):
        return LogExitEvent(
            self.session, self.elapsed, self.thread,
            self.format, self.context, self.depth,
            next_event.elapsed - self.elapsed,
            )



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



@export
class EnterContext(tuple):
    """
    """

    __slots__ = ()

    def __new__(cls, elapsed, thread, format, message):
        t = (elapsed, thread, format, message)
        return tuple.__new__(cls, t)

    def __repr__(self):
        fields = []
        for name in ("elapsed", "thread", "format", "message"):
            value = getattr(self, name)
            fields.append(f"{name}={value!r}")
        return f"EnterContext({', '.join(fields)})"

    def __lt__(self, other):
        if not isinstance(other, EnterContext):
            raise TypeError(f"'<' not supported between instances of EnterContext and {type(other)}")
        return self.elapsed < other.elapsed

    @property
    def elapsed(self):
        return self[0]

    @property
    def thread(self):
        return self[1]

    @property
    def format(self):
        return self[2]

    @property
    def message(self):
        return self[3]



@export
class Scheduler:
    def __init__(self, log, *, atexit=False, drain=False, first=False, wait=False):
        """
        * atexit - sets wait=True, and in threaded mode
            also schedules a None so the worker thread will exit
        * drain - if true, and in in non-threaded mode, flush the work queue
        * first - if true, insert these jobs on the front of the work queue,
            default is to add them to the end
        * wait - wait until all this scheduled work is completed
            * in non-threaded mode, this is the same as drain
            * in threaded mode, this blocks until the worker thread
              processes every job queued by the scheduler
        """
        self.log = log
        self.jobs = []
        self.atexit = atexit
        self.first = first

        wait = wait or atexit
        threaded = log._threaded
        self.block = wait and threaded
        self.drain = (drain or wait) and (not threaded)

        assert not (self.block and self.drain)

    def __bool__(self):
        return bool(self.jobs)

    def __call__(self, method=None, *args):
        if method is None:
            jobs = self.jobs
            locker = None
            threaded = self.log._threaded

            if self.block:
                locker = threading.Lock()
                locker.acquire()
                jobs.append(((locker,), locker.release, ()))

            if self.atexit:
                jobs.append(((), None, (locker.release,)))

            if jobs:
                self.log._schedule(jobs, first=self.first)
                self.jobs = jobs = []

            if self.block:
                locker.acquire()

            if self.drain:
                self.log._drain()

            return

        involved = []

        if isinstance(method, types.MethodType):
            method_self = method.__self__
            if isinstance(method_self, (Destination, Formatter)):
                involved.append(method_self)
        else:
            method_self = None

        for a in args:
            if isinstance(a, (Destination, Formatter)):
                assert a not in involved
                involved.append(a)

        t = (involved, method, args)
        # print(t)
        self.jobs.append(t)



@export
class Formatter:
    """
    format must have the signature:
        format(elapsed, thread, format, message, data, *, nesting=None)
    Pass in None if you've subclassed Formatter, and you've defined
    a "format" method on the subclass, and you want to use that.
    """
    # destinations                        # list of Destinations
    # supported_formats                   # frozenset, or True = accepts any
    # output_type                         # type (str, bytes, SinkEvent, etc.)

    def __init__(self, format, *, name=None):
        self.root = self.owner = None
        self.started = False

        self.destinations = []

        if name is None:
            name = type(self).__name__
        self.name = name

        # every destination appears in either dormant or active.
        #     invariant: dormant | active == set(destinations)
        # (Once the implementation settles down, maybe we can
        # remove one of these.)
        self.dormant = set()
        self.active = set()
        self.dirty = set()

        self.start_time_ns = None
        self.start_time_epoch = None

        if not callable(format):
            raise ValueError('format must be callable')
        self.format = format

        self._scheduler = None


    def append(self, destination):
        if self.root:
            destination.register(self.root, self.owner)
        self.destinations.append(destination)
        self.dormant.add(destination)

    def _dirty_add(self, destination):
        self.dirty.add(destination)

    def _dirty_clear(self):
        self.dirty.clear()

    def _dirty_discard(self, destination):
        self.dirty.discard(destination)

    def _mark_dormant(self, destination):
        self.active.remove(destination)
        self.dormant.add(destination)

    def end_destination(self, destination, s):
        """
        Returns True if the destination was active and we transitioned it to dormant.
        Returns False if it was already dormant.

        When this function returns, the destination will be in dormant.

        Second argument 's' should be a Scheduler.
        """
        if destination in self.dormant:
            assert destination not in self.active
            return False
        assert destination in self.active
        if destination in self.dirty:
            s(self._dirty_discard, destination)
            s(destination.flush, False)
        s(destination.end)
        s(self._mark_dormant, destination)
        return True

    def _remove(self, destination, started):
        if started:
            self.dormant.remove(destination)
        self.destinations.remove(destination)

    def remove(self, destination):
        s = self._scheduler()
        self.end_destination(destination, s)
        s(self._remove, destination)
        s(destination.unregister)
        s()

    # def _clear(self):
    #     self.destinations.clear()
    #     self.dormant.clear()
    #     self.active.clear()
    #     self.dirty.clear()

    # def clear(self):
    #     s = self._scheduler()

    #     if self.started:
    #         for d in self.destinations:
    #             self.end_destination(d, s)

    #     if s:
    #         s(self._clear)
    #         s()
    #     else:
    #         self._clear()


    @staticmethod
    def ns_to_float(ns):
        return ns / 1_000_000_000.0

    def register(self, log, owner):
        assert self.root is None
        assert self.owner is None
        assert log is not None
        assert owner is not None
        assert not self.started
        self.root = log
        self.owner = owner
        self._scheduler = log._scheduler

        for d in self.destinations:
            d.register(log, owner)

    def unregister(self):
        assert self.root is not None
        assert self.owner is not None
        assert not self.started
        self.root = self.owner = None
        for d in self.destinations:
            d.unregister()

    def start(self, ns, epoch, nesting):
        assert not self.started
        self.started = True
        self.start_time_ns = ns
        self.start_time_epoch = epoch
        self.nesting = list(nesting)

    def _end(self):
        self.started = False

    def end(self, elapsed):
        assert self.started
        self.flush()
        self.started = False

    def flush(self):
        assert self.started
        if self.dirty:
            s = self._scheduler(first=True)
            for d in self.destinations:
                if d in self.dirty:
                    s(d.flush)
            if s:
                s(self._dirty_clear)
                s()

    def fix(self, exception):
        pass

    def validate(self, format, message, data):
        # used for real-time validation of a requested format
        raise NotImplementedError()

    # def write(self, formatted):
    #     assert self.started
    #     assert formatted

    #     for d in self.destinations:
    #         self.dirty.add(d)

    #         if d in self.dormant:
    #             self.dormant.remove(d)
    #             self.active.add(d)
    #             d.start()

    #         d.write(formatted)

    def write_queued(self, formatted, s):
        assert self.started
        assert formatted

        for d in self.destinations:
            if d in self.dormant:
                self.dormant.remove(d)
                self.active.add(d)
                s(d.start)

            s(d.write, formatted)
            s(self._dirty_add, d)

    def log(self, elapsed, thread, format, message, data):
        formatted = self.format(elapsed, thread, format, message, data, self.nesting)
        s = self._scheduler(first=True)
        if formatted:
            # self.write(formatted)
            self.write_queued(formatted, s)
        s()

    def enter(self, elapsed, thread, format, message):
        pass

    def exit(self, elapsed, thread, format, context):
        pass



@export
class TextFormatter(Formatter):
    # supported_formats = frozenset({...})
    # owns formats dict, prefix, nesting stack, indentation

    @staticmethod
    def prefix_format(time_seconds_width, time_fractional_width, thread_name_width=12, *, indent=True):
        """
        Formats a "prefix" string for use with a Log object.

        The format it returns is in the form:
            "[{elapsed} {thread.name}] "
        formatted with these widths:
             "[{time_seconds_width}.{time_fractional_width} {thread_name_width}]"
        For example, the default value for Log.prefix is prefix_format(3, 10, 12),
        which looks like this in the final log:
            "[003.0706368860   MainThread]"

        If the indent parameter is true (the default), the prefix generated
        is followed by {indent}, which inserts the current indent string.

        (The actual value of "indent" supplied by TextFormatter will be
        the string passed in to its 'indent' parameter, multipled by the
        current "enter" nesting depth.)
        """
        # the +1 is for the dot between seconds and fractional seconds
        time_width = time_seconds_width + 1 + time_fractional_width
        indent = '{indent}' if indent else ''
        return f'{{elapsed:0{time_width}.{time_fractional_width}f}} {{thread.name:>{thread_name_width}}}│ {indent}'

    def __init__(self,
        *,
        formats=None,
        indent='    ',
        prefix=prefix_format(3, 10, 12),
        timestamp_format=timestamp_human,
        width=79,
        ):

        if not isinstance(indent, str):
            raise  TypeError('indent must be a non-empty str')
        if not indent:
            raise ValueError('indent must be a non-empty str')
        if not isinstance(prefix, str):
            raise  TypeError('prefix must be a str')
        if not callable(timestamp_format):
            raise  TypeError('timestamp_format must be callable')
        if not isinstance(width, int):
            raise  TypeError('width must be an int and greater than zero')
        if not (width > 0):
            raise ValueError('width must be an int and greater than zero')
        if formats is None:
            formats = {}
        elif not isinstance(formats, dict):
            raise  TypeError('formats must be a dict')

        super().__init__(self.format)

        self.formats, self.formatters = self.parse_formats(self.base_formats, formats, width)
        self.default_indent = indent
        self.indent = ''
        self.indent_stack = []
        self.prefix = prefix
        self.timestamp_format = timestamp_format

        self.supported_formats = set(self.formats)

    def validate(self, format, message, data):
        if data is not None:
            raise FormatterValueError(f'{type(self).__name__} only supports data=None')

        if isinstance(format, str):
            format_name = format
        elif isinstance(format, dict):
            if not 'format' in format:
                raise FormatterValueError(f"format dict must contain 'format' key")
            format_name = format['format']
            if self.name in format:
                raise FormatterValueError(f"{type(self).__name__} doesn't support configuration in format dict")
        else:
            raise FormatterTypeError(f"format must be str or dict, not {type(format).__name__}")

        if not format_name in self.supported_formats:
            raise FormatterValueError(f"{type(self).__name__} doesn't support {format_name!r} format")



    def start(self, ns, epoch, nesting):
        super().start(ns, epoch, nesting)
        self.indent_stack = []
        for context in nesting:
            format = context.format
            if isinstance(format, str):
                format_name = format
            else:
                format_name = format['format']
            if format_name not in self.formats:
                indent = self.default_indent
            else:
                format = self.formats[format_name]
                assert 'exit' in format
                indent = format.get('indent', self.default_indent)
            self.indent_stack.append(indent)

        self.indent = ''.join(self.indent_stack)



    base_formats = {
        "box" : {
            "template": '{prefix}┌{line*}┐\n{prefix}│ {message}{space*} │\n{prefix}└{line*}┘\n',
            "line*": '─',
            "space*": ' ',
        },
        "box2" : {
            "template": '{prefix}╔{double*}╗\n{prefix}║ {message}{space*} ║\n{prefix}╚{double*}╝\n',
            "double*": '═',
            "space*": ' ',
        },
        "end" : {
            "template": '╔{double*}╗\n║ {name} finish at {timestamp} {space*}║\n╚{double*}╝\n',
            "double*": '═',
            "space*": ' ',
        },
        "enter": {
            "template": '{prefix}┏━━━━━┱{line*}┐\n{prefix}┃enter┃ {message}{space*} │\n{prefix}┃     ┃ {message}{space*} │\n{prefix}┡━━━━━┹{line*}┘\n',
            "line*": '─',
            "space*": ' ',
            "indent": '│   ',
            "exit": 'exit',
        },
        "exit": {
            "template": '{prefix}┢━━━━━┱{line*}┐\n{prefix}┃exit ┃ {message}{space*} │\n{prefix}┃     ┃ {message}{space*} │\n{prefix}┗━━━━━┹{line*}┘\n',
            "line*": '─',
            "space*": ' ',
        },
        "log": {
            "template": '{prefix}{message}\n',
        },
        "start": {
            "template": '╔{double*}╗\n║ {name} start at {timestamp} {space*}║\n╚{double*}╝\n',
            "double*": '═',
            "space*": ' ',
        },
        "preformatted": {
            "template": '{prefix}{message}\n',
        },

    }

    @staticmethod
    def parse_formats(base_formats, override_formats, width):

        formats = dict(base_formats)
        formatters = {}

        for key, value in override_formats.items():
            if not isinstance(key, str):
                raise TypeError(f"formats dict contains {key!r}, formats dict keys must be str")

            if value is None:
                if key not in ("start", "end", 'enter', 'exit'):
                    raise ValueError("None is only a valid value for 'start', 'end', 'enter', and 'exit' formats")
                formats.pop(key, None)
                formatters[key] = _none_format
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
                formats[key] = dict(value)

        for key, d in formats.items():
            d_copy = dict(d)
            template = d_copy.pop('template')
            formatters[key] = big_template.Formatter(template, d_copy, width=width).format_map

        return formats, formatters

    def format(self, elapsed, thread, format, message, data, nesting):
        if data is not None:
            raise TypeError("data must be None")

        if nesting is None:
            nesting_depth = len(self.nesting)
            cache = True
        else:
            nesting_depth = len(nesting)
            cache = False

        if thread is None:
            thread = _empty_thread

        epoch = self.start_time_epoch + self.ns_to_float(elapsed)

        map = {
            "elapsed": self.ns_to_float(elapsed),
            "format": format,
            "indent": self.indent,
            "name": self.root.name,
            "thread": thread,
            "time": epoch,
            "timestamp": self.timestamp_format(epoch),
            }

        prefix = self.prefix.format_map(map)
        map['prefix'] = prefix

        # unbox format
        format_name = format['format']

        formatter = self.formatters[format_name]
        formatted = formatter(message, map)
        return formatted

    def exit_format(self, format):
        if isinstance(format, str):
            format_name = format
            result = {}
        else:
            format_name = format['format']
            result = dict(format)
        d = self.formats.get(format_name, None)
        if (d is None) or ('exit' not in d):
            return None
        result['format'] = d['exit']
        return result


    def enter(self, elapsed, thread, format, message):
        if isinstance(format, str):
            format_name = format
        else:
            format_name = format['format']
        if format_name not in self.formats:
            indent = self.default_indent
        else:
            format = self.formats[format_name]
            assert 'exit' in format
            indent = format.get('indent', self.default_indent)
        self.indent_stack.append(indent)

        self.indent = ''.join(self.indent_stack)

    def exit(self, elapsed, thread, format, context):
        assert self.indent_stack
        self.indent_stack.pop()
        self.indent = ''.join(self.indent_stack)




_ascii_translation_table = ''.maketrans({
    '│': '|',
    '─': '-',

    '┌': '+',
    '┐': '+',
    '└': '+',
    '┘': '+',


    '║': '|',
    '═': '-',

    '╔': '+',
    '╗': '+',
    '╚': '+',
    '╝': '+',


    '┃': '|',
    '━': '-',

    '┏': '+',
    '┓': '+',
    '┗': '+',
    '┛': '+',

    '┱': '+',
    '┡': '+',
    '┹': '+',
    '┢': '+',
    '┱': '+',
    '┹': '+',
    })

@export
class ASCIIFormatter(TextFormatter):

    def make_base_formats():
        base_formats = {}
        for format_name, format in TextFormatter.base_formats.items():
            base_formats[format_name] = d = {}
            for key, value in format.items():
                d[key] = value.translate(_ascii_translation_table)
        return base_formats

    base_formats = make_base_formats()
    del make_base_formats


    @staticmethod
    def prefix_format(time_seconds_width, time_fractional_width, thread_name_width=12, *, indent=True):
        """
        Formats a "prefix" string for use with a Log object.

        The format it returns is in the form:
            "[{elapsed} {thread.name}] "
        formatted with these widths:
             "[{time_seconds_width}.{time_fractional_width} {thread_name_width}]"
        For example, the default value for Log.prefix is prefix_format(3, 10, 12),
        which looks like this in the final log:
            "[003.0706368860   MainThread]"

        If the indent parameter is true (the default), the prefix generated
        is followed by {indent}, which inserts the current indent string.

        (The actual value of "indent" supplied by TextFormatter will be
        the string passed in to its 'indent' parameter, multipled by the
        current "enter" nesting depth.)
        """
        # the +1 is for the dot between seconds and fractional seconds
        s = TextFormatter.prefix_format(time_seconds_width=time_seconds_width, time_fractional_width=time_fractional_width, thread_name_width=thread_name_width, indent=indent)
        return s.translate(_ascii_translation_table)

    def __init__(self,
        *,
        formats=None,
        indent='    ',
        prefix=prefix_format(3, 10, 12),
        timestamp_format=timestamp_human,
        width=79,
        ):
        super().__init__(formats=formats, indent=indent, prefix=prefix, timestamp_format=timestamp_format, width=width)



class Sink(Formatter):
    """
    A Formatter retaining all log messages, in order, using LogEvents.

    Every time Sink receives an event from the Log, it appends
    a LogEvent object to an internal list of events.
    See LogEvent and its subclasses for more.

    You may iterate over a Sink, which yields all events logged so far.

    Sink.print() formats the events and prints them using
    builtins.print.
    """

    supported_formats = True

    def validate(self, format, message, data):
        return True

    def __init__(self):
        super().__init__(self._format)
        self._session = 0
        self._events = []
        self._longest_message = 0
        self._depth = 0

    def _format(self):
        raise NotImplementedError()

    def _event(self, event):
        if hasattr(event, 'message') and (event.message is not None):
            self._longest_message = max(self._longest_message, len(event.message))

        if self._events:
            previous = self._events[-1]
            if not isinstance(previous, LogEndEvent):
                assert event.elapsed >= previous.elapsed, \
                    f"duration should be >= 0 but it's {event.elapsed - previous.elapsed} ({previous})"
                self._events[-1] = previous._calculate_duration(event)

        self._events.append(event)

    def start(self, start_time_ns, start_time_epoch, nesting):
        super().start(start_time_ns, start_time_epoch, nesting)
        self._session += 1

        configuration = {
            "clock" : self.root._clock,
            "name" : self.root._name,
            "paused" : self.root.paused_on_reset,
            "threaded" : self.root._threaded,
            "timestamp_clock" : self.root._timestamp_clock,
        }
        nesting = tuple(nesting)
        self._event(LogStartEvent(self._session, start_time_ns, start_time_epoch, nesting, configuration))


    def end(self, elapsed):
        super().end(elapsed)
        self._event(LogEndEvent(self._session, elapsed))
        self._depth = 0

    def log(self, elapsed, thread, format, message, data):
        self._event(LogLogEvent(self._session, elapsed, thread, format, message, data, self._depth))

    def enter(self, elapsed, thread, format, message):
        self._event(LogEnterEvent(self._session, elapsed, thread, format, message, self._depth))
        self._depth += 1

    def exit(self, elapsed, thread, format, context):
        self._depth -= 1
        self._event(LogExitEvent(self._session, elapsed, thread, format, context, self._depth))

    def __iter__(self):
        for e in self._events:
            yield e

    def print(self, *,
            enter='',
            exit='',
            indent=2,
            prefix='[{elapsed:>014.10f} {thread.name:>12} {duration:>014.10f} {format:>8} {type:>5}] {indent}',
            print=None,
            timestamp=timestamp_human,
            width=None,
            ):
        if not self._events:
            return

        # start_time_epoch will always have a valid value
        assert isinstance(self._events[0], LogStartEvent)

        if not print:
            print = builtins.print

        if width is None:
            width = self._longest_message

        start_time_epoch = None

        for e in self._events:
            if isinstance(e, LogStartEvent):
                start_time_epoch = e.epoch

            elapsed = e.elapsed / 1_000_000_000.0
            duration = getattr(e, 'duration', 0) / 1_000_000_000.0
            epoch = elapsed + start_time_epoch
            ts = timestamp(epoch)
            indent_str = ' ' * (e.depth * indent)
            thread = getattr(e, 'thread', _empty_thread)

            e_type = type(e).__name__[3:-5].lower()

            format = getattr(e, 'format', None) or {}
            format_name = format.get('format', '')

            fields = {
                'elapsed': elapsed,
                'duration': duration,
                'format': format_name,
                'timestamp': ts,
                'thread': thread,
                'type': e_type,
                'depth': e.depth,
                'indent': indent_str,
            }
            prefix_str = prefix.format_map(fields)
            space_str = " " * len(prefix_str)
            message = getattr(e, 'message', '')
            for line in message.split('\n'):
                print(prefix_str + line)
                prefix_str = space_str

            data = getattr(e, 'data', None)
            if data is not None:
                print(prefix_str + repr(data))


@export
class Destination:
    def __init__(self):
        self._owner = self._log = None
        self._active = False

    def __eq__(self, other):
        raise NotImplementedError()

    def __hash__(self):
        raise NotImplementedError()

    def __repr__(self):
        registered = 'registered' if self._owner is not None else 'unregistered'
        active = 'active' if self._active else 'inactive'
        return f'<{type(self).__name__} {registered}>'

    def register(self, log, owner):
        assert self._log is None
        assert self._owner is None
        assert log is not None
        assert owner is not None
        self._log = log
        self._owner = owner

    def unregister(self):
        assert self._log is not None
        assert self._owner is not None
        self._log = self._owner = None

    def start(self):
        assert not self._active
        self._active = True

    def end(self):
        assert self._active
        self._active = False

    def write(self, formatted):
        raise NotImplementedError()

    def flush(self):
        pass

@export
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
        return isinstance(other, Callable) and (other._callable is self._callable)

    def __hash__(self):
        return hash(Callable) ^ hash(self._callable)

    def write(self, formatted):
        self._callable(formatted)

@export
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

        Path = pathlib.Path

        original_path = path

        is_bytes = isinstance(path, bytes)
        is_str = isinstance(path, str)
        is_path = isinstance(path, Path)

        if not (is_bytes or is_str or is_path):
            raise TypeError("path must be str, bytes, or pathlib.Path, and non-empty")
        if not path:
            raise ValueError("path must be str, bytes, or pathlib.Path, and non-empty")

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
        return isinstance(other, File) and (other._path == self._path)

    def __hash__(self):
        return hash(File) ^ hash(self._path)

    def start(self):
        super().start()
        self._f = None if self._buffering else self._path.open(self._mode, encoding=self._encoding)

    def end(self):
        super().end()
        assert not self._buffer
        if self._f:
            assert not self._buffering
            f = self._f
            self._f = None
            f.close()
            self._mode = "at"

    def write(self, formatted):
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


@export
class FileHandle(Destination):
    def __init__(self, handle, *, autoflush=False):
        super().__init__()
        self._handle = handle
        self._autoflush = autoflush

    def __eq__(self, other):
        return isinstance(other, FileHandle) and (other._handle is self._handle)

    def __hash__(self):
        return hash(FileHandle) ^ hash(self._handle)

    def write(self, message):
        self._handle.write(message)
        if self._autoflush:
            self._handle.flush()

    def flush(self):
        self._handle.flush()

@export
class List(Destination):
    def __init__(self, list):
        super().__init__()
        self._list = list

    def __eq__(self, other):
        return isinstance(other, List) and (other._list is self._list)

    def __hash__(self):
        return hash(List) ^ id(self._list)

    def write(self, message):
        self._list.append(message)

@export
class NoneType(Destination):
    """
    A Destination wrapping None.  Does nothing.
    """
    def __eq__(self, other):
        return isinstance(other, NoneType)

    def __hash__(self):
        return hash(NoneType) ^ hash(object)

    def write(self, message):
        pass

@export
class Print(Destination):
    def __eq__(self, other):
        return isinstance(other, Print)

    def __hash__(self):
        return hash(Print) ^ hash(object)

    def write(self, message):
        builtins.print(message, end='')

    def flush(self):
        builtins.print('', end='', flush=True)

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

    def __eq__(self, other):
        return isinstance(other, Buffer) and (other._destination == self._destination)

    def __hash__(self):
        return hash(Buffer) ^ hash(self._destination)

    def register(self, log, owner):
        super().register(log, owner)
        self._destination.register(log, self)

    def unregister(self):
        super().unregister()
        self._destination.unregister()

    def start(self):
        super().start()
        self._destination.start()

    def end(self):
        super().end()
        self._destination.end()

    def write(self, formatted):
        self._buffer.append(formatted)

    def flush(self):
        if self._buffer:
            contents = "".join(self._buffer)
            self._buffer.clear()
            self._destination.write(contents)
        if self._buffer:
            self._destination.flush()



@export
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

    def __init__(self, prefix='{name}', *, buffering=True, encoding=None, timestamp_format=timestamp_human):
        # use a fake path for now,
        # we'll compute a proper one when we get the "start" event
        path = pathlib.Path(tempfile.gettempdir()) / f"Log-init.{os.getpid()}.tmp"
        super().__init__(path, buffering=buffering, encoding=encoding)
        if not (isinstance(prefix, str) and prefix):
            raise TypeError("prefix must be str, and cannot be empty")
        self._name = None
        self._prefix = prefix
        self._rendered_prefix = None
        self._timestamp_format = timestamp_format

    @property
    def prefix(self):
        return self._prefix

    @property
    def path(self):
        return self._path

    def __eq__(self, other):
        return isinstance(other, TmpFile) and (other._prefix == self._prefix)

    def __hash__(self):
        return hash(TmpFile) ^ hash(self._prefix)

    def register(self, log, owner):
        super().register(log, owner)
        self._name = self._log.name
        self._rendered_prefix = self._prefix.format(name=self._name)

    def start(self):
        super().start()
        assert self._owner
        log = self._log

        log_timestamp = self._timestamp_format(log.start_time_epoch)
        log_timestamp = log_timestamp.replace("/", "-").replace(":", "-").replace(" ", ".")
        thread = threading.current_thread()
        tmpfile = f"{self._rendered_prefix}.{log_timestamp}.{os.getpid()}.{thread.name}.txt"
        tmpfile = translate_filename_to_exfat(tmpfile)
        tmpfile = tmpfile.replace(" ", '_')
        self._path = pathlib.Path(tempfile.gettempdir()) / tmpfile

TMPFILE = object()
export("TMPFILE")



@export
class Log:
    def __init__(self, *destinations,
            clock=default_clock,
            formatter=None,
            name='Log',
            paused=False,
            timestamp_clock=time.time,
            threaded=True,
            ):

        ns1 = clock()
        epoch = timestamp_clock()
        ns2 = clock()
        start_time_ns = (ns1 + ns2) // 2
        start_time_epoch = epoch

        self._name = name

        self.paused_on_reset = bool(paused)
        self._paused_counter = int(self.paused_on_reset)

        self._threaded = threaded

        self._dispatch_lock = threading.Lock()
        # if you need both, grab dispatch lock first.
        # dispatch lock is only used for non-threaded mode.
        self._configuration_lock = threading.Lock()

        self._enter_token = 1

        # when you schedule a job, you insert it into
        # job_queue wherever you like, then you queue
        # that number on the notify_queue.
        #
        # why this weird design with two queues?
        # linked_list gives us snazzy APIs, and lets
        #   me dogfood my new ADT.  (a deque would probably
        #   work here, but deque.extendleft irritates me.)
        # Queue gives us cheap cross-thread notification.
        #
        # We use queue.SimpleQueue on 3.7+,
        # and queue.Queue on 3.6.
        #
        self._notify_queue = Queue()
        # self._notify_queue = queue.Queue()
        self._job_queue = linked_list(lock=True)

        self._reset(start_time_ns, start_time_epoch)

        self._clock = clock
        self._timestamp_clock = timestamp_clock

        if formatter is not None:
            if not isinstance(formatter, Formatter):
                raise TypeError(f"formatter must be Formatter, not {type(formatter).__name__}")
            df = formatter
        else:
            df = TextFormatter()

        df.register(self, self)
        self._default_formatter = df
        self._formatters = [df]

        self._active = set()

        if not destinations:
            destinations = (builtins.print,)

        wrapped_destinations = []
        for d in destinations:
            if isinstance(d, Formatter):
                self._formatters.append(d)
                d.register(self, self)
                continue
            if not isinstance(d, Destination):
                d = self.map_destination(d)
                assert isinstance(d, Destination)
            wrapped_destinations.append(d)

        for d in wrapped_destinations:
            df.append(d)

        intersection_formats = None
        for f in self._formatters:
            if f.supported_formats is True:
                continue
            if intersection_formats is None:
                intersection_formats = set(f.supported_formats)
                continue
            intersection_formats = intersection_formats.intersection(f.supported_formats)

        if intersection_formats is None:
            intersection_formats = set()
        intersection_formats = list(intersection_formats)
        intersection_formats.sort()
        for key in (
            'start',
            'end',
            'enter',
            'exit',
            'log',
            'preformatted',
            ):
            if key in intersection_formats:
                intersection_formats.remove(key)

        for key in intersection_formats:
            if isinstance(key, str) and key.isidentifier() and (not hasattr(self, key)):
                def make_method(key):
                    format_dict = {'format': key}
                    clock = self._clock
                    current_thread = threading.current_thread
                    scheduler = self._scheduler
                    log = self._log
                    validate = self._validate
                    def method(message=''):
                        time = clock()
                        thread = current_thread()

                        validate(format_dict, message, None)

                        s = scheduler(drain=True)
                        s(log, time, thread, format_dict, message, None)
                        s()

                    method.__doc__ = f"Writes a message to the log using the {key!r} format."
                    return method
                setattr(self, key, make_method(key))

        atexit.register(self._atexit)

        self._manage_thread()

    def _manage_thread(self):
        if not self._threaded:
            self._queue = self._thread = None
            return

        self._thread = threading.Thread(target=self._worker_thread, daemon=True)
        self._thread.start()

    def _stop_thread(self):
        pass

    def _atexit(self):
        clock = self._clock
        timestamp_clock = self._timestamp_clock
        ns1 = clock()
        epoch = timestamp_clock()
        ns2 = clock()
        ns = (ns1 + ns2) // 2

        s = self._scheduler(atexit=True)
        self._ensure_state('exited', ns=ns, epoch=epoch, s=s)
        s(self._stop_thread)
        s()


    @property
    def clock(self):
        return self._clock

    @property
    def name(self):
        return self._name

    @property
    def start_time_ns(self):
        return self._start_time_ns

    @property
    def start_time_epoch(self):
        return self._start_time_epoch


    @classmethod
    def base_destination_mapper(cls, o):
        "Implements the default mapping of objects to Destination objects."

        if isinstance(o, Destination):
            return o
        if o is print:
            return Print()
        if isinstance(o, (bytes, str, pathlib.Path)):
            return File(o)
        if isinstance(o, list):
            return List(o)
        if isinstance(o, io.TextIOBase):
            return FileHandle(o)
        if callable(o):
            return Callable(o)
        if o is TMPFILE:
            return TmpFile()
        if o is None:
            return NoneType()
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

    def _reset(self, start_time_ns, start_time_epoch):
        self._state = 'initial'

        self._start_time_ns = start_time_ns
        self._start_time_epoch = start_time_epoch
        self._end_time_ns = None
        self._end_time_epoch = None

        self._ever_wrote_anything = False

        self._nesting_tokens = []
        self._nesting_contexts = []

        # do this immediately, don't wait for the thread to do it.
        # otherwise, user might observe a delay between reset()
        # and paused state changing.
        #
        # modifications of _paused_counter are always under lock
        # so we don't have race conditions with incr/decr

        if self._configuration_lock:
            paused = self._paused_counter = int(bool(self.paused_on_reset))

        self._send_start_banner = not paused
        self._ever_logged_anything = set()



    """
    All methods on a Log object that interact with the log are
    implemented using "jobs" objects.  A "jobs" object is a
    list of jobs:
        [job, job2, ...]
    These "job" objects are 3-tuples:
         (involved, callable, args)
    involved is a tuple of objects (Formatters and Destinations)
    involved in this job.  callable is a callable, args is an
    iterable (probably a tuple) of arguments.  We execute the
    jobs like this, more or less:

        for callable, args in jobs:
            callable(*args)

    If threaded is True, the jobs are sent to the worker
    thread.  If threaded is False, the jobs are executed
    immediately, in the current thread, while holding
    self._queue_lock.

    None is also a legal "job"; it must be the last "job"
    in jobs.  If threaded is True, this causes the
    worker thread to exit; if threaded is False, it causes
    the dispatch call to return immediately.

    Why send sequences of jobs?  Why not queue each job
    individually?  The sequence ensures that jobs from
    multiple threads don't get interleaved.  For example,
    Log.enter() logs the "enter" message and indents the log.
    If we queued them separately, we could have a race with
    another thread trying to log something; that other thread
    could get its message logged after the "enter" message but
    before the indent!  By sending both jobs in a list all at
    once, we guarantee that no job from another thread gets
    queued between these two jobs.
    """


    @property
    def _closed(self):
        return self._state in ('closed', 'exited')

    def _set_state(self, state):
        self._state = state

    def _active_add(self, formatter):
        self._active.add(formatter)

    def _active_remove(self, formatter):
        self._active.remove(formatter)

    def _ensure_active(self, s):
        nesting = tuple(self._nesting_contexts)
        paused = bool(self._paused_counter)
        for f in self._formatters:
            s(f.start, self._start_time_ns, self._start_time_epoch, nesting)
            s(self._active_add, f)

            if (self._send_start_banner) and (f.supported_formats is not True) and ('start' in f.supported_formats):
                s(f.log, 0, None, {'format': 'start'}, '', None)
                self._ever_logged_anything.add(id(f))

        self._send_start_banner = False
        s(self._set_state, 'active')

    def _ensure_closed(self, ns, epoch, state, s):
        """
        Ensure the Log is in its closed state, regardless of current state.

        Always called from a thread holding self._configuration_lock,
        though that probably isn't necessary for correctness.
        (It's only in case the _atexit handler gets called
        while we're already executing a state transition.)
        """

        if self._state in ('closed', 'exited'):
            return

        self._end_time_ns = ns
        self._end_time_epoch = epoch
        elapsed = self._elapsed(ns)

        if self._threaded:
            # force some synchronization:
            # if we have any formatters that have never seen anything logged,
            # it might be because the worker thread has been starved for CPU
            # and hasn't been allowed to run their jobs yet.
            # so, block until the worker thread clears the job queue.
            #
            # this will only happen if
            #    * the Log object is unused, in which case the job queue
            #      will be empty anyway, so this'll be quick.
            #    * the program ran and finished super quick, less than
            #      sys.getsysinterval() seconds.  if the program did any
            #      logging, those jobs might be stuck in the queue,
            #      and this will fix it.
            #
            # if all formatters have ever logged anything, we don't bother
            # to block here.
            all_f_ids = set(id(f) for f in self._formatters)
            if self._ever_logged_anything != all_f_ids:
                self._block()


        for f in self._formatters:
            if f in self._active:
                if (id(f) in self._ever_logged_anything) and (not self._paused_counter) and (f.supported_formats is not True) and ('end' in f.supported_formats):
                    s(f.log, elapsed, None, {'format': 'end'}, '', None)
                s(f.end, elapsed)
                s(self._active_remove, f)

        s(self._set_state, state)

    def _ensure_state(self, state, *, s=None, ns=None, epoch=None):
        # four states:
        #
        #     initial
        #        The initial state.  Log starts out in initial,
        #        and Log.reset() returns to initial.
        #        Reachable from closed and logged.
        #
        #     active
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
        #     faulted
        #        Somebody (Log? Formatter? Destination?)
        #        raised an unexpected, and unhandled,
        #        exception.  If it was a Formatter or
        #        Destination, you can clear the fault
        #        by running Log.fix.  If it was Log itself
        #        that raised, the Log instance is unrecoverable.
        #
        assert state in ('initial', 'active', 'closed', 'exited', 'faulted')

        # fast path: we're already in the correct state
        if self._state == state:
            return True

        # good news! you can always transition to faulted.
        if state == 'faulted':
            self._state = state
            return True

        # exited is a terminal state.
        if self._state == 'exited':
            return False

        if state == 'initial':
            # because of the above ifs, we already know
            # we're not in 'initial' or 'exited'.
            # that means we're in 'logged' or 'closed'.
            # we're transitioning backwards!
            assert ns is not None
            assert epoch is not None

            if self._state == 'active':
                self._ensure_closed(ns, epoch, 'closed', s)
            s(self._reset, ns, epoch)
            return True

        simulated_self_state = self._state

        # we're not in the correct state,
        # and we're not trying to get to 'initial'.
        # therefore we're making a forwards transition.
        if simulated_self_state == 'initial':
            if state in ('closed', 'exited'):
                # we're transitioning directly from 'initial' to 'closed' or 'exited'.
                # we don't need to do any intermediary stuff.
                self._ensure_closed(ns, epoch, state, s)
                return True

            # transition to 'logged':
            self._ensure_active(s)
            simulated_self_state = 'active'

            if state == 'active':
                assert ns is None
                assert epoch is None
                return True

        if simulated_self_state == 'active':
            self._ensure_closed(ns, epoch, 'closed', s)
            simulated_self_state = 'closed'

            if state == 'closed':
                return True

        assert simulated_self_state == 'closed'
        if state == 'active':
            # it's illegal to transition directly from closed to active,
            # you have to go through initial first (by resetting)
            return False

        assert state == 'exited'
        # transition to exited
        s(self._set_state, 'exited')

        return True

    def _execute(self, block):
        jq = self._job_queue
        nq = self._notify_queue
        result = False
        release_blockers = False

        # if you hit an exception, and you fault,
        # put the remaining count back on nq!
        while True:
            if nq.empty() and (not block):
                break
            count = nq.get()
            for _ in range(count):
                assert jq
                job = jq.rpop()
                involved, fn, args = job
                if fn is None:
                    if args:
                        assert len(args) == 1
                        result = args[0]
                    else:
                        result = True
                    release_blockers = True
                    break
                fn(*args)

        if release_blockers:
            # atexit handler called.
            # we're shutting down.
            # zip through the jobs in the queue,
            # and if any of them are blockers,
            # release 'em.
            for job in jq:
                if job is None:
                    continue
                involved, fn, args = job
                for i in involved:
                    if isinstance(i, threading.Lock):
                        fn(*args)

        return result

    def _block(self):
        if self._threaded:
            locker = threading.Lock()
            locker.acquire()
            self._schedule([((locker,), locker.release, ())])
            locker.acquire()

    def _drain(self):
        with self._dispatch_lock:
            self._execute(False)

    def _worker_thread(self):
        fn = self._execute(True)
        if fn:
            print("ATEXIT calling", fn)
            fn()


    def _schedule(self, jobs, *, first=False):
        """
        jobs is an iterable of job objects.

        a job is either None or a tuple.  (None is a special case.)
        if it's a tuple, it contains
            (involved, fn, args)
        * involved is an iterable of objects "involved" in this job.
          you will see three types: instances of Formatter, Destination,
          and threading.Lock.
        * fn is a callable.
        * args is a tuple of arguments to pass in to fn, a la fn(*args).
        """
        assert isinstance(jobs,       (tuple, list))
        for job in jobs:
            assert isinstance(job,    (tuple, list))
            if job is not None:
                assert isinstance(job[0], (tuple, list))      # involved
                assert   callable(job[1]) or (job[1] is None) # fn or None
                assert isinstance(job[2], (tuple, list))      # args

        count = len(jobs)
        jq = self._job_queue
        nq = self._notify_queue

        if first:
            jq.rextend(jobs)
        else:
            jq.extend(jobs)

        nq.put(count)


    def _scheduler(self, atexit=False, drain=False, first=False, wait=False):
        return Scheduler(self, atexit=atexit, drain=drain, first=first, wait=wait)


    def _no_longer_used(self):
        if not self._thread:
            try:
                self._execute(jobs)
            finally:
                if notify:
                    notify()
            return

        lock = None
        try:
            if notify:
                lock = self._queue_lock
                lock.acquire()

                # what if there's a race between this dispatch call
                # and _atexit closing the thread?  _atexit will only
                # set self._thread to None while holding the lock.
                # now that we hold the lock, we know for certain.
                # if self._thread is now false, recursively call
                # ourselves, which will now execute the jobs directly.
                # (it's all on one line to make coverage happy; this
                # situation is devilishly hard to reproduce.  if only
                # there were some library that made it easy to reproduce
                # race conditions...!)
                if not self._thread: lock.release() ; lock = None ; self._dispatch(jobs, notify=notify); return

                jobs.append( (notify, ()) )

            self._queue.put(jobs)

        finally:
            if lock:
                lock.release()


    def _elapsed(self, t):
        # t should be a value returned by _clock.
        # returns t converted to elapsed time
        # since self.start_time_ns, as integer nanoseconds.
        return t - self._start_time_ns


    def _flush(self):
        s = self._scheduler()
        for f in self._formatters:
            s(f.flush)
        s()

    def flush(self, *, wait=True):
        s = self._scheduler(drain=True, wait=wait)
        s(self._flush)
        s()

    def _log(self, time, thread, format, message, data):
        if self._paused_counter:
            return

        s = self._scheduler(first=True)

        self._ensure_state('active', s=s)

        elapsed = self._elapsed(time)

        if isinstance(format, str):
            format = {'format': format}

        for f in self._formatters:
            s(f.log, elapsed, thread, format, message, data)
            self._ever_logged_anything.add(id(f))

        s()


    def _validate(self, format, message, data):
        for f in self._formatters:
            f.validate(format, message, data)

    def log(self, message, *, format='log', data=None):
        time = self._clock()
        thread = threading.current_thread()

        if isinstance(format, str):
            format = {'format': format}
        else:
            if not isinstance(format, dict):
                raise TypeError("format must be str or dict")
            if not isinstance(format.get('format', None), str):
                raise TypeError("format['format'] must be defined, and must be str")
            format = dict(format)

        self._validate(format, message, data)

        s = self._scheduler(drain=True)
        s(self._log, time, thread, format, message, data)
        s()

    def write(self, message):
        self.log(message, format={'format': 'preformatted'})

    def _call(self, time, thread, args, sep, end, flush, format):
        if not isinstance(sep, str):
            raise TypeError(f'sep must be str, not {type(sep).__name__}')
        if not isinstance(end, str):
            raise TypeError(f'end must be str, not {type(end).__name__}')

        message = sep.join(str(a) for a in args) + end
        if message.endswith('\n'):
            message = message[:-1]

        if isinstance(format, str):
            format = {'format': format}
        else:
            if not isinstance(format, dict):
                raise TypeError("format must be dict or str, not {type(format).__name__}")
            if not isinstance(format.get('format', None), str):
                raise TypeError("format must contain a 'format' key with value str")
        self._validate(format, message, None)

        s = self._scheduler(drain=True)
        s(self._log, time, thread, format, message, None)
        if flush:
            s(self._flush)
        s()

    def __call__(self, *args, sep=' ', end='\n', flush=False, format='log'):
        time = self._clock()
        thread = threading.current_thread()
        return self._call(time, thread, args, sep, end, bool(flush), format)

    def print(self, *args, sep=' ', end='\n', flush=False, format='log'):
        time = self._clock()
        thread = threading.current_thread()
        return self._call(time, thread, args, sep, end, bool(flush), format)


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

    def _nesting_append(self, token, context):
        self._nesting_tokens.append(token)
        self._nesting_contexts.append(context)

    def _nesting_pop(self, token):
        if token not in self._nesting_tokens:
            return None
        self._nesting_tokens.pop()
        context = self._nesting_contexts.pop()
        return context

    def _enter(self, time, thread, token, format, message):
        elapsed = self._elapsed(time)
        s = self._scheduler(first=True)

        self._ensure_state('active', s=s)

        context = EnterContext(elapsed, thread, format, message)

        format_name = format['format']

        for f in self._formatters:
            if (not self._paused_counter) and (f.supported_formats is not True) and (format_name in f.supported_formats):
                s(f.log, elapsed, thread, format, message, None)
            s(f.enter, *context)

        s(self._nesting_append, token, context)
        s()

    def _exit(self, time, thread, token):
        elapsed = self._elapsed(time)
        s = self._scheduler(first=True)

        self._ensure_state('active', s=s)
        s(self._exit2, elapsed, thread, token)
        s()

    def _exit2(self, elapsed, thread, token):
        context = self._nesting_pop(token)
        if (not context) or (self._state != 'active'):
            return

        s = self._scheduler(first=True)
        for f in self._formatters:
            if f.supported_formats is True:
                exit_format = None
            else:
                exit_format = f.exit_format(context.format)
            s(f.exit, elapsed, thread, exit_format, context)
            if not self._paused_counter:
                if exit_format and ('format' in exit_format) and (f.supported_formats is not True) and (exit_format['format'] in f.supported_formats):
                    s(f.log, elapsed, thread, exit_format, context.message, None)
        s(self._exit2, elapsed, thread, token)
        s()

    class _ExitContextManager:
        """
        The context manager returned by Log.enter().  Calls Log.exit() on exit.
        """
        def __init__(self, log, token):
            assert log
            self._log = log
            self._token = token

        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_value, traceback):
            self.__call__()

        def __call__(self):
            log = self._log
            time = log._clock()
            thread = threading.current_thread()
            log._schedule([((), log._exit, (time, thread, self._token))])
            if not log._threaded:
                log._drain()

    def enter(self, message, *, format='enter'):
        time = self._clock()
        thread = threading.current_thread()
        if isinstance(format, str):
            format = {'format': format}
        # note: we don't validate the exit format.
        # you gotta validate that here, when validating
        # the enter format.  stay on the ball, son!
        self._validate(format, message, None)
        with self._configuration_lock:
            token = self._enter_token
            self._enter_token += 1
        self._schedule([((), self._enter, (time, thread, token, format, message))])
        if not self._threaded:
            self._drain()
        return self._ExitContextManager(self, token)


    def _reset_or_close(self, state, ns, epoch):
        s = self._scheduler(first=True)
        self._ensure_state(state, ns=ns, epoch=epoch, s=s)
        s()



    def close(self, *, wait=True):
        clock = self._clock
        timestamp_clock = self._timestamp_clock
        ns1 = clock()
        epoch = timestamp_clock()
        ns2 = clock()
        ns = (ns1 + ns2) // 2

        s = self._scheduler(wait=wait)
        s(self._reset_or_close, 'closed', ns, epoch)
        s()

    def reset(self, *, wait=True):
        clock = self._clock
        timestamp_clock = self._timestamp_clock
        ns1 = clock()
        epoch = timestamp_clock()
        ns2 = clock()
        ns = (ns1 + ns2) // 2

        s = self._scheduler(wait=wait)
        s(self._reset_or_close, 'initial', ns, epoch)
        s()


    @property
    def paused(self):
        "Returns True if the log is paused, None if the log is closed, and otherwise False."
        if self._configuration_lock:
            if self._closed:
                return None
            return bool(self._paused_counter)


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


    def _pause(self):
        if self._closed:
            return

        with self._configuration_lock:
            self._paused_counter += 1

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
        self._schedule( [( (), self._pause, () )] )
        if not self._threaded:
            self._drain()

        return self._ResumeContextManager(self)

    def _resume(self):
        # modifications of _paused_counter are always under lock
        # so we don't have race conditions with incr/decr
        if self._closed:
            return

        with self._configuration_lock:
            if self._paused_counter > 1:
                self._paused_counter -= 1
                return

            # clamp to zero
            self._paused_counter = 0


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
        self._schedule( [( (), self._resume, () )] )
        if not self._threaded:
            self._drain()


mm()
