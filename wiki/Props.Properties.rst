
props.properties module
***********************

Python descriptor framework.

This module defines the ``PropertyBase``, ``ListPropertyBase``, and
``HasProperties`` classes, which form the basis for defining class
properties. See also the `properties_value
<Props.Properties_Value#module-props.properties_value>`_ and
`properties_types
<Props.Properties_Types#module-props.properties_types>`_ modules.

**class props.properties._InstanceData(instance, propVal)**

   Bases: ``object``

   An ``_InstanceData`` object is created for every ``PropertyBase``
   object of a ``HasProperties`` instance. It stores references to the
   the instance and the associated property value(s).

**class props.properties.PropertyBase(default=None, validateFunc=None,
equalityFunc=None, required=False, allowInvalid=True, **constraints)**

   Bases: ``object``

   The base class for properties.

   For every ``HasProperties`` object which has this ``PropertyBase``
   object as a property, one ``_InstanceData`` object is created and
   attached as an attribute of the ``HasProperties`` object.

   One important point to note is that a ``PropertyBase`` object may
   exist without being bound to a ``HasProperties`` object (in which
   case it will not create or manage any `PropertyValue
   <Props.Properties_Value#props.properties_value.PropertyValue>`_
   objects). This is useful if you just want validation functionality
   via the ``validate()``, ``getConstraint()`` and ``setConstraint()``
   methods, passing in ``None`` for the instance parameter. Nothing
   else will work properly though.

   Subclasses should:

   ..

      * Ensure that the superclass ``__init__()`` is called.

      * Override the ``validate()`` method to implement any built in
        validation rules, ensuring that the the superclass
        implementation is called first.

      * Override the ``cast()`` method for implicit casting/conversion
        logic (see `Boolean
        <Props.Properties_Types#props.properties_types.Boolean>`_ for
        an example).

   Define a ``PropertyBase`` property.

   :Parameters:
      * **default** -- Default/initial value.

      * **required** (*bool*) -- Boolean determining whether or not
        this property must have a value. May alternately be a function
        which accepts one parameter, the owning ``HasProperties``
        instance, and returns ``True`` or ``False``.

      * **validateFunc** -- Custom validation function. Must accept
        three parameters: a reference to the ``HasProperties``
        instance, the owner of this property; a dictionary containing
        the constraints for this property; and the new property value.
        Should return ``True`` if the property value is valid,
        ``False`` otherwise.

      * **equalityFunc** -- Function for testing equality of two
        property values. See `PropertyValue
        <Props.Properties_Value#props.properties_value.PropertyValue>`_.

      * **allowInvalid** -- If ``False``, a ``ValueError`` will be
        raised on all attempts to set this property to an invalid
        value. This does not guarantee that the property value will
        never be invalid - see caveats in the `PropertyValue
        <Props.Properties_Value#props.properties_value.PropertyValue>`_
        documentation.

      * **constraints** -- Type specific constraints used to test
        validity.

   **_setLabel(cls, label)**

      Sets the property label for the given class. A RuntimeError is
      raised if a label already exists for the given class.

   **getLabel(instance)**

      Returns the property label for the given instance (more
      specifically, for the class of the given instance), or ``None``
      if no such label has been defined.

   **enable(instance)**

      Enables this property for the given ``HasProperties`` instance.

      See the ``disable()`` method for more details.

   **disable(instance)**

      Disables this property for the given ``HasProperties`` instance.

      An attempt to set the value of a disabled property will result
      in a ``RuntimeError``. This behaviour can be circumvented by
      dealing directly with the underlying
      `props.properties_value.PropertyValue
      <Props.Properties_Value#props.properties_value.PropertyValue>`_
      object.

      Changes to the enabled state of a property may be detected by
      registering a constraint listener (see
      ``addConstraintListener()``) and listening for changes to the
      ``enabled`` constraint.

   **isEnabled(instance)**

      Returns ``True``if this property is enabled for the given
      :class:`HasProperties` instance, ``False`` otherwise.

      See the ``disable()`` method for more details.

   **addListener(instance, name, callback, overwrite=False)**

      Register a listener with the `PropertyValue
      <Props.Properties_Value#props.properties_value.PropertyValue>`_
      object managed by this property. See `addListener()
      <Props.Properties_Value#props.properties_value.PropertyValue.addListener>`_.

      :Parameters:
         * **instance** -- The ``HasProperties`` instance on which the
           listener is to be registered.

         * **name** (*str*) -- A name for the listener.

         * **callback** -- The listener callback function

         * **overwrite** -- Overwrite any existing listener with the
           same name

   **removeListener(instance, name)**

      De-register the named listener from the `PropertyValue
      <Props.Properties_Value#props.properties_value.PropertyValue>`_
      object managed by this property.

   **addConstraintListener(instance, name, listener)**

      Add a listener which will be notified whenever any constraint on
      the `PropertyValue
      <Props.Properties_Value#props.properties_value.PropertyValue>`_
      object bound to the given instance change. An ``AttributeError``
      will be raised if instance is ``None``.  The listener function
      must accept the following parameters:

      ..

         * ``instance``:   The ``HasProperties`` instance

         * ``constraint``: The name of the constraint that changed

         * ``value``:      The new constraint value

   **removeConstraintListener(instance, name)**

      Removes the named constraint listener.

   **getConstraint(instance, constraint)**

      Returns the value of the named constraint for the specified
      instance, or the default constraint value if instance is
      ``None``.

   **setConstraint(instance, constraint, value)**

      Sets the value of the named constraint for the specified
      instance, or the default value if instance is ``None``.

   **getPropVal(instance)**

      Return the `PropertyValue
      <Props.Properties_Value#props.properties_value.PropertyValue>`_
      object(s) for this property, associated with the given
      ``HasProperties`` instance, or ``None`` if there is no value for
      the given instance.

   **_getInstanceData(instance)**

      Returns the ``_InstanceData`` object for the given instance, or
      ``None`` if there is no ``_InstanceData`` for the given
      instance. An ``_InstanceData`` object, which provides a binding
      between a ``PropertyBase`` object and a ``HasProperties``
      instance, is created by that ``HasProperties`` instance when it
      is created (see ``HasProperties.__new__()``).

   **_makePropVal(instance)**

      Creates and returns a `PropertyValue
      <Props.Properties_Value#props.properties_value.PropertyValue>`_
      object for the given ``HasProperties`` instance.

   **validate(instance, attributes, value)**

      Called when an attempt is made to set the property value on the
      given instance.

      Called by `PropertyValue
      <Props.Properties_Value#props.properties_value.PropertyValue>`_
      objects when their value changes. The sole purpose of
      ``validate()`` is to determine whether a given value is valid or
      invalid; it should not do anything else. In particular, it
      should not modify any other property values on the instance, as
      bad things will probably happen.

      If the given value is invalid, subclass implementations should
      raise a ``ValueError`` containing a useful message as to why the
      value is invalid. Otherwise, they should not return any value.
      The default implementation does nothing, unless a custom
      validate function, and/or ``required=True``, was passed to the
      constructor. If ``required`` is ``True``, and the value is
      ``None``, a ``ValueError`` is raised. If a custom validate
      function was set, it is called and, if it returns ``False``, a
      ``ValueError`` is raised. It may also raise a ``ValueError`` of
      its own for invalid values.

      Subclasses which override this method should therefore call this
      superclass implementation in addition to performing their own
      validation.

      :Parameters:
         * **instance** -- The ``HasProperties`` instance which owns
           this ``PropertyBase`` instance, or ``None`` for an unbound
           property value.

         * **attributes** (*dict*) -- Attributes of the `PropertyValue
           <Props.Properties_Value#props.properties_value.PropertyValue>`_
           object, which are used to store type-specific constraints
           for ``PropertyBase`` subclasses.

         * **value** -- The value to be validated.

   **cast(instance, attributes, value)**

      This method is called when a value is assigned to this
      ``PropertyBase`` object through a ``HasProperties`` attribute
      access. The default implementaton just returns the given value.
      Subclasses may override this method to perform any required
      implicit casting or conversion rules.

   **revalidate(instance)**

      Forces validation of this property value, for the current
      instance. This will result in any registered listeners being
      notified, but only if the validity of the value has changed.

