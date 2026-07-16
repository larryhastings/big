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

import bigtestlib
bigtestlib.preload_local_big()

from big.test import raises, subtest

import builtins
import big.all as big
import big.log as log_module
import io
import os.path
import pathlib
import tempfile
import threading
import time




class FakeClock:
    def __init__(self):
        self.time = 0

    def __call__(self):
        return self.time

    def advance(self, ns=12_000_000):
        self.time += ns


class EventSink(big.log.LogDestination):
    """
    A custom LogDestination that records the *names* of everything
    that happens to it: its own lifecycle events (start/end/flush)
    plus the type of every SinkEvent written to it.
    """

    def __init__(self):
        super().__init__(types=frozenset((big.log.SinkEvent,)))
        self.value = ''

    def __eq__(self, other): # pragma: no cover
        # identity armor; the routing machinery compares
        # destinations, but two EventSinks are never equal
        return other is self

    def __hash__(self):
        return hash(EventSink) ^ id(self)

    def _event(self, s):
        if self.value:
            s = f"{self.value} {s}"

        self.value = s

    def start(self, session):
        super().start(session)
        self._event("start")

    def end(self):
        super().end()
        self._event("end")

    def write(self, event):
        self._event(event.type)

    def flush(self):
        self._event("flush")

def testing_log(*destinations, threaded=False, formatter=None, formats=None, prefix='', width=79, **kwargs):
    "A log object convenient for testing.  Threading, start banner, end banner, and prefix are all off."
    base_formats = {"start": None, "end": None}
    if formats:
        base_formats.update(formats)
    if formatter is None:
        # these tests' expected output is written in the ASCII art
        # (which was the default before 0.14 flipped it to unicode)
        formatter = big.log.TextFormatter(big.log.ascii_format_dict(),
                                          formats=base_formats, prefix=prefix, width=width)
    return big.Log(*destinations, threaded=threaded, formatter=formatter, **kwargs)


def wait_for_job(log):
    "Returns a callable.  Call it to wait until the log has processed all work queued so far."
    event = threading.Event()
    log._core.Scheduler(event.set)
    return event.wait


def test_dict_merge():
    # base only has false values (apart from dicts)
    base = {
        'only in base': '',
        'int': 0,
        'str': '',
        'base is None 1': None,
        'base is None 2': None,
        'update is None 1': 0,
        'update is None 2': {'key': 456},
        'subdict': {
            'only in base': '',
            'int': 0,
            'str': '',
            'base is None 1': None,
            'base is None 2': None,
            'update is None 1': 0,
            'update is None 2': {'key': 456},
        },
    }

    update = {
        'only in update': 'update value',
        'int': 1,
        'str': 'x',
        'base is None 1': 'update value',
        'base is None 2': {'key': 'update value'},
        'update is None 1': None,
        'update is None 2': None,
        'subdict': {
            'only in update': 'update value',
            'int': 1,
            'str': 'update value',
            'base is None 1': 'update value',
            'base is None 2': {'key': 'update value'},
            'update is None 1': None,
            'update is None 2': None,
        }
    }

    expected = {
        'base is None 1': 'update value',
        'base is None 2': {'key': 'update value'},
        'int': 1,
        'only in base': '',
        'only in update': 'update value',
        'str': 'x',
        'subdict': {
            'base is None 1': 'update value',
            'base is None 2': {'key': 'update value'},
            'int': 1,
            'only in base': '',
            'only in update': 'update value',
            'str': 'update value',
            'update is None 1': None,
            'update is None 2': None
            },
        'update is None 1': None,
        'update is None 2': None
        }

    got = big.log._merge_dicts(base, update)
    assert got == expected

def test_type_mismatch():
    base = {
        'subdict': {
            'mismatched': 3,
            'x': 'y',
        }
    }

    update = {
        'subdict': {
            'mismatched': {'a': 'b'},
            'x': 'z',
        }
    }

    with raises(TypeError):
        big.log._merge_dicts(base, update)


def test_destination_init():
    destination = big.log.LogDestination()
    assert destination.core is None
    assert destination.formatter is None
    assert destination.session is None

def test_destination_register():
    destination = big.log.LogDestination()
    destination.register("test core", "test formatter")
    assert destination.core == "test core"
    assert destination.formatter == "test formatter"

def test_destination_register_already_registered():
    destination = big.log.LogDestination()
    destination.register("core1", "formatter1")
    with raises(RuntimeError) as cm:
        destination.register("core2", "formatter2")
    assert "already registered" in str(cm.exception)

def test_destination_virtual_write():
    destination = big.log.LogDestination()
    with raises(RuntimeError):
        destination.write("test")

def test_destination_flush_does_nothing():
    destination = big.log.LogDestination()
    destination.flush()  # Should not raise

def test_destination_start_without_register():
    destination = big.log.LogDestination()
    with raises(RuntimeError) as e:
        destination.start("test session")
    text = str(e.exception)
    assert "can't start" in text
    assert "unregistered" in text

def test_destination_two_starts():
    destination = big.log.LogDestination()
    destination.register(3, 5)
    destination.start("session 1")
    with raises(RuntimeError) as e:
        destination.start("session 2")
    text = str(e.exception)
    assert "can't start" in text
    assert "already started" in text

def test_destination_end_without_a_start():
    destination = big.log.LogDestination()
    with raises(RuntimeError) as e:
        destination.end()
    text = str(e.exception)
    assert "can't end" in text
    assert "it wasn't started" in text


def test_callable_write():
    results = []
    c = big.log.Callable(results.append)
    c.write("test string")
    assert results == ["test string"]


def test_print_write():
    captured = []
    original_print = builtins.print
    builtins.print = lambda *args, **kwargs: captured.append((args, kwargs))
    try:
        printer = big.log.Print()
        printer.write("hello")
    finally:
        builtins.print = original_print
    assert len(captured) == 1
    assert captured[0][0] == ("hello",)
    assert captured[0][1] == {"end": ""}

def test_list_write():
    array = []
    list_destination = big.log.List(array)
    list_destination.write("line1\n")
    list_destination.write("line2\n")
    assert array == ["line1\n", "line2\n"]


def test_buffer_write_and_flush():
    captured = []
    original_print = builtins.print
    builtins.print = lambda *args, **kwargs: captured.append((args, kwargs))
    try:
        buffer = big.log.Buffer()
        buffer.write("hello ")
        buffer.write("world")
        assert buffer._buffer == ["hello ", "world"]
        buffer.flush()
        assert buffer._buffer == []
    finally:
        builtins.print = original_print
    # two calls: the joined message, then Print.flush's empty flushing write
    assert len(captured) == 2
    assert captured[0][0] == ("hello world",)
    assert captured[1][1] == {"end": "", "flush": True}

def test_buffer_flush_empty():
    buffer = big.log.Buffer()
    buffer.flush()  # Should not raise or print


def test_map_destination_support():
    # if we never start logging, we don't open the file,
    # so we don't have to clean up here
    s = '/tmp/x'
    log = big.Log(s)
    d_s = log._core.routes[log.formatter.key][0]
    log.close()
    assert d_s.path == s

    p = pathlib.Path('/tmp/x')
    log = big.Log(p)
    d_p = log._core.routes[log.formatter.key][0]
    log.close()
    assert d_p.path == p

    b = b'/tmp/x'
    log = big.Log(b)
    d_b = log._core.routes[log.formatter.key][0]
    log.close()
    assert d_b.path == b

    assert d_s == d_p
    assert d_s == d_b
    assert d_p == d_b


def test_file_type_checks():
    with raises(TypeError):
        big.log.File(3456)
    with raises(TypeError):
        big.log.File(3.14159)
    with raises(TypeError):
        big.log.File([1, 2, 3])
    with raises(TypeError):
        big.log.File({'a': 'b'})

    with raises(ValueError):
        big.log.File('')
    with raises(ValueError):
        big.log.File(b'')

    with raises(TypeError):
        big.log.File('xyz', b'at')
    with raises(TypeError):
        big.log.File('xyz', [1, 2, 3])
    with raises(TypeError):
        big.log.File('xyz', 8475)
    with raises(ValueError):
        big.log.File('xyz', '')
    with raises(ValueError):
        big.log.File('xyz', 'marjoram')

def test_file_buffered_mode():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        path = f.name

    try:
        file_destination = big.log.File(path, initial_mode='wt')
        file_destination.write("line1\n")
        file_destination.write("line2\n")
        assert file_destination._buffer == ["line1\n", "line2\n"]

        # File should be empty before flush
        with open(path, 'r') as f:
            assert f.read() == ""

        file_destination.flush()
        assert file_destination._buffer == []

        with open(path, 'r') as f:
            content = f.read()
        assert content == "line1\nline2\n"

    finally:
        os.unlink(path)

def test_file_without_buffering():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        path = f.name

    try:
        fd = big.log.File(path, initial_mode='wt', buffering=False)
        log = big.Log(fd, threaded=False)

        log.write("immediate\n")

        # File should have content immediately
        with open(path, 'r') as f:
            content = f.read()
        assert "immediate\n" in content

        log.close()
    finally:
        os.unlink(path)


def test_file_append_mode():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        path = f.name
        f.write("existing\n")

    try:
        fd = big.log.File(path, initial_mode='at')
        log = big.Log(fd, threaded=False)
        log.write("appended\n")
        log.close()

        with open(path, 'r') as f:
            content = f.read()
        assert "existing\n" in content
        assert "appended\n" in content
    finally:
        os.unlink(path)

def test_TmpFile():
    path = None
    try:
        tmpfile = big.log.TmpFile(timestamp_format=lambda x:"ABACAB /DEADBEEF")
        log = testing_log(tmpfile, name="LogName")
        log("xyz")
        path = tmpfile.path.name
        log.close()

        expected = f"LogName.ABACAB.-DEADBEEF.{os.getpid()}.MainThread.txt"
        assert path == expected
    finally:
        if path and os.path.exists(path): # pragma: nocover
            os.unlink(path)

    path = None
    try:
        tmpfile = big.log.TmpFile(prefix='wackadoodle', timestamp_format=lambda x:"ABACAB /DEADBEEF")
        log = testing_log(tmpfile, name="LogName")
        log("xyz")
        path = tmpfile.path.name
        log.close()

        expected = f"wackadoodle.ABACAB.-DEADBEEF.{os.getpid()}.MainThread.txt"
        assert path == expected
    finally:
        if path and os.path.exists(path): # pragma: nocover
            os.unlink(path)

    with raises(TypeError):
        big.log.TmpFile(prefix=345)
    with raises(TypeError):
        big.log.TmpFile(prefix=3.1415)
    with raises(TypeError):
        big.log.TmpFile(prefix=[1, 2, 3])
    with raises(TypeError):
        big.log.TmpFile(prefix={'a': 'b'})
    with raises(TypeError):
        big.log.TmpFile(prefix=b'foo bar')




def test_invalid_filehandle():
    with raises(TypeError):
        big.log.FileHandle(None)

def test_filehandle_write():
    buffer = io.StringIO()
    fh_destination = big.log.FileHandle(buffer)
    fh_destination.write("test content")
    assert buffer.getvalue() == "test content"

def test_filehandle_write_without_autoflush():
    buffer = io.StringIO()
    fh_destination = big.log.FileHandle(buffer, autoflush=False)
    fh_destination.write("test content")
    assert buffer.getvalue() == "test content"

def test_filehandle_flush():
    buffer = io.StringIO()
    fh_destination = big.log.FileHandle(buffer)
    fh_destination.flush()  # Should not raise


class ExplodingFormatter(big.TextFormatter):
    "A TextFormatter that raises on render whenever .explode is set."
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.explode = False

    def render(self, message):
        if self.explode:
            raise RuntimeError('boom')
        return super().render(message)


def test_formatter_fault_unroutes_only_that_formatter():
    dest1, dest2 = [], []
    f2 = ExplodingFormatter()
    log = big.Log(dest1, threaded=False)
    log.route(f2, dest2)

    log('one')
    f2.explode = True
    log('two')                    # f2 faults; default fix declines
    f2.explode = False            # too late: f2 was unrouted
    log('three')
    log.flush()
    log.close()

    text1, text2 = ''.join(dest1), ''.join(dest2)
    for msg in ('one', 'two', 'three'):
        assert msg in text1             # survivor got everything
    assert 'one' in text2
    assert 'two' not in text2            # the faulted message
    assert 'three' not in text2          # and everything after

def test_destination_fault_spares_siblings():
    good = []
    def bad(msg):
        raise OSError('nope')
    log = big.Log(bad, good, threaded=False)
    log('one')                    # bad faults on this very message...
    log('two')
    log.flush()
    log.close()
    text = ''.join(good)
    assert 'one' in text    # ...but its sibling still received it
    assert 'two' in text

def test_filter_none_silences_subtree():
    seen_by_a, seen_by_b = [], []
    quiet = big.Filter(lambda s: None, name='quiet')
    log = big.Log(seen_by_a, threaded=False)
    log.route(log.formatter, quiet)
    log.route(quiet, seen_by_b)

    log('x')
    log('y')
    log.flush()
    log.close()

    text_a = ''.join(seen_by_a)
    assert 'x' in text_a
    assert 'y' in text_a
    assert not (seen_by_b)   # None = dropped, quietly, every time
    # and returning None is not a fault: quiet was never unrouted

def test_deep_chain_fault_isolated():
    dest_b, dest_c = [], []
    passthrough = big.Filter(lambda s: s, name='passthrough')
    def explode(s):
        raise RuntimeError('kaboom')
    exploder = big.Filter(explode, name='exploder')

    log = big.Log([], threaded=False)
    log.route(log.formatter, passthrough)
    log.route(passthrough, dest_b, exploder)
    log.route(exploder, dest_c)

    log('x')                      # exploder faults; its subtree dies
    log('y')
    log.flush()
    log.close()

    text_b = ''.join(dest_b)
    assert 'x' in text_b    # sibling of the exploder: unaffected
    assert 'y' in text_b
    assert not (dest_c)

def test_fix_retry_heals_destination():
    state = {'failed': False}
    received = []
    def flaky(msg):
        if not state['failed']:
            state['failed'] = True
            raise OSError('transient')
        received.append(msg)
    def fix(involved, exception):
        return True               # "try again, it'll work"

    log = big.Log(flaky, fix=fix, threaded=False)
    log('one')
    log('two')
    log.flush()
    log.close()
    text = ''.join(received)
    assert 'one' in text    # retried and delivered
    assert 'two' in text    # still routed afterward

def test_fix_retry_heals_formatter():
    f = ExplodingFormatter()
    received = []
    def fix(involved, exception):
        f.explode = False         # "fixed it!"
        return True

    log = big.Log(received, formatter=f, fix=fix, threaded=False)
    log('one')
    f.explode = True
    log('two')                    # faults once, fix heals, retry succeeds
    log.flush()
    log.close()
    text = ''.join(received)
    assert 'one' in text
    assert 'two' in text


def test_fix_declining_means_knowing():
    # fix is consulted on the fault; returning false means the
    # drop follows immediately--the user was told, by definition
    calls = []
    def fix(involved, exception):
        calls.append((involved, exception))
        return False

    def bad(msg):
        raise OSError('disk full')

    good = []
    log = big.Log(bad, good, fix=fix, threaded=False)
    log('one')
    log('two')
    log.flush()
    log.close()

    assert len(calls) == 1             # one fault, one call
    assert isinstance(calls[0][1], OSError)
    assert good                       # survivor still logs

def test_optimistic_fix_not_called_for_final_drop():
    # documented subtlety: a fix that keeps returning true until
    # retries is exhausted is NOT called again for the drop
    fix_calls = []
    write_attempts = []

    def optimist(involved, exception):
        fix_calls.append(1)
        return True

    def bad(msg):
        write_attempts.append(1)
        raise OSError('still broken')

    log = big.Log(bad, [], fix=optimist, retries=3, threaded=False)
    log('x')
    log.flush()
    log.close()

    assert len(fix_calls) == 3         # consulted per retry...
    assert len(write_attempts) == 4    # ...1 fault + 3 retries
        # ...and the drop happened without a fourth fix call


def test_fix_must_be_callable():
    with raises(TypeError):
        big.Log([], fix=42)


def test_callers_dict_unchanged():
    my_dict = big.unicode_format_dict()
    original_prefix = my_dict['prefix']
    original_formats = set(my_dict['formats'])

    tf = big.TextFormatter(
        my_dict,
        prefix='>>> ',
        formats={'box': None, 'mine': {'template': '{prefix}~{message}~\n'}},
    )

    assert my_dict['prefix'] == original_prefix
    assert set(my_dict['formats']) == original_formats
    # ...while the formatter itself got the changes
    assert tf.format_dict['prefix'] == '>>> '
    assert 'box' not in tf.format_dict['formats']
    assert 'mine' in tf.format_dict['formats']

