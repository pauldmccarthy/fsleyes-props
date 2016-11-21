#!/usr/bin/env python
#
# setup.py - setuptools configuration for installing the props package.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import            os 
import os.path as op


from setuptools               import setup
from setuptools               import find_packages
from setuptools.command.sdist import sdist


class fsl_sdist(sdist):
    """Custom sdist command which inserts the LICENSE text at the
    beginning of every source file.
    """

    def make_distribution(self):

        # Force distutils.command.sdist to copy
        # files instead of hardlinking them. This
        # hack is performed by setuptools >= 24.3.0,
        # but is not done by earlier versions. 
        link = getattr(os, 'link', None)
        try:
            del(os.link)
        except:
            pass
        
        sdist.make_distribution(self)

        if link is not None:
            os.link = link
    
    def make_release_tree(self, base_dir, files):

        # Make the release tree
        sdist.make_release_tree(self, base_dir, files)

        licence = op.abspath('LICENSE')

        if not op.exists(licence):
            return

        with open(licence, 'rt') as f:
            licence = f.read()

        patchfuncs = {

            '.py' : self.__patch_py_file,
        }

        # Walk through the release 
        # tree, and patch the license 
        # into every relevant file.
        for root, dirs, files in os.walk(base_dir):
            for filename in files:

                filename  = op.join(root, filename)
                ext       = op.splitext(filename)[1]
                patchfunc = patchfuncs.get(ext)

                if patchfunc is not None:
                    patchfunc(filename, licence)


    def __patch_py_file(self, filename, licence):

        licence = licence.split('\n')
        licence = ['# {0}'.format(l) for l in licence]

        with open(filename, 'rt') as f:
            lines = f.read().split('\n')

        # Remove any existing hashbang line
        if len(lines) > 0 and lines[0].startswith('#!'):
            lines = lines[1:]

        # Insert the fsl hashbang and the licence
        lines = ['#!/usr/bin/env fslpython'] + ['#'] + licence + lines
        lines = ['{0}\n'.format(l) for l in lines]

        with open(filename, 'wt') as f:
            f.writelines(lines)

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

    license='FMRIB',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: Free for non-commercial use',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules'],

    packages=find_packages(exclude=('doc')),

    cmdclass={'fsl_sdist' : fsl_sdist},

    install_requires=install_requires
)
