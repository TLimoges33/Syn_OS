#!/usr/bin/env python3
"""
Consciousness System V2 Main Entry Point

This module serves as the main entry point for the consciousness system,
integrating all components and establishing the NATS bridge connection.
"""

import asyncio
import logging
import signal
import sys
import os
from typing import Optional

from .components.consciousness_core import ConsciousnessCore
from .components.event_bus import EventBus
from .bridges.nats_bridge import NATSBridge


class ConsciousnessSystem:
    """Main consciousness system orchestrator"""
    
    def __init__(self):
        """Initialize the consciousness system"""
        self.logger = logging.getLogger(__name__)
        self.consciousness_core: Optional[ConsciousnessCore] = None
        self.event_bus: Optional[EventBus] = None
        self.nats_bridge: Optional[NATSBridge] = None
        self.running = False
        
        # Configuration from environment
        self.nats_url = os.getenv('NATS_URL', 'nats://localhost:4222')
        self.orchestrator_url = os.getenv('ORCHESTRATOR_URL', 'http://localhost:8080')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.consciousness_mode = os.getenv('CONSCIOUSNESS_MODE', 'development')
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('/app/data/consciousness.log') if os.path.exists('/app/data') else logging.NullHandler()
            ]
        )
        
        # Set specific logger levels
        logging.getLogger('nats').setLevel(logging.WARNING)
        logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    async def initialize(self) -> bool:
        """Initialize all consciousness components"""
        try:
            self.logger.info("Initializing Consciousness System V2...")
            
            # Initialize event bus
            self.logger.info("Initializing event bus...")
            self.event_bus = EventBus()
            await self.event_bus.start()
            
            # Initialize consciousness core
            self.logger.info("Initializing consciousness core...")
            self.consciousness_core = ConsciousnessCore()
            await self.consciousness_core.start()
            
            # Initialize NATS bridge
            self.logger.info(f"Initializing NATS bridge to {self.nats_url}...")
            self.nats_bridge = NATSBridge(
                nats_url=self.nats_url,
                consciousness_core=self.consciousness_core,
                event_bus=self.event_bus
            )
            
            # Connect to NATS
            if not await self.nats_bridge.connect():
                self.logger.error("Failed to connect to NATS")
                return False
            
            self.logger.info("Consciousness System V2 initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize consciousness system: {e}")
            return False
    
    async def start(self):
        """Start the consciousness system"""
        if not await self.initialize():
            sys.exit(1)
        
        self.running = True
        self.logger.info("Starting Consciousness System V2...")
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            # Start all components
            tasks = []
            
            # Start consciousness core monitoring
            if self.consciousness_core:
                tasks.append(asyncio.create_task(self._consciousness_monitor()))
            
            # Start NATS bridge
            if self.nats_bridge:
                tasks.append(asyncio.create_task(self.nats_bridge.start()))
            
            # Start health check server
            tasks.append(asyncio.create_task(self._health_check_server()))
            
            # Start consciousness monitoring
            tasks.append(asyncio.create_task(self._consciousness_monitor()))
            
            self.logger.info("All consciousness components started")
            
            # Wait for all tasks
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            self.logger.error(f"Error running consciousness system: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown the consciousness system gracefully"""
        self.logger.info("Shutting down Consciousness System V2...")
        self.running = False
        
        # Shutdown components in reverse order
        if self.nats_bridge:
            await self.nats_bridge.stop()
            await self.nats_bridge.disconnect()
        
        if self.consciousness_core:
            await self.consciousness_core.stop()
        
        if self.event_bus:
            await self.event_bus.stop()
        
        self.logger.info("Consciousness System V2 shutdown complete")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, initiating shutdown...")
        self.running = False
    
    async def _health_check_server(self):
        """Simple health check server"""
        from aiohttp import web
        
        async def health_check(request):
            """Health check endpoint"""
            status = {
                'status': 'healthy' if self.running else 'shutting_down',
                'consciousness_core': self.consciousness_core is not None,
                'event_bus': self.event_bus is not None,
                'nats_bridge': self.nats_bridge is not None and self.nats_bridge.nc is not None,
                'mode': self.consciousness_mode
            }
            
            if self.consciousness_core:
                status['attention_level'] = self.consciousness_core.get_attention_level()
                status['cognitive_load'] = self.consciousness_core.get_cognitive_load()
                status['learning_mode'] = self.consciousness_core.get_learning_mode()
            
            return web.json_response(status)
        
        async def metrics(_request):
            """Metrics endpoint"""
            metrics_data = {}
            
            if self.consciousness_core:
                metrics_data['consciousness'] = {
                    'attention_level': self.consciousness_core.get_attention_level(),
                    'cognitive_load': self.consciousness_core.get_cognitive_load(),
                    'emotional_state': self.consciousness_core.get_emotional_state(),
                    'learning_mode': self.consciousness_core.get_learning_mode(),
                    'memory_size': self.consciousness_core.get_working_memory_size()
                }
            
            if self.event_bus:
                metrics_data['events'] = {
                    'running': self.event_bus.is_running,
                    'pending_count': self.event_bus.pending_events.qsize() if hasattr(self.event_bus, 'pending_events') else 0
                }
            
            return web.json_response(metrics_data)
        
        app = web.Application()
        app.router.add_get('/health', health_check)
        app.router.add_get('/metrics', metrics)
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        # Bind to localhost only for security instead of all interfaces
        site = web.TCPSite(runner, '127.0.0.1', 8081)
        await site.start()
        
        self.logger.info("Health check server started on port 8081")
        
        # Keep server running
        while self.running:
            await asyncio.sleep(1)
        
        await runner.cleanup()
    
    async def _consciousness_monitor(self):
        """Monitor consciousness state and publish updates"""
        while self.running:
            try:
                if self.nats_bridge and self.consciousness_core:
                    # Publish consciousness state every 30 seconds
                    await self.nats_bridge.publish_consciousness_state()
                
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error in consciousness monitor: {e}")
                await asyncio.sleep(5)


async def main():
    """Main entry point"""
    system = ConsciousnessSystem()
    await system.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)