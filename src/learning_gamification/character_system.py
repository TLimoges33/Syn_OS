#!/usr/bin/env python3
"""
Gamified Character System for Syn_OS Learning Platform
RPG-style character progression with cybersecurity specializations
"""

import asyncio
import logging
import time
import json
import hashlib
import secrets
import os
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import uuid
from datetime import datetime, timedelta

# Mock imports for development - replace with actual imports when available
try:
    from src.consciousness_v2.consciousness_bus import ConsciousnessBus, ConsciousnessState
except ImportError:
    class ConsciousnessState:
        def __init__(self):
            self.overall_consciousness_level = 0.7
            self.neural_populations = {}
            self.timestamp = time.time()
    
    class ConsciousnessBus:
        async def get_consciousness_state(self):
            return ConsciousnessState()

try:
    from src.security.audit_logger import AuditLogger
except ImportError:
    class AuditLogger:
        async def log_system_event(self, event_type, details):
            pass


class CharacterClass(Enum):
    """Cybersecurity character classes"""
    PENETRATION_TESTER = "penetration_tester"
    INCIDENT_RESPONDER = "incident_responder"
    THREAT_HUNTER = "threat_hunter"
    SECURITY_ANALYST = "security_analyst"
    FORENSICS_INVESTIGATOR = "forensics_investigator"
    MALWARE_ANALYST = "malware_analyst"
    NETWORK_DEFENDER = "network_defender"
    CRYPTOGRAPHER = "cryptographer"
    SOCIAL_ENGINEER = "social_engineer"
    COMPLIANCE_AUDITOR = "compliance_auditor"


class SkillCategory(Enum):
    """Skill categories in cybersecurity"""
    RECONNAISSANCE = "reconnaissance"
    VULNERABILITY_ASSESSMENT = "vulnerability_assessment"
    EXPLOITATION = "exploitation"
    POST_EXPLOITATION = "post_exploitation"
    DEFENSE = "defense"
    FORENSICS = "forensics"
    CRYPTOGRAPHY = "cryptography"
    SOCIAL_ENGINEERING = "social_engineering"
    COMPLIANCE = "compliance"
    PROGRAMMING = "programming"
    NETWORKING = "networking"
    OPERATING_SYSTEMS = "operating_systems"


class EthicalAlignment(Enum):
    """Ethical alignment system"""
    WHITE_HAT = "white_hat"
    GREY_HAT = "grey_hat"
    BLACK_HAT = "black_hat"


class QuestType(Enum):
    """Types of learning quests"""
    TUTORIAL = "tutorial"
    CHALLENGE = "challenge"
    CTF = "ctf"
    SIMULATION = "simulation"
    CERTIFICATION_PREP = "certification_prep"
    REAL_WORLD_SCENARIO = "real_world_scenario"
    TEAM_MISSION = "team_mission"
    CLAN_WAR = "clan_war"


class QuestDifficulty(Enum):
    """Quest difficulty levels"""
    NOVICE = "novice"
    APPRENTICE = "apprentice"
    JOURNEYMAN = "journeyman"
    EXPERT = "expert"
    MASTER = "master"
    GRANDMASTER = "grandmaster"


@dataclass
class Skill:
    """Individual skill in the grimoire"""
    skill_id: str
    name: str
    category: SkillCategory
    description: str
    level: int
    experience: int
    max_level: int
    prerequisites: List[str]
    tools_unlocked: List[str]
    legal_warnings: List[str]
    ethical_impact: int  # -100 to +100
    real_world_applications: List[str]
    certification_relevance: List[str]


@dataclass
class Character:
    """Player character with RPG-style attributes"""
    character_id: str
    username: str
    display_name: str
    character_class: CharacterClass
    level: int
    experience: int
    total_experience: int
    
    # Core attributes (0-100)
    technical_prowess: int
    analytical_thinking: int
    creativity: int
    persistence: int
    ethical_awareness: int
    communication: int
    
    # Ethical alignment (-100 to +100)
    ethical_score: int
    alignment: EthicalAlignment
    
    # Skills and progression
    skills: Dict[str, Skill]
    completed_quests: List[str]
    active_quests: List[str]
    achievements: List[str]
    
    # Social features
    clan_id: Optional[str]
    team_id: Optional[str]
    mentor_id: Optional[str]
    mentees: List[str]
    
    # Statistics
    quests_completed: int
    ctf_wins: int
    certifications_earned: List[str]
    tools_mastered: List[str]
    vulnerabilities_found: int
    incidents_resolved: int
    
    # Timestamps
    created_at: float
    last_active: float
    
    # Metadata
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    preferred_learning_style: Optional[str] = None


@dataclass
class Quest:
    """Learning quest with gamification elements"""
    quest_id: str
    title: str
    description: str
    quest_type: QuestType
    difficulty: QuestDifficulty
    category: SkillCategory
    
    # Requirements
    prerequisites: List[str]
    required_level: int
    required_skills: Dict[str, int]
    
    # Rewards
    experience_reward: int
    skill_experience: Dict[str, int]
    tools_unlocked: List[str]
    achievements_unlocked: List[str]
    
    # Ethical considerations
    ethical_impact: int
    legal_warnings: List[str]
    ethical_choices: List[Dict[str, Any]]
    
    # Content
    learning_objectives: List[str]
    tasks: List[Dict[str, Any]]
    resources: List[str]
    hints: List[str]
    
    # Team features
    team_quest: bool
    max_team_size: int
    clan_exclusive: bool
    
    # Metadata
    estimated_duration: int  # minutes
    created_by: str
    created_at: float
    updated_at: float
    completion_rate: float
    average_rating: float


@dataclass
class Achievement:
    """Achievement system"""
    achievement_id: str
    name: str
    description: str
    icon: str
    category: str
    rarity: str  # common, uncommon, rare, epic, legendary
    points: int
    requirements: Dict[str, Any]
    unlocked_by: List[str]  # character IDs
    created_at: float


