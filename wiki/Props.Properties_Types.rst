
props.properties_types module
*****************************

Definitions for different property types.

This module provides a number of `PropertyBase
<Props.Properties#props.properties.PropertyBase>`_ subclasses which
define properties of different types.

**class props.properties_types.Object(**kwargs)**

   Bases: `props.properties.PropertyBase
   <Props.Properties#props.properties.PropertyBase>`_

   A property which encapsulates any value.

   Create a ``Object`` property. If an ``equalityFunc`` is not
   provided, any writes to this property will be treated as if the
   value has changed (and any listeners will be notified).

**class props.properties_types.Boolean(**kwargs)**

   Bases: `props.properties.PropertyBase
   <Props.Properties#props.properties.PropertyBase>`_

   A property which encapsulates a ``bool`` value.

   Create a ``Boolean`` property.

   If the ``default`` ``kwarg`` is not provided, a default value of
   ``False`` is used.

   :Parameters:
      **kwargs** -- All passed through to the `PropertyBase
      <Props.Properties#props.properties.PropertyBase>`_ constructor.

   **cast(instance, attributes, value)**

      Overrides `cast
      <Props.Properties#props.properties.PropertyBase.cast>`_. Casts
      the given value to a ``bool``.

**class props.properties_types.Number(minval=None, maxval=None,
clamped=False, editLimits=False, **kwargs)**

   Bases: `props.properties.PropertyBase
   <Props.Properties#props.properties.PropertyBase>`_

   Base class for the ``Int`` and ``Real`` classes.

   A property which represents a number.  Don't use/subclass this,
   use/subclass one of ``Int`` or ``Real``.

   Define a ``Number`` property.

   :Parameters:
      * **minval** (*number*) -- Minimum valid value

      * **maxval** (*number*) -- Maximum valid value

      * **clamped** (*bool*) -- If ``True``, the value will be clamped
        to its min/max bounds.

      * **editLimits** (*bool*) -- If ``True``, widgets created to
        modify ``Number`` properties will allow the user to change the
        min/max values.

      * **kwargs** -- Passed through to the `PropertyBase
        <Props.Properties#props.properties.PropertyBase>`_
        constructor. If a ``default`` value is not provided, it is set
        to something sensible.

   **validate(instance, attributes, value)**

      Overrides `validate()
      <Props.Properties#props.properties.PropertyBase.validate>`_.
      Validates the given number.

      Calls the `validate()
      <Props.Properties#props.properties.PropertyBase.validate>`_
      method. Then, if the ``minval`` and/or ``maxval`` constraints
      have been set, and the given value is not within those values, a
      ``ValueError`` is raised.

      :Parameters:
         * **instance** -- The owning `HasProperties
           <Props.Properties#props.properties.HasProperties>`_
           instance (or ``None`` for unbound property values).

         * **attributes** (*dict*) -- Dictionary containing property
           constraints.

         * **value** (*number*) -- The value to validate.

   **cast(instance, attributes, value)**

      Overrides `cast()
      <Props.Properties#props.properties.PropertyBase.cast>`_.

      If the ``clamped`` constraint is ``True`` and the ``minval``
      and/or ``maxval`` have been set, this function ensures that the
      given value lies within the ``minval`` and ``maxval`` limits.

**class props.properties_types.Int(**kwargs)**

   Bases: ``props.properties_types.Number``

   A property which encapsulates an integer.

   Define an ``Int`` property. See the ``Number`` constructor
   documentation for keyword arguments.

   **cast(instance, attributes, value)**

      Overrides ``Number.cast()``. Casts the given value to an
      ``int``, and then passes the value to ``Number.cast()``.

**class props.properties_types.Real(precision=1e-09, **kwargs)**

   Bases: ``props.properties_types.Number``

   A property which encapsulates a floating point number.

   Define a ``Real`` property. See the ``Number`` constructor
   documentation for keyword arguments.

   **cast(instance, attributes, value)**

      Overrides ``Number.cast()``. Casts the given value to a
      ``float``, and then passes the value to ``Number.cast()``.

   **_Real__equals(a, b)**

