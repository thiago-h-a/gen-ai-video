
#!/usr/bin/env bash
set -euo pipefail
echo "Starting stack via Docker Compose (full)"
docker compose -f ../deploy/compose/docker-compose.full.yml up --build
