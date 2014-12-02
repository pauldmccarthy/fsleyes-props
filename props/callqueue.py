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
import inspect
import traceback

def _getCallbackDetails(cb):
    
    members = inspect.getmembers(cb)

    funcName  = ''
    modName   = ''

    for name, val in members:
        if name == '__func__':
            funcName  = val.__name__
            modName   = val.__module__
            break

    return funcName, modName



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

                funcName, modName = _getCallbackDetails(func)

                log.debug('Calling listener {} [{}.{}] ({} in queue)'.format(
                    desc, modName, funcName, self._queue.qsize()))

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

        funcName, modName = _getCallbackDetails(func)
        log.debug('Adding listener {} [{}.{}] to queue ({} in queue)'.format(
            desc, modName, funcName, self._queue.qsize())) 
        self._queue.put_nowait((desc, func, args))
        self._call()


    def callAll(self, funcs):
        """
        """
        for func in funcs:
            desc, func, args = func
            funcName, modName = _getCallbackDetails(func)
            log.debug('Adding listener {} [{}.{}] to queue ({} in queue)'.format(
                desc, modName, funcName, self._queue.qsize())) 
            
            self._queue.put_nowait((desc, func, args))
        self._call()


queue = CallQueue()
