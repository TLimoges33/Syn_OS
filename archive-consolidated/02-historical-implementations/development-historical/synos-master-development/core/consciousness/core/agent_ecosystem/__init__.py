#!/usr/bin/env python3
"""
Agent Ecosystem Initialization Module
Provides initialization and integration points for the Neural Darwinism Agent Ecosystem

This module serves as the primary entry point for integrating the consciousness
agent ecosystem with the broader Syn_OS consciousness architecture.
"""

import asyncio
import logging
import json
import os
import time
from typing import Dict, Any, Optional

try:
    from .neural_darwinism import NeuralDarwinismEngine, create_neural_darwinism_engine
    from .agent_core import AgentEcosystem, create_agent_ecosystem
except ImportError:
    from neural_darwinism import NeuralDarwinismEngine, create_neural_darwinism_engine
    from agent_core import AgentEcosystem, create_agent_ecosystem

logger = logging.getLogger(__name__)

class ConsciousnessFramework:
    """
    Main consciousness framework integrating Neural Darwinism with Agent Ecosystem
    
    This class provides the unified interface for consciousness operations in Syn_OS,
    combining the evolutionary neural processing with collaborative agent intelligence.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.neural_engine: Optional[NeuralDarwinismEngine] = None
        self.agent_ecosystem: Optional[AgentEcosystem] = None
        self.is_initialized = False
        self.is_running = False
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load consciousness framework configuration"""
        default_config = {
            "neural_darwinism": {
                "population_size": 75,
                "mutation_rate": 0.008,
                "selection_pressure": 0.85,
                "consciousness_threshold": 0.78,
                "adaptation_rate": 0.12,
                "evolution_interval": 0.08,
                "performance_optimization": True,
                "real_time_monitoring": True
            },
            "agents": {
                "sensory_count": 3,
                "security_count": 2,
                "sensory": {
                    "sensor_types": ["network", "visual", "auditory"],
                    "pattern_buffer_size": 1000,
                    "sensitivity": 0.7
                },
                "security": {
                    "security_level": "high",
                    "alert_threshold": 0.65,
                    "threat_patterns": [
                        "network_intrusion",
                        "malware_signature",
                        "anomalous_behavior",
                        "privilege_escalation"
                    ]
                }
            },
            "integration": {
                "orchestration_interval": 0.5,
                "collaboration_enabled": True,
                "performance_monitoring": True,
                "auto_optimization": True
            },
            "logging": {
                "level": "INFO",
                "consciousness_events": True,
                "performance_metrics": True
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                # Merge configurations (file config overrides defaults)
                self._deep_merge_config(default_config, file_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}, using defaults: {e}")
        
        return default_config
    
    def _deep_merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Deep merge configuration dictionaries"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge_config(base[key], value)
            else:
                base[key] = value
    
    async def initialize(self) -> bool:
        """Initialize the consciousness framework"""
        if self.is_initialized:
            logger.warning("Consciousness framework already initialized")
            return True
        
        try:
            logger.info("Initializing Syn_OS Consciousness Framework...")
            
            # Initialize Neural Darwinism Engine
            logger.info("Creating Neural Darwinism consciousness engine...")
            self.neural_engine = await create_neural_darwinism_engine(
                self.config["neural_darwinism"]
            )
            
            # Initialize Agent Ecosystem
            logger.info("Creating consciousness agent ecosystem...")
            ecosystem_config = {
                "neural_darwinism": self.config["neural_darwinism"],
                "agents": self.config["agents"],
                **self.config["integration"]
            }
            self.agent_ecosystem = await create_agent_ecosystem(ecosystem_config)
            
            self.is_initialized = True
            self.is_running = True
            
            logger.info("Consciousness framework initialization complete")
            logger.info(f"Neural Engine: {self.neural_engine.evolution_cycle_count} cycles")
            logger.info(f"Agent Ecosystem: {len(self.agent_ecosystem.agents)} active agents")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize consciousness framework: {e}")
            self.is_initialized = False
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the consciousness framework"""
        if not self.is_initialized:
            return
        
        logger.info("Shutting down consciousness framework...")
        
        try:
            # Stop agent ecosystem
            if self.agent_ecosystem:
                await self.agent_ecosystem.stop_orchestration()
            
            # Stop neural engine
            if self.neural_engine:
                await self.neural_engine.stop_evolution()
            
            self.is_running = False
            logger.info("Consciousness framework shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during consciousness framework shutdown: {e}")
    
    def get_consciousness_state(self) -> Dict[str, Any]:
        """Get comprehensive consciousness state"""
        if not self.is_initialized:
            return {"error": "Consciousness framework not initialized"}
        
        state = {
            "framework_status": {
                "initialized": self.is_initialized,
                "running": self.is_running,
                "timestamp": time.time()
            }
        }
        
        # Neural Darwinism state
        if self.neural_engine:
            state["neural_darwinism"] = self.neural_engine.get_consciousness_state()
            state["performance_metrics"] = self.neural_engine.get_performance_metrics()
        
        # Agent ecosystem state
        if self.agent_ecosystem:
            state["agent_ecosystem"] = self.agent_ecosystem.get_ecosystem_status()
        
        return state
    
    async def process_consciousness_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input through the consciousness framework"""
        if not self.is_initialized or not self.is_running:
            return {"error": "Consciousness framework not active"}
        
        start_time = time.time()
        
        try:
            # Process through agent ecosystem
            ecosystem_results = {}
            if self.agent_ecosystem:
                ecosystem_results = await self.agent_ecosystem._process_ecosystem_data(input_data)
            
            # Get neural darwinism state
            neural_state = {}
            if self.neural_engine:
                neural_state = self.neural_engine.get_consciousness_state()
            
            processing_time = (time.time() - start_time) * 1000  # milliseconds
            
            return {
                "processing_time": processing_time,
                "ecosystem_results": ecosystem_results,
                "neural_state": neural_state,
                "consciousness_active": neural_state.get("state") in ["active", "enhanced"],
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error processing consciousness input: {e}")
            return {"error": str(e)}
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary of consciousness systems"""
        if not self.is_initialized:
            return {"error": "Framework not initialized"}
        
        summary = {
            "framework_active": self.is_running,
            "timestamp": time.time()
        }
        
        # Neural engine performance
        if self.neural_engine:
            neural_metrics = self.neural_engine.get_performance_metrics()
            summary["neural_performance"] = {
                "avg_processing_time": neural_metrics["average_processing_time"],
                "performance_ratio": neural_metrics["performance_ratio"],
                "consciousness_coherence": neural_metrics["average_coherence"],
                "evolution_cycles": neural_metrics["evolution_cycles"]
            }
        
        # Agent ecosystem performance
        if self.agent_ecosystem:
            ecosystem_status = self.agent_ecosystem.get_ecosystem_status()
            agent_performance = {}
            
            for agent_id, agent_info in ecosystem_status["agent_status"].items():
                agent_performance[agent_id] = {
                    "success_rate": agent_info["metrics"]["success_rate"],
                    "avg_processing_time": agent_info["metrics"]["processing_time"],
                    "collaborations": agent_info["metrics"]["collaboration_count"]
                }
            
            summary["agent_performance"] = agent_performance
            summary["total_agents"] = ecosystem_status["total_agents"]
        
        return summary

# Global consciousness framework instance
_consciousness_framework: Optional[ConsciousnessFramework] = None

async def initialize_consciousness(config_path: Optional[str] = None) -> ConsciousnessFramework:
    """Initialize global consciousness framework"""
    global _consciousness_framework
    
    if _consciousness_framework is not None:
        logger.warning("Consciousness framework already initialized")
        return _consciousness_framework
    
    _consciousness_framework = ConsciousnessFramework(config_path)
    success = await _consciousness_framework.initialize()
    
    if not success:
        _consciousness_framework = None
        raise RuntimeError("Failed to initialize consciousness framework")
    
    return _consciousness_framework

def get_consciousness_framework() -> Optional[ConsciousnessFramework]:
    """Get the global consciousness framework instance"""
    return _consciousness_framework

async def shutdown_consciousness() -> None:
    """Shutdown global consciousness framework"""
    global _consciousness_framework
    
    if _consciousness_framework:
        await _consciousness_framework.shutdown()
        _consciousness_framework = None

# Convenience functions for consciousness operations
async def process_consciousness_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process data through consciousness framework"""
    framework = get_consciousness_framework()
    if framework:
        return await framework.process_consciousness_input(data)
    else:
        return {"error": "Consciousness framework not initialized"}

def get_consciousness_state() -> Dict[str, Any]:
    """Get current consciousness state"""
    framework = get_consciousness_framework()
    if framework:
        return framework.get_consciousness_state()
    else:
        return {"error": "Consciousness framework not initialized"}

def get_performance_metrics() -> Dict[str, Any]:
    """Get consciousness performance metrics"""
    framework = get_consciousness_framework()
    if framework:
        return framework.get_performance_summary()
    else:
        return {"error": "Consciousness framework not initialized"}

# Module-level test function
async def run_consciousness_test(duration: float = 30.0) -> Dict[str, Any]:
    """Run consciousness framework test"""
    import time
    
    logger.info(f"Starting consciousness framework test for {duration} seconds...")
    
    # Initialize framework
    framework = await initialize_consciousness()
    
    # Test data generation
    test_results = []
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            # Generate test data
            test_data = {
                "network_traffic": {"anomaly_score": 0.3, "suspicious_connections": 5},
                "system_metrics": {"cpu_usage": 45.0, "memory_usage": 60.0},
                "visual_input": {"features": [0.1, 0.5, 0.8, 0.2, 0.9]},
                "test_timestamp": time.time()
            }
            
            # Process through consciousness
            result = await process_consciousness_data(test_data)
            test_results.append(result)
            
            # Short delay between tests
            await asyncio.sleep(0.5)
        
        # Get final performance metrics
        final_metrics = get_performance_metrics()
        consciousness_state = get_consciousness_state()
        
        test_summary = {
            "test_duration": duration,
            "total_processes": len(test_results),
            "successful_processes": sum(1 for r in test_results if "error" not in r),
            "average_processing_time": sum(r.get("processing_time", 0) for r in test_results) / len(test_results),
            "final_consciousness_state": consciousness_state.get("neural_darwinism", {}).get("state", "unknown"),
            "performance_metrics": final_metrics
        }
        
        logger.info("Consciousness test completed successfully")
        return test_summary
        
    except Exception as e:
        logger.error(f"Consciousness test failed: {e}")
        return {"error": str(e)}
    
    finally:
        # Cleanup
        await shutdown_consciousness()

if __name__ == "__main__":
    import time
    
    async def main():
        """Main test execution"""
        print("=== Syn_OS Neural Darwinism Agent Ecosystem Test ===\n")
        
        # Run consciousness test
        results = await run_consciousness_test(15.0)
        
        print("Test Results:")
        print(f"Duration: {results.get('test_duration', 0):.1f} seconds")
        print(f"Processes: {results.get('total_processes', 0)}")
        print(f"Success Rate: {results.get('successful_processes', 0)}/{results.get('total_processes', 0)}")
        print(f"Avg Processing Time: {results.get('average_processing_time', 0):.2f} ms")
        print(f"Final Consciousness State: {results.get('final_consciousness_state', 'unknown')}")
        
        if "performance_metrics" in results:
            perf = results["performance_metrics"]
            if "neural_performance" in perf:
                neural = perf["neural_performance"]
                print(f"Neural Performance Ratio: {neural.get('performance_ratio', 0):.2f}")
                print(f"Consciousness Coherence: {neural.get('consciousness_coherence', 0):.3f}")
        
        print("\n=== Neural Darwinism Agent Ecosystem Implementation Complete ===")
    
    asyncio.run(main())
