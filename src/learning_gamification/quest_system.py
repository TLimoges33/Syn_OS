#!/usr/bin/env python3
"""
Quest System for Syn_OS Learning Platform
Manages learning quests, ethical choices, and progression tracking
"""

import asyncio
import logging
import time
import json
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3

from src.learning_gamification.character_system import (
    Quest, QuestType, QuestDifficulty, SkillCategory,
    Character, EthicalAlignment
)


class QuestStatus(Enum):
    """Quest status for tracking"""
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    LOCKED = "locked"


@dataclass
class QuestProgress:
    """Track progress on a quest"""
    character_id: str
    quest_id: str
    status: QuestStatus
    progress: Dict[str, Any]
    started_at: float
    completed_at: Optional[float] = None
    ethical_choices_made: Optional[List[Dict[str, Any]]] = None
    hints_used: Optional[List[str]] = None
    attempts: int = 0
    score: int = 0


class QuestSystem:
    """
    Quest management system for gamified cybersecurity learning
    """
    
    def __init__(self, character_system):
        """Initialize quest system"""
        self.character_system = character_system
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.database_file = character_system.database_file
        
        # In-memory tracking
        self.active_quests: Dict[str, Dict[str, QuestProgress]] = {}  # character_id -> quest_id -> progress
        
        # Initialize system
        asyncio.create_task(self._initialize_quest_system())
    
    async def _initialize_quest_system(self):
        """Initialize quest system"""
        try:
            self.logger.info("Initializing quest system...")
            
            # Create quest progress table
            await self._initialize_quest_tables()
            
            # Load active quest progress
            await self._load_quest_progress()
            
            self.logger.info("Quest system initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing quest system: {e}")
    
    async def _initialize_quest_tables(self):
        """Initialize quest-related database tables"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            # Quest progress table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quest_progress (
                    progress_id TEXT PRIMARY KEY,
                    character_id TEXT NOT NULL,
                    quest_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    progress TEXT,
                    started_at REAL NOT NULL,
                    completed_at REAL,
                    ethical_choices_made TEXT,
                    hints_used TEXT,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    score INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (character_id) REFERENCES characters (character_id),
                    FOREIGN KEY (quest_id) REFERENCES quests (quest_id),
                    UNIQUE(character_id, quest_id)
                )
            ''')
            
            # Quest ratings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quest_ratings (
                    rating_id TEXT PRIMARY KEY,
                    character_id TEXT NOT NULL,
                    quest_id TEXT NOT NULL,
                    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                    feedback TEXT,
                    created_at REAL NOT NULL,
                    FOREIGN KEY (character_id) REFERENCES characters (character_id),
                    FOREIGN KEY (quest_id) REFERENCES quests (quest_id),
                    UNIQUE(character_id, quest_id)
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_quest_progress_character ON quest_progress (character_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_quest_progress_status ON quest_progress (status)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error initializing quest tables: {e}")
            raise
    
    async def _load_quest_progress(self):
        """Load active quest progress from database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM quest_progress WHERE status IN (?, ?)', 
                         (QuestStatus.ACTIVE.value, QuestStatus.AVAILABLE.value))
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                progress = QuestProgress(
                    character_id=row[1],
                    quest_id=row[2],
                    status=QuestStatus(row[3]),
                    progress=json.loads(row[4]) if row[4] else {},
                    started_at=row[5],
                    completed_at=row[6],
                    ethical_choices_made=json.loads(row[7]) if row[7] else [],
                    hints_used=json.loads(row[8]) if row[8] else [],
                    attempts=row[9],
                    score=row[10]
                )
                
                if progress.character_id not in self.active_quests:
                    self.active_quests[progress.character_id] = {}
                
                self.active_quests[progress.character_id][progress.quest_id] = progress
            
            self.logger.info(f"Loaded quest progress for {len(self.active_quests)} characters")
            
        except Exception as e:
            self.logger.error(f"Error loading quest progress: {e}")
    
    async def start_quest(self, character_id: str, quest_id: str) -> bool:
        """Start a quest for a character"""
        try:
            if character_id not in self.character_system.characters:
                return False
            
            if quest_id not in self.character_system.quests:
                return False
            
            character = self.character_system.characters[character_id]
            quest = self.character_system.quests[quest_id]
            
            # Check if already started or completed
            if character_id in self.active_quests and quest_id in self.active_quests[character_id]:
                return False
            
            if quest_id in character.completed_quests:
                return False
            
            # Check prerequisites
            if not self._check_quest_prerequisites(character, quest):
                return False
            
            # Create quest progress
            progress = QuestProgress(
                character_id=character_id,
                quest_id=quest_id,
                status=QuestStatus.ACTIVE,
                progress={},
                started_at=time.time(),
                ethical_choices_made=[],
                hints_used=[],
                attempts=1
            )
            
            # Store progress
            await self._store_quest_progress(progress)
            
            # Update in-memory tracking
            if character_id not in self.active_quests:
                self.active_quests[character_id] = {}
            self.active_quests[character_id][quest_id] = progress
            
            # Add to character's active quests
            character.active_quests.append(quest_id)
            await self.character_system._store_character(character)
            
            self.logger.info(f"Started quest '{quest.title}' for {character.username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting quest: {e}")
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
    
    async def update_quest_progress(self, character_id: str, quest_id: str, 
                                  task_id: str, progress_data: Dict[str, Any]) -> bool:
        """Update progress on a quest task"""
        try:
            if character_id not in self.active_quests:
                return False
            
            if quest_id not in self.active_quests[character_id]:
                return False
            
            progress = self.active_quests[character_id][quest_id]
            
            # Update progress data
            progress.progress[task_id] = progress_data
            
            # Check if quest is complete
            quest = self.character_system.quests[quest_id]
            if self._is_quest_complete(progress, quest):
                await self._complete_quest(character_id, quest_id)
            else:
                # Store updated progress
                await self._store_quest_progress(progress)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating quest progress: {e}")
            return False
    
    def _is_quest_complete(self, progress: QuestProgress, quest: Quest) -> bool:
        """Check if quest is complete based on progress"""
        # Simple completion check - all tasks have progress
        required_tasks = len(quest.tasks)
        completed_tasks = len([task for task in progress.progress.values() 
                             if task.get('completed', False)])
        
        return completed_tasks >= required_tasks
    
    async def _complete_quest(self, character_id: str, quest_id: str):
        """Complete a quest"""
        try:
            progress = self.active_quests[character_id][quest_id]
            progress.status = QuestStatus.COMPLETED
            progress.completed_at = time.time()
            
            # Calculate score based on performance
            progress.score = self._calculate_quest_score(progress)
            
            # Complete quest in character system
            await self.character_system.complete_quest(character_id, quest_id)
            
            # Store final progress
            await self._store_quest_progress(progress)
            
            # Remove from active quests
            del self.active_quests[character_id][quest_id]
            
        except Exception as e:
            self.logger.error(f"Error completing quest: {e}")
    
    def _calculate_quest_score(self, progress: QuestProgress) -> int:
        """Calculate score for completed quest"""
        base_score = 100
        
        # Deduct points for hints used
        hint_penalty = len(progress.hints_used or []) * 5
        
        # Deduct points for multiple attempts
        attempt_penalty = (progress.attempts - 1) * 10
        
        # Time bonus (completed quickly)
        time_taken = (progress.completed_at or time.time()) - progress.started_at
        if time_taken < 3600:  # Less than 1 hour
            time_bonus = 20
        elif time_taken < 7200:  # Less than 2 hours
            time_bonus = 10
        else:
            time_bonus = 0
        
        final_score = max(0, base_score - hint_penalty - attempt_penalty + time_bonus)
        return final_score
    
    async def make_ethical_choice(self, character_id: str, quest_id: str, 
                                choice_id: str, choice: str) -> bool:
        """Record an ethical choice made during a quest"""
        try:
            if character_id not in self.active_quests:
                return False
            
            if quest_id not in self.active_quests[character_id]:
                return False
            
            progress = self.active_quests[character_id][quest_id]
            
            # Record the choice
            ethical_choice = {
                "choice_id": choice_id,
                "choice": choice,
                "timestamp": time.time()
            }
            
            if progress.ethical_choices_made is None:
                progress.ethical_choices_made = []
            progress.ethical_choices_made.append(ethical_choice)
            
            # Update character's ethical score
            character = self.character_system.characters[character_id]
            if choice == "white_hat":
                character.ethical_score += 5
            elif choice == "black_hat":
                character.ethical_score -= 10
            elif choice == "grey_hat":
                character.ethical_score -= 2
            
            # Update alignment
            if character.ethical_score > 30:
                character.alignment = EthicalAlignment.WHITE_HAT
            elif character.ethical_score < -30:
                character.alignment = EthicalAlignment.BLACK_HAT
            else:
                character.alignment = EthicalAlignment.GREY_HAT
            
            # Store updates
            await self._store_quest_progress(progress)
            await self.character_system._store_character(character)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording ethical choice: {e}")
            return False
    
    async def use_hint(self, character_id: str, quest_id: str, hint_id: str) -> Optional[str]:
        """Use a hint for a quest"""
        try:
            if character_id not in self.active_quests:
                return None
            
            if quest_id not in self.active_quests[character_id]:
                return None
            
            quest = self.character_system.quests[quest_id]
            progress = self.active_quests[character_id][quest_id]
            
            # Check if hint exists
            if hint_id not in quest.hints:
                return None
            
            # Check if already used
            if progress.hints_used and hint_id in progress.hints_used:
                return quest.hints[hint_id]
            
            # Record hint usage
            if progress.hints_used is None:
                progress.hints_used = []
            progress.hints_used.append(hint_id)
            await self._store_quest_progress(progress)
            
            return quest.hints[hint_id]
            
        except Exception as e:
            self.logger.error(f"Error using hint: {e}")
            return None
    
    async def rate_quest(self, character_id: str, quest_id: str, 
                        rating: int, feedback: Optional[str] = None) -> bool:
        """Rate a completed quest"""
        try:
            if rating < 1 or rating > 5:
                return False
            
            character = self.character_system.characters.get(character_id)
            if not character or quest_id not in character.completed_quests:
                return False
            
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            rating_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT OR REPLACE INTO quest_ratings 
                (rating_id, character_id, quest_id, rating, feedback, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (rating_id, character_id, quest_id, rating, feedback, time.time()))
            
            conn.commit()
            conn.close()
            
            # Update quest average rating
            await self._update_quest_rating(quest_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error rating quest: {e}")
            return False
    
    async def _update_quest_rating(self, quest_id: str):
        """Update average rating for a quest"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT AVG(rating) FROM quest_ratings WHERE quest_id = ?', (quest_id,))
            avg_rating = cursor.fetchone()[0] or 0.0
            
            conn.close()
            
            # Update quest
            quest = self.character_system.quests[quest_id]
            quest.average_rating = avg_rating
            await self.character_system._store_quest(quest)
            
        except Exception as e:
            self.logger.error(f"Error updating quest rating: {e}")
    
    async def _store_quest_progress(self, progress: QuestProgress):
        """Store quest progress in database"""
        try:
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            
            progress_id = f"{progress.character_id}_{progress.quest_id}"
            cursor.execute('''
                INSERT OR REPLACE INTO quest_progress 
                (progress_id, character_id, quest_id, status, progress, started_at, completed_at,
                 ethical_choices_made, hints_used, attempts, score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                progress_id, progress.character_id, progress.quest_id, progress.status.value,
                json.dumps(progress.progress), progress.started_at, progress.completed_at,
                json.dumps(progress.ethical_choices_made), json.dumps(progress.hints_used),
                progress.attempts, progress.score
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing quest progress: {e}")
    
    def get_available_quests(self, character_id: str) -> List[Dict[str, Any]]:
        """Get available quests for a character"""
        try:
            if character_id not in self.character_system.characters:
                return []
            
            character = self.character_system.characters[character_id]
            available_quests = []
            
            for quest in self.character_system.quests.values():
                # Skip if already completed
                if quest.quest_id in character.completed_quests:
                    continue
                
                # Skip if already active
                if quest.quest_id in character.active_quests:
                    continue
                
                # Check prerequisites
                if self._check_quest_prerequisites(character, quest):
                    available_quests.append({
                        "quest_id": quest.quest_id,
                        "title": quest.title,
                        "description": quest.description,
                        "difficulty": quest.difficulty.value,
                        "category": quest.category.value,
                        "experience_reward": quest.experience_reward,
                        "estimated_duration": quest.estimated_duration,
                        "legal_warnings": quest.legal_warnings,
                        "ethical_impact": quest.ethical_impact
                    })
            
            return available_quests
            
        except Exception as e:
            self.logger.error(f"Error getting available quests: {e}")
            return []
    
    def get_quest_progress(self, character_id: str, quest_id: str) -> Optional[Dict[str, Any]]:
        """Get progress for a specific quest"""
        try:
            if character_id not in self.active_quests:
                return None
            
            if quest_id not in self.active_quests[character_id]:
                return None
            
            progress = self.active_quests[character_id][quest_id]
            quest = self.character_system.quests[quest_id]
            
            return {
                "quest_id": quest_id,
                "title": quest.title,
                "status": progress.status.value,
                "progress": progress.progress,
                "started_at": progress.started_at,
                "attempts": progress.attempts,
                "hints_used": len(progress.hints_used or []),
                "ethical_choices": progress.ethical_choices_made,
                "tasks": quest.tasks,
                "completion_percentage": len([t for t in progress.progress.values() 
                                            if t.get('completed', False)]) / len(quest.tasks) * 100
            }
            
        except Exception as e:
            self.logger.error(f"Error getting quest progress: {e}")
            return None
    
    async def abandon_quest(self, character_id: str, quest_id: str) -> bool:
        """Abandon an active quest"""
        try:
            if character_id not in self.active_quests:
                return False
            
            if quest_id not in self.active_quests[character_id]:
                return False
            
            # Remove from active tracking
            del self.active_quests[character_id][quest_id]
            
            # Remove from character's active quests
            character = self.character_system.characters[character_id]
            if quest_id in character.active_quests:
                character.active_quests.remove(quest_id)
                await self.character_system._store_character(character)
            
            # Update database
            conn = sqlite3.connect(self.database_file)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM quest_progress WHERE character_id = ? AND quest_id = ?',
                         (character_id, quest_id))
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error abandoning quest: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on quest system"""
        try:
            active_quest_count = sum(len(quests) for quests in self.active_quests.values())
            
            return {
                "status": "healthy",
                "active_quests": active_quest_count,
                "total_characters_with_quests": len(self.active_quests)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }