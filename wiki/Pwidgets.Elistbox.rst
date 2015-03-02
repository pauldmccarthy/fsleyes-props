
pwidgets.elistbox module
************************

An alternative to ``wx.gizmos.EditableListBox``.

An ``EditableListBox`` implementation. The
``wx.gizmos.EditableListBox`` is buggy under OS X Mavericks, and
getting tooltips working with the ``wx.ListBox`` is an absolute pain
in the behind. So I felt the need to replicate its functionality. This
implementation supports single selection only.

``pwidgets.elistbox.EVT_ELB_SELECT_EVENT = <wx._core.PyEventBinder
object at 0x108c5d050>``

   Identifier for the ``ListSelectEvent`` event.

``pwidgets.elistbox.EVT_ELB_ADD_EVENT = <wx._core.PyEventBinder object
at 0x108c5d110>``

   Identifier for the ``ListAddEvent`` event.

``pwidgets.elistbox.EVT_ELB_REMOVE_EVENT = <wx._core.PyEventBinder
object at 0x108c5d1d0>``

   Identifier for the ``ListRemoveEvent`` event.

``pwidgets.elistbox.EVT_ELB_MOVE_EVENT = <wx._core.PyEventBinder
object at 0x108c5d290>``

   Identifier for the ``ListMoveEvent`` event.

``pwidgets.elistbox.EVT_ELB_EDIT_EVENT = <wx._core.PyEventBinder
object at 0x108c5d350>``

   Identifier for the ``ListEditEvent`` event.

``pwidgets.elistbox.ListSelectEvent``

   Event emitted when an item is selected. A ``ListSelectEvent`` has
   the following attributes (all are set to ``None`` if no item was
   selected):

   * ``idx``:   Index of selected item

   * ``label``: Label of selected item

   * ``data``:  Client data associated with selected item

   alias of ``_Event``

``pwidgets.elistbox.ListAddEvent``

   Event emitted when the 'add item' button is pushed. It is up to a
   listener of this event to actually add a new item to the list. A
   ``ListAddEvent`` has the following attributes (all are set to
   ``None`` if no item was selected):

   * ``idx``:   Index of selected item

   * ``label``: Label of selected item

   * ``data``:  Client data associated with selected item

   alias of ``_Event``

``pwidgets.elistbox.ListRemoveEvent``

   Event emitted when the 'remove item' button is pushed. A
   ``ListRemoveEvent`` has the following attributes:

   * ``idx``:   Index of removed item

   * ``label``: Label of removed item

   * ``data``:  Client data associated with removed item

   alias of ``_Event``

``pwidgets.elistbox.ListMoveEvent``

   Event emitted when one of the 'move up'/'move down' buttons is
   pushed. A ``ListMoveEvent`` has the following attributes:

   * ``oldIdx``: Index of item before move

   * ``newIdx``: Index of item after move

   * ``label``:  Label of moved item

   * ``data``:   Client data associated with moved item

   alias of ``_Event``

``pwidgets.elistbox.ListEditEvent``

   Event emitted when a list item is edited by the user (see the
   ``ELB_EDITABLE`` style). A ``ListEditEvent`` has the following
   attributes:

   ..

      * ``idx``:   Index of edited item

      * ``label``: New label of edited item

      * ``data``:  Client data associated with edited item.

   alias of ``_Event``

``pwidgets.elistbox.ELB_NO_SCROLL = 1``

   Style flag - if enabled, there will be no scrollbar.

``pwidgets.elistbox.ELB_NO_ADD = 2``

   Style flag - if enabled, there will be no 'add item' button.

``pwidgets.elistbox.ELB_NO_REMOVE = 4``

   Style flag - if enabled, there will be no 'remove item' button.

``pwidgets.elistbox.ELB_NO_MOVE = 8``

   Style flag - if enabled there will be no 'move item up' or 'move
   item down' buttons.

``pwidgets.elistbox.ELB_REVERSE = 16``

   Style flag - if enabled, the first item in the list (index 0) will
   be shown at the botom, and the last item at the top.

``pwidgets.elistbox.ELB_TOOLTIP = 32``

   Style flag - if enabled, list items will be replaced with a tooltip
   on mouse-over.

