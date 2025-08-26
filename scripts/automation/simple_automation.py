#!/usr/bin/env python3
"""
Simple Automated Development Workflow
====================================

Easy-to-use automation for Syn_OS development workflow.
"""

import os
import json
import subprocess
import requests
from datetime import datetime

class SimpleWorkflow:
    """Simple automation workflow."""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        self.dev_repo = "TLimoges33/Syn_OS-Dev-Team"
        self.master_repo = "TLimoges33/Syn_OS"
    
    def run_cmd(self, cmd, cwd=None):
        """Run command safely."""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
            return result.stdout.strip(), result.returncode == 0
        except:
            return "", False
    
    def check_completion_markers(self, branch):
        """Check if branch has completion markers."""
        print(f"🔍 Checking completion markers for {branch}")
        
        # Get recent commits
        cmd = f"git log --oneline -5 origin/{branch}"
        output, success = self.run_cmd(cmd)
        
        if not success:
            return False
        
        markers = [
            "🎯 Phase Implementation Complete",
            "✅ Ready for Integration", 
            "🧪 All Tests Passing",
            "📚 Documentation Updated"
        ]
        
        found_markers = []
        for line in output.split('\n'):
            for marker in markers:
                if marker in line:
                    found_markers.append(marker)
                    print(f"   ✅ Found: {marker}")
        
        # Need either "Ready for Integration" OR all three others
        ready = ("✅ Ready for Integration" in found_markers or 
                len(found_markers) >= 3)
        
        print(f"   {'✅ Ready for automation' if ready else '❌ Not ready yet'}")
        return ready
    
    def create_simple_pr(self, branch, team_name):
        """Create a simple pull request."""
        print(f"🔄 Creating PR for {branch}")
        
        if not self.github_token:
            print("❌ GitHub token not configured")
            return False
        
        # Get latest commit
        cmd = f"git log -1 --format='%H|%s|%an' origin/{branch}"
        output, success = self.run_cmd(cmd)
        
        if not success:
            return False
        
        commit_hash, commit_msg, author = output.split('|', 2)
        
        # Simple PR data
        pr_data = {
            "title": f"🚀 {team_name} Phase Integration",
            "head": branch,
            "base": "main", 
            "body": f"""# {team_name} Development Complete

## Summary
Automated integration of {team_name} development phase.

**Latest Commit**: {commit_hash[:8]}
**Message**: {commit_msg}
**Author**: {author}

## Verification
- ✅ Phase markers detected
- ✅ Ready for integration
- ✅ Automated testing enabled

---
*Created automatically by Syn_OS Workflow*"""
        }
        
        # GitHub API call
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        url = f"https://api.github.com/repos/{self.dev_repo}/pulls"
        
        try:
            response = requests.post(url, headers=headers, json=pr_data)
            if response.status_code == 201:
                pr = response.json()
                print(f"✅ Created PR #{pr['number']}: {pr['html_url']}")
                return True
            else:
                print(f"❌ Failed to create PR: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error creating PR: {e}")
            return False
    
    def sync_to_master(self):
        """Sync dev-team changes to master repo."""
        print(f"🔄 Syncing to master repository")
        
        commands = [
            "git fetch dev-team main",
            "git checkout master",
            "git merge dev-team/main --no-ff -m 'Auto-sync: Dev team integration'",
            "git push origin master"
        ]
        
        for cmd in commands:
            print(f"   Running: {cmd}")
            output, success = self.run_cmd(cmd)
            if not success:
                print(f"   ❌ Failed: {output}")
                return False
            print(f"   ✅ Success")
        
        return True
    
    def build_iso(self):
        """Build ISO if script exists."""
        print(f"🏗️ Building ISO")
        
        iso_script = "scripts/build-simple-kernel-iso.sh"
        if not os.path.exists(iso_script):
            print(f"❌ ISO build script not found: {iso_script}")
            return False
        
        # Make executable and run
        self.run_cmd(f"chmod +x {iso_script}")
        output, success = self.run_cmd(f"./{iso_script}")
        
        if success:
            print(f"✅ ISO build completed")
            # Look for generated ISOs
            iso_output, _ = self.run_cmd("find build/ -name '*.iso' 2>/dev/null")
            for iso in iso_output.split('\n'):
                if iso.strip():
                    print(f"   📀 Generated: {iso}")
            return True
        else:
            print(f"❌ ISO build failed: {output}")
            return False
    
    def run_automation_check(self):
        """Run automation check for all feature branches."""
        print("🤖 SYN_OS AUTOMATION CHECK")
        print("=" * 30)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Fetch latest
        print("\n📡 Fetching latest changes...")
        self.run_cmd("git fetch --all")
        
        # Check each feature branch
        branches = [
            ("feature/consciousness-kernel", "Consciousness"),
            ("feature/security-framework", "Security"),
            ("feature/education-platform", "Education"),
            ("feature/performance-optimization", "Performance"),
            ("feature/enterprise-integration", "Enterprise"),
            ("feature/quantum-computing", "Quantum"),
            ("feature/documentation-system", "Documentation"),
            ("feature/testing-framework", "QA"),
            ("feature/iso-building", "Build"),
            ("feature/monitoring-observability", "DevOps")
        ]
        
        ready_branches = []
        
        for branch, team in branches:
            print(f"\n📋 Checking {team} Team ({branch})")
            if self.check_completion_markers(branch):
                ready_branches.append((branch, team))
        
        # Process ready branches
        if ready_branches:
            print(f"\n🚀 Processing {len(ready_branches)} ready branches:")
            
            for branch, team in ready_branches:
                print(f"\n--- Processing {team} ---")
                
                # Create PR
                if self.create_simple_pr(branch, team):
                    print(f"✅ {team}: PR created successfully")
                else:
                    print(f"❌ {team}: PR creation failed")
        else:
            print(f"\n📋 No branches ready for automation")
        
        return len(ready_branches)

if __name__ == "__main__":
    workflow = SimpleWorkflow()
    ready_count = workflow.run_automation_check()
    
    print(f"\n🎯 AUTOMATION SUMMARY")
    print("=" * 20)
    print(f"Branches processed: {ready_count}")
    print(f"Status: {'✅ Active' if ready_count > 0 else '⏸️ Monitoring'}")
    
    # If in master repo and changes detected, build ISO
    if os.path.exists("scripts/build-simple-kernel-iso.sh"):
        print(f"\n🏗️ Checking if ISO build needed...")
        # Simple check - if we're in master repo
        repo_check, _ = workflow.run_cmd("git remote get-url origin")
        if "Syn_OS.git" in repo_check and not "Dev-Team" in repo_check:
            print("📍 In master repository - checking for ISO build")
            workflow.build_iso()
