#!/bin/bash

# Check if Docker is running, and start it if not
if ! docker info >/dev/null 2>&1; then
    echo "Starting Docker..."
    open --background -a Docker
    while ! docker info >/dev/null 2>&1; do
        sleep 1
    done
    echo "Docker started."
fi

# Build and push the image
poetry export --without-hashes -f requirements.txt -o requirements.txt
docker build -t trackflow .
docker tag trackflow:latest 498969721544.dkr.ecr.us-east-1.amazonaws.com/trackflow:latest
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 498969721544.dkr.ecr.us-east-1.amazonaws.com
docker push 498969721544.dkr.ecr.us-east-1.amazonaws.com/trackflow:latest

# Get the image digest
image_digest=$(aws ecr describe-images \
    --repository-name trackflow \
    --image-ids imageTag=latest \
    --query 'imageDetails[0].imageDigest' \
    --output text)

# Update the image in the Terraform variables
cd ../infra/app
sed -i '' "s|^image = .*|image = \"498969721544.dkr.ecr.us-east-1.amazonaws.com/trackflow@$image_digest\"|" terraform.tfvars
terraform apply -auto-approve

# Return to the api folder
cd ../../api
