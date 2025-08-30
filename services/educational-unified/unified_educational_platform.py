#!/usr/bin/env python3
"""
Syn_OS Unified Educational Platform
Combined platform integration service + consciousness-aware GUI framework
Consolidates educational-platform + gui-framework functionality
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable
import aiohttp
import aiofiles
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import sqlite3
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import threading
import time

# GUI components (Qt-based for desktop interface)
try:
    import qasync
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtCharts import *
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    QT_AVAILABLE = True
except ImportError:
    logger = logging.getLogger('educational-unified')
    logger.warning("Qt dependencies not available, GUI framework disabled")
    QT_AVAILABLE = False

# Logging setup
log_dir = Path('/app/logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / 'educational-unified.log')
    ]
)
logger = logging.getLogger('educational-unified')

class Platform(Enum):
    """Supported educational platforms"""
    FREECODECAMP = "freecodecamp"
    BOOTDEV = "bootdev"
    LEETCODE = "leetcode"
    TRYHACKME = "tryhackme"
    HACKTHEBOX = "hackthebox"
    OVERTHEWIRE = "overthewire"

class DifficultyLevel(Enum):
    """Learning difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class LearningSession:
    """Educational learning session"""
    session_id: str
    user_id: str
    platform: Platform
    challenge_id: str
    difficulty: DifficultyLevel
    start_time: datetime
    end_time: Optional[datetime] = None
    score: Optional[float] = None
    consciousness_enhancement: float = 0.0
    learning_metrics: Dict[str, Any] = None

@dataclass
class ConsciousnessMetrics:
    """Consciousness metrics for GUI adaptation"""
    level: float
    learning_rate: float
    adaptation_factor: float
    user_engagement: float
    interface_efficiency: float
    timestamp: str

@dataclass
class GUIComponent:
    """GUI component with consciousness enhancement"""
    component_id: str
    component_type: str
    title: str
    widget: Any  # QWidget when available
    consciousness_adaptation: Dict[str, Any]
    usage_metrics: Dict[str, Any]

class ConsciousnessAdaptiveTheme:
    """Adaptive theme system based on consciousness metrics"""
    
    def __init__(self):
        self.themes = {
            'beginner': {
                'primary_color': '#4CAF50',
                'secondary_color': '#81C784',
                'accent_color': '#FFC107',
                'text_color': '#333333',
                'background_color': '#F5F5F5'
            },
            'intermediate': {
                'primary_color': '#2196F3',
                'secondary_color': '#64B5F6',
                'accent_color': '#FF9800',
                'text_color': '#212121',
                'background_color': '#FAFAFA'
            },
            'advanced': {
                'primary_color': '#9C27B0',
                'secondary_color': '#BA68C8',
                'accent_color': '#E91E63',
                'text_color': '#000000',
                'background_color': '#FFFFFF'
            },
            'consciousness': {
                'primary_color': '#FF5722',
                'secondary_color': '#FF8A65',
                'accent_color': '#795548',
                'text_color': '#FFFFFF',
                'background_color': '#263238'
            }
        }
    
    def get_theme_for_consciousness_level(self, consciousness_level: float) -> Dict[str, str]:
        """Get adaptive theme based on consciousness level"""
        if consciousness_level < 0.3:
            return self.themes['beginner']
        elif consciousness_level < 0.6:
            return self.themes['intermediate']
        elif consciousness_level < 0.9:
            return self.themes['advanced']
        else:
            return self.themes['consciousness']

