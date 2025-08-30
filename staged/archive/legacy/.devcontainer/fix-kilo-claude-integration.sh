#!/bin/bash
# Kilo Code + Claude API Integration Fix Script
# Resolves ENOENT spawn claude errors

set -euo pipefail

echo "🔧 Fixing Kilo Code + Claude API Integration..."

# Verify Claude CLI installation
CLAUDE_PATH="/home/diablorain/.nvm/versions/node/v22.17.0/bin/claude"
if [[ -f "$CLAUDE_PATH" ]]; then
    echo "✅ Claude CLI found at: $CLAUDE_PATH"
    echo "   Version: $(${CLAUDE_PATH} --version)"
else
    echo "❌ Claude CLI not found at expected path"
    echo "   Checking alternative locations..."
    
    # Check if claude is in PATH
    if command -v claude >/dev/null 2>&1; then
        CLAUDE_PATH=$(which claude)
        echo "✅ Claude CLI found at: $CLAUDE_PATH"
    else
        echo "❌ Claude CLI not installed. Installing..."
        npm install -g @anthropic-ai/claude-code
        CLAUDE_PATH=$(which claude)
    fi
fi

# Update shell environment
echo ""
echo "🔄 Updating shell environment..."

# Add to bashrc if not already present
if ! grep -q "# Kilo Code Claude Integration" ~/.bashrc; then
    cat >> ~/.bashrc << 'EOF'

# Kilo Code Claude Integration - PATH Fix
export CLAUDE_CLI_PATH="/home/diablorain/.nvm/versions/node/v22.17.0/bin/claude"
export PATH="/home/diablorain/.nvm/versions/node/v22.17.0/bin:$PATH"
EOF
    echo "✅ Updated ~/.bashrc with Claude CLI path"
else
    echo "✅ Shell environment already configured"
fi

# Create VS Code environment file
mkdir -p .vscode
cat > .vscode/environment.json << EOF
{
  "PATH": "/home/diablorain/.nvm/versions/node/v22.17.0/bin:/usr/local/bin:/usr/bin:/bin",
  "CLAUDE_CLI_PATH": "${CLAUDE_PATH}",
  "NODE_PATH": "/home/diablorain/.nvm/versions/node/v22.17.0/lib/node_modules"
}
EOF
echo "✅ Created VS Code environment configuration"

# Verify MCP configuration
echo ""
echo "🔍 Verifying MCP configuration..."
if [[ -f ".kilocode/mcp.json" ]]; then
    if grep -q "claude-code-engine" .kilocode/mcp.json; then
        echo "✅ MCP configuration includes Claude Code engine"
    else
        echo "⚠️  MCP configuration missing Claude Code engine"
    fi
else
    echo "❌ MCP configuration file not found"
fi

# Test Claude CLI accessibility
echo ""
echo "🧪 Testing Claude CLI accessibility..."
if "$CLAUDE_PATH" --version >/dev/null 2>&1; then
    echo "✅ Claude CLI is accessible and working"
else
    echo "❌ Claude CLI test failed"
    exit 1
fi

# Create diagnostic script
cat > .devcontainer/diagnose-claude.sh << 'EOF'
#!/bin/bash
echo "🔍 Claude CLI Diagnostic Report"
echo "================================"
echo "Environment PATH: $PATH"
echo "Claude CLI location: $(which claude 2>/dev/null || echo 'NOT FOUND')"
echo "Direct path test: $(/home/diablorain/.nvm/versions/node/v22.17.0/bin/claude --version 2>/dev/null || echo 'FAILED')"
echo "Node.js version: $(node --version 2>/dev/null || echo 'NOT FOUND')"
echo "NPM version: $(npm --version 2>/dev/null || echo 'NOT FOUND')"
echo ""
echo "Kilo Code Configuration:"
echo "- Engine: $(grep '"engine"' .vscode/settings.json || echo 'NOT CONFIGURED')"
echo "- Claude Path: $(grep 'claudeCodePath' .vscode/settings.json || echo 'NOT CONFIGURED')"
echo ""
echo "MCP Configuration:"
if [[ -f ".kilocode/mcp.json" ]]; then
    echo "- Claude engine: $(grep -A 5 'claude-code-engine' .kilocode/mcp.json | grep 'command' || echo 'NOT CONFIGURED')"
else
    echo "- MCP file: NOT FOUND"
fi
EOF
chmod +x .devcontainer/diagnose-claude.sh

echo ""
echo "✅ Integration fix completed!"
echo ""
echo "🎯 Next Steps:"
echo "1. Restart VS Code completely (Ctrl+Shift+P -> 'Developer: Reload Window')"
echo "2. Open a new terminal and run: source ~/.bashrc"
echo "3. Test with: .devcontainer/diagnose-claude.sh"
echo "4. Try using Kilo Code with Claude engine"
echo ""
echo "📋 If issues persist:"
echo "- Check VS Code Output panel for Kilo Code logs"
echo "- Verify Anthropic API key authentication"
echo "- Run diagnostic script for detailed analysis"