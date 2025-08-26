#!/bin/bash
# Manual sync to master repository
echo "🔄 Manual sync to master repository"
git fetch dev-team main
git checkout master
git merge dev-team/main --no-ff -m "Manual sync: Dev team integration"
git push origin master
echo "✅ Sync complete"
