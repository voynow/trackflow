#!/bin/bash

rm -rf package
rm -f function.zip

poetry export -f requirements.txt --output requirements.txt --without-hashes
pip install --target ./package -r requirements.txt

cd package || exit
zip -r ../function.zip .
cd ..

cp src/training_week_generation/lambda_function.py .
zip -g function.zip training_week_generation/lambda_function.py
zip -r function.zip src -x "src/training_week_generation/lambda_function.py"
rm training_week_generation/lambda_function.py
