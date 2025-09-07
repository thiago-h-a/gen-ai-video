
#!/usr/bin/env bash
set -euo pipefail
: "${RELEASE:?Usage: RELEASE=v0.1.0 $0}"
git tag -a "$RELEASE" -m "release $RELEASE"
git push origin "$RELEASE"
