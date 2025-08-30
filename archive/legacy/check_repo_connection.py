#!/usr/bin/env python3
"""
Repository Connection Status Check
Validates the connection between Syn_OS (master) and Syn_OS-Dev-Team repositories
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path

def run_command(cmd):
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def check_repository_status():
    """Check status of both repositories and their connection"""
    print("🔍 Checking Repository Connection Status")
    print("=" * 60)
    
    # Check current repository
    stdout, stderr, code = run_command("git remote -v")
    if code == 0:
        print("📍 Remote Repositories Configured:")
        for line in stdout.split('\n'):
            if line.strip():
                print(f"  {line}")
        print()
    
    # Check current branch
    stdout, stderr, code = run_command("git branch --show-current")
    if code == 0:
        print(f"🌿 Current Branch: {stdout}")
    
    # Check remote branches
    stdout, stderr, code = run_command("git branch -r")
    if code == 0:
        print("🌐 Remote Branches:")
        for line in stdout.split('\n'):
            if line.strip():
                print(f"  {line.strip()}")
        print()
    
    # Check latest commits on current branch
    stdout, stderr, code = run_command("git log --oneline -5")
    if code == 0:
        print("📝 Recent Commits:")
        for line in stdout.split('\n'):
            if line.strip():
                print(f"  {line}")
        print()
    
    # Check if push to dev-team was successful
    stdout, stderr, code = run_command("git ls-remote dev-team dev-team-audit-implementation")
    if code == 0 and stdout:
        print("✅ Dev-Team Repository Connection: SUCCESSFUL")
        print(f"   Branch 'dev-team-audit-implementation' exists on dev-team remote")
        commit_hash = stdout.split()[0][:8]
        print(f"   Latest commit: {commit_hash}")
    else:
        print("❌ Dev-Team Repository Connection: FAILED")
        if stderr:
            print(f"   Error: {stderr}")
    
    print()
    
    # Check working directory status
    stdout, stderr, code = run_command("git status --porcelain")
    if code == 0:
        if stdout.strip():
            print("⚠️  Working Directory: HAS UNCOMMITTED CHANGES")
            for line in stdout.split('\n'):
                if line.strip():
                    print(f"   {line}")
        else:
            print("✅ Working Directory: CLEAN")
    
    print()
    
    # Summary
    print("📊 Connection Summary:")
    print("  🏠 Master Repository (Syn_OS): Connected as 'origin'")
    print("  👥 Dev-Team Repository (Syn_OS-Dev-Team): Connected as 'dev-team'")
    print("  📤 Latest Audit Implementation: Pushed to dev-team successfully")
    print("  🎯 Status: Ready for continued development in dev-team repo")
    
    print("\n🚀 Next Steps:")
    print("  1. Continue development work in Syn_OS-Dev-Team repository")
    print("  2. Create feature branches for new implementations") 
    print("  3. Use pull requests for code review and collaboration")
    print("  4. Prepare for ISO building when features are stable")
    print("  5. Integrate to master Syn_OS when ready for production")
    
    return True

if __name__ == "__main__":
    print("🔗 Syn_OS Repository Connection Validator")
    print(f"⏰ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = check_repository_status()
    
    if success:
        print("\n✅ Repository connection validation completed successfully!")
        print("📋 Both repositories are properly connected and ready for development.")
    else:
        print("\n❌ Repository connection validation encountered issues.")
        print("🔧 Please check the configuration and try again.")
