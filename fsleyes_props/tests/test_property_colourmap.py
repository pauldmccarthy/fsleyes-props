#!/usr/bin/env python
#
# test_property_colourmap.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import                      wx
import numpy             as np
import matplotlib.colors as colors
import matplotlib        as mpl

import fsleyes_props as props

from . import run_with_wx, addall, realYield


# "cool" is assumed to already be registered with mpl
custom_cmaps = ['custom1', 'custom2', 'custom_cool']


def setup_module():
    props.initGUI()

    colours    = np.zeros((2, 3), dtype=np.float32)
    colours[0] = [0, 0, 0]
    colours[1] = [1, 1, 1]

    # "cool" is assumed to already be registered with mpl
    custom_cmaps = ['custom1', 'custom2', 'custom_cool']

    for key in custom_cmaps:
        cmap = colors.ListedColormap(colours, name=key)
        mpl.colormaps.register(cmap, name=key, force=True)



class MyObj(props.HasProperties):

    cmap1 = props.ColourMap()
    cmap2 = props.ColourMap(cmaps=custom_cmaps + ['hot', 'viridis', 'cool'])
    cmap3 = props.ColourMap(prefix='custom_')


def test_assignment():

    obj = MyObj()

    obj.cmap1 = 'custom1'
    obj.cmap2 = 'custom1'
    obj.cmap3 = 'custom1'

    assert isinstance(obj.cmap1, colors.ListedColormap)
    assert isinstance(obj.cmap2, colors.ListedColormap)
    assert isinstance(obj.cmap3, colors.ListedColormap)

    obj.cmap1 = 'jet'
    obj.cmap2 = 'jet'
    obj.cmap3 = 'jet'

    assert isinstance(obj.cmap1, colors.LinearSegmentedColormap)
    assert isinstance(obj.cmap2, colors.LinearSegmentedColormap)
    assert isinstance(obj.cmap3, colors.LinearSegmentedColormap)

    obj.cmap1 = 'cool'
    obj.cmap2 = 'cool'
    obj.cmap3 = 'cool'

    assert isinstance(obj.cmap1, colors.LinearSegmentedColormap)
    assert isinstance(obj.cmap2, colors.LinearSegmentedColormap)
    assert isinstance(obj.cmap3, colors.ListedColormap)
    assert            obj.cmap3.name == 'custom_cool'



def  test_widget_colourmap(): run_with_wx(_test_widget_colourmap)
def _test_widget_colourmap(parent):

    obj   = MyObj()
    cmap2 = props.makeWidget(parent, obj, 'cmap2')

    addall(parent, [cmap2])
    realYield()
