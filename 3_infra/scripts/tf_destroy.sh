
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../terraform"
terraform destroy -auto-approve || true
