#!/bin/bash
sudo yum update -y
sudo amazon-linux-extras install docker -y
sudo service docker start
sudo systemctl enable docker
ecr_address=`cat ./ecr_address.txt`
aws --region us-east-1 ecr get-login-password | sudo docker login --username AWS --password-stdin $ecr_address
sleep 60s
sudo docker pull $ecr_address:latest
sudo docker run -d $ecr_address:latest