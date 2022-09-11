![# big](/resources/images/big.header.png)

##### Copyright 2022 by Larry Hastings

**big** is a Python package, a grab-bag of useful technology
I always want to have handy.  Finally!  Instead of copying-and-pasting
all my little helper functions between projects, I have them all in
one easily-importable place.  And, since it's a public package, you can
use 'em too!

**big** requires Python 3.6 or newer.  It has few dependencies.

*Think big!*

## Using big

To use **big**, just install the **big** package (and its dependencies)
from PyPI using your favorite Python package manager.  Then simply

```Python
import big
```

in your programs.

Internally **big** is broken up into submodules, aggregated together
loosely by problem domain.  But all functions are also imported into the top-level
module; every function or class published in **big** is available directly in the
`big` module.

**big** is designed to be safe for use with `import *`:

```Python
from big import *
```

but that's up to you.

**big** is licensed using the [MIT license.](https://opensource.org/licenses/MIT)
You're free to use it and even ship it in your own programs, as long as you leave my copyright
notice on the source code.

# Index

[`BoundInnerClass`](#boundinnerclasscls)

[`CycleError`](#cycleerror)

[`fgrep(path, text, *, encoding=None, enumerate=False, case_insensitive=False)`](#fgreppath-text--encodingnone-enumeratefalse-case_insensitivefalse)

[`file_mtime(path)`](#file_mtimepath)

[`file_mtime_ns(path)`](#file_mtime_nspath)

[`file_size(path)`](#file_sizepath)

[`gently_title(s)`](#gently_titles)

[`get_float(o, default=_sentinel)`](#get_floato-default_sentinel)

[`get_int(o, default=_sentinel)`](#get_into-default_sentinel)

[`get_int_or_float(o, default=_sentinel)`](#get_int_or_floato-default_sentinel)

[ `grep(path, pattern, *, encoding=None, enumerate=False, flags=0)`](#greppath-pattern--encodingnone-enumeratefalse-flags0)

[`merge_columns(*columns, column_separator=" ", overflow_response=OverflowResponse.RAISE, overflow_before=0, overflow_after=0)`](#merge_columnscolumns-column_separator--overflow_responseoverflowresponsenormal-overflow_before0-overflow_after0)

[`multisplit(text, separators, *, maxsplit=-1)`](#multisplittext-separators--maxsplit-1)

[`normalize_whitespace(s)`](#normalize_whitespaces)

[`parse_timestamp_3339Z(s)`](#parse_timestamp_3339zs)

[`pushd(directory)`](#pushddirectory)

[`re_partition(text, pattern, *, flags=0)`](#re_partitiontext-pattern--flags0)

[`re_rpartition(text, pattern, *, flags=0)`](#re_rpartitiontext-pattern--flags0)

[`rstripped_lines(s, *, sep=None)`](#rstripped_liness--sepNone)

[`safe_mkdir(path)`](#safe_mkdirpath)

[`safe_unlink(path)`](#safe_unlinkpath)

[`split_text_with_code(s, *, tab_width=8, allow_code=True, code_indent=4, convert_tabs_to_spaces=True)`](#split_text_with_codes--tab_width8-allow_codetrue-code_indent4-convert_tabs_to_spacestrue)

[`stripped_lines(s, *, sep=None)`](#stripped_liness--sepNone)

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

[`touch(path)`](#touchpath)

[`translate_filename_to_exfat(s)`](#translate_filename_to_exfats)

[`translate_filename_to_unix(s)`](#translate_filename_to_unixs)

[`try_float(o)`](#try_floato)

[`try_int(o)`](#try_into)

[`UnboundInnerClass`](#unboundinnerclasscls)

[`View.close()`](#viewclose)

[`View.copy()`](#viewcopy)

[`View.done(*nodes)`](#viewdonenodes)

[`View.print(print=print)`](#viewprintprintprint)

[`View.ready()`](#viewready)

[`View.reset()`](#viewreset)

[`wrap_words(words, margin=79, *, two_spaces=True)`](#wrap_wordswords-margin79--two_spacestrue)

[**Word wrapping and formatting**](#word-wrapping-and-formatting)

[**Bound inner classes**](#bound-inner-classes)

[**Enhanced `TopologicalSorter`**](#enhanced-topologicalsorter)


# API Reference


## `big.boundinnerclass`

Class decorators that implement bound inner classes.  See the
[**Bound inner classes**](#bound-inner-classes)
section for more information.


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
> (Tip: to perform a case-insensitive pattern match, pass in the
> `re.IGNORECASE` flag into flags for this function (if pattern is a string
> or bytes) or when creating your regular expression object (if pattern is
> an `re.Pattern` object).

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

See the [**Enhanced `TopologicalSorter`**](#enhanced-topologicalsorter) section for more information.

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

#### `View.__bool__()`

> Returns `True` if more work can be done in the
> view--if there are nodes waiting to be yielded by
> `get_ready`, or waiting to be returned by `done`.
>
> Aliased to `TopologicalSorter.is_active` for compatibility
> with graphlib.

#### `View.close()`

> Closes the view.  A closed view can no longer be used.

#### `View.copy()`

> Returns a shallow copy of the view, duplicating its current state.

#### `View.done(*nodes)`

> Marks nodes returned by `ready` as "done",
> possibly allowing additional nodes to be available
> from `ready`.

#### `View.print(print=print)`

> Prints the internal state of the view, and its graph.
> Used for debugging.
>
> `print` is the function used for printing;
> it should behave identically to the builtin `print` function.

#### `View.ready()`

> Returns a tuple of "ready" nodes--nodes with no
> predecessors, or nodes whose predecessors have all
> been marked "done".
>
> Aliased to TopologicalSorter.get_ready for
> compatibility with graphlib.

#### `View.reset()`

> Resets the view to its initial state,
> forgetting all "ready" and "done" state.


## `big.text`

Functions for working with text strings.  See the
[**Word wrapping and formatting**](#word-wrapping-and-formatting)
section below for a higher-level view on some of these functions.


#### `gently_title(s)`

> Uppercase the first character of every word in `s`.
> Leave the other letters alone.

> (For the purposes of this algorithm, words are
> any blob of non-whitespace characters.)

> Capitalize the letter after an apostrophe if
>   a) the apostrophe is after whitespace
>      (or is the first letter of the string), or
>   b) if the apostrophe is after a letter O or D,
>      and that O or D is after whitespace (or is
>      the first letter of the string).  The O or D
>      here will also be capitalized.
> Rule a) handles internally quoted strings:
>   He Said 'No I Did Not'
> and contractions that start with an apostrophe
>   'Twas The Night Before christmas
> Rule b) handles certain Irish, French, and Italian
> names.
>   Peter O'Toole
>   Lord D'Arcy
>
> Capitalize the letter after a quote mark if
> the quote mark is after whitespace (or is the
> first letter of a string).
>
> A run of consecutive apostrophes and/or
> quote marks is considered one quote mark for
> the purposes of capitalization.
>
> Each of these Unicode code points is considered
> an apostrophe:
>    '‘’‚‛
>
> Each of these Unicode code points is considered
> a quote mark:
>   "“”„‟«»‹›

#### `normalize_whitespace(s)`

> Returns `s`, but with every run of consecutive
> whitespace characters turned into a single space.
> Preserves leading and trailing whitespace.
>
> `normalize_whitespace("   a    b   c")` returns `" a b c"`.


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

#### `multisplit(text, separators, *, maxsplit=-1)`

> Like `str.split`, but separators is an iterable of separator strings.
>
> `text` can be `str` or `bytes`.
>
> `separators` should be an iterable.  Each element of `separators`
> should be the same type as `text`.  If `separators` is a string or bytes
> object, `multisplit` behaves as separators is a tuple containing each
> individual character.
>
> Returns a list of the substrings split from `text`.
>
> `maxsplit` should be either an integer or `None`.  If `maxsplit` is an
> integer greater than -1, multisplit will split `text` no more than
> `maxsplit` times.
>
> Example:
> ```Python
>     multisplit('ab:cd,:ef', ':,')
> ```
> returns
> ```Python
>     ["ab", "cd", "ef"]
> ```
>
> Example:
> ```Python
>     multisplit('\tthis is a\n\tbunch of words', (' ', '\t', '\n'))
> ```
>
> would produce the same result as
> ```Python
>     '\tthis is a\n\tbunch of words'.split()
> ```


#### `re_partition(text, pattern, *, flags=0)`

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
> If `pattern` is a string or bytes object, `flags` is passed in
> as the `flags` argument to `re.compile`.

#### `re_rpartition(text, pattern, *, flags=0)`

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
> If `pattern` is a string, `flags` is passed in
> as the `flags` argument to `re.compile`.


#### `rstripped_lines(s, *, sep=None)`

> Splits `s` at line boundaries, then "rstrips"
> (strips trailing whitespace) from each line.
>
> Returns an iterator yielding lines.
>
> `sep` specifies an alternate separator string.
> If provided, it should match the type of `s`.


#### `split_text_with_code(s, *, tab_width=8, allow_code=True, code_indent=4, convert_tabs_to_spaces=True)`

> Splits the string `s` into individual words,
> suitable for feeding into `wrap_words`.
>
> Paragraphs indented by less than `code_indent` will be
> broken up into individual words.
>
> If `allow_code` is true, paragraphs indented by at least
> `code_indent` spaces will preserve their whitespace:
> internal whitespace is preserved, and the newline is
> preserved.  (This will preserve the formatting of code
> examples when these words are rejoined into lines
> by `wrap_words`.)

#### `stripped_lines(s, *, sep=None)`

> Splits `s` at line boundaries, then strips
> whitespace from each line.
>
> Returns an iterator yielding lines.
>
> `sep` specifies an alternate separator string.
> If provided, it should match the type of `s`.


#### `wrap_words(words, margin=79, *, two_spaces=True)`

> Combines 'words' into lines and returns the result as a string.
> Similar to `textwrap.wrap`.
>
> 'words' should be an iterator containing text split at word
> boundaries.  Example:
> ```Python
>      "this is an example of text split at word boundaries".split()
> ```
>
> A single `'\n'` indicates a line break.
> If you want a paragraph break, embed two `'\n'` characters in a row.
>
> 'margin' specifies the maximum length of each line. The length of
> every line will be less than or equal to 'margin', unless the length
> of an individual element inside 'words' is greater than 'margin'.
>
> If 'two_spaces' is true, elements from 'words' that end in
> sentence-ending punctuation ('.', '?', and '!') will be followed
> by two spaces, not one.
>
> Elements in 'words' are not modified; any leading or trailing
> whitespace will be preserved.  You can use this to preserve
> whitespace where necessary, like in code examples.


## `big.time`

Functions for working with time.  Currently deals specifically
with timestamps.  The time functions in **big** are designed
to make it easy to use best practices.


#### `parse_timestamp_3339Z(s)`

> Parses a timestamp string returned by `timestamp_3339Z`.
> Returns a `datetime.datetime` object.

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


# Subsystem notes


## Word wrapping and formatting

**big** contains three functions used to reflow and format text
in a pleasing manner.  In the order you should use them, they are
`split_text_with_code`, `word_wrap`, and optionally `merge_columns`.
This trio of functions gives you the following word-wrap superpowers:

* Paragraphs of text representing embedded "code" don't get word-wrapped.
  Instead, their formatting is preserved.
* Multiple texts can be merged together into multiple columns.

#### Split text array

`split_text_with_code` splits a string of text into a
*split text array*,
and `word_wrap` consumes a *split text array* to produce its
word-wrapped output.  A split text array is an array of strings.
You'll see four kinds of strings in a split text array:

* Individual words, ready to be word-wrapped.
* Entire lines of "code", preserving their formatting.
* Line breaks, represented by a single newline: `'\n'`.
* Paragraph breaks, represented by two newlines: `'\n\n'`.

When `split_text_with_code` splits a string, it views each
line as either a "text" line or a "code" line.  Any non-blank
line that starts with `code_indent` or more spaces (or the
equivalent using tabs) is a "code" line, and any other
non-blank line is a "text" line.  But it has some state
here; when `split_text_with_code` sees a "text" line,
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

Also, whenever `split_text_with_code` switches between
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

`split_text_with_code` would turn this into the following split text array:
```Python
[ 'hello', 'there!', 'this', 'is', 'text.', '\n\n',
  'this', 'is', 'a', 'second', 'paragraph!']
```

`split_text_with_code` merged the first two lines together into
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

would be represented in a Python string as:
```Python
"What are the first four squared numbers?\n\n    for i in range(1, 5):\n\n\n        print(i**2)\n\nPython is just that easy!"
```

`split_text_with_code` considers the two lines with initial whitespace as "code" lines,
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
punctuation.  In practice you should just use `wrap_words`.

#### Merging columns

`merge_columns` merges multiple strings into columns on the same line.

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

(Note that `merge_columns` doesn't do its own word-wrapping;
instead, it's designed to consume the output of `wrap_words`.)

Each column is passed in to `merge_columns` as a "column tuple":

```Python
(s, min_width, max_width)
```

`s` is the string,
`min_width` is the minimum width of the column, and
`max_width` is the minimum width of the column.

As you saw above, `s` can contain newline characters,
and `merge_columns` obeys those when formatting each
column.

For each column, `merge_columns` measures the longest
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
column's `max_width`.  `merge_columns` discusses both "overflow lines",
lines that are longer than `max_width`, and "overflow columns", which
are columns that contain any overflow lines.

What does `merge_columns` do when it encounters overflow?  It provides
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

**big**'s `TopologicalSorter` is a drop-in replacement for
[`graphlib.TopologicalSorter`](https://docs.python.org/3/library/graphlib.html#graphlib.TopologicalSorter)
in the Python standard library (new in 3.9).  However, the version in **big** has been greatly upgraded:

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

- 'Y' has been marked as `done`.
- 'Z' has not yet been yielded by `get_ready`.

then `v` is no longer "coherent".

(If 'Y' has been marked as `done`, then it's okay to make 'Z' dependent on
'Y' regardless of what state 'Y' is in.  Likewise, if 'Z' hasn't been yielded
by `get_ready` yet, then it's okay to make 'Z' dependent on 'Y' regardless
of what state 'Y' is in.)

Note that you can restore a view to coherence.  In this case,
removing either `Y` or `Z` from `g` would resolve the incoherence
between `v` and `g`, and `v` would start working again.

Also note that you can have multiple views, in various states of iteration,
and by modifying the graph you may cause some to become incoherent but not
others.  Views are completely independent from each other.


## Bound inner classes

#### Overview

One minor complaint about Python is that inner classes don't have access to the outer object
at construction time.  Consider this Python code:

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
(generally called `self`). But that doesn't happen when `o.Inner` is called.  (It does pass in
a `self`, but in this case it's the newly-created `Inner` object.)  There's just no built-in way
for the `o.Inner` object being constructed to automatically get a reference to the `o` `Outer`
object.  If you need one, you must explicitly pass one in, like so:

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

This seems redundant.  You don't have to pass in `o` explicitly to method calls;
why should you have to pass it in explicitly to inner classes?  Well--now you don't have to!
You just need to decorate the inner class with `@big.BoundInnerClass`.

#### Using bound inner classes

Let's modify the above example to use our `BoundInnerClass` decorator:

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
Thanks, `BoundInnerClass`!  You've saved the day.

#### Inheritance

Bound inner classes get slightly complicated when mixed with inheritance.
It's not all that difficult, you merely need to obey the following rules:

1. *A bound inner class can inherit normally from any unbound class.*

2. *To subclass from a bound inner class while still inside the outer
class scope, or when referencing the inner class from the outer class
(as opposed to an instance of the outer class), you must actually
subclass or reference `classname.cls`.*  This is because inside the
outer class, the "class" you see is actually an instance of a
`BoundInnerClass` object.

3. *All classes that inherit from a bound inner class must always call the
superclass's `__init__`. You don't need to pass in the outer parameter;
it'll be automatically passed in to the superclass's `__init__` as before.*

4. *An inner class that inherits from a bound inner class, and which also wants
to be bound to the outer object, should be decorated with `BoundInnerClass`.*

5. *An inner class that inherits from a bound inner class, but doesn't want
to be bound to the outer object, should be decorated with UnboundInnerClass.*

Restating the last two rules: every class that descends from any `BoundInnerClass`
should be decorated with either `BoundInnerClass` or `UnboundInnerClass`.

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
* Since `ChildOfInner` inherits from a `BoundInnerClass`, it must be
  decorated with either `BoundInnerClass` or `UnboundInnerClass`.
  It doesn't want the outer object passed in, so it's decorated
  with `UnboundInnerClass`.
* `ChildOfInner.__init__` calls `super().__init__`.

Note that, because `ChildOfInner` is decorated with `UnboundInnerClass`,
it doesn't take an `outer` parameter.  Nor does it pass in an `outer`
argument when it calls `super().__init__`.  But when the constructor for
`Inner` is called, the correct `outer` parameter is passed in--like magic!
Thanks again, `BoundInnerClass`!

If you wanted `ChildOfInner` to also get the outer argument passed in to
its `__init__`, just decorate it with `BoundInnerClass` instead of
`UnboundInnerClass`, like so:

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
`BoundInnerClass` (and `UnboundInnerClass`) in the test suite.

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

* You must not rename inner classes decorated with either `BoundInnerClass`
  or `UnboundInnerClass`!  The implementation of `BoundInnerClass` looks up
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

**0.5.2**

* Added `stripped_lines` and `rstripped_lines` to the `text` module.
* Added support for `len` to the `graph.TopologicalSorter` object.

**0.5.1**

* Added `gently_title` and `normalize_whitespace` to the `text` module.
* Changed `translate_filename_to_exfat` to handle translating `:` in a special way.
  If the colon is followed by a space, then the colon is turned into " -".
  This yields a more natural translation when colons are used in text, e.g.
  "xXx: The Return Of Xander Cage" -> "xXx - The Return Of Xander Cage".
  If the colon is not followed by a space, turns the colon into "-".
  This is good for tiresome modern gobbledygook like "Re:code" -> "Re-code".

**0.5**

* Initial release.
