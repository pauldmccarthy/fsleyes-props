
props.widgets_number module
***************************

A widget for editing a `Number
<Props.Properties_Types#props.properties_types.Number>`_ property.

This module is not intended to be used directly - it is imported into
the `props.widgets <Props.Widgets#module-props.widgets>`_ namespace.

**props.widgets_number._makeSpinBox(parent, hasProps, propObj,
propVal)**

   Creates a ``wx.SpinCtrl`` or ``wx.SpinCtrlDouble`` bound to the
   given `PropertyValue
   <Props.Properties_Value#props.properties_value.PropertyValue>`_
   object.

**props.widgets_number._makeSlider(parent, hasProps, propObj, propVal,
showSpin, showLimits)**

   Creates a `SliderSpinPanel
   <Pwidgets.Floatslider#pwidgets.floatslider.SliderSpinPanel>`_ bound
   to the given `PropertyValue
   <Props.Properties_Value#props.properties_value.PropertyValue>`_
   object.

**props.widgets_number._Number(parent, hasProps, propObj, propVal,
slider=True, spin=True, showLimits=True)**

   Creates and returns a widget allowing the user to edit the given
   `Number <Props.Properties_Types#props.properties_types.Number>`_
   property value.

   See the `_String() <Props.Widgets#props.widgets._String>`_
   documentation for details on the parameters.
