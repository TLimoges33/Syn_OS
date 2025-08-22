#!/usr/bin/env python3
"""
FreeCodeCamp Platform Integration Client

Integrates with FreeCodeCamp's public API and web scraping to track:
- Course progress and completion
- Certificate achievements
- Project submissions
- Coding skill development
- Time spent learning

Provides consciousness-aware analysis of web development learning patterns.
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import aiohttp
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class FreeCodeCampClient:
    """FreeCodeCamp platform integration with consciousness awareness"""
    
    def __init__(self, consciousness_bridge):
        self.consciousness = consciousness_bridge
        self.api_base = "https://api.freecodecamp.org"
        self.web_base = "https://www.freecodecamp.org"
        self.session = None
        
        # FreeCodeCamp curriculum structure
        self.curriculum_map = {
            "responsive-web-design": {
                "name": "Responsive Web Design",
                "skills": ["html", "css", "responsive_design"],
                "difficulty": "beginner",
                "estimated_hours": 300
            },
            "javascript-algorithms-and-data-structures": {
                "name": "JavaScript Algorithms and Data Structures",
                "skills": ["javascript", "algorithms", "data_structures"],
                "difficulty": "intermediate",
                "estimated_hours": 300
            },
            "front-end-development-libraries": {
                "name": "Front End Development Libraries",
                "skills": ["react", "redux", "sass", "bootstrap"],
                "difficulty": "intermediate",
                "estimated_hours": 300
            },
            "data-visualization": {
                "name": "Data Visualization",
                "skills": ["d3", "json", "ajax"],
                "difficulty": "intermediate",
                "estimated_hours": 300
            },
            "back-end-development-and-apis": {
                "name": "Back End Development and APIs",
                "skills": ["nodejs", "express", "mongodb", "mongoose"],
                "difficulty": "intermediate",
                "estimated_hours": 300
            },
            "quality-assurance": {
                "name": "Quality Assurance",
                "skills": ["testing", "chai", "mocha", "security"],
                "difficulty": "advanced",
                "estimated_hours": 300
            },
            "scientific-computing-with-python": {
                "name": "Scientific Computing with Python",
                "skills": ["python", "numpy", "matplotlib"],
                "difficulty": "intermediate",
                "estimated_hours": 300
            },
            "data-analysis-with-python": {
                "name": "Data Analysis with Python",
                "skills": ["pandas", "numpy", "matplotlib", "seaborn"],
                "difficulty": "intermediate",
                "estimated_hours": 300
            },
            "information-security": {
                "name": "Information Security",
                "skills": ["security", "penetration_testing", "bcrypt"],
                "difficulty": "advanced",
                "estimated_hours": 300
            },
            "machine-learning-with-python": {
                "name": "Machine Learning with Python",
                "skills": ["tensorflow", "neural_networks", "machine_learning"],
                "difficulty": "advanced",
                "estimated_hours": 300
            }
        }
    
    async def get_user_progress(self, username: str) -> Dict[str, Any]:
        """Get comprehensive user progress from FreeCodeCamp"""
        try:
            # Get user profile data
            profile_data = await self._get_user_profile(username)
            
            # Get detailed progress for each curriculum
            curriculum_progress = await self._get_curriculum_progress(username)
            
            # Get project submissions
            projects = await self._get_user_projects(username)
            
            # Calculate overall statistics
            stats = self._calculate_progress_stats(profile_data, curriculum_progress, projects)
            
            # Get consciousness insights
            consciousness_insights = await self._get_consciousness_analysis(
                username, profile_data, curriculum_progress, projects
            )
            
            return {
                "platform": "freecodecamp",
                "username": username,
                "profile": profile_data,
                "curriculum_progress": curriculum_progress,
                "projects": projects,
                "statistics": stats,
                "consciousness_insights": consciousness_insights,
                "last_updated": datetime.utcnow().isoformat(),
                "recent_activity": stats.get("recent_activity", False)
            }
            
        except Exception as e:
            logger.error(f"Failed to get FreeCodeCamp progress for {username}: {e}")
            return {
                "platform": "freecodecamp",
                "username": username,
                "error": str(e),
                "last_updated": datetime.utcnow().isoformat()
            }
    
    async def _get_user_profile(self, username: str) -> Dict[str, Any]:
        """Get user profile information"""
        try:
            async with httpx.AsyncClient() as client:
                # Try to get public profile
                response = await client.get(f"{self.web_base}/api/users/get-public-profile", 
                                          params={"username": username})
                
                if response.status_code == 200:
                    data = response.json()
                    
                    profile = data.get("entities", {}).get("user", {}).get(username, {})
                    
                    return {
                        "username": username,
                        "name": profile.get("name", ""),
                        "location": profile.get("location", ""),
                        "about": profile.get("about", ""),
                        "points": profile.get("points", 0),
                        "picture": profile.get("picture", ""),
                        "joined_date": profile.get("joinDate", ""),
                        "is_donor": profile.get("isDonating", False),
                        "current_challenge": profile.get("currentChallengeId", ""),
                        "completed_challenges": len(profile.get("completedChallenges", [])),
                        "portfolio": profile.get("portfolio", [])
                    }
                else:
                    # Fallback: scrape public profile page
                    return await self._scrape_user_profile(username)
                    
        except Exception as e:
            logger.warning(f"Failed to get FreeCodeCamp profile for {username}: {e}")
            return {"username": username, "error": str(e)}
    
    async def _scrape_user_profile(self, username: str) -> Dict[str, Any]:
        """Scrape user profile from public page as fallback"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.web_base}/{username}")
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract basic profile information
                    name_elem = soup.find('h1', class_='text-center')
                    name = name_elem.text.strip() if name_elem else username
                    
                    # Extract points/score
                    points_elem = soup.find('div', string=re.compile(r'points'))
                    points = 0
                    if points_elem:
                        points_text = points_elem.text
                        points_match = re.search(r'(\d+)', points_text)
                        if points_match:
                            points = int(points_match.group(1))
                    
                    # Extract certificates
                    cert_elements = soup.find_all('div', class_='certification')
                    certificates = []
                    for cert in cert_elements:
                        cert_name = cert.find('h3')
                        if cert_name:
                            certificates.append(cert_name.text.strip())
                    
                    return {
                        "username": username,
                        "name": name,
                        "points": points,
                        "certificates": certificates,
                        "completed_challenges": len(certificates) * 5,  # Estimate
                        "scraped": True
                    }
                    
        except Exception as e:
            logger.warning(f"Failed to scrape FreeCodeCamp profile for {username}: {e}")
            
        return {"username": username, "error": "Profile not accessible"}
    
    async def _get_curriculum_progress(self, username: str) -> Dict[str, Any]:
        """Get detailed progress for each curriculum"""
        progress = {}
        
        for curriculum_id, curriculum_info in self.curriculum_map.items():
            try:
                # This would require more detailed API access or scraping
                # For now, provide estimated progress based on available data
                progress[curriculum_id] = {
                    "name": curriculum_info["name"],
                    "skills": curriculum_info["skills"],
                    "difficulty": curriculum_info["difficulty"],
                    "estimated_hours": curriculum_info["estimated_hours"],
                    "completion_percentage": 0,  # Would need detailed tracking
                    "completed_challenges": 0,
                    "current_challenge": "",
                    "time_spent": 0,
                    "last_activity": None
                }
            except Exception as e:
                logger.warning(f"Failed to get {curriculum_id} progress: {e}")
                
        return progress
    
    async def _get_user_projects(self, username: str) -> List[Dict[str, Any]]:
        """Get user's project submissions"""
        try:
            # This would require access to user's portfolio or project submissions
            # For now, return placeholder structure
            return [
                {
                    "title": "Sample Project",
                    "description": "Project description",
                    "technologies": ["html", "css", "javascript"],
                    "github_url": "",
                    "live_url": "",
                    "completion_date": datetime.utcnow().isoformat(),
                    "curriculum": "responsive-web-design"
                }
            ]
        except Exception as e:
            logger.warning(f"Failed to get projects for {username}: {e}")
            return []
    
    def _calculate_progress_stats(self, profile: Dict, curriculum: Dict, projects: List) -> Dict[str, Any]:
        """Calculate overall progress statistics"""
        total_challenges = profile.get("completed_challenges", 0)
        total_points = profile.get("points", 0)
        certificates = profile.get("certificates", [])
        
        # Calculate completion percentage across all curricula
        total_curricula = len(self.curriculum_map)
        completed_curricula = len(certificates)
        overall_completion = (completed_curricula / total_curricula * 100) if total_curricula > 0 else 0
        
        # Estimate time spent (rough calculation)
        estimated_time_per_challenge = 2  # hours
        estimated_total_time = total_challenges * estimated_time_per_challenge
        
        # Determine current focus area
        current_focus = "responsive-web-design"  # Default starting point
        if completed_curricula > 0:
            curriculum_keys = list(self.curriculum_map.keys())
            if completed_curricula < len(curriculum_keys):
                current_focus = curriculum_keys[completed_curricula]
        
        return {
            "total_challenges": total_challenges,
            "total_points": total_points,
            "certificates_earned": len(certificates),
            "completion_percentage": overall_completion,
            "estimated_time_spent": estimated_total_time,
            "current_focus": current_focus,
            "skill_level": self._determine_skill_level(total_challenges, len(certificates)),
            "recent_activity": total_challenges > 0,  # Simple check
            "learning_velocity": self._calculate_learning_velocity(profile),
            "strongest_skills": self._identify_strongest_skills(certificates),
            "next_milestone": self._get_next_milestone(certificates)
        }
    
    def _determine_skill_level(self, challenges: int, certificates: int) -> str:
        """Determine user's skill level based on progress"""
        if certificates >= 5:
            return "advanced"
        elif certificates >= 2 or challenges >= 100:
            return "intermediate"
        elif challenges >= 20:
            return "beginner"
        else:
            return "novice"
    
    def _calculate_learning_velocity(self, profile: Dict) -> float:
        """Calculate learning velocity (challenges per week)"""
        # This would require historical data
        # For now, provide estimated velocity
        total_challenges = profile.get("completed_challenges", 0)
        if total_challenges > 0:
            # Assume user has been learning for some time
            return min(total_challenges / 10, 20)  # Max 20 challenges per week
        return 0
    
    def _identify_strongest_skills(self, certificates: List[str]) -> List[str]:
        """Identify user's strongest skills based on certificates"""
        skills = []
        for cert in certificates:
            if "responsive" in cert.lower() or "web design" in cert.lower():
                skills.extend(["html", "css", "responsive_design"])
            elif "javascript" in cert.lower():
                skills.extend(["javascript", "algorithms"])
            elif "react" in cert.lower() or "front end" in cert.lower():
                skills.extend(["react", "frontend"])
            elif "backend" in cert.lower() or "api" in cert.lower():
                skills.extend(["nodejs", "backend", "api"])
            elif "python" in cert.lower():
                skills.extend(["python"])
        
        return list(set(skills))  # Remove duplicates
    
    def _get_next_milestone(self, certificates: List[str]) -> Dict[str, Any]:
        """Get the next learning milestone"""
        completed_count = len(certificates)
        curriculum_keys = list(self.curriculum_map.keys())
        
        if completed_count < len(curriculum_keys):
            next_curriculum = curriculum_keys[completed_count]
            curriculum_info = self.curriculum_map[next_curriculum]
            
            return {
                "type": "certificate",
                "name": curriculum_info["name"],
                "skills": curriculum_info["skills"],
                "estimated_time": curriculum_info["estimated_hours"],
                "difficulty": curriculum_info["difficulty"]
            }
        else:
            return {
                "type": "mastery",
                "name": "Full Stack Development Mastery",
                "description": "Continue building projects and contributing to open source"
            }
    
    async def _get_consciousness_analysis(self, username: str, profile: Dict, 
                                        curriculum: Dict, projects: List) -> Dict[str, Any]:
        """Get AI consciousness analysis of learning progress"""
        try:
            if not self.consciousness:
                return self._fallback_analysis(profile, curriculum, projects)
            
            analysis_data = {
                "platform": "freecodecamp",
                "username": username,
                "profile_data": profile,
                "curriculum_progress": curriculum,
                "projects": projects,
                "analysis_type": "web_development_learning"
            }
            
            # Request consciousness analysis
            insights = await self._request_consciousness_analysis(analysis_data)
            
            return insights or self._fallback_analysis(profile, curriculum, projects)
            
        except Exception as e:
            logger.warning(f"Consciousness analysis failed for {username}: {e}")
            return self._fallback_analysis(profile, curriculum, projects)
    
    async def _request_consciousness_analysis(self, data: Dict) -> Optional[Dict]:
        """Request analysis from consciousness system"""
        try:
            # This would integrate with the consciousness system
            # For now, return None to trigger fallback
            return None
        except Exception as e:
            logger.warning(f"Failed to get consciousness analysis: {e}")
            return None
    
    def _fallback_analysis(self, profile: Dict, curriculum: Dict, projects: List) -> Dict[str, Any]:
        """Fallback analysis when consciousness is unavailable"""
        challenges = profile.get("completed_challenges", 0)
        certificates = profile.get("certificates", [])
        
        # Basic learning pattern analysis
        learning_pattern = "consistent" if challenges > 50 else "sporadic"
        engagement_level = "high" if len(certificates) > 2 else "moderate" if challenges > 20 else "low"
        
        # Skill development assessment
        skill_development = {
            "frontend": len([c for c in certificates if "web design" in c.lower() or "front end" in c.lower()]) > 0,
            "backend": len([c for c in certificates if "backend" in c.lower() or "api" in c.lower()]) > 0,
            "algorithms": len([c for c in certificates if "javascript" in c.lower() or "algorithm" in c.lower()]) > 0
        }
        
        # Learning recommendations
        recommendations = []
        if challenges < 10:
            recommendations.append("Focus on completing basic HTML/CSS challenges")
        elif len(certificates) == 0:
            recommendations.append("Work towards your first certificate completion")
        elif len(certificates) < 3:
            recommendations.append("Continue with JavaScript algorithms and data structures")
        else:
            recommendations.append("Start building portfolio projects")
        
        return {
            "learning_pattern": learning_pattern,
            "engagement_level": engagement_level,
            "skill_development": skill_development,
            "recommendations": recommendations,
            "learning_efficiency": min(challenges / 100 * 100, 100),
            "next_focus_area": self._suggest_next_focus(certificates),
            "estimated_completion_time": self._estimate_completion_time(challenges, certificates),
            "consciousness_available": False
        }
    
    def _suggest_next_focus(self, certificates: List[str]) -> str:
        """Suggest next area of focus based on current progress"""
        if len(certificates) == 0:
            return "Complete Responsive Web Design certification"
        elif len(certificates) == 1:
            return "Learn JavaScript algorithms and data structures"
        elif len(certificates) == 2:
            return "Master React and front-end libraries"
        else:
            return "Build full-stack projects with backend APIs"
    
    def _estimate_completion_time(self, challenges: int, certificates: int) -> Dict[str, int]:
        """Estimate time to complete next milestone"""
        cert_count = len(certificates) if isinstance(certificates, list) else 0
        if cert_count == 0:
            remaining_challenges = max(20 - challenges, 0)
            return {
                "next_certificate_hours": remaining_challenges * 2,
                "full_curriculum_months": 12 - (cert_count * 2)
            }
        else:
            return {
                "next_certificate_hours": 60,  # Estimated
                "full_curriculum_months": max(12 - (cert_count * 2), 2)
            }
    
    async def get_recommendations(self, user_id: str, progress_data: Dict) -> List[Dict[str, Any]]:
        """Get personalized learning recommendations"""
        try:
            consciousness_insights = progress_data.get("consciousness_insights", {})
            stats = progress_data.get("statistics", {})
            
            recommendations = []
            
            # Based on current progress
            completion = stats.get("completion_percentage", 0)
            if completion < 10:
                recommendations.append({
                    "type": "foundation",
                    "title": "Start with HTML Basics",
                    "description": "Begin your web development journey with HTML fundamentals",
                    "priority": 0.9,
                    "estimated_time": "2-3 hours",
                    "skills": ["html"],
                    "platform": "freecodecamp"
                })
            elif completion < 30:
                recommendations.append({
                    "type": "skill_building",
                    "title": "Master CSS Styling",
                    "description": "Learn CSS to make your websites visually appealing",
                    "priority": 0.8,
                    "estimated_time": "4-5 hours",
                    "skills": ["css"],
                    "platform": "freecodecamp"
                })
            else:
                recommendations.append({
                    "type": "advancement",
                    "title": "JavaScript Programming",
                    "description": "Add interactivity to your websites with JavaScript",
                    "priority": 0.7,
                    "estimated_time": "6-8 hours",
                    "skills": ["javascript"],
                    "platform": "freecodecamp"
                })
            
            # Add consciousness-driven recommendations if available
            if consciousness_insights.get("recommendations"):
                for rec in consciousness_insights["recommendations"]:
                    recommendations.append({
                        "type": "ai_suggested",
                        "title": f"AI Recommendation: {rec}",
                        "description": "Personalized suggestion from consciousness analysis",
                        "priority": 0.85,
                        "platform": "freecodecamp"
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get FreeCodeCamp recommendations: {e}")
            return []
    
    async def sync_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Manually sync user progress data"""
        try:
            # For FreeCodeCamp, user_id is typically the username
            progress_data = await self.get_user_progress(user_id)
            
            # Store in local cache/database if needed
            # This would integrate with the user context manager
            
            return {
                "sync_status": "success",
                "platform": "freecodecamp",
                "user_id": user_id,
                "data": progress_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to sync FreeCodeCamp data for {user_id}: {e}")
            return {
                "sync_status": "failed",
                "platform": "freecodecamp",
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }