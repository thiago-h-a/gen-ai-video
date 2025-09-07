
output "artifacts_bucket" { value = module.s3_artifacts.bucket_name }
output "redis_endpoint"   { value = module.redis.primary_endpoint }
output "redis_port"       { value = module.redis.port }

output "irsa_webapi"         { value = module.irsa_webapi.role_arn }
output "irsa_prompt"         { value = module.irsa_prompt.role_arn }
output "irsa_model_catalog"  { value = module.irsa_model_catalog.role_arn }
output "irsa_gpu_worker"     { value = module.irsa_gpu_worker.role_arn }
output "irsa_video_worker"   { value = module.irsa_video_worker.role_arn }
output "irsa_fair_scheduler" { value = module.irsa_fair_scheduler.role_arn }
