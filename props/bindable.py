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
    propValMap       = []
    for myItem, otherItem in zip(myPropValList, otherPropValList):
        _bindPropVals(self,
                      other,
                      myItem,
                      otherItem,
                      '{}_Item'.format(myProp.getLabel(self)),
                      '{}_Item'.format(otherProp.getLabel(other)),
                      unbind=unbind)

        propValMap.append((id(myItem), id(otherItem)))

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

    if myListChanged:
        masterList, slaveList = myList, otherList
        masterIdx,  slaveIdx  = 0, 1
    else:
        masterList, slaveList = otherList, myList
        masterIdx,  slaveIdx  = 1, 0

    print 'listPropChanged'
    print
    print 'masterList: {}'.format(map(id, masterList.getPropertyValueList()))
    print 'slaveList:  {}'.format(map(id, slaveList .getPropertyValueList()))

    print 'propValMap:\n{}'.format('\n'.join(['{} - {}'.format(k, v)
                                              for k, v in propValMap]))

    def getSlavePropVal(masterPropVal):
        for i in range(len(propValMap)):
            mpvid = propValMap[i][masterIdx]
            spvid = propValMap[i][slaveIdx]
            if mpvid == id(masterPropVal):
                return spvid
        return None
    
    def addPropValMapping(masterPropVal, slavePropVal):
        pvmap = [0, 0]
        pvmap[masterIdx] = masterPropVal
        pvmap[slaveIdx]  = slavePropVal
        propValMap.append(tuple(pvmap))
    
    def delPropValMapping(masterPropVal, slavePropVal):
        pvmap = [0, 0]
        pvmap[masterIdx] = masterPropVal
        pvmap[slaveIdx]  = slavePropVal
        propValMap.remove(tuple(pvmap))
    
    def getMasterPropVal(slavePropVal):
        for i in range(len(propValMap)):
            mpvid = propValMap[i][masterIdx]
            spvid = propValMap[i][slaveIdx] 
            if spvid == id(slavePropVal):
                return mpvid
        return None 

    slaveListChanged = False
    slaveList.disableNotification()
    
    # list addition
    if len(masterList) > len(slaveList):

        print 'addition'
        
        for i, mpv in enumerate(masterList.getPropertyValueList()):

            spvid = getSlavePropVal(mpv)

            # we've found a value in the master
            # list which is not in the slave list
            if spvid is None:
                slaveListChanged = True
                slaveList.insert(i, mpv.get())
                spv = slaveList.getPropertyValueList()[i]
                
                addPropValMapping(id(mpv), id(spv))

                # Bind the two new PV objects
                _bindPropVals(self,
                              other,
                              myList,
                              otherList,
                              myProp.getLabel(self),
                              otherProp.getLabel(other),
                              val=False)                 

    # list deletion
    elif len(masterList) < len(slaveList):

        print 'deletion'
        
        mpvIds = map(id, masterList.getPropertyValueList())
        
        for i, spv in reversed(
                list(enumerate(slaveList.getPropertyValueList()))):

            mpvid = getMasterPropVal(spv)

            print 'Checking {} - {} ...'.format(id(spv), mpvid)

            # If this happens, there's
            # a bug in somebody's code.
            if mpvid is None:
                raise RuntimeError('Lists are out of sync')

            # we've found a value in
            # the slave list which is no
            # longer in the master list 
            if mpvid not in mpvIds:
                print '  This is the deleted one'
                slaveListChanged = True
                del slaveList[ i]
                delPropValMapping(mpvid, id(spv))
                
    # list re-order (or individual value
    # change, which we don't care about)
    else:
        
        mpvIds   = map(id, masterList.getPropertyValueList())
        newOrder = []
        for i, spv in enumerate(slaveList.getPropertyValueList()):

            mpvid = getMasterPropVal(spv)
            newOrder.append(mpvIds.index(mpvid))

        if newOrder != range(len(slaveList)):
            print 'reorder'
            slaveListChanged = True
            slaveList.reorder(newOrder)
        else:
            print 'No change to list structure - have been a value change'

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