def test_two_formatters_from_one_dict():
    shared = big.unicode_format_dict()
    a = big.TextFormatter(shared, prefix='A| ')
    b = big.TextFormatter(shared, prefix='B| ')
    assert a.format_dict['prefix'] == 'A| '
    assert b.format_dict['prefix'] == 'B| '


def test_root_pause_silences_child_handles():
    collected = []
    log = testing_log(collected)
    child = log.enter('block')
    child('before pause')
    log.pause()
    child('while root paused')      # the old leak
    assert child.paused   # and the property says so
    log.resume()
    child('after resume')
    log.exit()
    log.close()
    out = ''.join(collected)
    assert 'before pause' in out
    assert 'while root paused' not in out
    assert 'after resume' in out

def test_child_pause_leaves_root_running():
    collected = []
    log = testing_log(collected)
    child = log.child('side')
    child.pause()
    child('silenced')
    log('root still logging')
    assert not (log.paused)
    child.close()
    log.close()
    out = ''.join(collected)
    assert 'silenced' not in out
    assert 'root still logging' in out

def test_explicit_child_pause_is_its_own():
    collected = []
    log = testing_log(collected)
    child = log.child('born-paused', paused=True)
    child('never seen')
    child.resume()                   # its own counter, its own resume
    child('now visible')
    child.close()
    log.close()
    out = ''.join(collected)
    assert 'never seen' not in out
    assert 'now visible' in out

def test_enter_while_ancestor_paused_is_inert():
    collected = []
    log = testing_log(collected)
    child = log.child('side')
    log.pause()
    cm = child.enter('ghost')        # ancestor paused: inert
    with cm:
        pass
    log.resume()
    child.close()
    log.close()
    assert 'ghost' not in ''.join(collected)


def test_paused_exit_closes_and_banners():
    collected = []
    log = big.Log(collected, threaded=False)
    log('body')
    log.enter('block')
    log('inside')

    log.pause()
    log('suppressed')             # logging methods are ignored...
    inert = log.enter('ghost')    # ...enter creates nothing...
    with inert:
        pass
    log.exit()                    # ...but exit still closes 'block'
    log.resume()

    log('after')
    log.flush()
    log.close()

    out = ''.join(collected)
    assert 'exit' in out                    # banner emitted
    assert 'suppressed' not in out
    assert 'ghost' not in out
    assert log.nesting == ()
    # and 'after' is back at root indentation: it follows the
    # exit banner, not indented block content
    after_line = [l for l in out.splitlines() if 'after' in l][0]
    inside_line = [l for l in out.splitlines() if 'inside' in l][0]
    assert after_line.index('after') < inside_line.index('inside')


def test_write_preserves_everything():
    collected = []
    log = big.Log(collected, threaded=False)
    log.write('trailing spaces:   \nno final newline')
    log.flush()
    log.close()
    chunk = [c for c in collected if 'trailing' in c][0]
    assert chunk == 'trailing spaces:   \nno final newline'

def test_consecutive_writes_concatenate():
    collected = []
    log = big.Log(collected, threaded=False)
    log.write('a')
    log.write('b')
    log.write('c\n')
    log.flush()
    log.close()
    text = ''.join(c for c in collected if c in ('a', 'b', 'c\n'))
    assert text == 'abc\n'

def test_custom_verbatim_format():
    collected = []
    formatter = big.TextFormatter(
        big.ascii_format_dict(),
        formats={'raw': {'template': '>{message}', 'verbatim': True},
                 'cooked': {'template': '>{message}'}},
    )
    log = big.Log(collected, threaded=False, formatter=formatter)
    log('data   ', format='raw')
    log('data   ', format='cooked')
    log.flush()
    log.close()
    assert '>data   ' in collected          # verbatim: spaces live
    assert '>data\n' in collected           # cooked: rstripped + newline


def test_numeric_thread_specs_survive_banners():
    collected = []
    formatter = big.TextFormatter(
        big.ascii_format_dict(),
        formats={'idents': {'template': '{prefix}[{thread.ident:d}] {message}\n'}},
    )
    log = big.Log(collected, threaded=False, formatter=formatter)
    log('real message', format='idents')   # real thread: ident formats as int
    log.flush()
    log.close()                            # banners rendered: must not fault

    out = ''.join(collected)
    assert 'real message' in out
    assert 'Log start' in out        # the banner rendered...
    assert 'Log finish' in out       # ...and so did this one
    # and the formatter survived to the end (never unrouted)
    import threading
    assert f'[{threading.current_thread().ident}]' in out

def test_empty_value_honors_alignment():
    v = big.log._EMPTY_VALUE
    assert format(v, '>12') == ' ' * 12   # prefix-style padding
    assert format(v, 'd') == ''
    assert format(v, '09d') == ' ' * 9
    assert str(v) == ''


def test_sink_accumulates_across_reset():
    sink = big.Sink()
    log = big.Log(sink, threaded=False)
    log('generation one')
    log.reset()
    log('generation two')
    log.flush()
    log.close()

    events = list(sink)
    generations = {e.session for e in events}
    assert generations == {1, 2}
    messages = [e.message for e in events if getattr(e, 'message', None)]
    assert 'generation one' in messages     # history survived reset
    assert 'generation two' in messages

def test_sink_clear():
    sink = big.Sink()
    log = big.Log(sink, threaded=False)
    log('before')
    log.flush()
    sink.clear()
    assert len(sink) == 0
    log('after')
    log.flush()
    log.close()
    messages = [e.message for e in sink if getattr(e, 'message', None)]
    assert 'before' not in messages
    assert 'after' in messages


def render(format_dict, message='hello', enter=None):
    collected = []
    log = big.Log(collected, threaded=False,
                  formatter=big.TextFormatter(format_dict, width=40,
                                              formats={'start': None, 'end': None}))
    if enter:
        with log.enter(enter):
            log(message)
    else:
        log(message, format='box')
    log.flush()
    log.close()
    return ''.join(collected)

def test_default_is_open_unicode():
    # a default-constructed TextFormatter uses the open unicode tree
    assert big.TextFormatter().format_dict == big.unicode_format_dict()
    collected = []
    log = big.Log(collected, threaded=False)
    log('x', format='box')
    log.flush()
    log.close()
    out = ''.join(collected)
    assert '┌' in out               # unicode box art
    assert '┐' not in out            # ...and it's open

def test_ascii_formatter_default_is_open_ascii():
    # a default-constructed ASCIIFormatter uses the open ASCII tree
    assert big.ASCIIFormatter().format_dict == big.ascii_format_dict()

def test_open_unicode_enter_has_no_lid():
    out = render(big.unicode_format_dict(),
                      enter='subsystem')
    assert '┃enter┃' in out
    assert '┳' not in out            # no T anywhere
    assert '┱' not in out

def test_open_ascii_enter_keeps_its_lid():
    out = render(big.ascii_format_dict(),
                      enter='subsystem')
    assert '|enter|' in out
    assert '+-----+' in out         # the lid, T rendered as +

def test_closed_boxes_align():
    # the alignment invariant: every line of a closed box is
    # exactly the same character length
    for closed_dict in (big.unicode_format_dict(closed=True),
                        big.ascii_format_dict(closed=True)):
        out = render(closed_dict, message='hello')
        box_lines = [l for l in out.splitlines() if l]
        lengths = {len(l) for l in box_lines}
        assert len(lengths) == 1, f'ragged box: {box_lines!r}'

def test_closed_box_overflow_omits_right_border():
    # a line whose content overflows the width runs open rather
    # than wearing a border glued onto the overflow
    long_message = 'this message is far wider than forty characters, oh dear'
    out = render(big.ascii_format_dict(closed=True),
                      message=long_message)
    message_line = [l for l in out.splitlines() if 'oh dear' in l][0]
    assert not (message_line.endswith('|'))
    # while the border lines still close, at exactly the width
    border_lines = [l for l in out.splitlines() if l.endswith('+')]
    assert border_lines
    assert all(len(l) == 40 for l in border_lines)


def test_dot_reserved_in_formats_parameter():
    with raises(ValueError) as cm:
        big.TextFormatter(formats={'a.b': {'template': '{message}\n'}})
    assert 'reserved for future namespacing' in str(cm.exception)

def test_dot_reserved_in_format_dict():
    d = big.unicode_format_dict()
    d['formats']['a.b'] = {'template': '{message}\n'}
    with raises(ValueError):
        big.TextFormatter(d)

def test_optional_is_a_str():
    o = big.log.Optional('box')
    assert isinstance(o, str)
    assert o == 'box'

def test_optional_falls_back_silently():
    collected = []
    log = big.Log(collected, threaded=False)
    log('hi', format=big.log.Optional('no-such-format'))
    log.flush()
    log.close()
    assert 'hi' in ''.join(collected)     # default format used

def test_undefined_bare_name_raises():
    collected = []
    log = big.Log(collected, threaded=False)
    with raises(ValueError):
        log('hi', format='no-such-format')
    log.close()

def test_sink_event_format_is_a_name():
    # SinkLogEvent.format used to leak the internal tuple path
    # ('', 'enter'); it's the plain name now
    sink = big.Sink()
    log = big.Log(sink, threaded=False)
    log('body')
    with log.enter('block'):
        log('inside')
    log.flush()
    log.close()
    formats = {e.type: e.format for e in sink if hasattr(e, 'format')}
    assert formats.get('enter') == 'enter'
    assert formats.get('exit') == 'exit'


def test_reserved_formats_rejected():
    collected = []
    log = big.Log(collected, threaded=False)
    for name in ('start', 'end', 'enter', 'exit'):
        with subtest(name=name):
            with raises(ValueError):
                log('gotcha', format=name)
            with raises(ValueError):
                log('gotcha', format=big.log.Optional(name))
    log.close()

def test_machinery_defaults_still_pass():
    collected = []
    log = big.Log(collected, threaded=False)
    log('via print')                                    # Optional('print')
    log.log('via log')                                  # Optional('log')
    log.write('via write\n')                            # Optional('preformatted')
    log('explicit', format=big.log.Optional('log'))
    log.flush()
    log.close()
    out = ''.join(collected)
    for expected in ('via print', 'via log', 'via write', 'explicit'):
        assert expected in out


def test_renders_bytes():
    collected = []
    log = big.Log(collected, formatter=big.ASCIIFormatter(), threaded=False)
    log('hello')
    log.flush()
    log.close()
    assert collected
    assert all(isinstance(o, bytes) for o in collected)
    assert b'hello' in b''.join(collected)

def test_non_ascii_never_crashes():
    # regression: log('café') raised UnicodeEncodeError at the
    # call site--the one place user data could detonate before
    # reaching the fault ladder.  non-ASCII now renders with
    # backslash escapes: nothing fails, nothing is lost.
    for threaded in (False, True):
        with subtest(threaded=threaded):
            collected = []
            log = big.Log(collected, formatter=big.ASCIIFormatter(),
                          threaded=threaded)
            log('café')
            log.log('touché', note='olé')
            log.flush()
            log.close()
            output = b''.join(collected)
            assert rb'caf\xe9' in output
            assert rb'touch\xe9' in output
            assert rb'note=ol\xe9' in output


def test_log_properties():
    ns = big.log.default_clock()
    epoch = time.time()
    time.sleep(0.001)

    a = []
    log = big.Log(a)

    assert log.clock == big.log.default_clock
    assert log.name == 'Log'
    assert log.threaded == True
    assert log.timestamp_clock == time.time

    assert log.closed == False
    assert log.start_time_ns > ns
    assert log.start_time_epoch > epoch
    assert log.nesting == ()

    log.enter("xyz")
    log.flush()
    assert len(log.nesting) == 1
    assert log.nesting[0].message == 'xyz'


def test_log_default_destination():
    # With no destinations specified, should use print
    captured = []
    original_print = builtins.print
    builtins.print = lambda *args, **kwargs: captured.append((args, kwargs))
    try:
        log = testing_log()
        log("test message")
        log.close()
    finally:
        builtins.print = original_print
    assert captured == [(("test message\n",), {'end': ''}), (("",), {'end': '', 'flush': True})]

def test_log_with_list():
    array = []
    log = testing_log(array)
    log("hello")
    log.close()
    assert array == ["hello\n"]

def test_log_with_path_string():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        path = f.name

    try:
        log = testing_log(path)
        log("test message")
        log.close()

        with open(path, 'r') as f:
            content = f.read()
        assert "test message\n" == content
    finally:
        os.unlink(path)

def test_log_with_callable():
    results = []
    log = testing_log(results.append)
    log("callable test")
    log.close()
    assert results == ['callable test\n']

def test_log_with_invalid_destinations():
    with raises(TypeError) as cm:
        log = big.Log(12345, threaded=False)
    assert "don't know how to log to destination" in str(cm.exception)


def test_extensible_destination_mapper():
    with raises(TypeError) as cm:
        log = big.Log(12345, threaded=False)


    try:
        # undocumented interface!
        def custom_destination_mapper(o):
            if isinstance(o, int):
                return EventSink()
            return None

        big.log.LogDestination.mappers.append(custom_destination_mapper)
        log = testing_log(12345, [], print)
        destinations = list(log._destinations)
        assert isinstance(destinations[0], EventSink)
        assert isinstance(destinations[1], big.log.List)
        assert isinstance(destinations[2], big.log.Print)
    finally:
        big.log.LogDestination.mappers.clear()

def test_exit_without_logging_or_enter():
    sink = EventSink()
    log = testing_log(sink)
    log.exit()
    log.close()
    assert not (sink.value)

def test_log_after_closed():
    array = []
    log = testing_log(array)
    log.close()
    log("after close")
    log.close()
    assert not (array)

def test_log_write_after_closed():
    array = []
    log = testing_log(array)
    log.close(wait=False)
    log.write("after close")
    log.close(wait=True)
    assert not (array)

def test_log_heading_after_closed():
    array = []
    log = testing_log(array)
    log.close()
    log.box("after close")
    log.close()
    assert not (array)

def test_log_close_is_idempotent():
    array = []
    log = testing_log(array)
    assert not (log.closed)
    log.close()
    assert log.closed
    log.close()
    assert log.closed

def test_log_dirty():
    array = []
    log = testing_log(array)
    assert not (log.dirty)
    log.write("hello pigpen!\n")
    assert log.dirty
    log.flush()
    assert not (log.dirty)

def test_log_atexit():
    for threading in (False, True):
        for log_once in (False, True):
            with subtest(threaded=threading, log_once=log_once):
                log = testing_log([], threaded=threading)
                assert not (log.closed)
                if log_once:
                    log("hello!")
                    log.flush()
                log._atexit()
                assert log.closed
                # log ignores reset after atexit
                log.reset()
                assert log.closed

def test_log_name():
    log = big.Log(name='xyz')
    assert log.name == 'xyz'
    log.close()

    with raises(TypeError):
        big.Log(name=385)

    with raises(TypeError):
        big.Log(name=3.1415)

    with raises(TypeError):
        big.Log(name=[1, 2, 3])

    with raises(TypeError):
        big.Log(name={1:2})

    with raises(ValueError):
        big.Log(name='')




def test_print():
    array = []
    log = testing_log(array)
    log.print("via print method")
    log.close()
    assert array == ["via print method\n"]

def test_multiline_print():
    buffer = io.StringIO()
    log = testing_log(buffer, prefix='[-] ')
    log("This message has multiple lines!\nHere's line two.\n  Line three is indented a little!\nAnd this is the final line.")
    log.close()
    assert buffer.getvalue() == """
[-] This message has multiple lines!
[-] Here's line two.
[-]   Line three is indented a little!
[-] And this is the final line.
""".lstrip()

def test_log_write():
    array = []
    log = testing_log(array)
    log.write("raw write\n")
    log.close()
    assert array == ["raw write\n"]

def test_log_write_not_string():
    array = []
    log = testing_log(array)
    with raises(TypeError):
        log.write(12345)
    log.close()

def test_log_blank_line():
    s = io.StringIO()
    log = testing_log(s, prefix='[PREFIX] ')
    log("before")
    log() # should inject an empty line into the log (but should still have the prefix)
    log("after")
    log.close()
    assert s.getvalue() == "[PREFIX] before\n[PREFIX]\n[PREFIX] after\n"

def test_log_box():
    s = io.StringIO()
    log = testing_log(s, prefix='(/) ')
    log.box("call-out text")
    log.close()
    assert s.getvalue() == """
(/) +--------------------------------------------------------------------------
(/) | call-out text
(/) +--------------------------------------------------------------------------
""".lstrip()

def test_multiline_box():
    buffer = io.StringIO()
    log = testing_log(buffer, prefix='[#] ')
    log.box("Multi-line box!\n  Very pretty.")
    log.close()
    assert buffer.getvalue() == """
[#] +--------------------------------------------------------------------------
[#] | Multi-line box!
[#] |   Very pretty.
[#] +--------------------------------------------------------------------------
""".lstrip()

