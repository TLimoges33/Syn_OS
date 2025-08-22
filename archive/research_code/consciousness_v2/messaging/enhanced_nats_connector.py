"""
Advanced NATS JetStream Integration with Enhanced Messaging
Priority 4: NATS Message Bus Enhancement

Enhanced messaging system with:
- JetStream persistence and replay
- Performance monitoring and alerting
- Schema validation and error handling
- High-availability clustering
- Advanced pub/sub patterns
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
import uuid

# NATS imports
import nats
from nats.js import JetStreamContext
from nats.js.api import StreamConfig, ConsumerConfig, DeliverPolicy, AckPolicy
from nats.js.errors import KeyValueStoreError

# Monitoring imports
import psutil
import asyncio
from concurrent.futures import ThreadPoolExecutor


class MessagePriority(Enum):
    """Message priority levels for enhanced routing"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class MessageType(Enum):
    """Enhanced message types for consciousness system"""
    CONSCIOUSNESS_EVENT = "consciousness.event"
    SECURITY_ALERT = "security.alert"
    PERFORMANCE_METRIC = "performance.metric"
    SYSTEM_STATUS = "system.status"
    AI_DECISION = "ai.decision"
    NEURAL_UPDATE = "neural.update"
    BEHAVIORAL_ANOMALY = "behavioral.anomaly"
    ORCHESTRATOR_COMMAND = "orchestrator.command"


@dataclass
class MessageMetadata:
    """Enhanced message metadata for tracking and routing"""
    message_id: str
    timestamp: datetime
    sender_service: str
    recipient_service: Optional[str]
    priority: MessagePriority
    message_type: MessageType
    correlation_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    ttl_seconds: int = 300
    schema_version: str = "1.0"


@dataclass
class ConsciousnessMessage:
    """Enhanced consciousness message format"""
    metadata: MessageMetadata
    payload: Dict[str, Any]
    signature: Optional[str] = None  # For message integrity
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for transmission"""
        return {
            'metadata': asdict(self.metadata),
            'payload': self.payload,
            'signature': self.signature
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConsciousnessMessage':
        """Create message from dictionary"""
        metadata_dict = data['metadata']
        metadata_dict['timestamp'] = datetime.fromisoformat(metadata_dict['timestamp'])
        metadata_dict['priority'] = MessagePriority(metadata_dict['priority'])
        metadata_dict['message_type'] = MessageType(metadata_dict['message_type'])
        
        return cls(
            metadata=MessageMetadata(**metadata_dict),
            payload=data['payload'],
            signature=data.get('signature')
        )


class MessageValidator:
    """Schema validation for consciousness messages"""
    
    def __init__(self):
        self.schemas = {
            MessageType.CONSCIOUSNESS_EVENT: {
                'required_fields': ['event_type', 'consciousness_level', 'context'],
                'optional_fields': ['neural_state', 'decision_confidence']
            },
            MessageType.SECURITY_ALERT: {
                'required_fields': ['alert_level', 'threat_type', 'source_ip'],
                'optional_fields': ['user_id', 'action_taken', 'additional_context']
            },
            MessageType.PERFORMANCE_METRIC: {
                'required_fields': ['metric_name', 'value', 'unit'],
                'optional_fields': ['threshold', 'status', 'trend']
            },
            MessageType.AI_DECISION: {
                'required_fields': ['decision_id', 'decision_type', 'confidence'],
                'optional_fields': ['reasoning', 'alternatives', 'impact_assessment']
            }
        }
    
    def validate_message(self, message: ConsciousnessMessage) -> bool:
        """Validate message against schema"""
        try:
            message_type = message.metadata.message_type
            schema = self.schemas.get(message_type)
            
            if not schema:
                logging.warning(f"No schema found for message type: {message_type}")
                return True  # Allow unknown message types
            
            # Check required fields
            for field in schema['required_fields']:
                if field not in message.payload:
                    logging.error(f"Missing required field '{field}' in {message_type} message")
                    return False
            
            return True
            
        except Exception as e:
            logging.error(f"Message validation error: {e}")
            return False


class NATSPerformanceMonitor:
    """Performance monitoring for NATS operations"""
    
    def __init__(self):
        self.metrics = {
            'messages_sent': 0,
            'messages_received': 0,
            'messages_failed': 0,
            'avg_latency_ms': 0.0,
            'connection_count': 0,
            'jetstream_operations': 0
        }
        self.latency_samples = []
        self.max_samples = 1000
    
    def record_message_sent(self, latency_ms: float = 0.0):
        """Record successful message send"""
        self.metrics['messages_sent'] += 1
        if latency_ms > 0:
            self._record_latency(latency_ms)
    
    def record_message_received(self):
        """Record message received"""
        self.metrics['messages_received'] += 1
    
    def record_message_failed(self):
        """Record failed message"""
        self.metrics['messages_failed'] += 1
    
    def record_jetstream_operation(self):
        """Record JetStream operation"""
        self.metrics['jetstream_operations'] += 1
    
    def _record_latency(self, latency_ms: float):
        """Record latency sample"""
        self.latency_samples.append(latency_ms)
        if len(self.latency_samples) > self.max_samples:
            self.latency_samples.pop(0)
        
        # Update average
        if self.latency_samples:
            self.metrics['avg_latency_ms'] = sum(self.latency_samples) / len(self.latency_samples)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        return {
            'metrics': self.metrics.copy(),
            'system_resources': self._get_system_resources(),
            'health_status': self._assess_health(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_system_resources(self) -> Dict[str, float]:
        """Get current system resource usage"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent if hasattr(psutil, 'disk_usage') else 0.0
        }
    
    def _assess_health(self) -> str:
        """Assess overall system health"""
        failure_rate = self.metrics['messages_failed'] / max(1, self.metrics['messages_sent'])
        avg_latency = self.metrics['avg_latency_ms']
        
        if failure_rate > 0.1 or avg_latency > 1000:
            return "CRITICAL"
        elif failure_rate > 0.05 or avg_latency > 500:
            return "WARNING"
        else:
            return "HEALTHY"


