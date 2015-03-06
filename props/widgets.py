#!/usr/bin/env python
#
# widgets.py - Generate wx GUI widgets for props.PropertyBase objects.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""Generate wx GUI widgets for :class:`~props.properties.PropertyBase` objects.

This module provides the following functions:

  - :func:`makeWidget`: Creates a widget for a ``PropertyBase`` object. This
    function is called by functions in the :mod:`props.build` module when
    they automatically build a GUI for the properties of a
    :class:`~props.properties.HasProperties` instance.

  - :func:`makeSyncWidget`: Creates a widget to control synchronisation of a
    ``PropertyBase`` object of a :class:`~props.syncable.SyncableHasProperties`
    instance with its parent.

  - :func:`bindWidget`: Binds an existing widget with a ``PropertyBase``
    instance.
"""

import logging
log = logging.getLogger(__name__)

import sys

import os
import os.path as op

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
              widgetGet=None,
              widgetSet=None,
              widgetDestroy=None):
    """Binds a :class:`~props.properties_value.PropertyValue` to a widget.
    
    Sets up event callback functions such that, on a change to the given
    property value, the value displayed by the given GUI widget will be
    updated. Similarly, whenever a GUI event of the specified type (or types -
    you may pass in a list of event types) occurs, the property value will be
    set to the value controlled by the GUI widget.

    :param hasProps:      The owning :class:`~props.properties.HasProperties`
                          instance.
    
    :param propObj:       The :class:`~props.properties.PropertyBase` property
                          type.
    
    :param propVal:       The :class:`~props.properties_value.PropertyValue` to 
                          be bound.
    
    :param guiObj:        The :mod:`wx` GUI widget
    
    :param evType:        The event type (or list of event types) which should 
                          be listened for on the ``guiObj``.
    
    :param widgetGet:     Function which returns the current widget value. If
                          ``None``, the ``guiObj.GetValue`` method is used.
 
    :param widgetSet:     Function which sets the current widget value. If
                          ``None``, the ``guiObj.SetValue`` method is used.

    :param widgetDestroy: Function which is called if/when the widget is
                          destroyed. Must accept one argument - the
                          :class:`wx.Event` object.
    """

    if not isinstance(evType, Iterable): evType = [evType]

    listenerName = 'WidgetBind_{}'.format(id(guiObj))

    if widgetGet is None: widgetGet = guiObj.GetValue
    if widgetSet is None: widgetSet = guiObj.SetValue

    log.debug('Binding PropertyValue ({}.{} [{}]) to widget {} ({})'.format(
        hasProps.__class__.__name__,
        propVal._name,
        id(hasProps),
        guiObj.__class__.__name__, id(guiObj)))

    def _guiUpdate(value, *a):
        """
        Called whenever the property value is changed.
        Sets the GUI widget value to that of the property.
        """

        if widgetGet() == value: return

        # most wx widgets complain if you try to set their value to None
        if value is None: value = ''

        log.debug('Updating Widget {} ({}) from {}.{} ({}): {}'.format(
            guiObj.__class__.__name__,
            id(guiObj),
            hasProps.__class__.__name__,
            propVal._name,
            id(hasProps),
            value))
        
        widgetSet(value)
        
    def _propUpdate(*a):
        """
        Called when the value controlled by the GUI widget
        is changed. Updates the property value.
        """

        value = widgetGet()

        if propVal.get() == value: return

        log.debug('Updating {}.{} ({}) from widget  {} ({}): {}'.format(
            hasProps.__class__.__name__,
            propVal._name,
            id(hasProps),
            guiObj.__class__.__name__,
            id(guiObj),
            value)) 

        propVal.set(value)

    def _attUpdate(ctx, att, val, name):
        if att == 'enabled': 
            guiObj.Enable(val)

    _guiUpdate(propVal.get())

    # set up the callback functions
    for ev in evType: guiObj.Bind(ev, _propUpdate)
    propVal.addListener(         listenerName, _guiUpdate)
    propVal.addAttributeListener(listenerName, _attUpdate)

    def onDestroy(ev):
        ev.Skip()
        log.debug('Widget {} ({}) destroyed (removing '
                  'listener {} from {}.{})'.format(
                      guiObj.__class__.__name__,
                      id(guiObj),
                      listenerName,
                      hasProps.__class__.__name__,
                      propVal._name))
        propVal.removeListener(listenerName)

        if widgetDestroy is not None:
            widgetDestroy(ev)

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

    def _changeBGOnValidate(value, valid, *a):
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


def _FilePath(parent, hasProps, propObj, propVal, **kwargs):
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
    

def _Choice(parent, hasProps, propObj, propVal, **kwargs):
    """Creates and returns a :class:`wx.Combobox` allowing the user to set the
    given ``propObj`` (props.Choice) object.

    See the :func:`_String` documentation for details on the parameters.
    """

    choices = propObj.getChoices(hasProps)
    labels  = propObj.getLabels( hasProps)
    cl      = filter(lambda (c, l): propObj.choiceEnabled(c, hasProps),
                     zip(choices, labels))

    choices, labels = zip(*cl)

    widget = wx.ComboBox(
        parent,
        choices=labels,
        style=wx.CB_READONLY | wx.CB_DROPDOWN)

    def widgetGet():
        choices = propObj.getChoices(hasProps)
        return choices[widget.GetSelection()]

    def widgetSet(value):
        choices = propObj.getChoices(hasProps)
        widget.SetSelection(choices.index(value))

    # Update the combobox choices
    # when they change.
    def choicesChanged(ctx, name, *a):

        if name not in ('choices', 'labels', 'choiceEnabled'):
            return

        choices = propObj.getChoices(hasProps)
        labels  = propObj.getLabels( hasProps)

        # Remove any disabled choices from the list.
        # It would be nice if wx.ComboBox allowed
        # us to enable/disable individual items.
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

        widget.Set(labels)
        widgetSet(propVal.get())

    listenerName = 'WidgetChoiceUpdate_{}'.format(id(widget))
    propVal.addAttributeListener(listenerName, choicesChanged)

    def onDestroy(ev):
        propVal.removeAttributeListener(listenerName)

    _propBind(hasProps,
              propObj,
              propVal,
              widget,
              wx.EVT_COMBOBOX,
              widgetGet,
              widgetSet,
              widgetDestroy=onDestroy)
    
    return widget


def _String(parent, hasProps, propObj, propVal, **kwargs):
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

    :param kwargs:   Type-specific options.
    """

    widget = wx.TextCtrl(parent)
    
    # Use a DC object to calculate a decent
    # minimum size fort the widget
    dc       = wx.ClientDC(widget)
    textSize = dc.GetTextExtent('w' * 17)
    widgSize = widget.GetBestSize().Get()

    widget.SetMinSize((max(textSize[0], widgSize[0]),
                       max(textSize[1], widgSize[1])))
 
    _propBind(hasProps, propObj, propVal, widget, wx.EVT_TEXT)
    _setupValidation(widget, hasProps, propObj, propVal)
    
    return widget


