#!/usr/bin/env python

import fsleyes_props as props

def test_bindable():
    class Thing(props.HasProps):
        myint = props.Int()
        mystr = props.String()

    for order in ('backwards',' forwards'):

        t1, t2 = [Thing(), Thing()]

        t1.myint = 123
        t2.myint = 456
        t1.mystr = '123'
        t2.mystr = '456'

        assert t1.myint == 123
        assert t2.myint == 456
        assert t1.mystr == '123'
        assert t2.mystr == '456'

        assert not t1.isBound('myint', t2)
        assert not t2.isBound('myint', t1)
        assert not t1.isBound('mystr', t2)
        assert not t2.isBound('mystr', t1)

        if order == 'backwards':
            t1.bindProps('myint', t2)
            t1.bindProps('mystr', t2)
        else:
            t2.bindProps('myint', t1)
            t2.bindProps('mystr', t1)

        assert t1.isBound('myint', t2)
        assert t2.isBound('myint', t1)
        assert t1.isBound('mystr', t2)
        assert t2.isBound('mystr', t1)

        if order == 'backwards': expint, expstr = 456, '456'
        else:                    expint, expstr = 123, '123'

        assert t1.myint == expint
        assert t2.myint == expint
        assert t1.mystr == expstr
        assert t2.mystr == expstr

        t1.unbindProps('myint', t2)
        t1.unbindProps('mystr', t2)

        assert not t1.isBound('myint', t2)
        assert not t2.isBound('myint', t1)
        assert not t1.isBound('mystr', t2)
        assert not t2.isBound('mystr', t1)

        t1.myint = 333
        t2.myint = 999
        t1.mystr = 'abc'
        t2.mystr = 'def'

        assert t1.myint == 333
        assert t2.myint == 999
        assert t1.mystr == 'abc'
        assert t2.mystr == 'def'
