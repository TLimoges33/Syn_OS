#!/usr/bin/env bash
set -euo pipefail

# Disable rulesets and remove classic branch protections across repos
# Usage:
#   ./scripts/gh_unprotect_all.sh OWNER REPO1 [REPO2 ...]
# Defaults to OWNER=TLimoges33 and repos: SynOS SynapticOS SynOS_Master-Archive-Vault

OWNER="${1:-TLimoges33}"
shift || true
REPOS=("${@:-SynOS SynapticOS SynOS_Master-Archive-Vault}")

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found. Install https://cli.github.com/ and authenticate: gh auth login" >&2
  exit 1
fi

if ! gh auth status -h github.com >/dev/null 2>&1; then
  echo "gh not authenticated. Run: gh auth login" >&2
  exit 1
fi

for REPO in "${REPOS[@]}"; do
  echo "=== ${OWNER}/${REPO} ==="

  # Disable active rulesets (ignore if endpoint missing)
  if IDS=$(gh api -H "Accept: application/vnd.github+json" \
      "/repos/${OWNER}/${REPO}/rulesets" --jq ".[] | select(.enforcement==\"active\") | .id" 2>/dev/null || true); then
    if [ -n "${IDS:-}" ]; then
      while read -r id; do
        [ -z "$id" ] && continue
        echo "- disable ruleset $id"
        gh api -X PATCH -H "Accept: application/vnd.github+json" \
          "/repos/${OWNER}/${REPO}/rulesets/${id}" -f enforcement=disabled >/dev/null || true
      done <<<"$IDS"
    else
      echo "- no active rulesets"
    fi
  else
    echo "- rulesets endpoint unavailable"
  fi

  # Remove classic protections on all branches
  if BRANCHES=$(gh api -H "Accept: application/vnd.github+json" \
      "/repos/${OWNER}/${REPO}/branches?per_page=100" --jq ".[ ].name" 2>/dev/null || true); then
    if [ -z "${BRANCHES:-}" ]; then
      echo "- no branches found"
    else
      while read -r br; do
        [ -z "$br" ] && continue
        status=$(gh api -X GET -H "Accept: application/vnd.github+json" \
          "/repos/${OWNER}/${REPO}/branches/${br}/protection" -i 2>/dev/null | head -n1 || true)
        if echo "$status" | grep -q " 200 "; then
          echo "  * $br: remove"
          gh api -X DELETE -H "Accept: application/vnd.github+json" \
            "/repos/${OWNER}/${REPO}/branches/${br}/protection" >/dev/null || true
        else
          echo "  * $br: none"
        fi
      done <<<"$BRANCHES"
    fi
  else
    echo "- branch list unavailable"
  fi
done

echo "Done."
