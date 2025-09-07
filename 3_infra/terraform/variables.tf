
variable "project" { type = string }
variable "region"  { type = string }
variable "vpc_id"  { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "eks_cluster_name" { type = string }
variable "eks_oidc_provider_arn" { type = string }
variable "eks_oidc_provider_url" { type = string }
