
props.widgets module
********************

Generate wx GUI widgets for `PropertyBase
<Props.Properties#props.properties.PropertyBase>`_ objects.

This module provides the following functions:

..

   * ``makeWidget()``: Creates a widget for a ``PropertyBase`` object.
     This function is called by functions in the `props.build
     <Props.Build#module-props.build>`_ module when they automatically
     build a GUI for the properties of a `HasProperties
     <Props.Properties#props.properties.HasProperties>`_ instance.

   * ``makeSyncWidget()``: Creates a widget to control synchronisation
     of a ``PropertyBase`` object of a `SyncableHasProperties
     <Props.Syncable#props.syncable.SyncableHasProperties>`_ instance
     with its parent.

   * ``bindWidget()``: Binds an existing widget with a
     ``PropertyBase`` instance.

**props.widgets._propBind(hasProps, propObj, propVal, guiObj, evType,
widgetGet=None, widgetSet=None, widgetDestroy=None)**

   Binds a `PropertyValue
   <Props.Properties_Value#props.properties_value.PropertyValue>`_ to
   a widget.

   Sets up event callback functions such that, on a change to the
   given property value, the value displayed by the given GUI widget
   will be updated. Similarly, whenever a GUI event of the specified
   type (or types - you may pass in a list of event types) occurs, the
   property value will be set to the value controlled by the GUI
   widget.

   :Parameters:
      * **hasProps** -- The owning `HasProperties
        <Props.Properties#props.properties.HasProperties>`_ instance.

      * **propObj** -- The `PropertyBase
        <Props.Properties#props.properties.PropertyBase>`_ property
        type.

      * **propVal** -- The `PropertyValue
        <Props.Properties_Value#props.properties_value.PropertyValue>`_
        to  be bound.

      * **guiObj** -- The ``wx`` GUI widget

      * **evType** -- The event type (or list of event types) which
        should  be listened for on the ``guiObj``.

      * **widgetGet** -- Function which returns the current widget
        value. If ``None``, the ``guiObj.GetValue`` method is used.

      * **widgetSet** -- Function which sets the current widget value.
        If ``None``, the ``guiObj.SetValue`` method is used.

      * **widgetDestroy** -- Function which is called if/when the
        widget is destroyed. Must accept one argument - the
        ``wx.Event`` object.

**props.widgets._setupValidation(widget, hasProps, propObj, propVal)**

   Configures input validation for the given widget, which is assumed
   to be bound to the given ``propVal`` (a `PropertyValue
   <Props.Properties_Value#props.properties_value.PropertyValue>`_
   object).

   Any changes to the property value are validated and, if the new
   value is invalid, the widget background colour is changed to a
   light red, so that the user is aware of the invalid-ness.

   This function is only used for a few different property types,
   namely `String
   <Props.Properties_Types#props.properties_types.String>`_, `FilePath
   <Props.Properties_Types#props.properties_types.FilePath>`_, and
   `Number <Props.Properties_Types#props.properties_types.Number>`_
   properties.

   :Parameters:
      * **widget** -- The ``wx`` GUI widget.

      * **hasProps** -- The owning `HasProperties
        <Props.Properties#props.properties.HasProperties>`_ instance.

      * **propObj** -- The `PropertyBase
        <Props.Properties#props.properties.PropertyBase>`_ property
        type.

      * **propVal** -- The `PropertyValue
        <Props.Properties_Value#props.properties_value.PropertyValue>`_
        instance.

**props.widgets._FilePath(parent, hasProps, propObj, propVal,
**kwargs)**

   Creates and returns a panel containing a ``wx.TextCtrl`` and a
   ``wx.Button``. The button, when clicked, opens a file dialog
   allowing the user to choose a file/directory to open, or a location
   to save (this depends upon how the ``propObj`` [a `FilePath
   <Props.Properties_Types#props.properties_types.FilePath>`_] object
   was configured).

   See the ``_String()`` documentation for details on the parameters.

**props.widgets._Choice(parent, hasProps, propObj, propVal,
**kwargs)**

   Creates and returns a ``wx.Combobox`` allowing the user to set the
   given ``propObj`` (props.Choice) object.

   See the ``_String()`` documentation for details on the parameters.

