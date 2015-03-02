
props.build module
******************

Automatically build a ``wx`` GUI for a `HasProperties
<Props.Properties#props.properties.HasProperties>`_ object.

This module provides functionality to automatically build a ``wx`` GUI
containing widgets which allow the user to change the property values
(`PropertyBase <Props.Properties#props.properties.PropertyBase>`_
objects) of a specified `HasProperties
<Props.Properties#props.properties.HasProperties>`_ object.

The sole entry point for this module is the ``buildGUI()`` function,
which accepts as parameters a GUI object to be used as the parent
(e.g. a ``wx.Panel`` object), a `HasProperties
<Props.Properties#props.properties.HasProperties>`_ object, an
optional ``ViewItem`` object, which specifies how the interface is to
be laid out, and two optional dictionaries for passing in labels and
tooltips.

The ``buildDialog()`` function is also provided for convenience. It
simply embeds the result of a call to ``buildGUI()`` in a
``wx.Dialog``, and returns the dialog instance.

A number of classes are defined in the separate `props.build_parts
<Props.Build_Parts#module-props.build_parts>`_ module.  The `ViewItem
<Props.Build_Parts#props.build_parts.ViewItem>`_ class allows the
layout of the generated interface to be customised.  Property widgets
may be grouped together by embedding them within a `HGroup
<Props.Build_Parts#props.build_parts.HGroup>`_ or `VGroup
<Props.Build_Parts#props.build_parts.VGroup>`_ object; they will then
respectively be laid out horizontally or verticaly.  Groups may be
embedded within a `NotebookGroup
<Props.Build_Parts#props.build_parts.NotebookGroup>`_ object, which
will result in an interface containing a tab for each child `Group
<Props.Build_Parts#props.build_parts.Group>`_. The label for, and
behaviour of, the widget for an individual property may be customised
with a `Widget <Props.Build_Parts#props.build_parts.Widget>`_ object.
As an example:

::

   import wx
   import props

   class MyObj(props.HasProperties):
       myint  = props.Int()
       mybool = props.Boolean()

   # A reasonably complex view specification
   view = props.VGroup(
     label='MyObj properties',
     children=(
         props.Widget('mybool',
                      label='MyObj Boolean',
                      tooltip='If this is checked, you can '
                              'edit the MyObj Integer'),
         props.Widget('myint',
                      label='MyObj Integer',
                      enabledWhen=lambda mo: mo.mybool)))

   # A simpler view specification
   view = props.VGroup(('mybool', 'myint'))

   # The simplest view specification - a
   # default one will be generated
   view = None

   myobj = MyObj()

   app   = wx.App()
   frame = wx.Frame(None)

   myObjPanel = props.buildGUI(frame, myobj, view)

You may also pass in widget labels and tooltips to the ``buildGUI()``
function:

::

   labels = {
       'myint':  'MyObj Integer value',
       'mybool': 'MyObj Boolean value'
   }

   tooltips = {
       'myint' : 'MyObj Integer tooltip'
   }

   props.buildGUI(frame, myobj, view=view, labels=labels, tooltips=tooltips)

As an alternative to passing in a view, labels, and tooltips to the
``buildGUI()`` function, they may be specified as class attributes of
the HasProperties object, with respective names ``_view``,
``_labels``, and ``_tooltips``:

::

   class MyObj(props.HasProperties):
       myint  = props.Int()
       mybool = props.Boolean()

       _view = props.HGroup(('myint', 'mybool'))
       _labels = {
           'myint':  'MyObj integer',
           'mybool': 'MyObj boolean'
       }
       _tooltips = {
           'myint':  'MyObj integer tooltip',
           'mybool': 'MyObj boolean tooltip'
       }

   props.buildGUI(frame, myobj)

**class props.build.PropGUI**

   Bases: ``object``

   An internal container class used for convenience. Stores references
   to all ``wx`` objects that are created, and to all conditional
   callbacks (which control visibility/state).

**props.build._configureEnabledWhen(viewItem, guiObj, hasProps)**

   Returns a reference to a callback function for this view item, if
   its ``enabledWhen`` attribute was set.

   :Parameters:
      * **viewItem** -- The ``ViewItem`` object

      * **guiObj** -- The GUI object created from the ``ViewItem``

      * **hasProps** -- The `HasProperties
        <Props.Properties#props.properties.HasProperties>`_ instance

**props.build._configureVisibleWhen(viewItem, guiObj, hasProps)**

   Returns a reference to a callback function for this view item, if
   its visibleWhen attribute was set. See ``_configureEnabledWhen()``.

**props.build._createLinkBox(parent, viewItem, hasProps, propGui)**

   Creates a checkbox which can be used to link/unlink a property from
   its parent property.

**props.build._createLabel(parent, viewItem, hasProps, propGui)**

   Creates a ``wx.StaticText`` object containing a label for the given
   ``ViewItem``.

**props.build._createButton(parent, viewItem, hasProps, propGui)**

   Creates a ``wx.Button`` object for the given ``Button`` object.

**props.build._createWidget(parent, viewItem, hasProps, propGui)**

   Creates a widget for the given ``Widget`` object, using the
   `makeWidget() <Props.Widgets#props.widgets.makeWidget>`_ function
   (see the `props.widgets <Props.Widgets#module-props.widgets>`_
   module for more details).