``pwidgets.elistbox.ELB_EDITABLE = 64``

   Style flag - if enabled, double clicking a list item will allow the
   user to edit the item value.

**class pwidgets.elistbox._ListItem(label, data, tooltip, labelWidget,
container, defaultFGColour, selectedFGColour, defaultBGColour,
selectedBGColour, extraWidget=None)**

   Bases: ``object``

   Internal class used to represent items in the list.

   Create a _ListItem object.

   :Parameters:
      * **label** (*str*) -- The item label which will be displayed.

      * **data** -- User data associated with the item.

      * **tooltip** (*str*) -- A tooltip to be displayed when the
        mouse is moved over the item.

      * **labelWidget** -- The ``wx`` object which represents the
        list item.

      * **container** -- The ``wx`` object used as a container for
        the ``widget``.

      * **defaultFGColour** -- Foreground colour to use when the item
        is not selected.

      * **selectedFGColour** -- Foreground colour to use when the item
        is selected.

      * **defaultBGColour** -- Background colour to use when the item
        is not selected.

      * **selectedBGColour** -- Background colour to use when the item
        is selected.

      * **extraWidget** -- A user-settable widget to be displayed
        alongside this item.

**class pwidgets.elistbox.EditableListBox(parent, labels=None,
clientData=None, tooltips=None, style=0)**

   Bases: ``wx._windows.Panel``

   An alternative to ``wx.gizmos.EditableListBox``.

   An ``EditableListBox`` contains a ``wx.Panel`` which in turn
   contains a collection of ``wx.StaticText`` widgets, which are laid
   out vertically, and display labels for each of the items in the
   list. Some rudimentary wrapper methods for modifying the list
   contents are provided by an ``EditableListBox`` object, with an
   interface similar to that of the ``wx.ListBox`` class.

   Create an ``EditableListBox`` object.

   :Parameters:
      * **parent** -- ``wx`` parent object

      * **labels** (*list of strings*) -- List of strings, the items
        in the list

      * **clientData** -- List of data associated with the list items.

      * **tooltips** (*list of strings*) -- List of strings, tooltips
        for each item.

      * **style** (*int*) -- Style bitmask - accepts
        ``ELB_NO_SCROLL``, ``ELB_NO_ADD``, ``ELB_NO_REMOVE``,
        ``ELB_NO_MOVE``, ``ELB_REVERSE``, ``ELB_TOOLTIP``, and
        ``ELB_EDITABLE``.

   ``_selectedFG = '#000000'``

      Default foreground colour for the currently selected item.

   ``_defaultFG = '#000000'``

      Default foreground colour for unselected items.

   ``_selectedBG = '#7777FF'``

      Background colour for the currently selected item.

   ``_defaultBG = '#FFFFFF'``

      Background colour for the unselected items.

   **_onKeyboard(ev)**

      Called when a key is pressed. On up/down arrow key presses,
      changes the selected item, and scrolls if necessary.

   **_onMouseWheel(ev=None, move=None)**

      Called when the mouse wheel is scrolled over the list. Scrolls
      through the list accordingly.

      :Parameters:
         * **ev** -- A ``wx.MouseEvent``

         * **move** -- If called programmatically, a number indicating
           the direction in which to scroll.

   **VisibleItemCount()**

      Returns the number of items in the list which are visible (i.e.
      which have not been hidden via a call to ``ApplyFilter()``).

   **_drawList(ev=None)**

      'Draws' the set of items in the list according to the current
      scrollbar thumb position.

   **_updateScrollbar(ev=None)**

      Updates the scrollbar parameters according to the number of
      items in the list, and the screen size of the list panel. If
      there is enough room to display all items in the list, the
      scroll bar is hidden.

   **_fixIndex(idx)**

      If the ``ELB_REVERSE`` style is active, this method will return
      an inverted version of the given index. Otherwise it returns the
      index value unchanged.

   **GetCount()**

      Returns the number of items in the list.

   **Clear()**

      Removes all items from the list.

   **ClearSelection()**

      Ensures that no items are selected.

   **SetSelection(n)**

      Selects the item at the given index.

   **GetSelection()**

      Returns the index of the selected item, or ``wx.NOT_FOUND`` if
      no item is selected.

   **Insert(label, pos, clientData=None, tooltip=None,
   extraWidget=None)**

      Insert an item into the list.

      :Parameters:
         * **label** (*str*) -- The label to be displayed

         * **pos** (*int*) -- Index at which the item is to be
           inserted

         * **clientData** -- Data associated with the item

         * **tooltip** (*str*) -- Tooltip to be shown, if the
           ``ELB_TOOLTIP`` style is active.

         * **extraWidget** -- A widget to be displayed alongside the
           label.

   **_configTooltip(listItem)**

      If the ``ELB_TOOLTIP`` style was enabled, this method configures
      mouse-over listeners on the widget representing the given list
      item, so the item displays the tool tip on mouse overs.

   **Append(label, clientData=None, tooltip=None, extraWidget=None)**

      Appends an item to the end of the list.

      :Parameters:
         * **label** (*str*) -- The label to be displayed

         * **clientData** -- Data associated with the item

         * **tooltip** (*str*) -- Tooltip to be shown, if the
           ``ELB_TOOLTIP`` style is active.

         * **extraWidget** -- A widget to be displayed alonside the
           item.

   **Delete(n)**

      Removes the item at the given index from the list.

   **IndexOf(clientData)**

      Returns the index of the list item with the specified
      ``clientData``.

   **SetItemWidget(n, widget=None)**

      Sets the widget to be displayed alongside the item at index
      ``n``.

   **GetItemWidget(i)**

      Returns the widget for the item at index ``i``, or ``None``, if
      the widget hasn't been set.

   **SetItemForegroundColour(n, defaultColour=None,
   selectedColour=None)**

      Sets the foreground colour of the item at index ``n``.

   **SetItemBackgroundColour(n, defaultColour=None,
   selectedColour=None)**

      Sets the background colour of the item at index ``n``.

   **SetItemFont(n, font)**

      Sets the font for the item label at index ``n``.

   **GetItemFont(n)**

      Returns the font for the item label at index ``n``.

   **SetString(n, s)**

      Sets the label of the item at index ``n`` to the string ``s``.

      :Parameters:
         * **n** (*int*) -- Index of the item.

         * **s** (*str*) -- New label for the item.

   **ApplyFilter(filterStr=None, ignoreCase=False)**

      Hides any items for which the label does not contain the given
      ``filterStr``. To clear the filter (and hence show all items),
      pass in ``filterStr=None``.

   **_getSelection(fix=False)**

      Returns a 3-tuple containing the (uncorrected) index, label, and
      associated client data of the currently selected list item, or
      (None, None, None) if no item is selected.

   **_itemClicked(ev=None, widget=None)**

      Called when an item in the list is clicked. Selects the item and
      posts an ``EVT_ELB_SELECT_EVENT``.

      This method may be called programmatically, by explicitly
      passing in the target ``widget``.  This functionality is used by
      the ``_onKeyboard()`` event.

      :Parameters:
         * **ev** -- A ``wx.MouseEvent``.

         * **widget** -- The widget on which to simulate a mouse
           click.

   **_moveItem(offset)**

      Called when the 'move up' or 'move down' buttons are pushed.
      Moves the selected item by the specified offset and posts an
      ``EVT_ELB_MOVE_EVENT``, unless it doesn't make sense to do the
      move.

   **_moveItemDown(ev)**

      Called when the 'move down' button is pushed. Calls the
      ``_moveItem()`` method.

   **_moveItemUp(ev)**

      Called when the 'move up' button is pushed. Calls the
      ``_moveItem()`` method.

   **_addItem(ev)**

      Called when the 'add item' button is pushed. Does nothing but
      post an ``EVT_ELB_ADD_EVENT`` - it is up to a registered handler
      to implement the functionality of adding an item to the list.

   **_removeItem(ev)**

      Called when the 'remove item' button is pushed. Removes the
      selected item from the list, and posts an
      ``EVT_ELB_REMOVE_EVENT``.

   **_onEdit(ev, listItem)**

      Called when an item is double clicked. See the ``ELB_EDITABLE``
      style.

      Creates and displays a ``wx.TextCtrl`` allowing the user to edit
      the item label. A ``ListEditEvent`` is posted every time the
      text changes.

   **_updateMoveButtons()**

**pwidgets.elistbox._testEListBox()**

   Little testing application.
