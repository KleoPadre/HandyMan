#!/bin/bash

# Cleaning previous builds
rm -rf build dist

# Building application in debug mode
python setup.py py2app -A

echo "Debug build completed. Run the application using:"
echo "dist/HandyMan.app/Contents/MacOS/HandyMan"
