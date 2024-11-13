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

module "ecs" {
  source             = "./ecs"
  app_name           = var.app_name
  region             = var.region
  image              = var.image
  supabase_url       = var.supabase_url
  supabase_key       = var.supabase_key
  email_api_key      = var.email_api_key
  openai_api_key     = var.openai_api_key
  vpc_id             = module.network.vpc.id
  public_subnet_ids  = [for s in module.network.public_subnets : s.id]
  depends_on         = [module.network]
}


# Outputs
output "alb_dns_name" {
  value = module.ecs.alb_dns_name
}
