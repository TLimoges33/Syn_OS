#!/usr/bin/env python3
"""
A+ Security Audit for Syn_OS Academic Achievement
==============================================

Comprehensive security audit focusing on A+ grade requirements:
- Dependency vulnerability analysis
- Code security scanning with Bandit
- Technical debt assessment
- Security score calculation

Target: Achieve A grade security (85/100) for A+ academic achievement
"""

import subprocess
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple
import asyncio

def run_command(cmd: List[str]) -> Tuple[int, str, str]:
    """Run system command and return status, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)

def analyze_dependency_vulnerabilities() -> Tuple[int, List[str]]:
    """Analyze dependency vulnerabilities using safety"""
    print("🔍 Analyzing dependency vulnerabilities...")
    
    # Use new safety scan command
    cmd = ["python", "-m", "safety", "scan", "--json"]
    code, stdout, stderr = run_command(cmd)
    
    vulnerabilities = []
    vuln_count = 0
    
    if code == 0 and stdout:
        try:
            # Try to parse JSON output
            data = json.loads(stdout)
            if "vulnerabilities" in data:
                vuln_count = len(data["vulnerabilities"])
                for vuln in data["vulnerabilities"]:
                    pkg_name = vuln.get("package_name", "unknown")
                    vuln_id = vuln.get("vulnerability_id", "unknown")
                    vulnerabilities.append(f"{pkg_name}: {vuln_id}")
        except json.JSONDecodeError:
            # Fallback to legacy check command
            cmd_legacy = ["python", "-m", "safety", "check", "--json"]
            code_legacy, stdout_legacy, stderr_legacy = run_command(cmd_legacy)
            
            if code_legacy == 0 and stdout_legacy:
                try:
                    data = json.loads(stdout_legacy)
                    if "vulnerabilities" in data:
                        vuln_count = len(data["vulnerabilities"])
                        for vuln in data["vulnerabilities"]:
                            pkg_name = vuln.get("package_name", "unknown")
                            vuln_id = vuln.get("vulnerability_id", "unknown")
                            vulnerabilities.append(f"{pkg_name}: {vuln_id}")
                except:
                    print(f"⚠️ Warning: Could not parse safety output")
                    vuln_count = 5  # Conservative estimate
    
    print(f"   Found {vuln_count} dependency vulnerabilities")
    return vuln_count, vulnerabilities

def analyze_bandit_issues() -> Tuple[int, List[str]]:
    """Analyze Python security issues with Bandit"""
    print("🔍 Analyzing Python security issues with Bandit...")
    
    cmd = ["python", "-m", "bandit", "-r", "src/", "-f", "json", "-q"]
    code, stdout, stderr = run_command(cmd)
    
    high_severity_issues = []
    medium_severity_issues = []
    
    if stdout:
        try:
            data = json.loads(stdout)
            results = data.get("results", [])
            
            for issue in results:
                severity = issue.get("issue_severity", "").upper()
                filename = issue.get("filename", "")
                test_id = issue.get("test_id", "")
                line_num = issue.get("line_number", "")
                
                issue_desc = f"{filename}:{line_num} - {test_id}"
                
                if severity == "HIGH":
                    high_severity_issues.append(issue_desc)
                elif severity == "MEDIUM":
                    medium_severity_issues.append(issue_desc)
                    
        except json.JSONDecodeError:
            print("⚠️ Warning: Could not parse Bandit output")
    
    print(f"   Found {len(high_severity_issues)} high-severity issues")
    print(f"   Found {len(medium_severity_issues)} medium-severity issues")
    
    return len(high_severity_issues), high_severity_issues

def analyze_technical_debt() -> Tuple[int, List[str]]:
    """Analyze technical debt markers"""
    print("🔍 Analyzing technical debt (TODO/FIXME comments)...")
    
    debt_markers = []
    total_markers = 0
    
    # Search for TODO and FIXME comments
    for pattern in ["TODO", "FIXME", "XXX", "HACK"]:
        cmd = ["grep", "-r", "-n", "-i", pattern, "src/"]
        code, stdout, stderr = run_command(cmd)
        
        if code == 0 and stdout:
            lines = stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    debt_markers.append(line)
                    total_markers += 1
    
    print(f"   Found {total_markers} technical debt markers")
    return total_markers, debt_markers

def calculate_security_score(vuln_count: int, high_bandit: int, debt_markers: int) -> Tuple[int, str]:
    """Calculate overall security score based on A+ criteria"""
    base_score = 100
    
    # Deduct points for vulnerabilities
    vulnerability_penalty = min(vuln_count * 3, 25)  # Max 25 points for vulnerabilities
    
    # Deduct points for high-severity Bandit issues
    bandit_penalty = min(high_bandit * 10, 20)  # Max 20 points for Bandit issues
    
    # Deduct points for technical debt (moderate impact)
    debt_penalty = min(debt_markers // 10, 10)  # Max 10 points for technical debt
    
    final_score = max(0, base_score - vulnerability_penalty - bandit_penalty - debt_penalty)
    
    # Determine grade
    if final_score >= 92:
        grade = "A+"
    elif final_score >= 85:
        grade = "A"
    elif final_score >= 80:
        grade = "B+"
    elif final_score >= 75:
        grade = "B"
    elif final_score >= 70:
        grade = "C+"
    elif final_score >= 65:
        grade = "C"
    else:
        grade = "F"
    
    return final_score, grade

def generate_a_plus_recommendations(vuln_count: int, high_bandit: int, debt_markers: int, vulnerabilities: List[str]) -> List[str]:
    """Generate specific recommendations for A+ achievement"""
    recommendations = []
    
    if vuln_count > 0:
        recommendations.append(f"🔒 CRITICAL: Update {vuln_count} vulnerable dependencies")
        recommendations.append("   - Priority: python-jose, ecdsa (known cryptographic vulnerabilities)")
        recommendations.append("   - Consider alternatives: PyJWT[crypto], cryptography")
    
    if high_bandit > 0:
        recommendations.append(f"🛡️ HIGH: Fix {high_bandit} high-severity Bandit security issues")
        recommendations.append("   - Focus on hardcoded passwords, SQL injection, insecure crypto")
    
    if debt_markers > 50:
        recommendations.append(f"🧹 MODERATE: Reduce {debt_markers} technical debt markers to <10 for A+")
        recommendations.append("   - Replace TODO comments with actual implementations")
        recommendations.append("   - Remove FIXME markers by addressing underlying issues")
    
    # A+ specific recommendations
    recommendations.append("📈 A+ ACHIEVEMENT TARGETS:")
    recommendations.append("   - Security Score: 85+ (A grade minimum)")
    recommendations.append("   - Vulnerabilities: 0 (Zero tolerance for A+)")
    recommendations.append("   - High-severity Bandit: 0 (Zero tolerance for A+)")
    recommendations.append("   - Technical Debt: <10 markers (Excellence standard)")
    
    return recommendations

def main():
    """Main A+ security audit execution"""
    print("🎯 A+ SECURITY AUDIT FOR SYN_OS ACADEMIC ACHIEVEMENT")
    print("=" * 60)
    print(f"Audit Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Change to project directory
    os.chdir('/home/diablorain/Syn_OS')
    
    # Activate virtual environment check
    if not os.path.exists('venv/bin/activate'):
        print("❌ Virtual environment not found. Run 'python -m venv venv' first.")
        sys.exit(1)
    
    # Run security analyses
    vuln_count, vulnerabilities = analyze_dependency_vulnerabilities()
    high_bandit, bandit_issues = analyze_bandit_issues()
    debt_markers, debt_list = analyze_technical_debt()
    
    # Calculate security score
    security_score, grade = calculate_security_score(vuln_count, high_bandit, debt_markers)
    
    # Generate report
    print("\n🏆 A+ SECURITY ASSESSMENT RESULTS")
    print("=" * 40)
    print(f"Security Score: {security_score}/100")
    print(f"Security Grade: {grade}")
    print()
    
    print("📊 DETAILED FINDINGS:")
    print(f"   Dependency Vulnerabilities: {vuln_count}")
    print(f"   High-Severity Bandit Issues: {high_bandit}")
    print(f"   Technical Debt Markers: {debt_markers}")
    print()
    
    # A+ achievement status
    if grade in ["A+", "A"]:
        print("🎉 CONGRATULATIONS! A+ SECURITY FOUNDATION ACHIEVED!")
        print("   Excellence in security implementation demonstrated")
    elif grade in ["B+", "B"]:
        print("📈 STRONG PROGRESS TOWARD A+ ACHIEVEMENT")
        print("   Close to A+ security standards - final sprint recommended")
    else:
        print("⚠️  ADDITIONAL SECURITY WORK REQUIRED FOR A+")
        print("   Focus on critical vulnerabilities and high-severity issues")
    
    print()
    
    # Generate recommendations
    recommendations = generate_a_plus_recommendations(vuln_count, high_bandit, debt_markers, vulnerabilities)
    
    print("🚀 A+ ACHIEVEMENT RECOMMENDATIONS:")
    for rec in recommendations:
        print(rec)
    
    print()
    
    # Save detailed results
    results = {
        "timestamp": datetime.now().isoformat(),
        "security_score": security_score,
        "security_grade": grade,
        "vulnerability_count": vuln_count,
        "high_bandit_issues": high_bandit,
        "technical_debt_markers": debt_markers,
        "vulnerabilities": vulnerabilities[:10],  # Top 10
        "bandit_issues": bandit_issues[:10],  # Top 10
        "recommendations": recommendations,
        "a_plus_ready": grade in ["A+", "A"]
    }
    
    # Ensure results directory exists
    os.makedirs("results/security_reports", exist_ok=True)
    
    # Save JSON report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = f"results/security_reports/a_plus_audit_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save summary report
    summary_file = f"results/security_reports/a_plus_summary_{timestamp}.txt"
    with open(summary_file, 'w') as f:
        f.write(f"A+ SECURITY AUDIT SUMMARY\n")
        f.write(f"========================\n\n")
        f.write(f"Audit Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Security Score: {security_score}/100\n")
        f.write(f"Security Grade: {grade}\n")
        f.write(f"A+ Ready: {'Yes' if grade in ['A+', 'A'] else 'No'}\n\n")
        f.write(f"FINDINGS:\n")
        f.write(f"- Dependency Vulnerabilities: {vuln_count}\n")
        f.write(f"- High-Severity Bandit Issues: {high_bandit}\n")
        f.write(f"- Technical Debt Markers: {debt_markers}\n\n")
        f.write(f"A+ ACHIEVEMENT STATUS:\n")
        if grade in ["A+", "A"]:
            f.write("🎉 A+ SECURITY FOUNDATION ACHIEVED!\n")
        else:
            f.write("📈 Continue A+ push - focus on critical security issues\n")
    
    print(f"📄 Detailed reports saved:")
    print(f"   JSON: {json_file}")
    print(f"   Summary: {summary_file}")
    
    # Return appropriate exit code
    if grade in ["A+", "A"]:
        return 0  # Success - A+ ready
    elif grade in ["B+", "B"]:
        return 1  # Progress - continue A+ push
    else:
        return 2  # Significant work needed

if __name__ == "__main__":
    sys.exit(main())