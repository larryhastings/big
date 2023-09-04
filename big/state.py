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


from functools import update_wrapper
from inspect import signature

__all__ = []

def export(o):
    __all__.append(o.__name__)
    return o


@export
class State:
    """
    Base class for state machine state implementation classes.
    Use of this base class is optional; states can be instances
    of any type except types.NoneType.
    """

    def on_enter(self):
        """
        Called when entering this state.  Optional.
        """
        pass

    def on_exit(self):
        """
        Called when exiting this state.  Optional.
        """
        pass



@export
class TransitionError(RecursionError):
    """
    Exception raised when attempting to execute an illegal state transition.

    There are only two types of illegal state transitions:

    * An attempted state transition while we're in the process
      of transitioning to another state.  In other words,
      if state_manager is your StateManager object, you can't
      set state_manager.state when state_manager.next is not None.

    * An attempt to transition to the current state.
      This is illegal:
          state_manager = StateManager()
          state_manager.state = foo
          state_manager.state = foo  # <-- this statement raises TransitionError

      (Note that transitioning to a different but *identical* object
       is permitted.)
    """
    pass



@export
class StateManager:
    """
    Simple, Pythonic state machine manager.

    Has three public attributes:

        state is the current state.  You transition from
        one state to another by assigning to this attribute.

        next is the state the StateManager is transitioning to,
        if it's currently in the process of transitioning to a
        new state.  If the StateManager object isn't currently
        transitioning to a new state, its next attribute is None.
        While the manager is currently transitioning to a new
        state, it's illegal to start a second transition.  (In
        other words: you can't assign to state while next is not
        None.)

        observers is a list of callables that get called
        during any state transition.  It's initially empty.
            * The callables should accept one positional argument,
              which is the state manager.
            * Since observers are called during the state transition,
              they aren't permitted to initiate state transitions.
            * You're permitted to modify the list of observers
              at any time.  If you modify the list of observers
              from an observer call, StateManager will still use
              the old list for the remainder of that transition.

    The constructor takes the following parameters:

        state is the initial state.  It can be any valid
        state object; by default, any Python value can be a state
        except None.  (But also see the state_class parameter below.)

        on_enter represents a method call on states called when
        entering that state.  The value itself is a string used
        to look up an attribute on state objects; by default
        on_enter is the string 'on_enter', but it can be any legal
        Python identifier string or any false value.
        If on_enter is a valid identifier string, and this StateMachine
        object transitions to a state object O, and O has an attribute
        with this name, StateMachine will call that attribute (with no
        arguments) immediately after transitioning to that state.
        Passing in a false value for on_enter disables this behavior.
        on_enter is called immediately after the transition is complete,
        which means you're expressly permitted to make a state transition
        inside an on_enter call.  If defined, on_exit will be called on
        the initial state object, from inside the StateManager constructor.

        on_exit is similar to on_enter, except the attribute is
        called when transitioning *away* from a state object.
        Its default value is 'on_exit'.  on_exit is called
        *during* the state transition, which means you're expressly
        forbidden from making a state transition inside an on_exit call.

        state_class is either None or a class.  If it's a class,
        the StateManager object will require every value assigned
        to its 'state' attribute to be an instance of that class.

    To transition to a new state, assign to the 'state' attribute.

        If state_class is None, you may use *any* value as a state
        except None.

        It's illegal to assign to 'state' while currently
        transitioning to a new state.  (Or, in other words,
        at any time self.next is not None.)

        It's illegal to attempt to transition to the current
        state.  (If state_manager.state is already foo,
        setting "state_manager.state = foo" raises an exception.)

        If the current state object has an 'on_exit' attribute,
        it will be called as a function with zero arguments during
        the the transition to the next state.

        If you assign an object to 'state' that has an 'on_enter'
        attribute, it will be called as a function with zero
        arguments immediately after we have transitioned to that
        state.

    If you have an StateManager instance called "state_manager",
    and you transition it to "new_state":

        state_manager.state = new_state

    StateManager will execute the following sequence of actions:

        * Set self.next to 'new_state'.
            * At of this moment your StateManager instance is
              "transitioning" to the new state.
        * If self.state has an attribute called 'on_exit',
          call self.state.on_exit().
        * For every object 'o' in the observer list, call o(self).
        * Set self.next to None.
        * Set self.state to 'new_state'.
            * As of this moment, the transition is complete, and
              your StateManager instance is now "in" the new state.
        * If self.state has an attribute called 'on_enter',
          call self.state.on_enter().

    You may also be interested in the `accessor` and `dispatch`
    decorators in this module.
    """

    __state = None
    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, state):
        if (self.state_class is not None) and (not isinstance(state, self.state_class)):
            raise TypeError(f"invalid state object {state}, must be an instance of {self.state_class.__name__}")
        if state is None:
            raise ValueError("state can't be None")
        if self.__next is not None:
            raise TransitionError(f"can't start new state transition to {state}, still processing transition to {self.__next}")

        #
        # Use of the "is" operator is deliberate here.
        #
        # StateManager doesn't permit transitioning to the same
        # exact state *object.*  But you are explicitly permitted
        # to transition to an *identical* object... as long as it's
        # a different object.
        #
        # Why does StateManager prevent you from transitioning
        # to the same state?
        #
        #  a) Conceptually it's nonsense.  You can't "transition"
        #     to the state you're currently in.  That's akin to saying
        #     "Please travel to exactly where you are".
        #  b) Attempting to do this is almost certainly due to a bug.
        #     And you want Python to raise an exception when you have
        #     a bug... don't you?
        #
        if state is self.__state:
            raise TransitionError(f"can't transition to {state}, it's already the current state")

        self.__next = state
        # as of this moment we are "transitioning" to a new state.

        if self.on_exit:
            on_exit = getattr(self.__state, self.on_exit, None)
            if on_exit is not None:
                on_exit()
        if self.observers:
            for o in tuple(self.observers):
                o(self)

        self.__state = state
        self.__next = None
        # as of this moment we are "in" our new state, the transition is over.
        # (it's explicitly permitted to start a new state transition from inside enter().)

        if self.on_enter:
            on_enter = getattr(self.__state, self.on_enter, None)
            if on_enter is not None:
                on_enter()

    __next = None
    @property
    def next(self):
        return self.__next

    def __init__(self,
        state,
        *,
        on_enter='on_enter',
        on_exit='on_exit',
        state_class=None,
        ):
        if not ((state_class is None) or isinstance(state_class, type)):
            raise TypeError(f"state_class value {state_class} is invalid, it must either be None or a class")
        self.state_class = state_class

        if not on_enter:
            on_enter = None
        elif not (isinstance(on_enter, str) and on_enter.isidentifier()):
            raise ValueError(f'on_enter must be a string containing a valid Python identifier, not {on_enter}')
        self.on_enter = on_enter

        if not on_exit:
            on_exit = None
        elif not (isinstance(on_exit, str) and on_exit.isidentifier()):
            raise ValueError(f'on_exit must be a string containing a valid Python identifier, not {on_exit}')
        self.on_exit = on_exit

        self.observers = []
        self.state = state

    def __repr__(self):
        return f"<{type(self).__name__} state={self.state} next={self.next} observers={self.observers}>"


