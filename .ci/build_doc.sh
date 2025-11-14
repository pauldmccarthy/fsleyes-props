#!/bin/bash

set -e

micromamba activate /test.env

pip install ".[doc]"

sphinx-build doc public
