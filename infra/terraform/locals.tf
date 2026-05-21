locals {
  azs = ["${var.aws_region}a", "${var.aws_region}b"]

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}