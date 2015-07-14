#!/usr/bin/env python
#
# syncable.py - An extension to the HasProperties class which allows
# a master-slave relationship to exist between instances.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""The :mod:`syncable` module provides the :class:`SyncableHasProperties`
class, an extension to the :class:`props.HasProperties` class which allows a
parent-child relationship to exist between instances. All that is needed to
make use of this functionality is to extend the :class:`SyncableHasProperties`
class instead of the :class:`HasProperties` class::

    >>> import props

    >>> class MyObj(props.SyncableHasProperties):
    >>>     myint = props.Int()
    >>>     def __init__(self, parent=None):
    >>>         props.SyncableHasProperties.__init__(self, parent)
    >>>

Given a class definition such as the above, a parent-child relationship
between two instances can be set up as follows::

    >>> myParent = MyObj()
    >>> myChild  = MyObj(myParent)

The ``myint`` properties of both instances are now bound to each other (see
the :mod:`~props.bindable` module) - when it changes in one instance, that
change is propagated to the other instance::

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
:meth:`unsyncFromParent` and :meth:`syncToParent` methods of the
:class:`SyncableHasProperties` class.  Listeners to sync state changes may
be registered on the child instance via the :meth:`addSyncChangeListener`
method (and de-registered via the :meth:`removeSyncChangeListener` method).

