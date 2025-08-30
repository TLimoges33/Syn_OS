#!/usr/bin/env python3
"""
Syn_OS AI Development Environment Validator

This script validates the development environment for optimal AI-assisted development
with Claude Code, GitHub Copilot, and other modern tools.
"""

import os
import sys
import json
import subprocess
import shutil
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class ValidationLevel(Enum):
    """Validation severity levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"

@dataclass
class ValidationResult:
    """Individual validation result"""
    component: str
    status: ValidationLevel
    message: str
    details: Optional[str] = None
    fix_command: Optional[str] = None

class DevEnvironmentValidator:
    """Comprehensive development environment validator"""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
        self.project_root = Path(__file__).parent.parent
        self.required_tools = {
            'git': 'Version control system',
            'gh': 'GitHub CLI for repository management',
            'code': 'Visual Studio Code editor',
            'docker': 'Container runtime',
            'podman': 'Alternative container runtime',
            'rustc': 'Rust compiler',
            'cargo': 'Rust package manager',
            'python3': 'Python interpreter',
            'go': 'Go programming language',
            'make': 'Build automation tool'
        }
        self.vscode_extensions = {
            'rust-lang.rust-analyzer': 'Rust language support',
            'ms-python.python': 'Python language support',
            'github.copilot': 'AI code completion',
            'anthropic.claude-code': 'Claude AI assistant',
            'ms-vscode.cpptools': 'C/C++ support',
            'golang.go': 'Go language support',
            'snyk-security.snyk-vulnerability-scanner': 'Security scanning',
            'eamodio.gitlens': 'Enhanced Git features'
        }

    def log_result(self, component: str, status: ValidationLevel, 
                   message: str, details: str = None, fix_command: str = None):
        """Log a validation result"""
        result = ValidationResult(
            component=component,
            status=status,
            message=message,
            details=details,
            fix_command=fix_command
        )
        self.results.append(result)
        
        # Color coding for terminal output
        colors = {
            ValidationLevel.CRITICAL: '\033[0;31m',  # Red
            ValidationLevel.WARNING: '\033[1;33m',   # Yellow
            ValidationLevel.INFO: '\033[0;34m',      # Blue
            ValidationLevel.SUCCESS: '\033[0;32m'    # Green
        }
        reset = '\033[0m'
        
        color = colors.get(status, '')
        status_symbol = {
            ValidationLevel.CRITICAL: '❌',
            ValidationLevel.WARNING: '⚠️',
            ValidationLevel.INFO: 'ℹ️',
            ValidationLevel.SUCCESS: '✅'
        }
        
        symbol = status_symbol.get(status, '•')
        print(f"{color}{symbol} [{component}] {message}{reset}")
        
        if details:
            print(f"   Details: {details}")
        if fix_command:
            print(f"   Fix: {fix_command}")

    def run_command(self, cmd: List[str], capture_output: bool = True) -> Tuple[bool, str, str]:
        """Run a command and return success status and output"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            return False, "", str(e)

    def check_tool_availability(self):
        """Check if required development tools are available"""
        print("\n🔍 Checking Development Tools...")
        
        for tool, description in self.required_tools.items():
            success, stdout, stderr = self.run_command(['which', tool])
            
            if success and stdout.strip():
                # Get version information
                version_cmd = {
                    'git': ['git', '--version'],
                    'gh': ['gh', '--version'],
                    'code': ['code', '--version'],
                    'rustc': ['rustc', '--version'],
                    'cargo': ['cargo', '--version'],
                    'python3': ['python3', '--version'],
                    'go': ['go', 'version'],
                    'docker': ['docker', '--version'],
                    'podman': ['podman', '--version'],
                    'make': ['make', '--version']
                }
                
                if tool in version_cmd:
                    ver_success, ver_stdout, _ = self.run_command(version_cmd[tool])
                    version_info = ver_stdout.split('\n')[0] if ver_success else "version unknown"
                else:
                    version_info = "available"
                
                self.log_result(
                    f"Tool: {tool}",
                    ValidationLevel.SUCCESS,
                    f"{description} - {version_info}",
                    details=f"Location: {stdout.strip()}"
                )
            else:
                self.log_result(
                    f"Tool: {tool}",
                    ValidationLevel.CRITICAL,
                    f"{description} is not available",
                    fix_command=f"Please install {tool}"
                )

    def check_vscode_configuration(self):
        """Check VS Code configuration and extensions"""
        print("\n🔍 Checking VS Code Configuration...")
        
        vscode_dir = self.project_root / '.vscode'
        settings_file = vscode_dir / 'settings.json'
        extensions_file = vscode_dir / 'extensions.json'
        
        # Check .vscode directory
        if not vscode_dir.exists():
            self.log_result(
                "VS Code Config",
                ValidationLevel.WARNING,
                ".vscode directory missing",
                fix_command="mkdir -p .vscode"
            )
        else:
            self.log_result(
                "VS Code Config",
                ValidationLevel.SUCCESS,
                ".vscode directory exists"
            )
        
        # Check settings.json
        if not settings_file.exists():
            self.log_result(
                "VS Code Settings",
                ValidationLevel.WARNING,
                "settings.json missing",
                fix_command="Run setup script to create optimized settings"
            )
        else:
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                
                # Check for AI development settings
                ai_settings = [
                    'github.copilot.enable',
                    'rust-analyzer.checkOnSave.command',
                    'python.linting.pylintEnabled',
                    'editor.inlineSuggest.enabled'
                ]
                
                configured_ai_settings = [s for s in ai_settings if s in json.dumps(settings)]
                
                if configured_ai_settings:
                    self.log_result(
                        "VS Code AI Settings",
                        ValidationLevel.SUCCESS,
                        f"AI development settings configured ({len(configured_ai_settings)}/4)",
                        details=f"Configured: {', '.join(configured_ai_settings)}"
                    )
                else:
                    self.log_result(
                        "VS Code AI Settings",
                        ValidationLevel.WARNING,
                        "AI development settings not optimized",
                        fix_command="Run setup script to optimize settings"
                    )
                    
            except json.JSONDecodeError:
                self.log_result(
                    "VS Code Settings",
                    ValidationLevel.WARNING,
                    "settings.json has invalid JSON",
                    fix_command="Fix JSON syntax in settings.json"
                )
        
        # Check extensions.json
        if not extensions_file.exists():
            self.log_result(
                "VS Code Extensions Config",
                ValidationLevel.WARNING,
                "extensions.json missing",
                fix_command="Run setup script to create extension recommendations"
            )
        else:
            try:
                with open(extensions_file, 'r') as f:
                    extensions_config = json.load(f)
                
                recommended = extensions_config.get('recommendations', [])
                ai_extensions = ['github.copilot', 'anthropic.claude-code', 'kilocode.kilo-code']
                configured_ai_extensions = [ext for ext in ai_extensions if ext in recommended]
                
                if configured_ai_extensions:
                    self.log_result(
                        "VS Code AI Extensions",
                        ValidationLevel.SUCCESS,
                        f"AI extensions configured ({len(configured_ai_extensions)}/3)",
                        details=f"Recommended: {', '.join(configured_ai_extensions)}"
                    )
                else:
                    self.log_result(
                        "VS Code AI Extensions",
                        ValidationLevel.WARNING,
                        "AI extensions not recommended",
                        fix_command="Add AI extensions to recommendations"
                    )
                    
            except json.JSONDecodeError:
                self.log_result(
                    "VS Code Extensions Config",
                    ValidationLevel.WARNING,
                    "extensions.json has invalid JSON"
                )

    def check_installed_extensions(self):
        """Check installed VS Code extensions"""
        print("\n🔍 Checking Installed VS Code Extensions...")
        
        success, stdout, stderr = self.run_command(['code', '--list-extensions'])
        
        if not success:
            self.log_result(
                "Extension Check",
                ValidationLevel.WARNING,
                "Could not retrieve installed extensions",
                details=stderr
            )
            return
        
        installed = set(stdout.strip().split('\n')) if stdout.strip() else set()
        
        for ext_id, description in self.vscode_extensions.items():
            if ext_id in installed:
                self.log_result(
                    f"Extension: {ext_id}",
                    ValidationLevel.SUCCESS,
                    f"{description} - installed"
                )
            else:
                self.log_result(
                    f"Extension: {ext_id}",
                    ValidationLevel.WARNING,
                    f"{description} - not installed",
                    fix_command=f"code --install-extension {ext_id}"
                )

    def check_rust_environment(self):
        """Check Rust development environment"""
        print("\n🔍 Checking Rust Environment...")
        
        # Check rustup components
        components = ['clippy', 'rustfmt', 'llvm-tools-preview']
        
        for component in components:
            success, stdout, stderr = self.run_command(['rustup', 'component', 'list', '--installed'])
            
            if success and component in stdout:
                self.log_result(
                    f"Rust Component: {component}",
                    ValidationLevel.SUCCESS,
                    f"{component} is installed"
                )
            else:
                self.log_result(
                    f"Rust Component: {component}",
                    ValidationLevel.WARNING,
                    f"{component} not installed",
                    fix_command=f"rustup component add {component}"
                )
        
        # Check cargo tools
        cargo_tools = {
            'cargo-audit': 'Security auditing for Rust',
            'cargo-deny': 'Dependency verification',
            'cargo-watch': 'Automatic rebuilds',
            'cargo-tarpaulin': 'Code coverage'
        }
        
        for tool, description in cargo_tools.items():
            success, _, _ = self.run_command(['which', tool])
            
            if success:
                self.log_result(
                    f"Cargo Tool: {tool}",
                    ValidationLevel.SUCCESS,
                    f"{description} - installed"
                )
            else:
                self.log_result(
                    f"Cargo Tool: {tool}",
                    ValidationLevel.INFO,
                    f"{description} - not installed",
                    fix_command=f"cargo install --locked {tool}"
                )

    def check_python_environment(self):
        """Check Python development environment"""
        print("\n🔍 Checking Python Environment...")
        
        venv_path = self.project_root / 'venv'
        
        if venv_path.exists():
            self.log_result(
                "Python Virtual Env",
                ValidationLevel.SUCCESS,
                "Virtual environment exists"
            )
            
            # Check if virtual environment has key packages
            pip_path = venv_path / 'bin' / 'pip'
            if pip_path.exists():
                success, stdout, _ = self.run_command([str(pip_path), 'list'])
                if success:
                    installed_packages = stdout.lower()
                    key_packages = ['black', 'pylint', 'pytest', 'mypy', 'bandit']
                    
                    for package in key_packages:
                        if package in installed_packages:
                            self.log_result(
                                f"Python Tool: {package}",
                                ValidationLevel.SUCCESS,
                                f"{package} is installed"
                            )
                        else:
                            self.log_result(
                                f"Python Tool: {package}",
                                ValidationLevel.WARNING,
                                f"{package} not installed",
                                fix_command=f"pip install {package}"
                            )
        else:
            self.log_result(
                "Python Virtual Env",
                ValidationLevel.WARNING,
                "Virtual environment not found",
                fix_command="python3 -m venv venv"
            )

    def check_docker_environment(self):
        """Check Docker/container environment"""
        print("\n🔍 Checking Container Environment...")
        
        # Check Docker daemon
        success, stdout, stderr = self.run_command(['docker', 'ps'])
        
        if success:
            self.log_result(
                "Docker Daemon",
                ValidationLevel.SUCCESS,
                "Docker is running"
            )
            
            # Check for project containers
            if 'syn_os' in stdout:
                self.log_result(
                    "Project Containers",
                    ValidationLevel.SUCCESS,
                    "Syn_OS containers are running"
                )
            else:
                self.log_result(
                    "Project Containers",
                    ValidationLevel.INFO,
                    "Syn_OS containers not running",
                    fix_command="docker-compose up -d"
                )
        else:
            self.log_result(
                "Docker Daemon",
                ValidationLevel.WARNING,
                "Docker is not running or not accessible",
                details=stderr
            )
        
        # Check docker-compose file
        compose_file = self.project_root / 'docker-compose.yml'
        if compose_file.exists():
            self.log_result(
                "Docker Compose",
                ValidationLevel.SUCCESS,
                "docker-compose.yml exists"
            )
        else:
            self.log_result(
                "Docker Compose",
                ValidationLevel.WARNING,
                "docker-compose.yml not found"
            )

    def check_git_configuration(self):
        """Check Git configuration and hooks"""
        print("\n🔍 Checking Git Configuration...")
        
        # Check if we're in a git repository
        success, stdout, stderr = self.run_command(['git', 'rev-parse', '--git-dir'])
        
        if not success:
            self.log_result(
                "Git Repository",
                ValidationLevel.CRITICAL,
                "Not in a Git repository",
                fix_command="git init"
            )
            return
        
        self.log_result(
            "Git Repository",
            ValidationLevel.SUCCESS,
            "Git repository detected"
        )
        
        # Check git hooks
        hooks_dir = self.project_root / '.githooks'
        if hooks_dir.exists():
            hooks = list(hooks_dir.glob('*'))
            if hooks:
                self.log_result(
                    "Git Hooks",
                    ValidationLevel.SUCCESS,
                    f"Custom git hooks configured ({len(hooks)} hooks)"
                )
            else:
                self.log_result(
                    "Git Hooks",
                    ValidationLevel.INFO,
                    "Git hooks directory exists but no hooks configured"
                )
        else:
            self.log_result(
                "Git Hooks",
                ValidationLevel.INFO,
                "No custom git hooks configured",
                fix_command="Run setup script to configure security hooks"
            )
        
        # Check gitignore
        gitignore = self.project_root / '.gitignore'
        if gitignore.exists():
            with open(gitignore, 'r') as f:
                content = f.read()
            
            ai_patterns = ['.ai_temp/', '.claude_temp/', '.copilot_cache/']
            configured_patterns = [p for p in ai_patterns if p in content]
            
            if configured_patterns:
                self.log_result(
                    "Git Ignore (AI)",
                    ValidationLevel.SUCCESS,
                    f"AI development patterns in .gitignore ({len(configured_patterns)}/3)"
                )
            else:
                self.log_result(
                    "Git Ignore (AI)",
                    ValidationLevel.INFO,
                    "AI development patterns not in .gitignore",
                    fix_command="Add AI temp directories to .gitignore"
                )
        else:
            self.log_result(
                "Git Ignore",
                ValidationLevel.WARNING,
                ".gitignore not found"
            )

    def check_project_structure(self):
        """Check project structure and key files"""
        print("\n🔍 Checking Project Structure...")
        
        key_files = {
            'CLAUDE.md': 'Claude Code instructions',
            'Makefile': 'Build automation',
            'Cargo.toml': 'Rust workspace configuration',
            '.env.example': 'Environment template',
            'README.md': 'Project documentation'
        }
        
        for filename, description in key_files.items():
            filepath = self.project_root / filename
            if filepath.exists():
                self.log_result(
                    f"Project File: {filename}",
                    ValidationLevel.SUCCESS,
                    f"{description} exists"
                )
            else:
                self.log_result(
                    f"Project File: {filename}",
                    ValidationLevel.WARNING,
                    f"{description} missing"
                )
        
        # Check directory structure
        key_directories = ['src', 'scripts', 'docs', 'tests']
        
        for dirname in key_directories:
            dirpath = self.project_root / dirname
            if dirpath.exists() and dirpath.is_dir():
                file_count = len(list(dirpath.rglob('*')))
                self.log_result(
                    f"Directory: {dirname}",
                    ValidationLevel.SUCCESS,
                    f"Directory exists ({file_count} files)"
                )
            else:
                self.log_result(
                    f"Directory: {dirname}",
                    ValidationLevel.WARNING,
                    f"Directory missing or empty"
                )

    def check_environment_files(self):
        """Check environment configuration files"""
        print("\n🔍 Checking Environment Configuration...")
        
        env_example = self.project_root / '.env.example'
        env_file = self.project_root / '.env'
        
        if env_example.exists():
            self.log_result(
                "Environment Template",
                ValidationLevel.SUCCESS,
                ".env.example exists"
            )
        else:
            self.log_result(
                "Environment Template",
                ValidationLevel.WARNING,
                ".env.example missing"
            )
        
        if env_file.exists():
            self.log_result(
                "Environment Config",
                ValidationLevel.SUCCESS,
                ".env file exists"
            )
            
            # Check for placeholder values
            with open(env_file, 'r') as f:
                content = f.read()
            
            placeholders = [
                'your_secure_password_here',
                'your_api_key_here',
                'your_secret_key_here'
            ]
            
            found_placeholders = [p for p in placeholders if p in content]
            
            if found_placeholders:
                self.log_result(
                    "Environment Security",
                    ValidationLevel.WARNING,
                    f"Found placeholder values in .env ({len(found_placeholders)} placeholders)",
                    fix_command="Replace placeholder values with actual configuration"
                )
            else:
                self.log_result(
                    "Environment Security",
                    ValidationLevel.SUCCESS,
                    "No placeholder values found in .env"
                )
        else:
            self.log_result(
                "Environment Config",
                ValidationLevel.WARNING,
                ".env file missing",
                fix_command="cp .env.example .env && configure values"
            )

    def generate_report(self) -> Dict:
        """Generate comprehensive validation report"""
        critical_count = sum(1 for r in self.results if r.status == ValidationLevel.CRITICAL)
        warning_count = sum(1 for r in self.results if r.status == ValidationLevel.WARNING)
        success_count = sum(1 for r in self.results if r.status == ValidationLevel.SUCCESS)
        info_count = sum(1 for r in self.results if r.status == ValidationLevel.INFO)
        
        overall_status = "READY"
        if critical_count > 0:
            overall_status = "CRITICAL_ISSUES"
        elif warning_count > 5:
            overall_status = "NEEDS_ATTENTION"
        elif warning_count > 0:
            overall_status = "MINOR_ISSUES"
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'overall_status': overall_status,
            'summary': {
                'total_checks': len(self.results),
                'critical': critical_count,
                'warnings': warning_count,
                'success': success_count,
                'info': info_count
            },
            'results': [asdict(r) for r in self.results]
        }
        
        return report

    def run_all_validations(self):
        """Run all validation checks"""
        print("🚀 Syn_OS AI Development Environment Validator")
        print("=" * 60)
        
        try:
            self.check_tool_availability()
            self.check_vscode_configuration()
            self.check_installed_extensions()
            self.check_rust_environment()
            self.check_python_environment()
            self.check_docker_environment()
            self.check_git_configuration()
            self.check_project_structure()
            self.check_environment_files()
        except KeyboardInterrupt:
            print("\n⚠️  Validation interrupted by user")
            return None
        except Exception as e:
            print(f"\n❌ Validation failed with error: {e}")
            return None
        
        return self.generate_report()

