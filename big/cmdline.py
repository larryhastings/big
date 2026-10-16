#!/usr/bin/env python3

#########################################################
#########################################################
###
###  For people who don't want a dependency on Appeal,
###  maybe I should write a mini-Appeal and put it in big,
###  just the same way that big has a mini-Tidy in the
###  big.template module.
###
###  You'd get:
###
###  * long options with automatic short options
###  * options support bool or a single str (converted)
###  * same type annotation rules
###      * annotation is highest priority
###      * if not that, type(default)
###      * if no default or annotation it's a str
###  * arguments go into keyword-or-positional args
###    (or positional-only, first, if you use those)
###  * arguments also support annotations and/or defaults
###  * args works
###  * only handles arguments and options,
###    commands are implemented separately
###  * '--' for no more args, '-' for stdin
###  * maybe explicit override for short and long options
###  * help and version are automatic, can be overriden
###
###
###     -abcVALUE        bundled shorts; first oparg-taker ends the bundle, rest is its oparg
###     -cVALUE          same rule, bundle of one
###     * -c=VALUE         = stripped; -c==VALUE passes a value starting with =
###     * -c VALUE         next argv component, unconditionally (even if it starts with -)
###     * --option=VALUE   = splits at the FIRST =; --option=a=b passes a=b
###     * --option VALUE   next argv component, unconditionally
###     --               ends option parsing
###
###     foo(*, x) should map -x but not --x
###
### appeal should use this approach for default_mappings and default_options
###
###
### decorate usage arguments and opargs like appeal
###
### outdent docstring
###
### implement repeat


import inspect
import math
import os.path
import re
import sys
import textwrap

from big.text import format_definition_list
from big.builtin import ModuleManager

mm = ModuleManager()
export = mm.export

try:
    from shlex import join as shlex_join
except ImportError: # pragma: nocover
    def shlex_join(args):
        return " ".join(repr(s) if len(s.split()) > 1 else s for s in args)

@export
class CommandLineError(RuntimeError):
    def __init__(self, s, *, command=None):
        super().__init__(s)
        self.command = command


@export
class UsageError(CommandLineError):
    def __init__(self, s, *, command=None, usage=''):
        super().__init__(s)
        self.command = command
        self.usage = usage

@export
class ConfigurationError(CommandLineError):
    pass


@export
class Processor:
    def __init__(self, args):
        self.args = list(args)
        self.ignore_options = False

    def insert(self, args):
        self.args = list(args) + self.args

    def push(self, arg):
        return self.args.insert(0, arg)

    def pop(self):
        return self.args.pop(0)

    def peek(self):
        if not self.args:
            return ''
        return self.args[0]

    def __bool__(self):
        return bool(self.args)

    def __repr__(self):
        return f"<Processor {self.args} ignore_options={self.ignore_options}>"


def _p_to_converter(p, converter=None):
    if converter is not None:
        return converter
    if p.annotation is not p.empty:
        return p.annotation
    if p.default not in (p.empty, None):
        return type(p.default)
    return str


# --8<-- start cmdline optional --8<--
class _OptionalMeta(type):
    def __getitem__(cls, T):
        return cls(T)

def _convert(converter, value, *, command=None):
    if isinstance(converter, optional):
        converter = converter.T

    if value is None:
        return converter()

    try:
        return converter(value)
    except (ValueError, TypeError):
        name = getattr(converter, '__name__', 'value')
        raise UsageError(f"invalid value {value!r} (not a valid {name})", command=command) from None

class optional(metaclass=_OptionalMeta):
    """
    Marks an option's oparg as *optional*, like "make -j [jobs]".

    Annotate the parameter with optional[T].  If the user doesn't
    specify the option ("make"), the parameter gets the default value
    as its argument.  If they specify the option but don't specify an
    oparg ("make -j"), cmdline will call the appropriate type (the
    annotation, or the type of the default) without an argument and
    pass in the result as the argument.  And of course, if they specify
    the option with its oparg ("make -j 3") cmdline passes in the
    oparg converted using the appropriate type.
    """

    def __init__(self, T):
        if isinstance(T, tuple):
            raise ConfigurationError("optional[] takes exactly one converter")
        if not callable(T):
            raise ConfigurationError(f"optional[]: {T!r} isn't callable")

        self.T = T

    def __call__(self, value=None):
        return _convert(self.T, value)

