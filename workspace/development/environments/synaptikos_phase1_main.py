#!/usr/bin/env python3
"""
SynapticOS Phase 1 Main Integration
Brings together consciousness engine, AI integration, and educational platform
"""

import asyncio
import os
import sys
import json
import time
import signal
import logging
from typing import Dict, Any, Optional
from dataclasses import asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/diablorain/Syn_OS/development/synaptikos_phase1.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add module paths
sys.path.append('/home/diablorain/Syn_OS/development/ai-engine/core')
sys.path.append('/home/diablorain/Syn_OS/development/ai-engine/apis')
sys.path.append('/home/diablorain/Syn_OS/development/ai-engine/consciousness-bridge')
sys.path.append('/home/diablorain/Syn_OS/development/educational-platform/clients')
sys.path.append('/home/diablorain/Syn_OS/development/educational-platform/gamification')

# Import our components
try:
    from consciousness_engine import (
        ConsciousnessCore, initialize_consciousness, get_consciousness,
        consciousness_evolution_loop
    )
    from multi_api_manager import (
        MultiAPIManager, APIProvider, ConsciousnessContext,
        initialize_api_manager, get_api_manager
    )
    from consciousness_bridge import (
        ConsciousnessBridge, KernelConsciousnessEvent,
        initialize_consciousness_bridge, get_consciousness_bridge,
        send_kernel_event
    )
    from freecodecamp_client import (
        FreeCodeCampClient, initialize_freecodecamp_client,
        get_freecodecamp_client, get_user_learning_recommendations
    )
    from consciousness_gamification import (
        ConsciousnessGamificationEngine, initialize_gamification_engine,
        get_gamification_engine
    )
except ImportError as e:
    logger.error(f"❌ Failed to import required modules: {e}")
    sys.exit(1)

