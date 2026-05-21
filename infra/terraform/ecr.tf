resource "aws_ecr_repository" "app" {
  name                 = "${var.project_name}-compiler-app"  # ← match karao pipeline se
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.common_tags
}