**class props.properties_types.Percentage(**kwargs)**

   Bases: ``props.properties_types.Real``

   A property which represents a percentage.

   A ``Percentage`` property is just a ``Real`` property with a
   default minimum value of ``0`` and maximum value of ``100``.

**class props.properties_types.String(minlen=None, maxlen=None,
**kwargs)**

   Bases: `props.properties.PropertyBase
   <Props.Properties#props.properties.PropertyBase>`_

   A property which encapsulates a string.

   Define a ``String`` property.

   :Parameters:
      * **minlen** (*int*) -- Minimum valid string length.

      * **maxlen** (*int*) -- Maximum valid string length.

   **cast(instance, attributes, value)**

      Overrides `cast()
      <Props.Properties#props.properties.PropertyBase.cast>`_.

      Casts the given value to a string. If the given value is the
      empty string, it is replaced with ``None``.

   **validate(instance, attributes, value)**

      Overrides `validate()
      <Props.Properties#props.properties.PropertyBase.validate>`_.

      Passes the given value to `validate()
      <Props.Properties#props.properties.PropertyBase.validate>`_.
      Then, if either the ``minlen`` or ``maxlen`` constraints have
      been set, and the given value has length less than ``minlen`` or
      greater than ``maxlen``, raises a ``ValueError``.

**class props.properties_types.Choice(choices=None, labels=None,
**kwargs)**

   Bases: `props.properties.PropertyBase
   <Props.Properties#props.properties.PropertyBase>`_

   A property which may only be set to one of a set of predefined
   values.

   Individual choices can be enabled/disabled via the
   ``enableChoice()`` and ``disableChoice()`` methods. The
   ``choiceEnabled`` property constraint/attribute contains a list of
   boolean values representing the enabled/disabled state of each
   choice.

   Define a ``Choice`` property.

   As an alternative to passing in separate ``choice`` and
   ``choiceLabels`` lists, you may pass in a dict as the ``choice``
   parameter. The keys will be used as the choices, and the values as
   labels. Make sure to use a ``collections.OrderedDict`` if the
   display order is important.

   :Parameters:
      * **choices** (*list*) -- List of values, the possible values
        that this property can take.

      * **labels** (*list*) -- List of string labels, one for each
        choice, to be used for display purposes.

   **enableChoice(choice, instance=None)**

      Enables the given choice.

   **disableChoice(choice, instance=None)**

      Disables the given choice. An attempt to set the property to a
      disabled value will result in a ``ValueError``.

   **choiceEnabled(choice, instance=None)**

      Returns ``True`` if the given choice is enabled, ``False``
      otherwise.

   **getChoices(instance=None)**

      Returns a list of the current choices.

   **getLabels(instance=None)**

      Returns a list of the current choice labels.

   **setLabel(choice, label, instance=None)**

      Sets the label for the specified choice.

   **_updateChoices(choices, labels, instance=None)**

   **setChoices(choices, labels=None, instance=None)**

      Sets the list of possible choices (and their labels, if not
      None).

   **addChoice(choice, label=None, instance=None)**

      Adds a new choice to the list of possible choices.

   **validate(instance, attributes, value)**

      Raises a ``ValueError`` if the given value is not one of the
      possible values for this ``Choice`` property.

**class props.properties_types.FilePath(exists=False, isFile=True,
suffixes=[], **kwargs)**

   Bases: ``props.properties_types.String``

   A property which represents a file or directory path.

   There is currently no support for validating a path which may be
   either a file or a directory - only one or the other.

   Define a ``FilePath`` property.

   :Parameters:
      * **exists** (*bool*) -- If ``True``, the path must exist.

      * **isFile** (*bool*) -- If ``True``, the path must be a file.
        If ``False``, the path must be a directory. This check is only
        performed if ``exists`` is ``True``.

      * **suffixes** (*list*) -- List of acceptable file suffixes
        (only relevant if ``isFile`` is ``True``).

   **validate(instance, attributes, value)**

      Overrides `validate()
      <Props.Properties#props.properties.PropertyBase.validate>`_.

      If the ``exists`` constraint is not ``True``, does nothing.
      Otherwise, if ``isFile`` is ``False`` and the given value is not
      a path to an existing directory, a ``ValueError`` is raised.

      If ``isFile`` is ``True``, and the given value is not a path to
      an existing file (which, if ``suffixes`` is not None, must end
      in one of the specified suffixes), a ``ValueError`` is raised.

