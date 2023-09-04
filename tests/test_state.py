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

import bigtestlib
bigtestlib.preload_local_big()


import big.all as big
from big.state import State, StateManager, accessor, dispatch, TransitionError
import collections
import sys
import unittest

class StateManagerTests(unittest.TestCase):

    def test_repr(self):
        state_manager = StateManager(1)
        self.assertEqual(repr(state_manager), '<StateManager state=1 next=None observers=[]>')


    def test_invalid_parameters(self):
        with self.assertRaises(TypeError):
            state_manager = StateManager(..., state_class=45)
        with self.assertRaises(TypeError):
            state_manager = StateManager(..., state_class='voodoo')

        with self.assertRaises(ValueError):
            state_manager = StateManager(..., on_enter=56)
        with self.assertRaises(ValueError):
            state_manager = StateManager(..., on_enter=b'goofy')
        with self.assertRaises(ValueError):
            state_manager = StateManager(..., on_enter='hey man')

        with self.assertRaises(ValueError):
            state_manager = StateManager(..., on_exit=67)
        with self.assertRaises(ValueError):
            state_manager = StateManager(..., on_exit=b'donald')
        with self.assertRaises(ValueError):
            state_manager = StateManager(..., on_exit='what\'s up')


    def test_invalid_states(self):
        state_manager = StateManager(...)
        with self.assertRaises(ValueError):
            state_manager.state = None

        state_manager = StateManager(State(), state_class=State)
        with self.assertRaises(TypeError):
            state_manager.state = 3

        state_manager = StateManager(3)
        with self.assertRaises(TransitionError):
            state_manager.state = 3


    def test_transition_inside_on_exit(self):
        state_manager = StateManager(...)
        class Stateoroonie(big.State):
            def on_exit(self):
                state_manager.state = 3
        state_manager.state = Stateoroonie()
        with self.assertRaises(TransitionError):
            state_manager.state = 4


    def test_transition_inside_observer(self):
        def malicious_observer(state_manager):
            state_manager.state = 5
        state_manager = StateManager(...)
        state_manager.observers.append(malicious_observer)
        with self.assertRaises(TransitionError):
            state_manager.state = 6


    def test_observer_is_called(self):
        seen = []
        def observer(state_manager):
            seen.append(state_manager.next)
        state_manager = StateManager(...)
        state_manager.observers.append(observer)
        for i in range(1, 6):
            state_manager.state = i
        self.assertEqual(seen, [1, 2, 3, 4, 5])


    def test_methods_as_states(self):
        @accessor('estate', 'state_manager')
        class MiamiStateMachine:
            def __init__(self):
                self.state_manager = StateManager(self.false)

            def false(self):
                return False

            def true(self):
                return True

            def toggle(self):
                self.estate = self.true if self.estate == self.false else self.false

        msm = MiamiStateMachine()
        self.assertIs(msm.estate(), False)
        msm.toggle()
        self.assertIs(msm.estate(), True)
        msm.toggle()
        self.assertIs(msm.estate(), False)


    def test_integers_as_states(self):
        @accessor()
        class IntegerStateMachine:
            def __init__(self):
                self.state_manager = StateManager(0)

            def increment(self):
                self.state += 1

        ism = IntegerStateMachine()
        for i in range(20):
            self.assertIs(ism.state, i)
            ism.increment()


    def test_on_exit_and_on_enter(self):
        methods_called = []

        @accessor()
        class StateMachine:
            def __init__(self, unittest):
                self.unittest = unittest
                self.state_manager = StateManager(self.ZerothState(self, unittest), state_class=self.MyState, on_exit='on_my_exit')

            class MyState(State):
                def __init__(self, sm, unittest):
                    self.sm = sm
                    self.unittest = unittest

            class ZerothState(MyState):
                pass

            class FirstState(MyState):
                def on_enter(self):
                    self.unittest.assertEqual(self.sm.state, self)
                    self.unittest.assertEqual(self.sm.state_manager.next, None)
                    # self.unittest.assertEqual(self.sm.state_manager.next, big.invalid_state)
                    methods_called.append('FirstState.on_enter')
                    sm.state = sm.SecondState(sm, self.unittest)

            class SecondState(MyState):
                def on_my_exit(self):
                    self.unittest.assertEqual(self.sm.state, self)
                    self.unittest.assertEqual(self.sm.state_manager.next, self.next)
                    methods_called.append('SecondState.on_exit')

                def on_enter(self):
                    self.unittest.assertEqual(self.sm.state, self)
                    self.unittest.assertEqual(self.sm.state_manager.next, None)
                    # self.unittest.assertEqual(self.sm.state_manager.next, big.invalid_state)
                    methods_called.append('SecondState.on_enter')
                    self.next = sm.ThirdState(sm, self.unittest)
                    sm.state = self.next

            class ThirdState(MyState):
                def on_my_exit(self):
                    self.unittest.assertEqual(self.sm.state, self)
                    self.unittest.assertTrue(isinstance(self.sm.state_manager.next, self.sm.FourthState))
                    methods_called.append('ThirdState.on_exit')

            class FourthState(MyState):
                pass

        sm = StateMachine(self)
        sm.state = sm.FirstState(sm, self)
        sm.state = sm.FourthState(sm, self)

        self.assertEqual(methods_called,
            [
            'FirstState.on_enter',
            'SecondState.on_enter',
            'SecondState.on_exit',
            'ThirdState.on_exit',
            ])

        with self.assertRaises(TypeError):
            sm.state = None


    def test_deactivated_on_exit_and_on_enter(self):
        class MyState(State):
            def on_enter(self): # pragma: no cover
                raise RuntimeError("this on_enter should never get called")
            def on_exit(self): # pragma: no cover
                raise RuntimeError("this on_exit should never get called")

        state_manager = StateManager(..., on_enter=None, on_exit='')
        state_manager.state = MyState()
        state_manager.state = 45


    def test_vending_machine(self):
        import decimal
        from decimal import Decimal

        decimal.getcontext().prec = 2
        Money = Decimal

        @accessor()
        class VendingMachine:
            """
            Super dumb vending machine.
            You wouldn't really write a vending machine this way,
            this is just to exercise StateManager.

            Everything in the machine has the same price;
            that price is set by the "dollars" and "cents"
            arguments to the constructor.

            Because it's just a dumb example, and because this was easier,
            the machine doesn't auto-refund the remaining balance after
            vending.  You have to call refund() after vend() to get your
            money back.
            """
            def __init__(self, price):
                self.balance = Money(0)
                self.price = price

                self.stock = collections.defaultdict(int)
                self.not_ready = self.NotReadyToVend()
                self.ready = self.ReadyToVend()
                self.state_manager = StateManager(self.not_ready,
                    state_class=self.VendingMachineState)

            def restock(self, product, count):
                assert isinstance(count, int)
                assert count > 0
                self.stock[product] += count

            def status(self):
                """
                Returns a dict containing current status
                """
                return {
                    'balance': self.balance,
                    'stock': { product: count for product, count in self.stock.items() if count },
                    'ready': self.state == self.ready,
                }

            def refund(self):
                """
                Refunds the machine's current balance.
                Returns a Money object containing the remaining balance.
                """
                if not self.balance:
                    return Money(0)
                amount = self.balance
                self.balance = Money(0)
                self.state.on_refund()
                return amount

            def insert_money(self, money):
                """
                Adds money to the machine's current balance.
                """
                assert isinstance(money, Money)
                assert money >= 0
                self.balance += money
                self.state.on_insert_money()

            @dispatch()
            def vend(self, product): # pragma: no cover
                """
                If you've put enough money in the machine,
                and the requested product is in stock,
                vends product.

                Returns the product on success
                and None for failure.
                """
                ...

            @big.BoundInnerClass
            class VendingMachineState(State):

                def __init__(self, machine):
                    self.machine = machine

                def on_refund(self): # pragma: no cover
                    pass

                def on_insert_money(self): # pragma: no cover
                    pass

                def on_vend(self, product): # pragma: no cover
                    pass

            @big.BoundInnerClass
            class NotReadyToVend(VendingMachineState.cls):
                def on_insert_money(self):
                    machine = self.machine
                    if machine.balance >= machine.price:
                        machine.state = machine.ready

                def vend(self, product):
                    return None

            @big.BoundInnerClass
            class ReadyToVend(VendingMachineState.cls):
                def on_refund(self):
                    # balance is now zero
                    machine = self.machine
                    machine.state = machine.not_ready

                def vend(self, product):
                    machine = self.machine
                    if not machine.stock[product]:
                        return None

                    machine.stock[product] -= 1
                    assert machine.stock[product] >= 0

                    machine.balance -= machine.price
                    assert machine.balance >= 0

                    if machine.balance < machine.price:
                        machine.state = machine.not_ready
                    return product

        no_money = Money(0)
        quarter = Money(1) / Money(4)
        dime = Money(1) / Money(10)
        nickel = Money(1) / Money(20)

        vm = VendingMachine(quarter + quarter + nickel)

        rc_cola = 'Royal Crown Cola'
        vm.restock(rc_cola, 12)

        squirt = 'Squirt'
        vm.restock(squirt, 1)

        self.assertEqual(vm.refund(), no_money)


        for round in range(1, 3):
            if round == 1:
                self.assertEqual(vm.status(),
                    {
                    'balance': Money(0),
                    'stock': { rc_cola: 12, squirt: 1 },
                    'ready': False,
                    }
                    )
            elif round == 2:
                self.assertEqual(vm.status(),
                    {
                    'balance': Money(0),
                    'stock': { rc_cola: 11 },
                    'ready': False,
                    }
                    )

            # not enough money yet, vending should fail
            result = vm.vend(rc_cola)
            self.assertEqual(result, None)

            vm.insert_money(quarter)
            vm.insert_money(quarter)
            vm.insert_money(nickel)

            # should vend one item now
            result = vm.vend(rc_cola)
            self.assertEqual(result, rc_cola)

            # ... but not two
            result = vm.vend(squirt)
            self.assertEqual(result, None)

            vm.insert_money(quarter)
            vm.insert_money(quarter)
            # still not enough money yet, vending should fail
            result = vm.vend(squirt)
            self.assertEqual(result, None)

            vm.insert_money(dime)
            result = vm.vend(squirt)
            change = vm.refund()

            if round == 1:
                self.assertEqual(result, squirt)
                self.assertEqual(change, nickel)
            elif round == 2:
                self.assertEqual(result, None)
                self.assertEqual(change, quarter + quarter + dime)


def run_tests():
    bigtestlib.run(name="big.state", module=__name__)


if __name__ == "__main__": # pragma: no cover
    run_tests()
    bigtestlib.finish()
