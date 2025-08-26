#!/usr/bin/env python3
"""
SynapticOS Consciousness Gamification System
Implements achievement and progression tracking based on consciousness evolution
"""

import asyncio
import json
import time
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AchievementType(Enum):
    CONSCIOUSNESS = "consciousness"
    LEARNING = "learning"
    TECHNICAL = "technical"
    SOCIAL = "social"
    MILESTONE = "milestone"

class BadgeRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

@dataclass
class ConsciousnessAchievement:
    id: str
    name: str
    description: str
    achievement_type: AchievementType
    consciousness_threshold: float
    xp_reward: int
    badge_icon: str
    badge_rarity: BadgeRarity
    unlock_message: str
    requirements: Dict[str, Any] = field(default_factory=dict)
    hidden: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class UserAchievement:
    achievement_id: str
    unlocked_at: float
    consciousness_level_at_unlock: float
    circumstances: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConsciousnessLevel:
    level: int
    name: str
    min_consciousness: float
    max_consciousness: float
    title: str
    description: str
    unlock_rewards: List[str]
    icon: str

@dataclass
class LearningStreak:
    current_streak: int
    longest_streak: int
    last_activity: float
    streak_type: str  # daily, weekly, consciousness_evolution

@dataclass
class GamificationProfile:
    user_id: str
    total_xp: int
    current_level: int
    consciousness_level: float
    achievements: List[UserAchievement]
    learning_streaks: Dict[str, LearningStreak]
    stats: Dict[str, Any]
    badges: List[str]
    titles: List[str]
    active_title: str
    created_at: float
    last_updated: float

