# 🔧 Component Dependencies

## 📁 Component-Specific Python Requirements

This directory contains specialized Python requirements files for different SynOS components.

### **AI & Machine Learning**

- **`requirements-ai-integration.txt`** - AI/ML dependencies including TensorFlow, PyTorch, and consciousness frameworks

### **Consciousness System**

- **`requirements-consciousness.txt`** - Consciousness system dependencies for quantum substrate and neural processing

### **Infrastructure**

- **`requirements-nats.txt`** - NATS message bus dependencies for distributed communication
- **`requirements-testing.txt`** - Testing framework dependencies including pytest, coverage, and integration tools

### **Security Tools**

- **`requirements-security.txt`** - Security tool dependencies for monitoring, scanning, and compliance

## 🔗 Integration

These requirements integrate with:

- [`../core/requirements.txt`](../core/requirements.txt) - Unified base requirements
- Component-specific installation scripts in `/scripts/`

## 🚀 Usage

```bash
# Install specific component dependencies
pip install -r config/dependencies/requirements-ai-integration.txt

# Install all dependencies
pip install -r config/core/requirements.txt
```
