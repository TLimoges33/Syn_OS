#!/usr/bin/env python3
"""
Personal Context Engine for SynapticOS
Tracks user behavior, skills, and preferences to provide adaptive experiences
"""

import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque
import numpy as np
from enum import Enum

logger = logging.getLogger('synapticos.context_engine')

class SkillLevel(Enum):
    """User skill levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ActivityType(Enum):
    """Types of user activities"""
    LEARNING = "learning"
    PRACTICING = "practicing"
    RESEARCHING = "researching"
    DEVELOPING = "developing"
    TESTING = "testing"
    EXPLOITING = "exploiting"

@dataclass
class SkillProfile:
    """User's skill profile for a specific domain"""
    domain: str
    level: SkillLevel
    experience_points: int = 0
    completed_modules: List[str] = field(default_factory=list)
    success_rate: float = 0.0
    last_activity: datetime = field(default_factory=datetime.now)
    time_spent_hours: float = 0.0
    
    def update_experience(self, points: int):
        """Update experience and potentially level up"""
        self.experience_points += points
        
        # Level progression thresholds
        thresholds = {
            SkillLevel.BEGINNER: 100,
            SkillLevel.INTERMEDIATE: 500,
            SkillLevel.ADVANCED: 2000,
            SkillLevel.EXPERT: 10000
        }
        
        # Check for level up
        current_threshold = thresholds.get(self.level, float('inf'))
        if self.experience_points >= current_threshold:
            levels = list(SkillLevel)
            current_index = levels.index(self.level)
            if current_index < len(levels) - 1:
                self.level = levels[current_index + 1]
                logger.info(f"Level up! {self.domain} is now {self.level.value}")

@dataclass
class UserActivity:
    """Record of a user activity"""
    timestamp: datetime
    activity_type: ActivityType
    domain: str
    tool_used: str
    duration_seconds: int
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserContext:
    """Complete user context"""
    user_id: str
    created_at: datetime = field(default_factory=datetime.now)
    skill_profiles: Dict[str, SkillProfile] = field(default_factory=dict)
    activity_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    preferences: Dict[str, Any] = field(default_factory=dict)
    learning_style: str = "balanced"
    current_goals: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)

