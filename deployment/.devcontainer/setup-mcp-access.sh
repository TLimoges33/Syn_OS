#!/bin/bash
# 🔐 MCP Secure Access Setup for AI Tools
# Configures comprehensive but secure MCP access for GitHub Copilot and Claude

set -euo pipefail

echo "🔐 Setting up secure MCP access for AI tools..."

# Create MCP directories if they don't exist
mkdir -p ~/.config/Code/User/globalStorage/anthropic.claude-code
mkdir -p ~/.config/github-copilot
mkdir -p ./logs/mcp

# Copy enhanced MCP configuration
if [ -f ".kilocode/mcp-enhanced-secure.json" ]; then
    echo "📋 Configuring enhanced MCP access..."
    
    # Setup Claude Code MCP access
    cp .kilocode/mcp-enhanced-secure.json ~/.config/Code/User/globalStorage/anthropic.claude-code/mcp.json
    
    # Setup GitHub Copilot context
    cat > ~/.config/github-copilot/mcp-config.json << 'EOF'
{
  "mcpIntegration": {
    "enabled": true,
    "secureMode": true,
    "allowedServers": [
      "synos-consciousness",
      "synos-kernel", 
      "synos-zero-trust",
      "filesystem",
      "git",
      "rust-analyzer"
    ],
    "restrictedPaths": [
      "/workspaces/Syn_OS-Dev-Team/archive/legacy",
      "/workspaces/Syn_OS-Dev-Team/build",
      "/workspaces/Syn_OS-Dev-Team/target"
    ]
  }
}
EOF

    echo "✅ MCP configurations deployed"
else
    echo "⚠️ Enhanced MCP config not found, using defaults"
fi

# Install MCP server dependencies
echo "📦 Installing MCP server dependencies..."

# Python MCP servers
if command -v python3 >/dev/null 2>&1; then
    python3 -m pip install --user mcp anthropic openai requests fastapi uvicorn
fi

# Node.js MCP servers (install commonly used ones)
if command -v npm >/dev/null 2>&1; then
    npm install -g @upstash/context7-mcp
    npm install -g @modelcontextprotocol/server-sequential-thinking
    npm install -g @modelcontextprotocol/server-filesystem  
    npm install -g @modelcontextprotocol/server-git
fi

# Set proper permissions
chmod 755 ./mcp_servers/*.py 2>/dev/null || true
chmod 644 ~/.config/Code/User/globalStorage/anthropic.claude-code/mcp.json 2>/dev/null || true
chmod 644 ~/.config/github-copilot/mcp-config.json 2>/dev/null || true

echo "🎯 MCP Access Configuration Summary:"
echo "  ✅ Claude Code: Full secure MCP access to SynOS development"
echo "  ✅ GitHub Copilot: Contextual MCP integration"
echo "  ✅ Security: Restricted paths and secure mode enabled"
echo "  ✅ Servers: Consciousness, Kernel, Zero-Trust, Filesystem, Git"
echo ""
echo "🚀 AI tools now have comprehensive but secure access to your development environment!"
