#!/bin/bash

# Reports Folder Organization Script
# Cleans up duplication and creates logical structure

echo "📊 REPORTS FOLDER ORGANIZATION"
echo "=============================="

cd /home/diablorain/Syn_OS/docs/reports

# Create backup
backup_dir="../archive/reports-cleanup-backup-$(date +%Y%m%d-%H%M%S)"
echo "📦 Creating backup: $backup_dir"
mkdir -p "$backup_dir"
cp -r . "$backup_dir/"

echo ""
echo "🔍 ANALYZING CURRENT STATE"
echo "=========================="

echo "📄 Files in main reports/:"
find . -maxdepth 1 -name "*.md" | wc -l

echo "📄 Files in completion/:"
find completion/ -name "*.md" 2>/dev/null | wc -l || echo "0"

echo "📄 Empty files:"
find . -name "*.md" -size 0 | wc -l

echo ""
echo "🧹 CLEANING UP STRUCTURE"
echo "========================"

# Step 1: Remove empty files
echo "🗑️ Removing empty files..."
find . -name "*.md" -size 0 -delete

# Step 2: Create proper categorized structure
echo "📁 Creating organized structure..."
mkdir -p {optimization,integration,phase-completions,system-status,current-session}

# Step 3: Categorize and organize files
echo "📋 Categorizing reports..."

# Current session reports (today's work)
echo "📅 Moving current session reports..."
mv ARCHITECTURE_INTEGRATION_COMPLETE.md current-session/ 2>/dev/null || true
mv FINAL_ARCHITECTURE_SUCCESS.md current-session/ 2>/dev/null || true
mv FINAL_OPTIMIZATION_COMPLETE.md current-session/ 2>/dev/null || true
mv OPTIMIZATION_COMPLETE_REPORT.md current-session/ 2>/dev/null || true

# Phase completion reports
echo "🏗️ Moving phase completion reports..."
mv PHASE_*_COMPLETION_REPORT.md phase-completions/ 2>/dev/null || true
mv PHASE_*_PLANNING.md phase-completions/ 2>/dev/null || true
mv PHASE_*_TESTING_COMPLETE.md phase-completions/ 2>/dev/null || true
mv PHASE_*_NETWORK_STACK_COMPLETE.md phase-completions/ 2>/dev/null || true
mv PHASE_*_USERSPACE_APPLICATIONS_PLAN.md phase-completions/ 2>/dev/null || true
mv PHASE_*_COMPLETION_PHASE_*_ROADMAP.md phase-completions/ 2>/dev/null || true

# System status and achievements
echo "🎯 Moving system status reports..."
mv SYNOS_V1_COMPLETE_ACHIEVEMENT.md system-status/ 2>/dev/null || true
mv PRODUCTION_READINESS_REPORT.md system-status/ 2>/dev/null || true
mv SYSTEM_REALITY_AUDIT.md system-status/ 2>/dev/null || true

# Security and eBPF reports
echo "🔒 Moving security reports..."
mv EBPF_*_COMPLETION_REPORT.md system-status/ 2>/dev/null || true

# Step 4: Handle completion folder duplication
echo "🔄 Resolving completion folder duplication..."

if [ -d "completion/" ]; then
    # Move unique files from completion/ to appropriate categories
    cd completion/
    
    # Files that belong in system-status
    mv IMPLEMENTATION_COMPLETE.md ../system-status/ 2>/dev/null || true
    mv ORGANIZATION_SUCCESS_SUMMARY.md ../system-status/ 2>/dev/null || true
    mv PRODUCTION_READINESS_REPORT.md ../system-status/ 2>/dev/null || true
    mv SYNOS_V1_COMPLETE_ACHIEVEMENT.md ../system-status/ 2>/dev/null || true
    mv SYNOS_V1_COMPLETION_REPORT.md ../system-status/ 2>/dev/null || true
    mv TODO_IMPLEMENTATION_STATUS_COMPLETE.md ../system-status/ 2>/dev/null || true
    
    # Phase completion files
    mv PHASE_*_COMPLETION_REPORT.md ../phase-completions/ 2>/dev/null || true
    mv PHASE_*_NETWORK_STACK_COMPLETE.md ../phase-completions/ 2>/dev/null || true
    
    # Remove empty completion folder
    cd ..
    rmdir completion/ 2>/dev/null || true
fi

# Step 5: Create master index
echo "📖 Creating reports index..."

cat > README.md << 'EOF'
# SynOS Reports Directory

## Overview

This directory contains all SynOS project reports organized by category and purpose.

## Directory Structure

### 📅 [current-session/](current-session/)
Reports from the current documentation optimization session (September 12, 2025):
- Architecture integration completion
- Final optimization achievements
- Session summary reports

