# 🔄 Build Script Consolidation Plan

## Reducing from 62 to 10 Core Scripts

**Date:** October 23, 2025  
**Status:** 🚧 IN PROGRESS  
**Goal:** Consolidate 62 build scripts into 10 maintainable core scripts

---

## 📊 Current State Analysis

### Statistics:

-   **Total build scripts:** 62
-   **Duplicated functionality:** ~75%
-   **Primary script:** unified-iso-builder.sh (excellent quality)
-   **Legacy scripts:** 10+ in archived directories
-   **Specialized scripts:** 15+ with overlapping features

### Problems:

1. **High duplication** - Same functionality implemented 5-10 times
2. **Inconsistent patterns** - Different error handling, logging styles
3. **Maintenance burden** - Changes need to be replicated across scripts
4. **User confusion** - Hard to know which script to use
5. **No shared library** - Common code duplicated everywhere

---

## 🎯 Target Architecture

### Core Scripts (10 total):

```
scripts/
├── lib/
│   └── build-common.sh          ✅ CREATED - Shared functions library
│
├── build-iso.sh                 🔄 TO CREATE - Primary ISO builder (replaces unified-iso-builder.sh)
├── build-kernel-only.sh         🔄 TO CREATE - Quick kernel-only ISO
├── build-full-linux.sh          🔄 TO CREATE - Complete Linux distribution
│
├── docker/
│   └── build-docker.sh          📋 PLANNED - Docker-based builds
│
├── testing/
│   ├── test-iso.sh              📋 PLANNED - ISO testing automation
│   └── verify-build.sh          📋 PLANNED - Pre-build verification
│
├── maintenance/
│   ├── clean-builds.sh          📋 PLANNED - Clean build artifacts
│   └── archive-old-isos.sh      📋 PLANNED - Archive management
│
└── utilities/
    ├── sign-iso.sh              📋 PLANNED - ISO signing
    └── create-checksums.sh      📋 PLANNED - Checksum generation
```

---

## 📂 Script Consolidation Mapping

### Phase 1: Create Common Library ✅ COMPLETE

**Created:** `scripts/lib/build-common.sh`

**Functions provided:**

-   Logging (log, success, error, warning, info, section)
-   Environment setup (init_build_env)
-   Dependency checking (check_not_root, check_required_tools, check_disk_space)
-   Rust builds (build_kernel, find_kernel_binary, build_workspace, collect_binaries)
-   GRUB configuration (create_grub_config)
-   ISO generation (generate_iso, generate_checksums)
-   File operations (copy_documentation, create_source_archive)
-   Cleanup (setup_cleanup, cleanup_handler)
-   Validation (verify_iso)
-   Utilities (print_banner, human_size, elapsed_time)

---

### Phase 2: Consolidate Primary Builders 🔄 IN PROGRESS

#### 1. build-iso.sh (Primary Builder)

**Consolidates:**

-   `scripts/unified-iso-builder.sh` ⭐ Primary
-   `deployment/infrastructure/build-system/build_synos_iso.sh`
-   `deployment/infrastructure/build-system/build-syn-iso.sh`
-   `deployment/infrastructure/build-system/build-production-iso.sh`
-   `deployment/operations/admin/build-iso.sh`

**Purpose:** Complete bootable ISO with all features

**Features:**

-   Uses build-common.sh library
-   Rust kernel + workspace binaries
-   Documentation + optional source
-   GRUB bootloader (4 modes)
-   Checksums (MD5, SHA256)
-   Configurable via environment variables

**Build Time:** 10-15 minutes  
**Output:** 1-2GB ISO

---

#### 2. build-kernel-only.sh (Quick Test Builder)

**Consolidates:**

-   `scripts/02-build/core/build-simple-kernel-iso.sh`
-   `deployment/infrastructure/build-system/build-simple-kernel-iso.sh`
-   `scripts/02-build/build-bootable-kernel.sh`

**Purpose:** Minimal kernel-only ISO for quick testing

**Features:**

-   Kernel compilation only
-   Minimal GRUB config
-   Fast build (<5 minutes)
-   Small ISO (200MB)

**Build Time:** 5 minutes  
**Output:** 200MB ISO

---

#### 3. build-full-linux.sh (Complete Distribution)

**Consolidates:**

