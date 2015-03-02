
props.widgets_point module
**************************

Create widgets for modifying `Point
<Props.Properties_Types#props.properties_types.Point>`_ properties.

This module is not intended to be used directly - it is imported into
the `props.widgets <Props.Widgets#module-props.widgets>`_ namespace.

**props.widgets_point._pointBind(hasProps, propObj, propVal, slider,
dim)**

   Binds the given `SliderSpinPanel
   <Pwidgets.Floatslider#pwidgets.floatslider.SliderSpinPanel>`_ to
   one dimension of the given `PointValueList
   <Props.Properties_Types#props.properties_types.PointValueList>`_ so
   that changes in one are propagated to the other.

   :Parameters:
      * **hasProps** -- The owning `HasProperties
        <Props.Properties#props.properties.HasProperties>`_ instance.

      * **propObj** -- The `Point
        <Props.Properties_Types#props.properties_types.Point>`_
        instance.

      * **sliderPanel** -- The `SliderSpinPanel
        <Pwidgets.Floatslider#pwidgets.floatslider.SliderSpinPanel>`_
        instance.

      * **propVal** -- The `PointValueList
        <Props.Properties_Types#props.properties_types.PointValueList>`_
        instance.

      * **dim** -- The 0-indexed dimension of the `Point
        <Props.Properties_Types#props.properties_types.Point>`_ value.

**props.widgets_point._Point(parent, hasProps, propObj, propVal)**

   Creates and returns a widget allowing the user to edit the values
   for each dimension of the given `Point
   <Props.Properties_Types#props.properties_types.Point>`_ property
   value.
