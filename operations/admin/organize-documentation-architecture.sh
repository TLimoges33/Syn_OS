#!/bin/bash

# Documentation Architecture Optimization Script
# Organizes documentation files into logical locations within the docs structure

echo "📚 DOCUMENTATION ARCHITECTURE OPTIMIZATION"
echo "=========================================="

cd /home/diablorain/Syn_OS

# Create comprehensive backup
backup_dir="/home/diablorain/Syn_OS/archive/documentation-optimization-backup-$(date +%Y%m%d-%H%M%S)"
echo "📦 Creating documentation backup: $backup_dir"
mkdir -p "$backup_dir"

# Backup documentation files being moved
echo "💾 Backing up documentation files..."
cp ARCHITECTURE_AUDIT_REPORT.json "$backup_dir/" 2>/dev/null || true
cp ARCHITECTURE_OPTIMIZATION_PLAN.md "$backup_dir/" 2>/dev/null || true
cp OPTIMIZED_ARCHITECTURE.md "$backup_dir/" 2>/dev/null || true
cp ECOSYSTEM_OPTIMIZATION_COMPLETE.md "$backup_dir/" 2>/dev/null || true
cp ECOSYSTEM_PRODUCTION_SUCCESS.md "$backup_dir/" 2>/dev/null || true
cp FINAL_TOOLS_OPTIMIZATION.md "$backup_dir/" 2>/dev/null || true
cp ROADMAP_COMPLETE_OS.md "$backup_dir/" 2>/dev/null || true
cp TODO_IMPLEMENTATION_STATUS.md "$backup_dir/" 2>/dev/null || true

echo ""
echo "🎯 DOCUMENTATION CATEGORIZATION STRATEGY"
echo "========================================"

echo "📋 File organization by logical purpose:"
echo ""
echo "🏗️ ARCHITECTURE DOCUMENTATION:"
echo "   → /docs/02-architecture/"
echo "   Files: Architecture audit, optimization plan, optimized structure"
echo ""
echo "📊 OPERATIONS REPORTS:"
echo "   → /docs/05-operations/optimization-reports/"
echo "   Files: Ecosystem optimization, production success, tools optimization"
echo ""
echo "📝 PROJECT MANAGEMENT:"
echo "   → /docs/06-reference/project-management/"
echo "   Files: Roadmap, TODO status, implementation tracking"

echo ""
echo "🚀 EXECUTING DOCUMENTATION OPTIMIZATION"
echo "======================================"

# Step 1: Create directory structure
echo "🏗️ Creating documentation directory structure..."

mkdir -p docs/02-architecture/
mkdir -p docs/05-operations/optimization-reports/
mkdir -p docs/06-reference/project-management/

echo "  ✅ Created documentation directory structure"

# Step 2: Move architecture documentation
echo "🏗️ Moving architecture documentation..."

if [ -f "ARCHITECTURE_AUDIT_REPORT.json" ]; then
    mv ARCHITECTURE_AUDIT_REPORT.json docs/02-architecture/
    echo "  ✅ Moved ARCHITECTURE_AUDIT_REPORT.json to /docs/02-architecture/"
fi

if [ -f "ARCHITECTURE_OPTIMIZATION_PLAN.md" ]; then
    mv ARCHITECTURE_OPTIMIZATION_PLAN.md docs/02-architecture/
    echo "  ✅ Moved ARCHITECTURE_OPTIMIZATION_PLAN.md to /docs/02-architecture/"
fi

if [ -f "OPTIMIZED_ARCHITECTURE.md" ]; then
    mv OPTIMIZED_ARCHITECTURE.md docs/02-architecture/
    echo "  ✅ Moved OPTIMIZED_ARCHITECTURE.md to /docs/02-architecture/"
fi

# Step 3: Move operations reports
echo "📊 Moving operations optimization reports..."

if [ -f "ECOSYSTEM_OPTIMIZATION_COMPLETE.md" ]; then
    mv ECOSYSTEM_OPTIMIZATION_COMPLETE.md docs/05-operations/optimization-reports/
    echo "  ✅ Moved ECOSYSTEM_OPTIMIZATION_COMPLETE.md to /docs/05-operations/optimization-reports/"
fi

if [ -f "ECOSYSTEM_PRODUCTION_SUCCESS.md" ]; then
    mv ECOSYSTEM_PRODUCTION_SUCCESS.md docs/05-operations/optimization-reports/
    echo "  ✅ Moved ECOSYSTEM_PRODUCTION_SUCCESS.md to /docs/05-operations/optimization-reports/"