class PersonalContextEngine:
    """Main context engine for tracking and adapting to user behavior"""
    
    def __init__(self, storage_path: str = "/var/lib/synapticos/context"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.contexts: Dict[str, UserContext] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.skill_domains = [
            "network_security", "web_exploitation", "cryptography",
            "forensics", "reverse_engineering", "social_engineering",
            "malware_analysis", "cloud_security", "mobile_security"
        ]
        
        # Learning adaptation parameters
        self.adaptation_weights = {
            'success_rate': 0.4,
            'time_spent': 0.2,
            'consistency': 0.2,
            'challenge_seeking': 0.2
        }
        
    async def initialize(self) -> bool:
        """Initialize the context engine"""
        try:
            # Load existing contexts
            await self._load_contexts()
            logger.info("Personal Context Engine initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize context engine: {e}")
            return False
    
    async def get_or_create_context(self, user_id: str) -> UserContext:
        """Get existing context or create new one"""
        if user_id not in self.contexts:
            context = UserContext(user_id=user_id)
            
            # Initialize skill profiles
            for domain in self.skill_domains:
                context.skill_profiles[domain] = SkillProfile(
                    domain=domain,
                    level=SkillLevel.BEGINNER
                )
            
            self.contexts[user_id] = context
            await self._save_context(user_id)
            
        return self.contexts[user_id]
    
    async def record_activity(self, 
                            user_id: str,
                            activity_type: ActivityType,
                            domain: str,
                            tool_used: str,
                            duration_seconds: int,
                            success: bool,
                            metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record a user activity"""
        
        context = await self.get_or_create_context(user_id)
        
        # Create activity record
        activity = UserActivity(
            timestamp=datetime.now(),
            activity_type=activity_type,
            domain=domain,
            tool_used=tool_used,
            duration_seconds=duration_seconds,
            success=success,
            metadata=metadata or {}
        )
        
        # Add to history
        context.activity_history.append(activity)
        
        # Update skill profile
        if domain in context.skill_profiles:
            profile = context.skill_profiles[domain]
            
            # Update time spent
            profile.time_spent_hours += duration_seconds / 3600
            
            # Update experience based on activity
            exp_gain = self._calculate_experience_gain(activity_type, success, duration_seconds)
            profile.update_experience(exp_gain)
            
            # Update success rate
            recent_activities = [a for a in context.activity_history 
                               if a.domain == domain and a.timestamp > datetime.now() - timedelta(days=7)]
            if recent_activities:
                success_count = sum(1 for a in recent_activities if a.success)
                profile.success_rate = success_count / len(recent_activities)
            
            profile.last_activity = datetime.now()
        
        # Save context
        await self._save_context(user_id)
        
        # Trigger adaptation if needed
        await self._check_adaptation_triggers(user_id, context)
    
    def _calculate_experience_gain(self, 
                                 activity_type: ActivityType, 
                                 success: bool, 
                                 duration_seconds: int) -> int:
        """Calculate experience points gained from an activity"""
        
        base_points = {
            ActivityType.LEARNING: 10,
            ActivityType.PRACTICING: 15,
            ActivityType.RESEARCHING: 12,
            ActivityType.DEVELOPING: 20,
            ActivityType.TESTING: 25,
            ActivityType.EXPLOITING: 30
        }
        
        points = base_points.get(activity_type, 10)
        
        # Success multiplier
        if success:
            points *= 1.5
        else:
            points *= 0.7  # Still gain some experience from failures
        
        # Duration bonus (up to 2x for longer sessions)
        duration_multiplier = min(2.0, 1.0 + (duration_seconds / 3600))
        points *= duration_multiplier
        
        return int(points)
    
    async def get_skill_level(self, user_id: str, domain: str) -> SkillLevel:
        """Get user's skill level in a domain"""
        context = await self.get_or_create_context(user_id)
        
        if domain in context.skill_profiles:
            return context.skill_profiles[domain].level
        
        return SkillLevel.BEGINNER
    
    async def get_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Get personalized recommendations for the user"""
        context = await self.get_or_create_context(user_id)
        
        recommendations = {
            'next_modules': [],
            'suggested_tools': [],
            'skill_focus': [],
            'challenge_level': 'moderate'
        }
        
        # Analyze skill gaps
        weakest_skills = sorted(
            context.skill_profiles.items(),
            key=lambda x: (x[1].level.value, x[1].experience_points)
        )[:3]
        
        recommendations['skill_focus'] = [skill[0] for skill in weakest_skills]
        
        # Suggest modules based on current level
        for domain, profile in context.skill_profiles.items():
            if profile.level == SkillLevel.BEGINNER:
                recommendations['next_modules'].append(f"{domain}_basics")
            elif profile.level == SkillLevel.INTERMEDIATE:
                recommendations['next_modules'].append(f"{domain}_advanced")
        
        # Analyze learning patterns
        recent_activities = list(context.activity_history)[-50:]
        if recent_activities:
            success_rate = sum(1 for a in recent_activities if a.success) / len(recent_activities)
            
            if success_rate > 0.8:
                recommendations['challenge_level'] = 'hard'
            elif success_rate < 0.4:
                recommendations['challenge_level'] = 'easy'
        
        # Tool recommendations based on activity
        tool_usage = defaultdict(int)
        for activity in recent_activities:
            tool_usage[activity.tool_used] += 1
        
        # Suggest tools they haven't used much
        all_tools = ['nmap', 'burpsuite', 'metasploit', 'wireshark', 'john', 'hashcat', 'sqlmap']
        unused_tools = [tool for tool in all_tools if tool_usage[tool] < 3]
        recommendations['suggested_tools'] = unused_tools[:3]
        
        return recommendations
    
    async def get_learning_path(self, user_id: str, target_skill: str) -> List[Dict[str, Any]]:
        """Generate a personalized learning path"""
        context = await self.get_or_create_context(user_id)
        current_level = context.skill_profiles.get(target_skill, SkillProfile(domain=target_skill, level=SkillLevel.BEGINNER)).level
        
        path = []
        
        # Define learning modules for each level
        modules = {
            SkillLevel.BEGINNER: [
                {'name': f'{target_skill}_fundamentals', 'duration': '2 hours', 'type': 'theory'},
                {'name': f'{target_skill}_basic_tools', 'duration': '3 hours', 'type': 'practical'},
                {'name': f'{target_skill}_first_challenge', 'duration': '1 hour', 'type': 'challenge'}
            ],
            SkillLevel.INTERMEDIATE: [
                {'name': f'{target_skill}_advanced_concepts', 'duration': '3 hours', 'type': 'theory'},
                {'name': f'{target_skill}_real_scenarios', 'duration': '4 hours', 'type': 'practical'},
                {'name': f'{target_skill}_ctf_practice', 'duration': '2 hours', 'type': 'challenge'}
            ],
            SkillLevel.ADVANCED: [
                {'name': f'{target_skill}_expert_techniques', 'duration': '4 hours', 'type': 'theory'},
                {'name': f'{target_skill}_tool_development', 'duration': '6 hours', 'type': 'practical'},
                {'name': f'{target_skill}_research_project', 'duration': '8 hours', 'type': 'project'}
            ]
        }
        
        # Build path from current level to expert
        levels = list(SkillLevel)
        current_index = levels.index(current_level)
        
        for i in range(current_index, len(levels) - 1):
            level = levels[i]
            if level in modules:
                for module in modules[level]:
                    module['skill_level'] = level.value
                    module['estimated_xp'] = 50 * (i + 1)
                    path.append(module)
        
        return path
    
    async def adapt_difficulty(self, user_id: str, domain: str) -> Dict[str, Any]:
        """Adapt difficulty based on user performance"""
        context = await self.get_or_create_context(user_id)
        profile = context.skill_profiles.get(domain)
        
        if not profile:
            return {'difficulty': 'normal', 'hints_enabled': True}
        
        # Analyze recent performance
        recent_activities = [a for a in context.activity_history 
                           if a.domain == domain and a.timestamp > datetime.now() - timedelta(days=3)]
        
        if not recent_activities:
            return {'difficulty': 'normal', 'hints_enabled': True}
        
        success_rate = sum(1 for a in recent_activities if a.success) / len(recent_activities)
        avg_duration = sum(a.duration_seconds for a in recent_activities) / len(recent_activities)
        
        # Determine difficulty adjustment
        if success_rate > 0.85 and avg_duration < 1800:  # High success, quick completion
            difficulty = 'hard'
            hints_enabled = False
        elif success_rate < 0.3:  # Struggling
            difficulty = 'easy'
            hints_enabled = True
        else:
            difficulty = 'normal'
            hints_enabled = success_rate < 0.5
        
        return {
            'difficulty': difficulty,
            'hints_enabled': hints_enabled,
            'success_rate': success_rate,
            'recommended_break': avg_duration > 7200  # Suggest break after 2 hours
        }
    
    async def _check_adaptation_triggers(self, user_id: str, context: UserContext) -> None:
        """Check if any adaptation triggers are met"""
        
        # Check for achievement unlocks
        total_experience = sum(p.experience_points for p in context.skill_profiles.values())
        
        achievements = [
            ('first_steps', 50, "Complete your first challenge"),
            ('dedicated_learner', 500, "Earn 500 total experience points"),
            ('multi_skilled', 1000, "Reach intermediate in 3 domains"),
            ('expert_hacker', 5000, "Reach expert level in any domain")
        ]
        
        for achievement_id, threshold, description in achievements:
            if achievement_id not in context.achievements:
                if achievement_id == 'first_steps' and total_experience >= threshold:
                    context.achievements.append(achievement_id)
                    logger.info(f"Achievement unlocked for {user_id}: {description}")
                elif achievement_id == 'multi_skilled':
                    intermediate_count = sum(1 for p in context.skill_profiles.values() 
                                           if p.level.value >= SkillLevel.INTERMEDIATE.value)
                    if intermediate_count >= 3:
                        context.achievements.append(achievement_id)
                        logger.info(f"Achievement unlocked for {user_id}: {description}")
    
    async def _save_context(self, user_id: str) -> None:
        """Save user context to disk"""
        if user_id in self.contexts:
            context_file = self.storage_path / f"{user_id}.json"
            
            # Convert to serializable format
            context_dict = {
                'user_id': self.contexts[user_id].user_id,
                'created_at': self.contexts[user_id].created_at.isoformat(),
                'skill_profiles': {
                    domain: {
                        'domain': profile.domain,
                        'level': profile.level.value,
                        'experience_points': profile.experience_points,
                        'completed_modules': profile.completed_modules,
                        'success_rate': profile.success_rate,
                        'last_activity': profile.last_activity.isoformat(),
                        'time_spent_hours': profile.time_spent_hours
                    }
                    for domain, profile in self.contexts[user_id].skill_profiles.items()
                },
                'preferences': self.contexts[user_id].preferences,
                'learning_style': self.contexts[user_id].learning_style,
                'current_goals': self.contexts[user_id].current_goals,
                'achievements': self.contexts[user_id].achievements
            }
            
            with open(context_file, 'w') as f:
                json.dump(context_dict, f, indent=2)
    
    async def _load_contexts(self) -> None:
        """Load all user contexts from disk"""
        for context_file in self.storage_path.glob("*.json"):
            try:
                with open(context_file) as f:
                    data = json.load(f)
                
                # Reconstruct context
                context = UserContext(
                    user_id=data['user_id'],
                    created_at=datetime.fromisoformat(data['created_at']),
                    preferences=data.get('preferences', {}),
                    learning_style=data.get('learning_style', 'balanced'),
                    current_goals=data.get('current_goals', []),
                    achievements=data.get('achievements', [])
                )
                
                # Reconstruct skill profiles
                for domain, profile_data in data.get('skill_profiles', {}).items():
                    context.skill_profiles[domain] = SkillProfile(
                        domain=profile_data['domain'],
                        level=SkillLevel(profile_data['level']),
                        experience_points=profile_data['experience_points'],
                        completed_modules=profile_data['completed_modules'],
                        success_rate=profile_data['success_rate'],
                        last_activity=datetime.fromisoformat(profile_data['last_activity']),
                        time_spent_hours=profile_data['time_spent_hours']
                    )
                
                self.contexts[context.user_id] = context
                
            except Exception as e:
                logger.error(f"Failed to load context from {context_file}: {e}")
    
    def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        if user_id not in self.contexts:
            return {}
        
        context = self.contexts[user_id]
        
        return {
            'total_experience': sum(p.experience_points for p in context.skill_profiles.values()),
            'total_time_hours': sum(p.time_spent_hours for p in context.skill_profiles.values()),
            'skill_levels': {d: p.level.value for d, p in context.skill_profiles.items()},
            'achievements_count': len(context.achievements),
            'average_success_rate': np.mean([p.success_rate for p in context.skill_profiles.values()]),
            'most_active_domain': max(context.skill_profiles.items(), 
                                     key=lambda x: x[1].time_spent_hours)[0] if context.skill_profiles else None
        }


# Example usage
async def main():
    """Example usage of Personal Context Engine"""
    engine = PersonalContextEngine()
    await engine.initialize()
    
    # Simulate user activity
    user_id = "test_user"
    
    # Record some activities
    await engine.record_activity(
        user_id=user_id,
        activity_type=ActivityType.LEARNING,
        domain="network_security",
        tool_used="nmap",
        duration_seconds=1800,
        success=True
    )
    
    # Get recommendations
    recommendations = await engine.get_recommendations(user_id)
    print(f"Recommendations: {recommendations}")
    
    # Get skill level
    skill_level = await engine.get_skill_level(user_id, "network_security")
    print(f"Network Security Level: {skill_level.value}")
    
    # Get learning path
    path = await engine.get_learning_path(user_id, "web_exploitation")
    print(f"Learning Path: {path}")
    
    # Get statistics
    stats = engine.get_statistics(user_id)
    print(f"User Statistics: {stats}")


if __name__ == "__main__":
    asyncio.run(main())