-   `scripts/02-build/variants/build-synos-minimal-iso.sh`
-   `linux-distribution/SynOS-Linux-Builder/scripts/build-complete-synos-iso.sh`
-   `scripts/02-build/core/archived-legacy-scripts/build-synos-linux.sh`

**Purpose:** Full Debian-based Linux distribution

**Features:**

-   Debootstrap Debian base
-   XFCE4 desktop
-   Complete SynOS source
-   Development tools
-   Network tools

**Build Time:** 30-60 minutes  
**Output:** 4-8GB ISO

---

### Phase 3: Specialized Tools 📋 PLANNED

#### 4. docker/build-docker.sh

**Consolidates:**

-   `deployment/operations/admin/build-master-iso-v1.0.sh`
-   `deployment/docker/strategies/scripts/build-synos-kernel.sh`

**Purpose:** Reproducible Docker-based builds

---

#### 5. testing/test-iso.sh

**New functionality** - currently missing

**Purpose:** Automated ISO testing

-   QEMU boot test
-   Verify GRUB menu
-   Check kernel loads
-   Test all boot modes

---

#### 6. testing/verify-build.sh

**Consolidates:**

-   `scripts/02-build/auditing/verify-build-ready.sh`
-   `scripts/02-build/auditing/verify-pre-build.sh`

**Purpose:** Pre-build verification and readiness checks

---

#### 7. maintenance/clean-builds.sh

**New functionality** - currently scattered

**Purpose:** Clean build artifacts

-   Remove old build/ contents
-   Clean cargo cache
-   Archive old ISOs
-   Preserve specific builds

---

#### 8. maintenance/archive-old-isos.sh

**New functionality** - manual process now

**Purpose:** Archive management

-   Move old ISOs to archive/
-   Compress if needed
-   Maintain inventory
-   Delete ancient builds

---

#### 9. utilities/sign-iso.sh

**Consolidates:**

-   `deployment/operations/admin/build-signing.sh`
-   `src/security/tools/security/build-signing.sh`

**Purpose:** Digital signing

-   GPG signatures
-   Certificate signing
-   Verification

---

#### 10. utilities/create-checksums.sh

**New functionality** - extracted from builders

**Purpose:** Checksum generation

-   MD5, SHA256, SHA512
-   Manifest creation
-   Verification script generation

---

## 📋 Implementation Phases

### Phase 1: Foundation ✅ COMPLETE

-   [x] Create `scripts/lib/build-common.sh`
-   [x] Implement core functions
-   [x] Test library loading
-   [x] Document usage

### Phase 2: Core Builders 🔄 IN PROGRESS

-   [ ] Create `scripts/build-iso.sh` (refactor unified-iso-builder.sh)
-   [ ] Create `scripts/build-kernel-only.sh`
-   [ ] Create `scripts/build-full-linux.sh`
-   [ ] Test all three builders
-   [ ] Update documentation

### Phase 3: Testing Tools 📋 PLANNED

-   [ ] Create `scripts/testing/test-iso.sh`
-   [ ] Create `scripts/testing/verify-build.sh`
-   [ ] Add QEMU automation
-   [ ] Add smoke tests

### Phase 4: Maintenance Tools 📋 PLANNED

-   [ ] Create `scripts/maintenance/clean-builds.sh`
-   [ ] Create `scripts/maintenance/archive-old-isos.sh`
-   [ ] Add inventory tracking
-   [ ] Add metrics collection

### Phase 5: Specialized Tools 📋 PLANNED

-   [ ] Create `scripts/docker/build-docker.sh`
-   [ ] Create `scripts/utilities/sign-iso.sh`
-   [ ] Create `scripts/utilities/create-checksums.sh`
-   [ ] Add CI/CD integration

### Phase 6: Migration & Cleanup 📋 PLANNED

-   [ ] Update all documentation to use new scripts
-   [ ] Create migration guide
-   [ ] Archive all legacy scripts to `archive/build-scripts-deprecated/`
-   [ ] Update Makefile targets
-   [ ] Add deprecation warnings to old scripts

---

## 🔧 Migration Strategy

### For Users:

**Old Command:**

```bash
./scripts/unified-iso-builder.sh
```

**New Command:**

```bash
./scripts/build-iso.sh
```

**Backward Compatibility:**

