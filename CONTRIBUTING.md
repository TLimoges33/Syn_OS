# Contributing to SynOS

First off, thank you for considering contributing to SynOS! 🎉

SynOS is an ambitious project combining AI, cybersecurity, and Linux distribution development. We welcome contributions from developers, security researchers, designers, and documentation writers.

## 🤝 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the [existing issues](https://github.com/TLimoges33/Syn_OS/issues) to avoid duplicates.

**When filing a bug report, include:**

-   SynOS version
-   Steps to reproduce
-   Expected vs actual behavior
-   Error messages/logs
-   System specs (if relevant)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues.

**Include in your suggestion:**

-   Clear description of the feature
-   Why this would be useful
-   Possible implementation approach
-   Screenshots/mockups (if UI related)

### Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Make your changes** following our code style
3. **Test thoroughly** - ensure nothing breaks
4. **Update documentation** - if you changed APIs or added features
5. **Submit a PR** with a clear description

## 📝 Development Guidelines

### Code Style

**Rust Code:**

```rust
// Use rustfmt
cargo fmt

// Use clippy
cargo clippy -- -D warnings

// Follow Rust conventions
// - snake_case for functions/variables
// - CamelCase for types
// - SCREAMING_SNAKE_CASE for constants
```

**Shell Scripts:**

```bash
#!/bin/bash
# Use shellcheck
shellcheck script.sh

# Follow conventions:
# - Use ${VAR} not $VAR
# - Quote variables: "${VAR}"
# - Check errors: || { echo "error"; exit 1; }
```

**Python Code:**

```python
# Follow PEP 8
# Use black formatter
black *.py

# Use type hints
def function(param: str) -> int:
    pass
```

### Commit Messages

Follow conventional commits:

```
feat: Add new security tool integration
fix: Resolve boot sequence bug
docs: Update installation guide
style: Format code with rustfmt
refactor: Restructure AI engine modules
test: Add unit tests for neural network
chore: Update dependencies
```

**Format:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Examples:**

-   `feat(ai-engine): Implement pattern recognition cache`
-   `fix(boot): Correct Plymouth theme path`
-   `docs(readme): Add screenshot section`

### Branch Naming

-   `feature/short-description` - New features
-   `fix/issue-number-description` - Bug fixes
-   `docs/what-changed` - Documentation
-   `refactor/component-name` - Code refactoring

### Testing

**Before submitting PR:**

```bash
# Build successfully
cargo build --workspace

# Run tests
cargo test --workspace

# Build ISO (if changing build system)
sudo ./scripts/02-build/core/build-synos-ultimate-iso.sh

# Test in VM
qemu-system-x86_64 -cdrom build/synos-ultimate.iso -m 4096
```

## 🏗️ Project Structure

```
Syn_OS/
├── src/              # Rust source code (kernel, AI, security)
├── core/             # Framework libraries
├── scripts/          # Build and utility scripts
├── assets/           # Branding, themes, icons
├── docs/             # Documentation
├── tests/            # Test suites
└── linux-distribution/  # Live-build workspace
```

**Key areas for contribution:**

-   `src/ai-engine/` - AI consciousness system
-   `src/kernel/` - Custom Rust kernel
-   `src/security/` - Security framework
-   `assets/themes/` - UI/UX themes
-   `docs/` - Documentation

## 📚 Documentation Standards

**All user-facing features need documentation:**

-   README.md updates (if public-facing)
-   docs/02-user-guide/ for user features
-   docs/04-development/ for developer features
-   Inline code comments for complex logic
-   CLAUDE.md updates for AI agent context

**Documentation format:**

-   Use Markdown
-   Include code examples
-   Add screenshots (for UI)
-   Link related docs

## 🎨 Design Contributions

**Brand Guidelines:**

-   Follow red/black color scheme
-   Use phoenix logo variants appropriately
-   Maintain cyberpunk aesthetic
-   See [REVOLUTION_2025_BRAND_GUIDE.md](assets/branding/REVOLUTION_2025_BRAND_GUIDE.md)

**Asset Guidelines:**

-   PNG for raster images
-   SVG for vectors
-   High resolution (512px+ for logos)
-   Proper naming (phoenix-512.png)

## 🔒 Security Contributions

**Reporting Security Vulnerabilities:**

⚠️ **DO NOT** create public issues for security vulnerabilities.

Instead:

1. Email: mogeem33@gmail.com (Subject: SECURITY - SynOS Vulnerability)
2. Provide detailed report
3. Wait for response (48-72 hours)
4. Work with maintainers on fix

See [SECURITY.md](docs/08-security/SECURITY.md) for details.

**Security Tool Additions:**

-   Ensure tool is legal & ethical
-   Document usage
-   Add to appropriate category
-   Include educational notes

## 🤖 AI/ML Contributions

**Neural Network Enhancements:**

-   Document model architecture
-   Include training data requirements
-   Provide performance benchmarks
-   Ensure privacy compliance

**AI Features:**

-   Must have educational value
-   Should enhance security workflows
-   Needs clear user documentation
-   Requires testing with sample data

## 📦 Adding Security Tools

**Process:**

1. **Research** - Ensure tool is reputable
2. **Legal Check** - Verify licensing
3. **Integration** - Add to build script
4. **Documentation** - Create tool guide
5. **Testing** - Verify functionality

**Example:**

```bash
# In scripts/02-build/core/build-synos-ultimate-iso.sh
# Add to install_security_tools() function

chroot "${CHROOT_DIR}" apt install -y newtool
echo "✓ New tool installed"
```

## 👥 Community

-   **Discord:** (Coming soon)
-   **Matrix:** (Coming soon)
-   **Mailing List:** (Coming soon)

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment.

### Our Standards

**✅ Do:**

-   Be respectful and inclusive
-   Accept constructive criticism
-   Focus on what's best for the community
-   Show empathy towards others

**❌ Don't:**

-   Use inappropriate language
-   Harass or insult
-   Troll or make political attacks
-   Publish others' private information

### Enforcement

Violations can be reported to: mogeem33@gmail.com (Subject: Code of Conduct Violation)

Maintainers will review and take appropriate action.

## ❓ Questions?

-   Check [documentation](docs/README.md)
-   Search [existing issues](https://github.com/TLimoges33/Syn_OS/issues)
-   Ask on community channels
-   Email: mogeem33@gmail.com

## 🎯 Good First Issues

Look for issues tagged:

-   `good first issue` - Easy for newcomers
-   `help wanted` - Community input needed
-   `documentation` - Docs improvements
-   `enhancement` - New features

## 📈 Development Roadmap

See [ROADMAP.md](docs/05-planning/ROADMAP.md) for planned features.

Want to work on something not listed? Create an issue to discuss!

## 🙏 Thank You!

Every contribution makes SynOS better. Whether it's code, docs, design, or ideas - we appreciate your time and effort!

**🔴 Together we build the future of cybersecurity. 🔴**

---

_Last Updated: October 12, 2025_
_Maintained by the SynOS Core Team_
