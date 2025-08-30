"""
Consciousness Component Interface
================================

Base interface for all consciousness system components.
Provides standardized methods for component lifecycle, health monitoring,
and event handling.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

from ..core.event_types import ConsciousnessEvent, EventType
from ..core.data_models import ComponentStatus, ComponentState


class ConsciousnessComponent(ABC):
    """
    Base interface for all consciousness system components
    
    All consciousness components must implement this interface to ensure
    proper integration with the consciousness bus and state management.
    """
    
    def __init__(self, component_id: str, component_type: str):
        self.component_id = component_id
        self.component_type = component_type
        self.is_running = False
        self.logger = logging.getLogger(f"{__name__}.{component_id}")
        
        # Component state
        self.status = ComponentStatus(
            component_id=component_id,
            component_type=component_type,
            state=ComponentState.UNKNOWN,
            health_score=0.0,
            last_heartbeat=datetime.now()
        )
        
        # Event handling
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self.consciousness_bus = None
        self.state_manager = None
    
    @abstractmethod
    async def start(self) -> bool:
        """Start the component"""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the component"""
        pass
    
    @abstractmethod
    async def process_event(self, event: ConsciousnessEvent) -> bool:
        """Process a consciousness event"""
        pass
    
    @abstractmethod
    async def get_health_status(self) -> ComponentStatus:
        """Get current health status"""
        pass
    
    @abstractmethod
    async def update_configuration(self, config: Dict[str, Any]) -> bool:
        """Update component configuration"""
        pass
    
    # Common implementation methods
    
    async def initialize(self, consciousness_bus, state_manager) -> bool:
        """Initialize component with consciousness bus and state manager"""
        self.consciousness_bus = consciousness_bus
        self.state_manager = state_manager
        
        # Register with consciousness bus
        if consciousness_bus:
            await consciousness_bus.register_component(self.status)
        
        # Register with state manager
        if state_manager:
            await state_manager.update_component_state(self.component_id, self.status)
        
        self.logger.info(f"Initialized component {self.component_id}")
        return True
    
    async def register_event_handler(self, event_type: EventType, handler: Callable) -> str:
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        
        # Subscribe to event type on consciousness bus
        if self.consciousness_bus:
            subscription_id = await self.consciousness_bus.subscribe(
                event_type, self._handle_event, self.component_id
            )
            return subscription_id
        
        return ""
    
    async def publish_event(self, event: ConsciousnessEvent) -> bool:
        """Publish an event to the consciousness bus"""
        if self.consciousness_bus:
            return await self.consciousness_bus.publish(event)
        return False
    
    async def update_heartbeat(self) -> None:
        """Update component heartbeat"""
        self.status.last_heartbeat = datetime.now()
        
        if self.consciousness_bus:
            await self.consciousness_bus.update_component_heartbeat(self.component_id)
        
        if self.state_manager:
            await self.state_manager.update_component_state(self.component_id, self.status)
    
    async def update_health_score(self, score: float) -> None:
        """Update component health score"""
        self.status.health_score = max(0.0, min(1.0, score))
        
        if self.state_manager:
            await self.state_manager.update_component_state(self.component_id, self.status)
    
    async def set_component_state(self, state: ComponentState) -> None:
        """Set component state"""
        self.status.state = state
        
        if self.state_manager:
            await self.state_manager.update_component_state(self.component_id, self.status)
    
    async def _handle_event(self, event: ConsciousnessEvent) -> None:
        """Internal event handler that routes to registered handlers"""
        try:
            # Call component's process_event method
            await self.process_event(event)
            
            # Call registered event handlers
            handlers = self.event_handlers.get(event.event_type, [])
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    self.logger.error(f"Error in event handler: {e}")
            
        except Exception as e:
            self.logger.error(f"Error processing event {event.event_id}: {e}")
            self.status.error_rate += 0.01  # Increment error rate
    
    def get_component_info(self) -> Dict[str, Any]:
        """Get component information"""
        return {
            'component_id': self.component_id,
            'component_type': self.component_type,
            'is_running': self.is_running,
            'status': self.status.to_dict(),
            'registered_events': list(self.event_handlers.keys())
        }