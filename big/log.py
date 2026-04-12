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
import operator
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


_DEFAULT_CHILD_FORMAT = None

class DefaultChildFormat:
    def __new__(cls):
        global _DEFAULT_CHILD_FORMAT
        if _DEFAULT_CHILD_FORMAT is not None:
            raise ValueError("_DEFAULT_CHILD_FORMAT is a singleton")
        _DEFAULT_CHILD_FORMAT = super().__new__(cls)
        return _DEFAULT_CHILD_FORMAT

    def __repr__(self):
        return "<DefaultChildFormat>"

_DEFAULT_CHILD_FORMAT = DefaultChildFormat()





def _merge_dicts_recurse(base, update, path):
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
        dict_count = base_is_dict + update_is_dict

        if (base_value is None) or (update_value is None) or (not dict_count):
            result[key] = update_value
            continue

        child_path = path + f'[{key!r}]'
        if dict_count == 2:
            result[key] = _merge_dicts_recurse(base_value, update_value, child_path)
            continue

        raise TypeError(f"type mismatch at {child_path} between dict and non-dict")
    return result


def _merge_dicts(base, update):
    """
    Recursively updates base with update.
    Returns a new dict; doesn't modify either base or update.

    The shape of the two dicts must match, to the extent that
    every value in common between the two dicts must be either
    both dicts or neither dicts.  The one exception: one can
    be a dict and the other, None.
    """
    return _merge_dicts_recurse(base, update, '')


_serial_number_lock = threading.Lock()
_serial_number_counter = 1

def _serial_number():
    global _serial_number_counter
    with _serial_number_lock:
        sn = _serial_number_counter
        _serial_number_counter += 1
    return sn



@export
class Optional(tuple):
    def __new__(cls, *elements):
        if not elements:
            raise TypeError("Optional requires at least one path element")
        if not all(isinstance(s, str) for s in elements):
            raise TypeError("Optional path elements must all be str")
        if any(s == '' for s in elements[1:]):
            raise ValueError("'' may only appear at index 0 in a format path")
        return super().__new__(cls, elements)

@export
def format_path(base, format):
    if base is None:
        raise TypeError("base can't be None")
    if format is None:
        return base  # assume base is normalized

    results = []
    optional = False
    for value in (base, format):
        if isinstance(value, str):
            value = (value,)
        else:
            if not value:
                raise ValueError("format path tuples may not be empty")
            if not all(isinstance(element, str) for element in value):
                raise TypeError("format path tuple elements may only be str")
            if '' in value[1:]:
                raise ValueError("'' may only appear at index 0 in a format path")

        optional = optional or isinstance(value, Optional)
        results.append(value)

    base, format = results

    if format[0] == '':
        result = format
    else:
        result = base + format

    if not optional:
        if len(result) == 1:
            return result[0]
        return result
    return Optional(*result)



