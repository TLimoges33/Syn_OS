#!/usr/bin/env python3
"""
Syn_OS Multi-Platform Learning Hub

A consciousness-aware unified learning ecosystem that integrates with:
- FreeCodeCamp (Web Development)
- Boot.dev (Backend Development) 
- HackTheBox (Penetration Testing)
- TryHackMe (Cybersecurity)
- LeetCode (Algorithms & Data Structures)
- OverTheWire (Linux & Security Fundamentals)
- School LMS Integration (Academic Curriculum)

This system provides AI-powered learning guidance, cross-platform progress tracking,
and adaptive curriculum optimization through consciousness-aware analysis.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

# FastAPI and WebSocket imports
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Consciousness system imports
from src.consciousness_v2.bridges.nats_bridge import NATSBridge
from src.consciousness_v2.persistence.user_context_manager import UserContextManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/syn-os/learning-hub.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="Syn_OS Learning Hub",
    description="Consciousness-aware multi-platform learning ecosystem",
    version="1.0.0"
)

# CORS middleware for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8084"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="applications/learning_hub/static"), name="static")
templates = Jinja2Templates(directory="applications/learning_hub/templates")

# Pydantic models for API
class UserProfile(BaseModel):
    user_id: str
    learning_style: Dict[str, Any]
    preferences: Dict[str, Any]
    goals: List[str]

class PlatformProgress(BaseModel):
    platform: str
    user_id: str
    progress_data: Dict[str, Any]
    last_updated: datetime

class LearningRecommendation(BaseModel):
    platform: str
    recommendation_type: str
    content: Dict[str, Any]
    priority: float
    reasoning: str

class StudySchedule(BaseModel):
    user_id: str
    daily_schedule: Dict[str, List[Dict]]
    weekly_goals: Dict[str, Any]
    platform_rotation: List[str]

# Global instances
consciousness_bridge = None
user_context_manager = None
active_websockets: Dict[str, WebSocket] = {}

class LearningHub:
    """Main Learning Hub orchestrator with consciousness integration"""
    
    def __init__(self):
        self.consciousness = None
        self.user_context = None
        self.platforms = {}
        self.analytics = None
        self.curriculum = None
        
    async def initialize(self):
        """Initialize all components"""
        try:
            # Initialize consciousness bridge
            self.consciousness = NATSBridge()
            await self.consciousness.connect()
            
            # Initialize user context manager
            self.user_context = UserContextManager()
            
            # Initialize platform integrations
            await self._initialize_platform_clients()
            
            # Initialize analytics and curriculum engines
            await self._initialize_learning_engines()
            
            logger.info("Learning Hub initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Learning Hub: {e}")
            raise
    
    async def _initialize_platform_clients(self):
        """Initialize all platform integration clients"""
        from .platform_integrations.freecodecamp_client import FreeCodeCampClient
        from .platform_integrations.hackthebox_client import HackTheBoxClient
        from .platform_integrations.leetcode_client import LeetCodeClient
        from .platform_integrations.tryhackme_client import TryHackMeClient
        from .platform_integrations.bootdev_client import BootDevClient
        from .platform_integrations.overthewire_client import OverTheWireClient
        from .platform_integrations.school_lms_client import SchoolLMSClient
        
        self.platforms = {
            "freecodecamp": FreeCodeCampClient(self.consciousness),
            "hackthebox": HackTheBoxClient(self.consciousness),
            "leetcode": LeetCodeClient(self.consciousness),
            "tryhackme": TryHackMeClient(self.consciousness),
            "bootdev": BootDevClient(self.consciousness),
            "overthewire": OverTheWireClient(self.consciousness),
            "school": SchoolLMSClient(self.consciousness)
        }
        
        logger.info(f"Initialized {len(self.platforms)} platform clients")
    
    async def _initialize_learning_engines(self):
        """Initialize learning analytics and curriculum engines"""
        from .analytics.learning_analytics import LearningAnalytics
        from .curriculum.adaptive_curriculum import AdaptiveCurriculum
        
        self.analytics = LearningAnalytics(self.consciousness)
        self.curriculum = AdaptiveCurriculum(self.consciousness)
        
        logger.info("Learning engines initialized")
    
    async def get_unified_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data across all platforms"""
        try:
            # Get platform data
            platform_data = {}
            for platform_name, client in self.platforms.items():
                try:
                    platform_data[platform_name] = await client.get_user_progress(user_id)
                except Exception as e:
                    logger.warning(f"Failed to get {platform_name} data: {e}")
                    platform_data[platform_name] = {"error": str(e), "status": "unavailable"}
            
            # Get consciousness analysis
            consciousness_insights = await self._get_consciousness_insights(user_id, platform_data)
            
            # Get learning recommendations
            recommendations = await self._get_learning_recommendations(user_id, platform_data)
            
            # Get optimized study schedule
            study_schedule = await self._get_study_schedule(user_id)
            
            # Get skill progression analysis
            skill_analysis = await self._get_skill_analysis(user_id, platform_data)
            
            return {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "platforms": platform_data,
                "consciousness_insights": consciousness_insights,
                "recommendations": recommendations,
                "study_schedule": study_schedule,
                "skill_analysis": skill_analysis,
                "learning_velocity": consciousness_insights.get("learning_velocity", 0),
                "overall_progress": self._calculate_overall_progress(platform_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data for {user_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_consciousness_insights(self, user_id: str, platform_data: Dict) -> Dict[str, Any]:
        """Get AI consciousness insights about learning progress"""
        try:
            # Send platform data to consciousness for analysis
            analysis_request = {
                "type": "multi_platform_learning_analysis",
                "user_id": user_id,
                "platform_data": platform_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Publish to consciousness system
            await self.consciousness.publish("learning.analysis.request", analysis_request)
            
            # Wait for consciousness response (with timeout)
            response = await self.consciousness.request_with_timeout(
                "learning.analysis.response", 
                analysis_request, 
                timeout=10.0
            )
            
            if response:
                return response.get("insights", {})
            else:
                # Fallback analysis if consciousness unavailable
                return await self._fallback_analysis(user_id, platform_data)
                
        except Exception as e:
            logger.warning(f"Consciousness analysis failed, using fallback: {e}")
            return await self._fallback_analysis(user_id, platform_data)
    
    async def _fallback_analysis(self, user_id: str, platform_data: Dict) -> Dict[str, Any]:
        """Fallback analysis when consciousness is unavailable"""
        total_platforms = len([p for p in platform_data.values() if "error" not in p])
        active_platforms = len([p for p in platform_data.values() 
                               if "error" not in p and p.get("recent_activity", False)])
        
        return {
            "learning_velocity": min(active_platforms / max(total_platforms, 1) * 100, 100),
            "active_platforms": active_platforms,
            "total_platforms": total_platforms,
            "engagement_level": "moderate" if active_platforms > 2 else "low",
            "recommended_focus": "Increase activity across more platforms",
            "consciousness_status": "offline"
        }
    
    async def _get_learning_recommendations(self, user_id: str, platform_data: Dict) -> List[Dict]:
        """Get personalized learning recommendations"""
        recommendations = []
        
        # Analyze each platform for recommendations
        for platform_name, data in platform_data.items():
            if "error" not in data and platform_name in self.platforms:
                try:
                    platform_recs = await self.platforms[platform_name].get_recommendations(user_id, data)
                    recommendations.extend(platform_recs)
                except Exception as e:
                    logger.warning(f"Failed to get {platform_name} recommendations: {e}")
        
        # Sort by priority and return top recommendations
        recommendations.sort(key=lambda x: x.get("priority", 0), reverse=True)
        return recommendations[:10]  # Top 10 recommendations
    
    async def _get_study_schedule(self, user_id: str) -> Dict[str, Any]:
        """Get AI-optimized study schedule"""
        try:
            if self.curriculum:
                return await self.curriculum.get_optimal_schedule(user_id)
            else:
                return self._default_study_schedule()
        except Exception as e:
            logger.warning(f"Failed to get study schedule: {e}")
            return self._default_study_schedule()
    
    def _default_study_schedule(self) -> Dict[str, Any]:
        """Default study schedule when AI optimization unavailable"""
        return {
            "daily_schedule": {
                "morning": [{"platform": "leetcode", "duration": 30, "focus": "algorithms"}],
                "afternoon": [{"platform": "freecodecamp", "duration": 60, "focus": "web_dev"}],
                "evening": [{"platform": "hackthebox", "duration": 45, "focus": "security"}]
            },
            "weekly_goals": {
                "leetcode_problems": 10,
                "fcc_projects": 1,
                "htb_machines": 2,
                "thm_rooms": 3
            },
            "platform_rotation": ["leetcode", "freecodecamp", "hackthebox", "tryhackme"]
        }
    
    async def _get_skill_analysis(self, user_id: str, platform_data: Dict) -> Dict[str, Any]:
        """Analyze skill development across platforms"""
        skills = {
            "web_development": 0,
            "cybersecurity": 0,
            "algorithms": 0,
            "linux_systems": 0,
            "backend_development": 0
        }
        
        # Map platform progress to skills
        if "freecodecamp" in platform_data and "error" not in platform_data["freecodecamp"]:
            skills["web_development"] = platform_data["freecodecamp"].get("completion_percentage", 0)
        
        if "hackthebox" in platform_data and "error" not in platform_data["hackthebox"]:
            htb_data = platform_data["hackthebox"]
            skills["cybersecurity"] = min((htb_data.get("machines_owned", 0) * 5), 100)
        
        if "leetcode" in platform_data and "error" not in platform_data["leetcode"]:
            lc_data = platform_data["leetcode"]
            skills["algorithms"] = min((lc_data.get("problems_solved", 0) / 10), 100)
        
        if "overthewire" in platform_data and "error" not in platform_data["overthewire"]:
            otw_data = platform_data["overthewire"]
            skills["linux_systems"] = otw_data.get("completion_percentage", 0)
        
        if "bootdev" in platform_data and "error" not in platform_data["bootdev"]:
            bootdev_data = platform_data["bootdev"]
            skills["backend_development"] = bootdev_data.get("completion_percentage", 0)
        
        return {
            "skills": skills,
            "overall_level": sum(skills.values()) / len(skills),
            "strongest_skill": max(skills, key=skills.get),
            "weakest_skill": min(skills, key=skills.get),
            "skill_balance": max(skills.values()) - min(skills.values())
        }
    
    def _calculate_overall_progress(self, platform_data: Dict) -> float:
        """Calculate overall learning progress across all platforms"""
        total_progress = 0
        active_platforms = 0
        
        for platform, data in platform_data.items():
            if "error" not in data:
                progress = data.get("completion_percentage", 0)
                if progress > 0:
                    total_progress += progress
                    active_platforms += 1
        
        return total_progress / max(active_platforms, 1) if active_platforms > 0 else 0
    
    async def sync_platform_data(self, user_id: str, platform: str) -> Dict[str, Any]:
        """Manually sync data from a specific platform"""
        if platform not in self.platforms:
            raise HTTPException(status_code=404, detail=f"Platform {platform} not supported")
        
        try:
            client = self.platforms[platform]
            progress_data = await client.sync_user_progress(user_id)
            
            # Store in user context
            if self.user_context:
                await self.user_context.update_platform_progress(user_id, platform, progress_data)
            
            return {
                "platform": platform,
                "user_id": user_id,
                "sync_status": "success",
                "data": progress_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to sync {platform} data for {user_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Global learning hub instance
learning_hub = LearningHub()

# API Routes
@app.on_event("startup")
async def startup_event():
    """Initialize the learning hub on startup"""
    global learning_hub
    try:
        await learning_hub.initialize()
        logger.info("Learning Hub startup completed successfully")
    except Exception as e:
        logger.error(f"Learning Hub startup failed: {e}")
        # Continue startup even if some components fail
        pass

@app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Serve the main dashboard page"""
    return templates.TemplateResponse("unified_dashboard.html", {"request": {}})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "learning_hub",
        "version": "1.0.0"
    }

@app.get("/api/v1/dashboard/{user_id}")
async def get_dashboard(user_id: str):
    """Get unified dashboard data for a user"""
    return await learning_hub.get_unified_dashboard_data(user_id)

@app.get("/api/v1/platforms/{platform}/progress/{user_id}")
async def get_platform_progress(platform: str, user_id: str):
    """Get progress from a specific platform"""
    if platform not in learning_hub.platforms:
        raise HTTPException(status_code=404, detail=f"Platform {platform} not supported")
    
    try:
        client = learning_hub.platforms[platform]
        progress = await client.get_user_progress(user_id)
        return {
            "platform": platform,
            "user_id": user_id,
            "progress": progress,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/platforms/{platform}/sync/{user_id}")
async def sync_platform(platform: str, user_id: str):
    """Manually sync data from a specific platform"""
    return await learning_hub.sync_platform_data(user_id, platform)

@app.get("/api/v1/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    """Get personalized learning recommendations"""
    dashboard_data = await learning_hub.get_unified_dashboard_data(user_id)
    return {
        "user_id": user_id,
        "recommendations": dashboard_data["recommendations"],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/schedule/{user_id}")
async def get_study_schedule(user_id: str):
    """Get AI-optimized study schedule"""
    dashboard_data = await learning_hub.get_unified_dashboard_data(user_id)
    return {
        "user_id": user_id,
        "schedule": dashboard_data["study_schedule"],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/consciousness/analyze")
async def trigger_consciousness_analysis(user_id: str):
    """Trigger comprehensive consciousness analysis"""
    try:
        dashboard_data = await learning_hub.get_unified_dashboard_data(user_id)
        return {
            "user_id": user_id,
            "analysis_triggered": True,
            "insights": dashboard_data["consciousness_insights"],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time updates
@app.websocket("/ws/learning/{user_id}")
async def learning_websocket(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time learning updates"""
    await websocket.accept()
    active_websockets[user_id] = websocket
    
    try:
        logger.info(f"WebSocket connected for user {user_id}")
        
        # Send initial dashboard data
        initial_data = await learning_hub.get_unified_dashboard_data(user_id)
        await websocket.send_json({
            "type": "initial_data",
            "data": initial_data
        })
        
        # Keep connection alive and send periodic updates
        while True:
            try:
                # Wait for client message or timeout
                message = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                # Handle client requests
                if message == "refresh":
                    updated_data = await learning_hub.get_unified_dashboard_data(user_id)
                    await websocket.send_json({
                        "type": "dashboard_update",
                        "data": updated_data
                    })
                
            except asyncio.TimeoutError:
                # Send periodic updates every 30 seconds
                try:
                    updated_data = await learning_hub.get_unified_dashboard_data(user_id)
                    await websocket.send_json({
                        "type": "periodic_update",
                        "data": updated_data
                    })
                except Exception as e:
                    logger.warning(f"Failed to send periodic update: {e}")
                    break
                    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        if user_id in active_websockets:
            del active_websockets[user_id]

# Utility function to broadcast updates to all connected clients
async def broadcast_update(update_data: Dict[str, Any]):
    """Broadcast update to all connected WebSocket clients"""
    if not active_websockets:
        return
    
    disconnected_clients = []
    
    for user_id, websocket in active_websockets.items():
        try:
            await websocket.send_json({
                "type": "broadcast_update",
                "data": update_data
            })
        except Exception as e:
            logger.warning(f"Failed to send broadcast to {user_id}: {e}")
            disconnected_clients.append(user_id)
    
    # Clean up disconnected clients
    for user_id in disconnected_clients:
        del active_websockets[user_id]

if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8084,
        reload=True,
        log_level="info"
    )
