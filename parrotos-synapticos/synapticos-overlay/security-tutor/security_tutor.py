#!/usr/bin/env python3
"""
Security Tutor Module for SynapticOS
Interactive cybersecurity education with adaptive difficulty
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import random
import subprocess

logger = logging.getLogger('synapticos.security_tutor')

class ModuleType(Enum):
    """Types of security modules"""
    NETWORK_SECURITY = "network_security"
    WEB_EXPLOITATION = "web_exploitation"
    CRYPTOGRAPHY = "cryptography"
    FORENSICS = "forensics"
    REVERSE_ENGINEERING = "reverse_engineering"
    SOCIAL_ENGINEERING = "social_engineering"
    MALWARE_ANALYSIS = "malware_analysis"
    CLOUD_SECURITY = "cloud_security"
    MOBILE_SECURITY = "mobile_security"

class LessonType(Enum):
    """Types of lessons"""
    THEORY = "theory"
    DEMONSTRATION = "demonstration"
    HANDS_ON = "hands_on"
    CHALLENGE = "challenge"
    ASSESSMENT = "assessment"

@dataclass
class Lesson:
    """Individual lesson in a module"""
    id: str
    title: str
    module: ModuleType
    lesson_type: LessonType
    difficulty: str  # beginner, intermediate, advanced, expert
    duration_minutes: int
    objectives: List[str]
    content: str
    tools_required: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    
@dataclass
class Challenge:
    """Hands-on security challenge"""
    id: str
    title: str
    description: str
    difficulty: str
    points: int
    hints: List[str]
    solution: str
    validation_script: str
    environment_setup: Dict[str, Any]

@dataclass
class Progress:
    """User's progress in a module"""
    user_id: str
    module: ModuleType
    completed_lessons: List[str] = field(default_factory=list)
    current_lesson: Optional[str] = None
    score: int = 0
    time_spent_minutes: int = 0
    last_activity: datetime = field(default_factory=datetime.now)

