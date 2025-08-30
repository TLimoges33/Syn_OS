#!/usr/bin/env python3
"""
Documentation Chaos Analysis Script
==================================

Analyzes the current documentation mess and provides detailed cleanup recommendations.
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import json

def analyze_documentation_chaos():
    """Comprehensive analysis of documentation sprawl"""
    
    print("🔍 ANALYZING DOCUMENTATION CHAOS")
    print("=" * 60)
    
    root_dir = Path(".")
    docs_dir = Path("docs")
    
    # Analyze root directory mess
    root_md_files = list(root_dir.glob("*.md"))
    print(f"\n📁 ROOT DIRECTORY ANALYSIS")
    print(f"Total .md files in root: {len(root_md_files)}")
    
    # Categorize root files
    categories = {
        "progress": [],
        "completion": [],  
        "audit": [],
        "setup": [],
        "architecture": [],
        "other": []
    }
    
    for file in root_md_files:
        name = file.name.lower()
        if "week" in name or "progress" in name:
            categories["progress"].append(file.name)
        elif "completion" in name or "summary" in name:
            categories["completion"].append(file.name)
        elif "audit" in name or "report" in name:
            categories["audit"].append(file.name)
        elif "setup" in name or "guide" in name or "quick" in name:
            categories["setup"].append(file.name)
        elif "architecture" in name or "implementation" in name:
            categories["architecture"].append(file.name)
        else:
            categories["other"].append(file.name)
    
    for category, files in categories.items():
        if files:
            print(f"\n  {category.upper()} FILES ({len(files)}):")
            for file in sorted(files):
                print(f"    - {file}")
    
    # Analyze docs directory
    if docs_dir.exists():
        docs_files = list(docs_dir.glob("*.md"))
        jupyter_files = list(docs_dir.glob("*.ipynb"))
        
        print(f"\n📁 DOCS DIRECTORY ANALYSIS")
        print(f"Total .md files in docs/: {len(docs_files)}")
        print(f"Total .ipynb files in docs/: {len(jupyter_files)}")
        
        # Find potential duplicates
        print(f"\n🔄 POTENTIAL DUPLICATES")
        name_groups = defaultdict(list)
        
        all_files = [(f, "root") for f in root_md_files] + [(f, "docs") for f in docs_files]
        
        for file_path, location in all_files:
            # Extract key terms for grouping
            name = file_path.stem.lower()
            key_terms = set()
            
            # Common grouping terms
            if "architecture" in name:
                key_terms.add("architecture")
            if "security" in name:
                key_terms.add("security")
            if "consciousness" in name:
                key_terms.add("consciousness")
            if "implementation" in name:
                key_terms.add("implementation")
            if "guide" in name or "setup" in name:
                key_terms.add("guide")
            if "api" in name:
                key_terms.add("api")
            if "documentation" in name:
                key_terms.add("documentation")
                
            for term in key_terms:
                name_groups[term].append((file_path.name, location))
        
        for term, files in name_groups.items():
            if len(files) > 1:
                print(f"\n  {term.upper()} related files ({len(files)}):")
                for file_name, location in files:
                    print(f"    - {file_name} ({location})")
    
    # Analyze Jupyter notebooks claiming to be "source of truth"
    print(f"\n📓 JUPYTER NOTEBOOK ANALYSIS")
    jupyter_files = list(docs_dir.glob("*.ipynb"))
    source_of_truth_claims = []
    
    for notebook in jupyter_files:
        if "encyclopedia" in notebook.name.lower() or "unified" in notebook.name.lower() or "master" in notebook.name.lower():
            source_of_truth_claims.append(notebook.name)
    
    print(f"Notebooks claiming authority ({len(source_of_truth_claims)}):")
    for notebook in source_of_truth_claims:
        print(f"  - {notebook}")
    
    if len(source_of_truth_claims) > 1:
        print("  ⚠️  CONFLICT: Multiple 'source of truth' documents!")
    
    # Analyze README variations
    print(f"\n📄 README VARIATIONS")
    readme_files = list(root_dir.glob("README*.md"))
    print(f"README variants ({len(readme_files)}):")
    for readme in readme_files:
        print(f"  - {readme.name}")
    
    # Generate cleanup recommendations
    print(f"\n🧹 CLEANUP RECOMMENDATIONS")
    print("=" * 60)
    
    total_files_to_move = len([f for f in root_md_files if f.name not in ["README.md", "CLAUDE.md", "SECURITY.md", "LESSONS_LEARNED.md"]])
    
    print(f"1. MOVE {total_files_to_move} files from root to organized docs/ structure")
    print(f"2. CONSOLIDATE {len(source_of_truth_claims)} competing 'source of truth' documents")
    print(f"3. ELIMINATE duplicate README files (keep main README.md only)")
    print(f"4. CREATE module-specific documentation for {len(list(Path('src').glob('*')))} src/ modules")
    print(f"5. ORGANIZE {len(docs_files)} docs/ files into logical hierarchy")
    
    # Specific move recommendations
    print(f"\n📋 SPECIFIC MOVE PLAN")
    print("Files to KEEP in root:")
    keep_in_root = ["README.md", "CLAUDE.md", "SECURITY.md", "LESSONS_LEARNED.md", "QUICK_START.md"]
    for file in keep_in_root:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (missing)")
    
    print(f"\nFiles to MOVE to docs/07-archive/:")
    for category, files in categories.items():
        if category in ["progress", "completion", "audit"]:
            for file in files:
                print(f"  📦 {file} → docs/07-archive/development-phases/")
    
    print(f"\nFiles to MOVE to docs/01-overview/:")
    for file in categories["setup"]:
        print(f"  📦 {file} → docs/01-overview/")
    
    print(f"\nFiles to MOVE to docs/02-architecture/:")
    for file in categories["architecture"]:
        print(f"  📦 {file} → docs/02-architecture/")
    
    # Generate implementation script
    generate_cleanup_script(categories, docs_files)
    
    print(f"\n✅ Analysis complete!")
    print(f"📄 Cleanup script generated: cleanup_documentation.py")
    print(f"🎯 Ready to begin professional documentation overhaul")

def generate_cleanup_script(categories, docs_files):
    """Generate automated cleanup script"""
    
    script_content = '''#!/usr/bin/env python3
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
'''
    
    # Add specific file moves based on analysis
    move_plans = {
        "07-archive/development-phases": categories["progress"] + categories["completion"],
        "07-archive/legacy-docs": categories["audit"],
        "01-overview": [f for f in categories["setup"] if "quick" not in f.lower()],
        "02-architecture": categories["architecture"]
    }
    
    for dest, files in move_plans.items():
        for file in files:
            script_content += f'        "{file}": "{dest}",\n'
    
    script_content += '''    }
    
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
    
    print("\\n🎉 Documentation cleanup complete!")
    print("📖 New documentation hub: docs/README.md")

if __name__ == "__main__":
    cleanup_documentation()
'''
    
    with open("cleanup_documentation.py", "w") as f:
        f.write(script_content)
    
    os.chmod("cleanup_documentation.py", 0o755)

if __name__ == "__main__":
    analyze_documentation_chaos()