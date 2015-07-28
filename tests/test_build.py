#!/usr/bin/env python
#
# test_build.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import logging
logging.basicConfig()

logging.getLogger('props').setLevel(logging.DEBUG)

import wx
import props


class MyObj1(props.HasProperties):
    myPropA = props.Boolean()

    
class MyObj2(props.HasProperties):
    myProp1 = props.Int()
    myProp2 = props.Real()
    myProp3 = props.Boolean()

    def __init__(self, mo1):
        self.mo1 = mo1

        
mo2View = props.VGroup((

    # myProp1 is only visible
    # when MyObj1.myPropA is True 
    props.Widget(
        'myProp1',

        # MyObj2 stores a reference to the
        # MyObj1 instance which controls
        # the state of the myProp1 widget.
        dependencies=[(lambda i: i.mo1, 'myPropA')],

        # The visibleWhen callback gets
        # passed the MyObj1 instance,
        # and the value of MyObj2.mo1.myPropA
        visibleWhen=lambda i, mo1val: mo1val),

    # myProp2 is only enabled
    # when MyObj2.myProp3 is True
    props.Widget(
        'myProp2',
        enabledWhen=lambda i: i.myProp3),

    # myProp3 is alway visible/enabled
    'myProp3'))

mo1 = MyObj1()
mo2 = MyObj2(mo1)

app      = wx.App()
mo1Frame = props.buildGUI(None, mo1)
mo2Frame = props.buildGUI(None, mo2, view=mo2View)

mo1Frame.Fit()
mo2Frame.Fit()
mo1Frame.Show()
mo2Frame.Show()
app.MainLoop()
