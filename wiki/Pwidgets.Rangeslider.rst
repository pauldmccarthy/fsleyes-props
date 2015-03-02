
pwidgets.rangeslider module
***************************

Twin sliders for defining the values of a range.

Provides two classes, ``RangePanel``, and ``RangeSliderSpinPanel``.

The ``RangePanel`` is a widget which contains two sliders or
spinboxes, allowing a range to be set. The slider/spinbox which
controls the low range value must always be less than the slider
which/spinbox controls the high value.

The ``RangeSliderSpinPanel`` is a widget which contains two
``RangePanel`` widgets - one with sliders, and one with spinboxes. All
four control widgets are linked.

``pwidgets.rangeslider.EVT_RANGE = <wx._core.PyEventBinder object at
0x108c69090>``

   Identifier for the ``RangeEvent``.

``pwidgets.rangeslider.EVT_RANGE_LIMIT = <wx._core.PyEventBinder
object at 0x108c69150>``

   Identifier for the ``RangeLimitEvent``.

``pwidgets.rangeslider.RangeEvent``

   Event emitted by ``RangePanel`` and ``RangeSliderSpinPanel``
   objects  when either of their low or high values change. Contains
   two attributes, ``low`` and ``high``, containing the new low/high
   range values.

   alias of ``_Event``

``pwidgets.rangeslider.RangeLimitEvent``

   Event emitted by ``RangeSliderSpinPanel`` objects when the user
   modifies the range limits. Contains two attributes, ``min`` and
   ``max``, containing the new minimum/maximum range limits.

   alias of ``_Event``

**class pwidgets.rangeslider.RangePanel(parent, widgetType, real=True,
minValue=None, maxValue=None, lowValue=None, highValue=None,
lowLabel=None, highLabel=None, minDistance=None)**

   Bases: ``wx._windows.Panel``

   A ``wx.Panel`` containing two widgets (either `FloatSlider
   <Pwidgets.Floatslider#pwidgets.floatslider.FloatSlider>`_, or
   ``wx.SpinCtrlDouble``), representing the 'low' and 'high' values of
   a range, respectively. When the user changes the low slider to a
   value beyond the current high value, the high value is increased
   such that it remains at least a minimum value above the low value.
   The inverse relationship is also enforced.

   Initialise a ``RangePanel`` panel.

   :Parameters:
      * **parent** -- The ``wx`` parent object.

      * **widgetType** (*str*) -- Widget type - either ``slider`` or
        ``spin``.

      * **real** -- If ``False``, ``wx.Slider`` and ``wx.SpinCtrl``
        widgets are used instead of `FloatSlider
        <Pwidgets.Floatslider#pwidgets.floatslider.FloatSlider>`_ and
        ``wx.SpinCtrlDouble``.

      * **minValue** (*number*) -- Minimum range value.

      * **maxValue** (*number*) -- Maximum range value.

      * **lowLabel** (*str*) -- If not ``None``, a ``wx.StaticText``
        widget is placed to the left of the low  widget, containing
        the given label.

      * **highLabel** (*str*) -- If not ``None``, a ``wx.StaticText``
        widget is placed to the left of the high  widget, containing
        the given label.

      * **lowValue** (*number*) -- Initial low range value.

      * **highValue** (*number*) -- Initial high range value.

      * **minDistance** (*number*) -- Minimum distance to be
        maintained between low/high values.

   **_onMouseWheel(ev)**

      Called when the mouse wheel is spun on on of the spin controls.
      Increases/decreases the respective low/high value accordingly.

   **_onLowChange(ev=None)**

      Called when the user changes the low widget.  Attempts to make
      sure that the high widget is at least (low value + min
      distance), then posts a ``RangeEvent``.

   **_onHighChange(ev=None)**

      Called when the user changes the high widget.  Attempts to make
      sure that the low widget is at least (high value - min
      distance), then posts a ``RangeEvent``.

   **GetRange()**

      Returns a tuple containing the current (low, high) range values.

   **SetRange(lowValue, highValue)**

      Sets the current (low, high) range values.

   **GetLow()**

      Returns the current low range value.

   **GetHigh()**

      Returns the current high range value.

   **SetLow(lowValue)**

      Set the current low range value, and attempts to make sure that
      the high value is at least (low value + min distance).

   **SetHigh(highValue)**

      Set the current high range value, and attempts to make sure that
      the high value is at least (low value + min distance).

   **getLimits()**

      Returns a tuple containing the current (minimum, maximum) range
      limit values.

   **SetLimits(minValue, maxValue)**

      Sets the current (minimum, maximum) range limit values.

   **GetMin()**

      Returns the current minimum range value.

   **GetMax()**

      Returns the current maximum range value.

   **SetMin(minValue)**

      Sets the current minimum range value.

   **SetMax(maxValue)**

      Sets the current maximum range value.

