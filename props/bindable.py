#!/usr/bin/env python
#
# bindable.py - An extension to the HasProperties class which allows
# a master-slave relationship to exist between instances.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""The :mod:`bindable` module provides the :class:`BindableHasProperties`
class, an extension to the :class:`props.HasProperties` class which allows a
parent-child relationship to exist between instances. All that is needed to
make use of this functionality is to extend the :class:`BindableHasProperties`
class instead of the :class:`HasProperties` class::

    >>> import props

    >>> class MyObj(props.BindableHasProperties):
    >>>     myint = props.Int()
    >>>     def __init__(self, parent=None):
    >>>         props.BindableHasProperties.__init__(self, parent)
    >>>

Given a class definition such as the above, a parent-child relationship
between two instances can be set up as follows::

    >>> myParent = MyObj()
    >>> myChild  = MyObj(myParent)

The ``myint`` properties of both instances are now bound to each
other - when it changes in one instance, that change is propagated to the
other instance::

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

This binding can be toggled on the child instance, via the
:meth:`unbindFromParent` and :meth:`bindToParent` methods of the
:class:`BindableHasProperties` class.  Listeners to binding state changes may
be registered on the child instance via the :meth:`addBindChangeListener`
method (and de-registered via the :meth:`removeBindChangeListener` method).

A one-to-many binding relationship is possible between one parent, and many
children.
"""

import logging
log = logging.getLogger(__name__)

import properties       as props
import properties_types as types


_BIND_SALT_ = '_bind_'
"""Constant string added to binding-related property names and listeners."""


class BindablePropertyOwner(props.PropertyOwner):
    """Metaclass for the :class:`BindableHasProperties` class. Creates
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
            # the BindableHasProperties.__init__ method.
            bindProp = types.Boolean(default=True)
            newAttrs['{}{}'.format(_BIND_SALT_, propName)] = bindProp

        newCls = super(BindablePropertyOwner, cls).__new__(
            cls, name, bases, newAttrs)

        return newCls 

    
