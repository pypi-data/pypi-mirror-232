#!/bin/bash -e
# Usage
#   $ ./scripts/run_tests.sh
# or
#   $ ./scripts/run_tests.sh --cov lindh --cov-report html
#python -m pytest --doctest-modules --pep8 --flakes $@
python3 -m pytest --pep8 --flakes -v $@
python3 -m doctest README.rst
python3 -m rstcheck README.rst
