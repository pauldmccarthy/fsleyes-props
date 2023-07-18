#!/usr/bin/env python


import fsleyes_props as props


def test_suppress():

    class Foo(props.Props):
        num1 = props.Int()
        num2 = props.Int()

    p = Foo()

    called = {}

    def num1Changed():
        called['num1'] = True
    def num2Changed():
        called['num2'] = True

    p.listen('num1', 'listener', num1Changed)
    p.listen('num2', 'listener', num2Changed)

    p.num1 = 1
    assert called == {'num1' : True}
    p.num2 = 1
    assert called == {'num1' : True, 'num2' : True}

    called = {}

    with props.suppress(p, 'num1'):
        p.num1 = 4
        p.num2 = 4
    assert called == {'num2' : True}

    called = {}
    with props.suppress(p, 'num1', 'num2'):
        p.num1 = 6
        p.num2 = 6
    assert called == {}

    with props.suppressAll(p):
        p.num1 = 7
        p.num2 = 7
    assert called == {}

    p.num1 = 8
    p.num2 = 8
    assert called == {'num1' : True, 'num2' : True}


def test_skip():

    class Foo(props.Props):
        num1 = props.Int()
        num2 = props.Int()

    p = Foo()

    called = {}

    def num1Changed1():
        called['num11'] = True
    def num2Changed1():
        called['num21'] = True

    def num1Changed2():
        called['num12'] = True
    def num2Changed2():
        called['num22'] = True

    p.listen('num1', 'listener1', num1Changed1)
    p.listen('num2', 'listener1', num2Changed1)
    p.listen('num1', 'listener2', num1Changed2)
    p.listen('num2', 'listener2', num2Changed2)

    p.num1 = 1
    p.num2 = 1
    assert called == {'num11' : True, 'num21' : True,
                      'num12' : True, 'num22' : True}

    called = {}
    with props.skip(p, 'num1', 'listener1'):
        p.num1 = 2
        p.num2 = 2
    assert called == {'num12' : True, 'num21' : True, 'num22' : True}

    called = {}
    with props.skip(p, 'num2', 'listener1'):
        p.num1 = 3
        p.num2 = 3
    assert called == {'num11' : True, 'num12' : True, 'num22' : True}

    called = {}
    with props.skip(p, ('num1', 'num2'), 'listener1'):
        p.num1 = 4
        p.num2 = 4
    assert called == {'num12' : True, 'num22' : True}

    called = {}
    with props.skip(p, ('num1', 'num2'), 'listener2'):
        p.num1 = 5
        p.num2 = 5
    assert called == {'num11' : True, 'num21' : True}
