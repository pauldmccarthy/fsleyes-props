#!/bin/bash

micromamba activate /test.env

apt install -y locales
locale-gen en_US.UTF-8
locale-gen en_GB.UTF-8
update-locale

pip install ".[test,style]"

# install latest versions of fslpy/widgets
wget https://git.fmrib.ox.ac.uk/fsl/fslpy/-/archive/main/fslpy-main.tar.bz2
wget https://git.fmrib.ox.ac.uk/fsl/fsleyes/widgets/-/archive/master/widgets-master.tar.bz2
tar xf fslpy-main.tar.bz2     && pushd fslpy-main     && pip install . && popd
tar xf widgets-master.tar.bz2 && pushd widgets-master && pip install . && popd

# style stage
if [ "$TEST_STYLE"x != "x" ]; then flake8                           fsleyes_props || true; fi;
if [ "$TEST_STYLE"x != "x" ]; then pylint --output-format=colorized fsleyes_props || true; fi;
if [ "$TEST_STYLE"x != "x" ]; then exit 0;                                                 fi

# Run the tests
xvfb-run -a -s "-screen 0 1920x1200x24" pytest
