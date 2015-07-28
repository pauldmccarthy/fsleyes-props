#!/usr/bin/env python
#
# widgets_number.py - Create widgets for modifying Number properties.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""A widget for editing a :class:`~props.properties_types.Number` property.

This module is not intended to be used directly - it is imported into the
:mod:`props.widgets` namespace.
"""

import logging
import sys

import wx


import properties as props
import widgets

import pwidgets.floatslider as floatslider
import pwidgets.floatspin   as floatspin


log = logging.getLogger(__name__)


def _makeSpinBox(parent, hasProps, propObj, propVal):
    """Creates a :class:`wx.SpinCtrl` or :class:`wx.SpinCtrlDouble` bound to
    the given :class:`~props.properties_value.PropertyValue` object.
    """

    def getMinVal(val):
        if val is not None: return val
        if   isinstance(propObj, props.Int):  return -2 ** 31 + 1
        elif isinstance(propObj, props.Real): return -sys.float_info.max
        
    def getMaxVal(val):
        if val is not None: return val
        if   isinstance(propObj, props.Int):  return 2 ** 31 - 1
        elif isinstance(propObj, props.Real): return sys.float_info.max 

    value   = propVal.get()
    minval  = propVal.getAttribute('minval')
    maxval  = propVal.getAttribute('maxval')
    isRange = (minval is not None) and (maxval is not None)

    minval    = getMinVal(minval)
    maxval    = getMaxVal(maxval)
    increment = 0
    style     = floatspin.FSC_MOUSEWHEEL

    if   isinstance(propObj, props.Int):
        increment  = 1
        style     |= floatspin.FSC_INTEGER

    elif isinstance(propObj, props.Real):

        if isRange: increment = (maxval - minval) / 100.0
        else:       increment = 0.5

        increment = increment
                
    else:
        raise TypeError('Unrecognised property type: {}'.format(
            propObj.__class__.__name__))

    spin = floatspin.FloatSpinCtrl(
        parent,
        value=value,
        minValue=minval,
        maxValue=maxval,
        increment=increment,
        style=style)
    
    widgets._propBind(
        hasProps, propObj, propVal, spin, floatspin.EVT_FLOATSPIN)

    def updateRange(*a):
        minval = getMinVal(propVal.getAttribute('minval'))
        maxval = getMaxVal(propVal.getAttribute('maxval'))

        log.debug('Updating {} range from {}.{}: {} - {}'.format(
            type(spin).__name__,
            type(hasProps).__name__,
            propVal._name,
            minval,
            maxval))

        spin.SetRange(minval, maxval)

    listenerName = 'widgets_number_py_updateRange_{}'.format(id(spin))
    propVal.addAttributeListener(listenerName, updateRange, weak=False)

    def onDestroy(ev):
        propVal.removeAttributeListener(listenerName)
        ev.Skip()
    
    spin.Bind(wx.EVT_WINDOW_DESTROY, onDestroy)

    return spin


def _makeSlider(
        parent, hasProps, propObj, propVal, showSpin, showLimits, editLimits):
    """Creates a :class:`~pwidgets.floatslider.SliderSpinPanel` bound to the
    given :class:`~props.properties_value.PropertyValue` object.
    """

    value  = propVal.get()
    minval = propVal.getAttribute('minval')
    maxval = propVal.getAttribute('maxval')

    if   isinstance(propObj, props.Int):  real = False
    elif isinstance(propObj, props.Real): real = True

    if not showSpin:
        style = floatslider.FS_MOUSEWHEEL
        if real:
            style |= floatslider.FS_INTEGER
        evt    = wx.EVT_SLIDER
        slider = floatslider.FloatSlider(
            parent,
            value=value,
            minValue=minval,
            maxValue=maxval,
            style=style)
        
    else:
        evt    = floatslider.EVT_SSP_VALUE 
        slider = floatslider.SliderSpinPanel(
            parent,
            real=real,
            value=value,
            minValue=minval,
            maxValue=maxval,
            showLimits=showLimits,
            editLimits=editLimits,
            mousewheel=True)

    # bind the slider value to the property value
    widgets._propBind(hasProps, propObj, propVal, slider, evt)

    # Update slider min/max bounds and labels
    # whenever the property constraints change.    
    def updateSliderRange(*a):
        minval = propVal.getAttribute('minval')
        maxval = propVal.getAttribute('maxval')
        
        slider.SetRange(minval, maxval)
        # TODO check that value has changed due to the range change?

    listenerName = 'widgets_number_py_updateRange_{}'.format(id(slider))
    propVal.addAttributeListener(listenerName, updateSliderRange, weak=False)

    # remove the listener when the slider is destroyed
    def onDestroy(ev):
        propVal.removeAttributeListener(listenerName)
        ev.Skip()
    
    slider.Bind(wx.EVT_WINDOW_DESTROY, onDestroy)

    if editLimits:

        # When the user edits the slider bounds,
        # update the property constraints
        def updatePropRange(ev):
            propVal.setAttribute('minval', ev.min)
            propVal.setAttribute('maxval', ev.max)

        slider.Bind(floatslider.EVT_SSP_LIMIT, updatePropRange)

    return slider


def _Number(
        parent,
        hasProps,
        propObj,
        propVal,
        slider=True,
        spin=True,
        showLimits=True,
        editLimits=True):
    """Creates and returns a widget allowing the user to edit the given
    :class:`~props.properties_types.Number` property value.

    See the :func:`~props.widgets._String` documentation for details on the
    parameters.
    """

    if not (slider or spin):
        raise ValueError('One of slider or spin must be True')

    minval  = propVal.getAttribute('minval')
    maxval  = propVal.getAttribute('maxval')
    isRange = (minval is not None) and (maxval is not None)

    if (not isRange) or (not slider):
        return _makeSpinBox(parent, hasProps, propObj, propVal)
    
    else:
        return _makeSlider(parent,
                           hasProps,
                           propObj,
                           propVal,
                           spin,
                           showLimits,
                           editLimits)
