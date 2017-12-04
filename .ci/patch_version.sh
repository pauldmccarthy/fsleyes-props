#!/bin/bash
####################################################
# The patch_version script is run on release builds,
# and makes sure that the version in the code is up
# to date (i.e. equal to the tag name).
####################################################

if [[ "x$CI_COMMIT_TAG" != "x" ]]; then
    echo "Release detected - patching version - $CI_COMMIT_REF_NAME";
    sed -ie "s/^__version__ = .*$/__version__ = '$CI_COMMIT_REF_NAME'/g" fsleyes_props/__init__.py;
fi
