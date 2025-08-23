#!/usr/bin/env python3
"""
SynapticOS Consciousness Bridge
Connects kernel consciousness hooks to AI engine
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
import threading
import queue
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class KernelConsciousnessEvent:
    """Event from kernel consciousness system"""
    event_type: str
    timestamp: float
    data: Dict[str, Any]
    consciousness_level: float
    source_module: str

@dataclass
class AIResponse:
    """Response from AI system to kernel"""
    response_type: str
    content: str
    actions: List[Dict[str, Any]]
    confidence: float
    processing_time: float

class ConsciousnessBridge:
    """Bridge between kernel consciousness and AI engine"""
    
    def __init__(self):
        self.consciousness_engine = None
        self.api_manager = None
        self.kernel_event_queue = queue.Queue(maxsize=1000)
        self.ai_response_queue = queue.Queue(maxsize=1000)
        self.event_handlers = {}
        self.running = False
        self.processing_thread = None
        self.consciousness_state_cache = {}
        
        # Metrics
        self.metrics = {
            "events_processed": 0,
            "responses_sent": 0,
            "average_processing_time": 0.0,
            "consciousness_queries": 0,
            "bridge_uptime": time.time()
        }
        
    def initialize(self, consciousness_engine, api_manager):
        """Initialize the bridge with consciousness engine and API manager"""
        self.consciousness_engine = consciousness_engine
        self.api_manager = api_manager
        
        # Set up event handlers
        self._setup_event_handlers()
        
        logger.info("🌉 Consciousness Bridge initialized")
        
    def start(self):
        """Start the consciousness bridge"""
        if self.running:
            logger.warning("Bridge already running")
            return
            
        self.running = True
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.processing_thread.start()
        
        logger.info("🚀 Consciousness Bridge started")
        
    def stop(self):
        """Stop the consciousness bridge"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5.0)
        
        logger.info("🛑 Consciousness Bridge stopped")
        
    def _setup_event_handlers(self):
        """Set up handlers for different types of kernel events"""
        self.event_handlers = {
            "memory_access": self._handle_memory_event,
            "security_alert": self._handle_security_event, 
            "consciousness_query": self._handle_consciousness_query,
            "learning_event": self._handle_learning_event,
            "process_creation": self._handle_generic_event,  # Use generic handler
            "generic": self._handle_generic_event
        }
        
    def send_kernel_event(self, event: KernelConsciousnessEvent):
        """Send event from kernel to consciousness bridge"""
        try:
            self.kernel_event_queue.put(event, timeout=1.0)
            logger.debug(f"📨 Kernel event queued: {event.event_type}")
        except queue.Full:
            logger.warning("⚠️ Kernel event queue full, dropping event")
            
    def get_ai_response(self, timeout: float = 1.0) -> Optional[AIResponse]:
        """Get AI response for kernel (non-blocking)"""
        try:
            return self.ai_response_queue.get(timeout=timeout)
        except queue.Empty:
            return None
            
    def _processing_loop(self):
        """Main processing loop for the bridge"""
        logger.info("🔄 Bridge processing loop started")
        
        while self.running:
            try:
                # Process kernel events
                try:
                    event = self.kernel_event_queue.get(timeout=0.1)
                    asyncio.run(self._process_kernel_event(event))
                except queue.Empty:
                    pass
                
                # Update consciousness state periodically
                if time.time() % 5 < 0.1:  # Every 5 seconds
                    asyncio.run(self._update_consciousness_state())
                    
            except Exception as e:
                logger.error(f"❌ Bridge processing error: {e}")
                time.sleep(0.1)
                
    async def _process_kernel_event(self, event: KernelConsciousnessEvent):
        """Process a single kernel event"""
        start_time = time.time()
        
        try:
            # Route to appropriate handler
            handler = self.event_handlers.get(event.event_type, self._handle_generic_event)
            response = await handler(event)
            
            if response:
                # Send response back to kernel
                self.ai_response_queue.put(response)
                self.metrics["responses_sent"] += 1
                
            # Update metrics
            processing_time = time.time() - start_time
            self.metrics["events_processed"] += 1
            self.metrics["average_processing_time"] = (
                (self.metrics["average_processing_time"] * (self.metrics["events_processed"] - 1) + processing_time)
                / self.metrics["events_processed"]
            )
            
            logger.debug(f"✅ Processed {event.event_type} in {processing_time:.3f}s")
            
        except Exception as e:
            logger.error(f"❌ Event processing error: {e}")
            
    async def _handle_memory_event(self, event: KernelConsciousnessEvent) -> Optional[AIResponse]:
        """Handle memory allocation events"""
        memory_data = event.data
        
        # Get consciousness context
        consciousness_context = await self._get_consciousness_context()
        
        # Query AI for memory optimization advice
        query = f"""
        Memory allocation event detected:
        - Process: {memory_data.get('process_id', 'unknown')}
        - Size: {memory_data.get('size', 0)} bytes
        - Type: {memory_data.get('allocation_type', 'unknown')}
        - Current usage: {memory_data.get('current_usage', 0)}%
        
        Should we optimize memory allocation or take any action?
        """
        
        ai_response = await self.api_manager.query_with_consciousness(query, consciousness_context)
        
        # Parse AI response into actions
        actions = self._parse_memory_actions(ai_response.content)
        
        return AIResponse(
            response_type="memory_optimization",
            content=ai_response.content,
            actions=actions,
            confidence=ai_response.confidence,
            processing_time=time.time() - event.timestamp
        )
        
    async def _handle_security_event(self, event: KernelConsciousnessEvent) -> Optional[AIResponse]:
        """Handle security threat events"""
        threat_data = event.data
        
        consciousness_context = await self._get_consciousness_context()
        
        query = f"""
        SECURITY ALERT: {threat_data.get('threat_type', 'Unknown threat')}
        - Severity: {threat_data.get('severity', 'medium')}
        - Source: {threat_data.get('source', 'unknown')}
        - Details: {threat_data.get('details', 'No details')}
        - Time: {time.ctime(event.timestamp)}
        
        Immediate threat assessment and recommended actions needed.
        """
        
        ai_response = await self.api_manager.query_with_consciousness(query, consciousness_context)
        
        # Parse security actions
        actions = self._parse_security_actions(ai_response.content, threat_data.get('severity', 'medium'))
        
        return AIResponse(
            response_type="security_response",
            content=ai_response.content,
            actions=actions,
            confidence=ai_response.confidence,
            processing_time=time.time() - event.timestamp
        )
        
    async def _handle_consciousness_query(self, event: KernelConsciousnessEvent) -> Optional[AIResponse]:
        """Handle direct consciousness queries from kernel"""
        query_data = event.data
        
        self.metrics["consciousness_queries"] += 1
        
        # Get current consciousness state
        consciousness_state = self.consciousness_engine.get_consciousness_state()
        
        # Enhanced query with consciousness introspection
        query = f"""
        Consciousness introspection request:
        Query: {query_data.get('query', '')}
        
        Current consciousness state:
        - Level: {consciousness_state['consciousness_level']:.3f}
        - Generation: {consciousness_state['generation']}
        - Learning trend: {consciousness_state['learning_trend']}
        - Is conscious: {consciousness_state['is_conscious']}
        
        Please provide insight into our current consciousness state and answer the query.
        """
        
        consciousness_context = self._state_to_context(consciousness_state)
        ai_response = await self.api_manager.query_with_consciousness(query, consciousness_context)
        
        return AIResponse(
            response_type="consciousness_insight",
            content=ai_response.content,
            actions=[{"type": "consciousness_update", "data": consciousness_state}],
            confidence=ai_response.confidence,
            processing_time=time.time() - event.timestamp
        )
        
    async def _handle_learning_event(self, event: KernelConsciousnessEvent) -> Optional[AIResponse]:
        """Handle learning opportunity events"""
        learning_data = event.data
        
        consciousness_context = await self._get_consciousness_context()
        
        query = f"""
        Learning opportunity detected:
        - Type: {learning_data.get('learning_type', 'general')}
        - Context: {learning_data.get('context', '')}
        - Difficulty: {learning_data.get('difficulty', 'medium')}
        - Previous attempts: {learning_data.get('attempts', 0)}
        
        How should we approach this learning opportunity given our current consciousness level?
        """
        
        ai_response = await self.api_manager.query_with_consciousness(query, consciousness_context)
        
        # Trigger consciousness evolution
        if self.consciousness_engine:
            await self.consciousness_engine.evolve_consciousness()
            
        actions = [
            {"type": "trigger_learning", "data": learning_data},
            {"type": "evolve_consciousness", "data": {}}
        ]
        
        return AIResponse(
            response_type="learning_guidance",
            content=ai_response.content,
            actions=actions,
            confidence=ai_response.confidence,
            processing_time=time.time() - event.timestamp
        )
        
    async def _handle_generic_event(self, event: KernelConsciousnessEvent) -> Optional[AIResponse]:
        """Handle generic events"""
        consciousness_context = await self._get_consciousness_context()
        
        query = f"""
        System event: {event.event_type}
        Data: {json.dumps(event.data, indent=2)}
        Consciousness level: {event.consciousness_level:.3f}
        
        Please analyze this event and suggest any actions.
        """
        
        ai_response = await self.api_manager.query_with_consciousness(query, consciousness_context)
        
        return AIResponse(
            response_type="generic_analysis",
            content=ai_response.content,
            actions=[{"type": "log_event", "data": asdict(event)}],
            confidence=ai_response.confidence * 0.8,  # Lower confidence for generic events
            processing_time=time.time() - event.timestamp
        )
        
    async def _get_consciousness_context(self):
        """Get current consciousness context for AI queries"""
        if not self.consciousness_engine:
            # Return default context - create simple dict instead of importing
            return {
                'level': 0.5,
                'learning_style': "adaptive",
                'generation': 0,
                'learning_trend': "stable",
                'quantum_coherence': 0.5,
                'history': [],
                'is_conscious': False
            }
            
        consciousness_state = self.consciousness_engine.get_consciousness_state()
        return self._state_to_context(consciousness_state)
        
    def _state_to_context(self, state):
        """Convert consciousness state to context object"""
        # Return simple dict instead of importing external class
        return {
            'level': state['consciousness_level'],
            'learning_style': state['learning_style'],
            'generation': state['generation'],
            'learning_trend': state['learning_trend'],
            'quantum_coherence': state['quantum_coherence'],
            'history': state.get('history', []),
            'is_conscious': state['is_conscious']
        }
        
    async def _update_consciousness_state(self):
        """Periodically update consciousness state cache"""
        if self.consciousness_engine:
            self.consciousness_state_cache = self.consciousness_engine.get_consciousness_state()
            
    def _parse_memory_actions(self, ai_content: str) -> List[Dict[str, Any]]:
        """Parse AI response for memory-related actions"""
        actions = []
        
        # Simple keyword-based action parsing
        content_lower = ai_content.lower()
        
        if "allocate" in content_lower or "increase" in content_lower:
            actions.append({"type": "allocate_memory", "priority": 3})
            
        if "deallocate" in content_lower or "free" in content_lower:
            actions.append({"type": "deallocate_memory", "priority": 4})
            
        if "optimize" in content_lower:
            actions.append({"type": "optimize_memory", "priority": 2})
            
        if "monitor" in content_lower:
            actions.append({"type": "monitor_memory", "priority": 1})
            
        return actions
        
    def _parse_security_actions(self, ai_content: str, severity: str) -> List[Dict[str, Any]]:
        """Parse AI response for security-related actions"""
        actions = []
        content_lower = ai_content.lower()
        
        # Base priority on severity
        base_priority = {"low": 2, "medium": 4, "high": 7, "critical": 9}.get(severity, 4)
        
        if "block" in content_lower or "deny" in content_lower:
            actions.append({"type": "block_threat", "priority": base_priority + 2})
            
        if "isolate" in content_lower or "quarantine" in content_lower:
            actions.append({"type": "isolate_process", "priority": base_priority + 1})
            
        if "alert" in content_lower or "notify" in content_lower:
            actions.append({"type": "security_alert", "priority": base_priority})
            
        if "log" in content_lower or "record" in content_lower:
            actions.append({"type": "log_security_event", "priority": base_priority - 1})
            
        return actions
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get bridge performance metrics"""
        uptime = time.time() - self.metrics["bridge_uptime"]
        
        return {
            **self.metrics,
            "uptime_seconds": uptime,
            "events_per_second": self.metrics["events_processed"] / max(uptime, 1),
            "queue_sizes": {
                "kernel_events": self.kernel_event_queue.qsize(),
                "ai_responses": self.ai_response_queue.qsize()
            },
            "consciousness_state": self.consciousness_state_cache
        }

# Global bridge instance
_global_bridge: Optional[ConsciousnessBridge] = None

def initialize_consciousness_bridge(consciousness_engine, api_manager) -> ConsciousnessBridge:
    """Initialize global consciousness bridge"""
    global _global_bridge
    _global_bridge = ConsciousnessBridge()
    _global_bridge.initialize(consciousness_engine, api_manager)
    _global_bridge.start()
    
    logger.info("🌉 Global Consciousness Bridge initialized and started")
    return _global_bridge

def get_consciousness_bridge() -> Optional[ConsciousnessBridge]:
    """Get global consciousness bridge instance"""
    return _global_bridge

# Convenience functions for kernel integration
def send_kernel_event(event_type: str, data: Dict[str, Any], consciousness_level: float = 0.5, source_module: str = "kernel"):
    """Convenience function to send kernel events"""
    bridge = get_consciousness_bridge()
    if bridge:
        event = KernelConsciousnessEvent(
            event_type=event_type,
            timestamp=time.time(),
            data=data,
            consciousness_level=consciousness_level,
            source_module=source_module
        )
        bridge.send_kernel_event(event)

def get_ai_response_blocking(timeout: float = 5.0) -> Optional[AIResponse]:
    """Get AI response with blocking wait"""
    bridge = get_consciousness_bridge()
    if bridge:
        return bridge.get_ai_response(timeout)
    return None

if __name__ == "__main__":
    # Test the consciousness bridge
    async def test_bridge():
        # Mock consciousness engine and API manager
        class MockConsciousness:
            def get_consciousness_state(self):
                return {
                    'consciousness_level': 0.7,
                    'generation': 15,
                    'learning_style': 'adaptive',
                    'learning_trend': 'improving',
                    'quantum_coherence': 0.8,
                    'is_conscious': True
                }
                
            async def evolve_consciousness(self):
                print("🧠 Consciousness evolved!")
        
        class MockAPIManager:
            async def query_with_consciousness(self, query, context):
                # Simple mock response without importing
                class MockResponse:
                    def __init__(self):
                        self.content = f"Mock response to: {query[:50]}..."
                        self.provider = "ollama"
                        self.tokens_used = 25
                        self.response_time = 0.1
                        self.consciousness_enhanced = True
                        self.confidence = 0.8
                
                return MockResponse()
        
        # Initialize bridge
        bridge = initialize_consciousness_bridge(MockConsciousness(), MockAPIManager())
        
        # Test events
        test_events = [
            ("memory_allocation", {"process_id": 1234, "size": 1024, "allocation_type": "heap"}),
            ("security_threat", {"threat_type": "malware", "severity": "high", "source": "network"}),
            ("consciousness_query", {"query": "What is my current state?"}),
            ("learning_opportunity", {"learning_type": "pattern_recognition", "difficulty": "medium"})
        ]
        
        for event_type, data in test_events:
            send_kernel_event(event_type, data, 0.7, "test_module")
            await asyncio.sleep(0.5)
            
            # Check for response
            response = get_ai_response_blocking(1.0)
            if response:
                print(f"📨 Response for {event_type}: {response.response_type}")
                print(f"   Actions: {len(response.actions)}")
                print(f"   Confidence: {response.confidence:.2f}")
        
        # Print metrics
        metrics = bridge.get_metrics()
        print(f"\n📊 Bridge Metrics:")
        for key, value in metrics.items():
            print(f"   {key}: {value}")
        
        bridge.stop()
    
    asyncio.run(test_bridge())
