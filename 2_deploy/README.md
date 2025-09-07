
# deploy/

Deployment manifests for **ai-microgen**.

## Compose (local all-in-one)

```bash
docker compose -f deploy/compose/docker-compose.full.yml up --build
```

## Kubernetes via kustomize

- Dev overlay brings dev Redis/MinIO.
- AWS overlay expects: ECR images; S3 buckets; ElastiCache Redis; ALB Ingress.

```bash
# Dev
kubectl apply -k k8s/overlays/dev

# AWS — edit overlays/aws/patches-env.yaml first
kubectl apply -k k8s/overlays/aws
```

### Useful scripts

- `deploy/scripts/deploy_dev.sh`
- `deploy/scripts/deploy_aws.sh`
- `deploy/scripts/scale_workers.sh <N>`
