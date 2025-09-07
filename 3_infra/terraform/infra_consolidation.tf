
# S3 artifacts bucket
module "s3_artifacts" {
  source            = "./modules/s3-artifacts"
  bucket_name       = "${var.project}-artifacts"
  enable_public_read = false
}

# ElastiCache Redis for fair-scheduler
module "redis" {
  source     = "./modules/redis"
  name       = "${var.project}-redis"
  vpc_id     = var.vpc_id
  subnet_ids = var.private_subnet_ids
}

# ---- IRSA roles per service ----
module "irsa_webapi" {
  source                  = "./modules/irsa-role"
  name                    = "${var.project}-webapi"
  namespace               = "ai-microgen"
  service_account         = "webapi-sa"
  eks_oidc_provider_arn   = var.eks_oidc_provider_arn
  eks_oidc_provider_url   = var.eks_oidc_provider_url
  attach_policy_arns      = [aws_iam_policy.s3_read_artifacts.arn]
}

module "irsa_prompt" {
  source                  = "./modules/irsa-role"
  name                    = "${var.project}-prompt"
  namespace               = "ai-microgen"
  service_account         = "prompt-service-sa"
  eks_oidc_provider_arn   = var.eks_oidc_provider_arn
  eks_oidc_provider_url   = var.eks_oidc_provider_url
  attach_policy_arns      = []
}

module "irsa_model_catalog" {
  source                  = "./modules/irsa-role"
  name                    = "${var.project}-model-catalog"
  namespace               = "ai-microgen"
  service_account         = "model-catalog-sa"
  eks_oidc_provider_arn   = var.eks_oidc_provider_arn
  eks_oidc_provider_url   = var.eks_oidc_provider_url
  attach_policy_arns      = [try(module.model_catalog.policy_arn, data.aws_iam_policy.model_catalog.arn)]
}

module "irsa_gpu_worker" {
  source                  = "./modules/irsa-role"
  name                    = "${var.project}-gpu-worker"
  namespace               = "ai-microgen"
  service_account         = "gpu-worker-sa"
  eks_oidc_provider_arn   = var.eks_oidc_provider_arn
  eks_oidc_provider_url   = var.eks_oidc_provider_url
  attach_policy_arns      = [aws_iam_policy.s3_write_artifacts.arn]
}

module "irsa_video_worker" {
  source                  = "./modules/irsa-role"
  name                    = "${var.project}-video-worker"
  namespace               = "ai-microgen"
  service_account         = "video-worker-sa"
  eks_oidc_provider_arn   = var.eks_oidc_provider_arn
  eks_oidc_provider_url   = var.eks_oidc_provider_url
  attach_policy_arns      = [aws_iam_policy.s3_write_artifacts.arn]
}

module "irsa_fair_scheduler" {
  source                  = "./modules/irsa-role"
  name                    = "${var.project}-fair-scheduler"
  namespace               = "ai-microgen"
  service_account         = "fair-scheduler-sa"
  eks_oidc_provider_arn   = var.eks_oidc_provider_arn
  eks_oidc_provider_url   = var.eks_oidc_provider_url
  attach_policy_arns      = []
}
