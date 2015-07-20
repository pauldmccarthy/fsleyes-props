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
import types
import weakref
import inspect
import traceback

from collections import OrderedDict

import callqueue


log = logging.getLogger(__name__)


class WeakFunctionRef(object):
    """Class which encapsulates a :mod:`weakref` to a function or method.

    This class is used by :class:`PropertyValue` instances to reference
    listeners which have been registered to be notified of property value
    or attribute changes.
    """

    
    def __init__(self, func):
        """Create a new ``WeakFunctionRef`` to encapsulate the given
        function or bound/unbound method.
        """

        # Bound method
        if isinstance(func, types.MethodType) and func.im_self is not None:

            # We can't take a weakref of the method
            # object, so we have to weakref the object
            # and the unbound class function. The
            # function method will search for and
            # return the bound method, though.
            self.obj  = weakref.ref(func.im_self)
            self.func = weakref.ref(func.im_func)

            self.objType  = type(func.im_self).__name__
            self.funcName =      func.im_func .__name__

        # Unbound/class method or function
        else:
 
            self.obj      = None
            self.objType  = None
            self.func     = weakref.ref(func)
            self.funcName = func.__name__


    def __str__(self):
        """Return a string representation of the function."""

        selftype = type(self).__name__
        func     = self.function()

        if self.obj is None:
            s = '{}: {}'   .format(selftype, self.funcName)
        else:
            s = '{}: {}.{}'.format(selftype, self.objType, self.funcName)

        if func is None: return '{} <dead>'.format(s)
        else:            return s

        
    def __repr__(self):
        """Return a string representation of the function."""
        return self.__str__()


    def __findPrivateMethod(self):
        """Finds and returns the bound method associated with the encapsulated
        function.
        """

        obj      = self.obj()
        func     = self.func()
        methName = self.funcName

        # Find all attributes on the object which end with
        # the method name - there will be more than one of
        # these if the object has base classes which have
        # private methods of the same name.
        attNames = dir(obj)
        attNames = filter(lambda n: n.endswith(methName), attNames)

        # Find the attribute with the correct name, which
        # is a method, and has the correct function.
        for name in attNames:

            att = getattr(obj, name)

            if isinstance(att, types.MethodType) and \
               att.im_func is func:
                return att

        return None

    
    def function(self):
        """Return a reference to the encapsulated function or method,
        or ``None`` if the function has been garbage collected.
        """

        # Unbound/class method or function
        if self.obj is None:
            return self.func()

        # The instance owning the method has been destroyed
        if self.obj() is None or self.func() is None:
            return None

        obj = self.obj()

        # Return the bound method object
        try:    return getattr(obj, self.funcName)

        # If the function is a bound private method,
        # its name on the instance will have been
        # mangled, so we need to search for it 
        except: return self.__findPrivateMethod()