@export
class Formatter:
    # formats                   # set, or True = accepts any
    # types                     # set of types (str, bytes, SinkEvent, etc.)

    # __slots__ = ('name', 'key', '__weakref__') + BOUNDINNERCLASS_OUTER_SLOTS


    def __init__(self, format_dict, types, *, name=None):
        # self.root = self.owner = None
        if not ((name is None) or isinstance(name, str)):
            raise  TypeError('str must be name or None')

        self.format_dict = format_dict

        def yield_formats(d, path=['']):
            if len(path) == 1:
                assert path == ['']
                yield ''
            else:
                yield tuple(path)

            formats = d.get('formats')
            if not (formats and isinstance(formats, dict)):
                return
            for key, value in formats.items():
                assert isinstance(value, dict)
                path.append(key)
                yield from yield_formats(value, path)
                path.pop()

        self.formats = frozenset(yield_formats(format_dict))
        self.types = types

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
        key_list = list(key)
        key_list.reverse()
        assert key_list[-1] == ''
        key_list.pop()

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
        # key must be an absolute path.
        # so, either '', or a tuple starting with ('', ...).

        if key == '':
            return self.format_dict

        if isinstance(key, list):
            key = tuple(key)
        else:
            assert isinstance(key, tuple)
        assert key[0] == ''
        assert '' not in key[1:]

        cached = self.format_cache.get(key)
        if cached is None:
            format_dict = self.key_to_format_dict(self.format_dict, key)
            if format_dict != None:
                base_key = format_dict.get('base', None)
                if base_key is not None:
                    base_key = format_path(key, base_key)
                    base = self.format(base_key)
                    format_dict = _merge_dicts(base, format_dict)
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
    # owns formats dict, prefix, nesting stack, indentation

    # __slots__ = ('format_dict', 'formats', 'timestamp_format', 'width', 'indents', 'renderers')

    @classmethod
    def format_dict(cls):
        return {
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
                            "template": '╔{double*}╗\n║ {message} start at {timestamp} {space*}║\n {message} {space*}║\n╚{double*}╝\n',
                        },
                        "end" : {
                            'base': '',
                            "template": '╔{double*}╗\n║ {message} finish at {timestamp} {space*}║\n {message} {space*}║\n╚{double*}╝\n',
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
                            # "template": '{prefix}┢━━━━━┱{line*}┐\n{prefix}┃exit ┃ {message}{space*} │\n{prefix}┃     ┃ {message}{space*} │\n{prefix}┃     ┃ {space*} │\n{prefix}┃     ┃ {duration}s{space*} │\n{prefix}┗━━━━━┹{line*}┘\n',
                            "template": '{prefix}┢━━━━━┱{line*}┐\n{prefix}┃exit ┃ {duration}s{space*} │\n{prefix}┗━━━━━┹{line*}┘\n',
                            "space*": ' ',
                            'relaxed': True,
                        },
                    }
                }
            }
        }

    _types = frozenset((str,))

    def __init__(self,
        format_dict=None,
        *,
        name=None,
        width=79,
        ):

        if not isinstance(width, int):
            raise  TypeError('width must be an int and greater than zero')
        if not (width > 0):
            raise ValueError('width must be an int and greater than zero')

        if format_dict is None:
            format_dict = self.format_dict()
        elif not isinstance(format_dict, dict):
            raise TypeError('format_dict must be a dict or None')

        super().__init__(format_dict, self._types, name=name)


        self.width = width
        self.renderers = {}

        self.indent = ''


    class Prepared:
        # __slots__ = ('args', 'kwargs', 'format', 'keys', 'dedup_keys')

        def __init__(self, args, kwargs, fstate):
            self.args = tuple(str(o) for o in args)
            self.kwargs = {name: str(value) for name, value in kwargs.items()}
            self.fstate = fstate

        def __repr__(self):
            return f"<TextFormatter.Prepared fstate={self.fstate!r} args={self.args!r} kwargs={self.kwargs!r}>"

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
            relaxed = bool(format_dict.get('relaxed', False))
            template_renderer = big_template.Formatter(
                format_dict['template'],
                format_dict,
                width=self.width,
                relaxed=relaxed,
                )
            self.renderers[format] = renderers = (prefix_renderer, template_renderer)
        return renderers

    def message_to_priority(self, message, prepared):
        session = self.session
        clock = session.clock
        fstate = prepared.fstate

        d = {
            'elapsed': clock.delta_to_seconds(message.time - session.clock.initial),
            'indent': fstate.indent,
            'name': session.name,
            'thread': message.thread,
            'timestamp': clock.time_to_timestamp(message.time),
            }
        if message.duration is not None:
            d['duration'] = message.duration
        return d

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

@export
def format_dict_to_ascii(d):
    result = {}
    for key, value in d.items():
        if isinstance(value, str) and (key != 'base'):
            value = value.translate(_ascii_translation_table)
        elif isinstance(value, dict):
            value = format_dict_to_ascii(value)
        result[key] = value

    return result


@export
class ASCIIFormatter(TextFormatter):
    """
    A Formatter that renders to bytes objects containing
    ASCII-encoded text.

    This is a subclass of TextFormatter, and most of its
    functionality is just inherited.  For this reason,
    it actually does most of its computation of the log
    messages as str, and only encodes to ASCII at the
    very end.
    """

    _types = frozenset((bytes,))

    @classmethod
    def format_dict(cls):
        return (
            # format_dict_to_bytes(
            format_dict_to_ascii(TextFormatter.format_dict())
            # )
            )

    @BoundInnerClass
    class State(TextFormatter.State):
        def prepare(self, message):
            prepared = super().prepare(message)
            # confirm everybody is happy ascii
            try:
                for s in prepared.args:
                    s.encode('ascii')
                for s in prepared.kwargs.values():
                    s.encode('ascii')
            except UnicodeEncodeError as e:
                return e
            return prepared

    def render(self, message):
        s = super().render(message)
        b = s.encode('ascii')
        return b


