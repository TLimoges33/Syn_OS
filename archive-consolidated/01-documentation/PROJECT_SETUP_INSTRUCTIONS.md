# Syn_OS Project Setup Instructions

**Version**: 1.0  
**Date**: 2025-07-23  
**Purpose**: Instructions and scripts for setting up the Syn_OS project structure

## Quick Setup

Copy and run this script to create the complete project structure:

```bash
#!/bin/bash

# Syn_OS Project Structure Setup Script
# Version: 1.0
# Date: 2025-07-23

set -e  # Exit on error

echo "🚀 Setting up Syn_OS project structure..."

# Define colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to create directory with message
create_dir() {
    mkdir -p "$1"
    echo -e "${GREEN}✓${NC} Created: $1"
}

# Function to create file with template
create_file() {
    touch "$1"
    echo -e "${BLUE}✓${NC} Created: $1"
}

# Root directory
PROJECT_ROOT="syn_os"
create_dir "$PROJECT_ROOT"
cd "$PROJECT_ROOT"

# Create root level directories
echo -e "\n${YELLOW}Creating root directories...${NC}"
create_dir ".github/workflows"
create_dir ".github/ISSUE_TEMPLATE"
create_dir ".gitlab/ci"
create_dir "docs/architecture"
create_dir "docs/api"
create_dir "docs/guides"
create_dir "docs/security"
create_dir "docs/images"
create_dir "parrot-base"
create_dir "vendor"

# Create synapticos-overlay structure
echo -e "\n${YELLOW}Creating synapticos-overlay structure...${NC}"
create_dir "synapticos-overlay/consciousness/neural_darwinism"
create_dir "synapticos-overlay/consciousness/api"
create_dir "synapticos-overlay/consciousness/services"
create_dir "synapticos-overlay/consciousness/config"
create_dir "synapticos-overlay/consciousness/tests/unit"
create_dir "synapticos-overlay/consciousness/tests/integration"
create_dir "synapticos-overlay/consciousness/scripts"

create_dir "synapticos-overlay/context-engine/src/models"
create_dir "synapticos-overlay/context-engine/src/trackers"
create_dir "synapticos-overlay/context-engine/src/storage"
create_dir "synapticos-overlay/context-engine/src/api"
create_dir "synapticos-overlay/context-engine/migrations/alembic"
create_dir "synapticos-overlay/context-engine/tests"
create_dir "synapticos-overlay/context-engine/config"

create_dir "synapticos-overlay/kernel-mods"
create_dir "synapticos-overlay/lm-studio/api"
create_dir "synapticos-overlay/lm-studio/config"
create_dir "synapticos-overlay/lm-studio/tests"

create_dir "synapticos-overlay/security/src/auth"
create_dir "synapticos-overlay/security/src/authz"
create_dir "synapticos-overlay/security/src/crypto"
create_dir "synapticos-overlay/security/src/api"
create_dir "synapticos-overlay/security/src/storage"
create_dir "synapticos-overlay/security/tests/unit"
create_dir "synapticos-overlay/security/tests/integration"
create_dir "synapticos-overlay/security/benches"
create_dir "synapticos-overlay/security/examples"

create_dir "synapticos-overlay/security-tutor/backend/src/lessons"
create_dir "synapticos-overlay/security-tutor/backend/src/labs"
create_dir "synapticos-overlay/security-tutor/backend/src/assessment"
create_dir "synapticos-overlay/security-tutor/backend/src/api"
create_dir "synapticos-overlay/security-tutor/backend/tests"
create_dir "synapticos-overlay/security-tutor/frontend/src/components"
create_dir "synapticos-overlay/security-tutor/frontend/src/pages"
create_dir "synapticos-overlay/security-tutor/frontend/src/services"
create_dir "synapticos-overlay/security-tutor/frontend/src/hooks"
create_dir "synapticos-overlay/security-tutor/frontend/src/utils"
create_dir "synapticos-overlay/security-tutor/frontend/public"
create_dir "synapticos-overlay/security-tutor/content/lessons"
create_dir "synapticos-overlay/security-tutor/content/exercises"
create_dir "synapticos-overlay/security-tutor/content/solutions"

# Create services structure
echo -e "\n${YELLOW}Creating services structure...${NC}"
create_dir "synapticos-overlay/services/orchestrator/cmd/orchestrator"
create_dir "synapticos-overlay/services/orchestrator/internal/api"
create_dir "synapticos-overlay/services/orchestrator/internal/config"
create_dir "synapticos-overlay/services/orchestrator/internal/core"
create_dir "synapticos-overlay/services/orchestrator/internal/models"
create_dir "synapticos-overlay/services/orchestrator/internal/storage"
create_dir "synapticos-overlay/services/orchestrator/pkg/client"
create_dir "synapticos-overlay/services/orchestrator/api"
create_dir "synapticos-overlay/services/orchestrator/configs"
create_dir "synapticos-overlay/services/orchestrator/deployments"
create_dir "synapticos-overlay/services/orchestrator/tests/unit"
create_dir "synapticos-overlay/services/orchestrator/tests/integration"

create_dir "synapticos-overlay/services/message-bus/config/tls"
create_dir "synapticos-overlay/services/message-bus/clients/python"
create_dir "synapticos-overlay/services/message-bus/clients/go"
create_dir "synapticos-overlay/services/message-bus/clients/javascript"
create_dir "synapticos-overlay/services/message-bus/schemas/generated"
create_dir "synapticos-overlay/services/message-bus/scripts"

create_dir "synapticos-overlay/dashboard/src"
create_dir "synapticos-overlay/cli/src"
create_dir "synapticos-overlay/api-gateway/plugins"
create_dir "synapticos-overlay/config/global"

# Create test structure
echo -e "\n${YELLOW}Creating test structure...${NC}"
create_dir "tests/unit/consciousness"
create_dir "tests/unit/context-engine"
create_dir "tests/unit/security"
create_dir "tests/unit/services"
create_dir "tests/integration/api"
create_dir "tests/integration/message-bus"
create_dir "tests/integration/workflows"
create_dir "tests/e2e/scenarios"
create_dir "tests/e2e/fixtures"
create_dir "tests/security/penetration"
create_dir "tests/security/vulnerability"
create_dir "tests/security/compliance"
create_dir "tests/performance/load"
create_dir "tests/performance/stress"
create_dir "tests/performance/benchmarks"
create_dir "tests/fixtures"
create_dir "tests/mocks"
create_dir "tests/utils"

# Create scripts structure
echo -e "\n${YELLOW}Creating scripts structure...${NC}"
create_dir "scripts/build"
create_dir "scripts/deploy"
create_dir "scripts/dev"
create_dir "scripts/test"
create_dir "scripts/utils"

# Create tools structure
echo -e "\n${YELLOW}Creating tools structure...${NC}"
create_dir "tools/generators"
create_dir "tools/analyzers"
create_dir "tools/migrations"

# Create config structure
echo -e "\n${YELLOW}Creating config structure...${NC}"
create_dir "config/base"
create_dir "config/development"
create_dir "config/staging"
create_dir "config/production"
create_dir "config/schemas"

# Create deployment structure
echo -e "\n${YELLOW}Creating deployment structure...${NC}"
create_dir "deployments/docker"
create_dir "deployments/kubernetes"
create_dir "deployments/terraform"

# Create standard files
echo -e "\n${YELLOW}Creating standard files...${NC}"

# Root files
create_file "README.md"
create_file "LICENSE"
create_file "CHANGELOG.md"
create_file "CONTRIBUTING.md"
create_file "CODE_OF_CONDUCT.md"
create_file ".gitignore"
create_file ".gitattributes"
create_file ".pre-commit-config.yaml"
create_file "Makefile"

# GitHub files
create_file ".github/PULL_REQUEST_TEMPLATE.md"
create_file ".github/workflows/ci.yml"
create_file ".github/workflows/cd.yml"
create_file ".github/workflows/security-scan.yml"

# Component README files
create_file "synapticos-overlay/consciousness/README.md"
create_file "synapticos-overlay/context-engine/README.md"
create_file "synapticos-overlay/security/README.md"
create_file "synapticos-overlay/security-tutor/README.md"
create_file "synapticos-overlay/services/orchestrator/README.md"
create_file "synapticos-overlay/services/message-bus/README.md"

# Component specific files
create_file "synapticos-overlay/consciousness/requirements.txt"
create_file "synapticos-overlay/consciousness/Dockerfile"
create_file "synapticos-overlay/consciousness/Makefile"

create_file "synapticos-overlay/context-engine/requirements.txt"
create_file "synapticos-overlay/context-engine/Dockerfile"
create_file "synapticos-overlay/context-engine/Makefile"

create_file "synapticos-overlay/security/Cargo.toml"
create_file "synapticos-overlay/security/Dockerfile"
create_file "synapticos-overlay/security/Makefile"

create_file "synapticos-overlay/services/orchestrator/go.mod"
create_file "synapticos-overlay/services/orchestrator/Dockerfile"
create_file "synapticos-overlay/services/orchestrator/Makefile"

# Test files
create_file "tests/conftest.py"
create_file "tests/Makefile"

# Config files
create_file "config/base/services.yaml"
create_file "config/base/security.yaml"
create_file "config/base/logging.yaml"
create_file "config/development/.env.example"

# Script files
create_file "scripts/build/build-all.sh"
create_file "scripts/deploy/deploy-local.sh"
create_file "scripts/dev/setup-dev.sh"
create_file "scripts/test/run-unit.sh"

echo -e "\n${GREEN}✅ Syn_OS project structure created successfully!${NC}"
echo -e "${BLUE}📁 Total directories created: $(find . -type d | wc -l)${NC}"
echo -e "${BLUE}📄 Total files created: $(find . -type f | wc -l)${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. cd $PROJECT_ROOT"
echo "2. git init"
echo "3. Copy existing code to appropriate directories"
echo "4. Run 'make setup' to install dependencies"
```