def _Real(parent, hasProps, propObj, propVal, **kwargs):
    """Creates and returns a widget allowing the user to edit the given
    :class:`~props.properties_types.Real` property value. See the
    :mod:`props.widgets_number` module.

    See the :func:`_String` documentation for details on the parameters.
    """
    return _Number(parent, hasProps, propObj, propVal, **kwargs)


def _Int(parent, hasProps, propObj, propVal, **kwargs):
    """Creates and returns a widget allowing the user to edit the given
    :class:`~props.properties_types.Int` property value. See the
    :mod:`props.widgets_number` module.

    See the :func:`_String` documentation for details on the parameters.
    """ 
    return _Number(parent, hasProps, propObj, propVal, **kwargs)


def _Percentage(parent, hasProps, propObj, propVal, **kwargs):
    """Creates and returns a widget allowing the user to edit the given
    :class:`~props.properties_types.Percentage` property value. See the
    :mod:`props.widgets_number` module.

    See the :func:`_String` documentation for details on the parameters.
    """ 
    # TODO Add '%' signs to Scale labels.
    return _Number(parent, hasProps, propObj, propVal, **kwargs) 
        

def _Boolean(parent, hasProps, propObj, propVal, **kwargs):
    """Creates and returns a :class:`wx.CheckBox`, allowing the user to set the
    given :class:`~props.properties_types.Boolean` property value.

    See the :func:`_String` documentation for details on the parameters.
    """

    checkBox = wx.CheckBox(parent)
    _propBind(hasProps, propObj, propVal, checkBox, wx.EVT_CHECKBOX)
    return checkBox


