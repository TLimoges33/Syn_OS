#!/usr/bin/env python3
"""
Development Repository Completeness Analyzer
============================================

Compares the main Syn_OS repository with the dev-team repository to identify
missing essential development files and infrastructure components.

Author: Syn_OS Development Team
Date: August 2025
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

class RepositoryCompleteness:
    """Analyze repository completeness for development needs."""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.main_repo = "/home/diablorain/Syn_OS"
        self.dev_team_remote = "dev-team"
        
    def run_command(self, command, cwd=None):
        """Run a shell command and return the output."""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=cwd or self.main_repo
            )
            return result.stdout.strip(), result.returncode == 0
        except Exception as e:
            return f"Error: {e}", False
    
    def get_essential_files(self):
        """Identify essential development files in main repository."""
        
        print("🔍 SCANNING MAIN REPOSITORY FOR ESSENTIAL FILES")
        print("=" * 55)
        
        essential_patterns = {
            "Build System": [
                "Makefile",
                "Cargo.toml",
                "package.json",
                "requirements*.txt",
                "setup.py",
                "pyproject.toml"
            ],
            "Source Code": [
                "src/**/*.py",
                "src/**/*.rs", 
                "src/**/*.go",
                "src/**/*.js",
                "src/**/*.ts"
            ],
            "Testing Framework": [
                "tests/**/*.py",
                "tests/**/*.rs",
                "test_*.py",
                "*_test.py",
                "pytest.ini",
                "tox.ini"
            ],
            "Scripts & Tools": [
                "scripts/*.py",
                "scripts/*.sh",
                "tools/*.py",
                "build/*.py"
            ],
            "Configuration": [
                ".devcontainer/**/*",
                "config/**/*",
                "docker-compose.yml",
                "Dockerfile*",
                ".github/**/*"
            ],
            "Documentation": [
                "README.md",
                "docs/**/*.md",
                "*.md"
            ]
        }
        
        found_files = {}
        
        for category, patterns in essential_patterns.items():
            print(f"\n📂 {category}")
            print("-" * 25)
            
            category_files = []
            for pattern in patterns:
                command = f"find . -path './.git' -prune -o -path '{pattern}' -type f -print"
                output, success = self.run_command(command)
                
                if success and output:
                    files = [f for f in output.split('\n') if f.strip()]
                    category_files.extend(files)
            
            # Remove duplicates and sort
            category_files = sorted(list(set(category_files)))
            found_files[category] = category_files
            
            print(f"Found {len(category_files)} files:")
            for file in category_files[:10]:  # Show first 10
                print(f"  ✅ {file}")
            if len(category_files) > 10:
                print(f"  ... and {len(category_files) - 10} more")
        
        return found_files
    
    def check_dev_team_repo_structure(self):
        """Check what exists in the dev-team repository."""
        
        print(f"\n🏗️  CHECKING DEV-TEAM REPOSITORY STRUCTURE")
        print("=" * 45)
        
        # Fetch latest from dev-team
        print("📡 Fetching latest from dev-team repository...")
        self.run_command(f"git fetch {self.dev_team_remote}")
        
        # Get file list from dev-team/main
        command = f"git ls-tree -r --name-only {self.dev_team_remote}/main"
        output, success = self.run_command(command)
        
        if not success:
            print("❌ Unable to access dev-team repository structure")
            return []
        
        dev_team_files = output.split('\n') if output else []
        
        print(f"📊 Found {len(dev_team_files)} files in dev-team repository")
        
        # Categorize dev-team files
        dev_categories = {
            "Source Code": [],
            "Tests": [],
            "Scripts": [],
            "Configuration": [],
            "Documentation": [],
            "Build System": []
        }
        
        for file in dev_team_files:
            if not file.strip():
                continue
                
            if file.startswith('src/'):
                dev_categories["Source Code"].append(file)
            elif file.startswith('tests/') or 'test' in file:
                dev_categories["Tests"].append(file)
            elif file.startswith('scripts/') or file.endswith('.sh'):
                dev_categories["Scripts"].append(file)
            elif file.startswith('.devcontainer/') or file.startswith('config/'):
                dev_categories["Configuration"].append(file)
            elif file.endswith('.md') or file.startswith('docs/'):
                dev_categories["Documentation"].append(file)
            elif file in ['Makefile', 'Cargo.toml', 'package.json'] or 'requirements' in file:
                dev_categories["Build System"].append(file)
        
        print("\n📋 Dev-Team Repository Contents:")
        for category, files in dev_categories.items():
            print(f"\n{category} ({len(files)} files):")
            for file in files[:5]:  # Show first 5
                print(f"  ✅ {file}")
            if len(files) > 5:
                print(f"  ... and {len(files) - 5} more")
        
        return dev_team_files
    
    def identify_missing_essentials(self, main_files, dev_team_files):
        """Identify critical missing files for development."""
        
        print(f"\n🎯 IDENTIFYING MISSING DEVELOPMENT ESSENTIALS")
        print("=" * 50)
        
        critical_missing = []
        recommendations = []
        
        # Essential development files that should be copied
        essential_transfers = {
            "Build System": [
                "Makefile",
                "requirements-consciousness.txt",
                "src/*/Cargo.toml"
            ],
            "Core Scripts": [
                "scripts/validate-environment.sh",
                "scripts/setup-dev-env.sh", 
                "scripts/a_plus_security_audit.py",
                "scripts/setup-security.sh"
            ],
            "DevContainer": [
                ".devcontainer/devcontainer.json",
                ".devcontainer/scripts/post-create.sh",
                ".devcontainer/scripts/setup-environment.sh"
            ],
            "Testing Infrastructure": [
                "tests/comprehensive_test_framework.py",
                "tests/run_tests.py",
                "tests/test_error_handling.py"
            ],
            "Source Code Core": [
                "src/error_handling/",
                "src/consciousness/",
                "src/kernel/",
                "src/security/"
            ]
        }
        
        print("🔍 Analyzing missing critical components...")
        
        for category, items in essential_transfers.items():
            print(f"\n📦 {category}")
            print("-" * 30)
            
            missing_in_category = []
            
            for item in items:
                # Check if item exists in main repo
                if item.endswith('/'):
                    # Directory check
                    command = f"test -d {item}"
                    _, exists_main = self.run_command(command)
                else:
                    # File check (handle wildcards)
                    if '*' in item:
                        command = f"find . -path '{item}' -type f | head -1"
                        output, _ = self.run_command(command)
                        exists_main = bool(output.strip())
                    else:
                        command = f"test -f {item}"
                        _, exists_main = self.run_command(command)
                
                # Check if exists in dev-team
                exists_dev = any(item.replace('*', '') in f for f in dev_team_files)
                
                if exists_main and not exists_dev:
                    missing_in_category.append(item)
                    critical_missing.append((category, item))
                    print(f"  ❌ MISSING: {item}")
                elif exists_main and exists_dev:
                    print(f"  ✅ EXISTS: {item}")
                elif not exists_main:
                    print(f"  ⚠️  NOT IN MAIN: {item}")
        
        return critical_missing, recommendations
    
    def check_empty_files(self, dev_team_files):
        """Check for empty markdown files in dev-team repo."""
        
        print(f"\n📄 CHECKING FOR EMPTY DOCUMENTATION FILES")
        print("=" * 45)
        
        empty_files = []
        
        # Check specific files that are likely to be empty
        md_files = [f for f in dev_team_files if f.endswith('.md')]
        
        print(f"Found {len(md_files)} markdown files to check:")
        for md_file in md_files:
            print(f"  📝 {md_file}")
        
        # Since we can't directly check file contents in remote, 
        # we'll identify files that should have content
        expected_content_files = {
            "README.md": "Project overview and setup instructions",
            "docs/README.md": "Documentation navigation and structure",
            "SECURITY.md": "Security policies and procedures", 
            "CONTRIBUTING.md": "Contribution guidelines",
            "CHANGELOG.md": "Version history and changes",
            "docs/architecture/README.md": "System architecture documentation",
            "docs/development/README.md": "Development guidelines",
            "docs/api/README.md": "API documentation"
        }
        
        potentially_empty = []
        for expected_file, description in expected_content_files.items():
            if expected_file in md_files:
                potentially_empty.append((expected_file, description))
        
        if potentially_empty:
            print(f"\n⚠️  Files that may need content:")
            for file, desc in potentially_empty:
                print(f"  📝 {file}")
                print(f"     Should contain: {desc}")
        
        return potentially_empty
    
    def generate_transfer_plan(self, missing_essentials):
        """Generate a plan to transfer missing essentials."""
        
        print(f"\n🚀 DEVELOPMENT ESSENTIALS TRANSFER PLAN")
        print("=" * 45)
        
        if not missing_essentials:
            print("✅ No critical files missing - dev-team repo is complete!")
            return
        
        print(f"Found {len(missing_essentials)} critical items to transfer:")
        
        # Group by category
        transfer_by_category = {}
        for category, item in missing_essentials:
            if category not in transfer_by_category:
                transfer_by_category[category] = []
            transfer_by_category[category].append(item)
        
        transfer_commands = []
        
        for category, items in transfer_by_category.items():
            print(f"\n📦 {category} ({len(items)} items)")
            print("-" * 30)
            
            for item in items:
                print(f"  📋 {item}")
                
                # Generate transfer command
                if item.endswith('/'):
                    # Directory transfer
                    cmd = f"rsync -av {item} /tmp/dev_team_transfer/{item}"
                else:
                    # File transfer (handle wildcards)
                    if '*' in item:
                        cmd = f"find . -path '{item}' -exec cp {{}} /tmp/dev_team_transfer/ \\;"
                    else:
                        cmd = f"cp {item} /tmp/dev_team_transfer/{item}"
                
                transfer_commands.append(cmd)
        
        print(f"\n🔧 TRANSFER COMMANDS")
        print("-" * 20)
        print("# Create transfer directory")
        print("mkdir -p /tmp/dev_team_transfer")
        print()
        
        for cmd in transfer_commands[:10]:  # Show first 10 commands
            print(f"# Transfer command")
            print(cmd)
            print()
        
        if len(transfer_commands) > 10:
            print(f"... and {len(transfer_commands) - 10} more commands")
        
        return transfer_commands
    
    def run_analysis(self):
        """Run complete repository completeness analysis."""
        
        print("🔬 DEVELOPMENT REPOSITORY COMPLETENESS ANALYSIS")
        print("=" * 60)
        print(f"Generated: {self.timestamp}")
        print(f"Main Repository: {self.main_repo}")
        print(f"Dev-Team Remote: {self.dev_team_remote}")
        print()
        
        # 1. Scan main repository for essential files
        main_files = self.get_essential_files()
        
        # 2. Check dev-team repository structure
        dev_team_files = self.check_dev_team_repo_structure()
        
        # 3. Identify missing essentials
        missing_essentials, recommendations = self.identify_missing_essentials(main_files, dev_team_files)
        
        # 4. Check for empty files
        empty_files = self.check_empty_files(dev_team_files)
        
        # 5. Generate transfer plan
        transfer_commands = self.generate_transfer_plan(missing_essentials)
        
        # Final Summary
        print(f"\n🎯 ANALYSIS SUMMARY")
        print("=" * 20)
        print(f"📊 Main Repository Files Scanned: {sum(len(files) for files in main_files.values())}")
        print(f"📊 Dev-Team Repository Files: {len(dev_team_files)}")
        print(f"❌ Critical Missing Items: {len(missing_essentials)}")
        print(f"📝 Potentially Empty Files: {len(empty_files)}")
        
        if missing_essentials:
            print(f"\n⚠️  IMMEDIATE ACTION NEEDED:")
            print(f"   • Transfer {len(missing_essentials)} critical development files")
            print(f"   • Update documentation content")
            print(f"   • Verify build system functionality")
        else:
            print(f"\n✅ DEVELOPMENT REPOSITORY STATUS: COMPLETE")
            print(f"   • All critical files present")
            print(f"   • Ready for development")
        
        return {
            "missing_essentials": missing_essentials,
            "empty_files": empty_files,
            "transfer_commands": transfer_commands,
            "status": "NEEDS_TRANSFER" if missing_essentials else "COMPLETE"
        }

if __name__ == "__main__":
    analyzer = RepositoryCompleteness()
    result = analyzer.run_analysis()
