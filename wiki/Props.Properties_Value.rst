
props.properties_value module
*****************************

Definitions of the ``PropertyValue`` and ``PropertyValueList``
classes.

These definitions are really a part of the `props.properties
<Props.Properties#module-props.properties>`_ module, and are intended
to be created and managed by `PropertyBase
<Props.Properties#props.properties.PropertyBase>`_ objects. However,
the ``PropertyValue`` class definitions have absolutely no
dependencies upon the `PropertyBase
<Props.Properties#props.properties.PropertyBase>`_ definitions. The
same can't be said for the other way around though.

**class props.properties_value.PropertyValue(context, name=None,
value=None, castFunc=None, validateFunc=None, equalityFunc=None,
preNotifyFunc=None, postNotifyFunc=None, allowInvalid=True,
**attributes)**

   Bases: ``object``

   An object which encapsulates a value of some sort.

   The value may be subjected to validation rules, and listeners may
   be registered for notification of value and validity changes.

   Create a ``PropertyValue`` object.

   :Parameters:
      * **context** -- An object which is passed as the first argument
        to the ``validateFunc``, ``preNotifyFunc``,
        ``postNotifyFunc``, and any registered listeners. Can be
        anything, but will nearly always be a `HasProperties
        <Props.Properties#props.properties.HasProperties>`_ instance.

      * **name** (*str*) -- Value name - if not provided, a default,
        unique name is created.

      * **value** -- Initial value.

      * **castFunc** -- Function which performs type casting or data
        conversion. Must accept three parameters - the context, a
        dictionary containing the attributes of this object, and the
        value to cast. Must return that value, cast appropriately.

      * **validateFunc** -- Function which accepts three parameters -
        the context, a dictionary containing the attributes of this
        object, and a value. This function should test the provided
        value, and raise a ``ValueError`` if it is invalid.

      * **equalityFunc** -- Function which accepts two values, and
        should return ``True`` if they are equal, ``False`` otherwise.
        If not provided, the python equailty operator (i.e. ``==``) is
        used.

      * **preNotifyFunc** -- Function to be called whenever the
        property value changes, but before any registered listeners
        are called. See the ``addListener()`` method for details of
        the parameters this function must accept.

      * **postNotifyFunc** -- Function to be called whenever the
        property value changes, but after any registered listeners are
        called. Must accept the same parameters as the
        ``preNotifyFunc``.

      * **allowInvalid** -- If ``False``, any attempt to set the value
        to something invalid will result in a ``ValueError``. Note
        that this does not guarantee that the property will never have
        an invalid value, as the definition of 'valid' depends on
        external factors (i.e. the ``validateFunc``).  Therefore, the
        validity of a value may change, even if the value itself has
        not changed.

      * **attributes** -- Any key-value pairs which are to be
        associated  with this ``PropertyValue`` object, and  passed to
        the ``castFunc`` and ``validateFunc``  functions. Attributes
        are not used by the  ``PropertyValue`` or
        ``PropertyValueList`` classes, however they are used by the
        `ListPropertyBase
        <Props.Properties#props.properties.ListPropertyBase>`_ and
        `PropertyBase
        <Props.Properties#props.properties.PropertyBase>`_ classes to
        store per-instance property constraints. Listeners may
        register to be notified when attribute values change.

   ``queue = <props.callqueue.CallQueue object at 0x104172690>``

      A ``CallQueue`` instance shared by all ``PropertyValue`` objects
      for notifying listeners of value and attribute changes.

   **enableNotification()**

      Enables notification of property value and attribute listeners
      for this ``PropertyValue`` object.

   **disableNotification()**

      Disables notification of property value and attribute listeners
      for this ``PropertyValue`` object. Notification can be
      re-enabled via the ``enableNotification()`` method.

   **getNotificationState()**

      Returns ``True`` if notification is currently enabled, ``False``
      otherwise.

   **setNotificationState(value)**

      Sets the current notification state.

   **_saltListenerName(name)**

      Adds a constant string to the given listener name.

      This is done for debug output, so we can better differentiate
      between listeners with the same name registered on different PV
      objects.

   **addAttributeListener(name, listener)**

      Adds an attribute listener for this ``PropertyValue``. The
      listener callback function must accept the following arguments:

      ..

         * ``context``:   The context associated with this
              ``PropertyValue``.

         * ``attribute``: The name of the attribute that changed.

         * ``value``:     The new attribute value.

         * ``name``:      The name of this ``PropertyValue`` instance.

      :Parameters:
         * **name** (*str*) -- A unique name for the listener. If a
           listener with the specified name already exists, it will be
           overwritten.

         * **listener** -- The callback function.

   **removeAttributeListener(name)**

      Removes the attribute listener of the given name.

   **getAttributes()**

      Returns a dictionary containing all the attributes of this
      ``PropertyValue`` object.

   **setAttributes(atts)**

      Sets all the attributes of this ``PropertyValue`` object. from
      the given dictionary.

   **getAttribute(name)**

      Returns the value of the named attribute.

   **setAttribute(name, value)**

      Sets the named attribute to the given value, and notifies any
      registered attribute listeners of the change.

   **notifyAttributeListeners(name, value)**

      This method replaces the ``notifyAttributeListeners()`` method.
      It ensures that the attributes of any bound ``PropertyValue``
      instances are synchronised before any attribute listeners are
      notified.

   **addListener(name, callback, overwrite=False)**

      Adds a listener for this value.

      When the value changes, the listener callback function is
      called. The callback function must accept the following
      arguments:

      ..

         * ``value``:   The property value

         * ``valid``:   Whether the value is valid or invalid

         * ``context``: The context object passed to ``__init__()``.

         * ``name``:    The name of this ``PropertyValue`` instance.

      Listener names 'prenotify' and 'postnotify' are reserved - if
      either of these are passed in for the listener name, a
      ``ValueError`` is raised.

      :Parameters:
         * **name** (*str*) -- A unique name for this listener. If a
           listener with the name already exists, a RuntimeError will
           be raised, or it will be overwritten, depending upon the
           value of the ``overwrite`` argument.

         * **callback** -- The callback function.

         * **overwrite** -- If ``True`` any previous listener with the
           same name will be overwritten.

   **removeListener(name)**

      Removes the listener with the given name from this
      ``PropertyValue``.

   **enableListener(name)**

      (Re-)Enables the listener with the specified ``name``.

   **disableListener(name)**

      Disables the listener with the specified ``name``, but does not
      remove it from the list of listeners.

   **hasListener(name)**

      Returns ``True`` if a listener with the given name is
      registered, ``False`` otherwise.

   **setPreNotifyFunction(preNotifyFunc)**

      Sets the function to be called on value changes, before any
      registered listeners.

   **setPostNotifyFunction(postNotifyFunc)**

      Sets the function to be called on value changes, after any
      registered listeners.

   **get()**

      Returns the current property value.

   **set(newValue)**

      Sets the property value.

      The property is validated and, if the property value or its
      validity has changed, the ``preNotifyFunc``, any registered
      listeners, and the ``postNotifyFunc`` are called.  If
      ``allowInvalid`` was set to ``False``, and the new value is not
      valid, a ``ValueError`` is raised, and listeners are not
      notified.

   **notify()**

      This method replaces ``notify()``. It ensures that bound
      ``ProperyValue`` objects are synchronised to have the same
      value, before any registered listeners are notified.

   **revalidate()**

      Revalidates the current property value, and re-notifies any
      registered listeners if the value validity has changed.

   **isValid()**

      Returns ``True`` if the current property value is valid,
      ``False`` otherwise.

   **_orig_notify()**

      Notifies registered listeners.

      Calls the ``preNotify`` function (if it is set), any listeners
      which have been registered with this ``PropertyValue`` object,
      and the ``postNotify`` function (if it is set). If notification
      has been disabled (via the ``disableNotification()`` method),
      this method does nothing.

   **_orig_notifyAttributeListeners(name, value)**

      Notifies all registered attribute listeners of an attribute
      change (unless notification has been disabled via the
      ``disableNotification()`` method). This method is separated so
      that it can be called from subclasses (specifically the
      ``PropertyValueList``).

