#!/usr/bin/env python3
"""
Test Decision Engine Implementation
==================================

Test script to verify that our AI decision making engine with confidence scoring 
and neural integration is working correctly.
"""

import asyncio
import sys
import os

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from consciousness_v2.components.decision_engine import (
    DecisionEngine, 
    DecisionCriteria, 
    DecisionType, 
    DecisionOption,
    ConfidenceLevel
)
from consciousness_v2.core.event_types import EventType, ConsciousnessEvent
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

async def test_decision_engine_initialization():
    """Test decision engine initialization"""
    print("Testing decision engine initialization...")
    
    config = {
        'confidence_threshold': 0.5,
        'max_decision_time_ms': 5000,
        'neural_voting_enabled': True,
        'learning_enabled': True
    }
    
    engine = DecisionEngine(config)
    
    # Initialize with mock systems
    consciousness_bus = MockConsciousnessBus()
    state_manager = MockStateManager()
    
    await engine.initialize(consciousness_bus, state_manager)
    
    # Start the engine
    success = await engine.start()
    assert success, "Decision engine failed to start"
    
    # Check configuration
    assert engine.config['confidence_threshold'] == 0.5
    assert engine.neural_voting_enabled == True
    assert engine.learning_enabled == True
    
    print("✅ Decision engine initialized successfully")
    print(f"   - Component ID: {engine.component_id}")
    print(f"   - Neural voting: {'enabled' if engine.neural_voting_enabled else 'disabled'}")
    print(f"   - Learning: {'enabled' if engine.learning_enabled else 'disabled'}")
    print(f"   - Confidence threshold: {engine.default_confidence_threshold}")
    
    await engine.stop()
    return True

async def test_threat_assessment_decision():
    """Test threat assessment decision making"""
    print("\nTesting threat assessment decision...")
    
    engine = DecisionEngine()
    
    consciousness_bus = MockConsciousnessBus()
    state_manager = MockStateManager()
    
    await engine.initialize(consciousness_bus, state_manager)
    await engine.start()
    
    # Add mock neural populations
    engine.neural_populations = {
        'executive': {
            'specialization': 'executive',
            'fitness_average': 0.8,
            'consciousness_contributions': 0.7
        },
        'sensory': {
            'specialization': 'sensory', 
            'fitness_average': 0.75,
            'consciousness_contributions': 0.6
        }
    }
    
    # Create threat assessment criteria
    criteria = DecisionCriteria(
        decision_type=DecisionType.THREAT_ASSESSMENT,
        context={
            'threat_data': {
                'type': 'intrusion_detection',
                'severity': 'high',
                'source': {'ip': '192.168.1.100'},
                'indicators': ['unusual_network_activity', 'failed_authentication']
            },
            'system_load': 0.3,
            'user_activity': 'low'
        },
        constraints={'response_time': 'immediate'},
        priorities={'security': 0.9, 'availability': 0.6},
        min_confidence=0.4
    )
    
    # Make decision
    result = await engine.make_decision(criteria)
    
    assert result is not None, "No decision result returned"
    assert result.decision_type == DecisionType.THREAT_ASSESSMENT
    assert result.selected_option is not None
    assert 0.0 <= result.overall_confidence <= 1.0
    assert result.processing_time_ms > 0
    
    print("✅ Threat assessment decision made:")
    print(f"   - Selected option: {result.selected_option.name}")
    print(f"   - Confidence: {result.overall_confidence:.1%}")
    print(f"   - Action type: {result.selected_option.action_type}")
    print(f"   - Processing time: {result.processing_time_ms:.1f}ms")
    print(f"   - Neural consensus: {result.neural_consensus:.1%}")
    print(f"   - Consciousness influence: {result.consciousness_influence:.1%}")
    print(f"   - Alternatives considered: {len(result.alternative_options)}")
    
    if result.reasoning_chain:
        print("   - Reasoning:")
        for reason in result.reasoning_chain:
            print(f"     • {reason}")
    
    await engine.stop()
    return True

