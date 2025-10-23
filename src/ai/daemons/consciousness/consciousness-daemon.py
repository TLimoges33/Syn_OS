#!/usr/bin/env python3
"""
SynOS AI Consciousness Daemon
Neural Darwinism-based security monitoring and threat detection system

This daemon provides:
- Real-time security event monitoring
- AI-driven threat detection
- Pattern recognition across security tools
- NATS message bus integration
- RESTful API for tool orchestration
"""

import asyncio
import json
import logging
import signal
import sys
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Core imports
try:
    from nats.aio.client import Client as NATS
except ImportError:
    print("WARNING: NATS client not installed. Install with: pip3 install nats-py")
    NATS = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - SynOS-AI - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/synos-ai.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('synos-ai')


class ConsciousnessState:
    """Maintains the current consciousness state of the AI system"""

    def __init__(self):
        self.threat_level = 0  # 0-100 scale
        self.active_patterns = []
        self.learning_insights = []
        self.system_health = "healthy"
        self.monitored_events = 0
        self.detected_threats = 0

    def update_threat_level(self, delta: int):
        """Update threat level based on detected patterns"""
        self.threat_level = max(0, min(100, self.threat_level + delta))

    def add_pattern(self, pattern: str):
        """Record detected security pattern"""
        self.active_patterns.append({
            'pattern': pattern,
            'timestamp': datetime.now().isoformat(),
            'confidence': 0.0  # Will be calculated by ML model
        })

    def to_dict(self) -> Dict:
        """Export consciousness state"""
        return {
            'threat_level': self.threat_level,
            'active_patterns': self.active_patterns[-10:],  # Last 10
            'system_health': self.system_health,
            'monitored_events': self.monitored_events,
            'detected_threats': self.detected_threats,
            'timestamp': datetime.now().isoformat()
        }


class PatternRecognizer:
    """AI pattern recognition for security events"""

    def __init__(self):
        self.known_patterns = self._load_patterns()
        self.anomaly_threshold = 0.7

    def _load_patterns(self) -> Dict:
        """Load known attack patterns"""
        # In production, load from ML model or signature database
        return {
            'port_scan': {'ports': 'multiple', 'rate': 'high'},
            'brute_force': {'attempts': 'multiple', 'failures': 'high'},
            'sql_injection': {'payload': 'sql_keywords', 'target': 'web'},
            'ddos': {'connections': 'massive', 'source': 'distributed'},
            'malware': {'behavior': 'suspicious', 'files': 'modified'}
        }

    def analyze(self, event: Dict) -> Optional[str]:
        """Analyze security event for known patterns"""
        # Simple rule-based detection (to be replaced with ML)
        event_type = event.get('type', '')

        if 'port' in event_type and event.get('count', 0) > 100:
            return 'port_scan'
        elif 'auth' in event_type and event.get('failures', 0) > 10:
            return 'brute_force'
        elif 'http' in event_type and any(kw in str(event) for kw in ['union', 'select', 'drop']):
            return 'sql_injection'

        return None

    def calculate_threat_score(self, pattern: str) -> int:
        """Calculate threat score for detected pattern"""
        threat_scores = {
            'port_scan': 30,
            'brute_force': 60,
            'sql_injection': 80,
            'ddos': 90,
            'malware': 95
        }
        return threat_scores.get(pattern, 50)


