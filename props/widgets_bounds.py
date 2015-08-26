#!/usr/bin/env python
#
# widgets_bounds.py - Create widgets for modifying Bounds properties.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

"""This module provides the :func:`_Bounds` function, which is imported into
the :mod:`widgets` module namespace. It is separated purely to keep the
``widgets`` module file size down.
"""

import wx

import pwidgets.rangeslider as rangeslider


def _Bounds(parent,
            hasProps,
            propObj,
            propVal,
            slider=True,
            spin=True,
            showLimits=True,
            editLimits=True,
            mousewheel=False,
            labels=None,
            **kwargs):
    """Creates and returns a panel containing sliders/spinboxes which
    allow the user to edit the low/high values along each dimension of the
    given :class:`.Bounds` value.

    
    If both the ``slider`` and ``spin`` arguments are ``True``, a
    :class:`.RangeSliderSpinPanel` widget is returned; otherwise
    a :class:`.RangePanel` is returned.

    
    If both ``slider`` and ``spin`` are ``False``, a :exc:`ValueError` is
    raised.
    

    :arg slider:     Display slider widgets allowing the user to control the
                     bound values.

    :arg spin:       Display spin control widgets allowing the user to control 
                     the bound values.

    :arg showLimits: Show the bound limits.

    :arg editLimits: Add buttons allowing the user to edit the bound limits.

    :arg mousewheel: If ``True``, mouse wheel events over the slider/spin
                     controls will change the bounds values.

    :arg labels:     A list of strings of length ``2 * ndims``, where ``ndims``
                     is the number of dimensions on the ``Bounds`` property;
                     the strings are used as labels on the widget.

    
    See the :func:`.widgets._String` documentation for details on the other
    parameters.
    """

    ndims    = propObj._ndims
    panel    = wx.Panel(parent)
    sizer    = wx.BoxSizer(wx.VERTICAL)

    if labels is None:
        labels = [None] * 2 * ndims
    
    panel.SetSizer(sizer)

    for i in range(ndims):
        minDistance = propObj.getConstraint(hasProps, 'minDistance')
        minval      = propVal.getMin(i)
        maxval      = propVal.getMax(i)
        loval       = propVal.getLo(i)
        hival       = propVal.getHi(i)

        if minDistance is None: minDistance = 0

        if slider and spin:

            if minval is None: minval = loval
            if maxval is None: maxval = hival
        
            slider = rangeslider.RangeSliderSpinPanel(
                panel,
                minValue=minval,
                maxValue=maxval,
                lowValue=loval,
                highValue=hival,
                lowLabel=labels[i * 2],
                highLabel=labels[i * 2 + 1],
                minDistance=minDistance, 
                showLimits=showLimits,
                editLimits=editLimits,
                mousewheel=mousewheel)
        else:
            if slider:
                widgetType = 'slider'
                if minval is None: minval = loval
                if maxval is None: maxval = hival                
            elif spin:
                widgetType = 'spin'
            else: raise ValueError('One of slider or spin must be True')
            
            slider = rangeslider.RangePanel(
                panel,
                widgetType,
                minValue=minval,
                maxValue=maxval,
                lowValue=loval,
                highValue=hival,
                lowLabel=labels[i * 2],
                highLabel=labels[i * 2 + 1],
                minDistance=minDistance,
                mousewheel=mousewheel) 

        sizer.Add(slider, flag=wx.EXPAND)

        _boundBind(hasProps, propObj, slider, propVal, i, editLimits)

    panel.Layout()
    return panel


def _boundBind(hasProps, propObj, sliderPanel, propVal, axis, editLimits):
    """Called by the :func:`_Bounds` function.

    Binds the given :class:`.RangeSliderSpinPanel` or :class:`.RangePanel` to
    one axis of the given :class:`.BoundsValueList` so that changes in one are
    propagated to the other.

    :param hasProps:    The owning :class:`.HasProperties` instance.
    
    :param propObj:     The :class:`.Bounds` instance.
    
    :param sliderPanel: The :class:`.RangeSliderSpinPanel`/:class:`.RangePanel`
                        instance.
    
    :param propVal:     The :class:`.BoundsValueList` instance.
    
    :param axis:        The 0-indexed axis of the :class:`.Bounds` value.

    :param editLimits: If ``True`` assumes that the ``sliderPanel`` has been
                        configured to allow the user to edit the bound limits.
    """

    
    lowProp    = propVal.getPropertyValueList()[axis * 2]
    highProp   = propVal.getPropertyValueList()[axis * 2 + 1]

    lowName    = 'BoundBind_{}_{}'.format(id(sliderPanel), id(lowProp))
    highName   = 'BoundBind_{}_{}'.format(id(sliderPanel), id(highProp))

    def lowGuiUpdate(value, *a):
        if sliderPanel.GetLow() == value: return
        sliderPanel.SetLow(value)
        
    def highGuiUpdate(value, *a):
        if sliderPanel.GetHigh() == value: return
        sliderPanel.SetHigh(value)

    def propUpdate(ev):
        lowProp .set(ev.low)
        highProp.set(ev.high)
        ev.Skip()

    def updateSliderRange(ctx, att, *a):

        if att not in ('minval', 'maxval'):
            return
        
        minval = propVal.getMin(axis)
        maxval = propVal.getMax(axis)

        if minval is not None: sliderPanel.SetMin(minval)
        if maxval is not None: sliderPanel.SetMax(maxval) 

    def updatePropRange(ev):
        propVal.setMin(axis, ev.min)
        propVal.setMax(axis, ev.max)
        ev.Skip()

    sliderPanel.Bind(rangeslider.EVT_RANGE, propUpdate)

    lowProp .addListener(lowName,  lowGuiUpdate,  weak=False)
    highProp.addListener(highName, highGuiUpdate, weak=False)

    lowProp .addAttributeListener(lowName,  updateSliderRange, weak=False)
    highProp.addAttributeListener(highName, updateSliderRange, weak=False)

    if editLimits:
        sliderPanel.Bind(rangeslider.EVT_RANGE_LIMIT, updatePropRange)

    def onDestroy(ev):
        lowProp .removeListener(         lowName)
        highProp.removeListener(         highName)
        lowProp .removeAttributeListener(lowName)
        highProp.removeAttributeListener(highName)
        ev.Skip()
        
    sliderPanel.Bind(wx.EVT_WINDOW_DESTROY, onDestroy)
