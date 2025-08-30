#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT_DIR"

PLAN_FILE=${PLAN_FILE:-root_cleanup_plan.txt}
DRY_RUN=${DRY_RUN:-1}

if [ ! -f "$PLAN_FILE" ]; then
  echo "Plan file $PLAN_FILE not found. Generate it with scripts/plan_root_cleanup.sh" >&2
  exit 1
fi

echo "Using plan: $PLAN_FILE (DRY_RUN=$DRY_RUN)"

while IFS= read -r line; do
  # Skip comments/blank lines
  [[ -z "$line" || "$line" =~ ^# ]] && continue
  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY-RUN: $line"
  else
    # Ensure destination directory exists
    dest_dir=$(echo "$line" | awk '{print $NF}' | xargs dirname)
    mkdir -p "$dest_dir"
    eval "$line"
  fi
done < "$PLAN_FILE"

echo "Done."
