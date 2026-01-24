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
import os
import tempfile
import threading
import unittest


class FakeClock:
    def __init__(self):
        self.time = 0

    def __call__(self):
        return self.time

    def advance(self, ns=12_000_000):
        self.time += ns


class TestDestination(unittest.TestCase):
    """Tests for the base Destination class."""

    def test_destination_init(self):
        destination = big.Destination()
        self.assertIsNone(destination.owner)

    def test_destination_register(self):
        destination = big.Destination()
        destination.owner = None  # Reset to allow re-registration
        destination.register("test_owner")
        self.assertEqual(destination.owner, "test_owner")

    def test_destination_register_already_registered(self):
        destination = big.Destination()
        destination.owner = None
        destination.register("owner1")
        with self.assertRaises(RuntimeError) as cm:
            destination.register("owner2")
        self.assertIn("already registered", str(cm.exception))

    def test_destination_virtual_write(self):
        destination = big.Destination()
        with self.assertRaises(RuntimeError):
            destination.write(0, None, "test")

    def test_destination_flush_does_nothing(self):
        destination = big.Destination()
        destination.flush()  # Should not raise

    def test_destination_close_does_nothing(self):
        destination = big.Destination()
        destination.close()  # Should not raise

    def test_destination_reset(self):
        destination = big.Destination()
        destination.reset()


class TestCallable(unittest.TestCase):
    """Tests for the Callable destination."""

    def test_callable_write(self):
        results = []
        c = big.Callable(results.append)
        c.write(0, None, "test string")
        self.assertEqual(results, ["test string"])


class TestPrint(unittest.TestCase):
    """Tests for the Print destination."""

    def test_print_write(self):
        captured = []
        original_print = builtins.print
        builtins.print = lambda *args, **kwargs: captured.append((args, kwargs))
        try:
            printer = big.Print()
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
        list_destination = big.List(array)
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
            buffer = big.Buffer()
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
        buffer = big.Buffer()
        buffer.flush()  # Should not raise or print


