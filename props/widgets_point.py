#!/usr/bin/env python
#
# widgets_point.py - Create widgets for modifying Point properties.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :func:`_Point` function, which is imported into
the :mod:`widgets` module namespace. It is separated purely to keep the
``widgets`` module file size down.
"""


import wx

import pwidgets.floatslider as floatslider

import widgets


def _Point(parent,
           hasProps,
           propObj,
           propVal,
           showLimits=True,
           editLimits=True):
    """Creates and returns a :class:`.SliderSpinPanel` allowing the user to
    edit the low/high values along each dimension of the given
    :class:`.Point` property value.

    :arg showLimits: Show labels displaying the point limits.
    
    :arg editLimits: Show buttons allowing the user to edit the point limits.

    See the :func:`.widgets._String` documentation for details on the other
    parameters. 
    """
    panel = wx.Panel(parent)
    sizer = wx.BoxSizer(wx.VERTICAL)
    panel.SetSizer(sizer)

    ndims  = propObj._ndims
    real   = propObj._real
    labels = propObj._labels

    if labels is None: labels = [None] * ndims

    for dim in range(len(propVal)):

        slider = floatslider.SliderSpinPanel(
            panel,
            real=real,
            value=propVal[dim],
            minValue=propVal.getMin(dim),
            maxValue=propVal.getMax(dim),
            label=labels[dim],
            showLimits=showLimits,
            editLimits=editLimits)

        sizer.Add(slider, flag=wx.EXPAND)

        _pointBind(hasProps, propObj, propVal, slider, dim)

    panel.Layout()

    return panel


def _pointBind(hasProps, propObj, propVal, slider, dim, editLimits):
    """Called by the :func:`_Point` function.

    Binds the given :class:`.SliderSpinPanel` to one dimension of the given
    :class:`.PointValueList` so that changes in one are propagated to the
    other.

    :arg slider: The :class:`.SliderSpinPanel` instance.
    
    :arg dim:    The 0-indexed dimension of the :class:`.Point` value.

    See :func:`_Point` for details on the other arguments.
    """

    dimPropVal = propVal.getPropertyValueList()[dim]
    
    widgets._propBind(hasProps,
                      propObj._listType,
                      dimPropVal,
                      slider,
                      floatslider.EVT_SSP_VALUE)

    def propLimitsChanged(*a):
        minval = propVal.getMin(dim)
        maxval = propVal.getMax(dim)
        
        if minval is not None: slider.SetMin(minval)
        if maxval is not None: slider.SetMax(maxval)

    def sliderLimitsChanged(ev):
        propVal.setMin(dim, ev.min)
        propVal.setMax(dim, ev.max)
        ev.Skip()

    if editLimits:
        slider.Bind(floatslider.EVT_SSP_LIMIT, sliderLimitsChanged)

    lName = 'PointLimits_{}_{}'.format(id(slider), dim)

    dimPropVal.addAttributeListener(lName, propLimitsChanged, weak=False)

    def onDestroy(ev):
        dimPropVal.removeAttributeListener(lName)
        ev.Skip()

    slider.Bind(wx.EVT_WINDOW_DESTROY, onDestroy)