class BindableHasProperties(props.HasProperties):
    """An extension to the :class:`props.HasProperties` class which supports
    parent-child relationships between instances.
    """

    
    __metaclass__ = BindablePropertyOwner

    
    def __init__(self, parent=None, nobind=None, nounbind=None):
        """Create a :class:`BindableHasProperties` object.

        If this :class:`BindableHasProperties` object does not have a parent,
        there is no need to call this constructor explicitly. Otherwise, the
        parent must be an instance of the same class to which this instance's
        properties should be bound.
        
        :arg parent:   Another :class:`Bindable HasProperties` instance, which
                       has the same type as this instance.
        
        :arg nobind:   A sequence of property names which should not be bound
                       with the parent.
        
        :arg nounbind: A sequence of property names which cannot be unbound
                       from the parent.
        """
        if nobind   is None: nobind   = []
        if nounbind is None: nounbind = []

        self._parent   = parent
        self._nobind   = nobind
        self._nounbind = nounbind

        # Get a list of all the
        # properties of this class
        propNames, propObjs  = super(
            BindableHasProperties,
            self).getAllProperties()

        # If parent is none, then this instance
        # is a 'parent' instance, and doesn't need
        # to worry about being bound. So we'll
        # remove all the _bind_ properties which
        # were created by the metaclass
        if parent is None:
            for propName in propNames:
                if propName.startswith(_BIND_SALT_):
                    self.__dict__[propName] = None

        # Otherwise, this instance is a 'child'
        # instance - set up a binding between
        # this instance and its parent for every
        # property - see _initBindProperty
        else:

            if not isinstance(parent, self.__class__):
                raise TypeError('parent is of a different type '
                                '({} != {})'.format(parent.__class__,
                                                    self.__class__))

            propNames, _ = self.getAllProperties()

            log.debug('Binding properties of {} ({}) to parent ({})'.format(
                self.__class__.__name__, id(self), id(parent)))

            for propName in propNames:
                self._initBindProperty(propName)


    def _initBindProperty(self, propName):
        """Called by child instances from __init__.

        Configures a binding between this instance and its parent for the
        specified property.
        """
        
        bindPropName  = '{}{}'.format(_BIND_SALT_, propName)
        bindPropObj   = self.getProp(bindPropName)
        bindPropVal   = bindPropObj.getPropVal(self)

        if not self.canBeBoundToParent(propName):
            bindPropVal.set(False)
            return

        bindPropVal.set(True)

        if self.canBeUnboundFromParent(propName):
            lName = '{}{}_{}'.format(_BIND_SALT_, propName, id(self))
            bindPropVal.addListener(
                lName,
                lambda *a: self._bindPropChanged(propName, *a))

        self.bindProps(propName, self._parent)        

            
    def _bindPropChanged(self, propName, *a):
        """Called when a hidden boolean property controlling the binding
        state of the specified real property changes.

        Changes the binding state of the property accordingly.
        """

        bindPropName = '{}{}'.format(_BIND_SALT_, propName)
        bindPropVal  = getattr(self, bindPropName)

        if bindPropVal and (propName in self._nobind):
            raise RuntimeError('{} cannot be bound to '
                               'parent'.format(propName))

        if (not bindPropVal) and (propName in self._nounbind):
            raise RuntimeError('{} cannot be unbound from '
                               'parent'.format(propName))
        self.bindProps(propName, self._parent, unbind=(not bindPropVal)) 

        
    @classmethod 
    def getAllProperties(cls):
        """Returns all of the properties of this :class:`BindableHasProperties`
        class, not including the hidden boolean properties which control 
        binding states.
        """

        # TODO this code will crash for BHP
        # objects which have no properties
        
        propNames, propObjs = super(
            BindableHasProperties,
            cls).getAllProperties()

        propNames, propObjs  = zip(
            *filter(lambda (pn, p) : not pn.startswith(_BIND_SALT_),
                    zip(propNames, propObjs)))

        return propNames, propObjs
        
                    
    def getParent(self):
        """Returns the parent of this instance, or ``None`` if there is no
        parent.
        """
        return self._parent


    def bindToParent(self, propName):
        """Bind the given property with the parent instance.

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

        bindPropName = '{}{}'.format(_BIND_SALT_, propName)
        setattr(self, bindPropName, True)

    
    def unbindFromParent(self, propName):
        """Unbind the given property from the parent instance.

        If this :class:`HasProperties` instance has no parent, a
        `RuntimeError` is raised. If the specified property is in the
        `nounbind` list (see :meth:`__init__`), a `RuntimeError` is raised.

        ..note:: The ``nounbind`` check can be avoided by calling
        :meth:`bindProps` directly. But don't do that. 
        """
        if propName in self._nounbind:
            raise RuntimeError('{} cannot be unbound from '
                               'parent'.format(propName))        
        
        bindPropName = '{}{}'.format(_BIND_SALT_, propName)
        setattr(self, bindPropName, False) 

        
    def isBoundToParent(self, propName):
        """Returns true if the specified property is bound to the parent of
        this :class:`HasProperties` instance, ``False`` otherwise.
        """
        return getattr(self, '{}{}'.format(_BIND_SALT_, propName))

    
    def canBeBoundToParent(self, propName):
        """Returns ``True`` if the given property can be bound between a
        child and its parent (see the ``nobind`` parameter in
        :meth:`__init__`).
        """
        return propName not in self._nobind

    
    def canBeUnboundFromParent(self, propName):
        """Returns ``True`` if the given property can be unbound between a
        child and its parent (see the ``nounbind`` parameter in
        :meth:`__init__`).
        """ 
        return propName not in self._nounbind


    def addBindChangeListener(self, propName, listenerName, callback):
        """Registers the given callback function to be called when
        the binding state of the specified property changes.
        """
        bindPropName = '{}{}'.format(_BIND_SALT_, propName)
        self.addListener(bindPropName, listenerName, callback)

        
    def removeBindChangeListener(self, propName, listenerName):
        """De-registers the given listener from receiving binding
        state changes.
        """ 
        bindPropName = '{}{}'.format(_BIND_SALT_, propName)
        self.removeListener(bindPropName, listenerName)
