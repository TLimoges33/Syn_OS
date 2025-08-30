#!/usr/bin/env python3
"""
LeetCode Platform Integration Client

Integrates with LeetCode's GraphQL API to track:
- Problem solving progress
- Contest participation
- Skill ratings and rankings
- Algorithm and data structure proficiency
- Coding interview preparation

Provides consciousness-aware analysis of algorithmic thinking patterns.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import httpx

logger = logging.getLogger(__name__)

class LeetCodeClient:
    """LeetCode platform integration with consciousness awareness"""
    
    def __init__(self, consciousness_bridge):
        self.consciousness = consciousness_bridge
        self.graphql_endpoint = "https://leetcode.com/graphql"
        self.api_base = "https://leetcode.com/api"
        
        # LeetCode problem categories
        self.problem_categories = {
            "array": {"name": "Array", "difficulty_weight": 1.0},
            "string": {"name": "String", "difficulty_weight": 1.0},
            "hash-table": {"name": "Hash Table", "difficulty_weight": 1.2},
            "dynamic-programming": {"name": "Dynamic Programming", "difficulty_weight": 2.0},
            "math": {"name": "Math", "difficulty_weight": 1.1},
            "tree": {"name": "Tree", "difficulty_weight": 1.5},
            "depth-first-search": {"name": "Depth-First Search", "difficulty_weight": 1.6},
            "binary-search": {"name": "Binary Search", "difficulty_weight": 1.4},
            "greedy": {"name": "Greedy", "difficulty_weight": 1.7},
            "breadth-first-search": {"name": "Breadth-First Search", "difficulty_weight": 1.6},
            "two-pointers": {"name": "Two Pointers", "difficulty_weight": 1.3},
            "graph": {"name": "Graph", "difficulty_weight": 1.8},
            "backtracking": {"name": "Backtracking", "difficulty_weight": 1.9},
            "linked-list": {"name": "Linked List", "difficulty_weight": 1.2}
        }
        
        # Difficulty levels
        self.difficulty_levels = {
            "Easy": {"points": 1, "weight": 1.0},
            "Medium": {"points": 2, "weight": 1.5},
            "Hard": {"points": 3, "weight": 2.0}
        }
    
    async def get_user_progress(self, username: str) -> Dict[str, Any]:
        """Get comprehensive user progress from LeetCode"""
        try:
            # Get user profile data
            profile_data = await self._get_user_profile(username)
            
            # Get problem solving statistics
            problem_stats = await self._get_problem_statistics(username)
            
            # Get contest history
            contest_history = await self._get_contest_history(username)
            
            # Get recent submissions
            recent_submissions = await self._get_recent_submissions(username)
            
            # Calculate overall statistics
            stats = self._calculate_progress_stats(profile_data, problem_stats, contest_history, recent_submissions)
            
            # Get consciousness insights
            consciousness_insights = await self._get_consciousness_analysis(
                username, profile_data, problem_stats, contest_history, stats
            )
            
            return {
                "platform": "leetcode",
                "username": username,
                "profile": profile_data,
                "problem_statistics": problem_stats,
                "contest_history": contest_history,
                "recent_submissions": recent_submissions,
                "statistics": stats,
                "consciousness_insights": consciousness_insights,
                "last_updated": datetime.utcnow().isoformat(),
                "recent_activity": stats.get("recent_activity", False)
            }
            
        except Exception as e:
            logger.error(f"Failed to get LeetCode progress for {username}: {e}")
            return {
                "platform": "leetcode",
                "username": username,
                "error": str(e),
                "last_updated": datetime.utcnow().isoformat()
            }
    
    async def _get_user_profile(self, username: str) -> Dict[str, Any]:
        """Get user profile information"""
        try:
            query = """
            query getUserProfile($username: String!) {
                matchedUser(username: $username) {
                    username
                    profile {
                        realName
                        aboutMe
                        userAvatar
                        location
                        websites
                        skillTags
                        ranking
                    }
                    submitStats {
                        acSubmissionNum {
                            difficulty
                            count
                            submissions
                        }
                        totalSubmissionNum {
                            difficulty
                            count
                            submissions
                        }
                    }
                }
            }
            """
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.graphql_endpoint,
                    json={"query": query, "variables": {"username": username}},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    user_data = data.get("data", {}).get("matchedUser")
                    
                    if user_data:
                        profile = user_data.get("profile", {})
                        submit_stats = user_data.get("submitStats", {})
                        
                        return {
                            "username": username,
                            "real_name": profile.get("realName", ""),
                            "about_me": profile.get("aboutMe", ""),
                            "avatar": profile.get("userAvatar", ""),
                            "location": profile.get("location", ""),
                            "websites": profile.get("websites", []),
                            "skill_tags": profile.get("skillTags", []),
                            "ranking": profile.get("ranking", 0),
                            "submit_stats": submit_stats
                        }
                
                # Fallback to basic profile
                return await self._get_basic_profile(username)
                
        except Exception as e:
            logger.warning(f"Failed to get LeetCode profile for {username}: {e}")
            return {"username": username, "error": str(e)}
    
    async def _get_basic_profile(self, username: str) -> Dict[str, Any]:
        """Get basic profile information as fallback"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://leetcode.com/{username}/")
                
                if response.status_code == 200:
                    # Basic profile data - would need HTML parsing for detailed extraction
                    return {
                        "username": username,
                        "profile_accessible": True,
                        "ranking": 0,
                        "submit_stats": {
                            "acSubmissionNum": [],
                            "totalSubmissionNum": []
                        }
                    }
                    
        except Exception as e:
            logger.warning(f"Failed to get basic LeetCode profile for {username}: {e}")
            
        return {"username": username, "error": "Profile not accessible"}
    
    async def _get_problem_statistics(self, username: str) -> Dict[str, Any]:
        """Get detailed problem solving statistics"""
        try:
            query = """
            query getUserStats($username: String!) {
                matchedUser(username: $username) {
                    submitStats {
                        acSubmissionNum {
                            difficulty
                            count
                        }
                        totalSubmissionNum {
                            difficulty
                            count
                        }
                    }
                    problemsSolvedBeatsStats {
                        difficulty
                        percentage
                    }
                    languageProblemCount {
                        languageName
                        problemsSolved
                    }
                    tagProblemCounts {
                        advanced {
                            tagName
                            tagSlug
                            problemsSolved
                        }
                        intermediate {
                            tagName
                            tagSlug
                            problemsSolved
                        }
                        fundamental {
                            tagName
                            tagSlug
                            problemsSolved
                        }
                    }
                }
            }
            """
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.graphql_endpoint,
                    json={"query": query, "variables": {"username": username}},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    user_data = data.get("data", {}).get("matchedUser", {})
                    
                    return {
                        "submit_stats": user_data.get("submitStats", {}),
                        "beats_stats": user_data.get("problemsSolvedBeatsStats", []),
                        "language_stats": user_data.get("languageProblemCount", []),
                        "tag_stats": user_data.get("tagProblemCounts", {})
                    }
                    
        except Exception as e:
            logger.warning(f"Failed to get problem statistics for {username}: {e}")
            
        return {}
    
    async def _get_contest_history(self, username: str) -> List[Dict[str, Any]]:
        """Get contest participation history"""
        try:
            query = """
            query getUserContestRanking($username: String!) {
                userContestRanking(username: $username) {
                    attendedContestsCount
                    rating
                    globalRanking
                    totalParticipants
                    topPercentage
                    badge {
                        name
                    }
                }
                userContestRankingHistory(username: $username) {
                    attended
                    trendDirection
                    problemsSolved
                    totalProblems
                    finishTimeInSeconds
                    rating
                    ranking
                    contest {
                        title
                        startTime
                    }
                }
            }
            """
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.graphql_endpoint,
                    json={"query": query, "variables": {"username": username}},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    contest_ranking = data.get("data", {}).get("userContestRanking", {})
                    contest_history = data.get("data", {}).get("userContestRankingHistory", [])
                    
                    return contest_history
                    
        except Exception as e:
            logger.warning(f"Failed to get contest history for {username}: {e}")
            
        return []
    
    async def _get_recent_submissions(self, username: str) -> List[Dict[str, Any]]:
        """Get recent submission history"""
        try:
            query = """
            query getRecentSubmissions($username: String!, $limit: Int) {
                recentSubmissionList(username: $username, limit: $limit) {
                    title
                    titleSlug
                    timestamp
                    statusDisplay
                    lang
                    runtime
                    memory
                    url
                }
            }
            """
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.graphql_endpoint,
                    json={"query": query, "variables": {"username": username, "limit": 20}},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    submissions = data.get("data", {}).get("recentSubmissionList", [])
                    
                    return submissions
                    
        except Exception as e:
            logger.warning(f"Failed to get recent submissions for {username}: {e}")
            
        return []
    
    def _calculate_progress_stats(self, profile: Dict, problem_stats: Dict,
                                contest_history: List, submissions: List) -> Dict[str, Any]:
        """Calculate overall progress statistics"""
        submit_stats = problem_stats.get("submit_stats", {})
        ac_stats = submit_stats.get("acSubmissionNum", [])
        total_stats = submit_stats.get("totalSubmissionNum", [])
        
        # Calculate problems solved by difficulty
        problems_by_difficulty = {}
        total_problems_solved = 0
        
        for stat in ac_stats:
            difficulty = stat.get("difficulty", "All")
            count = stat.get("count", 0)
            problems_by_difficulty[difficulty] = count
            if difficulty != "All":
                total_problems_solved += count
        
        # Calculate acceptance rate
        total_accepted = problems_by_difficulty.get("All", 0)
        total_submitted = 0
        for stat in total_stats:
            if stat.get("difficulty") == "All":
                total_submitted = stat.get("count", 0)
                break
        
        acceptance_rate = (total_accepted / max(total_submitted, 1)) * 100
        
        # Contest statistics
        contest_rating = 0
        contests_attended = 0
        if contest_history and len(contest_history) > 0:
            latest_contest = contest_history[0] if isinstance(contest_history, list) else contest_history
            contest_rating = latest_contest.get("rating", 0)
            contests_attended = len(contest_history) if isinstance(contest_history, list) else 1
        
        # Recent activity analysis
        recent_activity = len([s for s in submissions 
                             if self._is_recent_submission(s.get("timestamp", "0"))]) > 0
        
        # Calculate skill level
        skill_level = self._determine_skill_level(total_problems_solved, contest_rating)
        
        # Language preferences
        language_stats = problem_stats.get("language_stats", [])
        favorite_languages = sorted(language_stats, 
                                  key=lambda x: x.get("problemsSolved", 0), 
                                  reverse=True)[:3]
        
        return {
            "total_problems_solved": total_problems_solved,
            "problems_by_difficulty": problems_by_difficulty,
            "acceptance_rate": acceptance_rate,
            "contest_rating": contest_rating,
            "contests_attended": contests_attended,
            "global_ranking": 0,
            "skill_level": skill_level,
            "recent_activity": recent_activity,
            "favorite_languages": [lang.get("languageName", "") for lang in favorite_languages],
            "problem_solving_streak": self._calculate_streak(submissions),
            "strongest_topics": self._identify_strongest_topics(problem_stats),
            "learning_velocity": self._calculate_learning_velocity(submissions),
            "next_milestone": self._get_next_milestone(total_problems_solved, contest_rating)
        }
    
    def _is_recent_submission(self, timestamp: str) -> bool:
        """Check if submission is recent (within last 7 days)"""
        try:
            submission_time = datetime.fromtimestamp(int(timestamp))
            return (datetime.utcnow() - submission_time).days <= 7
        except:
            return False
    
    def _determine_skill_level(self, problems_solved: int, contest_rating: int) -> str:
        """Determine user's skill level based on progress"""
        if contest_rating >= 2000 or problems_solved >= 500:
            return "expert"
        elif contest_rating >= 1600 or problems_solved >= 200:
            return "advanced"
        elif contest_rating >= 1200 or problems_solved >= 50:
            return "intermediate"
        elif problems_solved >= 10:
            return "beginner"
        else:
            return "novice"
    
    def _calculate_streak(self, submissions: List) -> int:
        """Calculate current problem solving streak"""
        if not submissions:
            return 0
        
        # Sort submissions by timestamp
        sorted_submissions = sorted(submissions, 
                                  key=lambda x: int(x.get("timestamp", "0")), 
                                  reverse=True)
        
        streak = 0
        current_date = datetime.utcnow().date()
        
        for submission in sorted_submissions:
            try:
                submission_date = datetime.fromtimestamp(int(submission.get("timestamp", "0"))).date()
                if submission.get("statusDisplay") == "Accepted":
                    if (current_date - submission_date).days <= 1:
                        streak += 1
                        current_date = submission_date
                    else:
                        break
            except:
                continue
        
        return streak
    
    def _identify_strongest_topics(self, problem_stats: Dict) -> List[str]:
        """Identify user's strongest problem-solving topics"""
        tag_stats = problem_stats.get("tag_stats", {})
        all_tags = []
        
        # Combine all tag categories
        for category in ["advanced", "intermediate", "fundamental"]:
            tags = tag_stats.get(category, [])
            all_tags.extend(tags)
        
        # Sort by problems solved and return top topics
        sorted_tags = sorted(all_tags, 
                           key=lambda x: x.get("problemsSolved", 0), 
                           reverse=True)
        
        return [tag.get("tagName", "") for tag in sorted_tags[:5]]
    
    def _calculate_learning_velocity(self, submissions: List) -> Dict[str, float]:
        """Calculate learning velocity metrics"""
        if not submissions:
            return {"problems_per_week": 0, "acceptance_trend": 0}
        
        # Calculate problems solved per week (last 4 weeks)
        recent_cutoff = datetime.utcnow() - timedelta(days=28)
        recent_accepted = []
        
        for submission in submissions:
            try:
                timestamp = int(submission.get("timestamp", "0"))
                submission_time = datetime.fromtimestamp(timestamp)
                
                if (submission_time > recent_cutoff and 
                    submission.get("statusDisplay") == "Accepted"):
                    recent_accepted.append(submission)
            except:
                continue
        
        problems_per_week = len(recent_accepted) / 4.0
        
        # Calculate acceptance trend (improvement over time)
        acceptance_trend = 0  # Simplified - would need more historical data
        
        return {
            "problems_per_week": problems_per_week,
            "acceptance_trend": acceptance_trend,
            "recent_accepted_count": len(recent_accepted)
        }
    
    def _get_next_milestone(self, problems_solved: int, contest_rating: int) -> Dict[str, Any]:
        """Get the next learning milestone"""
        if problems_solved < 10:
            return {
                "type": "foundation",
                "title": "Solve Your First 10 Problems",
                "description": "Build basic problem-solving skills with easy problems",
                "target": f"Solve {10 - problems_solved} more problems",
                "estimated_time": f"{(10 - problems_solved) * 2} hours"
            }
        elif problems_solved < 50:
            return {
                "type": "skill_building",
                "title": "Reach 50 Problems Solved",
                "description": "Diversify your skills across different problem types",
                "target": f"Solve {50 - problems_solved} more problems",
                "estimated_time": f"{(50 - problems_solved) * 1.5} hours"
            }
        elif contest_rating == 0:
            return {
                "type": "contest_participation",
                "title": "Participate in Your First Contest",
                "description": "Test your skills in a timed competitive environment",
                "target": "Join the next weekly contest",
                "estimated_time": "1.5 hours per contest"
            }
        elif contest_rating < 1200:
            return {
                "type": "rating_improvement",
                "title": "Reach 1200 Contest Rating",
                "description": "Improve problem-solving speed and accuracy",
                "target": f"Gain {1200 - contest_rating} rating points",
                "estimated_time": "2-3 months of regular practice"
            }
        else:
            return {
                "type": "mastery",
                "title": "Master Advanced Algorithms",
                "description": "Focus on hard problems and advanced data structures",
                "target": "Solve 10 Hard problems",
                "estimated_time": "3-6 months"
            }
    
    async def _get_consciousness_analysis(self, username: str, profile: Dict, 
                                        problem_stats: Dict, contest_history: Dict, 
                                        stats: Dict) -> Dict[str, Any]:
        """Get AI consciousness analysis of algorithmic learning progress"""
        try:
            if not self.consciousness:
                return self._fallback_analysis(profile, problem_stats, contest_history, stats)
            
            analysis_data = {
                "platform": "leetcode",
                "username": username,
                "profile_data": profile,
                "problem_statistics": problem_stats,
                "contest_history": contest_history,
                "statistics": stats,
                "analysis_type": "algorithmic_thinking_learning"
            }
            
            # Request consciousness analysis
            insights = await self._request_consciousness_analysis(analysis_data)
            
            return insights or self._fallback_analysis(profile, problem_stats, contest_history, stats)
            
        except Exception as e:
            logger.warning(f"Consciousness analysis failed for {username}: {e}")
            return self._fallback_analysis(profile, problem_stats, contest_history, stats)
    
    async def _request_consciousness_analysis(self, data: Dict) -> Optional[Dict]:
        """Request analysis from consciousness system"""
        try:
            # This would integrate with the consciousness system
            # For now, return None to trigger fallback
            return None
        except Exception as e:
            logger.warning(f"Failed to get consciousness analysis: {e}")
            return None
    
    def _fallback_analysis(self, profile: Dict, problem_stats: Dict, 
                          contest_history: Dict, stats: Dict) -> Dict[str, Any]:
        """Fallback analysis when consciousness is unavailable"""
        problems_solved = stats.get("total_problems_solved", 0)
        contest_rating = stats.get("contest_rating", 0)
        acceptance_rate = stats.get("acceptance_rate", 0)
        
        # Determine learning pattern
        if contest_rating > 0:
            learning_pattern = "competitive_focused"
        elif problems_solved > 100:
            learning_pattern = "practice_focused"
        else:
            learning_pattern = "beginner"
        
        # Assess problem-solving efficiency
        if acceptance_rate > 80:
            efficiency = "high"
        elif acceptance_rate > 60:
            efficiency = "moderate"
        else:
            efficiency = "low"
        
        # Generate recommendations
        recommendations = []
        skill_level = stats.get("skill_level", "novice")
        
        if skill_level == "novice":
            recommendations.extend([
                "Start with Easy array and string problems",
                "Focus on understanding basic algorithms",
                "Practice daily for consistency"
            ])
        elif skill_level == "beginner":
            recommendations.extend([
                "Learn fundamental data structures (trees, graphs)",
                "Practice medium difficulty problems",
                "Consider participating in contests"
            ])
        else:
            recommendations.extend([
                "Focus on dynamic programming and advanced algorithms",
                "Participate regularly in contests",
                "Practice system design problems"
            ])
        
        return {
            "learning_pattern": learning_pattern,
            "problem_solving_efficiency": efficiency,
            "algorithmic_thinking": {
                "pattern_recognition": min(problems_solved * 2, 100),
                "optimization_skills": min(contest_rating / 20, 100),
                "code_quality": min(acceptance_rate, 100)
            },
            "recommendations": recommendations,
            "learning_efficiency": min(problems_solved / 5, 100),
            "next_focus_area": self._suggest_next_focus(stats),
            "estimated_improvement_time": self._estimate_improvement_time(problems_solved, contest_rating),
            "consciousness_available": False
        }
    
    def _suggest_next_focus(self, stats: Dict) -> str:
        """Suggest next area of focus based on current progress"""
        skill_level = stats.get("skill_level", "novice")
        contest_rating = stats.get("contest_rating", 0)
        problems_solved = stats.get("total_problems_solved", 0)
        
        if skill_level == "novice":
            return "Master basic array and string manipulation"
        elif skill_level == "beginner":
            return "Learn tree and graph algorithms"
        elif contest_rating == 0:
            return "Start participating in weekly contests"
        elif contest_rating < 1500:
            return "Improve contest problem-solving speed"
        else:
            return "Master advanced dynamic programming patterns"
    
    def _estimate_improvement_time(self, problems_solved: int, contest_rating: int) -> Dict[str, str]:
        """Estimate time to reach next skill level"""
        current_level = "novice"
        if contest_rating >= 1600:
            current_level = "advanced"
        elif contest_rating >= 1200 or problems_solved >= 50:
            current_level = "intermediate"
        elif problems_solved >= 10:
            current_level = "beginner"
        
        improvement_estimates = {
            "novice": {
                "next_level": "beginner",
                "estimated_time": "1-2 months with daily practice",
                "requirements": "Solve 20+ Easy problems"
            },
            "beginner": {
                "next_level": "intermediate",
                "estimated_time": "3-4 months",
                "requirements": "Solve 100+ problems, participate in contests"
            },
            "intermediate": {
                "next_level": "advanced",
                "estimated_time": "6-12 months",
                "requirements": "Reach 1600+ contest rating"
            },
            "advanced": {
                "next_level": "expert",
                "estimated_time": "1-2 years",
                "requirements": "Reach 2000+ contest rating, master all topics"
            }
        }
        
        return improvement_estimates.get(current_level, improvement_estimates["novice"])
    
    async def get_recommendations(self, user_id: str, progress_data: Dict) -> List[Dict[str, Any]]:
        """Get personalized learning recommendations"""
        try:
            consciousness_insights = progress_data.get("consciousness_insights", {})
            stats = progress_data.get("statistics", {})
            
            recommendations = []
            
            # Based on current skill level
            skill_level = stats.get("skill_level", "novice")
            problems_solved = stats.get("total_problems_solved", 0)
            
            if skill_level == "novice":
                recommendations.append({
                    "type": "foundation",
                    "title": "Start with Easy Problems",
                    "description": "Begin with basic array and string problems to build confidence",
                    "priority": 0.9,
                    "estimated_time": "1-2 hours per problem",
                    "skills": ["arrays", "strings", "basic_algorithms"],
                    "platform": "leetcode"
                })
            elif skill_level == "beginner":
                recommendations.append({
                    "type": "skill_building",
                    "title": "Learn Data Structures",
                    "description": "Master trees, graphs, and hash tables through medium problems",
                    "priority": 0.8,
                    "estimated_time": "2-3 hours per problem",
                    "skills": ["trees", "graphs", "hash_tables"],
                    "platform": "leetcode"
                })
            else:
                recommendations.append({
                    "type": "advancement",
                    "title": "Contest Participation",
                    "description": "Improve problem-solving speed through regular contest participation",
                    "priority": 0.7,
                    "estimated_time": "1.5 hours per contest",
                    "skills": ["competitive_programming", "time_management"],
                    "platform": "leetcode"
                })
            
            # Add consciousness-driven recommendations if available
            if consciousness_insights.get("recommendations"):
                for rec in consciousness_insights["recommendations"]:
                    recommendations.append({
                        "type": "ai_suggested",
                        "title": f"AI Recommendation: {rec}",
                        "description": "Personalized suggestion from consciousness analysis",
                        "priority": 0.85,
                        "platform": "leetcode"
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get LeetCode recommendations: {e}")
            return []
    
    async def sync_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Manually sync user progress data"""
        try:
            progress_data = await self.get_user_progress(user_id)
            
            return {
                "sync_status": "success",
                "platform": "leetcode",
                "user_id": user_id,
                "data": progress_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to sync LeetCode data for {user_id}: {e}")
            return {
                "sync_status": "failed",
                "platform": "leetcode",
                "user_id": user_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }