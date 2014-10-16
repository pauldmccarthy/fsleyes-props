#!/usr/bin/env python
#
# cli.py - Generate command line arguments for a HasProperties object.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

"""Generate command line arguments for a
:class:`~props.properties.HasProperties` object.

This module provides the following functions:

:func:`addParserArguments`:
    Given an :class:`argparse.ArgumentParser` and a
    :class:`~props.properties.HasProperties` class (or instance), adds
    arguments to the parser for each :class:`~props.properties.PropertyBase`
    attribute of the :class:`~props.properties.HasProperties` class.

:func:`applyArguments`:
    Given a :class:`~props.properties.HasProperties` instance and an
    :class:`argparse.Namespace` object assumed to have been created by the
    parser mentioned above, sets the property values of the
    :class:`~props.properties.HasProperties` instance from the values stored
    in the :class:`~argparse.Namespace` object.

:func:`generateArguments`:
    Basically the inverse of the :func:`applyArguments` function. Given a
    :class:`~props.properties.HasProperties` instance, generates a string
    which contains arguments that could be used to re-configure another
    instance of the same class.

The :func:`addParserArguments` function is used to add arguments to a
:class:`argparse.ArgumentParser` object for the properties of a
:class:`~props.properties.HasProperties` class. The simplest way to do so is
to allow the :func:`addParserArguments` function to automatically generate
short and long arguments from the property names::

    >>> import argparse
    >>> import props

    >>> class MyObj(props.HasProperties):
            intProp  = props.Int()
            boolProp = props.Boolean()

    >>> parser = argparse.ArgumentParser('MyObj')
    >>> props.addParserArguments(MyObj, parser)

    >>> parser.print_help()
    usage: MyObj [-h] [-b] [-i INT]

    optional arguments:
        -h, --help            show this help message and exit
        -b, --boolProp
        -i INT, --intProp INT

Now, if we have a :class:`MyObj` instance, and some arguments::

    >>> myobj = MyObj()

    >>> args = parser.parse_args(['-b', '--intProp', '52'])

    >>> print myobj
    MyObj
      boolProp = False
       intProp = 0

    >>> props.applyArguments(myobj, args)
    >>> print myobj
    MyObj
      boolProp = True
       intProp = 52

If you want to customise the short and long argument tags, and the help text,
for each property, you can pass them in to the :func:`addParserArguments`
function::

    >>> shortArgs = {'intProp' : 'r',              'boolProp' : 't'}
    >>> longArgs  = {'intProp' : 'TheInt',         'boolProp' : 'someBool'}
    >>> propHelp  = {'intProp' : 'Sets int value', 'boolProp' : 'Toggles bool'}

    >>> parser = argparse.ArgumentParser('MyObj')
    >>> props.addParserArguments(MyObj, 
                                 parser,
                                 shortArgs=shortArgs,
                                 longArgs=longArgs,
                                 propHelp=propHelp)
    >>> parser.print_help()
    usage: MyObj [-h] [-t] [-r INT]

    optional arguments:
      -h, --help            show this help message and exit
      -t, --someBool        Toggles bool
      -r INT, --TheInt INT  Sets int value

Or, you can add the short and long arguments, and the help text, as specially
named class attributes of your :class:`~props.properties.HasProperties` class::

    >>> class MyObj(props.HasProperties):
            intProp  = props.Int()
            boolProp = props.Boolean()
            _shortArgs = {
                'intProp'  : 'r',
                'boolProp' : 't'
            }
            _longArgs = {
                'intProp'  : 'TheInt',
                'boolProp' : 'someBool'
            }
            _propHelp = {
                'intProp' : 'Sets int value',
                'boolProp' : 'Toggles bool'
            }

    >>> parser = argparse.ArgumentParser('MyObj')
    >>> props.addParserArguments(MyObj, parser)

    >>> parser.print_help()
    usage: MyObj [-h] [-t] [-r INT]

    optional arguments:
      -h, --help            show this help message and exit
      -t, --someBool        Toggles bool
      -r INT, --TheInt INT  Sets int value

    >>> args = parser.parse_args('--someBool -r 23413'.split())
    >>> myobj = MyObj()
    >>> props.applyArguments(myobj, args)
    >>> print myobj
    MyObj
      boolProp = True
       intProp = 23413

Finally, the :func:`generateArguments` function, as the name suggests,
generates command line arguments from a
:class:`~props.properties.HasProperties` instance::

    >>> props.cli.generateArguments(myobj)
    ['--someBool', '--TheInt', '23413']

Not all property types are supported at the moment. The ones which are
supported:

  - :class:`~props.properties_types.String`
  - :class:`~props.properties_types.Choice`
  - :class:`~props.properties_types.Int`
  - :class:`~props.properties_types.Real`
  - :class:`~props.properties_types.Percentage`
  - :class:`~props.properties_types.Boolean`
  - :class:`~props.properties_types.ColourMap`
  - :class:`~props.properties_types.Bounds`
  - :class:`~props.properties_types.Point`
"""

