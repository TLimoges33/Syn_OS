#!/usr/bin/env python3
"""
Syn_OS A+ Security Audit Script
Comprehensive security scanning and vulnerability assessment
"""

import os
import sys
import json
import subprocess
import time
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Colors for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class SecurityAuditor:
    """Main security auditing class for Syn_OS"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results_dir = self.project_root / "results" / "security_reports"
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.vulnerabilities = []
        self.warnings = []
        self.passed_checks = []
        self.critical_count = 0
        self.high_count = 0
        self.medium_count = 0
        self.low_count = 0

    def print_banner(self):
        """Print audit banner"""
        banner = f"""
{Colors.CYAN}{'='*60}
   Syn_OS A+ Security Audit System
   Neural Darwinism-Enhanced Security Scanner
{'='*60}{Colors.RESET}
        """
        print(banner)

    def log_result(self, level: str, category: str, message: str, details: str = ""):
        """Log security finding"""
        timestamp = datetime.now().isoformat()

        if level == "CRITICAL":
            color = Colors.RED
            self.critical_count += 1
            self.vulnerabilities.append((level, category, message, details))
        elif level == "HIGH":
            color = Colors.RED
            self.high_count += 1
            self.vulnerabilities.append((level, category, message, details))
        elif level == "MEDIUM":
            color = Colors.YELLOW
            self.medium_count += 1
            self.vulnerabilities.append((level, category, message, details))
        elif level == "LOW":
            color = Colors.YELLOW
            self.low_count += 1
            self.warnings.append((level, category, message, details))
        elif level == "INFO":
            color = Colors.BLUE
            self.warnings.append((level, category, message, details))
        elif level == "PASS":
            color = Colors.GREEN
            self.passed_checks.append((category, message))
        else:
            color = Colors.WHITE

        symbol = "✗" if level in ["CRITICAL", "HIGH"] else "⚠" if level in ["MEDIUM", "LOW"] else "✓" if level == "PASS" else "ℹ"

        print(f"{color}{symbol} [{level}] {category}: {message}{Colors.RESET}")
        if details:
            print(f"  {Colors.WHITE}Details: {details}{Colors.RESET}")

    def check_dependencies(self) -> bool:
        """Check for vulnerable dependencies"""
        print(f"\n{Colors.CYAN}[*] Checking dependencies for vulnerabilities...{Colors.RESET}")

        vulnerabilities_found = False

        # Check Rust dependencies with cargo audit
        if (self.project_root / "Cargo.toml").exists():
            try:
                result = subprocess.run(
                    ["cargo", "audit", "--json"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )

                if result.returncode == 0:
                    try:
                        audit_data = json.loads(result.stdout)
                        if audit_data.get("vulnerabilities", {}).get("count", 0) == 0:
                            self.log_result("PASS", "Rust Dependencies", "No known vulnerabilities in Cargo dependencies")
                        else:
                            for vuln in audit_data.get("vulnerabilities", {}).get("list", []):
                                self.log_result("HIGH", "Rust Dependencies",
                                              f"Vulnerability in {vuln.get('package', {}).get('name', 'unknown')}",
                                              vuln.get('advisory', {}).get('description', ''))
                                vulnerabilities_found = True
                    except json.JSONDecodeError:
                        # Fallback to text parsing
                        if "0 vulnerabilities" in result.stdout:
                            self.log_result("PASS", "Rust Dependencies", "No known vulnerabilities in Cargo dependencies")
                        else:
                            self.log_result("MEDIUM", "Rust Dependencies", "cargo audit found issues", result.stdout[:200])
                            vulnerabilities_found = True

            except FileNotFoundError:
                self.log_result("INFO", "Rust Dependencies", "cargo audit not installed",
                              "Install with: cargo install cargo-audit")

        # Check Python dependencies
        requirements_files = [
            "config/dependencies/requirements-security.txt",
            "config/dependencies/requirements-ai-integration.txt",
            "config/dependencies/requirements-testing.txt",
            "config/dependencies/requirements-nats.txt"
        ]

        for req_file in requirements_files:
            req_path = self.project_root / req_file
            if req_path.exists():
                try:
                    # Use safety check if available
                    result = subprocess.run(
                        ["safety", "check", "-r", str(req_path), "--json"],
                        capture_output=True,
                        text=True
                    )

                    if result.returncode == 0:
                        self.log_result("PASS", "Python Dependencies", f"No vulnerabilities in {req_file}")
                    else:
                        try:
                            issues = json.loads(result.stdout)
                            for issue in issues:
                                self.log_result("HIGH", "Python Dependencies",
                                              f"Vulnerable package: {issue.get('package', 'unknown')}",
                                              issue.get('vulnerability', ''))
                                vulnerabilities_found = True
                        except:
                            self.log_result("MEDIUM", "Python Dependencies", f"Issues found in {req_file}")
                            vulnerabilities_found = True

                except FileNotFoundError:
                    # Fallback to pip-audit if safety is not installed
                    try:
                        result = subprocess.run(
                            ["pip-audit", "-r", str(req_path), "--format", "json"],
                            capture_output=True,
                            text=True
                        )

                        if result.stdout:
                            audit_results = json.loads(result.stdout)
                            if not audit_results:
                                self.log_result("PASS", "Python Dependencies", f"No vulnerabilities in {req_file}")
                            else:
                                for vuln in audit_results:
                                    self.log_result("HIGH", "Python Dependencies",
                                                  f"Vulnerable: {vuln.get('name', 'unknown')}",
                                                  vuln.get('description', ''))
                                    vulnerabilities_found = True
                    except FileNotFoundError:
                        self.log_result("INFO", "Python Dependencies",
                                      "Neither safety nor pip-audit installed",
                                      "Install with: pip install safety pip-audit")

        return not vulnerabilities_found

    def scan_source_code(self):
        """Scan source code for security issues"""
        print(f"\n{Colors.CYAN}[*] Scanning source code for security issues...{Colors.RESET}")

        security_patterns = {
            "hardcoded_password": re.compile(r'password\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
            "hardcoded_key": re.compile(r'(api_key|apikey|secret_key|private_key)\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
            "unsafe_sql": re.compile(r'(SELECT|INSERT|UPDATE|DELETE).*\+.*%(s|d)', re.IGNORECASE),
            "eval_usage": re.compile(r'\beval\s*\('),
            "exec_usage": re.compile(r'\bexec\s*\('),
            "pickle_load": re.compile(r'pickle\.load'),
            "unsafe_yaml": re.compile(r'yaml\.load\s*\([^)]*\)(?!\s*,\s*Loader)'),
            "weak_crypto": re.compile(r'(md5|sha1)\s*\('),
            "insecure_random": re.compile(r'random\.(random|randint|choice)\s*\('),
            "http_no_tls": re.compile(r'http://[^/\s]+'),
            "shell_injection": re.compile(r'subprocess\.(call|run|Popen)\s*\([^)]*shell\s*=\s*True'),
        }

        extensions_to_scan = ['.py', '.rs', '.go', '.js', '.ts', '.sh', '.yaml', '.yml']

        issues_found = False
        files_scanned = 0

        for root, dirs, files in os.walk(self.project_root):
            # Skip directories we don't want to scan
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'target', '__pycache__', '.venv', 'archive']]

            for file in files:
                file_path = Path(root) / file

                if any(file_path.suffix == ext for ext in extensions_to_scan):
                    files_scanned += 1

                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        for pattern_name, pattern in security_patterns.items():
                            matches = pattern.findall(content)
                            if matches:
                                relative_path = file_path.relative_to(self.project_root)

                                if pattern_name in ["hardcoded_password", "hardcoded_key"]:
                                    self.log_result("CRITICAL", "Source Code Security",
                                                  f"Potential {pattern_name.replace('_', ' ')} in {relative_path}",
                                                  f"Found: {matches[0][:50]}...")
                                    issues_found = True
                                elif pattern_name in ["unsafe_sql", "shell_injection"]:
                                    self.log_result("HIGH", "Source Code Security",
                                                  f"Potential {pattern_name.replace('_', ' ')} in {relative_path}")
                                    issues_found = True
                                elif pattern_name in ["eval_usage", "exec_usage", "pickle_load"]:
                                    self.log_result("HIGH", "Source Code Security",
                                                  f"Unsafe {pattern_name.replace('_', ' ')} in {relative_path}")
                                    issues_found = True
                                elif pattern_name == "weak_crypto":
                                    self.log_result("MEDIUM", "Source Code Security",
                                                  f"Weak cryptographic hash in {relative_path}")
                                    issues_found = True
                                elif pattern_name == "insecure_random":
                                    self.log_result("LOW", "Source Code Security",
                                                  f"Non-cryptographic random in {relative_path}",
                                                  "Use secrets module for security-sensitive randomness")
                                elif pattern_name == "http_no_tls":
                                    if not any(safe in matches[0] for safe in ['localhost', '127.0.0.1', '0.0.0.0']):
                                        self.log_result("MEDIUM", "Source Code Security",
                                                      f"Unencrypted HTTP URL in {relative_path}",
                                                      f"URL: {matches[0]}")
                                        issues_found = True

                    except Exception as e:
                        self.log_result("INFO", "Source Code Security",
                                      f"Could not scan {file_path.name}: {str(e)}")

        if not issues_found:
            self.log_result("PASS", "Source Code Security", f"No critical security issues found in {files_scanned} files")

    def check_file_permissions(self):
        """Check for insecure file permissions"""
        print(f"\n{Colors.CYAN}[*] Checking file permissions...{Colors.RESET}")

        sensitive_dirs = ["config", "scripts", ".ssh", "keys", "certs", "secrets"]
        issues_found = False

        for root, dirs, files in os.walk(self.project_root):
            path = Path(root)

            # Check for world-writable files
            for file in files:
                file_path = path / file
                try:
                    stat_info = file_path.stat()
                    mode = oct(stat_info.st_mode)[-3:]

                    if mode[-1] in ['2', '3', '6', '7']:  # World writable
                        relative_path = file_path.relative_to(self.project_root)
                        self.log_result("HIGH", "File Permissions",
                                      f"World-writable file: {relative_path}",
                                      f"Current permissions: {mode}")
                        issues_found = True

                    # Check for sensitive files with too broad permissions
                    if any(sensitive in str(file_path).lower() for sensitive in ['key', 'secret', 'password', 'token', 'cert']):
                        if mode != '600' and mode != '400':
                            relative_path = file_path.relative_to(self.project_root)
                            self.log_result("MEDIUM", "File Permissions",
                                          f"Sensitive file with broad permissions: {relative_path}",
                                          f"Current: {mode}, Recommended: 600 or 400")
                            issues_found = True

                except Exception:
                    pass

        if not issues_found:
            self.log_result("PASS", "File Permissions", "No insecure file permissions detected")

    def check_docker_security(self):
        """Check Docker configuration for security issues"""
        print(f"\n{Colors.CYAN}[*] Checking Docker security...{Colors.RESET}")

        docker_files = [
            "docker/docker-compose.yml",
            "deployment/docker-compose.ha.yml",
            "Dockerfile"
        ]

        issues_found = False

        for docker_file in docker_files:
            file_path = self.project_root / docker_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()

                    # Check for running as root
                    if "USER root" in content or (docker_file == "Dockerfile" and "USER" not in content):
                        self.log_result("MEDIUM", "Docker Security",
                                      f"Container may run as root in {docker_file}",
                                      "Consider adding a non-root USER directive")
                        issues_found = True

                    # Check for privileged mode
                    if "privileged: true" in content:
                        self.log_result("HIGH", "Docker Security",
                                      f"Privileged mode enabled in {docker_file}",
                                      "Avoid privileged mode unless absolutely necessary")
                        issues_found = True

                    # Check for exposed sensitive ports
                    if re.search(r'ports:\s*-\s*["\']*22[:"]', content):
                        self.log_result("MEDIUM", "Docker Security",
                                      f"SSH port exposed in {docker_file}",
                                      "Consider using Docker exec instead of SSH")
                        issues_found = True

                    # Check for latest tags
                    if ":latest" in content:
                        self.log_result("LOW", "Docker Security",
                                      f"Using :latest tag in {docker_file}",
                                      "Pin to specific versions for reproducibility")

                except Exception as e:
                    self.log_result("INFO", "Docker Security", f"Could not analyze {docker_file}: {str(e)}")

        if not issues_found:
            self.log_result("PASS", "Docker Security", "Docker configurations follow security best practices")

    def check_kernel_security(self):
        """Check kernel-specific security features"""
        print(f"\n{Colors.CYAN}[*] Checking kernel security features...{Colors.RESET}")

        kernel_src = self.project_root / "src" / "kernel" / "src"

        if kernel_src.exists():
            security_features = {
                "stack_guard": False,
                "nx_bit": False,
                "aslr": False,
                "secure_boot": False
            }

            # Check for security features in kernel code
            for root, dirs, files in os.walk(kernel_src):
                for file in files:
                    if file.endswith('.rs'):
                        file_path = Path(root) / file
                        try:
                            with open(file_path, 'r') as f:
                                content = f.read()

                            if "stack_guard" in content.lower() or "stack_canary" in content.lower():
                                security_features["stack_guard"] = True
                            if "nx_bit" in content.lower() or "no_execute" in content.lower():
                                security_features["nx_bit"] = True
                            if "aslr" in content.lower() or "address_space_layout" in content.lower():
                                security_features["aslr"] = True
                            if "secure_boot" in content.lower() or "uefi" in content.lower():
                                security_features["secure_boot"] = True

                        except Exception:
                            pass

            # Report findings
            for feature, enabled in security_features.items():
                if enabled:
                    self.log_result("PASS", "Kernel Security", f"{feature.replace('_', ' ').title()} appears to be implemented")
                else:
                    self.log_result("MEDIUM", "Kernel Security",
                                  f"{feature.replace('_', ' ').title()} not detected",
                                  "Consider implementing this security feature")

    def generate_report(self):
        """Generate comprehensive security report"""
        print(f"\n{Colors.CYAN}[*] Generating security report...{Colors.RESET}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.results_dir / f"security_audit_{timestamp}.json"

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "critical": self.critical_count,
                "high": self.high_count,
                "medium": self.medium_count,
                "low": self.low_count,
                "passed": len(self.passed_checks)
            },
            "vulnerabilities": [
                {
                    "level": v[0],
                    "category": v[1],
                    "message": v[2],
                    "details": v[3]
                } for v in self.vulnerabilities
            ],
            "warnings": [
                {
                    "level": w[0],
                    "category": w[1],
                    "message": w[2],
                    "details": w[3]
                } for w in self.warnings
            ],
            "passed_checks": [
                {
                    "category": p[0],
                    "message": p[1]
                } for p in self.passed_checks
            ]
        }

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"{Colors.GREEN}✓ Report saved to: {report_file}{Colors.RESET}")

        return report

    def print_summary(self):
        """Print audit summary"""
        print(f"\n{Colors.CYAN}{'='*60}")
        print("                SECURITY AUDIT SUMMARY")
        print(f"{'='*60}{Colors.RESET}")

        total_issues = self.critical_count + self.high_count + self.medium_count + self.low_count

        if self.critical_count > 0:
            print(f"{Colors.RED}CRITICAL Issues: {self.critical_count}{Colors.RESET}")
        if self.high_count > 0:
            print(f"{Colors.RED}HIGH Issues: {self.high_count}{Colors.RESET}")
        if self.medium_count > 0:
            print(f"{Colors.YELLOW}MEDIUM Issues: {self.medium_count}{Colors.RESET}")
        if self.low_count > 0:
            print(f"{Colors.YELLOW}LOW Issues: {self.low_count}{Colors.RESET}")

        print(f"{Colors.GREEN}Passed Checks: {len(self.passed_checks)}{Colors.RESET}")

        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")

        if self.critical_count > 0 or self.high_count > 0:
            print(f"{Colors.RED}{Colors.BOLD}⚠ SECURITY STATUS: FAILED{Colors.RESET}")
            print(f"{Colors.RED}Critical security issues detected. Immediate action required!{Colors.RESET}")
            return False
        elif self.medium_count > 0:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠ SECURITY STATUS: NEEDS ATTENTION{Colors.RESET}")
            print(f"{Colors.YELLOW}Medium priority issues detected. Review and fix recommended.{Colors.RESET}")
            return True
        elif self.low_count > 0:
            print(f"{Colors.GREEN}{Colors.BOLD}✓ SECURITY STATUS: PASSED WITH WARNINGS{Colors.RESET}")
            print(f"{Colors.GREEN}System is secure with minor recommendations.{Colors.RESET}")
            return True
        else:
            print(f"{Colors.GREEN}{Colors.BOLD}✓ SECURITY STATUS: EXCELLENT{Colors.RESET}")
            print(f"{Colors.GREEN}No security issues detected! System is secure.{Colors.RESET}")
            return True

    def run(self) -> bool:
        """Run complete security audit"""
        self.print_banner()

        # Run all security checks
        self.check_dependencies()
        self.scan_source_code()
        self.check_file_permissions()
        self.check_docker_security()
        self.check_kernel_security()

        # Generate and save report
        self.generate_report()

        # Print summary and return status
        return self.print_summary()


def main():
    """Main entry point"""
    auditor = SecurityAuditor()

    try:
        success = auditor.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Audit interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Audit failed with error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()