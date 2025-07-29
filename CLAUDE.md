# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Syn_OS is a complete rebuild of SynapticOS - a security-first consciousness-integrated operating system. The rebuild was necessitated by critical architectural flaws and security vulnerabilities in the legacy system.

**Current Status**: Foundation Development Phase - Repository contains architecture and documentation, with implementation beginning.

## Architecture

```
src/
├── security/           # Rust - Authentication, encryption, validation (PRIORITY 1)
├── consciousness/      # Python - AI decision engine and learning systems (PRIORITY 2)  
├── kernel/            # C/eBPF - System monitoring and security enforcement (PRIORITY 3)
└── frontend/          # TypeScript/Node.js - User interfaces and dashboards (PRIORITY 4)
```

## Why This Rebuild Exists

**CRITICAL**: Read `LESSONS_LEARNED.md` to understand the failures that led to this rebuild. Key issues in SynapticOS:

- **Security**: Hardcoded secrets, command injection, unsafe deserialization, CORS misconfig
- **Architecture**: 292 broad exception handlers, 5+ duplicate state managers, broken imports
- **Quality**: Syntax errors in tests, 20+ TODOs for core features, impossible deployment
- **Maintenance**: Tight coupling, no abstraction, massive code duplication

## Development Commands

Since this is a multi-language project, commands vary by component:

### Security Components (Rust)
```bash
cd src/security
cargo build                    # Build security modules
cargo test                     # Run unit tests  
cargo clippy                   # Lint and security checks
cargo audit                    # Dependency vulnerability scan
```

### Consciousness Components (Python)
```bash
cd src/consciousness
python -m pytest --cov=. --cov-report=html  # Run tests with coverage
python -m mypy .                             # Type checking
python -m ruff check .                       # Linting
python -m bandit -r .                        # Security scanning
```

### Kernel Components (C/eBPF)
```bash
cd src/kernel
make build                     # Build eBPF programs
make test                      # Test in VM environment
make verify                    # Verify eBPF programs
make install                   # Install kernel modules (requires root)
```

### Frontend Components (TypeScript)
```bash
cd src/frontend
npm install                    # Install dependencies
npm run build                  # Build for production
npm run dev                    # Development server
npm run test                   # Run test suite
npm run lint                   # ESLint checking
npm audit                      # Security audit
```

### Integration Testing
```bash
make test-integration          # Full system integration tests
make security-scan             # Complete security vulnerability scan
make performance-test          # Load testing and benchmarks
```

## Quality Requirements (NON-NEGOTIABLE)

Based on SynapticOS failures, these standards are MANDATORY:

### Security Requirements
- **NO hardcoded secrets** - Use environment variables or secure vaults
- **Input validation everywhere** - Validate and sanitize all external input
- **Safe serialization only** - JSON with schema validation, never pickle
- **Parameterized commands** - No shell injection vulnerabilities  
- **Zero high/critical vulnerabilities** in dependency scans

### Code Quality Requirements
- **>90% test coverage** for all modules
- **Specific exception handling** - No broad `except Exception` patterns
- **Type safety** - Full type hints in Python, strict TypeScript
- **Single responsibility** - One clear purpose per module/class
- **Performance targets** - <100ms response times for consciousness decisions

### Architecture Requirements
- **Dependency injection** - All dependencies injectable for testing
- **Layer isolation** - Clear boundaries between security/consciousness/kernel/frontend
- **Error propagation** - Proper error handling with recovery strategies
- **State management** - ACID properties, no data corruption
- **Resource management** - Proper cleanup, no memory leaks

## Development Workflow

### 1. Security-First Development
Every feature MUST start with security analysis:
- Threat modeling for new components
- Input validation strategy
- Authentication/authorization requirements
- Data encryption needs

### 2. Test-Driven Development
Write tests BEFORE implementation:
- Unit tests for business logic
- Integration tests for component interaction
- Security tests for attack scenarios
- Performance tests for scalability

### 3. Component Integration
When integrating with existing components:
- Check `src/consciousness/core/` for AI decision patterns
- Use `src/security/` modules for all authentication/encryption
- Follow `src/kernel/` patterns for system monitoring
- Implement proper error boundaries between layers

## Key Architectural Patterns

