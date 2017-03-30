#!/usr/bin/env python
#
# setup.py - setuptools configuration for installing the props package.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import os.path as op


from setuptools               import setup
from setuptools               import find_packages


basedir = op.dirname(__file__)

install_requires = open(op.join(basedir, 'requirements.txt'), 'rt').readlines()


# Extract the vesrion number from props/__init__.py
version = {}
with open(op.join(basedir, "props", "__init__.py")) as f:
    for line in f:
        if line.startswith('__version__'):
            exec(line, version)
            break

setup(

    name='props',

    version=version.get('__version__'),

    description='Python descriptor framework',

    url='https://git.fmrib.ox.ac.uk/paulmc/props',


    author='Paul McCarthy',

    author_email='pauldmccarthy@gmail.com',

    license='Apache License Version 2.0',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules'],

    packages=find_packages(exclude=('doc', 'tests')),

    install_requires=install_requires
)