class TestFile(unittest.TestCase):
    """Tests for the File destination."""

    def test_file_buffered_mode(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            path = f.name

        try:
            file_destination = big.File(path, mode='wt')
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
            file_destination.close()
        finally:
            os.unlink(path)

    def test_file_immediate_mode(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            path = f.name

        try:
            file_destination = big.File(path, mode='wt', flush=True)
            file_destination.write(0, None, "immediate\n")

            # File should have content immediately
            with open(path, 'r') as f:
                content = f.read()
            self.assertEqual(content, "immediate\n")

            file_destination.close()
        finally:
            os.unlink(path)

    def test_file_append_mode(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            path = f.name
            f.write("existing\n")

        try:
            file_destination = big.File(path, mode='at')
            file_destination.write(0, None, "appended\n")
            file_destination.flush()

            with open(path, 'r') as f:
                content = f.read()
            self.assertEqual(content, "existing\nappended\n")
        finally:
            os.unlink(path)

    def test_tmpfile(self):
        def fake_clock():
            return 1769224889.123456

        expected = f"LogName.2026-01-23.19-21-29.123456.PST.{os.getpid()}.txt"

        log = big.Log(big.log.tmpfile, name="LogName", threading=False, header='', footer='', prefix='', timestamp_clock=fake_clock)
        self.assertEqual(log.tmpfile.name, expected)

        destination = log._destinations[0][0]
        self.assertIsInstance(destination, big.log.File)
        self.assertEqual(destination.path, log.tmpfile)





class TestFileHandle(unittest.TestCase):
    """Tests for the FileHandle destination."""

    def test_invalid_filehandle(self):
        with self.assertRaises(TypeError):
            big.FileHandle(None)

    def test_filehandle_write(self):
        buffer = io.StringIO()
        fh_destination = big.FileHandle(buffer)
        fh_destination.write(0, None, "test content")
        self.assertEqual(buffer.getvalue(), "test content")

    def test_filehandle_write_with_flush(self):
        buffer = io.StringIO()
        fh_destination = big.FileHandle(buffer, flush=True)
        fh_destination.write(0, None, "test content")
        self.assertEqual(buffer.getvalue(), "test content")

    def test_filehandle_flush(self):
        buffer = io.StringIO()
        fh_destination = big.FileHandle(buffer)
        fh_destination.flush()  # Should not raise


class TestLogBasics(unittest.TestCase):
    """Basic tests for the Log class."""

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
        log = big.Log(array, threading=False, header='', footer='', prefix='')
        log("hello")
        log.close()
        self.assertTrue(any("hello" in s for s in array))

    def test_log_with_path_string(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            path = f.name

        try:
            log = big.Log(path, threading=False, header='', footer='', prefix='')
            log("test message")
            log.close()

            with open(path, 'r') as f:
                content = f.read()
            self.assertIn("test message", content)
        finally:
            os.unlink(path)

    def test_log_with_callable(self):
        results = []
        log = big.Log(results.append, threading=False, header='', footer='', prefix='')
        log("callable test")
        log.close()
        self.assertTrue(any("callable test" in s for s in results))

    def test_log_with_none_destination(self):
        # None destinations should be skipped
        array = []
        log = big.Log(None, array, None, threading=False, header='', footer='', prefix='')
        log("test")
        log.close()
        self.assertTrue(len(array) > 0)

    def test_log_with_invalid_destination(self):
        with self.assertRaises(ValueError) as cm:
            log = big.Log(12345, threading=False)
        self.assertIn("don't know how to use destination", str(cm.exception))

    def test_log_after_closed(self):
        array = []
        log = big.Log(array, threading=False, header='', footer='', prefix='')
        log.close()
        log("after close")

    def test_log_write_after_closed(self):
        array = []
        log = big.Log(array, threading=False, header='', footer='', prefix='')
        log.close()
        log.write("after close")

    def test_log_heading_after_closed(self):
        array = []
        log = big.Log(array, threading=False, header='', footer='', prefix='')
        log.close()
        log.heading("after close")

    def test_log_close_is_idempotent(self):
        array = []
        log = big.Log(array, threading=False, header='', footer='', prefix='')
        self.assertFalse(log.closed)
        log.close()
        self.assertTrue(log.closed)
        log.close()
        self.assertTrue(log.closed)

    def test_log_atexit(self):
        # simulate atexit calls
        log = big.Log([], threading=False)
        self.assertFalse(log.closed)
        log._atexit()
        self.assertTrue(log.closed)

        log = big.Log([], threading=True)
        self.assertFalse(log.closed)
        log._atexit()
        self.assertTrue(log.closed)


class TestLogMethods(unittest.TestCase):
    """Tests for Log methods."""

    def test_log_method(self):
        array = []
        log = big.Log(array, threading=False, header='', footer='', prefix='')
        log.log("via log method")
        log.close()
        self.assertTrue(any("via log method" in s for s in array))

    def test_log_write(self):
        array = []
        log = big.Log(array, threading=False, header='', footer='', prefix='')
        log.write("raw write\n")
        log.close()
        self.assertTrue(any("raw write" in s for s in array))

    def test_log_write_not_string(self):
        array = []
        log = big.Log(array, threading=False, header='', footer='', prefix='')
        with self.assertRaises(TypeError):
            log.write(12345)
        log.close()

    def test_log_heading(self):
        array = []
        log = big.Log(array, threading=False, header='', footer='', prefix='')
        log.heading("My Heading")
        log.close()
        self.assertTrue(any("My Heading" in s for s in array))

    def test_log_heading_not_string(self):
        array = []
        log = big.Log(array, threading=False, header='', footer='', prefix='')
        with self.assertRaises(TypeError):
            log.heading(12345)
        log.close()

    def test_log_heading_custom_separator(self):
        array = []
        log = big.Log(array, threading=False, header='', footer='', prefix='')
        log.heading("Custom", separator='*-')
        log.close()
        self.assertTrue(any("*-*-*" in s for s in array))

    def test_log_enter_exit(self):
        array = []
        log = big.Log(array, threading=False, header='', footer='', prefix='')
        log.enter("subsystem")
        log("inside")
        log.exit()
        log.close()
        output = ''.join(array)
        self.assertIn("subsystem", output)
        self.assertIn("inside", output)

    def test_log_enter_context_manager(self):
        array = []
        log = big.Log(array, threading=False, header='', footer='', prefix='')
        with log.enter("subsystem"):
            log("inside context")
        log.close()
        output = ''.join(array)
        self.assertIn("subsystem", output)
        self.assertIn("inside context", output)

    def test_log_unbalanced_exit(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, header='', footer='', prefix='')
        log.enter("entered!")
        log.exit()
        log.exit()
        log.exit()
        log.close()
        self.assertIn("entered!\n", s.getvalue())

    def test_reuse_log(self):
        array = []
        log = big.Log(array, threading=False, header='', footer='', prefix='')
        log.write("before reset")
        log.close()
        log.reset()
        log.write("after reset")
        log.close()
        self.assertIn("before reset", array)
        self.assertIn("after reset", array)

    def test_log_sep_end_params(self):
        array = []
        log = big.Log(array, threading=False, header='', footer='', prefix='')
        log("a", "b", "c", sep="-", end="!\n")
        log.close()
        self.assertTrue(any("a-b-c!" in s for s in array))

    def test_log_with_flush_param(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, header='', footer='', prefix='')
        log("flushed message!", flush=True)
        self.assertIn("flushed message!\n", s.getvalue())
        log.close()

    def test_log_messages_after_close(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, header='', footer='', prefix='')
        log("kooky!")
        log.close()
        log.heading("nope")
        log.write("nope\n")
        with log.enter("nope"):
            log("nope")
        log.reset()
        log("wonderful!")
        value = s.getvalue()
        self.assertIn("kooky!\n", value)
        self.assertIn("wonderful!\n", value)
        self.assertNotIn("nope", value)

class TestLogLazyHeaderAndFooter(unittest.TestCase):

    def test_lazy_header_from_log(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, header='HEADER', footer='FOOTER', prefix='[PREFIX] ', width=20)
        log("howdy!")
        log.close()

        expected = """
[PREFIX] ===========
[PREFIX] HEADER
[PREFIX] ===========
[PREFIX] howdy!
[PREFIX] ===========
[PREFIX] FOOTER
[PREFIX] ===========
        """.strip()
        assert s.getvalue().strip() == expected

    def test_lazy_header_from_write(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, header='HEADER', footer='FOOTER', prefix='[PREFIX] ', width=20)
        log.write("howdy!\n")
        log.close()

        expected = """
[PREFIX] ===========
[PREFIX] HEADER
[PREFIX] ===========
howdy!
[PREFIX] ===========
[PREFIX] FOOTER
[PREFIX] ===========
        """.strip()
        assert s.getvalue().strip() == expected

    def test_lazy_header_from_heading(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, header='HEADER', footer='FOOTER', prefix='[PREFIX] ', width=20)
        log.heading("howdy!")
        log.close()

        expected = """
[PREFIX] ===========
[PREFIX] HEADER
[PREFIX] ===========
[PREFIX] -----------
[PREFIX] howdy!
[PREFIX] -----------
[PREFIX] ===========
[PREFIX] FOOTER
[PREFIX] ===========
        """.strip()
        assert s.getvalue().strip() == expected

    def test_lazy_header_from_enter(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, header='HEADER', footer='FOOTER', prefix='[PREFIX] ', width=20)
        with log.enter("howdy!"):
            log("woah!")
        log.close()

        expected = """
[PREFIX] ===========
[PREFIX] HEADER
[PREFIX] ===========
[PREFIX] -----------
[PREFIX] howdy!
[PREFIX] -----------
[PREFIX]     woah!
[PREFIX] -----------
[PREFIX] ===========
[PREFIX] FOOTER
[PREFIX] ===========
        """.strip()
        assert s.getvalue().strip() == expected


class TestLogContextManager(unittest.TestCase):
    """Tests for Log as a context manager."""

    def test_log_context_manager(self):
        array = []
        with big.Log(array, threading=False, header='', footer='', prefix='') as log:
            log("inside with block")
        # After exiting, flush should have been called
        self.assertTrue(any("inside with block" in s for s in array))


class TestLogThreading(unittest.TestCase):
    """Tests for Log with threading enabled."""

    def test_log_threaded(self):
        array = []
        log = big.Log(array, threading=True, header='', footer='', prefix='')
        log("threaded message")
        log.write("threaded write")
        log.close()
        self.assertTrue(any("threaded message" in s for s in array))
        self.assertTrue(any("threaded write" in s for s in array))

    def test_log_threaded_multiple_messages(self):
        array = []
        log = big.Log(array, threading=True, header='', footer='', prefix='')
        for i in range(10):
            log(f"message {i}")
        log.close()
        output = ''.join(array)
        for i in range(10):
            self.assertIn(f"message {i}", output)

    def test_log_threaded_enter_exit(self):
        array = []
        log = big.Log(array, threading=True, header='', footer='', prefix='')
        with log.enter("threaded subsystem"):
            log("inside threaded")
        log.close()
        output = ''.join(array)
        self.assertIn("threaded subsystem", output)

    def test_log_threaded_reset(self):
        array = []
        log = big.Log(array, threading=True, header='', footer='', prefix='')
        log("before")
        log.reset()
        log("after")
        log.close()

    def test_log_threaded_reset_after_close(self):
        array = []
        log = big.Log(array, threading=True, header='', footer='', prefix='')
        log("before")
        log.close()
        log.reset()
        log("after")
        log.close()

    def test_log_threaded_heading(self):
        array = []
        log = big.Log(array, threading=True, header='', footer='', prefix='')
        log.heading("threaded heading")
        log.close()
        self.assertTrue(any("threaded heading" in s for s in array))

    def test_log_threaded_flush(self):
        array = []
        log = big.Log(array, threading=True, header='', footer='', prefix='')
        log("message")
        log.flush()
        log.close()

    def test_log_exit_closed_error(self):
        array = []
        log = big.Log(array, threading=False, header='', footer='', prefix='')
        log.close()
        log.exit()

    def test_log_flush_closed_error(self):
        array = []
        log = big.Log(array, threading=False, header='', footer='', prefix='')
        log.close()
        log.flush()


class TestLogNestedLogs(unittest.TestCase):
    """Tests for nested Log objects."""

    def test_nested_logs(self):
        array1 = []
        array2 = []
        inner_log = big.Log(array2, threading=False, header='', footer='', prefix='')
        outer_log = big.Log(array1, inner_log, threading=False, header='', footer='', prefix='')
        outer_log("message")
        outer_log.close()
        # Message should appear in both
        self.assertTrue(any("message" in s for s in array1))
        self.assertTrue(any("message" in s for s in array2))

    def test_nested_logs_write(self):
        array1 = []
        array2 = []
        inner_log = big.Log(array2, threading=False, header='', footer='', prefix='')
        outer_log = big.Log(array1, inner_log, threading=False, header='', footer='', prefix='')
        outer_log.write("raw write\n")
        outer_log.close()
        self.assertTrue(any("raw write" in s for s in array2))

    def test_nested_logs_heading(self):
        array1 = []
        array2 = []
        inner_log = big.Log(array2, threading=False, header='', footer='', prefix='')
        outer_log = big.Log(array1, inner_log, threading=False, header='', footer='', prefix='')
        outer_log.heading("nested heading")
        outer_log.close()
        self.assertTrue(any("nested heading" in s for s in array2))

    def test_nested_logs_enter_exit(self):
        array1 = []
        array2 = []
        inner_log = big.Log(array2, threading=False, header='', footer='', prefix='')
        outer_log = big.Log(array1, inner_log, threading=False, header='', footer='', prefix='')
        outer_log.enter("nested subsystem")
        outer_log("inside nested")
        outer_log.exit()
        outer_log.close()
        self.assertTrue(any("nested subsystem" in s for s in array2))
        self.assertIn("inside nested\n", array2)

    def test_nested_logs_flush(self):
        array1 = []
        array2 = []
        inner_log = big.Log(array2, threading=False, header='', footer='', prefix='')
        outer_log = big.Log(array1, inner_log, threading=False, header='', footer='', prefix='')
        outer_log("before flush")
        outer_log.flush()
        outer_log.close()
        self.assertIn("before flush\n", array1)
        self.assertIn("before flush\n", array2)

    def test_nested_logs_reset(self):
        array1 = []
        array2 = []
        inner_log = big.Log(array2, threading=False, header='', footer='', prefix='')
        outer_log = big.Log(array1, inner_log, threading=False, header='', footer='', prefix='')
        outer_log("before reset")
        outer_log.close()
        outer_log.reset()
        outer_log("after reset")
        outer_log.close()
        self.assertIn("before reset\n", array1)
        self.assertIn("before reset\n", array2)
        self.assertIn("after reset\n", array1)
        self.assertIn("after reset\n", array2)

    def test_nested_logs_with_banners_and_prefix(self):
        array1 = []
        array2 = []
        inner_log = big.Log(array2, threading=False, prefix='[prefix] ')
        outer_log = big.Log(array1, inner_log, threading=False, prefix='[PREFIX] ')
        outer_log("message")
        outer_log.close()
        self.assertIn("[PREFIX] message\n", array1)
        self.assertIn("[prefix] message\n", array2)


class TestLogFormatting(unittest.TestCase):
    """Tests for Log formatting options."""

    def test_log_with_prefix(self):
        array = []
        log = big.Log(array, threading=False, header='', footer='', prefix='[PREFIX] ')
        log("test")
        log.close()
        self.assertTrue(any("[PREFIX]" in s for s in array))

    def test_log_with_initial_and_final(self):
        array = []
        log = big.Log(array, threading=False, header='START', footer='FINISH', prefix='')
        log("middle")
        log.close()
        output = ''.join(array)
        self.assertIn("START", output)
        self.assertIn("FINISH", output)

    def test_log_no_start_final_or_prefix(self):
        array = []
        log = big.Log(array, threading=False, header='', footer='', prefix='')
        log("test")
        log.close()

    def test_log_empty_separator(self):
        array = []
        log = big.Log(array, threading=False, header='', footer='', prefix='', separator='')
        log.enter("sub")
        log("test")
        log.exit()
        log.close()


class TestSink(unittest.TestCase):
    """Tests for Sink."""

    def test_sink_basic(self):
        sink = big.Sink()
        log = big.Log(sink, threading=False, header='', footer='', prefix='')
        log("message1")
        log("message2")
        log.close()

        events = list(sink)
        self.assertEqual(len(events), 2)
        for i, e in enumerate(events, 1):
            type, thread, elapsed, duration, depth, message = e
            self.assertGreater(elapsed, 0)
            self.assertGreaterEqual(duration, 0)
            self.assertEqual(thread, threading.current_thread())
            self.assertEqual(depth, 0)
            self.assertEqual(type, big.log.Sink.LOG)
            self.assertTrue(message.startswith('message'))
            self.assertTrue(message.endswith(str(i)))

    def test_sink_event_types(self):
        sink = big.Sink()
        log = big.Log(sink, threading=False)
        log("regular event")
        log.write("write event")
        log.heading("heading event")
        log.enter("enter event")
        log.exit()
        log.close()

        events = list(sink)
        types = [e[0] for e in events]
        self.assertIn(big.Sink.WRITE, types)
        self.assertIn(big.Sink.LOG, types)
        self.assertIn(big.Sink.HEADER, types)
        self.assertIn(big.Sink.FOOTER, types)
        self.assertIn(big.Sink.HEADING, types)
        self.assertIn(big.Sink.ENTER, types)
        self.assertIn(big.Sink.EXIT, types)

    def test_sink_print(self):
        sink = big.Sink()
        log = big.Log(sink, threading=False, header='', footer='', prefix='')
        log("test event")
        log.close()

        output = []
        sink.print(print=output.append)
        self.assertTrue(len(output) > 0)

    def test_sink_print_with_formats(self):
        sink = big.Sink()
        log = big.Log(sink, threading=False, header='', footer='', prefix='')
        log("test")
        log.heading("heading")
        log.enter("sub")
        log.exit()
        log.close()

        output = []
        sink.print(
            print=output.append,
            format='{message}',
            heading='=={message}==',
            enter='>>{message}',
            exit='<<exit'
        )
        self.assertTrue(len(output) > 0)

    def test_sink_print_no_separator(self):
        sink = big.Sink()
        log = big.Log(sink, threading=False, header='', footer='', prefix='')
        log("test event")
        log.close()

        output = []
        sink.print(print=output.append, separator='')
        self.assertTrue(len(output) > 0)

    def test_sink_print_default_print(self):
        sink = big.Sink()
        log = big.Log(sink, threading=False, header='', footer='', prefix='')
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
        sink = big.Sink()
        log = big.Log(sink, threading=False, header='', footer='', prefix='')
        log("before reset")
        log.close()

        self.assertTrue(len(list(sink)) > 0)

        log.reset()
        # After reset, sink should also be reset
        # (events cleared when re-registered)

    def test_sink_write(self):
        sink = big.Sink()
        log = big.Log(sink, threading=False, header='', footer='', prefix='')
        s = "raw write\n"
        log.write(s)
        log.close()
        events = list(sink)
        self.assertEqual(len(events), 1)
        self.assertIn(s, events[0])

    def test_sink_with_banners(self):
        sink = big.Sink()
        log = big.Log(sink, threading=False, name='Sink', header='{name} start', footer='{name} finish', prefix='[PREFIX] ')
        log("message")
        log.close()
        events = list(sink)
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0][0], big.log.Sink.HEADER)
        self.assertEqual(events[0][-1], 'Sink start')
        self.assertEqual(events[1][0], big.log.Sink.LOG)
        self.assertEqual(events[1][-1], 'message')
        self.assertEqual(events[2][0], big.log.Sink.FOOTER)
        self.assertEqual(events[2][-1], 'Sink finish')


class TestOldDestination(unittest.TestCase):
    """Tests for OldDestination."""

    def test_old_destination_basic(self):
        old = big.OldDestination()
        log = big.Log(old, threading=False, header='', footer='', prefix='')
        log("event")
        log.close()

        events = list(old)
        # Should have "log start" and "event"
        self.assertTrue(len(events) >= 2)

    def test_old_destination_enter_exit(self):
        old = big.OldDestination()
        log = big.Log(old, threading=False, header='', footer='', prefix='')
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
        log = big.Log(old, threading=False, header='', footer='', prefix='')
        log("test")
        log.close()

        output = []
        old.print(print=output.append)
        self.assertTrue(len(output) > 0)

    def test_old_destination_print_no_title(self):
        old = big.OldDestination()
        log = big.Log(old, threading=False, header='', footer='', prefix='')
        log("test")
        log.close()

        output = []
        old.print(print=output.append, title=None)
        # First line should not be "[event log]"
        self.assertFalse(output[0].startswith("[event log]"))

    def test_old_destination_print_no_headings(self):
        old = big.OldDestination()
        log = big.Log(old, threading=False, header='', footer='', prefix='')
        log("test")
        log.close()

        output = []
        old.print(print=output.append, headings=False)

    def test_old_destination_write(self):
        old = big.OldDestination()
        log = big.Log(old, threading=False, header='', footer='', prefix='')
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
        log = big.Log(buffer, threading=False, header='', footer='', prefix='')
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
            log = big.Log(path, threading=False, header='', footer='', prefix='')
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
        log = big.Log(array, threading=False, header='', footer='', prefix='[{elapsed}] ', clock=clock)

        clock.advance(1_000_000_000)  # 1 second
        log("at 1 second")
        log.close()

        output = ''.join(array)
        self.assertIn("1", output)


class TestExport(unittest.TestCase):
    """Test that all expected symbols are exported."""

    def test_all_exports(self):
        expected = [
            'Destination', 'Callable', 'Print', 'List', 'Buffer', 'File', 'FileHandle',
            'Log', 'Sink', 'OldDestination', 'OldLog'
        ]
        for name in expected:
            self.assertIn(name, log_module.__all__)


def run_tests():
    bigtestlib.run(name="big.log", module=__name__)


if __name__ == "__main__":  # pragma: no cover
    run_tests()
    bigtestlib.finish()
