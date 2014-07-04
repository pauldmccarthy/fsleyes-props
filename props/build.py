#!/usr/bin/env python
#
# build.py - Automatically build a wx GUI for a props.HasProperties
#            object.

# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

"""Automatically build a :mod:`wx` GUI for a
:class:`~props.properties.HasProperties` object.

This module provides functionality to automatically build a :mod:`wx` GUI
containing widgets which allow the user to change the property values
(:class:`~props.properties.PropertyBase` objects) of a specified
:class:`~props.properties.HasProperties` object.


The sole entry point for this module is the :func:`buildGUI` function, which
accepts as parameters a GUI object to be used as the parent (e.g. a
:class:`wx.Panel` object), a :class:`~props.properties.HasProperties` object,
an optional :class:`ViewItem` object, which specifies how the interface is to
be laid out, and two optional dictionaries for passing in labels and tooltips.


The :func:`buildDialog` function is also provided for convenience. It simply
embeds the result of a call to :func:`buildGUI` in a :class:`wx.Dialog`, and
returns the dialog instance.


The :class:`ViewItem` class allows the layout of the generated interface to be
customised.  Property widgets may be grouped together by embedding them within
a :class:`HGroup` or :class:`VGroup` object; they will then respectively be
laid out horizontally or verticaly.  Groups may be embedded within a
:class:`NotebookGroup` object, which will result in an interface containing a
tab for each child :class:`Group`.  The label for, and behaviour of, the
widget for an individual property may be customised with a :class:`Widget`
object. As an example::

    import wx
    import props

    class MyObj(props.HasProperties):
        myint  = props.Int()
        mybool = props.Boolean()

    # A reasonably complex view specification
    view = props.VGroup(
      label='MyObj properties',
      children=(
          props.Widget('mybool',
                       label='MyObj Boolean',
                       tooltip='If this is checked, you can '
                               'edit the MyObj Integer'),
          props.Widget('myint',
                       label='MyObj Integer',
                       enabledWhen=lambda mo: mo.mybool)))

    # A simpler view specification
    view = props.VGroup(('mybool', 'myint'))

    # The simplest view specification - a
    # default one will be generated
    view = None

    myobj = MyObj()
 
    app   = wx.App()
    frame = wx.Frame(None)

    myObjPanel = props.buildGUI(frame, myobj, view)

You may also pass in widget labels and tooltips to the :func:`buildGUI`
function::

    labels = {
        'myint':  'MyObj Integer value',
        'mybool': 'MyObj Boolean value'
    }

    tooltips = {
        'myint' : 'MyObj Integer tooltip'
    }

    props.buildGUI(frame, myobj, view=view, labels=labels, tooltips=tooltips)

As an alternative to passing in a view, labels, and tooltips to the
:func:`buildGUI` function, they may be specified as class attributes of the
HasProperties object, with respective names ``_view``, ``_labels``, and
``_tooltips``::

    class MyObj(props.HasProperties):
        myint  = props.Int()
        mybool = props.Boolean()

        _view = props.HGroup(('myint', 'mybool'))
        _labels = {
            'myint':  'MyObj integer',
            'mybool': 'MyObj boolean'
        }
        _tooltips = {
            'myint':  'MyObj integer tooltip',
            'mybool': 'MyObj boolean tooltip'
        }

    props.buildGUI(frame, myobj)

"""

import sys
import wx

import widgets

import pwidgets.notebook as nb


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


class PropGUI(object):
    """An internal container class used for convenience. Stores references to
    all :mod:`wx` objects that are created, and to all conditional callbacks
    (which control visibility/state).
    """
    
    def __init__(self):
        self.onChangeCallbacks = []
        self.guiObjects        = {}
        self.topLevel          = None
 

