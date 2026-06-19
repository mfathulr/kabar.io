#!/usr/bin/env bash

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$REPO_DIR/logs"
LOG_FILE="$LOG_DIR/fetch.log"
PYTHON_BIN="$REPO_DIR/.venv/bin/python"

mkdir -p "$LOG_DIR"
cd "$REPO_DIR"

if [ -z "${NEWSDATA_CATEGORIES:-}" ]; then
  case "$(date +%u)" in
    1)
      export NEWSDATA_ACTIVE_CATEGORY_SET="core_daily_plus_tail_a"
      export NEWSDATA_CATEGORIES="politics,business,technology,health,world,entertainment,sports,domestic,education"
      ;;
    2)
      export NEWSDATA_ACTIVE_CATEGORY_SET="core_daily_plus_tail_b"
      export NEWSDATA_CATEGORIES="politics,business,technology,health,world,crime,environment,food,lifestyle"
      ;;
    3)
      export NEWSDATA_ACTIVE_CATEGORY_SET="core_daily_plus_tail_c"
      export NEWSDATA_CATEGORIES="politics,business,technology,health,world,science,tourism,top,other"
      ;;
    4)
      export NEWSDATA_ACTIVE_CATEGORY_SET="core_daily_plus_tail_a"
      export NEWSDATA_CATEGORIES="politics,business,technology,health,world,entertainment,sports,domestic,education"
      ;;
    5)
      export NEWSDATA_ACTIVE_CATEGORY_SET="core_daily_plus_tail_b"
      export NEWSDATA_CATEGORIES="politics,business,technology,health,world,crime,environment,food,lifestyle"
      ;;
    6)
      export NEWSDATA_ACTIVE_CATEGORY_SET="core_daily_plus_tail_c"
      export NEWSDATA_CATEGORIES="politics,business,technology,health,world,science,tourism,top,other"
      ;;
    *)
      export NEWSDATA_ACTIVE_CATEGORY_SET="core_daily"
      export NEWSDATA_CATEGORIES="politics,business,technology,health,world"
      ;;
  esac
fi

if [ -x "$PYTHON_BIN" ]; then
  "$PYTHON_BIN" pipeline.py --skip-sentiment >> "$LOG_FILE" 2>&1
else
  python pipeline.py --skip-sentiment >> "$LOG_FILE" 2>&1
fi
