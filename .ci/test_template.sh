#!/bin/bash

source /test.venv/bin/activate

# If running on a fork repository, we merge in the
# upstream/master branch. This is done so that merge
# requests from fork to the parent repository will
# have unit tests run on the merged code, something
# which gitlab CE does not currently do for us.
if [[ "$CI_PROJECT_PATH" != "$UPSTREAM_PROJECT" ]]; then
  git fetch upstream;
  git merge --no-commit --no-ff upstream/master;
fi;

pip install --retries 10 -r requirements-dev.txt

wget https://git.fmrib.ox.ac.uk/fsl/fslpy/-/archive/master/fslpy-master.tar.bz2
wget https://git.fmrib.ox.ac.uk/fsl/fsleyes/widgets/-/archive/master/widgets-master.tar.bz2

tar xf fslpy-master.tar.bz2   && pushd fslpy-master   && pip install . && popd
tar xf widgets-master.tar.bz2 && pushd widgets-master && pip install . && popd

cat requirements.txt | grep -v "fsl" > requirements-ci.txt
pip install --retries 10 -r requirements-ci.txt

# style stage
if [ "$TEST_STYLE"x != "x" ]; then pip install --retries 10 pylint flake8; fi;
if [ "$TEST_STYLE"x != "x" ]; then flake8                           fsleyes_props || true; fi;
if [ "$TEST_STYLE"x != "x" ]; then pylint --output-format=colorized fsleyes_props || true; fi;
if [ "$TEST_STYLE"x != "x" ]; then exit 0; fi

# Run the tests
xvfb-run python setup.py test
