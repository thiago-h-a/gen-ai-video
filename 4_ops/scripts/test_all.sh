
#!/usr/bin/env bash
set -euo pipefail
echo "Running smoke tests..."
bash $(dirname $0)/smoke.sh
echo "Done."
