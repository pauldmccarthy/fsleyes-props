#!/usr/bin/env python
#
# build.py - Automatically build a wx GUI for a props.HasProperties
#            object.
#
# This module provides functionality to automatically build a GUI
# interface containing widgets which allow the user to change the
# properties (props.PropertyBase objects) of a specified
# props.HasProperties object.

# The sole entry point for this module is the buildGUI function, which
# accepts as parameters a tk object to be used as the parent (e.g. a
# wx.Frame object), a props.HasProperties object, an optional
# ViewItem object, which specifies how the interface is to be laid
# out, two optional dictionaries for passing in labels and tooltips,
# and another optional dictionary for any buttons to be added.
#
# The view parameter allows the layout of the generated interface to
# be customised.  Property widgets may be grouped together by embedding
# them within a HGroup or VGroup object; they will then respectively be
# laid out horizontally or verticaly.  Groups may be embedded within a
# NotebookGroup object, which will result in an interface containing a
# tab for each child Group.  The label for, and behaviour of, the widget
# for an individual property may be customised with a Widget object.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import sys

import wx
import widgets

class ViewItem(object):
    """
    Superclass for Widgets, Buttons, Labels  and Groups. Represents an
    item to be displayed.
    """
    
    def __init__(self, key=None, label=None, tooltip=None,
                 visibleWhen=None, enabledWhen=None):
        """
        Parameters:

          - key:         An identifier for this item. If this item is a
                         Widget, this should be the property name that
                         the widget edits. This key is used to look up
                         labels and tooltips, if they are passed in as
                         dicts (see the buildGUI function).
        
          - label:       A label for this item, which may be used in the
                         GUI.

          - tooltip:     A tooltip, which may be displayed when the user
                         hovers the mouse over the widget for this
                         ViewItem.
        
          - visibleWhen: A 2-tuple which contains the name of a property
                         of the HasProperties object, or a list of
                         property names, and a reference to a function
                         which takes one argument, and returns a
                         boolean.  When the specified property changes,
                         the function is called, and the HasProperties
                         instance passed to it. The return value is used
                         to determine whether this item should be made
                         visible or invisible.
        
          - enabledWhen: Same as the visibleWhen parameter, except the
                         state of the item (or its children) is changed
                         between enabled and disabled.
        """
        
        self.key         = key
        self.label       = label
        self.tooltip     = tooltip
        self.visibleWhen = visibleWhen
        self.enabledWhen = enabledWhen


class Button(ViewItem):
    """
    Represents a button which, when clicked, will call a specified
    callback function.
    """

    def __init__(self, key=None, text=None, callback=None, **kwargs):
        self.callback = callback
        self.text     = text
        ViewItem.__init__(self, key, **kwargs)


class Label(ViewItem):
    """
    Represents a static text label.
    """
    def __init__(self, viewItem=None, **kwargs):
        """
        A Label object may either be created in the same way as any other
        ViewItem object, or it may be created from another ViewItem object,
        the object to be labelled.
        """

        if viewItem is not None:
            kwargs['key']         = '{}_label'.format(viewItem.key)
            kwargs['label']       = viewItem.label
            kwargs['tooltip']     = viewItem.tooltip
            kwargs['visibleWhen'] = viewItem.visibleWhen
            kwargs['enabledWhen'] = viewItem.enabledWhen
            
        ViewItem.__init__(self, **kwargs)
    pass


class Widget(ViewItem):
    """
    Represents a widget which is used to modify a property value.
    """
    def __init__(self, propName, **kwargs):
        """
        Parameters:
        
          - propName: The name of the property which this widget can
                      modify.
        
          - kwargs:   Passed to the ViewItem constructor.
        """
        
        kwargs['key'] = propName
        ViewItem.__init__(self, **kwargs)


class Group(ViewItem):
    """
    Represents a collection of other ViewItems.
    """
    def __init__(self, children=[], showLabels=True, border=False, **kwargs):
        """
        Parameters:
        
          - children:   List of ViewItem objects, the children of this
                        Group.
        
          - showLabels: Whether labels should be displayed for each of
                        the children. If this is true, an attribute will
                        be added to this Group object in the _prepareView
                        function, called 'childLabels', and containing a
                        Label object for each child.

          - border:     If True, this group will be drawn with a border
                        around it. If this group is a child of another
                        VGroup, it will be laid out a bit differently,
                        too.
        
          - kwargs:     Passed to the ViewItem constructor.
        """
        ViewItem.__init__(self, **kwargs)
        self.children   = children
        self.border     = border
        self.showLabels = showLabels


