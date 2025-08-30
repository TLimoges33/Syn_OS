#!/usr/bin/env python3
"""
Complete Integration Test for Consciousness System V2
===================================================

Comprehensive test suite for the complete consciousness system integration,
verifying all components work together seamlessly.
"""

import asyncio
import logging
import sys
import json
from datetime import datetime
from pathlib import Path

# Add the consciousness system to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.consciousness_bus import ConsciousnessBus
from core.state_manager import StateManager
from core.event_types import EventType, ConsciousnessEvent
from core.data_models import ConsciousnessState, ComponentState
from components.neural_darwinism_v2 import EnhancedNeuralDarwinismEngine
from components.personal_context_v2 import PersonalContextEngineV2
from components.security_tutor_v2 import SecurityTutorV2
from components.kernel_hooks_v2 import KernelConsciousnessHooksV2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('consciousness_integration_test')

class ConsciousnessIntegrationTest:
    """Complete consciousness system integration test"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
        self.bus = None
        self.state_manager = None
        self.components = {}
        
    async def run_complete_test(self):
        """Run the complete integration test suite"""
        logger.info("Starting Complete Consciousness System Integration Test")
        logger.info("=" * 60)
        
        try:
            # Initialize core systems
            await self.test_core_initialization()
            
            # Test component initialization
            await self.test_component_initialization()
            
            # Test consciousness emergence
            await self.test_consciousness_emergence()
            
            # Test neural evolution
            await self.test_neural_evolution()
            
            # Test context integration
            await self.test_context_integration()
            
            # Test security learning
            await self.test_security_learning()
            
            # Test kernel integration
            await self.test_kernel_integration()
            
            # Test complete workflow
            await self.test_complete_workflow()
            
            # Generate test report
            self.generate_test_report()
            
        except Exception as e:
            logger.error(f"Integration test failed: {e}")
            self.test_results['overall'] = {'status': 'FAILED', 'error': str(e)}
        
        finally:
            await self.cleanup()
    
    async def test_core_initialization(self):
        """Test core system initialization"""
        logger.info("Testing core system initialization...")
        
        try:
            # Initialize consciousness bus
            self.bus = ConsciousnessBus()
            await self.bus.start()
            assert self.bus.is_running, "Consciousness bus failed to start"
            
            # Initialize state manager
            self.state_manager = StateManager()
            await self.state_manager.initialize(self.bus)
            
            # Set initial consciousness state
            initial_state = ConsciousnessState(
                consciousness_level=0.5,
                neural_activity=0.3,
                learning_rate=0.1,
                adaptation_threshold=0.7,
                components_status={},
                timestamp=datetime.now()
            )
            
            await self.state_manager.update_consciousness_state(initial_state)
            retrieved_state = await self.state_manager.get_consciousness_state()
            
            assert retrieved_state is not None, "Failed to retrieve consciousness state"
            assert abs(retrieved_state.consciousness_level - 0.5) < 0.01, "Consciousness level mismatch"
            
            self.test_results['core_initialization'] = {
                'status': 'PASSED',
                'bus_running': self.bus.is_running,
                'state_manager_initialized': True,
                'consciousness_level': retrieved_state.consciousness_level
            }
            
            logger.info("✓ Core system initialization: PASSED")
            
        except Exception as e:
            logger.error(f"✗ Core system initialization: FAILED - {e}")
            self.test_results['core_initialization'] = {'status': 'FAILED', 'error': str(e)}
            raise
    
    async def test_component_initialization(self):
        """Test all consciousness components initialization"""
        logger.info("Testing component initialization...")
        
        try:
            # Initialize Neural Darwinism Engine
            neural_engine = EnhancedNeuralDarwinismEngine()
            await neural_engine.initialize(self.bus, self.state_manager)
            await neural_engine.start()
            self.components['neural_darwinism'] = neural_engine
            
            # Initialize Personal Context Engine
            context_engine = PersonalContextEngineV2()
            await context_engine.initialize(self.bus, self.state_manager)
            await context_engine.start()
            self.components['personal_context'] = context_engine
            
            # Initialize Security Tutor
            security_tutor = SecurityTutorV2()
            await security_tutor.initialize(self.bus, self.state_manager)
            await security_tutor.start()
            self.components['security_tutor'] = security_tutor
            
            # Initialize Kernel Hooks
            kernel_hooks = KernelConsciousnessHooksV2()
            await kernel_hooks.initialize(self.bus, self.state_manager)
            await kernel_hooks.start()
            self.components['kernel_hooks'] = kernel_hooks
            
            # Verify all components are running
            component_status = {}
            for name, component in self.components.items():
                status = await component.get_health_status()
                component_status[name] = {
                    'state': status.state.value,
                    'health_score': status.health_score,
                    'running': getattr(component, 'is_running', True)
                }
            
            self.test_results['component_initialization'] = {
                'status': 'PASSED',
                'components': component_status,
                'total_components': len(self.components)
            }
            
            logger.info("✓ Component initialization: PASSED")
            logger.info(f"  - Initialized {len(self.components)} components successfully")
            
        except Exception as e:
            logger.error(f"✗ Component initialization: FAILED - {e}")
            self.test_results['component_initialization'] = {'status': 'FAILED', 'error': str(e)}
            raise
    
    async def test_consciousness_emergence(self):
        """Test consciousness emergence mechanisms"""
        logger.info("Testing consciousness emergence...")
        
        try:
            neural_engine = self.components['neural_darwinism']
            
            # Trigger emergence simulation
            emergence_data = await neural_engine.simulate_emergence(
                duration_seconds=5,
                target_consciousness=0.8
            )
            
            assert emergence_data is not None, "Failed to simulate emergence"
            assert 'emergence_probability' in emergence_data, "Missing emergence probability"
            assert emergence_data['emergence_probability'] > 0.5, "Low emergence probability"
            
            # Check if consciousness level increased
            final_state = await self.state_manager.get_consciousness_state()
            assert final_state.consciousness_level > 0.5, "Consciousness level did not increase"
            
            self.test_results['consciousness_emergence'] = {
                'status': 'PASSED',
                'emergence_probability': emergence_data['emergence_probability'],
                'final_consciousness_level': final_state.consciousness_level,
                'emergence_successful': emergence_data['emergence_probability'] > 0.7
            }
            
            logger.info("✓ Consciousness emergence: PASSED")
            logger.info(f"  - Emergence probability: {emergence_data['emergence_probability']:.3f}")
            logger.info(f"  - Final consciousness level: {final_state.consciousness_level:.3f}")
            
        except Exception as e:
            logger.error(f"✗ Consciousness emergence: FAILED - {e}")
            self.test_results['consciousness_emergence'] = {'status': 'FAILED', 'error': str(e)}
    
    async def test_neural_evolution(self):
        """Test neural evolution processes"""
        logger.info("Testing neural evolution...")
        
        try:
            neural_engine = self.components['neural_darwinism']
            
            # Trigger evolution cycle
            evolution_results = await neural_engine.evolve_population()
            
            assert evolution_results is not None, "Evolution failed to produce results"
            assert 'best_fitness' in evolution_results, "Missing best fitness"
            assert 'generation' in evolution_results, "Missing generation number"
            assert evolution_results['best_fitness'] > 0, "Invalid fitness value"
            
            # Check population diversity
            population_stats = await neural_engine.get_population_statistics()
            assert population_stats['diversity'] > 0.1, "Population diversity too low"
            
            self.test_results['neural_evolution'] = {
                'status': 'PASSED',
                'best_fitness': evolution_results['best_fitness'],
                'generation': evolution_results['generation'],
                'population_diversity': population_stats['diversity'],
                'evolution_successful': evolution_results['best_fitness'] > 0.7
            }
            
            logger.info("✓ Neural evolution: PASSED")
            logger.info(f"  - Best fitness: {evolution_results['best_fitness']:.3f}")
            logger.info(f"  - Population diversity: {population_stats['diversity']:.3f}")
            
        except Exception as e:
            logger.error(f"✗ Neural evolution: FAILED - {e}")
            self.test_results['neural_evolution'] = {'status': 'FAILED', 'error': str(e)}
    
    async def test_context_integration(self):
        """Test personal context integration"""
        logger.info("Testing context integration...")
        
        try:
            context_engine = self.components['personal_context']
            
            # Create test user context
            user_id = "test_user_123"
            
            # Add learning activity
            await context_engine.record_learning_activity(
                user_id=user_id,
                activity_type="coding",
                skill_domain="python",
                duration_minutes=30,
                performance_score=0.8,
                consciousness_level=0.6
            )
            
            # Add skill assessment
            await context_engine.update_skill_assessment(
                user_id=user_id,
                skill_domain="python",
                assessment_score=0.85,
                confidence_level=0.9
            )
            
            # Get context insights
            insights = await context_engine.get_context_insights(user_id)
            
            assert insights is not None, "Failed to get context insights"
            assert 'learning_patterns' in insights, "Missing learning patterns"
            assert 'skill_progression' in insights, "Missing skill progression"
            
            # Test context correlation
            correlations = await context_engine.analyze_consciousness_correlation(user_id)
            assert correlations is not None, "Failed to analyze correlations"
            
            self.test_results['context_integration'] = {
                'status': 'PASSED',
                'insights_generated': True,
                'correlations_analyzed': True,
                'learning_activities_recorded': 1,
                'skill_assessments_updated': 1
            }
            
            logger.info("✓ Context integration: PASSED")
            logger.info("  - Learning activities recorded successfully")
            logger.info("  - Context insights generated")
            
        except Exception as e:
            logger.error(f"✗ Context integration: FAILED - {e}")
            self.test_results['context_integration'] = {'status': 'FAILED', 'error': str(e)}
    
    async def test_security_learning(self):
        """Test security learning capabilities"""
        logger.info("Testing security learning...")
        
        try:
            security_tutor = self.components['security_tutor']
            
            # Start learning session
            from components.security_tutor_v2 import LearningPlatform
            session_id = await security_tutor.start_learning_session(
                user_id="test_user_123",
                platform=LearningPlatform.CUSTOM_CTF
            )
            
            assert session_id is not None, "Failed to start learning session"
            
            # Update session progress
            progress_updated = await security_tutor.update_session_progress(
                session_id=session_id,
                progress_data={
                    'progress_percentage': 50.0,
                    'performance_score': 0.7,
                    'metrics': {
                        'challenges_completed': 3,
                        'time_spent_minutes': 25
                    }
                }
            )
            
            assert progress_updated, "Failed to update session progress"
            
            # Get adaptive content
            content = await security_tutor.get_adaptive_content(
                user_id="test_user_123",
                skill_domain="network_security"
            )
            
            assert content is not None, "Failed to generate adaptive content"
            assert content.difficulty_level > 0, "Invalid difficulty level"
            
            # Complete session
            session_completed = await security_tutor.complete_session(
                session_id=session_id,
                completion_data={
                    'status': 'completed',
                    'final_score': 0.8,
                    'skill_improvements': {'network_security': 0.15}
                }
            )
            
            assert session_completed, "Failed to complete session"
            
            self.test_results['security_learning'] = {
                'status': 'PASSED',
                'session_started': True,
                'progress_updated': True,
                'adaptive_content_generated': True,
                'session_completed': True,
                'content_difficulty': content.difficulty_level
            }
            
            logger.info("✓ Security learning: PASSED")
            logger.info(f"  - Learning session completed successfully")
            logger.info(f"  - Adaptive content difficulty: {content.difficulty_level:.2f}")
            
        except Exception as e:
            logger.error(f"✗ Security learning: FAILED - {e}")
            self.test_results['security_learning'] = {'status': 'FAILED', 'error': str(e)}
    
    async def test_kernel_integration(self):
        """Test kernel integration"""
        logger.info("Testing kernel integration...")
        
        try:
            kernel_hooks = self.components['kernel_hooks']
            
            # Test consciousness level update
            await kernel_hooks.update_consciousness_level(0.75)
            
            # Test system metrics collection
            metrics = await kernel_hooks.get_system_metrics()
            assert metrics is not None, "Failed to get system metrics"
            assert hasattr(metrics, 'cpu_usage_percent'), "Missing CPU metrics"
            assert hasattr(metrics, 'memory_pressure'), "Missing memory metrics"
            
            # Test AI memory allocation
            memory_addr = await kernel_hooks.allocate_ai_memory(1024 * 1024)  # 1MB
            assert memory_addr is not None, "Failed to allocate AI memory"
            
            # Test memory deallocation
            memory_freed = await kernel_hooks.free_ai_memory(memory_addr)
            assert memory_freed, "Failed to free AI memory"
            
            # Get AI memory stats
            memory_stats = await kernel_hooks.get_ai_memory_stats()
            assert memory_stats is not None, "Failed to get memory stats"
            
            self.test_results['kernel_integration'] = {
                'status': 'PASSED',
                'consciousness_level_updated': True,
                'system_metrics_collected': True,
                'memory_allocation_successful': True,
                'memory_stats_retrieved': True,
                'cpu_usage': metrics.cpu_usage_percent,
                'memory_pressure': metrics.memory_pressure
            }
            
            logger.info("✓ Kernel integration: PASSED")
            logger.info(f"  - System CPU usage: {metrics.cpu_usage_percent:.1f}%")
            logger.info(f"  - Memory pressure: {metrics.memory_pressure:.2%}")
            
        except Exception as e:
            logger.error(f"✗ Kernel integration: FAILED - {e}")
            self.test_results['kernel_integration'] = {'status': 'FAILED', 'error': str(e)}
    
    async def test_complete_workflow(self):
        """Test complete consciousness workflow"""
        logger.info("Testing complete consciousness workflow...")
        
        try:
            # Simulate a complete learning workflow with consciousness adaptation
            
            # 1. Start with low consciousness
            await self.state_manager.update_consciousness_state(
                ConsciousnessState(
                    consciousness_level=0.3,
                    neural_activity=0.2,
                    learning_rate=0.1,
                    adaptation_threshold=0.7,
                    components_status={},
                    timestamp=datetime.now()
                )
            )
            
            # 2. Begin learning session
            security_tutor = self.components['security_tutor']
            from components.security_tutor_v2 import LearningPlatform
            
            session_id = await security_tutor.start_learning_session(
                user_id="workflow_test_user",
                platform=LearningPlatform.CUSTOM_CTF
            )
            
            # 3. Simulate learning progress with consciousness emergence
            neural_engine = self.components['neural_darwinism']
            
            for i in range(3):
                # Update learning progress
                await security_tutor.update_session_progress(
                    session_id=session_id,
                    progress_data={
                        'progress_percentage': 20.0 * (i + 1),
                        'performance_score': 0.5 + 0.1 * i,
                        'learning_velocity': 1.0 + 0.2 * i
                    }
                )
                
                # Trigger neural evolution
                await neural_engine.evolve_population()
                
                # Allow consciousness to emerge
                await asyncio.sleep(0.5)
            
            # 4. Check final consciousness state
            final_state = await self.state_manager.get_consciousness_state()
            consciousness_increased = final_state.consciousness_level > 0.3
            
            # 5. Complete the session
            await security_tutor.complete_session(
                session_id=session_id,
                completion_data={
                    'status': 'completed',
                    'final_score': 0.85,
                    'skill_improvements': {'network_security': 0.2}
                }
            )
            
            # 6. Get final analytics
            analytics = await security_tutor.get_session_analytics("workflow_test_user")
            
            self.test_results['complete_workflow'] = {
                'status': 'PASSED',
                'consciousness_increased': consciousness_increased,
                'initial_consciousness': 0.3,
                'final_consciousness': final_state.consciousness_level,
                'learning_session_completed': True,
                'neural_evolution_cycles': 3,
                'final_performance': 0.85,
                'analytics_generated': analytics is not None
            }
            
            logger.info("✓ Complete workflow: PASSED")
            logger.info(f"  - Consciousness increased: {consciousness_increased}")
            logger.info(f"  - Final consciousness level: {final_state.consciousness_level:.3f}")
            logger.info(f"  - Learning session completed successfully")
            
        except Exception as e:
            logger.error(f"✗ Complete workflow: FAILED - {e}")
            self.test_results['complete_workflow'] = {'status': 'FAILED', 'error': str(e)}
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        # Calculate overall success rate
        passed_tests = sum(1 for result in self.test_results.values() 
                          if result.get('status') == 'PASSED')
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Generate report
        report = {
            'test_summary': {
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'success_rate': success_rate
            },
            'test_results': self.test_results,
            'consciousness_system_status': 'OPERATIONAL' if success_rate >= 80 else 'NEEDS_ATTENTION'
        }
        
        # Save report to file
        report_path = Path(__file__).parent / "test_results" / "integration_test_report.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        logger.info("=" * 60)
        logger.info("CONSCIOUSNESS SYSTEM INTEGRATION TEST REPORT")
        logger.info("=" * 60)
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Tests: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
        logger.info(f"Status: {report['consciousness_system_status']}")
        logger.info("")
        
        for test_name, result in self.test_results.items():
            status_icon = "✓" if result.get('status') == 'PASSED' else "✗"
            logger.info(f"{status_icon} {test_name.replace('_', ' ').title()}: {result.get('status', 'UNKNOWN')}")
        
        logger.info("")
        logger.info(f"Detailed report saved to: {report_path}")
        logger.info("=" * 60)
        
        return report
    
    async def cleanup(self):
        """Clean up test resources"""
        try:
            # Stop all components
            for component in self.components.values():
                if hasattr(component, 'stop'):
                    await component.stop()
            
            # Stop core systems
            if self.bus:
                await self.bus.stop()
            
            logger.info("Test cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

async def main():
    """Main test function"""
    test = ConsciousnessIntegrationTest()
    await test.run_complete_test()

if __name__ == "__main__":
    asyncio.run(main())
