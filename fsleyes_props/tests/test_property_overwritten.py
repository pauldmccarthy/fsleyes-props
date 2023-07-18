#!/usr/bin/env python


import fsleyes_props as props

class Base(props.Props):
    thing = props.Choice((1, 2, 3))


class Sub(Base):
    thing = props.Choice((4, 5, 6))

# fsl/fsleyes/props!58
def test_property_overwritten():
    b = Base()
    s = Sub()

    assert Base.thing.getChoices()  == [1, 2, 3]
    assert Base.thing.getChoices(b) == [1, 2, 3]
    assert Sub .thing.getChoices()  == [4, 5, 6]
    assert Sub .thing.getChoices(s) == [4, 5, 6]
