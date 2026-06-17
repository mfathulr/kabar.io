#!/usr/bin/env bash

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$REPO_DIR/logs"
LOG_FILE="$LOG_DIR/pipeline.log"
PYTHON_BIN="$REPO_DIR/.venv/bin/python"

mkdir -p "$LOG_DIR"
cd "$REPO_DIR"

if [ -x "$PYTHON_BIN" ]; then
  "$PYTHON_BIN" pipeline.py >> "$LOG_FILE" 2>&1
else
  python pipeline.py >> "$LOG_FILE" 2>&1
fi
