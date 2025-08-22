#!/usr/bin/env python3
"""
User Context Persistence and Management

This module provides comprehensive user context management for the consciousness
system, including learning patterns, preferences, behavioral analysis, and
personalized adaptation mechanisms.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import aiosqlite
from pathlib import Path

from ..components.event_bus import EventBus


class ContextType(Enum):
    LEARNING = "learning"
    BEHAVIORAL = "behavioral"
    PREFERENCE = "preference"
    PERFORMANCE = "performance"
    ATTENTION = "attention"
    COGNITIVE = "cognitive"


@dataclass
class UserContext:
    """User context data structure"""
    user_id: str
    context_type: ContextType
    data: Dict[str, Any]
    timestamp: datetime
    confidence: float
    source: str
    metadata: Dict[str, Any]


@dataclass
class UserProfile:
    """Comprehensive user profile"""
    user_id: str
    created_at: datetime
    last_updated: datetime
    learning_patterns: Dict[str, Any]
    behavioral_patterns: Dict[str, Any]
    preferences: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    attention_patterns: Dict[str, Any]
    cognitive_profile: Dict[str, Any]
    adaptation_history: List[Dict[str, Any]]


class UserContextManager:
    """Manages user context persistence and analysis"""
    
    def __init__(self, db_path: str = "data/user_contexts.db", event_bus: Optional[EventBus] = None):
        self.db_path = Path(db_path)
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        
        # Ensure data directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Context analysis parameters
        self.context_retention_days = 90
        self.analysis_window_hours = 24
        self.confidence_threshold = 0.7
        
        # In-memory cache for active user contexts
        self.active_contexts: Dict[str, UserProfile] = {}
        self.context_buffer: List[UserContext] = []
        
        # Analysis patterns
        self.learning_patterns = {
            'optimal_session_length': self._analyze_session_length,
            'attention_decay_rate': self._analyze_attention_decay,
            'learning_velocity': self._analyze_learning_velocity,
            'mistake_patterns': self._analyze_mistake_patterns,
            'engagement_triggers': self._analyze_engagement_triggers
        }
        
        self.behavioral_patterns = {
            'interaction_frequency': self._analyze_interaction_frequency,
            'navigation_patterns': self._analyze_navigation_patterns,
            'help_seeking_behavior': self._analyze_help_seeking,
            'persistence_level': self._analyze_persistence,
            'social_learning_preference': self._analyze_social_learning
        }
    
    async def initialize(self):
        """Initialize the user context manager"""
        await self._create_database_schema()
        await self._load_active_contexts()
        
        # Start background tasks
        asyncio.create_task(self._context_analyzer())
        asyncio.create_task(self._context_persister())
        asyncio.create_task(self._context_cleaner())
        
        self.logger.info("User Context Manager initialized")
    
    async def _create_database_schema(self):
        """Create database schema for user contexts"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    created_at TIMESTAMP,
                    last_updated TIMESTAMP,
                    learning_patterns TEXT,
                    behavioral_patterns TEXT,
                    preferences TEXT,
                    performance_metrics TEXT,
                    attention_patterns TEXT,
                    cognitive_profile TEXT,
                    adaptation_history TEXT
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_contexts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    context_type TEXT,
                    data TEXT,
                    timestamp TIMESTAMP,
                    confidence REAL,
                    source TEXT,
                    metadata TEXT,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                )
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_contexts_user_id 
                ON user_contexts (user_id)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_contexts_timestamp 
                ON user_contexts (timestamp)
            """)
            
            await db.commit()
    
    async def _load_active_contexts(self):
        """Load recently active user contexts into memory"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=self.analysis_window_hours)
            
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT DISTINCT user_id FROM user_contexts 
                    WHERE timestamp > ? 
                    ORDER BY timestamp DESC
                """, (cutoff_time,)) as cursor:
                    
                    async for row in cursor:
                        user_id = row[0]
                        profile = await self._load_user_profile(user_id)
                        if profile:
                            self.active_contexts[user_id] = profile
            
            self.logger.info(f"Loaded {len(self.active_contexts)} active user contexts")
            
        except Exception as e:
            self.logger.error(f"Error loading active contexts: {e}")
    
    async def _load_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Load a complete user profile from database"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT * FROM user_profiles WHERE user_id = ?
                """, (user_id,)) as cursor:
                    
                    row = await cursor.fetchone()
                    if row:
                        return UserProfile(
                            user_id=row[0],
                            created_at=datetime.fromisoformat(row[1]),
                            last_updated=datetime.fromisoformat(row[2]),
                            learning_patterns=json.loads(row[3]) if row[3] else {},
                            behavioral_patterns=json.loads(row[4]) if row[4] else {},
                            preferences=json.loads(row[5]) if row[5] else {},
                            performance_metrics=json.loads(row[6]) if row[6] else {},
                            attention_patterns=json.loads(row[7]) if row[7] else {},
                            cognitive_profile=json.loads(row[8]) if row[8] else {},
                            adaptation_history=json.loads(row[9]) if row[9] else []
                        )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error loading user profile {user_id}: {e}")
            return None
    
    async def record_context(self, user_id: str, context_type: ContextType, 
                           data: Dict[str, Any], confidence: float = 1.0,
                           source: str = "system", metadata: Dict[str, Any] = None):
        """Record a new user context"""
        context = UserContext(
            user_id=user_id,
            context_type=context_type,
            data=data,
            timestamp=datetime.utcnow(),
            confidence=confidence,
            source=source,
            metadata=metadata or {}
        )
        
        # Add to buffer for batch processing
        self.context_buffer.append(context)
        
        # Update active context if user is active
        if user_id in self.active_contexts:
            await self._update_active_context(user_id, context)
        
        # Publish event if event bus is available
        if self.event_bus:
            await self.event_bus.publish_event({
                'type': 'user_context_recorded',
                'user_id': user_id,
                'context_type': context_type.value,
                'timestamp': context.timestamp.isoformat(),
                'source': source
            })
    
    async def _update_active_context(self, user_id: str, context: UserContext):
        """Update active user context in memory"""
        try:
            profile = self.active_contexts.get(user_id)
            if not profile:
                # Create new profile
                profile = UserProfile(
                    user_id=user_id,
                    created_at=datetime.utcnow(),
                    last_updated=datetime.utcnow(),
                    learning_patterns={},
                    behavioral_patterns={},
                    preferences={},
                    performance_metrics={},
                    attention_patterns={},
                    cognitive_profile={},
                    adaptation_history=[]
                )
                self.active_contexts[user_id] = profile
            
            # Update relevant pattern based on context type
            if context.context_type == ContextType.LEARNING:
                profile.learning_patterns.update(context.data)
            elif context.context_type == ContextType.BEHAVIORAL:
                profile.behavioral_patterns.update(context.data)
            elif context.context_type == ContextType.PREFERENCE:
                profile.preferences.update(context.data)
            elif context.context_type == ContextType.PERFORMANCE:
                profile.performance_metrics.update(context.data)
            elif context.context_type == ContextType.ATTENTION:
                profile.attention_patterns.update(context.data)
            elif context.context_type == ContextType.COGNITIVE:
                profile.cognitive_profile.update(context.data)
            
            profile.last_updated = datetime.utcnow()
            
        except Exception as e:
            self.logger.error(f"Error updating active context for {user_id}: {e}")
    
    async def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive insights for a user"""
        try:
            profile = self.active_contexts.get(user_id)
            if not profile:
                profile = await self._load_user_profile(user_id)
                if profile:
                    self.active_contexts[user_id] = profile
            
            if not profile:
                return {}
            
            # Generate insights from patterns
            insights = {
                'learning_insights': await self._generate_learning_insights(profile),
                'behavioral_insights': await self._generate_behavioral_insights(profile),
                'performance_insights': await self._generate_performance_insights(profile),
                'attention_insights': await self._generate_attention_insights(profile),
                'cognitive_insights': await self._generate_cognitive_insights(profile),
                'recommendations': await self._generate_recommendations(profile),
                'adaptation_suggestions': await self._generate_adaptation_suggestions(profile)
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating insights for {user_id}: {e}")
            return {}
    
    async def _generate_learning_insights(self, profile: UserProfile) -> Dict[str, Any]:
        """Generate learning-specific insights"""
        patterns = profile.learning_patterns
        
        insights = {
            'optimal_session_length': patterns.get('optimal_session_length', 15),
            'learning_velocity': patterns.get('learning_velocity', 'moderate'),
            'retention_rate': patterns.get('retention_rate', 0.75),
            'preferred_difficulty_progression': patterns.get('difficulty_progression', 'gradual'),
            'mistake_recovery_time': patterns.get('mistake_recovery_time', 30),
            'engagement_peak_times': patterns.get('engagement_peaks', []),
            'learning_style_effectiveness': patterns.get('style_effectiveness', {})
        }
        
        return insights
    
    async def _generate_behavioral_insights(self, profile: UserProfile) -> Dict[str, Any]:
        """Generate behavioral insights"""
        patterns = profile.behavioral_patterns
        
        insights = {
            'interaction_frequency': patterns.get('interaction_frequency', 'moderate'),
            'help_seeking_tendency': patterns.get('help_seeking', 'balanced'),
            'persistence_level': patterns.get('persistence', 'high'),
            'exploration_vs_exploitation': patterns.get('exploration_ratio', 0.3),
            'social_learning_preference': patterns.get('social_preference', 'individual'),
            'feedback_responsiveness': patterns.get('feedback_response', 'positive')
        }
        
        return insights
    
    async def _generate_performance_insights(self, profile: UserProfile) -> Dict[str, Any]:
        """Generate performance insights"""
        metrics = profile.performance_metrics
        
        insights = {
            'overall_performance_trend': metrics.get('trend', 'improving'),
            'strength_areas': metrics.get('strengths', []),
            'improvement_areas': metrics.get('weaknesses', []),
            'consistency_score': metrics.get('consistency', 0.8),
            'peak_performance_conditions': metrics.get('peak_conditions', {}),
            'performance_variability': metrics.get('variability', 'low')
        }
        
        return insights
    
    async def _generate_attention_insights(self, profile: UserProfile) -> Dict[str, Any]:
        """Generate attention pattern insights"""
        patterns = profile.attention_patterns
        
        insights = {
            'attention_span': patterns.get('span', 20),
            'focus_stability': patterns.get('stability', 'stable'),
            'distraction_triggers': patterns.get('distractions', []),
            'attention_recovery_rate': patterns.get('recovery_rate', 'fast'),
            'optimal_break_frequency': patterns.get('break_frequency', 15),
            'attention_enhancement_factors': patterns.get('enhancement_factors', [])
        }
        
        return insights
    
    async def _generate_cognitive_insights(self, profile: UserProfile) -> Dict[str, Any]:
        """Generate cognitive profile insights"""
        cognitive = profile.cognitive_profile
        
        insights = {
            'cognitive_load_tolerance': cognitive.get('load_tolerance', 'medium'),
            'processing_speed': cognitive.get('processing_speed', 'average'),
            'working_memory_capacity': cognitive.get('working_memory', 'normal'),
            'cognitive_flexibility': cognitive.get('flexibility', 'adaptive'),
            'metacognitive_awareness': cognitive.get('metacognition', 'developing'),
            'cognitive_style': cognitive.get('style', 'balanced')
        }
        
        return insights
    
    async def _generate_recommendations(self, profile: UserProfile) -> List[Dict[str, Any]]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Learning recommendations
        if profile.learning_patterns.get('optimal_session_length', 15) < 10:
            recommendations.append({
                'type': 'session_length',
                'recommendation': 'Consider shorter, more frequent sessions',
                'reason': 'Your attention span suggests micro-learning would be more effective',
                'priority': 'high'
            })
        
        # Performance recommendations
        if profile.performance_metrics.get('consistency', 0.8) < 0.6:
            recommendations.append({
                'type': 'consistency',
                'recommendation': 'Focus on establishing regular learning routines',
                'reason': 'Consistent practice will improve your performance stability',
                'priority': 'medium'
            })
        
        # Attention recommendations
        if profile.attention_patterns.get('stability', 'stable') == 'unstable':
            recommendations.append({
                'type': 'attention',
                'recommendation': 'Implement attention training exercises',
                'reason': 'Your attention patterns show room for improvement',
                'priority': 'high'
            })
        
        return recommendations
    
    async def _generate_adaptation_suggestions(self, profile: UserProfile) -> List[Dict[str, Any]]:
        """Generate system adaptation suggestions"""
        adaptations = []
        
        # UI adaptations
        if profile.cognitive_profile.get('processing_speed', 'average') == 'slow':
            adaptations.append({
                'type': 'ui_adaptation',
                'suggestion': 'Increase response time allowances',
                'impact': 'Reduces cognitive pressure and improves performance'
            })
        
        # Content adaptations
        if profile.learning_patterns.get('difficulty_progression', 'gradual') == 'steep':
            adaptations.append({
                'type': 'content_adaptation',
                'suggestion': 'Provide more challenging content earlier',
                'impact': 'Maintains engagement for fast learners'
            })
        
        # Interaction adaptations
        if profile.behavioral_patterns.get('help_seeking', 'balanced') == 'reluctant':
            adaptations.append({
                'type': 'interaction_adaptation',
                'suggestion': 'Provide proactive hints and guidance',
                'impact': 'Supports learning without requiring explicit help requests'
            })
        
        return adaptations
    
    async def _context_analyzer(self):
        """Background task for analyzing user contexts"""
        while True:
            try:
                # Analyze patterns for all active users
                for user_id, profile in self.active_contexts.items():
                    await self._analyze_user_patterns(user_id, profile)
                
                await asyncio.sleep(300)  # Analyze every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in context analyzer: {e}")
                await asyncio.sleep(60)
    
    async def _context_persister(self):
        """Background task for persisting contexts to database"""
        while True:
            try:
                if self.context_buffer:
                    # Batch persist contexts
                    contexts_to_persist = self.context_buffer.copy()
                    self.context_buffer.clear()
                    
                    await self._persist_contexts(contexts_to_persist)
                
                await asyncio.sleep(30)  # Persist every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in context persister: {e}")
                await asyncio.sleep(10)
    
    async def _context_cleaner(self):
        """Background task for cleaning old contexts"""
        while True:
            try:
                cutoff_time = datetime.utcnow() - timedelta(days=self.context_retention_days)
                
                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute("""
                        DELETE FROM user_contexts WHERE timestamp < ?
                    """, (cutoff_time,))
                    await db.commit()
                
                await asyncio.sleep(3600)  # Clean every hour
                
            except Exception as e:
                self.logger.error(f"Error in context cleaner: {e}")
                await asyncio.sleep(600)
    
    async def _persist_contexts(self, contexts: List[UserContext]):
        """Persist contexts to database"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                for context in contexts:
                    await db.execute("""
                        INSERT INTO user_contexts 
                        (user_id, context_type, data, timestamp, confidence, source, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        context.user_id,
                        context.context_type.value,
                        json.dumps(context.data),
                        context.timestamp,
                        context.confidence,
                        context.source,
                        json.dumps(context.metadata)
                    ))
                
                await db.commit()
                
        except Exception as e:
            self.logger.error(f"Error persisting contexts: {e}")
    
    async def _analyze_user_patterns(self, user_id: str, profile: UserProfile):
        """Analyze patterns for a specific user"""
        try:
            # Run learning pattern analysis
            for pattern_name, analyzer in self.learning_patterns.items():
                result = await analyzer(user_id, profile)
                if result:
                    profile.learning_patterns[pattern_name] = result
            
            # Run behavioral pattern analysis
            for pattern_name, analyzer in self.behavioral_patterns.items():
                result = await analyzer(user_id, profile)
                if result:
                    profile.behavioral_patterns[pattern_name] = result
            
            # Update profile in database
            await self._save_user_profile(profile)
            
        except Exception as e:
            self.logger.error(f"Error analyzing patterns for {user_id}: {e}")
    
    async def _save_user_profile(self, profile: UserProfile):
        """Save user profile to database"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO user_profiles 
                    (user_id, created_at, last_updated, learning_patterns, behavioral_patterns,
                     preferences, performance_metrics, attention_patterns, cognitive_profile, adaptation_history)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.user_id,
                    profile.created_at,
                    profile.last_updated,
                    json.dumps(profile.learning_patterns),
                    json.dumps(profile.behavioral_patterns),
                    json.dumps(profile.preferences),
                    json.dumps(profile.performance_metrics),
                    json.dumps(profile.attention_patterns),
                    json.dumps(profile.cognitive_profile),
                    json.dumps(profile.adaptation_history)
                ))
                
                await db.commit()
                
        except Exception as e:
            self.logger.error(f"Error saving user profile: {e}")
    
    # Pattern analysis methods (simplified implementations)
    async def _analyze_session_length(self, user_id: str, profile: UserProfile) -> Optional[int]:
        """Analyze optimal session length for user"""
        # Implementation would analyze actual session data
        return profile.learning_patterns.get('optimal_session_length', 15)
    
    async def _analyze_attention_decay(self, user_id: str, profile: UserProfile) -> Optional[float]:
        """Analyze attention decay rate"""
        return profile.attention_patterns.get('decay_rate', 0.1)
    
    async def _analyze_learning_velocity(self, user_id: str, profile: UserProfile) -> Optional[str]:
        """Analyze learning velocity"""
        return profile.learning_patterns.get('velocity', 'moderate')
    
    async def _analyze_mistake_patterns(self, user_id: str, profile: UserProfile) -> Optional[Dict]:
        """Analyze mistake patterns"""
        return profile.performance_metrics.get('mistake_patterns', {})
    
    async def _analyze_engagement_triggers(self, user_id: str, profile: UserProfile) -> Optional[List]:
        """Analyze engagement triggers"""
        return profile.behavioral_patterns.get('engagement_triggers', [])
    
    async def _analyze_interaction_frequency(self, user_id: str, profile: UserProfile) -> Optional[str]:
        """Analyze interaction frequency"""
        return profile.behavioral_patterns.get('interaction_frequency', 'moderate')
    
    async def _analyze_navigation_patterns(self, user_id: str, profile: UserProfile) -> Optional[Dict]:
        """Analyze navigation patterns"""
        return profile.behavioral_patterns.get('navigation_patterns', {})
    
    async def _analyze_help_seeking(self, user_id: str, profile: UserProfile) -> Optional[str]:
        """Analyze help-seeking behavior"""
        return profile.behavioral_patterns.get('help_seeking', 'balanced')
    
    async def _analyze_persistence(self, user_id: str, profile: UserProfile) -> Optional[str]:
        """Analyze persistence level"""
        return profile.behavioral_patterns.get('persistence', 'medium')
    
    async def _analyze_social_learning(self, user_id: str, profile: UserProfile) -> Optional[str]:
        """Analyze social learning preference"""
        return profile.behavioral_patterns.get('social_learning', 'individual')


# Convenience function to create and initialize context manager
async def create_user_context_manager(db_path: str = "data/user_contexts.db", 
                                    event_bus: Optional[EventBus] = None) -> UserContextManager:
    """Create and initialize a user context manager"""
    manager = UserContextManager(db_path, event_bus)
    await manager.initialize()
    return manager