#!/usr/bin/env python
#
# __init__.py - Sets up the props package namespace.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""Python descriptor framework.

Usage::

    >>> import props

    >>> class PropObj(props.HasProperties):
    >>>     myProperty = props.Boolean()

    >>> myPropObj = PropObj()


    # Access the property value as a normal attribute:
    >>> myPropObj.myProperty = True
    >>> myPropObj.myProperty
    >>> True


    # access the props.Boolean instance:
    >>> myPropObj.getProp('myProperty')
    >>> <props.prop.Boolean at 0x1045e2710>


    # access the underlying props.PropertyValue object
    # (there are caveats for List properties):
    >>> myPropObj.getPropVal('myProperty')
    >>> <props.prop.PropertyValue instance at 0x1047ef518>


    # Receive notification of property value changes
    >>> def myPropertyChanged(value, *args):
    >>>     print('New property value: {}'.format(value))

    >>> myPropObj.addListener(
    >>>    'myProperty', 'myListener', myPropertyChanged)

    >>> myPropObj.myProperty = False
    >>> New property value: False


    # Remove a previously added listener
    >>> myPropObj.removeListener('myListener')


Lots of the code in this package is probably very confusing. First of all, you
will need to understand python descriptors.  Descriptors are a way of adding
properties to python objects, and allowing them to be accessed as if they were
just simple attributes of the object, but controlling the way that the
attributes are accessed and assigned.

The following link provides a good overview, and contains the ideas
which form the basis for the implementation in this module:

 -  http://nbviewer.ipython.org/urls/gist.github.com/\
ChrisBeaumont/5758381/raw/descriptor_writeup.ipynb

And if you've got 30 minutes, this video gives a very good
introduction to descriptors:

 - http://pyvideo.org/video/1760/encapsulation-with-descriptors


A :class:`~props.properties.HasProperties` subclass contains a collection of
:class:`~props.properties.PropertyBase` instances as class attributes. When an
instance of the :class:`~props.properties.HasProperties` class is created, a
:class:`~props.properties_value.PropertyValue` object is created for each of
the :class:`~props.properties.PropertyBase` instances (or a
:class:`~props.properties_value.PropertyValueList` for
:class:`~props.properties.ListPropertyBase` instances).


Each of these :class:`~props.properties_value.PropertyValue` instances
encapsulates a single value, of any type (a
:class:`~props.properties_value.PropertyValueList` instance encapsulates
multiple :class:`~props.properties_value.PropertyValue` instances).  Whenever
a variable value changes, the :class:`~props.properties_value.PropertyValue`
instance passes the new value to the
:meth:`~props.properties.PropertyBase.validate` method of its parent
:class:`~props.properties.PropertyBase` instance to determine whether the new
value is valid, and notifies any registered listeners of the change. The
:class:`~props.properties_value.PropertyValue` object may allow its underlying
value to be set to something invalid, but it will tell registered listeners
whether the new value is valid or
invalid. :class:`~props.properties_value.PropertyValue` objects can
alternately be configured to raise a :exc:`ValueError` on an attempt to set
them to an invalid value, but this has some caveats - see the
:class:`~props.properties_value.PropertyValue` documentation. Finally, to make
things more confusing, some :class:`~props.properties.PropertyBase` types will
configure their :class:`~props.properties_value.PropertyValue` objects to
perform implicit casts when the property value is set.


The default validation logic of most :class:`~props.properties.PropertyBase`
objects can be configured via 'constraints'. For example, the
:class:`~props.properties_types.Number` property allows ``minval`` and
``maxval`` constraints to be set.  These may be set via
:class:`~props.properties.PropertyBase` constructors, (i.e. when it is defined
as a class attribute of a :class:`~props.properties.HasProperties`
definition), and may be queried and changed on individual
:class:`~props.properties.HasProperties` instances via the
:class:`~props.properties.HasProperties.getConstraint`/\
:class:`~props.properties.HasProperties.setConstraint` methods, which are
available on both :class:`~props.properties.PropertyBase` and
:class:`~props.properties.HasProperties` objects.


Properties from different :class:`~props.properties.HasProperties` instances
may be bound to each other, so that changes in one are propagated to the other
- see the :mod:`~props.bindable` module.  Building on this is the
:mod:`~props.syncable` module and its
:class:`~props.syncable.SyncableHasProperties` class, which allows a
one-to-many (one parent, multiple children) synchronisation hierarchy to be
maintained, whereby all the properties of a child instance are by default
synchronised to those of the parent, and this synchronisation can be
independently enabled/disabled for each property.


Application code may be notified of property changes by registering a callback
listener on a :class:`~props.properties_value.PropertyValue` object, via the
equivalent methods:

  - :meth:`props.properties.HasProperties.addListener`
  - :meth:`props.properties.PropertyBase.addListener`
  - :meth:`props.properties_value.PropertyValue.addListener`

Such a listener will be notified of changes to the
:class:`~props.properties_value.PropertyValue` object managed by the
:class:`~props.properties.PropertyBase` object, and associated with the
:class:`~props.properties.HasProperties` instance. For
:class:`~props.properties.ListPropertyBase` properties, a listener registered
through one of the above methods will be notified of changes to the entire
list.  Alternately, a listener may be registered with individual items
contained in the list (see
:meth:`~props.properties_value.PropertyValueList.getPropertyValueList`).
"""

import logging
log = logging.getLogger(__name__)

# Allow access to the individual properties
# modules for internal/advanced/dangerous usage.
import properties
import properties_value
import properties_types
import bindable
import syncable
import cli
import build_parts

# The 'public' props API starts here.
from build_parts import (
    ViewItem, 
    Button,
    Label,
    Widget, 
    Group, 
    NotebookGroup,
    HGroup, 
    VGroup)

from properties import (
    PropertyBase,
    HasProperties)

from syncable import (
    SyncableHasProperties)

from properties_types import (
    Boolean,
    Int,
    Real,
    Percentage,
    String,
    FilePath,
    Choice,
    List,
    ColourMap,
    Bounds,
    Point)

from cli import (
    applyArguments,
    addParserArguments,
    generateArguments)

try:
    import widgets
    import widgets_number
    import widgets_bounds
    import widgets_point
    import widgets_list
    import build
 
    from widgets import makeWidget
    
    from build import (
        buildGUI,
        buildDialog)
    
except Exception as e:
    log.warn('GUI property module import failed '
             '- GUI functionality is disabled')
