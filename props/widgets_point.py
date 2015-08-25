#!/usr/bin/env python
#
# widgets_point.py - Create widgets for modifying Point properties.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""Create widgets for modifying :class:`~props.properties_types.Point`
properties.

This module is not intended to be used directly - it is imported into the
:mod:`props.widgets` namespace.
"""

import wx

import pwidgets.floatslider as floatslider

import widgets

def _pointBind(hasProps, propObj, propVal, slider, dim, editLimits):
    """Binds the given :class:`~pwidgets.floatslider.SliderSpinPanel` to
    one dimension of the given :class:`~props.properties_types.PointValueList`
    so that changes in one are propagated to the other.

    :param hasProps:    The owning :class:`~props.properties.HasProperties`
                        instance.
    
    :param propObj:     The :class:`~props.properties_types.Point` instance.
    
    :param sliderPanel: The :class:`~pwidgets.floatslider.SliderSpinPanel`
                        instance.
    
    :param propVal:     The :class:`~props.properties_types.PointValueList`
                        instance.
    
    :param dim:         The 0-indexed dimension of the
                        :class:`~props.properties_types.Point` value.

    :param editLimits:  If ``True`` the ``sliderPanel`` has been configure to
                        allow the user to edit the point limits.    
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


def _Point(
        parent, hasProps, propObj, propVal, showLimits=True, editLimits=True):
    """Creates and returns a widget allowing the user to edit the values for
    each dimension of the given :class:`~props.properties_types.Point`
    property value.
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
