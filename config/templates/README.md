# 📝 Configuration Templates

## 📁 Environment & Configuration Templates

This directory contains template files for setting up SynOS environments and configurations.

### **Environment Templates**

- **`.env.example`** - Complete environment configuration template
  - Database connections (PostgreSQL, Redis)
  - NATS message bus configuration
  - Service orchestration settings
  - Security and monitoring configurations
- **`.env.tokens.example`** - GitHub token configuration template
  - Personal access token setup
  - CLI authentication examples
  - API access configuration

## 🚀 Usage

### **Setting up Environment**

```bash
# Copy template and customize
cp config/templates/.env.example .env
cp config/templates/.env.tokens.example .env.tokens

# Edit with your specific values
nano .env
nano .env.tokens
```

### **Security Notes**

- **Never commit `.env` or `.env.tokens` files**
- **Use strong, unique passwords**
- **Rotate tokens regularly**
- **Follow principle of least privilege**

## 🔗 Related

- [`../core/syn_os_config.yaml`](../core/syn_os_config.yaml) - Main system configuration
- [`../environments/`](../environments/) - Environment validation scripts