def _configureEnabledWhen(viewItem, guiObj, hasProps):
    """Returns a reference to a callback function for this view item,
    if its ``enabledWhen`` attribute was set.

    :param viewItem: The :class:`ViewItem` object
    :param guiObj:   The GUI object created from the :class:`ViewItem`
    :param hasProps: The :class:`~props.properties.HasProperties` instance
    """

    if viewItem.enabledWhen is None: return None

    parent         = guiObj.GetParent()
    isNotebookPage = isinstance(parent, nb.Notebook)

    def toggleAll(obj, state):

        obj.Enable(state)

        for child in obj.GetChildren():
            toggleAll(child, state)

    def _toggleEnabled():
        """Calls the viewItem.enabledWhen function and
        enables/disables the GUI object, depending
        upon the result.
        """

        if viewItem.enabledWhen(hasProps): state = True
        else:                              state = False

        if isNotebookPage:
            if state: parent.EnablePage( parent.FindPage(guiObj))
            else:     parent.DisablePage(parent.FindPage(guiObj))

        elif guiObj.IsEnabled() != state:
            toggleAll(guiObj, state)

    return _toggleEnabled


def _configureVisibleWhen(viewItem, guiObj, hasProps):
    """Returns a reference to a callback function for this view item,
    if its visibleWhen attribute was set. See :func:`_configureEnabledWhen`.
    """ 

    if viewItem.visibleWhen is None: return None

    parent         = guiObj.GetParent()
    isNotebookPage = isinstance(parent, nb.Notebook)

    def _toggleVis():

        visible = viewItem.visibleWhen(hasProps)

        if isNotebookPage:
            if visible: parent.ShowPage(parent.FindPage(guiObj))
            else:       parent.HidePage(parent.FindPage(guiObj))

        elif visible != guiObj.IsShown():
            parent.GetSizer().Show(guiObj, visible)
            parent.GetSizer().Layout()
        
    return _toggleVis


def _createLabel(parent, viewItem, hasProps, propGui):
    """Creates a :class:`wx.StaticText` object containing a label for the
    given :class:`ViewItem`.
    """
    label = wx.StaticText(parent, label=viewItem.label)
    return label


def _createButton(parent, viewItem, hasProps, propGui):
    """Creates a :class:`wx.Button` object for the given :class:`Button`
    object.
    """

    btnText = None

    if   viewItem.text  is not None: btnText = viewItem.text
    elif viewItem.label is not None: btnText = viewItem.label
    elif viewItem.key   is not None: btnText = viewItem.key
        
    button = wx.Button(parent, label=btnText)
    button.Bind(wx.EVT_BUTTON, lambda e: viewItem.callback(hasProps, button))
    return button


def _createWidget(parent, viewItem, hasProps, propGui):
    """Creates a widget for the given :class:`Widget` object, using the
    :func:`~props.widgets.makeWidget` function (see the :mod:`props.widgets`
    module for more details).
    """

    widget = widgets.makeWidget(parent, hasProps, viewItem.key)
    return widget


def _makeGroupBorder(parent, group, ctr, *args, **kwargs):
    """Makes a border for a :class:`Group`.
    
    If a the ``border`` attribute of a :class:`Group` object has been set to
    ``True``, this function is called. It creates a parent :class:`wx.Panel`
    with a border and title, then creates and embeds the GUI object
    representing the group (via the `ctr` argument). Returns the parent border
    panel, and the group GUI object. Parameters:
    
    :param parent:   Parent GUI object
    :param group:    :class:`VGroup`, :class:`HGroup` or :class:`NotebookGroup`
    :param ctr:      Constructor for a :class:`wx.Window` object.
    :param args:     Passed to `ctr`. You don't need to pass in the parent.
    :param kwargs:   Passed to `ctr`.
    """
    
    borderPanel = wx.Panel(parent, style=wx.SUNKEN_BORDER)
    borderSizer = wx.BoxSizer(wx.VERTICAL)
    groupObject = ctr(borderPanel, *args, **kwargs)
    
    if group.label is not None:
        label = wx.StaticText(borderPanel, label=group.label)
        line  = wx.StaticLine(borderPanel, style=wx.LI_HORIZONTAL)
        
        font  = label.GetFont()
        font.SetPointSize(font.GetPointSize() - 2)
        font.SetWeight(wx.FONTWEIGHT_LIGHT)
        label.SetFont(font)
        
        borderSizer.Add(label, border=5, flag=wx.ALL)
        borderSizer.Add(line,  border=5, flag=wx.EXPAND | wx.ALL)
    
    borderSizer.Add(
        groupObject, border=5, flag=wx.EXPAND | wx.ALL, proportion=1)
    borderPanel.SetSizer(borderSizer)
    borderSizer.Layout()
    borderSizer.Fit(borderPanel)

    return borderPanel, groupObject
    

