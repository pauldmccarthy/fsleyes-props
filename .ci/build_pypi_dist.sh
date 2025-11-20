#!/bin/bash

set -e

pip install --upgrade pip wheel setuptools twine build packaging
python -m build
twine check dist/*

PIPARGS="--retries 10 --timeout 30"

pip install dist/*.whl
pip uninstall -y fsleyes-props

pip install dist/*.tar.gz
pip uninstall -y fsleyes-props
