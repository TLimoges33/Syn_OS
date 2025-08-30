#!/usr/bin/env python3
"""
GenAI OS - Ray Consciousness Production Deployment
Production deployment system for distributed consciousness processing
"""

import os
import sys
import logging
import asyncio
import ray
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.consciousness.neural_darwinism import NeuralDarwinismEngine
from src.consciousness.consciousness_core import ConsciousnessCore
from src.monitoring.performance_monitor import PerformanceMonitor

@dataclass
class ProductionConfig:
    """Production deployment configuration"""
    ray_cluster_address: Optional[str] = None
    num_workers: int = 4
    cpu_per_worker: int = 2
    memory_per_worker_gb: int = 4
    gpu_enabled: bool = False
    redis_url: str = "redis://localhost:6379"
    nats_url: str = "nats://localhost:4222"
    monitoring_enabled: bool = True
    log_level: str = "INFO"

class RayConsciousnessProduction:
    """Production-grade Ray consciousness deployment system"""
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.consciousness_core = None
        self.performance_monitor = None
        self.workers = []
        
    def _setup_logging(self) -> logging.Logger:
        """Setup production logging"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/var/log/genai-os/ray-consciousness.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)
    
    async def initialize_ray_cluster(self) -> bool:
        """Initialize Ray cluster for distributed consciousness processing"""
        try:
            if self.config.ray_cluster_address:
                # Connect to existing cluster
                ray.init(address=self.config.ray_cluster_address)
                self.logger.info(f"Connected to Ray cluster: {self.config.ray_cluster_address}")
            else:
                # Start local cluster
                ray.init(
                    num_cpus=self.config.num_workers * self.config.cpu_per_worker,
                    object_store_memory=self.config.memory_per_worker_gb * 1024**3,
                    include_dashboard=True
                )
                self.logger.info("Started local Ray cluster")
            
            # Verify cluster status
            cluster_resources = ray.cluster_resources()
            self.logger.info(f"Ray cluster resources: {cluster_resources}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Ray cluster: {e}")
            return False
    
    async def deploy_consciousness_workers(self) -> bool:
        """Deploy consciousness processing workers"""
        try:
            @ray.remote(num_cpus=self.config.cpu_per_worker, 
                       memory=self.config.memory_per_worker_gb * 1024**3)
            class ConsciousnessWorker:
                def __init__(self, worker_id: int):
                    self.worker_id = worker_id
                    self.consciousness_engine = NeuralDarwinismEngine()
                    self.processed_count = 0
                
                async def process_consciousness_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
                    """Process consciousness event"""
                    try:
                        result = await self.consciousness_engine.process_event(event_data)
                        self.processed_count += 1
                        return {
                            'worker_id': self.worker_id,
                            'processed_count': self.processed_count,
                            'result': result,
                            'status': 'success'
                        }
                    except Exception as e:
                        return {
                            'worker_id': self.worker_id,
                            'error': str(e),
                            'status': 'error'
                        }
                
                def get_worker_stats(self) -> Dict[str, Any]:
                    """Get worker statistics"""
                    return {
                        'worker_id': self.worker_id,
                        'processed_count': self.processed_count,
                        'status': 'active'
                    }
            
            # Deploy workers
            self.workers = []
            for i in range(self.config.num_workers):
                worker = ConsciousnessWorker.remote(i)
                self.workers.append(worker)
                self.logger.info(f"Deployed consciousness worker {i}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deploy consciousness workers: {e}")
            return False
    
    async def start_consciousness_core(self) -> bool:
        """Start the consciousness core system"""
        try:
            self.consciousness_core = ConsciousnessCore(
                distributed_mode=True,
                ray_workers=self.workers
            )
            
            await self.consciousness_core.initialize()
            self.logger.info("Consciousness core initialized in distributed mode")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start consciousness core: {e}")
            return False
    
    async def start_monitoring(self) -> bool:
        """Start performance monitoring"""
        if not self.config.monitoring_enabled:
            return True
            
        try:
            self.performance_monitor = PerformanceMonitor(
                ray_cluster=True,
                workers=self.workers
            )
            
            await self.performance_monitor.start()
            self.logger.info("Performance monitoring started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
            return False
    
    async def deploy(self) -> bool:
        """Complete production deployment"""
        self.logger.info("Starting GenAI OS consciousness production deployment...")
        
        # Deploy in stages
        stages = [
            ("Ray Cluster", self.initialize_ray_cluster),
            ("Consciousness Workers", self.deploy_consciousness_workers),
            ("Consciousness Core", self.start_consciousness_core),
            ("Performance Monitoring", self.start_monitoring)
        ]
        
        for stage_name, stage_func in stages:
            self.logger.info(f"Deploying {stage_name}...")
            if not await stage_func():
                self.logger.error(f"Failed to deploy {stage_name}")
                return False
            self.logger.info(f"{stage_name} deployed successfully")
        
        self.logger.info("GenAI OS consciousness production deployment complete!")
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_status = {
            'timestamp': asyncio.get_event_loop().time(),
            'overall_status': 'healthy',
            'components': {}
        }
        
        try:
            # Check Ray cluster
            ray_status = ray.cluster_resources()
            health_status['components']['ray_cluster'] = {
                'status': 'healthy',
                'resources': ray_status
            }
            
            # Check workers
            worker_stats = await asyncio.gather(*[
                worker.get_worker_stats.remote() for worker in self.workers
            ])
            health_status['components']['workers'] = {
                'status': 'healthy',
                'count': len(self.workers),
                'stats': worker_stats
            }
            
            # Check consciousness core
            if self.consciousness_core:
                core_stats = await self.consciousness_core.get_health_status()
                health_status['components']['consciousness_core'] = core_stats
            
            # Check monitoring
            if self.performance_monitor:
                monitor_stats = await self.performance_monitor.get_health_status()
                health_status['components']['monitoring'] = monitor_stats
                
        except Exception as e:
            health_status['overall_status'] = 'unhealthy'
            health_status['error'] = str(e)
        
        return health_status
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("Shutting down consciousness production deployment...")
        
        # Stop monitoring
        if self.performance_monitor:
            await self.performance_monitor.stop()
        
        # Stop consciousness core
        if self.consciousness_core:
            await self.consciousness_core.shutdown()
        
        # Stop Ray cluster
        ray.shutdown()
        
        self.logger.info("Consciousness production deployment shutdown complete")

async def main():
    """Main deployment entry point"""
    # Load configuration from environment
    config = ProductionConfig(
        ray_cluster_address=os.getenv('RAY_CLUSTER_ADDRESS'),
        num_workers=int(os.getenv('CONSCIOUSNESS_WORKERS', '4')),
        cpu_per_worker=int(os.getenv('CPU_PER_WORKER', '2')),
        memory_per_worker_gb=int(os.getenv('MEMORY_PER_WORKER_GB', '4')),
        gpu_enabled=os.getenv('GPU_ENABLED', 'false').lower() == 'true',
        redis_url=os.getenv('REDIS_URL', 'redis://localhost:6379'),
        nats_url=os.getenv('NATS_URL', 'nats://localhost:4222'),
        monitoring_enabled=os.getenv('MONITORING_ENABLED', 'true').lower() == 'true',
        log_level=os.getenv('LOG_LEVEL', 'INFO')
    )
    
    # Deploy consciousness system
    deployment = RayConsciousnessProduction(config)
    
    try:
        success = await deployment.deploy()
        if success:
            print("✅ GenAI OS consciousness production deployment successful!")
            
            # Run health check
            health = await deployment.health_check()
            print(f"🏥 Health Status: {health['overall_status']}")
            
            # Keep running (in production, this would be managed by systemd/k8s)
            if os.getenv('KEEP_RUNNING', 'false').lower() == 'true':
                print("🔄 Running in daemon mode...")
                try:
                    while True:
                        await asyncio.sleep(60)
                        health = await deployment.health_check()
                        if health['overall_status'] != 'healthy':
                            print(f"⚠️  Health check failed: {health}")
                except KeyboardInterrupt:
                    print("👋 Received shutdown signal")
        else:
            print("❌ GenAI OS consciousness production deployment failed!")
            sys.exit(1)
    
    finally:
        await deployment.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
