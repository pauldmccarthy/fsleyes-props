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

The :func:`bindProps`, :func:`unbindProps`, and :func:`isBound` functions
defined in this module are added as methods of the
:class:`~props.properties.HasProperties` class - the logic defined in this
module is separated purely to keep the :mod:`props.properties` module file
size down.
"""


import properties as props


class Bidict(object):
    """A bare-bones bi-directional dictionary, used for binding
    :class:`~props.properties_value.PropertyValueList` instances -
    see the :func:`_bindListProps` and :func:`_boundsListChanged`
    functions.
    """

    def __init__(self):
        self._thedict = {}

    def __setitem__(self, key, value):
        self._thedict[key]   = value
        self._thedict[value] = key

    def __delitem__(self, key):
        val = self._thedict.pop(key)
        self      ._thedict.pop(val)

    def get(self, key, default=None):
        return self._thedict.get(key, default)
    
    def __getitem__(self, key): return self._thedict.__getitem__(key)
    def __repr__(   self):      return self._thedict.__repr__()
    def __str__(    self):      return self._thedict.__str__() 

    
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

    :arg myProp:    The :class:`ListPropertyBase` instance of this
                    :class:`HasProperties` instance.
    
    :arg other:     The other :class:`HasProperties` instance.
    
    :arg otherProp: The :class:`ListPropertyBase` instance of the
                    ``other`` :class:`HasProperties` instance.

    :arg unbind:    If ``True``, the properties are unbound.
    """

    myPropVal    = myProp   .getPropVal(self)
    otherPropVal = otherProp.getPropVal(other)

    # Force the two lists to have
    # the same number of elements
    if not unbind:
        if len(myPropVal) > len(otherPropVal):
            del myPropVal[len(otherPropVal):]
    
        elif len(myPropVal) < len(otherPropVal):
            myPropVal.extend(otherPropVal[len(myPropVal):])

    # Bind item level values and attributes
    # between the two lists, and create a
    # mapping between the PropertyValue
    # pairs across the two lists
    myPropValList    = myPropVal   .getPropertyValueList()
    otherPropValList = otherPropVal.getPropertyValueList()
    propValMap       = Bidict()
    for myItem, otherItem in zip(myPropValList, otherPropValList):
        _bindPropVals(self,
                      other,
                      myItem,
                      otherItem,
                      '{}_Item'.format(myProp.getLabel(self)),
                      '{}_Item'.format(otherProp.getLabel(other)),
                      unbind=unbind)

        propValMap[id(myItem)] = id(otherItem)

    # Bind list-level attributes between
    # the PropertyValueList objects -
    # we manually add a list-level value
    # listener below, which deals with
    # list additiosn/removals/reorderings
    _bindPropVals(self,
                  other,
                  myPropVal,
                  otherPropVal,
                  myProp.getLabel(self),
                  otherProp.getLabel(other),
                  val=False,
                  unbind=unbind)

    # As promised - register listeners on each
    # PropertyValueList to synchronise list
    # additions, deletions, and re-orderings
    myName, otherName = _makeBindingNames(self,
                                          other,
                                          myProp.getLabel(self),
                                          otherProp.getLabel(other))

    def listChange(myListChanged, *a):
        _boundListChanged(self,
                          myProp,
                          other,
                          otherProp,
                          myPropVal,
                          otherPropVal,
                          myListChanged,
                          propValMap,
                          *a)        

    if not unbind:
        myPropVal   .addListener(myName,    lambda *a: listChange(True,  *a))
        otherPropVal.addListener(otherName, lambda *a: listChange(False, *a))
    else:
        myPropVal   .removeListener(myName)
        otherPropVal.removeListener(otherName)


def _boundListChanged(self,
                      myProp,
                      other,
                      otherProp,
                      myList,
                      otherList,
                      myListChanged,
                      propValMap,
                      *a):
    """Called when one of a pair of bound
    :class:`~props.properties_value.PropertyValueList` instances changes.
    
    Propagates the change (either an addition, a removal, or a re-ordering)
    to the other list.
    """

    if myList == otherList:
        return

    # The masterList is the list which has
    # changed, and the slaveList is the list
    # which needs to be synced to the master
    if myListChanged: masterList, slaveList = myList, otherList
    else:             masterList, slaveList = otherList, myList

    # This flag will be set to False if it turns
    # out that the list change which triggered
    # the call to this function was a change to
    # an individual value in the list (which is
    # not handled by this callback)
    slaveListChanged = True
    slaveList.disableNotification()
    
    # one or more items have been
    # added to the master list
    if len(masterList) > len(slaveList):

        # Loop through the PV objects in the master
        # list, and search for any which do not have
        # a paired PV object in the slave list
        for i, mpv in enumerate(masterList.getPropertyValueList()):

            spvid = propValMap.get(id(mpv), None)

            # we've found a value in the master
            # list which is not in the slave list
            if spvid is None:

                # add a new value to the slave list
                slaveList.insert(i, mpv.get())
                spv = slaveList.getPropertyValueList()[i]

                # register a mapping between the
                # new master and slave PV objects
                propValMap[id(mpv)] = id(spv)

                # Bind the two new PV objects
                _bindPropVals(self,
                              other,
                              mpv,
                              spv,
                              '{}_Item'.format(myProp.getLabel(self)),
                              '{}_Item'.format(otherProp.getLabel(other)))

    # one or more items have been
    # removed from the master list
    elif len(masterList) < len(slaveList):

        mpvIds = map(id, masterList.getPropertyValueList())
        
        # Loop through the PV objects in the slave
        # list, and check to see if their mapped
        # master PV object has been removed from
        # the master list. Loop backwards so we can
        # delete items from the slave list as we go,
        # without having to offset the list index.
        for i, spv in reversed(
                list(enumerate(slaveList.getPropertyValueList()))):

            # If this raises an error, there's a bug
            # in somebody's code ... probably mine.
            mpvid = propValMap[id(spv)]

            # we've found a value in the slave list
            # which is no longer in the master list 
            if mpvid not in mpvIds:

                # Delete the item from the slave
                # list, and delete the PV mapping
                del slaveList[ i]
                del propValMap[mpvid]
                
    # list re-order (or individual value
    # change, which we don't care about)
    else:
        
        mpvIds   = map(id, masterList.getPropertyValueList())
        newOrder = []

        # loop through the PV objects in the slave list,
        # and build a list of indices of the corresponding
        # PV objects in the master list
        for i, spv in enumerate(slaveList.getPropertyValueList()):

            mpvid = propValMap[id(spv)]
            newOrder.append(mpvIds.index(mpvid))

        # If the master list order has been
        # changed, re-order the slave list
        if newOrder != range(len(slaveList)):
            slaveListChanged = True
            slaveList.reorder(newOrder)

        # The list order hasn't changed, so
        # this call must have been triggered
        # by a value change, which we don't
        # care about
        else: slaveListChanged = False

    # Force notification on the slave
    # list if it has been changed
    slaveList.enableNotification()
    if slaveListChanged:
        slaveList.notify()

        
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

    # If val is true, bind the property values
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

    # If att is true, bind the property attributes
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
