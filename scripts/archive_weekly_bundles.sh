#!/usr/bin/env bash
set -euo pipefail

# Create commit-by-commit incremental git bundles for a repo's default branch (first-parent chain),
# compress and chunk them, and upload as GitHub Release assets in the Archive Vault repo.
#
# Usage:
#   OWNER=TLimoges33 VAULT_REPO=SynOS_Master-Archive-Vault ./scripts/archive_weekly_bundles.sh <DEV_TEAM_REPO_NAME>
# Env vars:
#   OWNER           GitHub owner (default: TLimoges33)
#   VAULT_REPO      Archive Vault repository (default: SynOS_Master-Archive-Vault)
#   CHUNK_MB        Chunk size in MB for split (default: 500)
#   START_DATE      Optional ISO date to start from (e.g., 2023-01-01). If unset, starts at repo root.
#   MAX_WEEKS       Max commits to process (reusing var name for simplicity)

OWNER="${OWNER:-TLimoges33}"
VAULT_REPO="${VAULT_REPO:-SynOS_Master-Archive-Vault}"
CHUNK_MB="${CHUNK_MB:-500}"
VERBOSE="${VERBOSE:-0}"
DRY_RUN="${DRY_RUN:-0}"
MAX_WEEKS="${MAX_WEEKS:-0}"  # 0 = no limit
RETRIES="${RETRIES:-3}"
SLEEP_BETWEEN="${SLEEP_BETWEEN:-0}"  # seconds between uploads
DEV_REPO="${1:-}"
if [ -z "$DEV_REPO" ]; then echo "Usage: $0 <DEV_TEAM_REPO_NAME>" >&2; exit 1; fi

if ! command -v gh >/dev/null 2>&1; then echo "gh CLI not found" >&2; exit 1; fi
if ! gh auth status -h github.com >/dev/null 2>&1; then echo "gh not authenticated (gh auth login)" >&2; exit 1; fi
# Compression tool check (prefer xz, fallback to gzip)
COMPRESSOR="${COMPRESSOR:-xz}"
if ! command -v xz >/dev/null 2>&1; then COMPRESSOR=gzip; fi
case "$COMPRESSOR" in
  xz)
    COMP_CMD=(xz -T0 -9e -f)
    COMP_EXT=xz
    ;;
  gzip)
    COMP_CMD=(gzip -9 -f)
    COMP_EXT=gz
    ;;
  *)
    echo "Unsupported COMPRESSOR=$COMPRESSOR (use xz or gzip)" >&2
    exit 1
    ;;
esac

TOKEN=$(gh auth token)
WORKDIR=$(mktemp -d -t weekly-archive-XXXXXX)
trap 'rm -rf "$WORKDIR"' EXIT

SRC_URL="https://x-access-token:${TOKEN}@github.com/${OWNER}/${DEV_REPO}.git"
# Sanity: ensure Vault repo is reachable
if ! gh repo view "${OWNER}/${VAULT_REPO}" >/dev/null 2>&1; then
  echo "Vault repo ${OWNER}/${VAULT_REPO} not found or not accessible" >&2
  exit 1
fi
echo "Cloning (mirror) ${OWNER}/${DEV_REPO} ..."
git clone -q --mirror "$SRC_URL" "$WORKDIR/repo.git"
cd "$WORKDIR/repo.git"

DEFAULT_BRANCH=$(gh repo view "${OWNER}/${DEV_REPO}" --json defaultBranchRef --jq .defaultBranchRef.name)
if [ -z "${DEFAULT_BRANCH:-}" ]; then echo "Could not determine default branch for ${DEV_REPO}" >&2; exit 1; fi

