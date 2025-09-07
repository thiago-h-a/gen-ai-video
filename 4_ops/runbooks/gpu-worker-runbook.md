
# GPU Worker Runbook

## Health
- `GET /healthz` should return `{ok:true}`
- `GET /readyz` checks artifact root and optional S3

## Common issues
- Out of disk space under `/data`: purge old artifacts or mount larger volume
- S3 upload failures: verify credentials and bucket policy

## Scaling
- Horizontal scaling via Deployment replicas; orchestrator round-robins
