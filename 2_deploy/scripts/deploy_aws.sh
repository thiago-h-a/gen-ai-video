
#!/usr/bin/env bash
set -euo pipefail
THIS_DIR=$(dirname $0)
echo "Applying AWS overlay (ensure images pushed to ECR and patches-env.yaml is filled)"
kubectl apply -k ${THIS_DIR}/../k8s/overlays/aws
kubectl -n ai-microgen get ingress ai-web
