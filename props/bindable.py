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

    if not unbind:
        myPropVal.setAttributes(otherPropVal.getAttributes())
        myPropVal.set(          otherPropVal.get())
        
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

    # TODO You're almost certainly not handling
    # unbind=True properly in this code

    # Force the two lists to have
    # the same number of elements
    if not unbind:
        if len(myPropVal) > len(otherPropVal):
            del myPropVal[len(otherPropVal):]
    
        elif len(myPropVal) < len(otherPropVal):
            myPropVal.extend(otherPropVal[len(myPropVal):])

    # Create a mapping between the
    # PropertyValue pairs across
    # the two lists
    myPropValList    = myPropVal   .getPropertyValueList()
    otherPropValList = otherPropVal.getPropertyValueList()
    propValMap       = Bidict()

    # Inhibit list-level notification due to item
    # changes during the initial sync - we'll
    # manually do a list-level notification after
    # all the list values have been synced
    notifState = myPropVal.getNotificationState()
    myPropVal.disableNotification()

    # Copy item values from the master list
    # to the slave list, and save the mapping
    for myItem, otherItem in zip(myPropValList, otherPropValList):

        log.debug('Binding list item {}.{} ({}) <- {}.{} ({})'.format(
            self.__class__.__name__,
            myProp.getLabel(self),
            myItem.get(),
            other.__class__.__name__,
            otherProp.getLabel(other),
            otherItem.get()))

        # Disable item notification - we'll
        # manually force a notify after the
        # sync
        itemNotifState = myItem.getNotificationState()
        myItem.disableNotification()

        # Bind attributes between PV item pairs,
        # but not value - value change of items
        # in a list is handled at the list level
        _bindPropVals(myItem, otherItem, val=False, unbind=unbind)
        propValMap[myItem] = otherItem
        
        atts = otherItem.getAttributes()

        # Set attributes first, because the attribute
        # values may influence/modify the property value
        myItem.setAttributes(atts)
        myItem.set(otherItem.get())

        # Notify item level listeners of the value
        # change (if notification was enabled).
        #
        # TODO This notification occurs even
        # if the two PV objects had the same
        # value before the sync - you should
        # notify only if the myItem PV value
        # has changed.
        myItem.setNotificationState(itemNotifState)
        if itemNotifState:

            # notify attribute listeners first
            for name, val in atts.items():
                myItem._orig_notifyAttributeListeners(name, val)            
            
            myItem._orig_notify()


    # This mapping is stored on the PVL objects,
    # and used by the _syncListPropVals function
    setattr(myPropVal,
            '_{}_propValMap'.format(id(otherPropVal)),
            propValMap)
    setattr(otherPropVal,
            '_{}_propValMap'.format(id(myPropVal)),
            propValMap)

    # When a master list is synchronised to a slave list,
    # it stores the slave list ID in the _syncing set.
    # 
    # The _syncing set is checked before starting a
    # sync, so that the slave list is not synchronised
    # back to the master list during the sync.
    # See the notify function below.
    myPropVal   ._syncing = set()
    otherPropVal._syncing = set()

    # Bind list-level value/attributes
    # between the PropertyValueList objects
    atts = otherPropVal.getAttributes()
    myPropVal.setAttributes(atts)
    
    _bindPropVals(myPropVal, otherPropVal, unbind=unbind)

    # Manually notify list-level listeners
    #
    # TODO This notification will occur
    # even if the two lists had the same
    # value before being bound. It might
    # be worth only performing the
    # notification if the list has changed
    # value
    myPropVal.setNotificationState(notifState)
    if notifState:
        # Notify attribute listeners first
        for name, val in atts.items():
            myPropVal._orig_notifyAttributeListeners(name, val)
        
        myPropVal._orig_notify()


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

    if unbind: action = 'Unbinding'
    else:      action = 'Binding'

    log.debug('{} property values '
              '(val={}, att={}) {}.{} <-> {}.{}'.format(
                  action,
                  val,
                  att,
                  myPropVal._context.__class__.__name__,
                  myPropVal._name,
                  otherPropVal._context.__class__.__name__,
                  otherPropVal._name))

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

    # If the change was due to the values of one or more PV
    # items changing (as opposed to a list modification -
    # addition/removal/reorder), the indices of the PV objects
    # which changed are stored in this list and returned
    propValsChanged = []
    
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

                # Bind the attributes of
                # the two new PV objects
                _bindPropVals(mpv, spv, val=False)

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
                
    # list re-order, or individual
    # value change
    else:
        
        mpvs     = masterList.getPropertyValueList()
        mpvids   = map(id, mpvs)
        newOrder = []

        # loop through the PV objects in the slave list,
        # and build a list of indices of the corresponding
        # PV objects in the master list
        for i, spv in enumerate(slaveList.getPropertyValueList()):

            mpv = propValMap[spv]
            newOrder.append(mpvids.index(id(mpv)))

        # If the master list order has been
        # changed, re-order the slave list
        if newOrder != range(len(slaveList)):
            slaveList.reorder(newOrder)

        # The list order hasn't changed, so
        # this call must have been triggered
        # by a value change. Find the items
        # which have changed, and copy the
        # new value across to the slave list
        else:
            
            for i, (masterVal, slaveVal) in \
                enumerate(
                    zip(masterList.getPropertyValueList(),
                        slaveList .getPropertyValueList())):

                if masterVal == slaveVal: continue
                
                notifState = slaveVal.getNotificationState()
                slaveVal.disableNotification()
 
                slaveVal.set(masterVal.get())
                propValsChanged.append(i)
                    
                slaveVal.setNotificationState(notifState)

    return propValsChanged


