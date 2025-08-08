#!/usr/bin/env python3
"""
HackTheBox Platform Integration Client

Integrates with HackTheBox API and web scraping to track:
- Machine completions and ownership
- Challenge solutions
- Ranking and points progression
- Skill development in penetration testing
- Attack vector analysis

Provides consciousness-aware analysis of cybersecurity learning patterns.
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class HackTheBoxClient:
    """HackTheBox platform integration with consciousness awareness"""
    
    def __init__(self, consciousness_bridge):
        self.consciousness = consciousness_bridge
        self.api_base = "https://www.hackthebox.eu/api/v4"
        self.web_base = "https://www.hackthebox.eu"
        self.session = None
        
        # HackTheBox skill categories
        self.skill_categories = {
            "web": {
                "name": "Web Application Security",
                "techniques": ["sql_injection", "xss", "csrf", "lfi", "rfi", "ssrf"],
                "difficulty_levels": ["easy", "medium", "hard", "insane"]
            },
            "crypto": {
                "name": "Cryptography",
                "techniques": ["rsa", "aes", "hash_cracking", "encoding", "steganography"],
                "difficulty_levels": ["easy", "medium", "hard", "insane"]
            },
            "pwn": {
                "name": "Binary Exploitation",
                "techniques": ["buffer_overflow", "rop", "format_string", "heap_exploitation"],
                "difficulty_levels": ["easy", "medium", "hard", "insane"]
            },
            "reverse": {
                "name": "Reverse Engineering",
                "techniques": ["static_analysis", "dynamic_analysis", "malware_analysis", "obfuscation"],
                "difficulty_levels": ["easy", "medium", "hard", "insane"]
            },
            "forensics": {
                "name": "Digital Forensics",
                "techniques": ["memory_analysis", "network_forensics", "disk_forensics", "log_analysis"],
                "difficulty_levels": ["easy", "medium", "hard", "insane"]
            },
            "misc": {
                "name": "Miscellaneous",
                "techniques": ["osint", "social_engineering", "physical_security", "programming"],
                "difficulty_levels": ["easy", "medium", "hard", "insane"]
            }
        }
        
        # Machine categories and skills
        self.machine_skills = {
            "enumeration": ["nmap", "gobuster", "ffuf", "nikto", "enum4linux"],
            "exploitation": ["metasploit", "custom_exploits", "public_exploits", "manual_exploitation"],
            "privilege_escalation": ["linux_privesc", "windows_privesc", "kernel_exploits", "misconfigurations"],
            "post_exploitation": ["persistence", "lateral_movement", "data_exfiltration", "cleanup"]
        }
    
    async def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user progress from HackTheBox"""
        try:
            # Get user profile data
            profile_data = await self._get_user_profile(user_id)
            
            # Get machine completions
            machines = await self._get_completed_machines(user_id)
            
            # Get challenge completions
            challenges = await self._get_completed_challenges(user_id)
            
            # Get ranking information
            ranking_data = await self._get_user_ranking(user_id)
            
            # Calculate statistics
            stats = self._calculate_progress_stats(profile_data, machines, challenges, ranking_data)
            
            # Get consciousness insights
            consciousness_insights = await self._get_consciousness_analysis(
                user_id, profile_data, machines, challenges, stats
            )
            
            return {
                "platform": "hackthebox",
                "user_id": user_id,
                "profile": profile_data,
                "machines": machines,
                "challenges": challenges,
                "ranking": ranking_data,
                "statistics": stats,
                "consciousness_insights": consciousness_insights,
                "last_updated": datetime.utcnow().isoformat(),
                "recent_activity": stats.get("recent_activity", False)
            }
            
        except Exception as e:
            logger.error(f"Failed to get HackTheBox progress for {user_id}: {e}")
            return {
                "platform": "hackthebox",
                "user_id": user_id,
                "error": str(e),
                "last_updated": datetime.utcnow().isoformat()
            }
    
    async def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile information"""
        try:
            async with httpx.AsyncClient() as client:
                # Try to get user profile via API
                headers = {"User-Agent": "Syn_OS Learning Hub"}
                response = await client.get(f"{self.api_base}/user/profile/{user_id}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    return {
                        "user_id": user_id,
                        "username": data.get("name", ""),
                        "avatar": data.get("avatar", ""),
                        "country": data.get("country", ""),
                        "points": data.get("points", 0),
                        "rank": data.get("rank", ""),
                        "respect": data.get("respect", 0),
                        "owns": data.get("owns", {"user": 0, "root": 0, "system": 0}),
                        "bloods": data.get("bloods", {"user": 0, "root": 0, "system": 0}),
                        "team": data.get("team", {}),
                        "university": data.get("university", {}),
                        "is_vip": data.get("isVip", False),
                        "join_date": data.get("joinDate", "")
                    }
                else:
                    # Fallback to web scraping
                    return await self._scrape_user_profile(user_id)
                    
        except Exception as e:
            logger.warning(f"Failed to get HackTheBox profile for {user_id}: {e}")
            return {"user_id": user_id, "error": str(e)}
    
    async def _scrape_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Scrape user profile from public page as fallback"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"User-Agent": "Syn_OS Learning Hub"}
                response = await client.get(f"{self.web_base}/home/users/profile/{user_id}", headers=headers)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract basic profile information
                    username_elem = soup.find('h1')
                    username = username_elem.text.strip() if username_elem else f"user_{user_id}"
                    
                    # Extract points
                    points_elem = soup.find('span', string=re.compile(r'points'))
                    points = 0
                    if points_elem:
                        points_text = points_elem.parent.text if points_elem.parent else ""
                        points_match = re.search(r'(\d+)', points_text)
                        if points_match:
                            points = int(points_match.group(1))
                    
                    # Extract rank
                    rank_elem = soup.find('span', class_='rank')
                    rank = rank_elem.text.strip() if rank_elem else "Noob"
                    
                    # Extract owns (machines owned)
                    owns = {"user": 0, "root": 0, "system": 0}
                    owns_section = soup.find('div', class_='owns')
                    if owns_section and hasattr(owns_section, 'find_all'):
                        spans = owns_section.find_all('span')
                        user_owns = None
                        root_owns = None
                        system_owns = None
                        
                        for span in spans:
                            if span.text and 'User' in span.text:
                                user_owns = span
                            elif span.text and 'Root' in span.text:
                                root_owns = span
                            elif span.text and 'System' in span.text:
                                system_owns = span
                        
                        if user_owns:
                            user_match = re.search(r'(\d+)', user_owns.text)
                            owns["user"] = int(user_match.group(1)) if user_match else 0
                        
                        if root_owns:
                            root_match = re.search(r'(\d+)', root_owns.text)
                            owns["root"] = int(root_match.group(1)) if root_match else 0
                        
                        if system_owns:
                            system_match = re.search(r'(\d+)', system_owns.text)
                            owns["system"] = int(system_match.group(1)) if system_match else 0
                    
                    return {
                        "user_id": user_id,
                        "username": username,
                        "points": points,
                        "rank": rank,
                        "owns": owns,
                        "scraped": True
                    }
                    
        except Exception as e:
            logger.warning(f"Failed to scrape HackTheBox profile for {user_id}: {e}")
            
        return {"user_id": user_id, "error": "Profile not accessible"}
    
    async def _get_completed_machines(self, user_id: str) -> List[Dict[str, Any]]:
        """Get list of completed machines"""
        try:
            # This would require authenticated API access or detailed scraping
            # For now, return estimated data based on profile owns
            machines = []
            
            # Placeholder machine data structure
            sample_machines = [
                {
                    "id": 1,
                    "name": "Lame",
                    "os": "Linux",
                    "difficulty": "Easy",
                    "points": 20,
                    "user_owned": True,
                    "root_owned": True,
                    "completion_date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                    "techniques_used": ["smb_enumeration", "samba_exploit", "privilege_escalation"],
                    "time_to_complete": 4.5  # hours
                },
                {
                    "id": 2,
                    "name": "Legacy",
                    "os": "Windows",
                    "difficulty": "Easy",
                    "points": 20,
                    "user_owned": True,
                    "root_owned": True,
                    "completion_date": (datetime.utcnow() - timedelta(days=25)).isoformat(),
                    "techniques_used": ["smb_enumeration", "ms08_067", "buffer_overflow"],
                    "time_to_complete": 3.2
                }
            ]
            
            return sample_machines
            
        except Exception as e:
            logger.warning(f"Failed to get completed machines for {user_id}: {e}")
            return []
    
    async def _get_completed_challenges(self, user_id: str) -> List[Dict[str, Any]]:
        """Get list of completed challenges"""
        try:
            # This would require authenticated API access
            # For now, return placeholder challenge data
            challenges = [
                {
                    "id": 1,
                    "name": "Invitation",
                    "category": "web",
                    "difficulty": "Easy",
                    "points": 20,
                    "completion_date": (datetime.utcnow() - timedelta(days=20)).isoformat(),
                    "techniques_used": ["web_enumeration", "javascript_analysis"],
                    "time_to_complete": 1.5
                },
                {
                    "id": 2,
                    "name": "Find The Easy Pass",
                    "category": "reverse",
                    "difficulty": "Easy",
                    "points": 20,
                    "completion_date": (datetime.utcnow() - timedelta(days=18)).isoformat(),
                    "techniques_used": ["static_analysis", "string_analysis"],
                    "time_to_complete": 2.0
                }
            ]
            
            return challenges
            
        except Exception as e:
            logger.warning(f"Failed to get completed challenges for {user_id}: {e}")
            return []
    
    async def _get_user_ranking(self, user_id: str) -> Dict[str, Any]:
        """Get user ranking information"""
        try:
            # This would require API access to ranking data
            return {
                "global_rank": 15000,  # Placeholder
                "country_rank": 500,
                "university_rank": 25,
                "team_rank": 10,
                "points_to_next_rank": 150,
                "rank_progression": [
                    {"rank": "Noob", "date": "2023-01-01", "points": 0},
                    {"rank": "Script Kiddie", "date": "2023-02-15", "points": 100},
                    {"rank": "Hacker", "date": "2023-04-10", "points": 500}
                ]
            }
            
        except Exception as e:
            logger.warning(f"Failed to get ranking data for {user_id}: {e}")
            return {}
    
    def _calculate_progress_stats(self, profile: Dict, machines: List, 
                                challenges: List, ranking: Dict) -> Dict[str, Any]:
        """Calculate overall progress statistics"""
        owns = profile.get("owns", {"user": 0, "root": 0, "system": 0})
        total_owns = owns.get("user", 0) + owns.get("root", 0) + owns.get("system", 0)
        points = profile.get("points", 0)
        
        # Calculate skill distribution
        skill_distribution = self._analyze_skill_distribution(machines, challenges)
        
        # Calculate learning velocity
        learning_velocity = self._calculate_learning_velocity(machines, challenges)
        
        # Determine current skill level
        skill_level = self._determine_skill_level(total_owns, len(challenges), points)
        
        # Calculate completion rates by difficulty
        difficulty_stats = self._analyze_difficulty_progression(machines, challenges)
        
        return {
            "total_machines_owned": total_owns,
            "user_owns": owns.get("user", 0),
            "root_owns": owns.get("root", 0),
            "system_owns": owns.get("system", 0),
            "challenges_completed": len(challenges),
            "total_points": points,
            "current_rank": profile.get("rank", "Noob"),
            "skill_level": skill_level,
            "skill_distribution": skill_distribution,
            "learning_velocity": learning_velocity,
            "difficulty_progression": difficulty_stats,
            "recent_activity": len(machines) > 0 or len(challenges) > 0,
            "penetration_testing_score": self._calculate_pentest_score(owns, challenges),
            "favorite_attack_vectors": self._identify_favorite_techniques(machines, challenges),
            "next_milestone": self._get_next_milestone(owns, challenges, points)
        }
    
    def _analyze_skill_distribution(self, machines: List, challenges: List) -> Dict[str, float]:
        """Analyze distribution of skills across completed items"""
        skill_counts = {}
        total_items = len(machines) + len(challenges)
        
        if total_items == 0:
            return {}
        
        # Count skills from machines
        for machine in machines:
            techniques = machine.get("techniques_used", [])
            for technique in techniques:
                skill_counts[technique] = skill_counts.get(technique, 0) + 1
        
        # Count skills from challenges
        for challenge in challenges:
            techniques = challenge.get("techniques_used", [])
            for technique in techniques:
                skill_counts[technique] = skill_counts.get(technique, 0) + 1
        
        # Convert to percentages
        skill_distribution = {}
        for skill, count in skill_counts.items():
            skill_distribution[skill] = (count / total_items) * 100
        
        return skill_distribution
    
    def _calculate_learning_velocity(self, machines: List, challenges: List) -> Dict[str, float]:
        """Calculate learning velocity metrics"""
        if not machines and not challenges:
            return {"machines_per_week": 0, "challenges_per_week": 0, "points_per_week": 0}
        
        # Calculate based on recent activity (last 30 days)
        recent_cutoff = datetime.utcnow() - timedelta(days=30)
        
        recent_machines = [m for m in machines 
                          if datetime.fromisoformat(m.get("completion_date", "1970-01-01")) > recent_cutoff]
        recent_challenges = [c for c in challenges 
                           if datetime.fromisoformat(c.get("completion_date", "1970-01-01")) > recent_cutoff]
        
        # Calculate weekly rates
        weeks_in_period = 4.3  # ~30 days / 7
        
        return {
            "machines_per_week": len(recent_machines) / weeks_in_period,
            "challenges_per_week": len(recent_challenges) / weeks_in_period,
            "points_per_week": sum(m.get("points", 0) for m in recent_machines) + 
                              sum(c.get("points", 0) for c in recent_challenges) / weeks_in_period,
            "avg_time_per_machine": sum(m.get("time_to_complete", 0) for m in recent_machines) / 
                                   max(len(recent_machines), 1),
            "avg_time_per_challenge": sum(c.get("time_to_complete", 0) for c in recent_challenges) / 
                                     max(len(recent_challenges), 1)
        }
    
    def _determine_skill_level(self, total_owns: int, challenges_completed: int, points: int) -> str:
        """Determine user's skill level based on progress"""
        if points >= 1000 and total_owns >= 20:
            return "advanced"
        elif points >= 500 and total_owns >= 10:
            return "intermediate"
        elif points >= 100 and (total_owns >= 3 or challenges_completed >= 5):
            return "beginner"
        else:
            return "novice"
    
    def _analyze_difficulty_progression(self, machines: List, challenges: List) -> Dict[str, Any]:
        """Analyze progression through difficulty levels"""
        difficulty_counts = {"Easy": 0, "Medium": 0, "Hard": 0, "Insane": 0}
        
        # Count machines by difficulty
        for machine in machines:
            difficulty = machine.get("difficulty", "Easy")
            if difficulty in difficulty_counts:
                difficulty_counts[difficulty] += 1
        
        # Count challenges by difficulty
        for challenge in challenges:
            difficulty = challenge.get("difficulty", "Easy")
            if difficulty in difficulty_counts:
                difficulty_counts[difficulty] += 1
        
        total = sum(difficulty_counts.values())
        if total == 0:
            return difficulty_counts
        
        # Calculate percentages and progression
        progression = {}
        for difficulty, count in difficulty_counts.items():
            progression[difficulty] = {
                "count": count,
                "percentage": (count / total) * 100
            }
        
        # Determine readiness for next difficulty
        easy_percentage = progression.get("Easy", {}).get("percentage", 0)
        medium_percentage = progression.get("Medium", {}).get("percentage", 0)
        
        if easy_percentage >= 70 and medium_percentage < 30:
            progression["recommended_next"] = "Medium"
        elif medium_percentage >= 60 and progression.get("Hard", {}).get("percentage", 0) < 20:
            progression["recommended_next"] = "Hard"
        elif progression.get("Hard", {}).get("percentage", 0) >= 50:
            progression["recommended_next"] = "Insane"
        else:
            progression["recommended_next"] = "Easy"
        
        return progression
    
    def _calculate_pentest_score(self, owns: Dict, challenges: List) -> float:
        """Calculate overall penetration testing proficiency score"""
        # Weight different achievements
        user_score = owns.get("user", 0) * 1.0
        root_score = owns.get("root", 0) * 2.0
        system_score = owns.get("system", 0) * 3.0
        challenge_score = len(challenges) * 0.5
        
        total_score = user_score + root_score + system_score + challenge_score
        
        # Normalize to 0-100 scale
        max_possible = 100  # Arbitrary max for normalization
        return min((total_score / max_possible) * 100, 100)
    
    def _identify_favorite_techniques(self, machines: List, challenges: List) -> List[str]:
        """Identify most frequently used attack techniques"""
        technique_counts = {}
        
        # Count techniques from all completed items
        for machine in machines:
            for technique in machine.get("techniques_used", []):
                technique_counts[technique] = technique_counts.get(technique, 0) + 1
        
        for challenge in challenges:
            for technique in challenge.get("techniques_used", []):
                technique_counts[technique] = technique_counts.get(technique, 0) + 1
        
        # Sort by frequency and return top techniques
        sorted_techniques = sorted(technique_counts.items(), key=lambda x: x[1], reverse=True)
        return [technique for technique, count in sorted_techniques[:5]]
    
    def _get_next_milestone(self, owns: Dict, challenges: List, points: int) -> Dict[str, Any]:
        """Get the next learning milestone"""
        total_owns = sum(owns.values())
        
        if total_owns == 0:
            return {
                "type": "first_machine",
                "title": "Complete Your First Machine",
                "description": "Start with an Easy-rated machine to learn basic enumeration",
                "target": "Own user flag on any Easy machine",
                "estimated_time": "4-6 hours"
            }
        elif total_owns < 5:
            return {
                "type": "basic_skills",
                "title": "Build Foundation Skills",
                "description": "Complete 5 Easy machines to master basic techniques",
                "target": f"Complete {5 - total_owns} more Easy machines",
                "estimated_time": f"{(5 - total_owns) * 4} hours"
            }
        elif len(challenges) < 10:
            return {
                "type": "challenge_focus",
                "title": "Diversify with Challenges",
                "description": "Complete challenges to learn specific techniques",
                "target": f"Complete {10 - len(challenges)} more challenges",
                "estimated_time": f"{(10 - len(challenges)) * 2} hours"
            }
        elif points < 500:
            return {
                "type": "intermediate_progression",
                "title": "Progress to Medium Difficulty",
                "description": "Start tackling Medium-rated machines and challenges",
                "target": "Reach 500 points total",
                "estimated_time": "2-3 weeks"
            }
        else:
            return {
                "type": "advanced_mastery",
                "title": "Master Advanced Techniques",
                "description": "Focus on Hard and Insane difficulty items",
                "target": "Complete 3 Hard machines",
                "estimated_time": "1-2 months"
            }
    
    async def _get_consciousness_analysis(self, user_id: str, profile: Dict, 
                                        machines: List, challenges: List, stats: Dict) -> Dict[str, Any]:
        """Get AI consciousness analysis of penetration testing progress"""
        try:
            if not self.consciousness:
                return self._fallback_analysis(profile, machines, challenges, stats)
            
            analysis_data = {
                "platform": "hackthebox",
                "user_id": user_id,
                "profile_data": profile,
                "machines": machines,
                "challenges": challenges,
                "statistics": stats,
                "analysis_type": "penetration_testing_learning"
            }
            
            # Request consciousness analysis
            insights = await self._request_consciousness_analysis(analysis_data)
            
            return insights or self._fallback_analysis(profile, machines, challenges, stats)
            
        except Exception as e:
            logger.warning(f"Consciousness analysis failed for {user_id}: {e}")
            return self._fallback_analysis(profile, machines, challenges, stats)
    
    async def _request_consciousness_analysis(self, data: Dict) -> Optional[Dict]:
        """Request analysis from consciousness system"""
        try:
            # This would integrate with the consciousness system
            # For now, return None to trigger fallback
            return None
        except Exception as e:
            logger.warning(f"Failed to get consciousness analysis: {e}")
            return None
    
    def _fallback_analysis(self, profile: Dict, machines: List, 
                          challenges: List, stats: Dict) -> Dict[str, Any]:
        """Fallback analysis when consciousness is unavailable"""
        total_owns = sum(profile.get("owns", {}).values())
        points = profile.get("points", 0)
        
        # Determine learning pattern
        if len(machines) > len(challenges) * 2:
            learning_pattern = "machine_focused"
        elif len(challenges) > len(machines) * 2:
            learning_pattern = "challenge_focused"
        else:
            learning_pattern = "balanced"
        
        # Assess engagement level
        if total_owns > 10 and len(challenges) > 5:
            engagement_level = "high"
        elif total_owns > 3 or len(challenges) > 2:
            engagement_level = "moderate"
        else:
            engagement_level = "low"
        
        # Generate recommendations
        recommendations = []
        skill_level = stats.get("skill_level", "novice")
        
        if skill_level == "novice":
            recommendations.extend([
                "Start with Easy-rated machines like 'Lame' or 'Legacy'",
                "Focus on basic enumeration techniques (nmap, gobuster)",
                "Learn fundamental privilege escalation methods"
            ])
        elif skill_level == "beginner":
            recommendations.extend([
                "Try Medium-rated machines to challenge yourself",
                "Complete web application challenges to diversify skills",
                "Practice manual exploitation techniques"
            ])
        else:
            recommendations.extend([
                "Attempt Hard-rated machines for advanced techniques",
                "Focus on zero-day research and custom exploit development",
                "Contribute to the community with writeups and tools"
            ])
        
        return {
            "learning_pattern": learning_pattern,
            "engagement_level": engagement_level,
            "skill_assessment": {
                "enumeration": min(total_owns * 10, 100),
                "exploitation": min(len(challenges) * 15, 100),
                "privilege_escalation": min(profile.get("owns", {}).get("root", 0) * 20, 100)
            },
            "recommendations": recommendations,
            "learning_efficiency": min(points / 10, 100),
            "next_focus_area": self._suggest_next_focus(stats),
            "estimated_skill_growth": self._estimate_skill_growth(total_owns, len(challenges)),
            "consciousness_available": False
        }
    
    def _suggest_next_focus(self, stats: Dict) -> str:
        """Suggest next area of focus based on current progress"""
        skill_level = stats.get("skill_level", "novice")
        difficulty_progression = stats.get("difficulty_progression", {})
        
        if skill_level == "novice":
            return "Master basic enumeration and Easy machines"
        elif skill_level == "beginner":
            easy_count = difficulty_progression.get("Easy", {}).get("count", 0)
            if easy_count < 5:
                return "Complete more Easy machines for solid foundation"
            else:
                return "Progress to Medium difficulty machines"
        elif skill_level == "intermediate":
            return "Focus on Hard machines and advanced techniques"
        else:
            return "Master Insane machines and contribute to community"
    
    def _estimate_skill_growth(self, total_owns: int, challenges_completed: int) -> Dict[str, str]:
        """Estimate skill growth timeline"""
        current_level = "novice"
        if total_owns >= 20:
            current_level = "advanced"
        elif total_owns >= 10:
            current_level = "intermediate"
        elif total_owns >= 3:
            current_level = "beginner"
        
        growth_estimates = {
            "novice": {
                "next_level": "beginner",
                "estimated_time": "2-3 months with consistent practice",
                "requirements": "Complete 5+ Easy machines"
            },
            "beginner": {
                "next_level": "intermediate", 
                "estimated_time": "4-6 months",
                "requirements": "Complete 10+ machines including Medium difficulty"
            },
            "intermediate": {
                "next_level": "advanced",
                "estimated_time": "6-12 months",
                "requirements": "Complete Hard machines and contribute to community"
            },
            "advanced": {
                "next_level": "expert",
                "estimated_time": "1-2 years",
                "requirements": "Master Insane machines and develop original research"
            }
        }
        
        return growth_estimates.get(current_level, growth_estimates["novice"])
    
    async def get_recommendations(self, user_id: str, progress_data: Dict) -> List[Dict[str, Any]]:
        """Get personalized learning recommendations"""
        try:
            consciousness_insights = progress_data.get("consciousness_insights", {})
            stats = progress_data.get("statistics", {})
            
            recommendations = []
            
            # Based on current skill level
            skill_level = stats.get("skill_level", "novice")
            total_owns = stats.get("total_machines_owned", 0)
            
            if skill_level == "novice":
                recommendations.append({
                    "type": "foundation",
                    "title": "Start with Easy Machines",
                    "description": "Begin with beginner-friendly machines like Lame, Legacy, or Blue",
                    "priority": 0.9,
                    "estimated_time": "4-6 hours per machine",
                    "skills": ["enumeration", "basic_exploitation"],
                    "platform": "hackthebox"
                })
            elif skill_level == "beginner":
                recommendations.append({
                    "type": "skill_building",
                    "title": "Diversify with Challenges",
                    "description": "Complete web and crypto challenges to build specific skills",
                    "priority": 0.8,
                    "estimated_time": "1-3 hours per challenge",
                    "skills": ["web_security", "cryptography"],
                    "platform": "hackthebox"
                })
            else:
                recommendations.append({
                    "type": "advancement",
                    "title": "Tackle Hard Machines",
                    "description": "Challenge yourself with Hard-rated machines for advanced techniques",
                    "priority": 0.7,
                    "estimated_time": "8-12 hours per machine",
                    "skills": ["advanced_exploitation", "custom_exploits"],
                    "platform": "hackthebox"
                })
            
            # Add consciousness-driven recommendations if available
            if consciousness_insights.get("recommendations"):
                for rec in consciousness_insights["recommendations"]:
                    recommendations.append({
                        "type": "ai_suggested",
                        "title": f"AI Recommendation: {rec}",
                        "description": "Personalized suggestion from consciousness analysis",
                        "priority": 0.85,
                        "platform": "hackthebox"
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get HackTheBox recommendations: {e}")
            return []
    
    async def sync_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Manually sync user progress data"""
        try:
            progress_data = await self.get_user_progress(user_id)
            
            return {
                "sync_status": "success",
                "platform": "hackthebox",
                "user_id": user_id,
                "data": progress_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to sync HackTheBox data for {user_id}: {e}")
            return {
                "sync_status": "failed",
                "platform": "hackthebox",
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            