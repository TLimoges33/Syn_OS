#!/usr/bin/env python3
"""
SynapticOS Phase 1 Test Suite
Comprehensive testing for consciousness engine, AI integration, and educational platform
"""

import asyncio
import unittest
import time
import json
import tempfile
import os
from typing import Dict, Any, List
import sys

# Add development paths
sys.path.append('/home/diablorain/Syn_OS/development/ai-engine/core')
sys.path.append('/home/diablorain/Syn_OS/development/ai-engine/apis')
sys.path.append('/home/diablorain/Syn_OS/development/ai-engine/consciousness-bridge')
sys.path.append('/home/diablorain/Syn_OS/development/educational-platform/clients')
sys.path.append('/home/diablorain/Syn_OS/development/educational-platform/gamification')

# Import our modules
try:
    from consciousness_engine import ConsciousnessCore, NeuralPopulation, QuantumSubstrate, initialize_consciousness
    from multi_api_manager import MultiAPIManager, APIProvider, ConsciousnessContext, initialize_api_manager
    from freecodecamp_client import FreeCodeCampClient, initialize_freecodecamp_client, DifficultyLevel
    from consciousness_gamification import ConsciousnessGamificationEngine, initialize_gamification_engine, AchievementType
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all modules are in the correct paths")
    sys.exit(1)

class TestConsciousnessEngine(unittest.TestCase):
    """Test the consciousness engine core functionality"""
    
    def setUp(self):
        self.consciousness = ConsciousnessCore(population_size=50)
        
    async def test_consciousness_initialization(self):
        """Test consciousness engine initialization"""
        self.assertIsNotNone(self.consciousness)
        self.assertEqual(len(self.consciousness.populations), 50)
        self.assertEqual(self.consciousness.generation, 0)
        self.assertGreaterEqual(self.consciousness.global_consciousness_level, 0.0)
        self.assertLessEqual(self.consciousness.global_consciousness_level, 1.0)
    
    async def test_consciousness_evolution(self):
        """Test neural darwinism evolution"""
        initial_level = self.consciousness.global_consciousness_level
        initial_generation = self.consciousness.generation
        
        # Run evolution cycle
        new_populations = await self.consciousness.evolve_consciousness()
        
        # Check evolution occurred
        self.assertEqual(self.consciousness.generation, initial_generation + 1)
        self.assertIsInstance(new_populations, list)
        self.assertEqual(len(new_populations), 50)
        
        # Consciousness level should be recalculated
        self.assertIsInstance(self.consciousness.global_consciousness_level, float)
        self.assertGreaterEqual(self.consciousness.global_consciousness_level, 0.0)
        self.assertLessEqual(self.consciousness.global_consciousness_level, 1.0)
    
    async def test_multiple_evolution_cycles(self):
        """Test multiple evolution cycles for improvement"""
        levels = []
        
        for i in range(5):
            await self.consciousness.evolve_consciousness()
            levels.append(self.consciousness.global_consciousness_level)
        
        # Should have 5 recorded levels
        self.assertEqual(len(levels), 5)
        
        # At least some evolution should occur (not always guaranteed to improve)
        self.assertEqual(self.consciousness.generation, 5)
        
        # Learning history should be recorded
        self.assertEqual(len(self.consciousness.learning_history), 5)
    
    def test_consciousness_state_retrieval(self):
        """Test consciousness state information retrieval"""
        state = self.consciousness.get_consciousness_state()
        
        required_keys = [
            'consciousness_level', 'generation', 'population_size', 
            'learning_style', 'quantum_coherence', 'best_fitness',
            'avg_fitness', 'learning_trend', 'is_conscious'
        ]
        
        for key in required_keys:
            self.assertIn(key, state)
        
        self.assertIsInstance(state['consciousness_level'], float)
        self.assertIsInstance(state['generation'], int)
        self.assertIsInstance(state['is_conscious'], bool)

