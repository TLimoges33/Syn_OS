#!/usr/bin/env bash
set -euo pipefail

# Vault sync script: verifies bundle checksum, pushes a bare mirror to Vault, and creates a release with assets.
# Config via env vars (override as needed):
#   BUNDLE   - path to the .bundle file (default: archive/bundles/wip-*.bundle)
#   SUMFILE  - path to the .sha256 file (default: ${BUNDLE}.sha256)
#   REPO_SLUG- owner/repo for Vault (default: TLimoges33/SynOS_Master-Archive-Vault)
#   VAULT_SSH- SSH URL for Vault (default: git@github.com:TLimoges33/SynOS_Master-Archive-Vault.git)
#   TAG      - release tag (default: archive-YYYY-MM-DD)
#   LOG_FILE - optional explicit logfile path (default: data/logs/vault_sync_<timestamp>.log)

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT_DIR"

default_bundle="archive/bundles/wip-f0f203abd3ab7d44e5a536782a0cda975f9cc66c.bundle"
BUNDLE=${BUNDLE:-$default_bundle}
SUMFILE=${SUMFILE:-"${BUNDLE}.sha256"}
REPO_SLUG=${REPO_SLUG:-"TLimoges33/SynOS_Master-Archive-Vault"}
VAULT_SSH=${VAULT_SSH:-"git@github.com:TLimoges33/SynOS_Master-Archive-Vault.git"}
TAG=${TAG:-"archive-$(date +%F)"}

LOG_DIR="$ROOT_DIR/data/logs"
mkdir -p "$LOG_DIR"
LOG_FILE=${LOG_FILE:-"$LOG_DIR/vault_sync_$(date +%F_%H-%M-%S).log"}

echo "[START] $(date -Is) Vault sync" | tee -a "$LOG_FILE"
echo "Root: $ROOT_DIR" | tee -a "$LOG_FILE"
echo "Bundle: $BUNDLE" | tee -a "$LOG_FILE"
echo "Sumfile: $SUMFILE" | tee -a "$LOG_FILE"
echo "Vault repo: $REPO_SLUG" | tee -a "$LOG_FILE"
echo "Tag: $TAG" | tee -a "$LOG_FILE"

if [[ ! -f "$BUNDLE" ]]; then echo "[ERROR] Missing bundle: $BUNDLE" | tee -a "$LOG_FILE"; exit 1; fi
if [[ ! -f "$SUMFILE" ]]; then echo "[ERROR] Missing checksum: $SUMFILE" | tee -a "$LOG_FILE"; exit 1; fi

echo "[INFO] Bundle size:" | tee -a "$LOG_FILE"
du -h "$BUNDLE" | tee -a "$LOG_FILE"
stat -c 'Bytes: %s' "$BUNDLE" | tee -a "$LOG_FILE" || true

echo "[STEP] Verifying bundle checksum..." | tee -a "$LOG_FILE"
EXPECTED=$(awk '{print $1}' "$SUMFILE" | head -n1)
echo "Expected: $EXPECTED" | tee -a "$LOG_FILE"

# Prefer dd with progress if available; fallback to sha256sum
if command -v dd >/dev/null 2>&1; then
  echo "[INFO] Computing SHA-256 with dd status=progress (this may take time)..." | tee -a "$LOG_FILE"
  ACTUAL=$(dd if="$BUNDLE" bs=64M status=progress 2>/dev/stdout | sha256sum | awk '{print $1}')
else
  echo "[INFO] Computing SHA-256 with sha256sum (no progress)..." | tee -a "$LOG_FILE"
  ACTUAL=$(sha256sum "$BUNDLE" | awk '{print $1}')
fi

echo "Actual:   $ACTUAL" | tee -a "$LOG_FILE"
if [[ "$ACTUAL" != "$EXPECTED" ]]; then
  echo "[ERROR] Checksum mismatch" | tee -a "$LOG_FILE"
  exit 1
fi
echo "[OK] Checksum verified" | tee -a "$LOG_FILE"

echo "[STEP] Creating bare mirror from bundle..." | tee -a "$LOG_FILE"
WORKDIR=$(mktemp -d)
echo "Workdir: $WORKDIR" | tee -a "$LOG_FILE"
git clone --bare "$ROOT_DIR/$BUNDLE" "$WORKDIR/vault-mirror.git" >>"$LOG_FILE" 2>&1
cd "$WORKDIR/vault-mirror.git"
git remote add origin "$VAULT_SSH"

echo "[STEP] Pushing --mirror to Vault (dry-run then real)..." | tee -a "$LOG_FILE"
if GIT_SSH_COMMAND='ssh -o StrictHostKeyChecking=accept-new' git push --mirror --dry-run origin >>"$LOG_FILE" 2>&1; then
  echo "[OK] Dry-run" | tee -a "$LOG_FILE"
else
  echo "[WARN] Dry-run failed; continuing to real push" | tee -a "$LOG_FILE"
fi

if GIT_SSH_COMMAND='ssh -o StrictHostKeyChecking=accept-new' git push --mirror origin >>"$LOG_FILE" 2>&1; then
  echo "[OK] Mirror push complete" | tee -a "$LOG_FILE"
else
  echo "[ERROR] Mirror push failed" | tee -a "$LOG_FILE"
  exit 1
fi

echo "[STEP] Tagging and pushing tag $TAG ..." | tee -a "$LOG_FILE"
git tag -f "$TAG" "$(git rev-parse --verify HEAD)" >>"$LOG_FILE" 2>&1 || true
GIT_SSH_COMMAND='ssh -o StrictHostKeyChecking=accept-new' git push -f origin "$TAG" >>"$LOG_FILE" 2>&1 || true

TITLE="Archive $(date +%F)"
BODY='Full repository archive mirror + original bundle and checksum.'
echo "[STEP] Creating/updating release and uploading assets..." | tee -a "$LOG_FILE"
if GH_PAGER= gh release create "$TAG" --repo "$REPO_SLUG" --title "$TITLE" --notes "$BODY" \
     "$ROOT_DIR/$BUNDLE" \
     "$ROOT_DIR/$SUMFILE" >>"$LOG_FILE" 2>&1; then
  echo "[OK] Release created with assets" | tee -a "$LOG_FILE"
else
  echo "[INFO] Release likely exists; attempting upload of assets..." | tee -a "$LOG_FILE"
  GH_PAGER= gh release upload "$TAG" --repo "$REPO_SLUG" \
     "$ROOT_DIR/$BUNDLE" \
     "$ROOT_DIR/$SUMFILE" >>"$LOG_FILE" 2>&1 || true
fi

echo "[STEP] Release URL:" | tee -a "$LOG_FILE"
GH_PAGER= gh release view "$TAG" --repo "$REPO_SLUG" --json url --jq .url | tee -a "$LOG_FILE" || true

echo "[DONE] $(date -Is)" | tee -a "$LOG_FILE"
