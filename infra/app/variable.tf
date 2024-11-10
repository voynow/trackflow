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