**class props.properties_types.List(listType=None, minlen=None,
maxlen=None, embed=False, **kwargs)**

   Bases: `props.properties.ListPropertyBase
   <Props.Properties#props.properties.ListPropertyBase>`_

   A property which represents a list of items, of another property
   type.

   If you use ``List`` properties, you really should read the
   documentation for the `PropertyValueList
   <Props.Properties_Value#props.properties_value.PropertyValueList>`_,
   as it contains important usage information.

   Define a ``List`` property.

   :Parameters:
      * **listType** -- A `PropertyBase
        <Props.Properties#props.properties.PropertyBase>`_ type,
        specifying the values allowed in the list. If ``None``,
        anything can be stored in the list,  but no casting or
        validation will occur.

      * **minlen** (*int*) -- Minimum list length.

      * **maxlen** (*int*) -- Maximum list length.

      * **embed** (*bool*) -- If ``True``, when a graphical interface
        is made to edit this list property, a widget is embedded
        directly into the parent GUI. Otherwise, a button is embedded
        which, when clicked, opens a dialog allowing the user to edit
        the list.

   **validate(instance, attributes, value)**

      Overrides `validate()
      <Props.Properties#props.properties.PropertyBase.validate>`_.

      Checks that the given value (which should be a list) meets the
      ``minlen``/``maxlen`` constraints. Raises a ``ValueError`` if it
      does not.

**class props.properties_types.Colour(**kwargs)**

   Bases: `props.properties.PropertyBase
   <Props.Properties#props.properties.PropertyBase>`_

   A property which represents a RGBA colour, stored as four floating
   point values in the range ``0.0 - 1.0``.

   Create a ``Colour`` property.

   If the ``default`` ``kwarg`` is not provided, the default is set to
   white.

   :Parameters:
      **kwargs** -- All passed through to the `PropertyBase
      <Props.Properties#props.properties.PropertyBase>`_ constructor.

   **validate(instance, attributes, value)**

      Checks the given ``value``, and raises a ``ValueError`` if it
      does not consist of three floating point numbers in the range
      ``(0.0 - 1.0)``.

   **cast(instance, attributes, value)**

      Ensures that the given ``value`` contains three or four floating
      point numbers, in the range ``(0.0 - 1.0)``.

**class props.properties_types.ColourMap(cmapNames=None, **kwargs)**

   Bases: `props.properties.PropertyBase
   <Props.Properties#props.properties.PropertyBase>`_

   A property which encapsulates a ``matplotlib.colors.Colormap``.

   ColourMap values may be specified either as a
   ``matplotlib.colors.Colormap`` instance, or as a string containing
   the name of a registered colour map instance.

   Define a ``ColourMap`` property.

   If a default value is not given, the ``matplotlib.cm.Greys_r``
   colour map is used. Or, if ``cmapNames`` is not ``None``, the first
   name is used.

   :Parameters:
      **cmapNames** -- List of strings, the names of possible colour
      maps (must be registered with the ``matplotlib.cm`` module). If
      ``None``, all registered colour maps are used.

   **cast(instance, attributes, value)**

      Overrides `cast()
      <Props.Properties#props.properties.PropertyBase.cast>`_.

      If the provided value is a string, an attempt is made to convert
      it to a colour map, via the ``matplotlib.cm.get_cmap()``
      function.

