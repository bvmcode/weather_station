#!/bin/sh
rds_address=`cat ./prod/rds_host.txt`
cp ./prod/.env_tmp ./prod/.env
echo $rds_address >> ./prod/.env
ecr_address=`cat ./scripts/ecr_address.txt`
echo $ecr_address > ./scripts/preserve_ecr_address.txt
aws --region us-east-1 ecr get-login-password --profile wx_deploy | docker login --username AWS --password-stdin $ecr_address
docker build --platform linux/amd64 -t $ecr_address ./prod
docker push $ecr_address