def test_log_box_not_string():
    s = io.StringIO()
    log = testing_log(s, width=7)
    log.box(12345)
    log.close()
    assert s.getvalue() == "+------\n| 12345\n+------\n"

def test_log_empty_thread():
    s = io.StringIO()
    log = testing_log(s, formats={"start": {'template': "thread.name={thread.name} thread={thread} thread!r={thread!r} thread.ident={thread.ident} thread.native_id={thread.native_id} thread.daemon={thread.daemon}"}})
    log('boo')
    log.close()
    assert s.getvalue() == "thread.name= thread= thread!r= thread.ident= thread.native_id= thread.daemon=\nboo\n"

def test_log_enter_exit():
    s = io.StringIO()
    log = testing_log(s, prefix='(*) ')
    log.enter("subsystem")
    log("inside")
    log.exit()
    log.close()
    assert s.getvalue() == """
(*) +-----+--------------------------------------------------------------------
(*) |enter| subsystem
(*) +-----+--------------------------------------------------------------------
(*)     inside
(*) +-----+--------------------------------------------------------------------
(*) |exit | subsystem
(*) +-----+--------------------------------------------------------------------
""".lstrip()

def test_multiline_enter():
    s = io.StringIO()
    log = testing_log(s, prefix='[_] ')
    with log.enter("Multi-line enter!\nWhat will happen?"):
        log("zzz...")
    log.close()
    assert s.getvalue() == """
[_] +-----+--------------------------------------------------------------------
[_] |enter| Multi-line enter!
[_] |     | What will happen?
[_] +-----+--------------------------------------------------------------------
[_]     zzz...
[_] +-----+--------------------------------------------------------------------
[_] |exit | Multi-line enter!
[_] |     | What will happen?
[_] +-----+--------------------------------------------------------------------
""".lstrip()

def test_log_enter_context_manager():
    s = io.StringIO()
    log = testing_log(s, width=20)
    with log.enter("froot broot"):
        log("and here we are")
    log.close()
    assert s.getvalue() == """
+-----+-------------
|enter| froot broot
+-----+-------------
    and here we are
+-----+-------------
|exit | froot broot
+-----+-------------
""".lstrip()

def test_log_unbalanced_exit():
    s = io.StringIO()
    log = testing_log(s, width=16)
    log.enter("entered!")
    log.exit()
    log.exit()
    log.exit()
    log.close()
    assert s.getvalue() == """
+-----+---------
|enter| entered!
+-----+---------
+-----+---------
|exit | entered!
+-----+---------
""".lstrip()

def test_reuse_log():
    s = io.StringIO()
    log = testing_log(s, formats={'start': {'template': 'START'}, 'end': {'template': 'END'}})
    log.write("before reset\n")
    log.close()
    log.reset()
    log.write("after reset\n")
    log.close()
    assert s.getvalue() == """
START
before reset
END
START
after reset
END
""".lstrip()

def test_log_sep_end_params():
    s = io.StringIO()
    log = testing_log(s)
    log("a", "b", "c", sep="-", end="!\n")
    log.close()
    assert s.getvalue() == "a-b-c!\n"

    with raises(TypeError):
        log(35, sep=35)
    with raises(TypeError):
        log(36, end=36)
    with raises(TypeError):
        log.print(37, sep=37)
    with raises(TypeError):
        log.print(38, end=38)

def test_log_with_flush_param():
    s = io.StringIO()
    log = testing_log(s)
    log("flushed message!", flush=True)
    assert "flushed message!\n" == s.getvalue()
    log.close()

def test_blank_enter_and_exit_before_formatted_logging():
    s = io.StringIO()
    log = testing_log(s, formats={'enter': None, 'exit': None})
    log.enter('subsystem')
    log.exit()
    o = log.enter('subsystem 2')
    assert isinstance(o, big.Log._ExitContextManager)
    with o:
        with log.enter('subsystem 3'):
            log('finally!')
    log.close()
    assert s.getvalue() == '        finally!\n'

def test_log_messages_after_close():
    s = io.StringIO()
    log = testing_log(s)
    log("kooky!")
    log.close()
    log.box("nope")
    log.write("nope\n")
    o = log.enter("nope")
    assert isinstance(o, big.Log._InertContextManager)
    with o:
        log("nope")
    log.pause()
    log.resume()
    log.reset()
    log("wonderful!")
    assert s.getvalue() == "kooky!\nwonderful!\n"

def test_log_unwinds_enters_at_close():
    s = io.StringIO()
    log = testing_log(s,
        formats={'enter': {'template': '{prefix}//enter {message}//'}, 'exit': {'template': '{prefix}//exit {message}//'}})
    log("miasma")
    log.enter('verrifast')
    log.enter('boodle boy')
    log('and here we are.')
    log.close()
    assert s.getvalue() == """
miasma
//enter verrifast//
    //enter boodle boy//
        and here we are.
    //exit boodle boy//
//exit verrifast//
""".lstrip()


def test_formats_exceptions():
    # formats= lives on TextFormatter (Log's formats= convenience
    # was removed: formatter configuration belongs to the formatter)
    with raises(TypeError):
        big.Log(formats={"mixmox": None})
    with raises(ValueError):
        big.TextFormatter(formats={"mixmox": None})
    with raises(TypeError):
        big.TextFormatter(formats={83: {"template": "abc", "line": "-"}})
    with raises(TypeError):
        # formats value must be dict
        big.TextFormatter(formats={"splunk": 55})
    with raises(ValueError):
        # format dict must contain template
        big.TextFormatter(formats={"splunk": {"zippy": "howdy doodles!"}})
    with raises(TypeError):
        # format dict template value must be str
        big.TextFormatter(formats={"splunk": {"template": 33}})

    with raises(ValueError):
        # format dict can't have message
        big.TextFormatter(formats={"splunk": {"template": "xyz", "message": "hello dere!"}})

    l = big.Log(formatter=big.TextFormatter(formats={"start": None, "end": None}))
    with raises(ValueError):
        l.print("abc", format="spooky")
    l.close()

    # you're allowed to use format names that collide with Log methods,
    # as well as format names containing spaces.
    # you just won't get the prebound method (a la "box", "peanut", etc).
    s = io.StringIO()
    l = testing_log(s, formats={
        "reset": {"template": "_reset_{line*}\n{message}\n{line*}", "line*": "_"},
        "has two spaces": {"template": "#has two spaces#{line*}\n{message}\n{line*}", "line*": "#"}},
        width=20)
    l('dis is rasat', format='reset')
    l('has spacings', format='has two spaces')
    l.close()
    assert s.getvalue() == """
_reset______________
dis is rasat
____________________
#has two spaces#####
has spacings
####################
""".lstrip()



def test_fix_may_touch_routing():
    # the fault handler calls fix() *without* holding the
    # configuration lock, so a fix callback may legitimately
    # call log.route()--e.g. to route a replacement for a
    # destination that's died.  configuration_lock is a plain
    # Lock (not an RLock!); the discipline that keeps it one
    # is "never call foreign code while holding it", and this
    # test is the canary: if someone reintroduces a
    # callback-under-lock, this deadlocks instead of rotting.

    class Doomed(big.log.LogDestination):
        def __init__(self):
            super().__init__(types=True)

        def __eq__(self, other):
            return other is self

        def __hash__(self):
            return id(self)

        def write(self, o):
            raise RuntimeError("doomed")

    good = []
    log = None

    def fix(involved, fault):
        # route a replacement...
        log.route(log.formatter, good)
        # ...but report the doomed destination unfixed,
        # so it gets unrouted
        return False

    log = testing_log(Doomed(), fix=fix)
    log("first")        # Doomed faults; fix() routes `good`; Doomed is unrouted
    log("second")
    log.close()

    joined = ''.join(good)
    assert "second" in joined
    assert "doomed" not in joined


def test_no_log_means_no_banners():
    s = io.StringIO()
    sink = EventSink()
    log = testing_log(s, sink, formats={"start": {"template": "START"}, "end": {"template": "END"}}, prefix='[PREFIX] ', width=20)
    log.close()

    expected = ''
    assert s.getvalue() == expected
    assert sink.value == ""


def test_empty_template_still_logs():
    # an empty template is not special: the message wakes the log
    # (banners and all) and renders as a blank line.  the log
    # doesn't second-guess the user's formatter graph.
    s = io.StringIO()
    sink = EventSink()
    log = testing_log(s, sink, formats={"start": {"template": "START"}, "end": {"template": "END"}, "print": {"template": ''}}, width=20)
    log('')
    log.close()

    assert s.getvalue() == 'START\n\nEND\n'
    assert 'start' in sink.value
    assert 'end' in sink.value

def test_lazy_start_from_log():
    s = io.StringIO()
    log = testing_log(s, formats={"start": {"template": "START"}, "end": {"template": "END"}}, prefix='[PREFIX] ', width=20)
    log("howdy!")
    log.close()

    expected = """
START
[PREFIX] howdy!
END
""".lstrip()
    assert s.getvalue() == expected

def test_lazy_start_from_write():
    s = io.StringIO()
    log = testing_log(s, formats={"start": {"template": "START"}, "end": {"template": "END"}}, prefix='[PREFIX] ', width=20)
    log.write("howdy!\n")
    log.close()

    expected = """
START
howdy!
END
""".lstrip()
    assert s.getvalue() == expected

def test_lazy_start_from_heading():
    s = io.StringIO()
    log = testing_log(s, formats={"start": {"template": "START"}, "end": {"template": "END"}}, prefix='[PREFIX] ', width=20)
    log.box("howdy!")
    log.close()

    expected = """
START
[PREFIX] +----------
[PREFIX] | howdy!
[PREFIX] +----------
END
""".lstrip()
    assert s.getvalue() == expected

def test_lazy_start_from_enter():
    s = io.StringIO()
    log = testing_log(s, formats={"start": {"template": "START"}, "end": {"template": "END"}}, prefix='[PREFIX] ', width=20)
    with log.enter("howdy!"):
        log("woah!")
    log.close()

    expected = """
START
[PREFIX] +-----+----
[PREFIX] |enter| howdy!
[PREFIX] +-----+----
[PREFIX]     woah!
[PREFIX] +-----+----
[PREFIX] |exit | howdy!
[PREFIX] +-----+----
END
""".lstrip()

    assert s.getvalue() == expected

def test_log_permanently_paused():
    sink = big.Log.Sink()
    log = big.Log(sink, threaded=False)
    log.pause()
    log('howdy')
    log.enter('hey you')
    with log.enter('yoo-hoo'):
        log("over here")
        log.box('hey there')
    log.close()
    events = list(sink)
    assert len(events) == 0

def test_log_paused():
    s = io.StringIO()
    log = testing_log(s)
    assert not (log.paused_on_reset)
    assert not (log.paused)
    log.pause()
    log('howdy')
    log.enter('hey you')
    with log.enter('yoo-hoo'):
        log.box('hey there')
    log.exit()
    log.close()
    assert not (log.paused_on_reset)
    assert log.paused is None
    assert s.getvalue() == ''

    log = testing_log(s, paused=True)
    assert log.paused_on_reset
    assert log.paused
    log('howdy')
    log.close()
    assert log.paused_on_reset
    assert log.paused is None
    assert s.getvalue() == ''

    log = testing_log(s, paused=True)
    assert log.paused_on_reset
    assert log.paused
    log.resume()
    log.reset()
    assert log.paused_on_reset
    assert log.paused
    log('howdy')
    log.close()
    assert log.paused_on_reset
    assert log.paused is None
    assert s.getvalue() == ''

    log = testing_log(s, paused=False)
    assert not (log.paused_on_reset)
    assert not (log.paused)
    log.resume()
    log('howdy')
    log.close()
    assert not (log.paused_on_reset)
    assert log.paused is None
    assert s.getvalue() == 'howdy\n'
    log.reset()
    assert not (log.paused_on_reset)
    assert not (log.paused)

    s = io.StringIO()
    log = testing_log(s)
    log.pause()
    log('doody')
    log.reset()
    log('howdy')
    log.close()
    assert not (log.paused_on_reset)
    assert log.paused is None
    assert s.getvalue() == 'howdy\n'

    o = log.pause()
    assert log.paused is None
    assert isinstance(o, big.Log._InertContextManager)

def test_log_paused_vs_enter():
    "with log.enter(): doesn't call log.exit() when you outdent from the with block."
    s = io.StringIO()
    log = testing_log(s)
    log.pause()
    o = log.enter('ignored')
    assert isinstance(o, big.Log._InertContextManager)
    with o:
        log('also ignored')
        log.resume()
        log('doody')
    log('howdy')
    assert not (log.paused)
    log.close()
    assert not (log.paused_on_reset)
    assert log.paused is None
    assert s.getvalue() == 'doody\nhowdy\n'

def test_log_paused_journey():
    # wrote this in an email to demonstrate all the features;
    # figured it'd work fine as a test.
    # by default, log objects aren't paused.
    log = big.Log()
    assert log.paused is False

    # this log starts out in paused state
    log = big.Log(paused=True)
    assert log.paused is True
    assert log._paused_counter == 1

    # log is no longer paused
    log.resume()

    # paused is a read-only property, always a bool
    assert log._paused_counter == 0
    assert log.paused is False

    # log is now paused
    log.pause()
    assert log.paused is True
    assert log._paused_counter == 1

    # context manager calls resume on exit
    o = log.pause()
    assert isinstance(o, big.Log._ResumeContextManager)

    with o:
        # actual pause value is an internal counter.
        # pause increments, resume decrements.
        # internal pause counter is now 2.

        log("this is totes ignored")

        # but user never sees the integer value of the pause counter.
        assert log.paused is True
        assert log._paused_counter == 2

    # automatic log.resume() when we exit the "with log.pause():" block,
    # internal pause counter is now 1 again.
    assert log.paused is True
    assert log._paused_counter == 1

    # internal pause counter is now 0.
    log.resume()
    assert log.paused is False
    assert log._paused_counter == 0

    # still 0--we clamp at 0.
    log.resume()
    assert log.paused is False
    assert log._paused_counter == 0
    log.resume()
    assert log.paused is False
    assert log._paused_counter == 0
    log.resume()
    assert log.paused is False
    assert log._paused_counter == 0
    log.resume()
    assert log.paused is False
    assert log._paused_counter == 0

    # internal pause counter is now 1.
    log.pause()
    assert log.paused is True
    assert log._paused_counter == 1

    # back to zero--
    log.resume()
    assert log.paused is False
    assert log._paused_counter == 0

    # reset *resets* paused state.
    # after reset, internal pause counter = int(self.pause_on_resume)
    # just like it was immediately after construction.
    log.reset()
    assert log.paused is True
    assert log._paused_counter == 1

    log.paused_on_reset = False
    log.reset()
    assert log.paused is False
    assert log._paused_counter == 0

    log.paused_on_reset = 35
    log.reset()
    assert log.paused is True
    assert log._paused_counter == 1
    log.resume()
    assert log.paused is False
    assert log._paused_counter == 0

        # you can't change pause state while


def test_log_context_manager():
    array = []
    with testing_log(array) as log:
        log("inside with block")
    # After exiting, flush should have been called
    assert any("inside with block" in s for s in array)


def test_log_threaded():
    array = []
    log = testing_log(array, threaded=True)
    log("threaded message")
    log.write("threaded write")
    log.close()
    assert any("threaded message" in s for s in array)
    assert any("threaded write" in s for s in array)

def test_log_threaded_multiple_messages():
    array = []
    log = testing_log(array, threaded=True)
    for i in range(10):
        log(f"message {i}")
    log.close()
    output = ''.join(array)
    for i in range(10):
        assert f"message {i}" in output

def test_log_threaded_enter_exit():
    array = []
    log = testing_log(array, threaded=True)
    with log.enter("threaded subsystem"):
        log("inside threaded")
    log.close()
    output = ''.join(array)
    assert "threaded subsystem" in output

def test_log_threaded_reset():
    array = []
    log = testing_log(array, threaded=True)
    log("before")
    log.reset()
    log("after")
    log.flush()

    text = "\n".join(array)
    assert 'before' in text
    assert 'after' in text

def test_log_threaded_reset_after_close():
    array = []
    log = testing_log(array, threaded=True)
    log("before")
    log.close()
    log("dropped")
    log.reset()
    log("after")
    log.flush()

    text = "\n".join(array)
    assert 'before' in text
    assert 'after' in text
    assert 'dropped' not in text

def test_log_threaded_box():
    array = []
    log = testing_log(array, threaded=True)
    log.box("threaded heading")
    log.close()
    assert any("threaded heading" in s for s in array)

def test_log_threaded_blocking_flush():
    array = []
    buffer = big.log.Buffer(array)
    log = testing_log(array, threaded=True)
    log("message")
    text = "\n".join(array)
    assert 'message' not in text
    log.flush()
    text = "\n".join(array)
    assert 'message' in text

