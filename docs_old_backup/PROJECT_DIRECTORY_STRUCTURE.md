# Syn_OS Complete Directory Structure

**Version**: 1.0  
**Date**: 2025-07-23  
**Purpose**: Define the complete directory structure for Syn_OS development

## Root Directory Structure

```
syn_os/
├── .github/                      # GitHub specific files
│   ├── workflows/               # CI/CD workflows
│   ├── ISSUE_TEMPLATE/         # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md
├── .gitlab/                     # GitLab specific files (if using)
│   └── ci/                     # CI/CD templates
├── docs/                       # Documentation
│   ├── architecture/          # Architecture documents
│   ├── api/                   # API documentation
│   ├── guides/                # User and developer guides
│   ├── security/              # Security documentation
│   └── images/                # Documentation images
├── synapticos-overlay/         # Main SynapticOS code
│   ├── consciousness/         # AI consciousness system
│   ├── context-engine/        # Personal context tracking
│   ├── kernel-mods/           # Kernel modifications
│   ├── lm-studio/            # LM Studio integration
│   ├── security/             # Security framework
│   ├── security-tutor/       # Educational modules
│   ├── services/             # Core services
│   ├── dashboard/            # Web dashboard
│   ├── cli/                  # Command-line interface
│   ├── api-gateway/          # Kong configuration
│   └── config/               # Global configuration
├── parrot-base/              # ParrotOS base (submodule)
├── tests/                    # Test suites
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   ├── e2e/                 # End-to-end tests
│   ├── security/            # Security tests
│   └── performance/         # Performance tests
├── scripts/                  # Build and utility scripts
│   ├── build/              # Build scripts
│   ├── deploy/             # Deployment scripts
│   ├── dev/                # Development utilities
│   └── test/               # Test runners
├── tools/                   # Development tools
│   ├── generators/         # Code generators
│   ├── analyzers/          # Code analyzers
│   └── migrations/         # Migration tools
├── config/                  # Configuration templates
│   ├── development/        # Dev environment configs
│   ├── staging/            # Staging configs
│   └── production/         # Production configs
├── deployments/            # Deployment configurations
│   ├── docker/            # Docker files
│   ├── kubernetes/        # K8s manifests
│   └── terraform/         # Infrastructure as code
└── vendor/                 # Third-party dependencies
```

## Detailed Component Structure

### Service Orchestrator
```
synapticos-overlay/services/orchestrator/
├── cmd/
│   └── orchestrator/
│       └── main.go              # Entry point
├── internal/
│   ├── api/                     # API handlers
│   │   ├── handlers.go
│   │   ├── middleware.go
│   │   └── routes.go
│   ├── config/                  # Configuration
│   │   ├── config.go
│   │   └── validation.go
│   ├── core/                    # Core business logic
│   │   ├── orchestrator.go
│   │   ├── service_manager.go
│   │   └── health_checker.go
│   ├── models/                  # Data models
│   │   ├── service.go
│   │   └── health.go
│   └── storage/                 # Data persistence
│       ├── interface.go
│       └── memory.go
├── pkg/                         # Public packages
│   └── client/
│       └── client.go
├── api/                         # API definitions
│   └── openapi.yaml
├── configs/                     # Configuration files
│   └── default.yaml
├── deployments/                 # Deployment files
│   ├── Dockerfile
│   └── docker-compose.yml
├── tests/                       # Component tests
│   ├── unit/
│   └── integration/
├── Makefile
├── go.mod
├── go.sum
└── README.md
```

### Message Bus
```
synapticos-overlay/services/message-bus/
├── config/
│   ├── nats.conf               # NATS configuration
│   ├── nats-cluster.conf       # Cluster configuration
│   └── tls/                    # TLS certificates
├── clients/                    # Client libraries
│   ├── python/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── events.py
│   │   └── requirements.txt
│   ├── go/
│   │   ├── client.go
│   │   ├── events.go
│   │   └── go.mod
│   └── javascript/
│       ├── index.js
│       ├── events.js
│       └── package.json
├── schemas/                    # Event schemas
│   ├── events.proto           # Protobuf definitions
│   ├── events.json            # JSON Schema
│   └── generated/             # Generated code
├── scripts/
│   ├── setup.sh
│   └── test-connection.sh
├── docker-compose.yml
└── README.md
```

### Security Framework
```
synapticos-overlay/security/
├── src/
│   ├── lib.rs                  # Library entry point
│   ├── auth/                   # Authentication module
│   │   ├── mod.rs
│   │   ├── jwt.rs
│   │   ├── oauth.rs
│   │   └── mfa.rs
│   ├── authz/                  # Authorization module
│   │   ├── mod.rs
│   │   ├── rbac.rs
│   │   ├── policies.rs
│   │   └── evaluator.rs
│   ├── crypto/                 # Cryptography module
│   │   ├── mod.rs
│   │   ├── encryption.rs
│   │   ├── hashing.rs
│   │   └── keys.rs
│   ├── api/                    # API module
│   │   ├── mod.rs
│   │   ├── handlers.rs
│   │   └── middleware.rs
│   └── storage/                # Storage backends
│       ├── mod.rs
│       ├── vault.rs
│       └── redis.rs
├── tests/
│   ├── unit/
│   └── integration/
├── benches/                    # Benchmarks
│   └── crypto_bench.rs
├── examples/                   # Usage examples
│   ├── basic_auth.rs
│   └── jwt_validation.rs
├── Cargo.toml
├── Cargo.lock
├── Dockerfile
└── README.md
```

