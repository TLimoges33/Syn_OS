"""
Main NATS Integration for Consciousness System V2
================================================

This module provides the main integration point for the consciousness system
with NATS messaging, bringing together all components for service-to-service
communication.
"""

import asyncio
import logging
import os
import signal
import json
from typing import Optional
from datetime import datetime
from pathlib import Path

from .components.event_bus import EventBus
from .components.consciousness_core import ConsciousnessCore
from .bridges.nats_bridge import NATSBridge
from .core.state_manager import StateManager
from .core.consciousness_bus import ConsciousnessBus


class ConsciousnessNATSService:
    """
    Main consciousness service with NATS integration
    
    Coordinates all consciousness components and provides NATS messaging
    for service-to-service communication with the orchestrator.
    """
    
    def __init__(self,
                 nats_url: Optional[str] = None,
                 persistence_path: Optional[str] = None):
        """
        Initialize consciousness NATS service
        
        Args:
            nats_url: NATS server URL (defaults to env var or localhost)
            persistence_path: Path for state persistence
        """
        # Configuration
        self.nats_url = nats_url or os.getenv('NATS_URL', 'nats://localhost:4222')
        self.persistence_path = persistence_path or os.getenv('CONSCIOUSNESS_DATA_PATH', 'data/consciousness')
        
        # Core components
        self.state_manager: Optional[StateManager] = None
        self.consciousness_core: Optional[ConsciousnessCore] = None
        self.event_bus: Optional[EventBus] = None
        self.nats_bridge: Optional[NATSBridge] = None
        
        # Service state
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
        # Logger
        self.logger = logging.getLogger(__name__)
        
        # Signal handlers
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start(self) -> bool:
        """Start the consciousness NATS service"""
        if self.is_running:
            self.logger.warning("Consciousness NATS service is already running")
            return True
        
        try:
            self.logger.info("Starting Consciousness NATS Service...")
            
            # Initialize state manager
            self.logger.info("Initializing state manager...")
            persistence_path = Path(self.persistence_path) if self.persistence_path else None
            self.state_manager = StateManager(persistence_path=persistence_path)
            if not await self.state_manager.start():
                raise RuntimeError("Failed to start state manager")
            
            # Initialize consciousness core
            self.logger.info("Initializing consciousness core...")
            self.consciousness_core = ConsciousnessCore(self.state_manager)
            if not await self.consciousness_core.start():
                raise RuntimeError("Failed to start consciousness core")
            
            # Initialize event bus
            self.logger.info("Initializing event bus...")
            self.event_bus = EventBus()
            if not await self.event_bus.start():
                raise RuntimeError("Failed to start event bus")
            
            # Initialize NATS bridge
            self.logger.info("Initializing NATS bridge...")
            self.nats_bridge = NATSBridge(
                nats_url=self.nats_url,
                consciousness_core=self.consciousness_core,
                event_bus=self.event_bus
            )
            
            # Start NATS bridge (this will run in background)
            bridge_task = asyncio.create_task(self.nats_bridge.start())
            
            # Wait a moment to ensure NATS connection is established
            await asyncio.sleep(2)
            
            # Verify NATS connection
            if not self.nats_bridge.nc or not self.nats_bridge.nc.is_connected():
                raise RuntimeError("Failed to establish NATS connection")
            
            self.is_running = True
            
            # Publish initial consciousness state
            await self._publish_initial_state()
            
            # Start health monitoring
            asyncio.create_task(self._health_monitoring_loop())
            
            self.logger.info("✅ Consciousness NATS Service started successfully")
            self.logger.info(f"   - NATS URL: {self.nats_url}")
            self.logger.info(f"   - Persistence: {self.persistence_path}")
            self.logger.info(f"   - Components: State Manager, Consciousness Core, Event Bus, NATS Bridge")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start Consciousness NATS Service: {e}")
            await self.stop()
            return False
    
    async def stop(self) -> None:
        """Stop the consciousness NATS service"""
        if not self.is_running:
            return
        
        self.logger.info("Stopping Consciousness NATS Service...")
        self.is_running = False
        self.shutdown_event.set()
        
        # Stop components in reverse order
        if self.nats_bridge:
            await self.nats_bridge.stop()
            await self.nats_bridge.disconnect()
        
        if self.event_bus:
            await self.event_bus.stop()
        
        if self.consciousness_core:
            await self.consciousness_core.stop()
        
        if self.state_manager:
            await self.state_manager.stop()
        
        self.logger.info("✅ Consciousness NATS Service stopped")
    
    async def run(self) -> None:
        """Run the service until shutdown"""
        if not await self.start():
            return
        
        try:
            # Wait for shutdown signal
            await self.shutdown_event.wait()
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        finally:
            await self.stop()
    
    async def _publish_initial_state(self) -> None:
        """Publish initial consciousness state to NATS"""
        try:
            if self.nats_bridge and self.consciousness_core:
                await self.nats_bridge.publish_consciousness_state()
                self.logger.info("Published initial consciousness state to NATS")
        except Exception as e:
            self.logger.error(f"Failed to publish initial state: {e}")
    
    async def _health_monitoring_loop(self) -> None:
        """Background health monitoring loop"""
        while self.is_running:
            try:
                await self._perform_health_check()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                self.logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(30)
    
    async def _perform_health_check(self) -> None:
        """Perform health check on all components"""
        try:
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'service_status': 'healthy',
                'components': {}
            }
            
            # Check state manager
            if self.state_manager and self.state_manager.is_running:
                metrics = await self.state_manager.get_state_metrics()
                health_status['components']['state_manager'] = {
                    'status': 'healthy',
                    'metrics': metrics
                }
            else:
                health_status['components']['state_manager'] = {'status': 'failed'}
                health_status['service_status'] = 'degraded'
            
            # Check consciousness core
            if self.consciousness_core and self.consciousness_core.is_running:
                health_status['components']['consciousness_core'] = {
                    'status': 'healthy',
                    'attention_level': self.consciousness_core.get_attention_level(),
                    'cognitive_load': self.consciousness_core.get_cognitive_load(),
                    'emotional_state': self.consciousness_core.get_emotional_state()
                }
            else:
                health_status['components']['consciousness_core'] = {'status': 'failed'}
                health_status['service_status'] = 'degraded'
            
            # Check event bus
            if self.event_bus and self.event_bus.is_running:
                health_status['components']['event_bus'] = {'status': 'healthy'}
            else:
                health_status['components']['event_bus'] = {'status': 'failed'}
                health_status['service_status'] = 'degraded'
            
            # Check NATS bridge
            if self.nats_bridge and self.nats_bridge.nc and self.nats_bridge.nc.is_connected():
                health_status['components']['nats_bridge'] = {
                    'status': 'healthy',
                    'connected': True,
                    'nats_url': self.nats_url
                }
            else:
                health_status['components']['nats_bridge'] = {'status': 'failed'}
                health_status['service_status'] = 'critical'
            
            # Publish health status to NATS
            if (self.nats_bridge and self.nats_bridge.js and
                health_status['service_status'] != 'critical'):
                await self.nats_bridge.js.publish(
                    'consciousness.health.status',
                    json.dumps(health_status).encode(),
                    headers={'Content-Type': 'application/json'}
                )
            
            # Log health status
            if health_status['service_status'] == 'healthy':
                self.logger.debug("Health check: All components healthy")
            else:
                self.logger.warning(f"Health check: Service status {health_status['service_status']}")
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
    
    async def get_service_status(self) -> dict:
        """Get current service status"""
        return {
            'is_running': self.is_running,
            'nats_url': self.nats_url,
            'persistence_path': self.persistence_path,
            'components': {
                'state_manager': self.state_manager.is_running if self.state_manager else False,
                'consciousness_core': self.consciousness_core.is_running if self.consciousness_core else False,
                'event_bus': self.event_bus.is_running if self.event_bus else False,
                'nats_bridge': (self.nats_bridge.nc.is_connected() 
                              if self.nats_bridge and self.nats_bridge.nc else False)
            }
        }


# Main entry point
async def main():
    """Main entry point for consciousness NATS service"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run service
    service = ConsciousnessNATSService()
    await service.run()


if __name__ == "__main__":
    asyncio.run(main())