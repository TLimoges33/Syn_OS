#!/bin/bash
# Quick Environment Status Check
# Usage: ./scripts/quick-status.sh

echo "SynOS Environment Quick Status"
echo "==============================="
echo "Memory: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
echo "Disk: $(df -h /home | tail -1 | awk '{print $3 "/" $2}')"
echo "FDs: $(lsof -u $(whoami) 2>/dev/null | wc -l) / $(ulimit -n)"
echo "VS Code: $(ps aux | grep -c '[c]ode') processes"
echo "Rust-analyzer: $(ps aux | grep '[r]ust-analyzer' | awk '{printf "%.0fMB", $6/1024}' | head -1 || echo 'not running')"
echo "Devices: $([ -c /dev/null ] && [ -c /dev/ptmx ] && echo '✓ OK' || echo '✗ ERROR')"
echo "PTYs: $(ls /dev/pts/ | wc -l) active"
