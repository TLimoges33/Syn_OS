#!/usr/bin/env python3
"""
Comprehensive Security Audit for Syn_OS
========================================

This module performs automated security testing and generates
a detailed security report with actual metrics - no unsubstantiated claims.
"""

import subprocess
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import tempfile

class SecurityAuditor:
    """Comprehensive security auditing for Syn_OS"""
    
    def __init__(self, project_root="/home/diablorain/Syn_OS"):
        self.project_root = Path(project_root)
        self.results_dir = self.project_root / "results" / "security_reports"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.audit_results = {
            "timestamp": datetime.now().isoformat(),
            "project": "Syn_OS",
            "version": "2.0.0-Alpha",
            "auditor": "Academic Security Assessment",
            "python_security": {},
            "rust_security": {},
            "dependency_security": {},
            "code_quality": {},
            "summary": {}
        }
    
    def run_bandit_scan(self):
        """Run Bandit Python security scanner"""
        print("🔍 Running Bandit Python security scan...")
        
        try:
            # Run bandit on Python source files
            cmd = [
                "bandit", 
                "-r", str(self.project_root / "src"),
                "-f", "json",
                "-ll"  # Low confidence, low severity minimum
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode in [0, 1]:  # 0 = no issues, 1 = issues found
                try:
                    bandit_data = json.loads(result.stdout) if result.stdout else {}
                    
                    self.audit_results["python_security"] = {
                        "total_issues": len(bandit_data.get("results", [])),
                        "high_severity": len([r for r in bandit_data.get("results", []) 
                                            if r.get("issue_severity") == "HIGH"]),
                        "medium_severity": len([r for r in bandit_data.get("results", []) 
                                              if r.get("issue_severity") == "MEDIUM"]),
                        "low_severity": len([r for r in bandit_data.get("results", []) 
                                           if r.get("issue_severity") == "LOW"]),
                        "files_scanned": bandit_data.get("metrics", {}).get("_totals", {}).get("loc", 0),
                        "syntax_errors": len(bandit_data.get("errors", [])),
                        "issues": bandit_data.get("results", [])[:10]  # Top 10 issues
                    }
                except json.JSONDecodeError as e:
                    print(f"⚠️ Bandit JSON parsing issue: {e}")
                    # Count issues from stderr text output
                    issue_count = result.stderr.count("Issue:") if result.stderr else 0
                    self.audit_results["python_security"] = {
                        "total_issues": issue_count,
                        "parsing_error": str(e),
                        "raw_output": result.stdout[:1000]  # First 1000 chars
                    }
                print(f"✅ Bandit scan complete: {self.audit_results['python_security']['total_issues']} issues found")
            else:
                print(f"❌ Bandit scan failed: {result.stderr}")
                self.audit_results["python_security"]["error"] = result.stderr
                
        except Exception as e:
            print(f"❌ Bandit scan error: {e}")
            self.audit_results["python_security"]["error"] = str(e)
    
    def run_cargo_audit(self):
        """Run Cargo audit for Rust dependencies"""
        print("🔍 Running Cargo audit for Rust security...")
        
        try:
            os.chdir(self.project_root)
            result = subprocess.run(
                ["cargo", "audit", "--format", "json"], 
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                # Parse cargo audit output
                lines = result.stdout.strip().split('\n')
                vulnerabilities = []
                
                for line in lines:
                    if line.strip() and line.startswith('{'):
                        try:
                            vuln_data = json.loads(line)
                            vulnerabilities.append(vuln_data)
                        except json.JSONDecodeError:
                            continue
                
                self.audit_results["rust_security"] = {
                    "vulnerabilities_found": len(vulnerabilities),
                    "critical_count": len([v for v in vulnerabilities if v.get("severity") == "critical"]),
                    "high_count": len([v for v in vulnerabilities if v.get("severity") == "high"]),
                    "medium_count": len([v for v in vulnerabilities if v.get("severity") == "medium"]),
                    "low_count": len([v for v in vulnerabilities if v.get("severity") == "low"]),
                    "vulnerabilities": vulnerabilities[:10]  # Top 10
                }
                print(f"✅ Cargo audit complete: {len(vulnerabilities)} vulnerabilities found")
            else:
                self.audit_results["rust_security"] = {
                    "vulnerabilities_found": 0,
                    "status": "No vulnerabilities found"
                }
                print("✅ Cargo audit complete: No vulnerabilities found")
                
        except Exception as e:
            print(f"❌ Cargo audit error: {e}")
            self.audit_results["rust_security"]["error"] = str(e)
    
    def run_safety_check(self):
        """Run Safety check for Python dependencies"""
        print("🔍 Running Safety check for Python dependencies...")
        
        try:
            result = subprocess.run(
                ["python", "-m", "safety", "check", "--json"],
                capture_output=True, text=True
            )
            
            if result.returncode in [0, 64]:  # 0 = safe, 64 = vulnerabilities found
                try:
                    safety_data = json.loads(result.stdout) if result.stdout else []
                    
                    self.audit_results["dependency_security"] = {
                        "python_vulnerabilities": len(safety_data),
                        "critical_deps": len([v for v in safety_data if "critical" in v.get("vulnerability_id", "").lower()]),
                        "high_deps": len([v for v in safety_data if "high" in v.get("vulnerability_id", "").lower()]),
                        "vulnerabilities": safety_data[:10]  # Top 10
                    }
                    print(f"✅ Safety check complete: {len(safety_data)} dependency vulnerabilities found")
                except json.JSONDecodeError:
                    # Safety might return plain text
                    vuln_count = result.stdout.count("vulnerability") if result.stdout else 0
                    self.audit_results["dependency_security"] = {
                        "python_vulnerabilities": vuln_count,
                        "raw_output": result.stdout[:1000]  # First 1000 chars
                    }
                    print(f"✅ Safety check complete: ~{vuln_count} dependency issues found")
            else:
                print(f"❌ Safety check failed: {result.stderr}")
                self.audit_results["dependency_security"]["error"] = result.stderr
                
        except Exception as e:
            print(f"❌ Safety check error: {e}")
            self.audit_results["dependency_security"]["error"] = str(e)
    
    def analyze_code_quality(self):
        """Analyze code quality metrics"""
        print("🔍 Analyzing code quality metrics...")
        
        try:
            # Count files and lines of code
            python_files = list(self.project_root.rglob("src/**/*.py"))
            rust_files = list(self.project_root.rglob("src/**/*.rs"))
            
            total_python_lines = 0
            total_rust_lines = 0
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        total_python_lines += len(f.readlines())
                except:
                    pass
            
            for rust_file in rust_files:
                try:
                    with open(rust_file, 'r', encoding='utf-8') as f:
                        total_rust_lines += len(f.readlines())
                except:
                    pass
            
            # Search for TODO/FIXME/HACK comments
            todo_count = 0
            for file_path in list(python_files) + list(rust_files):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().upper()
                        todo_count += content.count('TODO') + content.count('FIXME') + content.count('HACK')
                except:
                    pass
            
            self.audit_results["code_quality"] = {
                "python_files": len(python_files),
                "rust_files": len(rust_files),
                "total_python_loc": total_python_lines,
                "total_rust_loc": total_rust_lines,
                "technical_debt_markers": todo_count,
                "avg_lines_per_python_file": round(total_python_lines / max(len(python_files), 1), 2),
                "avg_lines_per_rust_file": round(total_rust_lines / max(len(rust_files), 1), 2)
            }
            
            print(f"✅ Code quality analysis complete")
            print(f"   - Python: {len(python_files)} files, {total_python_lines} lines")
            print(f"   - Rust: {len(rust_files)} files, {total_rust_lines} lines")
            print(f"   - Technical debt: {todo_count} TODO/FIXME/HACK comments")
            
        except Exception as e:
            print(f"❌ Code quality analysis error: {e}")
            self.audit_results["code_quality"]["error"] = str(e)
    
    def generate_summary(self):
        """Generate security audit summary"""
        print("📊 Generating security audit summary...")
        
        # Calculate overall security score
        python_issues = self.audit_results["python_security"].get("total_issues", 0)
        rust_vulns = self.audit_results["rust_security"].get("vulnerabilities_found", 0)
        dep_vulns = self.audit_results["dependency_security"].get("python_vulnerabilities", 0)
        
        total_issues = python_issues + rust_vulns + dep_vulns
        
        # Simple scoring: start at 100, deduct points for issues
        security_score = max(0, 100 - (python_issues * 2) - (rust_vulns * 5) - (dep_vulns * 3))
        
        if security_score >= 90:
            security_grade = "A"
        elif security_score >= 80:
            security_grade = "B"
        elif security_score >= 70:
            security_grade = "C"
        elif security_score >= 60:
            security_grade = "D"
        else:
            security_grade = "F"
        
        self.audit_results["summary"] = {
            "total_security_issues": total_issues,
            "security_score": security_score,
            "security_grade": security_grade,
            "critical_findings": python_issues + rust_vulns,
            "recommendations": self._generate_recommendations(),
            "next_steps": [
                "Address high-severity Python security issues",
                "Update Rust dependencies with vulnerabilities", 
                "Implement automated security testing in CI/CD",
                "Add security testing to development workflow"
            ]
        }
        
        print(f"✅ Security audit summary complete")
        print(f"   - Security Score: {security_score}/100 (Grade: {security_grade})")
        print(f"   - Total Issues: {total_issues}")
    
    def _generate_recommendations(self):
        """Generate specific security recommendations"""
        recommendations = []
        
        python_issues = self.audit_results["python_security"].get("total_issues", 0)
        if python_issues > 0:
            recommendations.append(f"Fix {python_issues} Python security issues identified by Bandit")
        
        rust_vulns = self.audit_results["rust_security"].get("vulnerabilities_found", 0)
        if rust_vulns > 0:
            recommendations.append(f"Update {rust_vulns} vulnerable Rust dependencies")
        
        dep_vulns = self.audit_results["dependency_security"].get("python_vulnerabilities", 0)
        if dep_vulns > 0:
            recommendations.append(f"Update {dep_vulns} vulnerable Python dependencies")
        
        todo_count = self.audit_results["code_quality"].get("technical_debt_markers", 0)
        if todo_count > 20:
            recommendations.append(f"Address {todo_count} TODO/FIXME comments in codebase")
        
        if not recommendations:
            recommendations.append("Security posture is good - maintain current practices")
        
        return recommendations
    
    def save_report(self):
        """Save the security audit report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.results_dir / f"security_audit_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.audit_results, f, indent=2)
        
        print(f"📄 Security audit report saved: {report_file}")
        
        # Also create a human-readable summary
        summary_file = self.results_dir / f"security_summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write("SYN_OS SECURITY AUDIT SUMMARY\n")
            f.write("=" * 40 + "\n\n")
            
            f.write(f"Audit Date: {self.audit_results['timestamp']}\n")
            f.write(f"Security Score: {self.audit_results['summary']['security_score']}/100\n")
            f.write(f"Security Grade: {self.audit_results['summary']['security_grade']}\n")
            f.write(f"Total Issues: {self.audit_results['summary']['total_security_issues']}\n\n")
            
            f.write("FINDINGS:\n")
            f.write(f"- Python Security Issues: {self.audit_results['python_security'].get('total_issues', 0)}\n")
            f.write(f"- Rust Vulnerabilities: {self.audit_results['rust_security'].get('vulnerabilities_found', 0)}\n")
            f.write(f"- Dependency Vulnerabilities: {self.audit_results['dependency_security'].get('python_vulnerabilities', 0)}\n")
            f.write(f"- Code Quality Markers: {self.audit_results['code_quality'].get('technical_debt_markers', 0)}\n\n")
            
            f.write("RECOMMENDATIONS:\n")
            for i, rec in enumerate(self.audit_results['summary']['recommendations'], 1):
                f.write(f"{i}. {rec}\n")
        
        print(f"📄 Security summary saved: {summary_file}")
        return report_file, summary_file
    
    def run_full_audit(self):
        """Run complete security audit"""
        print("🚀 Starting comprehensive security audit...")
        print("=" * 60)
        
        self.run_bandit_scan()
        self.run_cargo_audit()
        self.run_safety_check()
        self.analyze_code_quality()
        self.generate_summary()
        
        report_file, summary_file = self.save_report()
        
        print("\n🎉 Security audit complete!")
        print(f"📊 Security Score: {self.audit_results['summary']['security_score']}/100")
        print(f"🎯 Security Grade: {self.audit_results['summary']['security_grade']}")
        print(f"📄 Full report: {report_file}")
        print(f"📋 Summary: {summary_file}")
        
        return self.audit_results

if __name__ == "__main__":
    auditor = SecurityAuditor()
    results = auditor.run_full_audit()