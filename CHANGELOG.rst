This document contains the ``fsleyes-props`` release history in reverse
chronological order.



1.12.0 (Friday 8th November 2024)
---------------------------------


Added
^^^^^


* The :meth:`.Choice.setChoices` method now accepts a `newChoice` argument,
  allowing the new choice value to be set when the choices are updated.
* New `onUser` argument when creating a :class:`.Widget` for a `.Choice`
  property, which is called whenever the user interacts with the widget.


1.11.0 (Monday 18th September 2023)
-----------------------------------


Added
^^^^^


* New ``prefix`` option for :class:`.ColourMap` properties - when a prefix is
  set, assignments to the property, e.g. ``obj.cmap = 'red'``, will cause a
  colour map named ``{prefix}_red`` to be chosen over a colour map named
  ``red``, if the former is registered with matplotlib.


Changed
^^^^^^^


* The :class:`.ColourMap` property no longer supports looking up colour maps
  by their name or registered key. This is because matplotlib 3.8 has made it
  impossible to give a colour map a name different to the key under which it
  registered.


1.10.0 (Tuesday 18th July 2023)
-------------------------------


Changed
^^^^^^^


* :class:`.Array` property types can now be set to ``None``.
* Replaced ``setup.py``-based build system with ``pyproject.toml``.


1.9.6 (Monday 10th July 2023)
-----------------------------


Changed
^^^^^^^


* The type-specific equality function is now used when the ``'default'``
  attribute value is changed, instead of a naive equality (``==``) comparison.
  This is primarily to allow the default value to be set to a ``numpy.array``
  (e.g. for the :class:`.Array` type), for which a naive equality test would
  result in an error.


1.9.5 (Thursday 6th July 2023)
------------------------------


Added
^^^^^


* Added the ability to set the label shown alongside a checkbox bound to a
  :class:`.Boolean` property when creating a via :class:`.Widget`
  specification. The label can be specified with the ``cblabel`` argument.


1.9.4 (Thursday 6th July 2023)
------------------------------


Changed
^^^^^^^


* Adjusted the :func:`.buildGUI` function so that initial widget states (as determined
  by ``enabledWhen`` / ``visibleWhen``) are correctly set.


1.9.3 (Monday 20th March 2023)
------------------------------


Fixed
^^^^^


* Fixed potential infinite loop if a property value is set to the
  :class:`.HasProperties` instance.


1.9.2 (Wednesday 15th March 2023)
---------------------------------


Added
^^^^^


* New :meth:`.HasProperties.wlisten` method, an alias for
  ``addListener(weak=False)``.


1.9.1 (Tuesday 21st February 2023)
----------------------------------


Changed
^^^^^^^


* Adjustments to the :class:`.ColourMap` property so that it prefers colour
  maps that are specified with the ``ColourMap`` over built-in ``matplotlib``
  colour maps.


1.9.0 (Monday 20th February 2023)
---------------------------------


Changed
^^^^^^^


* ``fsleyes-props`` now requires ``matplotlib >= 3.5.0``, and has been
  updated to use the new ``matplotlib.colormaps`` registry.


1.8.3 (Tuesday 7th February 2023)
---------------------------------


Fixed
^^^^^


* Fixed an issue in dependency specification.



1.8.2 (Monday 22nd August 2022)
-------------------------------


Fixed
^^^^^


* Fixed a bug whereby property definitions from a base class would be used
  when creating a :class:`.HasProperties` object, even if those properties
  were overwritten in a sub class.


1.8.1 (Thursday 18th August 2022)
---------------------------------


Changed
^^^^^^^


* Changed the initialisation logic for :class:`.Bounds` properties,
  so that if a ``default`` and ``minval``/``maxval`` are specified,
  the former is not overwritten by the latter.


1.8.0 (Thursday 18th August 2022)
---------------------------------


Added
^^^^^


* New :attr:`fsleyes_props.Props`, :meth:`.HasProperties.listen`,
  :meth:`.HasProperties.ilisten`, :meth:`.HasProperties.remove`,
  :meth:`.HasProperties.bind`, :meth:`.HasProperties.unbind`,
  :meth:`.HasProperties.getatt`, and :meth:`.HasProperties.setatt`
  aliases.


