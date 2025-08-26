#!/usr/bin/env python3
"""
Syn_OS Unified CTF Platform
Combined CTF challenge generator + platform for consciousness-enhanced cybersecurity training
Consolidates ctf-generator + ctf-platform functionality
"""

import asyncio
import json
import logging
import os
import sys
import random
import hashlib
import tempfile
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
import string
import base64
import zipfile
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Logging setup
log_dir = Path('/app/logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / 'ctf-unified.log')
    ]
)
logger = logging.getLogger('ctf-unified')

@dataclass
class ChallengeTemplate:
    """CTF challenge template"""
    id: str
    name: str
    category: str
    difficulty: str
    description: str
    flag_format: str
    hints: List[str]
    files: List[str]
    consciousness_adaptation: Dict[str, Any]

@dataclass
class GeneratedChallenge:
    """Generated CTF challenge instance"""
    id: str
    template_id: str
    name: str
    category: str
    difficulty: str
    description: str
    flag: str
    hints: List[str]
    files: List[str]
    consciousness_level: float
    created_at: str
    expires_at: Optional[str]
    metadata: Dict[str, Any]

@dataclass
class UserSubmission:
    """User challenge submission"""
    id: str
    user_id: str
    challenge_id: str
    flag_submitted: str
    is_correct: bool
    submitted_at: str
    consciousness_feedback: Dict[str, Any]