class SecurityTutor:
    """Main security education system"""
    
    def __init__(self, content_path: str = "/opt/synapticos/security-tutor/content"):
        self.content_path = Path(content_path)
        self.lessons: Dict[str, Lesson] = {}
        self.challenges: Dict[str, Challenge] = {}
        self.user_progress: Dict[str, Dict[ModuleType, Progress]] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Integration with other systems
        self.lm_studio_client = None
        self.context_engine = None
        
    async def initialize(self, lm_studio_client=None, context_engine=None) -> bool:
        """Initialize the security tutor"""
        try:
            self.lm_studio_client = lm_studio_client
            self.context_engine = context_engine
            
            # Load content
            await self._load_content()
            
            # Initialize default lessons if none exist
            if not self.lessons:
                await self._create_default_content()
            
            logger.info("Security Tutor initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Security Tutor: {e}")
            return False
    
    async def _create_default_content(self):
        """Create default lesson content"""
        # Network Security Basics
        self.lessons["net_sec_101"] = Lesson(
            id="net_sec_101",
            title="Network Security Fundamentals",
            module=ModuleType.NETWORK_SECURITY,
            lesson_type=LessonType.THEORY,
            difficulty="beginner",
            duration_minutes=30,
            objectives=[
                "Understand OSI model and security implications",
                "Learn about common network protocols",
                "Identify network vulnerabilities"
            ],
            content="""
# Network Security Fundamentals

## Introduction
Network security is the practice of protecting computer networks from intruders, 
whether targeted attackers or opportunistic malware.

## The OSI Model
Understanding the 7 layers of the OSI model is crucial for network security:

1. **Physical Layer**: Hardware, cables, signals
2. **Data Link Layer**: Ethernet, switches, MAC addresses
3. **Network Layer**: IP addresses, routers, packets
4. **Transport Layer**: TCP/UDP, ports, segments
5. **Session Layer**: Sessions, connections
6. **Presentation Layer**: Encryption, compression
7. **Application Layer**: HTTP, FTP, SMTP

## Common Attack Vectors
- Man-in-the-Middle (MITM)
- Denial of Service (DoS/DDoS)
- Port Scanning
- Packet Sniffing
- ARP Spoofing

## Next Steps
Practice with tools like Wireshark and nmap to see these concepts in action.
""",
            tools_required=["wireshark", "nmap"],
            prerequisites=[]
        )
        
        # Nmap Hands-on
        self.lessons["nmap_hands_on"] = Lesson(
            id="nmap_hands_on",
            title="Network Scanning with Nmap",
            module=ModuleType.NETWORK_SECURITY,
            lesson_type=LessonType.HANDS_ON,
            difficulty="beginner",
            duration_minutes=45,
            objectives=[
                "Learn basic nmap commands",
                "Understand different scan types",
                "Interpret scan results"
            ],
            content="""
# Network Scanning with Nmap

## Basic Commands

### 1. Simple Scan
```bash
nmap 192.168.1.1
```

### 2. Scan Network Range
```bash
nmap 192.168.1.0/24
```

### 3. Service Version Detection
```bash
nmap -sV 192.168.1.1
```

### 4. OS Detection
```bash
nmap -O 192.168.1.1
```

### 5. Stealth Scan
```bash
nmap -sS 192.168.1.1
```

## Practice Exercise
1. Scan your local network (with permission)
2. Identify all active hosts
3. Determine services running on each host
4. Document your findings

## Important: Legal and Ethical Considerations
- Only scan networks you own or have permission to test
- Unauthorized scanning is illegal in many jurisdictions
- Always follow responsible disclosure practices
""",
            tools_required=["nmap"],
            prerequisites=["net_sec_101"]
        )
        
        # Web Exploitation Basics
        self.lessons["web_exp_101"] = Lesson(
            id="web_exp_101",
            title="Web Application Security Basics",
            module=ModuleType.WEB_EXPLOITATION,
            lesson_type=LessonType.THEORY,
            difficulty="beginner",
            duration_minutes=40,
            objectives=[
                "Understand OWASP Top 10",
                "Learn about common web vulnerabilities",
                "Know basic defense mechanisms"
            ],
            content="""
# Web Application Security Basics

## OWASP Top 10 (2021)

1. **Broken Access Control**
2. **Cryptographic Failures**
3. **Injection**
4. **Insecure Design**
5. **Security Misconfiguration**
6. **Vulnerable Components**
7. **Authentication Failures**
8. **Data Integrity Failures**
9. **Security Logging Failures**
10. **Server-Side Request Forgery**

## Common Vulnerabilities

### SQL Injection
```sql
' OR '1'='1' --
```

### Cross-Site Scripting (XSS)
```javascript
<script>alert('XSS')</script>
```

### Directory Traversal
```
../../../../etc/passwd
```

## Defense Mechanisms
- Input validation
- Output encoding
- Parameterized queries
- Content Security Policy (CSP)
- Regular security updates
""",
            tools_required=["burpsuite"],
            prerequisites=[]
        )
        
        # Create challenges
        self.challenges["basic_sqli"] = Challenge(
            id="basic_sqli",
            title="Basic SQL Injection",
            description="Find and exploit a SQL injection vulnerability in the login form",
            difficulty="beginner",
            points=100,
            hints=[
                "Try special characters in the input fields",
                "Think about how SQL queries work",
                "What happens if you close the quote early?"
            ],
            solution="username: admin' -- \npassword: anything",
            validation_script="validate_sqli.py",
            environment_setup={
                "docker_image": "vulnerables/web-dvwa",
                "port": 8080,
                "path": "/login.php"
            }
        )
        
        await self._save_content()
    
    async def start_lesson(self, user_id: str, lesson_id: str) -> Dict[str, Any]:
        """Start a lesson for a user"""
        if lesson_id not in self.lessons:
            return {"error": "Lesson not found"}
        
        lesson = self.lessons[lesson_id]
        
        # Check prerequisites
        if lesson.prerequisites:
            progress = await self._get_user_progress(user_id, lesson.module)
            for prereq in lesson.prerequisites:
                if prereq not in progress.completed_lessons:
                    return {"error": f"Prerequisite not met: {prereq}"}
        
        # Create session
        session_id = f"{user_id}_{lesson_id}_{datetime.now().timestamp()}"
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "lesson": lesson,
            "start_time": datetime.now(),
            "completed": False
        }
        
        # Get adaptive content if AI is available
        content = lesson.content
        if self.lm_studio_client and self.context_engine:
            skill_level = await self.context_engine.get_skill_level(user_id, lesson.module.value)
            if skill_level:
                # Enhance content based on skill level
                enhanced = await self._enhance_content_for_skill(content, skill_level.value)
                if enhanced:
                    content = enhanced
        
        return {
            "session_id": session_id,
            "lesson": lesson,
            "content": content,
            "estimated_time": lesson.duration_minutes
        }
    
    async def complete_lesson(self, session_id: str, score: int = 100) -> Dict[str, Any]:
        """Mark a lesson as completed"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        lesson = session["lesson"]
        user_id = session["user_id"]
        
        # Calculate time spent
        time_spent = int((datetime.now() - session["start_time"]).total_seconds() / 60)
        
        # Update progress
        progress = await self._get_user_progress(user_id, lesson.module)
        if lesson.id not in progress.completed_lessons:
            progress.completed_lessons.append(lesson.id)
            progress.score += score
        progress.time_spent_minutes += time_spent
        progress.last_activity = datetime.now()
        
        # Record in context engine if available
        if self.context_engine:
            await self.context_engine.record_activity(
                user_id=user_id,
                activity_type="learning",
                domain=lesson.module.value,
                tool_used="security_tutor",
                duration_seconds=time_spent * 60,
                success=score >= 70,
                metadata={"lesson_id": lesson.id, "score": score}
            )
        
        # Clean up session
        del self.active_sessions[session_id]
        
        # Get next recommendation
        next_lesson = await self._recommend_next_lesson(user_id, lesson.module)
        
        return {
            "completed": True,
            "score": score,
            "time_spent": time_spent,
            "next_recommendation": next_lesson
        }
    
    async def start_challenge(self, user_id: str, challenge_id: str) -> Dict[str, Any]:
        """Start a hands-on challenge"""
        if challenge_id not in self.challenges:
            return {"error": "Challenge not found"}
        
        challenge = self.challenges[challenge_id]
        
        # Set up challenge environment
        environment = await self._setup_challenge_environment(challenge)
        
        if not environment:
            return {"error": "Failed to set up challenge environment"}
        
        # Create session
        session_id = f"{user_id}_challenge_{challenge_id}_{datetime.now().timestamp()}"
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "challenge": challenge,
            "environment": environment,
            "start_time": datetime.now(),
            "hints_used": 0
        }
        
        return {
            "session_id": session_id,
            "challenge": {
                "title": challenge.title,
                "description": challenge.description,
                "difficulty": challenge.difficulty,
                "points": challenge.points
            },
            "environment": environment
        }
    
    async def get_hint(self, session_id: str) -> Dict[str, Any]:
        """Get a hint for the current challenge"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        challenge = session["challenge"]
        hints_used = session["hints_used"]
        
        if hints_used >= len(challenge.hints):
            return {"error": "No more hints available"}
        
        hint = challenge.hints[hints_used]
        session["hints_used"] += 1
        
        # Reduce points for using hints
        points_reduction = 10 * session["hints_used"]
        
        return {
            "hint": hint,
            "hints_remaining": len(challenge.hints) - session["hints_used"],
            "points_reduction": points_reduction
        }
    
    async def submit_challenge(self, session_id: str, solution: str) -> Dict[str, Any]:
        """Submit a challenge solution"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        challenge = session["challenge"]
        user_id = session["user_id"]
        
        # Validate solution
        is_correct = await self._validate_solution(challenge, solution)
        
        # Calculate score
        base_points = challenge.points
        hints_penalty = 10 * session["hints_used"]
        time_bonus = max(0, 30 - int((datetime.now() - session["start_time"]).total_seconds() / 60))
        final_score = max(0, base_points - hints_penalty + time_bonus) if is_correct else 0
        
        # Clean up environment
        await self._cleanup_challenge_environment(session["environment"])
        
        # Update progress
        if is_correct and self.context_engine:
            await self.context_engine.record_activity(
                user_id=user_id,
                activity_type="practicing",
                domain="security_challenges",
                tool_used="challenge_platform",
                duration_seconds=int((datetime.now() - session["start_time"]).total_seconds()),
                success=True,
                metadata={
                    "challenge_id": challenge.id,
                    "score": final_score,
                    "hints_used": session["hints_used"]
                }
            )
        
        # Clean up session
        del self.active_sessions[session_id]
        
        return {
            "correct": is_correct,
            "score": final_score,
            "explanation": challenge.solution if is_correct else "Try again!",
            "time_taken": int((datetime.now() - session["start_time"]).total_seconds() / 60)
        }
    
    async def get_module_progress(self, user_id: str, module: ModuleType) -> Dict[str, Any]:
        """Get user's progress in a module"""
        progress = await self._get_user_progress(user_id, module)
        
        # Get all lessons in module
        module_lessons = [l for l in self.lessons.values() if l.module == module]
        total_lessons = len(module_lessons)
        completed_lessons = len(progress.completed_lessons)
        
        # Calculate completion percentage
        completion = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        # Get next lesson
        next_lesson = None
        for lesson in sorted(module_lessons, key=lambda x: (x.difficulty, x.id)):
            if lesson.id not in progress.completed_lessons:
                next_lesson = lesson
                break
        
        return {
            "module": module.value,
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons,
            "completion_percentage": completion,
            "total_score": progress.score,
            "time_spent_hours": progress.time_spent_minutes / 60,
            "next_lesson": next_lesson,
            "last_activity": progress.last_activity.isoformat()
        }
    
    async def get_learning_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive learning dashboard for user"""
        dashboard = {
            "modules": {},
            "total_score": 0,
            "total_time_hours": 0,
            "achievements": [],
            "recommendations": []
        }
        
        # Get progress for each module
        for module in ModuleType:
            progress = await self.get_module_progress(user_id, module)
            dashboard["modules"][module.value] = progress
            dashboard["total_score"] += progress["total_score"]
            dashboard["total_time_hours"] += progress["time_spent_hours"]
        
        # Get recommendations
        if self.context_engine:
            recommendations = await self.context_engine.get_recommendations(user_id)
            dashboard["recommendations"] = recommendations.get("next_modules", [])
        
        # Check achievements
        achievements = self._check_achievements(dashboard)
        dashboard["achievements"] = achievements
        
        return dashboard
    
    def _check_achievements(self, dashboard: Dict[str, Any]) -> List[Dict[str, str]]:
        """Check for earned achievements"""
        achievements = []
        
        # First module completed
        for module_data in dashboard["modules"].values():
            if module_data["completion_percentage"] >= 100:
                achievements.append({
                    "id": "module_master",
                    "title": "Module Master",
                    "description": f"Completed all lessons in {module_data['module']}"
                })
                break
        
        # Score milestones
        total_score = dashboard["total_score"]
        score_achievements = [
            (1000, "score_1k", "Rising Star", "Earned 1,000 points"),
            (5000, "score_5k", "Security Enthusiast", "Earned 5,000 points"),
            (10000, "score_10k", "Security Expert", "Earned 10,000 points")
        ]
        
        for threshold, id, title, desc in score_achievements:
            if total_score >= threshold:
                achievements.append({
                    "id": id,
                    "title": title,
                    "description": desc
                })
        
        # Time dedication
        if dashboard["total_time_hours"] >= 10:
            achievements.append({
                "id": "dedicated_learner",
                "title": "Dedicated Learner",
                "description": "Spent 10+ hours learning"
            })
        
        return achievements
    
    async def _get_user_progress(self, user_id: str, module: ModuleType) -> Progress:
        """Get or create user progress for a module"""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {}
        
        if module not in self.user_progress[user_id]:
            self.user_progress[user_id][module] = Progress(
                user_id=user_id,
                module=module
            )
        
        return self.user_progress[user_id][module]
    
    async def _recommend_next_lesson(self, user_id: str, module: ModuleType) -> Optional[Lesson]:
        """Recommend the next lesson based on progress and skill"""
        progress = await self._get_user_progress(user_id, module)
        module_lessons = [l for l in self.lessons.values() if l.module == module]
        
        # Filter out completed lessons
        available_lessons = [l for l in module_lessons if l.id not in progress.completed_lessons]
        
        if not available_lessons:
            return None
        
        # Get skill level from context engine
        skill_level = "beginner"
        if self.context_engine:
            level = await self.context_engine.get_skill_level(user_id, module.value)
            if level:
                skill_level = level.value
        
        # Find lessons matching skill level
        matching_lessons = [l for l in available_lessons if l.difficulty == skill_level]
        
        if matching_lessons:
            # Prioritize by lesson type: theory -> demonstration -> hands_on -> challenge
            type_priority = [LessonType.THEORY, LessonType.DEMONSTRATION, 
                           LessonType.HANDS_ON, LessonType.CHALLENGE]
            
            for lesson_type in type_priority:
                typed_lessons = [l for l in matching_lessons if l.lesson_type == lesson_type]
                if typed_lessons:
                    return typed_lessons[0]
        
        # If no matching lessons, return the easiest available
        return min(available_lessons, key=lambda x: ["beginner", "intermediate", "advanced", "expert"].index(x.difficulty))
    
    async def _enhance_content_for_skill(self, content: str, skill_level: str) -> Optional[str]:
        """Use AI to enhance content based on skill level"""
        if not self.lm_studio_client:
            return None
        
        try:
            prompt = f"""Adapt this security lesson content for a {skill_level} level student.
