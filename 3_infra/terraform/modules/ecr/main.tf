
variable "project" {}
variable "repos" {}

resource "aws_ecr_repository" "this" {
  for_each = toset(var.repos)
  name                 = "${var.project}/${each.key}"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration { scan_on_push = true }
  tags = { Project = var.project, Service = each.key }
}

output "repo_urls" {
  value = { for k, r in aws_ecr_repository.this : k => r.repository_url }
}
