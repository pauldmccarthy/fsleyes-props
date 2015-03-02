
pwidgets.numberdialog module
****************************

An alternative to ``wx.NumberEntryDialog`` which supports floating
point numbers.

**class pwidgets.numberdialog.NumberDialog(parent, real=True,
title=None, message=None, initial=None, minValue=None,
maxValue=None)**

   Bases: ``wx._windows.Dialog``

   A ``wx.Dialog`` which prompts the user for a number.

   A dialog which contains a ``wx.TextCtrl``, and Ok/Cancel buttons,
   allowing the user to specify a number. If the user pushes the Ok
   button, the number they entered will be accessible via the
   ``GetValue()`` method.

   I've specifically not used the ``wx.SpinCtrl`` or
   ``wx.SpinCtrlDouble``, because they are too limited in their
   flexibility with regard to validation and events.

   Create and lay out a ``NumberDialog``.

   :Parameters:
      * **parent** -- The ``wx`` parent object.

      * **real** (*bool*) -- If ``True``, a floating point number will
        be accepted. Otherwise, only integers are accepted.

      * **title** (*str*) -- Dialog title.

      * **message** (*str*) -- If not None, a ``wx.StaticText`` label
        is added, containing the message.

      * **initial** (*number*) -- Initial value.

      * **minValue** (*number*) -- Minimum value.

      * **maxValue** (*number*) -- Maximum value.

   **GetValue()**

      Return the value that the user entered.

      After a valid value has been entered, and OK button pushed (or
      enter pressed), this method may be used to retrieve the value.
      Returns ``None`` in all other situations.

   **_validate()**

      Validates the current value.

      If the value is valid, returns it.  Otherwise a ``ValueError``
      is raised with an appropriate message.

   **_onOk(ev)**

      Called when the Ok button is pushed, or enter is pressed.

      If the entered value is valid, it is stored and the dialog is
      closed. The value may be retrieved via the ``GetValue()``
      method. If the value is not valid, the dialog remains open.

   **_onCancel(ev)**

      Called when the Cancel button is pushed. Closes the dialog.

**pwidgets.numberdialog._testNumberDialog()**

   Little test program.
