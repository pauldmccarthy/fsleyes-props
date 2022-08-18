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

class Context:
    pass


def test_listener():

    ctx    = Context()
    pv     = properties_value.PropertyValue(ctx)
    called = {}

    # TODO Test args passed to listener

    def l1(*a):
        called['l1'] = called.get('l1', 0) + 1

    def l2():
        called['l2'] = called.get('l2', 0) + 1

    def l3(a, b, c, d):
        called['l3'] = called.get('l3', 0) + 1

    def l7(a, b, *rest):
        called['l7'] = called.get('l7', 0) + 1

    def al1(*a):
        called['al1'] = called.get('al1', 0) + 1

    def al2():
        called['al2'] = called.get('al2', 0) + 1

    def al3(a, b, c, d):
        called['al3'] = called.get('al3', 0) + 1

    def al7(a, b, *rest):
        called['al7'] = called.get('al7', 0) + 1

    class ListenerObj:

        def l4(self, *a):
            called['l4'] = called.get('l4', 0) + 1

        def l5(self):
            called['l5'] = called.get('l5', 0) + 1

        def l6(self, a, b, c, d):
            called['l6'] = called.get('l6', 0) + 1

        def al4(self, *a):
            called['al4'] = called.get('al4', 0) + 1

        def al5(self):
            called['al5'] = called.get('al5', 0) + 1

        def al6(self, a, b, c, d):
            called['al6'] = called.get('al6', 0) + 1

    lobj = ListenerObj()

    pv.addListener(         'l1',  l1)
    pv.addListener(         'l2',  l2)
    pv.addListener(         'l3',  l3)
    pv.addListener(         'l4',  lobj.l4)
    pv.addListener(         'l5',  lobj.l5)
    pv.addListener(         'l6',  lobj.l6)
    pv.addListener(         'l7',  l7)

    pv.addAttributeListener('al1', al1)
    pv.addAttributeListener('al2', al2)
    pv.addAttributeListener('al3', al3)
    pv.addAttributeListener('al4', lobj.al4)
    pv.addAttributeListener('al5', lobj.al5)
    pv.addAttributeListener('al6', lobj.al6)
    pv.addAttributeListener('al7', al7)

    listeners    = ['l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7']
    attListeners = ['al1', 'al2', 'al3', 'al4', 'al5', 'al6', 'al7']

    for l in listeners:
        assert pv.hasListener(l)

    pv.set('New value')
    for l in listeners:
        assert called[l] == 1

    # value unchanged, notification should not take place
    pv.set('New value')
    for l in listeners:
        assert called[l] == 1

    pv.set('New new value')
    for l in listeners:
        assert called[l] == 2

    for l in attListeners:
        assert called.get(l) is None

    pv.setAttribute('newAtt', 'value')
    for l in attListeners:
        assert called[l] == 1

    pv.setAttribute('newAtt', 'value')
    for l in attListeners:
        assert called[l] == 1

    pv.setAttribute('newAtt', 'new value')
    for l in attListeners:
        assert called[l] == 2
