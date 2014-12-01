#!/usr/bin/env python
#
# callqueue.py - A queue for calling functions sequentially.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""The :mod:`callqueue` module provides a single instance of a
:class:`CallQueue` object, which is used by 
:class:`~props.properties_value.PropertyValue` objects to enqueue
property listeners.
"""

import logging
log = logging.getLogger(__name__)

import Queue
import traceback


class CallQueue(object):
    """
    """

    def __init__(self):

        self._queue   = Queue.Queue()
        self._calling = False

        
    def _call(self):
        """
        """

        if self._calling: return
        self._calling = True

        while True:

            try:
                desc, func, args = self._queue.get_nowait()

                log.debug('Calling listener {}'.format(desc))

                try: func(*args)
                except Exception as e:
                    log.warn('Listener {} raised exception: {}'.format(
                        desc, e), exc_info=True)
                    traceback.print_stack()
            except Queue.Empty:
                break

        self._calling = False 


    def call(self, desc, func, *args):
        """
        """
        self._queue.put_nowait((desc, func, args))
        self._call()


    def callAll(self, funcs):
        """
        """
        for func in funcs:
            desc, func, args = func
            self._queue.put_nowait((desc, func, args))
        self._call()


queue = CallQueue()