## Manual Setup Steps

If you prefer to set up the structure manually or need to understand what each directory is for:

### 1. Create Root Directory
```bash
mkdir syn_os && cd syn_os
```

### 2. Initialize Git Repository
```bash
git init
echo "# Syn_OS - AI-Enhanced Cybersecurity Operating System" > README.md
```

### 3. Create .gitignore
```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env
.venv

# Go
*.exe
*.exe~
*.dll
*.so
*.dylib
*.test
*.out
vendor/

# Rust
target/
Cargo.lock
**/*.rs.bk

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Docker
.docker/

# Secrets
*.key
*.pem
*.crt
secrets/
*.secret

# Build artifacts
build/
dist/
*.iso
*.img

# Logs
logs/
*.log

# Test coverage
.coverage
coverage/
htmlcov/
*.cover
.pytest_cache/

# Documentation
docs/_build/
site/
EOF
```

### 4. Create Initial Makefile
```bash
cat > Makefile << 'EOF'
.PHONY: help setup build test clean

help:
	@echo "Available targets:"
	@echo "  setup    - Set up development environment"
	@echo "  build    - Build all components"
	@echo "  test     - Run all tests"
	@echo "  clean    - Clean build artifacts"

setup:
	@echo "Setting up development environment..."
	@./scripts/dev/setup-dev.sh

build:
	@echo "Building all components..."
	@./scripts/build/build-all.sh

test:
	@echo "Running tests..."
	@./scripts/test/run-unit.sh
	@./scripts/test/run-integration.sh

clean:
	@echo "Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name "target" -exec rm -rf {} +
	@find . -type d -name "build" -exec rm -rf {} +
	@find . -type d -name "dist" -exec rm -rf {} +
EOF
```

