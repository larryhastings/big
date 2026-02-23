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

import builtins
import big.all as big
import big.log as log_module
import io
import os.path
import pathlib
import tempfile
import threading
import time
import unittest


class FakeClock:
    def __init__(self):
        self.time = 0

    def __call__(self):
        return self.time

    def advance(self, ns=12_000_000):
        self.time += ns


class EventSink(big.Log.Destination):
    """
    A custom destination that just logs event names.
    """

    def __init__(self):
        super().__init__()
        self.value = ''

    def _event(self, s):
        if self.value:
            s = f"{self.value} {s}"

        self.value = s

    def reset(self):
        self._event("reset")

    def flush(self):
        self._event("flush")

    def start(self, start_time_ns, start_time_epoch):
        self._event("start")

    def end(self, elapsed):
        self._event("end")

    def write(self, elapsed, thread, formatted):
        self._event("write")

    def log(self, elapsed, thread, format, message, formatted):
        self._event("log")

    def enter(self, elapsed, thread, message):
        self._event("enter")

    def exit(self, elapsed, thread):
        self._event("exit")



class TestDestination(unittest.TestCase):
    """Tests for the base Destination class."""

    def test_destination_init(self):
        destination = big.Log.Destination()
        self.assertIsNone(destination.owner)

    def test_destination_register(self):
        destination = big.Log.Destination()
        destination.owner = None  # Reset to allow re-registration
        destination.register("test_owner")
        self.assertEqual(destination.owner, "test_owner")

    def test_destination_register_already_registered(self):
        destination = big.Log.Destination()
        destination.owner = None
        destination.register("owner1")
        with self.assertRaises(RuntimeError) as cm:
            destination.register("owner2")
        self.assertIn("already registered", str(cm.exception))

    def test_destination_virtual_write(self):
        destination = big.Log.Destination()
        with self.assertRaises(RuntimeError):
            destination.write(0, None, "test")

    def test_destination_flush_does_nothing(self):
        destination = big.Log.Destination()
        destination.flush()  # Should not raise

    def test_destination_close_does_nothing(self):
        destination = big.Log.Destination()
        destination.end(12345)  # Should not raise

    def test_destination_reset(self):
        destination = big.Log.Destination()
        destination.reset()


class TestCallable(unittest.TestCase):
    """Tests for the Callable destination."""

    def test_callable_write(self):
        results = []
        c = big.Log.Callable(results.append)
        c.write(0, None, "test string")
        self.assertEqual(results, ["test string"])


class TestPrint(unittest.TestCase):
    """Tests for the Print destination."""

    def test_print_write(self):
        captured = []
        original_print = builtins.print
        builtins.print = lambda *args, **kwargs: captured.append((args, kwargs))
        try:
            printer = big.Log.Print()
            printer.write(0, None, "hello")
        finally:
            builtins.print = original_print
        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0][0], ("hello",))
        self.assertEqual(captured[0][1], {"end": "", "flush": True})


class TestList(unittest.TestCase):
    """Tests for the List destination."""

    def test_list_write(self):
        array = []
        list_destination = big.Log.List(array)
        list_destination.write(0, None, "line1\n")
        list_destination.write(0, None, "line2\n")
        self.assertEqual(array, ["line1\n", "line2\n"])


class TestBuffer(unittest.TestCase):
    """Tests for the Buffer destination."""

    def test_buffer_write_and_flush(self):
        captured = []
        original_print = builtins.print
        builtins.print = lambda *args, **kwargs: captured.append((args, kwargs))
        try:
            buffer = big.Log.Buffer()
            buffer.write(0, None, "hello ")
            buffer.write(0, None, "world")
            self.assertEqual(buffer.array, ["hello ", "world"])
            buffer.flush()
            self.assertEqual(buffer.array, [])
        finally:
            builtins.print = original_print
        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0][0], ("hello world",))

    def test_buffer_flush_empty(self):
        buffer = big.Log.Buffer()
        buffer.flush()  # Should not raise or print


