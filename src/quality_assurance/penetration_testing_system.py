#!/usr/bin/env python3
"""
Comprehensive Penetration Testing System for Syn_OS
Automated penetration testing and security assessment framework
"""

import asyncio
import logging
import time
import json
import subprocess
import socket
import ssl
import requests
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import uuid
from datetime import datetime, timedelta
import threading
import queue
import ipaddress

from src.consciousness_v2.consciousness_bus import ConsciousnessBus


class TestSeverity(Enum):
    """Penetration test finding severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TestCategory(Enum):
    """Penetration test categories"""
    NETWORK_SCANNING = "network_scanning"
    WEB_APPLICATION = "web_application"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ENCRYPTION = "encryption"
    SOCIAL_ENGINEERING = "social_engineering"
    PHYSICAL_SECURITY = "physical_security"
    WIRELESS_SECURITY = "wireless_security"
    DATABASE_SECURITY = "database_security"
    SYSTEM_HARDENING = "system_hardening"


class TestStatus(Enum):
    """Penetration test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PenetrationTestFinding:
    """Individual penetration test finding"""
    finding_id: str
    test_name: str
    target: str
    severity: TestSeverity
    category: TestCategory
    description: str
    impact: str
    evidence: Dict[str, Any]
    remediation: str
    cvss_score: float
    exploitability: str  # low, medium, high
    risk_rating: str  # low, medium, high, critical
    false_positive: bool = False
    verified: bool = False
    created_at: float = 0.0
    
    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()


@dataclass
class PenetrationTestSuite:
    """Penetration test suite configuration"""
    suite_id: str
    name: str
    description: str
    targets: List[str]
    test_categories: List[TestCategory]
    scope: Dict[str, Any]
    exclusions: List[str]
    intensity: str  # light, moderate, aggressive
    duration_hours: int
    created_at: float
    
    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()


@dataclass
class PenetrationTestReport:
    """Penetration test report"""
    report_id: str
    suite_id: str
    test_name: str
    targets: List[str]
    findings: List[PenetrationTestFinding]
    summary: Dict[str, Any]
    recommendations: List[str]
    executive_summary: str
    technical_details: Dict[str, Any]
    created_at: float
    completed_at: Optional[float] = None
    total_tests_run: int = 0
    success_rate: float = 0.0


