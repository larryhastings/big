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
import inspect
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
from .types import linked_list, SpecialNodeError


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


# threading.Lock is a factory function, not a class, before
# Python 3.13--so isinstance(x, threading.Lock) raises TypeError
# there.  the *type* of an instance works on every version.
_LockType = type(_serial_number_lock)



@export
class Optional(str):
    """
    A format name that falls back silently.

    Wrap a format name in Optional and, if the named format isn't
    defined by every routed formatter, the message quietly uses the
    session's default format instead of raising ValueError.
    """
    __slots__ = ()



# Session is defined before the formatters, so LogFormatter's
# accepts parameter can default to frozenset((Session.Message,)).


class Session:
    __slots__ = (
        'core',

        '_fstate_cache',
        '_live_cache',
        '_message_fstate_cache',
        '_pause_lock',
        'active',
        'buffer',
        'clock',
        'depth',
        'format',
        'handles',
        'initial',
        'kwargs',
        'name',
        'parent',
        'paused',
        'serial',
        'state',
        'thread',
        'unregister_core',
        'unregister_parent',
        'upstream',

        ) + ('__weakref__',) + BOUNDINNERCLASS_OUTER_SLOTS

    def __init__(self, core, name, parent, *, buffered, clock, format, kwargs, paused):
        assert not isinstance(format, Optional)

        self.core = core
        self.name = name
        self.parent = parent
        self.format = format
        self.buffer = [] if buffered else None
        self.paused = int(bool(paused))
        self.kwargs = kwargs

        clock = clock or core.clock()
        self.clock = clock
        # a root session begins when its clock begins; a child
        # session begins when it's created.  (children share the
        # parent's clock, so clock.initial would be log-start time.)
        self.initial = clock.initial if parent is None else clock()

        self.thread = threading.current_thread()
        self.state = STATE_INITIAL
        self._pause_lock = threading.Lock()
        # epoch-checked cache for _live: (pause_epoch, value).
        # -1 never matches a real epoch, so the first read computes.
        self._live_cache = (-1, False)
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
            with core.configuration_lock:
                core.session_generation += 1
                self.serial = core.session_generation
            self.depth = 0
        else:
            self.upstream = parent
            self.unregister_parent = parent.register(self)
            self.serial = parent.serial
            self.depth = parent.depth + 1


    def __repr__(self):
        if self.buffer is None:
            buffer = "buffer=None"
        else:
            buffer = f"buffer={len(self.buffer)} waiting"
        return f"<Session {hex(id(self))} name={self.name!r} format={self.format!r} state={self.state[1]} {buffer} parent={self.parent}>"

    @property
    def closed(self):
        return self.state >= STATE_CLOSED

    def pause(self):
        # guarded: the counter must update correctly under
        # concurrent pause/resume from multiple threads.
        # (reads of self.paused stay bare--stale is acceptable,
        # torn is impossible.)
        with self._pause_lock:
            self.paused += 1
        # after the mutation, never before (see bump_pause_epoch)
        self.core.bump_pause_epoch()

    def resume(self):
        with self._pause_lock:
            if self.paused > 1:
                self.paused -= 1
            else:
                # clamp to zero
                self.paused = 0
        self.core.bump_pause_epoch()

    @property
    def paused_in_tree(self):
        # pause is hierarchical: a session is paused if it or any
        # ancestor is paused.  this is PULL (walk the parents at
        # check time), not PUSH (notify the children at pause time),
        # deliberately: pause is a pure read-time predicate with no
        # per-session side effects, so pulling is correct by
        # construction--there's no propagation event to miss, no
        # child registry to maintain, and pause()/resume() stay
        # local and O(1).  (if pause ever grows side effects--
        # "pause also flushes", "pause notifies destinations"--this
        # must become an inform-the-tree push protocol instead.)
        session = self
        while session is not None:
            if session.paused:
                return True
            session = session.parent
        return False

    @property
    def _live(self):
        # "would a message logged on this session right now be
        # delivered?"--open, and neither this session nor any
        # ancestor paused.  the pause half is cached, validated
        # against the core's pause epoch (bumped by every pause and
        # resume anywhere in the log), so the ancestor walk runs
        # only on the first read after pause state changed
        # somewhere--the only time the answer can differ.  the
        # cache is a single tuple assignment: stale is acceptable,
        # torn is impossible.
        if self.state >= STATE_CLOSED:
            return False
        epoch = self.core.pause_epoch
        cached_epoch, unpaused = self._live_cache
        if cached_epoch != epoch:
            unpaused = not self.paused_in_tree
            self._live_cache = (epoch, unpaused)
        return unpaused

    def fstate(self, formatter):
        fstate = self._fstate_cache.get(formatter.key, None)
        if fstate is None:
            parent = self.parent
            if parent is None:
                parent_fstate = None
            else:
                parent_fstate = parent.fstate(formatter)

            self._fstate_cache[formatter.key] = fstate = formatter.State(self.format, parent_fstate, child=(self.parent is not None))
        return fstate

    def message_fstate(self, formatter, format):
        formatter_cache = self._message_fstate_cache.get(formatter.key, None)
        if formatter_cache is None:
            self._message_fstate_cache[formatter.key] = formatter_cache = {}

        assert format is not None

        message_fstate = formatter_cache.get(format, None)
        if message_fstate is None:
            fstate = self.fstate(formatter)
            format_dict = formatter.format(format)

            if format_dict is None:
                message_fstate = fstate
            else:
                message_fstate = formatter.State(format, fstate)
            formatter_cache[format] = message_fstate
        return message_fstate

    def register(self, o):
        # print(f"register: {self} gets {o}")
        if not isinstance(o, (Log, Child, Session)):
            raise TypeError(f"can't register {o!r}")

        # handles is a cross-thread refcount: two threads closing
        # their *own* (different) child handles concurrently is
        # legal, and both decrement this session's counter.  a bare
        # += is a read-modify-write that loses updates under
        # preemption (observed on 3.6-3.9), so it's guarded--by the
        # core's configuration_lock, which nothing holds while
        # calling register/unregister.
        with self.core.configuration_lock:
            self.handles += 1

        unregistered = False
        def unregister(time=None):
            # print(f"unregister: {self} loses {o}")
            # time is when the user closed the handle; it stamps
            # the end/exit banner if this unregister closes the
            # session.
            nonlocal unregistered
            if unregistered:
                return
            unregistered = True

            # decrement-and-test atomically; schedule _close
            # outside the lock (keep the critical section to the
            # counter itself).
            with self.core.configuration_lock:
                self.handles -= 1
                closing = not self.handles
            if closing:
                self.core.Scheduler(self._close, time)

        return unregister

    def ensure_state(self, desired_state, time=None):
        # time stamps the end/exit banner when closing: the moment
        # the *user* closed the log, threaded down from the entry
        # point--not whenever this job got around to running.  None
        # means nobody upstream noted the time (reset, atexit); then
        # it's noted here.
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
            # send start banner (unless that format is disabled)
            if self.parent is None:
                format_key = 'start'
                session = self
            else:
                format_key = 'enter'
                session = self.parent
            if format_key in self.core.formats:
                message = session.Message(self.initial, format_key, (self.name,), self.kwargs, thread=_EMPTY_THREAD)
                # print(f"[S] {message}")
                self.log(message)
            return True

        assert self.state == STATE_ACTIVE
        assert desired_state == STATE_CLOSED
        self.state = STATE_CLOSED
        # send end banner (unless that format is disabled)
        clock = self.clock
        if time is None:
            time = clock()
        if self.parent is None:
            format_key = 'end'
            session = self
            duration = None
        else:
            format_key = 'exit'
            session = self.parent
            duration = clock.delta_to_seconds(time - self.initial)
        if format_key in self.core.formats:
            message = session.Message(time, format_key, (self.name,), {}, thread=_EMPTY_THREAD, duration=duration)
            # print(f"[S] {message}")
            self.log(message)

        if self.buffer:
            self.flush()

        return True

    def _close(self, time=None):
        "Force the session to close.  Internal-only API, only used by reset and atexit."
        # a child session always shows its enter and exit banners,
        # even if nothing was ever logged inside it.  (a root session
        # that never logged anything stays silent--if you never
        # actually log, Log never writes to your destinations.)
        if self.parent is not None:
            self.ensure_state(STATE_ACTIVE)
        self.ensure_state(STATE_CLOSED, time)

        u = self.unregister_parent
        self.unregister_parent = None
        if u:
            u(time)

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

    @BoundInnerClass
    class Message:
        __slots__ = (
            'args',
            'depth',
            'duration',
            'format',
            'kwargs',
            'prepared',
            'session_serial',
            'thread',
            'time',
            )

        def __init__(self, session, time, format, args, kwargs, duration=None, thread=None):
            core = session.core

            # a format is a name, or None for the session default.
            # Optional names fall back to the default silently.
            if format is None:
                format = session.format
            elif format not in core.formats:
                if isinstance(format, Optional):
                    format = session.format
                else:
                    raise ValueError(f"format {format!r} not defined for all formatters")

            self.time = time
            self.thread = thread or threading.current_thread()
            self.format = format
            self.args = args
            self.kwargs = kwargs
            self.prepared = prepared = {}
            self.duration = duration
            self.session_serial = session.serial
            self.depth = session.depth

            for formatter in core.formatters:
                fstate = session.message_fstate(formatter, format)
                s = core.Scheduler()
                prepare_job = Job(fstate.prepare, (self,), involved=formatter)
                s.add(prepare_job)
                s.execute()
                prepared[formatter.key] = prepare_job.result

        def __repr__(self):
            return f"<Message time={self.time!r} thread={self.thread!r} format={self.format!r} args={self.args!r} kwargs={self.kwargs!r} prepared={self.prepared!r} duration={self.duration!r}>"



@export
class LogFormatter:
    # formats                   # set, or True = accepts any
    # types                     # set of types (str, bytes, SinkEvent, etc.)

    # deliberately no __slots__: LogFormatter is a base class users
    # subclass (TextFormatter, SinkFormatter, Filter, and their own
    # custom formatters), and a slotted base is an unkindness to
    # subclassers--it silently constrains their attributes and their
    # own slots.  (its subclasses in this module stay unslotted too.)


    def __init__(self, format_dict, types, *, accepts=frozenset((Session.Message,)), name=None):
        # the accepts default: a formatter consumes log Messages,
        # so it belongs at the top level.  accepting anything is
        # something you have to say out loud: accepts=True.
        if not ((name is None) or isinstance(name, str)):
            raise TypeError('name must be str or None')
        if not ((accepts is True) or isinstance(accepts, (set, frozenset))):
            raise TypeError('accepts must be True or a set of types')

        # format_dict may be None: a formatter that doesn't render
        # from a format tree at all (SinkFormatter produces
        # structured events, not text).  Such a formatter has no
        # named formats, and format() returns None for every name.
        self.format_dict = format_dict

        # a format is a str name; '' names the root template.
        # the namespace is flat--but '.' is reserved in names, so
        # a future need for nesting can give 'child.start' nested
        # *semantics* as a pure addition, with no interface change
        # and no possible collision with existing user names.
        names = {''}
        formats = format_dict.get('formats') if format_dict else None
        if formats and isinstance(formats, dict):
            for key, value in formats.items():
                assert isinstance(value, dict)
                if '.' in key:
                    raise ValueError(f"format name {key!r} is invalid: '.' is reserved for future namespacing")
                names.add(key)
        self.formats = frozenset(names)
        self.types = types
        # the types this formatter accepts as input.  a top-level
        # formatter is fed log Messages; a formatter downstream of
        # another formatter is fed its parent's renderings.  True
        # accepts anything.
        self.accepts = accepts

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

    def format(self, name):
        # name is a str format name; '' (or None) names the root.
        # returns the format's dict (with its 'base' merged in),
        # or None if the format isn't defined--or if this formatter
        # has no format tree at all (format_dict is None).
        if not name:
            return self.format_dict
        assert isinstance(name, str)
        if self.format_dict is None:
            return None

        cached = self.format_cache.get(name)
        if cached is None:
            format_dict = self.format_dict.get('formats', {}).get(name)
            if format_dict is not None:
                base_name = format_dict.get('base', None)
                if base_name is not None:
                    base = self.format(base_name)
                    format_dict = _merge_dicts(base, format_dict)
            cached = self.format_cache[name] = format_dict
        return cached

    # bound inner class: constructed as formatter.State(...);
    # the owning formatter is injected as the first argument.
    @BoundInnerClass
    class State:
        def __repr__(self):
            return f"<State formatter={self.formatter} format={self.format!r} parent={self.parent!r}>"

        def __init__(self, formatter, format, parent=None, *, child=False):
            self.formatter = formatter
            self.format = format
            self.format_dict = formatter.format(format)
            self.parent = parent

        def prepare(self, message):
            raise NotImplementedError

    def render(self, message):
        raise NotImplementedError


