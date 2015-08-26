#!/usr/bin/env python
#
# widgets_boolean.py - Generate a widget to control a Boolean property.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :func:`_Boolean` function, which is imported into
the :mod:`widgets` module namespace. It is separated purely to keep the
``widgets`` module file size down.
"""


import wx

import widgets

import pwidgets.bitmapradio  as bmpradio
import pwidgets.bitmaptoggle as bmptoggle


def _Boolean(parent,
             hasProps,
             propObj,
             propVal,
             icon=None,
             toggle=False,
             style=None,
             **kwargs):
    """Creates and returns a ``wx.CheckBox``, allowing the user to set the
    given :class:`.Boolean` property value.

    If the ``icon`` argument is provided, it should be a string containing the
    name of an image file, or a list of two image file names.  In the former
    case, a ``wx.ToggleButton`` is used instead of a ``CheckBox``.

    If two icon images are provided, and the ``toggle`` argument is ``True``,
    a :class:`.BitmapToggleButton` is used. If ``toggle=False``, a
    :class:`.BitmapRadioBox` is used instead.  In the latter case, the
    ``style`` argument is passed through to the
    :meth:`.BitmapRadioBox.__init__` method.

    See the :func:`.widgets._String` documentation for details on the other
    parameters.
    """

    widgetGet = None
    widgetSet = None

    if icon is None:
        widget = wx.CheckBox(parent)
        event  = wx.EVT_CHECKBOX
        
    elif isinstance(icon, basestring):

        # Load the bitmap using this two-stage
        # approach, because under OSX, any other
        # way will not load the retina '@2x'
        # icon version (if it is present).
        bmp = wx.EmptyBitmap(1, 1)
        bmp.LoadFile(icon, wx.BITMAP_TYPE_PNG)

        # Gaargh. Under OSX the BU_NOTEXT style
        # causes a segmentation fault - wtf??
        # I have to live with the button bitmap
        # being slightly off centre (a gap is
        # left to display the empty label)
        if wx.Platform == '__WXMAC__':
            widget = wx.ToggleButton(parent, style=wx.BU_EXACTFIT)
        else:
            widget = wx.ToggleButton(parent,
                                     style=wx.BU_EXACTFIT | wx.BU_NOTEXT)
        event  = wx.EVT_TOGGLEBUTTON
        
        widget.SetBitmap(bmp)
        widget.SetBitmapMargins(0, 0)

    else:
        trueBmp  = wx.EmptyBitmap(1, 1)
        falseBmp = wx.EmptyBitmap(1, 1)

        trueBmp .LoadFile(icon[0], wx.BITMAP_TYPE_PNG)
        falseBmp.LoadFile(icon[1], wx.BITMAP_TYPE_PNG)

        if toggle:
            widget = bmptoggle.BitmapToggleButton(parent, trueBmp, falseBmp)
            event  = bmptoggle.EVT_BITMAP_TOGGLE_EVENT
        else:
            widget = bmpradio.BitmapRadioBox(parent, style)
            event  = bmpradio.EVT_BITMAP_RADIO_EVENT

            widget.AddChoice(trueBmp)
            widget.AddChoice(falseBmp)

            def widgetGet():
                return widget.GetSelection() == 0

            def widgetSet(val):
                if val: widget.SetSelection(0)
                else:   widget.SetSelection(1)
            
    widgets._propBind(hasProps,
                      propObj,
                      propVal,
                      widget,
                      event,
                      widgetGet=widgetGet,
                      widgetSet=widgetSet)
    return widget
