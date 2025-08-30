# Syn_OS Developer Onboarding Guide

**Welcome to the Syn_OS Development Team!**

This guide will help you get started with contributing to Syn_OS, an AI-enhanced cybersecurity operating system built on ParrotOS.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Development Environment Setup](#development-environment-setup)
3. [Architecture Overview](#architecture-overview)
4. [Getting Started](#getting-started)
5. [Development Workflow](#development-workflow)
6. [Coding Standards](#coding-standards)
7. [Testing Guidelines](#testing-guidelines)
8. [Communication Channels](#communication-channels)

## Project Overview

### What is Syn_OS?
Syn_OS is a ParrotOS fork that integrates:
- AI consciousness system using Neural Darwinism
- Local LM Studio for privacy-focused AI processing
- Personal context engine for adaptive learning
- Interactive security tutor for cybersecurity education
- Custom kernel modifications for AI-OS interaction

### Key Technologies
- **Languages**: Python (AI/Services), C (Kernel), Go (Orchestration), Rust (Security)
- **AI Framework**: LM Studio (local inference)
- **Base OS**: ParrotOS (Debian-based)
- **Containerization**: Docker, Docker Compose
- **Message Bus**: NATS/RabbitMQ
- **API Gateway**: Kong
- **Monitoring**: Prometheus, Grafana, Loki

## Development Environment Setup

### Prerequisites
```bash
# System Requirements
- Ubuntu 22.04+ or Debian 11+ (recommended)
- 16GB RAM minimum
- 100GB free disk space
- Docker and Docker Compose
- Git

# Required Tools
sudo apt update
sudo apt install -y \
    build-essential \
    git \
    docker.io \
    docker-compose \
    python3-pip \
    python3-venv \
    golang-go \
    rustc \
    cargo \
    linux-headers-$(uname -r) \
    nodejs \
    npm
```

### Initial Setup

1. **Clone the Repository**
```bash
git clone https://github.com/your-org/syn_os.git
cd syn_os
```

2. **Set Up Development Environment**
```bash
# Run the setup script
./scripts/dev-setup.sh

# This will:
# - Create Python virtual environments
# - Install dependencies
# - Set up Docker networks
# - Initialize configuration files
```

3. **Configure LM Studio**
```bash
# Install LM Studio (if not already installed)
wget https://lmstudio.ai/downloads/latest/linux -O lmstudio.AppImage
chmod +x lmstudio.AppImage
./lmstudio.AppImage

# Configure for Syn_OS
cp config/lmstudio.example.json ~/.lmstudio/config.json
```

4. **Build Development Containers**
```bash
cd synapticos-overlay/
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d
```

## Architecture Overview

### System Layers
1. **User Interface Layer**: Desktop, Terminal, Web Dashboard
2. **Application Services**: Security Tutor, Learning Engine
3. **Core Services**: Neural Darwinism, Context Engine, LM Studio
4. **System Services**: Orchestrator, Message Bus, Security
5. **Kernel Layer**: Microprocess API, AI Hooks, ParrotOS Base

### Key Components You'll Work With

#### 1. Neural Darwinism Engine (Python)
- Location: `synapticos-overlay/consciousness/`
- Purpose: AI consciousness and decision-making
- Key Files: `neural_darwinism.py`, `consciousness_api.py`

#### 2. Context Engine (Python)
- Location: `synapticos-overlay/context-engine/`
- Purpose: User behavior tracking and personalization
- Key Files: `personal_context.py`, `skill_tracker.py`

#### 3. Service Orchestrator (Go)
- Location: `synapticos-overlay/services/orchestrator/`
- Purpose: Manage service lifecycle and dependencies
- Key Files: `main.go`, `service_manager.go`

#### 4. Security Framework (Rust)
- Location: `synapticos-overlay/security/`
- Purpose: Authentication, authorization, encryption
- Key Files: `lib.rs`, `auth.rs`, `crypto.rs`

## Getting Started

### Your First Contribution

1. **Pick a Starter Issue**
   - Look for issues labeled `good-first-issue`
   - Check the [Critical Components List](./CRITICAL_COMPONENTS_PRIORITY.md)
   - Join #dev-chat to ask for suggestions

2. **Set Up Your Branch**
```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bugfixes
git checkout -b fix/issue-description
```

3. **Make Your Changes**
   - Follow the coding standards (see below)
   - Write tests for new functionality
   - Update documentation as needed

4. **Test Your Changes**
```bash
# Run unit tests
make test-unit

# Run integration tests
make test-integration

# Run linting
make lint
```

5. **Submit a Pull Request**
   - Push your branch: `git push origin feature/your-feature-name`
   - Create PR via GitHub/GitLab
   - Fill out the PR template completely
   - Request review from appropriate team members

## Development Workflow

### Daily Development

1. **Morning Sync**
   - Check #dev-updates for overnight changes
   - Pull latest changes: `git pull origin main`
   - Review assigned issues

2. **Development Process**
   - Work in feature branches
   - Commit frequently with clear messages
   - Run tests before pushing
   - Update documentation inline

3. **Code Review**
   - Review others' PRs promptly
   - Provide constructive feedback
   - Test changes locally when needed

### Component Development

#### Python Components
```bash
# Navigate to component
cd synapticos-overlay/your-component/

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run component
python main.py

# Run tests
pytest tests/
```

#### Go Components
```bash
# Navigate to component
cd synapticos-overlay/services/your-service/

# Get dependencies
go mod download

# Run service
go run main.go

# Run tests
go test ./...

# Build
go build -o your-service
```

#### Rust Components
```bash
# Navigate to component
cd synapticos-overlay/security/

# Build
cargo build

# Run tests
cargo test

# Run with logging
RUST_LOG=debug cargo run
```

## Coding Standards

### General Principles
1. **Clarity over Cleverness**: Write readable code
2. **Document Everything**: Functions, classes, modules
3. **Test Everything**: Aim for 80%+ coverage
4. **Security First**: Consider security implications
5. **Performance Matters**: Profile and optimize

### Language-Specific Standards

#### Python
- Follow PEP 8
- Use type hints
- Docstrings for all public functions
- Async/await for I/O operations

#### Go
- Follow official Go style guide
- Use `gofmt` and `golint`
- Handle all errors explicitly
- Use contexts for cancellation

#### Rust
- Follow Rust style guide
- Use `rustfmt` and `clippy`
- Prefer safe code, document unsafe blocks
- Use Result<T, E> for error handling

#### C (Kernel)
- Follow Linux kernel coding style
- Comment complex logic
- Validate all inputs
- No dynamic memory in interrupt context

## Testing Guidelines

### Test Types

1. **Unit Tests**
   - Test individual functions/methods
   - Mock external dependencies
   - Fast execution (<1s per test)

2. **Integration Tests**
   - Test component interactions
   - Use test containers
   - Verify API contracts

3. **Security Tests**
   - Input validation tests
   - Authentication/authorization tests
   - Penetration testing (coordinated)

### Writing Tests

#### Python Example
```python
import pytest
from unittest.mock import Mock

def test_context_engine_update():
    """Test that context engine updates user profile correctly."""
    engine = ContextEngine()
    user_id = "test_user"
    
    # Test skill update
    engine.update_skill(user_id, "nmap", 0.7)
    
    profile = engine.get_profile(user_id)
    assert profile.skills["nmap"] == 0.7
```

#### Go Example
```go
func TestServiceOrchestrator(t *testing.T) {
    orchestrator := NewOrchestrator()
    
    // Test service registration
    err := orchestrator.RegisterService("test-service", &ServiceConfig{})
    assert.NoError(t, err)
    
    // Test service start
    err = orchestrator.StartService("test-service")
    assert.NoError(t, err)
}
```

## Communication Channels

### Development Channels
- **#dev-general**: General development discussion
- **#dev-help**: Ask for help with issues
- **#code-review**: PR review requests
- **#architecture**: Architecture discussions

### Meetings
- **Weekly Dev Sync**: Mondays 10 AM EST
- **Architecture Review**: Thursdays 2 PM EST
- **Sprint Planning**: Every 2 weeks

### Documentation
- **Wiki**: Internal documentation and guides
- **API Docs**: Auto-generated from code
- **Architecture Docs**: In `docs/architecture/`

## Getting Help

### Resources
1. [Architecture Blueprint](./SYN_OS_ARCHITECTURE_BLUEPRINT.md)
2. [API Documentation](./api/)
3. [Component Guides](./guides/components/)
4. [Security Guidelines](./SECURITY_GUIDELINES.md)

### Mentorship
- New developers are paired with a mentor
- Weekly 1:1 sessions for first month
- Code review from mentor on first 5 PRs

### Common Issues

#### Docker Issues
```bash
# Reset Docker environment
docker-compose down -v
docker system prune -a
docker-compose up -d
```

#### Build Issues
```bash
# Clean build artifacts
make clean
rm -rf build/ dist/

# Rebuild
make build
```

#### Test Failures
```bash
# Run specific test with verbose output
pytest -vvs tests/test_specific.py::test_function

# Debug Go tests
go test -v -run TestSpecific
```

## Next Steps

1. **Complete Environment Setup** (30 mins)
2. **Read Architecture Blueprint** (1 hour)
3. **Run Example Components** (1 hour)
4. **Pick Your First Issue** (30 mins)
5. **Join Team Channels** (15 mins)

Welcome aboard! We're excited to have you contributing to Syn_OS. Remember, no question is too small - we're here to help you succeed.

---

**Quick Links:**
- [Issue Tracker](https://github.com/your-org/syn_os/issues)
- [Project Board](https://github.com/your-org/syn_os/projects)
- [CI/CD Dashboard](https://ci.syn-os.dev)
- [Team Calendar](https://calendar.syn-os.dev)