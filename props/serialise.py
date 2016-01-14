#!/usr/bin/env python
#
# serialise.py - Functions for serialising/deserialising property values.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides functions for serialising and deserialising the values
of most ``props`` property types (which are defined in
:mod:`.properties_types`).


This module only contains logic for those property types that the default
python conversion routines would not be able to handle. For example, an
:class:`.Int` property value can be serialised with ``str``, and deserialised
with ``int``. Such logic is already built into the ``Int`` class, so there
is no need for this module to duplicate it.


An example of where specific serialisation/deserialisation logic is useful is
the :class:`.Boolean` property. Passing a boolean value,``True`` or ``False``
to the ``str`` function will result in a string ``'True'`` or
``'False'``. However, passing a string ``'True'`` or ``'False'`` to the
``bool`` function will result in ``True`` in both cases.


The logic needed to safely serialise/deserialise :class:`.Boolean` values, and
other property types for which it is needed, is provided by this module.
"""

import sys
import logging


log = logging.getLogger(__name__)


DELIMITER = '#'
"""Delimiter string used to join multi-valued properties. """


def serialise(hasProps, propName):
    """Get the value of the named property from the given
    :class:`.HasProperties` instance, serialise it, and return the
    serialised string.
    """

    propObj  = hasProps.getProp(propName)
    propVal  = getattr(hasProps, propName)
    propType = type(propObj).__name__
    sfunc    = getattr(sys.modules[__name__],
                       '_serialise_{}'.format(propType),
                       None)

    if sfunc is None:
        sfunc = str

    return sfunc(propVal)


def deserialise(hasProps, propName, string):
    """Deserialise the given string, under the assumption that it is a
    serialised value of the named property from the given
    :class:`.HasProperties` instance.
    """
    
    propObj  = hasProps.getProp(propName)
    propType = type(propObj).__name__
    dfunc    = getattr(sys.modules[__name__],
                       '_deserialise_{}'.format(propType),
                       None)

    if dfunc is None:
        dfunc = lambda s: s

    return dfunc(string) 


def _serialise_Boolean(value):
    return str(value)


def _deserialise_Boolean(value):
        
    # Special case - a string containig 'false'
    # (case insensitive) evaluates to False.
    if isinstance(value, basestring):
        value = value.lower()
        if value == 'false':
            value = ''

    # For anything else, we
    # rely on default conversion.
    return bool(value) 


def _serialise_Colour(value):

    # Colour values should be in the range [0, 1]
    r, g, b, a = [int(v * 255) for v in value]
    hexstr     = '#{:02x}{:02x}{:02x}{:02x}'.format(r, g, b, a)
    
    return hexstr


def _deserialise_Colour(value):

    r = value[1:3]
    g = value[3:5]
    b = value[5:7]
    a = value[7:9]

    r, g, b, a = [int(v, base=16) for v in (r, g, b, a)]
    r, g, b, a = [v / 255.0       for v in (r, g, b, a)]

    return [r, g, b, a]


def _serialise_ColourMap(value):
    return value.name


def _deserialise_ColourMap(value):
    import matplotlib.cm as mplcm
    return mplcm.get_cmap(value)


def _serialise_Bounds(value):
    value = map(str, value)
    return DELIMITER.join(value)


def _deserialise_Bounds(value):
    value = value.split(DELIMITER)
    return map(float, value)


def _serialise_Point(value):
    value = map(str, value)
    return DELIMITER.join(value) 


def _deserialise_Point(value):
    value = map(str, value)
    return DELIMITER.join(value)      
