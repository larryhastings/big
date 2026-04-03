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
import copy
import io
import os
import pathlib
import queue
import sys
import tempfile
import threading
import time
import types
import weakref

from . import template as big_template

from .boundinnerclass import BoundInnerClass, BOUNDINNERCLASS_OUTER_SLOTS
from .builtin import ModuleManager
from .file import translate_filename_to_exfat
from .time import timestamp_human
from .types import linked_list

Queue = getattr(queue, "SimpleQueue", queue.Queue)



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


_USE_DEFAULT = None

class UseDefault:
    def __new__(cls):
        global _USE_DEFAULT
        if _USE_DEFAULT is not None:
            raise ValueError("_USE_DEFAULT is a singleton")
        _USE_DEFAULT = super().__new__(cls)
        return _USE_DEFAULT

    def __repr__(self):
        return "<UseDefault>"

_USE_DEFAULT = UseDefault()





def _merge_dicts(base, update, path):
    base_keys = set(base)
    update_keys = set(update)
    all_keys = base_keys | update_keys

    result = {}

    for key in all_keys:
        in_base = key in base_keys
        in_update = key in update_keys

        if not (in_base and in_update):
            if in_base:
                value = base[key]
            else:
                value = update[key]
            result[key] = value
            continue

        # it's in both base and update.
        base_value = base[key]
        update_value = update[key]

        base_is_dict = int(isinstance(base_value, dict))
        update_is_dict = int(isinstance(update_value, dict))
        is_dict_sum = base_is_dict + update_is_dict

        if (base_value is None) or (update_value is None) or (not is_dict_sum):
            result[key] = update_value
            continue

        child_path = path + f'[{key!r}]'
        if is_dict_sum == 2:
            result[key] = _merge_dicts(base_value, update_value, child_path)
            continue

        raise TypeError(f"type mismatch at {child_path} between dict and non-dict")
    return result


def merge_dicts(base, update):
    """
    Recursively updates base with update.
    Returns a new dict; doesn't modify either base or update.

    The shape of the two dicts must match, to the extent that
    every value in common between the two dicts must be either
    both dicts or neither dicts.  The one exception: one can
    be a dict and the other, None.
    """
    return _merge_dicts(base, update, '')



def deep_update(dst, src):
    for key, value in src.items():
        if isinstance(value, dict) and isinstance(dst.get(key), dict):
            deep_update(dst[key], value)
        else:
            dst[key] = copy.deepcopy(value)
    return dst



_serial_number_lock = threading.Lock()
_serial_number_counter = 1

def _serial_number():
    global _serial_number_counter
    with _serial_number_lock:
        sn = _serial_number_counter
        _serial_number_counter += 1
    return sn



@export
class Formatter:
    # supported_formats                   # frozenset, or True = accepts any
    # output_type                         # type (str, bytes, SinkEvent, etc.)

    # __slots__ = ('name', 'key', '__weakref__') + BOUNDINNERCLASS_OUTER_SLOTS

    def __init__(self, format_dict, *, name=None):
        # self.root = self.owner = None
        if not ((name is None) or isinstance(name, str)):
            raise  TypeError('str must be name or None')

        self.format_dict = format_dict

        if name is None:
            name = type(self).__name__
        self.name = name

        self.serial_number = _serial_number()
        self.key = (self.name, self.serial_number, id(self))
        self.format_cache = {}

        self.core = None
        self.session = None

    # a callback, core calls f.register(self) when f is routed in this Log
    def register(self, core):
        assert self.core is None
        self.core = core
        # print(f"{self!r} registered! {core=}")

    def unregister(self):
        assert isinstance(self.core, Core)
        self.core = None

    # a callback, somebody calls f.start(session) after f is registered and a session has been created
    def start(self, session):
        assert self.session is None
        self.session = session
        # print(f"{self!r} started! {session=}")

    def end(self):
        assert isinstance(self.session, Session)
        self.session = None

    @staticmethod
    def key_to_format_dict(d, key):
        if isinstance(key, tuple):
            key_list = list(key)
            key_list.reverse()
        else:
            key_list = [key]

        while key_list:
            subkey = key_list.pop()
            d = d['formats']
            if key_list:
                d = d[subkey]
            else:
                # let the last one be None
                d = d.get(subkey, None)
        return d

    def format(self, key):
        if key == '':
            return self.format_dict

        cached = self.format_cache.get(key, None)
        if cached is None:
            format_dict = self.key_to_format_dict(self.format_dict, key)
            if format_dict != None:
                base_key = format_dict.get('base', None)
                if base_key is not None:
                    base = self.format(base_key)
                    format_dict = merge_dicts(base, format_dict)
            cached = self.format_cache[key] = format_dict
        return cached

    @BoundInnerClass
    class State:
        # __slots__ = ('formatter', 'fstates',)

        def __repr__(self):
            return f"<State formatter={self.formatter} format={self.format!r} parent={self.parent!r}>"

        def __init__(self, formatter, format, parent=None):
            self.formatter = formatter
            self.format = format
            self.format_dict = formatter.format(format)
            self.parent = parent

        def prepare(self, message):
            raise NotImplementedError

    def render(self, message):
        raise NotImplementedError







