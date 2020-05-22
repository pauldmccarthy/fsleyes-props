#!/usr/bin/env python
#
# test_widget_boolean.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import os.path as op
import wx

import fsleyes_props                as props
import fsleyes_widgets.bitmaptoggle as bmptoggle
import fsleyes_widgets.bitmapradio  as bmpradio

from . import run_with_wx, addall, realYield


datadir = op.join(op.dirname(__file__), 'testdata')


def setup_module():
    props.initGUI()


class MyObj(props.HasProperties):
    mybool = props.Boolean()


def  test_widget_boolean(): run_with_wx(_test_widget_boolean)
def _test_widget_boolean(parent):

    trueicon  = op.join(datadir, 'true.png')
    falseicon = op.join(datadir, 'false.png')

    obj = MyObj()

    # ch
    myboolcb  = props.makeWidget(parent, obj, 'mybool')
    mybooltog = props.makeWidget(parent, obj, 'mybool',
                                 icon=[trueicon, falseicon])
    myboolrad = props.makeWidget(parent, obj, 'mybool',
                                 icon=[trueicon, falseicon],
                                 toggle=False)

    assert isinstance(myboolcb,  wx.CheckBox)
    assert isinstance(mybooltog, bmptoggle.BitmapToggleButton)
    assert isinstance(myboolrad, bmpradio .BitmapRadioBox)

    addall(parent, (myboolcb, mybooltog, myboolrad))

    obj.mybool = False

    assert not myboolcb .GetValue()
    assert not mybooltog.GetValue()
    assert myboolrad.GetSelection() == 1
    obj.mybool = True

    assert myboolcb .GetValue()
    assert mybooltog.GetValue()
    assert myboolrad.GetSelection() == 0

    myboolcb.SetValue(False)
    wx.PostEvent(myboolcb, wx.CommandEvent(wx.EVT_CHECKBOX.evtType[0]))
    realYield()
    assert not obj.mybool
    assert not myboolcb .GetValue()
    assert not mybooltog.GetValue()
    assert myboolrad.GetSelection() == 1

    myboolcb.SetValue(True)
    wx.PostEvent(myboolcb, wx.CommandEvent(wx.EVT_CHECKBOX.evtType[0]))
    realYield()
    assert obj.mybool
    assert myboolcb .GetValue()
    assert mybooltog.GetValue()
    assert myboolrad.GetSelection() == 0
