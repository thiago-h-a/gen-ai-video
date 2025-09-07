
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../terraform"
ARTIFACTS=$(terraform output -raw artifacts_bucket || true)
MODELS=$(terraform output -raw models_bucket || true)
REDIS=$(terraform output -raw redis_endpoint || true)
REGION=$(terraform output -raw region || echo "us-east-1")

cat <<EOF
# Export these before applying deploy/k8s overlays (AWS)
export ARTIFACTS_BUCKET=${ARTIFACTS}
export MODELS_BUCKET=${MODELS}
export REDIS_ENDPOINT=${REDIS}
export AWS_REGION=${REGION}
EOF