@export
def prefix_format(time_seconds_width, time_fractional_width, thread_name_width=12, *, indent=True, ascii=False):
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
    prefix = f'{{elapsed:0{time_width}.{time_fractional_width}f}} {{thread.name:>{thread_name_width}}}│ {indent}'
    if ascii:
        prefix = prefix.translate(_ascii_translation_table)
    return prefix


@export
class TextFormatter(Formatter):
    # supported_formats = frozenset({...})
    # owns formats dict, prefix, nesting stack, indentation

    # __slots__ = ('format_dict', 'formats', 'timestamp_format', 'width', 'indents', 'renderers')


    def __init__(self,
        format_dict=None,
        *,
        name=None,
        # indent='    ',
        # prefix=prefix_format(3, 10, 12),
        width=79,
        ):

        if not isinstance(width, int):
            raise  TypeError('width must be an int and greater than zero')
        if not (width > 0):
            raise ValueError('width must be an int and greater than zero')

        format_dict_is_None = format_dict is None
        if not (format_dict_is_None or isinstance(format_dict, dict)):
            raise TypeError('format_dict must be a dict or None')

        if format_dict_is_None:
            format_dict = self.base_format_dict
        else:
            format_dict = merge_dicts(self.base_format_dict, format_dict)

        super().__init__(format_dict, name=name)


        self.width = width
        self.indents = {}
        self.renderers = {}

        self.indent = ''
        # self.indent_stack = []
        # self.prefix = prefix

        self.supported_formats = set(self.format_dict.get('formats', ()))


    base_format_dict = {
        "prefix": prefix_format(3, 10, 12),
        'template': '{prefix}{message}\n',

        "double*": '═',
        "line*": '─',
        "space*": ' ',

        "formats": {
            "box" : {
                'base': '',
                "template": '{prefix}┌{line*}┐\n{prefix}│ {message}{space*} │\n{prefix}└{line*}┘\n',
            },
            "box2" : {
                'base': '',
                "template": '{prefix}╔{double*}╗\n{prefix}║ {message}{space*} ║\n{prefix}╚{double*}╝\n',
            },

            'session': {
                'formats': {
                    "start": {
                        'base': '',
                        "template": '╔{double*}╗\n║ {name} start at {timestamp} {space*}║\n╚{double*}╝\n',
                    },
                    "end" : {
                        'base': '',
                        "template": '╔{double*}╗\n║ {name} finish at {timestamp} {space*}║\n╚{double*}╝\n',
                    },
                }
            },

            "child": {
                "base": '',
                "indent": "│   ",
                "formats": {
                    "start": {
                        'base': '',
                        "template": '{prefix}┏━━━━━┱{line*}┐\n{prefix}┃enter┃ {message}{space*} │\n{prefix}┃     ┃ {message}{space*} │\n{prefix}┡━━━━━┹{line*}┘\n',
                    },
                    "end": {
                        'base': '',
                        "template": '{prefix}┢━━━━━┱{line*}┐\n{prefix}┃exit ┃ {message}{space*} │\n{prefix}┃     ┃ {message}{space*} │\n{prefix}┗━━━━━┹{line*}┘\n',
                        "space*": ' ',
                    },
                }
            }
        }
    }


    class Prepared:
        # __slots__ = ('args', 'kwargs', 'format', 'keys', 'dedup_keys')

        def __init__(self, args, kwargs, fstate):
            self.args = tuple(str(o) for o in args)
            self.kwargs = {name: str(value) for name, value in kwargs.items()}
            self.fstate = fstate

        def __repr__(self):
            return f"<TextFormatter.Prepared fstate={self.fstate!r} args={self.args!r} kwargs={self.kwargs!r} keys={self.keys!r} dedup_keys={self.dedup_keys!r}>"

    @BoundInnerClass
    class State(Formatter.State):
        # __slots__ = ()

        def __init__(self, formatter, format, parent=None):
            super().__init__(formatter, format, parent)

            if parent is None:
                parent_indent = ''
            else:
                parent_indent = parent.indent
            self.indent = parent_indent + self.format_dict.get('indent', '')

        def prepare(self, message):
            return self.formatter.Prepared(message.args, message.kwargs, self)



    def get_renderers(self, prepared):
        fstate = prepared.fstate
        format = fstate.format
        renderers = self.renderers.get(format)
        if renderers is None:
            format_dict = fstate.format_dict
            prefix_renderer = format_dict.get('prefix', '').format_map
            template_renderer = big_template.Formatter(
                format_dict['template'],
                format_dict,
                width=self.width,
                )
            self.renderers[format] = renderers = (prefix_renderer, template_renderer)
        return renderers

    def message_to_priority(self, message, prepared):
        session = self.session
        clock = session.clock
        timestamp = clock.time_to_timestamp(message.time)
        elapsed = clock.delta_to_seconds(message.time - session.clock.initial)
        fstate = prepared.fstate

        return {
            'elapsed': elapsed,
            'indent': fstate.indent,
            'name': session.name,
            'thread': message.thread,
            'timestamp': timestamp,
            }

    def render(self, message):
        prepared = message.prepared[self.key]
        prefix_renderer, template_renderer = self.get_renderers(prepared)
        priority = self.message_to_priority(message, prepared)
        priority['prefix'] = prefix_renderer(priority)
        lines = list(prepared.args)
        if prepared.kwargs:
            lines.extend(f'{name}={value}' for name, value in prepared.kwargs.items())
        message_text = '\n'.join(lines)
        s = template_renderer(message=message_text, **priority)
        return s


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

