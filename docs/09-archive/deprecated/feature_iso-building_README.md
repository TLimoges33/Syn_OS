# feature/iso-building

## Overview

ISO building and distribution system

**Lead Team:** Build Team  
**Priority:** CRITICAL  
**Created:** 2025-08-26 12:11:18

## Focus Areas

- build/
- scripts/build/
- iso/

## Development Guidelines

### Code Standards
- Follow established error handling patterns in `src/error_handling/`
- Use structured logging with JSON format
- Implement comprehensive test coverage (>95%)
- Follow architectural patterns established in main branch

### Testing Requirements
- Run full test suite: `python3 tests/run_tests.py`
- Add unit tests for new functionality
- Include integration tests for complex features
- Test edge cases and failure scenarios

### Documentation Requirements
- Update relevant documentation in `docs/`
- Add inline code comments for complex logic
- Create user-facing documentation for new features
- Update API documentation if applicable

### Commit Guidelines
- Use structured commit messages (emoji prefixes encouraged)
- Reference issues/PRs in commit messages
- Keep commits focused and atomic
- Include tests and documentation in commits

## Getting Started

1. **Switch to this branch:**
   ```bash
   git checkout feature/iso-building
   ```

2. **Install dependencies:**
   ```bash
   make install  # or equivalent setup
   ```

3. **Run tests:**
   ```bash
   python3 tests/run_tests.py --category all
   ```

4. **Start development:**
   - Focus on areas listed above
   - Follow development guidelines
   - Submit PRs for review

## Resources

- **Main Documentation:** [docs/](../docs/)
- **Development Workflow:** [docs/workflows/DEV_TEAM_WORKFLOW.md](../docs/workflows/DEV_TEAM_WORKFLOW.md)
- **Technical Specifications:** [docs/specifications/](../docs/specifications/)
- **Testing Framework:** [tests/README.md](../tests/README.md)

## Status

- **Current Status:** ACTIVE
- **Last Updated:** 2025-08-26 12:11:18
- **Next Milestone:** TBD

---

**Ready for Build Team Development! 🚀**
