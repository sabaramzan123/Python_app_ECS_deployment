data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

locals {
  # Availability Zones (Ye wahi rahega)
  azs = length(var.availability_zones) > 0 ? var.availability_zones : slice(data.aws_availability_zones.available.names, 0, 2)

  # Common Tags
  common_tags = merge(
    {
      Project   = var.project_name
      ManagedBy = "terraform"
    },
    var.tags
  )

  # Streamlit App Configuration
  # Hamare paas sirf ek hi service hai: compiler-app
  app_port   = 8501
  app_cpu    = 512
  app_memory = 1024
}