**class props.properties_types.BoundsValueList(*args, **kwargs)**

   Bases: `props.properties_value.PropertyValueList
   <Props.Properties_Value#props.properties_value.PropertyValueList>`_

   A list of values which represent bounds along a number of
   dimensions (up to 4).

   This class is used by the ``Bounds`` property to encapsulate
   bounding values for an arbitrary number of dimensions. For ``N+1``
   dimensions, the bounding values are stored as a list:

   ::

      [lo0, hi0, lo1, hi1, ..., loN, hiN]

   This class just adds some convenience methods and attributes to the
   `PropertyValueList
   <Props.Properties_Value#props.properties_value.PropertyValueList>`_
   superclass.  For a single dimension, a bound object has a ``lo``
   value and a ``hi`` value, specifying the bounds along that
   dimension. To make things confusing, each dimension also has
   ``min`` and ``max`` constraints, which define the minimum/maximum
   values that the ``lo`` and ``high`` values may take for that
   dimension.

   Some dynamic attributes are available on ``BoundsValueList``
   objects, allowing access to and assignment of bound values and
   constraints. Dimensions ``0, 1, 2, 3`` respectively map to
   identifiers ``x, y, z, t``. If an attempt is made to access/assign
   an attribute corresponding to a dimension which does not exist on a
   particular ``BoundsValueList`` instance (e.g. attribute ``t`` on a
   3-dimensional list), an ``IndexError`` will be raised. Here is an
   example of dynamic bound attribute access:

   ::

      class MyObj(props.HasProperties):
          myBounds = Bounds(ndims=4)

      obj = MyObj()

      # set/access lo/hi values together
      xlo, xhi = obj.mybounds.x
      obj.mybounds.z = (25, 30)

      # set/access lo/hi values separately
      obj.mybounds.xlo = 2
      obj.mybounds.zhi = 50

      # get the length of the bounds for a dimension
      ylen = obj.mybounds.ylen

      # set/access the minimum/maximum 
      # constraints for a dimension
      obj.mybounds.xmin = 0
      tmax = obj.mybounds.tmax

   **getLo(axis)**

      Return the low value for the given (0-indexed) axis.

   **getHi(axis)**

      Return the high value for the given (0-indexed) axis.

   **getRange(axis)**

      Return the (low, high) values for the given (0-indexed) axis.

   **getLen(axis)**

      Return the distance between the low and high values for the
      specified axis.

   **setLo(axis, value)**

      Set the low value for the specified axis.

   **setHi(axis, value)**

      Set the high value for the specified axis.

   **setRange(axis, loval, hival)**

      Set the low and high values for the specified axis.

   **getMin(axis)**

      Return the minimum value (the low limit) for the specified axis.

   **getMax(axis)**

      Return the maximum value (the high limit) for the specified
      axis.

   **setMin(axis, value)**

      Set the minimum value for the specified axis.

   **setMax(axis, value)**

      Set the maximum value for the specified axis.

   **getLimits(axis)**

      Return (minimum, maximum) limit values for the specified axis.

   **setLimits(axis, minval, maxval)**

      Set the minimum and maximum limit values for the specified axis.

