#!/usr/bin/env python3
"""
Leaderboard and Clan System for Syn_OS Learning Platform
Competitive learning with team-based operations
"""

import asyncio
import logging
import time
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from datetime import datetime, timedelta

from src.learning_gamification.character_system import Character, Clan, CharacterClass, EthicalAlignment


class LeaderboardType(Enum):
    """Types of leaderboards"""
    EXPERIENCE = "experience"
    LEVEL = "level"
    QUESTS_COMPLETED = "quests_completed"
    CTF_WINS = "ctf_wins"
    ETHICAL_SCORE = "ethical_score"
    VULNERABILITIES_FOUND = "vulnerabilities_found"
    INCIDENTS_RESOLVED = "incidents_resolved"
    CLAN_EXPERIENCE = "clan_experience"
    CLAN_LEVEL = "clan_level"


class LeaderboardPeriod(Enum):
    """Time periods for leaderboards"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ALL_TIME = "all_time"


@dataclass
class LeaderboardEntry:
    """Individual leaderboard entry"""
    character_id: str
    username: str
    display_name: str
    character_class: str
    level: int
    score: int
    rank: int
    clan_id: Optional[str] = None
    clan_tag: Optional[str] = None
    avatar_url: Optional[str] = None
    change_from_previous: int = 0  # Position change from last period


@dataclass
class ClanLeaderboardEntry:
    """Clan leaderboard entry"""
    clan_id: str
    name: str
    tag: str
    level: int
    total_experience: int
    member_count: int
    average_level: float
    rank: int
    leader_username: str
    change_from_previous: int = 0


class LeaderboardSystem:
    """
    Competitive leaderboard and clan management system
    """
    
    def __init__(self, character_system):
        """Initialize leaderboard system"""
        self.character_system = character_system
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.database_file = character_system.database_file
        
        # Caching
        self.leaderboard_cache: Dict[str, Dict[str, List[LeaderboardEntry]]] = {}
        self.clan_leaderboard_cache: Dict[str, List[ClanLeaderboardEntry]] = {}
        self.cache_expiry = 300  # 5 minutes
        self.last_cache_update = 0
        
        # Initialize system
        asyncio.create_task(self._initialize_leaderboard_system())
    
    async def _initialize_leaderboard_system(self):
        """Initialize leaderboard system"""
        try:
            self.logger.info("Initializing leaderboard system...")
            
            # Create leaderboard tables
            await self._initialize_leaderboard_tables()
            
            # Start periodic updates
            asyncio.create_task(self._periodic_leaderboard_update())
            
            self.logger.info("Leaderboard system initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing leaderboard system: {e}")
    
    async def _initialize_leaderboard_tables(self):
        """Initialize leaderboard database tables"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Historical leaderboard snapshots
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leaderboard_snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    leaderboard_type TEXT NOT NULL,
                    period TEXT NOT NULL,
                    character_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    rank INTEGER NOT NULL,
                    snapshot_date TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    FOREIGN KEY (character_id) REFERENCES characters (character_id)
                )
            ''')
            
            # Clan wars and competitions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clan_wars (
                    war_id TEXT PRIMARY KEY,
                    clan1_id TEXT NOT NULL,
                    clan2_id TEXT NOT NULL,
                    war_type TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    clan1_score INTEGER DEFAULT 0,
                    clan2_score INTEGER DEFAULT 0,
                    winner_clan_id TEXT,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at REAL NOT NULL,
                    FOREIGN KEY (clan1_id) REFERENCES clans (clan_id),
                    FOREIGN KEY (clan2_id) REFERENCES clans (clan_id)
                )
            ''')
            
            # Weekly/monthly competitions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS competitions (
                    competition_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    competition_type TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL NOT NULL,
                    prizes TEXT,
                    participants TEXT,
                    winners TEXT,
                    status TEXT NOT NULL DEFAULT 'upcoming',
                    created_at REAL NOT NULL
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_leaderboard_snapshots_type_period ON leaderboard_snapshots (leaderboard_type, period)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_leaderboard_snapshots_date ON leaderboard_snapshots (snapshot_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_clan_wars_status ON clan_wars (status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_competitions_status ON competitions (status)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing leaderboard tables: {e}")
            raise
    
    async def _periodic_leaderboard_update(self):
        """Periodically update leaderboards"""
        while True:
            try:
                await asyncio.sleep(300)  # Update every 5 minutes
                await self._update_all_leaderboards()
                
            except Exception as e:
                self.logger.error(f"Error in periodic leaderboard update: {e}")
    
    async def _update_all_leaderboards(self):
        """Update all leaderboard caches"""
        try:
            current_time = time.time()
            
            # Update character leaderboards
            for lb_type in LeaderboardType:
                if lb_type.value.startswith('clan_'):
                    continue  # Skip clan leaderboards here
                
                for period in LeaderboardPeriod:
                    leaderboard = await self._generate_leaderboard(lb_type, period)
                    
                    if lb_type.value not in self.leaderboard_cache:
                        self.leaderboard_cache[lb_type.value] = {}
                    
                    self.leaderboard_cache[lb_type.value][period.value] = leaderboard
            
            # Update clan leaderboards
            for period in LeaderboardPeriod:
                clan_leaderboard = await self._generate_clan_leaderboard(period)
                self.clan_leaderboard_cache[period.value] = clan_leaderboard
            
            self.last_cache_update = current_time
            self.logger.info("Updated all leaderboard caches")
            
        except Exception as e:
            self.logger.error(f"Error updating leaderboards: {e}")
    
    async def _generate_leaderboard(self, leaderboard_type: LeaderboardType, 
                                  period: LeaderboardPeriod, limit: int = 100) -> List[LeaderboardEntry]:
        """Generate leaderboard for specific type and period"""
        try:
            entries = []
            
            # Get time range for period
            start_time = self._get_period_start_time(period)
            
            for character in self.character_system.characters.values():
                # Skip if character created after period start
                if period != LeaderboardPeriod.ALL_TIME and character.created_at < start_time:
                    continue
                
                # Calculate score based on leaderboard type
                score = self._get_character_score(character, leaderboard_type, period, start_time)
                
                # Get clan info
                clan_tag = None
                if character.clan_id and character.clan_id in self.character_system.clans:
                    clan_tag = self.character_system.clans[character.clan_id].tag
                
                entry = LeaderboardEntry(
                    character_id=character.character_id,
                    username=character.username,
                    display_name=character.display_name,
                    character_class=character.character_class.value,
                    level=character.level,
                    score=score,
                    rank=0,  # Will be set after sorting
                    clan_id=character.clan_id,
                    clan_tag=clan_tag,
                    avatar_url=character.avatar_url
                )
                
                entries.append(entry)
            
            # Sort by score (descending)
            entries.sort(key=lambda x: x.score, reverse=True)
            
            # Assign ranks and limit results
            for i, entry in enumerate(entries[:limit]):
                entry.rank = i + 1
            
            return entries[:limit]
            
        except Exception as e:
            self.logger.error(f"Error generating leaderboard: {e}")
            return []
    
    def _get_character_score(self, character: Character, leaderboard_type: LeaderboardType, 
                           period: LeaderboardPeriod, start_time: float) -> int:
        """Get character score for specific leaderboard type"""
        if leaderboard_type == LeaderboardType.EXPERIENCE:
            return character.total_experience
        elif leaderboard_type == LeaderboardType.LEVEL:
            return character.level
        elif leaderboard_type == LeaderboardType.QUESTS_COMPLETED:
            return character.quests_completed
        elif leaderboard_type == LeaderboardType.CTF_WINS:
            return character.ctf_wins
        elif leaderboard_type == LeaderboardType.ETHICAL_SCORE:
            return character.ethical_score
        elif leaderboard_type == LeaderboardType.VULNERABILITIES_FOUND:
            return character.vulnerabilities_found
        elif leaderboard_type == LeaderboardType.INCIDENTS_RESOLVED:
            return character.incidents_resolved
        else:
            return 0
    
    async def _generate_clan_leaderboard(self, period: LeaderboardPeriod, 
                                       limit: int = 50) -> List[ClanLeaderboardEntry]:
        """Generate clan leaderboard"""
        try:
            entries = []
            
            for clan in self.character_system.clans.values():
                # Calculate clan statistics
                member_count = len(clan.members)
                if member_count == 0:
                    continue
                
                # Calculate average level of members
                total_level = 0
                active_members = 0
                
                for member_id in clan.members:
                    if member_id in self.character_system.characters:
                        character = self.character_system.characters[member_id]
                        total_level += character.level
                        active_members += 1
                
                if active_members == 0:
                    continue
                
                average_level = total_level / active_members
                
                # Get leader username
                leader_username = "Unknown"
                if clan.leader_id in self.character_system.characters:
                    leader_username = self.character_system.characters[clan.leader_id].username
                
                entry = ClanLeaderboardEntry(
                    clan_id=clan.clan_id,
                    name=clan.name,
                    tag=clan.tag,
                    level=clan.level,
                    total_experience=clan.total_experience,
                    member_count=active_members,
                    average_level=average_level,
                    rank=0,  # Will be set after sorting
                    leader_username=leader_username
                )
                
                entries.append(entry)
            
            # Sort by total experience (descending)
            entries.sort(key=lambda x: x.total_experience, reverse=True)
            
            # Assign ranks
            for i, entry in enumerate(entries[:limit]):
                entry.rank = i + 1
            
            return entries[:limit]
            
        except Exception as e:
            self.logger.error(f"Error generating clan leaderboard: {e}")
            return []
    
    def _get_period_start_time(self, period: LeaderboardPeriod) -> float:
        """Get start time for leaderboard period"""
        now = datetime.now()
        
        if period == LeaderboardPeriod.DAILY:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == LeaderboardPeriod.WEEKLY:
            days_since_monday = now.weekday()
            start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
        elif period == LeaderboardPeriod.MONTHLY:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # ALL_TIME
            return 0.0
        
        return start.timestamp()
    
    async def get_leaderboard(self, leaderboard_type: str, period: str = "all_time", 
                            limit: int = 100) -> List[Dict[str, Any]]:
        """Get leaderboard data"""
        try:
            # Check cache first
            current_time = time.time()
            if (current_time - self.last_cache_update > self.cache_expiry or 
                leaderboard_type not in self.leaderboard_cache or 
                period not in self.leaderboard_cache[leaderboard_type]):
                
                await self._update_all_leaderboards()
            
            # Get from cache
            if (leaderboard_type in self.leaderboard_cache and 
                period in self.leaderboard_cache[leaderboard_type]):
                
                entries = self.leaderboard_cache[leaderboard_type][period][:limit]
                return [asdict(entry) for entry in entries]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting leaderboard: {e}")
            return []
    
    async def get_clan_leaderboard(self, period: str = "all_time", 
                                 limit: int = 50) -> List[Dict[str, Any]]:
        """Get clan leaderboard data"""
        try:
            # Check cache first
            current_time = time.time()
            if (current_time - self.last_cache_update > self.cache_expiry or 
                period not in self.clan_leaderboard_cache):
                
                await self._update_all_leaderboards()
            
            # Get from cache
            if period in self.clan_leaderboard_cache:
                entries = self.clan_leaderboard_cache[period][:limit]
                return [asdict(entry) for entry in entries]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting clan leaderboard: {e}")
            return []
    
    async def get_character_rank(self, character_id: str, leaderboard_type: str, 
                               period: str = "all_time") -> Optional[int]:
        """Get character's rank in specific leaderboard"""
        try:
            leaderboard = await self.get_leaderboard(leaderboard_type, period, 1000)
            
            for entry in leaderboard:
                if entry['character_id'] == character_id:
                    return entry['rank']
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting character rank: {e}")
            return None
    
    async def create_clan(self, leader_id: str, name: str, tag: str, 
                         description: str = "", motto: str = "") -> Optional[str]:
        """Create a new clan"""
        try:
            if leader_id not in self.character_system.characters:
                return None
            
            leader = self.character_system.characters[leader_id]
            
            # Check if leader is already in a clan
            if leader.clan_id:
                return None
            
            # Check if clan name or tag already exists
            for clan in self.character_system.clans.values():
                if clan.name.lower() == name.lower() or clan.tag.upper() == tag.upper():
                    return None
            
            # Create clan
            clan_id = str(uuid.uuid4())
            current_time = time.time()
            
            clan = Clan(
                clan_id=clan_id,
                name=name,
                description=description,
                tag=tag.upper(),
                leader_id=leader_id,
                officers=[],
                members=[leader_id],
                total_experience=leader.total_experience,
                level=1,
                reputation=0,
                clan_quests=[],
                clan_achievements=[],
                clan_wars_won=0,
                clan_wars_lost=0,
                recruitment_open=True,
                required_level=1,
                clan_motto=motto,
                created_at=current_time,
                last_active=current_time
            )
            
            # Store clan
            await self._store_clan(clan)
            self.character_system.clans[clan_id] = clan
            
            # Update leader's clan membership
            leader.clan_id = clan_id
            await self.character_system._store_character(leader)
            
            self.logger.info(f"Created clan '{name}' [{tag}] led by {leader.username}")
            return clan_id
            
        except Exception as e:
            self.logger.error(f"Error creating clan: {e}")
            return None
    
    async def join_clan(self, character_id: str, clan_id: str) -> bool:
        """Join a clan"""
        try:
            if character_id not in self.character_system.characters:
                return False
            
            if clan_id not in self.character_system.clans:
                return False
            
            character = self.character_system.characters[character_id]
            clan = self.character_system.clans[clan_id]
            
            # Check if already in a clan
            if character.clan_id:
                return False
            
            # Check if clan is recruiting
            if not clan.recruitment_open:
                return False
            
            # Check level requirement
            if character.level < clan.required_level:
                return False
            
            # Add to clan
            clan.members.append(character_id)
            clan.total_experience += character.total_experience
            clan.last_active = time.time()
            
            # Update character
            character.clan_id = clan_id
            
            # Store updates
            await self._store_clan(clan)
            await self.character_system._store_character(character)
            
            self.logger.info(f"{character.username} joined clan '{clan.name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Error joining clan: {e}")
            return False
    
    async def leave_clan(self, character_id: str) -> bool:
        """Leave current clan"""
        try:
            if character_id not in self.character_system.characters:
                return False
            
            character = self.character_system.characters[character_id]
            
            if not character.clan_id:
                return False
            
            clan = self.character_system.clans[character.clan_id]
            
            # Remove from clan
            if character_id in clan.members:
                clan.members.remove(character_id)
            
            if character_id in clan.officers:
                clan.officers.remove(character_id)
            
            # Handle leadership transfer
            if clan.leader_id == character_id:
                if clan.officers:
                    clan.leader_id = clan.officers[0]
                elif clan.members:
                    clan.leader_id = clan.members[0]
                else:
                    # Clan is empty, delete it
                    del self.character_system.clans[clan.clan_id]
                    await self._delete_clan(clan.clan_id)
                    character.clan_id = None
                    await self.character_system._store_character(character)
                    return True
            
            # Update clan stats
            clan.total_experience -= character.total_experience
            clan.last_active = time.time()
            
            # Update character
            character.clan_id = None
            
            # Store updates
            await self._store_clan(clan)
            await self.character_system._store_character(character)
            
            self.logger.info(f"{character.username} left clan '{clan.name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Error leaving clan: {e}")
            return False
    
    async def _store_clan(self, clan: Clan):
        """Store clan in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO clans 
                (clan_id, name, description, tag, leader_id, officers, members, total_experience,
                 level, reputation, clan_quests, clan_achievements, clan_wars_won, clan_wars_lost,
                 recruitment_open, required_level, clan_motto, created_at, last_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                clan.clan_id, clan.name, clan.description, clan.tag, clan.leader_id,
                json.dumps(clan.officers), json.dumps(clan.members), clan.total_experience,
                clan.level, clan.reputation, json.dumps(clan.clan_quests),
                json.dumps(clan.clan_achievements), clan.clan_wars_won, clan.clan_wars_lost,
                clan.recruitment_open, clan.required_level, clan.clan_motto,
                clan.created_at, clan.last_active
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing clan: {e}")
    
    async def _delete_clan(self, clan_id: str):
        """Delete clan from database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM clans WHERE clan_id = ?', (clan_id,))
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error deleting clan: {e}")
    
    async def get_clan_info(self, clan_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed clan information"""
        try:
            if clan_id not in self.character_system.clans:
                return None
            
            clan = self.character_system.clans[clan_id]
            
            # Get member details
            members = []
            for member_id in clan.members:
                if member_id in self.character_system.characters:
                    character = self.character_system.characters[member_id]
                    members.append({
                        "character_id": character.character_id,
                        "username": character.username,
                        "display_name": character.display_name,
                        "level": character.level,
                        "character_class": character.character_class.value,
                        "is_leader": member_id == clan.leader_id,
                        "is_officer": member_id in clan.officers,
                        "last_active": character.last_active
                    })
            
            return {
                "clan_id": clan.clan_id,
                "name": clan.name,
                "description": clan.description,
                "tag": clan.tag,
                "level": clan.level,
                "total_experience": clan.total_experience,
                "reputation": clan.reputation,
                "member_count": len(members),
                "members": members,
                "clan_wars_won": clan.clan_wars_won,
                "clan_wars_lost": clan.clan_wars_lost,
                "recruitment_open": clan.recruitment_open,
                "required_level": clan.required_level,
                "clan_motto": clan.clan_motto,
                "created_at": clan.created_at,
                "last_active": clan.last_active
            }
            
        except Exception as e:
            self.logger.error(f"Error getting clan info: {e}")
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on leaderboard system"""
        try:
            return {
                "status": "healthy",
                "cached_leaderboards": len(self.leaderboard_cache),
                "cached_clan_leaderboards": len(self.clan_leaderboard_cache),
                "last_cache_update": self.last_cache_update,
                "total_clans": len(self.character_system.clans)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }