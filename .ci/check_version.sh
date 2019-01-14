#!/bin/bash
####################################################
# The check_version script is run on release builds,
# and makes sure that the version in the code is up
# to date (i.e. equal to the tag name).
####################################################

set -e

cat fsleyes_props/__init__.py | egrep "^__version__ += +'$CI_COMMIT_REF_NAME' *$"
