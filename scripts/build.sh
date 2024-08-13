#!/bin/bash

rm -rf package
rm -f function.zip

poetry export -f requirements.txt --output requirements.txt --without-hashes
pip install --target ./package -r requirements.txt

cd package || exit
zip -r ../function.zip .
cd ..

zip -r function.zip src 