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


class ModuleManager:
    def __init__(self):
        self.__all__ = []
        self.deletions = []

    def export(self, *args):
        append = self.__all__.append
        for o in args:
            name = getattr(o, '__name__', None)
            if name:
                append(name)
                continue
            if not isinstance(o, str):
                raise TypeError("{o} isn't a string and doesn't have a __name__")
            append(o)
        if len(args) == 1:
            return args[0]

    def delete(self, *args):
        append = self.deletions.append
        for o in args:
            name = getattr(o, '__name__', None)
            if name:
                append(name)
                continue
            if not isinstance(o, str):
                raise TypeError("{o} isn't a string and doesn't have a __name__")
            append(o)
        if len(args) == 1:
            return args[0]

    def clean(self):
        import sys
        frame = sys._getframe(1)
        for name in self.deletions:
            del frame.f_locals[name]


mm = ModuleManager()
export = mm.export
delete = mm.delete
clean  = mm.clean
delete('mm', 'export', 'delete', 'clean')
__all__ = mm.__all__

export(ModuleManager)

from functools import update_wrapper
from inspect import signature

from types import SimpleNamespace as namespace
export('namespace')


@export
def try_float(o):
    """
    Returns True if o can be converted into a float,
    and False if it can't.
    """
    try:
        float(o)
        return True
    except (TypeError, ValueError):
        return False

@export
def try_int(o):
    """
    Returns True if o can be converted into an int,
    and False if it can't.
    """
    try:
        int(o)
        return True
    except (TypeError, ValueError):
        return False

_sentinel = object()

@export
def get_float(o, default=_sentinel):
    """
    Returns float(o), unless that conversion fails,
    in which case returns the default value.  If
    you don't pass in an explicit default value,
    the default value is o.
    """
    try:
        return float(o)
    except (TypeError, ValueError):
        if default != _sentinel:
            return default
        return o

@export
def get_int(o, default=_sentinel):
    """
    Returns int(o), unless that conversion fails,
    in which case returns the default value.  If
    you don't pass in an explicit default value,
    the default value is o.
    """
    try:
        return int(o)
    except (TypeError, ValueError):
        if default != _sentinel:
            return default
        return o

@export
def get_int_or_float(o, default=_sentinel):
    """
    Converts o into a number, preferring an int to a float.

    If o is already an int, return o unchanged.
    If o is already a float, if int(o) == o, return int(o),
      otherwise return o.
    Otherwise, tries int(o).  If that conversion succeeds,
    returns the result.
    Failing that, tries float(o).  If that conversion succeeds,
    returns the result.
    If all else fails, returns the default value.  If you don't
    pass in an explicit default value, the default value is o.
    """
    if isinstance(o, int):
        return o
    if isinstance(o, float):
        int_o = int(o)
        if int_o == o:
            return int_o
        return o
    try:
        return int(o)
    except (TypeError, ValueError):
        try:
            # if you pass in the *string* "0.0",
            # this will return 0, not 0.0.
            return get_int_or_float(float(o))
        except (TypeError, ValueError):
            if default != _sentinel:
                return default
            return o

@export
def pure_virtual():
    """
    Decorator for pure virtual methods.  Calling a method
    decorated with this raises a NotImplementedError exception.
    """
    def pure_virtual(fn):
        def wrapper(self, *args, **kwargs):
            raise NotImplementedError(f"pure virtual method {fn.__name__} called")
        update_wrapper(wrapper, fn)
        wrapper.__signature__ = signature(fn)
        return wrapper
    return pure_virtual


@export
class ClassRegistry(dict):
    """
    A dict subclass with attribute-style access used as a class decorator.

    Python's scoping rules make it clumsy to work with heavily-nested classes.
    ClassRegistry makes it easy to reference base classes in a different class
    scope for easier subclassing.  To use:
        1. Create a ClassRegistry object.
        2. Decorate the base classes you need with a call to that instance.
        3. Access those base classes as attributes on the ClassRegistry.

    By default the name of the class is used as the name of the attribute.
    You can specify a custom name by passing it in an argument to the instance
    when you decorate the class.

    Example:
        # 1. Create a registry
        base = ClassRegistry()

        # 2. Register a class using the decorator
        @base()
        class Dingus:
            pass

        # 3. Access that class as an attribute on the registry
        class Doodad(base.Dingus):
            pass

        # Register using a custom name
        @base('MyName')
        class SomeClass:
            pass

        # Access via that custom name
        class Other(base.MyName):
            pass

    When using with BoundInnerClass, put @base() above @BoundInnerClass:

        @base()
        @BoundInnerClass
        class Transaction(base.Signaling):
            pass
    """

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name) from None

    def __call__(self, name=None):
        """Decorator factory to register a class."""
        def decorator(cls):
            key = name if name is not None else cls.__name__
            self[key] = cls
            return cls
        return decorator

clean()
