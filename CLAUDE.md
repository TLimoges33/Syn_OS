# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Build and Testing

```bash

## Build all components

make build

## Run comprehensive test suite

make test
pytest tests/ -v

## Run integration tests

make test-integration
python tests/integration/a_plus_comprehensive_test.py

## Run security tests

python tests/test_security.py
python scripts/a_plus_security_audit.py

## Performance testing

python tests/performance_validation/quick_benchmark.py
```text
## Run comprehensive test suite

make test
pytest tests/ -v

## Run integration tests

make test-integration
python tests/integration/a_plus_comprehensive_test.py

## Run security tests

python tests/test_security.py
python scripts/a_plus_security_audit.py

## Performance testing

python tests/performance_validation/quick_benchmark.py

```text

### Rust Development

```bash
```bash

## Build Rust workspace (kernel, security, consciousness components)

cargo build --workspace

## Run Rust tests

cargo test --workspace

## Build kernel specifically

cd src/kernel && cargo build --target x86_64-syn_os.json

## Run security tests

cd src/security && cargo test
```text
## Run Rust tests

cargo test --workspace

## Build kernel specifically

cd src/kernel && cargo build --target x86_64-syn_os.json

## Run security tests

cd src/security && cargo test

```text

### Development Environment

```bash
```bash

## Setup development environment

./scripts/development/setup-environment.sh

## Start development containers

make dev

## Validate environment

./scripts/validate-environment.sh

## Start security dashboard

./scripts/start-security-dashboard.sh
```text
## Start development containers

make dev

## Validate environment

./scripts/validate-environment.sh

## Start security dashboard

./scripts/start-security-dashboard.sh

```text

### NATS Integration Testing

```bash
```bash

## Test NATS message bus integration

./scripts/test-nats-integration.sh

## Test consciousness NATS integration

./scripts/test-consciousness-nats-integration.sh

## Comprehensive NATS testing

./scripts/test-nats-comprehensive-integration.sh
```text
## Test consciousness NATS integration

./scripts/test-consciousness-nats-integration.sh

## Comprehensive NATS testing

./scripts/test-nats-comprehensive-integration.sh

