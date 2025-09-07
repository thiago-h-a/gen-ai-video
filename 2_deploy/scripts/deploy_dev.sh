
#!/usr/bin/env bash
set -euo pipefail
kubectl apply -k $(dirname $0)/../k8s/overlays/dev
kubectl -n ai-microgen get pods -o wide
echo "Deployed dev overlay. Ingress may require an IngressController (nginx)."
