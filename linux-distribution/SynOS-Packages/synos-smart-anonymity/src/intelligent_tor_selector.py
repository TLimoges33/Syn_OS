#!/usr/bin/env python3

"""
SynOS Intelligent Tor Circuit Selection
AI-driven path optimization based on network conditions and threat analysis

This module provides intelligent Tor circuit selection using:
- Network latency and bandwidth analysis
- Exit node reputation scoring
- Geographic diversity optimization
- Threat intelligence integration
- Circuit performance prediction
"""

import asyncio
import json
import logging
import time
import random
import socket
import subprocess
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
import numpy as np
from datetime import datetime, timedelta
import requests
import aiohttp
import stem
from stem import CircStatus
from stem.control import Controller
from stem.descriptor import parse_file
import geoip2.database
import geoip2.errors

logger = logging.getLogger(__name__)

class CircuitPurpose(Enum):
    """Circuit usage purposes for optimization"""
    GENERAL_BROWSING = "general_browsing"
    RECONNAISSANCE = "reconnaissance"
    EXPLOITATION = "exploitation"
    EXFILTRATION = "exfiltration"
    COMMUNICATION = "communication"
    FILE_TRANSFER = "file_transfer"
    STREAMING = "streaming"

class ThreatLevel(Enum):
    """Threat level classifications"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RelayInfo:
    """Information about a Tor relay"""
    fingerprint: str
    nickname: str
    ip_address: str
    country_code: str
    bandwidth: int
    uptime: int
    exit_policy: List[str]
    flags: Set[str]
    consensus_weight: int
    reputation_score: float = 0.0
    latency_ms: Optional[float] = None
    threat_score: float = 0.0
    last_updated: datetime = None

@dataclass
class CircuitCandidate:
    """Potential circuit configuration"""
    entry_relay: RelayInfo
    middle_relay: RelayInfo
    exit_relay: RelayInfo
    predicted_latency: float
    predicted_bandwidth: float
    privacy_score: float
    security_score: float
    overall_score: float
    geographic_diversity: float

@dataclass
class NetworkConditions:
    """Current network conditions"""
    bandwidth_mbps: float
    latency_ms: float
    jitter_ms: float
    packet_loss_percent: float
    timestamp: datetime

class IntelligentTorSelector:
    """AI-enhanced Tor circuit selection system"""

    def __init__(self, config_path: str = "/etc/synos/phase4/tor-selector-config.yaml"):
        self.config_path = config_path
        self.config = {}

        # Tor controller
        self.tor_controller: Optional[Controller] = None

        # Relay information cache
        self.relay_cache: Dict[str, RelayInfo] = {}
        self.consensus_timestamp: Optional[datetime] = None

        # Network monitoring
        self.network_conditions: Optional[NetworkConditions] = None
        self.performance_history: List[Tuple[str, float, float]] = []  # (circuit_id, latency, bandwidth)

        # Threat intelligence
        self.threat_intel: Dict[str, float] = {}  # IP -> threat_score

        # Machine learning models (simplified for this implementation)
        self.latency_model_weights = np.random.random(10)  # Placeholder for ML model
        self.bandwidth_model_weights = np.random.random(10)

        # GeoIP database
        self.geoip_reader = None

        # Performance tracking
        self.circuit_performance: Dict[str, List[float]] = {}

    async def initialize(self) -> bool:
        """Initialize the Tor selector system"""
        try:
            logger.info("Initializing Intelligent Tor Circuit Selector...")

            # Load configuration
            await self._load_configuration()

            # Initialize Tor controller
            await self._initialize_tor_controller()

            # Initialize GeoIP database
            await self._initialize_geoip()

            # Load threat intelligence
            await self._load_threat_intelligence()

            # Fetch initial relay information
            await self._fetch_relay_information()

            # Start monitoring tasks
            asyncio.create_task(self._monitor_network_conditions())
            asyncio.create_task(self._update_relay_information_periodically())

            logger.info("Intelligent Tor Circuit Selector initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Tor selector: {e}")
            return False

    async def _load_configuration(self):
        """Load configuration from YAML file"""
        try:
            import yaml
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            # Default configuration
            self.config = {
                'tor_control_port': 9051,
                'tor_control_password': None,
                'update_interval_seconds': 300,
                'max_circuit_attempts': 5,
                'min_bandwidth_kbps': 1000,
                'max_latency_ms': 2000,
                'geographic_diversity_weight': 0.3,
                'security_weight': 0.4,
                'performance_weight': 0.3,
                'threat_intel_sources': [
                    'https://reputation.alienvault.com/reputation.data',
                    'https://rules.emergingthreats.net/blockrules/compromised-ips.txt'
                ]
            }

    async def _initialize_tor_controller(self):
        """Initialize connection to Tor control port"""
        try:
            self.tor_controller = Controller.from_port(port=self.config.get('tor_control_port', 9051))
            self.tor_controller.authenticate(password=self.config.get('tor_control_password'))
            logger.info("Connected to Tor control port")
        except Exception as e:
            logger.error(f"Failed to connect to Tor controller: {e}")
            raise

    async def _initialize_geoip(self):
        """Initialize GeoIP database for geographic analysis"""
        try:
            # Try to use system GeoIP database
            geoip_paths = [
                '/usr/share/GeoIP/GeoLite2-Country.mmdb',
                '/var/lib/GeoIP/GeoLite2-Country.mmdb',
                '/opt/synos/data/GeoLite2-Country.mmdb'
            ]

            for path in geoip_paths:
                try:
                    self.geoip_reader = geoip2.database.Reader(path)
                    logger.info(f"Loaded GeoIP database from {path}")
                    break
                except FileNotFoundError:
                    continue

            if not self.geoip_reader:
                logger.warning("GeoIP database not found, geographic analysis will be limited")

        except Exception as e:
            logger.error(f"Failed to initialize GeoIP: {e}")

    async def _load_threat_intelligence(self):
        """Load threat intelligence data for relay reputation scoring"""
        try:
            logger.info("Loading threat intelligence data...")

            # Load from configured sources
            for source_url in self.config.get('threat_intel_sources', []):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(source_url, timeout=30) as response:
                            if response.status == 200:
                                data = await response.text()
                                await self._parse_threat_intel(data, source_url)
                except Exception as e:
                    logger.warning(f"Failed to load threat intel from {source_url}: {e}")

            logger.info(f"Loaded threat intelligence for {len(self.threat_intel)} IPs")

        except Exception as e:
            logger.error(f"Failed to load threat intelligence: {e}")

    async def _parse_threat_intel(self, data: str, source: str):
        """Parse threat intelligence data"""
        lines = data.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Simple IP extraction (can be enhanced for different formats)
            parts = line.split()
            if parts:
                ip = parts[0]
                try:
                    socket.inet_aton(ip)  # Validate IP address
                    # Assign threat score based on source
                    if 'compromised' in source.lower():
                        self.threat_intel[ip] = 0.8
                    else:
                        self.threat_intel[ip] = 0.5
                except socket.error:
                    continue

    async def _fetch_relay_information(self):
        """Fetch current Tor relay information"""
        try:
            logger.info("Fetching Tor relay information...")

            # Get relay descriptors
            relays = self.tor_controller.get_server_descriptors()

            for relay in relays:
                relay_info = RelayInfo(
                    fingerprint=relay.fingerprint,
                    nickname=relay.nickname,
                    ip_address=relay.address,
                    country_code=self._get_country_code(relay.address),
                    bandwidth=relay.average_bandwidth,
                    uptime=0,  # Would need additional API calls
                    exit_policy=relay.exit_policy_summary.split(',') if relay.exit_policy_summary else [],
                    flags=set(),  # Would need consensus data
                    consensus_weight=0,  # Would need consensus data
                    last_updated=datetime.now()
                )

                # Calculate reputation score
                relay_info.reputation_score = await self._calculate_reputation_score(relay_info)

                # Calculate threat score
                relay_info.threat_score = self.threat_intel.get(relay.address, 0.0)

                self.relay_cache[relay.fingerprint] = relay_info

            self.consensus_timestamp = datetime.now()
            logger.info(f"Cached information for {len(self.relay_cache)} relays")

        except Exception as e:
            logger.error(f"Failed to fetch relay information: {e}")

    def _get_country_code(self, ip_address: str) -> str:
        """Get country code for IP address"""
        if not self.geoip_reader:
            return "Unknown"

        try:
            response = self.geoip_reader.country(ip_address)
            return response.country.iso_code
        except geoip2.errors.AddressNotFoundError:
            return "Unknown"
        except Exception:
            return "Unknown"

    async def _calculate_reputation_score(self, relay: RelayInfo) -> float:
        """Calculate reputation score for a relay"""
        score = 0.5  # Base score

        # Bandwidth contribution
        if relay.bandwidth > 10000000:  # 10 MB/s
            score += 0.2
        elif relay.bandwidth > 1000000:  # 1 MB/s
            score += 0.1

        # Geographic diversity (prefer less common countries)
        country_relays = sum(1 for r in self.relay_cache.values() if r.country_code == relay.country_code)
        total_relays = len(self.relay_cache) or 1
        diversity_bonus = 0.3 * (1 - (country_relays / total_relays))
        score += diversity_bonus

        # Threat intelligence penalty
        score -= relay.threat_score

        return max(0.0, min(1.0, score))

    async def _monitor_network_conditions(self):
        """Monitor network conditions continuously"""
        while True:
            try:
                # Measure network conditions (simplified)
                latency = await self._measure_latency()
                bandwidth = await self._measure_bandwidth()

                self.network_conditions = NetworkConditions(
                    bandwidth_mbps=bandwidth,
                    latency_ms=latency,
                    jitter_ms=0.0,  # Would need more sophisticated measurement
                    packet_loss_percent=0.0,  # Would need more sophisticated measurement
                    timestamp=datetime.now()
                )

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Error monitoring network conditions: {e}")
                await asyncio.sleep(60)

    async def _measure_latency(self) -> float:
        """Measure current network latency"""
        try:
            # Ping a reliable server
            result = subprocess.run(['ping', '-c', '3', '8.8.8.8'],
                                  capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                # Extract average latency from ping output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'avg' in line:
                        parts = line.split('/')
                        if len(parts) >= 5:
                            return float(parts[4])

            return 100.0  # Default fallback

        except Exception:
            return 100.0

    async def _measure_bandwidth(self) -> float:
        """Measure available bandwidth (simplified)"""
        # This would typically use a speed test or monitor interface statistics
        # For now, return a placeholder value
        return 10.0  # 10 Mbps default

    async def _update_relay_information_periodically(self):
        """Update relay information periodically"""
        while True:
            try:
                await asyncio.sleep(self.config.get('update_interval_seconds', 300))
                await self._fetch_relay_information()
            except Exception as e:
                logger.error(f"Error updating relay information: {e}")

    async def select_optimal_circuit(self, purpose: CircuitPurpose,
                                   threat_level: ThreatLevel,
                                   target_countries: Optional[List[str]] = None,
                                   excluded_countries: Optional[List[str]] = None) -> Optional[CircuitCandidate]:
        """Select optimal Tor circuit based on current conditions and requirements"""
        try:
            logger.info(f"Selecting optimal circuit for {purpose.value} at threat level {threat_level.value}")

            # Filter relays based on requirements
            entry_relays = await self._filter_entry_relays(threat_level, excluded_countries)
            middle_relays = await self._filter_middle_relays(excluded_countries)
            exit_relays = await self._filter_exit_relays(purpose, target_countries, excluded_countries)

            if not (entry_relays and middle_relays and exit_relays):
                logger.error("Insufficient relays available for circuit construction")
                return None

            # Generate circuit candidates
            candidates = []
            max_candidates = 50  # Limit for performance

            for _ in range(max_candidates):
                entry = random.choice(entry_relays)
                middle = random.choice(middle_relays)
                exit = random.choice(exit_relays)

                # Ensure relay diversity
                if len({entry.fingerprint, middle.fingerprint, exit.fingerprint}) != 3:
                    continue

                # Ensure geographic diversity if required
                if len({entry.country_code, middle.country_code, exit.country_code}) < 2:
                    continue

                candidate = await self._evaluate_circuit_candidate(entry, middle, exit, purpose, threat_level)
                candidates.append(candidate)

            if not candidates:
                logger.error("No valid circuit candidates generated")
                return None

            # Select best candidate
            best_candidate = max(candidates, key=lambda c: c.overall_score)

            logger.info(f"Selected circuit: {best_candidate.entry_relay.country_code} -> "
                       f"{best_candidate.middle_relay.country_code} -> "
                       f"{best_candidate.exit_relay.country_code} "
                       f"(score: {best_candidate.overall_score:.3f})")

            return best_candidate

        except Exception as e:
            logger.error(f"Failed to select optimal circuit: {e}")
            return None

    async def _filter_entry_relays(self, threat_level: ThreatLevel,
                                  excluded_countries: Optional[List[str]] = None) -> List[RelayInfo]:
        """Filter suitable entry relays"""
        relays = []
        excluded = set(excluded_countries or [])

        for relay in self.relay_cache.values():
            # Skip excluded countries
            if relay.country_code in excluded:
                continue

            # Minimum bandwidth requirement
            if relay.bandwidth < self.config.get('min_bandwidth_kbps', 1000) * 1000:
                continue

            # Reputation threshold based on threat level
            min_reputation = {
                ThreatLevel.LOW: 0.3,
                ThreatLevel.MEDIUM: 0.5,
                ThreatLevel.HIGH: 0.7,
                ThreatLevel.CRITICAL: 0.8
            }.get(threat_level, 0.5)

            if relay.reputation_score < min_reputation:
                continue

            # Threat score threshold
            max_threat = {
                ThreatLevel.LOW: 0.8,
                ThreatLevel.MEDIUM: 0.5,
                ThreatLevel.HIGH: 0.3,
                ThreatLevel.CRITICAL: 0.1
            }.get(threat_level, 0.5)

            if relay.threat_score > max_threat:
                continue

            relays.append(relay)

        return relays

    async def _filter_middle_relays(self, excluded_countries: Optional[List[str]] = None) -> List[RelayInfo]:
        """Filter suitable middle relays"""
        relays = []
        excluded = set(excluded_countries or [])

        for relay in self.relay_cache.values():
            # Skip excluded countries
            if relay.country_code in excluded:
                continue

            # Higher bandwidth requirement for middle relays
            if relay.bandwidth < self.config.get('min_bandwidth_kbps', 1000) * 2000:
                continue

            # Good reputation required
            if relay.reputation_score < 0.4:
                continue

            relays.append(relay)

        return relays

    async def _filter_exit_relays(self, purpose: CircuitPurpose,
                                 target_countries: Optional[List[str]] = None,
                                 excluded_countries: Optional[List[str]] = None) -> List[RelayInfo]:
        """Filter suitable exit relays based on purpose"""
        relays = []
        excluded = set(excluded_countries or [])
        target = set(target_countries or [])

        for relay in self.relay_cache.values():
            # Skip excluded countries
            if relay.country_code in excluded:
                continue

            # Prefer target countries if specified
            if target and relay.country_code not in target:
                continue

            # Check exit policy compatibility
            if not self._check_exit_policy_compatibility(relay, purpose):
                continue

            # Higher reputation requirement for exit relays
            if relay.reputation_score < 0.6:
                continue

            # Lower threat tolerance for exit relays
            if relay.threat_score > 0.3:
                continue

            relays.append(relay)

        return relays

    def _check_exit_policy_compatibility(self, relay: RelayInfo, purpose: CircuitPurpose) -> bool:
        """Check if exit relay policy is compatible with circuit purpose"""
        # Simplified exit policy checking
        # In reality, this would parse the actual exit policy

        required_ports = {
            CircuitPurpose.GENERAL_BROWSING: [80, 443],
            CircuitPurpose.RECONNAISSANCE: [80, 443, 53],
            CircuitPurpose.EXPLOITATION: [80, 443, 22, 3389],
            CircuitPurpose.EXFILTRATION: [80, 443, 21, 22],
            CircuitPurpose.COMMUNICATION: [80, 443, 993, 587],
            CircuitPurpose.FILE_TRANSFER: [21, 22, 80, 443],
            CircuitPurpose.STREAMING: [80, 443, 1935]
        }

        # For now, assume relay allows required ports if it's an exit relay
        # Real implementation would parse exit_policy field
        return len(relay.exit_policy) > 0

    async def _evaluate_circuit_candidate(self, entry: RelayInfo, middle: RelayInfo,
                                        exit: RelayInfo, purpose: CircuitPurpose,
                                        threat_level: ThreatLevel) -> CircuitCandidate:
        """Evaluate a circuit candidate and calculate scores"""

        # Predict latency using simple model
        latency_features = np.array([
            entry.bandwidth / 1000000,  # Entry bandwidth in MB/s
            middle.bandwidth / 1000000,  # Middle bandwidth in MB/s
            exit.bandwidth / 1000000,   # Exit bandwidth in MB/s
            len({entry.country_code, middle.country_code, exit.country_code}),  # Country diversity
            (entry.reputation_score + middle.reputation_score + exit.reputation_score) / 3,
            self.network_conditions.latency_ms if self.network_conditions else 100,
            1 if purpose in [CircuitPurpose.STREAMING, CircuitPurpose.FILE_TRANSFER] else 0,
            threat_level.value == ThreatLevel.CRITICAL.value,
            0,  # Padding
            0   # Padding
        ])

        predicted_latency = max(50, np.dot(latency_features, self.latency_model_weights) + 100)

        # Predict bandwidth
        bandwidth_features = latency_features.copy()
        predicted_bandwidth = max(0.5, np.dot(bandwidth_features, self.bandwidth_model_weights) + 5)

        # Calculate privacy score
        country_diversity = len({entry.country_code, middle.country_code, exit.country_code})
        geographic_diversity = country_diversity / 3.0

        avg_reputation = (entry.reputation_score + middle.reputation_score + exit.reputation_score) / 3
        avg_threat = (entry.threat_score + middle.threat_score + exit.threat_score) / 3

        privacy_score = (geographic_diversity * 0.4 + avg_reputation * 0.4 + (1 - avg_threat) * 0.2)

        # Calculate security score
        security_score = (
            avg_reputation * 0.5 +
            (1 - avg_threat) * 0.3 +
            (1 - min(predicted_latency / 1000, 1.0)) * 0.2
        )

        # Calculate overall score
        weights = self.config
        overall_score = (
            privacy_score * weights.get('geographic_diversity_weight', 0.3) +
            security_score * weights.get('security_weight', 0.4) +
            (predicted_bandwidth / 10) * weights.get('performance_weight', 0.3)
        )

        return CircuitCandidate(
            entry_relay=entry,
            middle_relay=middle,
            exit_relay=exit,
            predicted_latency=predicted_latency,
            predicted_bandwidth=predicted_bandwidth,
            privacy_score=privacy_score,
            security_score=security_score,
            overall_score=overall_score,
            geographic_diversity=geographic_diversity
        )

    async def create_circuit(self, candidate: CircuitCandidate) -> Optional[str]:
        """Create a Tor circuit using the selected candidate"""
        try:
            logger.info("Creating Tor circuit...")

            # Build circuit path
            path = [
                candidate.entry_relay.fingerprint,
                candidate.middle_relay.fingerprint,
                candidate.exit_relay.fingerprint
            ]

            # Create circuit through Tor controller
            circuit_id = self.tor_controller.new_circuit(path, await_build=True)

            logger.info(f"Created circuit {circuit_id}: {' -> '.join(path)}")

            # Track circuit performance
            self.circuit_performance[circuit_id] = []

            return circuit_id

        except Exception as e:
            logger.error(f"Failed to create circuit: {e}")
            return None

    async def monitor_circuit_performance(self, circuit_id: str) -> Dict:
        """Monitor performance of an active circuit"""
        try:
            # Get circuit information
            circuit = self.tor_controller.get_circuit(circuit_id)

            if circuit.status != CircStatus.BUILT:
                return {'status': 'not_built', 'performance': None}

            # Measure current performance
            start_time = time.time()

            # Simple latency test through the circuit
            # In reality, this would be more sophisticated
            test_latency = await self._test_circuit_latency(circuit_id)

            # Record performance
            performance = {
                'circuit_id': circuit_id,
                'latency_ms': test_latency,
                'timestamp': datetime.now().isoformat(),
                'status': 'active'
            }

            # Store in performance history
            if circuit_id not in self.circuit_performance:
                self.circuit_performance[circuit_id] = []

            self.circuit_performance[circuit_id].append(test_latency)

            return performance

        except Exception as e:
            logger.error(f"Error monitoring circuit {circuit_id}: {e}")
            return {'status': 'error', 'error': str(e)}

    async def _test_circuit_latency(self, circuit_id: str) -> float:
        """Test latency of a specific circuit"""
        # This would typically make a request through the specific circuit
        # For now, return a simulated value
        return random.uniform(100, 500)

    async def adaptive_circuit_management(self):
        """Continuously manage and optimize circuits"""
        while True:
            try:
                # Get active circuits
                circuits = self.tor_controller.get_circuits()

                for circuit in circuits:
                    if circuit.status == CircStatus.BUILT:
                        performance = await self.monitor_circuit_performance(circuit.id)

                        # Check if circuit needs replacement
                        if await self._should_replace_circuit(circuit.id, performance):
                            logger.info(f"Replacing underperforming circuit {circuit.id}")

                            # Close old circuit
                            self.tor_controller.close_circuit(circuit.id)

                            # Create new optimized circuit
                            # This would determine purpose and requirements automatically
                            new_candidate = await self.select_optimal_circuit(
                                CircuitPurpose.GENERAL_BROWSING,
                                ThreatLevel.MEDIUM
                            )

                            if new_candidate:
                                await self.create_circuit(new_candidate)

                await asyncio.sleep(120)  # Check every 2 minutes

            except Exception as e:
                logger.error(f"Error in adaptive circuit management: {e}")
                await asyncio.sleep(120)

    async def _should_replace_circuit(self, circuit_id: str, performance: Dict) -> bool:
        """Determine if a circuit should be replaced"""
        if performance.get('status') != 'active':
            return True

        latency = performance.get('latency_ms', 0)

        # Replace if latency is too high
        if latency > self.config.get('max_latency_ms', 2000):
            return True

        # Check performance history
        if circuit_id in self.circuit_performance:
            recent_latencies = self.circuit_performance[circuit_id][-5:]  # Last 5 measurements
            if len(recent_latencies) >= 3:
                avg_latency = sum(recent_latencies) / len(recent_latencies)
                if avg_latency > self.config.get('max_latency_ms', 2000) * 0.8:
                    return True

        return False

    async def get_circuit_recommendations(self, purpose: CircuitPurpose,
                                        threat_level: ThreatLevel) -> List[Dict]:
        """Get circuit recommendations with explanations"""
        try:
            candidates = []

            # Generate multiple candidates
            for i in range(5):
                candidate = await self.select_optimal_circuit(purpose, threat_level)
                if candidate:
                    recommendation = {
                        'rank': i + 1,
                        'entry_country': candidate.entry_relay.country_code,
                        'middle_country': candidate.middle_relay.country_code,
                        'exit_country': candidate.exit_relay.country_code,
                        'predicted_latency_ms': candidate.predicted_latency,
                        'predicted_bandwidth_mbps': candidate.predicted_bandwidth,
                        'privacy_score': candidate.privacy_score,
                        'security_score': candidate.security_score,
                        'overall_score': candidate.overall_score,
                        'geographic_diversity': candidate.geographic_diversity,
                        'explanation': self._generate_explanation(candidate, purpose, threat_level)
                    }
                    candidates.append(recommendation)

            # Sort by overall score
            candidates.sort(key=lambda x: x['overall_score'], reverse=True)

            return candidates

        except Exception as e:
            logger.error(f"Error generating circuit recommendations: {e}")
            return []

    def _generate_explanation(self, candidate: CircuitCandidate,
                            purpose: CircuitPurpose, threat_level: ThreatLevel) -> str:
        """Generate human-readable explanation for circuit selection"""
        explanations = []

        if candidate.geographic_diversity >= 0.8:
            explanations.append("High geographic diversity provides better anonymity")

        if candidate.security_score >= 0.7:
            explanations.append("High-reputation relays reduce compromise risk")

        if candidate.predicted_latency < 200:
            explanations.append("Low predicted latency for good performance")

        if candidate.predicted_bandwidth > 5:
            explanations.append("High bandwidth capacity for data-intensive tasks")

        purpose_explanations = {
            CircuitPurpose.RECONNAISSANCE: "Optimized for reconnaissance activities with good exit policy coverage",
            CircuitPurpose.EXPLOITATION: "Selected for exploitation tasks with security emphasis",
            CircuitPurpose.EXFILTRATION: "High bandwidth path suitable for data exfiltration",
            CircuitPurpose.STREAMING: "Low latency configuration for streaming applications"
        }

        if purpose in purpose_explanations:
            explanations.append(purpose_explanations[purpose])

        return "; ".join(explanations) if explanations else "Balanced configuration for general use"

    async def export_circuit_analytics(self) -> Dict:
        """Export circuit performance analytics"""
        try:
            analytics = {
                'timestamp': datetime.now().isoformat(),
                'total_circuits_created': len(self.circuit_performance),
                'active_circuits': len([c for c in self.tor_controller.get_circuits()
                                      if c.status == CircStatus.BUILT]),
                'average_latency_ms': 0,
                'relay_statistics': {
                    'total_relays': len(self.relay_cache),
                    'countries_represented': len(set(r.country_code for r in self.relay_cache.values())),
                    'high_reputation_relays': len([r for r in self.relay_cache.values()
                                                 if r.reputation_score > 0.7])
                },
                'performance_history': {}
            }

            # Calculate average performance
            all_latencies = []
            for circuit_id, latencies in self.circuit_performance.items():
                if latencies:
                    analytics['performance_history'][circuit_id] = {
                        'average_latency': sum(latencies) / len(latencies),
                        'measurements': len(latencies)
                    }
                    all_latencies.extend(latencies)

            if all_latencies:
                analytics['average_latency_ms'] = sum(all_latencies) / len(all_latencies)

            return analytics

        except Exception as e:
            logger.error(f"Error exporting circuit analytics: {e}")
            return {'error': str(e)}

    async def shutdown(self):
        """Shutdown the Tor selector system"""
        try:
            logger.info("Shutting down Intelligent Tor Circuit Selector...")

            if self.tor_controller:
                self.tor_controller.close()

            if self.geoip_reader:
                self.geoip_reader.close()

            logger.info("Tor selector shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Example usage and testing
async def main():
    """Test the Intelligent Tor Selector"""
    selector = IntelligentTorSelector()

    if await selector.initialize():
        # Test circuit selection for different purposes
        purposes = [CircuitPurpose.RECONNAISSANCE, CircuitPurpose.EXPLOITATION]
        threat_levels = [ThreatLevel.MEDIUM, ThreatLevel.HIGH]

        for purpose in purposes:
            for threat_level in threat_levels:
                print(f"\n=== Testing {purpose.value} at {threat_level.value} threat level ===")

                candidate = await selector.select_optimal_circuit(purpose, threat_level)
                if candidate:
                    print(f"Selected circuit: {candidate.entry_relay.country_code} -> "
                          f"{candidate.middle_relay.country_code} -> "
                          f"{candidate.exit_relay.country_code}")
                    print(f"Overall score: {candidate.overall_score:.3f}")
                    print(f"Predicted latency: {candidate.predicted_latency:.1f}ms")
                    print(f"Privacy score: {candidate.privacy_score:.3f}")
                    print(f"Security score: {candidate.security_score:.3f}")

                # Get recommendations
                recommendations = await selector.get_circuit_recommendations(purpose, threat_level)
                if recommendations:
                    print(f"\nTop recommendation explanation: {recommendations[0]['explanation']}")

    await selector.shutdown()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())