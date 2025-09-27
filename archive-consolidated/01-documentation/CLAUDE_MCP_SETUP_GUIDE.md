# Claude CLI with MCP Setup - Complete Guide

## 🎉 Setup Complete!

Your Claude CLI is now configured with Model Context Protocol (MCP) capabilities similar to what I have as GitHub Copilot. Here's what's been set up and how to use it:

## ✅ Working MCP Servers

1. **GitHub** - Repository management and operations
2. **Memory** - Context and conversation memory
3. **Filesystem** - File operations in your Syn OS project
4. **Syn OS Test Server** - Your custom MCP server (configured but needs environment setup)

## 🚀 Quick Start

### 1. Start Claude with MCP

```bash
claude
```

### 2. Test Basic MCP Functionality

```
> /mcp
```

This command shows MCP server status and authentication options.

### 3. Use Slash Commands (MCP Tools)

```
> /filesystem__list_files
> /github__list_repositories
> /memory__store "Important project context"
```

### 4. Use @ Mentions (MCP Resources)

```
> @filesystem:file://README.md
> Can you analyze @filesystem:file://src/kernel/main.rs?
> Compare @filesystem:file://Cargo.toml with the project structure
```

## 🔧 Advanced Usage

### File Operations

```
> List all Rust files in the src directory
> Show me the contents of @filesystem:file://src/kernel/Cargo.toml
> /filesystem__read_file src/kernel/main.rs
```

### Git Operations (when working)

```
> /git__show_status
> /git__list_commits
> Show me recent commits with @git:commit://HEAD~5..HEAD
```

### Memory System

```
> /memory__store "SynOS is a consciousness-integrated operating system"
> /memory__recall "consciousness"
> Remember that this project focuses on quantum substrate coherence
```

### GitHub Integration

```
> /github__list_repositories
> /github__create_issue "title" "description"
> Show me issues in @github:repository://TLimoges33/SynOS_Master-Archive-Vault
```

## 🔨 Troubleshooting Failed Servers

### Fix Syn OS MCP Server

```bash
# Install missing dependencies
pip3 install mcp

# Test the server manually
python3 mcp_servers/test_simple_mcp_server.py
```

### Fix Other Servers

```bash
# Install missing MCP server packages
npm install -g @modelcontextprotocol/server-sqlite
npm install -g @modelcontextprotocol/server-postgres
npm install -g @modelcontextprotocol/server-docker
npm install -g @modelcontextprotocol/server-git
npm install -g @modelcontextprotocol/server-shell

# Set up environment variables
source scripts/claude-mcp-env.sh
```

### Set API Keys

```bash
export GITHUB_TOKEN="your_github_token"
export BRAVE_API_KEY="your_brave_api_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
```

## 🎯 Key Differences from GitHub Copilot

### What Claude CLI with MCP Can Do:

- ✅ File system operations across your entire project
- ✅ Git repository analysis and operations
- ✅ Database queries (when configured)
- ✅ External API integrations
- ✅ Memory and context management
- ✅ Custom tool integration (like your Syn OS server)
- ✅ Shell command execution (when configured)
- ✅ Web search and research
- ✅ Real-time data access

### GitHub Copilot Integration:

- 🤝 Both can work together
- 🤝 Claude CLI handles broader context and tools
- 🤝 GitHub Copilot handles in-editor code completion
- 🤝 Different but complementary capabilities

## 📚 Next Steps

1. **Test the working servers**:

   ```bash
   claude
   > /filesystem__list_files
   > @filesystem:file://README.md
   ```

2. **Set up authentication for additional services**:

   ```bash
   claude mcp auth github
   ```

3. **Configure your API keys**:

   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   export GITHUB_TOKEN="your_token"
   export ANTHROPIC_API_KEY="your_key"
   ```

4. **Explore available tools**:

   ```
   > /
   # Shows all available slash commands including MCP tools
   ```

5. **Use @ mentions for file references**:
   ```
   > @
   # Shows available resources from MCP servers
   ```

## 🛠 Configuration Files

- **User config**: `~/.claude.json` (global MCP servers)
- **Project config**: `.mcp.json` (team-shared servers)
- **Environment**: `scripts/claude-mcp-env.sh`

## 🔄 Managing MCP Servers

```bash
# List all servers
claude mcp list

# Add a new server
claude mcp add server-name --scope user -- command args

# Remove a server
claude mcp remove server-name

# Get server details
claude mcp get server-name
```

## 🎉 You're Ready!

Your Claude CLI now has extensive tooling capabilities similar to what I have as GitHub Copilot. The main difference is that you have direct access to the same MCP servers and can extend them with custom tools like your Syn OS consciousness integration!

Start with:

```bash
claude
> Hello! Can you list the files in my Syn OS project using @filesystem:file://?
```