import logging
log = logging.getLogger(__name__)

import sys
import argparse

import matplotlib.cm as mplcm

import properties as props

# The functions below add an argument to an 
# ArgumentParser for a specific property type.

def _String(parser, propObj, propCls, propName, propHelp, shortArg, longArg):
    """Adds an argument to the given parser for the given
    :class:`~props.properties_types.String` property.
    
    :param parser:       An :class:`argparse.ArgumentParser` instance.
    
    :param propCls:      A :class:`~props.properties.HasProperties` class.

    :param propObj:      The :class:`~props.properties.PropertyBase` class.
    
    :param str propName: Name of the property.
    
    :param str propHelp: Custom help text for the property.
    
    :param str shortArg: String to use as the short argument.
    
    :param str longArg:  String to use as the long argument.
    """
    parser.add_argument(shortArg, longArg, help=propHelp) 


def _Choice(parser, propObj, propCls, propName, propHelp, shortArg, longArg):
    """Adds an argument to the given parser for the given
    :class:`~props.properties_types.Choice` property. See the
    :func:`_String` documentation for details on the parameters.
    """
    # I'm assuming here that all choices are of the
    # same type, and that said type is a standard
    # python builtin (e.g. str, int, float, etc)
    parser.add_argument(shortArg,
                        longArg,
                        type=type(propObj._choices[0]),
                        help=propHelp,
                        default=propObj._default,
                        choices=propObj._choices)
    
    
def _Boolean(parser, propObj, propCls, propName, propHelp, shortArg, longArg):
    """Adds an argument to the given parser for the given
    :class:`~props.properties_types.Boolean` property. See the
    :func:`_String` documentation for details on the parameters.
    """
    parser.add_argument(shortArg,
                        longArg,
                        help=propHelp,
                        action='store_true')

    
def _Int(parser, propObj, propCls, propName, propHelp, shortArg, longArg):
    """Adds an argument to the given parser for the given
    :class:`~props.properties_types.Int` property. See the
    :func:`_String` documentation for details on the parameters.
    """ 
    parser.add_argument(shortArg,
                        longArg,
                        help=propHelp,
                        metavar='INT',
                        type=int)

    
def _Real(parser, propObj, propCls, propName, propHelp, shortArg, longArg):
    """Adds an argument to the given parser for the given
    :class:`~props.properties_types.Real` property. See the
    :func:`_String` documentation for details on the parameters.
    """ 
    parser.add_argument(shortArg,
                        longArg,
                        help=propHelp,
                        metavar='REAL',
                        type=float)

    
def _Percentage(
        parser, propObj, propCls, propName, propHelp, shortArg, longArg):
    """Adds an argument to the given parser for the given
    :class:`~props.properties_types.Percentage` property. See the
    :func:`_String` documentation for details on the parameters.
    """ 
    parser.add_argument(shortArg,
                        longArg,
                        help=propHelp,
                        metavar='PERC',
                        type=float)    


def _Bounds(parser, propObj, propCls, propName, propHelp, shortArg, longArg):
    """Adds an argument to the given parser for the given
    :class:`~props.properties_types.Bounds` property. See the
    :func:`_String` documentation for details on the parameters.
    """ 
    ndims = getattr(propCls, propName)._ndims
    real  = getattr(propCls, propName)._real
    if real: bType = float
    else:    bType = int
    parser.add_argument(shortArg,
                        longArg,
                        help=propHelp,
                        metavar='N',
                        type=bType,
                        nargs=2 * ndims)


def _Point(parser, propObj, propCls, propName, propHelp, shortArg, longArg):
    """Adds an argument to the given parser for the given
    :class:`~props.properties_types.Point` property. See the
    :func:`_String` documentation for details on the parameters.
    """ 
    ndims = getattr(propCls, propName)._ndims
    real  = getattr(propCls, propName)._real
    if real: pType = float
    else:    pType = int 
    parser.add_argument(shortArg,
                        longArg,
                        help=propHelp,
                        metavar='N',
                        type=pType,
                        nargs=ndims) 

    
