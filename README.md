# Ambient Weather Station Data Collection

This repo builds a container and creates the AWS infrastructure for persisting Ambient weather station data every 2 minutes.
This builds

* ECR image repository with our image
* RDS Postgres instance with a table for writing data to
* EC2 instance that runs our container

## Files Needed

### ./infra/secrets.tfvars

```
db_password="<password>"
db_user="<user name>"
```

### ./infra/prod/.env_tmp

```
AMBIENT_API_KEY=<api key>
AMBIENT_APPLICATION_KEY=<api app key>
POSTGRES_PWD=<password in secrets.tfvars>
POSTGRES_USER=<username in secrets.tfvars>
POSTGRES_DB=postgres
```

POSTGRES_HOST gets added to this in a generated `.env` file

### ./infra/keys/

public and private keys called `terraform-keys` and `terraform-keys.pub`