### Neural Darwinism Engine
```
synapticos-overlay/consciousness/
├── neural_darwinism/
│   ├── __init__.py
│   ├── engine.py              # Core engine
│   ├── population.py          # Neural populations
│   ├── selection.py           # Selection mechanisms
│   ├── evolution.py           # Evolution algorithms
│   └── emergence.py           # Emergence detection
├── api/
│   ├── __init__.py
│   ├── app.py                # FastAPI application
│   ├── routes.py             # API routes
│   ├── models.py             # Pydantic models
│   └── dependencies.py       # Dependency injection
├── services/
│   ├── __init__.py
│   ├── consciousness_service.py
│   └── message_handler.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── scripts/
│   ├── train_model.py
│   └── evaluate.py
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

### Context Engine
```
synapticos-overlay/context-engine/
├── src/
│   ├── __init__.py
│   ├── context_engine.py      # Main engine
│   ├── models/                # Data models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── skill.py
│   │   └── activity.py
│   ├── trackers/              # Tracking modules
│   │   ├── __init__.py
│   │   ├── skill_tracker.py
│   │   ├── activity_tracker.py
│   │   └── progress_tracker.py
│   ├── storage/               # Storage layer
│   │   ├── __init__.py
│   │   ├── interface.py
│   │   ├── postgres.py
│   │   └── redis.py
│   └── api/                   # API layer
│       ├── __init__.py
│       ├── app.py
│       └── routes.py
├── migrations/                # Database migrations
│   └── alembic/
├── tests/
├── config/
├── requirements.txt
├── Dockerfile
└── README.md
```

### Security Tutor
```
synapticos-overlay/security-tutor/
├── backend/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── lessons/          # Lesson content
│   │   ├── labs/             # Interactive labs
│   │   ├── assessment/       # Skill assessment
│   │   └── api/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── hooks/           # Custom hooks
│   │   └── utils/
│   ├── public/
│   ├── package.json
│   └── tsconfig.json
├── content/                  # Educational content
│   ├── lessons/
│   ├── exercises/
│   └── solutions/
├── docker-compose.yml
└── README.md
```

### Testing Structure
```
tests/
├── unit/
│   ├── consciousness/
│   ├── context-engine/
│   ├── security/
│   └── services/
├── integration/
│   ├── api/
│   ├── message-bus/
│   └── workflows/
├── e2e/
│   ├── scenarios/
│   └── fixtures/
├── security/
│   ├── penetration/
│   ├── vulnerability/
│   └── compliance/
├── performance/
│   ├── load/
│   ├── stress/
│   └── benchmarks/
├── fixtures/                 # Test data
├── mocks/                   # Mock services
├── utils/                   # Test utilities
├── conftest.py             # Pytest configuration
└── Makefile
```

### Configuration Structure
```
config/
├── base/                    # Base configurations
│   ├── services.yaml
│   ├── security.yaml
│   └── logging.yaml
├── development/
│   ├── services.override.yaml
│   └── .env.example
├── staging/
│   ├── services.override.yaml
│   └── secrets.encrypted
├── production/
│   ├── services.override.yaml
│   └── secrets.encrypted
└── schemas/                # Configuration schemas
    └── config.schema.json
```

### Scripts Structure
```
scripts/
├── build/
│   ├── build-all.sh        # Build all components
│   ├── build-docker.sh     # Build Docker images
│   └── build-iso.sh        # Build ISO image
├── deploy/
│   ├── deploy-local.sh     # Local deployment
│   ├── deploy-staging.sh   # Staging deployment
│   └── deploy-prod.sh      # Production deployment
├── dev/
│   ├── setup-dev.sh        # Setup dev environment
│   ├── reset-db.sh         # Reset databases
│   └── generate-certs.sh   # Generate certificates
├── test/
│   ├── run-unit.sh         # Run unit tests
│   ├── run-integration.sh  # Run integration tests
│   └── run-security.sh     # Run security tests
└── utils/
    ├── check-deps.sh       # Check dependencies
    ├── lint-all.sh         # Run linters
    └── format-code.sh      # Format code
```

## File Naming Conventions

### General Rules
1. Use lowercase with underscores for Python files: `context_engine.py`
2. Use lowercase with hyphens for directories: `context-engine/`
3. Use PascalCase for Go files with types: `ServiceManager.go`
4. Use lowercase for Go files with functions: `handlers.go`
5. Use kebab-case for config files: `nats-cluster.conf`
6. Use UPPERCASE for documentation: `README.md`, `LICENSE`

### Component Naming
- Services: `service-name/`
- Tests: `test_component_name.py` or `component_test.go`
- Configs: `component.yaml` or `component.conf`
- Docker: `Dockerfile.component` or just `Dockerfile`

## Standard Files in Each Component

Every component directory should contain:
1. `README.md` - Component documentation
2. `Dockerfile` - Container definition
3. `Makefile` - Build commands
4. `.gitignore` - Git ignore rules
5. `LICENSE` - License file (if different from root)
6. `CHANGELOG.md` - Version history
7. `requirements.txt` or `go.mod` - Dependencies
8. `.env.example` - Environment variables example

## Development Workflow Files

### IDE Configuration
```
.vscode/
├── settings.json
├── launch.json
├── tasks.json
└── extensions.json

.idea/
└── # IntelliJ IDEA settings
```

### Git Configuration
```
.gitignore
.gitattributes
.gitmessage
.pre-commit-config.yaml
```

### CI/CD Files
```
.github/workflows/
├── ci.yml
├── cd.yml
├── security-scan.yml
└── release.yml

.gitlab-ci.yml
Jenkinsfile
```

## Security Files

```
security/
├── .trivyignore          # Trivy scanner ignore
├── .snyk                 # Snyk configuration
├── security-baseline.json # Security baseline
└── compliance/           # Compliance reports
```

This structure provides a solid foundation for the Syn_OS project, ensuring consistency, maintainability, and scalability across all components.