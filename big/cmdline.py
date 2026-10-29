#!/usr/bin/env python3

#########################################################
#########################################################
###
###  For people who don't want a dependency on Appeal,
###  here's a mini-Appeal just for big.
###  just the same way that big has a mini-Tidy in the
###  big.template module.
###
###  You get:
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

@export
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
                            is_optional = isinstance(converter, optional)
                            if is_optional:
                                converter = converter.T
                                rendered.append('[')
                            rendered.append(converter.__name__)
                            if is_optional:
                                rendered.append(']')
                    else:
                        rendered.append(' value')
                    rendered.append(']')
                    options.append(''.join(rendered))
        usage = []
        if self.name:
            usage.append(self.name)
        if options:
            usage.extend(options)
        if arguments:
            usage.append(''.join(arguments) + ''.join(trailing))
        return ' '.join(usage)


    def __call__(self, processor):
        self._introspect()

        a = []
        kw = {}
        arguments = list(self.arguments)
        arguments.reverse()

        keep_going = True

        while keep_going and processor:
            arg = processor.pop()

            if (not processor.ignore_options) and arg.startswith('-') and (arg != '-'):
                if arg == '--':
                    processor.ignore_options = True
                    continue

                if arg == '-':
                    raise UsageError(f"invalid option {arg}", command=self)

                if arg.startswith('--'):
                    option, equals, oparg = arg.partition('=')
                else:
                    option = arg
                    equals = oparg = ''

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


def validate_option_string(s):
    "'-X' (one alphanumeric) or '--xx' (at least four chars)."
    ok = (isinstance(s, str)
          and s.startswith('-')
          and (((len(s) == 2) and s[1].isalnum())
               or ((len(s) >= 4) and s.startswith('--'))))
    if not ok:
        raise ConfigurationError(f"{s!r} is not a legal option string")
    return s

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



@export
def default_global_mappings(app):
    app.map_help_options()
    app.map_version_options()
    app.map_help_command()
    app.map_version_command()
    app.map_default()