class NotebookGroup(Group):
    """
    A Group representing a GUI Notebook. Children are added as notebook
    pages.
    """
    pass


class HGroup(Group):
    """
    A group representing a GUI panel, whose children are laid out
    horizontally.
    """
    pass


class VGroup(Group): 
    """
    A group representing a GUI panel, whose children are laid out
    vertically.
    """
    pass


class PropGUI(object):
    """
    A container class used for convenience. Stores references to
    all wx objects that are created, and to all conditional
    callbacks (which control visibility/state).
    """
    
    def __init__(self):
        self.onChangeCallbacks = []
        self.tkObjects         = {}
 

def _configureEnabledWhen(viewItem, guiObj, hasProps):
    """
    Returns a reference to a callback function for this view item,
    if its enabledWhen attribute was set.
    Parameters:

      - viewItem: The ViewItem object
      - guiObj:   The GUI object created from the ViewItem
      - hasProps: The HasProperties instance
    """

    if viewItem.enabledWhen is None: return None

    def _toggleEnabled():
        """
        Calls the viewItem.enabledWhen function and
        enables/disables the GUI object, depending
        upon the result.
        """

        if viewItem.enabledWhen(hasProps): state = True
        else:                              state = False

        if guiObj.IsEnabled != state:
            guiObj.Enable(state)

    return _toggleEnabled


def _configureVisibleWhen(viewItem, guiObj, hasProps):
    """
    Returns a reference to a callback function for this view item,
    if its visibleWhen attribute was set.
    """ 

    if viewItem.visibleWhen is None: return None

    def _toggleVis():

        visible = viewItem.visibleWhen(hasProps)

        if visible != guiObj.IsShown():
            guiObj.Show(visible)
            #guiObj.GetParent().Fit()
            guiObj.GetParent().Layout()
        
    return _toggleVis


def _createLabel(parent, viewItem, hasProps, propGui):
    """
    Creates a GUI static text label object containing a label for the
    given viewItem.
    """

    label = wx.StaticText(parent, label=viewItem.label)
    return label


def _createButton(parent, viewItem, hasProps, propGui):
    """
    Creates a GUI Button object for the given ViewItem (assumed to be a
    Button).
    """

    btnText = None

    if   viewItem.text  is not None: btnText = viewItem.text
    elif viewItem.label is not None: btnText = viewItem.label
    elif viewItem.key   is not None: btnText = viewItem.key
        
    button = ttk.Button(parent, text=btnText, command=viewItem.callback)
    return button


def _createWidget(parent, viewItem, hasProps, propGui):
    """
    Creates a widget for the given Widget object, using the
    props.makeWidget function (see the props.widgets module
    for more details).
    """

    widget = widgets.makeWidget(parent, hasProps, viewItem.key)
    return widget

    
def _createNotebookGroup(parent, group, hasProps, propGui):
    """
    Creates a GUI Notebook object for the given NotebookGroup object.
    The children of the group object are also created via recursive
    calls to the _create function.
    """

    panel    = wx.Panel(parent)
    sizer    = wx.BoxSizer(wx.VERTICAL)
    notebook = wx.Notebook(panel)

    for child in group.children:

        page = _create(notebook, child, hasProps, propGui)
        notebook.AddPage(page, child.label)

    panel.SetSizer(sizer)
    sizer.Add(notebook, flag=wx.EXPAND)

    panel.Fit()
    panel.Layout()

    return notebook