class UnifiedCTFPlatform:
    """Unified CTF platform combining challenge generation and platform management"""
    
    def __init__(self, data_dir: str = "/app/data/ctf"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Challenge management
        self.challenge_templates = {}
        self.generated_challenges = {}
        self.user_submissions = {}
        
        # Consciousness integration
        self.consciousness_level = 0.5
        self.difficulty_adaptation = True
        
        # WebSocket connections
        self.connected_clients = set()
        
        # Initialize components
        self.setup_database()
        self.load_default_templates()
    
    def setup_database(self):
        """Initialize CTF platform database"""
        self.db_path = self.data_dir / 'ctf_platform.db'
        
        with sqlite3.connect(self.db_path) as conn:
            # Challenge templates table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS challenge_templates (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    description TEXT NOT NULL,
                    flag_format TEXT NOT NULL,
                    hints TEXT DEFAULT '[]',
                    files TEXT DEFAULT '[]',
                    consciousness_adaptation TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Generated challenges table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS generated_challenges (
                    id TEXT PRIMARY KEY,
                    template_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    description TEXT NOT NULL,
                    flag TEXT NOT NULL,
                    hints TEXT DEFAULT '[]',
                    files TEXT DEFAULT '[]',
                    consciousness_level REAL DEFAULT 0.5,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (template_id) REFERENCES challenge_templates (id)
                )
            ''')
            
            # User submissions table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_submissions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    challenge_id TEXT NOT NULL,
                    flag_submitted TEXT NOT NULL,
                    is_correct BOOLEAN NOT NULL,
                    submitted_at TEXT NOT NULL,
                    consciousness_feedback TEXT DEFAULT '{}',
                    FOREIGN KEY (challenge_id) REFERENCES generated_challenges (id)
                )
            ''')
            
            # User progress table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_progress (
                    user_id TEXT NOT NULL,
                    challenges_attempted INTEGER DEFAULT 0,
                    challenges_solved INTEGER DEFAULT 0,
                    total_score INTEGER DEFAULT 0,
                    consciousness_level REAL DEFAULT 0.5,
                    last_activity TEXT,
                    PRIMARY KEY (user_id)
                )
            ''')
            
            conn.commit()
    
    def load_default_templates(self):
        """Load default CTF challenge templates"""
        templates = [
            ChallengeTemplate(
                id="web_basic_sqli",
                name="Basic SQL Injection",
                category="web",
                difficulty="easy",
                description="Find the SQL injection vulnerability and extract the flag",
                flag_format="SYN{.*}",
                hints=["Try different input values", "Look for error messages", "Union select might help"],
                files=["web_app.zip"],
                consciousness_adaptation={"adaptive_hints": True, "dynamic_difficulty": True}
            ),
            ChallengeTemplate(
                id="crypto_caesar",
                name="Caesar Cipher",
                category="crypto",
                difficulty="easy", 
                description="Decrypt the Caesar cipher to find the flag",
                flag_format="SYN{.*}",
                hints=["Try different shift values", "Look for English words", "ROT13 is common"],
                files=["encrypted.txt"],
                consciousness_adaptation={"hint_progression": True, "pattern_analysis": True}
            ),
            ChallengeTemplate(
                id="reversing_basic",
                name="Basic Reverse Engineering",
                category="reversing",
                difficulty="medium",
                description="Reverse engineer the binary to find the flag validation logic",
                flag_format="SYN{.*}",
                hints=["Use a debugger", "Look at string comparisons", "Check for obfuscation"],
                files=["challenge.bin"],
                consciousness_adaptation={"tool_suggestions": True, "step_guidance": True}
            ),
            ChallengeTemplate(
                id="forensics_memory",
                name="Memory Forensics",
                category="forensics",
                difficulty="hard",
                description="Analyze the memory dump to find the hidden flag",
                flag_format="SYN{.*}",
                hints=["Use volatility framework", "Look for processes", "Check for network connections"],
                files=["memory.dump"],
                consciousness_adaptation={"tool_integration": True, "evidence_correlation": True}
            )
        ]
        
        for template in templates:
            self.challenge_templates[template.id] = template
            self._store_challenge_template(template)
    
    def _store_challenge_template(self, template: ChallengeTemplate):
        """Store challenge template in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO challenge_templates 
                (id, name, category, difficulty, description, flag_format, hints, files, consciousness_adaptation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                template.id, template.name, template.category, template.difficulty,
                template.description, template.flag_format, json.dumps(template.hints),
                json.dumps(template.files), json.dumps(template.consciousness_adaptation)
            ))
            conn.commit()
    
    async def generate_challenge(self, template_id: str, user_id: str, consciousness_level: float = None) -> GeneratedChallenge:
        """Generate a new challenge instance from template"""
        if template_id not in self.challenge_templates:
            raise ValueError(f"Template {template_id} not found")
        
        template = self.challenge_templates[template_id]
        consciousness_level = consciousness_level or self.consciousness_level
        
        # Generate unique challenge ID
        challenge_id = hashlib.md5(f"{template_id}_{user_id}_{datetime.now().isoformat()}".encode()).hexdigest()
        
        # Generate challenge-specific content
        challenge_content = await self._generate_challenge_content(template, consciousness_level)
        
        # Create generated challenge
        challenge = GeneratedChallenge(
            id=challenge_id,
            template_id=template_id,
            name=template.name,
            category=template.category,
            difficulty=template.difficulty,
            description=challenge_content['description'],
            flag=challenge_content['flag'],
            hints=challenge_content['hints'],
            files=challenge_content['files'],
            consciousness_level=consciousness_level,
            created_at=datetime.now().isoformat(),
            expires_at=(datetime.now() + timedelta(hours=24)).isoformat(),
            metadata={
                'generated_for_user': user_id,
                'generation_method': 'consciousness_adaptive',
                'template_version': '1.0'
            }
        )
        
        # Store challenge
        self.generated_challenges[challenge_id] = challenge
        await self._store_generated_challenge(challenge)
        
        logger.info(f"Generated challenge {challenge_id} from template {template_id}")
        return challenge
    
    async def _generate_challenge_content(self, template: ChallengeTemplate, consciousness_level: float) -> Dict[str, Any]:
        """Generate challenge content based on template and consciousness level"""
        # Generate flag
        flag_suffix = self._generate_random_string(16)
        flag = f"SYN{{{flag_suffix}}}"
        
        # Adapt description based on consciousness level
        description = template.description
        if consciousness_level > 0.7:
            description += " Advanced techniques may be required."
        elif consciousness_level < 0.3:
            description += " Start with basic approaches."
        
        # Adapt hints based on consciousness level
        hints = template.hints.copy()
        if consciousness_level < 0.5:
            # Add more detailed hints for lower consciousness levels
            if template.category == "web":
                hints.insert(0, "Start by examining the input fields carefully")
            elif template.category == "crypto":
                hints.insert(0, "Consider common cipher types first")
        
        # Generate files based on template
        files = await self._generate_challenge_files(template, flag, consciousness_level)
        
        return {
            'description': description,
            'flag': flag,
            'hints': hints,
            'files': files
        }
    
    async def _generate_challenge_files(self, template: ChallengeTemplate, flag: str, consciousness_level: float) -> List[str]:
        """Generate challenge files based on template"""
        files = []
        
        for file_template in template.files:
            if file_template == "encrypted.txt":
                # Generate encrypted text file
                file_content = await self._generate_crypto_file(flag, consciousness_level)
                file_path = self._save_challenge_file("encrypted.txt", file_content)
                files.append(file_path)
            elif file_template == "web_app.zip":
                # Generate web application
                file_path = await self._generate_web_app(flag, consciousness_level)
                files.append(file_path)
            elif file_template in ["challenge.bin", "memory.dump"]:
                # Generate placeholder binary files
                file_path = self._generate_placeholder_file(file_template)
                files.append(file_path)
        
        return files
    
    async def _generate_crypto_file(self, flag: str, consciousness_level: float) -> str:
        """Generate cryptographic challenge file"""
        # Simple Caesar cipher implementation
        shift = random.randint(1, 25)
        
        # Encrypt the flag
        encrypted_flag = ""
        for char in flag:
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                encrypted_flag += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
            else:
                encrypted_flag += char
        
        # Add some context based on consciousness level
        if consciousness_level < 0.5:
            content = f"The secret message is: {encrypted_flag}\n"
            content += f"Hint: Caesar cipher with shift {shift}\n"
        else:
            content = f"Encrypted message: {encrypted_flag}\n"
            content += "Decode this message to find your prize.\n"
        
        return content
    
    async def _generate_web_app(self, flag: str, consciousness_level: float) -> str:
        """Generate web application challenge"""
        # Create a simple vulnerable web app
        web_app_content = f'''
