
#!/usr/bin/env bash
set -euo pipefail
echo "Exporting local dev env vars..."
export REDIS_URL=${REDIS_URL:-redis://localhost:6379/0}
export S3_ENDPOINT=${S3_ENDPOINT:-http://localhost:9000}
export S3_REGION=${S3_REGION:-us-east-1}
export S3_ACCESS_KEY=${S3_ACCESS_KEY:-minioadmin}
export S3_SECRET_KEY=${S3_SECRET_KEY:-minioadmin}
export ARTIFACTS_BUCKET=${ARTIFACTS_BUCKET:-artifacts}
echo "Done."
