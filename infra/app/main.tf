provider "aws" {
  region = var.region
  default_tags {
    tags = {
      app = var.app_name
    }
  }
}

module "network" {
  source   = "./network"
  app_name = var.app_name
  region   = var.region
}

resource "aws_acm_certificate" "trackflow_api" {
  domain_name       = "api.trackflow.xyz"
  validation_method = "DNS"
}

output "certificate_validation_records" {
  value = {
    for dvo in aws_acm_certificate.trackflow_api.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }
}

module "ecs" {
  source             = "./ecs"
  app_name           = var.app_name
  region             = var.region
  image              = var.image
  supabase_url       = var.supabase_url
  supabase_key       = var.supabase_key
  email_api_key      = var.email_api_key
  openai_api_key     = var.openai_api_key
  api_key            = var.api_key
  certificate_arn    = aws_acm_certificate.trackflow_api.arn
  vpc_id             = module.network.vpc.id
  public_subnet_ids  = [for s in module.network.public_subnets : s.id]
  depends_on         = [module.network]
}

module "eventbridge" {
  source       = "./eventbridge"
  api_key      = var.api_key
  api_base_url = var.api_base_url
}


# Outputs
output "alb_dns_name" {
  value = module.ecs.alb_dns_name
}

output "certificate_arn" {
  value = aws_acm_certificate.trackflow_api.arn
}
