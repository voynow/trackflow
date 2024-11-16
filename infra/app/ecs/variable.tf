variable "app_name" {
  description = "Name of the app."
  type        = string
}
variable "region" {
  description = "AWS region to deploy the network to."
  type        = string
}
variable "image" {
  description = "Image used to start the container. Should be in repository-url/image:tag format."
  type        = string
}
variable "vpc_id" {
  description = "ID of the VPC where the ECS will be hosted."
  type        = string
}
variable "public_subnet_ids" {
  description = "IDs of public subnets where the ALB will be attached to."
  type        = list(string)
}
variable "supabase_url" {
  type        = string
  description = "Supabase URL for the application"
  sensitive   = true
}
variable "supabase_key" {
  type        = string
  description = "Supabase API key"
  sensitive   = true
}
variable "email_api_key" {
  type        = string
  description = "API key for the email service"
  sensitive   = true
}
variable "openai_api_key" {
  type        = string
  description = "API key for the OpenAI service"
  sensitive   = true
}
variable "api_key" {
  description = "API key for authentication"
  type        = string
  sensitive   = true
}
variable "certificate_arn" {
  type        = string
  description = "ARN of the ACM certificate for HTTPS"
}