**class pwidgets.rangeslider.RangeSliderSpinPanel(parent, real=True,
minValue=None, maxValue=None, lowValue=None, highValue=None,
minDistance=None, lowLabel=None, highLabel=None, showLimits=True,
editLimits=False)**

   Bases: ``wx._windows.Panel``

   A ``wx.Panel`` which contains two sliders and two spinboxes.

   The sliders and spinboxes are contained within two ``RangePanel``
   instances respectively). One slider and spinbox are used to edit
   the 'low' value of a range, and the other slider/spinbox are used
   to edit the 'high' range value. Buttons are optionally displayed on
   either end which display the minimum/maximum limits and, when
   clicked, allow the user to modify said limits.

   Initialise a ``RangeSliderSpinPanel``.

   :Parameters:
      * **parent** -- The ``wx`` parent object.

      * **real** -- If ``False``, ``wx.Slider`` and ``wx.SpinCtrl``
        widgets are used instead of `FloatSlider
        <Pwidgets.Floatslider#pwidgets.floatslider.FloatSlider>`_ and
        ``wx.SpinCtrlDouble``.

      * **minValue** (*number*) -- Minimum low value.

      * **maxValue** (*number*) -- Maximum high value.

      * **lowValue** (*number*) -- Initial low value.

      * **highValue** (*number*) -- Initial high value.

      * **minDistance** (*number*) -- Minimum distance to maintain
        between low and high values.

      * **lowLabel** (*str*) -- If not ``None``, a ``wx.StaticText``
        widget is placed to the left of the low  slider, containing
        the label.

      * **highLabel** (*str*) -- If not ``None``, a ``wx.StaticText``
        widget is placed to the left of the high  slider, containing
        the label.

      * **showLimits** (*bool*) -- If ``True``, a button will be shown
        on either side, displaying the minimum/maximum values.

      * **editLimits** (*bool*) -- If ``True``, when aforementioned
        buttons are clicked, a `NumberDialog
        <Pwidgets.Numberdialog#pwidgets.numberdialog.NumberDialog>`_
        window will pop up, allowing the user to edit the min/max
        limits.

   **_onRangeChange(ev)**

      Called when the user modifies the low or high range values.
      Syncs the change between the sliders and spinboxes, and emits a
      ``RangeEvent``.

   **_onLimitButton(ev)**

      Called when one of the min/max buttons is pushed. Pops up a
      dialog prompting the user to enter a new value, and updates the
      range limits accordingly. Emits a ``RangeLimitEvent``.

   **SetLimits(minValue, maxValue)**

      Sets the minimum/maximum range values.

   **SetMin(minValue)**

      Sets the minimum range value.

   **SetMax(maxValue)**

      Sets the maximum range value.

   **GetMin()**

      Returns the minimum range value.

   **GetMax()**

      Returns the maximum range value.

   **GetLow()**

      Returns the current low range value.

   **GetHigh()**

      Returns the current high range value.

   **SetLow(lowValue)**

      Sets the current low range value.

   **SetHigh(highValue)**

      Sets the current high range value.

   **GetRange()**

      Return the current (low, high) range values.

   **SetRange(lowValue, highValue)**

      Set the current low and high range values.

**pwidgets.rangeslider._testRangeSliderSpinPanel()**

   Little test program.
