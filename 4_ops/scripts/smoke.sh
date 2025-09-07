
#!/usr/bin/env bash
set -euo pipefail
BASE=${BASE:-http://localhost:8080}
echo "[smoke] GET $BASE/healthz (gateway)"
curl -fsS "$BASE/healthz" || true
echo
echo "[smoke] POST /api/prompts"
JOB=$(curl -fsS -X POST "$BASE/api/prompts" -H 'content-type: application/json' -d '{"prompt":"a robot violinist","model_id":"base-v1"}') || true
echo "$JOB"
echo "Done."