# --8<-- end cmdline optional --8<--


@export
class Command:
    POSITIONAL_ONLY = inspect.Parameter.POSITIONAL_ONLY
    POSITIONAL_OR_KEYWORD = inspect.Parameter.POSITIONAL_OR_KEYWORD
    VAR_POSITIONAL = inspect.Parameter.VAR_POSITIONAL
    KEYWORD_ONLY = inspect.Parameter.KEYWORD_ONLY
    VAR_KEYWORD = inspect.Parameter.VAR_KEYWORD
    empty = inspect.Parameter.empty

    positional = set((POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD))

    def __init__(self, app, callable, *, name=''):
        self.app = app
        self.callable = callable
        self.name = name or callable.__name__

        self.__doc__ = textwrap.dedent(callable.__doc__ or '')

        self.configured = set()
        self.arguments = []
        self.var_positional = None
        self.options = {}
        self.minimum_arguments = 0
        self.maximum_arguments = 0

        self._signature = None

    @property
    def signature(self):
        if self._signature is None:
            self._signature = inspect.signature(self.callable)
        return self._signature

    def _introspect(self):
        POSITIONAL_ONLY = self.POSITIONAL_ONLY
        POSITIONAL_OR_KEYWORD = self.POSITIONAL_OR_KEYWORD
        VAR_POSITIONAL = self.VAR_POSITIONAL
        KEYWORD_ONLY = self.KEYWORD_ONLY
        VAR_KEYWORD = self.VAR_KEYWORD
        empty = self.empty
        positional = self.positional

        signature = self.signature

        for name, p in signature.parameters.items():
            if name in self.configured:
                continue
            self.configured.add(name)
            converter = _p_to_converter(p)

            if p.kind in positional:
                required = p.default is empty
                self.minimum_arguments += required
                self.maximum_arguments += 1
                self.arguments.append((name, converter))
            elif p.kind is VAR_POSITIONAL:
                self.var_positional = converter
                self.maximum_arguments = math.inf
            elif p.kind is KEYWORD_ONLY:
                options = self.app.default_options(self.app, self.callable, name)
            else:
                raise ConfigurationError(f'unhandled kind {p.kind}')

    def usage(self):
        self._introspect()

        POSITIONAL_ONLY = self.POSITIONAL_ONLY
        POSITIONAL_OR_KEYWORD = self.POSITIONAL_OR_KEYWORD
        VAR_POSITIONAL = self.VAR_POSITIONAL
        KEYWORD_ONLY = self.KEYWORD_ONLY
        VAR_KEYWORD = self.VAR_KEYWORD
        empty = self.empty
        positional = self.positional

        signature = self.signature
        arguments = []
        trailing = []
        options = []
        for name, p in signature.parameters.items():
            if p.kind in positional:
                if arguments:
                    arguments.append(' ')
                if p.default is not empty:
                    arguments.append('[')
                    trailing.append(']')
                arguments.append(name)
                continue

            if p.kind == KEYWORD_ONLY:
                rendered = []
                converters = set()
                for option, bundle in self.options.items():
                    _name, converter, default = bundle
                    if _name == name:
                        rendered.append('[' if not rendered else '|')
                        rendered.append(option)
                        converters.add(converter)
                if rendered:
                    if len(converters) == 1:
                        converter = list(converters)[0]
                        if converter is not bool:
                            rendered.append(' ')
                            if isinstance(converter, optional):
                                converter = converter.T
                            rendered.append(converter.__name__)
                    else:
                        rendered.append(' value')
                    rendered.append(']')
                    options.append(''.join(rendered))
        usage = self.name
        if options:
            usage += ' ' + ' '.join(options)
        if arguments:
            usage += ' ' + ''.join(arguments) + ''.join(trailing)
        return usage


    def __call__(self, processor):
        self._introspect()

        ignore_options = False

        a = []
        kw = {}
        arguments = list(self.arguments)
        arguments.reverse()

        keep_going = True

        while keep_going and processor:
            arg = processor.pop()

            if (not ignore_options) and arg.startswith('-') and (arg != '-'):
                if arg == '--':
                    ignore_options = True
                    continue

                option, equals, oparg = arg.partition('=')
                if option == '-':
                    raise UsageError(f"invalid option {arg}", command=self)
                bundle = self.options.get(option)
                if bundle:
                    # it's an option!
                    name, converter, default = bundle
                    if converter is bool:
                        if equals:
                            raise UsageError(f"can't use = syntax with boolean option {option}", command=self)
                        kw[name] = not default
                    else:
                        if equals:
                            value = oparg
                        elif processor:
                            oparg = processor.pop()
                            value = oparg
                        elif isinstance(converter, optional):
                            value = None
                        else:
                            raise UsageError(f"missing oparg for option {option}", command=self)

                        kw[name] = _convert(converter, value, command=self)
                    continue

                if option.startswith('--'):
                    # not for us, maybe it's for the next guy
                    processor.push(option)
                    break

                # option doesn't start with '--',
                # but it does start with '-':

                if not option[1].isdigit():
                    # do we have grouped single options?
                    #   -abc
                    # maybe with a concatenated value?
                    #   -abcVALUE
                    #
                    # rewrite into separate options, with possible trailing oparg:
                    # "-abc"      -> ["-a", "-b", "-c"]
                    # "-abcVALUE" -> ["-a", "-b", "-c", "VALUE"]
                    short_options = list(option)
                    short_options.reverse()
                    short_options.pop() # remove '-'
                    inserted = []
                    while short_options:
                        short_option = "-" + short_options.pop()
                        bundle = self.options.get(short_option)
                        if not bundle:
                            # not for us, maybe it's for the next guy
                            processor.push(option)
                            keep_going = False
                            inserted.clear()
                            break
                        name, converter, default = bundle
                        inserted.append(short_option)
                        if converter is not bool:
                            if equals:
                                if short_options:
                                    o = short_options[0]
                                    raise UsageError(f'unrecognized option -{o}', command=self)
                            else:
                                short_options.reverse()
                                oparg = ''.join(short_options)
                                short_options.clear()
                            inserted.append(oparg)

                    if inserted:
                        processor.insert(inserted)
                    continue

                # if the first character after the - is a digit 0-9,
                # it might be a numeric short option, or an int/float.
                #
                # here's how cmdline handles a command-line argument
                # that COULD be an option, which starts with a single
                # dash followed by a digit 0-9:
                #
                #    * if the argument is PERFECTLY parsed as an
                #      option, then it's an option.  if you have
                #      -2 and -3 both defined, but not -4, -23 is
                #      parsed as an option, but -24 fails this test.
                #    * if float() parses the string without raising,
                #      it's an argument.
                #    * otherwise, we raise a UsageError assuming that
                #      it's a malformed option.
                #
                # since we got here, we've already failed looking up
                # the option.  so only float is acceptable now.
                try:
                    float(option)
                    if ('_' in option) or (not option.isascii()):
                        raise ValueError('x')
                except ValueError:
                    raise UsageError(f"unrecognized option {option}", command=self)

            # conventional argument
            if arguments:
                name, converter = arguments.pop()
            elif self.var_positional:
                converter = self.var_positional
            else:
                processor.push(arg)
                break

            value = _convert(converter, arg, command=self)
            a.append(value)

        assert len(a) <= self.maximum_arguments
        if not (self.minimum_arguments <= len(a)):
            if self.maximum_arguments is not math.inf:
                if self.minimum_arguments == self.maximum_arguments:
                    raise UsageError(f"{self.name} requires {self.minimum_arguments} arguments, not {len(a)} arguments", command=self)
                raise UsageError(f"{self.name} requires between {self.minimum_arguments} and {self.maximum_arguments} arguments, not {len(a)} arguments", command=self)
            else:
                raise UsageError(f"{self.name} requires at least {self.minimum_arguments} arguments, not {len(a)} arguments", command=self)

        return self.callable(*a, **kw)