A one-to-many synchronisation relationship is possible between one parent, and
many children.
"""

import weakref
import logging

import properties       as props
import properties_types as types


log = logging.getLogger(__name__)


_SYNC_SALT_ = '_sync_'
"""Constant string added to sync-related property names and listeners."""


class SyncablePropertyOwner(props.PropertyOwner):
    """Metaclass for the :class:`SyncableHasProperties` class. Creates
    a :class:`~props.Boolean` property for every other property in the
    class, which controls whether the corresponding property is bound
    to the parent or not.
    """

    def __new__(cls, name, bases, attrs):

        newAttrs = dict(attrs)

        for propName, propObj in attrs.items():
            
            if not isinstance(propObj, props.PropertyBase): continue

            # Add a hidden boolean property for every
            # real property which controls the
            # parent-child bind state of that property.
            # The logic to control this is configured in
            # the SyncableHasProperties.__init__ method.
            bindProp = types.Boolean(default=True)
            newAttrs['{}{}'.format(_SYNC_SALT_, propName)] = bindProp

        newCls = super(SyncablePropertyOwner, cls).__new__(
            cls, name, bases, newAttrs)

        return newCls 

    
class SyncableHasProperties(props.HasProperties):
    """An extension to the :class:`props.HasProperties` class which supports
    parent-child relationships between instances.
    """

    
    __metaclass__ = SyncablePropertyOwner


    @classmethod
    def _saltSyncPropertyName(cls, propName):
        """Adds a prefix to the given property name, to be used as the
        name for the corresponding boolean sync property.
        """
        return '{}{}'.format(_SYNC_SALT_, propName)
 

    @classmethod
    def getSyncPropertyName(cls, propName):
        """Returns the name of the boolean property which can be used to
        toggle binding of the given property to the parent property of
        this instance.
        """
        return cls._saltSyncPropertyName(propName)

    
    @classmethod
    def getSyncProperty(cls, propName):
        """Returns the :class:`~props.properties.PropertyBase` instance
        which can be used to toggle binding of the given property to the
        parent property of this instance.
        """
        return cls.getProp(cls.getSyncPropertyName(propName))

    
    def __init__(self,
                 parent=None,
                 nobind=None,
                 nounbind=None,
                 *args,
                 **kwargs):
        """Create a :class:`SyncableHasProperties` object.

        If this :class:`SyncableHasProperties` object does not have a parent,
        there is no need to call this constructor explicitly. Otherwise, the
        parent must be an instance of the same class to which this instance's
        properties should be bound.
        
        :arg parent:   Another :class:`SyncableHasProperties` instance, which
                       has the same type as this instance.
        
        :arg nobind:   A sequence of property names which should not be bound
                       with the parent.
        
        :arg nounbind: A sequence of property names which cannot be unbound
                       from the parent.
        """
        props.HasProperties.__init__(self, *args, **kwargs)
        
        if nobind   is None: nobind   = []
        if nounbind is None: nounbind = []

        self._nobind   = nobind
        self._nounbind = nounbind

        # Get a list of all the
        # properties of this class,
        # including private ones
        attNames  = dir(type(self))
        propNames = []
        for attName in attNames:
            att = getattr(type(self), attName)

            if isinstance(att, props.PropertyBase):
                propNames.append(attName)
        
        # If parent is none, then this instance
        # is a 'parent' instance, and doesn't need
        # to worry about being bound. So we'll
        # remove all the _bind_ properties which
        # were created by the metaclass
        if parent is None:
            for propName in propNames:
                if propName.startswith(_SYNC_SALT_):
                    log.debug('Clearing sync property '
                              'from parent ({}.{}) [{}]'.format(
                                  self.__class__.__name__,
                                  propName,
                                  id(self)))
                    self.__dict__[propName] = None

            # This array maintains a list of
            # all the children synced to this
            # parent
            self._children = []
            self._parent   = None


        # Otherwise, this instance is a 'child'
        # instance - set up a binding between
        # this instance and its parent for every
        # property - see _initBindProperty
        else:

            self._parent = weakref.ref(parent)

            if not isinstance(parent, self.__class__):
                raise TypeError('parent is of a different type '
                                '({} != {})'.format(parent.__class__,
                                                    self.__class__))

            parent._children.append(weakref.ref(self))

            propNames, _ = self.getAllProperties()

            log.debug('Binding properties of {} ({}) to parent ({})'.format(
                self.__class__.__name__, id(self), id(parent)))

            for propName in propNames:
                self._initSyncProperty(propName)

                    
    def getParent(self):
        """Returns the parent of this instance, or ``None`` if there is no
        parent.
        """
        # This will raise an AttributeError if
        # called before __init__ has been called.
        # If this happens, it's the user code
        # which is at fault.
        if self._parent is None: return None
        else:                    return self._parent()


    def getChildren(self):
        """Returns a list of any children that are synced to this parent
        instance, or ``None`` if this instance is not a parent.
        """
        if self._parent is not None:
            return None

        return list([c() for c  in self._children])
                
    
    def _saltSyncListenerName(self, propName):
        """Adds a prefix and a suffix to the given property name, to be used
        as the name for an internal listener on the corresponding boolean sync
        property.

        """
        return '{}{}_{}'.format(_SYNC_SALT_, propName, id(self))


    def _initSyncProperty(self, propName):
        """Called by child instances from __init__.

        Configures a binding between this instance and its parent for the
        specified property.
        """
        
        bindPropName  = self._saltSyncPropertyName(propName)
        bindPropObj   = self.getProp(bindPropName)
        bindPropVal   = bindPropObj.getPropVal(self)

        if not self.canBeSyncedToParent(propName):
            bindPropVal.set(False)
            return

        bindPropVal.set(True)

        if self.canBeUnsyncedFromParent(propName):
            lName = self._saltSyncListenerName(propName)
            bindPropVal.addListener(
                lName,
                lambda *a: self._syncPropChanged(propName, *a))

        self.bindProps(propName, self._parent()) 

        
    def _syncPropChanged(self, propName, *a):
        """Called when a hidden boolean property controlling the sync
        state of the specified real property changes.

        Changes the sync state of the property accordingly.
        """

        bindPropName = self._saltSyncPropertyName(propName)
        bindPropVal  = getattr(self, bindPropName)

        if bindPropVal and (propName in self._nobind):
            raise RuntimeError('{} cannot be bound to '
                               'parent'.format(propName))

        if (not bindPropVal) and (propName in self._nounbind):
            raise RuntimeError('{} cannot be unbound from '
                               'parent'.format(propName))

        log.debug('Sync property changed for {} - '
                  'changing binding state'.format(propName))
        
        self.bindProps(propName, self._parent(), unbind=(not bindPropVal)) 

        
    def syncToParent(self, propName):
        """Synchronise the given property with the parent instance.

        If this :class:`HasProperties` instance has no parent, a
        `RuntimeError` is raised. If the specified property is in the
        ``nobind`` list (see :meth:`__init__`), a `RuntimeError` is
        raised.

        ..note:: The ``nobind`` check can be avoided by calling
        :meth:`bindProps` directly. But don't do that.
        """
        if propName in self._nobind:
            raise RuntimeError('{} cannot be bound to '
                               'parent'.format(propName))

        bindPropName = self._saltSyncPropertyName(propName)
        setattr(self, bindPropName, True)


    def detachFromParent(self):
        """If this is a child ``SyncableHasProperties`` instance, it
        detaches itself from its parent. This is an irreversible operation.

        TODO: Add the ability to dynamically set/clear the parent
              SHP instance.
        """

        if self._parent is None or self._parent() is None:
            self._parent = None
            return

        propNames = self.getAllProperties()[0]

        for propName in propNames:
            if propName not in self._nounbind:
                syncPropName = self._saltSyncPropertyName(propName)
                lName        = self._saltSyncListenerName(propName)
                self.removeListener(syncPropName, lName)
                self.unsyncFromParent(propName)

        for c in list(self._parent()._children):
            if c() is self:
                self._parent()._children.remove(c)

        self._parent = None
 
    
    def unsyncFromParent(self, propName):
        """Unsynchronise the given property from the parent instance.

        If this :class:`SyncableHasProperties` instance has no parent, a
        `RuntimeError` is raised. If the specified property is in the
        `nounbind` list (see :meth:`__init__`), a `RuntimeError` is raised.

        ..note:: The ``nounbind`` check can be avoided by calling
        :meth:`bindProps` directly. But don't do that. 
        """
        if propName in self._nounbind:
            raise RuntimeError('{} cannot be unbound from '
                               'parent'.format(propName))        
        
        bindPropName = self._saltSyncPropertyName(propName)
        setattr(self, bindPropName, False) 

        
    def isSyncedToParent(self, propName):
        """Returns true if the specified property is synced to the parent of
        this :class:`HasProperties` instance, ``False`` otherwise.
        """
        return getattr(self, self._saltSyncPropertyName(propName))

    
    def canBeSyncedToParent(self, propName):
        """Returns ``True`` if the given property can be synced between a
        child and its parent (see the ``nobind`` parameter in
        :meth:`__init__`).
        """
        return propName not in self._nobind

    
    def canBeUnsyncedFromParent(self, propName):
        """Returns ``True`` if the given property can be unsynced between a
        child and its parent (see the ``nounbind`` parameter in
        :meth:`__init__`).
        """ 
        return propName not in self._nounbind


    def addSyncChangeListener(self,
                              propName,
                              listenerName,
                              callback,
                              overwrite=False,
                              weak=True):
        """Registers the given callback function to be called when
        the sync state of the specified property changes.
        """
        bindPropName = self._saltSyncPropertyName(propName)
        self.addListener(bindPropName,
                         listenerName,
                         callback,
                         overwrite=overwrite,
                         weak=weak)

        
    def removeSyncChangeListener(self, propName, listenerName):
        """De-registers the given listener from receiving sync
        state changes.
        """ 
        bindPropName = self._saltSyncPropertyName(propName)
        self.removeListener(bindPropName, listenerName)
