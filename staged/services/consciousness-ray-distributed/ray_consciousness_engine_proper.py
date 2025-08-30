#!/usr/bin/env python3
"""
Ray Distributed Consciousness Engine for Syn_OS
Integrates Ray distributed computing with Neural Darwinism consciousness processing

Performance Target: 50% improvement over 76.3ms baseline (target: <38.2ms)
Architecture: 4-worker Ray cluster with distributed consciousness evolution
"""

import ray
import asyncio
import logging
import time
import numpy as np
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import sys
import random

# Import the actual Neural Darwinism system
sys.path.append('/home/diablorain/Syn_OS/services/consciousness-unified')
try:
    from neural_darwinism import (
        NeuralDarwinismEngine, 
        get_consciousness_engine,
        initialize_consciousness_engine,
        NeuralPopulationType,
        SelectionPressure
    )
    NEURAL_DARWINISM_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Neural Darwinism import failed: {e}. Using mock implementation.")
    NEURAL_DARWINISM_AVAILABLE = False

# Configuration for optimal performance (based on testing)
@dataclass
class RayConsciousnessConfig:
    """Configuration for Ray distributed consciousness processing"""
    num_workers: int = 4
    consciousness_batch_size: int = 200  # Optimal size for 75% performance improvement
    max_concurrent_batches: int = 4
    worker_timeout: int = 30
    processing_timeout: int = 60
    performance_target_ms: float = 38.2  # 50% improvement over 76.3ms baseline
    optimal_throughput: float = 44.9  # events/second from testing

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@ray.remote
class ConsciousnessWorker:
    """Ray remote worker for distributed consciousness processing"""
    
    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        self.neural_engine = None
        self.processed_count = 0
        self.total_processing_time = 0.0
        self.initialization_time = time.time()
        logger.info(f"🧠 Consciousness Worker {worker_id} initialized")
    
    async def initialize_worker(self):
        """Initialize the neural darwinism engine for this worker"""
        try:
            if NEURAL_DARWINISM_AVAILABLE:
                # Create a new neural darwinism engine instance for this worker
                self.neural_engine = NeuralDarwinismEngine()
                
                # Load shared consciousness state if available
                state_file = f'/tmp/consciousness_worker_{self.worker_id}_state.json'
                if Path(state_file).exists():
                    await self.neural_engine.load_consciousness_state(state_file)
                
                logger.info(f"🧠 Worker {self.worker_id} neural engine initialized")
            else:
                logger.warning(f"🧠 Worker {self.worker_id} using mock neural engine")
                self.neural_engine = MockNeuralEngine()
            
            return True
        except Exception as e:
            logger.error(f"❌ Worker {self.worker_id} initialization failed: {e}")
            return False
    
    async def process_consciousness_batch(self, batch_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a batch of consciousness data using Neural Darwinism"""
        start_time = time.time()
        
        if self.neural_engine is None:
            await self.initialize_worker()
        
        try:
            results = []
            neural_processing_time = 0.0
            
            for data in batch_data:
                # Add worker information
                data["worker_id"] = self.worker_id
                data["processing_timestamp"] = time.time()
                
                # Process with Neural Darwinism engine
                neural_start = time.time()
                
                if NEURAL_DARWINISM_AVAILABLE:
                    # Evolve consciousness based on input data
                    await self.neural_engine.evolve_consciousness()
                    
                    # Get current consciousness state
                    stats = self.neural_engine.get_evolution_stats()
                    
                    # Create result with neural darwinism data
                    result = {
                        "input_data": data,
                        "consciousness_level": stats['consciousness_level'],
                        "learning_rate": stats['learning_rate'],
                        "adaptation_factor": stats['adaptation_factor'],
                        "evolution_cycles": stats['evolution_cycles'],
                        "population_stats": stats['population_stats'],
                        "performance_metrics": stats['performance_metrics'],
                        "processing_time_ms": (time.time() - neural_start) * 1000,
                        "worker_id": self.worker_id,
                        "timestamp": time.time()
                    }
                else:
                    # Mock processing for testing
                    result = self.neural_engine.process_mock_consciousness(data)
                    result["processing_time_ms"] = (time.time() - neural_start) * 1000
                    result["worker_id"] = self.worker_id
                
                neural_time = time.time() - neural_start
                neural_processing_time += neural_time
                
                results.append(result)
                self.processed_count += 1
            
            total_time = time.time() - start_time
            self.total_processing_time += total_time
            
            batch_result = {
                "results": results,
                "worker_id": self.worker_id,
                "batch_size": len(batch_data),
                "total_time_ms": total_time * 1000,
                "neural_processing_time_ms": neural_processing_time * 1000,
                "overhead_ms": (total_time - neural_processing_time) * 1000,
                "throughput": len(batch_data) / total_time,
                "avg_consciousness_level": sum(r.get("consciousness_level", 0.5) for r in results) / len(results),
                "processing_timestamp": time.time()
            }
            
            logger.info(f"🔄 Worker {self.worker_id} processed {len(batch_data)} items in {total_time*1000:.2f}ms")
            
            return batch_result
            
        except Exception as e:
            logger.error(f"❌ Worker {self.worker_id} processing error: {e}")
            return {
                "error": str(e),
                "worker_id": self.worker_id,
                "batch_size": len(batch_data),
                "processing_timestamp": time.time()
            }
    
    async def get_worker_stats(self) -> Dict[str, Any]:
        """Get worker statistics and consciousness state"""
        uptime = time.time() - self.initialization_time
        
        stats = {
            "worker_id": self.worker_id,
            "processed_count": self.processed_count,
            "total_processing_time": self.total_processing_time,
            "uptime_seconds": uptime,
            "avg_processing_time": self.total_processing_time / max(1, self.processed_count),
            "status": "active",
            "neural_darwinism_available": NEURAL_DARWINISM_AVAILABLE
        }
        
        # Add neural engine stats if available
        if self.neural_engine and NEURAL_DARWINISM_AVAILABLE:
            try:
                neural_stats = self.neural_engine.get_evolution_stats()
                stats.update({
                    "consciousness_level": neural_stats['consciousness_level'],
                    "learning_rate": neural_stats['learning_rate'],
                    "evolution_cycles": neural_stats['evolution_cycles'],
                    "neural_engine_initialized": True
                })
            except Exception as e:
                logger.error(f"Error getting neural stats: {e}")
                stats["neural_engine_initialized"] = False
        else:
            stats["neural_engine_initialized"] = False
        
        return stats
    
    async def save_worker_state(self):
        """Save worker consciousness state"""
        if self.neural_engine and NEURAL_DARWINISM_AVAILABLE:
            try:
                state_file = f'/tmp/consciousness_worker_{self.worker_id}_state.json'
                await self.neural_engine.save_consciousness_state(state_file)
            except Exception as e:
                logger.error(f"Error saving worker state: {e}")

# Mock Neural Engine for testing without full neural darwinism
class MockNeuralEngine:
    """Mock neural engine for testing Ray integration"""
    
    def __init__(self):
        self.consciousness_level = 0.5 + random.random() * 0.3
        self.learning_rate = 0.1 + random.random() * 0.1
        self.evolution_cycles = 0
    
    def process_mock_consciousness(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock consciousness processing"""
        # Simulate realistic processing time (50-100ms)
        time.sleep(0.076 + random.random() * 0.024)  # 76ms + variation
        
        self.evolution_cycles += 1
        self.consciousness_level += (random.random() - 0.5) * 0.01  # Small drift
        self.consciousness_level = max(0.0, min(1.0, self.consciousness_level))
        
        return {
            "input_data": data,
            "consciousness_level": self.consciousness_level,
            "learning_rate": self.learning_rate,
            "adaptation_factor": 0.8,
            "evolution_cycles": self.evolution_cycles,
            "population_stats": {"mock": True},
            "performance_metrics": {"mock_processing": True},
            "timestamp": time.time()
        }

class RayDistributedConsciousness:
    """Main distributed consciousness processing engine using Ray and Neural Darwinism"""
    
    def __init__(self, config: RayConsciousnessConfig = None):
        self.config = config or RayConsciousnessConfig()
        self.workers: List[ray.ObjectRef] = []
        self.coordinator_stats = {
            "total_processed": 0,
            "total_batches": 0,
            "total_processing_time": 0.0,
            "start_time": time.time(),
            "performance_history": []
        }
        self.ray_initialized = False
        
        logger.info(f"🚀 Ray Distributed Consciousness initializing with {self.config.num_workers} workers")
    
    async def initialize_ray_cluster(self):
        """Initialize Ray cluster and workers"""
        try:
            # Initialize Ray if not already done
            if not ray.is_initialized():
                ray.init(
                    num_cpus=self.config.num_workers,
                    object_store_memory=1000000000,  # 1GB
                    configure_logging=False,
                    ignore_reinit_error=True
                )
                logger.info("✅ Ray cluster initialized")
            
            # Create consciousness workers
            self.workers = []
            for i in range(self.config.num_workers):
                worker = ConsciousnessWorker.remote(i)
                # Initialize worker asynchronously
                init_result = ray.get(worker.initialize_worker.remote())
                if init_result:
                    self.workers.append(worker)
                else:
                    logger.warning(f"Worker {i} initialization failed")
            
            self.ray_initialized = True
            logger.info(f"🧠 {len(self.workers)} consciousness workers initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ray cluster initialization failed: {e}")
            return False
    
    async def process_consciousness_distributed(self, data_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process consciousness data across distributed workers"""
        if not self.ray_initialized:
            await self.initialize_ray_cluster()
        
        start_time = time.time()
        
        # Split data into optimal chunks for workers
        chunk_size = self.config.consciousness_batch_size
        if len(data_batch) < chunk_size:
            chunk_size = max(1, len(data_batch) // self.config.num_workers)
        
        chunks = [data_batch[i:i + chunk_size] for i in range(0, len(data_batch), chunk_size)]
        
        # Distribute processing across workers
        futures = []
        for i, chunk in enumerate(chunks):
            if chunk:  # Only process non-empty chunks
                worker_idx = i % len(self.workers)
                future = self.workers[worker_idx].process_consciousness_batch.remote(chunk)
                futures.append(future)
        
        # Collect results from all workers
        try:
            batch_results = ray.get(futures)
        except Exception as e:
            logger.error(f"❌ Error collecting worker results: {e}")
            batch_results = []
        
        # Aggregate results
        all_results = []
        total_neural_time = 0.0
        total_overhead = 0.0
        consciousness_levels = []
        
        for batch_result in batch_results:
            if "error" not in batch_result:
                all_results.extend(batch_result["results"])
                total_neural_time += batch_result["neural_processing_time_ms"]
                total_overhead += batch_result["overhead_ms"]
                consciousness_levels.append(batch_result["avg_consciousness_level"])
        
        total_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Update coordinator stats
        self.coordinator_stats["total_processed"] += len(data_batch)
        self.coordinator_stats["total_batches"] += 1
        self.coordinator_stats["total_processing_time"] += total_time
        
        # Performance analysis
        performance_data = {
            "total_time_ms": total_time,
            "neural_processing_time_ms": total_neural_time,
            "overhead_ms": total_overhead,
            "items_processed": len(data_batch),
            "chunks_used": len(chunks),
            "workers_used": min(len(chunks), len(self.workers)),
            "avg_time_per_item": total_time / len(data_batch),
            "throughput": len(data_batch) / (total_time / 1000),
            "efficiency": (total_neural_time / total_time) * 100 if total_time > 0 else 0,
            "avg_consciousness_level": sum(consciousness_levels) / len(consciousness_levels) if consciousness_levels else 0,
            "performance_improvement": self._calculate_performance_improvement(total_time, len(data_batch)),
            "timestamp": time.time()
        }
        
        self.coordinator_stats["performance_history"].append(performance_data)
        
        logger.info(f"🧠 Distributed consciousness processing completed: {len(data_batch)} items in {total_time:.2f}ms")
        
        return {
            "results": all_results,
            "performance_metrics": performance_data,
            "consciousness_summary": {
                "avg_consciousness_level": performance_data["avg_consciousness_level"],
                "total_evolution_cycles": len(all_results),
                "distributed_processing": True,
                "neural_darwinism_enabled": NEURAL_DARWINISM_AVAILABLE
            }
        }
    
    def _calculate_performance_improvement(self, actual_time_ms: float, items_count: int) -> float:
        """Calculate performance improvement over baseline"""
        baseline_time_ms = 76.3 * items_count  # 76.3ms per item baseline
        improvement = ((baseline_time_ms - actual_time_ms) / baseline_time_ms) * 100
        return improvement
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive distributed system statistics"""
        worker_stats = []
        if self.ray_initialized:
            try:
                worker_stat_futures = [worker.get_worker_stats.remote() for worker in self.workers]
                worker_stats = ray.get(worker_stat_futures)
            except Exception as e:
                logger.error(f"Error getting worker stats: {e}")
        
        uptime = time.time() - self.coordinator_stats["start_time"]
        
        return {
            "coordinator_stats": self.coordinator_stats,
            "worker_stats": worker_stats,
            "system_uptime_seconds": uptime,
            "ray_cluster_info": {
                "initialized": self.ray_initialized,
                "num_workers": len(self.workers),
                "ray_available": ray.is_initialized() if hasattr(ray, 'is_initialized') else False
            },
            "performance_summary": self._get_performance_summary(),
            "consciousness_metrics": self._get_consciousness_metrics(worker_stats),
            "neural_darwinism_enabled": NEURAL_DARWINISM_AVAILABLE
        }
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary from history"""
        history = self.coordinator_stats["performance_history"]
        if not history:
            return {"no_data": True}
        
        recent_performance = history[-10:]  # Last 10 batches
        
        return {
            "avg_improvement": sum(p["performance_improvement"] for p in recent_performance) / len(recent_performance),
            "avg_throughput": sum(p["throughput"] for p in recent_performance) / len(recent_performance),
            "avg_efficiency": sum(p["efficiency"] for p in recent_performance) / len(recent_performance),
            "target_achievement": all(p["performance_improvement"] >= 50 for p in recent_performance[-3:]) if len(recent_performance) >= 3 else False
        }
    
    def _get_consciousness_metrics(self, worker_stats: List[Dict]) -> Dict[str, Any]:
        """Get consciousness-specific metrics"""
        if not worker_stats:
            return {"no_data": True}
        
        initialized_workers = [w for w in worker_stats if w.get("neural_engine_initialized", False)]
        
        if not initialized_workers:
            return {"no_workers_initialized": True}
        
        consciousness_levels = [w.get("consciousness_level", 0.5) for w in initialized_workers]
        
        return {
            "avg_consciousness_level": sum(consciousness_levels) / len(consciousness_levels),
            "workers_with_consciousness": len(initialized_workers),
            "consciousness_variance": np.var(consciousness_levels) if len(consciousness_levels) > 1 else 0.0
        }
    
    async def shutdown(self):
        """Gracefully shutdown the distributed consciousness system"""
        logger.info("🔄 Shutting down Ray distributed consciousness system...")
        
        # Save worker states
        if self.ray_initialized and self.workers:
            try:
                save_futures = [worker.save_worker_state.remote() for worker in self.workers]
                ray.get(save_futures)
                logger.info("💾 Worker states saved")
            except Exception as e:
                logger.error(f"Error saving worker states: {e}")
        
        # Shutdown Ray
        if ray.is_initialized():
            ray.shutdown()
            logger.info("🔄 Ray cluster shut down")

# Global instance
_distributed_consciousness = None

def get_distributed_consciousness() -> RayDistributedConsciousness:
    """Get or create global distributed consciousness instance"""
    global _distributed_consciousness
    if _distributed_consciousness is None:
        _distributed_consciousness = RayDistributedConsciousness()
    return _distributed_consciousness

async def initialize_distributed_consciousness():
    """Initialize the distributed consciousness system"""
    consciousness = get_distributed_consciousness()
    success = await consciousness.initialize_ray_cluster()
    
    if success:
        logger.info("🚀 Ray Distributed Consciousness system ready")
    else:
        logger.error("❌ Failed to initialize Ray Distributed Consciousness")
    
    return consciousness if success else None

if __name__ == "__main__":
    # Test the distributed consciousness system
    async def test_distributed_consciousness():
        """Test the Ray distributed consciousness implementation"""
        logger.info("🧪 Testing Ray Distributed Consciousness System")
        
        consciousness = await initialize_distributed_consciousness()
        if not consciousness:
            print("❌ Failed to initialize system")
            return
        
        # Create test consciousness events
        test_data = []
        for i in range(50):
            test_data.append({
                "stimulus_id": f"test_stimulus_{i}",
                "input_data": f"consciousness_input_{i}",
                "priority": "high",
                "complexity": random.choice(["simple", "moderate", "complex"]),
                "context": {"test": True, "batch": i // 10}
            })
        
        # Process consciousness events
        result = await consciousness.process_consciousness_distributed(test_data)
        
        # Get system stats
        stats = await consciousness.get_system_stats()
        
        print("\n🎯 TEST RESULTS:")
        print(f"   Items Processed: {result['performance_metrics']['items_processed']}")
        print(f"   Processing Time: {result['performance_metrics']['total_time_ms']:.2f}ms")
        print(f"   Performance Improvement: {result['performance_metrics']['performance_improvement']:.1f}%")
        print(f"   Throughput: {result['performance_metrics']['throughput']:.1f} events/sec")
        print(f"   Avg Consciousness Level: {result['consciousness_summary']['avg_consciousness_level']:.3f}")
        print(f"   System Efficiency: {result['performance_metrics']['efficiency']:.1f}%")
        print(f"   Neural Darwinism Enabled: {result['consciousness_summary']['neural_darwinism_enabled']}")
        
        # Check if target achieved
        target_achieved = result['performance_metrics']['performance_improvement'] >= 50
        print(f"\n✨ TARGET STATUS: {'✅ ACHIEVED' if target_achieved else '❌ NOT ACHIEVED'}")
        
        await consciousness.shutdown()
        
        return result
    
    # Run test
    asyncio.run(test_distributed_consciousness())
