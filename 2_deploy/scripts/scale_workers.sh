
#!/usr/bin/env bash
set -euo pipefail
N=${1:-10}
kubectl -n ai-microgen scale deploy/gpu-worker --replicas=${N}
kubectl -n ai-microgen get deploy/gpu-worker