**class props.properties_value.PropertyValueList(context, name=None,
values=None, itemCastFunc=None, itemEqualityFunc=None,
itemValidateFunc=None, listValidateFunc=None, itemAllowInvalid=True,
preNotifyFunc=None, postNotifyFunc=None, listAttributes=None,
itemAttributes=None)**

   Bases: ``props.properties_value.PropertyValue``

   A ``PropertyValue`` object which stores other ``PropertyValue``
   objects in a list. Instances of this class are managed by a
   `ListPropertyBase
   <Props.Properties#props.properties.ListPropertyBase>`_ instance.

   When created, separate validation functions may be passed in for
   individual items, and for the list as a whole. Listeners may be
   registered on individual items (accessible via the
   ``getPropertyValueList()`` method), or on the entire list.

   The values contained in this ``PropertyValueList`` may be accessed
   through standard Python list operations, including slice-based
   access and assignment, ``append()``, ``insert()``, ``extend()``,
   ``pop()``, ``index()``, ``count()``, ``move()``, ``insertAll()``,
   ``removeAll()``, and ``reorder()`` (these last few are
   non-standard).

   Because the values contained in this list are ``PropertyValue``
   instances themselves, some limitations are present on list
   modifying operations. First of all, it is not possible to simply
   assign an arbitrary sequence of values to a `ListPropertyBase
   <Props.Properties#props.properties.ListPropertyBase>`_ instance:

   ::

      class MyObj(props.HasProperties):
        mylist = props.List(default[1, 2, 3])

      myobj = MyObj()

      # This will result in a ValueError
      myobj.mylist = [1,2,3,4,5]

   It *is* possible to perform assignment in this manner if the list
   lengths match. In this case, each of the individual
   ``PropertyValue`` instances contained in the list will be assigned
   to each of the values in the input sequence:

   ::

      # This will work as expected
      myobj.mylist = [4, 5, 6]

   In a similar vein, value assigments via indexing must not change
   the length of the list. For example, this is a valid assignment:

   ::

      mylist[2:7] = [3,4,5,6,7]

   Whereas this would result in an ``IndexError``:

   ::

      mylist[2:7] = [3,4,5,6]

   A listener registered on a ``PropertyValueList`` will be notified
   whenever the list is modified (e.g. additions, removals,
   reorderings), and whenever any individual value in the list
   changes. Alternately, listeners may be registered on the individual
   ``PropertyValue`` items (which are accessible through the
   ``getPropertyValueList()`` method) to be nofitied of changes to
   those values only.

   There are some interesting type-specific subclasses of the
   ``PropertyValueList``, which provide additional functionality:

   ..

      * The `PointValueList
        <Props.Properties_Types#props.properties_types.PointValueList>`_,
        for `Point
        <Props.Properties_Types#props.properties_types.Point>`_
        properties.

      * The `BoundsValueList
        <Props.Properties_Types#props.properties_types.BoundsValueList>`_,
        for `Bounds
        <Props.Properties_Types#props.properties_types.Bounds>`_
        properties.

   Create a ``PropertyValueList``.

   :Parameters:
      * **context** -- See the ``PropertyValue`` constructor.

      * **name** (*str*) -- See the ``PropertyValue`` constructor.

      * **values** (*list*) -- Initial list values.

      * **itemCastFunc** -- Function which casts a single list item.
        See the ``PropertyValue`` constructor.

      * **itemValidateFunc** -- Function which validates a single list
        item. See the ``PropertyValue`` constructor.

      * **itemEqualityFunc** -- Function which tests equality of two
        values. See the ``PropertyValue`` constructor.

      * **listValidateFunc** -- Function which validates the list as a
        whole.

      * **itemAllowInvalid** (*bool*) -- Whether items are allowed to
        containg invalid values.

      * **preNotifyFunc** -- See the ``PropertyValue`` constructor.

      * **postNotifyFunc** -- See the ``PropertyValue`` constructor.

      * **listAttributes** (*dict*) -- Attributes to be associated
        with this ``PropertyValueList``.

      * **itemAttributes** (*dict*) -- Attributes to be associated
        with new ``PropertyValue`` items added to the list.

   **_listEquality(a, b)**

      Uses the item equality function to test whether two lists are
      equal. Returns ``True`` if they are, ``False`` if they're not.

   **getPropertyValueList()**

      Return (a copy of) the underlying property value list, allowing
      access to the ``PropertyValue`` objects which manage each list
      item.

   **get()**

      Overrides ``PropertyValue.get()``. Returns this
      ``PropertyValueList`` object.

   **set(newValues)**

      Overrides ``PropertyValue.set()``.

      Sets the values stored in this ``PropertyValueList``.  If the
      length of the ``newValues`` argument does not match the current
      list length,  a ``ValueError`` is raised.

   **enableNotification()**

      Enables notification of list-level listeners.

   **disableNotification()**

      Disables notification of list-level listeners. Listeners on
      individual ``PropertyValue`` items will still be notified of
      item changes.

   **_itemChanged(*a)**

      This function is called when any list item value changes.
      List-level listeners are notified of the change.

   **index(item)**

   **count(item)**

   **insert(index, item)**

      Inserts the given item before the given index.

   **insertAll(index, items)**

      Inserts all of the given items before the given index.

   **append(item)**

      Appends the given item to the end of the list.

   **extend(iterable)**

      Appends all items in the given iterable to the end of the list.

   **pop(index=-1)**

      Remove and return the specified value in the list (default:
      last).

   **move(from_, to)**

      Move the item from 'from_' to 'to'.

   **remove(value)**

      Remove the first item in the list with the specified value.

   **removeAll(values)**

      Removes the first occurrence in the list of all of the specified
      values.

   **_PropertyValueList__newItem(item)**

      Called whenever a new item is added to the list.  Encapsulate
      the given item in a ``PropertyValue`` object.

   **reorder(idxs)**

      Reorders the list according to the given sequence of indices.
