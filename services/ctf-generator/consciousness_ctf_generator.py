#!/usr/bin/env python3
"""
SynapticOS CTF Dynamic Challenge Generator
Consciousness-enhanced adaptive cybersecurity challenges
"""

import asyncio
import json
import logging
import os
import random
import hashlib
import tempfile
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
import string
import base64
import zipfile

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ctf-generator')

@dataclass
class ChallengeTemplate:
    """CTF challenge template"""
    id: str
    name: str
    category: str
    difficulty: str
    description: str
    template_code: str
    solution_code: str
    hint_levels: List[str]
    consciousness_adaptation: Dict[str, Any]

@dataclass
class GeneratedChallenge:
    """Generated CTF challenge instance"""
    challenge_id: str
    template_id: str
    name: str
    category: str
    difficulty: str
    description: str
    flag: str
    challenge_files: Dict[str, str]
    hints: List[str]
    solution: str
    consciousness_level: float
    metadata: Dict[str, Any]
    created_at: str

@dataclass
class PlayerProfile:
    """Player profile with consciousness tracking"""
    player_id: str
    skill_level: float
    preferred_categories: List[str]
    consciousness_adaptation: float
    challenge_history: List[str]
    learning_pattern: Dict[str, Any]
    last_active: str

@dataclass
class ChallengeResult:
    """Challenge completion result"""
    result_id: str
    challenge_id: str
    player_id: str
    completed: bool
    time_taken: int
    hints_used: int
    consciousness_growth: float
    timestamp: str

