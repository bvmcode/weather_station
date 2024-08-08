plan:
	terraform plan -var-file="secrets.tfvars"
deploy:
	terraform apply -auto-approve -var-file="secrets.tfvars"
destroy:
	./scripts/delete_resources.sh