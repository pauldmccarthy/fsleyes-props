
props.widgets_bounds module
***************************

Create widgets for modifying `Bounds
<Props.Properties_Types#props.properties_types.Bounds>`_ properties.

This module is not intended to be used directly - it is imported into
the `props.widgets <Props.Widgets#module-props.widgets>`_ namespace.

**props.widgets_bounds._boundBind(hasProps, propObj, sliderPanel,
propVal, axis)**

   Binds the given `RangeSliderSpinPanel
   <Pwidgets.Rangeslider#pwidgets.rangeslider.RangeSliderSpinPanel>`_
   to one axis of the given `BoundsValueList
   <Props.Properties_Types#props.properties_types.BoundsValueList>`_
   so that changes in one are propagated to the other.

   :Parameters:
      * **hasProps** -- The owning `HasProperties
        <Props.Properties#props.properties.HasProperties>`_ instance.

      * **propObj** -- The `Bounds
        <Props.Properties_Types#props.properties_types.Bounds>`_
        instance.

      * **sliderPanel** -- The `RangeSliderSpinPanel
        <Pwidgets.Rangeslider#pwidgets.rangeslider.RangeSliderSpinPanel>`_
        instance.

      * **propVal** -- The `BoundsValueList
        <Props.Properties_Types#props.properties_types.BoundsValueList>`_
        instance.

      * **axis** -- The 0-indexed axis of the `Bounds
        <Props.Properties_Types#props.properties_types.Bounds>`_
        value.

**props.widgets_bounds._Bounds(parent, hasProps, propObj, propVal,
slider=True, spin=True, showLimits=True)**

   Creates and returns a panel containing sliders/spinboxes which
   allow the user to edit the low/high values along each dimension of
   the given `Bounds
   <Props.Properties_Types#props.properties_types.Bounds>`_ value.
