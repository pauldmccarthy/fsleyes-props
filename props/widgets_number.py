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

import sys

import wx

import properties as props
import widgets

import pwidgets.floatslider as floatslider


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
    minval  = propObj.getConstraint(hasProps, 'minval')
    maxval  = propObj.getConstraint(hasProps, 'maxval')
    isRange = (minval is not None) and (maxval is not None)
    params  = {}

    minval = getMinVal(minval)
    maxval = getMaxVal(maxval)
        
    if isinstance(propObj, props.Int):
        SpinCtr   = wx.SpinCtrl
        increment = 1

    elif isinstance(propObj, props.Real):
        
        SpinCtr = wx.SpinCtrlDouble

        if isRange: increment = (maxval - minval) / 100.0
        else:       increment = 0.5

        params['inc'] = increment
                
    else:
        raise TypeError('Unrecognised property type: {}'.format(
            propObj.__class__.__name__))
        
    params['min']     = minval
    params['max']     = maxval
    params['initial'] = value
    params['value']   = '{}'.format(value)

    spin = SpinCtr(parent, **params)
    
    widgets._propBind(hasProps, propObj, propVal, spin,
                      (wx.EVT_SPIN, wx.EVT_SPINCTRL, wx.EVT_SPINCTRLDOUBLE))

    def updateRange(*a):
        minval = getMinVal(propObj.getConstraint(hasProps, 'minval'))
        maxval = getMaxVal(propObj.getConstraint(hasProps, 'maxval'))
        spin.SetRange(minval, maxval)

    listenerName = 'widgets_number_py_updateRange_{}'.format(id(spin))
    propVal.addAttributeListener(listenerName, updateRange)


    def onMouseWheel(ev):

        if not spin.IsEnabled():
            return
        
        wheelDir = ev.GetWheelRotation()

        if   wheelDir < 0: offset = -increment
        elif wheelDir > 0: offset =  increment
        else:              return
        
        propVal.set(propVal.get() + offset)

        
    def onDestroy(ev):
        propVal.removeAttributeListener(listenerName)
        ev.Skip()
    
    spin.Bind(wx.EVT_WINDOW_DESTROY, onDestroy)
    spin.Bind(wx.EVT_MOUSEWHEEL,     onMouseWheel)

    return spin


def _makeSlider(parent, hasProps, propObj, propVal, showSpin, showLimits):
    """Creates a :class:`~pwidgets.floatslider.SliderSpinPanel` bound to the
    given :class:`~props.properties_value.PropertyValue` object.
    """

    value      = propVal.get()
    minval     = propObj.getConstraint(hasProps, 'minval')
    maxval     = propObj.getConstraint(hasProps, 'maxval')
    editLimits = propObj.getConstraint(hasProps, 'editLimits')

    if   isinstance(propObj, props.Int):  real = False
    elif isinstance(propObj, props.Real): real = True

    if not showSpin:
        evt    = wx.EVT_SLIDER
        slider = floatslider.FloatSlider(
            parent,
            value=value,
            minValue=minval,
            maxValue=maxval)
        
    else:
        evt    = floatslider.EVT_SSP_VALUE 
        slider = floatslider.SliderSpinPanel(
            parent,
            real=real,
            value=value,
            minValue=minval,
            maxValue=maxval,
            showLimits=showLimits,
            editLimits=editLimits)

    # bind the slider value to the property value
    widgets._propBind(hasProps, propObj, propVal, slider, evt)

    # Update slider min/max bounds and labels
    # whenever the property constraints change.    
    def updateSliderRange(*a):
        minval = propObj.getConstraint(hasProps, 'minval')
        maxval = propObj.getConstraint(hasProps, 'maxval')
        
        slider.SetRange(minval, maxval)
        # TODO check that value has changed due to the range change?


    listenerName = 'widgets_number_py_updateRange_{}'.format(id(slider))
    propObj.addConstraintListener(hasProps, listenerName, updateSliderRange)

    # remove the listener when the slider is destroyed
    def onDestroy(ev):
        propObj.removeConstraintListener(hasProps, listenerName)
        ev.Skip()
    
    slider.Bind(wx.EVT_WINDOW_DESTROY, onDestroy)

    if editLimits:

        # When the user edits the slider bounds,
        # update the property constraints
        def updatePropRange(ev):
            propObj.setConstraint(hasProps, 'minval', ev.min)
            propObj.setConstraint(hasProps, 'maxval', ev.max)

        slider.Bind(floatslider.EVT_SSP_LIMIT, updatePropRange)

    return slider


def _Number(
        parent,
        hasProps,
        propObj,
        propVal,
        slider=True,
        spin=True,
        showLimits=True):
    """Creates and returns a widget allowing the user to edit the given
    :class:`~props.properties_types.Number` property value.

    See the :func:`~props.widgets._String` documentation for details on the
    parameters.
    """

    if not (slider or spin):
        raise ValueError('One of slider or spin must be True')

    minval  = propObj.getConstraint(hasProps, 'minval')
    maxval  = propObj.getConstraint(hasProps, 'maxval')
    isRange = (minval is not None) and (maxval is not None)

    if (not isRange) or (not slider):
        return _makeSpinBox(parent, hasProps, propObj, propVal)
    
    else:
        return _makeSlider(parent,
                           hasProps,
                           propObj,
                           propVal,
                           spin,
                           showLimits)
