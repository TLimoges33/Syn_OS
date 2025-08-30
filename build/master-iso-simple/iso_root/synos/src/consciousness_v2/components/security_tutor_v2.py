#!/usr/bin/env python3
"""
Consciousness-Aware Security Tutor v2 for SynapticOS
Enhanced with real-time consciousness feedback, adaptive learning algorithms,
Vivaldi browser integration, and support for multiple learning platforms.

Supports: FreeCodeCamp, Boot.dev, HackTheBox, TryHackMe, OverTheWire, 
school assignments (PDF processing), and Vivaldi browser guidance.
"""

import asyncio
import json
import logging
import numpy as np
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

import requests
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import uuid
import subprocess
import tempfile
import shutil
from urllib.parse import urlparse, urljoin
import re
from collections import defaultdict

# Import consciousness system components
from ..core.consciousness_bus import ConsciousnessBus
from ..core.event_types import EventType, ConsciousnessEvent, create_learning_progress_event
from ..core.data_models import (
    ConsciousnessState, ComponentStatus, ComponentState,
    LearningProgressData, LearningSession,
    ConsciousnessLearningSession as DataConsciousnessLearningSession,
    LearningContent as DataLearningContent
)
from ..interfaces.consciousness_component import ConsciousnessComponent

logger = logging.getLogger('synapticos.security_tutor_v2')

class LearningPlatform(Enum):
    """Supported learning platforms"""
    FREECODECAMP = "freecodecamp"
    BOOT_DEV = "boot_dev"
    HACKTHEBOX = "hackthebox"
    TRYHACKME = "tryhackme"
    OVERTHEWIRE = "overthewire"
    SCHOOL_ASSIGNMENT = "school_assignment"
    VIVALDI_GUIDED = "vivaldi_guided"
    CUSTOM_CTF = "custom_ctf"

class LearningMode(Enum):
    """Consciousness-driven learning modes"""
    EXPLORATION = "exploration"      # Low consciousness - discovery learning
    FOCUSED = "focused"             # Moderate consciousness - structured learning
    INTENSIVE = "intensive"         # High consciousness - accelerated learning
    BREAKTHROUGH = "breakthrough"   # Peak consciousness - advanced concepts

class CognitiveState(Enum):
    """Cognitive load states"""
    OVERLOADED = "overloaded"      # Too much information
    OPTIMAL = "optimal"            # Perfect learning state
    UNDERUTILIZED = "underutilized" # Could handle more complexity
    FATIGUED = "fatigued"          # Need break or easier content

class ContentType(Enum):
    """Types of educational content"""
    THEORY = "theory"
    PRACTICAL = "practical"
    CHALLENGE = "challenge"
    ASSESSMENT = "assessment"
    GUIDED_WALKTHROUGH = "guided_walkthrough"
    PDF_ANALYSIS = "pdf_analysis"
    BROWSER_GUIDANCE = "browser_guidance"

@dataclass
class ConsciousnessLearningSession:
    """Learning session with consciousness tracking"""
    session_id: str
    user_id: str
    platform: LearningPlatform
    content_id: str
    start_time: datetime
    consciousness_level: float
    learning_mode: LearningMode
    cognitive_state: CognitiveState
    adaptation_history: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    end_time: Optional[datetime] = None
    completion_status: str = "in_progress"
    skill_improvements: Dict[str, float] = field(default_factory=dict)

@dataclass
class LearningContent:
    """Enhanced learning content with consciousness optimization"""
    content_id: str
    title: str
    content_type: ContentType
    difficulty_level: float  # 0.0 to 1.0
    estimated_duration_minutes: int
    consciousness_requirements: Dict[str, float]  # Required consciousness levels
    skills_targeted: List[str]
    content_data: Dict[str, Any]
    prerequisites: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AdaptiveAssessment:
    """Adaptive assessment that adjusts to consciousness level"""
    assessment_id: str
    base_questions: List[Dict[str, Any]]
    consciousness_adaptations: Dict[str, List[Dict[str, Any]]]
    scoring_algorithm: str = "consciousness_weighted"
    time_limits: Dict[str, int] = field(default_factory=dict)

