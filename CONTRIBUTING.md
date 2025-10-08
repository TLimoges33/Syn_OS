# Contributing to SynOS

Thank you for your interest in contributing to SynOS! This document provides guidelines and instructions for contributing to the project.

## 🎯 Ways to Contribute

-   🐛 **Bug Reports**: Help us identify and fix issues
-   ✨ **Feature Requests**: Suggest new capabilities
-   📝 **Documentation**: Improve guides and API docs
-   🔧 **Code Contributions**: Submit bug fixes and features
-   🔒 **Security Research**: Responsible disclosure of vulnerabilities
-   🧪 **Testing**: Validate functionality and report issues
-   🌍 **Community Support**: Help other users

---

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

```bash
# Required
- Rust 1.85.0 or later
- Python 3.9+
- Docker and Docker Compose
- Git

# Optional (for kernel work)
- LLVM/Clang
- Cross-compilation toolchain
- QEMU for testing
```

### Development Setup

1. **Fork the repository** on GitHub

2. **Clone your fork**:

    ```bash
    git clone https://github.com/YOUR_USERNAME/Syn_OS.git
    cd Syn_OS
    ```

3. **Add upstream remote**:

    ```bash
    git remote add upstream https://github.com/TLimoges33/Syn_OS.git
    ```

4. **Install dependencies**:

    ```bash
    # Python dependencies
    pip install -r development/requirements.txt

    # Rust toolchain
    rustup target add x86_64-unknown-none

    # Development containers
    docker-compose -f docker/docker-compose.yml up -d
    ```

5. **Verify setup**:

    ```bash
    # Check Rust compilation
    cargo build --manifest-path=src/kernel/Cargo.toml --target=x86_64-unknown-none
    cargo build --manifest-path=core/security/Cargo.toml

    # Run tests
    make test
    ```

---

## 📋 Contribution Workflow

### 1. Create an Issue First

Before starting work:

-   Check if an issue already exists
-   If not, create one describing your proposed change
-   Wait for maintainer feedback/approval
-   This prevents duplicate work and ensures alignment

### 2. Create a Feature Branch

```bash
# Update your fork
git fetch upstream
git checkout master
git merge upstream/master

# Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 3. Make Your Changes

Follow our coding standards (see below) and:

-   Write clear, self-documenting code
-   Add tests for new functionality
-   Update documentation as needed
-   Keep commits atomic and focused

### 4. Test Your Changes

```bash
# Run relevant tests
cargo test --manifest-path=src/kernel/Cargo.toml
cargo test --workspace

# Check for warnings
cargo clippy --all-targets --all-features

# Format code
cargo fmt --all

# Run security audit (if applicable)
python3 scripts/a_plus_security_audit.py
```

### 5. Commit Your Changes

Follow our commit message format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:

-   `feat`: New feature
-   `fix`: Bug fix
-   `docs`: Documentation changes
-   `style`: Code style changes (formatting, no logic change)
-   `refactor`: Code refactoring
-   `test`: Test additions or changes
-   `chore`: Build process, tooling, dependencies

**Examples**:

```bash
git commit -m "feat(ai-daemon): add pattern recognition caching"
git commit -m "fix(kernel): resolve scheduler mutex deadlock"
git commit -m "docs(api): add REST API examples for consciousness service"
```

### 6. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create PR on GitHub
# Use the PR template (auto-populated)
```

---

## 💻 Coding Standards

### Rust Code Style

We follow standard Rust conventions:

````rust
// Use descriptive names
fn process_security_event(event: SecurityEvent) -> Result<(), Error> {
    // Document complex logic
    // TODO: Add event filtering

    // Handle errors explicitly
    let validated = validate_event(&event)
        .map_err(|e| Error::ValidationFailed(e))?;

    // Use pattern matching
    match validated.severity {
        Severity::Critical => handle_critical(validated),
        Severity::High => handle_high(validated),
        _ => handle_standard(validated),
    }
}

// Document public APIs
/// Processes incoming security events and routes them to appropriate handlers.
///
/// # Arguments
/// * `event` - The security event to process
///
/// # Returns
/// * `Ok(())` on success
/// * `Err(Error)` if processing fails
///
/// # Examples
/// ```
/// let event = SecurityEvent::new(Severity::High, "unauthorized_access");
/// process_security_event(event)?;
/// ```
pub fn process_security_event(event: SecurityEvent) -> Result<(), Error> {
    // Implementation
}
````

**Key Points**:

-   Use `rustfmt` for automatic formatting
-   Use `clippy` for linting (`cargo clippy`)
-   Avoid `unwrap()` in production code (use proper error handling)
-   Document public APIs with doc comments
-   Prefer explicit types over type inference in public APIs
-   Use `Result<T, E>` for fallible operations

### Python Code Style

Follow PEP 8:

```python
"""Module for AI consciousness pattern recognition.

This module implements the neural darwinism pattern learning system.
"""

from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class PatternRecognizer:
    """Recognizes and learns patterns in security events."""

    def __init__(self, confidence_threshold: float = 0.8):
        """Initialize pattern recognizer.

        Args:
            confidence_threshold: Minimum confidence for pattern matching (0.0-1.0)
        """
        self.threshold = confidence_threshold
        self.patterns: Dict[str, Pattern] = {}

    def recognize(self, data: List[Event]) -> Optional[Pattern]:
        """Recognize patterns in event data.

        Args:
            data: List of security events to analyze

        Returns:
            Recognized pattern if confidence > threshold, None otherwise
        """
        # Implementation
        pass
```

**Key Points**:

-   Use type hints
-   Follow PEP 8 naming conventions
-   Document modules, classes, and functions
-   Use logging instead of print statements
-   Keep functions focused and testable

### C/C++ Code Style (Kernel)

For kernel components:

```c
/**
 * @brief Initialize the AI hardware abstraction layer
 *
 * @param config Hardware configuration parameters
 * @return 0 on success, negative error code on failure
 */
int ai_hal_init(const struct ai_config *config) {
    if (!config) {
        return -EINVAL;
    }

    // Implementation
    return 0;
}
```

---

## 🧪 Testing Requirements

### For All Contributions

-   Add tests for new functionality
-   Ensure existing tests pass
-   Aim for >80% code coverage for new code

### Running Tests

```bash
# All tests
make test

# Kernel tests
cargo test --manifest-path=src/kernel/Cargo.toml

# Service tests
cargo test --workspace

# Python tests
pytest tests/

# Integration tests
python3 -m pytest tests/integration/
```

### Writing Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pattern_recognition() {
        let recognizer = PatternRecognizer::new(0.8);
        let events = vec![/* test events */];

        let result = recognizer.recognize(&events);

        assert!(result.is_some());
        assert!(result.unwrap().confidence > 0.8);
    }
}
```

---

## 📝 Documentation Standards

### Code Documentation

-   Document all public APIs
-   Include examples in doc comments
-   Explain complex algorithms
-   Document safety considerations

### README Files

-   Each major component should have a README
-   Include: purpose, usage, examples, configuration
-   Keep them up-to-date with code changes

### Wiki/User Documentation

-   Write for the target audience (beginners to advanced)
-   Include screenshots and examples
-   Test instructions before committing

---

## 🔒 Security Contributions

### Reporting Vulnerabilities

**DO NOT** report security issues publicly. See [SECURITY.md](./SECURITY.md) for responsible disclosure.

### Security Code Reviews

When contributing security-critical code:

-   Document threat model considerations
-   Explain security assumptions
-   Include security tests
-   Highlight crypto or auth changes

---

## 📦 Pull Request Guidelines

### PR Requirements

✅ **Must Have**:

-   Descriptive title and description
-   Reference related issue(s)
-   Pass all CI checks
-   Include tests
-   Update documentation
-   Follow coding standards

❌ **Avoid**:

-   Mixing unrelated changes
-   Breaking existing functionality
-   Submitting untested code
-   Large PRs (>500 lines if possible)

### PR Template

When creating a PR, include:

```markdown
## Description

Brief description of changes

## Related Issue

Fixes #123

## Type of Change

-   [ ] Bug fix
-   [ ] New feature
-   [ ] Breaking change
-   [ ] Documentation update

## Testing

Describe testing performed

## Checklist

-   [ ] Code follows style guidelines
-   [ ] Self-review completed
-   [ ] Documentation updated
-   [ ] Tests added/updated
-   [ ] All tests pass
-   [ ] No new warnings
```

---

## 🔄 Review Process

1. **Automated Checks**: CI/CD runs tests and linters
2. **Code Review**: Maintainers review your code
3. **Feedback**: Address review comments
4. **Approval**: Maintainer approves PR
5. **Merge**: PR is merged to master

### Review Timeline

-   Initial review: 2-5 business days
-   Follow-up reviews: 1-3 business days
-   Critical fixes: Prioritized for same-day review

---

## 🏗️ Project Structure

Understanding the layout:

```
Syn_OS/
├── src/
│   ├── kernel/          # Custom kernel modules (Rust)
│   ├── ai-daemon/       # AI orchestration service
│   └── services/        # All 5 AI services
├── core/
│   ├── kernel/          # C/C++ kernel implementation
│   ├── security/        # Security frameworks
│   └── libraries/       # Shared libraries
├── scripts/             # Build and automation scripts
├── tests/               # Test suites
├── docs/                # All documentation
└── config/              # Configuration files
```

---

## 🐛 Bug Report Guidelines

When reporting bugs, include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: Exact steps to trigger bug
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: OS, version, hardware
6. **Logs**: Relevant log files or error messages

---

## ✨ Feature Request Guidelines

When requesting features:

1. **Use Case**: Why is this needed?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Other approaches considered?
4. **Impact**: Who benefits from this?

---

## 📞 Getting Help

-   💬 **Discussions**: GitHub Discussions for questions
-   📧 **Email**: For sensitive topics
-   📚 **Documentation**: Check docs/ first
-   🐛 **Issues**: For bug reports only

---

## 📜 Code of Conduct

Be respectful, inclusive, and professional. We're all here to build something great together.

-   Use welcoming and inclusive language
-   Respect differing viewpoints
-   Accept constructive criticism gracefully
-   Focus on what's best for the community
-   Show empathy towards others

---

## ⚖️ License

By contributing, you agree that your contributions will be licensed under the same license as the project (see [LICENSE](./LICENSE)).

You must have the right to contribute the code you submit. Do not submit copyrighted code without permission.

---

## 🙏 Recognition

Contributors are recognized in:

-   CHANGELOG.md for each release
-   GitHub contributors page
-   Security Hall of Fame (for security researchers)

---

## 📅 Release Cycle

-   **Patch releases** (1.0.x): Monthly or as needed for critical fixes
-   **Minor releases** (1.x.0): Quarterly with new features
-   **Major releases** (x.0.0): Annually with breaking changes

---

**Thank you for contributing to SynOS! Together we're building the future of AI-enhanced cybersecurity. 🚀**

For questions about contributing, open a Discussion on GitHub or contact the maintainers.