def _convert_to_ascii(d):
    result = {}
    for key, value in d.items():
        if isinstance(value, str):
            value = value.translate(_ascii_translation_table)
        elif isinstance(value, dict):
            value = _convert_to_ascii(value)
        result[key] = value

    return result


@export
class ASCIIFormatter(TextFormatter):

    base_format_dict = _convert_to_ascii(TextFormatter.base_format_dict)


    def __init__(self,
        *,
        formats=None,
        # indent='    ',
        # prefix=prefix_format(3, 10, 12, ascii=True),
        timestamp_format=timestamp_human,
        width=79,
        ):
        super().__init__(formats=formats,
            # indent=indent, prefix=prefix,
            timestamp_format=timestamp_format, width=width)




@export
class Destination:
    # __slots__ = ('_log', '_formatter', '_session')

    def __init__(self):
        self._core = None
        self._formatter = None
        self._session = None

        self._serial_number = _serial_number()
        self._key = (self.__class__.__name__, self._serial_number, id(self))

    def __eq__(self, other):
        raise NotImplementedError()

    def __hash__(self):
        raise NotImplementedError()

    def __repr__(self):
        registered = 'registered' if self._core is not None else 'unregistered'
        active = 'active' if self._session else 'inactive'
        return f'<{type(self).__name__} {registered}>'

    def register(self, core, formatter):
        if (self._core is not None) or (self._formatter is not None):
            raise RuntimeError(f"{self} is already registered")
        self._core = core
        self._formatter = formatter
        # print(f"{self!r} registered! {core=} {formatter=}")

    def unregister(self):
        if (self._core is None) or (self._formatter is None):
            raise RuntimeError(f"{self} isn't registered")
        self._core = self._formatter = None

    def start(self, session):
        if (self._core is None) or (self._formatter is None):
            raise RuntimeError(f"can't start {self}, it's unregistered")
        if (self._session is not None):
            raise RuntimeError(f"can't start {self}, it was already started")
        self._session = session
        # print(f"{self!r} started! {session=}")

    def end(self):
        if self._session is None:
            raise RuntimeError(f"can't end {self}, it wasn't started")
        self._session = None

    def write(self, o):
        assert self._session
        raise NotImplementedError()

    def flush(self):
        assert self._session