class UnifiedEducationalPlatform:
    """Unified educational platform combining API services and GUI framework"""
    
    def __init__(self):
        # Platform integration components
        self.platform_clients = {}
        self.learning_sessions = {}
        self.user_progress = {}
        
        # GUI framework components
        self.gui_components = {}
        self.adaptive_theme = ConsciousnessAdaptiveTheme()
        self.qt_app = None
        self.main_window = None
        
        # Consciousness integration
        self.consciousness_metrics = ConsciousnessMetrics(
            level=0.5,
            learning_rate=0.1,
            adaptation_factor=0.2,
            user_engagement=0.7,
            interface_efficiency=0.8,
            timestamp=datetime.now().isoformat()
        )
        
        # WebSocket connections for real-time updates
        self.connected_clients = set()
        
        # Database setup
        self.setup_database()
        
    def setup_database(self):
        """Initialize SQLite database for learning progress"""
        db_dir = Path('/app/data')
        db_dir.mkdir(exist_ok=True)
        
        self.db_path = db_dir / 'educational_progress.db'
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS learning_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    challenge_id TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    score REAL,
                    consciousness_enhancement REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_progress (
                    user_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    total_challenges INTEGER DEFAULT 0,
                    completed_challenges INTEGER DEFAULT 0,
                    average_score REAL DEFAULT 0.0,
                    consciousness_level REAL DEFAULT 0.5,
                    last_activity TEXT,
                    PRIMARY KEY (user_id, platform)
                )
            ''')
            
            conn.commit()
    
    async def initialize_platform_clients(self):
        """Initialize API clients for educational platforms"""
        logger.info("Initializing educational platform clients...")
        
        # HTTP session for API calls
        self.http_session = aiohttp.ClientSession()
        
        # Platform configurations
        self.platform_configs = {
            Platform.FREECODECAMP: {
                'base_url': 'https://api.freecodecamp.org',
                'enabled': True
            },
            Platform.TRYHACKME: {
                'base_url': 'https://tryhackme.com/api',
                'enabled': bool(os.getenv('TRYHACKME_API_KEY'))
            },
            Platform.HACKTHEBOX: {
                'base_url': 'https://www.hackthebox.com/api',
                'enabled': bool(os.getenv('HACKTHEBOX_API_KEY'))
            },
            Platform.LEETCODE: {
                'base_url': 'https://leetcode.com/api',
                'enabled': True
            },
            Platform.BOOTDEV: {
                'base_url': 'https://api.boot.dev',
                'enabled': bool(os.getenv('BOOTDEV_API_KEY'))
            },
            Platform.OVERTHEWIRE: {
                'base_url': 'https://overthewire.org/api',
                'enabled': True
            }
        }
        
        logger.info(f"Platform clients initialized: {sum(1 for config in self.platform_configs.values() if config['enabled'])} platforms enabled")
    
    async def get_challenges_from_platform(self, platform: Platform, difficulty: DifficultyLevel = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get challenges from specific platform"""
        config = self.platform_configs.get(platform)
        if not config or not config['enabled']:
            return []
        
        try:
            # Platform-specific implementations
            if platform == Platform.FREECODECAMP:
                return await self._get_freecodecamp_challenges(limit)
            elif platform == Platform.TRYHACKME:
                return await self._get_tryhackme_challenges(difficulty, limit)
            elif platform == Platform.HACKTHEBOX:
                return await self._get_hackthebox_challenges(difficulty, limit)
            elif platform == Platform.LEETCODE:
                return await self._get_leetcode_challenges(difficulty, limit)
            else:
                return self._generate_mock_challenges(platform, difficulty, limit)
                
        except Exception as e:
            logger.error(f"Error fetching challenges from {platform.value}: {e}")
            return []
    
    async def _get_freecodecamp_challenges(self, limit: int) -> List[Dict[str, Any]]:
        """Get FreeCodeCamp challenges"""
        # Simplified implementation - would need actual FreeCodeCamp API
        return [
            {
                'id': f'fcc_{i}',
                'title': f'FreeCodeCamp Challenge {i}',
                'description': f'Web development challenge focusing on practical skills',
                'difficulty': DifficultyLevel.BEGINNER.value if i <= 3 else DifficultyLevel.INTERMEDIATE.value,
                'platform': Platform.FREECODECAMP.value,
                'tags': ['web-development', 'javascript', 'html', 'css'],
                'estimated_time': 30 + (i * 15),
                'consciousness_enhancement': 0.1 + (i * 0.05)
            }
            for i in range(1, min(limit + 1, 11))
        ]
    
    async def _get_tryhackme_challenges(self, difficulty: DifficultyLevel, limit: int) -> List[Dict[str, Any]]:
        """Get TryHackMe challenges"""
        return [
            {
                'id': f'thm_{i}',
                'title': f'TryHackMe Room {i}',
                'description': f'Cybersecurity challenge with hands-on experience',
                'difficulty': difficulty.value if difficulty else DifficultyLevel.INTERMEDIATE.value,
                'platform': Platform.TRYHACKME.value,
                'tags': ['cybersecurity', 'penetration-testing', 'linux'],
                'estimated_time': 45 + (i * 20),
                'consciousness_enhancement': 0.15 + (i * 0.07)
            }
            for i in range(1, min(limit + 1, 11))
        ]
    
    async def _get_hackthebox_challenges(self, difficulty: DifficultyLevel, limit: int) -> List[Dict[str, Any]]:
        """Get HackTheBox challenges"""
        return [
            {
                'id': f'htb_{i}',
                'title': f'HackTheBox Machine {i}',
                'description': f'Advanced penetration testing challenge',
                'difficulty': difficulty.value if difficulty else DifficultyLevel.ADVANCED.value,
                'platform': Platform.HACKTHEBOX.value,
                'tags': ['pentesting', 'privilege-escalation', 'network-security'],
                'estimated_time': 90 + (i * 30),
                'consciousness_enhancement': 0.2 + (i * 0.1)
            }
            for i in range(1, min(limit + 1, 6))
        ]
    
    async def _get_leetcode_challenges(self, difficulty: DifficultyLevel, limit: int) -> List[Dict[str, Any]]:
        """Get LeetCode challenges"""
        return [
            {
                'id': f'lc_{i}',
                'title': f'Algorithm Challenge {i}',
                'description': f'Programming algorithm and data structure problem',
                'difficulty': difficulty.value if difficulty else DifficultyLevel.INTERMEDIATE.value,
                'platform': Platform.LEETCODE.value,
                'tags': ['algorithms', 'data-structures', 'programming'],
                'estimated_time': 25 + (i * 10),
                'consciousness_enhancement': 0.12 + (i * 0.06)
            }
            for i in range(1, min(limit + 1, 11))
        ]
    
    def _generate_mock_challenges(self, platform: Platform, difficulty: DifficultyLevel, limit: int) -> List[Dict[str, Any]]:
        """Generate mock challenges for testing"""
        return [
            {
                'id': f'{platform.value}_{i}',
                'title': f'{platform.value.title()} Challenge {i}',
                'description': f'Educational challenge from {platform.value}',
                'difficulty': difficulty.value if difficulty else DifficultyLevel.BEGINNER.value,
                'platform': platform.value,
                'tags': ['education', 'learning'],
                'estimated_time': 30,
                'consciousness_enhancement': 0.1
            }
            for i in range(1, min(limit + 1, 6))
        ]
    
    async def start_learning_session(self, user_id: str, platform: Platform, challenge_id: str, difficulty: DifficultyLevel) -> str:
        """Start a new learning session"""
        session_id = hashlib.md5(f"{user_id}_{platform.value}_{challenge_id}_{datetime.now().isoformat()}".encode()).hexdigest()
        
        session = LearningSession(
            session_id=session_id,
            user_id=user_id,
            platform=platform,
            challenge_id=challenge_id,
            difficulty=difficulty,
            start_time=datetime.now(),
            learning_metrics={}
        )
        
        self.learning_sessions[session_id] = session
        
        # Save to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO learning_sessions 
                (session_id, user_id, platform, challenge_id, difficulty, start_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session_id, user_id, platform.value, challenge_id, 
                difficulty.value, session.start_time.isoformat()
            ))
            conn.commit()
        
        # Update consciousness metrics
        await self._update_consciousness_for_learning_start(session)
        
        logger.info(f"Started learning session {session_id} for user {user_id}")
        return session_id
    
    async def complete_learning_session(self, session_id: str, score: float, completion_metrics: Dict[str, Any] = None) -> Dict[str, Any]:
        """Complete a learning session with results"""
        if session_id not in self.learning_sessions:
            raise ValueError(f"Learning session {session_id} not found")
        
        session = self.learning_sessions[session_id]
        session.end_time = datetime.now()
        session.score = score
        session.learning_metrics = completion_metrics or {}
        
        # Calculate consciousness enhancement
        session.consciousness_enhancement = self._calculate_consciousness_enhancement(session, score, completion_metrics)
        
        # Update database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE learning_sessions 
                SET end_time = ?, score = ?, consciousness_enhancement = ?
                WHERE session_id = ?
            ''', (
                session.end_time.isoformat(), score, 
                session.consciousness_enhancement, session_id
            ))
            
            # Update user progress
            self._update_user_progress_db(conn, session)
            conn.commit()
        
        # Update consciousness metrics
        await self._update_consciousness_for_learning_completion(session)
        
        # Broadcast update to connected clients
        await self._broadcast_session_update(session)
        
        result = {
            'session_id': session_id,
            'duration': (session.end_time - session.start_time).total_seconds(),
            'score': score,
            'consciousness_enhancement': session.consciousness_enhancement,
            'new_consciousness_level': self.consciousness_metrics.level
        }
        
        logger.info(f"Completed learning session {session_id} with score {score}")
        return result
    
    def _calculate_consciousness_enhancement(self, session: LearningSession, score: float, metrics: Dict[str, Any]) -> float:
        """Calculate consciousness enhancement based on session performance"""
        base_enhancement = 0.1
        
        # Score factor (0.0 to 1.0 multiplier)
        score_factor = min(score / 100.0, 1.0) if score else 0.5
        
        # Difficulty factor
        difficulty_factors = {
            DifficultyLevel.BEGINNER: 1.0,
            DifficultyLevel.INTERMEDIATE: 1.5,
            DifficultyLevel.ADVANCED: 2.0,
            DifficultyLevel.EXPERT: 3.0
        }
        difficulty_factor = difficulty_factors.get(session.difficulty, 1.0)
        
        # Time factor (bonus for quick completion, penalty for giving up early)
        duration = (session.end_time - session.start_time).total_seconds()
        time_factor = min(max(duration / 3600.0, 0.1), 2.0)  # 0.1 to 2.0 range
        
        enhancement = base_enhancement * score_factor * difficulty_factor * time_factor
        return min(enhancement, 0.5)  # Cap at 0.5 enhancement per session
    
    def _update_user_progress_db(self, conn, session: LearningSession):
        """Update user progress in database"""
        conn.execute('''
            INSERT OR REPLACE INTO user_progress 
            (user_id, platform, total_challenges, completed_challenges, average_score, consciousness_level, last_activity)
            VALUES (?, ?, 
                COALESCE((SELECT total_challenges FROM user_progress WHERE user_id = ? AND platform = ?), 0) + 1,
                COALESCE((SELECT completed_challenges FROM user_progress WHERE user_id = ? AND platform = ?), 0) + 1,
                (COALESCE((SELECT average_score FROM user_progress WHERE user_id = ? AND platform = ?), 0) + ?) / 2,
                ?,
                ?
            )
        ''', (
            session.user_id, session.platform.value,
            session.user_id, session.platform.value,
            session.user_id, session.platform.value,
            session.user_id, session.platform.value, session.score or 0,
            self.consciousness_metrics.level,
            session.end_time.isoformat()
        ))
    
    async def _update_consciousness_for_learning_start(self, session: LearningSession):
        """Update consciousness metrics when learning starts"""
        self.consciousness_metrics.user_engagement = min(1.0, self.consciousness_metrics.user_engagement + 0.1)
        self.consciousness_metrics.timestamp = datetime.now().isoformat()
    
    async def _update_consciousness_for_learning_completion(self, session: LearningSession):
        """Update consciousness metrics when learning completes"""
        if session.consciousness_enhancement:
            self.consciousness_metrics.level = min(1.0, self.consciousness_metrics.level + session.consciousness_enhancement)
            self.consciousness_metrics.learning_rate = min(1.0, self.consciousness_metrics.learning_rate + 0.05)
        
        self.consciousness_metrics.timestamp = datetime.now().isoformat()
    
    async def _broadcast_session_update(self, session: LearningSession):
        """Broadcast session update to connected WebSocket clients"""
        if not self.connected_clients:
            return
        
        update_data = {
            'type': 'learning_session_update',
            'session': asdict(session),
            'consciousness_metrics': asdict(self.consciousness_metrics)
        }
        
        disconnected_clients = set()
        for client in self.connected_clients.copy():
            try:
                await client.send_text(json.dumps(update_data, default=str))
            except Exception as e:
                logger.warning(f"Failed to send update to client: {e}")
                disconnected_clients.add(client)
        
        self.connected_clients -= disconnected_clients
    
    def initialize_gui_framework(self):
        """Initialize Qt-based GUI framework (if available)"""
        if not QT_AVAILABLE:
            logger.warning("Qt not available, GUI framework disabled")
            return
        
        try:
            self.qt_app = QApplication(sys.argv)
            self.main_window = self._create_main_window()
            logger.info("Qt GUI framework initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GUI framework: {e}")
    
    def _create_main_window(self):
        """Create main Qt application window"""
        if not QT_AVAILABLE:
            return None
        
        window = QMainWindow()
        window.setWindowTitle("Syn_OS Educational Platform")
        window.setGeometry(100, 100, 1200, 800)
        
        # Apply consciousness-adaptive theme
        theme = self.adaptive_theme.get_theme_for_consciousness_level(self.consciousness_metrics.level)
        self._apply_theme_to_window(window, theme)
        
        # Create central widget with tabs
        central_widget = QTabWidget()
        
        # Dashboard tab
        dashboard_tab = self._create_dashboard_tab()
        central_widget.addTab(dashboard_tab, "Dashboard")
        
        # Platforms tab
        platforms_tab = self._create_platforms_tab()
        central_widget.addTab(platforms_tab, "Learning Platforms")
        
        # Progress tab
        progress_tab = self._create_progress_tab()
        central_widget.addTab(progress_tab, "Learning Progress")
        
        # Consciousness tab
        consciousness_tab = self._create_consciousness_tab()
        central_widget.addTab(consciousness_tab, "Consciousness Metrics")
        
        window.setCentralWidget(central_widget)
        return window
    
    def _apply_theme_to_window(self, window, theme: Dict[str, str]):
        """Apply consciousness-adaptive theme to Qt window"""
        if not QT_AVAILABLE:
            return
        
        style_sheet = f"""
        QMainWindow {{
            background-color: {theme['background_color']};
            color: {theme['text_color']};
        }}
        QTabWidget::pane {{
            border: 2px solid {theme['secondary_color']};
            background-color: {theme['background_color']};
        }}
        QTabBar::tab {{
            background-color: {theme['primary_color']};
            color: {theme['text_color']};
            padding: 8px 16px;
            margin: 2px;
        }}
        QTabBar::tab:selected {{
            background-color: {theme['accent_color']};
        }}
        QPushButton {{
            background-color: {theme['primary_color']};
            color: {theme['text_color']};
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: {theme['secondary_color']};
        }}
        """
        
        window.setStyleSheet(style_sheet)
    
    def _create_dashboard_tab(self):
        """Create dashboard tab widget"""
        if not QT_AVAILABLE:
            return None
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Consciousness level display
        consciousness_label = QLabel(f"Consciousness Level: {self.consciousness_metrics.level:.2f}")
        consciousness_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(consciousness_label)
        
        # Learning metrics
        metrics_group = QGroupBox("Learning Metrics")
        metrics_layout = QGridLayout()
        
        metrics_layout.addWidget(QLabel("Learning Rate:"), 0, 0)
        metrics_layout.addWidget(QLabel(f"{self.consciousness_metrics.learning_rate:.2f}"), 0, 1)
        
        metrics_layout.addWidget(QLabel("User Engagement:"), 1, 0)
        metrics_layout.addWidget(QLabel(f"{self.consciousness_metrics.user_engagement:.2f}"), 1, 1)
        
        metrics_layout.addWidget(QLabel("Interface Efficiency:"), 2, 0)
        metrics_layout.addWidget(QLabel(f"{self.consciousness_metrics.interface_efficiency:.2f}"), 2, 1)
        
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_platforms_tab(self):
        """Create platforms tab widget"""
        if not QT_AVAILABLE:
            return None
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Platform selection
        platform_group = QGroupBox("Available Platforms")
        platform_layout = QVBoxLayout()
        
        for platform in Platform:
            config = self.platform_configs.get(platform, {})
            enabled = config.get('enabled', False)
            
            platform_btn = QPushButton(f"{platform.value.title()} {'(Enabled)' if enabled else '(Disabled)'}")
            platform_btn.setEnabled(enabled)
            if enabled:
                platform_btn.clicked.connect(lambda p=platform: self._show_platform_challenges(p))
            
            platform_layout.addWidget(platform_btn)
        
        platform_group.setLayout(platform_layout)
        layout.addWidget(platform_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_progress_tab(self):
        """Create progress tracking tab"""
        if not QT_AVAILABLE:
            return None
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        progress_label = QLabel("Learning Progress")
        progress_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(progress_label)
        
        # Progress visualization would go here
        # For now, just a placeholder
        progress_text = QTextEdit()
        progress_text.setReadOnly(True)
        progress_text.setText("Learning progress visualization will be displayed here...")
        layout.addWidget(progress_text)
        
        widget.setLayout(layout)
        return widget
    
    def _create_consciousness_tab(self):
        """Create consciousness metrics visualization tab"""
        if not QT_AVAILABLE:
            return None
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        consciousness_label = QLabel("Consciousness Metrics Visualization")
        consciousness_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(consciousness_label)
        
        # Consciousness visualization would go here
        consciousness_text = QTextEdit()
        consciousness_text.setReadOnly(True)
        consciousness_text.setText("Real-time consciousness evolution visualization will be displayed here...")
        layout.addWidget(consciousness_text)
        
        widget.setLayout(layout)
        return widget
    
    def _show_platform_challenges(self, platform: Platform):
        """Show challenges for selected platform"""
        logger.info(f"Showing challenges for platform: {platform.value}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'service_name': 'unified-educational-platform',
            'version': '1.0.0',
            'status': 'operational',
            'platforms_enabled': sum(1 for config in self.platform_configs.values() if config.get('enabled', False)),
            'total_platforms': len(Platform),
            'active_sessions': len(self.learning_sessions),
            'consciousness_metrics': asdict(self.consciousness_metrics),
            'gui_framework_available': QT_AVAILABLE,
            'connected_clients': len(self.connected_clients),
            'timestamp': datetime.now().isoformat()
        }

# Initialize unified educational platform
educational_platform = UnifiedEducationalPlatform()

# FastAPI app
app = FastAPI(
    title="Syn_OS Unified Educational Platform",
    description="Combined educational platform integration and consciousness-aware GUI framework",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
static_dir = Path("static")
templates_dir = Path("templates")

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
if templates_dir.exists():
    templates = Jinja2Templates(directory=templates_dir)

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info("Starting Syn_OS Unified Educational Platform...")
    await educational_platform.initialize_platform_clients()
    
    # Initialize GUI framework in separate thread if available
    if QT_AVAILABLE:
        gui_thread = threading.Thread(target=educational_platform.initialize_gui_framework, daemon=True)
        gui_thread.start()
    
    logger.info("Unified Educational Platform started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Unified Educational Platform...")
    if hasattr(educational_platform, 'http_session'):
        await educational_platform.http_session.close()

# API Endpoints
@app.get("/api/v1/platforms")
async def list_platforms():
    """List available educational platforms"""
    return {
        'platforms': [
            {
                'name': platform.value,
                'enabled': educational_platform.platform_configs[platform].get('enabled', False),
                'description': f"Educational platform: {platform.value.title()}"
            }
            for platform in Platform
        ]
    }

@app.get("/api/v1/challenges/{platform}")
async def get_platform_challenges(platform: str, difficulty: str = None, limit: int = 10):
    """Get challenges from specific platform"""
    try:
        platform_enum = Platform(platform.lower())
        difficulty_enum = DifficultyLevel(difficulty.lower()) if difficulty else None
        
        challenges = await educational_platform.get_challenges_from_platform(platform_enum, difficulty_enum, limit)
        return {'challenges': challenges}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid platform or difficulty: {str(e)}")

@app.post("/api/v1/sessions/start")
async def start_learning_session(
    user_id: str,
    platform: str,
    challenge_id: str,
    difficulty: str = "intermediate"
):
    """Start a new learning session"""
    try:
        platform_enum = Platform(platform.lower())
        difficulty_enum = DifficultyLevel(difficulty.lower())
        
        session_id = await educational_platform.start_learning_session(
            user_id, platform_enum, challenge_id, difficulty_enum
        )
        
        return {'session_id': session_id, 'status': 'started'}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/sessions/{session_id}/complete")
async def complete_learning_session(
    session_id: str,
    score: float,
    completion_metrics: Dict[str, Any] = None
):
    """Complete a learning session"""
    try:
        result = await educational_platform.complete_learning_session(
            session_id, score, completion_metrics
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/v1/consciousness/metrics")
async def get_consciousness_metrics():
    """Get current consciousness metrics"""
    return asdict(educational_platform.consciousness_metrics)

@app.get("/api/v1/status")
async def system_status():
    """Get system status"""
    return educational_platform.get_system_status()

# WebSocket endpoint for real-time updates
@app.websocket("/ws/education")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time educational updates"""
    await websocket.accept()
    educational_platform.connected_clients.add(websocket)
    
    try:
        # Send initial data
        await websocket.send_text(json.dumps({
            'type': 'connection_established',
            'consciousness_metrics': asdict(educational_platform.consciousness_metrics),
            'active_sessions': len(educational_platform.learning_sessions)
        }, default=str))
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        educational_platform.connected_clients.discard(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        educational_platform.connected_clients.discard(websocket)

# Dashboard web interface
@app.get("/", response_class=HTMLResponse)
async def education_dashboard(request=None):
    """Educational platform dashboard"""
    return HTMLResponse("""
    <html>
    <head><title>Syn_OS Educational Platform</title></head>
    <body>
    <h1>Syn_OS Unified Educational Platform</h1>
    <h2>Consciousness-Enhanced Learning</h2>
    <div id="platform-status">Loading...</div>
    <div id="consciousness-metrics">Loading...</div>
    <script>
    async function updateDashboard() {
        try {
            const [statusResponse, metricsResponse] = await Promise.all([
                fetch('/api/v1/status'),
                fetch('/api/v1/consciousness/metrics')
            ]);
            
            const status = await statusResponse.json();
            const metrics = await metricsResponse.json();
            
            document.getElementById('platform-status').innerHTML = `
                <h3>Platform Status</h3>
                <p>Active Platforms: ${status.platforms_enabled}/${status.total_platforms}</p>
                <p>Active Sessions: ${status.active_sessions}</p>
                <p>GUI Available: ${status.gui_framework_available ? 'Yes' : 'No'}</p>
            `;
            
            document.getElementById('consciousness-metrics').innerHTML = `
                <h3>Consciousness Metrics</h3>
                <p>Level: ${metrics.level.toFixed(2)}</p>
                <p>Learning Rate: ${metrics.learning_rate.toFixed(2)}</p>
                <p>User Engagement: ${metrics.user_engagement.toFixed(2)}</p>
                <p>Interface Efficiency: ${metrics.interface_efficiency.toFixed(2)}</p>
            `;
            
        } catch (error) {
            console.error('Dashboard update error:', error);
        }
    }
    updateDashboard();
    setInterval(updateDashboard, 5000);
    </script>
    </body>
    </html>
    """)

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "unified-educational-platform",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    logger.info("Starting Syn_OS Unified Educational Platform...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8081,
        log_level="info",
        access_log=True
    )