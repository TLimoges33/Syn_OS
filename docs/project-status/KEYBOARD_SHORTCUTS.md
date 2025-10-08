# SynOS v1.0 - Keyboard Shortcuts Reference

**Three-Panel Workspace Interface Guide**

---

## 🎯 Overview

SynOS features a revolutionary three-panel workspace with toggleable UI components for maximum productivity and distraction-free focus.

```
┌─────────┬──────────────────────────┬─────────┐
│ FILE    │  MAIN WORKSPACE          │ AI      │
│ TREE    │  (Terminal/Browser/IDE)  │ CHAT    │
│ (F10)   │                          │ (F11)   │
└─────────┴──────────────────────────┴─────────┘
```

---

## ⌨️ Core Keyboard Shortcuts

### Panel Toggles

| Shortcut | Action | Description |
|----------|--------|-------------|
| **F9** | Toggle All Panels | Distraction-free mode (hide all panels) |
| **F10** | Toggle File Tree | Show/hide left sidebar (AI-enhanced file browser) |
| **F11** | Toggle AI Chat | Show/hide right sidebar (Jarvis chat interface) |
| **F12** | Toggle Terminal | Show/hide dropdown smart terminal |

### System Management

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Ctrl+Alt+Delete** | System Monitor | Launch MATE System Monitor (task manager) |
| **Ctrl+K** | Emergency Kill | Kill all non-essential processes (memory emergency) |

### Jarvis CLI Commands

All commands start with `synos-jarvis`:

| Command | Description | Example |
|---------|-------------|---------|
| `status` | Check AI services status | `synos-jarvis status` |
| `query "..."` | Ask Jarvis a question | `synos-jarvis query "What is XSS?"` |
| `switch-client NAME` | Switch MSSP client context | `synos-jarvis switch-client acme_corp` |
| `workflow save NAME` | Save current workflow | `synos-jarvis workflow save recon_phase` |
| `workflow load NAME` | Load saved workflow | `synos-jarvis workflow load recon_phase` |
| `learn` | Show learning insights | `synos-jarvis learn` |
| `help` | Show help message | `synos-jarvis help` |

---

## 🎨 Workspace Modes

### 1. Full Power Mode (All Panels Visible)

**When to use:**
- Complex engagements requiring multiple tools
- MSSP client work with context switching
- Educational labs with AI guidance

**Activate:**
- Press **F10** to show file tree
- Press **F11** to show AI chat
- Press **F12** for smart terminal

### 2. Distraction-Free Mode (All Panels Hidden)

**When to use:**
- Deep focus on single task
- Writing reports or documentation
- Analyzing complex code or data

**Activate:**
- Press **F9** to hide all panels
- Or individually hide with **F10**, **F11**, **F12**

### 3. AI Assistant Mode (Right Panel Only)

**When to use:**
- Learning new concepts
- Getting command suggestions
- Asking cybersecurity questions

**Activate:**
- Press **F11** to show AI chat
- Press **F10** and **F12** to hide others

---

## 🖥️ Terminal Shortcuts

### Smart Terminal (F12)

| Shortcut | Action |
|----------|--------|
| **F12** | Toggle terminal visibility |
| **Ctrl+Shift+T** | New terminal tab |
| **Ctrl+Shift+W** | Close terminal tab |
| **Ctrl+Shift+C** | Copy |
| **Ctrl+Shift+V** | Paste |
| **Ctrl+Shift+N** | New terminal window |

### AI-Enhanced Commands

The smart terminal includes AI suggestions:
- Start typing a command → get AI-powered autocomplete
- Typo detection → Jarvis suggests corrections
- Command chaining → AI suggests next steps

---

## 💬 AI Chat Panel Shortcuts

### In AI Chat Window

| Shortcut | Action |
|----------|--------|
| **Ctrl+Enter** | Send message |
| **Escape** | Hide chat panel |
| **Ctrl+L** | Clear chat history |
| **Ctrl+S** | Save conversation |

### Chat Commands

Type these directly in the chat:
- `/status` - Check AI services
- `/context CLIENT` - Switch client context
- `/learn` - Show learning insights
- `/help` - Show available commands

---

## 📁 File Tree Panel Shortcuts

### Navigation

| Shortcut | Action |
|----------|--------|
| **F10** | Toggle file tree panel |
| **Ctrl+F** | Search files |
| **Ctrl+H** | Show/hide hidden files |
| **Enter** | Open selected file |
| **Delete** | Move to trash |

### AI-Enhanced Features

- **Right-click** → AI-powered file analysis
- **Ctrl+I** → Get file insights (purpose, threats, etc.)
- **Ctrl+M** → Show file metadata with AI context

---

## 🚨 Emergency & System Management

### Critical Shortcuts

| Shortcut | Action | Use Case |
|----------|--------|----------|
| **Ctrl+Alt+Delete** | System Monitor | View/kill processes, check memory/CPU |
| **Ctrl+K** | Emergency Kill All | Kill all non-essential processes when system freezes |
| **Ctrl+Alt+Escape** | Force Quit Window | Click on frozen window to kill it |

### Emergency Kill (Ctrl+K) Behavior

When you press **Ctrl+K**, SynOS executes an intelligent emergency cleanup:

**Protected (Will NOT be killed):**
- Kernel processes
- System services (systemd, dbus, etc.)
- Display server (X11/Wayland)
- Window manager (MATE)
- Essential AI services (synos-ai-daemon core)

**Killed (Non-essential):**
- Browser tabs
- Heavy applications (VMs, IDEs)
- Background tools
- User applications

**After Emergency Kill:**
- System shows notification with freed memory
- Jarvis suggests next steps
- Logs created in `/var/log/synos/emergency-kill.log`

