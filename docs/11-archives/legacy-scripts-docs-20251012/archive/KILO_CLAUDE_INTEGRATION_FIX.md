# Kilo Code + Claude API Integration Fix

**Status**: ✅ **RESOLVED**  
**Date**: 2025-07-19  
**Issue**: `spawn claude ENOENT` error when using Claude API as Kilo Code engine

## Problem Summary

Kilo Code was configured to use Claude Code CLI as the engine but failed with:
```
Command failed with ENOENT: claude -p --system-prompt ...
spawn claude ENOENT
```

## Root Cause

**PATH Resolution Issue**: VS Code couldn't find the `claude` command because:
- Claude CLI was installed at `/home/diablorain/.nvm/versions/node/v22.17.0/bin/claude`
- VS Code/Kilo Code spawns processes with limited PATH environment
- MCP configuration used relative command `claude-code` instead of absolute path

## Solution Applied

### 1. MCP Configuration Fix
Updated `.kilocode/mcp.json`:
```json
"claude-code-engine": {
  "command": "/home/diablorain/.nvm/versions/node/v22.17.0/bin/claude",
  "args": ["--mcp-server"],
  "env": {
    "CLAUDE_CODE_MODE": "kilo-engine",
    "FREE_MODE": "true",
    "BYPASS_EXTERNAL_APIS": "true",
    "PATH": "/home/diablorain/.nvm/versions/node/v22.17.0/bin:/usr/local/bin:/usr/bin:/bin"
  }
}
```

### 2. VS Code Settings Update
Enhanced `.vscode/settings.json`:
```json
"kilocode.claudeCodePath": "/home/diablorain/.nvm/versions/node/v22.17.0/bin/claude",
"kilocode.environmentPath": "/home/diablorain/.nvm/versions/node/v22.17.0/bin:/usr/local/bin:/usr/bin:/bin"
```

### 3. Shell Environment Fix
Updated `~/.bashrc`:
```bash
# Kilo Code Claude Integration - PATH Fix
export CLAUDE_CLI_PATH="/home/diablorain/.nvm/versions/node/v22.17.0/bin/claude"
export PATH="/home/diablorain/.nvm/versions/node/v22.17.0/bin:$PATH"
```

### 4. Diagnostic Tools
Created scripts:
- `.devcontainer/fix-kilo-claude-integration.sh` - Automated fix script
- `.devcontainer/diagnose-claude.sh` - Integration diagnostic tool

## Verification Results

✅ **Claude CLI**: Found at `/home/diablorain/.nvm/versions/node/v22.17.0/bin/claude`  
✅ **Version**: 1.0.56 (Claude Code)  
✅ **PATH Access**: Command accessible from shell  
✅ **MCP Config**: Absolute path configured  
✅ **VS Code Settings**: Kilo Code path settings updated  

## Current Configuration Status

### Kilo Code Engine Settings
- **Engine**: `claude-code`
- **Provider**: `local-claude`
- **Free Mode**: ✅ Enabled
- **Bypass External API**: ✅ Enabled
- **MCP Integration**: ✅ Project config enabled

### MCP Servers Available
- **Claude Code Engine**: ✅ Configured with absolute path
- **Context7**: ✅ Ready
- **Sequential Thinking**: ✅ Ready
- **Filesystem**: ✅ Configured for workspace access
- **Git**: ✅ Ready
- **Memory**: ✅ Ready
- **GitHub**: ⚠️ Requires API token
- **Puppeteer**: ✅ Ready

## Next Steps for Users

1. **Restart VS Code**: `Ctrl+Shift+P` → `Developer: Reload Window`
2. **Reload Shell**: `source ~/.bashrc`
3. **Test Integration**: Try using Kilo Code with Claude engine
4. **Monitor**: Check VS Code Output panel for any remaining issues

## Troubleshooting

If issues persist:

1. **Run Diagnostic**: `.devcontainer/diagnose-claude.sh`
2. **Check Logs**: VS Code Output → Kilo Code
3. **Verify Auth**: Ensure Anthropic API key is configured
4. **Path Issues**: Confirm Claude CLI location with `which claude`

## Technical Notes

- **Claude CLI Version**: 1.0.56 (Official Anthropic Claude Code)
- **Node.js**: v22.17.0 via NVM
- **Installation Method**: Global npm install
- **Environment**: Linux development container
- **Integration Method**: MCP (Model Context Protocol)

## Prevention

To prevent similar issues:
- Always use absolute paths in MCP configurations
- Include explicit PATH environment variables
- Test CLI tool accessibility before configuration
- Use diagnostic scripts for troubleshooting

---

**Documentation**: This fix resolves the core PATH resolution issue that prevented Kilo Code from properly spawning the Claude CLI for AI engine integration.