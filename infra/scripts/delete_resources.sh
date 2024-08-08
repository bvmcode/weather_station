#!/bin/sh
ecr_address=`cat ./scripts/preserve_ecr_address.txt`
aws ecr batch-delete-image --repository-name wx_station --image-ids imageTag=latest --profile wx_deploy
rm ./prod/.env
rm ./prod/rds_host.txt
rm ./scripts/preserve_ecr_address.txt
terraform destroy -auto-approve -var-file="secrets.tfvars"
