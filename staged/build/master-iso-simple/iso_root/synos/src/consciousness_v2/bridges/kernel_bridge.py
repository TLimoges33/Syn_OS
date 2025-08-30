#!/usr/bin/env python3
"""
Consciousness-Kernel Bridge for Syn_OS
=====================================

This bridge provides secure, high-performance communication between the 
consciousness system (Python) and the kernel (Rust), enabling real-time
AI-driven security decisions and system optimizations.

Key Features:
- Bidirectional async communication
- Security validation and isolation
- Real-time event streaming
- Performance monitoring
- Educational integration
"""

import asyncio
import json
import logging
import os
import socket
import struct
import subprocess
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum, IntEnum
import psutil

from ..interfaces.consciousness_component import ConsciousnessComponent
from ..core.consciousness_bus import ConsciousnessBus
from ..core.event_types import (
    EventType, EventPriority, ConsciousnessEvent, 
    create_system_event, create_security_event
)
from ..core.data_models import ComponentStatus, ComponentState

logger = logging.getLogger('synapticos.kernel_bridge')


class KernelEventType(Enum):
    """Types of events from kernel"""
    SYSTEM_PERFORMANCE = "system_performance"
    SECURITY_ALERT = "security_alert"
    THREAT_DETECTED = "threat_detected"
    MEMORY_PRESSURE = "memory_pressure"
    PROCESS_ANOMALY = "process_anomaly"
    EDUCATIONAL_REQUEST = "educational_request"
    NEURAL_FEEDBACK = "neural_feedback"


class ConsciousnessResponseType(Enum):
    """Types of responses to kernel"""
    SCHEDULING_DECISION = "scheduling_decision"
    SECURITY_ACTION = "security_action"
    MEMORY_OPTIMIZATION = "memory_optimization"
    THREAT_MITIGATION = "threat_mitigation"
    EDUCATIONAL_RESPONSE = "educational_response"
    SYSTEM_ADJUSTMENT = "system_adjustment"


@dataclass
class KernelMessage:
    """Message from kernel to consciousness"""
    message_id: str
    event_type: KernelEventType
    timestamp: datetime
    data: Dict[str, Any]
    priority: int = 5
    requires_response: bool = False
    
    def to_consciousness_event(self, source_component: str = "kernel") -> ConsciousnessEvent:
        """Convert to consciousness event"""
        # Map kernel events to consciousness event types
        event_type_mapping = {
            KernelEventType.SECURITY_ALERT: EventType.SECURITY_EVENT,
            KernelEventType.THREAT_DETECTED: EventType.SECURITY_EVENT,
            KernelEventType.SYSTEM_PERFORMANCE: EventType.SYSTEM_STATUS,
            KernelEventType.MEMORY_PRESSURE: EventType.SYSTEM_STATUS,
            KernelEventType.PROCESS_ANOMALY: EventType.SECURITY_EVENT,
            KernelEventType.EDUCATIONAL_REQUEST: EventType.USER_INTERACTION,
            KernelEventType.NEURAL_FEEDBACK: EventType.CONSCIOUSNESS_UPDATE
        }
        
        consciousness_event_type = event_type_mapping.get(
            self.event_type, EventType.SYSTEM_STATUS
        )
        
        # Map priority
        priority_mapping = {
            1: EventPriority.CRITICAL,
            2: EventPriority.HIGH,
            3: EventPriority.HIGH,
            4: EventPriority.MEDIUM,
            5: EventPriority.MEDIUM,
            6: EventPriority.LOW,
            7: EventPriority.LOW,
            8: EventPriority.LOW,
            9: EventPriority.LOW,
            10: EventPriority.LOW
        }
        
        consciousness_priority = priority_mapping.get(self.priority, EventPriority.MEDIUM)
        
        return ConsciousnessEvent(
            event_type=consciousness_event_type,
            source_component=source_component,
            timestamp=self.timestamp,
            priority=consciousness_priority,
            data={
                'kernel_event_type': self.event_type.value,
                'kernel_message_id': self.message_id,
                'requires_response': self.requires_response,
                **self.data
            },
            metadata={
                'bridge_processed': True,
                'original_priority': self.priority
            }
        )


