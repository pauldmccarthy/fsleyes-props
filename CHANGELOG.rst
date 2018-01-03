This document contains the ``fsleyes-props`` release history in reverse
chronological order.


1.3.1 (Wednesday January 3rd 2017)
----------------------------------


* Fixed issue in :mod:`.syncable` where sync property change listeners were
  not being called after calls to :meth:`.syncToParent` or
  :meth:`.unsyncFromParent`.


1.3.0 (Wednesday January 3rd 2017)
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