@export
class Destination:
    # __slots__ = ('_log', '_formatter', '_session')

    def __init__(self, types):
        self._core = None
        self._formatter = None
        self._session = None
        self._types = types

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

    @property
    def types(self):
        return self._types

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
        super().__init__(types=True)
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

    def __init__(self):
        super().__init__(types=True)

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
        super().__init__(types=True)
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
    def __init__(self):
        super().__init__(types=True)

    def __eq__(self, other):
        return isinstance(other, NoneType)

    def __hash__(self):
        return hash(NoneType) ^ hash(object)

    def __bool__(self):
        return False

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
    time, File uses the "subsequent_mode" passed in;
    if "subsequent_mode" is None, File computes one based
    on initial_mode changed to use "a" (append).
    """
    def __init__(self, path, initial_mode="at", *, buffering=True, encoding=None, subsequent_mode=None):
        message = "initial_mode must be a str, compatible with the mode argument to open(), and must not be read-only"
        if not isinstance(initial_mode, str):
            raise TypeError(message)

        def separate(s, letters):
            count = 0
            matching = []
            non_matching = []
            for c in s:
                (matching if c in letters else non_matching).append(c)
            return ''.join(non_matching), ''.join(matching)

        mode, actions = separate(initial_mode, "rwax")
        mode, plus = separate(mode, '+')
        mode, modes = separate(mode, "bt")

        if (len(actions) > 1) or (actions == 'r') or (len(actions) > 1) or  (len(actions) > 1) or mode:
            raise ValueError(message)

        if subsequent_mode is None:
            subsequent_mode = 'a' + plus + modes

        binary = modes == 'b'
        super().__init__(types=frozenset((bytes if binary else str,)))

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

        self._buffer = buffer = []
        self._binary = binary
        self._join = b''.join if binary else ''.join
        self._buffering = buffering
        self._original_path = original_path
        self._path = path
        self._mode = initial_mode
        self._subsequent_mode = subsequent_mode
        self._encoding = encoding
        self._f = None

    def __repr__(self):
        mode = "binary" if self._binary else "text"
        return f"<File {self._path!r} {mode}>"

    @property
    def binary(self):
        return self._binary

    @property
    def buffering(self):
        return self._buffering

    @property
    def encoding(self):
        return self._encoding

    @property
    def mode(self):
        return self._mode

    @property
    def path(self):
        return self._original_path

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
            self._mode = self._subsequent_mode

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
        contents = self._join(self._buffer)
        self._buffer.clear()
        with self._path.open(self._mode, encoding=self._encoding) as f:
            f.write(contents)
        self._mode = self._subsequent_mode


@export
class FileHandle(Destination):
    def __init__(self, handle, *, autoflush=False):
        if not isinstance(handle, io.IOBase):
            raise TypeError(f"invalid file handle {handle}")
        binary = not isinstance(handle, io.TextIOBase)
        super().__init__(types=frozenset((bytes if binary else str,)))
        self._handle = handle
        self._autoflush = autoflush
        self._binary = binary

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
    When the log is flushed, Buffer will write
    all the log messages to 
    writes that string to the underlying Destination,
    and also flushes the underlying Destination.

    By default, Buffer wraps a Print destination,
    but you may supply your own Destination as a
    positional argument to the constructor.
    """
    def __init__(self, destination=None):
        original_destination = destination
        destination = Log.map_destination(destination) if destination is not None else Print()
        super().__init__(types=destination.types)
        self._buffer = []
        self._original_destination = original_destination
        self._destination = destination

    @property
    def buffer(self):
        return self._buffer

    @property
    def destination(self):
        return self._original_destination

    def __eq__(self, other):
        return isinstance(other, Buffer) and (other._original_destination is self._original_destination)

    def __hash__(self):
        return hash(Buffer) ^ hash(self._destination)

    def write(self, formatted):
        self._buffer.append(formatted)

    def flush(self):
        if self._buffer:
            b = self._buffer
            self._buffer = []
            if isinstance(self._destination, Print) or (self._types == frozenset((str,))):
                message = "".join(b)
                self._destination.write(message)
            elif self._types == frozenset((bytes,)):
                message = b"".join(b)
                self._destination.write(message)
            else:
                for message in b:
                    self._destination.write(message)
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


