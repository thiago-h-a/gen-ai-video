
variable "create" {}
variable "project" {}
variable "version" {}
variable "subnet_ids" {}
variable "vpc_id" {}
variable "node_count" {}
variable "instance_type" {}

locals { enabled = var.create == true }

resource "aws_iam_role" "cluster" {
  count = local.enabled ? 1 : 0
  name               = "${var.project}-eks-cluster"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{ Effect = "Allow", Principal = { Service = "eks.amazonaws.com" }, Action = "sts:AssumeRole" }]
  })
}

resource "aws_iam_role_policy_attachment" "cluster_AmazonEKSClusterPolicy" {
  count      = local.enabled ? 1 : 0
  role       = aws_iam_role.cluster[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

resource "aws_eks_cluster" "this" {
  count    = local.enabled ? 1 : 0
  name     = "${var.project}"
  role_arn = aws_iam_role.cluster[0].arn
  version  = var.version
  vpc_config { subnet_ids = var.subnet_ids }
  depends_on = [aws_iam_role_policy_attachment.cluster_AmazonEKSClusterPolicy]
}

resource "aws_iam_role" "node" {
  count = local.enabled ? 1 : 0
  name  = "${var.project}-eks-node"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{ Effect = "Allow", Principal = { Service = "ec2.amazonaws.com" }, Action = "sts:AssumeRole" }]
  })
}

resource "aws_iam_role_policy_attachment" "node_AmazonEKSWorkerNodePolicy" {
  count = local.enabled ? 1 : 0
  role  = aws_iam_role.node[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

resource "aws_iam_role_policy_attachment" "node_AmazonEC2ContainerRegistryReadOnly" {
  count = local.enabled ? 1 : 0
  role  = aws_iam_role.node[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_role_policy_attachment" "node_AmazonEKS_CNI_Policy" {
  count = local.enabled ? 1 : 0
  role  = aws_iam_role.node[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}

resource "aws_eks_node_group" "ng" {
  count             = local.enabled ? 1 : 0
  cluster_name      = aws_eks_cluster.this[0].name
  node_group_name   = "${var.project}-ng"
  node_role_arn     = aws_iam_role.node[0].arn
  subnet_ids        = var.subnet_ids
  scaling_config    = { desired_size = var.node_count, min_size = 1, max_size = max(3, var.node_count) }
  instance_types    = [var.instance_type]
  ami_type          = "AL2_x86_64"
  disk_size         = 40
  depends_on = [
    aws_iam_role_policy_attachment.node_AmazonEKSWorkerNodePolicy,
    aws_iam_role_policy_attachment.node_AmazonEC2ContainerRegistryReadOnly,
    aws_iam_role_policy_attachment.node_AmazonEKS_CNI_Policy,
  ]
}

output "cluster_name"    { value = local.enabled ? aws_eks_cluster.this[0].name : null }
output "cluster_endpoint" { value = local.enabled ? aws_eks_cluster.this[0].endpoint : null }
output "oidc_issuer"      { value = local.enabled ? aws_eks_cluster.this[0].identity[0].oidc[0].issuer : null }
