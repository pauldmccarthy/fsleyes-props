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

import pwidgets.bitmapradio as bmpradio
from . import                  widgets


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
    :class:`.Choice` property value.

    
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
                  files to be used for each choice. The ``icons`` dictionary
                  may alternately contain ``{ choice : (selectedImageFile,
                  unselectedImageFile) }`` mappings, which specifies separate
                  icons to be used when the corresponding choice is selected
                  or not selected.

    :arg style:   Passed through to the :meth:`.BitmapRadioBox.__init__` 
                  method. Not used if no ``icons`` were provided.

    
    See the :func:`.widgets._String` documentation for details on the other
    parameters.
    """

    # A reference to the choices - this is
    # shared by the inner functions defined
    # below, and updated in choicesChanged
    choices = [propObj.getChoices(hasProps)]

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
        if len(choices[0]) > 0: return choices[0][widget.GetSelection()]
        else:                   return None

    # When the property value changes,
    # update the widget value
    def widgetSet(value):
        if len(choices[0]) > 0:
            return widget.SetSelection(choices[0].index(value))
        else:
            return None

    # Update the combobox choices
    # when they change.
    def choicesChanged(ctx, name, *a):

        if name not in ('choices', 'choiceEnabled'):
            return

        choices[0] = propObj.getChoices(hasProps)
        curLabels  = []

        if labels is None:
            curLabels = [str(c) for c in choices[0]]

        # labels can either be a dict
        # of {choice : label} mappings
        elif isinstance(labels, dict):
            curLabels = [labels[c] for c in choices[0]]
                
        # or a function which, given a
        # choice, returns a label for it
        else:
            curLabels = map(labels, choices[0])

        # If we're using a wx.Choice widget, remove
        # any disabled choices from the list.
        # It would be nice if wx.Choice allowed
        # us to enable/disable individual items, but
        # it doesn't, so our only option is to hide
        # the disabled ones.
        if icons is None:
            for i, choice in enumerate(choices[0]):
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
            # show all choices, but disable the
            # buttons for disabled choices
            for i, choice in enumerate(choices[0]):

                choiceIcons = icons[choice]

                if not isinstance(choiceIcons, (tuple, list)):
                    choiceIcons = [choiceIcons]
                else:
                    choiceIcons = list(choiceIcons)

                # Load the image file for each choice
                # if they have not already been loaded
                for i, ci in enumerate(choiceIcons):
                    if isinstance(ci, basestring):
                        bmp  = wx.EmptyBitmap(1, 1)
                        bmp.LoadFile(ci, type=wx.BITMAP_TYPE_PNG)
                        choiceIcons[i] = bmp

                # Only one bitmap specified - add
                # a placeholder for the unselected
                # bitmap
                if len(choiceIcons) == 1:
                    choiceIcons = choiceIcons + [None]

                # Replace the mapping in the
                # icon dict with the bitmaps
                icons[choice]    = choiceIcons
                selBmp, deselBmp = choiceIcons

                widget.AddChoice(selBmp, deselBmp)
                if not propObj.choiceEnabled(choice, hasProps):
                    widget.Disable(i)

        # Make sure the widget
        # selection is up to date
        widget.SetSelection(choices[0].index(propVal.get()))

    listenerName = 'WidgetChoiceUpdate_{}'.format(id(widget))
    propVal.addAttributeListener(listenerName, choicesChanged, weak=False)

    # Initialise the widget
    choicesChanged(None, 'choices')
    widgetSet(propVal.get())

    def onDestroy(ev):
        log.debug('Removing attribute listener {}'.format(listenerName))
        propVal.removeAttributeListener(listenerName)

    widgets._propBind(hasProps,
                      propObj,
                      propVal,
                      widget,
                      event,
                      widgetGet=widgetGet,
                      widgetSet=widgetSet,
                      widgetDestroy=onDestroy)
    
    return widget
