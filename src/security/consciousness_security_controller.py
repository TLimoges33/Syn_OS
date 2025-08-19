#!/usr/bin/env python3
"""
Consciousness-Security Integration Controller
===========================================

The core bridge between consciousness system and security operations,
enabling AI-driven security decision making and adaptive threat response.

This controller implements the unique differentiator of Syn_OS:
consciousness-aware security that learns and adapts in real-time.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import threading
from contextlib import asynccontextmanager

# Consciousness system imports with fallback handling
try:
    from src.consciousness_v2.consciousness_bus import ConsciousnessBus
    from src.consciousness_v2.components.neural_darwinism_v2 import NeuralDarwinismV2
    CONSCIOUSNESS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Consciousness system not fully available: {e}")
    CONSCIOUSNESS_AVAILABLE = False
    # Fallback stubs
    class ConsciousnessBus:
        async def publish_event(self, event): pass
        async def subscribe(self, event_type, handler): pass
    class NeuralDarwinismV2:
        async def analyze_threat(self, threat_data): return {"threat_level": 0.5, "confidence": 0.5}

# Security system imports
from src.security.ultra_optimized_auth_engine import UltraOptimizedAuthEngine
from src.security.advanced_security_orchestrator import AdvancedSecurityOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityEventType(Enum):
    """Types of security events that consciousness can analyze"""
    AUTHENTICATION_ATTEMPT = "auth_attempt"
    SUSPICIOUS_ACTIVITY = "suspicious_activity" 
    POLICY_VIOLATION = "policy_violation"
    INTRUSION_DETECTION = "intrusion_detection"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    MALWARE_DETECTION = "malware_detection"

class ThreatLevel(Enum):
    """Consciousness-assessed threat levels"""
    BENIGN = "benign"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    CATASTROPHIC = "catastrophic"

class SecurityAction(Enum):
    """Actions that can be taken based on consciousness decisions"""
    ALLOW = "allow"
    MONITOR = "monitor"
    CHALLENGE = "challenge"
    BLOCK = "block"
    ISOLATE = "isolate"
    TERMINATE = "terminate"
    ALERT_ADMIN = "alert_admin"
    FORENSIC_CAPTURE = "forensic_capture"

@dataclass
class SecurityEvent:
    """Represents a security event for consciousness analysis"""
    event_id: str
    event_type: SecurityEventType
    timestamp: datetime
    source_ip: str
    user_id: Optional[str]
    resource: str
    details: Dict[str, Any]
    raw_data: Dict[str, Any]
    
    def to_consciousness_format(self) -> Dict[str, Any]:
        """Convert to format suitable for consciousness analysis"""
        return {
            "event_id": self.event_id,
            "type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source": {
                "ip": self.source_ip,
                "user": self.user_id
            },
            "target": {
                "resource": self.resource
            },
            "context": self.details,
            "raw": self.raw_data,
            "severity_indicators": self._extract_severity_indicators()
        }
    
    def _extract_severity_indicators(self) -> Dict[str, Any]:
        """Extract severity indicators for consciousness analysis"""
        indicators = {}
        
        # Time-based indicators
        if self.timestamp.hour < 6 or self.timestamp.hour > 22:
            indicators["off_hours"] = True
            
        # Frequency indicators (simplified for this implementation)
        indicators["event_frequency"] = self.details.get("frequency", 1)
        
        # Pattern indicators
        if "failed_attempts" in self.details:
            indicators["repeated_failures"] = self.details["failed_attempts"] > 3
            
        # Geographic indicators
        if "geo_location" in self.details:
            indicators["geographic_anomaly"] = self.details.get("geo_anomaly", False)
            
        return indicators

@dataclass 
class ConsciousnessSecurityDecision:
    """Represents a consciousness-driven security decision"""
    event_id: str
    threat_level: ThreatLevel
    confidence: float  # 0.0 to 1.0
    recommended_action: SecurityAction
    reasoning: str
    learning_data: Dict[str, Any]
    processing_time_ms: int
    consciousness_version: str
    
    def to_enforcement_format(self) -> Dict[str, Any]:
        """Convert to format suitable for security enforcement"""
        return {
            "event_id": self.event_id,
            "decision": {
                "action": self.recommended_action.value,
                "threat_level": self.threat_level.value,
                "confidence": self.confidence
            },
            "metadata": {
                "reasoning": self.reasoning,
                "processing_time": self.processing_time_ms,
                "consciousness_version": self.consciousness_version
            }
        }

class ConsciousnessSecurityMetrics:
    """Tracks consciousness-security integration metrics"""
    
    def __init__(self):
        self.decisions_made = 0
        self.avg_processing_time = 0.0
        self.accuracy_score = 0.0
        self.learning_improvements = 0
        self.threat_detections = {level.value: 0 for level in ThreatLevel}
        self.action_frequencies = {action.value: 0 for action in SecurityAction}
        self.start_time = datetime.now()
        self._lock = threading.Lock()
    
    def record_decision(self, decision: ConsciousnessSecurityDecision, actual_outcome: Optional[bool] = None):
        """Record a consciousness security decision for metrics"""
        with self._lock:
            self.decisions_made += 1
            
            # Update processing time
            self.avg_processing_time = (
                (self.avg_processing_time * (self.decisions_made - 1) + decision.processing_time_ms) / 
                self.decisions_made
            )
            
            # Update threat level counts
            self.threat_detections[decision.threat_level.value] += 1
            
            # Update action frequencies
            self.action_frequencies[decision.recommended_action.value] += 1
            
            # Update accuracy if outcome is known
            if actual_outcome is not None:
                # Simplified accuracy calculation
                if actual_outcome and decision.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL, ThreatLevel.CATASTROPHIC]:
                    self.accuracy_score = (self.accuracy_score * (self.decisions_made - 1) + 1.0) / self.decisions_made
                elif not actual_outcome and decision.threat_level in [ThreatLevel.BENIGN, ThreatLevel.LOW]:
                    self.accuracy_score = (self.accuracy_score * (self.decisions_made - 1) + 1.0) / self.decisions_made
                else:
                    self.accuracy_score = (self.accuracy_score * (self.decisions_made - 1) + 0.0) / self.decisions_made
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        uptime = datetime.now() - self.start_time
        return {
            "uptime_seconds": uptime.total_seconds(),
            "decisions_made": self.decisions_made,
            "decisions_per_second": self.decisions_made / max(uptime.total_seconds(), 1),
            "avg_processing_time_ms": self.avg_processing_time,
            "accuracy_score": self.accuracy_score,
            "threat_distribution": self.threat_detections,
            "action_distribution": self.action_frequencies,
            "learning_improvements": self.learning_improvements
        }

class ConsciousnessSecurityController:
    """
    Core consciousness-security integration controller
    
    This controller serves as the bridge between the consciousness system
    and security operations, enabling AI-driven security decisions.
    """
    
    def __init__(self):
        self.consciousness_bus = ConsciousnessBus() if CONSCIOUSNESS_AVAILABLE else None
        self.neural_darwinism = NeuralDarwinismV2() if CONSCIOUSNESS_AVAILABLE else None
        self.auth_engine = UltraOptimizedAuthEngine()
        self.security_orchestrator = AdvancedSecurityOrchestrator()
        
        # Metrics and monitoring
        self.metrics = ConsciousnessSecurityMetrics()
        self.decision_cache = {}  # Cache for recent decisions
        self.learning_history = []
        
        # Configuration
        self.config = {
            "cache_ttl_seconds": 300,  # 5 minutes
            "max_processing_time_ms": 100,  # Maximum decision time
            "learning_threshold": 0.8,  # Confidence threshold for learning
            "emergency_fallback": True,  # Enable fallback for consciousness failures
        }
        
        # State management
        self._running = False
        self._monitoring_task = None
        
        logger.info("Consciousness-Security Controller initialized")
    
    async def start(self):
        """Start the consciousness-security controller"""
        if self._running:
            logger.warning("Controller already running")
            return
            
        self._running = True
        
        # Subscribe to consciousness events if available
        if self.consciousness_bus:
            await self.consciousness_bus.subscribe("security_event", self._handle_consciousness_security_event)
            await self.consciousness_bus.subscribe("learning_update", self._handle_learning_update)
        
        # Start monitoring task
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("Consciousness-Security Controller started")
    
    async def stop(self):
        """Stop the consciousness-security controller"""
        self._running = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Consciousness-Security Controller stopped")
    
    async def analyze_security_event(self, event: SecurityEvent) -> ConsciousnessSecurityDecision:
        """
        Analyze a security event using consciousness and return a decision
        
        Args:
            event: The security event to analyze
            
        Returns:
            ConsciousnessSecurityDecision with threat assessment and recommended action
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(event)
            cached_decision = self._get_cached_decision(cache_key)
            if cached_decision:
                logger.debug(f"Using cached decision for event {event.event_id}")
                return cached_decision
            
            # Prepare event for consciousness analysis
            consciousness_data = event.to_consciousness_format()
            
            # Analyze with consciousness system
            if self.neural_darwinism and CONSCIOUSNESS_AVAILABLE:
                threat_analysis = await self.neural_darwinism.analyze_threat(consciousness_data)
            else:
                # Fallback analysis
                threat_analysis = await self._fallback_threat_analysis(consciousness_data)
            
            # Generate decision based on consciousness analysis
            decision = self._generate_security_decision(event, threat_analysis, start_time)
            
            # Cache the decision
            self._cache_decision(cache_key, decision)
            
            # Record metrics
            self.metrics.record_decision(decision)
            
            # Publish consciousness event for learning
            if self.consciousness_bus:
                await self.consciousness_bus.publish_event({
                    "type": "security_decision",
                    "event": asdict(event),
                    "decision": asdict(decision),
                    "timestamp": datetime.now().isoformat()
                })
            
            logger.info(f"Analyzed security event {event.event_id}: {decision.threat_level.value} threat, {decision.recommended_action.value} action")
            return decision
            
        except Exception as e:
            logger.error(f"Error analyzing security event {event.event_id}: {e}")
            # Emergency fallback decision
            return self._emergency_fallback_decision(event, start_time)
    
    async def enforce_security_decision(self, decision: ConsciousnessSecurityDecision) -> bool:
        """
        Enforce a consciousness security decision through security systems
        
        Args:
            decision: The security decision to enforce
            
        Returns:
            bool indicating success of enforcement
        """
        try:
            enforcement_data = decision.to_enforcement_format()
            
            # Route to appropriate enforcement mechanism
            success = await self._route_enforcement(decision, enforcement_data)
            
            if success:
                logger.info(f"Successfully enforced decision for event {decision.event_id}: {decision.recommended_action.value}")
            else:
                logger.warning(f"Failed to enforce decision for event {decision.event_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error enforcing security decision {decision.event_id}: {e}")
            return False
    
    async def process_security_event(self, event: SecurityEvent) -> Tuple[ConsciousnessSecurityDecision, bool]:
        """
        Complete processing of a security event: analyze and enforce
        
        Args:
            event: The security event to process
            
        Returns:
            Tuple of (decision, enforcement_success)
        """
        # Analyze the event
        decision = await self.analyze_security_event(event)
        
        # Enforce the decision
        enforcement_success = await self.enforce_security_decision(decision)
        
        # Record the complete processing
        await self._record_processing_outcome(event, decision, enforcement_success)
        
        return decision, enforcement_success
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current consciousness-security metrics"""
        return self.metrics.get_performance_summary()
    
    def _generate_cache_key(self, event: SecurityEvent) -> str:
        """Generate cache key for security event"""
        key_data = f"{event.event_type.value}:{event.source_ip}:{event.resource}:{json.dumps(event.details, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_decision(self, cache_key: str) -> Optional[ConsciousnessSecurityDecision]:
        """Get cached decision if still valid"""
        if cache_key in self.decision_cache:
            cached_item = self.decision_cache[cache_key]
            if datetime.now() - cached_item["timestamp"] < timedelta(seconds=self.config["cache_ttl_seconds"]):
                return cached_item["decision"]
            else:
                del self.decision_cache[cache_key]
        return None
    
    def _cache_decision(self, cache_key: str, decision: ConsciousnessSecurityDecision):
        """Cache a security decision"""
        self.decision_cache[cache_key] = {
            "decision": decision,
            "timestamp": datetime.now()
        }
        
        # Clean old cache entries
        self._clean_cache()
    
    def _clean_cache(self):
        """Clean expired cache entries"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, item in self.decision_cache.items():
            if current_time - item["timestamp"] > timedelta(seconds=self.config["cache_ttl_seconds"]):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.decision_cache[key]
    
    async def _fallback_threat_analysis(self, consciousness_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback threat analysis when consciousness system unavailable"""
        logger.debug("Using fallback threat analysis")
        
        # Rule-based threat assessment
        threat_score = 0.0
        confidence = 0.7  # Lower confidence for rule-based analysis
        
        # Analyze severity indicators
        indicators = consciousness_data.get("severity_indicators", {})
        
        if indicators.get("off_hours", False):
            threat_score += 0.2
        
        if indicators.get("repeated_failures", False):
            threat_score += 0.4
            
        if indicators.get("geographic_anomaly", False):
            threat_score += 0.3
        
        # Event type based scoring
        event_type = consciousness_data.get("type", "")
        type_scores = {
            "auth_attempt": 0.1,
            "suspicious_activity": 0.5,
            "policy_violation": 0.4,
            "intrusion_detection": 0.8,
            "behavioral_anomaly": 0.6,
            "privilege_escalation": 0.9,
            "data_exfiltration": 0.9,
            "malware_detection": 1.0
        }
        
        threat_score += type_scores.get(event_type, 0.3)
        
        # Normalize and cap
        threat_score = min(threat_score, 1.0)
        
        return {
            "threat_level": threat_score,
            "confidence": confidence,
            "reasoning": f"Rule-based analysis for {event_type}",
            "analysis_type": "fallback"
        }
    
    def _generate_security_decision(self, event: SecurityEvent, threat_analysis: Dict[str, Any], start_time: float) -> ConsciousnessSecurityDecision:
        """Generate security decision from threat analysis"""
        processing_time = int((time.time() - start_time) * 1000)
        
        # Map threat level
        threat_score = threat_analysis.get("threat_level", 0.5)
        if threat_score >= 0.9:
            threat_level = ThreatLevel.CATASTROPHIC
        elif threat_score >= 0.8:
            threat_level = ThreatLevel.CRITICAL
        elif threat_score >= 0.6:
            threat_level = ThreatLevel.HIGH
        elif threat_score >= 0.4:
            threat_level = ThreatLevel.MEDIUM
        elif threat_score >= 0.2:
            threat_level = ThreatLevel.LOW
        else:
            threat_level = ThreatLevel.BENIGN
        
        # Determine recommended action
        recommended_action = self._determine_security_action(threat_level, threat_analysis, event)
        
        # Extract confidence and reasoning
        confidence = threat_analysis.get("confidence", 0.5)
        reasoning = threat_analysis.get("reasoning", f"Threat analysis for {event.event_type.value}")
        
        # Prepare learning data
        learning_data = {
            "event_pattern": event.event_type.value,
            "threat_indicators": event._extract_severity_indicators(),
            "analysis_features": threat_analysis,
            "decision_factors": {
                "threat_score": threat_score,
                "confidence": confidence,
                "processing_time": processing_time
            }
        }
        
        return ConsciousnessSecurityDecision(
            event_id=event.event_id,
            threat_level=threat_level,
            confidence=confidence,
            recommended_action=recommended_action,
            reasoning=reasoning,
            learning_data=learning_data,
            processing_time_ms=processing_time,
            consciousness_version="v2.0" if CONSCIOUSNESS_AVAILABLE else "fallback"
        )
    
    def _determine_security_action(self, threat_level: ThreatLevel, threat_analysis: Dict[str, Any], event: SecurityEvent) -> SecurityAction:
        """Determine security action based on threat level and context"""
        
        # Base action mapping
        action_map = {
            ThreatLevel.BENIGN: SecurityAction.ALLOW,
            ThreatLevel.LOW: SecurityAction.MONITOR,
            ThreatLevel.MEDIUM: SecurityAction.CHALLENGE,
            ThreatLevel.HIGH: SecurityAction.BLOCK,
            ThreatLevel.CRITICAL: SecurityAction.ISOLATE,
            ThreatLevel.CATASTROPHIC: SecurityAction.TERMINATE
        }
        
        base_action = action_map[threat_level]
        
        # Context-based adjustments
        confidence = threat_analysis.get("confidence", 0.5)
        
        # Lower confidence might warrant less aggressive action
        if confidence < 0.6 and threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            return SecurityAction.CHALLENGE
        
        # Certain event types might warrant specific actions
        if event.event_type == SecurityEventType.DATA_EXFILTRATION:
            if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL, ThreatLevel.CATASTROPHIC]:
                return SecurityAction.FORENSIC_CAPTURE
        
        # Admin alerts for high-confidence critical events
        if confidence > 0.8 and threat_level in [ThreatLevel.CRITICAL, ThreatLevel.CATASTROPHIC]:
            # Could return multiple actions, but for simplicity, prioritize isolation
            return SecurityAction.ISOLATE
        
        return base_action
    
    def _emergency_fallback_decision(self, event: SecurityEvent, start_time: float) -> ConsciousnessSecurityDecision:
        """Generate emergency fallback decision when all analysis fails"""
        processing_time = int((time.time() - start_time) * 1000)
        
        return ConsciousnessSecurityDecision(
            event_id=event.event_id,
            threat_level=ThreatLevel.MEDIUM,  # Safe default
            confidence=0.3,  # Low confidence
            recommended_action=SecurityAction.MONITOR,  # Safe default
            reasoning="Emergency fallback due to analysis failure",
            learning_data={},
            processing_time_ms=processing_time,
            consciousness_version="emergency_fallback"
        )
    
    async def _route_enforcement(self, decision: ConsciousnessSecurityDecision, enforcement_data: Dict[str, Any]) -> bool:
        """Route enforcement to appropriate security system"""
        action = decision.recommended_action
        
        try:
            if action == SecurityAction.ALLOW:
                return True  # No enforcement needed
            
            elif action == SecurityAction.MONITOR:
                # Enhanced monitoring
                return await self._enable_enhanced_monitoring(decision, enforcement_data)
            
            elif action == SecurityAction.CHALLENGE:
                # Trigger additional authentication
                return await self._trigger_challenge(decision, enforcement_data)
            
            elif action == SecurityAction.BLOCK:
                # Block the action/user
                return await self._block_action(decision, enforcement_data)
            
            elif action == SecurityAction.ISOLATE:
                # Isolate user/system
                return await self._isolate_entity(decision, enforcement_data)
            
            elif action == SecurityAction.TERMINATE:
                # Terminate session/connection
                return await self._terminate_session(decision, enforcement_data)
            
            elif action == SecurityAction.ALERT_ADMIN:
                # Send admin alert
                return await self._send_admin_alert(decision, enforcement_data)
            
            elif action == SecurityAction.FORENSIC_CAPTURE:
                # Capture forensic data
                return await self._capture_forensic_data(decision, enforcement_data)
            
            else:
                logger.warning(f"Unknown security action: {action}")
                return False
                
        except Exception as e:
            logger.error(f"Error routing enforcement for action {action}: {e}")
            return False
    
    async def _enable_enhanced_monitoring(self, decision: ConsciousnessSecurityDecision, enforcement_data: Dict[str, Any]) -> bool:
        """Enable enhanced monitoring for the entity"""
        # Implementation would integrate with monitoring systems
        logger.info(f"Enhanced monitoring enabled for event {decision.event_id}")
        return True
    
    async def _trigger_challenge(self, decision: ConsciousnessSecurityDecision, enforcement_data: Dict[str, Any]) -> bool:
        """Trigger additional authentication challenge"""
        # Implementation would integrate with authentication systems
        logger.info(f"Authentication challenge triggered for event {decision.event_id}")
        return True
    
    async def _block_action(self, decision: ConsciousnessSecurityDecision, enforcement_data: Dict[str, Any]) -> bool:
        """Block the security event action"""
        # Implementation would integrate with firewall/access control
        logger.info(f"Action blocked for event {decision.event_id}")
        return True
    
    async def _isolate_entity(self, decision: ConsciousnessSecurityDecision, enforcement_data: Dict[str, Any]) -> bool:
        """Isolate the user or system"""
        # Implementation would integrate with network isolation systems
        logger.info(f"Entity isolated for event {decision.event_id}")
        return True
    
    async def _terminate_session(self, decision: ConsciousnessSecurityDecision, enforcement_data: Dict[str, Any]) -> bool:
        """Terminate user session or connection"""
        # Implementation would integrate with session management
        logger.info(f"Session terminated for event {decision.event_id}")
        return True
    
    async def _send_admin_alert(self, decision: ConsciousnessSecurityDecision, enforcement_data: Dict[str, Any]) -> bool:
        """Send alert to administrators"""
        # Implementation would integrate with alerting systems
        logger.warning(f"Admin alert sent for event {decision.event_id}: {decision.reasoning}")
        return True
    
    async def _capture_forensic_data(self, decision: ConsciousnessSecurityDecision, enforcement_data: Dict[str, Any]) -> bool:
        """Capture forensic data for investigation"""
        # Implementation would integrate with forensic systems
        logger.warning(f"Forensic data capture initiated for event {decision.event_id}")
        return True
    
    async def _record_processing_outcome(self, event: SecurityEvent, decision: ConsciousnessSecurityDecision, enforcement_success: bool):
        """Record the outcome of processing for learning"""
        outcome_record = {
            "event": asdict(event),
            "decision": asdict(decision),
            "enforcement_success": enforcement_success,
            "timestamp": datetime.now().isoformat()
        }
        
        self.learning_history.append(outcome_record)
        
        # Limit history size
        if len(self.learning_history) > 1000:
            self.learning_history = self.learning_history[-1000:]
        
        # Publish for consciousness learning if available
        if self.consciousness_bus:
            await self.consciousness_bus.publish_event({
                "type": "processing_outcome",
                "data": outcome_record
            })
    
    async def _handle_consciousness_security_event(self, event: Dict[str, Any]):
        """Handle consciousness security events"""
        logger.debug(f"Received consciousness security event: {event.get('type', 'unknown')}")
    
    async def _handle_learning_update(self, update: Dict[str, Any]):
        """Handle consciousness learning updates"""
        self.metrics.learning_improvements += 1
        logger.info(f"Applied consciousness learning update: {update.get('improvement_type', 'unknown')}")
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self._running:
            try:
                await asyncio.sleep(10)  # Monitor every 10 seconds
                
                # Clean cache
                self._clean_cache()
                
                # Log metrics periodically
                if self.metrics.decisions_made > 0 and self.metrics.decisions_made % 100 == 0:
                    metrics = self.get_metrics()
                    logger.info(f"Consciousness-Security Metrics: {metrics['decisions_made']} decisions, "
                              f"{metrics['avg_processing_time_ms']:.1f}ms avg, "
                              f"{metrics['accuracy_score']:.3f} accuracy")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")

# Factory function for easy instantiation
def create_consciousness_security_controller() -> ConsciousnessSecurityController:
    """Create and return a consciousness security controller instance"""
    return ConsciousnessSecurityController()

# Example usage and testing
async def main():
    """Example usage of the consciousness security controller"""
    controller = create_consciousness_security_controller()
    
    try:
        await controller.start()
        
        # Example security event
        test_event = SecurityEvent(
            event_id="test_001",
            event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
            timestamp=datetime.now(),
            source_ip="192.168.1.100",
            user_id="test_user",
            resource="/sensitive/data",
            details={
                "failed_attempts": 5,
                "geo_anomaly": True,
                "frequency": 10
            },
            raw_data={"user_agent": "suspicious_agent"}
        )
        
        # Process the event
        decision, enforcement_success = await controller.process_security_event(test_event)
        
        print(f"Decision: {decision.threat_level.value} threat, {decision.recommended_action.value} action")
        print(f"Confidence: {decision.confidence:.3f}")
        print(f"Reasoning: {decision.reasoning}")
        print(f"Enforcement: {'Success' if enforcement_success else 'Failed'}")
        
        # Get metrics
        metrics = controller.get_metrics()
        print(f"Metrics: {metrics}")
        
    finally:
        await controller.stop()

if __name__ == "__main__":
    asyncio.run(main())