def _createNotebookGroup(parent, group, hasProps, propGui):
    """Creates a :class:`pwidgets.notebook.Notebook` object from the given
    :class:`NotebookGroup` object.

    The children of the group object are also created via recursive calls to
    the :func:`_create` function.
    """

    if group.border:
        borderPanel, notebook = _makeGroupBorder(
            parent, group, nb.Notebook)
    else:
        notebook = nb.Notebook(parent)
                                                 
    for i, child in enumerate(group.children):
        
        if child.label is None: pageLabel = '{}'.format(i)
        else:                   pageLabel = child.label

        if isinstance(child, Group):
            child.border = False

        page = _create(notebook, child, hasProps, propGui)
        notebook.InsertPage(i, page, pageLabel)
        page._notebookIdx = i

    notebook.SetSelection(0)
    notebook.Layout()
    notebook.Fit()

    if group.border: return borderPanel
    else:            return notebook


def _layoutHGroup(group, parent, children, labels):
    """Lays out the children (and labels, if not ``None``) of the given
    :class:`HGroup` object. Parameters:
    
    :param group:    :class:`HGroup` object
    
    :param parent:   GUI object which represents the group
    
    :param children: List of GUI objects, the children of the group.

    :param labels:   ``None`` if no labels, otherwise a list of GUI Label
                     objects, one for each child.
    """

    sizer = wx.BoxSizer(wx.HORIZONTAL)

    for cidx in range(len(children)):

        if labels is not None and labels[cidx] is not None:
            sizer.Add(labels[cidx], flag=wx.EXPAND)
                
        sizer.Add(children[cidx], flag=wx.EXPAND, proportion=1)

        # TODO I have not added support
        # for child groups with borders

    parent.SetSizer(sizer)

    
def _layoutVGroup(group, parent, children, labels):
    """Lays out the children (and labels, if not ``None``) of the
    given :class:`VGroup` object. Parameters the same as :func:`_layoutHGroup`.
    """

    sizer = wx.GridBagSizer(1, 1)
    sizer.SetEmptyCellSize((0, 0))

    for cidx in range(len(children)):

        vItem       = group.children[cidx]
        child       = children[cidx]
        label       = labels[cidx]
        childParams = {}

        # Groups within VGroups, which don't have a border, are 
        # laid out the same as any other widget, which probably
        # looks a bit ugly. If they do have a border, however, 
        # they are laid out so as to span the entire width of
        # the parent VGroup. Instead of having a separate label
        # widget, the label is embedded in the border. The
        # _createGroup function takes care of creating the
        # border/label for the child GUI object.
        if (isinstance(vItem, Group) and vItem.border):

            label = None
            childParams['pos']    = (cidx, 0)
            childParams['span']   = (1, 2)
            childParams['border'] = 20
            childParams['flag']   = wx.EXPAND | wx.ALL

        # No labels are being drawn for any child, so all
        # children should span both columns. In this case
        # we could just use a vertical BoxSizer instead of
        # a GridBagSizer,  but I'm going to leave that for
        # the time being.
        elif not group.showLabels:
            childParams['pos']    = (cidx, 0)
            childParams['span']   = (1, 2)
            childParams['border'] = 2
            childParams['flag']   = wx.EXPAND | wx.BOTTOM

        # Otherwise the child is drawn in the standard way -
        # label on the left column, child on the right.
        else:
            childParams['pos']    = (cidx, 1)
            childParams['border'] = 2
            childParams['flag']   = wx.EXPAND | wx.BOTTOM
            
        if label is not None:
            sizer.Add(labels[cidx],
                      pos=(cidx, 0),
                      flag=wx.ALIGN_CENTER_VERTICAL)
            
        sizer.Add(child, **childParams)

    sizer.AddGrowableCol(1)

    parent.SetSizer(sizer)


