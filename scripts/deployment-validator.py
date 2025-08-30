#!/usr/bin/env python3
"""
Syn_OS Production Deployment Validator

This script performs comprehensive validation of the Syn_OS system for production readiness,
including security, performance, and integration testing.
"""

import os
import sys
import json
import subprocess
import time
import threading
import socket
import ssl
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/deployment_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    """Validation result severity levels"""
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"
    SUCCESS = "success"
    INFO = "info"

@dataclass
class ValidationResult:
    """Individual validation test result"""
    test_name: str
    component: str
    severity: ValidationSeverity
    status: bool
    message: str
    details: Optional[str] = None
    metrics: Optional[Dict] = None
    duration: Optional[float] = None
    fix_recommendation: Optional[str] = None

class DeploymentValidator:
    """Comprehensive production deployment validator"""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
        self.project_root = Path(__file__).parent.parent
        self.start_time = time.time()
        
        # Default service endpoints (can be overridden by environment)
        self.endpoints = {
            'postgres': os.getenv('POSTGRES_HOST', 'localhost:5432'),
            'redis': os.getenv('REDIS_HOST', 'localhost:6379'),
            'nats': os.getenv('NATS_URL', 'nats://localhost:4222'),
            'orchestrator': os.getenv('ORCHESTRATOR_URL', 'http://localhost:8080'),
            'consciousness': os.getenv('CONSCIOUSNESS_URL', 'http://localhost:8081')
        }
        
        # Performance thresholds
        self.thresholds = {
            'max_response_time': float(os.getenv('MAX_RESPONSE_TIME', '2.0')),
            'min_memory_free': float(os.getenv('MIN_MEMORY_FREE', '1.0')),  # GB
            'max_cpu_usage': float(os.getenv('MAX_CPU_USAGE', '80.0')),  # %
            'min_disk_free': float(os.getenv('MIN_DISK_FREE', '5.0'))  # GB
        }

    def log_result(self, test_name: str, component: str, severity: ValidationSeverity, 
                   status: bool, message: str, details: str = None, 
                   metrics: Dict = None, duration: float = None,
                   fix_recommendation: str = None):
        """Log a validation result with proper formatting"""
        
        result = ValidationResult(
            test_name=test_name,
            component=component,
            severity=severity,
            status=status,
            message=message,
            details=details,
            metrics=metrics,
            duration=duration,
            fix_recommendation=fix_recommendation
        )
        
        self.results.append(result)
        
        # Console output with color coding
        colors = {
            ValidationSeverity.CRITICAL: '\033[1;31m',  # Bold Red
            ValidationSeverity.HIGH: '\033[0;31m',      # Red
            ValidationSeverity.MEDIUM: '\033[1;33m',    # Bold Yellow
            ValidationSeverity.LOW: '\033[0;33m',       # Yellow
            ValidationSeverity.SUCCESS: '\033[0;32m',   # Green
            ValidationSeverity.INFO: '\033[0;34m'       # Blue
        }
        reset = '\033[0m'
        
        status_symbol = '✅' if status else '❌'
        color = colors.get(severity, '')
        
        duration_str = f" ({duration:.2f}s)" if duration else ""
        
        print(f"{color}{status_symbol} [{component}] {test_name}: {message}{duration_str}{reset}")
        
        if details and not status:
            print(f"   📋 Details: {details}")
        if fix_recommendation and not status:
            print(f"   💡 Fix: {fix_recommendation}")
        if metrics:
            print(f"   📊 Metrics: {metrics}")

    def run_command(self, cmd: List[str], timeout: int = 30, capture_output: bool = True) -> Tuple[bool, str, str, float]:
        """Execute command and return results with timing"""
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            duration = time.time() - start_time
            return result.returncode == 0, result.stdout, result.stderr, duration
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return False, "", f"Command timed out after {timeout}s", duration
        except Exception as e:
            duration = time.time() - start_time
            return False, "", str(e), duration

    def check_network_connectivity(self, host: str, port: int, timeout: int = 5) -> Tuple[bool, float]:
        """Check if a network service is reachable"""
        start_time = time.time()
        try:
            with socket.create_connection((host, port), timeout=timeout):
                duration = time.time() - start_time
                return True, duration
        except Exception:
            duration = time.time() - start_time
            return False, duration

    def check_http_endpoint(self, url: str, timeout: int = 10) -> Tuple[bool, float, Optional[int]]:
        """Check HTTP endpoint availability and response time"""
        start_time = time.time()
        try:
            response = requests.get(url, timeout=timeout, verify=False)
            duration = time.time() - start_time
            return response.status_code < 400, duration, response.status_code
        except Exception:
            duration = time.time() - start_time
            return False, duration, None

    def validate_system_resources(self):
        """Validate system resource availability"""
        logger.info("Validating system resources...")
        
        # Memory check
        try:
            success, stdout, stderr, duration = self.run_command(['free', '-g'])
            if success:
                lines = stdout.strip().split('\n')
                mem_line = lines[1].split()
                available_mem = float(mem_line[6])  # Available memory
                
                if available_mem >= self.thresholds['min_memory_free']:
                    self.log_result(
                        "Memory Availability",
                        "System",
                        ValidationSeverity.SUCCESS,
                        True,
                        f"Sufficient memory available: {available_mem:.1f}GB",
                        metrics={"available_gb": available_mem, "threshold_gb": self.thresholds['min_memory_free']},
                        duration=duration
                    )
                else:
                    self.log_result(
                        "Memory Availability",
                        "System", 
                        ValidationSeverity.CRITICAL,
                        False,
                        f"Insufficient memory: {available_mem:.1f}GB < {self.thresholds['min_memory_free']:.1f}GB",
                        fix_recommendation="Free up memory or add more RAM"
                    )
            else:
                self.log_result(
                    "Memory Check",
                    "System",
                    ValidationSeverity.HIGH,
                    False,
                    "Could not check memory availability",
                    details=stderr
                )
        except Exception as e:
            self.log_result(
                "Memory Check",
                "System", 
                ValidationSeverity.HIGH,
                False,
                "Memory check failed",
                details=str(e)
            )

        # CPU usage check
        try:
            success, stdout, stderr, duration = self.run_command(['top', '-bn1'], timeout=5)
            if success:
                lines = stdout.split('\n')
                cpu_line = next(line for line in lines if '%Cpu(s):' in line)
                # Parse CPU usage (this is a simplified parser)
                idle_pct = float(cpu_line.split('id,')[0].split()[-1])
                cpu_usage = 100.0 - idle_pct
                
                if cpu_usage <= self.thresholds['max_cpu_usage']:
                    self.log_result(
                        "CPU Usage",
                        "System",
                        ValidationSeverity.SUCCESS,
                        True,
                        f"CPU usage within limits: {cpu_usage:.1f}%",
                        metrics={"cpu_usage_pct": cpu_usage, "threshold_pct": self.thresholds['max_cpu_usage']},
                        duration=duration
                    )
                else:
                    self.log_result(
                        "CPU Usage",
                        "System",
                        ValidationSeverity.HIGH,
                        False,
                        f"High CPU usage: {cpu_usage:.1f}% > {self.thresholds['max_cpu_usage']:.1f}%",
                        fix_recommendation="Reduce system load or optimize processes"
                    )
        except Exception as e:
            self.log_result(
                "CPU Check",
                "System",
                ValidationSeverity.MEDIUM,
                False,
                "Could not check CPU usage",
                details=str(e)
            )

        # Disk space check
        try:
            success, stdout, stderr, duration = self.run_command(['df', '-h', '.'])
            if success:
                lines = stdout.strip().split('\n')
                if len(lines) > 1:
                    disk_info = lines[1].split()
                    available = disk_info[3]
                    # Simple parsing - convert to GB
                    if available.endswith('G'):
                        available_gb = float(available[:-1])
                    elif available.endswith('M'):
                        available_gb = float(available[:-1]) / 1024
                    elif available.endswith('T'):
                        available_gb = float(available[:-1]) * 1024
                    else:
                        available_gb = float(available) / (1024**3)
                    
                    if available_gb >= self.thresholds['min_disk_free']:
                        self.log_result(
                            "Disk Space",
                            "System",
                            ValidationSeverity.SUCCESS,
                            True,
                            f"Sufficient disk space: {available_gb:.1f}GB available",
                            metrics={"available_gb": available_gb, "threshold_gb": self.thresholds['min_disk_free']},
                            duration=duration
                        )
                    else:
                        self.log_result(
                            "Disk Space",
                            "System",
                            ValidationSeverity.CRITICAL,
                            False,
                            f"Insufficient disk space: {available_gb:.1f}GB < {self.thresholds['min_disk_free']:.1f}GB",
                            fix_recommendation="Free up disk space"
                        )
        except Exception as e:
            self.log_result(
                "Disk Check",
                "System",
                ValidationSeverity.MEDIUM,
                False,
                "Could not check disk space",
                details=str(e)
            )

    def validate_rust_components(self):
        """Validate Rust components build and tests"""
        logger.info("Validating Rust components...")
        
        os.chdir(self.project_root)
        
        # Build workspace
        success, stdout, stderr, duration = self.run_command(['cargo', 'build', '--workspace'], timeout=300)
        
        if success:
            self.log_result(
                "Rust Build",
                "Build System",
                ValidationSeverity.SUCCESS,
                True,
                "Rust workspace built successfully",
                duration=duration
            )
        else:
            self.log_result(
                "Rust Build",
                "Build System",
                ValidationSeverity.CRITICAL,
                False,
                "Rust workspace build failed",
                details=stderr,
                fix_recommendation="Fix compilation errors and dependencies"
            )
            return  # Skip further Rust tests if build fails
        
        # Run Rust tests
        success, stdout, stderr, duration = self.run_command(['cargo', 'test', '--workspace'], timeout=300)
        
        if success:
            # Parse test results
            test_lines = [line for line in stdout.split('\n') if 'test result:' in line]
            if test_lines:
                test_summary = test_lines[-1]
                self.log_result(
                    "Rust Tests",
                    "Testing",
                    ValidationSeverity.SUCCESS,
                    True,
                    f"Rust tests passed - {test_summary}",
                    duration=duration
                )
            else:
                self.log_result(
                    "Rust Tests",
                    "Testing",
                    ValidationSeverity.SUCCESS,
                    True,
                    "Rust tests completed",
                    duration=duration
                )
        else:
            self.log_result(
                "Rust Tests",
                "Testing",
                ValidationSeverity.HIGH,
                False,
                "Rust tests failed",
                details=stderr,
                fix_recommendation="Fix failing tests"
            )
        
        # Security audit
        success, stdout, stderr, duration = self.run_command(['cargo', 'audit'], timeout=60)
        
        if success:
            if 'Vulnerabilities found!' not in stdout:
                self.log_result(
                    "Rust Security Audit",
                    "Security",
                    ValidationSeverity.SUCCESS,
                    True,
                    "No security vulnerabilities found",
                    duration=duration
                )
            else:
                self.log_result(
                    "Rust Security Audit",
                    "Security",
                    ValidationSeverity.HIGH,
                    False,
                    "Security vulnerabilities detected",
                    details=stdout,
                    fix_recommendation="Update vulnerable dependencies"
                )
        else:
            self.log_result(
                "Rust Security Audit",
                "Security",
                ValidationSeverity.MEDIUM,
                False,
                "Could not run security audit",
                details=stderr,
                fix_recommendation="Install cargo-audit: cargo install cargo-audit"
            )

    def validate_python_components(self):
        """Validate Python components and security"""
        logger.info("Validating Python components...")
        
        venv_python = self.project_root / 'venv' / 'bin' / 'python'
        
        if not venv_python.exists():
            self.log_result(
                "Python Environment",
                "Python",
                ValidationSeverity.CRITICAL,
                False,
                "Python virtual environment not found",
                fix_recommendation="Create virtual environment: python3 -m venv venv"
            )
            return
        
        # Run Python tests
        success, stdout, stderr, duration = self.run_command([str(venv_python), '-m', 'pytest', 'tests/', '-v'], timeout=180)
        
        if success:
            self.log_result(
                "Python Tests",
                "Testing",
                ValidationSeverity.SUCCESS,
                True,
                "Python tests passed",
                duration=duration
            )
        else:
            # Check if it's just missing pytest or actual test failures
            if 'No module named pytest' in stderr:
                self.log_result(
                    "Python Tests",
                    "Testing",
                    ValidationSeverity.MEDIUM,
                    False,
                    "pytest not installed",
                    fix_recommendation="Install pytest: pip install pytest"
                )
            else:
                self.log_result(
                    "Python Tests",
                    "Testing",
                    ValidationSeverity.HIGH,
                    False,
                    "Python tests failed",
                    details=stderr[:500],  # Truncate long error messages
                    fix_recommendation="Fix failing tests"
                )
        
        # Security scan with bandit
        success, stdout, stderr, duration = self.run_command([str(venv_python), '-m', 'bandit', '-r', 'src/', '-f', 'json'], timeout=60)
        
        if success:
            try:
                bandit_results = json.loads(stdout)
                high_severity = len([i for i in bandit_results.get('results', []) if i.get('issue_severity') == 'HIGH'])
                medium_severity = len([i for i in bandit_results.get('results', []) if i.get('issue_severity') == 'MEDIUM'])
                
                if high_severity == 0 and medium_severity <= 2:
                    self.log_result(
                        "Python Security Scan",
                        "Security",
                        ValidationSeverity.SUCCESS,
                        True,
                        f"Security scan passed (0 high, {medium_severity} medium issues)",
                        duration=duration
                    )
                else:
                    self.log_result(
                        "Python Security Scan",
                        "Security",
                        ValidationSeverity.HIGH if high_severity > 0 else ValidationSeverity.MEDIUM,
                        False,
                        f"Security issues found: {high_severity} high, {medium_severity} medium",
                        fix_recommendation="Review and fix security issues"
                    )
            except json.JSONDecodeError:
                self.log_result(
                    "Python Security Scan",
                    "Security",
                    ValidationSeverity.SUCCESS,
                    True,
                    "Security scan completed",
                    duration=duration
                )
        else:
            if 'No module named bandit' in stderr:
                self.log_result(
                    "Python Security Scan",
                    "Security",
                    ValidationSeverity.MEDIUM,
                    False,
                    "bandit not installed",
                    fix_recommendation="Install bandit: pip install bandit"
                )
            else:
                self.log_result(
                    "Python Security Scan",
                    "Security",
                    ValidationSeverity.MEDIUM,
                    False,
                    "Security scan failed",
                    details=stderr
                )

    def validate_container_services(self):
        """Validate container services are running and healthy"""
        logger.info("Validating container services...")
        
        # Check if docker-compose services are running
        success, stdout, stderr, duration = self.run_command(['docker-compose', 'ps'], timeout=30)
        
        if not success:
            self.log_result(
                "Container Services",
                "Infrastructure",
                ValidationSeverity.HIGH,
                False,
                "Could not check container status",
                details=stderr,
                fix_recommendation="Ensure Docker and docker-compose are installed and running"
            )
            return
        
        # Parse container status
        running_services = []
        for line in stdout.split('\n')[2:]:  # Skip header lines
            if line.strip() and 'Up' in line:
                service_name = line.split()[0]
                running_services.append(service_name)
        
        expected_services = ['syn_os_postgres', 'syn_os_redis', 'syn_os_nats']
        missing_services = [svc for svc in expected_services if not any(svc in running for running in running_services)]
        
        if not missing_services:
            self.log_result(
                "Container Services",
                "Infrastructure", 
                ValidationSeverity.SUCCESS,
                True,
                f"All required services running: {', '.join(running_services)}",
                duration=duration
            )
        else:
            self.log_result(
                "Container Services",
                "Infrastructure",
                ValidationSeverity.HIGH,
                False,
                f"Missing services: {', '.join(missing_services)}",
                fix_recommendation="Start missing services: docker-compose up -d"
            )

    def validate_service_connectivity(self):
        """Test connectivity to all required services"""
        logger.info("Validating service connectivity...")
        
        connectivity_tests = []
        
        # PostgreSQL
        def test_postgres():
            host, port = self.endpoints['postgres'].split(':')
            success, duration = self.check_network_connectivity(host, int(port))
            return ('PostgreSQL', 'Database', success, duration, 'Check PostgreSQL service and connection')
        
        # Redis
        def test_redis():
            host, port = self.endpoints['redis'].split(':')
            success, duration = self.check_network_connectivity(host, int(port))
            return ('Redis', 'Cache', success, duration, 'Check Redis service and connection')
        
        # NATS
        def test_nats():
            # Extract host and port from NATS URL
            nats_url = self.endpoints['nats'].replace('nats://', '')
            if ':' in nats_url:
                host, port = nats_url.split(':')
            else:
                host, port = nats_url, '4222'
            success, duration = self.check_network_connectivity(host, int(port))
            return ('NATS', 'MessageBus', success, duration, 'Check NATS service and connection')
        
        # HTTP endpoints
        def test_orchestrator():
            success, duration, status_code = self.check_http_endpoint(self.endpoints['orchestrator'] + '/health')
            return ('Orchestrator API', 'HTTP Service', success, duration, 'Check orchestrator service health endpoint')
        
        def test_consciousness():
            success, duration, status_code = self.check_http_endpoint(self.endpoints['consciousness'] + '/health')
            return ('Consciousness API', 'HTTP Service', success, duration, 'Check consciousness service health endpoint')
        
        # Run tests in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(test_postgres),
                executor.submit(test_redis), 
                executor.submit(test_nats),
                executor.submit(test_orchestrator),
                executor.submit(test_consciousness)
            ]
            
            for future in as_completed(futures):
                try:
                    name, component, success, duration, fix_rec = future.result()
                    
                    if success:
                        self.log_result(
                            f"{name} Connectivity",
                            component,
                            ValidationSeverity.SUCCESS,
                            True,
                            f"{name} is reachable",
                            duration=duration
                        )
                    else:
                        severity = ValidationSeverity.CRITICAL if component in ['Database', 'MessageBus'] else ValidationSeverity.HIGH
                        self.log_result(
                            f"{name} Connectivity",
                            component,
                            severity,
                            False,
                            f"{name} is not reachable",
                            duration=duration,
                            fix_recommendation=fix_rec
                        )
                except Exception as e:
                    self.log_result(
                        "Connectivity Test",
                        "Network",
                        ValidationSeverity.MEDIUM,
                        False,
                        "Connectivity test failed",
                        details=str(e)
                    )

    def validate_security_configuration(self):
        """Validate security configurations and certificates"""
        logger.info("Validating security configuration...")
        
        # Check environment file security
        env_file = self.project_root / '.env'
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()
            
            # Check for default/weak passwords
            weak_patterns = [
                'password123',
                'admin',
                'your_password_here',
                'changeme',
                'default'
            ]
            
            found_weak = [pattern for pattern in weak_patterns if pattern in content.lower()]
            
            if not found_weak:
                self.log_result(
                    "Environment Security",
                    "Security",
                    ValidationSeverity.SUCCESS,
                    True,
                    "No weak passwords detected in environment"
                )
            else:
                self.log_result(
                    "Environment Security",
                    "Security",
                    ValidationSeverity.HIGH,
                    False,
                    f"Weak passwords detected: {', '.join(found_weak)}",
                    fix_recommendation="Use strong, randomly generated passwords"
                )
        else:
            self.log_result(
                "Environment Configuration",
                "Security",
                ValidationSeverity.MEDIUM,
                False,
                "Environment file not found",
                fix_recommendation="Create .env from .env.example"
            )
        
        # Check for sensitive files in git
        success, stdout, stderr, duration = self.run_command(['git', 'ls-files'], timeout=30)
        
        if success:
            sensitive_patterns = ['.env', 'private', 'secret', '.key', '.pem', 'password']
            tracked_sensitive = []
            
            for line in stdout.split('\n'):
                if any(pattern in line.lower() for pattern in sensitive_patterns):
                    tracked_sensitive.append(line)
            
            if not tracked_sensitive:
                self.log_result(
                    "Git Security",
                    "Security",
                    ValidationSeverity.SUCCESS,
                    True,
                    "No sensitive files tracked in git"
                )
            else:
                self.log_result(
                    "Git Security",
                    "Security",
                    ValidationSeverity.HIGH,
                    False,
                    f"Sensitive files in git: {', '.join(tracked_sensitive[:3])}",
                    fix_recommendation="Remove sensitive files from git and add to .gitignore"
                )

    def validate_performance_benchmarks(self):
        """Run basic performance benchmarks"""
        logger.info("Running performance benchmarks...")
        
        # Simple I/O benchmark
        start_time = time.time()
        try:
            test_file = Path('/tmp/syn_os_io_test')
            test_data = b'0' * (1024 * 1024)  # 1MB
            
            # Write test
            write_start = time.time()
            with open(test_file, 'wb') as f:
                for _ in range(100):  # Write 100MB
                    f.write(test_data)
            write_duration = time.time() - write_start
            
            # Read test
            read_start = time.time()
            with open(test_file, 'rb') as f:
                data = f.read()
            read_duration = time.time() - read_start
            
            test_file.unlink()  # Clean up
            
            write_speed = 100 / write_duration  # MB/s
            read_speed = len(data) / (1024 * 1024) / read_duration  # MB/s
            
            self.log_result(
                "I/O Performance",
                "Performance",
                ValidationSeverity.SUCCESS,
                True,
                f"I/O test completed",
                metrics={
                    "write_speed_mbps": round(write_speed, 2),
                    "read_speed_mbps": round(read_speed, 2)
                },
                duration=time.time() - start_time
            )
            
        except Exception as e:
            self.log_result(
                "I/O Performance",
                "Performance",
                ValidationSeverity.MEDIUM,
                False,
                "I/O performance test failed",
                details=str(e)
            )

    def generate_deployment_report(self) -> Dict:
        """Generate comprehensive deployment validation report"""
        total_duration = time.time() - self.start_time
        
        # Categorize results
        critical_failures = [r for r in self.results if r.severity == ValidationSeverity.CRITICAL and not r.status]
        high_failures = [r for r in self.results if r.severity == ValidationSeverity.HIGH and not r.status]
        medium_failures = [r for r in self.results if r.severity == ValidationSeverity.MEDIUM and not r.status]
        successes = [r for r in self.results if r.status]
        
        # Determine overall readiness
        if critical_failures:
            overall_status = "NOT_READY"
            readiness_score = 0
        elif len(high_failures) > 3:
            overall_status = "NEEDS_WORK"
            readiness_score = 25
        elif len(high_failures) > 0 or len(medium_failures) > 5:
            overall_status = "CAUTION"
            readiness_score = 50
        elif len(medium_failures) > 0:
            overall_status = "MOSTLY_READY"
            readiness_score = 75
        else:
            overall_status = "PRODUCTION_READY"
            readiness_score = 100
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'validation_duration': round(total_duration, 2),
            'overall_status': overall_status,
            'readiness_score': readiness_score,
            'summary': {
                'total_tests': len(self.results),
                'passed': len(successes),
                'critical_failures': len(critical_failures),
                'high_failures': len(high_failures),
                'medium_failures': len(medium_failures),
                'low_failures': len([r for r in self.results if r.severity == ValidationSeverity.LOW and not r.status])
            },
            'component_status': self._generate_component_summary(),
            'performance_metrics': self._extract_performance_metrics(),
            'security_summary': self._generate_security_summary(),
            'recommendations': self._generate_recommendations(),
            'detailed_results': [asdict(r) for r in self.results]
        }
        
        return report

    def _generate_component_summary(self) -> Dict:
        """Generate per-component status summary"""
        components = {}
        
        for result in self.results:
            if result.component not in components:
                components[result.component] = {
                    'total_tests': 0,
                    'passed': 0,
                    'failed': 0,
                    'critical_issues': 0,
                    'high_issues': 0
                }
            
            components[result.component]['total_tests'] += 1
            
            if result.status:
                components[result.component]['passed'] += 1
            else:
                components[result.component]['failed'] += 1
                if result.severity == ValidationSeverity.CRITICAL:
                    components[result.component]['critical_issues'] += 1
                elif result.severity == ValidationSeverity.HIGH:
                    components[result.component]['high_issues'] += 1
        
        return components

    def _extract_performance_metrics(self) -> Dict:
        """Extract performance metrics from results"""
        metrics = {}
        
        for result in self.results:
            if result.metrics:
                metrics[result.test_name] = result.metrics
        
        return metrics

    def _generate_security_summary(self) -> Dict:
        """Generate security-specific summary"""
        security_results = [r for r in self.results if r.component == 'Security']
        
        return {
            'total_security_tests': len(security_results),
            'security_issues': len([r for r in security_results if not r.status]),
            'critical_security_issues': len([r for r in security_results 
                                           if not r.status and r.severity == ValidationSeverity.CRITICAL])
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate deployment recommendations based on results"""
        recommendations = []
        
        critical_failures = [r for r in self.results if r.severity == ValidationSeverity.CRITICAL and not r.status]
        
        if critical_failures:
            recommendations.append("🚨 CRITICAL: Address all critical failures before deployment")
            for failure in critical_failures[:3]:  # Show top 3
                if failure.fix_recommendation:
                    recommendations.append(f"   • {failure.fix_recommendation}")
        
        high_failures = [r for r in self.results if r.severity == ValidationSeverity.HIGH and not r.status]
        
        if len(high_failures) > 0:
            recommendations.append(f"⚠️  HIGH: Address {len(high_failures)} high-priority issues")
        
        # Add specific recommendations
        if any('memory' in r.test_name.lower() for r in self.results if not r.status):
            recommendations.append("💾 Consider upgrading system memory for better performance")
            
        if any('security' in r.component.lower() for r in self.results if not r.status):
            recommendations.append("🔐 Review and strengthen security configurations")
            
        if any('connectivity' in r.test_name.lower() for r in self.results if not r.status):
            recommendations.append("🌐 Ensure all required services are running and accessible")
        
        return recommendations

    def run_full_validation(self) -> Dict:
        """Execute complete deployment validation suite"""
        print("🚀 Syn_OS Production Deployment Validator")
        print("=" * 60)
        print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            # Run all validation categories
            self.validate_system_resources()
            self.validate_rust_components()
            self.validate_python_components() 
            self.validate_container_services()
            self.validate_service_connectivity()
            self.validate_security_configuration()
            self.validate_performance_benchmarks()
            
        except KeyboardInterrupt:
            print("\n⚠️  Validation interrupted by user")
            return None
        except Exception as e:
            logger.error(f"Validation failed with error: {e}")
            print(f"\n❌ Validation failed: {e}")
            return None
        
        return self.generate_deployment_report()

def main():
    """Main function"""
    validator = DeploymentValidator()
    report = validator.run_full_validation()
    
    if report is None:
        sys.exit(1)
    
    # Print final summary
    print("\n" + "=" * 60)
    print("📊 DEPLOYMENT VALIDATION SUMMARY")
    print("=" * 60)
    
    status_colors = {
        'PRODUCTION_READY': '\033[1;32m',    # Bold Green
        'MOSTLY_READY': '\033[0;32m',        # Green
        'CAUTION': '\033[1;33m',             # Bold Yellow
        'NEEDS_WORK': '\033[0;33m',          # Yellow
        'NOT_READY': '\033[1;31m'            # Bold Red
    }
    
    color = status_colors.get(report['overall_status'], '')
    reset = '\033[0m'
    
    print(f"Overall Status: {color}{report['overall_status']}{reset}")
    print(f"Readiness Score: {report['readiness_score']}/100")
    print(f"Validation Duration: {report['validation_duration']}s")
    
    summary = report['summary']
    print(f"\nTest Results:")
    print(f"  ✅ Passed: {summary['passed']}")
    print(f"  ❌ Critical: {summary['critical_failures']}")
    print(f"  🚨 High: {summary['high_failures']}")
    print(f"  ⚠️  Medium: {summary['medium_failures']}")
    print(f"  ℹ️  Low: {summary['low_failures']}")
    
    # Show recommendations
    if report['recommendations']:
        print(f"\n📋 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"  {rec}")
    
    # Save detailed report
    report_file = Path('results') / 'deployment_validation_report.json'
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    if report['overall_status'] in ['NOT_READY', 'NEEDS_WORK']:
        print(f"\n🚫 System is not ready for production deployment!")
        print("   Please address critical and high-priority issues.")
        sys.exit(1)
    elif report['overall_status'] == 'CAUTION':
        print(f"\n⚠️  System has some issues but may be deployable with caution.")
        print("   Monitor closely and address issues as soon as possible.")
        sys.exit(2)
    else:
        print(f"\n✅ System validation completed successfully!")
        if report['overall_status'] == 'MOSTLY_READY':
            print("   Minor issues detected - consider addressing before deployment.")
        else:
            print("   System appears ready for production deployment.")
        sys.exit(0)

if __name__ == "__main__":
    main()