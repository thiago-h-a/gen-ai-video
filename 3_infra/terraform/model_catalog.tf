
module "model_catalog" {
  source       = "./modules/model-catalog"
  project      = var.project
  table_prefix = "model_catalog"
}
