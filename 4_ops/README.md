
# ops/

Operational tooling for **ai-microgen**: scripts, CI/CD, monitors, and
runbooks.

## Makefile targets

```bash
make help           # list targets
make fmt            # format code where applicable
make lint           # run static checks
make test           # run smoke/unit tests
make build          # docker build all service images
make push           # docker push (requires registry login)
make tag RELEASE=v0.1.0
```

## CI/CD
- GitHub Actions workflows are under `ops/gha/.github/workflows/`.
- They call `make` targets defined here.

## Monitoring
- Prometheus alert rules in `ops/monitoring/prometheus/alerts.yml`.
- Grafana dashboard skeleton in `ops/monitoring/grafana/dashboards/`.

## Observability
- `ops/observability/otel-collector-config.yaml` — OTLP receiver + exporters.

## Runbooks
- `runbooks/incident-response.md`
- `runbooks/queue-drain.md`
- `runbooks/gpu-worker-runbook.md`
