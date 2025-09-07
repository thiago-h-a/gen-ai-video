
# API — Orchestrator

Base: `http://localhost:8084`

| Method | Path           | Description |
|--------|----------------|-------------|
| GET    | /healthz       | Liveness |
| POST   | /tick?max=N    | Process up to N jobs |
| POST   | /dispatch/test | Call first worker (dry-run) |