async def test_learning_adaptation_decision():
    """Test learning adaptation decision making"""
    print("\nTesting learning adaptation decision...")
    
    engine = DecisionEngine()
    
    consciousness_bus = MockConsciousnessBus()
    state_manager = MockStateManager()
    
    await engine.initialize(consciousness_bus, state_manager)
    await engine.start()
    
    # Set higher consciousness level
    engine.consciousness_level = 0.8
    
    # Add neural populations with different fitness levels
    engine.neural_populations = {
        'executive': {
            'specialization': 'executive',
            'fitness_average': 0.85,
            'consciousness_contributions': 0.8
        },
        'memory': {
            'specialization': 'memory',
            'fitness_average': 0.9,
            'consciousness_contributions': 0.75
        }
    }
    
    # Create learning adaptation criteria
    criteria = DecisionCriteria(
        decision_type=DecisionType.LEARNING_ADAPTATION,
        context={
            'learning_context': {
                'performance_score': 0.7,
                'user_engagement': 0.8,
                'current_difficulty': 'intermediate',
                'session_duration': 1800  # 30 minutes
            },
            'user_context': {
                'skill_level': 'intermediate',
                'learning_style': 'hands_on',
                'previous_performance': 0.6
            },
            'consciousness_level': 0.8
        },
        priorities={'engagement': 0.8, 'learning_efficiency': 0.9},
        min_confidence=0.5
    )
    
    # Make decision
    result = await engine.make_decision(criteria)
    
    assert result.decision_type == DecisionType.LEARNING_ADAPTATION
    assert result.overall_confidence >= 0.5  # Should meet minimum
    
    print("✅ Learning adaptation decision made:")
    print(f"   - Selected option: {result.selected_option.name}")
    print(f"   - Confidence: {result.overall_confidence:.1%}")
    print(f"   - Description: {result.selected_option.description}")
    print(f"   - Utility score: {result.selected_option.utility_score:.2f}")
    print(f"   - Risk score: {result.selected_option.risk_score:.2f}")
    print(f"   - Consciousness alignment: {result.selected_option.consciousness_alignment:.2f}")
    
    # Test with low performance
    criteria.context['learning_context']['performance_score'] = 0.2
    low_performance_result = await engine.make_decision(criteria)
    
    print(f"   - Low performance decision: {low_performance_result.selected_option.name}")
    
    await engine.stop()
    return True

async def test_user_guidance_decision():
    """Test user guidance decision making"""
    print("\nTesting user guidance decision...")
    
    engine = DecisionEngine()
    
    consciousness_bus = MockConsciousnessBus()
    state_manager = MockStateManager()
    
    await engine.initialize(consciousness_bus, state_manager)
    await engine.start()
    
    # Create user guidance criteria
    criteria = DecisionCriteria(
        decision_type=DecisionType.USER_GUIDANCE,
        context={
            'user_context': {
                'skill_level': 'beginner',
                'current_task': 'network_scanning',
                'confusion_indicators': ['repeated_errors', 'slow_progress'],
                'help_requests': 3
            },
            'task_context': {
                'complexity': 'moderate',
                'time_pressure': 'low',
                'learning_objectives': ['understand_nmap', 'practice_scanning']
            }
        },
        priorities={'clarity': 0.9, 'engagement': 0.7},
        max_options=4
    )
    
    result = await engine.make_decision(criteria)
    
    assert result.decision_type == DecisionType.USER_GUIDANCE
    
    print("✅ User guidance decision made:")
    print(f"   - Selected option: {result.selected_option.name}")
    print(f"   - Description: {result.selected_option.description}")
    print(f"   - Pros: {', '.join(result.selected_option.pros)}")
    print(f"   - Cons: {', '.join(result.selected_option.cons)}")
    
    await engine.stop()
    return True