@export
class Callable(Destination):
    """
    A Destination wrapping a callable.

    Calls the callable for every formatted log message.
    """
    __slots__ = ('_callable',)

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

    def write(self, o):
        self._callable(o)


@export
class Print(Destination):
    __slots__ = ()

    def __eq__(self, other):
        return isinstance(other, Print)

    def __hash__(self):
        return hash(Print) ^ hash(object)

    def write(self, o):
        builtins.print(o, end='')

    def flush(self):
        builtins.print('', end='', flush=True)


@export
class List(Destination):
    __slots__ = ('_list',)

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

    def start(self, session):
        super().start(session)
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
        if not isinstance(handle, io.TextIOBase):
            raise TypeError(f"invalid file handle {handle}")
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
        self._destination = Log.map_destination(destination) if destination is not None else Print()
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

    def register(self, core, log):
        super().register(core, log)
        self._destination.register(core, log)

    def unregister(self):
        super().unregister()
        self._destination.unregister()

    def start(self, session):
        super().start(session)
        self._destination.start(session)

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
        self._name = log.name
        self._rendered_prefix = self._prefix.format(name=self._name)

    def start(self, session):
        super().start(session)
        assert self._core
        clock = session.clock

        log_timestamp = clock.time_to_timestamp(clock.initial)
        log_timestamp = log_timestamp.replace("/", "-").replace(":", "-").replace(" ", ".")
        thread = threading.current_thread()

        tmpfile = f"{self._rendered_prefix}.{log_timestamp}.{os.getpid()}.{thread.name}.txt"
        tmpfile = translate_filename_to_exfat(tmpfile)
        tmpfile = tmpfile.replace(" ", '_')
        self._path = pathlib.Path(tempfile.gettempdir()) / tmpfile

TMPFILE = object()
export("TMPFILE")





