
props.syncable module
*********************

The ``syncable`` module provides the ``SyncableHasProperties`` class,
an extension to the ``props.HasProperties`` class which allows a
parent-child relationship to exist between instances. All that is
needed to make use of this functionality is to extend the
``SyncableHasProperties`` class instead of the ``HasProperties``
class:

::

   >>> import props

   >>> class MyObj(props.SyncableHasProperties):
   >>>     myint = props.Int()
   >>>     def __init__(self, parent=None):
   >>>         props.SyncableHasProperties.__init__(self, parent)
   >>>

Given a class definition such as the above, a parent-child
relationship between two instances can be set up as follows:

::

   >>> myParent = MyObj()
   >>> myChild  = MyObj(myParent)

The ``myint`` properties of both instances are now bound to each other
(see the `bindable <Props.Bindable#module-props.bindable>`_ module) -
when it changes in one instance, that change is propagated to the
other instance:

::

   >>> def parentPropChanged(*a):
   >>>     print 'myParent.myint changed: {}'.format(myParent.myint)
   >>>
   >>> def childPropChanged(*a):
   >>>     print 'myChild.myint changed: {}'.format(myChild.myint)

   >>> myParent.addListener('myint', 'parentPropChanged', parentPropChanged)
   >>> myChild.addListener( 'myint', 'childPropChanged',  childPropChanged)

   >>> myParent.myint = 12345
   myParent.myint changed: 12345
   myChild.myint changed: 12345

   >>> myChild.myint = 54321
   myParent.myint changed: 54321
   myChild.myint changed: 54321

This synchronisation can be toggled on the child instance, via the
``unsyncFromParent()`` and ``syncToParent()`` methods of the
``SyncableHasProperties`` class.  Listeners to sync state changes may
be registered on the child instance via the
``addSyncChangeListener()`` method (and de-registered via the
``removeSyncChangeListener()`` method).

A one-to-many synchronisation relationship is possible between one
parent, and many children.

**class props.syncable.SyncablePropertyOwner**

   Bases: `props.properties.PropertyOwner
   <Props.Properties#props.properties.PropertyOwner>`_

   Metaclass for the ``SyncableHasProperties`` class. Creates a
   ``Boolean`` property for every other property in the class, which
   controls whether the corresponding property is bound to the parent
   or not.

**class props.syncable.SyncableHasProperties(parent=None, nobind=None,
nounbind=None, *args, **kwargs)**

   Bases: `props.properties.HasProperties
   <Props.Properties#props.properties.HasProperties>`_

   An extension to the ``props.HasProperties`` class which supports
   parent-child relationships between instances.

   Create a ``SyncableHasProperties`` object.

   If this ``SyncableHasProperties`` object does not have a parent,
   there is no need to call this constructor explicitly. Otherwise,
   the parent must be an instance of the same class to which this
   instance's properties should be bound.

   :Parameters:
      * **parent** -- Another ``SyncableHasProperties`` instance,
        which has the same type as this instance.

      * **nobind** -- A sequence of property names which should not be
        bound with the parent.

      * **nounbind** -- A sequence of property names which cannot be
        unbound from the parent.

   ``classmethod _saltSyncPropertyName(propName)``

      Adds a prefix to the given property name, to be used as the name
      for the corresponding boolean sync property.

   ``classmethod getSyncPropertyName(propName)``

      Returns the name of the boolean property which can be used to
      toggle binding of the given property to the parent property of
      this instance.

   ``classmethod getSyncProperty(propName)``

      Returns the `PropertyBase
      <Props.Properties#props.properties.PropertyBase>`_ instance
      which can be used to toggle binding of the given property to the
      parent property of this instance.

   **getParent()**

      Returns the parent of this instance, or ``None`` if there is no
      parent.

   **_saltSyncListenerName(propName)**

      Adds a prefix and a suffix to the given property name, to be
      used as the name for an internal listener on the corresponding
      boolean sync property.

   **_initSyncProperty(propName)**

      Called by child instances from __init__.

      Configures a binding between this instance and its parent for
      the specified property.

   **_syncPropChanged(propName, *a)**

      Called when a hidden boolean property controlling the sync state
      of the specified real property changes.

      Changes the sync state of the property accordingly.

   **syncToParent(propName)**

      Synchronise the given property with the parent instance.

      If this ``HasProperties`` instance has no parent, a
      *RuntimeError* is raised. If the specified property is in the
      ``nobind`` list (see ``__init__()``), a *RuntimeError* is
      raised.

      ..note:: The ``nobind`` check can be avoided by calling
      ``bindProps()`` directly. But don't do that.

   **unsyncFromParent(propName)**

      Unsynchronise the given property from the parent instance.

      If this ``SyncableHasProperties`` instance has no parent, a
      *RuntimeError* is raised. If the specified property is in the
      *nounbind* list (see ``__init__()``), a *RuntimeError* is
      raised.

      ..note:: The ``nounbind`` check can be avoided by calling
      ``bindProps()`` directly. But don't do that.

   **isSyncedToParent(propName)**

      Returns true if the specified property is synced to the parent
      of this ``HasProperties`` instance, ``False`` otherwise.

   **canBeSyncedToParent(propName)**

      Returns ``True`` if the given property can be synced between a
      child and its parent (see the ``nobind`` parameter in
      ``__init__()``).

   **canBeUnsyncedFromParent(propName)**

      Returns ``True`` if the given property can be unsynced between a
      child and its parent (see the ``nounbind`` parameter in
      ``__init__()``).

   **addSyncChangeListener(propName, listenerName, callback)**

      Registers the given callback function to be called when the sync
      state of the specified property changes.

   **removeSyncChangeListener(propName, listenerName)**

      De-registers the given listener from receiving sync state
      changes.
