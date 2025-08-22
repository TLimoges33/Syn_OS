#!/usr/bin/env python3
"""
Consciousness-Aware Security Tutor Application

This application provides personalized cybersecurity training that adapts
based on the consciousness system's understanding of user behavior, learning
patterns, and attention levels.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

import aiohttp
from aiohttp import web
import nats
from jinja2 import Environment, FileSystemLoader

# Add the consciousness system to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from consciousness_v2.bridges.nats_bridge import NATSBridge


class SkillLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class LearningStyle(Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING = "reading"


@dataclass
class UserProfile:
    """User profile with learning preferences and progress"""
    user_id: str
    name: str
    skill_level: SkillLevel
    learning_style: LearningStyle
    attention_span: int  # minutes
    preferred_session_length: int  # minutes
    completed_modules: List[str]
    current_streak: int
    total_score: int
    last_active: datetime
    consciousness_insights: Dict[str, Any]


@dataclass
class SecurityModule:
    """Security training module"""
    module_id: str
    title: str
    description: str
    skill_level: SkillLevel
    estimated_duration: int  # minutes
    prerequisites: List[str]
    learning_objectives: List[str]
    content_type: str  # "interactive", "video", "simulation", "quiz"
    difficulty_score: float
    engagement_factors: List[str]


@dataclass
class LearningSession:
    """Individual learning session"""
    session_id: str
    user_id: str
    module_id: str
    start_time: datetime
    end_time: Optional[datetime]
    attention_level: float
    engagement_score: float
    completion_rate: float
    mistakes_made: int
    time_spent: int  # seconds
    consciousness_feedback: Dict[str, Any]


class ConsciousnessAwareSecurityTutor:
    """Main security tutor application with consciousness integration"""
    
    def __init__(self):
        self.app = web.Application()
        self.nats_client = None
        self.consciousness_bridge = None
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.nats_url = os.getenv('NATS_URL', 'nats://localhost:4222')
        self.orchestrator_url = os.getenv('ORCHESTRATOR_URL', 'http://localhost:8080')
        self.port = int(os.getenv('SECURITY_TUTOR_PORT', '8082'))
        
        # In-memory storage (would be database in production)
        self.user_profiles: Dict[str, UserProfile] = {}
        self.security_modules: Dict[str, SecurityModule] = {}
        self.active_sessions: Dict[str, LearningSession] = {}
        
        # Jinja2 template environment
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
        self._setup_routes()
        self._load_security_modules()
    
    def _setup_routes(self):
        """Setup web application routes"""
        # Static files
        self.app.router.add_static('/static', 'applications/security_tutor/static')
        
        # API routes
        self.app.router.add_get('/', self.index)
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_post('/api/users', self.create_user)
        self.app.router.add_get('/api/users/{user_id}', self.get_user)
        self.app.router.add_get('/api/users/{user_id}/recommendations', self.get_recommendations)
        self.app.router.add_post('/api/sessions', self.start_session)
        self.app.router.add_put('/api/sessions/{session_id}', self.update_session)
        self.app.router.add_post('/api/sessions/{session_id}/complete', self.complete_session)
        self.app.router.add_get('/api/modules', self.get_modules)
        self.app.router.add_get('/api/modules/{module_id}', self.get_module)
        self.app.router.add_get('/api/consciousness/insights/{user_id}', self.get_consciousness_insights)
        
        # Web interface routes
        self.app.router.add_get('/dashboard/{user_id}', self.dashboard)
        self.app.router.add_get('/learn/{module_id}', self.learning_interface)
        self.app.router.add_get('/profile/{user_id}', self.user_profile_page)
    
    def _load_security_modules(self):
        """Load predefined security training modules"""
        modules = [
            SecurityModule(
                module_id="phishing_basics",
                title="Phishing Attack Recognition",
                description="Learn to identify and avoid phishing attempts",
                skill_level=SkillLevel.BEGINNER,
                estimated_duration=15,
                prerequisites=[],
                learning_objectives=[
                    "Identify common phishing indicators",
                    "Understand social engineering tactics",
                    "Practice safe email habits"
                ],
                content_type="interactive",
                difficulty_score=2.0,
                engagement_factors=["gamification", "real_examples", "immediate_feedback"]
            ),
            SecurityModule(
                module_id="password_security",
                title="Advanced Password Security",
                description="Master password creation and management",
                skill_level=SkillLevel.INTERMEDIATE,
                estimated_duration=20,
                prerequisites=["phishing_basics"],
                learning_objectives=[
                    "Create strong, unique passwords",
                    "Understand password manager benefits",
                    "Implement multi-factor authentication"
                ],
                content_type="simulation",
                difficulty_score=3.5,
                engagement_factors=["hands_on", "password_strength_meter", "security_scenarios"]
            ),
            SecurityModule(
                module_id="network_security",
                title="Network Security Fundamentals",
                description="Understand network threats and protections",
                skill_level=SkillLevel.ADVANCED,
                estimated_duration=30,
                prerequisites=["password_security"],
                learning_objectives=[
                    "Identify network vulnerabilities",
                    "Configure secure network settings",
                    "Understand VPN and encryption"
                ],
                content_type="simulation",
                difficulty_score=4.5,
                engagement_factors=["network_diagrams", "threat_modeling", "practical_exercises"]
            ),
            SecurityModule(
                module_id="incident_response",
                title="Security Incident Response",
                description="Learn to respond to security incidents",
                skill_level=SkillLevel.EXPERT,
                estimated_duration=45,
                prerequisites=["network_security"],
                learning_objectives=[
                    "Develop incident response procedures",
                    "Practice forensic analysis",
                    "Coordinate security team response"
                ],
                content_type="simulation",
                difficulty_score=5.0,
                engagement_factors=["crisis_scenarios", "team_coordination", "decision_making"]
            )
        ]
        
        for module in modules:
            self.security_modules[module.module_id] = module
    
    async def start(self):
        """Start the security tutor application"""
        self.logger.info("Starting Consciousness-Aware Security Tutor...")
        
        # Connect to NATS and consciousness system
        await self._connect_consciousness()
        
        # Start web server
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        self.logger.info(f"Security Tutor started on port {self.port}")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Shutting down Security Tutor...")
        finally:
            await runner.cleanup()
            if self.nats_client:
                await self.nats_client.close()
    
    async def _connect_consciousness(self):
        """Connect to consciousness system via NATS"""
        try:
            self.nats_client = await nats.connect(self.nats_url)
            
            # Subscribe to consciousness insights
            await self.nats_client.subscribe(
                "consciousness.user_insights.*",
                self._handle_consciousness_insights
            )
            
            self.logger.info("Connected to consciousness system")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to consciousness system: {e}")
    
    async def _handle_consciousness_insights(self, msg):
        """Handle consciousness insights about users"""
        try:
            data = json.loads(msg.data.decode())
            user_id = data.get('user_id')
            insights = data.get('insights', {})
            
            if user_id in self.user_profiles:
                self.user_profiles[user_id].consciousness_insights.update(insights)
                self.logger.debug(f"Updated consciousness insights for user {user_id}")
                
        except Exception as e:
            self.logger.error(f"Error handling consciousness insights: {e}")
    
    async def _get_consciousness_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Get personalized recommendations from consciousness system"""
        try:
            if not self.nats_client:
                return {}
            
            # Request consciousness analysis
            request = {
                "user_id": user_id,
                "context": "security_training",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.nats_client.publish(
                "consciousness.analyze_user",
                json.dumps(request).encode()
            )
            
            # In a real implementation, we'd wait for a response
            # For now, return mock recommendations based on stored insights
            user_profile = self.user_profiles.get(user_id)
            if user_profile and user_profile.consciousness_insights:
                return self._generate_recommendations_from_insights(user_profile)
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting consciousness recommendations: {e}")
            return {}
    
    def _generate_recommendations_from_insights(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Generate recommendations based on consciousness insights"""
        insights = user_profile.consciousness_insights
        recommendations = {
            "suggested_modules": [],
            "optimal_session_length": user_profile.preferred_session_length,
            "best_time_to_learn": "morning",  # Default
            "learning_approach": "adaptive",
            "difficulty_adjustment": 0.0
        }
        
        # Analyze attention patterns
        attention_level = insights.get('attention_level', 0.5)
        if attention_level > 0.8:
            recommendations["optimal_session_length"] = min(45, user_profile.preferred_session_length + 10)
            recommendations["difficulty_adjustment"] = 0.2
        elif attention_level < 0.3:
            recommendations["optimal_session_length"] = max(10, user_profile.preferred_session_length - 5)
            recommendations["difficulty_adjustment"] = -0.3
        
        # Analyze cognitive load
        cognitive_load = insights.get('cognitive_load', 0.5)
        if cognitive_load > 0.7:
            recommendations["learning_approach"] = "simplified"
            recommendations["suggested_break_frequency"] = 5  # minutes
        
        # Recommend modules based on skill level and completion
        available_modules = [
            module for module in self.security_modules.values()
            if module.module_id not in user_profile.completed_modules
            and all(prereq in user_profile.completed_modules for prereq in module.prerequisites)
        ]
        
        # Sort by difficulty and user's current state
        suitable_modules = [
            module for module in available_modules
            if abs(module.difficulty_score - self._get_user_difficulty_preference(user_profile)) <= 1.5
        ]
        
        recommendations["suggested_modules"] = [
            {"module_id": module.module_id, "title": module.title, "reason": self._get_recommendation_reason(module, insights)}
            for module in suitable_modules[:3]
        ]
        
        return recommendations
    
    def _get_user_difficulty_preference(self, user_profile: UserProfile) -> float:
        """Calculate user's preferred difficulty level"""
        base_difficulty = {
            SkillLevel.BEGINNER: 2.0,
            SkillLevel.INTERMEDIATE: 3.5,
            SkillLevel.ADVANCED: 4.5,
            SkillLevel.EXPERT: 5.0
        }[user_profile.skill_level]
        
        # Adjust based on recent performance
        if user_profile.consciousness_insights.get('recent_success_rate', 0.5) > 0.8:
            base_difficulty += 0.5
        elif user_profile.consciousness_insights.get('recent_success_rate', 0.5) < 0.4:
            base_difficulty -= 0.5
        
        return max(1.0, min(5.0, base_difficulty))
    
    def _get_recommendation_reason(self, module: SecurityModule, insights: Dict[str, Any]) -> str:
        """Generate explanation for why a module is recommended"""
        reasons = []
        
        if insights.get('attention_level', 0.5) > 0.7 and module.difficulty_score > 4.0:
            reasons.append("High attention level suitable for challenging content")
        
        if insights.get('learning_momentum', 0.5) > 0.6:
            reasons.append("Good learning momentum for skill progression")
        
        if module.content_type == "interactive" and insights.get('engagement_preference') == "hands_on":
            reasons.append("Matches your hands-on learning preference")
        
        return reasons[0] if reasons else "Recommended based on your learning path"
    
    # Web route handlers
    async def index(self, request):
        """Main index page"""
        template = self.jinja_env.get_template('index.html')
        return web.Response(text=template.render(), content_type='text/html')
    
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "service": "security_tutor",
            "consciousness_connected": self.nats_client is not None,
            "active_users": len(self.user_profiles),
            "active_sessions": len(self.active_sessions)
        })
    
    async def create_user(self, request):
        """Create a new user profile"""
        try:
            data = await request.json()
            
            user_profile = UserProfile(
                user_id=data['user_id'],
                name=data['name'],
                skill_level=SkillLevel(data.get('skill_level', 'beginner')),
                learning_style=LearningStyle(data.get('learning_style', 'visual')),
                attention_span=data.get('attention_span', 20),
                preferred_session_length=data.get('preferred_session_length', 15),
                completed_modules=[],
                current_streak=0,
                total_score=0,
                last_active=datetime.utcnow(),
                consciousness_insights={}
            )
            
            self.user_profiles[user_profile.user_id] = user_profile
            
            return web.json_response({
                "status": "success",
                "user_id": user_profile.user_id,
                "message": "User profile created successfully"
            })
            
        except Exception as e:
            return web.json_response({
                "status": "error",
                "message": str(e)
            }, status=400)
    
    async def get_user(self, request):
        """Get user profile"""
        user_id = request.match_info['user_id']
        
        if user_id not in self.user_profiles:
            return web.json_response({
                "status": "error",
                "message": "User not found"
            }, status=404)
        
        user_profile = self.user_profiles[user_id]
        # Convert datetime objects to strings for JSON serialization
        user_data = asdict(user_profile)
        user_data['last_active'] = user_profile.last_active.isoformat()
        return web.json_response(user_data)
    
    async def get_recommendations(self, request):
        """Get personalized learning recommendations"""
        user_id = request.match_info['user_id']
        
        if user_id not in self.user_profiles:
            return web.json_response({
                "status": "error",
                "message": "User not found"
            }, status=404)
        
        recommendations = await self._get_consciousness_recommendations(user_id)
        
        return web.json_response({
            "status": "success",
            "user_id": user_id,
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat()
        })
    
    async def get_modules(self, request):
        """Get available security modules"""
        modules_data = [asdict(module) for module in self.security_modules.values()]
        return web.json_response({
            "status": "success",
            "modules": modules_data
        })
    
    async def get_module(self, request):
        """Get specific security module"""
        module_id = request.match_info['module_id']
        
        if module_id not in self.security_modules:
            return web.json_response({
                "status": "error",
                "message": "Module not found"
            }, status=404)
        
        module = self.security_modules[module_id]
        return web.json_response(asdict(module))
    
    async def dashboard(self, request):
        """User dashboard page"""
        user_id = request.match_info['user_id']
        
        if user_id not in self.user_profiles:
            return web.Response(text="User not found", status=404)
        
        user_profile = self.user_profiles[user_id]
        recommendations = await self._get_consciousness_recommendations(user_id)
        
        template = self.jinja_env.get_template('dashboard.html')
        return web.Response(
            text=template.render(
                user=user_profile,
                recommendations=recommendations,
                modules=self.security_modules
            ),
            content_type='text/html'
        )


