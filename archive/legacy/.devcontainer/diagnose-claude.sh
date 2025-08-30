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
