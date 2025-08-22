#!/usr/bin/env python3
"""
Cloud-Based Threat Intelligence Feeds for Syn_OS
Provides real-time threat intelligence integration with consciousness-aware processing
"""

import asyncio
import logging
import time
import json
import hashlib
import secrets
import os
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import aiofiles
from datetime import datetime, timedelta
import uuid
import re
from urllib.parse import urlparse

# Mock imports for development - replace with actual imports when available
try:
    from src.consciousness_v2.consciousness_bus import ConsciousnessBus, ConsciousnessState
except ImportError:
    class ConsciousnessState:
        def __init__(self):
            self.overall_consciousness_level = 0.7
            self.neural_populations = {}
            self.timestamp = time.time()
    
    class ConsciousnessBus:
        async def get_consciousness_state(self):
            return ConsciousnessState()

try:
    from src.cloud_integration.secure_cloud_connector import SecureCloudConnector, CloudRequest
except ImportError:
    class CloudRequest:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class CloudResponse:
        def __init__(self, status_code=200, data=b"", consciousness_verified=True):
            self.status_code = status_code
            self.data = data
            self.consciousness_verified = consciousness_verified
    
    class SecureCloudConnector:
        def __init__(self, consciousness_bus, tmp_engine):
            pass
        
        async def make_request(self, request):
            return CloudResponse()

try:
    from src.hardware_security.tmp_security_engine import TPMSecurityEngine
except ImportError:
    class TPMSecurityEngine:
        def __init__(self, consciousness_bus):
            pass
        
        async def generate_secure_random(self, size):
            return secrets.token_bytes(size)

try:
    from src.security.audit_logger import AuditLogger
except ImportError:
    class AuditLogger:
        async def log_system_event(self, event_type, details):
            pass


class ThreatType(Enum):
    """Types of threats"""
    MALWARE = "malware"
    PHISHING = "phishing"
    BOTNET = "botnet"
    APT = "apt"
    RANSOMWARE = "ransomware"
    TROJAN = "trojan"
    WORM = "worm"
    ROOTKIT = "rootkit"
    SPYWARE = "spyware"
    ADWARE = "adware"
    EXPLOIT = "exploit"
    VULNERABILITY = "vulnerability"
    SUSPICIOUS_DOMAIN = "suspicious_domain"
    MALICIOUS_IP = "malicious_ip"
    C2_SERVER = "c2_server"
    UNKNOWN = "unknown"


