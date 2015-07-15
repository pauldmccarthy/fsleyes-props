#!/usr/bin/env python
#
# callqueue.py - A queue for calling functions sequentially.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""The :mod:`callqueue` module provides the :class:`CallQueue` class, which
is used by :class:`~props.properties_value.PropertyValue` objects to enqueue
property listener callback functions.
"""

import logging
log = logging.getLogger(__name__)

import Queue
import inspect
import traceback


class Call(object):
    """A little class which is used to represent function calls that are
    on the queue.
    """

    def __init__(self, func, name, args):
        self.func    = func
        self.name    = name
        self.args    = args
        self.execute = True

        # The CallQueue.dequeue method sets the
        # above execute attribute to False for
        # calls which are to be dequeued - this
        # causees the CallQueue.__call method
        # to skip over the call.


class CallQueue(object):
    """A queue of functions to be called. Functions can be enqueued via
    the :meth:`call` or :meth:`callAll` methods.
    """

    def __init__(self, skipDuplicates=False):
        """Create a :class:`CallQueue` instance.

        If ``skipDuplicates`` is ``True``, a function which is already on
        the queue will be silently dropped if an attempt is made to add it
        again.
        """

        # The queue is a queue of Call instances
        # 
        # The queued dict contains mappings of
        # {name : [List of Call instances]}
        # 
        self.__queue          = Queue.Queue()
        self.__queued         = {}
        self.__skipDuplicates = skipDuplicates
        self.__calling        = False


    def dequeue(self, name):
        """If the specified function is on the queue, it is (effectively)
        dequeued, and not executed.

        If ``skipDuplicates`` is ``False``, and more than one function of
        the same name is enqueued, they are all dequeued.
        """

        # Get all calls with the specified name
        calls = self.__queued.get(name, [])

        # Set each of their execute flags to
        # False - the __call method will skip
        # over Call instances with execute=False
        for call in calls:

            self.__debug(call, 'Dequeueing function', 'from queue')
            call.execute = False
        

    def call(self, func, name, args):
        """Enqueues the given function, and calls all functions in the queue
        
        (unless the call to this method was as a result another function
        being called from the queue).
        """

        if self.__push(Call(func, name, args)):
            self.__call()


    def callAll(self, funcs):
        """Enqueues all of the given functions, and calls all functions in
        the queue.
        
        (unless the call to this method was as a result another function
        being called from the queue).

        Assumes that the given ``funcs`` parameter is a list of 
        ``(function, name, arguments)`` tuples.
        """
        
        anyEnqueued = False
        
        for func in funcs:
            if self.__push(Call(*func)):
                anyEnqueued = True

        if anyEnqueued:
            self.__call()

        
    def __call(self):
        """Call all of the functions which are currently enqueued.

        This method is not re-entrant - if a call to one of the
        functions in the queue triggers another call to this method,
        this second call will return immediately without doing anything.
        """

        if self.__calling: return
        self.__calling = True

        while True:

            try:
                call = self.__pop()

                if not call.execute:
                    self.__debug(call, 'Skipping dequeued function')
                    continue

                self.__debug(call, 'Calling function')

                try:
                    call.func(*call.args)
                
                except Exception as e:
                    log.warn('Function {} raised exception: {}'.format(
                        call.name, e), exc_info=True)
                    traceback.print_stack()
                    
            except Queue.Empty:
                break
            
        self.__calling = False


    def __push(self, call):
        """Enqueues the given ``Call`` instance.

        If ``True`` was passed in for the ``skipDuplicates`` parameter
        during initialisation, and the function is already enqueued,
        it is not added to the queue, and this method returns ``False``.

        Otherwise, this method returnes ``True``.
        """

        funcName, modName = self.__getCallbackDetails(call.func)
        enqueued          = self.__queued.get(call.name, [])

        # I'm only taking into account the call
        # name when checking for duplicates, meaning
        # that the callqueue does not support
        # enqueueing the same function with different
        # arguments.
        #
        # I can't take the hash of the arguments, as
        # I can't assume that they are hashable (e.g.
        # numpy arrays).
        #
        # I can't test for identity, as things which
        # have the same value may not have the same
        # id (e.g. strings).
        #
        # I can't test argument equality, because in
        # some cases the argument may be a mutable
        # type, and its value may have changed between
        # the time the function was queued, and the
        # time it is called.
        # 
        # So this is quite a pickle. Something to come
        # back to if things are breaking because of it.
        
        if self.__skipDuplicates and (len(enqueued) > 0):
            self.__debug(call, 'Skipping function')
            return False

        self.__debug(call, 'Queueing function', 'to queue')

        self.__queue.put_nowait(call)
        self.__queued[call.name] = enqueued + [call]
        
        return True

    
    def __pop(self):
        """Pops the next function from the queue and returns a 3-tuple
        containing the function description, the function, and the arguments
        to be passed to it.
        """

        call     = self.__queue.get_nowait()
        enqueued = self.__queued[call.name]

        # TODO shouldn't the call always
        # be at the end of the list?
        # 
        # This will be a little bit faster
        # if you remove the call by index.
        enqueued.remove(call)
        
        if len(enqueued) == 0:
            self.__queued.pop(call.name)
            
        return call


    def __debug(self, call, prefix, postfix=None):
        
        if log.getEffectiveLevel() != log.DEBUG:
            return

        funcName, modName = self.__getCallbackDetails(call.func)

        if postfix is None: postfix = ' '
        else:               postfix = ' {} '.format(postfix)
            
        log.debug('{} {} [{}.{}]{}({} in queue)'.format(
            prefix,
            call.name,
            modName,
            funcName,
            postfix,
            self.__queue.qsize()))


    def __getCallbackDetails(self, cb):
        """Returns the function name and module name of the given
        function reference. Used purely for debug log statements.
        """

        if log.getEffectiveLevel() != logging.DEBUG:
            return '', ''

        members = inspect.getmembers(cb)

        funcName  = ''
        modName   = ''

        for name, val in members:
            if name == '__func__':
                funcName  = val.__name__
                modName   = val.__module__
                break

        return funcName, modName
