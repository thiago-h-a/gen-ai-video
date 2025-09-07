
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../terraform"
terraform init
echo "Terraform initialized. Configure backend in backend.tf for remote state."
