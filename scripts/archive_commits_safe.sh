#!/usr/bin/env bash
set -euo pipefail

# Safe commit-by-commit archiver with resource limits and batching
# Creates bundles for recent commits only, with system resource protection

OWNER="${OWNER:-TLimoges33}"
VAULT_REPO="${VAULT_REPO:-SynOS_Master-Archive-Vault}"
CHUNK_MB="${CHUNK_MB:-100}"  # Smaller chunks
BATCH_SIZE="${BATCH_SIZE:-5}"  # Process 5 commits at a time
MAX_COMMITS="${MAX_COMMITS:-10}"  # Hard limit
DRY_RUN="${DRY_RUN:-1}"
SLEEP_BETWEEN="${SLEEP_BETWEEN:-2}"  # Longer delays

DEV_REPO="${1:-}"
if [ -z "$DEV_REPO" ]; then 
  echo "Usage: $0 <DEV_TEAM_REPO_NAME>" >&2
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then echo "gh CLI not found" >&2; exit 1; fi
if ! gh auth status -h github.com >/dev/null 2>&1; then echo "gh not authenticated" >&2; exit 1; fi

# Check available memory (basic safeguard)
if command -v free >/dev/null 2>&1; then
  AVAIL_MB=$(free -m | awk '/^Mem:/ {print $7}')
  if [ "${AVAIL_MB:-0}" -lt 500 ]; then
    echo "Warning: Low available memory (${AVAIL_MB}MB). Consider increasing SLEEP_BETWEEN or reducing BATCH_SIZE." >&2
  fi
fi

TOKEN=$(gh auth token)
WORKDIR=$(mktemp -d -t safe-archive-XXXXXX)
trap 'rm -rf "$WORKDIR"' EXIT

echo "Safe archiving ${DEV_REPO} (max ${MAX_COMMITS} commits, batches of ${BATCH_SIZE})"

SRC_URL="https://x-access-token:${TOKEN}@github.com/${OWNER}/${DEV_REPO}.git"
git clone -q --bare --depth=50 "$SRC_URL" "$WORKDIR/repo.git"  # Shallow clone
cd "$WORKDIR/repo.git"

DEFAULT_BRANCH=$(gh repo view "${OWNER}/${DEV_REPO}" --json defaultBranchRef --jq .defaultBranchRef.name)
if [ -z "${DEFAULT_BRANCH:-}" ]; then echo "Could not determine default branch" >&2; exit 1; fi

# Get recent commits only (last 50 or MAX_COMMITS, whichever is smaller)
LIMIT=$((MAX_COMMITS < 50 ? MAX_COMMITS : 50))
mapfile -t COMMITS < <(git log --first-parent "refs/heads/${DEFAULT_BRANCH}" --pretty=format:'%H %ai' -n "$LIMIT")
echo "Found ${#COMMITS[@]} recent commits"

process_commit_batch() {
  local batch_start="$1" batch_end="$2"
  echo "Processing batch: commits $batch_start to $batch_end"
  
  for ((i=batch_start; i<=batch_end && i<${#COMMITS[@]}; i++)); do
    sha=$(echo "${COMMITS[$i]}" | awk '{print $1}')
    ts=$(echo "${COMMITS[$i]}" | awk '{print $2" "$3}')  # Just date
    short_sha="${sha:0:12}"
    
    echo "  - commit $((i+1))/${#COMMITS[@]}: ${short_sha} ($ts)"
    
    if [ "$DRY_RUN" = "1" ]; then
      echo "    DRY_RUN: would create bundle and upload to archive-${DEV_REPO}-${short_sha}"
      continue
    fi
    
    # Create minimal bundle (just this commit vs parent)
    bundle_name="${DEV_REPO}-${short_sha}.bundle"
    parent_sha=$(git rev-parse "${sha}^" 2>/dev/null || echo "")
    
    if [ -n "$parent_sha" ]; then
      git bundle create "$WORKDIR/$bundle_name" "$sha" "^$parent_sha" >/dev/null 2>&1 || {
        echo "    Warning: failed to create bundle for $short_sha; skipping"
        continue
      }
    else
      # Root commit - create bundle with just this commit
      git bundle create "$WORKDIR/$bundle_name" "$sha" >/dev/null 2>&1 || {
        echo "    Warning: failed to create bundle for $short_sha; skipping"
        continue
      }
    fi
    
    # Compress (simple gzip to avoid xz memory usage)
    gzip -f "$WORKDIR/$bundle_name"
    
    # Simple manifest
    cat > "$WORKDIR/${DEV_REPO}-${short_sha}-manifest.json" <<JSON
{
  "repo": "${DEV_REPO}",
  "commit_sha": "${sha}",
  "parent_sha": "${parent_sha}",
  "timestamp": "${ts}",
  "bundle_file": "${bundle_name}.gz"
}
JSON
    
    # Upload to release
    tag="archive-${DEV_REPO}-${short_sha}"
    if ! gh release view "$tag" -R "${OWNER}/${VAULT_REPO}" >/dev/null 2>&1; then
      gh release create "$tag" -R "${OWNER}/${VAULT_REPO}" -t "Archive ${DEV_REPO} ${short_sha}" -n "Single commit bundle" >/dev/null || {
        echo "    Warning: failed to create release $tag; skipping"
        continue
      }
    fi
    
    gh release upload "$tag" -R "${OWNER}/${VAULT_REPO}" --clobber \
      "$WORKDIR/${bundle_name}.gz" \
      "$WORKDIR/${DEV_REPO}-${short_sha}-manifest.json" >/dev/null || {
      echo "    Warning: failed to upload to $tag; skipping"
      continue
    }
    
    echo "    uploaded: $tag"
    sleep "$SLEEP_BETWEEN"
  done
}

# Process in batches
for ((start=0; start<${#COMMITS[@]}; start+=BATCH_SIZE)); do
  end=$((start + BATCH_SIZE - 1))
  process_commit_batch "$start" "$end"
  
  # Longer sleep between batches
  if [ "$DRY_RUN" = "0" ] && [ $((end + 1)) -lt ${#COMMITS[@]} ]; then
    echo "Batch complete. Sleeping 5 seconds before next batch..."
    sleep 5
  fi
done

echo "Safe archive complete for ${DEV_REPO}"