@export
def default_options(app, fn, name):
    assert name
    if name.startswith('_'):
        return

    c = app._fn_to_command(fn)

    mapped = False
    short_option = f'-{name[0]}'
    if short_option not in c.options:
        app.option(name, short_option)(fn)
        mapped = True

    if len(name) == 1:
        if not mapped:
            raise ConfigurationError(f"unmappable parameter {name}")
        return

    long_option = '--' + name.lower().replace('_', '-')
    app.option(name, long_option)(fn)


default_mappings_help = ('-h', '--help', 'help')
export('default_mappings_help')

default_mappings_version = ('-V', '--version', 'version')
export('default_mappings_version')


@export
def default_mappings(*options):
    default_options_set = set(default_mappings_help + default_mappings_version)
    options_set = set(options) if options else default_options_set

    unsupported = options_set - default_options_set
    if unsupported:
        s = ' '.join(str(s) for s in sorted(unsupported))
        raise ConfigurationError('unsupported default mappings: {s}')


    def default_mappings(app):
        global_command = app._global_command
        if global_command:
            global_command._introspect()
            defined = global_command.options.__contains__
        else:
            defined = lambda name: False

        defaults = [
            (('-h', '--help'),    'help',    False),
            (('-V', '--version'), 'Version',  True),
            ]

        for options, name, is_version in defaults:
            added = []
            for option in options:
                if is_version and (not app.version):
                    continue
                if (option in options_set) and (not defined(option)):
                    added.append(option)

            app.option(name, *added)(app.precommand)
            app._precommand = app._fn_to_command(app.precommand)

        for name, command, is_version in (
            ('version', app.print_version, True),
            ('help', app.help, False),
            ):
            if is_version:
                if not app.version:
                    continue
            if (name in options_set) and (name not in app.commands):
                c = app._fn_to_command(command)
                app.commands[name] = c

        if not app._default_command:
            app._default_command = app.help

    return default_mappings

