# MCP Tool Optimization Guide

## Quick Start

Switch between MCP configurations:
```bash
# Use lightweight development config (~10k tokens)
./scripts/switch-mcp.sh dev

# Use full-featured config (~25k+ tokens)
./scripts/switch-mcp.sh full

# Check current configuration
./scripts/switch-mcp.sh status
```

## Configuration Profiles

### Development Profile (`.mcp-dev.json`)
**Token Usage: ~10,000 tokens**

Perfect for daily development work:
- **filesystem**: File operations
- **git**: Version control
- **brave-search**: Web search

### Full Profile (`.mcp-full.json`)
**Token Usage: ~25,000+ tokens**

All available tools for complex tasks:
- All development profile tools
- **github**: PR creation, issue management (26 tools)
- **memory**: Knowledge graph operations
- **sqlite/postgres**: Database operations
- **docker**: Container management

## Recommendations

### For Daily Development
Use the `dev` profile to:
- Reduce context token usage by 60%
- Speed up Claude's response time
- Focus on core development tasks

### When to Use Full Profile
Switch to `full` when you need:
- GitHub operations (creating PRs, managing issues)
- Database work
- Docker container management
- Knowledge graph features

### Custom Configurations
Create your own profile by copying `.mcp-dev.json` to `.mcp-custom.json` and modifying as needed.

## Token Usage Breakdown

| Server | Tools | Tokens | Use Case |
|--------|-------|--------|----------|
| github | 26 | ~13,365 | GitHub operations |
| filesystem | 14 | ~6,659 | File operations |
| memory | 9 | ~3,968 | Knowledge graph |
| sequential-thinking | 1 | ~1,272 | Complex reasoning |
| brave-search | 2 | ~1,048 | Web search |
| git | 5 | ~800 | Version control |
| Others | - | ~500 each | Various |

## Environment Variables

Ensure these are set in your shell:
```bash
export GITHUB_TOKEN="your-github-token"
export BRAVE_API_KEY="your-brave-api-key"
export POSTGRES_CONNECTION_STRING="postgresql://localhost:5432/synos"
```

## Troubleshooting

If Claude shows high context usage:
1. Check current profile: `./scripts/switch-mcp.sh status`
2. Switch to dev profile: `./scripts/switch-mcp.sh dev`
3. Restart Claude to apply changes

## Notes

- Configuration changes require Claude restart
- The script creates symlinks for easy switching
- Original configs are preserved as `.mcp-dev.json` and `.mcp-full.json`