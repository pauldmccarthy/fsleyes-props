#!/usr/bin/env python
#
# suppress.py - Notification suppression.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides a couple of functions which may be used as context
managers for suppressing notification of changes to :class:`.HasProperties`
property values.

.. autosummary::
   :nosignatures:

   suppress
   suppressAll
"""


import contextlib


@contextlib.contextmanager
def suppress(hasProps, propName, notify=False):
    """Suppress notification for the given property on the given
    :class:`.HasProperties` instance.

    This function saves the current notification state of the
    property, disables notification, yields to the calling code,
    and then restores the notification state.


    :arg hasProps: ``HasProperties`` instance.
    
    :arg propName: Property to suppress notifications for.
    
    :arg notify:   If ``True``, a notification will be triggered
                   on ``propName`` via :meth:`.HasProperties.notify`,
                   exit. Defaults to ``False``.


    This function is intended to be used as follows::

        with suppress(hasProps1, 'prop1'):
            # Do stuff which might cause unwanted
            # property value notifications to occur
    """

    state = hasProps.getNotificationState(propName)
    hasProps.disableNotification(propName)

    try:
        yield
        
    finally:
        hasProps.setNotificationState(propName, state)

    if notify:
        hasProps.notify(propName)


@contextlib.contextmanager
def suppressAll(hasProps):
    """Suppress notification for all properties on the given
    :class:`.HasProperties` instance.

    :arg hasProps: The ``HasProperties`` instance to suppress.


    This function is intended to be used as follows::

        with suppressAll(hasProps):
            # Do stuff which might cause unwanted 
            # property value notifications to occur


    .. note:: After this function has completed. notification
              will be enabled for all properties of ``hasProps``.
              This is in contrast to the :func:`suppress` function,
              which restores the previous notification state of
              the property.
    """

    hasProps.disableAllNotification()

    try:
        yield
    finally:
        hasProps.enableAllNotification()
