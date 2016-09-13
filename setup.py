#!/usr/bin/env python
#
# setup.py - setuptools configuration for installing the props package.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import os.path as op

from setuptools import setup
from setuptools import find_packages

import props

basedir = op.dirname(__file__)

install_requires = open(op.join(basedir, 'requirements.txt'), 'rt').readlines()

setup(

    name='props',

    version=props.__version__,

    description='Python descriptor framework',

    url='https://git.fmrib.ox.ac.uk/paulmc/props',


    author='Paul McCarthy',

    author_email='pauldmccarthy@gmail.com',

    license='FMRIB',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: Free for non-commercial use',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules'],

    packages=find_packages(exclude=('doc')),

    install_requires=install_requires
)
