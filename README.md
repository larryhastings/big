![# big](/resources/images/big.header.png)

##### Copyright 2022 by Larry Hastings

**big** is a Python package, a grab-bag of useful technology
I always want to have handy.

Finally!  For years, I've copied-and-pasted all my little
helper functions between projects--we've all done it.
But now I've finally taken the time to consolidate all those
useful little functions into one big package, so they're always
at hand, ready to use.
And, since it's a public package, you can use 'em too!

Not only that, but I've taken my time and re-thought and
retooled a lot of these functions.  All the difficult-to-use,
overspecialized, cheap hacks have been upgraded with elegant
new APIs and clever functionality.
**big** is a real pleasure to use!

**big** requires Python 3.6 or newer.  It has few dependencies.

*Think big!*

## Using big

To use **big**, just install the **big** package (and its dependencies)
from PyPI using your favorite Python package manager.

Once **big** is installed, you can simply import it.  However, the
top-level **big** package doesn't contain anything but a version number.
Internally **big** is broken up into submodules, aggregated together
loosely by problem domain, and you can selectively import just the
functions you want.  For example, if you only want to use the text functions,
just import the **text** submodule:

```Python
import big.text
```

If you'd prefer to import everything all at once, simply import the
**big.all** module.  This one module imports all the other modules,
and imports all their symbols too.  So, one convenient way to work
with **big** is this:

```Python
import big.all as big
```

That will make every symbol defined in **big** accessible from the `big`
object. For example, if you want to use
[`multisplit`,](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
you can call it with just `big.multisplit`.

You can also use **big.all** with `import *`:

```Python
from big.all import *
```

but that's up to you.

**big** is licensed using the [MIT license.](https://opensource.org/licenses/MIT)
You're free to use it and even ship it in your own programs, as long as you leave my copyright
notice on the source code.

# Index

[`ascii_newlines`](#newlines)

[`ascii_newlines_without_dos`](#newlines)

[`ascii_whitespace`](#whitespace)

[`ascii_whitespace_without_dos`](#whitespace)

[`big.boundinnerclass`](#`bigboundinnerclass`)

[`big.builtin`](#bigbuiltin)

[`big.file`](#bigfile)

[`big.graph`](#biggraph)

[`big.heap`](#bigheap)

[`big.itertools`](#bigitertools)

[`big.scheduler`](#bigscheduler)

[`big.text`](#bigtext)

[`big.time`](#bigtime)

[`BoundInnerClass`](#boundinnerclasscls)

[`CycleError`](#cycleerror)

[`datetime_ensure_timezone(d, timezone)`](#datetime_ensure_timezoned-timezone)

[`datetime_set_timezone(d, timezone)`](#datetime_set_timezoned-timezone)

[`fgrep(path, text, *, encoding=None, enumerate=False, case_insensitive=False)`](#fgreppath-text--encodingnone-enumeratefalse-case_insensitivefalse)

[`file_mtime(path)`](#file_mtimepath)

[`file_mtime_ns(path)`](#file_mtime_nspath)

[`file_size(path)`](#file_sizepath)

[`gently_title(s, *, apostrophes=None, double_quotes=None)`](#gently_titles-apostrophesnone-double_quotesnone)

[`get_float(o, default=_sentinel)`](#get_floato-default_sentinel)

[`get_int(o, default=_sentinel)`](#get_into-default_sentinel)

[`get_int_or_float(o, default=_sentinel)`](#get_int_or_floato-default_sentinel)

[`grep(path, pattern, *, encoding=None, enumerate=False, flags=0)`](#greppath-pattern--encodingnone-enumeratefalse-flags0)

[`Heap(i=None)`](#heapinone)

[`Heap.append(o)`](#heapappendo)

[`Heap.clear()`](#heapclear)

[`Heap.copy()`](#heapcopy)

[`Heap.extend(i)`](#heapextendi)

[`Heap.remove(o)`](#heapremoveo)

[`Heap.popleft()`](#heappopleft)

[`Heap.append_and_popleft(o)`](#heapappend_and_poplefto)

[`Heap.popleft_and_append(o)`](#heappopleft_and_append0)

[`Heap.queue`](#heapqueue)

[`lines(s, separators=None, *, line_number=1, column_number=1, tab_width=8, **kwargs)`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs)

[`lines_convert_tabs_to_spaces(li)`](#lines_convert_tabs_to_spacesli)

[`lines_filter_comment_lines(li, comment_separators)`](#lines_filter_comment_linesli-comment_separators)

[`lines_containing(li, s, *, invert=False)`](#lines_containingli-s--invertfalse)

[`lines_grep(li, pattern, *, invert=False, flags=0)`](#lines_grepli-pattern--invertfalse-flags0)

[`lines_rstrip(li)`](#lines_rstripli)

[`lines_sort(li, *, reverse=False)`](#lines_sortli--reversefalse)

[`lines_strip(li)`](#lines_stripli)

[`lines_strip_comments(li, comment_separators, *, quotes=('"', "'"), backslash='\\', rstrip=True, triple_quotes=True)`](#lines_strip_commentsli-comment_separators--quotes--backslash-rstriptrue-triple_quotestrue)

[`lines_strip_indent(li)`](#lines_strip_indentli)

[`merge_columns(*columns, column_separator=" ", overflow_response=OverflowResponse.RAISE, overflow_before=0, overflow_after=0)`](#merge_columnscolumns-column_separator--overflow_responseoverflowresponseraise-overflow_before0-overflow_after0)

[`multipartition(s, separators, count=1, *, reverse=False, separate=True)`](#multipartitions-separators-count1--reverseFalse-separateTrue)

[`multisplit(s, separators, *, keep=False, maxsplit=-1, reverse=False, separate=False, strip=False)`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)

[`multistrip(s, separators, left=True, right=True)`](#multistrips-separators-leftTrue-rightTrue)

[`newlines`](#newlines)

[`newlines_without_dos`](#newlines)

[`normalize_whitespace(s, separators=None, replacement=None)`](#normalize_whitespaces-separatorsNone-replacementnone)

[`parse_timestamp_3339Z(s, *, timezone=None)`](#parse_timestamp_3339zs--timezonenone)

[`PushbackIterator(iterable=None)`](#pushbackiteratoriterablenone)

[`PushbackIterator.next(default=None)`](#pushbackiteratornextdefaultnone)

[`PushbackIterator.push(o)`](#pushbackiteratorpusho)

[`pushd(directory)`](#pushddirectory)

[`re_partition(text, pattern, count=1, *, flags=0, reverse=False)`](#re_partitiontext-pattern-count1--flags0-reversefalse)

[`re_rpartition(text, pattern, count=1, *, flags=0)`](#re_rpartitiontext-pattern-count1--flags0)

[`safe_mkdir(path)`](#safe_mkdirpath)

[`safe_unlink(path)`](#safe_unlinkpath)

[`Scheduler(regulator=None)`](#schedulerregulatornone)

[`Scheduler.schedule(o, time, *, absolute=False, priority=DEFAULT_PRIORITY)`](#schedulerscheduleo-time--absolutefalse-prioritydefault_priority)

[`Scheduler.cancel(event)`](#schedulercancelevent)

[`Scheduler.queue`](#schedulerqueue)

[`Scheduler.non_blocking()`](#schedulernon_blocking)

[`Scheduler.Event(time, priority, sequence, event, scheduler)`](#schedulereventtime-priority-sequence-event-scheduler)

[`Scheduler.Event.cancel()`](#schedulereventcancel)

[`Scheduler.Regulator(scheduler)`](#schedulerregulatorscheduler)

[`Scheduler.Regulator.now()`](#schedulerregulatornow)

[`Scheduler.Regulator.sleep(t)`](#schedulerregulatorsleept)

[`Scheduler.Regulator.wake()`](#schedulerregulatorwake)

[`split_quoted_strings(s, quotes=('"', "'"), *, triple_quotes=True, backslash='\\')`](#split_quoted_stringss-quotes---triple_quotestrue-backslash)

[`split_text_with_code(s, *, tab_width=8, allow_code=True, code_indent=4, convert_tabs_to_spaces=True)`](#split_text_with_codes--tab_width8-allow_codetrue-code_indent4-convert_tabs_to_spacestrue)

[`timestamp_3339Z(t=None, want_microseconds=None)`](#timestamp_3339ztnone-want_microsecondsnone)

[`timestamp_human(t=None, want_microseconds=None)`](#timestamp_humantnone-want_microsecondsnone)

[`TopologicalSorter(graph=None)`](#topologicalsortergraphnone)

[`TopologicalSorter.copy()`](#topologicalsortercopy)

[`TopologicalSorter.cycle()`](#topologicalsortercycle)

[`TopologicalSorter.print()`](#topologicalsorterprintprintprint)

[`TopologicalSorter.remove(node)`](#topologicalsorterremovenode)

[`TopologicalSorter.reset()`](#topologicalsorterreset)

[`TopologicalSorter.View`](#topologicalsorterview-1)

[`TopologicalSorter.view()`](#topologicalsorterview)

[`TopologicalSorter.View.close()`](#topologicalsorterviewclose)

[`TopologicalSorter.View.copy()`](#topologicalsorterviewcopy)

[`TopologicalSorter.View.done(*nodes)`](#topologicalsorterviewdonenodes)

[`TopologicalSorter.View.print(print=print)`](#topologicalsorterviewprintprintprint)

[`TopologicalSorter.View.ready()`](#topologicalsorterviewready)

[`TopologicalSorter.View.reset()`](#topologicalsorterviewreset)

[`touch(path)`](#touchpath)

[`translate_filename_to_exfat(s)`](#translate_filename_to_exfats)

[`translate_filename_to_unix(s)`](#translate_filename_to_unixs)

[`try_float(o)`](#try_floato)

[`try_int(o)`](#try_into)

[`UnboundInnerClass`](#unboundinnerclasscls)

[`utf8_newlines`](#newlines)

[`utf8_newlines_without_dos`](#newlines)

[`utf8_whitespace`](#whitespace)

[`utf8_whitespace_without_dos`](#whitespace)

[`whitespace`](#whitespace)

[`whitespace_without_dos`](#whitespace)

[`wrap_words(words, margin=79, *, two_spaces=True)`](#wrap_wordswords-margin79--two_spacestrue)

[**The `multi-` family of functions**](#The-multi--family-of-functions)

[**`lines` and lines modifier functions**](#lines-and-lines-modifier-functions)

[**Word wrapping and formatting**](#word-wrapping-and-formatting)

[**Bound inner classes**](#bound-inner-classes)

[**Enhanced `TopologicalSorter`**](#enhanced-topologicalsorter)


# API Reference

## `big.all`

This submodule doesn't define any of its own symbols.  Instead, it
imports every other submodule in **big**, and uses `import *` to
import every symbol from every other submodule, too.  Every
symbol in **big** is available in `big.all`.

## `big.boundinnerclass`

Class decorators that implement bound inner classes.  See the
[**Bound inner classes**](#bound-inner-classes)
deep-dive for more information.


#### `BoundInnerClass(cls)`

> Class decorator for an inner class.  When accessing the inner class
> through an instance of the outer class, "binds" the inner class to
> the instance.  This changes the signature of the inner class's `__init__`
> from
> ```Python
> def __init__(self, *args, **kwargs):`
> ```
> to
> ```Python
> def __init__(self, outer, *args, **kwargs):
> ```
> where `outer` is the instance of the outer class.

#### `UnboundInnerClass(cls)`

> Class decorator for an inner class that prevents binding
> the inner class to an instance of the outer class.
>
> Subclasses of a class decorated with `BoundInnerClass` must always
> be decorated with either `BoundInnerClass` or `UnboundInnerClass`.


## `big.builtin`

Functions for working with builtins.  (Named `builtin` to avoid a
name collision with the `builtins` module.)

In general, the idea with these functions is a principle I first
read about in either
[Code Complete](http://aroma.vn/web/wp-content/uploads/2016/11/code-complete-2nd-edition-v413hav.pdf)
or
[Writing Solid Code:](http://cs.brown.edu/courses/cs190/2008/documents/restricted/Writing%20Solid%20Code.pdf)

> *Don't associate with losers.*

The intent here is, try to design APIs where it's impossible to call them
the wrong way.  Restrict the inputs to your functions to values you can
always handle, and you won't ever have to return an error.

The functions in this sub-module are designed to always work.  None of
them should ever raise an exception--no matter *what* nonsense you pass in.
(But don't take that as a challenge!)


#### `get_float(o, default=_sentinel)`

> Returns `float(o)`, unless that conversion fails,
> in which case returns the default value.  If
> you don't pass in an explicit default value,
> the default value is `o`.

#### `get_int(o, default=_sentinel)`

> Returns `int(o)`, unless that conversion fails,
> in which case returns the default value.  If
> you don't pass in an explicit default value,
> the default value is `o`.

#### `get_int_or_float(o, default=_sentinel)`

> Converts `o` into a number, preferring an int to a float.
>
> If `o` is already an int or float, returns `o` unchanged.  Otherwise,
> tries `int(o)`.  If that conversion succeeds, returns the result.
> Otherwise, tries `float(o)`.  If that conversion succeeds, returns
> the result.  Otherwise returns the default value.  If you don't
> pass in an explicit default value, the default value is `o`.

#### `try_float(o)`

> Returns `True` if `o` can be converted into a float,
> and `False` if it can't.

#### `try_int(o)`

> Returns `True` if `o` can be converted into an int,
> and `False` if it can't.


## `big.file`

Functions for working with files, directories, and I/O.


#### `fgrep(path, text, *, encoding=None, enumerate=False, case_insensitive=False)`

> Find the lines of a file that match some text, like the UNIX `fgrep` utility
> program.
>
> `path` should be an object representing a path to an existing file, one of:
>
> * a string,
> * a bytes object, or
> * a `pathlib.Path` object.
>
> `text` should be either string or bytes.
>
> `encoding` is used as the file encoding when opening the file.
>
> if `text` is a str, the file is opened in text mode.
> if `text` is a bytes object, the file is opened in binary mode.
> `encoding` must be `None` when the file is opened in binary mode.
>
> If `case_insensitive` is true, perform the search in a case-insensitive
> manner.
>
> Returns a list of lines in the file containing `text`.  The lines are either
> strings or bytes objects, depending on the type of `pattern`.  The lines
> have their newlines stripped but preserve all other whitespace.
>
> If `enumerate` is true, returns a list of tuples of (line_number, line).
> The first line of the file is line number 1.
>
> For simplicity of implementation, the entire file is read in to memory
> at one time.  If `case_insensitive` is True, a lowercased copy is also used.


#### `file_mtime(path)`

> Returns the modification time of `path`, in seconds since the epoch.
> Note that seconds is a float, indicating the sub-second with some
> precision.

#### `file_mtime_ns(path)`

> Returns the modification time of `path`, in nanoseconds since the epoch.

#### `file_size(path)`

> Returns the size of the file at `path`, as an integer representing the
> number of bytes.

#### `grep(path, pattern, *, encoding=None, enumerate=False, flags=0)`

> Look for matches to a regular expression pattern in the lines of a file,
> like the UNIX `grep` utility program.
>
> `path` should be an object representing a path to an existing file, one of:
>
> * a string,
> * a bytes object, or
> * a `pathlib.Path` object.
>
> `pattern` should be an object containing a regular expression, one of:
> * a string,
> * a bytes object, or
> * an `re.Pattern`, initialized with either `str` or `bytes`.
>
> `encoding` is used as the file encoding when opening the file.
>
> if `pattern` uses a `str`, the file is opened in text mode.
> if `pattern` uses a bytes object, the file is opened in binary mode.
> `encoding` must be `None` when the file is opened in binary mode.
>
> `flags` is passed in as the `flags` argument to `re.compile` if `pattern`
> is a string or bytes.  (It's ignored if `pattern` is an `re.Pattern` object.)
>
> Returns a list of lines in the file matching the pattern.  The lines
> are either strings or bytes objects, depending on the type of `text`.
> The lines have their newlines stripped but preserve all other whitespace.
>
> If `enumerate` is true, returns a list of tuples of `(line_number, line)`.
> The first line of the file is line number 1.
>
> For simplicity of implementation, the entire file is read in to memory
> at one time.
>
> Tip: to perform a case-insensitive pattern match, pass in the
> `re.IGNORECASE` flag into flags for this function (if pattern is a string
> or bytes) or when creating your regular expression object (if pattern is
> an `re.Pattern` object.
>
> (In older versions of Python, `re.Pattern` was a private type called
> `re._pattern_type`.)

#### `pushd(directory)`

> A context manager that temporarily changes the directory.
> Example:
>
> ```Python
> with big.pushd('x'):
>     pass
> ````
>
> This would change into the `'x'` subdirectory before
> executing the nested block, then change back to
> the original directory after the nested block.
>
> You can change directories in the nested block;
> this won't affect pushd restoring the original current
> working directory upon exiting the nested block.

#### `safe_mkdir(path)`

> Ensures that a directory exists at `path`.
> If this function returns and doesn't raise,
> it guarantees that a directory exists at `path`.
>
> If a directory already exists at `path`,
> does nothing.
>
> If a file exists at `path`, unlinks it
> then creates the directory.
>
> If the parent directory doesn't exist,
> creates it, then creates `path`.
>
> This function can still fail:
>
> * 'path' could be on a read-only filesystem.
> * You might lack the permissions to create `path`.
> * You could ask to create the directory 'x/y'
>   and 'x' is a file (not a directory).

#### `safe_unlink(path)`

> Unlinks `path`, if `path` exists and is a file.

#### `touch(path)`

> Ensures that `path` exists, and its modification time is the current time.
>
> If `path` does not exist, creates an empty file.
>
> If `path` exists, updates its modification time to the current time.

#### `translate_filename_to_exfat(s)`

> Ensures that all characters in s are legal for a FAT filesystem.
>
> Returns a copy of `s` where every character not allowed in a FAT
> filesystem filename has been replaced with a character (or characters)
> that are permitted.

#### `translate_filename_to_unix(s)`

> Ensures that all characters in s are legal for a UNIX filesystem.
>
> Returns a copy of `s` where every character not allowed in a UNIX
> filesystem filename has been replaced with a character (or characters)
> that are permitted.

## `big.graph`

A drop-in replacement for Python's
[`graphlib.TopologicalSorter`](https://docs.python.org/3/library/graphlib.html#graphlib.TopologicalSorter)
with an enhanced API.  This version of `TopologicalSorter` allows modifying the
graph at any time, and supports multiple simultaneous *views,* allowing
iteration over the graph more than once.

See the [**Enhanced `TopologicalSorter`**](#enhanced-topologicalsorter) deep-dive for more information.

#### `CycleError`

> Exception thrown by `TopologicalSorter` when it detects a cycle.

#### `TopologicalSorter(graph=None)`

> An object representing a directed graph of nodes.  See Python's
> [`graphlib.TopologicalSorter`](https://docs.python.org/3/library/graphlib.html#graphlib.TopologicalSorter)
> for concepts and the basic API.

New methods on `TopologicalSorter`:

#### `TopologicalSorter.copy()`

> Returns a shallow copy of the graph.  The copy also duplicates
> the state of `get_ready` and `done`.

#### `TopologicalSorter.cycle()`

> Checks the graph for cycles.  If no cycles exist, returns None.
> If at least one cycle exists, returns a tuple containing nodes
> that constitute a cycle.

#### `TopologicalSorter.print(print=print)`

> Prints the internal state of the graph.  Used for debugging.
>
> `print` is the function used for printing;
> it should behave identically to the builtin `print` function.

#### `TopologicalSorter.remove(node)`

> Remove `node` from the graph.
>
> If any node `P` depends on a node `N`, and `N` is removed,
> this dependency is also removed, but `P` is not
> removed from the graph.
>
> remove() works but it's slow (O(N)).
> TopologicalSorter is optimized for fast adds and fast views.

#### `TopologicalSorter.reset()`

Resets `get_ready` and `done` to their initial state.

#### `TopologicalSorter.view()`

> Returns a new `View` object on this graph.

#### `TopologicalSorter.View`

> A view on a `TopologicalSorter` graph object.
> Allows iterating over the nodes of the graph
> in dependency order.

Methods on a `View` object:

#### `TopologicalSorter.View.__bool__()`

> Returns `True` if more work can be done in the
> view--if there are nodes waiting to be yielded by
> `get_ready`, or waiting to be returned by `done`.
>
> Aliased to `TopologicalSorter.is_active` for compatibility
> with graphlib.

#### `TopologicalSorter.View.close()`

> Closes the view.  A closed view can no longer be used.

#### `TopologicalSorter.View.copy()`

> Returns a shallow copy of the view, duplicating its current state.

#### `TopologicalSorter.View.done(*nodes)`

> Marks nodes returned by `ready` as "done",
> possibly allowing additional nodes to be available
> from `ready`.

#### `TopologicalSorter.View.print(print=print)`

> Prints the internal state of the view, and its graph.
> Used for debugging.
>
> `print` is the function used for printing;
> it should behave identically to the builtin `print` function.

#### `TopologicalSorter.View.ready()`

> Returns a tuple of "ready" nodes--nodes with no
> predecessors, or nodes whose predecessors have all
> been marked "done".
>
> Aliased to `TopologicalSorter.get_ready` for
> compatibility with `graphlib`.

#### `TopologicalSorter.View.reset()`

> Resets the view to its initial state,
> forgetting all "ready" and "done" state.


## `big.heap`

Functions for working with heap objects.
Well, just one heap object really.

#### `Heap(i=None)`

> An object-oriented wrapper around the `heapq` library, designed to be
> easy to use--and easy to remember how to use.  The `heapq` library
> implements a [binary heap](https://en.wikipedia.org/wiki/Binary_heap),
> a data structure used for sorting;
> you add objects to the heap, and you can then remove
> objects in sorted order.  Heaps are useful because they have are efficient
> both in space and in time; they're also inflexible, in that iterating over
> the sorted items is destructive.
>
> Big's `Heap` API mimics the `list` and `collections.deque` objects;
> this way, all you need to remember is "it works kinda like a `list` object".
> You `append` new items to the heap, then `popleft` them off in sorted order.
>
> By default `Heap` creates an empty heap.  If you pass in an iterable `i`
> to the constructor, this is equivalent to calling the `extend(i)` on the
> freshly-constructed `Heap`.
>
> In addition to the below methods, `Heap` objects support iteration,
> `len`, the `in` operator, and use as a boolean expression.  You can
> also index or slice into a `Heap` object, which behaves as if the
> heap is a list of objects in sorted order.  Getting the first item
> (`Heap[0]`, aka *peek*) is cheap, the other operations can get very
> expensive.
>
> Methods on a `Heap` object:


#### `Heap.append(o)`

> Adds object `o` to the heap.

#### `Heap.clear()`

> Removes all objects from the heap,
> resetting it to empty.

#### `Heap.copy()`

> Returns a shallow copy of the heap.
> Only duplicates the heap data structures itself;
> does not duplicate the objects *in* the heap.

#### `Heap.extend(i)`

> Adds all the objects from the iterable `i` to the heap.

#### `Heap.remove(o)`

> If object `o` is in the heap, removes it.  If `o` is not
> in the heap, raises `ValueError`.

#### `Heap.popleft()`

> If the heap is not empty, returns the first item in the
> heap in sorted order.  If the heap is empty, raises `IndexError`.

#### `Heap.append_and_popleft(o)`

> Equivalent to calling `Heap.append(o)` immediately followed
> by `Heap.popleft()`.  If `o` is smaller than any other object
> in the heap at the time it's added, this will return `o`.

#### `Heap.popleft_and_append(o)`

> Equivalent to calling `Heap.popleft()` immediately followed
> by `Heap.append(o)`.  This method will *never* return `o`,
> unless `o` was already in the heap before the method was called.

#### `Heap.queue`

> Not a method, a property.  Returns a copy of the contents
> of the heap, in sorted order.


## `big.itertools`

Functions and classes for working with iteration.
Only one entry so far.

#### `PushbackIterator(iterable=None)`

> Wraps any iterator, allowing you to push items back on the iterator.
> This allows you to "peek" at the next item (or items); you can get the
> next item, examine it, and then push it back.  If any objects have
> been pushed onto the iterator, they are yielded first, before attempting
> to yield from the wrapped iterator.
>
> Pass in any `iterable` to the constructor.  Passing in an `iterable`
> of `None` means the `PushbackIterator` is created in an exhausted state.
>
> When the wrapped `iterable` is exhausted (or if you passed in `None`
> to the constructor) you can still call push to add new items, at which
> point the `PushBackIterator` can be iterated over again.
>
> In addition to the following methods, `PushbackIterator` supports
> the iterator protocol and testing for truth.  A `PushbackIterator`
> is true if iterating over it will yield at least one value.

#### `PushbackIterator.next(default=None)`

> Equivalent to `next(PushbackIterator)`,
> but won't raise `StopIteration`.
> If the iterator is exhausted, returns
> the `default` argument.

#### `PushbackIterator.push(o)`

> Pushes a value into the iterator's internal stack.
> When a `PushbackIterator` is iterated over, and there are
> any pushed values, the top value on the stack will be popped
> and yielded.  `PushbackIterator` only yields from the
> iterator it wraps when this internal stack is empty.


## `big.scheduler`

> A replacement for Python's `sched.scheduler` object,
> adding full threading support and a modern Python interface.
>
> Python's `sched.scheduler` object was a clever idea for the
> time.  It abstracted away the concept of time from its interface,
> allowing it to be adapted to new schemes of measuring time--including
> mock time used for testing.  Very nice!
>
> But unfortunately, `sched.scheduler` was designed in 1991--long
> before multithreading was common, years before threading support
> was added to Python.  Sadly its API isn't flexible enough to
> correctly handle some scenarios:
>
> * If one thread has called `sched.scheduler.run`,
>   and the next scheduled event will occur at time **T**,
>   and a second thread schedules a new event which
>   occurs at a time < **T**, `sched.scheduler.run` won't
>   return any events to the first thread until time **T**.
> * If one thread has called `sched.scheduler.run`,
>   and the next scheduled event will occur at time **T**,
>   and a second thread cancels all events,
>   `sched.scheduler.run` won't exit until time **T**.
>
> Also, `sched.scheduler` is thirty years behind the times in
> Python API design--its design predates many common modern
> Python conventions.  Its events are callbacks, which it
> calls directly.  `Scheduler` fixes this: its events are
> objects, and you iterate over the `Scheduler` object to receive
> events as they become due.
>
> `Scheduler` also benefits from thirty years of improvements
> to `sched.scheduler`.  In particular, big reimplements the
> bulk of the `sched.scheduler` test suite, to ensure that
> `Scheduler` never repeats the historical problems discovered
> over the lifetime of `sched.scheduler`.

#### `Scheduler(regulator=None)`

> Implements a thread-safe scheduler.  The only argument is the
> "regulator" object to use; the regulator abstracts away all
> time-related details for the scheduler.  By default `Scheduler`
> creates a new `Scheduler.Regulator` object and uses that.
>
> In addition to the below methods, `Scheduler` objects support
> being evaluated in a boolean context (they are true if they
> contain any events), and they support being iterated over.
> Iterating over a `Scheduler` object blocks until the next
> event comes due, at which point the `Scheduler` yields that
> event.  An empty `Scheduler` that is iterated over raises
> `StopIteration`.  You can reuse `Scheduler` objects, iterating
> over them until empty, then adding more objects and iterating
> over them again.

#### `Scheduler.schedule(o, time, *, absolute=False, priority=DEFAULT_PRIORITY)`

> Schedules an object `o` to be yielded as an event by this `schedule` object
> at some time in the future.
>
> By default the `time` value is a relative time value,
> and is added to the current time; using a `time` value of 0
> should schedule this event to be yielded immediately.
>
> If `absolute` is true, `time` is regarded as an absolute time value.
>
> If multiple events are scheduled for the same time, they will
> be yielded by order of `priority`.  Lowever values of
> `priority` represent higher priorities.  The default value
> is `Scheduler.DEFAULT_PRIORITY`, which is 100.  If two events
> are scheduled for the same time, and have the same priority,
> `Scheduler` will yield the events in the order they were added.
>
> Returns an `Event` object, which can be used to cancel the event.

#### `Scheduler.cancel(event)`

> Cancels a scheduled event.  `event` must be an object
> returned by this `Scheduler` object.  If `event` is not
> currently scheduled in this `Scheduler` object,
> raises `ValueError`.

#### `Scheduler.queue`

> A property, not a method.  Returns a list of the
> current `Event` objects in the scheduler, in order
> that they will be yielded.

#### `Scheduler.non_blocking()`

> Returns an iterator for the events in the
> `Scheduler` that only yields the events that
> are currently due.  Never blocks; if the next
> event is not due yet, raises `StopIteration`.

#### `Scheduler.Event(time, priority, sequence, event, scheduler)`

> An object representing a scheduled event in a `Scheduler`.
> You shouldn't need to create them manually; `Event` objects
> are created automatically when you add events to a `Scheduler`.
>
> Supports one method:

#### `Scheduler.Event.cancel()`

> Cancels this event.  If this event has already been canceled,
> raises `ValueError`.

#### `Scheduler.Regulator(scheduler)`

> Creates a regulator object for use with a `Scheduler`.
> Measures time using the `time.monotonic` clock, and
> sleeps using a `threading.Event` object.
> Time values are expressed in seconds, either integer
> or floating point.
>
> You can write your own regulator class and use it with
> `Scheduler`; it must implement the three following methods.

#### `Scheduler.Regulator.now()`

> Returns a "time value", an object representing the
> current time. The object returned must support
> simple arithmetic operations (`+` and `-`) and
> rich comparison with other time values.

#### `Scheduler.Regulator.sleep(t)`

> Sleeps for a period of time expressed as a
> relative "time value".  Note that `sleep` must
> be interruptable with the `wake` method.

#### `Scheduler.Regulator.wake()`

> Wakes up *all* threads that are current sleeping
> using `Scheduler.Regulator.sleep(t)`.  All calls
> to `sleep` on this `Regulator` object must return
> immediately.

## `big.text`

> Functions for working with text strings.  There are
> several families of functions inside the `text` module;
> for a higher-level view of those families, read the
> following deep-dives:
>
> * [**The `multi-` family of functions**](#The-multi--family-of-functions)
> * [**`lines` and lines modifier functions**](#lines-and-lines-modifier-functions)
> * [**Word wrapping and formatting**](#word-wrapping-and-formatting)
>
> All the functions in `big.text` will work with either
> `str` or `bytes` objects, except the three
> [**Word wrapping and formatting**](#word-wrapping-and-formatting)
> functions.  When working with `bytes`,
> by default the functions will only work with ASCII
> characters.

#### `gently_title(s, *, apostrophes=None, double_quotes=None)`

> Uppercase the first character of every word in `s`.
> Leave the other letters alone.  s should be `str` or `bytes`.
>
> (For the purposes of this algorithm, words are
> any blob of non-whitespace characters.)
>
> Capitalize the letter after an apostrophe if
>
>     a) the apostrophe is after whitespace or a
>        left parenthesis character (`'('`)
>        (or is the first letter of the string), or
>
>     b) if the apostrophe is after a letter O or D,
>        and that O or D is after whitespace (or is
>       the first letter of the string).  The O or D
>        here will also be capitalized.
>
> Rule a) handles internally quoted strings:
>
>     He Said 'No I Did Not'
>
> and contractions that start with an apostrophe
>
>     'Twas The Night Before Christmas
>
> Rule b) handles certain Irish, French, and Italian
> names.
>
>     Peter O'Toole
>     Lord D'Arcy
>
> Capitalize the letter after a quote mark if
> the quote mark is after whitespace (or is the
> first letter of a string).
>
> A run of consecutive apostrophes and/or
> quote marks is considered one quote mark for
> the purposes of capitalization.
>
> If specified, `apostrophes` should be a `str`
> or `bytes` object containing characters that
> should be considered apostrophes.  If `apostrophes`
> is false, and `s` is `bytes`, `apostrophes` is set to `"'"`.
> If `apostrophes` is false and s is `str`, `apostrophes`
> is set to a string containing these Unicode apostrophe code points:
>     '‘’‚‛
>
> If specified, `double_quotes` should be a `str`
> or `bytes` object containing characters that
> should be considered double-quote characters.
> If `double_quotes` is false, and `s` is `bytes`,
> `double_quotes` is set to "'".
> If `double_quotes` is false and `s` is `str`, double_quotes
> is set to a string containing these Unicode double quote code points:
>     "“”„‟«»‹›

#### `lines(s, separators=None, *, line_number=1, column_number=1, tab_width=8, **kwargs)`

> A "lines iterator" object.  Splits s into lines, and iterates yielding those lines.
>
> `s` can be `str`, `bytes`, or any iterable.
>
> By default, if `s` is `str`, splits `s` by all Unicode line break characters.
> If `s` is `bytes`, splits `s` by all ASCII line break characters.
>
> If `s` is neither str nor bytes, `s` must be an iterable;
> lines yields successive elements of `s` as lines.
>
> `separators`, if not `None`, must be an iterable of strings of the
> same type as `s`.  `lines` will split `s` using those strings as
> separator strings (using [`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)).
>
> When iterated over, yields 2-tuples:
>     (info, line)
>
> `info` is a `LineInfo` object, which contains three fields by
> default:
>
> * `line` - the original line, never modified
> * `line_number` - the line number of this line, starting at the
> `line_number` passed in and adding 1 for each successive line
> * `column_number` - the column this line starts on,
> starting at the `column_number` passed in, and adjusted when
> characters are removed from the beginning of `line`
>
> `tab_width` is not used by `lines` itself, but is stored
> internally and may be used by other lines modifier functions
> (e.g. `lines_convert_tabs_to_spaces`). Similarly, all keyword
> arguments passed in via `kwargs` are stored internally and can
> be accessed by user-defined lines modifier functions.
>
> For more information, see the deep-dive on [**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)

#### `LineInfo(line, line_number, column_number, **kwargs)`

> The info object yielded by a [`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs) iterator.
> You can add your own fields by passing them in
> via `**kwargs`; you can also add new attributes
> or modify existing attributes as needed from
> inside a "lines modifier" function.
>
> For more information, see the deep-dive on [**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)


#### `lines_convert_tabs_to_spaces(li)`

> A lines modifier function.  Converts tabs to spaces for the lines
> of a "lines iterator", using the `tab_width` passed in to [`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs).
>
> For more information, see the deep-dive on [**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)

#### `lines_filter_comment_lines(li, comment_separators)`

> A lines modifier function.  Filters out comment lines from the
> lines of a "lines iterator".  Comment lines are lines whose
> first non-whitespace characters appear in the iterable of
> `comment_separators` strings passed in.
>
> What's the difference between
> [`lines_strip_comments`](#lines_strip_commentsli-comment_separators--quotes--backslash-rstriptrue-triple_quotestrue)
> and
> [`lines_filter_comment_lines`](#lines_filter_comment_linesli-comment_separators)?
>
>  * [`lines_filter_comment_lines`](#lines_filter_comment_linesli-comment_separators)
>    only recognizes lines that
>    *start* with a comment separator (ignoring leading
>    whitespace).  Also, it filters out those lines
>    completely, rather than modifying the line.
>  * [`lines_strip_comments`](#lines_strip_commentsli-comment_separators--quotes--backslash-rstriptrue-triple_quotestrue)
>    handles comment characters
>    anywhere in the line, although it can ignore
>    comments inside quoted strings.  It truncates the
>    line but still always yields the line.
>
> For more information, see the deep-dive on [**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)

#### `lines_containing(li, s, *, invert=False)`

> A lines modifier function.  Only yields lines
> that contain `s`.  (Filters out lines that
> don't contain `s`.)
>
> If `invert` is true, returns the opposite--
> filters out lines that contain `s`.
>
> For more information, see the deep-dive on [**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)

#### `lines_grep(li, pattern, *, invert=False, flags=0)`

> A lines modifier function.  Only yields lines
> that match the regular expression `pattern`.
> (Filters out lines that don't match `pattern`.)
>
> `pattern` can be `str`, `bytes`, or an `re.Pattern` object.
> If `pattern` is not an `re.Pattern` object, it's compiled
> with `re.compile(pattern, flags=flags)`.
>
> If `invert` is true, returns the opposite--
> filters out lines that match `pattern`.
>
> For more information, see the deep-dive on [**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)
>
> (In older versions of Python, `re.Pattern` was a private type called
> `re._pattern_type`.)

#### `lines_rstrip(li)`

> A lines modifier function.  Strips trailing whitespace from the
> lines of a "lines iterator".
>
> For more information, see the deep-dive on [**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)

#### `lines_sort(li, *, reverse=False)`

> A lines modifier function.  Sorts all
> input lines before yielding them.
>
> Lines are sorted lexicographically,
> from lowest to highest.
> If `reverse` is true, lines are sorted
> from highest to lowest.

#### `lines_strip(li)`

> A lines modifier function.  Strips leading and trailing whitespace
> from the lines of a "lines iterator".
>
> If `lines_strip` removes leading whitespace from a line, it adds
> a field to the associated `LineInfo` object:
>
> * `leading` - the leading whitespace string that was removed
>
> For more information, see the deep-dive on [**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)

#### `lines_strip_comments(li, comment_separators, *, quotes=('"', "'"), backslash='\\', rstrip=True, triple_quotes=True)`

> A lines modifier function.  Strips comments from the lines
> of a "lines iterator".  Comments are substrings that indicate
> the rest of the line should be ignored; `lines_strip_comments`
> truncates the line at the beginning of the leftmost comment
> separator.
>
> If `rstrip` is true (the default), `lines_strip_comments` calls
> the `rstrip()` method on `line` after it truncates the line.
>
> If `quotes` is true, it must be an iterable of quote characters.
> (Each quote character *must* be a single character.)
> `lines_strip_comments` will parse the line and ignore comment
> characters inside quoted strings.  If `quotes` is false,
> quote characters are ignored and `line_strip_comments` will truncate
> anywhere in the line.
>
> `backslash` and `triple_quotes` are passed in to
> `split_quoted_string`, which is used internally to detect the quoted
> strings in the line.
>
> Sets a new field on the associated `LineInfo` object for every line:
>
>  * `comment` - the comment stripped from the line, if any.
>     if no comment was found, `comment` will be an empty string.
>
> What's the difference between
> [`lines_strip_comments`](#lines_strip_commentsli-comment_separators--quotes--backslash-rstriptrue-triple_quotestrue)
> and
> [`lines_filter_comment_lines`](#lines_filter_comment_linesli-comment_separators)?
>
>  * [`lines_filter_comment_lines`](#lines_filter_comment_linesli-comment_separators)
>    only recognizes lines that
>    *start* with a comment separator (ignoring leading
>    whitespace).  Also, it filters out those lines
>    completely, rather than modifying the line.
>  * [`lines_strip_comments`](#lines_strip_commentsli-comment_separators--quotes--backslash-rstriptrue-triple_quotestrue)
>    handles comment characters
>    anywhere in the line, although it can ignore
>    comments inside quoted strings.  It truncates the
>    line but still always yields the line.
>
> For more information, see the deep-dive on [**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)


#### `lines_strip_indent(li)`

> A lines modifier function.  Automatically measures and strips indents.
>
> Sets two new fields on the associated `LineInfo` object for every line:
>
> * `indent` - an integer indicating how many indents it's observed
> * `leading` - the leading whitespace string that was removed
>
> Uses an intentionally simple algorithm.
> Only understands tab and space characters as indent characters.
> Internally detabs to spaces first for consistency, using the
> `tab_width` passed in to lines.
>
> You can only dedent out to a previous indent.
> Raises `IndentationError` if there's an illegal dedent.
>
> For more information, see the deep-dive on [**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)

#### `merge_columns(*columns, column_separator=" ", overflow_response=OverflowResponse.RAISE, overflow_before=0, overflow_after=0)`

> Merge n column tuples, with each column tuple being
> formatted into its own column in the resulting string.
> Returns a string.
>
> `columns` should be an iterable of column tuples.
> Each column tuple should contain three items:
> ```Python
>     (text, min_width, max_width)
> ```
> `text` should be a single text string, with newline
> characters separating lines. `min_width` and `max_width`
> are the minimum and maximum permissible widths for that
> column, not including the column separator (if any).
>
> Note that this function does not text-wrap the lines.
>
> `column_separator` is printed between every column.
>
> `overflow_strategy` tells merge_columns how to handle a column
> with one or more lines that are wider than that column's `max_width`.
> The supported values are:
>
> * `OverflowStrategy.RAISE`: Raise an OverflowError.  The default.
> * `OverflowStrategy.INTRUDE_ALL`: Intrude into all subsequent columns
>   on all lines where the overflowed column is wider than its `max_width`.
> * `OverflowStrategy.DELAY_ALL`: Delay all columns after the overflowed
>   column, not beginning any until after the last overflowed line
>   in the overflowed column.
>
> When `overflow_strategy` is `INTRUDE_ALL` or `DELAY_ALL`, and
> either `overflow_before` or `overflow_after` is nonzero, these
> specify the number of extra lines before or after
> the overflowed lines in a column.
>
> For more information, see the deep-dive on
> [**Word wrapping and formatting.**](#word-wrapping-and-formatting)

#### `multipartition(s, separators, count=1, *, reverse=False, separate=True)`

> Like `str.partition`, but supports partitioning based on multiple
> separator strings, and can partition more than once.
>
> `s` can be str or bytes.
>
> `separators` should be an iterable of str or bytes, matching `s`.
>
> By default, if any of the strings in `separators` are found in `s`,
> returns a tuple of three strings: the portion of `s` leading up to
> the earliest separator, the separator, and the portion of `s` after
> that separator.  Example:
>
>     multipartition('aXbYz', ('X', 'Y')) => ('a', 'X', 'bYz')
>
> If none of the separators are found in the string, returns
> a tuple containing `s` unchanged followed by two empty strings.
>
> Passing in an explicit `count` lets you control how many times
> `multipartition` partitions the string.  `multipartition` will always
> return a tuple containing `(2*count)+1` elements.
> Passing in a `count` of 0 will always return a tuple containing `s`.
>
> If `separate` is true, multiple adjacent separator strings behave
> like one separator.  Example:
>
>     multipartition('aXYbXYc', ('X', 'Y',), separate=True) => ('a', 'XY', 'bXYc')
>
> If `reverse` is true, multipartition behaves like `str.rpartition`.
> It partitions starting on the right, scanning backwards through slooking
> for separators.
>
> For more information, see the deep-dive on [**The `multi-` family of functions.**](#The-multi--family-of-functions)

#### `multisplit(s, separators, *, keep=False, maxsplit=-1, reverse=False, separate=False, strip=False)`

> Splits strings like `str.split`, but with multiple separators and options.
>
> `s` can be `str` or `bytes`.
>
> `separators` should be an iterable.  Each element of `separators`
> should be the same type as `text`.  If `separators` is a string or bytes
> object, `multisplit` behaves as separators is a tuple containing each
> individual character.
>
> Returns an iterator yielding the strings split from `s`.  If `keep`
> is true (or `ALTERNATING`), and `strip` is false, joining these strings
> together will recreate `s`.
>
> `keep` indicates whether or not multisplit should preserve the separator
> strings in the strings it yields.  It supports four values:
>
>       false (the default)
>            Discard the separators.
>       true (apart from ALTERNATING and AS_PAIRS)
>            Append the separators to the end of the split strings.
>            You can recreate the original string by passing the
>            list returned in to "".join .
>       ALTERNATING
>            Yield alternating strings in the output: strings consisting
>            of separators, alternating with strings consisting of
>            non-separators.  If "separate" is true, separator strings
>            will contain exactly one separator, and non-separator strings
>            may be empty; if "separate" is false, separator strings will
>            contain one or more separators, and non-separator strings
>            will never be empty, unless "s" was empty.
>            You can recreate the original string by passing the
>            list returned in to "".join .
>       AS_PAIRS
>            Yield 2-tuples containing a non-separator string and its
>            subsequent separator string.  Either string may be empty;
>            the separator string in the last 2-tuple will always be
>            empty, and if "s" ends with a separator string, *both*
>            strings in the final 2-tuple will be empty.
>
> `separate` indicates whether multisplit should consider adjacent
> separator strings in `s` as one separator or as multiple separators
> each separated by a zero-length string.  It supports two values:
>
>        false (the default)
>            Multiple adjacent separators should behave as if they
>            are one big separator.
>        true
>            Don't group separators together.  Each separator should
>            split the string individually, even if there are no
>            characters between two separators.
>
> `strip` indicates whether multisplit should strip separators from
> the beginning and/or end of `s`.  It supports six values:
>
>        false (the default)
>            Don't strip separators from the beginning or end of "s".
>        true (apart from LEFT, RIGHT, and PROGRESSIVE)
>            Strip separators from the beginning and end of "s"
>            (similarly to `str.strip`).
>        LEFT
>            Strip separators only from the beginning of "s"
>            (similarly to `str.lstrip`).
>        RIGHT
>            Strip separators only from the end of "s"
>            (similarly to `str.rstrip`).
>        PROGRESSIVE
>            Strip from the beginning and end of "s", unless "maxsplit"
>            is nonzero and the entire string is not split.  If
>            splitting stops due to "maxsplit" before the entire string
>            is split, and "reverse" is false, don't strip the end of
>            the string. If splitting stops due to "maxsplit" before
>            the entire string is split, and "reverse" is true, don't
>            strip the beginning of the string.  (This is how str.strip
>            and str.rstrip behave when you pass in sep=None .)
>
> `maxsplit` should be either an integer or `None`.  If `maxsplit` is an
> integer greater than -1, multisplit will split `text` no more than
> `maxsplit` times.
>
> `reverse` changes where `multisplit` starts splitting the string, and
> what direction it moves through the string when parsing.
>
>        false (the default)
>            Start splitting from the beginning of the string
>            and parse moving right (towards the end).
>        true
>            Start splitting from the end of the string and
>            parse moving left (towards the beginning).
>
>    Splitting starting from the end of the string and parsing to
>    the left has two effects.  First, if `maxsplit` is a number
>    greater than 0, the splits will start at the end of the string
>    rather than the beginning.  Second, if there are overlapping
>    instances of separators in the string, `multisplit` will prefer
>    the rightmost separator rather than the left.  For example:
>
>        multisplit(" x x ", (" x ",), keep=big.ALTERNATING)
>
>    will split on the leftmost instance of `" x "`, yielding
>
>        "", " x ", "x "
>
>    whereas
>
>        multisplit(" x x ", (" x ",), keep=big.ALTERNATING, reverse=True)
>
>    will split on the rightmost instance of `" x "`, yielding
>
>        " x", " x ", ""
>
> For more information, see the deep-dive on [**The `multi-` family of functions.**](#The-multi--family-of-functions)

#### `multistrip(s, separators, left=True, right=True)`

> Like `str.strip`, but supports stripping multiple substrings from `s`.
>
> Strips from the string `s` all leading and trailing instances of strings
> found in `separators`.
>
> `s` should be str or bytes.
>
> `separators` should be an iterable of either `str` or `bytes`
> objects matching the type of `s`.
>
> If `left` is a true value, strips all leading separators
> from `s`.
>
> If `right` is a true value, strips all trailing separators
> from `s`.
>
> Processing always stops at the first character that
> doesn't match one of the separators.
>
> Returns a copy of `s` with the leading and/or trailing
> separators stripped.  (If `left` and `right` are both
> false, returns `s` unchanged.)
>
> For more information, see the deep-dive on [**The `multi-` family of functions.**](#The-multi--family-of-functions)


#### `newlines`

> A list of all newline characters recognized by Python.
> Includes many Unicode newline characters, like `'\u2029'`
> (a paragraph separator).  Useful as a list of separator
> strings for `[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)` et al; `newlines` is specifically
> used by the [`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs) iterator constructor.
>
> **big** also defines `utf8_newlines`, which is `newlines`
> with all strings encoded to UTF-8 (as bytes),
> and `ascii_newlines`, with all strings converted into
> bytes and all characters with code points greater than
> 128 discarded.
>
> Note that `newlines` contains `'\r\n'`, the DOS sequence
> of characters representing a newline.  This lets **big**
> text-processing functions recognize this sequence as a
> *single* newline marker, rather than as two *separate*
> newline characters.  If you don't want this behavior,
> you can use `newlines_without_dos` instead;
> **big** also provides `utf8_newlines_without_dos` and
> `ascii_newlines_without_dos`.


#### `normalize_whitespace(s, separators=None, replacement=None)`

> Returns `s`, but with every run of consecutive
> separator characters turned into a replacement string.
> By default turns all runs of consecutive whitespace
> characters into a single space character.
>
> `s` may be `str` or `bytes`.
> `separators` should be an iterable of either `str` or `bytes`
> objects, matching `s`.
> `replacement` should be either a `str` or `bytes` object,
> also matching `s`, or `None` (the default).
> If `replacement` is `None`, `normalize_whitespace` will use
> a replacement string consisting of a single space character,
> either `str` or `bytes` as appropriate.)
>
> Leading or trailing runs of separator characters will
> be replaced with the replacement string, e.g.:
>
>     normalize_whitespace("   a    b   c") == " a b c"

#### `re_partition(text, pattern, count=1, *, flags=0, reverse=False)`

> Like `str.partition`, but `pattern` is matched as a regular expression.
>
> `text` can be a string or a bytes object.
>
> `pattern` can be a string, bytes, or an `re.Pattern` object.
>
> `text` and `pattern` (or `pattern.pattern`) must be the same type.
>
> If `pattern` is found in text, returns a tuple
> ```Python
>     (before, match, after)
> ```
> where `before` is the text before the matched text,
> `match` is the `re.Match` object resulting from the match, and
> `after` is the text after the matched text.
>
> If `pattern` appears in `text` multiple times,
> `re_partition` will match against the first (leftmost)
> appearance.
>
> If `pattern` is not found in `text`, returns a tuple
> ```Python
>     (text, None, '')
> ```
> where the empty string is `str` or `bytes` as appropriate.
>
> Passing in an explicit `count` lets you control how many times
> `re_partition` partitions the string.  `re_partition` will always
> return a tuple containing `(2*count)+1` elements, and
> odd-numbered elements will be either `re.Match` objects or `None`.
> Passing in a `count` of 0 will always return a tuple containing `s`.
>
> If `pattern` is a string or bytes object, `flags` is passed in
> as the `flags` argument to `re.compile`.
>
> If `reverse` is true, partitions starting at the right,
> like [`re_rpartition`](#re_rpartitiontext-pattern-count1--flags0).
>
> (In older versions of Python, `re.Pattern` was a private type called
> `re._pattern_type`.)


#### `re_rpartition(text, pattern, count=1, *, flags=0)`

> Like `str.rpartition`, but `pattern` is matched as a regular expression.
>
> `text` can be a string or a bytes object.
>
> `pattern` can be a string, bytes, or an `re.Pattern` object.
>
> `text` and `pattern` (or `pattern.pattern`) must be the same type.
>
> If `pattern` is found in `text`, returns a tuple
> ```Python
>     (before, match, after)
> ```
> where `before` is the text before the matched text,
> `match` is the re.Match object resulting from the match, and
> `after` is the text after the matched text.
>
> If `pattern` appears in `text` multiple times,
> `re_partition` will match against the last (rightmost)
> appearance.
>
> If `pattern` is not found in `text`, returns a tuple
> ```Python
>     ('', None, text)
> ```
> where the empty string is `str` or `bytes` as appropriate.
>
> Passing in an explicit `count` lets you control how many times
> `re_rpartition` partitions the string.  `re_rpartition` will always
> return a tuple containing `(2*count)+1` elements, and
> odd-numbered elements will be either `re.Match` objects or `None`.
> Passing in a `count` of 0 will always return a tuple containing `s`.
>
> If `pattern` is a string, `flags` is passed in
> as the `flags` argument to `re.compile`.
>
> (In older versions of Python, `re.Pattern` was a private type called
> `re._pattern_type`.)

#### `split_quoted_strings(s, quotes=('"', "'"), *, triple_quotes=True, backslash='\\')`

> Splits s into quoted and unquoted segments.  Returns an iterator yielding 2-tuples:
>     (is_quoted, segment)
> where `segment` is a substring of `s`, and `is_quoted` is true if the segment is
> quoted.  Joining all the segments together recreates `s`.
>
> `quotes` is an iterable of quote separators.  Note that `split_quoted_strings`
> only supports quote *characters,* as in, each quote separator must be exactly
> one character long.
>
> If `triple_quotes` is true, supports "triple-quoted" strings like Python.
>
> If `backslash` is a character, this character will quoting characters inside
> a quoted string, like the backslash character inside strings in Python.

#### `split_text_with_code(s, *, tab_width=8, allow_code=True, code_indent=4, convert_tabs_to_spaces=True)`

> Splits the string `s` into individual words,
> suitable for feeding into
> [`wrap_words`](#wrap_wordswords-margin79--two_spacestrue).
>
> Paragraphs indented by less than `code_indent` will be
> broken up into individual words.
>
> If `allow_code` is true, paragraphs indented by at least
> `code_indent` spaces will preserve their whitespace:
> internal whitespace is preserved, and the newline is
> preserved.  (This will preserve the formatting of code
> examples when these words are rejoined into lines by
> [`wrap_words`](#wrap_wordswords-margin79--two_spacestrue).)
>
> For more information, see the deep-dive on
> [**Word wrapping and formatting.**](#word-wrapping-and-formatting)


#### `whitespace`

> A list of all whitespace characters recognized by Python.
> Includes many Unicode whitespace strings, like `'\xa0'`
> (a non-breaking space).  Useful as a list of separator
> strings for `[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)` et al.
>
> **big** also defines `utf8_whitespace`, which is `whitespace`
> with all strings encoded to UTF-8 (as bytes),
> and `ascii_whitespace`, with all strings converted into
> bytes and all characters with code points greater than
> 128 discarded.
>
> Note that `whitespace` contains `'\r\n'`, the DOS sequence
> of characters representing a newline.  This lets **big**
> text-processing functions recognize this sequence as a
> *single* whitespace marker, rather than as two *separate*
> whitespace characters.  If you don't want this behavior,
> you can use `whitespace_without_dos` instead;
> **big** also provides `utf8_whitespace_without_dos` and
> `ascii_whitespace_without_dos`.

#### `wrap_words(words, margin=79, *, two_spaces=True)`

> Combines `words` into lines and returns the result as a string.
> Similar to `textwrap.wrap`.
>
> `words` should be an iterator containing text split at word
> boundaries.  Example:
> ```Python
>      "this is an example of text split at word boundaries".split()
> ```
>
> A single `'\n'` indicates a line break.
> If you want a paragraph break, embed two `'\n'` characters in a row.
>
> `margin` specifies the maximum length of each line. The length of
> every line will be less than or equal to `margin`, unless the length
> of an individual element inside `words` is greater than `margin`.
>
> If `two_spaces` is true, elements from `words` that end in
> sentence-ending punctuation (`'.'`, `'?'`, and `'!'`)
> will be followed by two spaces, not one.
>
> Elements in `words` are not modified; any leading or trailing
> whitespace will be preserved.  You can use this to preserve
> whitespace where necessary, like in code examples.
>
> For more information, see the deep-dive on
> [**Word wrapping and formatting.**](#word-wrapping-and-formatting)


## `big.time`

Functions for working with time.  Currently deals specifically
with timestamps.  The time functions in **big** are designed
to make it easy to use best practices.

#### `date_ensure_timezone(d, timezone)`

> Ensures that a `datetime.date` object has
> a timezone set.
>
> If `d` has a timezone set, returns `d`.
> Otherwise, returns a new `datetime.date`
> object equivalent to `d` with its `tzinfo` set
> to `timezone`.

#### `date_set_timezone(d, timezone)`

> Returns a new `datetime.date` object identical
> to `d` but with its `tzinfo` set to `timezone`.

#### `datetime_ensure_timezone(d, timezone)`

> Ensures that a `datetime.datetime` object has
> a timezone set.
>
> If `d` has a timezone set, returns `d`.
> Otherwise, creates a new `datetime.datetime`
> object equivalent to `d` with its `tzinfo` set
> to `timezone`.

#### `datetime_set_timezone(d, timezone)`

> Returns a new `datetime.datetime` object identical
> to `d` but with its `tzinfo` set to `timezone`.

#### `parse_timestamp_3339Z(s, *, timezone=None)`

> Parses a timestamp string returned by `timestamp_3339Z`.
> Returns a `datetime.datetime` object.
>
> `timezone` is an optional default timezone, and should
> be a `datetime.tzinfo` object (or `None`).  If provided,
> and the time represented in the string doesn't specify
> a timezone, the `tzinfo` attribute of the returned object
> will be explicitly set to `timezone`.

#### `timestamp_3339Z(t=None, want_microseconds=None)`

> Return a timestamp string in RFC 3339 format, in the UTC
> time zone.  This format is intended for computer-parsable
> timestamps; for human-readable timestamps, use `timestamp_human()`.
>
> Example timestamp: `'2022-05-25T06:46:35.425327Z'`
>
> `t` may be one of several types:
>
> - If `t` is None, `timestamp_3339Z` uses the current time in UTC.
> - If `t` is an int or a float, it's interpreted as seconds
> since the epoch in the UTC time zone.
> - If `t` is a `time.struct_time` object or `datetime.datetime`
> object, and it's not in UTC, it's converted to UTC.
> (Technically, `time.struct_time` objects are converted to GMT,
> using `time.gmtime`.  Sorry, pedants!)
>
> If `want_microseconds` is true, the timestamp ends with
> microseconds, represented as a period and six digits between
> the seconds and the `'Z'`.  If `want_microseconds`
> is `false`, the timestamp will not include this text.
> If `want_microseconds` is `None` (the default), the timestamp
> ends with microseconds if the type of `t` can represent
> fractional seconds: a float, a `datetime` object, or the
> value `None`.

#### `timestamp_human(t=None, want_microseconds=None)`

> Return a timestamp string formatted in a pleasing way
> using the currently-set local timezone.  This format
> is intended for human readability; for computer-parsable
> time, use `timestamp_3339Z()`.
>
> Example timestamp: `"2022/05/24 23:42:49.099437"`
>
> `t` can be one of several types:
>
> - If `t` is `None`, `timestamp_human` uses the current local time.
> - If `t` is an int or float, it's interpreted as seconds since the epoch.
> - If `t` is a `time.struct_time` or `datetime.datetime` object,
> it's converted to the local timezone.
>
> If `want_microseconds` is true, the timestamp will end with
> the microseconds, represented as ".######".  If `want_microseconds`
> is false, the timestamp will not include the microseconds.
> If `want_microseconds` is `None` (the default), the timestamp
> ends with microseconds if the type of `t` can represent
> fractional seconds: a float, a `datetime` object, or the
> value `None`.

# Topic deep-dives

## The `multi-` family of functions

This family of functions was inspired by Python's `str.strip`,
`str.rstrip`, and `str.splitlines` functions.  These functions
are well-designed, and often do what you want.  But they're
all surprisingly opinionated.  And... what if your use case
doesn't fit exactly into their narrow viewpoints?  `str.strip`
supports two distinct modes of operation; if you want
to split your string in a third, slightly different way, you
probably just can't use `str.strip`.
So what *can* you use?  There's `re.strip`, but it can be
hard to use.  Now there's a new answer:
[`multisplit`.](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)

The goal of
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
is to be the be-all end-all text
splitting function.  You pass in the string you want to split,
and an iterable containing the separator strings you want to
split on.  It returns an iterator yielding the split strings.
It's designed to replace every mode of operation for
`str.split`, `str.rstrip`, and `str.splitlines`, and it
can even be used to replace `str.partition` and `str.rpartition`
too.

The cornerstone of [`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
is the `separators` argument.
This is an iterable of strings, of the same type (`str` or `bytes`)
as the string you want to split (`s`).  `multisplit` will split
the string at *each* non-overlapping instance of any string
specified in `separators`.

But
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
also let you fine-tune how it splits, through five keyword-only
parameters:

* `keep` lets you include the separator strings in the output,
  in a number of different formats.
* `separate` lets you specify whether adjacent separator strings
  should be grouped together (like `str.strip` operating on
  whitespace) or regarded as separate (like `str.strip` when
  you pass in an explicit `sep` separator).
* `strip` lets you strip separator strings from the beginning,
  end, or both ends of the string you're splitting.  It also
  supports a special *progressive* mode that duplicates the
  behavior of `str.strip` when you use `None` as the separator.
* `maxsplit` lets you specify the maximum number of times to
  split the string (like the `maxsplit` argument to `str.strip`).
* `reverse` lets you apply `maxsplit` to the end of the string
  and splitting backwards (like using `str.rstrip` instead of
  `str.strip`).

To make it slightly easier to remember, all these keyword-only
parameters default to a false value.  (Well, technically,
`maxsplit` defaults to its special value `-1`, but this is its
special "don't do anything" magic value.  All the other keyword-only
parameters default to `False`.)

[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
also inspired [`multistrip`](#multistrips-separators-leftTrue-rightTrue)
 and [`multipartition`,](#multipartitions-separators-count1--reverseFalse-separateTrue)
which also take this same `separators` arguments.  There are
other **big** functions that take a `separators` argument, and the
parameter name always has the word `separators` in it.
(For example, `comment_separators` for `lines_filter_comment_lines`.)

The downside of [`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
is that, since it *is* so
sophisticated and tunable, it can be hard to use.  It takes
*five keyword-only parameters* after all.  However, these
are designed to be reasonably memorable, and they all default
to `False`.  But the best way to combat the complexity of calling
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
is to use it as a building block for your own, presumably easier-to-use,
text splitting functions.  For example,
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
is used to implement [`multipartition`,](#multipartitions-separators-count1--reverseFalse-separateTrue)
`normalize_whitespace`,  and [`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs),
and several others.

### Demonstrations of each `multisplit` keyword-only parameter

To give you a sense of how you can use
[`multisplit`,](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
here's a breakdown of each of the five keyword-only parameters, with examples.

#### `maxsplit`

`maxsplit` specifies the maximum number of times the string should be split.
The default value of `-1` means "split as many times as you can".  In our
example here, the string can be split a maximum of three times.  Therefore,
specifying a `maxsplit` of `-1` is equivalent to specifying a `maxsplit` of
`2` or greater:

    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y')))
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), maxsplit=0))
    ['appleXbananaYcookie']
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), maxsplit=1))
    ['apple', 'bananaYcookie']
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), maxsplit=2))
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), maxsplit=3))
    ['apple', 'banana', 'cookie']

#### `keep`

`keep` indicates whether or not multisplit should preserve the separator
strings in the strings it yields.  It supports four values: false, true,
and the special values `ALTERNATING` and `AS_PAIRS`.

    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y')))
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), keep=False))
    ['apple', 'banana', 'cookie']

When `keep` is true, `multisplit` keeps the separators, appending them to
the end of the separated string:

    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), keep=True))
    ['appleX', 'bananaY', 'cookie']

When `keep` is `ALTERNATING`, `multisplit` keeps the separators as separate
strings.  The first string yielded is always a non-separator string, and
from then on it always alternates between a separator string and a non-separator
string.  Put another way, if you store the output of `multisplit` in a list,
entries with an even-numbered index (0, 2, 4, ...) are always non-separator strings,
and entries with an odd-numbered index (1, 3, 5, ...) are always separator strings.

    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), keep=big.ALTERNATING))
    ['apple', 'X', 'banana', 'Y', 'cookie']

Finally, when `keep` is `AS_PAIRS`,  `multisplit` keeps the separators as separate
strings.  But instead of yielding strings, it yields 2-tuples of strings.  Every
2-tuple contains a non-separator string followed by a separator string.

If the original string doesn't end with a separator, or if `strip` is set to a
value that means the string is stripped to the right, the last 2-tuple will
contain an empty separator string:

    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), keep=big.AS_PAIRS))
    [('apple', 'X'), ('banana', 'Y'), ('cookie', '')]
    >>> list(big.multisplit('appleXbananaYcookieXXX', ('X', 'Y'), keep=big.AS_PAIRS, strip=True))
    [('apple', 'X'), ('banana', 'Y'), ('cookie', '')]

If the original string starts with a separator, the first 2-tuple will contain
an empty non-separator string:

    >>> list(big.multisplit('YappleXbananaYcookie', ('X', 'Y'), keep=big.AS_PAIRS))
    [('', 'Y'), ('apple', 'X'), ('banana', 'Y'), ('cookie', '')]

Sometimes `AS_PAIRS` will exhibit what seems to be bizarre behavior:

    >>> list(big.multisplit('appleXbananaYcookieX', ('X', 'Y'), keep=big.AS_PAIRS))
    [('apple', 'X'), ('banana', 'Y'), ('cookie', 'X'), ('', '')]

Although this looks very strange, this *is* sensible and correct.

For an explanation as to why `multisplit` will sometimes emit empty
strings when using a true value with `keep`, read the
[Why do you sometimes get empty strings when you split?](#why-do-you-sometimes-get-empty-strings-when-you-split])
section below.



#### `separate`

`separate` indicates whether multisplit should consider adjacent
separator strings in `s` as one separator or as multiple separators
each separated by a zero-length string.  It can be either false or
true.

    >>> list(big.multisplit('appleXYbananaYXYcookie', ('X', 'Y')))
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('appleXYbananaYXYcookie', ('X', 'Y'), separate=False))
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('appleXYbananaYXYcookie', ('X', 'Y'), separate=True))
    ['apple', '', 'banana', '', '', 'cookie']

When you use `separate` and `keep` at the same time, and your string
has multiple adjacent separators, the second and subsequent adjacent
separators will be in a string by themselves:

    >>> list(big.multisplit('appleXYbananaYXYcookie', ('X', 'Y'), separate=True, keep=True))
    ['appleX', 'Y', 'bananaY', 'X', 'Y', 'cookie']

    >>> list(big.multisplit('appleXYbananaYXYcookie', ('X', 'Y'), separate=True, keep=big.AS_PAIRS))
    [('apple', 'X'), ('', 'Y'), ('banana', 'Y'), ('', 'X'), ('', 'Y'), ('cookie', '')]


#### `strip`

`strip` indicates whether multisplit should strip separators from
the beginning and/or end of `s`.  It supports six values:
false, true, `big.LEFT`, `big.RIGHT`, and `big.PROGRESSIVE`.

By default, `strip` is false, which means it doesn't strip any
leading or trailing separators:

    >>> list(big.multisplit('XYappleXbananaYcookieYXY', ('X', 'Y')))
    ['', 'apple', 'banana', 'cookie', '']

Setting `strip` to true strips both leading and trailing separators:

    >>> list(big.multisplit('XYappleXbananaYcookieYXY', ('X', 'Y'), strip=True))
    ['apple', 'banana', 'cookie']

`big.LEFT` and `big.RIGHT` tell `multistrip` to only strip on that
side of the string

    >>> list(big.multisplit('XYappleXbananaYcookieYXY', ('X', 'Y'), strip=big.LEFT))
    ['apple', 'banana', 'cookie', '']
    >>> list(big.multisplit('XYappleXbananaYcookieYXY', ('X', 'Y'), strip=big.RIGHT))
    ['', 'apple', 'banana', 'cookie']

`big.PROGRESSIVE` duplicates a specific behavior of `str.split` when using
`maxsplit`.  It always strips on the left, but it only strips on the right
if the string is completely split.  If `maxsplit` is reached before the entire
string is split, and `strip` is `big.PROGRESSIVE`, `multisplit` *won't* strip
the right side of the string.

    >>> list(big.multisplit('XappleXbananaYcookieY', ('X', 'Y'), strip=big.PROGRESSIVE))
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('XappleXbananaYcookieY', ('X', 'Y'), maxsplit=0, strip=big.PROGRESSIVE))
    ['appleXbananaYcookieY']
    >>> list(big.multisplit('XappleXbananaYcookieY', ('X', 'Y'), maxsplit=1, strip=big.PROGRESSIVE))
    ['apple', 'bananaYcookieY']
    >>> list(big.multisplit('XappleXbananaYcookieY', ('X', 'Y'), maxsplit=2, strip=big.PROGRESSIVE))
    ['apple', 'banana', 'cookieY']
    >>> list(big.multisplit('XappleXbananaYcookieY', ('X', 'Y'), maxsplit=3, strip=big.PROGRESSIVE))
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('XappleXbananaYcookieY', ('X', 'Y'), maxsplit=4, strip=big.PROGRESSIVE))
    ['apple', 'banana', 'cookie']

#### `reverse`

`reverse` specifies where `multisplit` starts parsing the string--from
the beginning, or the end--and in what direction it moves when parsing
the string--towards the end, or towards the beginning.  It only supports
two values: when it's false, `multisplit` starts at the beginning of the
string, and parses moving to the right (towards the end).  But when `reverse`
is true, `multisplit` starts at the *end* of the
string, and parses moving to the *left* (towards the *beginning).*

This has two noticable effects on `multisplit`'s output.  First, this
changes what splits are kept when `maxsplit` is less than the total number
of splits in the string.  When `reverse` is true, the string is split
starting on the right and moving towards the left:

    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), reverse=True))
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), maxsplit=0, reverse=True))
    ['appleXbananaYcookie']
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), maxsplit=1, reverse=True))
    ['appleXbanana', 'cookie']
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), maxsplit=2, reverse=True))
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), maxsplit=3, reverse=True))
    ['apple', 'banana', 'cookie']

The second effect is far more subtle.  It pertains to strings where there
are multiple *overlapping* separators.  When `reverse` is false, and there
are two overlapping separators, the string is split by the leftmost overlapping
separator.  When `reverse` is true and there are two overlapping separators,
the string is split by the *rightmost* overlapping separator.

    >>> list(big.multisplit('appleXAYbananaXAYcookie', ('XA', 'AY')))
    ['apple', 'Ybanana', 'Ycookie']
    >>> list(big.multisplit('appleXAYbananaXAYcookie', ('XA', 'AY'), reverse=True))
    ['appleX', 'bananaX', 'cookie']

### Reimplementing library functions using `multisplit`

Finally, here are some concrete examples of how you could use
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
to replace some common Python string splitting methods.  These exactly duplicate the
behavior of the originals:
```Python
def str_split(s, sep, maxsplit=-1):
    separate = sep != None
    if separate:
        strip = False
    else:
        sep = big.ascii_whitespace if isinstance(s, bytes) else big.whitespace
        strip = big.PROGRESSIVE
    result = list(big.multisplit(s, sep,
        maxsplit=maxsplit, separate=separate, strip=strip))
    if not separate:
        empty = b'' if isinstance(s, bytes) else ''
        if result and result[-1] == empty:
            result.pop()
    return result

def str_rsplit(s, sep, maxsplit=-1):
    separate = sep != None
    if separate:
        strip = False
    else:
        sep = big.ascii_whitespace if isinstance(s, bytes) else big.whitespace
        strip = big.PROGRESSIVE
    result = list(big.multisplit(s, sep,
        maxsplit=maxsplit, reverse=True, separate=separate, strip=strip))
    if not separate:
        empty = b'' if isinstance(s, bytes) else ''
        if result and result[-1] == empty:
            result.pop()
    return result

def str_splitlines(s, keepends=False):
    newlines = big.ascii_newlines if isinstance(s, bytes) else big.newlines
    l = list(big.multisplit(s, newlines,
        keep=keepends, separate=True, strip=False))
    if l and not l[-1]:
        l.pop()
    return l

def str_partition(s, sep):
    if not sep:
        raise ValueError("empty separator")
    l = tuple(big.multisplit(s, (sep,),
        keep=big.ALTERNATING, maxsplit=1, separate=True))
    if len(l) == 1:
        empty = b'' if isinstance(s, bytes) else ''
        l += (empty, empty)
    return l

def str_rpartition(s, sep):
    if not sep:
        raise ValueError("empty separator")
    l = tuple(big.multisplit(s, (sep,),
        keep=big.ALTERNATING, maxsplit=1, reverse=True, separate=True))
    if len(l) == 1:
        empty = b'' if isinstance(s, bytes) else ''
        l = (empty, empty) + l
    return l
```

### Why do you sometimes get empty strings when you split?

Sometimes when you split using
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse),
you'll get empty strings in the return value.  This might be unexpected,
violating the [Principle Of Least Astonishment.](https://en.wikipedia.org/wiki/Principle_of_least_astonishment)
But there are excellent reasons for this behavior, and it stems from observing
how `str.split` behaves.

`str.split` really has two
major modes of operation: when you don't pass in a separator (or pass in `None` for the
separator), and when you pass in an explicit separator string.  In this latter mode,
the documentation says it regards every instance of a separator string as an individual
separator splitting the string.  What does that mean?  Watch what happens when you have
two adjacent separators in the string you're splitting:

    >>> '1,2,,3'.split(',')
    ['1', '2', '', '3']

What's that empty string doing between `'2'` and `'3'`?  Here's how to think about it:
when you pass in an explicit separator, `str.split` splits at *every* occurance of that
separator in the string.  It *always* splits the string into two places, whenever there's
a separator.  And when there are two adjacent separators, conceptually, they have a
zero-length string in between them:

    >>> '1,2,,3'[4:4]
    ''

The empty string in the output of `str.split` represents the fact that there
were two adjacent separators.  If `str.split` didn't add that empty string,
and the output looked like this:

    ['1', '2', '3']

it'd be indistinguishable from splitting the same string but *without*
two separators in a row:

    >>> '1,2,3'.split(',')
    ['1', '2', '3']

This difference is crucial when you want to reconstruct the original string from
the split list.  `str.join` should always be the inverse of `str.split`, and with
that empty string there, it works correctly:

    >>> ','.join(['1', '2', '3'])
    '1,2,3'
    >>> ','.join(['1', '2', '', '3'])
    '1,2,,3'

Now take a look at what happens when the string
you're splitting starts or ends with a separator:

    >>> ',1,2,3,'.split(',')
    ['', '1', '2', '3', '']

This might seem weird.  But, just like with two adjacent separators,
this behavior is important for consistency.  Conceptually there's
a zero-length string between the beginning of the string and the first
comma.  And `str.join` needs those empty strings in order to correctly
recreate the original string.

    >>> ','.join(['', '1', '2', '3', ''])
    ',1,2,3,'

Naturally,
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
duplicates this behavior.  When you want
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
to emulate the behavior of `str.split` when using an explicit separator
string, just pass in `keep=False`, `separate=True`, and `strip=False`.  That is, if 'a' and 'b' are strings,

     big.multisplit(a, (b,), keep=False, separate=True, strip=False)

produces the same output as

     a.split(b)

Here's sample code using
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
to split the strings we've been playing with:

    >>> list(big.multisplit('1,2,,3', (',',), keep=False, separate=True, strip=False))
    ['1', '2', '', '3']
    >>> list(big.multisplit(',1,2,3,', (',',), keep=False, separate=True, strip=False))
    ['', '1', '2', '3', '']

This "emit an empty string" behavior has ramifications for the other `keep` modes, too.
The behavior of `keep=True` is perhaps easy to predict; we just append the separators
to the previous string segment:

    >>> list(big.multisplit('1,2,,3', (',',), keep=True, separate=True, strip=False))
    ['1,', '2,', ',', '3']
    >>> list(big.multisplit(',1,2,3,', (',',), keep=True, separate=True, strip=False))
    [',', '1,', '2,', '3,', '']

The principle here is that, when you use `keep=True`, you should be able to reconstitute
the original string with `''.join`:

    >>> ''.join(['1,', '2,', ',', '3'])
    '1,2,,3'
    >>> ''.join([',', '1,', '2,', '3,', ''])
    ',1,2,3,''

`keep=big.ALTERNATING` is much the same, except we insert the separators as their
own segments, rather than appending each one to the previous segment:

    >>> list(big.multisplit('1,2,,3', (',',), keep=big.ALTERNATING, separate=True, strip=False))
    ['1', ',', '2', ',', '', ',', '3']
    >>> list(big.multisplit(',1,2,3,', (',',), keep=big.ALTERNATING, separate=True, strip=False))
    ['', ',', '1', ',', '2', ',', '3', ',', '']

And, as with `keep=True`, you can also recreate the original string by passing
these arrays in to `''.join`:

    >>> ''.join(['1', ',', '2', ',', '', ',', '3'])
    '1,2,,3'
    >>> ''.join(['', ',', '1', ',', '2', ',', '3', ',', ''])
    ',1,2,3,''

Finally, consider `keep=big.AS_PAIRS`.  The behavior here seemed so strange,
initially I thought it was wrong.  But I gave it a lot of thought and convinced
myself that, yes, this is correct:

    >>> list(big.multisplit('1,2,,3', (',',), keep=big.AS_PAIRS, separate=True, strip=False))
    [('1', ','), ('2', ','), ('', ','), ('3', '')]
    >>> list(big.multisplit(',1,2,3,', (',',), keep=big.AS_PAIRS, separate=True, strip=False))
    [('', ','), ('1', ','), ('2', ','), ('3', ','), ('', '')]

That tuple at the end, just containing two empty strings:

    ('', '')

is so strange.  How can that be right?

It's the same as `str.split`.
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
*must* split the string into two pieces *every* time it finds the separator
in the original string.  So it *must* emit the empty non-separator string.
And since that zero-length string isn't (cannot!) be followed by a separator,
when using `keep=AS_PAIRS` the final separator string is *also* empty.

You can recreate the original string from this result too,
although you have to unpack the tuples:

    >>> ''.join(s  for t in [('1', ','), ('2', ','), ('', ','), ('3', '')]  for s in t)
    '1,2,,3'
    >>> ''.join(s  for t in [('', ','), ('1', ','), ('2', ','), ('3', ','), ('', '')]  for s in t)
    ',1,2,3,'


## `lines` and lines modifier functions

[`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs) creates an iterator that yields individual lines
split from a string.  It's designed to make it easy to write
well-behaved simple text parsers.

For example, every yielded line is accompanied by a `LinesInfo`
object which provides the line number and starting column number
for each line.  This makes it easy for your parser to provide
line and column information for error messages.

The output of [`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs) can be modified by "lines modifier"
functions.  These are functions that iterate over a lines
iterator and re-yield the values, possibly modifying or
discarding them along the way.  For example, passing
a [`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs) iterator into `lines_filter_empty_lines` results
in an iterator that skips over the empty lines.
All the lines modifier functions that ship with big
start with the string `lines_`.

Actually there are additional constraints on the names
of lines modifier functions.  The second word of the name
of the function, immediately after `lines_`, tells you what
the function will do.  Some examples:

* `filter` means this lines modifier may remove some
  lines from the output.  `lines_filter_empty_lines`
  will only yield a line if it isn't empty.
* `strip` means this lines modifier may remove one or
  more substrings from the line.  A lines modifier that
  removes the initial part of a line will add a
  `leading` field to the accompanying `LineInfo` object
  containing the substring removed from the beginning
  of the line, and will also update the `column_number`
  of the line to reflect the change to the line.
* `convert` means this lines modifier may change one
  or more substrings in the line.

All lines modifier functions are composable with each
other; you can "stack" them together simply by passing
the output of one into the input of another.  For example,

     with open("textfile.txt", "rt") as f:
         for info, lines in big.lines_filter_empty_lines(
     	     big.lines_rstrip(lines(f.read()))):
     	     ...

will iterate over the lines of `textfile.txt`, skipping
over all empty lines and lines that consist only of
whitespace.

When you stack line modifiers in this way, note that the
*outer* modifiers happen *later*.  In the above example,
each line is first "r-stripped", and then discarded
if it is empty.  If you stacked the line modifiers in
the opposite order:

     with open("textfile.txt", "rt") as f:
         for info, lines in big.lines_rstrip(
     	     big.lines_filter_empty_lines(lines(f.read()))):
     	     ...

then you would filter out empty lines first, and *then*
"r-strip" the lines.  So lines in the input that contained
only whitespace would still get yielded as empty lines,
which in this case is probably not what you wanted.

Of course, you can write your own lines modifier functions!
Simply accept a lines iterator as an argument, iterate over
it, and yield each line info and line, modifying them
(or not yielding them!) as you see fit.  You can potentially
even write your own lines iterator, a replacement for [`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs),
if you need functionality [`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs) doesn't provide.

## Word wrapping and formatting

**big** contains three functions used to reflow and format text
in a pleasing manner.  In the order you should use them, they are
[`split_text_with_code`](#split_text_with_codes--tab_width8-allow_codetrue-code_indent4-convert_tabs_to_spacestrue),
`word_wrap`,
and optionally
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_responseoverflowresponseraise-overflow_before0-overflow_after0).
This trio of functions gives you the following word-wrap superpowers:

* Paragraphs of text representing embedded "code" don't get word-wrapped.
  Instead, their formatting is preserved.
* Multiple texts can be merged together into multiple columns.

#### Split text array

[`split_text_with_code`](#split_text_with_codes--tab_width8-allow_codetrue-code_indent4-convert_tabs_to_spacestrue)
splits a string of text into a *split text array*,
and `word_wrap` consumes a *split text array* to produce its
word-wrapped output.  A split text array is an array of strings.
You'll see four kinds of strings in a split text array:

* Individual words, ready to be word-wrapped.
* Entire lines of "code", preserving their formatting.
* Line breaks, represented by a single newline: `'\n'`.
* Paragraph breaks, represented by two newlines: `'\n\n'`.

When
[`split_text_with_code`](#split_text_with_codes--tab_width8-allow_codetrue-code_indent4-convert_tabs_to_spacestrue)
splits a string, it views each
line as either a "text" line or a "code" line.  Any non-blank
line that starts with `code_indent` or more spaces (or the
equivalent using tabs) is a "code" line, and any other
non-blank line is a "text" line.  But it has some state
here; when
[`split_text_with_code`](#split_text_with_codes--tab_width8-allow_codetrue-code_indent4-convert_tabs_to_spacestrue)
sees a "text" line,
it switches into "text" mode, and when it sees a "code"
line it switches into "code" mode.

In "text" mode:

* words are separated by whitespace,
* initial whitespace on the line is discarded,
* the amount of whitespace between words is irrelevant,
* individual newline characters are ignored, and
* more than two newline characters are converted into exactly
  two newlines (aka a "paragraph break").

In "code" mode:

* all whitespace is preserved, except for trailing whitespace on a line, and
* all newline characters are preserved.

Also, whenever
[`split_text_with_code`](#split_text_with_codes--tab_width8-allow_codetrue-code_indent4-convert_tabs_to_spacestrue)
switches between
"text" and "code" mode, it emits a paragraph break.

This might be clearer with an example or two.  The following text:

```
hello there!
this is text.


this is a second paragraph!
```

would be represented in a Python string as:
```Python
"hello there!\nthis is text.\n\n\nthis is a second paragraph!"
```

Note the three newlines between the second and third lines.

[`split_text_with_code`](#split_text_with_codes--tab_width8-allow_codetrue-code_indent4-convert_tabs_to_spacestrue)
would turn this into the following split text array:
```Python
[ 'hello', 'there!', 'this', 'is', 'text.', '\n\n',
  'this', 'is', 'a', 'second', 'paragraph!']
```

[`split_text_with_code`](#split_text_with_codes--tab_width8-allow_codetrue-code_indent4-convert_tabs_to_spacestrue)
merged the first two lines together into
a single paragraph, and collapsed the three newlines separating
the two paragraphs into a "paragraph break" marker
(two newlines in one string).

And this text:

```
What are the first four squared numbers?

    for i in range(1, 5):


        print(i**2)

Python is just that easy!
```

would be represented in a Python string as (broken up into multiple strings for clarity):
```Python
"What are the first four squared numbers?\n\n"
+
"    for i in range(1, 5):\n\n\n"
+
"        print(i**2)\n\nPython is just that easy!"
```

[`split_text_with_code`](#split_text_with_codes--tab_width8-allow_codetrue-code_indent4-convert_tabs_to_spacestrue)
considers the two lines with initial whitespace as "code" lines,
and so the text is split into the following split text array:
```Python
['What', 'are', 'the', 'first', 'four', 'squared', 'numbers?', '\n\n',
  '    for i in range(1, 5):', '\n', '\n', '\n', '        print(i**2)', '\n\n',
  'Python', 'is', 'just', 'that', 'easy!']
```

Here we have a text paragraph, followed by a "code paragraph", followed
by a second text paragraph.  The code paragraph preserves the internal
newlines, though they are represented as individual "line break" markers
(strings containing a single newline).  Every paragraph is separated by
a "paragraph marker".

Here's a simple algorithm for joining a split text array back into a
single string:
```Python

prev = None
a = []
for word in split_text_array:
    if not (prev and prev.isspace() and word.isspace()):
        a.append(' ')
    a.append(word)
text = "".join(a)
```

Of course, this algorithm is too simple to do word wrapping.
Nor does it handle adding two spaces after sentence-ending
punctuation.  In practice you should just use
[`wrap_words`](#wrap_wordswords-margin79--two_spacestrue).

#### Merging columns

[`merge_columns`](#merge_columnscolumns-column_separator--overflow_responseoverflowresponseraise-overflow_before0-overflow_after0)
merges multiple strings into columns on the same line.

For example, it could merge these three Python strings:
```Python
[
"Here's the first\ncolumn of text.",
"More text over here!\nIt's the second\ncolumn!  How\nexciting!",
"And here's a\nthird column.",
]
```

into the following text:

```
Here's the first    More text over here!   And here's a
column of text.     It's the second        third column.
                    column!  How
                    exciting!
```

(Note that
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_responseoverflowresponseraise-overflow_before0-overflow_after0)
doesn't do its own word-wrapping;
instead, it's designed to consume the output of
[`wrap_words`](#wrap_wordswords-margin79--two_spacestrue).)

Each column is passed in to
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_responseoverflowresponseraise-overflow_before0-overflow_after0)
as a "column tuple":

```Python
(s, min_width, max_width)
```

`s` is the string,
`min_width` is the minimum width of the column, and
`max_width` is the minimum width of the column.

As you saw above, `s` can contain newline characters,
and
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_responseoverflowresponseraise-overflow_before0-overflow_after0)
obeys those when formatting each column.

For each column,
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_responseoverflowresponseraise-overflow_before0-overflow_after0)
measures the longest
line of each column.  The width of the column is determined
as follows:

- If the longest line is less than `min_width` characters long,
  the column will be `min_width` characters wide.
- If the longest line is less than or equal to `min_width`
  characters long, and less than or equal to `max_width`
  characters long, the column will be as wide as the longest line.
- If the longest line is greater than `max_width` characters long,
  the column will be `max_width` characters wide, and lines that
  are longer than `max_width` characters will "overflow".

#### Overflow

What is "overflow"?  It's when the text in a column is wider than that
column's `max_width`.
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_responseoverflowresponseraise-overflow_before0-overflow_after0)
discusses both "overflow lines",
lines that are longer than `max_width`, and "overflow columns", which
are columns that contain any overflow lines.

What does
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_responseoverflowresponseraise-overflow_before0-overflow_after0)
do when it encounters overflow?  It provides
three "strategies" to deal with this condition, and you can control
which it uses through the `overflow_strategy` parameter.  The three are:

`OverflowStrategy.RAISE`: Raise an `OverflowError` exception.  The default.

`OverflowStrategy.INTRUDE_ALL`: Intrude into all subsequent columns on
all lines where the overflowed column is wider than its max_width.
The subsequent columns "make space" for the overflow text by pausing their
output on the overflow lines.

`OverflowStrategy.DELAY_ALL`:  Delay all columns after the overflowed
column, not beginning any until after the last overflowed line
in the overflowed column.  This is like `INTRUDE_ALL`, except that
they "make space" by pausing their output until the last overflowed
line.

When `overflow_strategy` is `INTRUDE_ALL` or `DELAY_ALL`, and
either `overflow_before` or `overflow_after` is nonzero, these
specify the number of extra lines before or after
the overflowed lines in a column where the subsequent columns
"pause".


## Enhanced `TopologicalSorter`

#### Overview

**big**'s [`TopologicalSorter`](#topologicalsortergraphnone)
is a drop-in replacement for
[`graphlib.TopologicalSorter`](https://docs.python.org/3/library/graphlib.html#graphlib.TopologicalSorter)
in the Python standard library (new in 3.9).
However, the version in **big** has been greatly upgraded:

- `prepare` is now optional, though it still performs a cycle check.
- You can add nodes and edges to a graph at any time, even while
  iterating over the graph.  Adding nodes and edges always succeeds.
- You can remove nodes from graph `g` with the new method `g.remove(node)`.
  Again, you can do this at any time, even while iterating over the graph.
  Removing a node from the graph always succeeds, assuming the node is in the graph.
- The functionality for iterating over a graph now lives in its own object called
  a *view*.  View objects implement the `get_ready`, `done`, and `__bool__`
  methods.  There's a default view built in to the graph object;
  the `get_ready`, `done`, and `__bool__` methods on a graph just call
  into the graph's default view.  You can create a new view at any time
  by calling the new `view` method.

Note that if you're using a view to iterate over the graph, and you modify the graph,
and the view now represents a state that isn't *coherent* with the graph,
attempting to use that view raises a `RuntimeError`.  More on what I mean
by "coherence" in a minute.

This implementation also fixes some minor warts with the existing API:

- In Python's implementation, `static_order` and `get_ready`/`done` are mutually exclusive.  If you ever call
  `get_ready` on a graph,  you can never call `static_order`, and vice-versa.  The implementaiton in **big**
  doesn't have this restriction, because its implementation of `static_order` creates and uses a new view object
  every time it's called..
- In Python's implementation, you can only iterate over the graph once, or call `static_order` once.
  The implementation in **big** solves this in several ways: it allows you to create as many views as you
  want, and you can call the new `reset` method on a view to reset it to its initial state.

#### Graph / view coherence

So what does it mean for a view to no longer be coherent with the graph?
Consider the following code:

```Python
g = big.TopologicalSorter()
g.add('B', 'A')
g.add('C', 'A')
g.add('D', 'B', 'C')
g.add('B', 'A')
v = g.view()
g.ready() # returns ('A',)
g.add('A', 'Q')
```

First this code creates a graph `g` with a classic "diamond"
dependency pattern.  Then it creates a new view `v`, and gets
the currently "ready" nodes, which consists just of the node
`'A'`.  Finally it adds a new dependency: `'A'` depends on `'Q'`.

At this moment, view `v` is no longer _coherent._  `'A'` has been
marked as "ready", but `'Q'` has not.  And yet `'A'` depends on `'Q'`.
All those statements can't be true at the same time!
So view `v` is no longer _coherent,_  and any attempt to interact
with `v` raises an exception.

To state it more precisely: if view `v` is a view on graph `g`,
and you call `g.add('Z', 'Y')`,
and neither of these statements is true in view `v`:

- `'Y'` has been marked as `done`.
- `'Z'` has not yet been yielded by `get_ready`.

then `v` is no longer "coherent".

(If `'Y'` has been marked as `done`, then it's okay to make `'Z'` dependent on
`'Y'` regardless of what state `'Z'` is in.  Likewise, if `'Z'` hasn't been yielded
by `get_ready` yet, then it's okay to make `'Z'` dependent on `'Y'` regardless
of what state `'Y'` is in.)

Note that you can restore a view to coherence.  In this case,
removing either `Y` or `Z` from `g` would resolve the incoherence
between `v` and `g`, and `v` would start working again.

Also note that you can have multiple views, in various states of iteration,
and by modifying the graph you may cause some to become incoherent but not
others.  Views are completely independent from each other.


## Bound inner classes

#### Overview

One minor complaint I have about Python is about inner classes.
An "inner class" is a class defined inside another class.  And,
well, inner classes seem kind of half-baked.   Unlike methods,
inner classes don't get bound to the object.

Consider this Python code:

```Python
class Outer(object):
    def method(self):
        pass
    class Inner(object):
        def __init__(self):
            pass

o = Outer()
o.method()
i = o.Inner()
```

When `o.method` is called, Python automatically passes in the `o` object as the first parameter
(generally called `self`).  In object-oriented lingo, `o` is *bound* to `method`, and indeed
Python calls this object a *bound method*:


    >>> o.method
    <bound method Outer.method of <__main__.Outer object at 0x########>>

But that doesn't happen when `o.Inner` is called.  (It *does* pass in
a `self`, but in this case it's the newly-created `Inner` object.)
There's just no built-in way for the `o.Inner` object being constructed
to *automatically* get a reference to `o`.  If you need one, you must
explicitly pass one in, like so:

```Python
class Outer(object):
    def method(self):
        pass
    class Inner(object):
        def __init__(self, outer):
            self.outer = outer

o = Outer()
o.method()
i = o.Inner(o)
```

This seems redundant.  You don't have to pass in `o` explicitly to method calls,
why should you have to pass it in explicitly to inner classes?

Well--now you don't have to!
You just need to decorate the inner class with `@big.BoundInnerClass`.

#### Using bound inner classes

Let's modify the above example to use our [`BoundInnerClass`](#boundinnerclasscls)
decorator:

```Python
from big import BoundInnerClass

class Outer(object):
    def method(self):
        pass

    @BoundInnerClass
    class Inner(object):
        def __init__(self, outer):
            self.outer = outer

o = Outer()
o.method()
i = o.Inner()
```

Notice that `Inner.__init__` now accepts an `outer` parameter,
even though you didn't pass in any arguments to `o.Inner`.
And when it's called, `o` is magically passed in to `outer`!
Thanks, [`BoundInnerClass`](#boundinnerclasscls)!  You've saved the day.

Decorating an inner class like this always adds a second positional
parameter, after `self`.  And, like `self`, in theory you don't have
to use the name `outer`.  (Although for consistency's sakes, it's probably
a good idea.)

#### Inheritance

Bound inner classes get slightly complicated when mixed with inheritance.
It's not all that difficult, you merely need to obey the following rules:

1. *A bound inner class can inherit normally from any unbound class.*

2. *To subclass from a bound inner class while still inside the outer
class scope, or when referencing the inner class from the outer class
(as opposed to an instance of the outer class), you must actually
subclass or reference `classname.cls`.*  This is because inside the
outer class, the "class" you see is actually an instance of a
[`BoundInnerClass`](#boundinnerclasscls) object.

3. *All classes that inherit from a bound inner class must always call the
superclass's `__init__`. You don't need to pass in the outer parameter;
it'll be automatically passed in to the superclass's `__init__` as before.*

4. *An inner class that inherits from a bound inner class, and which also wants
to be bound to the outer object, should be decorated with
[`BoundInnerClass`](#boundinnerclasscls).*

5. *An inner class that inherits from a bound inner class, but doesn't want
to be bound to the outer object, should be decorated with
[`UnboundInnerClass`](#unboundinnerclasscls).*

Restating the last two rules: every class that descends from any
[`BoundInnerClass`](#boundinnerclasscls)
should be decorated with either
[`BoundInnerClass`](#boundinnerclasscls)
or
[`UnboundInnerClass`](#unboundinnerclasscls).

Here's a simple example using inheritance with bound inner classes:

```Python
from big import BoundInnerClass, UnboundInnerClass

class Outer(object):

    @BoundInnerClass
    class Inner(object):
        def __init__(self, outer):
            self.outer = outer

    @UnboundInnerClass
    class ChildOfInner(Inner.cls):
        def __init__(self):
            super(Outer.ChildOfInner, self).__init__()

o = Outer()
i = o.ChildOfInner()
```

We followed the rules:

* `Inner` inherits from object; since object isn't a bound inner class,
  there are no special rules about inheritance `Inner` needs to obey.
* `ChildOfInner` inherits from `Inner.cls`, not `Inner`.
* Since `ChildOfInner` inherits from a
  [`BoundInnerClass`](#boundinnerclasscls),
  it must be
  decorated with either [`BoundInnerClass`](#boundinnerclasscls)
  or [`UnboundInnerClass`](#unboundinnerclasscls).
  It doesn't want the outer object passed in, so it's decorated
  with [`UnboundInnerClass`](#unboundinnerclasscls).
* `ChildOfInner.__init__` calls `super().__init__`.

Note that, because `ChildOfInner` is decorated with
[`UnboundInnerClass`](#unboundinnerclasscls),
it doesn't take an `outer` parameter.  Nor does it pass in an `outer`
argument when it calls `super().__init__`.  But when the constructor for
`Inner` is called, the correct `outer` parameter is passed in--like magic!
Thanks again, [`BoundInnerClass`](#boundinnerclasscls)!

If you wanted `ChildOfInner` to also get the outer argument passed in to
its `__init__`, just decorate it with [`BoundInnerClass`](#boundinnerclasscls)
instead of
[`UnboundInnerClass`](#unboundinnerclasscls),
like so:

```Python
from big import BoundInnerClass

class Outer(object):

    @BoundInnerClass
    class Inner(object):
        def __init__(self, outer):
            self.outer = outer

    @BoundInnerClass
    class ChildOfInner(Inner.cls):
        def __init__(self, outer):
            super(Outer.ChildOfInner, self).__init__()
            assert self.outer == outer

o = Outer()
i = o.ChildOfInner()
```

Again, `ChildOfInner.__init__` doesn't need to explicitly
pass in `outer` when calling `super.__init__`.

You can see more complex examples of using inheritance with
[`BoundInnerClass`](#boundinnerclasscls)
(and [`UnboundInnerClass`](#unboundinnerclasscls))
in the **big** test suite.

#### Miscellaneous notes

* If you refer to a bound inner class directly from the outer class,
  rather than using the outer instance, you get the original class.
  This means that references to `Outer.Inner` are consistent, and it's
  a base class of all the bound inner classes. This also means that if
  you attempt to construct one without using an outer instance, you must
  pass in the outer parameter by hand, just as you would have to pass
  in the self parameter by hand when calling an unbound method.

* If you refer to a bound inner class from an outer instance,
  you get a subclass of the original class.

* Bound classes are cached in the outer object, which both provides
  a small speedup and ensures that `isinstance` relationships are
  consistent.

* You must not rename inner classes decorated with either
  [`BoundInnerClass`](#boundinnerclasscls)
  or [`UnboundInnerClass`](#unboundinnerclasscls)!
  The implementation of
  [`BoundInnerClass`](#boundinnerclasscls)
  looks up
  the bound inner class in the outer object by name in several places.
  Adding aliases to bound inner classes is harmless, but the original
  attribute name must always work.

* Bound inner classes from different objects are different classes.
  This is symmetric with bound methods; if you have two objects
  `a` and `b` that are instances of the same class,
  `a.BoundInnerClass != b.BoundInnerClass`, just as `a.method != b.method`.

* The binding only goes one level deep; if you had an inner class `C`
  inside another inner class `B` inside a class `A`, the constructor
  for `C` would be called with the `B` object, not the `A` object.

* Similarly, if you have a bound inner class `B` inside a class `A`,
  and another bound inner class `D` inside a class `C`, and `D`
  inherits from `B`, the constructor for `D` will be called with
  the `B` object but not the `A` object. When `D` calls `super().__init__`
  it'll have to fill in the `outer` parameter by hand.

* There's a race condition in the implementation: if you access a
  bound inner class through an outer instance from two separate threads,
  and the bound inner class was not previously cached, the two threads
  may get different (but equivalent) bound inner class objects, and only
  one of those instances will get cached on the outer object.  This could
  lead to confusion and possibly cause bugs. For example, you could have
  two objects that would be considered equal if they were instances of
  the same bound inner class, but would not be considered equal if
  instantiated by different instances of that same bound inner class.
  There's an easy workaround for this problem: access the bound inner
  class from the `__init__` of the outer class, which should allow
  the code to cache the bound inner class instance before a second
  thread could ever get a reference to the outer object.

## Release history

**0.6.16**

* Fixed Python 3.6 support! Some equals-signs-in-f-strings and some
  other anachronisms had crept in.  0.6.16 has been tested on all
  versions from 3.6 to 3.11 (as well as having 100% *coverage*).
* Made the `dateutils` package an optional dependency.  Only one function
  needs it, [`parse_timestamp_3339Z()`](#parse_timestamp_3339zs--timezonenone).
* Minor cleanup in [`PushbackIterator()`](#pushbackiteratoriterablenone).
  It also uses slots now, which should make it a bit faster.

**0.6.15**

* Added the new functions
  [`datetime_ensure_timezone(d, timezone)`](#datetime_ensure_timezoned-timezone) and
  [`datetime_set_timezone(d, timezone)`](#datetime_set_timezoned-timezone).
  These allow you to ensure or explicitly set a timezone on a `datetime.datetime`
  object.
* Added the `timezone` argument to 
  [`parse_timestamp_3339Z()`](#parse_timestamp_3339zs--timezonenone).
* [`gently_title()`](#gently_titles-apostrophesnone-double_quotesnone)
  now capitalizes the first letter after a left parenthesis.
* Changed the secret `multirpartition` function slightly.  Its `reverse`
  parameter now means to un-reverse its reversing behavior.  Stated
  another way, `multipartition(reverse=X)` and `multirpartition(reverse=not X)`
  now do the same thing.

**0.6.14**

* Improved the text of the `RuntimeError` raised by `TopologicalSorter.View`
  when the view is incoherent.  Now it tells you exactly what nodes are
  conflicting.
* Expanded the deep dive on `multisplit`.

**0.6.13**

* Changed [`translate_filename_to_exfat(s)`](#translate_filename_to_exfats)
  behavior: when modifying a string with a colon (`':'`) *not* followed by
  a space, it used to convert it to a dash (`'-'`).  Now it converts the
  colon to a period (`'.'`), which looks a little more natural.  A colon
  followed by a space is still converted to a dash followed by a space.

*p.s.* There's a revision with a comment claiming it represents 0.6.13.  But
I forgot to actually tag it and release it, and I forgot to actually.  Oops!

**0.6.12**

* Bugfix: When calling
  [`TopologicalSorter.print()`](#topologicalsorterprintprintprint),
  it sorts the list of nodes, for consistency's sakes.
  But if the node objects don't support `<` or `>` comparison,
  that throws an exception.  `TopologicalSorter.print()` now catches
  that exception and simply 
* Added a secret (otherwise undocumented!) function: `multirpartition`,
  which is like
  [`multipartition`](#multipartitions-separators-count1--reverseFalse-separateTrue)
  but with `reverse=True`.
* Added the list of conflicted nodes to the "node is incoherent"
  exception text.

**0.6.11**

* Changed the import strategy.  The top-level **big** module used
  to import all its child modules, and `import *` all the symbols
  from all those modules.  But a friend (hi Mark Shannon!) talked
  me out of this.  It's convenient, but if a user doesn't care about
  a particular module, why make them import it.  So now the top-level
  **big** module contains nothing but a version number, and you
  can either import just the submodules you need, or you can import
  **big.all** to get all the symbols (like **big** itself used to do).

**0.6.10**

* All code changes had to do with
  [`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse):
    * Fixed a subtle bug.  When splitting with a separator that can overlap
      itself, like `' x '`, `multisplit` will prefer the *leftmost* instance.
      But when `reverse=True`, it must prefer the *rightmost* instance.
      Thanks to Eric V. Smith for suggesting the clever "reverse everything,
      call `re.split`, and un-reverse everything" approach that meant I could
      fix this bug while still implementing on top of `re.split`!
    * Implemented `PROGRESSIVE` mode for the `strip` keyword.  This behaves
      like `str.strip`: when splitting, strip on the left, then start splitting.
      If we don't exhaust `maxsplit`, strip on the right; if we *do* exhaust
      `maxsplit`, *don't* strip on the right.  (Similarly for `str.rstrip`
      when `reverse=True`.)
    * Changed the default for `strip` to `False`.  It used to be
      `NOT_SEPARATE`.  But this was too surprising--I'd forget that it
      was the default, and turning on `keep` wouldn't return everything I
      thought I should get, and I'd head off to debug `multisplit`, when in
      fact it was behaving as specified.  The Principle Of Least Surprise
      tells me that `strip` defaulting to `False` is less surprising.
      Also, maintaining the invariant that all the keyword-only parameters
      to `multisplit` default to `False` is a helpful mnemonic device in
      several ways.
    * Removed `NOT_SEPARATE` (and the not-yet-implemented `STR_STRIP`)
      modes for `strip`.  They're easy to implement yourself, and this
      removes some surface area from the already-too-big
      `multisplit` API.
* Modernized `pyproject.toml` metadata to make `flit` happier.  This was
  necessary to ensure that `pip install big` also installs its dependencies.

**0.6.8**

* Renamed two of the three freshly-added lines modifier functions:
  `lines_filter_contains` is now 
  [`lines_containing`](#lines_containingli-s--invertfalse),
  and `lines_filter_grep` is now
  [`lines_grep`](#lines_grepli-pattern--invertfalse-flags0).

**0.6.7**

* Added three new lines modifier functions
  to the [`text`](#bigtext) module:
  `lines_filter_contains`,
  `lines_filter_grep`,
  and
  [`lines_sort`](#lines_sortli--reversefalse).
* [`gently_title`](#gently_titles-apostrophesnone-double_quotesnone)
  now accepts `str` or `bytes`.  Also added the `apostrophes` and
  `double_quotes` arguments.

**0.6.6**

* Fixed a bug in
  [`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse).
  I thought when using `keep=AS_PAIRS` that it shouldn't ever emit a 2-tuple
  containing just empty strings--but on further reflection I've realized that
  that's correct.  This behavior is now tested and documented, along with
  the reasoning behind it.
* Added the `reverse` flag to
  [`re_partition`](#re_partitiontext-pattern-count1--flags0-reversefalse).
* `whitespace_without_dos` and `newlines_without_dos` still had the DOS
  end-of-line sequence in them!  Oops!
    * Added a unit test to check that.  The unit test also ensures that
      `whitespace`, `newlines`, and all the variants (`utf8_`, `ascii_`,
      and `_with_dos`) exactly match the set of characters Python considers
      whitespace and newline characters.
* Lots more documentation and formatting fixes.

**0.6.5**

* Added the new [`itertools`](#bigitertools) module, which so far only contains
  [`PushbackIterator`](#pushbackiteratoriterablenone).
* Added
  [`lines_strip_comments`](#lines_strip_commentsli-comment_separators--quotes--backslash-rstriptrue-triple_quotestrue)
  and
  [`split_quoted_strings`](#split_quoted_stringss-quotes---triple_quotestrue-backslash)
  to the
  [`text`](#bigtext)
  module.

**0.6.1**

* I realized that [`whitespace`](#whitespace) should contain the DOS end-of-line
  sequence (`'\r\n'`), as it should be considered a single separator
  when splitting etc.  I added that, along with [`whitespace_no_dos`](#whitespace),
  and naturally [`utf8_whitespace_no_dos`](#whitespace) and
  [`ascii_whitespace_no_dos`](#whitespace) too.
* Minor doc fixes.

**0.6**

A **big** upgrade!

* Completely retooled and upgraded
  [`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse),
  and added
  [`multistrip`](#multistrips-separators-leftTrue-rightTrue)
  and
  [`multipartition`,](#multipartitions-separators-count1--reverseFalse-separateTrue)
  collectively called
  [**The `multi-` family of functions.**](#The-multi--family-of-functions)
  (Thanks to Eric Smith for suggesting
  [`multipartition`!](#multipartitions-separators-count1--reverseFalse-separateTrue)
  Well, sort of.)
  * `[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)`
    now supports five (!) keyword-only parameters, allowing the caller
    to tune its behavior to an amazing degree.
  * Also, the original implementation of
    `[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)`
    got its semantics a bit wrong; it was inconsistent and maybe a little buggy.
  * [`multistrip`](#multistrips-separators-leftTrue-rightTrue)
    is like `str.strip` but accepts an iterable of
    separator strings.  It can strip from the left, right, both, or
    neither (in which case it does nothing).
  * [`multipartition`](#multipartitions-separators-count1--reverseFalse-separateTrue)
    is like `str.partition`, but accepts an iterable
    of separator strings.  It can also partition more than once,
    and supports `reverse=True` which causes it to partition from the right
    (like `str.rpartition`).
  * Also added useful predefined lists of separators for use with all
    the `multi` functions: [`whitespace`](#whitespace) and [`newlines`](#newlines),
    with `ascii_` and `utf8_` versions of each, and `without_dos` variants of
    all three [`newlines`](#newlines) variants.
* Added the
  [`Scheduler`](#schedulerregulatornone)
  and
  [`Heap`](#heapinone)
  classes.  [`Scheduler`](#schedulerregulatornone)
  is a replacement for Python's `sched.scheduler` class, with a modernized
  interface and a major upgrade in functionality.  [`Heap`](#heapinone)
  is an object-oriented interface to Python's `heapq` module, used by
  [`Scheduler`](#schedulerregulatornone).
  These are in their own modules.
* Added
  [`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs)
  and all the `lines_` modifiers.  These are great for writing little text parsers.
  For more information, please see the deep-dive on
  [**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)
* Removed`stripped_lines` and `rstripped_lines` from the `text` module,
  as they're superceded by the far superior
  [`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs)
  family.
* Enhanced
  [`normalize_whitespace`](#normalize_whitespaces-separatorsNone-replacementNone).
  Added the `separators` and `replacement` parameters,
  and added support for `bytes` objects.
* Added the `count` parameter to
  [`re_partition`](#re_partitiontext-pattern-count1--flags0)
  and
  [`re_rpartition`](#re_rpartitiontext-pattern-count1--flags0).

**0.5.2**

* Added `stripped_lines` and `rstripped_lines` to the [`text`](#bigtext) module.
* Added support for `len` to the [`TopologicalSorter`](#topologicalsortergraphnone) object.

**0.5.1**

* Added
  [`gently_title`](#gently_titles-apostrophesnone-double_quotesnone)
  and
  [`normalize_whitespace`](#normalize_whitespaces-separatorsNone-replacementNone)
  to the [`text`](#bigtext) module.
* Changed [`translate_filename_to_exfat`](#translate_filename_to_exfats)
  to handle translating `':'` in a special way.
  If the colon is followed by a space, then the colon is turned into `' -'`.
  This yields a more natural translation when colons are used in text, e.g.
  `'xXx: The Return Of Xander Cage'` is translated to `'xXx - The Return Of Xander Cage'`.
  If the colon is not followed by a space, turns the colon into `'-'`.
  This is good for tiresome modern gobbledygook like `'Re:code'`, which
  will now be translated to `'Re-code'`.

**0.5**

* Initial release.
