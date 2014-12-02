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

The logic defined in this module is separated purely to keep the
:mod:`props.properties` and :mod:`props.properties_value` module file sizes
down.

The :func:`bindProps`, :func:`unbindProps`, and :func:`isBound` functions
defined in this module are added (monkey-patched) as methods of the
:class:`~props.properties.HasProperties` class.

The :func:`notify` and :func:`notifyAttributeListeners` functions replace
the :class:`~props.properties_value.PropertyValue` methods of the same
names.
"""

import logging
log = logging.getLogger(__name__)


import properties
import properties_value


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

    if isinstance(myProp, properties.ListPropertyBase):
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

    myBoundPropVals    = myPropVal   .__dict__.get('boundPropVals', set())
    otherBoundPropVals = otherPropVal.__dict__.get('boundPropVals', set())

    return (otherPropVal in myBoundPropVals and
            myPropVal    in otherBoundPropVals)
    

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
    myPropVal.set(otherPropVal.get())
    _bindPropVals(myPropVal, otherPropVal, unbind=unbind)


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
        myItem.set(otherItem.get())
        _bindPropVals(myItem, otherItem, unbind=unbind)

        propValMap[myItem] = otherItem

    # This mapping is stored on the PVL objects,
    # and used by the _syncListPropVals function
    setattr(myPropVal,    '_{}_propValMap'.format(id(otherPropVal)), propValMap)
    setattr(otherPropVal, '_{}_propValMap'.format(id(myPropVal)),    propValMap)

    # When a master list is synchronised to a slave list,
    # it stores the slave list ID in the _syncing set.
    # 
    # The _syncing set is checked before starting a
    # sync, so that the slave list is not synchronised
    # back to the master list during the sync.
    # See the notify function below.
    myPropVal   ._syncing = set()
    otherPropVal._syncing = set()

    # Bind list-level attributes between
    # the PropertyValueList objects
    _bindPropVals(myPropVal, otherPropVal, unbind=unbind)


def _bindPropVals(myPropVal,
                  otherPropVal,
                  val=True,
                  att=True,
                  unbind=False):
    """Binds two :class:`~props.properties_value.PropertyValue`
    instances together such that when the value of one changes,
    the other is changed. Attributes are also bound between the
    two instances.
    """

    mine  = myPropVal
    other = otherPropVal

    myBoundPropVals       = mine .__dict__.get('boundPropVals',    set())
    myBoundAttPropVals    = mine .__dict__.get('boundAttPropVals', set())
    otherBoundPropVals    = other.__dict__.get('boundPropVals',    set())
    otherBoundAttPropVals = other.__dict__.get('boundAttPropVals', set()) 

    if val:
        if unbind:
            myBoundPropVals   .remove(other)
            otherBoundPropVals.remove(mine)
        else:
            myBoundPropVals   .add(other)
            otherBoundPropVals.add(mine) 
        
    if att:
        if unbind:
            myBoundAttPropVals   .remove(other)
            otherBoundAttPropVals.remove(mine)
        else:
            myBoundAttPropVals   .add(other)
            otherBoundAttPropVals.add(mine) 

    mine .boundPropVals    = myBoundPropVals
    mine .boundAttPropVals = myBoundAttPropVals
    other.boundPropVals    = otherBoundPropVals
    other.boundAttPropVals = otherBoundAttPropVals

    
def _syncPropValLists(masterList, slaveList):
    """Called when one of a pair of bound
    :class:`~props.properties_value.PropertyValueList` instances changes.
    
    Propagates the change on the ``masterList`` (either an addition, a
    removal, or a re-ordering) to the ``slaveList``.
    """

    propValMap = getattr(masterList, '_{}_propValMap'.format(id(slaveList)))

    # This flag (used as the return value of this
    # function) will be set to False if it turns
    # out that the list change which triggered
    # the call to this function was a change to
    # an individual value in the list (which is
    # not handled by this callback)
    slaveListChanged = True
    
    # one or more items have been
    # added to the master list
    if len(masterList) > len(slaveList):

        # Loop through the PV objects in the master
        # list, and search for any which do not have
        # a paired PV object in the slave list
        for i, mpv in enumerate(masterList.getPropertyValueList()):

            spv = propValMap.get(mpv, None)

            # we've found a value in the master
            # list which is not in the slave list
            if spv is None:

                # add a new value to the slave list
                slaveList.insert(i, mpv.get())

                # retrieve the corresponding PV
                # object that was created by
                # the slave list
                spvs = slaveList.getPropertyValueList()
                spv  = spvs[i]

                # register a mapping between the
                # new master and slave PV objects
                propValMap[mpv] = spv

                # Bind the two new PV objects
                _bindPropVals(mpv, spv)

    # one or more items have been
    # removed from the master list
    elif len(masterList) < len(slaveList):

        mpvs = masterList.getPropertyValueList()
        
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
            mpv = propValMap[spv]

            # we've found a value in the slave list
            # which is no longer in the master list 
            if mpv not in mpvs:

                # Delete the item from the slave
                # list, and delete the PV mapping
                del slaveList[ i]
                del propValMap[mpv]
                
    # list re-order (or individual value
    # change, which we don't care about)
    else:
        
        mpvs     = masterList.getPropertyValueList()
        newOrder = []

        # loop through the PV objects in the slave list,
        # and build a list of indices of the corresponding
        # PV objects in the master list
        for i, spv in enumerate(slaveList.getPropertyValueList()):

            mpv = propValMap[spv]
            newOrder.append(mpvs.index(mpv))

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

    return slaveListChanged


def notify(self):
    """
    """
    
    boundPropVals = self.__dict__.get('boundPropVals', [])
    
    if isinstance(self, properties_value.PropertyValueList):
        for i, bpv in enumerate(boundPropVals):

            # lists already contain the same value,
            # or the other list is already in the
            # process of syncing to this list
            if (self == bpv) or self in bpv._syncing:
                continue

            self._syncing.add(bpv)
            bpv.disableNotification()

            log.debug('Syncing bound property value lists {} - {}'.format(
                self._name, bpv._name))

            bpvChanged = _syncPropValLists(self, bpv)
            bpv.enableNotification()
            if bpvChanged:
                bpv.notify()
            self._syncing.remove(bpv)
            
    else:
        for bpv in boundPropVals:
            if self == bpv: continue
            log.debug('Syncing bound property values {} - {}'.format(
                self._name, bpv._name))
            bpv.set(self.get())
            
    self._orig_notify()


def notifyAttributeListeners(self, name, value):
    
    boundPropVals = self.__dict__.get('boundAttPropVals', [])
    
    for bpv in boundPropVals:
        bpv.setAttribute(name, value)

    self._orig_notifyAttributeListeners(name, value)

                         
# Patch the HasPropertyies and PropertyValue
properties.HasProperties.bindProps   = bindProps
properties.HasProperties.unbindProps = unbindProps
properties.HasProperties.isBound     = isBound

properties_value.PropertyValue._orig_notify = \
    properties_value.PropertyValue.notify
properties_value.PropertyValue._orig_notifyAttributeListeners = \
    properties_value.PropertyValue._notifyAttributeListeners

properties_value.PropertyValue.notify                    = notify
properties_value.PropertyValue._notifyAttributeListeners = \
    notifyAttributeListeners