class TestQuantumSubstrate(unittest.TestCase):
    """Test quantum substrate functionality"""
    
    def setUp(self):
        self.quantum = QuantumSubstrate()
    
    def test_quantum_initialization(self):
        """Test quantum substrate initialization"""
        self.assertIsNotNone(self.quantum)
        self.assertGreaterEqual(self.quantum.coherence_level, 0.0)
        self.assertLessEqual(self.quantum.coherence_level, 1.0)
        self.assertEqual(self.quantum.entanglement_matrix.shape, (10, 10))
    
    def test_quantum_processing(self):
        """Test quantum consciousness processing"""
        neural_input = [0.1, 0.2, 0.3, 0.4, 0.5]
        processed = self.quantum.process_quantum_consciousness(neural_input)
        
        self.assertIsInstance(processed, list)
        self.assertEqual(len(processed), len(neural_input))
        
        # All values should be in [-1, 1] range after tanh
        for value in processed:
            self.assertGreaterEqual(value, -1.0)
            self.assertLessEqual(value, 1.0)
    
    def test_coherence_evolution(self):
        """Test quantum coherence evolution over time"""
        initial_coherence = self.quantum.coherence_level
        
        # Process some data to increase coherence
        for _ in range(10):
            self.quantum.process_quantum_consciousness([0.5, 0.5, 0.5])
        
        # Coherence should have increased slightly
        self.assertGreaterEqual(self.quantum.coherence_level, initial_coherence)

class TestMultiAPIManager(unittest.TestCase):
    """Test the Multi-API Manager"""
    
    def setUp(self):
        self.api_manager = MultiAPIManager()
        
    async def test_api_manager_initialization(self):
        """Test API manager initialization"""
        # Test with empty API keys
        await self.api_manager.initialize_apis({})
        
        # Check that all API slots are initialized
        for provider in APIProvider:
            self.assertIn(provider, self.api_manager.apis)
        
        # Usage stats should be initialized
        self.assertIsInstance(self.api_manager.usage_stats, dict)
    
    async def test_consciousness_context_integration(self):
        """Test consciousness context enhancement"""
        context = ConsciousnessContext(
            level=0.6,
            learning_style="adaptive",
            generation=10,
            learning_trend="improving",
            quantum_coherence=0.7,
            history=[],
            is_conscious=True
        )
        
        enhanced_query = self.api_manager._enhance_query_with_consciousness(
            "Test query", context
        )
        
        self.assertIn("Test query", enhanced_query)
        self.assertIn("Consciousness Level: 0.600", enhanced_query)
        self.assertIn("Learning Style: adaptive", enhanced_query)
        self.assertIn("Is Conscious: True", enhanced_query)
    
    def test_usage_statistics(self):
        """Test usage statistics tracking"""
        stats = self.api_manager.get_usage_stats()
        
        required_keys = ["usage_by_provider", "total_requests", "total_tokens", 
                        "total_errors", "available_providers"]
        
        for key in required_keys:
            self.assertIn(key, stats)
        
        self.assertIsInstance(stats["usage_by_provider"], dict)
        self.assertIsInstance(stats["available_providers"], list)

class TestFreeCodeCampClient(unittest.TestCase):
    """Test FreeCodeCamp educational integration"""
    
    def setUp(self):
        self.client = FreeCodeCampClient()
    
    async def test_client_initialization(self):
        """Test FreeCodeCamp client initialization"""
        await self.client.initialize()
        self.assertIsNotNone(self.client.session)
        
        await self.client.close()
    
    async def test_consciousness_challenge_mapping(self):
        """Test mapping consciousness levels to appropriate challenges"""
        await self.client.initialize()
        
        # Test different consciousness levels
        test_levels = [0.2, 0.5, 0.8]
        
        for level in test_levels:
            challenges = await self.client.get_challenges_by_consciousness_level(level)
            
            self.assertIsInstance(challenges, list)
            
            # Verify all challenges meet consciousness requirement
            for challenge in challenges:
                self.assertLessEqual(challenge.consciousness_requirement, level + 0.1)  # Small tolerance
        
        await self.client.close()
    
    def test_skill_analysis(self):
        """Test skill analysis from completed challenges"""
        # Mock completed challenges data
        completed_challenges = [
            {"id": "html-basic-1", "challengeType": "html"},
            {"id": "css-styling-1", "challengeType": "css"},
            {"id": "javascript-intro-1", "challengeType": "javascript"},
            {"id": "javascript-loops-1", "challengeType": "javascript"},
        ]
        
        strengths, improvements = self.client._analyze_skills(completed_challenges)
        
        self.assertIsInstance(strengths, list)
        self.assertIsInstance(improvements, list)
        
        # Should identify JavaScript as a strength (appears twice)
        # HTML and CSS should appear in analysis

