
pwidgets.notebook module
************************

Re-implementation of the ``wx.Notebook`` widget.

This ``Notebook`` implementation supports page enabling/disabling, and
page visibility.

I didn't want it to come to this, but both the
``wx.lib.agw.aui.AuiNotebook`` and ``wx.lib.agw.flatnotebook`` are too
difficult to use. The ``AuiNotebook`` requires me to use an
``AuiManager`` for layout, and the ``flatnotebook`` has layout/fitting
issues.

**class pwidgets.notebook.Notebook(parent)**

   Bases: ``wx._windows.Panel``

   A ``wx.Panel`` which provides ``wx.Notebook``-like functionality.
   Manages the display of multiple child windows. A row of buttons
   along the top allows the user to select which child window to
   display.

   Create a ``Notebook`` object.

   :Parameters:
      **parent** -- The ``wx`` parent object.

   **_updateMinSize()**

      Calculate and return the best (minimum) size for the
      ``Notebook`` widget. The returned size is the minimum size of
      the largest page, plus the size of the button panel.

   **FindPage(page)**

      Returns the index of the given page, or ``wx.NOT_FOUND`` if the
      page is not in this notebook.

   **InsertPage(index, page, text)**

      Inserts the given page into the notebook at the specified index.
      A button for the page is also added to the button row, with the
      specified text.

   **AddPage(page, text)**

      Adds the given page (and a corresponding button with the given
      text) to the end of the notebook.

   **RemovePage(index)**

      Removes the page at the specified index, but does not destroy
      it.

   **DeletePage(index)**

      Removes the page at the specified index, and (attempts to)
      destroy it.

   **GetSelection()**

      Returns the index of the currently selected page.

   **SetSelection(index)**

      Sets the displayed page to the one at the specified index.

   **AdvanceSelection(forward=True)**

      Selects the next (or previous, if ``forward`` is ``False``)
      enabled page.

   **EnablePage(index)**

      Enables the page at the specified index.

   **DisablePage(index)**

      Disables the page at the specified index.

   **ShowPage(index)**

      Shows the page at the specified index.

   **HidePage(index)**

      Hides the page at the specified index.
