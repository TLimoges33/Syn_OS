#!/usr/bin/env python3
"""
Comprehensive SynOS Workspace Audit Tool
Performs complete codebase organization and optimization audit
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

class SynOSWorkspaceAuditor:
    def __init__(self, workspace_root="/home/diablorain/Syn_OS"):
        self.workspace_root = Path(workspace_root)
        self.audit_results = {
            "timestamp": datetime.now().isoformat(),
            "workspace_root": str(self.workspace_root),
            "summary": {},
            "issues": [],
            "recommendations": [],
            "directory_structure": {},
            "file_analysis": {},
            "optimization_opportunities": []
        }
        
    def audit_directory_structure(self):
        """Audit the overall directory structure for organization and consistency"""
        print("🔍 Auditing directory structure...")
        
        expected_top_level = {
            "src", "core", "docs", "tests", "scripts",
            "development", "infrastructure", "security", "integration", "operations",
            "config", "deploy", "deployment", "docker", "assets", "archive", "reports", "results"
        }
        
        actual_dirs = {d.name for d in self.workspace_root.iterdir() if d.is_dir()}
        
        # Check for proper organization
        self.audit_results["directory_structure"] = {
            "expected_top_level": list(expected_top_level),
            "actual_top_level": list(actual_dirs),
            "missing_expected": list(expected_top_level - actual_dirs),
            "unexpected_dirs": list(actual_dirs - expected_top_level)
        }
        
        # Analyze each major directory
        for directory in actual_dirs:
            dir_path = self.workspace_root / directory
            if dir_path.is_dir():
                self.audit_results["directory_structure"][directory] = {
                    "file_count": len(list(dir_path.rglob("*"))),
                    "subdirs": [d.name for d in dir_path.iterdir() if d.is_dir()],
                    "size_analysis": self._analyze_directory_size(dir_path)
                }
    
    def audit_file_organization(self):
        """Audit file organization and identify potential issues"""
        print("📁 Auditing file organization...")
        
        file_analysis = {
            "duplicates": [],
            "large_files": [],
            "orphaned_files": [],
            "misplaced_files": [],
            "empty_files": [],
            "config_files": [],
            "documentation_files": []
        }
        
        # Analyze all files
        for file_path in self.workspace_root.rglob("*"):
            if file_path.is_file():
                self._analyze_file(file_path, file_analysis)
        
        # Check for duplicate names
        file_names = defaultdict(list)
        for file_path in self.workspace_root.rglob("*"):
            if file_path.is_file():
                file_names[file_path.name].append(str(file_path))
        
        file_analysis["duplicates"] = {
            name: paths for name, paths in file_names.items() 
            if len(paths) > 1 and not self._is_acceptable_duplicate(name)
        }
        
        self.audit_results["file_analysis"] = file_analysis
    
    def audit_configuration_consistency(self):
        """Audit configuration files for consistency"""
        print("⚙️ Auditing configuration consistency...")
        
        config_files = {
            ".gitignore": self.workspace_root / ".gitignore",
            "CODEOWNERS": self.workspace_root / "CODEOWNERS",
            "Cargo.toml": self.workspace_root / "Cargo.toml",
            "workspace": self.workspace_root / "SynOS-Focused.code-workspace",
            "tasks.json": self.workspace_root / ".vscode" / "tasks.json"
        }
        
        consistency_issues = []
        
        for config_name, config_path in config_files.items():
            if config_path.exists():
                content = config_path.read_text()
                issues = self._check_config_consistency(config_name, content)
                if issues:
                    consistency_issues.extend(issues)
        
        self.audit_results["configuration_consistency"] = consistency_issues
    
    def audit_documentation_organization(self):
        """Audit documentation structure and completeness"""
        print("📚 Auditing documentation organization...")
        
        docs_dir = self.workspace_root / "docs"
        doc_structure = {}
        doc_issues = []
        
        if docs_dir.exists():
            # Check expected structure
            expected_sections = ["01-getting-started", "02-architecture", "03-development", 
                               "04-deployment", "05-operations", "06-reference"]
            
            actual_sections = [d.name for d in docs_dir.iterdir() if d.is_dir()]
            
            doc_structure = {
                "expected": expected_sections,
                "actual": actual_sections,
                "missing": [s for s in expected_sections if s not in actual_sections],
                "extra": [s for s in actual_sections if s not in expected_sections and s != "archive"]
            }
            
            # Check for README files
            for section in actual_sections:
                section_path = docs_dir / section
                if not (section_path / "README.md").exists():
                    doc_issues.append(f"Missing README.md in {section}")
        
        self.audit_results["documentation"] = {
            "structure": doc_structure,
            "issues": doc_issues
        }
    
    def audit_development_readiness(self):
        """Audit development environment readiness"""
        print("🚀 Auditing development environment readiness...")
        
        readiness_checks = {
            "rust_project": (self.workspace_root / "Cargo.toml").exists(),
            "kernel_source": (self.workspace_root / "src" / "kernel").exists(),
            "core_libraries": (self.workspace_root / "core").exists(),
            "development_tools": (self.workspace_root / "development").exists(),
            "security_framework": (self.workspace_root / "security").exists(),
            "infrastructure": (self.workspace_root / "infrastructure").exists(),
            "integration_tools": (self.workspace_root / "integration").exists(),
            "operations_tools": (self.workspace_root / "operations").exists(),
            "documentation": (self.workspace_root / "docs").exists(),
            "testing_framework": (self.workspace_root / "tests").exists()
        }
        
        development_issues = []
        for check, status in readiness_checks.items():
            if not status:
                development_issues.append(f"Missing or misconfigured: {check}")
        
        self.audit_results["development_readiness"] = {
            "checks": readiness_checks,
            "issues": development_issues,
            "score": sum(readiness_checks.values()) / len(readiness_checks) * 100
        }
    
    def generate_optimization_recommendations(self):
        """Generate specific optimization recommendations"""
        print("💡 Generating optimization recommendations...")
        
        recommendations = []
        
        # Directory structure recommendations
        if self.audit_results["directory_structure"]["unexpected_dirs"]:
            recommendations.append({
                "type": "structure",
                "priority": "medium",
                "issue": "Unexpected top-level directories",
                "recommendation": f"Consider reorganizing: {self.audit_results['directory_structure']['unexpected_dirs']}"
            })
        
        # File organization recommendations
        if self.audit_results["file_analysis"]["duplicates"]:
            recommendations.append({
                "type": "files",
                "priority": "high",
                "issue": "Duplicate files detected",
                "recommendation": "Review and consolidate duplicate files"
            })
        
        # Configuration consistency recommendations
        if self.audit_results["configuration_consistency"]:
            recommendations.append({
                "type": "configuration",
                "priority": "high",
                "issue": "Configuration inconsistencies",
                "recommendation": "Update configuration files to match current structure"
            })
        
        # Development readiness recommendations
        if self.audit_results["development_readiness"]["score"] < 100:
            recommendations.append({
                "type": "development",
                "priority": "high",
                "issue": "Development environment incomplete",
                "recommendation": "Address missing development components"
            })
        
        self.audit_results["recommendations"] = recommendations
    
    def _analyze_directory_size(self, dir_path):
        """Analyze directory size and file distribution"""
        files = list(dir_path.rglob("*"))
        total_files = len([f for f in files if f.is_file()])
        total_dirs = len([f for f in files if f.is_dir()])
        
        return {
            "total_files": total_files,
            "total_directories": total_dirs,
            "depth": len(dir_path.parts) - len(self.workspace_root.parts)
        }
    
    def _analyze_file(self, file_path, analysis):
        """Analyze individual file for issues"""
        try:
            stat = file_path.stat()
            size = stat.st_size
            
            # Large files (>10MB)
            if size > 10 * 1024 * 1024:
                analysis["large_files"].append({
                    "path": str(file_path),
                    "size": size
                })
            
            # Empty files
            if size == 0:
                analysis["empty_files"].append(str(file_path))
            
            # Configuration files
            if file_path.suffix in [".toml", ".json", ".yaml", ".yml", ".conf", ".cfg"]:
                analysis["config_files"].append(str(file_path))
            
            # Documentation files
            if file_path.suffix in [".md", ".rst", ".txt"] and "README" not in file_path.name:
                analysis["documentation_files"].append(str(file_path))
                
        except (OSError, PermissionError):
            pass
    
    def _is_acceptable_duplicate(self, filename):
        """Check if duplicate filename is acceptable"""
        acceptable = [
            "README.md", "Cargo.toml", "requirements.txt", "package.json",
            ".gitignore", "Dockerfile", "docker-compose.yml", "Makefile"
        ]
        return filename in acceptable
    
    def _check_config_consistency(self, config_name, content):
        """Check configuration file for consistency issues"""
        issues = []
        
        if config_name == ".gitignore":
            # Check for outdated patterns
            if "tools/" in content and "development/" not in content:
                issues.append("gitignore: Missing new directory patterns")
        
        elif config_name == "CODEOWNERS":
            # Check for outdated paths
            if "/tools/" in content:
                issues.append("CODEOWNERS: Contains outdated path references")
        
        return issues
    
    def generate_summary(self):
        """Generate audit summary"""
        total_issues = (
            len(self.audit_results.get("configuration_consistency", [])) +
            len(self.audit_results.get("documentation", {}).get("issues", [])) +
            len(self.audit_results.get("development_readiness", {}).get("issues", [])) +
            len(self.audit_results.get("file_analysis", {}).get("duplicates", {}))
        )
        
        self.audit_results["summary"] = {
            "total_issues": total_issues,
            "organization_score": self._calculate_organization_score(),
            "readiness_score": self.audit_results.get("development_readiness", {}).get("score", 0),
            "status": "excellent" if total_issues == 0 else "good" if total_issues < 5 else "needs_improvement"
        }
    
    def _calculate_organization_score(self):
        """Calculate overall organization score"""
        scores = []
        
        # Directory structure score
        expected = len(self.audit_results["directory_structure"]["expected_top_level"])
        actual_good = expected - len(self.audit_results["directory_structure"]["missing_expected"])
        scores.append(actual_good / expected * 100)
        
        # Configuration consistency score
        config_issues = len(self.audit_results.get("configuration_consistency", []))
        scores.append(max(0, 100 - config_issues * 20))
        
        # Documentation score
        doc_issues = len(self.audit_results.get("documentation", {}).get("issues", []))
        scores.append(max(0, 100 - doc_issues * 10))
        
        return sum(scores) / len(scores)
    
    def run_audit(self):
        """Run complete workspace audit"""
        print("🔍 Starting comprehensive SynOS workspace audit...")
        print(f"Workspace: {self.workspace_root}")
        print("=" * 50)
        
        self.audit_directory_structure()
        self.audit_file_organization()
        self.audit_configuration_consistency()
        self.audit_documentation_organization()
        self.audit_development_readiness()
        self.generate_optimization_recommendations()
        self.generate_summary()
        
        print("=" * 50)
        print("✅ Audit complete!")
        
        return self.audit_results
    
    def save_report(self, output_path="workspace-audit-report.json"):
        """Save audit report to file"""
        output_file = self.workspace_root / output_path
        with open(output_file, 'w') as f:
            json.dump(self.audit_results, f, indent=2)
        print(f"📄 Report saved to: {output_file}")
        return output_file

def main():
    auditor = SynOSWorkspaceAuditor()
    results = auditor.run_audit()
    
    # Print summary
    print("\n📊 AUDIT SUMMARY")
    print("=" * 30)
    summary = results["summary"]
    print(f"Overall Status: {summary['status'].upper()}")
    print(f"Organization Score: {summary['organization_score']:.1f}/100")
    print(f"Development Readiness: {summary['readiness_score']:.1f}/100")
    print(f"Total Issues: {summary['total_issues']}")
    
    # Print key recommendations
    if results["recommendations"]:
        print("\n🚨 KEY RECOMMENDATIONS")
        print("=" * 30)
        for rec in results["recommendations"][:5]:  # Top 5
            print(f"• [{rec['priority'].upper()}] {rec['issue']}: {rec['recommendation']}")
    
    # Save detailed report
    report_file = auditor.save_report()
    
    return results

if __name__ == "__main__":
    main()
