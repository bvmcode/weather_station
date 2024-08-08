
resource "aws_iam_role" "ecr_role" {
  name               = "ecr-role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": ["ec2.amazonaws.com"]
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

}

resource "aws_iam_policy" "ecr_policy" {
  name = "ecr-access-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ecr:*",
          "rds:*"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}


resource "aws_iam_policy_attachment" "attach" {
  name       = "ecr-attach"
  roles      = ["${aws_iam_role.ecr_role.name}"]
  policy_arn = "${aws_iam_policy.ecr_policy.arn}"
}

resource "aws_iam_instance_profile" "profile" {
  name = "profile"
  role = aws_iam_role.ecr_role.name
}


# create default subnet if one does not exit
resource "aws_default_subnet" "default_az1" {
  availability_zone = data.aws_availability_zones.available.names[0]#data.aws_availability_zones.available_zones.names[0]

  tags = {
    Name = "default subnet"
  }
}


# create security group for the ec2 instance
resource "aws_security_group" "ec2_security_group" {
  name        = "ec2 security group"
  description = "allow access on ports 80 and 22"
  vpc_id      = module.vpc.vpc_id  #aws_default_vpc.default_vpc.id

  ingress {
    description = "http access"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "ssh access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "db access"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "docker server sg"
  }
}


# use data source to get a registered amazon linux 2 ami
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "owner-alias"
    values = ["amazon"]
  }

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm*"]
  }
}


resource "aws_key_pair" "terraform-keys" {
  key_name = "terraform-keys"
  public_key = "${file("${path.root}/keys/terraform-keys.pub")}"
}

# launch the ec2 instance
resource "aws_instance" "ec2_instance" {
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = "t2.micro"
  subnet_id              = module.vpc.public_subnets[0]#aws_default_subnet.default_az1.id
  vpc_security_group_ids = [aws_security_group.ec2_security_group.id]
  key_name               = aws_key_pair.terraform-keys.key_name
  iam_instance_profile        = aws_iam_instance_profile.profile.name
  

  tags = {
    Name = "docker server"
  }
}
# an empty resource block
resource "null_resource" "name" {

  # ssh into the ec2 instance 
  connection {
    type        = "ssh"
    user        = "ec2-user"
    private_key = file("./keys/terraform-keys")
    host        = aws_instance.ec2_instance.public_ip
  }

  provisioner "file" {
    source      = "./scripts/ecr_address.txt"
    destination = "/home/ec2-user/ecr_address.txt"
  }
  
  provisioner "file" {
    source      = "./scripts/deployment.sh"
    destination = "/home/ec2-user/deployment.sh"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo chmod +x /home/ec2-user/deployment.sh",
      "sh /home/ec2-user/deployment.sh",

    ]
  }

  # wait for ec2 to be created
  depends_on = [aws_instance.ec2_instance, null_resource.push_docker_image]

}
# # print the url of the container
# output "container_url" {
#   value = join("", ["http://", aws_instance.ec2_instance.public_dns])
# }