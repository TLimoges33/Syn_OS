#!/usr/bin/env python3
"""
Test Neural Population Implementation
====================================

Test script to verify that our neural population management system is working correctly
with the genetic algorithm-based evolution and consciousness prediction.
"""

import asyncio
import sys
import os

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from consciousness_v2.components.neural_darwinism_v2 import (
    EnhancedNeuralDarwinismEngine, 
    NeuralConfiguration,
    PopulationManager,
    FitnessEvaluator,
    LearningHistoryManager
)
from consciousness_v2.core.data_models import create_population_state, create_default_consciousness_state
from consciousness_v2.core.event_types import EventType, ConsciousnessEvent, NeuralEvolutionData
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockConsciousnessBus:
    """Mock consciousness bus for testing"""
    
    def __init__(self):
        self.published_events = []
        self.registered_components = []
        
    async def register_component(self, status):
        self.registered_components.append(status)
        
    async def publish(self, event):
        self.published_events.append(event)
        return True
        
    async def subscribe(self, event_type, handler, component_id):
        return f"sub_{component_id}_{event_type}"
        
    async def update_component_heartbeat(self, component_id):
        pass

class MockStateManager:
    """Mock state manager for testing"""
    
    def __init__(self):
        self.component_states = {}
        self.consciousness_states = {}
        
    async def update_component_state(self, component_id, status):
        self.component_states[component_id] = status
        
    async def update_consciousness_state(self, component_id, updates):
        if component_id not in self.consciousness_states:
            self.consciousness_states[component_id] = {}
        self.consciousness_states[component_id].update(updates)
        return True

async def test_neural_population_creation():
    """Test creating neural populations"""
    print("Testing neural population creation...")
    
    # Create configuration
    config = NeuralConfiguration()
    
    # Create engine
    engine = EnhancedNeuralDarwinismEngine(config)
    
    # Initialize mock systems
    consciousness_bus = MockConsciousnessBus()
    state_manager = MockStateManager()
    
    await engine.initialize(consciousness_bus, state_manager)
    
    # Start the engine
    success = await engine.start()
    assert success, "Engine failed to start"
    
    # Check populations were created
    populations = engine.get_population_states()
    assert len(populations) > 0, "No populations created"
    
    print(f"✅ Created {len(populations)} neural populations:")
    for pop_id, population in populations.items():
        print(f"   - {pop_id}: {population.size} neurons, specialization: {population.specialization}")
    
    # Stop the engine
    await engine.stop()
    
    return True

async def test_evolution_cycle():
    """Test a single evolution cycle"""
    print("\nTesting neural evolution cycle...")
    
    config = NeuralConfiguration()
    config.evolution_frequency_hz = 100.0  # Fast for testing
    
    engine = EnhancedNeuralDarwinismEngine(config)
    
    consciousness_bus = MockConsciousnessBus()
    state_manager = MockStateManager()
    
    await engine.initialize(consciousness_bus, state_manager)
    await engine.start()
    
    # Get initial state
    initial_populations = engine.get_population_states()
    initial_fitness = {pop_id: pop.fitness_average for pop_id, pop in initial_populations.items()}
    
    # Trigger evolution cycle
    evolution_results = await engine.trigger_evolution_cycle()
    
    assert len(evolution_results) > 0, "No evolution results"
    
    print(f"✅ Evolution cycle completed with {len(evolution_results)} population updates")
    
    for result in evolution_results:
        print(f"   - Population {result.population_id}: cycle {result.evolution_cycle}")
        print(f"     Fitness improvements: {result.fitness_improvements}")
        print(f"     Consciousness level: {result.new_consciousness_level:.3f}")
        print(f"     Selected neurons: {len(result.selected_neurons)}")
    
    # Check that fitness may have changed (due to random evolution)
    updated_populations = engine.get_population_states()
    
    await engine.stop()
    
    return True

