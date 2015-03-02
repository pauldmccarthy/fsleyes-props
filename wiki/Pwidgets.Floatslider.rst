
pwidgets.floatslider module
***************************

Floating point slider widgets.

Provides two classes, ``FloatSlider`` and ``SliderSpinPanel``.

The ``FloatSlider`` class is an alternative to ``wx.Slider`` which
supports floating point numbers.

The ``SliderSpinPanel`` class is a panel containing a ``FloatSlider``
and a ``wx.SpinCtrlDouble``, linked such that changes in one are
reflected in the other. The ``SliderSpinPanel`` class also allows the
user to change the slider limits, via the `NumberDialog
<Pwidgets.Numberdialog#pwidgets.numberdialog.NumberDialog>`_ class.

**class pwidgets.floatslider.FloatSlider(parent, value=None,
minValue=None, maxValue=None, **kwargs)**

   Bases: ``wx._controls.Slider``

   Floating point slider widget.

   A cheap and nasty subclass of ``wx.Slider`` which supports floating
   point numbers of any range. The desired range is transformed into
   the internal range [-2^{31}, 2^{31-1}].

   Initialise a FloatSlider.

   :Parameters:
      * **parent** -- The ``wx`` parent object.

      * **value** (*float*) -- Initial slider value.

      * **minValue** (*float*) -- Minimum slider value.

      * **maxValue** (*float*) -- Maximum slider value.

      * **kwargs** -- Passed through to the ``wx.Slider`` constructor.

   **GetRange()**

      Return a tuple containing the (minimum, maximum) slider values.

   **SetRange(minValue, maxValue)**

      Set the minimum/maximum slider values.

   **GetMin()**

      Return the minimum slider value.

   **GetMax()**

      Return the maximum slider value.

   **SetMin(minValue)**

      Set the minimum slider value.

   **SetMax(maxValue)**

      Set the maximum slider value.

   **SetValue(value)**

      Set the slider value.

   **GetValue()**

      Returns the slider value.

   **_FloatSlider__SetRange(minValue, maxValue)**

      Set the minimum/maximum slider values.

      This logic is not in the public ``SetRange()`` method so we can
      overcome a chicken-and-egg problem in ``__init__()`` -
      ``SetValue()`` needs ``__realMin`` and ``__realMax`` to be set,
      but ``SetRange()`` needs to retrieve the value before setting
      ``__realMin`` and ``__realMax``.

   **_FloatSlider__onMouseWheel(ev)**

      Called when the mouse wheel is spun over the slider widget.
      Increases/decreases the slider value accordingly.

   **_FloatSlider__realToSlider(value)**

      Converts the given value from real space to slider space.

   **_FloatSlider__sliderToReal(value)**

      Converts the given value from slider space to real space.

``pwidgets.floatslider.EVT_SSP_VALUE = <wx._core.PyEventBinder object
at 0x108c64ed0>``

   Identifier for the ``SliderSpinValueEvent``.

``pwidgets.floatslider.EVT_SSP_LIMIT = <wx._core.PyEventBinder object
at 0x108c64f90>``

   Identifier for the ``SliderSpinLimitEvent``.

``pwidgets.floatslider.SliderSpinValueEvent``

   Event emitted when the ``SliderSpinPanel`` value changes. Contains
   a single attribute, ``value``, which contains the new value.

   alias of ``_Event``

``pwidgets.floatslider.SliderSpinLimitEvent``

   Event emitted when the ``SliderSpinPanel`` limits change. Contains
   two attributes, ``min`` and ``max``, which contain the new limit
   values.

   alias of ``_Event``

**class pwidgets.floatslider.SliderSpinPanel(parent, real=True,
value=None, minValue=None, maxValue=None, label=None, showLimits=True,
editLimits=False)**

   Bases: ``wx._windows.Panel``

   A panel containing a ``FloatSlider`` and a ``wx.SpinCtrlDouble``.

   The slider and spinbox are linked such that changes to one are
   reflected in the other.  The ``SliderSpinPanel`` class also
   provides the option to have the minimum/maximum limits displayed on
   either side of the slider/spinbox, and to have those limits
   editable via a button push.

   Users of the ``SliderSpinPanel`` may wish to bind listeners to the
   following events:

   ..

      * ``EVT_SSP_VALUE``: Emitted when the slider value changes.

      * ``EVT_SSP_LIMIT``: Emitted when the slider limits change.

   Initialise a ``SliderSpinPanel`` object.

   :Parameters:
      * **parent** -- The ``wx`` parent object.

      * **real** (*bool*) -- If ``False``, a ``wx.Slider`` and
        ``wx.SpinCtrl`` are used, instead of a ``FloatSlider`` and
        ``wx.SpinCtrlDouble``.

      * **value** (*number*) -- Initial slider/spin value.

      * **minValue** (*number*) -- Minimum slider/spin value.

      * **maxValue** (*number*) -- Maximum slider/spin value.

      * **label** (*str*) -- If not ``None``, a ``wx.StaticText``
        widget is added to the left of the slider, containing the
        given label.

      * **showLimits** (*bool*) -- If ``True``, buttons placed on the
        left and right, displaying the minimum/maximum limits.

      * **editLimits** (*bool*) -- If ``True``, when said buttons are
        clicked, a ``NumberDialog`` window pops up allowing the user
        to edit the limit values. Has no effect if ``showLimits`` is
        ``False``.

   **_onLimitButton(ev)**

      Called when either of the minimum/maximum limit buttons are
      clicked. Pops up a ``NumberDialog`` window and, if the user
      changes the value, updates the slider/spin limits, and emits an
      ``EVT_SSP_LIMIT`` event.

   **_onSlider(ev)**

      Called when the user changes the slider value. Updates the
      spinbox value and emits an ``EVT_SSP_VALUE`` event.

   **_onSpin(ev)**

      Called when the user changes the spinbox value. Updates the
      slider value and emits an ``EVT_SSP_VALUE`` event.

   **_onMouseWheel(ev)**

      Called when the mouse wheel is rotated on the spinbox.
      Increases/decreases the current value accordingly.

   **GetRange()**

      Return a tuple containing the (minimum, maximum) slider/spinbox
      values.

   **GetMin()**

      Returns the minimum slider/spinbox value.

   **GetMax()**

      Returns the maximum slider/spinbox value.

   **GetValue()**

      Returns the current slider/spinbox value.

   **SetRange(minValue, maxValue)**

      Sets the minimum/maximum slider/spinbox values.

   **SetMin(minValue)**

      Sets the minimum slider/spinbox value.

   **SetMax(maxValue)**

      Sets the maximum slider/spinbox value.

   **SetValue(value)**

      Sets the current slider/spinbox value.
