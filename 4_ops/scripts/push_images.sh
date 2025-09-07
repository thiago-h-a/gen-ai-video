
#!/usr/bin/env bash
set -euo pipefail
: "${REG:?Set REG=account_id.dkr.ecr.region.amazonaws.com}"
SERVICES=(webapi prompt-service notify-service orchestrator gpu-worker model-registry)
for s in "${SERVICES[@]}"; do
  docker tag $s:latest $REG/$s:latest
  docker push $REG/$s:latest
done
