#!/usr/bin/env bash
####################################################
# The check_version script is run on release builds,
# and makes sure that the version in the code is up
# to date (i.e. equal to the tag name).
####################################################

set -e

source /test.venv/bin/activate
pip install  dist/*.whl

exp=${CI_COMMIT_REF_NAME}
got=$(python -c "import fsleyes_props as p;print(p.__version__)")

if [[ ${exp} == ${got} ]]; then
  exit 0
else
  exit 1
fi