class PropertyValue(object):
    """An object which encapsulates a value of some sort.

    The value may be subjected to validation rules, and listeners may be
    registered for notification of value and validity changes.
    """


    queue = callqueue.CallQueue(skipDuplicates=True)
    """A :class:`~props.callqueue.CallQueue` instance shared by all
    :class:`PropertyValue` objects for notifying listeners of value
    and attribute changes.
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
                 parent=None,
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
                               listeners are called. See the
                               :meth:`addListener` method for details of the
                               parameters this function must accept.
        
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

        :param parent:         If this PV instance is a memeber of a 
                               :class:`PropertyValueList` instance, the latter
                               sets itself as the parent of this PV. Whenever
                               the value of this PV changes, the
                               :meth:`PropertyValueList._listPVChanged` method
                               is called.
        
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
        
        self._context              = weakref.ref(context)
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

        if parent is not None: self._parent = weakref.ref(parent)
        else:                  self._parent = None

        if not allowInvalid and validateFunc is not None:
            validateFunc(context, self._attributes, value)

        self._changeListenerStates['prenotify']  = True
        self._changeListenerStates['postnotify'] = True


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


    def __makeQueueCallName(self, cbName):
        """Munges the given listener function name before it gets passed
        to the :class:`CallQueue` for execution.
        """
        
        return '{} ({}.{})'.format(
            cbName,
            self._context().__class__.__name__,
            self._name) 

    
    def allowInvalid(self, allow=None):
        """Query/set the allow invalid state of this value.

        If no arguments are passed, returns the current allow invalid state.
        Otherwise, sets the current allow invalid state. to the given argument.
        """
        if allow is None:
            return self._allowInvalid

        self._allowInvalid = bool(allow)
    
        
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

    
    def _unsaltListenerName(self, name):
        """Removes a constant string from the given listener name,
        which is assumed to have been generated by the
        :meth:`_saltListenerName` method.
        """

        salt = 'PropertyValue_{}_'.format(self._name)
        
        return name[len(salt):]
 
        
    def addAttributeListener(self, name, listener, weak=True):
        """Adds an attribute listener for this :class:`PropertyValue`. The
        listener callback function must accept the following arguments:
        
          - ``context``:   The context associated with this
                           :class:`PropertyValue`.
        
          - ``attribute``: The name of the attribute that changed.
        
          - ``value``:     The new attribute value.

          - ``name``:      The name of this :class:`PropertyValue` instance.

        :param str name: A unique name for the listener. If a listener with
                         the specified name already exists, it will be
                         overwritten.
        
        :param listener: The callback function.

        :param weak:     If ``True`` (the default), a weak reference to the
                         callback function is used.
        """
        log.debug('Adding attribute listener on {}.{} ({}): {}'.format(
            self._context().__class__.__name__, self._name, id(self), name))

        if weak:
            listener = WeakFunctionRef(listener)
        
        name = self._saltListenerName(name)
        self._attributeListeners[name] = listener

        
    def removeAttributeListener(self, name):
        """Removes the attribute listener of the given name."""
        log.debug('Removing attribute listener on {}.{}: {}'.format(
            self._context().__class__.__name__, self._name, name))
        
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

        self._attributes[name] = value

        if oldVal == value: return

        log.debug('Attribute on {}.{} ({}) changed: {} = {}'.format(
            self._context().__class__.__name__,
            self._name,
            id(self),
            name,
            value))

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
        args         = (self._context(), name, value, self._name)
        
        for cbName, cb in list(self._attributeListeners.items()):

            if isinstance(cb, WeakFunctionRef):
                cb = cb.function()

            if cb is None:
                log.debug('Removing dead attribute listener {}'.format(cbName))
                
                self.removeAttributeListener(self._unsaltListenerName(cbName))
                continue
                
            attListeners.append((cb, self.__makeQueueCallName(cbName), args))

        self.queue.callAll(attListeners)
        
        
    def addListener(self, name, callback, overwrite=False, weak=True):
        """Adds a listener for this value.

        When the value changes, the listener callback function is called. The
        callback function must accept the following arguments:

          - ``value``:   The property value
          - ``valid``:   Whether the value is valid or invalid
          - ``context``: The context object passed to :meth:`__init__`.
          - ``name``:    The name of this :class:`PropertyValue` instance.

        Listener names 'prenotify' and 'postnotify' are reserved - if
        either of these are passed in for the listener name, a ``ValueError``
        is raised.

        :param str name:  A unique name for this listener. If a listener with
                          the name already exists, a RuntimeError will be
                          raised, or it will be overwritten, depending upon
                          the value of the ``overwrite`` argument.
        :param callback:  The callback function.
        :param overwrite: If ``True`` any previous listener with the same name
                          will be overwritten.

        :param weak:      If ``True`` (the default), a weak reference to the
                          callback function is retained, meaning that it
                          can be garbage-collected. If passing in a lambda or
                          inner function, you will probably want to set
                          ``weak`` to ``False``, in which case a strong
                          reference will be used.
        """

        if name in ('prenotify', 'postnotify'):
            raise ValueError('Reserved listener name used: {}. '
                             'Use a different name.'.format(name))
        
        log.debug('Adding listener on {}.{}: {}'.format(
            self._context().__class__.__name__,
            self._name,
            name))

        
        fullName = self._saltListenerName(name)
        prior    = self._changeListeners.get(fullName, None)

        if weak:
            callback = WeakFunctionRef(callback)

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
        if log.getEffectiveLevel() == logging.DEBUG:
            stack = inspect.stack()

            if len(stack) >= 4: frame = stack[ 3]
            else:               frame = stack[-1]

            srcMod  = '...{}'.format(frame[1][-20:])
            srcLine = frame[2]

            log.debug('Removing listener on {}.{}: {} ({}:{})'.format(
                self._context().__class__.__name__,
                self._name,
                name,
                srcMod,
                srcLine))

        name = self._saltListenerName(name)
        cb   = self._changeListeners     .pop(name, None)
        self       ._changeListenerStates.pop(name, None)

        if isinstance(cb, WeakFunctionRef):
            cb = cb.function()

        if cb is not None:
            PropertyValue.queue.dequeue(self.__makeQueueCallName(name))


    def enableListener(self, name):
        """(Re-)Enables the listener with the specified ``name``."""
        name = self._saltListenerName(name)
        log.debug('Enabling listener on {}: {}'.format(self._name, name))
        self._changeListenerStates[name] = True

    
    def disableListener(self, name):
        """Disables the listener with the specified ``name``, but does not
        remove it from the list of listeners.
        """
        name = self._saltListenerName(name)
        log.debug('Disabling listener on {}: {}'.format(self._name, name))
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


    def getLast(self):
        """Returns the most recent property value before the current one."""
        return self.__lastValue

        
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
            newValue = self._castFunc(self._context(),
                                      self._attributes,
                                      newValue)
            
        # Check to see if the new value is valid
        valid    = False
        validStr = None
        try:
            if self._validate is not None:
                self._validate(self._context(), self._attributes, newValue)
            valid = True

        except ValueError as e:

            # Oops, we don't allow invalid values.
            validStr = str(e)
            if not self._allowInvalid:
                log.debug('Attempt to set {}.{} to an invalid value ({}), '
                          'but allowInvalid is False ({})'.format(
                              self._context().__class__.__name__,
                              self._name,
                              newValue,
                              e), exc_info=True)
                traceback.print_stack()
                raise e

        self.__lastValue = self.__value
        self.__lastValid = self.__valid
        self.__value     = newValue
        self.__valid     = valid

        # If the value or its validity has not
        # changed, listeners are not notified
        changed = (self.__valid != self.__lastValid) or \
                  not self._equalityFunc(self.__value, self.__lastValue)

        if not changed: return

        log.debug('Value {}.{} changed: {} -> {} ({})'.format(
            self._context().__class__.__name__,
            self._name,
            self.__lastValue,
            self.__value,
            'valid' if valid else 'invalid - {}'.format(validStr)))
        
        # Notify any registered listeners. It is
        # critical that this is the last step in
        # the set() method, due to the way that
        # the bindable module monkey-patches it,
        # adding in extra functionality, to
        # synchronise bound PV objects before any
        # notification occurs.
        self.notify()

        
    def notify(self):
        """Notifies registered listeners.

        Calls the ``preNotify`` function (if it is set), any listeners which
        have been registered with this :class:`PropertyValue` object, and the
        ``postNotify`` function (if it is set). If notification has been
        disabled (via the :meth:`disableNotification` method), this method
        does nothing.
        """

        if not self.__notification:
            return
        
        value        = self.get()
        valid        = self.__valid
        listeners    = []
        allListeners = OrderedDict()
        args         = (value, valid, self._context(), self._name)

        # call prenotify listener first
        if self._preNotifyFunc is not None:
            allListeners['prenotify'] = self._preNotifyFunc

        # registered listeners second
        allListeners.update(self._changeListeners)

        # and postnotify last
        if self._postNotifyFunc is not None:
            allListeners['postnotify'] = self._postNotifyFunc

        # filter out listeners which have been disabled
        for cbName, cb in list(allListeners.items()):
            
            if not self._changeListenerStates[cbName]:
                continue

            # If the listener is a WeakFunctionRef
            # instance, we retrieve the actual function
            if isinstance(cb, WeakFunctionRef):
                cb = cb.function()

            if cb is None:
                log.debug('Removing dead listener {}'.format(cbName))
                
                self.removeListener(self._unsaltListenerName(cbName))
                continue
            
            listeners.append((cb, self.__makeQueueCallName(cbName), args))
        
        self.queue.callAll(listeners)

        # If this PV is a member of a PV list, 
        # tell the list that this PV has
        # changed, so that it can notify its own
        # list-level listeners of the change
        if self._parent is not None and self._parent() is not None:
            self._parent()._listPVChanged(self)


    def revalidate(self):
        """Revalidates the current property value, and re-notifies any
        registered listeners if the value validity has changed.
        """
        self.set(self.get())


    def isValid(self):
        """Returns ``True`` if the current property value is valid, ``False``
        otherwise.
        """
        try: self._validate(self._context(), self._attributes, self.get())
        except: return False
        return True


class PropertyValueList(PropertyValue):
    """A :class:`PropertyValue` object which stores other
    :class:`PropertyValue` objects in a list. Instances of this class are
    managed by a :class:`~props.properties.ListPropertyBase` instance.

    When created, separate validation functions may be passed in for
    individual items, and for the list as a whole. Listeners may be registered
    on individual items (accessible via the :meth:`getPropertyValueList`
    method), or on the entire list.

    The values contained in this :class:`PropertyValueList` may be accessed
    through standard Python list operations, including slice-based access and
    assignment, :meth:`append`, :meth:`insert`, :meth:`extend`, :meth:`pop`,
    :meth:`index`, :meth:`count`, :meth:`move`, :meth:`insertAll`,
    :meth:`removeAll`, and :meth:`reorder` (these last few are non-standard).

    Because the values contained in this list are :class:`PropertyValue`
    instances themselves, some limitations are present on list modifying
    operations::

      class MyObj(props.HasProperties):
        mylist = props.List(default[1, 2, 3])

      myobj = MyObj()

    Simple list-slicing modifications work as expected::

      # the value after this will be [5, 2, 3]
      myobj.mylist[0]  = 5
    
      # the value after this will be [5, 6, 7]
      myobj.mylist[1:] = [6, 7]

    However, modifications which would change the length of the list are not
    supported::

      # This will result in an IndexError
      myobj.mylist[0:2] = [6, 7, 8]

    The exception to this rule concerns modifications which would replace 
    every value in the list::

      # These assignments are equivalent
      myobj.mylist[:] = [1, 2, 3, 4, 5]
      myobj.mylist    = [1, 2, 3, 4, 5]

    Where the simple list modifications described above will change the
    value(s) of the existing ``PropertyValue`` instances in the list,
    modifications which replace the entire list contents will result in
    existing ``PropertyValue`` instances being destroyed, and new ones
    being created. This is a very important point to remember if you have
    registered listeners on individual ``PropertyValue`` items.

    A listener registered on a :class:`PropertyValueList` will be notified
    whenever the list is modified (e.g. additions, removals, reorderings), and
    whenever any individual value in the list changes. Alternately, listeners
    may be registered on the individual :class:`~PropertyValue` items (which
    are accessible through the :meth:`getPropertyValueList` method) to be
    nofitied of changes to those values only.

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

        if other is None:
            return False
        
        if len(self) != len(other): return False
        return all([self._itemEqualityFunc(ai, bi)
                    for ai, bi
                    in zip(self[:], other[:])])

        
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
        length of the ``newValues`` argument does not match the current list
        length,  a ``ValueError`` is raised.
        """

        if self._itemCastFunc is not None:
            newValues = map(lambda v: self._itemCastFunc(
                self._context(),
                self._itemAttributes,
                v), newValues)

        self[:] = newValues

        
    def __newItem(self, item):
        """Called whenever a new item is added to the list.  Encapsulate the
        given item in a :class:`PropertyValue` object.
        """

        if self._itemAttributes is None: itemAtts = {}
        else:                            itemAtts = self._itemAttributes

        if self._context() is None:

            if not hasattr(self, 'babcount'):
                self.babcount = 0
                
            import objgraph
            objgraph.show_backrefs(self, filename='{}_{}.png'.format(
                id(self), self.babcount), too_many=50, max_depth=4)
            self.babcount += 1

        propVal = PropertyValue(
            self._context(),
            name='{}_Item'.format(self._name),
            value=item,
            castFunc=self._itemCastFunc,
            allowInvalid=self._itemAllowInvalid,
            equalityFunc=self._itemEqualityFunc,
            validateFunc=self._itemValidateFunc,
            parent=self,
            **itemAtts)
        
        return propVal


    def enableNotification(self):
        """Enables notification of list-level listeners. """
        PropertyValue.enableNotification(self)

        
    def disableNotification(self):
        """Disables notification of list-level listeners. Listeners on
        individual :class:`PropertyValue` items will still be notified
        of item changes.
        """
        PropertyValue.disableNotification(self)


    def getLast(self):
        """Overrides :meth:`PropertyValue.getLast`. Returns the most
        recent list value.
        """
        return [pv.get() for pv in PropertyValue.getLast(self)]

    
    def _listPVChanged(self, pv):
        """This function is called by list items when their value changes.
        List-level listeners are notified of the change.
        """

        if self.getNotificationState():
            log.debug('List item {}.{} changed ({}) - nofiying '
                      'list-level listeners ({})'.format(
                          self._context().__class__.__name__,
                          self._name,
                          pv,
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
        PropertyValue.set(self, propVals)


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
            if len(indices) != len(self) and \
               len(indices) != len(values):
                raise IndexError(
                    'PropertyValueList does not support complex slices')

        elif isinstance(key, int):
            indices = [key]
            values  = [values]
        else:
            raise IndexError('Invalid key type')

        # Replacement of all items in list
        if len(indices) == len(self) and \
           len(indices) != len(values):
            
            notifState = self.getNotificationState()
            self.disableNotification()
            del self[:]
            self.setNotificationState(notifState)
            self.extend(values)
            return

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
                self._context().__class__.__name__,
                self._name,
                id(self._context()))) 
            self.notify()

            log.debug('Notifying item-level listeners ({}.{} {})'.format(
                self._context().__class__.__name__,
                self._name,
                id(self._context())))
        
            for idx in indices:
                if changedVals[idx]:
                    propVals[idx].notify()

        
    def __delitem__(self, key):
        """Remove items at the specified index/slice from the list."""
        
        propVals = self.getPropertyValueList()
        propVals.__delitem__(key)
        PropertyValue.set(self, propVals)
