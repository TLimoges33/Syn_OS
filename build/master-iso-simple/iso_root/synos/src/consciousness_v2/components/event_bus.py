"""
Event Bus Component - Bridge to Core Consciousness Bus
=====================================================

This module provides a simplified interface to the core consciousness bus
for compatibility with the NATS bridge and other components.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

from ..core.consciousness_bus import ConsciousnessBus as CoreConsciousnessBus
from ..core.event_types import ConsciousnessEvent, EventType, EventPriority


class EventBus:
    """
    Event Bus wrapper for the core consciousness bus
    Provides simplified interface for NATS bridge integration
    """
    
    def __init__(self, core_bus: Optional[CoreConsciousnessBus] = None):
        """
        Initialize event bus
        
        Args:
            core_bus: Core consciousness bus instance
        """
        self.core_bus = core_bus or CoreConsciousnessBus()
        self.logger = logging.getLogger(__name__)
        self.pending_events = asyncio.Queue()
        self.is_running = False
        
        # Event forwarding task
        self.forwarding_task: Optional[asyncio.Task] = None
    
    async def start(self) -> bool:
        """Start the event bus"""
        try:
            # Start core bus if not already running
            if not self.core_bus.is_running:
                await self.core_bus.start()
            
            self.is_running = True
            
            # Start event forwarding task
            self.forwarding_task = asyncio.create_task(self._event_forwarding_loop())
            
            self.logger.info("Event bus started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start event bus: {e}")
            return False
    
    async def stop(self) -> None:
        """Stop the event bus"""
        self.is_running = False
        
        if self.forwarding_task:
            self.forwarding_task.cancel()
        
        # Stop core bus if we started it
        if self.core_bus.is_running:
            await self.core_bus.stop()
        
        self.logger.info("Event bus stopped")
    
    async def publish_event(self, event: Dict[str, Any]) -> bool:
        """
        Publish an event to the bus
        
        Args:
            event: Event dictionary with type, data, etc.
            
        Returns:
            bool: True if published successfully
        """
        try:
            # Convert dict to ConsciousnessEvent
            consciousness_event = self._dict_to_consciousness_event(event)
            
            # Publish to core bus
            success = await self.core_bus.publish(consciousness_event)
            
            if success:
                self.logger.debug(f"Published event {event.get('type', 'unknown')}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to publish event: {e}")
            return False
    
    async def get_pending_events(self) -> List[Dict[str, Any]]:
        """
        Get pending events for NATS forwarding
        
        Returns:
            List of event dictionaries
        """
        events = []
        
        try:
            # Get all available events from queue (non-blocking)
            while not self.pending_events.empty():
                try:
                    event = self.pending_events.get_nowait()
                    events.append(event)
                except asyncio.QueueEmpty:
                    break
        except Exception as e:
            self.logger.error(f"Error getting pending events: {e}")
        
        return events
    
    async def subscribe(self, 
                       event_type: str, 
                       handler: Callable[[Dict[str, Any]], None],
                       component_id: str = "event_bus") -> str:
        """
        Subscribe to events of a specific type
        
        Args:
            event_type: Type of event to subscribe to
            handler: Event handler function
            component_id: ID of subscribing component
            
        Returns:
            Subscription ID
        """
        try:
            # Convert string event type to EventType enum
            event_type_enum = self._string_to_event_type(event_type)
            
            # Wrap handler to convert ConsciousnessEvent to dict
            async def wrapped_handler(consciousness_event: ConsciousnessEvent):
                event_dict = self._consciousness_event_to_dict(consciousness_event)
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_dict)
                else:
                    handler(event_dict)
            
            # Subscribe to core bus
            subscription_id = await self.core_bus.subscribe(
                event_type_enum, wrapped_handler, component_id
            )
            
            self.logger.debug(f"Subscribed to {event_type} events")
            return subscription_id
            
        except Exception as e:
            self.logger.error(f"Failed to subscribe to {event_type}: {e}")
            return ""
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events
        
        Args:
            subscription_id: Subscription ID to remove
            
        Returns:
            bool: True if unsubscribed successfully
        """
        try:
            return await self.core_bus.unsubscribe(subscription_id)
        except Exception as e:
            self.logger.error(f"Failed to unsubscribe {subscription_id}: {e}")
            return False
    
    def _dict_to_consciousness_event(self, event_dict: Dict[str, Any]) -> ConsciousnessEvent:
        """Convert event dictionary to ConsciousnessEvent"""
        
        # Extract event type
        event_type_str = event_dict.get('type', 'state_sync')
        event_type = self._string_to_event_type(event_type_str)
        
        # Extract priority
        priority_str = event_dict.get('priority', 'normal')
        priority = self._string_to_priority(priority_str)
        
        # Create consciousness event
        consciousness_event = ConsciousnessEvent(
            event_type=event_type,
            source_component=event_dict.get('source', 'event_bus'),
            target_components=event_dict.get('target_components', []),
            priority=priority,
            data=event_dict.get('data', {}),
            correlation_id=event_dict.get('correlation_id')
        )
        
        # Set timestamp if provided
        if 'timestamp' in event_dict:
            if isinstance(event_dict['timestamp'], str):
                consciousness_event.timestamp = datetime.fromisoformat(event_dict['timestamp'])
            elif isinstance(event_dict['timestamp'], datetime):
                consciousness_event.timestamp = event_dict['timestamp']
        
        return consciousness_event
    
    def _consciousness_event_to_dict(self, event: ConsciousnessEvent) -> Dict[str, Any]:
        """Convert ConsciousnessEvent to dictionary"""
        
        return {
            'id': event.event_id,
            'type': event.event_type.value,
            'source': event.source_component,
            'target_components': event.target_components,
            'priority': event.priority.value,
            'timestamp': event.timestamp.isoformat(),
            'data': event.data,
            'correlation_id': event.correlation_id,
            'retry_count': event.retry_count,
            'processed_at': event.processed_at.isoformat() if event.processed_at else None
        }
    
    def _string_to_event_type(self, event_type_str: str) -> EventType:
        """Convert string to EventType enum"""
        
        # Map common event type strings to EventType enum
        type_mapping = {
            'consciousness.state_change': EventType.STATE_UPDATE,
            'consciousness.attention_shift': EventType.CONSCIOUSNESS_EMERGENCE,
            'consciousness.memory_update': EventType.CONTEXT_UPDATE,
            'consciousness.decision_made': EventType.NEURAL_EVOLUTION,
            'consciousness.learning_event': EventType.LEARNING_PROGRESS,
            'consciousness.error': EventType.ERROR_RECOVERY,
            'state_sync': EventType.STATE_SYNC,
            'state_update': EventType.STATE_UPDATE,
            'neural_evolution': EventType.NEURAL_EVOLUTION,
            'context_update': EventType.CONTEXT_UPDATE,
            'learning_progress': EventType.LEARNING_PROGRESS,
            'performance_update': EventType.PERFORMANCE_UPDATE,
            'security_event': EventType.SECURITY_EVENT,
            'health_check': EventType.HEALTH_CHECK,
            'error_recovery': EventType.ERROR_RECOVERY
        }
        
        return type_mapping.get(event_type_str, EventType.STATE_SYNC)
    
    def _string_to_priority(self, priority_str: str) -> EventPriority:
        """Convert string to EventPriority enum"""
        
        priority_mapping = {
            'low': EventPriority.LOW,
            'normal': EventPriority.NORMAL,
            'high': EventPriority.HIGH,
            'critical': EventPriority.CRITICAL
        }
        
        return priority_mapping.get(priority_str.lower(), EventPriority.NORMAL)
    
    async def _event_forwarding_loop(self) -> None:
        """Background loop to forward events to pending queue for NATS"""
        
        # Subscribe to all events for forwarding
        subscription_id = await self.core_bus.subscribe(
            EventType.STATE_SYNC,  # This will be overridden by wildcard subscription
            self._forward_event_to_pending,
            "nats_forwarder"
        )
        
        try:
            while self.is_running:
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
        finally:
            if subscription_id:
                await self.core_bus.unsubscribe(subscription_id)
    
    async def _forward_event_to_pending(self, event: ConsciousnessEvent) -> None:
        """Forward event to pending queue for NATS bridge"""
        
        try:
            event_dict = self._consciousness_event_to_dict(event)
            await self.pending_events.put(event_dict)
        except Exception as e:
            self.logger.error(f"Failed to forward event to pending queue: {e}")


# Convenience function to create event bus
async def create_event_bus() -> EventBus:
    """Create and start an event bus instance"""
    event_bus = EventBus()
    await event_bus.start()
    return event_bus