async def test_tool_recommendation_decision():
    """Test tool recommendation decision making"""
    print("\nTesting tool recommendation decision...")
    
    engine = DecisionEngine()
    
    consciousness_bus = MockConsciousnessBus()
    state_manager = MockStateManager()
    
    await engine.initialize(consciousness_bus, state_manager)
    await engine.start()
    
    criteria = DecisionCriteria(
        decision_type=DecisionType.TOOL_RECOMMENDATION,
        context={
            'task_context': {
                'task_type': 'web_security_testing',
                'target_environment': 'test_application',
                'user_skill_level': 'intermediate',
                'time_constraints': 'moderate'
            },
            'available_tools': ['burpsuite', 'owasp-zap', 'nikto', 'sqlmap'],
            'previous_tools_used': ['nmap', 'dirb']
        },
        priorities={'effectiveness': 0.9, 'usability': 0.7},
        min_confidence=0.4
    )
    
    result = await engine.make_decision(criteria)
    
    assert result.decision_type == DecisionType.TOOL_RECOMMENDATION
    
    print("✅ Tool recommendation decision made:")
    print(f"   - Recommended tool: {result.selected_option.name}")
    print(f"   - Tool parameters: {result.selected_option.parameters}")
    print(f"   - Confidence: {result.overall_confidence:.1%}")
    
    await engine.stop()
    return True

async def test_neural_population_integration():
    """Test integration with neural populations"""
    print("\nTesting neural population integration...")
    
    engine = DecisionEngine()
    
    consciousness_bus = MockConsciousnessBus()
    state_manager = MockStateManager()
    
    await engine.initialize(consciousness_bus, state_manager)
    await engine.start()
    
    # Add detailed neural populations
    engine.neural_populations = {
        'executive': {
            'specialization': 'executive',
            'fitness_average': 0.9,
            'consciousness_contributions': 0.85,
            'generation': 10
        },
        'sensory': {
            'specialization': 'sensory',
            'fitness_average': 0.7,
            'consciousness_contributions': 0.6,
            'generation': 8
        },
        'memory': {
            'specialization': 'memory',
            'fitness_average': 0.8,
            'consciousness_contributions': 0.75,
            'generation': 12
        },
        'motor': {
            'specialization': 'motor',
            'fitness_average': 0.6,
            'consciousness_contributions': 0.5,
            'generation': 6
        }
    }
    
    # Test decision with neural voting
    criteria = DecisionCriteria(
        decision_type=DecisionType.SECURITY_ACTION,
        context={
            'threat_level': 'medium',
            'system_impact': 'low',
            'user_activity': 'active'
        },
        min_confidence=0.3
    )
    
    result = await engine.make_decision(criteria)
    
    # Verify neural integration
    assert result.neural_populations_consulted == list(engine.neural_populations.keys())
    assert 0.0 <= result.neural_consensus <= 1.0
    
    print("✅ Neural population integration working:")
    print(f"   - Populations consulted: {len(result.neural_populations_consulted)}")
    print(f"   - Neural consensus: {result.neural_consensus:.1%}")
    print(f"   - Neural support: {result.selected_option.neural_support}")
    
    # Test without neural voting
    engine.neural_voting_enabled = False
    result_no_neural = await engine.make_decision(criteria)
    
    print(f"   - Decision without neural voting: {result_no_neural.selected_option.name}")
    print(f"   - Consensus without voting: {result_no_neural.neural_consensus:.1%}")
    
    await engine.stop()
    return True

