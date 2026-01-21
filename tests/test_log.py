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


class TestLogger(unittest.TestCase):
    """Tests for the base Logger class."""

    def test_logger_init(self):
        logger = big.Logger()
        self.assertIsNone(logger.owner)
        self.assertEqual(logger.start, 0)

    def test_logger_register(self):
        logger = big.Logger()
        logger.owner = None  # Reset to allow re-registration
        logger.register(100, None, "test_owner")
        self.assertEqual(logger.owner, "test_owner")
        self.assertEqual(logger.start, 100)

    def test_logger_register_already_registered(self):
        logger = big.Logger()
        logger.owner = None
        logger.register(100, None, "owner1")
        with self.assertRaises(RuntimeError) as cm:
            logger.register(200, None, "owner2")
        self.assertIn("already registered", str(cm.exception))

    def test_logger_virtual_write(self):
        logger = big.Logger()
        with self.assertRaises(RuntimeError):
            logger.write(0, None, "test")

    def test_logger_flush_does_nothing(self):
        logger = big.Logger()
        logger.flush(0, None)  # Should not raise

    def test_logger_close_does_nothing(self):
        logger = big.Logger()
        logger.close(0, None)  # Should not raise

    def test_logger_reset(self):
        logger = big.Logger()
        logger.reset(500, None)
        self.assertEqual(logger.start, 500)


class TestCallable(unittest.TestCase):
    """Tests for the Callable logger."""

    def test_callable_write(self):
        results = []
        c = big.Callable(results.append)
        c.write(0, None, "test string")
        self.assertEqual(results, ["test string"])


class TestPrint(unittest.TestCase):
    """Tests for the Print logger."""

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
    """Tests for the List logger."""

    def test_list_write(self):
        array = []
        list_logger = big.List(array)
        list_logger.write(0, None, "line1\n")
        list_logger.write(0, None, "line2\n")
        self.assertEqual(array, ["line1\n", "line2\n"])


class TestBuffer(unittest.TestCase):
    """Tests for the Buffer logger."""

    def test_buffer_write_and_flush(self):
        captured = []
        original_print = builtins.print
        builtins.print = lambda *args, **kwargs: captured.append((args, kwargs))
        try:
            buffer = big.Buffer()
            buffer.write(0, None, "hello ")
            buffer.write(0, None, "world")
            self.assertEqual(buffer.array, ["hello ", "world"])
            buffer.flush(0, None)
            self.assertEqual(buffer.array, [])
        finally:
            builtins.print = original_print
        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0][0], ("hello world",))

    def test_buffer_flush_empty(self):
        buffer = big.Buffer()
        buffer.flush(0, None)  # Should not raise or print


