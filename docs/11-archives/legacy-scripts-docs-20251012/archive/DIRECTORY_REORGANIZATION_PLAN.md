# Directory Structure Reorganization Plan

## Problem Statement
The current directory structure contains redundancies, similar content in separate folders, and naming inconsistencies. This makes navigation difficult and could lead to path-related errors during builds.

## Consolidation Plan

### 1. Source Code Directories
- Consolidate `src`, `src_clean`, and `src_new` into a single `src` directory
- Structure the source directory properly with subdirectories for different components
- Keep a clear separation between kernel and user-space components

### 2. Documentation Directories
- Merge `docs` and `docs_new` into a single `docs` directory
- Organize by topic rather than creation date

### 3. Service Directories
- Consolidate `services` and `services_new` into a single `services` directory
- Organize by functionality

### 4. Test Directories
- Merge `testing`, `tests`, `test_suite`, and `test_reports` into a single `tests` directory
- Use subdirectories for different types of tests and reports

### 5. Legacy and Archive Content
- Move `old-synapticos` into `archive` 
- Keep only necessary historical data

### 6. ParrotOS Integration Files
- Consolidate `parrotos-synapticos` and `parrotos_extracted` into a single `parrotos-integration` directory
- Keep ISO extraction separate under `iso-extraction` subdirectory

### 7. MCP Related Directories
- Consolidate `mcp` and `mcp_servers` into a single `mcp` directory

### 8. Build and Deployment
- Keep `build` and `deploy` separate as they serve different functions
- Organize build outputs consistently

### 9. Configuration
- Keep `config` directory but ensure it's properly organized

### 10. Tools and Scripts
- Consolidate similar functionality between `tools` and `scripts`

## Directory Structure After Reorganization

```
/home/diablorain/Syn_OS/
├── archive/              # Historical and archived content
├── build/                # Build artifacts and outputs
├── config/               # Configuration files
├── deploy/               # Deployment scripts and configurations
├── docs/                 # All documentation
├── iso-extraction/       # Extracted ISO files
├── mcp/                  # Model Context Protocol related files
├── scripts/              # Utility scripts
├── services/             # Service definitions and implementations
├── src/                  # Source code
│   ├── kernel/           # Kernel code
│   ├── userspace/        # User-space applications
│   └── libraries/        # Shared libraries
├── tests/                # All testing related files
└── tools/                # Development and maintenance tools
```

## Implementation Approach

1. **Preparation**
   - Create backup of current structure
   - Document current path references in build scripts

2. **Execution**
   - Create new consolidated directories
   - Move files from old locations to new ones
   - Update path references in build scripts and configuration files

3. **Verification**
   - Test builds in the new structure
   - Verify all scripts work with new paths
   - Update documentation to reflect new structure

4. **Cleanup**
   - Remove empty directories
   - Update .gitignore file
