#!/usr/bin/env python3
"""
Comprehensive Test Suite for Personal Context Engine v2
Tests real-time consciousness feedback loops, predictive skill assessment,
and high-performance in-memory processing.
"""

import asyncio
import pytest
import logging
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil

# Import consciousness system components
from .core.consciousness_bus import ConsciousnessBus
from .core.state_manager import StateManager
from .core.event_types import EventType, create_neural_evolution_event
from .core.data_models import ConsciousnessState, PopulationState, create_population_state
from .components.personal_context_v2_complete import (
    PersonalContextEngineV2, SkillLevel, ActivityType, EnhancedSkillProfile,
    UserContextState, ConsciousnessCorrelation, RealTimeContextUpdate
)

logger = logging.getLogger(__name__)

class TestPersonalContextEngineV2:
    """Comprehensive test suite for Personal Context Engine v2"""
    
    @pytest.fixture
    async def temp_storage(self):
        """Create temporary storage directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    async def consciousness_bus(self):
        """Create consciousness bus for testing"""
        bus = ConsciousnessBus()
        await bus.initialize()
        yield bus
        await bus.shutdown()
    
    @pytest.fixture
    async def state_manager(self, temp_storage):
        """Create state manager for testing"""
        manager = StateManager(storage_path=temp_storage)
        await manager.initialize()
        yield manager
        await manager.shutdown()
    
    @pytest.fixture
    async def context_engine(self, temp_storage):
        """Create context engine for testing"""
        engine = PersonalContextEngineV2(storage_path=temp_storage)
        success = await engine.start()
        assert success, "Context engine should start successfully"
        yield engine
        await engine.stop()
    
    @pytest.fixture
    def sample_consciousness_state(self):
        """Create sample consciousness state for testing"""
        return ConsciousnessState(
            consciousness_level=0.7,
            neural_populations={
                'executive': create_population_state('executive', 1000, 'executive', 0.8),
                'memory': create_population_state('memory', 800, 'memory', 0.6),
                'sensory': create_population_state('sensory', 600, 'sensory', 0.7)
            }
        )
    
    async def test_engine_initialization(self, context_engine):
        """Test that the context engine initializes properly"""
        # Check that engine is running
        assert context_engine.is_running
        
        # Check that skill domains are initialized
        assert len(context_engine.skill_domains) == 9
        assert 'network_security' in context_engine.skill_domains
        assert 'web_exploitation' in context_engine.skill_domains
        
        # Check that correlators are initialized
        assert len(context_engine.consciousness_correlators) == 9
        
        # Check health status
        health = await context_engine.get_health_status()
        assert health.component_id == "personal_context_v2"
        assert health.component_type == "context_engine"
    
    async def test_user_context_creation(self, context_engine):
        """Test user context creation and initialization"""
        user_id = "test_user_001"
        
        # Create user context
        context = await context_engine.get_or_create_context(user_id)
        
        # Verify context properties
        assert context.user_id == user_id
        assert isinstance(context.created_at, datetime)
        assert len(context.skill_profiles) == 9
        
        # Verify skill profiles are initialized
        for domain in context_engine.skill_domains:
            assert domain in context.skill_profiles
            profile = context.skill_profiles[domain]
            assert profile.level == SkillLevel.BEGINNER
            assert profile.experience_points == 0
            assert profile.consciousness_correlation == 0.0
        
        # Verify learning preferences are initialized
        assert 'difficulty' in context.learning_preferences
        assert 'pace_multiplier' in context.learning_preferences
        assert context.learning_preferences['difficulty'] == 'normal'
        
        # Verify consciousness profile is initialized
        assert 'baseline_consciousness' in context.consciousness_profile
        assert context.consciousness_profile['baseline_consciousness'] == 0.5
    
    async def test_activity_recording(self, context_engine, sample_consciousness_state):
        """Test activity recording with consciousness correlation"""
        user_id = "test_user_002"
        
        # Record an activity
        await context_engine.record_activity(
            user_id=user_id,
            activity_type=ActivityType.LEARNING,
            domain="network_security",
            tool_used="nmap",
            duration_seconds=1800,  # 30 minutes
            success=True,
            consciousness_state=sample_consciousness_state,
            metadata={"difficulty": "beginner", "module": "port_scanning"}
        )
        
        # Get context and verify activity was recorded
        context = await context_engine.get_or_create_context(user_id)
        
        # Check activity history
        assert len(context.activity_history) == 1
        activity = list(context.activity_history)[0]
        assert activity.activity_type == ActivityType.LEARNING
        assert activity.domain == "network_security"
        assert activity.tool_used == "nmap"
        assert activity.success == True
        assert activity.consciousness_level == 0.7
        
        # Check skill profile updates
        profile = context.skill_profiles["network_security"]
        assert profile.experience_points > 0
        assert profile.time_spent_hours == 0.5  # 30 minutes
        assert profile.last_activity > context.created_at
        
        # Check consciousness correlation
        assert activity.correlation_strength != 0.0  # Should have some correlation
    
    async def test_consciousness_boost_calculation(self, context_engine, sample_consciousness_state):
        """Test consciousness boost in experience calculation"""
        user_id = "test_user_003"
        
        # Record activity with high consciousness
        high_consciousness = ConsciousnessState(consciousness_level=0.9)
        await context_engine.record_activity(
            user_id=user_id,
            activity_type=ActivityType.PRACTICING,
            domain="cryptography",
            tool_used="openssl",
            duration_seconds=3600,  # 1 hour
            success=True,
            consciousness_state=high_consciousness
        )
        
        context = await context_engine.get_or_create_context(user_id)
        high_exp = context.skill_profiles["cryptography"].experience_points
        
        # Record similar activity with low consciousness
        user_id_2 = "test_user_004"
        low_consciousness = ConsciousnessState(consciousness_level=0.2)
        await context_engine.record_activity(
            user_id=user_id_2,
            activity_type=ActivityType.PRACTICING,
            domain="cryptography",
            tool_used="openssl",
            duration_seconds=3600,  # 1 hour
            success=True,
            consciousness_state=low_consciousness
        )
        
        context_2 = await context_engine.get_or_create_context(user_id_2)
        low_exp = context_2.skill_profiles["cryptography"].experience_points
        
        # High consciousness should result in more experience
        assert high_exp > low_exp, "High consciousness should boost experience gain"
    
    async def test_skill_level_progression(self, context_engine, sample_consciousness_state):
        """Test skill level progression with experience"""
        user_id = "test_user_005"
        
        # Record multiple successful activities to trigger level up
        for i in range(10):
            await context_engine.record_activity(
                user_id=user_id,
                activity_type=ActivityType.PRACTICING,
                domain="web_exploitation",
                tool_used="burpsuite",
                duration_seconds=1800,
                success=True,
                consciousness_state=sample_consciousness_state
            )
        
        context = await context_engine.get_or_create_context(user_id)
        profile = context.skill_profiles["web_exploitation"]
        
        # Should have leveled up from BEGINNER
        assert profile.level.value > SkillLevel.BEGINNER.value
        assert profile.experience_points >= 100  # Threshold for INTERMEDIATE
    
    async def test_success_rate_calculation(self, context_engine, sample_consciousness_state):
        """Test success rate calculation from recent activities"""
        user_id = "test_user_006"
        
        # Record mix of successful and failed activities
        activities = [
            (True, "successful_activity_1"),
            (True, "successful_activity_2"),
            (False, "failed_activity_1"),
            (True, "successful_activity_3"),
            (False, "failed_activity_2")
        ]
        
        for success, tool in activities:
            await context_engine.record_activity(
                user_id=user_id,
                activity_type=ActivityType.TESTING,
                domain="forensics",
                tool_used=tool,
                duration_seconds=900,
                success=success,
                consciousness_state=sample_consciousness_state
            )
        
        context = await context_engine.get_or_create_context(user_id)
        profile = context.skill_profiles["forensics"]
        
        # Success rate should be 3/5 = 0.6
        expected_success_rate = 3.0 / 5.0
        assert abs(profile.success_rate - expected_success_rate) < 0.01
    
    async def test_consciousness_correlation_analysis(self, context_engine):
        """Test consciousness correlation analysis"""
        user_id = "test_user_007"
        domain = "reverse_engineering"
        
        # Create correlator
        correlator = context_engine.consciousness_correlators[domain]
        
        # Test correlation calculation
        consciousness_state = ConsciousnessState(
            consciousness_level=0.8,
            neural_populations={
                'executive': create_population_state('executive', 1000, 'executive', 0.9),
                'memory': create_population_state('memory', 800, 'memory', 0.7)
            }
        )
        
        skill_data = {
            'success_rate': 0.8,
            'learning_velocity': 1.2,
            'experience_points': 500,
            'time_spent_hours': 10.0
        }
        
        correlation = await correlator.correlate(consciousness_state, skill_data)
        
        # Should return a valid correlation value
        assert -1.0 <= correlation <= 1.0
        assert len(correlator.correlation_history) == 1
    
    async def test_real_time_context_updates(self, context_engine, sample_consciousness_state):
        """Test real-time context update processing"""
        user_id = "test_user_008"
        
        # Record activity to trigger real-time update
        await context_engine.record_activity(
            user_id=user_id,
            activity_type=ActivityType.CONSCIOUSNESS_TRAINING,
            domain="malware_analysis",
            tool_used="ida_pro",
            duration_seconds=2400,
            success=True,
            consciousness_state=sample_consciousness_state
        )
        
        # Wait for background processing
        await asyncio.sleep(0.1)
        
        # Check that update was queued and processed
        assert context_engine.metrics['updates_processed'] > 0
    
    async def test_consciousness_event_handling(self, context_engine, consciousness_bus):
        """Test consciousness event handling"""
        user_id = "test_user_009"
        
        # Create user context first
        await context_engine.get_or_create_context(user_id)
        
        # Initialize context engine with consciousness bus
        await context_engine.initialize(consciousness_bus, None)
        
        # Create and publish neural evolution event
        evolution_event = create_neural_evolution_event(
            source_component="test_neural_engine",
            evolution_data={
                'new_consciousness_level': 0.85,
                'neural_populations': {'executive': 0.9, 'memory': 0.8}
            },
            target_components=["personal_context_v2"]
        )
        
        await consciousness_bus.publish(evolution_event)
        
        # Wait for event processing
        await asyncio.sleep(0.1)
        
        # Check that consciousness feedback was processed
        assert context_engine.update_queue.qsize() >= 0  # Queue should be processing
    
    async def test_cache_functionality(self, context_engine):
        """Test memory cache functionality"""
        user_id = "test_user_010"
        
        # Create context (should be cached)
        context1 = await context_engine.get_or_create_context(user_id)
        
        # Get context again (should come from cache)
        context2 = await context_engine.get_or_create_context(user_id)
        
        # Should be the same object from cache
        assert context1 is context2
        
        # Test cache invalidation
        context_engine.cache_manager.invalidate(f"context_{user_id}")
        
        # Get context again (should create new instance)
        context3 = await context_engine.get_or_create_context(user_id)
        
        # Should be different object but same data
        assert context1 is not context3
        assert context1.user_id == context3.user_id
    
    async def test_recommendations_generation(self, context_engine, sample_consciousness_state):
        """Test personalized recommendations generation"""
        user_id = "test_user_011"
        
        # Record activities to build profile
        await context_engine.record_activity(
            user_id=user_id,
            activity_type=ActivityType.LEARNING,
            domain="cloud_security",
            tool_used="aws_cli",
            duration_seconds=1800,
            success=True,
            consciousness_state=sample_consciousness_state
        )
        
        # Get recommendations
        recommendations = await context_engine.get_recommendations(user_id)
        
        # Verify recommendation structure
        assert 'next_modules' in recommendations
        assert 'suggested_tools' in recommendations
        assert 'skill_focus' in recommendations
        assert 'challenge_level' in recommendations
        assert 'consciousness_optimized' in recommendations
        
        # Should have consciousness-optimized recommendations
        assert recommendations['consciousness_optimized'] == True
        
        # Should suggest modules for weakest skills
        assert len(recommendations['skill_focus']) <= 3
    
    async def test_learning_path_generation(self, context_engine):
        """Test consciousness-optimized learning path generation"""
        user_id = "test_user_012"
        target_skill = "mobile_security"
        
        # Generate learning path
        path = await context_engine.get_learning_path(user_id, target_skill)
        
        # Verify path structure
        assert isinstance(path, list)
        assert len(path) > 0
        
        # Check path modules
        for module in path:
            assert 'name' in module
            assert 'duration' in module
            assert 'type' in module
            assert 'skill_level' in module
            assert 'estimated_xp' in module
            assert 'consciousness_optimized' in module
            
            # Should be consciousness optimized
            assert module['consciousness_optimized'] == True
    
    async def test_statistics_generation(self, context_engine, sample_consciousness_state):
        """Test enhanced statistics generation"""
        user_id = "test_user_013"
        
        # Record some activities
        for i in range(5):
            await context_engine.record_activity(
                user_id=user_id,
                activity_type=ActivityType.DEVELOPING,
                domain="social_engineering",
                tool_used=f"tool_{i}",
                duration_seconds=1200,
                success=i % 2 == 0,  # Alternate success/failure
                consciousness_state=sample_consciousness_state
            )
        
        # Get statistics
        stats = context_engine.get_statistics(user_id)
        
        # Verify statistics structure
        assert 'total_experience' in stats
        assert 'total_time_hours' in stats
        assert 'skill_levels' in stats
        assert 'achievements_count' in stats
        assert 'average_success_rate' in stats
        assert 'consciousness_correlation' in stats
        assert 'learning_velocity' in stats
        assert 'adaptation_count' in stats
        assert 'consciousness_optimized' in stats
        
        # Should be consciousness optimized
        assert stats['consciousness_optimized'] == True
        
        # Should have valid values
        assert stats['total_experience'] > 0
        assert stats['total_time_hours'] > 0
        assert 0.0 <= stats['average_success_rate'] <= 1.0
    
    async def test_performance_metrics(self, context_engine, sample_consciousness_state):
        """Test performance metrics tracking"""
        user_id = "test_user_014"
        
        # Record multiple activities to generate metrics
        for i in range(10):
            await context_engine.record_activity(
                user_id=user_id,
                activity_type=ActivityType.NEURAL_EVOLUTION,
                domain="network_security",
                tool_used="custom_tool",
                duration_seconds=600,
                success=True,
                consciousness_state=sample_consciousness_state
            )
        
        # Wait for processing
        await asyncio.sleep(0.2)
        
        # Check metrics
        metrics = context_engine.metrics
        assert metrics['updates_processed'] > 0
        assert metrics['average_processing_time'] >= 0.0
        assert 'correlation_accuracy' in metrics
        assert 'consciousness_adaptations' in metrics
    
    async def test_database_persistence(self, context_engine, sample_consciousness_state):
        """Test database persistence functionality"""
        user_id = "test_user_015"
        
        # Record activity
        await context_engine.record_activity(
            user_id=user_id,
            activity_type=ActivityType.EXPLOITING,
            domain="web_exploitation",
            tool_used="sqlmap",
            duration_seconds=1800,
            success=True,
            consciousness_state=sample_consciousness_state
        )
        
        # Force save to database
        await context_engine._save_context_to_db(user_id)
        
        # Clear in-memory context
        del context_engine.contexts[user_id]
        context_engine.cache_manager.invalidate(f"context_{user_id}")
        
        # Load from database
        await context_engine._load_contexts()
        
        # Verify context was restored
        assert user_id in context_engine.contexts
        restored_context = context_engine.contexts[user_id]
        assert restored_context.user_id == user_id
        assert len(restored_context.activity_history) == 1
    
    async def test_error_handling(self, context_engine):
        """Test error handling and recovery"""
        user_id = "test_user_016"
        
        # Test with invalid consciousness state
        try:
            await context_engine.record_activity(
                user_id=user_id,
                activity_type=ActivityType.LEARNING,
                domain="invalid_domain",  # Invalid domain
                tool_used="test_tool",
                duration_seconds=600,
                success=True,
                consciousness_state=None
            )
            # Should not raise exception, should handle gracefully
        except Exception as e:
            pytest.fail(f"Should handle invalid input gracefully: {e}")
        
        # Context should still be created
        context = await context_engine.get_or_create_context(user_id)
        assert context.user_id == user_id
    
    async def test_concurrent_operations(self, context_engine, sample_consciousness_state):
        """Test concurrent operations and thread safety"""
        user_ids = [f"concurrent_user_{i}" for i in range(10)]
        
        # Create concurrent tasks
        tasks = []
        for user_id in user_ids:
            task = context_engine.record_activity(
                user_id=user_id,
                activity_type=ActivityType.TESTING,
                domain="cryptography",
                tool_used="concurrent_tool",
                duration_seconds=300,
                success=True,
                consciousness_state=sample_consciousness_state
            )
            tasks.append(task)
        
        # Execute concurrently
        await asyncio.gather(*tasks)
        
        # Verify all contexts were created
        for user_id in user_ids:
            context = await context_engine.get_or_create_context(user_id)
            assert context.user_id == user_id
            assert len(context.activity_history) == 1


# Integration test
async def test_full_integration():
    """Full integration test of Personal Context Engine v2"""
    logger.info("Starting Personal Context Engine v2 integration test")
    
    # Create temporary storage
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize components
        consciousness_bus = ConsciousnessBus()
        await consciousness_bus.initialize()
        
        state_manager = StateManager(storage_path=temp_dir)
        await state_manager.initialize()
        
        context_engine = PersonalContextEngineV2(storage_path=temp_dir)
        success = await context_engine.start()
        assert success, "Context engine should start successfully"
        
        # Initialize with consciousness system
        await context_engine.initialize(consciousness_bus, state_manager)
        
        # Test user journey
        user_id = "integration_test_user"
        
        # Create consciousness state
        consciousness_state = ConsciousnessState(
            consciousness_level=0.75,
            neural_populations={
                'executive': create_population_state('executive', 1000, 'executive', 0.85),
                'memory': create_population_state('memory', 800, 'memory', 0.70),
                'sensory': create_population_state('sensory', 600, 'sensory', 0.65)
            }
        )
        
        # Simulate learning session
        learning_activities = [
            ("network_security", "nmap", True),
            ("network_security", "wireshark", True),
            ("web_exploitation", "burpsuite", False),
            ("web_exploitation", "sqlmap", True),
            ("cryptography", "openssl", True)
        ]
        
        for domain, tool, success in learning_activities:
            await context_engine.record_activity(
                user_id=user_id,
                activity_type=ActivityType.LEARNING,
                domain=domain,
                tool_used=tool,
                duration_seconds=1800,
                success=success,
                consciousness_state=consciousness_state,
                metadata={"session": "integration_test"}
            )
        
        # Wait for processing
        await asyncio.sleep(0.5)
        
        # Get user context and verify
        context = await context_engine.get_or_create_context(user_id)
        assert len(context.activity_history) == 5
        
        # Check skill progression
        network_profile = context.skill_profiles["network_security"]
        assert network_profile.experience_points > 0
        assert network_profile.success_rate == 1.0  # Both network activities succeeded
        
        web_profile = context.skill_profiles["web_exploitation"]
        assert web_profile.success_rate == 0.5  # One success, one failure
        
        # Get recommendations
        recommendations = await context_engine.get_recommendations(user_id)
        assert recommendations['consciousness_optimized'] == True
        assert len(recommendations['next_modules']) > 0
        
        # Get learning path
        path = await context_engine.get_learning_path(user_id, "forensics")
        assert len(path) > 0
        assert all(module['consciousness_optimized'] for module in path)
        
        # Get statistics
        stats = context_engine.get_statistics(user_id)
        assert stats['consciousness_optimized'] == True
        assert stats['total_experience'] > 0
        assert stats['consciousness_correlation'] != 0.0
        
        # Test consciousness event
        evolution_event = create_neural_evolution_event(
            source_component="integration_test",
            evolution_data={
                'new_consciousness_level': 0.9,
                'neural_populations': {'executive': 0.95, 'memory': 0.85}
            }
        )
        
        await consciousness_bus.publish(evolution_event)
        await asyncio.sleep(0.2)
        
        # Verify health
        health = await context_engine.get_health_status()
        assert health.component_id == "personal_context_v2"
        assert health.health_score > 0.0
        
        logger.info("✓ Personal Context Engine v2 integration test completed successfully")
        
        # Cleanup
        await context_engine.stop()
        await state_manager.shutdown()
        await consciousness_bus.shutdown()
        
    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    # Run integration test
    asyncio.run(test_full_integration())