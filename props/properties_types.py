#!/usr/bin/env python
#
# properties_types.py - Definitions for different property types.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""Definitions for different property types.

This module provides a number of :class:`~props.properties.PropertyBase`
subclasses which define properties of different types.
"""

import os.path as op

import collections

import matplotlib.colors as mplcolors
import matplotlib.cm     as mplcm

import properties       as props
import properties_value as propvals


class Object(props.PropertyBase):
    """A property which encapsulates any value. """

    def __init__(self, **kwargs):
        """Create a :class:`Object` property. If an ``equalityFunc`` is not
        provided, any writes to this property will be treated as if the value
        has changed (and any listeners will be notified).
        """

        def defaultEquals(this, other):
            return False

        kwargs['equalityFunc'] = kwargs.get('equalityFunc', defaultEquals)
        props.PropertyBase.__init__(self, **kwargs)


class Boolean(props.PropertyBase):
    """A property which encapsulates a ``bool`` value."""

    def __init__(self, **kwargs):
        """Create a :class:`Boolean` property.

        If the ``default`` ``kwarg`` is not provided, a default value of
        ``False`` is used.

        :param kwargs: All passed through to the
                       :class:`~props.properties.PropertyBase`
                       constructor.
        """

        kwargs['default'] = kwargs.get('default', False)
        props.PropertyBase.__init__(self, **kwargs)

        
    def cast(self, instance, attributes, value):
        """Overrides :class:`~props.properties.PropertyBase.cast`.
        Casts the given value to a ``bool``.
        """
        return bool(value)


class Number(props.PropertyBase):
    """Base class for the :class:`Int` and :class:`Real` classes.

    A property which represents a number.  Don't use/subclass this,
    use/subclass one of :class:`Int` or :class:`Real`.
    """
    
    def __init__(self,
                 minval=None,
                 maxval=None,
                 clamped=False,
                 editLimits=False,
                 **kwargs):
        """Define a :class:`Number` property.
        
        :param number minval:   Minimum valid value
        
        :param number maxval:   Maximum valid value
        
        :param bool clamped:    If ``True``, the value will be clamped to its
                                min/max bounds.
        
        :param bool editLimits: If ``True``, widgets created to modify
                                :class:`Number` properties will allow the user
                                to change the min/max values.
        
        :param kwargs:          Passed through to the
                                :class:`~props.properties.PropertyBase`
                                constructor. If a ``default`` value is not
                                provided, it is set to something sensible.
        """

        default = kwargs.get('default', None)

        if default is None:
            if minval is not None and maxval is not None:
                default = (minval + maxval) / 2
            elif minval is not None:
                default = minval
            elif maxval is not None:
                default = maxval
            else:
                default = 0

        kwargs['default']    = default
        kwargs['minval']     = minval
        kwargs['maxval']     = maxval
        kwargs['editLimits'] = editLimits
        kwargs['clamped']    = clamped
        props.PropertyBase.__init__(self, **kwargs)

        
    def validate(self, instance, attributes, value):
        """Overrides :meth:`~props.properties.PropertyBase.validate`.
        Validates the given number.

        Calls the :meth:`~props.properties.PropertyBase.validate` method.
        Then, if the ``minval`` and/or ``maxval`` constraints have been set,
        and the given value is not within those values, a :exc:`ValueError` is
        raised.

        :param instance:        The owning
                                :class:`~props.properties.HasProperties`
                                instance (or ``None`` for unbound property
                                values).
        
        :param dict attributes: Dictionary containing property constraints.
        
        :param number value:    The value to validate.
        """
        
        props.PropertyBase.validate(self, instance, attributes, value)
        
        minval = attributes['minval']
        maxval = attributes['maxval']

        if minval is not None and value < minval:
            raise ValueError('Must be at least {}'.format(minval))
            
        if maxval is not None and value > maxval:
            raise ValueError('Must be at most {}'.format(maxval))


    def cast(self, instance, attributes, value):
        """Overrides :meth:`~props.properties.PropertyBase.cast`.

        If the ``clamped`` constraint is ``True`` and the ``minval`` and/or
        ``maxval`` have been set, this function ensures that the given value
        lies within the ``minval`` and ``maxval`` limits.
        """

        clamped = attributes['clamped']
        
        if not clamped: return value

        minval = attributes['minval']
        maxval = attributes['maxval']

        if minval is not None and value < minval: return minval
        if maxval is not None and value > maxval: return maxval

        return value
        
        
class Int(Number):
    """A property which encapsulates an integer."""
    
    def __init__(self, **kwargs):
        """Define an :class:`Int` property. See the :class:`Number` constructor
        documentation for keyword arguments.
        """
        Number.__init__(self, **kwargs)

        
    def cast(self, instance, attributes, value):
        """Overrides :meth:`Number.cast`. Casts the given value to an ``int``,
        and then passes the value to :meth:`Number.cast`.
        """
        return Number.cast(self, instance, attributes, int(value))
        

class Real(Number):
    """A property which encapsulates a floating point number."""


    def __equals(self, a, b):
        if any((a is None, b is None)): return a == b
        return abs(a - b) < self.__precision

    
    def __init__(self, precision=0.000000001, **kwargs):
        """Define a :class:`Real` property. See the :class:`Number` constructor
        documentation for keyword arguments.
        """

        self.__precision = precision

        Number.__init__(self, equalityFunc=self.__equals, **kwargs)


    def cast(self, instance, attributes, value):
        """Overrides :meth:`Number.cast`. Casts the given value to a ``float``,
        and then passes the value to :meth:`Number.cast`.
        """ 
        return Number.cast(self, instance, attributes, float(value))
        

class Percentage(Real):
    """A property which represents a percentage.

    A :class:`Percentage` property is just a :class:`Real` property with
    a default minimum value of ``0`` and maximum value of ``100``.
    """

    def __init__(self, **kwargs):
        kwargs['minval']  = kwargs.get('minval',    0.0)
        kwargs['maxval']  = kwargs.get('maxval',  100.0)
        kwargs['default'] = kwargs.get('default',  50.0)
        Real.__init__(self, **kwargs)


class String(props.PropertyBase):
    """A property which encapsulates a string."""
    
    def __init__(self, minlen=None, maxlen=None, **kwargs):
        """Define a :class:`String` property.
        
        :param int minlen: Minimum valid string length.
        :param int maxlen: Maximum valid string length.
        """ 
        
        kwargs['default'] = kwargs.get('default', None)
        kwargs['minlen']  = minlen
        kwargs['maxlen']  = maxlen
        props.PropertyBase.__init__(self, **kwargs)


    def cast(self, instance, attributes, value):
        """Overrides :meth:`~props.properties.PropertyBase.cast`.

        Casts the given value to a string. If the given value is the empty
        string, it is replaced with ``None``.
        """

        if value is None: value = ''
        else:             value = str(value)
        
        if value == '': value = None
        return value

        
    def validate(self, instance, attributes, value):
        """Overrides :meth:`~props.properties.PropertyBase.validate`.

        Passes the given value to
        :meth:`~props.properties.PropertyBase.validate`. Then, if either the
        ``minlen`` or ``maxlen`` constraints have been set, and the given
        value has length less than ``minlen`` or greater than ``maxlen``,
        raises a :exc:`ValueError`.
        """
        
        if value == '': value = None
        
        props.PropertyBase.validate(self, instance, attributes, value)

        if value is None: return

        if not isinstance(value, basestring):
            raise ValueError('Must be a string')

        minlen = attributes['minlen']
        maxlen = attributes['maxlen']

        if minlen is not None and len(value) < minlen:
            raise ValueError('Must have length at least {}'.format(minlen))

        if maxlen is not None and len(value) > maxlen:
            raise ValueError('Must have length at most {}'.format(maxlen))
        

class Choice(props.PropertyBase):
    """A property which may only be set to one of a set of predefined values.

    Individual choices can be enabled/disabled via the :meth:`enableChoice`
    and :meth:`disableChoice` methods. The ``choiceEnabled`` property
    constraint/attribute contains a list of boolean values representing the
    enabled/disabled state of each choice.
    """

    def __init__(self, choices=None, labels=None, **kwargs):
        """Define a :class:`Choice` property.

        As an alternative to passing in separate ``choice`` and
        ``choiceLabels`` lists, you may pass in a dict as the ``choice``
        parameter. The keys will be used as the choices, and the values as
        labels. Make sure to use a :class:`collections.OrderedDict` if the
        display order is important.
        
        :param list choices: List of values, the possible values that
                             this property can take.

        :param list labels:  List of string labels, one for each choice,
                             to be used for display purposes.
        """

        if choices is None:
            choices = []
            labels  = []

        elif isinstance(choices, dict):
            choices, labels = zip(*choices.items())

        elif labels is None:
            labels = map(str, choices)

        if len(choices) > 0: default = choices[0]
        else:                default = None

        if len(choices) != len(labels):
            raise ValueError('A label is required for every choice')

        kwargs['choices']       = list(choices)
        kwargs['labels']        = list(labels)
        kwargs['default']       = kwargs.get('default',      default)
        kwargs['allowInvalid']  = kwargs.get('allowInvalid', False)
        kwargs['choiceEnabled'] = {choice: True for choice in choices}

        props.PropertyBase.__init__(self, **kwargs)

        
    def enableChoice(self, choice, instance=None):
        """Enables the given choice.
        """
        choiceEnabled = dict(self.getConstraint(instance, 'choiceEnabled'))
        choiceEnabled[choice] = True
        self.setConstraint(instance, 'choiceEnabled', choiceEnabled)

        
    def disableChoice(self, choice, instance=None):
        """Disables the given choice. An attempt to set the property to
        a disabled value will result in a ``ValueError``.
        """
        choiceEnabled = dict(self.getConstraint(instance, 'choiceEnabled'))
        choiceEnabled[choice] = False
        self.setConstraint(instance, 'choiceEnabled', choiceEnabled) 


    def choiceEnabled(self, choice, instance=None):
        """Returns ``True`` if the given choice is enabled, ``False``
        otherwise.
        """
        return self.getConstraint(instance, 'choiceEnabled')[choice]


    def getChoices(self, instance=None):
        """Returns a list of the current choices. """
        return list(self.getConstraint(instance, 'choices'))

    
    def getLabels(self, instance=None):
        """Returns a list of the current choice labels. """
        return list(self.getConstraint(instance, 'labels'))

    
    def setLabel(self, choice, label, instance=None):
        """Sets the label for the specified choice."""
        choices = list(self.getConstraint(instance, 'choices'))
        labels  = list(self.getConstraint(instance, 'labels'))

        labels[choices.index(choice)] = label

        self.setConstraint(instance, 'labels',  labels)


    def _updateChoices(self, choices, labels, instance=None):
        
        propVal    = self.getPropVal(instance)
        default    = self.getConstraint(instance, 'default')
        oldEnabled = self.getConstraint(instance, 'choiceEnabled')
        newEnabled = {}

        # Prevent notification during the period
        # where the length of the labels list
        # may not match the length of the choices
        # list
        if propVal is not None:
            oldChoice  = propVal.get()
            notifState = propVal.getNotificationState()
            propVal.disableNotification()

        for choice in choices:
            if choice in oldEnabled: newEnabled[choice] = oldEnabled[choice]
            else:                    newEnabled[choice] = True

        self.setConstraint(instance, 'labels',        labels)
        self.setConstraint(instance, 'choiceEnabled', newEnabled)

        if propVal is not None:
            propVal.setNotificationState(notifState)

            if oldChoice not in choices:
                if default in choices: propVal.set(default)
                else:                  propVal.set(choices[0])
             
        self.setConstraint(instance, 'choices', choices)


    def setChoices(self, choices, labels=None, instance=None):
        """Sets the list of possible choices (and their labels, if not None).
        """
        if labels is None: labels = map(str, choices)

        if len(choices) != len(labels):
            raise ValueError('A label is required for every choice')

        self._updateChoices(choices, labels, instance)

        if len(choices) > 0:
            self.setConstraint(instance, 'default', choices[0])
            self.__set__(instance, choices[0])
        else:
            self.setConstraint(instance, 'default', None)


    def addChoice(self, choice, label=None, instance=None):
        """Adds a new choice to the list of possible choices."""

        if label is None:
            label = choice

        choices = list(self.getConstraint(instance, 'choices'))
        labels  = list(self.getConstraint(instance, 'labels'))

        choices.append(choice)
        labels .append(label)

        self._updateChoices(choices, labels, instance)

        if len(choices) == 1:
            self.setConstraint(instance, 'default', choices[0])
            self.__set__(instance, choices[0])

        
    def validate(self, instance, attributes, value):
        """Raises a :exc:`ValueError` if the given value is not one of the
        possible values for this :class:`Choice` property.
        """
        props.PropertyBase.validate(self, instance, attributes, value)

        enabled = self.getConstraint(instance, 'choiceEnabled')
        choices = self.getChoices(instance)

        if len(choices) == 0: return
        if value is None:     return

        if value not in choices:
            raise ValueError('Invalid choice ({})'    .format(value))
        if not enabled[value]:
            raise ValueError('Choice is disabled ({})'.format(value))
                


class FilePath(String):
    """A property which represents a file or directory path.

    There is currently no support for validating a path which may be either a
    file or a directory - only one or the other. 
    """

    def __init__(self, exists=False, isFile=True, suffixes=[], **kwargs):
        """Define a :class:`FilePath` property.

        :param bool exists:   If ``True``, the path must exist.
        
        :param bool isFile:   If ``True``, the path must be a file. If
                              ``False``, the path must be a directory. This
                              check is only performed if ``exists`` is
                              ``True``.
        
        :param list suffixes: List of acceptable file suffixes (only relevant
                              if ``isFile`` is ``True``).
        """

        kwargs['exists']   = exists
        kwargs['isFile']   = isFile
        kwargs['suffixes'] = suffixes
        
        String.__init__(self, **kwargs)

        
    def validate(self, instance, attributes, value):
        """Overrides :meth:`~props.properties.PropertyBase.validate`.

        If the ``exists`` constraint is not ``True``, does nothing. Otherwise,
        if ``isFile`` is ``False`` and the given value is not a path to an
        existing directory, a :exc:`ValueError` is raised.

        If ``isFile`` is ``True``, and the given value is not a path to an
        existing file (which, if ``suffixes`` is not None, must end in one of
        the specified suffixes), a :exc:`ValueError` is raised.
        """

        String.validate(self, instance, attributes, value)

        exists   = attributes['exists']
        isFile   = attributes['isFile']
        suffixes = attributes['suffixes']

        if value is None: return
        if value == '':   return
        if not exists:    return

        if isFile:

            matchesSuffix = any(map(lambda s: value.endswith(s), suffixes))

            # If the file doesn't exist, it's bad
            if not op.isfile(value):
                raise ValueError('Must be a file ({})'.format(value))

            # if the file exists, and matches one of
            # the specified suffixes, then it's good
            if len(suffixes) == 0 or matchesSuffix: return

            # Otherwise it's bad
            else:
                raise ValueError(
                    'Must be a file ending in [{}] ({})'.format(
                        ','.join(suffixes), value))

        elif not op.isdir(value):
            raise ValueError('Must be a directory ({})'.format(value))


class List(props.ListPropertyBase):
    """A property which represents a list of items, of another property type.

    If you use :class:`List` properties, you really should read the
    documentation for the :class:`~props.properties_value.PropertyValueList`,
    as it contains important usage information.
    """
    
    def __init__(self,
                 listType=None,
                 minlen=None,
                 maxlen=None,
                 embed=False,
                 **kwargs):
        """Define a :class:`List` property.
        
        :param listType:   A :class:`~props.properties.PropertyBase` type,
                           specifying the values allowed in the list. If
                           ``None``, anything can be stored in the list, 
                           but no casting or validation will occur.
                
        :param int minlen: Minimum list length.
        :param int maxlen: Maximum list length.
        :param bool embed: If ``True``, when a graphical interface is made
                           to edit this list property, a widget is embedded
                           directly into the parent GUI. Otherwise, a button
                           is embedded which, when clicked, opens a dialog
                           allowing the user to edit the list.
        """

        if (listType is not None) and \
           (not isinstance(listType, props.PropertyBase)):
            raise ValueError(
                'A list type (a PropertyBase instance) must be specified')

        kwargs['default'] = kwargs.get('default', [])
        kwargs['minlen']  = minlen
        kwargs['maxlen']  = maxlen

        self.embed        = embed

        props.ListPropertyBase.__init__(self, listType,  **kwargs)


    def validate(self, instance, attributes, value):
        """Overrides :meth:`~props.properties.PropertyBase.validate`.
        
        Checks that the given value (which should be a list) meets the
        ``minlen``/``maxlen`` constraints. Raises a :exc:`ValueError` if it
        does not.
        """

        props.ListPropertyBase.validate(self, instance, attributes, value)

        minlen = attributes['minlen']
        maxlen = attributes['maxlen']

        if minlen is not None and len(value) < minlen:
            raise ValueError('Must have length at least {}'.format(minlen))
        if maxlen is not None and len(value) > maxlen:
            raise ValueError('Must have length at most {}'.format(maxlen))
     

class Colour(props.PropertyBase):
    """A property which represents a RGB colour, stored as three floating
    point values in the range ``0.0 - 1.0``.
    """

    
    def __init__(self, **kwargs):
        """Create a :class:`Colour` property.

        If the ``default`` ``kwarg`` is not provided, the default is set
        to white.

        :param kwargs: All passed through to the
                       :class:`~props.properties.PropertyBase`
                       constructor.
        """

        kwargs['default'] = kwargs.get('default', (1.0, 1.0, 1.0))
        props.PropertyBase.__init__(self, **kwargs)


    def validate(self, instance, attributes, value):
        """Checks the given ``value``, and raises a ``ValueError`` if
        it does not consist of three floating point numbers in the
        range ``(0.0 - 1.0)``.
        """
        props.PropertyBase.validate(self, instance, attributes, value)

        if (not isinstance(value, collections.Sequence)) or (len(value) != 3):
            raise ValueError('Colour must be a sequence of three values')

        for v in value:
            if (v < 0.0) or (v > 1.0):
                raise ValueError('Colour values must be between 0.0 and 1.0')
    
        
    def cast(self, instance, attributes, value):
        """Ensures that the given ``value`` contains three floating point
        numbers, in the range ``(0.0 - 1.0)``.
        """

        value = map(float, value[:3])

        for i, v in enumerate(value):
            if v < 0.0: value[i] = 0.0
            if v > 1.0: value[i] = 1.0
        
        return value


class ColourMap(props.PropertyBase):
    """A property which encapsulates a :class:`matplotlib.colors.Colormap`.

    ColourMap values may be specified either as a
    :class:`matplotlib.colors.Colormap` instance, or as a string containing
    the name of a registered colour map instance.
    """

    def __init__(self, cmapNames=None, **kwargs):
        """Define a :class:`ColourMap` property.
        
        If a default value is not given, the :data:`matplotlib.cm.Greys_r`
        colour map is used. Or, if ``cmapNames`` is not ``None``, the first
        name is used.

        :param cmapNames: List of strings, the names of possible colour maps
                          (must be registered with the :mod:`matplotlib.cm`
                          module). If ``None``, all registered colour maps
                          are used.
        """

        default = kwargs.get('default', None)

        if default is None:
            if cmapNames is None: default = mplcm.Greys_r
            else:                 default = mplcm.get_cmap(cmapNames[0])

        elif isinstance(default, str):
            default = mplcm.get_cmap(default)
            
        elif not isinstance(default, mplcolors.Colormap):
            raise ValueError(
                'Invalid  ColourMap default: '.format(
                    default.__class__.__name__))
 
        if cmapNames is None:
            cmapNames = sorted(mplcm.cmap_d.keys())
        
        kwargs['cmapNames'] = cmapNames
        kwargs['default']   = default
        props.PropertyBase.__init__(self, **kwargs)


    def cast(self, instance, attributes, value):
        """Overrides :meth:`~props.properties.PropertyBase.cast`.
        
        If the provided value is a string, an attempt is made to convert it to
        a colour map, via the :func:`matplotlib.cm.get_cmap` function.
        """

        if isinstance(value, str):
            value = mplcm.get_cmap(value)
            
        return value


class BoundsValueList(propvals.PropertyValueList):
    """A list of values which represent bounds along a number of dimensions
    (up to 4).

    This class is used by the :class:`Bounds` property to encapsulate bounding
    values for an arbitrary number of dimensions. For ``N+1`` dimensions, the
    bounding values are stored as a list::

      [lo0, hi0, lo1, hi1, ..., loN, hiN]

    This class just adds some convenience methods and attributes to the
    :class:`~props.properties_value.PropertyValueList` superclass.  For a
    single dimension, a bound object has a ``lo`` value and a ``hi`` value,
    specifying the bounds along that dimension. To make things confusing, each
    dimension also has ``min`` and ``max`` constraints, which define the
    minimum/maximum values that the ``lo`` and ``high`` values may take for
    that dimension.

    Some dynamic attributes are available on :class:`BoundsValueList` objects,
    allowing access to and assignment of bound values and
    constraints. Dimensions ``0, 1, 2, 3`` respectively map to identifiers
    ``x, y, z, t``. If an attempt is made to access/assign an attribute
    corresponding to a dimension which does not exist on a particular
    :class:`BoundsValueList` instance (e.g. attribute ``t`` on a 3-dimensional
    list), an :exc:`IndexError` will be raised. Here is an example of dynamic
    bound attribute access::

        class MyObj(props.HasProperties):
            myBounds = Bounds(ndims=4)

        obj = MyObj()

        # set/access lo/hi values together
        xlo, xhi = obj.mybounds.x
        obj.mybounds.z = (25, 30)

        # set/access lo/hi values separately
        obj.mybounds.xlo = 2
        obj.mybounds.zhi = 50

        # get the length of the bounds for a dimension
        ylen = obj.mybounds.ylen

        # set/access the minimum/maximum 
        # constraints for a dimension
        obj.mybounds.xmin = 0
        tmax = obj.mybounds.tmax

    """


    def __init__(self, *args, **kwargs):
        propvals.PropertyValueList.__init__(self, *args, **kwargs)

        
    def getLo(self, axis):
        """Return the low value for the given (0-indexed) axis."""
        return self[axis * 2]

        
    def getHi(self, axis):
        """Return the high value for the given (0-indexed) axis."""
        return self[axis * 2 + 1]

        
    def getRange(self, axis):
        """Return the (low, high) values for the given (0-indexed) axis."""
        return (self.getLo(axis), self.getHi(axis))

        
    def getLen(self, axis):
        """Return the distance between the low and high values for the
        specified axis.
        """
        return abs(self.getHi(axis) - self.getLo(axis))

        
    def setLo(self, axis, value):
        """Set the low value for the specified axis."""        
        self[axis * 2] = value

        
    def setHi(self, axis, value):
        """Set the high value for the specified axis."""
        self[axis * 2 + 1] = value

        
    def setRange(self, axis, loval, hival):
        """Set the low and high values for the specified axis."""
        self[axis * 2:axis * 2 + 2] = [loval, hival]

        
    def getMin(self, axis):
        """Return the minimum value (the low limit) for the specified axis."""
        return self.getPropertyValueList()[axis * 2].getAttribute('minval')

        
    def getMax(self, axis):
        """Return the maximum value (the high limit) for the specified axis."""
        return self.getPropertyValueList()[axis * 2 + 1].getAttribute('maxval') 

        
    def setMin(self, axis, value):
        """Set the minimum value for the specified axis."""
        self.getPropertyValueList()[axis * 2]    .setAttribute('minval', value)
        self.getPropertyValueList()[axis * 2 + 1].setAttribute('minval', value)

        
    def setMax(self, axis, value):
        """Set the maximum value for the specified axis."""
        self.getPropertyValueList()[axis * 2]    .setAttribute('maxval', value)
        self.getPropertyValueList()[axis * 2 + 1].setAttribute('maxval', value)

        
    def getLimits(self, axis):
        """Return (minimum, maximum) limit values for the specified axis."""
        return (self.getMin(axis), self.getMax(axis))

        
    def setLimits(self, axis, minval, maxval):
        """Set the minimum and maximum limit values for the specified axis."""
        self.setMin(axis, minval)
        self.setMax(axis, maxval)

        
    def __getattr__(self, name):
        """Return the specified value. Raises an :exc:`AttributeError` for
        unrecognised attributes, or an :exc:`IndexError` if an attempt is made
        to access bound values values of a higher dimension than this list
        contains.
        
        See the :class:`BoundsValueList` documentation for details on the
        different attributes available.
        """

        lname = name.lower()

        # TODO this is easy to read, but 
        # could be made much more efficient
        if   lname == 'x':    return self.getRange(0)
        elif lname == 'y':    return self.getRange(1)
        elif lname == 'z':    return self.getRange(2)
        elif lname == 't':    return self.getRange(3)
        elif lname == 'xlo':  return self.getLo(   0)
        elif lname == 'xhi':  return self.getHi(   0)
        elif lname == 'ylo':  return self.getLo(   1)
        elif lname == 'yhi':  return self.getHi(   1)
        elif lname == 'zlo':  return self.getLo(   2)
        elif lname == 'zhi':  return self.getHi(   2)
        elif lname == 'tlo':  return self.getLo(   3)
        elif lname == 'thi':  return self.getHi(   3) 
        elif lname == 'xlen': return self.getLen(  0)
        elif lname == 'ylen': return self.getLen(  1)
        elif lname == 'zlen': return self.getLen(  2)
        elif lname == 'tlen': return self.getLen(  3)
        elif lname == 'xmin': return self.getMin(  0)
        elif lname == 'ymin': return self.getMin(  1)
        elif lname == 'zmin': return self.getMin(  2)
        elif lname == 'tmin': return self.getMin(  3)
        elif lname == 'xmax': return self.getMax(  0)
        elif lname == 'ymax': return self.getMax(  1)
        elif lname == 'zmax': return self.getMax(  2)
        elif lname == 'tmax': return self.getMax(  3) 

        raise AttributeError('{} has no attribute called {}'.format(
            self.__class__.__name__, name))

        
    def __setattr__(self, name, value):
        """Set the specified value. Raises an :exc:`IndexError` if an attempt 
        is made to assign bound values values of a higher dimension than this 
        list contains.
        
        See the :class:`BoundsValueList` documentation for details on the
        different attributes available.

        """ 

        lname = name.lower()
        
        if   lname == 'x':    self.setRange(0, *value)
        elif lname == 'y':    self.setRange(1, *value)
        elif lname == 'z':    self.setRange(2, *value)
        elif lname == 't':    self.setRange(3, *value)
        elif lname == 'xlo':  self.setLo(   0, value)
        elif lname == 'xhi':  self.setHi(   0, value)
        elif lname == 'ylo':  self.setLo(   1, value)
        elif lname == 'yhi':  self.setHi(   1, value)
        elif lname == 'zlo':  self.setLo(   2, value)
        elif lname == 'zhi':  self.setHi(   2, value)
        elif lname == 'tlo':  self.setLo(   3, value)
        elif lname == 'thi':  self.setHi(   3, value) 
        elif lname == 'xmin': self.setMin(  0, value)
        elif lname == 'ymin': self.setMin(  1, value)
        elif lname == 'zmin': self.setMin(  2, value)
        elif lname == 'tmin': self.setMin(  3, value)
        elif lname == 'xmax': self.setMax(  0, value)
        elif lname == 'ymax': self.setMax(  1, value)
        elif lname == 'zmax': self.setMax(  2, value)
        elif lname == 'tmax': self.setMax(  3, value)
        else:                 self.__dict__[name] = value


class Bounds(List):
    """Property which represents numeric bounds in any number of dimensions,
    as long as that number is no more than 4.

    :class:`Bound` values are stored in a :class:`BoundsValueList`, a list of
    integer or floating point values, with two values (lo, hi) for each
    dimension.

    :class:`Bound` values may also have bounds of their own,
    i.e. minimium/maximum values that the bound values can take. These
    bound-limits are referred to as 'min' and 'max', and can be set via the
    :meth:`BoundsValueList.setMin` and :meth:`BoundsValueList.setMax`
    methods. The advantage to using these methods, instead of using, for
    example, :meth:`~props.properties.HasProperties.setItemConstraint`, is
    that if you use the latter you will have to set the constraints on both
    the low and the high values.

    """

    def __init__(self,
                 ndims=1,
                 real=True, 
                 minDistance=None,
                 editLimits=False,
                 labels=None,
                 **kwargs):
        """Define a :class:`Bounds` property.
        
        :param int ndims:         Number of dimensions. This is (currently) 
                                  not a property constraint, hence it cannot 
                                  be changed.

        :param bool real:         If ``True``, the point values are stored as
                                  :class:`Real` values; otherwise, they are
                                  stored as :class:`Int` values.
        
        :param float minDistance: Minimum distance to be maintained between the
                                  low/high values for each dimension.
        
        :param bool editLimits:   If ``True``, widgets created to edit this
                                  :class:`Bounds` will allow the user to edit
                                  the min/max limits.
        
        :param list labels:       List of labels of length ``2*ndims``, 
                                  containing (low, high) labels for each
                                  dimension.
        """

        default = kwargs.get('default', None)

        if minDistance is None:
            minDistance = 0.0

        if default is None:
            default = [0.0, minDistance] * ndims

        if ndims < 1 or ndims > 4:
            raise ValueError('Only bounds of one to four '
                             'dimensions are supported')

        elif len(default) != 2 * ndims:
            raise ValueError('{} bound values are required'.format(2 * ndims))

        if labels is not None and len(labels) != 2 * ndims:
            raise ValueError('A label for each dimension is required')

        kwargs['default']     = default
        kwargs['minDistance'] = minDistance
        kwargs['editLimits']  = editLimits

        self._real   = real
        self._ndims  = ndims
        self._labels = labels

        if real: listType = Real(clamped=True, editLimits=editLimits)
        else:    listType = Int( clamped=True, editLimits=editLimits)

        List.__init__(self,
                      listType=listType,
                      minlen=ndims * 2,
                      maxlen=ndims * 2,
                      **kwargs)

        
    def _makePropVal(self, instance):
        """Overrides :meth:`~props.properties.ListPropertyBase._makePropVal`.

        Creates and returns a :class:`BoundsValueList` instead of a
        :class:`~props.properties.PropertyValueList`, so callers get to use the
        convenience methods/attributes defined in the BVL class.
        """

        default = self._defaultConstraints.get('default', None)

        bvl = BoundsValueList(
            instance,
            name=self.getLabel(instance),
            values=default,
            itemCastFunc=self._listType.cast,
            itemEqualityFunc=self._listType._equalityFunc,
            itemValidateFunc=self._listType.validate,
            listValidateFunc=self.validate,
            listAttributes=self._defaultConstraints,
            itemAttributes=self._listType._defaultConstraints)
        
        return bvl

        
    def validate(self, instance, attributes, value):
        """Overrides :meth:`~props.properties.PropertyBase.validate`.
        
        Raises a :exc:`ValueError` if the given value (a list of min/max
        values) is of the wrong length or data type, or if any of the min
        values are greater than the corresponding max value.
        """

        minDistance = attributes['minDistance']

        # the List.validate method will check
        # the value length and type for us
        List.validate(self, instance, attributes, value)

        for i in range(self._ndims):

            imin = value[i * 2]
            imax = value[i * 2 + 1]

            if imin > imax:
                raise ValueError('Minimum bound must be smaller '
                                 'than maximum bound (dimension {}, '
                                 '{} - {}'.format(i, imin, imax))

            if imax - imin < minDistance:
                raise ValueError('Minimum and maximum bounds must be at '
                                 'least {} apart'.format(minDistance))


class PointValueList(propvals.PropertyValueList):
    """A list of values which represent a point in some n-dimensional (up to 4)
    space.
    
    This class is used by the :class:`Point` property to encapsulate point
    values for between 1 and 4 dimensions. 

    This class just adds some convenience methods and attributes to the
    :class:`~props.properties_value.PropertyValueList` superclass.

    The point values for each dimension may be queried/assigned via the
    dynamic attributes ``x, y, z, t``, which respectively map to dimensions
    ``0, 1, 2, 3``. When querying/assigning point values, you may use
    `GLSL-like swizzling
    <http://www.opengl.org/wiki/Data_Type_(GLSL)#Swizzling>`_. For example::

        class MyObj(props.HasProperties):
            mypoint = props.Point(ndims=3)
 
        obj = MyObj()

        y,z = obj.mypoint.yz

        obj.mypoint.zxy = (3,6,1)
    """

    
    def __init__(self, *args, **kwargs):
        propvals.PropertyValueList.__init__(self, *args, **kwargs)

        
    def getPos(self, axis):
        """Return the point value for the specified (0-indexed) axis."""
        return self[axis]

        
    def setPos(self, axis, value):
        """Set the point value for the specified axis."""
        self[axis] = value

        
    def getMin(self, axis):
        """Get the minimum limit for the specified axis."""
        return self.getPropertyValueList()[axis].getAttribute('minval')

        
    def getMax(self, axis):
        """Get the maximum limit for the specified axis."""
        return self.getPropertyValueList()[axis].getAttribute('maxval')

        
    def getLimits(self, axis):
        """Get the (minimum, maximum) limits for the specified axis."""
        return (self.getMin(axis), self.getMax(axis))

        
    def setMin(self, axis, value):
        """Set the minimum limit for the specified axis."""
        self.getPropertyValueList()[axis].setAttribute('minval', value)

        
    def setMax(self, axis, value):
        """Set the maximum limit for the specified axis."""
        self.getPropertyValueList()[axis].setAttribute('maxval', value)

        
    def setLimits(self, axis, minval, maxval):
        """Set the minimum and maximum limits for the specified axis."""
        self.setMin(axis, minval)
        self.setMax(axis, maxval)

        
    def __getattr__(self, name):
        """Return the specified point value. Raises an :exc:AttributeError for
        unrecognised attributes, or an :exc:`IndexError` if a dimension which
        does not exist for this :class:`PointValueList` is specified.

        See the :class:`PointValueList` documentation for more details.
        """

        lname = name.lower()

        if any([dim not in 'xyzt' for dim in lname]):
            raise AttributeError('{} has no attribute called {}'.format(
                self.__class__.__name__, name))

        res = []
        for dim in lname:
            if   dim == 'x': res.append(self[0])
            elif dim == 'y': res.append(self[1])
            elif dim == 'z': res.append(self[2])
            elif dim == 't': res.append(self[3])
            
        if len(res) == 1: return res[0]
        return res

        
    def __setattr__(self, name, value):
        """Set the specified point value. Raises an :exc:`IndexError` if a
        dimension which does not exist for this :class:`PointValueList` is
        specified.

        See the :class:`PointValueList` documentation for more details.
        """ 

        lname = name.lower()

        if any([dim not in 'xyzt' for dim in lname]):
            self.__dict__[name] = value
            return

        if len(lname) == 1:
            value = [value]

        if len(lname) != len(value):
            raise AttributeError('Improper number of values '
                                 '({}) for attribute {}'.format(
                                     len(value), lname))
            
        newvals = self[:]
        
        for dim, val in zip(lname, value):
            if   dim == 'x': newvals[0] = val
            elif dim == 'y': newvals[1] = val
            elif dim == 'z': newvals[2] = val
            elif dim == 't': newvals[3] = val

        self[:] = newvals


class Point(List):
    """A property which represents a point in some n-dimensional (up to 4)
    space.

    :class:`Point` property values are stored in a :class:`PointValueList`, a
    list of integer or floating point values, one for each dimension.
    """

    def __init__(self,
                 ndims=2,
                 real=True, 
                 editLimits=False,
                 labels=None,
                 **kwargs):
        """Define a :class:`Point` property.
        
        :param int ndims:       Number of dimensions.
        
        :param bool real:       If ``True`` the point values are stored as
                                :class:`Real` values, otherwise they are
                                stored as :class:`Int` values.
        
        :param bool editLimits: If ``True``, widgets created to edit this
                                :class:`Point` will allow the user to edit
                                the min/max limits.
        
        :param list labels:     List of labels, one for each dimension.
        """

        default = kwargs.get('default', None)

        if default is None: default = [0] * ndims

        if real:
            default = map(float, default)

        if ndims < 1 or ndims > 4:
            raise ValueError('Only points of one to four '
                             'dimensions are supported')
            
        elif len(default) != ndims:
            raise ValueError('{} point values are required'.format(ndims))

        if labels is not None and len(labels) != ndims:
            raise ValueError('A label for each dimension is required')

        kwargs['default']    = default
        kwargs['editLimits'] = editLimits
        
        self._ndims   = ndims
        self._real    = real
        self._labels  = labels

        if real: listType = Real(clamped=True, editLimits=editLimits)
        else:    listType = Int( clamped=True, editLimits=editLimits)

        List.__init__(self,
                      listType=listType,
                      minlen=ndims,
                      maxlen=ndims,
                      **kwargs)

        
    def _makePropVal(self, instance):
        """Overrides :meth:`~props.properties.ListPropertyBase._makePropVal`.

        Creates and returns a :class:`PointValueList` instead of a
        :class:`~props.properties_value.PropertyValueList`, so callers get to
        use the convenience methods/attributes defined in the PVL class.
        """

        default = self._defaultConstraints.get('default', None)

        pvl = PointValueList(
            instance,
            name=self.getLabel(instance),
            values=default,
            itemCastFunc=self._listType.cast,
            itemEqualityFunc=self._listType._equalityFunc,
            itemValidateFunc=self._listType.validate,
            listValidateFunc=self.validate,
            listAttributes=self._defaultConstraints,
            itemAttributes=self._listType._defaultConstraints)
        
        return pvl
