
variable "name" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }
variable "engine_version" { default = "7.0" }
variable "node_type" { default = "cache.t3.small" }

resource "aws_security_group" "redis" {
  name        = "${var.name}-sg"
  description = "ElastiCache Redis SG"
  vpc_id      = var.vpc_id
  ingress { from_port = 6379 to_port = 6379 protocol = "tcp" cidr_blocks = ["0.0.0.0/0"] }
  egress  { from_port = 0    to_port = 0    protocol = "-1"  cidr_blocks = ["0.0.0.0/0"] }
}

resource "aws_elasticache_subnet_group" "this" {
  name       = "${var.name}-subnets"
  subnet_ids = var.subnet_ids
}

resource "aws_elasticache_replication_group" "this" {
  replication_group_id          = var.name
  description                   = "Redis for ai-microgen fair-scheduler"
  engine                        = "redis"
  engine_version                = var.engine_version
  node_type                     = var.node_type
  parameter_group_name          = "default.redis7"
  port                          = 6379
  num_node_groups               = 1
  replicas_per_node_group       = 0
  automatic_failover_enabled    = false
  at_rest_encryption_enabled    = true
  transit_encryption_enabled    = true
  subnet_group_name             = aws_elasticache_subnet_group.this.name
  security_group_ids            = [aws_security_group.redis.id]
}

output "primary_endpoint" { value = aws_elasticache_replication_group.this.primary_endpoint_address }
output "port"             { value = aws_elasticache_replication_group.this.port }