```text

## Architecture Overview

### Core Components

* *Syn_OS** is a security-first research operating system exploring consciousness integration and advanced AI concepts. The architecture follows a modular design:

### 1. Kernel Layer (`src/kernel/`)

- Rust-based microkernel with educational features
- Security-enhanced memory management
- AI interface hooks for consciousness integration
- Bootloader integration with custom targets (`x86_64-syn_os.json`)

### 2. Security Framework (`src/security/`)

- Zero-trust architecture implementation
- Multi-language security modules (Rust + Python)
- HSM integration for cryptographic operations
- Quantum-resistant cryptography research
- Advanced audit logging and monitoring

### 3. Consciousness System (`src/consciousness_v2/`)

- Neural Darwinism engine implementation
- Event-driven consciousness simulation
- NATS message bus integration for distributed consciousness
- Personal context management
- Decision-making framework

### 4. Service Orchestrator (`services/orchestrator/`)

- Go-based microservices orchestration
- NATS integration for service communication
- PostgreSQL and Redis backend storage
- Health monitoring and service discovery
- RESTful API with Gin framework

### 5. AI Integration (`src/ai_integration/`)

- Multi-model AI orchestration (Claude, Gemini, Perplexity)
- Consciousness-aware AI interfaces
- Educational AI tutoring systems

## Key Architecture Patterns

### Message Bus Architecture

- NATS JetStream for reliable messaging
- Event-driven communication between components
- Consciousness events and system-wide coordination
- Schema validation and message persistence

### Security-First Design

- Input validation at all system boundaries
- Comprehensive audit logging
- Defense-in-depth strategies
- Zero-trust network architecture

### Modular Consciousness Design

- Component-based consciousness simulation
- Pluggable neural processing modules
- State persistence and recovery
- Performance optimization frameworks

## Development Workflows

### Adding New Security Features

1. Implement in `src/security/` (Rust or Python)
2. Add tests in `tests/security_tests.rs` or `tests/test_security.py`
3. Update security audit in `scripts/a_plus_security_audit.py`
4. Run security validation: `make security-scan`

### Extending Consciousness Components

1. Add module to `src/consciousness_v2/components/`
2. Implement consciousness interface in `interfaces/consciousness_component.py`
3. Register with event bus in `components/event_bus.py`
4. Test integration with `test_consciousness_orchestrator_integration.py`

### Kernel Development

1. Modify Rust code in `src/kernel/src/`
2. Build with `cargo build --target x86_64-syn_os.json`
3. Test with `./scripts/build-simple-kernel-iso.sh`
4. Validate with QEMU: `qemu_test_rust.sh`

## Configuration Files

### Python Dependencies

- `config/dependencies/requirements-security.txt` - Security framework
- `config/dependencies/requirements-ai-integration.txt` - AI components
- `config/dependencies/requirements-testing.txt` - Testing framework
- `config/dependencies/requirements-nats.txt` - Message bus integration

### Rust Workspace

- Root `Cargo.toml` defines workspace with kernel, security, consciousness modules
- Custom targets in `src/kernel/x86_64-syn_os.json` for kernel compilation
- Shared dependencies for bootloader, x86_64, security crates

### Container Orchestration

- `docker/docker-compose.yml` - Development environment
- `deploy/docker-compose.production.yml` - Production deployment
- `deploy/docker-compose.ha.yml` - High availability setup

## Testing Strategy

### Test Categories

1. **Unit Tests**: Component-level validation
2. **Integration Tests**: Cross-component communication
3. **Security Tests**: Vulnerability assessment and audit
4. **Performance Tests**: Optimization validation and benchmarking
5. **Consciousness Tests**: AI behavior validation

### Test Execution

- Use `pytest` for Python tests with coverage reporting
- Use `cargo test` for Rust component testing
- Integration tests in `tests/integration/` directory
- Security audits generate reports in `results/security_reports/`

## Key Development Principles

### Security-First Development

- All code must pass security scans before merge
- Input validation required at all system boundaries
- Cryptographic operations use vetted libraries only
- Comprehensive audit logging for all security events

### Consciousness Integration

- Event-driven architecture for consciousness simulation
- NATS message bus for distributed consciousness processing
- State persistence for consciousness continuity
- Performance monitoring for real-time consciousness simulation

### Educational Focus

- Clear documentation for learning operating system concepts
- Security education integration throughout codebase
- AI-assisted learning and tutoring capabilities
- Academic research integration and publication readiness

## Common Development Tasks

### Starting Development Session

```bash
* *Syn_OS** is a security-first research operating system exploring consciousness integration and advanced AI concepts. The architecture follows a modular design:

### 1. Kernel Layer (`src/kernel/`)

- Rust-based microkernel with educational features
- Security-enhanced memory management
- AI interface hooks for consciousness integration
- Bootloader integration with custom targets (`x86_64-syn_os.json`)

### 2. Security Framework (`src/security/`)

- Zero-trust architecture implementation
- Multi-language security modules (Rust + Python)
- HSM integration for cryptographic operations
- Quantum-resistant cryptography research
- Advanced audit logging and monitoring

### 3. Consciousness System (`src/consciousness_v2/`)

- Neural Darwinism engine implementation
- Event-driven consciousness simulation
- NATS message bus integration for distributed consciousness
- Personal context management
- Decision-making framework

### 4. Service Orchestrator (`services/orchestrator/`)

- Go-based microservices orchestration
- NATS integration for service communication
- PostgreSQL and Redis backend storage
- Health monitoring and service discovery
- RESTful API with Gin framework

### 5. AI Integration (`src/ai_integration/`)

- Multi-model AI orchestration (Claude, Gemini, Perplexity)
- Consciousness-aware AI interfaces
- Educational AI tutoring systems

## Key Architecture Patterns

### Message Bus Architecture

- NATS JetStream for reliable messaging
- Event-driven communication between components
- Consciousness events and system-wide coordination
- Schema validation and message persistence

### Security-First Design

- Input validation at all system boundaries
- Comprehensive audit logging
- Defense-in-depth strategies
- Zero-trust network architecture

### Modular Consciousness Design

- Component-based consciousness simulation
- Pluggable neural processing modules
- State persistence and recovery
- Performance optimization frameworks

## Development Workflows

