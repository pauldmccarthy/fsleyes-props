#!/usr/bin/env python
#
# test_hasprops.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import fsleyes_props as props


# fsl/fsleyes/props!63
def test_self_reference():

    class Thing(props.HasProps):
        ref = props.Object()

    t = Thing()

    vals = [None, 123, 'abc', t]

    for v in vals:
        t.ref = v
        print(t)