### 5. Create Component Templates

#### Python Component Template
```bash
# For any Python component (consciousness, context-engine, etc.)
cat > synapticos-overlay/component-name/setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="synos-component-name",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # Add dependencies
    ],
    python_requires=">=3.9",
)
EOF
```

#### Go Component Template
```bash
# For any Go component (orchestrator, etc.)
cat > synapticos-overlay/services/component-name/go.mod << 'EOF'
module github.com/syn-os/component-name

go 1.21

require (
    // Add dependencies
)
EOF
```

#### Rust Component Template
```bash
# For Rust components (security framework)
cat > synapticos-overlay/security/Cargo.toml << 'EOF'
[package]
name = "synos-security"
version = "0.1.0"
edition = "2021"

[dependencies]
# Add dependencies

[dev-dependencies]
# Add dev dependencies
EOF
```

## Component-Specific Setup

### Service Orchestrator Setup
```bash
cd synapticos-overlay/services/orchestrator
go mod init github.com/syn-os/orchestrator
go get github.com/docker/docker/client
go get github.com/gorilla/mux
go get github.com/spf13/viper
```

### Message Bus Setup
```bash
cd synapticos-overlay/services/message-bus
docker pull nats:latest
# Create NATS configuration
cat > config/nats.conf << 'EOF'
port: 4222
monitor_port: 8222

cluster {
  port: 6222
  routes: []
}

authorization {
  users: [
    {user: synos, password: "$2a$10$..."}
  ]
}
EOF
```

### Security Framework Setup
```bash
cd synapticos-overlay/security
cargo init --name synos-security
cargo add tokio --features full
cargo add jsonwebtoken
cargo add argon2
cargo add serde --features derive
```

## Verification

After running the setup script, verify the structure:

```bash
# Count directories
find . -type d | wc -l
# Should be around 150+ directories

# Count files
find . -type f | wc -l
# Should be around 50+ files

# Verify key directories exist
for dir in consciousness context-engine security services/orchestrator; do
    if [ -d "synapticos-overlay/$dir" ]; then
        echo "✓ $dir exists"
    else
        echo "✗ $dir missing"
    fi
done
```

## Next Steps

1. **Copy existing code** to the appropriate directories
2. **Set up development environment** using the onboarding guide
3. **Start with critical components** as defined in the priority list
4. **Follow the architecture blueprint** for implementation details

## Troubleshooting

### Permission Issues
```bash
# If you get permission denied
chmod +x scripts/**/*.sh
```

### Missing Directories
```bash
# Re-run the setup script
./scripts/setup-project-structure.sh
```

### Git Issues
```bash
# If git init fails
rm -rf .git
git init
```

This setup creates a professional, scalable project structure ready for team development.