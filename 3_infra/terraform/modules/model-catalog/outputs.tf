
output "ddb_models"   { value = aws_dynamodb_table.models.name }
output "ddb_versions" { value = aws_dynamodb_table.versions.name }
output "ddb_cards"    { value = aws_dynamodb_table.cards.name }
output "policy_arn"   { value = aws_iam_policy.catalog.arn }