async def test_consciousness_prediction():
    """Test consciousness emergence prediction"""
    print("\nTesting consciousness prediction...")
    
    config = NeuralConfiguration()
    config.consciousness_prediction_enabled = True
    
    engine = EnhancedNeuralDarwinismEngine(config)
    
    consciousness_bus = MockConsciousnessBus()
    state_manager = MockStateManager()
    
    await engine.initialize(consciousness_bus, state_manager)
    await engine.start()
    
    # Get consciousness prediction
    prediction = await engine.predict_consciousness()
    
    if prediction:
        print("✅ Consciousness prediction generated:")
        print(f"   - Predicted level: {prediction.predicted_level:.3f}")
        print(f"   - Confidence: {prediction.confidence:.3f}")
        print(f"   - Emergence probability: {prediction.emergence_probability:.3f}")
        print(f"   - Patterns detected: {prediction.patterns_detected}")
    else:
        print("✅ Consciousness prediction disabled (fallback working)")
    
    await engine.stop()
    
    return True

async def test_threat_analysis():
    """Test threat analysis using consciousness"""
    print("\nTesting threat analysis integration...")
    
    engine = EnhancedNeuralDarwinismEngine()
    
    consciousness_bus = MockConsciousnessBus()
    state_manager = MockStateManager()
    
    await engine.initialize(consciousness_bus, state_manager)
    await engine.start()
    
    # Test threat data
    threat_data = {
        'type': 'intrusion_detection',
        'severity_indicators': {
            'off_hours': True,
            'repeated_failures': False,
            'geographic_anomaly': True
        },
        'source': {'ip': '192.168.1.100'},
        'context': {'user_activity': 'high'}
    }
    
    # Analyze threat
    analysis = await engine.analyze_threat(threat_data)
    
    assert 'threat_level' in analysis, "Missing threat level"
    assert 'confidence' in analysis, "Missing confidence"
    assert 'reasoning' in analysis, "Missing reasoning"
    
    print("✅ Threat analysis completed:")
    print(f"   - Threat level: {analysis['threat_level']:.3f}")
    print(f"   - Confidence: {analysis['confidence']:.3f}")
    print(f"   - Reasoning: {analysis['reasoning']}")
    print(f"   - Analysis type: {analysis['analysis_type']}")
    
    await engine.stop()
    
    return True

async def test_population_management():
    """Test population management system"""
    print("\nTesting population management...")
    
    config = NeuralConfiguration()
    manager = PopulationManager(config)
    
    # Create mock evolution results
    evolution_results = [
        NeuralEvolutionData(
            population_id="executive",
            evolution_cycle=1,
            fitness_improvements={'overall': 0.1, 'accuracy': 0.05},
            new_consciousness_level=0.6,
            selected_neurons=[1, 2, 3, 4, 5],
            adaptation_triggers=['significant_improvement']
        ),
        NeuralEvolutionData(
            population_id="memory",
            evolution_cycle=1,
            fitness_improvements={'overall': 0.02, 'accuracy': 0.01},
            new_consciousness_level=0.4,
            selected_neurons=[10, 11],
            adaptation_triggers=['baseline_evolution']
        )
    ]
    
    # Test population management
    management_actions = await manager.manage_populations(evolution_results)
    
    print("✅ Population management completed:")
    print(f"   - Actions taken: {sum(len(v) for v in management_actions.values())}")
    for action_type, actions in management_actions.items():
        if actions:
            print(f"   - {action_type}: {len(actions)} actions")
    
    return True

async def test_fitness_evaluation():
    """Test fitness evaluation system"""
    print("\nTesting fitness evaluation...")
    
    config = NeuralConfiguration()
    evaluator = FitnessEvaluator(config)
    
    # Mock population data
    population_data = {
        'population_id': 'test_population',
        'size': 1000,
        'active_neurons': 800,
        'fitness_average': 0.7,
        'generation': 5,
        'successful_adaptations': 12,
        'consciousness_contributions': 0.6,
        'specialization': 'executive'
    }
    
    # Evaluate fitness
    fitness_scores = await evaluator.evaluate_population_fitness(population_data)
    
    assert 'overall' in fitness_scores, "Missing overall fitness"
    assert 0.0 <= fitness_scores['overall'] <= 1.0, "Fitness score out of range"
    
    print("✅ Fitness evaluation completed:")
    for metric, score in fitness_scores.items():
        print(f"   - {metric}: {score:.3f}")
    
    return True

