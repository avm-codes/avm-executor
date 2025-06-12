#!/bin/bash
# build and push the container to your own ECR repository

source .env

aws ecr get-login-password --region eu-north-1 \
  | podman login --username AWS \
  --password-stdin $ECR_BASE

podman build -t $CONTAINER_NAME .

podman tag $CONTAINER_NAME:latest \
  $ECR_BASE$ECR_REPOSITORY

podman push $ECR_BASE$ECR_REPOSITORY