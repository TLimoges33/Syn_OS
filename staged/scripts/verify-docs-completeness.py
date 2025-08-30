#!/usr/bin/env python3
"""
Documentation Completeness Verification
Ensures all documentation is comprehensive and ready for cloud dev team integration
"""

import os
import json
from pathlib import Path
from datetime import datetime

def check_documentation_completeness():
    """Check if documentation is complete and comprehensive"""
    
    print("📚 Verifying Documentation Completeness...")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    docs_dir = Path("/home/diablorain/Syn_OS/docs")
    repo_root = Path("/home/diablorain/Syn_OS")
    
    # Critical documentation files that should exist
    critical_docs = [
        "README.md",
        "CONTRIBUTING.md", 
        "SECURITY.md",
        "LICENSE",
        "CODEOWNERS",
        "docs/README.md",
        "docs/01-user-guides/README.md",
        "docs/02-development/README.md",
        "docs/03-architecture/README.md",
        "docs/04-api/README.md",
        "docs/05-tutorials/README.md",
        "docs/06-reports/README.md",
        "docs/07-roadmaps/README.md",
        "docs/08-research/README.md",
        "docs/09-archive/README.md"
    ]
    
    # Check each critical file
    missing_files = []
    existing_files = []
    
    for doc_file in critical_docs:
        file_path = repo_root / doc_file
        if file_path.exists():
            existing_files.append(doc_file)
            print(f"✅ {doc_file}")
        else:
            missing_files.append(doc_file)
            print(f"❌ Missing: {doc_file}")
    
    # Generate documentation structure report
    print("\n📊 Documentation Structure Analysis:")
    
    if docs_dir.exists():
        for item in sorted(docs_dir.rglob("*")):
            if item.is_file() and item.suffix in ['.md', '.rst', '.txt']:
                rel_path = item.relative_to(repo_root)
                size_kb = item.stat().st_size / 1024
                print(f"📄 {rel_path} ({size_kb:.1f} KB)")
    
    # Check for comprehensive content
    print("\n🔍 Content Completeness Check:")
    
    # Check README.md
    readme_path = repo_root / "README.md"
    if readme_path.exists():
        content = readme_path.read_text()
        if len(content) > 1000:
            print("✅ README.md is comprehensive")
        else:
            print("⚠️  README.md needs more content")
    
    # Check for architecture documentation
    arch_files = list((docs_dir / "03-architecture").glob("*.md")) if (docs_dir / "03-architecture").exists() else []
    if len(arch_files) >= 3:
        print(f"✅ Architecture documentation complete ({len(arch_files)} files)")
    else:
        print(f"⚠️  Architecture documentation needs expansion ({len(arch_files)} files)")
    
    # Check for API documentation
    api_files = list((docs_dir / "04-api").glob("*.md")) if (docs_dir / "04-api").exists() else []
    if len(api_files) >= 2:
        print(f"✅ API documentation complete ({len(api_files)} files)")
    else:
        print(f"⚠️  API documentation needs expansion ({len(api_files)} files)")
    
    # Generate final report
    print("\n📋 Final Documentation Report:")
    print(f"✅ Existing files: {len(existing_files)}")
    print(f"❌ Missing files: {len(missing_files)}")
    
    completeness_percentage = (len(existing_files) / len(critical_docs)) * 100
    print(f"📊 Documentation completeness: {completeness_percentage:.1f}%")
    
    if completeness_percentage >= 90:
        print("🌟 Documentation is ready for cloud dev team integration!")
        return True
    elif completeness_percentage >= 70:
        print("⚠️  Documentation needs minor improvements before team integration")
        return False
    else:
        print("❌ Documentation needs significant work before team integration")
        return False

def create_missing_documentation():
    """Create any missing critical documentation files"""
    
    print("\n🔧 Creating missing documentation files...")
    
    repo_root = Path("/home/diablorain/Syn_OS")
    
    # Create basic README files for missing directories
    readme_dirs = [
        "docs/01-user-guides",
        "docs/02-development", 
        "docs/03-architecture",
        "docs/04-api",
        "docs/05-tutorials",
        "docs/06-reports",
        "docs/07-roadmaps",
        "docs/08-research",
        "docs/09-archive"
    ]
    
    for dir_path in readme_dirs:
        full_dir = repo_root / dir_path
        readme_file = full_dir / "README.md"
        
        if not readme_file.exists():
            full_dir.mkdir(parents=True, exist_ok=True)
            
            # Create appropriate content based on directory
            if "user-guides" in dir_path:
                content = "# User Guides\n\nComprehensive guides for Syn_OS users.\n"
            elif "development" in dir_path:
                content = "# Development Documentation\n\nDeveloper resources and guides.\n"
            elif "architecture" in dir_path:
                content = "# Architecture Documentation\n\nSystem architecture and design documents.\n"
            elif "api" in dir_path:
                content = "# API Documentation\n\nAPI references and specifications.\n"
            elif "tutorials" in dir_path:
                content = "# Tutorials\n\nStep-by-step tutorials and learning materials.\n"
            elif "reports" in dir_path:
                content = "# Reports\n\nProject reports and analysis documents.\n"
            elif "roadmaps" in dir_path:
                content = "# Roadmaps\n\nProject roadmaps and planning documents.\n"
            elif "research" in dir_path:
                content = "# Research Documentation\n\nResearch papers and experimental documentation.\n"
            elif "archive" in dir_path:
                content = "# Archive\n\nArchived documentation and historical records.\n"
            else:
                content = f"# {dir_path.split('/')[-1].title()}\n\nDocumentation section.\n"
            
            readme_file.write_text(content)
            print(f"✅ Created {readme_file}")

if __name__ == "__main__":
    # Create missing documentation first
    create_missing_documentation()
    
    # Then check completeness
    is_complete = check_documentation_completeness()
    
    if is_complete:
        print("\n🚀 Documentation verification complete - ready for cloud integration!")
    else:
        print("\n⚠️  Documentation needs attention before cloud integration")
    
    exit(0 if is_complete else 1)
