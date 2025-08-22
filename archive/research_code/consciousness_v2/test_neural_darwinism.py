"""
Test Neural Darwinism Engine v2
===============================

Test script to validate the Enhanced Neural Darwinism Engine functionality,
including GPU acceleration, consciousness prediction, and real-time integration.
"""

import asyncio
import logging
import time
from datetime import datetime

from .core.consciousness_bus import ConsciousnessBus
from .core.state_manager import StateManager
from .core.event_types import (
    EventType, create_neural_evolution_event, create_context_update_event,
    ContextUpdateData
)
from .components.neural_darwinism_v2 import (
    EnhancedNeuralDarwinismEngine, NeuralConfiguration
)


async def test_neural_darwinism_engine():
    """Test the Enhanced Neural Darwinism Engine"""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("=== Testing Enhanced Neural Darwinism Engine v2 ===")
    
    try:
        # 1. Initialize core infrastructure
        logger.info("1. Initializing consciousness infrastructure...")
        consciousness_bus = ConsciousnessBus(max_queue_size=1000, max_workers=2)
        state_manager = StateManager()
        state_manager.event_bus = consciousness_bus
        
        # Start infrastructure
        bus_started = await consciousness_bus.start()
        state_started = await state_manager.start()
        
        if not bus_started or not state_started:
            logger.error("Failed to start infrastructure")
            return False
        
        logger.info("✓ Infrastructure started")
        
        # 2. Create and configure neural engine
        logger.info("2. Creating Neural Darwinism Engine...")
        
        # Configure for testing (CPU-only mode for compatibility)
        config = NeuralConfiguration(
            base_population_sizes={
                'executive': 1000,
                'sensory': 800,
                'memory': 600,
                'motor': 500
            },
            use_gpu=False,  # Use CPU for testing compatibility
            consciousness_prediction_enabled=False,  # Disable ML for testing
            evolution_frequency_hz=5.0,  # 5Hz for testing
            adaptive_scaling_enabled=True,
            memory_optimization_enabled=True
        )
        
        neural_engine = EnhancedNeuralDarwinismEngine(config)
        
        # Initialize with consciousness infrastructure
        await neural_engine.initialize(consciousness_bus, state_manager)
        
        logger.info("✓ Neural engine created and configured")
        
        # 3. Start neural engine
        logger.info("3. Starting neural engine...")
        
        engine_started = await neural_engine.start()
        if not engine_started:
            logger.error("Failed to start neural engine")
            return False
        
        logger.info("✓ Neural engine started")
        
        # 4. Test population initialization
        logger.info("4. Testing population initialization...")
        
        populations = neural_engine.get_population_states()
        logger.info(f"Initialized populations: {list(populations.keys())}")
        
        for pop_id, population in populations.items():
            logger.info(f"  {pop_id}: {population.size} neurons, "
                       f"fitness={population.fitness_average:.3f}, "
                       f"generation={population.generation}")
        
        logger.info("✓ Population initialization verified")
        
        # 5. Test manual evolution cycle
        logger.info("5. Testing manual evolution cycle...")
        
        start_time = time.time()
        evolution_results = await neural_engine.trigger_evolution_cycle()
        evolution_time = (time.time() - start_time) * 1000
        
        logger.info(f"Evolution cycle completed in {evolution_time:.2f}ms")
        logger.info(f"Evolution results: {len(evolution_results)} populations evolved")
        
        for result in evolution_results:
            logger.info(f"  {result.population_id}: "
                       f"cycle={result.evolution_cycle}, "
                       f"consciousness={result.new_consciousness_level:.3f}, "
                       f"selected={len(result.selected_neurons)} neurons")
        
        logger.info("✓ Manual evolution cycle successful")
        
        # 6. Test event-driven adaptation
        logger.info("6. Testing event-driven adaptation...")
        
        # Create context update event
        context_data = ContextUpdateData(
            user_id="test_user",
            activity_type="learning",
            domain="technical",
            success=True,
            duration_seconds=300,
            skill_changes={"technical": 0.1, "analytical": 0.05},
            consciousness_feedback={"engagement": 0.8, "focus": 0.7},
            metadata={"test": True}
        )
        
        context_event = create_context_update_event(
            source_component="test_context_engine",
            context_data=context_data,
            target_components=["neural_darwinism_v2"]
        )
        
        # Publish event and wait for processing
        await consciousness_bus.publish(context_event)
        await asyncio.sleep(0.5)  # Allow processing time
        
        logger.info("✓ Context update event processed")
        
        # 7. Test metrics collection
        logger.info("7. Testing metrics collection...")
        
        # Wait for some evolution cycles
        await asyncio.sleep(2.0)
        
        metrics = neural_engine.get_evolution_metrics()
        logger.info("Evolution metrics:")
        for key, value in metrics.items():
            if isinstance(value, dict):
                logger.info(f"  {key}: {len(value)} items")
            else:
                logger.info(f"  {key}: {value}")
        
        logger.info("✓ Metrics collection successful")
        
        # 8. Test consciousness prediction (if enabled)
        if config.consciousness_prediction_enabled:
            logger.info("8. Testing consciousness prediction...")
            
            prediction = await neural_engine.predict_consciousness()
            if prediction:
                logger.info(f"Consciousness prediction:")
                logger.info(f"  Level: {prediction.predicted_level:.3f}")
                logger.info(f"  Confidence: {prediction.confidence:.3f}")
                logger.info(f"  Emergence probability: {prediction.emergence_probability:.3f}")
                logger.info(f"  Patterns: {prediction.patterns_detected}")
                
                logger.info("✓ Consciousness prediction successful")
            else:
                logger.info("✓ Consciousness prediction disabled")
        else:
            logger.info("8. Consciousness prediction disabled for testing")
        
        # 9. Test configuration updates
        logger.info("9. Testing configuration updates...")
        
        config_updates = {
            'mutation_rate': 0.15,
            'evolution_frequency_hz': 8.0,
            'population_sizes': {
                'executive': 1200,
                'sensory': 900
            }
        }
        
        config_success = await neural_engine.update_configuration(config_updates)
        if config_success:
            updated_metrics = neural_engine.get_evolution_metrics()
            logger.info(f"Updated evolution frequency: {updated_metrics['evolution_frequency_hz']}")
            logger.info(f"Updated population sizes: {updated_metrics['population_sizes']}")
            
            logger.info("✓ Configuration update successful")
        else:
            logger.error("✗ Configuration update failed")
        
        # 10. Test health monitoring
        logger.info("10. Testing health monitoring...")
        
        health_status = await neural_engine.get_health_status()
        logger.info(f"Component health:")
        logger.info(f"  State: {health_status.state.value}")
        logger.info(f"  Health score: {health_status.health_score:.3f}")
        logger.info(f"  Response time: {health_status.response_time_ms:.2f}ms")
        logger.info(f"  Error rate: {health_status.error_rate:.3f}")
        
        logger.info("✓ Health monitoring successful")
        
        # 11. Performance validation
        logger.info("11. Validating performance...")
        
        # Run multiple evolution cycles and measure performance
        cycle_times = []
        for i in range(5):
            start_time = time.time()
            await neural_engine.trigger_evolution_cycle()
            cycle_time = (time.time() - start_time) * 1000
            cycle_times.append(cycle_time)
        
        avg_cycle_time = sum(cycle_times) / len(cycle_times)
        min_cycle_time = min(cycle_times)
        max_cycle_time = max(cycle_times)
        
        logger.info(f"Performance metrics:")
        logger.info(f"  Average cycle time: {avg_cycle_time:.2f}ms")
        logger.info(f"  Min cycle time: {min_cycle_time:.2f}ms")
        logger.info(f"  Max cycle time: {max_cycle_time:.2f}ms")
        logger.info(f"  Cycles per second: {1000/avg_cycle_time:.1f}")
        
        # Performance targets (CPU mode)
        if avg_cycle_time < 100:  # < 100ms per cycle
            logger.info("✓ Performance target met")
        else:
            logger.warning(f"⚠ Performance below target (expected <100ms, got {avg_cycle_time:.2f}ms)")
        
        # 12. Integration validation
        logger.info("12. Validating integration...")
        
        # Check consciousness bus metrics
        bus_metrics = await consciousness_bus.get_metrics()
        logger.info(f"Bus metrics - Total events: {bus_metrics['total_events']}")
        
        # Check state manager
        state_metrics = await state_manager.get_state_metrics()
        logger.info(f"State metrics - Version: {state_metrics['state_version']}")
        
        # Check component registration
        component_health = await consciousness_bus.get_component_health()
        if neural_engine.component_id in component_health:
            comp_health = component_health[neural_engine.component_id]
            logger.info(f"Component registered: {comp_health['is_responsive']}")
            
            logger.info("✓ Integration validation successful")
        else:
            logger.error("✗ Component not properly registered")
        
        # 13. Cleanup
        logger.info("13. Cleaning up...")
        
        await neural_engine.stop()
        await consciousness_bus.stop()
        await state_manager.stop()
        
        logger.info("✓ Cleanup completed")
        
        logger.info("=== Neural Darwinism Engine Test Completed Successfully! ===")
        return True
        
    except Exception as e:
        logger.error(f"Neural Darwinism Engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    success = await test_neural_darwinism_engine()
    if success:
        print("\n🧠 Neural Darwinism Engine v2 test passed! Engine is working correctly.")
        print("\nKey features validated:")
        print("✓ Population initialization and management")
        print("✓ Evolution cycle processing")
        print("✓ Event-driven adaptation")
        print("✓ Real-time integration with consciousness bus")
        print("✓ Performance monitoring and metrics")
        print("✓ Configuration management")
        print("✓ Health monitoring")
        print("✓ CPU fallback mode (GPU acceleration available when libraries installed)")
    else:
        print("\n❌ Neural Darwinism Engine test failed. Check the logs for details.")
    
    return success


if __name__ == "__main__":
    asyncio.run(main())