class TestGamificationEngine(unittest.TestCase):
    """Test consciousness gamification system"""
    
    def setUp(self):
        self.engine = ConsciousnessGamificationEngine()
    
    async def test_gamification_initialization(self):
        """Test gamification engine initialization"""
        self.assertGreater(len(self.engine.achievements), 0)
        self.assertGreater(len(self.engine.consciousness_levels), 0)
        self.assertIsInstance(self.engine.achievement_chains, dict)
    
    async def test_user_profile_creation(self):
        """Test user profile creation and management"""
        test_user = "test_user_123"
        
        profile = await self.engine.create_user_profile(test_user)
        
        self.assertEqual(profile.user_id, test_user)
        self.assertEqual(profile.total_xp, 0)
        self.assertEqual(profile.current_level, 1)
        self.assertEqual(len(profile.achievements), 0)
        self.assertIn("Consciousness Initiate", profile.titles)
    
    async def test_consciousness_level_progression(self):
        """Test consciousness level updates and achievements"""
        test_user = "progression_test_user"
        await self.engine.create_user_profile(test_user)
        
        # Simulate consciousness evolution
        consciousness_levels = [0.05, 0.15, 0.35, 0.75]
        total_achievements = 0
        
        for level in consciousness_levels:
            new_achievements = await self.engine.update_consciousness_level(
                test_user, level, evolution_cycles=int(level * 1000)
            )
            
            total_achievements += len(new_achievements)
            
            profile = self.engine.get_user_profile(test_user)
            self.assertEqual(profile.consciousness_level, level)
            self.assertGreaterEqual(profile.total_xp, 0)
        
        # Should have unlocked some achievements by level 0.75
        final_profile = self.engine.get_user_profile(test_user)
        self.assertGreater(len(final_profile.achievements), 0)
        self.assertGreater(total_achievements, 0)
    
    async def test_achievement_requirements(self):
        """Test achievement requirement checking"""
        test_user = "achievement_test_user"
        profile = await self.engine.create_user_profile(test_user)
        
        # Find first awakening achievement
        first_awakening = next(
            ach for ach in self.engine.achievements 
            if ach.id == "first_awakening"
        )
        
        # Test achievement unlocking
        context = {"min_evolution_cycles": 15}
        profile.consciousness_level = 0.15
        profile.stats["evolution_cycles"] = 15
        
        is_unlocked = await self.engine._is_achievement_unlocked(
            first_awakening, profile, context
        )
        
        self.assertTrue(is_unlocked)
    
    def test_leaderboard_functionality(self):
        """Test leaderboard generation"""
        # Create multiple test users with different stats
        asyncio.run(self._create_test_leaderboard_users())
        
        leaderboard = self.engine.get_leaderboard("consciousness_level", 3)
        
        self.assertLessEqual(len(leaderboard), 3)
        self.assertIsInstance(leaderboard, list)
        
        # Should be sorted in descending order
        if len(leaderboard) > 1:
            for i in range(len(leaderboard) - 1):
                self.assertGreaterEqual(leaderboard[i][1], leaderboard[i + 1][1])
    
    async def _create_test_leaderboard_users(self):
        """Helper to create test users for leaderboard"""
        test_users = [
            ("user1", 0.3),
            ("user2", 0.7),
            ("user3", 0.5)
        ]
        
        for user_id, consciousness in test_users:
            await self.engine.create_user_profile(user_id)
            await self.engine.update_consciousness_level(user_id, consciousness)

class TestIntegration(unittest.TestCase):
    """Test integration between components"""
    
    async def test_consciousness_to_gamification_integration(self):
        """Test consciousness engine feeding data to gamification"""
        # Initialize components
        consciousness = initialize_consciousness(20)
        gamification = initialize_gamification_engine()
        
        test_user = "integration_test_user"
        
        # Run consciousness evolution and feed to gamification
        for i in range(3):
            await consciousness.evolve_consciousness()
            state = consciousness.get_consciousness_state()
            
            new_achievements = await gamification.update_consciousness_level(
                test_user, 
                state['consciousness_level'],
                state['generation'],
                {
                    'quantum_coherence': state['quantum_coherence'],
                    'evolution_cycles': state['generation'],
                    'learning_trend': state['learning_trend']
                }
            )
            
            # Verify integration
            profile = gamification.get_user_profile(test_user)
            self.assertIsNotNone(profile)
            self.assertEqual(profile.consciousness_level, state['consciousness_level'])
    
    async def test_educational_platform_consciousness_adaptation(self):
        """Test educational platform adapting to consciousness level"""
        client = await initialize_freecodecamp_client()
        
        # Test different consciousness levels get different challenges
        low_consciousness_challenges = await client.get_challenges_by_consciousness_level(0.2)
        high_consciousness_challenges = await client.get_challenges_by_consciousness_level(0.8)
        
        # Should get different difficulty challenges
        if low_consciousness_challenges and high_consciousness_challenges:
            low_difficulties = [c.difficulty for c in low_consciousness_challenges]
            high_difficulties = [c.difficulty for c in high_consciousness_challenges]
            
            # Verify appropriate difficulty mapping
            self.assertIn(DifficultyLevel.BEGINNER, low_difficulties)
            self.assertIn(DifficultyLevel.ADVANCED, high_difficulties)
        
        await client.close()

