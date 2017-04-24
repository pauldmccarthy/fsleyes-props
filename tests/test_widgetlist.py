#!/usr/bin/env python
#
# test_widgetlist.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx
import props
props.initGUI()

import fsleyes_widgets.widgetlist as wl


        
if __name__ == '__main__':

    class Test(props.HasProperties):
        myint    = props.Int()
        mybool   = props.Boolean()
        myreal   = props.Real(minval=0, maxval=10, clamped=True)
        mystring = props.String()
        mybounds = props.Bounds(ndims=2)

        myreal2    = props.Real(minval=0, maxval=10, clamped=True)
        myreal3    = props.Real(minval=0, maxval=10, clamped=True)
        mystring2  = props.String()
        mystring3  = props.String()
        mybool2    = props.Boolean()
        myint2     = props.Boolean()


    testObj = Test()
    testObj.mybounds.xmin = 0
    testObj.mybounds.xmax = 10
    testObj.mybounds.ymin = 10
    testObj.mybounds.ymax = 20 
    app     = wx.App()
    frame   = wx.Frame(None)
    wlist   = wl.WidgetList(frame)

    widg = wx.TextCtrl(wlist)
    widg.SetValue('Bah, humbug!')

    wlist.AddWidget(props.makeWidget(wlist, testObj, 'myint'), 'My int')
    wlist.AddWidget(props.makeWidget(wlist, testObj, 'mybool'), 'mybool')
    wlist.AddWidget(
        props.makeWidget(wlist, testObj, 'myreal',
                         showLimits=False, spin=False),
        'My real')
    wlist.AddWidget(props.makeWidget(wlist, testObj, 'mystring'), 'mystring')

    wlist.AddWidget(widg, 'My widget')
    
    wlist.AddGroup('extra1', 'Extras 1')
    wlist.AddGroup('extra2', 'Extras 2')
    
    wlist.AddWidget(
        props.makeWidget(wlist, testObj, 'myreal2', showLimits=False),
        'myreal2', groupName='extra1')
    wlist.AddWidget(
        props.makeWidget(wlist, testObj, 'myreal3', spin=False),
        'myreal3', groupName='extra1')
    wlist.AddWidget(
        props.makeWidget(wlist, testObj, 'mystring2'),
        'mystring2', groupName='extra1')
    wlist.AddWidget(
        props.makeWidget(wlist, testObj, 'mybounds', showLimits=False),
        'My bounds, hur', groupName='extra1', )
    wlist.AddWidget(
        props.makeWidget(wlist, testObj, 'mystring3'),
        'mystring3', groupName='extra2')
    wlist.AddWidget(
        props.makeWidget(wlist, testObj, 'mybool2'),
        'mybool2', groupName='extra2')
    wlist.AddWidget(
        props.makeWidget(wlist, testObj, 'myint2'),
        'myint2', groupName='extra2')

    frame.Layout()
    frame.Fit()

    frame.SetSize((300, 300))
    frame.Show()
    app.MainLoop()
