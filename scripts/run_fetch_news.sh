#!/usr/bin/env bash

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$REPO_DIR/logs"
LOG_FILE="$LOG_DIR/fetch.log"
PYTHON_BIN="$REPO_DIR/.venv/bin/python"

mkdir -p "$LOG_DIR"
cd "$REPO_DIR"

if [ -x "$PYTHON_BIN" ]; then
  "$PYTHON_BIN" pipeline.py --skip-sentiment >> "$LOG_FILE" 2>&1
else
  python pipeline.py --skip-sentiment >> "$LOG_FILE" 2>&1
fi
