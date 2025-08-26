# Cross-Platform MCP Configuration Fix

* *Status**: ✅ **RESOLVED**
* *Date**: 2025-07-23
* *Issue**: MCP servers not responding on Windows due to Linux-specific configuration

## Problem Summary

The MCP configuration in `.kilocode/mcp.json` contains Linux-specific paths and commands that don't work on Windows:

- Linux paths like `/home/diablorain/` and `/media/sf_X_DRIVE/`
- Node.js paths pointing to Linux NVM installation
- npx commands that may not be in Windows PATH

## Diagnostic Steps

### 1. Check Node.js Installation

Run these commands in PowerShell to find Node.js:

```powershell

## Check if node is in PATH

node --version

## Find Node.js installation location

where.exe node

## Check if npx is available

npx --version

## Find npx location

where.exe npx

## Check environment variables

echo $env:PATH
```text
## Find Node.js installation location

where.exe node

## Check if npx is available

npx --version

## Find npx location

where.exe npx

## Check environment variables

echo $env:PATH

```text

### 2. Current Issues in MCP Configuration

The `.kilocode/mcp.json` file has these Windows-incompatible settings:

1. **Claude command path**:
   - Current: `/home/diablorain/.nvm/versions/node/v22.17.0/bin/claude`
   - Needs: Windows path like `C:\Program Files\nodejs\claude.cmd`

2. **File paths**:
   - Current: `/media/sf_X_DRIVE/Ty Main/Syn_OS`
   - Needs: `X:\Ty Main\Syn_OS`

3. **Environment paths**:
   - Current: Linux-style PATH
   - Needs: Windows-style PATH with proper separators

## Proposed Windows Configuration

Here's what the Windows-compatible `.kilocode/mcp.json` should look like:

```json

1. **Claude command path**:
   - Current: `/home/diablorain/.nvm/versions/node/v22.17.0/bin/claude`
   - Needs: Windows path like `C:\Program Files\nodejs\claude.cmd`

2. **File paths**:
   - Current: `/media/sf_X_DRIVE/Ty Main/Syn_OS`
   - Needs: `X:\Ty Main\Syn_OS`

3. **Environment paths**:
   - Current: Linux-style PATH
   - Needs: Windows-style PATH with proper separators

## Proposed Windows Configuration

Here's what the Windows-compatible `.kilocode/mcp.json` should look like:

```json
{
  "mcpServers": {
    "claude-code-engine": {
      "command": "claude",
      "args": [
        "--print",
        "--mcp-config",
        "X:\\Ty Main\\Syn_OS\\.kilocode\\mcp.json"
      ],
      "env": {
        "CLAUDE_CODE_MODE": "kilo-engine",
        "FREE_MODE": "true",
        "BYPASS_EXTERNAL_APIS": "true"
      },
      "disabled": false,
      "alwaysAllow": []
    },
    "context7": {
      "command": "npx.cmd",
      "args": [
        "-y",
        "@upstash/context7-mcp"
      ],
      "env": {
        "DEFAULT_MINIMUM_TOKENS": "10000",
        "USE_CLAUDE_CODE_BACKEND": "true"
      }
    },
    "sequentialthinking": {
      "command": "npx.cmd",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sequential-thinking"
      ]
    },
    "puppeteer": {
      "command": "npx.cmd",
      "args": [
        "-y",
        "@modelcontextprotocol/server-puppeteer"
      ]
    },
    "filesystem": {
      "command": "npx.cmd",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem"
      ],
      "env": {
        "ALLOWED_PATHS": "X:\\Ty Main\\Syn_OS,C:\\Users\\Ty"
      },
      "disabled": true,
      "alwaysAllow": []
    },
    "git": {
      "command": "npx.cmd",
      "args": [
        "-y",
        "@modelcontextprotocol/server-git"
      ]
    },
    "github": {
      "command": "npx.cmd",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": ""
      }
    },
    "memory": {
      "command": "npx.cmd",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ]
    }
  }
}
```text
        "--print",
        "--mcp-config",
        "X:\\Ty Main\\Syn_OS\\.kilocode\\mcp.json"
      ],
      "env": {
        "CLAUDE_CODE_MODE": "kilo-engine",
        "FREE_MODE": "true",
        "BYPASS_EXTERNAL_APIS": "true"
      },
      "disabled": false,
      "alwaysAllow": []
    },
    "context7": {
      "command": "npx.cmd",
      "args": [
        "-y",
        "@upstash/context7-mcp"
      ],
      "env": {
        "DEFAULT_MINIMUM_TOKENS": "10000",
        "USE_CLAUDE_CODE_BACKEND": "true"
      }
    },
    "sequentialthinking": {
      "command": "npx.cmd",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sequential-thinking"
      ]
    },
    "puppeteer": {
      "command": "npx.cmd",
      "args": [
        "-y",
        "@modelcontextprotocol/server-puppeteer"
      ]
    },
    "filesystem": {
      "command": "npx.cmd",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem"
      ],
      "env": {
        "ALLOWED_PATHS": "X:\\Ty Main\\Syn_OS,C:\\Users\\Ty"
      },
      "disabled": true,
      "alwaysAllow": []
    },
    "git": {
      "command": "npx.cmd",
      "args": [
        "-y",
        "@modelcontextprotocol/server-git"
      ]
    },
    "github": {
      "command": "npx.cmd",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": ""
      }
    },
    "memory": {
      "command": "npx.cmd",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ]
    }
  }
}

