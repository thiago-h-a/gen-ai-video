
# ADR 0002 — S3 Presigned URLs for Artifacts

## Context
Serving media via the API layer increases egress and resource usage and
complicates caching.

## Decision
Store artifacts in S3 and return keys. Web/API issues presigned URLs for
direct client access.

## Consequences
- Buckets must be private and locked down
- Expired links require re-issue
- CDN can be added later for scale
