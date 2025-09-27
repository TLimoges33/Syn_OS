# 🌍 Environment Validation

## 📁 Environment Validation Tools

This directory contains environment validation and setup verification tools.

### **Validation Scripts**

- **`validate_environment.py`** - Python environment validation script for dependencies and system requirements

## 🔗 Integration

Environment validation integrates with:

- [`../core/dev-environment.yaml`](../core/dev-environment.yaml) - Development environment specifications
- [`../dependencies/`](../dependencies/) - Component requirements validation
- `/scripts/validate-environment.sh` - Main validation orchestrator

## 🚀 Usage

```bash
# Validate Python environment
python3 config/environments/validate_environment.py

# Full environment validation
./scripts/validate-environment.sh
```
