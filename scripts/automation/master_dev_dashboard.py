#!/usr/bin/env python3
"""
🎯 Master Dev Codespace Dashboard
Central command center for monitoring all development teams
"""

import subprocess
import json
import datetime
from typing import Dict, List, Any
import os

class MasterDevDashboard:
    def __init__(self):
        self.teams = {
            "Consciousness": "feature/consciousness-kernel",
            "Security": "feature/security-framework",
            "Education": "feature/education-platform",
            "Performance": "feature/performance-optimization",
            "Enterprise": "feature/enterprise-integration",
            "Quantum": "feature/quantum-computing",
            "Documentation": "feature/documentation-system",
            "QA": "feature/testing-framework",
            "Build": "feature/iso-building",
            "DevOps": "feature/monitoring-observability"
        }
        
    def fetch_all_branches(self):
        """Fetch latest changes from all remotes"""
        print("📡 Fetching updates from all repositories...")
        try:
            # Fetch from dev-team repo
            subprocess.run(["git", "fetch", "origin"], check=True, capture_output=True)
            
            # Fetch from master repo if configured
            try:
                subprocess.run(["git", "fetch", "master"], check=True, capture_output=True)
                print("✅ Fetched from both dev-team and master repositories")
            except:
                print("⚠️  Master remote not configured - fetched from dev-team only")
                
        except Exception as e:
            print(f"❌ Error fetching: {e}")
    
    def get_branch_status(self, branch_name: str) -> Dict[str, Any]:
        """Get detailed status of a specific branch"""
        try:
            # Switch to branch
            subprocess.run(["git", "checkout", branch_name], 
                         check=True, capture_output=True, text=True)
            
            # Get latest commit info
            commit_info = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%H|%an|%ae|%s|%cd"], 
                capture_output=True, text=True, check=True
            ).stdout.strip()
            
            if commit_info:
                hash_val, author, email, message, date = commit_info.split("|", 4)
                
                # Check for completion markers
                completion_markers = [
                    "🎯 Phase Implementation Complete",
                    "✅ Ready for Integration",
                    "🧪 All Tests Passing", 
                    "📚 Documentation Updated"
                ]
                
                found_markers = [marker for marker in completion_markers if marker in message]
                
                # Check if branch is ahead of main
                try:
                    ahead_behind = subprocess.run(
                        ["git", "rev-list", "--count", "--left-right", "origin/main...HEAD"],
                        capture_output=True, text=True, check=True
                    ).stdout.strip()
                    
                    if ahead_behind:
                        behind, ahead = ahead_behind.split("\t")
                        commits_ahead = int(ahead)
                        commits_behind = int(behind)
                    else:
                        commits_ahead = commits_behind = 0
                        
                except:
                    commits_ahead = commits_behind = 0
                
                return {
                    "branch": branch_name,
                    "latest_commit": hash_val[:8],
                    "author": author,
                    "email": email,
                    "message": message,
                    "date": date,
                    "completion_markers": found_markers,
                    "ready_for_automation": len(found_markers) >= 2,
                    "commits_ahead": commits_ahead,
                    "commits_behind": commits_behind,
                    "status": "🟢 Active" if commits_ahead > 0 else "🟡 Synced"
                }
            else:
                return {
                    "branch": branch_name,
                    "status": "❌ No commits found",
                    "ready_for_automation": False
                }
                
        except Exception as e:
            return {
                "branch": branch_name,
                "status": f"❌ Error: {str(e)}",
                "ready_for_automation": False
            }
    
    def generate_team_dashboard(self) -> None:
        """Generate comprehensive dashboard of all teams"""
        print("🎯 MASTER DEV CODESPACE DASHBOARD")
        print("=" * 50)
        print(f"📅 Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Fetch latest updates
        self.fetch_all_branches()
        print()
        
        ready_branches = []
        active_branches = []
        
        for team_name, branch_name in self.teams.items():
            print(f"📋 {team_name} Team ({branch_name})")
            print("-" * 40)
            
            status = self.get_branch_status(branch_name)
            
            if "Error" in status.get("status", ""):
                print(f"   ❌ Status: {status['status']}")
            else:
                print(f"   📍 Latest Commit: {status.get('latest_commit', 'N/A')}")
                print(f"   👤 Author: {status.get('author', 'N/A')}")
                print(f"   📝 Message: {status.get('message', 'N/A')[:60]}...")
                print(f"   📅 Date: {status.get('date', 'N/A')}")
                print(f"   🔢 Commits: +{status.get('commits_ahead', 0)} / -{status.get('commits_behind', 0)}")
                
                markers = status.get('completion_markers', [])
                if markers:
                    print(f"   ✅ Completion Markers:")
                    for marker in markers:
                        print(f"      • {marker}")
                else:
                    print(f"   ⏳ No completion markers found")
                
                if status.get('ready_for_automation'):
                    print(f"   🚀 Status: READY FOR AUTOMATION")
                    ready_branches.append(team_name)
                else:
                    print(f"   🔄 Status: In Development")
                
                if status.get('commits_ahead', 0) > 0:
                    active_branches.append(team_name)
            
            print()
        
        # Summary
        print("🎯 DASHBOARD SUMMARY")
        print("=" * 30)
        print(f"📊 Teams monitored: {len(self.teams)}")
        print(f"🚀 Ready for automation: {len(ready_branches)}")
        print(f"🔥 Active development: {len(active_branches)}")
        
        if ready_branches:
            print(f"🎯 Ready teams: {', '.join(ready_branches)}")
        
        if active_branches:
            print(f"🔥 Active teams: {', '.join(active_branches)}")
        
        # Return to main branch
        subprocess.run(["git", "checkout", "main"], capture_output=True)
        
        return {
            "ready_branches": ready_branches,
            "active_branches": active_branches,
            "total_teams": len(self.teams)
        }
    
    def pull_from_branch(self, team_name: str) -> bool:
        """Pull latest changes from a specific team branch"""
        if team_name not in self.teams:
            print(f"❌ Team '{team_name}' not found")
            return False
        
        branch_name = self.teams[team_name]
        print(f"🔄 Pulling latest changes from {team_name} ({branch_name})")
        
        try:
            # Fetch latest
            subprocess.run(["git", "fetch", "origin"], check=True)
            
            # Checkout branch
            subprocess.run(["git", "checkout", branch_name], check=True)
            
            # Pull latest changes
            result = subprocess.run(["git", "pull", "origin", branch_name], 
                                  check=True, capture_output=True, text=True)
            
            print(f"✅ Successfully pulled from {team_name}")
            print(f"📝 {result.stdout}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error pulling from {team_name}: {e}")
            return False
    
    def run_automation_check(self) -> None:
        """Run the automation check from master codespace"""
        print("🤖 Running automation check...")
        try:
            result = subprocess.run(["python3", "simple_automation.py"], 
                                  capture_output=True, text=True, check=True)
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ Automation check failed: {e}")
            print(f"Error output: {e.stderr}")
    
    def sync_to_master_repo(self) -> None:
        """Sync current changes to master repository"""
        print("🔄 Syncing to master repository...")
        try:
            result = subprocess.run(["./sync_to_master.sh"], 
                                  capture_output=True, text=True, check=True)
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ Sync to master failed: {e}")
    
    def build_iso(self) -> None:
        """Build ISO from master codespace"""
        print("🏗️ Building ISO...")
        try:
            result = subprocess.run(["./build_iso.sh"], 
                                  capture_output=True, text=True, check=True)
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ ISO build failed: {e}")

def main():
    dashboard = MasterDevDashboard()
    
    print("🎯 Welcome to Master Dev Codespace!")
    print("Select an action:")
    print("1. 📊 Show full dashboard")
    print("2. 🔄 Pull from specific team")
    print("3. 🤖 Run automation check")
    print("4. 🔄 Sync to master repository")
    print("5. 🏗️ Build ISO")
    print("6. 🚪 Exit")
    
    while True:
        choice = input("\n👉 Enter your choice (1-6): ").strip()
        
        if choice == "1":
            dashboard.generate_team_dashboard()
        elif choice == "2":
            print("\nAvailable teams:")
            for i, team in enumerate(dashboard.teams.keys(), 1):
                print(f"{i}. {team}")
            team_choice = input("Enter team name: ").strip()
            dashboard.pull_from_branch(team_choice)
        elif choice == "3":
            dashboard.run_automation_check()
        elif choice == "4":
            dashboard.sync_to_master_repo()
        elif choice == "5":
            dashboard.build_iso()
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-6.")

if __name__ == "__main__":
    main()
