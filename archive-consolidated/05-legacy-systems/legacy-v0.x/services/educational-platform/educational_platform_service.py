#!/usr/bin/env python3
"""
SynapticOS Educational Platform Integration Service
Multi-platform educational content aggregator with consciousness integration
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import aiohttp
import aiofiles
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import sqlite3
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Logging setup
log_dir = Path('/app/logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / 'educational-platform.log')
    ]
)
logger = logging.getLogger('educational-platform')

class Platform(Enum):
    """Supported educational platforms"""
    FREECODECAMP = "freecodecamp"
    BOOTDEV = "bootdev"
    LEETCODE = "leetcode"
    TRYHACKME = "tryhackme"
    HACKTHEBOX = "hackthebox"
    OVERTHEWIRE = "overthewire"

@dataclass
class LearningProgress:
    """Learning progress tracking"""
    platform: Platform
    user_id: str
    course_id: str
    completion_percentage: float
    last_activity: str
    consciousness_correlation: float
    skill_level: float
    
    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class SkillAssessment:
    """Skill assessment across platforms"""
    skill_name: str
    platforms: List[Platform]
    overall_level: float
    confidence_score: float
    learning_velocity: float
    consciousness_enhancement: float
    recommendations: List[str]

class PlatformIntegrator:
    """Educational platform integration manager"""
    
    def __init__(self):
        self.session = None
        self.api_keys = {}
        self.user_data = {}
        self.db_path = '/var/lib/synapticos/education/learning_progress.db'
        self.consciousness_bridge_url = os.getenv('CONSCIOUSNESS_BRIDGE_URL', 'http://localhost:8082')
        self.load_configurations()
        self.init_database()
    
    def load_configurations(self):
        """Load platform API configurations"""
        try:
            self.api_keys = {
                Platform.FREECODECAMP: os.getenv('FREECODECAMP_API_KEY'),
                Platform.BOOTDEV: os.getenv('BOOTDEV_API_KEY'),
                Platform.LEETCODE: os.getenv('LEETCODE_API_KEY'),
                Platform.TRYHACKME: os.getenv('TRYHACKME_API_KEY'),
                Platform.HACKTHEBOX: os.getenv('HACKTHEBOX_API_KEY'),
                Platform.OVERTHEWIRE: None  # No official API
            }
            
            # Platform endpoints
            self.endpoints = {
                Platform.FREECODECAMP: "https://api.freecodecamp.org",
                Platform.BOOTDEV: "https://api.boot.dev",
                Platform.LEETCODE: "https://leetcode.com/api",
                Platform.TRYHACKME: "https://tryhackme.com/api",
                Platform.HACKTHEBOX: "https://www.hackthebox.eu/api",
            }
            
            logger.info(f"Loaded configurations for {len(self.endpoints)} platforms")
            
        except Exception as e:
            logger.error(f"Failed to load configurations: {e}")
    
    def init_database(self):
        """Initialize SQLite database for progress tracking"""
        try:
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    course_id TEXT NOT NULL,
                    completion_percentage REAL NOT NULL,
                    last_activity TEXT NOT NULL,
                    consciousness_correlation REAL NOT NULL,
                    skill_level REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(platform, user_id, course_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS skill_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_name TEXT NOT NULL,
                    platforms TEXT NOT NULL,
                    overall_level REAL NOT NULL,
                    confidence_score REAL NOT NULL,
                    learning_velocity REAL NOT NULL,
                    consciousness_enhancement REAL NOT NULL,
                    recommendations TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(skill_name)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS platform_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    session_start TEXT NOT NULL,
                    session_end TEXT,
                    activities_completed INTEGER DEFAULT 0,
                    consciousness_level REAL NOT NULL,
                    learning_efficiency REAL NOT NULL,
                    created_at TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def sync_platform_progress(self, platform: Platform, user_id: str) -> List[LearningProgress]:
        """Sync learning progress from platform"""
        try:
            if platform not in self.endpoints:
                raise ValueError(f"Platform {platform} not supported")
            
            # Get current consciousness level
            consciousness_level = await self._get_consciousness_level()
            
            # Platform-specific progress fetching
            progress_data = await self._fetch_platform_progress(platform, user_id)
            
            # Convert to LearningProgress objects
            progress_list = []
            for item in progress_data:
                progress = LearningProgress(
                    platform=platform,
                    user_id=user_id,
                    course_id=item.get('course_id', 'unknown'),
                    completion_percentage=item.get('completion', 0.0),
                    last_activity=item.get('last_activity', datetime.now().isoformat()),
                    consciousness_correlation=consciousness_level * item.get('engagement', 1.0),
                    skill_level=item.get('skill_level', 0.0)
                )
                progress_list.append(progress)
            
            # Store in database
            await self._store_progress(progress_list)
            
            logger.info(f"Synced {len(progress_list)} progress items for {platform.value}")
            return progress_list
            
        except Exception as e:
            logger.error(f"Failed to sync progress for {platform.value}: {e}")
            return []
    
    async def _fetch_platform_progress(self, platform: Platform, user_id: str) -> List[Dict]:
        """Fetch progress from specific platform"""
        if platform == Platform.FREECODECAMP:
            return await self._fetch_freecodecamp_progress(user_id)
        elif platform == Platform.BOOTDEV:
            return await self._fetch_bootdev_progress(user_id)
        elif platform == Platform.LEETCODE:
            return await self._fetch_leetcode_progress(user_id)
        elif platform == Platform.TRYHACKME:
            return await self._fetch_tryhackme_progress(user_id)
        elif platform == Platform.HACKTHEBOX:
            return await self._fetch_hackthebox_progress(user_id)
        elif platform == Platform.OVERTHEWIRE:
            return await self._fetch_overthewire_progress(user_id)
        else:
            return []
    
    async def _fetch_freecodecamp_progress(self, user_id: str) -> List[Dict]:
        """Fetch FreeCodeCamp progress"""
        try:
            # Mock implementation - replace with actual API calls
            return [
                {
                    'course_id': 'responsive-web-design',
                    'completion': 75.0,
                    'last_activity': datetime.now().isoformat(),
                    'engagement': 0.8,
                    'skill_level': 0.75
                },
                {
                    'course_id': 'javascript-algorithms-data-structures',
                    'completion': 45.0,
                    'last_activity': (datetime.now() - timedelta(days=2)).isoformat(),
                    'engagement': 0.9,
                    'skill_level': 0.45
                }
            ]
        except Exception as e:
            logger.error(f"FreeCodeCamp API error: {e}")
            return []
    
    async def _fetch_bootdev_progress(self, user_id: str) -> List[Dict]:
        """Fetch Boot.dev progress"""
        # Mock implementation
        return [
            {
                'course_id': 'learn-go',
                'completion': 60.0,
                'last_activity': datetime.now().isoformat(),
                'engagement': 0.95,
                'skill_level': 0.6
            }
        ]
    
    async def _fetch_leetcode_progress(self, user_id: str) -> List[Dict]:
        """Fetch LeetCode progress"""
        # Mock implementation
        return [
            {
                'course_id': 'algorithms',
                'completion': 30.0,
                'last_activity': datetime.now().isoformat(),
                'engagement': 0.7,
                'skill_level': 0.3
            }
        ]
    
    async def _fetch_tryhackme_progress(self, user_id: str) -> List[Dict]:
        """Fetch TryHackMe progress"""
        # Mock implementation
        return [
            {
                'course_id': 'pre-security',
                'completion': 100.0,
                'last_activity': (datetime.now() - timedelta(days=7)).isoformat(),
                'engagement': 1.0,
                'skill_level': 1.0
            },
            {
                'course_id': 'complete-beginner',
                'completion': 65.0,
                'last_activity': datetime.now().isoformat(),
                'engagement': 0.85,
                'skill_level': 0.65
            }
        ]
    
    async def _fetch_hackthebox_progress(self, user_id: str) -> List[Dict]:
        """Fetch HackTheBox progress"""
        # Mock implementation
        return [
            {
                'course_id': 'starting-point',
                'completion': 40.0,
                'last_activity': datetime.now().isoformat(),
                'engagement': 0.9,
                'skill_level': 0.4
            }
        ]
    
    async def _fetch_overthewire_progress(self, user_id: str) -> List[Dict]:
        """Fetch OverTheWire progress (manual tracking)"""
        # Since OverTheWire has no API, this would be manual entry
        return []
    
    async def _get_consciousness_level(self) -> float:
        """Get current consciousness level from consciousness bridge"""
        try:
            async with self.session.get(f"{self.consciousness_bridge_url}/consciousness/level") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('level', 0.5)
                else:
                    return 0.5  # Default level
        except Exception as e:
            logger.error(f"Failed to get consciousness level: {e}")
            return 0.5
    
    async def _store_progress(self, progress_list: List[LearningProgress]):
        """Store progress in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for progress in progress_list:
                cursor.execute('''
                    INSERT OR REPLACE INTO learning_progress 
                    (platform, user_id, course_id, completion_percentage, last_activity, 
                     consciousness_correlation, skill_level, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    progress.platform.value,
                    progress.user_id,
                    progress.course_id,
                    progress.completion_percentage,
                    progress.last_activity,
                    progress.consciousness_correlation,
                    progress.skill_level,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store progress: {e}")
    
    async def analyze_cross_platform_skills(self, user_id: str) -> List[SkillAssessment]:
        """Analyze skills across all platforms"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all progress for user
            cursor.execute('''
                SELECT platform, course_id, completion_percentage, consciousness_correlation, skill_level
                FROM learning_progress 
                WHERE user_id = ?
            ''', (user_id,))
            
            progress_data = cursor.fetchall()
            conn.close()
            
            # Skill mapping (simplified)
            skill_mapping = {
                'web_development': ['responsive-web-design', 'javascript-algorithms-data-structures'],
                'backend_development': ['learn-go', 'learn-python'],
                'algorithms': ['algorithms', 'leetcode-problems'],
                'cybersecurity': ['pre-security', 'complete-beginner', 'starting-point'],
                'linux': ['linux-fundamentals', 'overthewire-bandit']
            }
            
            assessments = []
            consciousness_level = await self._get_consciousness_level()
            
            for skill, course_ids in skill_mapping.items():
                relevant_progress = [p for p in progress_data if p[1] in course_ids]
                
                if relevant_progress:
                    platforms = list(set([Platform(p[0]) for p in relevant_progress]))
                    overall_level = sum([p[2] for p in relevant_progress]) / len(relevant_progress) / 100.0
                    confidence_score = min(1.0, len(relevant_progress) / 3.0)  # More platforms = higher confidence
                    learning_velocity = sum([p[3] for p in relevant_progress]) / len(relevant_progress)
                    consciousness_enhancement = consciousness_level * overall_level
                    
                    recommendations = await self._generate_skill_recommendations(skill, overall_level, platforms)
                    
                    assessment = SkillAssessment(
                        skill_name=skill,
                        platforms=platforms,
                        overall_level=overall_level,
                        confidence_score=confidence_score,
                        learning_velocity=learning_velocity,
                        consciousness_enhancement=consciousness_enhancement,
                        recommendations=recommendations
                    )
                    assessments.append(assessment)
            
            return assessments
            
        except Exception as e:
            logger.error(f"Failed to analyze cross-platform skills: {e}")
            return []
    
    async def _generate_skill_recommendations(self, skill: str, level: float, platforms: List[Platform]) -> List[str]:
        """Generate skill-specific recommendations"""
        recommendations = []
        
        if level < 0.3:
            recommendations.append(f"Focus on foundational {skill} concepts")
            recommendations.append("Consider starting with beginner-friendly platforms")
        elif level < 0.7:
            recommendations.append(f"Continue building {skill} proficiency")
            recommendations.append("Try intermediate challenges and projects")
        else:
            recommendations.append(f"Excellent {skill} foundation!")
            recommendations.append("Consider advanced challenges and specialization")
        
        # Platform-specific recommendations
        if Platform.TRYHACKME in platforms and skill == 'cybersecurity':
            recommendations.append("Continue TryHackMe learning paths")
        if Platform.LEETCODE in platforms and skill == 'algorithms':
            recommendations.append("Practice daily LeetCode problems")
        
        return recommendations

class EducationalPlatformService:
    """Main educational platform integration service"""
    
    def __init__(self):
        self.integrator = None
        self.running = False
        self.sync_interval = int(os.getenv('SYNC_INTERVAL', '3600'))  # Default 1 hour
        self.user_id = os.getenv('DEFAULT_USER_ID', 'default_user')
    
    async def start_service(self):
        """Start the educational platform service"""
        logger.info("Starting Educational Platform Integration Service")
        self.running = True
        
        async with PlatformIntegrator() as integrator:
            self.integrator = integrator
            
            # Start service loops
            await asyncio.gather(
                self._sync_loop(),
                self._analysis_loop(),
                self._health_check_loop()
            )
    
    async def _sync_loop(self):
        """Periodic platform synchronization"""
        while self.running:
            try:
                logger.info("Starting platform synchronization")
                
                # Sync all platforms
                for platform in Platform:
                    if platform != Platform.OVERTHEWIRE:  # Skip non-API platforms
                        await self.integrator.sync_platform_progress(platform, self.user_id)
                
                logger.info("Platform synchronization completed")
                
            except Exception as e:
                logger.error(f"Sync loop error: {e}")
            
            await asyncio.sleep(self.sync_interval)
    
    async def _analysis_loop(self):
        """Periodic skill analysis"""
        while self.running:
            try:
                assessments = await self.integrator.analyze_cross_platform_skills(self.user_id)
                
                if assessments:
                    logger.info(f"Generated {len(assessments)} skill assessments")
                    
                    # Log skill levels
                    for assessment in assessments:
                        logger.info(f"Skill: {assessment.skill_name}, "
                                  f"Level: {assessment.overall_level:.2f}, "
                                  f"Platforms: {len(assessment.platforms)}")
                
            except Exception as e:
                logger.error(f"Analysis loop error: {e}")
            
            await asyncio.sleep(self.sync_interval * 2)  # Less frequent than sync
    
    async def _health_check_loop(self):
        """Service health monitoring"""
        while self.running:
            try:
                health_status = {
                    'service_running': self.running,
                    'last_sync': datetime.now().isoformat(),
                    'supported_platforms': len(Platform),
                    'sync_interval': self.sync_interval,
                    'user_id': self.user_id
                }
                
                # Write health status
                health_dir = Path('/var/lib/synapticos/health')
                health_dir.mkdir(parents=True, exist_ok=True)
                
                health_file = health_dir / 'educational-platform.json'
                async with aiofiles.open(health_file, 'w') as f:
                    await f.write(json.dumps(health_status, indent=2))
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
            
            await asyncio.sleep(300)  # Every 5 minutes

# FastAPI Application with Lifespan Management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan management"""
    # Startup
    logger.info("Starting Educational Platform API")
    global global_service
    global_service = EducationalPlatformService()
    
    # Start background service
    service_task = asyncio.create_task(global_service.start_service())
    
    yield
    
    # Shutdown
    logger.info("Shutting down Educational Platform API")
    service_task.cancel()
    try:
        await service_task
    except asyncio.CancelledError:
        pass

# FastAPI Application
app = FastAPI(
    title="SynapticOS Educational Platform API",
    description="Consciousness-integrated educational platform with multi-platform support",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instance
global_service: Optional[EducationalPlatformService] = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "educational-platform",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running" if global_service else "starting"
    }

@app.get("/api/stats")
async def get_stats():
    """Get platform statistics"""
    if not global_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    return {
        "platforms_synced": len(global_service.progress_data),
        "last_sync": global_service.last_sync.isoformat() if hasattr(global_service, 'last_sync') else None,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/platforms")
async def get_platforms():
    """Get supported platforms"""
    return {
        "platforms": [
            {"name": platform.value, "description": f"{platform.value.title()} Learning Platform"}
            for platform in Platform
        ],
        "count": len(Platform),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/progress/{user_id}")
async def get_user_progress(user_id: str):
    """Get progress for a specific user"""
    if not global_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        progress = await global_service.sync_user_progress(user_id)
        return {
            "user_id": user_id,
            "progress": [p.to_dict() for p in progress],
            "total_courses": len(progress),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get user progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve progress")

@app.get("/api/skills")
async def get_skill_analysis():
    """Get cross-platform skill analysis"""
    if not global_service:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        # Get sample skills analysis
        skills = await global_service.analyze_cross_platform_skills("sample_user")
        return {
            "skills": [skill.to_dict() for skill in skills],
            "analysis_time": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get skill analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze skills")

if __name__ == "__main__":
    # Create necessary directories
    Path('/app/logs').mkdir(parents=True, exist_ok=True)
    Path('/app/data').mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/app/logs/educational-platform.log')
        ]
    )
    
    # Run FastAPI with uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8084,
        log_level="info",
        access_log=True
    )