**class props.properties.ListPropertyBase(listType, **kwargs)**

   Bases: ``props.properties.PropertyBase``

   A ``PropertyBase`` for properties which encapsulate more than one
   value.

   Define a ``ListPropertyBase`` property.

   :Parameters:
      **listType** -- An unbound ``PropertyBase`` instance, defining
      the type of value allowed in the list. This is optional; if not
      provided, values of any type will be allowed in the list, but no
      validation or casting will be performed.

   **_makePropVal(instance)**

      Creates and returns a `PropertyValueList
      <Props.Properties_Value#props.properties_value.PropertyValueList>`_
      object to be associated with the given ``HasProperties``
      instance.

   **getPropValList(instance)**

      Returns the list of `PropertyValue
      <Props.Properties_Value#props.properties_value.PropertyValue>`_
      objects which represent the items stored in this list.

   **addItemListener(instance, index, name, callback)**

      Convenience method which adds a listener to the property value
      object at the given index.

   **removeItemListener(instance, index, name)**

      Convenience method which removes the named listener from the
      property value at the given index.

   **addItemConstraintListener(instance, index, name, listener)**

      Convenience method which adds a constraint listener (actually an
      attribute listener) to the `PropertyValue
      <Props.Properties_Value#props.properties_value.PropertyValue>`_
      object at the given index.

   **removeItemConstraintListener(instance, index, name)**

      Convenience method which removes the named constraint listener
      from the property value at the given index.

   **getItemConstraint(instance, index, constraint)**

      Convenience method which returns the specified constraint for
      the property value at the given index. If ``instance`` is
      ``None``, the index is ignored, and the default list type
      constraint value is returned. If no list type was specified for
      this list, an :exc:AttributeError` is raised.

   **setItemConstraint(instance, index, constraint, value)**

      Convenience method which sets the specified constraint to the
      specified value, for the property value at the given index. If
      instance is ``None``, the index is ignored, and the default list
      type constraint value is changed. If no list type was specified
      for this list, an ``AttributeError`` is raised.

**class props.properties.PropertyOwner**

   Bases: ``type``

   Metaclass for classes which contain ``PropertyBase`` objects. Sets
   ``PropertyBase`` labels from the corresponding class attribute
   names.

**class props.properties.HasProperties(validateOnChange=False)**

   Bases: ``object``

   Base class for classes which contain ``PropertyBase`` objects.  All
   classes which contain ``PropertyBase`` objects must subclass this
   class.

   Create a HasProperties instance.

   **addProperty(propName, propObj)**

      Add the given property to this ``HasProperties`` instance.

   ``classmethod getAllProperties()``

      Returns two lists, the first containing the names of all
      properties of this object, and the second containing the
      corresponding ``PropertyBase`` objects.

      Properties which have a name beginning with an underscore are
      not returned by this method

   ``classmethod getProp(propName)``

      Return the ``PropertyBase`` object for the given property.

   **getPropVal(propName)**

      Return the `PropertyValue
      <Props.Properties_Value#props.properties_value.PropertyValue>`_
      object(s) for the given property.

   **enableNotification(propName)**

      Enables notification of listeners on the given property.

   **disableNotification(propName)**

      Disables notification of listeners on the given property.

   **enableProperty(propName)**

      Enables the given property - see ``PropertyBase.enable()``.

   **disableProperty(propName)**

      Disables the given property - see ``PropertyBase.disable()``.

   **propertyIsEnabled(propName)**

      Returns the enabled state of the given property - see
      ``PropertyBase.isEnabled()``.

   **notify(propName)**

      Force notification of listeners on the given property. This will
      have no effect if notification for the property is disabled.

   **getConstraint(propName, constraint)**

      Convenience method, returns the value of the named constraint
      for the named property. See ``PropertyBase.getConstraint()``.

   **setConstraint(propName, constraint, value)**

      Convenience method, sets the value of the named constraint for
      the named property. See ``PropertyBase.setConstraint()``.

   **getItemConstraint(propName, index, constraint)**

      Convenience method, returns the value of the named constraint
      for the value at the specified index of the named list property.
      See ``ListPropertyBase.getItemConstraint()``. If the named
      property is not a list property, an ``AttributeError`` is
      raised.

   **setItemConstraint(propName, index, constraint, value)**

      Convenience method, sets the value of the named constraint for
      the value at the specified index of the named list property. See
      ``ListPropertyBase.setItemConstraint()``. If the named property
      is not a list property, an ``AttributeError`` is raised.

   **addListener(propName, listenerName, callback, overwrite=False)**

      Convenience method, adds the specified listener to the specified
      property. See ``PropertyBase.addListener()``.

   **removeListener(propName, listenerName)**

      Convenience method, removes the specified listener from the
      specified property. See ``PropertyBase.addListener()``.

   **enableListener(propName, name)**

      (Re-)Enables the listener on the specified property with the
      specified ``name``.

   **disableListener(propName, name)**

      Disables the listener on the specified property with the
      specified ``name``, but does not remove it from the list of
      listeners.

   **addGlobalListener(listenerName, callback, overwrite=False)**

      Registers the given listener so that it will be notified of
      changes to any of the properties of this HasProperties instance.

   **removeGlobalListener(listenerName)**

      De-registers the specified global listener (see
      ``addGlobalListener()``).

   **addConstraintListener(propName, listenerName, callback)**

      Convenience method, adds the specified constraint listener to
      the specified property. See
      ``PropertyBase.addConstraintListener()``.

   **removeConstraintListener(propName, listenerName)**

      Convenience method, removes the specified constraint listener
      from the specified property. See
      ``PropertyBase.removeConstraintListener()``.

   **isValid(propName)**

      Returns ``True`` if the current value of the specified property
      is valid, ``False`` otherwise.

   **validateAll()**

      Validates all of the properties of this ``HasProperties``
      object.  A list of tuples is returned, with each tuple
      containing a property name, and an associated error string. The
      error string is a message about the property which failed
      validation. If all property values are valid, the returned list
      will be empty.

   **_HasProperties__valueChanged(ctx, value, valid, name)**

      This function is called by `PropertyValue
      <Props.Properties_Value#props.properties_value.PropertyValue>`_
      objects which are managed by this ``PropertyBase`` object.

   **bindProps(propName, other, otherPropName=None, unbind=False)**

      Binds the properties specified by ``propName``  and
      ``otherPropName`` such that changes to one are applied to the
      other.

      :Parameters:
         * **propName** (*str*) -- The name of a property on this
           ``HasProperties`` instance.

         * **other** (*HasProperties*) -- Another ``HasProperties``
           instance.

         * **otherPropName** (*str*) -- The name of a property on
           ``other`` to bind to. If ``None`` it is assumed that there
           is a property on ``other`` called ``propName``.

         * **unbind** -- If ``True``, the properties are unbound. See
           the ``unbindProps()`` method.

   **isBound(propName, other, otherPropName=None)**

      Returns ``True`` if the specified property is bound to the other
      ``HasProperties`` object, ``False`` otherwise.

   **unbindProps(propName, other, otherPropName=None)**

      Unbinds two properties previously bound via a call to
      ``bindProps()``.
