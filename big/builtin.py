#!/usr/bin/env python3

_license = """
big
Copyright 2022-2024 Larry Hastings
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


__all__ = []

def export(o):
    __all__.append(o.__name__)
    return o


from functools import update_wrapper
from inspect import signature

from types import SimpleNamespace as namespace
__all__.append('namespace')


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