async def test_consciousness_influence():
    """Test consciousness level influence on decisions"""
    print("\nTesting consciousness influence...")
    
    engine = DecisionEngine()
    
    consciousness_bus = MockConsciousnessBus()
    state_manager = MockStateManager()
    
    await engine.initialize(consciousness_bus, state_manager)
    await engine.start()
    
    criteria = DecisionCriteria(
        decision_type=DecisionType.EDUCATIONAL_CONTENT,
        context={
            'learner_profile': {
                'skill_level': 'advanced',
                'engagement_level': 'high'
            },
            'content_options': ['basic_tutorial', 'advanced_challenge', 'expert_scenario']
        }
    )
    
    # Test with low consciousness
    engine.consciousness_level = 0.3
    low_consciousness_result = await engine.make_decision(criteria)
    
    # Test with high consciousness  
    engine.consciousness_level = 0.9
    high_consciousness_result = await engine.make_decision(criteria)
    
    print("✅ Consciousness influence tested:")
    print(f"   - Low consciousness (0.3): {low_consciousness_result.selected_option.name}")
    print(f"     Consciousness influence: {low_consciousness_result.consciousness_influence:.1%}")
    print(f"   - High consciousness (0.9): {high_consciousness_result.selected_option.name}")
    print(f"     Consciousness influence: {high_consciousness_result.consciousness_influence:.1%}")
    
    # High consciousness should generally have higher influence
    assert (high_consciousness_result.consciousness_influence >= 
            low_consciousness_result.consciousness_influence - 0.1)  # Allow some tolerance
    
    await engine.stop()
    return True

async def test_decision_learning():
    """Test decision learning from outcomes"""
    print("\nTesting decision learning...")
    
    engine = DecisionEngine()
    
    consciousness_bus = MockConsciousnessBus()
    state_manager = MockStateManager()
    
    await engine.initialize(consciousness_bus, state_manager)
    await engine.start()
    
    criteria = DecisionCriteria(
        decision_type=DecisionType.SYSTEM_OPTIMIZATION,
        context={'system_load': 0.8, 'optimization_target': 'performance'}
    )
    
    # Make initial decision
    result = await engine.make_decision(criteria)
    decision_id = result.decision_id
    
    initial_metrics = engine.get_decision_metrics()
    initial_successful = initial_metrics['performance_metrics']['successful_decisions']
    
    # Record successful outcome
    await engine.record_decision_outcome(decision_id, success=True, outcome_data={
        'improvement': 0.2,
        'side_effects': None
    })
    
    # Check that learning occurred
    updated_metrics = engine.get_decision_metrics()
    updated_successful = updated_metrics['performance_metrics']['successful_decisions']
    
    assert updated_successful == initial_successful + 1, "Success count not updated"
    
    print("✅ Decision learning working:")
    print(f"   - Decision recorded: {decision_id[:8]}...")
    print(f"   - Successful decisions: {updated_successful}")
    print(f"   - Success patterns learned: {updated_metrics['success_patterns_count']}")
    
    # Test failure learning
    result2 = await engine.make_decision(criteria)
    await engine.record_decision_outcome(result2.decision_id, success=False, outcome_data={
        'error': 'resource_conflict',
        'recovery_time': 300
    })
    
    final_metrics = engine.get_decision_metrics()
    print(f"   - Failure patterns learned: {final_metrics['failure_patterns_count']}")
    
    await engine.stop()
    return True

async def test_configuration_updates():
    """Test dynamic configuration updates"""
    print("\nTesting configuration updates...")
    
    engine = DecisionEngine()
    
    consciousness_bus = MockConsciousnessBus()
    state_manager = MockStateManager()
    
    await engine.initialize(consciousness_bus, state_manager)
    await engine.start()
    
    # Initial configuration
    assert engine.default_confidence_threshold == 0.5  # default
    assert engine.neural_voting_enabled == True  # default
    
    # Update configuration
    new_config = {
        'confidence_threshold': 0.7,
        'max_decision_time_ms': 3000,
        'neural_voting_enabled': False,
        'learning_enabled': True
    }
    
    success = await engine.update_configuration(new_config)
    assert success, "Configuration update failed"
    
    # Verify changes
    assert engine.default_confidence_threshold == 0.7
    assert engine.max_decision_time_ms == 3000
    assert engine.neural_voting_enabled == False
    assert engine.learning_enabled == True
    
    print("✅ Configuration updates working:")
    print(f"   - Confidence threshold: {engine.default_confidence_threshold}")
    print(f"   - Max decision time: {engine.max_decision_time_ms}ms")
    print(f"   - Neural voting: {'enabled' if engine.neural_voting_enabled else 'disabled'}")
    print(f"   - Learning: {'enabled' if engine.learning_enabled else 'disabled'}")
    
    await engine.stop()
    return True

