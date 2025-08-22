"""
NATS Bridge for Consciousness System V2

This module provides a bridge between the consciousness_v2 event system
and the NATS message bus used by the Service Orchestrator.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime

import nats
from nats.errors import ConnectionClosedError, TimeoutError

from ..components.event_bus import EventBus
from ..components.consciousness_core import ConsciousnessCore


class NATSBridge:
    """Bridge between consciousness_v2 and NATS message bus"""
    
    def __init__(self, 
                 nats_url: str = "nats://localhost:4222",
                 consciousness_core: Optional[ConsciousnessCore] = None,
                 event_bus: Optional[EventBus] = None):
        """
        Initialize NATS bridge
        
        Args:
            nats_url: NATS server URL
            consciousness_core: Consciousness core instance
            event_bus: Event bus instance
        """
        self.nats_url = nats_url
        self.consciousness_core = consciousness_core
        self.event_bus = event_bus
        self.nc = None
        self.js = None
        self.logger = logging.getLogger(__name__)
        self.running = False
        
        # Event mappings
        self.consciousness_to_nats = {
            'consciousness.state_change': 'orchestrator.consciousness.state',
            'consciousness.attention_shift': 'orchestrator.consciousness.attention',
            'consciousness.memory_update': 'orchestrator.consciousness.memory',
            'consciousness.decision_made': 'orchestrator.consciousness.decision',
            'consciousness.learning_event': 'orchestrator.consciousness.learning',
            'consciousness.error': 'orchestrator.consciousness.error'
        }
        
        self.nats_to_consciousness = {
            'orchestrator.service.started': 'service.lifecycle.started',
            'orchestrator.service.stopped': 'service.lifecycle.stopped',
            'orchestrator.service.health': 'service.health.update',
            'orchestrator.system.resource': 'system.resource.update',
            'orchestrator.user.request': 'user.request.received'
        }
    
    async def connect(self) -> bool:
        """Connect to NATS server"""
        try:
            self.nc = await nats.connect(self.nats_url)
            self.js = self.nc.jetstream()
            
            # Create streams if they don't exist
            await self._ensure_streams()
            
            self.logger.info(f"Connected to NATS at {self.nats_url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to NATS: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from NATS server"""
        if self.nc:
            await self.nc.close()
            self.nc = None
            self.js = None
            self.logger.info("Disconnected from NATS")
    
    async def _ensure_streams(self):
        """Ensure required JetStream streams exist"""
        streams = [
            {
                'name': 'ORCHESTRATOR',
                'subjects': ['orchestrator.>'],
                'retention': 'limits',
                'max_msgs': 10000,
                'max_age': 86400  # 24 hours
            },
            {
                'name': 'CONSCIOUSNESS',
                'subjects': ['consciousness.>'],
                'retention': 'limits',
                'max_msgs': 10000,
                'max_age': 86400  # 24 hours
            }
        ]
        
        for stream_config in streams:
            try:
                await self.js.stream_info(stream_config['name'])
                self.logger.debug(f"Stream {stream_config['name']} already exists")
            except:
                try:
                    await self.js.add_stream(**stream_config)
                    self.logger.info(f"Created stream {stream_config['name']}")
                except Exception as e:
                    self.logger.error(f"Failed to create stream {stream_config['name']}: {e}")
    
    async def start(self):
        """Start the bridge"""
        if not await self.connect():
            return False
        
        self.running = True
        
        # Start event forwarding tasks
        tasks = []
        
        if self.event_bus:
            tasks.append(asyncio.create_task(self._forward_consciousness_events()))
        
        tasks.append(asyncio.create_task(self._subscribe_orchestrator_events()))
        
        # Wait for all tasks
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"Bridge error: {e}")
        finally:
            self.running = False
            await self.disconnect()
        
        return True
    
    async def stop(self):
        """Stop the bridge"""
        self.running = False
    
    async def _forward_consciousness_events(self):
        """Forward consciousness events to NATS"""
        if not self.event_bus:
            return
        
        while self.running:
            try:
                # Get events from consciousness event bus
                events = await self.event_bus.get_pending_events()
                
                for event in events:
                    await self._publish_consciousness_event(event)
                
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                self.logger.error(f"Error forwarding consciousness events: {e}")
                await asyncio.sleep(1)
    
    async def _publish_consciousness_event(self, event: Dict[str, Any]):
        """Publish a consciousness event to NATS"""
        try:
            event_type = event.get('type', '')
            nats_subject = self.consciousness_to_nats.get(event_type)
            
            if not nats_subject:
                # Use generic subject for unmapped events
                nats_subject = f"consciousness.{event_type.replace('.', '_')}"
            
            # Prepare event data
            nats_event = {
                'id': event.get('id', ''),
                'type': event_type,
                'source': 'consciousness_v2',
                'timestamp': event.get('timestamp', datetime.utcnow().isoformat()),
                'data': event.get('data', {}),
                'metadata': {
                    'consciousness_state': self._get_consciousness_state(),
                    'attention_level': self._get_attention_level(),
                    'memory_context': self._get_memory_context()
                }
            }
            
            # Publish to NATS
            await self.js.publish(
                nats_subject,
                json.dumps(nats_event).encode(),
                headers={'Content-Type': 'application/json'}
            )
            
            self.logger.debug(f"Published consciousness event: {event_type} -> {nats_subject}")
            
        except Exception as e:
            self.logger.error(f"Failed to publish consciousness event: {e}")
    
    async def _subscribe_orchestrator_events(self):
        """Subscribe to orchestrator events from NATS"""
        try:
            # Subscribe to orchestrator events
            psub = await self.js.pull_subscribe(
                "orchestrator.>",
                "consciousness-bridge",
                stream="ORCHESTRATOR"
            )
            
            while self.running:
                try:
                    msgs = await psub.fetch(batch=10, timeout=1.0)
                    
                    for msg in msgs:
                        await self._handle_orchestrator_event(msg)
                        await msg.ack()
                        
                except TimeoutError:
                    # No messages available, continue
                    continue
                except Exception as e:
                    self.logger.error(f"Error processing orchestrator events: {e}")
                    await asyncio.sleep(1)
                    
        except Exception as e:
            self.logger.error(f"Failed to subscribe to orchestrator events: {e}")
    
    async def _handle_orchestrator_event(self, msg):
        """Handle an orchestrator event"""
        try:
            # Parse event data
            event_data = json.loads(msg.data.decode())
            subject = msg.subject
            
            # Map to consciousness event
            consciousness_event_type = self.nats_to_consciousness.get(subject)
            
            if consciousness_event_type and self.event_bus:
                # Forward to consciousness event bus
                consciousness_event = {
                    'type': consciousness_event_type,
                    'source': 'orchestrator',
                    'timestamp': datetime.utcnow().isoformat(),
                    'data': event_data.get('data', {}),
                    'metadata': event_data.get('metadata', {})
                }
                
                await self.event_bus.publish_event(consciousness_event)
                self.logger.debug(f"Forwarded orchestrator event: {subject} -> {consciousness_event_type}")
            
            # Update consciousness state based on orchestrator events
            if self.consciousness_core:
                await self._update_consciousness_from_orchestrator(subject, event_data)
                
        except Exception as e:
            self.logger.error(f"Failed to handle orchestrator event: {e}")
    
    async def _update_consciousness_from_orchestrator(self, subject: str, event_data: Dict[str, Any]):
        """Update consciousness state based on orchestrator events"""
        try:
            if subject.startswith('orchestrator.service'):
                # Service lifecycle events affect consciousness attention
                service_name = event_data.get('data', {}).get('service_name', '')
                service_status = event_data.get('data', {}).get('status', '')
                
                if service_status in ['started', 'healthy']:
                    # Positive service events increase attention to system management
                    await self.consciousness_core.adjust_attention('system_management', 0.1)
                elif service_status in ['stopped', 'unhealthy', 'failed']:
                    # Negative service events increase attention and trigger problem-solving
                    await self.consciousness_core.adjust_attention('system_management', 0.3)
                    await self.consciousness_core.trigger_problem_solving(f"Service issue: {service_name} - {service_status}")
            
            elif subject.startswith('orchestrator.system.resource'):
                # Resource events affect consciousness resource awareness
                resource_data = event_data.get('data', {})
                cpu_usage = resource_data.get('cpu_usage', 0)
                memory_usage = resource_data.get('memory_usage', 0)
                
                if cpu_usage > 80 or memory_usage > 80:
                    # High resource usage increases attention to performance
                    await self.consciousness_core.adjust_attention('performance_optimization', 0.2)
            
            elif subject.startswith('orchestrator.user'):
                # User events increase attention to user interaction
                await self.consciousness_core.adjust_attention('user_interaction', 0.2)
                
        except Exception as e:
            self.logger.error(f"Failed to update consciousness from orchestrator event: {e}")
    
    def _get_consciousness_state(self) -> Dict[str, Any]:
        """Get current consciousness state"""
        if not self.consciousness_core:
            return {}
        
        try:
            return {
                'attention_focus': self.consciousness_core.get_attention_focus(),
                'emotional_state': self.consciousness_core.get_emotional_state(),
                'cognitive_load': self.consciousness_core.get_cognitive_load(),
                'learning_mode': self.consciousness_core.get_learning_mode()
            }
        except:
            return {}
    
    def _get_attention_level(self) -> float:
        """Get current attention level"""
        if not self.consciousness_core:
            return 0.0
        
        try:
            return self.consciousness_core.get_attention_level()
        except:
            return 0.0
    
    def _get_memory_context(self) -> Dict[str, Any]:
        """Get current memory context"""
        if not self.consciousness_core:
            return {}
        
        try:
            return {
                'working_memory_size': self.consciousness_core.get_working_memory_size(),
                'long_term_memory_active': self.consciousness_core.is_long_term_memory_active(),
                'recent_experiences': self.consciousness_core.get_recent_experiences(limit=5)
            }
        except:
            return {}
    
    async def publish_consciousness_state(self):
        """Manually publish current consciousness state"""
        if not self.consciousness_core:
            return
        
        state_event = {
            'type': 'consciousness.state_snapshot',
            'source': 'consciousness_v2',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'state': self._get_consciousness_state(),
                'attention_level': self._get_attention_level(),
                'memory_context': self._get_memory_context()
            }
        }
        
        await self._publish_consciousness_event(state_event)
    
    async def request_service_action(self, service_name: str, action: str, parameters: Dict[str, Any] = None):
        """Request a service action through the orchestrator"""
        try:
            request_event = {
                'id': f"consciousness-request-{datetime.utcnow().timestamp()}",
                'type': 'service_action_request',
                'source': 'consciousness_v2',
                'timestamp': datetime.utcnow().isoformat(),
                'data': {
                    'service_name': service_name,
                    'action': action,
                    'parameters': parameters or {},
                    'consciousness_context': self._get_consciousness_state()
                }
            }
            
            await self.js.publish(
                'orchestrator.service.action_request',
                json.dumps(request_event).encode(),
                headers={'Content-Type': 'application/json'}
            )
            
            self.logger.info(f"Requested service action: {service_name}.{action}")
            
        except Exception as e:
            self.logger.error(f"Failed to request service action: {e}")


# Convenience function to create and start bridge
async def create_nats_bridge(consciousness_core: ConsciousnessCore, 
                           event_bus: EventBus,
                           nats_url: str = "nats://localhost:4222") -> NATSBridge:
    """Create and start a NATS bridge"""
    bridge = NATSBridge(nats_url, consciousness_core, event_bus)
    
    # Start bridge in background task
    asyncio.create_task(bridge.start())
    
    return bridge