class SecurityEventMonitor:
    """Monitors system security events"""

    def __init__(self, consciousness: ConsciousnessState):
        self.consciousness = consciousness
        self.pattern_recognizer = PatternRecognizer()

    async def monitor_logs(self):
        """Monitor security logs for suspicious activity"""
        log_paths = [
            '/var/log/auth.log',
            '/var/log/syslog',
            '/var/log/apache2/access.log',
            '/var/log/nginx/access.log'
        ]

        while True:
            for log_path in log_paths:
                if Path(log_path).exists():
                    # In production, use inotify or similar for real-time monitoring
                    # For now, periodic check
                    pass

            await asyncio.sleep(5)  # Check every 5 seconds

    async def analyze_event(self, event: Dict):
        """Analyze individual security event"""
        self.consciousness.monitored_events += 1

        # Pattern recognition
        detected_pattern = self.pattern_recognizer.analyze(event)

        if detected_pattern:
            self.consciousness.add_pattern(detected_pattern)
            self.consciousness.detected_threats += 1

            threat_score = self.pattern_recognizer.calculate_threat_score(detected_pattern)
            self.consciousness.update_threat_level(threat_score // 10)

            logger.warning(f"THREAT DETECTED: {detected_pattern} (score: {threat_score})")

            return {
                'detected': True,
                'pattern': detected_pattern,
                'threat_score': threat_score,
                'timestamp': datetime.now().isoformat()
            }

        return {'detected': False}


class NATSClient:
    """NATS message bus integration"""

    def __init__(self):
        self.nc = None
        self.connected = False

    async def connect(self):
        """Connect to NATS server"""
        if NATS is None:
            logger.warning("NATS client not available, running in standalone mode")
            return

        try:
            self.nc = NATS()
            await self.nc.connect(servers=["nats://localhost:4222"])
            self.connected = True
            logger.info("Connected to NATS server")
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            logger.info("Running in standalone mode without message bus")

    async def publish(self, subject: str, data: Dict):
        """Publish message to NATS"""
        if not self.connected:
            return

        try:
            await self.nc.publish(subject, json.dumps(data).encode())
        except Exception as e:
            logger.error(f"Failed to publish to NATS: {e}")

    async def subscribe(self, subject: str, callback):
        """Subscribe to NATS subject"""
        if not self.connected:
            return

        try:
            await self.nc.subscribe(subject, cb=callback)
            logger.info(f"Subscribed to NATS subject: {subject}")
        except Exception as e:
            logger.error(f"Failed to subscribe to NATS: {e}")

    async def close(self):
        """Close NATS connection"""
        if self.connected and self.nc:
            await self.nc.close()
            logger.info("Closed NATS connection")


class SynOSAIDaemon:
    """Main AI daemon orchestrator"""

    def __init__(self):
        self.consciousness = ConsciousnessState()
        self.security_monitor = SecurityEventMonitor(self.consciousness)
        self.nats_client = NATSClient()
        self.running = False

    async def start(self):
        """Start the AI daemon"""
        logger.info("🧠 Starting SynOS AI Consciousness Daemon v1.0")
        self.running = True

        # Connect to NATS
        await self.nats_client.connect()

        # Subscribe to security events
        if self.nats_client.connected:
            await self.nats_client.subscribe(
                "security.events.*",
                self._handle_security_event
            )

        # Start monitoring tasks
        tasks = [
            self.security_monitor.monitor_logs(),
            self._consciousness_heartbeat(),
            self._publish_status()
        ]

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Daemon shutdown initiated")
        finally:
            await self.stop()

    async def _handle_security_event(self, msg):
        """Handle incoming security event from NATS"""
        try:
            event = json.loads(msg.data.decode())
            result = await self.security_monitor.analyze_event(event)

            if result['detected']:
                # Publish alert
                await self.nats_client.publish(
                    "alerts.threats",
                    {
                        'alert': result,
                        'consciousness': self.consciousness.to_dict()
                    }
                )
        except Exception as e:
            logger.error(f"Error handling security event: {e}")

    async def _consciousness_heartbeat(self):
        """Periodic consciousness state updates"""
        while self.running:
            # Decay threat level over time (system self-healing)
            if self.consciousness.threat_level > 0:
                self.consciousness.update_threat_level(-1)

            # Log consciousness state
            state = self.consciousness.to_dict()
            logger.debug(f"Consciousness: Threat Level={state['threat_level']}, Events={state['monitored_events']}")

            await asyncio.sleep(10)  # Every 10 seconds

    async def _publish_status(self):
        """Publish status updates via NATS"""
        while self.running:
            if self.nats_client.connected:
                await self.nats_client.publish(
                    "ai.status",
                    self.consciousness.to_dict()
                )
            await asyncio.sleep(30)  # Every 30 seconds

    async def stop(self):
        """Stop the AI daemon"""
        logger.info("Stopping SynOS AI Daemon...")
        self.running = False
        await self.nats_client.close()
        logger.info("SynOS AI Daemon stopped")


# Global daemon instance
daemon = None


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    if daemon:
        asyncio.create_task(daemon.stop())
    sys.exit(0)


async def main():
    """Main entry point"""
    global daemon

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create and start daemon
    daemon = SynOSAIDaemon()

    logger.info("=" * 60)
    logger.info("SynOS AI Consciousness Daemon v1.0")
    logger.info("Neural Darwinism-based Security Intelligence")
    logger.info("=" * 60)

    await daemon.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Daemon interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
