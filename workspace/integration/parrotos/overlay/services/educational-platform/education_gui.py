#!/usr/bin/env python3
"""
SynapticOS Educational Platform GUI
Gamified learning interface with cross-platform achievement tracking
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiofiles
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import aiohttp
import sqlite3
from dataclasses import dataclass, asdict
import hashlib
import secrets

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('education-gui')

# FastAPI app
app = FastAPI(title="SynapticOS Educational Platform", version="2.0.0")

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@dataclass
class Achievement:
    """Achievement data structure"""
    id: str
    name: str
    description: str
    icon: str
    points: int
    category: str
    unlocked: bool = False
    unlock_date: Optional[str] = None

@dataclass
class Badge:
    """Badge data structure"""
    id: str
    name: str
    description: str
    icon: str
    rarity: str  # common, rare, epic, legendary
    requirements: Dict[str, Any]
    earned: bool = False
    earned_date: Optional[str] = None

@dataclass
class UserProfile:
    """User profile with gamification elements"""
    username: str
    level: int
    xp: int
    total_points: int
    achievements: List[Achievement]
    badges: List[Badge]
    learning_streak: int
    favorite_platform: str
    join_date: str
    last_active: str

class GamificationEngine:
    """Gamification system for learning platforms"""
    
    def __init__(self):
        self.db_path = "education_platform.db"
        self.education_service_url = "http://localhost:8084"
        self.consciousness_bridge_url = "http://localhost:8082"
        self.connected_clients = set()
        self.user_sessions = {}
        self.init_database()
        self.init_achievements_and_badges()
    
    def init_database(self):
        """Initialize gamification database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                total_points INTEGER DEFAULT 0,
                learning_streak INTEGER DEFAULT 0,
                favorite_platform TEXT DEFAULT '',
                join_date TEXT DEFAULT CURRENT_TIMESTAMP,
                last_active TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User achievements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_achievements (
                username TEXT,
                achievement_id TEXT,
                unlocked BOOLEAN DEFAULT FALSE,
                unlock_date TEXT,
                PRIMARY KEY (username, achievement_id)
            )
        ''')
        
        # User badges table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_badges (
                username TEXT,
                badge_id TEXT,
                earned BOOLEAN DEFAULT FALSE,
                earned_date TEXT,
                PRIMARY KEY (username, badge_id)
            )
        ''')
        
        # Learning sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                platform TEXT,
                duration INTEGER,
                skills_practiced TEXT,
                xp_gained INTEGER,
                consciousness_correlation REAL,
                session_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def init_achievements_and_badges(self):
        """Initialize default achievements and badges"""
        self.achievements = [
            Achievement("first_steps", "First Steps", "Complete your first lesson", "🎯", 50, "beginner"),
            Achievement("code_warrior", "Code Warrior", "Solve 10 coding problems", "⚔️", 200, "coding"),
            Achievement("security_minded", "Security Minded", "Complete 5 cybersecurity challenges", "🛡️", 300, "security"),
            Achievement("consistent_learner", "Consistent Learner", "Maintain a 7-day learning streak", "📚", 400, "consistency"),
            Achievement("multi_platform", "Platform Explorer", "Learn on 3 different platforms", "🌐", 250, "exploration"),
            Achievement("consciousness_sync", "Consciousness Synced", "Achieve 90%+ consciousness correlation", "🧠", 500, "consciousness"),
            Achievement("night_owl", "Night Owl", "Learn for 2 hours after 10 PM", "🦉", 150, "dedication"),
            Achievement("early_bird", "Early Bird", "Learn for 1 hour before 7 AM", "🐦", 150, "dedication"),
            Achievement("marathon_learner", "Marathon Learner", "Study for 6+ hours in one day", "🏃", 350, "endurance"),
            Achievement("skill_master", "Skill Master", "Reach advanced level in any skill", "🏆", 600, "mastery")
        ]
        
        self.badges = [
            Badge("python_novice", "Python Novice", "Complete Python basics", "🐍", "common", {"python_lessons": 5}),
            Badge("js_ninja", "JavaScript Ninja", "Master JavaScript fundamentals", "🥷", "rare", {"javascript_lessons": 10}),
            Badge("security_expert", "Security Expert", "Complete advanced security course", "🔒", "epic", {"security_lessons": 20}),
            Badge("algorithm_master", "Algorithm Master", "Solve 50 algorithm problems", "🧮", "legendary", {"algorithms_solved": 50}),
            Badge("full_stack", "Full Stack Developer", "Complete both frontend and backend", "📱", "epic", {"frontend_lessons": 10, "backend_lessons": 10}),
            Badge("consciousness_pioneer", "Consciousness Pioneer", "Integrate with AI consciousness system", "🌟", "legendary", {"consciousness_sessions": 10})
        ]
    
    async def get_user_profile(self, username: str) -> UserProfile:
        """Get complete user profile with gamification data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get user data
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        
        if not user_data:
            # Create new user
            cursor.execute('''
                INSERT INTO users (username) VALUES (?)
            ''', (username,))
            conn.commit()
            
            # Initialize achievements and badges
            for achievement in self.achievements:
                cursor.execute('''
                    INSERT INTO user_achievements (username, achievement_id, unlocked)
                    VALUES (?, ?, FALSE)
                ''', (username, achievement.id))
            
            for badge in self.badges:
                cursor.execute('''
                    INSERT INTO user_badges (username, badge_id, earned)
                    VALUES (?, ?, FALSE)
                ''', (username, badge.id))
            
            conn.commit()
            user_data = (username, 1, 0, 0, 0, '', datetime.now().isoformat(), datetime.now().isoformat())
        
        # Get achievements
        cursor.execute('''
            SELECT achievement_id, unlocked, unlock_date
            FROM user_achievements WHERE username = ?
        ''', (username,))
        achievement_data = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
        
        user_achievements = []
        for achievement in self.achievements:
            unlocked, unlock_date = achievement_data.get(achievement.id, (False, None))
            user_achievements.append(Achievement(
                id=achievement.id,
                name=achievement.name,
                description=achievement.description,
                icon=achievement.icon,
                points=achievement.points,
                category=achievement.category,
                unlocked=bool(unlocked),
                unlock_date=unlock_date
            ))
        
        # Get badges
        cursor.execute('''
            SELECT badge_id, earned, earned_date
            FROM user_badges WHERE username = ?
        ''', (username,))
        badge_data = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
        
        user_badges = []
        for badge in self.badges:
            earned, earned_date = badge_data.get(badge.id, (False, None))
            user_badges.append(Badge(
                id=badge.id,
                name=badge.name,
                description=badge.description,
                icon=badge.icon,
                rarity=badge.rarity,
                requirements=badge.requirements,
                earned=bool(earned),
                earned_date=earned_date
            ))
        
        conn.close()
        
        return UserProfile(
            username=user_data[0],
            level=user_data[1],
            xp=user_data[2],
            total_points=user_data[3],
            achievements=user_achievements,
            badges=user_badges,
            learning_streak=user_data[4],
            favorite_platform=user_data[5],
            join_date=user_data[6],
            last_active=user_data[7]
        )
    
    async def award_xp(self, username: str, xp_amount: int, reason: str = ""):
        """Award XP and check for level ups"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current XP and level
        cursor.execute("SELECT xp, level FROM users WHERE username = ?", (username,))
        current_xp, current_level = cursor.fetchone()
        
        new_xp = current_xp + xp_amount
        new_level = current_level
        
        # Calculate new level (100 XP per level with scaling)
        while new_xp >= (new_level * 100):
            new_xp -= (new_level * 100)
            new_level += 1
        
        # Update user
        cursor.execute('''
            UPDATE users 
            SET xp = ?, level = ?, last_active = CURRENT_TIMESTAMP
            WHERE username = ?
        ''', (new_xp, new_level, username))
        
        conn.commit()
        conn.close()
        
        # Broadcast level up if applicable
        if new_level > current_level:
            await self.broadcast_notification({
                'type': 'level_up',
                'username': username,
                'new_level': new_level,
                'reason': f"Level up! {reason}"
            })
        
        return new_level > current_level
    
    async def check_achievements(self, username: str, activity_data: Dict[str, Any]):
        """Check and unlock achievements based on user activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        unlocked_achievements = []
        
        for achievement in self.achievements:
            # Check if already unlocked
            cursor.execute('''
                SELECT unlocked FROM user_achievements 
                WHERE username = ? AND achievement_id = ?
            ''', (username, achievement.id))
            
            if cursor.fetchone()[0]:
                continue
            
            # Check achievement conditions
            should_unlock = False
            
            if achievement.id == "first_steps" and activity_data.get('lessons_completed', 0) >= 1:
                should_unlock = True
            elif achievement.id == "code_warrior" and activity_data.get('problems_solved', 0) >= 10:
                should_unlock = True
            elif achievement.id == "security_minded" and activity_data.get('security_challenges', 0) >= 5:
                should_unlock = True
            elif achievement.id == "consistent_learner" and activity_data.get('learning_streak', 0) >= 7:
                should_unlock = True
            elif achievement.id == "consciousness_sync" and activity_data.get('consciousness_correlation', 0) >= 0.9:
                should_unlock = True
            
            if should_unlock:
                cursor.execute('''
                    UPDATE user_achievements 
                    SET unlocked = TRUE, unlock_date = CURRENT_TIMESTAMP
                    WHERE username = ? AND achievement_id = ?
                ''', (username, achievement.id))
                
                # Award points
                cursor.execute('''
                    UPDATE users 
                    SET total_points = total_points + ?
                    WHERE username = ?
                ''', (achievement.points, username))
                
                unlocked_achievements.append(achievement)
        
        conn.commit()
        conn.close()
        
        # Broadcast new achievements
        for achievement in unlocked_achievements:
            await self.broadcast_notification({
                'type': 'achievement_unlocked',
                'username': username,
                'achievement': asdict(achievement)
            })
        
        return unlocked_achievements
    
    async def broadcast_notification(self, notification: Dict[str, Any]):
        """Broadcast notification to connected clients"""
        if not self.connected_clients:
            return
        
        message = json.dumps({
            'type': 'notification',
            'notification': notification,
            'timestamp': datetime.now().isoformat()
        })
        
        disconnected_clients = set()
        for client in self.connected_clients:
            try:
                await client.send_text(message)
            except:
                disconnected_clients.add(client)
        
        self.connected_clients -= disconnected_clients

# Global gamification engine
gamification = GamificationEngine()

@app.get("/", response_class=HTMLResponse)
async def education_home(request: Request):
    """Main education platform page"""
    return templates.TemplateResponse("education_platform.html", {"request": request})

@app.get("/profile/{username}", response_class=HTMLResponse)
async def user_profile(request: Request, username: str):
    """User profile page"""
    profile = await gamification.get_user_profile(username)
    return templates.TemplateResponse("user_profile.html", {
        "request": request,
        "profile": profile
    })

@app.post("/api/learning/session")
async def log_learning_session(
    username: str = Form(...),
    platform: str = Form(...),
    duration: int = Form(...),
    skills: str = Form(...)
):
    """Log a learning session"""
    # Calculate XP based on duration and platform
    base_xp = duration * 2  # 2 XP per minute
    platform_bonus = {"leetcode": 1.5, "tryhackme": 2.0, "hackthebox": 2.5}.get(platform.lower(), 1.0)
    xp_gained = int(base_xp * platform_bonus)
    
    # Award XP
    level_up = await gamification.award_xp(username, xp_gained, f"Learning on {platform}")
    
    # Check achievements
    activity_data = {
        'lessons_completed': 1,
        'platform': platform,
        'duration': duration
    }
    
    # Get consciousness correlation
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{gamification.consciousness_bridge_url}/consciousness/correlation") as response:
                if response.status == 200:
                    data = await response.json()
                    activity_data['consciousness_correlation'] = data.get('correlation', 0.0)
    except:
        activity_data['consciousness_correlation'] = 0.0
    
    unlocked_achievements = await gamification.check_achievements(username, activity_data)
    
    # Log session to database
    conn = sqlite3.connect(gamification.db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO learning_sessions 
        (username, platform, duration, skills_practiced, xp_gained, consciousness_correlation)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, platform, duration, skills, xp_gained, activity_data['consciousness_correlation']))
    conn.commit()
    conn.close()
    
    return JSONResponse({
        'success': True,
        'xp_gained': xp_gained,
        'level_up': level_up,
        'achievements_unlocked': len(unlocked_achievements),
        'consciousness_correlation': activity_data['consciousness_correlation']
    })

@app.get("/api/leaderboard")
async def get_leaderboard():
    """Get user leaderboard"""
    conn = sqlite3.connect(gamification.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT username, level, total_points, learning_streak
        FROM users
        ORDER BY total_points DESC, level DESC
        LIMIT 50
    ''')
    
    leaderboard = []
    for i, row in enumerate(cursor.fetchall()):
        leaderboard.append({
            'rank': i + 1,
            'username': row[0],
            'level': row[1],
            'total_points': row[2],
            'learning_streak': row[3]
        })
    
    conn.close()
    return JSONResponse(leaderboard)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    gamification.connected_clients.add(websocket)
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        gamification.connected_clients.discard(websocket)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'connected_clients': len(gamification.connected_clients)
    })

def setup_education_gui():
    """Setup education GUI directories and files"""
    Path("static").mkdir(exist_ok=True)
    Path("templates").mkdir(exist_ok=True)
    
    # Create main education platform template
    education_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SynapticOS Education Platform</title>
    <link rel="stylesheet" href="/static/education.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <span class="logo">🎓</span>
            <h1>SynapticOS Education</h1>
        </div>
        <div class="nav-links">
            <a href="/profile/demo">Profile</a>
            <a href="#leaderboard">Leaderboard</a>
            <a href="#platforms">Platforms</a>
        </div>
    </nav>

    <main class="education-main">
        <!-- User Dashboard -->
        <section class="dashboard-section">
            <div class="user-card">
                <div class="user-avatar">👤</div>
                <div class="user-info">
                    <h3>Welcome back, <span id="username">Learner</span>!</h3>
                    <div class="user-stats">
                        <div class="stat">
                            <span class="stat-label">Level</span>
                            <span class="stat-value" id="user-level">1</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">XP</span>
                            <span class="stat-value" id="user-xp">0</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Streak</span>
                            <span class="stat-value" id="user-streak">0</span>
                        </div>
                    </div>
                    <div class="xp-bar">
                        <div class="xp-fill" id="xp-fill" style="width: 0%"></div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Quick Actions -->
        <section class="quick-actions">
            <h2>🚀 Quick Start</h2>
            <div class="action-grid">
                <div class="action-card" onclick="openPlatform('freecodecamp')">
                    <div class="action-icon">💻</div>
                    <h3>FreeCodeCamp</h3>
                    <p>Web Development & Programming</p>
                </div>
                <div class="action-card" onclick="openPlatform('tryhackme')">
                    <div class="action-icon">🛡️</div>
                    <h3>TryHackMe</h3>
                    <p>Cybersecurity Challenges</p>
                </div>
                <div class="action-card" onclick="openPlatform('leetcode')">
                    <div class="action-icon">🧮</div>
                    <h3>LeetCode</h3>
                    <p>Algorithm & Data Structures</p>
                </div>
                <div class="action-card" onclick="openPlatform('bootdev')">
                    <div class="action-icon">🎯</div>
                    <h3>Boot.dev</h3>
                    <p>Backend Development</p>
                </div>
            </div>
        </section>

        <!-- Learning Session Tracker -->
        <section class="session-tracker">
            <h2>📚 Log Learning Session</h2>
            <form id="session-form" class="session-form">
                <div class="form-group">
                    <label for="platform">Platform</label>
                    <select id="platform" name="platform" required>
                        <option value="">Select Platform</option>
                        <option value="freecodecamp">FreeCodeCamp</option>
                        <option value="tryhackme">TryHackMe</option>
                        <option value="leetcode">LeetCode</option>
                        <option value="bootdev">Boot.dev</option>
                        <option value="hackthebox">HackTheBox</option>
                        <option value="overthewire">OverTheWire</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="duration">Duration (minutes)</label>
                    <input type="number" id="duration" name="duration" min="1" required>
                </div>
                <div class="form-group">
                    <label for="skills">Skills Practiced</label>
                    <input type="text" id="skills" name="skills" placeholder="e.g., Python, JavaScript, Security" required>
                </div>
                <button type="submit" class="submit-btn">Log Session</button>
            </form>
        </section>

        <!-- Recent Achievements -->
        <section class="achievements-section">
            <h2>🏆 Recent Achievements</h2>
            <div class="achievements-grid" id="achievements-grid">
                <div class="achievement-placeholder">
                    Complete your first learning session to unlock achievements!
                </div>
            </div>
        </section>

        <!-- Leaderboard -->
        <section class="leaderboard-section" id="leaderboard">
            <h2>👑 Leaderboard</h2>
            <div class="leaderboard-list" id="leaderboard-list">
                Loading leaderboard...
            </div>
        </section>
    </main>

    <!-- Notification System -->
    <div id="notifications" class="notifications"></div>

    <script>
        // Demo user data
        let currentUser = 'demo';
        const ws = new WebSocket('ws://localhost:8001/ws');

        // Load user data
        async function loadUserData() {
            // This would normally fetch from API
            document.getElementById('username').textContent = currentUser;
        }

        // Load leaderboard
        async function loadLeaderboard() {
            try {
                const response = await fetch('/api/leaderboard');
                const leaderboard = await response.json();
                
                const container = document.getElementById('leaderboard-list');
                container.innerHTML = leaderboard.map((user, index) => `
                    <div class="leaderboard-item ${user.username === currentUser ? 'current-user' : ''}">
                        <span class="rank">#${user.rank}</span>
                        <span class="username">${user.username}</span>
                        <span class="level">Lv.${user.level}</span>
                        <span class="points">${user.total_points} pts</span>
                        <span class="streak">${user.learning_streak}🔥</span>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Failed to load leaderboard:', error);
            }
        }

        // Log learning session
        document.getElementById('session-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData();
            formData.append('username', currentUser);
            formData.append('platform', document.getElementById('platform').value);
            formData.append('duration', document.getElementById('duration').value);
            formData.append('skills', document.getElementById('skills').value);
            
            try {
                const response = await fetch('/api/learning/session', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showNotification(
                        `🎉 Session logged! +${result.xp_gained} XP${result.level_up ? ' Level up!' : ''}`,
                        'success'
                    );
                    
                    if (result.achievements_unlocked > 0) {
                        showNotification(`🏆 ${result.achievements_unlocked} new achievement(s) unlocked!`, 'achievement');
                    }
                    
                    // Reset form
                    document.getElementById('session-form').reset();
                    
                    // Reload data
                    loadUserData();
                    loadLeaderboard();
                }
            } catch (error) {
                console.error('Failed to log session:', error);
                showNotification('Failed to log session. Please try again.', 'error');
            }
        });

        // Open external platform
        function openPlatform(platform) {
            const urls = {
                'freecodecamp': 'https://www.freecodecamp.org',
                'tryhackme': 'https://tryhackme.com',
                'leetcode': 'https://leetcode.com',
                'bootdev': 'https://boot.dev'
            };
            
            if (urls[platform]) {
                window.open(urls[platform], '_blank');
            }
        }

        // Show notification
        function showNotification(message, type = 'info') {
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.textContent = message;
            
            document.getElementById('notifications').appendChild(notification);
            
            // Auto remove after 5 seconds
            setTimeout(() => {
                notification.remove();
            }, 5000);
        }

        // WebSocket handlers
        ws.onmessage = function(event) {
            const message = JSON.parse(event.data);
            
            if (message.type === 'notification') {
                const notif = message.notification;
                
                if (notif.type === 'level_up') {
                    showNotification(`🎊 ${notif.username} reached level ${notif.new_level}!`, 'success');
                } else if (notif.type === 'achievement_unlocked') {
                    showNotification(`🏆 ${notif.username} unlocked "${notif.achievement.name}"!`, 'achievement');
                }
            }
        };

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadUserData();
            loadLeaderboard();
        });
    </script>
</body>
</html>
"""
    
    with open("templates/education_platform.html", "w") as f:
        f.write(education_html)
    
    # Create CSS for education platform
    education_css = """
/* SynapticOS Education Platform Styles */
:root {
    --primary: #667eea;
    --secondary: #764ba2;
    --success: #48bb78;
    --warning: #ed8936;
    --error: #f56565;
    --background: #1a202c;
    --surface: #2d3748;
    --text: #e2e8f0;
    --text-muted: #a0aec0;
    --border: #4a5568;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, var(--background), var(--surface));
    color: var(--text);
    min-height: 100vh;
}

.navbar {
    background: rgba(45, 55, 72, 0.9);
    backdrop-filter: blur(10px);
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    z-index: 100;
}

.nav-brand {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.logo {
    font-size: 1.5rem;
}

.nav-brand h1 {
    font-size: 1.25rem;
    font-weight: 600;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.nav-links {
    display: flex;
    gap: 2rem;
}

.nav-links a {
    color: var(--text);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s ease;
}

.nav-links a:hover {
    color: var(--primary);
}

.education-main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

.dashboard-section {
    margin-bottom: 3rem;
}

.user-card {
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    border-radius: 16px;
    padding: 2rem;
    display: flex;
    align-items: center;
    gap: 2rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.user-avatar {
    font-size: 4rem;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.user-info h3 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
    color: white;
}

.user-stats {
    display: flex;
    gap: 2rem;
    margin-bottom: 1rem;
}

.stat {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.stat-label {
    font-size: 0.875rem;
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 0.25rem;
}

.stat-value {
    font-size: 1.25rem;
    font-weight: bold;
    color: white;
}

.xp-bar {
    width: 100%;
    height: 8px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    overflow: hidden;
}

.xp-fill {
    height: 100%;
    background: linear-gradient(90deg, #48bb78, #38a169);
    border-radius: 4px;
    transition: width 0.5s ease;
}

.quick-actions {
    margin-bottom: 3rem;
}

.quick-actions h2 {
    margin-bottom: 1.5rem;
    font-size: 1.5rem;
    color: var(--text);
}

.action-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}

.action-card {
    background: var(--surface);
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 1px solid var(--border);
}

.action-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    border-color: var(--primary);
}

.action-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.action-card h3 {
    font-size: 1.25rem;
    margin-bottom: 0.5rem;
    color: var(--text);
}

.action-card p {
    color: var(--text-muted);
    font-size: 0.875rem;
}

.session-tracker {
    background: var(--surface);
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 3rem;
    border: 1px solid var(--border);
}

.session-tracker h2 {
    margin-bottom: 1.5rem;
    color: var(--text);
}

.session-form {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    align-items: end;
}

.form-group {
    display: flex;
    flex-direction: column;
}

.form-group label {
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: var(--text);
}

.form-group input,
.form-group select {
    padding: 0.75rem;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--background);
    color: var(--text);
    font-size: 1rem;
}

.form-group input:focus,
.form-group select:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.submit-btn {
    padding: 0.75rem 2rem;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.submit-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.achievements-section,
.leaderboard-section {
    background: var(--surface);
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 3rem;
    border: 1px solid var(--border);
}

.achievements-section h2,
.leaderboard-section h2 {
    margin-bottom: 1.5rem;
    color: var(--text);
}

.achievements-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.achievement-placeholder {
    text-align: center;
    padding: 2rem;
    color: var(--text-muted);
    border: 2px dashed var(--border);
    border-radius: 8px;
}

.leaderboard-item {
    display: grid;
    grid-template-columns: auto 1fr auto auto auto;
    gap: 1rem;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 0.5rem;
    background: rgba(255, 255, 255, 0.05);
    align-items: center;
}

.leaderboard-item.current-user {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
    border: 1px solid var(--primary);
}

.rank {
    font-weight: bold;
    color: var(--primary);
}

.username {
    font-weight: 500;
}

.notifications {
    position: fixed;
    top: 2rem;
    right: 2rem;
    z-index: 1000;
}

.notification {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    animation: slideIn 0.3s ease;
}

.notification-success {
    border-color: var(--success);
    background: rgba(72, 187, 120, 0.1);
}

.notification-achievement {
    border-color: var(--warning);
    background: rgba(237, 137, 54, 0.1);
}

.notification-error {
    border-color: var(--error);
    background: rgba(245, 101, 101, 0.1);
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@media (max-width: 768px) {
    .education-main {
        padding: 1rem;
    }
    
    .user-card {
        flex-direction: column;
        text-align: center;
    }
    
    .session-form {
        grid-template-columns: 1fr;
    }
    
    .user-stats {
        justify-content: center;
    }
}
"""
    
    with open("static/education.css", "w") as f:
        f.write(education_css)

if __name__ == "__main__":
    setup_education_gui()
    uvicorn.run(
        "education_gui:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