**props.build._makeGroupBorder(parent, group, ctr, *args, **kwargs)**

   Makes a border for a ``Group``.

   If a the ``border`` attribute of a ``Group`` object has been set to
   ``True``, this function is called. It creates a parent ``wx.Panel``
   with a border and title, then creates and embeds the GUI object
   representing the group (via the *ctr* argument). Returns the parent
   border panel, and the group GUI object. Parameters:

   :Parameters:
      * **parent** -- Parent GUI object

      * **group** -- ``VGroup``, ``HGroup`` or ``NotebookGroup``

      * **ctr** -- Constructor for a ``wx.Window`` object.

      * **args** -- Passed to *ctr*. You don't need to pass in the
        parent.

      * **kwargs** -- Passed to *ctr*.

**props.build._createNotebookGroup(parent, group, hasProps, propGui)**

   Creates a `pwidgets.notebook.Notebook
   <Pwidgets.Notebook#pwidgets.notebook.Notebook>`_ object from the
   given ``NotebookGroup`` object.

   The children of the group object are also created via recursive
   calls to the ``_create()`` function.

**props.build._layoutHGroup(group, parent, children, labels)**

   Lays out the children (and labels, if not ``None``) of the given
   ``HGroup`` object. Parameters:

   :Parameters:
      * **group** -- ``HGroup`` object

      * **parent** -- GUI object which represents the group

      * **children** -- List of GUI objects, the children of the
        group.

      * **labels** -- ``None`` if no labels, otherwise a list of GUI
        Label objects, one for each child.

**props.build._layoutVGroup(group, parent, children, labels)**

   Lays out the children (and labels, if not ``None``) of the given
   ``VGroup`` object. Parameters the same as ``_layoutHGroup()``.

**props.build._createGroup(parent, group, hasProps, propGui)**

   Creates a GUI panel object for the given ``HGroup`` or ``VGroup``.

   Children of the group are recursively created via calls to
   ``_create()``, and laid out via the ``_layoutHGroup`` or
   ``_layoutVGroup`` functions.

**props.build._createHGroup(parent, group, hasProps, propGui)**

   Alias for the ``_createGroup()`` function.

**props.build._createVGroup(parent, group, hasProps, propGui)**

   Alias for the ``_createGroup()`` function.

**props.build._getCreateFunction(viewItemClass)**

   Searches within this module for a function which can parse
   instances of the specified  `ViewItem
   <Props.Build_Parts#props.build_parts.ViewItem>`_ class.

   A match will be found if the given class is one of those defined in
   the `build_parts <Props.Build_Parts#module-props.build_parts>`_
   module, or has one of those classes in its base class hierarchy. In
   other words, application-defined subclasses of any of the
   `build_parts <Props.Build_Parts#module-props.build_parts>`_ classes
   will still be built.

**props.build._create(parent, viewItem, hasProps, propGui)**

   Creates a GUI object for the given ``ViewItem`` object and, if it
   is a group, all of its children.

**props.build._defaultView(hasProps)**

   Creates a default view specification for the given `HasProperties
   <Props.Properties#props.properties.HasProperties>`_ object, with
   all properties laid out vertically. This function is only called if
   a view specification was not provided in the call to the
   ``buildGUI()`` function

**props.build._prepareView(hasProps, viewItem, labels, tooltips,
showUnlink)**

   Recursively steps through the given ``viewItem`` and its children
   (if any).

   If the ``viewItem`` is a string, it is assumed to be a property
   name, and it is turned into a ``Widget`` object. If the
   ``viewItem`` does not have a label/tooltip, and there is a
   label/tooltip for it in the given labels/tooltips dict, then its
   label/tooltip is set.  Returns a reference to the updated/newly
   created ``ViewItem``.

**props.build._prepareEvents(hasProps, propGui)**

   If the ``visibleWhen`` or ``enabledWhen`` conditional attributes
   were set for any ``ViewItem`` objects, a callback function is set
   on all properties. When any property value changes, the
   ``visibleWhen``/``enabledWhen`` callback functions are called.

**props.build.buildGUI(parent, hasProps, view=None, labels=None,
tooltips=None, showUnlink=True)**

   Builds a GUI interface which allows the properties of the given
   `HasProperties <Props.Properties#props.properties.HasProperties>`_
   object to be edited.

   Returns a reference to the top level GUI object (typically a
   ``wx.Frame``, ``wx.Panel`` or `Notebook
   <Pwidgets.Notebook#pwidgets.notebook.Notebook>`_).

   Parameters:

   :Parameters:
      * **parent** -- parent GUI object. If ``None``, the interface is
        embedded within a ``wx.Frame``.

      * **hasProps** -- `HasProperties
        <Props.Properties#props.properties.HasProperties>`_ object

      * **view** -- ``ViewItem`` object, specifying the interface
        layout

      * **labels** -- Dict specifying labels

      * **tooltips** -- Dict specifying tooltips

      * **showUnlink** -- If the given ``hasProps`` object is a
        ``props.SyncableHasProperties`` instance, and it has a parent,
        a 'link/unlink' checkbox will be shown next to any properties
        that can be bound/unbound from the parent object.

**props.build.buildDialog(parent, hasProps, view=None, labels=None,
tooltips=None, showUnlink=True)**

   Convenience method which embeds the result of a call to
   ``buildGUI()`` in a ``wx.Dialog``.

   See the ``buildGUI()`` documentation for details on the paramters.
