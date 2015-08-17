#!/usr/bin/env python
#
# test.py -
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

logging.getLogger('props').setLevel(logging.DEBUG)


import wx

import numpy as np

import props
props.initGUI()
import pwidgets.elistbox as elistbox

class Bag(props.HasProperties):
    mob = props.Choice()

    
bag     = Bag()
cprop   = bag.getProp('mob')
app     = wx.App()
frame   = wx.Frame(None)
panel   = wx.Panel(frame)
pSizer  = wx.BoxSizer(wx.VERTICAL)
fSizer  = wx.BoxSizer(wx.VERTICAL)
choice  = props.makeWidget(panel, bag, 'mob')
listbox = elistbox.EditableListBox(panel, style=elistbox.ELB_EDITABLE)


pSizer.Add(listbox, flag=wx.EXPAND, proportion=1)
pSizer.Add(choice,  flag=wx.EXPAND)

fSizer.Add(panel,   flag=wx.EXPAND, proportion=1)

panel.SetSizer(pSizer)
frame.SetSizer(fSizer)

frame.SetSize((500, 500))
frame.Layout()
frame.Show()



def lbAdd(ev):

    print 'Listbox add    - choice value before: {}'.format(bag.mob)
    
    n   = str(np.random.randint(1, 1000))
    lbl = 'New choice {}'.format(n)
    
    cprop.addChoice(n, label=lbl, alternate=[lbl], instance=bag)
    listbox.Append(lbl, n)

    print '                 choice value after:  {}'.format(bag.mob)

    
def lbRemove(ev):
    print 'Listbox remove - choice value before: {}'.format(bag.mob)
    cprop.removeChoice(ev.data, instance=bag)
    print '                 choice value after:  {}'.format(bag.mob)


def lbMove(ev):
    print 'Listbox move   - choice value before: {}'.format(bag.mob)
    labels     = listbox.GetLabels()
    choices    = listbox.GetData()
    alternates = [[lbl] for choice, lbl in zip(choices, labels)]
    cprop.setChoices(choices,
                     labels=labels,
                     alternates=alternates,
                     instance=bag)
    print '                 choice value after:  {}'.format(bag.mob)


def lbEdit(ev):

    print 'Listbox edit   - choice value before: {}'.format(bag.mob)
    choice   = ev.data
    newLabel = ev.label
    newAlt   = [newLabel]
    cprop.updateChoice(choice, newLabel=newLabel, newAlt=newAlt, instance=bag)
    print '                 choice value after:  {}'.format(bag.mob)


def lbSelect(ev):
    print 'Listbox select - choice value before: {}'.format(bag.mob)
    if np.random.random(1) >= 0.5: val = ev.data
    else:                          val = ev.label

    print 'Setting value to {}'.format(val)
    bag.mob = val

    print '                 choice value after:  {}'.format(bag.mob)



listbox.Bind(elistbox.EVT_ELB_ADD_EVENT,    lbAdd)
listbox.Bind(elistbox.EVT_ELB_REMOVE_EVENT, lbRemove)
listbox.Bind(elistbox.EVT_ELB_MOVE_EVENT,   lbMove)
listbox.Bind(elistbox.EVT_ELB_EDIT_EVENT,   lbEdit)
listbox.Bind(elistbox.EVT_ELB_SELECT_EVENT, lbSelect)
             
app.MainLoop()
