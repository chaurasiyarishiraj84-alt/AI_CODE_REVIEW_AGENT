#!/usr/bin/env bash
# Production entrypoint: fast proxy on $PORT, Streamlit on $PORT+1.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PORT="${PORT:-5000}"

echo "==> Starting proxy+Streamlit via proxy.py on port ${PORT} …"
exec python "${SCRIPT_DIR}/proxy.py"