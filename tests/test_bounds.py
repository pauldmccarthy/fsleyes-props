#!/usr/bin/env python
#
# test_bounds.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
import wx

import logging

import props


class Thing(props.HasProperties):

    
    bounds       = props.Bounds(ndims=1, minDistance=0.5)
    centreBounds = props.Boolean(default=False)
    centreVal    = props.Real(minval=0, maxval=100, clamped=True)


    def __init__(self):

        self.bounds.setLimits(0, 0.0, 100.0)

        self.addListener('centreBounds',
                         'Thing_{}'.format(id(self)),
                         self.centreValChanged)

        self.addListener('centreVal',
                         'Thing_{}'.format(id(self)),
                         self.centreValChanged) 


    def centreValChanged(self, *a):

        if not self.centreBounds: val = None
        else:                     val = self.centreVal

        self.setConstraint('bounds', 'dimCentres', [val])


if __name__ == '__main__':

    props.initGUI()
    
    logging.basicConfig()
    # logging.getLogger('fsleyes_widgets.rangeslider').setLevel(logging.DEBUG)

    app   = wx.App()
    frame = wx.Frame(None)
    sizer = wx.BoxSizer(wx.VERTICAL)
    frame.SetSizer(sizer)

    specs = [props.Widget('bounds', showLimits=True, slider=True),
             props.Widget('centreBounds'),
             props.Widget('centreVal')]

    thing = Thing()

    for s in specs:
        widget = props.buildGUI(frame, thing, s)
        sizer.Add(widget, flag=wx.EXPAND)

    frame.Layout()
    frame.Show()
    app.MainLoop()