def test_log_threaded_asynchronous_flush():
    array = []
    buffer = big.log.Buffer(array)
    log = testing_log(array, threaded=True)
    log("message")
    text = "\n".join(array)
    assert 'message' not in text
    log.flush(wait=False)
    waiter = wait_for_job(log)
    log.write("sentinel")
    waiter()
    text = "\n".join(array)
    assert 'message' in text

def test_log_flush_closed_error():
    array = []
    log = testing_log(array, threaded=True)
    log.close()
    log.flush()


def test_log_with_prefix():
    array = []
    log = testing_log(array, prefix='[PREFIX] ')
    log("test")
    log.close()
    assert any("[PREFIX]" in s for s in array)

def test_log_with_start_and_end():
    array = []
    log = testing_log(array, formats={"start": {"template": "START"}, "end": {"template": "END"}})
    log("middle")
    log.close()
    output = ''.join(array)
    assert "START" in output
    assert "END" in output

def test_custom_format():
    s = io.StringIO()
    # peanut has multiple lines after the {message} lines
    # to exercise some specific code in Log
    log = testing_log(s,
        formats={"start": None, "end": None, "peanut": {"template": "{prefix}{line*}\n{prefix}=peanut=start{line*}\n{prefix}== {message}\n{prefix}-- {message}\n{prefix}=peanut=end{line*}\n{prefix}{line*}", "line*": "=-"}},
        prefix='[PFX] ')
    log.peanut("test\ntest2\ntest3")
    log.close()
    assert s.getvalue() == """
[PFX] =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
[PFX] =peanut=start=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
[PFX] == test
[PFX] -- test2
[PFX] -- test3
[PFX] =peanut=end=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
[PFX] =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
""".lstrip()

    # non-contiguous {message} lines
    with raises(ValueError):
        big.TextFormatter(formats={"peanut": {"template": "foo\n{message}\nbar\n{message}"}})

def test_empty_banner_template_suppresses_banners():
    s = io.StringIO()
    log = testing_log(s, prefix='[PREFIX] ', width=20)
    log("z")
    log.close()

    expected = '[PREFIX] z\n'
    assert s.getvalue() == expected

def test_empty_start_banner_template_end_still_works():
    s = io.StringIO()
    log = testing_log(s, formats={"end": {"template": "END"}}, prefix='[PREFIX] ', width=20)
    log("z")
    log.close()

    expected = '[PREFIX] z\nEND\n'
    assert s.getvalue() == expected


def test_empty_end_banner_template():
    s = io.StringIO()
    log = testing_log(s, formats={"start": {"template": "START"}}, prefix='[PREFIX] ', width=20)
    log("z")
    log.close()

    expected = 'START\n[PREFIX] z\n'
    assert s.getvalue() == expected

def test_system_formats_are_disallowed():
    a =[]
    log = big.Log(a, threaded=False)

    with raises(ValueError):
        log("w", format='start')
    with raises(ValueError):
        log("x", format='end')
    with raises(ValueError):
        log("y", format='enter')
    with raises(ValueError):
        log("z", format='exit')
    log.close()



def test_sink_basic():
    sink = big.Log.Sink()
    log = testing_log(sink)
    log("message1")
    log("message2")
    log.close()

    events = list(sink)
    assert len(events) == 4

    assert isinstance(events.pop(0), log_module.SinkStartEvent)

    assert isinstance(events.pop(), log_module.SinkEndEvent)

    for i, e in enumerate(events, 1):
        assert isinstance(e, log_module.SinkLogEvent)
        assert e.depth == 0
        assert e.duration >= 0
        assert e.elapsed > 0
        assert e.message.startswith('message')
        assert e.message.endswith(str(i))
        assert e.session == 1
        assert e.thread == threading.current_thread()

    e = events[0]
    clone = e._calculate_duration(events[1])
    assert e == clone
    assert e != events[1]
    assert e < events[1]

    with raises(TypeError):
        e < 3.1415

    sse = big.SinkStartEvent(1, 5, 10, {})
    assert repr(sse) == "SinkStartEvent(session=1, ns=5, epoch=10, configuration={}, duration=0)"

def test_sink_event_types():
    sink = big.Log.Sink()
    log = big.Log(sink, threaded=False)
    log("regular event")
    log.write("write event")
    log.box("heading event")
    with log.enter("enter event"):
        pass
    log.close()
    log.reset()

    SinkEvent = log_module.SinkEvent

    events = list(sink)
    types = [e.type for e in events]
    Sink = big.Log.Sink
    assert 'start' in types
    assert 'end' in types
    assert 'write' in types
    assert 'log' in types
    assert 'enter' in types
    assert 'exit' in types

    # coverage stuff
    # exercise __hash__ on every sink event type
    events_map = dict.fromkeys(events, None)
    session = 1
    for e in events:
        with subtest(e=e):
            assert e.session == session
            if isinstance(e, big.log.SinkEndEvent):
                session += 1
            else:
                assert e.duration >= 0


def test_sink_events_without_any_logging():
    sink = big.Log.Sink()
    log = big.Log(sink, threaded=False)
    log.close()
    log.reset()
    log.close()

    events = list(sink)
    assert len(events) == 0


def test_sink_print():
    sink = big.Log.Sink()
    log = testing_log(sink)
    log("test event")
    log.close()

    output = []
    sink.print(print=output.append)
    assert (len(output) > 0)

def test_sink_print_default_print():
    sink = big.Log.Sink()
    log = testing_log(sink)
    log("test event")
    log.close()

    # Capture stdout
    captured = []
    original_print = builtins.print
    builtins.print = lambda *args, **kwargs: captured.append(args)
    try:
        sink.print()  # Use default print
    finally:
        builtins.print = original_print
    assert (len(captured) > 0)

def test_sink_reset():
    sink = big.Log.Sink()
    log = testing_log(sink)
    log("before reset")
    log.close()

    assert (len(list(sink)) > 0)

    log.reset()
    # After reset, sink should also be reset
    # (events cleared when re-registered)

def test_sink_write():
    sink = big.Log.Sink()
    log = testing_log(sink)
    s = "raw write\n"
    log.write(s)
    log.close()
    events = list(sink)
    assert len(events) == 3
    assert s == events[1].message

def test_sink_with_banners():
    sink = big.Log.Sink()
    log = testing_log(sink, name='Sink', formats={"start": {"template": "{name} START"}, "end": {"template": "{name} END"}}, prefix='[PREFIX] ')
    log("message")
    log.close()

    events = list(sink)
    assert len(events) == 5

    SinkEvent = log_module.SinkEvent
    assert isinstance(events[0], big.SinkStartEvent)
    assert events[0].elapsed == 0
    assert events[0].ns > 0
    assert events[0].epoch > 0

    assert isinstance(events[1], big.SinkLogEvent)
    # the start banner is a structured event: the message is the
    # session name, and the format tells you it's a banner.  there's
    # no rendered 'Sink START\n' text--that's the consumer's job.
    assert events[1].format == 'start'
    assert events[1].message == 'Sink'

    assert isinstance(events[2], big.SinkLogEvent)
    assert events[2].message == 'message'

    assert isinstance(events[3], big.SinkLogEvent)
    assert events[3].format == 'end'
    assert events[3].message == 'Sink'

    assert isinstance(events[4], big.SinkEndEvent)
    assert events[4].elapsed > 0




def test_eventsink_events_without_any_logging():
    esink = EventSink()
    log = big.Log(esink, threaded=False)
    log.close()
    log.reset()
    log.close()

    assert esink.value == ""

def test_sink_events():
    esink = EventSink()
    log = big.Log(esink, threaded=False)
    log.write("abc")
    log("xyz")
    with log.enter("subsystem"):
        log.box("xyz")
    log.close()
    log.reset()
    log.print('hey now')
    log.close()

    # one event per message: start banner / body / end banner are
    # 'log'; write/enter/exit have their own types.  (the pre-rewrite
    # protocol fired extra 'log' callbacks alongside box and exit.)
    assert esink.value == "start log write log enter log exit log flush end start log log log flush end"



def test_old_destination_basic():
    old = big.OldDestination()
    log = testing_log(old)
    log("smedley")
    log.close()

    events = list(old)
    assert len(events) == 2
    e = events[0]
    assert e[0] == 0
    assert e[2] == 'log start'
    assert e[3] == 0
    e = events[1]
    assert e[0] > 0
    assert e[2] == 'smedley'
    assert e[3] == 0

def test_old_destination_enter_exit():
    old = big.OldDestination()
    log = testing_log(old)
    log.enter("subsystem")
    log("inside")
    log.exit()
    log.close()

    events = list(old)
    event_strs = [e[2] for e in events]
    assert "subsystem start" in event_strs
    assert "subsystem end" in event_strs

def test_old_destination_print():
    old = big.OldDestination()
    log = testing_log(old)
    log("test")
    log.close()

    output = []
    old.print(print=output.append)
    assert (len(output) > 0)

def test_old_destination_print_no_title():
    old = big.OldDestination()
    log = testing_log(old)
    log("test")
    log.close()

    output = []
    old.print(print=output.append, title=None)
    # First line should not be "[event log]"
    assert not (output[0].startswith("[event log]"))

def test_old_destination_print_no_headings():
    old = big.OldDestination()
    log = testing_log(old)
    log("test")
    log.close()

    output = []
    old.print(print=output.append, headings=False)

def test_old_destination_write():
    old = big.OldDestination()
    log = testing_log(old)
    log.write("raw write content\n")
    log.close()

    events = list(old)
    event_strs = [e[2] for e in events]
    assert "raw write content" in event_strs


pass

def test_smoke_test_log():
    clock = FakeClock()
    log = big.OldLog(clock=clock)

    log.reset()
    clock.advance()
    log.enter("subsystem")
    clock.advance()
    log('event 1')
    clock.advance()
    clock.advance()
    log('event 2')
    clock.advance()
    log.exit()
    got = []
    log.print(print=got.append, fractional_width=3)

    expected = """
[event log]
  start   elapsed  event
  ------  ------  ---------------
  00.000  00.012  log start
  00.012  00.012  subsystem start
  00.024  00.024    event 1
  00.048  00.012    event 2
  00.060  00.000  subsystem end
        """.strip().split('\n')

    assert expected == got

def test_default_settings():
    log = big.OldLog()
    log('event 1')
    buffer = []
    real_print = builtins.print
    builtins.print = buffer.append
    log.print()
    builtins.print = real_print
    got = "\n".join(buffer)
    assert "event 1" in got

def test_old_log_iter():
    log = big.OldLog()
    log("test event")
    events = list(log)
    assert (len(events) >= 2)  # log start + test event

def test_old_log_reset():
    log = big.OldLog()
    log("before")
    log.reset()
    log("after")
    events = list(log)
    event_strs = [e[2] for e in events]
    assert "after" in event_strs


def test_log_with_stringio():
    buffer = io.StringIO()
    log = testing_log(buffer)
    log("stringio test")
    log.close()
    content = buffer.getvalue()
    assert "stringio test" in content


def test_log_with_path_object():
    from pathlib import Path
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        path = Path(f.name)

    try:
        log = testing_log(path)
        log("path object test")
        log.close()

        with open(path, 'r') as f:
            content = f.read()
        assert "path object test" in content
    finally:
        os.unlink(path)


def test_custom_clock():
    clock = FakeClock()
    array = []
    log = testing_log(array, prefix='[{elapsed}] ', clock=clock)

    clock.advance(1_000_000_000)  # 1 second
    log("at 1 second")
    log.close()

    output = ''.join(array)
    assert "1" in output


def test_all_exports():
    expected = [
        'Log', 'OldDestination', 'OldLog'
    ]
    for name in expected:
        assert name in log_module.__all__


def test_duplicate_destinations():
    a = []
    log = testing_log(a, print)
    with raises(ValueError):
        log.destinations = [a, print, a]
    with raises(ValueError):
        log.destinations = [print, a, print]
    with raises(ValueError):
        log.destinations = ['/tmp/x', b'/tmp/x']
    with raises(ValueError):
        log.destinations = ['/tmp/x', pathlib.Path('/tmp/x')]
    with raises(ValueError):
        log.destinations = ['/tmp/x', '/tmp/../tmp/x']
    log.close()

def test_log_wrong_type_for_destinations():
    a = []
    b = []
    log = testing_log(a, print)
    with raises(TypeError):
        log.destinations = print
    with raises(TypeError):
        log.destinations = '/tmp/x'
    with raises(TypeError):
        log.destinations = {a, print, b}
    log.close()

def test_log_with_added_destination():
    initial = io.StringIO()
    log = testing_log(initial)
    log("first")
    log("second")

    secondary = io.StringIO()
    d = log.destinations
    d.append(secondary)
    log.destinations = d

    log("third")
    log.close()

    assert initial.getvalue() == "first\nsecond\nthird\n"
    assert secondary.getvalue() == "third\n"

def test_added_destination_gets_recap():
    # with banners enabled, a late joiner receives the start
    # banner (already delivered to everyone else) on arrival
    initial = io.StringIO()
    log = testing_log(initial,
        name='Recap',
        formats={
            'start': {'template': '{prefix}//start {name}//'},
            'end':   {'template': '{prefix}//end {name}//'},
            },
        )
    log("first")

    secondary = io.StringIO()
    log.destinations = log.destinations + [secondary]
    log("second")
    log.close()

    assert initial.getvalue() == "//start Recap//\nfirst\nsecond\n//end Recap//\n"
    assert secondary.getvalue() == "//start Recap//\nsecond\n//end Recap//\n"

def test_add_destination_inside_buffered_block():
    # a buffered enter() block delivers its whole contents at
    # flush time--to everyone routed at that moment, including
    # a destination added mid-block
    initial = io.StringIO()
    log = testing_log(initial,
        formats={
            'enter': {'template': '{prefix}//enter {message}//'},
            'exit':  {'template': '{prefix}//exit {message}//'},
            },
        )
    log("first")
    secondary = io.StringIO()
    with log.enter("block"):
        log("second")
        log.destinations = log.destinations + [secondary]
        log("third")
    log("fourth")
    log.close()

    assert initial.getvalue() == """
first
//enter block//
    second
    third
//exit block//
fourth
""".lstrip()
    # secondary joined mid-block: the block's contents hadn't
    # been delivered to ANYONE yet, so it receives all of them
    assert secondary.getvalue() == """
//enter block//
    second
    third
//exit block//
fourth
""".lstrip()

def test_removed_buffer_is_flushed_not_dropped():
    a = io.StringIO()
    b = io.StringIO()
    buffer = big.log.Log.Buffer(big.log.FileHandle(b))

    log = testing_log(a, buffer)
    assert buffer.owner is log

    log("delivered before removal")
    log.destinations = [log.destinations[0]]     # remove the buffer
    assert buffer.owner is None

    log("after removal")
    log.close()

    assert "delivered before removal" in b.getvalue()   # flushed!
    assert "after removal" not in b.getvalue()
    assert "after removal" in a.getvalue()

def test_owner_property():
    a = []
    log = testing_log(a)
    d = log.destinations[0]
    assert d.owner is log
    log.destinations = [print]
    assert d.owner is None
    log.close()

class Shout(log_module.Filter):
    "A filter that uppercases its parent's renderings."
    def render(self, value):
        return value.upper()


def hush(value):
    "Drops any rendering containing 'secret'."
    if 'secret' in value:
        return None
    return value


class Grumpy(log_module.Filter):
    "A filter that throws a tantrum when it sees 'tantrum'."
    def render(self, value):
        if 'tantrum' in value:
            raise ValueError('tantrum!')
        return value


def test_formatter_under_formatter():
    # F feeds A and C; C is a second formatter feeding J.
    # C sees F's formatted output--that's the key to the design.
    a = []
    j = []
    log = big.Log(a, threaded=False)
    shout = Shout()
    log.route(log.formatter, shout)
    log.route(shout, j)
    log('hello there')
    log.close()
    assert any('hello there' in s for s in a)
    assert len(a) == len(j)
    for rendered, shouted in zip(a, j):
        assert shouted == rendered.upper()

def test_formatter_child_in_constructor():
    # the constructor spelling works too: Log(a, shout)
    # attaches shout under the default formatter.
    a = []
    j = []
    shout = Shout()
    log = big.Log(a, shout, threaded=False)
    log.route(shout, j)
    log('constructed')
    log.close()
    assert any('constructed' in s for s in a)
    assert any('CONSTRUCTED' in s for s in j)

def test_filter_drops_subtree():
    # a filter returning None silences its subtree for that
    # message; siblings are unaffected.
    a = []
    j = []
    log = big.Log(a, threaded=False)
    quiet = log_module.Filter(hush)
    log.route(log.formatter, quiet)
    log.route(quiet, j)
    log('public knowledge')
    log('this is secret business')
    log('more public knowledge')
    log.close()
    assert any('secret' in s for s in a)
    assert not (any('secret' in s for s in j))
    assert any('public knowledge' in s for s in j)

