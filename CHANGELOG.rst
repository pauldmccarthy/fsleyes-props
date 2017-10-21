 ``fsleyes-props`` release history
===================================


1.2.2 (under development)
-------------------------


* ``cli`` custom transform functions can now raise a ``SkipArgument``
  exception to indicate that the argument shouid be skipped, either
  when applying or generating arguments.


1.2.1 (Thursday September 21st 2017)
------------------------------------


* ``cli.generateArguments`` function wraps string values in quotes.
* ``cli.generateArguments`` allows extra arguments to be passed through to
  custom transform functions.


1.2.0 (Monday September 11th 2017)
----------------------------------


* Deprecated ``get``/``setConstraint`` in favour of ``get``/``setAttribute``



1.1.2 (Friday August 25th 2017)
-------------------------------


* Even more adjustement to ``PropertyValueList`` item notification/
  synchronisation.


1.1.1 (Thursday August 24th 2017)
---------------------------------


* Further adjustement to ``PropertyValueList`` item notification/
  synchronisation.


1.1.0 (Wednesday August 23rd 2017)
----------------------------------


* ``HasProperties.__init__`` now accepts ``kwargs`` which allow initial
  property values to be set.
* ``SyncableHasProperties`` has new/renamed methods ``detachFromParent`` and
  ``detachAllFromParent``, allowing individual properties to be permanently
  un-synchronised.
* Bugfix to ``PropertyValueList.getLast``
* ``suppress.skip`` function has option to ignore non-existent/deleted
  listeners.
* Fix to ``PropertyValueList`` item notification.



1.0.4 (Thursday August 10th 2017)
---------------------------------


* New function ``makeListWidget``, which creates a widget for a specific item
  in a property value list.


1.0.3 (Friday July 14th 2017)
-----------------------------


* Bug fix to ``fsleyes_props.bindable`` - could potentially pass GC'd functions
  to the ``callqueue``.
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


* ``props`` renamed to ``fsleyes_props``
* ``pwidgets`` removed (moved to separate project ``fsleyes-widgets``)
* Removed ``WeakFunctionRef`` - this is now defined in the ``fslpy`` project.
* Removed ``Bounds`` centering logic
* Adjusted ``CallQueue`` interface to allow arbitrary arguments to be passed
  through to queued functions.


0.10.1 (Thursday April 20th 2017)
---------------------------------


* First public release as part of FSL 5.0.10
