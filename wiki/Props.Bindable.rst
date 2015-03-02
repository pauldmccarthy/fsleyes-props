
props.bindable module
*********************

The ``bindable`` module adds functionality to the `HasProperties
<Props.Properties#props.properties.HasProperties>`_ class to allow
properties from different instances to be bound to each other.

The logic defined in this module is separated purely to keep the
`props.properties <Props.Properties#module-props.properties>`_ and
`props.properties_value
<Props.Properties_Value#module-props.properties_value>`_ module file
sizes down.

The ``bindProps()``, ``unbindProps()``, and ``isBound()`` functions
defined in this module are added (monkey-patched) as methods of the
`HasProperties <Props.Properties#props.properties.HasProperties>`_
class.

The ``notify()`` and ``notifyAttributeListeners()`` functions replace
the `PropertyValue
<Props.Properties_Value#props.properties_value.PropertyValue>`_
methods of the same names.

**class props.bindable.Bidict**

   Bases: ``object``

   A bare-bones bi-directional dictionary, used for binding
   `PropertyValueList
   <Props.Properties_Value#props.properties_value.PropertyValueList>`_
   instances - see the ``_bindListProps()`` and
   ``_boundsListChanged()`` functions.

   **get(key, default=None)**

**props.bindable.bindProps(self, propName, other, otherPropName=None,
unbind=False)**

   Binds the properties specified by ``propName``  and
   ``otherPropName`` such that changes to one are applied to the
   other.

   :Parameters:
      * **propName** (*str*) -- The name of a property on this
        ``HasProperties`` instance.

      * **other** (*HasProperties*) -- Another ``HasProperties``
        instance.

      * **otherPropName** (*str*) -- The name of a property on
        ``other`` to bind to. If ``None`` it is assumed that there is
        a property on ``other`` called ``propName``.

      * **unbind** -- If ``True``, the properties are unbound. See the
        ``unbindProps()`` method.

**props.bindable.unbindProps(self, propName, other,
otherPropName=None)**

   Unbinds two properties previously bound via a call to
   ``bindProps()``.

**props.bindable.isBound(self, propName, other, otherPropName=None)**

   Returns ``True`` if the specified property is bound to the other
   ``HasProperties`` object, ``False`` otherwise.

**props.bindable._bindProps(self, myProp, other, otherProp,
unbind=False)**

   Binds two `PropertyValue
   <Props.Properties_Value#props.properties_value.PropertyValue>`_
   instances together.

   The ``_bindListProps()`` method is used to bind two
   `PropertyValueList
   <Props.Properties_Value#props.properties_value.PropertyValueList>`_
   instances.

   :Parameters:
      * **myProp** -- The ``PropertyBase`` instance of this
        ``HasProperties`` instance.

      * **other** -- The other ``HasProperties`` instance.

      * **otherProp** -- The ``PropertyBase`` instance of the
        ``other`` ``HasProperties`` instance.

      * **unbind** -- If ``True``, the properties are unbound.

**props.bindable._bindListProps(self, myProp, other, otherProp,
unbind=False)**

   Binds two `PropertyValueList
   <Props.Properties_Value#props.properties_value.PropertyValueList>`_
   instances together.

   :Parameters:
      * **myProp** -- The ``ListPropertyBase`` instance of this
        ``HasProperties`` instance.

      * **other** -- The other ``HasProperties`` instance.

      * **otherProp** -- The ``ListPropertyBase`` instance of the
        ``other`` ``HasProperties`` instance.

      * **unbind** -- If ``True``, the properties are unbound.

**props.bindable._bindPropVals(myPropVal, otherPropVal, val=True,
att=True, unbind=False)**

   Binds two `PropertyValue
   <Props.Properties_Value#props.properties_value.PropertyValue>`_
   instances together such that when the value of one changes, the
   other is changed. Attributes are also bound between the two
   instances.

**props.bindable._syncPropValLists(masterList, slaveList)**

   Called when one of a pair of bound `PropertyValueList
   <Props.Properties_Value#props.properties_value.PropertyValueList>`_
   instances changes.

   Propagates the change on the ``masterList`` (either an addition, a
   removal, or a re-ordering) to the ``slaveList``.

**props.bindable.notify(self)**

   This method replaces `notify()
   <Props.Properties_Value#props.properties_value.PropertyValue.notify>`_.
   It ensures that bound ``ProperyValue`` objects are synchronised to
   have the same value, before any registered listeners are notified.

**props.bindable.notifyAttributeListeners(self, name, value)**

   This method replaces the `notifyAttributeListeners()
   <Props.Properties_Value#props.properties_value.PropertyValue.notifyAttributeListeners>`_
   method. It ensures that the attributes of any bound `PropertyValue
   <Props.Properties_Value#props.properties_value.PropertyValue>`_
   instances are synchronised before any attribute listeners are
   notified.
