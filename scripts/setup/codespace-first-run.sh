#!/bin/bash
# First run setup for Codespace
set -euo pipefail

echo "[Codespace First Run] Sourcing environment..."
source ~/.bashrc
echo "[Codespace First Run] Validating environment..."
validate-env
echo "[Codespace First Run] Checking VS Code extensions..."
code --list-extensions | grep -E 'copilot|kilo|continue' || echo "[Codespace First Run] Some extensions may be missing."
echo "[Codespace First Run] Setup complete. Ready for development!"
