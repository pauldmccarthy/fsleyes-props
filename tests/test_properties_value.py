#!/usr/bin/env python
#
# test_propertyvalue.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import fsleyes_props.properties_value as properties_value

import logging

logging.basicConfig()
logging.getLogger('fsleyes_props').setLevel(logging.DEBUG)

class Context():
    pass


def test_listener():

    ctx    = Context()
    pv     = properties_value.PropertyValue(ctx)
    called = {}

    # TODO Test args passed to listener

    def l1(*a):
        called['l1'] = called.get('l1', 0) + 1

    def l2(*a):
        called['l2'] = called.get('l2', 0) + 1

    pv.addListener('l1', l1)
    pv.addListener('l2', l2)

    assert pv.hasListener('l1')
    assert pv.hasListener('l2')

    pv.set('New value')

    assert called['l1'] == 1
    assert called['l2'] == 1
