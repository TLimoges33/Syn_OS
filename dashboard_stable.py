#!/usr/bin/env python3
"""
🎯 Stable Master Dev Dashboard for Codespaces
Lightweight version to avoid extension host issues
"""

import subprocess
import sys
import os
from datetime import datetime

class StableMasterDashboard:
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
        self.public_repos = {
            "docs": "https://github.com/TLimoges33/SynapticOS-Docs.git"
        }
    
    def safe_git_command(self, cmd):
        """Execute git command safely with error handling"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None
    
    def get_team_status(self):
        """Get simple status of all teams"""
        print("🎯 MASTER DEV DASHBOARD - STABLE VERSION")
        print("=" * 50)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Fetch latest safely
        print("📡 Fetching updates...")
        self.safe_git_command("git fetch origin --quiet")
        
        active_teams = []
        
        for team_name, branch_name in self.teams.items():
            print(f"📋 {team_name} Team")
            print("-" * 30)
            
            # Check if branch exists
            branch_exists = self.safe_git_command(f"git ls-remote --heads origin {branch_name}")
            
            if branch_exists:
                # Get latest commit info
                commit_info = self.safe_git_command(f"git log origin/{branch_name} -1 --pretty=format:'%h|%an|%s|%cr' 2>/dev/null")
                
                if commit_info:
                    try:
                        hash_val, author, message, time_ago = commit_info.split("|", 3)
                        print(f"   📍 Latest: {hash_val}")
                        print(f"   👤 Author: {author}")
                        print(f"   📝 Message: {message[:50]}...")
                        print(f"   ⏰ Time: {time_ago}")
                        
                        # Check for completion markers
                        markers = ["🎯 Phase Implementation Complete", "✅ Ready for Integration", "🧪 All Tests Passing"]
                        found_markers = [m for m in markers if m in message]
                        
                        if found_markers:
                            print(f"   🚀 Status: READY FOR AUTOMATION")
                            active_teams.append(team_name)
                        else:
                            print(f"   🔄 Status: In Development")
                    except:
                        print("   ❌ Error parsing commit info")
                else:
                    print("   ❌ No commits found")
            else:
                print("   ❌ Branch not found")
            
            print()
        
        print("🎯 SUMMARY")
        print("=" * 20)
        print(f"📊 Teams monitored: {len(self.teams)}")
        print(f"🚀 Ready for automation: {len(active_teams)}")
        if active_teams:
            print(f"🎯 Ready teams: {', '.join(active_teams)}")
        
        # Show repository status
        print()
        self.show_repository_status()
        
        return active_teams
    
    def check_docs_sync(self):
        """Check documentation sync status"""
        print("📚 DOCUMENTATION SYNC STATUS:")
        print("=" * 35)
        
        # Check if sync workflow exists
        sync_workflow = "test -f .github/workflows/sync-to-docs.yml"
        workflow_exists = self.safe_git_command(sync_workflow)
        
        if workflow_exists is not None:
            print("✅ Sync workflow configured")
        else:
            print("⚠️  Sync workflow missing")
        
        # Check public documentation files
        public_files = ["docs/PUBLIC_README.md", "docs/PUBLIC_API.md"]
        for file_path in public_files:
            file_exists = self.safe_git_command(f"test -f {file_path}")
            if file_exists is not None:
                print(f"✅ {file_path} ready")
            else:
                print(f"📝 {file_path} needs creation")
        
        # Check documentation repository status
        docs_status = self.safe_git_command(f"git ls-remote {self.public_repos['docs']} HEAD")
        if docs_status:
            commit_hash = docs_status.split('\t')[0][:8] if docs_status else "unknown"
            print(f"✅ Docs repository active (latest: {commit_hash})")
        else:
            print("⚠️  Docs repository access issue")
        
        print()
        print("🌐 Public Repository:")
        print("   https://github.com/TLimoges33/SynapticOS-Docs")
        print("🔄 Auto-sync: Enabled on dev-team commits")
    
    def show_repository_status(self):
        """Show status of all repositories"""
        print("🌐 REPOSITORY STATUS:")
        print("=" * 25)
        
        # Dev team repository
        dev_status = self.safe_git_command("git status --porcelain")
        if dev_status is not None:
            if dev_status:
                print("📝 Dev-Team: Local changes pending")
            else:
                print("✅ Dev-Team: Clean working directory")
        else:
            print("⚠️  Dev-Team: Status check failed")
        
        # Documentation repository
        docs_remote = self.safe_git_command(f"git ls-remote {self.public_repos['docs']} HEAD")
        if docs_remote:
            print("✅ Documentation: Repository accessible")
        else:
            print("⚠️  Documentation: Access issue")
        
        print()
        """Show available commands"""
        print("\n🎮 AVAILABLE COMMANDS:")
        print("=" * 30)
        print("📊 dashboard         - Show team status")
        print("🌿 teams            - List feature branches")
        print("� docs             - Check documentation sync")
        print("�🔧 recovery         - Fix codespace issues")
        print("📚 help             - Show this help")
        print("🚪 exit             - Exit dashboard")
    
    def run_recovery(self):
        """Run recovery script"""
        print("🔧 Running codespace recovery...")
        result = subprocess.run(["bash", "fix_codespace_issues.sh", "all"], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"❌ Recovery script error: {result.stderr}")
        else:
            print("✅ Recovery completed!")
    
    def list_teams(self):
        """List all team branches"""
        print("🌿 DEVELOPMENT TEAMS:")
        print("=" * 25)
        for team_name, branch_name in self.teams.items():
            print(f"📋 {team_name:<15} → {branch_name}")

def main():
    dashboard = StableMasterDashboard()
    
    print("🎯 Welcome to Stable Master Dev Dashboard!")
    print("Optimized for Codespace stability")
    print()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "status":
            dashboard.get_team_status()
        elif command == "teams":
            dashboard.list_teams()
        elif command == "docs":
            dashboard.check_docs_sync()
        elif command == "recovery":
            dashboard.run_recovery()
        elif command == "help":
            dashboard.show_commands()
        else:
            print(f"❌ Unknown command: {command}")
            dashboard.show_commands()
        return
    
    while True:
        print("\n" + "="*40)
        print("1. 📊 Show team status")
        print("2. 🌿 List teams")
        print("3. � Check documentation sync")
        print("4. �🔧 Run recovery")
        print("5. 📚 Show commands")
        print("6. 🚪 Exit")
        
        try:
            choice = input("\n👉 Enter choice (1-6): ").strip()
            
            if choice == "1":
                dashboard.get_team_status()
            elif choice == "2":
                dashboard.list_teams()
            elif choice == "3":
                dashboard.check_docs_sync()
            elif choice == "4":
                dashboard.run_recovery()
            elif choice == "5":
                dashboard.show_commands()
            elif choice == "6":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("🔧 Try running recovery: python3 dashboard_stable.py recovery")

if __name__ == "__main__":
    main()