def _Colour(parent, hasProps, propObj, propVal, **kwargs):
    """Creates and returns a :class:`wx.ColourPickerCtrl` widget, allowing
    the user to modify the given :class:`props.properties_types.Colour`
    value.
    """
    colourPicker = wx.ColourPickerCtrl(parent)

    def widgetGet():
        vals = colourPicker.GetColour()
        return [v / 255.0 for v in vals]
    
    def widgetSet(vals):
        colourPicker.SetColour([v * 255.0 for v in vals])

    _propBind(hasProps,
              propObj,
              propVal,
              colourPicker,
              wx.EVT_COLOURPICKER_CHANGED,
              widgetGet,
              widgetSet)

    return colourPicker


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


def _ColourMap(parent, hasProps, propObj, propVal, **kwargs):
    """Creates and returns a combobox, allowing the user to change the value of
    the given :class:`~props.properties_types.ColourMap` property value.

    See also the :func:`_makeColourMapComboBox` function.
    """

    cmapNames = propVal.getAttribute('cmapNames')
    cmapObjs  = map(mplcm.get_cmap, cmapNames)

    # create the combobox
    cbox = wx.combo.BitmapComboBox(
        parent, style=wx.CB_READONLY | wx.CB_DROPDOWN)

    def widgetGet():
        return cmapObjs[cbox.GetSelection()]

    def widgetSet(value):
        cbox.SetSelection(cmapObjs.index(value))

    # Called when the list of available 
    # colour maps changes - updates the 
    # options displayed in the combobox 
    def cmapsChanged(*a):

        selected  = cbox.GetSelection()
        cmapNames = propVal.getAttribute('cmapNames')
        cmapObjs  = map(mplcm.get_cmap, cmapNames)

        cbox.Clear()

        # Store the width of the biggest bitmap, 
        # and the width of the biggest label.
        # the BitmapComboBox doesn't size itself
        # properly on all platforms, so we'll
        # do it manually, dammit
        maxBmpWidth = 0
        maxLblWidth = 0
        dc          = wx.ClientDC(cbox)

        # Make a little bitmap for every colour
        # map, and add it to the combobox
        for name, cmap in zip(cmapNames, cmapObjs):
            
            bitmap = _makeColourMapBitmap(cmap)
            cbox.Append(name, bitmap)

            # use the DC to get the label size
            lblWidth = dc.GetTextExtent(name)[0]
            bmpWidth = bitmap.GetWidth()

            print '{} {}'.format(name, lblWidth)

            if bmpWidth > maxBmpWidth: maxBmpWidth = bmpWidth
            if lblWidth > maxLblWidth: maxLblWidth = lblWidth

        # Explicitly set the minimum size from
        # the maximum bitmap/label sizes, with 
        # some extra to account for the drop
        # down button
        cbox.InvalidateBestSize()
        bestHeight = cbox.GetBestSize().GetHeight()
        cbox.SetMinSize((maxBmpWidth + maxLblWidth + 40, bestHeight))

        cbox.SetSelection(selected)
        cbox.Refresh()

    # Initialise the combobox options
    cmapsChanged()

    # Bind the combobox to the property
    _propBind(hasProps,
              propObj,
              propVal,
              cbox,
              wx.EVT_COMBOBOX,
              widgetGet,
              widgetSet)

    # Make sure the combobox options are updated
    # when the property options change
    propVal.addAttributeListener(
        'ColourMap_ComboBox_{}'.format(id(cbox)), cmapsChanged)

    # Set the initial combobox selection
    currentVal = propVal.get().name
    if currentVal is None: currentVal = 0
    else:                  currentVal = cmapNames.index(currentVal)

    cbox.SetSelection(currentVal)
 
    return cbox