Changed
^^^^^^^

* Property value listener functions can be defined to accept no arguments,
  if none are needed.
* The :class:`.Bounds` property type now accepts ``minval`` and ``maxval``
  options, for setting the initial minimum/maximum limits for each axis.
* The :func:`.suppress` and :func:`.skip` functions now accept one or
  more property names.


1.7.3 (Wednesday April 21st 2021)
---------------------------------


Changed
^^^^^^^

* Fixed deprecated usage of the ``matplotilb.cm.cmap_d`` colour map
  dictionary.


1.7.2 (Saturday March 27th 2021)
--------------------------------


Changed
^^^^^^^

* The :class:`.Color` property type now accepts any value that is accepted by
  the `matplotlib.to_rgba
  <https://matplotlib.org/stable/api/_as_gen/matplotlib.colors.to_rgba.html>`_
  function.
* Properties of type The :class:`.Int` and :class:`.Real` can be set to
  ``None`` (unless ``required=True and allowInvalid=False``).


1.7.1 (Tuesday March 9th 2021)
------------------------------


Changed
^^^^^^^


* The ``fsleyes-props`` API documentation is now hosted at
  https://open.win.ox.ac.uk/pages/fsl/fsleyes/props/
* ``fsleyes-props`` is now tested against Python 3.7, 3.8, and 3.9.
* Removed ``six`` as a dependency.


1.7.0 (Tuesday May 26th 2020)
-----------------------------


Added
^^^^^


* Added a short-hand alias for :class:`.HasProperties` - ``HasProps``.


1.6.7 (Friday October 4th 2019)
-------------------------------


Changed
^^^^^^^


* Minor GTK3 compatibility fixes.


1.6.6 (Wednesday September 18th 2019)
-------------------------------------


Changed
^^^^^^^


* ``fsleyes-props`` is no longer tested against Python 2.7-3.5, but is now
  tested against Python 3.6-3.8, and GTK3.



1.6.5 (Monday January 7th 2019)
-------------------------------


Changed
^^^^^^^


* Removed the ``deprecation`` library as a dependency.


1.6.4 (Friday October 5th 2018)
-------------------------------


Changed
^^^^^^^


* Development (test and documentation dependencies) are no longer listed
  in ``setup.py`` - they now need to be installed manually.
* Removed conda build infrastructure.


1.6.3 (Thursday July 5th 2018)
------------------------------


Changed
^^^^^^^


* Removed ``pytest-runner`` as a dependency.


1.6.2 (Tuesday June 5th 2018)
-----------------------------


Added
^^^^^


* The :mod:`.serialise` module now has support for :class:`.Array` property
  types.


Fixed
^^^^^


* Fixed a regression in the :class:`.SyncableHasProperties` class.


1.6.1 (Friday May 11th 2018)
----------------------------


Fixed
^^^^^


* Fixed an issue in the behaviour of the :meth:`.HasProperties.addProperty`
  method and the :mod:`.syncable` module, with handling of class hierarchies.


Deprecated
^^^^^^^^^^

* Deprecated the :class:`.PropertyOwner` metaclass - property initialisation
  now occurs at the instance level within :meth:`.HasProperties.__new__`.


1.6.0 (Thursday May 3rd 2018)
-----------------------------


Changed
^^^^^^^


* Adjustment to the :mod:`.widgets_choice` module needed due to changes
  in the :class:`.BitmapRadioBox` API.


1.5.1 (Wednesday March 7th 2018)
--------------------------------


Changed
^^^^^^^


* Adjustments to the ``conda`` package build and deployment process.


1.5.0 (Tuesday February 27th 2018)
----------------------------------


* A new class, the :class:`.PropCache`, has been added. This class will
  automatically cache property values based on changes to other property
  values.
* Small adjustments to layout of :class:`.Group` classes in the :mod:`.build`
  module.


1.4.0 (Monday January 8th 2018)
-------------------------------