def _createGroup(parent, group, hasProps, propGui):
    """Creates a GUI panel object for the given :class:`HGroup` or
    :class:`VGroup`.

    Children of the group are recursively created via calls to
    :func:`_create`, and laid out via the :class:`_layoutHGroup` or
    :class:`_layoutVGroup` functions.
    """

    if group.border:
        borderPanel, panel = _makeGroupBorder(parent, group, wx.Panel)
    else:
        panel = wx.Panel(parent)

    childObjs = []
    labelObjs = []

    for i, child in enumerate(group.children):
        
        childObj = _create(panel, child, hasProps, propGui)

        # Create a label for the child if necessary
        if group.showLabels and group.childLabels[i] is not None:
            labelObj = _create(panel, group.childLabels[i], hasProps, propGui)
        else:
            labelObj = None

        labelObjs.append(labelObj) 
        childObjs.append(childObj)

    if   isinstance(group, HGroup):
        _layoutHGroup(group, panel, childObjs, labelObjs)
    elif isinstance(group, VGroup):
        _layoutVGroup(group, panel, childObjs, labelObjs)

    panel.Layout()
    panel.Fit()

    if group.border:
        borderPanel.Layout()
        borderPanel.Fit()
        return borderPanel
    else:
        return panel


# These aliases are defined so we can introspectively look
# up the appropriate _create* function based upon the class
# name of the ViewItem being created, in the _create
# function below.

_createHGroup = _createGroup
"""Alias for the :func:`_createGroup` function."""


_createVGroup = _createGroup
"""Alias for the :func:`_createGroup` function."""


def _create(parent, viewItem, hasProps, propGui):
    """Creates a GUI object for the given :class:`ViewItem` object and, if it
    is a group, all of its children.
    """

    cls = viewItem.__class__.__name__

    createFunc = getattr(sys.modules[__name__], '_create{}'.format(cls), None)

    if createFunc is None:
        raise ValueError('Unrecognised ViewItem: {}'.format(
            viewItem.__class__.__name__))

    guiObject = createFunc(parent, viewItem, hasProps, propGui)
    visibleCb = _configureVisibleWhen(viewItem, guiObject, hasProps)
    enableCb  = _configureEnabledWhen(viewItem, guiObject, hasProps)

    if visibleCb is not None: propGui.onChangeCallbacks.append(visibleCb)
    if enableCb  is not None: propGui.onChangeCallbacks.append(enableCb)

    if viewItem.tooltip is not None:

        # Add the tooltip to the GUI object, and
        # also do so recursively to any children
        def setToolTip(obj):
            
            obj.SetToolTipString(viewItem.tooltip)

            children = obj.GetChildren()
            if len(children) > 0:
                map(setToolTip, children)
        
        setToolTip(guiObject)

    propGui.guiObjects[viewItem.key] = guiObject

    return guiObject


def _defaultView(hasProps):
    """Creates a default view specification for the given
    :class:`~props.properties.HasProperties` object, with all properties
    laid out vertically. This function is only called if a view specification
    was not provided in the call to the :func:`buildGUI` function
    """

    propNames, propObjs = hasProps.getAllProperties()

    widgets = [Widget(name, label=name) for name in propNames]
    
    return VGroup(label=hasProps.__class__.__name__, children=widgets)


def _prepareView(viewItem, labels, tooltips):
    """Recursively steps through the given ``viewItem`` and its children (if
    any).

    If the ``viewItem`` is a string, it is assumed to be a property name, and
    it is turned into a :class:`Widget` object. If the ``viewItem`` does not
    have a label/tooltip, and there is a label/tooltip for it in the given
    labels/tooltips dict, then its label/tooltip is set.  Returns a reference
    to the updated/newly created :class:`ViewItem`.
    """

    if isinstance(viewItem, str):
        viewItem = Widget(viewItem)

    if not isinstance(viewItem, ViewItem):
        raise ValueError('Not a ViewItem')

    if viewItem.label   is None:
        viewItem.label   = labels  .get(viewItem.key, viewItem.key)
    if viewItem.tooltip is None:
        viewItem.tooltip = tooltips.get(viewItem.key, None) 

    if isinstance(viewItem, Group):

        # children may have been specified as a tuple,
        # so we cast it to a list, making it mutable
        viewItem.children    = list(viewItem.children)
        viewItem.childLabels = []

        for i, child in enumerate(viewItem.children):
            viewItem.children[i] = _prepareView(child, labels, tooltips)

        # Create a Label object for each 
        # child of this group if necessary
        for child in viewItem.children:

            # unless no labels are to be shown
            # for the items in this group
            mkLabel = viewItem.showLabels

            # or there is no label specified for this child
            mkLabel = mkLabel and (child.label is not None)

            # or this child is a group with a border
            mkLabel = mkLabel and \
                      not (isinstance(child, Group) and child.border)

            # unless there is no label specified
            if mkLabel: viewItem.childLabels.append(Label(child))
            else:       viewItem.childLabels.append(None)

    return viewItem

    
