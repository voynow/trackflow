#!/bin/bash

rm -rf package
rm -f function.zip

poetry export -f requirements.txt --output requirements.txt --without-hashes
pip install --target ./package -r requirements.txt

cd package || exit
zip -r ../function.zip .
cd ..

cp src/lambda_function.py .
zip -g function.zip lambda_function.py
rm lambda_function.py