@export
class App:
    def __init__(self, name=None, *,
            default_options=default_options,
            default_mappings=default_mappings(),
            doc='',
            repeat=False,
            version=None):
        self.name = name
        self.default_mappings = default_mappings
        self.default_options = default_options
        self.doc = doc
        self.repeat = repeat
        self.version = version

        self.fn_to_command = {}
        self.commands = {}
        self._called_default_mappings = False

        self._default_command = None
        self._precommand = None
        self._global_command = None

    default_help_template = textwrap.dedent("""
        Usage: {usage}

        {doc}

        Commands:
            {commands}
        """.lstrip('\n').rstrip())

    def _command_summary(self):
        template = self.default_help_template
        map = {}

        doc = self.doc

        usage = [os.path.basename(sys.argv[0])]
        global_command = self._global_command
        if global_command:
            global_options = global_command.usage().strip().partition(' ')[2]
            if global_options:
                usage.append(global_options)
            d = global_command.callable.__doc__
            if (not doc) and d:
                doc = d

        if not doc:
            # do all of our commands come from the same script?
            # if so, use the docstring of that script as our docs.
            modules = set()
            for c in self.commands.values():
                modules.add(c.callable.__module__)
            if len(modules) == 1:
                module_name = list(modules).pop()
                module = sys.modules[module_name]
                doc = module.__doc__

        map['doc'] = doc

        usage.append("<command> ...")
        map['usage'] = ' '.join(usage)


        pairs = []
        for name, c in self.commands.items():
            summary = c.__doc__.strip().split('\n')[0]
            pairs.append((name, summary))

        # figure out indent of {commands} line, if present
        indent = '    '
        for line in template.splitlines():
            before, marker, after = line.partition("{commands}")
            if marker:
                indent = before
                break
        map['commands'] = format_definition_list(pairs, indent=indent).lstrip()
        print(template.format_map(map))

    def _usage(self, command=None):
            usages = []
            if self._precommand:
                usages.append(self._precommand.usage())
            if self._global_command:
                usages.append(self._global_command.usage())
            if command is not None:
                usages.append(command.usage())
            return " ".join(usages)

    def help(self, topic=''):
        """
        Shows a help overview, or help on a specific topic.

        The 'help' command with no arguments produces basic usage,
        showing global options as well as a list of all commands
        supported by this program.

        With an argument, 'help' shows help on that specific topic.
        """
        if not topic:
            self._command_summary()
            return

        command = self.commands.get(topic, None)
        if command is None:
            raise UsageError(f"unknown help topic '{topic}'")

        usage = command.usage()
        assert usage
        doc = command.__doc__

        print(usage)
        if doc:
            print()
            print(doc)

    def print_version(self):
        print(self.version)

    def default_command(self):
        def default_command(fn):
            if self._default_command:
                raise ConfigurationError("can't set default_command twice")
            self._default_command = self._fn_to_command(fn)
            return fn
        return default_command

    def global_command(self):
        def global_command(fn):
            if self._global_command:
                raise ConfigurationError("can't set global_command twice")
            self._global_command = self._fn_to_command(fn)
            return fn
        return global_command

    def precommand(self, *, help:optional[str]=None, Version=False):
        if help is not None:
            self.help(help)
            sys.exit(0)
        if Version:
            print(f"Version={Version}")
            self.print_version()
            sys.exit(0)

    def _fn_to_command(self, fn):
        return self.fn_to_command.setdefault(fn, Command(self, fn))

    def command(self, name=None):
        def command(fn):
            nonlocal name
            name = name or fn.__name__
            if name in self.commands:
                raise ConfigurationError(f'name {name!r} already registered')
            c = self._fn_to_command(fn)
            c.name = name
            self.commands[name] = c
            return fn
        return command

    def option(self, name, *options, annotation=None):
        def option(fn):
            c = self._fn_to_command(fn)
            p = c.signature.parameters.get(name)
            if not p:
                raise ConfigurationError(f"callable has no {name} parameter")
            c.configured.add(name)
            converter = _p_to_converter(p, annotation)
            t = (name, converter, p.default)
            for option in options:
                if option in c.options:
                    raise ConfigurationError(f"can't set option {option} twice")
                c.options[option] = t
            return fn
        return option

    def process(self, args=None):
        if args is None:
            args = sys.argv[1:]
        processor = Processor(args)

        if not self._called_default_mappings:
            self._called_default_mappings = True
            if self.default_mappings:
                self.default_mappings(self)

        try:
            if not processor:
                return self._default_command(processor)

            result = 0

            if self._precommand:
                self._precommand(processor)

            if self._global_command:
                result = self._global_command(processor)

            command = None
            while processor:
                name = processor.pop()
                if name.startswith('-') and (not processor.ignore_options):
                    raise UsageError(f"unknown option '{name}'")
                command = self.commands.get(name)
                if command is None:
                    raise UsageError(f"unknown command '{name}'")

                result = command(processor)

                if processor.peek().startswith('-') and (not processor.ignore_options):
                    option = processor.pop()
                    raise UsageError(f"unknown option '{option}'", command=command)
                if result:
                    return result
                if not self.repeat:
                    break
                command = None

            if processor:
                quoted = shlex_join(processor.args)
                raise UsageError(f"extra arguments {quoted}", command=command)

        except UsageError as ue:
            if not ue.usage:
                ue.usage = self._usage(ue.command)
            raise

        return result


    def main(self, args=None):
        if args is None:
            args = sys.argv[1:]

        try:
            sys.exit(self.process(args))

        except UsageError as ue:
            print("error:", str(ue), file=sys.stderr)
            assert ue.usage
            print("usage:", ue.usage, file=sys.stderr)
            sys.exit(2)


mm()