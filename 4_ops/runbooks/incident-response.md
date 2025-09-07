
# Incident Response Runbook

## When to page
- Queue depth grows continuously for >10 minutes
- Errors from orchestrator or GPU workers spike above baseline

## First steps (30 min)
1. Check Redis health and queue length.
2. Check orchestrator logs for dispatch failures.
3. Verify GPU workers `/healthz` and `/readyz`.
4. Verify Notify Service and Web/API liveness.

## Mitigations
- Scale GPU workers (see `deploy/scripts/scale_workers.sh`).
- Pause new prompt submissions temporarily (Web/API feature-flag).
- Drain queue (see `queue-drain.md`).

## Postmortem
- Within 48 hours, document timeline, impact, root cause, and fix.
