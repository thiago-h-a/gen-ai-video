
variable "bucket_name" { type = string }
variable "enable_public_read" { type = bool default = false }

resource "aws_s3_bucket" "artifacts" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_versioning" "v" {
  bucket = aws_s3_bucket.artifacts.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "sse" {
  bucket = aws_s3_bucket.artifacts.id
  rule { apply_server_side_encryption_by_default { sse_algorithm = "AES256" } }
}

# Optional public read policy (dev only)
resource "aws_s3_bucket_policy" "public" {
  count = var.enable_public_read ? 1 : 0
  bucket = aws_s3_bucket.artifacts.id
  policy = <<POL
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicRead",
      "Effect": "Allow",
      "Principal": "*",
      "Action": ["s3:GetObject"],
      "Resource": ["${aws_s3_bucket.artifacts.arn}/*"]
    }
  ]
}
POL
}

output "bucket_name" { value = aws_s3_bucket.artifacts.bucket }
output "bucket_arn"  { value = aws_s3_bucket.artifacts.arn }
