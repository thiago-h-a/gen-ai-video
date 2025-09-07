
# ---- Managed policies used by IRSA roles ----

# S3 read for webapi
data "aws_iam_policy_document" "s3_read_artifacts" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${module.s3_artifacts.bucket_arn}/*"]
  }
}
resource "aws_iam_policy" "s3_read_artifacts" {
  name   = "${var.project}-s3-read-artifacts"
  policy = data.aws_iam_policy_document.s3_read_artifacts.json
}

# S3 write for workers
data "aws_iam_policy_document" "s3_write_artifacts" {
  statement {
    actions   = ["s3:PutObject", "s3:GetObject", "s3:AbortMultipartUpload", "s3:ListBucket"]
    resources = [module.s3_artifacts.bucket_arn, "${module.s3_artifacts.bucket_arn}/*"]
  }
}
resource "aws_iam_policy" "s3_write_artifacts" {
  name   = "${var.project}-s3-write-artifacts"
  policy = data.aws_iam_policy_document.s3_write_artifacts.json
}

# DynamoDB + SMR policy for model-catalog (reuses Step 12 module where policy_arn is exposed)
# If you used module.model_catalog earlier, it outputs policy_arn; otherwise attach simple read-only
data "aws_iam_policy" "model_catalog" {
  arn = try(module.model_catalog.policy_arn, "arn:aws:iam::aws:policy/AmazonSageMakerReadOnly")
}
