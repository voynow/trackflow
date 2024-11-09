

docker build -t trackflow .
docker tag trackflow:latest 498969721544.dkr.ecr.us-east-1.amazonaws.com/trackflow:latest
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 498969721544.dkr.ecr.us-east-1.amazonaws.com
docker push 498969721544.dkr.ecr.us-east-1.amazonaws.com/trackflow:latest

