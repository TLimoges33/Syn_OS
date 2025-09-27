# 🐚 Shell Scripts & Automation

## 📁 Shell Infrastructure for SynOS

This directory contains shell scripts, security wrappers, and automation tools for SynOS development and operations.

### **Security & Environment**

- **`environment-secure.sh`** - Secure environment configuration and project root detection
- **`secure-sudo.sh`** - Enterprise security wrapper for sudo operations with audit logging
- **`rbac.sh`** - Role-Based Access Control system for development operations
- **`error-handling.sh`** - Comprehensive error handling framework with security monitoring

### **Logging & Monitoring**

- **`logging.sh`** - Structured security logging framework with JSON output support

### **Development Aliases**

- **`synos-aliases`** - SynOS development aliases and shortcuts
  - Quick navigation commands
  - Git save system integration
  - Development workflow shortcuts
  - Docker management aliases

## 🔧 Usage

### **Source Aliases**

```bash
source config/shell/synos-aliases
```

### **Security Functions**

```bash
source config/shell/environment-secure.sh
source config/shell/secure-sudo.sh
```

### **Error Handling**

```bash
source config/shell/error-handling.sh
# Automatically sets up error trapping
```

## 🛡️ Security Features

- **Audit Logging**: All operations logged with timestamps and user context
- **Path Validation**: Prevents dangerous operations on critical system paths
- **Role-Based Access**: User permissions validated before operations
- **Error Monitoring**: Comprehensive error tracking with security alerts
