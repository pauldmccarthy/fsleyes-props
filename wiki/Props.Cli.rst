
props.cli module
****************

Generate command line arguments for a `HasProperties
<Props.Properties#props.properties.HasProperties>`_ object.

This module provides the following functions:

``addParserArguments()``:
   Given an ``argparse.ArgumentParser`` and a `HasProperties
   <Props.Properties#props.properties.HasProperties>`_ class (or
   instance), adds arguments to the parser for each `PropertyBase
   <Props.Properties#props.properties.PropertyBase>`_ attribute of the
   `HasProperties <Props.Properties#props.properties.HasProperties>`_
   class.

``applyArguments()``:
   Given a `HasProperties
   <Props.Properties#props.properties.HasProperties>`_ instance and an
   ``argparse.Namespace`` object assumed to have been created by the
   parser mentioned above, sets the property values of the
   `HasProperties <Props.Properties#props.properties.HasProperties>`_
   instance from the values stored in the ``Namespace`` object.

``generateArguments()``:
   Basically the inverse of the ``applyArguments()`` function. Given a
   `HasProperties <Props.Properties#props.properties.HasProperties>`_
   instance, generates a string which contains arguments that could be
   used to re-configure another instance of the same class.

The ``addParserArguments()`` function is used to add arguments to a
``argparse.ArgumentParser`` object for the properties of a
`HasProperties <Props.Properties#props.properties.HasProperties>`_
class. The simplest way to do so is to allow the
``addParserArguments()`` function to automatically generate short and
long arguments from the property names:

::

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

Now, if we have a ``MyObj`` instance, and some arguments:

::

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

If you want to customise the short and long argument tags, and the
help text, for each property, you can pass them in to the
``addParserArguments()`` function:

::

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

Or, you can add the short and long arguments, and the help text, as
specially named class attributes of your `HasProperties
<Props.Properties#props.properties.HasProperties>`_ class:

::

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

Finally, the ``generateArguments()`` function, as the name suggests,
generates command line arguments from a `HasProperties
<Props.Properties#props.properties.HasProperties>`_ instance:

::

   >>> props.cli.generateArguments(myobj)
   ['--someBool', '--TheInt', '23413']

Not all property types are supported at the moment. The ones which are
supported:

..

   * `String <Props.Properties_Types#props.properties_types.String>`_

   * `Choice <Props.Properties_Types#props.properties_types.Choice>`_

   * `Int <Props.Properties_Types#props.properties_types.Int>`_

   * `Real <Props.Properties_Types#props.properties_types.Real>`_

   * `Percentage
     <Props.Properties_Types#props.properties_types.Percentage>`_

   * `Boolean
     <Props.Properties_Types#props.properties_types.Boolean>`_

   * `ColourMap
     <Props.Properties_Types#props.properties_types.ColourMap>`_

   * `Bounds <Props.Properties_Types#props.properties_types.Bounds>`_

   * `Point <Props.Properties_Types#props.properties_types.Point>`_

**props.cli._String(parser, propObj, propCls, propName, propHelp,
shortArg, longArg)**

   Adds an argument to the given parser for the given `String
   <Props.Properties_Types#props.properties_types.String>`_ property.

   :Parameters:
      * **parser** -- An ``argparse.ArgumentParser`` instance.

      * **propCls** -- A `HasProperties
        <Props.Properties#props.properties.HasProperties>`_ class.

      * **propObj** -- The `PropertyBase
        <Props.Properties#props.properties.PropertyBase>`_ class.

      * **propName** (*str*) -- Name of the property.

      * **propHelp** (*str*) -- Custom help text for the property.

      * **shortArg** (*str*) -- String to use as the short argument.

      * **longArg** (*str*) -- String to use as the long argument.

**props.cli._Choice(parser, propObj, propCls, propName, propHelp,
shortArg, longArg)**

   Adds an argument to the given parser for the given `Choice
   <Props.Properties_Types#props.properties_types.Choice>`_ property.
   See the ``_String()`` documentation for details on the parameters.

**props.cli._Boolean(parser, propObj, propCls, propName, propHelp,
shortArg, longArg)**

   Adds an argument to the given parser for the given `Boolean
   <Props.Properties_Types#props.properties_types.Boolean>`_ property.
   See the ``_String()`` documentation for details on the parameters.

**props.cli._Int(parser, propObj, propCls, propName, propHelp,
shortArg, longArg)**

   Adds an argument to the given parser for the given `Int
   <Props.Properties_Types#props.properties_types.Int>`_ property. See
   the ``_String()`` documentation for details on the parameters.

**props.cli._Real(parser, propObj, propCls, propName, propHelp,
shortArg, longArg)**

   Adds an argument to the given parser for the given `Real
   <Props.Properties_Types#props.properties_types.Real>`_ property.
   See the ``_String()`` documentation for details on the parameters.

