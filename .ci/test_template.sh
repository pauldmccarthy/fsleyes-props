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

pip install -r requirements-dev.txt
pip install git+https://git.fmrib.ox.ac.uk/fsl/fslpy.git
pip install git+https://git.fmrib.ox.ac.uk/fsl/fsleyes/widgets.git
cat requirements.txt | grep -v "fsl" > ci-requirements.txt
pip install -r ci-requirements.txt


# style stage
if [ "$TEST_STYLE"x != "x" ]; then pip install pylint flake8; fi;
if [ "$TEST_STYLE"x != "x" ]; then flake8                           fsleyes_props || true; fi;
if [ "$TEST_STYLE"x != "x" ]; then pylint --output-format=colorized fsleyes_props || true; fi;
if [ "$TEST_STYLE"x != "x" ]; then exit 0; fi

# Run the tests
xvfb-run python setup.py test
