#!/bin/bash
# MCP Configuration Switcher for Syn_OS

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

show_usage() {
    echo -e "${BLUE}MCP Configuration Switcher${NC}"
    echo ""
    echo "Usage: $0 [dev|full|status]"
    echo ""
    echo "Profiles:"
    echo -e "  ${GREEN}dev${NC}    - Lightweight config for daily development (~10k tokens)"
    echo "           Includes: filesystem, git, brave-search"
    echo ""
    echo -e "  ${GREEN}full${NC}   - Full featured config (~25k+ tokens)"
    echo "           Includes: all available MCP servers"
    echo ""
    echo -e "  ${GREEN}status${NC} - Show current configuration"
    echo ""
    echo "Example:"
    echo "  $0 dev    # Switch to development profile"
    echo "  $0 status # Check current configuration"
}

check_current() {
    if [ -L "$PROJECT_ROOT/.mcp.json" ]; then
        current=$(readlink "$PROJECT_ROOT/.mcp.json" | xargs basename | sed 's/.mcp-//' | sed 's/.json//')
        echo -e "${BLUE}Current MCP profile:${NC} ${GREEN}$current${NC}"
    elif [ -f "$PROJECT_ROOT/.mcp.json" ]; then
        echo -e "${YELLOW}Using custom .mcp.json (not a managed profile)${NC}"
    else
        echo -e "${RED}No MCP configuration found${NC}"
    fi
}

switch_config() {
    local profile=$1
    local config_file="$PROJECT_ROOT/.mcp-${profile}.json"
    
    if [ ! -f "$config_file" ]; then
        echo -e "${RED}Error: Configuration file $config_file not found${NC}"
        exit 1
    fi
    
    # Remove existing config or symlink
    if [ -e "$PROJECT_ROOT/.mcp.json" ] || [ -L "$PROJECT_ROOT/.mcp.json" ]; then
        rm -f "$PROJECT_ROOT/.mcp.json"
    fi
    
    # Create symlink to selected profile
    ln -s ".mcp-${profile}.json" "$PROJECT_ROOT/.mcp.json"
    
    echo -e "${GREEN}✓ Switched to ${profile} profile${NC}"
    echo ""
    
    # Show what's included
    echo -e "${BLUE}Enabled MCP servers:${NC}"
    grep '".*":' "$config_file" | grep -v mcpServers | sed 's/.*"\(.*\)".*/  - \1/'
    
    echo ""
    echo -e "${YELLOW}Note: Restart Claude to apply changes${NC}"
}

# Main script logic
case "${1:-}" in
    dev)
        switch_config "dev"
        ;;
    full)
        switch_config "full"
        ;;
    status)
        check_current
        ;;
    *)
        show_usage
        exit 0
        ;;
esac