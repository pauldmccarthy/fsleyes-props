#!/usr/bin/env python
#
# bindable.py - This module adds functionality to the HasProperties class
# to allow properties from different instances to be bound to each other.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""The :mod:`bindable` module adds functionality to the
:class:`~props.properties.HasProperties` class to allow properties from
different instances to be bound to each other.

The functions defined in this module should be considered to be methods
of the :class:`~props.properties.HasProperties` class - they're separated
purely to keep the properties.py file size down.
"""

import properties as props

    
def bindProps(self, propName, other, otherPropName=None, unbind=False):
    """Binds the properties specified by ``propName``  and
    ``otherPropName`` such that changes to one are applied
    to the other.

    :arg str propName:        The name of a property on this
                              :class:`HasProperties` instance.
    
    :arg HasProperties other: Another :class:`HasProperties` instance.
    
    :arg str otherPropName:   The name of a property on ``other`` to
                              bind to. If ``None`` it is assumed that
                              there is a property on ``other`` called
                              ``propName``.

    :arg unbind:              If ``True``, the properties are unbound.
                              See the :meth:`unbindProps` method.
    """

    if otherPropName is None: otherPropName = propName

    myProp    = self .getProp(propName)
    otherProp = other.getProp(otherPropName)

    if type(myProp) != type(otherProp):
        raise ValueError('Properties must be of the '
                         'same type to be bound')

    if isinstance(myProp, props.ListPropertyBase):
        _bindListProps(self, myProp, other, otherProp, unbind)
    else:
        _bindProps(self, myProp, other, otherProp, unbind)


def unbindProps(self, propName, other, otherPropName=None):
    """Unbinds two properties previously bound via a call to
    :meth:`bindProps`. 
    """
    self.bindProps(propName, other, otherPropName, unbind=True)


def isBound(self, propName, other, otherPropName=None):
    """Returns ``True`` if the specified property is bound to the
    other :class:`HasProperties` object, ``False`` otherwise.
    """
    
    if otherPropName is None: otherPropName = propName

    myProp       = self     .getProp(   propName)
    otherProp    = other    .getProp(   otherPropName)
    myPropVal    = myProp   .getPropVal(self)
    otherPropVal = otherProp.getPropVal(other)

    myPropName    = myProp   .getLabel(self)
    otherPropName = otherProp.getLabel(other)

    myName, otherName = _makeBindingNames(self,
                                          other,
                                          myPropName,
                                          otherPropName)
    
    return myPropVal   .hasListener(myName) and \
           otherPropVal.hasListener(otherName)
    

def _bindProps(self, myProp, other, otherProp, unbind=False):
    """Binds two :class:`~props.properties_value.PropertyValue` instances
    together.

    The :meth:`_bindListProps` method is used to bind two
    :class:`~props.properties_value.PropertyValueList` instances.

    :arg myProp:    The :class:`PropertyBase` instance of this
                    :class:`HasProperties` instance.
    
    :arg other:     The other :class:`HasProperties` instance.
    
    :arg otherProp: The :class:`PropertyBase` instance of the ``other``
                    :class:`HasProperties` instance.

    :arg unbind:    If ``True``, the properties are unbound.
    """

    myPropVal    = myProp   .getPropVal(self)
    otherPropVal = otherProp.getPropVal(other)

    _bindPropVals(self,
                  other,
                  myPropVal,
                  otherPropVal,
                  myProp.getLabel(self),
                  otherProp.getLabel(other),
                  unbind=unbind)


def _bindListProps(self, myProp, other, otherProp, unbind=False):
    """Binds two :class:`~props.properties_value.PropertyValueList`
    instances together. 

    The two properties must be non-mutable (i.e. their lengths must be
    equal, and may not be changed). If this is not the case, a
    :exc:`RuntimeError` is raised.

    :arg myProp:    The :class:`ListPropertyBase` instance of this
                    :class:`HasProperties` instance.
    
    :arg other:     The other :class:`HasProperties` instance.
    
    :arg otherProp: The :class:`ListPropertyBase` instance of the
                    ``other`` :class:`HasProperties` instance.

    :arg unbind:    If ``True``, the properties are unbound.
    """

    myPropVal    = myProp   .getPropVal(self)
    otherPropVal = otherProp.getPropVal(other)

    myMinLen    = myPropVal   .getAttribute('minlen')
    myMaxLen    = myPropVal   .getAttribute('maxlen')
    otherMinLen = otherPropVal.getAttribute('minlen')
    otherMaxLen = otherPropVal.getAttribute('maxlen')

    # if myMinLen    is None        or \
    #    myMaxLen    is None        or \
    #    otherMinLen is None        or \
    #    otherMaxLen is None        or \
    #    myMinLen    != myMaxLen    or \
    #    otherMinLen != otherMaxLen or \
    #    myMinLen    != otherMinLen:
    #     raise RuntimeError('Only non-mutable lists of '
    #                        'the same length may be bound')

    # copy value and attributes for each
    # pair of PropertyValue items and add
    # value/attribute listeners for each pair
    myPropValList    = myPropVal   .getPropertyValueList()
    otherPropValList = otherPropVal.getPropertyValueList()

    _bindPropVals(self,
                  other,
                  myPropVal,
                  otherPropVal,
                  myProp.getLabel(self),
                  otherProp.getLabel(other),
                  val=False,
                  unbind=unbind)

    for myItem, otherItem in zip(myPropValList, otherPropValList):
        _bindPropVals(self,
                      other,
                      myItem,
                      otherItem,
                      '{}_Item'.format(myProp.getLabel(self)),
                      '{}_Item'.format(otherProp.getLabel(other)),
                      unbind=unbind)

        
def _makeBindingNames(self, other, myPropName, otherPropName):
    """Generates property listener names for binding."""
    
    myName    = 'bindProps_{}_{}_{}_{}'.format(myPropName,
                                               otherPropName,
                                               id(self),
                                               id(other))
    otherName = 'bindProps_{}_{}_{}_{}'.format(otherPropName,
                                               myPropName,
                                               id(other),
                                               id(self))
    return myName, otherName


def _bindPropVals(self,
                  other,
                  myPropVal,
                  otherPropVal,
                  myPropName,
                  otherPropName,
                  val=True,
                  att=True,
                  unbind=False):
    """Binds two :class:`~props.properties_value.PropertyValue`
    instances together such that when the value of one changes,
    the other is changed. Attributes are also bound between the
    two instances.
    """

    myName, otherName = _makeBindingNames(self,
                                          other,
                                          myPropName,
                                          otherPropName)

    if val:
        myPropVal.set(otherPropVal.get())

        def onVal(slave, value, *a):
            if slave.get() != value:
                slave.set(value)

        if not unbind:
            myPropVal.addListener(
                myName, lambda *a: onVal(otherPropVal, *a))
            otherPropVal.addListener(
                otherName, lambda *a: onVal(myPropVal, *a))
        else:
            myPropVal   .removeListener(myName)
            otherPropVal.removeListener(otherName) 

    if att:
        myPropVal.setAttributes(otherPropVal.getAttributes()) 

        def onAtt(slave, ctx, attName, value):
            slave.setAttribute(attName, value)
        
        if not unbind:
            myPropVal.addAttributeListener(
                myName, lambda *a: onAtt(otherPropVal, *a))
            otherPropVal.addAttributeListener(
                otherName, lambda *a: onAtt(myPropVal, *a))
        else:
            myPropVal   .removeAttributeListener(myName)
            otherPropVal.removeAttributeListener(otherName)

props.HasProperties.bindProps   = bindProps
props.HasProperties.unbindProps = unbindProps
props.HasProperties.isBound     = isBound