def _layoutGroup(group, parent, children, labels):
    """
    Lays out the children (and labels, if not None) of the
    given Group object. Parameters:
    
      - group:    HGroup or VGroup object
    
      - parent:   GUI Frame object which represents the group
    
      - children: List of GUI objects, the children of the group.

      - labels:   None if no labels, otherwise a list of GUI Label
                  objects, one for each child.
    """

    if   isinstance(group, VGroup): sizer = wx.GridBagSizer()
    elif isinstance(group, HGroup): sizer = wx.BoxSizer(wx.HORIZONTAL)
    else:
        raise TypeError('Unknown group type: {}'.format(
            group.__class__.__name__))

    for cidx in range(len(children)):

        if isinstance(group, HGroup):
            if labels is not None and labels[cidx] is not None:
                sizer.Add(labels[cidx], flag=wx.EXPAND)
                
            sizer.Add(children[cidx], flag=wx.EXPAND)
            
        elif isinstance(group, VGroup):

            # Groups within VGroups, which don't have a border, are 
            # laid out the same as any other widget, which probably
            # looks a bit ugly. If they do have a border, however,
            # they are laid out so as to span the entire width of
            # the parent VGroup, and given a border. Instead of
            # having a separate label widget, the label is embedded
            # in the border.
            if isinstance(group.children[cidx], (HGroup, VGroup)) and \
               group.children[cidx].border:

                sizer.Add(children[cidx],
                          pos=(cidx,0),
                          span=(1,2),
                          flag=wx.EXPAND)

            elif labels is not None:
                if labels[cidx] is not None:
                    sizer.Add(labels  [cidx], pos=(cidx,0), flag=wx.EXPAND)
                    sizer.Add(children[cidx], pos=(cidx,1), flag=wx.EXPAND)

                else:
                    sizer.Add(children[cidx],
                              pos=(cidx,1),
                              span=(1,2),
                              flag=wx.EXPAND)

            else:
                sizer.Add(children[cidx],
                          pos=(cidx,0),
                          span=(1,2),
                          flag=wx.EXPAND)

    if isinstance(group, VGroup): sizer.AddGrowableCol(1)

    parent.SetSizer(sizer)
    parent.Layout()


def _createGroup(parent, group, hasProps, propGui):
    """
    Creates a GUI panel object for the given group. Children of the
    group are recursively created via calls to _create, and laid out on
    the Frame via the _layoutGroup function.
    """

    if not group.border:
        realPanel = wx.Panel(parent)
        panel     = realPanel
    else:
        realPanel = wx.StaticBox(parent, group.label)
        panel     = wx.Panel(realPanel)

    childObjs = []

    if group.showLabels: labelObjs = []
    else:                labelObjs = None

    for i,child in enumerate(group.children):

        labelObj = None

        if group.showLabels:
            if group.childLabels[i] is not None:
                labelObj = _create(
                    panel, group.childLabels[i], hasProps, propGui)
                labelObjs.append(labelObj)
            else:
                labelObjs.append(None)

        childObj = _create(panel, child, hasProps, propGui)

        childObjs.append(childObj)

    _layoutGroup(group, panel, childObjs, labelObjs)

    return realPanel


# These aliases are defined so we can introspectively look
# up the appropriate _create* function based upon the class
# name of the ViewItem being created, in the _create
# function below.
_createHGroup = _createGroup
_createVGroup = _createGroup


def _create(parent, viewItem, hasProps, propGui):
    """
    Creates the given ViewItem object and, if it is a group, all of its
    children.
    """

    cls = viewItem.__class__.__name__

    createFunc = getattr(sys.modules[__name__], '_create{}'.format(cls), None)

    if createFunc is None:
        raise ValueError('Unrecognised ViewItem: {}'.format(
            viewItem.__class__.__name__))

    tkObject  = createFunc(parent, viewItem, hasProps, propGui)
    visibleCb = _configureVisibleWhen(viewItem, tkObject, hasProps)
    enableCb  = _configureEnabledWhen(viewItem, tkObject, hasProps)

    if visibleCb is not None: propGui.onChangeCallbacks.append(visibleCb)
    if enableCb  is not None: propGui.onChangeCallbacks.append(enableCb)

    propGui.tkObjects[viewItem.key] = tkObject

    return tkObject


def _defaultView(hasProps):
    """
    Creates a default view specification for the given HasProperties
    object, with all properties laid out vertically. This function is
    only called if a view specification was not provided in the call
    to the buildGUI function (defined below).
    """

    propNames, propObjs = hasProps.getAllProperties()

    widgets = [Widget(name) for name in propNames]
    
    return VGroup(label=hasProps.__class__.__name__, children=widgets)


