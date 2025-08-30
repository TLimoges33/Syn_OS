#!/usr/bin/env python3
"""
Syn_OS Main Startup Script
==========================

Consciousness-aware security operating system startup orchestrator.
Initializes and coordinates all Syn_OS components in the correct order.
"""

import asyncio
import logging
import signal
import sys
import yaml
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('syn_os.startup')

# Import Syn_OS components
try:
    from src.consciousness_v2.components.kernel_hooks_v2 import KernelConsciousnessHooksV2
    from src.ai_integration.claude_consciousness_interface import ClaudeConsciousnessInterface
    from src.ai_integration.ai_orchestration_engine import AIOrchestrationEngine
    from src.security_orchestration.security_tool_orchestrator import SecurityToolOrchestrator
    from src.consciousness_v2.core.consciousness_bus import ConsciousnessBus
    from src.consciousness_v2.core.state_manager import StateManager
except ImportError as e:
    logger.error(f"Failed to import Syn_OS components: {e}")
    logger.error("Please ensure all dependencies are installed and paths are correct")
    sys.exit(1)


class SynOSOrchestrator:
    """Main Syn_OS system orchestrator"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.components: Dict[str, Any] = {}
        self.running = False
        self.shutdown_event = asyncio.Event()
        
        # Core components
        self.consciousness_bus: Optional[ConsciousnessBus] = None
        self.state_manager: Optional[StateManager] = None
        self.kernel_hooks: Optional[KernelConsciousnessHooksV2] = None
        self.ai_orchestrator: Optional[AIOrchestrationEngine] = None
        self.security_orchestrator: Optional[SecurityToolOrchestrator] = None
        
        # Component initialization order
        self.initialization_order = [
            "consciousness_bus",
            "state_manager", 
            "kernel_hooks",
            "ai_orchestrator",
            "security_orchestrator"
        ]
    
    async def load_configuration(self) -> bool:
        """Load Syn_OS configuration"""
        try:
            logger.info(f"Loading configuration from {self.config_path}")
            
            if not os.path.exists(self.config_path):
                logger.error(f"Configuration file not found: {self.config_path}")
                return False
            
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            
            # Expand environment variables
            self._expand_environment_variables(self.config)
            
            logger.info("Configuration loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return False
    
    def _expand_environment_variables(self, obj: Any) -> Any:
        """Recursively expand environment variables in configuration"""
        if isinstance(obj, dict):
            return {k: self._expand_environment_variables(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._expand_environment_variables(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            env_var = obj[2:-1]
            return os.getenv(env_var, obj)
        else:
            return obj
    
    async def initialize_components(self) -> bool:
        """Initialize all Syn_OS components in correct order"""
        try:
            logger.info("Initializing Syn_OS components...")
            
            # Initialize consciousness bus first
            if not await self._initialize_consciousness_bus():
                return False
            
            # Initialize state manager
            if not await self._initialize_state_manager():
                return False
            
            # Initialize kernel hooks
            if not await self._initialize_kernel_hooks():
                return False
            
            # Initialize AI orchestrator
            if not await self._initialize_ai_orchestrator():
                return False
            
            # Initialize security orchestrator
            if not await self._initialize_security_orchestrator():
                return False
            
            logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            return False
    
    async def _initialize_consciousness_bus(self) -> bool:
        """Initialize consciousness bus"""
        try:
            logger.info("Initializing consciousness bus...")
            
            # This would be implemented based on the actual ConsciousnessBus class
            # For now, we'll create a placeholder
            self.consciousness_bus = None  # ConsciousnessBus(self.config.get("message_bus", {}))
            
            logger.info("Consciousness bus initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize consciousness bus: {e}")
            return False
    
    async def _initialize_state_manager(self) -> bool:
        """Initialize state manager"""
        try:
            logger.info("Initializing state manager...")
            
            # This would be implemented based on the actual StateManager class
            self.state_manager = None  # StateManager(self.config.get("database", {}))
            
            logger.info("State manager initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize state manager: {e}")
            return False
    
    async def _initialize_kernel_hooks(self) -> bool:
        """Initialize kernel consciousness hooks"""
        try:
            if not self.config.get("consciousness", {}).get("kernel_hooks", {}).get("enabled", False):
                logger.info("Kernel hooks disabled in configuration")
                return True
            
            logger.info("Initializing kernel consciousness hooks...")
            
            device_path = self.config["consciousness"]["kernel_hooks"].get("device_path", "/dev/consciousness")
            self.kernel_hooks = KernelConsciousnessHooksV2(device_path)
            
            success = await self.kernel_hooks.initialize(self.consciousness_bus, self.state_manager)
            if success:
                await self.kernel_hooks.start()
                self.components["kernel_hooks"] = self.kernel_hooks
                logger.info("Kernel consciousness hooks initialized")
            else:
                logger.warning("Kernel hooks initialization failed, continuing without kernel integration")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize kernel hooks: {e}")
            return False
    
    async def _initialize_ai_orchestrator(self) -> bool:
        """Initialize AI orchestration engine"""
        try:
            if not self.config.get("ai_integration", {}).get("orchestration", {}).get("enabled", False):
                logger.info("AI orchestration disabled in configuration")
                return True
            
            logger.info("Initializing AI orchestration engine...")
            
            ai_config = self.config.get("ai_integration", {})
            self.ai_orchestrator = AIOrchestrationEngine(ai_config)
            
            success = await self.ai_orchestrator.initialize(self.consciousness_bus, self.state_manager)
            if success:
                await self.ai_orchestrator.start()
                self.components["ai_orchestrator"] = self.ai_orchestrator
                logger.info("AI orchestration engine initialized")
            else:
                logger.error("AI orchestrator initialization failed")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize AI orchestrator: {e}")
            return False
    
    async def _initialize_security_orchestrator(self) -> bool:
        """Initialize security tool orchestrator"""
        try:
            if not self.config.get("security_orchestration", {}).get("enabled", False):
                logger.info("Security orchestration disabled in configuration")
                return True
            
            logger.info("Initializing security tool orchestrator...")
            
            security_config = self.config.get("security_orchestration", {})
            self.security_orchestrator = SecurityToolOrchestrator(security_config)
            
            success = await self.security_orchestrator.initialize(self.consciousness_bus, self.state_manager)
            if success:
                await self.security_orchestrator.start()
                self.components["security_orchestrator"] = self.security_orchestrator
                logger.info("Security tool orchestrator initialized")
            else:
                logger.error("Security orchestrator initialization failed")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize security orchestrator: {e}")
            return False
    
    async def start_system(self) -> bool:
        """Start the complete Syn_OS system"""
        try:
            logger.info("🧠 Starting Syn_OS - Consciousness-Aware Security Operating System")
            logger.info(f"Version: {self.config.get('system', {}).get('version', 'Unknown')}")
            logger.info(f"Codename: {self.config.get('system', {}).get('codename', 'Unknown')}")
            
            # Load configuration
            if not await self.load_configuration():
                return False
            
            # Initialize components
            if not await self.initialize_components():
                return False
            
            # Start monitoring and health checks
            await self._start_monitoring()
            
            # System is now running
            self.running = True
            logger.info("🚀 Syn_OS system started successfully!")
            
            # Print system status
            await self._print_system_status()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Syn_OS system: {e}")
            return False
    
    async def _start_monitoring(self):
        """Start system monitoring and health checks"""
        try:
            # Start background monitoring task
            asyncio.create_task(self._monitoring_loop())
            logger.info("System monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.running:
            try:
                # Check component health
                await self._check_component_health()
                
                # Sleep for monitoring interval
                monitoring_interval = self.config.get("performance", {}).get("monitoring", {}).get("interval", 30)
                await asyncio.sleep(monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _check_component_health(self):
        """Check health of all components"""
        try:
            unhealthy_components = []
            
            for name, component in self.components.items():
                if hasattr(component, 'get_health_status'):
                    try:
                        status = await component.get_health_status()
                        if hasattr(status, 'health_score') and status.health_score < 0.5:
                            unhealthy_components.append(name)
                    except Exception as e:
                        logger.warning(f"Failed to get health status for {name}: {e}")
                        unhealthy_components.append(name)
            
            if unhealthy_components:
                logger.warning(f"Unhealthy components detected: {unhealthy_components}")
            
        except Exception as e:
            logger.error(f"Error checking component health: {e}")
    
    async def _print_system_status(self):
        """Print current system status"""
        try:
            print("\n" + "="*60)
            print("🧠 SYN_OS SYSTEM STATUS")
            print("="*60)
            
            # System info
            system_info = self.config.get("system", {})
            print(f"System: {system_info.get('name', 'Syn_OS')} {system_info.get('version', '1.0.0')}")
            print(f"Base OS: {system_info.get('base_os', 'ParrotOS 6.4')}")
            print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Component status
            print(f"\nComponents: {len(self.components)} active")
            for name, component in self.components.items():
                status = "✅ Running"
                if hasattr(component, 'get_health_status'):
                    try:
                        health = await component.get_health_status()
                        if hasattr(health, 'health_score'):
                            if health.health_score > 0.8:
                                status = "✅ Healthy"
                            elif health.health_score > 0.5:
                                status = "⚠️  Degraded"
                            else:
                                status = "❌ Unhealthy"
                    except:
                        status = "❓ Unknown"
                
                print(f"  {name}: {status}")
            
            # Configuration highlights
            print(f"\nConfiguration:")
            print(f"  Consciousness: {'✅ Enabled' if self.config.get('consciousness', {}).get('enabled') else '❌ Disabled'}")
            print(f"  AI Integration: {'✅ Enabled' if self.config.get('ai_integration', {}).get('orchestration', {}).get('enabled') else '❌ Disabled'}")
            print(f"  Security Tools: {'✅ Enabled' if self.config.get('security_orchestration', {}).get('enabled') else '❌ Disabled'}")
            
            print("\n" + "="*60)
            print("🔒 Ready for consciousness-aware security operations!")
            print("="*60 + "\n")
            
        except Exception as e:
            logger.error(f"Error printing system status: {e}")
    
    async def shutdown_system(self):
        """Gracefully shutdown the Syn_OS system"""
        try:
            logger.info("🛑 Shutting down Syn_OS system...")
            
            self.running = False
            
            # Shutdown components in reverse order
            shutdown_order = list(reversed(self.initialization_order))
            
            for component_name in shutdown_order:
                if component_name in self.components:
                    component = self.components[component_name]
                    try:
                        if hasattr(component, 'stop'):
                            await component.stop()
                        elif hasattr(component, 'shutdown'):
                            await component.shutdown()
                        logger.info(f"Shutdown {component_name}")
                    except Exception as e:
                        logger.error(f"Error shutting down {component_name}: {e}")
            
            logger.info("Syn_OS system shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during system shutdown: {e}")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.shutdown_system())
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run(self):
        """Main run loop"""
        try:
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Start the system
            if not await self.start_system():
                logger.error("Failed to start Syn_OS system")
                return False
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
            # Shutdown system
            await self.shutdown_system()
            
            return True
            
        except Exception as e:
            logger.error(f"Error in main run loop: {e}")
            return False


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Syn_OS - Consciousness-Aware Security Operating System")
    parser.add_argument(
        "--config", 
        default="config/syn_os_config.yaml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information"
    )
    
    args = parser.parse_args()
    
    if args.version:
        print("Syn_OS v1.0.0-alpha (Consciousness)")
        print("Consciousness-Aware Security Operating System")
        print("Based on ParrotOS 6.4")
        return
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Create orchestrator
    orchestrator = SynOSOrchestrator(args.config)
    
    try:
        # Run the system
        success = await orchestrator.run()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Ensure we're running with Python 3.8+
    if sys.version_info < (3, 8):
        print("Error: Syn_OS requires Python 3.8 or higher")
        sys.exit(1)
    
    # Run the main function
    asyncio.run(main())