fi

if [ -f "FINAL_TOOLS_OPTIMIZATION.md" ]; then
    mv FINAL_TOOLS_OPTIMIZATION.md docs/05-operations/optimization-reports/
    echo "  ✅ Moved FINAL_TOOLS_OPTIMIZATION.md to /docs/05-operations/optimization-reports/"
fi

# Step 4: Move project management documentation
echo "📝 Moving project management documentation..."

if [ -f "ROADMAP_COMPLETE_OS.md" ]; then
    mv ROADMAP_COMPLETE_OS.md docs/06-reference/project-management/
    echo "  ✅ Moved ROADMAP_COMPLETE_OS.md to /docs/06-reference/project-management/"
fi

if [ -f "TODO_IMPLEMENTATION_STATUS.md" ]; then
    mv TODO_IMPLEMENTATION_STATUS.md docs/06-reference/project-management/
    echo "  ✅ Moved TODO_IMPLEMENTATION_STATUS.md to /docs/06-reference/project-management/"
fi

# Step 5: Create documentation index updates
echo "📋 Creating documentation index updates..."

# Update architecture section README
cat >> docs/02-architecture/README.md << 'EOF'

## Architecture Optimization Documentation

### 📊 Architecture Analysis & Planning

- **[Architecture Audit Report](ARCHITECTURE_AUDIT_REPORT.json)** - Comprehensive analysis of project structure with optimization opportunities
- **[Architecture Optimization Plan](ARCHITECTURE_OPTIMIZATION_PLAN.md)** - Strategic plan for transforming project architecture
- **[Optimized Architecture](OPTIMIZED_ARCHITECTURE.md)** - Final production-grade architecture documentation

### 🎯 Key Achievements

The architecture optimization transformed a chaotic 959-file tools folder and scattered structure into a logical, production-grade architecture with clear separation of concerns.
EOF

# Update operations section
cat > docs/05-operations/optimization-reports/README.md << 'EOF'
# 📊 Operations Optimization Reports

This directory contains comprehensive reports documenting the major optimization efforts that transformed SynOS from a chaotic structure into a production-grade architecture.

## Optimization Timeline

### 🏗️ [Ecosystem Optimization](ECOSYSTEM_OPTIMIZATION_COMPLETE.md)
Initial transformation of the 1098-file ecosystem folder into organized components.

### 🎉 [Ecosystem Production Success](ECOSYSTEM_PRODUCTION_SUCCESS.md)  
Comprehensive success report documenting the complete elimination of ecosystem chaos.

### 🔧 [Final Tools Optimization](FINAL_TOOLS_OPTIMIZATION.md)
Final cleanup of remaining tools folder components with optimal architectural placement.

## Impact Summary

- **Transformed:** 1098+ scattered files into logical organization
- **Eliminated:** Chaotic folder structures  
- **Achieved:** Production-grade architecture with clear separation of concerns
- **Result:** Maintainable, scalable, enterprise-ready codebase
EOF

# Update reference section
cat >> docs/06-reference/project-management/README.md << 'EOF'

## Project Management Documentation

### 📋 Planning & Tracking

- **[Complete OS Roadmap](ROADMAP_COMPLETE_OS.md)** - Strategic roadmap for SynOS development
- **[Implementation Status](TODO_IMPLEMENTATION_STATUS.md)** - Current status of TODO items and implementation progress

### 🎯 Project Status

The project has achieved major architectural optimization milestones with a clean, production-grade structure now in place.
EOF

echo ""
echo "✅ DOCUMENTATION OPTIMIZATION COMPLETE!"
echo "======================================"

echo "📊 Organization Results:"
echo "  🏗️ Architecture docs → /docs/02-architecture/ (3 files)"
echo "  📊 Operations reports → /docs/05-operations/optimization-reports/ (3 files)"
echo "  📝 Project management → /docs/06-reference/project-management/ (2 files)"
echo "  📋 Updated section READMEs with proper documentation"

echo ""
echo "🎯 Documentation Benefits:"
echo "  ✅ Logical categorization by purpose and audience"
echo "  ✅ Architecture documentation with architecture section"
echo "  ✅ Operations reports properly categorized" 
echo "  ✅ Project management in reference section"
echo "  ✅ Clean root directory structure"
echo "  ✅ Improved discoverability and navigation"

echo ""
echo "💾 Backup location: $backup_dir"