def _prepareView(viewItem, labels, tooltips):
    """
    Recursively steps through the given viewItem and its children (if
    any). If the viewItem is a string, it is assumed to be a property
    name, and it is turned into a Widget object. If the viewItem does
    not have a label/tooltip, and there is a label/tooltip for it in
    the given labels/tooltips dict, then its label/tooltip is set.
    Returns a reference to the updated/newly created ViewItem.
    """

    if isinstance(viewItem, str):
        viewItem = Widget(viewItem)

    if not isinstance(viewItem, ViewItem):
        raise ValueError('Not a ViewItem')

    if viewItem.label   is None:
        viewItem.label   = labels  .get(viewItem.key, None)
    if viewItem.tooltip is None:
        viewItem.tooltip = tooltips.get(viewItem.key, None) 

    if isinstance(viewItem, Group):

        # children may have been specified as a tuple,
        # so we cast it to a list, making it mutable
        viewItem.children = list(viewItem.children)

        for i,child in enumerate(viewItem.children):
            viewItem.children[i] = _prepareView(child, labels, tooltips)

        # Create a Label object for
        # each child of this group
        if viewItem.showLabels:
            viewItem.childLabels = []

            for child in viewItem.children:

                # unless there is no label specified
                if child.label is None:
                    viewItem.childLabels.append(None)

                # or the child is also a group, and it
                # is configured to be laid out with a
                # border (in which case the label will
                # be displayed as a title)
                elif isinstance(child, (HGroup,VGroup)) and child.border:
                    viewItem.childLabels.append(None)
                else:
                    viewItem.childLabels.append(Label(child))

    return viewItem

    
def _prepareEvents(hasProps, propGui):
    """
    If the visibleWhen or enabledWhen conditional attributes were set
    for any ViewItem objects, a callback function is set on all
    properties. When any property value changes, the visibleWhen/
    enabledWhen callback functions are called.
    """

    if len(propGui.onChangeCallbacks) == 0:
        return

    def onChange(*a):
        for cb in propGui.onChangeCallbacks:
            cb()

    propNames, propObjs = hasProps.getAllProperties()

    # initialise widget states
    onChange()

    # add a callback listener to every property
    for propObj,propName in zip(propObjs,propNames):

        lName = 'ChangeEvent_{}'.format(propName)
        propObj.addListener(hasProps, lName, onChange)
 

def buildGUI(parent,
             hasProps,
             view=None,
             labels=None,
             tooltips=None,
             buttons=None):
    """
    Builds a GUI interface which allows the properties of the given
    hasProps object (a props.HasProperties instance) to be edited.
    Returns a reference to the top level Tkinter object (typically a
    wx.Frame or wx.Notebook).

    Parameters:
    
     - parent:   wx parent object
     - hasProps: props.HasProperties object
    
    Optional:
    
     - view:     ViewItem object, specifying the interface layout
     - labels:   Dict specifying labels
     - tooltips: Dict specifying tooltips
     - buttons:  Dict specifying buttons to add to the interface.
                 Keys are used as button labels, and values are
                 callback functions which take two arguments - the
                 Tkinter parent object, and the HasProperties
                 object (parent and hasProps). Make sure to use a
                 collections.OrderedDict if order is important.
    """

    if view is None: view = _defaultView(hasProps)

    if labels   is None: labels   = {}
    if tooltips is None: tooltips = {}
    if buttons  is None: buttons  = {}

    propGui  = PropGUI()
    view     = _prepareView(view, labels, tooltips) 

    # If any buttons were specified, the properties
    # interface is embedded in a higher level frame,
    # along with the buttons
    if len(buttons) > 0:
        
        topLevel  = wx.Frame(parent)
        topSizer  = wx.BoxSizer(wx.VERTICAL)
        propFrame = _create(topLevel, view, hasProps, propGui)
        
        btnFrame  = wx.Frame(topLevel)
        btnSizer  = wx.BoxSizer(wx.HORIZONTAL) 

        topSizer.Add(propFrame, flag=wx.EXPAND)
        topSizer.Add(btnFrame,  flag=wx.EXPAND)

        for i,(label,callback) in enumerate(buttons.items()):

            button = wx.Button(btnFrame, label=label)

            button.Bind(wx.EVT_BUTTON, lambda e: callback())
            btnSizer.Add(button, flag=wx.EXPAND)
            
    else:
        topLevel = _create(parent, view, hasProps, propGui)

    _prepareEvents(hasProps, propGui)

    # TODO return the propGui object, so the caller has
    # access to all of the Tkinter objects that were
    # created, via the propGui.tkObjects dict.

    return topLevel