### Adding New Security Features

1. Implement in `src/security/` (Rust or Python)
2. Add tests in `tests/security_tests.rs` or `tests/test_security.py`
3. Update security audit in `scripts/a_plus_security_audit.py`
4. Run security validation: `make security-scan`

### Extending Consciousness Components

1. Add module to `src/consciousness_v2/components/`
2. Implement consciousness interface in `interfaces/consciousness_component.py`
3. Register with event bus in `components/event_bus.py`
4. Test integration with `test_consciousness_orchestrator_integration.py`

### Kernel Development

1. Modify Rust code in `src/kernel/src/`
2. Build with `cargo build --target x86_64-syn_os.json`
3. Test with `./scripts/build-simple-kernel-iso.sh`
4. Validate with QEMU: `qemu_test_rust.sh`

## Configuration Files

### Python Dependencies

- `config/dependencies/requirements-security.txt` - Security framework
- `config/dependencies/requirements-ai-integration.txt` - AI components
- `config/dependencies/requirements-testing.txt` - Testing framework
- `config/dependencies/requirements-nats.txt` - Message bus integration

### Rust Workspace

- Root `Cargo.toml` defines workspace with kernel, security, consciousness modules
- Custom targets in `src/kernel/x86_64-syn_os.json` for kernel compilation
- Shared dependencies for bootloader, x86_64, security crates

### Container Orchestration

- `docker/docker-compose.yml` - Development environment
- `deploy/docker-compose.production.yml` - Production deployment
- `deploy/docker-compose.ha.yml` - High availability setup

## Testing Strategy

### Test Categories

1. **Unit Tests**: Component-level validation
2. **Integration Tests**: Cross-component communication
3. **Security Tests**: Vulnerability assessment and audit
4. **Performance Tests**: Optimization validation and benchmarking
5. **Consciousness Tests**: AI behavior validation

### Test Execution

- Use `pytest` for Python tests with coverage reporting
- Use `cargo test` for Rust component testing
- Integration tests in `tests/integration/` directory
- Security audits generate reports in `results/security_reports/`

## Key Development Principles

### Security-First Development

- All code must pass security scans before merge
- Input validation required at all system boundaries
- Cryptographic operations use vetted libraries only
- Comprehensive audit logging for all security events

### Consciousness Integration

- Event-driven architecture for consciousness simulation
- NATS message bus for distributed consciousness processing
- State persistence for consciousness continuity
- Performance monitoring for real-time consciousness simulation

### Educational Focus

- Clear documentation for learning operating system concepts
- Security education integration throughout codebase
- AI-assisted learning and tutoring capabilities
- Academic research integration and publication readiness

## Common Development Tasks

### Starting Development Session

```bash

## 1. Validate environment

./scripts/validate-environment.sh

## 2. Start containers

make dev

## 3. Run quick tests

make test

## 4. Start security dashboard

./scripts/start-security-dashboard.sh
```text
## 2. Start containers

make dev

## 3. Run quick tests

make test

## 4. Start security dashboard

./scripts/start-security-dashboard.sh

```text

### Before Committing Changes

```bash
```bash

## 1. Run security audit

python scripts/a_plus_security_audit.py

## 2. Run comprehensive tests

make test && cargo test --workspace

## 3. Check test coverage

pytest tests/ --cov=src --cov-report=term-missing

## 4. Validate integration

./scripts/test-nats-integration.sh
```text
## 2. Run comprehensive tests

make test && cargo test --workspace

## 3. Check test coverage

pytest tests/ --cov=src --cov-report=term-missing

## 4. Validate integration

./scripts/test-nats-integration.sh

```text

## Important File Locations

- **Main configuration**: `config/syn_os_config.yaml`
- **Security configurations**: `config/security/`
- **Development scripts**: `scripts/development/`
- **Test results**: `results/` (security_reports, performance_reports, coverage_reports)
- **Documentation**: `docs/` (architecture, guides, research)
- **Container definitions**: `docker/` and `deploy/`
- **Development scripts**: `scripts/development/`
- **Test results**: `results/` (security_reports, performance_reports, coverage_reports)
- **Documentation**: `docs/` (architecture, guides, research)
- **Container definitions**: `docker/` and `deploy/`