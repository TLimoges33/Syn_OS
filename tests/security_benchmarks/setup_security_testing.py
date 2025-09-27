#!/usr/bin/env python3
"""
Security Testing Infrastructure Setup
=====================================

This module sets up comprehensive security testing and benchmarking
for the Syn_OS project, focusing on validating actual security capabilities
rather than making unsubstantiated claims.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_security_tools():
    """Install required security testing tools"""
    tools = [
        "bandit[toml]",  # Python security scanner
        "safety",        # Dependency vulnerability scanner  
        "pytest-benchmark",  # Performance benchmarking
        "pytest-cov",   # Test coverage measurement
        "semgrep",       # Static analysis
        "httpx",         # HTTP testing
        "cryptography",  # Additional crypto testing
    ]
    
    print("🔧 Installing security testing tools...")
    for tool in tools:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", tool], 
                         check=True, capture_output=True)
            print(f"✅ Installed {tool}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {tool}: {e}")
    
    print("🔧 Setting up Rust security tools...")
    rust_tools = ["cargo-audit", "cargo-tarpaulin"]
    for tool in rust_tools:
        try:
            subprocess.run(["cargo", "install", tool], 
                         check=True, capture_output=True)
            print(f"✅ Installed {tool}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {tool}: {e}")

def create_test_structure():
    """Create comprehensive test directory structure"""
    test_dirs = [
        "tests/security_benchmarks",
        "tests/performance_validation", 
        "tests/integration_complete",
        "tests/security_audits",
        "results/benchmarks",
        "results/security_reports",
        "results/coverage_reports"
    ]
    
    print("📁 Creating test directory structure...")
    for dir_path in test_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {dir_path}")

def create_security_config():
    """Create security testing configuration files"""
    
    # Bandit configuration for Python security scanning
    bandit_config = """
[bandit]
exclude_dirs = ["tests", "venv", "build"]
skips = ["B101"]  # Skip assert_used test

[bandit.any_other_function_with_shell_equals_true]
no_shell = [
    "subprocess.run",
    "subprocess.Popen",
    "subprocess.call"
]
"""
    
    # PyProject.toml test configuration
    pyproject_config = """
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "--cov=src",
    "--cov-report=html:results/coverage_reports/html",
    "--cov-report=term-missing",
    "--benchmark-only",
    "--benchmark-sort=mean"
]

[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "venv/*", "*/migrations/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError"
]
"""
    
    print("📝 Creating security configuration files...")
    
    with open("bandit.yml", "w") as f:
        f.write(bandit_config)
    print("✅ Created bandit.yml")
    
    # Update or create pyproject.toml
    if not os.path.exists("pyproject.toml"):
        with open("pyproject.toml", "w") as f:
            f.write(pyproject_config)
        print("✅ Created pyproject.toml")

if __name__ == "__main__":
    print("🚀 Setting up Syn_OS Security Testing Infrastructure")
    print("=" * 60)
    
    install_security_tools()
    create_test_structure()
    create_security_config()
    
    print("\n✅ Security testing infrastructure setup complete!")
    print("\nNext steps:")
    print("1. Run: python tests/security_benchmarks/security_audit.py")
    print("2. Run: python tests/performance_validation/benchmark_auth.py")
    print("3. Review results in results/ directory")