class EnhancedNATSConnector:
    """Enhanced NATS connector with JetStream and advanced features"""
    
    def __init__(self, nats_url: str = "nats://localhost:4222"):
        self.nats_url = nats_url
        self.nc: Optional[nats.NATS] = None
        self.js: Optional[JetStreamContext] = None
        self.validator = MessageValidator()
        self.monitor = NATSPerformanceMonitor()
        self.message_handlers: Dict[str, Callable] = {}
        self.streams_created = set()
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Configuration
        self.stream_config = {
            'consciousness': StreamConfig(
                name="CONSCIOUSNESS",
                subjects=["consciousness.>"],
                max_msgs=10000,
                max_age=86400,  # 24 hours
                storage="file"
            ),
            'security': StreamConfig(
                name="SECURITY",
                subjects=["security.>"],
                max_msgs=50000,
                max_age=604800,  # 7 days
                storage="file"
            ),
            'performance': StreamConfig(
                name="PERFORMANCE",
                subjects=["performance.>"],
                max_msgs=100000,
                max_age=259200,  # 3 days
                storage="memory"
            )
        }
    
    async def connect(self) -> bool:
        """Enhanced connection with retry logic"""
        max_retries = 5
        retry_delay = 2.0
        
        for attempt in range(max_retries):
            try:
                logging.info(f"Connecting to NATS server: {self.nats_url} (attempt {attempt + 1})")
                
                # Enhanced connection options
                self.nc = await nats.connect(
                    self.nats_url,
                    max_reconnect_attempts=10,
                    reconnect_time_wait=2.0,
                    ping_interval=30,
                    max_outstanding_pings=3,
                    error_cb=self._error_callback,
                    disconnected_cb=self._disconnected_callback,
                    reconnected_cb=self._reconnected_callback
                )
                
                # Initialize JetStream
                self.js = self.nc.jetstream()
                
                # Create required streams
                await self._setup_streams()
                
                self.monitor.metrics['connection_count'] = 1
                logging.info("Successfully connected to NATS with JetStream")
                return True
                
            except Exception as e:
                logging.error(f"NATS connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logging.error("All NATS connection attempts failed")
                    return False
        
        return False
    
    async def _setup_streams(self):
        """Setup JetStream streams"""
        try:
            for stream_name, config in self.stream_config.items():
                try:
                    await self.js.add_stream(config)
                    self.streams_created.add(stream_name)
                    logging.info(f"Created JetStream stream: {config.name}")
                except Exception as e:
                    # Stream might already exist
                    if "already exists" in str(e).lower():
                        self.streams_created.add(stream_name)
                        logging.info(f"JetStream stream already exists: {config.name}")
                    else:
                        logging.error(f"Failed to create stream {config.name}: {e}")
                        
        except Exception as e:
            logging.error(f"Failed to setup JetStream streams: {e}")
    
    async def publish_message(
        self, 
        subject: str, 
        message: ConsciousnessMessage,
        use_jetstream: bool = True
    ) -> bool:
        """Enhanced message publishing with validation and monitoring"""
        start_time = time.time()
        
        try:
            # Validate message
            if not self.validator.validate_message(message):
                self.monitor.record_message_failed()
                return False
            
            # Serialize message
            message_data = json.dumps(message.to_dict()).encode()
            
            if use_jetstream and self.js:
                # Use JetStream for persistence
                await self.js.publish(subject, message_data)
                self.monitor.record_jetstream_operation()
            else:
                # Use core NATS for simple pub/sub
                await self.nc.publish(subject, message_data)
            
            # Record performance
            latency_ms = (time.time() - start_time) * 1000
            self.monitor.record_message_sent(latency_ms)
            
            logging.debug(f"Published message to {subject}: {message.metadata.message_id}")
            return True
            
        except Exception as e:
            self.monitor.record_message_failed()
            logging.error(f"Failed to publish message to {subject}: {e}")
            return False
    
    async def subscribe_to_subject(
        self, 
        subject: str, 
        handler: Callable,
        use_jetstream: bool = True,
        durable_name: Optional[str] = None
    ):
        """Enhanced subscription with JetStream consumers"""
        try:
            if use_jetstream and self.js:
                # Create JetStream consumer
                consumer_config = ConsumerConfig(
                    durable_name=durable_name or f"consumer_{subject.replace('.', '_')}_{int(time.time())}",
                    deliver_policy=DeliverPolicy.ALL,
                    ack_policy=AckPolicy.EXPLICIT,
                    max_deliver=3,
                    ack_wait=30.0
                )
                
                # Subscribe with consumer
                subscription = await self.js.subscribe(
                    subject,
                    config=consumer_config,
                    cb=self._create_jetstream_handler(handler)
                )
            else:
                # Use core NATS subscription
                subscription = await self.nc.subscribe(
                    subject,
                    cb=self._create_core_handler(handler)
                )
            
            self.message_handlers[subject] = handler
            logging.info(f"Subscribed to subject: {subject}")
            return subscription
            
        except Exception as e:
            logging.error(f"Failed to subscribe to {subject}: {e}")
            return None
    
    def _create_jetstream_handler(self, handler: Callable):
        """Create JetStream message handler with ack"""
        async def jetstream_handler(msg):
            try:
                # Decode message
                message_data = json.loads(msg.data.decode())
                consciousness_msg = ConsciousnessMessage.from_dict(message_data)
                
                # Process message
                await handler(consciousness_msg)
                
                # Acknowledge message
                await msg.ack()
                
                self.monitor.record_message_received()
                
            except Exception as e:
                logging.error(f"Error processing JetStream message: {e}")
                # Negative acknowledge to trigger redelivery
                await msg.nak()
        
        return jetstream_handler
    
    def _create_core_handler(self, handler: Callable):
        """Create core NATS message handler"""
        async def core_handler(msg):
            try:
                # Decode message
                message_data = json.loads(msg.data.decode())
                consciousness_msg = ConsciousnessMessage.from_dict(message_data)
                
                # Process message
                await handler(consciousness_msg)
                
                self.monitor.record_message_received()
                
            except Exception as e:
                logging.error(f"Error processing core NATS message: {e}")
        
        return core_handler
    
    async def get_stream_info(self, stream_name: str) -> Optional[Dict[str, Any]]:
        """Get JetStream stream information"""
        try:
            if not self.js:
                return None
                
            stream_info = await self.js.stream_info(stream_name)
            return {
                'name': stream_info.config.name,
                'subjects': stream_info.config.subjects,
                'messages': stream_info.state.messages,
                'bytes': stream_info.state.bytes,
                'first_seq': stream_info.state.first_seq,
                'last_seq': stream_info.state.last_seq,
                'consumer_count': stream_info.state.consumer_count
            }
            
        except Exception as e:
            logging.error(f"Failed to get stream info for {stream_name}: {e}")
            return None
    
    async def replay_messages(
        self, 
        stream_name: str, 
        start_seq: int = 1,
        handler: Optional[Callable] = None
    ) -> List[ConsciousnessMessage]:
        """Replay messages from JetStream"""
        try:
            if not self.js:
                logging.error("JetStream not available for replay")
                return []
            
            messages = []
            
            # Create ephemeral consumer for replay
            consumer_config = ConsumerConfig(
                deliver_policy=DeliverPolicy.BY_START_SEQUENCE,
                opt_start_seq=start_seq,
                ack_policy=AckPolicy.EXPLICIT
            )
            
            # Get messages
            subscription = await self.js.subscribe(
                f"{stream_name.lower()}.>",
                config=consumer_config
            )
            
            # Process up to 1000 messages for safety
            for _ in range(1000):
                try:
                    msg = await subscription.next_msg(timeout=1.0)
                    message_data = json.loads(msg.data.decode())
                    consciousness_msg = ConsciousnessMessage.from_dict(message_data)
                    
                    messages.append(consciousness_msg)
                    
                    if handler:
                        await handler(consciousness_msg)
                    
                    await msg.ack()
                    
                except asyncio.TimeoutError:
                    break  # No more messages
                except Exception as e:
                    logging.error(f"Error during message replay: {e}")
                    break
            
            await subscription.unsubscribe()
            
            logging.info(f"Replayed {len(messages)} messages from {stream_name}")
            return messages
            
        except Exception as e:
            logging.error(f"Failed to replay messages from {stream_name}: {e}")
            return []
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        metrics = self.monitor.get_performance_report()
        
        # Add NATS-specific metrics
        if self.nc:
            stats = self.nc.stats
            metrics['nats_stats'] = {
                'in_msgs': stats['in_msgs'],
                'out_msgs': stats['out_msgs'],
                'in_bytes': stats['in_bytes'],
                'out_bytes': stats['out_bytes'],
                'reconnects': stats['reconnects']
            }
        
        # Add JetStream metrics
        if self.js:
            stream_metrics = {}
            for stream_name in self.streams_created:
                stream_info = await self.get_stream_info(stream_name.upper())
                if stream_info:
                    stream_metrics[stream_name] = stream_info
            metrics['jetstream_streams'] = stream_metrics
        
        return metrics
    
    async def _error_callback(self, error):
        """Handle NATS errors"""
        logging.error(f"NATS error: {error}")
        self.monitor.record_message_failed()
    
    async def _disconnected_callback(self):
        """Handle NATS disconnection"""
        logging.warning("NATS disconnected")
        self.monitor.metrics['connection_count'] = 0
    
    async def _reconnected_callback(self):
        """Handle NATS reconnection"""
        logging.info("NATS reconnected")
        self.monitor.metrics['connection_count'] = 1
    
    async def disconnect(self):
        """Graceful disconnection"""
        try:
            if self.nc:
                await self.nc.drain()
                await self.nc.close()
                self.monitor.metrics['connection_count'] = 0
                logging.info("NATS connection closed")
        except Exception as e:
            logging.error(f"Error during NATS disconnection: {e}")


class ConsciousnessMessageBus:
    """High-level consciousness message bus using enhanced NATS"""
    
    def __init__(self, nats_url: str = "nats://localhost:4222"):
        self.connector = EnhancedNATSConnector(nats_url)
        self.running = False
        self.health_check_task = None
        
        # Message routing configuration
        self.routing_rules = {
            MessageType.CONSCIOUSNESS_EVENT: "consciousness.events",
            MessageType.SECURITY_ALERT: "security.alerts",
            MessageType.PERFORMANCE_METRIC: "performance.metrics",
            MessageType.SYSTEM_STATUS: "system.status",
            MessageType.AI_DECISION: "consciousness.decisions",
            MessageType.NEURAL_UPDATE: "consciousness.neural",
            MessageType.BEHAVIORAL_ANOMALY: "security.behavioral",
            MessageType.ORCHESTRATOR_COMMAND: "orchestrator.commands"
        }
    
    async def start(self) -> bool:
        """Start the message bus"""
        try:
            # Connect to NATS
            if not await self.connector.connect():
                return False
            
            # Setup default subscriptions
            await self._setup_default_subscriptions()
            
            # Start health monitoring
            self.running = True
            self.health_check_task = asyncio.create_task(self._health_monitor())
            
            logging.info("Consciousness message bus started")
            return True
            
        except Exception as e:
            logging.error(f"Failed to start message bus: {e}")
            return False
    
    async def _setup_default_subscriptions(self):
        """Setup default message subscriptions"""
        # Subscribe to consciousness events
        await self.connector.subscribe_to_subject(
            "consciousness.>",
            self._handle_consciousness_message,
            durable_name="consciousness_handler"
        )
        
        # Subscribe to security alerts
        await self.connector.subscribe_to_subject(
            "security.>",
            self._handle_security_message,
            durable_name="security_handler"
        )
        
        # Subscribe to performance metrics
        await self.connector.subscribe_to_subject(
            "performance.>",
            self._handle_performance_message,
            durable_name="performance_handler"
        )
    
    async def publish_consciousness_event(
        self,
        event_type: str,
        consciousness_level: float,
        context: Dict[str, Any],
        sender_service: str = "consciousness_v2",
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> bool:
        """Publish consciousness event"""
        
        message = ConsciousnessMessage(
            metadata=MessageMetadata(
                message_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                sender_service=sender_service,
                recipient_service=None,
                priority=priority,
                message_type=MessageType.CONSCIOUSNESS_EVENT,
                correlation_id=context.get('correlation_id')
            ),
            payload={
                'event_type': event_type,
                'consciousness_level': consciousness_level,
                'context': context,
                'neural_state': context.get('neural_state', {}),
                'decision_confidence': context.get('decision_confidence', 0.0)
            }
        )
        
        subject = self.routing_rules[MessageType.CONSCIOUSNESS_EVENT]
        return await self.connector.publish_message(subject, message)
    
    async def publish_security_alert(
        self,
        alert_level: str,
        threat_type: str,
        source_ip: str,
        context: Dict[str, Any],
        sender_service: str = "zero_trust",
        priority: MessagePriority = MessagePriority.HIGH
    ) -> bool:
        """Publish security alert"""
        
        message = ConsciousnessMessage(
            metadata=MessageMetadata(
                message_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                sender_service=sender_service,
                recipient_service=None,
                priority=priority,
                message_type=MessageType.SECURITY_ALERT
            ),
            payload={
                'alert_level': alert_level,
                'threat_type': threat_type,
                'source_ip': source_ip,
                'user_id': context.get('user_id'),
                'action_taken': context.get('action_taken'),
                'additional_context': context
            }
        )
        
        subject = self.routing_rules[MessageType.SECURITY_ALERT]
        return await self.connector.publish_message(subject, message)
    
    async def publish_ai_decision(
        self,
        decision_id: str,
        decision_type: str,
        confidence: float,
        reasoning: str,
        alternatives: List[str] = None,
        sender_service: str = "ai_consciousness",
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> bool:
        """Publish AI decision"""
        
        message = ConsciousnessMessage(
            metadata=MessageMetadata(
                message_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                sender_service=sender_service,
                recipient_service=None,
                priority=priority,
                message_type=MessageType.AI_DECISION,
                correlation_id=decision_id
            ),
            payload={
                'decision_id': decision_id,
                'decision_type': decision_type,
                'confidence': confidence,
                'reasoning': reasoning,
                'alternatives': alternatives or [],
                'impact_assessment': {
                    'risk_level': 'medium',
                    'expected_outcome': 'positive'
                }
            }
        )
        
        subject = self.routing_rules[MessageType.AI_DECISION]
        return await self.connector.publish_message(subject, message)
    
    async def _handle_consciousness_message(self, message: ConsciousnessMessage):
        """Handle consciousness messages"""
        logging.info(f"Received consciousness message: {message.metadata.message_id}")
        # Add consciousness-specific processing here
    
    async def _handle_security_message(self, message: ConsciousnessMessage):
        """Handle security messages"""
        logging.info(f"Received security message: {message.metadata.message_id}")
        # Add security-specific processing here
    
    async def _handle_performance_message(self, message: ConsciousnessMessage):
        """Handle performance messages"""
        logging.info(f"Received performance message: {message.metadata.message_id}")
        # Add performance-specific processing here
    
    async def _health_monitor(self):
        """Monitor message bus health"""
        while self.running:
            try:
                # Get performance metrics
                metrics = await self.connector.get_performance_metrics()
                
                # Assess health
                health_status = metrics.get('health_status', 'UNKNOWN')
                
                if health_status == 'CRITICAL':
                    logging.error("Message bus health is CRITICAL")
                    # Could trigger alerts here
                elif health_status == 'WARNING':
                    logging.warning("Message bus health is WARNING")
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logging.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get message bus metrics"""
        return await self.connector.get_performance_metrics()
    
    async def stop(self):
        """Stop the message bus"""
        try:
            self.running = False
            
            if self.health_check_task:
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass
            
            await self.connector.disconnect()
            logging.info("Consciousness message bus stopped")
            
        except Exception as e:
            logging.error(f"Error stopping message bus: {e}")


# Example usage and testing
async def test_enhanced_nats():
    """Test the enhanced NATS system"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize message bus
    bus = ConsciousnessMessageBus()
    
    try:
        # Start the bus
        if not await bus.start():
            logging.error("Failed to start message bus")
            return
        
        # Test consciousness event
        await bus.publish_consciousness_event(
            event_type="neural_evolution",
            consciousness_level=0.85,
            context={
                'neural_state': {'population_size': 100, 'generation': 42},
                'decision_confidence': 0.92,
                'correlation_id': 'test-001'
            }
        )
        
        # Test security alert
        await bus.publish_security_alert(
            alert_level="HIGH",
            threat_type="behavioral_anomaly",
            source_ip="192.168.1.100",
            context={
                'user_id': 'user_123',
                'action_taken': 'account_locked',
                'anomaly_score': 0.95
            }
        )
        
        # Test AI decision
        await bus.publish_ai_decision(
            decision_id="dec_001",
            decision_type="security_action",
            confidence=0.87,
            reasoning="Anomalous behavior detected with high confidence",
            alternatives=["monitor_only", "temporary_restriction"]
        )
        
        # Wait for message processing
        await asyncio.sleep(2)
        
        # Get metrics
        metrics = await bus.get_metrics()
        logging.info(f"Message bus metrics: {json.dumps(metrics, indent=2, default=str)}")
        
    except Exception as e:
        logging.error(f"Test error: {e}")
    
    finally:
        await bus.stop()


if __name__ == "__main__":
    asyncio.run(test_enhanced_nats())