**Manual Alternative:**
```bash
# Same as Ctrl+K
synos-emergency-kill

# Kill specific process by name
synos-emergency-kill --target firefox

# Dry run (show what would be killed)
synos-emergency-kill --dry-run
```

---

## 🔧 MSSP Workflow Shortcuts

### Client Context Switching

```bash
# Switch to client context
synos-jarvis switch-client client_a

# Jarvis loads:
# - Previous vulnerability findings
# - Report progress
# - Meeting notes
# - Saved workflows
```

### Workflow Management

```bash
# Save current workspace state
synos-jarvis workflow save recon_complete

# Later, restore exactly where you left off
synos-jarvis workflow load recon_complete
```

---

## 🎓 Educational Mode Shortcuts

### Learning Commands

| Command | Purpose |
|---------|---------|
| `synos-jarvis learn` | Show personalized learning insights |
| `synos-jarvis query "explain X"` | Get detailed explanations |
| `/practice MODE` | Launch practice environment |

### Practice Environments

Available in AI chat:
- `/practice sql-injection` - SQL injection lab
- `/practice xss` - Cross-site scripting lab
- `/practice privesc` - Privilege escalation lab

---

## 🛡️ Security Tools Integration

### Quick Launch

The smart terminal includes aliases:
- `nmap-scan` - AI-suggested Nmap scan
- `burp-start` - Launch Burp Suite with context
- `metasploit` - Metasploit with AI suggestions

### AI-Enhanced Reconnaissance

```bash
# Start recon, Jarvis suggests next steps
synos-jarvis query "I'm starting recon on 192.168.1.0/24"

# Jarvis responds with:
# 1. Suggested nmap scan
# 2. Port analysis strategy
# 3. Service enumeration plan
```

---

## 🔍 Advanced Features

### Context-Aware AI

Jarvis knows:
- Your current working directory
- Open files and terminal history
- Active security tools
- Client context (MSSP mode)
- Learning progress (Education mode)

**Example:**

```bash
# You're in a directory with Nmap results
$ synos-jarvis query "analyze these scan results"

# Jarvis automatically reads nmap.txt and provides:
# - Open ports summary
# - Service version vulnerabilities
# - Next recommended actions
```

### Neural Darwinism Learning

The OS learns YOUR workflow:
- **Day 1-7:** Observation mode
- **Day 8-30:** Suggestion mode
- **Day 31+:** Automation mode

**See your progress:**
```bash
synos-jarvis learn
```

---

## 📊 Status Indicators

### AI Chat Panel Header

- **🟢 Online** - LLM engine connected
- **🔴 Offline** - LLM engine not running
- **🟡 Limited** - CPU-only mode (no GPU)

### Terminal Prompt

```bash
# Jarvis-enhanced prompt shows:
synos@hostname [client_a] [97% confidence] ~/recon $
               ^^^^^^^^   ^^^^^^^^^^^^^^^
               MSSP Client  AI Confidence
```

---

## 🚀 Power User Tips

### 1. **Combine Panels for Max Efficiency**

```
Left: File tree with target IP directories
Center: Terminal running scans
Right: AI chat suggesting next steps
```

### 2. **Use Workflows for Repeatable Tasks**

```bash
# Save your MSSP recon workflow once
synos-jarvis workflow save mssp_recon_v1

# Reuse for every engagement
synos-jarvis workflow load mssp_recon_v1
```

### 3. **Leverage AI Context**

Instead of:
```bash
nmap -sV -sC -oA output 192.168.1.1
```

Ask Jarvis:
```bash
synos-jarvis query "scan 192.168.1.1 comprehensively"
```

Jarvis provides:
- Optimized Nmap command
- Reasoning for chosen flags
- Expected results
- Next recommended actions

---

## 🎯 Quick Reference Card

**Print this for your desk:**

```
╔═══════════════════════════════════════════════════════════════╗
║           SYNOS v1.0 - KEYBOARD SHORTCUTS                     ║
╠═══════════════════════════════════════════════════════════════╣
║ F9  → Toggle All Panels (Distraction-Free)                   ║
║ F10 → Toggle File Tree (Left Panel)                          ║
║ F11 → Toggle AI Chat (Right Panel)                           ║
║ F12 → Toggle Smart Terminal (Dropdown)                       ║
╠═══════════════════════════════════════════════════════════════╣
║ SYSTEM:                                                       ║
║   Ctrl+Alt+Delete → System Monitor (Task Manager)            ║
║   Ctrl+K          → Emergency Kill All Processes             ║
║   Ctrl+Alt+Escape → Force Quit Window                        ║
╠═══════════════════════════════════════════════════════════════╣
║ JARVIS CLI:                                                   ║
║   synos-jarvis status            Check AI services           ║
║   synos-jarvis query "..."       Ask Jarvis                  ║
║   synos-jarvis switch-client X   MSSP context switch         ║
║   synos-jarvis workflow save X   Save workspace              ║
║   synos-jarvis learn             Learning insights           ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 📖 Additional Resources

- **User Guide:** `/usr/share/doc/synos/USER_GUIDE.md`
- **AI Features:** `/usr/share/doc/synos/AI_FEATURES.md`
- **MSSP Platform:** `/usr/share/doc/synos/MSSP_GUIDE.md`
- **Educational Mode:** `/usr/share/doc/synos/EDUCATION_GUIDE.md`

---

## 🆘 Help & Support

**In-OS Help:**
```bash
synos-jarvis help
man synos
```

**Community:**
- GitHub: https://github.com/synos/synos
- Discord: https://discord.gg/synos
- Docs: https://docs.synos.dev

---

**Remember:** Jarvis learns YOUR workflow. The more you use SynOS, the smarter it becomes.

**Welcome to the future of cybersecurity operating systems.** 🚀