**props.cli._Percentage(parser, propObj, propCls, propName, propHelp,
shortArg, longArg)**

   Adds an argument to the given parser for the given `Percentage
   <Props.Properties_Types#props.properties_types.Percentage>`_
   property. See the ``_String()`` documentation for details on the
   parameters.

**props.cli._Bounds(parser, propObj, propCls, propName, propHelp,
shortArg, longArg)**

   Adds an argument to the given parser for the given `Bounds
   <Props.Properties_Types#props.properties_types.Bounds>`_ property.
   See the ``_String()`` documentation for details on the parameters.

**props.cli._Point(parser, propObj, propCls, propName, propHelp,
shortArg, longArg)**

   Adds an argument to the given parser for the given `Point
   <Props.Properties_Types#props.properties_types.Point>`_ property.
   See the ``_String()`` documentation for details on the parameters.

**props.cli._ColourMap(parser, propObj, propCls, propName, propHelp,
shortArg, longArg)**

   Adds an argument to the given parser for the given `ColourMap
   <Props.Properties_Types#props.properties_types.ColourMap>`_
   property. See the ``_String()`` documentation for details on the
   parameters.

**props.cli.applyArguments(hasProps, arguments, longArgs=None)**

   Apply arguments to a `HasProperties
   <Props.Properties#props.properties.HasProperties>`_ instance.

   Given a `HasProperties
   <Props.Properties#props.properties.HasProperties>`_ instance and an
   ``argparse.Namespace`` instance, sets the property values of the
   `HasProperties <Props.Properties#props.properties.HasProperties>`_
   instance from the values stored in the ``argparse.Namespace``
   object.

   :Parameters:
      * **hasProps** -- The `HasProperties
        <Props.Properties#props.properties.HasProperties>`_ instance.

      * **arguments** -- The ``argparse.Namespace`` instance.

      * **longArgs** -- Dict containing {property name : longArg}
        mappings.

**props.cli._getShortArgs(propCls, propNames, exclude='')**

   Generates unique single-letter argument names for each of the names
   in the given list of property names. Any letters in the exclude
   string are not used as short arguments.

   :Parameters:
      * **propCls** -- A `HasProperties
        <Props.Properties#props.properties.HasProperties>`_ class.

      * **propNames** (*list*) -- List of property names for which
        short arguments  are to be generated.

      * **exclude** (*str*) -- String containing letters which should
        not be used.

**props.cli.addParserArguments(propCls, parser, cliProps=None,
shortArgs=None, longArgs=None, propHelp=None, exclude='')**

   Adds arguments to the given ``argparse.ArgumentParser`` for the
   properties of the given `HasProperties
   <Props.Properties#props.properties.HasProperties>`_ object.

   :Parameters:
      * **propCls** -- A `HasProperties
        <Props.Properties#props.properties.HasProperties>`_ class.  An
        instance may alternately be passed in.

      * **parser** -- An ``argparse.ArgumentParser`` to add arguments
        to.

      * **cliProps** (*list*) -- List containing the names of
        properties to add arguments for. If ``None``, and an attribute
        called ``_cliProps``' is present on the ``propCls`` class, the
        value of that attribute is used. Otherwise an argument is
        added for all properties.

      * **shortArgs** (*dict*) -- Dict containing ``{propName:
        shortArg}`` mappings, to be used as the short (typically
        single letter) argument flag for each property. If ``None``,
        and  an attribute called ``_shortArgs`` is present on the
        ``propCls`` class, the value of that attribute is used.
        Otherwise, short arguments are automatically generated for
        each property.

      * **longArgs** (*dict*) -- Dict containing ``{propName:
        longArg}`` mappings, to be used as the long argument flag for
        each property. If ``None``, and an attribute called
        ``_longArgs`` is present on the ``propCls`` class, the value
        of that attribute is used. Otherwise, the name of each
        property is used as its long argument.

      * **propHelp** (*dict*) -- Dict containing ``{propName:
        helpString]`` mappings, to be used as the help text for each
        property. If ``None``, and an attribute called ``_propHelp``
        is present on the ``propCls`` class, the value of that
        attribute is used. Otherwise, no help string is used.

      * **exclude** (*str*) -- String containing letters which should
        not be used as short arguments.

**props.cli.generateArguments(hasProps, useShortArgs=False,
cliProps=None, shortArgs=None, longArgs=None, exclude='')**

   Given a `HasProperties
   <Props.Properties#props.properties.HasProperties>`_ instance,
   generates a list of arguments which could be used to configure
   another instance in the same way.

   :Parameters:
      * **hasProps** -- The `HasProperties
        <Props.Properties#props.properties.HasProperties>`_ instance.

      * **useShortArgs** -- If *True* the short argument version is
        used instead of the long argument version.

   See the ``addParserArguments()`` function for descriptions of the
   other parameters.
