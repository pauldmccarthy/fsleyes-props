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
             toggle=True,
             style=None,
             **kwargs):
    """Creates and returns a ``wx.CheckBox``, allowing the user to set the
    given :class:`.Boolean` property value.

    If the ``icon`` argument is provided, it should be a string containing the
    name of an image file, or a list of two image file names.  In this case,
    case, a `:class:`.BitmapToggleButton` is used instead of a ``CheckBox``.

    If two icon images are provided, and the ``toggle`` argument is ``True``
    (the default), a :class:`.BitmapToggleButton` is used. If
    ``toggle=False``, a :class:`.BitmapRadioBox` is used instead.  In the
    latter case, the ``style`` argument is passed through to the
    :meth:`.BitmapRadioBox.__init__` method.

    See the :func:`.widgets._String` documentation for details on the other
    parameters.
    """

    widgetGet = None
    widgetSet = None

    if icon is None:
        widget = wx.CheckBox(parent)
        event  = wx.EVT_CHECKBOX
        
    else:


        if isinstance(icon, basestring):
            icon = [icon]

        for i in range(len(icon)):

            # Load the bitmap using this two-stage
            # approach, because under OSX, any other
            # way will not load the retina '@2x'
            # icon version (if it is present).
            bmp  = wx.EmptyBitmap(1, 1)
            bmp .LoadFile(icon[i], wx.BITMAP_TYPE_PNG)
            
            icon[i] = bmp

        if len(icon) == 1:
            icon = icon + [None]

        trueBmp  = icon[0]
        falseBmp = icon[1]

        if toggle:
            style  = wx.BU_EXACTFIT | wx.ALIGN_CENTRE | wx.BU_NOTEXT
            widget = bmptoggle.BitmapToggleButton(
                parent,
                trueBmp=trueBmp,
                falseBmp=falseBmp,
                style=style)
            event  = bmptoggle.EVT_BITMAP_TOGGLE
            
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