@dataclass
class ConsciousnessResponse:
    """Response from consciousness to kernel"""
    request_id: str
    response_type: ConsciousnessResponseType
    timestamp: datetime
    decision: Dict[str, Any]
    confidence: float
    explanation: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_kernel_format(self) -> Dict[str, Any]:
        """Convert to kernel-compatible format"""
        return {
            'request_id': self.request_id,
            'response_type': self.response_type.value,
            'timestamp': self.timestamp.isoformat(),
            'decision': self.decision,
            'confidence': self.confidence,
            'explanation': self.explanation,
            'metadata': self.metadata
        }


class KernelBridge(ConsciousnessComponent):
    """
    Bridge between consciousness system and kernel
    
    Provides secure communication channel for:
    - Real-time system monitoring
    - AI-driven security decisions
    - Performance optimizations
    - Educational interactions
    """
    
    def __init__(self, 
                 consciousness_bus: ConsciousnessBus,
                 kernel_socket_path: str = None,
                 bridge_port: int = 8900,
                 max_queue_size: int = 1000):
        
        # Use secure temp directory instead of hardcoded /tmp
        if kernel_socket_path is None:
            import tempfile
            temp_dir = tempfile.mkdtemp(prefix="syn_os_", suffix="_kernel")
            kernel_socket_path = os.path.join(temp_dir, "kernel.sock")
        
        super().__init__(
            component_id="kernel_bridge",
            component_type="system_integration",
            consciousness_bus=consciousness_bus
        )
        
        # Configuration
        self.kernel_socket_path = Path(kernel_socket_path)
        self.bridge_port = bridge_port
        self.max_queue_size = max_queue_size
        
        # Communication channels
        self.kernel_socket: Optional[socket.socket] = None
        self.bridge_server: Optional[asyncio.Server] = None
        self.connected_clients: Dict[str, Tuple[asyncio.StreamReader, asyncio.StreamWriter]] = {}
        
        # Message queues
        self.incoming_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.outgoing_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        
        # Response tracking
        self.pending_responses: Dict[str, asyncio.Future] = {}
        self.response_timeout = 30.0  # seconds
        
        # Background tasks
        self.message_processor_task: Optional[asyncio.Task] = None
        self.kernel_listener_task: Optional[asyncio.Task] = None
        self.response_sender_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.stats = {
            'messages_received': 0,
            'messages_sent': 0,
            'responses_sent': 0,
            'errors': 0,
            'avg_response_time_ms': 0.0,
            'last_kernel_contact': None
        }
        
        # Event handlers
        self.event_handlers: Dict[KernelEventType, Callable] = {
            KernelEventType.SECURITY_ALERT: self._handle_security_alert,
            KernelEventType.THREAT_DETECTED: self._handle_threat_detection,
            KernelEventType.SYSTEM_PERFORMANCE: self._handle_performance_update,
            KernelEventType.MEMORY_PRESSURE: self._handle_memory_pressure,
            KernelEventType.PROCESS_ANOMALY: self._handle_process_anomaly,
            KernelEventType.EDUCATIONAL_REQUEST: self._handle_educational_request,
            KernelEventType.NEURAL_FEEDBACK: self._handle_neural_feedback
        }
        
        logger.info(f"Kernel bridge initialized: socket={kernel_socket_path}, port={bridge_port}")
    
    async def initialize(self) -> bool:
        """Initialize the bridge"""
        try:
            logger.info("Initializing kernel bridge...")
            
            # Subscribe to consciousness events that need kernel communication
            await self.consciousness_bus.subscribe(
                EventType.SECURITY_EVENT,
                self._handle_security_response,
                self.component_id
            )
            
            await self.consciousness_bus.subscribe(
                EventType.SYSTEM_OPTIMIZATION,
                self._handle_optimization_response,
                self.component_id
            )
            
            await self.consciousness_bus.subscribe(
                EventType.USER_INTERACTION,
                self._handle_user_response,
                self.component_id
            )
            
            # Start bridge server for kernel connections
            await self._start_bridge_server()
            
            # Start message processing tasks
            self.message_processor_task = asyncio.create_task(self._message_processor())
            self.response_sender_task = asyncio.create_task(self._response_sender())
            
            # Register with consciousness bus
            status = ComponentStatus(
                component_id=self.component_id,
                component_type=self.component_type,
                state=ComponentState.INITIALIZING,
                health_score=1.0,
                last_heartbeat=datetime.now()
            )
            await self.consciousness_bus.register_component(status)
            
            logger.info("Kernel bridge initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize kernel bridge: {e}")
            return False
    
    async def start(self) -> bool:
        """Start the bridge"""
        try:
            if not await self.initialize():
                return False
            
            # Update status to running
            await self._update_component_status(ComponentState.RUNNING, 1.0)
            
            logger.info("Kernel bridge started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start kernel bridge: {e}")
            await self._update_component_status(ComponentState.FAILED, 0.0)
            return False
    
    async def stop(self) -> None:
        """Stop the bridge"""
        logger.info("Stopping kernel bridge...")
        
        # Update status
        await self._update_component_status(ComponentState.STOPPING, 0.5)
        
        # Cancel background tasks
        if self.message_processor_task:
            self.message_processor_task.cancel()
        if self.kernel_listener_task:
            self.kernel_listener_task.cancel()
        if self.response_sender_task:
            self.response_sender_task.cancel()
        
        # Close server
        if self.bridge_server:
            self.bridge_server.close()
            await self.bridge_server.wait_closed()
        
        # Close client connections
        for client_id, (reader, writer) in self.connected_clients.items():
            writer.close()
            await writer.wait_closed()
        
        self.connected_clients.clear()
        
        # Update final status
        await self._update_component_status(ComponentState.STOPPED, 0.0)
        
        logger.info("Kernel bridge stopped")
    
    async def send_to_kernel(self, response: ConsciousnessResponse) -> bool:
        """Send response to kernel"""
        try:
            # Convert to kernel format
            kernel_data = response.to_kernel_format()
            
            # Add to outgoing queue
            await self.outgoing_queue.put(kernel_data)
            
            self.stats['responses_sent'] += 1
            logger.debug(f"Queued response for kernel: {response.request_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send response to kernel: {e}")
            self.stats['errors'] += 1
            return False
    
    async def get_bridge_status(self) -> Dict[str, Any]:
        """Get bridge status and statistics"""
        return {
            'component_id': self.component_id,
            'is_running': self.message_processor_task is not None and not self.message_processor_task.done(),
            'connected_clients': len(self.connected_clients),
            'queue_sizes': {
                'incoming': self.incoming_queue.qsize(),
                'outgoing': self.outgoing_queue.qsize()
            },
            'pending_responses': len(self.pending_responses),
            'statistics': self.stats.copy(),
            'kernel_socket_path': str(self.kernel_socket_path),
            'bridge_port': self.bridge_port
        }
    
    # --- Private Methods ---
    
    async def _start_bridge_server(self) -> None:
        """Start the bridge server for kernel connections"""
        try:
            self.bridge_server = await asyncio.start_server(
                self._handle_kernel_connection,
                'localhost',
                self.bridge_port
            )
            
            logger.info(f"Bridge server started on port {self.bridge_port}")
            
        except Exception as e:
            logger.error(f"Failed to start bridge server: {e}")
            raise
    
    async def _handle_kernel_connection(self, 
                                      reader: asyncio.StreamReader, 
                                      writer: asyncio.StreamWriter) -> None:
        """Handle connection from kernel"""
        client_addr = writer.get_extra_info('peername')
        client_id = f"kernel_{client_addr[0]}_{client_addr[1]}_{int(time.time())}"
        
        logger.info(f"Kernel connected: {client_id}")
        
        try:
            # Store connection
            self.connected_clients[client_id] = (reader, writer)
            
            # Send welcome message
            welcome = {
                'type': 'connection_established',
                'bridge_id': self.component_id,
                'timestamp': datetime.now().isoformat(),
                'capabilities': ['security_response', 'optimization', 'educational']
            }
            await self._send_to_client(writer, welcome)
            
            # Handle messages from this client
            while True:
                try:
                    # Read message length
                    length_data = await reader.readexactly(4)
                    message_length = struct.unpack('!I', length_data)[0]
                    
                    # Read message data
                    message_data = await reader.readexactly(message_length)
                    message_json = message_data.decode('utf-8')
                    message = json.loads(message_json)
                    
                    # Process message
                    await self._process_kernel_message(message, client_id)
                    
                except asyncio.IncompleteReadError:
                    # Client disconnected
                    break
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON from {client_id}: {e}")
                except Exception as e:
                    logger.error(f"Error handling message from {client_id}: {e}")
            
        except Exception as e:
            logger.error(f"Error in kernel connection {client_id}: {e}")
        
        finally:
            # Clean up connection
            if client_id in self.connected_clients:
                del self.connected_clients[client_id]
            
            writer.close()
            await writer.wait_closed()
            logger.info(f"Kernel disconnected: {client_id}")
    
    async def _send_to_client(self, writer: asyncio.StreamWriter, data: Dict[str, Any]) -> None:
        """Send data to a specific client"""
        try:
            # Serialize message
            message_json = json.dumps(data)
            message_data = message_json.encode('utf-8')
            
            # Send length prefix + data
            length_prefix = struct.pack('!I', len(message_data))
            writer.write(length_prefix + message_data)
            await writer.drain()
            
        except Exception as e:
            logger.error(f"Failed to send data to client: {e}")
            raise
    
    async def _process_kernel_message(self, message: Dict[str, Any], client_id: str) -> None:
        """Process message from kernel"""
        try:
            # Parse kernel message
            kernel_msg = KernelMessage(
                message_id=message.get('id', ''),
                event_type=KernelEventType(message.get('event_type', 'system_performance')),
                timestamp=datetime.fromisoformat(message.get('timestamp', datetime.now().isoformat())),
                data=message.get('data', {}),
                priority=message.get('priority', 5),
                requires_response=message.get('requires_response', False)
            )
            
            # Add to incoming queue
            await self.incoming_queue.put((kernel_msg, client_id))
            
            self.stats['messages_received'] += 1
            self.stats['last_kernel_contact'] = datetime.now().isoformat()
            
            logger.debug(f"Received kernel message: {kernel_msg.event_type.value}")
            
        except Exception as e:
            logger.error(f"Failed to process kernel message: {e}")
            self.stats['errors'] += 1
    
    async def _message_processor(self) -> None:
        """Process incoming messages from kernel"""
        logger.info("Started kernel message processor")
        
        while True:
            try:
                # Get message from queue
                kernel_msg, client_id = await self.incoming_queue.get()
                
                # Handle the message
                handler = self.event_handlers.get(kernel_msg.event_type)
                if handler:
                    await handler(kernel_msg, client_id)
                else:
                    logger.warning(f"No handler for event type: {kernel_msg.event_type}")
                
                # Convert to consciousness event and publish
                consciousness_event = kernel_msg.to_consciousness_event("kernel_bridge")
                await self.consciousness_bus.publish(consciousness_event)
                
                # Mark task as done
                self.incoming_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in message processor: {e}")
                await asyncio.sleep(1.0)
        
        logger.info("Kernel message processor stopped")
    
    async def _response_sender(self) -> None:
        """Send responses back to kernel"""
        logger.info("Started response sender")
        
        while True:
            try:
                # Get response from queue
                response_data = await self.outgoing_queue.get()
                
                # Send to all connected clients (broadcast)
                for client_id, (reader, writer) in self.connected_clients.items():
                    try:
                        await self._send_to_client(writer, response_data)
                        logger.debug(f"Sent response to {client_id}")
                    except Exception as e:
                        logger.error(f"Failed to send response to {client_id}: {e}")
                
                self.stats['messages_sent'] += 1
                
                # Mark task as done
                self.outgoing_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in response sender: {e}")
                await asyncio.sleep(1.0)
        
        logger.info("Response sender stopped")
    
    # --- Event Handlers ---
    
    async def _handle_security_alert(self, kernel_msg: KernelMessage, client_id: str) -> None:
        """Handle security alert from kernel"""
        logger.warning(f"Security alert from kernel: {kernel_msg.data}")
        
        # Create high-priority security event
        security_event = create_security_event(
            source_component="kernel_bridge",
            security_data={
                'alert_type': kernel_msg.data.get('alert_type', 'unknown'),
                'severity': kernel_msg.data.get('severity', 'medium'),
                'details': kernel_msg.data.get('details', {}),
                'requires_immediate_action': kernel_msg.data.get('critical', False)
            }
        )
        
        await self.consciousness_bus.publish(security_event)
    
    async def _handle_threat_detection(self, kernel_msg: KernelMessage, client_id: str) -> None:
        """Handle threat detection from kernel"""
        logger.critical(f"Threat detected by kernel: {kernel_msg.data}")
        
        # This requires immediate response
        if kernel_msg.requires_response:
            response = ConsciousnessResponse(
                request_id=kernel_msg.message_id,
                response_type=ConsciousnessResponseType.THREAT_MITIGATION,
                timestamp=datetime.now(),
                decision={
                    'action': 'isolate_and_analyze',
                    'quarantine': True,
                    'notify_admin': True
                },
                confidence=0.95,
                explanation="Immediate threat isolation based on kernel detection"
            )
            
            await self.send_to_kernel(response)
    
    async def _handle_performance_update(self, kernel_msg: KernelMessage, client_id: str) -> None:
        """Handle performance update from kernel"""
        logger.debug(f"Performance update from kernel: {kernel_msg.data}")
        
        # Update consciousness state with performance data
        await self.consciousness_bus.update_consciousness_state(
            self.component_id,
            {
                'system_performance': kernel_msg.data,
                'last_performance_update': kernel_msg.timestamp.isoformat()
            }
        )
    
    async def _handle_memory_pressure(self, kernel_msg: KernelMessage, client_id: str) -> None:
        """Handle memory pressure from kernel"""
        logger.warning(f"Memory pressure detected: {kernel_msg.data}")
        
        if kernel_msg.requires_response:
            response = ConsciousnessResponse(
                request_id=kernel_msg.message_id,
                response_type=ConsciousnessResponseType.MEMORY_OPTIMIZATION,
                timestamp=datetime.now(),
                decision={
                    'action': 'optimize_memory',
                    'free_cache': True,
                    'adjust_priorities': True,
                    'target_reduction': '20%'
                },
                confidence=0.85,
                explanation="Memory optimization to relieve pressure"
            )
            
            await self.send_to_kernel(response)
    
    async def _handle_process_anomaly(self, kernel_msg: KernelMessage, client_id: str) -> None:
        """Handle process anomaly from kernel"""
        logger.warning(f"Process anomaly detected: {kernel_msg.data}")
        
        # Create security event for anomaly analysis
        anomaly_event = create_security_event(
            source_component="kernel_bridge",
            security_data={
                'anomaly_type': 'process_behavior',
                'process_id': kernel_msg.data.get('process_id'),
                'anomaly_details': kernel_msg.data,
                'requires_analysis': True
            }
        )
        
        await self.consciousness_bus.publish(anomaly_event)
    
    async def _handle_educational_request(self, kernel_msg: KernelMessage, client_id: str) -> None:
        """Handle educational request from kernel"""
        logger.info(f"Educational request from kernel: {kernel_msg.data}")
        
        if kernel_msg.requires_response:
            response = ConsciousnessResponse(
                request_id=kernel_msg.message_id,
                response_type=ConsciousnessResponseType.EDUCATIONAL_RESPONSE,
                timestamp=datetime.now(),
                decision={
                    'provide_explanation': True,
                    'learning_content': kernel_msg.data.get('topic', 'general'),
                    'difficulty_level': kernel_msg.data.get('level', 'intermediate')
                },
                confidence=0.90,
                explanation="Educational content provided based on kernel request"
            )
            
            await self.send_to_kernel(response)
    
    async def _handle_neural_feedback(self, kernel_msg: KernelMessage, client_id: str) -> None:
        """Handle neural feedback from kernel"""
        logger.debug(f"Neural feedback from kernel: {kernel_msg.data}")
        
        # Update neural darwinism with feedback
        await self.consciousness_bus.update_consciousness_state(
            self.component_id,
            {
                'neural_feedback': kernel_msg.data,
                'last_neural_update': kernel_msg.timestamp.isoformat()
            }
        )
    
    # --- Consciousness Event Handlers ---
    
    async def _handle_security_response(self, event: ConsciousnessEvent) -> None:
        """Handle security response to send to kernel"""
        if event.source_component == self.component_id:
            return  # Avoid loops
        
        # Check if this requires kernel notification
        if event.data.get('notify_kernel', False):
            response = ConsciousnessResponse(
                request_id=event.data.get('kernel_request_id', event.event_id),
                response_type=ConsciousnessResponseType.SECURITY_ACTION,
                timestamp=datetime.now(),
                decision=event.data.get('security_decision', {}),
                confidence=event.data.get('confidence', 0.8),
                explanation=event.data.get('explanation', 'Security response from consciousness')
            )
            
            await self.send_to_kernel(response)
    
    async def _handle_optimization_response(self, event: ConsciousnessEvent) -> None:
        """Handle optimization response to send to kernel"""
        if event.source_component == self.component_id:
            return  # Avoid loops
        
        if event.data.get('target') == 'kernel':
            response = ConsciousnessResponse(
                request_id=event.data.get('kernel_request_id', event.event_id),
                response_type=ConsciousnessResponseType.SYSTEM_ADJUSTMENT,
                timestamp=datetime.now(),
                decision=event.data.get('optimization_decision', {}),
                confidence=event.data.get('confidence', 0.75),
                explanation=event.data.get('explanation', 'System optimization from consciousness')
            )
            
            await self.send_to_kernel(response)
    
    async def _handle_user_response(self, event: ConsciousnessEvent) -> None:
        """Handle user interaction response to send to kernel"""
        if event.source_component == self.component_id:
            return  # Avoid loops
        
        # Check if this is an educational response for the kernel
        if event.data.get('educational_target') == 'kernel':
            response = ConsciousnessResponse(
                request_id=event.data.get('kernel_request_id', event.event_id),
                response_type=ConsciousnessResponseType.EDUCATIONAL_RESPONSE,
                timestamp=datetime.now(),
                decision=event.data.get('educational_content', {}),
                confidence=event.data.get('confidence', 0.9),
                explanation=event.data.get('explanation', 'Educational response from consciousness')
            )
            
            await self.send_to_kernel(response)
    
    async def _update_component_status(self, state: ComponentState, health_score: float) -> None:
        """Update component status in consciousness bus"""
        if hasattr(self, 'consciousness_bus'):
            status = ComponentStatus(
                component_id=self.component_id,
                component_type=self.component_type,
                state=state,
                health_score=health_score,
                last_heartbeat=datetime.now()
            )
            await self.consciousness_bus.register_component(status)