@export
class Core:
    # __slots__ = (
    #     'clock',
    #     'clock_to_timestamp',
    #     'sessions',
    #     'formatters',
    #     'formatters_by_key',
    #     'job_queue',
    #     'name',
    #     'notify_queue',
    #     'routes',
    #     'sessions',
    #     'started',
    #     'threaded',
    #     'timestamp_clock',
    #     'thread',
    #     )


    def __init__(self,
        *,
        clock,
        name,
        threaded,
        ):

        self.clock = clock
        self.name = name
        self.threaded = bool(threaded)

        self.notify_queue = Queue()
        self.job_queue = linked_list(lock=True)

        self.formatters = []
        self.formatters_by_key = {}
        self.routes = {}
        self.fstates = {}

        self.started = None

        self.configuration_lock = threading.Lock()
        self.sessions = linked_list(lock=True)
        self.supported_formats = None

        atexit.register(self.atexit)

        self.thread = None
        self._start_thread()


    def _start_thread(self):
        if not (self.threaded and (self.thread is None)):
            return

        self.thread = threading.Thread(target=self.execute, args=(True,), daemon=True)
        self.thread.start()

    def _stop_thread(self):
        if not (self.threaded and (self.thread is not None)):
            return

        thread = self.thread
        jq = self.job_queue
        nq = self.notify_queue

        # ensure all jobs up to now have been executed
        blocker = threading.Lock()
        blocker.acquire()
        self.dispatch([(blocker.release, ())])
        blocker.acquire()

        # flip all sessions to closed
        self.reset()

        self.flush()

        self.thread = self.job_queue = self.notify_queue = None

        jq.append(None)
        nq.put(1)
        thread.join()


    def route(self, formatter, destinations):
        try:
            session = self.sessions[0]()
            assert self.started is not None
        except IndexError:
            session = None

        if formatter.key not in self.formatters_by_key:
            self.formatters.append(formatter)
            self.formatters_by_key[formatter.key] = formatter
            self.routes[formatter.key] = []

            formatter.register(self)

            if self.supported_formats is None:
                self.supported_formats = formatter.supported_formats
            else:
                self.supported_formats &= formatter.supported_formats

            if session is not None:
                formatter.start(session)
                self.started.add(formatter.key)

        route = self.routes[formatter.key]
        for d in destinations:
            if d not in route:
                d.register(self, formatter)
                route.append(d)
                if session is not None:
                    d.start(session)
                    self.started.add(d._key)

    def _start(self, session):
        assert self.started is None
        self.started = set()

        for f in self.formatters:
            self.started.add(f.key)
            f.start(session)
            for d in self.routes[f.key]:
                self.started.add(d._key)
                d.start(session)

    def register(self, session):
        start = not self.sessions

        wr = weakref.ref(session)
        self.sessions.append(wr)
        i = self.sessions.rfind(wr)
        def unregister():
            try:
                return i.pop
            except SpecialNodeError:
                pass
            if not self.sessions:
                self.flush()

        if start:
            self._start(session)

        return unregister

    def dispatch(self, jobs, *, first=False):
        if not jobs:
            return
        jq = self.job_queue
        if first:
            verb = jq.rextend
        else:
            verb = jq.extend
        verb(jobs)
        self.notify_queue.put(len(jobs))
        if not self.threaded:
            self.drain()

    def drain(self):
        self.execute(False)

    def execute(self, block):
        jq = self.job_queue
        nq = self.notify_queue
        break_if_empty = not block

        while True:
            if break_if_empty and nq.empty():
                break
            count = nq.get()
            for _ in range(count):
                job = jq.rpop()
                if job is None:
                    return
                fn, args = job
                # print(f">> {fn.__self__} {fn.__name__} {args}")
                fn(*args)


    def log(self, message):
        for key, prepared in message.prepared.items():
            formatter = self.formatters_by_key.get(key)
            if formatter is None:
                continue
            rendered = formatter.render(message)
            for destination in self.routes.get(key, ()):
                destination.write(rendered)

    def flush(self):
        if self.threaded:
            blocker = threading.Lock()
            blocker.acquire()
            self.dispatch( [(blocker.release, ())] )
            blocker.acquire()
        else:
            self.drain()

        for destinations in self.routes.values():
            for d in destinations:
                d.flush()

    def reset(self):
        sessions = self.sessions
        while sessions:
            rit = reversed(sessions) # rit points at tail
            rit.next(None)           # rit points to node before tail
            while rit:               # rit is True if it's not head
                wr = rit.rpop()
                session = wr()
                if session is not None:
                    session._close()
        self.flush()

    def atexit(self):
        # If the process is shutting down,
        # Log only aspires to keep everything
        # logged up to that point.
        if self.threaded:
            self._stop_thread()
            return
        self.reset()


STATE_INITIAL = (1, 'initial')
STATE_ACTIVE = (2, 'active')
STATE_DRAINING = (3, 'draining')
STATE_CLOSED = (4, 'closed')

