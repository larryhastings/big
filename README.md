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

The current version is [0.14.](#014)

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

One caution about `import *`: since **big.all** exports its submodules
by name, `from big.all import *` binds the names `time`, `types`,
`itertools`, `heap`, and `log` in your namespace--to *big's* submodules.
If your module also uses the standard library's `time`, `types`, or
`itertools`, whichever import runs *last* wins, and the loser fails at
runtime with a confusing `AttributeError`.  This is the usual hazard of
`import *`, but worth naming, since these collide with modules you
probably use.  Happily, if you keep your imports sorted, the problem
fixes itself: `from big.all import *` sorts ahead of `import itertools`,
`import time`, and `import types`, so the standard library wins every
collision.  (No promises that every future submodule of big will sort
quite so conveniently.)

**big** is licensed using the
[MIT license.](https://opensource.org/licenses/MIT)
You're free to use it and even ship it in your own programs,
as long as you leave my copyright notice on the source code.

## The best of big

Although **big** is *crammed full* of fabulous code, a few of
its subsystems rise above the rest.  If you're curious what
**big** might do for you, here are the seven things in **big**
I'm proudest of:

* [**`linked_list`**](#linked_list)
* [**`string`**](#string)
* [**Bound inner classes**](#bound-inner-classes)
* [**The `multi-` family of string functions**](#The-multi--family-of-string-functions)
* [**`Log`**](#the-big-log)
* [**`split_delimiters` and `python_delimiters`**](#split_delimiterss-delimiters--state-yields4)
* [**Snippets: `big.snip`**](#bigsnip)

And here are seven little functions/classes I use all the time:

* [`big.state`](#bigstate)
* [`eval_template_string`](#eval_template_strings-globals-localsnone--parse_expressionstrue-parse_commentsfalse-parse_whitespace_eaterfalse)
* [**Enhanced `TopologicalSorter`**](#enhanced-topologicalsorter)
* [`ModuleManager`](#ModuleManager)
* [`pushd`](#pushddirectory)
* [`re_partition`](#re_partitiontext-pattern-count1--flags0-reversefalse)
* [`timestamp_human`](#timestamp_humantnone-want_microsecondsnone--tzinfonone) and [`timestamp_3339Z`](#timestamp_3339ztnone-want_microsecondsnone)


# Index

### Modules

<dl><dd>

[`accessor(attribute='state', state_manager='state_manager')`](#accessorattributestate-state_managerstate_manager)

[`apply_snippets(s, snippets, comment='#')`](#apply_snippetss-snippets-comment)

[`ascii_format_dict(*, closed=False)`](#ascii_format_dict-closedfalse)

[`ascii_linebreaks`](#ascii_linebreaks)

[`ascii_linebreaks_without_crlf`](#ascii_linebreaks_without_crlf)

[`ascii_whitespace`](#ascii_whitespace)

[`ascii_whitespace_without_crlf`](#ascii_whitespace_without_crlf)

[`ASCIIFormatter`](#asciiformatter)

[`atomic_write(path, mode='w', *, encoding=None, errors=None, newline=None)`](#atomic_writepath-modew--encodingnone-errorsnone-newlinenone)

[`big.all`](#bigall)

[`big.boundinnerclass`](#bigboundinnerclass)

[`big.builtin`](#bigbuiltin)

[`big.deprecated`](#bigdeprecated)

[`big.file`](#bigfile)

[`big.graph`](#biggraph)

[`big.heap`](#bigheap)

[`big.itertools`](#bigitertools)

[`big.log`](#biglog)

[`big.markdown`](#bigmarkdown)

[`big.metadata`](#bigmetadata)

[`big.scheduler`](#bigscheduler)

[`big.snip`](#bigsnip)

[`big.state`](#bigstate)

[`big.stylesheet`](#bigstylesheet)

[`big.template`](#bigtemplate)

[`big.test`](#bigtest)

[`big.text`](#bigtext)

[`big.time`](#bigtime)

[`big.tokens`](#bigtokens)

[`big.types`](#bigtypes)

[`big.version`](#bigversion)

[`bound_inner_base(cls)`](#bound_inner_basecls)

[`bound_to(cls)`](#bound_tocls)

[`BoundInnerClass`](#boundinnerclasscls)

[`BOUNDINNERCLASS_OUTER_ATTR`](#boundinnerclass_outer_attr)

[`BOUNDINNERCLASS_OUTER_SLOTS`](#boundinnerclass_outer_slots)

[`Buffer(destination=None)`](#bufferdestinationnone)

[`bytes_linebreaks`](#bytes_linebreaks)

[`bytes_linebreaks_without_crlf`](#bytes_linebreaks_without_crlf)

[`bytes_whitespace`](#bytes_whitespace)

[`bytes_whitespace_without_crlf`](#bytes_whitespace_without_crlf)

[`Callable(callable)`](#callablecallable)

[`ClassRegistry()`](#classregistry)

[`Clock`](#clock)

[`combine_splits(s, *split_arrays)`](#combine_splitss-split_arrays)


[`CycleError()`](#cycleerror)

[`date_ensure_timezone(d, timezone)`](#date_ensure_timezoned-timezone)

[`date_set_timezone(d, timezone)`](#date_set_timezoned-timezone)

[`datetime_ensure_timezone(d, timezone)`](#datetime_ensure_timezoned-timezone)

[`datetime_set_timezone(d, timezone)`](#datetime_set_timezoned-timezone)

[`decode_python_script(script, *, newline=None, use_bom=True, use_source_code_encoding=True)`](#decode_python_scriptscript--newlinenone-use_bomtrue-use_source_code_encodingtrue)

[`default_clock()`](#default_clock)

[`default_fix(o, fault)`](#default_fixo-fault)

[`Delimiter(close, *, escape='', multiline=True, quoting=False, nested=None, literal=(), change=None)`](#delimiterclose--escape-multilinetrue-quotingfalse-nestednone-literal-changenone)

[`dispatch(state_manager='state_manager', *, prefix='', suffix='')`](#dispatchstate_managerstate_manager--prefix-suffix)

[`duration_human(t, *, long=True, want_microseconds=None)`](#duration_humant--longtrue-want_microsecondsnone)

[`encode_strings(o, *, encoding='ascii')`](#encode_stringso--encodingascii)

[`extract_snippets(s, *names, comment='#')`](#extract_snippetss-names-comment)

[`eval_template_string(s, globals, locals=None, *, ...)`](#eval_template_strings-globals-localsnone--parse_expressionstrue-parse_commentsfalse-parse_whitespace_eaterfalse)

[`Event(scheduler, event, time, priority, sequence)`](#eventscheduler-event-time-priority-sequence)

[`Event.cancel()`](#eventcancel)

[`expand_tabs(s, *, column=1, first_column=1, tab_width=8)`](#expand_tabss--column1-first_column1-tab_width8)

[`fgrep(path, text, *, case_insensitive=False, encoding=None, enumerate=False)`](#fgreppath-text--case_insensitivefalse-encodingnone-enumeratefalse)

[`File(path, initial_mode="at", *, buffering=True, encoding=None, subsequent_mode=None)`](#filepath-initial_modeat--bufferingtrue-encodingnone-subsequent_modenone)

[`file_mtime(path)`](#file_mtimepath)

[`file_mtime_ns(path)`](#file_mtime_nspath)

[`file_size(path)`](#file_sizepath)

[`FileHandle(handle, *, autoflush=False)`](#filehandlehandle--autoflushfalse)

[`Filter(filter=None, *, accepts=None, name=None, types=None)`](#filterfilternone--acceptsnone-namenone-typesnone)

[`format_definition_list(pairs, margin=79, *, definition_left_column=None, definition_relative_tabs=True, indent='  ', spacer='  ', tab_width=8, term_relative_tabs=True)`](#format_definition_listpairs-margin79--definition_left_columnnone-definition_relative_tabstrue-indent---spacer---tab_width8-term_relative_tabstrue)

[`format_dict_to_ascii(d)`](#format_dict_to_asciid)

[`format_map(s, mapping)`](#format_maps-mapping)

[`Formatter(template, map=None, *, relaxed=False, stretch=True, width=79, **kwargs)`](#formattertemplate-mapnone--relaxedfalse-stretchtrue-width79-kwargs)

[`generate_tokens(s)`](#generate_tokenss)

[`gently_title(s, *, apostrophes=None, double_quotes=None)`](#gently_titles--apostrophesnone-double_quotesnone)

[`get_float(o, default=_sentinel)`](#get_floato-default_sentinel)

[`get_int(o, default=_sentinel)`](#get_into-default_sentinel)

[`get_int_or_float(o, default=_sentinel)`](#get_int_or_floato-default_sentinel)

[`grep(path, pattern, *, case_insensitive=None, encoding=None, enumerate=False, flags=0)`](#greppath-pattern--case_insensitivenone-encodingnone-enumeratefalse-flags0)

[`Heap(i=None)`](#heapinone)

[`Heap.append(o)`](#heapappendo)

[`Heap.append_and_popleft(o)`](#heapappend_and_poplefto)

[`Heap.clear()`](#heapclear)

[`Heap.copy()`](#heapcopy)

[`Heap.extend(i)`](#heapextendi)

[`Heap.popleft()`](#heappopleft)

[`Heap.popleft_and_append(o)`](#heappopleft_and_appendo)

[`Heap.queue`](#heapqueue)

[`Heap.remove(o)`](#heapremoveo)

[`int_to_words(i, *, flowery=True, ordinal=False)`](#int_to_wordsi--flowerytrue-ordinalfalse)

[`Interpolation(expression, *filters, debug='', format=None)`](#interpolationexpression-filters-debug-formatnone)

[`is_bound(cls)`](#is_boundcls)

[`is_boundinnerclass(cls)`](#is_boundinnerclasscls)

[`is_unboundinnerclass(cls)`](#is_unboundinnerclasscls)

[`iterator_context(iterator, start=0)`](#iterator_contextiterator-start0)

[`iterator_filter(iterator, *, ...)`](#iterator_filteriterator--stop_at_valueundefined-stop_at_innone-stop_at_predicatenone-stop_at_countnone-reject_valueundefined-reject_innone-reject_predicatenone-only_valueundefined-only_innone-only_predicatenone-call_everynone)

[`IteratorContext`](#iterator_contextiterator-start0)

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

[`linked_list.move(where, start=None, stop=None)`](#linked_listmovewhere-startnone-stopnone)

[`linked_list.pop(index=-1)`](#linked_listpopindex-1)

[`linked_list.prepend(object)`](#linked_listprependobject)

[`linked_list.rcount(value)`](#linked_listrcountvalue)

[`linked_list.rcut(start=None, stop=None, *, lock=None)`](#linked_listrcutstartnone-stopnone--locknone)

[`linked_list.remove(value, default=undefined)`](#linked_listremovevalue-defaultundefined)

[`linked_list.reverse()`](#linked_listreverse)

[`linked_list.rextend(iterable)`](#linked_listrextenditerable)

[`linked_list.rfind(value)`](#linked_listrfindvalue)

[`linked_list.rmatch(predicate)`](#linked_listrmatchpredicate)

[`linked_list.rmove(where, start=None, stop=None)`](#linked_listrmovewhere-startnone-stopnone)

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

[`linked_list_iterator.move(where, stop=None)`](#linked_list_iteratormovewhere-stopnone)

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

[`linked_list_iterator.rmove(where, stop=None)`](#linked_list_iteratorrmovewhere-stopnone)

[`linked_list_iterator.rpop(index=0)`](#linked_list_iteratorrpopindex0)

[`linked_list_iterator.rremove(value, default=undefined)`](#linked_list_iteratorrremovevalue-defaultundefined)

[`linked_list_iterator.rsplice(other)`](#linked_list_iteratorrspliceother)

[`linked_list_iterator.rtruncate()`](#linked_list_iteratorrtruncate)

[`linked_list_iterator.special`](#linked_list_iteratorspecial)

[`linked_list_iterator.splice(other)`](#linked_list_iteratorspliceother)

[`linked_list_iterator.truncate()`](#linked_list_iteratortruncate)

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

[`linked_list_reverse_iterator.move(where, stop=None)`](#linked_list_reverse_iteratormovewhere-stopnone)

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

[`linked_list_reverse_iterator.rmove(where, stop=None)`](#linked_list_reverse_iteratorrmovewhere-stopnone)

[`linked_list_reverse_iterator.rpop(index=0)`](#linked_list_reverse_iteratorrpopindex0)

[`linked_list_reverse_iterator.rremove(value, default=undefined)`](#linked_list_reverse_iteratorrremovevalue-defaultundefined)

[`linked_list_reverse_iterator.rsplice(other)`](#linked_list_reverse_iteratorrspliceother)

[`linked_list_reverse_iterator.rtruncate()`](#linked_list_reverse_iteratorrtruncate)

[`linked_list_reverse_iterator.special`](#linked_list_reverse_iteratorspecial)

[`linked_list_reverse_iterator.splice(other)`](#linked_list_reverse_iteratorspliceother)

[`linked_list_reverse_iterator.truncate()`](#linked_list_reverse_iteratortruncate)

[`List(list)`](#listlist)

[`literal_eval(s)`](#literal_evals)

[`load(name)`](#loadname)

[`Log(*destinations, **options)`](#logdestinations-options)

[`Log` properties](#log-properties)

[`Log.child(name='', buffered=True, *, format=..., paused=None, **kwargs)`](#logchildname-bufferedtrue--format-pausednone-kwargs)

[`Log.close(wait=True)`](#logclosewaittrue)

[`Log.enter(message='', **kwargs)`](#logentermessage-kwargs)

[`Log.exit()`](#logexit)

[`Log.flush(wait=True)`](#logflushwaittrue)

[`Log.log(*args, format=Optional('log'), flush=False, **kwargs)`](#loglogargs-formatoptionallog-flushfalse-kwargs)

[`Log.map_destination(o)`](#logmap_destinationo)

[`Log.pause()` and `Log.resume()`](#logpause-and-logresume)

[`Log.print(*args, sep=' ', end='\\n', format=Optional('print'), flush=False)`](#logprintargs-sep--endn-formatoptionalprint-flushfalse)

[`Log.reset()`](#logreset)

[`Log.route(formatter, *destinations)`](#logrouteformatter-destinations)

[`Log.write(s, format=Optional('preformatted'), flush=False)`](#logwrites-formatoptionalpreformatted-flushfalse)

[`LogDestination(types=True)`](#logdestinationtypestrue)

[`LogDestination.mappers`](#logdestinationmappers)

[`LogFormatter(format_dict, types, *, name=None)`](#logformatterformat_dict-types--namenone)

[`merge_columns(*columns, column_separator=" ", overflow_strategy=OverflowStrategy.RAISE, overflow_before=0, overflow_after=0, tab_width=8, raw=None)`](#merge_columnscolumns-column_separator--overflow_strategyoverflowstrategyraise-overflow_before0-overflow_after0-tab_width8-rawnone)

[`metadata.version`](#metadataversion)

[`ModuleManager()`](#modulemanager)

[`multipartition(s, separators, count=1, *, reverse=False, separate=True)`](#multipartitions-separators-count1--reversefalse-separatetrue)

[`multireplace(s, replacements, count=-1, *, reverse=False)`](#multireplaces-replacements-count-1--reversefalse)

[`multisplit(s, separators, *, keep=False, maxsplit=-1, reverse=False, separate=False, strip=False)`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)

[`multistrip(s, separators, left=True, right=True)`](#multistrips-separators-lefttrue-righttrue)

[`normalize_whitespace(s, separators=None, replacement=None)`](#normalize_whitespaces-separatorsnone-replacementnone)

[`OldDestination()`](#olddestination)

[`OldLog(clock=None)`](#oldlogclocknone)

[`Optional(name)`](#optionalname)

[`parse_template_string(s, *, ...)`](#parse_template_strings--parse_expressionstrue-parse_commentsfalse-parse_statementsfalse-parse_whitespace_eaterfalse-quotes--multiline_quotes-escape)

[`parse_timestamp_3339Z(s, *, timezone=None)`](#parse_timestamp_3339zs--timezonenone)

[`Pattern(s, flags=0)`](#patterns-flags0)

[`pluralize(singular, count, plural=None)`](#pluralizesingular-count-pluralnone)

[`prefix_format(time_seconds_width, time_fractional_width, thread_name_width=12, *, ascii=False)`](#prefix_formattime_seconds_width-time_fractional_width-thread_name_width12--asciifalse)

[`Print()`](#print)

[`pure_virtual()`](#pure_virtual)

[`PushbackIterator(iterable=None)`](#pushbackiteratoriterablenone)

[`PushbackIterator.next(default=None)`](#pushbackiteratornextdefaultnone)

[`PushbackIterator.push(o)`](#pushbackiteratorpusho)

[`pushd(directory)`](#pushddirectory)

[`python_delimiters`](#python_delimiters)

[`python_delimiters_version`](#python_delimiters_version)

[`re_partition(text, pattern, count=1, *, flags=0, reverse=False)`](#re_partitiontext-pattern-count1--flags0-reversefalse)

[`re_rpartition(text, pattern, count=1, *, flags=0)`](#re_rpartitiontext-pattern-count1--flags0)

[`read_python_file(path, *, newline=None, use_bom=True, use_source_code_encoding=True)`](#read_python_filepath--newlinenone-use_bomtrue-use_source_code_encodingtrue)

[`Regulator()`](#regulator)

[`Regulator.lock`](#regulatorlock)

[`Regulator.now()`](#regulatornow)

[`Regulator.sleep(t)`](#regulatorsleept)

[`Regulator.wake()`](#regulatorwake)

[`reversed_re_finditer(pattern, string, flags=0)`](#reversed_re_finditerpattern-string-flags0)

[`safe_mkdir(path)`](#safe_mkdirpath)

[`safe_unlink(path)`](#safe_unlinkpath)

[`Scheduler(regulator=default_regulator)`](#schedulerregulatordefault_regulator)

[`Scheduler.cancel(event)`](#schedulercancelevent)

[`Scheduler.non_blocking()`](#schedulernon_blocking)

[`Scheduler.queue`](#schedulerqueue)

[`Scheduler.schedule(o, time, *, absolute=False, priority=DEFAULT_PRIORITY)`](#schedulerscheduleo-time--absolutefalse-prioritydefault_priority)

[`search_path(paths, extensions=('',), *, case_sensitive=None, preserve_extension=True, want_directories=False, want_files=True)`](#search_pathpaths-extensions--case_sensitivenone-preserve_extensiontrue-want_directoriesfalse-want_filestrue)

[`SingleThreadedRegulator()`](#singlethreadedregulator)

[`Sink()`](#sink)

[`SinkEvent`](#sinkevent)

[`SinkFormatter`](#sinkformatter)

[`SpecialNodeError`](#specialnodeerror)

[`split_delimiters(s, delimiters={...}, *, state=(), yields=4)`](#split_delimiterss-delimiters--state-yields4)

[`split_quoted_strings(s, quotes=('"', "'"), *, escape='\\', multiline_quotes=(), state='')`](#split_quoted_stringss-quotes---escape-multiline_quotes-state)

[`split_text_with_code(s, *, code_indent=4, tab_width=8)`](#split_text_with_codes--code_indent4-tab_width8)

[`split_title_case(s, *, split_allcaps=True)`](#split_title_cases--split_allcapstrue)

[`sync_snippets(source, destination, filter=None, *, comment='#')`](#sync_snippetssource-destination-filternone--comment)

[`State()`](#state)

[`StateManager(state, *, on_enter='on_enter', on_exit='on_exit', state_class=None)`](#statemanagerstate--on_enteron_enter-on_exiton_exit-state_classnone)

[`Statement(statement)`](#statementstatement)

[`str_linebreaks`](#str_linebreaks)

[`str_linebreaks_without_crlf`](#str_linebreaks_without_crlf)

[`str_whitespace`](#str_whitespace)

[`str_whitespace_without_crlf`](#str_whitespace_without_crlf)

[`string(s='', *, ...)`](#strings--sourcenone-line_number1-column_number1-first_column_number1-tab_width8)

[`string.bisect(index)`](#stringbisectindex)

[`string.cat(*strings)`](#stringcatstrings)

[`string.compile(flags=0)`](#stringcompileflags0)

[`string.generate_tokens()`](#stringgenerate_tokens)

[`string.literal_eval()`](#stringliteral_eval)

[`string.multireplace(replacements, count=-1, *, reverse=False)`](#stringmultireplacereplacements-count-1--reversefalse)

[`strip_indents(lines, *, tab_width=8, linebreaks=linebreaks)`](#strip_indentslines--tab_width8-linebreakslinebreaks)

[`strip_line_comments(lines, line_comment_markers, *, escape='\\', quotes=(), multiline_quotes=(), linebreaks=linebreaks)`](#strip_line_commentslines-line_comment_markers--escape-quotes-multiline_quotes-linebreakslinebreaks)

[`test.explain(tb, write)`](#testexplaintb-write)

[`test.ExplainResult`](#testexplainresult)

[`test.finish()`](#testfinish)

[`test.main()`](#testmain)

[`test.preload(package)`](#testpreloadpackage)

[`test.raises` and `test.raises_regex`](#testraises-and-testraises_regex)

[`test.register_type_equality(type, function)`](#testregister_type_equalitytype-function)

[`test.run(name=None, module=None, permutations=None)`](#testrunnamenone-modulenone-permutationsnone)

[`test.stats`](#teststats)

[`test.suite()`](#testsuite)

[`TextFormatter(format_dict=None, *, formats=None, indent='    ', name=None, prefix=None, width=79)`](#textformatterformat_dictnone--formatsnone-indent-----namenone-prefixnone-width79)

[`ThreadSafeRegulator()`](#threadsaferegulator)

[`timestamp_3339Z(t=None, want_microseconds=None)`](#timestamp_3339ztnone-want_microsecondsnone)

[`timestamp_human(t=None, want_microseconds=None, *, tzinfo=None)`](#timestamp_humantnone-want_microsecondsnone--tzinfonone)

[`TMPFILE`](#tmpfile)

[`TmpFile(prefix='{name}', *, buffering=True, encoding=None, timestamp_format=None)`](#tmpfileprefixname--bufferingtrue-encodingnone-timestamp_formatnone)

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

[`toy_multisplit(s, separators)`](#toy_multisplits-separators)

[`TransitionError`](#transitionerror)

[`translate_filename_to_exfat(s)`](#translate_filename_to_exfats)

[`translate_filename_to_unix(s)`](#translate_filename_to_unixs)

[`try_float(o)`](#try_floato)

[`try_int(o)`](#try_into)

[`type_bound_to(instance)`](#type_bound_toinstance)

[`unbound(cls)`](#unboundcls)

[`UnboundInnerClass`](#unboundinnerclasscls)

[`UndefinedIndexError`](#undefinedindexerror)

[`unicode_format_dict(*, closed=False)`](#unicode_format_dict-closedfalse)

[`unicode_linebreaks`](#unicode_linebreaks)

[`unicode_linebreaks_without_crlf`](#unicode_linebreaks_without_crlf)

[`unicode_whitespace`](#unicode_whitespace)

[`unicode_whitespace_without_crlf`](#unicode_whitespace_without_crlf)

[`Version(s=None, *, epoch=None, release=None, release_level=None, serial=None, post=None, dev=None, local=None)`](#versionsnone--epochnone-releasenone-release_levelnone-serialnone-postnone-devnone-localnone)

[`Version.format(s)`](#versionformats)

[`whitespace`](#whitespace)

[`whitespace_without_crlf`](#whitespace_without_crlf)

[`wrap_words(words, margin=79, *, code_indent=None, indent='', left_column=1, tab_width=8, two_spaces=True, raw=None)`](#wrap_wordswords-margin79--code_indentnone-indent-left_column1-tab_width8-two_spacestrue-rawnone)

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
the instance.  This changes the signature of the inner class's  `__new__`
and `__init__` methods from
```Python
def __new__(cls, *args, **kwargs):`
def __init__(self, *args, **kwargs):`
```
to
```Python
def __new__(cls, outer, *args, **kwargs):
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
  passed in as the second argument to `__new__` and  `__init__`,
  after `cls` and `self` respectively.

`BoundInnerClass` only binds `__new__` and `__init__` methods the
decorated class *itself* defines.  Methods inherited from base
classes are left alone: a regular base class's methods receive
only the arguments you pass in, and a bound parent class injects
`outer` into its own methods itself.

Note that this has an implication for all subclasses.
If class ***B*** is decorated with `BoundInnerClass`,
and class ***S*** is a subclass of ***B***, such that
`issubclass(`***S***`, `***B***`)`,
class ***S*** *must* be decorated with either
`BoundInnerClass` or `UnboundInnerClass`.

Base classes are matched by class *identity*, never by name.
In particular, an inner class may inherit from a same-named
inner class of an ancestor outer class--`class MyApp(BaseApp)`
defining `class Config(BaseApp.Config)`--and bare
`super().__init__()` delivers `outer` automatically, exactly
as it does for any other bound base.
</dd></dl>

#### `UnboundInnerClass(cls)`

<dl><dd>

Class decorator for an inner class that omits passing
the outer instance in as an argument to its `__new__` and
`__init__` methods.

If class ***B*** is decorated with `BoundInnerClass`,
and class ***S*** is a subclass of ***B***, such that
`issubclass(`***S***`, `***B***`)` returns `True`,
class ***S*** *must* be decorated with either
`BoundInnerClass` or `UnboundInnerClass` in order for
its base classes to become bound inner classes.  Which
decorator you use depends on whether or not you want
`outer` passed in to S's `__new__` and `__init__` methods.

Speaking precisely: an "unbound inner class" *is*
bound to the outer instance, in every important way.
For example, `is_bound` on an unbound inner class
will still return true.  The practical difference between
a class decorated with `BoundInnerClass` and one
decorated with `UnboundInnerClass` is that the former
will pass in `outer` to its `__new__` and `__init__`
methods, and the latter will not.

(The name is a bit of a misnomer--a class decorated
with `UnboundInnerClass` is still bound to the outer
instance.  The name was chosen because it's obvious
and easy to remember, even if it's technically
inaccurate.)

</dd></dl>

#### `bound_inner_base(cls)`

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
    __slots__ = ('x', 'y', 'z') + BOUNDINNERCLASS_OUTER_SLOTS

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

#### `ansi_color_depth()`

<dl><dd>

Guesses the terminal's ANSI color depth from the `COLORTERM` and
`TERM` environment variables, returning `'truecolor'`, `'256color'`,
or `'16color'` (defaulting to `'truecolor'` when nothing says
otherwise).  Pairs with [`can_colorize`](#can_colorizefilenone) to
choose a palette; see
[`big.stylesheet.best_palette`](#best_palettefilenone).

</dd></dl>

#### `can_colorize(*, file=None)`

<dl><dd>

Returns `True` if `file` (default `sys.stdout`) should get colorized
output.  On Python 3.13+ this is exactly CPython's
`_colorize.can_colorize`; on 3.12 and earlier it reimplements the same
logic.  `PYTHON_COLORS` forces the answer (unless running under `-E`/
`-I`); otherwise `NO_COLOR` disables color, `FORCE_COLOR` enables it,
`TERM=dumb` disables it, on Windows the console must support
virtual-terminal sequences, and failing all of those `file` must be a
tty.

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

`get_int_or_float` is designed for converting strings: it's a
sort of poor man's `ast.literal_eval`.  If `o` is a string
(`str`, `bytes`, or `bytearray`) that reads as an int, returns
that int; if it reads as a float instead, returns that float.
(Anything `float()` accepts "reads as a float", including
`"inf"` and `"nan"`.)

If `o` is already an int, returns `o` unchanged.  If `o` is
already a float, returns `int(o)` if that's equal to `o`,
otherwise returns `o` unchanged.  (Infinities and NaNs are
returned unchanged.)

Anything else--including number-like objects such as
`decimal.Decimal` and `fractions.Fraction`--is outside
`get_int_or_float`'s purview: it returns the default value.
If you don't pass in an explicit default value, the default
value is `o`.
</dd></dl>

#### `literal_eval(s)`

<dl><dd>

Wrapper around
[`ast.literal_eval`](https://docs.python.org/3/library/ast.html#ast.literal_eval)
that preserves `big.string` provenance.

`literal_eval(s)` evaluates `s` exactly like `ast.literal_eval`.
If `s` is an ordinary `str`, or the result isn't a `str`, the
result is exactly `ast.literal_eval`'s result.

If `s` is a `big.string` and the result is a `str`,
`literal_eval` tries to preserve provenance, in one of three
ways, best-first:

* If the decoded value appears verbatim in `s`—there are no
  escape sequences—the result is a true slice of `s`.  Both
  `where` and `context` work, and every character knows its
  true position.
* If the literal contains escape sequences, the result is
  assembled from verbatim slices of `s`, splicing in a
  synthesized character for each escape sequence.  Every
  character still reports a true line and column—a decoded
  escape reports the position of its escape sequence—but
  `context` is unavailable, as the result is no longer one
  contiguous slice of the original.
* If `s` opens with a quoted string whose contents are exactly
  the decoded value—an escape-free literal followed by trailing
  text `ast.literal_eval` tolerates, like a comment—the result
  is that true slice, found by reparsing the source with big's
  own [`split_quoted_strings`](#split_quoted_stringss-quotes---escape-multiline_quotes-state).
  `where` and `context` both work.

If the decoded value can't be honestly mapped back onto the
source—implicit string concatenation (`"a" "b"`), or a literal
whose escape sequences make the value differ from the source
text, followed by trailing text—`literal_eval` returns
a plain `str`.  This is `big.string`'s standing policy: a
position is a promise, and failing loudly (plain `str` has no
`.where`) beats reporting positions that are confidently wrong.

In every case the value is character-for-character identical to
`ast.literal_eval`'s result; only the type and metadata vary.
</dd></dl>

#### `load(name)`

<dl><dd>

Puts the local checkout of `name` — a package or a single-file
module — on `sys.path`, so your code runs against the source tree
instead of an installed copy, and returns the imported module — so
you can write `mypackage = big.load('mypackage')` in place of a
load-then-import pair.  Handy for tests and prototypes that should
exercise the tree you're editing, not whatever's installed.

Searches for `name`/`__init__.py` or `name`.py in the directory
containing the running script (`sys.argv[0]`), then in each parent
directory; the directory nearest the script wins, and within one
directory a package beats a module of the same name (the import
runs under Python's own rules).  (In the REPL, and anywhere else
`sys.argv[0]` is the empty string, there's no script to anchor to,
so the search starts in the current directory.)  Raises
`FileNotFoundError` if it's not found.  Imports `name` and confirms
it came from the checkout.  The directory added to `sys.path` is
`pathlib.Path(module.__file__).parents[1]` for a package,
`.parent` for a module.

(big's own test suite can't use this to find big--it lives in the
very package being located--so it bootstraps with its own copy of
this logic.  Every *other* package is paradox-free.)
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

`mm.export(*args, force=False)` adds symbols to `__all__`.
When used as a decorator, adds the decorated function or class
by name.  When called with strings, adds those strings to
`__all__`.  Exporting a name that's already in `__all__` raises
`ValueError`--it's nearly always a bug (a stale hand-rolled
`__all__`, or a stray decorator on an internal function).  If
the redundancy is intentional, pass `force=True`: it never
raises, and `__all__` still only lists each name once.

`mm.delete(*args, force=False)` marks symbols for deletion.
When used as a decorator, marks the decorated function or class
for deletion.  When called with strings, marks those names for
deletion.  Deleting a name that's already scheduled for deletion
raises `ValueError`, unless you use `force=True`.

When the `ModuleManager` instance is called, it deletes all
symbols on the deletions list from the module namespace.
It also automatically deletes itself, and any module-level
references to its `export` and `delete` methods.
</dd></dl>

#### `pluralize(singular, count, plural=None)`

<dl><dd>

Returns a string pluralizing a string singular as appropriate.

`singular` should be the singular form of a noun. `count` should
be a number, used to calculate whether you want the singular
or plural form of that noun.  If `plural` is `None` (the default),
the plural form is computed by taking the the singular form
and appending an `'s'``.  For nouns with an irregular plural,
you'll need to pass it in explicitly:

```Python
  >>> pluralize('box', 2, 'boxes')
  'boxes'
```

Returns the plural form for every value of count except exactly
1; if singular is `'apple'`, `count=0` and `count=1.5` both return
`'apples'`.

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

#### `atomic_write(path, mode='w', *, encoding=None, errors=None, newline=None)`

<dl><dd>

A context manager that writes a file atomically: readers of `path`
see either the old contents or the new contents, never a mixture,
no matter when the writer crashes or the machine loses power.

Yields a file object open for writing.  Write the new contents
to it as usual:

```Python
with big.atomic_write(path) as f:
    f.write(everything)
```

If the nested block exits normally, the new contents atomically
replace the old file at `path` (or create it, if it didn't exist).
If the nested block raises, the file at `path` is completely
untouched, and the partially-written new contents are removed.

How it works: `atomic_write` writes to a temporary file in the
same directory as `path`.  On success, the temporary file is
flushed, fsync'ed, and renamed over `path` with `os.replace`,
which is atomic.  ("The same directory" matters: rename is only
atomic within one filesystem.)  On failure, the temporary file
is unlinked.

`path` should be a `str`, `bytes`, or `os.PathLike` object.

`mode` selects how you write the new contents:

* `'w'`, `'wt'`, or `'wb'` -- write.  The new file starts empty;
  you write it from scratch.
* `'a'`, `'at'`, or `'ab'` -- append.  The old contents (if any)
  are preserved, and you write additional contents after them.
* `'r+'`, `'r+t'`, or `'r+b'` -- update in place.  The old contents
  are preserved and the file is positioned at the start, so you can
  read and rewrite them; like `open`, `'r+'` requires `path` to
  already exist.

For append and update, `atomic_write` copies the existing file into
the temporary file before handing it to you, so that even an append
or an in-place edit is atomic: readers see the whole old file or the
whole new file, never a mixture.  Note the cost: this means copying
the entire original file first, before writing.  "atomic" append is
a poor fit for a hot loop (e.g. appending one line at a time to a
large log)--each call to `atomic_write` will recopy the *entire file.*

`encoding`, `errors`, and `newline` work as they do for `open`, and
like `open`, they're only permitted in text mode.

Permissions: if a file already exists at `path`, the new file
inherits its permissions.  If `path` is new, it gets the same
default permissions an ordinary `open` would give it (respecting
the umask)--not the private permissions temporary files usually
get.

Closing the yielded file object yourself is harmless, though it
means `atomic_write` can't fsync the contents (`close` already
flushed them; the rename is still atomic).

If `path` exists it must be a regular file.  `atomic_write` raises
if it's a directory (`IsADirectoryError`), a symbolic link, or
another special file (`OSError`)--rather than let `os.replace` do
something surprising, like replace a symlink with the new file
(detaching the link from its target).  This check samples the path,
so it's necessarily racy: if the path is swapped for a directory or
symlink after the check, the final rename simply fails on its own.
The check just turns the common mistake into a clear error up front.

Caveat: the hard link count isn't preserved--replacing one name of
a multiply-linked file detaches it from the other names.
</dd></dl>

#### `fgrep(path, text, *, case_insensitive=False, encoding=None, enumerate=False)`

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
Lines are split according to big's own definition of linebreaks (see
[`linebreaks`](#linebreaks) and [`bytes_linebreaks`](#bytes_linebreaks)
in `big.text`)--which is exactly what `str.splitlines` and
`bytes.splitlines` split on.  In particular, binary-mode lines may end
in `\r\n`, `\r`, or `\n`, and all three are recognized and stripped.

If `enumerate` is true, returns a list of tuples of (line_number, line).
The first line of the file is line number 1.

For simplicity of implementation, the entire file is read in to memory
at one time.  If `case_insensitive` is true, `fgrep` also makes a
case-folded copy.
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

#### `grep(path, pattern, *, case_insensitive=None, encoding=None, enumerate=False, flags=0)`

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

`case_insensitive` controls case sensitivity explicitly, and may be
`None` (the default), `True`, or `False`:

* `None` means make no effort in either direction.  A `str` or
  `bytes` pattern is compiled with `flags` exactly as given; `flags`
  is 0 by default, which means case-sensitive.  A precompiled
  pattern keeps whatever flags it already has.
* `True` forces a case-insensitive search, adding `re.IGNORECASE`.
* `False` forces a case-sensitive search, removing `re.IGNORECASE`.

When `case_insensitive` is `True` or `False`, the pattern is
(re)compiled to honor it--even a precompiled `re.Pattern`.  (One
limitation: an inline `(?i)` flag baked into the pattern text itself
isn't affected by `case_insensitive=False`; it lives in the pattern,
not the flags.)  Passing `case_insensitive=True` is equivalent to
adding `re.IGNORECASE` to `flags` yourself, if `pattern` is `str` or `bytes`.

Returns a list of lines in the file matching the pattern.  The lines
are either strings or bytes objects, depending on the type of `text`.
The lines have their newlines stripped but preserve all other whitespace.
Lines are split according to big's own definition of linebreaks (see
[`linebreaks`](#linebreaks) and [`bytes_linebreaks`](#bytes_linebreaks)
in `big.text`)--which is exactly what `str.splitlines` and
`bytes.splitlines` split on.  In particular, binary-mode lines may end
in `\r\n`, `\r`, or `\n`, and all three are recognized and stripped.

If `enumerate` is true, returns a list of tuples of `(line_number, line)`.
The first line of the file is line number 1.

For simplicity of implementation, the entire file is read in to memory
at one time.

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

The original directory is captured when the block is
*entered*, not when the pushd object is constructed.
(Like the shell builtin: pushd pushes the directory you're
in right now.)  This also means a single pushd object can
be reused.

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

A symlink at `path` that doesn't lead to a directory--a
symlink to a file, or a dangling symlink--counts as a file:
it's unlinked.  A symlink that leads to a directory is left
alone; a directory exists at `path`, which is the goal.

This function can still fail:

* `path` could be on a read-only filesystem.
* You might lack the permissions to create `path`.
* You could ask to create the directory `x/y`
   and `x` is a file (not a directory).

</dd></dl>

#### `safe_unlink(path)`

<dl><dd>

Unlinks `path`, if `path` exists and is a file.

A symlink at `path` that doesn't lead to a directory--a
symlink to a file, or a dangling symlink--counts as a file.
(Unlinking it removes the symlink itself, never its target.)
A symlink that leads to a directory is left alone.
</dd></dl>


#### `search_path(paths, extensions=('',), *, case_sensitive=None, preserve_extension=True, want_directories=False, want_files=True)`

<dl><dd>

Search a list of directories for a file.  Given a sequence
of directories, an optional list of file extensions, and a
filename, searches those directories for a file with that
name and possibly one of those file extensions.

Returns a function:

```Python
    search(filename)
```

which returns either a `pathlib.Path` object on success (it found a
matching file) or `None` on failure (it couldn't find a matching file).

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

(Caveat: on Windows, the underlying filesystem globbing is itself
case-insensitive, and `search_path` doesn't attempt to compensate.
`case_sensitive=True` on Windows still finds files whose names
match case-insensitively.)

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
   `ctx.countdown` will be undefined, and accessing it will raise
   `AttributeError` (so `hasattr(ctx, 'countdown')` tells you
   whether it's available).
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
   if it doesn't, `ctx.length` will be undefined, and accessing
   it will raise `AttributeError` (so `hasattr(ctx, 'length')`
   tells you whether it's available).
</dd><dt>

`ctx.next`
</dt><dd>
   contains the next value to be yielded by
   this iterator if there is one.  (If `o` is the last
   value yielded by the iterator, `ctx.next` will be
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

#### `iterator_filter(iterator, *, stop_at_value=undefined, stop_at_in=None, stop_at_predicate=None, stop_at_count=None, reject_value=undefined, reject_in=None, reject_predicate=None, only_value=undefined, only_in=None, only_predicate=None, call_every=None)`

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

There are two additional rules:

* `stop_at_count`, an integer.  The iterator
becomes exhausted after yielding `stop_at_count` items.  If `stop_at_count`
is initially `<= 0`, the iterator is initialized in an exhausted state.

* `call_every`, a 2-tuple of `(callable, number)`.  This calls the
`callable` callable--without arguments--after every `number` values
yielded.  Passing in `call_every=(foo, 4)`
for an iterator that yields 14 values would call `foo()` after
yielding 4 values, again after yielding 8 values, and a third
time after yielding 12 values.

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

The best version of debug prints you ever saw.

`Log` is a lightweight, thread-safe logging object intended for
*print-style debugging*.  It's deliberately **not** a full-fledged
"enterprise" application logger like Python's
[`logging`](https://docs.python.org/3/library/logging.html) module--no
severity levels, no handler configuration files.  You are the writer
*and* the reader; `Log` just makes the story you print to yourself
enormously better: elapsed times, thread names, nesting with
indentation, call-out boxes, effortless redirection, and pause/resume
instead of commenting your prints out.

The cheapest log is the one that's off:

```Python
if log:
    log(f"boiler state: {pprint.pformat(hopper)}")
```

A `Log` handle is true while logging to it would actually deliver:
it has real destinations, it\'s open, and it isn\'t paused (directly
or by an ancestor).  Remove the last destination, close the log, or
pause it, and it\'s false--guarding with `if log:` means the f-string
is *never even evaluated* when the log is dark, whatever made it
dark.  Logging you can afford to leave in.

Internally, `Log` routes messages from `LogFormatter` objects (rendering
policy) to `LogDestination` objects (output mechanism), running all work
through a job queue with fault handling--a misbehaving destination is
retried, then dropped; your program never crashes because of its log.

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

#### `default_fix(o, fault)`

<dl><dd>

The default "fix" callback used by [`Log`](#logdestinations-options).
Does nothing, and returns `None`--meaning "I didn't fix it".

When a `LogFormatter` or `LogDestination` raises an exception, `Log` calls
the log's `fix` callback, passing in the offending object and the
exception.  If `fix` returns a true value, the failed operation is
retried (up to `retries` times).  If the fault can't be fixed, the
offending object is removed from the log's routing, and the log
carries on without it.

The drop itself is silent, on purpose: the log exists to serve *your*
logging, never its own--it will never inject a message you didn't
write into your output.  If you want to know when a formatter or
destination dies, `fix` is your hook: it's consulted on every fault,
and if it returns false, the drop follows immediately--so a `fix`
that records (or prints, or logs elsewhere) before declining is a
complete death notification.  One subtlety: a `fix` that keeps
returning true until `retries` is exhausted is *not* called again
for the final drop--if you always return true, count your own calls.
</dd></dl>

#### `LogDestination.mappers`

<dl><dd>

A class attribute of [`LogDestination`](#logdestinationtypestrue)--a
single shared list of callables extending
[`Log.map_destination`](#logmap_destinationo).
Each mapper is called with a prospective destination object; it should
return a [`LogDestination`](#logdestinationtypestrue), or `None` meaning
"not mine, keep looking".  Append your mapper to
`LogDestination.mappers`; user-registered mappers run before the
built-in mappings.
</dd></dl>

#### `Log(*destinations, **options)`

<dl><dd>

The log object.  Messages logged to it are formatted by a
[`LogFormatter`](#logformatterformat_dict-types--namenone) and routed to
one or more [`LogDestination`](#logdestinationtypestrue) objects.

`destinations` may be `LogDestination` objects, or any value
[`map_destination`](#logmap_destinationo) understands: `print`,
a callable, a list, a path (`str`, `bytes`, or `pathlib.Path`),
a text file object, [`TMPFILE`](#tmpfile), or `None`.
If you don't pass any destinations, the log prints.

Keyword-only options:

* `buffered` (default `False`) -- buffer messages in the root session
  until flushed.
* `clock` (default [`Clock`](#clock)) -- a `Clock` subclass, or a
  plain callable returning integer nanoseconds (it's wrapped
  automatically).
* `fix` (default [`default_fix`](#default_fixo-fault)) -- the
  fault-repair callback; see `default_fix`.
* `formatter` -- an explicit `LogFormatter`; default is
  `TextFormatter()`.  All formatter configuration--`formats`,
  `prefix`, `width`, `indent`--lives on the formatter: construct
  your own
  [`TextFormatter`](#textformatterformat_dictnone--formatsnone-indent-----namenone-prefixnone-width79)
  and pass it in.  (For example,
  `formatter=TextFormatter(formats={"start": None, "end": None})`
  turns off the banners.)
* `name` (default `\'Log\'`) -- the log\'s name, shown in banners.
* `paused` (default `False`) -- start out paused.
* `retries` (default `1`) -- fault retry budget; see `default_fix`.
* `threaded` (default `True`) -- run the log\'s work in a worker
  thread.  (`threading=` is accepted as a deprecated alias.)

A `Log` is a context manager; leaving the `with` block closes it.
`bool(log)` is true if the log has at least one true destination--
so `if log: log(...)` skips even evaluating the log message\'s
arguments when the log is dark.

Logs start *lazily*: until the first message is actually logged,
`Log` never touches your destinations--no file is opened, no
temporary filename is computed, and no start banner is printed.
</dd></dl>

#### `Log.log(*args, format=Optional('log'), flush=False, **kwargs)`

<dl><dd>

Logs a message.  Positional arguments become lines of the message;
keyword arguments are rendered as additional `name=value` lines.
`format` selects a named format from the formatter\'s format tree.
If `flush` is true, flushes the log afterwards.
</dd></dl>

#### `Log.print(*args, sep=' ', end='\\n', format=Optional('print'), flush=False)`

<dl><dd>

Logs a message with `print` semantics: arguments are joined with
`sep` and terminated with `end`.  Calling the log object directly--
`log("hello")`--calls `print`.
</dd></dl>

#### `Log.write(s, format=Optional('preformatted'), flush=False)`

<dl><dd>

Logs a preformatted string, verbatim: no prefix, no formatting,
no whitespace cleanup, no appended newline--you own every byte.
(Its `preformatted` format declares `"verbatim": True`, which any
format may do to skip the render pipeline's rstrip-and-newline
cleanup.)
</dd></dl>

#### `Log.enter(message='', **kwargs)`

<dl><dd>

Opens a nested block in the log: prints an "enter" banner, and
indents every message logged until the matching
[`exit()`](#logexit) call.  Blocks nest.

Returns a context manager: exiting it closes the block, so
`with log.enter("subsystem"):` works, as do bare `enter()`/`exit()`
pairs.  If the log is closed or paused, returns an inert context
manager that does nothing.
</dd></dl>

#### `Log.exit()`

<dl><dd>

Closes the most deeply nested [`enter()`](#logentermessage-kwargs)
block: prints an "exit" banner (with the elapsed time inside the
block) and removes one level of indent.  Extra `exit()` calls are
harmless no-ops.
</dd></dl>

#### `Log.child(name='', buffered=True, *, format=..., paused=None, **kwargs)`

<dl><dd>

Creates and returns a child log handle--like
[`enter()`](#logentermessage-kwargs), but without the automatic
nesting-stack bookkeeping.  The child is its own context manager and
must be closed independently.  Child messages are buffered by default,
so a child\'s output is contiguous in the log even when other threads
log concurrently.
</dd></dl>

#### `Log.close(wait=True)`

<dl><dd>

Closes the log: unwinds any open `enter()` blocks (deepest first),
prints the end banner, and flushes all destinations.  If `wait` is
true and the log is threaded, blocks until the worker thread has
finished the log\'s outstanding work.  Closing is idempotent.
</dd></dl>

#### `Log.flush(wait=True)`

<dl><dd>

Flushes the log: buffered sessions push their messages upstream, and
every destination is flushed (e.g. a buffered
[`File`](#filepath-initial_modeat--bufferingtrue-encodingnone-subsequent_modenone)
writes its accumulated output to disk).
</dd></dl>

#### `Log.pause()` and `Log.resume()`

<dl><dd>

Pause and resume the log.  A paused log ignores its logging
methods--`write`, `print`, `__call__`, `log`, and `enter`: no
messages, no banners, no destination activity--the runtime equivalent
of commenting out your debug prints.  One deliberate exception:
`exit()` still closes the deepest open `enter()` block, and emits
its exit banner--nesting tracks your program's structure, paused
or not.  (Likewise, closing an `enter()` context manager closes
the block.)

Pause is *hierarchical*: pausing a handle silences its entire
subtree--including child handles held elsewhere--and pausing a child
handle silences just that subtree.

Pause state is a counter: `pause()` increments, `resume()` decrements
(clamping at zero); the log is paused while it\'s nonzero.  `pause()`
returns a context manager that calls `resume()` on exit.

The read-only property `Log.paused` is `True`/`False` (or `None` if
the log is closed).  The settable property `Log.paused_on_reset` is
the paused state [`reset()`](#logreset) restores.
</dd></dl>

#### `Log.destinations`

<dl><dd>

The destinations of the log's main formatter, as a list.  *Settable*:
assign a list or tuple of destinations (anything
[`Log.map_destination`](#logmap_destinationo) understands) to
reconfigure the log live.  Duplicates are a `ValueError`--including
the same file reached by different spellings of its path.

Destinations *removed* by the assignment are flushed first--pending
buffered content is the user's data, written, never dropped--then
ended and unregistered.  Destinations *added* while the log is
running receive a "recap": the start banner, and the enter banner of
each open block whose banner has already been delivered, so the
newcomer's output reads as a coherent log from the top.  (A buffered
block's contents haven't been delivered to anyone yet; they arrive
for everybody, newcomers included, when the block flushes.)

Every `LogDestination` also has an `owner` property: the `Log` it's
currently attached to, or `None`.

(Destinations routed to other formatters via
[`route()`](#logrouteparent-children) are not affected.)
</dd></dl>

#### `Log.reset()`

<dl><dd>

Closes and reopens the log: a fresh session with a fresh start time.
The next message logged prints a new start banner and restarts every
destination--for example,
[`TmpFile`](#tmpfileprefixname--bufferingtrue-encodingnone-timestamp_formatnone)
computes a fresh filename.  If the process is exiting, `reset` does
nothing.
</dd></dl>

#### `Log.route(formatter, *destinations)`

<dl><dd>

Adds another route to the log: `formatter` renders every message,
and the rendered output is written to each of `destinations`.
A log may have any number of formatter routes--e.g. a
`TextFormatter` writing to the screen *and* an
[`ASCIIFormatter`](#asciiformatter) writing bytes to a file.

Routing is type-checked: every destination must accept the types the
formatter renders (`str`, `bytes`, [`SinkEvent`](#sinkevent), ...).
Destinations that want `SinkEvent`s (like
[`Sink`](#sink)) are automatically routed to a companion
[`SinkFormatter`](#sinkformatter).
</dd></dl>

#### `Log.map_destination(o)`

<dl><dd>

Static method.  Maps a value to a
[`LogDestination`](#logdestinationtypestrue):
`LogDestination` objects pass through; `print` maps to
[`Print`](#print); callables map to
[`Callable`](#callablecallable); lists map to [`List`](#listlist);
`str`/`bytes`/`pathlib.Path` map to
[`File`](#filepath-initial_modeat--bufferingtrue-encodingnone-subsequent_modenone);
text file objects map to [`FileHandle`](#filehandlehandle--autoflushfalse);
[`TMPFILE`](#tmpfile) maps to a `TmpFile`; `None` maps to
`NoneType`.  User-registered
[`LogDestination.mappers`](#logdestinationmappers) run first.
</dd></dl>

#### `Log` properties

<dl><dd>

* `clock` -- the underlying clock callable (default
  [`default_clock`](#default_clock)).
* `closed` -- true if the log has been closed.
* `dirty` -- true if the log has unflushed messages.
* `formatter` -- the log\'s default formatter.
* `name` -- the log\'s name.
* `nesting` -- a tuple of the currently open `enter()` blocks.
* `paused`, `paused_on_reset` -- see [`Log.pause()`](#logpause-and-logresume).
* `start_time_ns`, `start_time_epoch` -- when this log (session)
  started, in monotonic nanoseconds and seconds-since-the-epoch.
* `threaded` -- whether the log runs a worker thread.
* `timestamp_clock` -- the wall-clock callable (default `time.time`).
</dd></dl>

#### `Clock`

<dl><dd>

The default clock class for [`Log`](#logdestinations-options).
Captures `initial` (monotonic nanoseconds) and `epoch` (wall time)
at construction; calling it returns the current monotonic time.
Also provides `delta_to_seconds(delta)` and
`time_to_timestamp(time)`.  Subclass it (or just pass a plain
nanoseconds-returning callable to `Log(clock=)`) to control time
in tests.
</dd></dl>

#### `LogDestination(types=True)`

<dl><dd>

Abstract base class for log outputs.  A destination receives
*rendered* messages via `write(o)`, plus lifecycle calls:
`start(session)` when logging begins, `end()` when the log closes,
and `flush()`.  `types` declares what types `write` accepts
(`True` means anything; otherwise a set of types such as
`{str}`, `{bytes}`, or `{SinkEvent}`)--routing is type-checked
against the formatter.

Subclasses should implement `__eq__` and `__hash__`; duplicate
destinations are rejected at routing time.

If your `start()` (or `flush()`) does fallible work--opening a
file, connecting a socket--do that work *before* calling
`super().start()` (and before discarding any buffered state).  A
failing lifecycle call goes through the log\'s fault handling: if
`fix()` repairs the problem, the *same call is retried*--and the
retry only works if the failed attempt didn\'t already commit.
(Committing first turns the retry into "can\'t start, it was
already started".)  Fallible work first, state changes after
success.

Built-in destinations:

* [`Buffer`](#bufferdestinationnone), [`Callable`](#callablecallable),
  [`File`](#filepath-initial_modeat--bufferingtrue-encodingnone-subsequent_modenone),
  [`FileHandle`](#filehandlehandle--autoflushfalse),
  [`List`](#listlist), `NoneType`, [`Print`](#print),
  [`Sink`](#sink), and
  [`TmpFile`](#tmpfileprefixname--bufferingtrue-encodingnone-timestamp_formatnone).
</dd></dl>

#### `Buffer(destination=None)`

<dl><dd>

A destination that buffers rendered messages, then writes them to an
underlying destination (default: `Print()`) all at once when flushed.

`Buffer` owns the underlying destination\'s lifecycle--`register`,
`start`, `end`, and `unregister` are forwarded--so stateful
destinations work underneath it: a
[`File`](#filepath-initial_modeat--bufferingtrue-encodingnone-subsequent_modenone)
opens its file, a [`TmpFile`](#tmpfileprefixname--bufferingtrue-encodingnone-timestamp_formatnone)
computes its filename, a [`Sink`](#sink) records its start and end
events.
</dd></dl>

#### `Callable(callable)`

<dl><dd>

A destination wrapping a callable; calls it once per rendered message.
</dd></dl>

#### `File(path, initial_mode="at", *, buffering=True, encoding=None, subsequent_mode=None)`

<dl><dd>

A destination writing to a file.  With `buffering=True` (the default)
messages accumulate in memory and the file is opened, written, and
closed in one operation per flush.  With `buffering=False` the file
is opened at start and every message is written and flushed
immediately.

The first open uses `initial_mode`; subsequent opens (after a flush
or a [`reset()`](#logreset)) use `subsequent_mode`, which defaults to
`initial_mode` with the action changed to append.  A binary mode
makes this a `bytes` destination (pair it with
[`ASCIIFormatter`](#asciiformatter)).  Two `File`s are equal if their
resolved paths are equal.
</dd></dl>

#### `FileHandle(handle, *, autoflush=False)`

<dl><dd>

A destination wrapping an already-open file object.  Text or binary
is detected from the handle.
</dd></dl>

#### `List(list)`

<dl><dd>

A destination appending each rendered message to a list.
</dd></dl>

#### `Print()`

<dl><dd>

A destination that prints each rendered message.
</dd></dl>

#### `TMPFILE`

<dl><dd>

A sentinel value; pass it as a destination to log to an
automatically-named temporary file (a
[`TmpFile`](#tmpfileprefixname--bufferingtrue-encodingnone-timestamp_formatnone)).
</dd></dl>

#### `TmpFile(prefix='{name}', *, buffering=True, encoding=None, timestamp_format=None)`

<dl><dd>

A [`File`](#filepath-initial_modeat--bufferingtrue-encodingnone-subsequent_modenone)
subclass that computes a timestamped filename in the system temp
directory, approximately:

    tempfile.gettempdir() / "{prefix}.{timestamp}.{pid}.{thread}.txt"

The filename is recomputed every time logging starts--so after a
[`reset()`](#logreset), you get a fresh file.
</dd></dl>

#### `LogFormatter(format_dict, types, *, name=None)`

<dl><dd>

Abstract base class for rendering policy.  A formatter owns a
"format tree" (a dict of named formats, each with a template and
optional values, supporting inheritance via a `\'base\'` key), declares
the `types` it renders to, and splits its work in two:
`State.prepare(message)` runs eagerly on the logging thread,
capturing everything volatile; `render(message)` runs later (on the
worker thread, if threaded) and does the expensive work.
</dd></dl>

#### `TextFormatter(format_dict=None, *, formats=None, indent='    ', name=None, prefix=None, width=79)`

<dl><dd>

The standard formatter; renders messages to `str` using
[`big.template.Formatter`](#formattertemplate-mapnone--relaxedfalse-stretchtrue-width79-kwargs)
templates.

The default format tree provides: the root template
(`\'{prefix}{message}\\n\'`), call-out boxes (`box`, `box2`), session
banners (`start`, `end`), nested-block banners (`enter`, `exit`),
and `preformatted` (used by `write()`).

The default art is *open unicode*: box-drawing characters, with no
right-hand borders, and no lid over the enter/exit label cells.
Open art is immune to the classic misalignment where a viewer
substitutes box-drawing glyphs from a different-width font--in open
art, a vertical stroke only ever needs to align with another
vertical stroke that has identical characters to its left, which
survives any font.  Four trees are available:

* `unicode_format_dict()` -- open unicode (the default).
* `unicode_format_dict(closed=True)` -- fully closed
  boxes: right borders, lids, corners.  Beautiful when your font
  renders box-drawing characters at the same width as everything
  else; ragged on the right when it doesn't.
* `ascii_format_dict()` -- open ASCII.  Pure ASCII
  always aligns, so this art keeps the enter/exit label lids (the
  T junctions render as `+`).
* `ascii_format_dict(closed=True)` -- closed ASCII:
  fully boxed *and* aligned on every terminal ever made.

These are module-level functions
([`big.unicode_format_dict`](#unicode_format_dict-closedfalse) and
[`big.ascii_format_dict`](#ascii_format_dict-closedfalse)); each
returns a fresh format tree you can pass as `format_dict` (or edit
first).

In closed art, a line whose content overflows the width runs open--
its right border is omitted rather than drawn glued onto the
overflow.

* `formats` merges named formats into the tree.  Each value must be
  a dict containing a str `\'template\'`--or `None`, which *disables*
  an existing format (a disabled banner simply doesn\'t print).
  Templates are validated immediately at construction.
* `prefix` replaces the default line prefix (see
  [`prefix_format`](#prefix_formattime_seconds_width-time_fractional_width-thread_name_width12--indenttrue-asciifalse)).
* `indent` is the per-nesting-level indent string.
* `width` is the target line width; rule lines (`{line*}`) pad to it.

Any format name in the tree works as a log method:
`log.box("hi")` logs with the `box` format.
</dd></dl>

#### `ASCIIFormatter`

<dl><dd>

A [`TextFormatter`](#textformatterformat_dictnone--formatsnone-indent-----namenone-prefixnone-width79)
subclass that renders to `bytes` containing ASCII--pair it with a
binary-mode [`File`](#filepath-initial_modeat--bufferingtrue-encodingnone-subsequent_modenone).
Messages containing non-ASCII characters are encoded with backslash
escapes: `log('café')` renders as `b'caf\\xe9'`.  Nothing fails,
nothing is lost--a log statement never crashes the program it's
observing.
</dd></dl>

#### `SinkFormatter`

<dl><dd>

A [`LogFormatter`](#logformatterformat_dict-types--namenone) that
renders messages into [`SinkEvent`](#sinkevent) objects instead of
text--structured logging as "just another formatter".  A
`SinkFormatter` does *no* text formatting: it isn't a `TextFormatter`
and has no format tree.  Each event carries the message\'s structured
fields--elapsed time, nesting depth, thread, format name, and the raw
message text--but no rendered string.  How to turn those into text,
if at all, is the consumer\'s business.

You rarely construct one yourself: passing a
[`Sink`](#sink) (or any `SinkEvent`-typed destination) to `Log`
automatically routes it through a companion `SinkFormatter`, which
borrows its parent formatter\'s format *names* so the same log
methods (`log.box`, `log.enter`, ...) produce the matching events.
</dd></dl>

#### `Filter(filter=None, *, accepts=None, name=None, types=None)`

<dl><dd>

A [`LogFormatter`](#logformatterformat_dict-types--namenone) that sits
*downstream* of another formatter, transforming--or dropping--its
rendered output.  By default a `Filter` consumes and produces `str`,
so it can sit under any text formatter, or under another `Filter`.

Subclass `Filter` and override `render(value)`: return the value,
transformed to taste, or `None` to drop this message for the filter\'s
whole subtree.  Or use `Filter` directly, wrapping a callable with the
same contract--it\'s handed the rendered value, and returns the
transformed value or `None`:

```Python
log.route(log.formatter, a, Filter(boring), c)
```

To filter other types, pass `accepts` (what the filter consumes)
and/or `types` (what it produces)--each may be a type, a set of
types, or `True` meaning anything--or simply annotate your callable:
the annotation on its first positional parameter declares what the
filter accepts, and its return annotation declares what it produces.
An explicit parameter wins over an annotation, and `str` is the
default when there\'s neither.  So this filter can sit under an
[`ASCIIFormatter`](#asciiformatter) (which produces `bytes`) and feed
`str` destinations:

```Python
def unbyte(b: bytes) -> str:
    return b.decode('ascii')
```

Returning `None` is how one filter silences a branch of the routing
tree without touching the others--so a `Filter` in front of one
destination lets the *same* log feed destinations at different
verbosities.  When you wrap a callable, `name` defaults to that
callable\'s `__name__`.
</dd></dl>

#### `Sink()`

<dl><dd>

A destination that records the log as a list of
[`SinkEvent`](#sinkevent) objects.  Useful for tests, and for
programs that consume their own logs.

Iterating over a `Sink` yields its events, with each event\'s
`duration` computed as the time until the following event.
`Sink.print(print=None)` prints them.  A `Sink` *accumulates*:
after a [`reset()`](#logreset), new events are recorded after the
old ones, and each event's `session` generation counter tells you
which session it belongs to.  `Sink.clear()` gives you a clean
slate.
</dd></dl>

#### `SinkEvent`

<dl><dd>

Base class of the event objects produced by
[`SinkFormatter`](#sinkformatter) and [`Sink`](#sink).

Common attributes: `session` (the log generation--1 for a log\'s
first session; [`reset()`](#logreset) increments it), `ns` and
`epoch` (the event\'s time), `duration` (nanoseconds until the next
event; excluded from equality), and `type` (a str).

Subclasses: `SinkStartEvent` and `SinkEndEvent` (the log started /
ended), and `SinkLogEvent` with its subclasses `SinkWriteEvent`,
`SinkEnterEvent`, and `SinkExitEvent`--these add `elapsed`, `depth`,
`format`, `message`, and `thread`.  (There's no rendered-text
attribute: sink events carry structured data, not formatting.)

Events are ordered by `ns`.
</dd></dl>

#### `prefix_format(time_seconds_width, time_fractional_width, thread_name_width=12, *, ascii=False)`

<dl><dd>

Builds a prefix template string in the form
`"{elapsed} {thread.name}│ "` with the given field widths.  The
default `TextFormatter` prefix is `prefix_format(3, 10, 12)`, which
renders like:

    003.0706368860   MainThread|
</dd></dl>

#### `expand_tabs(s, *, column=1, first_column=1, tab_width=8)`

<dl><dd>

Expands the tabs in `s` to spaces and returns the result.
If `s` contains no tabs, returns `s` unchanged.

`s` may be `str` or `bytes`, and may contain multiple lines.

`column` is the column of the first character of `s`.
`first_column` is the column the count resets to after a
linebreak--the column your lines start at.  (These follow
`big.string`, which uses `column_number` and
`first_column_number` the same way.)  `column` may not be less
than `first_column`, and `first_column` may not be negative.

Tab stops sit every `tab_width` columns, counted from
`first_column`: with the default `first_column` of 1 and the
default `tab_width` of 8, a tab advances to column 9, 17, 25...
This too matches `big.string`'s arithmetic.  A tab's width
depends on the column where it lands, so if `s` is going to be
placed anywhere other than the left edge of the page, expanding
its tabs correctly requires knowing where it starts.

Lines are separated as `str.splitlines` splits them (for bytes,
`bytes.splitlines`); the linebreak characters are preserved in
the result.
</dd></dl>

#### `format_definition_list(pairs, margin=79, *, definition_left_column=None, definition_relative_tabs=True, indent='  ', spacer='  ', tab_width=8, term_relative_tabs=True)`

<dl><dd>

Formats a "definition list" and returns it as a string:
terms on the left, definitions on the right, definitions
wrapped to fit and aligned in a column.

```
  -v, --verbose  Print more output.  Repeat
                 for even more.
  --color <red|green|blue>
                 Sets the output color.
```

`pairs` is an iterable of `(term, definition)` pairs of strings.
Terms are used verbatim--never wrapped--and may not contain
linebreak characters.  Definitions are text: each one is split
with
[`split_text_with_code`](#split_text_with_codes--code_indent4-tab_width8)
and wrapped with
[`wrap_words`](#wrap_wordswords-margin79--code_indentnone-indent-left_column1-tab_width8-two_spacestrue-rawnone),
so paragraph breaks and code lines work as they do there.
A pair with an empty definition is just the term on a line
by itself.

`margin` is the target width, as in `wrap_words`.

`indent` is a string prefixed to every line.  It counts towards
the margin: if your margin is 70 and your indent is 5 characters,
your "effective margin" is 65.

`spacer` is the fill material between a term and its definition,
in the manner of TeX's leaders: conceptually the spacer repeats,
phase-locked to the start of the term column, from the end of
each term to the definition column--so the repeats line up
vertically from line to line, and a line with no term (a wrapped
continuation line, or a code line) fills the whole span.  The
default spacer is two spaces, which renders as the classic help
table above.  A visible spacer renders leaders, like a table of
contents--`spacer=':'` gives you

```
x:::::::::abcde
y so long:this is the text
::::::::::for y no fooling
```

A multi-character spacer tiles, clipped at the front so the
columns still line up.  The spacer may not be empty: it's the
fill material, and there's no such thing as filling with nothing.

The definition column is computed, one `spacer` past the widest
term that's no wider than a third of the effective margin.  A
term wider than that "hangs": it gets a line to itself, and its
definition starts on the next line, in the definition column.
(This is why there's no overflow strategy here: a wide term
isn't an error, and this is what it does.)  Either way, a term
on the same line as its definition always has at least one full
spacer after it.

`definition_left_column` overrides the computed column: it's the
1-based column (indent included) where the first character of
every definition goes.  Fussy users may know exactly what they
want.  The hang rule still applies, now purely geometric: a term
hangs iff it can't fit on the line with a full spacer after it.
A `definition_left_column` that leaves no room for the spacer,
or no room for definitions inside the margin, raises
`ValueError`.

Tabs are permitted in the terms and the indent; they're expanded
to spaces, using `tab_width`.  Tabs in the indent expand at the
indent's true position (it starts every line, at column 1).
Tabs in a term expand in the term's own coordinates--as if the
term started at column 1--and the expanded term shifts rigidly
into place, so the term's internal alignment survives wherever
the term lands; pass `term_relative_tabs=False` to expand them
at the term's true position on the page instead.
`definition_relative_tabs` works the same way for the
definitions: by default (True) each definition is laid out in
its author's own coordinates--tab stops counted from the
definition column, exactly as the author saw them--and shifts
rigidly into place; pass False to land the definition's tabs on
the tab stops of the page.  Tabs are disallowed in the spacer:
the spacer repeats and shifts around, and a tab's width depends
on where it lands.

`pairs` may contain str or bytes; as with `wrap_words`, all the
strings must agree.  If they're bytes, `indent` and `spacer` must
be bytes too (the defaults adapt).

If `pairs` is empty, returns the empty string.

For more information, see the tutorial on
[**Word wrapping and formatting.**](#word-wrapping-and-formatting)
</dd></dl>

#### `unicode_format_dict(*, closed=False)`

<dl><dd>

Returns a fresh unicode format tree, with box-drawing characters.
This is the default format tree for
[`TextFormatter`](#textformatterformat_dictnone--formatsnone-indent-----namenone-prefixnone-width79).
By default the art is *open* (no right borders, no lids over the
enter/exit label cells), which stays aligned under box-drawing font
substitution.  Pass `closed=True` for fully closed boxes--beautiful
when your font renders box-drawing characters at the true monospace
width, ragged on the right when it doesn't.
</dd></dl>

#### `ascii_format_dict(*, closed=False)`

<dl><dd>

Returns a fresh pure-ASCII format tree.  This is the default format
tree for [`ASCIIFormatter`](#asciiformatter).  Pure ASCII always
aligns, so the open art keeps the enter/exit label lids (the T
junctions render as `+`); `closed=True` gives fully closed boxes that
align on every terminal ever made.
</dd></dl>

#### `format_dict_to_ascii(d)`

<dl><dd>

Returns a copy of a format tree with Unicode box-drawing characters
translated to ASCII.
</dd></dl>

#### `Optional(name)`

<dl><dd>

Marks a format name as optional.  `Optional` is a `str` subclass;
a message logged with `format=Optional('box')` uses the `box` format
if every routed formatter defines it, and silently falls back to the
default format otherwise.  (A plain str format name raises
`ValueError` if it isn't defined.)

Format names may not contain `'.'`--the dot is reserved, so a future
need for nested format namespaces can give names like `'child.start'`
nested semantics without breaking any interface.
</dd></dl>

#### `OldDestination()`

<dl><dd>

*Deprecated.*  A destination providing backwards compatibility with
the pre-0.13 `big.log` interface: accumulates
`[start, elapsed, event, depth]` entries for iteration, and provides
the old `print()` report.  Internally a thin shim consuming
[`SinkEvent`](#sinkevent)s.
</dd></dl>

#### `OldLog(clock=None)`

<dl><dd>

*Deprecated.*  A drop-in replacement for the pre-0.13 `big.log.Log`
class, implemented over the new machinery.  Provided as a
stepping-stone; please migrate to [`Log`](#logdestinations-options).
</dd></dl>


## `big.markdown`

<dl><dd>

A parser for a subset of standards-compliant CommonMark, plus
rendering back ends over a shared intermediate representation.

`big.markdown` separates parsing from rendering:

* **`parse`** turns Markdown text into an *intermediate
  representation* (the node classes below) — a tree of blocks and
  inline runs.
* For a **terminal**, a pipeline lays that tree out and paints it.
  `style_document` bakes [`StyleSheet`](#stylesheetformats--delimiters-escape)
  role markup into the text, `split_styles_document` splits it to word
  granularity, and `layout_document` produces a *width-independent*
  "layout".  At render time
  [`wrap_words`](#wrap_wordswords-margin79--code_indentnone-indent-left_column1-tab_width8-two_spacestrue-rawnone)
  fits the layout to a width,
  [`join_styles`](#join_stylestext-span_linebreaksfalse) coalesces the markup, and a
  [`StyleSheet`](#stylesheetformats--delimiters-escape) paints it — to
  ANSI, to plain text, to anything.
* For **Markdown or a man page**, `render_document(document, format)`
  renders the raw IR directly.

The structural glyphs `layout_document` draws — the bullet, the quote
bar, the thematic break, alert emoji and titles — are emitted as *glyph
roles* (`⦃bullet⦄`, `⦃note_emoji⦄`, `⦃note_title⦄`, …), not baked
characters, so `layout_document` hard-codes nothing.  A `StyleSheet`
that defines them resolves them: [`markdown_defaults`](#markdown_defaults)
gives the Unicode glyphs, [`markdown_ascii_glyphs`](#markdown_ascii_glyphs)
the ASCII ones.  Because they're markup, the wrap-time `raw=` must
resolve them to measure visible width — that's what
[`unicode_glyphs`](#unicode_glyphs-ascii_glyphs) is for below.

The full terminal pipeline is:

```Python
    from big.markdown import *
    from big.stylesheet import join_styles, strip_styles, best_palette
    from big.text import wrap_words

    document = parse(markdown_text)
    document = style_document(document)          # bake in ⦃role⦙…⦄ markup
    document = split_styles_document(document)    # per-word spans, for wrapping
    layout   = layout_document(document)          # width-independent layout
    raw      = lambda w: strip_styles(unicode_glyphs(w))   # visible width, past markup + glyphs
    wrapped  = wrap_words(layout, margin=79, raw=raw)
    sheet    = markdown_defaults | best_palette()  # resolves the glyph roles too
    print(sheet.render(join_styles(wrapped)))
```

For plain, unstyled output, resolve the glyphs with
[`unicode_glyphs`](#unicode_glyphs-ascii_glyphs) (or `ascii_glyphs`) and
strip the rest with [`strip_styles`](#strip_stylestext):

```Python
    from big.markdown import *
    from big.stylesheet import join_styles, strip_styles
    from big.text import wrap_words

    layout  = layout_document(split_styles_document(style_document(parse(markdown_text))))
    raw     = lambda w: strip_styles(unicode_glyphs(w))
    wrapped = wrap_words(layout, margin=79, raw=raw)
    print(strip_styles(unicode_glyphs(join_styles(wrapped))))   # ascii_glyphs for ASCII
```

**The subset.** Every CommonMark block and inline construct is
implemented *except* three, deliberately omitted: images
(`![alt](url)`), raw HTML (block and inline), and entity/numeric
character references (`&amp;`).  Within what it implements the parser
follows CommonMark closely — it passes about 85% of the applicable
CommonMark spec tests, with the remaining gaps concentrated in a few
link/URL edge cases — and it is *fail-soft*: it never raises on
malformed input, it degrades.  Three non-CommonMark extensions are
supported:
GitHub-Flavored strikethrough (`~~text~~`), definition lists
(a `term` line followed by `: definition` lines), and GitHub
**alerts** (a block quote whose first line is `[!NOTE]`, `[!TIP]`,
`[!IMPORTANT]`, `[!WARNING]`, or `[!CAUTION]` — strictly uppercase).

**The IR.** Every node is a small `__slots__` class with structural
equality and a readable `repr`.  Block nodes: `Document` — abstract:
a `MarkdownDocument` (what `parse` returns; its text is literal) or a
`StyledDocument` (what `style_document` returns; its text carries
style markup), and each stage function demands its kind, so styling
twice or exporting a styled tree fails loudly instead of producing
plausible garbage — then `Heading`, `Paragraph`, `BulletList`,
`OrderedList`, `ListItem`, `DefinitionList`, `DefinitionEntry`,
`Term`, `Definition`, `CodeBlock`, `BlockQuote`, `Alert`,
`ThematicBreak`, and `Raw` (an escape hatch: anything outside the
subset — a table, raw HTML — is preserved here to be degraded rather
than dropped).  Inline nodes: `Text`, `StyledText`, `Strong`, `Emph`,
`Strikethrough`, `Code`, `Link`, and `HardBreak`.  A `StyledText`
holds text that is *already* well-formed `⦃role⦙…⦄` markup: where
`style_document` escapes a `Text` (a literal `⦃` in a docstring is
quoted), it passes a `StyledText` through verbatim, so a caller can
carry a role structurally — e.g. a definition-list term of
`StyledText('⦃argument⦙<HOST>⦄')` styles to `⦃term⦙⦃argument⦙<HOST>⦄⦄`
instead of the renderer re-deriving it.  `style_document` validates the
markup (refusing an unbalanced string at the source) and collapses it
into a `Text`.  The `render_document` back ends can't honor the roles,
so — like `Raw` — they degrade a `StyledText` to its stripped text.

</dd></dl>

#### `parse(text)`

<dl><dd>

Parses a Markdown string and returns a `MarkdownDocument` (the root
IR node).
Never raises; malformed constructs degrade to text.

```Python
    >>> parse("# Hi\n\nsome **bold** text\n")
    MarkdownDocument(blocks=[Heading(level=1, children=[Text(text='Hi')]),
      Paragraph(children=[Text(text='some '), Strong(children=[Text(text='bold')]),
      Text(text=' text')])])
```

</dd></dl>

#### `style_document(document)`

<dl><dd>

Takes a `MarkdownDocument` and returns a `StyledDocument`: a copy with
styling markup baked into its text.  (A `StyledDocument` is refused —
styling twice would double-escape the markup.)
Each inline run is wrapped in its *role* — `Strong`&nbsp;→&nbsp;`bold`,
`Emph`&nbsp;→&nbsp;`italic`, `Strikethrough`&nbsp;→&nbsp;`strikethrough`,
`Code`&nbsp;→&nbsp;`code`, `Link`&nbsp;→&nbsp;`link` — and each heading
in `heading1`…`heading6` by level; code blocks use `codeblock`,
definition terms `term`.  A link carries its URL as a leading field
(`⦃link⦙URL⦙label⦄`): the default sheet shows only the label, and a
sheet that wants the URL — to print it, or emit a terminal
hyperlink — defines `link` to use it.  The markup uses
[`big.stylesheet.style`](#stylename-fields) syntax (`⦃role⦙text⦄`).

The result is still a `Document`; feed it to `split_styles_document`
and `layout_document`.  The structural glyphs `layout_document` draws
(list markers, quote and alert bars, the thematic break) always wear
their roles, so a document made entirely of plain prose still gets
styled glyphs — painting them plain is [`plain_stylesheet`](#plain_stylesheet)'s
job.

Literal delimiter characters in the source (`⦃ ⦙ ⦄`) are quoted
automatically, so a docstring that happens to contain them is safe.

</dd></dl>

#### `split_styles_document(document)`

<dl><dd>

Returns a copy of a styled document with every markup span split to
word granularity (built on
[`big.stylesheet.split_styles`](#split_stylestext)).  A run like
`⦃bold⦙a b c⦄` becomes `⦃bold⦙a⦄ ⦃bold⦙b⦄ ⦃bold⦙c⦄`, so wrapping can
break a line mid-run without tearing a span.  Run it after
`style_document` and before `layout_document`; code blocks are left
verbatim.

</dd></dl>

#### `layout_document(document)`

<dl><dd>

Lays a styled, split `Document` out as a *layout* — a flat tuple of
words and
[`wrap_words`](#wrap_wordswords-margin79--code_indentnone-indent-left_column1-tab_width8-two_spacestrue-rawnone)
instructions — drawing the block geometry as hanging-indent prefixes
(list markers, quote and alert bars, the code indent).  It hard-codes
nothing else: glyphs, alert titles, and the thematic break are all
roles.  It is *width-independent*: build it once, then fit it to any
terminal width later.  (Headings get no rule underline — that depends
on the line width; a width-aware renderer can add one from the
`heading{n}_rule` role.)

Feed it a `StyledDocument` that's been through
`split_styles_document`; a `MarkdownDocument` is refused.  To render, pass the layout to `wrap_words`
(with `raw=`&nbsp;[`strip_styles`](#strip_stylestext) so styled words
measure by their visible width), coalesce with
[`join_styles`](#join_stylestext-span_linebreaksfalse), and paint with a
[`StyleSheet`](#stylesheetformats--delimiters-escape) (or strip with
[`plain_stylesheet`](#plain_stylesheet)):

```Python
    layout  = layout_document(document)
    raw     = lambda w: strip_styles(unicode_glyphs(w))
    wrapped = wrap_words(layout, margin=79, raw=raw)
    painted = (markdown_defaults | best_palette()).render(join_styles(wrapped))
```

The glyphs it draws (bullet, quote bar, rules, alert emoji) are *glyph
roles* — `⦃bullet⦄`, `⦃note_emoji⦄`, … — resolved by the painting
`StyleSheet` (`markdown_defaults` defines them), so the wrap-time `raw=`
resolves them with [`unicode_glyphs`](#unicode_glyphs-ascii_glyphs) to
measure visible width.

Because a layout is a flat tuple of constants, it can be baked into a
generated script and wrapped at run time — no parser, no `big.markdown`
needed at run time, just `wrap_words` and a `StyleSheet`.

</dd></dl>

#### `render_document(document, format)`

<dl><dd>

Renders a `Document` to text in one of three formats (there is no
default):

* **`'gfm'`** — GitHub-Flavored Markdown.
* **`'commonmark'`** — CommonMark, with big's extensions degraded to
  plain CommonMark: strikethrough dropped to text, an alert to a
  bold-titled block quote, a definition list to a bold term over a
  block-quoted definition.
* **`'troff'`** — groff `man`-macro troff, the **body** of a man page.
  Headings become `.SH`/`.SS` sections, definition lists `.TP` tagged
  paragraphs (ideal for options), bullet/ordered lists `.IP`, code
  blocks `.EX`/`.EE`, block quotes `.RS`/`.RE`, and strong / emphasis /
  inline code the `\fB` / `\fI` font escapes; hyphens are escaped to
  `\-`.  The caller prepends the `.TH name section date …` header.

Call it on a `MarkdownDocument` — the raw `parse()` IR — never on
`style_document` output: it reads the structured inline nodes, not
role markup, and a `StyledDocument` is refused rather than leaking
markup into the export.

```Python
    print(".TH FOOZLE 1")
    print(render_document(parse(docstring), 'troff'))
```

An unknown `format` raises `ValueError`.

</dd></dl>

#### `markdown_defaults`

<dl><dd>

A [`StyleSheet`](#stylesheetformats--delimiters-escape) defining a
default for every high-level role `big.markdown` emits.  Compose it
*under* a theme and a low-level color map:

```Python
    sheet = markdown_defaults | my_theme | ansi_256_color_palette
```

Every role is defined explicitly (there is no `_default`, so an
*undefined* role raises rather than passing silently).  The
[`transforms`](#transforms) ride along too: `layout_document` puts a
`fill` under each list item — spaces as wide as its marker, sized when
painted — so a sheet built on these defaults can give the bullet any
width and the item text still lines up.  All are
do-nothing except `codeblock`, which inherits `code`; `link`, which
takes the URL as a leading field and shows only the label
(`('URL', 'T', 'T')`); and the ten alert roles, which default to
GitHub-ish colors: `note` blue, `tip`
green, `important` purple, `warning` orange, `caution` red — each
`heading_<kind>` being that color over `heading2`.

It also defines the **glyph roles** `layout_document` draws — `bullet`,
`quote_bar`, `thematic_break` (a fixed five-character rule), the
`note_emoji` … `caution_emoji` icons, and the `note_title` …
`caution_title` alert words (`Note`, `Tip`, …) — each rendering to its
Unicode glyph or English word.  Override any of them — e.g. a
`tip_title` of `Tipp` — for another language.  (`heading1_rule` /
`heading2_rule` are the rule *characters*, for a width-aware renderer to
fill; `layout_document` draws no heading rule itself.)

</dd></dl>

#### `markdown_ascii_glyphs`

<dl><dd>

A [`StyleSheet`](#stylesheetformats--delimiters-escape) defining the
same glyph roles as [`markdown_defaults`](#markdown_defaults), but with
**ASCII** glyphs — `*`, `| `, `-`, `(i)`, `(*)`, `(!)`, `/!\`, `(x)` —
for a terminal (or a pipe) that can't show the Unicode ones.  It defines
only the glyph roles; compose it over a palette for the rest, or use it
via [`ascii_glyphs`](#unicode_glyphs-ascii_glyphs).

</dd></dl>

#### `unicode_glyphs`, `ascii_glyphs`

<dl><dd>

Functions that swap `big.markdown`'s glyph markup for characters —
`unicode_glyphs('⦃bullet⦄ x')`&nbsp;→&nbsp;`'• x'`, `ascii_glyphs`
giving `'* x'` — and leave all other markup alone.  Use them when you
*aren't* rendering against a sheet that defines the glyph roles: as the
`raw=` callback so glyphs measure by visible width (with `strip_styles`
on top), and to produce plain text.  They're just
[`glyphs_from_stylesheet`](#glyphs_from_stylesheetstylesheet) applied to
`markdown_defaults` and `markdown_ascii_glyphs`.

</dd></dl>

#### `glyphs_from_stylesheet(stylesheet)`

<dl><dd>

Returns a glyph-swap function built from `stylesheet` — it renders each
glyph role through the sheet once and caches a `.replace` map.  Use it
to measure glyph widths (as `wrap_words`' `raw=`) against the very sheet
you'll render with, or to bake a custom glyph set.  The sheet must
define the glyph roles ([`markdown_defaults`](#markdown_defaults) does).

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

Aborts at least one current call to `sleep` on this
`Regulator`.

A wake must never be lost.  The `Scheduler` calls `wake`
while holding the lock, but calls `sleep` *after*
releasing it--so a wake may arrive after a thread has
committed to sleeping but before it actually sleeps.
`wake` must be a level, not a pulse: if no thread is
currently sleeping, the next call to `sleep` must
return immediately.

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

Sleeping and waking are built on the classic
"double acquire" trick: the blocker is a lock that's
held ("armed") by default.  `sleep` blocks trying to
acquire it a second time, with the sleep interval as
the timeout; `wake` releases it.  This makes `wake`
a level, not a pulse: a wake with no sleeper parks
the blocker open, so the next `sleep` returns
immediately--and its acquire re-arms the blocker in
the same atomic operation.  A wake can never be lost.
</dd></dl>


## `big.snip`

<dl><dd>

Snippets: marked regions of text files that other files borrow.
A "snippet" is a run of lines bracketed by two scissors marker
lines:

```
# --8<-- start NAME --8<--
...the body of the snippet...
# --8<-- end NAME --8<--
```

Keep one authoritative copy of the code in the world, and sync
the borrowers: `extract_snippets` pulls snippets out of the
authoritative file, and `apply_snippets` applies them to a
borrowing file, like a patch.

Snippets can't nest.  Snippet names can't be empty and can't
contain `--8<--`.  A marker line may be indented and may have
trailing whitespace, but the space after its second `--8<--` is
reserved for future use: for now, anything there is an error.

A snippet's body may declare that it depends on one or
more other snippets, with a "requires" directive line:

```
# --8<-- requires NAME --8<--
```

The directive is ordinary body text--it travels with the
snippet, so borrowed copies keep their dependency information.
Requirements resolve transitively, local file only--there is no
cross-file mechanism--and can't form a cycle.  Reference cycles are an error.

Running the module as a program--`python -m big.snip`--gives you
the command-line version: `list` prints a file's snippet names,
`extract` prints `extract_snippets` output, `apply` applies
snippets to a destination file (only writing it if something
changed), `check` reports what `apply` would do and exits
nonzero, for test suites, and `sync` treats the destination as
its own manifest--every snippet it already carries is updated
from the source, optionally filtered by name prefixes.  When a
file is malformed, the error says where: the tool reparses with
[`big.string`](#strings--sourcenone-line_number1-column_number1-first_column_number1-tab_width8),
so you get the file, line, and column.  `-c COMMENT` sets the comment leader
(default `#`), so e.g. `-c //` works with C-family files; it
may appear anywhere on the command line.  Files are read and
written as UTF-8 text.

#### `apply_snippets(s, snippets, comment='#')`

<dl><dd>

Applies snippets to `s`, like a patch: returns a copy of `s`
with every snippet in `snippets` applied.  `snippets` is a
string of marker-bracketed snippets, one after another--the
value returned by
[`extract_snippets`](#extract_snippetss-names-comment).

A snippet `s` already carries is overwritten in place, wherever
`s` keeps it; everything around it, and the order of the
snippets in `s`, is preserved.  A snippet `s` lacks is inserted:
immediately before the snippet that follows it in `snippets`,
or, if it's the last one, appended at the end of `s`.  (A
deliberately simple placement rule.  Rearrange the snippets in
`s` however you like; `apply_snippets` honors your ordering
forever after.)

End-of-line discipline is preserved: a snippet appended at the
end of `s` ends with a linebreak only if it ended with one in
`snippets`.

`s`, `snippets`, and `comment` must all be the same type, `str`
or `bytes`, and the return value is the same type as `s`.
`comment` is the comment leader the marker lines start with; it
defaults to `'#'`.

Raises `ValueError` if `snippets` contains anything besides
snippets, or if either argument's snippet structure is
malformed: nested snippets, an unterminated snippet, mismatched
or out-of-order markers, or two snippets with the same name.

</dd></dl>

#### `extract_snippets(s, *names, comment='#')`

<dl><dd>

Extracts the named snippets from `s` and returns them--
together with every snippet they require, transitively, in
source order, marker lines and all, with no blank lines between
them.  Pass the snippet names as positional arguments--
`extract_snippets(source, 'B', 'D')`--and the result is the
union of every name's closure, in source order, ready to feed to
[`apply_snippets`](#apply_snippetss-snippets-comment)--which
preserves that order.

Each snippet keeps its own end-of-line discipline: a snippet
that ended `s` without a trailing linebreak extracts without
one.

`s`, the names, and `comment` must all be the same type, `str`
or `bytes`, and the return value is the same type as `s`.
`comment` is the comment leader the marker lines start with; it
defaults to `'#'`--pass `comment='//'` for the C family, and so
on.  (As a convenience, when `s` is `bytes` and `comment` is
defaulted, it quietly becomes `b'#'`.)

Raises `ValueError` if the snippet (or any snippet it requires)
isn't in `s`, if the requirements form a cycle, or if `s`'s
snippet structure is malformed (the same errors as
`apply_snippets`).

</dd></dl>

#### `sync_snippets(source, destination, filter=None, *, comment='#')`

<dl><dd>

Updates `destination`'s borrowed snippets from `source`, and
returns the updated destination.  The destination is its own
manifest: `sync_snippets` reads the names of the snippets
`destination` already carries, extracts those snippets from
`source`--together with every snippet they require--and applies
them back.  (A required snippet the destination doesn't carry
yet gets installed by the apply.)

`filter`, if not `None`, is a callable: it's called with each of
destination's snippet names, and only names it approves are
synced.  Use it to whitelist by project prefix when the
destination folds together snippets borrowed from several
sources:

```Python
sync_snippets(big_text, warehouse,
              (lambda name: name.startswith('big ')))
```

`source`, `destination`, and `comment` must all be the same
type, `str` or `bytes`, and the return value is the same type.

Raises `ValueError` if the destination carries no snippets to
sync (after filtering), plus everything
[`extract_snippets`](#extract_snippetss-names-comment) and
[`apply_snippets`](#apply_snippetss-snippets-comment) raise.

</dd></dl>

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
Use of this base class is optional; states can be any
value except `None`.

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
  until the *next* state transition.  (Upon every state
  transition, `StateManager` locally caches the list of
  observers before calling any of them.)
* If an observer raises an exception,
  `StateManager` remembers the first exception,
  continues calling the remaining observers,
  completes the state transition,
  and then re-raises that first exception.
  (If more than one observer raises an exception, only
  the first exception is retained and re-raised.
  If `on_enter` *also* raises an exception, the observer's
  exception still wins--it was first--and the `on_enter`
  exception is chained to it, as its `__cause__`.)

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
defined with this name,
[`StateManager`](#statemanagerstate--on_enteron_enter-on_exiton_exit-state_classnone)
will call that attribute (with no
arguments) immediately after transitioning to that state.
Passing in a false value for `on_enter` to the `StateManager`
constructor disables this behavior.

`on_enter` is called immediately after the transition is complete,
which means you're expressly permitted to make a state transition
inside an `on_enter` call.

If defined, `on_enter` will be called on
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

If the `on_exit` method raises an exception, the state transition
is aborted, and the state machine stays in the current state.

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
  the transition to the next state.  This means it's
  illegal to initiate a state transition inside an `on_exit`
  call.  If the `on_exit` method raises an exception,
  the state transition is aborted, and the `StateManager`
  stays in the current state.
* If you assign an object to `state` that has an `on_enter`
  attribute, that method will be called (with zero
  arguments) immediately *after* we have transitioned to that
  state.  This means it's permitted to initiate a state
  transition inside an `on_enter` call.
* If the current state object's `on_exit` raises an exception,
  the transition is aborted, `state` remains unchanged,
  and `next` is restored to `None`.
* If an observer raises an exception, the transition still
  completes, `next` is restored to `None`, and `StateManager`
  re-raises the first observer exception after completing
  the transition.
* It's illegal to attempt to transition to the current
  state.  If `state_manager.state` is already `foo`,
  `state_manager.state = foo` will raise an exception.
  (However, it's legal to transition to an object `bar`
  even if `foo == bar` is true.  Equivalent objects are
  fine; you just can't transition to literally the *same*
  object.)

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
* For every object `o` in a snapshot of the
  `state_manager.observers` list,
  call `o(self)`.
    * If an observer raises an exception,
      `StateManager` remembers the first exception,
      then keeps calling the remaining observers.
* Set `state_manager.state` to `new_state`.
    * As of this moment, the transition is complete, and
      `state_manager` is now "in" the new state.
* Set `state_manager.next` to `None`.
* If `state_manager.state` has an `on_enter` attribute,
  call `state_manager.state.on_enter()`.
* If an observer or `on_enter` raised an exception,
  re-raise the *first* exception raised now.
  (If both an observer and `on_enter` raised, the
  observer's exception came first, so it wins; the
  `on_enter` exception is chained to it as its
  `__cause__`.)
</dd></dl>


#### `TransitionError()`

<dl><dd>
Exception raised when attempting to execute an illegal state transition.

`TransitionError` subclasses `RuntimeError`: both kinds of illegal
transition are legal operations attempted at an illegal moment,
which is `RuntimeError`'s beat.

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


## `big.stylesheet`

<dl><dd>

A tiny markup language for decorating text *within* a line — bold,
color, links — and a two-layer, recursive *style sheet* that renders
that markup to any backend.  It's the machinery `big.markdown` paints
with, but it stands on its own.

Markup is authored with [`style`](#stylename-fields) and
[`plain`](#plaintext), never typed by hand: the three delimiters
(`style_delimiters`, the string `'⦃⦙⦄'`) are deliberately exotic so
they're visible if they ever leak.  A span is written `⦃name⦙text⦄`.

A [`StyleSheet`](#stylesheetformats--delimiters-escape) maps each
*name* to a definition and renders the markup.  Because a definition's
replacement may itself contain markup, style sheets *compose*: a
high-level sheet mapping `heading`&nbsp;→&nbsp;`⦃bold⦙⦃red⦙…⦄⦄` merges
with a low-level sheet mapping `red`&nbsp;→&nbsp;an ANSI escape, and
`.render()` resolves the whole chain.  `StyleSheet` is a `dict`
subclass, so you compose with `|` and tweak with ordinary item
assignment.

**Decorate early, paint late.**  Text that will be wrapped gets pulled
apart into words by [`split_styles`](#split_stylestext) and put back
together by [`join_styles`](#join_stylestext-span_linebreaksfalse),
and those two are blind to what a role *means* — they run at bake
time, before any sheet exists.  So a role that rides through them must
be **paint**: something that looks the same brushed onto a phrase or
onto each of its words (bold, a color, an HTML tag).  Anything that
changes the *visible characters* — brackets around a metavar,
uppercase, a fill rule — is a **decoration**, and belongs *before*
wrapping, resolved into ordinary text (`<HOST>` is characters by the
time it wraps; the `argument` role that colors it is paint).  The one
sanctioned exception is a *block-level* role like a heading, applied
once per block: join reassembles a wrapped block into a single span,
and a blank line always ends one, so the block's decoration fires
exactly once.  A once-per-phrase decoration *inside* wrapped prose
(`('T', '[T]')`) is outside this contract — the stylesheet cannot tell
it from a tag, and will paint it per word.

</dd></dl>

#### `style(name, *fields)`

<dl><dd>

Returns the markup for one span: `'⦃name⦙field…⦄'`.  `name` must be
alphanumeric or underscore and must not start with a digit.  Fields
may themselves *contain* well-formed markup — `style('bold',
style('link', text))` composes — but a stray delimiter in a field
raises `ValueError` (quote it first with
[`escape_styles`](#escape_stylestext)).

```Python
    >>> style('bold', 'hello')
    '⦃bold⦙hello⦄'
```

</dd></dl>

#### `plain(text)`

<dl><dd>

Returns the markup for a "boring island": `text` renders with no
paint — any enclosing paint is suspended and nested paint stripped.

</dd></dl>

#### `escape_styles(text)`

<dl><dd>

Quotes any style-delimiter characters in `text` so it can be dropped
into markup as literal text.  Each delimiter is preceded by the open
delimiter (`⦃`&nbsp;→&nbsp;`⦃⦃`, `⦙`&nbsp;→&nbsp;`⦃⦙`,
`⦄`&nbsp;→&nbsp;`⦃⦄`); rendering turns them back into the literal
character.  Call it on raw text before wrapping it in a span.

</dd></dl>

#### `StyleSheet(formats=(), *, delimiters='⦃⦙⦄', escape=None)`

<dl><dd>

Maps format names to definitions; `.render(s)` paints marked-up text
`s`.  A definition is either a tuple of one or more strings —
`(*args, replacement)`, where each `arg` is a placeholder — or a
`callable(*fields)` returning text (the escape hatch).  The *last*
arg is the display text and must appear in `replacement`; any args
before it are luggage (a link's URL, say) that the replacement may
ignore: `('URL', 'T', 'T')` shows the label alone, `('URL', 'T',
'T <URL>')` shows both.

```Python
    sheet = StyleSheet({
        'bold': ('T', '\x1b[1mT\x1b[22m'),          # low level: T -> ANSI
        'heading': ('T', '⦃bold⦙⦃red⦙T⦄⦄'),          # high level: composes
        'red': ('T', '\x1b[31mT\x1b[39m'),
    })
    sheet.render(style('heading', 'Hi'))            # bold + red
```

`'_default'`, if present, catches unknown names (it takes one arg,
the display text); with no `'_default'`, an unknown name raises
`KeyError`.  `escape` is applied to literal source text at render
time (e.g. `html.escape` for an HTML backend).  Merging with `|`
composes vocabularies; the left operand's delimiters win.

</dd></dl>

#### `split_styles(text)`

<dl><dd>

Rewrites markup so every whitespace-delimited word carries its own
balanced span — `'⦃bold⦙a b c⦄'`&nbsp;→&nbsp;`'⦃bold⦙a⦄ ⦃bold⦙b⦄
⦃bold⦙c⦄'` — while preserving all whitespace verbatim (a two-space
gap stays two spaces).  This lets a consumer split the text at
whitespace (to wrap it, lay it in columns, …) and get self-contained
styled words, since a span never straddles a break.  Pure markup in,
markup out.

A *zero-arg* span (`⦃name⦄`, no field) is treated as a single
**character**: it has no text of its own, so it rides along with the
surrounding content rather than being dropped.  (`big.markdown` uses
zero-arg spans for its glyph roles.)

Only a span's *last* field is text; any fields before it are luggage —
a link's URL, a `fill`'s pattern — carried whole on every word:
`⦃link⦙URL⦙read more⦄`&nbsp;→&nbsp;`⦃link⦙URL⦙read⦄ ⦃link⦙URL⦙more⦄`.
So a multi-field span survives splitting, and renders word by word.

</dd></dl>

#### `join_styles(text, span_linebreaks=False)`

<dl><dd>

The inverse of [`split_styles`](#split_stylestext): factors out the
span stack that adjacent runs share, wrapping each shared span once and
nesting the differences inside it, and absorbs the whitespace between
them into the shared span.  Adjacent runs with the same full stack
merge outright — `⦃bold⦙This⦄ ⦃bold⦙is⦄`&nbsp;→&nbsp;`⦃bold⦙This is⦄` —
and runs that share only an outer prefix keep one toggle of that prefix
around the rest: `⦃a⦙with⦄ ⦃a⦙⦃code⦙x⦄⦄ ⦃a⦙z⦄`&nbsp;→&nbsp;`⦃a⦙with
⦃code⦙x⦄ z⦄`.  Used to minimize a backend's output (fewer style toggles)
after layout.  By default it never merges across a newline, so each
line's markup stays balanced and self-contained.  Pass
`span_linebreaks=True` to absorb a single newline too — a span may then
straddle a line break, so a wrapped heading is still one heading (fewer
toggles still, at the cost of per-line balance).  A *blank* line is
always a boundary: two blocks are never fused into one span.
Like `split_styles`, it treats a zero-arg span as a character, so glyph
markup survives it.  A span's leading fields are luggage (see
`split_styles`), and adjacent words merge only when their luggage
matches — two links to different URLs stay two links.

</dd></dl>

#### `strip_styles(text)`

<dl><dd>

Strips *all* style markup from `text`, leaving the visible characters —
`⦃bold⦙hi⦄`&nbsp;→&nbsp;`hi`.  The text transforms still apply, since
their output *is* visible characters: `⦃fill⦙ ⦙abcd⦄`&nbsp;→&nbsp;four
spaces, `⦃upper⦙x⦄`&nbsp;→&nbsp;`X`.  It's [`plain_stylesheet`](#plain_stylesheet)`.render`
under a shorter name, and it's *fail-soft*: text carrying an unquoted
literal delimiter (not real markup) comes back unchanged rather than
raising.  This is the callback to hand `wrap_words`/`merge_columns` as
`raw=`, so styled words wrap by their visible width.

</dd></dl>

#### `plain_stylesheet`

<dl><dd>

A `StyleSheet` that strips *all* paint to bare text — every span
renders as its content, any role — while the [`transforms`](#transforms)
still shape it (a `fill` still fills, an `upper` still uppercases).
Handy as a "render to plain text" backend.

</dd></dl>

#### `transforms`

<dl><dd>

A `dict` of stock text transforms, suitable for merging into a
`StyleSheet` and used as tags.  Pure text shaping, no paint:

* `⦃upper⦙text⦄`, `⦃lower⦙text⦄`, `⦃title⦙text⦄` — case (`title` uses
  big's [`gently_title`](#gently_titles-apostrophesnone-double_quotesnone)).
* `⦃strip⦙text⦄`, `⦃lstrip⦙text⦄`, `⦃rstrip⦙text⦄` — trim whitespace.
* `⦃fill⦙pattern⦙model⦄` — repeat `pattern` up to the length of `model`,
  then clip: `⦃fill⦙-=-⦙abcdefgh⦄`&nbsp;→&nbsp;`-=--=--=`.
* `⦃clip⦙model⦙text⦄` — cut `text` to the length of `model`.
* `⦃center⦙model[⦙fill]⦙text⦄`, `⦃ljust⦙model[⦙fill]⦙text⦄`,
  `⦃rjust⦙model[⦙fill]⦙text⦄` — pad `text` to the width of `model`,
  centered / left- / right-justified: `⦃center⦙abcdefg⦙xyz⦄`&nbsp;→&nbsp;`  xyz  `,
  `⦃rjust⦙abcdefg⦙xyz⦄`&nbsp;→&nbsp;`    xyz`.  The padding is a space by
  default, or an optional `fill` *string* — tiled and clipped like
  `fill` — that rides in the *middle*: `⦃rjust⦙abcdefg⦙-=-⦙xyz⦄`&nbsp;→&nbsp;`-=--=xyz`.
  Keeping `fill` in the middle means `text` is always the last field, so
  it can carry nested markup.

These compose — e.g. a heading rule sized to the text but capped at the
line width is `⦃clip⦙⦃line⦄⦙⦃fill⦙⦃heading1_rule⦄⦙⦃strip⦙T⦄⦄⦄` (where
`line` is a role you set to a full-width run for the current width).

A transform's fields are *visible text*.  Spans nested inside a field
still resolve — glyphs, rewrites, other transforms — but paint is
dropped, so `⦃upper⦙…⦄` never uppercases an escape sequence and
`fill` never counts one.  A transform's own output is then painted by
whatever encloses it, like any other run.

</dd></dl>

#### `ansi_truecolor_palette`, `ansi_256_color_palette`, `ansi_16_color_palette`, `uncolored_palette`, `plain_palette`

<dl><dd>

Five stock *low-level* style sheets that resolve the styling
vocabulary to terminal escape sequences.  Merge one *under* a
high-level theme so the theme's roles reach real escapes:

```Python
    sheet = my_theme | ansi_256_color_palette
```

Each defines the four attributes — `bold`, `italic`, `underline`,
`strikethrough` — and the 29-color vocabulary: `red`, `orange`,
`amber`, `yellow`, `green`, `cyan`, `blue`, `purple`, and `gray`, each
in `light`/`dark`/normal (`light_red`, `dark_red`, `red`), plus
`white` and `black`.  The color depth differs: `ansi_truecolor_palette` emits
24-bit `38;2;r;g;b`, `ansi_256_color_palette` the nearest xterm-256
index, `ansi_16_color_palette` an explicit mapping onto the 16 basic
colors, `uncolored_palette` renders the attributes but drops color
entirely, and `plain_palette` renders *everything* plain — no escapes
at all.  `plain_palette` differs from
[`plain_stylesheet`](#plain_stylesheet) only in that it enumerates all
33 roles explicitly rather than using `_default`, so it composes with a
theme (like [`markdown_defaults`](#markdown_defaults)) that forbids
`_default` and expects every role defined.

These maps are hard-coded (generated by
`resources/stylesheet/palettes.py` from the master 29-color palette),
so nothing about them is computed at import.

</dd></dl>

#### `best_palette(*, file=None)`

<dl><dd>

Returns the map best suited to `file` (default `sys.stdout`):
[`plain_stylesheet`](#plain_stylesheet) — fully plain text, no escapes
at all — when [`big.can_colorize(file=file)`](#can_colorizefilenone)
says color is unwanted, otherwise the low-level map matching
[`big.ansi_color_depth()`](#ansi_color_depth) — `ansi_truecolor_palette`,
`ansi_256_color_palette`, or `ansi_16_color_palette`.  Merge a theme *over* it:

```Python
    sheet = markdown_defaults | my_theme | best_palette()
```

</dd></dl>


## `big.template`

<dl><dd>

Functions for parsing strings containing a simple template syntax,
patterned after
[Django Templates](https://docs.djangoproject.com/en/stable/ref/templates/language/)
and [Jinja](https://jinja.palletsprojects.com/).
Similar in spirit to Python 3.14+ t-strings.

</dd></dl>

#### `Formatter(template, map=None, *, relaxed=False, stretch=True, width=79, **kwargs)`

<dl><dd>

A sophisticated template formatter, similar to `str.format`.

The `Formatter` constructor takes the following arguments:
    * `template`, a string.  Calling the `Formatter` object
      is like calling the `str.format` method on that string.
    * `map`, a `dict` or `None`, default `None`.  If a `dict`,
      pre-initializes values used at interpolation time.
    * `width`, an integer, default 79, the target width of
      lines when computing "starred interpolations".
    * `stretch`, a boolean, default `True`, also used in
      conjunction with "starred interpolations".

Also, additional `**kwargs` are used as additional pre-initialized
map values, and take precedence over the "map" parameter.

Returns a `Formatter` object.  Calling this object formats
the template string using `str.format_map` and returns
the result.  Substitutions in the template use `str.format_map`
syntax.  The signature of this callable is:

```Python
   fn(message='', **kwargs)
```

The `**kwargs` passed in here are also used as values for the
interpolation, and take precedence over any value passed in to the constructor.

Formatter has two additional features:

    * Special support for an interpolation named `"{message}"`,
      which are formatted in conjunction with the "message" parameter.
      If your template contains one or more lines containing `"{message}"`,
      these "message lines" are formatted using the lines of the `message`
      argument.  The "message" argument is split by the newline character
      (`'\n'`) and these are zipped together with the "message lines";
      the first "message line" will be formatted with the first line
      of the "message" parameter, the second with the second, etc.

        * If there are more "message lines" in the template than lines
          in the "message" parameter, the additional "message lines"
          are discarded.  Example: if there are three "message lines"
          in the template, but only two lines in the "message" parameter,
          the third "message line" won't appear in the output.

        * If there are more lines in the "message" parameter than
          "message lines" in the template, the last template
          "message line" will be repeated.  Example: if there are
          three lines in the "message" parameter, but only two
          "message lines" in the template, the last "message line"
          will be repeated, used to format the last two lines of
          the "message" parameter.

        * If the template doesn't contain any "message lines",
          but you pass in a non-empty string for the "message"
          when you call the `Formatter` object, normally this will
          raise `ValueError`.  If you want to permit passing in
          a message when rendering a `Formatter` without any
          "message lines", pass in `relaxed=True` to the `Formatter`
          constructor.

    * Values whose keys end with `'*'` (e.g. `"{line*}"`) are special:
      they are "starred interpolations".  Their value is repeated
      zero or more times then truncated until the line is at least
      "width" characters.  The value is converted with `str()` and
      must not be empty.  Starred interpolations must not use:

        * dotted expressions (`"{line.foo*}"`)
        * indexing (`"{line[3]*}"`)
        * a conversion (`"{line*!r}"`)
        * or a format spec (`"{line*:5}"`)

    If `stretch` is true, `Formatter` calculates the width of the
    longest formatted line (assuming all starred interpolations
    are length 0), then recomputes width as

```Python
    width = max(longest_line, width)
```

  This means the starred interpolations will "stretch" to fit
  the longest line of the output.

   Example:

```Python
    fmt = Formatter('{line*}\\n{name} start\\n>> {message}\\n<< {message}\\n{double*}{line*}',
      {'line*': '-', 'double*': '=', 'name': 'Log'},
      width=20)
    print(fmt("hello\\nthere\\nworld!"))
```

This prints:

```
    --------------------
    Log start
    >> hello
    << there
    << world!
    ==========----------
```

</dd></dl>

#### `eval_template_string(s, globals, locals=None, *, parse_expressions=True, parse_comments=False, parse_whitespace_eater=False)`

<dl><dd>

Parses and evaluates a template string, returning the rendered result.

`s` is parsed using
[`parse_template_string`](#parse_template_strings--parse_expressionstrue-parse_commentsfalse-parse_statementsfalse-parse_whitespace_eaterfalse-quotes--multiline_quotes-escape),
then each [`Interpolation`](#interpolationexpression-filters-debug-formatnone) is evaluated using
Python's built-in `eval()` with the provided `globals` and
`locals` dicts.  Filters are applied in order.  A format
specification is applied exactly like an f-string's--
`format(value, spec)`, with the spec taken verbatim--so like
an f-string, don't pad it with whitespace: `{{x:>10}}`, not
`{{ x : >10 }}`.  The rendered string is returned with all
interpolations replaced by their values.

`parse_comments` and `parse_whitespace_eater` may be enabled
optionally; they are disabled by default.  Statement parsing
is not supported by `eval_template_string`.
</dd></dl>

#### `Interpolation(expression, *filters, debug='', format=None)`

<dl><dd>

Represents a `{{ }}` expression interpolation from a parsed template.

`expression` contains the text of the expression.  `filters`
is a tuple containing the text of each filter expression, if any.
If the expression ended with `=`, `debug` contains the text
of the expression along with the `=` and all whitespace;
otherwise it is an empty string.

`format` contains the interpolation's *format specification*:
the text after a top-level `:`, kept verbatim, analogous to the
format spec of an f-string.  If the interpolation has no
top-level `:`, `format` is `None`.

See [`parse_template_string`](#parse_template_strings--parse_expressionstrue-parse_commentsfalse-parse_statementsfalse-parse_whitespace_eaterfalse-quotes--multiline_quotes-escape).
</dd></dl>

#### `parse_template_string(s, *, parse_expressions=True, parse_comments=False, parse_statements=False, parse_whitespace_eater=False, quotes=('"', "'"), multiline_quotes=(), escape='\\')`

<dl><dd>

Parses a string containing simple template markup, yielding
its components.

Returns a generator yielding `str` objects (literal text),
[`Interpolation`](#interpolationexpression-filters-debug-formatnone) objects (parsed expressions),
and [`Statement`](#statement) objects (parsed statements).

The supported delimiters are:

`{{ ... }}` — An expression.  Parsed into an
[`Interpolation`](#interpolationexpression-filters-debug-formatnone) object.  Expressions may
include filters separated by `|`, and a *format specification*
after a `:`, analogous to an f-string's:

```
{{ expression | filter | filter : format }}
```

Only *top-level* `|` and `:` characters count--characters nested
inside brackets or quotes belong to the expression or filter
they're inside, so slices, dict displays, and string literals
work as expected.  (A top-level lambda needs parentheses, same
as in an f-string.)  Everything after the first top-level `:` is
the format specification, preserved verbatim--including
whitespace and any further `|` or `:` characters.

`{% ... %}` — A statement.  Parsed into a
[`Statement`](#statement) object.  Quoted strings inside
statements are preserved and respected when looking for the
close delimiter.

`{# ... #}` — A comment.  The delimiters and all text between
them are discarded.

`{>}`, `{<}`, and `{<>}` — The whitespace eaters.  Each discards
its own characters plus adjacent whitespace: `{>}` eats all
whitespace *after* it, `{<}` eats all whitespace *before* it,
and `{<>}` eats in both directions.

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

## `big.test`

<dl><dd>

A tiny, low-ceremony test harness.  You can test the way you
write code, not the way `unittest` insists:

* bare `assert a == b`, never `self.assertWhicheverOne()`,
* `with raises(ValueError):` instead of `self.assertRaises`,
* no mandatory base class, no mandatory methods, no mandatory
  main--plain `def test_foo():` functions are first-class,
* and on a failing assert you get the *same* rich, type-aware
  diff `unittest`'s `assertEqual` gives you.  (big reuses
  unittest's own machinery.)

A test file looks like this:

```Python
import big.test
from big.test import raises
from big.builtin import load

mypackage = load('mypackage')     # local checkout beats installed

def test_frobnicate():
    got = mypackage.frobnicate('a', 'b')
    assert got == 'ab'

def test_bad_input_rejected():
    with raises(ValueError):
        mypackage.frobnicate('a', None)

if __name__ == '__main__':
    big.test.main()
```

and a multi-module test driver looks like this:

```Python
import big.test
from big.builtin import load
load('mypackage')

import test_basics, test_parsing

with big.test.suite() as run:
    run(name='mypackage.basics',  module=test_basics)
    run(name='mypackage.parsing', module=test_parsing)
```

Leaving the `with` block prints the summary and exits nonzero if
anything failed.

One habit makes the rich diffs work: **bind, then assert.**

```Python
got = mypackage.frobnicate('a', 'b')
assert got == expected
```

The explainer reads operand values out of the dead frame; it never
re-evaluates the asserted expression, so no side effects fire.
That also means it can only *show* operands that are names or
literals--a call expression inside the assert can't be safely
shown.  (When it can't produce a diff, it falls back to printing
the values of the names in the assert.)

`big.test` is stdlib-only, and `unittest.TestCase` classes still
work if you want them: [`test.run`](#testrunnamenone-modulenone-permutationsnone)
runs plain test functions and `TestCase` subclasses in one tally.
For convenience it also re-exports `TestCase`, `skip`, `skipIf`,
`skipUnless`, and `expectedFailure` from `unittest`.  (On a plain
test function, a skip decorator raises `unittest.SkipTest` when
the function is called; `test.run` counts it as a skip.)

`big.test` is *never* imported by `big.all`--not even as a
submodule, unlike `big.deprecated`--because importing `unittest`
costs real time, about as much as importing all the rest of big.
Import it explicitly: `import big.test`.

Importing `big.test` installs a `sys.excepthook` so that even a
script with bare module-level asserts--no test functions, no
runner--prints the explanation after an uncaught AssertionError's
traceback.

</dd></dl>

#### `test.explain(tb, write)`

<dl><dd>

Prints an explanation of a failed bare `assert` to `write`
(a callable taking a string).  `tb` is the traceback; the assert
is taken from its deepest frame.  Prints the rich type-aware diff
if the assertion was `a == b` and both operands are safely
readable (names or literals), otherwise prints the values of the
names appearing in the assert.  Prints nothing if it can't help
(and never raises).

This is the machinery underneath everything else; it's exposed
for building your own tools.
</dd></dl>

#### `test.ExplainResult`

<dl><dd>

A `unittest.TextTestResult` subclass that appends
[`test.explain`'s](#testexplaintb-write) explanation to each
failure report.  Importing `big.test` installs it as the default
result class for `unittest.TextTestRunner`, so `TestCase`-based
tests get explained failures too--even under a plain
`unittest.main()`.
</dd></dl>

#### `test.finish()`

<dl><dd>

Prints the final `OK`/`FAILED` summary from
[`test.stats`](#teststats), with the nonzero counts
(`OK (skipped=2)`).  If there were failures or errors, exits with
status 1.  ([`test.suite`](#testsuite) calls this for you.)
</dd></dl>

#### `test.main()`

<dl><dd>

The standalone-file entry point: put `big.test.main()` at the
bottom of a test file, under `if __name__ == '__main__':`.
Runs the file's tests and exits nonzero on failure.

(`main()` deliberately does no command-line processing yet.
When big grows its command-line argument processing module,
`main()` will use it.)
</dd></dl>

#### `test.preload(package)`

<dl><dd>

Deprecated alias for [`load(name)`](#loadname) in `big.builtin`,
where the function lives (and got its new name) as of big 0.15;
calling it emits a `DeprecationWarning`.  To be removed no sooner
than September 2027.
</dd></dl>

#### `test.raises` and `test.raises_regex`

<dl><dd>

The bare-function spellings of `assertRaises` and
`assertRaisesRegex`:

```Python
with raises(ValueError):
    mypackage.frobnicate('a', None)

with raises(TypeError) as cm:
    mypackage.frobnicate(1, 2)
assert 'frobnicate' in str(cm.exception)

with raises_regex(ValueError, 'colou?r'):
    mypackage.paint('plaid')
```

They *are* `unittest`'s own methods, borrowed from an internal
helper instance, so the callable form works too:
`raises(TypeError, fn, arg)`.
</dd></dl>

#### `test.register_type_equality(type, function)`

<dl><dd>

Teaches the explainer how to diff your own type, exactly like
unittest's `TestCase.addTypeEqualityFunc`.  `function(a, b, msg=None)`
should raise an `AssertionError` (with a nice message) when
`a != b`.  After this, a failing `assert a == b` on two of your
objects prints that message.
</dd></dl>

#### `test.run(name=None, module=None, permutations=None)`

<dl><dd>

Runs the tests in `module`.  Discovers:

* plain `def test_*()` functions that take no required arguments
  (a function with required parameters is yours to call by hand,
  so discovery skips it), and
* `unittest.TestCase` subclasses.

`module` may be a module object, a module name (test files pass
`__name__`), or `None` for the `__main__` module.

`name`, if given, is printed in a `Testing {name}...` banner.
`permutations`, if given, is a zero-argument callable returning a
number to report in the `Ran N tests` line (for tests that try
every permutation of something).

Adds the counts to [`test.stats`](#teststats), for
[`test.finish`](#testfinish).
Returns `(tests_run, failures_and_errors)`.
</dd></dl>

#### `test.stats`

<dl><dd>

The running tally, a dict: `failures`, `errors`, `skipped`,
`expected failures`, `unexpected successes`.
[`test.run`](#testrunnamenone-modulenone-permutationsnone) adds to
it; [`test.finish`](#testfinish) summarizes it.
</dd></dl>

#### `test.suite()`

<dl><dd>

A context manager for a multi-module test driver.  Entering
returns the [`test.run`](#testrunnamenone-modulenone-permutationsnone)
callable; leaving the block calls [`test.finish`](#testfinish):

```Python
with big.test.suite() as run:
    run(name='mypackage.basics',  module=test_basics)
    run(name='mypackage.parsing', module=test_parsing)
```

If the block raises, the exception propagates and `finish()`
isn't called.
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
with `keep=True`, flattening the 2-tuples it yields.)

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

#### `Delimiter(close, *, escape='', multiline=True, quoting=False, nested=None, literal=(), change=None)`

<dl><dd>

Class representing a delimiter for
[`split_delimiters`](#split_delimiterss-delimiters--state-yields4).

`close` is the closing delimiter: either a string or bytes object,
or a tuple of them--alternatives, any one of which closes the
delimiter.  (For example, `python_delimiters` defines its line
comment as `Delimiter(('\n', '\r'), quoting=True, multiline=False)`:
a comment ends at whichever linebreak comes first.)  No close
delimiter may be empty or a backslash (`"\\"` or `b"\\"`).
The `closes` property always presents the close delimiters as a
tuple, even if `close` was passed as a single string--and a single
string and a 1-tuple compare equal.

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

Three more parameters define what the text *inside* the
delimiter means.  Together they're expressive enough to define
grammars as intricate as [`python_delimiters`](#python_delimiters)
as plain data--f-strings included:

<dl><dt>

`nested`

</dt><dd>

A mapping of open delimiter strings to `Delimiter` objects:
delimiters that are live *inside* this delimiter.  For a quoting
delimiter, `nested` delimiters are the exceptions to the
quoting--it's how a Python f-string, which quotes, still opens a
`{`interpolation`}`.  For a non-quoting delimiter, every
top-level delimiter of the grammar is already live inside, and
`nested` adds to (or overrides) those.  (A `None` value is
reserved for future use, and currently rejected.)

</dd><dt>

`literal`

</dt><dd>

A token--or, like `close`, a tuple of them--that is plain text
inside this delimiter, even where it'd otherwise collide with a
meaningful token: how `'{{'` inside an f-string means a literal
`'{'` rather than two interpolations.  The `literal` property
always presents the tokens as a tuple.

</dd><dt>

`change`

</dt><dd>

A mapping of tokens to `Delimiter` objects: seeing the token
*changes* what the inside of the current delimiter means, without
opening a nested delimiter.  The current delimiter continues, and
its close still closes it--so a change target must have the same
`close` as its host.  This is how the `':'` inside an f-string
`{`interpolation`}` switches the text after it into the
format-spec sub-language.  The token is reported in the `change`
field of the values yielded by
[`split_delimiters`.](#split_delimiterss-delimiters--state-yields4)

</dd></dl>

`nested`, `literal`, and `change` can also be *assigned to*, as
attributes--but only until the first time the `Delimiter` is used
in a compiled grammar.  After that the `Delimiter` is frozen, and
assigning raises `ValueError`; to make a variant, modify a
`copy()`, which is always unfrozen.  Assignment exists so you can
construct grammars with reference cycles: build the `Delimiter`
objects, then close the loop by assigning at the end.  (Cycles
via `nested` are rarer than you'd think: inside a *non-quoting*
delimiter the grammar's whole top level is already live, no
back-reference needed.  Explicit cycles only come up when a chain
of *quoting* delimiters loops privately.)

Equality on `Delimiter` objects is deep (and cycle-safe): two
independently-built grammars with the same structure compare
equal.

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
    D'Artagnan
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


#### `merge_columns(*columns, column_separator=" ", overflow_strategy=OverflowStrategy.RAISE, overflow_before=0, overflow_after=0, tab_width=8, raw=None)`

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

A column tuple may carry an optional fourth member,
`relative_tabs`, governing how tabs in that column's text are
expanded (they're always expanded to spaces, using `tab_width`).
If true (the default), each line's tabs expand in the column's
own coordinates--as if the line started at column 1--and the
expanded text shifts rigidly into place, so the column's
internal alignment survives wherever the column lands.  If
false, tabs expand at the column's position on the page (its
nominal position: an overflow strategy that shifts lines
doesn't move their tab stops).

Note that this function does not text-wrap the text of the
columns.  The text in the columns should already be broken
into lines and separated by newline characters.  (Lines in
that are longer than that column tuple's `max_width` are
handled with the `overflow_strategy`, described below.)

`column_separator` is printed between every column.

`overflow_strategy` tells merge_columns how to handle a column
with one or more lines that are wider than that column's `max_width`.
The supported values are:

* `OverflowStrategy.RAISE`: Raise an OverflowError.  The default:
  overflow is an error, and it shouldn't pass silently unless you
  explicitly silence it by picking another strategy.
* `OverflowStrategy.INTRUDE_ALL`: Intrude into all subsequent columns
  on all lines where the overflowed column is wider than its `max_width`.
* `OverflowStrategy.DELAY_ALL`: Delay all columns after the overflowed
  column, not beginning any until after the last overflowed line
  in the overflowed column.  (Help-style tables usually want this one.)

When `overflow_strategy` is `INTRUDE_ALL` or `DELAY_ALL`, and
either `overflow_before` or `overflow_after` is nonzero, these
specify the number of extra lines before or after
the overflowed lines in a column.

`raw` is an optional callback mapping a line to its *plain text*,
for columns whose lines carry in-band styling markup.  It defaults
to the identity.  Line *widths* — for overflow detection and for
padding a column to its `max_width` — are measured on `raw(line)`,
while the original line (markup and all) is what's emitted.

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

```Python
>>> multipartition('aXbYz', ('X', 'Y'))
('a', 'X', 'bYz')
```

If none of the separators are found in the string, returns
a tuple containing `s` unchanged followed by two empty strings.

Returns a tuple of slices of `s`—including zero-length boundary slices
when needed—so concatenating the returned values reconstitutes the
original `s`.

`multipartition` is *greedy:* if two or more separators appear at
the leftmost location in `s`, `multipartition` partitions using
the longest matching separator.  For example:

```Python
>>> multipartition('wxabcyz', ('a', 'abc'))
('wx', 'abc', 'yz')
```

Passing in an explicit `count` lets you control how many times
`multipartition` partitions the string.  `multipartition` will always
return a tuple containing `(2*count)+1` elements.
Passing in a `count` of 0 will always return a tuple containing `s`.

If `separate` is false, multiple adjacent separator strings get joined
together, behaving like one big separator.  If `separate` is true,
they're kept separate.  Example:

```Python
>>> multipartition('aXYbYXc', ('X', 'Y',), count=2, separate=False)
('a', 'XY', 'b', 'YX', 'c')
>>> multipartition('aXYbYXc', ('X', 'Y',), count=4, separate=True )
('a', 'X', '', 'Y', 'b', 'Y', '', 'X', 'c')
>>> multipartition('aXYbYXc', ('X', 'Y',), count=2, separate=True )
('a', 'X', '', 'Y', 'bYXc')
```

If `reverse` is true, multipartition behaves like `str.rpartition`.
It partitions starting on the right, scanning backwards through s
looking for separators.

For more information, see the tutorial on
[**The `multi-` family of string functions.**](#The-multi--family-of-string-functions)
</dd></dl>

#### `multireplace(s, replacements, count=-1, *, reverse=False)`

<dl><dd>

Like `str.replace`, but supports multiple replacement strings,
and replaces them all in a single pass.

`s` can be either `str` or `bytes`.

`replacements` should be a mapping (e.g. a `dict`) mapping
old strings to the new strings replacing them.  Every key
and every value must be the same type as `s`, keys cannot
be empty, and `replacements` cannot itself be empty.

Returns a copy of `s` with every occurrence of every key
replaced by that key's value.  `multireplace` makes only one
pass over `s`: text that has already been replaced is never
itself examined for further replacements.  For example:

```Python
>>> big.multireplace('ab', {'a': 'b', 'b': 'a'})
'ba'
```

Calling `str.replace` repeatedly gets this wrong:
`'ab'.replace('a', 'b').replace('b', 'a')` returns `'aa'`,
because the second `replace` re-replaces the output of the first.

`multireplace` is *greedy:* if two or more keys match at the
same location in `s`, `multireplace` replaces using the longest
matching key.  For example:

```Python
>>> big.multireplace('a category', {'cat': 'dog', 'category': 'taxonomy'})
'a taxonomy'
```

not `'a dogegory'`.

`count` should be either an integer or `None`.  If `count` is an
integer greater than -1, `multireplace` will replace no more
than `count` times, like the `count` parameter to `str.replace`.

`reverse` controls the direction `multireplace` scans in.
Scanning from the end of the string (`reverse=True`) has two
effects.  First, if `count` is a number greater than 0, the
replacements start at the end of the string rather than the
beginning.  Second, if there are overlapping instances of keys
in the string, `multireplace` will prefer the rightmost key
rather than the leftmost:

```Python
>>> big.multireplace('xa0bx', {'a0': 'A', '0b': 'B'})
'xAbx'
>>> big.multireplace('xa0bx', {'a0': 'A', '0b': 'B'}, reverse=True)
'xaBx'
```

You can pass in instances of subclasses of `bytes` or `str`
for `s` and the keys and values of `replacements`, but the
base class for all of them must be the same (`str` or `bytes`).

`multireplace` supports [`big.string`:](#the-big-string) if `s`
is a `big.string` object, the result is reassembled with
[`string.cat`,](#stringcatstrings) so it's a `big.string` too,
and every unchanged segment still knows its original file,
line, and column.  (Also available as the method
[`string.multireplace`.](#stringmultireplacereplacements-count-1--reversefalse))

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

Returns an iterator yielding values split from `s`.  The values yielded
are slices of the original object, or in some cases adjacent slices joined
with `+`.  All slices are yielded in left-to-right order; this even includes
zero-length strings, which are sliced from the contextually correct spot.

If `keep` is true and `strip` is false, joining all the
yielded strings together will recreate `s`.

`multisplit` is *greedy:* if two or more separators start at the same
location in `s`, `multisplit` splits using the longest matching separator.
For example:

```Python
big.multisplit('wxabcyz', ('a', 'abc'))
```

yields `'wx'` then `'yz'`.

`keep` indicates whether or not multisplit should preserve the separator
strings in the strings it yields.  It supports two values:

<dl><dt>

false (the default)
</dt><dd>

Yield just the split strings, discarding the separators.

</dd><dt>

true
</dt><dd>

Yield 2-tuples containing a non-separator string and its
subsequent separator string.  Either string may be empty;
the separator string in the last 2-tuple will always be
empty, and if "s" ends with a separator string, *both*
strings in the final 2-tuple will be empty.
</dd></dl>

`keep` also supports three symbolic values.  These values
are *deprecated,* and will be removed no sooner than August
2027; passing any of them emits a `DeprecationWarning`:

<dl><dt>

`AS_PAIRS`
</dt><dd>

The old namefor what is now `keep=True`,
the 2-tuple `(string, separator)` form.

</dd><dt>

`ALTERNATING`
</dt><dd>

Yield alternating strings in the output: strings consisting
of separators, alternating with strings consisting of
non-separators.  The first and last will be non-separators,
which means this always yields an *odd* number of substrings.
If `separate` is true, separator strings
will contain exactly one separator, and non-separator strings
may be empty; if `separate` is false, separator strings will
contain one or more separators, and non-separator strings
will never be empty, unless `s` was empty.

You can recreate the original string by using `"".join`
to join the strings yielded.

You can recreate this format using `keep=True` with the following:
```Python
flat = list(itertools.chain.from_iterable(big.multisplit(s, seps, keep=True)))
flat.pop()
```

</dd><dt>

`JOINED`
</dt><dd>

Each separator is appended to its preceding string.

You can recreate this format using `keep=True` with the following:
```Python
(a + b  for (a, b) in big.multisplit(s, seps, keep=True))
```

</dd></dl>

> **Note:** In big 0.13 and earlier, `keep=True` meant what `JOINED`
  now means: separators appended to their preceding strings.  0.14
  changed its meaning to the 2-tuple form.  (Why?  The 2-tuple form
  can be mechanically converted into any other form, making it the
  ur-form that's useful in every situation.  It's just a better API
  this way--you don't need any of that other junk, I promise.)

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
multisplit("A x x Z", (" x ",), keep=True) => ("A", " x "), ("x Z", "")
```

If you pass in a true value for `reverse`, `multisplit` will prefer
the rightmost overlapping separator:

```
multisplit("A x x Z", (" x ",), keep=True, reverse=True) => ("A x", " x "), ("Z", "")
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

Returns `s` unchanged, or a slice of `s`, with the leading
and/or trailing separators stripped.

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
for the full API.  (Exceptions: `sub`, `subn`, and `Match.expand`
construct new strings, so they return plain `str`/`bytes`.)
</dd></dl>


#### `python_delimiters`

<dl><dd>

A delimiters mapping suitable for use as the `delimiters`
argument for  [`split_delimiters`](#split_delimiterss-delimiters--state-yields4).
`python_delimiters` defines *all* the delimiters for Python, and
is able to correctly split any modern Python text at its delimiter boundaries.

One rule of thumb:

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
  `b`, `f`, `r`, and `u`, in both lower and upper case.  (On
  Python 3.14 and newer, also `t`, for t-strings--which get the
  same special `{`interpolation`}` handling as f-strings.)
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
  If the text being split ends with a comment *without* a newline,
  you'll see yield where `open` is `'#'`, followed by a
  slightly-strange final yield: `text` will be the body of the
  comment, and the `open`, `close`, and `change` fields will all be
  an empty string.

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

There are entries in `python_delimiters_version` for every version of
Python supported by big (currently 3.6 to 3.14).  Each entry maps to
the grammar for *that* version of Python, independent of the running
interpreter; the only grammar fork in that range is t-strings, added
in Python 3.14, so `'3.6'` through `'3.13'` all map to one (t-free)
grammar and `'3.14'` maps to the t-aware one.

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

#### `split_delimiters(s, delimiters={...}, *, state=(), yields=4)`

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
contains four fields:

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

</dd></dl>


Iterating over a `SplitDelimitersValue` object yields these four
values in that order, so you can unpack it directly:

```Python
for text, open, close, change in big.split_delimiters(s):
    ...
```

A *change* delimiter changes the semantics of the *current*
delimiter, without entering a new nested delimiter.  The canonical
example is the colon inside curly braces inside a Python f-string:
before the colon, `#` means "line comment"; after it, `#` is just
another character.

At least one of the four strings will always be non-empty.
(Only one of `open`, `close`, and `change` will ever be non-empty in
a single `SplitDelimitersValue` object.)  If `s` doesn't end with
an opening, closing, or changing delimiter, the final value yielded
will have empty strings for `open`, `close`, and `change`.

The `yields` parameter is *deprecated*, and will be removed no
sooner than August 2027.  In big
0.12.5 through 0.13 it selected between yielding three values--the
pre-0.12.5 behavior--and yielding all four.  As promised in
[the 0.12.5 release notes,](#0125) that transition period is
over: `split_delimiters` always yields four values now, and the
only permitted value for `yields` is 4.  (Code that dutifully
migrated to `yields=4` keeps working; simply remove the argument
at your leisure.)  Relatedly, the `SplitDelimitersValue` object
has a *deprecated* `yields` attribute, which likewise once told
you whether the object iterated as three or four values; it now
always returns 4, and will be removed at the same time as the
`yields` parameter.

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
`escape` works inside both `quotes` and `multiline_quotes`,
and shields exactly one following character, like backslash
in Python.  So inside a `"""` string, `\"""` is an escaped
quote mark followed by two live quote marks--just like
Python--and doesn't close the string.

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
  different strings, use [`split_delimiters`](#split_delimiterss-delimiters--state-yields4).

</dd></dl>

#### `split_text_with_code(s, *, code_indent=4, tab_width=8)`

<dl><dd>

Splits `s` into individual words,
suitable for feeding into
[`wrap_words`](#wrap_wordswords-margin79--code_indentnone-indent-left_column1-tab_width8-two_spacestrue-rawnone).

`s` may be either `str` or `bytes`.

Paragraphs indented by less than `code_indent` will be
broken up into individual words.

`code_indent` must be an int.  If it's nonzero, lines indented
by at least `code_indent` columns are "code lines": paragraphs
of them preserve their whitespace, internal and leading, and
their linebreaks.  (This preserves the formatting of code
examples when these words are rejoined into lines by
[`wrap_words`](#wrap_wordswords-margin79--code_indentnone-indent-left_column1-tab_width8-two_spacestrue-rawnone).)
Code lines are emitted verbatim, tabs included; `wrap_words`
expands their tabs at render time, when it knows what column
the line lands at.  If `code_indent` is 0, there are no code
lines: everything is just text.

In text, a tab survives as its own `'\t'` word: a run of
whitespace containing k tabs becomes exactly k `'\t'` words,
in order--the rest of the whitespace is just separation, and
is thrown away as usual.  `wrap_words` renders a `'\t'` word
by placing the next word at the next tab stop.

The only whitespace-only words `split_text_with_code` will
ever emit are `'\n'` (line break), `'\n\n'` (paragraph break),
and `'\t'` (tab).

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

#### `toy_multisplit(s, separators)`

<dl><dd>

A toy version of [`multisplit`.](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)

`s` should be `str` or `bytes`.  `separators` should be a list or
tuple of `str` (or `bytes`, matching `s`); if `separators` is
itself a single `str` or `bytes`, every character (or byte) in it
is a separator.  `separators` must be non-empty and must not
contain the empty string.

Returns a list of 2-tuples of

```
(string, separator)
```

where `string` is a (possibly empty) substring of `s` containing
no separators, and `separator` is the separator that followed it.
The final 2-tuple's separator is always the empty string.
Splitting is greedy: at each position, the longest matching
separator wins.  The result is identical to

```Python
list(multisplit(s, separators, keep=True, separate=True))
```

Why use this instead of `multisplit`?  It has no startup time.
It's also available as a snippet.

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

#### `wrap_words(words, margin=79, *, code_indent=None, indent='', left_column=1, tab_width=8, two_spaces=True, raw=None)`

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
A double `'\n\n'` indicates a paragraph break.
Two line breaks in a row (`'\n'`, `'\n'`) doesn't count as
a paragraph break (`'\n\n'`).
A single `'\t'` indicates a tab: the next word is placed at the
next tab stop, as governed by `tab_width` and `left_column`.  A
tab renders as spaces--`wrap_words` is the final rendering, and
it knows what column everything lands at, so its output contains
no tabs.  No space is added around a tab (the tab IS the
separation); consecutive tabs advance consecutive stops; if the
word after a tab doesn't fit on the line, the word wraps and the
tab dies with the line, just like a space would.
Any other whitespace-only strings are unsupported, and if
you pass in a `words` array to `wrap_words` containing one,
its behavior is undefined.

`margin` specifies the maximum length of each line. The length of
every line will be less than or equal to `margin`, unless the length
of an individual element inside `words` is greater than `margin`.

`left_column` is the 1-based "virtual left column": the column
your output will start at, if you're going to place it somewhere
other than the left edge of the page.  It only affects how tabs
are rendered--tab stops live at fixed columns of the page
(9, 17, 25, ... with the default `tab_width` of 8), so text that
starts at column 5 reaches its first tab stop after four
characters, not eight.  `margin` is unaffected: it's the width
of the block `wrap_words` produces, wherever you put it.

If `two_spaces` is true, elements from `words` that end in
sentence-ending punctuation (`'.'`, `'?'`, and `'!'`)
will be followed by two spaces, not one.

`raw` is an optional callback mapping a word to its *plain text*,
for callers whose words carry in-band styling markup (so the emitted
word is wider than the text the reader sees).  It defaults to the
identity.  Every place `wrap_words` *inspects* a word — its width
for the margin, its trailing punctuation for `two_spaces`, and the
whitespace / first-character tests that detect line breaks and code
lines — runs on `raw(word)`, while the *original* word is what gets
emitted.  `wrap_words` never slices a word, so a plain-text view is
all it needs.

`indent` prefixes the wrapped lines.  It may be a single string,
used for every line, or a list or tuple of strings: the first
line gets `indent[0]`, the second line `indent[1]`, and so on;
once the indents run out, the last one repeats for the remaining
lines.  A paragraph break resets the sequence, so the first line
of every paragraph gets `indent[0]`.  The blank lines separating
paragraphs are never indented.

`code_indent` controls code lines.  A line that starts with
whitespace is a code line: the elements
[`split_text_with_code`](#split_text_with_codes--code_indent4-tab_width8)
emits for code carry their own leading indentation, and ordinary
wrapped lines always start with a word.  By default
(`code_indent=None`) code lines get no separate treatment: they
consume from `indent` like any other line--mid-paragraph they
count against the sequence, and a paragraph that opens with a
code line gets `indent[0]`.  Pass a string, or a list or tuple
of strings--same shape and rules as `indent`--and code lines
draw from `code_indent`'s own sequence instead, no longer
consuming from `indent`.  `code_indent=''` means code lines get
no indent at all.

Indents count against `margin`: a line's indent plus its words
fit in `margin` columns.  Tabs in an indent are expanded to
spaces at the indent's true position (an indent always starts
its line, at `left_column`), using `tab_width`.  Trailing
whitespace in an indent is preserved--for an indent like `'* '`,
that's the point.  An indent as wide as `margin` raises
`ValueError`, as does an indent containing any linebreak
character (as defined by `linebreaks` / `bytes_linebreaks`).

Elements in `words` are not modified--except for tab expansion;
any leading or trailing whitespace will be preserved.  You can
use this to preserve whitespace where necessary, like in code
examples.  Tabs inside a code line are expanded to spaces when
the line is rendered, at the column where they actually land.

An element of `words` may also be a *tuple*--an **instruction**
rather than a word.  Its first item names the instruction:

* `('indent', first, ..., last)` switches the active indent
  context mid-stream, using the same rules as the `indent`
  parameter, and resets the line counter (so the next line is a
  "first line").  Passing `indent=X` behaves as if the matching
  `('indent', ...)` were prepended to `words`.
* `('def start',)` ... `('def end',)` bracket a **definition
  list**, with one `('term', *words)` per entry followed by the
  words (and instructions) of its details.  `wrap_words` measures
  the terms, picks a detail column, and lays each entry out
  compact (term and details sharing a line) or tall.

These let a whole styled document bake to a flat tuple of
constants and wrap to any width later; `big.markdown`'s
[`layout_document`](#layout_documentdocument) produces exactly
such a tuple.

If `words` yields bytes, `indent` and `code_indent` must be
bytes too (or lists or tuples of bytes).

If `words` is empty, raises `ValueError`.  (Note that
`split_text_with_code` never returns an empty list--for empty
input it returns `['']`, which `wrap_words` is happy to wrap.)

For more information, see the tutorial on
[**Word wrapping and formatting.**](#word-wrapping-and-formatting)

Widths are measured in *code points* — `len(raw(word))` — not terminal
cells.  Wide characters (CJK, most emoji), combining marks, and emoji
with modifiers occupy a different number of columns than they have
code points, so text carrying them may misalign by a column or two; a
cell-width policy is a possible later addition.

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

#### `duration_human(t, *, long=True, want_microseconds=None)`

<dl><dd>

Returns an elapsed time formatted as a human-readable string,
breaking it into days, hours, minutes, and seconds.  The long
format reads like prose, joined with Oxford comma rules--two
units get a bare `and`, three or more get commas with `, and`
before the last:

```Python
>>> big.duration_human(90)
'1 minute and 30 seconds'
>>> big.duration_human(90061)
'1 day, 1 hour, 1 minute, and 1 second'
```

Pass in a false value for `long` to get the short format:

```Python
>>> big.duration_human(90, long=False)
'1m 30s'
>>> big.duration_human(90061, long=False)
'1d 1h 1m 1s'
```

`t` should be a number of seconds, either `int` or `float`,
or a `datetime.timedelta` object.

Days are the largest unit; a long duration is a large number
of days (`'365 days and 6 hours'`).  Units are included starting
at the largest nonzero unit and stopping at the last nonzero
unit; zero units in the middle are included, so every rendered
duration reads unambiguously:

```Python
>>> big.duration_human(3600, long=False)
'1h'
>>> big.duration_human(3601, long=False)
'1h 0m 1s'
```

A zero duration is `'0 seconds'` (or `'0s'`).  A negative
duration is formatted like a positive one, with a leading `'-'`.

`want_microseconds` controls sub-second precision, and may be
`None` (the default), `True`, or `False`:

* `True` means seconds are rendered with microsecond precision.
  Fractional seconds appear only when nonzero, rounded to
  microsecond precision, with trailing zeroes removed
  (`'1.5 seconds'`, never `'1.500000 seconds'`).
* `False` means seconds are rendered as whole seconds: the
  duration is rounded to the nearest second, ties rounding up
  (away from zero).
* `None` means `want_microseconds` decides for itself: it's
  `True` if the total duration is less than one minute, and
  `False` otherwise.  While a duration is short enough that
  fractions of a second matter, you get them; once it grows a
  minutes column, you don't:

```Python
>>> big.duration_human(1.5)
'1.5 seconds'
>>> big.duration_human(90061.5)
'1 day, 1 hour, 1 minute, and 2 seconds'
>>> big.duration_human(90061.5, want_microseconds=True)
'1 day, 1 hour, 1 minute, and 1.5 seconds'
```

The integer arithmetic is exact, so rounding can never produce
a nonsense duration like `'59.9999999 seconds'` or
`'60 seconds'`: 59.9999999 seconds renders as `'1 minute'`.
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

**Provenance and mutation:** methods that return *substrings*
of the original--slicing, `partition`, `split`, `strip`,
`replace`, and friends--always return `big.string` objects with
true positions.  But methods that *change the text*
(`capitalize`, `casefold`, `expandtabs`, `format`, `format_map`,
`lower`, `swapcase`, `title`, `upper`) return a plain `str`
when the text actually changes.  There's no honest position to
report for synthesized text, and `big.string` prefers failing
loudly (plain `str` has no `.where`) over reporting approximate
positions.  When such a method doesn't change the text, you get
the original `big.string` back, provenance intact.  (To expand
tabs *with* provenance, use `detab()`, which synthesizes only
the spaces.)

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

`string.expandtabs` deliberately keeps `str.expandtabs`'s exact
behavior: `big.string` starts as "a str that knows its own
provenance", and a shadowed `str` method must never produce
different text than `str` would.  The improvement is opt-in,
under a distinct name: `string.detab(tabsize=None)` expands
each tab according to its own origin's coordinates--the column
the tab sits at *in its source*, tab stops anchored at its
origin's `first_column_number`, the same arithmetic `where`
uses--rather than `str.expandtabs`'s assumption that everything
starts at column 0 of nowhere.  By default each tab uses its
origin's `tab_width`; pass an int to override (`tabsize <= 0`
removes tabs, as with `str`).  The result is a `big.string`: the
expanded spaces are synthesized text, and the characters around
them keep their provenance, so `where` still points into the
original source.

If you pass a `big.string` into Python modules implemented in C,
the returned substrings will be plain `str` objects.  big provides
wrappers for three of these, drop-in replacements where the returned
substrings will be `big.string` objects preserving provenance:

* [`string.generate_tokens`](#stringgenerate_tokens), a wrapper for
  [`tokenize.generate_tokens`](https://docs.python.org/3/library/tokenize.html#tokenize.generate_tokens),
* [`string.compile`](#stringcompileflags0), a wrapper for `re.compile`, and
* [`string.literal_eval`](#stringliteral_eval), a wrapper for
  [`ast.literal_eval`](https://docs.python.org/3/library/ast.html#ast.literal_eval).

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


#### `string.literal_eval()`

<dl><dd>

Wraps
[`ast.literal_eval`](https://docs.python.org/3/library/ast.html#ast.literal_eval),
preserving provenance when the result is a `str`.
Equivalent to calling
[`big.builtin.literal_eval`](#literal_evals) with this string;
see that entry for the full description of how provenance
is preserved.
</dd></dl>


#### `string.multireplace(replacements, count=-1, *, reverse=False)`

<dl><dd>

Calls
[`big.multireplace`](#multireplaces-replacements-count-1--reversefalse)
with this string.  The result is reassembled with
[`string.cat`,](#stringcatstrings) so it's a `big.string` too,
and every unchanged segment still knows its original file, line,
and column.  (The `string.multisplit` and `string.multipartition`
methods don't need this help: they return slices, which carry
their provenance naturally.  Replacing is the only member of the
`multi-` family that builds new text.)
</dd></dl>


#### `string.partition(sep, *, count=1)` and `string.rpartition(sep, *, count=1)`

<dl><dd>

Behaves like `str.partition` and `str.rpartition`,
but adds one feature: a `count=` parameter that
specifies how many times to split the string.
`count` must be an "index" with a value 0 or higher.
The returned tuple will be length `(count * 2) + 1`.
</dd></dl>

### `string_context`

The value returned by the `string.context` property.

`str(s.context)` evaluates to a string that represents
the "context" of `s`--where `s` was sliced from in the
larger string object.  For example:

```Python
    line = "elif attempt(blast):"
    s = line.partition('(')[2][:5] # s is 'blast'
    print(s.context)
```

would print:

```
    elif attempt(blast):
                 ^^^^^
```

Note that `str(s.context)` only shows one line of context;
if `s` is a multi-line string, this will only show the first
line.  If you want to show all lines, use `s.context.all`
instead, see below.

`string_context` supports the following attributes:

* `parts` is a tuple of "context line" tuples representing
  the lines of `str(context)`.  Each "context line" tuple
  matches `(before, span, after, linebreak)`, and has named
  accessors for these values.  These values are strings;
  joining all the strings of all the tuples produces
  `str(context)`.
* `all` is like `str(context)`, but contains context lines
  for all lines, in case `context` contains linebreaks.
* `all_parts` is like `parts`, but contains the parts for
  all the lines of `all`.

In addition, it provides many of the `string` properties,
like `where`, `origin`, `line_number`, etc.  These are the
same as the `string` object the context was taken from.

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

Cuts nodes from this list and returns them in a new `linked_list`.

`start` and `stop`, if specified, must be iterators over this
list.  If `start` is `None`, it defaults to the first node
after head.  (If the list is empty, this will be tail.)
If `stop` is `None`, it defaults to tail.
The range of nodes cut includes `start` but excludes `stop`.
`start` must not point to a node after `stop`.

`lock` is passed to the new list's constructor; if `None`,
the new list reuses this list's `lock` parameter.

If any nodes are cut, the `start` and `stop` iterators will
still point at the same nodes--which means `start` will have
been moved to the new list.

Raises `SpecialNodeError` if `start` points to head,
because you can't cut the head of the list.

`start` and `stop` may be reverse iterators; however, the
linked list resulting from a cut will have the elements
in forward order.  If either `start` or `stop` is a reverse
iterator, then they must both be reverse iterators (or `None`),
and:

 * `start` defaults to the last node before tail,
 * `stop` defaults to head,
 * `start` must not point to a node after `stop`, and
 * raises `SpecialNodeError` if `start` points to head.

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

#### `linked_list.move(where, start=None, stop=None)`

<dl><dd>

Moves a range of nodes to after `where`.

`start` and `stop`, if specified, must be iterators over this
list.  If `start` is `None`, it defaults to the first node
after head.  (If the list is empty, this will be tail.)
If `stop` is `None`, it defaults to tail.  The range of nodes
moved includes `start` but excludes `stop`.  `start` must not point
to a node after `stop`.  `where` must be an iterator over this list.
`where` must not point to a node being moved, or tail.

Raises `SpecialNodeError` if `start` points to head,
because you can't move the head of the list.

`start` and `stop` may be reverse iterators.  If either `start`
or `stop` is a reverse iterator, then they must both be reverse
iterators (or `None`), and:

 * `start` defaults to the last node before tail,
 * `stop` defaults to head,
 * `start` must not point to a node after `stop`, and
 * raises `SpecialNodeError` if `start` points to head.

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

Reverses all nodes in the linked list, including special nodes.
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

#### `linked_list.rmove(where, start=None, stop=None)`

<dl><dd>

Like [`linked_list.move`,](#linked_listmovewhere-startnone-stopnone)
but `start` must come *after* `stop`, the nodes are inserted
*before* `where`, and `where` cannot be head.  All other behaviors
are unchanged (e.g. `start` is inclusive, `stop` is exclusive).


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
except: if `where` is `None`, the nodes are prepended to the list.
If `where` is not `None`, the nodes are inserted before
(rather than after) the node pointed to by `where`.  Raises
`SpecialNodeError` if `where` is head, because you can't insert
nodes before head.
</dd></dl>

#### `linked_list.sort(key=None, reverse=False)`

<dl><dd>

Sorts the linked list in ascending order.  Arguments are the
same as `list.sort`.  `linked_list.sort` moves nodes rather
than swapping values, so iterators continue to point at the
same nodes.
</dd></dl>

#### `linked_list.splice(other, *, where=None)`

<dl><dd>

Moves all nodes from `other` into this list.  `other`
must be a `linked_list`; after a successful splice, `other`
will be empty.

`where` must be an iterator over this list, or `None`.
If `where` is an iterator, the nodes are inserted after
the node pointed to by `where`.  If `where` is `None`,
the nodes are appended.  Raises `SpecialNodeError` if
`where` is tail, because you can't insert nodes after tail.

See the [**The big `linked_list`**](#the-big-linked_list) tutorial for more.
</dd></dl>

#### `linked_list.tail()`

<dl><dd>

Returns a forwards iterator pointing at the linked list's
tail sentinel node.
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

#### `linked_list_iterator.move(where, stop=None)`

<dl><dd>

Moves nodes from the current node up to (but not including) `stop`
to after `where`.  If `stop` is `None`, the moved range extends to tail.

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

#### `linked_list_iterator.rmove(where, stop=None)`

<dl><dd>

Like [`linked_list_iterator.move`](#linked_list_iteratormovewhere-stopnone),
but moves the range to before `where` and walks the range in the reverse
direction.

</dd></dl>

#### `linked_list_iterator.rpop(index=0)`

<dl><dd>

Removes and returns the value at `index` relative to the current
position.  If `index` is `0` (the default), removes the current
node and the iterator advances forwards to the next node.
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

#### `linked_list_iterator.special`

<dl><dd>

An attribute containing the *special* attribute of the current node:
`None` for normal nodes, or a string (`'head'`, `'tail'`, or
`'special'`) for special nodes.
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

Behaves like [`linked_list_iterator.before`](#linked_list_iteratorbeforecount1)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.append(value)`

<dl><dd>

Behaves like [`linked_list_iterator.prepend`](#linked_list_iteratorprependvalue)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.before(count=1)`

<dl><dd>

Behaves like [`linked_list_iterator.after`](#linked_list_iteratoraftercount1)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.copy()`

<dl><dd>

Returns a copy of the reverse iterator, pointing at the same node.
</dd></dl>

#### `linked_list_reverse_iterator.count(value)`

<dl><dd>

Behaves like [`linked_list_iterator.rcount`](#linked_list_iteratorrcountvalue)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.cut(stop=None, *, lock=None)`

<dl><dd>

Behaves like [`linked_list_iterator.rcut`](#linked_list_iteratorrcutstopnone--locknone)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.exhaust()`

<dl><dd>

Advances the reverse iterator to point to head.
</dd></dl>

#### `linked_list_reverse_iterator.extend(iterable)`

<dl><dd>

Behaves like [`linked_list_iterator.rextend`](#linked_list_iteratorrextenditerable)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.find(value)`

<dl><dd>

Behaves like [`linked_list_iterator.rfind`](#linked_list_iteratorrfindvalue)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.insert(index, object)`

<dl><dd>

Inserts `object` relative to the current position, with reversed
index direction.
</dd></dl>

#### `linked_list_reverse_iterator.is_special()`

<dl><dd>

Behaves like [`linked_list_iterator.is_special`](#linked_list_iteratoris_special)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.linked_list`

<dl><dd>

Returns the `linked_list` this iterator belongs to.
</dd></dl>

#### `linked_list_reverse_iterator.match(predicate)`

<dl><dd>

Behaves like [`linked_list_iterator.rmatch`](#linked_list_iteratorrmatchpredicate)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.move(where, stop=None)`

<dl><dd>

Behaves like [`linked_list_iterator.rmove`](#linked_list_iteratorrmovewhere-stopnone)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.next(default=undefined, *, count=1)`

<dl><dd>

Behaves like [`linked_list_iterator.previous`](#linked_list_iteratorpreviousdefaultundefined--count1)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.pop(index=0)`

<dl><dd>

Behaves like [`linked_list_iterator.rpop`](#linked_list_iteratorrpopindex0)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.prepend(value)`

<dl><dd>

Behaves like [`linked_list_iterator.append`](#linked_list_iteratorappendvalue)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.previous(default=undefined, *, count=1)`

<dl><dd>

Behaves like [`linked_list_iterator.next`](#linked_list_iteratornextdefaultundefined--count1)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.rcount(value)`

<dl><dd>

Behaves like [`linked_list_iterator.count`](#linked_list_iteratorcountvalue)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.rcut(stop=None, *, lock=None)`

<dl><dd>

Behaves like [`linked_list_iterator.cut`](#linked_list_iteratorcutstopnone--locknone)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.remove(value, default=undefined)`

<dl><dd>

Behaves like [`linked_list_iterator.rremove`](#linked_list_iteratorrremovevalue-defaultundefined)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.reset()`

<dl><dd>

Resets the reverse iterator to point to tail.
</dd></dl>

#### `linked_list_reverse_iterator.rextend(iterable)`

<dl><dd>

Behaves like [`linked_list_iterator.extend`](#linked_list_iteratorextenditerable)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.rfind(value)`

<dl><dd>

Behaves like [`linked_list_iterator.find`](#linked_list_iteratorfindvalue)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.rmatch(predicate)`

<dl><dd>

Behaves like [`linked_list_iterator.match`](#linked_list_iteratormatchpredicate)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.rmove(where, stop=None)`

<dl><dd>

Behaves like [`linked_list_iterator.move`](#linked_list_iteratormovewhere-stopnone)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.rpop(index=0)`

<dl><dd>

Behaves like [`linked_list_iterator.pop`](#linked_list_iteratorpopindex0)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.rremove(value, default=undefined)`

<dl><dd>

Behaves like [`linked_list_iterator.remove`](#linked_list_iteratorremovevalue-defaultundefined)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.rsplice(other)`

<dl><dd>

Behaves like [`linked_list_iterator.splice`](#linked_list_iteratorspliceother)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.rtruncate()`

<dl><dd>

Behaves like [`linked_list_iterator.truncate`](#linked_list_iteratortruncate)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.special`

<dl><dd>

Identical to [`linked_list_iterator.special`](#linked_list_iteratorspecial).
</dd></dl>

#### `linked_list_reverse_iterator.splice(other)`

<dl><dd>

Behaves like [`linked_list_iterator.rsplice`](#linked_list_iteratorrspliceother)
with the directions reversed.
</dd></dl>

#### `linked_list_reverse_iterator.truncate()`

<dl><dd>

Behaves like [`linked_list_iterator.rtruncate`](#linked_list_iteratorrtruncate)
with the directions reversed.
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
  a [`Match`](https://docs.python.org/3/library/re.html#re.Match) object
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
provides workarounds for the three worst offenders: `re`, `tokenize`,
and `ast.literal_eval`.
big's `string` object has a `compile` method that is a drop-in replacement
for `re.compile`, and all the methods you call on it will return `string`
objects instead of `str` objects.  The `string` object also has a method
called `generate_tokens` that produces the same output as `tokenize.generate_tokens`,
except (of course!) all the strings returned in its `TokenInfo` objects
are `string` objects.  And it has a `literal_eval` method that evaluates
the string just like `ast.literal_eval`—but if the result is a `str`,
it comes back as a `string` that knows where it came from, whenever
that's honestly possible.  (`re` and
`tokenize` only *locate* substrings, so their wrappers preserve provenance
perfectly.  `literal_eval` *transforms* its input—decoded escape sequences
produce characters that don't exist in the source—so its wrapper preserves
provenance on a best-effort basis, returning a plain `str` when the value
can't be truthfully mapped back onto the source; see its documentation
for the details.)

Unfortunately, there's one more wrinkle.  The objects returned by CPython's
`re` module don't let you instantitate them, nor subclass them.
They deliberately set an internal flag that means "Python code is not
permitted to subclass this class".  This means it's *impossible* for
`String.compile` to return objects that pass `isinstance` tests.
`String.compile` returns a `Pattern` object, but it's *not* an instance
of `re.Pattern`, and `isinstance` tests will fail.  **big** was forced
to reimplement these objects, and we ensure they behave identically
to the originals, but CPython makes this facet of incompatibility unfixable.


### Migrating from `lines` to `string`

`lines`, `LineInfo`, and the `lines_*` modifier functions are
deprecated, and will be removed no sooner than March 2027.  `string`
replaces them--and the migration makes your code smaller, because
everything `LineInfo` tracked by hand travels *inside* the string now.

The core translation:

| the `lines` pipeline | the `string` way |
|---|---|
| `lines(s, source=f)` | `string(s, source=f).splitlines(True)` |
| `info.line_number`, `info.column_number` | `line.line_number`, `line.column_number` (any slice knows) |
| `info.leading` / `info.trailing` / clipping | just `strip()`--the stripped slice keeps true positions |
| `lines_strip_indent(li)` | [`strip_indents(lines)`](#strip_indentslines--tab_width8-linebreakslinebreaks) |
| `lines_strip_line_comments(li, markers)` | [`strip_line_comments(lines, markers)`](#strip_line_commentslines-line_comment_markers--escape-quotes-multiline_quotes-linebreakslinebreaks) |
| `lines_filter_empty_lines(li)` | `(line for line in lines if line.strip())` |
| `lines_grep(li, pattern)` | `string(pattern).compile()`, then test each line--matches keep positions |
| error messages from `info` fields | `f"{line.where}: ..."` |

A worked example.  The old pipeline:

```Python
for info, line in big.lines_strip_indent(big.lines(text, source='demo.txt')):
    if not line:
        continue
    print(info.indent, info.line_number, info.column_number, line)
```

becomes:

```Python
s = big.string(text, source='demo.txt')
for depth, line in big.strip_indents(s.splitlines(True)):
    stripped = line.strip()
    if not stripped:
        continue
    print(depth, stripped.line_number, stripped.column_number, stripped)
```

These print identical values--`strip_indents` reports the same depths,
and the stripped slice reports the same line and column `LineInfo`
used to track.  But notice what *isn't* there: no `LineInfo`, no
clipping bookkeeping, no metadata object riding alongside every line.
When you need to report an error, any slice can speak for itself:

```Python
raise SyntaxError(f"{stripped.where}: frobnitz expected")
# demo.txt line 4 column 5: frobnitz expected
```

And the modifiers you used to chain become ordinary Python--filters
are generator expressions, grep is a compiled `Pattern` whose matches
keep their positions, and any custom modifier you wrote is now just a
loop over strings that already know where they live.

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

There are actually two types of node in a big `linked_list`: "data"
nodes, which store a value, and "special" nodes, which don't store a
value.  Why are these "special" nodes needed?  First, `linked_list`
makes a design choice that's uncommon but not exactly rare for
linked lists: the "head" and "tail" nodes are "special" nodes in
the linked list (rather than being references to the real first and
last nodes).  When you create a new `linked_list` object, it already
contains *two* nodes, not *zero:* one "head" node, and one "tail" node.
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
[`list`](https://docs.python.org/3/library/stdtypes.html#list)
and
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
* `move` is like a `cut` followed immediately by a `splice` back
  into the same list.  But `move` is easier... and a lot faster!
* `rcut`, `rsplice`, and `rmove` are "reversed" versions of
  `cut`, `splice`, and `move` respectively.


### `linked_list` iterators

While developing `linked_list`, it occured to me: the classic use
case for a linked list involves an arbitrarily-long sequence of
data, which you iterate over and process.  For example, compilers
generally represent the program being compiled as a linked list
of "basic blocks".

When using a linked list for this class of problem, you generally
operate on a pointer to the linked list node under current
consideration.  In Python parlance, you iterate over the list,
getting a reference to each node in the list in turn.  You perform
your computation on that node, then iterate, moving on to the next
one.

However, you often want to *modify* the list while you're doing
this.  You may want to remove the node, or insert new nodes,
or both--replace the node with something else.  But idiomatic
Python iterators don't let you do anything like that.  All they
know how to do is "advance to the next value and yield it".
This was a genius design choice for Python, but for our linked
list it's simply not enough.

`linked_list` solves this by making its iterators far more
powerful.  One way of describing this is like a *database cursor:*
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

Here are just a few examples.  In these examples, `it`
is always a forwards iterator:

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
We'll create a new empty linked list, then create an iterator
over that linked list, and call `next` on it twice:

```Python
t = linked_list((1,))
it = iter(t)
value_a = next(it, None)
value_b = next(it, None)
```

When this is done, `value_a` will be `1`, and `value_b` will be `None`.
How does this work internally?

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
(To be clear: the *value* of the node isn't the string `"special"`.
As mentioned before, special nodes *have* no value.  We just put
the word "special" there to annotate that as a special node.)

If you now iterated over the linked list:

```Python
for i in t:
   print(i)
```

you'd see 1, 2, 4, and 5, like you'd expect.  The special node is
still there, but remember the rule: *linked list iterators automatically
skip over special nodes.*

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
* Evaluating `it[-1:1]`.  (But `it[-1:1:2]` works!  It skips over `it[0]`.)
* Popping the current value using `it.pop()` or `it.rpop()`.

If you're not sure whether or not your iterator is pointing at a special node,
you can call `it.is_special()`; that returns `True` if `it` is pointing
at a special node.  You can also examine the `it.special` property.
That evaluates to `None` for a data node, `"head"` for the head node,
`"tail"` for the tail node, and `"special"` for any other special node.
(Thus, this value is *also* true for a special node and false for a data node.)


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

a *reverse* iterator would "see" the same list like this:

```
[tail] <-> [5] <-> [4] <-> [3] <-> [special] <-> [2] <-> [1] <-> [head]
```

Apart from this behavioral change, reverse iterators behave identically
to forwards iterators.  They support the exact same APIs with the same
arguments.

This makes the behavior of a reverse iterator easy to predict.  For example,
if `fi` is a forwards iterator, and `ri` is a reverse iterator on the same list:

* A newly-created reverse iterator points to the "tail" node, and `ri.reset()`
  resets `ri` so it points at the "tail" node again.
* A reverse iterator becomes exhausted once it reaches the "head" node.
  `ri.exhaust()` moves `ri` so it points at the "head" node.
* `ri.append()` inserts *before* the current node, `ri.prepend()`
  inserts *after* the current node.  Remember, from the perspective
  of `ri`, it's inserting those nodes in the correct places!
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
* When traversing the list with an iterator using `next()` and/or `previous()`, iterators will skip past
  `"special"` nodes, but they always stop at head and tail.
* Operations on iterators that act on multiple nodes tend to include the node they're pointing at.
* iterator[0] *always* refers to the node the iterator is currently pointing at, even if it's a special
  node.  If the index is non-zero, it skips over special nodes.
* You can't ever insert a node *before* head, or *after* tail.  You can't ever remove head or tail.
* Any operation involving an empty range (start==stop) is a no-op and doesn't raise.


</dd></dl>


## The big `Log`

<dl><dd>

### tl;dr

Do you ever do print-style debugging?  Of course you do.
big's `Log` is the best print-style debugging log you've ever seen.

`Log` is deliberately *not* an "enterprise" logger.  There are no
severity levels, no handler hierarchies, no configuration files.
Just lightning-fast logging, with timestamps, hierarchy,
support for multiple threads, pretty Unicode boxes, and minimal
overhead.

   * `Log` automatically prepends each log message with the
     elapsed time so far, and the name of the thread that
     logged the message.
   * `Log` gives your output *shape*.  `log.enter("subsystem")`
     prints a banner and indents everything until `log.exit()`--
     so your log nests the way your program nests.  `log.box(s)`
     prints an eye-catching call-out box.
   * Want to write to a file instead?  Maybe a temporary file with a
     dynamically-generated filename, so old logs don't get
     overwritten?  Buffer everything and write it all at once?
     Log to a file *and* the screen?  It's one argument to the
     constructor.
   * Multithreaded programs are where debug prints go to die--and
     where `Log` shines.  All the work runs through one queue, so
     messages never interleave mid-line, and nested blocks stay
     contiguous.  And `Log` itself does all its work in a separate
     thread by default, so it takes up minimal time in your actual
     work threads.
   * Done debugging?  Don't delete your log lines--*pause* the log,
     or construct it with no destinations.  Which brings us to the
     single most important idiom:


### The most important idiom

```Python
if log:
    log(f"boiler state: {pprint.pformat(hopper)}")
```

A `Log` is *true* when it's configured to produce output,
and *false* when it has been silenced.  Prepend your log calls
with `if log:` and the message arguments are **never even evaluated.**
I used to comment out all my log calls when I wanted to turn
logging off--now I just configure that same log object to be
false, and I'm done.

Anything that quiets the log makes it evaluate to false--pausing,
closing, or not being configured to write anywhere.


### Quick start

```Python
import big.all as big

log = big.Log()

log("Hello, world!")
with log.enter("parsing"):
    log("phase one")
    log.box("something noteworthy!")
log("all done")
log.close()
```

This prints something like:

```
000.0000000000             │ ╔═════════════════════════════════════════════════
000.0000000000             │ ║ Log start at 2026/07/12 17:36:16.985964 PDT
000.0000000000             │ ╚═════════════════════════════════════════════════
000.0000845460   MainThread│ Hello, world!
000.0003936510             │ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
000.0003936510             │ ┃enter┃ parsing
000.0003936510             │ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
000.0004167140   MainThread│     phase one
000.0004868770   MainThread│     ┌─────────────────────────────────────────────
000.0004868770   MainThread│     │ something noteworthy!
000.0004868770   MainThread│     └─────────────────────────────────────────────
000.0022459870             │ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
000.0022459870             │ ┃exit ┃ parsing
000.0022459870             │ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
000.0027115580   MainThread│ all done
000.0029511810             │ ╔═════════════════════════════════════════════════
000.0029511810             │ ║ Log finish at 2026/07/12 17:36:16.988915 PDT
000.0029511810             │ ╚═════════════════════════════════════════════════
```

Notice you didn't have to explicitly *start* the log.  Logs start lazily,
on the first message.  If you never log, `Log` never opens your file,
never computes a tempfile name, never prints a banner--nothing happens.

(However, the "log start" time *is* the time when you create the `Log`
object.  Also, banners aren't "from" a thread conceptually, they're "from"
the log itself, so their thread column is blank.)


### Quick start, line by line

We're gonna go over every line in the "Quick start" section and
walk you through it.

Apart from the import, the first line of the "Quick start" makes the log object:
```Python
log = big.Log()
```

Without arguments, `Log` will call Python's `print` to print every line of the log.
See the *Destination* section below to see how to change that.

Also, by default a `Log` uses "threaded" mode.  Every time you send a message to
the log, it's bundled up and shipped across to a worker thread that does the actual
logging.  This minimizes how much time logging takes up in your threads.  (And in
Python's glorious free-threaded future, all the work will be done by one of your
lazy spare CPU cores!  Put 'em to work!)

The next line actually writes to the log:
```Python
log("Hello, world!")
```

Yup, to log, you just call the log handle itself.  Behaves exactly like Python's
`print` function--takes `sep` and `end`.  (Not `file` though, sorry.)

This line produced the following output:

```
000.0000000000             │ ╔═════════════════════════════════════════════════
000.0000000000             │ ║ Log start at 2026/07/12 17:36:16.985964 PDT
000.0000000000             │ ╚═════════════════════════════════════════════════
000.0000845460   MainThread│ Hello, world!
```

This includes the log start banner.  `Log` doesn't print *anything* until your first
actual log message.  The start time of the log is the time the `Log` constructor 
was created.  After that, we can see the call to `log()` itself happened 85 microseconds
later, from the `MainThread`, and the message was `Hello, world!`


Next two lines:
```Python
with log.enter("parsing"):
    log("phase one")
```

We're using a `with` statement, so `log.enter` must be a Python "context manager".
What "enter" means is, we're "entering" a nested logging block.  This does three things:

* Prints a banner at the beginning and end of the nested block.
* Messages logged inside the nested block get indented.
* Buffers up the contents of the nested block, only sending it to the log when it's done.

This last one means: when you log from multiple threads, messages from the other threads
don't interrupt your nested blocks.  If we simply interleaved messages from every thread
when they arrived, the lovely indented block of the "enter" would get interrupted with
outdented junk from these other miscreant threads.

This doesn't produce any output--yet!--so let's go on to the next line:

```Python
    log.box("something noteworthy!")
```

`box` is a method that "calls out" this log message through formatting.  By default,
it draws a three-sided box around the message using Unicode line-drawing characters.

Since this is the last line inside the `with` statement, let's show you the output
of the entire `with log.enter` block here:

```
000.0003936510             │ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
000.0003936510             │ ┃enter┃ parsing
000.0003936510             │ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
000.0004167140   MainThread│     phase one
000.0004868770   MainThread│     ┌─────────────────────────────────────────────
000.0004868770   MainThread│     │ something noteworthy!
000.0004868770   MainThread│     └─────────────────────────────────────────────
000.0022459870             │ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
000.0022459870             │ ┃exit ┃ parsing
000.0022459870             │ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

You can see the enter and exit banners, and the `phase one` message and the box
are both indented.  And again: if this program was multithreaded, this entire
series of banners and log messages would get added to the log atomically.

We're gonna combine together the last two lines:

```Python
log("all done")
log.close()
```

You've seen calling the log object before.  Calling `close()` on the log
closes it, naturally.  This writes out the log:

```
000.0027115580   MainThread│ all done
000.0029511810             │ ╔═════════════════════════════════════════════════
000.0029511810             │ ║ Log finish at 2026/07/12 17:36:16.988915 PDT
000.0029511810             │ ╚═════════════════════════════════════════════════
```

Once the log is closed, it ignores log messages--it's not an error to
use a closed handle, but the log messages are simply dropped on the floor.

However, you *can* restart a closed log, with the `reset()` method.
This brings the log back to life, pointed at all the same destinations.
You can also reset a non-closed log, which effectively closes and
reopens it.


### Destinations

A `Log` can write to one or more places simultaneously.
We call such a place a "destination".  Anything sensible
works as a destination, and you can just pass them in to
the `Log` constructor, as many as you want:

```Python
log = big.Log()                          # no explicit destinations? implicitly calls print.
log = big.Log(print)                     # print?  *explicitly* calls print.
log = big.Log("/tmp/my.log")             # path to a file?  append to it.
log = big.Log(big.TMPFILE)               # TMPFILE constant?  a timestamped temporary file.
log = big.Log(array)                     # Python list?  append to it.
log = big.Log(my_function)               # Python callable?  call it with every message.
log = big.Log(sys.stderr)                # an open file object?  write messages to it.
log = big.Log(None)                      # nothing!  and bool(Log(None)) is False.
log = big.Log("/tmp/my.log", print)      # append to a file *and* calls print.
```

File logging is buffered by default: output accumulates in memory and
is written in one open-write-close when the log is flushed or closed.

You can control exactly where your data goes and how it gets there.
For example: if you don't want buffering when writing to files, pass
in a `big.File(path, buffering=False)` destination to open the file
up front and flush every message as it happens--slower, but nothing
is lost if your program dies mid-run.

You can write your own custom destinations, if big doesn't provide
enough already!

### Writing to the log, and formatting

Couldn't be easier.  The `Log` itself is callable, just call it.
It behaves like Python's `print` function; it takes `*args`,
and `sep` and `end` and `flush`.  (Okay, it doesn't take `file`.)

```Python
log = big.Log()
log('Hello, world!')
```

This will produce normal output in the log:
```
000.0058273670   MainThread│ Hello, world!
```

But there are a couple more methods.  They mostly differ in how
the message is formatted.

Every message is formatted using a template.  Some templates
are for built-in log banners, like the "log start" or "enter" banners.
But there are other formats for other styles of logging.

You saw `box` above, which draws a box around the message to draw
attention to it.  There's also `write`, which writes a message without
any formatting, and `log`, which is like `print`.  But `box`, `write`,
and `print` only take one string to log, unlike `print` which takes
`*args` and `sep` and `end` and all that.

You can also create your own arbitrary formats, and specify which format
you want to use with any of the above logging functions with the `format=`
keyword-only parameter:

```Python
formatter = big.TextFormatter(formats={
    "phase": {"template": "{prefix}{line*}\\n{prefix}== {message}\\n{prefix}{line*}\\n"},
    })
log = big.Log(formatter=formatter)
log.log('indexing', format='phase')
```

This also binds a method with that format name you can call directly.
Because we made a `"phase"` format, we now also have a `phase` method:
```Python
log.phase("indexing")
```

### Pause and resume

`log.pause()` silences the log--no messages, no banners, no
destination activity--until `log.resume()`.  It's the runtime
equivalent of commenting out your prints, minus the part where your
codebase fills up with commented-out prints.  `pause()` returns a
context manager that resumes on exit, and pausing nests correctly.

`log.reset()` closes and reopens the log: fresh start time, fresh
banners, and a fresh filename for `TMPFILE` logs.


### Threads and faults

By default a `Log` runs its formatting and writing on a worker
thread, so logging costs your program almost nothing at the call
site.  Message content is captured *at the moment you log*
(so mutable objects render as they were, not as they became), and
everything downstream happens in order on the queue.  Pass
`threaded=False` to do all the work inline instead--output appears
immediately, which is sometimes what you want when debugging a crash.

A log must never take your program down.  If a destination or
formatter raises, `Log` calls your `fix` callback (see
[`default_fix`](#default_fixo-fault)); if the fault can't be fixed,
the offender is quietly dropped from the routing and the log carries
on.  Your program never crashes because of its own debug logging.


### Structured logging: Sink

Want the log as *data* instead of text?  Pass a [`Sink`](#sink):

```Python
sink = big.Sink()
log = big.Log(sink)
log("interesting")
log.close()

for event in sink:
    if event.type == 'log':
        print(event.elapsed, event.message, event.duration)
```

A `Sink` receives [`SinkEvent`](#sinkevent) objects--one object
per log message, and special objects for start, end, enter, and exit
events.  These objects carry the elapsed time, nesting depth, thread,
format name, and raw message text of the message--but not the rendered
version, as sink events contain structured, unformatted data.
This gives you the raw data from the log, in its original format,
in case you want to do your own analysis or formatting.

### Sharp edges

  * Message *content* is captured at log time, but with `threaded=True`
    the rendering happens slightly later, on the worker thread.
    `log.flush()` (or `close()`) waits for everything logged so far.
  * If two threads log at exactly the same moment, the order the two
    messages appear in the log is not guaranteed.  Either way, each
    message is intact and timestamped.
  * The format names `'start'`, `'end'`, `'enter'`, and `'exit'`
    are reserved for `Log` itself; logging a message with one of
    those formats raises `ValueError`.

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

(In case you want your class to define `__new__` instead of (or in
addition to) `__init__`, that works too!  Your bound inner class's
`__new__` method gets to add `outer` as its second argument,
after the `cls` argument.)

#### Inheritance

Bound inner classes get slightly complicated when mixed with inheritance.
It's not all that difficult, you merely need to obey some rules.:

<dl><dd>

**Rule 1:** *A bound inner class can inherit normally from any unbound class.*

**Rule 1a:** *If a class C inherits from any bound inner class P, for all
practical purposes C *must* be decorated with `@BoundInnerClass` or
`@UnboundInnerClass`.*

**Rule 2:** *If your bound inner class calls `super().__init__`, and its
parent class is also a bound inner class,* **don't** *pass in `outer` manually.*
When you instantiate a bound inner class, `outer` will be automatically
passed in to *all* `__init__` methods of *every* bound inner parent class.

**Rule 2a:** A corollary of rule 2: *If your bound inner class calls `super().__new__`, and its
parent class is also a bound inner class,* **don't** *pass in `outer` manually.*

**Rule 3:** *A bound inner class can only inherit from a parent bound inner class
if the parent is defined in the same outer class or a base of the outer class.*
If Child inherits from Parent, and Child and Parent are both
decorated with `@BoundInnerClass` (or `@UnboundInnerClass`), both classes
must be defined in the same outer class (e.g. `Outer`) or in a base class
of Child's outer class.  This is a type relation constraint; bound inner
classes guarantee that "outer" is an instance of the outer class.

**Rule 3a:** A corollary of rule 3: *When a subclass of a bound inner class
is itself decorated with `@BoundInnerClass` or `@UnboundInnerClass`, it
must live in the same outer class or in a subclass of that outer class.*

**Rule 4:** **Directly** *inheriting from a* **bound** *inner class is unsupported.*
If `o` is an instance of `Outer`, and `Outer.Inner` is an inner class
decorated with `@BoundInnerClass`, **don't** write a class that directly
inherits from `o.Inner`, for example `class Mistake(o.Inner)`.
You should *always* inherit from the unbound version, like this:
`class GotItRight(Outer.Inner)`

**Rule 5:** *An inner class that inherits from a bound inner class, and which also
wants the outer instance passed in to its `__new__` and `__init__`, should be
decorated with [`BoundInnerClass`](#boundinnerclasscls).*

**Rule 6:** *An inner class that inherits from a bound inner class, but doesn't
wants the outer instance passed in to its `__new__` and `__init__`, should be
decorated with [`UnboundInnerClass`](#unboundinnerclasscls).*
`@UnboundInnerClass` means this class's own `__new__` / `__init__` won't
receive `outer`--but its bound inner *parent* classes still *will.*

</dd></dl>

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

  * Are these classes usable?  Possibly.  Yes, you can construct
    an `Outer.Inner` directly, to construct an `Inner` object without
    using a bound version of the class. You'll have to pass in the
    outer parameter by hand--just like you'd have to pass in the
    `self` parameter by hand when calling
    a method via the *class* (`Outer.method`) rather than via an
    *instance* of the class (`o.method`).  This won't work if
    `Outer.Inner` is a subclass of *another* bound inner class,
    and calls its `super().__init__`.  The injection of the outer
    instance argument happens when the class is bound, and this
    handles injecting the argument for all the base classes too.
    Without this binding mechanism getting involved, the `outer`
    argument won't get supplied when calling the base class's
    `__init__`.

* Can you declare a class that inherits from a bound inner class,
  but which itself is not decorated with either `@BoundInnerClass`
  or `@UnboundInnerClass`?  Yes--but only in limited circumstances.

  If `class P` is decorated with `@BoundInnerClass`, and undecorated
  `class C(P)` inherits from it, `C` is just an ordinary subclass of
  the unbound version of `P`.  It just doesn't participate in any
  bound-inner-class stuff.

  But this means `outer` won't be automatic.  Either callers must
  pass `outer` explicitly when constructing `C`, or `C` must supply
  an `outer` itself by overriding the relevant construction methods.
  If `P` defines `__init__`, `C` must arrange to pass `outer` to `P.__init__`. 
  If `P` defines `__new__`, `C` must arrange to pass `outer` to `P.__new__`.
  If `P` defines both, `C` must handle both.

  Also, this only works one level deep.  In our example, it worked
  because `P` didn't inherit from anything.   If instead `P` inherited
  from another bound inner class, normal bound-inner-class cooperative
  inheritance expects `outer` to be supplied by the bound-inner-class
  machinery.  Since undecorated `C` is not using bound inner classes
  at all, that chain breaks.

  (But even this can be made to work.  It's just that every intermediate
  class has to be written to explicitly support this behavior.  In our
  example, we'd have to rewrite `P` so it explicitly passes `outer` in
  to *its* parent when it isn't being run as a bound inner class--i.e.
  when `is_bound(cls)` is false inside `__new__`, or `is_bound(type(self))`
  is false inside `__init__`.  Every intermediate class would have to do
  something like this to support an undecorated leaf class.)

* Can you declare a class that inherits from a bound inner class,
  but which itself is not decorated with either `@BoundInnerClass`
  or `@UnboundInnerClass`?  Yes--but only in limited circumstances.

  * If `class P` (parent) is decorated with `@BoundInnerClass`,
    and `class C(P)` (child) is not decorated with either
    `@BoundInnerClass` or `@UnboundInnerClass`, this can be made
    to work.  IF C explicitly defines either `__new__` or `__init__`,
    it must explicitly pass in an argument for the `outer` parameter
    on `P`.  This gets you an instance of `C`, which is a subclass
    of an unbound version of `P`.

    But this only works one level deep.  If, instead of `class P`,
    we had `class P(GP)` (grandparent), and `class GP` was decorated
    with `@BoundInnerClass`, this simply cannot be made to work.
 
* Bound inner classes are cached in the outer object, which both
  provides a small speedup and ensures that `isinstance`
  relationships are consistent.  This is an explicit feature and
  you're permitted to rely on it.

   * If you use slots on your outer class, you must add a slot for
     BoundInnerClass to store its cache.  Just add BOUNDINNERCLASS_OUTER_SLOTS
     to your slots tuple, like so:

```Python
__slots__ = ('x', 'y', 'z') + BOUNDINNERCLASS_OUTER_SLOTS
```

* Base classes are matched by class *identity*, never by name.  A
  same-named inner class inheriting from an ancestor outer's inner
  class--`class MyApp(BaseApp)` defining
  `class Config(BaseApp.Config)`--chains normally: bare
  `super().__init__()` delivers `outer` automatically.

* Binding only goes one level deep.  If you had a bound inner class `C`
  define inside another bound inner class `B`, which in turn was defined
  inside a class `A`, the constructor for `C` would be called with
  the `B` object, but not the `A` object.

* A bound inner class holds a *strong* reference to its outer
  instance--exactly like a bound method holds `__self__`.  The
  tempting one-liner `Outer().Inner()` therefore just works: the
  bound class keeps the temporary alive.  Two consequences worth
  knowing: a bound class (or any instance of one, via its class)
  keeps its outer alive as long as it lives; and the resulting
  outer → cache → bound class → outer reference cycle means outer
  instances that ever bound an inner class are reclaimed by the
  cycle collector, not by reference counting.

* You can't use pickle to serialize instances of bound inner classes.
  Sorry, but bound inner classes don't support pickle.

  The details, for those who are interested:

<dl><dd>

  pickle expects classes to be findable by name, in the module where
  they were defined; it serializes instances as essentially
  "class X.Y plus the instance state."  But bound inner classes don't
  work that way.  When you access an inner class through an outer
  instance, BoundInnerClass creates a dynamic subclass of that
  inner class, bound to that specific outer instance, and accessible
  by way of the descriptor protocol.

  That dynamic bound subclass has a name, but you can't use that
  name to look up the dynamic subclass--you'll find the original
  unbound inner class instead.  But that's the only way pickle knows
  how to find classes (by default).  pickle's just doesn't
  know how to work with bound inner classes.

  It's possible *custom* pickle machinery could make it work.  But
  BoundInnerClass doesn't provide that machinery, and doing it correctly
  would involve subtle pickle details: custom reducers, __new__ arguments,
  state restoration, weak outer references, and implementation details
  of bound inner classes.  It's not something BoundInnerClass could
  simply automate for users.  So, it's unsupported.

</dd></dl>

  The *outer* instance, though, copies, deepcopies, and pickles just
  fine--even after its inner classes have been bound.  `BoundInnerClass`'s
  internal cache doesn't travel with it; the duplicate simply re-binds
  its inner classes, lazily, on first access, exactly like a fresh
  instance.

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
[`multireplace`,](#multireplaces-replacements-count-1--reversefalse)
[`normalize_whitespace`,](#normalize_whitespaces-separatorsnone-replacementnone)
[`lines`,](#bigtext)
and several other functions.

The values returned or yielded by these functions are slices of the original object,
or in some cases adjacent slices joined with `+`.  All slices are returned in
left-to-right order; this even includes zero-length strings, which are sliced
from the contextually correct spot.

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
strings in the strings it yields.  It's either false or true.

When `keep` is false, `multisplit` throws away the separator strings;
they won't appear in the output.

```Python
    >>> list(big.multisplit('apple#banana-cookie', ('#', '-'))) # "keep" defaults to False
    ['apple', 'banana', 'cookie']
    >>> list(big.multisplit('apple-banana#cookie', ('#', '-'), keep=False))
    ['apple', 'banana', 'cookie']
```

When `keep` is true, `multisplit` keeps the separators as separate
strings.  It doesn't yield bare strings; instead, it yields 2-tuples of
strings.  Every 2-tuple contains a non-separator string followed by a
separator string.

If the original string starts with a separator, the first 2-tuple will contain
an empty non-separator string and the separator:

```Python
    >>> list(big.multisplit('^apple-banana^cookie', ('-', '^'), keep=True))
    [('', '^'), ('apple', '-'), ('banana', '^'), ('cookie', '')]
```

The last 2-tuple will *always* contain an empty separator string:

```Python
    >>> list(big.multisplit('apple*banana+cookie', ('*', '+'), keep=True))
    [('apple', '*'), ('banana', '+'), ('cookie', '')]
    >>> list(big.multisplit('apple*banana+cookie***', ('*', '+'), keep=True, strip=True))
    [('apple', '*'), ('banana', '+'), ('cookie', '')]
```

Because of this rule, if the original string ends with a separator,
and `multisplit` doesn't `strip` the right side, the final tuple
emitted will be a 2-tuple containing two empty strings:

```Python
    >>> list(big.multisplit('appleXbananaYcookieX', ('X', 'Y'), keep=True))
    [('apple', 'X'), ('banana', 'Y'), ('cookie', 'X'), ('', '')]
```

This looks strange and unnecessary.  But it *is* what you want.
This odd-looking behavior is discussed at length in the section below, titled
[Why do you sometimes get empty strings when you split?](#why-do-you-sometimes-get-empty-strings-when-you-split)

The 2-tuple form is lossless, and every other form you might want is a
mechanical transformation of it.  Joining the 2-tuples with `a + b`
reproduces the old (big 0.13) meaning of `keep=True`, separators appended
to their preceding strings:

```Python
    >>> ["".join(t) for t in big.multisplit('apple$banana~cookie', ('$', '~'), keep=True)]
    ['apple$', 'banana~', 'cookie']
```

Flattening the 2-tuples, then discarding the always-empty trailing
separator, produces the alternating form: non-separator and separator
strings, alternately, beginning and ending with a non-separator string.
(Historically this was `keep=ALTERNATING`.)

```Python
    >>> import itertools
    >>> flat = list(itertools.chain.from_iterable(big.multisplit('appleXbananaYcookie', ('X', 'Y'), keep=True)))
    >>> flat.pop()  # discard the always-empty trailing separator
    ''
    >>> flat
    ['apple', 'X', 'banana', 'Y', 'cookie']
```

`AS_PAIRS` is the old spelling of what `keep=True`
now means--pass `keep=True` instead.  `ALTERNATING` yields the alternating
form directly (without the trailing empty string)--transform the 2-tuples
instead.  And `JOINED` is the old (0.13) meaning of `keep=True`, separators
appended to their preceding strings; it exists to ease migration.

> **Note:** In big 0.13 and earlier, `keep=True` meant separators appended
  to their preceding strings, as in the `"".join` example above.  0.14
  changed its meaning to the 2-tuple form.
  Also, the symbolic constants for `keep` are *deprecated,* and will be
  removed no sooner than August 2027; passing any of them emits
  a `DeprecationWarning`.  

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
    if keepends:
        # keep=True yields (line, end) 2-tuples;
        # keepends means gluing each end back on.
        l = [line + end for line, end in big.multisplit(s, linebreaks,
            keep=True, separate=True, strip=False)]
    else:
        l = list(big.multisplit(s, linebreaks,
            keep=False, separate=True, strip=False))
    if l and not l[-1]:
    	# yes, ''.splitlines() returns an empty list
        l.pop()
    return l

def _partition_to_multisplit(s, sep, reverse):
    if not sep:
        raise ValueError("empty separator")
    # flatten the keep=True 2-tuples, and drop the
    # always-empty trailing separator
    l = tuple(big.multisplit(s, (sep,),
        keep=True, maxsplit=1, reverse=reverse, separate=True))
    l = tuple(x for pair in l for x in pair)[:-1]
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

This "emit an empty string" behavior also has ramifications when `keep` is true.
The behavior here seemed so strange, initially I thought it was wrong.
But I've given it a *lot* of thought, and I've convinced myself that
this is correct:

```Python
    >>> list(big.multisplit('1,2,,3', (',',), keep=True, separate=True, strip=False))
    [('1', ','), ('2', ','), ('', ','), ('3', '')]
    >>> list(big.multisplit(',1,2,3,', (',',), keep=True, separate=True, strip=False))
    [('', ','), ('1', ','), ('2', ','), ('3', ','), ('', '')]
```

That tuple at the end, just containing two empty strings:

```Python
    ('', '')
```

It's *so strange.*  How can that be right?

Here's the strongest argument that it's correct.  The number of
*fields* a split yields must not depend on `keep`.  `keep` only adds
information about the separators; it must never change how many fields
the string splits into.  Now split `',1,2,3,'` with `keep=False` (and
`separate=True, strip=False`), as in the first example above: you get
`['', '1', '2', '3', '']`--five fields, and that trailing empty field
isn't big's invention, it's `str.split` parity:

```Python
    >>> ',1,2,3,'.split(',')
    ['', '1', '2', '3', '']
```

Python itself asserts that a string ending with a separator has an
empty final field.  So the 2-tuple form of the *identical* split must
also have five entries--and the fifth is that same empty final field,
paired with the separator that follows it, which is nothing: `('', '')`.
Drop the strange tuple, and `keep=True` would claim the string has
*fewer fields* than `keep=False` says it has, for the same split.
The tuple isn't an artifact; it's the empty field every split
vocabulary already agrees exists, wearing 2-tuple clothing.

When called with `keep=True`,
[`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
therefore guarantees that the final tuple will contain an empty
separator string.  If the string you're splitting ends with a
separator, it *must* emit the empty non-separator string, followed
by the empty separator string.

There's a practical bonus, too: with the tuple of empty strings there,
you can easily convert the 2-tuples into any other format you might
want, without needing an `if` statement to add or remove empty stuff
from the end.

I'll demonstrate this with a simple example.  Here's the output of
`multisplit` splitting the string `'1a1z1'` by the separator `'1'`,
and the mechanical conversion of the 2-tuples into every other
format you might want:

```Python
>>> result = list(big.multisplit('1a1z1', '1', keep=True))
>>> result
[('', '1'), ('a', '1'), ('z', '1'), ('', '')]
>>> [s[0] for s in result] # convert to keep=False
['', 'a', 'z', '']
>>> [s[0]+s[1] for s in result] # the old (0.13) keep=True: separators appended
['1', 'a1', 'z1', '']
>>> [s for t in result for s in t][:-1] # the old ALTERNATING form
['', '1', 'a', '1', 'z', '1', '']
```

If the 2-tuple output *didn't* end with that tuple of empty strings,
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
[`split_text_with_code`](#split_text_with_codes--code_indent4-tab_width8),
[`wrap_words(),`](#wrap_wordswords-margin79--code_indentnone-indent-left_column1-tab_width8-two_spacestrue-rawnone),
and optionally
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_strategyoverflowstrategyraise-overflow_before0-overflow_after0-tab_width8-rawnone).
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
[`split_text_with_code`](#split_text_with_codes--code_indent4-tab_width8)
switches between
"text" and "code" mode, it emits a paragraph break.

#### Split text array

A *split text array* is an intermediary data structure
used by **big.text** functions to represent text.
It's literally just an array of strings, where the strings
represent individual word-wrappable substrings.

[`split_text_with_code`](#split_text_with_codes--code_indent4-tab_width8)
returns a *split text array,* and
[`wrap_words()`](#wrap_wordswords-margin79--code_indentnone-indent-left_column1-tab_width8-two_spacestrue-rawnone)
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
[`split_text_with_code`,](#split_text_with_codes--code_indent4-tab_width8)
it'd return this *split text array:*
```Python
[ 'hello', 'there!', 'this', 'is', 'text.', '\n\n',
  'this', 'is', 'a', 'second', 'paragraph!']
```

[`split_text_with_code`](#split_text_with_codes--code_indent4-tab_width8)
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

[`split_text_with_code`](#split_text_with_codes--code_indent4-tab_width8)
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
[`wrap_words`](#wrap_wordswords-margin79--code_indentnone-indent-left_column1-tab_width8-two_spacestrue-rawnone).

#### Merging columns

[`merge_columns`](#merge_columnscolumns-column_separator--overflow_strategyoverflowstrategyraise-overflow_before0-overflow_after0-tab_width8-rawnone)
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
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_strategyoverflowstrategyraise-overflow_before0-overflow_after0-tab_width8-rawnone)
doesn't do its own word-wrapping;
instead, it's designed to consume the output of
[`wrap_words`](#wrap_wordswords-margin79--code_indentnone-indent-left_column1-tab_width8-two_spacestrue-rawnone).)

Each column is passed in to
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_strategyoverflowstrategyraise-overflow_before0-overflow_after0-tab_width8-rawnone)
as a "column tuple":

```Python
(s, min_width, max_width)
```

`s` is the string,
`min_width` is the minimum width of the column, and
`max_width` is the minimum width of the column.

As you saw above, `s` can contain newline characters,
and
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_strategyoverflowstrategyraise-overflow_before0-overflow_after0-tab_width8-rawnone)
obeys those when formatting each column.

For each column,
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_strategyoverflowstrategyraise-overflow_before0-overflow_after0-tab_width8-rawnone)
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
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_strategyoverflowstrategyraise-overflow_before0-overflow_after0-tab_width8-rawnone)
may encounter when the text in a column is wider than that
column's `max_width`.
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_strategyoverflowstrategyraise-overflow_before0-overflow_after0-tab_width8-rawnone)
needs to consider both "overflow lines",
lines that are longer than `max_width`, and "overflow columns",
columns that contain one or more overflow lines.

What does
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_strategyoverflowstrategyraise-overflow_before0-overflow_after0-tab_width8-rawnone)
do when it encounters overflow?
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_strategyoverflowstrategyraise-overflow_before0-overflow_after0-tab_width8-rawnone)
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


## Thread safety in big

<dl><dd>

big's policy, stated once so every module doesn't have to:
**nothing in big is thread-safe unless it explicitly says so.**

The three things that explicitly say so:

* [`linked_list`](#linked_listiterable--locknone) — opt-in:
  pass `lock=True` to the constructor (or supply your own lock).
  Without a lock, a `linked_list` is as thread-unsafe as a `list`.
* [`Scheduler`](#schedulerregulatordefault_regulator) — delegated:
  thread safety comes from the
  [`Regulator`](#regulator) you construct it with.  The default
  `SingleThreadedRegulator` provides none;
  [`ThreadSafeRegulator`](#threadsaferegulator) provides it.
* [`Log`](#the-big-log) — by design: all work funnels through one
  internal job queue, and the threaded and unthreaded configurations
  share one execution model.

Everything else makes no thread-safety guarantees.  Two useful
notes, though:

* big's *immutable* objects — [`string`](#the-big-string),
  [`Version`](#versions-none--epochnone-releasenone-release_levelnone-serialnone-postnone-devnone-localnone),
  [`Delimiter`](#delimiterclose--escape-multilinetrue-quotingfalse-nestednone-literal-changenone),
  the whitespace/linebreak tuples — are safe to *share* between
  threads once constructed, like any immutable Python value.  (Some
  cache lazily-computed values, like `string`'s line and column
  numbers; those caches are benign under concurrent access--every
  thread that races computes and stores the same values.)
* Mutable containers — [`Heap`](#heapi--keynone-reversefalse),
  [`TopologicalSorter`](#topologicalsortergraphnone),
  an unlocked `linked_list` — need external locking if you share
  them, exactly as their stdlib counterparts do.

</dd></dl>

## Borrowable snippets

<dl><dd>

big doesn't just *ship* [`big.snip`](#bigsnip)--it uses it.  big's
own source publishes some of its machinery as snippets: regions of
code bracketed by scissors marker lines, for other projects to
borrow.  Copy one in with `python -m big.snip apply`, and re-sync
it whenever you like with `python -m big.snip sync`--your copy
will update itself!  Requirements resolve automatically, including
the `big license` snippet, so it's all nice and legal.  Any other
dependencies get brought along too.  You get self-contained,
dependency-free code, and a tool that keeps it fresh.

These are the snippets you'll be interested in, by source file.

### `big/itertools.py`

<dl><dt>

`big iterator context and filter`

</dt><dd>

[`iterator_context`](#iterator_contextiterator-start0) and its
[`IteratorContext`](#iterator_contextiterator-start0),
[`iterator_filter`](#iterator_filteriterator--stop_at_valueundefined-stop_at_innone-stop_at_predicatenone-stop_at_countnone-reject_valueundefined-reject_innone-reject_predicatenone-only_valueundefined-only_innone-only_predicatenone-call_everynone), and the `undefined` singleton
they share.

</dd></dl>


### `big/text.py`

<dl><dt>

`big format_definition_list`

</dt><dd>

[`format_definition_list`](#format_definition_listpairs-margin79--definition_left_columnnone-definition_relative_tabstrue-indent---spacer---tab_width8-term_relative_tabstrue).  (Which would have
formatted this very list, if this list weren't Markdown.)

</dd><dt>

`big gently_title`

</dt><dd>

[`gently_title`](#gently_titles--apostrophesnone-double_quotesnone),
plus the private lookup tables it needs.

</dd><dt>

`big toy_multisplit`

</dt><dd>

[`toy_multisplit`](#toy_multisplits-separators), the tiny no-options
`multisplit`.

</dd><dt>

`big word wrap trio`

</dt><dd>

The word wrap trio itself--[`wrap_words`](#wrap_wordswords-margin79--code_indentnone-indent-left_column1-tab_width8-two_spacestrue-rawnone),
[`split_text_with_code`](#split_text_with_codes--code_indent4-tab_width8), and
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_strategyoverflowstrategyraise-overflow_before0-overflow_after0-tab_width8-rawnone)--plus `OverflowStrategy` and
[`expand_tabs`](#expand_tabss--column1-first_column1-tab_width8).

</dd></dl>

</dd></dl>

# Release history

## 0.15
*under development*

<dl><dd>

* Restored `pluralize` to the way I originally wrote it.  When Claude Fable merged
  it, for some reason it saw fit to change the API.  I swear, you take your eye off
  the ball for *one second...!*  The new API takes the *string* first, the *count*
  second, and does *not* insert the count for you at the front of the string.
  (Because you might want to write the count out in English, using `int_to_words`
  for example!)

* 🤖 **New module: [`big.markdown`](#bigmarkdown).**  A parser for a subset of
  standards-compliant CommonMark, plus rendering back ends over a shared
  intermediate representation.  The terminal path is a pipeline: `parse` →
  `style_document` (bake `⦃role⦙…⦄` markup into the text) → `split_styles_document`
  → `layout_document` (lay the blocks out as a *width-independent* "layout" for
  `wrap_words`); at render time `wrap_words` fits the layout to a width,
  `join_styles` coalesces the markup, and a `big.stylesheet` `StyleSheet` paints
  it (or `plain_stylesheet` strips it back to plain text).  Separately,
  `render_document(document, format)` renders the raw IR to GitHub-Flavored
  Markdown, CommonMark, or groff `man`-macro troff.  The parser covers its
  CommonMark subset closely (~85% of the applicable spec test suite; images, raw
  HTML, and entity references are deliberately omitted), plus three extensions:
  GFM strikethrough, definition lists, and GitHub alerts (`> [!NOTE]` and
  friends).  The structural glyphs it draws (bullet, quote bar, thematic
  break, alert emoji and titles) are *glyph roles* (`⦃bullet⦄`,
  `⦃tip_title⦄`, …) resolved by the painting `StyleSheet` —
  `markdown_defaults` for Unicode, `markdown_ascii_glyphs` for ASCII — or
  by the `unicode_glyphs` / `ascii_glyphs` / `glyphs_from_stylesheet` swap
  functions.  `layout_document` hard-codes nothing.  Alongside the literal
  `Text` inline node there's `StyledText`, holding text that is *already*
  well-formed `⦃role⦙…⦄` markup: `style_document` passes it through verbatim
  (rather than escaping it, as it does `Text`) so a caller can carry a role
  structurally — a definition-list term of `StyledText('⦃argument⦙<HOST>⦄')`
  styles to `⦃term⦙⦃argument⦙<HOST>⦄⦄` — validating the markup and refusing an
  unbalanced string at the source; the `render_document` back ends degrade it
  to its stripped text, like `Raw`.  `Document` itself is abstract: `parse`
  returns a `MarkdownDocument` and `style_document` a `StyledDocument`, and
  each stage function demands its kind, so styling twice or exporting a styled
  tree fails loudly.  A link carries its URL as a leading field
  (`⦃link⦙URL⦙label⦄`; the default sheet shows the label alone, a sheet that
  wants the URL uses it).  A list item's continuation indent is a `fill` sized
  when painted, so a sheet may give the bullet any width and the text still
  lines up.

* 🤖 **New module: [`big.stylesheet`](#bigstylesheet).**  The inline
  character-style layer: an `⦃role⦙text⦄` markup language and `StyleSheet`, a
  two-layer recursive style sheet that maps conceptual roles down to a backend's
  escape sequences.  Author markup with `style`, `plain`, and `escape_styles`;
  rewrite it to word granularity and back with `split_styles` and `join_styles`;
  strip it with `strip_styles`; and render it with any of five stock low-level
  maps — `ansi_truecolor_palette`, `ansi_256_color_palette`, `ansi_16_color_palette`,
  `uncolored_palette`, and `plain_palette` — over a 29-color vocabulary plus four
  attributes.  `best_palette` picks the right one for the current terminal.
  Format and role names may contain underscores (e.g. `dark_purple`).  A stock
  `transforms` dict supplies text-shaping roles you can merge into a sheet —
  case (`upper`, `lower`, `title`), whitespace (`strip`, `lstrip`, `rstrip`),
  and geometry sized to a model string (`fill`, `clip`, and `center` / `ljust` /
  `rjust`, each taking an optional tiled fill string).  A transform's fields
  are *visible text* — nested spans resolve, paint is dropped — so `upper` never
  uppercases an escape code and `fill` never counts one; and `plain_stylesheet`
  / `strip_styles` still apply the transforms, dropping only paint.
  `split_styles` and `join_styles` are inverses: the former splits every span
  to word granularity for wrapping, the latter factors the shared span-stack
  prefix back out to minimize a backend's toggles (with `span_linebreaks=True`
  to merge across a single newline; a blank line is always a boundary).  Only a
  span's last field is text — earlier fields are luggage that rides whole on
  every word, and join merges only matching luggage — and, correspondingly, a
  definition's last arg must appear in its replacement while earlier args may
  go unused.  The contract that makes this sound is spelled out in the section
  intro: *decorate early, paint late*.

* 🤖 **`big.text`: [`wrap_words`](#wrap_wordswords-margin79--code_indentnone-indent-left_column1-tab_width8-two_spacestrue-rawnone)
  and [`merge_columns`](#merge_columnscolumns-column_separator--overflow_strategyoverflowstrategyraise-overflow_before0-overflow_after0-tab_width8-rawnone)
  gain a `raw` callback.**  It maps a word or line to its plain text, so callers
  whose words carry in-band styling markup wrap by *visible* width while the
  original styled text is what's emitted.  Defaults to the identity, so existing
  behavior is unchanged.  Widths count code points, not terminal cells (so wide
  characters and emoji may misalign); a cell-width policy is a possible later
  addition.

* 🤖 **`big.text`: [`wrap_words`](#wrap_wordswords-margin79--code_indentnone-indent-left_column1-tab_width8-two_spacestrue-rawnone)
  learns layout instructions.**  An element of `words` may now be a tuple that's
  an *instruction* rather than a word: `('indent', …)` switches the active line
  prefix mid-stream, and `('def start',)` / `('term', …)` / `('def end',)` mark a
  definition list that `wrap_words` lays out itself (compact or tall, choosing a
  detail column to fit).  These let a whole styled document bake to a flat
  constant and wrap to any width later.

* 🤖 **[`big.builtin`](#bigbuiltin) gains `can_colorize` and
  `ansi_color_depth`.**  `can_colorize()` is an alias for CPython 3.13+'s
  `_colorize.can_colorize` (and reimplements the same logic — `NO_COLOR`,
  `FORCE_COLOR`, `TERM`, the tty test — on 3.12 and earlier).  `ansi_color_depth()`
  guesses the terminal's color depth (`truecolor`, `256color`, or `16color`)
  from `COLORTERM` and `TERM`.

* 🤖 **`big.test`: an uncaught `SystemExit` is now a failure, not a fatal
  escape.**  Code under test that calls `sys.exit()` is scored as an ordinary
  failure; only `KeyboardInterrupt` still propagates and stops the run.

* 🤖 **`big.test.preload(package)` is now [`big.builtin.load(name)`](#loadname),
  and better.**  It moved out of `big.test` — putting your local checkout
  first is useful to any script, not just tests — and the rename tracks two
  signature changes.  The parameter is
  now `name`, not `package`, because it accepts a single-file module
  (`name.py`) as well as a package (`name/__init__.py`).  And the return
  value is the imported module, not the `pathlib.Path` directory added to
  `sys.path` — so `mypackage = big.load('mypackage')` replaces the
  load-then-import pair.  (Callers that want the old return value can
  recover it: `pathlib.Path(module.__file__).parents[1]` for a package,
  `.parent` for a module.)  Also, in the REPL — where `sys.argv[0]` is empty
  and there's no script to anchor to — the search now correctly starts in
  the current directory (it used to start one level *up*).  `preload`
  survives as a deprecated alias that emits a `DeprecationWarning`, to be
  removed no sooner than September 2027.

</dd></dl>

## 0.14

*2026/07/16*

<dl><dd>

The biggest release yet!

I worked on this release with Claude Fable 5.  Claude was invaluable,
and Fable 5's code review uncovered many of the smaller bugs and
polish items in big 0.14!  Note however that the interfaces and
functionality are mostly designed by me; Claude did varying amounts
of the implementation.  Items annotated with a robot emoji (🤖)
were worked on by both me and Claude.

### Breaking changes to existing APIs

* 🤖 **`multisplit`'s `keep=True` is now `AS_PAIRS`**.
  In 0.13 and previous, `keep=True` was a distinct output
  format, where the string and the separator were joined
  together.  That's been displaced.  This format now has
  its own own symbolic name, `JOINED`, and `keep=True` is
  now what used to be called `AS_PAIRS` format.  

  Why?  Because it's the only one I ever use.  And it's all
  you ever need--every other output format for `keep` can be
  computed from `AS_PAIRS` format.

  When I initially wrote `multisplit`, it was both filling a
  need, and a bit of research.  I'd never had a multi-splitter
  before, and I didn't know what functionality I'd need.  So I
  threw in the kitchen sink.  And even so, I still didn't hit
  on `AS_PAIRS` format for like six months.  Once I added it,
  it became--and remains--the only non-false `keep` format
  I ever use.  Well, okay, I *did* use `ALTERNATING` for
  something recently.  But it could just as easily have
  used `AS_PAIRS`, which is good, because...

  I'm going to drop support for the alternate output formats.
  `keep` still supports `ALTERNATING`, `AS_PAIRS`, and `JOINED`
  as of today, but they're officially deprecated.  I plan to
  remove them no sooner than August 2027.  After that, `keep`
  will only consider its argument as a boolean, either true
  or false.  A false value will mean discard the separators
  as it does today, a true value will mean return a 2-tuple
  containing the split string and the separator.  (I added
  `DeprecationWarning` exceptions as appropriate.)

* 🤖 **`split_delimiters` now always yields four values.**  As
  promised in 0.12.5, every
  [`SplitDelimitersValue`](#split_delimiterss-delimiters--state-yields4)
  now iterates as `(text, open, close, change)`, with any grammar.
  Code unpacking three values fails loudly ("too many values to
  unpack"), which is the polite kind of breakage.  The `yields`
  parameter survives one more year, *deprecated*: it defaults to
  4, and 4 is the only value it accepts (anything else raises
  `ValueError`)--so code that dutifully migrated to `yields=4`
  keeps working after upgrading, and has a year to drop the
  argument.  The `SplitDelimitersValue` object's `yields`
  attribute survives on the same deprecated footing: it once told
  you whether the object iterated as three or four values, and now
  always returns 4.  Both the parameter and the attribute will be
  removed no sooner than August 2027.

### The `Log` rewrite

`big.log` was a new module in 0.13,
and was already a pretty good time.  But it's gotten a 
*total overhaul* for 0.14 🤖.  The new `Log` has a far more
sophisticated and streamlined internal model.  It's pretty
snazzy!

Two public base classes were renamed along the way, so they
carry their subsystem's name in big's shared `big.all` namespace.
The formatter base class `Formatter` became
[`LogFormatter`](#logformatterformat_dict-types--namenone)--it
collided with `big.template.Formatter`, new in 0.13--and, for
symmetry (and because the whole `Log` API changed anyway, so
you're already rewriting), the destination base class
`Destination` became
[`LogDestination`](#logdestinationtypestrue).  The user-extensible
destination-mapper registry moved with it: the module-level
`Destination_mappers` list is now the `LogDestination.mappers`
class attribute, append your mappers there.  Throughout these
notes, both classes are referred to by their new names even when
describing 0.13 behavior.

The high-level view of the new `Log` internal architecture:

* In 0.13, the `Log` object managed formatting, and formatted every message
  itself.  This conceptually only allowed for one format at a time.  But
  `LogDestination` objects received both the formatted text and the raw message,
  specifically to allow them to log the raw message, or reformat it
  themselves... the responsibilities were a jumbled mess.
  This is significantly improved:
    * The new [`LogFormatter`](#logformatterformat_dict-types--namenone) object
      is responsible for formatting.  A *formatter* transforms a log message
      from one type into another, but the output is still a "log message".
    * [`LogDestination`](#logdestinationtypestrue) objects don't get to reformat
      anymore.  They only get formatted messages, and their only responsibility
      is to send them to an output.
    * Internally, `LogFormatter` objects feed `LogDestination` objects,
      routed N×M and type-checked.
* *All* work is run through an internal job queue--one execution model,
  whether the log is threaded or not.
* Threaded-friendly fault handling: a misbehaving formatter
  or destination is retried, then surgically dropped.  Your program
  never crashes because of its own debug logging.

Other improvements in `Log` in 0.14:

* `if log: log(...)` is the recommended idiom for writing log messages
  with next-to-no runtime impact when logging is turned off.  A `Log`
  handle is true while logging to it would actually deliver--it has
  destinations, it's open, and it isn't paused (directly or by an
  ancestor)--and false the moment any of those stops being true, so
  this idiom means Python doesn't even *evaluate* the log message
  arguments.  Practically free!
* [`enter`](#logentermessage-kwargs)/[`exit`](#logexit) blocks nest,
  indent their contents, and work as context managers.  Now your log
  can have nested structure, reflecting the actual structure of your
  program.
* Logs start lazily: if you never log, `Log` never touches your
  destinations--never opens a file, never prints a banner.
* The other methods have changed a bit too:
  [`pause`/`resume`](#logpause-and-logresume), [`reset`](#logreset),
  `close(wait=)`, `flush(wait=)`, `dirty`, and a settable
  `paused_on_reset` flag to the constructor.
* Like 0.13, formats live in a flat namespace: a dict mapping
  a format's name (`str`) to its value.  `'.'` is reserved in
  format names: if we ever need to create nested formats,
  `'child.start'` can acquire nested semantics as a pure
  addition, with no interface change and no collision with
  any existing names.  (`SinkLogEvent.format` carries the
  plain name too--e.g. `'enter'`.)
* A flat, template-based format tree
  ([`TextFormatter`](#textformatterformat_dictnone--formatsnone-indent-----namenone-prefixnone-width79)):
  The `formats=` dict parameter lets you override built-in formats.
  You can disable a format by setting it to `None`.  Format names
  are automatically mapped to log methods (`'box'` format creates
  `log.box(...)`, etc).
* The default "ASCII art" for the log is now the *"open" Unicode*
  format--box-drawing characters with no right borders and no
  attempt to line up column markers with line-drawing horizontal
  lines.  (Current rendering of Unicode line-drawing characters often
  switches fonts, and the two fonts used to render have different
  charater widths, which throws off the columnar output and makes
  it look *worse* not better.)  Four predefined formats are available:
  the module-level builders
  [`unicode_format_dict()`](#unicode_format_dict-closedfalse) /
  [`ascii_format_dict()`](#ascii_format_dict-closedfalse), each with a
  `closed=True` variant if you want the right borders and such.
  Each returns a fresh format tree you can pass as `format_dict=`.
  By the way, log lines that overflow the right border just
  overwrite it, instead of pushing it out to the right.
* Structured logging: [`SinkFormatter`](#sinkformatter) renders
  messages into [`SinkEvent`](#sinkevent) objects--structured
  logging is just another formatter--and [`Sink`](#sink) collects
  them.  Passing a `Sink` to `Log` routes it automatically.
  A `SinkFormatter` does no text formatting at all (it isn't a
  `TextFormatter`); its events carry the message's structured
  fields, never a rendered string.
  (SinkEvents existed in 0.13; the 0.14 shapes are incompatible.
  `number` is now `session`--a generation counter, incremented by
  `reset()`.  Constructors changed--every event now carries `ns`
  and `epoch`--and `duration` is computed at iteration time and
  ignored by `==`.)
* [`ASCIIFormatter`](#asciiformatter) renders `bytes`--non-ASCII
  characters become backslash escapes.  `log('café')` renders
  `b'caf\\xe9'`; binary-mode
  [`File`](#filepath-initial_modeat--bufferingtrue-encodingnone-subsequent_modenone)
  destinations accept bytes.
* `TextFormatter` no longer mutates the `format_dict` you pass it;
  it deep-copies first, then mutates.
  (`prefix=` used to overwrite into your dict; `formats=` added and
  deleted in it--a module-level house style shared by two formatters
  compounded each other's edits).
* `Log.destinations` is now a *settable* property: assign a list to
  reconfigure the log live.  Removed destinations are flushed (their
  buffered content is written, never dropped), ended, and
  unregistered; added destinations receive a "recap" of the
  already-delivered banners, so a late joiner's output reads as a
  coherent log; and every `LogDestination` gained an `owner` property
 (the `Log` it's attached to, or `None`).
* `write()` is now verbatim: no per-line rstrip, no appended
  newline--"completely as-is" means *completely* as-is.  The
  render pipeline's cleanup is skipped for any format that declares
  `"verbatim": True` in its format dict (as `preformatted` now
  does); your own formats can too.
* Formatter configuration lives entirely on the formatter now:
  `Log`'s 0.13 constructor conveniences `prefix=`, `indent=`,
  `width=`, and `formats=` are all gone--construct your own
  `TextFormatter` (or whatever) and pass it as `formatter=` to
  use it by default.
* Pause is hierarchical: pausing a handle silences its entire
  subtree, including child handles held elsewhere.  (It used to be
  per-session: a held child handle logged straight through a paused
  root.)
* The reserved banner formats (`start`/`end`/`enter`/`exit`) are
  reserved even when smuggled through `Optional`--counterfeit
  banners are a `ValueError` under any spelling.
* The old `Log` API lives on as *deprecated* shims:
  [`OldLog`](#oldlogclocknone) and
  [`OldDestination`](#olddestination), now implemented over the
  new machinery.
* 🤖 The old `Log` could crash on Python 3.12 and earlier during a
  threaded log's shutdown, in the job queue's drain path: it
  used `isinstance(job.involved, threading.Lock)`, but
  `threading.Lock` is a factory function (not a class) before
  Python 3.13, so that `isinstance` raises `TypeError`.  (The
  path only runs when a shutdown blocker is released mid-drain,
  which is why it hid so long.)  Fixed by testing against
  `type(threading.Lock())`, which is a real type on every
  version.  Found by driving `big.log` to 100% test coverage.

We've kept the old 0.13 version of `Log` for you; it's at
 `big.deprecated.Log`. But we also fixed a bug:
* 🤖 `Log` generated garbage for fractional seconds for any event
 past the one-second
 mark: its time formatter computed the fraction as `t - seconds`--
 subtracting the second *count* from a nanosecond timestamp--
 instead of `t % 1_000_000_000`.  An event at 1.5 seconds printed
 as `01.149999999`.  Sub-second events were always formatted
 correctly, which is how a bug this loud hid in a
 performance-analysis class: nobody ever measured anything slow
 enough.  We'll remove the deprecated version no sooner than
 August 2027.

### New modules

#### big.test

[`big.test`](#bigtest) is a tiny, low-ceremony
test harness.  Write plain `def test_foo():` functions with bare
`assert a == b` (no base class, no `self.assertWhicheverOne()`),
and a failing assert still explains itself with the same rich,
type-aware diff `unittest.assertEqual` produces--big borrows
unittest's own machinery, reading the operands out of the dead
frame without re-evaluating anything.  `with raises(ValueError):`
replaces `assertRaises`; `big.builtin`'s [`load()`](#loadname)
puts your local checkout ahead of the installed copy; `run()`
runs plain functions and
`unittest.TestCase` classes in one tally; and a multi-module
driver is a context manager: `with big.test.suite() as run: ...`
prints the summary and sets the exit code when the block ends.
Stdlib-only.  Deliberately *never* imported by `big.all`
(importing `unittest` costs as much as importing everything
else in big combined).  big's own test suite now runs on it.

(Why write my own?  This style makes it easy to hoist your test
functions out of the unit test suite and into a temporary file
to test in isolation.)


#### big.snip

[`big.snip`](#bigsnip) implements "snippets", little clippable
regions of course.  The idea is, you make little bits of your
source code easy for other projects to borrow without having to
depend on your whole project.  You mark the borrowable sections
of your file by bracketing it with "scissors" marker lines
(`# --8<-- start NAME --8<--` / `# --8<-- end NAME --8<--`).
Snippets also support "requirements", other snippets from the same
file that your snippet needs in order to work; these get automatically
pulled along when you snip.  

**big** itself publishes snippets from *big.text* and *big.itertools*,
see the new
[**Borrowable snippets**](#borrowable-snippets) section.

The module provides three functions, making it easy to manage snippets:

  * [`extract_snippets`](#extract_snippetss-names-comment)
    pulls oe or more snippets out of the source text, along with their
    requirements.

  * [`apply_snippets`](#apply_snippetss-snippets-comment)
    applies some already-snipped-out snippets to a destination text,
    like a patch.

  * [`sync_snippets`](#sync_snippetssource-destination-filternone--comment)
    synchronizes the snippets used in the destination with the possibly-fresher
    ones in the source.

The `big.snip` submodule also has a built-in command-line tool
to manage snippets; run it with `python3 -m big.snip`.

### New features

* [`format_definition_list`](#format_definition_listpairs-margin79--definition_left_columnnone-definition_relative_tabstrue-indent---spacer---tab_width8-term_relative_tabstrue)
  is a ew function in *big.text*.
  It renders the classic two-column help-table shape: terms on the
  left, definitions wrapped and aligned in a computed column on
  the right.  It's built on top of big's classic word-wrap trio
  (`split_text_with_code`, `word_wrap`, and `merge_columns`).

* `parse_template_string` has two new features--or, three, depending
  on how you count them.

  * Its existing whitespace eater `{>}` has grown two
    siblings: alongside `{>}` (which eats all whitespace *after*
    itself) there's now `{<}` (eats all whitespace *before* itself)
    and `{<>}` (eats in both directions).  All three live under the
    existing `parse_whitespace_eater` flag, and
    `eval_template_string` inherits them automatically.

  * `parse_template_string` interpolations now support a *format
    specification*, analogous to an f-string's: the text after a
    top-level `:`--`{{ expression | filter : format }}`--lands
    verbatim in the new `Interpolation.format` attribute (`None`
    when there's no colon).  Only a *top-level* colon counts:
    colons nested in brackets or quotes still belong to the
    expression or filter they're inside, so slices, dict displays,
    and string literals are unaffected.  `eval_template_string`
    applies it exactly like an f-string--`format(value, spec)`--so
    `{{x:>10}}` right-aligns in ten columns, filters and all.

* 🤖 **`python_delimiters` now walks in through the front door.**
  Since its introduction in 0.12.5, `python_delimiters` was a bit
  of a hack, because the `Delimiter` API couldn't express f-strings.
  So, if you passed `python_delimiters` in to `split_delimiters`,
  it had a hard-coded hack: it recognized the value and swapped in
  a secret internal grammar, hand-patched by a page of state-machine
  surgery.  0.14 makes
  [`Delimiter`](#delimiterclose--escape-multilinetrue-quotingfalse-nestednone-literal-changenone)
  expressive enough, the surgery is unnecessary (and removed!), and
  `python_delimiters` is now ordinary data--copy it, modify the copy,
  and your variant grammar keeps all of Python's semantics.

  What `Delimiter` grew:
    * `close` accepts a tuple of alternatives, any one of which
      closes the delimiter (a line comment ends at `'\n'` *or*
      `'\r'`).
    * `nested=` names delimiters that are live *inside* this
      one--for a quoting delimiter, the exceptions to the quoting
      (an f-string quotes, except `'{'` opens an interpolation).
    * `literal=` names tokens that are plain text inside this
      one, overriding any collision (`'{{'` inside an f-string
      body is a literal brace, not two interpolations).
    * `change=` names tokens that *change* what the inside of the
      current delimiter means without pushing a new delimiter--the
      close stays, and a change target must share it.  (The `':'`
      and `'!'` inside an f-string interpolation; the token
      appears in the `change` field `split_delimiters` yields.
      The output side has carried that field since 0.12.5--the
      input side finally has a spelling for it.)
    * `nested`, `literal`, and `change` are also *assignable*, so
      grammars with reference cycles can be built and then closed
      by assignment--until the first time a `Delimiter` is used
      in a compiled grammar, which freezes it (modify a `copy()`
      instead).  Equality is deep and cycle-safe.

* 🤖 A new member of the `multi-` family:
  [`multireplace`](#multireplaces-replacements-count-1--reversefalse)
  is `str.replace` with multiple replacement strings, applied in a
  single pass--text that has already been replaced is never itself
  examined for further replacements, so
  `multireplace('ab', {'a': 'b', 'b': 'a'})` returns `'ba'`, where
  chained `str.replace` calls would return `'aa'`.  Like its
  siblings it's greedy (the longest matching key wins), supports
  `str` and `bytes`, and takes `count` and `reverse`.  (Built on
  `multisplit(keep=True)`, naturally.)  It supports `big.string`
  too: a `big.string` input is reassembled with `string.cat`, so
  every unchanged segment keeps its file, line, and column--also
  available as the method `string.multireplace`.  Suggested and
  designed by Claude--and it was almost right the first time!

* 🤖 And an old member of the `multi-` family comes out of hiding:
  [`toy_multisplit`](#toy_multisplits-separators), the tiny,
  no-options multisplit the test suite has always used to validate
  `multisplit`, is now exported.  It returns exactly
  `list(multisplit(s, separators, keep=True, separate=True))`--
  the canonical 2-tuple form--and nothing else: no `keep`, no
  `maxsplit`, no `reverse`, no `strip`.  Its virtue is smallness:
  one dependency-free function, fast to start (nothing to
  precompile), and easy to embed in another project--it's also
  published as a snippet, `big toy_multisplit`.

* 🤖 New in `big.file`:
  [`atomic_write`](#atomic_writepath-modew--encodingnone-errorsnone-newlinenone)
  is a context manager that writes a file atomically.  Supports writing
  a new file, but also appending and updating (expensive, as it has to
  make a copy of the old file first).  If everything goes right,
  users either see the old file or the new file, never a file in an
  in-between state.  If anything goes wrong, the original file is
  left untouched.  Suggested and designed by Claude--and it was perfect
  the first time!

* 🤖 New in `big.time`:
  [`duration_human`](#duration_humant--longtrue-want_microsecondsnone)
  formats an elapsed time--an int or float number of seconds, or
  a `datetime.timedelta`--as a human-readable string.  The long
  format reads like prose, with Oxford comma rules:
  `duration_human(90061)` returns
  `'1 day, 1 hour, 1 minute, and 1 second'`, and
  `duration_human(90061, long=False)` returns
  `'1d 1h 1m 1s'`.  Sub-second precision is controlled by
  `want_microseconds`: `True` renders microseconds, `False`
  rounds to whole seconds, and the default, `None`, decides for
  itself--microseconds while the total duration is under a
  minute, whole seconds once it isn't.  The natural companion to
  `timestamp_human`, and to `Log`, which is all about elapsed
  time.  Its helper is exported too:
  [`pluralize`](#pluralizei-singular-pluralnone)
  in `big.builtin` counts things with the correct English
  grammatical number--`pluralize(3, 'apple')` returns
  `'3 apples'`, with an optional third argument for irregular
  plurals.

* Also in `big.template`:
    a behavior change in
    [`Formatter`](#formattertemplate-mapnone--relaxedfalse-stretchtrue-width79-kwargs):
    when a line with starred interpolations *overflows* the width, the
    starred interpolations and everything after them are now omitted
    (previously they collapsed to zero width and any trailing template
    text was glued onto the overflowing content).  A line that fits
    exactly still renders in full.  And
    [`Formatter`](#formattertemplate-mapnone--relaxedfalse-stretchtrue-width79-kwargs)
    gained a `relaxed=` parameter (a template with no `{message}` lines
    may discard a message instead of raising).  And in `big.itertools`:
    [`iterator_filter`](#iterator_filteriterator--stop_at_valueundefined-stop_at_innone-stop_at_predicatenone-stop_at_countnone-reject_valueundefined-reject_innone-reject_predicatenone-only_valueundefined-only_innone-only_predicatenone-call_everynone)
    gained `call_every=`, calling a callable after every N values
    yielded--fired on the consumer's next request, without waiting for
    the wrapped iterator to produce anything, and including a final call
    when the total is an exact multiple of N.

* Three changes in the word-wrap "trio" (`split_text_with_code`,
  `word_wrap`, and `merge_columns`):

    * 🤖 The text trio now supports tabs intelligently.  The core idea: a tab
      stops being pre-rendered whitespace and becomes a deferred
      column-advance, resolved at final rendering, when the true
      column is known--and columns are 1-based, like every text
      editor, so tab stops sit at columns 9, 17, 25...  In text,
      [`split_text_with_code`](#split_text_with_codes--code_indent4-tab_width8)
      emits each tab as its own `'\t'` word (a behavior change: a tab
      in text used to be a plain word separator), and code lines keep
      their tabs verbatim;
      [`wrap_words`](#wrap_wordswords-margin79--code_indentnone-indent-left_column1-tab_width8-two_spacestrue-rawnone)
      renders both as spaces at the columns where they actually land,
      guided by the new `left_column` parameter (the 1-based "virtual
      left column" for output you'll place somewhere other than the
      left page edge).  The `convert_tabs_to_spaces` parameter of
      `split_text_with_code` is gone--both of its modes are worse
      than the new mechanism--and so is `allow_code`, which was
      redundant: `code_indent` (now strictly an int) already says it,
      with 0 meaning "no code lines".  `big.string` got the same
      religion, opt-in: the new `string.detab` method expands
      each tab according to its own origin's coordinates (the same
      arithmetic `where` uses) and returns a `big.string`--the
      characters around the synthesized spaces keep their
      provenance--while the shadowed `string.expandtabs` deliberately
      keeps `str`'s exact context-free behavior, because a `str`
      method on a drop-in `str` replacement must never produce
      different text than `str` would.  The positional expander is
      exported as
      [`expand_tabs`](#expand_tabss--column1-first_column1-tab_width8):
      like `str.expandtabs`, but it takes the 1-based `column` the
      string starts at.
      [`format_definition_list`](#format_definition_listpairs-margin79--definition_left_columnnone-definition_relative_tabstrue-indent---spacer---tab_width8-term_relative_tabstrue)
      grew `term_relative_tabs` and `definition_relative_tabs`
      (default True: terms and definitions lay out in their author's
      own coordinates and shift rigidly into place, preserving the
      author's alignment; False lands their tabs on the page's
      stops), plus `definition_left_column`, which lets fussy users
      name the exact column where definitions start.  And a
      [`merge_columns`](#merge_columnscolumns-column_separator--overflow_strategyoverflowstrategyraise-overflow_before0-overflow_after0-tab_width8-rawnone)
      column tuple takes an optional fourth member, `relative_tabs`,
      with the same meaning and the same default.

    * [`wrap_words`](#wrap_wordswords-margin79--code_indentnone-indent-left_column1-tab_width8-two_spacestrue-rawnone)
      learned to indent 🤖.  The new `indent` parameter prefixes the
      wrapped lines: pass a single string for every line, or a list
      or tuple--the first line gets the first indent, the last one
      repeats when they run out, and a paragraph break resets the
      sequence.  (So `('usage: ', '       ')` renders a usage line
      with a hanging indent in one call.)  The new `code_indent`
      parameter gives code lines--lines that start with whitespace--
      their own indent sequence; by default they just consume `indent`
      like any other line, and `code_indent=''` strips them of
      indenting entirely.  Blank lines between paragraphs are never
      indented, and linebreak characters in an indent are a
      `ValueError`.  Indents count against `margin`, and tabs in an
      indent are expanded using the new `tab_width` parameter.

* New in *big.builtins:* `literal_eval`.  A wrapper around
    `ast.literal_eval` that
    preserves [`big.string`](#the-big-string) provenance.  It joins
    `string.compile` and `string.generate_tokens` as the third
    "big.string wrapper for a C module that loses provenance"—but unlike
    `re` and `tokenize`, which merely *locate* substrings, `literal_eval`
    *transforms* its input, so it preserves provenance on a graduated
    best-effort basis: a literal with no escape sequences decodes to a
    true slice of the source (`where` and `context` both work); a
    literal with escapes decodes to a spliced string where every
    character still reports a true line and column (a decoded escape
    reports the position of its escape sequence); an escape-free
    literal followed by trailing text `ast.literal_eval` tolerates (a
    comment, say) is rescued by reparsing the source with big's own
    `split_quoted_strings`--if the quoted contents are exactly the
    decoded value, that's a true slice, and the comparison is the
    proof; and anything that can't be honestly mapped back onto the
    source (implicit string concatenation, an escaped literal with a
    trailing comment) decodes to a plain `str`--per big.string's
    standing policy, failing loudly beats reporting positions that are
    confidently wrong.  In every case the decoded value is
    character-for-character identical to `ast.literal_eval`'s result.

    Available as `big.literal_eval(s)` and as the method
    `string.literal_eval()`.


### Bugs squashed

* 🤖 `merge_columns` validated its arguments with `assert`, and
  asserts vanish under `python -O`: there,
  `OverflowStrategy.INVALID`--a real, exported enum member--
  silently behaved as `INTRUDE_ALL`, and calling with zero columns
  gave a bare IndexError.  Both guards are now real ValueErrors,
  under any interpreter.  (The test suite runs these cases under
  `-O` semantics too.)

* 🤖 `strip_indents` mishandled blank-line linebreak preservation
  three different ways: a line that was 100% linebreak characters
  (a bare `'\n'`--the most common blank line there is) lost its
  linebreak entirely, thanks to an off-by-one in the backwards
  scan; bytes lines *never* preserved linebreaks (iterating a
  bytes yields ints, which were never found in a set of bytes
  strings); and the `linebreaks` parameter's default--the *str*
  linebreaks--was never swapped for `bytes_linebreaks` when the
  lines were bytes (the same dance `strip_line_comments` already
  did).  All three fixed; the scan now walks one-character slices,
  which is type-agnostic and counts a tally instead of an index.

* 🤖 `decode_python_script` now implements PEP 263 exactly as
  CPython's `tokenize.detect_encoding` does.  It used to honor a
  magic coding comment on line *three* (PEP 263 permits only the
  first two lines), used the *last* comment when lines 1 and 2
  both had one (CPython uses the first), and consulted line 2
  even when line 1 was real code (CPython only reads line 2 when
  line 1 is blank or a comment).  All three rules now match
  tokenize, verified by contrast-testing against it.  Also, the
  BOM-vs-magic-comment agreement check now normalizes both names
  through `codecs.lookup`, so every spelling of the BOM's encoding
  agrees (`utf8`, `UTF_8`, `utf-8`)--here big is deliberately
  *more* correct than tokenize, whose alias handling is a string
  prefix hack that rejects `utf8`--and an endianness-unqualified
  comment (`utf-16`) agrees with an endian BOM (`utf-16-le`),
  since supplying the endianness is the BOM's job.

* [`split_text_with_code`](#split_text_with_codes--code_indent4-tab_width8)
  was rewritten 🤖 as a straightforward line scanner (it was a
  character-at-a-time state machine).  Same behavior, much less
  machinery--and it fixes a real bug: a code paragraph followed by a
  text paragraph followed by another code paragraph used to either
  crash with `AssertionError` or pollute the output with stray
  linebreak words, depending on the blank lines around the text.

* 🤖 In `split_delimiters`, a token that *starts with* a valid open
  delimiter raised `SyntaxError` inside non-quoting delimiters
  instead of opening it.  With delimiters `'x'`&rarr;`'y'` and
  `'a'`&rarr;`'xz'`, splitting `'qxzy'` greedily tokenizes `'xz'`
  (it's `'a'`'s close) and then declared it illegal--even though
  `'x'` opens a delimiter right there.  Quoting delimiters have
  always handled exactly this collision with a
  truncate-and-resplit fixup; the fixup is now applied uniformly,
  for every state and every meaningful token.  (The machinery
  that does this, `_resolve_foreign_tokens`, replaces both the
  old per-delimiter fixups and a page of the f-string surgery's
  hand-patching--a first installment on making `python_delimiters`
  expressible through the front door of the `Delimiter` API.)

* Speaking of `split_delimiters`, there were several correctness
  fixes to `python_delimiters`, all 🤖:

  * `python_delimiters`' documented
    no-linebreaks-inside-single-quoted-strings rule was only
    half-enforced: `'\r'` inside a single-quoted string raised
    `SyntaxError`, but `'\n'` was silently flushed--an unterminated
    single-quoted string would quietly swallow the rest of the
    script.  (The f-string surgery blanketed a `'\n'`-means-nothing
    rule into *every* string state, clobbering the single-line
    check the grammar had correctly installed.)  The same asymmetry
    existed inside f-string format specs, in the other direction:
    the spec state is shared by single- and triple-quoted
    f-strings, so it permits linebreaks--but only `'\n'` was made
    legal, so a `'\r'` in a format spec raised.  Both directions
    are now symmetric: linebreaks in single-quoted strings raise,
    linebreaks in format specs don't.

  * `python_delimiters` now agrees with CPython's tokenizer about
    *exotic* linebreak characters.  Python only recognizes `'\n'`
    and `'\r'` as line boundaries; the other characters big defines
    as linebreaks--vertical tab, form feed, `'\x85'`, `' '`,
    and friends--are plain text inside Python's strings and
    comments, and `python_delimiters` used to reject them there
    (`multiline=False` forbade *every* big linebreak).  The grammar
    now declares them `literal` tokens of the single-line string
    and comment delimiters: they're still linebreaks by big's
    definition, this grammar just declares them literal text where
    Python does.  (A literal `'\n'` or `'\r'` in a single-quoted
    string still raises, exactly like real Python.)

  * `python_delimiters` no longer misparses `!=` inside an f-string
    `{`interpolation`}`.  `f'{a != b}'` used to report a `'!'`
    conversion field and treat `= b` as its text; but that `!=` is
    the not-equals operator.  Real Python's rule is "a conversion
    is `'!'` not *followed* by `'='`"--and declaring `'!='` a
    `literal` token of the interpolation delimiter implements
    exactly that rule, because tokenization is greedy.  (A real
    conversion after an expression containing `!=` still works:
    `f'{a != b!r}'` parses both correctly.)  This bug dates to
    0.12.5; it became a one-line fix when `python_delimiters`
    moved to the front door.

* 🤖 `split_quoted_strings`' `escape` didn't protect
  `multiline_quotes`: an escaped multiline delimiter closed the
  string anyway.  Nobody noticed because the natural multiline
  quotes, `'''` and `"""`, were shielded *by accident*--the `'"'`
  in `quotes` contributed a `\"` separator that happened to cover
  `\"""` too; a multiline quote that doesn't share a first
  character with a regular quote (say, `<<<`) got no protection
  at all.  `escape` now works inside both `quotes` and
  `multiline_quotes`, with its semantics pinned down and
  documented: it shields exactly one following character, like
  backslash in Python, so `\"""` inside a `"""` string is an
  escaped quote followed by two live quotes and doesn't close
  the string.

* 🤖 `split_title_case` silently dropped a single-character final
  word: `'WhenIWasA'` split into `['When', 'I', 'Was']`, and a
  one-character string split into nothing at all.  The final-flush
  guard compared against the index of the last character seen
  rather than the length of the string.  Joining the split now
  always reconstructs the input, verified exhaustively.

* Multiple updates to `grep` and `fgrep`, all 🤖:

  * `fgrep` and `grep` now split lines according to big's own
    definition of linebreaks (see `linebreaks` and `bytes_linebreaks`
    in `big.text`)--which is to say, `splitlines`.  In binary mode
    that fixes Windows (`\r\n`) and old-Mac (`\r`) files: matched
    lines no longer carry a stray trailing `\r`.  In text mode, `\v`,
    `\f`, `\u2028` and friends now count as linebreaks, matching big's
    worldview.  In both modes, a file ending with a linebreak no
    longer yields a phantom empty final "line".
  
  * Also,
    `fgrep(case_insensitive=True)` now compares with `str.casefold`
    rather than `str.lower`--the correct Unicode case-insensitive
    comparison, so e.g. `'STRASSE'` matches `'straße'`.
  
  * 🤖 And `grep` grew a `case_insensitive` parameter, for symmetry
    with `fgrep`.  It's tri-state: `None` (the default) leaves the
    pattern's flags untouched, true forces `re.IGNORECASE`, and
    false forces no `re.IGNORECASE`.  If you passed in a
    `re.Pattern`, and pass in something besides `None` to
    `case_insensitive`, `grep` will recompile your pattern to honor
    the flag.

* Lots of improvements and fixes to bound inner classes, all 🤖:

  * How a bound inner class finds the bound versions of its base
    classes has been redesigned.  Resolution is now keyed on class
    *identity*, end to end--names are never consulted.  Previously the
    first resort was `getattr(outer, base.__name__)`, which worked
    right up until two classes shared a name.  What this fixes,
    concretely:
    * A bound inner class can now inherit from a *same-named* bound
      inner class of an ancestor outer class--`class MyApp(BaseApp)`
      defining `class Config(BaseApp.Config)`--with full bound-MRO
      chaining: call `super().__init__()` (or `super().__new__(cls)`)
      and the outer instance is passed along automatically.  This
      never worked before.
    * Inheriting from another *instance's* bound inner class--
      `class Anything(o1.Inner)`--used to work only if your subclass
      happened to share the base's name; under any other name it
      raised `RuntimeError`.  The spelling of your class names is no
      longer load-bearing.  (The base injects its own outer, `o1`--
      that's the point of the pattern.)
    * A base that merely *shared a name* with another inner class
      could send binding into infinite recursion (`RecursionError`),
      or silently bind an unrelated class as a side effect.  That's
      now structurally impossible: identity resolution only ever walks
      the inheritance DAG, which has no cycles.
    * A decorated base whose descriptor isn't anywhere on the outer
      class's MRO--a genuine configuration error--now always raises a
      helpful `RuntimeError`; one same-name spelling of this mistake
      used to bind silently with the wrong lineage.

  A happy side effect: plain (undecorated) base classes--including
  `object`, which is to say including everybody's--are now recognized
  instantly and skip resolution entirely, making binding a little
  faster across the board.  And **one interface change:** if you
  worked around namesake chaining by passing the outer instance
  explicitly--`super().__init__(outer, ...)`--remove that argument;
  the parent receives it automatically now.  (big.log's
  `TextFormatter.State` did exactly this, and has been updated.)

  * Bound inner classes now hold a **strong** reference to their
    outer instance--exactly like a bound method holds `__self__`.
    Previously the reference was weak, and the innocent-looking
    one-liner `Outer().Inner()` was a trap: the temporary `Outer()`
    could be garbage-collected between resolving `.Inner` and
    *calling* it, so whether your code worked depended on when the
    garbage collector last ran.  (This was field-diagnosed as a
    weeks-long 1-in-115 flaky test in a library built on
    BoundInnerClass; an unrelated change shifted it to 1-in-4,
    thankfully!  A correctness
    property that depends on collector timing is the worst kind.)
    The syntax borrows bound methods' look; now it borrows their
    lifetime guarantee too.
  
    This deliberately reverses a 0.13 decision, which traded the
    reference cycle for the weakref; turns out, the flaky behavior
    just isn't worth it.

    Consequences: a bound class--or any
    instance of one, via its class--keeps its outer alive; the outer
    → cache → bound class → outer cycle is reclaimed by the cycle
    collector rather than by reference counting; `bound_to()` never
    returns None for a bound class; and the transient dead-outer
    `ReferenceError` (introduced earlier in 0.14) is gone, because
    the condition it detected is now unrepresentable.
  
  * Copying an outer instance no longer breaks its bound inner classes.
    `BoundInnerClass` caches bound classes on the outer instance, and
    that cache didn't cooperate with duplication: `copy.copy(o)` shared
    it, so the copy's inner classes were silently bound to the
    *original*; `copy.deepcopy(o)` crashed on the `threading.Lock`
    inside the cache; and `pickle.dumps(o)` crashed trying to pickle a
    dynamically-created bound class.  All three, mind you, only if
    something had already accessed `o.Inner`--whether your object could
    be duplicated depended on what had merely *looked* at it.  Now the
    cache duplicates as a fresh empty cache under copy, deepcopy, and
    pickle; and--belt and suspenders--every cache remembers which
    instance it belongs to (by weak reference) and is validated on
    every access, so a cache transplanted onto the wrong instance by
    *any* mechanism (say, a user-defined `__deepcopy__` that naively
    shares `__dict__`) is detected and replaced on first use.  However
    it was duplicated, a duplicated outer instance simply re-binds its
    inner classes lazily, exactly like a fresh instance.  (Also, the
    error message you get when an outer class's `__slots__` won't
    accommodate the cache now mentions *both* requirements: the cache
    slot, and weak-reference support.)

  * `BoundInnerClass` now only binds an `__init__` the decorated class
    *itself* defines--exactly the rule it already followed for `__new__`.
    Previously an `__init__` inherited from a regular (non-BoundInnerClass) base
    class was wrapped as though the inner class had defined it, so the
    outer instance was passed to a method that never asked for it.
    If you were lucky, you got a baffling `TypeError`; if you were
    unlucky, the outer instance was silently misfiled into the base's
    first parameter.  (Inheriting `__init__` from a bound *parent*
    works exactly as before--the bound parent in the MRO injects
    `outer` itself, and always did.)

* Some fixes for `TopologicalSorter`, again all 🤖:

  * Every `TopologicalSorter` owns two internal views--the default
    view (backing the graph-level `ready`/`done`/`reset` convenience
    API) and the stock view (the pristine template that `view()`
    copies).  Both were ordinary `View` objects, reachable via
    `graph.views`--so a well-meaning "close all my views" sweep would
    close them, permanently crippling the graph with baffling errors
    blaming a view you never knew you had.  They're now instances of
    a separate internal view class whose `close()` refuses, with an
    error message naming the actual rule.  (That class and the public
    `View` are siblings--both deriving from a shared base--rather than
    one subclassing the other, so neither "is a" the other.  Views the
    graph hands *out* remain ordinary and closable--including the ones
    `view()` copies from the internal stock view.)
  
  * `TopologicalSorter`'s cycle *locator* (the depth-first-search that
    names the cycle's members for the `CycleError`, after Kahn's algorithm
    has detected that one exists) had no "finished" set--the classic third
    DFS color.  Acyclic diamond-shaped regions were therefore
    re-explored once per distinct path through them, which is
    exponential; a 79-node diamond-ladder graph took ~40 seconds to
    report its little 2-cycle.  Now fully-explored nodes are never
    descended into again, the locator is linear, and that same graph
    reports its cycle in well under a millisecond.  Only the
    already-have-a-cycle path was affected--acyclic graphs never ran
    the DFS at all.
  
  * `TopologicalSorter`: passing the same node to `done()` twice *in
    one call*--`view.done('a', 'a')`--marked it done twice, which
    double-decremented its successors' predecessor counts.  On a
    diamond graph (`c` depends on `a` and `b`), `done('a', 'a')` made
    `c` come ready while `b` was still outstanding: an ordering
    violation, the one thing a topological sorter is sworn to prevent.
    (Duplicates across *separate* calls were always caught.)  A
    duplicate node in a single `done()` call is now a `ValueError`,
    matching the existing errors for unknown and un-yielded nodes.
    And `done()` now validates all its arguments before mutating
    anything, so a rejected call--this error or the existing ones--
    leaves the view exactly as it was.
  
  * `TopologicalSorter.copy()` also failed to copy the `dirty` flag--
    the lazy "should we check for cycles?" bit.  Since the cycle
    detector trusts a clean flag as *proof* of acyclicity, a copy of a
    graph currently containing a cycle inherited the cycle but not the
    suspicion: the original's `ready()` raised `CycleError`, while the
    clone's returned an empty tuple with a clear conscience--turning
    the standard `while ts:` consumer loop into a silent infinite
    loop.  One line: the flag travels with the copy now.
  
  * `TopologicalSorter.copy()` cross-wired the view registries of the
    original and the clone.  A graph notifies its views about every
    mutation via its `views` list--but the clone's copied views were
    accidentally registered on the *original* graph, while two
    orphaned placeholder views sat registered on the clone.  So after
    a `copy()`, adding a node to the clone was invisible to every view
    the clone handed out (a consumer loop would spin forever waiting
    for the missing node), and adding a node to the *original* leaked
    into the clone's views--`clone.ready()` would happily yield a node
    that wasn't in the clone's graph at all.  In short: a copied graph
    only worked if you never mutated either graph again, which is
    precisely when you don't need a copy.  The clone's views are now
    constructed against the clone, which registers them correctly from
    birth.

* Some small fixes for `linked_list`, both 🤖:

   * `linked_list` indexing didn't ignore special nodes like it should.
     This design is `linked_list`'s signature move--removing a node an
     iterator points at demotes it to a hidden "special" node instead of
     unlinking it, so iterators never dangle--and every traversal
     must skip those special nodes.  Two sites didn't: the primitive
     under `t[i]` (and `insert`/`pop`/`del t[i]`), and
     `linked_list.index()` both didn't properly ignore special nodes.
     Special nodes are special enough to break the rules--but we must
     be consistent!

   * 🤖 linked_list iterators' `next(default=...)` and
     `previous(default=...)` tested their internal sentinel with `==`,
     so a default value with a promiscuous `__eq__`
     (`unittest.mock.ANY` is the everyday example) was mistaken for
     "no default supplied"--an exhausted iterator raised `StopIteration`
     instead of returning the caller's explicit default.  (A hostile
     `__eq__`, like a numpy array's, crashed instead.)  Switched to `is`,
     just like `iterator_context` did, and for the same reason.

* 🤖 The `undefined` singleton (`big.itertools.undefined`) didn't
  survive pickling or deepcopy: those reconstruct objects via
  `__new__`, bypassing the singleton guard in `__init__`, so a
  round-trip minted an impostor `Undefined` instance--identical
  repr, different identity--and every `is undefined` test
  downstream silently failed.  `Undefined.__reduce__` now routes
  reconstruction back to the one true `undefined`, which covers
  pickle, `copy.copy`, and `copy.deepcopy` in a single stroke.

* 🤖 `iterator_filter`'s `stop_at_count=N` consumed at least N+1 values
  from the wrapped iterator: the quota check ran just before yielding
  the *next* accepted value, so after the quota filled, the source
  got pulled again (and repeatedly, if rejection rules kept
  discarding what it produced) just to discover it was time to stop.
  Iterators aren't only value streams--pulling one can read a
  socket or consume an item some other consumer will never see.
  The quota now stops the filter on the consumer's next resume,
  *before* the source is touched again: exactly N accepted values
  are consumed.

* 🤖 `iterator_context` silently dropped its final value if that value
  had a promiscuous `__eq__`.  The end-of-iteration check compared
  the lookahead variable against an internal sentinel with `!=`,
  which asks the *value's* opinion--so anything that claims to equal
  everything (`unittest.mock.ANY` is the everyday example) claimed
  to be the sentinel, and the last item of the iteration silently
  vanished.  (A *hostile* `__eq__`, like a numpy array's, crashed
  instead.)  Losing specifically the final value is the rottenest
  failure mode--it's the one a spot-check misses.  The comparison is
  by identity now, as sentinel comparisons must always be.  (The
  local sentinel was also renamed: it was called `undefined`,
  shadowing big.itertools' *exported* `undefined` singleton, which
  is an unrelated object.)

* 🤖 `Heap` negative indexing returned wrong values for `heap[-3]`
  through `heap[-9]`.  The small-negative fast path uses `nlargest`,
  which returns values in *descending* order--a fact the very same
  method compensates for two branches earlier--and then indexed that
  descending list with the original negative index.  Work the algebra
  and it returned the second-largest value for every index in the
  branch (and something even wronger when the index ran off the end).
  `heap[-1]` and `heap[-2]` were accidentally correct, which is
  exactly how this survived: shallow testing checks -1 and -2, both
  look fine, ship it.  Fixed--the (-i)th-largest value is simply the
  *last* element of `nlargest(-i)`--and the test suite now sweeps
  every valid index, positive and negative, across sizes spanning
  every fast path and the sorted fallback.  Related: `Heap()[-1]` on
  an empty heap raised `ValueError` (from `max()`) where a list--and
  every other empty-heap index--raises `IndexError`; it conforms now.
  And `Heap.__eq__` now returns `NotImplemented` for non-Heap
  operands instead of `False`, so foreign types that know how to
  compare against a `Heap` get their reflected `__eq__` consulted,
  per protocol.  (Ordinary comparisons are unchanged.)

* 🤖 `StateManager`'s first-exception-wins rule had a hole: if an
  observer raised an exception (remembered, to be re-raised after
  the transition completes) and then the new state's `on_enter`
  *also* raised, the on_enter exception propagated and the
  observer's exception--the first one--was silently lost, not
  even chained.  Now the first exception always wins: the
  observer's exception is re-raised with the on_enter exception
  chained to it as its `__cause__`, so both tracebacks print and
  nothing is lost.

* 🤖 `ThreadSafeRegulator` had a lost-wakeup race.  `Scheduler`
  releases the regulator's lock *before* calling `sleep`--correctly,
  you should never sleep holding a lock--so there's a window where
  a thread has committed to sleeping but isn't actually waiting
  yet.  The old `wake` was a set-then-clear *pulse* on a
  `threading.Event`; a wake landing in that window evaporated,
  the consumer slept its full original interval, and an event
  scheduled to occur earlier was delivered late--the exact
  `sched.scheduler` bug `Scheduler` exists to fix.
  `ThreadSafeRegulator` is rebuilt on the classic "double acquire"
  trick: a "blocker" lock, held by default; `sleep` blocks trying
  to acquire it a second time (with the sleep interval as the
  timeout) and `wake` releases it.  Now `wake` is a level, not a
  pulse: a wake with no sleeper parks the blocker open, the next
  `sleep` returns immediately, and its acquire re-arms the blocker
  in the same atomic operation.  A wake can never be lost.
  (The `Regulator.wake` contract is now documented as "aborts at
  least one current call to `sleep`" rather than all of them--
  the woken thread re-reads the queue under the lock, which is
  all correctness requires.)

* 🤖 `Version(release=(1, 2), serial=3)` constructed happily, then
  `str()` blew an assert--a serial belongs to a pre-release, and
  the keyword path never checked it against the (defaulted)
  `'final'` release_level.  (Under `python -O` the assert vanished
  and it silently printed a *wrong* version, the serial simply
  evaporating.)  The constructor now rejects a nonzero serial with
  a final release_level, with a ValueError that says what to do
  instead.

* 🤖 Equal `Version` objects could hash differently, breaking set and
  dict membership: `__eq__` compares the normalized comparison
  tuple (where an unspecified epoch equals epoch 0), but `__hash__`
  hashed the raw attributes, where `None` and `0` differ.  So
  `Version("1.0") == Version("0!1.0")`, but a set could hold both.
  `__hash__` now hashes exactly what `__eq__` compares.

* 🤖 `Version` silently dropped a `dev` or `post` marker with no
  number: `Version("1.0.dev")` parsed *equal to* `Version("1.0")`,
  though PEP 440's implicit-number rule (quoted in big's own
  source!) says it means `1.0.dev0`--which sorts *before* `1.0`.
  Same for `"1.0.post"`.  Both now apply the implicit `0`; verified
  against `packaging.version.Version` on every affected form.
  (Pre-release markers always worked, by a lucky coincidence of the
  comparison tuple's None-substitution.)

* 🤖 `timestamp_human` didn't convert timezone-aware datetimes to the
  local timezone, despite its docstring's promise--only *naive*
  datetimes were converted; aware ones rendered in their own zone.
  Now every datetime goes through `astimezone`, which handles naive
  and aware alike.  The previously-undocumented `tzinfo` parameter
  (the timezone the timestamp is rendered in; None means local) is
  now documented.

* 🤖 `timestamp_3339Z` never included microseconds for float inputs,
  even though its docstring always promised them: the is-it-a-float
  check ran *after* the float had already been replaced with a
  datetime, so it never fired.  (Its twin, `timestamp_human`, always
  checked in the right order--the twins had drifted.)
  `timestamp_3339Z(1.5)` now returns
  `'1970-01-01T00:00:01.500000Z'`.

* 🤖 `safe_mkdir` and `safe_unlink` were defeated by broken symlinks:
  `os.path.isfile` follows symlinks, so a dangling symlink squatting
  on the name looked like "nothing there"--`safe_mkdir` went on to
  raise `FileExistsError` (despite its documented guarantee), and
  `safe_unlink` silently left the debris in place.  Now a symlink
  that doesn't lead to a directory--a symlink to a file, or a
  dangling one--counts as a file: it's unlinked (the symlink itself,
  never its target).  A symlink that leads to a directory is left
  alone by both functions.

* 🤖 `pushd` now captures the current directory when the `with` block
  is *entered*, not when the object is constructed--matching the
  shell builtin it's named after, which pushes the directory you're
  in right now.  Previously, constructing a `pushd` early and
  entering it later restored the construction-time directory on
  exit.  (For the idiomatic one-liner, `with big.pushd('x'):`,
  nothing changes--the two moments coincide.)  A pleasant side
  effect: a single `pushd` object is now reusable.

* 🤖 A starred interpolation whose value was the empty string
  (`Formatter('{x*}', {'x*': ''})`) constructed happily, then
  crashed at *format* time with a bare `ZeroDivisionError` from
  deep inside the fill arithmetic.  The emptiness could also
  arrive indirectly, via an object whose `__str__` returns `''`,
  or via a `format_map` per-call override.  An empty starred
  value now raises ValueError at construction (or at override
  time), naming the offending key--matching how protective the
  constructor already is about every other starred-interpolation
  rule.

* 🤖 `parse_template_string` silently yielded a phantom `Statement('')`
  when the template ended immediately after a `{%`--the entire
  find-the-`%}` scan, *including* its unterminated-statement error,
  was skipped when nothing followed the marker.  A trailing
  fat-fingered `{%` now raises SyntaxError ("unterminated statement",
  with the position) like every other unterminated construct, and a
  genuinely empty statement (`{%%}`) is still legal.

* 🤖 `parse_template_string`, on Python 3.11 and earlier, crashed
  with `IndexError` when an expression contained an unclosed open
  delimiter (`"{{ a( }}"`).  Old `tokenize` reports EOF-in-brackets
  with a `TokenError` positioned one line *past* the end of the
  text, and the caret-building error handler indexed that
  nonexistent line.  It now reports what it always should have:
  SyntaxError, "unterminated expression".  (The rewritten
  `tokenize` in 3.12+ doesn't raise there at all, so those
  versions were never affected.)

* 🤖 `get_int_or_float` now has an explicit purview: strings (`str`,
  `bytes`, `bytearray`) and things that are already `int` or `float`.
  It's a poor man's `ast.literal_eval`: if the string reads as an
  int you get the int, otherwise if it reads as a float you get the
  float.  Everything else--`Decimal`, `Fraction`, complex,
  kumquats--gets the documented "return the default" treatment.
  Previously it tried `int()` on *anything*, and `int()` *truncates*
  number-like objects rather than raising, so e.g.
  `get_int_or_float(Decimal('3.5'))` quietly returned `3`.  Also
  fixed: infinities and NaNs.  `get_int_or_float(float('inf'))`
  used to raise `OverflowError`, and `float('nan')` raised
  `ValueError`; now floats that `int()` can't stomach pass through
  unchanged, and the *strings* `"inf"` and `"nan"` convert to the
  floats `float()` says they are.

### Smaller fixes and polish

* 🤖 `import big.all` is roughly *twice* as fast (~39ms → ~19ms
  measured), via two rounds of deferral.  Round one: compiling the
  two `python_delimiters` grammars into their state machines
  (~12ms of runtime-assembled dict graphs over 158 tokens each)
  is deferred until the first
  `split_delimiters` call that actually uses one.  (The grammar
  *dicts* themselves are still built eagerly; they're small, and
  their contents are unchanged.)  Round two: five imports big paid
  for eagerly but rarely used are now deferred--`inspect` (~13ms!
  used only for signature computation; imported inside the three
  functions that need it), `ast` (only `literal_eval` uses it),
  and the optional packages `regex` and `packaging.version`
  (recognized via `sys.modules` at isinstance time, which is
  lossless--an instance of their types can only exist if somebody
  already imported them) and `dateutil.parser` (availability
  probed with `find_spec`, which doesn't execute the module; the
  real import happens at the first `parse_timestamp_3339Z` call).
  No behavior changes; the costs move from everyone's import to
  the first use by code that actually uses each feature.

* `str()` of a `big.string` that spans its entire origin--like a
  string freshly constructed from a slurped-in text file--now
  returns the origin's plain `str` directly, instead of copying
  the whole buffer.  Zero copies, effectively free.

  (Why?  So tokenizers built on `big.string`—which scan the raw span
  of a quoted string and let `literal_eval` do the unescaping—can hand
  out decoded *values* that still know their file, line, and column.  My
  **perky** file format is about to become its first public customer!)

* 🤖 The deprecated `lines` pipeline now *says so at runtime*: the
  `lines` constructor emits a `DeprecationWarning` (one warning
  covers the whole pipeline--every `lines_*` modifier consumes an
  iterator that started there), pointing at the new "Migrating
  from `lines` to `string`" section of this README.  Note that
  `warnings.warn` never halts anything; by default Python doesn't
  even display DeprecationWarnings outside `__main__`.

* 🤖 `int_to_words` said its cap of `10**75` was "one quadrillion
  vigintillion"; that's `10**78`.  The cap is unchanged and now
  correctly named: one *trillion* vigintillion.  (A function whose
  job is naming numbers should be able to name its own limit!)
  Also, passing a non-int now raises `TypeError`, not `ValueError`,
  matching the rest of big.

* 🤖 `int_to_words` also had two misspellings and a formatting leak.
  The misspellings: "twelveth" (it's "twelfth") and "qindecillion"
  (it's "quindecillion"); also "septdecillion" is now
  "septendecillion", the standard (and inflect's) name for `10**54`.
  The leak: the internal quantity table was column-aligned with
  spaces *inside* the string literals, so the shorter names
  rendered with their padding--`int_to_words(10**33)` returned
  `'one   decillion'`, three spaces, likewise nonillion, octillion,
  septillion, and sextillion.  The docstring's claim that flowery
  output is identical to `inflect.engine().number_to_words(i)` is
  now true at every magnitude inflect can handle (verified against
  inflect across 106 values); previously the test suite's numbers
  jumped from quintillions straight to ~`10**65`--past inflect's
  range--so the parity check never saw the broken middle.

  (You had ONE JOB, `int_to_words`!)

* `Pattern`'s wrong-type error
  message claimed "s must be str" while happily accepting bytes;
  it now says so, and Pattern and Pattern.Match--previously the
  only big exports with no docstrings at all--now have them.

* 🤖 `python_delimiters_version` now keeps the promise of its name.
  It used to map `'3.6'` through `'3.13'`--no `'3.14'`, despite
  big's t-string support--and every key mapped to the *same*
  object, whose contents depended on the running interpreter:
  ask for 3.8's grammar on a 3.14 interpreter and you got
  t-strings.  big now builds both grammars unconditionally
  (they're static data): `'3.6'`-`'3.13'` map to the t-free
  grammar, `'3.14'` maps to the t-aware one, and
  `python_delimiters` picks the right one for the running
  interpreter.  Bonus fix uncovered along the way: on 3.14
  interpreters, t-strings never got the f-string brace surgery
  (the check only recognized `f` prefixes), so `t'{name}'`
  parsed its braces as inert text; t-strings now get the same
  `{`interpolation`}`, `!conversion`, and `:format-spec`
  handling as f-strings.

* 🤖 `split_quoted_strings`' error for a linebreak inside a
  single-line quoted string literally said
  `unterminated quoted string, {s!r}`--the f-string prefix was
  missing, so the placeholder went to the user unfilled.  (The
  identical check at end-of-string always had its `f`.)  The
  message now shows the offending string.

* 🤖 `big.text.__all__` listed `split_delimiters` twice: the *internal*
  generator (whose docstring says right there that it's internal)
  wore an `@export` decorator alongside the public wrapper that
  rebinds the name.  Harmless to users--the module attribute always
  ended up as the public function--but `__all__` hygiene is hygiene.
  With this and the `big.scheduler` fix, big's export-hygiene test
  now runs with an *empty* grandfather list: any module that ever
  lists a name twice again fails the test suite on the spot.

* 🤖 Also, `strip_line_comments` now accepts its line comment markers
  as any iterable--sets and generators used to raise a bare
  `TypeError`, because validation indexed into the markers.

* 🤖 And a latent typo: the defensive branches that would add `\v` and
   `\f` to `bytes_linebreaks` (if Python's `bytes.splitlines` ever
  starts splitting on them) appended *str* literals to the bytes
  tuple.  Now they're bytes.  (The branches are dead code today,
  which is why nobody noticed.)

* 🤖 `linked_list.__eq__`/`__ne__` (and the iterator's `__eq__`) now
  return `NotImplemented` for types they don't understand, instead
  of a flat False/True--so reflected comparisons finally get their
  chance.  (The ordering methods always did this; the class was
  internally inconsistent about it.)  Also, big.string's
  provenance-and-mutation policy is now documented prominently:
  substring operations always return big.strings with true
  positions, but text-*changing* methods (lower, upper, casefold,
  format, ...) return plain str when the text changes--failing
  loudly beats approximate positions.

* 🤖 Reverse-iterator `extend` and `rextend` raised TypeError for
  generators (and any non-reversible iterable): they called
  `reversed()` directly on the argument, while every other extend
  in linked_list accepts any iterable.  Non-reversible iterables
  are materialized first now, and produce exactly the same result
  a list would.

* 🤖 `linked_list.pop` and `rpop` on an empty list now raise
  IndexError, matching `list.pop` and `deque.popleft`--they raised
  ValueError, so the try/except IndexError code that linked_list's
  "superset of list and deque" interface invites didn't work.
  (`popleft`, the deque-compatibility alias itself, raised the
  wrong exception for deque's most idiomatic failure case.)

* 🤖 `Heap`'s iterator wasn't itself iterable: it implemented `__next__`
  (plus a snapshot copy and modification detection!) but forgot the
  one-liner, `__iter__` returning self.  So `for x in heap` worked,
  but *holding* the iterator--`it = iter(heap); for x in it:`, or
  `zip(iter(heap), ...)`, or anything else that re-`iter()`s an
  iterator--raised `TypeError`.  Textbook line added.

* 🤖 `repr()` of an empty `Heap` raised `IndexError`--it interpolated
  `queue[0]` unguarded.  A broken repr's blast radius is always
  bigger than the method: an empty heap couldn't be printed, logged,
  interpolated, or inspected in a debugger--precisely the moments
  you're trying to *look* at the thing.  The empty repr now simply
  omits `first=`; and `first=` now shows the `repr` of the first
  element, so e.g. strings are quoted.

* 🤖 The `RuntimeError` raised when a `TopologicalSorter` view is
  incoherent with its graph interpolated a whole *set* of successor
  nodes into the message where a single node belonged.  Each
  conflicting edge now gets its own properly-formatted description.

* 🤖 `TopologicalSorter.static_order()` leaked a view on every call.
  Views stay registered on their graph until closed--and every
  `add()` and `remove()` notifies every registered view--so a
  long-lived graph that alternated mutation with `static_order()`
  got a little slower with every ordering it ever computed.  The
  view is now closed in a `finally`, which covers the fully-consumed
  case, the abandoned-generator case, *and* the `CycleError` case.

* 🤖 `Version.__lt__`'s incompatible-type error message was an
  f-string missing its `f`--it literally printed `'{type(other)}'`.
  Rather than just add the `f`, both `__lt__` and `__eq__` now
  return `NotImplemented` for types they don't understand, per the
  data model: Python raises the standard (correctly formatted!)
  TypeError for unhandled ordering, `==` against foreign types
  still evaluates False, and reflected comparisons finally get
  their chance.

* 🤖 `parse_template_string`'s SyntaxError messages now all put the
  position first, colon-separated (`line 1 column 21: unterminated
  statement`)--the compiler-error convention, and the one `big.snip`
  and the unterminated-comment message already used.  Previously
  statements, expressions, and quoted strings used the trailing
  "... at line 1 column 21" style, so the same parser spoke two
  dialects.

* 🤖 `TransitionError` now subclasses `RuntimeError` instead of
  `RecursionError`.  Both kinds of illegal transition are legal
  operations attempted at an illegal moment--`RuntimeError`'s
  beat--and only one of them was even recursion-shaped.  Worse,
  the old base meant `except RecursionError` handlers guarding
  against actual runaway recursion silently swallowed state-machine
  misuse.  Since `RecursionError` subclasses `RuntimeError`,
  every `except TransitionError` and `except RuntimeError` handler
  behaves exactly as before; only `except RecursionError` handlers
  change, and for them not catching `TransitionError` is the fix.

* 🤖 `big.scheduler.__all__` listed `Regulator`, `SingleThreadedRegulator`,
  `ThreadSafeRegulator`, and `Scheduler` twice: a hand-rolled `__all__`
  survived the module's conversion to `ModuleManager`, which *adopts*
  a pre-existing `__all__`--so every `@export` appended a name the
  hand list already had.  The stale hand-rolled list is gone;
  `__all__` is now purely `ModuleManager`-managed, and big's export
  hygiene test enforces that no module ever lists a name twice again.

* 🤖 A typo in `big.file` that, entirely by luck, was harmless: the
  compile-time probe for platform filename case-sensitivity (used
  for `search_path`'s `case_sensitive=None` default) compared
  `os.path.normcase('FOo')` against `os.path.norm`**`path`**`('foo')`.
  It should be `normcase` on both sides.  It computed the correct
  answer on every platform anyway, because `normpath('foo')` is
  `'foo'`, which is exactly what `normcase('foo')` returns
  everywhere.  Fixed so the incantation matches the intent--the
  same answer, honestly derived.

* 🤖 The descriptor `BoundInnerClass` leaves in the outer class's
  `__dict__` is a transparent proxy for the inner class.  It had
  forwarding properties for `__doc__` and `__module__`--which could
  never run.  Every class body implicitly defines `__doc__` (its
  docstring) and `__module__` in its class dict, and those
  plain-string entries shadowed the properties the decorator
  inherited from its proxy base class.  Upshot:
  `Outer.__dict__['Inner'].__doc__` returned `BoundInnerClass`'s own
  docstring--all sixty lines of it--instead of `Inner`'s, and
  `.__module__` claimed everything lived in `big.boundinnerclass`.
  (`help(Outer)` was always fine; pydoc reaches classes through
  `getattr`, which returns the real class.)  Now the proxy copies
  `__doc__` and `__module__` from the wrapped class into instance
  attributes, exactly as it already did for `__qualname__` and
  `__annotations__`, and no longer declares `__slots__`--instance
  attributes only win this particular staring contest if there's an
  instance `__dict__` for them to live in.  (An observable side
  effect: the proxy now has a `__dict__` of its own, so
  `Outer.__dict__['Inner'].__dict__` no longer forwards to the inner
  class's `__dict__`.)

* 🤖 `ModuleManager.export` now raises `ValueError` if you export a
  name that's already in `__all__`, and `ModuleManager.delete`
  likewise for a name already scheduled for deletion.  Both
  doubled-`__all__` bugs fixed in this release (`big.scheduler`'s
  stale hand-rolled `__all__`, `big.text`'s stray `@export` on an
  internal function) would have been caught at import time by this
  check--in *any* project that uses `ModuleManager`, not just big.
  If a redundant export/delete is intentional, the new
  keyword-only `force=True` flag permits it quietly, and
  `__all__` still only lists each name once.

* 🤖 Small fixes in `big.builtin`, all in error paths and
  hostile-input corners:

  * The `TypeError`s raised by `ModuleManager.export` and
    `ModuleManager.delete` were missing their f-string `f` prefix,
    so the message literally read `{o} isn't a string and doesn't
    have a __name__`.
  * `get_int` and `get_float` compared the caller's `default`
    against the internal sentinel with `!=`, which invites the
    default's `__eq__` to the party.  A default with vectorized
    equality (a numpy array, say) crashed instead of being
    returned.  Sentinels are compared by identity now, as is right
    and proper.
  * `ModuleManager`'s cleanup scanned the module's namespace for its
    own bound methods by running `==` against *every* global--same
    problem: one global with an exotic `__eq__` could blow up `mm()`
    at module cleanup.  The scan is now gated by type, so `==` only
    runs between actual bound methods.  (It can't simply use
    identity: bound method objects are created fresh on every
    attribute access, so `is` would never match your stored
    `export = mm.export` alias.)

* 🤖 Assorted small kindnesses:
  * `ClassRegistry` now supports attribute
    assignment and deletion (`registry.Name = cls` stores into the
    registry, matching how attribute *access* already read from it).
  * Using a `ClassRegistry` registry as a decorator without
    parentheses--`@registry` instead of `@registry()`--now raises a
    helpful `TypeError` instead of silently replacing your class with
    an internal function.
  * A `ModuleManager`'s cleanup now sweeps up only
    *itself* and its own bound methods--other `ModuleManager`
    instances in the same namespace are left alone, they can
    clean up after themselves.
  * `iterator_context`'s `ctx.length` and `ctx.countdown` now raise
    `AttributeError` when the iterator doesn't support `len()`--
    "undefined" now means the same thing for every ctx attribute, and
    `hasattr(ctx, 'length')` is a correct capability probe.  (They used
    to leak `TypeError` from `len()`.)
  * `translate_filename_to_exfat`/`_to_unix` now raise `TypeError` for
    non-string input, instead of claiming your integer was an empty
    filename.

</dd></dl>

## 0.13.4

*2026/07/02*

<dl><dd>

A bugfix release.  Comes with free regression tests!

* Fixed `PushbackIterator`: `__next__` had a bare `except:`, which caught
  *every* exception raised by the iterator it wraps--not just
  `StopIteration`.  If your iterator raised, say, `ValueError`,
  `PushbackIterator` would swallow the exception and simply claim
  to be exhausted, oops!  Now only `StopIteration` means exhausted;
  everything else propagates, as it should.
  * Also fixed two mistakes in the docstring: pushed values are yielded
    in *last*-in-first-out order (it said "first-in-first-out order,
    like a stack"--that's not even a stack!), and `__bool__` returns
    true if the iterator *isn't* exhausted.
* Fixed `wrap_words`: the `two_spaces` parameter was clobbered by a
  local variable, so `two_spaces=False` was silently ignored.
* Two fixes for `split_text_with_code`:
  * Unusual whitespace characters (`\r`, `\v`, `\f`, non-breaking
    space...) used as leading whitespace no longer raise
    `RuntimeError`.  They count as one column, and are preserved
    verbatim inside code lines.  (A non-breaking space can sneak into
    a docstring via copy-and-paste from a web page--that shouldn't
    crash your help system.)  I mean, nobody uses 'em--but now you can!
  * If the string ended with a code paragraph *without* a trailing
    linebreak, the final code line was simply lost.  Now it's lost
    in a more complicated manner!  Just kidding, it's fixed.
* Fixed `merge_columns`: an intermediate list of per-line-rstripped
  lines was carefully computed... and then never used.  Two
  user-visible consequences, both fixed: a line with trailing
  whitespace could fool the padding math and misalign every
  subsequent column, and `overflow_after` was silently ignored when
  the overflow was at the very end of a column.
* Fixed the computed signatures of `BoundInnerClass` classes whose
  `__new__` or `__init__` receive `outer` via `*args`--for example,
  the generic forwarding `def __init__(self, *args, **kwargs)`.
  The reported signature elided the `*args` as though it were the
  `outer` parameter; now `*args` correctly survives.
* Corrected the 0.13.3 release notes about the `BoundInnerClass`
  signature cache--two corrections, in opposite directions!  The cache
  is *safer* against races than advertised: the cache key is the pair
  of method objects themselves, and the bound class closes over those
  same objects, so a stale signature is impossible--the worst a race
  can do is make two threads redundantly compute the same signatures.
  However, the cache *can't* detect in-place mutation of a cached
  method--assigning to its `__signature__`, `__defaults__`,
  `__annotations__`, etc. after binding.  (*Replacing* the method is
  always detected.)  My sincere advice: don't mutate function
  signatures in place--if you must, do it early, before `BoundInnerClass`
  caches the signature.

</dd></dl>


## 0.13.3

*2026/06/10*

<dl><dd>

* A performance bump for `BoundInnerClass`!  Breaking news: computing
  the `inspect.signature` for `__new__` and `__init__` is *shockingly*
  expensive.  `BoundInnerClass` used to recompute them every time it
  bound a class, even though they almost never change.  It now caches
  the computed signatures for these two dunder methods in a private slot
  on its descriptor.  (Which means we don't modify your class, and also
  you won't see the cache unless you go hunting for it.)  The cache is
  verified safe every time; if you add / replace / delete either method,
  `BoundInnerClass` will notice and refresh the cache.  This verification
  is quick--recomputing the signatures is the slow part.

  The cache is naturally safe against races: the cache key is the pair
  of method objects themselves, and the bound class closes over those
  same objects, so a bound class's signature can never disagree with
  its behavior.  The worst a race can do is make two threads both
  recompute the same signatures, which is harmless.

  The one change the cache genuinely can't detect: *mutating* one of
  these methods in place, in a way that changes its signature--assigning
  to its `__signature__`, `__defaults__`, `__annotations__`, etc.--after
  the class has been bound.  The function's identity doesn't change, so
  the cache can't notice.  (*Replacing* the method is always detected.)
  My sincere advice: don't mutate function signatures in place--if you
  must, do it early, before `BoundInnerClass` caches the signature.
* Small fix for the test suite: `bigtestlib.preload_local_big` tries
  to find the root of your `big` directory by examining directories in a loop.
  If a directory fails, it tries that directory's parent.
  The bug: if it never found `big`, it would run forever--it would never
  notice that it had hit the root of your filesystem, so it'd keep trying
  the root directory, over and over, until the universe grew cold and dark.
  The fix: if it still hasn't found the `big` directory, and the directory
  it's examining is the same as that directory's parent,
  raise `FileNotFoundError`.

</dd></dl>


## 0.13.2

*2026/04/24*

<dl><dd>

* `BoundInnerClass` classes now support `__new__` as well as `__init__`!
  When calling `__new__`, `outer` is once again the second parameter,
  this time after `cls`.  A class can have both `__new__` and `__init__`,
  and it behaves just like normal Python--but with a secret extra parameter!
  BoundInnerClass also amends the bound signatures of `__new__`, `__init__`,
  and the class itself so they don't contain `outer`.
  * Touched up the `BoundInnerClass` docs and tutorial to reflect some new
    deeper understandings of how it works.
* Minor change to `linked_list`: renamed an internal attribute.
  `_lock_parameter` should have been named `_lock_argument`
  all along!  *slaps forehead*  This is purely an internal change
  and shouldn't have any user-visible effect.  (For those of you who
  don't understand the distinction: if you define `def foo(a): ...`
  then later call `foo(3)`, `a` is a *parameter* and `3` is an *argument.*
  A parameter is a thing that recieves an argument.)

</dd></dl>


## 0.13.1

*2026/03/23*

<dl><dd>

This is mostly a bugfix and polish release for 0.13, though I added
one new helper class in *big.template* and a few small APIs.

* `linked_list` got new APIs and a heap of bug fixes!  It's more correct
  than ever!
  * Added `move()` / `rmove()` to `linked_list`, `linked_list_iterator`, and
    `linked_list_reverse_iterator`.  Moves nodes internally inside a linked
    list--like a `cut` followed by a `splice`, but cheaper.
  * Breaking API change: `splice` used to allow you to pass in tail for `where`,
    and `rsplice` used to allow you to pass in head for `where`, and honestly
    its behavior was a little weird when you did.  Those values are no longer
    allowed.  The rule is: you can't ever add nodes before head or after tail;
    sadly, in 0.13, `splice` and `rsplice` got it wrong.
  * `reverse()` and `sort()` now move nodes rather than swapping values;
    this means iterators continue to point to the same value.  (What about
    special nodes?  `reverse` reverses those too, just like data nodes;
    `sort` groups special nodes with their *subsequent* data node, or tail.)
  * Fixed a number of iterator, locking, rotation, clearing, and cut/splice
    edge cases.
  * The "head" and "tail" nodes are now instances of special classes that
    disallow writing to some attributes.  This would have caught an obscure
    regression bug (which is also fixed) and should preclude similar bugs
    in the future.
* `string` got one new feature and some `str` compatibility improvements:
  * Added `string.context`: a property returning a `string_context`
    object.  `str(s.context)` produces a "context string", showing
    the entire line `s` was sliced from, and adding a second line below
    it with a line of carets (`"^^^"`) calling attention to `s` in context.
    This can make error messages even nicer!  The full `string_context`
    object contains the individual components, as well as the full
    context string for multi-line strings.  (`str(s.context)` only
    shows the first line of context for multi-line slices.)
  * Lots of little bugfixes: reverse-slice edge cases, `join([])`,
    signed `zfill()`, `removesuffix('')`, `partition('')` and
    `rpartition('')`, and `replace('', ...)`.
  * Added broader `__index__` support where `string` mirrors `str` APIs.
  * Improved support for stateless subclasses of `string`.  (If you want
    to subclass `string` *and* add new attributes, you'll probably have a
    rough time.  File a bug and maybe we can improve the interfaces for you.)
* Several quality-of-life improvements for the new `Log` class:
  * The log object no longer logs the start banner or end banner
    unless some operation actually logs some (formatted) output.
    If you never log a message, you don't get spurious (and
    uninteresting) start and end banners.
  * Mapping `'enter'` or `'exit'` to `None` in the `formats` dict you
    pass in to the constructor will suppress the `enter` and `exit`
    banners respectively.
  * `Log.write('')` is ignored; you have to log some text for real
    to cause the start and end banners to happen.
  * *Note:* I have a major, backwards-incompatible rewrite of
    `Log` under process.  The `Log` interface will change some,
    `Destination` will change completely, and `Sink` will change a
    whole lot too.  You're gonna love it!  (In the meantime...
    don't get too comfortable!)
* Added [`Formatter`](#formattertemplate-mapnone--relaxedfalse-stretchtrue-width79-kwargs)
  to [*big.template*](#bigtemplate).  `Formatter` is a reusable formatter for
  multi-line text templates with clever support for repeated / stretched
  line-fill fields via "starred interpolations".
* `StateManager` fixes in *big.state*:
  * If `on_exit` raises an exception, the transition is aborted;
    `state` remains unchanged, and `next` is reset to `None`.
  * `StateManager` now handles observers raising an exception.
    If any observer raises an exception, `StateManager` remembers the first
    exception raised, continues calling the remaining observers,
    completes the transition, and then re-raises that first exception.
  * Observer lists are no longer cached internally--they're now snapshotted
    at the start of every transition.  This fixes an obscure edge case:
    if you replaced one observer A with another observer B, and A == B even
    though they're different objects, the `StateManager` wouldn't refresh
    its cache and would continue calling A.
  * Trimmed no-op `State.on_enter` and `State.on_exit`
    methods.  They were useless in and of themselves, but I put them
    there on the theory that they'd help with autocomplete for these
    methods in subclasses when using advanced editors like PyCharm.
    But that's not a strong enough reason to keep 'em.  Sorry, you'll
    just have to type `def on_enter(self):` by hand yourself, like
    some sort of caveman.
* `big.text` multi-function fixes and polish:
  * `multistrip`, `multisplit`, and `multipartition`/`multirpartition`
    now correctly accept one-shot iterables--like generators--for
    their `separator` argument.
  * `multistrip`: fixed `strip=PROGRESSIVE` when `maxsplit=None`.
  * Added `__index__` support for `maxsplit` and `count` parameters.
  * Documentation updates, reflecting these functions returning
    slices of the original object (rather than guaranteed `str`
    or `bytes` objects).  This has been true for a while, but the
    documentation was stale.
* Minor bugfixes in `parse_template_string` in *big.template:*
  * Improved error message for an unterminated comment;
    it now shows where the comment started, not where it ended.
  * Now catch tokenization errors and re-raise a nicer exception.

</dd></dl>


## 0.13

*2026/02/17*

<dl><dd>

It's been more than a year... and I've been busy!

* Added three new modules:
  * [*big.types*](#bigtypes), which contains core types,
  * [*big.tokens*](#bigtokens), useful functions and values
    when working with Python's tokenizer, and
  * [*big.template*](#bigtemplate), functions that parse strings
    containing a simple template syntax.
* Added [`linked_list`](#linked_list) to new module *big.types*.
  `linked_list` is a
  thoughtful implementation of a standard linked list data
  structure, with an API and UX modeled on Python's `list`
  and `collections.deque` objects.  Unlike Python's builtins,
  you're permitted to add and remove values to a `linked_list`
  while iterating.  `linked_list` also supports locking.
* Added [`string`](#string) to new module *big.types*.
  `string` is a subclass
  of `str` that tracks line number and column number offsets
  for you.  Just initialize one big `string` containing an
  entire file, and every substring of that string will know
  its line number, column number, and offset in characters
  from the beginning.
* `big.lines` and all the "lines modifier" functions
  are now deprecated; `string` replaces all of it
  (and it's a *massive* upgrade!).  `big.lines` will
  move to the `deprecated` module no sooner than
  March 2026, and will be removed no sooner than November 2026.
* Added [`strip_indents`](#strip_indentslines--tab_width8-linebreakslinebreaks)
  and
  [`strip_line_comments`](#strip_line_commentslines-line_comment_markers--escape-quotes-multiline_quotes-linebreakslinebreaks) to *big.text*.
  These provide the same functionality as the old `lines_strip_indent`
  and `lines_strip_line_comments` line modifier functions,
  but now operate on iterables of strings instead of
  "lines" iterators.
* Added [`Pattern`](#patterns-flags0) to *big.text*.
  This is a wrapper around `re.Pattern` that preserves
  slices of str subclasses.
* Added [`parse_template_string`](#parse_template_strings--parse_expressionstrue-parse_commentsfalse-parse_statementsfalse-parse_whitespace_eaterfalse-quotes--multiline_quotes-escape)
  and
  [`eval_template_string`](#eval_template_strings-globals-localsnone--parse_expressionstrue-parse_commentsfalse-parse_whitespace_eaterfalse)
  to new module *big.template*.
    * `parse_template_string`
      parses a string containing Jinja-like interpolations,
      and returns an iterator that yields strings and
      `Interpolation` objects.  (This is similar to
      "t-strings" in Python 3.14+.)
    * `eval_template_string` calls `parse_template_string`
      to parse a string, then evaluates the expressions
      (and filters) using `eval`.  It returns the resulting
      string with all substitutions rendered.
* Rewrote [`BoundInnerClass`](#BoundInnerClass), and it's a
  huge improvement. The rewrite removes some old concerns:
    * You no longer need the `parent.cls` hack!  (Well, you
      do if you support Python 3.6, but it's no longer needed
      in Python 3.7+.  Bound inner class adds a new function,
      [`bound_inner_base`](#bound_inner_basecls),
      to help with the transition.)
    * The bound inner class implementation now relies on
      comparison by identity instead of by name, which means
      you may now add aliases and/or rename your inner classes
      to your heart's content.
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
    * [`unbound`](#unboundcls) returns the unbound base class
      of `cls` if `cls` is a bound inner class.
    * [`is_boundinnerclass`](#is_boundinnerclasscls) returns true if called on a
      class decorated with `@BoundInnerClass`, whether or
      not it has been bound to an instance.
    * [`is_unboundinnerclass`](#is_unboundinnerclasscls) returns true if called on a
      class decorated with `@UnboundInnerClass`, whether or
      not it has been bound to an instance.
    * [`is_bound`](#is_boundcls) returns true if called on a bound inner
      class that has been bound to an instance.
    * [`bound_to`](#bound_tocls) returns the instance that cls has been
      bound to, if `cls` is a bound inner class bound to an instance.
    * [`type_bound_to`](#type_bound_tocls)` returns the instance that `type(o)` has
      been bound to, if `type(o)` is a bound inner class bound
      to an instance.
    * [`bound_inner_base`](#bound_inner_basecls) is only needed to use BoundInnerClass
      with Python 3.6.  It's unnecessary in Python 3.7+.
* Added [`generate_tokens`](#generate_tokenss) to new module *big.tokens*.
  `generate_tokens` is a convenience wrapper around
  Python's `tokenize.generate_tokens`, which has an
  abstruse "readline"-based interface.
  `tokens.generate_tokens` instead
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
* Added [`iterator_context`](#iterator_contextiterator-start0) to *big.itertools*.  `iterator_context`
  is like an extended version of Python's `enumerate`,
  directly inspired by Jinja's
  ["loop special variables"](https://jinja.palletsprojects.com/en/stable/templates/#for)
  and Mako's ["loop context"](https://docs.makotemplates.org/en/latest/runtime.html#the-loop-context).
  It wraps an iterator and provides helpful metadata.
* Added
  [`iterator_filter`](#iterator_filteriterator--stop_at_valueundefined-stop_at_innone-stop_at_predicatenone-stop_at_countnone-reject_valueundefined-reject_innone-reject_predicatenone-only_valueundefined-only_innone-only_predicatenone-call_everynone)
  to *big.itertools*.  `iterator_filter`
  is a pass-through iterator that filters values.
  You pass in an iterator, and rules for what values you
  want to see / don't want to see, and it returns
  an iterator that only yields the values you want.
* Rewrote the entire [*big.log*](#biglog) module.  I'd stopped
  using the old `Log` class, yet on a couple recent projects
  I hacked up a quick-and-dirty log... clearly the old `Log`
  wasn't solving my problem anymore.  The new `Log` is designed
  explicitly for lightweight logging, mostly for debugging.
  It's simple to use, feature-rich, high-performance, and by
  default runs in "threaded" mode where logging calls are 5x
  faster than calling `print`!
  * I added a backwards-compatible [`OldLog`](#oldlogclocknone) to *big.log*
    in case anybody is using the old `Log` class.  This
    provides the API and functionality of the old `Log`
    class, but is reimplemented on top of the new `Log`.
    Hopefully the way I did it will ease your transition
    to the obviously-superior new `Log`.  The old `Log`
    has been relocated to the *big.deprecated*
    module. Both `OldLog` and the old `Log` are deprecated,
    and will be removed someday, no earlier than March 2027.
* Added [`ModuleManager`](#modulemanager) to *big.builtin*.
  `ModuleManager` helps you manage a module's namespace,
  making it easy to populate `__all__` and clean up
  temporary symbols.
* Added [`ClassRegistry`](#ClassRegistry) to *big.builtin*.
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
* [`split_quoted_strings`](#split_quoted_stringss-quotes---escape-multiline_quotes-state)
  in *big.text* now obeys
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

</dd></dl>


## 0.12.8

*2025/01/06*

<dl><dd>

* Added `search_path` to the *big.file* module.  `search_path`
  implements "search path" functionality; given a list of
  directories, a filename, and optionally a list of file
  extensions to try, returns the first existing file that matches.
* `multisplit` and `split_delimiters` now properly support
  subclasses of `str`. All strings yielded by these functions
  are now guaranteed to be slices of the original `s` parameter
  passed in, or otherwise produced by making method calls on the
  original `s` parameter that return strings.

</dd></dl>


## 0.12.7

*2024/12/15*

<dl><dd>

A teeny tiny new feature.

* `LineInfo` now supports a `copy` method, which returns a copy of the `LineInfo`
  object in its current state.

</dd></dl>


## 0.12.6

*2024/12/13*

<dl><dd>

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

</dd></dl>


## 0.12.5

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

* A breaking API change to [`split_delimiters`](#split_delimiterss-delimiters--state-yields4) is coming.

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
  [`Delimiter`](#delimiterclose--escape-multilinetrue-quotingfalse-nestednone-literal-changenone)
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


## 0.12.4

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


## 0.12.3

*2024/09/17*

<dl><dd>

Optimized
[`split_delimiters`](#split_delimiterss-delimiters--state-yields4).
The new version uses a much more efficient internal representation
of how to react to the various delimiters when processing the text.
Perfunctory `timeit` experiments suggest this new `split_delimiters`
is maybe 5-6% faster than it was in 12.2.

Minor breaking change: `split_delimiters` now consistently
raises `SyntaxError` for mismatched delimiters.  (Previously it
would sometimes raise `ValueError`.)

</dd></dl>


## 0.12.2

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


## 0.12.1

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


## 0.12

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

[`Delimiter`](#delimiterclose--escape-multilinetrue-quotingfalse-nestednone-literal-changenone)

[`LineInfo`](#lineinfo)

[`lines_strip_line_comments`](#lines_strip_line_comments)

[`split_delimiters`](#split_delimiterss-delimiters--state-yields4)

[`split_quoted_strings`](#split_quoted_stringss-quotes---escape-multiline_quotes-state)

</dd></dl>


These functions have been renamed:

<dl><dd>

`lines_filter_comment_lines` is now [`lines_filter_line_comment_lines`](#lines_filter_line_comment_lines)

`lines_strip_comments` is now [`lines_strip_line_comments`](#lines_strip_line_comments)

`parse_delimiters` is now [`split_delimiters`](#split_delimiterss-delimiters--state-yields4)

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
[`split_delimiters`](#split_delimiterss-delimiters--state-yields4)
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
[`merge_columns`](#merge_columnscolumns-column_separator--overflow_strategyoverflowstrategyraise-overflow_before0-overflow_after0-tab_width8-rawnone)
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
[`split_delimiters`](#split_delimiterss-delimiters--state-yields4)
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

[`split_delimiters`](#split_delimiterss-delimiters--state-yields4)
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


## 0.11

*2023/09/19*

<dl><dd>

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
  [`split_text_with_code`](#split_text_with_codes--code_indent4-tab_width8)
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

</dd></dl>


## 0.10

*2023/09/04*

<dl><dd>

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


## 0.9.2

*2023/07/22*

<dl><dd>

Extremely minor release.  No new features or bug fixes.

* Fixed coverage, now back to the usual 100%.
  (This just required changing the tests, which
  *didn't* find any new bugs.)
* Made the tests for [`Log`](#logdestinations-options)
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


## 0.9.1
<dl><dd>

*2023/06/28*

* Added the new [`big.log`](#biglog) module, with its new
  [`Log`](#logdestinations-options) class!
  I wrote this for another project--but it turned out so nice
  I just had to add it to **big**!

</dd></dl>

## 0.9

*2023/06/15*

<dl><dd>

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


## 0.8.3

*2023/06/11*

<dl><dd>

* Added
  [`int_to_words`](#int_to_wordsi--flowerytrue-ordinalfalse).
* All tests now insert the local **big** directory
  onto `sys.path`, so you can run the tests on your
  local copy without having to install.  Especially
  convenient for testing with old versions of Python!

> *Note:* tomorrow, **big** will be one year old!

</dd></dl>


## 0.8.2
*2023/05/19*

<dl><dd>

* Convert all iterator functions to use my new approach:
  instead of checking arguments inside the iterator,
  the function you call checks arguments, then has a
  nested iterator function which it runs and returns the
  result.  This means bad inputs raise their exceptions
  at the call site where the iterator is constructed,
  rather than when the first value is yielded by the iterator!

</dd></dl>


## 0.8.1

*2023/05/19*

<dl><dd>

* Added
  `parse_delimiters` (ed: now [`split_delimiters`](#split_delimiterss-delimiters--state-yields4))
  and
  [`Delimiter`.](#delimiteropen-close--backslashfalse-nestedtrue)

</dd></dl>


## 0.8

*2023/05/18*

<dl><dd>

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


## 0.7.1

*2023/03/13*

<dl><dd>

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


## 0.7

*2023/03/11*

<dl><dd>

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


## 0.6.18

*2023/03/09*

<dl><dd>

* Retooled
  [`multisplit`](#multisplits-separatorsnone--keepfalse-maxsplit-1-reversefalse-separatefalse-stripfalse)
  and
  [`multistrip`](#multistrips-separators-lefttrue-righttrue)
  argument verification code.  Both functions now consistently check all
  their inputs, and use consistent error messages when raising an exception.

</dd></dl>


## 0.6.17

*2023/03/09*

<dl><dd>

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


## 0.6.16

*2023/02/26*

<dl><dd>

* Fixed Python 3.6 support! Some equals-signs-in-f-strings and some
  other anachronisms had crept in.  0.6.16 has been tested on all
  versions from 3.6 to 3.11 (as well as having 100% *coverage*).
* Made the `dateutils` package an optional dependency.  Only one function
  needs it, [`parse_timestamp_3339Z()`](#parse_timestamp_3339zs--timezonenone).
* Minor cleanup in [`PushbackIterator()`](#pushbackiteratoriterablenone).
  It also uses slots now, which should make it a bit faster.

</dd></dl>


## 0.6.15

*2023/01/07*

<dl><dd>

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


## 0.6.14

*2022/12/11*

<dl><dd>

* Improved the text of the `RuntimeError` raised by `TopologicalSorter.View`
  when the view is incoherent.  Now it tells you exactly what nodes are
  conflicting.
* Expanded the tutorial on `multisplit`.

</dd></dl>


## 0.6.13

*2022/12/11*

<dl><dd>

* Changed [`translate_filename_to_exfat(s)`](#translate_filename_to_exfats)
  behavior: when modifying a string with a colon (`':'`) *not* followed by
  a space, it used to convert it to a dash (`'-'`).  Now it converts the
  colon to a period (`'.'`), which looks a little more natural.  A colon
  followed by a space is still converted to a dash followed by a space.

</dd></dl>


## 0.6.12

*tagged 2022/12/04*

<dl><dd>

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


## 0.6.11

*tagged 2022/11/13*

<dl><dd>

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


## 0.6.10

*2022/10/26*

<dl><dd>

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


## 0.6.8

*2022/10/16*

<dl><dd>

* Renamed two of the three freshly-added lines modifier functions:
  `lines_filter_contains` is now 
  [`lines_containing`](#bigtext),
  and `lines_filter_grep` is now
  [`lines_grep`](#lines_grep).

</dd></dl>


## 0.6.7

*2022/10/16*

<dl><dd>

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


## 0.6.6

*2022/10/14*

<dl><dd>

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


## 0.6.5

*2022/10/13*

<dl><dd>

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


## 0.6.1

*2022/10/13*

<dl><dd>

* I realized that [`whitespace`](#whitespace) should contain the DOS end-of-line
  sequence (`'\r\n'`), as it should be considered a single separator
  when splitting etc.  I added that, along with [`whitespace_no_dos`](#whitespace),
  and naturally [`utf8_whitespace_no_dos`](#whitespace) and
  [`ascii_whitespace_no_dos`](#whitespace) too.
* Minor doc fixes.

</dd></dl>


## 0.6

*2022/10/13*

<dl><dd>

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


## 0.5.2

*2022/09/12*

<dl><dd>

* Added `stripped_lines` and `rstripped_lines` to the [`text`](#bigtext) module.
* Added support for `len` to the [`TopologicalSorter`](#topologicalsortergraphnone) object.

</dd></dl>


## 0.5.1

*2022/09/04*

<dl><dd>

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


## 0.5

*2022/06/12*

<dl><dd>

* Initial release.
</dd></dl>
