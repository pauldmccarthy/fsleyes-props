#!/usr/bin/env python
#
# widgets_choice.py - Create widgets for modifying Choice properties.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :func:`_Choice` function, which is imported into
the :mod:`widgets` module namespace. It is separated purely to keep the
``widgets`` module file size down.
"""

import logging

import wx

import widgets

import pwidgets.bitmapradio as bmpradio


log = logging.getLogger(__name__)


def _Choice(parent,
            hasProps,
            propObj,
            propVal,
            labels=None,
            icons=None,
            style=None,
            **kwargs):
    """Creates and returns a widget allowing the user to modify the given
    :class:`.Choice` instance (``propObj``).

    
    By default, ``wx.Choice`` widget is used. However, if the ``icons``
    argument is specified, a :class:`.BitmapRadioBox` is used instead.


    :arg labels:  A dict of ``{choice : label}`` mappings, specifying the
                  label to be displayed for each choice. If not provided,
                  the string representation of each choice is used. Not
                  used if the ``icons`` argument is specified.
    
                  .. note:: If the ``Choice`` property is dynamic (i.e.
                            choices are going to be added/removed during
                            program execution), you must ensure that the
                            ``labels`` dictionary contains a value for
                            all possible choices, not just the initial
                            choices.

                            As an alternative to passing in a ``dict``, you
                            may also set ``labels`` to a function. In this
                            case, the ``labels`` function must accept a single
                            choice value as its only argument, and return a
                            label for that choice. 

    :arg icons:   If provided, a :class:`.BitmapRadioBox` is used instead of a
                  ``wx.Choice`` widget. The ``icons`` should be a dictionary
                  of ``{ choice : imageFile}`` mappings, containing an icon
                  files to be used for each choice.

    :arg style:   Passed through to the :meth:`.BitmapRadioBox.__init__` 
                  method. Not used if no ``icons`` were provided.

    
    See the :func:`.widgets._String` documentation for details on the other
    parameters.
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

        if name not in ('choices', 'choiceEnabled'):
            return

        choices   = propObj.getChoices(hasProps)
        curLabels = []

        if labels is None: curLabels = [str(c)    for c in choices]
        else:

            # labels can either be a dict
            # of {choice : label} mappings
            if isinstance(labels, dict):
                curLabels = [labels[c] for c in choices]
                
            # or a function which, given a
            # choice, returns a label for it
            else: curLabels = map(labels, choices)

        # If we're using a wx.Choice widget, remove
        # any disabled choices from the list.
        # It would be nice if wx.Choice allowed
        # us to enable/disable individual items, but
        # it doesn't, so our only option is to hide
        # the disabled ones.
        if icons is None:
            for i, choice in enumerate(choices):
                if not propObj.choiceEnabled(choice, hasProps):
                    curLabels.pop(i)
                    
        log.debug('Updating options for Widget '
                  '{} ({}) from {}.{} ({}): {}'.format(
                      widget.__class__.__name__,
                      id(widget),
                      hasProps.__class__.__name__,
                      propVal._name,
                      id(hasProps),
                      curLabels))

        if icons is None:
            widget.Set(curLabels)
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