def test_a_node_can_only_have_one_parent():
    a = []
    b = []
    log = big.Log(a, threaded=False)
    shout = Shout()
    shout2 = Shout()
    log.route(log.formatter, shout)
    log.route(shout, shout2)
    # a node already in the tree can't be attached again...
    with raises(ValueError):
        log.route(log.formatter, shout2)
    # ...and a top-level formatter can't become a child:
    # refused by type first (a TextFormatter consumes
    # Messages, not str), by the one-parent rule otherwise.
    other = log_module.TextFormatter()
    log.route(other, b)
    with raises((TypeError, ValueError)):
        log.route(log.formatter, other)
    log.close()

def test_filters_cannot_sit_at_the_top_level():
    # a str-accepting filter is fed renderings, not Messages;
    # the type system refuses it at the root.
    a = []
    log = big.Log(a, threaded=False)
    with raises(TypeError):
        log.route(log_module.Filter(hush), a)
    log.close()

def test_child_type_mismatch():
    # a child that can't accept what its parent emits is
    # refused at route time.
    a = []
    log = big.Log(a, threaded=False)
    shout = Shout()
    log.route(log.formatter, shout)
    bytes_only = log_module.LogDestination(types={bytes})
    with raises(TypeError):
        log.route(shout, bytes_only)
    log.close()

def test_filter_under_filter():
    # filters consume and produce str, so they chain.
    a = []
    j = []
    log = big.Log(a, threaded=False)
    quiet = log_module.Filter(hush)
    shout = Shout()
    log.route(log.formatter, quiet)
    log.route(quiet, shout)
    log.route(shout, j)
    log('hello')
    log('a secret hello')
    log.close()
    assert any('HELLO' in s for s in j)
    assert not (any('SECRET' in s for s in j))

def test_accepts_defaults():
    # by default a formatter accepts log Messages: welcome at
    # the top level, refused downstream of a text formatter.
    a = []
    log = big.Log(a, threaded=False)
    plain = log_module.LogFormatter({}, {str}, name='plain')
    with raises(TypeError):
        log.route(log.formatter, plain)
    # accepting anything must be said out loud...
    anything = log_module.LogFormatter({}, {str}, accepts=True, name='anything')
    log.route(log.formatter, anything)
    # ...and a bare Filter without a callable is a mistake
    # you hear about when it renders.
    log.close()

def test_faulty_filter_drops_its_subtree():
    # a misbehaving interior node is surgically dropped--
    # subtree and all--and the rest of the tree soldiers on.
    a = []
    j = []
    log = big.Log(a, threaded=False, retries=1)
    grumpy = Grumpy()
    log.route(log.formatter, grumpy)
    log.route(grumpy, j)
    log('before the storm')
    log('tantrum time')
    log('after the storm')
    log.close()
    # the root destination saw everything...
    assert any('before the storm' in s for s in a)
    assert any('tantrum time' in s for s in a)
    assert any('after the storm' in s for s in a)
    # ...the filtered destination saw only what came before
    # the tantrum.
    assert any('before the storm' in s for s in j)
    assert not (any('tantrum' in s for s in j))
    assert not (any('after the storm' in s for s in j))


##
## coverage grind: the corners the behavioral tests don't reach--
## constructor validation, the poisoned-log guard on every public
## method, reprs, and the internal machinery paths.
##

def test_constructor_validation():
    L = log_module

    # TextFormatter
    with raises(TypeError):
        L.TextFormatter(width='wide')
    with raises(ValueError):
        L.TextFormatter(width=0)
    with raises(TypeError):
        L.TextFormatter(indent=8)
    with raises(TypeError):
        L.TextFormatter(format_dict=['not', 'a', 'dict'])
    with raises(TypeError):
        L.TextFormatter(prefix=object())
    with raises(TypeError):
        L.TextFormatter(formats=['not', 'a', 'dict'])

    # LogFormatter
    with raises(TypeError):
        L.LogFormatter({}, {str}, name=123)
    with raises(TypeError):
        L.LogFormatter({}, {str}, accepts='everything')

    # Filter
    with raises(TypeError):
        L.Filter('not callable')
    # a Filter with no filter and no override raises when rendered
    with raises(NotImplementedError):
        L.Filter().render('x')

    # Log
    with raises(TypeError):
        L.Log(name=123)
    with raises(ValueError):
        L.Log(name='')
    with raises(ValueError):
        L.Log(retries=0)
    with raises(TypeError):
        L.Log(fix='not callable')
    with raises(TypeError):
        L.Log(formatter='not a formatter')
    with raises(TypeError):
        L.Log(clock='not callable')

    # Job
    with raises(TypeError):
        L.Job('not callable', ())

    # the abstract bases raise NotImplementedError
    with raises(NotImplementedError):
        L.LogFormatter({}, {str}).render(None)
    with raises(NotImplementedError):
        L.LogDestination().__eq__(object())
    with raises(NotImplementedError):
        L.LogDestination().__hash__()

    # DefaultChildFormat is a singleton
    with raises(ValueError):
        type(log_module._DEFAULT_CHILD_FORMAT)()

def test_map_destination_validation():
    log = testing_log()
    # a mapper that returns a non-LogDestination is an error
    log_module.LogDestination.mappers.insert(0, lambda o: 'not a destination' if o == 'trigger' else None)
    try:
        with raises(TypeError):
            log.map_destination('trigger')
    finally:
        log_module.LogDestination.mappers.pop(0)

def test_route_validation():
    log = testing_log()
    with raises(TypeError):
        log.route('not a formatter', log_module.Print())
    with raises(ValueError):
        log.route(log_module.TextFormatter())    # no destinations

def test_unregister_when_not_registered():
    d = log_module.Print()
    with raises(RuntimeError):
        d.unregister()

def test_poisoned_log_raises_everywhere():
    # once a log is poisoned (an unfixable internal fault), every
    # public method re-raises the poison.  we set the poison
    # directly--the fault machinery that produces it is exercised
    # separately--and check every guarded entry point.
    def fresh_poisoned():
        log = testing_log()
        log._core.poisoned = RuntimeError("the log is poisoned")
        return log

    for action in (
        lambda l: l('x'),
        lambda l: l.write('x'),
        lambda l: l.print('x'),
        lambda l: l.flush(),
        lambda l: l.reset(),
        lambda l: bool(l.paused),
        lambda l: l.pause(),
        lambda l: l.resume(),
        lambda l: l.route(log_module.TextFormatter(), log_module.Print()),
        ):
        with raises(RuntimeError):
            action(fresh_poisoned())

def test_destinations_setter_poisoned():
    log = testing_log()
    log._core.poisoned = RuntimeError("poisoned")
    with raises(RuntimeError):
        log.destinations = [log_module.Print()]

def test_reprs():
    # the debug reprs just have to run without raising.
    # (testing_log() with no destinations defaults to Print--give
    # it a list so the message stays off the test run's stdout.)
    log = testing_log([])
    log('a message')
    log.close()

    assert repr(log_module._DEFAULT_CHILD_FORMAT) == "<DefaultChildFormat>"
    assert "NotCalledYet" in repr(log_module._NOT_CALLED_YET)
    job = log_module.Job(None, ())
    assert repr(job).startswith("<Job")

def test_log_getattr_unknown():
    log = testing_log()
    with raises(AttributeError):
        log.no_such_helper_method_exists

def test_log_property_getters():
    # File property getters
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "log.txt")
        f = log_module.File(path)
        assert f.binary is False
        assert f.buffering is True
        assert f.encoding is None
        assert f.mode == "at"

    # Callable.callable
    fn = lambda s: None
    assert log_module.Callable(fn).callable is fn

    # NoneType destination
    none_dest = log_module.NoneType()
    assert none_dest == log_module.NoneType()
    assert not none_dest
    assert none_dest.write("ignored") is None

def test_destination_subclass_dunders():
    L = log_module

    # Buffer (distinct original destinations compare unequal)
    b1 = L.Buffer([])
    b2 = L.Buffer([])
    assert b1 == b1
    assert not (b1 == b2)          # different original_destination
    assert not (b1 == object())
    assert hash(b1) == hash(b1)
    assert b1.buffer == []
    assert b1.destination == []

    # a Buffer wrapping an explicit destination reports it
    p = L.Print()
    b3 = L.Buffer(p)
    assert b3.destination is p

    # Sink
    s1 = L.Sink()
    s2 = L.Sink()
    assert s1 == s1
    assert not (s1 == s2)
    assert hash(s1) == hash(s1)
    assert bool(s1) is True

    # OldDestination
    o1 = L.OldDestination()
    o2 = L.OldDestination()
    assert o1 == o1
    assert not (o1 == o2)
    assert hash(o1) == hash(o1)
    assert bool(o1) is True

    # TmpFile properties and dunders
    t1 = L.TmpFile(prefix='alpha')
    t2 = L.TmpFile(prefix='beta')
    assert t1.prefix == 'alpha'
    assert isinstance(t1.path, pathlib.Path)
    assert t1 == L.TmpFile(prefix='alpha')
    assert not (t1 == t2)
    assert hash(t1) == hash(L.TmpFile(prefix='alpha'))
    with raises(TypeError):
        L.TmpFile(prefix='')       # empty prefix

def test_buffer_flush_str_bytes_mixed():
    L = log_module

    # str buffer: joined and written as one string
    got = []
    class Collector(L.LogDestination):
        def __init__(self, types):
            super().__init__(types=types)
        def __eq__(self, other): return other is self
        def __hash__(self): return id(self)
        def write(self, message): got.append(message)

    str_buf = L.Buffer(Collector({str}))
    str_buf.write("a")
    str_buf.write("b")
    str_buf.flush()
    assert got == ["ab"]

    # bytes buffer: joined as bytes
    got.clear()
    bytes_buf = L.Buffer(Collector({bytes}))
    bytes_buf.write(b"a")
    bytes_buf.write(b"b")
    bytes_buf.flush()
    assert got == [b"ab"]

    # mixed types: written one at a time
    got.clear()
    mixed_buf = L.Buffer(Collector({str, bytes}))
    mixed_buf.write("a")
    mixed_buf.write(b"b")
    mixed_buf.flush()
    assert got == ["a", b"b"]

def test_tmpfile_end_to_end():
    # a TmpFile computes its name from the "start" event and writes
    # there; this exercises register/start and the timestamp path
    log = testing_log(log_module.TMPFILE)
    log("into the temp file")
    log.close()
    # the path was recomputed away from the Log-init placeholder
    for d in log.destinations:
        if isinstance(d, log_module.TmpFile):
            assert "Log-init" not in str(d.path)
            if d.path.exists():
                os.unlink(d.path)

def test_recap_replays_to_late_destination():
    # adding a destination after logging has started "recaps" the
    # banners to it, so a late joiner's output is coherent.  needs
    # a formatter that actually emits a start banner (testing_log
    # turns them off), so build one explicitly.
    early = []
    late = []
    log = big.Log(early, threaded=False,
        formatter=log_module.TextFormatter(log_module.ascii_format_dict()))
    log("first message")
    with log.enter("a block"):        # enter banner, recap-able
        log.destinations = [early, late]   # late joins mid-block
        log("second message")
    log.close()
    # late saw its live message...
    assert any("second message" in s for s in late)
    # ...and a recap of the enter banner it didn't witness live
    assert any("a block" in s for s in late)

def test_write_and_log_paths():
    a = []
    log = testing_log(a)

    # write() with flush=True
    log.write("verbatim\n", flush=True)
    assert any("verbatim" in s for s in a)

    # write() delegates into an enter() block (nesting)
    a.clear()
    with log.enter("block"):
        log.write("inside\n")
    log.close()
    assert any("inside" in s for s in a)

def test_log_delegates_and_flushes_in_block():
    a = []
    log = testing_log(a)
    with log.enter("outer"):
        log("delegated message", flush=True)
    log.close()
    assert any("delegated message" in s for s in a)

def test_write_when_paused_is_dropped():
    a = []
    log = testing_log(a)
    log.pause()
    log.write("should be dropped\n")
    log("also dropped")
    log.resume()
    log.close()
    assert not any("dropped" in s for s in a)

def test_child_format_validation():
    log = testing_log()
    # a child with an Optional format
    with raises(ValueError):
        log.child("kid", format=big.Optional('nope'))
    # a child with a non-str format
    with raises(TypeError):
        log.child("kid", format=123)
    # a child with a format no formatter defines
    with raises(ValueError):
        log.child("kid", format="undefined_format_xyz")
    # a child with a non-str name
    with raises(TypeError):
        log.child(name=123)

def test_map_destination_special_values():
    log = testing_log()
    # None maps to the null destination, TMPFILE to a TmpFile
    assert isinstance(log.map_destination(None), log_module.NoneType)
    assert isinstance(log.map_destination(log_module.TMPFILE), log_module.TmpFile)

def test_sinkevent_dunders():
    L = log_module
    a = L.SinkEvent(session=1, ns=100, epoch=200)
    b = L.SinkEvent(session=1, ns=100, epoch=200)
    c = L.SinkEvent(session=2, ns=100, epoch=200)
    assert a == b
    assert a != c
    assert not (a == c)
    # foreign types: NotImplemented, so == is False and != is True
    assert a.__eq__("foreign") is NotImplemented
    assert a.__ne__("foreign") is NotImplemented
    assert not (a == "foreign")
    assert a != "foreign"
    # different SinkEvent subtypes are unequal even with same key
    start = L.SinkStartEvent(session=1, ns=100, epoch=200, configuration=None)
    assert not (a == start)

def test_logbase_and_emptyvalue_bool():
    # a Log with destinations is truthy; the _EmptyValue is falsey
    log = testing_log([])
    assert bool(log) is True
    assert bool(log_module._EMPTY_VALUE) is False
    assert str(log_module._EMPTY_VALUE) == ''
    assert repr(log_module._EMPTY_VALUE) == ''

def test_filter_types_come_from_annotations():
    # a Filter reads its callable's annotations: the first
    # positional parameter's annotation is what it accepts, the
    # return annotation is what it produces.  either defaults
    # to str when unannotated.
    L = log_module

    # unannotated: str both ways (the historical behavior)
    f = L.Filter(lambda s: s)
    assert f.accepts == {str}
    assert f.types == {str}

    # fully annotated
    def unbyte(b: bytes) -> str:
        return b.decode('ascii')
    f = L.Filter(unbyte)
    assert f.accepts == {bytes}
    assert f.types == {str}
    assert f.render(b'x') == 'x'

    # each side independently defaulted
    def eats_bytes(b: bytes):
        return b
    f = L.Filter(eats_bytes)
    assert f.accepts == {bytes}
    assert f.types == {str}
    assert f.render(b'x') == b'x'

    def makes_bytes(s) -> bytes:
        return s.encode('ascii')
    f = L.Filter(makes_bytes)
    assert f.accepts == {str}
    assert f.types == {bytes}
    assert f.render('x') == b'x'

    # a first parameter that isn't positional (*args) gets the
    # default accepts
    f = L.Filter(lambda *args: args[0])
    assert f.accepts == {str}
    assert f.types == {str}
    assert f.render('x') == 'x'

    # a callable inspect can't get a signature from gets the
    # defaults
    def weird(b: bytes) -> bytes:
        return b
    weird.__signature__ = 'not a signature'
    f = L.Filter(weird)
    assert f.accepts == {str}
    assert f.types == {str}
    assert f.render(b'x') == b'x'


def test_filter_explicit_accepts_and_types():
    # explicit accepts= and types= win over annotations; each may
    # be a single type, a set of types, or True (anything).
    L = log_module

    # single types, no annotations to consult
    f = L.Filter(lambda b: b, accepts=bytes, types=bytes)
    assert f.accepts == {bytes}
    assert f.types == {bytes}

    # sets pass through as-is
    f = L.Filter(lambda o: o, accepts={str, bytes}, types=frozenset((str,)))
    assert f.accepts == {str, bytes}
    assert f.types == frozenset((str,))

    # True means anything
    f = L.Filter(lambda o: o, accepts=True, types=True)
    assert f.accepts is True
    assert f.types is True

    # explicit beats annotation...
    def unbyte(b: bytes) -> str:
        return b.decode('ascii')
    f = L.Filter(unbyte, accepts=str, types=bytes)
    assert f.accepts == {str}
    assert f.types == {bytes}
    assert f.render(b'x') == 'x'

    # ...and each side falls back to the annotation independently
    f = L.Filter(unbyte, accepts=str)
    assert f.accepts == {str}
    assert f.types == {str}          # from the return annotation
    f = L.Filter(unbyte, types=bytes)
    assert f.accepts == {bytes}      # from the parameter annotation
    assert f.types == {bytes}