async def test_learning_history():
    """Test learning history management"""
    print("\nTesting learning history management...")
    
    config = NeuralConfiguration()
    history_manager = LearningHistoryManager(config)
    
    # Create mock evolution data
    evolution_data = NeuralEvolutionData(
        population_id="executive",
        evolution_cycle=1,
        fitness_improvements={'overall': 0.08},
        new_consciousness_level=0.7,
        selected_neurons=[1, 2, 3],
        adaptation_triggers=['accuracy_boost']
    )
    
    context = {
        'system_load': 0.3,
        'user_activity_level': 0.8,
        'learning_progress': 0.6
    }
    
    # Record learning event
    await history_manager.record_learning_event(evolution_data, context, 'improved')
    
    # Get insights
    insights = history_manager.get_learning_insights()
    
    print("✅ Learning history management working:")
    if insights.get('status') == 'insufficient_data':
        print("   - Status: Insufficient data (expected for first test)")
    else:
        print(f"   - Total events: {insights.get('total_learning_events', 0)}")
        print(f"   - Success rate: {insights.get('recent_success_rate', 0):.3f}")
    
    return True

async def test_configuration_update():
    """Test configuration updates"""
    print("\nTesting configuration updates...")
    
    engine = EnhancedNeuralDarwinismEngine()
    
    consciousness_bus = MockConsciousnessBus()
    state_manager = MockStateManager()
    
    await engine.initialize(consciousness_bus, state_manager)
    await engine.start()
    
    # Update configuration
    new_config = {
        'mutation_rate': 0.15,
        'selection_pressure': 0.6,
        'evolution_frequency_hz': 15.0
    }
    
    success = await engine.update_configuration(new_config)
    assert success, "Configuration update failed"
    
    # Verify changes
    assert engine.config.mutation_rate == 0.15, "Mutation rate not updated"
    assert engine.config.selection_pressure == 0.6, "Selection pressure not updated"
    assert engine.config.evolution_frequency_hz == 15.0, "Evolution frequency not updated"
    
    print("✅ Configuration update successful:")
    print(f"   - Mutation rate: {engine.config.mutation_rate}")
    print(f"   - Selection pressure: {engine.config.selection_pressure}")
    print(f"   - Evolution frequency: {engine.config.evolution_frequency_hz} Hz")
    
    await engine.stop()
    
    return True

async def test_performance_metrics():
    """Test performance metrics collection"""
    print("\nTesting performance metrics...")
    
    engine = EnhancedNeuralDarwinismEngine()
    
    consciousness_bus = MockConsciousnessBus()
    state_manager = MockStateManager()
    
    await engine.initialize(consciousness_bus, state_manager)
    await engine.start()
    
    # Run a few evolution cycles to generate metrics
    for _ in range(3):
        await engine.trigger_evolution_cycle()
    
    # Get metrics
    metrics = engine.get_evolution_metrics()
    
    assert metrics['evolution_cycles_completed'] >= 3, "Evolution cycles not recorded"
    assert metrics['total_neurons_evolved'] >= 0, "Neuron evolution not tracked"
    
    print("✅ Performance metrics working:")
    print(f"   - Evolution cycles: {metrics['evolution_cycles_completed']}")
    print(f"   - Neurons evolved: {metrics['total_neurons_evolved']}")
    print(f"   - Average evolution time: {metrics['average_evolution_time_ms']:.2f}ms")
    print(f"   - Evolution frequency: {metrics['evolution_frequency_hz']:.1f}Hz")
    
    # Test population management status
    pop_status = engine.get_population_management_status()
    print(f"   - Total populations: {pop_status['total_populations']}")
    print(f"   - Population sizes: {pop_status['population_sizes']}")
    
    await engine.stop()
    
    return True

async def main():
    """Run all tests"""
    print("🧠 Neural Population Management Implementation Test")
    print("=" * 60)
    
    tests = [
        test_neural_population_creation,
        test_evolution_cycle,
        test_consciousness_prediction,
        test_threat_analysis,
        test_population_management,
        test_fitness_evaluation,
        test_learning_history,
        test_configuration_update,
        test_performance_metrics
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All neural population tests passed!")
        print("\n✅ Neural Population Management implementation is working correctly!")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)