### Consciousness Engine Pattern
```python
# Proper consciousness decision making
from src.consciousness.core.engine import ConsciousnessEngine
from src.security.validation import validate_input

async def process_security_event(event_data: dict) -> SecurityAction:
    # ALWAYS validate input first (learned from SynapticOS)
    validated_event = validate_input(event_data, SecurityEventSchema)
    
    # Use consciousness engine for decision making
    decision = await consciousness_engine.analyze_threat(validated_event)
    
    # Return typed action (no generic exceptions)
    return SecurityAction.from_decision(decision)
```

### Secure Service Pattern
```rust
// Rust security component pattern
use crate::validation::ValidatedInput;
use crate::auth::SecureSession;

pub async fn secure_operation(
    session: SecureSession,
    input: ValidatedInput<OperationRequest>
) -> Result<OperationResponse, SecurityError> {
    // Security checks first
    session.validate_permissions(&input.operation_type)?;
    
    // Process with validated input
    let result = process_operation(input.inner()).await?;
    
    // Audit log the operation
    audit_log::record_operation(&session, &input, &result).await;
    
    Ok(result)
}
```

## Integration Points

### State Management
- Use `src/consciousness/state/` for consciousness state
- Use `src/security/state/` for security-related state  
- Never mix state management systems (learned from SynapticOS duplicates)

### Message Passing
- All inter-component communication goes through `src/consciousness/messaging/`
- Messages MUST be validated and typed
- No direct component-to-component calls

### Kernel Integration
- eBPF programs in `src/kernel/ebpf/` for monitoring
- Userspace bridge in `src/kernel/bridge/` for communication
- All kernel interactions logged and audited

## Security Enforcement

Based on critical SynapticOS vulnerabilities:

### Input Validation (MANDATORY)
```python
from pydantic import BaseModel, validator

class SecureInput(BaseModel):
    user_command: str
    
    @validator('user_command')
    def validate_command(cls, v):
        # Prevent command injection
        if any(char in v for char in ['|', '&', ';', '`', '$']):
            raise ValueError("Invalid characters in command")
        return sanitize_input(v)
```

### Secrets Management (MANDATORY)
```rust
// Never hardcode secrets - use environment or vault
let api_key = env::var("SYN_OS_API_KEY")?;
let encrypted_key = SecureString::from_env("SYN_OS_ENCRYPTION_KEY")?;
```

### Error Handling (MANDATORY)
```python
# Specific exception handling only
try:
    result = risky_operation()
except NetworkTimeoutError as e:
    logger.error(f"Network timeout: {e}")
    return ErrorResponse.network_timeout()
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    return ErrorResponse.invalid_input()
# Never catch Exception - let others propagate
```

## Performance Requirements

Consciousness decisions must be real-time:
- **Threat detection**: <10ms
- **Security response**: <50ms  
- **State updates**: <100ms
- **Dashboard updates**: <200ms

## Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │  Consciousness  │    │    Security     │
│  (TypeScript)   │◄──►│    (Python)     │◄──►│     (Rust)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                        ▲                        ▲
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Kernel Layer (eBPF/C)                       │
│              System Monitoring & Security Enforcement           │
└─────────────────────────────────────────────────────────────────┘
```

## Common Mistakes to Avoid

Based on SynapticOS audit findings:

1. **NO sys.path manipulation** - Use proper Python packaging
2. **NO duplicate implementations** - Single source of truth for each capability
3. **NO broad exception handling** - Catch specific exceptions only
4. **NO hardcoded paths** - Use configuration and environment variables
5. **NO unsafe deserialization** - JSON with validation only
6. **NO unvalidated user input** - Validate everything at boundaries
7. **NO mixing async/sync patterns** - Choose one paradigm per component

## Testing Strategy

### Unit Tests
- Every public function has tests
- Edge cases and error conditions covered
- Mocked dependencies for isolation

### Integration Tests  
- Component interaction testing
- Message passing validation
- State consistency verification

### Security Tests
- Input validation bypass attempts
- Authentication/authorization testing
- Privilege escalation detection

### Performance Tests
- Load testing under realistic conditions
- Memory usage and leak detection
- Response time validation

## Getting Help

- Security questions: Tag issues with `security` label
- Architecture questions: Reference this file and `LESSONS_LEARNED.md`
- Performance issues: Tag with `performance` label
- Integration problems: Check component interfaces in `src/*/interfaces/`

Remember: **Security and quality are non-negotiable.** Every decision should be evaluated against the failures documented in `LESSONS_LEARNED.md`.