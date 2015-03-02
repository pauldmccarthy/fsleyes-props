
props.build_parts module
************************

Parts for building a GUI.

This module provides definitiions of the parts used by the `build
<Props.Build#module-props.build>`_ module to build a GUI from a
``HasProperties`` object.

**class props.build_parts.ViewItem(key=None, label=None, tooltip=None,
visibleWhen=None, enabledWhen=None, setup=None)**

   Bases: ``object``

   Superclass for ``Widget``, ``Button``, ``Label`` and ``Group``.
   Represents an item to be displayed.

   Define a ``ViewItem``.

   :Parameters:
      * **key** (*str*) -- An identifier for this item. If this item
        is a ``Widget``, this should be the property name that the
        widget edits. This key is used to look up labels and tooltips,
        if they are passed in as dicts (see ``buildGUI()``).

      * **label** (*str*) -- A label for this item, which may be used
        in the GUI.

      * **tooltip** (*str*) -- A tooltip, which may be displayed when
        the user hovers the mouse over the widget for this
        ``ViewItem``.

      * **visibleWhen** -- A function which takes one argument, the
        `HasProperties
        <Props.Properties#props.properties.HasProperties>`_ instance,
        and returns a ``bool``. When any property values change, the
        function is called. The return value is used to determine
        whether this item should be made visible or invisible.

      * **enabledWhen** -- Same as the ``visibleWhen`` parameter,
        except the state of the item (and its children) is changed
        between enabled and disabled.

      * **setup** -- Optional function which is called when te GUI
        object represented by this ViewItem is first  created. The
        function is passed the `HasProperties
        <Props.Properties#props.properties.HasProperties>`_ instance,
        the ``wx`` GUI parent object, and the ``wx`` object.

**class props.build_parts.Button(key=None, text=None, callback=None,
**kwargs)**

   Bases: ``props.build_parts.ViewItem``

   Represents a button which, when clicked, will call a specified
   callback function.

   When the button is clicked, the callback function is passed two
   arguemnts - the `HasProperties
   <Props.Properties#props.properties.HasProperties>`_ instance, and
   the ``wx.Button`` instance.

**class props.build_parts.Label(viewItem=None, **kwargs)**

   Bases: ``props.build_parts.ViewItem``

   Represents a static text label.

   Define a label.

   ``Label`` objects are automatically created for other ``ViewItem``
   objects, which are to be labelled.

**class props.build_parts.LinkBox(viewItem=None, **kwargs)**

   Bases: ``props.build_parts.ViewItem``

   Represents a checkbox which allows the user to control whether a
   property is linked (a.k.a. bound) to the parent of the
   ``HasProperties`` object.

**class props.build_parts.Widget(propName, **kwargs)**

   Bases: ``props.build_parts.ViewItem``

   Represents a widget which is used to modify a property value.

   Define a ``Widget``.

   :Parameters:
      * **propName** (*str*) -- The name of the property which this
        widget can modify.

      * **kwargs** -- Passed to the ``ViewItem`` constructor.

**class props.build_parts.Group(children, showLabels=True,
border=False, **kwargs)**

   Bases: ``props.build_parts.ViewItem``

   Represents a collection of other ``ViewItem`` objects.

   This class is not to be used directly - use one of the subclasses:
      * ``VGroup``

      * ``HGroup``

      * ``NotebookGroup``

   Define a ``Group``.

   Parameters:

   :Parameters:
      * **children** -- List of ``ViewItem`` objects, the children of
        this ``Group``.

      * **showLabels** (*bool*) -- Whether labels should be displayed
        for each of the children. If this is ``True``, an attribute
        will be added to this ``Group`` object in the
        ``_prepareView()`` function, called ``childLabels``, which
        contains a ``Label`` object for each child.

      * **border** (*bool*) -- If ``True``, this group will be drawn
        with a  border around it. If this group is a child of another
        ``VGroup``, it will be laid out a bit differently, too.

      * **kwargs** -- Passed to the ``ViewItem`` constructor.

**class props.build_parts.NotebookGroup(children, **kwargs)**

   Bases: ``props.build_parts.Group``

   A ``Group`` representing a GUI Notebook. Children are added as
   notebook pages.

   Define a ``NotebookGroup``.

   :Parameters:
      **children** -- List of ``ViewItem`` objects - a tab in the
      notebook is added for each child.

**class props.build_parts.HGroup(children, wrap=False,
vertLabels=False, **kwargs)**

   Bases: ``props.build_parts.Group``

   A group representing a GUI panel, whose children are laid out
   horizontally.

   Create a ``HGroup``.

   :Parameters:
      * **wrap** -- If ``True`` the children are wrapped, via a
        ``wx.WrapSizer``; if there is not enough horizontal space to
        display all children in a single row, the remaining children
        are displayed on a new row.

      * **vertLabels** -- If ``True`` child labels are displayed above
        the child.

**class props.build_parts.VGroup(children, **kwargs)**

   Bases: ``props.build_parts.Group``

   A group representing a GUI panel, whose children are laid out
   vertically.