class ConsciousnessLearningEngine:
    """Core learning engine with consciousness adaptation"""
    
    def __init__(self):
        self.adaptation_models = {}
        self.performance_predictors = {}
        self.content_library = {}
        self.learning_analytics = defaultdict(list)
        
    async def adapt_learning_path(self, 
                                user_id: str,
                                consciousness_state: ConsciousnessState,
                                learning_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Adapt learning path based on consciousness state"""
        
        consciousness_level = consciousness_state.consciousness_level
        
        # Determine optimal learning mode
        learning_mode = self._determine_learning_mode(consciousness_level)
        
        # Assess cognitive state
        cognitive_state = self._assess_cognitive_state(consciousness_level, learning_history)
        
        # Generate adaptive recommendations
        recommendations = {
            'learning_mode': learning_mode,
            'cognitive_state': cognitive_state,
            'content_difficulty': self._calculate_optimal_difficulty(consciousness_level),
            'session_duration': self._calculate_optimal_duration(consciousness_level),
            'content_types': self._recommend_content_types(learning_mode),
            'break_intervals': self._calculate_break_intervals(cognitive_state),
            'consciousness_optimization': {
                'target_level': min(1.0, consciousness_level * 1.2),
                'adaptation_frequency': 'real_time' if consciousness_level > 0.7 else 'periodic'
            }
        }
        
        return recommendations
    
    def _determine_learning_mode(self, consciousness_level: float) -> LearningMode:
        """Determine optimal learning mode based on consciousness"""
        if consciousness_level >= 0.8:
            return LearningMode.BREAKTHROUGH
        elif consciousness_level >= 0.6:
            return LearningMode.INTENSIVE
        elif consciousness_level >= 0.4:
            return LearningMode.FOCUSED
        else:
            return LearningMode.EXPLORATION
    
    def _assess_cognitive_state(self, consciousness_level: float, 
                              learning_history: List[Dict[str, Any]]) -> CognitiveState:
        """Assess cognitive state for load balancing"""
        
        # Analyze recent performance
        if learning_history:
            recent_sessions = learning_history[-5:]  # Last 5 sessions
            avg_performance = np.mean([s.get('performance', 0.5) for s in recent_sessions])
            
            if avg_performance > 0.9 and consciousness_level > 0.7:
                return CognitiveState.UNDERUTILIZED
            elif avg_performance < 0.3:
                return CognitiveState.OVERLOADED
            elif consciousness_level < 0.2:
                return CognitiveState.FATIGUED
        
        return CognitiveState.OPTIMAL
    
    def _calculate_optimal_difficulty(self, consciousness_level: float) -> float:
        """Calculate optimal content difficulty"""
        # Base difficulty on consciousness with some challenge
        base_difficulty = consciousness_level * 0.8
        challenge_factor = 0.1 + (consciousness_level * 0.2)
        return min(1.0, base_difficulty + challenge_factor)
    
    def _calculate_optimal_duration(self, consciousness_level: float) -> int:
        """Calculate optimal session duration in minutes"""
        if consciousness_level >= 0.8:
            return 60  # High focus - longer sessions
        elif consciousness_level >= 0.6:
            return 45  # Good focus - standard sessions
        elif consciousness_level >= 0.4:
            return 30  # Moderate focus - shorter sessions
        else:
            return 20  # Low focus - brief sessions
    
    def _recommend_content_types(self, learning_mode: LearningMode) -> List[ContentType]:
        """Recommend content types based on learning mode"""
        mode_mapping = {
            LearningMode.EXPLORATION: [ContentType.THEORY, ContentType.GUIDED_WALKTHROUGH],
            LearningMode.FOCUSED: [ContentType.PRACTICAL, ContentType.THEORY, ContentType.ASSESSMENT],
            LearningMode.INTENSIVE: [ContentType.CHALLENGE, ContentType.PRACTICAL, ContentType.ASSESSMENT],
            LearningMode.BREAKTHROUGH: [ContentType.CHALLENGE, ContentType.ASSESSMENT]
        }
        return mode_mapping.get(learning_mode, [ContentType.THEORY])
    
    def _calculate_break_intervals(self, cognitive_state: CognitiveState) -> Dict[str, int]:
        """Calculate optimal break intervals"""
        intervals = {
            CognitiveState.OPTIMAL: {'short_break': 15, 'long_break': 60},
            CognitiveState.OVERLOADED: {'short_break': 10, 'long_break': 30},
            CognitiveState.UNDERUTILIZED: {'short_break': 25, 'long_break': 90},
            CognitiveState.FATIGUED: {'short_break': 5, 'long_break': 20}
        }
        return intervals.get(cognitive_state, intervals[CognitiveState.OPTIMAL])

class AdaptiveContentGenerator:
    """Generate adaptive content based on consciousness and skill level"""
    
    def __init__(self):
        self.content_templates = {}
        self.difficulty_scalers = {}
        self.consciousness_enhancers = {}
        
    async def generate_exercise(self, 
                              skill_domain: str,
                              consciousness_level: float,
                              user_skill_level: float,
                              learning_mode: LearningMode) -> LearningContent:
        """Generate adaptive exercise"""
        
        # Calculate target difficulty
        target_difficulty = self._calculate_target_difficulty(
            consciousness_level, user_skill_level, learning_mode
        )
        
        # Select appropriate exercise template
        exercise_template = self._select_exercise_template(skill_domain, target_difficulty)
        
        # Generate consciousness-optimized content
        content_data = await self._generate_optimized_content(
            exercise_template, consciousness_level, learning_mode
        )
        
        # Create learning content object
        content = LearningContent(
            content_id=str(uuid.uuid4()),
            title=f"{skill_domain.title()} Challenge - Level {target_difficulty:.1f}",
            content_type=ContentType.CHALLENGE,
            difficulty_level=target_difficulty,
            estimated_duration_minutes=self._estimate_duration(target_difficulty, learning_mode),
            consciousness_requirements={
                'minimum': max(0.0, consciousness_level - 0.2),
                'optimal': consciousness_level,
                'maximum': min(1.0, consciousness_level + 0.3)
            },
            skills_targeted=[skill_domain],
            content_data=content_data,
            metadata={
                'generated_for_consciousness': consciousness_level,
                'generated_for_mode': learning_mode.value,
                'adaptable': True
            }
        )
        
        return content
    
    def _calculate_target_difficulty(self, consciousness_level: float,
                                   user_skill_level: float,
                                   learning_mode: LearningMode) -> float:
        """Calculate optimal difficulty target"""
        
        # Base difficulty on user skill level
        base_difficulty = user_skill_level
        
        # Apply consciousness modifier
        consciousness_modifier = (consciousness_level - 0.5) * 0.3
        
        # Apply learning mode modifier
        mode_modifiers = {
            LearningMode.EXPLORATION: -0.1,
            LearningMode.FOCUSED: 0.0,
            LearningMode.INTENSIVE: 0.2,
            LearningMode.BREAKTHROUGH: 0.4
        }
        mode_modifier = mode_modifiers.get(learning_mode, 0.0)
        
        target_difficulty = base_difficulty + consciousness_modifier + mode_modifier
        return max(0.1, min(1.0, target_difficulty))
    
    def _select_exercise_template(self, skill_domain: str, difficulty: float) -> Dict[str, Any]:
        """Select appropriate exercise template"""
        
        # Simplified template selection
        templates = {
            'network_security': {
                'basic': {
                    'type': 'network_analysis',
                    'scenario': 'Simple packet analysis',
                    'tools': ['wireshark'],
                    'complexity': 'low'
                },
                'intermediate': {
                    'type': 'intrusion_detection',
                    'scenario': 'Detect network intrusion',
                    'tools': ['nmap', 'wireshark', 'snort'],
                    'complexity': 'medium'
                },
                'advanced': {
                    'type': 'advanced_persistence',
                    'scenario': 'Multi-stage attack detection',
                    'tools': ['custom_scripts', 'multiple_monitors'],
                    'complexity': 'high'
                }
            }
        }
        
        domain_templates = templates.get(skill_domain, templates['network_security'])
        
        if difficulty <= 0.3:
            return domain_templates['basic']
        elif difficulty <= 0.7:
            return domain_templates['intermediate']
        else:
            return domain_templates['advanced']
    
    async def _generate_optimized_content(self, template: Dict[str, Any],
                                        consciousness_level: float,
                                        learning_mode: LearningMode) -> Dict[str, Any]:
        """Generate consciousness-optimized content"""
        
        content = {
            'scenario': template['scenario'],
            'objectives': self._generate_objectives(template, consciousness_level),
            'resources': template.get('tools', []),
            'hints': self._generate_hints(template, consciousness_level),
            'success_criteria': self._generate_success_criteria(template),
            'consciousness_adaptations': {
                'difficulty_scaling': True,
                'hint_availability': consciousness_level < 0.6,
                'time_pressure': consciousness_level > 0.7,
                'bonus_challenges': consciousness_level > 0.8
            }
        }
        
        return content
    
    def _generate_objectives(self, template: Dict[str, Any], consciousness_level: float) -> List[str]:
        """Generate consciousness-appropriate objectives"""
        base_objectives = [
            f"Analyze the {template['scenario'].lower()}",
            "Identify security issues",
            "Recommend solutions"
        ]
        
        if consciousness_level > 0.7:
            base_objectives.extend([
                "Explain the underlying attack vectors",
                "Propose preventive measures",
                "Design detection signatures"
            ])
        
        return base_objectives
    
    def _generate_hints(self, template: Dict[str, Any], consciousness_level: float) -> List[str]:
        """Generate consciousness-appropriate hints"""
        if consciousness_level > 0.6:
            return []  # High consciousness - no hints needed
        
        hints = [
            f"Start by examining the {template['scenario'].lower()}",
            f"Use {template.get('tools', ['standard tools'])[0]} for analysis",
            "Look for unusual patterns or behaviors"
        ]
        
        if consciousness_level < 0.4:
            hints.extend([
                "Check the documentation for tool usage",
                "Compare with known good examples",
                "Focus on one objective at a time"
            ])
        
        return hints
    
    def _generate_success_criteria(self, template: Dict[str, Any]) -> List[str]:
        """Generate success criteria for the exercise"""
        return [
            "Correctly identify the main security issue",
            "Provide a working solution",
            "Explain the reasoning behind the solution",
            "Demonstrate understanding of security principles"
        ]
    
    def _estimate_duration(self, difficulty: float, learning_mode: LearningMode) -> int:
        """Estimate exercise duration in minutes"""
        base_duration = int(30 + (difficulty * 60))  # 30-90 minutes base
        
        mode_multipliers = {
            LearningMode.EXPLORATION: 1.5,    # Slower, more discovery
            LearningMode.FOCUSED: 1.0,        # Standard pace
            LearningMode.INTENSIVE: 0.8,      # Faster pace
            LearningMode.BREAKTHROUGH: 0.6    # Rapid completion
        }
        
        multiplier = mode_multipliers.get(learning_mode, 1.0)
        return int(base_duration * multiplier)

class SecurityTutorV2(ConsciousnessComponent):
    """Enhanced Security Tutor with consciousness integration"""
    
    def __init__(self, storage_path: str = "/var/lib/synapticos/security_tutor"):
        super().__init__("security_tutor_v2", "adaptive_learning_system")
        
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Core components
        self.learning_engine = ConsciousnessLearningEngine()
        self.content_generator = AdaptiveContentGenerator()
        
        # Active sessions
        self.active_sessions: Dict[str, ConsciousnessLearningSession] = {}
        self.session_history: List[ConsciousnessLearningSession] = []
        
        # Learning analytics
        self.analytics = {
            'total_sessions': 0,
            'average_completion_rate': 0.0,
            'consciousness_correlation': 0.0,
            'skill_improvement_rate': 0.0,
            'adaptive_success_rate': 0.0
        }
        
        # Content library
        self.content_library: Dict[str, LearningContent] = {}
        
        # Platform integrations
        self.platform_handlers = {}
        
    async def start(self) -> bool:
        """Start the security tutor system"""
        try:
            self.is_running = True
            
            # Initialize platform handlers
            await self._initialize_platform_handlers()
            
            # Load content library
            await self._load_content_library()
            
            # Start background tasks
            asyncio.create_task(self._analytics_loop())
            asyncio.create_task(self._session_monitoring_loop())
            
            await self.set_component_state(ComponentState.HEALTHY)
            logger.info("Security Tutor v2 started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Security Tutor v2: {e}")
            await self.set_component_state(ComponentState.FAILED)
            return False
    
    async def stop(self) -> None:
        """Stop the security tutor system"""
        self.is_running = False
        
        # Save active sessions
        for session in self.active_sessions.values():
            await self._save_session(session)
        
        logger.info("Security Tutor v2 stopped")
    
    async def process_event(self, event: ConsciousnessEvent) -> bool:
        """Process consciousness events"""
        try:
            if event.event_type == EventType.CONSCIOUSNESS_EMERGENCE:
                await self._handle_consciousness_emergence(event)
            elif event.event_type == EventType.NEURAL_EVOLUTION:
                await self._handle_neural_evolution(event)
            elif event.event_type == EventType.CONTEXT_UPDATE:
                await self._handle_context_update(event)
            return True
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            return False
    
    async def get_health_status(self) -> ComponentStatus:
        """Get current health status"""
        self.status.last_heartbeat = datetime.now()
        self.status.throughput = len(self.active_sessions)
        return self.status
    
    async def update_configuration(self, config: Dict[str, Any]) -> bool:
        """Update tutor configuration"""
        try:
            # Update learning parameters
            if 'difficulty_scaling' in config:
                # Update difficulty scaling parameters
                pass
            
            if 'consciousness_thresholds' in config:
                # Update consciousness adaptation thresholds
                pass
                
            return True
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    async def start_learning_session(self, 
                                   user_id: str,
                                   platform: LearningPlatform,
                                   content_id: Optional[str] = None,
                                   consciousness_state: Optional[ConsciousnessState] = None) -> str:
        """Start a new learning session"""
        
        session_id = str(uuid.uuid4())
        
        # Get current consciousness state if not provided
        if consciousness_state is None:
            consciousness_state = await self._get_current_consciousness_state()
        
        consciousness_level = consciousness_state.consciousness_level if consciousness_state else 0.5
        
        # Determine learning mode and cognitive state
        learning_mode = self.learning_engine._determine_learning_mode(consciousness_level)
        cognitive_state = self.learning_engine._assess_cognitive_state(consciousness_level, [])
        
        # Create session
        session = ConsciousnessLearningSession(
            session_id=session_id,
            user_id=user_id,
            platform=platform,
            content_id=content_id or "adaptive_generated",
            start_time=datetime.now(),
            consciousness_level=consciousness_level,
            learning_mode=learning_mode,
            cognitive_state=cognitive_state
        )
        
        # Adapt learning path
        adaptations = await self.learning_engine.adapt_learning_path(
            user_id, consciousness_state, []
        )
        
        session.adaptation_history.append({
            'timestamp': datetime.now(),
            'adaptations': adaptations,
            'trigger': 'session_start'
        })
        
        # Store active session
        self.active_sessions[session_id] = session
        
        # Generate or retrieve content
        if content_id is None:
            # Generate adaptive content
            content = await self.content_generator.generate_exercise(
                'network_security',  # Default domain
                consciousness_level,
                0.5,  # Default skill level
                learning_mode
            )
            self.content_library[content.content_id] = content
            session.content_id = content.content_id
        
        logger.info(f"Started learning session {session_id} for user {user_id}")
        
        # Publish learning start event
        if self.consciousness_bus:
            learning_event = create_learning_progress_event(
                source_component=self.component_id,
                learning_data=LearningProgressData(
                    user_id=user_id,
                    session_id=session_id,
                    skill_domain='security',
                    progress_percentage=0.0,
                    consciousness_level=consciousness_level,
                    performance_score=0.0,
                    learning_velocity=1.0,
                    adaptation_triggers=['session_start']
                ),
                target_components=["personal_context_v2", "neural_darwinism_v2"]
            )
            await self.consciousness_bus.publish(learning_event)
        
        return session_id
    
    async def update_session_progress(self, 
                                    session_id: str,
                                    progress_data: Dict[str, Any],
                                    consciousness_state: Optional[ConsciousnessState] = None) -> bool:
        """Update learning session progress"""
        
        if session_id not in self.active_sessions:
            logger.error(f"Session {session_id} not found")
            return False
        
        session = self.active_sessions[session_id]
        
        # Get current consciousness state
        if consciousness_state is None:
            consciousness_state = await self._get_current_consciousness_state()
        
        current_consciousness = consciousness_state.consciousness_level if consciousness_state else 0.5
        
        # Update performance metrics
        session.performance_metrics.update(progress_data.get('metrics', {}))
        
        # Check if consciousness has changed significantly
        consciousness_change = abs(current_consciousness - session.consciousness_level)
        if consciousness_change > 0.2:
            # Adapt learning path dynamically
            new_adaptations = await self.learning_engine.adapt_learning_path(
                session.user_id, consciousness_state, session.adaptation_history
            )
            
            session.adaptation_history.append({
                'timestamp': datetime.now(),
                'adaptations': new_adaptations,
                'trigger': 'consciousness_change',
                'consciousness_delta': consciousness_change
            })
            
            # Update session consciousness level
            session.consciousness_level = current_consciousness
            
            logger.info(f"Adapted session {session_id} due to consciousness change: {consciousness_change:.3f}")
        
        # Publish progress update
        if self.consciousness_bus:
            progress_percentage = progress_data.get('progress_percentage', 0.0)
            performance_score = progress_data.get('performance_score', 0.0)
            
            learning_event = create_learning_progress_event(
                source_component=self.component_id,
                learning_data=LearningProgressData(
                    user_id=session.user_id,
                    session_id=session_id,
                    skill_domain='security',
                    progress_percentage=progress_percentage,
                    consciousness_level=current_consciousness,
                    performance_score=performance_score,
                    learning_velocity=progress_data.get('learning_velocity', 1.0),
                    adaptation_triggers=progress_data.get('adaptation_triggers', [])
                ),
                target_components=["personal_context_v2", "neural_darwinism_v2"]
            )
            await self.consciousness_bus.publish(learning_event)
        
        return True
    
    async def complete_session(self, session_id: str, completion_data: Dict[str, Any]) -> bool:
        """Complete a learning session"""
        
        if session_id not in self.active_sessions:
            logger.error(f"Session {session_id} not found")
            return False
        
        session = self.active_sessions[session_id]
        session.end_time = datetime.now()
        session.completion_status = completion_data.get('status', 'completed')
        session.skill_improvements = completion_data.get('skill_improvements', {})
        
        # Calculate final performance metrics
        session_duration = (session.end_time - session.start_time).total_seconds() / 60  # minutes
        final_performance = completion_data.get('final_score', 0.0)
        
        session.performance_metrics.update({
            'session_duration_minutes': session_duration,
            'final_performance': final_performance,
            'consciousness_stability': self._calculate_consciousness_stability(session),
            'adaptation_effectiveness': self._calculate_adaptation_effectiveness(session)
        })
        
        # Move to history
        self.session_history.append(session)
        del self.active_sessions[session_id]
        
        # Save session
        await self._save_session(session)
        
        # Update analytics
        self._update_analytics(session)
        
        logger.info(f"Completed learning session {session_id}")
        
        # Publish completion event
        if self.consciousness_bus:
            learning_event = create_learning_progress_event(
                source_component=self.component_id,
                learning_data=LearningProgressData(
                    user_id=session.user_id,
                    session_id=session_id,
                    skill_domain='security',
                    progress_percentage=100.0,
                    consciousness_level=session.consciousness_level,
                    performance_score=final_performance,
                    learning_velocity=completion_data.get('learning_velocity', 1.0),
                    adaptation_triggers=['session_complete']
                ),
                target_components=["personal_context_v2", "neural_darwinism_v2"]
            )
            await self.consciousness_bus.publish(learning_event)
        
        return True
    
    async def get_adaptive_content(self, 
                                 user_id: str,
                                 skill_domain: str,
                                 consciousness_state: Optional[ConsciousnessState] = None) -> Optional[LearningContent]:
        """Get adaptive content for user"""
        
        if consciousness_state is None:
            consciousness_state = await self._get_current_consciousness_state()
        
        consciousness_level = consciousness_state.consciousness_level if consciousness_state else 0.5
        learning_mode = self.learning_engine._determine_learning_mode(consciousness_level)
        
        # Generate adaptive content
        content = await self.content_generator.generate_exercise(
            skill_domain,
            consciousness_level,
            0.5,  # Default skill level - should be retrieved from context
            learning_mode
        )
        
        # Store in library
        self.content_library[content.content_id] = content
        
        return content
    
    async def get_session_analytics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get learning session analytics"""
        
        if user_id:
            # Filter sessions for specific user
            user_sessions = [s for s in self.session_history if s.user_id == user_id]
            active_user_sessions = [s for s in self.active_sessions.values() if s.user_id == user_id]
        else:
            user_sessions = self.session_history
            active_user_sessions = list(self.active_sessions.values())
        
        if not user_sessions and not active_user_sessions:
            return {'status': 'no_data'}
        
        all_sessions = user_sessions + active_user_sessions
        
        # Calculate analytics
        total_sessions = len(all_sessions)
        completed_sessions = [s for s in all_sessions if s.completion_status == 'completed']
        completion_rate = len(completed_sessions) / total_sessions if total_sessions > 0 else 0.0
        
        avg_consciousness = np.mean([s.consciousness_level for s in all_sessions])
        avg_performance = np.mean([
            s.performance_metrics.get('final_performance', 0.0) 
            for s in completed_sessions
        ]) if completed_sessions else 0.0
        
        # Consciousness correlation analysis
        if len(completed_sessions) >= 3:
            consciousness_levels = [s.consciousness_level for s in completed_sessions]
            performance_scores = [s.performance_metrics.get('final_performance', 0.0) for s in completed_sessions]
            consciousness_correlation = np.corrcoef(consciousness_levels, performance_scores)[0, 1]
            if np.isnan(consciousness_correlation):
                consciousness_correlation = 0.0
        else:
            consciousness_correlation = 0.0
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': len(active_user_sessions),
            'completion_rate': completion_rate,
            'average_consciousness_level': avg_consciousness,
            'average_performance': avg_performance,
            'consciousness_performance_correlation': consciousness_correlation,
            'learning_mode_distribution': self._calculate_mode_distribution(all_sessions),
            'skill_improvement_trends': self._calculate_skill_trends(completed_sessions)
        }
    
    # Event handlers
    async def _handle_consciousness_emergence(self, event: ConsciousnessEvent):
        """Handle consciousness emergence events"""
        emergence_data = event.data.get('emergence_prediction', {})
        
        # Update all active sessions with emergence data
        for session in self.active_sessions.values():
            if emergence_data.get('emergence_probability', 0.0) > 0.7:
                # Switch to breakthrough mode for high emergence
                session.learning_mode = LearningMode.BREAKTHROUGH
                session.adaptation_history.append({
                    'timestamp': datetime.now(),
                    'adaptations': {'learning_mode': 'breakthrough'},
                    'trigger': 'consciousness_emergence',
                    'emergence_strength': emergence_data.get('emergence_probability', 0.0)
                })
    
    async def _handle_neural_evolution(self, event: ConsciousnessEvent):
        """Handle neural evolution events"""
        evolution_data = event.data.get('evolution_data', {})
        
        # Adapt active sessions based on evolution results
        for session in self.active_sessions.values():
            consciousness_improvement = evolution_data.get('fitness_improvements', {}).get('overall', 0.0)
            
            if consciousness_improvement > 0.1:
                # Increase difficulty or pace for improving consciousness
                session.adaptation_history.append({
                    'timestamp': datetime.now(),
                    'adaptations': {'difficulty_boost': consciousness_improvement},
                    'trigger': 'neural_evolution',
                    'evolution_cycle': evolution_data.get('evolution_cycle', 0)
                })
    
    async def _handle_context_update(self, event: ConsciousnessEvent):
        """Handle context update events"""
        context_data = event.data.get('context_update', {})
        
        # Update active sessions based on context changes
        for session in self.active_sessions.values():
            skill_changes = context_data.get('skill_changes', {})
            if skill_changes:
                session.skill_improvements.update(skill_changes)
    
    # Helper methods
    async def _initialize_platform_handlers(self):
        """Initialize platform-specific handlers"""
        self.platform_handlers = {
            LearningPlatform.HACKTHEBOX: self._handle_hackthebox,
            LearningPlatform.TRYHACKME: self._handle_tryhackme,
            LearningPlatform.FREECODECAMP: self._handle_freecodecamp,
            LearningPlatform.SCHOOL_ASSIGNMENT: self._handle_school_assignment
        }
    
    async def _load_content_library(self):
        """Load content library from storage"""
        content_file = self.storage_path / "content_library.json"
        if content_file.exists():
            try:
                with open(content_file, 'r') as f:
                    content_data = json.load(f)
                    for content_id, data in content_data.items():
                        # Deserialize content objects
                        self.content_library[content_id] = self._deserialize_content(data)
            except Exception as e:
                logger.error(f"Error loading content library: {e}")
    
    async def _save_session(self, session: ConsciousnessLearningSession):
        """Save session to storage"""
        session_file = self.storage_path / f"session_{session.session_id}.json"
        try:
            with open(session_file, 'w') as f:
                json.dump(self._serialize_session(session), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving session {session.session_id}: {e}")
    
    async def _get_current_consciousness_state(self) -> Optional[ConsciousnessState]:
        """Get current consciousness state"""
        if self.state_manager:
            try:
                return await self.state_manager.get_consciousness_state()
            except Exception as e:
                logger.error(f"Error getting consciousness state: {e}")
        return None
    
    def _calculate_consciousness_stability(self, session: ConsciousnessLearningSession) -> float:
        """Calculate consciousness stability during session"""
        adaptations = session.adaptation_history
        if len(adaptations) <= 1:
            return 1.0  # Stable if no adaptations needed
        
        consciousness_changes = [
            a.get('consciousness_delta', 0.0) for a in adaptations 
            if 'consciousness_delta' in a
        ]
        
        if consciousness_changes:
            return 1.0 - np.std(consciousness_changes)
        return 1.0
    
    def _calculate_adaptation_effectiveness(self, session: ConsciousnessLearningSession) -> float:
        """Calculate effectiveness of adaptations"""
        # Simple effectiveness measure based on final performance
        final_performance = session.performance_metrics.get('final_performance', 0.0)
        num_adaptations = len(session.adaptation_history)
        
        if num_adaptations == 0:
            return final_performance
        
        # Higher performance with fewer adaptations is more effective
        effectiveness = final_performance * (1.0 - (num_adaptations * 0.1))
        return max(0.0, min(1.0, effectiveness))
    
    def _update_analytics(self, completed_session: ConsciousnessLearningSession):
        """Update global analytics with completed session"""
        self.analytics['total_sessions'] += 1
        
        # Update average completion rate
        total_sessions = self.analytics['total_sessions']
        completed_count = sum(1 for s in self.session_history if s.completion_status == 'completed')
        self.analytics['average_completion_rate'] = completed_count / total_sessions
        
        # Update consciousness correlation
        if len(self.session_history) >= 10:
            completed_sessions = [s for s in self.session_history if s.completion_status == 'completed']
            if len(completed_sessions) >= 3:
                consciousness_levels = [s.consciousness_level for s in completed_sessions[-20:]]
                performance_scores = [s.performance_metrics.get('final_performance', 0.0) for s in completed_sessions[-20:]]
                correlation = np.corrcoef(consciousness_levels, performance_scores)[0, 1]
                if not np.isnan(correlation):
                    self.analytics['consciousness_correlation'] = correlation
    
    def _calculate_mode_distribution(self, sessions: List[ConsciousnessLearningSession]) -> Dict[str, float]:
        """Calculate learning mode distribution"""
        if not sessions:
            return {}
        
        mode_counts = defaultdict(int)
        for session in sessions:
            mode_counts[session.learning_mode.value] += 1
        
        total = len(sessions)
        return {mode: count / total for mode, count in mode_counts.items()}
    
    def _calculate_skill_trends(self, sessions: List[ConsciousnessLearningSession]) -> Dict[str, float]:
        """Calculate skill improvement trends"""
        if not sessions:
            return {}
        
        skill_improvements = defaultdict(list)
        for session in sessions:
            for skill, improvement in session.skill_improvements.items():
                skill_improvements[skill].append(improvement)
        
        trends = {}
        for skill, improvements in skill_improvements.items():
            if len(improvements) >= 2:
                # Calculate trend slope
                x = list(range(len(improvements)))
                trend = np.polyfit(x, improvements, 1)[0]
                trends[skill] = trend
        
        return trends
    
    def _serialize_session(self, session: ConsciousnessLearningSession) -> Dict[str, Any]:
        """Serialize session for storage"""
        return {
            'session_id': session.session_id,
            'user_id': session.user_id,
            'platform': session.platform.value,
            'content_id': session.content_id,
            'start_time': session.start_time.isoformat(),
            'end_time': session.end_time.isoformat() if session.end_time else None,
            'consciousness_level': session.consciousness_level,
            'learning_mode': session.learning_mode.value,
            'cognitive_state': session.cognitive_state.value,
            'completion_status': session.completion_status,
            'adaptation_history': session.adaptation_history,
            'performance_metrics': session.performance_metrics,
            'skill_improvements': session.skill_improvements
        }
    
    def _deserialize_content(self, data: Dict[str, Any]) -> LearningContent:
        """Deserialize content from storage"""
        return LearningContent(
            content_id=data['content_id'],
            title=data['title'],
            content_type=ContentType(data['content_type']),
            difficulty_level=data['difficulty_level'],
            estimated_duration_minutes=data['estimated_duration_minutes'],
            consciousness_requirements=data['consciousness_requirements'],
            skills_targeted=data['skills_targeted'],
            content_data=data['content_data'],
            prerequisites=data.get('prerequisites', []),
            metadata=data.get('metadata', {})
        )
    
    # Background loops
    async def _analytics_loop(self):
        """Background analytics processing"""
        while self.is_running:
            try:
                # Update analytics
                await self._update_global_analytics()
                await asyncio.sleep(300)  # Every 5 minutes
            except Exception as e:
                logger.error(f"Error in analytics loop: {e}")
                await asyncio.sleep(300)
    
    async def _session_monitoring_loop(self):
        """Monitor active sessions for timeouts and adaptations"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Check for session timeouts
                for session_id, session in list(self.active_sessions.items()):
                    session_duration = (current_time - session.start_time).total_seconds() / 60
                    
                    # Timeout after 4 hours
                    if session_duration > 240:
                        logger.warning(f"Session {session_id} timed out")
                        await self.complete_session(session_id, {
                            'status': 'timeout',
                            'final_score': 0.0
                        })
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in session monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _update_global_analytics(self):
        """Update global analytics"""
        try:
            # Calculate system-wide metrics
            total_active = len(self.active_sessions)
            total_completed = len([s for s in self.session_history if s.completion_status == 'completed'])
            
            # Update analytics with current system state
            if hasattr(self, 'status'):
                self.status.throughput = total_active
                self.status.custom_metrics = {
                    'active_sessions': total_active,
                    'completed_sessions': total_completed,
                    'consciousness_correlation': self.analytics.get('consciousness_correlation', 0.0)
                }
                
        except Exception as e:
            logger.error(f"Error updating global analytics: {e}")
    
    # Platform-specific handlers (simplified implementations)
    async def _handle_hackthebox(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HackTheBox platform integration"""
        return {'status': 'hackthebox_integration_placeholder'}
    
    async def _handle_tryhackme(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle TryHackMe platform integration"""
        return {'status': 'tryhackme_integration_placeholder'}
    
    async def _handle_freecodecamp(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle FreeCodeCamp platform integration"""
        return {'status': 'freecodecamp_integration_placeholder'}
    
    async def _handle_school_assignment(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle school assignment processing"""
        return {'status': 'school_assignment_integration_placeholder'}

# Export main class for audit compatibility
SecurityTutorV2Engine = SecurityTutorV2

import asyncio
import json
import logging
import numpy as np
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

import requests
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import uuid
import subprocess
import tempfile
import shutil
from urllib.parse import urlparse, urljoin
import re
from collections import defaultdict

# Import consciousness system components
from ..core.consciousness_bus import ConsciousnessBus
from ..core.event_types import EventType, ConsciousnessEvent, create_learning_progress_event
from ..core.data_models import (
    ConsciousnessState, ComponentStatus, ComponentState,
    LearningProgressData, LearningSession,
    ConsciousnessLearningSession as DataConsciousnessLearningSession,
    LearningContent as DataLearningContent
)
from ..core.event_types import ConsciousnessEvent
from ..interfaces.consciousness_component import ConsciousnessComponent
from .security_tutor_helpers import (
    ConsciousnessLearningEngine, AdaptiveContentGenerator,
    VivaldiBrowserGuidanceSystem, PDFAssignmentProcessor,
    BrowserContext, PDFAssignmentData
)

logger = logging.getLogger('synapticos.security_tutor_v2')

class LearningPlatform(Enum):
    """Supported learning platforms"""
    FREECODECAMP = "freecodecamp"
    BOOT_DEV = "boot_dev"
    HACKTHEBOX = "hackthebox"
    TRYHACKME = "tryhackme"
    OVERTHEWIRE = "overthewire"
    SCHOOL_ASSIGNMENT = "school_assignment"
    VIVALDI_GUIDED = "vivaldi_guided"
    CUSTOM_CTF = "custom_ctf"

class LearningMode(Enum):
    """Consciousness-driven learning modes"""
    EXPLORATION = "exploration"      # Low consciousness - discovery learning
    FOCUSED = "focused"             # Moderate consciousness - structured learning
    INTENSIVE = "intensive"         # High consciousness - accelerated learning
    BREAKTHROUGH = "breakthrough"   # Peak consciousness - advanced concepts

class CognitiveState(Enum):
    """Cognitive load states"""
    OVERLOADED = "overloaded"      # Too much information
    OPTIMAL = "optimal"            # Perfect learning state
    UNDERUTILIZED = "underutilized" # Could handle more complexity
    FATIGUED = "fatigued"          # Need break or easier content

class ContentType(Enum):
    """Types of educational content"""
    THEORY = "theory"
    PRACTICAL = "practical"
    CHALLENGE = "challenge"
    ASSESSMENT = "assessment"
    GUIDED_WALKTHROUGH = "guided_walkthrough"
    PDF_ANALYSIS = "pdf_analysis"
    BROWSER_GUIDANCE = "browser_guidance"

@dataclass
class ConsciousnessLearningSession:
    """Learning session with consciousness tracking"""
    session_id: str
    user_id: str
    platform: LearningPlatform
    content_id: str
    start_time: datetime
    consciousness_level: float
    learning_mode: LearningMode
    cognitive_state: CognitiveState
    adaptation_history: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    consciousness_trajectory: List[Tuple[datetime, float]] = field(default_factory=list)
    browser_session_id: Optional[str] = None
    current_url: Optional[str] = None
    progress_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize progress data if empty"""
        if not self.progress_data:
            self.progress_data = {
                'history': [],
                'current_content': {},
                'difficulty_adjustment': 'maintain',
                'browser_guidance': {},
                'consciousness_adaptations': []
            }

@dataclass
class LearningContent:
    """Enhanced learning content with consciousness optimization"""
    content_id: str
    title: str
    platform: LearningPlatform
    content_type: ContentType
    difficulty_level: str
    consciousness_optimized: bool
    content_data: Dict[str, Any]
    prerequisites: List[str] = field(default_factory=list)
    estimated_duration: int = 30  # minutes
    consciousness_requirements: Dict[str, float] = field(default_factory=dict)

@dataclass
class PlatformIntegration:
    """Platform-specific integration configuration"""
    platform: LearningPlatform
    base_url: str
    api_endpoints: Dict[str, str]
    authentication: Dict[str, str]
    browser_automation: bool = False
    pdf_processing: bool = False
    custom_handlers: Dict[str, str] = field(default_factory=dict)

@dataclass
class VivaldiBrowserSession:
    """Vivaldi browser session for guided learning"""
    session_id: str
    user_id: str
    browser_process: Optional[subprocess.Popen]
    current_url: str
    guidance_active: bool
    screenshot_path: Optional[str] = None
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)

class ConsciousnessAwareSecurityTutorV2(ConsciousnessComponent):
    """Enhanced Security Tutor with consciousness integration and multi-platform support"""
    
    def __init__(self, 
                 storage_path: str = "/var/lib/synapticos/security_tutor_v2",
                 vivaldi_path: str = "/usr/bin/vivaldi"):
        super().__init__("security_tutor_v2", "educational_system")
        
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.vivaldi_path = vivaldi_path
        
        # Core components
        self.active_sessions: Dict[str, ConsciousnessLearningSession] = {}
        self.browser_sessions: Dict[str, VivaldiBrowserSession] = {}
        self.learning_content: Dict[str, LearningContent] = {}
        
        # Platform integrations
        self.platform_integrations = self._initialize_platform_integrations()
        
        # Consciousness learning components
        self.consciousness_learning_engine = ConsciousnessLearningEngine()
        self.adaptive_content_generator = AdaptiveContentGenerator()
        self.browser_guidance_system = VivaldiBrowserGuidanceSystem(vivaldi_path)
        self.pdf_processor = PDFAssignmentProcessor()
        
        # Learning analytics
        self.learning_analytics = {
            'active_sessions': 0,
            'total_sessions_completed': 0,
            'consciousness_adaptations': 0,
            'platform_interactions': defaultdict(int),
            'average_learning_effectiveness': 0.0
        }
        
        # Background tasks
        self.background_tasks = []
        
    def _initialize_platform_integrations(self) -> Dict[LearningPlatform, PlatformIntegration]:
        """Initialize platform-specific integrations"""
        return {
            LearningPlatform.FREECODECAMP: PlatformIntegration(
                platform=LearningPlatform.FREECODECAMP,
                base_url="https://www.freecodecamp.org",
                api_endpoints={
                    "curriculum": "/api/curriculum",
                    "progress": "/api/user/progress",
                    "challenges": "/api/challenges"
                },
                authentication={},
                browser_automation=True,
                custom_handlers={
                    "challenge_completion": "handle_freecodecamp_challenge",
                    "progress_tracking": "track_freecodecamp_progress"
                }
            ),
            
            LearningPlatform.BOOT_DEV: PlatformIntegration(
                platform=LearningPlatform.BOOT_DEV,
                base_url="https://boot.dev",
                api_endpoints={
                    "courses": "/api/courses",
                    "lessons": "/api/lessons",
                    "progress": "/api/progress"
                },
                authentication={},
                browser_automation=True,
                custom_handlers={
                    "lesson_completion": "handle_bootdev_lesson",
                    "coding_exercise": "guide_bootdev_coding"
                }
            ),
            
            LearningPlatform.HACKTHEBOX: PlatformIntegration(
                platform=LearningPlatform.HACKTHEBOX,
                base_url="https://app.hackthebox.com",
                api_endpoints={
                    "machines": "/api/v4/machine/list",
                    "challenges": "/api/v4/challenge/list",
                    "progress": "/api/v4/user/profile"
                },
                authentication={},
                browser_automation=True,
                custom_handlers={
                    "machine_guidance": "guide_htb_machine",
                    "challenge_hints": "provide_htb_hints",
                    "writeup_analysis": "analyze_htb_writeup"
                }
            ),
            
            LearningPlatform.TRYHACKME: PlatformIntegration(
                platform=LearningPlatform.TRYHACKME,
                base_url="https://tryhackme.com",
                api_endpoints={
                    "rooms": "/api/rooms",
                    "tasks": "/api/tasks",
                    "progress": "/api/user/progress"
                },
                authentication={},
                browser_automation=True,
                custom_handlers={
                    "room_guidance": "guide_thm_room",
                    "task_completion": "track_thm_task",
                    "hint_system": "provide_thm_hints"
                }
            ),
            
            LearningPlatform.OVERTHEWIRE: PlatformIntegration(
                platform=LearningPlatform.OVERTHEWIRE,
                base_url="https://overthewire.org",
                api_endpoints={},
                authentication={},
                browser_automation=True,
                custom_handlers={
                    "wargame_guidance": "guide_otw_wargame",
                    "ssh_assistance": "assist_otw_ssh",
                    "level_progression": "track_otw_progress"
                }
            ),
            
            LearningPlatform.SCHOOL_ASSIGNMENT: PlatformIntegration(
                platform=LearningPlatform.SCHOOL_ASSIGNMENT,
                base_url="",
                api_endpoints={},
                authentication={},
                pdf_processing=True,
                custom_handlers={
                    "pdf_analysis": "analyze_assignment_pdf",
                    "syllabus_parsing": "parse_syllabus",
                    "assignment_guidance": "guide_assignment_completion"
                }
            ),
            
            LearningPlatform.VIVALDI_GUIDED: PlatformIntegration(
                platform=LearningPlatform.VIVALDI_GUIDED,
                base_url="",
                api_endpoints={},
                authentication={},
                browser_automation=True,
                custom_handlers={
                    "browser_guidance": "provide_browser_guidance",
                    "screenshot_analysis": "analyze_browser_screenshot",
                    "interaction_tracking": "track_browser_interactions"
                }
            )
        }
    
    async def start(self) -> bool:
        """Start the consciousness-aware security tutor"""
        self.is_running = True
        return await self._initialize_tutor()
    
    async def stop(self) -> None:
        """Stop the security tutor"""
        self.is_running = False
        await self._shutdown_tutor()
    
    async def process_event(self, event: ConsciousnessEvent) -> bool:
        """Process consciousness events"""
        try:
            if event.event_type == EventType.NEURAL_EVOLUTION:
                await self._handle_consciousness_evolution(event)
            elif event.event_type == EventType.CONSCIOUSNESS_EMERGENCE:
                await self._handle_consciousness_emergence(event)
            elif event.event_type == EventType.LEARNING_PROGRESS:
                await self._handle_learning_progress(event)
            return True
        except Exception as e:
            self.logger.error(f"Error processing event: {e}")
            return False
    
    async def get_health_status(self) -> ComponentStatus:
        """Get current health status"""
        self.status.last_heartbeat = datetime.now()
        
        # Update metrics
        self.status.response_time_ms = 50.0  # Average response time
        self.status.throughput = len(self.active_sessions)
        
        return self.status
    
    async def update_configuration(self, config: Dict[str, Any]) -> bool:
        """Update component configuration"""
        try:
            if 'vivaldi_path' in config:
                self.vivaldi_path = config['vivaldi_path']
                self.browser_guidance_system.vivaldi_path = self.vivaldi_path
            return True
        except Exception as e:
            self.logger.error(f"Error updating configuration: {e}")
            return False
    
    async def _initialize_tutor(self) -> bool:
        """Initialize the enhanced security tutor"""
        try:
            # Initialize consciousness learning engine
            await self.consciousness_learning_engine.initialize(self.consciousness_bus)
            
            # Initialize adaptive content generator
            await self.adaptive_content_generator.initialize()
            
            # Initialize browser guidance system
            await self.browser_guidance_system.initialize()
            
            # Initialize PDF processor
            await self.pdf_processor.initialize()
            
            # Load learning content
            await self._load_learning_content()
            
            # Start background tasks
            self.background_tasks = [
                asyncio.create_task(self._consciousness_monitoring_loop()),
                asyncio.create_task(self._session_management_loop()),
                asyncio.create_task(self._browser_monitoring_loop())
            ]
            
            await self.set_component_state(ComponentState.HEALTHY)
            logger.info("Consciousness-Aware Security Tutor v2 initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Security Tutor v2: {e}")
            await self.set_component_state(ComponentState.FAILED)
            return False
    
    async def _shutdown_tutor(self) -> bool:
        """Shutdown the security tutor"""
        try:
            # Cancel background tasks
            for task in self.background_tasks:
                task.cancel()
            
            # Close all browser sessions
            for session in self.browser_sessions.values():
                await self.browser_guidance_system.close_browser_session(session.session_id)
            
            # Save session data
            await self._save_session_data()
            
            logger.info("Security Tutor v2 shutdown complete")
            return True
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            return False
    
    # Public API Methods
    
    async def start_learning_session(self, 
                                   user_id: str,
                                   platform: LearningPlatform,
                                   content_id: str,
                                   consciousness_state: Optional[ConsciousnessState] = None) -> Dict[str, Any]:
        """Start a consciousness-aware learning session"""
        
        # Get current consciousness state if not provided
        if consciousness_state is None:
            consciousness_state = await self._get_current_consciousness_state()
        
        # Determine learning mode based on consciousness
        learning_mode = self._determine_learning_mode(consciousness_state.consciousness_level)
        
        # Assess cognitive state
        cognitive_state = await self._assess_cognitive_state(consciousness_state)
        
        # Create learning session
        session_id = str(uuid.uuid4())
        session = ConsciousnessLearningSession(
            session_id=session_id,
            user_id=user_id,
            platform=platform,
            content_id=content_id,
            start_time=datetime.now(),
            consciousness_level=consciousness_state.consciousness_level,
            learning_mode=learning_mode,
            cognitive_state=cognitive_state
        )
        
        # Initialize consciousness trajectory
        session.consciousness_trajectory.append(
            (datetime.now(), consciousness_state.consciousness_level)
        )
        
        self.active_sessions[session_id] = session
        
        # Platform-specific initialization
        platform_data = await self._initialize_platform_session(session, platform)
        
        # Generate consciousness-optimized content
        content = await self.adaptive_content_generator.generate_consciousness_aware_content(
            session, consciousness_state
        )
        
        # Start consciousness monitoring for this session
        asyncio.create_task(self._monitor_session_consciousness(session_id))
        
        self.learning_analytics['active_sessions'] += 1
        self.learning_analytics['platform_interactions'][platform.value] += 1
        
        return {
            'session_id': session_id,
            'learning_mode': learning_mode.value,
            'cognitive_state': cognitive_state.value,
            'consciousness_level': consciousness_state.consciousness_level,
            'content': content,
            'platform_data': platform_data,
            'estimated_duration': content.get('estimated_duration', 30)
        }
    
    async def process_pdf_assignment(self, 
                                   user_id: str,
                                   pdf_path: str,
                                   assignment_type: str = "general") -> Dict[str, Any]:
        """Process a PDF assignment (syllabus, homework, etc.)"""
        
        try:
            # Extract text from PDF
            pdf_content = await self.pdf_processor.extract_pdf_content(pdf_path)
            
            # Analyze assignment content
            analysis = await self.pdf_processor.analyze_assignment(pdf_content, assignment_type)
            
            # Create learning session for assignment
            session_result = await self.start_learning_session(
                user_id=user_id,
                platform=LearningPlatform.SCHOOL_ASSIGNMENT,
                content_id=f"pdf_assignment_{uuid.uuid4()}"
            )
            
            # Generate consciousness-aware guidance
            guidance = await self.adaptive_content_generator.generate_assignment_guidance(
                analysis, session_result['consciousness_level']
            )
            
            return {
                'session_id': session_result['session_id'],
                'pdf_analysis': analysis,
                'guidance': guidance,
                'learning_objectives': analysis.get('learning_objectives', []),
                'estimated_completion_time': analysis.get('estimated_time', 60),
                'difficulty_assessment': analysis.get('difficulty', 'intermediate')
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF assignment: {e}")
            return {'error': f"Failed to process PDF: {str(e)}"}
    
    async def start_vivaldi_guided_session(self, 
                                         user_id: str,
                                         target_url: str,
                                         learning_objective: str) -> Dict[str, Any]:
        """Start a Vivaldi browser guided learning session"""
        
        try:
            # Start learning session
            session_result = await self.start_learning_session(
                user_id=user_id,
                platform=LearningPlatform.VIVALDI_GUIDED,
                content_id=f"browser_session_{uuid.uuid4()}"
            )
            
            session_id = session_result['session_id']
            session = self.active_sessions[session_id]
            
            # Launch Vivaldi browser session
            browser_session = await self.browser_guidance_system.launch_guided_session(
                user_id=user_id,
                target_url=target_url,
                learning_objective=learning_objective,
                consciousness_level=session.consciousness_level
            )
            
            # Link browser session to learning session
            session.browser_session_id = browser_session['session_id']
            session.current_url = target_url
            
            self.browser_sessions[browser_session['session_id']] = VivaldiBrowserSession(
                session_id=browser_session['session_id'],
                user_id=user_id,
                browser_process=browser_session['process'],
                current_url=target_url,
                guidance_active=True
            )
            
            return {
                'session_id': session_id,
                'browser_session_id': browser_session['session_id'],
                'guidance_url': target_url,
                'learning_objective': learning_objective,
                'consciousness_level': session.consciousness_level,
                'initial_guidance': browser_session.get('initial_guidance', [])
            }
            
        except Exception as e:
            logger.error(f"Error starting Vivaldi guided session: {e}")
            return {'error': f"Failed to start browser session: {str(e)}"}
    
    async def get_platform_guidance(self, 
                                  session_id: str,
                                  current_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get consciousness-aware guidance for current platform context"""
        
        if session_id not in self.active_sessions:
            return {'error': 'Session not found'}
        
        session = self.active_sessions[session_id]
        platform = session.platform
        
        # Get platform-specific handler
        integration = self.platform_integrations[platform]
        
        # Generate consciousness-aware guidance
        guidance = await self._generate_platform_guidance(session, current_context)
        
        # Update session with current context
        session.performance_metrics['guidance_requests'] = (
            session.performance_metrics.get('guidance_requests', 0) + 1
        )
        
        return {
            'guidance': guidance,
            'consciousness_level': session.consciousness_level,
            'learning_mode': session.learning_mode.value,
            'cognitive_state': session.cognitive_state.value,
            'platform_specific': await self._get_platform_specific_guidance(session, current_context)
        }
    
    async def track_learning_progress(self, 
                                    session_id: str,
                                    progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track learning progress and adapt based on consciousness"""
        
        if session_id not in self.active_sessions:
            return {'error': 'Session not found'}
        
        session = self.active_sessions[session_id]
        
        # Update session metrics
        session.performance_metrics.update(progress_data)
        
        # Analyze progress and consciousness correlation
        correlation_analysis = await self._analyze_progress_consciousness_correlation(session, progress_data)
        
        # Generate adaptive recommendations
        recommendations = await self._generate_adaptive_recommendations(session, correlation_analysis)
        
        # Update learning analytics
        # recommendations is a List[str], not a dict
        self.learning_analytics['consciousness_adaptations'] += len(recommendations)
        
        return {
            'progress_recorded': True,
            'correlation_analysis': correlation_analysis,
            'recommendations': recommendations,
            'session_metrics': session.performance_metrics
        }
    
    async def complete_learning_session(self, 
                                      session_id: str,
                                      completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete a learning session with consciousness analysis"""
        
        if session_id not in self.active_sessions:
            return {'error': 'Session not found'}
        
        session = self.active_sessions[session_id]
        
        # Calculate session duration
        duration = datetime.now() - session.start_time
        
        # Analyze consciousness trajectory during session
        consciousness_analysis = await self._analyze_consciousness_trajectory(session)
        
        # Generate session summary
        session_summary = await self._generate_session_summary(session, completion_data, consciousness_analysis)
        
        # Close browser session if active
        if session.browser_session_id and session.browser_session_id in self.browser_sessions:
            await self.browser_guidance_system.close_browser_session(session.browser_session_id)
            del self.browser_sessions[session.browser_session_id]
        
        # Update analytics
        self.learning_analytics['active_sessions'] -= 1
        self.learning_analytics['total_sessions_completed'] += 1
        
        # Clean up session
        del self.active_sessions[session_id]
        
        # Publish learning progress event
        progress_event = create_learning_progress_event(
            source_component="security_tutor_v2",
            progress_data={
                'user_id': session.user_id,
                'platform': session.platform.value,
                'duration_minutes': duration.total_seconds() / 60,
                'consciousness_analysis': consciousness_analysis,
                'completion_data': completion_data
            }
        )
        
        await self.consciousness_bus.publish(progress_event)
        
        return session_summary
    
    # Platform-specific handlers
    
    async def handle_freecodecamp_challenge(self, session_id: str, challenge_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle FreeCodeCamp challenge completion"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {'error': 'Session not found'}
        
        # Analyze challenge difficulty vs consciousness level
        difficulty_match = await self._analyze_difficulty_consciousness_match(
            challenge_data.get('difficulty', 'intermediate'),
            session.consciousness_level
        )
        
        # Generate consciousness-aware hints if needed
        hints = []
        if difficulty_match['needs_support']:
            hints = await self.adaptive_content_generator.generate_consciousness_aware_hints(
                challenge_data, session.consciousness_level
            )
        
        return {
            'difficulty_analysis': difficulty_match,
            'consciousness_hints': hints,
            'recommended_approach': difficulty_match.get('approach', 'standard')
        }
    
    async def guide_htb_machine(self, session_id: str, machine_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide consciousness-aware guidance for HackTheBox machines"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {'error': 'Session not found'}
        
        # Generate reconnaissance guidance based on consciousness level
        recon_guidance = await self._generate_htb_recon_guidance(machine_data, session.consciousness_level)
        
        # Provide enumeration steps
        enumeration_steps = await self._generate_enumeration_steps(machine_data, session.learning_mode)
        
        # Generate consciousness-optimized methodology
        methodology = await self._generate_consciousness_methodology(session, machine_data)
        
        return {
            'reconnaissance': recon_guidance,
            'enumeration': enumeration_steps,
            'methodology': methodology,
            'consciousness_level': session.consciousness_level,
            'learning_mode': session.learning_mode.value
        }
    
    async def guide_thm_room(self, session_id: str, room_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide consciousness-aware guidance for TryHackMe rooms"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {'error': 'Session not found'}
        
        # Generate task-specific guidance
        task_guidance = await self._generate_thm_task_guidance(room_data, session)
        
        # Provide learning path recommendations
        learning_path = await self._generate_thm_learning_path(room_data, session.consciousness_level)
        
        return {
            'task_guidance': task_guidance,
            'learning_path': learning_path,
            'consciousness_optimized': True
        }
    
    # Background monitoring loops
    
    async def _consciousness_monitoring_loop(self):
        """Monitor consciousness changes across all active sessions"""
        while self.is_running:
            try:
                for session_id, session in self.active_sessions.items():
                    # Get current consciousness state
                    current_state = await self._get_current_consciousness_state()
                    
                    if current_state and abs(current_state.consciousness_level - session.consciousness_level) > 0.1:
                        # Significant consciousness change detected
                        await self._handle_consciousness_change(session, current_state)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in consciousness monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _session_management_loop(self):
        """Manage active learning sessions"""
        while self.is_running:
            try:
                current_time = datetime.now()
                expired_sessions = []
                
                for session_id, session in self.active_sessions.items():
                    # Check for expired sessions (4 hours max)
                    if (current_time - session.start_time).total_seconds() > 14400:
                        expired_sessions.append(session_id)
                
                # Clean up expired sessions
                for session_id in expired_sessions:
                    await self._cleanup_expired_session(session_id)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in session management loop: {e}")
                await asyncio.sleep(300)
    
    async def _browser_monitoring_loop(self):
        """Monitor Vivaldi browser sessions"""
        while self.is_running:
            try:
                for session_id, browser_session in list(self.browser_sessions.items()):
                    if browser_session.guidance_active:
                        # Take screenshot for analysis
                        screenshot_path = await self.browser_guidance_system.take_screenshot(session_id)
                        
                        if screenshot_path:
                            browser_session.screenshot_path = screenshot_path
                            
                            # Analyze screenshot for guidance opportunities
                            analysis = await self.browser_guidance_system.analyze_screenshot(screenshot_path)
                            
                            if analysis.get('guidance_needed'):
                                await self._provide_browser_guidance(session_id, analysis)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in browser monitoring loop: {e}")
                await asyncio.sleep(30)
    
    # Helper methods
    
    def _determine_learning_mode(self, consciousness_level: float) -> LearningMode:
        """Determine optimal learning mode based on consciousness level"""
        if consciousness_level >= 0.8:
            return LearningMode.BREAKTHROUGH
        elif consciousness_level >= 0.6:
            return LearningMode.INTENSIVE
        elif consciousness_level >= 0.3:
            return LearningMode.FOCUSED
        else:
            return LearningMode.EXPLORATION
    
    async def _assess_cognitive_state(self, consciousness_state: ConsciousnessState) -> CognitiveState:
        """Assess cognitive state from consciousness data"""
        consciousness_level = consciousness_state.consciousness_level
        
        # Simple cognitive state assessment
        if consciousness_level >= 0.9:
            return CognitiveState.OVERLOADED
        elif consciousness_level >= 0.7:
            return CognitiveState.OPTIMAL
        elif consciousness_level >= 0.3:
            return CognitiveState.UNDERUTILIZED
        else:
            return CognitiveState.FATIGUED
    
    async def _get_current_consciousness_state(self) -> Optional[ConsciousnessState]:
        """Get current consciousness state from state manager"""
        if self.state_manager:
            try:
                return await self.state_manager.get_consciousness_state()
            except Exception as e:
                logger.error(f"Error getting consciousness state: {e}")
        
        # Return default state if unavailable
        return ConsciousnessState(consciousness_level=0.5)
    
    async def _load_learning_content(self):
        """Load learning content for all platforms"""
        # This would load content from database or files
        # For now, we'll create some sample content
        
        sample_content = LearningContent(
            content_id="sample_web_security",
            title="Web Security Fundamentals",
            platform=LearningPlatform.FREECODECAMP,
            content_type=ContentType.THEORY,
            difficulty_level="intermediate",
            consciousness_optimized=True,
            content_data={"description": "Basic web security concepts"}
        )
        
        self.learning_content[sample_content.content_id] = sample_content

    # Missing helper methods implementation
    async def _handle_consciousness_evolution(self, event: ConsciousnessEvent):
        """Handle consciousness evolution events"""
        logger.info(f"Processing consciousness evolution event: {event.event_type}")
        
        # Update all active sessions with new consciousness state
        for session_id, session in self.active_sessions.items():
            if self.state_manager:
                consciousness_state = await self.state_manager.get_consciousness_state()
            else:
                consciousness_state = None
            if consciousness_state:
                session.consciousness_level = consciousness_state.consciousness_level
                await self._adapt_session_to_consciousness(session_id, consciousness_state)

    async def _handle_consciousness_emergence(self, event: ConsciousnessEvent):
        """Handle consciousness emergence events"""
        logger.info(f"Processing consciousness emergence event: {event.event_type}")
        
        # Trigger breakthrough learning mode for active sessions
        for session_id, session in self.active_sessions.items():
            if session.learning_mode != LearningMode.BREAKTHROUGH:
                session.learning_mode = LearningMode.BREAKTHROUGH
                await self._update_session_content(session_id)

    async def _handle_learning_progress(self, event: ConsciousnessEvent):
        """Handle learning progress events"""
        logger.info(f"Processing learning progress event: {event.event_type}")
        
        # Analyze progress and adjust difficulty
        for session_id, session in self.active_sessions.items():
            await self._analyze_and_adjust_difficulty(session_id)

    async def _save_session_data(self):
        """Save session data periodically"""
        try:
            session_data = {
                'active_sessions': {
                    session_id: {
                        'platform': session.platform.value,
                        'learning_mode': session.learning_mode.value,
                        'start_time': session.start_time.isoformat(),
                        'consciousness_level': session.consciousness_level,
                        'progress_data': getattr(session, 'progress_data', {})
                    }
                    for session_id, session in self.active_sessions.items()
                },
                'learning_analytics': self.learning_analytics,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save to file or database
            # Use secure temp directory instead of hardcoded /tmp
            import tempfile
            temp_dir = tempfile.mkdtemp(prefix="syn_os_security_tutor_", suffix="_sessions")
            session_file = Path(temp_dir) / f"security_tutor_sessions_{datetime.now().strftime('%Y%m%d')}.json"
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save session data: {e}")

    async def _initialize_platform_session(self, session, platform: LearningPlatform) -> Dict[str, Any]:
        """Initialize platform-specific session data"""
        platform_data = {
            'platform': platform.value,
            'initialized_at': datetime.now().isoformat(),
            'configuration': {}
        }
        
        if platform == LearningPlatform.HACKTHEBOX:
            platform_data['configuration'] = {
                'api_endpoint': 'https://www.hackthebox.eu/api/v4',
                'machine_categories': ['easy', 'medium', 'hard', 'insane'],
                'preferred_os': ['linux', 'windows']
            }
        elif platform == LearningPlatform.TRYHACKME:
            platform_data['configuration'] = {
                'api_endpoint': 'https://tryhackme.com/api',
                'room_categories': ['beginner', 'intermediate', 'advanced'],
                'learning_paths': ['complete_beginner', 'offensive_pentesting', 'cyber_defense']
            }
        elif platform == LearningPlatform.VIVALDI_GUIDED:
            platform_data['configuration'] = {
                'browser_automation': True,
                'guidance_overlay': True,
                'real_time_hints': True
            }
        
        return platform_data

    async def _monitor_session_consciousness(self, session_id: str):
        """Monitor consciousness changes during a session"""
        while session_id in self.active_sessions:
            try:
                if self.state_manager:
                    consciousness_state = await self.state_manager.get_consciousness_state()
                else:
                    consciousness_state = None
                if consciousness_state:
                    session = self.active_sessions[session_id]
                    
                    # Check for significant consciousness changes
                    consciousness_change = abs(consciousness_state.consciousness_level - session.consciousness_level)
                    if consciousness_change > 0.2:  # Significant change threshold
                        await self._handle_consciousness_change(session, consciousness_state)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring session consciousness: {e}")
                break

    async def _generate_platform_guidance(self, session, current_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate platform-specific guidance"""
        guidance = {
            'suggestions': [],
            'next_steps': [],
            'resources': [],
            'difficulty_adjustment': None
        }
        
        if session.platform == LearningPlatform.HACKTHEBOX:
            guidance['suggestions'] = [
                "Start with nmap scan to identify open ports",
                "Enumerate services running on open ports",
                "Look for known vulnerabilities in identified services"
            ]
        elif session.platform == LearningPlatform.TRYHACKME:
            guidance['suggestions'] = [
                "Read the room description carefully",
                "Follow the guided questions step by step",
                "Use the provided hints when stuck"
            ]
        elif session.platform == LearningPlatform.FREECODECAMP:
            guidance['suggestions'] = [
                "Complete each lesson before moving forward",
                "Practice the concepts in the interactive editor",
                "Review the solution if you get stuck"
            ]
        
        return guidance

    async def _get_platform_specific_guidance(self, session, current_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed platform-specific guidance"""
        if session.platform == LearningPlatform.HACKTHEBOX:
            return await self._get_htb_specific_guidance(session, current_context)
        elif session.platform == LearningPlatform.TRYHACKME:
            return await self._get_thm_specific_guidance(session, current_context)
        else:
            return {'guidance': 'General learning guidance available'}

    async def _analyze_progress_consciousness_correlation(self, session, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze correlation between progress and consciousness"""
        correlation_analysis = {
            'correlation_strength': 0.0,
            'optimal_consciousness_range': (0.4, 0.8),
            'performance_indicators': [],
            'recommendations': []
        }
        
        # Analyze progress history
        progress_history = session.progress_data.get('history', [])
        if len(progress_history) > 5:
            consciousness_levels = [p[1] for p in progress_history[-10:]]
            progress_scores = [p[2] if len(p) > 2 else 0.5 for p in progress_history[-10:]]
            
            # Calculate correlation (simplified)
            if len(consciousness_levels) == len(progress_scores):
                correlation = np.corrcoef(consciousness_levels, progress_scores)[0, 1]
                correlation_analysis['correlation_strength'] = float(correlation) if not np.isnan(correlation) else 0.0
        
        return correlation_analysis

    async def _generate_adaptive_recommendations(self, session, correlation_analysis: Dict[str, Any]) -> List[str]:
        """Generate adaptive recommendations based on analysis"""
        recommendations = []
        
        correlation_strength = correlation_analysis.get('correlation_strength', 0.0)
        
        if correlation_strength > 0.5:
            recommendations.append("Strong positive correlation detected - maintain current approach")
        elif correlation_strength < -0.3:
            recommendations.append("Negative correlation detected - consider adjusting learning strategy")
        else:
            recommendations.append("Weak correlation - experiment with different approaches")
        
        # Add consciousness-specific recommendations
        if session.consciousness_level < 0.3:
            recommendations.extend([
                "Consider taking a break to improve consciousness state",
                "Try simpler exercises to build confidence",
                "Use more visual and interactive learning materials"
            ])
        elif session.consciousness_level > 0.8:
            recommendations.extend([
                "Challenge yourself with advanced topics",
                "Explore creative problem-solving approaches",
                "Consider mentoring others to reinforce learning"
            ])
        
        return recommendations

    async def _analyze_consciousness_trajectory(self, session) -> Dict[str, Any]:
        """Analyze consciousness trajectory during the session"""
        trajectory_analysis = {
            'trend': 'stable',
            'peak_consciousness': 0.0,
            'average_consciousness': 0.0,
            'consciousness_variance': 0.0,
            'optimal_periods': []
        }
        
        consciousness_history = [p[1] for p in session.progress_data.get('history', [])]
        
        if consciousness_history:
            trajectory_analysis['peak_consciousness'] = max(consciousness_history)
            trajectory_analysis['average_consciousness'] = sum(consciousness_history) / len(consciousness_history)
            trajectory_analysis['consciousness_variance'] = np.var(consciousness_history)
            
            # Determine trend
            if len(consciousness_history) > 3:
                recent_avg = sum(consciousness_history[-3:]) / 3
                early_avg = sum(consciousness_history[:3]) / 3
                
                if recent_avg > early_avg + 0.1:
                    trajectory_analysis['trend'] = 'improving'
                elif recent_avg < early_avg - 0.1:
                    trajectory_analysis['trend'] = 'declining'
        
        return trajectory_analysis

    async def _generate_session_summary(self, session, completion_data: Dict[str, Any],
                                      consciousness_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive session summary"""
        summary = {
            'session_id': session.session_id,
            'platform': session.platform.value,
            'duration_minutes': (datetime.now() - session.start_time).total_seconds() / 60,
            'learning_mode': session.learning_mode.value,
            'consciousness_summary': consciousness_analysis,
            'achievements': completion_data.get('achievements', []),
            'challenges_completed': completion_data.get('challenges_completed', 0),
            'skills_developed': completion_data.get('skills_developed', []),
            'recommendations': completion_data.get('recommendations', []),
            'next_session_suggestions': []
        }
        
        # Generate next session suggestions
        if consciousness_analysis.get('trend') == 'improving':
            summary['next_session_suggestions'].append("Continue with current difficulty level")
        elif consciousness_analysis.get('trend') == 'declining':
            summary['next_session_suggestions'].append("Consider easier content or take a break")
        
        return summary

    async def _analyze_difficulty_consciousness_match(self, session_id: str, content_difficulty: float) -> Dict[str, Any]:
        """Analyze if content difficulty matches consciousness level"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {'match_score': 0.0, 'recommendation': 'session_not_found'}
        
        consciousness_level = session.consciousness_level
        
        # Calculate match score (1.0 = perfect match, 0.0 = poor match)
        difficulty_gap = abs(content_difficulty - consciousness_level)
        match_score = max(0.0, 1.0 - (difficulty_gap * 2))
        
        analysis = {
            'match_score': match_score,
            'consciousness_level': consciousness_level,
            'content_difficulty': content_difficulty,
            'difficulty_gap': difficulty_gap,
            'recommendation': 'maintain'
        }
        
        if difficulty_gap > 0.3:
            if content_difficulty > consciousness_level:
                analysis['recommendation'] = 'reduce_difficulty'
            else:
                analysis['recommendation'] = 'increase_difficulty'
        
        return analysis

    async def _generate_htb_recon_guidance(self, machine_data: Dict[str, Any], consciousness_level: float) -> List[str]:
        """Generate HackTheBox reconnaissance guidance"""
        guidance = []
        
        if consciousness_level < 0.4:
            guidance.extend([
                "Start with basic nmap scan: nmap -sV -sC <target_ip>",
                "Check for common ports: 21, 22, 23, 25, 53, 80, 110, 443, 993, 995",
                "Look up any unfamiliar services online"
            ])
        else:
            guidance.extend([
                "Perform comprehensive port scan: nmap -p- -sV -sC <target_ip>",
                "Use aggressive scanning if needed: nmap -A <target_ip>",
                "Consider UDP scanning: nmap -sU --top-ports 1000 <target_ip>"
            ])
        
        return guidance

    async def _generate_enumeration_steps(self, machine_data: Dict[str, Any], learning_mode: LearningMode) -> List[str]:
        """Generate enumeration steps based on learning mode"""
        steps = []
        
        if learning_mode == LearningMode.EXPLORATION:
            steps.extend([
                "Explore each discovered service manually",
                "Take notes of interesting findings",
                "Research vulnerabilities for each service version"
            ])
        elif learning_mode == LearningMode.INTENSIVE:
            steps.extend([
                "Run automated enumeration tools",
                "Cross-reference findings with exploit databases",
                "Prioritize attack vectors based on likelihood"
            ])
        
        return steps

    async def _generate_consciousness_methodology(self, session, machine_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate consciousness-aware methodology"""
        methodology = {
            'approach': 'systematic',
            'phases': [],
            'consciousness_adaptations': []
        }
        
        if session.consciousness_level < 0.4:
            methodology['approach'] = 'guided'
            methodology['phases'] = [
                'Basic reconnaissance',
                'Service enumeration',
                'Vulnerability research',
                'Exploitation attempt'
            ]
        else:
            methodology['approach'] = 'adaptive'
            methodology['phases'] = [
                'Comprehensive reconnaissance',
                'Multi-vector enumeration',
                'Advanced exploitation',
                'Post-exploitation'
            ]
        
        return methodology

    async def _generate_thm_task_guidance(self, room_data: Dict[str, Any], session) -> List[str]:
        """Generate TryHackMe task-specific guidance"""
        guidance = []
        
        if session.consciousness_level < 0.5:
            guidance.extend([
                "Read each question carefully",
                "Use the provided hints liberally",
                "Don't skip the learning material"
            ])
        else:
            guidance.extend([
                "Try to solve without hints first",
                "Explore beyond the minimum requirements",
                "Document your methodology"
            ])
        
        return guidance

    async def _generate_thm_learning_path(self, room_data: Dict[str, Any], consciousness_level: float) -> Dict[str, Any]:
        """Generate TryHackMe learning path"""
        learning_path = {
            'current_room': room_data.get('name', 'Unknown'),
            'suggested_next': [],
            'skill_prerequisites': [],
            'estimated_duration': '1-2 hours'
        }
        
        if consciousness_level < 0.4:
            learning_path['suggested_next'] = ['Basic Pentesting', 'Web Fundamentals']
        else:
            learning_path['suggested_next'] = ['Advanced Exploitation', 'Red Team Fundamentals']
        
        return learning_path

    async def _handle_consciousness_change(self, session, current_state: ConsciousnessState):
        """Handle significant consciousness state changes"""
        logger.info(f"Handling consciousness change for session {session.session_id}")
        
        # Update session consciousness level
        session.consciousness_level = current_state.consciousness_level
        
        # Adjust learning mode if necessary
        new_mode = self._determine_learning_mode(current_state.consciousness_level)
        if new_mode != session.learning_mode:
            session.learning_mode = new_mode
            await self._update_session_content(session.session_id)

    async def _cleanup_expired_session(self, session_id: str):
        """Clean up expired session"""
        logger.info(f"Cleaning up expired session: {session_id}")
        
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            
            # Save final session data
            await self._save_final_session_data(session)
            
            # Close browser session if active
            if hasattr(session, 'browser_session') and getattr(session, 'browser_session', None):
                await self.browser_guidance_system.close_session()
            
            # Remove from active sessions
            del self.active_sessions[session_id]

    async def _provide_browser_guidance(self, session_id: str, analysis: Dict[str, Any]):
        """Provide browser-based guidance"""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        try:
            # Get current browser context
            browser_context = await self.browser_guidance_system.analyze_current_page()
            
            # Generate contextual guidance
            guidance = await self.browser_guidance_system.provide_contextual_guidance(
                browser_context, session.consciousness_level
            )
            
            # Update session with guidance
            if hasattr(session, 'progress_data'):
                session.progress_data['browser_guidance'] = guidance
            
        except Exception as e:
            logger.error(f"Failed to provide browser guidance: {e}")

    async def _save_final_session_data(self, session):
        """Save final session data before cleanup"""
        try:
            final_data = {
                'session_id': session.session_id,
                'platform': session.platform.value,
                'total_duration': (datetime.now() - session.start_time).total_seconds(),
                'final_consciousness_level': session.consciousness_level,
                'learning_mode': session.learning_mode.value,
                'progress_data': session.progress_data,
                'completed_at': datetime.now().isoformat()
            }
            
            # Save to persistent storage using secure temp directory
            import tempfile
            temp_dir = tempfile.mkdtemp(prefix="syn_os_sessions_", suffix="_storage")
            session_file = Path(temp_dir) / f"completed_session_{session.session_id}.json"
            with open(session_file, 'w') as f:
                json.dump(final_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save final session data: {e}")

    async def _update_session_content(self, session_id: str):
        """Update session content based on current state"""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        # Generate new content based on updated consciousness/learning mode
        new_content = await self.adaptive_content_generator.generate_content(
            topic="security",
            consciousness_level=session.consciousness_level,
            learning_mode=session.learning_mode.value,
            platform=session.platform.value
        )
        
        if hasattr(session, 'progress_data'):
            session.progress_data['current_content'] = new_content

    async def _adapt_session_to_consciousness(self, session_id: str, consciousness_state: ConsciousnessState):
        """Adapt session to new consciousness state"""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        # Update session parameters
        session.consciousness_level = consciousness_state.consciousness_level
        
        # Determine if learning mode should change
        optimal_mode = self._determine_learning_mode(consciousness_state.consciousness_level)
        if optimal_mode != session.learning_mode:
            session.learning_mode = optimal_mode
            await self._update_session_content(session_id)

    async def _analyze_and_adjust_difficulty(self, session_id: str):
        """Analyze progress and adjust difficulty accordingly"""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        # Analyze recent progress
        progress_data = getattr(session, 'progress_data', {})
        progress_history = progress_data.get('history', [])
        if len(progress_history) < 3:
            return  # Not enough data
        
        # Calculate recent performance
        recent_scores = [p[2] if len(p) > 2 else 0.5 for p in progress_history[-5:]]
        avg_performance = sum(recent_scores) / len(recent_scores)
        
        # Adjust difficulty based on performance and consciousness
        if avg_performance > 0.8 and session.consciousness_level > 0.6:
            # Increase difficulty
            if hasattr(session, 'progress_data'):
                session.progress_data['difficulty_adjustment'] = 'increase'
        elif avg_performance < 0.4 or session.consciousness_level < 0.3:
            # Decrease difficulty
            if hasattr(session, 'progress_data'):
                session.progress_data['difficulty_adjustment'] = 'decrease'
        else:
            # Maintain current difficulty
            if hasattr(session, 'progress_data'):
                session.progress_data['difficulty_adjustment'] = 'maintain'

    async def _get_htb_specific_guidance(self, session, current_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get HackTheBox-specific guidance"""
        return {
            'reconnaissance': await self._generate_htb_recon_guidance({}, session.consciousness_level),
            'enumeration': await self._generate_enumeration_steps({}, session.learning_mode),
            'methodology': await self._generate_consciousness_methodology(session, {})
        }

    async def _get_thm_specific_guidance(self, session, current_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get TryHackMe-specific guidance"""
        return {
            'task_guidance': await self._generate_thm_task_guidance({}, session),
            'learning_path': await self._generate_thm_learning_path({}, session.consciousness_level)
        }