**props.widgets._String(parent, hasProps, propObj, propVal,
**kwargs)**

   Creates and returns a ``wx.TextCtrl`` object, allowing the user to
   edit the given ``propVal`` (managed by a `String
   <Props.Properties_Types#props.properties_types.String>`_) object.

   :Parameters:
      * **parent** -- The ``wx`` parent object.

      * **hasProps** -- The owning `HasProperties
        <Props.Properties#props.properties.HasProperties>`_ instance.

      * **propObj** -- The `PropertyBase
        <Props.Properties#props.properties.PropertyBase>`_ instance
        (assumed to be a `String
        <Props.Properties_Types#props.properties_types.String>`_).

      * **propVal** -- The `PropertyValue
        <Props.Properties_Value#props.properties_value.PropertyValue>`_
        instance.

      * **kwargs** -- Type-specific options.

**props.widgets._Real(parent, hasProps, propObj, propVal, **kwargs)**

   Creates and returns a widget allowing the user to edit the given
   `Real <Props.Properties_Types#props.properties_types.Real>`_
   property value. See the `props.widgets_number
   <Props.Widgets_Number#module-props.widgets_number>`_ module.

   See the ``_String()`` documentation for details on the parameters.

**props.widgets._Int(parent, hasProps, propObj, propVal, **kwargs)**

   Creates and returns a widget allowing the user to edit the given
   `Int <Props.Properties_Types#props.properties_types.Int>`_ property
   value. See the `props.widgets_number
   <Props.Widgets_Number#module-props.widgets_number>`_ module.

   See the ``_String()`` documentation for details on the parameters.

**props.widgets._Percentage(parent, hasProps, propObj, propVal,
**kwargs)**

   Creates and returns a widget allowing the user to edit the given
   `Percentage
   <Props.Properties_Types#props.properties_types.Percentage>`_
   property value. See the `props.widgets_number
   <Props.Widgets_Number#module-props.widgets_number>`_ module.

   See the ``_String()`` documentation for details on the parameters.

**props.widgets._Boolean(parent, hasProps, propObj, propVal,
**kwargs)**

   Creates and returns a ``wx.CheckBox``, allowing the user to set the
   given `Boolean
   <Props.Properties_Types#props.properties_types.Boolean>`_ property
   value.

   See the ``_String()`` documentation for details on the parameters.

**props.widgets._Colour(parent, hasProps, propObj, propVal,
**kwargs)**

   Creates and returns a ``wx.ColourPickerCtrl`` widget, allowing the
   user to modify the given `props.properties_types.Colour
   <Props.Properties_Types#props.properties_types.Colour>`_ value.

**props.widgets._makeColourMapBitmap(cmap)**

   Makes a little bitmap image from a ``Colormap`` instance.

**props.widgets._ColourMap(parent, hasProps, propObj, propVal,
**kwargs)**

   Creates and returns a combobox, allowing the user to change the
   value of the given `ColourMap
   <Props.Properties_Types#props.properties_types.ColourMap>`_
   property value.

   See also the ``_makeColourMapComboBox()`` function.

**props.widgets._LinkBox(parent, hasProps, propObj, propVal,
**kwargs)**

   Creates a 'link' button which toggles synchronisation between the
   property on the given ``hasProps`` instance, and its parent.

**props.widgets.makeSyncWidget(parent, hasProps, propName, **kwargs)**

   Creates a button which controls synchronisation of the specified
   property on the given ``hasProps`` instance, with the corresponding
   property on its parent.

   See the ``makeWidget()`` function for a description of the
   arguments.

**props.widgets.makeWidget(parent, hasProps, propName, **kwargs)**

   Given ``hasProps`` (a `HasProperties
   <Props.Properties#props.properties.HasProperties>`_ object),
   ``propName`` (the name of a property of ``hasProps``), and
   ``parent``, a GUI object, creates and returns a widget, or a panel
   containing widgets, which may be used to edit the property.

   :Parameters:
      * **parent** -- A ``wx`` object to be used as the parent for the
        generated widget(s).

      * **hasProps** -- A `HasProperties
        <Props.Properties#props.properties.HasProperties>`_ instance.

      * **propName** (*str*) -- Name of the `PropertyBase
        <Props.Properties#props.properties.PropertyBase>`_ property to
        generate a widget for.

      * **kwargs** -- Type specific arguments.

**props.widgets.makeListWidgets(parent, hasProps, propName,
**kwargs)**

   Creates a widget for every value in the given list property.

**props.widgets.bindWidget(widget, hasProps, propName, evTypes,
widgetGet=None, widgetSet=None)**

   Binds the given widget to the specified property. See the
   ``_propBind()`` method for details of the arguments.

**props.widgets.bindListWidgets(widgets, hasProps, propName, evTypes,
widgetSets=None, widgetGets=None)**

   Binds the given sequence of widgets to each of the values in the
   specified list property.
