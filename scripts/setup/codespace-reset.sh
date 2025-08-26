#!/bin/bash
# Reset Codespace environment to a clean state
set -euo pipefail

echo "[Codespace Reset] Cleaning up..."
git clean -xfd
rm -rf ~/.local/bin/* ~/.cargo/* ~/.config/* ~/.cache/* ~/.venv/*
echo "[Codespace Reset] Re-running setup scripts..."
bash .devcontainer/codespace-setup.sh
source ~/.bashrc
validate-env
echo "[Codespace Reset] Complete. Please reload your shell."
