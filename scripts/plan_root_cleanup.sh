#!/usr/bin/env bash
set -euo pipefail

# Generate a non-destructive cleanup plan for the repo root.
# It suggests moving clutter into structured folders under archive/ and docs/.
# Writes a plan file with mv commands; can be consumed by apply_root_cleanup.sh.

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT_DIR"

PLAN_FILE=${PLAN_FILE:-root_cleanup_plan.txt}
> "$PLAN_FILE"

# Top-level items to keep in place
KEEP_DIRS=(
  ".git" ".github" "src" "services" "scripts" "docs" "docker" "config" "build" "tests" "test_suite" "integration"
  "phase4" "implementation" "tools" "tooling" "workspace" "security" "mcp" "cloud" "development" "deploy" "data"
)
KEEP_FILES=("README.md" "LICENSE" "SECURITY.md" "CODEOWNERS")

is_in_array() {
  local needle="$1"; shift; local x
  for x in "$@"; do [ "$x" = "$needle" ] && return 0; done
  return 1
}

mkdir -p archive/docs archive/legacy archive/integrations archive/research || true

echo "# Root cleanup plan generated on $(date -u)" >> "$PLAN_FILE"

shopt -s dotglob nullglob
for item in *; do
  # Skip allowed keeps
  if [ -d "$item" ]; then
    if is_in_array "$item" "${KEEP_DIRS[@]}"; then continue; fi
  else
    if is_in_array "$item" "${KEEP_FILES[@]}"; then continue; fi
  fi

  # Classify
  dest="archive/legacy"
  case "$item" in
    *.md)
      if [ -f "$item" ]; then dest="docs"; fi ;;
    academic_papers|reports|architecture|docs_old_backup|archive|results|test_reports)
      dest="archive/docs" ;;
    parrotos-*|parrotos*|synapticos-*|community|website|community|prototypes)
      dest="archive/integrations" ;;
    research_code|tests|testing)
      dest="archive/research" ;;
    build|data/cache|data/logs|data/logs-system|data/temporary)
      dest="archive/legacy" ;;
  esac

  # Don’t plan moving the archive root itself
  if [ "$item" = "archive" ]; then continue; fi

  # Propose move
  echo "mv -vn \"$item\" \"$dest/$item\"" >> "$PLAN_FILE"
done

echo "Plan written to $PLAN_FILE"
