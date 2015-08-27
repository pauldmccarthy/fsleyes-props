#!/usr/bin/env python
#
# widgets_number.py - Create widgets for modifying Number properties.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :func:`_Number` function, which is imported into
the :mod:`widgets` module namespace. It is separated purely to keep the
``widgets`` module file size down.
"""

import logging
import sys

import wx


import properties as props
import widgets

import pwidgets.floatslider as floatslider
import pwidgets.floatspin   as floatspin


log = logging.getLogger(__name__)


def _Number(
        parent,
        hasProps,
        propObj,
        propVal,
        slider=True,
        spin=True,
        showLimits=True,
        editLimits=True,
        mousewheel=False,
        **kwargs):
    """Creates and returns a widget allowing the user to edit the given
    :class:`.Number` property value.

    If both the ``slider`` and ``spin`` arguments are ``True``, a
    :class:`.SliderSpinPanel` widget is returned; otherwise a
    :class:`.FloatSpinCtrl`, or :class:`.FloatSliders` widget is returned.

    
    If both ``slider`` and ``spin`` are ``False``, a :exc:`ValueError` is
    raised.
    

    :arg slider:     Display slider widgets allowing the user to control the
                     bound values.

    :arg spin:       Display spin control widgets allowing the user to control 
                     the bound values.

    :arg showLimits: Show labels displaying the min/max values, if thye are 
                     set on the ``Number`` property.

    :arg editLimits: Allow the user to edit the min/max values.

    :arg mousewheel: If ``True``, mouse wheel events on the spin/slider
                     control(s) will change the value.

    See the :func:`.widgets._String` documentation for details on the
    parameters.
    """

    if not (slider or spin):
        raise ValueError('One of slider or spin must be True')

    minval  = propVal.getAttribute('minval')
    maxval  = propVal.getAttribute('maxval')
    isRange = (minval is not None) and (maxval is not None)

    if (not isRange) or (not slider):
        return _makeSpinBox(parent, hasProps, propObj, propVal, mousewheel)
    
    else:
        return _makeSlider(parent,
                           hasProps,
                           propObj,
                           propVal,
                           spin,
                           showLimits,
                           editLimits,
                           mousewheel)


def _makeSpinBox(parent, hasProps, propObj, propVal, mousewheel):
    """Used by the :func:`_Number` function.

    Creates a :class:`.FloatSpinCtrl` and binds it to the given
    :class:`.PropertyValue` instance.

    See :func:`_Number` for details on the parameters.
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

    if mousewheel: style = floatspin.FSC_MOUSEWHEEL
    else:          style = 0

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


def _makeSlider(parent,
                hasProps,
                propObj,
                propVal,
                showSpin,
                showLimits,
                editLimits,
                mousewheel):
    """Used by the :func:`_Number` function.

    Creates and returns a :class:`.FloatSlider` or :class:`.SliderSpinPanel`,
    and binds it to the given :class:`.PropertyValue` instance.

    See :func:`_Number` for details on the parameters.
    """

    value  = propVal.get()
    minval = propVal.getAttribute('minval')
    maxval = propVal.getAttribute('maxval')

    if   isinstance(propObj, props.Int):  real = False
    elif isinstance(propObj, props.Real): real = True

    if not showSpin:

        if mousewheel: style = floatslider.FS_MOUSEWHEEL
        else:          style = 0
        
        if not real:
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
        style  = 0
        
        if not real:   style |= floatslider.SSP_INTEGER
        if showLimits: style |= floatslider.SSP_SHOW_LIMITS
        if editLimits: style |= floatslider.SSP_EDIT_LIMITS
        if mousewheel: style |= floatslider.SSP_MOUSEWHEEL
        
        slider = floatslider.SliderSpinPanel(
            parent,
            value=value,
            minValue=minval,
            maxValue=maxval,
            style=style)

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
