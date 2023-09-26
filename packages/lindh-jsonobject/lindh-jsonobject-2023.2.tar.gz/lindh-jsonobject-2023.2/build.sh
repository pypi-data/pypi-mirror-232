#!/bin/bash

set -e

if [ -d dist ]; then
    rm -rf dist
fi
if [ -d build ]; then
    rm -rf build
fi
if [ -d lindh_jsonobjecy.egg-info ]; then
    rm -rf lindh_jsonobjecy.egg-info
fi

python -m build
#python -m twine upload dist/*
