#!/bin/bash
# Script Directory Quick Reference
# This script helps you quickly find and execute scripts in the organized structure

echo "=== Syn OS Scripts Directory ==="
echo ""
echo "📁 Available Categories:"
echo "  core/          - Main system tools and Claude integration"
echo "  setup/         - Initial setup and configuration"
echo "  ebpf/          - eBPF testing and monitoring"
echo "  merge/         - Git merge and branch management"
echo "  optimization/  - System and code optimization"
echo "  backup/        - Backup and recovery"
echo "  audit/         - Code and security audits"
echo "  documentation/ - Documentation management"
echo "  build/         - Build and compilation"
echo "  repo/          - Repository management"
echo "  maintenance/   - System maintenance and cleanup"
echo ""
echo "📂 Specialized directories:"
echo "  development/       - Development tools"
echo "  monitoring/        - System monitoring"
echo "  security-automation/ - Security automation"
echo "  systemd/          - Systemd services"
echo ""
echo "Usage: ./index.sh [category] to list scripts in a category"
echo "       ./index.sh help for more information"
echo ""

if [ "$1" = "help" ]; then
    echo "Examples:"
    echo "  ./index.sh core      # List core scripts"
    echo "  ./index.sh setup     # List setup scripts"
    echo "  ./index.sh           # Show this overview"
elif [ -n "$1" ] && [ -d "$1" ]; then
    echo "📋 Scripts in $1/:"
    find "$1" -maxdepth 1 -type f \( -name "*.sh" -o -name "*.py" -o -name "claude" \) -exec basename {} \; | sort
elif [ -n "$1" ]; then
    echo "❌ Category '$1' not found. Available categories listed above."
fi
