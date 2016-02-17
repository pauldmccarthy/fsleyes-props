#!/usr/bin/env python
#
# test_elistbox.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import logging

import random

import wx

import pwidgets.elistbox as elistbox


logging.basicConfig(
    format='%(levelname)8s '
           '%(filename)20s '
           '%(lineno)4d: '
           '%(funcName)s - '
           '%(message)s',
    level=logging.DEBUG)


items   = list(map(str, range(5)))
tips    = ['--{}--'.format(i) for i in items]

app     = wx.App()
frame   = wx.Frame(None)
panel   = wx.Panel(frame)
listbox = elistbox.EditableListBox(
    panel,
    items,
    tooltips=tips,
    style=(elistbox.ELB_REVERSE    |
           elistbox.ELB_TOOLTIP    |
           elistbox.ELB_EDITABLE))

panelSizer = wx.BoxSizer(wx.HORIZONTAL)
panel.SetSizer(panelSizer)
panelSizer.Add(listbox, flag=wx.EXPAND, proportion=1)

frameSizer = wx.BoxSizer(wx.HORIZONTAL)
frame.SetSizer(frameSizer)
frameSizer.Add(panel, flag=wx.EXPAND, proportion=1) 

frame.Show()

def addItem(ev):

    data   = random.randint(100, 200)
    widg   = wx.Button(listbox, label='Update')
    widg.toggle = False

    def onWidg(ev):

        widg.toggle = not widg.toggle
        idx    = listbox.IndexOf(data)
        if widg.toggle:
            font = wx.NORMAL_FONT.Larger().Larger().Bold().Italic()
            listbox.SetItemForegroundColour(idx, '#ff0000')
            listbox.SetItemFont(idx, font)
        else:
            listbox.SetItemForegroundColour(idx, '#000000')
            listbox.SetItemFont(idx, wx.NORMAL_FONT)

    widg.Bind(wx.EVT_BUTTON, onWidg)

    listbox.Append(
        str(data),
        data,
        tooltip='--{}--'.format(data),
        extraWidget=widg)

listbox.Bind(elistbox.EVT_ELB_ADD_EVENT, addItem)

app.MainLoop()