@export
def accessor(attribute='state', state_manager='state_manager'):
    """
    Class decorator.  Adds a convenient state accessor attribute to your class.

    Example:

        @accessor()
        class StateMachine:
            def __init__(self):
                self.state_manager = StateManager(self.InitialState)
        sm = StateMachine()

    This creates an attribute of StateMachine called "state".
    'state' behaves identically to the "state" attribute
    of the "state_manager" attribute of StateMachine.

    It evaluates to the same value:

        sm.state == sm.state_manager.state

    And setting it sets the state on the StateManager object.
    These two statements now do the same thing:

        sm.state_manager.state = new_state
        sm.state = new_state

    By default, this decorator assumes your StateManager instance
    is stored in 'state_manager', and you want to name the new
    accessor attribute 'state'.  You can override these defaults;
    the first parameter, 'attribute', is the name that will be used
    for the new accessor attribute, and the second parameter, 'state_manager',
    should be the name of the attribute where your StateManager instance
    is stored.
    """
    def accessor(cls):
        def getter(self):
            i = getattr(self, state_manager)
            return getattr(i, 'state')
        def setter(self, value):
            i = getattr(self, state_manager)
            setattr(i, 'state', value)
        setattr(cls, attribute, property(getter, setter))
        return cls
    return accessor


@export
def dispatch(state_manager='state_manager', *, prefix='', suffix=''):
    """
    Decorator for state machine event methods,
    dispatching the event from the state machine object
    to its current state.

    dispatch helps with the following scenario:
        * You have your own state machine class which contains
          a StateManager object.
        * You want your state machine class to have methods
          representing events.
        * Rather than handle those events in your state machine
          object itself, you want to dispatch them to the current
          state.

    For example, instead of writing this:

        class StateMachine:
            def __init__(self):
                self.state_manager = StateManager(self.InitialState)

            def on_sunrise(self, time, *, verbose=False):
                return self.state_manager.state.on_sunrise(time, verbose=verbose)

    you can literally write this, which does the same thing:

        class StateMachine:
            def __init__(self):
                self.state_manager = StateManager(self.InitialState)

            @dispatch()
            def on_sunrise(self, time, *, verbose=False):
                ...

    Here, the on_sunrise function you wrote is actually thrown away.
    (That's why the body is simply one "..." statement.)  Your function
    is replaced with a function that gets the "state_manager" attribute
    from self, then gets the 'state' attribute from that StateManager
    instance, then calls a method with the same name as the decorated
    function, passing in using *args and **kwargs.

    Note that, as a stylistic convention, you're encouraged to literally
    use a single ellipsis as the body of these functions, like so:

        class StateMachine:
            @dispatch()
            def on_sunrise(self, time, *, verbose=False):
                ...

    This is a visual cue to readers that the body of the function
    doesn't matter.

    The state_manager argument to the decorator should be the name of
    the attribute where the StateManager instance is stored in self.
    The default is 'state_manager'.  For example, if you store your
    state manager in the attribute 'smedley', you'd decorate with:

        @dispatch('smedley')

    The prefix and suffix arguments are strings added to the
    beginning and end of the method call we call on the current state.
    For example, if you want the method you call to have an active verb
    form (e.g. 'reset'), but you want it to directly call an event
    handler that starts with 'on_' by convention (e.g. 'on_reset'),
    you could do this:

        @dispatch(prefix='on_')
        def reset(self):
            ...

    This is equivalent to:

        def reset(self):
            return self.state_manager.state.on_reset()

    Note that you can cache the return value from calling
    dispatch and use it multiple times, like so:

        my_dispatch = dispatch('smedley', prefix='on_')

        @my_dispatch
        def reset(self):
            ...

        @my_dispatch
        def sunrise(self):
            ...

    """
    def dispatch(fn):
        def wrapper(self, *args, **kwargs):
            i = getattr(self, state_manager)
            method = getattr(i.state, f'{prefix}{fn.__name__}{suffix}')
            return method(*args, **kwargs)
        update_wrapper(wrapper, fn)
        wrapper.__signature__ = signature(fn)
        return wrapper
    return dispatch
