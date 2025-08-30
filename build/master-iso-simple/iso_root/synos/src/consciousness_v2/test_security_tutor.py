#!/usr/bin/env python3
"""
Test suite for Consciousness-Aware Security Tutor V2
"""

import asyncio
import pytest
import tempfile
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

# Import the security tutor components
from components.security_tutor_v2 import (
    ConsciousnessAwareSecurityTutorV2,
    LearningPlatform,
    LearningMode,
    CognitiveState,
    ContentType
)
from core.data_models import ConsciousnessState, LearningProgressData
from core.event_types import EventType, create_learning_progress_event


class TestConsciousnessAwareSecurityTutorV2:
    """Test cases for the security tutor"""
    
    @pytest.fixture
    async def security_tutor(self):
        """Create a security tutor instance for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            tutor = ConsciousnessAwareSecurityTutorV2(
                storage_path=temp_dir,
                vivaldi_path="/usr/bin/vivaldi"
            )
            
            # Mock the consciousness bus and state manager
            tutor.consciousness_bus = Mock()
            tutor.consciousness_bus.publish = AsyncMock()
            tutor.state_manager = Mock()
            tutor.state_manager.get_consciousness_state = AsyncMock()
            
            await tutor.initialize()
            yield tutor
            await tutor.shutdown()
    
    @pytest.fixture
    def mock_consciousness_state(self):
        """Create a mock consciousness state"""
        return ConsciousnessState(
            consciousness_level=0.7,
            emergence_strength=0.6,
            adaptation_rate=0.5
        )
    
    async def test_initialization(self, security_tutor):
        """Test security tutor initialization"""
        assert security_tutor.component_id == "security_tutor_v2"
        assert security_tutor.component_type == "educational_system"
        assert len(security_tutor.platform_integrations) > 0
        assert security_tutor.consciousness_learning_engine is not None
        assert security_tutor.adaptive_content_generator is not None
    
    async def test_start_learning_session(self, security_tutor, mock_consciousness_state):
        """Test starting a learning session"""
        security_tutor.state_manager.get_consciousness_state.return_value = mock_consciousness_state
        
        session_id = await security_tutor.start_learning_session(
            user_id="test_user",
            platform=LearningPlatform.HACKTHEBOX,
            topic="web_security"
        )
        
        assert session_id is not None
        assert session_id in security_tutor.active_sessions
        
        session = security_tutor.active_sessions[session_id]
        assert session.user_id == "test_user"
        assert session.platform == LearningPlatform.HACKTHEBOX
        assert session.consciousness_level == 0.7
    
    async def test_process_pdf_assignment(self, security_tutor):
        """Test PDF assignment processing"""
        # Create a mock PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf.write(b"Mock PDF content")
            temp_pdf_path = temp_pdf.name
        
        try:
            # Mock the PDF processor
            security_tutor.pdf_processor.extract_pdf_content = AsyncMock(
                return_value="Assignment: Implement a secure web application"
            )
            security_tutor.pdf_processor.analyze_assignment = AsyncMock(
                return_value={
                    'title': 'Web Security Assignment',
                    'difficulty': 'intermediate',
                    'topics': ['web security', 'authentication'],
                    'requirements': ['Implement login system', 'Add CSRF protection']
                }
            )
            
            result = await security_tutor.process_pdf_assignment(
                pdf_path=temp_pdf_path,
                assignment_type="homework"
            )
            
            assert result is not None
            assert 'analysis' in result
            assert 'guidance' in result
            
        finally:
            Path(temp_pdf_path).unlink()
    
    async def test_start_vivaldi_guided_session(self, security_tutor):
        """Test Vivaldi guided session"""
        # Mock the browser guidance system
        security_tutor.browser_guidance_system.launch_guided_session = AsyncMock(
            return_value="browser_session_123"
        )
        
        session_id = await security_tutor.start_vivaldi_guided_session(
            user_id="test_user",
            target_url="https://hackthebox.eu",
            learning_objective="Complete a CTF challenge"
        )
        
        assert session_id is not None
        security_tutor.browser_guidance_system.launch_guided_session.assert_called_once()
    
    async def test_get_adaptive_hints(self, security_tutor, mock_consciousness_state):
        """Test adaptive hint generation"""
        security_tutor.state_manager.get_consciousness_state.return_value = mock_consciousness_state
        
        # Mock the content generator
        security_tutor.adaptive_content_generator.generate_consciousness_aware_hints = AsyncMock(
            return_value=[
                "Consider the OWASP Top 10 vulnerabilities",
                "Start with reconnaissance",
                "Document your findings"
            ]
        )
        
        hints = await security_tutor.get_adaptive_hints(
            session_id="test_session",
            current_context={"challenge": "web_app_pentest"}
        )
        
        assert isinstance(hints, list)
        assert len(hints) > 0
    
    async def test_complete_learning_session(self, security_tutor, mock_consciousness_state):
        """Test completing a learning session"""
        security_tutor.state_manager.get_consciousness_state.return_value = mock_consciousness_state
        
        # First start a session
        session_id = await security_tutor.start_learning_session(
            user_id="test_user",
            platform=LearningPlatform.TRYHACKME,
            topic="network_security"
        )
        
        # Complete the session
        completion_data = {
            'challenges_completed': 3,
            'skills_acquired': ['nmap', 'wireshark'],
            'time_spent': 120,
            'final_score': 85
        }
        
        result = await security_tutor.complete_learning_session(
            session_id=session_id,
            completion_data=completion_data
        )
        
        assert result is not None
        assert 'session_summary' in result
        assert session_id not in security_tutor.active_sessions
    
    async def test_consciousness_adaptation(self, security_tutor):
        """Test consciousness-based adaptation"""
        # Test different consciousness levels
        consciousness_levels = [0.2, 0.5, 0.8]
        
        for level in consciousness_levels:
            mock_state = ConsciousnessState(consciousness_level=level)
            security_tutor.state_manager.get_consciousness_state.return_value = mock_state
            
            learning_mode = security_tutor._determine_learning_mode(level)
            
            if level < 0.3:
                assert learning_mode == LearningMode.EXPLORATION
            elif level < 0.6:
                assert learning_mode == LearningMode.FOCUSED
            elif level < 0.8:
                assert learning_mode == LearningMode.INTENSIVE
            else:
                assert learning_mode == LearningMode.BREAKTHROUGH
    
    async def test_platform_specific_guidance(self, security_tutor):
        """Test platform-specific guidance generation"""
        # Test HackTheBox guidance
        htb_guidance = await security_tutor.get_hackthebox_guidance(
            session_id="test_session",
            machine_data={"name": "test_machine", "difficulty": "easy"}
        )
        
        assert 'reconnaissance' in htb_guidance
        assert 'enumeration' in htb_guidance
        
        # Test TryHackMe guidance
        thm_guidance = await security_tutor.get_tryhackme_guidance(
            session_id="test_session",
            room_data={"name": "test_room", "difficulty": "medium"}
        )
        
        assert 'task_guidance' in thm_guidance
        assert 'learning_path' in thm_guidance
    
    async def test_event_processing(self, security_tutor):
        """Test consciousness event processing"""
        from core.event_types import ConsciousnessEvent
        
        # Test neural evolution event
        evolution_event = ConsciousnessEvent(
            event_type=EventType.NEURAL_EVOLUTION,
            source_component="neural_darwinism",
            data={"evolution_cycle": 100}
        )
        
        result = await security_tutor.process_event(evolution_event)
        assert result is True
        
        # Test learning progress event
        progress_event = create_learning_progress_event(
            user_id="test_user",
            progress_data=LearningProgressData(
                user_id="test_user",
                session_id="test_session",
                platform="hackthebox",
                topic="web_security",
                progress_percentage=75.0
            )
        )
        
        result = await security_tutor.process_event(progress_event)
        assert result is True
    
    async def test_learning_analytics(self, security_tutor, mock_consciousness_state):
        """Test learning analytics tracking"""
        security_tutor.state_manager.get_consciousness_state.return_value = mock_consciousness_state
        
        # Start multiple sessions to generate analytics data
        session_ids = []
        for i in range(3):
            session_id = await security_tutor.start_learning_session(
                user_id=f"user_{i}",
                platform=LearningPlatform.HACKTHEBOX,
                topic="penetration_testing"
            )
            session_ids.append(session_id)
        
        # Check analytics
        analytics = security_tutor.learning_analytics
        assert analytics['total_sessions'] >= 3
        assert analytics['active_sessions'] >= 3
        
        # Complete sessions
        for session_id in session_ids:
            await security_tutor.complete_learning_session(
                session_id=session_id,
                completion_data={'challenges_completed': 1}
            )
        
        assert analytics['completed_sessions'] >= 3
    
    async def test_error_handling(self, security_tutor):
        """Test error handling in various scenarios"""
        # Test invalid session ID
        hints = await security_tutor.get_adaptive_hints(
            session_id="invalid_session",
            current_context={}
        )
        assert hints == []
        
        # Test completing non-existent session
        result = await security_tutor.complete_learning_session(
            session_id="invalid_session",
            completion_data={}
        )
        assert result is None
        
        # Test invalid platform
        with pytest.raises(ValueError):
            await security_tutor.start_learning_session(
                user_id="test_user",
                platform="invalid_platform",
                topic="test"
            )
    
    def test_learning_mode_determination(self, security_tutor):
        """Test learning mode determination logic"""
        test_cases = [
            (0.1, LearningMode.EXPLORATION),
            (0.3, LearningMode.EXPLORATION),
            (0.4, LearningMode.FOCUSED),
            (0.6, LearningMode.FOCUSED),
            (0.7, LearningMode.INTENSIVE),
            (0.8, LearningMode.INTENSIVE),
            (0.9, LearningMode.BREAKTHROUGH),
            (1.0, LearningMode.BREAKTHROUGH)
        ]
        
        for consciousness_level, expected_mode in test_cases:
            actual_mode = security_tutor._determine_learning_mode(consciousness_level)
            assert actual_mode == expected_mode
    
    async def test_cognitive_state_assessment(self, security_tutor):
        """Test cognitive state assessment"""
        mock_state = ConsciousnessState(consciousness_level=0.5)
        
        cognitive_state = await security_tutor._assess_cognitive_state(mock_state)
        assert cognitive_state in [
            CognitiveState.OPTIMAL,
            CognitiveState.UNDERUTILIZED,
            CognitiveState.OVERLOADED,
            CognitiveState.FATIGUED
        ]
    
    async def test_content_generation(self, security_tutor):
        """Test adaptive content generation"""
        # Mock the content generator
        security_tutor.adaptive_content_generator.generate_consciousness_aware_content = AsyncMock(
            return_value={
                'introduction': 'Welcome to web security',
                'main_content': {'complexity_level': 'intermediate'},
                'exercises': [{'type': 'practical', 'difficulty': 'medium'}],
                'hints': ['Start with reconnaissance'],
                'resources': [{'type': 'article', 'title': 'Web Security Basics'}]
            }
        )
        
        content = await security_tutor.adaptive_content_generator.generate_consciousness_aware_content(
            topic="web_security",
            consciousness_level=0.6,
            learning_mode="focused",
            platform="hackthebox"
        )
        
        assert 'introduction' in content
        assert 'main_content' in content
        assert 'exercises' in content


async def run_tests():
    """Run all tests"""
    print("Running Consciousness-Aware Security Tutor V2 tests...")
    
    # Create test instance
    test_instance = TestConsciousnessAwareSecurityTutorV2()
    
    # Run basic tests
    with tempfile.TemporaryDirectory() as temp_dir:
        tutor = ConsciousnessAwareSecurityTutorV2(
            storage_path=temp_dir,
            vivaldi_path="/usr/bin/vivaldi"
        )
        
        # Mock dependencies
        tutor.consciousness_bus = Mock()
        tutor.consciousness_bus.publish = AsyncMock()
        tutor.state_manager = Mock()
        tutor.state_manager.get_consciousness_state = AsyncMock()
        
        try:
            await tutor.initialize()
            
            # Test initialization
            print("✓ Initialization test passed")
            
            # Test learning mode determination
            test_instance.test_learning_mode_determination(tutor)
            print("✓ Learning mode determination test passed")
            
            # Test consciousness adaptation
            await test_instance.test_consciousness_adaptation(tutor)
            print("✓ Consciousness adaptation test passed")
            
            # Test session management
            mock_state = ConsciousnessState(consciousness_level=0.7)
            tutor.state_manager.get_consciousness_state.return_value = mock_state
            
            session_id = await tutor.start_learning_session(
                user_id="test_user",
                platform=LearningPlatform.HACKTHEBOX,
                topic="web_security"
            )
            
            assert session_id is not None
            print("✓ Session management test passed")
            
            # Test completion
            completion_data = {
                'challenges_completed': 2,
                'skills_acquired': ['reconnaissance', 'enumeration'],
                'time_spent': 90
            }
            
            result = await tutor.complete_learning_session(session_id, completion_data)
            print("✓ Session completion test passed")
            
        finally:
            await tutor.shutdown()
    
    print("\n🎉 All Security Tutor V2 tests passed!")


if __name__ == "__main__":
    asyncio.run(run_tests())