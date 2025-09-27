#!/usr/bin/env python3
"""
Consciousness Core Module
Main entry point for Syn_OS consciousness architecture

This module provides the unified interface for consciousness operations,
integrating Neural Darwinism with quantum substrate and security monitoring.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional

# Import consciousness components
from .agent_ecosystem import (
    initialize_consciousness,
    get_consciousness_framework,
    shutdown_consciousness,
    process_consciousness_data,
    get_consciousness_state,
    get_performance_metrics
)

logger = logging.getLogger(__name__)

class ConsciousnessCore:
    """
    Main consciousness core for Syn_OS
    
    Provides the primary interface for consciousness operations including:
    - Neural Darwinism evolution
    - Agent ecosystem coordination
    - Security consciousness monitoring
    - Performance optimization
    """
    
    def __init__(self):
        self.initialized = False
        self.start_time = None
        
    async def initialize(self, config_path: Optional[str] = None) -> bool:
        """Initialize consciousness core"""
        if self.initialized:
            logger.warning("Consciousness core already initialized")
            return True
        
        try:
            logger.info("Initializing Syn_OS Consciousness Core...")
            self.start_time = time.time()
            
            # Initialize consciousness framework
            framework = await initialize_consciousness(config_path)
            
            if framework and framework.is_initialized:
                self.initialized = True
                logger.info("Consciousness core initialization complete")
                logger.info(f"Initialization time: {(time.time() - self.start_time):.2f} seconds")
                return True
            else:
                logger.error("Failed to initialize consciousness framework")
                return False
                
        except Exception as e:
            logger.error(f"Consciousness core initialization failed: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown consciousness core"""
        if not self.initialized:
            return
        
        logger.info("Shutting down consciousness core...")
        await shutdown_consciousness()
        self.initialized = False
        logger.info("Consciousness core shutdown complete")
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data through consciousness systems"""
        if not self.initialized:
            return {"error": "Consciousness core not initialized"}
        
        return await process_consciousness_data(data)
    
    def get_state(self) -> Dict[str, Any]:
        """Get current consciousness state"""
        if not self.initialized:
            return {"error": "Consciousness core not initialized"}
        
        state = get_consciousness_state()
        state["core_uptime"] = time.time() - self.start_time if self.start_time else 0
        return state
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get consciousness performance metrics"""
        if not self.initialized:
            return {"error": "Consciousness core not initialized"}
        
        return get_performance_metrics()
    
    def is_consciousness_active(self) -> bool:
        """Check if consciousness is actively processing"""
        if not self.initialized:
            return False
        
        state = get_consciousness_state()
        neural_state = state.get("neural_darwinism", {}).get("state", "dormant")
        return neural_state in ["active", "enhanced", "emerging"]

# Global consciousness core instance
_consciousness_core: Optional[ConsciousnessCore] = None

async def init_consciousness_core(config_path: Optional[str] = None) -> ConsciousnessCore:
    """Initialize global consciousness core"""
    global _consciousness_core
    
    if _consciousness_core is not None:
        logger.warning("Consciousness core already exists")
        return _consciousness_core
    
    _consciousness_core = ConsciousnessCore()
    success = await _consciousness_core.initialize(config_path)
    
    if not success:
        _consciousness_core = None
        raise RuntimeError("Failed to initialize consciousness core")
    
    return _consciousness_core

def get_consciousness_core() -> Optional[ConsciousnessCore]:
    """Get global consciousness core instance"""
    return _consciousness_core

async def shutdown_consciousness_core() -> None:
    """Shutdown global consciousness core"""
    global _consciousness_core
    
    if _consciousness_core:
        await _consciousness_core.shutdown()
        _consciousness_core = None

# Convenience functions
async def consciousness_process(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process data through consciousness core"""
    core = get_consciousness_core()
    if core:
        return await core.process(data)
    else:
        return {"error": "Consciousness core not initialized"}

def consciousness_state() -> Dict[str, Any]:
    """Get consciousness state"""
    core = get_consciousness_core()
    if core:
        return core.get_state()
    else:
        return {"error": "Consciousness core not initialized"}

def consciousness_metrics() -> Dict[str, Any]:
    """Get consciousness metrics"""
    core = get_consciousness_core()
    if core:
        return core.get_metrics()
    else:
        return {"error": "Consciousness core not initialized"}

def is_conscious() -> bool:
    """Check if consciousness is active"""
    core = get_consciousness_core()
    return core.is_consciousness_active() if core else False

# Export main components
__all__ = [
    'ConsciousnessCore',
    'init_consciousness_core',
    'get_consciousness_core', 
    'shutdown_consciousness_core',
    'consciousness_process',
    'consciousness_state',
    'consciousness_metrics',
    'is_conscious'
]