@export
class App:
    def __init__(self, name=None, *,
            default_options=default_options,
            default_mappings=default_global_mappings,
            doc='',
            repeat=False,
            version=None):
        default_name = os.path.basename(sys.argv[0])
        self.name = name or default_name
        self.default_mappings = default_mappings
        self.default_options = default_options
        self.doc = doc
        self.repeat = repeat
        self.version = version

        self.fn_to_command = {}
        self.commands = {}
        self._called_default_mappings = False

        self._preprecommand = self._fn_to_command(self.preprecommand)
        self._preprecommand.name = ''
        self.option('help')(self.preprecommand)
        self.option('version')(self.preprecommand)

        self._precommand = None
        self._default = None

    default_help_template = textwrap.dedent("""
        Usage: {usage}

        {doc}

        Commands:
            {commands}
        """.lstrip('\n').rstrip())

    def _map_default_options(self, options, name):
        c = self._precommand
        if c:
            c._introspect()

        for option in options:
            if c and (option in c.options):
                continue
            validate_option_string(option)
            self.option(name, option)(self.preprecommand)

    def map_help_options(self, *options):
        self._map_default_options(options or ('-h', '--help'), 'help')

    def map_version_options(self, *options):
        if self.version is None:
            return
        self._map_default_options(options or ('--version',), 'version')

    def map_version_command(self, name='version'):
        if (self.version is None) or (not self.commands) or (name in self.commands):
            return
        self.commands[name] = self._fn_to_command(self.print_version)

    def map_help_command(self, name='help'):
        if (not self.commands) or (name in self.commands):
            return
        self.commands[name] = self._fn_to_command(self.help)

    def map_default(self):
        if self.commands and (self._default is None):
            self._default = self._fn_to_command(self._default_default)


    def _command_summary(self):
        template = self.default_help_template
        map = {}

        doc = self.doc

        usage = [os.path.basename(self.name)]
        precommand = self._precommand
        if precommand:
            precommand_options = precommand.usage().strip().partition(' ')[2]
            if precommand_options:
                usage.append(precommand_options)
            d = precommand.callable.__doc__
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

        if doc is None:
            doc = ''

        doc = doc.rstrip()

        map['doc'] = doc

        usage.append("<command> ...")
        map['usage'] = ' '.join(usage)


        pairs = []
        for name, c in self.commands.items():
            summary = c.__doc__.strip().split('\n')[0]
            pairs.append((name, summary))

        # figure out indent of {commands} line, if present.
        # also, suppress {doc} and trailing newlines if doc is empty.
        # also, suppress Commands: and {commands} and trailing newlines if there are no commands.
        indent = '    '
        lines = []
        append = lines.append
        ignoring_blank_lines = False

        for line in template.splitlines(True):
            stripped = line.strip()

            if stripped:
                ignoring_blank_lines = False
            elif ignoring_blank_lines:
                continue

            if stripped == '{doc}':
                if not doc:
                    ignoring_blank_lines = True
                    continue

            if stripped == 'Commands:':
                if not self.commands:
                    ignoring_blank_lines = True
                    continue

            before, marker, after = line.partition("{commands}")
            if marker:
                if not self.commands:
                    ignoring_blank_lines = True
                    continue
                indent = before

            append(line)

        template = ''.join(lines)

        map['commands'] = format_definition_list(pairs, indent=indent).lstrip()
        print(template.format_map(map))

    def _usage(self, command=None):
            usages = [self.name]
            commands = [self._preprecommand, self._precommand]
            if command:
                commands.append(command)
            for o in commands:
                if o is None:
                    continue
                usage = o.usage()
                if usage:
                    usages.append(usage)
            if (not command) and self.commands:
                usages.append('<command> ...')
            return " ".join(usages)

    def _help_hint(self, command):
        if command:
            return ''

        help_command = self._fn_to_command(self.help)

        help = None
        if self.commands.get('help', None) == help_command:
            help = f'help'
        elif self.commands:
            for k, v in self.commands.items():
                if v == help_command:
                    help = k
                    break

        if (not help) and (self._preprecommand is not None):
            preprecommand_options = self._preprecommand.options
            for option in ('--help', '-h'):
                if option in preprecommand_options:
                    help = option
                    break

        if not help:
            return ''

        if self.commands:
            suffix = "for a list of commands"
        else:
            suffix = "for full usage"

        return f"(run '{self.name} {help}' {suffix})"

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

    def _default_default(self):
        raise UsageError('no command specified')

    def print_version(self):
        "Prints the version."
        print(self.version)

    def default(self):
        def default(fn):
            if self._default:
                raise ConfigurationError("can't set default twice")
            self._default = self._fn_to_command(fn)
            return fn
        return default

    def precommand(self):
        def precommand(fn):
            if self._precommand:
                raise ConfigurationError("can't set precommand twice")
            self._precommand = self._fn_to_command(fn)
            self._precommand.name = ''
            return fn
        return precommand

    def preprecommand(self, *, help:optional[str]=None, version=False):
        if help is not None:
            self.help(help)
            sys.exit(0)
        if version:
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
            result = 0

            if self._preprecommand:
                self._preprecommand(processor)

            if self._precommand:
                result = self._precommand(processor)

            if not processor:
                if self._default is None:
                    return result
                return self._default(processor)

            command = None
            if self.commands:
                while processor:
                    name = processor.pop()
                    if name.startswith('-') and (not processor.ignore_options):
                        raise UsageError(f"unknown option '{name}'")
                    command = self.commands.get(name)
                    if command is None:
                        raise UsageError(f"unknown command '{name}'")

                    processor.ignore_options = False # resets at every command boundary
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
            assert ue.usage
            print("error:", str(ue), file=sys.stderr)
            print("usage:", ue.usage, file=sys.stderr)
            hint = self._help_hint(ue.command)
            if hint:
                print(hint, file=sys.stderr)
            sys.exit(2)


mm()