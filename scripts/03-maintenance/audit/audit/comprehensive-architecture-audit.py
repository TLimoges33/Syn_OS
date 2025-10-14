#!/usr/bin/env python3
"""
Comprehensive Architecture Audit Script
Analyzes SynOS structure for optimization opportunities
"""

import os
import json
from pathlib import Path
from collections import defaultdict, Counter
import re

class ArchitectureAuditor:
    def __init__(self, root_path="/home/diablorain/Syn_OS"):
        self.root_path = Path(root_path)
        self.audit_results = {
            "folders": {},
            "patterns": {},
            "redundancies": [],
            "optimization_opportunities": [],
            "proposed_structure": {}
        }
        
    def analyze_folder_structure(self):
        """Analyze current folder structure and contents"""
        folders_to_audit = [
            "tools", "implementation", "mcp_servers", "prototypes", 
            "security/audit", "src", "services", "scripts", "tests"
        ]
        
        for folder in folders_to_audit:
            folder_path = self.root_path / folder
            if folder_path.exists():
                self.audit_results["folders"][folder] = self._analyze_folder(folder_path)
    
    def _analyze_folder(self, folder_path):
        """Analyze individual folder"""
        analysis = {
            "total_files": 0,
            "file_types": Counter(),
            "subdirectories": [],
            "purposes": [],
            "potential_moves": []
        }
        
        for item in folder_path.rglob("*"):
            if item.is_file():
                analysis["total_files"] += 1
                analysis["file_types"][item.suffix] += 1
                
                # Analyze file purpose
                purpose = self._determine_file_purpose(item)
                if purpose:
                    analysis["purposes"].append(purpose)
            elif item.is_dir() and item != folder_path:
                rel_path = item.relative_to(folder_path)
                analysis["subdirectories"].append(str(rel_path))
        
        return analysis
    
    def _determine_file_purpose(self, file_path):
        """Determine the purpose of a file based on name and content"""
        name = file_path.name.lower()
        parent = file_path.parent.name.lower()
        
        # Security patterns
        if any(keyword in name for keyword in ['security', 'audit', 'auth', 'crypto', 'ssl', 'tls']):
            return 'security'
        
        # Testing patterns
        if any(keyword in name for keyword in ['test', 'spec', 'benchmark', 'mock']):
            return 'testing'
        
        # Build patterns
        if any(keyword in name for keyword in ['build', 'compile', 'make', 'cargo', 'iso']):
            return 'build'
        
        # Consciousness patterns
        if any(keyword in name for keyword in ['consciousness', 'neural', 'ai', 'quantum']):
            return 'consciousness'
        
        # Deployment patterns
        if any(keyword in name for keyword in ['deploy', 'docker', 'k8s', 'kube']):
            return 'deployment'
        
        # Monitoring patterns
        if any(keyword in name for keyword in ['monitor', 'metrics', 'log', 'trace']):
            return 'monitoring'
        
        return 'general'
    
    def find_redundancies(self):
        """Find redundant files and patterns"""
        
        # Find duplicate functionality
        security_files = []
        test_files = []
        build_files = []
        
        for folder_name, folder_data in self.audit_results["folders"].items():
            for purpose in folder_data["purposes"]:
                if purpose == 'security':
                    security_files.append(f"{folder_name}")
                elif purpose == 'testing':
                    test_files.append(f"{folder_name}")
                elif purpose == 'build':
                    build_files.append(f"{folder_name}")
        
        if len(set(security_files)) > 1:
            self.audit_results["redundancies"].append({
                "type": "security_scattered",
                "folders": list(set(security_files)),
                "description": "Security functionality scattered across multiple folders"
            })
        
        if len(set(test_files)) > 1:
            self.audit_results["redundancies"].append({
                "type": "testing_scattered", 
                "folders": list(set(test_files)),
                "description": "Testing functionality scattered across multiple folders"
            })
    
    def propose_optimizations(self):
        """Propose optimization opportunities"""
        
        # Analyze tools folder overload
        tools_files = self.audit_results["folders"].get("tools", {}).get("total_files", 0)
        if tools_files > 500:
            self.audit_results["optimization_opportunities"].append({
                "type": "tools_reorganization",
                "priority": "high", 
                "description": f"Tools folder contains {tools_files} files - needs subcategorization",
                "proposed_action": "Split into logical subcategories: development/, production/, security/, monitoring/"
            })
        
        # Analyze small folders that could be consolidated
        small_folders = []
        for folder, data in self.audit_results["folders"].items():
            if data["total_files"] < 5 and folder not in ["src", "services"]:
                small_folders.append(folder)
        
        if small_folders:
            self.audit_results["optimization_opportunities"].append({
                "type": "small_folder_consolidation",
                "priority": "medium",
                "description": f"Small folders could be consolidated: {small_folders}",
                "proposed_action": "Consider merging into logical parent folders"
            })
        
        # Analyze security distribution
        security_folders = [f for f, data in self.audit_results["folders"].items() 
                          if 'security' in data["purposes"]]
        if len(security_folders) > 2:
            self.audit_results["optimization_opportunities"].append({
                "type": "security_consolidation",
                "priority": "high",
                "description": f"Security files scattered across: {security_folders}",
                "proposed_action": "Consolidate security tools under /security/ or /tools/security/"
            })
    
    def propose_new_structure(self):
        """Propose new optimized structure"""
        self.audit_results["proposed_structure"] = {
            "core/": {
                "description": "Core SynOS components (kernel, consciousness, services)",
                "contents": ["src/kernel/", "src/consciousness/", "core/"]
            },
            "development/": {
                "description": "All development tools and utilities", 
                "contents": [
                    "tools/dev-utils/", "tools/cli/", "tools/generators/",
                    "implementation/", "prototypes/"
                ]
            },
            "infrastructure/": {
                "description": "Build, deployment, and operations",
                "contents": [
                    "tools/build-system/", "services/", "deployment/",
                    "tools/monitoring/", "scripts/"
                ]
            },
            "security/": {
                "description": "All security-related tools and audits",
                "contents": [
                    "tools/security/", "security/audit/", "src/security/"
                ]
            },
            "testing/": {
                "description": "Comprehensive testing framework",
                "contents": ["tests/", "tools/testing/"]
            },
            "integration/": {
                "description": "System integrations and connectors",
                "contents": [
                    "mcp_servers/", "tools/integrations/", 
                    "tools/github-curator/"
                ]
            }
        }
    
    def generate_report(self):
        """Generate comprehensive audit report"""
        self.analyze_folder_structure()
        self.find_redundancies()
        self.propose_optimizations()
        self.propose_new_structure()
        
        # Save detailed results
        report_path = self.root_path / "ARCHITECTURE_AUDIT_REPORT.json"
        with open(report_path, 'w') as f:
            json.dump(self.audit_results, f, indent=2, default=str)
        
        # Generate human-readable summary
        self._generate_summary_report()
        
        return self.audit_results
    
    def _generate_summary_report(self):
        """Generate human-readable summary"""
        summary_path = self.root_path / "ARCHITECTURE_OPTIMIZATION_PLAN.md"
        
        with open(summary_path, 'w') as f:
            f.write("# 🏗️ SynOS Architecture Optimization Plan\n\n")
            
            f.write("## 📊 Current Structure Analysis\n\n")
            f.write("| Folder | Files | Key Purpose | Status |\n")
            f.write("|--------|--------|-------------|--------|\n")
            
            for folder, data in self.audit_results["folders"].items():
                file_count = data["total_files"]
                main_purpose = max(set(data["purposes"]), key=data["purposes"].count) if data["purposes"] else "mixed"
                status = "✅ Organized" if file_count < 50 else "⚠️ Needs Review" if file_count < 200 else "🚨 Overloaded"
                f.write(f"| `{folder}` | {file_count} | {main_purpose} | {status} |\n")
            
            f.write("\n## 🎯 Optimization Opportunities\n\n")
            for i, opportunity in enumerate(self.audit_results["optimization_opportunities"], 1):
                priority_emoji = "🔴" if opportunity["priority"] == "high" else "🟡" if opportunity["priority"] == "medium" else "🟢"
                f.write(f"### {i}. {opportunity['type'].replace('_', ' ').title()} {priority_emoji}\n\n")
                f.write(f"**Description:** {opportunity['description']}\n\n")
                f.write(f"**Proposed Action:** {opportunity['proposed_action']}\n\n")
            
            f.write("## 🏗️ Proposed New Structure\n\n")
            for folder, details in self.audit_results["proposed_structure"].items():
                f.write(f"### `{folder}`\n")
                f.write(f"{details['description']}\n\n")
                f.write("**Contents:**\n")
                for content in details['contents']:
                    f.write(f"- {content}\n")
                f.write("\n")
            
            f.write("## 📋 Implementation Priority\n\n")
            f.write("1. **High Priority:** Tools folder reorganization, Security consolidation\n")
            f.write("2. **Medium Priority:** Small folder consolidation, Testing unification\n") 
            f.write("3. **Low Priority:** Documentation restructuring, Asset optimization\n\n")

if __name__ == "__main__":
    auditor = ArchitectureAuditor()
    results = auditor.generate_report()
    
    print("🎯 Architecture Audit Complete!")
    print(f"📊 Analyzed {len(results['folders'])} folders")
    print(f"🔍 Found {len(results['redundancies'])} redundancy patterns")
    print(f"⚡ Identified {len(results['optimization_opportunities'])} optimization opportunities")
    print("\n📋 Reports generated:")
    print("- ARCHITECTURE_AUDIT_REPORT.json (detailed data)")
    print("- ARCHITECTURE_OPTIMIZATION_PLAN.md (human-readable)")