If beginner: Add more explanations and examples
If intermediate: Add practical tips and common pitfalls
If advanced: Add edge cases and advanced techniques
If expert: Add cutting-edge research and complex scenarios

Original content:
{content}

Adapted content:"""
            
            response = await self.lm_studio_client.generate(
                prompt=prompt,
                system_prompt="You are a cybersecurity educator adapting content for different skill levels.",
                max_tokens=2000
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"Failed to enhance content: {e}")
            return None
    
    async def _setup_challenge_environment(self, challenge: Challenge) -> Optional[Dict[str, Any]]:
        """Set up the challenge environment (Docker, VMs, etc.)"""
        try:
            # For now, return mock environment details
            # In production, this would spin up actual containers/VMs
            return {
                "type": "docker",
                "url": f"http://localhost:{challenge.environment_setup.get('port', 8080)}",
                "credentials": {
                    "username": "student",
                    "password": "student123"
                },
                "timeout_minutes": 60
            }
        except Exception as e:
            logger.error(f"Failed to setup challenge environment: {e}")
            return None
    
    async def _cleanup_challenge_environment(self, environment: Dict[str, Any]) -> None:
        """Clean up challenge environment"""
        # In production, this would stop containers/VMs
        logger.info(f"Cleaning up environment: {environment}")
    
    async def _validate_solution(self, challenge: Challenge, solution: str) -> bool:
        """Validate a challenge solution"""
        # Simple validation for now
        # In production, this would run the validation script
        return solution.strip().lower() == challenge.solution.strip().lower()
    
    async def _save_content(self) -> None:
        """Save lessons and challenges to disk"""
        # In production, this would persist to database
        logger.info("Content saved")
    
    async def _load_content(self) -> None:
        """Load lessons and challenges from disk"""
        # In production, this would load from database
        logger.info("Content loaded")


# Example usage
async def main():
    """Example usage of Security Tutor"""
    tutor = SecurityTutor()
    await tutor.initialize()
    
    user_id = "test_user"
    
    # Start a lesson
    result = await tutor.start_lesson(user_id, "net_sec_101")
    print(f"Started lesson: {result['lesson'].title}")
    
    # Complete the lesson
    completion = await tutor.complete_lesson(result['session_id'], score=95)
    print(f"Lesson completed with score: {completion['score']}")
    
    # Get module progress
    progress = await tutor.get_module_progress(user_id, ModuleType.NETWORK_SECURITY)
    print(f"Module progress: {progress['completion_percentage']}%")
    
    # Get dashboard
    dashboard = await tutor.get_learning_dashboard(user_id)
    print(f"Total score: {dashboard['total_score']}")


if __name__ == "__main__":
    asyncio.run(main())