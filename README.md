Props
=====

The props package uses 
[python descriptors](http://nbviewer.ipython.org/gist/ChrisBeaumont/5758381/descriptor_writeup.ipynb)
to implement an event programming framework. It also includes the ability for 
automatic CLI generation and, optionally, automatic GUI generation (if 
[wxPython](http://www.wxpython.org) is present).


Documentation
-------------


Developer documentation is available at
http://users.fmrib.ox.ac.uk/~paulmc/props/index.html. Dependencies are listed
in [requirements.txt](requirements.txt).


``props`` is documented using [sphinx](http://http://sphinx-doc.org/). The
documentation can be built by running the following command from the
``props/doc`` directory:


```sh
rm -r html; PYTHONPATH=.. sphinx-build . html
```


The generated documentation can then be viewed by opening
``doc/html/index.html`` in a web browser.


Example usage
-------------


```python
>>> import props

>>> class PropObj(props.HasProperties):
>>>     myProperty = props.Boolean()

>>> myPropObj = PropObj()


# Access the property value as a normal attribute:
>>> myPropObj.myProperty = True
>>> myPropObj.myProperty
>>> True


# access the props.Boolean instance:
>>> myPropObj.getProp('myProperty')
>>> <props.prop.Boolean at 0x1045e2710>


# access the underlying props.PropertyValue object
# (there are caveats for List properties):
>>> myPropObj.getPropVal('myProperty')
>>> <props.prop.PropertyValue instance at 0x1047ef518>


# Receive notification of property value changes
>>> def myPropertyChanged(value, *args):
>>>     print('New property value: {}'.format(value))

>>> myPropObj.addListener(
>>>    'myProperty', 'myListener', myPropertyChanged)

>>> myPropObj.myProperty = False
>>> New property value: False


# Remove a previously added listener
>>> myPropObj.removeListener('myListener')
```