@dataclass
class Clan:
    """Clan/guild system for team learning"""
    clan_id: str
    name: str
    description: str
    tag: str  # 3-4 character clan tag
    leader_id: str
    officers: List[str]
    members: List[str]
    
    # Clan stats
    total_experience: int
    level: int
    reputation: int
    
    # Clan features
    clan_quests: List[str]
    clan_achievements: List[str]
    clan_wars_won: int
    clan_wars_lost: int
    
    # Settings
    recruitment_open: bool
    required_level: int
    clan_motto: str
    
    # Timestamps
    created_at: float
    last_active: float


class CharacterSystem:
    """
    Gamified character progression system for cybersecurity learning
    """
    
    def __init__(self, consciousness_bus: ConsciousnessBus):
        """Initialize character system"""
        self.consciousness_bus = consciousness_bus
        self.audit_logger = AuditLogger()
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.system_directory = "/var/lib/synos/learning_gamification"
        self.database_file = os.path.join(self.system_directory, "character_system.db")
        
        # In-memory caches
        self.characters: Dict[str, Character] = {}
        self.quests: Dict[str, Quest] = {}
        self.achievements: Dict[str, Achievement] = {}
        self.clans: Dict[str, Clan] = {}
        
        # Skill definitions
        self.skill_definitions = self._initialize_skill_definitions()
        
        # Experience tables
        self.level_experience_table = self._generate_experience_table()
        
        # Initialize system
        asyncio.create_task(self._initialize_system())
    
    async def _initialize_system(self):
        """Initialize the character system"""
        try:
            self.logger.info("Initializing character system...")
            
            # Create directory
            os.makedirs(self.system_directory, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Load existing data
            await self._load_characters()
            await self._load_quests()
            await self._load_achievements()
            await self._load_clans()
            
            # Create default content
            await self._create_default_quests()
            await self._create_default_achievements()
            
            self.logger.info("Character system initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing character system: {e}")
    
    async def _initialize_database(self):
        """Initialize the character system database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Characters table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS characters (
                    character_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    display_name TEXT NOT NULL,
                    character_class TEXT NOT NULL,
                    level INTEGER NOT NULL,
                    experience INTEGER NOT NULL,
                    total_experience INTEGER NOT NULL,
                    technical_prowess INTEGER NOT NULL,
                    analytical_thinking INTEGER NOT NULL,
                    creativity INTEGER NOT NULL,
                    persistence INTEGER NOT NULL,
                    ethical_awareness INTEGER NOT NULL,
                    communication INTEGER NOT NULL,
                    ethical_score INTEGER NOT NULL,
                    alignment TEXT NOT NULL,
                    skills TEXT,
                    completed_quests TEXT,
                    active_quests TEXT,
                    achievements TEXT,
                    clan_id TEXT,
                    team_id TEXT,
                    mentor_id TEXT,
                    mentees TEXT,
                    quests_completed INTEGER NOT NULL,
                    ctf_wins INTEGER NOT NULL,
                    certifications_earned TEXT,
                    tools_mastered TEXT,
                    vulnerabilities_found INTEGER NOT NULL,
                    incidents_resolved INTEGER NOT NULL,
                    created_at REAL NOT NULL,
                    last_active REAL NOT NULL,
                    avatar_url TEXT,
                    bio TEXT,
                    location TEXT,
                    preferred_learning_style TEXT
                )
            ''')
            
            # Quests table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quests (
                    quest_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    quest_type TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    category TEXT NOT NULL,
                    prerequisites TEXT,
                    required_level INTEGER NOT NULL,
                    required_skills TEXT,
                    experience_reward INTEGER NOT NULL,
                    skill_experience TEXT,
                    tools_unlocked TEXT,
                    achievements_unlocked TEXT,
                    ethical_impact INTEGER NOT NULL,
                    legal_warnings TEXT,
                    ethical_choices TEXT,
                    learning_objectives TEXT,
                    tasks TEXT,
                    resources TEXT,
                    hints TEXT,
                    team_quest BOOLEAN NOT NULL,
                    max_team_size INTEGER NOT NULL,
                    clan_exclusive BOOLEAN NOT NULL,
                    estimated_duration INTEGER NOT NULL,
                    created_by TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    completion_rate REAL NOT NULL,
                    average_rating REAL NOT NULL
                )
            ''')
            
            # Achievements table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    achievement_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    icon TEXT,
                    category TEXT NOT NULL,
                    rarity TEXT NOT NULL,
                    points INTEGER NOT NULL,
                    requirements TEXT,
                    unlocked_by TEXT,
                    created_at REAL NOT NULL
                )
            ''')
            
            # Clans table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clans (
                    clan_id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    tag TEXT UNIQUE NOT NULL,
                    leader_id TEXT NOT NULL,
                    officers TEXT,
                    members TEXT,
                    total_experience INTEGER NOT NULL,
                    level INTEGER NOT NULL,
                    reputation INTEGER NOT NULL,
                    clan_quests TEXT,
                    clan_achievements TEXT,
                    clan_wars_won INTEGER NOT NULL,
                    clan_wars_lost INTEGER NOT NULL,
                    recruitment_open BOOLEAN NOT NULL,
                    required_level INTEGER NOT NULL,
                    clan_motto TEXT,
                    created_at REAL NOT NULL,
                    last_active REAL NOT NULL
                )
            ''')
            
            # Quest completions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quest_completions (
                    completion_id TEXT PRIMARY KEY,
                    character_id TEXT NOT NULL,
                    quest_id TEXT NOT NULL,
                    completed_at REAL NOT NULL,
                    experience_gained INTEGER NOT NULL,
                    ethical_choice_made TEXT,
                    rating INTEGER,
                    feedback TEXT,
                    FOREIGN KEY (character_id) REFERENCES characters (character_id),
                    FOREIGN KEY (quest_id) REFERENCES quests (quest_id)
                )
            ''')
            
            # Leaderboards table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leaderboard_entries (
                    entry_id TEXT PRIMARY KEY,
                    character_id TEXT NOT NULL,
                    leaderboard_type TEXT NOT NULL,
                    period TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    rank INTEGER NOT NULL,
                    timestamp REAL NOT NULL,
                    FOREIGN KEY (character_id) REFERENCES characters (character_id)
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_characters_level ON characters (level)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_characters_clan ON characters (clan_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_quest_completions_character ON quest_completions (character_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_leaderboard_type_period ON leaderboard_entries (leaderboard_type, period)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    def _initialize_skill_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize skill definitions for the grimoire"""
        return {
            # Reconnaissance Skills
            "passive_reconnaissance": {
                "name": "Passive Reconnaissance",
                "category": SkillCategory.RECONNAISSANCE,
                "description": "Gather information without directly interacting with target systems",
                "max_level": 100,
                "tools_unlocked": ["whois", "dig", "nslookup", "shodan", "google_dorking"],
                "legal_warnings": [
                    "Always ensure you have proper authorization before conducting reconnaissance",
                    "Passive reconnaissance should only be performed on systems you own or have explicit permission to test",
                    "Be aware of terms of service for search engines and databases"
                ],
                "ethical_impact": 10,
                "real_world_applications": [
                    "Bug bounty programs",
                    "Penetration testing",
                    "Threat intelligence gathering",
                    "Security assessments"
                ],
                "certification_relevance": ["CEH", "OSCP", "CISSP", "GCIH"]
            },
            
            "active_reconnaissance": {
                "name": "Active Reconnaissance",
                "category": SkillCategory.RECONNAISSANCE,
                "description": "Directly interact with target systems to gather information",
                "max_level": 100,
                "prerequisites": ["passive_reconnaissance"],
                "tools_unlocked": ["nmap", "masscan", "zmap", "nikto", "dirb"],
                "legal_warnings": [
                    "CRITICAL: Active reconnaissance can be considered unauthorized access",
                    "Only perform on systems you own or have explicit written permission",
                    "Unauthorized scanning can violate computer fraud and abuse laws",
                    "Always check local and international laws before proceeding"
                ],
                "ethical_impact": -20,
                "real_world_applications": [
                    "Authorized penetration testing",
                    "Internal security assessments",
                    "Vulnerability management"
                ],
                "certification_relevance": ["CEH", "OSCP", "GPEN"]
            },
            
            # Vulnerability Assessment
            "vulnerability_scanning": {
                "name": "Vulnerability Scanning",
                "category": SkillCategory.VULNERABILITY_ASSESSMENT,
                "description": "Identify security weaknesses in systems and applications",
                "max_level": 100,
                "tools_unlocked": ["nessus", "openvas", "qualys", "rapid7", "burp_suite"],
                "legal_warnings": [
                    "Vulnerability scanning must be authorized by system owners",
                    "Unauthorized scanning may violate computer crime laws",
                    "Always have proper documentation and approval"
                ],
                "ethical_impact": 30,
                "real_world_applications": [
                    "Compliance auditing",
                    "Risk assessment",
                    "Security monitoring",
                    "Patch management"
                ],
                "certification_relevance": ["CISSP", "CISA", "GSEC", "CompTIA Security+"]
            },
            
            # Exploitation Skills
            "web_application_exploitation": {
                "name": "Web Application Exploitation",
                "category": SkillCategory.EXPLOITATION,
                "description": "Exploit vulnerabilities in web applications",
                "max_level": 100,
                "prerequisites": ["vulnerability_scanning"],
                "tools_unlocked": ["burp_suite", "owasp_zap", "sqlmap", "metasploit", "custom_exploits"],
                "legal_warnings": [
                    "DANGER: Exploitation without authorization is illegal",
                    "Only exploit vulnerabilities in authorized environments",
                    "Unauthorized access can result in criminal charges",
                    "Always follow responsible disclosure practices"
                ],
                "ethical_impact": -50,
                "real_world_applications": [
                    "Authorized penetration testing",
                    "Bug bounty programs",
                    "Security research",
                    "Red team exercises"
                ],
                "certification_relevance": ["OSCP", "OSWE", "GWAPT", "CEH"]
            },
            
            # Defense Skills
            "incident_response": {
                "name": "Incident Response",
                "category": SkillCategory.DEFENSE,
                "description": "Respond to and contain security incidents",
                "max_level": 100,
                "tools_unlocked": ["volatility", "autopsy", "wireshark", "splunk", "elk_stack"],
                "legal_warnings": [
                    "Preserve chain of custody for evidence",
                    "Follow legal requirements for incident reporting",
                    "Understand privacy laws when handling incident data"
                ],
                "ethical_impact": 80,
                "real_world_applications": [
                    "SOC operations",
                    "Digital forensics",
                    "Malware analysis",
                    "Threat hunting"
                ],
                "certification_relevance": ["GCIH", "GCFA", "GNFA", "CISSP"]
            },
            
            # Add more skills...
        }
    
    def _generate_experience_table(self) -> Dict[int, int]:
        """Generate experience requirements for each level"""
        experience_table = {}
        base_exp = 100
        
        for level in range(1, 101):  # Levels 1-100
            if level == 1:
                experience_table[level] = 0
            else:
                # Exponential growth with some balancing
                multiplier = 1.1 + (level * 0.01)
                experience_table[level] = int(base_exp * (multiplier ** (level - 1)))
        
        return experience_table
    
    async def create_character(self, username: str, display_name: str, 
                             character_class: CharacterClass) -> str:
        """Create a new character"""
        try:
            character_id = str(uuid.uuid4())
            current_time = time.time()
            
            # Initialize starting skills based on character class
            starting_skills = self._get_starting_skills(character_class)
            
            character = Character(
                character_id=character_id,
                username=username,
                display_name=display_name,
                character_class=character_class,
                level=1,
                experience=0,
                total_experience=0,
                
                # Starting attributes (randomized with class bonuses)
                technical_prowess=self._get_starting_attribute(character_class, "technical"),
                analytical_thinking=self._get_starting_attribute(character_class, "analytical"),
                creativity=self._get_starting_attribute(character_class, "creativity"),
                persistence=self._get_starting_attribute(character_class, "persistence"),
                ethical_awareness=75,  # Start with high ethical awareness
                communication=self._get_starting_attribute(character_class, "communication"),
                
                # Ethical alignment starts neutral
                ethical_score=0,
                alignment=EthicalAlignment.WHITE_HAT,
                
                # Initialize collections
                skills=starting_skills,
                completed_quests=[],
                active_quests=[],
                achievements=[],
                
                # Social features
                clan_id=None,
                team_id=None,
                mentor_id=None,
                mentees=[],
                
                # Statistics
                quests_completed=0,
                ctf_wins=0,
                certifications_earned=[],
                tools_mastered=[],
                vulnerabilities_found=0,
                incidents_resolved=0,
                
                # Timestamps
                created_at=current_time,
                last_active=current_time
            )
            
            # Store character
            await self._store_character(character)
            self.characters[character_id] = character
            
            # Award starting achievement
            await self._award_achievement(character_id, "first_steps")
            
            # Log character creation
            await self.audit_logger.log_system_event(
                event_type="character_created",
                details={
                    "character_id": character_id,
                    "username": username,
                    "character_class": character_class.value,
                    "starting_level": 1
                }
            )
            
            self.logger.info(f"Created character: {username} ({character_class.value})")
            return character_id
            
        except Exception as e:
            self.logger.error(f"Error creating character: {e}")
            raise
    
    def _get_starting_skills(self, character_class: CharacterClass) -> Dict[str, Skill]:
        """Get starting skills based on character class"""
        starting_skills = {}
        
        # Base skills for all classes
        base_skills = ["basic_security_awareness", "ethical_hacking_fundamentals"]
        
        # Class-specific starting skills
        class_skills = {
            CharacterClass.PENETRATION_TESTER: ["passive_reconnaissance", "vulnerability_scanning"],
            CharacterClass.INCIDENT_RESPONDER: ["incident_response", "digital_forensics_basics"],
            CharacterClass.THREAT_HUNTER: ["threat_intelligence", "log_analysis"],
            CharacterClass.SECURITY_ANALYST: ["security_monitoring", "risk_assessment"],
            CharacterClass.FORENSICS_INVESTIGATOR: ["digital_forensics", "evidence_handling"],
            CharacterClass.MALWARE_ANALYST: ["malware_analysis", "reverse_engineering_basics"],
            CharacterClass.NETWORK_DEFENDER: ["network_security", "firewall_management"],
            CharacterClass.CRYPTOGRAPHER: ["cryptography_fundamentals", "key_management"],
            CharacterClass.SOCIAL_ENGINEER: ["social_engineering_awareness", "phishing_detection"],
            CharacterClass.COMPLIANCE_AUDITOR: ["compliance_frameworks", "audit_procedures"]
        }
        
        all_skills = base_skills + class_skills.get(character_class, [])
        
        for skill_name in all_skills:
            if skill_name in self.skill_definitions:
                skill_def = self.skill_definitions[skill_name]
                skill = Skill(
                    skill_id=str(uuid.uuid4()),
                    name=skill_def["name"],
                    category=skill_def["category"],
                    description=skill_def["description"],
                    level=1,
                    experience=0,
                    max_level=skill_def["max_level"],
                    prerequisites=skill_def.get("prerequisites", []),
                    tools_unlocked=skill_def.get("tools_unlocked", []),
                    legal_warnings=skill_def.get("legal_warnings", []),
                    ethical_impact=skill_def.get("ethical_impact", 0),
                    real_world_applications=skill_def.get("real_world_applications", []),
                    certification_relevance=skill_def.get("certification_relevance", [])
                )
                starting_skills[skill_name] = skill
        
        return starting_skills
    
    def _get_starting_attribute(self, character_class: CharacterClass, attribute: str) -> int:
        """Get starting attribute value based on character class"""
        base_value = 50
        
        # Class bonuses
        class_bonuses = {
            CharacterClass.PENETRATION_TESTER: {
                "technical": 15, "analytical": 10, "creativity": 15, "communication": 5
            },
            CharacterClass.INCIDENT_RESPONDER: {
                "technical": 10, "analytical": 15, "persistence": 15, "communication": 10
            },
            CharacterClass.THREAT_HUNTER: {
                "analytical": 20, "persistence": 15, "technical": 10, "creativity": 5
            },
            CharacterClass.SECURITY_ANALYST: {
                "analytical": 15, "technical": 10, "communication": 10, "persistence": 10
            },
            CharacterClass.FORENSICS_INVESTIGATOR: {
                "analytical": 20, "persistence": 15, "technical": 10, "communication": 5
            },
            CharacterClass.MALWARE_ANALYST: {
                "technical": 20, "analytical": 15, "persistence": 10, "creativity": 5
            },
            CharacterClass.NETWORK_DEFENDER: {
                "technical": 15, "analytical": 10, "persistence": 15, "communication": 5
            },
            CharacterClass.CRYPTOGRAPHER: {
                "technical": 20, "analytical": 20, "creativity": 5, "communication": 0
            },
            CharacterClass.SOCIAL_ENGINEER: {
                "creativity": 20, "communication": 20, "analytical": 5, "technical": 0
            },
            CharacterClass.COMPLIANCE_AUDITOR: {
                "analytical": 15, "communication": 15, "persistence": 10, "technical": 5
            }
        }
        
        bonus = class_bonuses.get(character_class, {}).get(attribute, 0)
        return min(100, base_value + bonus + secrets.randbelow(11) - 5)  # ±5 random
    
    async def _store_character(self, character: Character):
        """Store character in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO characters 
                (character_id, username, display_name, character_class, level, experience, total_experience,
                 technical_prowess, analytical_thinking, creativity, persistence, ethical_awareness, communication,
                 ethical_score, alignment, skills, completed_quests, active_quests, achievements,
                 clan_id, team_id, mentor_id, mentees, quests_completed, ctf_wins, certifications_earned,
                 tools_mastered, vulnerabilities_found, incidents_resolved, created_at, last_active,
                 avatar_url, bio, location, preferred_learning_style)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                character.character_id, character.username, character.display_name, character.character_class.value,
                character.level, character.experience, character.total_experience,
                character.technical_prowess, character.analytical_thinking, character.creativity,
                character.persistence, character.ethical_awareness, character.communication,
                character.ethical_score, character.alignment.value,
                json.dumps({k: asdict(v) for k, v in character.skills.items()}),
                json.dumps(character.completed_quests), json.dumps(character.active_quests),
                json.dumps(character.achievements), character.clan_id, character.team_id,
                character.mentor_id, json.dumps(character.mentees), character.quests_completed,
                character.ctf_wins, json.dumps(character.certifications_earned),
                json.dumps(character.tools_mastered), character.vulnerabilities_found,
                character.incidents_resolved, character.created_at, character.last_active,
                character.avatar_url, character.bio, character.location, character.preferred_learning_style
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing character: {e}")
            raise
    
    async def _load_characters(self):
        """Load characters from database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM characters')
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                # Reconstruct character object
                skills_data = json.loads(row[15]) if row[15] else {}
                skills = {}
                for skill_name, skill_data in skills_data.items():
                    skills[skill_name] = Skill(**skill_data)
                
                character = Character(
                    character_id=row[0],
                    username=row[1],
                    display_name=row[2],
                    character_class=CharacterClass(row[3]),
                    level=row[4],
                    experience=row[5],
                    total_experience=row[6],
                    technical_prowess=row[7],
                    analytical_thinking=row[8],
                    creativity=row[9],
                    persistence=row[10],
                    ethical_awareness=row[11],
                    communication=row[12],
                    ethical_score=row[13],
                    alignment=EthicalAlignment(row[14]),
                    skills=skills,
                    completed_quests=json.loads(row[16]) if row[16] else [],
                    active_quests=json.loads(row[17]) if row[17] else [],
                    achievements=json.loads(row[18]) if row[18] else [],
                    clan_id=row[19],
                    team_id=row[20],
                    mentor_id=row[21],
                    mentees=json.loads(row[22]) if row[22] else [],
                    quests_completed=row[23],
                    ctf_wins=row[24],
                    certifications_earned=json.loads(row[25]) if row[25] else [],
                    tools_mastered=json.loads(row[26]) if row[26] else [],
                    vulnerabilities_found=row[27],
                    incidents_resolved=row[28],
                    created_at=row[29],
                    last_active=row[30],
                    avatar_url=row[31],
                    bio=row[32],
                    location=row[33],
                    preferred_learning_style=row[34]
                )
                
                self.characters[character.character_id] = character
            
            self.logger.info(f"Loaded {len(self.characters)} characters")
            
        except Exception as e:
            self.logger.error(f"Error loading characters: {e}")
    
    async def _load_quests(self):
        """Load quests from database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM quests')
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                quest = Quest(
                    quest_id=row[0], title=row[1], description=row[2],
                    quest_type=QuestType(row[3]), difficulty=QuestDifficulty(row[4]),
                    category=SkillCategory(row[5]), prerequisites=json.loads(row[6]) if row[6] else [],
                    required_level=row[7], required_skills=json.loads(row[8]) if row[8] else {},
                    experience_reward=row[9], skill_experience=json.loads(row[10]) if row[10] else {},
                    tools_unlocked=json.loads(row[11]) if row[11] else [],
                    achievements_unlocked=json.loads(row[12]) if row[12] else [],
                    ethical_impact=row[13], legal_warnings=json.loads(row[14]) if row[14] else [],
                    ethical_choices=json.loads(row[15]) if row[15] else [],
                    learning_objectives=json.loads(row[16]) if row[16] else [],
                    tasks=json.loads(row[17]) if row[17] else [],
                    resources=json.loads(row[18]) if row[18] else [],
                    hints=json.loads(row[19]) if row[19] else [],
                    team_quest=row[20], max_team_size=row[21], clan_exclusive=row[22],
                    estimated_duration=row[23], created_by=row[24], created_at=row[25],
                    updated_at=row[26], completion_rate=row[27], average_rating=row[28]
                )
                
                self.quests[quest.quest_id] = quest
            
            self.logger.info(f"Loaded {len(self.quests)} quests")
            
        except Exception as e:
            self.logger.error(f"Error loading quests: {e}")
    
    async def _load_achievements(self):
        """Load achievements from database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM achievements')
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                achievement = Achievement(
                    achievement_id=row[0], name=row[1], description=row[2],
                    icon=row[3], category=row[4], rarity=row[5], points=row[6],
                    requirements=json.loads(row[7]) if row[7] else {},
                    unlocked_by=json.loads(row[8]) if row[8] else [],
                    created_at=row[9]
                )
                
                self.achievements[achievement.achievement_id] = achievement
            
            self.logger.info(f"Loaded {len(self.achievements)} achievements")
            
        except Exception as e:
            self.logger.error(f"Error loading achievements: {e}")
    
    async def _load_clans(self):
        """Load clans from database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM clans')
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                clan = Clan(
                    clan_id=row[0], name=row[1], description=row[2], tag=row[3],
                    leader_id=row[4], officers=json.loads(row[5]) if row[5] else [],
                    members=json.loads(row[6]) if row[6] else [],
                    total_experience=row[7], level=row[8], reputation=row[9],
                    clan_quests=json.loads(row[10]) if row[10] else [],
                    clan_achievements=json.loads(row[11]) if row[11] else [],
                    clan_wars_won=row[12], clan_wars_lost=row[13],
                    recruitment_open=row[14], required_level=row[15],
                    clan_motto=row[16], created_at=row[17], last_active=row[18]
                )
                
                self.clans[clan.clan_id] = clan
            
            self.logger.info(f"Loaded {len(self.clans)} clans")
            
        except Exception as e:
            self.logger.error(f"Error loading clans: {e}")
    
    async def _create_default_quests(self):
        """Create default learning quests"""
        try:
            # Tutorial quests
            tutorial_quests = [
                {
                    "title": "First Steps in Cybersecurity",
                    "description": "Learn the fundamentals of cybersecurity and ethical hacking",
                    "quest_type": QuestType.TUTORIAL,
                    "difficulty": QuestDifficulty.NOVICE,
                    "category": SkillCategory.RECONNAISSANCE,
                    "experience_reward": 100,
                    "ethical_impact": 20,
                    "legal_warnings": [
                        "Always ensure you have proper authorization before testing systems",
                        "This tutorial uses safe, isolated environments"
                    ],
                    "learning_objectives": [
                        "Understand the CIA triad",
                        "Learn about common attack vectors",
                        "Understand the importance of ethical hacking"
                    ],
                    "tasks": [
                        {"type": "reading", "content": "Read about cybersecurity fundamentals"},
                        {"type": "quiz", "questions": 5},
                        {"type": "practical", "description": "Set up a virtual lab environment"}
                    ]
                },
                
                {
                    "title": "Passive Reconnaissance Basics",
                    "description": "Learn to gather information without directly interacting with targets",
                    "quest_type": QuestType.TUTORIAL,
                    "difficulty": QuestDifficulty.NOVICE,
                    "category": SkillCategory.RECONNAISSANCE,
                    "experience_reward": 150,
                    "ethical_impact": 10,
                    "legal_warnings": [
                        "Passive reconnaissance should only be performed on authorized targets",
                        "Be aware of terms of service for search engines and databases"
                    ],
                    "learning_objectives": [
                        "Understand OSINT techniques",
                        "Learn to use search engines effectively",
                        "Practice information gathering"
                    ],
                    "tasks": [
                        {"type": "practical", "description": "Perform WHOIS lookup on a domain"},
                        {"type": "practical", "description": "Use Google dorking techniques"},
                        {"type": "practical", "description": "Analyze DNS records"}
                    ]
                }
            ]
            
            for quest_data in tutorial_quests:
                if not any(q.title == quest_data["title"] for q in self.quests.values()):
                    quest_id = str(uuid.uuid4())
                    quest = Quest(
                        quest_id=quest_id,
                        title=quest_data["title"],
                        description=quest_data["description"],
                        quest_type=quest_data["quest_type"],
                        difficulty=quest_data["difficulty"],
                        category=quest_data["category"],
                        prerequisites=[],
                        required_level=1,
                        required_skills={},
                        experience_reward=quest_data["experience_reward"],
                        skill_experience={quest_data["category"].value: 50},
                        tools_unlocked=[],
                        achievements_unlocked=[],
                        ethical_impact=quest_data["ethical_impact"],
                        legal_warnings=quest_data["legal_warnings"],
                        ethical_choices=[],
                        learning_objectives=quest_data["learning_objectives"],
                        tasks=quest_data["tasks"],
                        resources=[],
                        hints=[],
                        team_quest=False,
                        max_team_size=1,
                        clan_exclusive=False,
                        estimated_duration=60,
                        created_by="system",
                        created_at=time.time(),
                        updated_at=time.time(),
                        completion_rate=0.0,
                        average_rating=0.0
                    )
                    
                    await self._store_quest(quest)
                    self.quests[quest_id] = quest
            
        except Exception as e:
            self.logger.error(f"Error creating default quests: {e}")
    
    async def _create_default_achievements(self):
        """Create default achievements"""
        try:
            default_achievements = [
                {
                    "achievement_id": "first_steps",
                    "name": "First Steps",
                    "description": "Created your first character",
                    "icon": "🎯",
                    "category": "progression",
                    "rarity": "common",
                    "points": 10,
                    "requirements": {"action": "character_created"}
                },
                {
                    "achievement_id": "quest_master",
                    "name": "Quest Master",
                    "description": "Completed 10 quests",
                    "icon": "🏆",
                    "category": "progression",
                    "rarity": "uncommon",
                    "points": 50,
                    "requirements": {"quests_completed": 10}
                },
                {
                    "achievement_id": "ethical_hacker",
                    "name": "Ethical Hacker",
                    "description": "Maintained white hat alignment for 30 days",
                    "icon": "⚖️",
                    "category": "ethics",
                    "rarity": "rare",
                    "points": 100,
                    "requirements": {"ethical_alignment": "white_hat", "days": 30}
                }
            ]
            
            for ach_data in default_achievements:
                if ach_data["achievement_id"] not in self.achievements:
                    achievement = Achievement(
                        achievement_id=ach_data["achievement_id"],
                        name=ach_data["name"],
                        description=ach_data["description"],
                        icon=ach_data["icon"],
                        category=ach_data["category"],
                        rarity=ach_data["rarity"],
                        points=ach_data["points"],
                        requirements=ach_data["requirements"],
                        unlocked_by=[],
                        created_at=time.time()
                    )
                    
                    await self._store_achievement(achievement)
                    self.achievements[achievement.achievement_id] = achievement
            
        except Exception as e:
            self.logger.error(f"Error creating default achievements: {e}")
    
    async def _store_quest(self, quest: Quest):
        """Store quest in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO quests 
                (quest_id, title, description, quest_type, difficulty, category, prerequisites,
                 required_level, required_skills, experience_reward, skill_experience, tools_unlocked,
                 achievements_unlocked, ethical_impact, legal_warnings, ethical_choices,
                 learning_objectives, tasks, resources, hints, team_quest, max_team_size,
                 clan_exclusive, estimated_duration, created_by, created_at, updated_at,
                 completion_rate, average_rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                quest.quest_id, quest.title, quest.description, quest.quest_type.value,
                quest.difficulty.value, quest.category.value, json.dumps(quest.prerequisites),
                quest.required_level, json.dumps(quest.required_skills), quest.experience_reward,
                json.dumps(quest.skill_experience), json.dumps(quest.tools_unlocked),
                json.dumps(quest.achievements_unlocked), quest.ethical_impact,
                json.dumps(quest.legal_warnings), json.dumps(quest.ethical_choices),
                json.dumps(quest.learning_objectives), json.dumps(quest.tasks),
                json.dumps(quest.resources), json.dumps(quest.hints), quest.team_quest,
                quest.max_team_size, quest.clan_exclusive, quest.estimated_duration,
                quest.created_by, quest.created_at, quest.updated_at, quest.completion_rate,
                quest.average_rating
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing quest: {e}")
    
    async def _store_achievement(self, achievement: Achievement):
        """Store achievement in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO achievements 
                (achievement_id, name, description, icon, category, rarity, points, requirements, unlocked_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                achievement.achievement_id, achievement.name, achievement.description,
                achievement.icon, achievement.category, achievement.rarity, achievement.points,
                json.dumps(achievement.requirements), json.dumps(achievement.unlocked_by),
                achievement.created_at
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing achievement: {e}")
    
    async def _award_achievement(self, character_id: str, achievement_id: str):
        """Award achievement to character"""
        try:
            if character_id not in self.characters:
                return False
            
            character = self.characters[character_id]
            if achievement_id in character.achievements:
                return False  # Already has achievement
            
            if achievement_id not in self.achievements:
                return False  # Achievement doesn't exist
            
            # Award achievement
            character.achievements.append(achievement_id)
            achievement = self.achievements[achievement_id]
            achievement.unlocked_by.append(character_id)
            
            # Update database
            await self._store_character(character)
            await self._store_achievement(achievement)
            
            # Log achievement
            await self.audit_logger.log_system_event(
                event_type="achievement_awarded",
                details={
                    "character_id": character_id,
                    "achievement_id": achievement_id,
                    "achievement_name": achievement.name,
                    "points": achievement.points
                }
            )
            
            self.logger.info(f"Awarded achievement '{achievement.name}' to {character.username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error awarding achievement: {e}")
            return False
    
    async def complete_quest(self, character_id: str, quest_id: str, 
                           ethical_choice: Optional[str] = None, rating: Optional[int] = None) -> bool:
        """Complete a quest for a character"""
        try:
            if character_id not in self.characters or quest_id not in self.quests:
                return False
            
            character = self.characters[character_id]
            quest = self.quests[quest_id]
            
            # Check if already completed
            if quest_id in character.completed_quests:
                return False
            
            # Check prerequisites
            if not self._check_quest_prerequisites(character, quest):
                return False
            
            # Award experience and skill experience
            character.experience += quest.experience_reward
            character.total_experience += quest.experience_reward
            
            for skill_name, skill_exp in quest.skill_experience.items():
                if skill_name in character.skills:
                    character.skills[skill_name].experience += skill_exp
                    # Level up skill if needed
                    await self._check_skill_levelup(character, skill_name)
            
            # Update ethical alignment based on quest and choice
            if ethical_choice:
                ethical_impact = quest.ethical_impact
                if ethical_choice == "white_hat":
                    character.ethical_score += abs(ethical_impact)
                elif ethical_choice == "black_hat":
                    character.ethical_score -= abs(ethical_impact)
                # Grey hat choices don't change score much
                
                # Update alignment based on score
                if character.ethical_score > 30:
                    character.alignment = EthicalAlignment.WHITE_HAT
                elif character.ethical_score < -30:
                    character.alignment = EthicalAlignment.BLACK_HAT
                else:
                    character.alignment = EthicalAlignment.GREY_HAT
            
            # Mark quest as completed
            character.completed_quests.append(quest_id)
            character.quests_completed += 1
            
            # Remove from active quests if present
            if quest_id in character.active_quests:
                character.active_quests.remove(quest_id)
            
            # Check for level up
            await self._check_character_levelup(character)
            
            # Check for achievements
            await self._check_quest_achievements(character)
            
            # Update quest statistics
            quest.completion_rate = len([c for c in self.characters.values() 
                                       if quest_id in c.completed_quests]) / max(1, len(self.characters))
            
            if rating:
                # Update quest rating (simplified)
                quest.average_rating = (quest.average_rating + rating) / 2
            
            # Store completion
            completion_id = str(uuid.uuid4())
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO quest_completions 
                (completion_id, character_id, quest_id, completed_at, experience_gained, ethical_choice_made, rating, feedback)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (completion_id, character_id, quest_id, time.time(), quest.experience_reward, ethical_choice, rating, ""))
            
            conn.commit()
            conn.close()
            
            # Update character and quest in database
            await self._store_character(character)
            await self._store_quest(quest)
            
            # Log quest completion
            await self.audit_logger.log_system_event(
                event_type="quest_completed",
                details={
                    "character_id": character_id,
                    "quest_id": quest_id,
                    "quest_title": quest.title,
                    "experience_gained": quest.experience_reward,
                    "ethical_choice": ethical_choice,
                    "new_level": character.level
                }
            )
            
            self.logger.info(f"Quest '{quest.title}' completed by {character.username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error completing quest: {e}")
            return False
    
    def _check_quest_prerequisites(self, character: Character, quest: Quest) -> bool:
        """Check if character meets quest prerequisites"""
        # Check level requirement
        if character.level < quest.required_level:
            return False
        
        # Check skill requirements
        for skill_name, required_level in quest.required_skills.items():
            if skill_name not in character.skills:
                return False
            if character.skills[skill_name].level < required_level:
                return False
        
        # Check prerequisite quests
        for prereq_quest in quest.prerequisites:
            if prereq_quest not in character.completed_quests:
                return False
        
        return True
    
    async def _check_skill_levelup(self, character: Character, skill_name: str):
        """Check and handle skill level up"""
        try:
            skill = character.skills[skill_name]
            
            # Simple level up formula
            exp_needed = skill.level * 100
            
            while skill.experience >= exp_needed and skill.level < skill.max_level:
                skill.level += 1
                skill.experience -= exp_needed
                exp_needed = skill.level * 100
                
                # Log skill level up
                self.logger.info(f"{character.username} leveled up {skill.name} to level {skill.level}")
                
                # Check for tool unlocks
                if skill.level % 10 == 0:  # Every 10 levels
                    for tool in skill.tools_unlocked:
                        if tool not in character.tools_mastered:
                            character.tools_mastered.append(tool)
        
        except Exception as e:
            self.logger.error(f"Error checking skill levelup: {e}")
    
    async def _check_character_levelup(self, character: Character):
        """Check and handle character level up"""
        try:
            required_exp = self.level_experience_table.get(character.level + 1, float('inf'))
            
            while character.experience >= required_exp and character.level < 100:
                character.level += 1
                character.experience = int(character.experience - required_exp)
                
                # Attribute bonuses on level up
                character.technical_prowess = min(100, character.technical_prowess + 1)
                character.analytical_thinking = min(100, character.analytical_thinking + 1)
                
                required_exp = self.level_experience_table.get(character.level + 1, float('inf'))
                
                self.logger.info(f"{character.username} leveled up to level {character.level}")
        
        except Exception as e:
            self.logger.error(f"Error checking character levelup: {e}")
    
    async def _check_quest_achievements(self, character: Character):
        """Check for quest-related achievements"""
        try:
            # Check quest completion milestones
            if character.quests_completed == 10:
                await self._award_achievement(character.character_id, "quest_master")
            
            # Check ethical alignment achievements
            if character.alignment == EthicalAlignment.WHITE_HAT and character.quests_completed >= 5:
                await self._award_achievement(character.character_id, "ethical_hacker")
        
        except Exception as e:
            self.logger.error(f"Error checking quest achievements: {e}")
    
    def get_leaderboard(self, leaderboard_type: str, period: str = "all_time", limit: int = 100) -> List[Dict[str, Any]]:
        """Get leaderboard data"""
        try:
            leaderboard = []
            
            for character in self.characters.values():
                score = 0
                
                if leaderboard_type == "experience":
                    score = character.total_experience
                elif leaderboard_type == "level":
                    score = character.level
                elif leaderboard_type == "quests":
                    score = character.quests_completed
                elif leaderboard_type == "ctf_wins":
                    score = character.ctf_wins
                elif leaderboard_type == "ethical_score":
                    score = character.ethical_score
                
                leaderboard.append({
                    "character_id": character.character_id,
                    "username": character.username,
                    "display_name": character.display_name,
                    "character_class": character.character_class.value,
                    "level": character.level,
                    "score": score,
                    "clan_id": character.clan_id,
                    "avatar_url": character.avatar_url
                })
            
            # Sort by score descending
            leaderboard.sort(key=lambda x: x["score"], reverse=True)
            
            # Add ranks
            for i, entry in enumerate(leaderboard[:limit]):
                entry["rank"] = i + 1
            
            return leaderboard[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting leaderboard: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on character system"""
        try:
            # Check database connectivity
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM characters')
            character_count = cursor.fetchone()[0]
            conn.close()
            
            return {
                "status": "healthy",
                "character_count": character_count,
                "quest_count": len(self.quests),
                "achievement_count": len(self.achievements),
                "clan_count": len(self.clans),
                "system_directory_exists": os.path.exists(self.system_directory)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def shutdown(self):
        """Shutdown character system"""
        self.logger.info("Shutting down character system...")
        
        # Clear caches
        self.characters.clear()
        self.quests.clear()
        self.achievements.clear()
        self.clans.clear()
        
        self.logger.info("Character system shutdown complete")


# Example usage and testing
async def main():
    """Example usage of Character System"""
    # Initialize components
    consciousness_bus = ConsciousnessBus()
    character_system = CharacterSystem(consciousness_bus)
    
    # Wait for initialization
    await asyncio.sleep(3)
    
    # Health check
    health = await character_system.health_check()
    print(f"Health check: {health}")
    
    if health["status"] == "healthy":
        # Create a test character
        character_id = await character_system.create_character(
            username="test_hacker",
            display_name="Test Hacker",
            character_class=CharacterClass.PENETRATION_TESTER
        )
        print(f"Created character: {character_id}")
        
        # Get leaderboard
        leaderboard = character_system.get_leaderboard("experience", limit=10)
        print(f"Experience leaderboard: {leaderboard}")
    
    # Shutdown
    await character_system.shutdown()


if __name__ == "__main__":
    asyncio.run(main())