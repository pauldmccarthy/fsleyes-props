
props.widgets_list module
*************************

A widget for editing a `List
<Props.Properties_Types#props.properties_types.List>`_ property.

This module is not intended to be used directly - it is imported into
the `props.widgets <Props.Widgets#module-props.widgets>`_ namespace.

**props.widgets_list._pasteDataDialog(parent, hasProps, propObj)**

   Displays a dialog containing an editable text field, allowing the
   user to type/paste bulk data which will be used to populate the
   list (one line per item).

   :Parameters:
      * **parent** -- parent GUI object

      * **hasProps** -- The ``HasProperties`` object which owns the
        ``propObj``.

      * **propObj** -- The `List
        <Props.Properties_Types#props.properties_types.List>`_
        property object.

**props.widgets_list._editListDialog(parent, hasProps, propObj)**

   A dialog which displays a widget for every item in the list, and
   which allows the user to adjust the number of items in the list.

   See the ``_pasteDataDialog()`` for details on the parameters.

**props.widgets_list._listDialogWidget(parent, hasProps, propObj,
propVal)**

   Creates and returns a GUI panel containing two buttons which, when
   pushed, display dialogs allowing the user to edit the values
   contained in the list.

   See the ``_pasteDataDialog()`` and ``_editListDialog()`` functions.

**props.widgets_list._listEmbedWidget(parent, hasProps, propObj,
propVal)**

**props.widgets_list._List(parent, hasProps, propObj, propVal)**
