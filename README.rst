fsleyes-props
=============


.. image:: https://git.fmrib.ox.ac.uk/fsl/fsleyes/props/badges/master/build.svg
   :target: https://git.fmrib.ox.ac.uk/fsl/fsleyes/props/commits/master/

.. image:: https://git.fmrib.ox.ac.uk/fsl/fsleyes/props/badges/master/coverage.svg
   :target: https://git.fmrib.ox.ac.uk/fsl/fsleyes/props/commits/master/

.. image:: https://img.shields.io/pypi/v/fsleyes-props.svg
   :target: https://pypi.python.org/pypi/fsleyes-props/

.. image:: https://anaconda.org/conda-forge/fsleyes-props/badges/version.svg
   :target: https://anaconda.org/conda-forge/fsleyes-props


``fsleyes-props`` is a library which is used by used by `FSLeyes
<https://git.fmrib.ox.ac.uk/fsl/fsleyes/fsleyes>`_, and which allows you to:

  - Listen for change to attributes on a python object,

  - Automatically generate ``wxpython`` widgets which are bound
    to attributes of a python object

  - Automatically generate a command line interface to set
    values of the attributes of a python object.


To do this, you just need to subclass the ``fsleyes)props.HasProperties``
class (also available as ``fsleyes_props.Props``), and add some
``PropertyBase`` types as class attributes.


Installation
------------


You can install ``fsleyes-props`` via pip. If you are using Linux, you need to
install wxPython first, as binaries are not available on PyPI. Change the URL
for your specific platform::

    pip install -f https://extras.wxpython.org/wxPython4/extras/linux/gtk2/ubuntu-16.04/ wxpython


Then install ``fsleyes-props`` like so::

    pip install fsleyes-props


``fsleyes-props`` is also available on
`conda-forge <https://conda-forge.org/>`_::

    conda install -c conda-forge fsleyes-props


Dependencies
------------


All of the dependencies of ``fsleyes-props`` are listed in the
`requirements.txt <requirements.txt>`_ file. ``fsleyes-props`` can be used
without wxPython, but GUI functionality will not be available.


Dependencies for running the tests and building documentation are listed in the
`requirements-dev.txt <requirements-dev.txt>`_ file.


Documentation
-------------

The ``fsleyes-props`` API documentation is hosted at
https://open.win.ox.ac.uk/pages/fsl/fsleyes/props/.

``fsleyes-props`` is documented using `sphinx
<http://http://sphinx-doc.org/>`_. You can build the API documentation by
running::

    pip install -r requirements-dev.txt
    python setup.py doc

The HTML documentation will be generated and saved in the ``doc/html/``
directory.


Tests
-----

Run the test suite via::

    pip install -r requirements-dev.txt
    python setup.py test


Many of the tests assume that a display is accessible - if you are running on
a headless machine, you may need to run the tests using ``xvfb-run``.


Example usage
-------------


.. code-block:: python

    >>> import fsleyes_props as props
    >>>
    >>> class PropObj(props.Props):
    >>>     myProperty = props.Boolean()
    >>>
    >>> myPropObj = PropObj()
    >>>
    >>> # Access the property value as a normal attribute:
    >>> myPropObj.myProperty = True
    >>> myPropObj.myProperty
    True
    >>>
    >>> # Receive notification of property value changes
    >>> def myPropertyChanged(value, *args):
    >>>     print(f'New property value: {value}')
    >>>
    >>> myPropObj.listen('myProperty', 'myListener', myPropertyChanged)
    >>>
    >>> myPropObj.myProperty = False
    New property value: False
    >>>
    >>> # Remove a previously added listener
    >>> myPropObj.remove('myListener')


Contributing
------------

If you would like to contribute to ``fsleyes-props``, take a look at the
``fslpy`` `contributing guide
<https://git.fmrib.ox.ac.uk/fsl/fslpy/blob/master/doc/contributing.rst>`_.