@export
class Session:
    # __slots__ = (
    #     '__weakref__',
    #     'active',
    #     'buffer',
    #     'core',
    #     'clock',
    #     'format',
    #     'fstates',
    #     'handles',
    #     'kwargs',
    #     'name',
    #     'parent',
    #     'paused',
    #     'state',
    #     'upstream',
    #     'unregister_core',
    #     'unregister_parent',
    #     ) + BOUNDINNERCLASS_OUTER_SLOTS

    def __init__(self, name, core, parent, *, buffered, paused, format, kwargs):
        self.name = name
        self.core = core
        self.parent = parent
        self.format = format
        self.buffer = [] if buffered else None
        self.paused = bool(paused)
        self.kwargs = kwargs

        self.clock = core.clock()
        self.state = STATE_INITIAL
        self.active = set()
        self.handles = 0
        self.unregister_core = core.register(self)

        self._fstate_cache = {}
        self._message_fstate_cache = {}

        if parent is None:
            self.upstream = core
            self.unregister_parent = None
            assert format == ''
            assert not kwargs
        else:
            self.upstream = parent
            self.unregister_parent = parent.register(self)


    def __repr__(self):
        if self.buffer is None:
            buffer = "buffer=None"
        else:
            buffer = f"buffer={len(self.buffer)} waiting"
        return f"<Session {hex(id(self))} name={self.name!r} format={self.format!r} state={self.state[1]} {buffer} parent={self.parent}>"

    @BoundInnerClass
    class Message:
        __slots__ = ('time', 'thread', 'format', 'args', 'kwargs', 'prepared')

        def __init__(self, session, time, format, args, kwargs):
            self.time = time
            self.thread = threading.current_thread()
            # if (format != '') and (format not in session.core.supported_formats):
            #     raise ValueError(f"unsupported format {format!r}")
            self.format = format
            self.args = args
            self.kwargs = kwargs
            prepared = self.prepared = {}

            for formatter in session.core.formatters:
                fstate = session.message_fstate(formatter, format)
                prepared[formatter.key] = fstate.prepare(self)

        def __repr__(self):
            return f"<Message time={self.time!r} thread={self.thread!r} format={self.format!r} args={self.args!r} kwargs={self.kwargs!r} prepared={self.prepared!r}>"


    @property
    def closed(self):
        return self.state >= STATE_DRAINING

    @staticmethod
    def subformat(base, format):
        # slight hack:
        # if format is already a tuple, it's absolute, just use it
        if isinstance(format, tuple):
            return format

        if base == '':
            return format
        if isinstance(base, str):
            return (base, format)
        return base + (format,)

    def fstate(self, formatter):
        fstate = self._fstate_cache.get(formatter.key, None)
        if fstate is None:
            parent = self.parent
            if parent is None:
                parent_fstate = None
            else:
                parent_fstate = parent.fstate(formatter)

            self._fstate_cache[formatter.key] = fstate = formatter.State(self.format, parent_fstate)
        return fstate

    def message_fstate(self, formatter, format):
        formatter_cache = self._message_fstate_cache.get(formatter.key, None)
        if formatter_cache is None:
            self._message_fstate_cache[formatter.key] = formatter_cache = {}

        assert format is not None

        message_fstate = formatter_cache.get(format, None)
        if message_fstate is None:
            fstate = self.fstate(formatter)
            format_key = self.subformat(fstate.format, format)
            format_dict = formatter.format(format_key)

            if format_dict is None:
                message_fstate = fstate
            else:
                message_fstate = formatter.State(format_key, fstate)
            formatter_cache[format] = message_fstate
        return message_fstate

    def register(self, o):
        # print(f"register: {self} gets {o}")
        if not isinstance(o, (Log, Child, Session)):
            raise TypeError(f"can't register {o!r}")

        self.handles += 1

        unregistered = False
        def unregister():
            # print(f"unregister: {self} loses {o}")
            nonlocal unregistered
            if unregistered:
                return
            unregistered = True

            self.handles -= 1
            if not self.handles:
                self.core.dispatch( [(self.ensure_state, (STATE_DRAINING,))] )

        return unregister

    def ensure_state(self, desired_state):
        # print(f"{self.name} ensure state {self.state} -> {desired_state}")
        if desired_state < self.state:
            return False
        if desired_state == self.state:
            return True

        if self.state == STATE_INITIAL:
            if desired_state == STATE_ACTIVE:
                self.state = STATE_ACTIVE
                # send start banner
                if self.parent is None:
                    format_key = ('session', 'start')
                    session = self
                else:
                    format_key = self.subformat(self.format, 'start')
                    session = self.parent
                message = session.Message(self.clock.initial, format_key, (), self.kwargs)
                self.core.dispatch( [(self.log, (message,))], first=True)

                return True

        # we already handled initial -> active.
        # if we reach here, we must be going to draining or closed.

        assert desired_state in (STATE_DRAINING, STATE_CLOSED)

        if desired_state == STATE_DRAINING:
            self.state = STATE_DRAINING
            # print("send _close")
            self.core.dispatch( [(self._close, ())] )
            return True

        # print("ensure state closed")
        assert desired_state == STATE_CLOSED
        # send end banner
        time = self.clock()
        if self.parent is None:
            format_key = ('session', 'end')
            session = self
        else:
            format_key = self.subformat(self.format, 'end')
            session = self.parent
        message = session.Message(time, format_key, (), {})
        # self.log(message)
        self.core.dispatch( [(self.log, (message,))], first=True)

        if self.buffer:
            self.flush()

        self.state = STATE_CLOSED

        return True

    def _close(self):
        "Force the session to close.  Internal-only API, only used by reset and atexit."
        self.ensure_state(STATE_CLOSED)

        u = self.unregister_parent
        self.unregister_parent = None
        if u:
            u()

        u = self.unregister_core
        self.unregister_core = None
        if u:
            u()


    def log(self, message):
        self.ensure_state(STATE_ACTIVE)
        if self.buffer is not None:
            self.buffer.append(message)
            return
        self.upstream.log(message)


    def flush(self):
        self.ensure_state(STATE_ACTIVE)
        if self.buffer:
            for message in self.buffer:
                self.upstream.log(message)
            self.buffer.clear()


