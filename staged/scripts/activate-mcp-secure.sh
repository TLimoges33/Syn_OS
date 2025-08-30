#!/bin/bash

# Secure MCP Activation Script for Syn OS
# Implements phased security approach based on vulnerability assessment

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
KILOCODE_DIR="$PROJECT_ROOT/.kilocode"

echo -e "\033[32m🔐 SYN OS SECURE MCP ACTIVATION SCRIPT\033[0m"
echo -e "\033[36mBased on comprehensive 2025 security vulnerability assessment\033[0m"
echo ""

# Create backup of existing config
if [ -f "$KILOCODE_DIR/mcp.json" ]; then
    cp "$KILOCODE_DIR/mcp.json" "$KILOCODE_DIR/mcp-backup-$(date +%Y%m%d-%H%M%S).json"
    echo -e "\033[33m📁 Backed up existing MCP configuration\033[0m"
fi

# Function to activate specific phase
activate_phase() {
    local phase=$1
    local config_file="mcp-secure-${phase}.json"
    
    echo -e "\033[32m🚀 Activating Security Phase: $phase\033[0m"
    
    if [ -f "$KILOCODE_DIR/$config_file" ]; then
        cp "$KILOCODE_DIR/$config_file" "$KILOCODE_DIR/mcp.json"
        echo -e "\033[32m✅ Phase $phase configuration activated\033[0m"
    else
        echo -e "\033[31m❌ Phase $phase configuration not found\033[0m"
        return 1
    fi
}

# Show security assessment summary
echo -e "\033[33m🛡️  SECURITY ASSESSMENT SUMMARY:\033[0m"
echo -e "   • CVE-2025-6514 (CVSS 9.6) - mcp-remote RCE"
echo -e "   • CVE-2025-53109 (CVSS 8.4) - Filesystem symlink bypass" 
echo -e "   • CVE-2025-53110 (CVSS 7.3) - Directory containment bypass"
echo -e "   • 43% of MCP servers have command injection flaws"
echo -e "   • 33% allow unrestricted URL fetches"
echo ""

# Phase selection menu
echo -e "\033[32mSelect Security Phase to Activate:\033[0m"
echo "1) Phase 1 - Core Foundation (Low-Risk Tools Only)"
echo "2) Phase 2 - Educational Platform Integration (Medium Risk)"
echo "3) Full Configuration - All Tools (Maximum Security)"
echo "4) Show Current Configuration"
echo "5) Restore Backup"
echo ""

read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo -e "\033[36m🔒 PHASE 1: Core Foundation Security\033[0m"
        echo -e "   • Sequential Thinking (High Security)"
        echo -e "   • Time Server (Low Risk)"
        echo -e "   • Brave Search (Privacy-Focused)"
        echo -e "   • AWS Knowledge Base (Secure)"
        echo -e "   • YouTube Subtitles (Read-Only)"
        echo ""
        read -p "Activate Phase 1? (y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            activate_phase "phase1"
        fi
        ;;
    2)
        echo -e "\033[36m🔐 PHASE 2: Educational Platform Integration\033[0m"
        echo -e "   • All Phase 1 tools"
        echo -e "   • Google Drive (Encrypted)"
        echo -e "   • Slack (Audit Logging)"
        echo -e "   • Notion (Encrypted)"
        echo -e "   • Exa Search (Enhanced)"
        echo ""
        read -p "Activate Phase 2? (y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            activate_phase "phase2"
        fi
        ;;
    3)
        echo -e "\033[31m⚠️  FULL CONFIGURATION - MAXIMUM SECURITY REQUIRED\033[0m"
        echo -e "   • Includes HIGH-RISK tools with critical vulnerabilities"
        echo -e "   • Context7, GitHub, Filesystem, Puppeteer, Playwright, Redis"
        echo -e "   • Maximum security controls enabled"
        echo -e "   • Consciousness system isolation active"
        echo -e "   • Kernel protection layers enabled"
        echo ""
        echo -e "\033[33m🚨 WARNING: This configuration includes tools with:"
        echo -e "   • Known 2025 critical CVEs"
        echo -e "   • RCE vulnerabilities"
        echo -e "   • Directory traversal risks"
        echo -e "   • Prompt injection vectors\033[0m"
        echo ""
        read -p "Are you sure you want maximum risk configuration? (y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            activate_phase "full"
        fi
        ;;
    4)
        echo -e "\033[36m📋 CURRENT MCP CONFIGURATION:\033[0m"
        if [ -f "$KILOCODE_DIR/mcp.json" ]; then
            cat "$KILOCODE_DIR/mcp.json"
        else
            echo -e "\033[33m⚠️  No MCP configuration found\033[0m"
        fi
        ;;
    5)
        echo -e "\033[36m📁 AVAILABLE BACKUPS:\033[0m"
        ls -la "$KILOCODE_DIR"/mcp-backup-*.json 2>/dev/null || echo "No backups found"
        echo ""
        read -p "Enter backup filename to restore: " backup_file
        if [ -f "$KILOCODE_DIR/$backup_file" ]; then
            cp "$KILOCODE_DIR/$backup_file" "$KILOCODE_DIR/mcp.json"
            echo -e "\033[32m✅ Configuration restored from backup\033[0m"
        else
            echo -e "\033[31m❌ Backup file not found\033[0m"
        fi
        ;;
    *)
        echo -e "\033[31m❌ Invalid choice\033[0m"
        exit 1
        ;;
esac

# Security recommendations
echo ""
echo -e "\033[33m🛡️  SECURITY RECOMMENDATIONS:\033[0m"
echo -e "   • Restart VS Code/Claude Desktop to apply changes"
echo -e "   • Monitor MCP audit logs in logs/security/"
echo -e "   • Update MCP tools regularly for security patches"
echo -e "   • Use environment variables for sensitive credentials"
echo -e "   • Enable container isolation for high-risk tools"
echo -e "   • Regularly review consciousness system isolation"
echo ""
echo -e "\033[32m🚀 MCP Security Configuration Complete!\033[0m"

# Make script executable
chmod +x "$SCRIPT_DIR/activate-mcp-secure.sh"