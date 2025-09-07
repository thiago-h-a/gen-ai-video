
module "network" {
  source    = "./modules/network"
  project   = var.project
  vpc_cidr  = var.vpc_cidr
  az_count  = var.az_count
}

module "s3" {
  source            = "./modules/s3"
  project           = var.project
  artifacts_bucket  = var.artifacts_bucket
  models_bucket     = var.models_bucket
}

module "ecr" {
  source   = "./modules/ecr"
  project  = var.project
  repos    = var.ecr_repos
}

module "redis" {
  source            = "./modules/redis"
  project           = var.project
  subnet_ids        = module.network.private_subnet_ids
  vpc_id            = module.network.vpc_id
  instance_class    = var.redis_instance_class
}

module "eks" {
  source         = "./modules/eks"
  create         = var.create_eks
  project        = var.project
  version        = var.eks_version
  subnet_ids     = module.network.private_subnet_ids
  vpc_id         = module.network.vpc_id
  node_count     = var.eks_node_count
  instance_type  = var.eks_instance_type
}