def notify(self):
    """This method replaces
    :meth:`~props.properties_value.PropertyValue.notify`. It ensures that
    bound :class:`~props.properties_value.ProperyValue` objects are
    synchronised to have the same value, before any registered listeners
    are notified.
    """
    
    boundPropVals = self.__dict__.get('boundPropVals', [])
    changeState   = [False] * len(boundPropVals)

    # Sync all the values that need syncing    
    for i, bpv in enumerate(boundPropVals):

        # Normal PropertyValue object (i.e. not a PropertyValueList)
        if not isinstance(self, properties_value.PropertyValueList):

            # Don't bother if the values are already equal
            if self == bpv: continue

            # Make a note of the fact that the 
            # value of this slave PV is changing
            changeState[i] = True

            log.debug('Syncing bound property values {} - {}'.format(
                self._name, bpv._name))

            # Sync the PV, but don't notify
            notifState = bpv.getNotificationState()
            bpv.disableNotification()
            bpv.set(self.get())
            bpv.setNotificationState(notifState)

        # PropertyValueList instances
        else:

            # lists already contain the same value,
            # or the other list is already in the
            # process of syncing to this list
            if (self == bpv) or self in bpv._syncing:
                continue

            log.debug('Syncing bound property value lists '
                      '{}.{} ({}) - {}.{} ({})'.format(
                          self._context.__class__.__name__,
                          self._name,
                          id(self._context),
                          bpv._context.__class__.__name__,
                          bpv._name,
                          id(bpv._context)))

            self._syncing.add(bpv)

            notifState = bpv.getNotificationState()
            bpv.disableNotification()
            
            changeState[i] = _syncPropValLists(self, bpv)

            bpv.setNotificationState(notifState)

            self._syncing.remove(bpv)

    # Call the registered property listeners 
    # of any slave PVs which changed value
    for i, bpv in enumerate(boundPropVals):

        if changeState[i] is False: continue

        # Normal PropertyValue objects
        if not isinstance(bpv, properties_value.PropertyValueList):
            bpv.notify()

        # PropertyValueList objects
        else:
            bpvVals     = bpv.getPropertyValueList()
            valsChanged = changeState[i]

            listNotifState = bpv.getNotificationState()
            bpv.disableNotification()

            # Call the notify method on any individual
            # list items which changed value
            for i in valsChanged:
                bpvVals[i].notify()

            # Notify any list-level
            # listeners on the slave list
            bpv.setNotificationState(listNotifState)
            bpv.notify()

    # Now that the master-slave values are synced,
    # call the real PropertyValue.notify method
    self._orig_notify()


def notifyAttributeListeners(self, name, value):
    """This method replaces the
    :meth:`~props.properties_value.PropertyValue.notifyAttributeListeners`
    method. It ensures that the attributes of any bound
    :class:`~props.properties_value.PropertyValue` instances are synchronised
    before any attribute listeners are notified.
    """
    
    boundPropVals = self.__dict__.get('boundAttPropVals', [])
    changeState   = [False] * len(boundPropVals)

    # synchronise the attribute value
    for i, bpv in enumerate(boundPropVals):

        try:
            if bpv.getAttribute(name) == value: continue
        except KeyError:
            pass

        changeState[i] = True
        notifState     = bpv.getNotificationState()
        
        bpv.disableNotification()
        bpv.setAttribute(name, value)
        bpv.setNotificationState(notifState)

    # Notify the attribute listeners of any slave
    # PVs for which the attribute changed value
    #
    # TODO what if the attribute change caused
    # a change to the property value?
    # 
    for bpv in boundPropVals:
        if changeState[i]:
            bpv.notifyAttributeListeners(name, value)

    self._orig_notifyAttributeListeners(name, value)

                         
# Patch the HasPropertyies and PropertyValue
properties.HasProperties.bindProps   = bindProps
properties.HasProperties.unbindProps = unbindProps
properties.HasProperties.isBound     = isBound

properties_value.PropertyValue._orig_notify = \
    properties_value.PropertyValue.notify
properties_value.PropertyValue._orig_notifyAttributeListeners = \
    properties_value.PropertyValue.notifyAttributeListeners

properties_value.PropertyValue.notify                   = notify
properties_value.PropertyValue.notifyAttributeListeners = \
    notifyAttributeListeners