<!DOCTYPE html>
<html>
<head><title>Vulnerable Web App</title></head>
<body>
<h1>Login System</h1>
<form method="post">
    <input type="text" name="username" placeholder="Username">
    <input type="password" name="password" placeholder="Password">
    <input type="submit" value="Login">
</form>
<!-- SQL: SELECT * FROM users WHERE username='$username' AND password='$password' -->
<!-- Flag is stored in admin account: {flag} -->
</body>
</html>
'''
        
        # Create zip file
        zip_path = self.data_dir / f"web_app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.writestr('index.html', web_app_content)
        
        return str(zip_path)
    
    def _generate_placeholder_file(self, filename: str) -> str:
        """Generate placeholder file for complex challenges"""
        file_path = self.data_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate some random binary content
        with open(file_path, 'wb') as f:
            f.write(os.urandom(1024))  # 1KB of random data
        
        return str(file_path)
    
    def _save_challenge_file(self, filename: str, content: str) -> str:
        """Save challenge file content"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = self.data_dir / f"{timestamp}_{filename}"
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        return str(file_path)
    
    def _generate_random_string(self, length: int) -> str:
        """Generate random string for flags"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    async def _store_generated_challenge(self, challenge: GeneratedChallenge):
        """Store generated challenge in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO generated_challenges 
                (id, template_id, name, category, difficulty, description, flag, hints, files,
                 consciousness_level, created_at, expires_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                challenge.id, challenge.template_id, challenge.name, challenge.category,
                challenge.difficulty, challenge.description, challenge.flag,
                json.dumps(challenge.hints), json.dumps(challenge.files),
                challenge.consciousness_level, challenge.created_at, challenge.expires_at,
                json.dumps(challenge.metadata)
            ))
            conn.commit()
    
    async def submit_flag(self, user_id: str, challenge_id: str, submitted_flag: str) -> UserSubmission:
        """Process user flag submission"""
        if challenge_id not in self.generated_challenges:
            raise ValueError(f"Challenge {challenge_id} not found")
        
        challenge = self.generated_challenges[challenge_id]
        is_correct = submitted_flag.strip() == challenge.flag.strip()
        
        # Generate consciousness feedback
        consciousness_feedback = await self._generate_consciousness_feedback(
            challenge, submitted_flag, is_correct
        )
        
        # Create submission record
        submission_id = hashlib.md5(f"{user_id}_{challenge_id}_{datetime.now().isoformat()}".encode()).hexdigest()
        submission = UserSubmission(
            id=submission_id,
            user_id=user_id,
            challenge_id=challenge_id,
            flag_submitted=submitted_flag,
            is_correct=is_correct,
            submitted_at=datetime.now().isoformat(),
            consciousness_feedback=consciousness_feedback
        )
        
        # Store submission
        self.user_submissions[submission_id] = submission
        await self._store_user_submission(submission)
        
        # Update user progress
        await self._update_user_progress(user_id, challenge, is_correct)
        
        # Broadcast update
        await self._broadcast_submission_update(submission)
        
        logger.info(f"Flag submission from user {user_id} for challenge {challenge_id}: {'correct' if is_correct else 'incorrect'}")
        return submission
    
    async def _generate_consciousness_feedback(self, challenge: GeneratedChallenge, submitted_flag: str, is_correct: bool) -> Dict[str, Any]:
        """Generate consciousness-enhanced feedback"""
        feedback = {
            'is_correct': is_correct,
            'consciousness_level': challenge.consciousness_level,
            'feedback_type': 'adaptive',
            'timestamp': datetime.now().isoformat()
        }
        
        if is_correct:
            feedback['message'] = "Excellent work! Your consciousness level in this area is improving."
            feedback['consciousness_boost'] = 0.1
        else:
            # Analyze the submission to provide helpful feedback
            if challenge.category == "crypto":
                if "SYN{" in submitted_flag:
                    feedback['message'] = "You're on the right track with the flag format. Check your decryption method."
                else:
                    feedback['message'] = "Remember to include the flag in the correct format: SYN{...}"
            elif challenge.category == "web":
                feedback['message'] = "Consider different injection techniques or parameter manipulation."
            else:
                feedback['message'] = "Keep exploring different approaches. Review the hints if needed."
            
            feedback['consciousness_boost'] = -0.05
            feedback['hint_suggestion'] = random.choice(challenge.hints) if challenge.hints else None
        
        return feedback
    
    async def _store_user_submission(self, submission: UserSubmission):
        """Store user submission in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO user_submissions 
                (id, user_id, challenge_id, flag_submitted, is_correct, submitted_at, consciousness_feedback)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                submission.id, submission.user_id, submission.challenge_id,
                submission.flag_submitted, submission.is_correct, submission.submitted_at,
                json.dumps(submission.consciousness_feedback)
            ))
            conn.commit()
    
    async def _update_user_progress(self, user_id: str, challenge: GeneratedChallenge, is_correct: bool):
        """Update user progress tracking"""
        with sqlite3.connect(self.db_path) as conn:
            # Get current progress
            cursor = conn.execute('SELECT * FROM user_progress WHERE user_id = ?', (user_id,))
            current_progress = cursor.fetchone()
            
            if current_progress:
                attempts = current_progress[1] + 1
                solved = current_progress[2] + (1 if is_correct else 0)
                score = current_progress[3] + (100 if is_correct else 0)
                consciousness_level = min(1.0, current_progress[4] + (0.1 if is_correct else -0.05))
            else:
                attempts = 1
                solved = 1 if is_correct else 0
                score = 100 if is_correct else 0
                consciousness_level = 0.6 if is_correct else 0.45
            
            # Update progress
            conn.execute('''
                INSERT OR REPLACE INTO user_progress 
                (user_id, challenges_attempted, challenges_solved, total_score, consciousness_level, last_activity)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, attempts, solved, score, consciousness_level, datetime.now().isoformat()))
            conn.commit()
    
    async def _broadcast_submission_update(self, submission: UserSubmission):
        """Broadcast submission update to connected clients"""
        if not self.connected_clients:
            return
        
        update_data = {
            'type': 'flag_submission',
            'submission': asdict(submission),
            'timestamp': datetime.now().isoformat()
        }
        
        disconnected_clients = set()
        for client in self.connected_clients.copy():
            try:
                await client.send_text(json.dumps(update_data, default=str))
            except Exception as e:
                logger.warning(f"Failed to send update to client: {e}")
                disconnected_clients.add(client)
        
        self.connected_clients -= disconnected_clients
    
    def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user progress and statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT * FROM user_progress WHERE user_id = ?', (user_id,))
            progress = cursor.fetchone()
            
            if not progress:
                return {
                    'user_id': user_id,
                    'challenges_attempted': 0,
                    'challenges_solved': 0,
                    'total_score': 0,
                    'consciousness_level': 0.5,
                    'last_activity': None
                }
            
            return {
                'user_id': progress[0],
                'challenges_attempted': progress[1],
                'challenges_solved': progress[2],
                'total_score': progress[3],
                'consciousness_level': progress[4],
                'last_activity': progress[5]
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'service_name': 'unified-ctf-platform',
            'version': '1.0.0',
            'status': 'operational',
            'challenge_templates_count': len(self.challenge_templates),
            'generated_challenges_count': len(self.generated_challenges),
            'user_submissions_count': len(self.user_submissions),
            'consciousness_level': self.consciousness_level,
            'difficulty_adaptation_enabled': self.difficulty_adaptation,
            'connected_clients': len(self.connected_clients),
            'timestamp': datetime.now().isoformat()
        }