def _LinkBox(parent, hasProps, propObj, propVal, **kwargs):
    """Creates a 'link' button which toggles synchronisation
    between the property on the given ``hasProps`` instance,
    and its parent.
    """
    propName = propObj.getLabel(hasProps)
    value    = hasProps.isSyncedToParent(propName)
    linkBox  = wx.ToggleButton(parent,
                               label=u'\u21cb',
                               style=wx.BU_EXACTFIT)
    linkBox.SetValue(value)

    if (hasProps.getParent() is None)                   or \
       (not hasProps.canBeSyncedToParent(    propName)) or \
       (not hasProps.canBeUnsyncedFromParent(propName)):
        linkBox.Enable(False)
        
    else:

        # Update the binding state when the linkbox is modified
        def onLinkBox(ev):
            value = linkBox.GetValue()
            if value: hasProps.syncToParent(    propName)
            else:     hasProps.unsyncFromParent(propName)

        # And update the linkbox when the binding state is modified
        def onSyncProp(*a):
            linkBox.SetValue(hasProps.isSyncedToParent(propName))

        def onDestroy(ev):
            ev.Skip()
            hasProps.removeSyncChangeListener(propName, lName)

        lName = 'widget_LinkBox_{}_{}'.format(propName, linkBox)
        
        linkBox.Bind(wx.EVT_TOGGLEBUTTON,   onLinkBox)
        linkBox.Bind(wx.EVT_WINDOW_DESTROY, onDestroy)
        hasProps.addSyncChangeListener(propName, lName, onSyncProp)

    return linkBox    


def makeSyncWidget(parent, hasProps, propName, **kwargs):
    """Creates a button which controls synchronisation of the specified
    property on the given ``hasProps`` instance, with the corresponding
    property on its parent.

    See the :func:`makeWidget` function for a description of the
    arguments.
    """
    propObj = hasProps.getProp(propName)
    propVal = propObj.getPropVal(hasProps)

    return _LinkBox(parent, hasProps, propObj, propVal, **kwargs)


def makeWidget(parent, hasProps, propName, **kwargs):
    """Given ``hasProps`` (a :class:`~props.properties.HasProperties` object),
    ``propName`` (the name of a property of ``hasProps``), and ``parent``, a
    GUI object, creates and returns a widget, or a panel containing widgets,
    which may be used to edit the property.

    :param parent:       A :mod:`wx` object to be used as the parent for the
                         generated widget(s).
    
    :param hasProps:     A :class:`~props.properties.HasProperties` instance.
    
    :param str propName: Name of the :class:`~props.properties.PropertyBase`
                         property to generate a widget for.

    :param kwargs:       Type specific arguments.
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

    return makeFunc(parent, hasProps, propObj, propVal, **kwargs)


def makeListWidgets(parent, hasProps, propName, **kwargs):
    """Creates a widget for every value in the given list property.
    """

    propObj     = hasProps.getProp(propName)._listType
    propValList = getattr(hasProps, propName).getPropertyValueList()

    makeFunc = getattr(
        sys.modules[__name__],
        '_{}'.format(propObj.__class__.__name__), None)

    if makeFunc is None:
        raise ValueError(
            'Unknown property type: {}'.format(propObj.__class__.__name__))

    widgets = []

    for propVal in propValList:
        widgets.append(makeFunc(parent, hasProps, propObj, propVal, **kwargs))

    return widgets


def bindWidget(widget,
               hasProps,
               propName,
               evTypes,
               widgetGet=None,
               widgetSet=None):
    """Binds the given widget to the specified property. See the
    :func:`_propBind` method for details of the arguments.
    """

    propObj = hasProps.getProp(   propName)
    propVal = hasProps.getPropVal(propName)

    _propBind(
        hasProps, propObj, propVal, widget, evTypes, widgetGet, widgetSet)


def bindListWidgets(widgets,
                    hasProps,
                    propName,
                    evTypes,
                    widgetSets=None,
                    widgetGets=None):
    """Binds the given sequence of widgets to each of the values in the
    specified list property.
    """
    
    if widgetSets is None: widgetSets = [None] * len(widgets)
    if widgetGets is None: widgetGets = [None] * len(widgets)

    propObj     = hasProps.getProp( propName)
    propValList = getattr(hasProps, propName).getPropertyValueList()

    for propVal, widget, wGet, wSet in zip(
            propValList, widgets, widgetGets, widgetSets):
        
        _propBind(hasProps,
                  propObj,
                  propVal,
                  widget,
                  evTypes,
                  wGet,
                  wSet)
