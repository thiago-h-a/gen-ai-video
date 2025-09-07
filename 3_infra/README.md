
# infra/

Infrastructure-as-code for **ai-microgen** (Terraform on AWS).

## What gets created
- VPC (2 AZs) with public/private subnets, NAT, routing
- S3 buckets: artifacts (private), models (private) with versioning + lifecycle
- ElastiCache Redis (single primary)
- ECR repositories for service images
- (Optional) EKS cluster stub (control plane + single node group)

## Usage

```bash
cd terraform
../../scripts/tf_init.sh

export TF_VAR_project=ai-microgen
export TF_VAR_region=us-east-1
export TF_VAR_artifacts_bucket=ai-microgen-artifacts
export TF_VAR_models_bucket=ai-microgen-models

../../scripts/tf_apply.sh
../../scripts/print_env.sh
```

Review and customize variables in `variables.tf`. For production, set up a
proper remote backend (S3 + DynamoDB) in `backend.tf`.
