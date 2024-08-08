resource "aws_ecr_repository" "wx_station" {
  name                 = "wx_station"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  force_delete = false
 depends_on = [ local_file.rds_host_to_file, null_resource.db_setup ]
}

data "aws_ecr_authorization_token" "token" {}

provider "docker" {
  registry_auth {
      address = data.aws_ecr_authorization_token.token.proxy_endpoint
      username = data.aws_ecr_authorization_token.token.user_name
      password  = data.aws_ecr_authorization_token.token.password
    }
}

resource "local_file" "ecr_address" {
  filename = "./scripts/ecr_address.txt"
  content  = replace("${data.aws_ecr_authorization_token.token.proxy_endpoint}/wx_station", "https://", "")
}

resource "null_resource" "push_docker_image" {
  provisioner "local-exec" {
    command     = "./scripts/ecr_image_push.sh"
    interpreter = ["bash", "-c"]
  }
  depends_on = [aws_ecr_repository.wx_station, local_file.ecr_address]
}