### 🏗️ [phase-completions/](phase-completions/)
Development phase completion reports:
- Phase 4-8 completion reports
- Network stack completion
- Userspace applications planning
- Development milestone reports

### 🎯 [system-status/](system-status/)
Current system status and achievement reports:
- SynOS v1.0 completion status
- Production readiness assessments
- Implementation completion summaries
- Security framework completions

### 📊 [optimization/](optimization/)
System and documentation optimization reports:
- Performance optimization results
- Infrastructure improvements
- Workflow optimizations

### 🔗 [integration/](integration/)
Integration and consolidation reports:
- Service integration reports
- Architecture consolidation
- System unification achievements

## Quick Navigation

| Report Type | Location | Purpose |
|-------------|----------|---------|
| **Latest Session** | `current-session/` | Today's work and achievements |
| **Phase Status** | `phase-completions/` | Development milestone tracking |
| **System Health** | `system-status/` | Current system state and readiness |
| **Improvements** | `optimization/` | Performance and efficiency gains |
| **Consolidation** | `integration/` | Unification and integration work |

## Report Categories

### ✅ Completion Reports
- Track finished development phases
- Document achievement milestones
- Provide status summaries

### 📈 Status Reports
- Current system capabilities
- Readiness assessments
- Performance metrics

### 🔧 Optimization Reports
- Infrastructure improvements
- Workflow enhancements
- Efficiency gains

### 🎯 Achievement Reports
- Major milestone completions
- Success summaries
- Project accomplishments
EOF

# Create individual section READMEs
echo "📝 Creating section READMEs..."

cat > current-session/README.md << 'EOF'
# Current Session Reports

Reports from the September 12, 2025 documentation optimization session.

## Session Achievements

1. **Architecture Integration** - Consolidated scattered folders into optimal structure
2. **Final Optimization** - Eliminated duplicates and achieved professional organization
3. **Complete Integration** - Perfect documentation architecture achieved

## Session Files

- `ARCHITECTURE_INTEGRATION_COMPLETE.md` - Folder consolidation results
- `FINAL_ARCHITECTURE_SUCCESS.md` - Overall architecture transformation
- `FINAL_OPTIMIZATION_COMPLETE.md` - Documentation optimization summary
- `OPTIMIZATION_COMPLETE_REPORT.md` - Comprehensive session report
EOF

cat > phase-completions/README.md << 'EOF'
# Phase Completion Reports

Development phase milestone and completion tracking.

## Phase Overview

- **Phase 4-6**: Core system development and integration
- **Phase 7**: Network stack implementation
- **Phase 8**: Userspace applications and final system completion

## Report Files

Phase completion reports document the successful achievement of major development milestones and provide roadmaps for subsequent phases.
EOF

cat > system-status/README.md << 'EOF'
# System Status Reports

Current SynOS system status, achievements, and readiness assessments.

## Status Categories

- **v1.0 Completion**: SynOS version 1.0 achievement reports
- **Production Readiness**: System readiness for production deployment
- **Implementation Status**: Current implementation completion state
- **Security Status**: Security framework and eBPF completion

## Assessment Reports

These reports provide comprehensive views of system capabilities, completion status, and deployment readiness.
EOF

cat > optimization/README.md << 'EOF'
# Optimization Reports

System, infrastructure, and workflow optimization achievements.

## Optimization Areas

- **Performance**: System performance improvements
- **Infrastructure**: Infrastructure consolidation and optimization
- **Workflow**: Development workflow enhancements
- **Documentation**: Documentation organization and optimization

## Optimization Tracking

Reports in this section document improvements, efficiency gains, and optimization achievements across all system areas.
EOF

cat > integration/README.md << 'EOF'
# Integration Reports

System integration, consolidation, and unification achievements.

## Integration Types

- **Service Integration**: Microservice consolidation and unification
- **Architecture Integration**: System architecture consolidation
- **Documentation Integration**: Documentation system unification
- **Infrastructure Integration**: Infrastructure consolidation

## Integration Tracking

These reports document the consolidation and unification of various system components into cohesive, maintainable architectures.
EOF

echo ""
echo "✅ REPORTS ORGANIZATION COMPLETE!"
echo "================================="
echo "📊 Final structure:"
echo "  current-session: $(find current-session/ -name "*.md" 2>/dev/null | wc -l) files"
echo "  phase-completions: $(find phase-completions/ -name "*.md" 2>/dev/null | wc -l) files"
echo "  system-status: $(find system-status/ -name "*.md" 2>/dev/null | wc -l) files"
echo "  optimization: $(find optimization/ -name "*.md" 2>/dev/null | wc -l) files"
echo "  integration: $(find integration/ -name "*.md" 2>/dev/null | wc -l) files"
echo ""
echo "🎯 Reports folder is now perfectly organized!"
