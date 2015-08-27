#!/usr/bin/env python
#
# test_number_dialog.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx
import pwidgets.numberdialog as numdlg


if __name__ == '__main__':

    app    = wx.App()
    frame  = wx.Frame(None)
    panel  = wx.Panel(frame)
    sizer  = wx.BoxSizer(wx.HORIZONTAL)
    button = wx.Button(panel, label='Show dialog!')

    sizer.Add(button, flag=wx.EXPAND)
    panel.SetSizer(sizer)


    def _showDlg(ev):
        dlg = numdlg.NumberDialog(
            frame,
            real=True,
            title='Enter number',
            message='Enter a number between 0 and 100',
            initial=20,
            minValue=0,
            maxValue=100)

        if dlg.ShowModal() != wx.ID_OK:
            print 'Not ok'
        else:
            print 'Number entered: {}'.format(dlg.GetValue())


    button.Bind(wx.EVT_BUTTON, _showDlg)

    frame.Show()
    app.MainLoop()
