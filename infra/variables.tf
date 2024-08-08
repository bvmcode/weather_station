variable "region" {
  default     = "us-east-1"
  description = "AWS region"
}

variable "db_password" {
  description = "RDS root user password"
  sensitive   = true
}

variable "db_user" {
  description = "RDS root user password"
  sensitive   = true
}

variable "local_path" {
  description = "local_path"
  default = "../app/prod"
}