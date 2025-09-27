#!/usr/bin/env python3
"""
SynOS Intelligent Vulnerability Scanner
AI-enhanced vulnerability assessment with context-aware scanning policies
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import xml.etree.ElementTree as ET
import subprocess
import tempfile
import hashlib
import sqlite3
from enum import Enum

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
import requests
import nmap


class ScanType(Enum):
    NETWORK = "network"
    WEB = "web"
    INFRASTRUCTURE = "infrastructure"
    COMPLIANCE = "compliance"


class VulnSeverity(Enum):
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    INFO = 1


@dataclass
class VulnPolicy:
    scan_type: ScanType
    target_profile: str
    max_scan_time: int = 3600
    concurrent_scans: int = 10
    stealth_mode: bool = True
    custom_scripts: List[str] = field(default_factory=list)
    exclusions: List[str] = field(default_factory=list)
    compliance_frameworks: List[str] = field(default_factory=list)


@dataclass
class Vulnerability:
    id: str
    name: str
    severity: VulnSeverity
    cvss_score: float
    description: str
    target: str
    port: Optional[int] = None
    service: Optional[str] = None
    cve_ids: List[str] = field(default_factory=list)
    exploit_available: bool = False
    patch_available: bool = False
    remediation: str = ""
    confidence: float = 0.0
    detected_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScanResult:
    scan_id: str
    target: str
    scan_type: ScanType
    start_time: datetime
    end_time: Optional[datetime] = None
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    scan_stats: Dict[str, Any] = field(default_factory=dict)
    ai_insights: Dict[str, Any] = field(default_factory=dict)


class AIVulnAnalyzer:
    """AI-powered vulnerability analysis and prioritization"""

    def __init__(self):
        self.severity_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.exploit_predictor = RandomForestClassifier(n_estimators=100, random_state=42)
        self.text_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.scaler = StandardScaler()
        self.trained = False

    def train_models(self, vuln_dataset: List[Dict]):
        """Train AI models on vulnerability dataset"""
        if not vuln_dataset:
            return

        df = pd.DataFrame(vuln_dataset)

        # Extract text features from vulnerability descriptions
        text_features = self.text_vectorizer.fit_transform(df['description'])

        # Extract numerical features
        numerical_features = df[['cvss_score', 'port_count', 'service_count']].fillna(0)
        scaled_features = self.scaler.fit_transform(numerical_features)

        # Combine features
        features = np.hstack([text_features.toarray(), scaled_features])

        # Train severity classifier
        if 'severity' in df.columns:
            self.severity_classifier.fit(features, df['severity'])

        # Train exploit availability predictor
        if 'has_exploit' in df.columns:
            self.exploit_predictor.fit(features, df['has_exploit'])

        self.trained = True
        logging.info("AI vulnerability models trained successfully")

    def analyze_vulnerability(self, vuln: Vulnerability) -> Dict[str, Any]:
        """Analyze single vulnerability with AI"""
        if not self.trained:
            return {"confidence": 0.5, "priority_score": vuln.severity.value}

        # Extract features
        text_features = self.text_vectorizer.transform([vuln.description])
        numerical_features = [[vuln.cvss_score, vuln.port or 0, 1]]
        scaled_features = self.scaler.transform(numerical_features)
        features = np.hstack([text_features.toarray(), scaled_features])

        # Predict severity and exploit probability
        severity_prob = self.severity_classifier.predict_proba(features)[0]
        exploit_prob = self.exploit_predictor.predict_proba(features)[0][1]

        # Calculate priority score
        priority_score = (
            vuln.severity.value * 0.4 +
            vuln.cvss_score * 0.3 +
            exploit_prob * 10 * 0.2 +
            max(severity_prob) * 5 * 0.1
        )

        return {
            "confidence": max(severity_prob),
            "exploit_probability": exploit_prob,
            "priority_score": priority_score,
            "recommended_action": self._get_action_recommendation(vuln, exploit_prob)
        }

    def _get_action_recommendation(self, vuln: Vulnerability, exploit_prob: float) -> str:
        """Generate action recommendation based on analysis"""
        if vuln.severity == VulnSeverity.CRITICAL:
            return "IMMEDIATE: Critical vulnerability requires urgent patching"
        elif exploit_prob > 0.7:
            return "HIGH: Active exploits available, prioritize patching"
        elif vuln.cvss_score > 7.0:
            return "MEDIUM: Schedule patching within 30 days"
        else:
            return "LOW: Monitor and patch during next maintenance window"


class IntelligentVulnScanner:
    """AI-enhanced vulnerability scanner with adaptive policies"""

    def __init__(self, db_path: str = "/var/lib/synos/vuln_scanner.db"):
        self.db_path = Path(db_path)
        self.ai_analyzer = AIVulnAnalyzer()
        self.nm = nmap.PortScanner()
        self.active_scans: Dict[str, asyncio.Task] = {}
        self.scan_history: List[ScanResult] = []

        # Initialize database
        self._init_database()

        # Load and train AI models
        self._load_training_data()

    def _init_database(self):
        """Initialize SQLite database for scan results"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scans (
                    scan_id TEXT PRIMARY KEY,
                    target TEXT NOT NULL,
                    scan_type TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    status TEXT DEFAULT 'running',
                    vulnerabilities_count INTEGER DEFAULT 0
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS vulnerabilities (
                    id TEXT PRIMARY KEY,
                    scan_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    severity INTEGER NOT NULL,
                    cvss_score REAL NOT NULL,
                    description TEXT,
                    target TEXT NOT NULL,
                    port INTEGER,
                    service TEXT,
                    cve_ids TEXT,
                    confidence REAL DEFAULT 0.0,
                    detected_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (scan_id) REFERENCES scans (scan_id)
                )
            """)

            conn.commit()

    def _load_training_data(self):
        """Load historical vulnerability data for AI training"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT name, description, severity, cvss_score, port, service,
                           CASE WHEN cve_ids != '' THEN 1 ELSE 0 END as has_exploit,
                           1 as port_count, 1 as service_count
                    FROM vulnerabilities
                    WHERE description IS NOT NULL
                    LIMIT 1000
                """
                df = pd.read_sql_query(query, conn)

                if len(df) > 50:  # Need minimum data for training
                    training_data = df.to_dict('records')
                    self.ai_analyzer.train_models(training_data)

        except Exception as e:
            logging.warning(f"Could not load training data: {e}")

    async def create_adaptive_policy(self, target: str, context: Dict[str, Any]) -> VulnPolicy:
        """Create AI-tailored scanning policy based on target context"""

        # Analyze target characteristics
        target_info = await self._analyze_target(target)

        # Determine scan type based on target
        if self._is_web_target(target):
            scan_type = ScanType.WEB
        elif self._is_network_range(target):
            scan_type = ScanType.NETWORK
        else:
            scan_type = ScanType.INFRASTRUCTURE

        # Adapt policy based on context
        max_time = context.get('time_budget', 3600)
        stealth = context.get('stealth_required', True)
        compliance = context.get('compliance_frameworks', [])

        # AI-driven script selection
        custom_scripts = self._select_optimal_scripts(target_info, scan_type)

        return VulnPolicy(
            scan_type=scan_type,
            target_profile=target_info.get('profile', 'unknown'),
            max_scan_time=max_time,
            stealth_mode=stealth,
            custom_scripts=custom_scripts,
            compliance_frameworks=compliance
        )

    async def scan_target(self, target: str, policy: Optional[VulnPolicy] = None) -> str:
        """Initiate intelligent vulnerability scan"""

        scan_id = self._generate_scan_id(target)

        if not policy:
            policy = await self.create_adaptive_policy(target, {})

        # Record scan start
        scan_result = ScanResult(
            scan_id=scan_id,
            target=target,
            scan_type=policy.scan_type,
            start_time=datetime.now()
        )

        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO scans (scan_id, target, scan_type, start_time)
                VALUES (?, ?, ?, ?)
            """, (scan_id, target, policy.scan_type.value, scan_result.start_time))
            conn.commit()

        # Start asynchronous scan
        scan_task = asyncio.create_task(self._execute_scan(scan_result, policy))
        self.active_scans[scan_id] = scan_task

        logging.info(f"Started intelligent scan {scan_id} for target {target}")
        return scan_id

    async def _execute_scan(self, scan_result: ScanResult, policy: VulnPolicy):
        """Execute the actual vulnerability scan"""
        try:
            vulnerabilities = []

            if policy.scan_type == ScanType.NETWORK:
                vulnerabilities.extend(await self._network_scan(scan_result.target, policy))
            elif policy.scan_type == ScanType.WEB:
                vulnerabilities.extend(await self._web_scan(scan_result.target, policy))
            elif policy.scan_type == ScanType.INFRASTRUCTURE:
                vulnerabilities.extend(await self._infrastructure_scan(scan_result.target, policy))

            # AI analysis of discovered vulnerabilities
            for vuln in vulnerabilities:
                ai_analysis = self.ai_analyzer.analyze_vulnerability(vuln)
                vuln.confidence = ai_analysis['confidence']
                vuln.metadata['ai_analysis'] = ai_analysis

            # Prioritize vulnerabilities using AI
            vulnerabilities.sort(key=lambda v: v.metadata.get('ai_analysis', {}).get('priority_score', 0), reverse=True)

            scan_result.vulnerabilities = vulnerabilities
            scan_result.end_time = datetime.now()

            # Generate AI insights
            scan_result.ai_insights = self._generate_scan_insights(vulnerabilities)

            # Update database
            self._store_scan_results(scan_result)

            logging.info(f"Scan {scan_result.scan_id} completed: {len(vulnerabilities)} vulnerabilities found")

        except Exception as e:
            logging.error(f"Scan {scan_result.scan_id} failed: {e}")

        finally:
            if scan_result.scan_id in self.active_scans:
                del self.active_scans[scan_result.scan_id]

    async def _network_scan(self, target: str, policy: VulnPolicy) -> List[Vulnerability]:
        """Perform network vulnerability scan using Nmap"""
        vulnerabilities = []

        try:
            # Adaptive Nmap command based on policy
            nmap_args = self._build_nmap_args(target, policy)

            # Execute scan
            self.nm.scan(hosts=target, arguments=nmap_args)

            for host in self.nm.all_hosts():
                for proto in self.nm[host].all_protocols():
                    ports = self.nm[host][proto].keys()

                    for port in ports:
                        port_info = self.nm[host][proto][port]

                        if port_info['state'] == 'open':
                            # Check for known vulnerabilities
                            vuln = await self._check_service_vulnerabilities(
                                host, port, port_info.get('name', ''),
                                port_info.get('version', '')
                            )

                            if vuln:
                                vulnerabilities.append(vuln)

        except Exception as e:
            logging.error(f"Network scan failed: {e}")

        return vulnerabilities

    async def _web_scan(self, target: str, policy: VulnPolicy) -> List[Vulnerability]:
        """Perform web application vulnerability scan"""
        vulnerabilities = []

        try:
            # Web-specific vulnerability checks
            vulnerabilities.extend(await self._check_ssl_vulnerabilities(target))
            vulnerabilities.extend(await self._check_http_headers(target))
            vulnerabilities.extend(await self._check_common_web_vulns(target))

        except Exception as e:
            logging.error(f"Web scan failed: {e}")

        return vulnerabilities

    async def _infrastructure_scan(self, target: str, policy: VulnPolicy) -> List[Vulnerability]:
        """Perform infrastructure vulnerability scan"""
        vulnerabilities = []

        try:
            # Infrastructure-specific checks
            vulnerabilities.extend(await self._network_scan(target, policy))
            vulnerabilities.extend(await self._check_infrastructure_config(target))

        except Exception as e:
            logging.error(f"Infrastructure scan failed: {e}")

        return vulnerabilities

    async def _check_service_vulnerabilities(self, host: str, port: int, service: str, version: str) -> Optional[Vulnerability]:
        """Check for known service vulnerabilities"""

        # Query vulnerability databases
        vuln_info = await self._query_vuln_database(service, version)

        if vuln_info:
            return Vulnerability(
                id=self._generate_vuln_id(host, port, service),
                name=f"{service} {version} - {vuln_info['name']}",
                severity=VulnSeverity(vuln_info.get('severity', 3)),
                cvss_score=vuln_info.get('cvss_score', 5.0),
                description=vuln_info.get('description', ''),
                target=host,
                port=port,
                service=service,
                cve_ids=vuln_info.get('cve_ids', [])
            )

        return None

    async def _query_vuln_database(self, service: str, version: str) -> Optional[Dict]:
        """Query external vulnerability databases"""
        try:
            # Example: Query NVD API (simplified)
            # In production, implement proper CVE database integration
            return {
                'name': f'Known vulnerability in {service}',
                'severity': 3,
                'cvss_score': 6.5,
                'description': f'Potential security issue in {service} {version}',
                'cve_ids': []
            }
        except Exception:
            return None

    def _build_nmap_args(self, target: str, policy: VulnPolicy) -> str:
        """Build adaptive Nmap command arguments"""
        args = []

        if policy.stealth_mode:
            args.extend(['-sS', '-T2'])  # Stealth SYN scan, slower timing
        else:
            args.extend(['-sV', '-T4'])  # Version detection, faster timing

        # Add custom scripts
        if policy.custom_scripts:
            args.append(f"--script={','.join(policy.custom_scripts)}")
        else:
            args.append('--script=vuln')

        # Scan timing
        args.append(f'--max-scan-delay={policy.max_scan_time}ms')

        return ' '.join(args)

    def _generate_scan_insights(self, vulnerabilities: List[Vulnerability]) -> Dict[str, Any]:
        """Generate AI-powered insights from scan results"""

        if not vulnerabilities:
            return {"summary": "No vulnerabilities detected"}

        severity_counts = {}
        for vuln in vulnerabilities:
            severity_counts[vuln.severity.name] = severity_counts.get(vuln.severity.name, 0) + 1

        # Risk assessment
        critical_count = severity_counts.get('CRITICAL', 0)
        high_count = severity_counts.get('HIGH', 0)

        if critical_count > 0:
            risk_level = "CRITICAL"
        elif high_count > 2:
            risk_level = "HIGH"
        elif high_count > 0:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "summary": f"Found {len(vulnerabilities)} vulnerabilities",
            "severity_distribution": severity_counts,
            "risk_level": risk_level,
            "recommendations": self._generate_recommendations(vulnerabilities),
            "estimated_fix_time": self._estimate_fix_time(vulnerabilities)
        }

    def _generate_recommendations(self, vulnerabilities: List[Vulnerability]) -> List[str]:
        """Generate prioritized remediation recommendations"""
        recommendations = []

        # Group by severity and type
        critical_vulns = [v for v in vulnerabilities if v.severity == VulnSeverity.CRITICAL]
        if critical_vulns:
            recommendations.append("URGENT: Address critical vulnerabilities immediately")

        # Service-specific recommendations
        services = set(v.service for v in vulnerabilities if v.service)
        for service in services:
            recommendations.append(f"Review and update {service} service configuration")

        return recommendations

    def _estimate_fix_time(self, vulnerabilities: List[Vulnerability]) -> str:
        """Estimate time required to fix vulnerabilities"""
        total_hours = sum(self._get_fix_complexity(v) for v in vulnerabilities)

        if total_hours < 8:
            return "Less than 1 day"
        elif total_hours < 40:
            return "1-5 days"
        else:
            return "More than 1 week"

    def _get_fix_complexity(self, vuln: Vulnerability) -> int:
        """Estimate complexity hours for vulnerability fix"""
        if vuln.severity == VulnSeverity.CRITICAL:
            return 8
        elif vuln.severity == VulnSeverity.HIGH:
            return 4
        elif vuln.severity == VulnSeverity.MEDIUM:
            return 2
        else:
            return 1

    def _store_scan_results(self, scan_result: ScanResult):
        """Store scan results in database"""
        with sqlite3.connect(self.db_path) as conn:
            # Update scan record
            conn.execute("""
                UPDATE scans SET end_time = ?, status = 'completed',
                               vulnerabilities_count = ?
                WHERE scan_id = ?
            """, (scan_result.end_time, len(scan_result.vulnerabilities), scan_result.scan_id))

            # Store vulnerabilities
            for vuln in scan_result.vulnerabilities:
                conn.execute("""
                    INSERT OR REPLACE INTO vulnerabilities
                    (id, scan_id, name, severity, cvss_score, description, target,
                     port, service, cve_ids, confidence, detected_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    vuln.id, scan_result.scan_id, vuln.name, vuln.severity.value,
                    vuln.cvss_score, vuln.description, vuln.target, vuln.port,
                    vuln.service, ','.join(vuln.cve_ids), vuln.confidence, vuln.detected_at
                ))

            conn.commit()

    async def get_scan_status(self, scan_id: str) -> Dict[str, Any]:
        """Get current scan status and progress"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT target, scan_type, start_time, end_time, status, vulnerabilities_count
                FROM scans WHERE scan_id = ?
            """, (scan_id,))

            result = cursor.fetchone()
            if not result:
                return {"error": "Scan not found"}

            target, scan_type, start_time, end_time, status, vuln_count = result

            return {
                "scan_id": scan_id,
                "target": target,
                "scan_type": scan_type,
                "start_time": start_time,
                "end_time": end_time,
                "status": status,
                "vulnerabilities_found": vuln_count,
                "is_active": scan_id in self.active_scans
            }

    async def get_vulnerabilities(self, scan_id: str) -> List[Dict[str, Any]]:
        """Get vulnerabilities for a specific scan"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, name, severity, cvss_score, description, target,
                       port, service, cve_ids, confidence, detected_at
                FROM vulnerabilities WHERE scan_id = ?
                ORDER BY severity DESC, cvss_score DESC
            """, (scan_id,))

            vulnerabilities = []
            for row in cursor.fetchall():
                vulnerabilities.append({
                    "id": row[0],
                    "name": row[1],
                    "severity": VulnSeverity(row[2]).name,
                    "cvss_score": row[3],
                    "description": row[4],
                    "target": row[5],
                    "port": row[6],
                    "service": row[7],
                    "cve_ids": row[8].split(',') if row[8] else [],
                    "confidence": row[9],
                    "detected_at": row[10]
                })

            return vulnerabilities

    def _generate_scan_id(self, target: str) -> str:
        """Generate unique scan ID"""
        timestamp = str(int(time.time()))
        target_hash = hashlib.md5(target.encode()).hexdigest()[:8]
        return f"scan_{timestamp}_{target_hash}"

    def _generate_vuln_id(self, host: str, port: int, service: str) -> str:
        """Generate unique vulnerability ID"""
        data = f"{host}:{port}:{service}:{int(time.time())}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    async def _analyze_target(self, target: str) -> Dict[str, Any]:
        """Analyze target characteristics for policy adaptation"""
        return {
            "profile": "unknown",
            "estimated_services": 10,
            "risk_level": "medium"
        }

    def _is_web_target(self, target: str) -> bool:
        """Check if target is a web application"""
        return target.startswith(('http://', 'https://')) or ':80' in target or ':443' in target

    def _is_network_range(self, target: str) -> bool:
        """Check if target is a network range"""
        return '/' in target or '-' in target

    def _select_optimal_scripts(self, target_info: Dict[str, Any], scan_type: ScanType) -> List[str]:
        """AI-driven selection of optimal Nmap scripts"""
        base_scripts = ["vuln", "default"]

        if scan_type == ScanType.WEB:
            base_scripts.extend(["http-enum", "http-vuln-*"])
        elif scan_type == ScanType.NETWORK:
            base_scripts.extend(["discovery", "safe"])

        return base_scripts


async def main():
    """Example usage of Intelligent Vulnerability Scanner"""
    logging.basicConfig(level=logging.INFO)

    scanner = IntelligentVulnScanner()

    # Example: Scan a target with adaptive policy
    target = "scanme.nmap.org"

    print(f"Starting intelligent vulnerability scan of {target}")
    scan_id = await scanner.scan_target(target)

    # Monitor scan progress
    while True:
        status = await scanner.get_scan_status(scan_id)
        print(f"Scan status: {status['status']}")

        if status['status'] == 'completed':
            vulnerabilities = await scanner.get_vulnerabilities(scan_id)
            print(f"Found {len(vulnerabilities)} vulnerabilities")

            for vuln in vulnerabilities[:5]:  # Show top 5
                print(f"  - {vuln['name']} (Severity: {vuln['severity']})")

            break

        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())