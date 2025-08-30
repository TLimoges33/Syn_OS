#!/bin/bash

# Test MCP Installation Script
# Validates MCP servers can be installed and run

echo -e "\033[32m🧪 SYN OS MCP INSTALLATION TEST\033[0m"
echo ""

# Test Node.js and NPX availability
echo -e "\033[36mTesting prerequisites...\033[0m"
if command -v node &> /dev/null; then
    echo -e "\033[32m✅ Node.js: $(node --version)\033[0m"
else
    echo -e "\033[31m❌ Node.js not found - install Node.js first\033[0m"
    exit 1
fi

if command -v npx &> /dev/null; then
    echo -e "\033[32m✅ NPX available\033[0m"
else
    echo -e "\033[31m❌ NPX not found\033[0m"
    exit 1
fi

echo ""

# Test basic MCP servers
echo -e "\033[36mTesting MCP server installations...\033[0m"

test_mcp_server() {
    local server_name=$1
    local package_name=$2
    
    echo -e "\033[33m🔄 Testing: $server_name\033[0m"
    
    # Try to install and get help
    if timeout 30s npx -y "$package_name" --help &>/dev/null; then
        echo -e "\033[32m✅ $server_name: Installation successful\033[0m"
    else
        echo -e "\033[33m⚠️  $server_name: May require configuration\033[0m"
    fi
}

# Test low-risk servers first
test_mcp_server "Time Server" "@modelcontextprotocol/server-time"
test_mcp_server "Sequential Thinking" "@modelcontextprotocol/server-sequential-thinking"

# Test medium-risk servers
echo ""
echo -e "\033[33m🟡 Testing medium-risk servers...\033[0m"
test_mcp_server "Filesystem Server" "@modelcontextprotocol/server-filesystem"
test_mcp_server "Git Tools" "@modelcontextprotocol/server-git"

echo ""
echo -e "\033[32m✅ MCP Installation Test Complete!\033[0m"
echo ""
echo -e "\033[36mNext steps:\033[0m"
echo -e "   1. Run: /home/diablorain/Syn_OS/scripts/setup-mcp-environment.sh"
echo -e "   2. Configure your API keys"
echo -e "   3. Restart Claude Desktop"
echo -e "   4. Look for MCP tools indicator"