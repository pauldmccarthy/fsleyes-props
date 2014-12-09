#!/usr/bin/env python
#
# widgets.py - Generate wx GUI widgets for props.PropertyBase objects.
#
# The sole entry point for this module is the makeWidget function,
# which is called via the build module when it automatically
# builds a GUI for the properties of a props.HasProperties instance.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""Generate wx GUI widgets for :class:`~props.properties.PropertyBase` objects.

The sole entry point for this module is the :func:`makeWidget` function, which
is called via functions in the :mod:`props.build` module when they
automatically builds a GUI for the properties of a
:class:`~props.properties.HasProperties` instance.
"""

import sys

import os
import os.path as op

from collections import OrderedDict
from collections import Iterable

import wx
import wx.combo

import numpy         as np
import matplotlib.cm as mplcm

# These properties are complex
# enough to get their own modules.
from widgets_list   import _List
from widgets_bounds import _Bounds
from widgets_point  import _Point
from widgets_number import _Number


def _propBind(hasProps,
              propObj,
              propVal,
              guiObj,
              evType,
              labelMap=None,
              valMap=None):
    """Binds a :class:`~props.properties_value.PropertyValue` to a widget.
    
    Sets up event callback functions such that, on a change to the given
    property value, the value displayed by the given GUI widget will be
    updated. Similarly, whenever a GUI event of the specified type (or types -
    you may pass in a list of event types) occurs, the property value will be
    set to the value controlled by the GUI widget.

    If ``labelMap`` is provided, it should be a dictionary of ``{value :
    label}`` pairs where the label is what is displayed to the user, and the
    value is what is assigned to the property value when a corresponding label
    is selected. It is basically here to support
    :class:`~props.properties_types.Choice` and
    :class:`~props.properties_types.ColourMap` properties. Similarly,
    ``valMap`` should be a dictionary of ``{label : value}`` pairs. If a
    ``labelMap`` is provided, but a ``valMap`` is not, a ``valMap`` is created
    from the ``labelMap``.

    A little trickery is used for :class:`~props.properties_types.ColourMap`
    properties, as the list of available colour maps may change at runtime.
    If a ``labelMap`` and ``valMap`` are provided, a reference to them is
    stored, rather than a copy being created. This means that the two maps
    may be updated externally, with the listeners registered in this function
    still functioning with the updates.

    :param hasProps: The owning :class:`~props.properties.HasProperties`
                     instance.
    
    :param propObj:  The :class:`~props.properties.PropertyBase` property type.
    
    :param propVal:  The :class:`~props.properties_value.PropertyValue` to be
                     bound.
    
    :param guiObj:   The :mod:`wx` GUI widget
    
    :param evType:   The event type (or list of event types) which should be
                     listened for on the ``guiObj``.
    
    :param labelMap: Dictionary of ``{value : label}`` pairs
    
    :param valMap:   Dictionary of ``{label : value}`` pairs
    """

    if not isinstance(evType, Iterable): evType = [evType]

    listenerName = 'WidgetBind_{}'.format(id(guiObj))

    if labelMap is None:
        valMap = None

    elif valMap is None:
        valMap = dict([(lbl, val) for (val, lbl) in labelMap.items()])

    def _guiUpdate(value, *a):
        """
        Called whenever the property value is changed.
        Sets the GUI widget value to that of the property.
        """

        if guiObj.GetValue() == value: return

        if valMap is not None: value = labelMap[value]

        # most wx widgets complain if you try to set their value to None
        if value is None: value = ''
        guiObj.SetValue(value)
        
    def _propUpdate(*a):
        """
        Called when the value controlled by the GUI widget
        is changed. Updates the property value.
        """

        value = guiObj.GetValue()

        if propVal.get() == value: return

        if labelMap is not None: propVal.set(valMap[value])
        else:                    propVal.set(value)

    _guiUpdate(propVal.get())

    # set up the callback functions
    for ev in evType: guiObj.Bind(ev, _propUpdate)
    propVal.addListener(listenerName, _guiUpdate)

    def onDestroy(ev):
        propVal.removeListener(listenerName)
        ev.Skip()

    guiObj.Bind(wx.EVT_WINDOW_DESTROY, onDestroy)


def _setupValidation(widget, hasProps, propObj, propVal):
    """Configures input validation for the given widget, which is assumed to be
    bound to the given ``propVal`` (a
    :class:`~props.properties_value.PropertyValue` object).

    Any changes to the property value are validated and, if the new value is
    invalid, the widget background colour is changed to a light red, so that
    the user is aware of the invalid-ness.

    This function is only used for a few different property types, namely
    :class:`~props.properties_types.String`,
    :class:`~props.properties_types.FilePath`, and
    :class:`~props.properties_types.Number` properties.

    :param widget:   The :mod:`wx` GUI widget.
    
    :param hasProps: The owning :class:`~props.properties.HasProperties`
                     instance.
    
    :param propObj:  The :class:`~props.properties.PropertyBase` property type.
    
    :param propVal:  The :class:`~props.properties_value.PropertyValue`
                     instance.
    """

    invalidBGColour = '#ff9999'
    validBGColour   = widget.GetBackgroundColour()

    def _changeBGOnValidate(value, valid, instance):
        """
        Called whenever the property value changes. Checks
        to see if the new value is valid and changes the
        widget background colour according to the validity
        of the new value.
        """
        
        if valid: newBGColour = validBGColour
        else:     newBGColour = invalidBGColour
        
        widget.SetBackgroundColour(newBGColour)
        widget.Refresh()

    # We add a callback listener to the PropertyValue object,
    # rather than to the PropertyBase, as one property may be
    # associated with multiple variables, and we don't want
    # the widgets associated with those other variables to
    # change background.
    lName = 'widgets_py_ChangeBG_{}'.format(id(widget))
    propVal.addListener(lName, _changeBGOnValidate)

    # And ensure that the listener is
    # removed when the widget is destroyed
    def onDestroy(ev):
        propVal.removeListener(lName)
        ev.Skip()
    
    widget.Bind(wx.EVT_WINDOW_DESTROY, onDestroy)

    # Validate the initial property value,
    # so the background is appropriately set
    _changeBGOnValidate(None, propVal.isValid(), None)
    

_lastFilePathDir = None
"""The _lastFilePathDir variable is used to retain the most recently visited
directory in file dialogs. New file dialogs are initialised to display this
directory.

