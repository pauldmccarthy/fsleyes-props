#!/usr/bin/env python
#
# test_rangeslider.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx
import pwidgets.rangeslider as rngsld
        
        
if __name__ == '__main__':

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

    def _range(ev):
        print 'Range: {} {}'.format(ev.low, ev.high)

    def _limit(ev):
        print 'Limit: {} {}'.format(ev.min, ev.max)
    
       
    slider.Bind(rngsld.EVT_RANGE,       _range)
    slider.Bind(rngsld.EVT_RANGE_LIMIT, _limit)
    
    frame.Layout()
    frame.Show()
    app.MainLoop()