def test_annotated_filter_under_ascii_formatter():
    # the point of the feature: an annotated filter can sit where
    # a str filter can't.  ASCIIFormatter produces bytes; this
    # filter consumes them and produces str for a str destination.
    def unbyte(b: bytes) -> str:
        return b.decode('ascii')

    collected = []
    log = big.Log(None, threaded=False,
                  formatter=log_module.ASCIIFormatter(prefix=''))
    filt = log_module.Filter(unbyte)
    log.route(log.formatter, filt)
    log.route(filt, collected)
    log("through the bytes filter")
    log.close()
    assert any("through the bytes filter" in s for s in collected)
    assert all(isinstance(s, str) for s in collected)


def test_time_is_noted_at_the_top_and_survives_delegation():
    # the clock is read FIRST in every entry point--the message is
    # stamped with the moment the user called, before anything else
    # runs--and a nesting-delegated call keeps that original
    # reading instead of restamping later.  a counting clock makes
    # the stamp reveal exactly which read produced it.
    class CountingClock:
        def __init__(self):
            self.count = 0
        def __call__(self):
            self.count += 1
            return self.count

    clock = CountingClock()
    sink = big.Log.Sink()
    log = big.Log(sink, threaded=False, clock=clock)
    log.enter('block')

    # a delegated log() reads the clock exactly once, at the top,
    # and the message carries that reading
    before = clock.count
    log("delegated")
    assert clock.count == before + 1
    log.exit()
    events = list(sink)
    message_ns = [e.ns for e in events
                  if isinstance(e, big.SinkLogEvent) and e.message == 'delegated']
    assert message_ns == [before + 1]

    # exit() also reads the clock exactly once, at the top, and
    # the exit banner is stamped with that reading (threaded all
    # the way down through close -> unregister -> _close ->
    # ensure_state)
    log.enter('block2')
    before = clock.count
    log.exit()
    assert clock.count == before + 1
    events = list(sink)
    exit_ns = [e.ns for e in events if e.type == 'exit']
    assert exit_ns[-1] == before + 1

    log.close()


def test_log_truthiness_tracks_pause_and_close():
    # a handle is true iff logging to it right now would deliver:
    # destinations exist, the handle is open, and neither it nor
    # any ancestor is paused.  (the pause half is epoch-cached on
    # the session; pause/resume bump the core's pause_epoch.)
    log = testing_log([])
    assert log

    log.pause()
    assert not log                  # paused -> dark
    assert not log                  # (and again, via the cache)
    log.pause()
    log.resume()
    assert not log                  # still paused (nested)
    log.resume()
    assert log                      # resumed -> live

    child = log.enter('block')
    assert child
    log.pause()
    assert not child                # ancestor pause silences the child
    assert log._core.truthy         # ...but destinations are still there
    log.resume()
    assert child
    child.pause()
    assert not child                # own pause
    assert log                      # ...which doesn't silence the root
    child.resume()
    log.exit()

    log.close()
    assert not log                  # closed -> dark


def test_bool_false_when_session_closed_under_live_handle():
    # white box: a handle can briefly hold a session that's already
    # CLOSED (another thread reset the log, or atexit is running).
    # _live reports it dead before consulting the pause cache.
    log = testing_log([])
    assert log
    session = log._session
    session.state = log_module.STATE_CLOSED
    assert not log
    session.state = log_module.STATE_INITIAL
    log.close()


def test_log_truthiness_tracks_destinations():
    # a Log is true while it has destinations, and false again
    # when the last one is removed--truthiness is not a latch.
    log = testing_log([])
    assert log

    # emptying the destinations makes it false...
    log.destinations = []
    assert not log

    # ...and giving it a destination makes it true again
    log.destinations = [[]]
    assert log
    log.close()

def test_log_truthiness_after_fault_removes_last_destination():
    # the fault ladder surgically removes a hopeless destination;
    # if it was the last one, the log honestly goes false.
    class Doomed(log_module.LogDestination):
        def __init__(self):
            super().__init__(types=True)
        def __eq__(self, other): # pragma: no cover
            # identity armor, same as EventSink: the routing
            # machinery may compare destinations, but nothing in
            # this test's path actually does
            return other is self
        def __hash__(self):
            return id(self)
        def write(self, o):
            raise RuntimeError("doomed")

    log = testing_log(Doomed(), fix=lambda involved, fault: False)
    assert log
    log("this message kills the only destination")
    log.flush()
    assert not log
    log.close()

def test_sink_and_olddestination_write_none():
    # writing None to a Sink or OldDestination is a no-op
    s = log_module.Sink()
    s.write(None)
    assert len(s) == 0
    o = log_module.OldDestination()
    o.write(None)

def test_session_and_message_reprs():
    # drive a real log so Session/Message objects exist, then repr
    # them through the debug path
    a = []
    log = testing_log(a)
    log("a message")
    # the root session's repr
    session = log._session
    assert "Session" in repr(session)
    log.close()

def test_route_after_logging_started():
    # routing a formatter+destination after the log has started
    # immediately registers and STARTS them (the started-add and
    # start-callback paths in route())
    early = []
    late_dest = []
    log = big.Log(early, threaded=False,
        formatter=log_module.TextFormatter(log_module.ascii_format_dict()))
    log("first")                      # log starts here
    # a brand-new top-level formatter feeding a new destination
    late_fmt = log_module.TextFormatter(log_module.ascii_format_dict())
    log.route(late_fmt, late_dest)    # started immediately
    # a child formatter under it, also after start
    child_fmt = log_module.Filter(lambda s: s, name='passthrough')
    child_dest = []
    log.route(late_fmt, child_fmt)
    log.route(child_fmt, child_dest)
    log("second")
    log.close()
    assert any("second" in s for s in late_dest)
    assert any("second" in s for s in child_dest)

def test_route_errors():
    log = testing_log([])
    # a Filter (child formatter) under the root, feeding a
    # destination; that destination can't then get a second parent
    d = []
    f1 = log_module.Filter(lambda s: s, name='f1')
    f2 = log_module.Filter(lambda s: s, name='f2')
    log.route(log.formatter, f1)
    log.route(f1, d)
    log.route(log.formatter, f2)
    with raises(ValueError):
        log.route(f2, d)              # d already has a parent (f1)

def test_fix_that_raises_poisons_the_log():
    # if fix() itself raises, there's no recovering: the log is
    # poisoned with fix's exception
    def bad(msg):
        raise OSError("destination broke")
    def fix(involved, exception):
        raise RuntimeError("fix itself is broken")
    log = big.Log(bad, fix=fix, threaded=False)
    log("boom")
    log.close()
    assert isinstance(log._core.poisoned, RuntimeError)
    assert "fix itself is broken" in str(log._core.poisoned)

def test_childless_ancestor_formatter_retires():
    # a pure formatter chain with no siblings: when the leaf faults
    # and is removed, its now-childless parent formatter retires
    # too, climbing up
    dest = []
    def explode(s):
        raise RuntimeError("leaf explodes")
    leaf = log_module.Filter(explode, name='leaf')
    middle = log_module.Filter(lambda s: s, name='middle')

    log = big.Log([], threaded=False,
        formatter=log_module.TextFormatter(log_module.ascii_format_dict()))
    log.route(log.formatter, middle)
    log.route(middle, leaf)           # middle's only child is leaf
    log("x")                          # leaf faults, removed; middle childless -> retires
    log("y")
    log.close()
    # the whole chain is gone; the run didn't crash
    assert log._core.poisoned is None

def test_threaded_fault_and_removal():
    # a threaded log whose destination faults exercises the queue's
    # job-removal and deletion-swallowing paths
    good = []
    def bad(msg):
        raise OSError("threaded fault")
    log = big.Log(bad, good, threaded=True)
    for i in range(5):
        log(f"message {i}")
    log.close()
    # the surviving destination still got everything
    text = ''.join(good)
    for i in range(5):
        assert f"message {i}" in text

def test_threaded_many_jobs_and_reset():
    # exercises append/extend/prepend/drain across a threaded log
    # with nesting (enter creates child jobs) and a reset
    array = []
    log = testing_log(array, threaded=True)
    with log.enter("outer"):
        for i in range(3):
            log(f"nested {i}")
    log.reset()
    log("after reset")
    log.close()
    output = ''.join(array)
    assert "after reset" in output

def test_prefix_format_ascii():
    # ascii=True translates the box-drawing prefix chars to ASCII
    unicode_prefix = log_module.prefix_format(8, 3)
    ascii_prefix = log_module.prefix_format(8, 3, ascii=True)
    assert '|' in ascii_prefix          # the box char became ASCII
    assert unicode_prefix != ascii_prefix

def test_nonetype_hash():
    a = log_module.NoneType()
    b = log_module.NoneType()
    # all NoneType destinations are equal, so they hash equal
    assert hash(a) == hash(b)

def test_job_args_normalized_to_tuple():
    # Job accepts any iterable for args and stores a tuple
    job = log_module.Job(lambda: None, [1, 2, 3])
    assert job.args == (1, 2, 3)
    assert isinstance(job.args, tuple)

def test_log_threading_deprecated_alias():
    # 'threading=' is the deprecated alias for 'threaded='
    a = []
    log = big.Log(a, threading=False,
        formatter=log_module.TextFormatter(log_module.ascii_format_dict()))
    log("via the old alias")
    log.close()
    assert any("via the old alias" in s for s in a)

def test_paused_counter_no_session():
    # a fresh log with no active session reports paused-depth 0
    log = testing_log()
    assert log.paused == 0

def test_child_default_time_from_clock():
    # a child with no explicit time takes it from the parent
    # session's clock
    a = []
    log = testing_log(a)
    with log.child("kid") as kid:
        kid("child message")
    log.close()
    assert any("child message" in s for s in a)

def test_filehandle_autoflush():
    # a FileHandle with autoflush flushes after every write
    handle = io.StringIO()
    flushes = []
    original_flush = handle.flush
    handle.flush = lambda: (flushes.append(1), original_flush())[1]
    fh = log_module.FileHandle(handle, autoflush=True)
    fh.write("x")
    assert flushes == [1]

def test_sink_receives_kwargs():
    # logging with kwargs (via the .log() method, which takes them;
    # the plain call maps to .print()) exercises SinkLogEvent.render's
    # kwargs branch
    sink = big.Sink()
    log = big.Log(sink, threaded=False, formatter=log_module.SinkFormatter())
    log.log("a message", detail="extra", count=3)
    log.close()
    assert list(sink)

def test_object_reprs_run():
    # the debug reprs for Session/Message-ish internal objects run
    # without raising, during a real log
    a = []
    log = testing_log(a)
    log("drive the machinery")
    # Session repr (with an active buffer path is hard to force,
    # but the no-buffer path runs)
    assert "Session" in repr(log._session)
    log.close()

def test_core_register_rejects_foreign():
    log = testing_log()
    with raises(TypeError):
        log._core.register("not a Log/Child/Session")

def test_logformatter_state_prepare_is_abstract():
    # LogFormatter's base State.prepare raises NotImplementedError
    fmt = log_module.TextFormatter(log_module.ascii_format_dict())
    # the *base* LogFormatter.State (not TextFormatter's override)
    base_state = log_module.LogFormatter.State(fmt, '')
    with raises(NotImplementedError):
        base_state.prepare("message")

def test_empty_value_format_spec_stripping():
    # _EmptyValue formats against a type-spec by stripping it to the
    # fill/align/width bones (so a '{x:+09.2f}' on an empty value
    # doesn't blow up)
    ev = log_module._EMPTY_VALUE
    # a spec with a type code that '' can't satisfy directly forces
    # the strip path
    assert format(ev, '+09.2f') == format('', _stripped('+09.2f'))
    assert format(ev, '>12,') == format('', '>12')

def _stripped(spec):
    return log_module._strip_type_spec(spec)

def test_strip_type_spec_directly():
    # sign/space/grouping chars dropped, leading zero dropped,
    # everything from '.' or a type code onward dropped
    assert log_module._strip_type_spec('09d') == '9'
    assert log_module._strip_type_spec('>12,') == '>12'
    assert log_module._strip_type_spec('+.2f') == ''
    assert log_module._strip_type_spec('>10.4s') == '>10'

def test_child_poisoned_at_construction():
    # constructing a Child on a poisoned core re-raises the poison
    log = testing_log()
    log._core.poisoned = RuntimeError("already poisoned")
    with raises(RuntimeError):
        log.child("kid")

def test_log_flush_argument():
    a = []
    log = testing_log(a)
    # log() with flush=True (via the .log method)
    log.log("flushed message", flush=True)
    assert any("flushed message" in s for s in a)
    log.close()

def test_session_repr_buffered_and_unbuffered():
    a = []
    log = testing_log(a)
    log("root message")
    # the root session has no buffer
    assert "buffer=None" in repr(log._session)
    # inside an enter() block, the active session is a buffered child
    with log.enter("subsystem"):
        inner = repr(log._session)
        assert "waiting" in inner or "buffer=" in inner
    log.close()

def test_recap_enter_banner_to_late_destination():
    # a destination that joins mid-block gets the enter banner
    # recapped (the 'enter' branch of _recap)
    early, late = [], []
    log = big.Log(early, threaded=False,
        formatter=log_module.TextFormatter(log_module.ascii_format_dict()))
    log("before")
    with log.enter("the subsystem"):
        log.destinations = [early, late]     # joins inside the block
        log("during")
    log.close()
    text = ''.join(late)
    assert "during" in text
    assert "the subsystem" in text            # the recapped enter banner

def test_session_register_rejects_foreign():
    log = testing_log([])
    log("warm")
    session = log._session
    with raises(TypeError):
        session.register("not a Log/Child/Session")
    log.close()

def test_message_format_none_inherits_session_format():
    a = []
    log = testing_log(a)
    # format=None means "use the session's default format"
    log.log("inheriting format", format=None)
    log.close()
    assert any("inheriting format" in s for s in a)

def test_ensure_state_from_wrong_thread_raises():
    # in threaded mode, changing session state from any thread but
    # the worker is a RuntimeError
    log = testing_log([], threaded=True)
    log("warm")
    session = log._session
    with raises(RuntimeError):
        session.ensure_state(log_module.STATE_ACTIVE)
    log.close()

def test_file_write_empty_is_noop():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "f.txt")
        f = log_module.File(path)
        f.write("")               # empty write returns early, opens nothing
        assert not os.path.exists(path)

def test_threaded_log_closed_without_logging():
    # a threaded log that never logged has no worker thread; closing
    # it hits the early-return in _stop_thread
    log = big.Log([], threaded=True,
        formatter=log_module.TextFormatter(log_module.ascii_format_dict()))
    log.close()               # never started a thread
    assert True

def test_child_takes_time_from_parent_clock():
    # constructing a child with no explicit time takes it from the
    # parent session's clock (the time-is-None branch)
    a = []
    log = testing_log(a)
    log("warm")               # ensure a parent session exists
    kid = log.child("standalone")   # no time= -> parent_session.clock()
    assert kid is not None
    log.close()

def test_recap_failure_is_not_fatal():
    # if a late-joining destination faults during the banner recap,
    # the recap swallows it (a broken destination will fault on its
    # first real write and get handled the normal way)
    early = []
    class RecapExploder(log_module.LogDestination):
        def __init__(self):
            super().__init__(types=True)
            self.live = False
        def __eq__(self, other): return other is self
        def __hash__(self): return id(self)
        def write(self, s):
            if not self.live:     # explode during recap, not after
                raise RuntimeError("recap boom")
    exploder = RecapExploder()
    log = big.Log(early, threaded=False,
        formatter=log_module.TextFormatter(log_module.ascii_format_dict()))
    log("before")
    with log.enter("block"):
        log.destinations = [early, exploder]   # exploder faults on recap
        exploder.live = True
        log("after")
    log.close()
    # the run survived the recap failure
    assert any("after" in s for s in early)

def test_oldlog_and_olddestination():
    # the deprecated OldLog shim is callable and prints its event log
    old = big.OldLog()
    old("event one")
    old("event two")
    output = []
    old.print(print=output.append)
    text = '\n'.join(output)
    assert "event one" in text

##
## white-box coverage: internal debug reprs and the job queue,
## constructed directly.  (Larry's call: 100% coverage is worth
## reaching into the machinery.)
##

def test_internal_reprs_white_box():
    log = testing_log([])
    log("warm")
    root = log._session
    core = log._core

    # a buffered Session's repr (the "N waiting" branch)
    child = log_module.Session(core, "child", root, buffered=True,
        clock=root.clock, format=root.format, kwargs={}, paused=False)
    assert "waiting" in repr(child)

    # a Message's repr
    message = root.Message(root.clock(), '', ('hi',), {})
    assert "Message" in repr(message)

    log.close()

    # a LogFormatter.State repr and a TextFormatter.Prepared repr
    fmt = log_module.TextFormatter(log_module.ascii_format_dict())
    state = log_module.LogFormatter.State(fmt, '')
    assert "State" in repr(state)
    prepared = fmt.Prepared(('a',), {}, None)
    assert "Prepared" in repr(prepared)

    # a SinkFormatter.Prepared repr
    sink_prepared = log_module.SinkFormatter.Prepared(('a',), {})
    assert "Prepared" in repr(sink_prepared)

    # a tree-less formatter's format() returns None for any named
    # format: the base LogFormatter contract when format_dict is None
    treeless = log_module.LogFormatter(None, {str})
    assert treeless.format('nonesuch') is None

    # a SinkFormatter overrides format(): a marker dict for names it
    # knows, None for names it doesn't.
    sink_fmt = log_module.SinkFormatter(formats={'', 'enter'})
    assert sink_fmt.format('enter') == {}
    assert sink_fmt.format('nonesuch') is None