This is currently a global setting, but it may be more appropriate to make it
a per-widget setting.  Easily done, just make this a dict, with the widget (or
property name) as the key.
"""


def _FilePath(parent, hasProps, propObj, propVal):
    """Creates and returns a panel containing a :class:`wx.TextCtrl` and a
    :class:`wx.Button`. The button, when clicked, opens a file dialog allowing
    the user to choose a file/directory to open, or a location to save (this
    depends upon how the ``propObj`` [a
    :class:`~props.properties_types.FilePath`] object was configured).

    See the :func:`_String` documentation for details on the parameters.
    """

    global _lastFilePathDir
    if _lastFilePathDir is None:
        _lastFilePathDir = os.getcwd()

    value = propVal.get()
    if value is None: value = ''

    panel   = wx.Panel(parent)
    textbox = wx.TextCtrl(panel)
    button  = wx.Button(panel, label='Choose')

    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(textbox, flag=wx.EXPAND, proportion=1)
    sizer.Add(button,  flag=wx.EXPAND)

    panel.SetSizer(sizer)
    panel.SetAutoLayout(1)
    sizer.Fit(panel)

    exists = propObj.getConstraint(hasProps, 'exists')
    isFile = propObj.getConstraint(hasProps, 'isFile')
    
    def _choosePath(ev):
        global _lastFilePathDir

        if exists and isFile:
            dlg = wx.FileDialog(parent,
                                message='Choose file',
                                defaultDir=_lastFilePathDir,
                                defaultFile=value,
                                style=wx.FD_OPEN)
            
        elif exists and (not isFile):
            dlg = wx.DirDialog(parent,
                               message='Choose directory',
                               defaultPath=_lastFilePathDir) 

        else:
            dlg = wx.FileDialog(parent,
                                message='Save file',
                                defaultDir=_lastFilePathDir,
                                defaultFile=value,
                                style=wx.FD_SAVE)


        dlg.ShowModal()
        path = dlg.GetPath()
        
        if path != '' and path is not None:
            _lastFilePathDir = op.dirname(path)
            propVal.set(path)
            
    _setupValidation(textbox, hasProps, propObj, propVal)
    _propBind(hasProps, propObj, propVal, textbox, wx.EVT_TEXT)

    button.Bind(wx.EVT_BUTTON, _choosePath)
    
    return panel
    

def _Choice(parent, hasProps, propObj, propVal):
    """Creates and returns a :class:`wx.Combobox` allowing the user to set the
    given ``propObj`` (props.Choice) object.

    See the :func:`_String` documentation for details on the parameters.
    """

    choices = propObj._choices
    labels  = propObj._choiceLabels
    valMap  = OrderedDict(zip(choices, labels))
    widget  = wx.ComboBox(
        parent,
        choices=labels,
        style=wx.CB_READONLY | wx.CB_DROPDOWN)

    _propBind(hasProps, propObj, propVal, widget, wx.EVT_COMBOBOX, valMap)
    
    return widget


def _String(parent, hasProps, propObj, propVal):
    """Creates and returns a :class:`wx.TextCtrl` object, allowing the user to
    edit the given ``propVal`` (managed by a
    :class:`~props.properties_types.String`) object.

    :param parent:   The :mod:`wx` parent object.
    
    :param hasProps: The owning :class:`~props.properties.HasProperties`
                     instance.

    :param propObj:  The :class:`~props.properties.PropertyBase` instance
                     (assumed to be a
                     :class:`~props.properties_types.String`).
    
    :param propVal:  The :class:`~props.properties_value.PropertyValue`
                     instance.

    """

    widget = wx.TextCtrl(parent)

    _propBind(hasProps, propObj, propVal, widget, wx.EVT_TEXT)
    _setupValidation(widget, hasProps, propObj, propVal)
    
    return widget



def _Real(parent, hasProps, propObj, propVal):
    """Creates and returns a widget allowing the user to edit the given
    :class:`~props.properties_types.Real` property value. See the
    :mod:`props.widgets_number` module.

    See the :func:`_String` documentation for details on the parameters.
    """
    return _Number(parent, hasProps, propObj, propVal)


def _Int(parent, hasProps, propObj, propVal):
    """Creates and returns a widget allowing the user to edit the given
    :class:`~props.properties_types.Int` property value. See the
    :mod:`props.widgets_number` module.

    See the :func:`_String` documentation for details on the parameters.
    """ 
    return _Number(parent, hasProps, propObj, propVal)


def _Percentage(parent, hasProps, propObj, propVal):
    """Creates and returns a widget allowing the user to edit the given
    :class:`~props.properties_types.Percentage` property value. See the
    :mod:`props.widgets_number` module.

    See the :func:`_String` documentation for details on the parameters.
    """ 
    # TODO Add '%' signs to Scale labels.
    return _Number(parent, hasProps, propObj, propVal) 
        

def _Boolean(parent, hasProps, propObj, propVal):
    """Creates and returns a :class:`wx.CheckBox`, allowing the user to set the
    given :class:`~props.properties_types.Boolean` property value.

    See the :func:`_String` documentation for details on the parameters.
    """

    checkBox = wx.CheckBox(parent)
    _propBind(hasProps, propObj, propVal, checkBox, wx.EVT_CHECKBOX)
    return checkBox


def _makeColourMapBitmap(cmap):
    """Makes a little bitmap image from a :class:`~matplotlib.colors.Colormap`
    instance.
    """

    width, height = 75, 15
    
    # create a single colour  for each horizontal pixel
    colours = cmap(np.linspace(0.0, 1.0, width))

    # discard alpha values
    colours = colours[:, :3]

    # repeat each horizontal pixel (height) times
    colours = np.tile(colours, (height, 1, 1))

    # scale to [0,255] and cast to uint8
    colours = colours * 255
    colours = np.array(colours, dtype=np.uint8)

    # make a wx Bitmap from the colour data
    colours = colours.ravel(order='C')
    bitmap  = wx.BitmapFromBuffer(width, height, colours) 
    return bitmap


def _ColourMap(parent, hasProps, propObj, propVal):
    """Creates and returns a combobox, allowing the user to change the value of
    the given :class:`~props.properties_types.ColourMap` property value.

    See also the :func:`_makeColourMapComboBox` function.
    """

    cmapNames = propVal.getAttribute('cmapNames')
    cmapObjs  = map(mplcm.get_cmap, cmapNames)
    valMap    = OrderedDict(zip(cmapObjs,   cmapNames))
    lblMap    = OrderedDict(zip(cmapNames,  cmapObjs))

    # create the combobox
    cbox = wx.combo.BitmapComboBox(
        parent, style=wx.CB_READONLY | wx.CB_DROPDOWN)

    # Called when the list of available 
    # colour maps changes - updates the 
    # options displayed in the combobox 
    def cmapsChanged(*a):

        selected  = cbox.GetSelection()
        cmapNames = propVal.getAttribute('cmapNames')
        cmapObjs  = map(mplcm.get_cmap, cmapNames)
        newValMap = OrderedDict(zip(cmapObjs,   cmapNames))
        newLblMap = OrderedDict(zip(cmapNames,  cmapObjs))

        cbox.Clear()

        # Make a little bitmap for every colour
        # map, and add it to the combobox
        for name, cmap in zip(cmapNames, cmapObjs):
            bitmap = _makeColourMapBitmap(cmap)
            cbox.Append(name, bitmap)

        # Update the value/label maps used by the
        # _propBind listeners (see _propBind docs)
        valMap.update(newValMap)
        lblMap.update(newLblMap)
 
        cbox.SetSelection(selected)
        cbox.Refresh()
 
    cmapsChanged()
    
    # Bind the combobox to the property
    _propBind(hasProps, propObj, propVal, cbox, wx.EVT_COMBOBOX,
              valMap, lblMap)
    propVal.addAttributeListener(
        'ColourMap_ComboBox_{}'.format(id(cbox)), cmapsChanged)

    currentVal = propVal.get().name
    if currentVal is None: currentVal = 0
    else:                  currentVal = cmapNames.index(currentVal)

    cbox.SetSelection(currentVal)
 
    return cbox


def makeWidget(parent, hasProps, propName):
    """Given ``hasProps`` (a :class:`~props.properties.HasProperties` object),
    ``propName`` (the name of a property of ``hasProps``), and ``parent``, a
    GUI object, creates and returns a widget, or a panel containing widgets,
    which may be used to edit the property.

    :param parent:       A :mod:`wx` object to be used as the parent for the
                         generated widget(s).
    
    :param hasProps:     A :class:`~props.properties.HasProperties` instance.
    
    :param str propName: Name of the :class:`~props.properties.PropertyBase`
                         property to generate a widget for.
    """

    propObj = hasProps.getProp(propName)
    propVal = propObj.getPropVal(hasProps)

    if propObj is None:
        raise ValueError('Could not find property {}.{}'.format(
            hasProps.__class__.__name__, propName))

    makeFunc = getattr(
        sys.modules[__name__],
        '_{}'.format(propObj.__class__.__name__), None)

    if makeFunc is None:
        raise ValueError(
            'Unknown property type: {}'.format(propObj.__class__.__name__))

    return makeFunc(parent, hasProps, propObj, propVal)
