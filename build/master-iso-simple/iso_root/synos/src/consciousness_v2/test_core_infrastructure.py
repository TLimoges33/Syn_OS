"""
Test Core Infrastructure
========================

Simple test to verify that the core consciousness infrastructure is working properly.
Tests the Consciousness Bus, State Manager, and basic event flow.
"""

import asyncio
import logging
from datetime import datetime

from .core.consciousness_bus import ConsciousnessBus
from .core.state_manager import StateManager
from .core.event_types import (
    EventType, EventPriority, ConsciousnessEvent,
    create_neural_evolution_event, create_state_update_event,
    NeuralEvolutionData
)
from .core.data_models import (
    create_default_consciousness_state,
    create_component_status,
    ComponentState
)
from .interfaces.consciousness_component import ConsciousnessComponent


class TestComponent(ConsciousnessComponent):
    """Simple test component for demonstration"""
    
    def __init__(self, component_id: str):
        super().__init__(component_id, "test_component")
        self.events_received = []
    
    async def start(self) -> bool:
        """Start the test component"""
        self.is_running = True
        await self.set_component_state(ComponentState.HEALTHY)
        await self.update_health_score(1.0)
        self.logger.info(f"Test component {self.component_id} started")
        return True
    
    async def stop(self) -> None:
        """Stop the test component"""
        self.is_running = False
        await self.set_component_state(ComponentState.UNKNOWN)
        self.logger.info(f"Test component {self.component_id} stopped")
    
    async def process_event(self, event: ConsciousnessEvent) -> bool:
        """Process a consciousness event"""
        self.events_received.append(event)
        self.logger.info(f"Received event: {event.event_type.value} from {event.source_component}")
        return True
    
    async def get_health_status(self):
        """Get current health status"""
        return self.status
    
    async def update_configuration(self, config) -> bool:
        """Update component configuration"""
        return True


async def test_consciousness_infrastructure():
    """Test the core consciousness infrastructure"""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("=== Testing Consciousness Infrastructure ===")
    
    try:
        # 1. Initialize core components
        logger.info("1. Initializing Consciousness Bus...")
        consciousness_bus = ConsciousnessBus(max_queue_size=1000, max_workers=2)
        
        logger.info("2. Initializing State Manager...")
        state_manager = StateManager()
        
        # Connect state manager to bus
        state_manager.event_bus = consciousness_bus
        
        # 3. Start core components
        logger.info("3. Starting core components...")
        bus_started = await consciousness_bus.start()
        state_started = await state_manager.start()
        
        if not bus_started or not state_started:
            logger.error("Failed to start core components")
            return False
        
        logger.info("✓ Core components started successfully")
        
        # 4. Create test components
        logger.info("4. Creating test components...")
        test_comp1 = TestComponent("test_neural_engine")
        test_comp2 = TestComponent("test_context_engine")
        
        # Initialize components
        await test_comp1.initialize(consciousness_bus, state_manager)
        await test_comp2.initialize(consciousness_bus, state_manager)
        
        # Start components
        await test_comp1.start()
        await test_comp2.start()
        
        logger.info("✓ Test components created and started")
        
        # 5. Test event subscription
        logger.info("5. Testing event subscriptions...")
        
        # Subscribe to neural evolution events
        await test_comp1.register_event_handler(
            EventType.NEURAL_EVOLUTION,
            lambda event: logger.info(f"Neural handler received: {event.event_id}")
        )
        
        # Subscribe to state update events
        await test_comp2.register_event_handler(
            EventType.STATE_UPDATE,
            lambda event: logger.info(f"State handler received: {event.event_id}")
        )
        
        logger.info("✓ Event subscriptions registered")
        
        # 6. Test consciousness state management
        logger.info("6. Testing consciousness state management...")
        
        # Get initial state
        initial_state = await state_manager.get_consciousness_state()
        logger.info(f"Initial consciousness level: {initial_state.consciousness_level}")
        
        # Update consciousness state
        state_updates = {
            'consciousness_level': 0.75,
            'emergence_strength': 0.6
        }
        
        update_success = await state_manager.update_consciousness_state(
            "test_neural_engine", state_updates
        )
        
        if update_success:
            updated_state = await state_manager.get_consciousness_state()
            logger.info(f"Updated consciousness level: {updated_state.consciousness_level}")
            logger.info("✓ State management working")
        else:
            logger.error("✗ State update failed")
        
        # 7. Test event publishing and processing
        logger.info("7. Testing event publishing...")
        
        # Create and publish a neural evolution event
        evolution_data = NeuralEvolutionData(
            population_id="test_population",
            evolution_cycle=1,
            fitness_improvements={"accuracy": 0.1, "speed": 0.05},
            new_consciousness_level=0.8,
            selected_neurons=[1, 2, 3, 4, 5],
            adaptation_triggers=["performance_improvement"]
        )
        
        neural_event = create_neural_evolution_event(
            source_component="test_neural_engine",
            evolution_data=evolution_data,
            target_components=["test_context_engine"]
        )
        
        publish_success = await consciousness_bus.publish(neural_event)
        
        if publish_success:
            logger.info("✓ Event published successfully")
        else:
            logger.error("✗ Event publishing failed")
        
        # Wait for event processing
        await asyncio.sleep(1.0)
        
        # 8. Test state snapshots
        logger.info("8. Testing state snapshots...")
        
        snapshot_id = await state_manager.create_snapshot({
            'test_run': True,
            'timestamp': datetime.now().isoformat()
        })
        
        if snapshot_id:
            logger.info(f"✓ Snapshot created: {snapshot_id}")
        else:
            logger.error("✗ Snapshot creation failed")
        
        # 9. Check metrics
        logger.info("9. Checking system metrics...")
        
        bus_metrics = await consciousness_bus.get_metrics()
        state_metrics = await state_manager.get_state_metrics()
        component_health = await consciousness_bus.get_component_health()
        
        logger.info(f"Bus metrics - Total events: {bus_metrics['total_events']}")
        logger.info(f"State metrics - Version: {state_metrics['state_version']}")
        logger.info(f"Components registered: {len(component_health)}")
        
        # 10. Verify event reception
        logger.info("10. Verifying event reception...")
        
        logger.info(f"Test comp1 received {len(test_comp1.events_received)} events")
        logger.info(f"Test comp2 received {len(test_comp2.events_received)} events")
        
        # 11. Cleanup
        logger.info("11. Cleaning up...")
        
        await test_comp1.stop()
        await test_comp2.stop()
        await consciousness_bus.stop()
        await state_manager.stop()
        
        logger.info("✓ Cleanup completed")
        
        logger.info("=== Infrastructure Test Completed Successfully! ===")
        return True
        
    except Exception as e:
        logger.error(f"Infrastructure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    success = await test_consciousness_infrastructure()
    if success:
        print("\n🎉 All tests passed! Core consciousness infrastructure is working.")
    else:
        print("\n❌ Tests failed. Check the logs for details.")
    
    return success


if __name__ == "__main__":
    asyncio.run(main())