def test_faulting_prepare_on_user_thread_does_not_deadlock():
    # regression: the worker thread used to park in
    # notify_queue.get() while *holding* queue.lock.  a message
    # argument whose str() raises faults its prepare job on the
    # *user's* thread (prepare runs inline in Message.__init__);
    # the fault ladder then called queue.remove(), which blocked
    # forever on the lock the sleeping worker held.
    class Evil:
        def __str__(self):
            raise ZeroDivisionError("evil str")

    collected = []
    log = big.Log(collected, threaded=True)
    log("warm up the worker")
    log.flush()
    time.sleep(0.1)                 # let the worker park in nq.get()

    returned = []
    def target():
        log.log(Evil())             # used to deadlock right here
        returned.append(True)
    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(10)
    assert returned, "log.log(Evil()) deadlocked against the idle worker"
    log.close()


def test_failed_route_is_atomic_before_start():
    # regression: route() used to mutate the routing tables child
    # by child *while* validating, so a ValueError on a later child
    # left earlier children routed but never register()ed.  the
    # first message then poisoned the whole log during lazy start
    # ("can't start ..., it's unregistered")--after route() had
    # already reported the error and the user had handled it.
    a, b = [], []
    log = big.Log(a, threaded=False)
    f2 = log_module.TextFormatter()
    log.route(f2, b)
    d1 = log._core.routes[f2.key][0]

    d_new = log_module.List([])
    with raises(ValueError):
        log.route(log.formatter, d_new, d1)     # d1 already has a parent

    # the failed route left no trace of d_new
    assert d_new not in log._core.routes[log.formatter.key]
    assert d_new not in log._destinations
    assert d_new._core is None                  # never registered

    # ...and the log still works, unpoisoned
    log("hello")
    log("again")
    log.close()
    assert log._core.poisoned is None
    assert any("hello" in s for s in a)
    assert any("again" in s for s in a)


def test_failed_route_is_atomic_after_start():
    # the started-log variant: the half-routed child used to be
    # marked "started" without ever being started, so _end() blew
    # up on it at close ("can't end ..., it wasn't started"),
    # poisoning the log during shutdown.
    a, b = [], []
    log = big.Log(a, threaded=False)
    log("started")                              # log is live
    f2 = log_module.TextFormatter()
    log.route(f2, b)
    d1 = log._core.routes[f2.key][0]

    d_new = log_module.List([])
    with raises(ValueError):
        log.route(log.formatter, d_new, d1)

    log("after failed route")
    log.close()
    assert log._core.poisoned is None
    assert any("after failed route" in s for s in a)


def test_route_same_destination_twice_no_duplicate():
    # re-routing the same destination is a silent no-op in the
    # routing tables; the public all_destinations property used to
    # grow a duplicate anyway.  a destination passed twice in one
    # call is deduplicated too.
    a = []
    log = big.Log(a, threaded=False)
    d = log_module.List([])
    log.route(log.formatter, d, d)              # twice in one call
    log.route(log.formatter, d)                 # and again later
    assert log._destinations.count(d) == 1
    log.close()


def test_destination_start_failure_is_unrouted_not_poison():
    # regression: _start called every node's start() in a plain
    # loop inside an unattributable job, so a destination whose
    # start() raised (File meeting a missing directory) poisoned
    # the whole log: healthy siblings got a mangled log, the next
    # log call raised at an innocent call site, and close()
    # re-poisoned ending never-started survivors.  start now runs
    # through the fault ladder, per node.
    lines = []
    log = big.Log(big.File('/nonexistent-dir/x.log', buffering=False), lines,
                  threaded=False)
    log("hello")
    log("again")
    log.close()
    assert log._core.poisoned is None
    joined = ''.join(lines)
    assert "hello" in joined
    assert "again" in joined
    assert "Log start" in joined        # the start banner arrived too

def test_destination_start_failure_fix_can_repair():
    # the ladder gives fix() a crack at a failing start; a fix that
    # repairs the destination gets it retried and kept.
    class Flaky(log_module.LogDestination):
        def __init__(self):
            super().__init__(types=True)
            self.broken = True
            self.lines = []
        def __eq__(self, other): # pragma: no cover
            # identity armor, same as EventSink
            return other is self
        def __hash__(self):
            return id(self)
        def start(self, session):
            if self.broken:
                raise RuntimeError("not ready")
            super().start(session)
        def write(self, o):
            self.lines.append(o)

    flaky = Flaky()
    def fix(involved, fault):
        involved.broken = False     # repair it
        return True                 # and ask for a retry
    log = big.Log(flaky, threaded=False, fix=fix)
    log("hello")
    log.close()
    assert log._core.poisoned is None
    assert any("hello" in s for s in flaky.lines)

def test_formatter_start_failure_is_unrouted_not_poison():
    # formatters get the same treatment as destinations: one
    # lifecycle, one fault policy.  a formatter whose start()
    # raises is unrouted (with its subtree); the log survives.
    class Unstartable(log_module.TextFormatter):
        def start(self, session):
            raise RuntimeError("can't start")

    a, b = [], []
    log = big.Log(a, threaded=False)
    log.route(Unstartable(), b)
    log("hello")
    log.close()
    assert log._core.poisoned is None
    assert any("hello" in s for s in a)     # healthy tree delivered
    assert not b                            # unrouted subtree got nothing

def test_all_destinations_failing_to_start_makes_log_false():
    # if every destination fails to start, the ladder unroutes them
    # all--and the log honestly goes false.
    log = big.Log(big.File('/nonexistent-dir/x.log', buffering=False),
                  threaded=False)
    assert log
    log("hello")
    assert not log
    log.close()
    assert log._core.poisoned is None


class _BadFlushDestination(log_module.LogDestination):
    # a destination whose flush() raises (until repaired)--used by
    # the reconfiguration fault tests
    def __init__(self):
        super().__init__(types=True)
        self.lines = []
        self.broken = True
        self.flushed = False
    def __eq__(self, other): return other is self
    def __hash__(self): return id(self)
    def write(self, o): self.lines.append(o)
    def flush(self):
        if self.broken:
            raise RuntimeError("flush failed")
        self.flushed = True


def test_file_start_repair_and_retry_delivers():
    # regression: File.start() called super().start() (committing
    # _session) BEFORE the fallible open(), so when open() failed
    # and fix() repaired the filesystem, the ladder's retry died on
    # "can't start, it was already started"--the repaired file was
    # never created, and the discarded destination was left
    # half-started (_core None, _session set).  fallible work now
    # comes first, lifecycle commit last.
    with tempfile.TemporaryDirectory() as tmpdir:
        logdir = pathlib.Path(tmpdir) / 'not-yet'
        target = logdir / 'x.log'
        def fix(involved, fault):
            logdir.mkdir(exist_ok=True)
            return True
        f = big.File(target, buffering=False)
        log = big.Log(f, threaded=False, fix=fix)
        log("payload")
        log.close()
        assert log._core.poisoned is None
        assert f._core is not None          # still routed and registered
        assert f._session is None           # cleanly ended, not a zombie
        assert 'payload' in target.read_text()


def test_buffer_forwards_lifecycle_to_stateful_underlying():
    # regression: Buffer's docstring promised to wrap an *arbitrary*
    # destination, but it never forwarded register/start/end/
    # unregister--so a File(buffering=False) underneath it faulted
    # on _f is None and got unrouted without ever creating its
    # file, and a Sink never recorded its start/end events.  the
    # lifecycle forwards now.
    with tempfile.TemporaryDirectory() as tmpdir:
        # unbuffered File: start() must forward (it opens the file)
        target = pathlib.Path(tmpdir) / 'wrapped.log'
        log = big.Log(big.Buffer(big.File(target, buffering=False)),
                      threaded=False)
        log("through the buffer")
        log.close()
        assert log._core.poisoned is None
        assert 'through the buffer' in target.read_text()

        # buffered File: Buffer.end() flushes itself AND the
        # underlying before ending it, so File.end()'s
        # empty-buffer invariant holds
        target2 = pathlib.Path(tmpdir) / 'wrapped2.log'
        log2 = big.Log(big.Buffer(big.File(target2)), threaded=False)
        log2("buffered twice")
        log2.close()
        assert 'buffered twice' in target2.read_text()

    # Sink: start/end must forward (they record lifecycle events)
    sink = big.Log.Sink()
    log3 = big.Log(big.Buffer(sink), threaded=False)
    log3("event")
    log3.close()
    types = [e.type for e in sink]
    assert types[0] == 'start'
    assert types[-1] == 'end'
    assert 'log' in types


def test_tmpfile_unbuffered_writes_to_its_real_path():
    # regression: TmpFile.start() called super().start() BEFORE
    # computing its real timestamped path--and unbuffered
    # File.start opens self._path right there.  the log went to
    # the construction-time placeholder (Log-init.<pid>.tmp, only
    # pid-unique!) while destination.path advertised a timestamped
    # file that never existed.  the path is computed first now.
    placeholder = pathlib.Path(tempfile.gettempdir()) / f"Log-init.{os.getpid()}.tmp"
    if placeholder.exists():          # pragma: no cover
        placeholder.unlink()

    d = big.TmpFile(buffering=False)
    log = big.Log(d, threaded=False)
    log("payload")
    log.close()

    try:
        assert d.path.exists()
        assert 'payload' in d.path.read_text()
        assert not placeholder.exists()
    finally:
        if d.path.exists():
            d.path.unlink()
        if placeholder.exists():      # pragma: no cover
            placeholder.unlink()


def test_reconfigure_bad_removed_flush_spares_healthy_tree():
    # regression: the whole reconfiguration ran as ONE job whose
    # involved was inferred as the *formatter*, so a removed
    # destination whose flush() raised got the entire healthy tree
    # unrouted (log false, healthy destination silenced forever)
    # while the bad destination leaked in registered limbo.
    # lifecycle now runs as per-destination attributed jobs.
    healthy = []
    bad = _BadFlushDestination()
    log = big.Log(healthy, bad, threaded=False)   # default fix declines
    log("before reconfigure")
    log.destinations = [healthy]

    assert log                                    # still true
    assert log._core.poisoned is None
    assert bad._core is None                      # fully detached, no leak
    log("after reconfigure")
    log.close()
    assert any("after reconfigure" in s for s in healthy)


def test_reconfigure_hostile_removed_destination_still_detached():
    # the abandonment sweep: a removed destination whose flush()
    # is unfixable and whose end() *also* raises still ends up
    # fully detached--its end() exception is swallowed (fix()
    # already had its chance; tree coherence outranks a dying
    # destination's protests).
    class Hostile(_BadFlushDestination):
        def end(self):
            raise RuntimeError("end failed too")

    healthy = []
    bad = Hostile()
    log = big.Log(healthy, bad, threaded=False)
    log("before")
    log.destinations = [healthy]

    assert bad._core is None          # detached despite the tantrum
    assert log._core.poisoned is None
    log("after")
    log.close()
    assert any("after" in s for s in healthy)


def test_reconfigure_removed_flush_repaired_and_retried():
    # with a repairing fix(), the retry must re-run the *removed
    # destination's own* lifecycle--not the whole reconfiguration,
    # which would recompute removed=[] and silently skip the flush.
    healthy = []
    bad = _BadFlushDestination()
    seen = []
    def fix(involved, fault):
        seen.append(involved)
        bad.broken = False
        return True
    log = big.Log(healthy, bad, threaded=False, fix=fix)
    log("payload")
    log.destinations = [healthy]

    assert seen == [bad]              # attributed to the destination
    assert bad.flushed                # its pending data was written
    assert bad._core is None          # and it was cleanly retired
    assert log._core.poisoned is None
    log.close()


def test_reconfigure_bad_added_start_drops_only_it():
    # a newly added destination whose start() raises engages the
    # fault ladder as itself: it alone is unrouted, the healthy
    # tree keeps logging.
    class Unstartable(log_module.LogDestination):
        def __init__(self):
            super().__init__(types=True)
        def __eq__(self, other): return other is self
        def __hash__(self): return id(self)
        def write(self, o): pass
        def start(self, session):
            raise RuntimeError("can't start")

    healthy = []
    log = big.Log(healthy, threaded=False)
    log("before")                                 # log is started
    bad = Unstartable()
    log.destinations = [healthy, bad]

    assert log._core.poisoned is None
    assert log                                    # healthy destination remains
    log("after")
    log.close()
    assert any("after" in s for s in healthy)


class _UnstartableDestination(log_module.LogDestination):
    # start() raises until repaired--used by the live-route tests
    def __init__(self):
        super().__init__(types=True)
        self.lines = []
        self.broken = True
    def __eq__(self, other): return other is self
    def __hash__(self): return id(self)
    def write(self, o): self.lines.append(o)
    def start(self, session):
        if self.broken:
            raise RuntimeError("start failed")
        super().start(session)


def test_route_bad_start_on_live_log_engages_ladder():
    # regression: route() on a running log ran register/start as
    # bare calls after committing the tables, so a raising start()
    # escaped to route()'s caller with the node routed, registered,
    # and pre-marked started--and close() then poisoned the core
    # ("can't end ..., it wasn't started").  lifecycle now runs as
    # per-node attributed jobs: the failing node is unrouted, the
    # tables stay coherent, route() returns.
    healthy = []
    log = big.Log(healthy, threaded=False)
    log("running")                        # log is started
    bad = _UnstartableDestination()
    log.route(log.formatter, bad)         # returns; ladder unroutes bad

    core = log._core
    assert bad not in core.routes[log.formatter.key]
    assert bad._core is None
    assert bad._key not in core.started
    assert bad not in log._destinations
    log("after the failed route")
    log.close()
    assert core.poisoned is None
    assert any("after the failed route" in s for s in healthy)


def test_route_bad_start_repaired_by_fix():
    # the ladder gives fix() its chance: a repaired start is
    # retried, and the destination is kept and delivers.
    healthy = []
    bad = _UnstartableDestination()
    def fix(involved, fault):
        involved.broken = False
        return True
    log = big.Log(healthy, threaded=False, fix=fix)
    log("running")
    log.route(log.formatter, bad)
    log("delivered to both")
    log.close()
    assert log._core.poisoned is None
    assert any("delivered to both" in s for s in bad.lines)


def test_route_foreign_registered_node_rejected_atomically():
    # a node already registered to ANOTHER log is a configuration
    # error: ValueError, raised before any mutation.  (previously
    # a destination hit RuntimeError from register() after the
    # tables were committed, and a formatter hit a bare assert that
    # vanishes under -O.)
    d = log_module.List([])
    log1 = big.Log(d, threaded=False)

    log2 = big.Log([], threaded=False)
    with raises(ValueError):
        log2.route(log2.formatter, d)
    assert d not in log2._core.routes[log2.formatter.key]

    f = log_module.TextFormatter()
    log1.route(f, [])                     # f now registered to log1
    with raises(ValueError):
        log2.route(f, [])                 # as a new top-level parent
    assert f.key not in log2._core.routes

    filt = log_module.Filter(lambda s: s)
    log1.route(log1.formatter, filt)      # filt now registered to log1
    with raises(ValueError):
        log2.route(log2.formatter, filt)  # as a child
    assert filt.key not in log2._core.routes

    log1("still works")
    log2("still works")
    log1.close()
    log2.close()
    assert log1._core.poisoned is None
    assert log2._core.poisoned is None


def test_job_explicit_involved_none_is_not_inferred():
    # white box: Job(involved=None) means "nothing is involved"--
    # inference happens only for the _INFER_INVOLVED default.  a
    # fault in such a job is unattributable (poisons) instead of
    # being blamed on a node that appeared in the arguments.
    Job = log_module.Job
    dest = log_module.List([])
    job = Job(print, (dest,), involved=None)
    assert job.involved is None
    job2 = Job(print, (dest,))
    assert job2.involved is dest


