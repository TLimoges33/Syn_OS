#!/usr/bin/env python3
"""
SynOS NATS Message Bus Integration
High-performance messaging for AI service communication

Implements:
- Consciousness state broadcasting
- Neural activity streaming
- Security event distribution
- Learning event propagation
- System-wide AI coordination
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Callable, Optional, List
from dataclasses import asdict
from datetime import datetime

try:
    import nats
    from nats.errors import ConnectionClosedError, TimeoutError
except ImportError:
    # Fallback for environments without nats-py
    nats = None
    ConnectionClosedError = Exception
    TimeoutError = Exception

logger = logging.getLogger(__name__)

class SynOSNATSClient:
    """High-performance NATS client for SynOS AI services"""

    def __init__(self, servers: List[str] = None):
        self.servers = servers or ["nats://localhost:4222"]
        self.nc = None
        self.connected = False
        self.subscriptions = {}
        self.reconnect_count = 0
        self.max_reconnects = 10

        # Message subjects for different AI services
        self.subjects = {
            'consciousness_state': 'synos.consciousness.state',
            'neural_activity': 'synos.neural.activity',
            'learning_events': 'synos.learning.events',
            'security_events': 'synos.security.events',
            'system_metrics': 'synos.system.metrics',
            'ai_commands': 'synos.ai.commands',
            'model_updates': 'synos.models.updates',
            'inference_requests': 'synos.inference.requests',
            'adaptation_signals': 'synos.adaptation.signals'
        }

    async def connect(self) -> bool:
        """Connect to NATS server with resilience"""
        if not nats:
            logger.error("NATS library not available - install nats-py")
            return False

        try:
            self.nc = await nats.connect(
                servers=self.servers,
                reconnected_cb=self._reconnected_cb,
                disconnected_cb=self._disconnected_cb,
                error_cb=self._error_cb,
                closed_cb=self._closed_cb,
                name="synos-ai-client",
                max_reconnect_attempts=self.max_reconnects,
                reconnect_time_wait=2,  # 2 second wait between reconnects
            )

            self.connected = True
            logger.info(f"Connected to NATS server: {self.nc.connected_url}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Disconnect from NATS server gracefully"""
        if self.nc and self.connected:
            try:
                await self.nc.close()
                logger.info("Disconnected from NATS server")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")

        self.connected = False

    async def publish_consciousness_state(self, state: Dict[str, Any]) -> bool:
        """Publish consciousness state to the network"""
        return await self._publish_json(
            self.subjects['consciousness_state'],
            {
                'timestamp': datetime.now().isoformat(),
                'state': state,
                'node_id': 'main-consciousness'
            }
        )

    async def publish_neural_activity(self, activity_data: Dict[str, Any]) -> bool:
        """Publish neural activity metrics"""
        return await self._publish_json(
            self.subjects['neural_activity'],
            {
                'timestamp': datetime.now().isoformat(),
                'activity': activity_data,
                'source': 'neural-darwinism-engine'
            }
        )

    async def publish_learning_event(self, learning_data: Dict[str, Any]) -> bool:
        """Publish learning events for system-wide awareness"""
        return await self._publish_json(
            self.subjects['learning_events'],
            {
                'timestamp': datetime.now().isoformat(),
                'event': learning_data,
                'source': 'adaptive-learning-engine'
            }
        )

    async def publish_security_event(self, security_data: Dict[str, Any]) -> bool:
        """Publish security events for AI security orchestration"""
        return await self._publish_json(
            self.subjects['security_events'],
            {
                'timestamp': datetime.now().isoformat(),
                'event': security_data,
                'severity': security_data.get('severity', 'info'),
                'source': 'security-orchestrator'
            }
        )

    async def publish_system_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Publish system metrics for AI awareness"""
        return await self._publish_json(
            self.subjects['system_metrics'],
            {
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics,
                'node': 'localhost'
            }
        )

    async def request_inference(self, model_id: str, input_data: Any, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        """Request AI model inference via NATS"""
        if not self.connected:
            return None

        request_data = {
            'model_id': model_id,
            'input': input_data,
            'timestamp': datetime.now().isoformat(),
            'requester': 'consciousness-framework'
        }

        try:
            response = await self.nc.request(
                self.subjects['inference_requests'],
                json.dumps(request_data).encode(),
                timeout=timeout
            )

            return json.loads(response.data.decode())

        except TimeoutError:
            logger.warning(f"Inference request timeout for model {model_id}")
            return None
        except Exception as e:
            logger.error(f"Inference request failed: {e}")
            return None

    async def subscribe_to_consciousness_updates(self, callback: Callable) -> str:
        """Subscribe to consciousness state updates from other nodes"""
        return await self._subscribe_json(
            self.subjects['consciousness_state'],
            callback,
            queue="consciousness-subscribers"
        )

    async def subscribe_to_security_events(self, callback: Callable) -> str:
        """Subscribe to security events for AI response coordination"""
        return await self._subscribe_json(
            self.subjects['security_events'],
            callback,
            queue="security-ai-responders"
        )

    async def subscribe_to_model_updates(self, callback: Callable) -> str:
        """Subscribe to AI model updates and reloading signals"""
        return await self._subscribe_json(
            self.subjects['model_updates'],
            callback,
            queue="model-update-subscribers"
        )

    async def send_adaptation_signal(self, signal_type: str, data: Dict[str, Any]) -> bool:
        """Send adaptation signal to AI components"""
        signal_data = {
            'signal_type': signal_type,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'sender': 'consciousness-coordinator'
        }

        return await self._publish_json(
            self.subjects['adaptation_signals'],
            signal_data
        )

    async def _publish_json(self, subject: str, data: Dict[str, Any]) -> bool:
        """Publish JSON data to NATS subject"""
        if not self.connected or not self.nc:
            logger.warning(f"Cannot publish to {subject}: not connected to NATS")
            return False

        try:
            await self.nc.publish(
                subject,
                json.dumps(data, default=str).encode()
            )
            logger.debug(f"Published to {subject}: {len(json.dumps(data))} bytes")
            return True

        except Exception as e:
            logger.error(f"Failed to publish to {subject}: {e}")
            return False

    async def _subscribe_json(self, subject: str, callback: Callable, queue: str = None) -> str:
        """Subscribe to JSON messages on NATS subject"""
        if not self.connected or not self.nc:
            logger.error(f"Cannot subscribe to {subject}: not connected to NATS")
            return ""

        async def message_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                await callback(data)
            except Exception as e:
                logger.error(f"Error processing message from {subject}: {e}")

        try:
            if queue:
                sub = await self.nc.subscribe(subject, queue=queue, cb=message_handler)
            else:
                sub = await self.nc.subscribe(subject, cb=message_handler)

            sub_id = str(sub.sid)
            self.subscriptions[sub_id] = sub
            logger.info(f"Subscribed to {subject} (queue: {queue}) with ID {sub_id}")
            return sub_id

        except Exception as e:
            logger.error(f"Failed to subscribe to {subject}: {e}")
            return ""

    async def unsubscribe(self, subscription_id: str):
        """Unsubscribe from a NATS subscription"""
        if subscription_id in self.subscriptions:
            try:
                await self.subscriptions[subscription_id].unsubscribe()
                del self.subscriptions[subscription_id]
                logger.info(f"Unsubscribed from subscription {subscription_id}")
            except Exception as e:
                logger.error(f"Failed to unsubscribe {subscription_id}: {e}")

    # Connection event callbacks
    async def _reconnected_cb(self):
        """Handle NATS reconnection"""
        self.reconnect_count += 1
        logger.info(f"Reconnected to NATS server (count: {self.reconnect_count})")
        self.connected = True

    async def _disconnected_cb(self):
        """Handle NATS disconnection"""
        logger.warning("Disconnected from NATS server")
        self.connected = False

    async def _error_cb(self, e):
        """Handle NATS errors"""
        logger.error(f"NATS error: {e}")

    async def _closed_cb(self):
        """Handle NATS connection closure"""
        logger.info("NATS connection closed")
        self.connected = False

class ConsciousnessMessageBus:
    """High-level interface for consciousness framework messaging"""

    def __init__(self, nats_servers: List[str] = None):
        self.client = SynOSNATSClient(nats_servers)
        self.message_handlers = {}
        self.running = False

    async def start(self) -> bool:
        """Start the message bus"""
        if await self.client.connect():
            self.running = True
            logger.info("Consciousness message bus started")
            return True
        return False

    async def stop(self):
        """Stop the message bus"""
        self.running = False
        await self.client.disconnect()
        logger.info("Consciousness message bus stopped")

    async def broadcast_consciousness_state(self, awareness_level: float,
                                          neural_activity: float,
                                          active_patterns: List[str],
                                          metadata: Dict[str, Any] = None):
        """Broadcast consciousness state to all AI components"""
        state_data = {
            'awareness_level': awareness_level,
            'neural_activity': neural_activity,
            'active_patterns': active_patterns,
            'metadata': metadata or {}
        }

        return await self.client.publish_consciousness_state(state_data)

    async def coordinate_ai_response(self, trigger_event: str,
                                   context: Dict[str, Any],
                                   response_type: str = "adaptive"):
        """Coordinate AI response across all components"""
        coordination_data = {
            'trigger': trigger_event,
            'context': context,
            'response_type': response_type,
            'coordination_id': f"coord_{int(time.time() * 1000)}"
        }

        return await self.client.send_adaptation_signal("coordinate_response", coordination_data)

    async def register_consciousness_observer(self, callback: Callable):
        """Register to observe consciousness state changes"""
        return await self.client.subscribe_to_consciousness_updates(callback)

    async def register_security_responder(self, callback: Callable):
        """Register as AI security event responder"""
        return await self.client.subscribe_to_security_events(callback)

# Example usage and testing functions
async def test_message_bus():
    """Test the NATS message bus functionality"""
    print("Testing SynOS NATS Message Bus...")

    bus = ConsciousnessMessageBus()

    # Test connection
    if not await bus.start():
        print("Failed to connect to NATS server")
        return

    # Test consciousness state broadcast
    await bus.broadcast_consciousness_state(
        awareness_level=0.85,
        neural_activity=0.72,
        active_patterns=['security_analysis', 'learning_adaptation'],
        metadata={'test_mode': True}
    )

    # Test coordination signal
    await bus.coordinate_ai_response(
        trigger_event='high_system_load',
        context={'cpu_usage': 0.92, 'memory_usage': 0.78},
        response_type='performance_optimization'
    )

    print("Message bus test completed")
    await bus.stop()

if __name__ == "__main__":
    # Run test if executed directly
    asyncio.run(test_message_bus())