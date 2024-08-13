#!/bin/bash

# Clean up any previous builds
rm -rf package
rm -f function.zip

# Export dependencies and install them into the package directory
poetry export -f requirements.txt --output requirements.txt --without-hashes
pip install --target ./package -r requirements.txt

# Navigate to the package directory and zip its contents
cd package || exit
zip -r ../function.zip .
cd ..

# Zip the contents of the src directory directly into the function.zip
cd src || exit
zip -r ../function.zip .  # Note the dot here to include the contents, not the directory itself
cd ..