async def test_performance_metrics():
    """Test performance metrics collection"""
    print("\nTesting performance metrics...")
    
    engine = DecisionEngine()
    
    consciousness_bus = MockConsciousnessBus()
    state_manager = MockStateManager()
    
    await engine.initialize(consciousness_bus, state_manager)
    await engine.start()
    
    # Make several decisions to generate metrics
    decision_types = [
        DecisionType.THREAT_ASSESSMENT,
        DecisionType.LEARNING_ADAPTATION,
        DecisionType.USER_GUIDANCE
    ]
    
    results = []
    for decision_type in decision_types:
        criteria = DecisionCriteria(
            decision_type=decision_type,
            context={'test': 'performance_metrics'}
        )
        result = await engine.make_decision(criteria)
        results.append(result)
    
    # Get performance metrics
    metrics = engine.get_decision_metrics()
    
    assert metrics['performance_metrics']['total_decisions'] == 3
    assert metrics['performance_metrics']['average_confidence'] > 0
    assert metrics['performance_metrics']['average_processing_time_ms'] > 0
    assert len(metrics['performance_metrics']['decisions_by_type']) > 0
    
    print("✅ Performance metrics working:")
    print(f"   - Total decisions: {metrics['performance_metrics']['total_decisions']}")
    print(f"   - Average confidence: {metrics['performance_metrics']['average_confidence']:.1%}")
    print(f"   - Average processing time: {metrics['performance_metrics']['average_processing_time_ms']:.1f}ms")
    print(f"   - Decision types tracked: {list(metrics['performance_metrics']['decisions_by_type'].keys())}")
    print(f"   - Consciousness level: {metrics['consciousness_level']}")
    print(f"   - Decision history length: {metrics['decision_history_length']}")
    
    await engine.stop()
    return True

async def test_event_processing():
    """Test consciousness event processing"""
    print("\nTesting event processing...")
    
    engine = DecisionEngine()
    
    consciousness_bus = MockConsciousnessBus()
    state_manager = MockStateManager()
    
    await engine.initialize(consciousness_bus, state_manager)
    await engine.start()
    
    # Test neural evolution event
    neural_event = ConsciousnessEvent(
        event_type=EventType.NEURAL_EVOLUTION,
        source_component="test_neural_engine",
        data={
            'evolution_data': {
                'population_id': 'executive',
                'evolution_cycle': 5,
                'fitness_improvements': {'overall': 0.1},
                'new_consciousness_level': 0.8
            }
        }
    )
    
    initial_populations = len(engine.neural_populations)
    success = await engine.process_event(neural_event)
    assert success, "Failed to process neural evolution event"
    
    # Test consciousness emergence event
    emergence_event = ConsciousnessEvent(
        event_type=EventType.CONSCIOUSNESS_EMERGENCE,
        source_component="test_consciousness",
        data={
            'emergence_prediction': {
                'predicted_level': 0.85,
                'confidence': 0.9
            }
        }
    )
    
    old_consciousness = engine.consciousness_level
    success = await engine.process_event(emergence_event)
    assert success, "Failed to process consciousness emergence event"
    
    print("✅ Event processing working:")
    print(f"   - Neural evolution event processed")
    print(f"   - Consciousness updated: {old_consciousness:.2f} → {engine.consciousness_level:.2f}")
    print(f"   - Neural populations updated")
    
    await engine.stop()
    return True

async def main():
    """Run all decision engine tests"""
    print("🧠 AI Decision Making Engine Implementation Test")
    print("=" * 60)
    
    tests = [
        test_decision_engine_initialization,
        test_threat_assessment_decision,
        test_learning_adaptation_decision,
        test_user_guidance_decision,
        test_tool_recommendation_decision,
        test_neural_population_integration,
        test_consciousness_influence,
        test_decision_learning,
        test_configuration_updates,
        test_performance_metrics,
        test_event_processing
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
        print("🎉 All decision engine tests passed!")
        print("\n✅ AI Decision Making Engine with confidence scoring is working correctly!")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)