class TestFile(unittest.TestCase):
    """Tests for the File destination."""

    def test_map_destination_support(self):
        # if we never start logging, we don't open the file,
        # so we don't have to clean up here
        expected = pathlib.Path('/tmp/x')
        log = big.Log('/tmp/x')
        log.close()
        self.assertEqual(log.destinations[0].path, expected)

        log = big.Log(b'/tmp/x')
        log.close()
        self.assertEqual(log.destinations[0].path, expected)

        log = big.Log(pathlib.Path('/tmp/x'))
        log.close()
        self.assertEqual(log.destinations[0].path, expected)

    def test_file_type_checks(self):
        with self.assertRaises(TypeError):
            big.Log.File(3456)
        with self.assertRaises(TypeError):
            big.Log.File(3.14159)
        with self.assertRaises(TypeError):
            big.Log.File([1, 2, 3])
        with self.assertRaises(TypeError):
            big.Log.File({'a': 'b'})

        with self.assertRaises(ValueError):
            big.Log.File('')
        with self.assertRaises(ValueError):
            big.Log.File(b'')

        with self.assertRaises(TypeError):
            big.Log.File('xyz', b'at')
        with self.assertRaises(TypeError):
            big.Log.File('xyz', [1, 2, 3])
        with self.assertRaises(TypeError):
            big.Log.File('xyz', 8475)
        with self.assertRaises(ValueError):
            big.Log.File('xyz', '')
        with self.assertRaises(ValueError):
            big.Log.File('xyz', 'marjoram')

    def test_file_buffered_mode(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            path = f.name

        try:
            file_destination = big.Log.File(path, initial_mode='wt')
            file_destination.write(0, None, "line1\n")
            file_destination.write(0, None, "line2\n")
            self.assertEqual(file_destination.array, ["line1\n", "line2\n"])

            # File should be empty before flush
            with open(path, 'r') as f:
                self.assertEqual(f.read(), "")

            file_destination.flush()
            self.assertEqual(file_destination.array, [])

            with open(path, 'r') as f:
                content = f.read()
            self.assertEqual(content, "line1\nline2\n")

            # Close should work when array is empty
            file_destination.end(12345)
        finally:
            os.unlink(path)

    def test_file_immediate_mode(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            path = f.name

        try:
            fd = big.Log.File(path, initial_mode='wt', flush=True)
            log = big.Log(fd, threading=False)

            log.write("immediate\n")

            # File should have content immediately
            with open(path, 'r') as f:
                content = f.read()
            self.assertIn("immediate\n", content)

            log.close()
        finally:
            os.unlink(path)


    def test_file_append_mode(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            path = f.name
            f.write("existing\n")

        try:
            fd = big.Log.File(path, initial_mode='at')
            log = big.Log(fd, threading=False)
            log.write("appended\n")
            log.close()

            with open(path, 'r') as f:
                content = f.read()
            self.assertIn("existing\n", content)
            self.assertIn("appended\n", content)
        finally:
            os.unlink(path)

    def test_TmpFile(self):
        path = None
        try:
            tmpfile = big.log.Log.TmpFile()
            log = big.Log(tmpfile, name="LogName", threading=False, formats={"start": None, "end": None}, prefix='', timestamp_format=lambda x:"ABACAB /DEADBEEF")
            log("xyz")
            path = tmpfile.path.name
            log.close()

            expected = f"LogName.ABACAB.-DEADBEEF.{os.getpid()}.MainThread.txt"
            self.assertEqual(path, expected)
        finally:
            if path and os.path.exists(path): # pragma: nocover
                os.unlink(path)

        path = None
        try:
            tmpfile = big.log.Log.TmpFile(prefix='wackadoodle')
            log = big.Log(tmpfile, name="LogName", threading=False, formats={"start": None, "end": None}, prefix='', timestamp_format=lambda x:"ABACAB /DEADBEEF")
            log("xyz")
            path = tmpfile.path.name
            log.close()

            expected = f"wackadoodle.ABACAB.-DEADBEEF.{os.getpid()}.MainThread.txt"
            self.assertEqual(path, expected)
        finally:
            if path and os.path.exists(path): # pragma: nocover
                os.unlink(path)

        with self.assertRaises(TypeError):
            big.log.Log.TmpFile(prefix=345)
        with self.assertRaises(TypeError):
            big.log.Log.TmpFile(prefix=3.1415)
        with self.assertRaises(TypeError):
            big.log.Log.TmpFile(prefix=[1, 2, 3])
        with self.assertRaises(TypeError):
            big.log.Log.TmpFile(prefix={'a': 'b'})
        with self.assertRaises(TypeError):
            big.log.Log.TmpFile(prefix=b'foo bar')



class TestFileHandle(unittest.TestCase):
    """Tests for the FileHandle destination."""

    def test_invalid_filehandle(self):
        with self.assertRaises(TypeError):
            big.Log.FileHandle(None)

    def test_filehandle_write(self):
        buffer = io.StringIO()
        fh_destination = big.Log.FileHandle(buffer)
        fh_destination.write(0, None, "test content")
        self.assertEqual(buffer.getvalue(), "test content")

    def test_filehandle_write_with_flush(self):
        buffer = io.StringIO()
        fh_destination = big.Log.FileHandle(buffer, flush=True)
        fh_destination.write(0, None, "test content")
        self.assertEqual(buffer.getvalue(), "test content")

    def test_filehandle_flush(self):
        buffer = io.StringIO()
        fh_destination = big.Log.FileHandle(buffer)
        fh_destination.flush()  # Should not raise


class TestLogBasics(unittest.TestCase):
    """Basic tests for the Log class."""

    def test_log_properties(self):
        ns = big.log.default_clock()
        epoch = time.time()
        time.sleep(0.001)

        log = big.Log(None)

        self.assertEqual(log.clock, big.log.default_clock)
        self.assertEqual(log.indent, 4)
        self.assertEqual(log.name, 'Log')
        self.assertEqual(log.prefix, big.log.prefix_format(3, 10, 12))
        self.assertEqual(log.threading, True)
        self.assertEqual(log.timestamp_format, big.time.timestamp_human)
        self.assertEqual(log.timestamp_clock, time.time)
        self.assertEqual(log.width, 79)

        self.assertEqual(log.closed, False)
        self.assertGreater(log.start_time_ns, ns)
        self.assertGreater(log.start_time_epoch, epoch)
        self.assertEqual(log.end_time_epoch, None)
        self.assertEqual(log.nesting, ())
        self.assertEqual(log.depth, 0)

        log.enter("xyz")
        log.flush()
        self.assertEqual(log.nesting, ('xyz',))
        self.assertEqual(log.depth, 1)

    def test_log_default_destination(self):
        # With no destinations specified, should use print
        captured = []
        original_print = builtins.print
        builtins.print = lambda *args, **kwargs: captured.append((args, kwargs))
        try:
            log = big.Log(threading=False)
            log("test message")
            log.close()
        finally:
            builtins.print = original_print
        self.assertTrue(len(captured) > 0)

    def test_log_with_list(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        log("hello")
        log.close()
        self.assertTrue(any("hello" in s for s in array))

    def test_log_with_path_string(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            path = f.name

        try:
            log = big.Log(path, threading=False, formats={"start": None, "end": None}, prefix='')
            log("test message")
            log.close()

            with open(path, 'r') as f:
                content = f.read()
            self.assertIn("test message", content)
        finally:
            os.unlink(path)

    def test_log_with_callable(self):
        results = []
        log = big.Log(results.append, threading=False, formats={"start": None, "end": None}, prefix='')
        log("callable test")
        log.close()
        self.assertTrue(any("callable test" in s for s in results))

    def test_log_with_none_destination(self):
        # None destinations should be skipped
        array = []
        log = big.Log(None, array, None, threading=False, formats={"start": None, "end": None}, prefix='')
        log("test")
        log.close()
        self.assertTrue(len(array) > 0)

    def test_log_with_invalid_destination(self):
        with self.assertRaises(TypeError) as cm:
            log = big.Log(12345, threading=False)
        self.assertIn("don't know how to log to destination", str(cm.exception))


    def test_extensible_destination_mapper(self):
        with self.assertRaises(TypeError) as cm:
            log = big.Log(12345, threading=False)


        try:
            # undocumented interface!
            def custom_destination_mapper(o):
                if isinstance(o, int):
                    return EventSink()
                return None

            big.Log.destination_mappers.append(custom_destination_mapper)
            log = big.Log(12345, [], print, threading=False, formats={"start": None, "end": None}, prefix='')
            destinations = list(log.destinations)
            self.assertIsInstance(destinations[0], EventSink)
            self.assertIsInstance(destinations[1], big.Log.List)
            self.assertIsInstance(destinations[2], big.Log.Print)
        finally:
            big.Log.destination_mappers.clear()

    def test_exit_without_logging_or_enter(self):
        sink = EventSink()
        log = big.Log(sink, threading=False, formats={"start": None, "end": None}, prefix='')
        log.exit()
        log.close()
        self.assertFalse(sink.value)

    def test_log_after_closed(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        log.close()
        log("after close")
        log.close()
        self.assertFalse(array)

    def test_log_write_after_closed(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        log.close(block=False)
        log.write("after close")
        log.close(block=True)
        self.assertFalse(array)

    def test_log_heading_after_closed(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        log.close()
        log.box("after close")
        log.close()
        self.assertFalse(array)

    def test_log_close_is_idempotent(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        self.assertFalse(log.closed)
        log.close()
        self.assertTrue(log.closed)
        log.close()
        self.assertTrue(log.closed)

    def test_log_dirty(self):
        array = []
        log = big.Log(array, threading=False)
        self.assertFalse(log.dirty)
        log.write("hello pigpen!\n")
        self.assertTrue(log.dirty)
        log.flush()
        self.assertFalse(log.dirty)

    def test_log_atexit(self):
        for threading in (False, True):
            for log_once in (False, True):
                with self.subTest(threading=threading, log_once=log_once):
                    log = big.Log([], threading=threading)
                    self.assertFalse(log.closed)
                    if log_once:
                        log("hello!")
                        log.flush()
                    log._atexit()
                    self.assertTrue(log.closed)
                    # log ignores reset after atexit
                    log.reset()
                    self.assertTrue(log.closed)

    def test_log_name(self):
        log = big.Log(name='xyz')
        self.assertEqual(log.name, 'xyz')
        log.close()

        with self.assertRaises(TypeError):
            big.Log(name=385)

        with self.assertRaises(TypeError):
            big.Log(name=3.1415)

        with self.assertRaises(TypeError):
            big.Log(name=[1, 2, 3])

        with self.assertRaises(TypeError):
            big.Log(name={1:2})

        with self.assertRaises(ValueError):
            big.Log(name='')




class TestLogMethods(unittest.TestCase):
    """Tests for Log methods."""

    def test_print(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        log.print("via print method")
        log.close()
        self.assertTrue(any("via print method" in s for s in array))

    def test_multiline_print(self):
        buffer = io.StringIO()
        log = big.Log(buffer, threading=False, formats={"start": None, "end": None}, prefix='[-] ')
        log("This message has multiple lines!\nHere's line two.\n  Line three is indented a little!\nAnd this is the final line.")
        log.close()
        self.assertEqual(buffer.getvalue(),
"""
[-] This message has multiple lines!
[-] Here's line two.
[-]   Line three is indented a little!
[-] And this is the final line.
""".lstrip()
)

    def test_log_write(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        log.write("raw write\n")
        log.close()
        self.assertTrue(any("raw write" in s for s in array))

    def test_log_write_not_string(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        with self.assertRaises(TypeError):
            log.write(12345)
        log.close()

    def test_log_blank_line(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, formats={"start": None, "end": None}, prefix='[PREFIX] ')
        log("before")
        log() # should inject an empty line into the log (but should still have the prefix)
        log("after")
        log.close()
        self.assertEqual(s.getvalue(), "[PREFIX] before\n[PREFIX]\n[PREFIX] after\n")

    def test_log_box(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        log.box("call-out text")
        log.close()
        self.assertTrue(any("call-out text" in s for s in array))

    def test_multiline_box(self):
        buffer = io.StringIO()
        log = big.Log(buffer, threading=False, formats={"start": None, "end": None}, prefix='[#] ')
        log.box("Multi-line box!\nVery pretty.")
        log.close()
        self.assertEqual(buffer.getvalue(),
"""
[#] +--------------------------------------------------------------------------
[#] | Multi-line box!
[#] | Very pretty.
[#] +--------------------------------------------------------------------------
""".lstrip()
)

    def test_log_box_not_string(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, formats={"start": None, "end": None}, prefix='', width=7)
        log.box(12345)
        log.close()
        self.assertEqual(s.getvalue(), "+------\n| 12345\n+------\n")

    def test_log_empty_thread(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, formats={"start": {'template': "thread.name={thread.name} thread={thread} thread!r={thread!r} thread.ident={thread.ident} thread.native_id={thread.native_id} thread.daemon={thread.daemon}"}, "end": None}, prefix='')
        log('boo')
        log.close()
        self.assertEqual(s.getvalue(), "thread.name= thread= thread!r= thread.ident= thread.native_id= thread.daemon=\nboo\n")

    def test_log_enter_exit(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        log.enter("subsystem")
        log("inside")
        log.exit()
        log.close()
        output = ''.join(array)
        self.assertIn("subsystem", output)
        self.assertIn("inside", output)

    def test_multiline_enter(self):
        buffer = io.StringIO()
        log = big.Log(buffer, threading=False, formats={"start": None, "end": None}, prefix='[_] ')
        with log.enter("Multi-line enter!\nWhat will happen?"):
            log("zzz...")
        log.close()
        self.assertEqual(buffer.getvalue(),
"""
[_] +-----+--------------------------------------------------------------------
[_] |enter| Multi-line enter!
[_] |     | What will happen?
[_] +-----+--------------------------------------------------------------------
[_]     zzz...
[_] +-----+--------------------------------------------------------------------
[_] |exit | Multi-line enter!
[_] |     | What will happen?
[_] +-----+--------------------------------------------------------------------
""".lstrip())

    def test_log_enter_context_manager(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        with log.enter("subsystem"):
            log("inside context")
        log.close()
        output = ''.join(array)
        self.assertIn("subsystem", output)
        self.assertIn("inside context", output)

    def test_log_unbalanced_exit(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, formats={"start": None, "end": None}, prefix='')
        log.enter("entered!")
        log.exit()
        log.exit()
        log.exit()
        log.close()
        self.assertIn("entered!\n", s.getvalue())

    def test_reuse_log(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        log.write("before reset")
        log.close()
        log.reset()
        log.write("after reset")
        log.close()
        self.assertIn("before reset", array)
        self.assertIn("after reset", array)

    def test_log_sep_end_params(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        log("a", "b", "c", sep="-", end="!\n")
        log.close()
        self.assertTrue(any("a-b-c!" in s for s in array))

        with self.assertRaises(TypeError):
            log(35, sep=35)
        with self.assertRaises(TypeError):
            log(36, end=36)
        with self.assertRaises(TypeError):
            log.print(37, sep=37)
        with self.assertRaises(TypeError):
            log.print(38, end=38)

    def test_log_with_flush_param(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, formats={"start": None, "end": None}, prefix='')
        log("flushed message!", flush=True)
        self.assertIn("flushed message!\n", s.getvalue())
        log.close()

    def test_blank_enter_and_exit_before_formatted_logging(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, formats={"start": None, "end": None, 'enter': None, 'exit': None}, prefix='')
        log.enter('subsystem')
        log.exit()
        with log.enter('subsystem 2'):
            with log.enter('subsystem 3'):
                log('finally!')
        log.close()
        self.assertEqual(s.getvalue(), 'finally!\n')


    def test_log_messages_after_close(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, formats={"start": None, "end": None}, prefix='')
        log("kooky!")
        log.close()
        log.box("nope")
        log.write("nope\n")
        with log.enter("nope"):
            log("nope")
        log.reset()
        log("wonderful!")
        value = s.getvalue()
        self.assertIn("kooky!\n", value)
        self.assertIn("wonderful!\n", value)
        self.assertNotIn("nope", value)

    def test_formats_exceptions(self):
        with self.assertRaises(ValueError):
            big.Log(formats={"mixmox": None})
        with self.assertRaises(TypeError):
            big.Log(formats={83: {"template": "abc", "line": "-"}})
        with self.assertRaises(TypeError):
            # formats value must be dict
            big.Log(formats={"splunk": 55})
        with self.assertRaises(ValueError):
            # format dict must contain template
            big.Log(formats={"splunk": {"zippy": "howdy doodles!"}})
        with self.assertRaises(TypeError):
            # format dict template value must be str
            big.Log(formats={"splunk": {"template": 33}})

        with self.assertRaises(ValueError):
            # format dict can't have message
            big.Log(formats={"splunk": {"template": "xyz", "message": "hello dere!"}})

        l = big.Log(formats={"start": None, "end": None})
        with self.assertRaises(ValueError):
            l.print("abc", format="spooky")
        l.close()

        # you're allowed to use format names that collide with Log methods,
        # as well as format names containing spaces.
        # you just won't get the prebound method (a la "box", "peanut", etc).
        s = io.StringIO()
        l = big.Log(s, formats={
            "start": None,
            "end": None,
            "reset": {"template": "_reset_{line*}\n{message}\n{line*}", "line*": "_"},
            "has two spaces": {"template": "#has two spaces#{line*}\n{message}\n{line*}", "line*": "#"}},
            width=20)
        l('dis is rasat', format='reset')
        l('has spacings', format='has two spaces')
        l.close()
        self.assertEqual(s.getvalue(), """
_reset______________
dis is rasat
____________________
#has two spaces#####
has spacings
####################
""".lstrip())



class TestLogLazyStartAndEnd(unittest.TestCase):

    def test_no_log_means_no_banners(self):
        s = io.StringIO()
        sink = EventSink()
        log = big.Log(s, sink, threading=False, formats={"start": {"template": "START"}, "end": {"template": "END"}}, prefix='[PREFIX] ', width=20)
        log.close()

        expected = ''
        self.assertEqual(s.getvalue(), expected)
        self.assertEqual(sink.value, "")


    def test_empty_log_means_no_banners(self):
        s = io.StringIO()
        sink = EventSink()
        log = big.Log(s, sink, threading=False, formats={"start": {"template": "START"}, "end": {"template": "END"}, "print": {"template": ''}}, prefix='', width=20)
        log('')
        log.close()

        expected = ''
        self.assertEqual(s.getvalue(), expected)
        self.assertEqual(sink.value, "")

    def test_lazy_start_from_log(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, formats={"start": {"template": "START"}, "end": {"template": "END"}}, prefix='[PREFIX] ', width=20)
        log("howdy!")
        log.close()

        expected = """
START
[PREFIX] howdy!
END
""".lstrip()
        self.assertEqual(s.getvalue(), expected)

    def test_lazy_start_from_write(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, formats={"start": {"template": "START"}, "end": {"template": "END"}}, prefix='[PREFIX] ', width=20)
        log.write("howdy!\n")
        log.close()

        expected = """
START
howdy!
END
""".lstrip()
        self.assertEqual(s.getvalue(), expected)

    def test_lazy_start_from_heading(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, formats={"start": {"template": "START"}, "end": {"template": "END"}}, prefix='[PREFIX] ', width=20)
        log.box("howdy!")
        log.close()

        expected = """
START
[PREFIX] +----------
[PREFIX] | howdy!
[PREFIX] +----------
END
""".lstrip()
        self.assertEqual(s.getvalue(), expected)

    def test_lazy_start_from_enter(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, formats={"start": {"template": "START"}, "end": {"template": "END"}}, prefix='[PREFIX] ', width=20)
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
        self.assertEqual(s.getvalue(), expected)


class TestLogContextManager(unittest.TestCase):
    """Tests for Log as a context manager."""

    def test_log_context_manager(self):
        array = []
        with big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='') as log:
            log("inside with block")
        # After exiting, flush should have been called
        self.assertTrue(any("inside with block" in s for s in array))


class TestLogThreading(unittest.TestCase):
    """Tests for Log with threading enabled."""

    def test_log_threaded(self):
        array = []
        log = big.Log(array, threading=True, formats={"start": None, "end": None}, prefix='')
        log("threaded message")
        log.write("threaded write")
        log.close()
        self.assertTrue(any("threaded message" in s for s in array))
        self.assertTrue(any("threaded write" in s for s in array))

    def test_log_threaded_multiple_messages(self):
        array = []
        log = big.Log(array, threading=True, formats={"start": None, "end": None}, prefix='')
        for i in range(10):
            log(f"message {i}")
        log.close()
        output = ''.join(array)
        for i in range(10):
            self.assertIn(f"message {i}", output)

    def test_log_threaded_enter_exit(self):
        array = []
        log = big.Log(array, threading=True, formats={"start": None, "end": None}, prefix='')
        with log.enter("threaded subsystem"):
            log("inside threaded")
        log.close()
        output = ''.join(array)
        self.assertIn("threaded subsystem", output)

    def test_log_threaded_reset(self):
        array = []
        log = big.Log(array, threading=True, formats={"start": None, "end": None}, prefix='')
        log("before")
        log.reset()
        log("after")
        log.flush()

        text = "\n".join(array)
        self.assertIn('before', text)
        self.assertIn('after', text)

    def test_log_threaded_reset_after_close(self):
        array = []
        log = big.Log(array, threading=True, formats={"start": None, "end": None}, prefix='')
        log("before")
        log.close()
        log("dropped")
        log.reset()
        log("after")
        log.flush()

        text = "\n".join(array)
        self.assertIn('before', text)
        self.assertIn('after', text)
        self.assertNotIn('dropped', text)

    def test_log_threaded_box(self):
        array = []
        log = big.Log(array, threading=True, formats={"start": None, "end": None}, prefix='')
        log.box("threaded heading")
        log.close()
        self.assertTrue(any("threaded heading" in s for s in array))

    def test_log_threaded_blocking_flush(self):
        array = []
        buffer = big.Log.Buffer(array)
        log = big.Log(buffer, threading=True, formats={"start": None, "end": None}, prefix='')
        log("message")
        text = "\n".join(array)
        self.assertNotIn('message', text)
        log.flush()
        text = "\n".join(array)
        self.assertIn('message', text)

    def test_log_threaded_asynchronous_flush(self):
        array = []
        buffer = big.Log.Buffer(array)
        log = big.Log(buffer, threading=True, formats={"start": None, "end": None}, prefix='')
        log("message")
        text = "\n".join(array)
        self.assertNotIn('message', text)
        log.flush(block=False)
        log.write("sentinel")
        # I hate doing it, but how else do you test an asynchronous method?!
        while not log._queue.empty():
            time.sleep(0.0000001)
        text = "\n".join(array)
        self.assertIn('message', text)

    def test_log_flush_closed_error(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        log.close()
        log.flush()


class TestLogFormatting(unittest.TestCase):
    """Tests for Log formatting options."""

    def test_log_with_prefix(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='[PREFIX] ')
        log("test")
        log.close()
        self.assertTrue(any("[PREFIX]" in s for s in array))

    def test_log_with_start_and_end(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": {"template": "START"}, "end": {"template": "END"}}, prefix='')
        log("middle")
        log.close()
        output = ''.join(array)
        self.assertIn("START", output)
        self.assertIn("END", output)

    def test_custom_format(self):
        s = io.StringIO()
        # peanut has multiple lines after the {message} lines
        # to exercise some specific code in Log
        log = big.Log(s,
            threading=False,
            formats={"start": None, "end": None, "peanut": {"template": "{prefix}{line*}\n{prefix}=peanut=start{line*}\n{prefix}== {message}\n{prefix}-- {message}\n{prefix}=peanut=end{line*}\n{prefix}{line*}", "line*": "=-"}},
            prefix='[PFX] ')
        log.peanut("test\ntest2\ntest3")
        log.close()
        self.assertEqual(s.getvalue(), 
"""
[PFX] =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
[PFX] =peanut=start=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
[PFX] == test
[PFX] -- test2
[PFX] -- test3
[PFX] =peanut=end=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
[PFX] =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
""".lstrip())

        # non-contiguous {message} lines
        with self.assertRaises(ValueError):
            big.Log(formats={"peanut": {"template": "foo\n{message}\nbar\n{message}"}})

    def test_empty_banner_template_suppresses_banners(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, formats={"start": {"template": ""}, "end": {"template": ""}}, prefix='[PREFIX] ', width=20)
        log("z")
        log.close()

        expected = '[PREFIX] z\n'
        self.assertEqual(s.getvalue(), expected)

    def test_empty_start_banner_template_end_still_works(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, formats={"start": {"template": ""}, "end": {"template": "END"}}, prefix='[PREFIX] ', width=20)
        log("z")
        log.close()

        expected = '[PREFIX] z\nEND\n'
        self.assertEqual(s.getvalue(), expected)


    def test_empty_end_banner_template(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, formats={"start": {"template": "START"}, "end": {"template": ""}}, prefix='[PREFIX] ', width=20)
        log("z")
        log.close()

        expected = 'START\n[PREFIX] z\n'
        self.assertEqual(s.getvalue(), expected)

    def test_system_formats_are_disallowed(self):
        log = big.Log(None, threading=False)

        with self.assertRaises(ValueError):
            log("w", format='start')
        with self.assertRaises(ValueError):
            log("x", format='end')
        with self.assertRaises(ValueError):
            log("y", format='enter')
        with self.assertRaises(ValueError):
            log("z", format='exit')
        log.close()



class TestSink(unittest.TestCase):
    """Tests for Sink."""

    def test_sink_basic(self):
        sink = big.Log.Sink()
        log = big.Log(sink, threading=False, formats={"start": None, "end": None}, prefix='')
        log("message1")
        log("message2")
        log.close()

        events = list(sink)
        self.assertEqual(len(events), 4)

        self.assertIsInstance(events.pop(0), log_module.SinkStartEvent)

        self.assertIsInstance(events.pop(), log_module.SinkEndEvent)

        for i, e in enumerate(events, 1):
            self.assertIsInstance(e, log_module.SinkLogEvent)
            self.assertEqual(e.depth, 0)
            self.assertGreaterEqual(e.duration, 0)
            self.assertGreater(e.elapsed, 0)
            self.assertIn('message', e.formatted)
            self.assertTrue(e.message.startswith('message'))
            self.assertTrue(e.message.endswith(str(i)))
            self.assertEqual(e.number, 1)
            self.assertEqual(e.thread, threading.current_thread())

        e = events[0]
        clone = e._calculate_duration(events[1])
        self.assertEqual(e, clone)
        self.assertNotEqual(e, events[1])
        self.assertLess(e, events[1])

        with self.assertRaises(TypeError):
            e < 3.1415

        sse = big.SinkStartEvent(0, 5, 10, {})
        self.assertEqual(repr(sse), "SinkStartEvent(number=0, ns=5, epoch=10, configuration={}, duration=0)")

    def test_sink_event_types(self):
        sink = big.Log.Sink()
        log = big.Log(sink, threading=False)
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
        self.assertIn('start', types)
        self.assertIn('end', types)
        self.assertIn('write', types)
        self.assertIn('log', types)
        self.assertIn('enter', types)
        self.assertIn('exit', types)

        # coverage stuff
        # exercise __hash__ on every sink event type
        events_map = dict.fromkeys(events, None)
        number = 1
        for e in events:
            with self.subTest(e=e):
                self.assertEqual(e.number, number)
                if isinstance(e, big.log.SinkEndEvent):
                    number += 1
                else:
                    self.assertGreaterEqual(e.duration, 0)


    def test_sink_events_without_any_logging(self):
        sink = big.Log.Sink()
        log = big.Log(sink, threading=False)
        log.close()
        log.reset()
        log.close()

        events = list(sink)
        self.assertEqual(len(events), 0)


    def test_sink_print(self):
        sink = big.Log.Sink()
        log = big.Log(sink, threading=False, formats={"start": None, "end": None}, prefix='')
        log("test event")
        log.close()

        output = []
        sink.print(print=output.append)
        self.assertTrue(len(output) > 0)

    def test_sink_print_default_print(self):
        sink = big.Log.Sink()
        log = big.Log(sink, threading=False, formats={"start": None, "end": None}, prefix='')
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
        self.assertTrue(len(captured) > 0)

    def test_sink_reset(self):
        sink = big.Log.Sink()
        log = big.Log(sink, threading=False, formats={"start": None, "end": None}, prefix='')
        log("before reset")
        log.close()

        self.assertTrue(len(list(sink)) > 0)

        log.reset()
        # After reset, sink should also be reset
        # (events cleared when re-registered)

    def test_sink_write(self):
        sink = big.Log.Sink()
        log = big.Log(sink, threading=False, formats={"start": None, "end": None}, prefix='')
        s = "raw write\n"
        log.write(s)
        log.close()
        events = list(sink)
        self.assertEqual(len(events), 3)
        self.assertEqual(s, events[1].formatted)

    def test_sink_with_banners(self):
        sink = big.Log.Sink()
        log = big.Log(sink, threading=False, name='Sink', formats={"start": {"template": "{name} START"}, "end": {"template": "{name} END"}}, prefix='[PREFIX] ')
        log("message")
        log.close()

        events = list(sink)
        self.assertEqual(len(events), 5)

        SinkEvent = log_module.SinkEvent
        self.assertIsInstance(events[0], big.SinkStartEvent)
        self.assertEqual(events[0].elapsed, 0)
        self.assertGreater(events[0].ns, 0)
        self.assertGreater(events[0].epoch, 0)

        self.assertIsInstance(events[1], big.SinkLogEvent)
        self.assertEqual(events[1].formatted, 'Sink START\n')

        self.assertIsInstance(events[2], big.SinkLogEvent)
        self.assertEqual(events[2].message, 'message')

        self.assertIsInstance(events[3], big.SinkLogEvent)
        self.assertEqual(events[3].formatted, 'Sink END\n')

        self.assertIsInstance(events[4], big.SinkEndEvent)
        self.assertGreater(events[4].elapsed, 0)




class TestEventSink(unittest.TestCase):
    """Tests for our custom EventSink."""

    def test_sink_events_without_any_logging(self):
        esink = EventSink()
        log = big.Log(esink, threading=False)
        log.close()
        log.reset()
        log.close()

        self.assertEqual(esink.value, "")

    def test_sink_events(self):
        esink = EventSink()
        log = big.Log(esink, threading=False)
        log.write("abc")
        log("xyz")
        with log.enter("subsystem"):
            log.box("xyz")
        log.close()
        log.reset()
        log.print('hey now')
        log.close()

        self.assertEqual(esink.value, "start log write log log enter log exit log log flush end reset start log log log flush end")



class TestOldDestination(unittest.TestCase):
    """Tests for OldDestination."""

    def test_old_destination_basic(self):
        old = big.OldDestination()
        log = big.Log(old, threading=False, formats={"start": None, "end": None}, prefix='')
        log("smedley")
        log.close()

        events = list(old)
        self.assertEqual(len(events), 2)
        e = events[0]
        self.assertEqual(e[0], 0)
        self.assertEqual(e[2], 'log start')
        self.assertEqual(e[3], 0)
        e = events[1]
        self.assertGreater(e[0], 0)
        self.assertEqual(e[2], 'smedley')
        self.assertEqual(e[3], 0)

    def test_old_destination_enter_exit(self):
        old = big.OldDestination()
        log = big.Log(old, threading=False, formats={"start": None, "end": None}, prefix='')
        log.enter("subsystem")
        log("inside")
        log.exit()
        log.close()

        events = list(old)
        event_strs = [e[2] for e in events]
        self.assertIn("subsystem start", event_strs)
        self.assertIn("subsystem end", event_strs)

    def test_old_destination_print(self):
        old = big.OldDestination()
        log = big.Log(old, threading=False, formats={"start": None, "end": None}, prefix='')
        log("test")
        log.close()

        output = []
        old.print(print=output.append)
        self.assertTrue(len(output) > 0)

    def test_old_destination_print_no_title(self):
        old = big.OldDestination()
        log = big.Log(old, threading=False, formats={"start": None, "end": None}, prefix='')
        log("test")
        log.close()

        output = []
        old.print(print=output.append, title=None)
        # First line should not be "[event log]"
        self.assertFalse(output[0].startswith("[event log]"))

    def test_old_destination_print_no_headings(self):
        old = big.OldDestination()
        log = big.Log(old, threading=False, formats={"start": None, "end": None}, prefix='')
        log("test")
        log.close()

        output = []
        old.print(print=output.append, headings=False)

    def test_old_destination_write(self):
        old = big.OldDestination()
        log = big.Log(old, threading=False, formats={"start": None, "end": None}, prefix='')
        log.write("raw write content\n")
        log.close()

        events = list(old)
        event_strs = [e[2] for e in events]
        self.assertIn("raw write content", event_strs)


class TestOldLog(unittest.TestCase):
    """Tests for OldLog backwards compatibility class."""

    maxDiff = None

    def test_smoke_test_log(self):
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

        self.assertEqual(expected, got)

    def test_default_settings(self):
        log = big.OldLog()
        log('event 1')
        buffer = []
        real_print = builtins.print
        builtins.print = buffer.append
        log.print()
        builtins.print = real_print
        got = "\n".join(buffer)
        self.assertIn("event 1", got)

    def test_old_log_iter(self):
        log = big.OldLog()
        log("test event")
        events = list(log)
        self.assertTrue(len(events) >= 2)  # log start + test event

    def test_old_log_reset(self):
        log = big.OldLog()
        log("before")
        log.reset()
        log("after")
        events = list(log)
        event_strs = [e[2] for e in events]
        self.assertIn("after", event_strs)


class TestLogWithTextIOBase(unittest.TestCase):
    """Tests for Log with TextIOBase objects."""

    def test_log_with_stringio(self):
        buffer = io.StringIO()
        log = big.Log(buffer, threading=False, formats={"start": None, "end": None}, prefix='')
        log("stringio test")
        log.close()
        content = buffer.getvalue()
        self.assertIn("stringio test", content)


class TestLogWithPath(unittest.TestCase):
    """Tests for Log with Path objects."""

    def test_log_with_path_object(self):
        from pathlib import Path
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            path = Path(f.name)

        try:
            log = big.Log(path, threading=False, formats={"start": None, "end": None}, prefix='')
            log("path object test")
            log.close()

            with open(path, 'r') as f:
                content = f.read()
            self.assertIn("path object test", content)
        finally:
            os.unlink(path)


class TestLogWithCustomClock(unittest.TestCase):
    """Tests for Log with custom clock."""

    def test_custom_clock(self):
        clock = FakeClock()
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='[{elapsed}] ', clock=clock)

        clock.advance(1_000_000_000)  # 1 second
        log("at 1 second")
        log.close()

        output = ''.join(array)
        self.assertIn("1", output)


class TestExport(unittest.TestCase):
    """Test that all expected symbols are exported."""

    def test_all_exports(self):
        expected = [
            'Log', 'OldDestination', 'OldLog'
        ]
        for name in expected:
            self.assertIn(name, log_module.__all__)


def run_tests():
    bigtestlib.run(name="big.log", module=__name__)


if __name__ == "__main__":  # pragma: no cover
    run_tests()
    bigtestlib.finish()