def _prepareEvents(hasProps, propGui):
    """If the ``visibleWhen`` or ``enabledWhen`` conditional attributes were
    set for any :class:`ViewItem` objects, a callback function is set on all
    properties. When any property value changes, the
    ``visibleWhen``/``enabledWhen`` callback functions are called.
    """

    if len(propGui.onChangeCallbacks) == 0:
        return

    def onChange(*a):
        for cb in propGui.onChangeCallbacks:
            cb()
        propGui.topLevel.Layout()
        propGui.topLevel.Refresh()
        propGui.topLevel.Update()


    propNames, propObjs = hasProps.getAllProperties()

    # initialise widget states
    onChange()

    # add a callback listener to every property
    lName = 'build_py_WhenEvent'
    for propObj, propName in zip(propObjs, propNames):
        propObj.addListener(hasProps, lName, onChange)

    def removeListeners(ev):
        for propObj, propName in zip(propObjs, propNames):
            propObj.removeListener(hasProps, lName)
        ev.Skip()

    propGui.topLevel.Bind(wx.EVT_WINDOW_DESTROY, removeListeners)
 

def buildGUI(parent,
             hasProps,
             view=None,
             labels=None,
             tooltips=None):
    """Builds a GUI interface which allows the properties of the given
    :class:`~props.properties.HasProperties` object to be edited.
    
    Returns a reference to the top level GUI object (typically a
    :class:`wx.Panel` or :class:`~pwidgets.notebook.Notebook`).

    Parameters:
    
    :param parent:   parent GUI object
    :param hasProps: :class:`~props.properties.HasProperties` object
    :param view:     :class:`ViewItem` object, specifying the interface layout
    :param labels:   Dict specifying labels
    :param tooltips: Dict specifying tooltips

    """

    if view is None:
        if hasattr(hasProps, '_view'):     view = hasProps._view
        else:                              view = _defaultView(hasProps)
    if labels is None:
        if hasattr(hasProps, '_labels'):   labels = hasProps._labels
        else:                              labels = {}
    if tooltips is None:
        if hasattr(hasProps, '_tooltips'): tooltips = hasProps._tooltips
        else:                              tooltips = {}

    propGui   = PropGUI()
    view      = _prepareView(view, labels, tooltips) 
    mainPanel = _create(parent, view, hasProps, propGui)
    
    propGui.topLevel = mainPanel
    _prepareEvents(hasProps, propGui)

    # TODO return the propGui object, so the caller
    # has access to all of the GUI objects that were
    # created, via the propGui.guiObjects dict. ??

    return mainPanel


def buildDialog(parent,
                hasProps,
                view=None,
                labels=None,
                tooltips=None):
    """Convenience method which embeds the result of a call to
    :func:`buildGUI` in a :class:`wx.Dialog`.

    See the :func:`buildGUI` documentation for details on the paramters.
    """
    
    dialog = wx.Dialog(parent, style=wx.DEFAULT_DIALOG_STYLE |
                                     wx.RESIZE_BORDER)
    panel  = buildGUI(dialog, hasProps, view, labels, tooltips)

    sizer = wx.BoxSizer(wx.VERTICAL)
    dialog.SetSizer(sizer)

    sizer.Add(panel, flag=wx.EXPAND, proportion=1)

    dialog.Layout()
    dialog.Fit()

    return dialog