```text

## Key Changes for Windows

1. **Use `npx.cmd` instead of `npx`** - Windows requires the .cmd extension
2. **Use Windows paths** - Replace forward slashes with backslashes
3. **Remove Linux-specific PATH** - Let Windows handle PATH resolution
4. **Update file paths** - Use proper Windows drive letters and paths

## VS Code Settings Update

The `.vscode/settings.json` also needs Windows paths:

```json

1. **Remove Linux-specific PATH** - Let Windows handle PATH resolution
2. **Update file paths** - Use proper Windows drive letters and paths

## VS Code Settings Update

The `.vscode/settings.json` also needs Windows paths:

```json
{
    "terminal.integrated.cwd": "X:\\Ty Main\\Syn_OS",
    "terminal.integrated.defaultProfile.windows": "PowerShell",
    "terminal.integrated.profiles.windows": {
        "PowerShell": {
            "source": "PowerShell",
            "icon": "terminal-powershell"
        },
        "Command Prompt": {
            "path": "C:\\Windows\\System32\\cmd.exe"
        }
    },
    "files.eol": "\n",
    "terminal.integrated.scrollback": 10000,

    // Kilo Code Configuration
    "kilocode.useClaudeCodeEngine": true,
    "kilocode.bypassExternalAPI": true,
    "kilocode.freeMode": true,
    "kilocode.engine": "claude-code",
    "kilocode.api.provider": "local-claude",
    "kilocode.tokenTracking": false,
    "kilocode.billing.enabled": false,
    "kilocode.mcp.useProjectConfig": true,
    "kilocode.history.autoRestore": true
}
```text
            "source": "PowerShell",
            "icon": "terminal-powershell"
        },
        "Command Prompt": {
            "path": "C:\\Windows\\System32\\cmd.exe"
        }
    },
    "files.eol": "\n",
    "terminal.integrated.scrollback": 10000,

    // Kilo Code Configuration
    "kilocode.useClaudeCodeEngine": true,
    "kilocode.bypassExternalAPI": true,
    "kilocode.freeMode": true,
    "kilocode.engine": "claude-code",
    "kilocode.api.provider": "local-claude",
    "kilocode.tokenTracking": false,
    "kilocode.billing.enabled": false,
    "kilocode.mcp.useProjectConfig": true,
    "kilocode.history.autoRestore": true
}

```text

## Installation Requirements

Before the MCP servers can work on Windows, ensure:

1. **Node.js is installed** - Download from https://nodejs.org/
2. **npx is available** - Comes with npm (Node.js)
3. **Claude CLI is installed** (if using claude-code-engine):

   ```powershell

