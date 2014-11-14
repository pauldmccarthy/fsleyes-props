#!/usr/bin/env python
#
# build_parts.py - Parts used by the build module to build a GUI from a
# HasProperties object.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""Parts for building a GUI.

This module provides definitiions of the parts used by the :mod:`~props.build`
module to build a GUI from a :mod:`~props.HasProperties` object.
"""

import logging
log = logging.getLogger(__name__)


class ViewItem(object):
    """Superclass for :class:`Widget`, :class:`Button`, :class:`Label` and
    :class:`Group`. Represents an item to be displayed.
    """

    def __init__(self, key=None, label=None, tooltip=None,
                 visibleWhen=None, enabledWhen=None):
        """Define a :class:`ViewItem`.

        :param str key:     An identifier for this item. If this item is a
                            :class:`Widget`, this should be the property
                            name that the widget edits. This key is used to
                            look up labels and tooltips, if they are passed
                            in as dicts (see :func:`buildGUI`).
        
        :param str label:   A label for this item, which may be used in the
                            GUI.

        :param str tooltip: A tooltip, which may be displayed when the user
                            hovers the mouse over the widget for this
                            :class:`ViewItem`.
        
        :param visibleWhen: A function which takes one argument, the
                            :class:`~props.properties.HasProperties` instance,
                            and returns a ``bool``. When any property values
                            change, the function is called. The return value
                            is used to determine whether this item should be
                            made visible or invisible.
        
        :param enabledWhen: Same as the ``visibleWhen`` parameter, except the
                            state of the item (and its children) is changed
                            between enabled and disabled.

        """

        self.key         = key
        self.label       = label
        self.tooltip     = tooltip
        self.visibleWhen = visibleWhen
        self.enabledWhen = enabledWhen


class Button(ViewItem):
    """Represents a button which, when clicked, will call a specified callback
    function.

    When the button is clicked, it is passed two arguemnts - the
    :class:`~props.properties.HasProperties` instance, and the
    :class:`wx.Button` instance.
    """

    def __init__(self, key=None, text=None, callback=None, **kwargs):
        self.callback = callback
        self.text     = text
        ViewItem.__init__(self, key, **kwargs)


class Label(ViewItem):
    """Represents a static text label."""

    
    def __init__(self, viewItem=None, **kwargs):
        """Define a label.

        :class:`Label` objects are automatically created for other
        :class:`ViewItem` objects, which are to be labelled.
        """

        if viewItem is not None:
            kwargs['key']         = '{}_label'.format(viewItem.key)
            kwargs['label']       = viewItem.label
            kwargs['tooltip']     = viewItem.tooltip
            kwargs['visibleWhen'] = viewItem.visibleWhen
            kwargs['enabledWhen'] = viewItem.enabledWhen
            
        ViewItem.__init__(self, **kwargs)


class LinkBox(ViewItem):
    """Represents a checkbox which allows the user to control whether a
    property is linked (a.k.a. bound) to the parent of the
    :class:`HasProperties` object.
    """

    def __init__(self, viewItem=None, **kwargs):

        if viewItem is not None:
            self.propKey          = viewItem.key
            kwargs['key']         = '{}_linkBox'.format(viewItem.key)
            kwargs['label']       = viewItem.label
            kwargs['tooltip']     = viewItem.tooltip
            kwargs['visibleWhen'] = viewItem.visibleWhen
            kwargs['enabledWhen'] = viewItem.enabledWhen
            
        ViewItem.__init__(self, **kwargs) 


class Widget(ViewItem):
    """Represents a widget which is used to modify a property value. """

    
    def __init__(self, propName, **kwargs):
        """Define a :class:`Widget`.
        
        :param str propName: The name of the property which this widget can
                             modify.
        
        :param kwargs:       Passed to the :class:`ViewItem` constructor.
        """
        
        kwargs['key'] = propName
        ViewItem.__init__(self, **kwargs)


class Group(ViewItem):
    """Represents a collection of other :class:`ViewItem` objects.

    This class is not to be used directly - use one of the subclasses:
      - :class:`VGroup`
      - :class:`HGroup`
      - :class:`NotebookGroup`
    """

    
    def __init__(self, children, showLabels=True, border=False, **kwargs):
        """Define a :class:`Group`.
        
        Parameters:
        
        :param children:        List of :class:`ViewItem` objects, the
                                children of this :class:`Group`.
        
        :param bool showLabels: Whether labels should be displayed for each of
                                the children. If this is ``True``, an attribute
                                will be added to this :class:`Group` object in
                                the :func:`_prepareView` function, called
                                ``childLabels``, which contains a
                                :class:`Label` object for each child.

        :param bool border:     If ``True``, this group will be drawn with a 
                                border around it. If this group is a child of
                                another :class:`VGroup`, it will be laid out
                                a bit differently, too.
        
        :param kwargs:          Passed to the :class:`ViewItem` constructor.
        """
        ViewItem.__init__(self, **kwargs)
        self.children   = children
        self.border     = border
        self.showLabels = showLabels


class NotebookGroup(Group):
    """A :class:`Group` representing a GUI Notebook. Children are added as
    notebook pages.
    """
    def __init__(self, children, **kwargs):
        """Define a :class:`NotebookGroup`.

        :param children: List of :class:`ViewItem` objects - a tab in the
                         notebook is added for each child.
        """
        Group.__init__(self, children, **kwargs)


class HGroup(Group):
    """A group representing a GUI panel, whose children are laid out
    horizontally.
    """
    pass


class VGroup(Group): 
    """A group representing a GUI panel, whose children are laid out
    vertically.
    """
    def __init__(self, children, **kwargs):
        kwargs['border'] = kwargs.get('border', True)
        Group.__init__(self, children, **kwargs) 
