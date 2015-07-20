#!/usr/bin/env python
#
# test_bindable.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx

import props

class Test(props.HasProperties):

    myString = props.String()

    myBool   = props.Boolean()

    myNum    = props.Real(clamped=True)

    myRange1 = props.Bounds(ndims=1)

    myRange2 = props.Bounds(ndims=2)


t1 = Test()
t2 = Test()

t1.myRange1.xmin = 0
t1.myRange1.xmax = 10
t1.myRange2.xmin = 0
t1.myRange2.xmax = 10
t1.myRange2.ymin = 10
t1.myRange2.ymax = 20

t1.setConstraint('myNum', 'minval', 10)
t1.setConstraint('myNum', 'maxval', 50)
t2.setConstraint('myNum', 'minval', 20)
t2.setConstraint('myNum', 'maxval', 60)

t1.myRange1.xlo  = 1
t1.myRange1.xhi  = 9
t1.myRange2.xlo  = 1
t1.myRange2.xhi  = 9
t1.myRange2.ylo  = 11
t1.myRange2.yhi  = 19

t2.myRange1.xmin = 5
t2.myRange1.xmax = 10
t2.myRange2.xmin = 10
t2.myRange2.xmax = 20
t2.myRange2.ymin = 15
t2.myRange2.ymax = 25

t2.myRange1.xlo  = 7
t2.myRange1.xhi  = 8
t2.myRange2.xlo  = 12
t2.myRange2.xhi  = 18
t2.myRange2.ylo  = 17
t2.myRange2.yhi  = 23


t1.bindProps('myRange1', t2, bindatt=False)
t1.bindProps('myRange2', t2, bindatt=False)
t1.bindProps('myNum',    t2, bindatt=False)
t1.bindProps('myBool',   t2)
t1.bindProps('myString', t2)

app    = wx.App()
frame  = wx.Frame(None)
panel1 = wx.Panel(frame)
panel2 = wx.Panel(frame)
sizer  = wx.BoxSizer(wx.VERTICAL)

props.buildGUI(panel1, t1)
props.buildGUI(panel2, t2)

frame.SetSizer(sizer)
sizer.Add(panel1, flag=wx.EXPAND, proportion=1)
sizer.Add(panel2, flag=wx.EXPAND, proportion=1)

frame.Layout()
frame.Show()

app.MainLoop()
