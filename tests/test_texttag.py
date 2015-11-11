#!/usr/bin/env python
#
# test_texttag.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import logging
logging.basicConfig(
    format='%(levelname)8.8s '
           '%(filename)20.20s '
           '%(lineno)4d: '
           '%(funcName)-15.15s - '
           '%(message)s')

logging.getLogger('pwidgets').setLevel(logging.DEBUG)

import wx

import pwidgets.texttag      as texttag
import pwidgets.autotextctrl as autotextctrl


options = ['Signal',
           'sign',
           'Sausage',
           'sasquatch',
           'Seepage',
           'silly',
           'Sumptuous',
           'noise',
           'Nose',
           'nobby',
           'Noddy',
           'nibble',
           'No',
           'not',
           'Never'
           'grey matter',
           'Green',
           'gooey',
           'Gabbo',
           'gummy',
           'Great',
           'great',
           'Great',
           'GrEAT',
           'GREAT']

app       = wx.App()
frame     = wx.Frame(None)
sizer     = wx.BoxSizer(wx.VERTICAL)

tagpanel1 = texttag.TextTagPanel(frame,
                                 style=(texttag.TTP_ALLOW_NEW_TAGS |
                                        texttag.TTP_ADD_NEW_TAGS   |
                                        texttag.TTP_NO_DUPLICATES  |
                                        texttag.TTP_KEYBOARD_NAV))
tagpanel2 = texttag.TextTagPanel(frame,
                                 style=(texttag.TTP_ALLOW_NEW_TAGS |
                                        texttag.TTP_NO_DUPLICATES))
tagpanel3 = texttag.TextTagPanel(frame,
                                 style=(texttag.TTP_NO_DUPLICATES |
                                        texttag.TTP_CASE_SENSITIVE))
atc       = autotextctrl.AutoTextCtrl(frame)
tc        = wx.TextCtrl(frame)

tagpanel1.SetOptions(  options)
tagpanel2.SetOptions(  options)
tagpanel3.SetOptions(  options)
atc      .AutoComplete(options)
tc       .AutoComplete(options)

sizer.Add(tagpanel1, flag=wx.EXPAND)
sizer.Add(tagpanel2, flag=wx.EXPAND)
sizer.Add(tagpanel3, flag=wx.EXPAND)
sizer.Add(atc,       flag=wx.EXPAND)
sizer.Add(tc,        flag=wx.EXPAND)

frame.SetSizer(sizer)
frame.SetSize((600, 400))
frame.Layout()

frame.Show()
app.MainLoop()
