#!/usr/bin/env bash
set -euo pipefail

# Simple mirror script: commit current changes, sync branches, skip heavy archival
# Focus on getting repos aligned quickly

OWNER="${OWNER:-TLimoges33}"
echo "=== Phase A: Commit and Push Current Work ==="

# Commit current scripts and fixes
if ! git diff --cached --quiet || ! git diff --quiet; then
  git add -A
  git -c user.email="synos-bot@example.com" -c user.name="synos-bot" \
    commit -m "feat: archive scripts + compose fixes + protections helper"
  git push origin "$(git rev-parse --abbrev-ref HEAD)"
  echo "✓ Committed and pushed current work"
else
  echo "✓ No local changes to commit"
fi

echo -e "\n=== Phase B: Sync Dev-Team to Primary Repos ==="

# Get current Dev-Team repos
mapfile -t DEV_REPOS < <(gh repo list "$OWNER" --limit 200 --json name \
  --jq '.[] | select(.name | endswith("-Dev-Team")) | .name')

echo "Found ${#DEV_REPOS[@]} Dev-Team repos to sync"

for DEV in "${DEV_REPOS[@]}"; do
  # Map to primary repo name
  case "$DEV" in
    Syn_OS-Dev-Team) PRIMARY="Syn_OS";;
    SynapticOS-Dev-Team) PRIMARY="SynapticOS";;
    *) PRIMARY="${DEV%-Dev-Team}";;
  esac
  
  echo -e "\n--- $DEV -> $PRIMARY ---"
  
  # Check if primary repo exists
  if ! gh repo view "${OWNER}/${PRIMARY}" >/dev/null 2>&1; then
    echo "⚠️  Primary repo ${OWNER}/${PRIMARY} not found; skipping"
    continue
  fi
  
  # Get default branch and latest commit from Dev-Team repo
  DEFAULT_BRANCH=$(gh repo view "${OWNER}/${DEV}" --json defaultBranchRef --jq .defaultBranchRef.name)
  LATEST_SHA=$(gh api "/repos/${OWNER}/${DEV}/git/refs/heads/${DEFAULT_BRANCH}" --jq .object.sha)
  
  echo "📍 Dev-Team default: ${DEFAULT_BRANCH} @ ${LATEST_SHA:0:12}"
  
  # Remove protections on primary repo
  echo "🔓 Removing protections..."
  ./scripts/gh_unprotect_all.sh "${OWNER}" "${PRIMARY}" || true
  
  # Create/update branches on primary repo (dev-team, main, master) to point to latest Dev-Team commit
  echo "🔄 Syncing branches..."
  
  # Create branches pointing to the Dev-Team latest commit
  for BRANCH in dev-team main master; do
    gh api -X PATCH "/repos/${OWNER}/${PRIMARY}/git/refs/heads/${BRANCH}" \
      -f sha="$LATEST_SHA" >/dev/null 2>&1 || \
    gh api -X POST "/repos/${OWNER}/${PRIMARY}/git/refs" \
      -f ref="refs/heads/${BRANCH}" -f sha="$LATEST_SHA" >/dev/null 2>&1 || \
    echo "  ⚠️  Failed to create/update $BRANCH"
  done
  
  # Verify the sync
  echo "✅ Verification:"
  for BRANCH in dev-team main master; do
    CURRENT_SHA=$(gh api "/repos/${OWNER}/${PRIMARY}/git/refs/heads/${BRANCH}" --jq .object.sha 2>/dev/null || echo "missing")
    if [ "$CURRENT_SHA" = "$LATEST_SHA" ]; then
      echo "  ✓ $BRANCH: ${CURRENT_SHA:0:12}"
    else
      echo "  ❌ $BRANCH: ${CURRENT_SHA:0:12} (expected ${LATEST_SHA:0:12})"
    fi
  done
done

echo -e "\n=== Phase C: Clean Root Directory ==="
./scripts/plan_root_cleanup.sh
echo "📋 Cleanup plan generated. Review with: less root_cleanup_plan.txt"
echo "🧹 Apply with: DRY_RUN=1 ./scripts/apply_root_cleanup.sh"

echo -e "\n✅ Mirror sync complete!"
echo "Next steps:"
echo "1. Review cleanup plan: less root_cleanup_plan.txt" 
echo "2. Apply cleanup: DRY_RUN=0 ./scripts/apply_root_cleanup.sh"
echo "3. Verify branch alignment on GitHub"
