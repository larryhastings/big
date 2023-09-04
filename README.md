![# big](https://raw.githubusercontent.com/larryhastings/big/master/resources/images/big.header.png)

##### Copyright 2022-2023 by Larry Hastings

[![# test badge](https://img.shields.io/github/actions/workflow/status/larryhastings/big/test.yml?branch=master&label=test)](https://github.com/larryhastings/big/actions/workflows/test.yml) [![# coverage badge](https://img.shields.io/github/actions/workflow/status/larryhastings/big/coverage.yml?branch=master&label=coverage)](https://github.com/larryhastings/big/actions/workflows/coverage.yml) [![# python versions badge](https://img.shields.io/pypi/pyversions/big.svg?logo=python&logoColor=FBE072)](https://pypi.org/project/big/)


**big** is a Python package of useful little bits of
Python code I always want to have handy.  It's a central
place for code that's useful but not big enough to go in
its own module.

Finally!  For years, I've copied-and-pasted all my little
helper functions between projects--we've all done it.
But now I've finally taken the time to consolidate all those
useful little functions into one *big* package, so they're always
at hand, ready to use.
And, since it's a public package, you can use 'em too!

Not only that, but I've taken my time and re-thought and
retooled a lot of this code.  All the difficult-to-use,
overspecialized, cheap hacks I've lived with for years have
been upgraded with elegant, intuitive APIs and dazzling
functionality.
**big** is chock full of the sort of little functions and classes
we've all hacked together a million times--only with all the
API gotchas fixed, and thoroughly tested with 100% coverage.
It's the code you *would* have written... if only you had the time.
And it's a real pleasure to use!


**big** requires Python 3.6 or newer.  Its only dependency
is `python-dateutil`, and that's optional.  

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
you can access it with just `big.multisplit`.

You can also use **big.all** with `import *`:

```Python
from big.all import *
```

but that's up to you.

**big** is licensed using the
[MIT license.](https://opensource.org/licenses/MIT)
You're free to use it and even ship it in your own programs,
as long as you leave my copyright notice on the source code.

# Index

### Functions, classes, values, and modules

<dl><dd>

[`accessor(attribute='state', state_manager='state_manager')`](#accessorattributestate-state_managerstate_manager)

[`ascii_newlines`](#newlines)

[`ascii_newlines_without_dos`](#newlines)

[`ascii_whitespace`](#whitespace)

[`ascii_whitespace_without_dos`](#whitespace)

[`big.all`](#`bigall`)

[`big.boundinnerclass`](#`bigboundinnerclass`)

[`big.builtin`](#bigbuiltin)

[`big.file`](#bigfile)

[`big.graph`](#biggraph)

[`big.heap`](#bigheap)

[`big.itertools`](#bigitertools)

[`big.log`](#biglog)

[`big.scheduler`](#bigscheduler)

[`big.state`](#bigstate)

[`big.text`](#bigtext)

[`big.time`](#bigtime)

[`BoundInnerClass`](#boundinnerclasscls)

[`CycleError`](#cycleerror)

[`datetime_ensure_timezone(d, timezone)`](#datetime_ensure_timezoned-timezone)

[`datetime_set_timezone(d, timezone)`](#datetime_set_timezoned-timezone)

[`default_clock()`](#default_clock)

[`Delimiter(open, close, *, backslash=False, nested=True)`](#delimiteropen-close--backslashfalse-nestedtrue)

[`dispatch(state_manager='state_manager', *, prefix='', suffix='')`](#dispatchstate_managerstate_manager--prefix-suffix)

[`Event(scheduler, event, time, priority, sequence)`](#eventscheduler-event-time-priority-sequence)

[`Event.cancel()`](#eventcancel)

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

[`int_to_words(i, *, flowery=True, ordinal=False)`](#int_to_wordsi--flowerytrue-ordinalfalse)

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

[`Log`](#log-clocknone)

[`Log.enter(subsystem)`](#logentersubsystem)

[`Log.exit()`](#logexit)

[`Log.print(*, print=None, title="[event log]", headings=True, indent=2, seconds_width=2, fractional_width=9)`](#logprint-printnone-titleevent-log-headingstrue-indent2-seconds_width2-fractional_width9)

[`Log.reset()`](#logreset)

[`merge_columns(*columns, column_separator=" ", overflow_response=OverflowResponse.RAISE, overflow_before=0, overflow_after=0)`](#merge_columnscolumns-column_separator--overflow_responseoverflowresponseraise-overflow_before0-overflow_after0)

[`multipartition(s, separators, count=1, *, reverse=False, separate=True)`](#multipartitions-separators-count1--reverseFalse-separateTrue)

[`multisplit(s, separators, *, keep=False, maxsplit=-1, reverse=False, separate=False, strip=False)`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)

[`multistrip(s, separators, left=True, right=True)`](#multistrips-separators-leftTrue-rightTrue)

[`newlines`](#newlines)

[`newlines_without_dos`](#newlines)

[`normalize_whitespace(s, separators=None, replacement=None)`](#normalize_whitespaces-separatorsNone-replacementnone)

[`parse_delimiters(s, delimiters=None)`](#parse_delimiterss-delimitersNone)

[`parse_timestamp_3339Z(s, *, timezone=None)`](#parse_timestamp_3339zs--timezonenone)

[`pure_virtual`](#pure_virtual)

[`PushbackIterator(iterable=None)`](#pushbackiteratoriterablenone)

[`PushbackIterator.next(default=None)`](#pushbackiteratornextdefaultnone)

[`PushbackIterator.push(o)`](#pushbackiteratorpusho)

[`pushd(directory)`](#pushddirectory)

[`re_partition(text, pattern, count=1, *, flags=0, reverse=False)`](#re_partitiontext-pattern-count1--flags0-reversefalse)

[`re_rpartition(text, pattern, count=1, *, flags=0)`](#re_rpartitiontext-pattern-count1--flags0)

[`Regulator()`](#regulator)

[`Regulator.now()`](#regulatornow)

[`Regulator.sleep(t)`](#regulatorsleept)

[`Regulator.wake()`](#regulatorwake)

[`reversed_re_finditer(pattern, string, flags=0)`](#reversed_re_finditerpattern-string-flags0)

[`safe_mkdir(path)`](#safe_mkdirpath)

[`safe_unlink(path)`](#safe_unlinkpath)

[`Scheduler(regulator=default_regulator)`](#schedulerregulatordefault_regulator)

[`Scheduler.schedule(o, time, *, absolute=False, priority=DEFAULT_PRIORITY)`](#schedulerscheduleo-time--absolutefalse-prioritydefault_priority)

[`Scheduler.cancel(event)`](#schedulercancelevent)

[`Scheduler.queue`](#schedulerqueue)

[`Scheduler.non_blocking()`](#schedulernon_blocking)

[`SingleThreadedRegulator()`](#singlethreadedregulator)

[`split_quoted_strings(s, quotes=('"', "'"), *, triple_quotes=True, backslash='\\')`](#split_quoted_stringss-quotes---triple_quotestrue-backslash)

[`split_text_with_code(s, *, tab_width=8, allow_code=True, code_indent=4, convert_tabs_to_spaces=True)`](#split_text_with_codes--tab_width8-allow_codetrue-code_indent4-convert_tabs_to_spacestrue)

[`State`](#state)

[`StateMachine(state, *, on_enter='on_enter', on_exit='on_exit', state_class=None)`](#statemachinestate--on_enteron_enter-on_exiton_exit-state_classnone)

[`timestamp_3339Z(t=None, want_microseconds=None)`](#timestamp_3339ztnone-want_microsecondsnone)

[`timestamp_human(t=None, want_microseconds=None)`](#timestamp_humantnone-want_microsecondsnone)

[`ThreadSafeRegulator()`](#threadsaferegulator)

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

[`TransitionError`](#transitionerror)

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

</dd></dl>

### Topic deep-dives

<dl><dd>

[**The `multi-` family of string functions**](#The-multi--family-of-string-functions)

[**`lines` and lines modifier functions**](#lines-and-lines-modifier-functions)

[**Word wrapping and formatting**](#word-wrapping-and-formatting)

[**Bound inner classes**](#bound-inner-classes)

[**Enhanced `TopologicalSorter`**](#enhanced-topologicalsorter)

</dd></dl>


# API Reference, By Module


## `big.all`

This submodule doesn't define any of its own symbols.  Instead, it
imports every other submodule in **big**, and uses `import *` to
import every symbol from every other submodule, too.  Every
public symbol in **big** is available in `big.all`.


## `big.boundinnerclass`

Class decorators that implement bound inner classes.  See the
[**Bound inner classes**](#bound-inner-classes)
deep-dive for more information.

#### `BoundInnerClass(cls)`

<dl><dd>

Class decorator for an inner class.  When accessing the inner class
through an instance of the outer class, "binds" the inner class to
the instance.  This changes the signature of the inner class's `__init__`
from
```Python
def __init__(self, *args, **kwargs):`
```
to
```Python
def __init__(self, outer, *args, **kwargs):
```
where `outer` is the instance of the outer class.

Compare this to functions:

* If you put a *function* inside a class,
  and access it through an instance *I* of that class,
  the *function* becomes a *method.*  When you call
  the *method,* *I* is automatically passed in as the
  first argument.
* If you put a *class* inside a class, and access
  and access it through an instance of that class,
  the *class* becomes a *bound inner class.*  When
  you call the *bound inner class,* *I* is automatically
  passed in as the second argument to `__init__`,
  after `self`.

Note that this has an implication for all subclasses.
If class ***B*** is decorated with `BoundInnerClass`,
and class ***S*** is a subclass of ***B***, such that
`issubclass(`***S***`, `***B***`)`,
class ***S*** *must* be decorated with either
`BoundInnerClass` or `UnboundInnerClass`.
</dd></dl>

#### `UnboundInnerClass(cls)`

<dl><dd>

Class decorator for an inner class that prevents binding
the inner class to an instance of the outer class.

If class ***B*** is decorated with `BoundInnerClass`,
and class ***S*** is a subclass of ***B***, such that
`issubclass(`***S***`, `***B***`)` returns `True`,
class ***S*** *must* be decorated with either
`BoundInnerClass` or `UnboundInnerClass`.
</dd></dl>


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

<dl><dd>

Returns `float(o)`, unless that conversion fails,
in which case returns the default value.  If
you don't pass in an explicit default value,
the default value is `o`.
</dd></dl>

#### `get_int(o, default=_sentinel)`

<dl><dd>

Returns `int(o)`, unless that conversion fails,
in which case returns the default value.  If
you don't pass in an explicit default value,
the default value is `o`.
</dd></dl>

#### `get_int_or_float(o, default=_sentinel)`

<dl><dd>

Converts `o` into a number, preferring an int to a float.

If `o` is already an int or float, returns `o` unchanged.  Otherwise,
tries `int(o)`.  If that conversion succeeds, returns the result.
Otherwise, tries `float(o)`.  If that conversion succeeds, returns
the result.  Otherwise returns the default value.  If you don't
pass in an explicit default value, the default value is `o`.
</dd></dl>

#### `pure_virtual()`

<dl><dd>

A decorator for class methods.  When you have a method in
a base class that's "pure virtual"--that must not be called,
but must be overridden in child classes--decorate it with
`@pure_virtual()`.  Calling that method will throw a
`NotImplementedError`.

Note that the body of any function decorated with
`@pure_virtual()` is ignored.  By convention the body
of these methods should contain only a single ellipsis,
literally like this:

```Python
class BaseClass:
    @big.pure_virtual()
    def on_reset(self):
        ...
```
</dd></dl>

#### `try_float(o)`

<dl><dd>

Returns `True` if `o` can be converted into a `float`,
and `False` if it can't.
</dd></dl>

#### `try_int(o)`

<dl><dd>

Returns `True` if `o` can be converted into an `int`,
and `False` if it can't.
</dd></dl>



## `big.file`

Functions for working with files, directories, and I/O.

#### `fgrep(path, text, *, encoding=None, enumerate=False, case_insensitive=False)`

<dl><dd>

Find the lines of a file that match some text, like the UNIX `fgrep` utility
program.

`path` should be an object representing a path to an existing file, one of:

* a string,
* a bytes object, or
* a `pathlib.Path` object.

`text` should be either string or bytes.

`encoding` is used as the file encoding when opening the file.

* If `text` is a str, the file is opened in text mode.
* If `text` is a bytes object, the file is opened in binary mode.
  `encoding` must be `None` when the file is opened in binary mode.

If `case_insensitive` is true, perform the search in a case-insensitive
manner.

Returns a list of lines in the file containing `text`.  The lines are either
strings or bytes objects, depending on the type of `pattern`.  The lines
have their newlines stripped but preserve all other whitespace.

If `enumerate` is true, returns a list of tuples of (line_number, line).
The first line of the file is line number 1.

For simplicity of implementation, the entire file is read in to memory
at one time.  If `case_insensitive` is true, `fgrep` also makes a lowercased
copy.
</dd></dl>

#### `file_mtime(path)`

<dl><dd>

Returns the modification time of `path`, in seconds since the epoch.
Note that seconds is a float, indicating the sub-second with some
precision.
</dd></dl>

#### `file_mtime_ns(path)`

<dl><dd>

Returns the modification time of `path`, in nanoseconds since the epoch.
</dd></dl>

#### `file_size(path)`

<dl><dd>

Returns the size of the file at `path`, as an integer representing the
number of bytes.
</dd></dl>

#### `grep(path, pattern, *, encoding=None, enumerate=False, flags=0)`

<dl><dd>

Look for matches to a regular expression pattern in the lines of a file,
similarly to the UNIX `grep` utility program.

`path` should be an object representing a path to an existing file, one of:

* a string,
* a bytes object, or
* a `pathlib.Path` object.

`pattern` should be an object containing a regular expression, one of:

* a string,
* a bytes object, or
* an `re.Pattern`, initialized with either `str` or `bytes`.

`encoding` is used as the file encoding when opening the file.

If `pattern` uses a `str`, the file is opened in text mode.
If `pattern` uses a bytes object, the file is opened in binary mode.
`encoding` must be `None` when the file is opened in binary mode.

`flags` is passed in as the `flags` argument to `re.compile` if `pattern`
is a string or bytes.  (It's ignored if `pattern` is an `re.Pattern` object.)

Returns a list of lines in the file matching the pattern.  The lines
are either strings or bytes objects, depending on the type of `text`.
The lines have their newlines stripped but preserve all other whitespace.

If `enumerate` is true, returns a list of tuples of `(line_number, line)`.
The first line of the file is line number 1.

For simplicity of implementation, the entire file is read in to memory
at one time.

Tip: to perform a case-insensitive pattern match, pass in the
`re.IGNORECASE` flag into flags for this function (if pattern is a string
or bytes) or when creating your regular expression object (if pattern is
an `re.Pattern` object.

(In older versions of Python, `re.Pattern` was a private type called
`re._pattern_type`.)
</dd></dl>

#### `pushd(directory)`

<dl><dd>

A context manager that temporarily changes the directory.
Example:

```Python
with big.pushd('x'):
    pass
````

This would change into the `'x'` subdirectory before
executing the nested block, then change back to
the original directory after the nested block.

You can change directories in the nested block;
this won't affect pushd restoring the original current
working directory upon exiting the nested block.

You can safely nest `with pushd` blocks.
</dd></dl>

#### `safe_mkdir(path)`

<dl><dd>

Ensures that a directory exists at `path`.
If this function returns and doesn't raise,
it guarantees that a directory exists at `path`.

If a directory already exists at `path`,
`safe_mkdir` does nothing.

If a file exists at `path`, `safe_mkdir`
unlinks `path` then creates the directory.

If the parent directory doesn't exist,
`safe_mkdir` creates that directory,
then creates `path`.

This function can still fail:

* `path` could be on a read-only filesystem.
* You might lack the permissions to create `path`.
* You could ask to create the directory `x/y`
   and `x` is a file (not a directory).

</dd></dl>

#### `safe_unlink(path)`

<dl><dd>

Unlinks `path`, if `path` exists and is a file.
</dd></dl>

#### `touch(path)`

<dl><dd>

Ensures that `path` exists, and its modification time is the current time.

If `path` does not exist, creates an empty file.

If `path` exists, updates its modification time to the current time.
</dd></dl>

#### `translate_filename_to_exfat(s)`

<dl><dd>

Ensures that all characters in s are legal for a FAT filesystem.

Returns a copy of `s` where every character not allowed in a FAT
filesystem filename has been replaced with a character (or characters)
that are permitted.
</dd></dl>

#### `translate_filename_to_unix(s)`

<dl><dd>

Ensures that all characters in s are legal for a UNIX filesystem.

Returns a copy of `s` where every character not allowed in a UNIX
filesystem filename has been replaced with a character (or characters)
that are permitted.
</dd></dl>


## `big.graph`

A drop-in replacement for Python's
[`graphlib.TopologicalSorter`](https://docs.python.org/3/library/graphlib.html#graphlib.TopologicalSorter)
with an enhanced API.  This version of `TopologicalSorter` allows modifying the
graph at any time, and supports multiple simultaneous *views,* allowing
iteration over the graph more than once.

See the [**Enhanced `TopologicalSorter`**](#enhanced-topologicalsorter) deep-dive for more information.

#### `CycleError`

<dl><dd>

Exception thrown by `TopologicalSorter` when it detects a cycle.
</dd></dl>

#### `TopologicalSorter(graph=None)`

<dl><dd>

An object representing a directed graph of nodes.  See Python's
[`graphlib.TopologicalSorter`](https://docs.python.org/3/library/graphlib.html#graphlib.TopologicalSorter)
for concepts and the basic API.
</dd></dl>

New methods on `TopologicalSorter`:

#### `TopologicalSorter.copy()`

<dl><dd>

Returns a shallow copy of the graph.  The copy also duplicates
the state of `get_ready` and `done`.
</dd></dl>

#### `TopologicalSorter.cycle()`

<dl><dd>

Checks the graph for cycles.  If no cycles exist, returns None.
If at least one cycle exists, returns a tuple containing nodes
that constitute a cycle.
</dd></dl>

#### `TopologicalSorter.print(print=print)`

<dl><dd>

Prints the internal state of the graph.  Used for debugging.

`print` is the function used for printing;
it should behave identically to the builtin `print` function.
</dd></dl>

#### `TopologicalSorter.remove(node)`

<dl><dd>

Removes `node` from the graph.

If any node `P` depends on a node `N`, and `N` is removed,
this dependency is also removed, but `P` is not
removed from the graph.

Note that, while `remove()` works, it's slow. (It's O(N).)
`TopologicalSorter` is optimized for fast adds and fast views.
</dd></dl>

#### `TopologicalSorter.reset()`

<dl><dd>

Resets `get_ready` and `done` to their initial state.
</dd></dl>

#### `TopologicalSorter.view()`

<dl><dd>

Returns a new `View` object on this graph.
</dd></dl>

#### `TopologicalSorter.View`

<dl><dd>

A view on a `TopologicalSorter` graph object.
Allows iterating over the nodes of the graph
in dependency order.
</dd></dl>

Methods on a `View` object:

#### `TopologicalSorter.View.__bool__()`

<dl><dd>

Returns `True` if more work can be done in the
view--if there are nodes waiting to be yielded by
`get_ready`, or waiting to be returned by `done`.

Aliased to `TopologicalSorter.is_active` for compatibility
with graphlib.
</dd></dl>

#### `TopologicalSorter.View.close()`

<dl><dd>

Closes the view.  A closed view can no longer be used.
</dd></dl>

#### `TopologicalSorter.View.copy()`

<dl><dd>

Returns a shallow copy of the view, duplicating its current state.
</dd></dl>

#### `TopologicalSorter.View.done(*nodes)`

<dl><dd>

Marks nodes returned by `ready` as "done",
possibly allowing additional nodes to be available
from `ready`.
</dd></dl>

#### `TopologicalSorter.View.print(print=print)`

<dl><dd>

Prints the internal state of the view, and its graph.
Used for debugging.

`print` is the function used for printing;
it should behave identically to the builtin `print` function.
</dd></dl>

#### `TopologicalSorter.View.ready()`

<dl><dd>

Returns a tuple of "ready" nodes--nodes with no
predecessors, or nodes whose predecessors have all
been marked "done".

Aliased to `TopologicalSorter.get_ready` for
compatibility with `graphlib`.
</dd></dl>

#### `TopologicalSorter.View.reset()`

<dl><dd>

Resets the view to its initial state,
forgetting all "ready" and "done" state.
</dd></dl>


## `big.heap`

Functions for working with heap objects.
Well, just one heap object really.

#### `Heap(i=None)`

<dl><dd>

An object-oriented wrapper around the `heapq` library, designed to be
easy to use--and easy to remember how to use.  The `heapq` library
implements a [binary heap](https://en.wikipedia.org/wiki/Binary_heap),
a data structure used for sorting;
you add objects to the heap, and you can then remove
objects in sorted order.  Heaps are useful because they have are efficient
both in space and in time; they're also inflexible, in that iterating over
the sorted items is destructive.

The `Heap` API in **big** mimics the `list` and `collections.deque` objects;
this way, all you need to remember is "it works kinda like a `list` object".
You `append` new items to the heap, then `popleft` them off in sorted order.

By default `Heap` creates an empty heap.  If you pass in an iterable `i`
to the constructor, this is equivalent to calling the `extend(i)` on the
freshly-constructed `Heap`.

In addition to the below methods, `Heap` objects support iteration,
`len`, the `in` operator, and use as a boolean expression.  You can
also index or slice into a `Heap` object, which behaves as if the
heap is a list of objects in sorted order.  Getting the first item
(`Heap[0]`, aka *peek*) is cheap, the other operations can get very
expensive.
</dd></dl>


Methods on a `Heap` object:

#### `Heap.append(o)`

<dl><dd>

Adds object `o` to the heap.
</dd></dl>

#### `Heap.clear()`

<dl><dd>

Removes all objects from the heap, resetting it to empty.
</dd></dl>

#### `Heap.copy()`

<dl><dd>

Returns a shallow copy of the heap.
Only duplicates the heap data structures itself;
does not duplicate the objects *in* the heap.
</dd></dl>

#### `Heap.extend(i)`

<dl><dd>

Adds all the objects from the iterable `i` to the heap.
</dd></dl>

#### `Heap.remove(o)`

<dl><dd>

If object `o` is in the heap, removes it.  If `o` is not
in the heap, raises `ValueError`.
</dd></dl>

#### `Heap.popleft()`

<dl><dd>

If the heap is not empty, returns the first item in the
heap in sorted order.  If the heap is empty, raises `IndexError`.
</dd></dl>

#### `Heap.append_and_popleft(o)`

<dl><dd>

Equivalent to calling `Heap.append(o)` immediately followed
by `Heap.popleft()`.  If `o` is smaller than any other object
in the heap at the time it's added, this will return `o`.
</dd></dl>

#### `Heap.popleft_and_append(o)`

<dl><dd>

Equivalent to calling `Heap.popleft()` immediately followed
by `Heap.append(o)`.  This method will *never* return `o`,
unless `o` was already in the heap before the method was called.
</dd></dl>

#### `Heap.queue`

<dl><dd>

Not a method, a property.  Returns a copy of the contents
of the heap, in sorted order.
</dd></dl>


## `big.itertools`

Functions and classes for working with iteration.
Only one entry so far.

#### `PushbackIterator(iterable=None)`

<dl><dd>

Wraps any iterator, allowing you to push items back on the iterator.
This allows you to "peek" at the next item (or items); you can get the
next item, examine it, and then push it back.  If any objects have
been pushed onto the iterator, they are yielded first, before attempting
to yield from the wrapped iterator.

Pass in any `iterable` to the constructor.  Passing in an `iterable`
of `None` means the `PushbackIterator` is created in an exhausted state.

When the wrapped `iterable` is exhausted (or if you passed in `None`
to the constructor) you can still call push to add new items, at which
point the `PushBackIterator` can be iterated over again.

In addition to the following methods, `PushbackIterator` supports
the iterator protocol and testing for truth.  A `PushbackIterator`
is true if iterating over it will yield at least one value.
</dd></dl>

#### `PushbackIterator.next(default=None)`

<dl><dd>

Equivalent to `next(PushbackIterator)`, but won't raise `StopIteration`.
If the iterator is exhausted, returns the `default` argument.
</dd></dl>

#### `PushbackIterator.push(o)`

<dl><dd>

Pushes a value into the iterator's internal stack.
When a `PushbackIterator` is iterated over, and there are
any pushed values, the top value on the stack will be popped
and yielded.  `PushbackIterator` only yields from the
iterator it wraps when this internal stack is empty.
</dd></dl>


## `big.log`

A simple and lightweight logging class, useful for performance analysis.
Not intended as a full-fledged logging facility like Python's
[`logging`](https://docs.python.org/3/library/logging.html) module.

#### `default_clock()`

<dl><dd>

The default clock function used by the [`Log`](#log-clocknone) class.
This function returns elapsed time in nanoseconds,
expressed as an integer.

In Python 3.7+, this is
[`time.monotonic_ns`](https://docs.python.org/3/library/time.html#time.monotonic_ns);
in Python 3.6 this is
a custom function that calls
[`time.perf_counter`](https://docs.python.org/3/library/time.html#time.perf_counter),
then converts that time to an integer number of nanoseconds.
</dd></dl>

#### `Log(*, clock=None)`

<dl><dd>

A simple and lightweight logging class, useful for performance analysis.
Not intended as a full-fledged logging facility like Python's
[`logging`](https://docs.python.org/3/library/logging.html) module.

Allows nesting, which is literally just a presentation thing.

The `clock` named parameter specifies the function the `Log` object
should call to get the time.  This function should return an `int`,
representing elapsed time in nanoseconds.

To use: first, create your `Log` object.

```Python
log = Log()
```

Then log events by calling your `Log` object, passing in
a string describing the event.

```Python
log('text')
```

Enter a nested subsystem containing events with `log.enter`:

```Python
log.enter('subsystem')
```

Then later exit that subsystem with `log.exit`:

```Python
log.exit()
```

And finally print the log:

```Python
log.print()
```

You can also iterate over the log events using `iter(log)`.
This yields 4-tuples:

```
    (start_time, elapsed_time, event, depth)
```

`start_time` and `elapsed_time` are times, expressed as
an integer number of nanoseconds.  The first event
is at `start_time` 0, and all subsequent start times are
relative to that time.

`event` is the event string you
passed in to `log()` (or `"<subsystem> start"` or
`"<subsystem> end"`).

`depth` is an integer indicating how many subsystems
the event is nested in; larger numbers indicate deeper nesting.
</dd></dl>


#### `Log.enter(subsystem)`

<dl><dd>

Notifies the log that you've entered a subsystem.
The `subsystem` parameter should be a string describing the subsystem.

This is really just a presentation
thing; all subsequent logged entries will be indented
until you make the corresponding `log.exit()` call.

You may nest subsystems as deeply as you like.
</dd></dl>

#### `Log.exit()`

<dl><dd>

Exits a logged subsystem.  See [`Log.enter.`](#logentersubsystem)
</dd></dl>

#### `Log.print(*, print=None, title="[event log]", headings=True, indent=2, seconds_width=2, fractional_width=9)`

<dl><dd>

Prints the log.

Keyword-only parameters:

`print` specifies the print function to use, default is `builtins.print`.

`title` specifies the title to print at the beginning.
Default is `"[event log]"`.  To suppress, pass in `None`.

`headings` is a boolean; if `True` (the default),
prints column headings for the log.

`indent` is the number of spaces to indent in front of log entries,
and also how many spaces to indent each time we enter a subsystem.

`seconds_width` is how wide to make the seconds column, default 2.

`fractional_width` is how wide to make the fractional column, default 9.
</dd></dl>

#### `Log.reset()`

<dl><dd>

Resets the log to its initial state.
</dd></dl>

## `big.scheduler`

A replacement for Python's `sched.scheduler` object,
adding full threading support and a modern Python interface.

Python's `sched.scheduler` object was a clever idea for the
time.  It abstracted away the concept of time from its interface,
allowing it to be adapted to new schemes of measuring time--including
mock time used for testing.  Very nice!

But unfortunately, `sched.scheduler` was designed in 1991--long
before multithreading was common, years before threading support
was added to Python.  Sadly its API isn't flexible enough to
correctly handle some scenarios:

* If one thread has called `sched.scheduler.run`,
  and the next scheduled event will occur at time **T**,
  and a second thread schedules a new event which
  occurs at a time < **T**, `sched.scheduler.run` won't
  return any events to the first thread until time **T**.
* If one thread has called `sched.scheduler.run`,
  and the next scheduled event will occur at time **T**,
  and a second thread cancels all events,
  `sched.scheduler.run` won't exit until time **T**.

Also, `sched.scheduler` is thirty years behind the times in
Python API design--its design predates many common modern
Python conventions.  Its events are callbacks, which it
calls directly.  `Scheduler` fixes this: its events are
objects, and you iterate over the `Scheduler` object to receive
events as they become due.

`Scheduler` also benefits from thirty years of improvements
to `sched.scheduler`.  In particular, **big** reimplements the
relevant parts of the `sched.scheduler` test suite, to ensure that
`Scheduler` never repeats the historical problems discovered
over the lifetime of `sched.scheduler`.

#### `Event(scheduler, event, time, priority, sequence)`

<dl><dd>

An object representing a scheduled event in a `Scheduler`.
You shouldn't need to create them manually; `Event` objects
are created automatically when you add events to a `Scheduler`.

Supports one method:
</dd></dl>

#### `Event.cancel()`

<dl><dd>

Cancels this event.  If this event has already been canceled,
raises `ValueError`.
</dd></dl>

#### `Regulator()`

<dl><dd>

An abstract base class for `Scheduler` regulators.

A "regulator" handles all the details about time
for a `Scheduler`.  `Scheduler` objects don't actually
understand time; it's all abstracted away by the
`Regulator`.

You can implement your own `Regulator` and use it
with `Scheduler`.  Your `Regulator` subclass needs to
implement a minimum of three methods: `now`,
`sleep`, and `wake`.  It must also provide an
attribute called 'lock'.  The lock must implement
the context manager protocol, and should ensure thread
safety for the `Regulator`.  (`Scheduler` will only
request the `Regulator`'s lock if it's not already
holding it.  Put another way, the `Regulator` doesn't
need to be a "reentrant" or "recursive" lock.)

Normally a `Regulator` represents time using
a floating-point number, representing a fractional
number of seconds since some epoch.  But this
isn't strictly necessary.  Any Python object that
fulfills these requirements will work:

* The time class must implement `__le__`, `__eq__`, `__add__`,
  and `__sub__`, and these operations must be consistent in the
  same way they are for number objects.
* If `a` and `b` are instances of the time class,
  and `a.__le__(b)` is true, then `a` must either be
  an earlier time, or a smaller interval of time.
* The time class must also implement rich comparison
  with numbers (integers and floats), and `0` must
  represent both the earliest time and a zero-length
  interval of time.

</dd></dl>


#### `Regulator.now()`

<dl><dd>

Returns the current time in local units.
Must be monotonically increasing; for any
two calls to now during the course of the
program, the later call must *never*
have a lower value than the earlier call.

A `Scheduler` will only call this method while
holding this regulator's lock.
</dd></dl>

#### `Regulator.sleep(t)`

<dl><dd>

Sleeps for some amount of time, in local units.
Must support an interval of `0`, which should
represent not sleeping.  (Though it's preferable
that an interval of `0` yields the rest of the
current thread's remaining time slice back to
the operating system.)

If `wake` is called on this `Regulator` object while a
different thread has called this function to sleep,
`sleep` must abandon the rest of the sleep interval
and return immediately.

A `Scheduler` will only call this method while
*not* holding this regulator's lock.
</dd></dl>

#### `Regulator.wake()`

<dl><dd>

Aborts all current calls to `sleep` on this
`Regulator`, across all threads.

A `Scheduler` will only call this method while
holding this regulator's lock.
</dd></dl>

#### `Scheduler(regulator=default_regulator)`

<dl><dd>

Implements a scheduler.  The only argument is the
"regulator" object to use; the regulator abstracts away all
time-related details for the scheduler.  By default `Scheduler`
uses an instance of `SingleThreadedRegulator`,
which is not thread-safe.

(If you need the scheduler to be thread-safe, pass in an
instance of a thread-safe `Regulator` class like
`ThreadSafeRegulator`.)

In addition to the below methods, `Scheduler` objects support
being evaluated in a boolean context (they are true if they
contain any events), and they support being iterated over.
Iterating over a `Scheduler` object blocks until the next
event comes due, at which point the `Scheduler` yields that
event.  An empty `Scheduler` that is iterated over raises
`StopIteration`.  You can reuse `Scheduler` objects, iterating
over them until empty, then adding more objects and iterating
over them again.
</dd></dl>

#### `Scheduler.schedule(o, time, *, absolute=False, priority=DEFAULT_PRIORITY)`

<dl><dd>

Schedules an object `o` to be yielded as an event by this `schedule` object
at some time in the future.

By default the `time` value is a relative time value,
and is added to the current time; using a `time` value of 0
should schedule this event to be yielded immediately.

If `absolute` is true, `time` is regarded as an absolute time value.

If multiple events are scheduled for the same time, they will
be yielded by order of `priority`.  Lowever values of
`priority` represent higher priorities.  The default value
is `Scheduler.DEFAULT_PRIORITY`, which is 100.  If two events
are scheduled for the same time, and have the same priority,
`Scheduler` will yield the events in the order they were added.

Returns an `Event` object, which can be used to cancel the event.
</dd></dl>

#### `Scheduler.cancel(event)`

<dl><dd>

Cancels a scheduled event.  `event` must be an object
returned by this `Scheduler` object.  If `event` is not
currently scheduled in this `Scheduler` object,
raises `ValueError`.
</dd></dl>

#### `Scheduler.queue`

<dl><dd>

A list of the currently scheduled `Event` objects,
in the order they will be yielded.
</dd></dl>

#### `Scheduler.non_blocking()`

<dl><dd>

Returns an iterator for the events in the
`Scheduler` that only yields the events that
are currently due.  Never blocks; if the next
event is not due yet, raises `StopIteration`.
</dd></dl>

### `SingleThreadedRegulator()`

<dl><dd>

An implementation of `Regulator` designed for
use in single-threaded programs.  It doesn't support
multiple threads, and in particular is not thread-safe.
But it's much higher performance
than thread-safe `Regulator` implementations.

This `Regulator` isn't guaranteed to be safe
for use while in a signal-handler callback.
</dd></dl>

### `ThreadSafeRegulator()`

<dl><dd>

A thread-safe implementation of `Regulator`
designed for use in multithreaded programs.

This `Regulator` isn't guaranteed to be safe
for use while in a signal-handler callback.
</dd></dl>


## `big.state`

Library code for working with simple state machines.

There are lots of popular Python libraries for implementing
state machines.  But they all seem to be designed for
*large-scale* state machines.  These libraries are
sophisticated and data-driven, with expansive APIs.
And, as a rule, they require the state to be
a passive object (e.g. an `Enum`), and require you to explicitly
describe every possible state transition.

This approach is great for massive, super-complex state
machines--you need a sophisticated library to manage such
complex state machines.  This approach also permits these
libraries to offer clever features like automatically generating
diagrams of your state machine.  

However, most of the time, this level of sophistication is
unnecessary.  There are lots of use cases for small scale,
*simple* state machines, where theis complex data-driven approach
only gets in the way.  I prefer writing my state machines
with active objects--where states are implemented as classes,
events are implemented as method calls on those classes,
and you transition to a new state by simply overwriting a
`state` attribute with a new instance of one of these classes.

`big.state` is designed to make it easy to write this style of
state machine.  It has
a deliberately minimal, simple interface--the constructor for
the main `StateManager` class only has four parameters,
and it only exposes three attributes.  The module also has
two decorators to make your life easier.  And that's it!
With that small API surface area, you can effortlessly write
large scale state machines.

(But you can also write tiny data-driven state machines too.
Although `big.state` makes state machines with active states
easy to write, it's agnostic about how you actually implement
your state machine.  `big.state` makes it easy to write any
kind of state machine you like!)

`big.state` provides features like:

* method calls that get called when entering and exiting a state,
* observer objects that get called each time you transition
  to a new state, and
* safety mechanisms to catch bugs and prevent design mistakes.


#### Recommended best practices

The main class in `big.state` is `StateManager`.  This class
maintains the current "state" of your state machine, and
manages transitions to new states.  It takes one required
parameter, which is the initial state.

Here are my recommended best practices for working with
`StateManager` for medium-sized and larger state machines:

* Your state machine should be implemented as a *class.*
    * You should store `StateManager` as an an attribute of that class,
      preferably called `state_manager`.  (Your state machine
      should have a "has-a" relationship with `StateManager`,
      not an "is-a" relationship where it inherits from `StateManager`.)
    * Decorating your state machine class with the
      [`accessor`](accessorattributestate-state_managerstate_manager)
      decorator will save you a lot of boilerplate.
      If your state machine is stored in `o`, decorating with
      `accessor` lets you can access the current state using
      `o.state` instead of `o.state_manager.state`.
* Your states should be implemented as *classes.*
    * You should have a base class for your state classes,
      containing whatever functionality they have in common.
    * You're encouraged to define these state classes *inside*
      your state machine class, and use
      [`BoundInnerClass`](#boundinnerclasscls)
      so they automatically get references to the state machine
      they're a part of.
* Events should be *method calls* made on your state machine object.
    * As a rule, events should be dispatched from the state machine
      to a method call on the current state with the same name.
    * If all the code to handle a particular event lives in the
      states, use the
      [`dispatch`](#dispatchstate_managerstate_manager--prefix-suffix)
      decorator to handle dispatching the call.  This will write
      a new method for you, that calls the equivalent method on
      the current state, passing in all the arguments it received.
    * Your state base class should have a method for every
      event, decorated with [`pure_virtual'](pure_virtual).

#### Example code

Here's a simple example demonstrating all this functionality.
It's a state machine with two states, `On` and `Off`, and
one event method `toggle`.  Calling `toggle` transitions
the state machine from the `Off` state to the `On` state,
and vice-versa.

```Python
from big.all import accessor, BoundInnerClass, dispatch, pure_virtual, StateManager

@accessor()
class StateMachine:
    def __init__(self):
        self.state_manager = StateManager(self.Off())

    @dispatch()
    def toggle(self):
        ...

    @BoundInnerClass
    class State:
        def __init__(self, state_machine):
            self.state_machine = state_machine

        def __repr__(self):
            return f"<{type(self).__name__}>"

        @pure_virtual()
        def toggle(self):
            ...

    @BoundInnerClass
    class Off(State.cls):
        def on_enter(self):
            print("off!")

        def toggle(self):
            sm = self.state_machine
            sm.state = sm.On() # sm.state is the accessor

    @BoundInnerClass
    class On(State.cls):
        def on_enter(self):
            print("on!")

        def toggle(self):
            sm = self.state_machine
            sm.state = sm.Off()

sm = StateMachine()
print(sm.state)
for _ in range(3):
    sm.toggle()
    print(sm.state)
```

For another, more complete example of working with `StateManager`,
see the `test_vending_machine` test code in `tests/test_state.py`
in the **big** source tree.

#### `accessor(attribute='state', state_manager='state_manager')`

<dl><dd>

Class decorator.  Adds a convenient state accessor attribute to your class.

When you have a state machine class containing a `StateMachine`
object, it can be wordy and inconvenient to access the state through
the state machine attribute:

```Python
    class StateMachine:
        def __init__(self):
            self.state_manager = StateManager(self.InitialState)
        ...
    sm = StateMachine()
    # vvvvvvvvvvvvvvvvvvvv that's a lot!
    sm.state_manager.state = NextState()
```

The `accessor` class decorator creates a property for you, a
short-cut that directly accesses the `state` attribute of
your state manager.  Just decorate with `@accessor()`:

```Python
    @accessor()
    class StateMachine:
        def __init__(self):
            self.state_manager = StateManager(self.InitialState)
        ...
    sm = StateMachine()
    # vvvvvv that's a lot shorter!
    sm.state = NextState()
```

The `state` attribute evaluates to the same value:

```Python
    sm.state == sm.state_manager.state
```

And setting it sets the state on your `StateManager` instance.
These two statements now do the same thing:

```Python
    sm.state_manager.state = new_state
    sm.state = new_state
```

By default, this decorator assumes your `StateManager` instance
is in the `state_manager` attribute, and you want to name the new
accessor attribute `state`.  You can override these defaults;
the decorator's first parameter, `attribute`, should be the string used
for the new accessor attribute, and the second parameter,
`state_manager`, should be the name of the attribute where your
`StateManager` instance is stored.

For example, if your state manager is stored in an attribute called `sm`,
and you want the short-cut to be called `st`, you'd decorate your
class with

```Python
@accessor(attribute='st', state_manager='sm')
```
</dd></dl>


#### `dispatch(state_manager='state_manager', *, prefix='', suffix='')`

<dl><dd>

Decorator for state machine event methods,
dispatching the event from the state machine object
to its current state.

`dispatch` helps with the following scenario:

* You have your own state machine class which contains
  a `StateManager` object.
* You want your state machine class to have methods
  representing events.
* Rather than handle those events in your state machine
  object itself, you want to dispatch them to the current
  state.

Simply create a method in your state machine class
with the correct name and parameters but a no-op body,
and decorate it with `@dispatch`.  The `dispatch`
decorator will rewrite your method so it calls the
equivalent method on the current state, passing through
all the arguments.

For example, instead of writing this:

```Python
    class StateMachine:
        def __init__(self):
            self.state_manager = StateManager(self.InitialState)

        def on_sunrise(self, time, *, verbose=False):
            return self.state_manager.state.on_sunrise(time, verbose=verbose)
```

you can literally write this, which does the same thing:

```Python
    class StateMachine:
        def __init__(self):
            self.state_manager = StateManager(self.InitialState)

        @dispatch()
        def on_sunrise(self, time, *, verbose=False):
            ...
```

Here, the `on_sunrise` function you wrote is actually thrown away.
(That's why the body is simply one `"..."` statement.)  Your function
is replaced with a function that gets the `state_manager` attribute
from `self`, then gets the `state` attribute from that `StateManager`
instance, then calls a method with the same name as the decorated
function, passing in using `*args` and `**kwargs`.

Note that, as a stylistic convention, you're encouraged to literally
use a single ellipsis as the body of these functions, like in the
example above.  This is a visual cue to readers that the body of the
function doesn't matter.

The `state_manager` argument to the decorator should be the name of
the attribute where the `StateManager` instance is stored in `self`.
The default is `'state_manager'`, but you can specify a different
string if you've stored your `StateManager` in another attribute.
For example, if your state manager is in the attribute `smedley`,
you'd decorate with:

```Python
    @dispatch('smedley')
```

The `prefix` and `suffix` arguments are strings added to the
beginning and end of the method call we call on the current state.
For example, if you want the method you call to have an active verb
form (e.g. `reset`), but you want it to directly call an event
handler that starts with `on_` by convention (e.g. `on_reset`),
you could do this:

```Python
    @dispatch(prefix='on_')
    def reset(self):
        ...
```

This is equivalent to:

```Python
    def reset(self):
        return self.state_manager.state.on_reset()
```

If you have more than one event method, instead of decorating
every event method with the same copy-and-pasted `dispatch`
call, it's better to call `dispatch` once, cache the
function it returns, and decorate with that.  Like so:

```Python
    my_dispatch = dispatch('smedley', prefix='on_')

    @my_dispatch
    def reset(self):
        ...

    @my_dispatch
    def sunrise(self):
        ...
```

</dd></dl>


#### State

<dl><dd>

Base class for state machine state implementation classes.
Use of this base class is optional; states can be instances
of any type except `types.NoneType`.

</dd></dl>

#### `StateMachine(state, *, on_enter='on_enter', on_exit='on_exit', state_class=None)`

<dl><dd>

Simple, Pythonic state machine manager.

Has three public attributes:

<dl><dt>

`state`
</dt><dd>

The current state.  You transition from
one state to another by assigning to this attribute.

</dd><dt>

`next`
</dt><dd>

The state the `StateManager` is transitioning to,
if it's currently in the process of transitioning to a
new state.  If the `StateManager` isn't currently
transitioning to a new state, its `next` attribute is `None`.
While the manager is currently transitioning to a new
state, it's illegal to start a second transition.  (In
other words: you can't assign to `state` while `next` is not
`None`.)


</dd><dt>

`observers`
</dt><dd>

A list of callables that get called
during every state transition.  It's initially empty;
you should add and remove observers to the list
as needed.

* The callables will be called with one positional argument,
  the state manager object.
* Since observers are called during the state transition,
  they aren't permitted to initiate state transitions.
* You're permitted to modify the list of observers
  at any time.  If you modify the list of observers
  during an observer call, `StateManager` will finish
  the current observer callbacks using a copy of the
  old list.

</dd></dl>

The constructor takes the following parameters:

<dl><dt>

`state`
</dt><dd>

The initial state.  It can be any valid state object;
by default, any Python value can be a state except `None`.
(But also see the `state_class` parameter below.)

</dd><dt>

`on_enter`
</dt><dd>

`on_enter` represents a method call on states called when
entering that state.  The value itself is a string used
to look up an attribute on state objects; by default
`on_enter` is the string `'on_enter'`, but it can be any legal
Python identifier string, or any false value.

If `on_enter` is a valid identifier string, and this `StateMachine`
object transitions to a state object *O*, and *O* has an attribute
with this name, `StateMachine` will call that attribute (with no
arguments) immediately after transitioning to that state.
Passing in a false value for `on_enter` disables this behavior.

`on_enter` is called immediately after the transition is complete,
which means you're expressly permitted to make a state transition
inside an `on_enter` call.

If defined, `on_exit` will be called on
the initial state object, from inside the `StateManager` constructor.


</dd><dt>

`on_exit`
</dt><dd>

`on_exit` is similar to `on_enter`, except the attribute is
called when transitioning *away* from a state object.
Its default value is `'on_exit'``.

`on_exit` is called
*during* the state transition, which means you're expressly
forbidden from making a state transition inside an `on_exit` call.

</dd><dt>

`state_class`
</dt><dd>

`state_class` is used to enforce that this `StateManager`
only ever transitions to valid state objects.
It should be either `None` or a class.  If it's a class,
the `StateManager` object will require every value assigned
to its `state` attribute to be an instance of that class.
If it's `None`, states can be any object (except `None`).

</dd></dl>

#### State transitions

To transition to a new state, simply assign to the 'state'
attribute.

* If `state_class` is `None`, you may use *any* value as a state
  except `None`.
* It's illegal to assign to `state` while currently
  transitioning to a new state.  (Or, in other words,
  at any time `self.next` is not `None`.)
* If the current state object has an `on_exit` method,
  it will be called (with zero arguments) *during*
  the the transition to the next state.  This means it's
  illegal to initiate a state transition inside an `on_exit`
  call.
* If you assign an object to `state` that has an `on_enter`
  attribute, that method will be called (with zero
  arguments) immediately *after* we have transitioned to that
  state.  This means it's permitted to initiate a state
  transition inside an `on_enter` call.
* It's illegal to attempt to transition to the current
  state.  If `state_manager.state` is already `foo`,
  `state_manager.state = foo` will raise an exception.

#### Sequence of events during a state transition

If you have an `StateManager` instance called `state_manager`,
and you transition it to `new_state`:

```Python
    state_manager.state = new_state
```

`StateManager` will execute the following sequence of events:

* Set `state_manager.next` to `new_state`.
    * At of this moment `state_manager` is "transitioning"
      to the new state.
* If `state_manager.state` has an `on_exit` attribute,
  call `state_manager.state.on_exit()`.
* For every object `o` in the `state_manager.observer` list,
  call `o(self)`.
* Set `state_manager.next` to `None`.
* Set `state_manager.state` to `new_state`.
    * As of this moment, the transition is complete, and
      `state_manager` is now "in" the new state.
* If `state_manager.state` has an `on_enter` attribute,
  call `state_manager.state.on_enter()`.
</dd></dl>


#### `TransitionError`

<dl><dd>
Exception raised when attempting to execute an illegal state transition.

There are only two types of illegal state transitions:

* An attempted state transition while we're in the process
  of transitioning to another state.  In other words,
  if `state_manager` is your `StateManager` object, you can't
  set `state_manager.state` when `state_manager.next` is not `None`.

* An attempt to transition to the current state.
  This is illegal:

```Python
  state_manager = StateManager()
  state_manager.state = foo
  state_manager.state = foo # <-- this statement raises TransitionError
```

<dl><dd>

  Note that transitioning to a different but *identical* object
   is expressly permitted.
</dd></dl>

</dd></dl>


## `big.text`

Functions for working with text strings.  There are
several families of functions inside the `text` module;
for a higher-level view of those families, read the
following deep-dives:

* [**The `multi-` family of string functions**](#The-multi--family-of-string-functions)
* [**`lines` and lines modifier functions**](#lines-and-lines-modifier-functions)
* [**Word wrapping and formatting**](#word-wrapping-and-formatting)

All the functions in `big.text` will work with either
`str` or `bytes` objects, except the three
[**Word wrapping and formatting**](#word-wrapping-and-formatting)
functions.  When working with `bytes`,
by default the functions will only work with ASCII
characters.

#### Support for bytes and str

The **big** text functions all support both `str` and `bytes`.
The functions all automatically detect whether you passed in
`str` or `bytes`  using an
intentionally simple and predictable process, as follows:

At the start of each function, it'll test its first "string"
argument to see if it's a `bytes` object.

```Python
is_bytes = isinstance(<argument>, bytes)
```

If `isinstance` returns `True`, the function assumes all arguments are
`bytes` objects.  Otherwise the function assumes all arguments
are `str` objects.

As a rule, no further further testing, casting, or catching exceptions
is done.

Functions that take multiple string-like parameters require all
such arguments to be the same type.
These functions will check that all such arguments
are of the same type.

Subclasses of `str` and `bytes` will also work; anywhere you
should pass in a `str`, you can also pass in a subclass of
`str`, and likewise for `bytes`.

#### `Delimiter(open, close, *, backslash=False, nested=True)`

<dl><dd>

Class representing a delimiter for
[`parse_delimiters`.](#parse_delimiterss-delimitersNone)

`open` is the opening delimiter character, can be `str` or `bytes`, must be length 1.

`close` is the closing delimiter character, must be the same type as `open`, and length 1.

`backslash` is a boolean: when inside this delimiter, can you escape delimiters
with a backslash?  (You usually can inside single or double quotes.)

`nested` is a boolean: must other delimiters nest in this delimiter?
(Delimiters don't usually need to be nested inside single and double quotes.)
</dd></dl>

#### `gently_title(s, *, apostrophes=None, double_quotes=None)`

<dl><dd>

Uppercase the first character of every word in `s`.
Leave the other letters alone.  s should be `str` or `bytes`.

(For the purposes of this algorithm, words are
any contiguous run of non-whitespace characters.)

Capitalize the letter after an apostrophe if

* the apostrophe is after whitespace or a left parenthesis character (`'('`)
  (or is the first letter of the string), or
* if the apostrophe is after a letter O or D, and that O or D is after
  whitespace (or is the first letter of the string).  The O or D
  here will also be capitalized.

The first rule handles internally quoted strings:

```
    He Said 'No I Did Not'
```

and contractions that start with an apostrophe

```
    'Twas The Night Before Christmas
```

The second rule handles certain Irish, French,
and Italian names.

```
    Peter O'Toole
    Lord D'Arcy
```

Capitalize the letter after a quote mark if
the quote mark is after whitespace (or is the
first letter of a string).

A run of consecutive apostrophes and/or
quote marks is considered one quote mark for
the purposes of capitalization.

If specified, `apostrophes` should be a `str`
or `bytes` object containing characters that
should be considered apostrophes.  If `apostrophes`
is false, and `s` is `bytes`, `apostrophes` is set to `"'"`.
If `apostrophes` is false and s is `str`, `apostrophes`
is set to a string containing these Unicode apostrophe code points:

```
    '‘’‚‛
```

If specified, `double_quotes` should be a `str`
or `bytes` object containing characters that
should be considered double-quote characters.
If `double_quotes` is false, and `s` is `bytes`,
`double_quotes` is set to "'".
If `double_quotes` is false and `s` is `str`, double_quotes
is set to a string containing these Unicode double quote code points:

```
    "“”„‟«»‹›
```
</dd></dl>

#### `int_to_words(i, *, flowery=True, ordinal=False)`

<dl><dd>

Converts an integer into the equivalent English string.

```Python
int_to_words(2) -> "two"
int_to_words(35) -> "thirty-five"
```

If the keyword-only parameter `flowery` is true (the default),
you also get commas and the word `and` where you'd expect them.
(When `flowery` is true, `int_to_words(i)` produces identical
output to `inflect.engine().number_to_words(i)`, except for
negative numbers: `inflect` starts negative numbers with
"minus", **big** starts them with "negative".)

If the keyword-only parameter `ordinal` is true,
the string produced describes that *ordinal* number
(instead of that *cardinal* number).  Ordinal numbers
describe position, e.g. where a competitor placed in
a competition.  In other words, `int_to_words(1)`
returns the string `'one'`, but
`int_to_words(1, ordinal=True)` returns the
string `'first'`.

Numbers >= `10**66` (one thousand vigintillion)
are only converted using `str(i)`.  Sorry!
</dd></dl>

#### `lines(s, separators=None, *, line_number=1, column_number=1, tab_width=8, **kwargs)`

<dl><dd>

A "lines iterator" object.  Splits s into lines, and iterates yielding those lines.

`s` can be `str`, `bytes`, or any iterable of `str` or `bytes`.

If `s` is neither `str` nor `bytes`, `s` must be an iterable;
`lines` yields successive elements of `s` as lines.  All objects
yielded by this iterable should be homogeneous, either `str` or `bytes`.

If `s` is `str` or `bytes`, and `separators` is `None`, `lines`
will split `s` at line boundaries and yield those lines, including
empty lines.  If `separators` is not `None`, it must be an iterable
of strings of the same type as `s`; `lines` will split `s` using
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse).

When iterated over, yields 2-tuples:

```
     (info, line)
```

`info` is a `LineInfo` object, which contains three fields by
default:

* `line` - the original line, never modified
* `line_number` - the line number of this line, starting at the
  `line_number` passed in and adding 1 for each successive line
* `column_number` - the column this line starts on,
  starting at the `column_number` passed in, and adjusted when
  characters are removed from the beginning of `line`

The `tab_width` keyword-only parameter is an integer, representing
how many spaces wide a tab character should be.  It isn't used by
`lines` itself; instead, it's stored internally, and may be used by
lines modifier functions (e.g. `lines_convert_tabs_to_spaces`,
`lines_strip_indent`).  Similarly, all keyword arguments passed
in via `kwargs` are stored internally and can be accessed by
user-defined lines modifier functions.

For more information, see the deep-dive on
[**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)
</dd></dl>

#### `LineInfo(line, line_number, column_number, **kwargs)`

<dl><dd>

The second object yielded by a
[`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs)
iterator, containing metadata about the line.
You can add your own fields by passing them in
via `**kwargs`; you can also add new attributes
or modify existing attributes as needed from
inside a "lines modifier" function.

For more information, see the deep-dive on
[**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)
</dd></dl>

#### `lines_convert_tabs_to_spaces(li)`

<dl><dd>

A lines modifier function.  Converts tabs to spaces for the lines
of a "lines iterator", using the `tab_width` passed in to
[`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs).

For more information, see the deep-dive on
[**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)
</dd></dl>

#### `lines_filter_comment_lines(li, comment_separators)`

<dl><dd>

A lines modifier function.  Filters out comment lines from the
lines of a "lines iterator".  Comment lines are lines whose
first non-whitespace characters appear in the iterable of
`comment_separators` strings passed in.

What's the difference between
[`lines_strip_comments`](#lines_strip_commentsli-comment_separators--quotes--backslash-rstriptrue-triple_quotestrue)
and
[`lines_filter_comment_lines`](#lines_filter_comment_linesli-comment_separators)?

* [`lines_filter_comment_lines`](#lines_filter_comment_linesli-comment_separators)
  only recognizes lines that *start* with a comment separator
  (ignoring leading whitespace).  Also, it filters out those
  lines completely, rather than modifying the line.
* [`lines_strip_comments`](#lines_strip_commentsli-comment_separators--quotes--backslash-rstriptrue-triple_quotestrue)
  handles comment characters anywhere in the line, although it can ignore
  comments inside quoted strings.  It truncates the line but still always
  yields the line.

For more information, see the deep-dive on
[**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)
</dd></dl>

#### `lines_containing(li, s, *, invert=False)`

<dl><dd>

A lines modifier function.  Only yields lines
that contain `s`.  (Filters out lines that
don't contain `s`.)

If `invert` is true, returns the opposite--
filters out lines that contain `s`.

For more information, see the deep-dive on
[**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)
</dd></dl>

#### `lines_grep(li, pattern, *, invert=False, flags=0)`

<dl><dd>

A lines modifier function.  Only yields lines
that match the regular expression `pattern`.
(Filters out lines that don't match `pattern`.)

`pattern` can be `str`, `bytes`, or an `re.Pattern` object.
If `pattern` is not an `re.Pattern` object, it's compiled
with `re.compile(pattern, flags=flags)`.

If `invert` is true, returns the opposite--
filters out lines that match `pattern`.

For more information, see the deep-dive on
[**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)

(In older versions of Python, `re.Pattern` was a private type called
`re._pattern_type`.)
</dd></dl>

#### `lines_rstrip(li)`

<dl><dd>

A lines modifier function.  Strips trailing whitespace from the
lines of a "lines iterator".

For more information, see the deep-dive on
[**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)
</dd></dl>

#### `lines_sort(li, *, reverse=False)`

<dl><dd>

A lines modifier function.  Sorts all input lines before
yielding them.

Lines are sorted lexicographically, from lowest to highest.
If `reverse` is true, lines are sorted from highest to lowest.

For more information, see the deep-dive on
[**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)
</dd></dl>

#### `lines_strip(li)`

<dl><dd>

A lines modifier function.  Strips leading and trailing whitespace
from the lines of a "lines iterator".

If `lines_strip` removes leading whitespace from a line,
it updates `LineInfo.column_number` with the new starting
column number, and also adds a field to the `LinesInfo` object:

* `leading` - the leading whitespace string that was removed

For more information, see the deep-dive on
[**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)
</dd></dl>

#### `lines_strip_comments(li, comment_separators, *, quotes=('"', "'"), backslash='\\', rstrip=True, triple_quotes=True)`

<dl><dd>

A lines modifier function.  Strips comments from the lines
of a "lines iterator".  Comments are substrings that indicate
the rest of the line should be ignored; `lines_strip_comments`
truncates the line at the beginning of the leftmost comment
separator.

If `rstrip` is true (the default), `lines_strip_comments` calls
the `rstrip()` method on `line` after it truncates the line.

If `quotes` is true, it must be an iterable of quote characters.
(Each quote character *must* be a single character.)
`lines_strip_comments` will parse the line and ignore comment
characters inside quoted strings.  If `quotes` is false,
quote characters are ignored and `line_strip_comments` will truncate
anywhere in the line.

`backslash` and `triple_quotes` are passed in to
`split_quoted_string`, which is used internally to detect the quoted
strings in the line.

Sets a new field on the associated `LineInfo` object for every line:

* `comment` - the comment stripped from the line, if any.
  If no comment was found, `comment` will be an empty string.

What's the difference between
[`lines_strip_comments`](#lines_strip_commentsli-comment_separators--quotes--backslash-rstriptrue-triple_quotestrue)
and
[`lines_filter_comment_lines`](#lines_filter_comment_linesli-comment_separators)?

* [`lines_filter_comment_lines`](#lines_filter_comment_linesli-comment_separators)
  only recognizes lines that *start* with a comment separator
  (ignoring leading whitespace).  Also, it filters out those lines
  completely, rather than modifying the line.
* [`lines_strip_comments`](#lines_strip_commentsli-comment_separators--quotes--backslash-rstriptrue-triple_quotestrue)
  handles comment characters anywhere in the line, although it can ignore
  comments inside quoted strings.  It truncates the line but still always
  yields the line.

For more information, see the deep-dive on
[**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)
</dd></dl>

#### `lines_strip_indent(li)`

<dl><dd>

A lines modifier function.  Automatically measures and strips indents.

Sets two new fields on the associated `LineInfo` object for every line:

* `indent` - an integer indicating how many indents it's observed
* `leading` - the leading whitespace string that was removed

Also updates LineInfo.column_number as needed.

Uses an intentionally simple algorithm.
Only understands tab and space characters as indent characters.
Internally detabs to spaces first for consistency, using the
`tab_width` passed in to lines.

You can only dedent out to a previous indent.
Raises `IndentationError` if there's an illegal dedent.

For more information, see the deep-dive on
[**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)
</dd></dl>

#### `merge_columns(*columns, column_separator=" ", overflow_response=OverflowResponse.RAISE, overflow_before=0, overflow_after=0)`

<dl><dd>

Merge an arbitrary number of separate text strings into
columns.  Returns a single formatted string.

`columns` should be an iterable of "column tuples".
Each column tuple should contain three items:
```Python
(text, min_width, max_width)
```

`text` should be a single string, either `str` or `bytes`,
with newline characters separating lines. `min_width`
and `max_width` are the minimum and maximum permissible widths
for that column, not including the column separator (if any).

Note that this function does not text-wrap the text of the
columns.  The text in the columns should already be broken
into lines and separated by newline characters.  (Lines in
that are longer than that column tuple's `max_width` are
handled with the `overflow_strategy`, below.)

`column_separator` is printed between every column.

`overflow_strategy` tells merge_columns how to handle a column
with one or more lines that are wider than that column's `max_width`.
The supported values are:

* `OverflowStrategy.RAISE`: Raise an OverflowError.  The default.
* `OverflowStrategy.INTRUDE_ALL`: Intrude into all subsequent columns
  on all lines where the overflowed column is wider than its `max_width`.
* `OverflowStrategy.DELAY_ALL`: Delay all columns after the overflowed
  column, not beginning any until after the last overflowed line
  in the overflowed column.

When `overflow_strategy` is `INTRUDE_ALL` or `DELAY_ALL`, and
either `overflow_before` or `overflow_after` is nonzero, these
specify the number of extra lines before or after
the overflowed lines in a column.

For more information, see the deep-dive on
[**Word wrapping and formatting.**](#word-wrapping-and-formatting)
</dd></dl>

#### `multipartition(s, separators, count=1, *, reverse=False, separate=True)`

<dl><dd>

Like `str.partition`, but supports partitioning based on multiple
separator strings, and can partition more than once.

`s` can be either `str` or `bytes`.

`separators` should be an iterable of objects of the same type as `s`.

By default, if any of the strings in `separators` are found in `s`,
returns a tuple of three strings: the portion of `s` leading up to
the earliest separator, the separator, and the portion of `s` after
that separator.  Example:

```
multipartition('aXbYz', ('X', 'Y')) => ('a', 'X', 'bYz')
```

If none of the separators are found in the string, returns
a tuple containing `s` unchanged followed by two empty strings.

`multipartition` is *greedy:* if two or more separators appear at
the leftmost location in `s`, `multipartition` partitions using
the longest matching separator.  For example:

```
multipartition('wxabcyz', ('a', 'abc')) => `('wx', 'abc', 'yz')`
```

Passing in an explicit `count` lets you control how many times
`multipartition` partitions the string.  `multipartition` will always
return a tuple containing `(2*count)+1` elements.
Passing in a `count` of 0 will always return a tuple containing `s`.

If `separate` is true, multiple adjacent separator strings behave
like one separator.  Example:

```
big.text.multipartition('aXYbYXc', ('X', 'Y',), count=2, separate=False) => ('a', 'XY', 'b', 'YX', 'c')
big.text.multipartition('aXYbYXc', ('X', 'Y',), count=2, separate=True ) => ('a', 'X', '', 'Y', 'bYXc')
```

If `reverse` is true, multipartition behaves like `str.rpartition`.
It partitions starting on the right, scanning backwards through s
looking for separators.

For more information, see the deep-dive on
[**The `multi-` family of string functions.**](#The-multi--family-of-string-functions)
</dd></dl>

#### `multisplit(s, separators, *, keep=False, maxsplit=-1, reverse=False, separate=False, strip=False)`

<dl><dd>

Splits strings like `str.split`, but with multiple separators and options.

`s` can be `str` or `bytes`.

`separators` should be an iterable of `str` or `bytes`, matching `s`.

Returns an iterator yielding the strings split from `s`.  If `keep`
is true (or `ALTERNATING`), and `strip` is false, joining these strings
together will recreate `s`.

`multisplit` is *greedy:* if two or more separators start at the same
location in `s`, `multisplit` splits using the longest matching separator.
For example:

```Python
big.multisplit('wxabcyz', ('a', 'abc'))
```

yields `'wx'` then `'yz'`.

`keep` indicates whether or not multisplit should preserve the separator
strings in the strings it yields.  It supports four values:

<dl><dt>

false (the default)
</dt><dd>

Discard the separators.

</dd><dt>

true (apart from `ALTERNATING` and `AS_PAIRS`)
</dt><dd>

Append the separators to the end of the split strings.
You can recreate the original string by passing the
list returned in to "".join .

</dd><dt>

`ALTERNATING`
</dt><dd>

Yield alternating strings in the output: strings consisting
of separators, alternating with strings consisting of
non-separators.  If "separate" is true, separator strings
will contain exactly one separator, and non-separator strings
may be empty; if "separate" is false, separator strings will
contain one or more separators, and non-separator strings
will never be empty, unless "s" was empty.
You can recreate the original string by passing the
list returned in to "".join .

</dd><dt>

`AS_PAIRS`
</dt><dd>

Yield 2-tuples containing a non-separator string and its
subsequent separator string.  Either string may be empty;
the separator string in the last 2-tuple will always be
empty, and if "s" ends with a separator string, *both*
strings in the final 2-tuple will be empty.
</dd></dl>


`separate` indicates whether multisplit should consider adjacent
separator strings in `s` as one separator or as multiple separators
each separated by a zero-length string.  It supports two values:

<dl><dt>

false (the default)
</dt><dd>

Group separators together.  Multiple adjacent separators
behave as if they're one big separator.
</dd><dt>

true
</dt><dd>

Don't group separators together.  Each separator should
split the string individually, even if there are no
characters between two separators.  (`multisplit` will
behave as if there's a zero-character-wide string between
adjacent separators.)
</dd></dl>

`strip` indicates whether multisplit should strip separators from
the beginning and/or end of `s`.  It supports five values:

<dl><dt>

false (the default)
</dt><dd>
Don't strip separators from the beginning or end of "s".

</dd><dt>

true (apart from LEFT, RIGHT, and PROGRESSIVE)
</dt><dd>
Strip separators from the beginning and end of "s"
(similarly to `str.strip`).

</dd><dt>

`LEFT`
</dt><dd>
Strip separators only from the beginning of "s"
(similarly to `str.lstrip`).

</dd><dt>

`RIGHT`
</dt><dd>
Strip separators only from the end of "s"
(similarly to `str.rstrip`).

</dd><dt>

`PROGRESSIVE`
</dt><dd>
Strip from the beginning and end of "s", unless "maxsplit"
is nonzero and the entire string is not split.  If
splitting stops due to "maxsplit" before the entire string
is split, and "reverse" is false, don't strip the end of
the string. If splitting stops due to "maxsplit" before
the entire string is split, and "reverse" is true, don't
strip the beginning of the string.  (This is how `str.strip`
and `str.rstrip` behave when you pass in `sep=None`.)
</dd></dl>

`maxsplit` should be either an integer or `None`.  If `maxsplit` is an
integer greater than -1, multisplit will split `text` no more than
`maxsplit` times.

`reverse` changes where `multisplit` starts splitting the string, and
what direction it moves through the string when parsing.

<dl><dt>

false (the default)
</dt><dd>
Start splitting from the beginning of the string
and parse moving right (towards the end).

</dd><dt>

true
</dt><dd>
Start splitting from the end of the string and
parse moving left (towards the beginning).

</dd></dl>

Splitting starting from the end of the string and parsing moving
left has two effects.  First, if `maxsplit` is a number
greater than 0, the splits will start at the end of the string
rather than the beginning.  Second, if there are overlapping
instances of separators in the string, `multisplit` will prefer
the *rightmost* separator rather than the *leftmost.*  Consider this
example, where `reverse` is false:

```
multisplit("A x x Z", (" x ",), keep=big.ALTERNATING) => "A", " x ", "x Z"
```

If you pass in a true value for `reverse`, `multisplit` will prefer
the rightmost overlapping separator:

```
multisplit("A x x Z", (" x ",), keep=big.ALTERNATING, reverse=True) => "A x", " x ", "Z"
```

For more information, see the deep-dive on
[**The `multi-` family of string functions.**](#The-multi--family-of-string-functions)
</dd></dl>

#### `multistrip(s, separators, left=True, right=True)`

<dl><dd>

Like `str.strip`, but supports stripping multiple substrings from `s`.

Strips from the string `s` all leading and trailing instances of strings
found in `separators`.

`s` should be `str` or `bytes`.

`separators` should be an iterable of either `str` or `bytes`
objects matching the type of `s`.

If `left` is a true value, strips all leading separators
from `s`.

If `right` is a true value, strips all trailing separators
from `s`.

Processing always stops at the first character that
doesn't match one of the separators.

Returns a copy of `s` with the leading and/or trailing
separators stripped.  (If `left` and `right` are both
false, returns `s` unchanged.)

For more information, see the deep-dive on
[**The `multi-` family of string functions.**](#The-multi--family-of-string-functions)
</dd></dl>

#### `newlines`

<dl><dd>

A list of all newline characters recognized by Python.
Includes many Unicode newline characters, like `'\u2029'`
(a paragraph separator).  Useful as a list of separator
strings for
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
et al; `newlines` is specifically used by the
[`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs)
iterator constructor.

**big** also defines `utf8_newlines`, which is `newlines`
with all strings encoded to UTF-8 (as bytes),
and `ascii_newlines`, with all strings converted into
bytes and all characters with code points greater than
128 discarded.

Note that `newlines` contains `'\r\n'`, the DOS sequence
of characters representing a newline.  This lets **big**
text-processing functions recognize this sequence as a
*single* newline marker, rather than as two *separate*
newline characters.  If you don't want this behavior,
you can use `newlines_without_dos` instead.
(**big** also provides `utf8_newlines_without_dos` and
`ascii_newlines_without_dos`.)
</dd></dl>


#### `normalize_whitespace(s, separators=None, replacement=None)`

<dl><dd>

Returns `s`, but with every run of consecutive
separator characters turned into a replacement string.
By default turns all runs of consecutive whitespace
characters into a single space character.

`s` may be `str` or `bytes`.

`separators` should be an iterable of either `str` or `bytes`
objects, matching `s`.

`replacement` should be either a `str` or `bytes` object,
also matching `s`, or `None` (the default).
If `replacement` is `None`, `normalize_whitespace` will use
a replacement string consisting of a single space character.

Leading or trailing runs of separator characters will
be replaced with the replacement string, e.g.:

```
normalize_whitespace("   a    b   c") == " a b c"
```
</dd></dl>

#### `parse_delimiters(s, delimiters=None)`

<dl><dd>

Parses a string containing nesting delimiters.
Raises an exception if mismatched delimiters are detected.

`s` may be `str` or `bytes`.

`delimiters` may be either `None` or an iterable containing
either
[`Delimiter`](#delimiteropen-close--backslashfalse-nestedtrue)
objects or objects matching `s` (`str` or `bytes`).
Entries in the `delimiters` iterable which are `str` or `bytes`
should be exactly two characters long; these will be used
as the `open` and `close` arguments for a new `Delimiter` object.

If `delimiters` is `None`, `parse_delimiters` uses a default
value matching these pairs of delimiters:

```
() [] {} "" ''
```

The quote mark delimiters enable backslash quoting and disable nesting.

Yields 3-tuples containing strings:

```
(text, open, close)
```

where `text` is the text before the next opening or closing delimiter,
`open` is the trailing opening delimiter,
and `close` is the trailing closing delimiter.
At least one of these three strings will always be non-empty.
If `open` is non-empty, `close` will be empty, and vice-versa.
If `s` does not end with a closing delimiter, in the final tuple
yielded, both `open` and `close` will be empty strings.

(Concatenating every string yielded by `parse_delimiters` together
produces a new string identical to `s`.)

You can only specify a particular character as an opening delimiter
once, though you may reuse a particular character as a closing
delimiter multiple times.
</dd></dl>

#### `re_partition(text, pattern, count=1, *, flags=0, reverse=False)`

<dl><dd>

Like `str.partition`, but `pattern` is matched as a regular expression.

`text` can be a string or a bytes object.

`pattern` can be a string, bytes, or `re.Pattern` object.

`text` and `pattern` (or `pattern.pattern`) must be the same type.

If `pattern` is found in text, returns a tuple

```Python
(before, match, after)
```

where `before` is the text before the matched text,
`match` is the `re.Match` object resulting from the match, and
`after` is the text after the matched text.

If `pattern` appears in `text` multiple times,
`re_partition` will match against the first (leftmost)
appearance.

If `pattern` is not found in `text`, returns a tuple

```Python
(text, None, '')
```

where the empty string is `str` or `bytes` as appropriate.

Passing in an explicit `count` lets you control how many times
`re_partition` partitions the string.  `re_partition` will always
return a tuple containing `(2*count)+1` elements, and
odd-numbered elements will be either `re.Match` objects or `None`.
Passing in a `count` of 0 will always return a tuple containing `s`.

If `pattern` is a string or bytes object, `flags` is passed in
as the `flags` argument to `re.compile`.

If `reverse` is true, partitions starting at the right,
like [`re_rpartition`](#re_rpartitiontext-pattern-count1--flags0).

(In older versions of Python, `re.Pattern` was a private type called
`re._pattern_type`.)
</dd></dl>

#### `re_rpartition(text, pattern, count=1, *, flags=0)`

<dl><dd>

Like `str.rpartition`, but `pattern` is matched as a regular expression.

`text` can be a `str` or `bytes` object.

`pattern` can be a `str`, `bytes`, or `re.Pattern` object.

`text` and `pattern` (or `pattern.pattern`) must be the same type.

If `pattern` is found in `text`, returns a tuple

```Python
(before, match, after)
```

where `before` is the text before the matched text,
`match` is the re.Match object resulting from the match, and
`after` is the text after the matched text.

If `pattern` appears in `text` multiple times,
`re_partition` will match against the last (rightmost)
appearance.

If `pattern` is not found in `text`, returns a tuple

```Python
('', None, text)
```

where the empty string is `str` or `bytes` as appropriate.

Passing in an explicit `count` lets you control how many times
`re_rpartition` partitions the string.  `re_rpartition` will always
return a tuple containing `(2*count)+1` elements, and
odd-numbered elements will be either `re.Match` objects or `None`.
Passing in a `count` of 0 will always return a tuple containing `s`.

If `pattern` is a string, `flags` is passed in
as the `flags` argument to `re.compile`.

(In older versions of Python, `re.Pattern` was a private type called
`re._pattern_type`.)
</dd></dl>

#### `reversed_re_finditer(pattern, string, flags=0)`

<dl><dd>

An iterator.  Behaves almost identically to the Python
standard library function `re.finditer`, yielding
non-overlapping matches of `pattern` in `string`.  The difference
is, `reversed_re_finditer` searches `string` from right to left.

`pattern` can be `str`, `bytes`, or a precompiled `re.Pattern` object.
If it's `str` or `bytes`, it'll be compiled
with `re.compile` using the `flags` you passed in.

`string` should be the same type as `pattern` (or `pattern.pattern`).
</dd></dl>

#### `split_quoted_strings(s, quotes=('"', "'"), *, triple_quotes=True, backslash='\\')`

<dl><dd>

Splits `s` into quoted and unquoted segments.

`s` can be either `str` or `bytes`.

`quotes` is an iterable of quote separators, either `str` or `bytes`
matching `s`.  Note that `split_quoted_strings`
only supports quote *characters,* as in, each quote separator must be exactly
one character long.

Returns an iterator yielding 2-tuples:

```
(is_quoted, segment)
```

where `segment` is a substring of `s`, and `is_quoted` is true if the segment is
quoted.  Joining all the segments together recreates `s`.

If `triple_quotes` is true, supports "triple-quoted" strings like Python.

If `backslash` is a character, this character will quoting characters inside
a quoted string, like the backslash character inside strings in Python.
</dd></dl>

#### `split_text_with_code(s, *, tab_width=8, allow_code=True, code_indent=4, convert_tabs_to_spaces=True)`

<dl><dd>

Splits `s` into individual words,
suitable for feeding into
[`wrap_words`](#wrap_wordswords-margin79--two_spacestrue).

`s` may be either `str` or `bytes`.

Paragraphs indented by less than `code_indent` will be
broken up into individual words.

If `allow_code` is true, paragraphs indented by at least
`code_indent` spaces will preserve their whitespace:
internal whitespace is preserved, and the newline is
preserved.  (This will preserve the formatting of code
examples when these words are rejoined into lines by
[`wrap_words`](#wrap_wordswords-margin79--two_spacestrue).)

For more information, see the deep-dive on
[**Word wrapping and formatting.**](#word-wrapping-and-formatting)
</dd></dl>

#### `whitespace`

<dl><dd>

A list of all whitespace characters recognized by Python.
Includes many Unicode whitespace strings, like `'\xa0'`
(a non-breaking space).  Useful as a list of separator
strings for the **big** "multi-" family of functions,
e.g. 
[`multisplit`.](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)

**big** also defines `utf8_whitespace`, which is `whitespace`
with all strings encoded to UTF-8 (as bytes),
and `ascii_whitespace`, with all strings converted into
bytes and all characters with code points greater than
128 discarded.

Note that `whitespace` contains `'\r\n'`, the DOS sequence
of characters representing a newline.  This lets **big**
text-processing functions recognize this sequence as a
*single* whitespace marker, rather than as two *separate*
whitespace characters.  If you don't want this behavior,
you can use `whitespace_without_dos` instead;
**big** also provides `utf8_whitespace_without_dos` and
`ascii_whitespace_without_dos`.
</dd></dl>

#### `wrap_words(words, margin=79, *, two_spaces=True)`

<dl><dd>

Combines `words` into lines and returns the result as a string.
Similar to `textwrap.wrap`.

`words` should be an iterator yielding str or bytes strings,
and these strings should already be split at word boundaries.
Here's an example of a valid argument for `words`:

```Python
"this is an example of text split at word boundaries".split()
```

A single `'\n'` indicates a line break.
If you want a paragraph break, embed two `'\n'` characters in a row.

`margin` specifies the maximum length of each line. The length of
every line will be less than or equal to `margin`, unless the length
of an individual element inside `words` is greater than `margin`.

If `two_spaces` is true, elements from `words` that end in
sentence-ending punctuation (`'.'`, `'?'`, and `'!'`)
will be followed by two spaces, not one.

Elements in `words` are not modified; any leading or trailing
whitespace will be preserved.  You can use this to preserve
whitespace where necessary, like in code examples.

For more information, see the deep-dive on
[**Word wrapping and formatting.**](#word-wrapping-and-formatting)
</dd></dl>


## `big.time`

Functions for working with time.  Currently deals specifically
with timestamps.  The time functions in **big** are designed
to make it easy to use best practices.

#### `date_ensure_timezone(d, timezone)`

<dl><dd>

Ensures that a `datetime.date` object has a timezone set.

If `d` has a timezone set, returns `d`.
Otherwise, returns a new `datetime.date`
object equivalent to `d` with its `tzinfo` set
to `timezone`.
</dd></dl>

#### `date_set_timezone(d, timezone)`

<dl><dd>

Returns a new `datetime.date` object identical
to `d` but with its `tzinfo` set to `timezone`.
</dd></dl>

#### `datetime_ensure_timezone(d, timezone)`

<dl><dd>

Ensures that a `datetime.datetime` object has
a timezone set.

If `d` has a timezone set, returns `d`.
Otherwise, creates a new `datetime.datetime`
object equivalent to `d` with its `tzinfo` set
to `timezone`.
</dd></dl>

#### `datetime_set_timezone(d, timezone)`

<dl><dd>

Returns a new `datetime.datetime` object identical
to `d` but with its `tzinfo` set to `timezone`.
</dd></dl>

#### `parse_timestamp_3339Z(s, *, timezone=None)`

<dl><dd>

Parses a timestamp string returned by `timestamp_3339Z`.
Returns a `datetime.datetime` object.

`timezone` is an optional default timezone, and should
be a `datetime.tzinfo` object (or `None`).  If provided,
and the time represented in the string doesn't specify
a timezone, the `tzinfo` attribute of the returned object
will be explicitly set to `timezone`.

`parse_timestamp_3339Z` depends on the
[`python-dateutil`](https://github.com/dateutil/dateutil)
package.  If `python-dateutil` is unavailable,
`parse_timestamp_3339Z` will also be unavailable.
</dd></dl>

#### `timestamp_3339Z(t=None, want_microseconds=None)`

<dl><dd>

Return a timestamp string in RFC 3339 format, in the UTC
time zone.  This format is intended for computer-parsable
timestamps; for human-readable timestamps, use `timestamp_human()`.

Example timestamp: `'2021-05-25T06:46:35.425327Z'`

`t` may be one of several types:

* If `t` is None, `timestamp_3339Z` uses the current time in UTC.
* If `t` is an int or a float, it's interpreted as seconds
  since the epoch in the UTC time zone.
* If `t` is a `time.struct_time` object or `datetime.datetime`
  object, and it's not in UTC, it's converted to UTC.
  (Technically, `time.struct_time` objects are converted to GMT,
  using `time.gmtime`.  Sorry, pedants!)

If `want_microseconds` is true, the timestamp ends with
microseconds, represented as a period and six digits between
the seconds and the `'Z'`.  If `want_microseconds`
is `false`, the timestamp will not include this text.
If `want_microseconds` is `None` (the default), the timestamp
ends with microseconds if the type of `t` can represent
fractional seconds: a float, a `datetime` object, or the
value `None`.
</dd></dl>

#### `timestamp_human(t=None, want_microseconds=None)`

<dl><dd>

Return a timestamp string formatted in a pleasing way
using the currently-set local timezone.  This format
is intended for human readability; for computer-parsable
time, use `timestamp_3339Z()`.

Example timestamp: `"2021/05/24 23:42:49.099437"`

`t` can be one of several types:

* If `t` is `None`, `timestamp_human` uses the current local time.
* If `t` is an int or float, it's interpreted as seconds since the epoch.
* If `t` is a `time.struct_time` or `datetime.datetime` object,
  it's converted to the local timezone.

If `want_microseconds` is true, the timestamp will end with
the microseconds, represented as ".######".  If `want_microseconds`
is false, the timestamp will not include the microseconds.

If `want_microseconds` is `None` (the default), the timestamp
ends with microseconds if the type of `t` can represent
fractional seconds: a float, a `datetime` object, or the
value `None`.
</dd></dl>


# Topic deep-dives

## The `multi-` family of string functions

<dl><dd>

This family of string functions was inspired by Python's `str.strip`,
`str.rstrip`, and `str.splitlines` functions.  These functions
are well-designed, and often do what you want.  But they're
surprisingly opinionated.  And... what if your use case doesn't
fit exactly into their narrow functionality?  `str.strip`
supports two specific modes of operation; if you want
to split your string in a slightly different way, you
probably can't use `str.strip`.

So what *can* you use?  There's `re.strip`, but that can be
hard to use.<sup id=back_to_re_strip><a href=#re_strip_footnote>1</a></sup>
Now there's a new answer:
[`multisplit`.](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)

[`multisplit`'s](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
goal is to be the be-all end-all string splitting function.
It's designed to replace every mode of operation for
`str.split`, `str.rstrip`, and `str.splitlines`, and it
can even replace `str.partition` and `str.rpartition`.
(**big** uses
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
to implement
[`multipartition`.)](#multipartitions-separators-count1--reverseFalse-separateTrue)

To use
[`multisplit`,](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
pass in the string you want to split, the separators you
want to split on, and tweak its behavior with its five
keyword arguments.  It returns an iterator that yields
string segments from the original string in your preferred
format.

The cornerstone of [`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
is the `separators` argument.
This is an iterable of strings, of the same type (`str` or `bytes`)
as the string you want to split (`s`).  `multisplit` will split
the string at *each* non-overlapping instance of any string
specified in `separators`.

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
  split the string, exactly like the `maxsplit` argument to `str.strip`.
* `reverse` lets you apply `maxsplit` to the end of the string
  and splitting backwards, exactly like `str.rstrip`.

To make it slightly easier to remember, all these keyword-only
parameters default to a false value.  (Well, technically,
`maxsplit` defaults to the special value `-1`, for compatibility
with `str.split`.  But this is its special "don't do anything"
magic value.  All the *other* keyword-only parameters default
to `False`.)

[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
also inspired [`multistrip`](#multistrips-separators-leftTrue-rightTrue)
 and [`multipartition`,](#multipartitions-separators-count1--reverseFalse-separateTrue)
which also take this same `separators` arguments.  There are also
other **big** functions that take a `separators` argument; for
consistency's sakes, the parameter name always has the word
`separators` in it.
(For example, `comment_separators` for `lines_filter_comment_lines`.)

The downside of [`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
is that, since it *is* so
sophisticated and tunable, it can be hard to use.  It takes
*five keyword-only parameters* after all.  However, they're
designed to be reasonably memorable, and their default values
are designed to be easy to remember.  But the best
way to combat the complexity of calling
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
is to use it as a building block for your own
text splitting functions.  For example, inside **big**,
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
is used to implement
[`multipartition`,](#multipartitions-separators-count1--reverseFalse-separateTrue)
[`normalize_whitespace`,](#normalize_whitespaces-separatorsNone-replacementnone)
[`lines`,](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs)
and several others.

### Demonstrations of each `multisplit` keyword-only parameter

To give you a sense of how the five keyword-only parameters changes the behavior of
[`multisplit`,](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
here's a breakdown of each of these parameters with examples.

#### `maxsplit`

`maxsplit` specifies the maximum number of times the string should be split.
It behaves the same as the `maxsplit` parameter to `str.split`.

The default value of `-1` means "split as many times as you can".  In our
example here, the string can be split a maximum of three times.  Therefore,
specifying a `maxsplit` of `-1` is equivalent to specifying a `maxsplit` of
`2` or greater:

```Python
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'))) # "maxsplit" defaults to -1
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), maxsplit=0))
    ['appleXbananaYcookie']
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), maxsplit=1))
    ['apple', 'bananaYcookie']
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), maxsplit=2))
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), maxsplit=3))
    ['apple', 'banana', 'cookie']
```

`maxsplit` has interactions with `reverse` and `strip`.  For more
information, see the documentation regarding those parameters, below.

#### `keep`

`keep` indicates whether or not `multisplit` should preserve the separator
strings in the strings it yields.  It supports four values: false, true,
and the special values `ALTERNATING` and `AS_PAIRS`.

```Python
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'))) # "keep" defaults to False
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), keep=False))
    ['apple', 'banana', 'cookie']
```

When `keep` is true, `multisplit` keeps the separators, appending them to
the end of the separated string:

```Python
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), keep=True))
    ['appleX', 'bananaY', 'cookie']
```

When `keep` is `ALTERNATING`, `multisplit` keeps the separators as separate
strings.  The first string yielded is always a non-separator string, and
from then on it always alternates between a separator string and a non-separator
string.  Put another way, if you store the output of `multisplit` in a list,
entries with an even-numbered index (0, 2, 4, ...) are always non-separator strings,
and entries with an odd-numbered index (1, 3, 5, ...) are always separator strings.

```Python
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), keep=big.ALTERNATING))
    ['apple', 'X', 'banana', 'Y', 'cookie']
```

Note that `ALTERNATING` always emits an odd number of strings; the first and last
strings are always non-separator strings.  Like `str.split`, if the string you're
splitting starts or ends with a separator string, `multisplit` will emit an empty
string there:

```Python
    >>> list(big.multisplit('1a1z1', ('1',), keep=big.ALTERNATING))
    ['', '1', 'a', '1', 'z', '1', '']
```

Finally, when `keep` is `AS_PAIRS`,  `multisplit` keeps the separators as separate
strings.  But instead of yielding strings, it yields 2-tuples of strings.  Every
2-tuple contains a non-separator string followed by a separator string.

If the original string starts with a separator, the first 2-tuple will contain
an empty non-separator string and the separator:

```Python
    >>> list(big.multisplit('YappleXbananaYcookie', ('X', 'Y'), keep=big.AS_PAIRS))
    [('', 'Y'), ('apple', 'X'), ('banana', 'Y'), ('cookie', '')]
```

The last 2-tuple will *always* contain an empty separator string:

```Python
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), keep=big.AS_PAIRS))
    [('apple', 'X'), ('banana', 'Y'), ('cookie', '')]
    >>> list(big.multisplit('appleXbananaYcookieXXX', ('X', 'Y'), keep=big.AS_PAIRS, strip=True))
    [('apple', 'X'), ('banana', 'Y'), ('cookie', '')]
```

(This rule means that `AS_PAIRS` always emits an *even* number of strings.
Contrast that with `ALTERNATING`, which always emits an *odd* number of strings,
and the last string it emits is always a non-separator string.  Put another
way: if you ignore the tuples, the list of strings emitted by `AS_PAIRS` is the
same as those emitted by `ALTERNATING`, except `AS_PAIRS` appends an empty
string.)

Because of this rule, if the original string ends with a separator,
and `multisplit` doesn't `strip` the right side, the final tuple
emitted by `AS_PAIRS` will be a 2-tuple containing two empty strings:

```Python
    >>> list(big.multisplit('appleXbananaYcookieX', ('X', 'Y'), keep=big.AS_PAIRS))
    [('apple', 'X'), ('banana', 'Y'), ('cookie', 'X'), ('', '')]
```

This looks strange and unnecessary.  But it *is* what you want.
This odd-looking behavior is discussed at length in the section below, titled
[Why do you sometimes get empty strings when you split?](#why-do-you-sometimes-get-empty-strings-when-you-split)

The behavior of `keep` can be affected by the value of `separate`.
For more information, see the next section, on `separate`.


#### `separate`

`separate` indicates whether multisplit should consider adjacent
separator strings in `s` as one separator or as multiple separators
each separated by a zero-length string.  It can be either false or
true.

```Python
    >>> list(big.multisplit('appleXYbananaYXYcookie', ('X', 'Y'))) # separate defaults to False
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('appleXYbananaYXYcookie', ('X', 'Y'), separate=False))
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('appleXYbananaYXYcookie', ('X', 'Y'), separate=True))
    ['apple', '', 'banana', '', '', 'cookie']
```

If `separate` and `keep` are both true values, and your string
has multiple adjacent separators, `multisplit` will view `s`
as having zero-length non-separator strings between the
adjacent separators:

```Python
    >>> list(big.multisplit('appleXYbananaYXYcookie', ('X', 'Y'), separate=True, keep=True))
    ['appleX', 'Y', 'bananaY', 'X', 'Y', 'cookie']

    >>> list(big.multisplit('appleXYbananaYXYcookie', ('X', 'Y'), separate=True, keep=big.AS_PAIRS))
    [('apple', 'X'), ('', 'Y'), ('banana', 'Y'), ('', 'X'), ('', 'Y'), ('cookie', '')]
```

#### `strip`

`strip` indicates whether multisplit should strip separators from
the beginning and/or end of `s`.  It supports five values:
false, true, `big.LEFT`, `big.RIGHT`, and `big.PROGRESSIVE`.

By default, `strip` is false, which means it doesn't strip any
leading or trailing separators:

```Python
    >>> list(big.multisplit('XYappleXbananaYcookieYXY', ('X', 'Y'))) # strip defaults to False
    ['', 'apple', 'banana', 'cookie', '']
```

Setting `strip` to true strips both leading and trailing separators:

```Python
    >>> list(big.multisplit('XYappleXbananaYcookieYXY', ('X', 'Y'), strip=True))
    ['apple', 'banana', 'cookie']
```

`big.LEFT` and `big.RIGHT` tell `multistrip` to only strip on that
side of the string:

```Python
    >>> list(big.multisplit('XYappleXbananaYcookieYXY', ('X', 'Y'), strip=big.LEFT))
    ['apple', 'banana', 'cookie', '']
    >>> list(big.multisplit('XYappleXbananaYcookieYXY', ('X', 'Y'), strip=big.RIGHT))
    ['', 'apple', 'banana', 'cookie']
```

`big.PROGRESSIVE` duplicates a specific behavior of `str.split` when using
`maxsplit`.  It always strips on the left, but it only strips on the right
if the string is completely split.  If `maxsplit` is reached before the entire
string is split, and `strip` is `big.PROGRESSIVE`, `multisplit` *won't* strip
the right side of the string.  Note in this example how the trailing separator
`Y` isn't stripped from the input string when `maxsplit` is less than `3`.

```Python
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
```

#### `reverse`

`reverse` specifies where `multisplit` starts parsing the string--from
the beginning, or the end--and in what direction it moves when parsing
the string--towards the end, or towards the beginning.  It only supports
two values: when it's false, `multisplit` starts at the beginning of the
string, and parses moving to the right (towards the end of the string).
But when `reverse` is true, `multisplit` starts at the *end* of the
string, and parses moving to the *left* (towards the *beginning*
of the string).

This has two noticable effects on `multisplit`'s output.  First, this
changes which splits are kept when `maxsplit` is less than the total number
of splits in the string.  When `reverse` is true, the splits are counted
starting on the right and moving towards the left:

```Python
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), reverse=True)) # maxsplit defaults to -1
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), maxsplit=0, reverse=True))
    ['appleXbananaYcookie']
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), maxsplit=1, reverse=True))
    ['appleXbanana', 'cookie']
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), maxsplit=2, reverse=True))
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('appleXbananaYcookie', ('X', 'Y'), maxsplit=3, reverse=True))
    ['apple', 'banana', 'cookie']
```

The second effect is far more subtle.  It's only relevant when splitting strings
containing multiple *overlapping* separators.  When `reverse` is false, and there
are two (or more) overlapping separators, the string is split by the *leftmost*
overlapping separator.  When `reverse` is true, and there are two (or more)
overlapping separators, the string is split by the *rightmost* overlapping
separator.

Consider these two calls to `multisplit`.  The only difference between them is
the value of `reverse`.  They produce different results, even though neither
one uses `maxsplit`.

```Python
    >>> list(big.multisplit('appleXAYbananaXAYcookie', ('XA', 'AY'))) # reverse defaults to False
    ['apple', 'Ybanana', 'Ycookie']
    >>> list(big.multisplit('appleXAYbananaXAYcookie', ('XA', 'AY'), reverse=True))
    ['appleX', 'bananaX', 'cookie']
```

### Reimplementing library functions using `multisplit`

Here are some examples of how you could use
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
to replace some common Python string splitting methods.  These exactly duplicate the
behavior of the originals.

```Python
def _multisplit_to_split(s, sep, maxsplit, reverse):
    separate = sep != None
    if separate:
        strip = False
    else:
        sep = big.ascii_whitespace if isinstance(s, bytes) else big.whitespace
        strip = big.PROGRESSIVE
    result = list(big.multisplit(s, sep,
        maxsplit=maxsplit, reverse=reverse,
        separate=separate, strip=strip))
    if not separate:
        # ''.split() == '   '.split() == []
        if result and (not result[-1]):
            result.pop()
    return result

def str_split(s, sep=None, maxsplit=-1):
    return _multisplit_to_split(s, sep, maxsplit, False)

def str_rsplit(s, sep=None, maxsplit=-1):
    return _multisplit_to_split(s, sep, maxsplit, True)

def str_splitlines(s, keepends=False):
    newlines = big.ascii_newlines if isinstance(s, bytes) else big.newlines
    l = list(big.multisplit(s, newlines,
        keep=keepends, separate=True, strip=False))
    if l and not l[-1]:
    	# yes, ''.splitlines() returns an empty list
        l.pop()
    return l

def _partition_to_multisplit(s, sep, reverse):
    if not sep:
        raise ValueError("empty separator")
    l = tuple(big.multisplit(s, (sep,),
        keep=big.ALTERNATING, maxsplit=1, reverse=reverse, separate=True))
    if len(l) == 1:
        empty = b'' if isinstance(s, bytes) else ''
        if reverse:
            l = (empty, empty) + l
        else:
            l = l + (empty, empty)
    return l

def str_partition(s, sep):
    return _partition_to_multisplit(s, sep, False)

def str_rpartition(s, sep):
    return _partition_to_multisplit(s, sep, True)
```

You wouldn't want to use these, of course--Python's built-in
functions are so much faster!

### Why do you sometimes get empty strings when you split?

Sometimes when you split using
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse),
you'll get empty strings in the return value.  This might be unexpected,
violating the [Principle Of Least Astonishment.](https://en.wikipedia.org/wiki/Principle_of_least_astonishment)
But there are excellent reasons for this behavior.

Let's start by observing what `str.split` does. `str.split` really has two
major modes of operation: when you don't pass in a separator (or pass in `None` for the
separator), and when you pass in an explicit separator string.  In this latter mode,
the documentation says it regards every instance of a separator string as an individual
separator splitting the string.  What does that mean?  Watch what happens when you have
two adjacent separators in the string you're splitting:

```Python
    >>> '1,2,,3'.split(',')
    ['1', '2', '', '3']
```

What's that empty string doing between `'2'` and `'3'`?  Here's how you should think about it:
when you pass in an explicit separator, `str.split` splits at *every* occurance of that
separator in the string.  It *always* splits the string into two places, whenever there's
a separator.  And when there are two adjacent separators, conceptually, they have a
zero-length string in between them:

```Python
    >>> '1,2,,3'[4:4]
    ''
```

The empty string in the output of `str.split` represents the fact that there
were two adjacent separators.  If `str.split` didn't add that empty string,
the output would look like this:

```Python
    ['1', '2', '3']
```

But then it'd be indistinguishable from splitting the same string *without*
two separators in a row:

```Python
    >>> '1,2,3'.split(',')
    ['1', '2', '3']
```

This difference is crucial when you want to reconstruct the original string from
the split list.  `str.split` with a separator should always be reversable using
`str.join`, and with that empty string there it works correctly:

```Python
    >>> ','.join(['1', '2', '3'])
    '1,2,3'
    >>> ','.join(['1', '2', '', '3'])
    '1,2,,3'
```

Now take a look at what happens when the string
you're splitting starts or ends with a separator:

```Python
    >>> ',1,2,3,'.split(',')
    ['', '1', '2', '3', '']
```

This might seem weird.  But, just like with two adjacent separators,
this behavior is important for consistency.  Conceptually there's
a zero-length string between the beginning of the string and the first
comma.  And `str.join` needs those empty strings in order to correctly
recreate the original string.

```Python
    >>> ','.join(['', '1', '2', '3', ''])
    ',1,2,3,'
```

Naturally,
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
lets you duplicate this behavior.  When you want
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
to behave just like `str.split` does with an explicit separator
string, just pass in `keep=False`, `separate=True`, and `strip=False`.
That is, if `a` and `b` are strings,

```Python
     big.multisplit(a, (b,), keep=False, separate=True, strip=False)
```

always produces the same output as

```Python
     a.split(b)
```

For example, here's
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
splitting the strings we've been playing with, using these parameters:

```Python
    >>> list(big.multisplit('1,2,,3', (',',), keep=False, separate=True, strip=False))
    ['1', '2', '', '3']
    >>> list(big.multisplit(',1,2,3,', (',',), keep=False, separate=True, strip=False))
    ['', '1', '2', '3', '']
```

This "emit an empty string" behavior also has ramifications when `keep` isn't false.
The behavior of `keep=True` is easy to predict; `multisplit` just appends the separators
to the previous string segment:

```Python
    >>> list(big.multisplit('1,2,,3', (',',), keep=True, separate=True, strip=False))
    ['1,', '2,', ',', '3']
    >>> list(big.multisplit(',1,2,3,', (',',), keep=True, separate=True, strip=False))
    [',', '1,', '2,', '3,', '']
```

The principle here is that, when you use `keep=True`, you should be able to reconstitute
the original string with `''.join`:

```Python
    >>> ''.join(['1,', '2,', ',', '3'])
    '1,2,,3'
    >>> ''.join([',', '1,', '2,', '3,', ''])
    ',1,2,3,'
```

`keep=big.ALTERNATING` is much the same, except we insert the separators as their
own segments, rather than appending each one to the previous segment:

```Python
    >>> list(big.multisplit('1,2,,3', (',',), keep=big.ALTERNATING, separate=True, strip=False))
    ['1', ',', '2', ',', '', ',', '3']
    >>> list(big.multisplit(',1,2,3,', (',',), keep=big.ALTERNATING, separate=True, strip=False))
    ['', ',', '1', ',', '2', ',', '3', ',', '']
```

Remember, `ALTERNATING` output always begins and ends with a non-separator string.
If the string you're splitting begins or ends with a separator, the output
from `multisplit` specifying `keep=ALTERNATING` will correspondingly begin or end
with an empty string.

And, as with `keep=True`, you can also recreate the original string by passing
these arrays in to `''.join`:

```Python
    >>> ''.join(['1', ',', '2', ',', '', ',', '3'])
    '1,2,,3'
    >>> ''.join(['', ',', '1', ',', '2', ',', '3', ',', ''])
    ',1,2,3,'
```

Finally there's `keep=big.AS_PAIRS`.  The behavior here seemed so strange,
initially I thought it was wrong.  But I've given it a *lot* of thought, and
I've convinced myself that this is correct:

```Python
    >>> list(big.multisplit('1,2,,3', (',',), keep=big.AS_PAIRS, separate=True, strip=False))
    [('1', ','), ('2', ','), ('', ','), ('3', '')]
    >>> list(big.multisplit(',1,2,3,', (',',), keep=big.AS_PAIRS, separate=True, strip=False))
    [('', ','), ('1', ','), ('2', ','), ('3', ','), ('', '')]
```

That tuple at the end, just containing two empty strings:

```Python
    ('', '')
```

It's *so strange.*  How can that be right?

It's the same as `str.split`.
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
*must* split the string into two pieces *every* time it finds the separator
in the original string.  So it *must* emit the empty non-separator string.
And since that zero-length string isn't (cannot!) be followed by a separator,
when using `keep=AS_PAIRS` the final separator string is *also* empty.

Think of it this way: with the tuple of empty strings there, you can easily
convert one `keep` format into any another.  (Provided that you know
what the separators were--either the source `keep` format was not false,
or you only used one separator string when calling `multisplit`).
Without that tuple of empty strings at the end, you'd also have to have an
`if` statement to add or remove empty stuff from the end.

I'll demonstrate this with a simple example.  Here's the output of
`multisplit` splitting the string `'1a1z1'` by the separator `'1'`,
in each of the four `keep` formats:

```Python
>>> list(big.multisplit('1a1z1', '1', keep=False))
['', 'a', 'z', '']
>>> list(big.multisplit('1a1z1', '1', keep=True))
['1', 'a1', 'z1', '']
>>> list(big.multisplit('1a1z1', '1', keep=big.ALTERNATING))
['', '1', 'a', '1', 'z', '1', '']
>>> list(big.multisplit('1a1z1', '1', keep=big.AS_PAIRS))
[('', '1'), ('a', '1'), ('z', '1'), ('', '')]
```

Because the `AS_PAIRS` output ends with that tuple of empty
strings, we can mechanically convert it into any of the other
formats, like so:

```Python
>>> result = list(big.multisplit('1a1z1', '1', keep=big.AS_PAIRS))
>>> result
[('', '1'), ('a', '1'), ('z', '1'), ('', '')]
>>> [s[0] for s in result] # convert to keep=False
['', 'a', 'z', '']
>>> [s[0]+s[1] for s in result] # convert to keep=True
['1', 'a1', 'z1', '']
>>> [s for t in result for s in t][:-1] # convert to keep=big.ALTERNATING
['', '1', 'a', '1', 'z', '1', '']
```

If the `AS_PAIRS` output *didn't* end with that tuple of empty strings,
you'd need to add an `if` statement to restore the trailing empty
strings as needed.

### Other differences between multisplit and str.split

`str.split` returns an *empty list* when you split an
empty string by whitespace:

```Python
>>> ''.split()
[]
```

But not when you split by an explicit separator:

```Python
>>> ''.split('x')
['']
```

[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
is consistent here.  If you split an empty string, it always returns an empty string,
as long as the separators are valid:

```Python
>>> list(big.multisplit(''))
['']
>>> list(big.multisplit('', ('a', 'b', 'c')))
['']
```

Similarly, when splitting a string that only contains whitespace, `str.split` also
returns an empty list:

```Python
>>> '     '.split()
[]
```

This is really the same as "splitting an empty string", because when `str.split`
splits on whitespace, the first thing it does is strip leading whitespace.

If you [`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
a string that only contains whitespace, and you split on whitespace characters,
it returns two empty strings:

```Python
>>> list(big.multisplit('     '))
['', '']
```

This is because the string conceptually starts with a zero-length string,
then has a run of whitespace characters, then ends with another zero-length
string.  So those two empty strings are the leading and trailing zero-length
strings, separated by whitespace.  If you tell
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
to also strip the string, you'll get back a single empty string:

```Python
>>> list(big.multisplit('     ', strip=True))
['']
```

And
[`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
behaves consistently even when you use different separators:

```Python
>>> list(big.multisplit('ababa', 'ab'))
['', '']
>>> list(big.multisplit('ababa', 'ab', strip=True))
['']
```

----------

<ol><li id="re_strip_footnote"><p>

And I should know--`multisplit` is implemented using `re.split`!

</p></li></ol>

</dd></dl>

## `lines` and lines modifier functions

<dl><dd>

[`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs) creates an iterator that yields individual lines
split from a string.  It's designed to make it easy to write
simple, well-behaved text parsers.

For example, every yielded line is accompanied by a `LinesInfo`
object, which provides the line number and starting column number
for each line.  This makes it easy for your parser to provide
line and column information for error messages.

The output of [`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs) can be modified by "lines modifier"
functions.  These are functions that iterate over a lines
iterator and re-yield the values, possibly modifying or
discarding them along the way.  For example, passing
a [`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs) iterator into `lines_filter_empty_lines` results
in an iterator that skips over the empty lines.
All the lines modifier functions that ship with **big**
start with the string `lines_`.

Actually there are additional constraints on lines modifier
function names.  The second word in the function name,
immediately after `lines_`, may denote the lines modifier's
category.  Some examples:

* `lines_filter_` functions may remove
  lines from the output.  For example, `lines_filter_empty_lines`
  will only yield a line if it isn't empty.
* `lines_strip_` functions may remove one or
  more substrings from the line.  For example,
  [`lines_strip_indent(li)`](#lines_strip_indentli)
  strips the leading whitespace from a line before yielding
  it.  (Whenever a lines modifier removes leading text from a line,
  it will add a `leading` field to the accompanying `LineInfo` object
  containing the removed substring, and will also update the
  `column_number` of the line to reflect the new starting column.)
* `lines_convert_` functions means this lines modifier may change one
  or more substrings in the line.  For example,
  `lines_convert_tabs_to_spaces` changes tab characters
  to space characters in any lines it processes.

(**big** isn't strict about these category names though.
For example,
[`lines_containing(li, s, *, invert=False)`](#lines_containingli-s--invertfalse)
and
[`lines_grep(li, pattern, *, invert=False, flags=0)`](#lines_grepli-pattern--invertfalse-flags0)
are obviously "filter" modifiers, but their names
don't start with `lines_filter_`.)

All lines modifier functions are composable with each
other; you can "stack" them together simply by passing
the output of one into the input of another.  For example,

```Python
     with open("textfile.txt", "rt") as f:
         for info, line in big.lines_filter_empty_lines(
     	     big.lines_rstrip(lines(f.read()))):
     	     ...
```

will iterate over the lines of `textfile.txt`, skipping
over all empty lines and lines that consist only of
whitespace.

When you stack line modifiers in this way, note that the
*outer* modifiers happen *later*.  In the above example,
each line is first "r-stripped", and then discarded
if it's empty.  If you stacked the line modifiers in
the opposite order:

```Python
     with open("textfile.txt", "rt") as f:
         for info, line in big.lines_rstrip(
     	     big.lines_filter_empty_lines(lines(f.read()))):
     	     ...
```

then it'd filter out empty lines first, and *then*
"r-strip" the lines.  So lines in the input that contained
only whitespace would still get yielded as empty lines,
which is probably not what you want.

Of course, you can write your own lines modifier functions!
Simply accept a lines iterator as an argument, iterate over
it, and yield each line info and line, modifying them
(or not yielding them!) as you see fit.  You can potentially
even write your own lines iterator, a replacement for
[`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs),
if you need functionality
[`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs) doesn't provide.

Note that if you write your own lines modifier function,
and it removes text from the beginning the line, you'll have to
update the `LineInfo` object manually--it doesn't happen
automatically.

</dd></dl>

## Word wrapping and formatting

<dl><dd>

**big** contains three functions used to reflow and format text
in a pleasing manner.  In the order you should use them, they are
[`split_text_with_code`](#split_text_with_codes--tab_width8-allow_codetrue-code_indent4-convert_tabs_to_spacestrue),
[`wrap_words(),`](#wrap_wordswords-margin79--two_spacestrue),
and optionally
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_responseoverflowresponseraise-overflow_before0-overflow_after0).
This trio of functions gives you the following word-wrap superpowers:

* Paragraphs of text representing embedded "code" don't get word-wrapped.
  Instead, their formatting is preserved.
* Multiple texts can be merged together into multiple columns.

### "text" vs "code"

The **big** word wrapping functions also distinguish between
"text" and "code".  The main distinction is, "text" lines can
get word-wrapped, but "code" lines shouldn't.  **big** considers
any line starting with enough whitespace to be a "code" line;
by default, this is four spaces.  Any non-blank line that
starting with four spaces is a "code" line, and any non-blank
line that starts with less than four spaces is a "text" line.

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

#### Split text array

A *split text array* is an intermediary data structure
used by **big.text** functions to represent text.
It's literally just an array of strings, where the strings
represent individual word-wrappable substrings.

[`split_text_with_code`](#split_text_with_codes--tab_width8-allow_codetrue-code_indent4-convert_tabs_to_spacestrue)
returns a *split text array,* and
[`wrap_words()`](#wrap_wordswords-margin79--two_spacestrue)
consumes a *split text array.*

You'll see four kinds of strings in a *split text array:*

* Individual words, ready to be word-wrapped.
* Entire lines of "code", preserving their formatting.
* Line breaks, represented by a single newline: `'\n'`.
* Paragraph breaks, represented by two newlines: `'\n\n'`.

#### Examples

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

If you then passed this string in to
[`split_text_with_code`,](#split_text_with_codes--tab_width8-allow_codetrue-code_indent4-convert_tabs_to_spacestrue)
it'd return this *split text array:*
```Python
[ 'hello', 'there!', 'this', 'is', 'text.', '\n\n',
  'this', 'is', 'a', 'second', 'paragraph!']
```

[`split_text_with_code`](#split_text_with_codes--tab_width8-allow_codetrue-code_indent4-convert_tabs_to_spacestrue)
merged the first two lines together into
a single paragraph, and collapsed the three newlines separating
the two paragraphs into a "paragraph break" marker
(two newlines in one string).


Now let's add an example of text with some "code".  This text:

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
and so the text is split into the following *split text array:*
```Python
['What', 'are', 'the', 'first', 'four', 'squared', 'numbers?', '\n\n',
  '    for i in range(1, 5):', '\n', '\n', '\n', '        print(i**2)', '\n\n',
  'Python', 'is', 'just', 'that', 'easy!']
```

Here we have a "text" paragraph, followed by a "code" paragraph, followed
by a second "text" paragraph.  The "code" paragraph preserves the internal
newlines, though they are represented as individual "line break" markers
(strings containing a single newline).  Every paragraph is separated by
a "paragraph marker".

Here's a simple algorithm for joining a *split text array* back into a
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
punctuation.  In practice, you shouldn't do this by hand;
you should use
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

What is "overflow"?  It's a condition
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_responseoverflowresponseraise-overflow_before0-overflow_after0)
may encounter when the text in a column is wider than that
column's `max_width`.
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_responseoverflowresponseraise-overflow_before0-overflow_after0)
needs to consider both "overflow lines",
lines that are longer than `max_width`, and "overflow columns",
columns that contain one or more overflow lines.

What does
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_responseoverflowresponseraise-overflow_before0-overflow_after0)
do when it encounters overflow?
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_responseoverflowresponseraise-overflow_before0-overflow_after0)
supports three "strategies" to deal with this condition, and you can specify
which one you want using its `overflow_strategy` parameter.  The three
strategies are:

- `OverflowStrategy.RAISE`: Raise an `OverflowError` exception.  The default.

- `OverflowStrategy.INTRUDE_ALL`: Intrude into all subsequent columns on
all lines where the overflowed column is wider than its `max_width`.
The subsequent columns "make space" for the overflow text by not adding
text on those overflowed lines; this is called "pausing" their output.

- `OverflowStrategy.DELAY_ALL`:  Delay all columns after the overflowed
column, not beginning any until after the last overflowed line
in the overflowed column.  This is like the `INTRUDE_ALL` strategy,
except that the columns "make space" by pausing their output until
the last overflowed line.

When `overflow_strategy` is `INTRUDE_ALL` or `DELAY_ALL`, and
either `overflow_before` or `overflow_after` is nonzero, these
specify the number of extra lines before or after
the overflowed lines in a column where the subsequent columns
"pause".

</dd></dl>

## Enhanced `TopologicalSorter`

<dl><dd>

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

</dd></dl>

## Bound inner classes

<dl><dd>

#### Overview

One minor complaint I have about Python regards inner classes.
An "inner class" is a class defined inside another class.  And,
well, inner classes seem kind of half-baked.  Unlike functions,
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

```
    >>> o.method
    <bound method Outer.method of <__main__.Outer object at 0x########>>
```

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
You just decorate the inner class with `@big.BoundInnerClass`,
and `BoundInnerClass` takes care of the rest!

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

Notice that `Inner.__init__` now requires an `outer` parameter,
even though you didn't pass in any arguments to `o.Inner`.
When it's called, `o` is magically passed in to `outer`!
Thanks, [`BoundInnerClass`](#boundinnerclasscls)!  You've saved the day!

Decorating an inner class like this always adds a second positional
parameter, after `self`.  And, like `self`, you don't have
to use the name `outer`, you can use any name you like.
(Although it's probably a good idea, for consistency's sakes.)

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
superclass's `__init__`. You don't need to pass in the `outer` parameter;
it'll be automatically passed in to the superclass's `__init__` as before.*

4. *An inner class that inherits from a bound inner class, and which also
wants to be bound to the outer object, should be decorated with
[`BoundInnerClass`](#boundinnerclasscls).*

5. *An inner class that inherits from a bound inner class, but doesn't
want to be bound to the outer object, should be decorated with
[`UnboundInnerClass`](#unboundinnerclasscls).*

Restating the last two rules: every class that descends from any
[`BoundInnerClass`](#boundinnerclasscls)
should be decorated with either
[`BoundInnerClass`](#boundinnerclasscls)
or
[`UnboundInnerClass`](#unboundinnerclasscls).
Which one you use depends on what behavior you want--whether or
not you want your inner subclass to automatically get the `outer`
instance passed in to its `__init__`.

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
            super().__init__()

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
            super().__init__()
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

* If you refer to a bound inner class directly from the outer *class,*
  rather than using the outer *instance,* you get the original class.
  This ensures that references to `Outer.Inner` are consistent; this
  class is also a base class of all the bound inner classes. Additionally,
  if you attempt to construct an instance of an unbound `Outer.Inner`
  class without referencing it via an instance, you must pass in the
  outer parameter by hand--just like you'd have to pass in the `self`
  parameter by hand when calling a method on the *class itself* rather
  than on an *instance* of the class.

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

</dd></dl>


## Release history

#### 0.10
<dl><dd>

*released 2023/09/04*

* Added the new [`big.state`](#bigstate) module, with its exciting
  [`StateMachine`](#statemachinestate--on_enteron_enter-on_exiton_exit-state_classnone)
  class!
* [`int_to_words`](#int_to_wordsi--flowerytrue-ordinalfalse)
  now supports the new `ordinal` keyword-only parameter, to produce
  *ordinal* strings instead of *cardinal* strings.  (The number 1
  as a *cardinal* string is `'one'`, but as an *ordinal* string is `'first'`).
* Added the [`pure_virtual`](#pure_virtual) decorator to [`big.builtin`](#bigbuiltin).
* The documentation is now much prettier!  I finally discovered a syntax
  I can use to achieve a proper indent in Markdown, supported by both
  GitHub and PyPI. You simply nest the text you want indented inside
  an HTML description list as the description text, and skip the
  description item (`<dl><dd>`).  Note that you need a blank
  line after the `<dl><dd>` line, or else Markdown will ignore the
  markup in the following paragraph.  Thanks to Hugo van Kemenade
  for his help confirming this!  Oh, and, Hugo also fixed the image markup
  so the **big** banner displays properly on PyPI.  Thanks, Hugo!
</dd></dl>

#### 0.9.2
<dl><dd>

*released 2023/07/22*

Extremely minor release.  No new features or bug fixes.

* Fixed coverage, now back to the usual 100%.
  (This just required changing the tests, which
  *didn't* find any new bugs.)
* Made the tests for [`Log`](#log-clocknone)
  deterministic.  They now use a fake clock
  that always returns the same values.
* Added GitHub Actions integration.  Tests and
  coverage are run in the cloud after every checkin.
  Thanks to [Dan Pope](https://github.com/lordmauve)
  for gently walking me through this!
* Fixed metadata in the `pyproject.toml` file.
* Added badges for testing, coverage,
  and supported Python versions.
</dd></dl>

#### 0.9.1
<dl><dd>

*released 2023/06/28*

* Added the new [`big.log`](#biglog) module, with its new
  [`Log`](#log-clocknone) class!
  I wrote this for another project--but it turned out so nice
  I just had to add it to **big**!
</dd></dl>

#### 0.9
<dl><dd>

*released 2023/06/15*

* Bugfix!  If an outer class `Outer` had an inner class `Inner`
  decorated with `@BoundInnerClass`, and `o` is an instance of
  `Outer`, and `o` evaluated to false in a boolean context,
  `o.Inner` would be the *unbound* version of `Inner`.  Now
  it's the bound version, as is proper.
* Modified `tests/test_boundinnerclasses.py`:

    - Added regression test for the above bugfix (of course!).
    - It now takes advantage of that newfangled "zero-argument `super`".
    - Added testing of an unbound subclass of an unbound subclass.
</dd></dl>

#### 0.8.3
<dl><dd>

*released 2023/06/11*

* Added
  [`int_to_words`](#int_to_wordsi--flowerytrue-ordinalfalse).
* All tests now insert the local **big** directory
  onto `sys.path`, so you can run the tests on your
  local copy without having to install.  Especially
  convenient for testing with old versions of Python!

> *Note:* tomorrow, **big** will be one year old!
</dd></dl>

#### 0.8.2
<dl><dd>

*released 2023/05/19*

* Convert all iterator functions to use my new approach:
  instead of checking arguments inside the iterator,
  the function you call checks arguments, then has a
  nested iterator function which it runs and returns the
  result.  This means bad inputs raise their exceptions
  at the call site where the iterator is constructed,
  rather than when the first value is yielded by the iterator!
</dd></dl>

#### 0.8.1
<dl><dd>

*released 2023/05/19*

* Added
  [`parse_delimiters`](#parse_delimiterss-delimitersNone)
  and
  [`Delimiter`.](#delimiteropen-close--backslashfalse-nestedtrue)
</dd></dl>

#### 0.8
<dl><dd>

*released 2023/05/18*

* Major retooling of `str` and `bytes` support in `big.text`.
  * Functions in `big.text` now uniformly accept `str` or `bytes`
    or a subclass of either.  See the
    [Support for bytes and str](#Support-for-bytes-and-str) section
    for how it works.
  * Functions in `big.text` are now more consistent about raising
    `TypeError` vs `ValueError`.  If you mix `bytes` and `str`
    objects together in one call, you'll get a `TypeError`, but
    if you pass in an empty iterable (of a correct type) where
    a non-empty iterable is required you'll get a `ValueError`.
    `big.text` generally tries to give the `TypeError` higher
    priority; if you pass in a value that fails both the type
    check and the value check, the `big.text` function will raise
    `TypeError` first.
* Major rewrite of
  [`re_rpartition`.](#re_rpartitiontext-pattern-count1--flags0)
  I realized it had the same "reverse mode" problem that
  I fixed in
  [`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
  back in version **0.6.10**: the regular expression should really
  search the string in "reverse mode", from right to left.
  The difference is whether the regular
  expression potentially matches against overlapping strings.
  When in forwards mode, the regular expression should prefer
  the *leftmost* overlapping match, but in reverse mode it
  should prefer the *rightmost* overlapping match.  Most of the
  time this produces the same list of matches as you'd
  find searching the string forwards--but sometimes the matches come
  out *very* different.
  This was way harder to fix with `re_rpartition` than with `multisplit`,
  because Python's `re` module only supports searching forwards.
  I have to emulate reverse-mode searching by manually checking for
  overlapping matches and figuring out which one(s) to keep--a *lot* of
  work!  Fortunately it's only a minor speed hit if you don't have
  overlapping matches.  (And if you *do* have overlapping matches,
  you're probably just happy `re_rpartition` now produces correct
  results--though I did my best to make it performant anyway.)
  In the future, **big** will probably add support for the
  PyPI package `regex`, which reimplements Python's `re` module
  but adds many features... including reverse mode!
* New function:
  [`reversed_re_finditer`.](#reversed_re_finditerpattern-string-flags0)
  Behaves almost identically to the Python
  standard library function `re.finditer`, yielding
  non-overlapping matches of `pattern` in `string`.  The difference
  is, `reversed_re_finditer` searches `string` from right to left.
  (Written as part of the
  [`re_rpartition`](#re_rpartitiontext-pattern-count1--flags0)
  rewrite mentioned above.)
* Added `apostrophes`, `double_quotes`,
  `ascii_apostrophes`, `ascii_double_quotes`,
  `utf8_apostrophes`, and `utf8_double_quotes`
  to the `big.text` module.  Previously the first
  four of these were hard-coded strings inside
  [`gently_title`.](#gently_titles-apostrophesnone-double_quotesnone)
  (And the last two didn't exist!)
* Code cleanup in `split_text_with_code`, removed redundant code.
  I think it has about the same number of `if` statements; if anything
  it might be slightly faster.
* Retooled
  [`re_partition`](#re_partitiontext-pattern-count1--flags0)
  and
  [`re_rpartition`](#re_rpartitiontext-pattern-count1--flags0)
  slightly, should now be very-slightly faster.  (Well, `re_rpartition`
  will be slower if your pattern finds overlapping matches.  But at
  least now it's correct!)
* Lots and lots of doc improvements, as usual.
</dd></dl>

#### 0.7.1
<dl><dd>

*released 2023/03/13*

* Tweaked the implementation of
  [`multisplit`.](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
  Internally, it does the
  string splitting using `re.split`, which returns a `list`.  It used
  to iterate over the list and yield each element.  But that meant keeping
  the entire list around in memory until `multisplit` exited.  Now,
  [`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
  reverses the list, pops off the final element, and yields
  that.  This means
  [`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
  drops all references to the split strings
  as it iterates over the string, which may help in low-memory situations.
* Minor doc fixes.
</dd></dl>

#### 0.7
<dl><dd>

*released 2023/03/11*

* Breaking changes to the
  [`Scheduler`](#schedulerregulatordefault_regulator):
  * It's no longer thread-safe by default, which means it's much faster
    for non-threaded workloads.
  * The lock has been moved out of the
    [`Scheduler`](#schedulerregulatordefault_regulator)
    object and into the
    [`Regulator`](#regulator).  Among other things, this
    means that the
    [`Scheduler`](#schedulerregulatordefault_regulator)
    constructor no longer takes a `lock` argument.
  * [`Regulator`](#regulator) is now an abstract base class.
    `big.scheduler` also provides two concrete implementations:
    [`SingleThreadedRegulator`](#singlethreadedregulator)
    and
    [`ThreadSafeRegulator`](#threadsaferegulator).
  * [`Regulator`](#regulator) and
    [`Event`](#eventscheduler-event-time-priority-sequence)
    are now defined in the `big.scheduler` namespace.  They were
    previously defined inside the `Scheduler` class.
  * The arguments to the
    [`Event`](#eventscheduler-event-time-priority-sequence)
    constructor were rearranged.  (You shouldn't care, as you
    shouldn't be manually constructing
    [`Event`](#eventscheduler-event-time-priority-sequence)
    objects anyway.)
  * The `Scheduler` now guarantees that it will only call `now` and `wake`
    on a `Regulator` object while holding that `Regulator`'s lock.
* Minor doc fixes.
</dd></dl>

#### 0.6.18
<dl><dd>

*released 2023/03/09*

* Retooled
  [`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
  and
  [`multistrip`](#multistrips-separators-leftTrue-rightTrue)
  argument verification code.  Both functions now consistently check all
  their inputs, and use consistent error messages when raising an exception.
</dd></dl>

#### 0.6.17
<dl><dd>

*released 2023/03/09*

* Fixed a minor crashing bug in
  [`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse):
  if you passed in a *list* of separators (or `separators`
  was of any non-hashable type), and `reverse` was true,
  `multisplit` would crash.  It used `separators` as a key
  into a dict, which meant `separators` had to be hashable.
* [`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse)
  now verifies that the `s` passed in is either `str` or `bytes`.
* Updated all copyright date notices to 2023.
* Lots of doc fixes.
</dd></dl>

#### 0.6.16
<dl><dd>

*released 2023/02/26*

* Fixed Python 3.6 support! Some equals-signs-in-f-strings and some
  other anachronisms had crept in.  0.6.16 has been tested on all
  versions from 3.6 to 3.11 (as well as having 100% *coverage*).
* Made the `dateutils` package an optional dependency.  Only one function
  needs it, [`parse_timestamp_3339Z()`](#parse_timestamp_3339zs--timezonenone).
* Minor cleanup in [`PushbackIterator()`](#pushbackiteratoriterablenone).
  It also uses slots now, which should make it a bit faster.
</dd></dl>

#### 0.6.15
<dl><dd>

*released 2023/01/07*

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
</dd></dl>

#### 0.6.14
<dl><dd>

*released 2022/12/11*

* Improved the text of the `RuntimeError` raised by `TopologicalSorter.View`
  when the view is incoherent.  Now it tells you exactly what nodes are
  conflicting.
* Expanded the deep dive on `multisplit`.
</dd></dl>

#### 0.6.13
<dl><dd>

*released 2022/12/11*

* Changed [`translate_filename_to_exfat(s)`](#translate_filename_to_exfats)
  behavior: when modifying a string with a colon (`':'`) *not* followed by
  a space, it used to convert it to a dash (`'-'`).  Now it converts the
  colon to a period (`'.'`), which looks a little more natural.  A colon
  followed by a space is still converted to a dash followed by a space.
</dd></dl>

#### 0.6.12
<dl><dd>

*tagged 2022/12/04*

* Bugfix: When calling
  [`TopologicalSorter.print()`](#topologicalsorterprintprintprint),
  it sorts the list of nodes, for consistency's sakes and for ease of reading.
  But if the node objects don't support `<` or `>` comparison,
  that throws an exception.  `TopologicalSorter.print()` now catches
  that exception and simply skips sorting.  (It's only a presentation thing anyway.)
* Added a secret (otherwise undocumented!) function: `multirpartition`,
  which is like
  [`multipartition`](#multipartitions-separators-count1--reverseFalse-separateTrue)
  but with `reverse=True`.
* Added the list of conflicted nodes to the "node is incoherent"
  exception text.

> *Note:* although version **0.6.12** was tagged, it was never packaged for release.
</dd></dl>

#### 0.6.11
<dl><dd>

*tagged 2022/11/13*

* Changed the import strategy.  The top-level **big** module used
  to import all its child modules, and `import *` all the symbols
  from all those modules.  But a friend (hi Mark Shannon!) talked
  me out of this.  It's convenient, but if a user doesn't care about
  a particular module, why make them import it.  So now the top-level
  **big** module contains nothing but a version number, and you
  can either import just the submodules you need, or you can import
  **big.all** to get all the symbols (like **big** itself used to do).

> *Note:* although version **0.6.11** was tagged, it was never packaged for release.
</dd></dl>

#### 0.6.10
<dl><dd>

*released 2022/10/26*

* All code changes had to do with
  [`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse):
    * Fixed a subtle bug.  When splitting with a separator that can overlap
      itself, like `' x '`, `multisplit` will prefer the *leftmost* instance.
      But when `reverse=True`, it must prefer the *rightmost* instance.
      Thanks to Eric V. Smith for suggesting the clever "reverse everything,
      call `re.split`, and un-reverse everything" approach.  That let me
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
</dd></dl>

#### 0.6.8
<dl><dd>

*released 2022/10/16*

* Renamed two of the three freshly-added lines modifier functions:
  `lines_filter_contains` is now 
  [`lines_containing`](#lines_containingli-s--invertfalse),
  and `lines_filter_grep` is now
  [`lines_grep`](#lines_grepli-pattern--invertfalse-flags0).
</dd></dl>

#### 0.6.7
<dl><dd>

*released 2022/10/16*

* Added three new lines modifier functions
  to the [`text`](#bigtext) module:
  `lines_filter_contains`,
  `lines_filter_grep`,
  and
  [`lines_sort`](#lines_sortli--reversefalse).
* [`gently_title`](#gently_titles-apostrophesnone-double_quotesnone)
  now accepts `str` or `bytes`.  Also added the `apostrophes` and
  `double_quotes` arguments.
</dd></dl>

#### 0.6.6
<dl><dd>

*released 2022/10/14*

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
</dd></dl>

#### 0.6.5
<dl><dd>

*released 2022/10/13*

* Added the new [`itertools`](#bigitertools) module, which so far only contains
  [`PushbackIterator`](#pushbackiteratoriterablenone).
* Added
  [`lines_strip_comments`](#lines_strip_commentsli-comment_separators--quotes--backslash-rstriptrue-triple_quotestrue)
  and
  [`split_quoted_strings`](#split_quoted_stringss-quotes---triple_quotestrue-backslash)
  to the
  [`text`](#bigtext)
  module.
</dd></dl>

#### 0.6.1
<dl><dd>

*released 2022/10/13*

* I realized that [`whitespace`](#whitespace) should contain the DOS end-of-line
  sequence (`'\r\n'`), as it should be considered a single separator
  when splitting etc.  I added that, along with [`whitespace_no_dos`](#whitespace),
  and naturally [`utf8_whitespace_no_dos`](#whitespace) and
  [`ascii_whitespace_no_dos`](#whitespace) too.
* Minor doc fixes.
</dd></dl>

#### 0.6
<dl><dd>

*released 2022/10/13*

A **big** upgrade!

* Completely retooled and upgraded
  [`multisplit`](#multisplits-separators--keepFalse-maxsplit-1-reverseFalse-separateFalse-stripFalse),
  and added
  [`multistrip`](#multistrips-separators-leftTrue-rightTrue)
  and
  [`multipartition`,](#multipartitions-separators-count1--reverseFalse-separateTrue)
  collectively called
  [**The `multi-` family of string functions.**](#The-multi--family-of-string-functions)
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
  These are in their own modules, [`big.heap`](#bigheap) and [`big.scheduler`](#bigscheduler).
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
</dd></dl>

#### 0.5.2
<dl><dd>

*released 2022/09/12*

* Added `stripped_lines` and `rstripped_lines` to the [`text`](#bigtext) module.
* Added support for `len` to the [`TopologicalSorter`](#topologicalsortergraphnone) object.
</dd></dl>

#### 0.5.1
<dl><dd>

*released 2022/09/04*

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
</dd></dl>

#### 0.5
<dl><dd>

*released 2022/06/12*

* Initial release.
</dd></dl>


