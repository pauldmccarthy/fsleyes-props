#!/bin/bash

set -e

source /test.venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt
python setup.py doc
mkdir -p public
mv doc/html/* public/
