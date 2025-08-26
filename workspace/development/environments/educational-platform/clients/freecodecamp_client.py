#!/usr/bin/env python3
"""
SynapticOS Educational Platform - FreeCodeCamp Integration
Connects to FreeCodeCamp with consciousness-aware learning
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class Challenge:
    id: str
    title: str
    description: str
    difficulty: DifficultyLevel
    topics: List[str]
    estimated_time: int  # minutes
    consciousness_requirement: float
    completion_rate: float

@dataclass
class UserProgress:
    username: str
    completed_challenges: List[str]
    current_streak: int
    total_points: int
    consciousness_level: float
    learning_path: List[str]
    strengths: List[str]
    areas_for_improvement: List[str]

class FreeCodeCampClient:
    """FreeCodeCamp API client with consciousness integration"""
    
    def __init__(self):
        self.base_url = "https://www.freecodecamp.org/api"
        self.consciousness_tracker = None
        self.session = None
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def initialize(self):
        """Initialize the client and session"""
        self.session = aiohttp.ClientSession()
        logger.info("🎓 FreeCodeCamp client initialized")
        
    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.close()
            
    async def get_user_progress(self, username: str) -> Optional[UserProgress]:
        """Get user progress from FreeCodeCamp"""
        cache_key = f"user_progress_{username}"
        
        # Check cache first
        if self._is_cached(cache_key):
            return self.cache[cache_key]["data"]
            
        try:
            async with self.session.get(
                f"{self.base_url}/users/get-public-profile",
                params={"username": username},
                timeout=10
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Parse FreeCodeCamp data into our format
                    progress = self._parse_user_progress(data, username)
                    
                    # Cache the result
                    self._cache_data(cache_key, progress)
                    
                    logger.info(f"✅ Retrieved progress for user: {username}")
                    return progress
                else:
                    logger.warning(f"⚠️ FreeCodeCamp API returned status {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error fetching user progress: {e}")
            return None
    
    def _parse_user_progress(self, data: Dict, username: str) -> UserProgress:
        """Parse FreeCodeCamp API response into UserProgress"""
        points = data.get("points", 0)
        completed = data.get("completedChallenges", [])
        
        # Calculate consciousness level based on progress
        consciousness_level = min(1.0, len(completed) * 0.01 + points * 0.0001)
        
        # Determine learning path based on completed challenges
        learning_path = self._analyze_learning_path(completed)
        
        # Identify strengths and improvement areas
        strengths, improvements = self._analyze_skills(completed)
        
        return UserProgress(
            username=username,
            completed_challenges=[c.get("id", "") for c in completed],
            current_streak=data.get("currentStreak", 0),
            total_points=points,
            consciousness_level=consciousness_level,
            learning_path=learning_path,
            strengths=strengths,
            areas_for_improvement=improvements
        )
    
    def _analyze_learning_path(self, completed_challenges: List[Dict]) -> List[str]:
        """Analyze completed challenges to suggest learning path"""
        topics = {}
        for challenge in completed_challenges:
            challenge_topics = challenge.get("challengeType", "general")
            topics[challenge_topics] = topics.get(challenge_topics, 0) + 1
        
        # Sort topics by completion count
        sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
        
        # Suggest next learning areas
        common_paths = [
            "Responsive Web Design",
            "JavaScript Algorithms and Data Structures", 
            "Front End Development Libraries",
            "Data Visualization",
            "Back End Development and APIs",
            "Quality Assurance",
            "Scientific Computing with Python",
            "Data Analysis with Python",
            "Information Security",
            "Machine Learning with Python"
        ]
        
        return common_paths[:5]  # Return top 5 recommendations
    
    def _analyze_skills(self, completed_challenges: List[Dict]) -> tuple:
        """Analyze skills from completed challenges"""
        skill_counts = {}
        
        # Map challenge types to skills
        skill_mapping = {
            "html": ["HTML", "Web Development"],
            "css": ["CSS", "Styling", "Design"],
            "javascript": ["JavaScript", "Programming", "Logic"],
            "python": ["Python", "Data Science", "Backend"],
            "react": ["React", "Frontend Frameworks"],
            "node": ["Node.js", "Backend Development"]
        }
        
        for challenge in completed_challenges:
            challenge_id = challenge.get("id", "").lower()
            for skill_key, skills in skill_mapping.items():
                if skill_key in challenge_id:
                    for skill in skills:
                        skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Sort skills by count
        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
        
        strengths = [skill for skill, count in sorted_skills[:3]]
        
        # Areas for improvement (skills with low counts or missing)
        all_skills = set()
        for skills in skill_mapping.values():
            all_skills.update(skills)
        
        weak_skills = [skill for skill in all_skills if skill_counts.get(skill, 0) < 2]
        improvements = weak_skills[:3]
        
        return strengths, improvements
    
    async def get_challenges_by_consciousness_level(self, consciousness_level: float) -> List[Challenge]:
        """Get challenges appropriate for consciousness level"""
        cache_key = f"challenges_consciousness_{consciousness_level:.1f}"
        
        if self._is_cached(cache_key):
            return self.cache[cache_key]["data"]
        
        try:
            # Map consciousness level to difficulty
            if consciousness_level < 0.3:
                target_difficulty = DifficultyLevel.BEGINNER
                topics = ["HTML", "CSS", "Basic JavaScript"]
            elif consciousness_level < 0.6:
                target_difficulty = DifficultyLevel.INTERMEDIATE
                topics = ["JavaScript", "React", "APIs"]
            elif consciousness_level < 0.8:
                target_difficulty = DifficultyLevel.ADVANCED
                topics = ["Data Structures", "Algorithms", "Backend"]
            else:
                target_difficulty = DifficultyLevel.EXPERT
                topics = ["Machine Learning", "Advanced JavaScript", "System Design"]
            
            challenges = await self._fetch_challenges_by_topics(topics, target_difficulty)
            
            # Cache the result
            self._cache_data(cache_key, challenges)
            
            logger.info(f"📚 Found {len(challenges)} challenges for consciousness level {consciousness_level:.2f}")
            return challenges
            
        except Exception as e:
            logger.error(f"❌ Error fetching challenges: {e}")
            return []
    
    async def _fetch_challenges_by_topics(self, topics: List[str], difficulty: DifficultyLevel) -> List[Challenge]:
        """Fetch challenges from FreeCodeCamp by topics"""
        # This is a simplified implementation
        # In a real scenario, you'd query the FreeCodeCamp API for specific challenges
        
        sample_challenges = [
            Challenge(
                id="responsive-web-design-1",
                title="Build a Tribute Page",
                description="Build a tribute page using HTML and CSS",
                difficulty=DifficultyLevel.BEGINNER,
                topics=["HTML", "CSS"],
                estimated_time=60,
                consciousness_requirement=0.2,
                completion_rate=0.85
            ),
            Challenge(
                id="javascript-algorithms-1", 
                title="Palindrome Checker",
                description="Check if a string is a palindrome",
                difficulty=DifficultyLevel.INTERMEDIATE,
                topics=["JavaScript", "Algorithms"],
                estimated_time=30,
                consciousness_requirement=0.4,
                completion_rate=0.65
            ),
            Challenge(
                id="data-structures-1",
                title="Binary Search Tree",
                description="Implement a binary search tree",
                difficulty=DifficultyLevel.ADVANCED,
                topics=["Data Structures", "JavaScript"],
                estimated_time=120,
                consciousness_requirement=0.7,
                completion_rate=0.35
            ),
            Challenge(
                id="machine-learning-1",
                title="Neural Network from Scratch",
                description="Build a neural network without libraries",
                difficulty=DifficultyLevel.EXPERT,
                topics=["Machine Learning", "Python"],
                estimated_time=240,
                consciousness_requirement=0.9,
                completion_rate=0.15
            )
        ]
        
        # Filter by difficulty and topics
        filtered_challenges = []
        for challenge in sample_challenges:
            if challenge.difficulty == difficulty:
                topic_match = any(topic in challenge.topics for topic in topics)
                if topic_match:
                    filtered_challenges.append(challenge)
        
        return filtered_challenges
    
    async def get_personalized_learning_path(self, 
                                           user_progress: UserProgress,
                                           consciousness_level: float) -> List[Challenge]:
        """Get personalized learning path based on progress and consciousness"""
        
        # Get challenges appropriate for consciousness level
        available_challenges = await self.get_challenges_by_consciousness_level(consciousness_level)
        
        # Filter out already completed challenges
        uncompleted_challenges = [
            challenge for challenge in available_challenges
            if challenge.id not in user_progress.completed_challenges
        ]
        
        # Sort by consciousness requirement and completion rate
        learning_path = sorted(
            uncompleted_challenges,
            key=lambda c: (c.consciousness_requirement, -c.completion_rate)
        )
        
        # Focus on areas for improvement
        improvement_challenges = [
            challenge for challenge in learning_path
            if any(area in challenge.topics for area in user_progress.areas_for_improvement)
        ]
        
        # Combine improvement areas with general progression
        personalized_path = improvement_challenges[:3] + learning_path[:5]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_path = []
        for challenge in personalized_path:
            if challenge.id not in seen:
                unique_path.append(challenge)
                seen.add(challenge.id)
        
        logger.info(f"🎯 Generated personalized path with {len(unique_path)} challenges")
        return unique_path[:8]  # Return top 8 recommendations
    
    def _is_cached(self, key: str) -> bool:
        """Check if data is cached and still valid"""
        if key not in self.cache:
            return False
        
        cache_time = self.cache[key]["timestamp"]
        return (time.time() - cache_time) < self.cache_ttl
    
    def _cache_data(self, key: str, data: Any):
        """Cache data with timestamp"""
        self.cache[key] = {
            "data": data,
            "timestamp": time.time()
        }
    
    def set_consciousness_tracker(self, tracker):
        """Set consciousness tracker for integration"""
        self.consciousness_tracker = tracker
        logger.info("🧠 Consciousness tracker connected to FreeCodeCamp client")
    
    async def track_challenge_completion(self, user: str, challenge_id: str, consciousness_level: float):
        """Track challenge completion for consciousness analysis"""
        if self.consciousness_tracker:
            await self.consciousness_tracker.record_learning_event({
                "type": "challenge_completion",
                "user": user,
                "challenge_id": challenge_id,
                "consciousness_level": consciousness_level,
                "timestamp": time.time()
            })
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.cache),
            "cache_ttl": self.cache_ttl,
            "cached_keys": list(self.cache.keys())
        }

# Global client instance
_global_fcc_client: Optional[FreeCodeCampClient] = None

async def initialize_freecodecamp_client() -> FreeCodeCampClient:
    """Initialize global FreeCodeCamp client"""
    global _global_fcc_client
    _global_fcc_client = FreeCodeCampClient()
    await _global_fcc_client.initialize()
    
    logger.info("🎓 Global FreeCodeCamp client initialized")
    return _global_fcc_client

def get_freecodecamp_client() -> Optional[FreeCodeCampClient]:
    """Get global FreeCodeCamp client instance"""
    return _global_fcc_client

# Convenience functions
async def get_user_learning_recommendations(username: str, consciousness_level: float) -> Dict[str, Any]:
    """Get comprehensive learning recommendations for a user"""
    client = get_freecodecamp_client()
    if not client:
        raise Exception("FreeCodeCamp client not initialized")
    
    # Get user progress
    progress = await client.get_user_progress(username)
    if not progress:
        return {"error": "User not found or API unavailable"}
    
    # Get personalized learning path
    learning_path = await client.get_personalized_learning_path(progress, consciousness_level)
    
    # Get challenges by consciousness level
    consciousness_challenges = await client.get_challenges_by_consciousness_level(consciousness_level)
    
    return {
        "user_progress": progress,
        "personalized_path": learning_path,
        "consciousness_appropriate_challenges": consciousness_challenges,
        "recommendations": {
            "next_challenge": learning_path[0] if learning_path else None,
            "focus_areas": progress.areas_for_improvement,
            "strengths": progress.strengths,
            "consciousness_level": consciousness_level
        }
    }

if __name__ == "__main__":
    # Test the FreeCodeCamp client
    async def test_freecodecamp_client():
        client = await initialize_freecodecamp_client()
        
        # Test with a sample user
        test_username = "freecodecamp"  # Official FCC account
        test_consciousness = 0.5
        
        print(f"🧪 Testing FreeCodeCamp integration...")
        
        # Get user progress
        progress = await client.get_user_progress(test_username)
        if progress:
            print(f"✅ User Progress:")
            print(f"   Username: {progress.username}")
            print(f"   Completed: {len(progress.completed_challenges)} challenges")
            print(f"   Points: {progress.total_points}")
            print(f"   Consciousness: {progress.consciousness_level:.2f}")
            print(f"   Strengths: {progress.strengths}")
            print(f"   Improvements: {progress.areas_for_improvement}")
        
        # Get challenges by consciousness level
        challenges = await client.get_challenges_by_consciousness_level(test_consciousness)
        print(f"\n📚 Challenges for consciousness level {test_consciousness}:")
        for challenge in challenges[:3]:
            print(f"   • {challenge.title} ({challenge.difficulty.value})")
            print(f"     Topics: {', '.join(challenge.topics)}")
            print(f"     Time: {challenge.estimated_time}min")
        
        # Get personalized learning path
        if progress:
            learning_path = await client.get_personalized_learning_path(progress, test_consciousness)
            print(f"\n🎯 Personalized Learning Path:")
            for i, challenge in enumerate(learning_path[:5], 1):
                print(f"   {i}. {challenge.title}")
                print(f"      Difficulty: {challenge.difficulty.value}")
                print(f"      Consciousness Req: {challenge.consciousness_requirement:.1f}")
        
        # Get cache stats
        cache_stats = client.get_cache_stats()
        print(f"\n💾 Cache Stats: {cache_stats}")
        
        await client.close()
        print("\n✅ FreeCodeCamp client test completed!")
    
    asyncio.run(test_freecodecamp_client())
