#!/usr/bin/env python3

_license = """
big
Copyright 2022-2023 Larry Hastings
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


__all__ = ['default_clock', 'Log']


import builtins

try:
    # new in 3.7
    from time import monotonic_ns as default_clock
except ImportError: # pragma: no cover
    from time import perf_counter
    def default_clock():
        return int(perf_counter() * 1000000000.0)


class Log:
    """
    A simple lightweight logging class, useful for performance analysis.
    Not intended as a full-fledged logging facility like Python's
    "logging" module.

    The clock named parameter specifies the function to call to get the
    time.  This function should return an int, representing elapsed time
    in nanoseconds.

    Allows nesting, which is literally just a presentation thing.

    To use: first, create your Log object.
        log = Log()
    Then log events by calling your Log object,
    passing in a string describing the event.
        log('text')
    Enter a nested subsystem containing events with log.enter:
        log.enter('subsystem')
    Then later exit that subsystem with log.exit:
        log.exit()
    And finally print the log:
        log.print()

    You can also iterate over the log events using iter(log).
    This yields 4-tuples:
        (start_time, elapsed_time, event, depth)
    start_time and elapsed_time are times, expressed as
    an integer number of nanoseconds.  The first event
    is at start_time 0, and all subsequent start times are
    relative to that time.  event is the event string you
    passed in to log() (or "<subsystem> start" or
    "<subsystem> end").  depth is an integer indicating
    how many subsystems the event is nested in; larger
    numbers indicate deeper nesting.
    """

    # Internally, all times are stored relative to
    # the logging start time.
    # Writing this any other way was *madness.*
    # (You're dealing with 15-digit numbers that change
    # randomly in the last... seven? digits.  You'll go blind!)

    def __init__(self, clock=None):
        clock = clock or default_clock
        self.clock = clock
        self.reset()

    def reset(self):
        """
        Resets the log to its initial state.
        """
        self.start = self.clock()
        self.stack = []

        event = 'log start'
        self.longest_event = len(event)
        self.events = [(0, event, 0)]

    def enter(self, subsystem):
        """
        Notifies the log that you've entered a subsystem.
        The subsystem parameter should be a string
        describing the subsystem.

        This is really just a presentation
        thing; all subsequent logged entries will be indented
        until you make the corresponding `log.exit()` call.

        You may nest subsystems as deeply as you like.
        """
        self(subsystem + " start")
        self.stack.append(subsystem)

    def exit(self):
        """
        Exits a logged subsystem.  See Log.enter().
        """
        subsystem = self.stack.pop()
        self(subsystem + " end")

    def __call__(self, event):
        """
        Log an event.  Pass in a string specifying the event.
        """
        t = self.clock() - self.start
        self.events.append((t, event, len(self.stack)))
        self.end = t
        self.longest_event = max(self.longest_event, len(event))

    def __iter__(self):
        """
        Iterate over the events of the log.
        Yields 4-tuples:
            (start_time, elapsed_time, event, depth)
        start_time and elapsed_time are floats.
        event is the string you specified when you logged.
        depth is an integer; the higher the number,
          the more nested this event is (how many log.enter()
          calls are active).
        """
        i = iter(tuple(self.events))
        waiting = next(i)
        for e in i:
            t, event, depth = waiting
            next_t = e[0]
            yield (t, next_t - t, event, depth)
            waiting = e
        t, event, depth = waiting
        yield (t, 0, event, depth)

    def print(self, *, print=None, title="[event log]", headings=True, indent=2, seconds_width=2, fractional_width=9):
        """
        Prints the log.

        Keyword-only parameters:

        print specifies the print function to use, default is builtins.print.
        title specifies the title to print at the beginning.
          Default is "[event log]".  To suppress, pass in None.
        headings is a boolean; if True (the default), prints column headings
          for the log.
        indent is the number of spaces to indent in front of log entries,
          and also how many spaces to indent each time we enter a subsystem.
        seconds_width is how wide to make the seconds column, default 2.
        fractional_width is how wide to make the fractional column, default 9.
        """
        if not print:
            print = builtins.print

        indent = " " * indent
        column_width = seconds_width + 1 + fractional_width

        def format_time(t):
            assert t is not None
            seconds = t // 1_000_000_000
            nanoseconds = f"{t - seconds:>09}"
            nanoseconds = nanoseconds[:fractional_width]
            return f"{seconds:0{seconds_width}}.{nanoseconds}"

        if title:
            print(title)

        if headings:
            print(f"{indent}{'start':{column_width}}  {'elapsed':{column_width}}  event")
            column_dashes = '-' * column_width
            print(f"{indent}{column_dashes}  {column_dashes}  {'-' * self.longest_event}")

        formatted = []
        for start, elapsed, event, depth in self:
            indent2 = indent * depth
            print(f"{indent}{format_time(start)}  {format_time(elapsed)}  {indent2}{event}")