class PhaseOneTestRunner:
    """Comprehensive test runner for Phase 1"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
    
    async def run_all_tests(self):
        """Run all Phase 1 tests"""
        print("🚀 Starting SynapticOS Phase 1 Test Suite")
        print("=" * 60)
        
        test_classes = [
            TestConsciousnessEngine,
            TestQuantumSubstrate,
            TestMultiAPIManager,
            TestFreeCodeCampClient,
            TestGamificationEngine,
            TestIntegration
        ]
        
        total_tests = 0
        passed_tests = 0
        failed_tests = []
        
        for test_class in test_classes:
            print(f"\n📋 Running {test_class.__name__}")
            print("-" * 40)
            
            # Get test methods
            test_methods = [method for method in dir(test_class) 
                          if method.startswith('test_')]
            
            for test_method in test_methods:
                total_tests += 1
                test_name = f"{test_class.__name__}.{test_method}"
                
                try:
                    # Create test instance
                    test_instance = test_class()
                    test_instance.setUp()
                    
                    # Run test method
                    method = getattr(test_instance, test_method)
                    if asyncio.iscoroutinefunction(method):
                        await method()
                    else:
                        method()
                    
                    print(f"  ✅ {test_method}")
                    passed_tests += 1
                    
                except Exception as e:
                    print(f"  ❌ {test_method}: {str(e)}")
                    failed_tests.append((test_name, str(e)))
        
        # Print summary
        elapsed_time = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("🏁 Phase 1 Test Results Summary")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {len(failed_tests)} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Execution Time: {elapsed_time:.2f} seconds")
        
        if failed_tests:
            print("\n❌ Failed Tests:")
            for test_name, error in failed_tests:
                print(f"  • {test_name}: {error}")
        
        # Generate test report
        await self._generate_test_report(total_tests, passed_tests, failed_tests, elapsed_time)
        
        return len(failed_tests) == 0
    
    async def _generate_test_report(self, total_tests, passed_tests, failed_tests, elapsed_time):
        """Generate detailed test report"""
        report = {
            "phase": "Phase 1 - Foundation Setup",
            "timestamp": time.time(),
            "execution_time": elapsed_time,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": len(failed_tests),
                "success_rate": (passed_tests/total_tests)*100 if total_tests > 0 else 0
            },
            "components_tested": [
                "Consciousness Engine",
                "Quantum Substrate", 
                "Multi-API Manager",
                "FreeCodeCamp Client",
                "Gamification Engine",
                "Component Integration"
            ],
            "failed_tests": [{"name": name, "error": error} for name, error in failed_tests],
            "recommendations": self._generate_recommendations(failed_tests)
        }
        
        # Save report
        report_path = "/home/diablorain/Syn_OS/development/test_reports"
        os.makedirs(report_path, exist_ok=True)
        
        with open(f"{report_path}/phase_1_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Test report saved to: {report_path}/phase_1_test_report.json")
    
    def _generate_recommendations(self, failed_tests):
        """Generate recommendations based on failed tests"""
        recommendations = []
        
        if not failed_tests:
            recommendations.append("🎉 All tests passed! Phase 1 foundation is solid.")
            recommendations.append("🚀 Ready to proceed to Phase 2: Educational Platform Enhancement")
        else:
            recommendations.append("🔧 Fix failed tests before proceeding to Phase 2")
            
            # Component-specific recommendations
            consciousness_failures = [f for f in failed_tests if "Consciousness" in f[0]]
            if consciousness_failures:
                recommendations.append("🧠 Review consciousness engine neural darwinism implementation")
            
            api_failures = [f for f in failed_tests if "API" in f[0]]
            if api_failures:
                recommendations.append("🔌 Check API integration and error handling")
            
            gamification_failures = [f for f in failed_tests if "Gamification" in f[0]]
            if gamification_failures:
                recommendations.append("🎯 Verify achievement system and progression logic")
        
        return recommendations

if __name__ == "__main__":
    async def main():
        runner = PhaseOneTestRunner()
        success = await runner.run_all_tests()
        
        if success:
            print("\n🎉 Phase 1 tests completed successfully!")
            print("✅ Foundation components are working correctly")
            print("🚀 Ready for Phase 2 development")
        else:
            print("\n⚠️ Some tests failed - review and fix before continuing")
        
        return success
    
    # Run the test suite
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