async def main():
    """Main entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    tutor = ConsciousnessAwareSecurityTutor()
    await tutor.start()


    async def start_session(self, request):
        """Start a new learning session"""
        try:
            data = await request.json()
            user_id = data['user_id']
            module_id = data['module_id']
            
            if user_id not in self.user_profiles:
                return web.json_response({"status": "error", "message": "User not found"}, status=404)
            
            if module_id not in self.security_modules:
                return web.json_response({"status": "error", "message": "Module not found"}, status=404)
            
            session_id = f"session_{user_id}_{module_id}_{int(datetime.utcnow().timestamp())}"
            
            session = LearningSession(
                session_id=session_id,
                user_id=user_id,
                module_id=module_id,
                start_time=datetime.utcnow(),
                end_time=None,
                attention_level=0.5,
                engagement_score=0.0,
                completion_rate=0.0,
                mistakes_made=0,
                time_spent=0,
                consciousness_feedback={}
            )
            
            self.active_sessions[session_id] = session
            
            return web.json_response({
                "status": "success",
                "session_id": session_id,
                "module": asdict(self.security_modules[module_id])
            })
            
        except Exception as e:
            return web.json_response({"status": "error", "message": str(e)}, status=400)
    
    async def update_session(self, request):
        """Update learning session progress"""
        try:
            session_id = request.match_info['session_id']
            data = await request.json()
            
            if session_id not in self.active_sessions:
                return web.json_response({"status": "error", "message": "Session not found"}, status=404)
            
            session = self.active_sessions[session_id]
            
            # Update session data
            if 'attention_level' in data:
                session.attention_level = data['attention_level']
            if 'engagement_score' in data:
                session.engagement_score = data['engagement_score']
            if 'completion_rate' in data:
                session.completion_rate = data['completion_rate']
            if 'mistakes_made' in data:
                session.mistakes_made = data['mistakes_made']
            
            session.time_spent = int((datetime.utcnow() - session.start_time).total_seconds())
            
            return web.json_response({"status": "success", "session": asdict(session)})
            
        except Exception as e:
            return web.json_response({"status": "error", "message": str(e)}, status=400)
    
    async def complete_session(self, request):
        """Complete a learning session"""
        try:
            session_id = request.match_info['session_id']
            data = await request.json()
            
            if session_id not in self.active_sessions:
                return web.json_response({"status": "error", "message": "Session not found"}, status=404)
            
            session = self.active_sessions[session_id]
            session.end_time = datetime.utcnow()
            session.completion_rate = data.get('completion_rate', session.completion_rate)
            
            # Update user profile
            user_profile = self.user_profiles[session.user_id]
            
            if session.completion_rate >= 0.8:  # 80% completion threshold
                if session.module_id not in user_profile.completed_modules:
                    user_profile.completed_modules.append(session.module_id)
                    user_profile.current_streak += 1
                
                # Calculate score based on performance
                score = int(session.completion_rate * 100 * (1 - session.mistakes_made * 0.1))
                user_profile.total_score += max(0, score)
            
            user_profile.last_active = datetime.utcnow()
            
            # Remove from active sessions
            completed_session = self.active_sessions.pop(session_id)
            
            return web.json_response({
                "status": "success",
                "session": asdict(completed_session),
                "user_progress": {
                    "completed_modules": len(user_profile.completed_modules),
                    "current_streak": user_profile.current_streak,
                    "total_score": user_profile.total_score
                }
            })
            
        except Exception as e:
            return web.json_response({"status": "error", "message": str(e)}, status=400)
    
    async def get_consciousness_insights(self, request):
        """Get consciousness insights for a user"""
        user_id = request.match_info['user_id']
        
        if user_id not in self.user_profiles:
            return web.json_response({"status": "error", "message": "User not found"}, status=404)
        
        user_profile = self.user_profiles[user_id]
        
        return web.json_response({
            "status": "success",
            "user_id": user_id,
            "insights": user_profile.consciousness_insights,
            "last_updated": user_profile.last_active.isoformat()
        })
    
    async def learning_interface(self, request):
        """Learning interface for a specific module"""
        module_id = request.match_info['module_id']
        
        if module_id not in self.security_modules:
            return web.Response(text="Module not found", status=404)
        
        module = self.security_modules[module_id]
        template = self.jinja_env.get_template('learning.html')
        
        return web.Response(
            text=template.render(module=module),
            content_type='text/html'
        )
    
    async def user_profile_page(self, request):
        """User profile page"""
        user_id = request.match_info['user_id']
        
        if user_id not in self.user_profiles:
            return web.Response(text="User not found", status=404)
        
        user_profile = self.user_profiles[user_id]
        template = self.jinja_env.get_template('profile.html')
        
        return web.Response(
            text=template.render(user=user_profile),
            content_type='text/html'
        )


if __name__ == "__main__":
    asyncio.run(main())