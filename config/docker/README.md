# 🐳 Docker Configuration

## 📁 Container Infrastructure

This directory contains Docker configurations for SynOS testing and development.

### **Test Environment**

- **`docker-compose.test.yml`** - Docker Compose configuration for testing environment setup

## 🔗 Integration

Related container configurations:

- `/docker/` - Main Docker configurations and Dockerfiles
- [`../environments/`](../environments/) - Environment validation
- [`../core/`](../core/) - Core system configuration

## 🚀 Usage

```bash
# Start test environment
docker-compose -f config/docker/docker-compose.test.yml up -d

# Run tests in containers
docker-compose -f config/docker/docker-compose.test.yml exec test make test
```
