#!/usr/bin/env bash
set -euo pipefail

# Remove stray garbage files accidentally created by broken one-liners (containing spaces, quotes, or command fragments)
git status -z --porcelain | awk -v RS='\0' '$1=="??"{print substr($0,4)}' |
  grep -E 'git tag -f|; git tag -f|^"|^\s*else|^\s*echo' || true |
  while IFS= read -r path; do
    [ -z "$path" ] && continue
    if [ -e "$path" ] || [ -L "$path" ]; then
      echo "Removing stray file: $path"
      rm -rf -- "$path"
    fi
  done

echo "Stray cleanup complete."