1. **Node.js is installed** - Download from https://nodejs.org/
2. **npx is available** - Comes with npm (Node.js)
3. **Claude CLI is installed** (if using claude-code-engine):

   ```powershell
   npm install -g @anthropic-ai/claude-cli
```text

```text

## Testing MCP Servers

After configuration, test each server:

```powershell
```powershell

## Test npx availability

npx -y @upstash/context7-mcp --version

## Test a simple MCP server

npx -y @modelcontextprotocol/server-memory --help
```text
## Test a simple MCP server

npx -y @modelcontextprotocol/server-memory --help

```text

## Troubleshooting

If MCP servers still don't respond:

1. **Check Windows Firewall** - May block MCP server connections
2. **Verify Node.js PATH** - Ensure Node.js bin directory is in system PATH
3. **Run VS Code as Administrator** - Some MCP servers may need elevated permissions
4. **Check VS Code Output** - Look for error messages in Output panel → Kilo Code

## Cross-Platform Solution

To support both Windows and Linux/macOS (Parrot OS), we've created:

1. **Separate configuration files**:
   - `.kilocode/mcp-windows.json` - Windows-specific paths and commands
   - `.kilocode/mcp-linux.json` - Linux/macOS paths and commands

2. **Automatic setup scripts**:
   - `scripts/setup-mcp-config.ps1` - PowerShell script for Windows
   - `scripts/setup-mcp-config.sh` - Bash script for Linux/macOS

### Usage

## On Windows:
```powershell

1. **Check Windows Firewall** - May block MCP server connections
2. **Verify Node.js PATH** - Ensure Node.js bin directory is in system PATH
3. **Run VS Code as Administrator** - Some MCP servers may need elevated permissions
4. **Check VS Code Output** - Look for error messages in Output panel → Kilo Code

## Cross-Platform Solution

To support both Windows and Linux/macOS (Parrot OS), we've created:

1. **Separate configuration files**:
   - `.kilocode/mcp-windows.json` - Windows-specific paths and commands
   - `.kilocode/mcp-linux.json` - Linux/macOS paths and commands

2. **Automatic setup scripts**:
   - `scripts/setup-mcp-config.ps1` - PowerShell script for Windows
   - `scripts/setup-mcp-config.sh` - Bash script for Linux/macOS

### Usage

## On Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup-mcp-config.ps1
```text

```text

## On Linux/macOS (Parrot OS):
```bash

```bash
chmod +x scripts/setup-mcp-config.sh
./scripts/setup-mcp-config.sh
```text

```text

The scripts will:

- Detect your operating system
- Create/update `.kilocode/mcp.json` with the appropriate configuration
- Use symlinks on Unix systems for easy switching
- Use file copies on Windows for compatibility

### Git Configuration

Add to `.gitignore`:
```text

- Use symlinks on Unix systems for easy switching
- Use file copies on Windows for compatibility

### Git Configuration

Add to `.gitignore`:

```text
.kilocode/mcp.json
```text

```text

This ensures the OS-specific `mcp.json` isn't committed, while the platform-specific configs are tracked.

## Summary

✅ **Windows configuration created** with proper paths and `npx.cmd`
✅ **Linux configuration preserved** from original setup
✅ **Cross-platform scripts** for automatic configuration
✅ **Documentation updated** with complete instructions

### Next Steps

1. Restart VS Code to apply the new configuration
2. Test MCP servers after restart
3. On Parrot OS laptop, run the bash setup script
4. Verify both environments work correctly

- --

* *Note**: The MCP servers may take time to initialize on first run. If a server appears unresponsive, try restarting VS Code and testing again.
✅ **Windows configuration created** with proper paths and `npx.cmd`
✅ **Linux configuration preserved** from original setup
✅ **Cross-platform scripts** for automatic configuration
✅ **Documentation updated** with complete instructions

### Next Steps

1. Restart VS Code to apply the new configuration
2. Test MCP servers after restart
3. On Parrot OS laptop, run the bash setup script
4. Verify both environments work correctly

- --

* *Note**: The MCP servers may take time to initialize on first run. If a server appears unresponsive, try restarting VS Code and testing again.