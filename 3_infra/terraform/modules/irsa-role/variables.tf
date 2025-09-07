
variable "name" {}
variable "namespace" {}
variable "service_account" {}
variable "eks_oidc_provider_arn" {}
variable "eks_oidc_provider_url" {}
variable "attach_policy_arns" { type = list(string) }