def _ColourMap(
        parser, propObj, propCls, propName, propHelp, shortArg, longArg):
    """Adds an argument to the given parser for the given
    :class:`~props.properties_types.ColourMap` property. See the
    :func:`_String` documentation for details on the parameters.
    """ 
    # Attempt to retrieve a matplotlib.cm.ColourMap
    # instance given its name
    def parse(cmapName):
        try:
            return mplcm.get_cmap(cmapName)
        except:
            raise argparse.ArgumentTypeError(
                'Unknown colour map: {}'.format(cmapName))
    
    parser.add_argument(shortArg,
                        longArg,
                        help=propHelp,
                        type=parse,
                        metavar='CMAP',
                        action='store')


def applyArguments(hasProps,
                   arguments,
                   longArgs=None):
    """Apply arguments to a :class:`~props.properties.HasProperties` instance.

    Given a :class:`~props.properties.HasProperties` instance and an
    :class:`argparse.Namespace` instance, sets the property values of the
    :class:`~props.properties.HasProperties` instance from the values
    stored in the :class:`argparse.Namespace` object.

    :param hasProps:  The :class:`~props.properties.HasProperties` instance.
    
    :param arguments: The :class:`argparse.Namespace` instance.

    :param longArgs:  Dict containing {property name : longArg} mappings.
    """

    propNames, propObjs = hasProps.getAllProperties()

    if longArgs is None:
        if hasattr(hasProps, '_longArgs'): longArgs = hasProps._longArgs
        else:                              longArgs = dict(zip(propNames,
                                                               propNames))
    
    for propName, propObj in zip(propNames, propObjs):

        argName = longArgs[propName]
        argVal  = getattr(arguments, argName, None)

        if argVal is None: continue
            
        setattr(hasProps, propName, argVal)

    
def _getShortArgs(propCls, propNames, exclude=''):
    """Generates unique single-letter argument names for each of the names in
    the given list of property names. Any letters in the exclude string are
    not used as short arguments.

    :param propCls:        A :class:`~props.properties.HasProperties` class.
    
    :param list propNames: List of property names for which short arguments 
                           are to be generated.
    
    :param str exclude:    String containing letters which should not be used.
    """

    letters   = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    shortArgs = {}

    for propName in propNames:

        # if '_shortArgs' is present on the hasProps
        # object, and there is an entry for the
        # current property, use that entry.
        if hasattr(propCls, '_shortArgs'):
            if propName in propCls._shortArgs:

                # throw an error if that entry
                # has already been used, or
                # should be excluded
                if propCls._shortArgs[propName] in shortArgs.values() or \
                   propCls._shortArgs[propName] in exclude:
                    raise RuntimeError(
                        'Duplicate or excluded short argument for property '
                        '{}.{}: {}'.format(
                            propCls.__name__,
                            propName,
                            propCls._shortArgs[propName]))
                                       
                shortArgs[propName] = propCls._shortArgs[propName]
                continue

        # use the first unique letter in the
        # property name or, if that doesn't
        # work, in the alphabet
        for c in propName + letters:
            
            if (c not in shortArgs.values()) and (c not in exclude):
                shortArgs[propName] = c
                break

    if any([name not in shortArgs for name in propNames]):
        raise RuntimeError('Could not generate default short arguments '
                           'for HasProperties object {} - please provide '
                           'custom short arguments via a _shortArgs '
                           'attribute'.format(propCls.__name__))
        
    return shortArgs

    
