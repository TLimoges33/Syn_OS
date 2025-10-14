# 🚀 First Steps with SynOS

**Difficulty**: Beginner  
**Time**: 30 minutes  
**Prerequisites**: SynOS installed and running

Welcome to SynOS! This tutorial-style guide will walk you through your first experiences with the system, teaching you essential commands and helping you understand what makes SynOS unique.

---

## 📋 Table of Contents

1. [Verifying Your Installation](#verifying-your-installation)
2. [Understanding the Interface](#understanding-the-interface)
3. [Your First Commands](#your-first-commands)
4. [Exploring the AI Consciousness](#exploring-the-ai-consciousness)
5. [Running Security Tools](#running-security-tools)
6. [Understanding System Output](#understanding-system-output)
7. [Managing Services](#managing-services)
8. [Where to Go Next](#where-to-go-next)

---

## 1. Verifying Your Installation

Let's make sure everything is working correctly.

### Check System Status

```bash
# Display SynOS system information
synos info

# Expected output:
# SynOS v0.1.0
# Kernel: Custom Rust kernel (x86_64)
# AI Engine: Active (Neural Darwinism)
# Security Framework: Active
# Services: 12/12 running
```

If you see this output, congratulations! Your installation is working.

### Verify AI Consciousness

```bash
# Check AI consciousness status
synos consciousness status

# Expected output:
# AI Consciousness Engine: ACTIVE
# Neural Networks: 3/3 loaded
# Processing Units: TensorFlow Lite, ONNX Runtime
# State: Learning
# Uptime: [your uptime]
```

### Check Security Services

```bash
# Verify security framework
synos security status

# Expected output:
# Security Framework: ACTIVE
# Threat Detection: Enabled
# Access Control: MAC + RBAC
# Audit System: Logging
# Tools Installed: 500+
```

---

## 2. Understanding the Interface

SynOS provides multiple interfaces for interaction.

### Command-Line Interface (CLI)

The primary interface is the command line. You'll use:

-   **`synos`** - Main system control command
-   **`synos-security`** - Security tools and operations
-   **`synos-ai`** - AI consciousness management
-   **`synos-network`** - Network operations

### System Hierarchy

```
/
├── synos/              # SynOS core system files
│   ├── consciousness/  # AI consciousness engine
│   ├── security/       # Security framework
│   ├── kernel/         # Custom kernel modules
│   └── config/         # Configuration files
├── var/synos/          # Runtime data
│   ├── logs/           # System logs
│   ├── models/         # AI models
│   └── state/          # Consciousness state
└── home/[user]/        # User home directory
```

### Configuration Files

Key configuration files you should know:

```bash
# View main configuration
cat /etc/synos/config.toml

# View AI consciousness config
cat /etc/synos/consciousness/engine.toml

# View security framework config
cat /etc/synos/security/framework.toml
```

---

## 3. Your First Commands

Let's try some essential commands.

### System Information

```bash
# Get detailed system information
synos info --verbose

# Check kernel version
uname -r

# View loaded kernel modules
lsmod | grep synos

# Check system resources
synos resources
```

### Service Management

```bash
# List all SynOS services
synos services list

# Check status of a specific service
synos services status consciousness

# View service logs
synos services logs consciousness
```

### Help System

```bash
# Get help on any command
synos --help
synos consciousness --help
synos security --help

# Get command-specific help
synos consciousness start --help
```

---

## 4. Exploring the AI Consciousness

The AI Consciousness Engine is what makes SynOS unique. Let's interact with it.

### Starting the AI

If not already running:

```bash
# Start AI consciousness
synos consciousness start

# Watch the initialization process
synos consciousness logs --follow
```

### Basic AI Interactions

```bash
# Query the AI about system state
synos ai query "What is my current system load?"

# Ask the AI to analyze threats
synos ai query "Are there any security threats?"

# Get AI recommendations
synos ai query "What should I optimize?"
```

### Understanding AI State

```bash
# View current consciousness state
synos consciousness state

# Expected output:
# State: Active Learning
# Neural Activity: 72%
# Decision Quality: High
# Learning Rate: 0.001
# Episodes: 1,234
# Last Update: 2 minutes ago
```

### AI Learning

The AI learns from your usage patterns:

```bash
# View what the AI has learned
synos consciousness insights

# Export learning data
synos consciousness export --format json > ai-state.json

# View neural network architecture
synos consciousness architecture
```

---

## 5. Running Security Tools

SynOS includes 500+ security tools. Let's try some.

### Reconnaissance Tools

```bash
# Scan local network
synos security scan --network local

# Port scanning
synos security nmap 192.168.1.0/24

# Service enumeration
synos security enumerate --target 192.168.1.100
```

### Vulnerability Analysis

```bash
# Run vulnerability scan
synos security vuln-scan --target localhost

# Check for CVEs in installed packages
synos security cve-check

# Analyze system hardening
synos security audit
```

### Penetration Testing

```bash
# List available exploits
synos security exploits list

# Search for specific exploits
synos security exploits search --cve CVE-2024-1234

# Run Metasploit framework
synos security metasploit
```

### Security Monitoring

```bash
# Start threat detection
synos security threat-detect --start

# View detected threats
synos security threats list

# Analyze suspicious activity
synos security analyze --logs /var/log/auth.log
```

---

## 6. Understanding System Output

Let's decode what SynOS is telling you.

### Log Levels

SynOS uses standard log levels:

-   **DEBUG**: Detailed information for debugging
-   **INFO**: General informational messages
-   **WARN**: Warning messages (not critical)
-   **ERROR**: Error messages (needs attention)
-   **CRITICAL**: Critical issues (immediate action)

### Reading Logs

```bash
# View system logs
journalctl -u synos-core

# View AI consciousness logs
synos consciousness logs

# View security logs
synos security logs --level warn

# Search logs
synos logs search "authentication failure"
```

### Status Indicators

When you run `synos info`, you'll see status indicators:

-   **🟢 GREEN**: Everything working perfectly
-   **🟡 YELLOW**: Minor issues, system functional
-   **🔴 RED**: Critical issues, needs attention
-   **⚪ GRAY**: Service stopped or unknown state

### Performance Metrics

```bash
# View performance dashboard
synos metrics

# Monitor in real-time
synos metrics --watch

# Export metrics
synos metrics export --format prometheus
```

---

## 7. Managing Services

Learn to control SynOS services.

### Core Services

SynOS has several core services:

-   **synos-core**: Main system service
-   **synos-consciousness**: AI consciousness engine
-   **synos-security**: Security framework
-   **synos-network**: Network management
-   **synos-monitor**: System monitoring

### Service Commands

```bash
# Start a service
synos services start [service-name]

# Stop a service
synos services stop [service-name]

# Restart a service
synos services restart [service-name]

# Enable at boot
synos services enable [service-name]

# Check all services
synos services status --all
```

### Service Dependencies

Some services depend on others:

```bash
# View service dependencies
synos services deps consciousness

# Expected output:
# synos-consciousness depends on:
#   - synos-core (running)
#   - tensorflow-lite (running)
#   - onnxruntime (running)
```

### Troubleshooting Services

If a service won't start:

```bash
# Check service logs
synos services logs [service-name] --tail 100

# Validate configuration
synos services validate [service-name]

# Run diagnostics
synos diagnostics run --service [service-name]
```

---

## 8. Where to Go Next

Congratulations! You've completed your first steps with SynOS.

### Next Tutorials

Ready to dive deeper? Try these:

1. **[Tutorial: Your First Syscall](Tutorial-First-Syscall.md)** (Coming Soon)

    - Write and compile a simple system call
    - Understand kernel-userspace communication

2. **[Tutorial: Custom AI Model](Tutorial-Custom-AI-Model.md)** (Coming Soon)

    - Train a custom neural network
    - Deploy it to the consciousness engine

3. **[Tutorial: Security Automation](Tutorial-Security-Automation.md)** (Coming Soon)
    - Automate penetration testing
    - Build custom security workflows

### Deep Dives

Want to understand the internals?

-   **[Architecture Overview](Architecture-Overview.md)** - How SynOS works
-   **[AI Consciousness Engine](AI-Consciousness-Engine.md)** (Coming Soon) - Neural Darwinism explained
-   **[Security Framework](Security-Framework.md)** (Coming Soon) - Security architecture
-   **[Custom Kernel](Custom-Kernel.md)** (Coming Soon) - Kernel internals

### Developer Guides

Ready to contribute or customize?

-   **[Development Guide](Development-Guide.md)** (Coming Soon) - Set up dev environment
-   **[Contributing](Contributing.md)** - How to contribute
-   **[API Reference](API-Reference.md)** (Coming Soon) - System call reference

### Community Resources

-   **GitHub Issues**: Report bugs or request features
-   **GitHub Discussions**: Ask questions, share ideas
-   **DeepWiki**: AI-powered documentation Q&A at https://deepwiki.com/TLimoges33/Syn_OS

---

## 🎯 Quick Exercises

Test your knowledge with these exercises:

### Exercise 1: System Health Check

**Goal**: Verify all services are running correctly

```bash
# Your commands here:
synos info
synos services status --all
synos consciousness state
synos security status
```

**Expected**: All services should show 🟢 GREEN

### Exercise 2: AI Query

**Goal**: Ask the AI three questions about your system

```bash
# Your commands here:
synos ai query "What is my CPU usage?"
synos ai query "Are there any failed login attempts?"
synos ai query "What services are using the most memory?"
```

**Expected**: The AI provides relevant answers

### Exercise 3: Security Scan

**Goal**: Scan your local network for devices

```bash
# Your commands here:
synos security scan --network local
synos security nmap 192.168.1.0/24 --quick
```

**Expected**: List of discovered devices

### Exercise 4: Log Analysis

**Goal**: Find and analyze system warnings

```bash
# Your commands here:
synos logs search --level warn --last 24h
synos security analyze --logs /var/synos/logs/security.log
```

**Expected**: List of warnings with analysis

---

## 🐛 Common Issues

### Issue: AI Won't Start

**Symptoms**: `synos consciousness start` fails

**Solutions**:

```bash
# Check dependencies
synos consciousness deps

# Verify models are installed
ls /var/synos/models/

# Reinstall AI models
synos consciousness install-models

# Check logs
synos consciousness logs --tail 50
```

### Issue: Security Tools Missing

**Symptoms**: `synos security` commands fail

**Solutions**:

```bash
# Install security tools
synos security install-tools

# Verify installation
synos security tools list

# Update tool database
synos security update
```

### Issue: High CPU Usage

**Symptoms**: System running slow

**Solutions**:

```bash
# Check what's using CPU
synos resources --top

# Reduce AI learning rate
synos consciousness config set learning_rate 0.0001

# Disable background services
synos services stop synos-monitor
```

### Issue: Can't Connect to Network

**Symptoms**: Network commands fail

**Solutions**:

```bash
# Check network status
synos network status

# Restart network service
synos services restart synos-network

# Verify configuration
cat /etc/synos/network/config.toml

# Run diagnostics
synos diagnostics network
```

---

## 📖 Quick Reference

### Essential Commands

| Command                      | Description           |
| ---------------------------- | --------------------- |
| `synos info`                 | System information    |
| `synos services list`        | List all services     |
| `synos consciousness status` | Check AI status       |
| `synos security status`      | Check security status |
| `synos logs`                 | View system logs      |
| `synos metrics`              | Performance metrics   |
| `synos diagnostics`          | Run diagnostics       |
| `synos help`                 | Get help              |

### Important Paths

| Path                 | Description         |
| -------------------- | ------------------- |
| `/etc/synos/`        | Configuration files |
| `/var/synos/logs/`   | System logs         |
| `/var/synos/models/` | AI models           |
| `/var/synos/state/`  | System state        |
| `/synos/`            | Core system files   |

### Key Configuration Files

| File                                   | Purpose                |
| -------------------------------------- | ---------------------- |
| `/etc/synos/config.toml`               | Main configuration     |
| `/etc/synos/consciousness/engine.toml` | AI configuration       |
| `/etc/synos/security/framework.toml`   | Security configuration |
| `/etc/synos/network/config.toml`       | Network configuration  |

---

## 🎉 Congratulations!

You've completed your first steps with SynOS! You now know how to:

✅ Verify your installation  
✅ Navigate the system  
✅ Run essential commands  
✅ Interact with the AI consciousness  
✅ Use security tools  
✅ Understand system output  
✅ Manage services

**Next Steps**: Choose a tutorial or deep dive from the [Where to Go Next](#where-to-go-next) section.

---

**Last Updated**: October 4, 2025  
**Difficulty**: Beginner  
**Estimated Time**: 30 minutes  
**Prerequisites**: SynOS installed and running

**Need Help?**

-   GitHub Issues: https://github.com/TLimoges33/Syn_OS/issues
-   GitHub Discussions: https://github.com/TLimoges33/Syn_OS/discussions
-   DeepWiki: https://deepwiki.com/TLimoges33/Syn_OS