# Initialize unified CTF platform
ctf_platform = UnifiedCTFPlatform()

# FastAPI app
app = FastAPI(
    title="Syn_OS Unified CTF Platform",
    description="Combined CTF challenge generator and platform for consciousness-enhanced cybersecurity training",
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

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info("Starting Syn_OS Unified CTF Platform...")
    logger.info("Unified CTF Platform started successfully!")

# Challenge Management API Endpoints
@app.get("/api/v1/templates")
async def list_templates():
    """List available challenge templates"""
    return {
        'templates': [asdict(template) for template in ctf_platform.challenge_templates.values()],
        'count': len(ctf_platform.challenge_templates)
    }

@app.post("/api/v1/challenges/generate")
async def generate_challenge(template_id: str, user_id: str, consciousness_level: float = None):
    """Generate a new challenge instance"""
    try:
        challenge = await ctf_platform.generate_challenge(template_id, user_id, consciousness_level)
        # Don't return the flag in the API response
        challenge_data = asdict(challenge)
        challenge_data['flag'] = None  # Hide flag from response
        return {'challenge': challenge_data}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/challenges")
async def list_challenges(limit: int = 20):
    """List generated challenges (without flags)"""
    challenges = list(ctf_platform.generated_challenges.values())[:limit]
    challenge_data = []
    
    for challenge in challenges:
        data = asdict(challenge)
        data['flag'] = None  # Hide flags
        challenge_data.append(data)
    
    return {
        'challenges': challenge_data,
        'total_count': len(ctf_platform.generated_challenges)
    }

@app.post("/api/v1/submissions")
async def submit_flag(user_id: str, challenge_id: str, flag: str):
    """Submit flag for challenge"""
    try:
        submission = await ctf_platform.submit_flag(user_id, challenge_id, flag)
        return {'submission': asdict(submission)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/users/{user_id}/progress")
async def get_user_progress(user_id: str):
    """Get user progress and statistics"""
    progress = ctf_platform.get_user_progress(user_id)
    return progress

@app.get("/api/v1/status")
async def system_status():
    """Get system status"""
    return ctf_platform.get_system_status()

# WebSocket endpoint for real-time updates
@app.websocket("/ws/ctf")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time CTF updates"""
    await websocket.accept()
    ctf_platform.connected_clients.add(websocket)
    
    try:
        # Send initial data
        await websocket.send_text(json.dumps({
            'type': 'connection_established',
            'status': ctf_platform.get_system_status()
        }, default=str))
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        ctf_platform.connected_clients.discard(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ctf_platform.connected_clients.discard(websocket)

# Dashboard web interface
@app.get("/", response_class=HTMLResponse)
async def ctf_dashboard():
    """CTF platform dashboard"""
    return HTMLResponse("""
    <html>
    <head><title>Syn_OS CTF Platform</title></head>
    <body>
    <h1>Syn_OS Unified CTF Platform</h1>
    <h2>Consciousness-Enhanced Cybersecurity Training</h2>
    <div id="platform-status">Loading...</div>
    <script>
    async function updateDashboard() {
        try {
            const response = await fetch('/api/v1/status');
            const data = await response.json();
            
            document.getElementById('platform-status').innerHTML = `
                <h3>Platform Status: ${data.status}</h3>
                <p>Challenge Templates: ${data.challenge_templates_count}</p>
                <p>Generated Challenges: ${data.generated_challenges_count}</p>
                <p>User Submissions: ${data.user_submissions_count}</p>
                <p>Consciousness Level: ${data.consciousness_level.toFixed(2)}</p>
                <p>Connected Users: ${data.connected_clients}</p>
            `;
            
        } catch (error) {
            console.error('Dashboard update error:', error);
        }
    }
    updateDashboard();
    setInterval(updateDashboard, 10000);
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
        "service": "unified-ctf-platform",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    logger.info("Starting Syn_OS Unified CTF Platform...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8083,
        log_level="info",
        access_log=True
    )