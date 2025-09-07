
variable "name" { type = string }
variable "namespace" { type = string }
variable "service_account" { type = string }
variable "eks_oidc_provider_arn" { type = string }
variable "eks_oidc_provider_url" { type = string }
variable "attach_policy_arns" { type = list(string) default = [] }

# Trust policy for IRSA
data "aws_iam_policy_document" "trust" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"
    principals {
      type        = "Federated"
      identifiers = [var.eks_oidc_provider_arn]
    }
    condition {
      test     = "StringEquals"
      variable = "${replace(var.eks_oidc_provider_url, "https://", "")} :sub"
      values   = ["system:serviceaccount:${var.namespace}:${var.service_account}"]
    }
  }
}

resource "aws_iam_role" "this" {
  name               = var.name
  assume_role_policy = data.aws_iam_policy_document.trust.json
}

resource "aws_iam_role_policy_attachment" "extra" {
  count      = length(var.attach_policy_arns)
  role       = aws_iam_role.this.name
  policy_arn = var.attach_policy_arns[count.index]
}

output "role_arn" { value = aws_iam_role.this.arn }
