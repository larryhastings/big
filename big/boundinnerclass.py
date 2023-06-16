#!/usr/bin/env python3

_license = """
big
Copyright 2022-2023 Larry Hastings
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

#
# If you have a class with an inner class inside,
# decorate the inner class with BoundInnerClass below
# and now it'll automatically get a second parameter
# of the parent instance!
# _______________________________________
#
# class Outer:
#   @BoundInnerClass
#   class Inner:
#       def __init__(self, outer):
#           global o
#           print(outer = o)
# o = Outer()
# i = o.Inner()
# _______________________________________
#
# This program prints True.  The "outer" parameter
# to Inner.__init__ was filled in automatically by
# the BoundInnerClass decorator.
#
# Thanks, BoundInnerClass, you've saved the day!
#
# -----
#
# Infinite extra-special thanks to Alex Martelli for
# showing me how this could be done in the first place--
# all the way back in 2010!
#
# https://stackoverflow.com/questions/2278426/inner-classes-how-can-i-get-the-outer-class-object-at-construction-time
#
# Thanks, Alex, you've saved the day!


__all__ = ["BoundInnerClass", "UnboundInnerClass"]

import weakref

class _Worker(object):
    def __init__(self, cls):
        self.cls = cls

    def __get__(self, outer, outer_class):

        #
        # If outer is not None, we've been accessed through
        # an *instance* of the class, like so:
        #    o = Outer()
        #    ref = o.Inner
        #
        # See:
        #    https://docs.python.org/3/howto/descriptor.html#invocation-from-an-instance
        #
        #
        # If outer is None, we've been accessed through the *class itself*,
        # like so:
        #    ref = Outer.Inner
        #
        # See:
        #    https://docs.python.org/3/howto/descriptor.html#invocation-from-a-class
        #
        # If someone accesses us through the class, not through an instance,
        # return the unbound version of the class.
        #
        if outer is None:
            return self.cls

        name = self.cls.__name__

        wrapper_bases = [self.cls]

        # Iterate over cls's bases, and look in outer,
        #   to see if any have bound inner classes in outer.
        # If so, multiply inherit from the bound inner version(s).

        multiply_inherit = False
        for base in self.cls.__bases__:
            # If we can't find a bound inner base,
            # add the original unbound base instead.
            # this is harmless but helps preserve the original MRO.
            inherit_from = base

            # If we inherit from a BoundInnerClass from another outer class,
            # we *might* have the same name as a legitimate base class.
            # But if we get that attribute, we'll call __get__ recursively...
            # forever.
            #
            # If the name is the same as our own name, there's no way it's
            # a bound inner class we need to inherit from, so just skip it.
            if base.__name__ != name:
                bound_inner_base = getattr(outer, base.__name__, None)
                if bound_inner_base:
                    bases = getattr(bound_inner_base, "__bases__", (None,))
                    # The unbound class is always the first base of
                    # the bound inner class.
                    if bases[0] == base:
                        inherit_from = bound_inner_base
                        multiply_inherit = True
            wrapper_bases.append(inherit_from)

        Wrapper = self._wrap(outer, wrapper_bases[0])
        Wrapper.__name__ = name

        # Assigning to __bases__ is startling, but it's the only way to get
        # this code working simultaneously in both Python 2 and Python 3.
        if multiply_inherit:
            Wrapper.__bases__ = tuple(wrapper_bases)

        # Cache the bound instance in outer's dict.
        # This also means that future requests for us won't call our
        # __get__ again, it'll automatically use the cached copy.
        outer.__dict__[name] = Wrapper
        return Wrapper


class BoundInnerClass(_Worker):
    """
    Class decorator for an inner class.  When accessing the inner class
    through an instance of the outer class, "binds" the inner class to
    the instance.  This changes the signature of the inner class's __init__
    from

        def __init__(self, *args, **kwargs):

    to

        def __init__(self, outer, *args, **kwargs):

    where "outer" is the instance of the outer class.

    Note that this has an implication for all subclasses.
    If class B is decorated with BoundInnerClass, and class
    S is a subclass of B, such that issubclass(S, B) returns True,
    class S must be decorated with either BoundInnerClass
    or UnboundInnerClass.
    """
    def _wrap(self, outer, base):
        wrapper_self = self
        assert outer is not None
        outer_weakref = weakref.ref(outer)
        class Wrapper(base):
            def __init__(self, *bic_args, **bic_kwargs):
                wrapper_self.cls.__init__(self,
                                          outer_weakref(), *bic_args, **bic_kwargs)

            # give the bound inner class a nicer repr
            # (but only if it doesn't already have a custom repr)
            if wrapper_self.cls.__repr__ is object.__repr__:
                def __repr__(self):
                    return "".join([
                        "<",
                        wrapper_self.cls.__module__,
                        ".",
                        self.__class__.__name__,
                        " object bound to ",
                        repr(outer_weakref()),
                        " at ",
                        hex(id(self)),
                        ">"])
        Wrapper.__name__ = self.cls.__name__
        Wrapper.__module__ = self.cls.__module__
        Wrapper.__qualname__ = self.cls.__qualname__
        Wrapper.__doc__ = self.cls.__doc__
        if hasattr(self.cls, '__annotations__'):
            Wrapper.__annotations__ = self.cls.__annotations__
        return Wrapper


class UnboundInnerClass(_Worker):
    """
    Class decorator for an inner class that prevents binding
    the inner class to an instance of the outer class.

    If class B is decorated with BoundInnerClass, and class
    S is a subclass of B, such that issubclass(S, B) returns True,
    class S must be decorated with either BoundInnerClass
    or UnboundInnerClass.
    """
    def _wrap(self, outer, base):
        class Wrapper(base):
            pass
        Wrapper.__name__ = self.cls.__name__
        Wrapper.__module__ = self.cls.__module__
        Wrapper.__qualname__ = self.cls.__qualname__
        Wrapper.__doc__ = self.cls.__doc__
        if hasattr(self.cls, '__annotations__'):
            Wrapper.__annotations__ = self.cls.__annotations__
        return Wrapper
