
variable "create" { type = bool }
variable "project" { type = string }
variable "version" { type = string }
variable "subnet_ids" { type = list(string) }
variable "vpc_id" { type = string }
variable "node_count" { type = number }
variable "instance_type" { type = string }
