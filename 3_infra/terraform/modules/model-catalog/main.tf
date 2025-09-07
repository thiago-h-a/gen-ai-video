
variable "project" {}
variable "table_prefix" { default = "model_catalog" }

# DynamoDB tables
resource "aws_dynamodb_table" "models" {
  name         = "${var.table_prefix}_models"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "model_id"
  attribute { name = "model_id" type = "S" }
  tags = { Project = var.project, Purpose = "model-catalog" }
}

resource "aws_dynamodb_table" "versions" {
  name         = "${var.table_prefix}_versions"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "model_id"
  range_key    = "version"
  attribute { name = "model_id" type = "S" }
  attribute { name = "version" type = "S" }
  # Example GSIs you can uncomment/extend later:
  # global_secondary_index {
  #   name            = "by_modality"
  #   hash_key        = "modality"
  #   projection_type = "ALL"
  # }
  tags = { Project = var.project, Purpose = "model-catalog" }
}

resource "aws_dynamodb_table" "cards" {
  name         = "${var.table_prefix}_cards"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "model_id"
  range_key    = "version"
  attribute { name = "model_id" type = "S" }
  attribute { name = "version" type = "S" }
  tags = { Project = var.project, Purpose = "model-catalog" }
}

# Minimal IAM policy for DDB CRUD + SMR read
data "aws_iam_policy_document" "catalog" {
  statement {
    sid    = "DDBCrud"
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:Query",
      "dynamodb:Scan"
    ]
    resources = [
      aws_dynamodb_table.models.arn,
      aws_dynamodb_table.versions.arn,
      aws_dynamodb_table.cards.arn
    ]
  }
  statement {
    sid    = "SageMakerRead"
    effect = "Allow"
    actions = [
      "sagemaker:ListModelPackages",
      "sagemaker:ListModelPackageGroups",
      "sagemaker:DescribeModelPackage",
      "sagemaker:DescribeModelPackageGroup"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "catalog" {
  name   = "${var.project}-model-catalog"
  policy = data.aws_iam_policy_document.catalog.json
}

output "ddb_models"   { value = aws_dynamodb_table.models.name }
output "ddb_versions" { value = aws_dynamodb_table.versions.name }
output "ddb_cards"    { value = aws_dynamodb_table.cards.name }
output "policy_arn"   { value = aws_iam_policy.catalog.arn }