@export
def prefix_format(time_seconds_width, time_fractional_width, thread_name_width=12, *, ascii=False):
    """
    Formats a "prefix" string for use with a Log object.

    The format it returns is in the form:
        "[{elapsed} {thread.name}] "
    formatted with these widths:
         "[{time_seconds_width}.{time_fractional_width} {thread_name_width}]"
    For example, TextFormatter's default prefix is prefix_format(3, 10, 12),
    which looks like this in the final log:
        "[003.0706368860   MainThread]"

    The current nesting indent is applied by the render pipeline,
    after the prefix--prefixes don't need to request it.  (A custom
    template that wants the indent somewhere exotic can still
    interpolate {indent} itself.)
    """
    # the +1 is for the dot between seconds and fractional seconds
    time_width = time_seconds_width + 1 + time_fractional_width
    prefix = f'{{elapsed:0{time_width}.{time_fractional_width}f}} {{thread.name:>{thread_name_width}}}│ '
    if ascii:
        prefix = prefix.translate(_ascii_translation_table)
    return prefix


@export
class Filter(LogFormatter):
    """
    Base class for filters: formatters that sit downstream of
    another formatter, transforming--or dropping--its rendered
    output.

    Subclass Filter and override render(value): return the value,
    transformed to taste, or None to drop this message for the
    filter's whole subtree.  Or use Filter directly, wrapping a
    callable with the same contract:

        log.route(log.formatter, a, Filter(boring), c)

    By default a Filter consumes and produces str, so it can sit
    under any text formatter--or under another Filter.  To filter
    other types, pass accepts (what the filter consumes) and/or
    types (what it produces)--each may be a type, a set of types,
    or True meaning anything--or simply annotate your callable:
    the annotation on its first positional parameter declares what
    it accepts, and its return annotation declares what it
    produces.  An explicit parameter wins over an annotation, and
    str is the default when there's neither.  For example, a
    filter that consumes an ASCIIFormatter's bytes and produces
    str:

        def unbyte(b: bytes) -> str:
            return b.decode('ascii')
    """

    def __init__(self, filter=None, *, accepts=None, name=None, types=None):
        if not ((filter is None) or callable(filter)):
            raise TypeError('filter must be callable, or None')
        if name is None:
            name = getattr(filter, '__name__', None)

        # explicit accepts/types win.  when either is unspecified,
        # the filter's annotations declare it: the first positional
        # parameter's annotation is what it accepts, the return
        # annotation is what it produces--and str is the default
        # when there's no annotation either.  the annotation
        # objects come straight from the signature; a callable
        # inspect can't get a signature from (some builtins) just
        # gets the defaults.
        compute_accepts = accepts is None
        compute_types = types is None
        if compute_accepts or compute_types:
            annotated_accepts = annotated_produces = str
            if filter is not None:
                try:
                    signature = inspect.signature(filter)
                except (TypeError, ValueError):
                    signature = None
                if signature is not None:
                    for parameter in signature.parameters.values():
                        # only the first parameter, and only if
                        # it's positional
                        if ((parameter.kind in (parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD))
                            and (parameter.annotation is not parameter.empty)):
                            annotated_accepts = parameter.annotation
                        break
                    if signature.return_annotation is not signature.empty:
                        annotated_produces = signature.return_annotation
            if compute_accepts:
                accepts = annotated_accepts
            if compute_types:
                types = annotated_produces

        # each may be a single type, a set of types, or True
        # (meaning anything); normalize the single type to a set
        if not ((accepts is True) or isinstance(accepts, (set, frozenset))):
            accepts = {accepts}
        if not ((types is True) or isinstance(types, (set, frozenset))):
            types = {types}

        super().__init__({}, types, accepts=accepts, name=name)
        self.filter = filter

    def render(self, value):
        if self.filter is None:
            raise NotImplementedError('subclass Filter and override render, or construct it with a callable')
        return self.filter(value)


# the root of every format tree: the prefix, the plain-message
# template, and the starred fill characters banners draw with.
# the builders below copy this and add a 'formats' sub-tree.
# (a plain module-level dict, copied per build--not a factory
# function; there's nothing to compute, it's just data.)
_base_format_dict = {
    "prefix": prefix_format(3, 10, 12),
    'template': '{prefix}{message}\n',

    "double*": '═',
    "line*": '─',
    "heavy*": '━',
    "pad*": ' ',
}


@export
def unicode_format_dict(*, closed=False):
    """
    The unicode format tree, with box-drawing characters.
    This is the default format tree for TextFormatter.

    By default the art is "open": boxes and banners have no
    right-hand border, and the enter/exit banners' label cells
    have no lid.  Open art renders correctly even when your
    viewer substitutes box-drawing glyphs from a different-width
    font--a vertical stroke only ever needs to align with
    another vertical stroke that has identical characters to
    its left.

    Pass closed=True for fully closed boxes--right borders,
    lids, corners.  Beautiful when your font renders box-drawing
    characters at the same width as everything else; ragged on
    the right when it doesn't.  (If a line's content overflows
    the width, its right border is omitted rather than drawn
    glued onto the overflow.)
    """
    d = dict(_base_format_dict)
    if closed:
        d["formats"] = {
            "box" : {
                'base': '',
                "template": '{prefix}┌{line*}┐\n{prefix}│ {message}{pad*}│\n{prefix}└{line*}┘\n',
            },
            "box2" : {
                'base': '',
                "template": '{prefix}╔{double*}╗\n{prefix}║ {message}{pad*}║\n{prefix}╚{double*}╝\n',
            },
            "start": {
                'base': '',
                "template": '{prefix}╔{double*}╗\n{prefix}║ {message} start at {timestamp}{pad*}║\n{prefix}╚{double*}╝\n',
            },
            "end" : {
                'base': '',
                "template": '{prefix}╔{double*}╗\n{prefix}║ {message} finish at {timestamp}{pad*}║\n{prefix}╚{double*}╝\n',
            },
            # note the *two* '{message}' lines: for a one-line
            # message, the second line simply isn't rendered;
            # for a multi-line message, the second line renders
            # all the subsequent lines.
            "enter": {
                'base': '',
                "template": '{prefix}┏━━━━━┳{heavy*}┓\n{prefix}┃enter┃ {message}{pad*}┃\n{prefix}┃     ┃ {message}{pad*}┃\n{prefix}┗━━━━━┻{heavy*}┛\n',
            },
            "exit": {
                'base': '',
                "template": '{prefix}┏━━━━━┳{heavy*}┓\n{prefix}┃exit ┃ {message}{pad*}┃\n{prefix}┃     ┃ {message}{pad*}┃\n{prefix}┗━━━━━┻{heavy*}┛\n',
            },
            "preformatted": {
                'base': '',
                "template": '{message}',
                "verbatim": True,
            },
        }
        return d

    d["formats"] = {
        "box" : {
            'base': '',
            "template": '{prefix}┌{line*}\n{prefix}│ {message}\n{prefix}└{line*}\n',
        },
        "box2" : {
            'base': '',
            "template": '{prefix}╔{double*}\n{prefix}║ {message}\n{prefix}╚{double*}\n',
        },
        "start": {
            'base': '',
            "template": '{prefix}╔{double*}\n{prefix}║ {message} start at {timestamp}\n{prefix}╚{double*}\n',
        },
        "end" : {
            'base': '',
            "template": '{prefix}╔{double*}\n{prefix}║ {message} finish at {timestamp}\n{prefix}╚{double*}\n',
        },
        # the label cell has no lid: its vertical strokes exist
        # only in the text rows, where "enter" vs five spaces
        # align in any font.  (a lid would be all box-drawing
        # characters, whose total width under font substitution
        # differs from the text rows'--the classic ragged-box
        # effect.)  note the *two* '{message}' lines: for a
        # one-line message, the second line simply isn't
        # rendered; for a multi-line message, the second line
        # renders all the subsequent lines.
        "enter": {
            'base': '',
            "template": '{prefix}┏{heavy*}\n{prefix}┃enter┃ {message}\n{prefix}┃     ┃ {message}\n{prefix}┗{heavy*}\n',
        },
        "exit": {
            'base': '',
            "template": '{prefix}┏{heavy*}\n{prefix}┃exit ┃ {message}\n{prefix}┃     ┃ {message}\n{prefix}┗{heavy*}\n',
        },
        # write() logs with this format:
        # the message, completely as-is--no prefix, no nothing
        "preformatted": {
            'base': '',
            "template": '{message}',
            "verbatim": True,
        },
    }
    return d


def _t_style_format_dict():
    """
    (internal) The classic open art with T junctions on the
    enter/exit banners.  In a single font, T junctions are
    safe--which is why this is the source of the open *ASCII*
    art--but under box-drawing font substitution the lid
    misaligns, so the open unicode art dropped it.
    """
    d = dict(_base_format_dict)
    d["formats"] = {
        "box" : {
            'base': '',
            "template": '{prefix}┌{line*}\n{prefix}│ {message}\n{prefix}└{line*}\n',
        },
        "box2" : {
            'base': '',
            "template": '{prefix}╔{double*}\n{prefix}║ {message}\n{prefix}╚{double*}\n',
        },
        "start": {
            'base': '',
            "template": '{prefix}╔{double*}\n{prefix}║ {message} start at {timestamp}\n{prefix}╚{double*}\n',
        },
        "end" : {
            'base': '',
            "template": '{prefix}╔{double*}\n{prefix}║ {message} finish at {timestamp}\n{prefix}╚{double*}\n',
        },
        "enter": {
            'base': '',
            "template": '{prefix}┏━━━━━┱{line*}\n{prefix}┃enter┃ {message}\n{prefix}┃     ┃ {message}\n{prefix}┡━━━━━┹{line*}\n',
        },
        "exit": {
            'base': '',
            "template": '{prefix}┢━━━━━┱{line*}\n{prefix}┃exit ┃ {message}\n{prefix}┃     ┃ {message}\n{prefix}┗━━━━━┹{line*}\n',
        },
        "preformatted": {
            'base': '',
            "template": '{message}',
            "verbatim": True,
        },
    }
    return d


@export
def ascii_format_dict(*, closed=False):
    """
    The ASCII format tree.  Pure ASCII always aligns--every
    character comes from the same font--so the open art keeps
    the enter/exit label lids (the T junctions render as '+'),
    and closed=True gives you fully closed boxes that align on
    every terminal ever made.
    """
    if closed:
        return format_dict_to_ascii(unicode_format_dict(closed=True))
    return format_dict_to_ascii(_t_style_format_dict())