class ConsciousnessCTFGenerator:
    """Consciousness-enhanced CTF challenge generator"""
    
    def __init__(self, data_dir: str = "/app/data/ctf"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.db_path = self.data_dir / "ctf_challenges.db"
        self.init_database()
        
        # Challenge templates
        self.templates = {}
        self.load_default_templates()
        
        # Consciousness parameters
        self.consciousness_factors = {
            "adaptation_rate": 0.1,
            "difficulty_scaling": 0.2,
            "learning_acceleration": 0.15,
            "challenge_evolution": 0.25
        }
        
        logger.info("Consciousness CTF Generator initialized")
    
    def init_database(self):
        """Initialize SQLite database for CTF challenges"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS challenge_templates (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    category TEXT,
                    difficulty TEXT,
                    description TEXT,
                    template_code TEXT,
                    solution_code TEXT,
                    hint_levels TEXT,
                    consciousness_adaptation TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS generated_challenges (
                    challenge_id TEXT PRIMARY KEY,
                    template_id TEXT,
                    name TEXT,
                    category TEXT,
                    difficulty TEXT,
                    description TEXT,
                    flag TEXT,
                    challenge_files TEXT,
                    hints TEXT,
                    solution TEXT,
                    consciousness_level REAL,
                    metadata TEXT,
                    created_at TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS player_profiles (
                    player_id TEXT PRIMARY KEY,
                    skill_level REAL,
                    preferred_categories TEXT,
                    consciousness_adaptation REAL,
                    challenge_history TEXT,
                    learning_pattern TEXT,
                    last_active TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS challenge_results (
                    result_id TEXT PRIMARY KEY,
                    challenge_id TEXT,
                    player_id TEXT,
                    completed BOOLEAN,
                    time_taken INTEGER,
                    hints_used INTEGER,
                    consciousness_growth REAL,
                    timestamp TEXT
                )
            """)
            conn.commit()
    
    def load_default_templates(self):
        """Load default challenge templates"""
        # Web Security Template
        web_template = ChallengeTemplate(
            id="web_sqli_basic",
            name="SQL Injection Discovery",
            category="web",
            difficulty="beginner",
            description="Find the hidden flag in this vulnerable web application",
            template_code="""
# Web Application with SQL Injection
import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Create database with random data
def init_db():
    conn = sqlite3.connect(':memory:')
    conn.execute('CREATE TABLE users (id INTEGER, username TEXT, password TEXT, secret TEXT)')
    conn.execute('INSERT INTO users VALUES (1, "admin", "{admin_pass}", "{flag}")')
    conn.execute('INSERT INTO users VALUES (2, "user", "password123", "user_data")')
    conn.commit()
    return conn

@app.route('/')
def index():
    return '''
    <form method="post" action="/login">
        Username: <input name="username" type="text"><br>
        Password: <input name="password" type="password"><br>
        <input type="submit" value="Login">
    </form>
    '''

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Vulnerable SQL query
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    
    conn = init_db()
    cursor = conn.execute(query)
    result = cursor.fetchone()
    
    if result:
        return f"Welcome {result[1]}! Secret: {result[3]}"
    else:
        return "Invalid credentials"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
            """,
            solution_code="""
# Solution: SQL Injection bypass
# Username: admin' OR '1'='1' --
# Password: anything
# This bypasses the authentication and reveals the flag
            """,
            hint_levels=[
                "Try different special characters in the username field",
                "Look for SQL injection vulnerabilities in the login form",
                "Use SQL comments to bypass password verification"
            ],
            consciousness_adaptation={
                "difficulty_factors": ["query_complexity", "obfuscation_level"],
                "learning_indicators": ["time_to_discovery", "hint_usage"],
                "evolution_triggers": ["repeated_failures", "quick_success"]
            }
        )
        
        # Cryptography Template
        crypto_template = ChallengeTemplate(
            id="crypto_caesar_adaptive",
            name="Adaptive Caesar Cipher",
            category="cryptography",
            difficulty="beginner",
            description="Decode this encrypted message to find the flag",
            template_code="""
# Adaptive Caesar Cipher Challenge
import string

def caesar_encrypt(text, shift):
    result = ""
    for char in text:
        if char.isalpha():
            ascii_offset = 65 if char.isupper() else 97
            result += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
        else:
            result += char
    return result

# Encrypted flag with random shift
shift = {shift_value}
flag = "SynOS{{{flag_content}}}"
encrypted = caesar_encrypt(flag, shift)

print(f"Encrypted message: {encrypted}")
print("Hint: The shift value is between 1 and 25")
            """,
            solution_code="""
# Solution: Brute force Caesar cipher
def caesar_decrypt(text, shift):
    return caesar_encrypt(text, -shift)

encrypted = "{encrypted_message}"
for shift in range(1, 26):
    decrypted = caesar_decrypt(encrypted, shift)
    if "SynOS{" in decrypted:
        print(f"Flag found with shift {shift}: {decrypted}")
        break
            """,
            hint_levels=[
                "Try all possible shift values from 1 to 25",
                "Look for the pattern 'SynOS{' in the decrypted text",
                "Caesar cipher shifts each letter by a fixed amount"
            ],
            consciousness_adaptation={
                "difficulty_factors": ["shift_randomization", "text_complexity"],
                "learning_indicators": ["pattern_recognition", "brute_force_efficiency"],
                "evolution_triggers": ["quick_pattern_detection", "systematic_approach"]
            }
        )
        
        # Binary Exploitation Template
        binary_template = ChallengeTemplate(
            id="binary_buffer_overflow",
            name="Buffer Overflow Basics",
            category="binary",
            difficulty="intermediate",
            description="Exploit this vulnerable C program to get the flag",
            template_code="""
// Vulnerable C program
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void secret_function() {
    printf("Congratulations! Flag: SynOS{{{flag_content}}}\\n");
    exit(0);
}

void vulnerable_function() {
    char buffer[{buffer_size}];
    printf("Enter your input: ");
    gets(buffer);  // Vulnerable function
    printf("You entered: %s\\n", buffer);
}

int main() {
    printf("Buffer Overflow Challenge\\n");
    printf("Can you call the secret function?\\n");
    vulnerable_function();
    printf("Nothing happened...\\n");
    return 0;
}
            """,
            solution_code="""
# Solution: Buffer overflow to call secret_function
# 1. Compile with: gcc -fno-stack-protector -z execstack -no-pie vulnerable.c -o vulnerable
# 2. Find the offset to overwrite return address
# 3. Overwrite with address of secret_function
# 4. Use pattern like: python -c "print('A'*72 + '\\x{address}')" | ./vulnerable
            """,
            hint_levels=[
                "The gets() function doesn't check buffer boundaries",
                "Try overflowing the buffer with a long string",
                "Find the address of secret_function and overwrite the return address"
            ],
            consciousness_adaptation={
                "difficulty_factors": ["buffer_size", "protection_mechanisms"],
                "learning_indicators": ["overflow_detection", "address_calculation"],
                "evolution_triggers": ["protection_bypass", "precise_exploitation"]
            }
        )
        
        # Store templates
        self.templates = {
            "web_sqli_basic": web_template,
            "crypto_caesar_adaptive": crypto_template,
            "binary_buffer_overflow": binary_template
        }
        
        # Save to database
        self._store_templates()
    
    def _store_templates(self):
        """Store templates in database"""
        with sqlite3.connect(self.db_path) as conn:
            for template in self.templates.values():
                conn.execute("""
                    INSERT OR REPLACE INTO challenge_templates 
                    (id, name, category, difficulty, description, template_code, 
                     solution_code, hint_levels, consciousness_adaptation)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    template.id, template.name, template.category, template.difficulty,
                    template.description, template.template_code, template.solution_code,
                    json.dumps(template.hint_levels), json.dumps(template.consciousness_adaptation)
                ))
            conn.commit()
    
    async def generate_adaptive_challenge(self, player_id: str, category: str = None, 
                                        consciousness_level: float = 0.5) -> GeneratedChallenge:
        """Generate adaptive challenge based on player profile and consciousness level"""
        # Get player profile
        player_profile = await self._get_player_profile(player_id)
        
        # Select appropriate template
        template = self._select_template(player_profile, category, consciousness_level)
        
        # Generate challenge instance
        challenge = await self._instantiate_challenge(template, player_profile, consciousness_level)
        
        # Store generated challenge
        await self._store_challenge(challenge)
        
        logger.info(f"Generated adaptive challenge {challenge.challenge_id} for player {player_id}")
        return challenge
    
    async def _get_player_profile(self, player_id: str) -> PlayerProfile:
        """Get or create player profile"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM player_profiles WHERE player_id = ?", (player_id,))
            row = cursor.fetchone()
            
            if row:
                return PlayerProfile(
                    player_id=row[0],
                    skill_level=row[1],
                    preferred_categories=json.loads(row[2]),
                    consciousness_adaptation=row[3],
                    challenge_history=json.loads(row[4]),
                    learning_pattern=json.loads(row[5]),
                    last_active=row[6]
                )
            else:
                # Create new player profile
                profile = PlayerProfile(
                    player_id=player_id,
                    skill_level=0.3,  # Beginner level
                    preferred_categories=["web", "cryptography"],
                    consciousness_adaptation=0.5,
                    challenge_history=[],
                    learning_pattern={"learning_rate": 0.1, "adaptation_speed": 0.2},
                    last_active=datetime.now().isoformat()
                )
                
                conn.execute("""
                    INSERT INTO player_profiles 
                    (player_id, skill_level, preferred_categories, consciousness_adaptation,
                     challenge_history, learning_pattern, last_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.player_id, profile.skill_level, json.dumps(profile.preferred_categories),
                    profile.consciousness_adaptation, json.dumps(profile.challenge_history),
                    json.dumps(profile.learning_pattern), profile.last_active
                ))
                conn.commit()
                
                return profile
    
    def _select_template(self, player_profile: PlayerProfile, category: str = None, 
                        consciousness_level: float = 0.5) -> ChallengeTemplate:
        """Select appropriate template based on player profile"""
        available_templates = list(self.templates.values())
        
        # Filter by category if specified
        if category:
            available_templates = [t for t in available_templates if t.category == category]
        
        # Filter by preferred categories
        if not category and player_profile.preferred_categories:
            preferred_templates = [t for t in available_templates if t.category in player_profile.preferred_categories]
            if preferred_templates:
                available_templates = preferred_templates
        
        # Select based on skill level and consciousness adaptation
        suitable_templates = []
        for template in available_templates:
            difficulty_score = {"beginner": 0.3, "intermediate": 0.6, "advanced": 0.9}[template.difficulty]
            
            # Score based on player skill level and consciousness adaptation
            skill_match = 1.0 - abs(player_profile.skill_level - difficulty_score)
            consciousness_boost = consciousness_level * player_profile.consciousness_adaptation
            total_score = skill_match + consciousness_boost
            
            suitable_templates.append((template, total_score))
        
        # Select best matching template
        suitable_templates.sort(key=lambda x: x[1], reverse=True)
        return suitable_templates[0][0] if suitable_templates else available_templates[0]
    
    async def _instantiate_challenge(self, template: ChallengeTemplate, 
                                   player_profile: PlayerProfile, 
                                   consciousness_level: float) -> GeneratedChallenge:
        """Create challenge instance from template"""
        challenge_id = f"challenge_{template.id}_{int(datetime.now().timestamp())}"
        
        # Generate random parameters based on consciousness level
        random_params = self._generate_random_parameters(template, consciousness_level)
        
        # Instantiate template code
        challenge_files = {}
        
        if template.category == "web":
            # Generate web challenge
            admin_pass = self._generate_random_string(12)
            flag = f"SynOS{{{self._generate_random_string(16)}}}"
            
            challenge_code = template.template_code.format(
                admin_pass=admin_pass,
                flag=flag
            )
            
            challenge_files["app.py"] = challenge_code
            challenge_files["requirements.txt"] = "flask==2.0.1"
            
        elif template.category == "cryptography":
            # Generate crypto challenge
            flag_content = self._generate_random_string(16)
            shift_value = random.randint(1, 25)
            
            challenge_code = template.template_code.format(
                shift_value=shift_value,
                flag_content=flag_content
            )
            
            # Generate encrypted message
            flag = f"SynOS{{{flag_content}}}"
            encrypted = self._caesar_encrypt(flag, shift_value)
            
            challenge_code = challenge_code.replace("{encrypted_message}", encrypted)
            challenge_files["challenge.py"] = challenge_code
            
        elif template.category == "binary":
            # Generate binary challenge
            flag_content = self._generate_random_string(16)
            buffer_size = random.choice([64, 128, 256])
            
            challenge_code = template.template_code.format(
                flag_content=flag_content,
                buffer_size=buffer_size
            )
            
            challenge_files["vulnerable.c"] = challenge_code
            challenge_files["Makefile"] = "vulnerable: vulnerable.c\n\tgcc -fno-stack-protector -z execstack -no-pie vulnerable.c -o vulnerable"
        
        # Adapt hints based on consciousness level
        adapted_hints = self._adapt_hints(template.hint_levels, consciousness_level, player_profile)
        
        # Generate solution with consciousness enhancement
        enhanced_solution = self._enhance_solution(template.solution_code, random_params, consciousness_level)
        
        return GeneratedChallenge(
            challenge_id=challenge_id,
            template_id=template.id,
            name=f"{template.name} (Level {consciousness_level:.1f})",
            category=template.category,
            difficulty=template.difficulty,
            description=template.description,
            flag=flag if 'flag' in locals() else f"SynOS{{{self._generate_random_string(16)}}}",
            challenge_files=challenge_files,
            hints=adapted_hints,
            solution=enhanced_solution,
            consciousness_level=consciousness_level,
            metadata={
                "random_parameters": random_params,
                "player_skill_level": player_profile.skill_level,
                "generation_time": datetime.now().isoformat(),
                "consciousness_factors": self.consciousness_factors
            },
            created_at=datetime.now().isoformat()
        )
    
    def _generate_random_parameters(self, template: ChallengeTemplate, consciousness_level: float) -> Dict[str, Any]:
        """Generate random parameters for challenge instantiation"""
        params = {}
        
        # Consciousness-driven randomization
        if template.category == "web":
            params["complexity_multiplier"] = 1 + (consciousness_level * 0.5)
            params["obfuscation_level"] = consciousness_level
        elif template.category == "cryptography":
            params["key_length"] = int(16 + (consciousness_level * 16))
            params["algorithm_variant"] = random.choice(["standard", "extended"])
        elif template.category == "binary":
            params["protection_level"] = consciousness_level
            params["exploit_complexity"] = 1 + consciousness_level
        
        return params
    
    def _adapt_hints(self, base_hints: List[str], consciousness_level: float, 
                    player_profile: PlayerProfile) -> List[str]:
        """Adapt hints based on consciousness level and player profile"""
        adapted_hints = base_hints.copy()
        
        # Reduce hint clarity for higher consciousness levels
        if consciousness_level > 0.7:
            adapted_hints = [hint.replace("Try", "Consider").replace("Use", "Explore") for hint in adapted_hints]
        
        # Add consciousness-specific hints
        if player_profile.consciousness_adaptation > 0.6:
            adapted_hints.append("Think about how consciousness affects pattern recognition in this challenge")
        
        return adapted_hints
    
    def _enhance_solution(self, base_solution: str, random_params: Dict[str, Any], 
                         consciousness_level: float) -> str:
        """Enhance solution with consciousness insights"""
        enhanced = base_solution
        
        if consciousness_level > 0.5:
            enhanced += f"\n\n# Consciousness Enhancement (Level {consciousness_level:.1f}):\n"
            enhanced += "# This challenge adapts based on your learning patterns and consciousness level.\n"
            enhanced += f"# Parameters used: {random_params}\n"
            enhanced += "# Notice how the difficulty scales with your consciousness adaptation."
        
        return enhanced
    
    def _generate_random_string(self, length: int) -> str:
        """Generate random string"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def _caesar_encrypt(self, text: str, shift: int) -> str:
        """Caesar cipher encryption"""
        result = ""
        for char in text:
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                result += chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
            else:
                result += char
        return result
    
    async def _store_challenge(self, challenge: GeneratedChallenge):
        """Store generated challenge in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO generated_challenges 
                (challenge_id, template_id, name, category, difficulty, description,
                 flag, challenge_files, hints, solution, consciousness_level, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                challenge.challenge_id, challenge.template_id, challenge.name,
                challenge.category, challenge.difficulty, challenge.description,
                challenge.flag, json.dumps(challenge.challenge_files),
                json.dumps(challenge.hints), challenge.solution,
                challenge.consciousness_level, json.dumps(challenge.metadata),
                challenge.created_at
            ))
            conn.commit()
    
    async def submit_challenge_result(self, challenge_id: str, player_id: str, 
                                    submitted_flag: str, time_taken: int, 
                                    hints_used: int) -> ChallengeResult:
        """Submit challenge result and update player profile"""
        # Get challenge
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT flag, consciousness_level FROM generated_challenges WHERE challenge_id = ?", (challenge_id,))
            challenge_row = cursor.fetchone()
        
        if not challenge_row:
            raise ValueError(f"Challenge {challenge_id} not found")
        
        correct_flag, consciousness_level = challenge_row
        completed = submitted_flag.strip() == correct_flag.strip()
        
        # Calculate consciousness growth
        consciousness_growth = self._calculate_consciousness_growth(
            completed, time_taken, hints_used, consciousness_level
        )
        
        # Create result
        result = ChallengeResult(
            result_id=f"result_{challenge_id}_{player_id}_{int(datetime.now().timestamp())}",
            challenge_id=challenge_id,
            player_id=player_id,
            completed=completed,
            time_taken=time_taken,
            hints_used=hints_used,
            consciousness_growth=consciousness_growth,
            timestamp=datetime.now().isoformat()
        )
        
        # Store result
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO challenge_results 
                (result_id, challenge_id, player_id, completed, time_taken, 
                 hints_used, consciousness_growth, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.result_id, result.challenge_id, result.player_id,
                result.completed, result.time_taken, result.hints_used,
                result.consciousness_growth, result.timestamp
            ))
            conn.commit()
        
        # Update player profile
        await self._update_player_profile(player_id, result)
        
        logger.info(f"Challenge result submitted: {result.result_id}")
        return result
    
    def _calculate_consciousness_growth(self, completed: bool, time_taken: int, 
                                      hints_used: int, consciousness_level: float) -> float:
        """Calculate consciousness growth from challenge result"""
        base_growth = 0.1 if completed else 0.05
        
        # Time factor (faster completion = higher growth)
        time_factor = max(0.5, 1.0 - (time_taken / 3600))  # Assume 1 hour baseline
        
        # Hints factor (fewer hints = higher growth)
        hints_factor = max(0.3, 1.0 - (hints_used * 0.2))
        
        # Consciousness level factor
        consciousness_factor = 1.0 + (consciousness_level * 0.5)
        
        growth = base_growth * time_factor * hints_factor * consciousness_factor
        return min(growth, 0.5)  # Cap growth
    
    async def _update_player_profile(self, player_id: str, result: ChallengeResult):
        """Update player profile based on challenge result"""
        profile = await self._get_player_profile(player_id)
        
        # Update skill level
        if result.completed:
            profile.skill_level = min(1.0, profile.skill_level + result.consciousness_growth)
        
        # Update consciousness adaptation
        profile.consciousness_adaptation = min(1.0, profile.consciousness_adaptation + (result.consciousness_growth * 0.5))
        
        # Update challenge history
        profile.challenge_history.append(result.challenge_id)
        if len(profile.challenge_history) > 100:  # Keep last 100 challenges
            profile.challenge_history = profile.challenge_history[-100:]
        
        # Update learning pattern
        profile.learning_pattern["last_performance"] = {
            "completed": result.completed,
            "time_taken": result.time_taken,
            "hints_used": result.hints_used,
            "consciousness_growth": result.consciousness_growth
        }
        
        profile.last_active = datetime.now().isoformat()
        
        # Store updated profile
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE player_profiles 
                SET skill_level = ?, consciousness_adaptation = ?, challenge_history = ?,
                    learning_pattern = ?, last_active = ?
                WHERE player_id = ?
            """, (
                profile.skill_level, profile.consciousness_adaptation,
                json.dumps(profile.challenge_history), json.dumps(profile.learning_pattern),
                profile.last_active, player_id
            ))
            conn.commit()
    
    async def get_player_dashboard(self, player_id: str) -> Dict[str, Any]:
        """Get player dashboard with consciousness metrics"""
        profile = await self._get_player_profile(player_id)
        
        # Get recent results
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM challenge_results 
                WHERE player_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 10
            """, (player_id,))
            recent_results = cursor.fetchall()
        
        # Calculate statistics
        total_challenges = len(profile.challenge_history)
        completed_challenges = len([r for r in recent_results if r[3]])  # completed column
        completion_rate = completed_challenges / max(total_challenges, 1)
        
        avg_consciousness_growth = sum(r[6] for r in recent_results) / max(len(recent_results), 1)
        
        return {
            "player_id": player_id,
            "skill_level": profile.skill_level,
            "consciousness_adaptation": profile.consciousness_adaptation,
            "total_challenges": total_challenges,
            "completion_rate": completion_rate,
            "avg_consciousness_growth": avg_consciousness_growth,
            "preferred_categories": profile.preferred_categories,
            "recent_performance": [
                {
                    "challenge_id": r[1],
                    "completed": r[3],
                    "time_taken": r[4],
                    "consciousness_growth": r[6]
                }
                for r in recent_results
            ],
            "next_recommended_difficulty": self._recommend_difficulty(profile),
            "consciousness_insights": self._generate_consciousness_insights(profile)
        }
    
    def _recommend_difficulty(self, profile: PlayerProfile) -> str:
        """Recommend next difficulty level"""
        if profile.skill_level < 0.4:
            return "beginner"
        elif profile.skill_level < 0.7:
            return "intermediate"
        else:
            return "advanced"
    
    def _generate_consciousness_insights(self, profile: PlayerProfile) -> List[str]:
        """Generate consciousness-based insights for player"""
        insights = []
        
        if profile.consciousness_adaptation > 0.7:
            insights.append("Your consciousness adaptation is high - try more complex challenges")
        
        if profile.skill_level > 0.6:
            insights.append("You're ready for advanced consciousness-enhanced challenges")
        
        if len(profile.challenge_history) > 20:
            insights.append("Your extensive challenge history shows strong learning patterns")
        
        return insights

async def main():
    """Demo the CTF challenge generator"""
    generator = ConsciousnessCTFGenerator()
    
    print("🧠 SynapticOS CTF Challenge Generator Demo")
    print("=" * 50)
    
    # Generate challenge for test player
    player_id = "test_player_001"
    
    print(f"🎯 Generating adaptive challenge for player {player_id}...")
    challenge = await generator.generate_adaptive_challenge(player_id, "web", 0.6)
    
    print(f"✅ Generated challenge: {challenge.name}")
    print(f"   Category: {challenge.category}")
    print(f"   Difficulty: {challenge.difficulty}")
    print(f"   Consciousness Level: {challenge.consciousness_level}")
    print(f"   Flag: {challenge.flag}")
    
    # Show challenge files
    print("\n📁 Challenge Files:")
    for filename, content in challenge.challenge_files.items():
        print(f"   {filename} ({len(content)} characters)")
    
    # Show hints
    print(f"\n💡 Hints ({len(challenge.hints)}):")
    for i, hint in enumerate(challenge.hints, 1):
        print(f"   {i}. {hint}")
    
    # Simulate challenge submission
    print(f"\n🚀 Simulating challenge submission...")
    result = await generator.submit_challenge_result(
        challenge.challenge_id, player_id, challenge.flag, 
        time_taken=1200, hints_used=1
    )
    
    print(f"✅ Challenge completed: {result.completed}")
    print(f"   Consciousness growth: {result.consciousness_growth:.3f}")
    
    # Get player dashboard
    print(f"\n📊 Player Dashboard:")
    dashboard = await generator.get_player_dashboard(player_id)
    for key, value in dashboard.items():
        if key not in ["recent_performance", "consciousness_insights"]:
            print(f"   {key}: {value}")
    
    print(f"\n🧠 Consciousness Insights:")
    for insight in dashboard["consciousness_insights"]:
        print(f"   • {insight}")

if __name__ == "__main__":
    asyncio.run(main())