def addParserArguments(
        propCls,
        parser,
        cliProps=None,
        shortArgs=None,
        longArgs=None,
        propHelp=None,
        exclude=''):
    """Adds arguments to the given :class:`argparse.ArgumentParser` for the
    properties of the given :class:`~props.properties.HasProperties` object.

    :param propCls:        A :class:`~props.properties.HasProperties` class. 
                           An instance may alternately be passed in.
    
    :param parser:         An :class:`argparse.ArgumentParser` to add
                           arguments to.
    
    :param list cliProps:  List containing the names of properties to add
                           arguments for. If ``None``, and an attribute called
                           ``_cliProps``' is present on the ``propCls`` class,
                           the value of that attribute is used. Otherwise an
                           argument is added for all properties.
    
    :param dict shortArgs: Dict containing ``{propName: shortArg}`` mappings,
                           to be used as the short (typically single letter)
                           argument flag for each property. If ``None``, and 
                           an attribute called ``_shortArgs`` is present on
                           the ``propCls`` class, the value of that attribute
                           is used. Otherwise, short arguments are
                           automatically generated for each property.
    
    :param dict longArgs:  Dict containing ``{propName: longArg}`` mappings,
                           to be used as the long argument flag for each
                           property. If ``None``, and an attribute called
                           ``_longArgs`` is present on the ``propCls`` class,
                           the value of that attribute is used. Otherwise, the
                           name of each property is used as its long argument.
    
    :param dict propHelp:  Dict containing ``{propName: helpString]``
                           mappings, to be used as the help text for each
                           property. If ``None``, and an attribute called
                           ``_propHelp`` is present on the ``propCls`` class,
                           the value of that attribute is used. Otherwise, no
                           help string is used.
    
    :param str exclude:    String containing letters which should not be used
                           as short arguments.
    """

    if isinstance(propCls, props.HasProperties):
        propCls = propCls.__class__

    if cliProps is None:
        if hasattr(propCls, '_cliProps'):
            cliProps = propCls._cliProps
        else:
            cliProps = propCls.getAllProperties()[0]

    if propHelp is None:
        if hasattr(propCls, '_propHelp'): propHelp = propCls._propHelp
        else:                             propHelp = {}

    if longArgs is None:
        if hasattr(propCls, '_longArgs'): longArgs = propCls._longArgs
        else:                             longArgs = dict(zip(cliProps,
                                                              cliProps))

    if shortArgs is None:
        if hasattr(propCls, '_shortArgs'):
            shortArgs = propCls._shortArgs
        else:
            shortArgs = _getShortArgs(propCls, cliProps, exclude)

    for propName in cliProps:

        propObj    = propCls.getProp(propName)
        propType   = propObj.__class__.__name__
        parserFunc = getattr(
            sys.modules[__name__],
            '_{}'.format(propType), None)

        if parserFunc is None:
            log.warn('No CLI parser function for property {} '
                     '(type {})'.format(propName, propType))
            continue

        shortArg =  '-{}'.format(shortArgs[propName])
        longArg  = '--{}'.format(longArgs[ propName])

        parserFunc(parser,
                   propObj,
                   propCls,
                   propName,
                   propHelp.get(propName, None),
                   shortArg,
                   longArg)

        
def generateArguments(hasProps,
                      useShortArgs=False,
                      cliProps=None,
                      shortArgs=None,
                      longArgs=None,
                      exclude=''):
    """
    Given a :class:`~props.properties.HasProperties` instance, generates a list
    of arguments which could be used to configure another instance in the same
    way. 
    
    :param hasProps:     The :class:`~props.properties.HasProperties` instance.

    :param useShortArgs: If `True` the short argument version is used instead
                         of the long argument version.

    See the :func:`addParserArguments` function for descriptions of the other
    parameters.
    """
    args = []

    if cliProps is None:
        if hasattr(hasProps, '_cliProps'):
            cliProps = hasProps._cliProps
        else:
            cliProps = hasProps.getAllProperties()[0]

    if longArgs is None:
        if hasattr(hasProps, '_longArgs'): longArgs = hasProps._longArgs
        else:                              longArgs = dict(zip(cliProps,
                                                               cliProps))

    if shortArgs is None:
        if hasattr(hasProps, '_shortArgs'):
            shortArgs = hasProps._shortArgs
        else:
            shortArgs = _getShortArgs(hasProps, cliProps, exclude)
 
    for propName in cliProps:
        propObj = hasProps.getProp(propName)
        propVal = getattr(hasProps, propName)

        if useShortArgs: argKey =  '-{}'.format(shortArgs[propName])
        else:            argKey = '--{}'.format(longArgs[ propName])

        if isinstance(propObj, props.Bounds):
            value = ' '.join(['{}'.format(v) for v in propVal])
            
        elif isinstance(propObj, props.Point):
            value = ' '.join(['{}'.format(v) for v in propVal])

        elif isinstance(propObj, props.ColourMap):
            value = propVal.name
            
        elif isinstance(propObj, props.Boolean):
            value = None
            if not propVal: argKey = None
        else:
            value = propVal

        if argKey is not None: args.append(argKey)
        if value  is not None: args.append(value)

    return args
