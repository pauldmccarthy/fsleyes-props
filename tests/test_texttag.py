#!/usr/bin/env python
#
# test_texttag.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx

import pwidgets.texttag as texttag


app      = wx.App()
frame    = wx.Frame(None)
sizer    = wx.BoxSizer(wx.HORIZONTAL)
tagpanel = texttag.TextTagPanel(frame,
                                style=(texttag.TTP_ALLOW_NEW_TAGS |
                                       texttag.TTP_ADD_NEW_TAGS   |
                                       texttag.TTP_NO_DUPLICATES))

tagpanel.SetOptions(('signal', 'noise', 'grey matter'))

tagpanel.SetBackgroundColour((255, 255, 255))

sizer.Add(tagpanel, flag=wx.EXPAND, proportion=1)

frame.SetSizer(sizer)
frame.SetSize((600, 400))
frame.Layout()

frame.Show()
app.MainLoop()
