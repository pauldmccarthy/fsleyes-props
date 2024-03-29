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
   skip
"""


import contextlib


@contextlib.contextmanager
def suppress(hasProps, *propNames, notify=False):
    """Suppress notification for the given properties on the given
    :class:`.HasProperties` instance.

    This function saves the current notification state of the properties,
    disables notification, yields to the calling code, and then restores the
    notification state.

    :arg hasProps: ``HasProperties`` instance.

    :arg propNames: Properties to suppress notifications for.

    :arg notify:    If ``True``, a notification will be triggered
                    on ``propNames`` via :meth:`.HasProperties.propNotify`,
                    exit. Defaults to ``False``.

    This function is intended to be used as follows::

        with suppress(hasProps1, 'prop1'):
            # Do stuff which might cause unwanted
            # property value notifications to occur
    """

    states = [hasProps.getNotificationState(p) for p in propNames]

    for propName in propNames:
        hasProps.disableNotification(propName)

    try:
        yield

    finally:
        for propName, state in zip(propNames, states):
            hasProps.setNotificationState(propName, state)

    if notify:
        for propName in propNames:
            hasProps.propNotify(propName)


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


@contextlib.contextmanager
def skip(hasProps, propNames, listenerName, ignoreInvalid=False):
    """Skip the listener with the specified listener name, if/when
    changes to the specified property/properties occur.

    :arg hasProps:      A :class:`.HasProperties` instance.
    :arg propNames:     Name of a property on ``hasProps``, or a sequence of
                        property names.
    :arg listenerName:  Name of the listener to skip.
    :arg ignoreInvalid: Defaults to ``False``. If ``True``, passing a
                        non-existent listener will not result in an error.
    """

    if isinstance(propNames, str):
        propNames = [propNames]

    listenerStates = {}

    for propName in propNames:
        if (not ignoreInvalid) or \
           hasProps.hasListener(propName, listenerName):
            listenerStates[propName] = hasProps.getListenerState(
                propName, listenerName)
            hasProps.disableListener(propName, listenerName)

    try:
        yield

    finally:
        for propName, state in listenerStates.items():
            hasProps.setListenerState(propName, listenerName, state)
