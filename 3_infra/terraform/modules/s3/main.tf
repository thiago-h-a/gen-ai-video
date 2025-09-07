
variable "project" {}
variable "artifacts_bucket" {}
variable "models_bucket" {}

resource "aws_s3_bucket" "artifacts" {
  bucket = var.artifacts_bucket
  force_destroy = false
  tags = { Project = var.project, Purpose = "artifacts" }
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_lifecycle_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  rule {
    id     = "expire-old-multipart"
    status = "Enabled"
    abort_incomplete_multipart_upload { days_after_initiation = 7 }
  }
}

resource "aws_s3_bucket" "models" {
  bucket = var.models_bucket
  force_destroy = false
  tags = { Project = var.project, Purpose = "models" }
}

resource "aws_s3_bucket_versioning" "models" {
  bucket = aws_s3_bucket.models.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_lifecycle_configuration" "models" {
  bucket = aws_s3_bucket.models.id
  rule {
    id     = "transition-old-versions"
    status = "Enabled"
    noncurrent_version_transition { noncurrent_days = 30 storage_class = "STANDARD_IA" }
  }
}

output "artifacts_bucket_name" { value = aws_s3_bucket.artifacts.bucket }
output "models_bucket_name"    { value = aws_s3_bucket.models.bucket }