class ThreatSeverity(Enum):
    """Threat severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FeedSource(Enum):
    """Threat intelligence feed sources"""
    COMMERCIAL = "commercial"
    OPEN_SOURCE = "open_source"
    GOVERNMENT = "government"
    COMMUNITY = "community"
    INTERNAL = "internal"
    PARTNER = "partner"


class IndicatorType(Enum):
    """Types of threat indicators"""
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    URL = "url"
    FILE_HASH = "file_hash"
    EMAIL = "email"
    REGISTRY_KEY = "registry_key"
    MUTEX = "mutex"
    USER_AGENT = "user_agent"
    SSL_CERT = "ssl_cert"
    YARA_RULE = "yara_rule"


@dataclass
class ThreatIndicator:
    """Threat intelligence indicator"""
    indicator_id: str
    indicator_type: IndicatorType
    value: str
    threat_type: ThreatType
    severity: ThreatSeverity
    confidence: float
    first_seen: float
    last_seen: float
    source: str
    feed_source: FeedSource
    description: str
    tags: Set[str]
    context: Optional[Dict[str, Any]] = None
    ttl: Optional[float] = None


@dataclass
class ThreatReport:
    """Comprehensive threat report"""
    report_id: str
    title: str
    description: str
    threat_type: ThreatType
    severity: ThreatSeverity
    confidence: float
    created_at: float
    updated_at: float
    source: str
    feed_source: FeedSource
    indicators: List[str]  # List of indicator IDs
    mitre_tactics: List[str]
    mitre_techniques: List[str]
    affected_systems: List[str]
    recommendations: List[str]
    references: List[str]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class FeedConfiguration:
    """Threat intelligence feed configuration"""
    feed_id: str
    name: str
    source_type: FeedSource
    url: str
    api_key: Optional[str]
    update_interval: int
    enabled: bool
    consciousness_threshold: float
    priority: int
    tags: Set[str]
    last_update: float
    error_count: int
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ThreatMatch:
    """Threat intelligence match result"""
    match_id: str
    indicator_id: str
    matched_value: str
    threat_type: ThreatType
    severity: ThreatSeverity
    confidence: float
    timestamp: float
    source_system: str
    context: Dict[str, Any]


class ThreatIntelligenceFeeds:
    """
    Cloud-based threat intelligence feeds system
    Provides real-time threat intelligence with consciousness-aware processing
    """
    
    def __init__(self, consciousness_bus: ConsciousnessBus,
                 cloud_connector: SecureCloudConnector,
                 tmp_engine: TPMSecurityEngine):
        """Initialize threat intelligence feeds system"""
        self.consciousness_bus = consciousness_bus
        self.cloud_connector = cloud_connector
        self.tmp_engine = tmp_engine
        self.audit_logger = AuditLogger()
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.ti_directory = "/var/lib/synos/threat_intelligence"
        self.database_file = os.path.join(self.ti_directory, "threat_intelligence.db")
        
        # Feed management
        self.active_feeds: Dict[str, FeedConfiguration] = {}
        self.indicators: Dict[str, ThreatIndicator] = {}
        self.reports: Dict[str, ThreatReport] = {}
        
        # Processing state
        self.update_in_progress = False
        self.last_update_time = 0.0
        
        # Performance tracking
        self.indicators_processed = 0
        self.reports_processed = 0
        self.matches_found = 0
        self.feed_updates = 0
        
        # Consciousness-aware processing
        self.consciousness_weights = {
            ThreatSeverity.CRITICAL: 1.0,
            ThreatSeverity.HIGH: 0.8,
            ThreatSeverity.MEDIUM: 0.6,
            ThreatSeverity.LOW: 0.4,
            ThreatSeverity.INFO: 0.2
        }
        
        # Initialize system
        asyncio.create_task(self._initialize_threat_intelligence())
    
    async def _initialize_threat_intelligence(self):
        """Initialize the threat intelligence system"""
        try:
            self.logger.info("Initializing threat intelligence feeds...")
            
            # Create directory
            os.makedirs(self.ti_directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Load existing feeds
            await self._load_feed_configurations()
            
            # Start feed update loop
            asyncio.create_task(self._feed_update_loop())
            
            # Start indicator cleanup
            asyncio.create_task(self._cleanup_expired_indicators())
            
            self.logger.info("Threat intelligence feeds initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing threat intelligence: {e}")
    
    async def _initialize_database(self):
        """Initialize the threat intelligence database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_indicators (
                    indicator_id TEXT PRIMARY KEY,
                    indicator_type TEXT NOT NULL,
                    value TEXT NOT NULL,
                    threat_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    first_seen REAL NOT NULL,
                    last_seen REAL NOT NULL,
                    source TEXT NOT NULL,
                    feed_source TEXT NOT NULL,
                    description TEXT,
                    tags TEXT,
                    context TEXT,
                    ttl REAL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_reports (
                    report_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    threat_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    source TEXT NOT NULL,
                    feed_source TEXT NOT NULL,
                    indicators TEXT,
                    mitre_tactics TEXT,
                    mitre_techniques TEXT,
                    affected_systems TEXT,
                    recommendations TEXT,
                    references TEXT,
                    metadata TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feed_configurations (
                    feed_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    url TEXT NOT NULL,
                    api_key TEXT,
                    update_interval INTEGER NOT NULL,
                    enabled BOOLEAN NOT NULL,
                    consciousness_threshold REAL NOT NULL,
                    priority INTEGER NOT NULL,
                    tags TEXT,
                    last_update REAL NOT NULL,
                    error_count INTEGER NOT NULL,
                    metadata TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_matches (
                    match_id TEXT PRIMARY KEY,
                    indicator_id TEXT NOT NULL,
                    matched_value TEXT NOT NULL,
                    threat_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    timestamp REAL NOT NULL,
                    source_system TEXT NOT NULL,
                    context TEXT,
                    FOREIGN KEY (indicator_id) REFERENCES threat_indicators (indicator_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feed_updates (
                    update_id TEXT PRIMARY KEY,
                    feed_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    indicators_added INTEGER NOT NULL,
                    indicators_updated INTEGER NOT NULL,
                    reports_added INTEGER NOT NULL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    consciousness_level REAL NOT NULL,
                    FOREIGN KEY (feed_id) REFERENCES feed_configurations (feed_id)
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_indicators_value ON threat_indicators (value)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_indicators_type ON threat_indicators (indicator_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_indicators_severity ON threat_indicators (severity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_matches_timestamp ON threat_matches (timestamp)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    async def add_feed(self, name: str, source_type: FeedSource, url: str,
                      api_key: Optional[str] = None, update_interval: int = 3600,
                      consciousness_threshold: float = 0.5, priority: int = 5,
                      tags: Optional[Set[str]] = None) -> str:
        """Add a new threat intelligence feed"""
        try:
            feed_id = str(uuid.uuid4())
            
            feed_config = FeedConfiguration(
                feed_id=feed_id,
                name=name,
                source_type=source_type,
                url=url,
                api_key=api_key,
                update_interval=update_interval,
                enabled=True,
                consciousness_threshold=consciousness_threshold,
                priority=priority,
                tags=tags or set(),
                last_update=0.0,
                error_count=0
            )
            
            # Store in database
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO feed_configurations 
                (feed_id, name, source_type, url, api_key, update_interval, enabled,
                 consciousness_threshold, priority, tags, last_update, error_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                feed_config.feed_id,
                feed_config.name,
                feed_config.source_type.value,
                feed_config.url,
                feed_config.api_key,
                feed_config.update_interval,
                feed_config.enabled,
                feed_config.consciousness_threshold,
                feed_config.priority,
                json.dumps(list(feed_config.tags)),
                feed_config.last_update,
                feed_config.error_count,
                json.dumps(feed_config.metadata) if feed_config.metadata else None
            ))
            
            conn.commit()
            conn.close()
            
            # Store in memory
            self.active_feeds[feed_id] = feed_config
            
            # Log event
            await self.audit_logger.log_system_event(
                event_type="threat_feed_added",
                details={
                    "feed_id": feed_id,
                    "name": name,
                    "source_type": source_type.value,
                    "url": url,
                    "priority": priority
                }
            )
            
            self.logger.info(f"Added threat intelligence feed: {name} ({feed_id})")
            return feed_id
            
        except Exception as e:
            self.logger.error(f"Error adding feed: {e}")
            raise
    
    async def update_feed(self, feed_id: str) -> bool:
        """Update a specific threat intelligence feed"""
        try:
            if feed_id not in self.active_feeds:
                raise ValueError(f"Feed not found: {feed_id}")
            
            feed_config = self.active_feeds[feed_id]
            if not feed_config.enabled:
                self.logger.info(f"Feed disabled, skipping update: {feed_id}")
                return True
            
            # Check consciousness threshold
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            if consciousness_state.overall_consciousness_level < feed_config.consciousness_threshold:
                self.logger.warning(
                    f"Insufficient consciousness level for feed {feed_id}: "
                    f"{consciousness_state.overall_consciousness_level} < {feed_config.consciousness_threshold}"
                )
                return False
            
            self.logger.info(f"Updating threat intelligence feed: {feed_config.name}")
            
            # Fetch data from feed
            indicators_added = 0
            indicators_updated = 0
            reports_added = 0
            
            try:
                # Create cloud request for feed data
                headers = {"User-Agent": "Syn_OS-ThreatIntel/1.0"}
                if feed_config.api_key:
                    headers["Authorization"] = f"Bearer {feed_config.api_key}"
                
                request = CloudRequest(
                    request_id=f"feed_update_{feed_id}_{int(time.time())}",
                    endpoint_id="threat_feed",
                    method="GET",
                    path=feed_config.url,
                    headers=headers,
                    consciousness_level=consciousness_state.overall_consciousness_level
                )
                
                response = await self.cloud_connector.make_request(request)
                
                if response.status_code == 200:
                    # Parse feed data
                    feed_data = json.loads(response.data.decode())
                    
                    # Process indicators
                    if "indicators" in feed_data:
                        for indicator_data in feed_data["indicators"]:
                            result = await self._process_indicator(indicator_data, feed_config)
                            if result == "added":
                                indicators_added += 1
                            elif result == "updated":
                                indicators_updated += 1
                    
                    # Process reports
                    if "reports" in feed_data:
                        for report_data in feed_data["reports"]:
                            if await self._process_report(report_data, feed_config):
                                reports_added += 1
                    
                    # Update feed configuration
                    feed_config.last_update = time.time()
                    feed_config.error_count = 0
                    
                    success = True
                    error_message = None
                    
                else:
                    raise Exception(f"Feed request failed with status {response.status_code}")
                    
            except Exception as e:
                feed_config.error_count += 1
                success = False
                error_message = str(e)
                self.logger.error(f"Error updating feed {feed_id}: {e}")
            
            # Log update
            await self._log_feed_update(
                feed_id, indicators_added, indicators_updated, reports_added,
                success, error_message, consciousness_state
            )
            
            # Update feed in database
            await self._update_feed_configuration(feed_config)
            
            self.feed_updates += 1
            self.indicators_processed += indicators_added + indicators_updated
            self.reports_processed += reports_added
            
            self.logger.info(
                f"Feed update completed: {feed_config.name} - "
                f"Indicators: +{indicators_added}/~{indicators_updated}, Reports: +{reports_added}"
            )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error updating feed: {e}")
            return False
    
    async def _process_indicator(self, indicator_data: Dict[str, Any], 
                               feed_config: FeedConfiguration) -> str:
        """Process a threat indicator from feed data"""
        try:
            # Extract indicator information
            indicator_type = IndicatorType(indicator_data.get("type", "unknown"))
            value = indicator_data.get("value", "").strip()
            
            if not value:
                return "skipped"
            
            # Validate indicator format
            if not self._validate_indicator(indicator_type, value):
                return "skipped"
            
            # Create or update indicator
            indicator_id = hashlib.sha256(f"{indicator_type.value}:{value}".encode()).hexdigest()
            
            existing_indicator = self.indicators.get(indicator_id)
            current_time = time.time()
            
            if existing_indicator:
                # Update existing indicator
                existing_indicator.last_seen = current_time
                existing_indicator.confidence = max(
                    existing_indicator.confidence,
                    float(indicator_data.get("confidence", 0.5))
                )
                
                # Update tags
                new_tags = set(indicator_data.get("tags", []))
                existing_indicator.tags.update(new_tags)
                
                await self._store_indicator(existing_indicator)
                return "updated"
            else:
                # Create new indicator
                indicator = ThreatIndicator(
                    indicator_id=indicator_id,
                    indicator_type=indicator_type,
                    value=value,
                    threat_type=ThreatType(indicator_data.get("threat_type", "unknown")),
                    severity=ThreatSeverity(indicator_data.get("severity", "medium")),
                    confidence=float(indicator_data.get("confidence", 0.5)),
                    first_seen=current_time,
                    last_seen=current_time,
                    source=feed_config.name,
                    feed_source=feed_config.source_type,
                    description=indicator_data.get("description", ""),
                    tags=set(indicator_data.get("tags", [])),
                    context=indicator_data.get("context"),
                    ttl=indicator_data.get("ttl")
                )
                
                self.indicators[indicator_id] = indicator
                await self._store_indicator(indicator)
                return "added"
                
        except Exception as e:
            self.logger.error(f"Error processing indicator: {e}")
            return "error"
    
    async def _process_report(self, report_data: Dict[str, Any], 
                            feed_config: FeedConfiguration) -> bool:
        """Process a threat report from feed data"""
        try:
            report_id = report_data.get("id") or str(uuid.uuid4())
            
            # Check if report already exists
            if report_id in self.reports:
                return False
            
            # Create threat report
            report = ThreatReport(
                report_id=report_id,
                title=report_data.get("title", ""),
                description=report_data.get("description", ""),
                threat_type=ThreatType(report_data.get("threat_type", "unknown")),
                severity=ThreatSeverity(report_data.get("severity", "medium")),
                confidence=float(report_data.get("confidence", 0.5)),
                created_at=report_data.get("created_at", time.time()),
                updated_at=report_data.get("updated_at", time.time()),
                source=feed_config.name,
                feed_source=feed_config.source_type,
                indicators=report_data.get("indicators", []),
                mitre_tactics=report_data.get("mitre_tactics", []),
                mitre_techniques=report_data.get("mitre_techniques", []),
                affected_systems=report_data.get("affected_systems", []),
                recommendations=report_data.get("recommendations", []),
                references=report_data.get("references", []),
                metadata=report_data.get("metadata")
            )
            
            self.reports[report_id] = report
            await self._store_report(report)
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing report: {e}")
            return False
    
    def _validate_indicator(self, indicator_type: IndicatorType, value: str) -> bool:
        """Validate indicator format"""
        try:
            if indicator_type == IndicatorType.IP_ADDRESS:
                # Basic IP validation
                parts = value.split('.')
                if len(parts) != 4:
                    return False
                for part in parts:
                    if not (0 <= int(part) <= 255):
                        return False
                return True
                
            elif indicator_type == IndicatorType.DOMAIN:
                # Basic domain validation
                if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$', value):
                    return False
                return True
                
            elif indicator_type == IndicatorType.URL:
                # Basic URL validation
                try:
                    result = urlparse(value)
                    return all([result.scheme, result.netloc])
                except:
                    return False
                    
            elif indicator_type == IndicatorType.FILE_HASH:
                # Basic hash validation (MD5, SHA1, SHA256)
                if len(value) in [32, 40, 64] and re.match(r'^[a-fA-F0-9]+$', value):
                    return True
                return False
                
            elif indicator_type == IndicatorType.EMAIL:
                # Basic email validation
                return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value) is not None
                
            else:
                # For other types, just check if value is not empty
                return len(value.strip()) > 0
                
        except Exception:
            return False
    
    async def _store_indicator(self, indicator: ThreatIndicator):
        """Store threat indicator in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO threat_indicators 
                (indicator_id, indicator_type, value, threat_type, severity, confidence,
                 first_seen, last_seen, source, feed_source, description, tags, context, ttl)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                indicator.indicator_id,
                indicator.indicator_type.value,
                indicator.value,
                indicator.threat_type.value,
                indicator.severity.value,
                indicator.confidence,
                indicator.first_seen,
                indicator.last_seen,
                indicator.source,
                indicator.feed_source.value,
                indicator.description,
                json.dumps(list(indicator.tags)),
                json.dumps(indicator.context) if indicator.context else None,
                indicator.ttl
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing indicator: {e}")
    
    async def _store_report(self, report: ThreatReport):
        """Store threat report in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO threat_reports 
                (report_id, title, description, threat_type, severity, confidence,
                 created_at, updated_at, source, feed_source, indicators, mitre_tactics,
                 mitre_techniques, affected_systems, recommendations, references, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                report.report_id,
                report.title,
                report.description,
                report.threat_type.value,
                report.severity.value,
                report.confidence,
                report.created_at,
                report.updated_at,
                report.source,
                report.feed_source.value,
                json.dumps(report.indicators),
                json.dumps(report.mitre_tactics),
                json.dumps(report.mitre_techniques),
                json.dumps(report.affected_systems),
                json.dumps(report.recommendations),
                json.dumps(report.references),
                json.dumps(report.metadata) if report.metadata else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing report: {e}")
    
    async def check_indicator(self, indicator_type: IndicatorType, value: str,
                            source_system: str = "unknown") -> Optional[ThreatMatch]:
        """Check if an indicator matches known threats"""
        try:
            # Create indicator ID for lookup
            indicator_id = hashlib.sha256(f"{indicator_type.value}:{value}".encode()).hexdigest()
            
            # Check if indicator exists
            indicator = self.indicators.get(indicator_id)
            if not indicator:
                return None
            
            # Check if indicator is still valid (TTL)
            current_time = time.time()
            if indicator.ttl and (indicator.first_seen + indicator.ttl) < current_time:
                return None
            
            # Get consciousness state for weighting
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            
            # Calculate consciousness-weighted confidence
            severity_weight = self.consciousness_weights.get(indicator.severity, 0.5)
            consciousness_weight = consciousness_state.overall_consciousness_level
            weighted_confidence = indicator.confidence * severity_weight * consciousness_weight
            
            # Create match
            match = ThreatMatch(
                match_id=str(uuid.uuid4()),
                indicator_id=indicator_id,
                matched_value=value,
                threat_type=indicator.threat_type,
                severity=indicator.severity,
                confidence=weighted_confidence,
                timestamp=current_time,
                source_system=source_system,
                context={
                    "indicator_source": indicator.source,
                    "feed_source": indicator.feed_source.value,
                    "tags": list(indicator.tags),
                    "description": indicator.description,
                    "first_seen": indicator.first_seen,
                    "last_seen": indicator.last_seen,
                    "consciousness_level": consciousness_state.overall_consciousness_level
                }
            )
            
            # Store match
            await self._store_match(match)
            
            # Log match
            await self.audit_logger.log_system_event(
                event_type="threat_indicator_match",
                details={
                    "match_id": match.match_id,
                    "indicator_type": indicator_type.value,
                    "value": value,
                    "threat_type": indicator.threat_type.value,
                    "severity": indicator.severity.value,
                    "confidence": weighted_confidence,
                    "source_system": source_system
                }
            )
            
            self.matches_found += 1
            self.logger.warning(
                f"Threat indicator match: {indicator_type.value}={value} "
                f"({indicator.threat_type.value}, {indicator.severity.value})"
            )
            
            return match
            
        except Exception as e:
            self.logger.error(f"Error checking indicator: {e}")
            return None
    
    async def _store_match(self, match: ThreatMatch):
        """Store threat match in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO threat_matches 
                (match_id, indicator_id, matched_value, threat_type, severity,
                 confidence, timestamp, source_system, context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                match.match_id,
                match.indicator_id,
                match.matched_value,
                match.threat_type.value,
                match.severity.value,
                match.confidence,
                match.timestamp,
                match.source_system,
                json.dumps(match.context)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing match: {e}")
    
    async def _load_feed_configurations(self):
        """Load feed configurations from database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM feed_configurations')
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                feed_config = FeedConfiguration(
                    feed_id=row[0],
                    name=row[1],
                    source_type=FeedSource(row[2]),
                    url=row[3],
                    api_key=row[4],
                    update_interval=row[5],
                    enabled=row[6],
                    consciousness_threshold=row[7],
                    priority=row[8],
                    tags=set(json.loads(row[9])) if row[9] else set(),
                    last_update=row[10],
                    error_count=row[11],
                    metadata=json.loads(row[12]) if row[12] else None
                )
                
                self.active_feeds[feed_config.feed_id] = feed_config
            
            self.logger.info(f"Loaded {len(self.active_feeds)} feed configurations")
            
        except Exception as e:
            self.logger.error(f"Error loading feed configurations: {e}")
    
    async def _feed_update_loop(self):
        """Main feed update loop"""
        while True:
            try:
                if not self.update_in_progress:
                    self.update_in_progress = True
                    
                    # Get feeds that need updating
                    current_time = time.time()
                    feeds_to_update = []
                    
                    for feed_config in self.active_feeds.values():
                        if (feed_config.enabled and 
                            current_time - feed_config.last_update >= feed_config.update_interval):
                            feeds_to_update.append(feed_config)
                    
                    # Sort by priority (higher priority first)
                    feeds_to_update.sort(key=lambda f: f.priority, reverse=True)
                    
                    # Update feeds
                    for feed_config in feeds_to_update:
                        try:
                            await self.update_feed(feed_config.feed_id)
                            # Small delay between feeds to avoid overwhelming sources
                            await asyncio.sleep(1)
                        except Exception as e:
                            self.logger.error(f"Error updating feed {feed_config.feed_id}: {e}")
                    
                    self.update_in_progress = False
                    self.last_update_time = current_time
                
                # Sleep for 60 seconds before next check
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in feed update loop: {e}")
                self.update_in_progress = False
                await asyncio.sleep(60)
    
    async def _cleanup_expired_indicators(self):
        """Clean up expired threat indicators"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                current_time = time.time()
                expired_indicators = []
                
                # Find expired indicators
                for indicator_id, indicator in self.indicators.items():
                    if indicator.ttl and (indicator.first_seen + indicator.ttl) < current_time:
                        expired_indicators.append(indicator_id)
                
                # Remove expired indicators
                if expired_indicators:
                    conn = sqlite3.connect(self.database_file)
                    cursor = conn.cursor()
                    
                    for indicator_id in expired_indicators:
                        cursor.execute('DELETE FROM threat_indicators WHERE indicator_id = ?', (indicator_id,))
                        del self.indicators[indicator_id]
                    
                    conn.commit()
                    conn.close()
                    
                    self.logger.info(f"Cleaned up {len(expired_indicators)} expired indicators")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
    
    async def _log_feed_update(self, feed_id: str, indicators_added: int, indicators_updated: int,
                             reports_added: int, success: bool, error_message: Optional[str],
                             consciousness_state: ConsciousnessState):
        """Log feed update to database"""
        try:
            update_id = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO feed_updates 
                (update_id, feed_id, timestamp, indicators_added, indicators_updated,
                 reports_added, success, error_message, consciousness_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                update_id,
                feed_id,
                time.time(),
                indicators_added,
                indicators_updated,
                reports_added,
                success,
                error_message,
                consciousness_state.overall_consciousness_level
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error logging feed update: {e}")
    
    async def _update_feed_configuration(self, feed_config: FeedConfiguration):
        """Update feed configuration in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE feed_configurations 
                SET last_update = ?, error_count = ?
                WHERE feed_id = ?
            ''', (feed_config.last_update, feed_config.error_count, feed_config.feed_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error updating feed configuration: {e}")
    
    def get_threat_intelligence_status(self) -> Dict[str, Any]:
        """Get threat intelligence system status"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Get indicator counts by type
            cursor.execute('''
                SELECT indicator_type, COUNT(*) 
                FROM threat_indicators 
                GROUP BY indicator_type
            ''')
            indicator_counts = dict(cursor.fetchall())
            
            # Get indicator counts by severity
            cursor.execute('''
                SELECT severity, COUNT(*) 
                FROM threat_indicators 
                GROUP BY severity
            ''')
            severity_counts = dict(cursor.fetchall())
            
            # Get recent matches
            cursor.execute('''
                SELECT COUNT(*) FROM threat_matches 
                WHERE timestamp > ?
            ''', (time.time() - 86400,))  # Last 24 hours
            recent_matches = cursor.fetchone()[0]
            
            # Get feed status
            cursor.execute('''
                SELECT enabled, COUNT(*) 
                FROM feed_configurations 
                GROUP BY enabled
            ''')
            feed_status = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                "update_in_progress": self.update_in_progress,
                "last_update_time": self.last_update_time,
                "active_feeds": len(self.active_feeds),
                "total_indicators": len(self.indicators),
                "total_reports": len(self.reports),
                "indicator_counts": indicator_counts,
                "severity_counts": severity_counts,
                "recent_matches": recent_matches,
                "feed_status": feed_status,
                "performance_metrics": {
                    "indicators_processed": self.indicators_processed,
                    "reports_processed": self.reports_processed,
                    "matches_found": self.matches_found,
                    "feed_updates": self.feed_updates
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting threat intelligence status: {e}")
            return {"error": str(e)}
    
    def search_indicators(self, query: str, indicator_type: Optional[IndicatorType] = None,
                         severity: Optional[ThreatSeverity] = None, limit: int = 100) -> List[ThreatIndicator]:
        """Search threat indicators"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Build query
            sql = "SELECT * FROM threat_indicators WHERE value LIKE ?"
            params = [f"%{query}%"]
            
            if indicator_type:
                sql += " AND indicator_type = ?"
                params.append(indicator_type.value)
            
            if severity:
                sql += " AND severity = ?"
                params.append(severity.value)
            
            sql += " ORDER BY confidence DESC, last_seen DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()
            
            indicators = []
            for row in rows:
                indicator = ThreatIndicator(
                    indicator_id=row[0],
                    indicator_type=IndicatorType(row[1]),
                    value=row[2],
                    threat_type=ThreatType(row[3]),
                    severity=ThreatSeverity(row[4]),
                    confidence=row[5],
                    first_seen=row[6],
                    last_seen=row[7],
                    source=row[8],
                    feed_source=FeedSource(row[9]),
                    description=row[10],
                    tags=set(json.loads(row[11])) if row[11] else set(),
                    context=json.loads(row[12]) if row[12] else None,
                    ttl=row[13]
                )
                indicators.append(indicator)
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Error searching indicators: {e}")
            return []
    
    def get_recent_matches(self, hours: int = 24, limit: int = 100) -> List[ThreatMatch]:
        """Get recent threat matches"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM threat_matches 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (time.time() - (hours * 3600), limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            matches = []
            for row in rows:
                match = ThreatMatch(
                    match_id=row[0],
                    indicator_id=row[1],
                    matched_value=row[2],
                    threat_type=ThreatType(row[3]),
                    severity=ThreatSeverity(row[4]),
                    confidence=row[5],
                    timestamp=row[6],
                    source_system=row[7],
                    context=json.loads(row[8]) if row[8] else {}
                )
                matches.append(match)
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Error getting recent matches: {e}")
            return []
    
    async def bulk_check_indicators(self, indicators: List[Tuple[IndicatorType, str]],
                                  source_system: str = "bulk_check") -> List[ThreatMatch]:
        """Check multiple indicators at once"""
        matches = []
        
        for indicator_type, value in indicators:
            try:
                match = await self.check_indicator(indicator_type, value, source_system)
                if match:
                    matches.append(match)
            except Exception as e:
                self.logger.error(f"Error checking indicator {indicator_type.value}={value}: {e}")
        
        return matches
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on threat intelligence system"""
        try:
            # Check database connectivity
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM threat_indicators')
            indicator_count = cursor.fetchone()[0]
            conn.close()
            
            # Check directory
            ti_dir_exists = os.path.exists(self.ti_directory)
            
            # Check active feeds
            enabled_feeds = sum(1 for f in self.active_feeds.values() if f.enabled)
            
            return {
                "status": "healthy",
                "indicator_count": indicator_count,
                "active_feeds": len(self.active_feeds),
                "enabled_feeds": enabled_feeds,
                "ti_directory_exists": ti_dir_exists,
                "update_in_progress": self.update_in_progress,
                "threat_intelligence_status": self.get_threat_intelligence_status()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def shutdown(self):
        """Shutdown threat intelligence system"""
        self.logger.info("Shutting down threat intelligence feeds...")
        
        # Wait for current update to complete
        while self.update_in_progress:
            await asyncio.sleep(1)
        
        # Clear data structures
        self.active_feeds.clear()
        self.indicators.clear()
        self.reports.clear()
        
        self.logger.info("Threat intelligence feeds shutdown complete")


# Example usage and testing
async def main():
    """Example usage of Threat Intelligence Feeds"""
    # Initialize components
    consciousness_bus = ConsciousnessBus()
    tmp_engine = TPMSecurityEngine(consciousness_bus)
    cloud_connector = SecureCloudConnector(consciousness_bus, tmp_engine)
    ti_feeds = ThreatIntelligenceFeeds(consciousness_bus, cloud_connector, tmp_engine)
    
    # Wait for initialization
    await asyncio.sleep(3)
    
    # Health check
    health = await ti_feeds.health_check()
    print(f"Health check: {health}")
    
    if health["status"] == "healthy":
        # Add a test feed
        feed_id = await ti_feeds.add_feed(
            name="Test Threat Feed",
            source_type=FeedSource.OPEN_SOURCE,
            url="https://api.example.com/threats",
            update_interval=3600,
            priority=5
        )
        print(f"Added feed: {feed_id}")
        
        # Check a test indicator
        match = await ti_feeds.check_indicator(
            IndicatorType.IP_ADDRESS,
            "192.168.1.100",
            "test_system"
        )
        print(f"Indicator check result: {match}")
        
        # Search indicators
        indicators = ti_feeds.search_indicators("malware", limit=10)
        print(f"Found {len(indicators)} indicators")
        
        # Get recent matches
        matches = ti_feeds.get_recent_matches(hours=24)
        print(f"Recent matches: {len(matches)}")
        
        # Get status
        status = ti_feeds.get_threat_intelligence_status()
        print(f"TI status: {status}")
    
    # Shutdown
    await ti_feeds.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
            