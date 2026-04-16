#!/usr/bin/env python
#
# test_widget_string.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

from . import (run_with_wx, addall, realYield)

import fsleyes_props as props


def setup_module():
    props.initGUI()


class MyObj(props.HasProperties):
    mytext = props.String()


def  test_widget_string(): run_with_wx(_test_widget_string)
def _test_widget_string(parent):

    obj        = MyObj()
    obj.mytext = 'value1'
    myetext    = props.makeWidget(parent, obj, 'mytext')
    mystext    = props.makeWidget(parent, obj, 'mytext', static=True)

    addall(parent, [myetext, mystext])

    assert myetext.GetValue() == 'value1'
    assert mystext.GetLabel() == 'value1'

    obj.mytext = 'value2'

    assert myetext.GetValue() == 'value2'
    assert mystext.GetLabel() == 'value2'

    # TextCtrl.SetValue should cause
    # a EVT_TEXT event to be emited
    myetext.SetValue('value3')

    realYield()

    assert obj.mytext         == 'value3'
    assert myetext.GetValue() == 'value3'
    assert mystext.GetLabel() == 'value3'
