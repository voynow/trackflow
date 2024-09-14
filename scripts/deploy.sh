#!/bin/bash

set -e

AWS_REGION="us-east-1"
FUNCTION_NAME="strava"

# Step 1: Ensure Poetry's virtual environment is activated
echo "Activating Poetry environment..."
poetry install
POETRY_VENV_PATH=$(poetry env info --path)
export PATH="$POETRY_VENV_PATH/bin:$PATH"

# Step 2: Build the project and package dependencies
echo "Building the project and packaging dependencies..."
./scripts/build.sh

# Step 3: Deploy to AWS Lambda
echo "Deploying to AWS Lambda function: $FUNCTION_NAME"
aws lambda update-function-code \
  --function-name $FUNCTION_NAME \
  --zip-file fileb://function.zip \
  --region $AWS_REGION

echo "Deployment complete."

# Clean up
rm -rf package
rm -f function.zip