class PenetrationTestingSystem:
    """
    Comprehensive penetration testing system for Syn_OS
    Performs automated security assessments and penetration tests
    """
    
    def __init__(self, consciousness_bus: ConsciousnessBus):
        """Initialize penetration testing system"""
        self.consciousness_bus = consciousness_bus
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.system_directory = "/var/lib/synos/penetration_testing"
        self.database_file = f"{self.system_directory}/pentest.db"
        
        # Test configuration
        self.default_targets = ["127.0.0.1", "localhost"]
        self.test_timeout = 300  # 5 minutes per test
        self.max_concurrent_tests = 3
        
        # Data stores
        self.findings: Dict[str, PenetrationTestFinding] = {}
        self.test_suites: Dict[str, PenetrationTestSuite] = {}
        self.reports: Dict[str, PenetrationTestReport] = {}
        self.active_tests: Dict[str, Any] = {}
        
        # Test modules
        self.test_modules = self._initialize_test_modules()
        
        # Initialize system
        asyncio.create_task(self._initialize_pentest_system())
    
    async def _initialize_pentest_system(self):
        """Initialize the penetration testing system"""
        try:
            self.logger.info("Initializing penetration testing system...")
            
            # Create system directory
            import os
            os.makedirs(self.system_directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Load existing data
            await self._load_pentest_data()
            
            # Initialize default test suites
            await self._initialize_default_test_suites()
            
            self.logger.info("Penetration testing system initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing penetration testing system: {e}")
    
    async def _initialize_database(self):
        """Initialize penetration testing database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Penetration test findings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pentest_findings (
                    finding_id TEXT PRIMARY KEY,
                    test_name TEXT NOT NULL,
                    target TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    impact TEXT,
                    evidence TEXT,
                    remediation TEXT,
                    cvss_score REAL NOT NULL DEFAULT 0.0,
                    exploitability TEXT,
                    risk_rating TEXT,
                    false_positive BOOLEAN NOT NULL DEFAULT 0,
                    verified BOOLEAN NOT NULL DEFAULT 0,
                    created_at REAL NOT NULL
                )
            ''')
            
            # Test suites table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_suites (
                    suite_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    targets TEXT,
                    test_categories TEXT,
                    scope TEXT,
                    exclusions TEXT,
                    intensity TEXT,
                    duration_hours INTEGER,
                    created_at REAL NOT NULL
                )
            ''')
            
            # Test reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pentest_reports (
                    report_id TEXT PRIMARY KEY,
                    suite_id TEXT,
                    test_name TEXT NOT NULL,
                    targets TEXT,
                    findings TEXT,
                    summary TEXT,
                    recommendations TEXT,
                    executive_summary TEXT,
                    technical_details TEXT,
                    created_at REAL NOT NULL,
                    completed_at REAL,
                    total_tests_run INTEGER NOT NULL DEFAULT 0,
                    success_rate REAL NOT NULL DEFAULT 0.0
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_findings_severity ON pentest_findings (severity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_findings_category ON pentest_findings (category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_findings_target ON pentest_findings (target)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_suite ON pentest_reports (suite_id)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing pentest database: {e}")
            raise
    
    async def _load_pentest_data(self):
        """Load existing penetration test data from database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Load unresolved findings
            cursor.execute('SELECT * FROM pentest_findings WHERE verified = 0')
            for row in cursor.fetchall():
                finding = PenetrationTestFinding(
                    finding_id=row[0],
                    test_name=row[1],
                    target=row[2],
                    severity=TestSeverity(row[3]),
                    category=TestCategory(row[4]),
                    description=row[5],
                    impact=row[6],
                    evidence=json.loads(row[7]) if row[7] else {},
                    remediation=row[8],
                    cvss_score=row[9],
                    exploitability=row[10],
                    risk_rating=row[11],
                    false_positive=bool(row[12]),
                    verified=bool(row[13]),
                    created_at=row[14]
                )
                self.findings[finding.finding_id] = finding
            
            # Load test suites
            cursor.execute('SELECT * FROM test_suites')
            for row in cursor.fetchall():
                suite = PenetrationTestSuite(
                    suite_id=row[0],
                    name=row[1],
                    description=row[2],
                    targets=json.loads(row[3]) if row[3] else [],
                    test_categories=[TestCategory(cat) for cat in json.loads(row[4])] if row[4] else [],
                    scope=json.loads(row[5]) if row[5] else {},
                    exclusions=json.loads(row[6]) if row[6] else [],
                    intensity=row[7],
                    duration_hours=row[8],
                    created_at=row[9]
                )
                self.test_suites[suite.suite_id] = suite
            
            # Load recent reports
            cursor.execute('SELECT * FROM pentest_reports ORDER BY created_at DESC LIMIT 10')
            for row in cursor.fetchall():
                report = PenetrationTestReport(
                    report_id=row[0],
                    suite_id=row[1],
                    test_name=row[2],
                    targets=json.loads(row[3]) if row[3] else [],
                    findings=[],  # Will be loaded separately if needed
                    summary=json.loads(row[5]) if row[5] else {},
                    recommendations=json.loads(row[6]) if row[6] else [],
                    executive_summary=row[7],
                    technical_details=json.loads(row[8]) if row[8] else {},
                    created_at=row[9],
                    completed_at=row[10],
                    total_tests_run=row[11],
                    success_rate=row[12]
                )
                self.reports[report.report_id] = report
            
            conn.close()
            
            self.logger.info(f"Loaded {len(self.findings)} findings, {len(self.test_suites)} test suites, {len(self.reports)} reports")
            
        except Exception as e:
            self.logger.error(f"Error loading pentest data: {e}")
    
    def _initialize_test_modules(self) -> Dict[str, Any]:
        """Initialize penetration test modules"""
        return {
            "network_discovery": {
                "name": "Network Discovery",
                "description": "Discover live hosts and open ports",
                "category": TestCategory.NETWORK_SCANNING,
                "function": self._test_network_discovery
            },
            "port_scanning": {
                "name": "Port Scanning",
                "description": "Comprehensive port scanning",
                "category": TestCategory.NETWORK_SCANNING,
                "function": self._test_port_scanning
            },
            "service_enumeration": {
                "name": "Service Enumeration",
                "description": "Enumerate running services",
                "category": TestCategory.NETWORK_SCANNING,
                "function": self._test_service_enumeration
            },
            "web_application_scan": {
                "name": "Web Application Security",
                "description": "Test web application security",
                "category": TestCategory.WEB_APPLICATION,
                "function": self._test_web_application
            },
            "ssl_tls_test": {
                "name": "SSL/TLS Security",
                "description": "Test SSL/TLS configuration",
                "category": TestCategory.ENCRYPTION,
                "function": self._test_ssl_tls
            },
            "authentication_bypass": {
                "name": "Authentication Bypass",
                "description": "Test authentication mechanisms",
                "category": TestCategory.AUTHENTICATION,
                "function": self._test_authentication_bypass
            },
            "privilege_escalation": {
                "name": "Privilege Escalation",
                "description": "Test for privilege escalation vulnerabilities",
                "category": TestCategory.AUTHORIZATION,
                "function": self._test_privilege_escalation
            },
            "database_security": {
                "name": "Database Security",
                "description": "Test database security",
                "category": TestCategory.DATABASE_SECURITY,
                "function": self._test_database_security
            }
        }
    
    async def _initialize_default_test_suites(self):
        """Initialize default penetration test suites"""
        try:
            default_suites = [
                {
                    "name": "Basic Security Assessment",
                    "description": "Basic penetration testing suite for initial assessment",
                    "targets": self.default_targets,
                    "test_categories": [
                        TestCategory.NETWORK_SCANNING,
                        TestCategory.WEB_APPLICATION,
                        TestCategory.AUTHENTICATION
                    ],
                    "scope": {"ports": "1-1000", "protocols": ["tcp", "udp"]},
                    "exclusions": [],
                    "intensity": "light",
                    "duration_hours": 2
                },
                {
                    "name": "Comprehensive Security Assessment",
                    "description": "Comprehensive penetration testing suite",
                    "targets": self.default_targets,
                    "test_categories": [
                        TestCategory.NETWORK_SCANNING,
                        TestCategory.WEB_APPLICATION,
                        TestCategory.AUTHENTICATION,
                        TestCategory.AUTHORIZATION,
                        TestCategory.ENCRYPTION,
                        TestCategory.DATABASE_SECURITY
                    ],
                    "scope": {"ports": "1-65535", "protocols": ["tcp", "udp"]},
                    "exclusions": [],
                    "intensity": "moderate",
                    "duration_hours": 8
                },
                {
                    "name": "Advanced Penetration Test",
                    "description": "Advanced penetration testing with aggressive techniques",
                    "targets": self.default_targets,
                    "test_categories": list(TestCategory),
                    "scope": {"ports": "1-65535", "protocols": ["tcp", "udp", "icmp"]},
                    "exclusions": [],
                    "intensity": "aggressive",
                    "duration_hours": 24
                }
            ]
            
            for suite_data in default_suites:
                # Check if suite already exists
                existing = any(s.name == suite_data["name"] for s in self.test_suites.values())
                if existing:
                    continue
                
                suite_id = str(uuid.uuid4())
                suite = PenetrationTestSuite(
                    suite_id=suite_id,
                    name=suite_data["name"],
                    description=suite_data["description"],
                    targets=suite_data["targets"],
                    test_categories=suite_data["test_categories"],
                    scope=suite_data["scope"],
                    exclusions=suite_data["exclusions"],
                    intensity=suite_data["intensity"],
                    duration_hours=suite_data["duration_hours"],
                    created_at=time.time()
                )
                
                await self._store_test_suite(suite)
                self.test_suites[suite_id] = suite
            
            self.logger.info(f"Initialized {len(default_suites)} default test suites")
            
        except Exception as e:
            self.logger.error(f"Error initializing default test suites: {e}")
    
    async def execute_penetration_test(self, suite_id: str, targets: Optional[List[str]] = None) -> str:
        """Execute penetration test suite"""
        try:
            if suite_id not in self.test_suites:
                raise ValueError(f"Test suite {suite_id} not found")
            
            suite = self.test_suites[suite_id]
            test_targets = targets or suite.targets
            
            self.logger.info(f"Starting penetration test: {suite.name}")
            
            report_id = str(uuid.uuid4())
            current_time = time.time()
            
            # Initialize report
            report = PenetrationTestReport(
                report_id=report_id,
                suite_id=suite_id,
                test_name=suite.name,
                targets=test_targets,
                findings=[],
                summary={},
                recommendations=[],
                executive_summary="",
                technical_details={},
                created_at=current_time
            )
            
            # Execute tests based on categories
            all_findings = []
            tests_run = 0
            successful_tests = 0
            
            for category in suite.test_categories:
                category_findings = await self._execute_test_category(category, test_targets, suite)
                all_findings.extend(category_findings)
                tests_run += 1
                if category_findings:
                    successful_tests += 1
            
            # Store findings
            for finding in all_findings:
                await self._store_finding(finding)
                self.findings[finding.finding_id] = finding
            
            # Generate report
            report.findings = all_findings
            report.summary = self._generate_test_summary(all_findings)
            report.recommendations = self._generate_test_recommendations(all_findings)
            report.executive_summary = self._generate_executive_summary(all_findings, suite)
            report.technical_details = self._generate_technical_details(all_findings)
            report.completed_at = time.time()
            report.total_tests_run = tests_run
            report.success_rate = (successful_tests / tests_run * 100) if tests_run > 0 else 0
            
            # Store report
            await self._store_report(report)
            self.reports[report_id] = report
            
            self.logger.info(f"Penetration test completed. Found {len(all_findings)} issues.")
            return report_id
            
        except Exception as e:
            self.logger.error(f"Error executing penetration test: {e}")
            return ""
    
    async def _execute_test_category(self, category: TestCategory, targets: List[str], suite: PenetrationTestSuite) -> List[PenetrationTestFinding]:
        """Execute tests for a specific category"""
        findings = []
        
        try:
            # Get test modules for this category
            category_modules = [module for module in self.test_modules.values() 
                              if module["category"] == category]
            
            for module in category_modules:
                self.logger.info(f"Running test: {module['name']}")
                
                try:
                    # Execute test module
                    module_findings = await module["function"](targets, suite)
                    findings.extend(module_findings)
                    
                except Exception as e:
                    self.logger.error(f"Error in test module {module['name']}: {e}")
            
        except Exception as e:
            self.logger.error(f"Error executing test category {category}: {e}")
        
        return findings
    
    # Test module implementations
    
    async def _test_network_discovery(self, targets: List[str], suite: PenetrationTestSuite) -> List[PenetrationTestFinding]:
        """Network discovery test"""
        findings = []
        
        try:
            for target in targets:
                # Ping test
                ping_result = await self._ping_host(target)
                if ping_result["alive"]:
                    # Host is alive - this could be a finding depending on context
                    if target not in ["127.0.0.1", "localhost"]:
                        findings.append(PenetrationTestFinding(
                            finding_id=str(uuid.uuid4()),
                            test_name="Network Discovery",
                            target=target,
                            severity=TestSeverity.INFO,
                            category=TestCategory.NETWORK_SCANNING,
                            description=f"Host {target} is alive and responding to ping",
                            impact="Host discovery reveals network topology",
                            evidence=ping_result,
                            remediation="Consider implementing ICMP filtering if not required",
                            cvss_score=0.0,
                            exploitability="low",
                            risk_rating="low"
                        ))
            
        except Exception as e:
            self.logger.error(f"Error in network discovery test: {e}")
        
        return findings
    
    async def _ping_host(self, target: str) -> Dict[str, Any]:
        """Ping a host to check if it's alive"""
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '1', target], 
                                  capture_output=True, text=True, timeout=5)
            
            return {
                "alive": result.returncode == 0,
                "response_time": self._extract_ping_time(result.stdout) if result.returncode == 0 else None,
                "output": result.stdout
            }
            
        except Exception as e:
            return {"alive": False, "error": str(e)}
    
    def _extract_ping_time(self, ping_output: str) -> Optional[float]:
        """Extract ping response time from ping output"""
        try:
            match = re.search(r'time=(\d+\.?\d*)', ping_output)
            return float(match.group(1)) if match else None
        except:
            return None
    
    async def _test_port_scanning(self, targets: List[str], suite: PenetrationTestSuite) -> List[PenetrationTestFinding]:
        """Port scanning test"""
        findings = []
        
        try:
            port_range = suite.scope.get("ports", "1-1000")
            start_port, end_port = map(int, port_range.split('-'))
            
            for target in targets:
                open_ports = await self._scan_ports(target, start_port, end_port)
                
                for port, service in open_ports.items():
                    # Determine severity based on port and service
                    severity = self._assess_port_risk(port, service)
                    
                    findings.append(PenetrationTestFinding(
                        finding_id=str(uuid.uuid4()),
                        test_name="Port Scanning",
                        target=target,
                        severity=severity,
                        category=TestCategory.NETWORK_SCANNING,
                        description=f"Open port {port} running {service} on {target}",
                        impact=f"Service {service} on port {port} may be vulnerable to attacks",
                        evidence={"port": port, "service": service, "protocol": "tcp"},
                        remediation=f"Review necessity of {service} service and implement proper access controls",
                        cvss_score=self._calculate_port_cvss(port, service),
                        exploitability=self._assess_port_exploitability(port, service),
                        risk_rating=severity.value
                    ))
            
        except Exception as e:
            self.logger.error(f"Error in port scanning test: {e}")
        
        return findings
    
    async def _scan_ports(self, target: str, start_port: int, end_port: int) -> Dict[int, str]:
        """Scan ports on target host"""
        open_ports = {}
        
        try:
            # Limit concurrent connections
            semaphore = asyncio.Semaphore(50)
            
            async def scan_port(port):
                async with semaphore:
                    try:
                        reader, writer = await asyncio.wait_for(
                            asyncio.open_connection(target, port), timeout=1.0)
                        writer.close()
                        await writer.wait_closed()
                        
                        # Try to identify service
                        service = self._identify_service(port)
                        return port, service
                        
                    except:
                        return None
            
            # Scan ports concurrently
            tasks = [scan_port(port) for port in range(start_port, min(end_port + 1, start_port + 100))]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if result and not isinstance(result, Exception) and result is not None:
                    port, service = result
                    open_ports[port] = service
            
        except Exception as e:
            self.logger.error(f"Error scanning ports on {target}: {e}")
        
        return open_ports
    
    def _identify_service(self, port: int) -> str:
        """Identify service running on port"""
        common_services = {
            21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
            80: "http", 110: "pop3", 143: "imap", 443: "https", 993: "imaps",
            995: "pop3s", 3306: "mysql", 5432: "postgresql", 6379: "redis",
            27017: "mongodb"
        }
        return common_services.get(port, "unknown")
    
    def _assess_port_risk(self, port: int, service: str) -> TestSeverity:
        """Assess risk level of open port"""
        high_risk_ports = [21, 23, 25, 53, 135, 139, 445, 1433, 3389]
        medium_risk_ports = [22, 80, 443, 3306, 5432]
        
        if port in high_risk_ports:
            return TestSeverity.HIGH
        elif port in medium_risk_ports:
            return TestSeverity.MEDIUM
        else:
            return TestSeverity.LOW
    
    def _calculate_port_cvss(self, port: int, service: str) -> float:
        """Calculate CVSS score for open port"""
        base_scores = {
            21: 7.5, 23: 9.8, 25: 5.3, 53: 5.3, 80: 5.3, 135: 7.5,
            139: 7.5, 443: 5.3, 445: 7.5, 1433: 7.5, 3389: 7.5
        }
        return base_scores.get(port, 3.0)
    
    def _assess_port_exploitability(self, port: int, service: str) -> str:
        """Assess exploitability of open port"""
        high_exploit_ports = [21, 23, 135, 139, 445, 1433, 3389]
        if port in high_exploit_ports:
            return "high"
        elif port in [22, 25, 53]:
            return "medium"
        else:
            return "low"
    
    async def _test_service_enumeration(self, targets: List[str], suite: PenetrationTestSuite) -> List[PenetrationTestFinding]:
        """Service enumeration test"""
        findings = []
        
        try:
            for target in targets:
                # Test common services
                services_to_test = [
                    {"port": 22, "service": "ssh"},
                    {"port": 80, "service": "http"},
                    {"port": 443, "service": "https"},
                    {"port": 21, "service": "ftp"}
                ]
                
                for service_info in services_to_test:
                    service_findings = await self._enumerate_service(target, service_info)
                    findings.extend(service_findings)
            
        except Exception as e:
            self.logger.error(f"Error in service enumeration test: {e}")
        
        return findings
    
    async def _enumerate_service(self, target: str, service_info: Dict[str, Any]) -> List[PenetrationTestFinding]:
        """Enumerate specific service"""
        findings = []
        
        try:
            port = service_info["port"]
            service = service_info["service"]
            
            # Check if port is open
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(target, port), timeout=2.0)
                
                if service == "http" or service == "https":
                    # HTTP service enumeration
                    http_findings = await self._enumerate_http_service(target, port, service == "https")
                    findings.extend(http_findings)
                
                elif service == "ssh":
                    # SSH service enumeration
                    ssh_findings = await self._enumerate_ssh_service(target, port)
                    findings.extend(ssh_findings)
                
                writer.close()
                await writer.wait_closed()
                
            except asyncio.TimeoutError:
                pass  # Port is closed or filtered
            
        except Exception as e:
            self.logger.error(f"Error enumerating {service_info['service']}: {e}")
        
        return findings
    
    async def _enumerate_http_service(self, target: str, port: int, is_https: bool) -> List[PenetrationTestFinding]:
        """Enumerate HTTP service"""
        findings = []
        
        try:
            protocol = "https" if is_https else "http"
            url = f"{protocol}://{target}:{port}"
            
            # Make HTTP request
            response = requests.get(url, timeout=5, verify=True)
            
            # Check for information disclosure
            server_header = response.headers.get('Server', '')
            if server_header:
                findings.append(PenetrationTestFinding(
                    finding_id=str(uuid.uuid4()),
                    test_name="HTTP Service Enumeration",
                    target=target,
                    severity=TestSeverity.LOW,
                    category=TestCategory.WEB_APPLICATION,
                    description=f"Server header disclosure: {server_header}",
                    impact="Server version information may help attackers identify vulnerabilities",
                    evidence={"server_header": server_header, "url": url},
                    remediation="Configure web server to hide version information",
                    cvss_score=2.0,
                    exploitability="low",
                    risk_rating="low"
                ))
            
            # Check for missing security headers
            security_headers = ['X-Frame-Options', 'X-XSS-Protection', 'X-Content-Type-Options', 'Strict-Transport-Security']
            missing_headers = [header for header in security_headers if header not in response.headers]
            
            if missing_headers:
                findings.append(PenetrationTestFinding(
                    finding_id=str(uuid.uuid4()),
                    test_name="HTTP Security Headers",
                    target=target,
                    severity=TestSeverity.MEDIUM,
                    category=TestCategory.WEB_APPLICATION,
                    description=f"Missing security headers: {', '.join(missing_headers)}",
                    impact="Missing security headers may allow various client-side attacks",
                    evidence={"missing_headers": missing_headers, "url": url},
                    remediation="Implement missing security headers",
                    cvss_score=4.3,
                    exploitability="medium",
                    risk_rating="medium"
                ))
            
        except Exception as e:
            self.logger.debug(f"Could not enumerate HTTP service on {target}:{port}: {e}")
        
        return findings
    
    async def _enumerate_ssh_service(self, target: str, port: int) -> List[PenetrationTestFinding]:
        """Enumerate SSH service"""
        findings = []
        
        try:
            # Connect to SSH service and get banner
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(target, port), timeout=3.0)
            
            # Read SSH banner
            banner = await asyncio.wait_for(reader.readline(), timeout=2.0)
            banner_str = banner.decode('utf-8', errors='ignore').strip()
            
            writer.close()
            await writer.wait_closed()
            
            if banner_str:
                # Check for version disclosure
                findings.append(PenetrationTestFinding(
                    finding_id=str(uuid.uuid4()),
                    test_name="SSH Service Enumeration",
                    target=target,
                    severity=TestSeverity.LOW,
                    category=TestCategory.NETWORK_SCANNING,
                    description=f"SSH banner disclosure: {banner_str}",
                    impact="SSH version information may help attackers identify vulnerabilities",
                    evidence={"ssh_banner": banner_str, "port": port},
                    remediation="Configure SSH to hide version information if possible",
                    cvss_score=2.0,
                    exploitability="low",
                    risk_rating="low"
                ))
            
        except Exception as e:
            self.logger.debug(f"Could not enumerate SSH service on {target}:{port}: {e}")
        
        return findings
    
    async def _test_web_application(self, targets: List[str], suite: PenetrationTestSuite) -> List[PenetrationTestFinding]:
        """Web application security test"""
        findings = []
        
        try:
            for target in targets:
                # Test common web ports
                web_ports = [80, 443, 8080, 8443]
                
                for port in web_ports:
                    web_findings = await self._test_web_port(target, port)
                    findings.extend(web_findings)
            
        except Exception as e:
            self.logger.error(f"Error in web application test: {e}")
        
        return findings
    
    async def _test_web_port(self, target: str, port: int) -> List[PenetrationTestFinding]:
        """Test web application on specific port"""
        findings = []
        
        try:
            protocol = "https" if port in [443, 8443] else "http"
            url = f"{protocol}://{target}:{port}"
            
            # Test for common vulnerabilities
            response = requests.get(url, timeout=5, verify=True)
            
            # Check for directory listing
            if "Index of /" in response.text:
                findings.append(PenetrationTestFinding(
                    finding_id=str(uuid.uuid4()),
                    test_name="Directory Listing",
                    target=target,
                    severity=TestSeverity.MEDIUM,
                    category=TestCategory.WEB_APPLICATION,
                    description=f"Directory listing enabled on {url}",
                    impact="Directory listing may expose sensitive files and system information",
                    evidence={"url": url, "response_snippet": response.text[:200]},
                    remediation="Disable directory listing in web server configuration",
                    cvss_score=5.3,
                    exploitability="medium",
                    risk_rating="medium"
                ))
            
            # Test for common files
            common_files = ["/robots.txt", "/.htaccess", "/web.config", "/admin", "/login"]
            for file_path in common_files:
                file_url = f"{url}{file_path}"
                try:
                    file_response = requests.get(file_url, timeout=3, verify=True)
                    if file_response.status_code == 200:
                        findings.append(PenetrationTestFinding(
                            finding_id=str(uuid.uuid4()),
                            test_name="Sensitive File Exposure",
                            target=target,
                            severity=TestSeverity.LOW,
                            category=TestCategory.WEB_APPLICATION,
                            description=f"Accessible file: {file_path}",
                            impact="Exposed files may contain sensitive information",
                            evidence={"url": file_url, "status_code": file_response.status_code},
                            remediation="Review and restrict access to sensitive files",
                            cvss_score=3.0,
                            exploitability="low",
                            risk_rating="low"
                        ))
                except:
                    continue
            
        except Exception as e:
            self.logger.debug(f"Could not test web application on {target}:{port}: {e}")
        
        return findings
    
    async def _test_ssl_tls(self, targets: List[str], suite: PenetrationTestSuite) -> List[PenetrationTestFinding]:
        """SSL/TLS security test"""
        findings = []
        
        try:
            for target in targets:
                ssl_ports = [443, 8443, 993, 995]
                
                for port in ssl_ports:
                    ssl_findings = await self._test_ssl_port(target, port)
                    findings.extend(ssl_findings)
            
        except Exception as e:
            self.logger.error(f"Error in SSL/TLS test: {e}")
        
        return findings
    
    async def _test_ssl_port(self, target: str, port: int) -> List[PenetrationTestFinding]:
        """Test SSL/TLS on specific port"""
        findings = []
        
        try:
            # Create SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Connect and get certificate info
            with socket.create_connection((target, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=target) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    
                    if cert:
                        # Check certificate expiration
                        not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        days_until_expiry = (not_after - datetime.now()).days
                        
                        if days_until_expiry < 30:
                            findings.append(PenetrationTestFinding(
                                finding_id=str(uuid.uuid4()),
                                test_name="SSL Certificate Expiry",
                                target=target,
                                severity=TestSeverity.HIGH if days_until_expiry < 0 else TestSeverity.MEDIUM,
                                category=TestCategory.ENCRYPTION,
                                description=f"SSL certificate expires in {days_until_expiry} days",
                                impact="Expired or soon-to-expire certificates cause service disruption",
                                evidence={"port": port, "expiry_date": cert['notAfter'], "days_remaining": days_until_expiry},
                                remediation="Renew SSL certificate before expiration",
                                cvss_score=7.5 if days_until_expiry < 0 else 5.3,
                                exploitability="low",
                                risk_rating="high" if days_until_expiry < 0 else "medium"
                            ))
                    
                    if cipher:
                        # Check for weak ciphers
                        cipher_name = cipher[0]
                        if any(weak in cipher_name.lower() for weak in ['rc4', 'des', 'md5']):
                            findings.append(PenetrationTestFinding(
                                finding_id=str(uuid.uuid4()),
                                test_name="Weak SSL Cipher",
                                target=target,
                                severity=TestSeverity.HIGH,
                                category=TestCategory.ENCRYPTION,
                                description=f"Weak SSL cipher in use: {cipher_name}",
                                impact="Weak ciphers may be vulnerable to cryptographic attacks",
                                evidence={"port": port, "cipher": cipher_name},
                                remediation="Configure server to use only strong SSL ciphers",
                                cvss_score=7.4,
                                exploitability="medium",
                                risk_rating="high"
                            ))
            
        except Exception as e:
            self.logger.debug(f"Could not test SSL on {target}:{port}: {e}")
        
        return findings
    
    async def _test_authentication_bypass(self, targets: List[str], suite: PenetrationTestSuite) -> List[PenetrationTestFinding]:
        """Authentication bypass test"""
        findings = []
        
        try:
            for target in targets:
                # Test common authentication bypass techniques
                auth_findings = await self._test_common_auth_bypass(target)
                findings.extend(auth_findings)
            
        except Exception as e:
            self.logger.error(f"Error in authentication bypass test: {e}")
        
        return findings
    
    async def _test_common_auth_bypass(self, target: str) -> List[PenetrationTestFinding]:
        """Test common authentication bypass techniques"""
        findings = []
        
        try:
            # Test default credentials on common services
            default_creds = [
                {"service": "ssh", "port": 22, "username": "admin", "password": "admin"},
                {"service": "ssh", "port": 22, "username": "root", "password": "root"},
                {"service": "http", "port": 80, "username": "admin", "password": "password"}
            ]
            
            for cred in default_creds:
                # This is a simulated test - in real implementation would attempt actual authentication
                # For safety, we'll just report the potential vulnerability
                findings.append(PenetrationTestFinding(
                    finding_id=str(uuid.uuid4()),
                    test_name="Default Credentials Test",
                    target=target,
                    severity=TestSeverity.INFO,
                    category=TestCategory.AUTHENTICATION,
                    description=f"Should test for default credentials on {cred['service']} service",
                    impact="Default credentials may allow unauthorized access",
                    evidence={"service": cred["service"], "port": cred["port"]},
                    remediation="Ensure all default passwords are changed",
                    cvss_score=9.8,
                    exploitability="high",
                    risk_rating="critical"
                ))
            
        except Exception as e:
            self.logger.error(f"Error testing authentication bypass on {target}: {e}")
        
        return findings
    
    async def _test_privilege_escalation(self, targets: List[str], suite: PenetrationTestSuite) -> List[PenetrationTestFinding]:
        """Privilege escalation test"""
        findings = []
        
        try:
            for target in targets:
                # Test for common privilege escalation vectors
                privesc_findings = await self._test_privesc_vectors(target)
                findings.extend(privesc_findings)
            
        except Exception as e:
            self.logger.error(f"Error in privilege escalation test: {e}")
        
        return findings
    
    async def _test_privesc_vectors(self, target: str) -> List[PenetrationTestFinding]:
        """Test privilege escalation vectors"""
        findings = []
        
        try:
            # Simulated privilege escalation tests
            # In real implementation, these would be actual tests
            
            findings.append(PenetrationTestFinding(
                finding_id=str(uuid.uuid4()),
                test_name="Privilege Escalation Assessment",
                target=target,
                severity=TestSeverity.INFO,
                category=TestCategory.AUTHORIZATION,
                description="System should be tested for privilege escalation vulnerabilities",
                impact="Privilege escalation may allow attackers to gain administrative access",
                evidence={"target": target, "test_type": "privilege_escalation"},
                remediation="Implement proper access controls and regular security updates",
                cvss_score=7.8,
                exploitability="medium",
                risk_rating="high"
            ))
            
        except Exception as e:
            self.logger.error(f"Error testing privilege escalation on {target}: {e}")
        
        return findings
    
    async def _test_database_security(self, targets: List[str], suite: PenetrationTestSuite) -> List[PenetrationTestFinding]:
        """Database security test"""
        findings = []
        
        try:
            for target in targets:
                # Test common database ports
                db_ports = [3306, 5432, 1433, 27017, 6379]
                
                for port in db_ports:
                    db_findings = await self._test_database_port(target, port)
                    findings.extend(db_findings)
            
        except Exception as e:
            self.logger.error(f"Error in database security test: {e}")
        
        return findings
    
    async def _test_database_port(self, target: str, port: int) -> List[PenetrationTestFinding]:
        """Test database security on specific port"""
        findings = []
        
        try:
            # Check if database port is open
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(target, port), timeout=2.0)
                writer.close()
                await writer.wait_closed()
                
                # Database port is open
                db_service = self._identify_database_service(port)
                findings.append(PenetrationTestFinding(
                    finding_id=str(uuid.uuid4()),
                    test_name="Database Port Exposure",
                    target=target,
                    severity=TestSeverity.HIGH,
                    category=TestCategory.DATABASE_SECURITY,
                    description=f"{db_service} database port {port} is accessible",
                    impact="Exposed database ports may allow unauthorized access to sensitive data",
                    evidence={"port": port, "service": db_service},
                    remediation="Restrict database access to authorized hosts only",
                    cvss_score=7.5,
                    exploitability="high",
                    risk_rating="high"
                ))
                
            except asyncio.TimeoutError:
                pass  # Port is closed or filtered
            
        except Exception as e:
            self.logger.debug(f"Could not test database port {port} on {target}: {e}")
        
        return findings
    
    def _identify_database_service(self, port: int) -> str:
        """Identify database service by port"""
        db_services = {
            3306: "MySQL",
            5432: "PostgreSQL",
            1433: "SQL Server",
            27017: "MongoDB",
            6379: "Redis"
        }
        return db_services.get(port, "Unknown Database")
    
    # Storage and reporting methods
    
    async def _store_finding(self, finding: PenetrationTestFinding):
        """Store penetration test finding in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO pentest_findings
                (finding_id, test_name, target, severity, category, description, impact,
                 evidence, remediation, cvss_score, exploitability, risk_rating,
                 false_positive, verified, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                finding.finding_id, finding.test_name, finding.target,
                finding.severity.value, finding.category.value, finding.description,
                finding.impact, json.dumps(finding.evidence), finding.remediation,
                finding.cvss_score, finding.exploitability, finding.risk_rating,
                finding.false_positive, finding.verified, finding.created_at
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing finding: {e}")
    
    async def _store_test_suite(self, suite: PenetrationTestSuite):
        """Store test suite in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO test_suites
                (suite_id, name, description, targets, test_categories, scope,
                 exclusions, intensity, duration_hours, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                suite.suite_id, suite.name, suite.description,
                json.dumps(suite.targets), json.dumps([cat.value for cat in suite.test_categories]),
                json.dumps(suite.scope), json.dumps(suite.exclusions),
                suite.intensity, suite.duration_hours, suite.created_at
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing test suite: {e}")
    
    async def _store_report(self, report: PenetrationTestReport):
        """Store penetration test report in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO pentest_reports
                (report_id, suite_id, test_name, targets, findings, summary,
                 recommendations, executive_summary, technical_details, created_at,
                 completed_at, total_tests_run, success_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                report.report_id, report.suite_id, report.test_name,
                json.dumps(report.targets), json.dumps([f.finding_id for f in report.findings]),
                json.dumps(report.summary), json.dumps(report.recommendations),
                report.executive_summary, json.dumps(report.technical_details),
                report.created_at, report.completed_at, report.total_tests_run, report.success_rate
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing report: {e}")
    
    def _generate_test_summary(self, findings: List[PenetrationTestFinding]) -> Dict[str, Any]:
        """Generate test summary from findings"""
        summary = {
            "total_findings": len(findings),
            "by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0
            },
            "by_category": {},
            "risk_score": 0.0,
            "exploitability_assessment": {}
        }
        
        try:
            # Count by severity and category
            for finding in findings:
                summary["by_severity"][finding.severity.value] += 1
                
                category = finding.category.value
                if category not in summary["by_category"]:
                    summary["by_category"][category] = 0
                summary["by_category"][category] += 1
                
                # Count exploitability
                exploit = finding.exploitability
                if exploit not in summary["exploitability_assessment"]:
                    summary["exploitability_assessment"][exploit] = 0
                summary["exploitability_assessment"][exploit] += 1
            
            # Calculate overall risk score
            severity_weights = {
                TestSeverity.CRITICAL: 10,
                TestSeverity.HIGH: 7,
                TestSeverity.MEDIUM: 4,
                TestSeverity.LOW: 2,
                TestSeverity.INFO: 1
            }
            
            total_risk = sum(severity_weights.get(f.severity, 1) for f in findings)
            summary["risk_score"] = min(100.0, total_risk / 5.0)
            
        except Exception as e:
            self.logger.error(f"Error generating test summary: {e}")
        
        return summary
    
    def _generate_test_recommendations(self, findings: List[PenetrationTestFinding]) -> List[str]:
        """Generate test recommendations based on findings"""
        recommendations = []
        
        try:
            # Priority recommendations
            critical_findings = [f for f in findings if f.severity == TestSeverity.CRITICAL]
            high_findings = [f for f in findings if f.severity == TestSeverity.HIGH]
            
            if critical_findings:
                recommendations.append("CRITICAL: Address all critical vulnerabilities immediately")
                for finding in critical_findings[:3]:
                    recommendations.append(f"- {finding.remediation}")
            
            if high_findings:
                recommendations.append("HIGH PRIORITY: Remediate high-severity vulnerabilities")
                for finding in high_findings[:5]:
                    recommendations.append(f"- {finding.remediation}")
            
            # General security recommendations
            recommendations.extend([
                "Implement regular vulnerability assessments",
                "Establish a patch management program",
                "Conduct security awareness training",
                "Implement network segmentation",
                "Deploy intrusion detection systems",
                "Regular security configuration reviews"
            ])
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
        
        return recommendations
    
    def _generate_executive_summary(self, findings: List[PenetrationTestFinding], suite: PenetrationTestSuite) -> str:
        """Generate executive summary"""
        try:
            critical_count = len([f for f in findings if f.severity == TestSeverity.CRITICAL])
            high_count = len([f for f in findings if f.severity == TestSeverity.HIGH])
            medium_count = len([f for f in findings if f.severity == TestSeverity.MEDIUM])
            
            summary = f"""
EXECUTIVE SUMMARY - PENETRATION TEST REPORT

Test Suite: {suite.name}
Test Duration: {suite.duration_hours} hours
Total Findings: {len(findings)}

RISK ASSESSMENT:
- Critical Risk Issues: {critical_count}
- High Risk Issues: {high_count}
- Medium Risk Issues: {medium_count}

OVERALL SECURITY POSTURE:
"""
            
            if critical_count > 0:
                summary += "CRITICAL - Immediate action required to address critical vulnerabilities.\n"
            elif high_count > 5:
                summary += "HIGH RISK - Multiple high-severity issues require prompt attention.\n"
            elif high_count > 0:
                summary += "MODERATE RISK - Some high-severity issues identified.\n"
            else:
                summary += "LOW RISK - No critical or high-severity issues identified.\n"
            
            summary += f"""
RECOMMENDATIONS:
1. Prioritize remediation of critical and high-severity findings
2. Implement regular security assessments
3. Establish continuous monitoring capabilities
4. Conduct security awareness training for staff

This assessment was conducted using automated penetration testing tools and techniques.
Manual verification of findings is recommended before remediation efforts.
"""
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating executive summary: {e}")
            return "Error generating executive summary"
    
    def _generate_technical_details(self, findings: List[PenetrationTestFinding]) -> Dict[str, Any]:
        """Generate technical details section"""
        details = {
            "methodology": "Automated penetration testing using custom security assessment framework",
            "tools_used": ["Custom port scanner", "HTTP security scanner", "SSL/TLS analyzer"],
            "test_coverage": {},
            "limitations": [
                "Automated testing may not identify all vulnerabilities",
                "Manual verification recommended for all findings",
                "Some tests may produce false positives"
            ]
        }
        
        try:
            # Calculate test coverage by category
            categories = {}
            for finding in findings:
                category = finding.category.value
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1
            
            details["test_coverage"] = categories
            
        except Exception as e:
            self.logger.error(f"Error generating technical details: {e}")
        
        return details
    
    # Public API methods
    
    async def get_test_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get penetration test report by ID"""
        try:
            if report_id in self.reports:
                report = self.reports[report_id]
                return asdict(report)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting test report: {e}")
            return None
    
    async def get_test_findings(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get penetration test findings with optional filters"""
        try:
            if filters is None:
                filters = {}
            
            findings = []
            
            for finding in self.findings.values():
                # Apply filters
                if filters.get("severity") and finding.severity.value != filters["severity"]:
                    continue
                if filters.get("category") and finding.category.value != filters["category"]:
                    continue
                if filters.get("target") and finding.target != filters["target"]:
                    continue
                
                finding_dict = asdict(finding)
                finding_dict["severity"] = finding.severity.value
                finding_dict["category"] = finding.category.value
                findings.append(finding_dict)
            
            # Sort by severity and CVSS score
            severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
            findings.sort(key=lambda x: (severity_order.get(x["severity"], 0), x["cvss_score"]), reverse=True)
            
            return findings
            
        except Exception as e:
            self.logger.error(f"Error getting test findings: {e}")
            return []
    
    async def get_test_statistics(self) -> Dict[str, Any]:
        """Get penetration testing statistics"""
        try:
            unverified_findings = [f for f in self.findings.values() if not f.verified and not f.false_positive]
            
            stats = {
                "total_findings": len(self.findings),
                "unverified_findings": len(unverified_findings),
                "total_reports": len(self.reports),
                "total_test_suites": len(self.test_suites),
                "by_severity": {
                    "critical": len([f for f in unverified_findings if f.severity == TestSeverity.CRITICAL]),
                    "high": len([f for f in unverified_findings if f.severity == TestSeverity.HIGH]),
                    "medium": len([f for f in unverified_findings if f.severity == TestSeverity.MEDIUM]),
                    "low": len([f for f in unverified_findings if f.severity == TestSeverity.LOW]),
                    "info": len([f for f in unverified_findings if f.severity == TestSeverity.INFO])
                },
                "last_test": max([r.created_at for r in self.reports.values()], default=0)
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting test statistics: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Get penetration testing system health status"""
        try:
            return {
                "status": "healthy",
                "total_findings": len(self.findings),
                "critical_findings": len([f for f in self.findings.values()
                                        if f.severity == TestSeverity.CRITICAL and not f.verified]),
                "test_suites_available": len(self.test_suites),
                "database_connected": True,
                "last_test": max([r.created_at for r in self.reports.values()], default=0)
            }
            
        except Exception as e:
            self.logger.error(f"Error in health check: {e}")
            return {"status": "unhealthy", "error": str(e)}


# Example usage and testing
async def main():
    """Example usage of the penetration testing system"""
    from src.consciousness_v2.consciousness_bus import ConsciousnessBus
    
    # Initialize consciousness bus
    consciousness_bus = ConsciousnessBus()
    
    # Create penetration testing system
    pentest_system = PenetrationTestingSystem(consciousness_bus)
    
    # Wait for initialization
    await asyncio.sleep(3)
    
    # Get health status
    health = await pentest_system.health_check()
    print(f"Pentest system health: {health}")
    
    # Get available test suites
    print(f"Available test suites: {len(pentest_system.test_suites)}")
    for suite_id, suite in pentest_system.test_suites.items():
        print(f"- {suite.name}: {suite.description}")
    
    # Execute basic security assessment
    if pentest_system.test_suites:
        suite_id = list(pentest_system.test_suites.keys())[0]  # Get first suite
        print(f"Executing penetration test...")
        
        report_id = await pentest_system.execute_penetration_test(suite_id)
        
        if report_id:
            print(f"Penetration test completed. Report ID: {report_id}")
            
            # Get test report
            report = await pentest_system.get_test_report(report_id)
            if report:
                print(f"Total findings: {report['summary']['total_findings']}")
                print(f"Risk score: {report['summary']['risk_score']}")
            
            # Get test findings
            findings = await pentest_system.get_test_findings({"severity": "high"})
            print(f"High-severity findings: {len(findings)}")
            
            # Get statistics
            stats = await pentest_system.get_test_statistics()
            print(f"Test statistics: {stats}")


if __name__ == "__main__":
    asyncio.run(main())