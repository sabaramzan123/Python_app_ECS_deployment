# -----------------------------------------------
# ECR REPOSITORY
# -----------------------------------------------
resource "aws_ecr_repository" "app" {
  name                 = "${var.project_name}-compiler-app"
  image_tag_mutability = "MUTABLE"
  force_delete = true 

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.common_tags
}

# -----------------------------------------------
# CLOUDWATCH LOG GROUP
# -----------------------------------------------
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.project_name}"
  retention_in_days = 7
  tags              = local.common_tags
}

# -----------------------------------------------
# ECS CLUSTER
# -----------------------------------------------
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"
  tags = local.common_tags
}

# -----------------------------------------------
# ECS TASK DEFINITION
# -----------------------------------------------
resource "aws_ecs_task_definition" "app" {
  family                   = var.project_name
  cpu                      = "512"
  memory                   = "1024"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = var.project_name
      image     = "${aws_ecr_repository.app.repository_url}:${var.image_tag}"
      essential = true

      portMappings = [
        {
          containerPort = 8501
          hostPort      = 8501
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "PORT"
          value = "8501"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.app.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = var.project_name
        }
      }
    }
  ])

  tags = local.common_tags
}

# -----------------------------------------------
# SECURITY GROUP — ALB (internet se traffic aaye)
# -----------------------------------------------
resource "aws_security_group" "alb" {
  name   = "${var.project_name}-alb-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.common_tags
}

# -----------------------------------------------
# SECURITY GROUP — ECS (sirf ALB se traffic aaye)
# -----------------------------------------------
resource "aws_security_group" "ecs_service" {
  name   = "${var.project_name}-ecs-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    description     = "Streamlit port from ALB only"
    from_port       = 8501
    to_port         = 8501
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]  # internet se direct nahi, sirf ALB se
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.common_tags
}

# -----------------------------------------------
# APPLICATION LOAD BALANCER
# -----------------------------------------------
resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id  # public subnets mein

  tags = local.common_tags
}

# -----------------------------------------------
# ALB TARGET GROUP (ECS tasks yahan register honge)
# -----------------------------------------------
resource "aws_lb_target_group" "app" {
  name        = "${var.project_name}-tg"
  port        = 8501
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"  # Fargate ke liye "ip" zaroori hai

  health_check {
    path                = "/"
    protocol            = "HTTP"
    port                = "8501"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  tags = local.common_tags
}

# -----------------------------------------------
# ALB LISTENER (port 80 par suno, target group ko forward karo)
# -----------------------------------------------
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }

  tags = local.common_tags
}

# -----------------------------------------------
# ECS SERVICE (ab ALB se connected)
# -----------------------------------------------
resource "aws_ecs_service" "app" {
  name                               = "${var.project_name}-service"
  cluster                            = aws_ecs_cluster.main.id
  task_definition                    = aws_ecs_task_definition.app.arn
  desired_count                      = 1
  launch_type                        = "FARGATE"
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 50

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.ecs_service.id]
    assign_public_ip = true
  }

  # ALB se connect karo
  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = var.project_name
    container_port   = 8501
  }

  depends_on = [aws_lb_listener.http]  # listener pehle bane

  tags = local.common_tags
}