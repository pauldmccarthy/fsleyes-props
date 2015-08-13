#!/usr/bin/env python
#
# widgets_choice.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import logging

import wx

import widgets

import pwidgets.bitmapradio as bmpradio


log = logging.getLogger(__name__)


def _Choice(parent,
            hasProps,
            propObj,
            propVal,
            icons=None,
            style=None,
            **kwargs):
    """Creates and returns a :class:`wx.Choice` allowing the user to set the
    given ``propObj`` (props.Choice) object.

    If the ``icons`` parameter is provided, a :class:`.BitmapRadioBox` is
    used instead of a ``wx.Choice`` widget. The ``icons`` should be a
    dictionary of ``{ choice : imageFile}`` mappings, containing an icon
    files to be used for each choice.

    See the :func:`_String` documentation for details on the parameters.
    """

    # If we have been given some icons, we will use
    # a BitmapRadioBox, which has a toggle button
    # for each choice
    if icons is not None:
        event  = bmpradio.EVT_BITMAP_RADIO_EVENT
        widget = bmpradio.BitmapRadioBox(parent, style=style)

    # Otherwise we use a regular drop down 
    # box, via the wx.Choice widget.
    else:
        event  = wx.EVT_CHOICE
        widget = wx.Choice(parent)

        # Under linux/GTK, choice widgets absorb
        # mousewheel events. I don't want this.
        if wx.Platform == '__WXGTK__':
            def wheel(ev):
                widget.GetParent().GetEventHandler().ProcessEvent(ev)
            widget.Bind(wx.EVT_MOUSEWHEEL, wheel)

    # When the widget value changes,
    # return the corresponding choice
    # value
    def widgetGet():
        choices = propObj.getChoices(hasProps)

        if len(choices) > 0: return choices[widget.GetSelection()]
        else:                return None

    # When the property value changes,
    # update the widget value
    def widgetSet(value):
        choices = propObj.getChoices(hasProps)
        
        if len(choices) > 0: return widget.SetSelection(choices.index(value))
        else:                return None

    # Update the combobox choices
    # when they change.
    def choicesChanged(ctx, name, *a):

        if name not in ('choices', 'labels', 'choiceEnabled'):
            return

        choices = propObj.getChoices(hasProps)
        labels  = propObj.getLabels( hasProps)

        # If we're using a wx.Choice widget, remove
        # any disabled choices from the list.
        # It would be nice if wx.Choice allowed
        # us to enable/disable individual items.
        if icons is None:
            for i, choice in enumerate(choices):
                if not propObj.choiceEnabled(choice, hasProps):
                    labels.pop(i)

        log.debug('Updating options for Widget '
                  '{} ({}) from {}.{} ({}): {}'.format(
                      widget.__class__.__name__,
                      id(widget),
                      hasProps.__class__.__name__,
                      propVal._name,
                      id(hasProps),
                      labels))

        if icons is None:
            widget.Set(labels)
        else:

            widget.Clear()
            
            # If using a BitmapRadio widget, we can
            # show all choices, but disable  the
            # buttons for disabled choices
            for i, choice in enumerate(choices):

                # Load the image file for each choice
                # if they have not already been loaded
                if isinstance(icons[choice], basestring):
                    bmp = wx.EmptyBitmap(1, 1)
                    bmp.LoadFile(icons[choice], type=wx.BITMAP_TYPE_PNG)

                    # Replace the icon file
                    # name with the bitmap
                    icons[choice] = bmp

                widget.AddChoice(icons[choice])
                if not propObj.choiceEnabled(choice, hasProps):
                    widget.Disable(i) 

    listenerName = 'WidgetChoiceUpdate_{}'.format(id(widget))
    propVal.addAttributeListener(listenerName, choicesChanged, weak=False)

    # Initialise the widget
    choicesChanged(None, 'choices')
    widgetSet(propVal.get())

    def onDestroy(ev):
        propVal.removeAttributeListener(listenerName)

    widgets._propBind(hasProps,
                      propObj,
                      propVal,
                      widget,
                      event,
                      widgetGet,
                      widgetSet,
                      widgetDestroy=onDestroy)
    
    return widget