@export
class TextFormatter(LogFormatter):
    # owns formats dict, prefix, nesting stack, indentation

    _types = frozenset((str,))

    def __init__(self,
        format_dict=None,
        *,
        formats=None,
        indent='    ',
        name=None,
        prefix=None,
        width=79,
        ):

        if not isinstance(width, int):
            raise TypeError('width must be an int and greater than zero')
        if not (width > 0):
            raise ValueError('width must be an int and greater than zero')
        if not isinstance(indent, str):
            raise TypeError('indent must be str')

        if format_dict is None:
            format_dict = unicode_format_dict()
        elif not isinstance(format_dict, dict):
            raise TypeError('format_dict must be a dict or None')
        else:
            # never mutate the caller's dict: prefix= overwrites,
            # formats= adds and deletes.  (deepcopy, not
            # _merge_dicts(format_dict, {}): merging with an empty
            # dict shares every nested dict instead of copying it.)
            format_dict = copy.deepcopy(format_dict)

        if prefix is not None:
            if not isinstance(prefix, str):
                raise TypeError('prefix must be str or None')
            format_dict['prefix'] = prefix

        if formats:
            if not isinstance(formats, dict):
                raise TypeError('formats must be a dict or None')
            format_formats = format_dict.setdefault('formats', {})
            for key, value in formats.items():
                if not isinstance(key, str):
                    raise TypeError(f'format names must be str, not {type(key).__name__}')
                if '.' in key:
                    raise ValueError(f"format name {key!r} is invalid: '.' is reserved for future namespacing")
                if value is None:
                    # None means "this format is disabled":
                    # remove it from the tree entirely.
                    if key not in format_formats:
                        raise ValueError(f"can't disable format {key!r}, it isn't defined")
                    del format_formats[key]
                    continue
                if not isinstance(value, dict):
                    raise TypeError(f'formats[{key!r}] must be a dict or None')
                if 'message' in value:
                    raise ValueError(f"formats[{key!r}] must not contain 'message'")
                template = value.get('template')
                if template is None:
                    raise ValueError(f"formats[{key!r}] must contain 'template'")
                if not isinstance(template, str):
                    raise TypeError(f"formats[{key!r}]['template'] must be str, not {type(template).__name__}")
                existing = format_formats.get(key)
                if existing:
                    value = _merge_dicts(existing, value)
                else:
                    value = dict(value)
                    value.setdefault('base', '')
                # trial-construct the renderer now, so template errors
                # (e.g. non-contiguous {message} lines) are reported
                # here, not at first render.  the trial map includes
                # the root values, so templates can use the root's
                # starred interpolations (e.g. {line*}).
                trial_map = {k: v for k, v in format_dict.items() if not isinstance(v, dict)}
                trial_map.update({k: v for k, v in value.items() if k not in ('base', 'template', 'relaxed', 'verbatim')})
                big_template.Formatter(template, trial_map, width=width)
                format_formats[key] = value

        super().__init__(format_dict, self._types, name=name)


        self.width = width
        self.renderers = {}

        self.indent = indent


    class Prepared:
        __slots__ = ('args', 'kwargs', 'fstate')

        def __init__(self, args, kwargs, fstate):
            self.args = tuple(str(o) for o in args)
            self.kwargs = {name: str(value) for name, value in kwargs.items()}
            self.fstate = fstate

        def __repr__(self):
            return f"<TextFormatter.Prepared fstate={self.fstate!r} args={self.args!r} kwargs={self.kwargs!r}>"

    @BoundInnerClass
    class State(LogFormatter.State):
        def __init__(self, formatter, format, parent=None, *, child=False):
            # our bound LogFormatter.State parent injects formatter itself
            super().__init__(format, parent, child=child)

            if parent is None:
                parent_indent = ''
            else:
                parent_indent = parent.indent
            # a *child session's* State adds one level of indent.
            # message-level States (created per-format on top of a
            # session State) inherit their parent's indent unchanged.
            self.indent = parent_indent + (formatter.indent if child else '')

        def prepare(self, message):
            return self.formatter.Prepared(message.args, message.kwargs, self)

    def get_renderers(self, prepared):
        fstate = prepared.fstate
        format = fstate.format
        renderers = self.renderers.get(format)
        if renderers is None:
            format_dict = fstate.format_dict
            prefix_renderer = format_dict.get('prefix', '').format_map
            # relaxed by default: a template with no {message} lines
            # (e.g. a banner that only shows the timestamp) simply
            # discards the message instead of raising.
            relaxed = bool(format_dict.get('relaxed', True))
            template_renderer = big_template.Formatter(
                format_dict['template'],
                format_dict,
                width=self.width,
                relaxed=relaxed,
                stretch=False,
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
        # the current nesting indent rides along after the prefix
        priority['prefix'] = prefix_renderer(priority) + prepared.fstate.indent
        lines = list(prepared.args)
        if prepared.kwargs:
            lines.extend(f'{name}={value}' for name, value in prepared.kwargs.items())
        message_text = '\n'.join(lines)
        s = template_renderer(message=message_text, **priority)
        if prepared.fstate.format_dict.get('verbatim'):
            # a verbatim format skips the cleanup below: no rstrip,
            # no appended newline.  write()'s 'preformatted' format
            # is verbatim--"completely as-is" means completely.
            return s
        # log lines never have trailing whitespace,
        # and always end with a newline
        s = '\n'.join(line.rstrip() for line in s.split('\n'))
        if not s.endswith('\n'):
            s += '\n'
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
    '┳': '+',
    '┻': '+',
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
    A LogFormatter that renders to bytes objects containing
    ASCII-encoded text.

    This is a subclass of TextFormatter, and most of its
    functionality is just inherited.  For this reason,
    it actually does most of its computation of the log
    messages as str, and only encodes to ASCII at the
    very end.

    Messages containing non-ASCII characters can't crash the
    log--or your program.  They're encoded with backslash
    escapes: log('café') renders as b'caf\\xe9'.  Nothing
    fails, nothing is lost.
    """

    _types = frozenset((bytes,))

    def __init__(self, format_dict=None, **kwargs):
        # ASCIIFormatter's default tree is the open ASCII art, not
        # TextFormatter's open unicode.  otherwise it's a TextFormatter.
        if format_dict is None:
            format_dict = ascii_format_dict()
        super().__init__(format_dict, **kwargs)

    def render(self, message):
        s = super().render(message)
        # backslashreplace: non-ASCII characters become escapes
        # instead of exceptions.  a log statement must never
        # crash the program it's observing, and unrouting the
        # whole formatter over one accented character would be
        # a cure worse than the disease.
        b = s.encode('ascii', 'backslashreplace')
        return b


@export
class SinkEvent:
    """
    Base class for the events produced by SinkFormatter
    (and by Sink itself, for its start/end lifecycle).

    Common attributes:
        session       the log generation this event belongs to
                      (1 for a Log's first session; reset increments)
        ns            the event's time, in monotonic clock time
        epoch         the event's time, in seconds-since-the-epoch
        duration      how long until the next event, in nanoseconds.
                      computed when you iterate over a Sink;
                      0 for a bare event.  duration is *not*
                      considered by __eq__.
        type          the event type name, a str

    Events are ordered by ns.
    """

    type = None
    _fields = ('session', 'ns', 'epoch')

    def __init__(self, session, ns, epoch, *, duration=0):
        self.session = session
        self.ns = ns
        self.epoch = epoch
        self.duration = duration

    def _key(self):
        return tuple(getattr(self, field) for field in self._fields)

    def __eq__(self, other):
        if not isinstance(other, SinkEvent):
            return NotImplemented
        return (type(self) is type(other)) and (self._key() == other._key())

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __lt__(self, other):
        if not isinstance(other, SinkEvent):
            raise TypeError(f"'<' not supported between instances of {type(self).__name__!r} and {type(other).__name__!r}")
        return self.ns < other.ns

    def __hash__(self):
        # not _key(): fields like SinkStartEvent.configuration
        # may be unhashable (dicts)
        return hash((type(self), self.session, self.ns, self.epoch))

    def __repr__(self):
        fields = ', '.join(f'{field}={getattr(self, field)!r}' for field in self._fields)
        return f'{type(self).__name__}({fields}, duration={self.duration!r})'

    def _clone_kwargs(self):
        return {field: getattr(self, field) for field in self._fields if field not in ('session', 'ns', 'epoch')}

    def _calculate_duration(self, next_event):
        "Returns a clone of self, with duration = next_event.ns - self.ns."
        clone = type(self)(self.session, self.ns, self.epoch, duration=next_event.ns - self.ns, **self._clone_kwargs())
        return clone


@export
class SinkStartEvent(SinkEvent):
    "The log started (a new session began)."
    type = 'start'
    elapsed = 0
    _fields = ('session', 'ns', 'epoch', 'configuration')

    def __init__(self, session, ns, epoch, configuration, *, duration=0):
        super().__init__(session, ns, epoch, duration=duration)
        self.configuration = configuration


@export
class SinkEndEvent(SinkEvent):
    "The log ended (the session closed)."
    type = 'end'
    _fields = ('session', 'ns', 'epoch', 'elapsed')

    def __init__(self, session, ns, epoch, elapsed, *, duration=0):
        super().__init__(session, ns, epoch, duration=duration)
        self.elapsed = elapsed


@export
class SinkLogEvent(SinkEvent):
    "A log message."
    type = 'log'
    _fields = ('session', 'ns', 'epoch', 'elapsed', 'depth', 'format', 'message', 'thread')

    def __init__(self, session, ns, epoch, elapsed, depth, format, message, thread, *, duration=0):
        super().__init__(session, ns, epoch, duration=duration)
        self.elapsed = elapsed
        self.depth = depth
        self.format = format
        self.message = message
        self.thread = thread


@export
class SinkWriteEvent(SinkLogEvent):
    "A preformatted write."
    type = 'write'


@export
class SinkEnterEvent(SinkLogEvent):
    "An enter banner: a nested block opened."
    type = 'enter'


@export
class SinkExitEvent(SinkLogEvent):
    "An exit banner: a nested block closed."
    type = 'exit'


@export
class SinkFormatter(LogFormatter):
    """
    A LogFormatter that renders log messages into SinkEvent objects.

    Structured logging isn't a special pathway in big.log--it's
    just a LogFormatter whose render type is SinkEvent instead of str.
    Route a SinkFormatter to a Sink (or any destination whose types
    accept SinkEvent) and you receive the log as a stream of event
    objects instead of rendered text.

    A SinkFormatter does no text formatting whatsoever--it isn't a
    TextFormatter and has no format tree.  Its events carry the log's
    *structured* fields (message, depth, format, thread, timing); how
    to render those into text, if at all, is the consumer's business.

    (Log creates one of these automatically when you pass it a
    destination that wants SinkEvents, e.g. a Sink.)
    """

    _types = frozenset((SinkEvent,))

    _format_to_event_class = {
        'enter': SinkEnterEvent,
        'exit': SinkExitEvent,
        'preformatted': SinkWriteEvent,
    }

    def __init__(self, *, formats=None, name=None):
        # no format tree: format_dict is None.  but a SinkFormatter
        # still has format *names*--they're structural metadata (they
        # end up as event.format and drive the enter/exit/start/end
        # banner machinery), not templates.  the companion SinkFormatter
        # Log builds for a text formatter borrows that formatter's
        # names, so the same log statements (log.box, log.enter, ...)
        # produce the same structured events.
        super().__init__(None, self._types, name=name)
        if formats is not None:
            self.formats = frozenset(formats)

    def format(self, name):
        # no templates, but the State machinery needs a non-None
        # format_dict for a name to build a *per-format* State (one
        # that carries .format); otherwise message_fstate collapses
        # every format down to the session State.  return an empty
        # marker dict for any name we know, None for names we don't.
        if (not name) or (name in self.formats):
            return {}
        return None

    class Prepared:
        __slots__ = ('args', 'kwargs')

        def __init__(self, args, kwargs):
            self.args = tuple(str(o) for o in args)
            self.kwargs = {name: str(value) for name, value in kwargs.items()}

        def __repr__(self):
            return f"<SinkFormatter.Prepared args={self.args!r} kwargs={self.kwargs!r}>"

    @BoundInnerClass
    class State(LogFormatter.State):
        def prepare(self, message):
            return self.formatter.Prepared(message.args, message.kwargs)

    def render(self, message):
        prepared = message.prepared[self.key]
        lines = list(prepared.args)
        if prepared.kwargs:
            lines.extend(f'{name}={value}' for name, value in prepared.kwargs.items())
        message_text = '\n'.join(lines)

        clock = self.session.clock
        cls = self._format_to_event_class.get(message.format, SinkLogEvent)
        return cls(
            message.session_serial,
            message.time,
            clock.epoch + clock.delta_to_seconds(message.time - clock.initial),
            clock.delta_to_seconds(message.time - clock.initial),
            message.depth,
            message.format,
            message_text,
            message.thread,
            )


@export
class LogDestination:
    # deliberately no __slots__: LogDestination is a base class users
    # subclass, and a slotted base is an unkindness to subclassers
    # (it silently constrains their attributes and their own slots).

    # A list of callables used to extend Log.map_destination.
    # Each mapper is called with the destination object; it should
    # return a LogDestination, or None meaning "not mine, keep
    # looking".  User-registered mappers run before the built-in
    # mappings.  This is a single shared registry: append your
    # mapper to LogDestination.mappers.
    mappers = []

    def __init__(self, types=True):
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
        return f'<{type(self).__name__} {registered} {active}>'

    @property
    def types(self):
        return self._types

    @property
    def core(self):
        return self._core

    @property
    def owner(self):
        "The Log this destination is currently attached to, or None."
        core = self._core
        return core.owner if core is not None else None

    @property
    def formatter(self):
        return self._formatter

    @property
    def session(self):
        return self._session

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
        # virtual; subclasses must override.
        # (NotImplementedError is a subclass of RuntimeError.)
        raise NotImplementedError()

    def flush(self):
        pass




@export
class Callable(LogDestination):
    """
    A LogDestination wrapping a callable.

    Calls the callable for every formatted log message.
    """

    def __init__(self, callable):
        super().__init__(types=True)
        self._callable = callable

    @property
    def callable(self):
        return self._callable

    def __eq__(self, other):
        return isinstance(other, Callable) and (other._callable is self._callable)

    def __hash__(self):
        # id(), not hash(): __eq__ compares the callable by
        # *identity*, so hashing by identity is exactly consistent--
        # and a bound method of an unhashable object (a list's
        # .append, say) isn't even hashable before Python 3.8.
        return hash(Callable) ^ id(self._callable)

    def write(self, o):
        self._callable(o)


@export
class Print(LogDestination):

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
class List(LogDestination):

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
class NoneType(LogDestination):
    """
    A LogDestination wrapping None.  Does nothing.
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
class File(LogDestination):
    """
    A LogDestination wrapping a file in the filesystem.

    This LogDestination writes to a file in the filesystem,
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

        if (
            (len(actions) != 1) or (actions == 'r')
            or (len(plus) > 1) or (len(modes) > 1)
            or mode
            ):
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
        # fallible work first, lifecycle commit last: if the open
        # raises, the session was never recorded, so a fix() that
        # repairs the filesystem gets a clean retry.  (committing
        # first turned the retry into "can't start, it was already
        # started"--the double-start guard firing on the fault
        # ladder's legitimate second attempt.)
        f = None if self._buffering else self._path.open(self._mode, encoding=self._encoding)
        super().start(session)
        self._f = f

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
        with self._path.open(self._mode, encoding=self._encoding) as f:
            f.write(contents)
        # clear only after the write succeeded: a transient failure
        # repaired by fix() retries this flush, and the payload must
        # still be here for the retry.  (if the write itself fails
        # partway, a successful retry can append the payload again--
        # we prefer possible duplication to certain loss.)
        self._buffer.clear()
        self._mode = self._subsequent_mode


@export
class FileHandle(LogDestination):
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


@export
class Buffer(LogDestination):
    """
    A LogDestination that buffers log messages before sending them to another LogDestination.

    This LogDestination wraps another arbitrary
    LogDestination, referred to as the "underlying"
    LogDestination.

    Every time a formatted log message is logged,
    Buffer appends it to an internal buffer (a Python list).
    When the log is flushed, Buffer joins all the buffered
    messages into one string, writes that string to the
    underlying LogDestination, and flushes the underlying
    LogDestination.

    Buffer owns the underlying destination's lifecycle: register,
    start, end, and unregister are forwarded to it.  So stateful
    destinations work underneath a Buffer--a File opens its file,
    a TmpFile computes its filename, a Sink records its start and
    end events.

    By default, Buffer wraps a Print destination,
    but you may supply your own LogDestination as a
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

    # lifecycle forwarding: the underlying destination lives and
    # dies with the Buffer.  in every method the underlying goes
    # first and our own state commits last--the underlying is the
    # fallible part (start is where File meets the filesystem), and
    # a failed forward must leave the Buffer un-transitioned so the
    # fault ladder's retry gets a clean second attempt.

    def register(self, core, formatter):
        self._destination.register(core, formatter)
        super().register(core, formatter)

    def unregister(self):
        self._destination.unregister()
        super().unregister()

    def start(self, session):
        self._destination.start(session)
        super().start(session)

    def end(self):
        # deliver anything still buffered before ending the
        # underlying: end is the last exit for the user's data.
        # (flush also flushes the underlying, so a buffered File
        # underneath has written its file before its end() runs.)
        self.flush()
        self._destination.end()
        super().end()

    def __eq__(self, other):
        return isinstance(other, Buffer) and (other._original_destination is self._original_destination)

    def __hash__(self):
        return hash(Buffer) ^ hash(self._destination)

    def write(self, formatted):
        self._buffer.append(formatted)

    def flush(self):
        # failure-atomic: the buffer is only emptied as writes
        # succeed, so a transient failure repaired by fix() retries
        # with the payload intact.
        b = self._buffer
        if b:
            if isinstance(self._destination, Print) or (self._types == frozenset((str,))):
                message = "".join(b)
                self._destination.write(message)
                b.clear()
            elif self._types == frozenset((bytes,)):
                message = b"".join(b)
                self._destination.write(message)
                b.clear()
            else:
                # one at a time, popping after each success: a
                # mid-loop failure retries only the unwritten tail,
                # no duplicates.
                while b:
                    self._destination.write(b[0])
                    del b[0]
        # unconditional: when the log says flush, the underlying
        # gets flushed--including on a retry whose write already
        # succeeded (the underlying's flush was what faulted).
        self._destination.flush()


@export
class TmpFile(File):
    """
    A LogDestination that writes to a timestamped temporary file.

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

    def __init__(self, prefix='{name}', *, buffering=True, encoding=None, timestamp_format=None):
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

    def register(self, core, formatter):
        super().register(core, formatter)
        self._name = core.name
        self._rendered_prefix = self._prefix.format(name=self._name)

    def start(self, session):
        # compute the real timestamped path FIRST: super().start()
        # (File.start) opens self._path immediately when unbuffered,
        # and it must open the real file, not the construction-time
        # placeholder.  (buffered mode never noticed the old order:
        # it opens at flush time, after the reassignment.)
        assert self._core
        clock = session.clock

        if self._timestamp_format is None:
            log_timestamp = clock.time_to_timestamp(clock.initial)
        else:
            log_timestamp = self._timestamp_format(clock.epoch)
        log_timestamp = log_timestamp.replace("/", "-").replace(":", "-").replace(" ", ".")
        thread = threading.current_thread()

        tmpfile = f"{self._rendered_prefix}.{log_timestamp}.{os.getpid()}.{thread.name}.txt"
        tmpfile = translate_filename_to_exfat(tmpfile)
        tmpfile = tmpfile.replace(" ", '_')
        self._path = pathlib.Path(tempfile.gettempdir()) / tmpfile

        super().start(session)

@export
class Sink(LogDestination):
    """
    A LogDestination that records the log as a list of SinkEvent
    objects, instead of rendering it as text.  Useful for tests
    and for programs that consume their own logs.

    Route a Sink into a Log and you get:
      * a SinkStartEvent when logging starts,
      * a SinkLogEvent / SinkWriteEvent / SinkEnterEvent /
        SinkExitEvent per message (rendered by the SinkFormatter
        the Log creates automatically), and
      * a SinkEndEvent when the log closes.

    Iterating over a Sink yields its events, with each event's
    "duration" computed as the time until the following event
    (the last event's duration is 0).

    A Sink accumulates: after a Log.reset(), new events are
    recorded after the old ones, and each event's "session"
    generation counter tells you which session it belongs to.
    Call sink.clear() for a clean slate.
    """
    def __init__(self):
        super().__init__(types=frozenset((SinkEvent,)))
        self.events = []
        self._serial = None
        self._clock = None

    def __eq__(self, other):
        return other is self

    def __hash__(self):
        return hash(Sink) ^ id(self)

    def __bool__(self):
        return True

    def __iter__(self):
        events = self.events
        for event, next_event in zip(events, events[1:]):
            yield event._calculate_duration(next_event)
        if events:
            yield events[-1]

    def __len__(self):
        return len(self.events)

    def start(self, session):
        super().start(session)
        clock = session.clock
        self._serial = session.serial
        self._clock = clock
        self.events.append(SinkStartEvent(session.serial, clock.initial, clock.epoch, {}))

    def end(self):
        super().end()
        clock = self._clock
        ns = clock()
        elapsed = clock.delta_to_seconds(ns - clock.initial)
        self.events.append(SinkEndEvent(self._serial, ns, clock.epoch + elapsed, elapsed))

    def write(self, event):
        if event is None:
            return
        self.events.append(event)

    def clear(self):
        """Discards every recorded event."""
        self.events.clear()

    def print(self, *, print=None):
        "Prints every event in the sink.  Pass print= to use a different callable."
        if print is None:
            print = builtins.print
        for event in self:
            print(event)


@export
class OldDestination(LogDestination):
    """
    A LogDestination providing backwards compatibility with the
    pre-0.13 big.log.Log interface.  Accumulates events for
    later iteration or printing.

    Each accumulated event is a list:
        [start, elapsed, event, depth]
    where start and elapsed are integer nanoseconds, event is
    a str, and depth is the enter() nesting depth.

    (Internally this is now a thin shim consuming SinkEvents.)
    """

    def __init__(self):
        super().__init__(types=frozenset((SinkEvent,)))
        self.longest_event = 0
        self.reset()

    def __eq__(self, other):
        return other is self

    def __hash__(self):
        return hash(OldDestination) ^ id(self)

    def __bool__(self):
        return True

    def reset(self):
        self.stack = []
        self.events = []
        self.previous_event = None
        self._initial = 0

    def _event(self, elapsed, event):
        if self.previous_event:
            previous_event = self.previous_event
            previous_event[1] = elapsed - previous_event[0]
        e = self.previous_event = [elapsed, 0, event, len(self.stack)]
        self.events.append(e)

        self.longest_event = max(self.longest_event, len(event))

    def start(self, session):
        super().start(session)
        self.reset()
        self._initial = session.clock.initial
        self._event(0, "log start")

    def write(self, event):
        if event is None:
            return
        # elapsed as exact integer nanoseconds
        elapsed = event.ns - self._initial
        type = event.type
        if type == 'enter':
            self._event(elapsed, event.message + " start")
            self.stack.append(event.message)
            return
        if type == 'exit':
            subsystem = self.stack.pop()
            self._event(elapsed, subsystem + " end")
            return
        if event.format in ('start', 'end'):
            # banner text; the lifecycle "log start" event covers it
            return
        # SinkEvents carry no formatted text; reproduce the classic
        # 1.0 line ourselves.  the old formatter used prefix='' and
        # indent='  ', so a message at depth N was rendered as two
        # spaces per level of nesting followed by the message text.
        # (a preformatted write was verbatim: no nesting indent.)
        if event.type == 'write':
            message = event.message
        else:
            message = '  ' * event.depth + event.message
        self._event(elapsed, message.rstrip('\n'))

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
    A drop-in replacement for the pre-0.13 big.log.Log class.

    This creates a Log, populates it with an OldDestination,
    and exposes the old big.log.Log interface.  Provided for
    backwards compatibility, as a stepping-stone to make it
    easier to transition to the new Log.
    """

    def __init__(self, clock=None):
        self._destination = OldDestination()
        clock = clock or default_clock
        formatter = TextFormatter(formats={"start": None, "end": None}, prefix='', indent='  ')
        self._log = Log(self._destination, threaded=False, formatter=formatter, clock=clock)

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


TMPFILE = object()
export("TMPFILE")

class NotCalledYet:
    def __repr__(self):
        return "<NotCalledYet>"

_NOT_CALLED_YET = NotCalledYet()
del NotCalledYet

# the default for Job's involved parameter: infer the involved node
# from the method and arguments.  pass involved=None explicitly to
# say "nothing is involved"--a fault in such a job is unattributable
# and poisons the log, rather than being blamed on (and unrouting)
# whatever node happened to appear in the arguments.
_INFER_INVOLVED = object()

class Job:
    def __init__(self, method, args, involved=_INFER_INVOLVED):
        if not ((method is None) or callable(method)):
            raise TypeError("method must be callable, or None")

        if involved is _INFER_INVOLVED:
            involved = None
            involveds = []
            append = involveds.append

            if isinstance(method, types.MethodType):
                method_self = method.__self__
                if isinstance(method_self, (LogDestination, LogFormatter)):
                    append(method_self)

            for a in args:
                if isinstance(a, (LogDestination, LogFormatter)):
                    assert a not in involveds
                    append(a)
            assert len(involveds) <= 1
            if involveds:
                involved = involveds[0]

        self.method = method
        if not isinstance(args, tuple):
            args = tuple(args)
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
                self.result = self.method(*self.args)
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


class Core:
    __slots__ = (
        '__weakref__',
        'backroutes', 'blockers', 'clock', 'configuration_lock',
        'dirty', 'exited', 'fix', 'formats', 'formatters',
        'formatters_by_key', 'fstates', 'name', 'owner',
        'pause_epoch', 'poisoned',
        'queue', 'retries', 'routes', 'session_generation', 'sessions',
        'started', 'thread', 'threaded', 'truthy',
        ) + BOUNDINNERCLASS_OUTER_SLOTS


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

        # Threading invariants (the comment of record):
        #
        # 1. Session state transitions (ensure_state, _close) happen
        #    only on the executor: the worker thread when threaded,
        #    the draining thread when not.  (Asserted in ensure_state.)
        # 2. Routing mutations (route, the fault handler's unroute,
        #    _start/_end) hold configuration_lock.  It's a plain Lock,
        #    and the discipline that keeps it one: NEVER call foreign
        #    code--LogFormatter/LogDestination lifecycle methods, the user's
        #    fix() callback--while holding it.  Mutate the tables under
        #    the lock; collect the callbacks; call them after release.
        #    (A plain Lock *enforces* this: violate it and you deadlock
        #    in testing, instead of an RLock letting it rot.)
        # 3. Small cross-thread flags: session pause counters are
        #    guarded by a per-session lock (pause() must be
        #    synchronously visible); session handle refcounts are
        #    guarded by configuration_lock (see Session.register);
        #    "dirty" is only ever *written* on the executor;
        #    "truthy" is recomputed under configuration_lock
        #    whenever a destination is added to or removed from the
        #    routes (bare reads may be stale, torn is impossible).
        # 4. Scheduler(wait=True) is forbidden on the executor
        #    (Core.flush downgrades automatically).
        # 5. Log/Child *handles* may be logged to from any thread,
        #    but structural operations on one handle (close, reset,
        #    enter/exit, route) from concurrent threads are undefined.
        self.queue = self.Queue(self.threaded)
        self.blockers = []

        self.formatters = linked_list(lock=True)
        self.formatters_by_key = {}
        self.routes = {}
        self.backroutes = {}
        self.fstates = {}
        self.truthy = False
        self.pause_epoch = 0
        self.poisoned = None
        self.dirty = False
        self.exited = False

        self.started = None

        self.configuration_lock = threading.Lock()
        self.sessions = linked_list(lock=True)
        # "generation" counter: incremented per *root* session.
        # (a Log's first session is generation 1; each reset increments.)
        self.session_generation = 0

        self.formats = True

        # the Log that owns this core (set by Log.__init__);
        # surfaced to users via LogDestination.owner
        self.owner = None

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
        s = self.Scheduler(wait=True)
        s()

        # flip all sessions to closed
        self.reset()

        # barrier: wait for the _close jobs (normal lane) to run.
        # the last session's unregister--inside its _close job--
        # schedules _end, so once this barrier releases, _end is
        # already in the normal lane.  the atexit None below is
        # appended after it, so _end always runs before drain mode
        # starts discarding.  (the flush waits above and below
        # prove nothing here: they wait on priority-lane blockers,
        # which the worker services before the normal lane.)
        s = self.Scheduler(wait=True)
        s()

        self.flush()

        s = self.Scheduler(atexit=True)
        s()



    def route(self, parent, children):
        # mutate the routing tables under the lock; run the
        # (foreign) register/start lifecycle methods after releasing
        # it, as per-node attributed jobs through the fault ladder.
        # see the threading invariants in __init__.
        #
        # routing is a TREE: the log feeds top-level formatters,
        # every other node is fed its parent's renderings, and a
        # node can only have one parent.  children may be
        # Destinations (leaves) or Formatters (which may get
        # children of their own via a later route() call).
        jobs = []
        with self.configuration_lock:
            # if we've already started logging, newly routed
            # formatters and destinations get started immediately
            if self.started is not None:
                try:
                    session = self.sessions[0]()
                except IndexError: # pragma: no cover
                    session = None
            else:
                session = None

            if parent.key not in self.routes:
                # a formatter we've never routed: it becomes a
                # top-level formatter, fed log messages directly.
                # (a formatter attached as a child already has a
                # routes entry, made when it was attached.)
                # all validation happens *first*, so a ValueError
                # leaves the routing tables untouched.
                if parent.core is not None:
                    raise ValueError(f"{parent!r} is already registered to another log")
                if self.formats is True:
                    formats = parent.formats
                elif parent.formats is not True:
                    formats = self.formats & parent.formats
                    if not formats:
                        raise ValueError("formatters have no formats in common")
                else:
                    formats = self.formats
                self.formats = formats

                self.formatters.append(parent)
                self.formatters_by_key[parent.key] = parent
                self.routes[parent.key] = []
                jobs.append(Job(self._enroll_node, (parent, None, session), involved=parent))

            route = self.routes[parent.key]
            backroutes = self.backroutes

            # validate every child FIRST, then mutate: route() is
            # atomic--a ValueError leaves the routing tables (and
            # the lifecycle jobs) untouched.  (the `child in
            # accepted` term preserves the silent skip of a child
            # passed twice in one call, which the mutating loop
            # used to provide via `child in route`.)
            accepted = []
            for child in children:
                if (not child) or (child in route) or (child in accepted):
                    continue
                existing_parent = backroutes.get(child)
                if existing_parent is not None:
                    raise ValueError(f"{child!r} already has a parent ({existing_parent!r}); a node can only have one parent")
                if isinstance(child, LogFormatter):
                    if child.key in self.routes:
                        # it's already a top-level formatter;
                        # it can't also be somebody's child.
                        raise ValueError(f"{child!r} is already routed at the top level; a node can only have one parent")
                    if child.core is not None:
                        raise ValueError(f"{child!r} is already registered to another log")
                elif child._core is not None:
                    raise ValueError(f"{child!r} is already registered to another log")
                accepted.append(child)

            for child in accepted:
                if isinstance(child, LogFormatter):
                    self.routes[child.key] = []
                jobs.append(Job(self._enroll_node, (child, parent, session), involved=child))
                route.append(child)
                backroutes[child] = parent

            self._recompute_truthy()

        # register-and-start each newly routed node through the
        # fault ladder: a raising start() gets fix -> retry ->
        # unroute-just-that-node, instead of escaping to route()'s
        # caller with the tables half-committed.  (configuration
        # errors were all raised above, atomically; only genuine
        # runtime lifecycle failures reach these jobs.)
        self.execute(jobs)

    def _enroll_node(self, node, parent, session):
        # register-and-start a node just added to the routing tree.
        # retry-safe: each step re-checks what it's about to do, so
        # a fix() that repairs the node gets a clean second attempt.
        # started-marking lives in _start_node: only nodes that
        # actually started are ever end()ed.
        if isinstance(node, LogFormatter):
            if node.core is None:
                node.register(self)
        else:
            if node._core is None:
                node.register(self, parent)
        if session is not None:
            self._start_node(node, session)

    def bump_pause_epoch(self):
        # invalidates every session's cached liveness (see
        # Session._live).  call AFTER mutating pause state: a cache
        # entry computed mid-mutation then carries the old epoch
        # and re-walks on its next read.  (bumping before the
        # mutation could tag a stale walk with the new epoch,
        # freezing the stale answer in.)  guarded: += is a
        # read-modify-write, and pause/resume run on any thread.
        with self.configuration_lock:
            self.pause_epoch += 1

    def _recompute_truthy(self):
        # call with configuration_lock held.  a Log is true while
        # it has destinations in its routes--somebody is listening--
        # and false again when the last one is removed.  only real,
        # truthy destinations count: a subtree of formatters ends
        # nowhere, and a falsy destination (NoneType) is a discard.
        self.truthy = any(
            isinstance(child, LogDestination) and child
            for children in self.routes.values()
            for child in children
            )

    def _walk(self):
        # every routed node, parents before children.
        # call with configuration_lock held.
        for f in self.formatters:
            stack = [f]
            while stack:
                node = stack.pop()
                yield node
                if isinstance(node, LogFormatter):
                    stack.extend(reversed(self.routes.get(node.key, ())))

    @staticmethod
    def _node_key(node):
        return node.key if isinstance(node, LogFormatter) else node._key

    def _start(self, session):
        # snapshot under the lock; make the (foreign) start calls
        # after releasing it
        with self.configuration_lock:
            assert self.started is None
            self.started = set()
            starters = list(self._walk())

        # start each node as its own attributed job: a raising
        # start() engages the fault ladder (fix -> retry -> unroute)
        # instead of poisoning the log.  start is where File meets
        # the filesystem--the single likeliest moment for a
        # destination to fail--and formatters get the same treatment
        # (one lifecycle, one fault policy; unrouting a formatter
        # retires its whole subtree, which can never receive
        # renderings anyway).
        self.execute([Job(self._start_node, (node, session), involved=node)
                      for node in starters])

    def _start_node(self, node, session):
        node.start(session)
        # mark started only AFTER start() succeeded: a node that
        # never started must never receive end().
        with self.configuration_lock:
            if self.started is not None:
                self.started.add(self._node_key(node))

    def _end(self):
        # the mirror image of _start: sessions are all gone,
        # tell every started formatter and destination.
        # (snapshot under the lock, call end() outside it.)
        with self.configuration_lock:
            started = self.started
            if started is None:
                return
            self.started = None
            enders = []
            for node in self._walk():
                if self._node_key(node) in started:
                    enders.append(node)

        for o in enders:
            o.end()

    def register(self, session):
        wr = weakref.ref(session)
        self.sessions.append(wr)
        i = self.sessions.rmatch(lambda v: v is wr)
        def unregister():
            try:
                i.pop()
            except SpecialNodeError:
                pass
            if (not self.sessions) and (self.started is not None):
                # the last session is gone, and we actually started
                # logging: flush everything, then send "end" to every
                # started formatter and destination.  (the flush jobs
                # are scheduled at priority; _end is scheduled at
                # normal priority, so it runs after the flushes--and
                # after any straggler message jobs already queued.)
                self.flush()
                self.Scheduler(self._end)

        return unregister


    def execute(self, iterator):
        for job in iterator:
            while True:
                assert not job.called
                fault = job()
                if fault is None:
                    break

                involved = job.involved
                if not isinstance(involved, (LogFormatter, LogDestination)):
                    # unfixable exception, poisoned
                    self.poisoned = fault
                    break

                if job.resets < self.retries:
                    try:
                        # fix() is user code: never call it while
                        # holding configuration_lock.  (if it wants
                        # to touch routing, it can call route(),
                        # which takes the lock itself.)
                        result = self.fix(involved, fault)
                        if result:
                            job.reset()
                            # retry job!
                            continue
                    except Exception as e:
                        self.poisoned = e
                        break

                # failed to fix the job.

                # remove all pending jobs involving the same object.
                # (that's the whole cleanup: downstream jobs are
                # created on demand, after their input exists, so
                # there's no such thing as a queued job depending
                # on this one's never-coming result.)
                self.queue.remove_involved(involved)

                # unceremoniously remove involved from routing:
                # the node, and--if it's a formatter--its entire
                # subtree.  if that leaves an ancestor formatter
                # childless, retire the ancestor too, all the way
                # up.  (mutate the tables under the lock; call the
                # foreign unregister() methods after releasing it.)
                removed = []
                with self.configuration_lock:
                    attached = ((involved in self.backroutes)
                                or (isinstance(involved, LogFormatter) and (involved.key in self.routes)))
                    # attached is False if involved was already
                    # unrouted (e.g. collateral damage from an
                    # earlier fault); then there's nothing to do
                    if attached:
                        parent = self.backroutes.get(involved)
                        stack = [involved]
                        while stack:
                            node = stack.pop()
                            removed.append(node)
                            self.backroutes.pop(node, None)
                            if isinstance(node, LogFormatter):
                                stack.extend(self.routes.pop(node.key, ()))
                        node = involved
                        while True:
                            if parent is None:
                                # a top-level formatter
                                if isinstance(node, LogFormatter) and (node.key in self.formatters_by_key):
                                    del self.formatters_by_key[node.key]
                                    self.formatters.remove(node)
                                break
                            siblings = self.routes[parent.key]
                            siblings.remove(node)
                            if siblings:
                                break
                            # the parent is childless now:
                            # retire it too, and keep climbing
                            node = parent
                            parent = self.backroutes.pop(node, None)
                            removed.append(node)
                            self.routes.pop(node.key, None)
                        self._recompute_truthy()

                for node in removed:
                    self.queue.remove_involved(node)
                    node.unregister()
                break


    # bound inner class: constructed as core.Queue(...);
    # the owning core is injected as the first argument.
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
            self.executing = False

        def __iter__(self):
            return self

        def __next__(self):
            nq = self.notify_queue
            pj = self.priority_jobs
            nj = self.normal_jobs
            break_if_empty = not self.block
            drain = False

            # self.count is a spilled local, only touched by __next__,
            # so it doesn't need to be under the lock.
            #
            # self.deletions is also touched by self.remove(), so it's
            # shared state, needs to be under lock.

            count = self.count

            while True:
                if not count:
                    if break_if_empty and nq.empty():
                        break
                    count = nq.get()
                    assert count

                with self.lock:
                    while count:
                        if self.deletions:
                            # a queued job was removed; its notification
                            # is still in the queue.  swallow one
                            # notification per deletion.
                            self.deletions -= 1
                            count -= 1
                            continue

                        job = (pj if pj else nj).rpop()
                        count -= 1

                        if drain:
                            # drain mode discards jobs without
                            # running them--but a discarded job's
                            # blocker must still be released, or
                            # its waiter hangs forever.
                            if isinstance(job.involved, _LockType):
                                job.involved.release()
                            continue

                        if job.method is None:
                            # the atexit sentinel: stop processing,
                            # discard everything still queued, then
                            # exit when the queue runs dry.  (the
                            # guarantee that _end runs before this
                            # sentinel--so destinations get their
                            # end() lifecycle--lives in
                            # _stop_thread's barrier.)
                            assert not job.args
                            drain = True
                            break_if_empty = True
                            continue

                        # spill
                        self.count = count
                        return job

            # spill
            self.count = count
            raise StopIteration

        def extend(self, jobs, *, priority=False):
            if not jobs:
                return
            (self.priority_jobs if priority else self.normal_jobs).extend(jobs)
            self.notify_queue.put(len(jobs))

        def prepend(self, jobs, *, priority=False):
            # insert at the *front*--the pop end--preserving order.
            # this is how on-demand jobs cut in line: a render job
            # creates its downstream jobs the moment the rendering
            # exists, and they run before anything queued earlier.
            if not jobs:
                return
            lane = self.priority_jobs if priority else self.normal_jobs
            lane.extendleft(reversed(jobs))
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
            # Reentrancy guard.  A job being executed can queue more
            # jobs and then try to drain (e.g. a session banner logged
            # from inside an ensure_state job).  The nested call simply
            # returns; the jobs it queued are already in the queue, and
            # the *outer* execute loop will process them, in order.
            if self.executing:
                return
            self.executing = True
            try:
                self.core.execute(self)
            finally:
                self.executing = False

        def drain(self):
            assert not self.block
            self.execute()



    # bound inner class: constructed as core.Scheduler(...);
    # the owning core is injected as the first argument.
    @BoundInnerClass
    class Scheduler:
        def __init__(self, core, *args, atexit=False, priority=False, wait=False):
            """
            Manages creating "jobs" iterables and scheduling the work.  To use:

                s = core.Scheduler()   # returns a Scheduler
                a = s.add              # tear off add for repeated use
                a(fn, arg1, arg2)      # adds fn(arg1, arg2) to our local job list
                a(fn2, arg3)           # adds fn2(arg3)
                s()                    # schedules all the jobs on the local job list

            Calling the Scheduler itself takes no arguments and means
            exactly one thing: schedule everything added so far.
            There's also a shortcut if you're only scheduling one job:

                core.Scheduler(fn, arg1, arg2)

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
                self.add(*args)
                self()

        def __bool__(self):
            return bool(self.jobs)

        def execute(self):
            jobs = self.jobs
            self.jobs = []
            self.core.execute(jobs)

        def add(self, method, *args, involved=_INFER_INVOLVED):
            "Appends a job to the local job list."
            if isinstance(method, Job):
                assert not args
                assert involved is _INFER_INVOLVED
                job = method
            else:
                job = Job(method, args, involved)
            self.jobs.append(job)

        def __call__(self):
            "Schedules every job added so far."
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

            if not jobs:
                # nothing to schedule
                return
            self.jobs = []

            queue.extend(jobs, priority=self.priority)

            if blocker:
                core.block(blocker)

            if drain:
                core.queue.drain()

            if atexit:
                core.thread.join()


    def _ensure_started(self):
        # destinations start *lazily*, on the first actual log
        # message.  if you never log, Log never touches your
        # destinations--never opens your file, never computes
        # a tempfile name, nothing.
        if self.started is not None:
            return
        try:
            session = self.sessions[0]()
        except IndexError: # pragma: no cover
            session = None
        if session is None: # pragma: no cover
            return
        self._start(session)

    def log(self, message):
        self._ensure_started()
        if self.started is None:
            # a straggler: this message's job was queued by a thread
            # racing shutdown, and landed behind _end in the queue.
            # every destination has been end()ed; drop the message
            # rather than write to ended destinations.
            # (_ensure_started can't restart us: with no live
            # session, it returns without starting.)
            return
        s = self.Scheduler(priority=True)
        add = s.add
        for key, prepared in message.prepared.items():
            formatter = self.formatters_by_key.get(key)
            if formatter is None:
                continue
            if self.routes.get(formatter.key, ()):
                add(self._render_and_fanout, formatter, message, involved=formatter)
        if s:
            self.dirty = True
            s()

    def _render_and_fanout(self, node, value):
        # the routing tree is data; this method is its interpreter.
        # render, then create the downstream jobs NOW, carrying the
        # concrete rendering as an argument.  jobs are created on
        # demand, *after* their input exists--so a queued job can
        # never be waiting on a result that will never arrive, and
        # a node that faults simply never creates its subtree's
        # jobs.  (this replaced a futures design, where every write
        # job held an IOU on its render job, and a faulted render
        # meant transitively hunting the queue for dead IOUs.)
        #
        # every downstream job goes through the queue, so the fault
        # ladder in Core.execute handles every node uniformly--
        # destinations are independently failable, fixable, and
        # unroutable, and so are nested formatters.
        rendered = node.render(value)
        if rendered is None:
            # a formatter that renders None drops the message for
            # its whole subtree; that's how filters filter.
            return
        children = self.routes.get(node.key, ())
        jobs = []
        for child in children:
            if isinstance(child, LogFormatter):
                jobs.append(Job(self._render_and_fanout, (child, rendered), involved=child))
            else:
                jobs.append(Job(child.write, (rendered,)))
        self.queue.prepend(jobs, priority=True)

    def flush(self, wait=True):
        # never wait when we're already ON the worker thread--
        # we'd be waiting for ourselves to release the blocker
        # (a job behind the one we're currently executing).
        wait = wait and (threading.current_thread() is not self.thread)
        # snapshot the destinations under the lock: routes is
        # mutated (under configuration_lock) by route(), the fault
        # ladder, and _remap_destinations, possibly on other
        # threads--and this method runs on the caller's thread.
        # (snapshot under the lock, schedule outside it, same as
        # _end.)
        with self.configuration_lock:
            destinations = [child
                            for children in self.routes.values()
                            for child in children
                            if isinstance(child, LogDestination)]
        s = self.Scheduler(priority=True, wait=wait)
        add = s.add
        # _clean is scheduled (not called): every write to "dirty"
        # happens on the executor, so the flag can't race.
        add(self._clean)
        for d in destinations:
            add(d.flush)
        s()

    def _clean(self):
        self.dirty = False

    def _remap_destinations(self, formatter, mapped):
        # runs on the executor: replace formatter's destinations
        # with `mapped`.  removed destinations are flushed (pending
        # content is the user's data--written, not dropped), ended,
        # and unregistered.  added destinations get a "recap": the
        # banners that already went out are re-rendered for them, so
        # their output reads as a coherent log.
        with self.configuration_lock:
            route = self.routes.setdefault(formatter.key, [])
            current = [child for child in route if isinstance(child, LogDestination)]
            keep_formatters = [child for child in route if not isinstance(child, LogDestination)]
            removed = [d for d in current if not any(d == m for m in mapped)]
            added = [m for m in mapped if not any(m == d for d in current)]
            kept = [d for d in current if not any(d == r for r in removed)]

            # rebuild the route in the new order: mapped destinations
            # (using the existing object where one is kept), then any
            # routed sub-formatters
            new_destinations = []
            for m in mapped:
                for d in kept:
                    if d == m:
                        new_destinations.append(d)
                        break
                else:
                    new_destinations.append(m)
            route[:] = new_destinations + keep_formatters

            started = (self.started is not None) and (formatter.key in self.started)
            for d in removed:
                self.backroutes.pop(d, None)
                if self.started is not None:
                    self.started.discard(d._key)
            for d in added:
                self.backroutes[d] = formatter
                if started:
                    self.started.add(d._key)
            self._recompute_truthy()

            try:
                session = self.sessions[0]()
            except IndexError: # pragma: no cover
                session = None

        # lifecycle calls happen outside the lock--and each runs as
        # its own job, attributed to its own destination, through
        # the fault ladder.  (they're foreign code: a raising
        # flush() on a removed destination must not be blamed on
        # the formatter, and a repaired one must be retried with
        # its own state, not by re-running this whole method--the
        # tables above are already committed, so a re-run computes
        # removed=[] and silently skips the flush.)
        self.execute([Job(self._retire_destination, (d, started), involved=d)
                      for d in removed])
        # the ladder can abandon a retire job (fix() declined or
        # kept failing).  the destination is out of the tables
        # either way; make sure it's out of the *lifecycle* too, or
        # it leaks in registered limbo, impossible to ever re-route.
        # fix() already had its chance--tree coherence outranks a
        # dying destination's protests, so its end() exception is
        # swallowed here.
        for d in removed:
            if d._core is None:
                continue
            if started and (d.session is not None):
                try:
                    d.end()
                except Exception:
                    pass
            d.unregister()

        self.execute([Job(self._install_destination, (d, formatter, started, session), involved=d)
                      for d in added])

        owner = self.owner
        if owner is not None:
            # same still-routed filter as Log._route: an added
            # destination the install ladder already unrouted
            # doesn't belong in the public list.
            with self.configuration_lock:
                still_routed = [d for d in added if d in self.backroutes]
            owner._all_destinations[:] = [x for x in owner._all_destinations if not any(x == r for r in removed)]
            owner._all_destinations.extend(still_routed)

    def _retire_destination(self, d, started):
        # remove a destination reconfigured away: flush (pending
        # content is the user's data--written, not dropped), end,
        # unregister.  written to be safely *retried* by the fault
        # ladder: flush is failure-atomic (the payload survives a
        # faulted attempt), and the end/unregister steps re-check
        # the state they're about to change.
        self.queue.remove_involved(d)
        d.flush()
        if started and (d.session is not None):
            d.end()
        if d._core is not None:
            d.unregister()

    def _install_destination(self, d, formatter, started, session):
        # add a destination reconfigured in: register, start, recap.
        # its own attributed job, so a failing start engages the
        # fault ladder--and since the tables already carry d, the
        # ladder's unroute removes exactly d, nothing else.
        # retry-safe: re-check each step.
        if d._core is None:
            d.register(self, formatter)
        if started and (session is not None):
            if d.session is None:
                d.start(session)
            self._recap(formatter, d)

    def _recap(self, formatter, destination):
        # re-render the already-delivered banners--the start banner,
        # and the enter banner of each open unbuffered block--for one
        # newly added destination, so its log reads coherently from
        # the top.  (buffered blocks' banners haven't been delivered
        # to *anyone* yet; they'll arrive for everybody when the
        # block flushes.)
        try:
            sessions = [wr() for wr in self.sessions]
        except Exception: # pragma: no cover
            return
        for session in sessions:
            if (session is None) or (session.state != STATE_ACTIVE):
                continue
            if session.parent is None:
                format, banner_session, time = 'start', session, session.initial
            elif session.buffer is None:
                format, banner_session, time = 'enter', session.parent, session.initial
            else:
                continue
            if format not in self.formats:
                continue
            try:
                message = banner_session.Message(time, format, (session.name,), session.kwargs, thread=_EMPTY_THREAD)
                rendered = formatter.render(message)
                if rendered is not None:
                    destination.write(rendered)
            except Exception:
                # a recap failure is not fatal: the destination stays
                # routed, and if it's genuinely broken, its first real
                # write will fault and the normal ladder will handle it
                pass

    def reset(self):
        sessions = self.sessions
        s = self.Scheduler()
        add = s.add
        while sessions:
            rit = reversed(sessions) # rit points at tail
            rit.next(None)           # now rit points to node before tail
            while rit:               # rit is True if it's not head
                wr = rit.rpop()
                session = wr()
                if session is not None:
                    add(session._close)
        s()
        self.flush()

    def atexit(self):
        # If the process is shutting down,
        # Log only aspires to keep everything
        # logged up to that point.
        if self.exited:
            return
        self.exited = True
        if self.threaded:
            self._stop_thread()
            return
        self.reset()


# these formats belong to the Log machinery itself;
# user messages can't be logged with them directly
_SYSTEM_FORMATS = frozenset(('start', 'end', 'enter', 'exit'))

def _check_format_not_reserved(format):
    # Optional is a str subclass, so it's checked too: "fall back
    # silently if undefined" is orthogonal to "is this name
    # reserved".  The machinery's own defaults--Optional('log'),
    # Optional('print'), Optional('preformatted')--aren't reserved
    # names, so they pass; the real banners are constructed directly
    # in ensure_state and never come through here.
    if isinstance(format, str) and (format in _SYSTEM_FORMATS):
        raise ValueError(f"format {format!r} is reserved")


STATE_INITIAL = (1, 'initial')
STATE_ACTIVE = (2, 'active')
STATE_CLOSED = (3, 'closed')


_spec_type_codes = 'bcdeEfFgGnosxX%'

def _strip_type_spec(spec):
    # reduce a format spec to its fill/align/width bones, so it can
    # be applied to an empty string.  ('09d' -> '9', '>12,' -> '>12')
    result = []
    for c in spec:
        if c in _spec_type_codes:
            break
        if c in '+-# ,_':
            continue
        if (c == '0') and not result:
            continue
        if c == '.':
            break
        result.append(c)
    return ''.join(result)


class _EmptyValue:
    """
    Renders as '' under *any* format spec--honoring width and
    alignment, ignoring numeric type codes.  This is what makes
    _EmptyThread a competent counterfeit: a real thread's ident is
    an int, so a user template saying {thread.ident:d} works on
    every real message--and would fault on every banner if the
    empty ident were a plain ''.  (''.__format__('d') raises;
    a formatter fault unroutes the formatter.  A correct template
    must never kill the log.)
    """
    def __format__(self, spec):
        try:
            return format('', spec)
        except ValueError:
            return format('', _strip_type_spec(spec))

    def __str__(self):
        return ''
    __repr__ = __str__

    def __bool__(self):
        return False

_EMPTY_VALUE = _EmptyValue()


class _EmptyThread:
    """
    A fake "thread" used for session banners.  Banners aren't
    logged by any particular thread, so every attribute--name,
    ident, native_id, daemon--renders as the empty string, under
    any format spec (see _EmptyValue).
    """
    name = _EMPTY_VALUE
    ident = _EMPTY_VALUE
    native_id = _EMPTY_VALUE
    daemon = _EMPTY_VALUE
    def __str__(self):
        return ''
    __repr__ = __str__

_EMPTY_THREAD = _EmptyThread()

@export
class _InertContextManager:
    """
    The context manager returned by enter() on a closed log.
    Does nothing at all.
    """
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

_INERT_CONTEXT_MANAGER = _InertContextManager()


class LogBase:
    __slots__ = ('_core', '_clock', '_helper_cache', '_name', '_nesting', '_owner', '_session', '_unregister', '__weakref__', )

    def __init__(self, name, core, session, paused):
        self._name = name
        self._core = core
        self._session = session
        self._helper_cache = {}
        self._nesting = []
        self._owner = None

        self._unregister = session.register(self)
        self._clock = session.clock

    def __bool__(self):
        # true iff logging to this handle right now would deliver:
        # the log has destinations (core.truthy, recomputed when
        # destinations are added or removed), this handle is open,
        # and its session is live (open and unpaused--epoch-cached,
        # see Session._live).  everything here is a handful of
        # reads: `if log:` must stay practically free.
        session = self._session
        return (self._core.truthy
                and (session is not None)
                and session._live)

    def __getattr__(self, attr):
        # is this the name of a user-defined format?
        core = self._core
        if attr in core.formats:
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

    @property
    def nesting(self):
        return tuple(self._nesting)

    def enter(self, message='', **kwargs):
        """
        Opens a nested block in the log.

        Logs an "enter" banner, and indents every message
        logged until the matching exit() call.  enter may
        be nested.

        Returns a context manager; exiting the context
        manager closes this nested block.  (You can also
        close it by calling exit().)
        """
        # note the time FIRST: the enter banner is stamped with the
        # moment the user called us
        time = self._clock()
        session = self._session
        if (session is not None) and session.paused_in_tree:
            return _INERT_CONTEXT_MANAGER
        parent = self._nesting[-1] if self._nesting else self
        child = parent._child(time, message, True, _DEFAULT_CHILD_FORMAT, None, kwargs)
        if child is None:
            # the log is closed; hand back a context manager
            # that does nothing at all
            return _INERT_CONTEXT_MANAGER
        child._owner = self
        self._nesting.append(child)
        return child

    def exit(self):
        """
        Closes the most deeply nested enter() block.

        Logs an "exit" banner and removes one level of indent.
        If there's no currently-open enter() block, does nothing.
        """
        time = self._clock()
        if not self._nesting:
            return
        child = self._nesting.pop()
        child._owner = None
        child._close_handle(time, True)

    def close(self, wait=True):
        # note the time FIRST: it stamps the end/exit banners of
        # this handle and every open enter() block it closes--they
        # all close because of this one call, at this one moment.
        self._close_handle(self._clock(), wait)

    def _close_handle(self, time, wait):
        if not self._session:
            return
        # closing a log closes its open enter() blocks,
        # deepest first
        while self._nesting:
            child = self._nesting.pop()
            child._owner = None
            child._close_handle(time, True)
        owner = self._owner
        if owner is not None:
            self._owner = None
            try:
                owner._nesting.remove(self)
            except ValueError: # pragma: no cover
                pass
        self._session = None
        u = self._unregister
        self._unregister = None
        u(time)
        if wait:
            core = self._core
            if core.threaded and (threading.current_thread() is not core.thread):
                s = core.Scheduler(wait=True)
                s()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def flush(self, wait=True):
        if self._core.poisoned:
            raise self._core.poisoned
        core = self._core
        # never wait when we're already ON the worker thread--we'd
        # be waiting for ourselves to release the blocker (a job
        # queued behind the one we're currently executing).  same
        # rule as Core.flush and close().  the flush jobs are still
        # scheduled; the reentrant caller just doesn't block on
        # them--it can't, and they'll run as soon as it returns.
        wait = wait and not (core.threaded and (threading.current_thread() is core.thread))
        session = self._session
        if session:
            # first flush the session (pushes any buffered messages
            # upstream), then flush the core (pushes everything out
            # to the destinations)
            core.Scheduler(session.flush, wait=wait)
        core.flush(wait=wait)

    @property
    def paused(self):
        """Returns True if the handle is paused--directly, or by any
        ancestor (pause is hierarchical)--None if the log is closed,
        and otherwise False."""
        if self._core.poisoned:
            raise self._core.poisoned
        if not self._session:
            return None
        return self._session.paused_in_tree

    class _ResumeContextManager:
        """
        The context manager returned by Log.pause().  Calls Log.resume() on exit.
        """
        def __init__(self, log):
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

        A paused log ignores calls to its logging methods
        (write, print, __call__, log, and enter).  exit() still
        closes the deepest open enter() block--and emits its exit
        banner: nesting tracks your program's structure, paused
        or not.  (Likewise, closing an enter() context manager
        closes the block.)

        Pause is hierarchical: pausing a handle silences its
        entire subtree, including child handles held elsewhere.
        Pausing a child handle silences just that subtree.

        Pause state is internally stored as an integer;
        pause increments it, resume decrements it (but not below zero),
        and if it's greater than zero the log is paused.

        If the log is closed, this function does nothing,
        and it returns a context manager that also does nothing.
        """
        if self._core.poisoned:
            raise self._core.poisoned
        session = self._session
        if session is None:
            return _INERT_CONTEXT_MANAGER
        session.pause()

        return self._ResumeContextManager(self)

    def resume(self):
        """
        Resumes the log if it's not closed.

        If the log is not closed, and is currently paused,
        this resumes (un-pauses) the log.

        A paused log ignores calls to its logging methods
        (write, print, __call__, log, and enter).  exit() still
        closes the deepest open enter() block--and emits its exit
        banner: nesting tracks your program's structure, paused
        or not.

        Pause is hierarchical: resuming a handle un-silences only
        its own pause; ancestors' pauses still apply.

        Pause state is internally stored as an integer;
        pause increments it, resume decrements it (but not below zero),
        and if it's greater than zero the log is paused.

        If the log is closed, this function does nothing.
        """
        if self._core.poisoned:
            raise self._core.poisoned
        session = self._session
        if session is not None:
            session.resume()

    def child(self, name='', buffered=True, *, format=_DEFAULT_CHILD_FORMAT, paused=None, **kwargs):
        return self._child(self._clock(), name, buffered, format, paused, kwargs)

    def _child(self, time, name, buffered, format, paused, kwargs):
        session = self._session
        if (not session) or (session.state >= STATE_CLOSED):
            return None
        return Child(name, self._core, session, time=time, buffered=buffered, paused=paused, format=format, kwargs=kwargs)

    # log(), write(), and print() are one pipeline with three front
    # doors.  each front door does exactly one thing: note the time,
    # FIRST--the message is stamped with the moment the user called
    # us, before a single other instruction runs--then hand off to
    # its _impl twin.  the twins carry that time through the nesting
    # delegation (a delegated call must NOT restamp the message with
    # a later time) and keep only what's genuinely theirs--
    # validation and argument shaping--sharing the machinery:
    #
    #   _prologue(format)
    #       examine format and session.
    #       return True on ok, False on don't log (return now).
    #   _logging()  the guards: poisoned raises, a closed
    #                   handle/session returns None (drop).
    #   _log()          construct the Message and schedule it.
    #
    # _logging and _log are two helpers, not one, so print() can
    # shape its arguments *between* them: coercing args to str runs
    # foreign __str__ methods, and a dark log must never do that.

    def _prologue(self, format):
        session = self._session
        if (session is not None) and session.paused_in_tree:
            return False
        _check_format_not_reserved(format)
        return True

    def _logging(self):
        if self._core.poisoned:
            raise self._core.poisoned
        session = self._session
        if (not session) or (session.state >= STATE_CLOSED):
            return None
        return session

    def _send(self, session, time, format, args, kwargs, flush):
        message = session.Message(time, format, args, kwargs)
        scheduler = self._core.Scheduler()
        scheduler.add(session.ensure_state, STATE_ACTIVE)
        scheduler.add(session.log, message)
        scheduler()
        if flush:
            self.flush()

    def log(self, *args, format=Optional('log'), flush=False, **kwargs):
        self._log(self._clock(), format, flush, args, kwargs)

    def _log(self, time, format, flush, args, kwargs):
        if not self._prologue(format):
            return
        if self._nesting:
            return self._nesting[-1]._log(time, format, flush, args, kwargs)

        session = self._logging()
        if session is None:
            return
        self._send(session, time, format, args, kwargs, flush)

    def write(self, s, format=Optional('preformatted'), flush=False):
        self._write(self._clock(), format, flush, s)

    def _write(self, time, format, flush, s):
        if not self._prologue(format):
            return
        if self._nesting:
            return self._nesting[-1]._write(time, format, flush, s)

        if not isinstance(s, str):
            raise TypeError(f"write() argument must be str, not {type(s).__name__}")

        session = self._logging()
        if session is None:
            return
        self._send(session, time, format, (s,), {}, flush)

    def print(self, *args, sep=' ', end='\n', format=Optional('print'), flush=False):
        self._print(self._clock(), format, flush, args, sep, end)

    def _print(self, time, format, flush, args, sep, end):
        if not self._prologue(format):
            return
        if self._nesting:
            return self._nesting[-1]._print(time, format, flush, args, sep, end)

        if not isinstance(sep, str):
            raise TypeError(f"sep must be str, not {type(sep).__name__}")
        if not isinstance(end, str):
            raise TypeError(f"end must be str, not {type(end).__name__}")

        session = self._logging()
        if session is None:
            return

        s = sep.join(str(o) for o in args) + end
        if s.endswith('\n'):
            s = s[:-1]

        self._send(session, time, format, (s,), {}, flush)

    __call__ = print


class Child(LogBase):
    __slots__ = ()

    def __init__(self, name, core, parent_session, *, time=None, buffered=True, paused=False, format=_DEFAULT_CHILD_FORMAT, kwargs=None):
        if time is None:
            time = parent_session.clock()

        if not isinstance(name, str):
            raise TypeError(f'name must be str, not {type(name).__name__}')

        if format is _DEFAULT_CHILD_FORMAT:
            # a child session inherits the root format; its banners
            # are the flat 'enter' and 'exit' formats, and its body
            # is indented one level deeper than its parent.
            format = parent_session.format
        else:
            if isinstance(format, Optional):
                raise ValueError("Child format can't be Optional")
            if not isinstance(format, str):
                raise TypeError(f"format must be str, not {type(format).__name__}")

        if (core.formats is not True) and (format not in core.formats):
            raise ValueError(f"{format} is not defined by all formatters")

        if core.poisoned:
            raise core.poisoned

        if paused is None:
            # children inherit pause *live*, through the session
            # tree (see Session.paused_in_tree)--no snapshot needed
            paused = False

        session = Session(core, name, parent_session, buffered=buffered, clock=parent_session.clock, format=format, kwargs=kwargs, paused=paused)
        clock = session.clock

        super().__init__(name, core, session, paused)
        self._clock = clock

    @property
    def message(self):
        return self._name



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

        # the underlying callables, for introspection
        self.clock = default_clock
        self.timestamp_clock = time.time

    def __call__(self):
        return default_clock()

    def delta_to_seconds(self, delta):
        return delta / 1_000_000_000.0

    def time_to_timestamp(self, time):
        delta = time - self.initial
        seconds = delta / 1_000_000_000.0
        epoch = self.epoch + seconds
        return timestamp_human(epoch)


class _CustomClock(Clock):
    '''
    Adapts a plain callable (returning nanoseconds) into a Clock.
    '''
    def __init__(self, clock):
        super().__init__()
        self.clock = clock
        self.initial = clock()

    def __call__(self):
        return self.clock()


@export
def default_fix(o, fault):
    """
    The default fix callback: declines to fix anything.

    A Log's fix callback is called as fix(involved, exception)
    whenever a formatter or destination raises: "involved" is the
    offending object, "exception" is what it raised.  Return true
    to retry the failed operation (up to Log's retries count);
    return false and the object is immediately dropped from the
    log's routing.

    The drop is silent, on purpose: the log never injects messages
    you didn't write.  If you want a death notification, this is
    your hook--record, print, or log elsewhere before declining.
    (A fix that keeps returning true until retries is exhausted is
    NOT called again for the final drop; if you always return true,
    count your own calls.)
    """
    pass


@export
class Log(LogBase):
    """
    A fast, flexible, threaded log--designed to observe your
    program without perturbing it.  The call site pays only for
    stamping the time and capturing the message; formatting and
    output happen on a worker thread (or, if threaded=False,
    inline through the same machinery).

    Constructor parameters:

    *destinations is where the log writes.  Each may be a
    LogDestination object, or anything map_destination understands:
    print, a callable, a list, a str/bytes/pathlib.Path (a file),
    an open text file, TMPFILE, or None.  Default: print.

    formatter is the LogFormatter that renders messages; default
    is TextFormatter().  All formatter configuration--formats,
    prefix, width, indent--lives on the formatter: construct your
    own TextFormatter and pass it in.

    clock is either a Clock subclass or a plain callable
    returning integer nanoseconds (which gets wrapped).

    fix is the fault-repair callback, called as
    fix(involved, exception) when a formatter or destination
    raises; return true to retry.  retries is how many times a
    faulting job is retried (>= 1).  A job that still fails has
    its formatter or destination surgically unrouted; the log
    carries on without it.

    threaded (default True) runs the worker thread.
    buffered buffers the root session until flush/close.
    paused starts the log paused; it's also the state reset()
    restores (see paused_on_reset).
    name names the log (used in banners and TmpFile filenames).

    Destinations start lazily: if you never log, Log never
    touches them.  "if log: log(...)" costs almost nothing when
    the log has no destinations.
    """

    __slots__ = ('_all_destinations', '_buffered', '_formatter', '_paused_on_reset', '_sink_formatter')

    _InertContextManager = _InertContextManager
    _ExitContextManager = Child
    Buffer = Buffer
    Sink = Sink

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
        threading=None,
        ):

        # validate everything we can *before* creating the Core--
        # a Core owns an atexit handler (and possibly a thread),
        # so we don't want to create one and then raise.
        if not isinstance(name, str):
            raise TypeError(f'name must be str, not {type(name).__name__}')
        if not name:
            raise ValueError('name must not be empty')

        retries = operator.index(retries)
        if retries < 1:
            raise ValueError('retries must be >= 1')

        if not callable(fix):
            raise TypeError('fix must be callable')

        if threading is not None:
            # deprecated alias for "threaded"
            threaded = threading

        if formatter is None:
            formatter = TextFormatter()
        elif not isinstance(formatter, LogFormatter):
            raise TypeError(f"formatter must be LogFormatter, not {type(formatter).__name__}")

        if not destinations:
            destinations = [builtins.print]
        # children may be Destinations--or Formatters, which
        # _route understands; map (and so validate) the rest
        # here, before we commit to creating the Core.
        destinations = [d if isinstance(d, LogFormatter) else self.map_destination(d)
                        for d in destinations]

        self._buffered = buffered
        self._paused_on_reset = bool(paused)

        if not callable(clock):
            raise TypeError('clock must be callable')
        if not (isinstance(clock, type) and issubclass(clock, Clock)):
            # a plain callable returning nanoseconds:
            # wrap it in a Clock adapter
            custom = clock
            def clock():
                return _CustomClock(custom)

        core = Core(
            name=name,
            clock=clock,
            fix=fix,
            retries=retries,
            threaded=bool(threaded),
            )
        core.owner = self

        session = Session(core, name, None, buffered=buffered, clock=None, format='', kwargs={}, paused=paused)
        super().__init__(name, core, session, paused)

        self._formatter = formatter
        self._sink_formatter = None
        self._all_destinations = []

        self._route(formatter, destinations)

    @property
    def formatter(self):
        return self._formatter

    @property
    def clock(self):
        "The underlying clock callable used for timing log messages."
        return self._clock.clock

    @property
    def timestamp_clock(self):
        "The underlying clock callable used for wall-clock timestamps."
        return self._clock.timestamp_clock

    @property
    def threaded(self):
        return self._core.threaded

    @property
    def start_time_ns(self):
        "The time this log started, in monotonic clock time."
        return self._clock.initial

    @property
    def start_time_epoch(self):
        "The time this log started, in seconds-since-the-epoch."
        return self._clock.epoch

    @property
    def dirty(self):
        "True if the log has messages that haven't been flushed yet."
        return self._core.dirty

    @property
    def paused_on_reset(self):
        "The paused state reset() restores.  Initialized by the constructor's paused parameter."
        return self._paused_on_reset

    @paused_on_reset.setter
    def paused_on_reset(self, value):
        self._paused_on_reset = bool(value)

    @property
    def _paused_counter(self):
        session = self._session
        if session is None:
            return 0
        return session.paused

    @property
    def _destinations(self):
        return tuple(self._all_destinations)

    @property
    def destinations(self):
        """
        The destinations of the log's main formatter, as a list.

        Settable: assign a list or tuple of destinations (anything
        map_destination understands) to reconfigure the log live.
        Duplicates are a ValueError.  Destinations removed by the
        assignment are flushed (pending buffered content is written,
        not dropped), ended, and unregistered.  Destinations added
        while the log is running receive a "recap"--the start
        banner and the enter banners of the open blocks whose
        banners have already been delivered--so their output reads
        as a coherent log.

        (Destinations routed to other formatters via route() are
        not affected by this property.)
        """
        children = self._core.routes.get(self._formatter.key, ())
        return [child for child in children if isinstance(child, LogDestination)]

    @destinations.setter
    def destinations(self, value):
        core = self._core
        if core.poisoned:
            raise core.poisoned
        if not isinstance(value, (list, tuple)):
            raise TypeError(f'destinations must be a list or tuple, not {type(value).__name__}')
        mapped = [d if isinstance(d, LogDestination) else self.map_destination(d) for d in value]
        for i, d in enumerate(mapped):
            for other in mapped[i + 1:]:
                if d == other:
                    raise ValueError(f'duplicate destination {d!r}')

        # the actual reconfiguration runs on the executor, so it
        # serializes with in-flight message jobs
        wait = not (core.threaded and (threading.current_thread() is core.thread))
        s = core.Scheduler(wait=wait)
        # involved=None, explicitly: without it, Job would infer the
        # formatter from the arguments, and a fault in the table
        # code would unroute the whole healthy tree.  (destination
        # lifecycle failures never reach this job--they run as
        # their own attributed jobs inside _remap_destinations
        # --so a fault here is an internal invariant violation, and
        # poisoning is the honest response.)
        s.add(core._remap_destinations, self._formatter, mapped, involved=None)
        s()

    def _atexit(self):
        # simulates process shutdown, for testing
        self._core.atexit()
        self._session = None
        self._unregister = None

    def reset(self):
        """
        Closes and reopens the log.

        If the log was open, it's closed (sending the end banner
        and flushing all destinations).  Then the log is reopened:
        a fresh session begins, with a fresh start time, and the
        next message logged will send a new start banner (and
        restart all the destinations--for example, TmpFile will
        compute a fresh filename).

        If the process is exiting, reset does nothing.
        """
        core = self._core
        if core.exited:
            return
        if core.poisoned:
            raise core.poisoned

        self.close()
        if core.threaded and (threading.current_thread() is not core.thread):
            # one more round-trip: guarantees the scheduled "_end"
            # work from close() has been processed before we reopen
            s = core.Scheduler(wait=True)
            s()

        session = Session(core, self._name, None, buffered=self._buffered, clock=None, format='', kwargs={}, paused=self._paused_on_reset)
        self._session = session
        self._unregister = session.register(self)
        self._clock = session.clock

    def _route(self, parent, children):
        if not isinstance(parent, LogFormatter):
            raise TypeError(f"formatter must be LogFormatter, not {type(parent).__name__}")
        if not children:
            raise ValueError("must specify at least one destination")

        # a formatter we haven't routed yet becomes a top-level
        # formatter, fed log Messages directly--so it must accept
        # them.  (a filter that accepts str can't sit at the top
        # level; it belongs downstream of a formatter.)
        if parent.key not in self._core.routes:
            accepts = parent.accepts
            if accepts is not True:
                if not any(isinstance(t, type) and issubclass(Session.Message, t) for t in accepts):
                    raise TypeError(f"{parent!r} can't be routed at the top level: it doesn't accept log messages")

        # children may be Destinations--or Formatters, which see
        # this formatter's rendered output, and may get children
        # of their own via a later route() call.
        nodes = [child if isinstance(child, LogFormatter) else self.map_destination(child) for child in children]

        # confirm that each child can handle all types returned by
        # parent.render.  destinations that want SinkEvents instead
        # get routed to an automatically created companion
        # SinkFormatter--structured logging is just another formatter.
        failures = []
        sink_ds = []
        routed = []
        assert isinstance(parent.types, (set, frozenset, bool))
        for node in nodes:
            accepts = node.accepts if isinstance(node, LogFormatter) else node._types
            if accepts is True:
                routed.append(node)
                continue
            assert isinstance(accepts, (set, frozenset))
            if (parent.types is not True) and (parent.types <= accepts):
                routed.append(node)
                continue
            if isinstance(node, LogDestination) and any(isinstance(t, type) and issubclass(t, SinkEvent) for t in accepts):
                sink_ds.append(node)
                continue
            failures.append(node)
        if failures:
            incompatible = ", ".join(repr(node) for node in failures)
            raise TypeError(f"formatter {parent!r} can't be routed to {incompatible}")

        if routed:
            self._core.route(parent, routed)
        if sink_ds:
            sink_formatter = self._sink_formatter
            if sink_formatter is None:
                sink_formatter = self._sink_formatter = SinkFormatter(formats=parent.formats)
            self._core.route(sink_formatter, sink_ds)

        # update the public all_destinations only after routing
        # succeeded--a route() that raised must leave it untouched.
        # skip destinations already present, so re-routing the same
        # destination (a silent no-op above) doesn't duplicate it--
        # and skip any the enrollment fault ladder already unrouted
        # (a destination whose start() failed unfixably).
        core = self._core
        with core.configuration_lock:
            still_routed = [node for node in nodes
                            if isinstance(node, LogDestination)
                            and (node in core.backroutes)]
        all_destinations = self._all_destinations
        all_destinations.extend(
            node for node in still_routed
            if not any(node == existing for existing in all_destinations)
            )

    def route(self, parent, *children):
        """
        Adds edges to the log's routing tree.

        parent must be a LogFormatter.  A formatter the log has
        never routed becomes a top-level formatter, fed log
        messages directly--so it must accept them (see
        LogFormatter's accepts parameter).

        Every child is fed parent's rendered output.  A child
        may be a LogDestination (or anything map_destination
        understands)--or another LogFormatter, e.g. a Filter,
        which may get children of its own via a later route()
        call:

            log.route(log.formatter, a, b, quiet, d)
            log.route(quiet, j, k, l)

        Routing is a tree: a node can only have one parent.
        Route parents before giving children children--a
        formatter route() has never seen becomes a top-level
        formatter.

        If a formatter renders None for a message, the message
        is dropped for that formatter's whole subtree; that's
        how filters filter.
        """
        if self._core.poisoned:
            raise self._core.poisoned
        self._route(parent, children)

    @staticmethod
    def map_destination(o):
        # user-registered mappers get first crack
        for mapper in LogDestination.mappers:
            result = mapper(o)
            if result is not None:
                if not isinstance(result, LogDestination):
                    raise TypeError(f"destination mapper {mapper!r} returned non-LogDestination {result!r}")
                return result

        if isinstance(o, LogDestination):
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

        raise TypeError(f"don't know how to log to destination {o!r}")


mm()
