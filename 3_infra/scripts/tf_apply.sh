
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../terraform"
: "${TF_VAR_project:?TF_VAR_project required}"
: "${TF_VAR_region:?TF_VAR_region required}"
: "${TF_VAR_artifacts_bucket:?TF_VAR_artifacts_bucket required}"
: "${TF_VAR_models_bucket:?TF_VAR_models_bucket required}"

terraform plan -out=tfplan
terraform apply -auto-approve tfplan
echo "Apply complete."
