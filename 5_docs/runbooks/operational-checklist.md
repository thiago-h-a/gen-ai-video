
# Operational checklist

## First deploy
- Apply Terraform (see runbook `infra-consolidation.md`)
- Patch IRSA overlays from TF outputs
- Ensure ElastiCache REDIS_URL in fair-scheduler overlay
- `kubectl get pods -n ai-microgen` → all services Running
- `curl fair-scheduler/metrics` has `fair_queue_depth_total{type}`

## Health checks
- Web/API: `/healthz` responds `{ok:true}`
- Prompt Service: `/healthz`
- Workers: `/healthz`, `/readyz`
- Model Catalog: `/healthz`, `/models`

## Scaling knobs
- HPA targets (image backlog ~2/pod, video backlog ~1/pod)
- GPU/Video node group size limits in Terraform

## Incident quickstart
1. Identify saturation: Grafana panel `Queue depth total`
2. Throttle arrivals: temporarily reduce SPA concurrency
3. Increase replicas: `kubectl scale deploy video-worker --replicas=N`
4. If Redis impacted: failover/resize ElastiCache (maintenance window)

## Backups
- S3 artifacts are versioned; enable lifecycle policies to expire old versions
- DynamoDB PITR for model metadata
