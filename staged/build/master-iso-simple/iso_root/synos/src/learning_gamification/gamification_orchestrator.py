#!/usr/bin/env python3
"""
Gamification Orchestrator for Syn_OS Learning Platform
Main coordinator for the gamified cybersecurity learning system
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import asdict

from src.consciousness_v2.consciousness_bus import ConsciousnessBus
from src.learning_gamification.character_system import CharacterSystem, CharacterClass
from src.learning_gamification.quest_system import QuestSystem
from src.learning_gamification.leaderboard_system import LeaderboardSystem


class GamificationOrchestrator:
    """
    Main orchestrator for the gamified learning platform
    Coordinates character progression, quests, leaderboards, and ethical education
    """
    
    def __init__(self, consciousness_bus: ConsciousnessBus):
        """Initialize gamification orchestrator"""
        self.consciousness_bus = consciousness_bus
        self.logger = logging.getLogger(__name__)
        
        # Initialize subsystems
        self.character_system = CharacterSystem(consciousness_bus)
        self.quest_system = QuestSystem(self.character_system)
        self.leaderboard_system = LeaderboardSystem(self.character_system)
        
        # Configuration
        self.ethical_warnings_enabled = True
        self.legal_compliance_mode = True
        
        # Initialize system
        asyncio.create_task(self._initialize_orchestrator())
    
    async def _initialize_orchestrator(self):
        """Initialize the gamification orchestrator"""
        try:
            self.logger.info("Initializing gamification orchestrator...")
            
            # Wait for subsystems to initialize
            await asyncio.sleep(5)
            
            # Verify all systems are healthy
            health_checks = await asyncio.gather(
                self.character_system.health_check(),
                self.quest_system.health_check(),
                self.leaderboard_system.health_check(),
                return_exceptions=True
            )
            
            for i, health in enumerate(health_checks):
                system_name = ["character_system", "quest_system", "leaderboard_system"][i]
                if isinstance(health, Exception):
                    self.logger.error(f"{system_name} health check failed: {health}")
                elif isinstance(health, dict) and health.get("status") != "healthy":
                    self.logger.warning(f"{system_name} health check: {health}")
                else:
                    self.logger.info(f"{system_name} is healthy")
            
            self.logger.info("Gamification orchestrator initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing gamification orchestrator: {e}")
    
    # Character Management API
    async def create_character(self, username: str, display_name: str, 
                             character_class: str) -> Dict[str, Any]:
        """Create a new character with ethical education"""
        try:
            # Validate character class
            try:
                char_class = CharacterClass(character_class)
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid character class: {character_class}",
                    "available_classes": [cls.value for cls in CharacterClass]
                }
            
            # Create character
            character_id = await self.character_system.create_character(
                username, display_name, char_class
            )
            
            if not character_id:
                return {
                    "success": False,
                    "error": "Failed to create character"
                }
            
            # Get character details
            character = self.character_system.characters[character_id]
            
            # Show ethical guidelines and legal warnings
            ethical_guidelines = self._get_ethical_guidelines()
            legal_warnings = self._get_legal_warnings()
            
            return {
                "success": True,
                "character_id": character_id,
                "character": {
                    "username": character.username,
                    "display_name": character.display_name,
                    "character_class": character.character_class.value,
                    "level": character.level,
                    "ethical_alignment": character.alignment.value,
                    "ethical_score": character.ethical_score
                },
                "ethical_guidelines": ethical_guidelines,
                "legal_warnings": legal_warnings,
                "next_steps": [
                    "Complete the 'First Steps in Cybersecurity' tutorial quest",
                    "Read and acknowledge the ethical hacking guidelines",
                    "Set up your virtual lab environment",
                    "Join or create a clan for team learning"
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error creating character: {e}")
            return {
                "success": False,
                "error": "Internal server error"
            }
    
    def _get_ethical_guidelines(self) -> List[str]:
        """Get ethical hacking guidelines"""
        return [
            "🎯 ALWAYS obtain proper authorization before testing any system",
            "⚖️ Respect privacy and confidentiality of data encountered",
            "🛡️ Use your skills to protect and defend, not to harm",
            "📚 Continuously educate yourself on legal and ethical boundaries",
            "🤝 Share knowledge responsibly and help others learn ethically",
            "🚨 Report vulnerabilities through proper disclosure channels",
            "💼 Maintain professional integrity in all security activities",
            "🌍 Consider the broader impact of your actions on society"
        ]
    
    def _get_legal_warnings(self) -> List[str]:
        """Get legal warnings and disclaimers"""
        return [
            "⚠️ CRITICAL: Unauthorized access to computer systems is illegal in most jurisdictions",
            "📋 Computer Fraud and Abuse Act (CFAA) in the US carries severe penalties",
            "🌐 International laws vary - know your local regulations",
            "✅ Only use these tools on systems you own or have explicit written permission to test",
            "📝 Always maintain proper documentation of authorization",
            "🏢 Corporate environments require additional compliance considerations",
            "🎓 Educational use should be limited to designated lab environments",
            "⚡ Violation of these guidelines may result in account suspension or legal action"
        ]
    
    # Quest Management API
    async def get_available_quests(self, character_id: str) -> Dict[str, Any]:
        """Get available quests for a character with ethical context"""
        try:
            if character_id not in self.character_system.characters:
                return {
                    "success": False,
                    "error": "Character not found"
                }
            
            character = self.character_system.characters[character_id]
            available_quests = self.quest_system.get_available_quests(character_id)
            
            # Add ethical context to each quest
            for quest in available_quests:
                quest["ethical_context"] = self._get_quest_ethical_context(quest)
                quest["legal_compliance"] = self._check_quest_legal_compliance(quest)
            
            return {
                "success": True,
                "character": {
                    "username": character.username,
                    "level": character.level,
                    "ethical_alignment": character.alignment.value,
                    "ethical_score": character.ethical_score
                },
                "available_quests": available_quests,
                "ethical_reminder": "Remember: All activities must be performed on authorized systems only!"
            }
            
        except Exception as e:
            self.logger.error(f"Error getting available quests: {e}")
            return {
                "success": False,
                "error": "Internal server error"
            }
    
    def _get_quest_ethical_context(self, quest: Dict[str, Any]) -> Dict[str, Any]:
        """Get ethical context for a quest"""
        ethical_impact = quest.get("ethical_impact", 0)
        
        if ethical_impact > 20:
            alignment_impact = "Strongly promotes ethical behavior"
            color = "green"
        elif ethical_impact > 0:
            alignment_impact = "Promotes ethical behavior"
            color = "lightgreen"
        elif ethical_impact == 0:
            alignment_impact = "Neutral ethical impact"
            color = "yellow"
        elif ethical_impact > -20:
            alignment_impact = "May involve morally ambiguous techniques"
            color = "orange"
        else:
            alignment_impact = "Involves techniques that require careful ethical consideration"
            color = "red"
        
        return {
            "ethical_impact": ethical_impact,
            "alignment_impact": alignment_impact,
            "color_code": color,
            "requires_authorization": ethical_impact < 0
        }
    
    def _check_quest_legal_compliance(self, quest: Dict[str, Any]) -> Dict[str, Any]:
        """Check legal compliance requirements for a quest"""
        legal_warnings = quest.get("legal_warnings", [])
        
        risk_level = "low"
        if any("CRITICAL" in warning or "DANGER" in warning for warning in legal_warnings):
            risk_level = "high"
        elif any("unauthorized" in warning.lower() for warning in legal_warnings):
            risk_level = "medium"
        
        return {
            "risk_level": risk_level,
            "warnings_count": len(legal_warnings),
            "requires_acknowledgment": risk_level in ["medium", "high"],
            "lab_environment_required": risk_level == "high"
        }
    
    async def start_quest(self, character_id: str, quest_id: str, 
                         acknowledge_warnings: bool = False) -> Dict[str, Any]:
        """Start a quest with ethical acknowledgment"""
        try:
            if character_id not in self.character_system.characters:
                return {
                    "success": False,
                    "error": "Character not found"
                }
            
            if quest_id not in self.character_system.quests:
                return {
                    "success": False,
                    "error": "Quest not found"
                }
            
            quest = self.character_system.quests[quest_id]
            character = self.character_system.characters[character_id]
            
            # Check if ethical acknowledgment is required
            if quest.legal_warnings and not acknowledge_warnings:
                return {
                    "success": False,
                    "error": "Legal acknowledgment required",
                    "legal_warnings": quest.legal_warnings,
                    "ethical_impact": quest.ethical_impact,
                    "requires_acknowledgment": True
                }
            
            # Start the quest
            success = await self.quest_system.start_quest(character_id, quest_id)
            
            if not success:
                return {
                    "success": False,
                    "error": "Failed to start quest - check prerequisites"
                }
            
            # Log ethical choice if applicable
            if quest.ethical_impact < 0:
                await self.quest_system.make_ethical_choice(
                    character_id, quest_id, "quest_start", "acknowledged_risks"
                )
            
            return {
                "success": True,
                "message": f"Quest '{quest.title}' started successfully",
                "quest_progress": self.quest_system.get_quest_progress(character_id, quest_id),
                "ethical_reminder": "Remember to follow ethical guidelines throughout this quest!"
            }
            
        except Exception as e:
            self.logger.error(f"Error starting quest: {e}")
            return {
                "success": False,
                "error": "Internal server error"
            }
    
    # Leaderboard API
    async def get_leaderboards(self, period: str = "all_time") -> Dict[str, Any]:
        """Get all leaderboards with ethical context"""
        try:
            # Get character leaderboards
            experience_lb = await self.leaderboard_system.get_leaderboard("experience", period)
            level_lb = await self.leaderboard_system.get_leaderboard("level", period)
            quests_lb = await self.leaderboard_system.get_leaderboard("quests_completed", period)
            ethical_lb = await self.leaderboard_system.get_leaderboard("ethical_score", period)
            
            # Get clan leaderboard
            clan_lb = await self.leaderboard_system.get_clan_leaderboard(period)
            
            # Add ethical context to leaderboards
            for entry in ethical_lb:
                entry["ethical_context"] = self._get_ethical_alignment_context(entry["score"])
            
            return {
                "success": True,
                "period": period,
                "leaderboards": {
                    "experience": experience_lb[:10],  # Top 10
                    "level": level_lb[:10],
                    "quests_completed": quests_lb[:10],
                    "ethical_score": ethical_lb[:10],
                    "clans": clan_lb[:10]
                },
                "ethical_spotlight": {
                    "message": "Ethical hackers lead by example!",
                    "top_ethical_hacker": ethical_lb[0] if ethical_lb else None
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting leaderboards: {e}")
            return {
                "success": False,
                "error": "Internal server error"
            }
    
    def _get_ethical_alignment_context(self, ethical_score: int) -> Dict[str, Any]:
        """Get context for ethical alignment score"""
        if ethical_score > 50:
            return {
                "alignment": "Exemplary White Hat",
                "description": "Consistently demonstrates ethical behavior",
                "color": "gold"
            }
        elif ethical_score > 30:
            return {
                "alignment": "White Hat",
                "description": "Strong ethical foundation",
                "color": "lightblue"
            }
        elif ethical_score > -10:
            return {
                "alignment": "Grey Hat",
                "description": "Mixed ethical choices",
                "color": "gray"
            }
        elif ethical_score > -30:
            return {
                "alignment": "Dark Grey Hat",
                "description": "Concerning ethical patterns",
                "color": "darkgray"
            }
        else:
            return {
                "alignment": "Black Hat",
                "description": "Requires ethical guidance",
                "color": "red"
            }
    
    # Clan Management API
    async def create_clan(self, leader_id: str, name: str, tag: str, 
                         description: str = "") -> Dict[str, Any]:
        """Create a new clan"""
        try:
            clan_id = await self.leaderboard_system.create_clan(
                leader_id, name, tag, description
            )
            
            if not clan_id:
                return {
                    "success": False,
                    "error": "Failed to create clan - check requirements"
                }
            
            clan_info = await self.leaderboard_system.get_clan_info(clan_id)
            
            return {
                "success": True,
                "message": f"Clan '{name}' [{tag}] created successfully",
                "clan": clan_info
            }
            
        except Exception as e:
            self.logger.error(f"Error creating clan: {e}")
            return {
                "success": False,
                "error": "Internal server error"
            }
    
    async def join_clan(self, character_id: str, clan_id: str) -> Dict[str, Any]:
        """Join a clan"""
        try:
            success = await self.leaderboard_system.join_clan(character_id, clan_id)
            
            if not success:
                return {
                    "success": False,
                    "error": "Failed to join clan - check requirements"
                }
            
            clan_info = await self.leaderboard_system.get_clan_info(clan_id)
            
            return {
                "success": True,
                "message": f"Successfully joined clan '{clan_info['name'] if clan_info else 'Unknown'}'",
                "clan": clan_info
            }
            
        except Exception as e:
            self.logger.error(f"Error joining clan: {e}")
            return {
                "success": False,
                "error": "Internal server error"
            }
    
    # Character Profile API
    async def get_character_profile(self, character_id: str) -> Dict[str, Any]:
        """Get detailed character profile with progression data"""
        try:
            if character_id not in self.character_system.characters:
                return {
                    "success": False,
                    "error": "Character not found"
                }
            
            character = self.character_system.characters[character_id]
            
            # Get ranks in different leaderboards
            ranks = {}
            for lb_type in ["experience", "level", "quests_completed", "ethical_score"]:
                rank = await self.leaderboard_system.get_character_rank(
                    character_id, lb_type, "all_time"
                )
                ranks[lb_type] = rank
            
            # Get clan info if member
            clan_info = None
            if character.clan_id:
                clan_info = await self.leaderboard_system.get_clan_info(character.clan_id)
            
            # Get active quests progress
            active_quests = []
            for quest_id in character.active_quests:
                progress = self.quest_system.get_quest_progress(character_id, quest_id)
                if progress:
                    active_quests.append(progress)
            
            return {
                "success": True,
                "character": {
                    "character_id": character.character_id,
                    "username": character.username,
                    "display_name": character.display_name,
                    "character_class": character.character_class.value,
                    "level": character.level,
                    "experience": character.experience,
                    "total_experience": character.total_experience,
                    "ethical_alignment": character.alignment.value,
                    "ethical_score": character.ethical_score,
                    "quests_completed": character.quests_completed,
                    "ctf_wins": character.ctf_wins,
                    "achievements": len(character.achievements),
                    "tools_mastered": len(character.tools_mastered),
                    "created_at": character.created_at,
                    "last_active": character.last_active
                },
                "progression": {
                    "ranks": ranks,
                    "skills": {name: {"level": skill.level, "experience": skill.experience} 
                             for name, skill in character.skills.items()},
                    "active_quests": active_quests,
                    "recent_achievements": character.achievements[-5:] if character.achievements else []
                },
                "clan": clan_info,
                "ethical_context": self._get_ethical_alignment_context(character.ethical_score)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting character profile: {e}")
            return {
                "success": False,
                "error": "Internal server error"
            }
    
    # System Health and Status
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        try:
            # Get health checks from all subsystems
            health_checks = await asyncio.gather(
                self.character_system.health_check(),
                self.quest_system.health_check(),
                self.leaderboard_system.health_check(),
                return_exceptions=True
            )
            
            system_status = {
                "character_system": health_checks[0] if not isinstance(health_checks[0], Exception) else {"status": "error", "error": str(health_checks[0])},
                "quest_system": health_checks[1] if not isinstance(health_checks[1], Exception) else {"status": "error", "error": str(health_checks[1])},
                "leaderboard_system": health_checks[2] if not isinstance(health_checks[2], Exception) else {"status": "error", "error": str(health_checks[2])}
            }
            
            # Overall status
            all_healthy = all(
                isinstance(status, dict) and status.get("status") == "healthy"
                for status in system_status.values()
            )
            
            return {
                "success": True,
                "overall_status": "healthy" if all_healthy else "degraded",
                "subsystems": system_status,
                "ethical_compliance": {
                    "warnings_enabled": self.ethical_warnings_enabled,
                    "legal_compliance_mode": self.legal_compliance_mode
                },
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {
                "success": False,
                "error": "Internal server error"
            }
    
    async def shutdown(self):
        """Shutdown gamification orchestrator"""
        self.logger.info("Shutting down gamification orchestrator...")
        
        # Shutdown subsystems
        await asyncio.gather(
            self.character_system.shutdown(),
            return_exceptions=True
        )
        
        self.logger.info("Gamification orchestrator shutdown complete")


# Example usage and testing
async def main():
    """Example usage of Gamification Orchestrator"""
    # Initialize consciousness bus
    consciousness_bus = ConsciousnessBus()
    await consciousness_bus.initialize()
    
    # Initialize gamification orchestrator
    orchestrator = GamificationOrchestrator(consciousness_bus)
    
    # Wait for initialization
    await asyncio.sleep(8)
    
    # Test system status
    status = await orchestrator.get_system_status()
    print(f"System status: {status}")
    
    if status.get("success"):
        # Create a test character
        result = await orchestrator.create_character(
            username="ethical_hacker_01",
            display_name="Ethical Hacker",
            character_class="penetration_tester"
        )
        print(f"Character creation: {result}")
        
        if result.get("success"):
            character_id = result["character_id"]
            
            # Get available quests
            quests = await orchestrator.get_available_quests(character_id)
            print(f"Available quests: {len(quests.get('available_quests', []))}")
            
            # Get character profile
            profile = await orchestrator.get_character_profile(character_id)
            print(f"Character profile: {profile.get('character', {}).get('username')}")
            
            # Get leaderboards
            leaderboards = await orchestrator.get_leaderboards()
            print(f"Leaderboards loaded: {leaderboards.get('success')}")
    
    # Shutdown
    await orchestrator.shutdown()
    await consciousness_bus.shutdown()


if __name__ == "__main__":
    asyncio.run(main())