* The :class:`.ColourMap` widget no longer complains when its property is
  set to a colour map that is registered with ``matplotlib``, but not with
  the property. The error message when an unknown colour map is specified
  has also been improved.
* The :func:`.cli._Choice` function allows additional arguments to be
  passed through to the ``ArgumentParser.add_argument`` method.


1.3.1 (Wednesday January 3rd 2018)
----------------------------------


* Fixed issue in :mod:`.syncable` where sync property change listeners were
  not being called after calls to :meth:`.syncToParent` or
  :meth:`.unsyncFromParent`.


1.3.0 (Wednesday January 3rd 2018)
----------------------------------


* The :class:`SyncableHasProperties` raises a custom error type, instead of a
  ``RuntimeError``, when an illegal attempt is made to synchronise or
  unsynchronise a property.


1.2.5 (Wednesday December 6th 2017)
-----------------------------------


* Fixed a problem with the API documentation build failing again.
* Unit tests are now run against wxPython 3.0.2.0.


1.2.4 (Thursday November 9th 2017)
----------------------------------


* Fixed use of deprecated ``fsl.utils.async`` module from the ``fslpy``
  library.


1.2.3 (Thursday October 26th 2017)
-----------------------------------


* Fixed a problem with the API documentation build failing.


1.2.2 (Saturday October 21st 2017)
----------------------------------


* :mod:`.cli` custom transform functions can now raise a :exc:`.SkipArgument`
  exception to indicate that the argument shouid be skipped, either when
  applying or generating arguments.


1.2.1 (Thursday September 21st 2017)
------------------------------------


* :func:`.cli.generateArguments` function wraps string values in quotes.
* :func:`.cli.generateArguments` allows extra arguments to be passed through
  to custom transform functions.


1.2.0 (Monday September 11th 2017)
----------------------------------


* Deprecated ``get``/``setConstraint`` in favour of ``get``/``setAttribute``,
  on :class:`.HasProperties` and :class:`.PropertyBase` classes.


1.1.2 (Friday August 25th 2017)
-------------------------------


* Even more adjustement to :class:`.PropertyValueList` item notification/
  synchronisation.


1.1.1 (Thursday August 24th 2017)
---------------------------------


* Further adjustement to :class:`.PropertyValueList` item notification/
  synchronisation.


1.1.0 (Wednesday August 23rd 2017)
----------------------------------


* :meth:`.HasProperties.__init__` now accepts ``kwargs`` which allow initial
  property values to be set.
* :class:`.SyncableHasProperties` has new/renamed methods ``detachFromParent``
  and ``detachAllFromParent``, allowing individual properties to be
  permanently un-synchronised.
* Bugfix to :class:`.PropertyValueList.getLast`
* :func:`.suppress.skip` function has option to ignore non-existent/deleted
  listeners.
* Fix to :class:`.PropertyValueList` item notification.



1.0.4 (Thursday August 10th 2017)
---------------------------------


* New function :func:`.makeListWidget`, which creates a widget for a specific
  item in a property value list.


1.0.3 (Friday July 14th 2017)
-----------------------------


* Bug fix to :mod:`fsleyes_props.bindable` - could potentially pass GC'd
  functions to the :mod:`.callqueue`.
* Tweaks to CI build process


1.0.2 (Thursday June 8th 2017)
------------------------------


* Added CI build script
* Fixed some unit tests.


1.0.1 (Sunday June 4th 2017)
----------------------------


* Adjustments to pypi package metadata.


1.0.0 (Saturday May 27th 2017)
------------------------------


* ``props`` renamed to :mod:`fsleyes_props`
* ``pwidgets`` removed (moved to separate project ``fsleyes-widgets``)
* Removed :class:`.WeakFunctionRef` - this is now defined in the ``fslpy``
  project.
* Removed :class:`.Bounds` centering logic
* Adjusted :class:`.CallQueue` interface to allow arbitrary arguments to be
  passed through to queued functions.


0.10.1 (Thursday April 20th 2017)
---------------------------------


* First public release as part of FSL 5.0.10
