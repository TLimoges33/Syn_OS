# SynOS Build Safety Requirements

**Document Version:** 1.0
**Created:** September 15, 2025
**In Response To:** PERM-CORRUPT-2025-09-15 Incident

## Overview

This document establishes mandatory safety requirements for all SynOS build scripts to prevent system-wide permission corruption incidents.

## Mandatory Requirements

### 1. Safety Framework Integration

**ALL build scripts MUST:**
```bash
# Source the safety framework
source "$SYNOS_PROJECT_ROOT/scripts/build-safety-framework.sh"

# Validate environment before any operations
validate_build_environment
```

### 2. Forbidden Operations

The following operations are **STRICTLY FORBIDDEN** in all build scripts:

```bash
# NEVER USE THESE:
sudo chown -R $(whoami):$(whoami) "$VARIABLE"  # Variables can be unset
sudo chown -R user:group /                     # System root
sudo chown -R user:group /usr                  # System directories
sudo chmod -R 777 .                            # Overly permissive
sudo chmod -R 755 /usr                         # System modifications
```

### 3. Required Safe Alternatives

Instead of dangerous operations, use these safe functions:

```bash
# For ownership changes
safe_chown "$BUILD_DIR" "$(whoami):$(whoami)"

# For permission changes
safe_chmod "$SCRIPT_PATH" "755" false          # Single file
safe_chmod "$BUILD_DIR" "755" true             # Recursive
```

### 4. Environment Variable Validation

All scripts MUST validate critical variables:

```bash
# Check BUILD_DIR is set and safe
if [[ -z "$BUILD_DIR" ]] || [[ ! "$BUILD_DIR" =~ ^/home/diablorain/Syn_OS ]]; then
    echo "ERROR: BUILD_DIR not set or unsafe"
    exit 1
fi

# Always use absolute paths
BUILD_DIR=$(realpath "$BUILD_DIR")
```

### 5. Pre-commit Hooks

Git hooks are automatically installed to prevent dangerous commits:
- Scans all `.sh` files for forbidden patterns
- Blocks commits containing `chown -R` or `chmod -R`
- Provides guidance on safe alternatives

## Setup Instructions

### Initial Setup
```bash
# Initialize safety framework
cd /home/diablorain/Syn_OS
./scripts/build-safety-framework.sh init
```

### Script Verification
```bash
# Scan existing scripts for dangerous patterns
./scripts/build-safety-framework.sh scan
```

### Environment Validation
```bash
# Validate current build environment
./scripts/build-safety-framework.sh validate
```

## Testing Requirements

### Dry-Run Mode
All scripts MUST support dry-run mode:
```bash
# Enable dry-run for testing
export DRY_RUN=true
./your-build-script.sh
```

### Path Validation Testing
Test with invalid paths to ensure proper rejection:
```bash
export BUILD_DIR="/usr"  # Should fail
export BUILD_DIR=""      # Should fail
export BUILD_DIR="/home/diablorain/Syn_OS/build"  # Should pass
```

## Script Template

Use this template for all new build scripts:

```bash
#!/bin/bash
set -euo pipefail

# SynOS Build Script Template - SAFETY COMPLIANT
# Created: $(date)
# Purpose: [DESCRIBE PURPOSE]

# === SAFETY FRAMEWORK INTEGRATION ===
SYNOS_PROJECT_ROOT="/home/diablorain/Syn_OS"
if [[ -f "$SYNOS_PROJECT_ROOT/scripts/build-safety-framework.sh" ]]; then
    source "$SYNOS_PROJECT_ROOT/scripts/build-safety-framework.sh"
    validate_build_environment
else
    echo "ERROR: Safety framework not found"
    exit 1
fi

# === SCRIPT CONFIGURATION ===
BUILD_DIR="${BUILD_DIR:-$SYNOS_PROJECT_ROOT/build/$(basename $0 .sh)}"
WORK_DIR="${WORK_DIR:-$SYNOS_PROJECT_ROOT}"

# Validate configuration
if [[ -z "$BUILD_DIR" ]] || [[ ! "$BUILD_DIR" =~ ^$SYNOS_PROJECT_ROOT ]]; then
    log_error "Invalid BUILD_DIR: $BUILD_DIR"
    exit 1
fi

# === MAIN SCRIPT LOGIC ===
log_info "Starting build process..."

# Use safe operations only
safe_chown "$BUILD_DIR" "$(whoami):$(whoami)"
safe_chmod "$BUILD_DIR" "755" true

log_success "Build completed successfully"
```

## Compliance Verification

### Required Checks Before Script Execution
1. Safety framework sourced ✓
2. Environment validated ✓
3. No forbidden patterns ✓
4. Dry-run tested ✓

### Automated Verification
The pre-commit hook automatically verifies:
- No `chown -R` without safety wrapper
- No `chmod -R` without safety wrapper
- No operations on system directories
- Proper variable validation

## Incident Response

If a permission corruption incident occurs:

1. **STOP** all build operations immediately
2. Document the incident using template in `/documentation/incidents/`
3. Follow recovery procedures from incident report
4. Update safety framework if new vulnerability discovered
5. Test all scripts before resuming operations

## Exemptions

In exceptional cases where raw `chown -R` is required:
1. Document the business justification
2. Get approval from project owner
3. Use `# SAFETY-EXEMPTION: [REASON]` comment
4. Implement additional safeguards
5. Test extensively in isolated environment

## Training Requirements

All developers working on build scripts MUST:
1. Read this document completely
2. Understand the PERM-CORRUPT-2025-09-15 incident
3. Practice using safety framework functions
4. Test scripts with dry-run mode
5. Verify pre-commit hooks are working

## Violations and Enforcement

### Automatic Enforcement
- Pre-commit hooks block dangerous patterns
- Safety framework validates at runtime
- CI/CD pipelines check for compliance

### Manual Review Required
- All build script changes reviewed
- Exemption requests scrutinized
- Regular audits of existing scripts

### Violation Response
1. **Minor**: Education and script correction
2. **Major**: Script disabled until fixed
3. **Critical**: Full incident response procedure

---

**Remember:** The goal is **ZERO TOLERANCE** for system permission corruption. When in doubt, ask for help rather than risk another incident.

**Contact**: diablorain (System Owner)
**Documentation**: `/home/diablorain/Syn_OS/documentation/incidents/`
**Safety Framework**: `/home/diablorain/Syn_OS/scripts/build-safety-framework.sh`