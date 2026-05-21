# 1. ECR Repository
resource "aws_ecr_repository" "app_repo" {
  name = "compiler-app-repo"
}

# 2. ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "compiler-cluster"
}

# 3. Networking (Simple VPC)
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

# 4. Load Balancer (Public Access ke liye)
resource "aws_lb" "app_lb" {
  name               = "compiler-lb"
  internal           = false
  load_balancer_type = "application"
  subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

