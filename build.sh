#!/bin/bash

rm -rf package
rm function.zip

poetry export -f requirements.txt --output requirements.txt --without-hashes
pip install --target ./package -r requirements.txt

cd package
zip -r ../function.zip .
cd ..
zip -g function.zip src/lambda_function.py