def main():
    """Main function"""
    validator = DevEnvironmentValidator()
    report = validator.run_all_validations()
    
    if report is None:
        sys.exit(1)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    summary = report['summary']
    status_colors = {
        'READY': '\033[0;32m',           # Green
        'MINOR_ISSUES': '\033[1;33m',    # Yellow
        'NEEDS_ATTENTION': '\033[0;33m', # Yellow
        'CRITICAL_ISSUES': '\033[0;31m'  # Red
    }
    
    color = status_colors.get(report['overall_status'], '')
    reset = '\033[0m'
    
    print(f"Overall Status: {color}{report['overall_status']}{reset}")
    print(f"Total Checks: {summary['total_checks']}")
    print(f"✅ Success: {summary['success']}")
    print(f"ℹ️  Info: {summary['info']}")
    print(f"⚠️  Warnings: {summary['warnings']}")
    print(f"❌ Critical: {summary['critical']}")
    
    # Save report
    report_file = Path('results') / 'ai_dev_environment_validation.json'
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    if report['overall_status'] in ['CRITICAL_ISSUES']:
        print("\n🚨 Critical issues found! Please address them before development.")
        print("💡 Run the setup script: ./scripts/setup-modern-ai-dev.sh")
        sys.exit(1)
    elif report['overall_status'] in ['NEEDS_ATTENTION', 'MINOR_ISSUES']:
        print("\n⚠️  Some issues found. Consider running the setup script for optimal experience.")
        print("💡 Run: ./scripts/setup-modern-ai-dev.sh")
    else:
        print("\n🎉 Environment is ready for AI-assisted development!")
    
    print("\n🤖 AI Development Features Available:")
    print("  • GitHub Copilot for intelligent code completion")
    print("  • Claude Code for advanced AI assistance")
    print("  • Automated security scanning and validation")
    print("  • Optimized debugging and testing workflows")

if __name__ == "__main__":
    main()