-   Keep `unified-iso-builder.sh` as wrapper that calls `build-iso.sh`
-   Add deprecation warning
-   Remove after 30-day grace period

### For Developers:

**Old Pattern:**

```bash
# Duplicated code in every script
log() { echo -e "\033[0;36m[$(date)]$*\033[0m"; }
# ... 50 more lines of duplicated functions
```

**New Pattern:**

```bash
# Source common library
source "$(dirname "$0")/lib/build-common.sh"
init_build_env

# Use library functions
log "Starting build..."
build_kernel "x86_64-unknown-none"
```

---

## 📊 Expected Improvements

### Metrics:

| Metric                   | Before  | After  | Improvement    |
| ------------------------ | ------- | ------ | -------------- |
| **Total build scripts**  | 62      | 10     | 84% reduction  |
| **Lines of code**        | ~15,000 | ~3,000 | 80% reduction  |
| **Duplicated functions** | 75%     | 0%     | 100% reduction |
| **Maintenance burden**   | High    | Low    | 70% reduction  |
| **User confusion**       | High    | Low    | 80% reduction  |

### Benefits:

1. **Easier Maintenance**

    - Bug fixes in one place
    - Consistent behavior
    - Easier to test

2. **Better Documentation**

    - Clear script purposes
    - Consistent usage patterns
    - Better examples

3. **Improved Quality**

    - Standardized error handling
    - Consistent logging
    - Better validation

4. **Faster Development**
    - Reusable components
    - Less code duplication
    - Easier to add features

---

## 🎯 Success Criteria

### Phase 2 Complete When:

-   [ ] 3 core builders created and tested
-   [ ] All use build-common.sh library
-   [ ] Documentation updated
-   [ ] Backward compatibility maintained
-   [ ] No regressions in functionality

### Full Consolidation Complete When:

-   [ ] All 10 core scripts created
-   [ ] All 62 old scripts archived or removed
-   [ ] Full test coverage
-   [ ] Complete documentation
-   [ ] User migration completed
-   [ ] CI/CD integration working

---

## 📚 Documentation Updates Needed

### Files to Create:

-   [ ] `scripts/README.md` - Overview of new structure
-   [ ] `scripts/lib/README.md` - Common library documentation
-   [ ] `docs/BUILD_SCRIPT_MIGRATION_GUIDE.md` - Migration guide
-   [ ] `docs/BUILD_SCRIPT_DEVELOPMENT.md` - How to create new scripts

### Files to Update:

-   [ ] `README.md` - Update build instructions
-   [ ] `Makefile` - Update targets to use new scripts
-   [ ] `docs/BUILD_SCRIPTS_CATALOG.md` - Mark old scripts as deprecated
-   [ ] All quickstart guides

---

## 🚀 Timeline

### Week 1 (Current):

-   [x] Create common library
-   [ ] Refactor primary ISO builder
-   [ ] Test basic functionality

### Week 2:

-   [ ] Create kernel-only builder
-   [ ] Create full-linux builder
-   [ ] Create testing tools

### Week 3:

-   [ ] Create maintenance tools
-   [ ] Create specialized tools
-   [ ] Full integration testing

### Week 4:

-   [ ] Documentation sprint
-   [ ] User migration
-   [ ] Archive legacy scripts

---

## 📝 Notes

### Design Principles:

1. **DRY (Don't Repeat Yourself)**

    - Common functions in library
    - No code duplication

2. **KISS (Keep It Simple, Stupid)**

    - Each script has one purpose
    - Clear, readable code

3. **Convention over Configuration**

    - Sensible defaults
    - Environment variables for overrides

4. **Fail Fast**

    - `set -euo pipefail`
    - Early validation
    - Clear error messages

5. **Testability**
    - Functions over inline code
    - Small, focused functions
    - Easy to unit test

---

## 🔍 Next Steps

### Immediate (Today):

1. ✅ Create build-common.sh library
2. 🔄 Create build-iso.sh (refactor unified-iso-builder.sh)
3. ⏭️ Test new ISO builder
4. ⏭️ Update documentation

### This Week:

1. Create build-kernel-only.sh
2. Create build-full-linux.sh
3. Test all three builders
4. Create migration guide

---

**Status:** Phase 1 Complete, Phase 2 In Progress  
**Next Action:** Create scripts/build-iso.sh using build-common.sh library  
**Updated:** October 23, 2025
