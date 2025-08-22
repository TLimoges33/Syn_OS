"""
Consciousness Bus - Central Event System
========================================

The consciousness bus is the central nervous system of the consciousness system,
providing event-driven communication between all components with high performance,
reliability, and real-time processing capabilities.
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Callable, Awaitable, Set, Any
from collections import defaultdict, deque
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import weakref
import json

from .event_types import (
    ConsciousnessEvent, EventType, EventPriority,
    create_health_check_event, create_error_recovery_event
)
from .data_models import ConsciousnessState, ComponentStatus, ComponentState


@dataclass
class Subscription:
    """Event subscription information"""
    subscription_id: str
    component_id: str
    event_type: EventType
    handler: Callable[[ConsciousnessEvent], Awaitable[None]]
    created_at: datetime = field(default_factory=datetime.now)
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    error_count: int = 0
    
    def __hash__(self):
        return hash(self.subscription_id)


@dataclass
class EventMetrics:
    """Event processing metrics"""
    total_events: int = 0
    events_by_type: Dict[EventType, int] = field(default_factory=lambda: defaultdict(int))
    events_by_priority: Dict[EventPriority, int] = field(default_factory=lambda: defaultdict(int))
    average_processing_time_ms: float = 0.0
    failed_events: int = 0
    retried_events: int = 0
    dropped_events: int = 0
    
    # Performance tracking
    events_per_second: float = 0.0
    peak_events_per_second: float = 0.0
    last_reset: datetime = field(default_factory=datetime.now)


class ConsciousnessBus:
    """
    High-performance event bus for consciousness system communication
    
    Features:
    - Priority-based event queuing
    - Asynchronous event processing
    - Component health monitoring
    - Event retry and error handling
    - Performance metrics and monitoring
    - Real-time event streaming
    """
    
    def __init__(self, 
                 max_queue_size: int = 10000,
                 max_workers: int = 4,
                 health_check_interval: float = 30.0,
                 metrics_update_interval: float = 5.0):
        
        # Core configuration
        self.max_queue_size = max_queue_size
        self.max_workers = max_workers
        self.health_check_interval = health_check_interval
        self.metrics_update_interval = metrics_update_interval
        
        # Event processing
        self.event_queue = asyncio.PriorityQueue(maxsize=max_queue_size)
        self.processing_workers: List[asyncio.Task] = []
        self.is_running = False
        
        # Subscriptions management
        self.subscriptions: Dict[EventType, Set[Subscription]] = defaultdict(set)
        self.component_subscriptions: Dict[str, Set[Subscription]] = defaultdict(set)
        self.subscription_lookup: Dict[str, Subscription] = {}
        
        # Component tracking
        self.registered_components: Dict[str, ComponentStatus] = {}
        self.component_heartbeats: Dict[str, datetime] = {}
        
        # State management
        self.consciousness_state: Optional[ConsciousnessState] = None
        self.state_lock = asyncio.Lock()
        
        # Performance metrics
        self.metrics = EventMetrics()
        self.metrics_lock = asyncio.Lock()
        
        # Background tasks
        self.health_check_task: Optional[asyncio.Task] = None
        self.metrics_task: Optional[asyncio.Task] = None
        
        # Event history for debugging
        self.event_history: deque = deque(maxlen=1000)
        
        # Logger
        self.logger = logging.getLogger(f"{__name__}.ConsciousnessBus")
        
        # Shutdown event
        self.shutdown_event = asyncio.Event()
    
    async def start(self) -> bool:
        """Start the consciousness bus"""
        if self.is_running:
            self.logger.warning("Consciousness bus is already running")
            return True
        
        try:
            self.logger.info("Starting consciousness bus...")
            
            # Start processing workers
            for i in range(self.max_workers):
                worker = asyncio.create_task(
                    self._event_processing_worker(f"worker_{i}")
                )
                self.processing_workers.append(worker)
            
            # Start background tasks
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            self.metrics_task = asyncio.create_task(self._metrics_update_loop())
            
            self.is_running = True
            self.logger.info(f"Consciousness bus started with {self.max_workers} workers")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start consciousness bus: {e}")
            await self.stop()
            return False
    
    async def stop(self) -> None:
        """Stop the consciousness bus"""
        if not self.is_running:
            return
        
        self.logger.info("Stopping consciousness bus...")
        self.is_running = False
        self.shutdown_event.set()
        
        # Cancel background tasks
        if self.health_check_task:
            self.health_check_task.cancel()
        if self.metrics_task:
            self.metrics_task.cancel()
        
        # Cancel processing workers
        for worker in self.processing_workers:
            worker.cancel()
        
        # Wait for workers to finish
        if self.processing_workers:
            await asyncio.gather(*self.processing_workers, return_exceptions=True)
        
        self.processing_workers.clear()
        self.logger.info("Consciousness bus stopped")
    
    async def publish(self, event: ConsciousnessEvent) -> bool:
        """Publish an event to the bus"""
        if not self.is_running:
            self.logger.error("Cannot publish event: consciousness bus not running")
            return False
        
        try:
            # Validate event
            if not event.source_component:
                raise ValueError("Event must have a source component")
            
            # Add to queue with priority
            priority_value = 10 - event.priority.value  # Higher priority = lower number
            queue_item = (priority_value, time.time(), event)
            
            # Try to add to queue (non-blocking)
            try:
                self.event_queue.put_nowait(queue_item)
            except asyncio.QueueFull:
                self.logger.warning(f"Event queue full, dropping event {event.event_id}")
                async with self.metrics_lock:
                    self.metrics.dropped_events += 1
                return False
            
            # Update metrics
            async with self.metrics_lock:
                self.metrics.total_events += 1
                self.metrics.events_by_type[event.event_type] += 1
                self.metrics.events_by_priority[event.priority] += 1
            
            # Add to history
            self.event_history.append({
                'event_id': event.event_id,
                'event_type': event.event_type.value,
                'source': event.source_component,
                'timestamp': event.timestamp.isoformat(),
                'priority': event.priority.value
            })
            
            self.logger.debug(f"Published event {event.event_id} from {event.source_component}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to publish event: {e}")
            return False
    
    async def subscribe(self, 
                       event_type: EventType,
                       handler: Callable[[ConsciousnessEvent], Awaitable[None]],
                       component_id: str) -> str:
        """Subscribe to events of a specific type"""
        
        subscription_id = str(uuid.uuid4())
        
        subscription = Subscription(
            subscription_id=subscription_id,
            component_id=component_id,
            event_type=event_type,
            handler=handler
        )
        
        # Add to subscription tracking
        self.subscriptions[event_type].add(subscription)
        self.component_subscriptions[component_id].add(subscription)
        self.subscription_lookup[subscription_id] = subscription
        
        self.logger.info(f"Component {component_id} subscribed to {event_type.value} events")
        return subscription_id
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events"""
        
        subscription = self.subscription_lookup.get(subscription_id)
        if not subscription:
            return False
        
        # Remove from all tracking structures
        self.subscriptions[subscription.event_type].discard(subscription)
        self.component_subscriptions[subscription.component_id].discard(subscription)
        del self.subscription_lookup[subscription_id]
        
        self.logger.info(f"Unsubscribed {subscription_id} for component {subscription.component_id}")
        return True
    
    async def register_component(self, component_status: ComponentStatus) -> bool:
        """Register a component with the bus"""
        
        self.registered_components[component_status.component_id] = component_status
        self.component_heartbeats[component_status.component_id] = datetime.now()
        
        self.logger.info(f"Registered component {component_status.component_id}")
        return True
    
    async def update_component_heartbeat(self, component_id: str) -> bool:
        """Update component heartbeat"""
        
        if component_id not in self.registered_components:
            return False
        
        self.component_heartbeats[component_id] = datetime.now()
        self.registered_components[component_id].last_heartbeat = datetime.now()
        
        return True
    
    async def get_consciousness_state(self) -> Optional[ConsciousnessState]:
        """Get current consciousness state"""
        async with self.state_lock:
            return self.consciousness_state
    
    async def update_consciousness_state(self, 
                                       component_id: str,
                                       state_updates: Dict[str, Any]) -> bool:
        """Update consciousness state"""
        
        async with self.state_lock:
            if self.consciousness_state is None:
                from .data_models import create_default_consciousness_state
                self.consciousness_state = create_default_consciousness_state()
            
            # Apply updates based on component
            try:
                if 'consciousness_level' in state_updates:
                    self.consciousness_state.update_consciousness_level(
                        state_updates['consciousness_level']
                    )
                
                if 'neural_populations' in state_updates:
                    for pop_id, pop_data in state_updates['neural_populations'].items():
                        if pop_id in self.consciousness_state.neural_populations:
                            pop = self.consciousness_state.neural_populations[pop_id]
                            for key, value in pop_data.items():
                                if hasattr(pop, key):
                                    setattr(pop, key, value)
                
                if 'user_contexts' in state_updates:
                    for user_id, context_data in state_updates['user_contexts'].items():
                        if user_id in self.consciousness_state.user_contexts:
                            context = self.consciousness_state.user_contexts[user_id]
                            for key, value in context_data.items():
                                if hasattr(context, key):
                                    setattr(context, key, value)
                
                # Update timestamp
                self.consciousness_state.timestamp = datetime.now()
                
                self.logger.debug(f"Updated consciousness state from {component_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to update consciousness state: {e}")
                return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get bus performance metrics"""
        async with self.metrics_lock:
            return {
                'total_events': self.metrics.total_events,
                'events_by_type': {k.value: v for k, v in self.metrics.events_by_type.items()},
                'events_by_priority': {k.value: v for k, v in self.metrics.events_by_priority.items()},
                'average_processing_time_ms': self.metrics.average_processing_time_ms,
                'failed_events': self.metrics.failed_events,
                'retried_events': self.metrics.retried_events,
                'dropped_events': self.metrics.dropped_events,
                'events_per_second': self.metrics.events_per_second,
                'peak_events_per_second': self.metrics.peak_events_per_second,
                'queue_size': self.event_queue.qsize(),
                'max_queue_size': self.max_queue_size,
                'active_subscriptions': len(self.subscription_lookup),
                'registered_components': len(self.registered_components),
                'is_running': self.is_running
            }
    
    async def get_component_health(self) -> Dict[str, Any]:
        """Get health status of all registered components"""
        health_status = {}
        current_time = datetime.now()
        
        for comp_id, component in self.registered_components.items():
            last_heartbeat = self.component_heartbeats.get(comp_id, component.last_heartbeat)
            time_since_heartbeat = (current_time - last_heartbeat).total_seconds()
            
            health_status[comp_id] = {
                'component_type': component.component_type,
                'state': component.state.value,
                'health_score': component.health_score,
                'last_heartbeat': last_heartbeat.isoformat(),
                'seconds_since_heartbeat': time_since_heartbeat,
                'is_responsive': time_since_heartbeat < 60,
                'subscription_count': len(self.component_subscriptions.get(comp_id, set())),
                'error_rate': component.error_rate,
                'response_time_ms': component.response_time_ms
            }
        
        return health_status
    
    async def _event_processing_worker(self, worker_id: str) -> None:
        """Event processing worker"""
        self.logger.debug(f"Started event processing worker {worker_id}")
        
        while self.is_running and not self.shutdown_event.is_set():
            try:
                # Get event from queue with timeout
                try:
                    priority, timestamp, event = await asyncio.wait_for(
                        self.event_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Process the event
                start_time = time.time()
                success = await self._process_event(event)
                processing_time = (time.time() - start_time) * 1000  # ms
                
                # Update metrics
                async with self.metrics_lock:
                    if success:
                        # Update average processing time
                        current_avg = self.metrics.average_processing_time_ms
                        total_events = self.metrics.total_events
                        self.metrics.average_processing_time_ms = (
                            (current_avg * (total_events - 1) + processing_time) / total_events
                        )
                    else:
                        self.metrics.failed_events += 1
                
                # Mark event as processed
                event.mark_processed(processing_time)
                
                # Mark task as done
                self.event_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Error in event processing worker {worker_id}: {e}")
                await asyncio.sleep(1.0)
        
        self.logger.debug(f"Event processing worker {worker_id} stopped")
    
    async def _process_event(self, event: ConsciousnessEvent) -> bool:
        """Process a single event"""
        try:
            # Find subscribers for this event type
            subscribers = self.subscriptions.get(event.event_type, set())
            
            # Filter by target components if specified
            if event.target_components and "all" not in event.target_components:
                subscribers = {
                    sub for sub in subscribers 
                    if sub.component_id in event.target_components
                }
            
            if not subscribers:
                self.logger.debug(f"No subscribers for event {event.event_id}")
                return True
            
            # Process event for each subscriber
            tasks = []
            for subscription in subscribers:
                task = asyncio.create_task(
                    self._handle_subscription(subscription, event)
                )
                tasks.append(task)
            
            # Wait for all handlers to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check for errors
            success_count = 0
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    subscription = list(subscribers)[i]
                    self.logger.error(
                        f"Handler error for {subscription.component_id}: {result}"
                    )
                    subscription.error_count += 1
                else:
                    success_count += 1
            
            self.logger.debug(
                f"Processed event {event.event_id}: {success_count}/{len(subscribers)} handlers succeeded"
            )
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Failed to process event {event.event_id}: {e}")
            
            # Retry if allowed
            if event.should_retry():
                event.increment_retry()
                await self.publish(event)
                async with self.metrics_lock:
                    self.metrics.retried_events += 1
            
            return False
    
    async def _handle_subscription(self, subscription: Subscription, event: ConsciousnessEvent) -> None:
        """Handle event for a specific subscription"""
        try:
            # Update subscription metrics
            subscription.last_triggered = datetime.now()
            subscription.trigger_count += 1
            
            # Call the handler
            await subscription.handler(event)
            
        except Exception as e:
            subscription.error_count += 1
            raise e
    
    async def _health_check_loop(self) -> None:
        """Background health check loop"""
        while self.is_running and not self.shutdown_event.is_set():
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                self.logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks on all components"""
        current_time = datetime.now()
        unhealthy_components = []
        
        for comp_id, last_heartbeat in self.component_heartbeats.items():
            time_since_heartbeat = (current_time - last_heartbeat).total_seconds()
            
            # Check if component is unresponsive
            if time_since_heartbeat > 60:  # 1 minute timeout
                component = self.registered_components.get(comp_id)
                if component and component.state != ComponentState.FAILED:
                    component.state = ComponentState.FAILED
                    component.health_score = 0.0
                    unhealthy_components.append(comp_id)
                    
                    self.logger.warning(f"Component {comp_id} marked as failed (no heartbeat for {time_since_heartbeat:.1f}s)")
        
        # Publish health check events if needed
        if unhealthy_components:
            health_event = create_error_recovery_event(
                source_component="consciousness_bus",
                error_info={
                    "type": "component_health_failure",
                    "failed_components": unhealthy_components,
                    "timestamp": current_time.isoformat()
                }
            )
            await self.publish(health_event)
    
    async def _metrics_update_loop(self) -> None:
        """Background metrics update loop"""
        last_event_count = 0
        last_update_time = time.time()
        
        while self.is_running and not self.shutdown_event.is_set():
            try:
                current_time = time.time()
                time_diff = current_time - last_update_time
                
                async with self.metrics_lock:
                    # Calculate events per second
                    event_diff = self.metrics.total_events - last_event_count
                    if time_diff > 0:
                        current_eps = event_diff / time_diff
                        self.metrics.events_per_second = current_eps
                        
                        if current_eps > self.metrics.peak_events_per_second:
                            self.metrics.peak_events_per_second = current_eps
                
                last_event_count = self.metrics.total_events
                last_update_time = current_time
                
                await asyncio.sleep(self.metrics_update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in metrics update loop: {e}")
                await asyncio.sleep(self.metrics_update_interval)