
props package
*************


Submodules
==========

* `props.bindable module <Props.Bindable>`_
* `props.syncable module <Props.Syncable>`_
* `props.build module <Props.Build>`_
* `props.build_parts module <Props.Build_Parts>`_
* `props.cli module <Props.Cli>`_
* `props.properties module <Props.Properties>`_
* `props.properties_types module <Props.Properties_Types>`_
* `props.properties_value module <Props.Properties_Value>`_
* `props.widgets module <Props.Widgets>`_
* `props.widgets_bounds module <Props.Widgets_Bounds>`_
* `props.widgets_list module <Props.Widgets_List>`_
* `props.widgets_number module <Props.Widgets_Number>`_
* `props.widgets_point module <Props.Widgets_Point>`_

Module contents
===============

Python descriptor framework.

Usage:

::

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

Lots of the code in this package is probably very confusing. First of
all, you will need to understand python descriptors.  Descriptors are
a way of adding properties to python objects, and allowing them to be
accessed as if they were just simple attributes of the object, but
controlling the way that the attributes are accessed and assigned.

The following link provides a good overview, and contains the ideas
which form the basis for the implementation in this module:

..

   * http://nbviewer.ipython.org/urls/gist.github.com/ChrisBeaumont/5758381/raw/descriptor_writeup.ipynb

And if you've got 30 minutes, this video gives a very good
introduction to descriptors:

..

   * http://pyvideo.org/video/1760/encapsulation-with-descriptors

A `HasProperties <Props.Properties#props.properties.HasProperties>`_
subclass contains a collection of `PropertyBase
<Props.Properties#props.properties.PropertyBase>`_ instances as class
attributes. When an instance of the `HasProperties
<Props.Properties#props.properties.HasProperties>`_ class is created,
a `PropertyValue
<Props.Properties_Value#props.properties_value.PropertyValue>`_ object
is created for each of the `PropertyBase
<Props.Properties#props.properties.PropertyBase>`_ instances (or a
`PropertyValueList
<Props.Properties_Value#props.properties_value.PropertyValueList>`_
for `ListPropertyBase
<Props.Properties#props.properties.ListPropertyBase>`_ instances).

Each of these `PropertyValue
<Props.Properties_Value#props.properties_value.PropertyValue>`_
instances encapsulates a single value, of any type (a
`PropertyValueList
<Props.Properties_Value#props.properties_value.PropertyValueList>`_
instance encapsulates multiple `PropertyValue
<Props.Properties_Value#props.properties_value.PropertyValue>`_
instances).  Whenever a variable value changes, the `PropertyValue
<Props.Properties_Value#props.properties_value.PropertyValue>`_
instance passes the new value to the `validate()
<Props.Properties#props.properties.PropertyBase.validate>`_ method of
its parent `PropertyBase
<Props.Properties#props.properties.PropertyBase>`_ instance to
determine whether the new value is valid, and notifies any registered
listeners of the change. The `PropertyValue
<Props.Properties_Value#props.properties_value.PropertyValue>`_ object
may allow its underlying value to be set to something invalid, but it
will tell registered listeners whether the new value is valid or
invalid. `PropertyValue
<Props.Properties_Value#props.properties_value.PropertyValue>`_
objects can alternately be configured to raise a ``ValueError`` on an
attempt to set them to an invalid value, but this has some caveats -
see the `PropertyValue
<Props.Properties_Value#props.properties_value.PropertyValue>`_
documentation. Finally, to make things more confusing, some
`PropertyBase <Props.Properties#props.properties.PropertyBase>`_ types
will configure their `PropertyValue
<Props.Properties_Value#props.properties_value.PropertyValue>`_
objects to perform implicit casts when the property value is set.

The default validation logic of most `PropertyBase
<Props.Properties#props.properties.PropertyBase>`_ objects can be
configured via 'constraints'. For example, the `Number
<Props.Properties_Types#props.properties_types.Number>`_ property
allows ``minval`` and ``maxval`` constraints to be set.  These may be
set via `PropertyBase
<Props.Properties#props.properties.PropertyBase>`_ constructors, (i.e.
when it is defined as a class attribute of a `HasProperties
<Props.Properties#props.properties.HasProperties>`_ definition), and
may be queried and changed on individual `HasProperties
<Props.Properties#props.properties.HasProperties>`_ instances via the
`getConstraint
<Props.Properties#props.properties.HasProperties.getConstraint>`_/`setConstraint
<Props.Properties#props.properties.HasProperties.setConstraint>`_
methods, which are available on both `PropertyBase
<Props.Properties#props.properties.PropertyBase>`_ and `HasProperties
<Props.Properties#props.properties.HasProperties>`_ objects.

Properties from different `HasProperties
<Props.Properties#props.properties.HasProperties>`_ instances may be
bound to each other, so that changes in one are propagated to the
other - see the `bindable <Props.Bindable#module-props.bindable>`_
module.  Building on this is the `syncable
<Props.Syncable#module-props.syncable>`_ module and its
`SyncableHasProperties
<Props.Syncable#props.syncable.SyncableHasProperties>`_ class, which
allows a one-to-many (one parent, multiple children) synchronisation
hierarchy to be maintained, whereby all the properties of a child
instance are by default synchronised to those of the parent, and this
synchronisation can be independently enabled/disabled for each
property.

Application code may be notified of property changes by registering a
callback listener on a `PropertyValue
<Props.Properties_Value#props.properties_value.PropertyValue>`_
object, via the equivalent methods:

..

   * `props.properties.HasProperties.addListener()
     <Props.Properties#props.properties.HasProperties.addListener>`_

   * `props.properties.PropertyBase.addListener()
     <Props.Properties#props.properties.PropertyBase.addListener>`_

   * `props.properties_value.PropertyValue.addListener()
     <Props.Properties_Value#props.properties_value.PropertyValue.addListener>`_

Such a listener will be notified of changes to the `PropertyValue
<Props.Properties_Value#props.properties_value.PropertyValue>`_ object
managed by the `PropertyBase
<Props.Properties#props.properties.PropertyBase>`_ object, and
associated with the `HasProperties
<Props.Properties#props.properties.HasProperties>`_ instance. For
`ListPropertyBase
<Props.Properties#props.properties.ListPropertyBase>`_ properties, a
listener registered through one of the above methods will be notified
of changes to the entire list.  Alternately, a listener may be
registered with individual items contained in the list (see
`getPropertyValueList()
<Props.Properties_Value#props.properties_value.PropertyValueList.getPropertyValueList>`_).
