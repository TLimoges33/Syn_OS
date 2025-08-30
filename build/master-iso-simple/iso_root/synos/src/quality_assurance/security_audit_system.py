#!/usr/bin/env python3
"""
Comprehensive Security Audit System for Syn_OS
Automated security assessment and vulnerability analysis of the entire system
"""

import asyncio
import logging
import time
import json
import hashlib
import os
import subprocess
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import uuid
from datetime import datetime, timedelta
import stat
import pwd
import grp

from src.consciousness_v2.consciousness_bus import ConsciousnessBus


class AuditSeverity(Enum):
    """Security audit finding severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditCategory(Enum):
    """Security audit categories"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ENCRYPTION = "encryption"
    NETWORK_SECURITY = "network_security"
    FILE_PERMISSIONS = "file_permissions"
    CODE_SECURITY = "code_security"
    CONFIGURATION = "configuration"
    LOGGING = "logging"
    INPUT_VALIDATION = "input_validation"
    SESSION_MANAGEMENT = "session_management"
    ERROR_HANDLING = "error_handling"
    DEPENDENCY_SECURITY = "dependency_security"


class AuditStatus(Enum):
    """Audit execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SecurityFinding:
    """Individual security audit finding"""
    finding_id: str
    title: str
    description: str
    severity: AuditSeverity
    category: AuditCategory
    affected_component: str
    file_path: Optional[str]
    line_number: Optional[int]
    evidence: Dict[str, Any]
    recommendation: str
    cwe_id: Optional[str]  # Common Weakness Enumeration
    owasp_category: Optional[str]
    remediation_effort: str  # low, medium, high
    false_positive: bool = False
    resolved: bool = False
    created_at: float = 0.0
    
    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()


@dataclass
class AuditReport:
    """Security audit report"""
    report_id: str
    audit_type: str
    scope: List[str]
    findings: List[SecurityFinding]
    summary: Dict[str, Any]
    recommendations: List[str]
    compliance_status: Dict[str, Any]
    created_at: float
    completed_at: Optional[float] = None
    total_files_scanned: int = 0
    total_lines_scanned: int = 0


class SecurityAuditSystem:
    """
    Comprehensive security audit system for Syn_OS
    Performs automated security assessments across all system components
    """
    
    def __init__(self, consciousness_bus: ConsciousnessBus):
        """Initialize security audit system"""
        self.consciousness_bus = consciousness_bus
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.system_directory = "/var/lib/synos/security_audit"
        self.database_file = f"{self.system_directory}/security_audit.db"
        
        # Audit configuration
        self.scan_directories = [
            "src/",
            "config/",
            "scripts/",
            "docs/"
        ]
        
        # Security patterns and rules
        self.security_patterns = self._initialize_security_patterns()
        
        # Compliance frameworks
        self.compliance_frameworks = {
            "OWASP_TOP_10": self._get_owasp_top_10_rules(),
            "CIS_CONTROLS": self._get_cis_controls(),
            "NIST_CSF": self._get_nist_csf_controls()
        }
        
        # Data stores
        self.findings: Dict[str, SecurityFinding] = {}
        self.reports: Dict[str, AuditReport] = {}
        
        # Initialize system
        asyncio.create_task(self._initialize_audit_system())
    
    async def _initialize_audit_system(self):
        """Initialize the security audit system"""
        try:
            self.logger.info("Initializing security audit system...")
            
            # Create system directory
            os.makedirs(self.system_directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Load existing data
            await self._load_audit_data()
            
            self.logger.info("Security audit system initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing security audit system: {e}")
    
    async def _initialize_database(self):
        """Initialize security audit database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Security findings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_findings (
                    finding_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    severity TEXT NOT NULL,
                    category TEXT NOT NULL,
                    affected_component TEXT NOT NULL,
                    file_path TEXT,
                    line_number INTEGER,
                    evidence TEXT,
                    recommendation TEXT,
                    cwe_id TEXT,
                    owasp_category TEXT,
                    remediation_effort TEXT,
                    false_positive BOOLEAN NOT NULL DEFAULT 0,
                    resolved BOOLEAN NOT NULL DEFAULT 0,
                    created_at REAL NOT NULL
                )
            ''')
            
            # Audit reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_reports (
                    report_id TEXT PRIMARY KEY,
                    audit_type TEXT NOT NULL,
                    scope TEXT,
                    findings TEXT,
                    summary TEXT,
                    recommendations TEXT,
                    compliance_status TEXT,
                    created_at REAL NOT NULL,
                    completed_at REAL,
                    total_files_scanned INTEGER NOT NULL DEFAULT 0,
                    total_lines_scanned INTEGER NOT NULL DEFAULT 0
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_findings_severity ON security_findings (severity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_findings_category ON security_findings (category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_findings_component ON security_findings (affected_component)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_type ON audit_reports (audit_type)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing audit database: {e}")
            raise
    
    async def _load_audit_data(self):
        """Load existing audit data from database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Load unresolved findings
            cursor.execute('SELECT * FROM security_findings WHERE resolved = 0')
            for row in cursor.fetchall():
                finding = SecurityFinding(
                    finding_id=row[0],
                    title=row[1],
                    description=row[2],
                    severity=AuditSeverity(row[3]),
                    category=AuditCategory(row[4]),
                    affected_component=row[5],
                    file_path=row[6],
                    line_number=row[7],
                    evidence=json.loads(row[8]) if row[8] else {},
                    recommendation=row[9],
                    cwe_id=row[10],
                    owasp_category=row[11],
                    remediation_effort=row[12],
                    false_positive=bool(row[13]),
                    resolved=bool(row[14]),
                    created_at=row[15]
                )
                self.findings[finding.finding_id] = finding
            
            # Load recent reports
            cursor.execute('SELECT * FROM audit_reports ORDER BY created_at DESC LIMIT 10')
            for row in cursor.fetchall():
                report = AuditReport(
                    report_id=row[0],
                    audit_type=row[1],
                    scope=json.loads(row[2]) if row[2] else [],
                    findings=[],  # Will be loaded separately if needed
                    summary=json.loads(row[4]) if row[4] else {},
                    recommendations=json.loads(row[5]) if row[5] else [],
                    compliance_status=json.loads(row[6]) if row[6] else {},
                    created_at=row[7],
                    completed_at=row[8],
                    total_files_scanned=row[9],
                    total_lines_scanned=row[10]
                )
                self.reports[report.report_id] = report
            
            conn.close()
            
            self.logger.info(f"Loaded {len(self.findings)} unresolved findings, {len(self.reports)} recent reports")
            
        except Exception as e:
            self.logger.error(f"Error loading audit data: {e}")
    
    def _initialize_security_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize security vulnerability patterns"""
        return {
            "sql_injection": [
                {
                    "pattern": r"execute\s*\(\s*[\"'].*%.*[\"']\s*%",
                    "description": "Potential SQL injection via string formatting",
                    "severity": AuditSeverity.HIGH,
                    "cwe": "CWE-89"
                },
                {
                    "pattern": r"cursor\.execute\s*\(\s*f[\"'].*\{.*\}",
                    "description": "Potential SQL injection via f-string",
                    "severity": AuditSeverity.HIGH,
                    "cwe": "CWE-89"
                }
            ],
            "command_injection": [
                {
                    "pattern": r"subprocess\.(call|run|Popen)\s*\(\s*[\"'].*\+.*[\"']",
                    "description": "Potential command injection via string concatenation",
                    "severity": AuditSeverity.CRITICAL,
                    "cwe": "CWE-78"
                },
                {
                    "pattern": r"os\.system\s*\(\s*[\"'].*\+.*[\"']",
                    "description": "Potential command injection in os.system",
                    "severity": AuditSeverity.CRITICAL,
                    "cwe": "CWE-78"
                }
            ],
            "hardcoded_secrets": [
                {
                    "pattern": r"password\s*=\s*[\"'][^\"']{8,}[\"']",
                    "description": "Hardcoded password detected",
                    "severity": AuditSeverity.HIGH,
                    "cwe": "CWE-798"
                },
                {
                    "pattern": r"api_key\s*=\s*[\"'][A-Za-z0-9]{20,}[\"']",
                    "description": "Hardcoded API key detected",
                    "severity": AuditSeverity.HIGH,
                    "cwe": "CWE-798"
                },
                {
                    "pattern": r"secret\s*=\s*[\"'][^\"']{16,}[\"']",
                    "description": "Hardcoded secret detected",
                    "severity": AuditSeverity.HIGH,
                    "cwe": "CWE-798"
                }
            ],
            "weak_crypto": [
                {
                    "pattern": r"hashlib\.md5\s*\(",
                    "description": "Weak cryptographic hash MD5 used",
                    "severity": AuditSeverity.MEDIUM,
                    "cwe": "CWE-327"
                },
                {
                    "pattern": r"hashlib\.sha1\s*\(",
                    "description": "Weak cryptographic hash SHA1 used",
                    "severity": AuditSeverity.MEDIUM,
                    "cwe": "CWE-327"
                }
            ],
            "insecure_random": [
                {
                    "pattern": r"random\.random\s*\(",
                    "description": "Insecure random number generation",
                    "severity": AuditSeverity.MEDIUM,
                    "cwe": "CWE-338"
                }
            ],
            "path_traversal": [
                {
                    "pattern": r"open\s*\(\s*.*\+.*[\"']\.\.\/",
                    "description": "Potential path traversal vulnerability",
                    "severity": AuditSeverity.HIGH,
                    "cwe": "CWE-22"
                }
            ],
            "unsafe_deserialization": [
                {
                    "pattern": r"pickle\.loads?\s*\(",
                    "description": "Unsafe deserialization with pickle",
                    "severity": AuditSeverity.HIGH,
                    "cwe": "CWE-502"
                }
            ]
        }
    
    def _get_owasp_top_10_rules(self) -> List[Dict[str, Any]]:
        """Get OWASP Top 10 security rules"""
        return [
            {
                "id": "A01_2021",
                "name": "Broken Access Control",
                "description": "Access control enforces policy such that users cannot act outside of their intended permissions"
            },
            {
                "id": "A02_2021", 
                "name": "Cryptographic Failures",
                "description": "Failures related to cryptography which often leads to sensitive data exposure"
            },
            {
                "id": "A03_2021",
                "name": "Injection",
                "description": "Application is vulnerable to injection attacks"
            },
            {
                "id": "A04_2021",
                "name": "Insecure Design",
                "description": "Risks related to design flaws and architectural weaknesses"
            },
            {
                "id": "A05_2021",
                "name": "Security Misconfiguration", 
                "description": "Security misconfiguration is commonly a result of insecure default configurations"
            },
            {
                "id": "A06_2021",
                "name": "Vulnerable and Outdated Components",
                "description": "Components with known vulnerabilities"
            },
            {
                "id": "A07_2021",
                "name": "Identification and Authentication Failures",
                "description": "Confirmation of the user's identity, authentication, and session management"
            },
            {
                "id": "A08_2021",
                "name": "Software and Data Integrity Failures",
                "description": "Software and data integrity failures relate to code and infrastructure"
            },
            {
                "id": "A09_2021",
                "name": "Security Logging and Monitoring Failures",
                "description": "Logging and monitoring coupled with missing or ineffective integration"
            },
            {
                "id": "A10_2021",
                "name": "Server-Side Request Forgery",
                "description": "SSRF flaws occur whenever a web application is fetching a remote resource"
            }
        ]
    
    def _get_cis_controls(self) -> List[Dict[str, Any]]:
        """Get CIS Critical Security Controls"""
        return [
            {"id": "CIS_1", "name": "Inventory and Control of Enterprise Assets"},
            {"id": "CIS_2", "name": "Inventory and Control of Software Assets"},
            {"id": "CIS_3", "name": "Data Protection"},
            {"id": "CIS_4", "name": "Secure Configuration of Enterprise Assets and Software"},
            {"id": "CIS_5", "name": "Account Management"},
            {"id": "CIS_6", "name": "Access Control Management"}
        ]
    
    def _get_nist_csf_controls(self) -> List[Dict[str, Any]]:
        """Get NIST Cybersecurity Framework controls"""
        return [
            {"id": "NIST_ID", "name": "Identify"},
            {"id": "NIST_PR", "name": "Protect"},
            {"id": "NIST_DE", "name": "Detect"},
            {"id": "NIST_RS", "name": "Respond"},
            {"id": "NIST_RC", "name": "Recover"}
        ]
    
    async def conduct_comprehensive_audit(self) -> str:
        """Conduct comprehensive security audit of entire system"""
        try:
            self.logger.info("Starting comprehensive security audit...")
            
            report_id = str(uuid.uuid4())
            current_time = time.time()
            
            # Initialize report
            report = AuditReport(
                report_id=report_id,
                audit_type="comprehensive",
                scope=self.scan_directories.copy(),
                findings=[],
                summary={},
                recommendations=[],
                compliance_status={},
                created_at=current_time
            )
            
            # Perform different types of audits
            findings = []
            
            # 1. Static code analysis
            self.logger.info("Performing static code analysis...")
            code_findings = await self._perform_static_code_analysis()
            findings.extend(code_findings)
            
            # 2. Configuration audit
            self.logger.info("Performing configuration audit...")
            config_findings = await self._perform_configuration_audit()
            findings.extend(config_findings)
            
            # 3. File permissions audit
            self.logger.info("Performing file permissions audit...")
            perm_findings = await self._perform_file_permissions_audit()
            findings.extend(perm_findings)
            
            # 4. Dependency security audit
            self.logger.info("Performing dependency security audit...")
            dep_findings = await self._perform_dependency_audit()
            findings.extend(dep_findings)
            
            # 5. Network security audit
            self.logger.info("Performing network security audit...")
            net_findings = await self._perform_network_security_audit()
            findings.extend(net_findings)
            
            # Store findings
            for finding in findings:
                await self._store_finding(finding)
                self.findings[finding.finding_id] = finding
            
            # Generate summary and recommendations
            report.findings = findings
            report.summary = self._generate_audit_summary(findings)
            report.recommendations = self._generate_recommendations(findings)
            report.compliance_status = self._assess_compliance(findings)
            report.completed_at = time.time()
            
            # Store report
            await self._store_report(report)
            self.reports[report_id] = report
            
            self.logger.info(f"Comprehensive security audit completed. Found {len(findings)} issues.")
            return report_id
            
        except Exception as e:
            self.logger.error(f"Error conducting comprehensive audit: {e}")
            return ""
    
    async def _perform_static_code_analysis(self) -> List[SecurityFinding]:
        """Perform static code analysis for security vulnerabilities"""
        findings = []
        
        try:
            for directory in self.scan_directories:
                if not os.path.exists(directory):
                    continue
                
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c')):
                            file_path = os.path.join(root, file)
                            file_findings = await self._scan_file_for_vulnerabilities(file_path)
                            findings.extend(file_findings)
            
        except Exception as e:
            self.logger.error(f"Error in static code analysis: {e}")
        
        return findings
    
    async def _scan_file_for_vulnerabilities(self, file_path: str) -> List[SecurityFinding]:
        """Scan individual file for security vulnerabilities"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # Check against all security patterns
                for category, patterns in self.security_patterns.items():
                    for pattern_info in patterns:
                        if re.search(pattern_info["pattern"], line, re.IGNORECASE):
                            finding = SecurityFinding(
                                finding_id=str(uuid.uuid4()),
                                title=pattern_info["description"],
                                description=f"Security vulnerability detected in {file_path}:{line_num}",
                                severity=pattern_info["severity"],
                                category=self._map_pattern_to_category(category),
                                affected_component=file_path,
                                file_path=file_path,
                                line_number=line_num,
                                evidence={
                                    "line_content": line.strip(),
                                    "pattern_matched": pattern_info["pattern"],
                                    "vulnerability_type": category
                                },
                                recommendation=self._get_remediation_advice(category),
                                cwe_id=pattern_info.get("cwe"),
                                owasp_category=self._map_to_owasp_category(category),
                                remediation_effort="medium"
                            )
                            findings.append(finding)
            
        except Exception as e:
            self.logger.error(f"Error scanning file {file_path}: {e}")
        
        return findings
    
    def _map_pattern_to_category(self, pattern_type: str) -> AuditCategory:
        """Map vulnerability pattern to audit category"""
        mapping = {
            "sql_injection": AuditCategory.INPUT_VALIDATION,
            "command_injection": AuditCategory.INPUT_VALIDATION,
            "hardcoded_secrets": AuditCategory.AUTHENTICATION,
            "weak_crypto": AuditCategory.ENCRYPTION,
            "insecure_random": AuditCategory.ENCRYPTION,
            "path_traversal": AuditCategory.AUTHORIZATION,
            "unsafe_deserialization": AuditCategory.INPUT_VALIDATION
        }
        return mapping.get(pattern_type, AuditCategory.CODE_SECURITY)
    
    def _map_to_owasp_category(self, pattern_type: str) -> str:
        """Map vulnerability pattern to OWASP Top 10 category"""
        mapping = {
            "sql_injection": "A03_2021",
            "command_injection": "A03_2021", 
            "hardcoded_secrets": "A02_2021",
            "weak_crypto": "A02_2021",
            "insecure_random": "A02_2021",
            "path_traversal": "A01_2021",
            "unsafe_deserialization": "A08_2021"
        }
        return mapping.get(pattern_type, "A04_2021")
    
    def _get_remediation_advice(self, vulnerability_type: str) -> str:
        """Get remediation advice for vulnerability type"""
        advice = {
            "sql_injection": "Use parameterized queries or prepared statements instead of string concatenation",
            "command_injection": "Use subprocess with shell=False and validate all inputs",
            "hardcoded_secrets": "Store secrets in environment variables or secure configuration files",
            "weak_crypto": "Use strong cryptographic algorithms like SHA-256 or SHA-3",
            "insecure_random": "Use secrets.SystemRandom() for cryptographically secure random numbers",
            "path_traversal": "Validate and sanitize file paths, use os.path.join() safely",
            "unsafe_deserialization": "Use safe serialization formats like JSON instead of pickle"
        }
        return advice.get(vulnerability_type, "Review and remediate the identified security issue")
    
    async def _perform_configuration_audit(self) -> List[SecurityFinding]:
        """Perform configuration security audit"""
        findings = []
        
        try:
            # Check for insecure configuration files
            config_files = [
                "config/database.conf",
                "config/api.conf", 
                "config/security.conf",
                ".env",
                "docker-compose.yml"
            ]
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    config_findings = await self._audit_configuration_file(config_file)
                    findings.extend(config_findings)
            
            # Check system configuration
            system_findings = await self._audit_system_configuration()
            findings.extend(system_findings)
            
        except Exception as e:
            self.logger.error(f"Error in configuration audit: {e}")
        
        return findings
    
    async def _audit_configuration_file(self, file_path: str) -> List[SecurityFinding]:
        """Audit individual configuration file"""
        findings = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for common misconfigurations
            if "debug=true" in content.lower():
                findings.append(SecurityFinding(
                    finding_id=str(uuid.uuid4()),
                    title="Debug Mode Enabled",
                    description=f"Debug mode is enabled in {file_path}",
                    severity=AuditSeverity.MEDIUM,
                    category=AuditCategory.CONFIGURATION,
                    affected_component=file_path,
                    file_path=file_path,
                    line_number=None,
                    evidence={"config_setting": "debug=true"},
                    recommendation="Disable debug mode in production environments",
                    remediation_effort="low"
                ))
            
            if "password=" in content.lower() and len(content.split("password=")[1].split()[0]) < 8:
                findings.append(SecurityFinding(
                    finding_id=str(uuid.uuid4()),
                    title="Weak Password in Configuration",
                    description=f"Weak password detected in {file_path}",
                    severity=AuditSeverity.HIGH,
                    category=AuditCategory.AUTHENTICATION,
                    affected_component=file_path,
                    file_path=file_path,
                    line_number=None,
                    evidence={"issue": "weak_password"},
                    recommendation="Use strong passwords with minimum 12 characters",
                    cwe_id="CWE-521",
                    remediation_effort="low"
                ))
            
        except Exception as e:
            self.logger.error(f"Error auditing config file {file_path}: {e}")
        
        return findings
    
    async def _audit_system_configuration(self) -> List[SecurityFinding]:
        """Audit system-level configuration"""
        findings = []
        
        try:
            # Check SSH configuration
            if os.path.exists("/etc/ssh/sshd_config"):
                ssh_findings = await self._audit_ssh_config()
                findings.extend(ssh_findings)
            
            # Check firewall status
            firewall_findings = await self._audit_firewall_config()
            findings.extend(firewall_findings)
            
        except Exception as e:
            self.logger.error(f"Error in system configuration audit: {e}")
        
        return findings
    
    async def _audit_ssh_config(self) -> List[SecurityFinding]:
        """Audit SSH configuration"""
        findings = []
        
        try:
            with open("/etc/ssh/sshd_config", 'r') as f:
                ssh_config = f.read()
            
            if "PermitRootLogin yes" in ssh_config:
                findings.append(SecurityFinding(
                    finding_id=str(uuid.uuid4()),
                    title="Root Login Permitted via SSH",
                    description="SSH is configured to allow root login",
                    severity=AuditSeverity.HIGH,
                    category=AuditCategory.AUTHENTICATION,
                    affected_component="/etc/ssh/sshd_config",
                    file_path="/etc/ssh/sshd_config",
                    line_number=None,
                    evidence={"setting": "PermitRootLogin yes"},
                    recommendation="Set PermitRootLogin to 'no' or 'prohibit-password'",
                    cwe_id="CWE-250",
                    remediation_effort="low"
                ))
            
        except Exception as e:
            self.logger.error(f"Error auditing SSH config: {e}")
        
        return findings
    
    async def _audit_firewall_config(self) -> List[SecurityFinding]:
        """Audit firewall configuration"""
        findings = []
        
        try:
            # Check if firewall is active - SECURITY FIX: Use secure subprocess
            result = subprocess.run(['ufw', 'status'], capture_output=True, text=True, shell=False)
            if "Status: inactive" in result.stdout:
                findings.append(SecurityFinding(
                    finding_id=str(uuid.uuid4()),
                    title="Firewall Disabled",
                    description="System firewall is not active",
                    severity=AuditSeverity.HIGH,
                    category=AuditCategory.NETWORK_SECURITY,
                    affected_component="system_firewall",
                    file_path=None,
                    line_number=None,
                    evidence={"firewall_status": "inactive"},
                    recommendation="Enable and configure firewall with appropriate rules",
                    remediation_effort="medium"
                ))
            
        except Exception as e:
            self.logger.debug(f"Could not check firewall status: {e}")
        
        return findings
    
    async def _perform_file_permissions_audit(self) -> List[SecurityFinding]:
        """Perform file permissions security audit"""
        findings = []
        
        try:
            # Check critical system files
            critical_files = [
                "/etc/passwd",
                "/etc/shadow", 
                "/etc/sudoers",
                "config/",
                "src/",
                "scripts/"
            ]
            
            for file_path in critical_files:
                if os.path.exists(file_path):
                    perm_findings = await self._check_file_permissions(file_path)
                    findings.extend(perm_findings)
            
        except Exception as e:
            self.logger.error(f"Error in file permissions audit: {e}")
        
        return findings
    
    async def _check_file_permissions(self, file_path: str) -> List[SecurityFinding]:
        """Check file permissions for security issues"""
        findings = []
        
        try:
            file_stat = os.stat(file_path)
            file_mode = stat.filemode(file_stat.st_mode)
            
            # Check for world-writable files
            if file_stat.st_mode & stat.S_IWOTH:
                findings.append(SecurityFinding(
                    finding_id=str(uuid.uuid4()),
                    title="World-Writable File",
                    description=f"File {file_path} is world-writable",
                    severity=AuditSeverity.HIGH,
                    category=AuditCategory.FILE_PERMISSIONS,
                    affected_component=file_path,
                    file_path=file_path,
                    line_number=None,
                    evidence={"permissions": file_mode},
                    recommendation="Remove world-write permissions",
                    cwe_id="CWE-732",
                    remediation_effort="low"
                ))
            
            # Check for executable files with weak permissions
            if (file_stat.st_mode & stat.S_IXUSR and
                file_stat.st_mode & stat.S_IWGRP):
                findings.append(SecurityFinding(
                    finding_id=str(uuid.uuid4()),
                    title="Executable File with Group Write",
                    description=f"Executable file {file_path} has group write permissions",
                    severity=AuditSeverity.MEDIUM,
                    category=AuditCategory.FILE_PERMISSIONS,
                    affected_component=file_path,
                    file_path=file_path,
                    line_number=None,
                    evidence={"permissions": file_mode},
                    recommendation="Remove group write permissions from executable files",
                    cwe_id="CWE-732",
                    owasp_category="A05_2021",
                    remediation_effort="low"
                ))
            
        except Exception as e:
            self.logger.error(f"Error checking file permissions for {file_path}: {e}")
        
        return findings
    
    async def _perform_dependency_audit(self) -> List[SecurityFinding]:
        """Perform dependency security audit"""
        findings = []
        
        try:
            # Check Python dependencies
            if os.path.exists("requirements.txt"):
                dep_findings = await self._audit_python_dependencies()
                findings.extend(dep_findings)
            
            # Check Node.js dependencies
            if os.path.exists("package.json"):
                node_findings = await self._audit_node_dependencies()
                findings.extend(node_findings)
            
        except Exception as e:
            self.logger.error(f"Error in dependency audit: {e}")
        
        return findings
    
    async def _audit_python_dependencies(self) -> List[SecurityFinding]:
        """Audit Python dependencies for known vulnerabilities"""
        findings = []
        
        try:
            # Read requirements.txt
            with open("requirements.txt", 'r') as f:
                requirements = f.readlines()
            
            # Check for known vulnerable packages (simplified example)
            vulnerable_packages = {
                "django": {"version": "3.0", "cve": "CVE-2021-35042"},
                "flask": {"version": "1.0", "cve": "CVE-2019-1010083"},
                "requests": {"version": "2.19", "cve": "CVE-2018-18074"}
            }
            
            for req in requirements:
                req = req.strip()
                if req and not req.startswith('#'):
                    package_name = req.split('==')[0].split('>=')[0].split('<=')[0].lower()
                    
                    if package_name in vulnerable_packages:
                        findings.append(SecurityFinding(
                            finding_id=str(uuid.uuid4()),
                            title=f"Vulnerable Dependency: {package_name}",
                            description=f"Package {package_name} may have known vulnerabilities",
                            severity=AuditSeverity.HIGH,
                            category=AuditCategory.DEPENDENCY_SECURITY,
                            affected_component="requirements.txt",
                            file_path="requirements.txt",
                            line_number=None,
                            evidence={"package": req, "vulnerability": vulnerable_packages[package_name]},
                            recommendation=f"Update {package_name} to latest secure version",
                            cwe_id="CWE-1104",
                            owasp_category="A06_2021",
                            remediation_effort="medium"
                        ))
            
        except Exception as e:
            self.logger.error(f"Error auditing Python dependencies: {e}")
        
        return findings
    
    async def _audit_node_dependencies(self) -> List[SecurityFinding]:
        """Audit Node.js dependencies for known vulnerabilities"""
        findings = []
        
        try:
            # This would typically use npm audit or similar tools
            # For now, we'll do a basic check
            
            with open("package.json", 'r') as f:
                package_data = json.load(f)
            
            dependencies = package_data.get("dependencies", {})
            
            # Check for known vulnerable packages
            for package, version in dependencies.items():
                if package in ["lodash", "moment", "jquery"] and "4.17.20" not in version:
                    findings.append(SecurityFinding(
                        finding_id=str(uuid.uuid4()),
                        title=f"Potentially Vulnerable Node Package: {package}",
                        description=f"Package {package} version {version} may have vulnerabilities",
                        severity=AuditSeverity.MEDIUM,
                        category=AuditCategory.DEPENDENCY_SECURITY,
                        affected_component="package.json",
                        file_path="package.json",
                        line_number=None,
                        evidence={"package": package, "version": version},
                        recommendation=f"Update {package} to latest secure version",
                        cwe_id="CWE-1104",
                        owasp_category="A06_2021",
                        remediation_effort="medium"
                    ))
            
        except Exception as e:
            self.logger.error(f"Error auditing Node dependencies: {e}")
        
        return findings
    
    async def _perform_network_security_audit(self) -> List[SecurityFinding]:
        """Perform network security audit"""
        findings = []
        
        try:
            # Check for open ports
            port_findings = await self._audit_open_ports()
            findings.extend(port_findings)
            
            # Check SSL/TLS configuration
            ssl_findings = await self._audit_ssl_configuration()
            findings.extend(ssl_findings)
            
        except Exception as e:
            self.logger.error(f"Error in network security audit: {e}")
        
        return findings
    
    async def _audit_open_ports(self) -> List[SecurityFinding]:
        """Audit open network ports"""
        findings = []
        
        try:
            # Use netstat to check open ports - SECURITY FIX: Use secure subprocess
            result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True, shell=False)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'LISTEN' in line and '0.0.0.0:' in line:
                        # Extract port number
                        parts = line.split()
                        if len(parts) >= 4:
                            address = parts[3]
                            port = address.split(':')[-1]
                            
                            # Check for potentially risky open ports
                            risky_ports = ['21', '23', '25', '53', '80', '110', '143', '993', '995']
                            if port in risky_ports:
                                findings.append(SecurityFinding(
                                    finding_id=str(uuid.uuid4()),
                                    title=f"Open Network Port: {port}",
                                    description=f"Port {port} is open and listening on all interfaces",
                                    severity=AuditSeverity.MEDIUM,
                                    category=AuditCategory.NETWORK_SECURITY,
                                    affected_component=f"network_port_{port}",
                                    file_path=None,
                                    line_number=None,
                                    evidence={"port": port, "address": address},
                                    recommendation="Review if this port needs to be publicly accessible",
                                    cwe_id="CWE-200",
                                    owasp_category="A05_2021",
                                    remediation_effort="medium"
                                ))
            
        except Exception as e:
            self.logger.debug(f"Could not check open ports: {e}")
        
        return findings
    
    async def _audit_ssl_configuration(self) -> List[SecurityFinding]:
        """Audit SSL/TLS configuration"""
        findings = []
        
        try:
            # Check for SSL certificate files
            ssl_files = [
                "/etc/ssl/certs/",
                "/etc/nginx/ssl/",
                "/etc/apache2/ssl/",
                "config/ssl/"
            ]
            
            for ssl_dir in ssl_files:
                if os.path.exists(ssl_dir):
                    for root, dirs, files in os.walk(ssl_dir):
                        for file in files:
                            if file.endswith(('.pem', '.crt', '.key')):
                                file_path = os.path.join(root, file)
                                ssl_finding = await self._check_ssl_file(file_path)
                                if ssl_finding:
                                    findings.append(ssl_finding)
            
        except Exception as e:
            self.logger.error(f"Error auditing SSL configuration: {e}")
        
        return findings
    
    async def _check_ssl_file(self, file_path: str) -> Optional[SecurityFinding]:
        """Check individual SSL file for security issues"""
        try:
            file_stat = os.stat(file_path)
            
            # Check if private key has weak permissions
            if file_path.endswith('.key') and (file_stat.st_mode & 0o077):
                return SecurityFinding(
                    finding_id=str(uuid.uuid4()),
                    title="SSL Private Key with Weak Permissions",
                    description=f"SSL private key {file_path} has overly permissive file permissions",
                    severity=AuditSeverity.HIGH,
                    category=AuditCategory.ENCRYPTION,
                    affected_component=file_path,
                    file_path=file_path,
                    line_number=None,
                    evidence={"permissions": oct(file_stat.st_mode)},
                    recommendation="Set private key permissions to 600 (owner read/write only)",
                    cwe_id="CWE-732",
                    owasp_category="A02_2021",
                    remediation_effort="low"
                )
            
        except Exception as e:
            self.logger.error(f"Error checking SSL file {file_path}: {e}")
        
        return None
    
    async def _store_finding(self, finding: SecurityFinding):
        """Store security finding in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO security_findings
                (finding_id, title, description, severity, category, affected_component,
                 file_path, line_number, evidence, recommendation, cwe_id, owasp_category,
                 remediation_effort, false_positive, resolved, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                finding.finding_id, finding.title, finding.description,
                finding.severity.value, finding.category.value, finding.affected_component,
                finding.file_path, finding.line_number, json.dumps(finding.evidence),
                finding.recommendation, finding.cwe_id, finding.owasp_category,
                finding.remediation_effort, finding.false_positive, finding.resolved,
                finding.created_at
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing finding: {e}")
    
    async def _store_report(self, report: AuditReport):
        """Store audit report in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO audit_reports
                (report_id, audit_type, scope, findings, summary, recommendations,
                 compliance_status, created_at, completed_at, total_files_scanned, total_lines_scanned)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                report.report_id, report.audit_type, json.dumps(report.scope),
                json.dumps([f.finding_id for f in report.findings]),
                json.dumps(report.summary), json.dumps(report.recommendations),
                json.dumps(report.compliance_status), report.created_at, report.completed_at,
                report.total_files_scanned, report.total_lines_scanned
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing report: {e}")
    
    def _generate_audit_summary(self, findings: List[SecurityFinding]) -> Dict[str, Any]:
        """Generate audit summary from findings"""
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
            "top_issues": [],
            "risk_score": 0.0
        }
        
        try:
            # Count by severity
            for finding in findings:
                summary["by_severity"][finding.severity.value] += 1
                
                # Count by category
                category = finding.category.value
                if category not in summary["by_category"]:
                    summary["by_category"][category] = 0
                summary["by_category"][category] += 1
            
            # Calculate risk score
            severity_weights = {
                AuditSeverity.CRITICAL: 10,
                AuditSeverity.HIGH: 7,
                AuditSeverity.MEDIUM: 4,
                AuditSeverity.LOW: 2,
                AuditSeverity.INFO: 1
            }
            
            total_risk = sum(severity_weights.get(f.severity, 1) for f in findings)
            summary["risk_score"] = min(100.0, total_risk / 10.0)
            
            # Get top issues
            critical_high = [f for f in findings if f.severity in [AuditSeverity.CRITICAL, AuditSeverity.HIGH]]
            summary["top_issues"] = [f.title for f in critical_high[:5]]
            
        except Exception as e:
            self.logger.error(f"Error generating audit summary: {e}")
        
        return summary
    
    def _generate_recommendations(self, findings: List[SecurityFinding]) -> List[str]:
        """Generate security recommendations based on findings"""
        recommendations = []
        
        try:
            # Priority recommendations based on severity
            critical_findings = [f for f in findings if f.severity == AuditSeverity.CRITICAL]
            high_findings = [f for f in findings if f.severity == AuditSeverity.HIGH]
            
            if critical_findings:
                recommendations.append("URGENT: Address all critical security vulnerabilities immediately")
                for finding in critical_findings[:3]:
                    recommendations.append(f"- {finding.recommendation}")
            
            if high_findings:
                recommendations.append("HIGH PRIORITY: Remediate high-severity security issues")
                for finding in high_findings[:5]:
                    recommendations.append(f"- {finding.recommendation}")
            
            # General recommendations
            recommendations.extend([
                "Implement regular security code reviews",
                "Set up automated security scanning in CI/CD pipeline",
                "Conduct regular penetration testing",
                "Maintain an inventory of all software dependencies",
                "Implement security awareness training for development team"
            ])
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
        
        return recommendations
    
    def _assess_compliance(self, findings: List[SecurityFinding]) -> Dict[str, Any]:
        """Assess compliance with security frameworks"""
        compliance = {
            "OWASP_TOP_10": {"score": 0, "issues": []},
            "CIS_CONTROLS": {"score": 0, "issues": []},
            "NIST_CSF": {"score": 0, "issues": []}
        }
        
        try:
            # OWASP Top 10 assessment
            owasp_issues = {}
            for finding in findings:
                if finding.owasp_category:
                    if finding.owasp_category not in owasp_issues:
                        owasp_issues[finding.owasp_category] = 0
                    owasp_issues[finding.owasp_category] += 1
            
            # Calculate OWASP compliance score (100 - penalty for each category with issues)
            owasp_score = 100 - (len(owasp_issues) * 10)
            compliance["OWASP_TOP_10"]["score"] = max(0, owasp_score)
            compliance["OWASP_TOP_10"]["issues"] = list(owasp_issues.keys())
            
            # Basic CIS and NIST assessments
            config_issues = len([f for f in findings if f.category == AuditCategory.CONFIGURATION])
            access_issues = len([f for f in findings if f.category == AuditCategory.AUTHORIZATION])
            
            compliance["CIS_CONTROLS"]["score"] = max(0, 100 - (config_issues * 5))
            compliance["NIST_CSF"]["score"] = max(0, 100 - (access_issues * 8))
            
        except Exception as e:
            self.logger.error(f"Error assessing compliance: {e}")
        
        return compliance
    
    # Public API methods
    
    async def get_audit_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get audit report by ID"""
        try:
            if report_id in self.reports:
                report = self.reports[report_id]
                return asdict(report)
            
            # Load from database if not in memory
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM audit_reports WHERE report_id = ?', (report_id,))
            row = cursor.fetchone()
            
            if row:
                report = AuditReport(
                    report_id=row[0],
                    audit_type=row[1],
                    scope=json.loads(row[2]) if row[2] else [],
                    findings=[],
                    summary=json.loads(row[4]) if row[4] else {},
                    recommendations=json.loads(row[5]) if row[5] else [],
                    compliance_status=json.loads(row[6]) if row[6] else {},
                    created_at=row[7],
                    completed_at=row[8],
                    total_files_scanned=row[9],
                    total_lines_scanned=row[10]
                )
                conn.close()
                return asdict(report)
            
            conn.close()
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting audit report: {e}")
            return None
    
    async def get_security_findings(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get security findings with optional filters"""
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
                if filters.get("resolved") is not None and finding.resolved != filters["resolved"]:
                    continue
                
                finding_dict = asdict(finding)
                finding_dict["severity"] = finding.severity.value
                finding_dict["category"] = finding.category.value
                findings.append(finding_dict)
            
            # Sort by severity and creation time
            severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
            findings.sort(key=lambda x: (severity_order.get(x["severity"], 0), x["created_at"]), reverse=True)
            
            return findings
            
        except Exception as e:
            self.logger.error(f"Error getting security findings: {e}")
            return []
    
    async def update_finding(self, finding_id: str, updates: Dict[str, Any]) -> bool:
        """Update security finding"""
        try:
            if finding_id not in self.findings:
                return False
            
            finding = self.findings[finding_id]
            
            if "resolved" in updates:
                finding.resolved = updates["resolved"]
            if "false_positive" in updates:
                finding.false_positive = updates["false_positive"]
            
            await self._store_finding(finding)
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating finding: {e}")
            return False
    
    async def get_audit_statistics(self) -> Dict[str, Any]:
        """Get audit system statistics"""
        try:
            unresolved_findings = [f for f in self.findings.values() if not f.resolved and not f.false_positive]
            
            stats = {
                "total_findings": len(self.findings),
                "unresolved_findings": len(unresolved_findings),
                "total_reports": len(self.reports),
                "by_severity": {
                    "critical": len([f for f in unresolved_findings if f.severity == AuditSeverity.CRITICAL]),
                    "high": len([f for f in unresolved_findings if f.severity == AuditSeverity.HIGH]),
                    "medium": len([f for f in unresolved_findings if f.severity == AuditSeverity.MEDIUM]),
                    "low": len([f for f in unresolved_findings if f.severity == AuditSeverity.LOW]),
                    "info": len([f for f in unresolved_findings if f.severity == AuditSeverity.INFO])
                },
                "last_audit": max([r.created_at for r in self.reports.values()], default=0)
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting audit statistics: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Get audit system health status"""
        try:
            return {
                "status": "healthy",
                "total_findings": len(self.findings),
                "unresolved_critical": len([f for f in self.findings.values()
                                          if f.severity == AuditSeverity.CRITICAL and not f.resolved]),
                "database_connected": True,
                "last_audit": max([r.created_at for r in self.reports.values()], default=0)
            }
            
        except Exception as e:
            self.logger.error(f"Error in health check: {e}")
            return {"status": "unhealthy", "error": str(e)}


# Example usage and testing
async def main():
    """Example usage of the security audit system"""
    from src.consciousness_v2.consciousness_bus import ConsciousnessBus
    
    # Initialize consciousness bus
    consciousness_bus = ConsciousnessBus()
    
    # Create audit system
    audit_system = SecurityAuditSystem(consciousness_bus)
    
    # Wait for initialization
    await asyncio.sleep(2)
    
    # Get health status
    health = await audit_system.health_check()
    print(f"Audit system health: {health}")
    
    # Conduct comprehensive audit
    print("Starting comprehensive security audit...")
    report_id = await audit_system.conduct_comprehensive_audit()
    
    if report_id:
        print(f"Audit completed. Report ID: {report_id}")
        
        # Get audit report
        report = await audit_system.get_audit_report(report_id)
        if report:
            print(f"Total findings: {report['summary']['total_findings']}")
            print(f"Risk score: {report['summary']['risk_score']}")
        
        # Get security findings
        findings = await audit_system.get_security_findings({"severity": "critical"})
        print(f"Critical findings: {len(findings)}")
        
        # Get statistics
        stats = await audit_system.get_audit_statistics()
        print(f"Audit statistics: {stats}")


if __name__ == "__main__":
    asyncio.run(main())