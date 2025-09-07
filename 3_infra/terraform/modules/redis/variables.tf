
variable "name" {}
variable "vpc_id" {}
variable "subnet_ids" { type = list(string) }
variable "engine_version" {}
variable "node_type" {}
