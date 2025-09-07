
# ECR repository for video-worker
resource "aws_ecr_repository" "video_worker" {
  name = "video-worker"
  image_scanning_configuration { scan_on_push = true }
  image_tag_mutability = "MUTABLE"
  tags = { Project = var.project }
}

# EKS GPU node group for video workloads
# Note: requires existing cluster, role, and subnet variables.
variable "eks_cluster_name" {}
variable "eks_node_role_arn" {}
variable "eks_subnet_ids" { type = list(string) }

resource "aws_eks_node_group" "video_gpu" {
  cluster_name    = var.eks_cluster_name
  node_group_name = "video-gpu-ng"
  node_role_arn   = var.eks_node_role_arn
  subnet_ids      = var.eks_subnet_ids
  scaling_config { desired_size = 1, min_size = 1, max_size = 5 }
  ami_type  = "AL2_x86_64_GPU"
  instance_types = ["g5.xlarge"]
  labels = { "workload" = "video", "accelerator" = "nvidia" }
  tags   = { Project = var.project }
}
