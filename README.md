![# big](https://raw.githubusercontent.com/larryhastings/big/master/resources/images/big.header.png)

##### Copyright 2022-2024 by Larry Hastings

[![# test badge](https://img.shields.io/github/actions/workflow/status/larryhastings/big/test.yml?branch=master&label=test)](https://github.com/larryhastings/big/actions/workflows/test.yml) [![# coverage badge](https://img.shields.io/github/actions/workflow/status/larryhastings/big/coverage.yml?branch=master&label=coverage)](https://github.com/larryhastings/big/actions/workflows/coverage.yml) [![# python versions badge](https://img.shields.io/pypi/pyversions/big.svg?logo=python&logoColor=FBE072)](https://pypi.org/project/big/)


**big** is a Python package of small functions and classes
that aren't big enough to get a package of their own.
It's zillions of useful little bits of
Python code I always want to have handy.

For years, I've copied-and-pasted all my little
helper functions between projects--we've all done it.
But now I've finally taken the time to consolidate all those
useful little functions into one *big* package--no more
copy-and-paste, I just install one package and I'm ready to go.
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
It's a real pleasure to use!

**big** requires Python 3.6 or newer.  Its only dependencies
is `python-dateutil`, and that's optional.  The current version is [0.12.4.](#0124)

*Think big!*

## Why use big?

It's true that much of the code in **big** is short,
and one might reasonably have the reaction
"that's so short, it's easier to write it from scratch
every time I need it than remember where it is and how
to call it".  I still see value in these short functions
in **big** because:

1. everything in **big** is tested,
2. every interface in **big** has been thoughtfully
   considered and designed.

For example, consider
[`StateManager`.](#statemanagerstate--on_enteron_enter-on_exiton_exit-state_classnone)
If you remove the comments and documentation, it's actually pretty
short--easily less than a hundred lines.  I myself have written
state machines from scratch using a similar approach many times.
They're easy to write.  So why bother using `StateManager`?
Why not roll your own each time?

Because `StateManager` not only supports all the features you need--consider
[`accessor`](#accessorattributestate-state_managerstate_manager)
and
[`dispatch`](#dispatchstate_managerstate_manager--prefix-suffix)--its
API is carefully designed to help prevent bugs and logical errors.
In considering the predecessor of `StateManager` for inclusion in **big**,
I realized that if an "observer" initiated a state transition, it would produce
a blurry mess of observer callbacks and entered and exited states,
executed in a confusing order.  So `StateManager` in **big** simply
prevents you from executing state transitions in observers.


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
[`multisplit`,](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
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

## The best of big

Although **big** is *crammed full* of fabulous code, a few of
its subsystems rise above the rest.  If you're curious what
**big** might do for you, here are the five things in **big**
I'm proudest of:

* [**The `multi-` family of string functions**](#The-multi--family-of-string-functions)
* [`big.state`](#bigstate)
* [**Bound inner classes**](#bound-inner-classes)
* [**Enhanced `TopologicalSorter`**](#enhanced-topologicalsorter)
* [**`lines` and lines modifier functions**](#lines-and-lines-modifier-functions)

And here are five little functions/classes I use all the time:

* [`gently_title`](#gently_titles--apostrophesnone-double_quotesnone)
* [`Log`](#log-clocknone)
* [`pushd`](#pushddirectory)
* [`re_partition`](#re_partitiontext-pattern-count1--flags0-reversefalse)
* [`touch`](#touchpath)


# Index

### Modules

<dl><dd>

[`big.all`](#`bigall`)

[`big.boundinnerclass`](#`bigboundinnerclass`)

[`big.builtin`](#bigbuiltin)

[`big.file`](#bigfile)

[`big.deprecated`](#bigdeprecated)

[`big.graph`](#biggraph)

[`big.heap`](#bigheap)

[`big.itertools`](#bigitertools)

[`big.log`](#biglog)

[`big.metadata`](#bigmetadata)

[`big.scheduler`](#bigscheduler)

[`big.state`](#bigstate)

[`big.text`](#bigtext)

[`big.time`](#bigtime)

[`big.version`](#bigversion)

</dd></dl>

### Functions, classes, and values

<dl><dd>

[`accessor(attribute='state', state_manager='state_manager')`](#accessorattributestate-state_managerstate_manager)

[`ascii_linebreaks`](#ascii_linebreaks)

[`ascii_linebreaks_without_crlf`](#ascii_linebreaks_without_crlf)

[`ascii_whitespace`](#ascii_whitespace)

[`ascii_whitespace_without_crlf`](#ascii_whitespace_without_crlf)

[`BoundInnerClass`](#boundinnerclasscls)

[`bytes_linebreaks`](#bytes_linebreaks)

[`bytes_linebreaks_without_crlf`](#bytes_linebreaks_without_crlf)

[`bytes_whitespace`](#bytes_whitespace)

[`bytes_whitespace_without_crlf`](#bytes_whitespace_without_crlf)

[`combine_splits(s, *split_arrays)`](#combine_splitss-split_arrays)

[`CycleError()`](#cycleerror)

[`datetime_ensure_timezone(d, timezone)`](#datetime_ensure_timezoned-timezone)

[`datetime_set_timezone(d, timezone)`](#datetime_set_timezoned-timezone)

[`default_clock()`](#default_clock)

[`Delimiter(close, *, escape='', multiline=True, quoting=False)`](#delimiterclose--escape-multilinetrue-quotingfalse)

[`dispatch(state_manager='state_manager', *, prefix='', suffix='')`](#dispatchstate_managerstate_manager--prefix-suffix)

[`encode_strings(o, *, encoding='ascii')`](#encode_stringso--encodingascii)

[`Event(scheduler, event, time, priority, sequence)`](#eventscheduler-event-time-priority-sequence)

[`Event.cancel()`](#eventcancel)

[`fgrep(path, text, *, encoding=None, enumerate=False, case_insensitive=False)`](#fgreppath-text--encodingnone-enumeratefalse-case_insensitivefalse)

[`file_mtime(path)`](#file_mtimepath)

[`file_mtime_ns(path)`](#file_mtime_nspath)

[`file_size(path)`](#file_sizepath)

[`format_map(s, mapping)`](#format_maps-mapping)

[`gently_title(s, *, apostrophes=None, double_quotes=None)`](#gently_titles--apostrophesnone-double_quotesnone)

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

[`linebreaks`](#linebreaks)

[`linebreaks_without_crlf`](#linebreaks_without_crlf)

[`LineInfo(lines, line, line_number, column_number, *, leading=None, trailing=None, end=None, indent=0, match=None, **kwargs)`](#lineinfolines-line-line_number-column_number--leadingnone-trailingnone-endnone-indent0-matchnone-kwargs)

[`LineInfo.clip_leading(line, s)`](#lineinfoclip_leadingline-s)

[`LineInfo.clip_trailing(line, s)`](#lineinfoclip_trailingline-s)

[`lines(s, separators=None, *, clip_linebreaks=True, line_number=1, column_number=1, tab_width=8, **kwargs)`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs)

[`lines_convert_tabs_to_spaces(li)`](#lines_convert_tabs_to_spacesli)

[`lines_filter_empty_lines(li)`](#lines_filter_empty_linesli)

[`lines_filter_line_comment_lines(li, comment_markers)`](#lines_filter_line_comment_linesli-comment_markers)

[`lines_containing(li, s, *, invert=False)`](#lines_containingli-s--invertfalse)

[`lines_grep(li, pattern, *, invert=False, flags=0, match='match')`](#lines_grepli-pattern--invertfalse-flags0-matchmatch)

[`lines_rstrip(li, separators=None)`](#lines_rstripli-separatorsnone)

[`lines_sort(li, *, key=None, reverse=False)`](#lines_sortli--keynone-reversefalse)

[`lines_strip(li, separators=None)`](#lines_stripli-separatorsnone)

[`lines_strip_indent(li)`](#lines_strip_indentli)

[`lines_strip_line_comments(li, line_comment_markers, *, quotes=(), escape='\\', multiline_quotes=())`](#lines_strip_line_commentsli-line_comment_markers--quotes-escape-multiline_quotes)

[`Log(clock=None)`](#log-clocknone)

[`Log.enter(subsystem)`](#logentersubsystem)

[`Log.exit()`](#logexit)

[`Log.print(*, print=None, title="[event log]", headings=True, indent=2, seconds_width=2, fractional_width=9)`](#logprint-printnone-titleevent-log-headingstrue-indent2-seconds_width2-fractional_width9)

[`Log.reset()`](#logreset)

[`merge_columns(*columns, column_separator=" ", overflow_response=OverflowResponse.RAISE, overflow_before=0, overflow_after=0)`](#merge_columnscolumns-column_separator--overflow_responseoverflowresponseraise-overflow_before0-overflow_after0)

[`multipartition(s, separators, count=1, *, reverse=False, separate=True)`](#multipartitions-separators-count1--reverseFalse-separateTrue)

[`multisplit(s, separators, *, keep=False, maxsplit=-1, reverse=False, separate=False, strip=False)`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)

[`multistrip(s, separators, left=True, right=True)`](#multistrips-separators-leftTrue-rightTrue)

[`normalize_whitespace(s, separators=None, replacement=None)`](#normalize_whitespaces-separatorsNone-replacementnone)

[`parse_timestamp_3339Z(s, *, timezone=None)`](#parse_timestamp_3339zs--timezonenone)

[`pure_virtual()`](#pure_virtual)

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

[Release history](#release-history)

[`reversed_re_finditer(pattern, string, flags=0)`](#reversed_re_finditerpattern-string-flags0)

[`safe_mkdir(path)`](#safe_mkdirpath)

[`safe_unlink(path)`](#safe_unlinkpath)

[`Scheduler(regulator=default_regulator)`](#schedulerregulatordefault_regulator)

[`Scheduler.schedule(o, time, *, absolute=False, priority=DEFAULT_PRIORITY)`](#schedulerscheduleo-time--absolutefalse-prioritydefault_priority)

[`Scheduler.cancel(event)`](#schedulercancelevent)

[`Scheduler.queue`](#schedulerqueue)

[`Scheduler.non_blocking()`](#schedulernon_blocking)

[`SingleThreadedRegulator()`](#singlethreadedregulator)

[`split_delimiters(s, delimiters={...}, *, state=())`](#split_delimiterss-delimiters--state)

[`split_quoted_strings(s, quotes=('"', "'"), *, escape='\\', multiline_quotes=(), state='')`](#split_quoted_stringss-quotes---escape-multiline_quotes-state)

[`split_text_with_code(s, *, tab_width=8, allow_code=True, code_indent=4, convert_tabs_to_spaces=True)`](#split_text_with_codes--tab_width8-allow_codetrue-code_indent4-convert_tabs_to_spacestrue)

[`split_title_case(s, *, split_allcaps=True)`](#split_title_cases--split_allcapstrue)

[`State()`](#state)

[`StateManager(state, *, on_enter='on_enter', on_exit='on_exit', state_class=None)`](#statemanagerstate--on_enteron_enter-on_exiton_exit-state_classnone)

[`str_linebreaks`](#str_linebreaks)

[`str_linebreaks_without_crlf`](#str_linebreaks_without_crlf)

[`str_whitespace`](#str_whitespace)

[`str_whitespace_without_crlf`](#str_whitespace_without_crlf)

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

[`unicode_linebreaks`](#unicode_linebreaks)

[`unicode_linebreaks_without_crlf`](#unicode_linebreaks_without_crlf)

[`unicode_whitespace`](#unicode_whitespace)

[`unicode_whitespace_without_crlf`](#unicode_whitespace_without_crlf)

[`Version(s=None, *, epoch=None, release=None, release_level=None, serial=None, post=None, dev=None, local=None)`](#versionsnone--epochnone-releasenone-release_levelnone-serialnone-postnone-devnone-localnone)

['Version.format(s)'](#versionformats)

[`whitespace`](#whitespace)

[`whitespace_without_crlf`](#whitespace_without_crlf)

[`wrap_words(words, margin=79, *, two_spaces=True)`](#wrap_wordswords-margin79--two_spacestrue)

</dd></dl>

### Topic deep-dives

<dl><dd>

[**The `multi-` family of string functions**](#The-multi--family-of-string-functions)

[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)

[**`lines` and lines modifier functions**](#lines-and-lines-modifier-functions)

[**Word wrapping and formatting**](#word-wrapping-and-formatting)

[**Bound inner classes**](#bound-inner-classes)

[**Enhanced `TopologicalSorter`**](#enhanced-topologicalsorter)

</dd></dl>


# API Reference, By Module


## `big.all`

<dl><dd>

This submodule doesn't define any of its own symbols.  Instead, it
imports every other submodule in **big**, and uses `import *` to
import every symbol from every other submodule, too.  Every
public symbol in **big** is available in `big.all`.

</dd></dl>

## `big.boundinnerclass`

<dl><dd>

Class decorators that implement bound inner classes.  See the
[**Bound inner classes**](#bound-inner-classes)
deep-dive for more information.

</dd></dl>

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
* If you put a *class* inside a class,
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

<dl><dd>

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

</dd></dl>

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


## `big.deprecated`

<dl><dd>

Old versions of functions (and classes) from **big**.  These
versions are deprecated, either because the name was changed,
or the semantics were changed, or both.

Unlike the other modules, the contents of `big.deprecated` aren't
automatically imported into `big.all`.  (`big.all` does import
the `deprecated` submodule, it just doesn't `from deprected import *`
all the symbols.)

</dd></dl>

## `big.file`

<dl><dd>

Functions for working with files, directories, and I/O.

</dd></dl>

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
```

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

<dl><dd>

A drop-in replacement for Python's
[`graphlib.TopologicalSorter`](https://docs.python.org/3/library/graphlib.html#graphlib.TopologicalSorter)
with an enhanced API.  This version of `TopologicalSorter` allows modifying the
graph at any time, and supports multiple simultaneous *views,* allowing
iteration over the graph more than once.

See the [**Enhanced `TopologicalSorter`**](#enhanced-topologicalsorter) deep-dive for more information.

</dd></dl>

#### `CycleError()`

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

<dl><dd>

Functions for working with heap objects.
Well, just one heap object really.

</dd></dl>

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

<dl><dd>

Functions and classes for working with iteration.
Only one entry so far.

</dd></dl>

#### `PushbackIterator(iterable=None)`

<dl><dd>

Wraps any iterator, allowing you to push items back on the iterator.
This allows you to "peek" at the next item (or items); you can get the
next item, examine it, and then push it back.  If any objects have
been pushed onto the iterator, they are yielded first, before attempting
to yield from the wrapped iterator.

The constructor accepts one argument, an `iterable`, with a default of `None`.
If `iterable` is `None`, the `PushbackIterator` is created in an exhausted state.

When the wrapped `iterable` is exhausted (or if you passed in `None`
to the constructor) you can still call the `push` method to add items,
at which point the `PushBackIterator` can be iterated over again.

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

<dl><dd>

A simple and lightweight logging class, useful for performance analysis.
Not intended as a full-fledged logging facility like Python's
[`logging`](https://docs.python.org/3/library/logging.html) module.

</dd></dl>

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
After resetting the log, the log is
empty except for the initial `"log start"`
message, the elapsed time is zero, and
the log has not "entered" any subsystems.
</dd></dl>

## `big.metadata`

<dl><dd>

Contains metadata about **big** itself.

</dd></dl>

#### `metadata.version`

<dl><dd>

A
[`Version`](#versionsnone--epochnone-releasenone-release_levelnone-serialnone-postnone-devnone-localnone)
object representing the current version of **big**.

</dd></dl>


## `big.scheduler`

<dl><dd>

A replacement for Python's `sched.scheduler` object,
adding full threading support and a modern Python interface.

Python's `sched.scheduler` object was added way back in 1991,
and it was full of clever ideas.  It abstracted away the
concept of time from its interface, allowing it to be adapted
to new schemes of measuring time--including mock time, making
testing easy and repeatable.  Very nice!

Unfortunately, `sched.scheduler` predates multithreading
becoming common, much less multicore computers.  It certainly
predates threading support in Python.  And its API isn't
flexible enough to correctly handle some common scenarios in
multithreaded programs:

* If one thread is blocking on `sched.scheduler.run`,
  and the next scheduled event will occur at time **T**,
  and a second thread schedules a new event which
  occurs at a time < **T**, `sched.scheduler.run` won't
  return any events to the first thread until time **T**.
* If one thread is blocking on `sched.scheduler.run`,
  and the next scheduled event will occur at time **T**,
  and a second thread cancels all events,
  `sched.scheduler.run` won't exit until time **T**.

big's `Scheduler` object fixes both these problems.

Also, `sched.scheduler` is thirty years behind the times in
Python API design--its design predates many common modern
Python conventions.  Its events are callbacks, which it
calls directly.  `Scheduler` fixes this: *its* events are
*objects,* and you iterate over the `Scheduler` object to
see events as they occur.

`Scheduler` also benefits from thirty years of experience
with `sched.scheduler`.  In particular, **big** reimplements the
relevant parts of the `sched.scheduler` test suite, ensuring
`Scheduler` will never trip over the problems discovered
by `sched.scheduler` over its lifetime.

</dd></dl>

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
with `Scheduler`.  Your `Regulator` subclass must
implement three methods: `now`, `sleep`, and `wake`.
It must also provide a `lock` attribute.

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

#### `Regulator.lock`

<dl><dd>

A [lock](https://en.wikipedia.org/wiki/Lock_(computer_science))
object.  The `Scheduler` uses this lock
to protect its internal data structures.

Must support the "context manager" protocol
(`__enter__` and `__exit__`).  Entering the
object must acquire the lock; exiting must
release the lock.

This lock does not need to be
[recursive.](https://en.wikipedia.org/wiki/Reentrant_mutex)
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

Schedules an object `o` to be yielded as an event by this `schedule`
object at some time in the future.

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
multiple threads, and in particular is *not* thread-safe.
But it's much higher performance
than thread-safe `Regulator` implementations.
</dd></dl>

### `ThreadSafeRegulator()`

<dl><dd>

A thread-safe implementation of `Regulator`
designed for use in multithreaded programs.
</dd></dl>


## `big.state`

<dl><dd>

Library code for working with simple state machines.

There are lots of popular Python libraries for implementing
state machines.  But they all seem to be designed for
*large-scale* state machines.  These libraries are
sophisticated and data-driven, with expansive APIs.
And, as a rule, they require the state to be
a passive object (e.g. an `Enum`), and require you to explicitly
describe every possible state transition.

This approach is great for massive, super-complex state
machines--you need the features of a sophisticated library
to manage all that complexity.  It also enables clever
features like automatically generating diagrams of your
state machine, which is great!

But most of the time this level of sophistication is
unnecessary.  There are lots of use cases for small scale,
*simple* state machines, where this data-driven approach
and expansive, complex API only gets in the way.  I prefer
writing my state machines with active objects--where states
are implemented as classes, events are implemented as method
calls on those classes, and you transition to a new state by
simply overwriting a `state` attribute with a different state
instance.

`big.state` makes this style of state machine easy.  It has
a deliberately minimal, simple interface--the constructor for
the main `StateManager` class only has four parameters,
and it only exposes three attributes.  The module also has
two decorators to make your life easier.  And that's it!
But even this small API surface area makes it effortless to
write large scale state machines.

(But you can also write tiny data-driven state machines too.
Although `big.state` makes state machines with active states
easy to write, it's agnostic about how you actually implement
your state machine.  `big.state` makes it easy to write any
kind of state machine you like!)

`big.state` provides features like:

* method calls that get called when entering and exiting a state,
* "observers", callables that get called each time you transition
  to a new state, and
* safety mechanisms to catch bugs and prevent design mistakes.

</dd></dl>

#### Recommended best practices

The main class in `big.state` is `StateManager`.  This class
maintains the current "state" of your state machine, and
manages transitions to new states.  The constructor takes
one required parameter, the initial state.

Here are my recommendations for best practices when working
with `StateManager` for medium-sized and larger state machines:

* Your state machine should be implemented as a *class.*
    * You should store `StateManager` as an attribute of that class,
      preferably called `state_manager`.  (Your state machine
      should have a "has-a" relationship with `StateManager`,
      not an "is-a" relationship where it inherits from `StateManager`.)
    * You should decorate your state machine class with the
      [`accessor`](accessorattributestate-state_managerstate_manager)
      decorator--this will save you a lot of boilerplate.
      If your state machine is stored in `o`, decorating with
      `accessor` lets you can access the current state using
      `o.state` instead of `o.state_manager.state`.
* Every state should be implemented as a *class.*
    * You should have a base class for your state classes,
      containing whatever functionality they have in common.
    * You're encouraged to define these state classes *inside*
      your state machine class, and use
      [`BoundInnerClass`](#boundinnerclasscls)
      so they automatically get references to the state machine
      they're a part of.
* Events should be *method calls* made on your state machine object.
    * Your state base class should have a method for every
      event, decorated with [`pure_virtual'](pure_virtual).
    * As a rule, events should be dispatched from the state machine
      to a method call on the current state with the same name.
    * If all the code to handle a particular event lives in the
      states, use the
      [`dispatch`](#dispatchstate_managerstate_manager--prefix-suffix)
      decorator to save you more boilerplate when calling the event
      method.  Similarly to
      [`accessor`,](accessorattributestate-state_managerstate_manager)
      this creates a new method for you that calls the equivalent
      method on the current state, passing in all the arguments
      it received.

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

This code demonstrates both
[`accessor`](accessorattributestate-state_managerstate_manager)
and
[`dispatch`.](#dispatchstate_managerstate_manager--prefix-suffix)
`accessor` lets us reference the current state with `sm.state`
instead of `sm.state_manager.state`, and `dispatch` lets us call
`sm.toggle()` instead of `sm.state_manager.state.toggle()`.

For a more complete example of working with `StateManager`,
see the `test_vending_machine` test code in `tests/test_state.py`
in the **big** source tree.

#### `accessor(attribute='state', state_manager='state_manager')`

<dl><dd>

Class decorator.  Adds a convenient state accessor attribute to your class.

When you have a state machine class containing a
[`StateManager`](#statemanagerstate--on_enteron_enter-on_exiton_exit-state_classnone)
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

The `accessor` class decorator creates a property for you--a
shortcut that directly accesses the `state` attribute of
your state manager.  Just decorate your state machine class
with `@accessor()`:

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
state machine class with

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
use a single ellipsis as the body of these functions, as in the
example above.  This is a visual cue to readers that the body of the
function doesn't matter.  (In fact, the original `on_sunrise` method
above is thrown away inside the decorator, and replaced with a customized
method dispatch function.)

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


#### `State()`

<dl><dd>

Base class for state machine state implementation classes.
Use of this base class is optional; states can be instances
of any type except `types.NoneType`.

</dd></dl>

#### `StateManager(state, *, on_enter='on_enter', on_exit='on_exit', state_class=None)`

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
And if the `StateManager` *is* currently
transitioning to a new state, its `next` attribute will
*not* be `None`.

During the time the manager is currently transitioning to
a new state, it's illegal to start a second transition.  (In
other words: you can't assign to `state` while `next` is not
`None`.)


</dd><dt>

`observers`
</dt><dd>

A list of callables that get called during every state
transition.  It's initially empty; you may add and remove
observers to the list as needed.

* The callables will be called with one positional argument,
  the state manager object.
* Since observers are called during the state transition,
  they aren't permitted to initiate state transitions.
* You're permitted to modify the list of observers
  at any time--even from inside an observer callback.
  Note that this won't modify the list of observers called
  until the *next* state transition.
  (`StateManager` uses a copy of the observer list.)

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

If `on_enter` is a valid identifier string, and this
[`StateManager`](#statemanagerstate--on_enteron_enter-on_exiton_exit-state_classnone)
object transitions to a state object *O*, and *O* has an attribute
with this name,
[`StateManager`](#statemanagerstate--on_enteron_enter-on_exiton_exit-state_classnone)
will call that attribute (with no
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
Its default value is `'on_exit'`.

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


#### `TransitionError()`

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

<dl><dd>

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

As a rule, no further testing, casting, or catching exceptions
is done.

Functions that take multiple string-like parameters require all
such arguments to be the same type.
These functions will check that all such arguments
are of the same type.

Subclasses of `str` and `bytes` will also work; anywhere you
should pass in a `str`, you can also pass in a subclass of
`str`, and likewise for `bytes`.

</dd></dl>

#### `ascii_linebreaks`

<dl><dd>

A tuple of `str` objects, representing every line-breaking whitespace
character defined by ASCII.

Useful as a `separator` argument for **big** functions that accept one,
e.g. [the **big** "multi-" family of functions,](#the-multi--family-of-string-functions)
or the [`lines` and lines modifier functions.](#lines-and-lines-modifier-functions)

Also contains `'\r\n'`.
If you don't want to include this string, use [`ascii_linebreaks_without_crlf`](#ascii_linebreaks_without_crlf) instead.
See the deep-dive section on
[**The Unix, Mac, and DOS line-break conventions**](#the-unix-mac-and-dos-line-break-conventions)
for more.

For more information, please see the
[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
deep-dive.

</dd></dl>

#### `ascii_linebreaks_without_crlf`

<dl><dd>

Equivalent to [`ascii_linebreaks`](#ascii_linebreaks) without `'\r\n'`.

</dd></dl>

#### `ascii_whitespace`
<dl><dd>

A tuple of `str` objects, representing every whitespace
character defined by ASCII.

Useful as a `separator` argument for **big** functions that accept one,
e.g. [the **big** "multi-" family of functions,](#the-multi--family-of-string-functions)
or the [`lines` and lines modifier functions.](#lines-and-lines-modifier-functions)

Also contains `'\r\n'`.
If you don't want to include this string, use [`ascii_whitespace_without_crlf`](#ascii_whitespace_without_crlf) instead.
See the deep-dive section on
[**The Unix, Mac, and DOS line-break conventions**](#the-unix-mac-and-dos-line-break-conventions)
for more.

For more information, please see the
[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
deep-dive.

</dd></dl>

#### `ascii_whitespace_without_crlf`

<dl><dd>

Equivalent to [`ascii_whitespace`](#ascii_whitespace) without `'\r\n'`.

</dd></dl>

#### `bytes_linebreaks`

<dl><dd>

A tuple of `bytes` objects, representing every line-breaking whitespace
character recognized by the Python `bytes` object.

Useful as a `separator` argument for **big** functions that accept one,
e.g. [the **big** "multi-" family of functions,](#the-multi--family-of-string-functions)
or the [`lines` and lines modifier functions.](#lines-and-lines-modifier-functions)

Also contains `b'\r\n'`.
If you don't want to include this string, use [`bytes_linebreaks_without_crlf`](#bytes_linebreaks_without_crlf) instead.
See the deep-dive section on
[**The Unix, Mac, and DOS line-break conventions**](#the-unix-mac-and-dos-line-break-conventions)
for more.

For more information, please see the
[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
deep-dive.

</dd></dl>

#### `bytes_linebreaks_without_crlf`

<dl><dd>

Equivalent to [`bytes_linebreaks`](#bytes_linebreaks) with `'\r\n'` removed.

</dd></dl>

#### `bytes_whitespace`
<dl><dd>

A tuple of `bytes` objects, representing every line-breaking whitespace
character recognized by the Python `bytes` object.  (`bytes.isspace`,
`bytes.split`, etc will tell you which characters are considered whitespace...)

Useful as a `separator` argument for **big** functions that accept one,
e.g. [the **big** "multi-" family of functions,](#the-multi--family-of-string-functions)
or the [`lines` and lines modifier functions.](#lines-and-lines-modifier-functions)

Also contains `b'\r\n'`.
If you don't want to include this string, use [`bytes_whitespace_without_crlf`](#bytes_whitespace_without_crlf) instead.
See the deep-dive section on
[**The Unix, Mac, and DOS line-break conventions**](#the-unix-mac-and-dos-line-break-conventions)
for more.

For more information, please see the
[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
deep-dive.

</dd></dl>

#### `bytes_whitespace_without_crlf`

<dl><dd>

Equivalent to [`bytes_whitespace`](#bytes_whitespace) without `'\r\n'`.

</dd></dl>

#### `combine_splits(s, *split_arrays)`

<dl><dd>

Takes a string `s`, and one or more "split arrays",
and applies all the splits to `s`.  Returns
an iterator of the resulting string segments.

A "split array" is an array containing the original
string, but split into multiple pieces.  For example,
the string `"a b c d e"` could be split into the
split array `["a ", "b ", "c ", "d ", "e"]`.

For example,

```
    combine_splits('abcde', ['abcd', 'e'], ['a', 'bcde'])
```

returns `['a', 'bcd', 'e']`.

Note that the split arrays *must* contain all the
characters from `s`.  `''.join(split_array)` must recreate `s`.
`combine_splits` only examines the lengths of the strings
in the split arrays, and makes no attempt to infer
stripped characters.  (So, don't use the string's `.split`
method if you want to use `combine_splits`.  Instead, consider
big's
[`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
with `keep=True` or `keep=ALTERNATING`.)

</dd></dl>

#### `Delimiter(close, *, escape='', multiline=True, quoting=False)`

<dl><dd>

Class representing a delimiter for
[`split_delimiters`](#split_delimiterss-delimiters--state).

`close` is the closing delimiter character.  It must be a valid
string or bytes object, and cannot be a backslash ('"\\"' or `b"\\"`).

If `escape` is true, it should be a string;
when inside this delimiter, you can escape the trailing
delimiter with this string.  If `escape` is false,
there is no escape string for this delimiter.

`quoting` is a boolean: does this set of delimiters "quote" the text inside?
When an open delimiter enables quoting, `split_delimiters` will ignore all
other delimiters in the text until it encounters the matching close delimiter.
(Single- and double-quotes set this to `True`.)

Currently `escape` and `quoting` must either both be true or both be false.

If `multiline` is true, the closing delimiter may be on the current line
or any subsequent line.  If `multiline` is false, the closing delimiter
must appear on the current line.

</dd></dl>

#### `encode_strings(o, *, encoding='ascii')`

<dl><dd>

Converts an object `o` from `str` to `bytes`.
If `o` is a container, recursively converts
all objects and containers inside.

`o` and all `objects` inside `o` must be either
`bytes`, `str`, `dict`, `set`, `list`, `tuple`, or a subclass
of one of those.

Encodes every string inside using the encoding
specified in the _encoding_ parameter, default
is `'ascii'`.

Handles nested containers.

If `o` is of, or contains, a type not listed above,
raises `TypeError`.

</dd></dl>

#### `format_map(s, mapping)`

<dl><dd>
An implementation of `str.format_map` supporting *nested replacements.*

Unlike `str.format_map`, big's `format_map` allows you to perform
string replacements inside of other string replacements:

```Python
  big.format_map("{{extension} size}",
      {'extension': 'mp3', 'mp3 size': 8555})
```

returns the string `'8555'`.

Another difference between `str.format_map` and big's `format_map`
is how you escape curly braces.  To produce a `'{'` or `'}'` in the
output string, add `'\{'` or `'\}'` respectively.  (To produce a
backslash, `'\\'`, you must put *four* backslashes, `'\\\\'`.)

See the documentation for `str.format_map` for more.

</dd></dl>

#### `gently_title(s, *, apostrophes=None, double_quotes=None)`

<dl><dd>

Uppercases the first character of every word in `s`,
leaving the other letters alone.  `s` should be `str` or `bytes`.

(For the purposes of this algorithm, words are
any contiguous run of non-whitespace characters.)

This function will also capitalize the letter after an apostrophe
if the apostrophe:

  * is immediately after whitespace, or
  * is immediately after a left parenthesis character (`'('`), or
  * is the first letter of the string, or
  * is immediately after a letter O or D, when that O or D
      * is after whitespace, or
      * is the first letter of the string.

In this last case, the O or D will also be capitalized.

Finally, this function will capitalize the letter
after a quote mark if the quote mark:

* is after whitespace, or
* is the first letter of a string.

(A run of consecutive apostrophes and/or
quote marks is considered one quote mark for
the purposes of capitalization.)

All these rules mean `gently_title` correctly handles
internally quoted strings:

```
    He Said 'No I Did Not'
```

and contractions that start with an apostrophe:

```
    'Twas The Night Before Christmas
```

as well as certain Irish, French, and Italian names:

```
    Peter O'Toole
    Lord D'Arcy
```

If specified, `apostrophes` should be a `str`
or `bytes` object containing characters that
should be considered apostrophes.  If `apostrophes`
is false, and `s` is `bytes`, `apostrophes` is set to
a bytes object containing the only ASCII apostrophe character:

```
    '
```

If `apostrophes` is false and s is `str`, `apostrophes`
is set to a string containing these Unicode apostrophe code points:

```
    '‘’‚‛
```

Note that neither of these strings contains the "back-tick"
character:

```
    `
```

This is a diacritical used for modifying letters, and isn't
used as an apostrophe.

If specified, `double_quotes` should be a `str`
or `bytes` object containing characters that
should be considered double-quote characters.
If `double_quotes` is false, and `s` is `bytes`,
`double_quotes` is set to a bytes object containing
the only ASCII double-quote character:

```
    "
```

If `double_quotes` is false and `s` is `str`, double_quotes
is set to a string containing these Unicode double-quote code points:

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


#### `linebreaks`

<dl><dd>

A tuple of `str` objects, representing every line-breaking
whitespace character recognized by the Python `str` object.
Identical to [`str_linebreaks`.](#str_linebreaks)

Useful as a `separator` argument for **big** functions that accept one,
e.g. [the **big** "multi-" family of functions,](#the-multi--family-of-string-functions)
or the [`lines` and lines modifier functions.](#lines-and-lines-modifier-functions)

Also contains `'\r\n'`.  See the deep-dive section on
[**The Unix, Mac, and DOS line-break conventions**](#the-unix-mac-and-dos-line-break-conventions)
for more.

For more information, please see the
[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
deep-dive.

</dd></dl>


#### `linebreaks_without_crlf`

<dl><dd>

Equivalent to [`linebreaks`](#linebreaks) without `'\r\n'`.

</dd></dl>


#### `LineInfo(lines, line, line_number, column_number, *, leading=None, trailing=None, end=None, indent=0, match=None, **kwargs)`

<dl><dd>

The first object in the 2-tuple yielded by a
[`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs)
iterator, containing metadata about the line.
Every parameter to the constructor is stored as
an attribute of the new `LineInfo` object using
the same identifier.

`line` is the original unmodified line, split
from the original `s` input to `lines`.  Note
that `line` includes the trailing newline character,
if any.

`line_number` is the line number of this line.
`
`column_number` is the starting column of the
accompanying `line` string (the second entry
in the 2-tuple yielded by `lines`).

`leading` and `trailing` are strings that have
been stripped from the beginning or end of the
original `line`, if any.  (Not counting the
line-terminating linebreak character.)

`end` is the linebreak character that terminated
the current line, if any.  If the `s` passed in to
`lines` is an iterator yielding strings, `end`
will always be an empty string.

`indent` is the indent level of the current line,
represented as an integer.  See [`lines_strip_indent`](#lines_strip_indentli).
If the indent level hasn't been measured yet this
should be `0`.

`match` is the `re.Match` object that matched this
line, if any.  See [`lines_grep`](#lines_grepli-pattern--invertfalse-flags0-matchmatch).

You can add your own fields by passing them in
via `**kwargs`; you can also add new attributes
or modify existing attributes as needed from
inside a "lines modifier" function.

For more information, see the deep-dive on
[**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)
</dd></dl>

#### `LineInfo.clip_leading(line, s)`

<dl><dd>

Clip the leading substring `s` from `line`.

`s` may be either a string (`str` or `bytes`) or an `int`.
If `s` is a string, it must match the leading substring
of `line` you wish clipped.  If `s` is an `int`, it should
representing the number of characters you want clipped
from the beginning of `s`.

Returns `line` with `s` clipped; also appends
the clipped portion to `self.leading`, and updates
`self.column_number` to represent the column number
where `line` now starts.  (If the clipped portion of
`line` contains tabs, it's detabbed using `lines.tab_width`
and the `detab` method on the clipped substring before it
is measured.)

</dd></dl>

#### `LineInfo.clip_trailing(line, s)`

<dl><dd>

Clip the trailing substring `s` from `line`.

`s` may be either a string (`str` or `bytes`) or an `int`.
If `s` is a string, it must match the trailing substring
of `line` you wish clipped.  If `s` is an `int`, it should
representing the number of characters you want clipped
from the end of `s`.

Returns `line` with `s` clipped; also appends
the clipped portion to `self.trailing`.

</dd></dl>


#### `lines(s, separators=None, *, clip_linebreaks=True, line_number=1, column_number=1, tab_width=8, **kwargs)`

<dl><dd>

A "lines iterator" object.  Splits s into lines, and iterates yielding those lines.


When iterated over, yields 2-tuples:

```
     (info, line)
```

where `info` is a
[`LineInfo`](#lineinfolines-line-line_number-column_number--leadingnone-trailingnone-endnone-indent0-matchnone-kwargs)
object, and `line` is a `str` or `bytes` object.

`s` can be `str`, `bytes`, or an iterable.

If `s` is neither `str` nor `bytes`, `s` must be an iterable.
The iterable should either yield individual strings, which is the
line, or it should yield a tuple containing two strings, in which case
the strings should be the line and the line-terminating newline respectively.
All "string" objects yielded by this iterable should be homogeneous,
either `str` or `bytes`.

`separators` should either be `None` or an iterable of separator strings,
as per the `separators` argument to `multisplit`.  If `s` is `str` or `bytes`,
it will be split using `multisplit`, using these separators.  If
`separators` is `None`--which is the default value--and `s` is `str` or `bytes`,
`s` will be split at linebreak characters.  (If `s` is neither `str` nor `bytes`,
`separators` must be `None`.)

`line_number` is the starting line number given to the first
[`LineInfo`](#lineinfolines-line-line_number-column_number--leadingnone-trailingnone-endnone-indent0-matchnone-kwargs)
object.  This number is then incremented for every subsequent line.

`column_number` is the starting column number given to every
[`LineInfo`](#lineinfolines-line-line_number-column_number--leadingnone-trailingnone-endnone-indent0-matchnone-kwargs)
object.  This number represents the leftmost column of every line.

`tab_width` isn't used by lines itself, but is stored internally and
may be used by other lines modifier functions (e.g. [`lines_strip_indent`](#lines_strip_indentli),
`lines_convert_tabs_to_spaces`).  Similarly, all keyword arguments passed
in via kwargs are stored internally and can be accessed by user-defined
lines modifier functions.

`lines` copies the line-breaking character (usually `\n`) from each line
to `info.end`. If `clip_linebreaks` is true (the default), `lines` will clip
the line-breaking character off the end of each line.  If `clip_linebreaks`
is false, `lines` will leave the line-breaking character in place.

You can pass in an instance of a subclass of `bytes` or `str`
for `s` and elements of `separators`, but the base class
for both must be the same (`str` or `bytes`).  `lines` will
only yield `str` or `bytes` objects for `line`.

Composable with all the `lines_` modifier functions in the `big.text` module.

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

#### `lines_filter_empty_lines(li)`

<dl><dd>

A lines modifier function.  Filters out the empty lines
of a "lines iterator".

Preserves the line numbers.  If lines 0 through 2 are empty,
line 3 is `'a'``, line 4 is empty, and line 5 is `'b'``, this will yield:
```
    (LineInfo(line='a', line_number=3), 'a')
    (LineInfo(line='b', line_number=5), 'b')
```

For more information, see the deep-dive on
[**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)
</dd></dl>

#### `lines_filter_line_comment_lines(li, comment_markers)`

<dl><dd>

A lines modifier function.  Filters out comment lines from the
lines of a "lines iterator".  Comment lines are lines whose
first non-whitespace characters appear in the iterable of
`comment_separators` strings passed in.

What's the difference between
[`lines_strip_line_comments`](#lines_strip_line_commentsli-line_comment_markers--quotes-escape-multiline_quotes)
and
`lines_filter_line_comment_lines`?

* `lines_filter_line_comment_lines`
  only recognizes lines that *start* with a comment separator
  (ignoring leading whitespace).  Also, it filters out those
  lines completely, rather than modifying the line.
* [`lines_strip_line_comments`](#lines_strip_line_commentsli-line_comment_markers--quotes-escape-multiline_quotes)
  handles comment markers anywhere in the line, and it can also ignore
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

If `invert` is true, returns the opposite--filters
out lines that contain `s`.

For more information, see the deep-dive on
[**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)
</dd></dl>

#### `lines_grep(li, pattern, *, invert=False, flags=0, match='match')`

<dl><dd>

A lines modifier function.  Only yields lines
that match the regular expression `pattern`.
(Filters out lines that don't match `pattern`.)
Stores the resulting `re.Match` object in `info.match`.

`pattern` can be `str`, `bytes`, or an `re.Pattern` object.
If `pattern` is not an `re.Pattern` object, it's compiled
with `re.compile(pattern, flags=flags)`.

If `invert` is true, returns the opposite--filters
out lines that match `pattern`.

The match parameter specifies the
[`LineInfo`](#lineinfolines-line-line_number-column_number--leadingnone-trailingnone-endnone-indent0-matchnone-kwargs)
attribute name to
write to.  By default it writes to `info.match`; you can specify
any valid identifier, and it will instead write the `re.Match`
object (or `None`) to the identifier you specify.

For more information, see the deep-dive on
[**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)

(In older versions of Python, `re.Pattern` was a private type called
`re._pattern_type`.)
</dd></dl>

#### `lines_rstrip(li, separators=None)`

<dl><dd>

A lines modifier function.  Strips trailing whitespace from the
lines of a "lines iterator".

`separators` is an iterable of separators, like the argument
to `multistrip`.  The default value is `None`, which means
`lines_rstrip` strips all trailing whitespace characters.

All characters removed are clipped to `info.trailing`
as appropriate.  If the line is non-empty before stripping, and
empty after stripping, the entire line is clipped to `info.trailing`.

For more information, see the deep-dive on
[**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)
</dd></dl>

#### `lines_sort(li, *, key=None, reverse=False)`

<dl><dd>

A lines modifier function.  Sorts all input lines before
yielding them.

If `key` is specified, it's used as the `key` parameter to `list.sort`.
The `key` function will be called with the `(info, line)`` tuple yielded
by the *lines iterator.*  If `key` is a false value, `lines_sort`
sorts the lines lexicographically, from lowest to highest.

If `reverse` is true, lines are sorted from highest to lowest.

For more information, see the deep-dive on
[**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)
</dd></dl>

#### `lines_strip(li, separators=None)`

<dl><dd>

A lines modifier function.  Strips leading and trailing strings
from the lines of a "lines iterator".

`separators` is an iterable of separators, like the argument
to `multistrip`.  The default value is `None`, which means
`lines_strip` strips all leading and trailing whitespace characters.

All characters are clipped to `info.leading` and `info.trailing`
as appropriate.  If the line is non-empty before stripping, and
empty after stripping, the entire line is clipped to `info.trailing`.

For more information, see the deep-dive on
[**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)
</dd></dl>

#### `lines_strip_indent(li)`

<dl><dd>

A lines modifier function.  Strips leading whitespace and tracks
the indent level.

The indent level is stored in the
[`LineInfo`](#lineinfolines-line-line_number-column_number--leadingnone-trailingnone-endnone-indent0-matchnone-kwargs)
object's attribute
`indent`.  `indent` is an integer, the ordinal number of the current
indent; if the text has been indented three times, `indent` will be 3.

Strips any leading whitespace from the line, updating the
[`LineInfo`](#lineinfolines-line-line_number-column_number--leadingnone-trailingnone-endnone-indent0-matchnone-kwargs)
attributes `leading` and `column_number` as needed.

Uses an intentionally simple algorithm.
Only understands tab and space characters as indent characters.
Internally detabs to spaces first for consistency, using the
`tab_width` passed in to lines.

You can only dedent out to a previous indent.
Raises `IndentationError` if there's an illegal dedent.

For more information, see the deep-dive on
[**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)
</dd></dl>

#### `lines_strip_line_comments(li, line_comment_markers, *, quotes=(), escape='\\', multiline_quotes=())`

<dl><dd>

A lines modifier function.  Strips comments from the lines
of a "lines iterator".  Comments are substrings that indicate
the rest of the line should be ignored; `lines_strip_line_comments`
truncates the line at the beginning of the leftmost comment
separator.

`line_comment_markers` should be an iterable of line comment
marker strings.  These are strings that denote a "line comment",
which is to say, a comment that starts at that marker and extends
to the end of the line.

By default, `quotes` and `multiline_quotes` are both false,
in which case `lines_strip_line_comments` will truncate each
line, starting at the leftmost comment marker, and yield
the resulting line.  If the line doesn't contain any comment
markers, `lines_strip_line_comments` will yield it unchanged.

However, the syntax of the text you're parsing might support
quoted strings, and if so, comment marks in those quoted strings
should be ignored.  `lines_strip_quoted_strings` supports this
too, with its `escape`, `quotes`, and `multiline_quotes` parameters.

If `quotes` is true, it must be an iterable of quote characters.
`lines_strip_line_comments` will parse the line using **big**'s
[`split_quoted_strings`](#split_quoted_stringss-quotes---escape-multiline_quotes-state)
function and ignore comment
markers inside quoted strings.  Quote marks must be balanced; if you
open a quoted string, you must close it.  If a line ends with an
quoted string still open, `lines_strip_line_comments` will raise
`SyntaxError`.

`multiline_quotes` is similar to `quotes`, except quoted strings are
permitted to span lines.  If the iterator stops iteration with a
multiline quoted string still open, `lines_strip_line_comments`
will raise `SyntaxError`.

`escape` specifies an escape string to allow having the closing quote
marker inside a quoted string without closing ending the string.
If false, there is no escape string.

What's the difference between
`lines_strip_line_comments`
and
[`lines_filter_line_comment_lines`](#lines_filter_line_comment_linesli-comment_markers)?

* [`lines_filter_line_comment_lines`](#lines_filter_line_comment_linesli-comment_markers)
  only recognizes lines that *start* with a comment separator
  (ignoring leading whitespace).  Also, it filters out those lines
  completely, rather than modifying the line.
* `lines_strip_line_comments`
  handles comment markers anywhere in the line, and it can even ignore
  comments inside quoted strings.  It always yields the line, whether or
  not it's truncated the line.

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
handled with the `overflow_strategy`, described below.)

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

#### `multisplit(s, separators=None, *, keep=False, maxsplit=-1, reverse=False, separate=False, strip=False)`

<dl><dd>

Splits strings like `str.split`, but with multiple separators and options.

`s` can be `str` or `bytes`.

`separators` should either be `None` (the default),
or an iterable of `str` or `bytes`, matching `s`.

If `separators` is `None` and `s` is `str`,
`multisplit` will use [`big.whitespace`](#whitespace)
as `separators`.
If `separators` is `None` and `s` is `bytes`,
`multisplit` will use [`big.ascii_whitespace`](#whitespace)
as `separators`.

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
You can recreate the original string by using `"".join`
to join the strings yielded by `multisplit`.

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
You can recreate the original string by using `"".join`
to join the strings yielded by `multisplit`.

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

#### `split_delimiters(s, delimiters={...}, *, state=())`

<dl><dd>

Splits a string `s` at delimiter substrings.

`s` may be `str` or `bytes`.

`delimiters` may be either `None` or a mapping of open delimiter
strings to `Delimiter` objects.  The open delimiter strings,
close delimiter strings, and escape strings must match the type
of `s` (either `str` or `bytes`).

If `delimiters` is `None`, `split_delimiters` uses a default
value matching these pairs of delimiters:

```
    () [] {} "" ''
```

The first three delimiters allow multiline, disable
quoting, and have no escape string.  The last two
(the quote mark delimiters) enable quoting, disallow
multiline, and specify their escape string as a
single backslash.  (This default value automatically
supports both `str` and `bytes`.)

`state` specifies the initial state of parsing. It's an iterable
of open delimiter strings specifying the initial nested state of
the parser, with the innermost nesting level on the right.
If you wanted `split_delimiters` to behave as if it'd already seen
a `'('` and a `'['`, in that order, pass in `['(', '[']`
to `state`.

(Tip: Use a `list` as a stack to track the state of `split_delimiters`.
Push open delimiters with `.append`, and pop them off using `.pop`
whenever you see a close delimiter.  Since `split_delimiters` ensures
that open and close delimiters match, you don't need to check them
yourself!)

Yields 3-tuples containing strings:

```
    (text, open, close)
```

where `text` is the text before the next opening or closing delimiter,
`open` is the trailing opening delimiter,
and `close` is the trailing closing delimiter.
At least one of these three strings will always be non-empty.
(If `open` is non-empty, `close` will be empty, and vice-versa.)
If `s` doesn't end with an opening or closing delimiter,  the final
tuple yielded will have empty strings for both `open` and `close`.

You may not specify backslash (`'\\'`) as an open delimiter.

Multiple `Delimiter` objects specified in `delimiters` may use
the same close delimiter string.

`split_delimiters` doesn't react if the string ends with
unterminated delimiters.

See the `Delimiter` object for how delimiters are defined, and how
you can define your own delimiters.

</dd></dl>

#### `split_quoted_strings(s, quotes=('"', "'"), *, escape='\\', multiline_quotes=(), state='')`

<dl><dd>

Splits `s` into quoted and unquoted segments.

Returns an iterator yielding 3-tuples:

```
    (leading_quote, segment, trailing_quote)
```

where `leading_quote` and `trailing_quote` are either
empty strings or quote delimiters from `quotes`,
and `segment` is a substring of `s`.  Joining together
all strings yielded recreates `s`.

`s` can be either `str` or `bytes`.

`quotes` is an iterable of unique quote delimiters.
Quote delimiters may be any non-empty string.
They must be the same type as `s`, either `str` or `bytes`.
By default, `quotes` is `('"', "'")`.  (If `s` is `bytes`,
`quotes` defaults to `(b'"', b"'")`.)  If a newline character
appears inside a quoted string, `split_quoted_strings` will
raise `SyntaxError`.

`multiline_quotes` is like `quotes`, except quoted strings
using multiline quotes are permitted to contain newlines.
By default `split_quoted_strings` doesn't define any
multiline quote marks.

`escape` is a string of any length.  If `escape` is not
an empty string, the string will "escape" (quote)
quote delimiters inside a quoted string, like the
backslash ('\\') character inside strings in Python.
By default, `escape` is `'\\'`.  (If `s` is `bytes`,
`escape` defaults to `b'\\'`.)

`state` is a string.  It sets the initial state of
the function.  The default is an empty string (`str`
or `bytes`, matching `s`); this means the parser starts
parsing the string in an unquoted state.  If you
want parsing to start as if it had already encountered
a quote delimiter--for example, if you were parsing
multiple lines individually, and you wanted to begin
a new line continuing the state from the previous line--
pass in the appropriate quote delimiter from `quotes`
into `state`.  Note that when a non-empty string is
passed in to `state`, the `leading_quote` in the first
3-tuple yielded by `split_quoted_strings` will be an
empty string:

```
    list(split_quoted_strings("a b c'", state="'"))
```

evaluates to

```
    [('', 'a b c', "'")]
```

Note:
* `split_quoted_strings` is agnostic about the length
  of quoted strings.  If you're using `split_quoted_strings`
  to parse a C-like language, and you want to enforce
  C's requirement that single-quoted strings only contain
  one character, you'll have to do that yourself.
* `split_quoted_strings` doesn't raise an error
  if `s` ends with an unterminated quoted string.  In
  that case, the last tuple yielded will have a non-empty
  `leading_quote` and an empty `trailing_quote`.  (If you
  consider this an error, you'll need to raise `SyntaxError`
  in your own code.)
* `split_quoted_strings` only supports the opening and
  closing markers for a string being the same string.
  If you need the opening and closing markers to be
  different strings, use [`split_delimiters`](#split_delimiterss-delimiters--state).

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

#### `split_title_case(s, *, split_allcaps=True)`

<dl><dd>

Splits `s` into words, assuming that
upper-case characters start new words.
Returns an iterator yielding the split words.

Example:

```
    list(split_title_case('ThisIsATitleCaseString'))
```

is equal to

```
    ['This', 'Is', 'A', 'Title', 'Case', 'String']
```

If `split_allcaps` is a true value (the default),
runs of multiple uppercase characters will also
be split before the last character.  This is
needed to handle splitting single-letter words.
Consider:

```
    list(split_title_case('WhenIWasATeapot', split_allcaps=True))
```

returns

```
    ['When', 'I', 'Was', 'A', 'Teapot']
```

but

```
    list(split_title_case('WhenIWasATeapot', split_allcaps=False))
```

returns

```
    ['When', 'IWas', 'ATeapot']
```

Note: uses the `isupper` and `islower` methods
to determine what are upper- and lower-case
characters.  This means it only recognizes the ASCII
upper- and lower-case letters for bytes strings.

</dd></dl>

#### `str_linebreaks`

<dl><dd>

A tuple of `str` objects, representing every line-breaking
whitespace character recognized by the Python `str` object.
Identical to [`linebreaks`.](#linebreaks)

Useful as a `separator` argument for **big** functions that accept one,
e.g. [the **big** "multi-" family of functions,](#the-multi--family-of-string-functions)
or the [`lines` and lines modifier functions.](#lines-and-lines-modifier-functions)

Also contains `'\r\n'`.  See the deep-dive section on
[**The Unix, Mac, and DOS line-break conventions**](#the-unix-mac-and-dos-line-break-conventions)
for more.

For more information, please see the
[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
deep-dive.

</dd></dl>

#### `str_linebreaks_without_crlf`

<dl><dd>

Equivalent to [`str_linebreaks`](#str_linebreaks) without `'\r\n'`.

</dd></dl>

#### `str_whitespace`

<dl><dd>

A tuple of `str` objects, representing every whitespace
character recognized by the Python `str` object.
Identical to [`whitespace`.](#whitespace)

Useful as a `separator` argument for **big** functions that accept one,
e.g. [the **big** "multi-" family of functions,](#the-multi--family-of-string-functions)
or the [`lines` and lines modifier functions.](#lines-and-lines-modifier-functions)

Also contains `'\r\n'`.  See the deep-dive section on
[**The Unix, Mac, and DOS line-break conventions**](#the-unix-mac-and-dos-line-break-conventions)
for more.

For more information, please see the
[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
deep-dive.

</dd></dl>

#### `str_whitespace_without_crlf`

<dl><dd>

Equivalent to [`str_whitespace`](#str_whitespace) without `'\r\n'`.

</dd></dl>

#### `unicode_linebreaks`

<dl><dd>

A tuple of `str` objects, representing every line-breaking
whitespace character defined by Unicode.

Useful as a `separator` argument for **big** functions that accept one,
e.g. [the **big** "multi-" family of functions,](#the-multi--family-of-string-functions)
or the [`lines` and lines modifier functions.](#lines-and-lines-modifier-functions)

Also contains `'\r\n'`.  See the deep-dive section on
[**The Unix, Mac, and DOS line-break conventions**](#the-unix-mac-and-dos-line-break-conventions)
for more.

For more information, please see the
[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
deep-dive.

</dd></dl>

#### `unicode_linebreaks_without_crlf`

<dl><dd>

Equivalent to [`unicode_linebreaks`](#unicode_linebreaks) without `'\r\n'`.

</dd></dl>

#### `unicode_whitespace`

<dl><dd>

A tuple of `str` objects, representing every whitespace
character defined by Unicode.

Useful as a `separator` argument for **big** functions that accept one,
e.g. [the **big** "multi-" family of functions,](#the-multi--family-of-string-functions)
or the [`lines` and lines modifier functions.](#lines-and-lines-modifier-functions)

Also contains `'\r\n'`.  See the deep-dive section on
[**The Unix, Mac, and DOS line-break conventions**](#the-unix-mac-and-dos-line-break-conventions)
for more.

For more information, please see the
[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
deep-dive.

</dd></dl>

#### `unicode_whitespace_without_crlf`

<dl><dd>

Equivalent to [`unicode_whitespace`](#unicode_whitespace) without `'\r\n'`.

</dd></dl>

#### `whitespace`

<dl><dd>

A tuple of `str` objects, representing every whitespace
character recognized by the Python `str` object.
Identical to [`str_whitespace`.](#str_whitespace)

Useful as a `separator` argument for **big** functions that accept one,
e.g. [the **big** "multi-" family of functions,](#the-multi--family-of-string-functions)
or the [`lines` and lines modifier functions.](#lines-and-lines-modifier-functions)

Also contains `'\r\n'`.  See the deep-dive section on
[**The Unix, Mac, and DOS line-break conventions**](#the-unix-mac-and-dos-line-break-conventions)
for more.

For more information, please see the
[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
deep-dive.

</dd></dl>

#### `whitespace_without_crlf`

<dl><dd>

Equivalent to [`whitespace`](#whitespace) without `'\r\n'`.

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

<dl><dd>

Functions for working with time.  Currently deals specifically
with timestamps.  The time functions in **big** are designed
to make it easy to use best practices.

</dd></dl>

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

## `big.version`

<dl><dd>

Support for version metadata objects.

</dd></dl>

#### `Version(s=None, *, epoch=None, release=None, release_level=None, serial=None, post=None, dev=None, local=None)`

<dl><dd>

Constructs a `Version` object, which represents a version number.

You may define the version one of two ways:

* by passing in a version string to the `s` positional parameter.
  Example: `Version("1.3.24rc37")`
* by passing in keyword-only arguments setting the specific fields of the version.
  Example: `Version(release=(1, 3, 24), release_level="rc", serial=37)`

**big**'s `Version` objects conform to the [PEP 440](https://peps.python.org/pep-0440/)
version scheme, parsing version strings using that PEP's official regular
expression.

`Version` objects support the following features:
* They're immutable once constructed.
* They support the following read-only properties:
    * `epoch`
    * `release`
    * `major` (`release[0]`)
    * `minor` (a safe version of `release[1]`)
    * `micro` (a safe version of `release[2]`)
    * `release_level`
    * `serial`
    * `post`
    * `dev`
    * `local`
* `Version` objects are hashable.
* `Version` objects support ordering and comparison; you can ask if two `Version`
  objects are equal, or if one is less than the other.
* `str()` on a `Version` object returns a normalized version string
  for that version.  `repr()` on a `Version` object returns a string that,
  if `eval`'d, reconstructs that object.
* `Version` objects normalize themselves at initialization time:
    * Leading zeroes on version numbers are stripped.
    * Trailing zeroes in `release` (and trailing `.0` strings in
      the equivalent part of a version string) are stripped.
    * Abbreviations and alternate names for `release_level` are
      normalized.
* Don't tell anybody, but, you can also pass a `sys.version_info`
  object or a `packaging.Version` object into the constructor
  instead of a version string.

When constructing a `Version` by passing in a string `s`, the string must conform to this scheme,
where square brackets denote optional substrings and names in angle brackets represent parameterized
substrings:

```
[<epoch>!]<major>(.<minor_etc>)*[<release_level>[<serial>]][.post<post>][.dev<dev>][+<local>]
```

All fields should be non-negative integers except for:

* `<major>(.<minor_etc>)*` is meant to connote a conventional dotted version number, like `1.2` or `1.5.3.8`.
   This section can contain only numeric digits and periods (`'.'`).
   You may have as few or as many periods as you prefer.  Trailing `.0` entries will be stripped.
* `<release_level>` can only be be one of the following strings:
   * `a`, meaning an *alpha* release,
   * `b`, meaning a *beta* release, or
   * `rc`, meaning a *release candidate*.
   For a final release, skip the `release_level` (and the `serial`).
* `<local>` represents an arbitrary sequence of alphanumeric characters punctuated by periods.

Alternatively, you can construct a `Version` object by passing in these keyword-only arguments:

<dl><dt>

`epoch`

</dt><dd>

A non-negative `int` or `None`.  Represents an "epoch" of version numbers.  A version number
with a higher "epoch" is always a later release, regardless of all other fields.

</dd><dt>

`release`

</dt><dd>

A tuple containing one or more non-negative integers.  Represents the conventional part
of the version number; the version string `1.3.8` would translate to `Version(release=(1, 3, 8))`.

</dd><dt>

`release_level`

</dt><dd>

A `str` or `None`.  If it's a `str`, it must be one of the following strings:

   * `a`, meaning an *alpha* release,
   * `b`, meaning a *beta* release, or
   * `rc`, meaning a *release candidate*.

</dd><dt>

`serial`

</dt><dd>

A non-negative `int` or `None`.  Represents how many releases there have been at this `release_level`.
(The name is taken from [Python's `sys.version_info`](https://docs.python.org/3/library/sys.html#sys.version_info).)

</dd><dt>

`post`

</dt><dd>

A non-negative `int` or `None`.  Represents "post-releases", extremely minor releases made after a release:

```
Version(release=(1, 3, 5)) < Version(release=(1, 3, 5), post=1)
```

</dd><dt>

`dev`

</dt><dd>

A non-negative `int` or `None`.  Represents an under-development release.  Higher `dev` numbers represent
later releases, but any release where `dev` is not `None` comes *before* any release where `dev` is `None`.
In other words:

```
Version(release=(1, 3, 5), dev=34) < Version(release=(1, 3, 5), dev=35)
Version(release=(1, 3, 5), dev=35) < Version(release=(1, 3, 5))
```

</dd><dt>

`local`

</dt><dd>

A `tuple` of one or more `str` objects containing only one or more
alphanumeric characters
or `None`.  Represents a purely local version number,
allowing for minor build and patch differences
but with no API or ABI changes.


</dd></dl>

#### `Version.format(s)`

<dl><dd>

Returns a formatted version of `s`, substituting attributes from
`self` into `s` using `str.format_map`.

For example,

```Python
    Version("1.3.5").format('{major}.{minor}')
```

returns the string `'1.3'`.


</dd></dl>


</dd></dl>


# Topic deep-dives

## The `multi-` family of string functions

<dl><dd>

This family of string functions was inspired by Python's `str.split`,
`str.rsplit`, and `str.splitlines` methods.  These string splitting
methods are well-designed and often do what you want.  But they're
surprisingly narrow and opinionated.  What if your use case doesn't
map neatly to one of these functions?  `str.split` supports two
*very specific* modes of operation--unless you want to split your
string in *exactly* one of those two modes, you probably can't use
`str.split` to solve your problem.

So what *can* you use?  There's
[`re.split`,](https://docs.python.org/3/library/re.html#re.split)
but that can be  hard to use.<sup id=back_to_re_strip><a href=#re_strip_footnote>1</a></sup>
Regular expressions can be so hard to get right, and the
semantics of `re.split` are subtly different from the usual
string splitting functions.  Not to mention, it doesn't support
reverse!

Now there's a new answer:
[`multisplit`.](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
The goal of `multisplit` is to be the be-all end-all string splitting function.
It's designed to supercede *every* mode of operation provided by
`str.split`, `str.rsplit`, and `str.splitlines`, and it
can even replace `str.partition` and `str.rpartition` too.
`multisplit` does it all!

The downside of [`multisplit`'s](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
awesome flexibility is that it can be hard to use... after all,
it takes *five* keyword-only parameters.  However, these parameters
and their defaults are designed to be easy to remember.

The best way to cope with
[`multisplit`'s](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
complexity is to use it as a building block for your own
text splitting functions.  For example, **big** uses
[`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
to implement
[`multipartition`,](#multipartitions-separators-count1--reverseFalse-separateTrue)
[`normalize_whitespace`,](#normalize_whitespaces-separatorsNone-replacementnone)
[`lines`,](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs)
and several other functions.

### Using `multisplit`

To use
[`multisplit`,](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
pass in the string you want to split, the separators you
want to split on, and tweak its behavior with its five
keyword arguments.  It returns an iterator that yields
string segments from the original string in your preferred
format.  The separator list is optional; if you don't
pass one in, it defaults to an iterable of whitespace separators
(either
[`big.whitespace`](#whitespace)
or
[`big.ascii_whitespace`,](#whitespace)
as appropriate).

The cornerstone of [`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
is the `separators` argument.
This is an iterable of strings, of the same type (`str` or `bytes`)
as the string you want to split (`s`).  `multisplit` will split
the string at *each* non-overlapping instance of any string
specified in `separators`.

[`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
lets you fine-tune its behavior via five keyword-only
parameters:

* `keep` lets you include the separator strings in the output,
  in a number of different formats.
* `separate` lets you specify whether adjacent separator strings
  should be grouped together (like `str.split` operating on
  whitespace) or regarded as separate (like `str.split` when
  you pass in an explicit separator).
* `strip` lets you strip separator strings from the beginning,
  end, or both ends of the string you're splitting.  It also
  supports a special *progressive* mode that duplicates the
  behavior of `str.split` when you use `None` as the separator.
* `maxsplit` lets you specify the maximum number of times to
  split the string, exactly like the `maxsplit` argument to `str.split`.
* `reverse` makes `multisplit` behave like `str.rsplit`,
  starting at the end of the string and working backwards.
  (This only changes the behavior of `multisplit` if you use
  `maxsplit`, or if your string contains overlapping separators.)

To make it slightly easier to remember, all these keyword-only
parameters default to a false value.  (Well, technically,
`maxsplit` defaults to the special value `-1`, for compatibility
with `str.split`.  But that's its special "don't do anything"
magic value.  All the *other* keyword-only parameters default
to `False`.)

[`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
also inspired [`multistrip`](#multistrips-separators-leftTrue-rightTrue)
 and [`multipartition`,](#multipartitions-separators-count1--reverseFalse-separateTrue)
which also take this same `separators` arguments.  There are also
other **big** functions that take a `separators` argument,
for example `comment_markers` for
[`lines_filter_line_comment_lines`](#lines_filter_line_comment_linesli-comment_markers).)

### Demonstrations of each `multisplit` keyword-only parameter

To give you a sense of how the five keyword-only parameters changes the behavior of
[`multisplit`,](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
here's a breakdown of each of these parameters with examples.

#### `maxsplit`

<dl><dd>

`maxsplit` specifies the maximum number of times the string should be split.
It behaves the same as the `maxsplit` parameter to `str.split`.

The default value of `-1` means "split as many times as you can".  In our
example here, the string can be split a maximum of three times.  Therefore,
specifying a `maxsplit` of `-1` is equivalent to specifying a `maxsplit` of
`2` or greater:

```Python
    >>> list(big.multisplit('apple^banana_cookie', ('_', '^'))) # "maxsplit" defaults to -1
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('apple^banana_cookie', ('_', '^'), maxsplit=0))
    ['appleXbananaYcookie']
    >>> list(big.multisplit('apple^banana_cookie', ('_', '^'), maxsplit=1))
    ['apple', 'bananaYcookie']
    >>> list(big.multisplit('apple^banana_cookie', ('_', '^'), maxsplit=2))
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('apple^banana_cookie', ('_', '^'), maxsplit=3))
    ['apple', 'banana', 'cookie']
```

`maxsplit` has interactions with `reverse` and `strip`.  For more
information, see the documentation regarding those parameters below.

</dd></dl>

#### `keep`

<dl><dd>

`keep` indicates whether or not `multisplit` should preserve the separator
strings in the strings it yields.  It supports four values: false, true,
and the special values `ALTERNATING` and `AS_PAIRS`.

When `keep` is false, `multisplit` throws away the separator strings;
they won't appear in the output.

```Python
    >>> list(big.multisplit('apple#banana-cookie', ('#', '-'))) # "keep" defaults to False
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('apple-banana#cookie', ('#', '-'), keep=False))
    ['apple', 'banana', 'cookie']
```

When `keep` is true, `multisplit` keeps the separators, appending them to
the end of the separated string:

```Python
    >>> list(big.multisplit('apple$banana~cookie', ('$', '~'), keep=True))
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

Note that `ALTERNATING` always emits an odd number of strings, and the first and
last strings yielded are always non-separator strings.  Like `str.split`,
if the string you're splitting starts or ends with a separator string,
`multisplit` will emit an empty string at the beginning or end, to preserve
the "always begin and end with non-separator string" invariant:

```Python
    >>> list(big.multisplit('1a1z1', ('1',), keep=big.ALTERNATING))
    ['', '1', 'a', '1', 'z', '1', '']
```

Finally, when `keep` is `AS_PAIRS`, `multisplit` keeps the separators as separate
strings.  But it doesn't yield bare strings; instead, it yields 2-tuples of strings.
Every 2-tuple contains a non-separator string followed by a separator string.

If the original string starts with a separator, the first 2-tuple will contain
an empty non-separator string and the separator:

```Python
    >>> list(big.multisplit('^apple-banana^cookie', ('-', '^'), keep=big.AS_PAIRS))
    [('', '^'), ('apple', '-'), ('banana', '^'), ('cookie', '')]
```

The last 2-tuple will *always* contain an empty separator string:

```Python
    >>> list(big.multisplit('apple*banana+cookie', ('*', '+'), keep=big.AS_PAIRS))
    [('apple', '*'), ('banana', '+'), ('cookie', '')]
    >>> list(big.multisplit('apple*banana+cookie***', ('*', '+'), keep=big.AS_PAIRS, strip=True))
    [('apple', '*'), ('banana', '+'), ('cookie', '')]
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

</dd></dl>

#### `separate`

<dl><dd>

`separate` indicates whether multisplit should consider adjacent
separator strings in `s` as one separator or as multiple separators
each separated by a zero-length string.  It can be either false or
true.

```Python
    >>> list(big.multisplit('apple=?banana?=?cookie', ('=', '?'))) # separate defaults to False
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('apple=?banana?=?cookie', ('=', '?'), separate=False))
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('apple=?banana?=?cookie', ('=', '?'), separate=True))
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

</dd></dl>

#### `strip`

<dl><dd>

`strip` indicates whether multisplit should strip separators from
the beginning and/or end of `s`.  It supports five values:
false, true, `big.LEFT`, `big.RIGHT`, and `big.PROGRESSIVE`.

By default, `strip` is false, which means it doesn't strip any
leading or trailing separators:

```Python
    >>> list(big.multisplit('%|apple%banana|cookie|%|', ('%', '|'))) # strip defaults to False
    ['', 'apple', 'banana', 'cookie', '']
```

Setting `strip` to true strips both leading and trailing separators:

```Python
    >>> list(big.multisplit('%|apple%banana|cookie|%|', ('%', '|'), strip=True))
    ['apple', 'banana', 'cookie']
```

`big.LEFT` and `big.RIGHT` tell `multistrip` to only strip on that
side of the string:

```Python
    >>> list(big.multisplit('.?apple.banana?cookie.?.', ('.', '?'), strip=big.LEFT))
    ['apple', 'banana', 'cookie', '']
    >>> list(big.multisplit('.?apple.banana?cookie.?.', ('.', '?'), strip=big.RIGHT))
    ['', 'apple', 'banana', 'cookie']
```

`big.PROGRESSIVE` duplicates a specific behavior of `str.split` when using
`maxsplit`.  It always strips on the left, but it only strips on the right
if the string is completely split.  If `maxsplit` is reached before the entire
string is split, and `strip` is `big.PROGRESSIVE`, `multisplit` *won't* strip
the right side of the string.  Note in this example how the trailing separator
`Y` isn't stripped from the input string when `maxsplit` is less than `3`.

```Python
    >>> list(big.multisplit('^apple^banana_cookie_', ('^', '_'), strip=big.PROGRESSIVE))
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('^apple^banana_cookie_', ('^', '_'), maxsplit=0, strip=big.PROGRESSIVE))
    ['apple^banana_cookie_']
    >>> list(big.multisplit('^apple^banana_cookie_', ('^', '_'), maxsplit=1, strip=big.PROGRESSIVE))
    ['apple', 'banana_cookie_']
    >>> list(big.multisplit('^apple^banana_cookie_', ('^', '_'), maxsplit=2, strip=big.PROGRESSIVE))
    ['apple', 'banana', 'cookie_']
    >>> list(big.multisplit('^apple^banana_cookie_', ('^', '_'), maxsplit=3, strip=big.PROGRESSIVE))
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('^apple^banana_cookie_', ('^', '_'), maxsplit=4, strip=big.PROGRESSIVE))
    ['apple', 'banana', 'cookie']
```

</dd></dl>

#### `reverse`

<dl><dd>

`reverse` specifies where `multisplit` starts parsing the string--from
the beginning, or the end--and in what direction it moves when parsing
the string--towards the end, or towards the beginning_  It only supports
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
    >>> list(big.multisplit('apple-banana|cookie', ('-', '|'), reverse=True)) # maxsplit defaults to -1
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('apple-banana|cookie', ('-', '|'), maxsplit=0, reverse=True))
    ['apple-banana|cookie']
    >>> list(big.multisplit('apple-banana|cookie', ('-', '|'), maxsplit=1, reverse=True))
    ['apple-banana', 'cookie']
    >>> list(big.multisplit('apple-banana|cookie', ('-', '|'), maxsplit=2, reverse=True))
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('apple-banana|cookie', ('-', '|'), maxsplit=3, reverse=True))
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
    >>> list(big.multisplit('appleXYZbananaXYZcookie', ('XY', 'YZ'))) # reverse defaults to False
    ['apple', 'Zbanana', 'Zcookie']
    >>> list(big.multisplit('appleXYZbananaXYZcookie', ('XY', 'YZ'), reverse=True))
    ['appleX', 'bananaX', 'cookie']
```
</dd></dl>

### Reimplementing library functions using `multisplit`

Here are some examples of how you could use
[`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
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
    linebreaks = big.ascii_linebreaks if isinstance(s, bytes) else big.linebreaks
    l = list(big.multisplit(s, linebreaks,
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
[`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse),
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
[`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
lets you duplicate this behavior.  When you want
[`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
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
[`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
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

In short, it's similar to the `str.split` situation.
When called with `keep=AS_PAIRS`,
[`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
guarantees that the final tuple will contain an empty separator string.
If the string you're splitting ends with a separator, it *must* emit
the empty non-separator string, followed by the empty separator string.

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

[`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
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

If you [`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
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
[`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
to also strip the string, you'll get back a single empty string:

```Python
>>> list(big.multisplit('     ', strip=True))
['']
```

And
[`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
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

## Whitespace and line-breaking characters in Python and big

<dl><dd>

### Overview

Several functions in **big** take a `separators`
argument, an iterable of separator strings.
Examples of these functions include
[`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs)
and
[`multisplit`.](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
Although you can use any iterable of strings
you like, most often you'll be separating on some
form of whitespace.  But what, exactly, *is*
whitespace?  There's more to this topic than you
might suspect.

The good news is, you can almost certainly ignore all the
complexity.  These days the only whitespace characters you're
likely to encounter are spaces, tabs, newlines, and maybe
carriage returns.  Python and **big** handle all those easily.

With respect to **big** and these `separators` arguments,
**big** provides four values designed for use as `separators`.
All four of these are tuples containing whitespace characters:

* When working with `str` objects, you'll want to use either
  [`big.whitespace`](#whitespace) or [`big.linebreaks`.](#linebreaks)
  `big.whitespace` contains all the whitespace characters,
  `big.linebreaks` contains just the line-breaking
  whitespace characters.
* **big** also has equivalents for working with `bytes`
  objects: [`bytes_whitespace`](#bytes_whitespace)
  and [`bytes_linebreaks`,](#bytes_linebreaks)
  respectively.

Apart from exceptionally rare occasions, these are all you'll ever need.
And if that's all you need, you can stop reading this
section now.

But what about those exceptionally rare occasions?
You'll be pleased to know **big** handles them too.
The rest of this section is
a deep dive into these rare occasions.


### Python

Here's the list of all characters recognized by
Python `str` objects as whitespace characters:

    # char    decimal   hex      name
    ##########################################
    '\t'    , #     9 - 0x0009 - tab
    '\n'    , #    10 - 0x000a - newline
    '\v'    , #    11 - 0x000b - vertical tab
    '\f'    , #    12 - 0x000c - form feed
    '\r'    , #    13 - 0x000d - carriage return
    '\x1c'  , #    28 - 0x001c - file separator
    '\x1d'  , #    29 - 0x001d - group separator
    '\x1e'  , #    30 - 0x001e - record separator
    '\x1f'  , #    31 - 0x001f - unit separator
    ' '     , #    32 - 0x0020 - space
    '\x85'  , #   133 - 0x0085 - next line
    '\xa0'  , #   160 - 0x00a0 - non-breaking space
    '\u1680', #  5760 - 0x1680 - ogham space mark
    '\u2000', #  8192 - 0x2000 - en quad
    '\u2001', #  8193 - 0x2001 - em quad
    '\u2002', #  8194 - 0x2002 - en space
    '\u2003', #  8195 - 0x2003 - em space
    '\u2004', #  8196 - 0x2004 - three-per-em space
    '\u2005', #  8197 - 0x2005 - four-per-em space
    '\u2006', #  8198 - 0x2006 - six-per-em space
    '\u2007', #  8199 - 0x2007 - figure space
    '\u2008', #  8200 - 0x2008 - punctuation space
    '\u2009', #  8201 - 0x2009 - thin space
    '\u200a', #  8202 - 0x200a - hair space
    '\u2028', #  8232 - 0x2028 - line separator
    '\u2029', #  8233 - 0x2029 - paragraph separator
    '\u202f', #  8239 - 0x202f - narrow no-break space
    '\u205f', #  8287 - 0x205f - medium mathematical space
    '\u3000', # 12288 - 0x3000 - ideographic space

This list was derived by iterating over every character
defined in Unicode, and testing to see if the `split()`
method on a Python `str` object splits at that character.

The first surprise: this *isn't* the same as the list of
[all characters defined by Unicode as whitespace.](https://en.wikipedia.org/wiki/Whitespace_character#Unicode)
It's *almost* the same list, except Python adds four extra
characters: `'\x1c'`,  `'\x1d'`,  `'\x1e'`, and `'\x1f'`,
which respectively are called "file separator", "group separator",
"record separator", and "unit separator".
I'll refer to these as "the four ASCII separator characters".

These characters were defined as part of [the original ASCII
standard,](https://en.wikipedia.org/wiki/ASCII) way back in 1963.
As their names suggest, they were intended to be used as separator
characters for data, the same way
[Ctrl-Z was used to indicate end-of-file in the CPM and earliest
FAT filesystems.](https://en.wikipedia.org/wiki/End-of-file#EOF_character)
But the four ASCII separator characters were rarely used
even back in the day.  Today they're practically unheard of.

As a rule, printing these characters to the screen generally
doesn't do anything--they don't move the cursor, and the
screen doesn't change.
So their behavior is a bit mysterious.  A lot of people (including
early Python programmers it seems!) thought that meant they're
whitespace.  This seems like an odd conclusion to me.  After all,
all the other whitespace characters move the cursor, either right
or down or both; these don't move the cursor at all.

[The Unicode standard](https://www.unicode.org/Public/14.0.0/)
is unambiguous: these characters are *not whitespace.*  And yet Python's
"Unicode object" behaves as if they are.  So I'd say this is a bug;
Python's Unicode object should implement what the Unicode standard says.

> It seems that the C library used by GCC and clang on my workstation
> agree.  I wrote a quick C program to print out what characters
> are and aren't whitespace, according to the C function isspace().
> It seems the C library agrees with Unicode: it doesn't consider
> the four ASCII separator characters to be whitespace.
>
> Here's the program, in case you want to try it yourself.
>
>      #include <stdio.h>
>      #include <ctype.h>
>
>      int main(int c, char *a[]) {
>              int i;
>              printf("\nisspace table.\nAdd the row and column numbers together (in hex).\n\n");
>              printf("     | 0 1 2 3 4 5 6 7 8 9 a b c d e f\n");
>              printf("-----+--------------------------------\n");
>              for (i = 0 ; i < 256 ; i++) {
>                      char *message = isspace(i) ? "Y" : "n";
>                      if ((i % 16) == 0)
>                              printf("0x%02x |", i);
>                      printf(" %s", message);
>                      if ((i % 16) == 15)
>                              printf("\n");
>              }
>              return 0;
>      }
>
> Here's its output on my workstation:
>
>     isspace table.
>     Add the row and column numbers together (in hex).
>
>          | 0 1 2 3 4 5 6 7 8 9 a b c d e f
>     -----+--------------------------------
>     0x00 | n n n n n n n n n Y Y Y Y Y n n
>     0x10 | n n n n n n n n n n n n n n n n
>     0x20 | Y n n n n n n n n n n n n n n n
>     0x30 | n n n n n n n n n n n n n n n n
>     0x40 | n n n n n n n n n n n n n n n n
>     0x50 | n n n n n n n n n n n n n n n n
>     0x60 | n n n n n n n n n n n n n n n n
>     0x70 | n n n n n n n n n n n n n n n n
>     0x80 | n n n n n n n n n n n n n n n n
>     0x90 | n n n n n n n n n n n n n n n n
>     0xa0 | n n n n n n n n n n n n n n n n
>     0xb0 | n n n n n n n n n n n n n n n n
>     0xc0 | n n n n n n n n n n n n n n n n
>     0xd0 | n n n n n n n n n n n n n n n n
>     0xe0 | n n n n n n n n n n n n n n n n
>     0xf0 | n n n n n n n n n n n n n n n n
>
> 0x1c through 0x1f are represented by the last four `n` characters on
> the second line, the `0x10` line.  The fact that they're `n`s tells you
> that this C standard library doesn't consider those characters to be
> whitespace.


Like many bugs, this one has lingered for a long time.  The behavior
is present in Python 2, there's
[a ten-year-old issue on the Python issue tracker about this,](https://github.com/python/cpython/issues/62436)
 and it's not making progress.

The second surprise has to do with `bytes` objects.
Of course, `bytes` objects represent binary data, and don't
necessarily represent characters.  Even if they do, they don't
have any encoding associated with them.  However, for
convenience--and backwards-compatibility with Python 2--Python's
`bytes` objects support several method calls that treat the data
as if it were "ASCII-compatible".

The surprise: These methods on Python `bytes` objects recognize
a *different* set of whitespace characters.  Here's the list of
all bytes recognized by Python `bytes` objects as whitespace:

    # char  decimal  hex    name
    #######################################
    '\t'    , #  9 - 0x09 - tab
    '\n'    , # 10 - 0x0a - newline
    '\v'    , # 11 - 0x0b - vertical tab
    '\f'    , # 12 - 0x0c - form feed
    '\r'    , # 13 - 0x0d - carriage return
    ' '     , # 32 - 0x20 - space

This list was derived by iterating over every possible
byte value, and testing to see if the `split()` method
on a Python `bytes` object splits at that byte.

The good news is, this list is the same as ASCII's list,
and it agrees with Unicode.
In fact this list is quite familiar to C programmers;
it's the same whitespace characters recognized by the
standard C function
[`isspace()` (in `ctypes.h`).](https://www.oreilly.com/library/view/c-in-a/0596006977/re129.html)
Python has used this function to decide which characters
are and aren't whitespace in 8-bit strings since its very
beginning.

Notice that this list *doesn't* contain the
four ASCII separator characters.  That these two
types in Python don't agree only enhances the mystery.

### Line-breaking characters

The situation is slightly worse with line-breaking
characters. Line-breaking characters are a subset of
whitespace characters; they're whitespace characters that
always move the cursor down.  And, as with whitespace
generally, Python `str` objects don't agree with Unicode
about what is and is not a line-breaking character,
and Python `bytes` objects don't agree with either of those.

Here's the list of all Unicode characters recognized by
Python `str` objects as line-breaking characters:

    # char    decimal   hex      name
    ##########################################
    '\n'    , #   10 0x000a - newline
    '\v'    , #   11 0x000b - vertical tab
    '\f'    , #   12 0x000c - form feed
    '\r'    , #   13 0x000d - carriage return
    '\x1c'  , #   28 0x001c - file separator
    '\x1d'  , #   29 0x001d - group separator
    '\x1e'  , #   30 0x001e - record separator
    '\x85'  , #  133 0x0085 - next line
    '\u2028', # 8232 0x2028 - line separator
    '\u2029', # 8233 0x2029 - paragraph separator

This list was derived by iterating over every character
defined in Unicode, and testing to see if the `splitlines()`
method on a Python `str` object splits at that character.

Again, this is different from [the list of characters
defined as line-breaking whitespace in Unicode.](https://en.wikipedia.org/wiki/Newline#Unicode)
And again it's because Python defines some of the four ASCII separator
characters as line-breaking characters.  In this case
it's only the first three; Python doesn't consider
the fourth, "unit separator", as a line-breaking character.
(I don't know why Python draws this distinction...
but then again, I don't know why it considers the
first three to be line-breaking.  It's *all* a mystery to me.)

Here's the list of all characters recognized by
Python `bytes` objects as line-breaking characters:

    # char  decimal hex      name
    #######################################
    '\n'    , #  10 0x000a - newline
    '\r'    , #  13 0x000d - carriage return

This list was derived by iterating over every possible
byte, and testing to see if the `splitlines()`
method on a Python `bytes` object splits at that byte.

It's here we find our final unpleasant surprise:
the methods on Python `bytes` objects *don't* consider
`'\v'` (vertical tab)
and
`'\f'` (form feed)
to be line-break characters.  I assert this is also a bug.
These are well understood to be line-breaking characters;
"vertical tab" is like a "tab", except it moves the cursor
down instead of to the right.  And "form feed" moves the
cursor to the top left of the next "page", which requires
advancing at least one line.

### How **big** handles this situation

To be crystal clear: the odds that any of this will cause
a problem for you are *extremely* low.  In order for it
to make a difference:

* you'd have to encounter text using one of these six characters
  where Python disagrees with Unicode and ASCII, and
* you'd have to process the input based on some definition
  of whitespace, and
* it would have to produce different results than you might
  have other wise expected, *and*
* this difference in results would have to be important.

It seems extremely unlikely that all of these will be true for you.

In case this *does* affect you, **big** has
a complete set of predefined whitespace tuples that will
handle any of these situations.
**big** defines a total of *ten* tuples, sorted into
five categories.

In every category there are two values: one that contains
`whitespace`, the other contains `linebreaks`.  The
`whitespace` tuple contains all the possible values of
whitespace--characters that move the cursor either
horizontally, or vertically, or both, but don't
print anything visible to the screen.  The `linebreaks`
tuple contains the subset of whitespace characters that
move the cursor vertically.

The most important two values start with `str_`:
[`str_whitespace`](#str_whitespace)
and
[`str_linebreaks`.](#str_linebreaks)
These contain all the whitespace characters
recognized by the Python `str` object.

Next are two values that start with `unicode_`:
[`unicode_whitespace`](#unicode_whitespace)
and
[`unicode_linebreaks`.](#unicode_linebreaks)
These contain all the whitespace characters
defined in the Unicode standard.  They're the
same as the `str_` tuples except we remove the
four ASCII separator characters.

Third, two values that start with `ascii_`:
[`ascii_whitespace`](#ascii_whitespace)
and
[`ascii_linebreaks`.](#ascii_linebreaks)
These contain all the whitespace characters
defined in ASCII.  (Note that these contain
`str` objects, not `bytes` objects.)  They're
the same as the `unicode_` tuples, except we
throw away all characters with a code point
higher than 127.

Fourth, two values that start with `bytes_`:
[`bytes_whitespace`](#bytes_whitespace)
and
[`bytes_linebreaks`.](#bytes_linebreaks)
These contain all the whitespace characters
recognized by the Python `bytes` object.
These tuples contain `bytes` objects, encoded
using the `ascii` encoding.  The list of
characters is distinct from the other sets
of tuples, and was derived as described above.

Finally we have the two tuples that lack a prefix:
[`whitespace`](#whitespace)
and
[`linebreaks`.](#linebreaks)
These are the tuples you should use most of the time,
and several **big** functions use them as default values.
These are simply copies of `str_whitespace` and
`str_linebreaks` respectively.

(**big** actually defines an *additional* ten tuples,
as discussed in the very next section.)

### The Unix, Mac, and DOS line-break conventions

Historically, different platforms used different
ASCII characters--or sequences of ASCII characters--to
represent "go to the next line" in text files.  Here are the
most popular conventions:

    \n    - UNIX, Amiga, macOS 10+
    \r    - macOS 9 and earlier, many 8-bit computers
    \r\n  - Windows, DOS

(There are a couple more conventions, and a lot more history,
in the [Wikipedia article on newlines.)](https://en.wikipedia.org/wiki/Newline#Representation)

Handling these differing conventions was a stumbling block
for a long time--both for computer programs, and in the
daily lives of computer users.  Python went through several
iterations on how to handle this, eventually settling on
the ["universal newlines"](https://peps.python.org/pep-0278/)
support added in Python 2.3.
These days the world seems to be converging on the UNIX
standard `'\n'`; Windows supports it, and it's the default
on every other modern platform.
So in practice you probably don't have end-of-line conversion
problems, either.

But just in case, **big** has one more trick.  All of
the tuples defined in the previous section--from `whitespace`
to `ascii_linebreaks`--also contain this string:

    '\r\n'

(The two `bytes_` tuples contain the `bytes` equivalent,
`b'\r\n`.)

This addition means that, when you use one of these tuples
with one of the **big** functions that take separators,
it'll split on `\r\n` as if it was one character.  This
means that **big** itself should automatically handle
the DOS and Windows end-of-line character sequence, in
case one happens to creep into your data.

If you don't want this behavior, just add the suffix
`_without_crlf` to the end of any of the ten tuples,
e.g. `whitespace_without_crlf`, `bytes_linebreaks_without_crlf`.

### Whitespace and line-breaking characters for other platforms

What if you need to split text by whitespace, or by lines,
but that text is in `bytes` format with an unusual encoding?
**big** makes that easy too.  If one of the builtin tuples
won't work for you, you can can make your own tuple from scratch,
or modify an existing tuple to meet your needs.

For example, let's say you need to split a document by
whitespace, and the document is encoded in [code page 850,
aka "latin-1".](https://en.wikipedia.org/wiki/Code_page_850)
Normally the easiest thing would be to decode it a `str` object
using the `'latin-1'` text codec, then operate on it normally.
But you might have reasons why you don't want to decode it--maybe
the document is damaged and doesn't decode properly, and it's
easier to work with the encoded bytes than to fix it.  If you
want to process the text with a **big** function that accepts a
`separator` argument, you could make your own custom tuple
of "latin-1" whitespace characters.  "latin-1" has the same
whitespace characters as ASCII, but adds one more, value 255,
which is not line-breaking.  So it's easy to make the appropriate
tuples yourself:

    latin_1_whitespace = big.bytes_whitespace + (b'\xff',)
    latin_1_linebreaks = big.bytes_linebreaks

What if you want to process a `bytes` object containing
UTF-8?  That's easy too.  Just convert one of the existing
tuples containing `str` objects using
[`big.encode_strings`.](#encode_stringso--encodingascii)
For example, to split a UTF-8 encoded bytes object `b` using
the Unicode line-breaking characters, you could call:

    multisplit(b, encode_strings(unicode_linebreaks, encoding='utf-8'))

Note that this technique probably won't work correctly for most other
multibyte encodings, for example [UTF-16.](https://en.wikipedia.org/wiki/UTF-16)
For these encodings, you should decode to `str` before processing.

Why?  It's because `multisplit` could find matches in multibyte
sequences *straddling* characters.  Consider this example:

```Python
>>> haystack = '\u0101\u0102'
>>> needle = '\u0201'
>>> needle in haystack
False
>>>
>>> encoded_haystack = haystack.encode('utf-16-le')
>>> encoded_needle = needle.encode('utf-16-le')
>>> encoded_needle in encoded_haystack
True
```

The character `'\u0201'` doesn't appear in the original string,
but the *encoded* version appears in the *encoded* string,
as the *second* byte of the *first* character and the *first*
byte of the *second* character:

```Python
>>> encoded_haystack
b'\x01\x01\x02\x01'
>>> encoded_needle
b'\x01\x02'
```

</dd></dl>


## `lines` and lines modifier functions

<dl><dd>

[`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs)
is a function that makes it easy to write well-behaved, feature-rich text parsers.


[`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs) itself
iterates over a string, returning an iterator that yields individual lines
split from that string.  The iterator yields a 2-tuple:
```
(LinesInfo, line)
```
The `LinesInfo` object provides the line number and starting column number
for each line.  This makes it easy for your parser to provide
line and column information for error messages.

This iterator is designed to be modified by "lines modifier"
functions.  These are functions that consume a lines
iterator and re-yield the values, possibly modifying or
discarding them along the way.  For example, passing
a [`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs) iterator into `lines_filter_empty_lines` results
in an iterator that skips over the empty lines.
All the lines modifier functions that ship with **big**
start with the string `lines_`.

Most lines modifier function names belong to a category,
encoded as the second word in the function name
(immediately after `lines_`).  Some examples:

* `lines_filter_` functions conditionally remove
  lines from the output.  For example, `lines_filter_empty_lines`
  will only yield a line if it isn't empty.
* `lines_strip_` functions may remove one or
  more substrings from the line.  For example,
  [`lines_strip_indent`](#lines_strip_indentli)
  strips the leading whitespace from a line before yielding
  it.  (Whenever a lines modifier removes leading text from a line,
  it will add a `leading` field to the accompanying
  [`LineInfo`](#lineinfolines-line-line_number-column_number--leadingnone-trailingnone-endnone-indent0-matchnone-kwargs)
  object containing the removed substring, and will also update the
  `column_number` of the line to reflect the new starting column.)
* `lines_convert_` functions means this lines modifier may change one
  or more substrings in the line.  For example,
  `lines_convert_tabs_to_spaces` changes tab characters
  to space characters in any lines it processes.

(**big** isn't strictly consistent about these category names though.
For example,
[`lines_containing`](#lines_containingli-s--invertfalse)
and
[`lines_grep`](#lines_grepli-pattern--invertfalse-flags0)
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
which is probably not what you want.  Ordering is important!

It's probably clearer to constructed nested lines modifiers
this way:

```Python
     with open("textfile.txt", "rt") as f:
         li = lines(f.read())
         li = big.lines_filter_empty_lines(li)
         li = big.lines_rstrip(li)
         for info, line in li:
           ...
```

This is much easier to read, particularly when one or
more lines modifiers take additional arguments.

Of course, you can write your own lines modifier functions.
Simply accept a lines iterator as an argument, iterate over
it, and yield each line info and line--modifying them
(or not yielding them!) as you see fit.  You could
even write your own lines iterator, a replacement for
[`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs),
if you need functionality
[`lines`](#liness-separatorsnone--line_number1-column_number1-tab_width8-kwargs) doesn't provide.

Note that if you write your own lines modifier function,
and it removes text from the beginning the line, you must
update `column_number` in the
[`LineInfo`](#lineinfolines-line-line_number-column_number--leadingnone-trailingnone-endnone-indent0-matchnone-kwargs)
object manually--it
doesn't happen automatically.  The easiest way to handle this
is also the best way: whenever clipping text from the beginning
or end of the line, use the
[`clip_leading`](#lineinfoclip_leadingline-s)
and
[`clip_trailing`](#lineinfoclip_trailingline-s)
methods on the `LineInfo` object.

Speaking of best practices for lines modifier functions,
it's also best practice to *modify* the *existing*
`LineInfo` object that was yielded to you, rather than
throwing it away, creating a new one, and yielding that
instead.  Previous lines modifier iterators may have added
fields to the
[`LineInfo`](#lineinfolines-line-line_number-column_number--leadingnone-trailingnone-endnone-indent0-matchnone-kwargs)
that you'd to preserve.

### leading + line + trailing + end

Generally speaking,
[`LineInfo`](#lineinfolines-line-line_number-column_number--leadingnone-trailingnone-endnone-indent0-matchnone-kwargs)
objects obey an invariant.
For any `(info, line)` pair yielded by `lines` or a lines
modifier:

    info.leading + line + info.trailing + info.end == info.line

That is, you can recreate the original line by concatenating
the "leading" string, the modified line, the "trailing" string,
and the "end" string.

Of course, this won't be true if you use lines modifiers that
replace characters in the line.  For example, `lines_convert_tabs_to_spaces`
replaces tab characters with one or more space characters.
If the original line contains tabs, obviously the above invariant
will no longer hold true.

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
attempting to use that view raises a `RuntimeError`.  (I'll define what I mean
by view "coherence" in the next subsection.)

This implementation also fixes some minor warts with the existing API:

- In Python's implementation, `static_order` and `get_ready`/`done` are mutually exclusive.  If you ever call
  `get_ready` on a graph,  you can never call `static_order`, and vice-versa.  The implementaiton in **big**
  doesn't have this restriction, because its implementation of `static_order` creates and uses a new view object
  every time it's called.
- In Python's implementation, you can only iterate over the graph once, or call `static_order` once.
  The implementation in **big** solves this in several ways: it allows you to create as many views as you
  want, and you can call the new `reset` method on a view to reset it to its initial state.

#### View coherence

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

First this creates a graph `g` with a classic "diamond"
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

#### next version

*under development, no release date yet*

<dl><dd>

* `PushbackIterator` no longer evaluates the iterator you pass in
  in a boolean context.  (All we needed to do was compare it to `None`,
  so now that's all we do.)

</dd></dl>

#### 0.12.4

*2024/11/15*

<dl><dd>

* New function in the `text` module: `format_map`.
  This works like Python's `str.format_map` method,
  except it allows nested curly-braces.  Example:
  `big.format_map("The {extension} file is {{extension} size} bytes.", {'extension': 'mp3', 'mp3 size': 8555})`
* New method: `Version.format` is like `strftime` but for `Version` objects.
  You pass in a format string with `Version` attributes in curly braces
  and it formats the string with values from that `Version` object.
* The `Version` constructor now accepts a `packaging.Version` object
  as an initializer.  Embrace and extend!
* `lines` now takes two new arguments:
    * `clip_linebreaks`, default is true.
      If true, it clips the linebreaks off the lines before yielding them,
      otherwise it doesn't.  (Either way, the linebreaks are still stored
      in `info.end`.)
    * `source`, default is an empty string.
      `source` should represent the source of the line in a
      meaninful way to the user.  It's stored in the `LinesInfo`
      objects yielded by `lines`, and should be incorporated into
      error messages.
* `LineInfo.clip_leading` and `LineInfo.clip_trailing` now automatically
  detect if you've clipped the entire line, and if so move all clipped
  text to `info.trailing` (and adjust the `column_number` accordingly).
* `LineInfo.clip_leading` and `LineInfo.clip_trailing`: Minor performance
  upgrade. Previously, if the user passed in the string to clip, the
  two functions would throw it away then recreate it.  Now they just use
  the passed-in string.
* Changed the word "newline" to "linebreak" everywhere.  They mean the
  same thing, but the Unicode standard consistently uses the word
  "linebreak"; I assume the boffins on the committee thought about this
  a lot and argued and finally settled on this word for good
  (if unpublished?) reasons.
* Add explicit support (and CI coverage & testing) for Python 3.13.
  (big didn't need any changes, it was already 100% compatible with 3.13.)

<p><font size=1>p.s. 56</font></p>

</dd></dl>

#### 0.12.3

*2024/09/17*

<dl><dd>

Optimized
[`split_delimiters`](#split_delimiterss-delimiters--state).
The new version uses a much more efficient internal representation
of how to react to the various delimiters when processing the text.
Perfunctory `timeit` experiments suggest this new `split_delimiters`
is maybe 5-6% faster than it was in 12.2.

Minor breaking change: `split_delimiters` now consistently
raises `SyntaxError` for mismatched delimiters.  (Previously it
would sometimes raise `ValueError`.)

</dd></dl>

#### 0.12.2

*2024/09/11*

<dl><dd>

* A minor semantic change to [`lines_strip_indent`](#lines_strip_indentli):
  when it encounters a whitespace-only line, it clips the line to *trailing*
  in the `LineInfo` object.  It used to clip such lines to *leading*.  But this
  changed `LineInfo.column_number` in a nonsensical way.

  This behavior is policy going forward: if a lines modifer function ever clips
  the entire line, it must clip it to *trailing* rather than *leading*.  It
  shouldn't matter one way or another, as whitespace-only lines arguably
  shouldn't have any explicit semantics.  But it makes intuitive sense to me
  that their empty line should be at column number 1, rather than 9 or 13
  or whatnot.  (Especially considering that with `lines_strip_indent` their
  indent value is synthetic anyway, inferred by looking ahead.)

* Major cleanup to the lines modifier test suites.

</dd></dl>

#### 0.12.1

*2024/09/07*

<dl><dd>

In fine **big** tradition, here's an update published
immediately after a big release.

Surprisingly, even though this is only a small update,
it still adds *two* new packages to **big**: *metadata* and *version*.

There's sadly one breaking change.

#### `big.metadata`

<dl><dd>

New package.
A package containing metadata about **big** itself.
Currently only contains one thing: *version*.

</dd></dl>

#### `big.version`

<dl><dd>

New package.  A package for working with version information.

</dd></dl>


#### `lines_strip_line_comments`

<dl><dd>

> This API has breaking changes.

The default value for `quotes` has changed.  Now it's
what it should always have been: empty.  No quote marks
are defined by default, which means the default behavior of
[`lines_strip_line_comments`](#lines_strip_line_commentsli-line_comment_markers--quotes-escape-multiline_quotes)
is now to simply truncate the line
at the leftmost comment marker.

Processing quote marks by default was *always* too opinionated
for this function.  Consider: having `'` active as a quote
marker meant that single-quotes need to be balanced,

>    which means you can't process a line like this that only has one.

Wish I'd figured this out before the release yesterday!  Hopefully
this will only cause smiles, and no teeth-gnashing.

</dd></dl>

#### `metadata.version`

<dl><dd>

New value.  A
[`Version`](#versionsnone--epochnone-releasenone-release_levelnone-serialnone-postnone-devnone-localnone)
object representing the current version of **big**.

</dd></dl>

#### `Version`

<dl><dd>

New class.
[`Version`](#versionsnone--epochnone-releasenone-release_levelnone-serialnone-postnone-devnone-localnone)
represents a version number.  You can
construct them from [PEP 440](https://peps.python.org/pep-0440/)-compliant
version strings, or specify them using keyword-only parameters.
[`Version`](#versionsnone--epochnone-releasenone-release_levelnone-serialnone-postnone-devnone-localnone)
objects are immutable, ordered, and hashable.

</dd></dl>


#### 0.12

<dl><dd>

*2024/09/06*

Lots of changes this time!  Most of 'em are in the `big.text`
module, particularly the `lines` and _lines modifier_
functions.  But plenty of other modules got in on the fun too.

**big** even has a new module: `deprecated`.  Deprecated
functions and classes get moved into this module.  Note that
the contents of `deprecated` are not automatically imported
into `big.all`.

The following functions and classes have breaking changes:

<dl><dd>

[`Delimiter`](#delimiterclose--escape-multilinetrue-quotingfalse)

[`LineInfo`](#lineinfolines-line-line_number-column_number--leadingnone-trailingnone-endnone-indent0-matchnone-kwargs)

[`lines_strip_line_comments`](#lines_strip_line_commentsli-line_comment_markers--quotes-escape-multiline_quotes)

[`split_delimiters`](#split_delimiterss-delimiters--state)

[`split_quoted_strings`](#split_quoted_stringss-quotes---escape-multiline_quotes-state)

</dd></dl>


These functions have been renamed:

<dl><dd>

`lines_filter_comment_lines` is now [`lines_filter_line_comment_lines`](#lines_filter_line_comment_linesli-comment_markers)

`lines_strip_comments` is now [`lines_strip_line_comments`](#lines_strip_line_commentsli-line_comment_markers--quotes-escape-multiline_quotes)

`parse_delimiters` is now [`split_delimiters`](#split_delimiterss-delimiters--state)

</dd></dl>


**big** has five new functions:

<dl><dd>

[`combine_splits`](#combine_splitss-split_arrays)

[`encode_strings`](#encode_stringso--encodingascii)

[`LineInfo.clip_leading`](#lineinfoclip_leadingline-s)

[`LineInfo.clip_trailing`](#lineinfoclip_trailingline-s)

[`split_title_case`](split_title_cases--split_allcapstrue)

</dd></dl>

</dd></dl>

Finally, here's an in-depth description of all changes
in **big** 0.12, sorted by API name.

#### `bytes_linebreaks` and `bytes_linebreaks_without_crlf`

<dl><dd>

Extremely minor change!  Python's `bytes` and `str` objects
don't agree on which ASCII characters represent line breaks.
The `str` object obeys the Unicode standard, which means
there are four:

    \n \v \f \r

For some reason, Python's `bytes` object only supports two:

    \n \r

I have no idea why this is.  We might fix it.  And if we do,
**big** is ready.  It now calculates
[`bytes_linebreaks`](#bytes_linebreaks)
and
[`bytes_linebreaks_without_crlf`](#bytes_linebreaks_without_crlf)
on the fly to agree with Python.
If either (or both) work as newline characters for the `splitlines`
method on a `bytes` object, they'll automatically be inserted
into these iterables of bytes linebreaks.

</dd></dl>

#### `combine_splits`

<dl><dd>

New function. If you split a string two different ways,
producing two arrays that sum to the original string,
`combine_splits` will merge those splits together, producing
a new array that splits in every place any of the two split
arrays had a split.

Example:

    >>> big.combine_splits("abcdefg", ['a', 'bcdef', 'g'], ['abc', 'd', 'efg'])
    ['a, 'bc', 'd', 'ef', 'g']

</dd></dl>

#### `Delimiter`

<dl><dd>

> This API has breaking changes.

`Delimiter` is a simple data class, representing information about
delimiters to
[`split_delimiters`](#split_delimiterss-delimiters--state)
 (previously `parse_delimiters`).
`split_delimiters` has changed, and some of those changes are
reflected in the `Delimiter` object; also, some changes to `Delimiter`
are simply better API choices.

The old `Delimiter` object is deprecated but still available,
as `big.deprecated.Delimiter`.  It should only be used with
`big.deprecated.parse_delimiters`, which is also deprecated.
`big.deprecated.Delimiter` will be removed when
`big.deprecated.parse_delimiters` is removed, which will be
no sooner than September 2025.

Changes:
* The first argument to the old `Delimiter` object was `open`,
  and was stored as the `open` attribute.  These have both been
  completely removed.  Now, the "open delimiter" is specified
  as a key in a dictionary of delimiters, mapping open delimiters
  to `Delimiter` objects.
* The old `Delimiter` object had a boolean `backslash` attribute;
  if it was True, that delimiter allows escaping using a backslash.
  Now `Delimiter` has an `escape` parameter and attribute,
  specifying the escape string you want to use inside that
  set of delimiters.
* `Delimiter` also now has two new attributes, `quoting` and
  `multiline`.  These default to `False` and `True` respectively;
  you can specify values for these with keyword-only arguments
  to the constructor.
* The new `Delimiter` object is read-only after construction,
  and is hashable.

</dd></dl>


#### `encode_strings`

<dl><dd>

Slightly liberalized the types it accepts.  It previously
required `o` to be a collection; now `o` can be a `bytes`
or `str` object.  Also, it now explicitly supports `set`.

</dd></dl>

#### `get_int_or_float`

<dl><dd>

Minor behavior change.  If the `o` you pass in is a `float`,
or can be converted to `float` (but couldn't be converted directly
to an `int`), `get_int_or_float` will experimentally convert that
`float` to an `int`.  If the resulting `int` compares equal to that
`float`, it'll return the `int`, otherwise it'll return the `float`.

For example, `get_int_or_float("13.5")` still returns `13.5`
(a `float`), but `get_int_or_float("13.0")` now returns `13`
(an `int`).  (Previously, `get_int_or_float("13.0")` would
have returned `13.0`.)

This better represents the stated aesthetic of the function--it
prefers ints to floats.  And since the int is exactly equal to
the float, I assert this is completely backwards compatible.

</dd></dl>

#### `Heap`

<dl><dd>

Minor updates to the documentation and to the text of some exceptions.

</dd></dl>

#### `LineInfo`

<dl><dd>

> This API has breaking changes.

Breaking change: the
[`LineInfo`](#lineinfolines-line-line_number-column_number--leadingnone-trailingnone-endnone-indent0-matchnone-kwargs)
constructor has a
new `lines` positional parameter, added *in front of*
the existing positional parameters.  This new first argument
should be the  `lines` iterator that yielded this
`LineInfo` object.  It's stored in the `lines` attribute.
(Why this change?  The `lines` object contains information
needed by the lines modifiers, for example `tab_width`.)

Minor optimization:
[`LineInfo`](#lineinfolines-line-line_number-column_number--leadingnone-trailingnone-endnone-indent0-matchnone-kwargs)
objects previously had many
optional fields, which might or might not be added
dynamically.  Now all fields are pre-added.  (This makes
the CPython 3.13 runtime happier; it really wants you to
set *all* your class's attributes in its `__init__`.)

Minor breaking change: the original string stored in the
`line` attribute now includes the linebreak character, if any.
This means concatenating all the `info.line` strings
will reconstruct the original `s` passed in to `lines`.

New feature: while some methods used to update the `leading`
attribute when they clipped leading text from the line,
the "lines modifiers" are now very consistent about updating
`leading`, and the new symmetrical attribute `trailing`.

New feature:
[`LineInfo`](#lineinfolines-line-line_number-column_number--leadingnone-trailingnone-endnone-indent0-matchnone-kwargs)
now has an `end` attribute,
which contains the end-of-line character that ended this line.

These three attributes allow us to assert a new invariant:
as long as you _modify_ the contents of `line` (e.g.
turning tabs into spaces),

    info.leading + line + info.trailing + info.end == info.line

[`LineInfo`](#lineinfolines-line-line_number-column_number--leadingnone-trailingnone-endnone-indent0-matchnone-kwargs)
objects now always have these attributes:
  * `lines`, which contains the base lines iterator.
  * `line`, which contains the original unmodified line.
  * `line_number`, which contains the line number of
    this line.
  * `column_number`, which contains the starting column
    number of the first character of this line.
  * `indent`, which contains the indent level of the
    line if computed, and `None` otherwise.
  * `leading`, which contains the string stripped from
    the beginning of the line.  Initially this is the
    empty string.
  * `trailing`, which contains the string stripped from
    the end of the line.  Initially this is the
    empty string.
  * `end`, which is the end-of-line character
    that ended the current line.  For the last line yielded,
    `info.end` will always be the empty string.  If the last
    character of the text split by `lines` was an end-of-line
    character, the last `line` yielded will be the empty string,
    and `info.end` will also be the empty string.
  * `match`, which contains a `Match` object if this line
    was matched with a regular expression, and `None` otherwise.

#### `LineInfo.clip_leading` and `LineInfo.clip_trailing`


[`LineInfo`](#lineinfolines-line-line_number-column_number--leadingnone-trailingnone-endnone-indent0-matchnone-kwargs)
also has two new methods:
[`LineInfo.clip_leading`](#lineinfoclip_leadingline-s)
and
[`LineInfo.clip_trailing(line, s)`](#lineinfoclip_trailingline-s).
These methods clip a leading or
trailing substring from the current `line`, and transfer
it to the relevant field in
[`LineInfo`](#lineinfolines-line-line_number-column_number--leadingnone-trailingnone-endnone-indent0-matchnone-kwargs)
(either `leading` or
`trailing`).  `clip_leading` also updates the `column_number`
attribute.

The name "clip" was chosen deliberately to be distinct from "strip".
"strip" functions on strings remove substrings and throws them away;
my "clip" functions on strings removes substrings and puts them
somewhere else.

</dd></dl>

#### `lines_filter_comment_lines`

<dl><dd>

`lines_filter_comment_lines` has been renamed to
[`lines_filter_line_comment_lines`](#lines_filter_line_comment_linesli-comment_markers).
For backwards compatibility, the function
is also available under the old name; this old name will
eventually be removed, but not before September 2025.

</dd></dl>

#### `lines_filter_line_comment_lines`

<dl><dd>

> This API has breaking changes.

New name for `lines_filter_comment_lines`.

Correctness improvements:
[`lines_filter_line_comment_lines`](#lines_filter_line_comment_linesli-comment_markers)
now enforces that single-quoted strings can't span lines,
and multi-quoted strings must be closed before the end of
the last line.

Minor optimization: for every line, it used to `lstrip` a copy of
the line, then use a regular expression to see if the line started
with one of the comment characters.  Now the regular expression
itself skips past any leading whitespace.

</dd></dl>

#### `lines_grep`

<dl><dd>

New feature: [`lines_grep`](#lines_grepli-pattern--invertfalse-flags0-matchmatch)
has always used `re.search` to examine
the lines yielded.  It now writes the result to `info.match`.
(If you pass in `invert=True` to `lines_grep`, `lines_grep`
still writes to the `match` attribute--but it always writes `None`.)

If you want to write the `re.Match` object to another attribute,
pass in the name of that attribute to the keyword-only
parameter `match`.

</dd></dl>

#### `lines_rstrip` and `lines_strip`

<dl><dd>

New feature:
[`lines_rstrip`](#lines_rstripli-separatorsnone)
and
[`lines_strip`](#lines_stripli-separatorsnone)
now both accept a
`separators` argument; this is an iterable of separators,
like the argument to
[`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse).
The default value of `None` preserves the previous behavior,
stripping whitespace.

</dd></dl>

#### `lines_sort`

<dl><dd>

New feature:
[`lines_sort`](#lines_sortli--keynone-reversefalse)
now accepts a `key` parameter,
which is used as the `key` argument for `list.sort`.
The value passed in to `key` is the `(info, line)` tuple
yielded by the upstream iterator.  The default value preserves
the previous behavior, sorting by the `line` (ignoring the
`info`).

</dd></dl>


#### `lines_strip_comments`

<dl><dd>

This function has been renamed
[`lines_strip_line_comments`](#lines_strip_line_commentsli-line_comment_markers--quotes-escape-multiline_quotes)
and
rewritten, see below.  The old deprecated version will be
available at `big.deprecated.lines_strip_comments` until at
least September 2025.

Note that the old version of `line_strip_comments` still uses
the current version of
[`LineInfo`,](#lineinfolines-line-line_number-column_number--leadingnone-trailingnone-endnone-indent0-matchnone-kwargs)
so use of this deprecated
function is still exposed to those breaking changes.
(For example, `LineInfo.line` now includes the linebreak character
that terminated the current line, if any.)

</dd></dl>

#### `lines_strip_indent`

<dl><dd>

Bugfix:
[`lines_strip_indent`](#lines_strip_indentli)
previously required
whitespace-only lines to obey the indenting rules, which was
a mistake.  My intention was always for `lines_strip_indent`
to behave like Python, and that includes not really caring
about the intra-line-whitespace for whitespace-only
lines.  Now `lines_strip_indent` behaves more like Python:
a whitespace-only line behaves as if it has
the same indent as the previous line.  (Not that the
indent value of an empty line should matter--but this
behavior is how you'd intuitively expect it to work.)

</dd></dl>


#### `lines_strip_line_comments`

<dl><dd>

> This API has breaking changes.

[`lines_strip_line_comments`](#lines_strip_line_commentsli-line_comment_markers--quotes-escape-multiline_quotes)
is the new name for the old
`lines_strip_comments` lines modifier function.  It's also
been completely rewritten.

Changes:
* The old function required quote marks and the escape string
  to be single characters. The new function allows quote marks
  and the escape string to be of any length.
* The old function had a slightly-smelly `triple_quotes` parameter
  to support multiline strings.  The new version supports separate
  parameters for single-line quote marks (`quotes`)  and multiline
  quote marks (`multiline_quotes`).
* The `backslash` parameter has been renamed to `escape`.
* The `rstrip` parameter has been removed.  If you need to
  rstrip the line after stripping the comment, wrap your
  `lines_strip_line_comments` call with a
  [`lines_rstrip`](#lines_rstripli-separatorsnone)
  call.
* The old function didn't enforce that strings shouldn't
  span lines--single-quoted and triple-quoted strings behaved
  identically.  The new version raises `SyntaxError` if quoted
  strings using non-multiline quote marks contain newlines.

(`lines_strip_line_comments` has always been implemented using
[`split_quoted_strings`](#split_quoted_stringss-quotes---escape-multiline_quotes-state);
this is why it now supports multicharacter
quote marks and escape strings.  It also benefits from the
new optimizations in `split_quoted_strings`.)


</dd></dl>

#### `multisplit`

<dl><dd>

Minor optimizations.
[`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
used to locally define a
new generator function, then call it and return the generator.
I promoted the generator function to module level, which means
we no longer rebind it each time `multisplit` is called.  As
a very rough guess, this can be as much as a 10% speedup for
`multisplit` run on very short workloads.  (It's also *never*
slower.)

I also applied this same small optimization to several other
functions in the `text` module.  In particular,
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_responseoverflowresponseraise-overflow_before0-overflow_after0)
was binding functions inside a loop (!!).  (Dumb, huh!)
These local functions are still bound inside `merge_columns`,
but now at least they're outside the loop.

Another minor speedup for `multisplit`: when `reverse=True`,
it used to reverse the results *three times!*  `multisplit`
now explicitly observes and manages the reversed state of the
result to avoid needless reversing.

</dd></dl>

#### `parse_delimiters`

<dl><dd>

This function has been renamed
[`split_delimiters`](#split_delimiterss-delimiters--state)
and rewritten,
see below.  The old version is still available, using the name
`big.deprecated.parse_delimiters` module, and will be available
until at least September 2025.

</dd></dl>


#### `Scheduler`

<dl><dd>

Code cleanups both in the implementation and the test suite,
including one minor semantic change.

Cleaned up `Scheduler._next`, the internal method call
that implements the heart of the scheduler.  The only externally
visible change: the previous version would call `sleep(0)` every
time it yielded an event.  On modern operating systems this should
yields the rest of the current thread's current time slice back
to the OS's scheduler.  This can make multitasking smoother,
particularly in Python programs.  But this is too opinionated for
library code--if you want a `sleep(0)` there, by golly, you can
call that yourself when the `Scheduler` object yields to you.
I've restructured the code and eliminated this extraneous `sleep(0)`.

Also, rewrote big chunks of the test suite (`tests/test_scheduler.py`).
The multithreaded tests are now much better synchronized, while
also becoming easier to read.  Although it seems intractable to
purge *all* race conditions from the test suite, this change has
removed most of them.

</dd></dl>

#### `split_delimiters`

<dl><dd>

> This API has breaking changes.

[`split_delimiters`](#split_delimiterss-delimiters--state)
is the new name for the old `parse_delimiters`
function.  The function has also been completely re-tooled and
re-written.

Changes:
* `parse_delimiters` took an iterable of `Delimiters`
  objects, or strings of length 2.  `split_delimiters`
  takes a dictionary mapping open delimiter strings to
  `Delimiter` objects, and `Delimiter` objects no
  longer have an "open" attribute.
* `split_delimiters` now accepts an `state` parameter,
  which specifies the initial state of nested delimiters.
* `split_delimiters` no longer cares if there were unclosed
  open delimiters at the end of the string.  (It used to
  raise `ValueError`.)  This includes quote marks; if you
  don't want quoted strings to span multiple lines, it's up
  to you to detect it and react (e.g. raise an exception).
* The internal implementation has changed completely.
  `parse_delimiters` manually parsed the input string
  character by character.  `split_delimiters` uses
  [`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse),
  so it zips past the uninteresting characters and only examines
  the delimiters and escape characters.  It's always faster,
  except for some trivial calls (which are fast enough anyway).
* Another benefit of using `multisplit`: open delimiters,
  close delimiters, and the escape string may now all be
  any nonzero length.  (In the face of ambiguity,
  `split_delimiters` will always choose the longer delimiter.)

See also changes to `Delimiter`.

</dd></dl>

#### `split_quoted_strings`

<dl><dd>

> This API has breaking changes.

[`split_quoted_strings`](#split_quoted_stringss-quotes---escape-multiline_quotes-state)
has been completely re-tooled and
re-written.  The new API is simpler, easier to understand,
and conceptually clarified.  It's a major upgrade!

Changes:
* The value it yields is different:
  * The old version yielded `(is_quote, segment)`, where
    `is_quote` was a boolean value indicating whether or not
    `segment` was quoted.  If `segment` was quoted, it began
    and ended with (single character) quote marks.  To reassemble
    the original string, join together all the `segment` strings
    in order.
  * The new version yields `(leading_quote, segment, trailing_quote)`,
    where `leading_quote` and `trailing_quote` are either matching
    quote marks or empty.  If they're true values, the `segment`
    string is inside the quotes.  To reassemble the original string,
    join together *all* the yielded strings in order.
* The `backslash` parameter has been replaced by a new parameter,
  `escape`.  `escape` allows specifying the escape string, which
  defaults to '\\' (backslash).  If you specify a false value,
  there will be no escape character in strings.
* By default `quotes` only contains `'` (single-quote)
  and `"` (double-quote).  The previous version also
  recognized `"""` and `'''` as multiline quote marks
  by default; this is no longer true, as it's too
  opinionated and Python-specific.
* The old version didn't actually distinguish between
  single-quoted strings and triple-quoted strings.  It
  simply didn't care whether or not there were newlines
  inside quoted strings.  The new version raises a
  `SyntaxError` if there's a newline character inside
  a string delimited with a quote marker from `quotes`.
* The old version accepted a stinky `triple_quotes` parameter.
  That's been removed in favor of a new parameter,
  `multiline_quotes`.  `multiline_quotes` is like `quotes`,
  except that newline characters are allowed inside their
  quoted strings.
* `split_quoted_string` accepts another new parameter,
  `state`, which sets the initial state of quoting.
* Thd old implementation of `split_quoted_string` used a
  hand-coded parser, manually analyzing each character in
  the input text.  Now it uses
  [`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse),
  so it only bothers to examine
  the interesting substrings.  `multisplit` has a large
  startup cost the first time you use a particular set of
  iterators, but this information is cached for subsequent calls.
  Bottom line, the new version is much faster
  for larger workloads.  (It can be slower for trivial
  examples... where speed doesn't matter anyway.)
* Another benefit of switching to `multisplit`: `quotes`
  now supports quote delimiters and an escape string
  of any nonzero length.  In the case of ambiguity--if
  more than one quote delimiter matches at a
  time--`split_quoted_string` will always choose the
  longer delimiter.

</dd></dl>

#### `split_title_case`

<dl><dd>

New function.
[`split_title_case`](split_title_cases--split_allcapstrue)
splits a string at word boundaries,
assuming the string is in "TitleCase".

</dd></dl>

#### `StateManager`

<dl><dd>

Small performance upgrade for
[`StateManager`.](#statemanagerstate--on_enteron_enter-on_exiton_exit-state_classnone)
observers.
`StateManager` always uses a copy of the observer
list (specifically, a tuple) when calling the observers; this
means it's safe to modify the observer list at any time.
`StateManager` used to always make a fresh copy every time you
called an event; now it uses a cached copy, and only recomputes
the tuple when the observer list changes.

(Note that it's not thread-safe to modify the observer list
from one thread while also dispatching events in another.
Your program won't crash, but the list of observers called
may be unpredictable based on which thread wins or loses the
race.  But this has always been true.  As with many libraries,
the `StateManager` API leaves locking up to you.)

</dd></dl>

_p.s. I'm getting close to declaring big as being version 1.0._
_I don't want to do it until I'm done revising the APIs._

_p.p.s. Updated copyright notices to 2024._

_p.p.p.s. Yet again I thank Eric V. Smith for his willingness to humor me
in my how-many-parameters-could-dance-on-the-head-of-a-pin API theological
discussions._


</dd></dl>


#### 0.11
<dl><dd>

*released 2023/09/19*

* Breaking change: renamed almost all the old `whitespace` and `newlines` tuples.
  Worse yet, one symbol has the same name but a *different value:* `ascii_whitespace`!
  I've also changed the suffix `_without_dos` to the more accurate and intuitive
  `_without_crlf`, and similarly changed `newlines` to `linebreaks`.
  Sorry for all the confusion.  This resulted from a lot of research into whitespace
  and newline characters, in Python, Unicode, and ASCII; please see the new deep-dive
  [**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
  to see what all the fuss is about.  Here's a summary of all the
  changes to the whitespace tuples:

        RENAMED TUPLES (old name -> new name)
          ascii_newlines               -> bytes_linebreaks
          ascii_whitespace             -> bytes_whitespace
          newlines                     -> linebreaks

          ascii_newlines_without_dos   -> bytes_linebreaks_without_crlf
          ascii_whitespace_without_dos -> bytes_whitespace_without_crlf
          newlines_without_dos         -> linebreaks_without_crlf
          whitespace_without_dos       -> whitespace_without_crlf

        REMOVED TUPLES
          utf8_newlines
          utf8_whitespace

          utf8_newlines_without_dos
          utf8_whitespace_without_dos

        UNCHANGED TUPLES (same name, same meaning)
          whitespace

        NEW TUPLES
          ascii_linebreaks
          ascii_whitespace
          str_linebreaks
          str_whitespace
          unicode_linebreaks
          unicode_whitespace

          ascii_linebreaks_without_crlf
          ascii_whitespace_without_crlf
          str_linebreaks_without_crlf
          str_whitespace_without_crlf
          unicode_linebreaks_without_crlf
          unicode_whitespace_without_crlf

* Changed
  [`split_text_with_code`](#split_text_with_codes--tab_width8-allow_codetrue-code_indent4-convert_tabs_to_spacestrue)
  implementation to use `StateManager`.
  (No API or semantic changes, just an change to the internal implementation.)
* New function in the [`big.text`](#bigtext) module: [`encode_strings`,](#encode_stringso--encodingascii)
  which takes a container object containing `str` objects and returns an equivalent object
  containing encoded versions of those strings as `bytes`.
* When you call
  [`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
  with a type mismatch
  between 's' and 'separators', the exception it raises
  now includes the values of 's' and 'separators'.
* Added more tests for `big.state` to exercise all the string arguments
  of `accessor` and `dispatch`.
* The exhaustive
  [`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
  tester now lets you
  specify test cases as cohesive strings, rather
  than forcing you to split the string manually.
* The exhaustive
  [`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
  tester is better at
  internally verifying that it's doing the right
  thing.  (There are some internal sanity checks,
  and those are more accurate now.)
* Whoops!  The name of the main class in [`big.state`](#bigstate) is
  [`StateManager`.](#statemanagerstate--on_enteron_enter-on_exiton_exit-state_classnone)
  I accidentally wrote `StateMachine` instead in the docs... several times.
* Originally the
  [`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
  parameter 'separators'
  was required.  I changed it to optional a while ago,
  with a default of `None`.  (If you pass in `None`
  it uses [`big.str_whitespace`](#str_whitespace) or [`big.bytes_whitespace`](#bytes_whitespace),
  depending on the type of `s`.)  But the documentation
  didn't reflect this change until... now.
* Improved the prose in
  [**The `multi-` family of string functions** deep-dive.](#The-multi--family-of-string-functions)
  Hopefully now it does a better job of selling `multisplit` to the reader.
* The usual smattering of small doc fixes and improvements.

My thanks again to Eric V. Smith for his willingness to consider and discuss these
issues.  Eric is now officially a contributor to **big,** increasing the project's
[bus factor](https://en.wikipedia.org/wiki/Bus_factor) to two.  Thanks, Eric!

#### 0.10
<dl><dd>

*released 2023/09/04*

* Added the new [`big.state`](#bigstate) module, with its exciting
  [`StateManager`](#statemanagerstate--on_enteron_enter-on_exiton_exit-state_classnone)
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
  `parse_delimiters` (ed: now [`split_delimiters`](#split_delimiterss-delimiters--state))
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
  [`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
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
  [`multisplit`.](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
  Internally, it does the
  string splitting using `re.split`, which returns a `list`.  It used
  to iterate over the list and yield each element.  But that meant keeping
  the entire list around in memory until `multisplit` exited.  Now,
  [`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
  reverses the list, pops off the final element, and yields
  that.  This means
  [`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
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
  [`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
  and
  [`multistrip`](#multistrips-separators-leftTrue-rightTrue)
  argument verification code.  Both functions now consistently check all
  their inputs, and use consistent error messages when raising an exception.
</dd></dl>

#### 0.6.17
<dl><dd>

*released 2023/03/09*

* Fixed a minor crashing bug in
  [`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse):
  if you passed in a *list* of separators (or `separators`
  was of any non-hashable type), and `reverse` was true,
  `multisplit` would crash.  It used `separators` as a key
  into a dict, which meant `separators` had to be hashable.
* [`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
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
  [`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse):
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
  [`lines_grep`](#lines_grepli-pattern--invertfalse-flags0-matchmatch).
</dd></dl>

#### 0.6.7
<dl><dd>

*released 2022/10/16*

* Added three new lines modifier functions
  to the [`text`](#bigtext) module:
  `lines_filter_contains`,
  `lines_filter_grep`,
  and
  [`lines_sort`.](#lines_sortli--keynone-reversefalse)
* [`gently_title`](#gently_titles-apostrophesnone-double_quotesnone)
  now accepts `str` or `bytes`.  Also added the `apostrophes` and
  `double_quotes` arguments.
</dd></dl>

#### 0.6.6
<dl><dd>

*released 2022/10/14*

* Fixed a bug in
  [`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse).
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
  `lines_strip_comments` [ed: now [`lines_strip_line_comments`](#lines_strip_line_commentsli-line_comment_markers--quotes-escape-multiline_quotes)
  and
  [`split_quoted_strings`](#split_quoted_stringss-quotes---escape-multiline_quotes-state)
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
  [`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse),
  and added
  [`multistrip`](#multistrips-separators-leftTrue-rightTrue)
  and
  [`multipartition`,](#multipartitions-separators-count1--reverseFalse-separateTrue)
  collectively called
  [**The `multi-` family of string functions.**](#The-multi--family-of-string-functions)
  (Thanks to Eric Smith for suggesting
  [`multipartition`!](#multipartitions-separators-count1--reverseFalse-separateTrue)
  Well, sort of.)
  * `[`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)`
    now supports five (!) keyword-only parameters, allowing the caller
    to tune its behavior to an amazing degree.
  * Also, the original implementation of
    `[`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)`
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