# Build list of commits on first-parent of default branch in chronological order with ISO dates
mapfile -t COMMITS < <(git log --first-parent --reverse "refs/heads/${DEFAULT_BRANCH}" --pretty=format:'%H %ai')
if [ ${#COMMITS[@]} -eq 0 ]; then echo "No commits found on ${DEFAULT_BRANCH}" >&2; exit 0; fi
if [ "$VERBOSE" = "1" ]; then echo "Commits on ${DEFAULT_BRANCH}: ${#COMMITS[@]}"; fi

# Optional START_DATE filter
START_IDX=0
if [ -n "${START_DATE:-}" ]; then
  for i in "${!COMMITS[@]}"; do
    ts=$(echo "${COMMITS[$i]}" | awk '{print $2" "$3" "$4" "$5" "$6}')
    if [ "$(date -d "$ts" +%s)" -ge "$(date -d "$START_DATE" +%s)" ]; then START_IDX=$i; break; fi
  done
fi

# Create incremental bundles per commit:
# For each commit, bundle range: ^<prev_commit> <current_commit>
prev_commit=""

upload_commit_release() {
  local commit_sha="$1" base_sha="$2" ts="$3"
  local short_sha="${commit_sha:0:12}"
  local tag="archive-${DEV_REPO}-${short_sha}"
  local title="Archive ${DEV_REPO} ${short_sha}"
  local refname="refs/tags/arch-commit/${short_sha}"
  local bundle_name="${DEV_REPO}-${short_sha}.bundle"
  local desc_file="$WORKDIR/${DEV_REPO}-${short_sha}-manifest.json"

  echo "- creating bundle for commit ${short_sha} ($(date -d "$ts" +%Y-%m-%d))"
  # Create a temporary tag for the commit to carry a named ref inside the bundle
  git tag -f "arch-commit/${short_sha}" "$commit_sha" >/dev/null
  
  # Create bundle with explicit base prerequisite if available
  if [ -n "$base_sha" ]; then
    git bundle create "$WORKDIR/$bundle_name" "$refname" "^$base_sha" >/dev/null
  else
    # first commit: include just this commit (no history)
    git bundle create "$WORKDIR/$bundle_name" "$refname" >/dev/null
  fi

  # Compress and chunk
  "${COMP_CMD[@]}" "$WORKDIR/$bundle_name"
  local comp_name="$WORKDIR/$bundle_name.$COMP_EXT"
  local parts_dir="$WORKDIR/${bundle_name%.bundle}.parts"
  mkdir -p "$parts_dir"
  split -b "${CHUNK_MB}M" -d -a 3 "$comp_name" "$parts_dir/${bundle_name}.part."

  # Manifest JSON
  cat > "$desc_file" <<JSON
{
  "repo": "${DEV_REPO}",
  "default_branch": "${DEFAULT_BRANCH}",
  "commit_sha": "${commit_sha}",
  "base_sha": "${base_sha}",
  "timestamp": "${ts}",
  "ref": "${refname}",
  "compressor": "${COMPRESSOR}",
  "chunk_size_mb": ${CHUNK_MB},
  "parts": [
    $(printf '"%s"' $(basename -a "$parts_dir"/*) | sed 's/" "/", "/g')
  ]
}
JSON

  if [ "$DRY_RUN" = "1" ]; then
    echo "  DRY_RUN=1: skipping upload (would create tag $tag and upload $(ls -1 "$parts_dir" | wc -l) parts)"
    return 0
  fi
  # Create (or reuse) release in Vault and upload assets
  if ! gh release view "$tag" -R "${OWNER}/${VAULT_REPO}" >/dev/null 2>&1; then
    i=0; until gh release create "$tag" -R "${OWNER}/${VAULT_REPO}" -t "$title" -n "Incremental bundle for ${DEV_REPO} commit ${short_sha}" >/dev/null; do
      i=$((i+1)); [ "$i" -ge "$RETRIES" ] && { echo "  failed to create release $tag after $RETRIES attempts" >&2; return 1; }
      sleep $((2*i))
    done
  fi
  # Upload manifest with retries
  i=0; until gh release upload "$tag" -R "${OWNER}/${VAULT_REPO}" --clobber "$desc_file" >/dev/null; do
    i=$((i+1)); [ "$i" -ge "$RETRIES" ] && { echo "  failed to upload manifest for $tag after $RETRIES attempts" >&2; return 1; }
    sleep $((2*i))
  done
  # Upload parts with retries
  for part in "$parts_dir"/*; do
    [ -f "$part" ] || continue
    i=0; until gh release upload "$tag" -R "${OWNER}/${VAULT_REPO}" --clobber "$part" >/dev/null; do
      i=$((i+1)); [ "$i" -ge "$RETRIES" ] && { echo "  failed to upload part $(basename "$part") for $tag after $RETRIES attempts" >&2; return 1; }
      sleep $((2*i))
    done
    [ "$SLEEP_BETWEEN" -gt 0 ] && sleep "$SLEEP_BETWEEN"
  done
  echo "  uploaded: ${tag} (${DEV_REPO} commit ${short_sha})"
}

COMMIT_COUNT=0
for ((i=START_IDX; i<${#COMMITS[@]}; i++)); do
  sha=$(echo "${COMMITS[$i]}" | awk '{print $1}')
  ts=$(echo "${COMMITS[$i]}" | awk '{print $2" "$3" "$4" "$5" "$6}')

  # Upload commit bundle
  upload_commit_release "$sha" "$prev_commit" "$ts"
  COMMIT_COUNT=$((COMMIT_COUNT+1))
  if [ "$MAX_WEEKS" -gt 0 ] && [ "$COMMIT_COUNT" -ge "$MAX_WEEKS" ]; then
    echo "Reached MAX_WEEKS=$MAX_WEEKS commit limit; stopping."
    exit 0
  fi
  prev_commit="$sha"
done

echo "Completed commit-by-commit archive for ${DEV_REPO}"
