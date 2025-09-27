#!/usr/bin/env python3
"""
SynOS Real-Time Behavior Monitoring System
Advanced system call, filesystem, and network activity analysis
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import sqlite3
from enum import Enum
import threading
import queue
import subprocess
import psutil
import os
import signal

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN


class ActivityType(Enum):
    SYSCALL = "syscall"
    FILE_OPERATION = "file_operation"
    NETWORK_CONNECTION = "network_connection"
    PROCESS_CREATION = "process_creation"
    REGISTRY_ACCESS = "registry_access"
    MEMORY_ACCESS = "memory_access"
    USER_ACTION = "user_action"


class ThreatLevel(Enum):
    BENIGN = 0
    SUSPICIOUS = 1
    MALICIOUS = 2
    CRITICAL = 3


@dataclass
class BehaviorEvent:
    id: str
    timestamp: datetime
    activity_type: ActivityType
    process_id: int
    process_name: str
    user: str
    details: Dict[str, Any]
    threat_score: float = 0.0
    threat_level: ThreatLevel = ThreatLevel.BENIGN
    anomaly_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessBehavior:
    pid: int
    name: str
    command_line: str
    start_time: datetime
    user: str
    events: List[BehaviorEvent] = field(default_factory=list)
    network_connections: List[Dict[str, Any]] = field(default_factory=list)
    file_operations: List[Dict[str, Any]] = field(default_factory=list)
    syscalls: Dict[str, int] = field(default_factory=dict)
    risk_score: float = 0.0
    is_suspicious: bool = False


@dataclass
class ThreatPattern:
    name: str
    pattern_type: str
    detection_rules: List[Dict[str, Any]]
    severity: ThreatLevel
    description: str
    indicators: List[str] = field(default_factory=list)


class SystemCallMonitor:
    """Monitor system calls using strace/ptrace"""

    def __init__(self, event_queue: queue.Queue):
        self.event_queue = event_queue
        self.monitored_processes: Dict[int, subprocess.Popen] = {}
        self.running = False

    def start_monitoring(self, target_pids: Optional[List[int]] = None):
        """Start monitoring system calls"""
        self.running = True

        if target_pids:
            for pid in target_pids:
                self._monitor_process(pid)
        else:
            # Monitor all new processes
            threading.Thread(target=self._monitor_all_processes, daemon=True).start()

    def _monitor_process(self, pid: int):
        """Monitor specific process using strace"""
        try:
            # Use strace to monitor syscalls
            cmd = ['strace', '-p', str(pid), '-e', 'trace=all', '-f', '-t', '-T']
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            self.monitored_processes[pid] = process

            # Read strace output in separate thread
            threading.Thread(
                target=self._parse_strace_output,
                args=(process, pid),
                daemon=True
            ).start()

        except Exception as e:
            logging.error(f"Failed to monitor process {pid}: {e}")

    def _monitor_all_processes(self):
        """Monitor all processes for new creations"""
        known_pids = set(psutil.pids())

        while self.running:
            current_pids = set(psutil.pids())
            new_pids = current_pids - known_pids

            for pid in new_pids:
                try:
                    proc = psutil.Process(pid)
                    if proc.is_running():
                        self._monitor_process(pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            known_pids = current_pids
            time.sleep(1)

    def _parse_strace_output(self, process: subprocess.Popen, pid: int):
        """Parse strace output and generate events"""
        try:
            for line in process.stderr:
                if not self.running:
                    break

                # Parse strace line format: "timestamp syscall(args) = result <duration>"
                event = self._parse_syscall_line(line.strip(), pid)
                if event:
                    self.event_queue.put(event)

        except Exception as e:
            logging.error(f"Error parsing strace output for PID {pid}: {e}")

    def _parse_syscall_line(self, line: str, pid: int) -> Optional[BehaviorEvent]:
        """Parse individual strace line"""
        try:
            # Example: "10:30:15.123456 open("/etc/passwd", O_RDONLY) = 3 <0.000050>"
            parts = line.split(' ', 2)
            if len(parts) < 3:
                return None

            timestamp_str = parts[0]
            syscall_info = parts[2]

            # Extract syscall name and arguments
            if '(' not in syscall_info:
                return None

            syscall_name = syscall_info.split('(')[0]
            args_str = syscall_info.split('(', 1)[1].split(')')[0] if '(' in syscall_info else ""

            # Get process info
            try:
                proc = psutil.Process(pid)
                process_name = proc.name()
                user = proc.username()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "unknown"
                user = "unknown"

            # Create behavior event
            event = BehaviorEvent(
                id=f"syscall_{pid}_{int(time.time() * 1000000)}",
                timestamp=datetime.now(),  # Use current time since strace timestamp is relative
                activity_type=ActivityType.SYSCALL,
                process_id=pid,
                process_name=process_name,
                user=user,
                details={
                    "syscall": syscall_name,
                    "arguments": args_str,
                    "raw_line": line
                }
            )

            return event

        except Exception as e:
            logging.debug(f"Failed to parse syscall line: {line[:100]}... Error: {e}")
            return None

    def stop_monitoring(self):
        """Stop all monitoring"""
        self.running = False

        for pid, process in self.monitored_processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception:
                pass

        self.monitored_processes.clear()


class FilesystemMonitor:
    """Monitor filesystem operations using inotify"""

    def __init__(self, event_queue: queue.Queue, watch_paths: List[str] = None):
        self.event_queue = event_queue
        self.watch_paths = watch_paths or ["/", "/tmp", "/var", "/home"]
        self.running = False
        self.inotify_process = None

    def start_monitoring(self):
        """Start filesystem monitoring using inotifywait"""
        self.running = True

        cmd = [
            'inotifywait', '-m', '-r', '--format', '%T %w %e %f',
            '--timefmt', '%Y-%m-%d %H:%M:%S'
        ] + self.watch_paths

        try:
            self.inotify_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            threading.Thread(
                target=self._parse_inotify_output,
                daemon=True
            ).start()

        except FileNotFoundError:
            logging.warning("inotifywait not found - filesystem monitoring disabled")
        except Exception as e:
            logging.error(f"Failed to start filesystem monitoring: {e}")

    def _parse_inotify_output(self):
        """Parse inotifywait output"""
        if not self.inotify_process:
            return

        try:
            for line in self.inotify_process.stdout:
                if not self.running:
                    break

                event = self._parse_inotify_line(line.strip())
                if event:
                    self.event_queue.put(event)

        except Exception as e:
            logging.error(f"Error parsing inotify output: {e}")

    def _parse_inotify_line(self, line: str) -> Optional[BehaviorEvent]:
        """Parse inotify line"""
        try:
            # Format: "2024-01-01 10:30:15 /path/to/file CREATE filename"
            parts = line.split(' ', 4)
            if len(parts) < 4:
                return None

            timestamp_str = f"{parts[0]} {parts[1]}"
            file_path = parts[2]
            event_type = parts[3]
            filename = parts[4] if len(parts) > 4 else ""

            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

            # Get process info (limited without direct PID)
            details = {
                "file_path": file_path,
                "filename": filename,
                "event_type": event_type,
                "full_path": os.path.join(file_path, filename) if filename else file_path
            }

            event = BehaviorEvent(
                id=f"file_{int(time.time() * 1000000)}",
                timestamp=timestamp,
                activity_type=ActivityType.FILE_OPERATION,
                process_id=0,  # Cannot determine PID from inotify
                process_name="unknown",
                user="unknown",
                details=details
            )

            return event

        except Exception as e:
            logging.debug(f"Failed to parse inotify line: {line[:100]}... Error: {e}")
            return None

    def stop_monitoring(self):
        """Stop filesystem monitoring"""
        self.running = False
        if self.inotify_process:
            try:
                self.inotify_process.terminate()
                self.inotify_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.inotify_process.kill()
            except Exception:
                pass


class NetworkMonitor:
    """Monitor network connections and traffic"""

    def __init__(self, event_queue: queue.Queue):
        self.event_queue = event_queue
        self.running = False
        self.known_connections: Set[Tuple[str, int, str, int]] = set()

    def start_monitoring(self):
        """Start network monitoring"""
        self.running = True
        threading.Thread(target=self._monitor_connections, daemon=True).start()

    def _monitor_connections(self):
        """Monitor network connections using psutil"""
        while self.running:
            try:
                current_connections = set()

                for conn in psutil.net_connections(kind='inet'):
                    if conn.status == 'ESTABLISHED' and conn.raddr:
                        conn_tuple = (
                            conn.laddr.ip if conn.laddr else "",
                            conn.laddr.port if conn.laddr else 0,
                            conn.raddr.ip if conn.raddr else "",
                            conn.raddr.port if conn.raddr else 0
                        )
                        current_connections.add(conn_tuple)

                        # Check for new connections
                        if conn_tuple not in self.known_connections:
                            event = self._create_network_event(conn)
                            if event:
                                self.event_queue.put(event)

                self.known_connections = current_connections
                time.sleep(2)  # Check every 2 seconds

            except Exception as e:
                logging.error(f"Network monitoring error: {e}")
                time.sleep(5)

    def _create_network_event(self, conn) -> Optional[BehaviorEvent]:
        """Create network event from connection"""
        try:
            # Get process info
            process_name = "unknown"
            user = "unknown"

            if conn.pid:
                try:
                    proc = psutil.Process(conn.pid)
                    process_name = proc.name()
                    user = proc.username()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            details = {
                "local_ip": conn.laddr.ip if conn.laddr else "",
                "local_port": conn.laddr.port if conn.laddr else 0,
                "remote_ip": conn.raddr.ip if conn.raddr else "",
                "remote_port": conn.raddr.port if conn.raddr else 0,
                "status": conn.status,
                "family": conn.family.name if hasattr(conn.family, 'name') else str(conn.family),
                "type": conn.type.name if hasattr(conn.type, 'name') else str(conn.type)
            }

            event = BehaviorEvent(
                id=f"network_{conn.pid or 0}_{int(time.time() * 1000)}",
                timestamp=datetime.now(),
                activity_type=ActivityType.NETWORK_CONNECTION,
                process_id=conn.pid or 0,
                process_name=process_name,
                user=user,
                details=details
            )

            return event

        except Exception as e:
            logging.debug(f"Failed to create network event: {e}")
            return None

    def stop_monitoring(self):
        """Stop network monitoring"""
        self.running = False


class ThreatDetector:
    """Detect threats based on behavior patterns"""

    def __init__(self):
        self.threat_patterns = self._load_threat_patterns()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.trained = False

    def _load_threat_patterns(self) -> List[ThreatPattern]:
        """Load predefined threat detection patterns"""
        patterns = [
            ThreatPattern(
                name="Suspicious File Access",
                pattern_type="file_access",
                detection_rules=[
                    {"syscall": "open", "path_pattern": "/etc/shadow"},
                    {"syscall": "open", "path_pattern": "/etc/passwd"},
                    {"file_path": "/etc/ssh/ssh_host_*"}
                ],
                severity=ThreatLevel.SUSPICIOUS,
                description="Access to sensitive system files"
            ),
            ThreatPattern(
                name="Process Injection",
                pattern_type="syscall_sequence",
                detection_rules=[
                    {"syscalls": ["ptrace", "mmap", "write"], "sequence": True},
                    {"syscall": "ptrace", "args_contain": "PTRACE_POKETEXT"}
                ],
                severity=ThreatLevel.MALICIOUS,
                description="Potential process injection attack"
            ),
            ThreatPattern(
                name="Network Exfiltration",
                pattern_type="network",
                detection_rules=[
                    {"remote_port": [80, 443, 53], "data_volume": ">1MB"},
                    {"remote_ip_pattern": "tor_exit_node"}
                ],
                severity=ThreatLevel.CRITICAL,
                description="Potential data exfiltration"
            ),
            ThreatPattern(
                name="Privilege Escalation",
                pattern_type="process",
                detection_rules=[
                    {"process_name": "su", "frequency": ">5"},
                    {"process_name": "sudo", "failed_attempts": ">3"}
                ],
                severity=ThreatLevel.MALICIOUS,
                description="Potential privilege escalation attempt"
            )
        ]
        return patterns

    def analyze_event(self, event: BehaviorEvent) -> Dict[str, Any]:
        """Analyze single event for threats"""
        analysis = {
            "threat_detected": False,
            "threat_patterns": [],
            "anomaly_score": 0.0,
            "recommendations": []
        }

        # Pattern-based detection
        for pattern in self.threat_patterns:
            if self._matches_pattern(event, pattern):
                analysis["threat_detected"] = True
                analysis["threat_patterns"].append({
                    "name": pattern.name,
                    "severity": pattern.severity.value,
                    "description": pattern.description
                })
                event.threat_level = max(event.threat_level, pattern.severity)

        # Anomaly detection (if trained)
        if self.trained:
            features = self._extract_event_features(event)
            if features:
                anomaly_score = self.anomaly_detector.decision_function([features])[0]
                analysis["anomaly_score"] = float(anomaly_score)
                event.anomaly_score = abs(anomaly_score)

                if anomaly_score < -0.5:  # Threshold for anomaly
                    analysis["threat_detected"] = True
                    analysis["recommendations"].append("Investigate unusual behavior pattern")

        # Update event threat score
        event.threat_score = max(
            len(analysis["threat_patterns"]) * 0.3,
            abs(analysis["anomaly_score"]) * 0.7
        )

        return analysis

    def _matches_pattern(self, event: BehaviorEvent, pattern: ThreatPattern) -> bool:
        """Check if event matches threat pattern"""
        for rule in pattern.detection_rules:
            if self._matches_rule(event, rule):
                return True
        return False

    def _matches_rule(self, event: BehaviorEvent, rule: Dict[str, Any]) -> bool:
        """Check if event matches specific detection rule"""
        try:
            # Syscall pattern matching
            if "syscall" in rule:
                if event.activity_type != ActivityType.SYSCALL:
                    return False
                if event.details.get("syscall") != rule["syscall"]:
                    return False

            # Path pattern matching
            if "path_pattern" in rule:
                if event.activity_type == ActivityType.FILE_OPERATION:
                    file_path = event.details.get("full_path", "")
                elif event.activity_type == ActivityType.SYSCALL:
                    file_path = event.details.get("arguments", "")
                else:
                    return False

                import fnmatch
                if not fnmatch.fnmatch(file_path, rule["path_pattern"]):
                    return False

            # Network pattern matching
            if "remote_port" in rule:
                if event.activity_type != ActivityType.NETWORK_CONNECTION:
                    return False
                remote_port = event.details.get("remote_port", 0)
                if remote_port not in rule["remote_port"]:
                    return False

            # Process name matching
            if "process_name" in rule:
                if event.process_name != rule["process_name"]:
                    return False

            return True

        except Exception as e:
            logging.debug(f"Error matching rule: {e}")
            return False

    def _extract_event_features(self, event: BehaviorEvent) -> Optional[List[float]]:
        """Extract numerical features for anomaly detection"""
        try:
            features = [
                event.activity_type.value.__hash__() % 1000,  # Activity type hash
                event.process_id % 1000,  # Process ID (modulo for normalization)
                len(event.process_name),  # Process name length
                len(str(event.details)),  # Details complexity
                event.timestamp.hour,  # Hour of day
                event.timestamp.weekday(),  # Day of week
            ]

            # Activity-specific features
            if event.activity_type == ActivityType.SYSCALL:
                syscall_name = event.details.get("syscall", "")
                features.append(hash(syscall_name) % 1000)
            elif event.activity_type == ActivityType.NETWORK_CONNECTION:
                remote_port = event.details.get("remote_port", 0)
                features.append(remote_port)
            elif event.activity_type == ActivityType.FILE_OPERATION:
                file_path = event.details.get("full_path", "")
                features.append(len(file_path))

            return features

        except Exception as e:
            logging.debug(f"Feature extraction failed: {e}")
            return None

    def train_anomaly_detector(self, events: List[BehaviorEvent]):
        """Train anomaly detector on historical events"""
        if len(events) < 100:  # Need minimum data
            logging.warning("Insufficient data for anomaly detection training")
            return

        features = []
        for event in events:
            feature_vector = self._extract_event_features(event)
            if feature_vector:
                features.append(feature_vector)

        if len(features) < 50:
            return

        # Normalize features
        features_array = np.array(features)
        normalized_features = self.scaler.fit_transform(features_array)

        # Train isolation forest
        self.anomaly_detector.fit(normalized_features)
        self.trained = True

        logging.info(f"Anomaly detector trained on {len(features)} events")


class RealtimeBehaviorMonitor:
    """Main real-time behavior monitoring system"""

    def __init__(self, db_path: str = "/var/lib/synos/behavior_monitor.db"):
        self.db_path = Path(db_path)
        self.event_queue = queue.Queue(maxsize=10000)
        self.threat_detector = ThreatDetector()

        # Monitoring components
        self.syscall_monitor = SystemCallMonitor(self.event_queue)
        self.filesystem_monitor = FilesystemMonitor(self.event_queue)
        self.network_monitor = NetworkMonitor(self.event_queue)

        # Data structures
        self.active_processes: Dict[int, ProcessBehavior] = {}
        self.recent_events: List[BehaviorEvent] = []
        self.threat_alerts: List[Dict[str, Any]] = []

        # Control
        self.running = False
        self.event_processor_thread = None

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for behavior data"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS behavior_events (
                    id TEXT PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    activity_type TEXT NOT NULL,
                    process_id INTEGER NOT NULL,
                    process_name TEXT NOT NULL,
                    user_name TEXT NOT NULL,
                    details TEXT NOT NULL,
                    threat_score REAL DEFAULT 0.0,
                    threat_level INTEGER DEFAULT 0,
                    anomaly_score REAL DEFAULT 0.0,
                    metadata TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS threat_alerts (
                    id TEXT PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    event_id TEXT NOT NULL,
                    threat_patterns TEXT,
                    severity TEXT NOT NULL,
                    description TEXT,
                    recommendations TEXT,
                    acknowledged BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (event_id) REFERENCES behavior_events (id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS process_behavior (
                    pid INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    command_line TEXT,
                    start_time TIMESTAMP NOT NULL,
                    user_name TEXT NOT NULL,
                    events_count INTEGER DEFAULT 0,
                    risk_score REAL DEFAULT 0.0,
                    is_suspicious BOOLEAN DEFAULT FALSE,
                    last_activity TIMESTAMP
                )
            """)

            conn.commit()

    def start_monitoring(self, monitor_syscalls: bool = True, monitor_filesystem: bool = True, monitor_network: bool = True):
        """Start all monitoring components"""
        logging.info("Starting real-time behavior monitoring")

        self.running = True

        # Start monitoring components
        if monitor_syscalls:
            self.syscall_monitor.start_monitoring()

        if monitor_filesystem:
            self.filesystem_monitor.start_monitoring()

        if monitor_network:
            self.network_monitor.start_monitoring()

        # Start event processing thread
        self.event_processor_thread = threading.Thread(
            target=self._process_events,
            daemon=True
        )
        self.event_processor_thread.start()

        # Load historical data for training
        self._load_training_data()

        logging.info("Real-time behavior monitoring started")

    def _process_events(self):
        """Main event processing loop"""
        batch_size = 100
        events_batch = []

        while self.running:
            try:
                # Get events from queue (with timeout)
                try:
                    event = self.event_queue.get(timeout=1.0)
                    events_batch.append(event)
                except queue.Empty:
                    # Process any remaining events in batch
                    if events_batch:
                        self._process_event_batch(events_batch)
                        events_batch = []
                    continue

                # Process batch when full
                if len(events_batch) >= batch_size:
                    self._process_event_batch(events_batch)
                    events_batch = []

            except Exception as e:
                logging.error(f"Error in event processing loop: {e}")
                time.sleep(1)

        # Process remaining events
        if events_batch:
            self._process_event_batch(events_batch)

    def _process_event_batch(self, events: List[BehaviorEvent]):
        """Process a batch of events"""
        for event in events:
            try:
                # Analyze event for threats
                analysis = self.threat_detector.analyze_event(event)

                # Store event
                self._store_event(event)

                # Update process behavior
                self._update_process_behavior(event)

                # Generate alerts if necessary
                if analysis["threat_detected"]:
                    self._generate_alert(event, analysis)

                # Keep recent events for analysis
                self.recent_events.append(event)
                if len(self.recent_events) > 10000:
                    self.recent_events = self.recent_events[-5000:]

            except Exception as e:
                logging.error(f"Error processing event {event.id}: {e}")

    def _store_event(self, event: BehaviorEvent):
        """Store event in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO behavior_events
                (id, timestamp, activity_type, process_id, process_name, user_name,
                 details, threat_score, threat_level, anomaly_score, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.id, event.timestamp, event.activity_type.value,
                event.process_id, event.process_name, event.user,
                json.dumps(event.details), event.threat_score,
                event.threat_level.value, event.anomaly_score,
                json.dumps(event.metadata)
            ))
            conn.commit()

    def _update_process_behavior(self, event: BehaviorEvent):
        """Update process behavior tracking"""
        pid = event.process_id
        if pid == 0:  # Skip unknown processes
            return

        if pid not in self.active_processes:
            # Create new process behavior record
            try:
                proc = psutil.Process(pid)
                self.active_processes[pid] = ProcessBehavior(
                    pid=pid,
                    name=event.process_name,
                    command_line=' '.join(proc.cmdline()),
                    start_time=datetime.fromtimestamp(proc.create_time()),
                    user=event.user
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                self.active_processes[pid] = ProcessBehavior(
                    pid=pid,
                    name=event.process_name,
                    command_line="unknown",
                    start_time=event.timestamp,
                    user=event.user
                )

        # Update process behavior
        process_behavior = self.active_processes[pid]
        process_behavior.events.append(event)

        # Track specific activities
        if event.activity_type == ActivityType.NETWORK_CONNECTION:
            process_behavior.network_connections.append(event.details)
        elif event.activity_type == ActivityType.FILE_OPERATION:
            process_behavior.file_operations.append(event.details)
        elif event.activity_type == ActivityType.SYSCALL:
            syscall_name = event.details.get("syscall", "unknown")
            process_behavior.syscalls[syscall_name] = process_behavior.syscalls.get(syscall_name, 0) + 1

        # Update risk score
        process_behavior.risk_score = max(process_behavior.risk_score, event.threat_score)
        if event.threat_level.value >= ThreatLevel.SUSPICIOUS.value:
            process_behavior.is_suspicious = True

        # Update database
        self._update_process_db(process_behavior)

    def _update_process_db(self, process_behavior: ProcessBehavior):
        """Update process behavior in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO process_behavior
                (pid, name, command_line, start_time, user_name, events_count,
                 risk_score, is_suspicious, last_activity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                process_behavior.pid, process_behavior.name, process_behavior.command_line,
                process_behavior.start_time, process_behavior.user, len(process_behavior.events),
                process_behavior.risk_score, process_behavior.is_suspicious, datetime.now()
            ))
            conn.commit()

    def _generate_alert(self, event: BehaviorEvent, analysis: Dict[str, Any]):
        """Generate threat alert"""
        alert_id = f"alert_{int(time.time() * 1000)}_{event.id}"

        alert = {
            "id": alert_id,
            "timestamp": datetime.now(),
            "event_id": event.id,
            "event_details": {
                "activity_type": event.activity_type.value,
                "process_name": event.process_name,
                "process_id": event.process_id,
                "user": event.user,
                "details": event.details
            },
            "threat_patterns": analysis["threat_patterns"],
            "severity": event.threat_level.name,
            "anomaly_score": analysis["anomaly_score"],
            "recommendations": analysis["recommendations"],
            "acknowledged": False
        }

        self.threat_alerts.append(alert)

        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO threat_alerts
                (id, timestamp, event_id, threat_patterns, severity, description, recommendations)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                alert_id, alert["timestamp"], event.id,
                json.dumps(alert["threat_patterns"]), alert["severity"],
                f"Threat detected: {', '.join([p['name'] for p in alert['threat_patterns']])}",
                json.dumps(alert["recommendations"])
            ))
            conn.commit()

        logging.warning(f"THREAT ALERT: {alert['severity']} - {event.process_name} (PID: {event.process_id})")

    def _load_training_data(self):
        """Load historical data for training anomaly detector"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM behavior_events
                    WHERE threat_level = 0
                    ORDER BY timestamp DESC
                    LIMIT 5000
                """)

                events = []
                for row in cursor.fetchall():
                    event = BehaviorEvent(
                        id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        activity_type=ActivityType(row[2]),
                        process_id=row[3],
                        process_name=row[4],
                        user=row[5],
                        details=json.loads(row[6]),
                        threat_score=row[7],
                        threat_level=ThreatLevel(row[8]),
                        anomaly_score=row[9]
                    )
                    events.append(event)

                if events:
                    self.threat_detector.train_anomaly_detector(events)

        except Exception as e:
            logging.warning(f"Could not load training data: {e}")

    def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent threat alerts"""
        return sorted(
            self.threat_alerts[-limit:],
            key=lambda x: x["timestamp"],
            reverse=True
        )

    def get_process_statistics(self) -> Dict[str, Any]:
        """Get process behavior statistics"""
        total_processes = len(self.active_processes)
        suspicious_processes = sum(1 for p in self.active_processes.values() if p.is_suspicious)
        high_risk_processes = sum(1 for p in self.active_processes.values() if p.risk_score > 0.7)

        return {
            "total_monitored_processes": total_processes,
            "suspicious_processes": suspicious_processes,
            "high_risk_processes": high_risk_processes,
            "recent_events_count": len(self.recent_events),
            "total_alerts": len(self.threat_alerts),
            "unacknowledged_alerts": sum(1 for a in self.threat_alerts if not a["acknowledged"])
        }

    def acknowledge_alert(self, alert_id: str):
        """Mark alert as acknowledged"""
        for alert in self.threat_alerts:
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                break

        # Update database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE threat_alerts SET acknowledged = TRUE WHERE id = ?
            """, (alert_id,))
            conn.commit()

    def stop_monitoring(self):
        """Stop all monitoring"""
        logging.info("Stopping real-time behavior monitoring")

        self.running = False

        # Stop monitoring components
        self.syscall_monitor.stop_monitoring()
        self.filesystem_monitor.stop_monitoring()
        self.network_monitor.stop_monitoring()

        # Wait for event processor to finish
        if self.event_processor_thread:
            self.event_processor_thread.join(timeout=10)

        logging.info("Real-time behavior monitoring stopped")


async def main():
    """Example usage of Real-Time Behavior Monitor"""
    logging.basicConfig(level=logging.INFO)

    monitor = RealtimeBehaviorMonitor()

    print("Starting real-time behavior monitoring...")
    monitor.start_monitoring()

    try:
        # Run for demonstration
        for i in range(30):
            await asyncio.sleep(1)

            # Show statistics every 10 seconds
            if i % 10 == 0:
                stats = monitor.get_process_statistics()
                print(f"Stats: {stats['total_monitored_processes']} processes, "
                      f"{stats['recent_events_count']} events, "
                      f"{stats['total_alerts']} alerts")

                # Show recent alerts
                recent_alerts = monitor.get_recent_alerts(5)
                if recent_alerts:
                    print("Recent alerts:")
                    for alert in recent_alerts:
                        print(f"  - {alert['severity']}: {alert['event_details']['process_name']}")

    except KeyboardInterrupt:
        print("Stopping monitoring...")

    finally:
        monitor.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(main())