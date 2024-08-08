
resource "aws_db_parameter_group" "weather" {
  name   = "weather"
  family = "postgres16"

  parameter {
    name  = "log_connections"
    value = "1"
  }
}

resource "aws_security_group" "rds_security_group" {
  name   = "weather_rds"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "weather_rds"
  }
}


resource "aws_db_subnet_group" "weather" {
  name       = "weather_subnet"
  subnet_ids = module.vpc.public_subnets

  tags = {
    Name = "weather_subnet"
  }
}

resource "aws_db_instance" "weather" {
  identifier             = "weather"
  instance_class         = "db.t3.micro"
  allocated_storage      = 5
  engine                 = "postgres"
  engine_version         = "16.3"
  username               = var.db_user
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.weather.name
  vpc_security_group_ids = [aws_security_group.rds_security_group.id]
  parameter_group_name   = aws_db_parameter_group.weather.name
  publicly_accessible    = true
  skip_final_snapshot    = true
}

resource "local_file" "rds_host_to_file" {
  filename = "./prod/rds_host.txt"
  content  = "POSTGRES_HOST=${aws_db_instance.weather.address}"
}

resource "null_resource" "db_setup" {
    provisioner "local-exec" {
        command = "psql -h ${aws_db_instance.weather.address} -p 5432 -U \"${var.db_user}\" -d postgres -f \"./scripts/init.sql\""
        environment = {
          PGPASSWORD = "${var.db_password}"
        }
    }
    depends_on = [aws_db_instance.weather]
}