class NotCalledYet:
    def __repr__(self):
        return "<NotCalledYet>"

_NOT_CALLED_YET = NotCalledYet()
del NotCalledYet

class Job:
    def __init__(self, method, args, involved=None):
        if not ((method is None) or callable(method)):
            raise TypeError("method must be callable, or None")

        if involved is None:
            involveds = []
            append = involveds.append

            if isinstance(method, types.MethodType):
                method_self = method.__self__
                if isinstance(method_self, (Destination, Formatter)):
                    append(method_self)

            for a in args:
                if isinstance(a, (Destination, Formatter)):
                    assert a not in involveds
                    append(a)
            assert len(involveds) <= 1
            if involveds:
                involved = involveds[0]

        self.method = method
        if not isinstance(args, tuple):
            args = tuple(args)
        self.futures = sum(isinstance(a, Job) for a in args)
        self.args = args
        self.exception = None
        self.involved = involved
        self.resets = 0
        self.result = _NOT_CALLED_YET

    def __repr__(self):
        return f"<Job {self.method}{self.args} result={self.result} exception={self.exception} resets={self.resets} involved={self.involved}>"

    def __call__(self):
        if self.result is _NOT_CALLED_YET:
            try:
                if self.futures:
                    args = [_resolve(a) for a in self.args]
                else:
                    args = self.args
                self.result = self.method(*args)
            except Exception as e:
                self.exception = e
        return self.exception

    @property
    def called(self):
        return self.result is not _NOT_CALLED_YET

    def reset(self):
        self.resets += 1
        self.result = _NOT_CALLED_YET
        self.exception = None