def test_file_flush_retry_keeps_payload():
    # regression: File.flush cleared its buffer BEFORE the fallible
    # open/write, so a transient failure repaired by fix() retried
    # against an empty buffer--the log stayed healthy and the
    # payload silently vanished.  the buffer is now cleared only
    # after the write succeeds.
    with tempfile.TemporaryDirectory() as tmpdir:
        logdir = pathlib.Path(tmpdir) / 'not-yet'   # doesn't exist yet
        target = logdir / 'x.log'
        def fix(involved, fault):
            logdir.mkdir(exist_ok=True)             # repair the filesystem
            return True                             # and retry
        log = big.Log(big.File(target), threaded=False, fix=fix)
        log("precious payload")
        log.flush()                                 # open fails -> fix -> retry
        log("after the repair")
        log.close()
        assert log._core.poisoned is None
        text = target.read_text()
        assert "precious payload" in text
        assert "after the repair" in text


def test_buffer_flush_retry_keeps_payload():
    # the Buffer variant of the same bug: it detached its buffer
    # into a local before calling the underlying destination.
    state = {'broken': True}
    received = []
    def flaky_writer(s):
        if state['broken']:
            raise RuntimeError("transient")
        received.append(s)
    def fix(involved, fault):
        state['broken'] = False
        return True
    log = big.Log(big.Buffer(flaky_writer), threaded=False, fix=fix)
    log("precious payload")
    log.flush()
    log("after the repair")
    log.close()
    assert log._core.poisoned is None
    joined = ''.join(received)
    assert "precious payload" in joined
    assert "after the repair" in joined


def test_buffer_per_message_flush_retries_only_unwritten_tail():
    # the per-message branch (an underlying accepting arbitrary
    # types) pops each message after its write succeeds, so a
    # mid-loop failure retries only the unwritten tail--every
    # message delivered exactly once, no duplicates.
    class Picky(log_module.LogDestination):
        def __init__(self):
            super().__init__(types=True)
            self.received = []
            self.fail_on = 'two'
        def __eq__(self, other): return other is self
        def __hash__(self): return id(self)
        def write(self, o):
            if self.fail_on and (self.fail_on in o):
                raise RuntimeError("transient")
            self.received.append(o)

    picky = Picky()
    def fix(involved, fault):
        picky.fail_on = None
        return True
    buffer = log_module.Buffer(picky)
    log = big.Log(buffer, threaded=False, fix=fix,
                  formatter=log_module.TextFormatter(prefix=''))
    log("one")
    log("two")
    log("three")
    log.flush()                     # fails on "two" -> fix -> retry
    log.close()
    assert log._core.poisoned is None
    joined = ''.join(picky.received)
    for word in ('one', 'two', 'three'):
        assert joined.count(word) == 1, f"{word!r} delivered {joined.count(word)} times"


def test_concurrent_child_churn_keeps_handles_exact():
    # regression: session.handles was a bare +=/-= counter, and two
    # threads closing their own (different) child handles both
    # mutate the shared parent counter--a read-modify-write that
    # loses updates under preemption.  observed live on 3.6-3.9
    # (3.10+ interpreters currently don't split the window, which
    # is an accident, not a guarantee).  a lost decrement means the
    # session never closes; a lost increment closes it early,
    # silently dropping a live handle's messages.  handles is now
    # guarded by configuration_lock.
    log = big.Log(None, threaded=True)
    log("wake")
    session = log._session
    THREADS, ITERS = 4, 200
    barrier = threading.Barrier(THREADS)
    def churn():
        barrier.wait()
        for i in range(ITERS):
            child = log.child('c')
            child.close()
    threads = [threading.Thread(target=churn) for _ in range(THREADS)]
    for t in threads: t.start()
    for t in threads: t.join()
    log.flush()
    # exactly one handle remains: the root Log itself
    assert session.handles == 1, f"handles drifted: {session.handles}"
    log.close()


def test_atexit_delivers_end_lifecycle_despite_slow_worker():
    # regression: at atexit, the _end job could be enqueued *after*
    # the shutdown None job (main just has to win two wake-up races
    # against the worker--rare on an idle box, real on a loaded
    # one), and drain mode discarded it: no destination got end(),
    # no SinkEndEvent was recorded, while the end banner text made
    # the log *look* complete.  _stop_thread now waits on a
    # normal-lane barrier after reset(), so _end is always enqueued
    # before the None.  simulate the losing interleave by giving
    # the worker an OS-scheduling hiccup before every job pop.
    class EndTracker(log_module.LogDestination):
        def __init__(self):
            super().__init__(types=True)
            self.ended = False
        def __eq__(self, other): return other is self
        def __hash__(self): return id(self)
        def write(self, o): pass
        def end(self):
            super().end()
            self.ended = True

    tracker = EndTracker()
    sink = big.Log.Sink()
    log = big.Log(tracker, sink, threaded=True)
    q = log._core.queue
    orig_next = type(q).__next__
    def slow_next(self):
        time.sleep(0.005)
        return orig_next(self)
    type(q).__next__ = slow_next
    try:
        log("hello")
        log._atexit()
    finally:
        type(q).__next__ = orig_next

    assert tracker.ended, "destination end() was discarded by the atexit drain"
    assert any(isinstance(e, big.SinkEndEvent) for e in sink)


def test_straggler_message_after_end_is_dropped():
    # white box: _end rides the priority lane, so a queued message
    # job can run after it.  Core.log drops such stragglers (the
    # started set is None) instead of writing to ended destinations.
    a = []
    log = testing_log(a)
    core = log._core
    session = log._session
    log("first")
    message = session.Message(log._clock(), '', ("straggler",), {})
    log.close()
    assert core.started is None
    core.log(message)               # dropped: no crash, no write
    assert not any("straggler" in s for s in a)


def test_flush_concurrent_with_routing_does_not_crash():
    # regression: Core.flush iterated self.routes on the caller's
    # thread with no lock; a concurrent route() growing the dict
    # (or the fault ladder shrinking it) crashed the flusher with
    # "RuntimeError: dictionary changed size during iteration".
    # flush now snapshots the destinations under configuration_lock.
    log = big.Log([], threaded=True)
    log("start")

    crashed = []
    done = threading.Event()
    def flusher():
        try:
            while not done.is_set():
                log.flush(wait=False)
        except BaseException as e:   # pragma: no cover
            crashed.append(e)
    t = threading.Thread(target=flusher, daemon=True)
    t.start()
    try:
        for i in range(500):
            log.route(log.formatter, log_module.Filter(lambda s: s))
    finally:
        done.set()
        t.join(10)
    assert not crashed, f"flush() crashed against concurrent routing: {crashed[0]!r}"
    log.close()


def test_flush_from_worker_thread_does_not_deadlock():
    # regression: log.flush() lacked the never-wait-on-the-worker
    # downgrade that Core.flush and close() have.  a destination
    # (running as a job on the worker) that called log.flush()
    # queued a blocker-release job behind itself and waited for
    # itself, freezing the log--and then every other flush/close.
    log = None
    lines = []
    def eager_destination(s):
        lines.append(s)
        log.flush()             # used to deadlock the worker right here

    log = big.Log(eager_destination, threaded=True)

    returned = []
    def target():
        log("hello")
        log.flush()             # used to hang waiting on the frozen worker
        returned.append(True)
    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(10)
    assert returned, "flush() deadlocked against a reentrant worker flush"
    assert any("hello" in s for s in lines)
    log.close()


def test_queue_internals_white_box():
    log = testing_log([])
    core = log._core
    Queue = type(core).Queue
    Job = log_module.Job

    q = Queue(core, block=False)
    # empty extend / prepend return early
    q.extend([])
    q.prepend([])

    # remove a matching job: increments deletions and pops it
    marker = object()
    q.extend([Job(lambda: None, (), involved=marker), Job(lambda: None, ())])
    q.remove(lambda job: job.involved is marker)
    assert q.deletions == 1

    # __next__ swallows one notification per deletion, then returns
    # the surviving job
    survivor = next(iter(q))
    assert survivor is not None

    # drain mode: a None-method job flips drain on; a subsequent job
    # whose involved is a Lock gets released and skipped
    lock = threading.Lock()
    lock.acquire()
    q2 = Queue(core, block=False)
    q2.extend([Job(None, ()), Job(lambda: None, (), involved=lock)])
    # drain consumes both jobs internally and yields nothing
    assert list(q2) == []
    assert not lock.locked()

    log.close()

def test_session_closed_property():
    log = testing_log([])
    log("warm")
    root = log._session
    assert root.closed is False
    # force the state to closed and re-check
    root.state = log_module.STATE_CLOSED
    assert root.closed is True
    log.close()

def test_empty_scheduler_call():
    log = testing_log([])
    core = log._core
    scheduler = core.Scheduler()
    scheduler()               # no jobs added -> early return
    log.close()

def test_paused_counter_after_close():
    # a closed log has no session; _paused_counter reports 0
    log = testing_log([])
    log("x")
    log.close()
    assert log._session is None
    assert log._paused_counter == 0

def test_child_constructed_with_no_time():
    # constructing a Child with no time= takes it from the parent
    # clock (log.child always passes time, so build one directly)
    log = testing_log([])
    log("warm")
    root = log._session
    child = log_module.Child("wb", log._core, root)   # no time=
    assert child is not None
    log.close()

def test_write_after_close_is_dropped():
    a = []
    log = testing_log(a)
    log("x")
    log.close()
    log.write("after close")     # session is closed -> early return
    assert not any("after close" in s for s in a)

def test_core_lifecycle_idempotent():
    # _end and atexit are idempotent: a second call returns early
    log = testing_log([])
    log("x")
    core = log._core
    core._end()
    core._end()                  # started is None now -> return
    core.atexit()
    core.atexit()                # exited already -> return
    log.close()

def test_execute_poisons_on_unfixable_fault():
    # a job whose 'involved' isn't a formatter or destination (an
    # internal job) can't be dropped-and-isolated; a fault there
    # poisons the whole log
    log = testing_log([])
    core = log._core
    def boom():
        raise RuntimeError("internal machinery fault")
    core.execute([log_module.Job(boom, (), involved=None)])
    assert isinstance(core.poisoned, RuntimeError)

def test_route_sink_under_non_textformatter():
    # routing a Sink whose parent is a plain (non-TextFormatter)
    # formatter builds a bare SinkFormatter()
    log = testing_log([])
    sink = big.Sink()
    filt = log_module.Filter(lambda s: s, name='f')
    log.route(log.formatter, filt)
    log.route(filt, sink)
    log("into the sink chain")
    log.close()

def test_route_duplicate_child_is_ignored():
    # routing the same child twice: the second is a no-op (continue)
    log = testing_log([])
    f = log_module.Filter(lambda s: s, name='f')
    d = []
    log.route(log.formatter, f)
    log.route(f, d)
    log.route(f, d)              # d already routed under f -> continue
    log("x")
    log.close()

def test_route_defensive_format_branches_white_box():
    # two branches of route() that normal formatters can't reach
    # (every formatter's .formats contains '', and .formats is
    # always a frozenset, never True): force them white-box.
    log = testing_log([])
    core = log._core

    # 'no formats in common': force core.formats to a set with no
    # overlap, then route a fresh formatter
    f1 = log_module.TextFormatter(log_module.ascii_format_dict())
    saved = core.formats
    core.formats = frozenset({'nonexistent-format-name'})
    try:
        with raises(ValueError):
            core.route(f1, [[]])
    finally:
        core.formats = saved

    # 'parent.formats is True' branch: a formatter reporting
    # formats=True routed while core.formats is not True
    f2 = log_module.TextFormatter(log_module.ascii_format_dict())
    f2.formats = True
    core.route(f2, [[]])
    log.close()

def test_log_method_on_poisoned_log():
    # the .log() method (not the plain call, which is .print()) has
    # its own poison guard
    log = testing_log([])
    log._core.poisoned = RuntimeError("poisoned")
    with raises(RuntimeError):
        log.log("boom")

def test_log_no_args():
    # log() with no args is legal: an empty message line
    a = []
    log = testing_log(a)
    log.log()
    log.close()

def test_write_after_close_returns():
    a = []
    log = testing_log(a)
    log("x")
    log.close()
    log.write("dropped")    # session closed -> return at the guard
    assert not any("dropped" in s for s in a)

def test_recap_enter_banner_for_unbuffered_child():
    # a late destination that joins while an *unbuffered* child
    # session is active gets that child's 'enter' banner recapped
    early, late = [], []
    log = big.Log(early, threaded=False,
        formatter=log_module.TextFormatter(log_module.ascii_format_dict()))
    log("before")
    kid = log.child("subsystem", buffered=False)
    kid("in child")
    log.destinations = [early, late]     # joins with the child active
    kid("more")
    log.close()
    assert any("subsystem" in s for s in late)

def test_stop_thread_noop_when_not_threaded():
    # _stop_thread returns immediately for a non-threaded log
    log = testing_log([])
    log._core._stop_thread()
    log.close()

def test_reset_then_close():
    # reset then close exercises the idempotent session unregister
    log = testing_log([])
    log("x")
    log.reset()
    log.close()

def test_empty_template_format_renders_nothing():
    import copy
    fd = copy.deepcopy(log_module.ascii_format_dict())
    fd.setdefault('formats', {})['silent'] = {'template': ''}
    a = []
    log = big.Log(a, threaded=False, formatter=log_module.TextFormatter(fd))
    log.log("nothing rendered", format='silent')    # empty template -> continue
    log.close()

def test_oldlog_banners_drive_olddestination():
    # driving OldLog's enter/exit produces start/end banner events,
    # which OldDestination.write skips
    old = big.OldLog()
    old("first")
    old.enter("subsystem")
    old("inside")
    old.exit()
    old("last")
    output = []
    old.print(print=output.append)
    assert output

def test_route_top_level_formatter_as_child_white_box():
    # routing an already-top-level formatter as somebody's child is
    # an error; the type-compatibility guard normally fires first,
    # so force past it (accepts=True) to reach the routing guard
    log = testing_log([])
    top = log_module.TextFormatter(log_module.ascii_format_dict())
    log.route(top, [[]])            # top is now top-level
    top.accepts = True             # make it type-compatible as a child
    with raises(ValueError):
        log._core.route(log.formatter, [top])
    log.close()

def test_empty_template_write_renders_blank_line():
    # an empty template renders '' and the pipeline's cleanup
    # appends the newline every log line ends with: a blank line.
    # nothing is dropped--the log doesn't second-guess templates.
    import copy
    fd = copy.deepcopy(log_module.ascii_format_dict())
    fd.setdefault('formats', {})['silent'] = {'template': ''}
    a = []
    log = big.Log(a, threaded=False, formatter=log_module.TextFormatter(fd))
    log.write("dropped", format='silent')
    log.close()
    assert not any("dropped" in s for s in a)
    assert '\n' in a

def test_empty_template_formatter_still_renders():
    # two formatters share a format; one's template is empty.  both
    # render: the full one produces the message, the empty one a
    # blank line.
    import copy
    fd_full = copy.deepcopy(log_module.ascii_format_dict())
    fd_full.setdefault('formats', {})['common'] = {'template': '{message}'}
    fd_empty = copy.deepcopy(log_module.ascii_format_dict())
    fd_empty.setdefault('formats', {})['common'] = {'template': ''}
    a, b = [], []
    log = big.Log(a, threaded=False, formatter=log_module.TextFormatter(fd_full))
    log.route(log_module.TextFormatter(fd_empty), b)
    log.log("visible", format='common')
    log.close()
    assert any("visible" in s for s in a)
    assert '\n' in b

def test_olddestination_skips_banner_events():
    # OldDestination.write ignores 'start'/'end' banner events (the
    # lifecycle "log start" line already covers them)
    class BannerEvent:
        ns = 0
        type = 'log'
        format = 'start'
        formatted = ''
        message = ''
    dest = log_module.OldDestination()
    dest._initial = 0
    dest.write(BannerEvent())     # start banner -> return, nothing recorded
    assert not dest.events

def test_session_handle_unregister_is_idempotent():
    # a session handle's unregister closure is idempotent: the
    # second call returns immediately
    log = testing_log([])
    log("x")
    session = log._session
    unregister = session.register(log)   # returns an unregister closure
    unregister()
    unregister()                          # second call -> early return
    log.close()

def test_message_fstate_none_when_format_undefined():
    # session.message_fstate for a formatter that doesn't define the
    # format: formatter.format() returns None, so the fstate is used
    # as-is (white-box: normal logging can't get here, because the
    # Message constructor requires the format be defined by all
    # formatters)
    log = testing_log([])
    log("x")
    session = log._session
    result = session.message_fstate(log.formatter, 'undefined_format_xyz')
    assert result is not None
    log.close()

def test_core_log_skips_missing_formatter_key():
    # Core.log tolerates a prepared key whose formatter is no longer
    # registered (collateral of a fault that removed it): skip it
    log = testing_log([])
    log("x")
    core = log._core
    class GhostMessage:
        prepared = {('ghost', 0, 0): None}
    core.log(GhostMessage())     # ghost key not in formatters_by_key -> skip
    log.close()

def run_tests(run=None):
    (run or bigtestlib.run)(name="big.log", module=__name__)


if __name__ == "__main__":  # pragma: no cover
    run_tests()
    bigtestlib.finish()
