#!/usr/bin/env python
#
# test_rangeslider.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx
import pwidgets.floatslider as fltsld

import pwidgets.rangeslider as rngsld

import logging
        
if __name__ == '__main__':

    logging.basicConfig()
    logging.getLogger('pwidgets.rangeslider').setLevel(logging.DEBUG)

    app   = wx.App()
    frame = wx.Frame(None)
    sizer = wx.BoxSizer(wx.VERTICAL)
    frame.SetSizer(sizer)

    style = (rngsld.RSSP_SHOW_LIMITS |
             rngsld.RSSP_EDIT_LIMITS |
             rngsld.RSSP_MOUSEWHEEL)
    
    slider = rngsld.RangeSliderSpinPanel(
        frame,
        minValue=0,
        maxValue=100,
        lowValue=0,
        highValue=100,
        minDistance=5,
        lowLabel='Low',
        highLabel='High',
        style=style)

    sizer.Add(slider, flag=wx.EXPAND)

    centreCheck  = wx.CheckBox(frame)
    centreSlider = fltsld.FloatSlider(frame,value=50, minValue=0, maxValue=100)
    
    sizer.Add(centreCheck,  flag=wx.EXPAND)
    sizer.Add(centreSlider, flag=wx.EXPAND)


    def _range(ev):
        print 'Range: {} {}'.format(ev.low, ev.high)

    def _limit(ev):
        print 'Limit: {} {}'.format(ev.min, ev.max)
        centreSlider.SetRange(ev.min, ev.max)


    def _centreToggle(ev):
        if centreCheck.GetValue():
            print 'Centering range at {}'.format(centreSlider.GetValue())
            slider.CentreAt(centreSlider.GetValue())
        else:
            print 'De-centering range'
            slider.CentreAt(None)

    def _centreSlider(ev):
        _centreToggle(ev)
    
       
    slider.Bind(rngsld.EVT_RANGE,       _range)
    slider.Bind(rngsld.EVT_LOW_RANGE,   _range)
    slider.Bind(rngsld.EVT_HIGH_RANGE,  _range)
    slider.Bind(rngsld.EVT_RANGE_LIMIT, _limit)

    centreCheck .Bind(wx.EVT_CHECKBOX, _centreToggle)
    centreSlider.Bind(wx.EVT_SLIDER,   _centreSlider)
    
    frame.Layout()
    frame.Show()
    app.MainLoop()