def _resolve(o):
    if not isinstance(o, Job):
        return o
    result = o.result
    if result is _NOT_CALLED_YET:
        raise RuntimeError("attempted to resolve {o} before it was called")
    return result


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
        fix,
        name,
        retries,
        threaded,
        ):

        self.clock = clock
        self.fix = fix
        self.name = name
        self.retries = retries
        self.threaded = bool(threaded)

        self.queue = self.Queue(self.threaded)
        self.blockers = []

        self.formatters = linked_list(lock=True)
        self.formatters_by_key = {}
        self.routes = {}
        self.backroutes = {}
        self.fstates = {}
        self.truthy = False
        self.poisoned = None

        self.started = None

        self.configuration_lock = threading.Lock()
        self.sessions = linked_list(lock=True)

        self.formats = True

        atexit.register(self.atexit)

        self.thread = None
        self._start_thread()

    def blocker(self):
        if self.blockers:
            return self.blockers.pop()
        blocker = threading.Lock()
        blocker.acquire()
        return blocker

    def block(self, blocker):
        blocker.acquire()
        self.blockers.append(blocker)

    def _start_thread(self):
        if not (self.threaded and (self.thread is None)):
            return

        self.thread = threading.Thread(target=self.queue.execute, daemon=True, name=f'{self.name} worker')
        self.thread.start()

    def _stop_thread(self):
        if not (self.threaded and (self.thread is not None)):
            return

        thread = self.thread

        # ensure all jobs up to now have been executed
        # blocker = self.blocker()
        # jq.append([blocker.release, (), blocker, 0])
        # nq.put(1)
        # self.block(blocker)
        s = self.Scheduler(wait=True)
        s()

        # flip all sessions to closed
        self.reset()

        self.flush()

        # self.thread = self.job_queue = self.notify_queue = None
        # jq.append([None, (), None, 0])
        # nq.put(1)
        # thread.join()
        s = self.Scheduler(atexit=True)
        s()



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

            if self.formats is True:
                self.formats = formatter.formats
            elif formatter.formats is not True:
                self.formats &= formatter.formats
                if not self.formats:
                    raise ValueError("formatters have no formats in common")

            if session is not None:
                formatter.start(session)
                self.started.add(formatter.key)

        truthy = False
        route = self.routes[formatter.key]
        backroutes = self.backroutes

        for d in destinations:
            if d and (d not in route):
                truthy = True
                d.register(self, formatter)
                route.append(d)
                backroutes[d] = formatter
                if session is not None:
                    d.start(session)
                    self.started.add(d._key)

        if truthy:
            self.truthy = truthy

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
        i = self.sessions.rmatch(lambda v: v is wr)
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


    def execute(self, iterator):
        for job in iterator:
            while True:
                assert not job.called
                fault = job()
                if fault is None:
                    break

                if not isinstance(job.involved, (Formatter, Destination)):
                    # unfixable exception, poisoned
                    self.poisoned = fault
                    break

                if job.resets < self.retries:
                    try:
                        with self.configuration_lock:
                            result = self.fix(involved, fault)
                        if result:
                            job.reset()
                            # retry job!
                            continue
                    except Exception as e:
                        self.poisoned = e
                        break

                # failed to fix the job.

                # remove all jobs where job.involved == involved
                self.queue.remove_involved(involved)

                # unceremoniously remove involved from routing
                if isinstance(involved, Destination):
                    formatter = self.backroutes.get(involved)
                    destinations = (involved,)
                    unregister_formatter = True
                    unregister_destinations = False
                else:
                    isinstance(involved, Formatter)
                    destinations = tuple(reversed(self.routes[formatter.key]))
                    unregister_formatter = False
                    unregister_destinations = True

                route = self.routes[formatter.key]
                for d in destinations:
                    if unregister_destinations:
                        d.unregister()
                    route.remove(d)
                if not route:
                    # formatter has no more destinations, remove it too
                    if unregister_formatter:
                        formatter.unregister()
                    del self.routes[formatter.key]
                    del self.formatters_by_key[formatter.key]
                    self.formatters.remove(formatter)
                break


    @BoundInnerClass
    class Queue:
        def __init__(self, core, block):
            self.core = core
            self.block = bool(block)

            self.lock = threading.Lock()
            self.notify_queue = Queue()
            self.priority_jobs = linked_list(lock=True)
            self.normal_jobs = linked_list(lock=True)
            self.deletions = 0
            self.count = 0

        def __iter__(self):
            return self

        def __next__(self):
            nq = self.notify_queue
            pj = self.priority_jobs
            nj = self.normal_jobs
            break_if_empty = not self.block
            drain = False

            # load
            count = self.count
            deletions = self.deletions

            while True:
                with self.lock:
                    if not count:
                        if break_if_empty and nq.empty():
                            break
                        count = nq.get()

                    while count:
                        if deletions:
                            deletions -= 1
                            continue

                        job = (pj if pj else nj).rpop()
                        count -= 1

                        if drain:
                            if isinstance(job.involved, threading.Lock):
                                job.involved.release()
                            continue

                        if job.method is None:
                            # stop processing
                            assert not job.args
                            drain = True
                            break_if_empty = True
                            continue

                        # spill
                        self.count = count
                        self.deletions = deletions
                        return job

            # spill
            self.count = count
            self.deletions = deletions
            raise StopIteration

        def append(self, job, *, priority=False):
            (self.priority_jobs if priority else self.normal_jobs).append(job)
            self.notify_queue.put(1)

        def extend(self, jobs, *, priority=False):
            if not jobs:
                return
            (self.priority_jobs if priority else self.normal_jobs).extend(jobs)
            self.notify_queue.put(len(jobs))

        def remove(self, predicate):
            with self.lock:
                deletions = 0
                for q in (self.priority_jobs, self.normal_jobs):
                    i = iter(q)
                    while True:
                        i = i.match(predicate)
                        if i is None:
                            break
                        deletions += 1
                        i.rpop()

                self.deletions += deletions

        def remove_involved(self, involved):
            self.remove(lambda job: job.involved is involved)

        def execute(self):
            self.core.execute(self)

        def drain(self):
            assert not self.block
            self.execute()



    @BoundInnerClass
    class Scheduler:
        def __init__(self, core, *args, atexit=False, priority=False, wait=False):
            """
            Manages creating "jobs" iterables and scheduling the work.  To use:

                s = core.schedule() # returns a Scheduler
                s(fn, arg1, arg2)   # adds fn(arg1, arg2) to our local job list
                s()                 # schedules all the jobs on the local job list

            You can call s with arguments as many times as you like, to schedule
            multiple jobs.  There's also a shortcut if you're only scheduling one job:

                core.schedule(fn, arg1, arg2)

            schedule/Scheduler also takes four keyword-only boolean parameters
            which guide its behavior:

            * atexit - if true, and Log is in threaded mode,
                schedules a final None so the worker thread will exit.
                also, passes in a "blocker" so we can wait
                until the worker thread has finished.
                atexit creates a job.

            * priority - if true,
                these jobs are high priority and should be run sooner.
                default is False, the jobs are normal priority.

            * wait - if true,
                wait until all this scheduled work is completed:
                * in non-threaded mode, this is the same as drain.
                * in threaded mode, this blocks until the worker thread
                  processes every job queued by the scheduler.
                wait creates a job.
            """
            self.core = core
            self.jobs = []
            self.atexit = atexit
            self.priority = priority

            threaded = self.core.threaded
            self.drain = not threaded
            self.block = block = threaded and wait
            assert not (atexit and block)

            if args:
                self(*args)
                self()

        def __bool__(self):
            return bool(self.jobs)

        def execute(self):
            jobs = self.jobs
            self.jobs = []
            self.core.execute(jobs)

        def __call__(self, method=None, *args, involved=None):
            if method is not None:
                # append a job
                if isinstance(method, Job):
                    assert not args
                    assert involved is None
                    job = method
                else:
                    job = Job(method, args, involved)

                self.jobs.append(job)
                return

            # schedule
            core = self.core
            queue = core.queue

            jobs = self.jobs
            atexit = self.atexit
            drain = self.drain
            blocker = None

            if self.block:
                blocker = core.blocker()
                jobs.append(Job(blocker.release, (), involved=blocker))
            else:
                blocker = None

            if atexit:
                jobs.append(Job(None, ()))

            assert jobs
            self.jobs = []

            queue.extend(jobs, priority=self.priority)

            if blocker:
                core.block(blocker)

            if drain:
                core.queue.drain()

            if atexit:
                core.thread.join()


    def log(self, message):
        s = self.Scheduler(priority=True)
        for key, prepared in message.prepared.items():
            formatter = self.formatters_by_key.get(key)
            if formatter is None:
                continue
            destinations = self.routes.get(formatter.key, ())
            if destinations:
                render_job = Job(formatter.render, (message,))
                s(render_job)
                for destination in destinations:
                    s(destination.write, render_job)
        if s:
            s()

    def flush(self):
        s = self.Scheduler(priority=True, wait=True)
        for destinations in self.routes.values():
            for d in destinations:
                s(d.flush)
        s()

    def reset(self):
        sessions = self.sessions
        s = self.Scheduler()
        while sessions:
            rit = reversed(sessions) # rit points at tail
            rit.next(None)           # now rit points to node before tail
            while rit:               # rit is True if it's not head
                wr = rit.rpop()
                session = wr()
                if session is not None:
                    s(session._close)
        s()
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
STATE_CLOSED = (3, 'closed')

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

    def __init__(self, name, core, parent, *, buffered, clock, format, kwargs, paused):
        assert not isinstance(format, Optional)

        self.name = name
        self.core = core
        self.parent = parent
        self.format = format
        self.buffer = [] if buffered else None
        self.paused = int(bool(paused))
        self.kwargs = kwargs

        clock = clock or core.clock()
        self.clock = clock

        self.thread = threading.current_thread()
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
        __slots__ = ('time', 'thread', 'format', 'args', 'kwargs', 'prepared', 'duration')

        def __init__(self, session, time, format, args, kwargs, duration=None, thread=None):
            core = session.core

            format = format_path(session.format, format)
            if format not in core.formats:
                if isinstance(format, Optional):
                    format = session.format
                else:
                    raise ValueError(f"format {format} not defined for all formatters")

            self.time = time
            self.thread = thread or threading.current_thread()
            self.format = format
            self.args = args
            self.kwargs = kwargs
            self.prepared = prepared = {}
            self.duration = duration

            for formatter in core.formatters:
                fstate = session.message_fstate(formatter, format)
                s = core.Scheduler()
                prepare_job = Job(fstate.prepare, (self,), involved=formatter)
                s(prepare_job)
                s.execute()
                result = prepare_job.result
                if isinstance(result, Exception):
                    raise result
                prepared[formatter.key] = result

        def __repr__(self):
            return f"<Message time={self.time!r} thread={self.thread!r} format={self.format!r} args={self.args!r} kwargs={self.kwargs!r} prepared={self.prepared!r} duration={self.duration!r}>"


    @property
    def closed(self):
        return self.state >= STATE_CLOSED

    def pause(self):
        self.paused += 1

    def resume(self):
        if self.paused > 1:
            self.paused -= 1
            return

        # clamp to zero
        self.paused = 0


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
            format_key = format_path(fstate.format, format)

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
                self.core.Scheduler(self._close)

        return unregister

    def ensure_state(self, desired_state):
        if self.core.threaded and (threading.current_thread() != self.core.thread):
            raise RuntimeError("change state not from worker thread")
        if desired_state < self.state:
            return False
        if desired_state == self.state:
            return True
        # print(f"[S] {self.name!r}: {self.state!r} -> {desired_state!r} :: thread {threading.current_thread().name!r}")

        if self.state == STATE_INITIAL:
            if desired_state == STATE_CLOSED:
                # go directly to closed, skip start and end banners
                self.state = STATE_CLOSED
                return True

            assert desired_state == STATE_ACTIVE
            self.state = STATE_ACTIVE
            # send start banner
            if self.parent is None:
                format_key = ('', 'session', 'start')
                session = self
            else:
                format_key = format_path(self.format, 'start')
                session = self.parent
            message = session.Message(self.clock.initial, format_key, (self.name,), self.kwargs, thread=self.thread)
            # print(f"[S] {message}")
            # self.core.Scheduler(self.log, message)
            self.log(message)
            return True

        assert self.state == STATE_ACTIVE
        assert desired_state == STATE_CLOSED
        self.state = STATE_CLOSED
        # send end banner
        clock = self.clock
        time = clock()
        if self.parent is None:
            format_key = ('', 'session', 'end')
            session = self
            duration = None
        else:
            format_key = format_path(self.format, 'end')
            session = self.parent
            duration = clock.delta_to_seconds(time - clock.initial)
        message = session.Message(time, format_key, (self.name,), {}, thread=self.thread, duration=duration)
        # print(f"[S] {message}")
        # self.core.Scheduler(self.log, message)
        self.log(message)

        if self.buffer:
            self.flush()

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
    __slots__ = ('_core', '_clock', '_helper_cache', '_name', '_session', '_unregister', '__weakref__', )

    def __init__(self, name, core, session, paused):
        self._name = name
        self._core = core
        self._session = session
        self._helper_cache = {}

        self._unregister = session.register(self)
        self._clock = session.clock

    def __bool__(self):
        return self._core.truthy

    def __getattr__(self, attr):
        # is this the name of a user-defined format?
        format = ('', attr)
        core = self._core
        if format in core.formats:
            cached = self._helper_cache.get(attr, None)
            if cached is None:
                def helper(s):
                    return self.log(s, format=Optional(attr))
                self._helper_cache[attr] = cached = helper
            return cached
        raise AttributeError(f"{type(self).__name__!r} object has no attribute {attr!r}")

    @property
    def name(self):
        return self._name

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
        if self._core.poisoned:
            raise self._core.poisoned
        session = self._session
        if session:
            self._core.Scheduler(session.flush, wait=True)

    @property
    def paused(self):
        "Returns True if the handle is paused, None if the log is closed, and otherwise False."
        if self._core.poisoned:
            raise self._core.poisoned
        if not self._session:
            return None
        return bool(self._paused)

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
        if self._core.poisoned:
            raise self._core.poisoned
        session = self._session
        if session is not None:
            self._core.Scheduler(session.pause)

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
        if self._core.poisoned:
            raise self._core.poisoned
        session = self._session
        if session is not None:
            self._core.Scheduler(session.resume)

    def child(self, name='', buffered=True, *, format=_DEFAULT_CHILD_FORMAT, paused=None, **kwargs):
        time = self._clock()

        session = self._session
        core = self._core

        if (not session) or (session.state >= STATE_CLOSED):
            return None
        return Child(name, self._core, session, time=time, buffered=buffered, paused=paused, format=format, kwargs=kwargs)

    def log(self, *args, format=Optional('log'), **kwargs):
        time = self._clock()

        if self._core.poisoned:
            raise self._core.poisoned

        session = self._session
        if (not session) or (session.state >= STATE_CLOSED):
            return
        message = session.Message(time, format, args, kwargs)
        s = self._core.Scheduler()
        s(session.ensure_state, STATE_ACTIVE)
        s(session.log, message)
        s()

    def write(self, s, format=Optional('preformatted')):
        time = self._clock()

        if not isinstance(s, str):
            raise TypeError(f"write() argument must be str, not {type(s).__name__}")

        if self._core.poisoned:
            raise self._core.poisoned

        session = self._session
        if (not session) or (session.state >= STATE_CLOSED):
            return
        message = session.Message(time, format, (s,), {})
        s = self._core.Scheduler()
        s(session.ensure_state, STATE_ACTIVE)
        s(session.log, message)
        s()

    def print(self, *args, sep=' ', end='\n', format=Optional('print')):
        time = self._clock()

        if not isinstance(sep, str):
            raise TypeError(f"sep must be str, not {type(sep).__name__}")
        if not isinstance(end, str):
            raise TypeError(f"end must be str, not {type(end).__name__}")

        if self._core.poisoned:
            raise self._core.poisoned

        session = self._session
        if (not session) or (session.state >= STATE_CLOSED):
            return

        s = sep.join(str(o) for o in args) + end
        if s.endswith('\n'):
            s = s[:-1]

        message = session.Message(time, format, (s,), {})
        s = self._core.Scheduler()
        s(session.ensure_state, STATE_ACTIVE)
        s(session.log, message)
        s()

    __call__ = print


