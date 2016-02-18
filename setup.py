#!/usr/bin/env python
#
# setup.py - setuptools configuration for installing the props package.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

from setuptools import setup
from setuptools import find_packages


setup(

    name='props',

    version='0.0',

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

    install_requires=[
        'matplotlib>=1.3',
        'numpy>=1.8']
)