**class props.properties_types.Bounds(ndims=1, real=True,
minDistance=None, editLimits=False, labels=None, **kwargs)**

   Bases: ``props.properties_types.List``

   Property which represents numeric bounds in any number of
   dimensions, as long as that number is no more than 4.

   ``Bound`` values are stored in a ``BoundsValueList``, a list of
   integer or floating point values, with two values (lo, hi) for each
   dimension.

   ``Bound`` values may also have bounds of their own, i.e.
   minimium/maximum values that the bound values can take. These
   bound-limits are referred to as 'min' and 'max', and can be set via
   the ``BoundsValueList.setMin()`` and ``BoundsValueList.setMax()``
   methods. The advantage to using these methods, instead of using,
   for example, `setItemConstraint()
   <Props.Properties#props.properties.HasProperties.setItemConstraint>`_,
   is that if you use the latter you will have to set the constraints
   on both the low and the high values.

   Define a ``Bounds`` property.

   :Parameters:
      * **ndims** (*int*) -- Number of dimensions. This is (currently)
        not a property constraint, hence it cannot  be changed.

      * **real** (*bool*) -- If ``True``, the point values are stored
        as ``Real`` values; otherwise, they are stored as ``Int``
        values.

      * **minDistance** (*float*) -- Minimum distance to be maintained
        between the low/high values for each dimension.

      * **editLimits** (*bool*) -- If ``True``, widgets created to
        edit this ``Bounds`` will allow the user to edit the min/max
        limits.

      * **labels** (*list*) -- List of labels of length ``2*ndims``,
        containing (low, high) labels for each dimension.

   **_makePropVal(instance)**

      Overrides `_makePropVal()
      <Props.Properties#props.properties.ListPropertyBase._makePropVal>`_.

      Creates and returns a ``BoundsValueList`` instead of a
      ``PropertyValueList``, so callers get to use the convenience
      methods/attributes defined in the BVL class.

   **validate(instance, attributes, value)**

      Overrides `validate()
      <Props.Properties#props.properties.PropertyBase.validate>`_.

      Raises a ``ValueError`` if the given value (a list of min/max
      values) is of the wrong length or data type, or if any of the
      min values are greater than the corresponding max value.

**class props.properties_types.PointValueList(*args, **kwargs)**

   Bases: `props.properties_value.PropertyValueList
   <Props.Properties_Value#props.properties_value.PropertyValueList>`_

   A list of values which represent a point in some n-dimensional (up
   to 4) space.

   This class is used by the ``Point`` property to encapsulate point
   values for between 1 and 4 dimensions.

   This class just adds some convenience methods and attributes to the
   `PropertyValueList
   <Props.Properties_Value#props.properties_value.PropertyValueList>`_
   superclass.

   The point values for each dimension may be queried/assigned via the
   dynamic attributes ``x, y, z, t``, which respectively map to
   dimensions ``0, 1, 2, 3``. When querying/assigning point values,
   you may use GLSL-like swizzling. For example:

   ::

      class MyObj(props.HasProperties):
          mypoint = props.Point(ndims=3)

      obj = MyObj()

      y,z = obj.mypoint.yz

      obj.mypoint.zxy = (3,6,1)

   **getPos(axis)**

      Return the point value for the specified (0-indexed) axis.

   **setPos(axis, value)**

      Set the point value for the specified axis.

   **getMin(axis)**

      Get the minimum limit for the specified axis.

   **getMax(axis)**

      Get the maximum limit for the specified axis.

   **getLimits(axis)**

      Get the (minimum, maximum) limits for the specified axis.

   **setMin(axis, value)**

      Set the minimum limit for the specified axis.

   **setMax(axis, value)**

      Set the maximum limit for the specified axis.

   **setLimits(axis, minval, maxval)**

      Set the minimum and maximum limits for the specified axis.

**class props.properties_types.Point(ndims=2, real=True,
editLimits=False, labels=None, **kwargs)**

   Bases: ``props.properties_types.List``

   A property which represents a point in some n-dimensional (up to 4)
   space.

   ``Point`` property values are stored in a ``PointValueList``, a
   list of integer or floating point values, one for each dimension.

   Define a ``Point`` property.

   :Parameters:
      * **ndims** (*int*) -- Number of dimensions.

      * **real** (*bool*) -- If ``True`` the point values are stored
        as ``Real`` values, otherwise they are stored as ``Int``
        values.

      * **editLimits** (*bool*) -- If ``True``, widgets created to
        edit this ``Point`` will allow the user to edit the min/max
        limits.

      * **labels** (*list*) -- List of labels, one for each dimension.

   **_makePropVal(instance)**

      Overrides `_makePropVal()
      <Props.Properties#props.properties.ListPropertyBase._makePropVal>`_.

      Creates and returns a ``PointValueList`` instead of a
      `PropertyValueList
      <Props.Properties_Value#props.properties_value.PropertyValueList>`_,
      so callers get to use the convenience methods/attributes defined
      in the PVL class.