class TestFile(unittest.TestCase):
    """Tests for the File logger."""

    def test_file_buffered_mode(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            path = f.name

        try:
            file_logger = big.File(path, mode='wt')
            file_logger.write(0, None, "line1\n")
            file_logger.write(0, None, "line2\n")
            self.assertEqual(file_logger.array, ["line1\n", "line2\n"])

            # File should be empty before flush
            with open(path, 'r') as f:
                self.assertEqual(f.read(), "")

            file_logger.flush(0, None)
            self.assertEqual(file_logger.array, [])

            with open(path, 'r') as f:
                content = f.read()
            self.assertEqual(content, "line1\nline2\n")

            # Close should work when array is empty
            file_logger.close(0, None)
        finally:
            os.unlink(path)

    def test_file_immediate_mode(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            path = f.name

        try:
            file_logger = big.File(path, mode='wt', flush=True)
            file_logger.write(0, None, "immediate\n")

            # File should have content immediately
            with open(path, 'r') as f:
                content = f.read()
            self.assertEqual(content, "immediate\n")

            file_logger.close(0, None)
        finally:
            os.unlink(path)

    def test_file_append_mode(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            path = f.name
            f.write("existing\n")

        try:
            file_logger = big.File(path, mode='at')
            file_logger.write(0, None, "appended\n")
            file_logger.flush(0, None)

            with open(path, 'r') as f:
                content = f.read()
            self.assertEqual(content, "existing\nappended\n")
        finally:
            os.unlink(path)


class TestFileHandle(unittest.TestCase):
    """Tests for the FileHandle logger."""

    def test_filehandle_write(self):
        buffer = io.StringIO()
        fh_logger = big.FileHandle(buffer)
        fh_logger.write(0, None, "test content")
        self.assertEqual(buffer.getvalue(), "test content")

    def test_filehandle_write_with_flush(self):
        buffer = io.StringIO()
        fh_logger = big.FileHandle(buffer, flush=True)
        fh_logger.write(0, None, "test content")
        self.assertEqual(buffer.getvalue(), "test content")

    def test_filehandle_flush(self):
        buffer = io.StringIO()
        fh_logger = big.FileHandle(buffer)
        fh_logger.flush(0, None)  # Should not raise

    def test_filehandle_close(self):
        buffer = io.StringIO()
        fh_logger = big.FileHandle(buffer)
        self.assertIsNotNone(fh_logger.handle)
        fh_logger.close(0, None)
        self.assertIsNone(fh_logger.handle)


class TestLogBasics(unittest.TestCase):
    """Basic tests for the Log class."""

    def test_log_default_logger(self):
        # With no loggers specified, should use print
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
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        log("hello")
        log.close()
        self.assertTrue(any("hello" in s for s in array))

    def test_log_with_path_string(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            path = f.name

        try:
            log = big.Log(path, threading=False, initial='', final='', prefix='')
            log("test message")
            log.close()

            with open(path, 'r') as f:
                content = f.read()
            self.assertIn("test message", content)
        finally:
            os.unlink(path)

    def test_log_with_callable(self):
        results = []
        log = big.Log(results.append, threading=False, initial='', final='', prefix='')
        log("callable test")
        log.close()
        self.assertTrue(any("callable test" in s for s in results))

    def test_log_with_none_logger(self):
        # None loggers should be skipped
        array = []
        log = big.Log(None, array, None, threading=False, initial='', final='', prefix='')
        log("test")
        log.close()
        self.assertTrue(len(array) > 0)

    def test_log_with_invalid_logger(self):
        with self.assertRaises(ValueError) as cm:
            log = big.Log(12345, threading=False)
        self.assertIn("don't know how to log", str(cm.exception))

    def test_log_closed_error(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        log.close()
        with self.assertRaises(RuntimeError) as cm:
            log("after close")
        self.assertIn("closed", str(cm.exception))

    def test_log_write_closed_error(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        log.close()
        with self.assertRaises(RuntimeError):
            log.write("after close")

    def test_log_heading_closed_error(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        log.close()
        with self.assertRaises(RuntimeError):
            log.heading("after close")

    def test_log_close_is_idempotent(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        self.assertFalse(log.closed())
        log.close()
        self.assertTrue(log.closed())
        log.close()
        self.assertTrue(log.closed())

    def test_log_atexit(self):
        # simulate atexit calls
        log = big.Log([], threading=False)
        self.assertFalse(log.closed())
        log._atexit()
        self.assertTrue(log.closed())

        log = big.Log([], threading=True)
        self.assertFalse(log.closed())
        log._atexit()
        self.assertTrue(log.closed())


class TestLogMethods(unittest.TestCase):
    """Tests for Log methods."""

    def test_log_method(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        log.log("via log method")
        log.close()
        self.assertTrue(any("via log method" in s for s in array))

    def test_log_write(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        log.write("raw write\n")
        log.close()
        self.assertTrue(any("raw write" in s for s in array))

    def test_log_write_not_string(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        with self.assertRaises(TypeError):
            log.write(12345)
        log.close()

    def test_log_heading(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        log.heading("My Heading")
        log.close()
        self.assertTrue(any("My Heading" in s for s in array))

    def test_log_heading_not_string(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        with self.assertRaises(TypeError):
            log.heading(12345)
        log.close()

    def test_log_heading_custom_marker(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        log.heading("Custom", marker='*')
        log.close()
        self.assertTrue(any("*" in s for s in array))

    def test_log_enter_exit(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        log.enter("subsystem")
        log("inside")
        log.exit()
        log.close()
        output = ''.join(array)
        self.assertIn("subsystem", output)
        self.assertIn("inside", output)

    def test_log_enter_context_manager(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        with log.enter("subsystem"):
            log("inside context")
        log.close()
        output = ''.join(array)
        self.assertIn("subsystem", output)
        self.assertIn("inside context", output)

    def test_log_unbalanced_exit(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        with self.assertRaises(RuntimeError) as cm:
            log.exit()
        self.assertIn("unbalanced", str(cm.exception))
        log.close()

    def test_log_flush(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        log("before flush")
        log.flush()
        log.close()

    def test_log_reset(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        log("before reset")
        log.reset()
        log("after reset")
        log.close()

    def test_log_reset_after_close(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        log("before reset")
        log.close()
        log.reset()
        log("after reset")
        log.close()

    def test_log_sep_end_params(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        log("a", "b", "c", sep="-", end="!\n")
        log.close()
        self.assertTrue(any("a-b-c!" in s for s in array))

    def test_log_with_flush_param(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        log("flushed message", flush=True)
        log.close()


class TestLogContextManager(unittest.TestCase):
    """Tests for Log as a context manager."""

    def test_log_context_manager(self):
        array = []
        with big.Log(array, threading=False, initial='', final='', prefix='') as log:
            log("inside with block")
        # After exiting, flush should have been called
        self.assertTrue(any("inside with block" in s for s in array))


class TestLogThreading(unittest.TestCase):
    """Tests for Log with threading enabled."""

    def test_log_threaded(self):
        array = []
        log = big.Log(array, threading=True, initial='', final='', prefix='')
        log("threaded message")
        log.close()
        self.assertTrue(any("threaded message" in s for s in array))

    def test_log_threaded_multiple_messages(self):
        array = []
        log = big.Log(array, threading=True, initial='', final='', prefix='')
        for i in range(10):
            log(f"message {i}")
        log.close()
        output = ''.join(array)
        for i in range(10):
            self.assertIn(f"message {i}", output)

    def test_log_threaded_enter_exit(self):
        array = []
        log = big.Log(array, threading=True, initial='', final='', prefix='')
        with log.enter("threaded subsystem"):
            log("inside threaded")
        log.close()
        output = ''.join(array)
        self.assertIn("threaded subsystem", output)

    def test_log_threaded_reset(self):
        array = []
        log = big.Log(array, threading=True, initial='', final='', prefix='')
        log("before")
        log.reset()
        log("after")
        log.close()

    def test_log_threaded_reset_after_close(self):
        array = []
        log = big.Log(array, threading=True, initial='', final='', prefix='')
        log("before")
        log.close()
        log.reset()
        log("after")
        log.close()

    def test_log_threaded_heading(self):
        array = []
        log = big.Log(array, threading=True, initial='', final='', prefix='')
        log.heading("threaded heading")
        log.close()
        self.assertTrue(any("threaded heading" in s for s in array))

    def test_log_threaded_flush(self):
        array = []
        log = big.Log(array, threading=True, initial='', final='', prefix='')
        log("message")
        log.flush()
        log.close()

    def test_log_exit_closed_error(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        log.close()
        with self.assertRaises(RuntimeError):
            log.exit()

    def test_log_flush_closed_error(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        log.close()
        with self.assertRaises(RuntimeError):
            log.flush()


class TestLogNestedLogs(unittest.TestCase):
    """Tests for nested Log objects."""

    def test_nested_logs(self):
        array1 = []
        array2 = []
        inner_log = big.Log(array2, threading=False, initial='', final='', prefix='')
        outer_log = big.Log(array1, inner_log, threading=False, initial='', final='', prefix='')
        outer_log("message")
        outer_log.close()
        # Message should appear in both
        self.assertTrue(any("message" in s for s in array1))
        self.assertTrue(any("message" in s for s in array2))

    def test_nested_logs_write(self):
        array1 = []
        array2 = []
        inner_log = big.Log(array2, threading=False, initial='', final='', prefix='')
        outer_log = big.Log(array1, inner_log, threading=False, initial='', final='', prefix='')
        outer_log.write("raw write\n")
        outer_log.close()
        self.assertTrue(any("raw write" in s for s in array2))

    def test_nested_logs_heading(self):
        array1 = []
        array2 = []
        inner_log = big.Log(array2, threading=False, initial='', final='', prefix='')
        outer_log = big.Log(array1, inner_log, threading=False, initial='', final='', prefix='')
        outer_log.heading("nested heading")
        outer_log.close()
        self.assertTrue(any("nested heading" in s for s in array2))

    def test_nested_logs_enter_exit(self):
        array1 = []
        array2 = []
        inner_log = big.Log(array2, threading=False, initial='', final='', prefix='')
        outer_log = big.Log(array1, inner_log, threading=False, initial='', final='', prefix='')
        outer_log.enter("nested subsystem")
        outer_log("inside nested")
        outer_log.exit()
        outer_log.close()
        output2 = ''.join(array2)
        self.assertIn("nested subsystem", output2)

    def test_nested_logs_flush(self):
        array1 = []
        array2 = []
        inner_log = big.Log(array2, threading=False, initial='', final='', prefix='')
        outer_log = big.Log(array1, inner_log, threading=False, initial='', final='', prefix='')
        outer_log("before flush")
        outer_log.flush()
        outer_log.close()

    def test_nested_logs_reset(self):
        array1 = []
        array2 = []
        inner_log = big.Log(array2, threading=False, initial='', final='', prefix='')
        outer_log = big.Log(array1, inner_log, threading=False, initial='', final='', prefix='')
        outer_log("before reset")
        outer_log.close()
        outer_log.reset()
        outer_log("after reset")
        outer_log.close()


class TestLogFormatting(unittest.TestCase):
    """Tests for Log formatting options."""

    def test_log_with_prefix(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='[PREFIX] ')
        log("test")
        log.close()
        self.assertTrue(any("[PREFIX]" in s for s in array))

    def test_log_with_initial_and_final(self):
        array = []
        log = big.Log(array, threading=False, initial='START', final='FINISH', prefix='')
        log("middle")
        log.close()
        output = ''.join(array)
        self.assertIn("START", output)
        self.assertIn("FINISH", output)

    def test_log_no_start_final_or_prefix(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='')
        log("test")
        log.close()

    def test_log_empty_separator(self):
        array = []
        log = big.Log(array, threading=False, initial='', final='', prefix='', separator='')
        log.enter("sub")
        log("test")
        log.exit()
        log.close()


class TestSink(unittest.TestCase):
    """Tests for Sink."""

    def test_sink_basic(self):
        sink = big.Sink()
        log = big.Log(sink, threading=False, initial='', final='', prefix='')
        log("message1")
        log("message2")
        log.close()

        events = list(sink)
        self.assertEqual(len(events), 2)
        for i, e in enumerate(events, 1):
            elapsed, duration, thread, depth, type, message = e
            self.assertGreater(elapsed, 0)
            self.assertGreaterEqual(duration, 0)
            self.assertEqual(thread, threading.current_thread())
            self.assertEqual(depth, 0)
            self.assertEqual(type, big.log.Sink.LOG)
            self.assertTrue(message.startswith('message'))
            self.assertTrue(message.endswith(str(i)))

    def test_sink_event_types(self):
        sink = big.Sink()
        log = big.Log(sink, threading=False, initial='', final='', prefix='')
        log("regular event")
        log.write("write event")
        log.heading("heading event")
        log.enter("enter event")
        log.exit()
        log.close()

        events = list(sink)
        types = [e[4] for e in events]
        self.assertIn(big.Sink.WRITE, types)
        self.assertIn(big.Sink.LOG, types)
        self.assertIn(big.Sink.HEADING, types)
        self.assertIn(big.Sink.ENTER, types)
        self.assertIn(big.Sink.EXIT, types)

    def test_sink_print(self):
        sink = big.Sink()
        log = big.Log(sink, threading=False, initial='', final='', prefix='')
        log("test event")
        log.close()

        output = []
        sink.print(print=output.append)
        self.assertTrue(len(output) > 0)

    def test_sink_print_with_formats(self):
        sink = big.Sink()
        log = big.Log(sink, threading=False, initial='', final='', prefix='')
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
        log = big.Log(sink, threading=False, initial='', final='', prefix='')
        log("test event")
        log.close()

        output = []
        sink.print(print=output.append, separator='')
        self.assertTrue(len(output) > 0)

    def test_sink_print_default_print(self):
        sink = big.Sink()
        log = big.Log(sink, threading=False, initial='', final='', prefix='')
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
        log = big.Log(sink, threading=False, initial='', final='', prefix='')
        log("before reset")
        log.close()

        self.assertTrue(len(list(sink)) > 0)

        log.reset()
        # After reset, sink should also be reset
        # (events cleared when re-registered)

    def test_sink_write(self):
        sink = big.Sink()
        log = big.Log(sink, threading=False, initial='', final='', prefix='')
        log.write("raw write\n")
        log.close()
        events = list(sink)
        self.assertEqual(len(events), 1)


class TestOldLogger(unittest.TestCase):
    """Tests for OldLogger."""

    def test_old_logger_basic(self):
        old = big.OldLogger()
        log = big.Log(old, threading=False, initial='', final='', prefix='')
        log("event")
        log.close()

        events = list(old)
        # Should have "log start" and "event"
        self.assertTrue(len(events) >= 2)

    def test_old_logger_enter_exit(self):
        old = big.OldLogger()
        log = big.Log(old, threading=False, initial='', final='', prefix='')
        log.enter("subsystem")
        log("inside")
        log.exit()
        log.close()

        events = list(old)
        event_strs = [e[2] for e in events]
        self.assertIn("subsystem start", event_strs)
        self.assertIn("subsystem end", event_strs)

    def test_old_logger_print(self):
        old = big.OldLogger()
        log = big.Log(old, threading=False, initial='', final='', prefix='')
        log("test")
        log.close()

        output = []
        old.print(print=output.append)
        self.assertTrue(len(output) > 0)

    def test_old_logger_print_no_title(self):
        old = big.OldLogger()
        log = big.Log(old, threading=False, initial='', final='', prefix='')
        log("test")
        log.close()

        output = []
        old.print(print=output.append, title=None)
        # First line should not be "[event log]"
        self.assertFalse(output[0].startswith("[event log]"))

    def test_old_logger_print_no_headings(self):
        old = big.OldLogger()
        log = big.Log(old, threading=False, initial='', final='', prefix='')
        log("test")
        log.close()

        output = []
        old.print(print=output.append, headings=False)

    def test_old_logger_write(self):
        old = big.OldLogger()
        log = big.Log(old, threading=False, initial='', final='', prefix='')
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
        log = big.Log(buffer, threading=False, initial='', final='', prefix='')
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
            log = big.Log(path, threading=False, initial='', final='', prefix='')
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
        log = big.Log(array, threading=False, initial='', final='', prefix='[{elapsed}] ', clock=clock)

        clock.advance(1_000_000_000)  # 1 second
        log("at 1 second")
        log.close()

        output = ''.join(array)
        self.assertIn("1", output)


class TestExport(unittest.TestCase):
    """Test that all expected symbols are exported."""

    def test_all_exports(self):
        expected = [
            'Logger', 'Callable', 'Print', 'List', 'Buffer', 'File', 'FileHandle',
            'Log', 'Sink', 'OldLogger', 'OldLog'
        ]
        for name in expected:
            self.assertIn(name, log_module.__all__)


def run_tests():
    bigtestlib.run(name="big.log", module=__name__)


if __name__ == "__main__":  # pragma: no cover
    run_tests()
    bigtestlib.finish()
