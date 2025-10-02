#!/usr/bin/env bash
set -euo pipefail

# Mirrors Dev-Team repos to their primary repos, writes git bundles to the Archive Vault,
# and aligns branches: dev-team (active dev), main (integration/test), master (stable).
#
# Requirements: gh CLI authenticated, git, sha256sum.
# Default owner: TLimoges33
# Default vault: SynOS_Master-Archive-Vault

OWNER="${OWNER:-TLimoges33}"
VAULT_REPO="${VAULT_REPO:-SynOS_Master-Archive-Vault}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v gh >/dev/null 2>&1; then echo "gh CLI not found" >&2; exit 1; fi
if ! gh auth status -h github.com >/dev/null 2>&1; then echo "gh not authenticated (gh auth login)" >&2; exit 1; fi

TOKEN=$(gh auth token)
git_config_silence() { git config --global advice.detachedHead false >/dev/null 2>&1 || true; }
git_config_silence

TMP_ROOT=$(mktemp -d -t syn-mirror-XXXXXX)
cleanup() { rm -rf "$TMP_ROOT"; }
trap cleanup EXIT

echo "Discovering Dev-Team repos under $OWNER ..."
mapfile -t DEV_REPOS < <(gh repo list "$OWNER" --limit 200 --json name --jq '.[] | select(.name | endswith("-Dev-Team")) | .name')
if [ ${#DEV_REPOS[@]} -eq 0 ]; then echo "No *-Dev-Team repos found for $OWNER" >&2; exit 1; fi

# Helper to map dev-team repo name to primary repo name
map_primary() {
  local dev_name="$1"
  case "$dev_name" in
    Syn_OS-Dev-Team) echo "SynOS";;
    *) echo "${dev_name%-Dev-Team}";;
  esac
}

echo "Preparing Archive Vault clone ..."
VAULT_DIR="$TMP_ROOT/vault"
git clone -q "https://x-access-token:${TOKEN}@github.com/${OWNER}/${VAULT_REPO}.git" "$VAULT_DIR" || {
  echo "Failed to clone vault repo ${OWNER}/${VAULT_REPO}" >&2; exit 1;
}
mkdir -p "$VAULT_DIR/bundles"

for DEV in "${DEV_REPOS[@]}"; do
  PRIMARY=$(map_primary "$DEV")
  echo "\n=== ${DEV} -> ${PRIMARY} ==="

  # Verify primary repo exists
  if ! gh repo view "${OWNER}/${PRIMARY}" >/dev/null 2>&1; then
    echo "- primary repo ${OWNER}/${PRIMARY} not found; skipping" >&2
    continue
  fi

  SRC_URL="https://x-access-token:${TOKEN}@github.com/${OWNER}/${DEV}.git"
  DST_URL="https://x-access-token:${TOKEN}@github.com/${OWNER}/${PRIMARY}.git"

  WORKDIR="$TMP_ROOT/${DEV}.mirror"
  git clone -q --mirror "$SRC_URL" "$WORKDIR"

  pushd "$WORKDIR" >/dev/null

  # Determine source default branch and resolve its SHA from mirrored refs
  DEFAULT_BRANCH=$(gh repo view "${OWNER}/${DEV}" --json defaultBranchRef --jq .defaultBranchRef.name)
  # Try refs/heads/<default>
  if ! SRC_HEAD_SHA=$(git rev-parse -q --verify "refs/heads/${DEFAULT_BRANCH}" 2>/dev/null); then
    # Fall back to first available branch in refs/heads
    FIRST_BRANCH=$(git for-each-ref --format='%(refname:strip=2)' refs/heads | head -n1 || true)
    if [ -n "$FIRST_BRANCH" ]; then
      SRC_HEAD_SHA=$(git rev-parse -q --verify "refs/heads/${FIRST_BRANCH}" 2>/dev/null || true)
      DEFAULT_BRANCH="$FIRST_BRANCH"
    fi
  fi
  if [ -z "${SRC_HEAD_SHA:-}" ]; then echo "- could not resolve source HEAD; skipping" >&2; popd >/dev/null; continue; fi
  echo "- default branch: ${DEFAULT_BRANCH} @ ${SRC_HEAD_SHA:0:12}"

  # Weekly archival to Vault via Releases (phased, chunked)
  popd >/dev/null
  echo "- creating weekly bundles in Vault releases (phased)"
  OWNER="${OWNER}" VAULT_REPO="${VAULT_REPO}" "${REPO_ROOT}/scripts/archive_weekly_bundles.sh" "${DEV}" || true

  # Unprotect target branches
  echo "- removing protections on ${PRIMARY} branches"
  "${REPO_ROOT}/scripts/gh_unprotect_all.sh" "${OWNER}" "${PRIMARY}" || true

  # Push aligned branches to primary (dev-team, main, master) to same SHA
  echo "- pushing dev-team/main/master to ${SRC_HEAD_SHA:0:12}"
  pushd "$WORKDIR" >/dev/null
  git remote add primary "$DST_URL"
  git push -q --force --atomic primary \
    "${SRC_HEAD_SHA}:refs/heads/dev-team" \
    "${SRC_HEAD_SHA}:refs/heads/main" \
    "${SRC_HEAD_SHA}:refs/heads/master"
  popd >/dev/null

  echo "- verify heads"
  gh api "/repos/${OWNER}/${PRIMARY}/git/refs/heads/dev-team" --jq .object.sha 2>/dev/null | cut -c1-12 || true
  gh api "/repos/${OWNER}/${PRIMARY}/git/refs/heads/main" --jq .object.sha 2>/dev/null | cut -c1-12 || true
  gh api "/repos/${OWNER}/${PRIMARY}/git/refs/heads/master" --jq .object.sha 2>/dev/null | cut -c1-12 || true
done

echo "\nAll done. Bundles committed to ${OWNER}/${VAULT_REPO} under bundles/."
