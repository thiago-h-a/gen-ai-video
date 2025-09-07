
# Security & Access

- **IRSA** enforces least privilege per service:
  - Web/API: read artifacts from S3
  - Workers: write artifacts to S3
  - Model Catalog: read SMR + DynamoDB
  - Prompt & Fair Scheduler: no AWS data access required
- **AuthN/Z** (future): front Web/API with OIDC, propagate `X-User-Id` for `creator_id`.
- **Data**:
  - S3: SSE AES‑256
  - Redis: TLS in ElastiCache (enabled by default in Terraform module)
  - DDB: SSE default
  - SMR: managed by SageMaker
