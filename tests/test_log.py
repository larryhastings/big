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
import time
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
        destination.close()  # Should not raise

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

    def test_file_buffered_mode(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            path = f.name

        try:
            file_destination = big.Log.File(path, mode='wt')
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
            fd = big.Log.File(path, mode='wt', flush=True)
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
            fd = big.Log.File(path, mode='at')
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
        log = big.Log(big.log.TMPFILE, name="LogName", threading=False, formats={"start": None, "end": None}, prefix='', timestamp=lambda x:"ABACAB /DEADBEEF")
        expected = f"LogName.ABACAB.-DEADBEEF.{os.getpid()}.txt"
        self.assertEqual(big.log.TMPFILE.path.name, expected)



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
        self.assertEqual(log.timestamp, big.time.timestamp_human)
        self.assertEqual(log.timestamp_clock, time.time)
        self.assertEqual(log.width, 79)

        self.assertEqual(log.closed, False)
        self.assertGreater(log.start_time_ns, ns)
        self.assertGreater(log.start_time_epoch, epoch)
        self.assertEqual(log.end_time_epoch, None)
        self.assertEqual(log.nesting, ())

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
        with self.assertRaises(ValueError) as cm:
            log = big.Log(12345, threading=False)
        self.assertIn("don't know how to log to destination", str(cm.exception))

    def test_log_after_closed(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        log.close()
        log("after close")

    def test_log_write_after_closed(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        log.close()
        log.write("after close")

    def test_log_heading_after_closed(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        log.close()
        log.box("after close")

    def test_log_close_is_idempotent(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
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

    def test_print_method(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        log.print("via print method")
        log.close()
        self.assertTrue(any("via print method" in s for s in array))

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

    def test_log_heading(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        log.box("My Heading")
        log.close()
        self.assertTrue(any("My Heading" in s for s in array))

    def test_log_heading_not_string(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        with self.assertRaises(TypeError):
            log.box(12345)
        log.close()

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

    def test_log_with_flush_param(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, formats={"start": None, "end": None}, prefix='')
        log("flushed message!", flush=True)
        self.assertIn("flushed message!\n", s.getvalue())
        log.close()

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
            big.Log(formats={"enter": None})
        with self.assertRaises(TypeError):
            big.Log(formats={83: {"format": "abc", "line": "-"}})
        with self.assertRaises(ValueError):
            big.Log(formats={"not an id": {"format": "abc", "line": "-"}})
        with self.assertRaises(TypeError):
            big.Log(formats={"splunk": 55})
        with self.assertRaises(ValueError):
            big.Log(formats={"splunk": {"format": 33}})
        with self.assertRaises(ValueError):
            big.Log(formats={"reset": {"format": "abc", "line": "-"}})

        l = big.Log(formats={"start": None, "end": None})
        with self.assertRaises(ValueError):
            l.print("abc", format="spooky")
        l.close()

class TestLogLazyHeaderAndFooter(unittest.TestCase):

    def test_lazy_header_from_log(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, formats={"start": {"format": "START"}, "end": {"format": "END"}}, prefix='[PREFIX] ', width=20)
        log("howdy!")
        log.close()

        expected = """
START
[PREFIX] howdy!
END
        """.strip()
        self.assertEqual(s.getvalue().strip(), expected)

    def test_lazy_header_from_write(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, formats={"start": {"format": "START"}, "end": {"format": "END"}}, prefix='[PREFIX] ', width=20)
        log.write("howdy!\n")
        log.close()

        expected = """
START
howdy!
END
        """.strip()
        self.assertEqual(s.getvalue().strip(), expected)

    def test_lazy_header_from_heading(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, formats={"start": {"format": "START"}, "end": {"format": "END"}}, prefix='[PREFIX] ', width=20)
        log.box("howdy!")
        log.close()

        expected = """
START
[PREFIX] +----------
[PREFIX] | howdy!
[PREFIX] +----------
END
        """.strip()
        self.assertEqual(s.getvalue().strip(), expected)

    def test_lazy_header_from_enter(self):
        s = io.StringIO()
        log = big.Log(s, threading=False, formats={"start": {"format": "START"}, "end": {"format": "END"}}, prefix='[PREFIX] ', width=20)
        with log.enter("howdy!"):
            log("woah!")
        log.close()

        expected = """
START
[PREFIX] +-----+----
[PREFIX] |start| howdy!
[PREFIX] +-----+----
[PREFIX]     woah!
[PREFIX] +-----+----
[PREFIX] | end | howdy!
[PREFIX] +-----+----
END
        """.strip()
        self.assertEqual(s.getvalue().strip(), expected)


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
        log.close()

    def test_log_threaded_reset_after_close(self):
        array = []
        log = big.Log(array, threading=True, formats={"start": None, "end": None}, prefix='')
        log("before")
        log.close()
        log.reset()
        log("after")
        log.close()

    def test_log_threaded_heading(self):
        array = []
        log = big.Log(array, threading=True, formats={"start": None, "end": None}, prefix='')
        log.box("threaded heading")
        log.close()
        self.assertTrue(any("threaded heading" in s for s in array))

    def test_log_threaded_flush(self):
        array = []
        log = big.Log(array, threading=True, formats={"start": None, "end": None}, prefix='')
        log("message")
        log.flush()
        log.close()

    def test_log_exit_closed_error(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        log.close()
        log.exit()

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

    def test_log_with_initial_and_final(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": {"format": "START"}, "end": {"format": "END"}}, prefix='')
        log("middle")
        log.close()
        output = ''.join(array)
        self.assertIn("START", output)
        self.assertIn("END", output)

    def test_log_no_start_final_or_prefix(self):
        array = []
        log = big.Log(array, threading=False, formats={"start": None, "end": None}, prefix='')
        log("test")
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

        self.assertIsInstance(events.pop(), log_module.SinkCloseEvent)
        self.assertIsInstance(events.pop(), log_module.SinkFlushEvent)

        for i, e in enumerate(events, 1):
            self.assertIsInstance(e, log_module.SinkLogEvent)
            self.assertEqual(e.depth, 0)
            self.assertGreaterEqual(e.duration, 0)
            self.assertGreater(e.elapsed, 0)
            self.assertEqual(e.epoch, None)
            self.assertIn('message', e.formatted)
            self.assertTrue(e.message.startswith('message'))
            self.assertTrue(e.message.endswith(str(i)))
            self.assertEqual(e.ns, None)
            self.assertEqual(e.number, 1)
            self.assertEqual(e.thread, threading.current_thread())

        e = events[0]
        clone = log_module.SinkLogEvent(
            number=e.number,
            elapsed=e.elapsed,
            thread=e.thread,
            format=e.format,
            message=e.message,
            formatted=e.formatted,
            depth=e.depth,
            )
        clone._duration = e.duration
        self.assertEqual(e, clone)
        self.assertNotEqual(e, events[1])
        self.assertLess(e, events[1])

        with self.assertRaises(TypeError):
            e < 3.1415

        sse = big.SinkStartEvent(0, 5, 10, '')
        self.assertEqual(repr(sse), "SinkStartEvent(epoch=10, formatted='', ns=5)")

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
        self.assertIn(SinkEvent.TYPE_RESET, types)
        self.assertIn(SinkEvent.TYPE_START, types)
        self.assertIn(SinkEvent.TYPE_END, types)
        self.assertIn(SinkEvent.TYPE_FLUSH, types)
        self.assertIn(SinkEvent.TYPE_CLOSE, types)
        self.assertIn(SinkEvent.TYPE_WRITE, types)
        self.assertIn(SinkEvent.TYPE_LOG, types)
        self.assertIn(SinkEvent.TYPE_ENTER, types)
        self.assertIn(SinkEvent.TYPE_EXIT, types)

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
        self.assertEqual(s, events[0].message)

    def test_sink_with_banners(self):
        sink = big.Log.Sink()
        log = big.Log(sink, threading=False, name='Sink', formats={"start": {"format": "{name} START\n"}, "end": {"format": "{name} END\n"}}, prefix='[PREFIX] ')
        log("message")
        log.close()
        events = list(sink)
        self.assertEqual(len(events), 5)

        SinkEvent = log_module.SinkEvent
        self.assertEqual(events[0].type, SinkEvent.TYPE_START)
        self.assertEqual(events[0].elapsed, 0)
        self.assertGreater(events[0].ns, 0)
        self.assertGreater(events[0].epoch, 0)

        self.assertEqual(events[1].type, SinkEvent.TYPE_LOG)
        self.assertEqual(events[1].message, 'message')

        self.assertEqual(events[2].type, SinkEvent.TYPE_END)
        self.assertGreater(events[2].elapsed, 0)

        self.assertEqual(events[3].type, SinkEvent.TYPE_FLUSH)

        self.assertEqual(events[4].type, SinkEvent.TYPE_CLOSE)


class TestOldDestination(unittest.TestCase):
    """Tests for OldDestination."""

    def test_old_destination_basic(self):
        old = big.OldDestination()
        log = big.Log(old, threading=False, formats={"start": None, "end": None}, prefix='')
        log("event")
        log.close()

        events = list(old)
        # Should have "log start" and "event"
        self.assertTrue(len(events) >= 2)

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