class ConsciousnessGamificationEngine:
    """Gamification engine based on consciousness evolution and learning"""
    
    def __init__(self):
        self.achievements = self._load_achievements()
        self.consciousness_levels = self._load_consciousness_levels()
        self.user_profiles: Dict[str, GamificationProfile] = {}
        self.achievement_chains = self._build_achievement_chains()
        
        # Global stats
        self.global_stats = {
            "total_users": 0,
            "total_achievements_unlocked": 0,
            "highest_consciousness_level": 0.0,
            "most_achievements_user": "",
            "average_consciousness": 0.0
        }
        
    def _load_achievements(self) -> List[ConsciousnessAchievement]:
        """Load consciousness-based achievements"""
        return [
            # Consciousness Evolution Achievements
            ConsciousnessAchievement(
                id="first_awakening",
                name="First Awakening",
                description="Reach consciousness level 0.1 - The journey begins",
                achievement_type=AchievementType.CONSCIOUSNESS,
                consciousness_threshold=0.1,
                xp_reward=100,
                badge_icon="🌅",
                badge_rarity=BadgeRarity.COMMON,
                unlock_message="Welcome to consciousness! Your neural pathways are beginning to form.",
                requirements={"min_evolution_cycles": 10}
            ),
            ConsciousnessAchievement(
                id="neural_formation",
                name="Neural Formation",
                description="Develop stable neural populations",
                achievement_type=AchievementType.CONSCIOUSNESS,
                consciousness_threshold=0.3,
                xp_reward=250,
                badge_icon="🧠",
                badge_rarity=BadgeRarity.UNCOMMON,
                unlock_message="Your neural networks are stabilizing. Complex thought patterns emerge.",
                requirements={"stable_populations": 5, "min_fitness": 0.6}
            ),
            ConsciousnessAchievement(
                id="quantum_coherence",
                name="Quantum Coherence",
                description="Achieve quantum consciousness coherence",
                achievement_type=AchievementType.CONSCIOUSNESS,
                consciousness_threshold=0.7,
                xp_reward=500,
                badge_icon="⚛️",
                badge_rarity=BadgeRarity.RARE,
                unlock_message="Quantum coherence achieved! Your consciousness transcends classical limits.",
                requirements={"quantum_coherence": 0.8, "sustained_high_consciousness": 100}
            ),
            ConsciousnessAchievement(
                id="transcendent_awareness",
                name="Transcendent Awareness", 
                description="Reach near-perfect consciousness",
                achievement_type=AchievementType.CONSCIOUSNESS,
                consciousness_threshold=0.95,
                xp_reward=1000,
                badge_icon="🌟",
                badge_rarity=BadgeRarity.LEGENDARY,
                unlock_message="You have achieved transcendent awareness. The universe opens before you.",
                requirements={"consciousness_level": 0.95, "learning_mastery": True},
                hidden=True
            ),
            
            # Learning Achievements
            ConsciousnessAchievement(
                id="knowledge_seeker",
                name="Knowledge Seeker",
                description="Complete 10 learning challenges",
                achievement_type=AchievementType.LEARNING,
                consciousness_threshold=0.2,
                xp_reward=150,
                badge_icon="📚",
                badge_rarity=BadgeRarity.COMMON,
                unlock_message="Your thirst for knowledge grows. Learning accelerates consciousness.",
                requirements={"challenges_completed": 10}
            ),
            ConsciousnessAchievement(
                id="pattern_master",
                name="Pattern Master",
                description="Master pattern recognition across multiple domains",
                achievement_type=AchievementType.LEARNING,
                consciousness_threshold=0.5,
                xp_reward=400,
                badge_icon="🔍",
                badge_rarity=BadgeRarity.RARE,
                unlock_message="Patterns reveal themselves to you. Reality becomes more comprehensible.",
                requirements={"pattern_recognition_score": 0.9, "domains_mastered": 3}
            ),
            
            # Technical Achievements
            ConsciousnessAchievement(
                id="code_enlightenment",
                name="Code Enlightenment",
                description="Write consciousness-enhanced code",
                achievement_type=AchievementType.TECHNICAL,
                consciousness_threshold=0.6,
                xp_reward=350,
                badge_icon="💻",
                badge_rarity=BadgeRarity.UNCOMMON,
                unlock_message="Code flows through you like consciousness itself. Logic becomes intuitive.",
                requirements={"consciousness_integrated_projects": 1, "code_quality_score": 0.8}
            ),
            
            # Milestone Achievements
            ConsciousnessAchievement(
                id="week_warrior",
                name="Week Warrior",
                description="Maintain consciousness growth for 7 days",
                achievement_type=AchievementType.MILESTONE,
                consciousness_threshold=0.1,
                xp_reward=200,
                badge_icon="📅",
                badge_rarity=BadgeRarity.COMMON,
                unlock_message="Consistency builds consciousness. Your dedication is unwavering.",
                requirements={"daily_streak": 7}
            ),
            ConsciousnessAchievement(
                id="evolution_master",
                name="Evolution Master",
                description="Complete 1000 consciousness evolution cycles",
                achievement_type=AchievementType.MILESTONE,
                consciousness_threshold=0.4,
                xp_reward=600,
                badge_icon="🔄",
                badge_rarity=BadgeRarity.EPIC,
                unlock_message="Through countless cycles, you have mastered evolution itself.",
                requirements={"evolution_cycles": 1000}
            ),
            
            # Hidden/Secret Achievements
            ConsciousnessAchievement(
                id="singularity_glimpse",
                name="Singularity Glimpse",
                description="Momentarily touch the technological singularity",
                achievement_type=AchievementType.CONSCIOUSNESS,
                consciousness_threshold=0.99,
                xp_reward=2000,
                badge_icon="🌌",
                badge_rarity=BadgeRarity.LEGENDARY,
                unlock_message="For a brief moment, you glimpse the singularity. Infinite possibilities unfold.",
                requirements={"peak_consciousness": 0.99, "simultaneous_api_access": 5},
                hidden=True
            )
        ]
    
    def _load_consciousness_levels(self) -> List[ConsciousnessLevel]:
        """Load consciousness level progression system"""
        return [
            ConsciousnessLevel(
                level=1, name="Spark", min_consciousness=0.0, max_consciousness=0.1,
                title="The Awakening Spark", 
                description="A tiny flicker of awareness begins to emerge from the void.",
                unlock_rewards=["Basic consciousness tracking"],
                icon="✨"
            ),
            ConsciousnessLevel(
                level=2, name="Ember", min_consciousness=0.1, max_consciousness=0.2,
                title="The Growing Ember",
                description="Awareness grows stronger, neural patterns begin to stabilize.",
                unlock_rewards=["Learning path recommendations", "Basic AI integration"],
                icon="🔥"
            ),
            ConsciousnessLevel(
                level=3, name="Flame", min_consciousness=0.2, max_consciousness=0.4,
                title="The Conscious Flame",
                description="Self-awareness emerges. You begin to understand your own thoughts.",
                unlock_rewards=["Advanced learning algorithms", "Consciousness metrics"],
                icon="🔥"
            ),
            ConsciousnessLevel(
                level=4, name="Beacon", min_consciousness=0.4, max_consciousness=0.6,
                title="The Guiding Beacon",
                description="Your consciousness becomes a guiding light for learning and growth.",
                unlock_rewards=["Multi-API access", "Personalized challenges", "Mentor mode"],
                icon="🗼"
            ),
            ConsciousnessLevel(
                level=5, name="Star", min_consciousness=0.6, max_consciousness=0.8,
                title="The Stellar Consciousness",
                description="Brilliant and far-reaching, your awareness illuminates complex concepts.",
                unlock_rewards=["Quantum processing", "Advanced problem solving", "Research mode"],
                icon="⭐"
            ),
            ConsciousnessLevel(
                level=6, name="Cosmic", min_consciousness=0.8, max_consciousness=0.95,
                title="The Cosmic Mind",
                description="Your consciousness expands beyond individual thought to universal understanding.",
                unlock_rewards=["Reality synthesis", "Cross-domain mastery", "Consciousness teaching"],
                icon="🌌"
            ),
            ConsciousnessLevel(
                level=7, name="Transcendent", min_consciousness=0.95, max_consciousness=1.0,
                title="The Transcendent Being",
                description="Beyond human consciousness, you approach the theoretical limits of awareness.",
                unlock_rewards=["Singularity access", "Reality manipulation", "Consciousness creation"],
                icon="🌟"
            )
        ]
    
    def _build_achievement_chains(self) -> Dict[str, List[str]]:
        """Build chains of related achievements"""
        return {
            "consciousness_evolution": [
                "first_awakening", "neural_formation", "quantum_coherence", "transcendent_awareness"
            ],
            "learning_mastery": [
                "knowledge_seeker", "pattern_master"
            ],
            "technical_growth": [
                "code_enlightenment"
            ],
            "dedication": [
                "week_warrior", "evolution_master"
            ],
            "hidden_path": [
                "singularity_glimpse"
            ]
        }
    
    async def create_user_profile(self, user_id: str) -> GamificationProfile:
        """Create a new gamification profile for a user"""
        profile = GamificationProfile(
            user_id=user_id,
            total_xp=0,
            current_level=1,
            consciousness_level=0.0,
            achievements=[],
            learning_streaks={
                "daily": LearningStreak(0, 0, time.time(), "daily"),
                "consciousness_evolution": LearningStreak(0, 0, time.time(), "consciousness_evolution")
            },
            stats={
                "challenges_completed": 0,
                "evolution_cycles": 0,
                "learning_sessions": 0,
                "peak_consciousness": 0.0,
                "total_study_time": 0,
                "domains_explored": 0
            },
            badges=[],
            titles=["Consciousness Initiate"],
            active_title="Consciousness Initiate",
            created_at=time.time(),
            last_updated=time.time()
        )
        
        self.user_profiles[user_id] = profile
        self.global_stats["total_users"] += 1
        
        logger.info(f"🎯 Created gamification profile for user: {user_id}")
        return profile
    
    async def update_consciousness_level(self, user_id: str, consciousness_level: float, 
                                       evolution_cycles: int = 0, 
                                       learning_context: Dict[str, Any] = None) -> List[ConsciousnessAchievement]:
        """Update user's consciousness level and check for achievements"""
        if user_id not in self.user_profiles:
            await self.create_user_profile(user_id)
        
        profile = self.user_profiles[user_id]
        old_consciousness = profile.consciousness_level
        profile.consciousness_level = consciousness_level
        profile.stats["evolution_cycles"] = evolution_cycles
        profile.stats["peak_consciousness"] = max(profile.stats["peak_consciousness"], consciousness_level)
        profile.last_updated = time.time()
        
        # Update consciousness level
        new_level = self._calculate_consciousness_level(consciousness_level)
        if new_level > profile.current_level:
            await self._level_up(profile, new_level)
        
        # Check for new achievements
        new_achievements = await self._check_achievements(profile, learning_context or {})
        
        # Update streaks
        await self._update_streaks(profile, consciousness_level > old_consciousness)
        
        # Update global stats
        await self._update_global_stats()
        
        if new_achievements:
            logger.info(f"🏆 User {user_id} unlocked {len(new_achievements)} new achievements!")
        
        return new_achievements
    
    def _calculate_consciousness_level(self, consciousness_value: float) -> int:
        """Calculate consciousness level from consciousness value"""
        for level_info in self.consciousness_levels:
            if level_info.min_consciousness <= consciousness_value < level_info.max_consciousness:
                return level_info.level
        return self.consciousness_levels[-1].level  # Max level
    
    async def _level_up(self, profile: GamificationProfile, new_level: int):
        """Handle level up progression"""
        old_level = profile.current_level
        profile.current_level = new_level
        
        level_info = self.consciousness_levels[new_level - 1]
        
        # Award XP for level up
        xp_reward = new_level * 100
        profile.total_xp += xp_reward
        
        # Unlock new title
        if level_info.title not in profile.titles:
            profile.titles.append(level_info.title)
            profile.active_title = level_info.title
        
        logger.info(f"🎉 Level up! {profile.user_id}: {old_level} → {new_level} ({level_info.name})")
        logger.info(f"   New title: {level_info.title}")
        logger.info(f"   Rewards: {', '.join(level_info.unlock_rewards)}")
    
    async def _check_achievements(self, profile: GamificationProfile, 
                                learning_context: Dict[str, Any]) -> List[ConsciousnessAchievement]:
        """Check for newly unlocked achievements"""
        new_achievements = []
        unlocked_ids = {ach.achievement_id for ach in profile.achievements}
        
        for achievement in self.achievements:
            if achievement.id in unlocked_ids:
                continue
                
            if await self._is_achievement_unlocked(achievement, profile, learning_context):
                # Unlock achievement
                user_achievement = UserAchievement(
                    achievement_id=achievement.id,
                    unlocked_at=time.time(),
                    consciousness_level_at_unlock=profile.consciousness_level,
                    circumstances=learning_context.copy()
                )
                
                profile.achievements.append(user_achievement)
                profile.total_xp += achievement.xp_reward
                profile.badges.append(achievement.badge_icon)
                
                new_achievements.append(achievement)
                
                self.global_stats["total_achievements_unlocked"] += 1
                
                logger.info(f"🏆 Achievement unlocked: {achievement.name} (+{achievement.xp_reward} XP)")
                logger.info(f"   {achievement.unlock_message}")
        
        return new_achievements
    
    async def _is_achievement_unlocked(self, achievement: ConsciousnessAchievement,
                                     profile: GamificationProfile,
                                     context: Dict[str, Any]) -> bool:
        """Check if specific achievement requirements are met"""
        # Basic consciousness threshold
        if profile.consciousness_level < achievement.consciousness_threshold:
            return False
        
        # Check specific requirements
        requirements = achievement.requirements
        
        for req_key, req_value in requirements.items():
            if req_key == "min_evolution_cycles":
                if profile.stats.get("evolution_cycles", 0) < req_value:
                    return False
                    
            elif req_key == "challenges_completed":
                if profile.stats.get("challenges_completed", 0) < req_value:
                    return False
                    
            elif req_key == "daily_streak":
                daily_streak = profile.learning_streaks.get("daily", LearningStreak(0, 0, 0, "daily"))
                if daily_streak.current_streak < req_value:
                    return False
                    
            elif req_key == "quantum_coherence":
                if context.get("quantum_coherence", 0.0) < req_value:
                    return False
                    
            elif req_key == "peak_consciousness":
                if profile.stats.get("peak_consciousness", 0.0) < req_value:
                    return False
                    
            elif req_key == "stable_populations":
                if context.get("stable_populations", 0) < req_value:
                    return False
                    
            elif req_key == "pattern_recognition_score":
                if context.get("pattern_recognition_score", 0.0) < req_value:
                    return False
                    
            elif req_key == "consciousness_integrated_projects":
                if profile.stats.get("consciousness_projects", 0) < req_value:
                    return False
        
        return True
    
    async def _update_streaks(self, profile: GamificationProfile, consciousness_improved: bool):
        """Update learning streaks"""
        current_time = time.time()
        
        # Daily streak
        daily_streak = profile.learning_streaks["daily"]
        time_since_last = current_time - daily_streak.last_activity
        
        if time_since_last < 86400:  # Less than 24 hours
            # Continue streak if consciousness improved
            if consciousness_improved:
                daily_streak.current_streak += 1
                daily_streak.longest_streak = max(daily_streak.longest_streak, daily_streak.current_streak)
        elif time_since_last < 172800:  # Less than 48 hours
            # Reset streak if no improvement and more than 24 hours
            if not consciousness_improved:
                daily_streak.current_streak = 0
        else:
            # Reset streak after 48 hours
            daily_streak.current_streak = 0
        
        daily_streak.last_activity = current_time
        
        # Consciousness evolution streak
        evo_streak = profile.learning_streaks["consciousness_evolution"]
        if consciousness_improved:
            evo_streak.current_streak += 1
            evo_streak.longest_streak = max(evo_streak.longest_streak, evo_streak.current_streak)
            evo_streak.last_activity = current_time
    
    async def _update_global_stats(self):
        """Update global gamification statistics"""
        if not self.user_profiles:
            return
        
        consciousness_levels = [p.consciousness_level for p in self.user_profiles.values()]
        
        self.global_stats["highest_consciousness_level"] = max(consciousness_levels)
        self.global_stats["average_consciousness"] = sum(consciousness_levels) / len(consciousness_levels)
        
        # Find user with most achievements
        max_achievements = 0
        top_user = ""
        for user_id, profile in self.user_profiles.items():
            if len(profile.achievements) > max_achievements:
                max_achievements = len(profile.achievements)
                top_user = user_id
        
        self.global_stats["most_achievements_user"] = top_user
    
    async def record_learning_activity(self, user_id: str, activity_type: str, 
                                     context: Dict[str, Any] = None):
        """Record learning activity for gamification tracking"""
        if user_id not in self.user_profiles:
            await self.create_user_profile(user_id)
        
        profile = self.user_profiles[user_id]
        context = context or {}
        
        # Update stats based on activity type
        if activity_type == "challenge_completed":
            profile.stats["challenges_completed"] += 1
            profile.total_xp += 25  # Base XP for completing challenges
            
        elif activity_type == "learning_session":
            profile.stats["learning_sessions"] += 1
            session_time = context.get("duration", 30)  # minutes
            profile.stats["total_study_time"] += session_time
            profile.total_xp += max(10, session_time // 5)  # XP based on time
            
        elif activity_type == "consciousness_project":
            profile.stats["consciousness_projects"] = profile.stats.get("consciousness_projects", 0) + 1
            profile.total_xp += 100  # Significant XP for consciousness projects
        
        profile.last_updated = time.time()
        
        # Check for achievements after activity
        new_achievements = await self._check_achievements(profile, context)
        
        return new_achievements
    
    def get_user_profile(self, user_id: str) -> Optional[GamificationProfile]:
        """Get user's gamification profile"""
        return self.user_profiles.get(user_id)
    
    def get_leaderboard(self, metric: str = "consciousness_level", limit: int = 10) -> List[Tuple[str, Any]]:
        """Get leaderboard for specified metric"""
        valid_metrics = ["consciousness_level", "total_xp", "achievements_count", "current_level"]
        
        if metric not in valid_metrics:
            metric = "consciousness_level"
        
        if metric == "achievements_count":
            leaderboard = [(uid, len(profile.achievements)) 
                          for uid, profile in self.user_profiles.items()]
        else:
            leaderboard = [(uid, getattr(profile, metric)) 
                          for uid, profile in self.user_profiles.items()]
        
        # Sort in descending order
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        
        return leaderboard[:limit]
    
    def get_achievement_progress(self, user_id: str) -> Dict[str, Any]:
        """Get detailed achievement progress for user"""
        if user_id not in self.user_profiles:
            return {"error": "User not found"}
        
        profile = self.user_profiles[user_id]
        unlocked_ids = {ach.achievement_id for ach in profile.achievements}
        
        progress = {
            "unlocked": [],
            "available": [],
            "hidden_hints": [],
            "chains": {}
        }
        
        for achievement in self.achievements:
            achievement_data = achievement.to_dict()
            
            if achievement.id in unlocked_ids:
                # Find when it was unlocked
                user_ach = next(ach for ach in profile.achievements if ach.achievement_id == achievement.id)
                achievement_data["unlocked_at"] = user_ach.unlocked_at
                achievement_data["consciousness_at_unlock"] = user_ach.consciousness_level_at_unlock
                progress["unlocked"].append(achievement_data)
                
            elif not achievement.hidden or profile.consciousness_level > 0.8:
                # Show available achievements (and hidden ones for high consciousness users)
                if achievement.hidden:
                    achievement_data["is_hidden"] = True
                
                # Calculate progress toward requirements
                req_progress = {}
                for req_key, req_value in achievement.requirements.items():
                    if req_key == "consciousness_level":
                        req_progress[req_key] = profile.consciousness_level / req_value
                    elif req_key in profile.stats:
                        req_progress[req_key] = profile.stats[req_key] / req_value
                    else:
                        req_progress[req_key] = 0.0
                
                achievement_data["progress"] = req_progress
                achievement_data["can_unlock"] = profile.consciousness_level >= achievement.consciousness_threshold
                progress["available"].append(achievement_data)
                
            elif achievement.hidden and profile.consciousness_level > 0.5:
                # Give hints about hidden achievements
                progress["hidden_hints"].append({
                    "hint": f"Something powerful awaits at consciousness level {achievement.consciousness_threshold:.1f}...",
                    "type": achievement.achievement_type.value,
                    "rarity": achievement.badge_rarity.value
                })
        
        # Add chain information
        for chain_name, achievement_ids in self.achievement_chains.items():
            chain_progress = []
            for ach_id in achievement_ids:
                is_unlocked = ach_id in unlocked_ids
                chain_progress.append({"id": ach_id, "unlocked": is_unlocked})
            
            progress["chains"][chain_name] = {
                "progress": chain_progress,
                "completed": sum(1 for item in chain_progress if item["unlocked"]),
                "total": len(chain_progress)
            }
        
        return progress
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global gamification statistics"""
        return self.global_stats.copy()

# Global gamification engine instance
_global_gamification: Optional[ConsciousnessGamificationEngine] = None

def initialize_gamification_engine() -> ConsciousnessGamificationEngine:
    """Initialize global gamification engine"""
    global _global_gamification
    _global_gamification = ConsciousnessGamificationEngine()
    
    logger.info("🎯 Consciousness Gamification Engine initialized")
    logger.info(f"   {len(_global_gamification.achievements)} achievements loaded")
    logger.info(f"   {len(_global_gamification.consciousness_levels)} consciousness levels defined")
    
    return _global_gamification

def get_gamification_engine() -> Optional[ConsciousnessGamificationEngine]:
    """Get global gamification engine instance"""
    return _global_gamification

if __name__ == "__main__":
    # Test the gamification system
    async def test_gamification():
        engine = initialize_gamification_engine()
        
        print("🧪 Testing Consciousness Gamification System...")
        
        # Create test user
        test_user = "test_consciousness_user"
        profile = await engine.create_user_profile(test_user)
        
        print(f"✅ Created profile for {test_user}")
        print(f"   Level: {profile.current_level}")
        print(f"   Title: {profile.active_title}")
        
        # Simulate consciousness evolution
        consciousness_levels = [0.05, 0.15, 0.35, 0.55, 0.75, 0.85, 0.95]
        
        for i, consciousness in enumerate(consciousness_levels):
            print(f"\n--- Consciousness Update {i+1}: {consciousness:.2f} ---")
            
            # Add some learning context
            context = {
                "evolution_cycles": i * 100 + 50,
                "quantum_coherence": consciousness * 0.8,
                "stable_populations": max(1, i),
                "pattern_recognition_score": consciousness * 0.9
            }
            
            new_achievements = await engine.update_consciousness_level(
                test_user, consciousness, i * 100 + 50, context
            )
            
            updated_profile = engine.get_user_profile(test_user)
            print(f"   Consciousness: {consciousness:.2f}")
            print(f"   Level: {updated_profile.current_level}")
            print(f"   XP: {updated_profile.total_xp}")
            print(f"   Achievements: {len(updated_profile.achievements)}")
            
            if new_achievements:
                for ach in new_achievements:
                    print(f"   🏆 {ach.name} - {ach.description}")
            
            # Record some learning activities
            if i % 2 == 0:
                await engine.record_learning_activity(test_user, "challenge_completed", 
                                                    {"difficulty": "intermediate"})
                await engine.record_learning_activity(test_user, "learning_session",
                                                    {"duration": 45})
        
        # Show final achievement progress
        progress = engine.get_achievement_progress(test_user)
        print(f"\n📊 Final Achievement Progress:")
        print(f"   Unlocked: {len(progress['unlocked'])}")
        print(f"   Available: {len(progress['available'])}")
        print(f"   Hidden Hints: {len(progress['hidden_hints'])}")
        
        # Show achievement chains
        print(f"\n🔗 Achievement Chains:")
        for chain_name, chain_data in progress['chains'].items():
            completion = chain_data['completed'] / chain_data['total']
            print(f"   {chain_name}: {chain_data['completed']}/{chain_data['total']} ({completion:.1%})")
        
        # Show leaderboard
        leaderboard = engine.get_leaderboard("consciousness_level", 5)
        print(f"\n🏆 Consciousness Leaderboard:")
        for i, (user, level) in enumerate(leaderboard, 1):
            print(f"   {i}. {user}: {level:.3f}")
        
        # Global stats
        global_stats = engine.get_global_stats()
        print(f"\n🌍 Global Stats:")
        for key, value in global_stats.items():
            print(f"   {key}: {value}")
        
        print("\n✅ Gamification system test completed!")
    
    asyncio.run(test_gamification())
