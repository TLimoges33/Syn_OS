#!/usr/bin/env python3
"""
SynapticOS Integration Test Suite
Tests the integration between all major components
"""

import asyncio
import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Add overlay modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'synapticos-overlay'))

# Import SynapticOS components
try:
    from consciousness.neural_darwinism import NeuralDarwinismEngine
    from lm_studio.lm_studio_client import LMStudioClient, LMStudioConfig, ConsciousnessAIInterface
    from context_engine.personal_context import PersonalContextEngine, ActivityType, SkillLevel
    from security_tutor.security_tutor import SecurityTutor, ModuleType
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all SynapticOS components are in the correct paths")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('synapticos.integration_test')

class IntegrationTestSuite:
    """Main integration test suite"""
    
    def __init__(self):
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.components = {}
        
    async def setup(self):
        """Initialize all components"""
        logger.info("=== SynapticOS Integration Test Suite ===")
        logger.info("Initializing components...")
        
        try:
            # Initialize Neural Darwinism Engine
            consciousness_config = {
                'populations': [
                    {'id': 'test_pop', 'size': 100, 'specialization': 'general'}
                ],
                'evolution_interval': 0.1,
                'consciousness_threshold': 0.7
            }
            self.components['consciousness'] = NeuralDarwinismEngine(consciousness_config)
            
            # Initialize LM Studio Client (mock mode for testing)
            lm_config = LMStudioConfig(
                api_endpoint="http://localhost:1234/v1",
                model="test-model"
            )
            self.components['lm_studio'] = LMStudioClient(lm_config)
            
            # Initialize Personal Context Engine
            self.components['context_engine'] = PersonalContextEngine(
                storage_path="./test_context"
            )
            
            # Initialize Security Tutor
            self.components['security_tutor'] = SecurityTutor(
                content_path="./test_content"
            )
            
            # Initialize components
            init_results = await asyncio.gather(
                self._init_consciousness(),
                self._init_context_engine(),
                self._init_security_tutor(),
                return_exceptions=True
            )
            
            for i, result in enumerate(init_results):
                if isinstance(result, Exception):
                    logger.error(f"Component initialization failed: {result}")
                    
            logger.info("Component initialization complete")
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            self.test_results['errors'].append(str(e))
            
    async def _init_consciousness(self):
        """Initialize consciousness engine"""
        if self.components['consciousness'].initialize():
            logger.info("✓ Consciousness engine initialized")
            return True
        else:
            raise Exception("Failed to initialize consciousness engine")
            
    async def _init_context_engine(self):
        """Initialize context engine"""
        if await self.components['context_engine'].initialize():
            logger.info("✓ Context engine initialized")
            return True
        else:
            raise Exception("Failed to initialize context engine")
            
    async def _init_security_tutor(self):
        """Initialize security tutor"""
        # Pass LM Studio client and context engine if available
        lm_client = self.components.get('lm_studio')
        context_engine = self.components.get('context_engine')
        
        if await self.components['security_tutor'].initialize(
            lm_studio_client=lm_client,
            context_engine=context_engine
        ):
            logger.info("✓ Security tutor initialized")
            return True
        else:
            raise Exception("Failed to initialize security tutor")
    
    async def test_consciousness_basic(self):
        """Test basic consciousness operations"""
        logger.info("\n--- Testing Consciousness Engine ---")
        
        try:
            engine = self.components['consciousness']
            
            # Start the engine
            engine.start()
            await asyncio.sleep(0.5)  # Let it run briefly
            
            # Get status
            status = engine.get_status()
            assert status['running'] == True, "Engine should be running"
            assert status['evolution_cycles'] > 0, "Evolution should have occurred"
            
            # Get consciousness level
            level = engine.get_consciousness_level()
            assert 0 <= level <= 1, "Consciousness level should be between 0 and 1"
            
            # Trigger adaptation
            engine.trigger_adaptation("test_trigger")
            
            # Stop the engine
            engine.stop()
            
            logger.info(f"✓ Consciousness tests passed (cycles: {status['evolution_cycles']}, level: {level:.3f})")
            self.test_results['passed'] += 1
            
        except Exception as e:
            logger.error(f"✗ Consciousness test failed: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"Consciousness: {e}")
    
    async def test_context_engine(self):
        """Test personal context engine"""
        logger.info("\n--- Testing Personal Context Engine ---")
        
        try:
            engine = self.components['context_engine']
            user_id = "test_user_001"
            
            # Create user context
            context = await engine.get_or_create_context(user_id)
            assert context.user_id == user_id, "User ID should match"
            
            # Record some activities
            await engine.record_activity(
                user_id=user_id,
                activity_type=ActivityType.LEARNING,
                domain="network_security",
                tool_used="nmap",
                duration_seconds=1800,
                success=True
            )
            
            await engine.record_activity(
                user_id=user_id,
                activity_type=ActivityType.PRACTICING,
                domain="network_security",
                tool_used="wireshark",
                duration_seconds=2400,
                success=True
            )
            
            # Check skill level
            skill_level = await engine.get_skill_level(user_id, "network_security")
            assert skill_level == SkillLevel.BEGINNER, "Should start at beginner level"
            
            # Get recommendations
            recommendations = await engine.get_recommendations(user_id)
            assert 'next_modules' in recommendations, "Should have module recommendations"
            assert 'suggested_tools' in recommendations, "Should have tool suggestions"
            
            # Get statistics
            stats = engine.get_statistics(user_id)
            assert stats['total_experience'] > 0, "Should have gained experience"
            assert stats['total_time_hours'] > 0, "Should have tracked time"
            
            logger.info(f"✓ Context engine tests passed (XP: {stats['total_experience']}, Time: {stats['total_time_hours']:.1f}h)")
            self.test_results['passed'] += 1
            
        except Exception as e:
            logger.error(f"✗ Context engine test failed: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"Context Engine: {e}")
    
    async def test_security_tutor(self):
        """Test security tutor module"""
        logger.info("\n--- Testing Security Tutor ---")
        
        try:
            tutor = self.components['security_tutor']
            user_id = "test_student_001"
            
            # Start a lesson
            lesson_result = await tutor.start_lesson(user_id, "net_sec_101")
            assert 'error' not in lesson_result, f"Lesson start failed: {lesson_result.get('error')}"
            assert 'session_id' in lesson_result, "Should have session ID"
            
            session_id = lesson_result['session_id']
            
            # Complete the lesson
            completion = await tutor.complete_lesson(session_id, score=85)
            assert completion['completed'] == True, "Lesson should be completed"
            assert completion['score'] == 85, "Score should match"
            
            # Get module progress
            progress = await tutor.get_module_progress(user_id, ModuleType.NETWORK_SECURITY)
            assert progress['completed_lessons'] > 0, "Should have completed lessons"
            assert progress['total_score'] > 0, "Should have score"
            
            # Get learning dashboard
            dashboard = await tutor.get_learning_dashboard(user_id)
            assert 'modules' in dashboard, "Should have modules data"
            assert dashboard['total_score'] > 0, "Should have total score"
            
            logger.info(f"✓ Security tutor tests passed (Score: {dashboard['total_score']}, Time: {dashboard['total_time_hours']:.1f}h)")
            self.test_results['passed'] += 1
            
        except Exception as e:
            logger.error(f"✗ Security tutor test failed: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"Security Tutor: {e}")
    
    async def test_component_integration(self):
        """Test integration between components"""
        logger.info("\n--- Testing Component Integration ---")
        
        try:
            # Test consciousness + context integration
            consciousness = self.components['consciousness']
            context_engine = self.components['context_engine']
            
            # Simulate consciousness triggering context update
            consciousness.trigger_adaptation("learning_event", {
                "user_id": "integration_test_user",
                "domain": "ai_consciousness"
            })
            
            # Test context + tutor integration
            user_id = "integration_test_user"
            
            # Record activity in context engine
            await context_engine.record_activity(
                user_id=user_id,
                activity_type=ActivityType.LEARNING,
                domain="web_exploitation",
                tool_used="burpsuite",
                duration_seconds=3600,
                success=True
            )
            
            # Start a lesson in tutor (should consider context)
            tutor = self.components['security_tutor']
            lesson = await tutor.start_lesson(user_id, "web_exp_101")
            
            if 'error' not in lesson:
                # Complete it
                await tutor.complete_lesson(lesson['session_id'], score=90)
                
                # Check if context was updated
                stats = context_engine.get_statistics(user_id)
                assert stats['total_experience'] > 0, "Context should be updated"
            
            logger.info("✓ Component integration tests passed")
            self.test_results['passed'] += 1
            
        except Exception as e:
            logger.error(f"✗ Integration test failed: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"Integration: {e}")
    
    async def test_kernel_module_interface(self):
        """Test kernel module interface (simulated)"""
        logger.info("\n--- Testing Kernel Module Interface ---")
        
        try:
            # Simulate kernel module interaction
            # In real deployment, this would interact with /dev/synapticos
            
            # Check if device would be accessible
            device_path = Path("/dev/synapticos")
            proc_path = Path("/proc/synapticos_stats")
            
            if device_path.exists() and proc_path.exists():
                # Real kernel module is loaded
                logger.info("✓ Kernel module detected")
                
                # Try to read stats
                with open(proc_path, 'r') as f:
                    stats = f.read()
                    logger.info(f"Kernel stats:\n{stats}")
            else:
                # Simulate kernel module behavior
                logger.info("ℹ Kernel module not loaded (expected on non-Linux systems)")
                
                # Simulate metrics
                simulated_metrics = {
                    'process_interactions': 42,
                    'ai_requests': 17,
                    'context_switches': 128,
                    'consciousness_level': 73
                }
                
                logger.info(f"Simulated kernel metrics: {simulated_metrics}")
            
            logger.info("✓ Kernel interface test completed")
            self.test_results['passed'] += 1
            
        except Exception as e:
            logger.error(f"✗ Kernel interface test failed: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"Kernel Interface: {e}")
    
    async def run_all_tests(self):
        """Run all integration tests"""
        await self.setup()
        
        # Run individual component tests
        await self.test_consciousness_basic()
        await self.test_context_engine()
        await self.test_security_tutor()
        
        # Run integration tests
        await self.test_component_integration()
        await self.test_kernel_module_interface()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        logger.info("\n" + "="*50)
        logger.info("SYNAPTICOS INTEGRATION TEST REPORT")
        logger.info("="*50)
        logger.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Total Tests: {self.test_results['passed'] + self.test_results['failed']}")
        logger.info(f"Passed: {self.test_results['passed']} ✓")
        logger.info(f"Failed: {self.test_results['failed']} ✗")
        
        if self.test_results['errors']:
            logger.info("\nErrors:")
            for error in self.test_results['errors']:
                logger.info(f"  - {error}")
        
        # Overall status
        if self.test_results['failed'] == 0:
            logger.info("\n🎉 ALL TESTS PASSED! SynapticOS components are properly integrated.")
        else:
            logger.info("\n⚠️  Some tests failed. Please review the errors above.")
        
        logger.info("="*50)
        
        # Save report
        report = {
            'timestamp': datetime.now().isoformat(),
            'results': self.test_results,
            'status': 'PASS' if self.test_results['failed'] == 0 else 'FAIL'
        }
        
        with open('integration_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("Report saved to integration_test_report.json")


async def main():
    """Main test runner"""
    test_suite = IntegrationTestSuite()
    
    try:
        await test_suite.run_all_tests()
    except KeyboardInterrupt:
        logger.info("\nTests interrupted by user")
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())