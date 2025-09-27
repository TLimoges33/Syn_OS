# Development Guide

## Development Workflow

### Getting Started

1. Set up development environment ([Getting Started](../01-getting-started/README.md))
2. Review architecture ([Architecture](../02-architecture/README.md))
3. Configure development tools

### Code Organization

```
src/
├── kernel/          # Core kernel implementation
├── consciousness/   # neural networks substrate
├── security/        # Security framework
└── userspace/       # User applications
```

### Build System

```bash
# Build kernel
make build-kernel

# Build consciousness components
make build-consciousness

# Build security framework
make build-security

# Run comprehensive tests
make test
```

## Comprehensive Development Resources

### Development Standards and Workflows

- [Code Standards](./CODE_STANDARDS.md) - Coding conventions and best practices
- [Git Workflow Architecture](./GIT_WORKFLOW_ARCHITECTURE.md) - Version control workflows
- [Getting Started Guide](./GETTING_STARTED.md) - Detailed development setup
- [Kubernetes Development](./KUBERNETES_DEVELOPMENT_GUIDE.md) - Container development

### Implementation Documentation

- [Implementation Complete](./IMPLEMENTATION_COMPLETE.md) - Current implementation status
- [Current Implementation TODO](./CURRENT_IMPLEMENTATION_TODO.md) - Active development tasks
- [TODO Implementation Status](./TODO_IMPLEMENTATION_STATUS.md) - Task tracking

### Architecture and Security

- [Architecture Guide](./ARCHITECTURE_GUIDE.md) - System architecture details
- [Security Architecture](./SECURITY_ARCHITECTURE.md) - Security implementation
- [MCP Security Policy](./MCP_SECURITY_POLICY.md) - Model Context Protocol security

### Development Documentation

```
development/
├── phases/          # Phase-specific documentation
├── roadmaps/        # Project roadmaps
└── README.md        # Development overview
```

### Development Standards

- Code follows Rust best practices
- All components must include comprehensive tests
- Security reviews required for core components
- Documentation updates required with code changes

## Testing Framework

- Unit tests for all components
- Integration tests for system interfaces
- Security validation tests
- Performance benchmarks

## Documentation

- [Code Standards](./CODE_STANDARDS.md)
- [Testing Guide](./TESTING.md)
- [Security Guidelines](./SECURITY_GUIDELINES.md)

### Setup Guides

- [Claude CLI Setup](./claude-setup.md) - Setting up Claude CLI for development
- [Claude MCP Setup Guide](./CLAUDE_MCP_SETUP_GUIDE.md) - Complete MCP configuration

## Team Workflows

- [Development Team Workflow](workflows/DEV_TEAM_WORKFLOW_GUIDE.md)
- [Team Collaboration Guide](workflows/TEAM_COLLABORATION_GUIDE.md)
