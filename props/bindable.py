#!/usr/bin/env python
#
# parent.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import logging
log = logging.getLogger(__name__)

import properties       as props
import properties_types as types

_BIND_SALT = '_bind_'


class BindablePropertyOwner(props.PropertyOwner):
    """Metaclass for the :class:`BindableHasProperties` class. Creates
    a :class:`~props.Boolean` property for every other property in the
    class, which controls whether the corresponding property is bound
    to the parent or not.

    BindableHasProperties hierarchies are not supported at the moment.
    """

    def __new__(cls, name, bases, attrs):

        newAttrs = dict(attrs)

        for propName, propObj in attrs.items():
            
            if not isinstance(propObj, props.PropertyBase): continue
            
            bindProp = types.Boolean(default=True)
            newAttrs['{}{}'.format(_BIND_SALT, propName)] = bindProp

        newCls = super(BindablePropertyOwner, cls).__new__(
            cls, name, bases, newAttrs)

        return newCls 

    
class BindableHasProperties(props.HasProperties):

    __metaclass__ = BindablePropertyOwner

    def __init__(self, parent=None, nobind=None, nounbind=None):
        """Create a :class:`BindableHasProperties` object.

        If this :class:`BindableHasProperties` object does not have a parent,
        there is no need to call this constructor explicitly. Otherwise, the
        parent must be an instance of the same class to which this instance's
        properties should be bound.
        
        :arg parent:   Another :class:`Bindable HasProperties` instance, which
                       has the  same type as this instance.
        
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

        # If parent is none, then this instance
        # is a 'master' instance, and doesn't need
        # to worry about being bound. So we'll
        # remove all the _bind_ properties which
        # were created by the metaclass
        propNames, propObjs  = super(
            BindableHasProperties,
            self).getAllProperties()
 
        if parent is None:
            for propName in propNames:
                if propName.startswith(_BIND_SALT):
                    self.__dict__[propName] = None

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
        
        bindPropName  = '{}{}'.format(_BIND_SALT, propName)
        bindPropObj   = self.getProp(bindPropName)
        bindPropVal   = bindPropObj.getPropVal(self)

        if not self.canBeBoundToParent(propName):
            bindPropVal.set(False)
            return

        bindPropVal.set(True)

        if self.canBeUnboundFromParent(propName):
            lName = 'asdfasd'
            bindPropVal.addListener(
                lName,
                lambda *a: self._bindPropChanged(propName, *a))

        self.bindProps(propName, self._parent)        

            
    def _bindPropChanged(self, propName, *a):

        bindPropName = '{}{}'.format(_BIND_SALT, propName)
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
        """
        """

        # TODO this code will crash for BHP
        # objects which have no properties
        
        propNames, propObjs = super(
            BindableHasProperties,
            cls).getAllProperties()

        propNames, propObjs  = zip(
            *filter(lambda (pn, p) : not pn.startswith(_BIND_SALT),
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
        bindPropName = '{}{}'.format(_BIND_SALT, propName)
        setattr(self, bindPropName, True)

    
    def unbindFromParent(self, propName):
        """Unbind the given property from the parent instance.

        If this :class:`HasProperties` instance has no parent, a
        `RuntimeError` is raised. If the specified property is in the
        `nounbind` list (see :meth:`__init__`), a `RuntimeError` is raised.

        ..note:: The ``nounbind`` check can be avoided by calling
        :meth:`bindProps` directly. But don't do that. 
        """
        bindPropName = '{}{}'.format(_BIND_SALT, propName)
        setattr(self, bindPropName, False) 

        
    def isBoundToParent(self, propName):
        """Returns true if the specified property is bound to the parent of
        this :class:`HasProperties` instance, ``False`` otherwise.
        """
        return getattr(self, '{}{}'.format(_BIND_SALT, propName))

    
    def canBeBoundToParent(self, propName):
        """"""
        return propName not in self._nobind

    
    def canBeUnboundFromParent(self, propName):
        """"""
        return propName not in self._nounbind



    def addBindChangeListener(self, propName, listenerName, callback):
        bindPropName = '{}{}'.format(_BIND_SALT, propName)
        self.addListener(bindPropName, listenerName, callback)

        
    def removeBindChangeListener(self, propName, listenerName):
        bindPropName = '{}{}'.format(_BIND_SALT, propName)
        self.removeListener(bindPropName, listenerName)
