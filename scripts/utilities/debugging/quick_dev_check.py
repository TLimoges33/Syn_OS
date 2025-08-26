#!/usr/bin/env python3
"""
Quick Dev Repository Essentials Check
====================================

Focused analysis of critical missing files between repositories.
"""

import subprocess
from pathlib import Path

def run_cmd(cmd):
    """Run command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="/home/diablorain/Syn_OS")
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except:
        return []

def check_critical_files():
    """Check for critical development files."""
    
    print("🔍 CRITICAL DEVELOPMENT FILES CHECK")
    print("=" * 40)
    
    # Essential files that dev teams need
    critical_files = {
        "Build System": [
            "Makefile",
            "requirements-consciousness.txt", 
            "src/consciousness/Cargo.toml",
            "src/kernel/Cargo.toml"
        ],
        "Error Handling": [
            "src/error_handling/",
            "tests/test_error_handling.py"
        ],
        "Core Scripts": [
            "scripts/a_plus_security_audit.py",
            "scripts/setup-dev-env.sh"
        ]
    }
    
    # Check what exists in main repo
    print("\n📋 Main Repository Status:")
    for category, files in critical_files.items():
        print(f"\n{category}:")
        for file in files:
            if file.endswith('/'):
                exists = run_cmd(f"test -d {file} && echo 'YES' || echo 'NO'")
            else:
                exists = run_cmd(f"test -f {file} && echo 'YES' || echo 'NO'")
            status = "✅" if exists and exists[0] == "YES" else "❌"
            print(f"  {status} {file}")
    
    # Check dev-team repo
    print(f"\n📋 Dev-Team Repository Status:")
    dev_files = run_cmd("git ls-tree -r --name-only dev-team/main")
    
    missing = []
    for category, files in critical_files.items():
        print(f"\n{category}:")
        for file in files:
            # Check if file exists in dev-team
            file_base = file.rstrip('/')
            exists_in_dev = any(file_base in f for f in dev_files)
            
            if not exists_in_dev:
                # Check if exists in main
                if file.endswith('/'):
                    exists_in_main = run_cmd(f"test -d {file} && echo 'YES' || echo 'NO'")
                else:
                    exists_in_main = run_cmd(f"test -f {file} && echo 'YES' || echo 'NO'")
                
                if exists_in_main and exists_in_main[0] == "YES":
                    missing.append(file)
                    print(f"  ❌ MISSING: {file}")
                else:
                    print(f"  ⚠️  N/A: {file}")
            else:
                print(f"  ✅ EXISTS: {file}")
    
    return missing

def check_empty_readmes():
    """Check for potentially empty README files."""
    
    print(f"\n📄 POTENTIALLY EMPTY DOCUMENTATION")
    print("=" * 35)
    
    # Get README files from dev-team
    readmes = run_cmd("git ls-tree -r --name-only dev-team/main | grep -i readme")
    
    important_readmes = [
        "README.md",
        "docs/README.md", 
        "docs/architecture/README.md",
        "docs/development/README.md",
        "src/error_handling/README.md"
    ]
    
    print("Key README files that should have content:")
    for readme in important_readmes:
        exists = any(readme in f for f in readmes)
        status = "✅" if exists else "❌ MISSING"
        print(f"  {status} {readme}")
    
    return important_readmes

def generate_quick_fix():
    """Generate quick commands to fix issues."""
    
    print(f"\n🚀 QUICK FIX PLAN")
    print("=" * 18)
    
    print("1. Check which files actually need to be transferred:")
    print("   ls -la src/error_handling/ 2>/dev/null || echo 'Need to create error_handling'")
    print("   ls -la requirements-consciousness.txt 2>/dev/null || echo 'Missing requirements'")
    
    print("\n2. If files are missing, copy from main repo:")
    print("   # For missing error_handling:")
    print("   git checkout dev-team/main")
    print("   mkdir -p src/error_handling/")
    print("   # Add basic error handling structure")
    
    print("\n3. Create/update empty README files with basic content")
    print("   # Update main README.md, docs/README.md etc.")

if __name__ == "__main__":
    missing = check_critical_files()
    empty_readmes = check_empty_readmes()
    
    print(f"\n🎯 SUMMARY")
    print("=" * 10)
    print(f"Critical missing files: {len(missing)}")
    print(f"README files to check: {len(empty_readmes)}")
    
    if missing:
        print(f"\n❌ Action needed: Transfer {len(missing)} files")
        for file in missing:
            print(f"   • {file}")
    else:
        print(f"\n✅ All critical files present!")
    
    generate_quick_fix()
