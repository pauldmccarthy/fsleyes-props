#!/usr/bin/env python
#
# syncable.py - An extension to the HasProperties class which allows
# a master-slave relationship to exist between instances.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`SyncableHasProperties` class, an extension
to the :class:`.HasProperties` class which allows a parent-child relationship
to exist between instances. A one-to-many synchronisation relationship is
possible between one parent, and many children. Property values are
synchronised between a parent and its children, using the functionality
provided by the :mod:`bindable` module.

All that is needed to make use of this functionality is to extend the
``SyncableHasProperties`` class instead of the ``HasProperties`` class::

    >>> import props

    >>> class MyObj(props.SyncableHasProperties):
            myint = props.Int()
            def __init__(self, parent=None):
                props.SyncableHasProperties.__init__(self, parent=parent)
    

Given a class definition such as the above, a parent-child relationship
between two instances can be set up as follows::

    >>> myParent = MyObj()
    >>> myChild  = MyObj(myParent)

The ``myint`` properties of both instances are now bound to each other - when
it changes in one instance, that change is propagated to the other instance::

    >>> def parentPropChanged(*a):
            print 'myParent.myint changed: {}'.format(myParent.myint)
    >>>
    >>> def childPropChanged(*a):
            print 'myChild.myint changed: {}'.format(myChild.myint)

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
"""


import weakref
import logging

import properties       as props
import properties_types as types


log = logging.getLogger(__name__)


_SYNC_SALT_ = '_sync_'
"""Constant string added to sync-related property names and listeners."""


class SyncablePropertyOwner(props.PropertyOwner):
    """Metaclass for the ``SyncableHasProperties`` class. Creates a
    :class:`.Boolean` property for every other property in the class, which
    controls whether the corresponding property is bound to the parent or not.
    """

    def __new__(cls, name, bases, attrs):
        """Creates a new ``SyncableHasProperties`` class.

        Adds a hidden boolean property for every real property which controls
        the parent-child binding state of that property.  The logic to control
        this is configured in the :meth:`SyncableHasProperties.__init__`
        method.
        """

        newAttrs = dict(attrs)

        for propName, propObj in attrs.items():
            
            if not isinstance(propObj, props.PropertyBase): continue


            bindProp = types.Boolean(default=True)
            newAttrs['{}{}'.format(_SYNC_SALT_, propName)] = bindProp

        newCls = super(SyncablePropertyOwner, cls).__new__(
            cls, name, bases, newAttrs)

        return newCls 

    
class SyncableHasProperties(props.HasProperties):
    """An extension to the ``HasProperties`` class which supports parent-child
    relationships between instances.
    """

    
    __metaclass__ = SyncablePropertyOwner


    @classmethod
    def _saltSyncPropertyName(cls, propName):
        """Adds a prefix to the given property name, to be used as the
        name for the corresponding boolean sync property.
        """
        return '{}{}'.format(_SYNC_SALT_, propName)


    @classmethod
    def _unsaltSyncPropertyName(cls, propName):
        """Removes a prefix from the given property name, which was
        added by the :meth:`_saltSyncPropertyName` method.
        """
        return propName[len(_SYNC_SALT_):]
 

    @classmethod
    def getSyncPropertyName(cls, propName):
        """Returns the name of the boolean property which can be used to
        toggle binding of the given property to the parent property of
        this instance.
        """
        return cls._saltSyncPropertyName(propName)

    
    @classmethod
    def getSyncProperty(cls, propName):
        """Returns the :class:`.PropertyBase` instance of the boolean property
        which can be used to toggle binding of the given property to the parent
        property of this instance.
        """
        return cls.getProp(cls.getSyncPropertyName(propName))

    
    def __init__(self, **kwargs):
        """Create a ``SyncableHasProperties`` instance.

        If this ``SyncableHasProperties`` instance does not have a parent,
        there is no need to call this constructor explicitly. Otherwise, the
        parent must be an instance of the same class to which this instance's
        properties should be bound.
        
        :arg parent:   Another ``SyncableHasProperties`` instance, which has 
                       the same type as this instance.
        
        :arg nobind:   A sequence of property names which should not be bound
                       with the parent.
        
        :arg nounbind: A sequence of property names which cannot be unbound
                       from the parent.

        :arg state:    Initial synchronised state. Can be either ``True`` or
                       ``False``, in which case all properties will initially
                       be either synced or unsynced. Or can be a dictionary
                       of ``{propName : boolean}`` mappings, defining the sync
                       state for each property.

        :arg kwargs:   Other arguments are passed to the
                       :meth:`.HasProperties.__init__` method.
        """

        parent   = kwargs.pop('parent',   None)
        nobind   = kwargs.pop('nobind',   [])
        nounbind = kwargs.pop('nounbind', [])
        state    = kwargs.pop('state',    True)
        
        props.HasProperties.__init__(self, **kwargs)
        
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

            for pn in propNames:

                if isinstance(state, dict): pState = state.get(pn, True)
                else:                       pState = state
                
                if   not self.canBeSyncedToParent(    pn): pState = False
                elif not self.canBeUnsyncedFromParent(pn): pState = True
                
                self._initSyncProperty(pn, pState)

                    
    def getParent(self):
        """Returns the parent of this instance, or ``None`` if there is no
        parent.

        On child ``SyncableHasProperties`` instances, this method must not
        be called before :meth:`__init__` has been called. If this happens,
        an :exc:`AttributeError` will be raised.
        """

        if self._parent is None: return None
        else:                    return self._parent()


    def getChildren(self):
        """Returns a list of all children that are synced to this parent
        instance, or ``None`` if this instance is not a parent.
        """
        if self._parent is not None:
            return None

        children = [c() for c in self._children]
        children = filter(lambda c: c is not None, children)

        return children
                
    
    def _saltSyncListenerName(self, propName):
        """Adds a prefix and a suffix to the given property name, to be used
        as the name for an internal listener on the corresponding boolean sync
        property.

        """
        return '{}{}_{}'.format(_SYNC_SALT_, propName, id(self))


    def _initSyncProperty(self, propName, initState):
        """Called by child instances from :meth:`__init__`.

        Configures a binding between this instance and its parent for the
        specified property.
        """
        
        bindPropName  = self._saltSyncPropertyName(propName)
        bindPropObj   = self.getProp(bindPropName)
        bindPropVal   = bindPropObj.getPropVal(self)

        if initState and not self.canBeSyncedToParent(propName):
            raise ValueError('Invalid initial state for '
                             'nobind property {}'.format(propName))

        if (not initState) and (not self.canBeUnsyncedFromParent(propName)):
            raise ValueError('Invalid initial state for '
                             'nounbindproperty {}'.format(propName)) 

        if not self.canBeSyncedToParent(propName):
            bindPropVal.set(False)
            return

        bindPropVal.set(initState)

        if self.canBeUnsyncedFromParent(propName):
            lName = self._saltSyncListenerName(propName)
            bindPropVal.addListener(lName, self._syncPropChanged)

        if initState:
            self.bindProps(propName, self._parent()) 

        
    def _syncPropChanged(self, value, valid, ctx, bindPropName):
        """Called when a hidden boolean property controlling the sync
        state of the specified real property changes.

        Changes the sync state of the property accordingly.
        """

        propName    = self._unsaltSyncPropertyName(bindPropName)
        bindPropVal = getattr(self, bindPropName)

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

        If this ``SyncableHasProperties`` instance has no parent, a
        :exc:`RuntimeError` is raised. If the specified property is in the
        ``nobind`` list (see :meth:`__init__`), a :exc:`RuntimeError` is
        raised.

        ..note:: The ``nobind`` check can be avoided by calling
        :func:`.bindable.bindProps` directly. But don't do that.
        """
        if propName in self._nobind:
            raise RuntimeError('{} cannot be bound to '
                               'parent'.format(propName))

        bindPropName = self._saltSyncPropertyName(propName)
        setattr(self, bindPropName, True)

    
    def unsyncFromParent(self, propName):
        """Unsynchronise the given property from the parent instance.

        If this :class:`SyncableHasProperties` instance has no parent, a
        :exc:`RuntimeError` is raised. If the specified property is in the
        `nounbind` list (see :meth:`__init__`), a :exc:`RuntimeError` is
        raised.

        ..note:: The ``nounbind`` check can be avoided by calling
        :func:`bindable.bindProps` directly. But don't do that.
        """
        if propName in self._nounbind:
            raise RuntimeError('{} cannot be unbound from '
                               'parent'.format(propName))        
        
        bindPropName = self._saltSyncPropertyName(propName)
        setattr(self, bindPropName, False)


    def syncAllToParent(self):
        """Synchronises all properties to the parent instance.
        
        Does not attempt to synchronise properties in the ``nobind`` list.
        """
        propNames = self.getAllProperties()[0]

        for propName in propNames:
            if propName in self._nounbind or \
               propName in self._nobind:
                continue

            self.syncToParent(propName)


    def unsyncAllFromParent(self):
        """Unynchronises all properties from the parent instance.
        
        Does not attempt to synchronise properties in the ``nounbind`` list.
        """
        propNames = self.getAllProperties()[0]

        for propName in propNames:
            if propName in self._nounbind or \
               propName in self._nobind:
                continue

            self.unsyncFromParent(propName)         


    def detachFromParent(self):
        """If this is a child ``SyncableHasProperties`` instance, it
        detaches itself from its parent. This is an irreversible operation.

        TODO: Add the ability to dynamically set/clear the parent
              SHP instance.
        """

        if self._parent is None or self._parent() is None:
            self._parent = None
            return

        parent    = self._parent()
        propNames = self.getAllProperties()[0]

        for propName in propNames:
            if propName not in self._nounbind:
                syncPropName = self._saltSyncPropertyName(propName)
                lName        = self._saltSyncListenerName(propName)
                self.unsyncFromParent(propName)
                self.removeListener(syncPropName, lName)

        for c in list(parent._children):
            if c() is self:
                parent._children.remove(c)

        self._parent = None
 
        
    def isSyncedToParent(self, propName):
        """Returns ``True`` if the specified property is synced to the parent
        of this ``SyncableHasProperties`` instance, ``False`` otherwise.
        """
        return getattr(self, self._saltSyncPropertyName(propName))


    def anySyncedToParent(self):
        """Returns ``True`` if any properties are synced to the parent
        of this ``SyncableHasProperties`` instance, ``False`` otherwise.
        """
        propNames = self.getAllProperties()[0]
        return any([self.isSyncedToParent(p) for p in propNames])


    def allSyncedToParent(self):
        """Returns ``True`` if all properties are synced to the parent
        of this ``SyncableHasProperties`` instance, ``False`` otherwise.
        """
        propNames = self.getAllProperties()[0]
        return all([self.isSyncedToParent(p) for p in propNames]) 

    
    def canBeSyncedToParent(self, propName):
        """Returns ``True`` if the given property can be synced between this
        ``SyncableHasProperties`` instance and its parent (see the ``nobind``
        parameter in :meth:`__init__`).
        """
        return propName not in self._nobind

    
    def canBeUnsyncedFromParent(self, propName):
        """Returns ``True`` if the given property can be unsynced between this
        ``SyncableHasProperties`` instance and its parent (see the
        ``nounbind`` parameter in :meth:`__init__`).
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
