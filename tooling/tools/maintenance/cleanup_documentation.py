#!/usr/bin/env python3
"""
Automated Documentation Cleanup Script
=====================================

This script performs the professional documentation reorganization.
"""

import os
import shutil
from pathlib import Path

def cleanup_documentation():
    """Execute the documentation cleanup plan"""
    
    print("🧹 STARTING DOCUMENTATION CLEANUP")
    print("=" * 50)
    
    # Create new documentation structure
    new_docs = Path("docs_new")
    new_docs.mkdir(exist_ok=True)
    
    # Create directory structure
    directories = [
        "01-overview",
        "02-architecture", 
        "03-development",
        "04-api-reference",
        "05-implementation",
        "06-operations",
        "07-archive/development-phases",
        "07-archive/legacy-docs"
    ]
    
    for dir_path in directories:
        (new_docs / dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: docs_new/{dir_path}")
    
    # Move files according to plan
    moves = {
        "WEEK1_COMPLETION_SUMMARY.md": "07-archive/development-phases",
        "WEEK2_COMPLETION_SUMMARY.md": "07-archive/development-phases",
        "WEEK3_COMPLETION_SUMMARY.md": "07-archive/development-phases",
        "WEEK4_COMPLETION_SUMMARY.md": "07-archive/development-phases",
        "WEEK1_ACADEMIC_PROGRESS.md": "07-archive/development-phases",
        "WEEK2_ACADEMIC_PROGRESS.md": "07-archive/development-phases",
        "WEEK3_A_PLUS_PROGRESS.md": "07-archive/development-phases",
        "CODEBASE_AUDIT_AND_ENVIRONMENT_SUMMARY.md": "07-archive/development-phases",
        "PHASE1_CRITICAL_SECURITY_REMEDIATION_SUMMARY.md": "07-archive/development-phases",
        "PHASE2_QUALITY_MANAGEMENT_SYSTEM_SUMMARY.md": "07-archive/development-phases",
        "PHASE3_ENVIRONMENTAL_MANAGEMENT_SYSTEM_SUMMARY.md": "07-archive/development-phases",
        "COMPREHENSIVE_AUDIT_SUMMARY.md": "07-archive/development-phases",
        "CAPSTONE_COMPLETION_ROADMAP.md": "07-archive/development-phases",
        "CODEBASE_AUDIT_REPORT.md": "07-archive/legacy-docs",
        "COMPREHENSIVE_TECHNICAL_AUDIT_REPORT.md": "07-archive/legacy-docs",
        "ISO_CERTIFICATION_AUDIT_CLEANUP_PLAN.md": "07-archive/legacy-docs",
        "DOCUMENTATION_AUDIT_COMPREHENSIVE.md": "07-archive/legacy-docs",
        "CODESPACE_DEVELOPMENT_GUIDE.md": "01-overview",
        "CODESPACE_SETUP_GUIDE.md": "01-overview",
        "SYNAPTICOS_IMPLEMENTATION_COMPLETE.md": "02-architecture",
    }
    
    # Execute moves
    for file_name, dest_dir in moves.items():
        src = Path(file_name)
        if src.exists():
            dest = new_docs / dest_dir / file_name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
            print(f"📦 Moved: {file_name} → docs_new/{dest_dir}/")
    
    # Replace old docs directory
    if Path("docs").exists():
        shutil.move("docs", "docs_old_backup")
        print("📦 Backed up old docs/ → docs_old_backup/")
    
    shutil.move("docs_new", "docs")
    print("✅ Activated new documentation structure")
    
    # Replace main README
    if Path("README_NEW_PROFESSIONAL.md").exists():
        if Path("README.md").exists():
            shutil.move("README.md", "docs/07-archive/README_old.md")
        shutil.move("README_NEW_PROFESSIONAL.md", "README.md")
        print("✅ Activated new professional README")
    
    print("\n🎉 Documentation cleanup complete!")
    print("📖 New documentation hub: docs/README.md")

if __name__ == "__main__":
    cleanup_documentation()
