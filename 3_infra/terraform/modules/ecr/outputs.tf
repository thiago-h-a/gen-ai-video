
output "repo_urls" { value = { for k, r in aws_ecr_repository.this : k => r.repository_url } }