class Child(LogBase):
    __slots__ = ('_core', '_session', '_clock')

    def __init__(self, name, core, parent_session, *, time=None, buffered=True, paused=False, format=_DEFAULT_CHILD_FORMAT, kwargs=None):
        if time is None:
            time = parent_session.clock()

        if not isinstance(name, str):
            raise TypeError(f'name must be str, not {type(name).__name__}')

        if format == _DEFAULT_CHILD_FORMAT:
            format = ('', 'child') if name else None
        else:
            if isinstance(format, Optional):
                raise ValueError("Child format can't be Optional")
            format = format_path(parent_session.format, format)

        if (core.formats is not True) and (format not in core.formats):
            raise ValueError(f"{format} is not defined by all formatters")

        if core.poisoned:
            raise core.poisoned

        if paused is None:
            paused = parent_session.paused

        session = Session(name, core, parent_session, buffered=buffered, clock=parent_session.clock, format=format, kwargs=kwargs, paused=paused)
        clock = session.clock

        super().__init__(name, core, session, paused)
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
def default_fix(o, fault):
    pass


@export
class Log(LogBase):

    # __slots__ = ()

    def __init__(self,
        *destinations,
        buffered=False,
        clock=Clock,
        fix=default_fix,
        formatter=None,
        name='Log',
        paused=False,
        retries=1,
        threaded=True,
        ):

        retries = operator.index(retries)
        if retries < 1:
            raise ValueError('retries must be >= 1')

        core = Core(
            name=name,
            clock=Clock,
            fix=fix,
            retries=retries,
            threaded=bool(threaded),
            )

        session = Session(name, core, None, buffered=buffered, clock=None, format='', kwargs={}, paused=paused)
        super().__init__(name, core, session, paused)

        self.clock = session.clock

        if formatter is None:
            formatter = TextFormatter()
        elif not isinstance(formatter, Formatter):
            raise TypeError(f"formatter must be Formatter, not {type(formatter).__name__}")
        self._formatter = formatter

        if not destinations:
            destinations = [builtins.print]

        self._route(formatter, destinations)

    @property
    def formatter(self):
        return self._formatter

    def _route(self, formatter, destinations):
        if not isinstance(formatter, Formatter):
            raise TypeError(f"formatter must be Formatter, not {type(formatter).__name__}")
        if not destinations:
            raise ValueError("must specify at least one destination")

        ds = [self.map_destination(d) for d in destinations]

        # confirm that each destination.write can handle all types returned by formatter.render
        failures = []
        append = failures.append
        assert isinstance(formatter._types, (set, frozenset, bool))
        for d in ds:
            if d._types is True:
                continue
            if formatter._types is True:
                append(d)
            assert isinstance(d._types, (set, frozenset))
            if not (formatter._types <= d._types):
                append(d)
        if failures:
            incompatible_destinations = ", ".join(repr(d) for d in failures)
            raise TypeError(f"formatter {formatter!r} can't be routed to {incompatible_destinations}")

        self._core.route(formatter, ds)

    def route(self, formatter, *destinations):
        if self._core.poisoned:
            raise self._core.poisoned
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
