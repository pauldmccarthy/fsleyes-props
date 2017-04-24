#!/usr/bin/env python
#
# test_texttag.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

from __future__ import print_function

import logging
logging.basicConfig(
    format='%(levelname)8.8s '
           '%(filename)20.20s '
           '%(lineno)4d: '
           '%(funcName)-15.15s - '
           '%(message)s')

logging.getLogger('fsleyes_widgets').setLevel(logging.DEBUG)

import wx

import fsleyes_widgets.texttag      as texttag
import fsleyes_widgets.autotextctrl as autotextctrl


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

sizer.Add(wx.StaticText(frame, label='Tag panel 1 (allow+add+nodup+keynav)'), flag=wx.EXPAND)
sizer.Add(tagpanel1, flag=wx.EXPAND)
sizer.Add(wx.StaticText(frame, label='Tag panel 2 (allow+nodup)'), flag=wx.EXPAND)
sizer.Add(tagpanel2, flag=wx.EXPAND)
sizer.Add(wx.StaticText(frame, label='Tag panel 3 (nodup+casesense'), flag=wx.EXPAND)
sizer.Add(tagpanel3, flag=wx.EXPAND)
sizer.Add(wx.StaticText(frame, label='AutoTextCtrl'), flag=wx.EXPAND)
sizer.Add(atc,       flag=wx.EXPAND)
sizer.Add(wx.StaticText(frame, label='wx.TextCtrl (with auto complete)'), flag=wx.EXPAND)
sizer.Add(tc,        flag=wx.EXPAND)


opttext = '\n'.join([
    '\t'.join(options[  :5]),
    '\t'.join(options[ 5:10]),
    '\t'.join(options[10:15]),
    '\t'.join(options[15:20]),
    '\t'.join(options[20:])])



sizer.Add(wx.StaticText(frame, label='Options:\n\n{}'.format(opttext)))

frame.SetSizer(sizer)
frame.SetSize((600, 400))
frame.Layout()



def anychar(ev):
    ev.Skip()
    key = ev.GetKeyCode()
    focused = wx.Window.FindFocus()
    print('Character {} on window {}'.format(key, focused))
    

frame.Bind(wx.EVT_CHAR_HOOK, anychar)

frame.Show()
app.MainLoop()
