
#!/usr/bin/env bash
set -euo pipefail
SERVICES=(webapi prompt-service notify-service orchestrator gpu-worker model-registry)
for s in "${SERVICES[@]}"; do
  echo "[build] $s"
  docker build -t $s:latest ../../services/$s
done
