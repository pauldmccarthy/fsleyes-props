#!/usr/bin/env python
#
# properties_value.py - Definitions of the PropertyValue and
#                       PropertyValueList classes.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""Definitions of the :class:`PropertyValue` and :class:`PropertyValueList`
classes.

These definitions are really a part of the :mod:`props.properties` module,
and are intended to be created and managed by
:class:`~props.properties.PropertyBase` objects. However, the
:class:`PropertyValue` class definitions have absolutely no dependencies upon
the :class:`~props.properties.PropertyBase` definitions. The same can't be
said for the other way around though.

"""

import logging
import inspect
import traceback

from collections import OrderedDict

import callqueue

log = logging.getLogger(__name__)

class PropertyValue(object):
    """An object which encapsulates a value of some sort.

    The value may be subjected to validation rules, and listeners may be
    registered for notification of value and validity changes.
    """

    def __init__(self,
                 context,
                 name=None,
                 value=None,
                 castFunc=None,
                 validateFunc=None,
                 equalityFunc=None,
                 preNotifyFunc=None,
                 postNotifyFunc=None,
                 allowInvalid=True,
                 **attributes):
        """Create a :class:`PropertyValue` object.
        
        :param context:        An object which is passed as the first argument
                               to the ``validateFunc``, ``preNotifyFunc``,
                               ``postNotifyFunc``, and any registered
                               listeners. Can be anything, but will nearly
                               always be a
                               :class:`~props.properties.HasProperties`
                               instance.

        :param str name:       Value name - if not provided, a default, unique
                               name is created.

        :param value:          Initial value.

        :param castFunc:       Function which performs type casting or data
                               conversion. Must accept three parameters - the
                               context, a dictionary containing the attributes
                               of this object, and the value to cast. Must
                               return that value, cast appropriately.
        
        :param validateFunc:   Function which accepts three parameters - the
                               context, a dictionary containing the attributes
                               of this object, and a value. This function
                               should test the provided value, and raise a
                               :exc:`ValueError` if it is invalid.

        :param equalityFunc:   Function which accepts two values, and should
                               return ``True`` if they are equal, ``False``
                               otherwise. If not provided, the python equailty
                               operator (i.e. ``==``) is used.

        :param preNotifyFunc:  Function to be called whenever the property
                               value changes, but before any registered
                               listeners are called. Must accept three
                               parameters - the new value, a boolean value
                               which is ``True`` if the new value is valid,
                               ``False`` otherwise, and the context object.
        
        :param postNotifyFunc: Function to be called whenever the property
                               value changes, but after any registered
                               listeners are called. Must accept the same
                               parameters as the ``preNotifyFunc``.
        
        :param allowInvalid:   If ``False``, any attempt to set the value to
                               something invalid will result in a
                               :exc:`ValueError`. Note that this does not
                               guarantee that the property will never have an
                               invalid value, as the definition of 'valid'
                               depends on external factors (i.e. the
                               ``validateFunc``).  Therefore, the validity of
                               a value may change, even if the value itself
                               has not changed.
        
        :param attributes:     Any key-value pairs which are to be associated 
                               with this :class:`PropertyValue` object, and 
                               passed to the ``castFunc`` and ``validateFunc`` 
                               functions. Attributes are not used by the 
                               :class:`PropertyValue` or
                               :class:`PropertyValueList` classes, however
                               they are used by the
                               :class:`~props.properties.ListPropertyBase`
                               and :class:`~props.properties.PropertyBase`
                               classes to store per-instance property
                               constraints. Listeners may register to be
                               notified when attribute values change.
        """
        
        if name     is     None: name  = 'PropertyValue_{}'.format(id(self))
        if castFunc is not None: value = castFunc(context, attributes, value)
        if equalityFunc is None: equalityFunc = lambda a, b: a == b
        
        self._context              = context
        self._validate             = validateFunc
        self._name                 = name
        self._equalityFunc         = equalityFunc
        self._castFunc             = castFunc
        self._preNotifyFunc        = preNotifyFunc
        self._postNotifyFunc       = postNotifyFunc
        self._allowInvalid         = allowInvalid
        self._attributes           = attributes.copy()
        self._changeListeners      = OrderedDict()
        self._changeListenerStates = {}
        self._attributeListeners   = OrderedDict()

        self.__value               = value
        self.__valid               = False
        self.__lastValue           = None
        self.__lastValid           = False
        self.__notification        = True


    def __repr__(self):
        """Returns a string representation of this PropertyValue object."""
        
        return 'PV({})'.format(self.__value)


    def __str__(self):
        """Returns a string representation of this PropertyValue object."""
        return self.__repr__()


    def __eq__(self, other):
        """Returns ``True`` if the given object has the same value as this
        instance. Returns ``False`` otherwise.
        """
        if isinstance(other, PropertyValue):
            other = other.get()
        return self._equalityFunc(self.get(), other)

    
    def __ne__(self, other):
        """Returns ``True`` if the given object has a different value to
        this instance, ``False`` otherwise.
        """ 
        return not self.__eq__(other)
 
        
    def enableNotification(self):
        """Enables notification of property value and attribute listeners for
        this :class:`PropertyValue` object.
        """
        self.__notification = True

        
    def disableNotification(self):
        """Disables notification of property value and attribute listeners for
        this :class:`PropertyValue` object. Notification can be re-enabled via
        the :meth:`enableNotification` method.
        """
        self.__notification = False

        
    def getNotificationState(self):
        """Returns ``True`` if notification is currently enabled, ``False``
        otherwise.
        """
        return self.__notification

        
    def setNotificationState(self, value):
        """Sets the current notification state."""
        if value: self.enableNotification()
        else:     self.disableNotification()


    def _saltListenerName(self, name):
        """Adds a constant string to the given listener name.

        This is done for debug output, so we can better differentiate between
        listeners with the same name registered on different PV objects.

        """
        return 'PropertyValue_{}_{}'.format(self._name, name)
 
        
    def addAttributeListener(self, name, listener):
        """Adds an attribute listener for this :class:`PropertyValue`. The
        listener callback function must accept the following arguments:
        
          - ``context``:   The context associated with this
            :class:`PropertyValue`.
        
          - ``attribute``: The name of the attribute that changed.
        
          - ``value``:     The new attribute value.

        :param str name: A unique name for the listener. If a listener with
                         the specified name already exists, it will be
                         overwritten.
        
        :param listener: The callback function.
        """
        log.debug('Adding attribute listener on {}.{}: {}'.format(
            self._context.__class__.__name__, self._name, name))
        
        name = self._saltListenerName(name)
        self._attributeListeners[name] = listener

        
    def removeAttributeListener(self, name):
        """Removes the attribute listener of the given name."""
        log.debug('Removing attribute listener on {}.{}: {}'.format(
            self._context.__class__.__name__, self._name, name))
        
        name = self._saltListenerName(name)
        self._attributeListeners.pop(name, None)


    def getAttributes(self):
        """Returns a dictionary containing all the attributes of this
        :class:`PropertyValue` object.
        """
        return self._attributes.copy()

        
    def setAttributes(self, atts):
        """Sets all the attributes of this :class:`PropertyValue` object.
        from the given dictionary.
        """

        for name, value in atts.items():
            self.setAttribute(name, value)

        
    def getAttribute(self, name):
        """Returns the value of the named attribute."""
        return self._attributes[name]

        
    def setAttribute(self, name, value):
        """Sets the named attribute to the given value, and notifies any
        registered attribute listeners of the change.
        """
        oldVal = self._attributes.get(name, None)

        if oldVal == value: return

        self._attributes[name] = value

        log.debug('Attribute on {} changed: {} = {}'.format(
            self._name, name, value))

        self.notifyAttributeListeners(name, value)

        self.revalidate()


    def notifyAttributeListeners(self, name, value):
        """Notifies all registered attribute listeners of an attribute change
        (unless notification has been disabled via the
        :meth:`disableNotification` method). This method is separated so that
        it can be called from subclasses (specifically the
        :class:`PropertyValueList`).
        """

        if not self.__notification: return

        attListeners = []
        args         = (self._context, name, value)
        desc         = '{}.{}'.format(self._context.__class__.__name__,
                                      self._name) 
        
        for cbName, cb in self._attributeListeners.items():
            attListeners.append(('{} ({})'.format(cbName, desc), cb, args))

        callqueue.queue.callAll(attListeners)
        
        
    def addListener(self, name, callback, overwrite=False):
        """Adds a listener for this value.

        When the value changes, the listener callback function is called. The
        callback function must accept these arguments:

          - ``value``:   The property value
          - ``valid``:   Whether the value is valid or invalid
          - ``context``: The context object passed to :meth:`__init__`.

        :param str name:  A unique name for this listener. If a listener with
                          the name already exists, a RuntimeError will be
                          raised, or it will be overwritten, depending upon
                          the value of the ``overwrite`` argument.
        :param callback:  The callback function.
        :param overwrite: If ``True`` any previous listener with the same name
                          will be overwritten. 

        """
        log.debug('Adding listener on {}.{}: {}'.format(
            self._context.__class__.__name__,
            self._name,
            name))

        
        fullName = self._saltListenerName(name)
        prior    = self._changeListeners.get(fullName, None)

        if   prior is None: self._changeListeners[fullName] = callback
        elif overwrite:     self._changeListeners[fullName] = callback
        else:               raise RuntimeError('Listener {} already '
                                               'exists'.format(name))

        self._changeListenerStates[fullName] = True


    def removeListener(self, name):
        """Removes the listener with the given name from this
        :class:`PropertyValue`.
        """

        # The typical stack trace of a call to this method is:
        #    someHasPropertiesObject.removeListener(...) (the original call)
        #      HasProperties.removeListener(...)
        #        PropertyBase.removeListener(...)
        #          this method
        # So to be a bit more informative, we'll examine the stack
        # and extract the (assumed) location of the original call
        stack = inspect.stack()

        if len(stack) >= 4: frame = stack[ 3]
        else:               frame = stack[-1]
        
        srcMod  = '...{}'.format(frame[1][-20:])
        srcLine = frame[2]
        
        log.debug('Removing listener on {}.{}: {} ({}:{})'.format(
            self._context.__class__.__name__,
            self._name,
            name,
            srcMod,
            srcLine))

        name = self._saltListenerName(name)
        self._changeListeners     .pop(name, None)
        self._changeListenerStates.pop(name, None)


    def enableListener(self, name):
        """(Re-)Enables the listener with the specified ``name``."""
        name = self._saltListenerName(name)
        self._changeListenerStates[name] = True

    
    def disableListener(self, name):
        """Disables the listener with the specified ``name``, but does not
        remove it from the list of listeners.
        """
        name = self._saltListenerName(name)
        self._changeListenerStates[name] = False


    def hasListener(self, name):
        """Returns ``True`` if a listener with the given name is registered,
        ``False`` otherwise.
        """

        name = self._saltListenerName(name)
        return name in self._changeListeners.keys()


    def setPreNotifyFunction(self, preNotifyFunc):
        """Sets the function to be called on value changes, before any
        registered listeners.
        """
        self._preNotifyFunc = preNotifyFunc

        
    def setPostNotifyFunction(self, postNotifyFunc):
        """Sets the function to be called on value changes, after any
        registered listeners.
        """
        self._postNotifyFunc = postNotifyFunc 

        
    def get(self):
        """Returns the current property value."""
        return self.__value

        
    def set(self, newValue):
        """Sets the property value.

        The property is validated and, if the property value or its validity
        has changed, the ``preNotifyFunc``, any registered listeners, and the
        ``postNotifyFunc`` are called.  If ``allowInvalid`` was set to
        ``False``, and the new value is not valid, a :exc:`ValueError` is
        raised, and listeners are not notified.
        """

        # cast the value if necessary.
        # Allow any errors to be thrown
        if self._castFunc is not None:
            newValue = self._castFunc(self._context,
                                      self._attributes,
                                      newValue)
            
        # Check to see if the new value is valid
        valid    = False
        validStr = None
        try:
            if self._validate is not None:
                self._validate(self._context, self._attributes, newValue)
            valid = True

        except ValueError as e:

            # Oops, we don't allow invalid values.
            validStr = str(e)
            if not self._allowInvalid:
                log.debug('Attempt to set {}.{} to an invalid value ({}), '
                          'but allowInvalid is False ({})'.format(
                              self._context.__class__.__name__,
                              self._name,
                              newValue,
                              e, exc_info=True))
                traceback.print_stack()
                raise e

        self.__value = newValue
        self.__valid = valid

        # If the value or its validity has not
        # changed, listeners are not notified
        changed = (self.__valid != self.__lastValid) or \
                  not self._equalityFunc(self.__value, self.__lastValue)
                  
        if not changed: return

        log.debug('Value {}.{} changed: {} -> {} ({})'.format(
            self._context.__class__.__name__,
            self._name,
            self.__lastValue,
            newValue,
            'valid' if valid else 'invalid - {}'.format(validStr)))
        
        self.__lastValue = self.__value
        self.__lastValid = self.__valid

        # Notify any registered listeners
        self.notify()

        
    def notify(self):
        """Notifies registered listeners.

        Calls the ``preNotify`` function (if it is set), any listeners which
        have been registered with this :class:`PropertyValue` object, and the
        ``postNotify`` function (if it is set). If notification has been
        disabled (via the :meth:`disableNotification` method), this method
        does nothing.
        """

        if not self.__notification: return
        
        value        = self.get()
        valid        = self.__valid
        allListeners = []

        args         = (value, valid, self._context)
        desc         = '{}.{}'.format(self._context.__class__.__name__,
                                      self._name)

        # Call prenotify first
        if self._preNotifyFunc is not None:
            allListeners.append(('PreNotify ({})'.format(desc),
                                 self._preNotifyFunc,
                                 args))

        # registered listeners second
        for name, listener in self._changeListeners.items():
            
            if not self._changeListenerStates[name]:
                continue
            
            allListeners.append(('{} ({})'.format(name, desc),
                                 listener,
                                 args))

        # And postnotify last
        if self._postNotifyFunc is not None:
            allListeners.append(('PostNotify ({})'.format(desc),
                                 self._postNotifyFunc,
                                 args)) 

        callqueue.queue.callAll(allListeners)


    def revalidate(self):
        """Revalidates the current property value, and re-notifies any
        registered listeners if the value validity has changed.
        """
        self.set(self.get())


    def isValid(self):
        """Returns ``True`` if the current property value is valid, ``False``
        otherwise.
        """
        try: self._validate(self._context, self._attributes, self.get())
        except: return False
        return True


class PropertyValueList(PropertyValue):
    """A :class:`PropertyValue` object which stores other
    :class:`PropertyValue` objects in a list.

    When created, separate validation functions may be passed in for
    individual items, and for the list as a whole. Listeners may be registered
    on individual items (accessible via the :meth:`getPropertyValueList`
    method), or on the entire list.

    This code hurts my head, as it's a bit complicated. The ``__value``
    encapsulated by this :class:`PropertyValue` object (a
    :class:`PropertyValueList` is itself a :class:`PropertyValue`) is just the
    list of raw values.  Alongside this, a separate list is maintained, which
    contains :class:`PropertyValue` objects.  Whenever a list-modifying
    operation occurs on this :class:`PropertyValueList` (which also acts a bit
    like a Python list), both lists are updated.

    The values contained in this :class:`PropertyValueList` may be accessed
    through standard Python list operations, including slice-based access and
    assignment, :meth:`append`, :meth:`insert`, :meth:`extend`, :meth:`pop`,
    :meth:`index`, :meth:`count`, :meth:`move`, :meth:`insertAll`,
    :meth:`removeAll`, and :meth:`reorder` (these last few are non-standard).

    The main restriction of this list-like functionality is that value
    assigments via indexing must not change the length of the list. For
    example, this is a valid assignment::

      mylist[2:7] = [3,4,5,6,7]

    Whereas this would result in an :exc:`IndexError`::

      mylist[2:7] = [3,4,5,6]


    When a :class:`PropertyValueList` is accessed as an attribute of a
    :class:`~props.properties.HasProperties` instance (by far the most
    common use-case), there is an important semantic difference between
    an assignment like this::

      myObj.mylist = [1,2,3,4,5]

    and one like this::

      myObj.mylist[:] = [1,2,3,4,5]

    The first approach will result in any existing :class:`PropertyValue`
    objects in the list being discarded, and new ones created for the new list
    values. In contrast, the second approach, in addition to raising a
    :exc:`IndexError` if the existing list length is not ``5``, will not
    result in creation of new :class:`PropertyValue` instances; rather, the
    values of the existing :class:`PropertyValue` objects will be
    updated.

    This is a very important distinction to keep in mind when working with
    list properties and values which may exist for long periods of time and,
    more importantly, for which listeners have been registered with individual
    :class:`PropertyValue` objects contained in the list. If you register
    a listener with a :class:`PropertyValue` item, and then assign values to
    the list using the first assignment approach above, your listener will be
    lost in the ether.

    There are some interesting type-specific subclasses of the
    :class:`PropertyValueList`, which provide additional functionality:

      - The :class:`~props.properties_types.PointValueList`, for
        :class:`~props.properties_types.Point` properties.

      - The :class:`~props.properties_types.BoundsValueList`, for
        :class:`~props.properties_types.Bounds` properties.
    """

    def __init__(self,
                 context,
                 name=None,
                 values=None,
                 itemCastFunc=None,
                 itemEqualityFunc=None,
                 itemValidateFunc=None,
                 listValidateFunc=None,
                 itemAllowInvalid=True,
                 preNotifyFunc=None,
                 postNotifyFunc=None,
                 listAttributes=None,
                 itemAttributes=None):
        """Create a :class:`PropertyValueList`.

        :param context:               See the :class:`PropertyValue`
                                      constructor.
        
        :param str name:              See the :class:`PropertyValue`
                                      constructor.
        
        :param list values:           Initial list values.
        
        :param itemCastFunc:          Function which casts a single
                                      list item. See the :class:`PropertyValue`
                                      constructor.
        
        :param itemValidateFunc:      Function which validates a single
                                      list item. See the :class:`PropertyValue`
                                      constructor.
        
        :param itemEqualityFunc:      Function which tests equality of two
                                      values. See the :class:`PropertyValue`
                                      constructor. 
        
        :param listValidateFunc:      Function which validates the list as a
                                      whole.
        
        :param bool itemAllowInvalid: Whether items are allowed to containg
                                      invalid values.
        
        :param preNotifyFunc:         See the :class:`PropertyValue`
                                      constructor.
        
        :param postNotifyFunc:        See the :class:`PropertyValue`
                                      constructor.
        
        :param dict listAttributes:   Attributes to be associated with this
                                      :class:`PropertyValueList`.
        
        :param dict itemAttributes:   Attributes to be associated with new
                                      :class:`PropertyValue` items added to
                                      the list.
        """
        if name is None: name = 'PropertyValueList_{}'.format(id(self))
        
        if listAttributes is None: listAttributes = {}

        def itemEquals(a, b):
            if isinstance(a, PropertyValue): a = a.get()
            if isinstance(b, PropertyValue): b = b.get()

            if itemEqualityFunc is not None: return itemEqualityFunc(a, b)
            else:                            return a == b

        listValid = None
        if listValidateFunc is not None:
            def listValid(ctx, atts, value):
                value = list(value)
                for i, v in enumerate(value):
                    if isinstance(v, PropertyValue):
                        value[i] = v.get()
                return listValidateFunc(ctx, atts, value)

        # The list as a whole must be allowed to contain
        # invalid values because, if an individual
        # PropertyValue item value changes, there is no
        # nice way to propagate those changes on to other
        # (dependent) items without the list as a whole
        # being validated first, and errors being raised.
        PropertyValue.__init__(
            self,
            context,
            name=name,
            allowInvalid=True,
            equalityFunc=self._listEquality,
            validateFunc=listValid,
            preNotifyFunc=preNotifyFunc,
            postNotifyFunc=postNotifyFunc,
            **listAttributes)

        # These attributes are passed to the PropertyValue
        # constructor whenever a new item is added to the list
        self._itemCastFunc     = itemCastFunc
        self._itemValidateFunc = itemValidateFunc
        self._itemEqualityFunc = itemEquals
        self._itemAllowInvalid = itemAllowInvalid
        self._itemAttributes   = itemAttributes
            
        # The list of PropertyValue objects.
        if values is not None: values = map(self.__newItem, values)
        else:                  values = []

        PropertyValue.set(self, values)


    def __eq__(self, other):
        """Retuns ``True`` if the given object contains the same values as
        this instance, ``False`` otherwise.
        """

        return self._listEquality(self[:], other[:])


    def _listEquality(self, a, b):
        """Uses the item equality function to test whether two lists are
        equal. Returns ``True`` if they are, ``False`` if they're not.
        """
        if len(a) != len(b): return False
        return all([self._itemEqualityFunc(ai, bi) for ai, bi in zip(a, b)])

        
    def getPropertyValueList(self):
        """Return (a copy of) the underlying property value list, allowing
        access to the :class:`PropertyValue` objects which manage each list
        item.
        """
        return list(PropertyValue.get(self))
 
        
    def get(self):
        """Overrides :meth:`PropertyValue.get`. Returns this
        :class:`PropertyValueList` object.
        """
        return self


    def set(self, newValues):
        """Overrides :meth:`PropertyValue.set`.

        Sets the values stored in this :class:`PropertyValueList`.  If the
        ``recreate`` flag is ``True`` (default) all of the
        :class:`PropertyValue` objects managed by this ``PVL`` object are
        discarded, and new ones recreated. This flag is intended for internal
        use only.
        """

        if len(newValues) != len(self):
            raise ValueError('Lengths don\'t match')

        if self._itemCastFunc is not None:
            newValues = map(lambda v: self._itemCastFunc(
                self._context,
                self._itemAttributes,
                v), newValues)

        self[:] = newValues

        
    def __newItem(self, item):
        """Called whenever a new item is added to the list.  Encapsulate the
        given item in a :class:`PropertyValue` object.
        """

        if self._itemAttributes is None: itemAtts = {}
        else:                            itemAtts = self._itemAttributes

        propVal = PropertyValue(
            self._context,
            name='{}_Item'.format(self._name),
            value=item,
            castFunc=self._itemCastFunc,
            allowInvalid=self._itemAllowInvalid,
            postNotifyFunc=self._itemChanged,
            equalityFunc=self._itemEqualityFunc,
            validateFunc=self._itemValidateFunc,
            **itemAtts)

        # Attribute listeners on the list object are
        # notified of changes to item attributes
        def itemAttChanged(ctx, name, value):
            self.notifyAttributeListeners(name, value)

        propVal.addAttributeListener(self._name, itemAttChanged)
        
        return propVal


    def enableNotification(self):
        """Enables notification of list-level listeners. """
        for val in self.getPropertyValueList():
            val.setPostNotifyFunction(self._itemChanged)
        PropertyValue.enableNotification(self)

        
    def disableNotification(self):
        """Disables notification of list-level listeners. Listeners on
        individual :class:`PropertyValue` items will still be notified
        of item changes.
        """
        for val in self.getPropertyValueList():
            val.setPostNotifyFunction(None)
        PropertyValue.disableNotification(self)

    
    def _itemChanged(self, *a):
        """This function is called when any list item value changes. 
        List-level listeners are notified of the change.
        """

        if self.getNotificationState():
            log.debug('List item {}.{} changed ({}) - nofiying '
                      'list-level listeners ({})'.format(
                          self._context.__class__.__name__,
                          self._name,
                          a[0],
                          self[:]))
            self.notify()
    
    
    def __getitem__(self, key):
        vals = [pv.get() for pv in PropertyValue.get(self)]
        return vals.__getitem__(key)

    def __len__(     self):        return self[:].__len__()
    def __repr__(    self):        return self[:].__repr__()
    def __str__(     self):        return self[:].__str__()
    def __iter__(    self):        return self[:].__iter__()
    def __contains__(self, item):  return self[:].__contains__(item)
    def index(       self, item):  return self[:].index(item)
    def count(       self, item):  return self[:].count(item)

    
    def insert(self, index, item):
        """Inserts the given item before the given index. """
        
        propVals = self.getPropertyValueList()
        propVals.insert(index, self.__newItem(item)) 
        PropertyValue.set(self, propVals)

        
    def insertAll(self, index, items):
        """Inserts all of the given items before the given index."""

        propVals = self.getPropertyValueList()
        propVals[index:index] = map(self.__newItem, items) 
        PropertyValue.set(self, propVals)

        
    def append(self, item):
        """Appends the given item to the end of the list."""

        propVals = self.getPropertyValueList()
        propVals.append(self.__newItem(item))
        PropertyValue.get(self, propVals)


    def extend(self, iterable):
        """Appends all items in the given iterable to the end of the list."""

        propVals = self.getPropertyValueList()
        propVals.extend(map(self.__newItem, iterable))
        PropertyValue.set(self, propVals)

        
    def pop(self, index=-1):
        """Remove and return the specified value in the list (default:
        last).
        """

        propVals      = self.getPropertyValueList()
        poppedPropVal = propVals.pop(index)
        PropertyValue.set(self, propVals)
        return poppedPropVal.get()


    def move(self, from_, to):
        """Move the item from 'from\_' to 'to'."""

        propVals = self.getPropertyValueList()
        propVals.insert(to, propVals.pop(from_))
        PropertyValue.set(self, propVals)

    
    def remove(self, value):
        """Remove the first item in the list with the specified value. """

        # delegates to __delitem__, defined below
        del self[self.index(value)]

        
    def removeAll(self, values):
        """Removes the first occurrence in the list of all of the specified
        values.
        """
        
        propVals = self.getPropertyValueList()
        listVals = [pv.get() for pv in propVals]
        
        for v in values:
            propVals.pop(listVals.index(v))
            
        PropertyValue.set(self, propVals)

        
    def reorder(self, idxs):
        """Reorders the list according to the given sequence of indices."""

        if sorted(idxs) != range(len(self)):
            raise ValueError('Indices ({}) must '
                             'cover the list range '
                             '([0..{}])'.format(idxs, len(self) - 1))

        if idxs == range(len(self)):
            return

        propVals = self.getPropertyValueList()
        propVals = [propVals[i] for i in idxs]
        
        PropertyValue.set(self, propVals)


    def __setitem__(self, key, values):
        """Sets the value(s) of the list at the specified index/slice."""

        if isinstance(key, slice):
            indices = range(*key.indices(len(self)))
            if len(indices) != len(values):
                raise IndexError(
                    'PropertyValueList does not support complex slices')

        elif isinstance(key, int):
            indices = [key]
            values  = [values]
        else:
            raise IndexError('Invalid key type')

        # prepare the new values
        propVals    = self.getPropertyValueList()
        oldVals     = [pv.get() for pv in propVals]
        changedVals = [False] * len(self)

        # Update the PV instances that
        # correspond to the new values,
        # but suppress notification on them
        for idx, val in zip(indices, values):

            propVal    = propVals[idx]
            notifState = propVal.getNotificationState()

            propVal.disableNotification()
            propVal.set(val)
            propVal.setNotificationState(notifState)
            
            changedVals[idx] = not self._itemEqualityFunc(
                propVal.get(), oldVals[idx])

        # Notify list-level and item-level listeners
        # if any values in the list were changed
        if any(changedVals):
            
            log.debug('Notifying list-level listeners ({}.{} {})'.format(
                self._context.__class__.__name__,
                self._name,
                id(self._context))) 
            self.notify()

            log.debug('Notifying item-level listeners ({}.{} {})'.format(
                self._context.__class__.__name__,
                self._name,
                id(self._context)))
        
            for idx in indices:
                if changedVals[idx]:

                    # Make sure that the self._itemChanged
                    # method (which is set as the postNotify
                    # function for all PV items) is not
                    # called, otherwise there will be some
                    # nasty recursiveness
                    propVals[idx].setPostNotifyFunction(None)
                    propVals[idx].notify()
                    propVals[idx].setPostNotifyFunction(self._itemChanged)

        
    def __delitem__(self, key):
        """Remove items at the specified index/slice from the list."""
        
        propVals = PropertyValue.get(self)
        propVals.__delitem__(key)
        PropertyValue.set(self, propVals)