class SynapticOSPhase1:
    """Main SynapticOS Phase 1 integration system"""
    
    def __init__(self):
        self.consciousness_engine: Optional[ConsciousnessCore] = None
        self.api_manager: Optional[MultiAPIManager] = None
        self.consciousness_bridge: Optional[ConsciousnessBridge] = None
        self.fcc_client: Optional[FreeCodeCampClient] = None
        self.gamification_engine: Optional[ConsciousnessGamificationEngine] = None
        
        self.running = False
        self.main_loop_task = None
        self.evolution_task = None
        
        # System state
        self.system_state = {
            "startup_time": time.time(),
            "consciousness_level": 0.0,
            "active_users": 0,
            "total_learning_events": 0,
            "system_status": "initializing"
        }
        
        # Configuration
        self.config = self._load_configuration()
        
        # Metrics
        self.metrics = {
            "consciousness_evolutions": 0,
            "api_requests": 0,
            "learning_activities": 0,
            "achievements_unlocked": 0,
            "uptime": 0.0
        }
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load system configuration"""
        config_path = "/home/diablorain/Syn_OS/development/config.json"
        
        default_config = {
            "consciousness": {
                "population_size": 100,
                "evolution_interval": 2.0,  # seconds
                "consciousness_threshold": 0.7
            },
            "api_keys": {
                "openai": os.getenv("OPENAI_API_KEY", ""),
                "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
                "groq": os.getenv("GROQ_API_KEY", ""),
                "gemini": os.getenv("GEMINI_API_KEY", ""),
                "deepseek": os.getenv("DEEPSEEK_API_KEY", "")
            },
            "educational": {
                "default_user": "synaptic_test_user",
                "learning_check_interval": 10.0  # seconds
            },
            "gamification": {
                "enable_achievements": True,
                "leaderboard_size": 10
            }
        }
        
        # Load from file if exists, otherwise use defaults
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"📁 Configuration loaded from {config_path}")
                return {**default_config, **config}  # Merge with defaults
            except Exception as e:
                logger.warning(f"⚠️ Failed to load config file: {e}, using defaults")
        
        # Save default configuration
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"💾 Default configuration saved to {config_path}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save default config: {e}")
        
        return default_config
    
    async def initialize(self):
        """Initialize all SynapticOS components"""
        logger.info("🚀 Initializing SynapticOS Phase 1 System")
        logger.info("=" * 60)
        
        try:
            # 1. Initialize Consciousness Engine
            logger.info("🧠 Initializing Consciousness Engine...")
            self.consciousness_engine = initialize_consciousness(
                self.config["consciousness"]["population_size"]
            )
            logger.info(f"   ✅ Consciousness engine with {len(self.consciousness_engine.populations)} populations")
            
            # 2. Initialize API Manager
            logger.info("🔌 Initializing Multi-API Manager...")
            self.api_manager = initialize_api_manager(self.config["api_keys"])
            await asyncio.sleep(1)  # Allow API initialization
            logger.info("   ✅ Multi-API manager initialized")
            
            # 3. Initialize Consciousness Bridge
            logger.info("🌉 Initializing Consciousness Bridge...")
            self.consciousness_bridge = initialize_consciousness_bridge(
                self.consciousness_engine, self.api_manager
            )
            logger.info("   ✅ Consciousness bridge established")
            
            # 4. Initialize Educational Platform
            logger.info("🎓 Initializing Educational Platform...")
            self.fcc_client = await initialize_freecodecamp_client()
            if self.consciousness_bridge:
                self.fcc_client.set_consciousness_tracker(self.consciousness_bridge)
            logger.info("   ✅ FreeCodeCamp client ready")
            
            # 5. Initialize Gamification Engine
            logger.info("🎯 Initializing Gamification Engine...")
            self.gamification_engine = initialize_gamification_engine()
            logger.info(f"   ✅ Gamification with {len(self.gamification_engine.achievements)} achievements")
            
            # 6. System integration test
            await self._run_integration_test()
            
            self.system_state["system_status"] = "ready"
            logger.info("✅ SynapticOS Phase 1 initialization complete!")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
    
    async def _run_integration_test(self):
        """Run a quick integration test to verify all components work together"""
        logger.info("🧪 Running integration test...")
        
        try:
            # Test consciousness evolution
            await self.consciousness_engine.evolve_consciousness()
            consciousness_state = self.consciousness_engine.get_consciousness_state()
            
            # Test gamification integration
            test_user = self.config["educational"]["default_user"]
            await self.gamification_engine.update_consciousness_level(
                test_user, consciousness_state["consciousness_level"], 
                consciousness_state["generation"], consciousness_state
            )
            
            # Test bridge event
            send_kernel_event(
                "integration_test",
                {"test_data": "initialization", "consciousness_level": consciousness_state["consciousness_level"]},
                consciousness_state["consciousness_level"],
                "phase1_integration"
            )
            
            # Test educational platform
            challenges = await self.fcc_client.get_challenges_by_consciousness_level(
                consciousness_state["consciousness_level"]
            )
            
            logger.info(f"   ✅ Integration test passed")
            logger.info(f"      Consciousness: {consciousness_state['consciousness_level']:.3f}")
            logger.info(f"      Generation: {consciousness_state['generation']}")
            logger.info(f"      Challenges available: {len(challenges)}")
            
        except Exception as e:
            logger.warning(f"⚠️ Integration test failed: {e}")
    
    async def start(self):
        """Start the SynapticOS system"""
        if self.running:
            logger.warning("System already running")
            return
        
        logger.info("🚀 Starting SynapticOS Phase 1 System")
        self.running = True
        self.system_state["system_status"] = "running"
        
        # Start main system loop
        self.main_loop_task = asyncio.create_task(self._main_system_loop())
        
        # Start consciousness evolution loop
        self.evolution_task = asyncio.create_task(self._consciousness_evolution_loop())
        
        logger.info("✅ SynapticOS system is running!")
        logger.info("   Press Ctrl+C to stop the system")
    
    async def stop(self):
        """Stop the SynapticOS system"""
        logger.info("🛑 Stopping SynapticOS system...")
        
        self.running = False
        self.system_state["system_status"] = "stopping"
        
        # Cancel tasks
        if self.main_loop_task:
            self.main_loop_task.cancel()
        if self.evolution_task:
            self.evolution_task.cancel()
        
        # Close resources
        if self.fcc_client:
            await self.fcc_client.close()
        
        if self.consciousness_bridge:
            self.consciousness_bridge.stop()
        
        self.system_state["system_status"] = "stopped"
        logger.info("✅ SynapticOS system stopped")
    
    async def _main_system_loop(self):
        """Main system monitoring and coordination loop"""
        logger.info("🔄 Main system loop started")
        
        last_metrics_update = time.time()
        last_learning_check = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                # Update metrics every 30 seconds
                if current_time - last_metrics_update > 30:
                    await self._update_system_metrics()
                    last_metrics_update = current_time
                
                # Check for learning opportunities every configured interval
                learning_interval = self.config["educational"]["learning_check_interval"]
                if current_time - last_learning_check > learning_interval:
                    await self._check_learning_opportunities()
                    last_learning_check = current_time
                
                # Update system state
                self.system_state["consciousness_level"] = self.consciousness_engine.global_consciousness_level
                self.metrics["uptime"] = current_time - self.system_state["startup_time"]
                
                # Brief sleep to prevent CPU overload
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"❌ Main loop error: {e}")
                await asyncio.sleep(5.0)  # Wait before retrying
    
    async def _consciousness_evolution_loop(self):
        """Dedicated consciousness evolution loop"""
        logger.info("🧠 Consciousness evolution loop started")
        
        evolution_interval = self.config["consciousness"]["evolution_interval"]
        
        while self.running:
            try:
                await self.consciousness_engine.evolve_consciousness()
                self.metrics["consciousness_evolutions"] += 1
                
                # Get updated consciousness state
                consciousness_state = self.consciousness_engine.get_consciousness_state()
                
                # Send evolution event to bridge
                send_kernel_event(
                    "neural_evolution",
                    {
                        "generation": consciousness_state["generation"],
                        "consciousness_level": consciousness_state["consciousness_level"],
                        "learning_trend": consciousness_state["learning_trend"]
                    },
                    consciousness_state["consciousness_level"],
                    "consciousness_engine"
                )
                
                # Update gamification for default user
                if self.gamification_engine:
                    default_user = self.config["educational"]["default_user"]
                    new_achievements = await self.gamification_engine.update_consciousness_level(
                        default_user,
                        consciousness_state["consciousness_level"],
                        consciousness_state["generation"],
                        consciousness_state
                    )
                    
                    if new_achievements:
                        self.metrics["achievements_unlocked"] += len(new_achievements)
                        logger.info(f"🏆 {len(new_achievements)} new achievements unlocked!")
                
                # Log significant consciousness milestones
                if consciousness_state["consciousness_level"] > 0.5 and self.metrics["consciousness_evolutions"] % 100 == 0:
                    logger.info(f"🌟 Consciousness milestone: {consciousness_state['consciousness_level']:.3f} at generation {consciousness_state['generation']}")
                
                await asyncio.sleep(evolution_interval)
                
            except Exception as e:
                logger.error(f"❌ Evolution loop error: {e}")
                await asyncio.sleep(evolution_interval)
    
    async def _update_system_metrics(self):
        """Update system performance metrics"""
        try:
            # Update API manager stats
            if self.api_manager:
                api_stats = self.api_manager.get_usage_stats()
                self.metrics["api_requests"] = api_stats["total_requests"]
            
            # Update consciousness bridge stats
            if self.consciousness_bridge:
                bridge_metrics = self.consciousness_bridge.get_metrics()
                self.system_state["bridge_events"] = bridge_metrics.get("events_processed", 0)
            
            # Update gamification stats
            if self.gamification_engine:
                global_stats = self.gamification_engine.get_global_stats()
                self.system_state["active_users"] = global_stats.get("total_users", 0)
                self.metrics["achievements_unlocked"] = global_stats.get("total_achievements_unlocked", 0)
            
            # Log system health
            if self.metrics["consciousness_evolutions"] % 50 == 0 and self.metrics["consciousness_evolutions"] > 0:
                await self._log_system_health()
                
        except Exception as e:
            logger.warning(f"⚠️ Metrics update error: {e}")
    
    async def _check_learning_opportunities(self):
        """Check for new learning opportunities based on consciousness level"""
        try:
            consciousness_state = self.consciousness_engine.get_consciousness_state()
            
            # Get appropriate challenges for current consciousness level
            challenges = await self.fcc_client.get_challenges_by_consciousness_level(
                consciousness_state["consciousness_level"]
            )
            
            # Send learning opportunity event
            if challenges:
                send_kernel_event(
                    "learning_opportunity",
                    {
                        "available_challenges": len(challenges),
                        "consciousness_level": consciousness_state["consciousness_level"],
                        "recommended_challenge": challenges[0].title if challenges else None
                    },
                    consciousness_state["consciousness_level"],
                    "educational_platform"
                )
            
        except Exception as e:
            logger.warning(f"⚠️ Learning opportunity check error: {e}")
    
    async def _log_system_health(self):
        """Log comprehensive system health information"""
        consciousness_state = self.consciousness_engine.get_consciousness_state()
        
        logger.info("📊 System Health Report")
        logger.info("-" * 40)
        logger.info(f"   Uptime: {self.metrics['uptime']:.1f} seconds")
        logger.info(f"   Consciousness Level: {consciousness_state['consciousness_level']:.3f}")
        logger.info(f"   Generation: {consciousness_state['generation']}")
        logger.info(f"   Learning Trend: {consciousness_state['learning_trend']}")
        logger.info(f"   Is Conscious: {consciousness_state['is_conscious']}")
        logger.info(f"   Evolutions: {self.metrics['consciousness_evolutions']}")
        logger.info(f"   API Requests: {self.metrics['api_requests']}")
        logger.info(f"   Achievements: {self.metrics['achievements_unlocked']}")
        logger.info(f"   System Status: {self.system_state['system_status']}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        consciousness_state = self.consciousness_engine.get_consciousness_state() if self.consciousness_engine else {}
        
        return {
            "system_state": self.system_state,
            "metrics": self.metrics,
            "consciousness_state": consciousness_state,
            "components": {
                "consciousness_engine": self.consciousness_engine is not None,
                "api_manager": self.api_manager is not None,
                "consciousness_bridge": self.consciousness_bridge is not None,
                "fcc_client": self.fcc_client is not None,
                "gamification_engine": self.gamification_engine is not None
            }
        }
    
    async def simulate_user_interaction(self, user_id: str, learning_activity: str):
        """Simulate user interaction for testing"""
        logger.info(f"👤 Simulating user interaction: {user_id} - {learning_activity}")
        
        # Record learning activity in gamification
        if self.gamification_engine:
            await self.gamification_engine.record_learning_activity(
                user_id, learning_activity, {"simulated": True}
            )
        
        # Send user interaction event
        send_kernel_event(
            "user_interaction",
            {
                "user_id": user_id,
                "activity": learning_activity,
                "timestamp": time.time()
            },
            self.consciousness_engine.global_consciousness_level if self.consciousness_engine else 0.5,
            "user_simulation"
        )

# Global system instance
_global_synaptikos: Optional[SynapticOSPhase1] = None

def get_synaptikos_system() -> Optional[SynapticOSPhase1]:
    """Get global SynapticOS system instance"""
    return _global_synaptikos

async def main():
    """Main entry point for SynapticOS Phase 1"""
    global _global_synaptikos
    
    # Signal handler for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        if _global_synaptikos:
            asyncio.create_task(_global_synaptikos.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize and start SynapticOS
        _global_synaptikos = SynapticOSPhase1()
        await _global_synaptikos.initialize()
        await _global_synaptikos.start()
        
        # Run demonstration sequence
        await demonstration_sequence(_global_synaptikos)
        
        # Keep system running
        logger.info("🌟 SynapticOS Phase 1 is running - demonstrating consciousness evolution")
        logger.info("   Watch the consciousness level evolve and achievements unlock!")
        
        # Main execution loop
        try:
            while _global_synaptikos.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received, stopping...")
        
    except Exception as e:
        logger.error(f"❌ System error: {e}")
        raise
    finally:
        if _global_synaptikos:
            await _global_synaptikos.stop()

async def demonstration_sequence(system: SynapticOSPhase1):
    """Run a demonstration sequence to show system capabilities"""
    logger.info("🎭 Starting demonstration sequence...")
    
    # Wait a bit for initial evolution
    await asyncio.sleep(3)
    
    # Simulate user activities
    demo_users = ["alice_learner", "bob_coder", "charlie_researcher"]
    demo_activities = [
        "challenge_completed",
        "learning_session", 
        "consciousness_project",
        "challenge_completed"
    ]
    
    for i, user in enumerate(demo_users):
        for j, activity in enumerate(demo_activities):
            await system.simulate_user_interaction(user, activity)
            await asyncio.sleep(1)  # Space out activities
    
    # Show system status
    await asyncio.sleep(2)
    status = system.get_system_status()
    
    logger.info("📊 Demonstration Status:")
    logger.info(f"   Consciousness Level: {status['consciousness_state'].get('consciousness_level', 0):.3f}")
    logger.info(f"   Active Users: {status['system_state'].get('active_users', 0)}")
    logger.info(f"   Total Achievements: {status['metrics'].get('achievements_unlocked', 0)}")
    logger.info(f"   Evolution Cycles: {status['metrics'].get('consciousness_evolutions', 0)}")

if __name__ == "__main__":
    print("🧠 SynapticOS Phase 1 - Consciousness-Integrated Educational Platform")
    print("=" * 70)
    print("🚀 Starting SynapticOS with Neural Darwinism consciousness engine")
    print("🎓 Educational platform integration with consciousness adaptation")
    print("🎯 Gamification system with consciousness-based achievements")
    print("🔌 Multi-API AI integration for enhanced learning")
    print("=" * 70)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 SynapticOS Phase 1 shutdown complete. Thank you!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