class LogBase:
    __slots__ = ('_core', '_session', '_clock', '_unregister', '__weakref__', )

    def __init__(self, core, session):
        self._core = core
        self._session = session
        self._unregister = session.register(self)
        self._clock = session.clock

    @property
    def closed(self):
        return not self._session

    def close(self):
        if not self._session:
            return
        self._session = None
        u = self._unregister
        self._unregister = None
        u()

    def flush(self):
        session = self._session
        if session:
            session.flush()

    def child(self, name='', buffered=True, *, format=_USE_DEFAULT, paused=None, **kwargs):
        time = self._clock()

        if format == _USE_DEFAULT:
            format = 'child' if name else None
        # TODO: confirm format is defined

        session = self._session
        if (not session) or (session.state >= STATE_DRAINING):
            return None
        if paused is None:
            paused = session.paused
        return Child(self._core, session, time=time, name=name, buffered=buffered, paused=paused, format=format, kwargs=kwargs)

    def log(self, *args, format='log', **kwargs):
        time = self._clock()

        session = self._session
        if (not session) or (session.state >= STATE_DRAINING):
            return
        message = session.Message(time, format, args, kwargs)
        self._core.dispatch([(session.ensure_state, (STATE_ACTIVE,)), (session.log, (message,)),])

    def write(self, s, format='preformatted'):
        time = self._clock()

        if not isinstance(s, str):
            raise TypeError(f"write() argument must be str, not {type(s).__name__}")

        session = self._session
        if (not session) or (session.state >= STATE_DRAINING):
            return
        message = session.Message(time, format, (s,), {})
        self._core.dispatch([(session.ensure_state, (STATE_ACTIVE,)), (session.log, (message,)),])

    def print(self, *args, sep=' ', end='\n', format='print'):
        time = self._clock()

        if not isinstance(sep, str):
            raise TypeError(f"sep must be str, not {type(sep).__name__}")
        if not isinstance(end, str):
            raise TypeError(f"end must be str, not {type(end).__name__}")

        session = self._session
        if (not session) or (session.state >= STATE_DRAINING):
            return

        s = sep.join(str(o) for o in args) + end
        if s.endswith('\n'):
            s = s[:-1]

        message = session.Message(time, format, (s,), {})
        self._core.dispatch([(session.ensure_state, (STATE_ACTIVE,)), (session.log, (message,)),])

    __call__ = print

    def box(self, s):
        time = self._clock()

        session = self._session
        if (not session) or (session.state >= STATE_DRAINING):
            return

        message = session.Message(time, 'box', (s,), {})
        self._core.dispatch([(session.ensure_state, (STATE_ACTIVE,)), (session.log, (message,)),])


@export
class Child(LogBase):
    __slots__ = ('_core', '_session', '_clock')

    def __init__(self, core, parent_session, *, time=None, name=None, buffered=True, paused=False, format=_USE_DEFAULT, kwargs=None):
        session = Session(name, core, parent_session, buffered=buffered, paused=paused, format=format, kwargs=kwargs)
        clock = session.clock

        super().__init__(core, session)
        self._clock = clock

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()



class Clock:
    """
    Attributes of a Clock instance:
        __call__()
            A high performance clock.  The object returned must support
            __sub__ between two time() values, which produces a "delta".

        initial
            The time at which this Clock was constructed,
            same type as time().

        delta_to_seconds(delta)
            Converts "delta" to float seconds, for presentation
            to the user.

        time_to_timestamp(time)
            Converts time to a timestamp string in the user's time zone.
    """

    def __init__(self):
        c = default_clock
        ns1 = c()
        epoch = time.time()
        ns2 = c()
        self.epoch = epoch

        self.initial = (ns1 + ns2) // 2

    def __call__(self):
        return default_clock()

    def delta_to_seconds(self, delta):
        return delta / 1_000_000_000.0

    def time_to_timestamp(self, time):
        delta = time - self.initial
        seconds = delta / 1_000_000_000.0
        epoch = self.epoch + seconds
        return timestamp_human(epoch)



@export
class Log(LogBase):

    # __slots__ = ()

    def __init__(self,
        *destinations,
        clock=Clock,
        formatter=None,
        name='Log',
        threaded=True,
        # threaded=False,
        paused=False,
        ):

        core = Core(
            name=name,
            clock=Clock,
            threaded=threaded,
            )

        session = Session(name, core, None, buffered=False, format='', paused=paused, kwargs={})
        super().__init__(core, session)

        self.clock = session.clock

        if formatter is None:
            formatter = TextFormatter()
        elif not isinstance(formatter, Formatter):
            raise TypeError(f"formatter must be Formatter, not {type(formatter).__name__}")

        if not destinations:
            destinations = [builtins.print]

        self._route(formatter, destinations)


    def _route(self, formatter, destinations):
        if not isinstance(formatter, Formatter):
            raise TypeError(f"formatter must be Formatter, not {type(formatter).__name__}")
        map_destination = self.map_destination
        self._core.route(formatter, [map_destination(d) for d in destinations])

    def route(self, formatter, *destinations):
        self._route(formatter, destinations)

    @staticmethod
    def map_destination(o):
        if isinstance(o, Destination):
            return o
        if o is builtins.print:
            return Print()
        if callable(o):
            return Callable(o)
        if isinstance(o, list):
            return List(o)

        if isinstance(o, (bytes, str, pathlib.Path)):
            return File(o)
        if isinstance(o, io.TextIOBase):
            return FileHandle(o)
        if o is TMPFILE:
            return TmpFile()
        if o is None:
            return NoneType()

        raise TypeError(f'unsupported destination {o!r}')


mm()
