![# big](https://raw.githubusercontent.com/larryhastings/big/master/resources/images/big.header.png)

##### Copyright 2022-2026 by Larry Hastings

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
It's the missing batteries Python never shippet.
It's the code you *would* have written... if only you had the time.
And every API is a pleasure to use!

**big** requires Python 3.6 or newer.  It has no
required dependencies to run.  (**big**'s test suite
havs a few external dependencies, but **big** itself will
run fine without them.)
**big** is 100% pure Python code--no C extension
needed, no compilation step.

The current version is [0.13.](#013)

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
[`Log(*destinations, **options)`](#logdestinations-options).
It's easy to write a quick little disposable log function.
I should know; I've done it myself, many times.
But big's `Log` class is feature-rich, thoroughly debugged,
and lightning fast.  Rather than waste your time hacking
together something cheap, just use big!


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

but that's up to you.  Me, I generally use `import big.all as big` .

**big** is licensed using the
[MIT license.](https://opensource.org/licenses/MIT)
You're free to use it and even ship it in your own programs,
as long as you leave my copyright notice on the source code.

## The best of big

Although **big** is *crammed full* of fabulous code, a few of
its subsystems rise above the rest.  If you're curious what
**big** might do for you, here are the six things in **big**
I'm proudest of:

* [**`linked_list`**](#linked_list)
* [**`string`**](#string)
* [**Bound inner classes**](#bound-inner-classes)
* [**The `multi-` family of string functions**](#The-multi--family-of-string-functions)
* [`big.state`](#bigstate)
* [**Enhanced `TopologicalSorter`**](#enhanced-topologicalsorter)

And here are five little functions/classes I use all the time:

* [`eval_template_string`](#eval_template_strings-globals-localsnone--parse_expressionstrue-parse_commentsfalse-parse_whitespace_eaterfalse)
* [`iterator_context`](#iteratorcontext)
* [`Log`](#logdestinations-options)
* [`pushd`](#pushddirectory)
* [`re_partition`](#re_partitiontext-pattern-count1--flags0-reversefalse)


# Index

### Modules

<dl><dd>

[`big.all`](#bigall)

[`big.boundinnerclass`](#bigboundinnerclass)

[`big.builtin`](#bigbuiltin)

[`big.deprecated`](#bigdeprecated)

[`big.file`](#bigfile)

[`big.graph`](#biggraph)

[`big.heap`](#bigheap)

[`big.itertools`](#bigitertools)

[`big.log`](#biglog)

[`big.metadata`](#bigmetadata)

[`big.scheduler`](#bigscheduler)

[`big.state`](#bigstate)

[`big.template`](#bigtemplate)

[`big.text`](#bigtext)

[`big.time`](#bigtime)

[`big.tokens`](#bigtokens)

[`big.types`](#bigtypes)

[`big.version`](#bigversion)

</dd></dl>

### Functions, classes, and values

<dl><dd>

[`accessor(attribute='state', state_manager='state_manager')`](#accessorattributestate-state_managerstate_manager)

[`ascii_linebreaks`](#ascii_linebreaks)

[`ascii_linebreaks_without_crlf`](#ascii_linebreaks_without_crlf)

[`ascii_whitespace`](#ascii_whitespace)

[`ascii_whitespace_without_crlf`](#ascii_whitespace_without_crlf)

[`bound_inner_base(o)`](#bound_inner_baseo)

[`BoundInnerClass`](#boundinnerclasscls)

[`BOUNDINNERCLASS_OUTER_ATTR`](#boundinnerclass_outer_attr)

[`BOUNDINNERCLASS_OUTER_SLOTS`](#boundinnerclass_outer_slots)

[`bound_to(cls)`](#bound_tocls)

[`bytes_linebreaks`](#bytes_linebreaks)

[`bytes_linebreaks_without_crlf`](#bytes_linebreaks_without_crlf)

[`bytes_whitespace`](#bytes_whitespace)

[`bytes_whitespace_without_crlf`](#bytes_whitespace_without_crlf)

[`combine_splits(s, *split_arrays)`](#combine_splitss-split_arrays)

[`ClassRegistry()`](#classregistry)

[`CycleError()`](#cycleerror)

[`date_ensure_timezone(d, timezone)`](#date_ensure_timezoned-timezone)

[`date_set_timezone(d, timezone)`](#date_set_timezoned-timezone)

[`datetime_ensure_timezone(d, timezone)`](#datetime_ensure_timezoned-timezone)

[`datetime_set_timezone(d, timezone)`](#datetime_set_timezoned-timezone)

[`default_clock()`](#default_clock)

[`decode_python_script(script, *, newline=None, use_bom=True, use_source_code_encoding=True)`](#decode_python_scriptscript--newlinenone-use_bomtrue-use_source_code_encodingtrue)

[`Delimiter(close, *, escape='', multiline=True, quoting=False)`](#delimiterclose--escape-multilinetrue-quotingfalse)

[`dispatch(state_manager='state_manager', *, prefix='', suffix='')`](#dispatchstate_managerstate_manager--prefix-suffix)

[`encode_strings(o, *, encoding='ascii')`](#encode_stringso--encodingascii)

[`Event(scheduler, event, time, priority, sequence)`](#eventscheduler-event-time-priority-sequence)

[`Event.cancel()`](#eventcancel)

[`eval_template_string(s, globals, locals=None, *, ...)`](#eval_template_strings-globals-localsnone--parse_expressionstrue-parse_commentsfalse-parse_whitespace_eaterfalse)

[`fgrep(path, text, *, encoding=None, enumerate=False, case_insensitive=False)`](#fgreppath-text--encodingnone-enumeratefalse-case_insensitivefalse)

[`file_mtime(path)`](#file_mtimepath)

[`file_mtime_ns(path)`](#file_mtime_nspath)

[`file_size(path)`](#file_sizepath)

[`format_map(s, mapping)`](#format_maps-mapping)

[`generate_tokens(s)`](#generate_tokenss)

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

[`Heap.popleft_and_append(o)`](#heappopleft_and_appendo)

[`Heap.queue`](#heapqueue)

[`int_to_words(i, *, flowery=True, ordinal=False)`](#int_to_wordsi--flowerytrue-ordinalfalse)

[`Interpolation(expression, *filters, debug='')`](#interpolationexpression-filters-debug)

[`is_bound(cls)`](#is_boundcls)

[`is_boundinnerclass(cls)`](#is_boundinnerclasscls)

[`is_unboundinnerclass(cls)`](#is_unboundinnerclasscls)

[`IteratorContext`](#iterator_contextiterator-start0)

[`iterator_context(iterator, start=0)`](#iterator_contextiterator-start0)

[`iterator_filter(iterator, *, ...)`](#iterator_filteriterator--stop_at_valueundefined-stop_at_innone-stop_at_predicatenone-stop_at_countnone-reject_valueundefined-reject_innone-reject_predicatenone-only_valueundefined-only_innone-only_predicatenone)

[`linebreaks`](#linebreaks)

[`linebreaks_without_crlf`](#linebreaks_without_crlf)

[`linked_list(iterable=(), *, lock=None)`](#linked_listiterable--locknone)

[`linked_list.append(object)`](#linked_listappendobject)

[`linked_list.clear()`](#linked_listclear)

[`linked_list.copy(*, lock=None)`](#linked_listcopy-locknone)

[`linked_list.count(value)`](#linked_listcountvalue)

[`linked_list.cut(start=None, stop=None, *, lock=None)`](#linked_listcutstartnone-stopnone--locknone)

[`linked_list.extend(iterable)`](#linked_listextenditerable)

[`linked_list.extendleft(iterable)`](#linked_listextendleftiterable)

[`linked_list.find(value)`](#linked_listfindvalue)

[`linked_list.index(value, start=0, stop=sys.maxsize)`](#linked_listindexvalue-start0-stopsysmaxsize)

[`linked_list.insert(index, object)`](#linked_listinsertindex-object)

[`linked_list.match(predicate)`](#linked_listmatchpredicate)

[`linked_list.pop(index=-1)`](#linked_listpopindex-1)

[`linked_list.prepend(object)`](#linked_listprependobject)

[`linked_list.rcount(value)`](#linked_listrcountvalue)

[`linked_list.rcut(start=None, stop=None, *, lock=None)`](#linked_listrcutstartnone-stopnone--locknone)

[`linked_list.remove(value, default=undefined)`](#linked_listremovevalue-defaultundefined)

[`linked_list.reverse()`](#linked_listreverse)

[`linked_list.rextend(iterable)`](#linked_listrextenditerable)

[`linked_list.rfind(value)`](#linked_listrfindvalue)

[`linked_list.rmatch(predicate)`](#linked_listrmatchpredicate)

[`linked_list.rotate(n)`](#linked_listrotaten)

[`linked_list.rpop(index=0)`](#linked_listrpopindex0)

[`linked_list.rremove(value, default=undefined)`](#linked_listrremovevalue-defaultundefined)

[`linked_list.rsplice(other, *, where=None)`](#linked_listrspliceother--wherenone)

[`linked_list.sort(key=None, reverse=False)`](#linked_listsortkeynone-reversefalse)

[`linked_list.splice(other, *, where=None)`](#linked_listspliceother--wherenone)

[`linked_list.tail()`](#linked_listtail)

[`linked_list_iterator`](#linked_list_iterator)

[`linked_list_iterator.after(count=1)`](#linked_list_iteratoraftercount1)

[`linked_list_iterator.append(value)`](#linked_list_iteratorappendvalue)

[`linked_list_iterator.before(count=1)`](#linked_list_iteratorbeforecount1)

[`linked_list_iterator.copy()`](#linked_list_iteratorcopy)

[`linked_list_iterator.count(value)`](#linked_list_iteratorcountvalue)

[`linked_list_iterator.cut(stop=None, *, lock=None)`](#linked_list_iteratorcutstopnone--locknone)

[`linked_list_iterator.exhaust()`](#linked_list_iteratorexhaust)

[`linked_list_iterator.extend(iterable)`](#linked_list_iteratorextenditerable)

[`linked_list_iterator.find(value)`](#linked_list_iteratorfindvalue)

[`linked_list_iterator.insert(index, object)`](#linked_list_iteratorinsertindex-object)

[`linked_list_iterator.is_special()`](#linked_list_iteratoris_special)

[`linked_list_iterator.linked_list`](#linked_list_iteratorlinked_list)

[`linked_list_iterator.match(predicate)`](#linked_list_iteratormatchpredicate)

[`linked_list_iterator.next(default=undefined, *, count=1)`](#linked_list_iteratornextdefaultundefined--count1)

[`linked_list_iterator.pop(index=0)`](#linked_list_iteratorpopindex0)

[`linked_list_iterator.prepend(value)`](#linked_list_iteratorprependvalue)

[`linked_list_iterator.previous(default=undefined, *, count=1)`](#linked_list_iteratorpreviousdefaultundefined--count1)

[`linked_list_iterator.rcount(value)`](#linked_list_iteratorrcountvalue)

[`linked_list_iterator.rcut(stop=None, *, lock=None)`](#linked_list_iteratorrcutstopnone--locknone)

[`linked_list_iterator.remove(value, default=undefined)`](#linked_list_iteratorremovevalue-defaultundefined)

[`linked_list_iterator.reset()`](#linked_list_iteratorreset)

[`linked_list_iterator.rextend(iterable)`](#linked_list_iteratorrextenditerable)

[`linked_list_iterator.rfind(value)`](#linked_list_iteratorrfindvalue)

[`linked_list_iterator.rmatch(predicate)`](#linked_list_iteratorrmatchpredicate)

[`linked_list_iterator.rpop(index=0)`](#linked_list_iteratorrpopindex0)

[`linked_list_iterator.rremove(value, default=undefined)`](#linked_list_iteratorrremovevalue-defaultundefined)

[`linked_list_iterator.rsplice(other)`](#linked_list_iteratorrspliceother)

[`linked_list_iterator.rtruncate()`](#linked_list_iteratorrtruncate)

[`linked_list_iterator.special()`](#linked_list_iteratorspecial)

[`linked_list_iterator.splice(other)`](#linked_list_iteratorspliceother)

[`linked_list_iterator.truncate()`](#linked_list_iteratortruncate)

[`linked_list_node`](#linked_list_node)

[`linked_list_reverse_iterator`](#linked_list_reverse_iterator)

[`linked_list_reverse_iterator.after(count=1)`](#linked_list_reverse_iteratoraftercount1)

[`linked_list_reverse_iterator.append(value)`](#linked_list_reverse_iteratorappendvalue)

[`linked_list_reverse_iterator.before(count=1)`](#linked_list_reverse_iteratorbeforecount1)

[`linked_list_reverse_iterator.copy()`](#linked_list_reverse_iteratorcopy)

[`linked_list_reverse_iterator.count(value)`](#linked_list_reverse_iteratorcountvalue)

[`linked_list_reverse_iterator.cut(stop=None, *, lock=None)`](#linked_list_reverse_iteratorcutstopnone--locknone)

[`linked_list_reverse_iterator.exhaust()`](#linked_list_reverse_iteratorexhaust)

[`linked_list_reverse_iterator.extend(iterable)`](#linked_list_reverse_iteratorextenditerable)

[`linked_list_reverse_iterator.find(value)`](#linked_list_reverse_iteratorfindvalue)

[`linked_list_reverse_iterator.insert(index, object)`](#linked_list_reverse_iteratorinsertindex-object)

[`linked_list_reverse_iterator.is_special()`](#linked_list_reverse_iteratoris_special)

[`linked_list_reverse_iterator.linked_list`](#linked_list_reverse_iteratorlinked_list)

[`linked_list_reverse_iterator.match(predicate)`](#linked_list_reverse_iteratormatchpredicate)

[`linked_list_reverse_iterator.next(default=undefined, *, count=1)`](#linked_list_reverse_iteratornextdefaultundefined--count1)

[`linked_list_reverse_iterator.pop(index=0)`](#linked_list_reverse_iteratorpopindex0)

[`linked_list_reverse_iterator.prepend(value)`](#linked_list_reverse_iteratorprependvalue)

[`linked_list_reverse_iterator.previous(default=undefined, *, count=1)`](#linked_list_reverse_iteratorpreviousdefaultundefined--count1)

[`linked_list_reverse_iterator.rcount(value)`](#linked_list_reverse_iteratorrcountvalue)

[`linked_list_reverse_iterator.rcut(stop=None, *, lock=None)`](#linked_list_reverse_iteratorrcutstopnone--locknone)

[`linked_list_reverse_iterator.remove(value, default=undefined)`](#linked_list_reverse_iteratorremovevalue-defaultundefined)

[`linked_list_reverse_iterator.reset()`](#linked_list_reverse_iteratorreset)

[`linked_list_reverse_iterator.rextend(iterable)`](#linked_list_reverse_iteratorrextenditerable)

[`linked_list_reverse_iterator.rfind(value)`](#linked_list_reverse_iteratorrfindvalue)

[`linked_list_reverse_iterator.rmatch(predicate)`](#linked_list_reverse_iteratorrmatchpredicate)

[`linked_list_reverse_iterator.rpop(index=0)`](#linked_list_reverse_iteratorrpopindex0)

[`linked_list_reverse_iterator.rremove(value, default=undefined)`](#linked_list_reverse_iteratorrremovevalue-defaultundefined)

[`linked_list_reverse_iterator.rsplice(other)`](#linked_list_reverse_iteratorrspliceother)

[`linked_list_reverse_iterator.rtruncate()`](#linked_list_reverse_iteratorrtruncate)

[`linked_list_reverse_iterator.special()`](#linked_list_reverse_iteratorspecial)

[`linked_list_reverse_iterator.splice(other)`](#linked_list_reverse_iteratorspliceother)

[`linked_list_reverse_iterator.truncate()`](#linked_list_reverse_iteratortruncate)

[`Log(*destinations, **options)`](#logdestinations-options)

[`Log.box(s)`](#logboxs)

[`Log.Callable(callable)`](#logcallablecallable)

[`Log.close(block=True)`](#logcloseblocktrue)

[`Log.Destination`](#logdestination)

[`Log.Destination.Buffer(destination=None)`](#logdestinationbufferdestinationnone)

[`Log.enter(message)`](#logentermessage)

[`Log.exit()`](#logexit)

[`Log.File(path, initial_mode="at", *, flush=False)`](#logfilepath-initial_modeat--flushfalse)

[`Log.FileHandle(handle, *, flush=False)`](#logfilehandlehandle--flushfalse)

[`Log.flush(block=True)`](#logflushblocktrue)

[`Log.List(list)`](#loglistlist)

[`Log.map_destination(o)`](#logmap_destinationo)

[`Log.print(*args, end='\n', sep=' ', flush=False, format='print')`](#logprintargs-endn-sep--flushfalse-formatprint)

[`Log.Print()`](#logprint)

[`Log.reset()`](#logreset)

[`Log.Sink()`](#logsink)

[`Log.TmpFile(*, flush=False)`](#logtmpfile-flushfalse)

[`Log.write(formatted)`](#logwriteformatted)

[`merge_columns(*columns, column_separator=" ", overflow_response=OverflowResponse.RAISE, overflow_before=0, overflow_after=0)`](#merge_columnscolumns-column_separator--overflow_responseoverflowresponseraise-overflow_before0-overflow_after0)

[`metadata.version`](#metadataversion)

[`ModuleManager()`](#modulemanager)

[`multipartition(s, separators, count=1, *, reverse=False, separate=True)`](#multipartitions-separators-count1--reversefalse-separatetrue)

[`multisplit(s, separators, *, keep=False, maxsplit=-1, reverse=False, separate=False, strip=False)`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)

[`multistrip(s, separators, left=True, right=True)`](#multistrips-separators-lefttrue-righttrue)

[`normalize_whitespace(s, separators=None, replacement=None)`](#normalize_whitespaces-separatorsnone-replacementnone)

[`OldDestination()`](#olddestination)

[`OldLog(clock=None)`](#oldlogclocknone)

[`parse_template_string(s, *, ...)`](#parse_template_strings--parse_expressionstrue-parse_commentsfalse-parse_statementsfalse-parse_whitespace_eaterfalse-quotes--multiline_quotes-escape)

[`parse_timestamp_3339Z(s, *, timezone=None)`](#parse_timestamp_3339zs--timezonenone)

[`Pattern(s, flags=0)`](#patterns-flags0)

[`pure_virtual()`](#pure_virtual)

[`PushbackIterator(iterable=None)`](#pushbackiteratoriterablenone)

[`PushbackIterator.next(default=None)`](#pushbackiteratornextdefaultnone)

[`PushbackIterator.push(o)`](#pushbackiteratorpusho)

[`prefix_format(time_seconds_width, time_fractional_width, thread_name_width=12)`](#prefix_formattime_seconds_width-time_fractional_width-thread_name_width12)

[`pushd(directory)`](#pushddirectory)

[`python_delimiters`](#python_delimiters)

[`python_delimiters_version`](#python_delimiters_version)

[`read_python_file(path, *, newline=None, use_bom=True, use_source_code_encoding=True)`](#read_python_filepath--newlinenone-use_bomtrue-use_source_code_encodingtrue)

[`re_partition(text, pattern, count=1, *, flags=0, reverse=False)`](#re_partitiontext-pattern-count1--flags0-reversefalse)

[`re_rpartition(text, pattern, count=1, *, flags=0)`](#re_rpartitiontext-pattern-count1--flags0)

[`Regulator()`](#regulator)

[`Regulator.lock`](#regulatorlock)

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

[`search_path(paths, extensions=('',), *, case_sensitive=None, preserve_extension=True, want_directories=False, want_files=True)`](#search_pathpaths-extensions--case_sensitivenone-preserve_extensiontrue-want_directoriesfalse-want_filestrue)

[`SingleThreadedRegulator()`](#singlethreadedregulator)

[`split_delimiters(s, delimiters={...}, *, state=(), yields=None)`](#split_delimiterss-delimiters--state-yieldsnone)

[`split_quoted_strings(s, quotes=('"', "'"), *, escape='\\', multiline_quotes=(), state='')`](#split_quoted_stringss-quotes---escape-multiline_quotes-state)

[`split_text_with_code(s, *, tab_width=8, allow_code=True, code_indent=4, convert_tabs_to_spaces=True)`](#split_text_with_codes--tab_width8-allow_codetrue-code_indent4-convert_tabs_to_spacestrue)

[`split_title_case(s, *, split_allcaps=True)`](#split_title_cases--split_allcapstrue)

[`SinkEvent`](#sinkevent)

[`SinkEndEvent`](#sinkendevent)

[`SinkEnterEvent`](#sinkenterevent)

[`SinkExitEvent`](#sinkexitevent)

[`SinkLogEvent`](#sinklogevent)

[`SinkStartEvent`](#sinkstartevent)

[`SinkWriteEvent`](#sinkwriteevent)

[`SpecialNodeError`](#specialnodeerror)

[`State()`](#state)

[`StateManager(state, *, on_enter='on_enter', on_exit='on_exit', state_class=None)`](#statemanagerstate--on_enteron_enter-on_exiton_exit-state_classnone)

[`Statement(statement)`](#statementstatement)

[`string(s='', *, ...)`](#strings--sourcenone-line_number1-column_number1-first_column_number1-tab_width8)

[`string.bisect(index)`](#stringbisectindex)

[`string.cat(*strings)`](#stringcatstrings)

[`string.compile(flags=0)`](#stringcompileflags0)

[`string.generate_tokens()`](#stringgenerate_tokens)

[`strip_indents(lines, *, tab_width=8, linebreaks=linebreaks)`](#strip_indentslines--tab_width8-linebreakslinebreaks)

[`strip_line_comments(lines, line_comment_markers, *, escape='\\', quotes=(), multiline_quotes=(), linebreaks=linebreaks)`](#strip_line_commentslines-line_comment_markers--escape-quotes-multiline_quotes-linebreakslinebreaks)

[`str_linebreaks`](#str_linebreaks)

[`str_linebreaks_without_crlf`](#str_linebreaks_without_crlf)

[`str_whitespace`](#str_whitespace)

[`str_whitespace_without_crlf`](#str_whitespace_without_crlf)

[`timestamp_3339Z(t=None, want_microseconds=None)`](#timestamp_3339ztnone-want_microsecondsnone)

[`timestamp_human(t=None, want_microseconds=None, *, tzinfo=None)`](#timestamp_humantnone-want_microsecondsnone--tzinfonone)

[`ThreadSafeRegulator()`](#threadsaferegulator)

[`TMPFILE`](#tmpfile)

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

[`type_bound_to(instance)`](#type_bound_toinstance)

[`unbound(cls)`](#unboundcls)

[`UnboundInnerClass`](#unboundinnerclasscls)

[`UndefinedIndexError`](#undefinedindexerror)

[`unicode_linebreaks`](#unicode_linebreaks)

[`unicode_linebreaks_without_crlf`](#unicode_linebreaks_without_crlf)

[`unicode_whitespace`](#unicode_whitespace)

[`unicode_whitespace_without_crlf`](#unicode_whitespace_without_crlf)

[`Version(s=None, *, epoch=None, release=None, release_level=None, serial=None, post=None, dev=None, local=None)`](#versionsnone--epochnone-releasenone-release_levelnone-serialnone-postnone-devnone-localnone)

[`Version.format(s)`](#versionformats)

[`whitespace`](#whitespace)

[`whitespace_without_crlf`](#whitespace_without_crlf)

[`wrap_words(words, margin=79, *, two_spaces=True)`](#wrap_wordswords-margin79--two_spacestrue)

</dd></dl>

### Tutorials

<dl><dd>

[**The `multi-` family of string functions**](#The-multi--family-of-string-functions)

[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)

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

When I'm using big in my own projects, I tend to import it as

```Python
import big.all as big
```

That way, all big's symbols are available as one big flat namespace.


</dd></dl>

## `big.boundinnerclass`

<dl><dd>

Class decorators that implement bound inner classes.  See the
[**Bound inner classes**](#bound-inner-classes)
tutorial for more information.

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

#### `bound_inner_base(o)`

<dl><dd>
Simple wrapper for Python 3.6 compatibility for bound inner classes.

Returns the base class for declaring a subclass of a
bound inner class while still in the outer class scope.
Only needed for Python 3.6 compatibility; unnecessary
in Python 3.7+, or when the child class is defined
after exiting the outer class scope.

See the [**Bound inner classes**](#bound-inner-classes) tutorial for more information.
</dd></dl>

#### `bound_to(cls)`

<dl><dd>

Returns the outer instance that `cls` is bound to, or `None`.

If `cls` is a bindable inner class that was bound to an outer
instance, returns that outer instance.  If `cls` is any other
variety of type object, returns `None`.  Raises `TypeError` if
`cls` is not a class object.

[`BoundInnerClass`](#boundinnerclasscls) doesn't keep strong
references to outer instances.  If `cls` was bound to an object
that has since been destroyed, `bound_to` will return `None`.

See the [**Bound inner classes**](#bound-inner-classes) tutorial for more information.
</dd></dl>

#### `BOUNDINNERCLASS_OUTER_ATTR`

<dl><dd>

A string constant containing the attribute name that
[`BoundInnerClass`](#boundinnerclasscls) uses to store
its per-instance cache on the outer instance.
If your outer class uses `__slots__`, you must include
this attribute in your slots definition.

However, rather than using this attribute directly,
we suggest you use [`BOUNDINNERCLASS_OUTER_SLOTS`](#boundinnerclass_outer_slots)
to add the necessary attribute to your `__slots__` tuple.

See the [**Bound inner classes**](#bound-inner-classes) tutorial for more information.
</dd></dl>

#### `BOUNDINNERCLASS_OUTER_SLOTS`

<dl><dd>

A tuple containing [`BOUNDINNERCLASS_OUTER_ATTR`](#boundinnerclass_outer_attr).
If your outer class uses `__slots__`, you can add this to your
slots definition to ensure [`BoundInnerClass`](#boundinnerclasscls) works correctly.

Example:

```Python
class Foo:
    __slots__ = ('x', 'y', 'z') + BOUNDINNERCLASS_SLOTS

    @BoundInnerClass
    class Bar:
        ...
```

See the [**Bound inner classes**](#bound-inner-classes) tutorial for more information.
</dd></dl>

#### `is_bound(cls)`

<dl><dd>

Returns `True` if `cls` is a bound inner class that has been
bound to a specific outer instance.  Said another way,
`is_bound(cls)` returns `True` if
[`bound_to(cls)`](#bound_tocls) would return a non-`None` value.

Returns `False` for unbound inner classes and non-participating classes.
Raises `TypeError` if `cls` is not a class object.

See the [**Bound inner classes**](#bound-inner-classes) tutorial for more information.
</dd></dl>

#### `is_boundinnerclass(cls)`

<dl><dd>

Returns `True` if `cls` was decorated with
[`@BoundInnerClass`](#boundinnerclasscls),
or is a bound wrapper class created from one.

Returns `False` for [`@UnboundInnerClass`](#unboundinnerclasscls)
classes and regular classes.
Raises `TypeError` if `cls` is not a class object.

See the [**Bound inner classes**](#bound-inner-classes) tutorial for more information.
</dd></dl>

#### `is_unboundinnerclass(cls)`

<dl><dd>

Returns `True` if `cls` was decorated with
[`@UnboundInnerClass`](#unboundinnerclasscls),
or is a wrapper class created from one.

Returns `False` for [`@BoundInnerClass`](#boundinnerclasscls)
classes and regular classes.
Raises `TypeError` if `cls` is not a class object.

See the [**Bound inner classes**](#bound-inner-classes) tutorial for more information.
</dd></dl>

#### `type_bound_to(instance)`

<dl><dd>

Returns the outer instance that `type(instance)` is bound to, or `None`.

This is a convenience function equivalent to calling
[`bound_to(type(instance))`](#bound_tocls).

[`BoundInnerClass`](#boundinnerclasscls) doesn't keep strong
references to outer instances.  If `type(instance)` was bound
to an object that has since been destroyed, `type_bound_to`
will return `None`.

See the [**Bound inner classes**](#bound-inner-classes) tutorial for more information.
</dd></dl>

#### `unbound(cls)`

<dl><dd>

Returns the unbound version of a bound class.

If `cls` is a bound inner class, returns the original unbound class.
If `cls` is already unbound (or not a bindable inner class), returns `cls`.

Raises `ValueError` if `cls` inherits directly from a bound class
(e.g. `class Child(o.Inner)`), since such classes have no unbound
version.  Raises `TypeError` if `cls` is not a class object.

See the [**Bound inner classes**](#bound-inner-classes) tutorial for more information.
</dd></dl>


## `big.builtin`

<dl><dd>

Fundamental functions and types that don't fit neatly into
any other submodule.  (Named `builtin` to avoid a name collision
with Python's `builtins` module.)

</dd></dl>

#### `ClassRegistry()`

<dl><dd>

A `dict` subclass with attribute-style access, useful as
a class decorator for registering base classes.

[`BoundInnerClass`](#boundinnerclasscls) encourages heavily-nested
classes, but Python's scoping rules make it clumsy to reference
base classes defined in a different class scope.  `ClassRegistry`
solves this by giving you a place to store references to base
classes you can access later.

To use, create a `ClassRegistry` instance, then use it as a
decorator to register classes.  Access registered classes as
attributes on the `ClassRegistry`.  By default the class's
`__name__` is used as the attribute name; pass a string argument
to use a custom name instead.

When using with [`BoundInnerClass`](#boundinnerclasscls), put
`@base()` *above* `@BoundInnerClass`.
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

#### `ModuleManager()`

<dl><dd>

A class that manages your module's namespace, including `__all__`.

`ModuleManager` makes it easy to populate `__all__` and clean up
temporary symbols.  Instantiate a `ModuleManager` at module scope,
use its methods to declare exports and deletions, then call the
instance at the end of your module to finalize.

`ModuleManager` provides two methods, both of which can be used
as decorators or called with string arguments:

`mm.export(*args)` adds symbols to `__all__`.  When used as a
decorator, adds the decorated function or class by name.  When
called with strings, adds those strings to `__all__`.

`mm.delete(*args)` marks symbols for deletion.  When used as a
decorator, marks the decorated function or class for deletion.
When called with strings, marks those names for deletion.

When the `ModuleManager` instance is called, it deletes all
symbols on the deletions list from the module namespace.
It also automatically deletes itself, and any module-level
references to its `export` and `delete` methods.
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

#### `read_python_file(path, *, newline=None, use_bom=True, use_source_code_encoding=True)`

<dl><dd>

Opens, reads, and correctly decodes a Python script from a file.

`path` should specify the filesystem path to the file; it can
be any object accepted by `builtins.open` (a "path-like object").

Returns a `str` containing the decoded Python script.

Opens the file using `builtins.open`.

Decodes the script using big's `decode_python_script` function.
The `newline`, `use_bom` and `use_source_code_encoding`
parameters are passed through to that function.

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


#### `search_path(paths, extensions=('',), *, case_sensitive=None, preserve_extension=True, want_directories=False, want_files=True)`

<dl><dd>

Search a list of directories for a file.  Given a sequence
of directories, an optional list of file extensions, and a
filename, searches those directories for a file with that
name and possibly one of those file extensions.

`search_path` accepts the paths and extensions as parameters and
returns a *search function*.  The search function accepts one
`filename` parameter and performs the search, returning either the
path to the file it found (as a `pathlib.Path` object) or `None`.
You can reuse the search function to perform as many searches
as you like.

`paths` should be an iterable of `str` or `pathlib.Path` objects
representing directories.  These may be relative or absolute
paths; relative paths will be relative to the current directory
at the time the search function is run.  Specifying a directory
that doesn't exist is not an error.

`extensions` should be an iterable of `str` objects representing
extensions.  Every non-empty extension specified should start
with a period (`'.'`) character (technically `os.extsep`).  You
may specify at most one empty string in extensions, which
represents testing the filename without an additional
extension.  By default `extensions` is the tuple `('',)``.
Extension strings may contain additional period characters
after the initial one.

Shell-style "globbing" isn't supported for any parameter.  Both
the filename and the extension strings may contain filesystem
globbing characters, but they will only match those literal
characters themselves.  (`'*'` won't match any character, it'll
only match a literal `'*'` in the filename or extension.)

`case_sensitive` works like the parameter to `pathlib.Path.glob`.
If `case_sensitive` is true, files found while searching must
match the filename and extension exactly.  If `case_sensitive`
is false, the comparison is done in a case-insensitive manner.
If `case_sensitive` is `None` (the default), case sensitivity obeys
the platform default (as per `os.path.normcase`).  In practice,
only Windows platforms are case-insensitive by convention;
all other platforms that support Python are case-sensitive
by convention.

If `preserve_extension` is true (the default), the search function
checks the filename to see if it already ends with one of the
extensions.  If it does, the search is restricted to only files
with that extension--the other extensions are ignored.  This
check obeys the `case_sensitive` flag; if `case_sensitive` is None,
this comparison is case-insensitive only on Windows.

`want_files` and `want_directories` are boolean values; the
search function  will only return that type of file if the
corresponding *want_* parameter is true.  You can request files,
directories, or both.  (`want_files` and `want_directories`
can't both be false.)  By default, `want_files` is true and
`want_directories` is false.

`paths` and `extensions` are both tried in order, and the search
function returns the first match it finds.  All extensions are
tried in a path entry before considering the next path.

Returns a function:

```Python
    search(filename)
```

which returns either a `pathlib.Path` object on success or `None`
on failure.

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

See the [**Enhanced `TopologicalSorter`**](#enhanced-topologicalsorter) tutorial for more information.

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

</dd></dl>

#### `iterator_context(iterator, start=0)`

<dl><dd>

Iterates over `iterable`.  Yields `(ctx, o)` where `o`
is each value yielded by `iterable`, and `ctx` is a
"context" variable of type `IteratorContext`
containing metadata about the iteration.

`ctx` supports the following attributes:

</dd><dt>
`ctx.countdown`
</dt><dd>
   contains the "opposite" value of `ctx.index`.
   The values yielded by `ctx.countdown` are the same as
   `ctx.index`, but in reversed order.  (If `start` is 0,
   and the iterator yields four items, `ctx.index` will
   be `0`, `1`, `2`, and `3` in that order, and `ctx.countdown`
   will be `3`, `2`, `1`, and `0` in that order.)  `ctx.countdown`
   requires the iterator to support `__len__`; if it doesn't,
   `ctx.countdown` will be undefined.
</dd><dt>
`ctx.current`
</dt><dd>
   contains the current value yielded by the
   iterator (`o` as described above).
</dd><dt>
`ctx.index`
</dt><dd>
   contains the index of this value.  The first
   time the iterator yields a value, this will be `start`;
   the second time, it will be `start + 1`, etc.
<dl><dt>
`ctx.is_first`
</dt><dd>
   is true only for the first value yielded,
   and false otherwise.
</dd><dt>
`ctx.is_last`
</dt><dd>
   is true only for the last value yielded,
   and false otherwise.  (If the iterator only yields
   one value, `is_first` and `is_last` will both be true.)
</dd><dt>
`ctx.length`
</dt><dd>
   contain the total number of items that will be yielded.
   `ctx.length` requires the iterator to support `__len__`;
   if it doesn't, `ctx.length` will be undefined.
</dd><dt>
`ctx.next`
</dt><dd>
   contains the next value to be yielded by
   this iterator if there is one.  (If `o` is the last
   value yielded by the iterator, `ctx.previous` will be
   an `undefined` value.)
</dd><dt>
`ctx.previous`
</dt><dd>
   contains the previous value yielded if
   this is the second or subsequent time this iterator
   has yielded a value.  (If this is the first time
   the iterator has yielded, `ctx.previous` will be
   an `undefined` value.)
</dd>

</dd></dl>

#### `iterator_filter(iterator, *, stop_at_value=undefined, stop_at_in=None, stop_at_predicate=None, stop_at_count=None, reject_value=undefined, reject_in=None, reject_predicate=None, only_value=undefined, only_in=None, only_predicate=None)`

<dl><dd>

Wraps any iterator, filtering the values it yields based on rules
you specify as keyword-only parameters.

There are three categories of rules, examined in order:

*"stop_at"* rules cause the iterator to become exhausted.
If a value passes a "stop_at" rule, the iterator immediately
becomes exhausted without yielding that value.

*"reject"* rules act as a blacklist.  If a value passes any
"reject" rule, it's discarded and iteration continues.

*"only"* rules act as a whitelist.  If a value doesn't pass
all "only" rules, it's discarded and iteration continues.

Each category supports three suffix variants that define the test:

A rule ending in `_value` passes if the yielded value `==` the argument.

A rule ending in `_in` passes if the yielded value is `in` the argument
(which must support the `in` operator).

A rule ending in `_predicate` takes a callable as its argument; it passes
if calling the argument with the yielded value returns a true value.

There is one additional rule: `stop_at_count`, an integer.  The iterator
becomes exhausted after yielding `stop_at_count` items.  If `stop_at_count`
is initially `<= 0`, the iterator is initialized in an exhausted state.
</dd></dl>

#### `PushbackIterator(iterable=None)`

<dl><dd>

Wraps any iterator, letting you push items to be yielded first.

The `PushbackIterator` constructor accepts one argument, an iterable.
When you iterate over the `PushbackIterator` instance, it yields values
from that iterable.  You may also pass in `None`, in which case the
`PushbackIterator` is created in an *"exhausted"* state.

`PushbackIterator` also supports a `push(o)`` method, which "pushes"
that object onto the iterator.  If any objects have been pushed onto
the iterator, they're yielded first, before attempting to yield
from the wrapped iterator.  Pushed values are yielded in
first-in-first-out order, like a stack.

When the wrapped iterable is exhausted, you can still call push
to add new items, at which point the `PushbackIterator` can be
iterated over again.
</dd></dl>

#### `PushbackIterator.next(default=None)`

<dl><dd>

Equivalent to `next(PushbackIterator)`, but won't raise
`StopIteration`. If the iterator is exhausted,
returns the `default` argument.
</dd></dl>

#### `PushbackIterator.push(o)`

<dl><dd>

Pushes a value into the iterator's internal stack.
When a `PushbackIterator` is iterated over, and there are
any pushed values, the top value on the stack will be popped
and yielded.  `PushbackIterator` only yields from the
iterator it wraps when this internal stack is empty.

Example: you have a pushback iterator `J`, and you call `J.push(3)`
followed by `J.push('x')`.  The next two times you iterate over
`J`, it will yield `'x'`, followed by `3`.

It's explicitly supported to push values that were never yielded by
the wrapped iterator.  If you create `J = PushbackIterator(range(1, 20))`,
you may still call `J.push(33)`, or `J.push('xyz')`, or `J.push(None)`, etc.
</dd></dl>


## `big.log`

<dl><dd>

A lightweight, high-performance text-based logging module,
intended for debug-print-style use.  Not a full-fledged
application logger like Python's
[`logging`](https://docs.python.org/3/library/logging.html) module.

`Log` is flexible in where output is written (stdout, files,
lists, arbitrary callables, or custom
[`Destination`](#logdestination) objects)
and when (by default it runs in a background thread for
minimal overhead).

See the [**The big `Log`**](#the-big-log) tutorial for an
introduction and examples.

</dd></dl>

#### `default_clock()`

<dl><dd>

The default clock function used by [`Log`](#logdestinations-options).
Returns the current time, expressed as integer nanoseconds (>= 0)
since some earlier event.

In Python 3.7+, this is
[`time.monotonic_ns`](https://docs.python.org/3/library/time.html#time.monotonic_ns).
In Python 3.6 this is a compatibility function that calls
[`time.monotonic`](https://docs.python.org/3/library/time.html#time.monotonic)
and converts the result to integer nanoseconds.
</dd></dl>

#### `Log(*destinations, **options)`

<dl><dd>

A lightweight, high-performance text-based log object
intended for debug-print-style use.  To use, create
a `Log` instance, then call it to log messages:

```Python
    j = Log()
    j("Hello, world!")
```

Calling the `Log` instance is equivalent to calling
[`Log.print`](#logprintargs-end-sep--flushfalse-formatprint).

`Log` has three states: *initial* (just created or reset),
*logging* (actively accepting messages), and *closed*
(ignoring all writes).  The log transitions from initial
to logging automatically the first time a message is logged.

**Destinations**

Positional arguments to the `Log` constructor define destinations
for log messages.  The log sends every formatted message to
every destination.

If you construct a `Log` and don't specify any positional arguments,
it will send logged messages to `builtins.print`.

Destinations can be any of the following:

`print` (or `builtins.print`) — Log messages are printed using
`print(s, end='')`.  Equivalent to
[`Log.Print()`](#logprint).

`str` or `pathlib.Path` — Log messages are buffered locally
and written to the named file.  Equivalent to
[`Log.File(path)`](#logfilepath-initial_modeat--flushfalse).

`list` — Log messages are appended to the list.  Equivalent to
[`Log.List(list)`](#loglistlist).

`io.TextIOBase` — Log messages are written to the file-like object.
Equivalent to
[`Log.FileHandle(handle)`](#logfilehandlehandle).

`callable` — The callable is called with every formatted log message.
Equivalent to
[`Log.Callable(callable)`](#logcallablecallable).

[`TMPFILE`](#tmpfile) — A special sentinel value.  Log messages are
written to a timestamped temporary file.

[`Log.Destination`](#logdestination) — Used directly as a destination.

You can also call [`Log.map_destination`](#logmap_destinationo)
to manually convert any of the above types to the appropriate
`Destination` object.

**Keyword-only options**

Keyword-only parameters for the `Log` constructor
specify configuration for the log.  `Log` accepts
the following keyword-only parameters:

`name` — The name for this log.  Default is `'Log'`.

`threading` — If true (the default), log messages are sent to
a background thread for formatting and writing, reducing
overhead in the calling thread.  If false, messages are
formatted and written immediately, using a lock for thread
safety.  `Log` is always thread-safe regardless of this setting.

`indent` — Number of spaces to indent per nesting level when
using [`Log.enter`](#logentermessage).  Default is `4`.

`width` — Width in characters used for formatting separator
lines.  Default is `79`.

`clock` — A function returning nanoseconds since some
arbitrary past event, expressed as an integer.
Default is [`default_clock`](#default_clock).

`timestamp_clock` — A function returning seconds
since the UNIX epoch, expressed as a float.
Default is `time.time`.

`timestamp_format` — A function that formats values
returned by `timestamp_clock` into a human-readable
string.  Default is [`big.time.timestamp_human`](#timestamp_humantnone-want_microsecondsnone--tzinfonone).

`prefix` — A format string used to format text inserted at the
beginning of every log message.  Default is
[`prefix_format(3, 10, 12)`](#prefix_formattime_seconds_width-time_fractional_width-thread_name_width12).

`formats` — A dict mapping format names to format dicts.
A format dict has a `"template"` key (a template string with
`{}`-style placeholders) and an optional `"line"` key (a fill
character for separator lines).
`Log` has six built-in formats: `"print"`, `"box"`, `"enter"`,
`"exit"`, `"start"`, and `"end"`.  User-defined formats are
automatically added as methods on the `Log` instance.  To
suppress the initial or final log messages, set `"start"` or
`"end"` to `None` in the formats dict.

All keyword-only options are also available as read-only
properties on the `Log` instance.

**Read-only properties**

In addition to the constructor options above, `Log` exposes
these read-only properties:

`dirty` — `True` if any formatted text has been written to the
log since it was started or last flushed.

`closed` — `True` if the log is in the "closed" state.

`start_time_ns` — The time reported by `Log.clock`
when the log was started, in nanoseconds.

`start_time_epoch` — The wall-clock time reported by
`Log.timestamp_clock` when the log was
started, as seconds since the UNIX epoch.

`end_time_epoch` — The wall-clock time when the log was
closed, as seconds since the UNIX epoch.

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `Log.box(s)`

<dl><dd>

Logs `s` to the log, formatted with a three-sided box around
it to call attention to the message.

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `Log.close(block=True)`

<dl><dd>

Closes the log.  This ensures the log is in the "closed" state,
in which all writes are silently ignored.  To write to the log
again after closing, call [`Log.reset()`](#logreset).

* If the log is in "logging" state, it gets closed.
* If the log is in "initial" state, it gets opened then immediately closed.
* If the log is already "closed", this is a no-op.

If `block` is true (the default), `close` won't return
until after the log is fully closed.  If false, the log
may be closed asynchronously.

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `Log.enter(message)`

<dl><dd>

Logs `message` to the log formatted with a box, then indents
subsequent log output.  Call [`Log.exit()`](#logexit) to
outdent.  Nesting may be arbitrarily deep.

`Log.enter` returns a context manager; if used with a `with`
statement, [`Log.exit()`](#logexit) will be called automatically
upon exiting the block.

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `Log.exit()`

<dl><dd>

Outdents the log from the most recent
[`Log.enter()`](#logentermessage) call.

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `Log.flush(block=True)`

<dl><dd>

Flushes the log, if it is in "logging" state and is dirty.
A log is "dirty" if any formatted text has been written
since the log was started or last flushed.

If `block` is true (the default), `flush` won't return
until after the log is flushed.  If false, the log may
be flushed asynchronously.

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `Log.map_destination(o)`

<dl><dd>

Class method.  Maps `o` to the appropriate
[`Destination`](#logdestination) object using the same
conversion rules as the `Log` constructor's positional
arguments (e.g. `builtins.print` becomes `Log.Print()`,
a `str` becomes `Log.File(path)`, etc.).

Returns the `Destination` object, or raises `TypeError`
if `o` is not a recognized type.
</dd></dl>

#### `Log.print(*args, end='\n', sep=' ', flush=False, format='print')`

<dl><dd>

Logs a message, with an interface similar to `builtins.print`.

The arguments are formatted into a string as
`sep.join(str(a) for a in args) + end`, then logged
using the specified `format` (default `"print"`).

Calling the `Log` instance directly (e.g. `log("message")`)
is equivalent to calling this method.

If `flush` is true, the log is flushed immediately
after logging this message.

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `Log.reset()`

<dl><dd>

Resets the log to its initial state.

* If the log is in "initial" state, this is a no-op.
* If the log is in "logging" state, the log is closed, then reset.
* If the log is in "closed" state, the log is reset.

`Log.reset()` is the only way to reopen a closed log.

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `Log.write(formatted)`

<dl><dd>

Writes a pre-formatted string directly to the log with no
further formatting or modification.

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>


#### `Log.Destination`

<dl><dd>

Base class for objects that perform the actual logging for a
[`Log`](#logdestinations-options).  A `Destination` is owned
by a `Log`, and the `Log` sends it events by calling named
methods.

All `Destination` subclasses must implement the `write` method:

```Python
    write(elapsed, thread, formatted)
```

Subclasses may also optionally override:

```Python
    flush()
    close()
    reset()
    start(start_time_ns, start_time_epoch, formatted)
    end(elapsed, formatted)
    log(elapsed, thread, format, message, formatted)
    enter(elapsed, thread, message, formatted)
    exit(elapsed, thread, message, formatted)
```

The default implementations of `start`, `end`, `log`, `enter`,
and `exit` all call `self.write(elapsed, thread, formatted)`.
Subclasses need not call the base class method for any of these.

Subclasses may also override `register(owner)`, but *must*
call the base class implementation via `super().register(owner)`.
Subclasses must also call the base class `__init__` without
arguments.

The meaning of the arguments to the various `Destination` methods:

* `elapsed` is the elapsed time since the log was started/reset,
in nanoseconds.

* `thread` is the `threading.Thread` handle for the thread that
logged the message.

* `formatted` is the formatted log message.

* `format` is the name of the format applied to `message` to
produce `formatted`.

* `message` is the original message passed in to a `Log` method.

* `owner` is the `Log` object that owns this `Destination`.

`Log` guarantees events are sent in this order:

```
    register → start → [write | log | enter | exit | flush]* → end → [flush] → close
```

`register` is sent once, while the log is in its initial state.
The log transitions to logging state the first time a message
is logged.  `flush` is only sent when the log is dirty.
If the log is reset, it sends `end` / [`flush`] / `close` /
`reset`, returning to initial state.

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `Log.Destination.Buffer(destination=None)`

<dl><dd>

A [`Destination`](#logdestination) that buffers log messages
before sending them to another `Destination`.

Every formatted log message is stored in an internal buffer.
When the log is flushed, `Buffer` concatenates all buffered
messages into one string, writes that string to the underlying
`Destination`, and flushes it.

If `destination` is `None` (the default), `Buffer` wraps a
[`Log.Print()`](#logprint) destination.  Otherwise,
`destination` is mapped using
[`Log.map_destination`](#logmap_destinationo).

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `Log.Callable(callable)`

<dl><dd>

A [`Destination`](#logdestination) wrapping a callable.

Calls `callable(formatted)` for every formatted log message.

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `Log.File(path, initial_mode="at", *, flush=False)`

<dl><dd>

A [`Destination`](#logdestination) that writes to a file in
the filesystem.  `path` may be a `str` or `pathlib.Path`.

If `flush` is false (the default), formatted log messages are
buffered internally.  When the log is flushed, `File`
concatenates all buffered messages, opens the file, writes
them with one write call, and closes it.

If `flush` is true, the file is opened and kept open.  Every
formatted log message is written and flushed immediately.
On `close`, the file is closed; on `reset`, it is reopened.

The first time the file is opened, it uses `initial_mode`
(default `"at"`).  After the first time, `File` always uses
mode `"at"`.

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `Log.FileHandle(handle, *, flush=False)`

<dl><dd>

A [`Destination`](#logdestination) wrapping an already-open
Python file handle (an `io.TextIOBase` instance).

Every formatted log message is written to the file handle
immediately.  `FileHandle` will never close the handle;
it only writes to it and flushes it.

If `flush` is true, the file handle is flushed after every
write.  By default `flush` is false.

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `Log.List(list)`

<dl><dd>

A [`Destination`](#logdestination) wrapping a Python list.

Appends every formatted log message to `list`.

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `Log.Print()`

<dl><dd>

A [`Destination`](#logdestination) that writes to stdout
using `builtins.print`.

Calls `builtins.print(formatted, end='', flush=True)` for
every formatted log message.

This is the default destination when no destinations are
passed to the [`Log`](#logdestinations-options) constructor.

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `Log.Sink()`

<dl><dd>

A [`Destination`](#logdestination) that retains all log events
in order as [`SinkEvent`](#sinkevent) objects.

You may iterate over a `Sink` to yield all events logged so far.
`Sink` also has a `print` method that prints the events so far
with some simple formatting.

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `Log.TmpFile(*, flush=False)`

<dl><dd>

A [`Destination`](#logdestination) subclass of
[`Log.File`](#logfilepath-initial_modeat--flushfalse)
that writes to a timestamped temporary file.

The filename is computed approximately as:

    tempfile.gettempdir() / "{Log.name}.{start timestamp}.{pid}.txt"

The filename is recomputed on `register` and `reset` events,
so resetting the `Log` closes the old file and opens a new one.

The sentinel value [`TMPFILE`](#tmpfile) is a pre-created
`Log.TmpFile()` instance.

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `OldDestination()`

<dl><dd>

A [`Log.Destination`](#logdestination) subclass providing
backwards compatibility with the old `big.log.Log` interface.
Deprecated; will be removed no earlier than March 2027.

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `OldLog(clock=None)`

<dl><dd>

A drop-in replacement for the old `big.log.Log` class, reimplemented
on top of the new [`Log`](#logdestinations-options).  Provides
interface compatibility with the old `Log` to ease the transition
to the new one.  Deprecated; will be removed no earlier than
March 2027.

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `prefix_format(time_seconds_width, time_fractional_width, thread_name_width=12)`

<dl><dd>

Returns a prefix format string for use with the `prefix`
option of the [`Log`](#logdestinations-options) constructor.

The returned format string produces a prefix of the form:

```
    [{elapsed} {thread.name}]
```

formatted with the specified widths.  For example, the default
`Log` prefix is `prefix_format(3, 10, 12)`, which produces
output like:

```
    [003.0706368860   MainThread]
```

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `SinkEvent`

<dl><dd>

Base class for log events stored by [`Log.Sink`](#logsink).
Each subclass represents a different type of event.

All `SinkEvent` objects have these read-only properties:

`type` — A string identifying the event type
(e.g. `"start"`, `"end"`, `"write"`, `"log"`, `"enter"`, `"exit"`).

`number` — The log's sequence number (incremented on each reset).

`elapsed` — Elapsed time in nanoseconds since the log was started.

`duration` — Time in nanoseconds since the previous event with
a message.

`thread` — The `threading.Thread` that logged the event, or `None`.

`formatted` — The formatted log message string.

`message` — The original unformatted message, or `None`.

`format` — The format name used, or `None`.

`depth` — The nesting depth at the time of the event.

The subclasses are:

* [`SinkStartEvent`](#sinkstartevent),
* [`SinkEndEvent`](#sinkendevent),
* [`SinkWriteEvent`](#sinkwriteevent),
* [`SinkLogEvent`](#sinklogevent),
* [`SinkEnterEvent`](#sinkenterevent),
* and [`SinkExitEvent`](#sinkexitevent).

See the [**The big `Log`**](#the-big-log) tutorial for more.
</dd></dl>

#### `SinkStartEvent`

<dl><dd>

A [`SinkEvent`](#sinkevent) representing the start of a log.
Has a `configuration` property containing a dict of the
`Log`'s configuration at start time.
</dd></dl>

#### `SinkEndEvent`

<dl><dd>

A [`SinkEvent`](#sinkevent) representing the end of a log.
</dd></dl>

#### `SinkWriteEvent`

<dl><dd>

A [`SinkEvent`](#sinkevent) representing a
[`Log.write`](#logwriteformatted) call.
</dd></dl>

#### `SinkLogEvent`

<dl><dd>

A [`SinkEvent`](#sinkevent) representing a
[`Log.print`](#logprintargs-end-sep--flushfalse-formatprint)
call (or any format-based log call).
</dd></dl>

#### `SinkEnterEvent`

<dl><dd>

A [`SinkEvent`](#sinkevent) representing a
[`Log.enter`](#logentermessage) call.
</dd></dl>

#### `SinkExitEvent`

<dl><dd>

A [`SinkEvent`](#sinkevent) representing a
[`Log.exit`](#logexit) call.
</dd></dl>

#### `TMPFILE`

<dl><dd>

A pre-created [`Log.TmpFile()`](#logtmpfile-flushfalse) sentinel
value.  Pass this as a destination to the
[`Log`](#logdestinations-options) constructor to log to a
timestamped temporary file.

See the [**The big `Log`**](#the-big-log) tutorial for more.
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

Code that makes it easy to write simple state machines.

There are lots of popular Python libraries for implementing
state machines.  But they all seem to be designed for
*large-scale* state machines.  These libraries are
sophisticated and data-driven, with expansive APIs.
And, as a rule, they require the state to be
a passive object (e.g. an `Enum`), and require you to explicitly
describe every possible state transition.

That approach is great for massive, super-complex state
machines--you need the features of a sophisticated library
to manage all that complexity.  It also enables clever
features like automatically generating diagrams of your
state machine, which is great!

But most of the time this level of sophistication is
unnecessary.  There are lots of use cases for small scale,
*simple* state machines, where the sophisticated data-driven
approach and expansive, complex API only gets in the way.
I prefer writing my state machines with active objects--where
states are implemented as classes, events are implemented as
method calls on those classes, and you transition to a new
state by simply overwriting a `state` attribute with a
different state instance.

`big.state` makes it easy to write this style of state machine.
It has a deliberately minimal, simple interface--the constructor
for the main `StateManager` class only has four parameters,
and it only exposes three attributes.  The module also has
two decorators to make your life easier.  And that's it!
But even this small API surface area makes it effortless to
write some pretty big state machines.

(Of course, you can also use `big.state` to write *tiny*
data-driven state machines too. Although `big.state` makes
state machines with active states easy to write, it's agnostic
about how you actually implement your state machine.
Really, `big.state` makes it easy to write any kind of
state machine you like!)

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
    class Off(State):
        def on_enter(self):
            print("off!")

        def toggle(self):
            sm = self.state_machine
            sm.state = sm.On() # sm.state is the accessor

    @BoundInnerClass
    class On(State):
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

To transition to a new state, simply assign to the `state`
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
* For every object `o` in the `state_manager.observers` list,
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


## `big.template`

<dl><dd>

Functions for parsing strings containing a simple template syntax,
patterned after
[Django Templates](https://docs.djangoproject.com/en/stable/ref/templates/language/)
and [Jinja](https://jinja.palletsprojects.com/).
Similar in spirit to Python 3.14+ t-strings.

</dd></dl>

#### `eval_template_string(s, globals, locals=None, *, parse_expressions=True, parse_comments=False, parse_whitespace_eater=False)`

<dl><dd>

Parses and evaluates a template string, returning the rendered result.

`s` is parsed using
[`parse_template_string`](#parse_template_strings--parse_expressionstrue-parse_commentsfalse-parse_statementsfalse-parse_whitespace_eaterfalse-quotes--multiline_quotes-escape),
then each [`Interpolation`](#interpolation) is evaluated using
Python's built-in `eval()` with the provided `globals` and
`locals` dicts.  Filters are applied in order.  The rendered
string is returned with all interpolations replaced by their
values.

`parse_comments` and `parse_whitespace_eater` may be enabled
optionally; they are disabled by default.  Statement parsing
is not supported by `eval_template_string`.
</dd></dl>

#### `Interpolation(expression, *filters, debug='')`

<dl><dd>

Represents a `{{ }}` expression interpolation from a parsed template.

`expression` contains the text of the expression.  `filters`
is a tuple containing the text of each filter expression, if any.
If the expression ended with `=`, `debug` contains the text
of the expression along with the `=` and all whitespace;
otherwise it is an empty string.

See [`parse_template_string`](#parse_template_strings--parse_expressionstrue-parse_commentsfalse-parse_statementsfalse-parse_whitespace_eaterfalse-quotes--multiline_quotes-escape).
</dd></dl>

#### `parse_template_string(s, *, parse_expressions=True, parse_comments=False, parse_statements=False, parse_whitespace_eater=False, quotes=('"', "'"), multiline_quotes=(), escape='\\')`

<dl><dd>

Parses a string containing simple template markup, yielding
its components.

Returns a generator yielding `str` objects (literal text),
[`Interpolation`](#interpolation) objects (parsed expressions),
and [`Statement`](#statement) objects (parsed statements).

The supported delimiters are:

`{{ ... }}` — An expression.  Parsed into an
[`Interpolation`](#interpolation) object.  Expressions may
include filters separated by `|`.

`{% ... %}` — A statement.  Parsed into a
[`Statement`](#statement) object.  Quoted strings inside
statements are preserved and respected when looking for the
close delimiter.

`{# ... #}` — A comment.  The delimiters and all text between
them are discarded.

`{>}` — The whitespace eater.  These three characters and all
subsequent whitespace are discarded.

Each delimiter type can be individually enabled or disabled
via its corresponding boolean keyword-only parameter.
By default only `parse_expressions` is true.
</dd></dl>

#### `Statement(statement)`

<dl><dd>

Represents a `{% %}` statement from a parsed template.

`statement` contains the text of the statement, including
all leading and trailing whitespace.

See [`parse_template_string`](#parse_template_strings--parse_expressionstrue-parse_commentsfalse-parse_statementsfalse-parse_whitespace_eaterfalse-quotes--multiline_quotes-escape).
</dd></dl>


## `big.text`

<dl><dd>

Functions for working with text strings.  There are
several families of functions inside the `text` module;
for a higher-level view of those families, read the
following tutorials:

* [**The `multi-` family of string functions**](#The-multi--family-of-string-functions)
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
e.g. [the **big** "multi-" family of functions.](#the-multi--family-of-string-functions)

Also contains `'\r\n'`.
If you don't want to include this string, use [`ascii_linebreaks_without_crlf`](#ascii_linebreaks_without_crlf) instead.
See the tutorial section on
[**The Unix, Mac, and DOS linebreak conventions**](#the-unix-mac-and-dos-linebreak-conventions)
for more.

For more information, please see the
[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
tutorial.

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
e.g. [the **big** "multi-" family of functions.](#the-multi--family-of-string-functions)

Also contains `'\r\n'`.
If you don't want to include this string, use [`ascii_whitespace_without_crlf`](#ascii_whitespace_without_crlf) instead.
See the tutorial section on
[**The Unix, Mac, and DOS linebreak conventions**](#the-unix-mac-and-dos-linebreak-conventions)
for more.

For more information, please see the
[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
tutorial.

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
e.g. [the **big** "multi-" family of functions.](#the-multi--family-of-string-functions)

Also contains `b'\r\n'`.
If you don't want to include this string, use [`bytes_linebreaks_without_crlf`](#bytes_linebreaks_without_crlf) instead.
See the tutorial section on
[**The Unix, Mac, and DOS linebreak conventions**](#the-unix-mac-and-dos-linebreak-conventions)
for more.

For more information, please see the
[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
tutorial.

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
e.g. [the **big** "multi-" family of functions.](#the-multi--family-of-string-functions)

Also contains `b'\r\n'`.
If you don't want to include this string, use [`bytes_whitespace_without_crlf`](#bytes_whitespace_without_crlf) instead.
See the tutorial section on
[**The Unix, Mac, and DOS linebreak conventions**](#the-unix-mac-and-dos-linebreak-conventions)
for more.

For more information, please see the
[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
tutorial.

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

#### `decode_python_script(script, *, newline=None, use_bom=True, use_source_code_encoding=True)`

<dl><dd>

Correctly decodes a Python script from a bytes string.

`script` should be a `bytes` object containing an encoded Python script.

Returns a `str` containing the decoded Python script.

By default, Python 3 scripts must be encoded using [UTF-8.](https://en.wikipedia.org/wiki/UTF-8)
(This was established by [PEP 3120.)](https://peps.python.org/pep-3120/)
Python scripts are allowed to use other encodings, but when they do so
they must explicitly specify what encoding they used.  Python defines
two methods for scripts to specify their encoding; `decode_python_script`
supports both.

The first method uses a ["byte order mark", aka "BOM".](https://en.wikipedia.org/wiki/Byte_order_mark)
This is a sequence of bytes at the beginning of the file that indicate
the file's encoding.

If `use_bom` is true (the default), `decode_python_script` will
recognize a BOM if present, and decode the file using the encoding
specified by the BOM.  Note that `decode_python_script` removes the BOM
when it decodes the file.

The second method is called a "source code encoding", and it was defined
in [PEP 263.](https://peps.python.org/pep-0263/)  This is a "magic comment"
that must be one of the first two lines of the file.

If `use_source_code_encoding` is true (the default), `decode_python_script`
will recognize a source code encoding magic comment, and use that to decode
the file.  (`decode_python_script` leaves the magic comment in place.)

If both these "`use_`" keyword-only parameters are true (the default),
`decode_python_script` can handle either, both, or neither.  In this case,
if `script` contains both a BOM *and* a source code encoding magic comment,
the script will be decoded using the encoding specified by the BOM, and the
source code encoding must agree with the BOM.

The `newline` parameter supports Python's "universal newlines" convention.
This behaves identically to the newline parameter for Python's
[`open()`](https://docs.python.org/3/library/functions.html#open)
function.

</dd></dl>

#### `Delimiter(close, *, escape='', multiline=True, quoting=False)`

<dl><dd>

Class representing a delimiter for
[`split_delimiters`](#split_delimiterss-delimiters--state-yieldsnone).

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

If `escape` is true, `quoting` must also be true.

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
e.g. [the **big** "multi-" family of functions.](#the-multi--family-of-string-functions)

Also contains `'\r\n'`.  See the tutorial section on
[**The Unix, Mac, and DOS linebreak conventions**](#the-unix-mac-and-dos-linebreak-conventions)
for more.

For more information, please see the
[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
tutorial.

</dd></dl>


#### `linebreaks_without_crlf`

<dl><dd>

Equivalent to [`linebreaks`](#linebreaks) without `'\r\n'`.

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

For more information, see the tutorial on
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

For more information, see the tutorial on
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

For more information, see the tutorial on
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

For more information, see the tutorial on
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

#### `Pattern(s, flags=0)`

<dl><dd>

A drop-in replacement for
[`re.Pattern`](https://docs.python.org/3/library/re.html#re.Pattern)
that preserves `str` subclasses.

Python's `re` module converts `str` subclasses to plain `str`
when returning matched strings.  `Pattern` preserves the subclass:
if you search or match against a
[`big.string`](#the-big-string), the strings returned
in the `Match` object will be `big.string` slices, retaining
their line number and column number information.

`Pattern` supports the same interface as `re.Pattern`.
See the Python documentation for
[`re.Pattern`](https://docs.python.org/3/library/re.html#re.Pattern)
for the full API.
</dd></dl>


#### `python_delimiters`

<dl><dd>

A delimiters mapping suitable for use as the `delimiters`
argument for  [`split_delimiters`](#split_delimiterss-delimiters--state-yieldsnone).
`python_delimiters` defines *all* the delimiters for Python, and
is able to correctly split any modern Python text at its delimiter boundaries.

`python_delimiters` changes the rules a little bit for `split_delimiters`:

* When you use `split_delimiters` with `python_delimiters`, it yields *four*
  values, not three.  The fourth value is `change`.  See `split_delimiters`
  for more information.

* If you make a copy of `python_delimiters` and modify it, you will break
  its semantics.  Internally `python_delimiters` is really just a symbolic
  token, and `split_delimiters` uses a secret, internal-only, manually
  modified set of delimiters.  This was necessary because the `Delimiters`
  object isn't sophisticated enough (yet) to express all the semantics
  needed for `python_delimiters`.

* When you call `split_delimiters` and pass in `python_delimiters`,
  you *must* include the linebreak characters in the `text` string(s)
  you pass in.  This is necessary to support the comment delimiter
  correctly, and to enforce the no-linebreaks-inside-single-quoted-strings rule.
  If you're using `big.lines` to pre-process a script before passing
  it in to `split_delimiters`, consider calling it with `clip_linebreaks=False`.

Here's a list of all the delimiters recognized by `python_delimiters`:

* `()`, `{}`, and `[]`.
* All four string delimiters: `'`, `"`, `'''`, and `"""`.
* All possible string prefixes, including all valid combinations of
  `b`, `f`, `r`, and `u`, in both lower and upper case.
* Inside f-strings:
    * The quoting markers `{{` and `}}` are passed through in `text`
      unmodified.
    * The converter (`!`) and format spec (`:`) inside the curly braces
      inside an f-string.  These two delimiters are the only two that
      use the new `change` value yielded by `split_delimiters`.
* Line comments, which "open" with `#` and "close" with either a
  linebreak (`\n`) or a carriage return (`\r`).  (Python's
  "universal newlines" support should mean you won't normally
  see carriage returns here... unless you specifically permit them.)

See also `python_delimiters_version`.

</dd></dl>

#### `python_delimiters_version`

<dl><dd>

A dictionary mapping strings containing a Python major and minor version to
`python_delimiters` objects.

By default, `python_delimiters` parses the version of the Python language
matching the version it's being run under.  If you run Python 3.12, and
call `big.split_delimiters` and pass in `python_delimiters`, it will split
delimiters based on Python 3.12.  If you instead wanted to parse using the
semantics from Python 3.8, you would instead pass in `python_delimiters_version['3.8']`
as the `delimiters` argument to `split_delimiters`.

There are entries in `python_split_delimiters` for every version of
Python supported by big (currently 3.6 to 3.13).

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

> *Note:* `re_partition` supports partitioning on subclasses
> of `str` or `bytes`, and the `before` and `after` objects in
> the tuple returned will be slices of the `text` object.
> However, the `match` object doesn't honor this this; the objects
> it returns from e.g. `match.group` will always be of the base
> type, either `str` or `bytes`.  This isn't fixable, as you can't
> create `re.Match` objects in Python, nor can you subclass it.

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

> *Note:* `re_rpartition` supports partitioning on subclasses
> of `str` or `bytes`, and the `before` and `after` objects in
> the tuple returned will be slices of the `text` object.
> However, the `match` object doesn't honor this this; the objects
> it returns from e.g. `match.group` will always be of the base
> type, either `str` or `bytes`.  This isn't fixable, as you can't
> create `re.Match` objects in Python, nor can you subclass it.

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

#### `split_delimiters(s, delimiters={...}, *, state=(), yields=None)`

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

Yields a object of type `SplitDelimitersValue`.  This object
contains five fields:

<dl><dt>

`text`

</dt><dd>

A string, the text before the next opening, closing, or changing
delimiter.

</dd><dt>

`open`

</dt><dd>

A string, the trailing opening delimiter.

</dd><dt>

`close`

</dt><dd>

A string, the trailing closing delimiter.

</dd><dt>

`change`

</dt><dd>

A string, the trailing change delimiter.

</dd><dt>

`yields`

</dt><dd>

An integer, either 3 or 4.

</dd></dl>


At least one of the four strings will always be non-empty.
(Only one of `open`, `close`, and `change` will ever be non-empty in
a single `SplitDelimitersValue` object.)  If `s` doesn't end with
an opening or closing delimiter, the final value yielded will
have empty strings for `open`, `close`, and `change`.

The `yields` parameter to `split_delimiters` affects iteration over
a `SplitDelimitersValue` object.  `yields` may be None, 3, or 4:

* If `yields` is 3, when iterating over a `SplitDelimitersValue`
  object, it will yield `text`, `open`, and `close` in that order.
* If `yields` is 4, when iterating over a `SplitDelimitersValue`
  object, it will yield `text`, `open`, `close`, and `change` in that order.
* If yields is `None` (the default), `split_delimiters` will use
  a value of 4 if its `delimiters` argument is `python_delimiters`,
  and a value of 3 otherwise.

(The `yields` parameter exists because previously `split_delimiters`
always yielded an tuple containing three string values.  `python_delimiters`
required adding the fourth string value, `change`.  Eventually
`split_delimiters` will always yield an object yielding four values,
but big is allowing for a transition period to minimize code breakage.
See the release notes for [big version 0.12.5](#0125) for more information.)

You may not specify backslash ('\\\\') as an open delimiter.

Multiple Delimiter objects specified in delimiters may use
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
empty strings or quote delimiters from `quotes` (or `multiline_quotes`),
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

For more information, see the tutorial on
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
e.g. [the **big** "multi-" family of functions.](#the-multi--family-of-string-functions)

Also contains `'\r\n'`.  See the tutorial section on
[**The Unix, Mac, and DOS linebreak conventions**](#the-unix-mac-and-dos-linebreak-conventions)
for more.

For more information, please see the
[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
tutorial.

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
e.g. [the **big** "multi-" family of functions.](#the-multi--family-of-string-functions)

Also contains `'\r\n'`.  See the tutorial section on
[**The Unix, Mac, and DOS linebreak conventions**](#the-unix-mac-and-dos-linebreak-conventions)
for more.

For more information, please see the
[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
tutorial.

</dd></dl>

#### `str_whitespace_without_crlf`

<dl><dd>

Equivalent to [`str_whitespace`](#str_whitespace) without `'\r\n'`.

</dd></dl>

#### `strip_indents(lines, *, tab_width=8, linebreaks=linebreaks)`

<dl><dd>

Takes an iterable of lines, with or without linebreaks;
strips the leading whitespace from each line and tracks
the indent level.  Yields 2-tuples of `(depth, lstripped_line)`.

`depth` is an integer, the ordinal number of times the lines
were indented to reach the current indent.  Text at the leftmost
column is at `depth` 0; if the line was indented three times,
`depth` will be 3.

Uses an intentionally simple algorithm.  Only understands
tab and space characters as indent characters.  Internally
converts tabs to spaces for consistency, using the `tab_width`
passed in.

Text can only dedent out to a previous indent.  Raises
`IndentationError` if there's an illegal dedent.

Blank lines and empty lines have the indent level of the
*next* non-blank line, or `0` if there are no subsequent
non-blank lines.  If the line contains only whitespace,
any trailing characters found in `linebreaks` will be
preserved.  Pass in `None` or an empty sequence for
`linebreaks` to suppress this.
</dd></dl>

#### `strip_line_comments(lines, line_comment_markers, *, escape='\\', quotes=(), multiline_quotes=(), linebreaks=linebreaks)`

<dl><dd>

Strips line comments from an iterable of lines.

Line comments are substrings beginning with a special marker
that mean the rest of the line should be ignored.
`strip_line_comments` truncates each line at the beginning of
the leftmost line comment marker and yields the result.
If the line doesn't contain any unquoted comment markers,
it's yielded unchanged.

`line_comment_markers` should be an iterable of strings
denoting line comment markers (e.g. `['#']` or `['//']`).

If `quotes` is specified, it must be an iterable of quote
marker strings.  `strip_line_comments` will parse the line
using [`split_quoted_strings`](#split_quoted_stringss-quotes---escape-multiline_quotes-state)
and ignore comment characters inside quoted strings.  Quoted
strings may not span lines; if a line ends with an unterminated
quoted string, `strip_line_comments` will raise a `SyntaxError`.

If `multiline_quotes` is specified, it must be an iterable of
quote marker strings.  Quoted strings enclosed in multiline
quotes may span multiple lines.  There must be no quote markers
in common between `quotes` and `multiline_quotes`.

`escape` is a string used to escape quote markers inside quoted
strings, as per backslash inside strings in Python.  The default
is `'\\'`.

If lines end with linebreak characters, they will be preserved
even when a comment is stripped.
</dd></dl>

#### `unicode_linebreaks`

<dl><dd>

A tuple of `str` objects, representing every line-breaking
whitespace character defined by Unicode.

Useful as a `separator` argument for **big** functions that accept one,
e.g. [the **big** "multi-" family of functions.](#the-multi--family-of-string-functions)

Also contains `'\r\n'`.  See the tutorial section on
[**The Unix, Mac, and DOS linebreak conventions**](#the-unix-mac-and-dos-linebreak-conventions)
for more.

For more information, please see the
[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
tutorial.

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
e.g. [the **big** "multi-" family of functions.](#the-multi--family-of-string-functions)

Also contains `'\r\n'`.  See the tutorial section on
[**The Unix, Mac, and DOS linebreak conventions**](#the-unix-mac-and-dos-linebreak-conventions)
for more.

For more information, please see the
[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
tutorial.

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
e.g. [the **big** "multi-" family of functions.](#the-multi--family-of-string-functions)

Also contains `'\r\n'`.  See the tutorial section on
[**The Unix, Mac, and DOS linebreak conventions**](#the-unix-mac-and-dos-linebreak-conventions)
for more.

For more information, please see the
[**Whitespace and line-breaking characters in Python and big**](#whitespace-and-line-breaking-characters-in-python-and-big)
tutorial.

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

For more information, see the tutorial on
[**Word wrapping and formatting.**](#word-wrapping-and-formatting)
</dd></dl>

## `big.tokens`

<dl><dd>

Functions and constants for working with Python's tokenizer.

#### Token constants

`big.tokens` defines a `TOKEN_<n>` constant for every
token that could exist in any supported version of Python.
If a token isn't defined in the current version, its value
is set to `-1`, an invalid token value that won't match
any tokens.

This lets you write version-independent code like:

```Python
if token.type == big.tokens.TOKEN_FSTRING_START:
   ...
```

In Python versions where `FSTRING_START` doesn't exist,
`TOKEN_FSTRING_START` is `-1` and the condition will never
be true.

</dd></dl>

#### `generate_tokens(s)`

<dl><dd>

A convenient wrapper around
[`tokenize.generate_tokens`](https://docs.python.org/3/library/tokenize.html#tokenize.generate_tokens).

This function takes a `str` (or
[`big.string`](#the-big-string))
and handles the `readline` interface required by
`tokenize.generate_tokens` internally.

If the argument is a `big.string`, the string values in
the yielded `TokenInfo` objects will be `big.string` slices
from the original string, preserving line and column
information.
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

#### `timestamp_human(t=None, want_microseconds=None, *, tzinfo=None)`

<dl><dd>

Return a timestamp string formatted in a pleasing way
for the local timezone (by default).  This format
is intended for human readability; for computer-parsable
time, use `timestamp_3339Z()`.

Example timestamp: `"2021/05/24 23:42:49.099437"`

`t` can be one of several types:

* If `t` is `None`, `timestamp_human` uses the current local time.
* If `t` is an int or float, it's interpreted as seconds since the epoch.
* If `t` is a `time.struct_time`, it's converted to a `datetime.datetime` object.
* If `t` is a `datetime.datetime` object, it's used directly

If `want_microseconds` is true, the timestamp will end with
the microseconds, represented as ".######".  If `want_microseconds`
is false, the timestamp will not include the microseconds.

If `tzinfo` is `None` (the default), the time is converted to the local
timezone.  If `tzinfo` is a `datetime.timezone` object, the time is
converted to this timezone.  The timezone is printed at the end of
the string.

*0.13 update:* Added `tzinfo` parameter, and added the timezone
to the end of the string.
</dd></dl>

## `big.types`

<dl><dd>

New types for **big**.  Currently contains
[`string`](#strings--sourcenone-line_number1-column_number1-first_column_number1-tab_width8) and
[`linked_list`](#linked_listiterableundefined).

</dd></dl>

### `string`

<dl><dd>

`string` is a subclass of `str` that knows its own line number,
column number, and source.  Every operation that returns a substring
returns a `big.string` that preserves this information.

See the [**The big `string`**](#the-big-string) tutorial for
an introduction and examples.

</dd></dl>

#### `string(s='', *, source=None, line_number=1, column_number=1, first_column_number=1, tab_width=8)`

<dl><dd>

A subclass of `str` that maintains line, column, and offset
information.

`string` is a drop-in replacement for Python's `str`.  It
implements every `str` method; every operation that returns
a substring returns a `big.string` that knows its own line
and column information.  For documentation of the standard
`str` methods, see the Python documentation for
[`str`](https://docs.python.org/3/library/stdtypes.html#str).

Keyword-only parameters to the constructor:

* `source` — A human-readable string describing where this
  string came from (e.g. a filename).  Included in `where`.

* `line_number` — The line number of the first character.
  Default is `1`.

* `column_number` — The column number of the first character.
  Default is `1`.

* `first_column_number` — The column number to reset to after
  a linebreak.  Default is `1`.

* `tab_width` — The distance between tab columns, used when
  computing column numbers.  Default is `8`.

Read-only properties:

* `line_number` — The line number of this string.

* `column_number` — The column number of this string.

* `source` — The source string passed to the constructor.

* `origin` — The original `big.string` this string was sliced from.

* `offset` — The index of the first character of this string within
  `origin`.

* `first_column_number` — The column number reset to after linebreaks.

* `tab_width` — The tab width used for column calculations.

* `where` — A human-readable location string for error messages,
  in the format `"<source> line <n> column <n>"` (or without the
  source if none was specified).

If you pass a `big.string` into Python modules implemented in C,
the returned substrings will be plain `str` objects.  big provides
wrappers for two of these, drop-in replacements where the returned
substrings will be `big.string` slices of the original string:

* [`string.generate_tokens`](#stringgenerate_tokens), a wrapper for
  [`tokenize.generate_tokens`](https://docs.python.org/3/library/tokenize.html#tokenize.generate_tokens), and
* [`string.compile`](#stringcompileflags0), a wrapper for `re.compile`.

See the [**The big `string`**](#the-big-string) tutorial for more.
</dd></dl>

#### `string.bisect(index)`

<dl><dd>

Splits the string at `index`.  Returns a tuple of two strings:
`(string[:index], string[index:])`.
</dd></dl>

#### `string.cat(*strings)`

<dl><dd>

Class method.  Concatenates the `str` or `big.string` objects
passed in.  Roughly equivalent to `big.string('').join()`.
Always returns a `big.string`.
</dd></dl>

#### `string.compile(flags=0)`

<dl><dd>

Returns a [`Pattern`](#patterns-flags0) compiled from this
string.  Equivalent to `re.compile(self, flags)`.  All methods
on the `Pattern`, and method calls on objects it returns,
return `big.string` slices of the original string as appropriate.
</dd></dl>

#### `string.generate_tokens()`

<dl><dd>

Wraps
[`tokenize.generate_tokens`](https://docs.python.org/3/library/tokenize.html#tokenize.generate_tokens),
preserving `big.string` slices in the yielded `TokenInfo` objects.
Equivalent to calling
[`big.tokens.generate_tokens`](#generate_tokenss) with this
string.
</dd></dl>

### `linked_list`

<dl><dd>

`linked_list` is a doubly-linked list with an interface that's
a superset of both `list` and `collections.deque`.  It also supports
extracting and merging ranges of nodes with
[`cut`](#linked_listcutstartnone-stopnone--locknone) and
[`splice`](#linked_listspliceother--wherenone), and its iterators
behave like database cursors.

See the [**The big `linked_list`**](#the-big-linked_list) tutorial
for an introduction and examples.

</dd></dl>

#### `linked_list(iterable=(), *, lock=None)`

<dl><dd>

A doubly-linked list.

`iterable` provides initial values.  If `lock` is `True`,
the list uses an internal `threading.Lock` for thread safety.
If `lock` is a lock object, that lock is used (but the list
cannot be pickled).  If `lock` is `False` or `None`, no
locking is used.

`linked_list` has explicit "head" and "tail" sentinel nodes.
Iterating yields values between head and tail.
`linked_list` supports `len`, indexing, slicing,
`in`, `==`, `bool`, pickling, and `reversed`.

See the [**The big `linked_list`**](#the-big-linked_list) tutorial for more.
</dd></dl>

#### `linked_list.append(object)`

<dl><dd>

Appends `object` to the end of the linked list.
</dd></dl>

#### `linked_list.clear()`

<dl><dd>

Removes all values from the linked list.
</dd></dl>

#### `linked_list.copy(*, lock=None)`

<dl><dd>

Returns a shallow copy of the linked list.  `lock` is
passed to the new list's constructor.
</dd></dl>

#### `linked_list.count(value)`

<dl><dd>

Returns the number of occurrences of `value` in the linked list.
</dd></dl>

#### `linked_list.cut(start=None, stop=None, *, lock=None)`

<dl><dd>

Cuts a range of nodes from the list and returns them as a
new `linked_list`.

`start` and `stop`, if specified, must be iterators over this
list.  If `start` is `None`, it defaults to the first node
after head.  If `stop` is `None`, it defaults to tail.
The range includes `start` but excludes `stop`.  `start`
must not point to a node after `stop`.

`lock` is passed to the new list's constructor; if `None`,
the new list reuses this list's lock parameter.

Will not cut head.  Raises `SpecialNodeError` if `start`
points to head.

See the [**The big `linked_list`**](#the-big-linked_list) tutorial for more.
</dd></dl>

#### `linked_list.extend(iterable)`

<dl><dd>

Extends the linked list by appending elements from `iterable`.
</dd></dl>

#### `linked_list.extendleft(iterable)`

<dl><dd>

Prepends the elements from `iterable` to the linked list,
in reverse order.  Provided for `collections.deque` compatibility.
</dd></dl>

#### `linked_list.find(value)`

<dl><dd>

Returns an iterator pointing at the first occurrence of `value`,
or `None` if `value` does not appear.
</dd></dl>

#### `linked_list.index(value, start=0, stop=sys.maxsize)`

<dl><dd>

Returns the first index of `value`.  Raises `ValueError`
if `value` is not present.  `start` and `stop` limit the
search to a subsequence.
</dd></dl>

#### `linked_list.insert(index, object)`

<dl><dd>

Inserts `object` before `index`.
</dd></dl>

#### `linked_list.match(predicate)`

<dl><dd>

Returns an iterator pointing at the first value for which
`predicate(value)` returns a true value, or `None` if no
such value exists.
</dd></dl>

#### `linked_list.pop(index=-1)`

<dl><dd>

Removes and returns the value at `index` (default last).
</dd></dl>

#### `linked_list.prepend(object)`

<dl><dd>

Prepends `object` to the beginning of the linked list.
</dd></dl>

#### `linked_list.rcount(value)`

<dl><dd>

Returns the number of occurrences of `value` in the linked list.
Equivalent to [`linked_list.count`](#linked_listcountvalue)
but searches in reverse order.
</dd></dl>

#### `linked_list.rcut(start=None, stop=None, *, lock=None)`

<dl><dd>

Like [`linked_list.cut`](#linked_listcutstartnone-stopnone--locknone),
except all directions are reversed: `start` must not point to a
node before `stop`, and the cut range is from `stop` forwards to
`start`.  The returned list is still in forwards order.
</dd></dl>

#### `linked_list.remove(value, default=undefined)`

<dl><dd>

Removes and returns the first occurrence of `value`.
If `value` does not appear, returns `default` if specified,
otherwise raises `ValueError`.
</dd></dl>

#### `linked_list.reverse()`

<dl><dd>

Reverses all values in the linked list in place.
</dd></dl>

#### `linked_list.rextend(iterable)`

<dl><dd>

Extends the linked list by prepending elements from `iterable`,
in forwards order.
</dd></dl>

#### `linked_list.rfind(value)`

<dl><dd>

Returns an iterator pointing at the last occurrence of `value`,
or `None` if `value` does not appear.
</dd></dl>

#### `linked_list.rmatch(predicate)`

<dl><dd>

Returns an iterator pointing at the last value for which
`predicate(value)` returns a true value, or `None` if no
such value exists.
</dd></dl>

#### `linked_list.rpop(index=0)`

<dl><dd>

Removes and returns the value at `index` (default first).
</dd></dl>

#### `linked_list.rotate(n)`

<dl><dd>

Rotates the linked list `n` steps to the right.
If `n` is negative, rotates left.  Provided for
`collections.deque` compatibility.
</dd></dl>

#### `linked_list.rremove(value, default=undefined)`

<dl><dd>

Removes and returns the last occurrence of `value`.
If `value` does not appear, returns `default` if specified,
otherwise raises `ValueError`.
</dd></dl>

#### `linked_list.rsplice(other, *, where=None)`

<dl><dd>

Like [`linked_list.splice`](#linked_listspliceother--wherenone),
except: if `where` is `None`, the nodes are prepended (rather
than appended).  If `where` is not `None`, the nodes are inserted
before (rather than after) the node pointed to by `where`.
</dd></dl>

#### `linked_list.sort(key=None, reverse=False)`

<dl><dd>

Sorts the linked list in ascending order.  Arguments are the
same as `list.sort`.
</dd></dl>

#### `linked_list.splice(other, *, where=None)`

<dl><dd>

Moves all nodes from `other` into this list.  `other`
must be a `linked_list`; after a successful splice, `other`
will be empty.

`where` must be an iterator over this list, or `None`.
If `where` is an iterator, the nodes are inserted after
the node pointed to by `where`.  If `where` is `None`,
the nodes are appended.

See the [**The big `linked_list`**](#the-big-linked_list) tutorial for more.
</dd></dl>

#### `linked_list.tail()`

<dl><dd>

Returns a forwards iterator pointing at the linked list's
tail sentinel node.
</dd></dl>

#### `linked_list_node`

<dl><dd>

A node in a [`linked_list`](#linked_listiterableundefined).
`linked_list_node` objects are not created directly; they
are managed internally by the linked list.

Attributes:

`value` — The value stored in the node.

`special` — `None` for normal nodes, or a string (`'head'`,
`'tail'`, or `'special'`) for sentinel nodes.

`next` — The next node.

`previous` — The previous node.

`linked_list` — The `linked_list` this node belongs to.
</dd></dl>

#### `SpecialNodeError`

<dl><dd>

A `LookupError` subclass raised when an operation is attempted
on a special (sentinel) node that doesn't support it.
</dd></dl>

#### `UndefinedIndexError`

<dl><dd>

An `IndexError` subclass raised when accessing an undefined
index in a `linked_list` (before head or after tail).
</dd></dl>


#### `linked_list_iterator`

<dl><dd>

Iterates over a [`linked_list`](#linked_listiterable--locknone),
yielding values in order.  Created by calling `iter()` on a
`linked_list` or by calling `linked_list.find()` etc.

A `linked_list_iterator` behaves like a cursor: when it yields
a value, it continues pointing at that node until explicitly
advanced.  Indexing and slicing are relative to the current
node, and negative indices access previous nodes (not the end
of the list).

`linked_list` explicitly supports removing nodes while
iterating.  If the current node is removed, the iterator
points at a "special" placeholder node until advanced.

See the [**The big `linked_list`**](#the-big-linked_list)
tutorial for more.
</dd></dl>

#### `linked_list_iterator.after(count=1)`

<dl><dd>

Returns a new iterator pointing at the node `count` steps
after the current node.
</dd></dl>

#### `linked_list_iterator.append(value)`

<dl><dd>

Appends `value` immediately after the current node.
</dd></dl>

#### `linked_list_iterator.before(count=1)`

<dl><dd>

Returns a new iterator pointing at the node `count` steps
before the current node.
</dd></dl>

#### `linked_list_iterator.copy()`

<dl><dd>

Returns a copy of the iterator, pointing at the same node
in the same linked list.
</dd></dl>

#### `linked_list_iterator.count(value)`

<dl><dd>

Returns the number of occurrences of `value` between the
current node and tail.
</dd></dl>

#### `linked_list_iterator.cut(stop=None, *, lock=None)`

<dl><dd>

Bisects the list at the current node.  Cuts nodes starting
at the current node up to (but not including) `stop`, and
returns them as a new `linked_list`.

If `stop` is `None`, all subsequent nodes are cut (the
original list gets a new tail).  `lock` is passed to the
new list's constructor.

See the [**The big `linked_list`**](#the-big-linked_list)
tutorial for more.
</dd></dl>

#### `linked_list_iterator.exhaust()`

<dl><dd>

Advances the iterator to point to tail.
</dd></dl>

#### `linked_list_iterator.extend(iterable)`

<dl><dd>

Extends the list by appending elements from `iterable` after
the current node.
</dd></dl>

#### `linked_list_iterator.find(value)`

<dl><dd>

Returns an iterator pointing at the nearest next occurrence
of `value`, or `None` if not found before tail.
</dd></dl>

#### `linked_list_iterator.insert(index, object)`

<dl><dd>

Inserts `object` after the `index`'th node relative to the
current position.
</dd></dl>

#### `linked_list_iterator.is_special()`

<dl><dd>

Returns `True` if the iterator is pointing at a special
(sentinel) node, `False` otherwise.
</dd></dl>

#### `linked_list_iterator.linked_list`

<dl><dd>

Returns the `linked_list` this iterator belongs to.
</dd></dl>

#### `linked_list_iterator.match(predicate)`

<dl><dd>

Returns an iterator pointing at the nearest next value for which
`predicate(value)` returns a true value, or `None` if no such
value exists before tail.
</dd></dl>

#### `linked_list_iterator.next(default=undefined, *, count=1)`

<dl><dd>

Advances the iterator by `count` steps and returns the value
there.  If the iterator is exhausted, returns `default` if
specified, otherwise raises `StopIteration`.
</dd></dl>

#### `linked_list_iterator.pop(index=0)`

<dl><dd>

Removes and returns the value at `index` relative to the current
position.  If `index` is `0` (the default), removes the current
node and the iterator advances backwards to the previous node.
</dd></dl>

#### `linked_list_iterator.prepend(value)`

<dl><dd>

Inserts `value` immediately before the current node.
</dd></dl>

#### `linked_list_iterator.previous(default=undefined, *, count=1)`

<dl><dd>

Advances the iterator backwards by `count` steps and returns
the value there.  If the iterator reaches head, returns
`default` if specified, otherwise raises `StopIteration`.
</dd></dl>

#### `linked_list_iterator.rcount(value)`

<dl><dd>

Returns the number of occurrences of `value` between the
current node and head.
</dd></dl>

#### `linked_list_iterator.rcut(stop=None, *, lock=None)`

<dl><dd>

Like [`linked_list_iterator.cut`](#linked_list_iteratorcutstopnone--locknone),
except it cuts backwards: nodes from `stop` up to and including
the current node.  If `stop` is `None`, all preceding nodes
are cut.
</dd></dl>

#### `linked_list_iterator.remove(value, default=undefined)`

<dl><dd>

Removes the nearest next occurrence of `value`.
Returns `default` if specified and `value` is not found,
otherwise raises `ValueError`.
</dd></dl>

#### `linked_list_iterator.reset()`

<dl><dd>

Resets the iterator to point to head.
</dd></dl>

#### `linked_list_iterator.rextend(iterable)`

<dl><dd>

Extends the list by prepending elements from `iterable` before
the current node, preserving their order.
</dd></dl>

#### `linked_list_iterator.rfind(value)`

<dl><dd>

Returns an iterator pointing at the nearest previous occurrence
of `value`, or `None` if not found before head.
</dd></dl>

#### `linked_list_iterator.rmatch(predicate)`

<dl><dd>

Returns an iterator pointing at the nearest previous value for which
`predicate(value)` returns a true value, or `None` if no such
value exists before head.
</dd></dl>

#### `linked_list_iterator.rpop(index=0)`

<dl><dd>

Removes and returns the value at `index` relative to the current
position (default `0`).
</dd></dl>

#### `linked_list_iterator.rremove(value, default=undefined)`

<dl><dd>

Removes the nearest previous occurrence of `value`.
Returns `default` if specified and `value` is not found,
otherwise raises `ValueError`.
</dd></dl>

#### `linked_list_iterator.rsplice(other)`

<dl><dd>

Removes all nodes from `other` and inserts them immediately
before the current node.
</dd></dl>

#### `linked_list_iterator.rtruncate()`

<dl><dd>

Truncates the linked list at the current node, discarding the
current node and all previous nodes.  After this operation,
the iterator points to head.
</dd></dl>

#### `linked_list_iterator.special()`

<dl><dd>

Returns the `special` attribute of the current node: `None`
for normal nodes, or a string (`'head'`, `'tail'`, or
`'special'`) for sentinel nodes.
</dd></dl>

#### `linked_list_iterator.splice(other)`

<dl><dd>

Removes all nodes from `other` and inserts them immediately
after the current node.
</dd></dl>

#### `linked_list_iterator.truncate()`

<dl><dd>

Truncates the linked list at the current node, discarding the
current node and all subsequent nodes.  After this operation,
the iterator points to tail.
</dd></dl>


#### `linked_list_reverse_iterator`

<dl><dd>

Iterates over a [`linked_list`](#linked_listiterable--locknone)
in reverse order, yielding values from tail towards head.
Created by calling `reversed()` on a `linked_list` or on a
`linked_list_iterator`.

Provides the same interface as
[`linked_list_iterator`](#linked_list_iterator), but with all
directions reversed: `next` advances towards head, `previous`
advances towards tail, and so on.

See the [**The big `linked_list`**](#the-big-linked_list)
tutorial for more.
</dd></dl>

#### `linked_list_reverse_iterator.after(count=1)`

<dl><dd>

Behaves like [`linked_list_iterator.before`](#linked_list_iteratorbeforecount1).
</dd></dl>

#### `linked_list_reverse_iterator.append(value)`

<dl><dd>

Behaves like [`linked_list_iterator.prepend`](#linked_list_iteratorprependvalue).
</dd></dl>

#### `linked_list_reverse_iterator.before(count=1)`

<dl><dd>

Behaves like [`linked_list_iterator.after`](#linked_list_iteratoraftercount1).
</dd></dl>

#### `linked_list_reverse_iterator.copy()`

<dl><dd>

Returns a copy of the reverse iterator, pointing at the same node.
</dd></dl>

#### `linked_list_reverse_iterator.count(value)`

<dl><dd>

Behaves like [`linked_list_iterator.rcount`](#linked_list_iteratorrcountvalue).
</dd></dl>

#### `linked_list_reverse_iterator.cut(stop=None, *, lock=None)`

<dl><dd>

Behaves like [`linked_list_iterator.rcut`](#linked_list_iteratorrcutstopnone--locknone).
</dd></dl>

#### `linked_list_reverse_iterator.exhaust()`

<dl><dd>

Advances the reverse iterator to point to head.
</dd></dl>

#### `linked_list_reverse_iterator.extend(iterable)`

<dl><dd>

Behaves like [`linked_list_iterator.rextend`](#linked_list_iteratorrextenditerable).
</dd></dl>

#### `linked_list_reverse_iterator.find(value)`

<dl><dd>

Behaves like [`linked_list_iterator.rfind`](#linked_list_iteratorrfindvalue).
</dd></dl>

#### `linked_list_reverse_iterator.insert(index, object)`

<dl><dd>

Inserts `object` relative to the current position, with reversed
index direction.
</dd></dl>

#### `linked_list_reverse_iterator.is_special()`

<dl><dd>

Behaves like [`linked_list_iterator.is_special`](#linked_list_iteratoris_special).
</dd></dl>

#### `linked_list_reverse_iterator.linked_list`

<dl><dd>

Returns the `linked_list` this iterator belongs to.
</dd></dl>

#### `linked_list_reverse_iterator.match(predicate)`

<dl><dd>

Behaves like [`linked_list_iterator.rmatch`](#linked_list_iteratorrmatchpredicate).
</dd></dl>

#### `linked_list_reverse_iterator.next(default=undefined, *, count=1)`

<dl><dd>

Behaves like [`linked_list_iterator.previous`](#linked_list_iteratorpreviousdefaultundefined--count1).
</dd></dl>

#### `linked_list_reverse_iterator.pop(index=0)`

<dl><dd>

Behaves like [`linked_list_iterator.rpop`](#linked_list_iteratorrpopindex0).
</dd></dl>

#### `linked_list_reverse_iterator.prepend(value)`

<dl><dd>

Behaves like [`linked_list_iterator.append`](#linked_list_iteratorappendvalue).
</dd></dl>

#### `linked_list_reverse_iterator.previous(default=undefined, *, count=1)`

<dl><dd>

Behaves like [`linked_list_iterator.next`](#linked_list_iteratornextdefaultundefined--count1).
</dd></dl>

#### `linked_list_reverse_iterator.rcount(value)`

<dl><dd>

Behaves like [`linked_list_iterator.count`](#linked_list_iteratorcountvalue).
</dd></dl>

#### `linked_list_reverse_iterator.rcut(stop=None, *, lock=None)`

<dl><dd>

Behaves like [`linked_list_iterator.cut`](#linked_list_iteratorcutstopnone--locknone).
</dd></dl>

#### `linked_list_reverse_iterator.remove(value, default=undefined)`

<dl><dd>

Behaves like [`linked_list_iterator.rremove`](#linked_list_iteratorrremovevalue-defaultundefined).
</dd></dl>

#### `linked_list_reverse_iterator.reset()`

<dl><dd>

Resets the reverse iterator to point to tail.
</dd></dl>

#### `linked_list_reverse_iterator.rextend(iterable)`

<dl><dd>

Behaves like [`linked_list_iterator.extend`](#linked_list_iteratorextenditerable).
</dd></dl>

#### `linked_list_reverse_iterator.rfind(value)`

<dl><dd>

Behaves like [`linked_list_iterator.find`](#linked_list_iteratorfindvalue).
</dd></dl>

#### `linked_list_reverse_iterator.rmatch(predicate)`

<dl><dd>

Behaves like [`linked_list_iterator.match`](#linked_list_iteratormatchpredicate).
</dd></dl>

#### `linked_list_reverse_iterator.rpop(index=0)`

<dl><dd>

Behaves like [`linked_list_iterator.pop`](#linked_list_iteratorpopindex0).
</dd></dl>

#### `linked_list_reverse_iterator.rremove(value, default=undefined)`

<dl><dd>

Behaves like [`linked_list_iterator.remove`](#linked_list_iteratorremovevalue-defaultundefined).
</dd></dl>

#### `linked_list_reverse_iterator.rsplice(other)`

<dl><dd>

Behaves like [`linked_list_iterator.splice`](#linked_list_iteratorspliceother).
</dd></dl>

#### `linked_list_reverse_iterator.rtruncate()`

<dl><dd>

Behaves like [`linked_list_iterator.truncate`](#linked_list_iteratortruncate).
</dd></dl>

#### `linked_list_reverse_iterator.special()`

<dl><dd>

Behaves like [`linked_list_iterator.special`](#linked_list_iteratorspecial).
</dd></dl>

#### `linked_list_reverse_iterator.splice(other)`

<dl><dd>

Behaves like [`linked_list_iterator.rsplice`](#linked_list_iteratorrspliceother).
</dd></dl>

#### `linked_list_reverse_iterator.truncate()`

<dl><dd>

Behaves like [`linked_list_iterator.rtruncate`](#linked_list_iteratorrtruncate).
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
  instead of a version string. Shh!

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


# Tutorials

## The big `string`

<dl><dd>

Python's `tokenize` and `re` (regular expression) modules both had to
solve an API problem.  In both cases, you submit a large string to them,
and they split it up and return little substrings--tiny little slices
of the big string.  Often, the user needs to know *where* those little
slices came from.  How do you communicate that?

What `tokenize` and `re` did was add extra information accompanying the
string.  But they took different--and incompatible--approaches.  They
both represent "where" the little bitty strings came from differently:

* [`tokenize.tokenize`](https://docs.python.org/3/library/tokenize.html#tokenize.tokenize)
  returns a `TokenInfo` object containing the line and column numbers of the string it contains).
* `search` and `match` methods on a compiled regular expression return
  [a `Match` object](https://docs.python.org/3/library/re.html#re.Match)
  which tells you the index where the string started in the original string.

This is sufficient--barely.  It's also fragile.  What if you further
subdivide the string?   What if you join the text with the antecedent
or subsequent text from the original?  Now you have to clumsily
track these offsets yourself.  And if you want line and column
information, the re module's `Match` object is of no help.

And what if you're parsing your text yourself, rather than using
`tokenize` or `re`?  If you split up a string into lines using the
`splitlines` method on a string, you have to track the line numbers
yourself.  Worse yet, if you split by lines, then use `re` to subdivide
the string, you have to mate your offset tracking with the `re.Match`
object's tracking.  What a pain!

big's `string` object solves all that.  It's a drop-in replacement for
Python's `str` object, and in fact is a subclass of `str`.  What it gives you:
any time you extract a substring of a `string` object, the substring knows
its *own* offset, line number, and column number relative to the original
string.  You *don't* need to figure it out yourself, and you *don't* need to
store the information separately using some fragile external representation.
Any time you have a `string` object, you *automatically* know where it came
from.  (You can even specify a "source" for the text--the original filename
or what have you--and the `string` object will retain that too.)

This makes producing syntax error messages effortless.  If `s` is a `string`
object, and represents a syntax error because it was an unexpected token
in the middle of a text you're parsing, you can simply write this:

```Python
raise SyntaxError(f'{s.where}: unexpected token {s}')
```

`where` is a property, an automatically-formatted string containing
the line and column information for the string.  And if you specified
a "source", it contains that too.  For example, if you initialized the
`string` with "source" set to `/home/larry/myscript.py`, and `s` was
the token `whule` (whoops! mistyped `while`!), from line number 12,
column number 15, the text of the exception would read:

```
"/home/larry/myscript.py" line 12 column 15: unexpected token 'whule'
```

#### Tomorrow's methods, today

big supports older versions of Python; as of this writing it supports all
the way back to 3.6.  (The Python core development team dropped support for
3.6 several years ago!)

The `string` object supports *all* the methods of the `str` object.  At the
moment there's a new `str` method as of version 3.7, `isascii`.  Rather than
only provide that in 3.7+, `string` makes that available in 3.6 too.

#### Naughty modules not honoring the subclass

It was important that `string` not only be a drop-in replacement for `str`.
The only way for that to work: it had to literally *be* a subclass of `str`.
There's a lot of code that says
```Python
if isinstance(obj, str):
```
and if `string` objects failed that test they'd break code.

This has an unfortunate side-effect.  CPython ships with modules in its
standard library written in C that check to see "is this object a `str` object?"
And if the object passes that test, they use low-level C API calls on the `str`
object to interact with it.  The problem is, these low-level C API calls ignore
the fact that this is a *subclass* of `str`, and they sidestep the overloaded
behaviors of the `string` object.  This means that, for example, when they
extract a substring from the object, they don't get a `string` object preserving
the offsets, they just get a plain old `str` object.

Fixing this in CPython would be worthwhile, but it'd be a lot of work and it
would only benefit the future.  We want to solve our problem today.  So big
provides workarounds for the two worst offenders: `re` and `tokenize`.
big's `string` object has a `compile` method that is a drop-in replacement
for `re.compile`, and all the methods you call on it will return `string`
objects instead of `str` objects.  The `string` object also has a method
called `generate_tokens` that produces the same output as `tokenize.generate_tokens`,
except (of course!) all the strings returned in its `TokenInfo` objects
are `string` objects.

Unfortunately, there's one more wrinkle.  The objects returned by CPython's
`re` module don't let you instantitate them, nor subclass them.
They deliberately set an internal flag that means "Python code is not
permitted to subclass this class".  This means it's *impossible* for
`String.compile` to return objects that pass `isinstance` tests.
`String.compile` returns a `Pattern` object, but it's *not* an instance
of `re.Pattern`, and `isinstance` tests will fail.  **big** was forced
to reimplement these objects, and we ensure they behave identically
to the originals, but CPython makes this facet of incompatibility unfixable.


</dd></dl>

## The big `linked_list`

<dl><dd>

### Background

A [linked list](https://en.wikipedia.org/wiki/Linked_list) is a
*fundamental* data structure in computer science, second only perhaps
to the array and the record.  And yet Python has never officially
shipped with a linked list!

There *is* a linked list hidden in the standard library of CPython;
[`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque)
is *implemented* internally using a linked list.  So it's possible to
use a `deque` where you'd want a real linked list--like, a use case
where you frequently insert and remove values in the middle of the list.
This would have better performance than doing it with, say, the classic
Python `list`, where inserts and removals from the middle of the list
are an O(n) operation.  However, the `deque` API makes it inconvenient
to use as a linked list.

In 2025, I wanted a linked list for a project.  I surveyed the linked
lists available for Python at the time, decided I didn't want to use
*any* of them--so I wrote my own.  Now you get to use it too!

### Overview

big's `linked_list` itself behaves externally like a `list` or a
`deque`; you insert/append/prepend values to the list, and it stores
them in order and manages the storage.

Where big's `linked_list` shines is in its iterators.  `linked_list`
iterators are more like "database cursors"; they act like a moveable
virtual head of the list, centered on any value you like.

Also, unlike Python's other data structures, `linked_list` *explicitly*
supports modifying the list during iteration.  You can have as many
iterators iterating over a list as you like, and you can add or remove
nodes anywhere to your heart's content.

In addition, `linked_list` supports thread-safety through automatic
internal locking.

### Implementation details

Internally a big `linked_list` is a traditional doubly-linked-list.
The list is stored in a series of nodes; each node contains forwards
and backwards references, to the next and previous nodes respectively,
as well as a reference to your value. This classic design makes its
performance predictable: inserting and removing elements anywhere in
the list is O(1), whereas accessing elements by index is O(n).

There are acutally two types of node in a big `linked_list`: "data"
nodes, which store a value, and "special" nodes, which don't store a
value.  Why are these "special" nodes needed?  Several reasons.
First, `linked_list` makes a design choice that's uncommon
but not exactly rare for linked lists: the "head" and "tail" nodes
are "special" nodes in the linked list.  When you create a new
`linked_list` object, it contains *two* nodes, not *zero:* the
newly-created list already contains "head" and "tail" nodes.
This makes for a nice implementation; *every* insert and delete
simply updates four references, rather than needing lots of
"if we're pointed at the head" special cases all over the place.

There's a third type of "special" node: a *deleted* node.
If an iterator is pointing at a data node containing a value X,
and you remove X from the linked list, the *data* is removed but
the *node* stays in place.  That node is demoted to a "special"
node--again, "data" nodes store a reference to a value, "special"
nodes don't.  This change is harmless; the iterator can continue
pointing to it indefinitely, or can iterate forward or backwards
without difficulty. The fact that the node was demoted is invisible
to the user of the iterator if all they're doing is conventional
iteration. However, this implementation choice will have
ramifications for the "iterators as database cursors" APIs,
as we'll see shortly.

(In case you're wondering: once the last iterator departs a
"special" node resulting from a deleted value, `linked_list`
removes the node.)


#### `linked_list` methods

`linked_list` provides a superset of the union of the APIs of
`list` and
[`collections.deque`.](https://docs.python.org/3/library/collections.html#collections.deque)
Every method call supported by both `list` and `deque` is supported
by `linked_list`, and you can read the documentation for those types
to see the basics.

However, there are also some important changes.  First and
foremost, for `list` and `deque` methods that return an *index*
into the list, the `linked_list` equivalent returns an *iterator*.
This is a superior API, due to the "database cursor" features of
`linked_list` iterators.  It's also better for performance, as
this reduces accessing values by index, which is O[n] on
`linked_list`.

In addition, `linked_list` contains many "reversed" versions of
methods.  These are named by taking the original method name and
prepending it with `r`.  For example:
* `extend` is complemented with `rextend`, which inserts
  the values from the iterable in front of the head of the list
  in forwards order.
* `find` is complemented by `rfind`, which searches for a value
  starting at the end of the list and searching backwards.


`linked_list` also supports many of Python's "magic methods":

* `__add__`: `t + x` returns a new list containing the contents of `t` appended with `x`;
  `x` must be an iterable.
* `__bool__`: `bool(t)` returns `True` if `t` contains any values, or `False` if `t` is empty.
* `__contains__`: `v in t` evaluates to `True` if the value `v` is in `t`.
* `__copy__`: `copy.copy(t)` returns a shallow copy of the list.
* `__delitem__`: `del t[3]` will remove the fourth value in `t`.  Also supports slices.
* `__deepcopy__`: `copy.deepcopy(t)` returns a deep copy of the list.
* `__eq__` and the other five "rich comparison" methods: `t == t2` is true if and only if
  `t` and `t2` are of the same type and contain the same values in the same order.
* `__getitem__`: `t[3]` evaluates to the fourth value in `t`.  Also supports slices.
* `__iadd__`: `t += x` appends the contents of iterable `x` to `t`.
* `__imul__`: `t *= n` results in `t` containing `n` copies of its own contents.
* `__iter__`: `iter(t)` returns a forward iterator over `t`.
* `__len__`: `len(t)` returns the number of items in `t`.  If `t` is empty, this is 0.
* `__mul__`: `t * n` return a new list containing `n` copies of the contents of `t`.
* `__reversed__`: `reversed(t)` returns a reverse iterator over `t`.
* `__repr__`: `repr(t)` produces a custom repr showing the current contents of the list.
* `__setitem__`: `t[3] = v` will overwrite the fourth value in `t` with `v`.  Also supports slices.


Finally, `linked_list` supports methods that lets you move
nodes directly from one list to another, rather than inserting
new nodes.  If you're moving lots of nodes, this can be a huge
performance win.  The relevant methods:

* `cut` lets you specify a range of nodes to remove from a
  `linked_list`.  You can specify the start and stop for the
  range of nodes to cut, as iterators.  The nodes are removed
  from the linked list, and returned in their own new linked list.
* `splice` lets you move *all* the nodes of one `linked_list`
  into another.  After splicing linked list A into linked list B,
  A will be empty, and B will contain all of A's nodes, in order.
* `rcut` and `rsplice` are "reversed" versions of `cut` and `splice`.


### `linked_list` iterators

While developing `linked_list`, it occured to me: the usual use
case for a linked list involves an arbitrarily-long sequence of
data, which you iterate over and process.  For example, compilers
generally represent the program being compiled as a linked list
of "basic blocks".

When using a linked list for these sorts of use cases, you
generally operate on a pointer to the linked list node under
current consideration.  In Python parlance, you iterate over the
list, getting a reference to each node in the list in turn.
You perform your computation on that node, then iterate to the
next one.

However, you often want to *modify* the list while you're doing
this.  You may want to remove the node, or insert new nodes,
or both--replace the node with something else.  But idiomatic
Python iterators don't let you do anything like that.  All they
know how to do is "advance to the next value and yield it".
This was a genius design choice for Python, but for our linked
list it's simply not enough.

`linked_list` solves this by making its iterators far more
powerful.  One way of describing this is like a *database cursors:*
a `linked_list` iterator points at a value (or "row"), and
lets you modify the list (or "table") relative to that value.
I think of it more like a moveable virtual list "head";
the iterator points at a value, and provides APIs that let
it behave like a `linked_list` pointed at that value.
`linked_list` iterators provide nearly the *entire* API
that `linked_list` itself provides, though modified to
make sense given the context of pointing at any arbitrary
node in the list.

#### Indexing

Iterators support all operations you can perform by indexing
into a linked list; you can get, set, and delete values.

However, the meaning of the index is slightly different for
an iterator.  Negative indices don't start at the end and
work backwards; instead, they start at the *current node*
and work backwards.  If `t` is a linked list containing
`range(5)`, and `it` is an iterator pointing at value `2`,
indexing would look like this:

```
                            it
                            |
                            v
[head] <-> [0] <-> [1] <-> [2] <-> [3] <-> [4] <-> [tail]
        it[-2]  it[-1]   it[0]   it[1]   it[2]
```

If you advanced `it` once, so it pointed to the value `3`,
indexing would now look like this:

```
                                    it
                                    |
                                    v
[head] <-> [0] <-> [1] <-> [2] <-> [3] <-> [4] <-> [tail]
        it[-3]  it[-2]  it[-1]   it[0]   it[1]
```

Indexing into or past the "head" and "tail" nodes raises an
`IndexError`.

You can also use slices, e.g. `it[-3:5:2]`.  There are two
important differences from slicing into `list` or `deque` objects:

* First, negative indices in slices work like negative
  indices normally, retreating backwards into the list.
* Second, slices into `linked_list` iterators don't
  clamp for you.  Indexing into or past the "head" and "tail"
  nodes raises an `IndexError`, rather than silently
  clamping the indices to a legal range.


#### Method calls

You can also make method calls on the iterator, to operate
on the list starting at the current node.  These operations
always operate relative to the *current node,* rather than
relative to the beginning (or end) of the list.  Also, as
a rule, methods that operate on one or more nodes always
operate on the *current* node.

Here are some examples.  In these examples, `it` is always
a forwards iterator:

* `it.pop` pops and returns the value the iterator currently
  points at, then moves the iterator *back* one node.
* `it.rpop` pops and returns the value the iterator currently
  points at, then moves the iterator *forward* one node.
* `it.append` inserts a value *after* the current node.
* `it.prepend` inserts a value *before* the current node.
* `it.find` searches for a value, starting at the current
  node and continuing forwards.
* `it.rfind` searches for a value, starting at the current
  node and continuing backwards.
* `it.truncate` deletes all values at or after the current
  node.  When `it.truncate` is done, `it` will be pointing
  at "tail", and `it[-1]` will be unchanged.

#### Magic methods

`linked_list` iterators also implements many of the magic methods
supported by `linked_list`.  For example, if `it` is a forward
iterator pointing at an arbitrary node:

* `__bool__`: `bool(it)` returns `True` if `it` is not pointed at "tail".
* `__contains__`: `v in it` evaluates to `True` if the value `v` is found at or after `it` in the list.
* `__eq__`: `it == it2` is true if and only if
  `it` and `it2` point to the same node.  Iterators don't support relative comparison (less-than, etc).
* `__iter__`: `iter(it)` returns a copy of `it`.
* `__len__`: `len(t)` returns the number of items at or after `it` in the list.  If `it` points to "tail", this returns 0.
* `__reversed__`: `reversed(t)` returns a reverse iterator pointing at the same node as `it`.


#### Special nodes

There are two rules that apply to iterators when interacting
with special nodes:

* Special nodes never have a value.
* When an iterator navigates through a `linked_list`, it automatically skips over special nodes.


Let's see specifically how iterators interact with special nodes.
say you create a new empty linked list, and you create an iterator
over that linked list, and you call `next` on it:

```Python
t = LinkedList((1,))
it = iter(t)
value_a = next(it, None)
value_b = next(it, None)
```

Our iterator `it` started out pointing at the "head" node.  When you call `next(it, None)` the
first time, it advances to `1` and returns it.  The iterator is now pointing at the node for
the value `1`.  Calling `next(it, None)` the second time advances to the "tail" node;
this would normally raise `StopIteration`, but the second argument to `next` is a
"default value" it will return instead of raising.  So this second call to `next(it, None)`
just returns `None`.  After this second `next` call, `it` points to the "tail" node.

#### Deleted nodes

If an iterator is pointing at a value, and that value is deleted, the node is demoted
from a "data" node to a "special" node.  The iterator continues to point to it.  Consider
this example:

```Python
t = linked_list([1, 2, 3, 4, 5])
it = t.find(3)
del t[2]
```

The internal layout of the list and iterator now looks like this:

```
                               it
                               |
                               v
[head] <-> [1] <-> [2] <-> [special] <-> [4] <-> [5] <-> [tail]
```

Here `it` points to a "special" node, where the value `2` used to be.

If you now iterated over the linked list:

```Python
for i in t:
   print(i)
```

you'd see 1, 2, 4, and 5, like you'd expect.  The special node is
still there, but remember the rule: linked list iterators automatically
skip over special nodes.


When you have an iterator pointed at a special node, you can do almost anything
you can do with an iterator pointed at a normal node.  You can:

* navigate, using `next` or `previous` or `find` or `rfind` or `match` or `rmatch`
* create new iterators using `before` or `after`
* insert new values using `append` or `prepend` or `extend` or `extendleft`
* attempt to remove values using `remove` or `rremove`

What can't you do when pointing at a special node?  Any operation that attempts
to interact with the *value* of the *current* node will raise `SpecialNodeError`
(a subclass of `LookupError`).  For example:

* Evaluating `it[0]`.
* Evaluating `it[-1:1]`.
* Popping the current value using `it.pop()` or `it.rpop()`.

If you're worried about whether your iterator is pointing at a special node,
you can check the `special` property.  That returns `None` for a normal node,
`"head"` for the head node, `"tail"` for the tail node, and `"special"` for
any other special node.


#### Reverse iterators

`linked_list` objects also support reverse iteration.  You create a
reverse iterator by calling `reversed` on the list.  You can also create
a reverse iterator by calling `reversed` on a forwards iterator; this
returns a reverse iterator pointing at the same node.

Conceptually, a reverse iterator behaves identically to a forwards
iterator, except the reverse iterator "sees" the list backwards.
If you have a linked list that looks like this:

```
[head] <-> [1] <-> [2] <-> [special] <-> [3] <-> [4] <-> [5] <-> [tail]
```

a *reverse* iterator would see the list like this:

```
[tail] <-> [5] <-> [4] <-> [3] <-> [special] <-> [2] <-> [1] <-> [head]
```

Apart from this behavioral change, reverse iterators behave identically
to forwards iterators.  They support the exact same APIs with the same
arguments.

This makes the behavior of a reverse iterator easy to predict.  For example,
if `fi` is a forwards iterator, and `ri` is a reverse iterator on the same list:

* A newly-created reverse iterator points to the "tail" node, and `ri.reset()`
  moves the reverse iterator back to the "tail" node.
* A reverse iterator becomes exhausted once it reaches the "head" node.
  `ri.exhaust()` moves `ri` so it points at the "head" node.
* `ri.append()` inserts *before* the current node, `ri.prepend()`
  inserts *after* the current node.
* `ri[1]` evaluates to the *previous* value in the list, and `ri[-1]`
  evaluates to the *next* value in the list.

One thing that *doesn't* change: when inserting multiple nodes (`splice`, `extend`,
`rextend`), the nodes are always inserted in forwards order.  Effectively, if `fi` and
`ri` point to the same node, `fi.extend(X)` and `ri.rextend(X)` would do the same thing,
and `fi.rextend(X)` and `ri.extend(X)` would also do the same thing

#### Invariants

* An iterator pointing at a node will continue to point at that node until it takes action to move to a new node.
* If you use an iterator to append a new value, and nobody deletes that value, and you subsequently advance that
  iterator with `next()` enough times, the iterator will yield that value.
    * If you use an iterator to prepend a new value, and nobody deletes that value, and you subsequently advance
      that iterator with `previous()` enough times, the iterator will yield that value.
* As a rule, actions on iterators that act on multiple nodes include the node they're pointing at.
* iterator[0] *always* refers to the node the iterator is currently pointing at, even if it's a special
  node.  If the index is non-zero, it skips over special nodes.


</dd></dl>


## The big `Log`

<dl><dd>

### Overview

big's `Log` object is a high-performance logging mechanism, suitable
for debugging.  It has a very convenient interface, and it's easy to get
up and logging with very little configuration.  It's thread-safe,
ensuring logged messages are rendered atomically (unlike calling `print`
from multiple threads, which can interleave messages.)  And with default
parameters, logging a message is very quick--perhaps 5x faster than
calling `print`.

Although it's really designed for "print-style" debugging--where you
print out all the state in your program that you need to diagnose a
problem--it's usable for classic application logging, like Python's
`logging` module.  That said, it has a very different interface, and
is missing a lot of features as compared to the `logging` module, so
it's hardly a drop-in replacement.

### Getting started

Let's start by showing you a whole Python script that exercises
many of the big `Log` features.  We'll show you the script, then
its output, and then we'll go over it line by line and discuss
each of the features independently.

Here's the script:

```Python
import big.all as big

j = big.Log()
j.print("Hello, world!  2 + 2 =", 2 + 2)
j("Hello, world, round 2!  4 + 4 =", 4 + 4)
j.write("This was written without formatting!\nLine breaks work too!\n")
j.box(f"Today's important number is {6 * 7}!")
with j.enter("Newline subsystem"):
    j("Line one!\nAnd here's line two.\n  Leading spaces are preserved too!\nAnd here's the final line")
```

If you copy that to a new file, and run it (with big installed), you'll see
this on the output:

```
===============================================================================
Log start at 2026/02/15 13:46:51.410751 PST
===============================================================================
[000.0004777570   MainThread] Hello, world!  2 + 2 = 4
[000.0004971740   MainThread] Hello, world, round 2!  4 + 4 = 8
This was written without formatting!
Line breaks work too!
[000.0005088170   MainThread] +------------------------------------------------
[000.0005088170   MainThread] | Today's important number is 42!
[000.0005088170   MainThread] +------------------------------------------------
[000.0005117220   MainThread] +-----+------------------------------------------
[000.0005117220   MainThread] |start| Newline subsystem
[000.0005117220   MainThread] +-----+------------------------------------------
[000.0005174830   MainThread]     Line one!
[000.0005174830   MainThread]     And here's line two.
[000.0005174830   MainThread]       Leading spaces are preserved too!
[000.0005174830   MainThread]     And here's the final line
[000.0005208190   MainThread] +-----+------------------------------------------
[000.0005208190   MainThread] | end | Newline subsystem
[000.0005208190   MainThread] +-----+------------------------------------------
===============================================================================
Log finish at 2026/02/15 13:46:51.411292 PST
===============================================================================
```

Let's break it down, line by line.

To use `Log`, simply instantiate a `Log` object:

```Python
j = big.Log()
```

With all default parameters, your `Log` will send the log
to stdout via `builtins.print`.  However, it'll use a separate
thread to do the actual printing.  Logging a message will lightly
pre-format the message, then send it to the `Log` object's
internal thread; that thread finishes the formatting and sends
it to `print`.

The usual method call to log a message is the `Log.print` method:

```Python
j.print("Hello, world!  2 + 2 =", 2 + 2)
```

`Log.print` has a similar signature to `builtins.print`, although it
doesn't support the `file` parameter.

This is so common, there's a shortcut: calling the `Log` instance
itself behaves identically to calling the `print` method:

```Python
j("Hello, world, round 2!  4 + 4 =", 4 + 4)
```

These three lines so far produce the first five lines of the output:

```
===============================================================================
Log start at 2026/02/15 13:14:13.648816 PST
===============================================================================
[000.0004797210   MainThread] Hello, world!  2 + 2 = 4
[000.0005004200   MainThread] Hello, world, round 2!  4 + 4 = 8
```

As you can see, `Log` automatically adds a "start" banner showing the current
local time that the log was started.  (There's a symmetric "end" banner for
when the log is closed.)

Also, every printed log message gets a "prefix", showing the elapsed time
so far (since the start of the log) and the thread that logged the message.

(Obviously, if you run this script, *your* times will be different.  Probably
in the future... unless you've borrowed Guido's time machine.)

Let's explore the other `Log` methods that append messages to the log.
The simplest one is `write`, which only takes one `str` argument, and writes that
string to the log without any further formatting whatsoever:

```Python
j.write("This was written without formatting!\nLine breaks work too!\n")
```

This is useful in case you've carefully formatted some text by hand and
you want to dump it straight into the log.  (Or you simply want to suppress
the per-line prefix.)

`Log` also supports a method called `box` that writes a message with a three-sided
box drawn around it:

```Python
j.box(f"Today's important number is {6 * 7}!")
```

If you want to call attention to a logged message, log it
using `box` instead of `print`.  Note that the `box` method also only takes a single
`str` object.  (But that's no problem, just use an f-string!)

The above two lines in the script produce these five lines in the output:

```
This was written without formatting!
Line breaks work too!
[000.0005261250   MainThread] +------------------------------------------------
[000.0005261250   MainThread] | Today's important number is 42!
[000.0005261250   MainThread] +------------------------------------------------
```

You can see, the message logged with `Log.write` doesn't get the "prefix".
And it's easy to pick out the "boxed" message due to the lines `Log` draws
around it.

Let's finish up, examining the final two lines of the script.

`Log` supports two intertwined methods, `enter` and `exit`.  `enter`
logs a message in a box, then adds an indent that applies to subsequent
messages. `exit` outdents, then re-logs the message from the most recent
`enter` in another box.  This is a great way to add some structure to
your log, showing visually how your program enters and exits conceptual
subsystems (modules, functions, classes, algorithms, what have you).

For convenience, `Log.enter` also returns a "context manager".  If you use
a call to `Log.enter` as the argument to a `with` statement, it'll automatically
call `Log.exit` when you exit the `with` statement.   We use that feature in
the example script.

The last line demonstrates one more feature of `Log`.  All `Log` methods
that write to the log support newline characters, not just `Log.write`.
But when you log a message using the other methods--methods that write
the "prefix"--the lines are split up before they're formatted for the
log, and each line gets the prefix.

Here are the last two lines of the script:

```Python
with j.enter("Newline subsystem"):
    j("Line one!\nAnd here's line two.\n  Leading spaces are preserved too!\nAnd here's the final line")
```

Those two lines produce these *thirteen* lines in the output:

```
[000.0005117220   MainThread] +-----+------------------------------------------
[000.0005117220   MainThread] |enter| Newline subsystem
[000.0005117220   MainThread] +-----+------------------------------------------
[000.0005174830   MainThread]     Line one!
[000.0005174830   MainThread]     And here's line two.
[000.0005174830   MainThread]       Leading spaces are preserved too!
[000.0005174830   MainThread]     And here's the final line
[000.0005208190   MainThread] +-----+------------------------------------------
[000.0005208190   MainThread] |exit | Newline subsystem
[000.0005208190   MainThread] +-----+------------------------------------------
===============================================================================
Log finish at 2026/02/15 13:46:51.411292 PST
===============================================================================
```

Notice how the logged message inside the "enter" / "exit" section are indented by
four spaces.  If you nested another `with j.enter` inside the first one, text
logged inside that would be indented by eight spaces.

Once the script exited, `Log` automatically closed the log for you, including
writing the "end" banner with the end time of the log.


### Other methods

Log has three more methods; none of these write messages to the log.

`Log.flush(block=True)` flushes the log.  In some configurations, the log will
buffer up messages, instead of sending them right away.  A `flush` call
will flush all buffered messages.  If `block` is true (the default), the
`flush` call won't exit until all messages have been flushed.  If `block`
is false, `flush` may start the flushing process but won't necessarily
wait until it's complete.

`Log.close(block=True)` flushes then closes the log.  When a log is closed,
it *ignores* all attempts to write log messages to the log.  No error is
reported--the messages are simply ignored.  The only way to re-open a
closed log is to call its `reset` method.  The `block` parameter works
the same as it does for `flush`.

`Log.reset()` resets a log to its initial state.  After a log is reset,
it will print the "start" banner.  Resetting the log is the only way
to re-open a closed log.

Every `Log` also registers an "atexit" handler.  The "atexit" handler
closes the `Log` if it hasn't been closed already.


### Destinations

All our logging so far has just gone to `builtins.print`, which means it
shows up on `stdout`.  But what if you want to send the log somewhere else?

All *positional* arguments to the `Log` constructor specify *destinations.*
A *destination* is simply an object that the log sends messages to.  You
can specify as many destinations as you like when creating your `Log`
instance; however you can't add or remove destinations later.

As we've already seen, if you don't specify any destinations when you
construct the `Log`, the default is to log to `builtins.print`.  You
can explicitly configure your log to to this by passing in `print`
as a positional argument:

```Python
j = Log(print)
```

But there are lots of other options!  If you specify an list, `Log` will
append all the logged message strings to that list:

```Python
a = []
j = Log(a)
```

If you specify a string, `Log` will assume that string represents a
filename, and append the log to that file:

```Python
j = Log('/tmp/log.txt')
```

(You can also specify a `pathlib.Path` object--that works the same.)

When writing to a file, `Log` will buffer up messages until the log
is flushed, then open the file, flush *all* messages with one big
write, and close the file.

Some more options:

* If you pass in an open file handle (like the result of calling `open`),
  `Log` will write log messages to the file handle.
* If you pass in a callable, `Log` will call the callable once for every
  formatted message, with just one argument, the formatted log message.
* There's a special sentinel value in the `big.log` module: `big.log.TMPFILE`.
  If you specify that as a destination, `Log` will send the log to a
  file with a dynamically generated name in your configured temporary
  directory.  The filename starts with the name of the log; this is
  followed by the start time, then the process ID, and finally ends with
  `.txt`.  Every time the log resets it switches to a new filename.
* A destination of `None` doesn't log anywhere.  If you want to
  create a `Log` object that doesn't actually write the log anywhere,
  construct it as `big.Log(None)`.

If you pass in multiple destinations, `Log` will send all the
log messages to *all* of them.  You could log to `TMPFILE`, `print`,
and an array, all at the same time!

Finally, if you like the "buffer-until-flush" behavior of files,
but want to use that with another destination, wrap that destination
with a call to `Log.Buffer()`.  Without an argument, `Log.Buffer()`
buffers all messages until flush, then writes them all to
`builtins.print`.  If you specify a destination (as a positional
parameter), *that* destination is where the log messages are sent
when the log is flushed.  See the *Custom Destinations* section
below for more information on this and similar advanced techniques.


### Configuration via keyword-only parameters

You configure your `Log` instance by supplying keyword
arguments to the `Log` constructor.  Note that, like
the list of destinations, these can only be specified
as arguments to the constructor; you can't change any
of these settings once the `Log` instance is initialized.

The most important setting is the `threading`
parameter.  This configures whether or not the `Log`
instance uses a worker thread to do all the actual
logging.  By default `threading` is true, which means
the log uses an external thread to format and write
the log messages.  Log messages and other operations
are sent to that thread via a `queue.Queue`, which
ensures log messages are sent to the log in a
high-performance and thread-safe way.

If you pass in `threading=False` to the `Log` constructor,
the log won't use an external thread.  Instead, every
logging call will write to the log immediately; it
uses a `threading.Lock` to guarantee atomicity.

You can set the name of the log with the `name`
parameter.  This is shown in the start and end banners.

`indent` defaults to 4; this is how many spaces `enter`
indents the log.  `width` defaults to 79; this is the
column that "line" formats are truncated at.

`clock` is the clock used to compute the time at which
log messages were logged.  It should return an integer,
which is the number of nanoseconds since some previous
event.  By default it uses `time.monotonic_ns`.  (Well,
on Python 3.7+ anyway.  On Python 3.6 it simulates
`time.monotonic_ns` by calling `time.monotonic` and
multiplying it by a billion.)

`timestamp_clock` is the clock used to produce timestamps
used in the log.  It should return a float, which is the
number of seconds since the UNIX epoch.  The default value
is `time.time`.  `timestamp_format` is a callable that should
convert a `timestamp_clock` value into a pleasing human-readable
format; the default value is `big.time.timestamp_human`.

`prefix` is the string that will be inserted in front
of every line of a logged message (except `Log.write`).
It's formatted using the *Line formatting* rules as
described in the next section.  The `formats` parameter
establishes the formatting applied to log messages of
various types; this is quite involved, so see the *Formats*
section below for documentation on that.


### Line formatting

Several configuration settings for `Log` use what's called
"line formatting".  This formatting method lets you substitute
in dynamic values at runtime when writing to the log; the values
are recomputed and substituted every time `Log` formats a message
for the log.  For example, the `prefix` is freshly reformatted
for every log message.

The formatting is done using the `format` method on the
string.

Here are the values you can substitute when formatting the `prefix`:

  * `elapsed`:
            The elapsed time since the log was started,
            as float-seconds.
  * `format`:
            The format being applied to this log message.
  * `line`:
            The string used for repeating horizontal lines.  See next section, *Formats*.
  * `name`:
            The "name" of the log passed in to the Log constructor.
  * `thread`:
            A handle to the thread that logged this message.
  * `time`:
            The time of the log message, as float-seconds-since-epoch.
  * `timestamp`:
            The `time` value, formatted using the "timestamp_format"
            callable passed in to the Log constructor.

There are three more (`line`, `message`, and `prefix`) you can use when
formatting a "format", see next section.

### Formats and format dicts

The formatting of the various formatted log messages
is specified using a "format".  `Log` supports those six formats,
and has default values for each of those formats; you can change
how those messages are formatted, or add your own.

The `formats` parameter to the `Log` constructor should specify a
dict.  A key in this dict is the name of a format; a custom format name
must be a valid Python identifier, and can't collide with an existing
`Log` method name.  The matching value should be a "format dict",
which specifies the formatting to use for this message.

A "format dict" in turn supports only two fields, and one is optional.
The required one is `"template"`, which should be a string; this string
is formatted with the "line formatting" rules specified in the
previous section, with some additional values.  The optional one
is `"line"`, and you'll see what that's used for in a moment.

The string value of `"template"` is allowed to be a multi-line string.
Each line will be split up and formatted independently, using the
"line formatting" approach above.  But a template supports three additional
values:

  * `line`:
            The value of the "line" value from the format dict.
            If `{line}` is the last thing on a template line
            (either immediately before a '\n', or immediately
            before the end of the template string), the "line" value
            will be repeatedly appended to the formatted string
            until the line is >= `Log.width`, and then the line
            will then be truncated at `Log.width` characters.
            This is how `box` and the other methods draw those
            horizontal lines.
  * `message`:
            The message that was logged.  You can specify multiple
            lines containing `{message}`, however, all lines
            containing `{message}` must be contiguous.  The message
            will be split by lines, and then the template lines
            containing `{message}` will be "zipped" together with
            the lines of the message. For example, the first template
            line containing `{message}` will get the first line of
            the message, the second template line containing `{message}`
            will get the second line of the message, etc.  If there
            are more template lines than lines in the message, it skips
            the subsequent template lines; if there are more lines in the
            message than template lines, the last template line is repeated.
  * `prefix`:
            A string pre-formatted using the `prefix` format
            string passed in to the `Log` constructor.

### Predefined and user-defined formats

`Log` comes with six pre-defined formats:

  * `print`: used (by default) by `Log.print` and `Log.__call__`
  * `box`: used by `Log.box`
  * `enter`: used by `Log.enter`
  * `exit`: used by `Log.exit`
  * `start`: used to produce the "start banner" whenever the log is started
  * `end`: used to produce the "end banner" whenever the log is closed

You can override the default formatting for these by passing in a new format
dict for that value to the `formats` parameter to the `Log` constructor.
For example, to remove the prefix for lines printed by `Log.print`
and `Log.__call__`, construct your `Log` as follows:

```Python
j = big.Log(..., formats={"print": {"template": "{message}"}})
```

You can also suppress the "start banner" and "end banner", by setting those
to `None` in the `formats` dict you pass in.  This log won't print the
start and end banners:

```Python
j = big.Log(..., formats={"start": None, "end": None})
```

You can also add your own formats!  Here's some sample code that defines
a new format we'll call "critical":

```Python
j = big.Log(formats={"critical": {"template": "{prefix} =critical=start{line}\n{prefix} == {message}\n{prefix} =critical=end{line}", "line": "=-"}})
```

You'll notice, the template contains several newline characters, but
doesn't *end* with a newline.  `Log` automatically adds a trailing newline
character for you.

How do you use it?  `Log.print` and `Log.__call__` both take a
`format` keyword-only parameter, which specifies the format to apply
to the message.  So you can use it like this:

```Python
j("My hair is on fire!", format="critical")
```

However, `Log` also adds a method to the log instance for every user-defined
format.  You can just call `j.peanut` directly:

```Python
j.critical("We're almost out of coffee!")
```

This line, using the `"critical"` format specified above, produces the
following output in the log:

```
[000.0002390010   MainThread]  =critical=start=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
[000.0002390010   MainThread]  == We're almost out of coffee!
[000.0002390010   MainThread]  =critical=end=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
```

(And yes, you *could* use custom formats to simulate "log levels" with `Log`.)

### Custom Destinations

`Log` supports sending the log to lots of different kinds of
objects, called "destinations".  The actual implementation
wraps each of these diverse object types in a wrapper object
that handles logging to that "destination" object.  These wrapper
objects are all subclasses of a base class called `Log.Destination`.
You can write your own `Destination` subclasses, and `Log` will
happily send the log to those too!

First, declare your subclass.  You probably need to write an
`__init__`; that's fine, but you *must* call the base class init.

```Python
class MyDestination(Log.Destination):
    def __init__(self, o):
        super().__init__()
        ...
```

The methods on `Destination` subclasses called by the `Log` object
are referred to as "events".  They generally map to method calls
on the `Log` object, and represent the user calling that method on
the `Log`.

Second, all `Destination` subclasses *must* implement a `write`
method, like so:

```Python
    def write(elapsed, thread, formatted):
        ...
```

The `elapsed` parameter is the elapsed time since the log was
started / reset, in nanoseconds.  The `thread` parameter is the
`threading.Thread` handle for the thread that wrote this message,
or `None` if the message isn't associated with a particular thread
(like the "start banner" and "end banner" messages).  Finally,
`formatted` is the formatted string to be written to the log.
`Destination.write` is called directly to implement `Log.write`.

Next there are five optional `Destination` methods
representing high-level method calls on the `Log` object:

```Python
    def start(self, start_time_ns, start_time_epoch, formatted):
        ...

    def end(self, elapsed, formatted):
        ...

    def log(self, elapsed, thread, format, message, formatted):
        ...

    def enter(self, elapsed, thread, message, formatted):
        ...

    def exit(self, elapsed, thread, message, formatted):
        ...
```

These map respectively to the "start banner", the "end banner",
`Log.print` (and `Log.__call__`), `Log.enter`, and `Log.exit`.
If you implement one of these, it'll be called when the user
calls that method on the `Log`.  If you don't bother, you'll
get the base class implementation, which calls
`self.write(elapsed, thread, message)`.

`Destination` also supports optional methods handling the
three `Log` methods that don't send a log message:

```Python
    def reset(self):
        ...

    def flush(self):
        ...

    def close(self):
        ...
```

Finally, `Destination` objects support a `register` method,
which is called when they're passed in to the `Log` constructor.
If you override this method, you *must* call the base class
method, passing in the `owner` parameter, like so:

```Python
    def register(self, owner):
        super().register(owner)
        ...
```

`Log` objects obey a certain lifecycle, and guarantee that
the `Destination` methods will be called in this order:

```
register
  |
  v
start
  |
  +<---------------------------------+
  |                                  |
  v                                  |
write | log | enter | exit | flush   |
  |                                  |
  |                                  |
  +----------------------------------+
  |
  v
end
  |
  v
[flush]
  |
  v
close
```

The final `flush`, before `close`, is optional; it's only called
if the `Log` is "dirty".  (If the `Log` has sent formatted text to
its destinations since the log was started, or the last time the
log was flushed.)

### Final notes on `Log`

There's no guarantee that log messages will be logged in strict
chronological order.  It *usually* happens that way, but it's
not guaranteed.  If two threads both send a message at the same
time, they might arrive in any order--and it's possible the
later of the two arrives first.  This is a known behavior,
and is unlikely to change in future versions.

</dd></dl>

## Bound inner classes

<dl><dd>

#### Overview

One feature missing from Python pertains to "inner classes"--classes
defined inside other classes.

Consider this Python code:

```Python
class Outer(object):
    def think(self):
        pass

o = Outer()
o.think()
```

We've defined a function `think` inside class `Outer`.
When you call `o.think`, Python automatically passes in the `o` object as the
first parameter (by convention called `self`).  In object-oriented parlance,
`o` is *bound* to `think`, and indeed Python calls the object `o.think`
a *bound method*:

```
    >>> o.think
    <bound method Outer.think of <__main__.Outer object at 0x########>>
```

And if you refer to `Outer.think`--if you get your reference to the `think` function
from the class instead of an *instance* of the class--you just get the normal function.

```
    >>> Outer.think
    <function Outer.think at 0x7b5f4f49f110>
```

But there's no similar mechanism for a *class* defined inside another class.
Let's change our example and add a class inside `Outer`:

```Python
class Outer(object):
    def think(self):
        pass

    class Inner(object):
        def __init__(self):
            pass

o = Outer()
o.think()
i = o.Inner()
```

But classes defined inside classes don't behave the same as functions defined
inside classes.  No matter how you reference `Inner`, you get the same class object,
whether you access it through the outer class (`Outer.Inner`) or through an instance
of the outer class (`o.Inner`):

```
    >>> Outer.Inner
    <class '__main__.Outer.Inner'>
    >>> o.Inner
    <class '__main__.Outer.Inner'>
```

And if you call `o.Inner()`, Python won't automatically pass in `o` as an argument
into the way it does for `o.think()`.  If you want it passed in, you have to
pass it in yourself, like so:

```Python
class Outer(object):
    def think(self):
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
You can just decorate the inner class with `@big.BoundInnerClass`,
and the `BoundInnerClass` decorator takes care of the rest.

#### Using bound inner classes

Let's modify the above example to use our [`BoundInnerClass`](#boundinnerclasscls)
decorator:

```Python
from big import BoundInnerClass

class Outer(object):
    def think(self):
        pass

    @BoundInnerClass
    class Inner(object):
        def __init__(self, outer):
            self.outer = outer

o = Outer()
o.method()
i = o.Inner()
```

Notice that `Inner.__init__` now takes an `outer` parameter.
But you didn't have to pass it in yourself!
When you call `o.Inner()`, `o` is *automatically* passed in as the `outer`
argument to `Inner.__init__`.  That's what the `@BoundInnerClass`
decorator does for you.

Decorating an inner class like this always inserts a second
positional parameter, after `self`.  And, like `self`, you don't
*have* to use the name `outer`; you can use any name you like.
(But we'll always use the name `outer` in this documentation.)

#### Inheritance

Bound inner classes get slightly complicated when mixed with inheritance.
It's not all that difficult, you merely need to obey some rules:

1. *A bound inner class can inherit normally from any unbound class.*

2. *If your bound inner class calls `super().__init__`, and its
parent class is also a bound inner class,* **don't** *pass in `outer` manually.*
When you instantiate a bound inner class, `outer` will be automatically
passed in to *all* `__init__` methods of *every* bound inner parent class.

3. *A bound inner class can only inherit from a parent bound inner class
if the parent is defined in the same outer class or a base of the outer class.*
If Child inherits from Parent, and Child and Parent are both
decorated with `@BoundInnerClass` (or `@UnboundInnerClass`), both classes
must be defined in the same outer class (e.g. `Outer`) or in a base class
of Child's outer class.  This is a type relation constraint; bound inner
classes guarantee that "outer" is an instance of the outer class.

3a. A corollary of rule 3: *A subclass of a bound inner class, whether bound
or unbound, can only be defined in the same outer class or a subclass of the
outer class.*

4. **Directly** *inheriting from a* **bound** *inner class is unsupported.*
If `o` is an instance of `Outer`, and `Outer.Inner` is an inner class
decorated with `@BoundInnerClass`, **don't** write a class that directly
inherits from `o.Inner`, for example `class Mistake(o.Inner)`.
You should *always* inherit from the unbound version, like this:
`class GotItRight(Outer.Inner)`

5. *An inner class that inherits from a bound inner class, and which also
wants to be bound to the outer object, should be decorated with
[`BoundInnerClass`](#boundinnerclasscls).*

6. *An inner class that inherits from a bound inner class, but doesn't
want to be bound to the outer object, should be decorated with
[`UnboundInnerClass`](#unboundinnerclasscls).*

Restating the last two rules: every class that descends from any
class decorated with
[`BoundInnerClass`](#boundinnerclasscls)
must itself be decorated with either
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
    class Parent(object):
        def __init__(self, outer):
            self.outer = outer

    @UnboundInnerClass
    class Child(Parent):
        def __init__(self):
            super().__init__()

o = Outer()
child = o.Child()
```

We followed the rules:

* `Outer.Parent` inherits from object; since object isn't a bound inner class,
  there are no special rules about inheritance `Outer.Parent` needs to obey.
* Since `Outer.Child` inherits from a
  [`BoundInnerClass`](#boundinnerclasscls),
  it must be
  decorated with either [`BoundInnerClass`](#boundinnerclasscls)
  or [`UnboundInnerClass`](#unboundinnerclasscls).
  It doesn't want the outer object passed in, so it's decorated
  with [`UnboundInnerClass`](#unboundinnerclasscls).
* `Child.__init__` calls `super().__init__`, but doesn't pass in `outer`.
* Both `Parent` and `Child` are defined in the same class.

Note that, because `Child` is decorated with
[`UnboundInnerClass`](#unboundinnerclasscls),
it doesn't take an `outer` parameter.  Nor does it pass in an `outer`
argument when it calls `super().__init__`.  But when the constructor for
`Parent` is called, the correct `outer` parameter is passed in--like magic!

If you wanted `Child` to also get the outer argument passed in to
its `__init__`, just decorate it with [`BoundInnerClass`](#boundinnerclasscls)
instead of
[`UnboundInnerClass`](#unboundinnerclasscls),
like so:

```Python
from big import BoundInnerClass

class Outer(object):

    @BoundInnerClass
    class Parent(object):
        def __init__(self, outer):
            self.outer = outer

    @BoundInnerClass
    class Child(Parent):
        def __init__(self, outer):
            super().__init__()
            assert self.outer == outer

o = Outer()
child = o.Child()
```

Again, `Child.__init__` doesn't need to explicitly
pass in `outer` when calling `super.__init__`, but the
correct value for `outer` *does* get passed in to `Parent.__init__`.

You can see more complex examples of using inheritance with
[`BoundInnerClass`](#boundinnerclasscls)
(and [`UnboundInnerClass`](#unboundinnerclasscls))
in the **big** test suite.

#### Miscellaneous notes

* A bound inner class is a *subclass* of the original (unbound) class.
  `o.Inner` is a subclass of `Outer.Inner`.

* Bound inner classes bound to different outer instances are different
  classes. This is symmetric with methods; if you have two objects
  `a` and `b` that are instances of the same class,
  `a.BoundInnerClass != b.BoundInnerClass`, just as `a.method != b.method`.

* If you refer to a inner class directly from the outer *class*
  (like `Outer.Inner`) rather than an *instance* (like `o.Inner`)
  you get the original (unbound) class.

  * You might be able call `Outer.Inner` directly, to construct
    an `Inner` object without using a bound version of the class.
    You'll have to pass in the outer parameter by hand--just like
    you'd have to pass in the `self` parameter by hand when calling
    a method via the *class* (`Outer.method`) rather than via an
    *instance* of the class (`o.method`).  This won't work if
    `Outer.Inner` is a subclass of *another* bound inner class,
    and calls its `super().__init__`.  The injection of the outer
    instance argument happens when the class is bound, and this
    handles injecting the argument for all the base classes too.
    Without this binding mechanism getting involved, the `outer`
    argument won't get supplied when calling the base class's
    `__init__`.

* Bound inner classes are cached in the outer object, which both
  provides a small speedup and ensures that `isinstance`
  relationships are consistent.  This is an explicit feature, and
  you're permitted to rely on it.

   * If you use slots on your outer class, you must add a slot for
     BoundInnerClass to store its cache.  Just add BOUNDINNERCLASS_OUTER_SLOTS
     to your slots tuple, like so:

```Python
__slots__ = ('x', 'y', 'z') + BOUNDINNERCLASS_OUTER_SLOTS
```

* Binding only goes one level deep.  If you had a bound inner class `C`
  define inside another bound inner class `B`, which in turn was defined
  inside a class `A`, the constructor for `C` would be called with
  the `B` object, but not the `A` object.

* If you support Python 3.6, and you define bound inner child classes,
  you'll need to wrap all the bound inner base classes of those child
  classes with `big.boundinnerclass.bound_inner_base`.  For example:
  `class Child(bound_inner_base(Parent)):`  This is unnecessary
  in Python 3.7+.  However, using `bound_inner_base` works fine in
  all versions of Python supported by big.

* The rewrite of bound inner classes that shipped with big version 0.13
  removed some old provisos:

  * You may now rename your inner classes, even after
    decorating them with `@BoundInnerClass` (or `@UnboundInnerClass`).
    In previous versions this would break some internal mechanisms,
    but renaming your classes is now explicitly supported behavior.
  * The race condition around creating and caching the bound version
    of an inner class from multiple threads has been prevented, by
    adding just a little internal locking.  The implementation doesn't
    need to lock very often, so the performance cost is negligible.
  * It's no longer required to call `super().__init__` in bound
    inner subclasses!  In fact it was probably never necessary.
    It's totally up to you whether or not you call `super().__init__`.


</dd></dl>


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
but that can be hard to use.<sup id=back_to_re_strip><a href=#re_strip_footnote>1</a></sup>
Regular expressions can be difficult to get right, and the
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
[`multipartition`,](#multipartitions-separators-count1--reversefalse-separatetrue)
[`normalize_whitespace`,](#normalize_whitespaces-separatorsnone-replacementnone)
[`lines`,](#bigtext)
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
also inspired [`multistrip`](#multistrips-separators-lefttrue-righttrue)
 and [`multipartition`,](#multipartitions-separators-count1--reversefalse-separatetrue)
which also take this same `separators` arguments.  There are also
other **big** functions that take a `separators` argument,
for example `comment_markers` for
[`lines_filter_line_comment_lines`](#lines_filter_line_comment_lines).)

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
[`lines`](#bigtext)
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
characters. Line-breaking characters (aka *linebreaks*)
are a subset of whitespace characters; they're whitespace
characters that always move the cursor down to the next
line.  And, as with whitespace generally, Python `str`
objects don't agree with Unicode about what is and is
not a line-breaking character, and Python `bytes` objects
don't agree with either of those.

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

### The Unix, Mac, and DOS linebreak conventions

Historically, different platforms used different
ASCII characters--or sequences of ASCII characters--to
represent "go to the next line" in text files.  Here are the
most popular conventions:

    \n    - UNIX, Amiga, macOS 10+
    \r    - macOS 9 and earlier, many 8-bit computers
    \r\n  - Windows, DOS

(There are a couple more conventions, and a lot more history,
in the [Wikipedia article on newlines.)](https://en.wikipedia.org/wiki/Newline#Representation)

Handling these differing conventions was a real mess,
for a long time--not just for computer programmers, but
in the daily lives of many computer users.  It was a continual
problem for software developers back in the 90s, particularly those
who frequently switched back and forth between the two platforms.
And it took a long time before software development tooling figured
out how to seamlessly handle all the newline conventions.

Python itself went through several iterations on how to handle
this, eventually implementing
["universal newlines"](https://peps.python.org/pep-0278/)
support, added way back in Python 2.3.

These days the world seems to have converged on the UNIX
standard, `'\n'`; Windows supports it, and it's the default
on every other modern platform. So in practice these days
you probably don't have end-of-line conversion problems;
as long as you're decoding files to Unicode, and you don't
disable "universal newlines", it probably all works fine
and you never even noticed.

However!  **big** strives to behave identically to
Python in every way.  And even today, Python considers
the DOS linebreak sequence to be *one* linebreak,
not *two*.

The Python `splitlines` method on a string splits the
string at linebreaks. And if the `keepends` positional
parameter is True, it appends the linebreak character(s)
at the end of each substring.  A quick experiment with
`splitlines` will show us what Python thinks is and
isn't a linebreak. Sure enough, `splitlines` considers
'\n\r' to be two linebreaks, but it treats `\r\n` as a
*single* linebreak:

```Python
   ' a \n b \r c \r\n d \n\r e '.splitlines(True)
```
produces
```Python
   [' a \n', ' b \r', ' c \r\n', ' d \n', '\r', ' e ']
```

Naturally, if you use **big** to split by lines,
you get the same result:

```Python
list(big.multisplit(' a \n b \r c \r\n d \n\r e ', big.linebreaks, separate=True, keep=True))
```

How do we achieve this?  **big** has one more trick.  All of
the tuples defined in the previous section--from `whitespace`
to `ascii_linebreaks`--also contain the DOS linebreak
convention:

    '\r\n'

(The equivalent `bytes_` tuples contain the `bytes` equivalent,
`b'\r\n`.)

Because of this inclusion, when you use one of these tuples
with one of the **big** functions that take `separators`,
it'll recognize `\r\n` as if it was one whitespace "character".
(Just in case one happens to creep into your data.)  And since
functions like `multisplit` are "greedy", preferring the longest
matching separator, if the string you're splitting contains
`'\r\n'`, it'll prefer matching `'\r\n'` to just `'\r'`.

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
whitespace, and the document is encoded in
[code page 850](https://en.wikipedia.org/wiki/Code_page_850)
or
[code page 437.](https://en.wikipedia.org/wiki/Code_page_437)
(These two code pages are the most common code pages in
English-speaking countries.)

Normally the easiest thing would be to decode it a `str` object
using the `'cp850'` or `'cp437'` text codec as appropriate,
then operate on it normally.
But you might have reasons why you don't want to decode it--maybe
the document is damaged and doesn't decode properly, and it's
easier to work with the encoded bytes than to fix it.  If you
want to process the text with a **big** function that accepts a
`separator` argument, you could make your own custom tuples
of whitespace characters.  These two codepages have the same
whitespace characters as ASCII, but they both add one more:
value 255, "non-breaking space", a space character that is
not line-breaking.  (The intention is, this character should
behave like a space, except you shouldn't break a line at this
character when word wrapping.)

It's easy to make the appropriate tuples yourself:

    cp437_linebreaks = cp850_linebreaks = big.bytes_linebreaks
    cp437_whitespace = cp850_whitespace = big.bytes_whitespace + (b'\xff',)

Those tuples would work fine as the `separators` argument for
any **big** function that takes one.

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

But you can avoid this problem if you know you're working
in bytes on two-byte sequences.  Split the bytes string
into two-byte segments and operate on those.

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


## Release history

#### 0.13

*under development*

It's been a whole year... and I've been busy!

* Added three new modules:
  * *big.types*, which contains core types,
  * *big.tokens*, useful functions and values
    when working with Python's tokenizer, and
  * *big.template*, functions that parse strings
    containing a simple template syntax.
* Added `linked_list` to new module *big.types*.  `linked_list` is a
  thoughtful implementation of a standard linked list data
  structure, with an API and UX modeled on Python's `list`
  and `collections.deque` objects.  Unlike Python's builtins,
  you're permitted to add and remove values to a `linked_list`
  while iterating.  `linked_list` also supports locking.
* Added `string` to new module *big.types*.  `string` is a subclass
  of `str` that tracks line number and column number offsets
  for you.  Just initialize one big `string` containing an
  entire file, and every substring of that string will know
  its line number, column number, and offset in characters
  from the beginning.
* `big.lines` and all the "lines modifier" functions
  are now deprecated; `string` replaces all of it
  (and it's a *massive* upgrade!).  `big.lines` will
  move to the `deprecated` module no sooner than
  November 2025, and will be removed no sooner than May 2026.
* Added `strip_indents` and `strip_line_comments` to *big.text*.
  These provide the same functionality as the old `lines_strip_indent`
  and `lines_strip_line_comments` line modifier functions,
  but now operate on iterables of strings instead of
  "lines" iterators.
* Added `Pattern` to *big.text*.  This is a wrapper around
  `re.Pattern` that preserves slices of str subclasses.
* Added `parse_template_string` and `eval_template_string`
  to new module *big.template*.  `parse_template_string`
  parses a string containing Jinja-like interpolations,
  and returns an iterator that yields strings and
  `Interpolation` objects.  (This is similar to
  "t-strings" in Python 3.14+.)
  `eval_template_string` calls `parse_template_string` to
  parse a string, but then evaluates the expressions (and
  filters) using `eval`, returning the rendered string.
* Rewrote `BoundInnerClass`.  This removes some old concerns:
    * You no longer need the `parent.cls` hack!  (Well, you
      do if you support Python 3.6, but it's no longer needed
      in Python 3.7+.  Bound inner class adds a new function,
      `bound_inner_base`, to help with the transition.)
    * The bound inner class implementation now relies on
      comparison by identity instead of by name, which means
      you may now add aliases and/or rename your inner classes
      to your hearts' content.
    * Bound inner classes no longer keep a strong reference to
      the outer instance; they use weakrefs.  This reduces
      reference cycles, making it easier to reclaim abandoned
      bound inner class objects, albeit at the cost of adding
      a weakref "get ref" call every time a bound inner class
      is instantiated.
    * Bound inner classes now have explicit support for slots!
    * Bound inner classes now have accurate signatures,
      preserving the signature of the original class's `__init__`
      but with the `outer` parameter removed.
    * `BoundInnerClass` adds locking, to prevent a race condition
      when caching the same bound inner class created
      simultaneously in multiple threads.  It's rarely used
      and should have no real impact on performance.
* Added new functions to the *big.boundinnerclass* module:
    * `unbound(cls)` returns the unbound base class
      of `cls` if `cls` is a bound inner class.
    * `is_boundinnerclass(cls)` returns true if called on a
      class decorated with `@BoundInnerClass`, whether or
      not it has been bound to an instance.
    * `is_unboundinnerclass(cls)` returns true if called on a
      class decorated with `@UnboundInnerClass`, whether or
      not it has been bound to an instance.
    * `is_bound(cls)` returns true if called on a bound inner
      class that has been bound to an instance.
    * `bound_to(cls)` returns the instance that cls has been
      bound to, if `cls` is a bound inner class bound to an instance.
    * `type_bound_to(o)` returns the instance that `type(o)` has
      been bound to, if `type(o)` is a bound inner class bound
      to an instance.
    * `bound_inner_base(cls)` is only needed to use BoundInnerClass
      with Python 3.6.  It's unnecessary in Python 3.7+.
* Added `generate_tokens` to new module *big.tokens*.
  `generate_tokens` is a convenience wrapper around
  Python's `tokenize.generate_tokens`, which has an
  abstruse "readline"-based interface.  `tokens.generate_tokens`
  lets you simply pass in a string object, and returns a
  generator yielding tokens.  It also preserves slices
  of str subclasses--if the string you pass in is a
  `big.string` object, the `string` values it yields
  will be slices from that original `big.string`!
* The *big.tokens* module also contains definitions
  for every token defined by any version
  of Python supported by big (3.6+).  big's version
  always starts with `TOKEN_`, e.g. `token.COMMA`
  is `big.tokens.TOKEN_COMMA`.  Tokens not defined
  in the currently running version of Python have
  a value of `TOKEN_INVALID`, which is -1.
* Added `iterator_context` to *big.itertools*.  `iterator_context`
  is like an extended version of Python's `enumerate`,
  directly inspired by Jinja's
  ["loop special variables"](https://jinja.palletsprojects.com/en/stable/templates/#for)
  and Mako's ["loop context"](https://docs.makotemplates.org/en/latest/runtime.html#the-loop-context).
  It wraps an iterator and provides helpful metadata.
* Added `iterator_filter` to *big.itertools*.  `iterator_filter`
  is a pass-through iterator that filters values.
  You pass in an iterator, and rules for what values you
  want to see / don't want to see, and it returns
  an iterator that only yields the values you want.
* Rewrote the entire *big.log* module.  I stopped using
  the old `Log` class, yet on a couple recent projects
  I coded up a quick-and-dirty log... clearly the old `Log`
  wasn't solving my problem anymore.  The new `Log` is designed
  explicitly for lightweight logging, mostly for debugging
  purposes.  It's easy to use, feature-rich, high-performance,
  and by default runs in "threaded" mode where logging calls
  are 5x faster than calling `print`!
  * I added a backwards-compatible `OldLog` to *big.log*
    in case anybody is using the old `Log` class.  This
    provides the API and functionality of the old `Log`
    class, but is reimplemented on top of the new `Log`.
    Hopefully the way I did it will ease your transition
    to the obviously-superior new `Log`.  The old `Log`
    has been relocated to the *big.deprecated*
    module. Both `OldLog` and the old `Log` are deprecated,
    and will be removed someday, no earlier than March 2027.
* Added `ModuleManager` to *big.builtin*.
  `ModuleManager` helps you manage a module's namespace,
  making it easy to populate `__all__` and clean up
  temporary symbols.
* Added `ClassRegistry` to *big.builtin*.
  `ClassRegistry` helps you use inheritance with heavily
  nested class hierarchies, by giving you a place to
  store references to base classes you can access later.
  Very useful with [`BoundInnerClass`](#boundinnerclasscls)!
* The string returned by `big.time.timestamp_human` now
  includes the timezone, using the local timezone by default.
  If you want to override that and use a specific timezone,
  you can pass in a `datetime.timezone` object via the new
  `tzinfo` keyword-only parameter.
* Added support for Python 3.14, mainly to support t-strings:
  * `python_delimiters` now recognizes all the new string
    prefixes containing `t` (or `T`).
  * *big.tokens* supports the new tokens associated with
    t-strings, although that's a new module anyway.
* Sped up `test/test_text.py`.  The tests confirm that **big**'s list of whitespace
  characters is accurate.  It used to test if a particular character `c` was
  whitespace by using `len(f'a{c}b'.split()) == 2`.  D'oh!  It's obviously much
  faster to simply ask it with `c.isspace()`.  The resulting loop runs 3x
  faster... saving a whole 0.1 seconds on my workstation!
  Modifying the equivalent code for bytes instead of Unicode objects
  is also faster, but that optimization only saved 0.0000014 seconds.
  Hat tip to Eric V. Smith for his suggestions on how to make
  Big's test suite so much faster!
* `split_quoted_strings` in *big.text* now obeys
  subclasses of str better.  (It now works well with
  `big.string` for example.)
* Removed a bunch of old deprecated stuff:
  * Old names for sets of characters:
    * `whitespace_without_dos`
    * `ascii_whitespace_without_dos`
    * `newlines`
    * `newlines_without_dos`
    * `ascii_newlines`
    * `ascii_newlines_without_dos`
    * `utf8_whitespace`
    * `utf8_whitespace_without_dos`
    * `utf8_newlines`
    * `utf8_newlines_without_dos`
  * Old functions / classes / aliases:
    * `split_quoted_strings`
    * `lines_strip_comments`
    * `parse_delimiters` and its associated stuff:
      * `Delimiter` (a class)
      * `delimiter_parentheses`
      * `delimiter_square_brackets`
      * `delimiter_curly_braces`
      * `delimiter_angle_brackets`
      * `delimiter_single_quote`
      * `delimiter_double_quotes`
      * `parse_delimiters_default_delimiters`
      * `parse_delimiters_default_delimiters_bytes`
    * The old alias `lines_filter_comment_lines`
* Updated copyright notices to 2026.

#### 0.12.8

*2025/01/06*

* Added `search_path` to the *big.file* module.  `search_path`
  implements "search path" functionality; given a list of
  directories, a filename, and optionally a list of file
  extensions to try, returns the first existing file that matches.
* `multisplit` and `split_delimiters` now properly support
  subclasses of `str`. All strings yielded by these functions
  are now guaranteed to be slices of the original `s` parameter
  passed in, or otherwise produced by making method calls on the
  original `s` parameter that return strings.

#### 0.12.7

*2024/12/15*

A teeny tiny new feature.

* `LineInfo` now supports a `copy` method, which returns a copy of the `LineInfo`
  object in its current state.

#### 0.12.6

*2024/12/13*

It's a big release tradition!  Here's another small big release,
less than a day after the last big big release.

* New feature: [`decode_python_script`](#decode_python_scriptscript--newlinenone-use_bomtrue-use_source_code_encodingtrue)
  now supports "universal newlines".  It accepts a new `newline` parameter
  which behaves identically to the `newline` parameter for Python's built-in
  [`open`](https://docs.python.org/3/library/functions.html#open) function.
* Bugfix: The universal newlines support for
  [`read_python_file`](#read_python_filepath--newlinenone-use_bomtrue-use_source_code_encodingtrue)
  was broken in 0.12.5; the `newline` parameter was simply ignored.
  It now works great--it passes `newline` to `decode_python_script`.
  (Sorry I missed this; I use Linux and don't need to convert newlines.)
* Added Python 3.13 to the list of supported releases.  It was already
  supported and tested, it just wasn't listed in the project metadata.

> *Note:* Whoops!  Forgot to ever release 0.12.6 as a package.  Oh well.

#### 0.12.5

*2024/12/13*

<dl><dd>

* Added [`decode_python_script`](#decode_python_scriptscript--use_bomtrue-use_source_code_encodingtrue)
  to the *big.text* module.
  `decode_python_script` scans a binary Python script and
  decodes it to Unicode--correctly.  Python scripts can
  specify an explicit encoding in two diferent ways:
  [a Unicode "byte order mark",](https://en.wikipedia.org/wiki/Byte_order_mark)
  or [a PEP 263 "source file encoding" line.](https://peps.python.org/pep-0263/)
  `decode_python_script` handles either, both, or neither.

* Added [`read_python_file`](#read_python_filepath--newlinenone-use_bomtrue-use_source_code_encodingtrue)
  to the *big.file* module.
  `read_python_file` reads a binary Python file from the
  filesystem and decodes it using `decode_python_script`.

* Added [`python_delimiters`](#python_delimiters)
  to the *big.text* module.  This is
  a new predefined set of delimiters
  for use with `split_delimeters`, enabling it to correctly
  process Python scripts.  `python_delimiters` defines *all*
  delimiters defined by Python, including all *100* possible
  string delimiters (no kidding!).  If you want to parse the
  delimiters of Python code, and you don't want to use the
  Python tokenizer, you should use `python_delimiters`
  with `split_delimiters`.

  Note that defining `python_delimiters` correctly was difficult,
  and big's `Delimiters` API isn't expressive enough to
  express all of Python's semantics.  At this point the
  `python_delimiters` object doesn't itself actually define all its
  semantics; rather, at module load time it's compiled into a special
  internal runtime format which is cached, and then there's
  manually-written code that tweaks this compiled form so `python_delimiters`
  can correctly handle Python's special cases.  So, you're encouraged
  to use `python_delimiters`, but if you modify it and use the
  modified version, the modified version won't inherit all
  those tweaks, and will lose the ability to handle many of
  Python's weirder semantics.

  *Important note:* When you use `python_delimiters`, you *must*
  include the linebreak characters in the lines you split using
  `split_delimiters`.  This is necessary to support the comment
  delimiter correctly, and to enforce the
  no-linebreaks-inside-single-quoted-strings rule.

  There can be small differences in Python's syntax from one
  version to another.  `python_delimiters` is therefore
  version-sensitive, using the semantics appropriate for the
  version of Python it's being run under.  If you want to
  parse Python delimiters using the semantics of another version
  of the language, use instead `python_delimiters_version[s]`
  where `s` is a string containing the dotted Python major and minor
  version you want to use, for example `python_delimiters_version["3.10"]`
  to use Python 3.10 semantics.  (At the moment there are
  no differences between versions; this is planned for future
  versions of big.)

* Added [`python_delimiters_version`](#python_delimiters_version)
  to the *big.text* module.
  This maps simple Python version strings (`"3.6"`, `"3.13"`)
  to `python_delimiters` values implementing the semantics
  for that version.  Currently all the values of this dict
  are identical, but that should change in the future.

* A breaking API change to [`split_delimiters`](#split_delimiterss-delimiters--state-yieldsnone) is coming.

  `split_delimiters` now yields an object that
  can yield either three or four values.  Previous to 0.12.5, the
  `split_delimiters` iterator always yielded a tuple of three values,
  called `text`, `open`, and `close`.  But `python_delimiters`
  required adding a fourth value, `change`.

  When `change` is true, we are *changing* from one delimiter to
  another, *without* entering a new nested delimiter.  The canonical
  example of this is inside a Python f-string:

      `f"{abc:35}"`

  Here the colon (`:`) is a "change" delimiter.  Inside the curly
  braces inside the f-string, *before* the colon, the hash character
  (`#`) acts as a line comment character.  But *after* the colon
  it's just another character.  We've changed semantics, but we
  *haven't* pushed a new delimiter pair.  The only way to accurately
  convey this behavior was to add this new `change` field to the values
  yielded by `split_delimiters`.

  The goal is to eventually transition to `split_delimiters` yielding
  all four of these values (`text`, `open`, `close`, and `change`).
  But this will be a gradual process; as of 0.12.5, existing
  `split_delimiters` calls will continue to work unchanged.

  `split_delimiters` now yields a custom object, called
  `SplitDelimitersValue`.  This object is configurable to yield
  either three or four values.  The rules are:

  * If you pass in `yields=4` to `split_delimiters`,
    the object it yields will yield four values.
  * If you pass in `delimiters=python_delimiters` to `split_delimiters`,
    the object it yields will yield four values.  (`python_delimiters`
    is new, so any calls using it must be new code, therefore this
    change won't break existing calls.)
  * Otherwise,  the object yielded by `split_delimiters` will yield
    *three* values, as it did in versions prior to 0.12.5.

  `split_delimiters` will eventually change to always yielding
  four values, but big won't publish this change until at least June 2025.
  Six months after that change--at least December 2025--big will remove
  the `yields` parameter to `split_delimiters`.

* Minor semantic improvement:
  [`PushbackIterator`](#pushbackiteratoriterablenone)
  no longer
  evaluates the iterator you pass in in a boolean context.
  (All we really needed to do was compare it to `None`,
  so now that's all we do.)

* A minor change to the
  [`Delimiter`](#delimiterclose--escape-multilinetrue-quotingfalse)
  object used with
  `split_delimiters`: previously, the `quoting` and
  `escape` values had to agree, either both being true
  or both being false.  However, `python_delimiters`
  necessitated relaxing this restriction, as there are
  some delimiters (`!` inside curly braces in an f-string,
  `:` inside curly braces in an f-string) that are "quoting"
  but don't have an escape string.  So now, the restriction
  is simply that if `escape` is true, `quoting` must also
  be true.

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

* A minor semantic change to [`lines_strip_indent`](#lines_strip_indent):
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
[`lines_strip_line_comments`](#lines_strip_line_comments)
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

[`LineInfo`](#lineinfo)

[`lines_strip_line_comments`](#lines_strip_line_comments)

[`split_delimiters`](#split_delimiterss-delimiters--state)

[`split_quoted_strings`](#split_quoted_stringss-quotes---escape-multiline_quotes-state)

</dd></dl>


These functions have been renamed:

<dl><dd>

`lines_filter_comment_lines` is now [`lines_filter_line_comment_lines`](#lines_filter_line_comment_lines)

`lines_strip_comments` is now [`lines_strip_line_comments`](#lines_strip_line_comments)

`parse_delimiters` is now [`split_delimiters`](#split_delimiterss-delimiters--state)

</dd></dl>


**big** has five new functions:

<dl><dd>

[`combine_splits`](#combine_splitss-split_arrays)

[`encode_strings`](#encode_stringso--encodingascii)

[`LineInfo.clip_leading`](#lineinfoclip_leading-and-lineinfoclip_trailing)

[`LineInfo.clip_trailing`](#lineinfoclip_leading-and-lineinfoclip_trailing)

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
[`LineInfo`](#lineinfo)
constructor has a
new `lines` positional parameter, added *in front of*
the existing positional parameters.  This new first argument
should be the  `lines` iterator that yielded this
`LineInfo` object.  It's stored in the `lines` attribute.
(Why this change?  The `lines` object contains information
needed by the lines modifiers, for example `tab_width`.)

Minor optimization:
[`LineInfo`](#lineinfo)
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
[`LineInfo`](#lineinfo)
now has an `end` attribute,
which contains the end-of-line character that ended this line.

These three attributes allow us to assert a new invariant:
as long as you _modify_ the contents of `line` (e.g.
turning tabs into spaces),

    info.leading + line + info.trailing + info.end == info.line

[`LineInfo`](#lineinfo)
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


[`LineInfo`](#lineinfo)
also has two new methods:
[`LineInfo.clip_leading`](#lineinfoclip_leading-and-lineinfoclip_trailing)
and
[`LineInfo.clip_trailing(line, s)`](#lineinfoclip_leading-and-lineinfoclip_trailing).
These methods clip a leading or
trailing substring from the current `line`, and transfer
it to the relevant field in
[`LineInfo`](#lineinfo)
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
[`lines_filter_line_comment_lines`](#lines_filter_line_comment_lines).
For backwards compatibility, the function
is also available under the old name; this old name will
eventually be removed, but not before September 2025.

</dd></dl>

#### `lines_filter_line_comment_lines`

<dl><dd>

> This API has breaking changes.

New name for `lines_filter_comment_lines`.

Correctness improvements:
[`lines_filter_line_comment_lines`](#lines_filter_line_comment_lines)
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

New feature: [`lines_grep`](#lines_grep)
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
[`lines_rstrip`](#lines_rstrip-and-lines_strip)
and
[`lines_strip`](#lines_rstrip-and-lines_strip)
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
[`lines_sort`](#lines_sort)
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
[`lines_strip_line_comments`](#lines_strip_line_comments)
and
rewritten, see below.  The old deprecated version will be
available at `big.deprecated.lines_strip_comments` until at
least September 2025.

Note that the old version of `line_strip_comments` still uses
the current version of
[`LineInfo`,](#lineinfo)
so use of this deprecated
function is still exposed to those breaking changes.
(For example, `LineInfo.line` now includes the linebreak character
that terminated the current line, if any.)

</dd></dl>

#### `lines_strip_indent`

<dl><dd>

Bugfix:
[`lines_strip_indent`](#lines_strip_indent)
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

[`lines_strip_line_comments`](#lines_strip_line_comments)
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
  [`lines_rstrip`](#lines_rstrip-and-lines_strip)
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
  and newline characters, in Python, Unicode, and ASCII; please see the new tutorial
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
  [**The `multi-` family of string functions** tutorial.](#The-multi--family-of-string-functions)
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
  [`multistrip`](#multistrips-separators-lefttrue-righttrue)
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
* Expanded the tutorial on `multisplit`.
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
  [`multipartition`](#multipartitions-separators-count1--reversefalse-separatetrue)
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
  [`lines_containing`](#bigtext),
  and `lines_filter_grep` is now
  [`lines_grep`](#lines_grep).
</dd></dl>

#### 0.6.7
<dl><dd>

*released 2022/10/16*

* Added three new lines modifier functions
  to the [`text`](#bigtext) module:
  `lines_filter_contains`,
  `lines_filter_grep`,
  and
  [`lines_sort`.](#lines_sort)
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
  `lines_strip_comments` [ed: now [`lines_strip_line_comments`](#lines_strip_line_comments)
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
  [`multistrip`](#multistrips-separators-lefttrue-righttrue)
  and
  [`multipartition`,](#multipartitions-separators-count1--reversefalse-separatetrue)
  collectively called
  [**The `multi-` family of string functions.**](#The-multi--family-of-string-functions)
  (Thanks to Eric Smith for suggesting
  [`multipartition`!](#multipartitions-separators-count1--reversefalse-separatetrue)
  Well, sort of.)
  * `[`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)`
    now supports five (!) keyword-only parameters, allowing the caller
    to tune its behavior to an amazing degree.
  * Also, the original implementation of
    `[`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)`
    got its semantics a bit wrong; it was inconsistent and maybe a little buggy.
  * [`multistrip`](#multistrips-separators-lefttrue-righttrue)
    is like `str.strip` but accepts an iterable of
    separator strings.  It can strip from the left, right, both, or
    neither (in which case it does nothing).
  * [`multipartition`](#multipartitions-separators-count1--reversefalse-separatetrue)
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
  [`lines`](#bigtext)
  and all the `lines_` modifiers.  These are great for writing little text parsers.
  For more information, please see the tutorial on
  [**`lines` and lines modifier functions.**](#lines-and-lines-modifier-functions)
* Removed`stripped_lines` and `rstripped_lines` from the `text` module,
  as they're superceded by the far superior
  [`lines`](#bigtext)
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
