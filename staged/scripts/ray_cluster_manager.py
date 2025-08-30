#!/usr/bin/env python3
"""
Ray Cluster Memory Management Script
Handles startup, shutdown, and memory cleanup for Ray distributed consciousness
"""

import ray
import time
import logging
import psutil
import gc
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RayClusterManager:
    """Manages Ray cluster lifecycle with memory optimization"""
    
    def __init__(self):
        self.is_running = False
        self.start_time = None
        self.initial_memory = None
    
    def start_cluster(self, 
                     num_cpus: Optional[int] = None,
                     object_store_memory: int = 1024 * 1024 * 1024,  # 1GB
                     log_to_driver: bool = False) -> bool:
        """Start Ray cluster with memory optimization"""
        
        # Check if Ray is already running
        if ray.is_initialized():
            logger.warning("Ray cluster already running, shutting down first")
            self.shutdown_cluster()
        
        # Record initial memory usage
        process = psutil.Process()
        self.initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
        
        try:
            # Initialize Ray with memory constraints
            ray.init(
                num_cpus=num_cpus,
                object_store_memory=object_store_memory,
                log_to_driver=log_to_driver,
                _redis_max_memory=512 * 1024 * 1024,  # 512MB Redis limit
                _plasma_directory="/tmp",  # Use temp for plasma store
                _enable_object_reconstruction=False,  # Reduce memory overhead
                ignore_reinit_error=True
            )
            
            self.is_running = True
            self.start_time = time.time()
            
            logger.info(f"✅ Ray cluster started")
            logger.info(f"   Object store memory: {object_store_memory // (1024*1024)}MB")
            logger.info(f"   Initial system memory: {self.initial_memory:.1f}MB")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Ray cluster: {e}")
            return False
    
    def shutdown_cluster(self, force_cleanup: bool = True) -> bool:
        """Shutdown Ray cluster with thorough cleanup"""
        
        if not ray.is_initialized():
            logger.info("Ray cluster not running")
            return True
        
        try:
            # Get memory usage before shutdown
            process = psutil.Process()
            pre_shutdown_memory = process.memory_info().rss / (1024 * 1024)  # MB
            
            # Shutdown Ray
            ray.shutdown()
            
            if force_cleanup:
                # Force garbage collection
                for _ in range(3):
                    gc.collect()
                
                # Wait for cleanup
                time.sleep(2)
            
            # Check memory usage after shutdown
            post_shutdown_memory = process.memory_info().rss / (1024 * 1024)  # MB
            memory_freed = pre_shutdown_memory - post_shutdown_memory
            
            self.is_running = False
            uptime = time.time() - self.start_time if self.start_time else 0
            
            logger.info(f"✅ Ray cluster shutdown completed")
            logger.info(f"   Cluster uptime: {uptime:.1f} seconds")
            logger.info(f"   Memory freed: {memory_freed:.1f}MB")
            logger.info(f"   Final memory usage: {post_shutdown_memory:.1f}MB")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during Ray shutdown: {e}")
            return False
    
    def restart_cluster(self, **kwargs) -> bool:
        """Restart Ray cluster with memory cleanup"""
        
        logger.info("🔄 Restarting Ray cluster...")
        
        # Shutdown existing cluster
        if not self.shutdown_cluster(force_cleanup=True):
            logger.error("Failed to shutdown existing cluster")
            return False
        
        # Wait for complete cleanup
        time.sleep(3)
        
        # Start new cluster
        return self.start_cluster(**kwargs)
    
    def get_memory_status(self) -> dict:
        """Get current memory status"""
        
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'ray_running': ray.is_initialized() if self.is_running else False,
            'system_memory_mb': memory_info.rss / (1024 * 1024),
            'virtual_memory_mb': memory_info.vms / (1024 * 1024),
            'initial_memory_mb': self.initial_memory,
            'memory_growth_mb': (memory_info.rss / (1024 * 1024)) - (self.initial_memory or 0),
            'uptime_seconds': time.time() - self.start_time if self.start_time else 0
        }
    
    def check_memory_pressure(self, threshold_mb: int = 6000) -> bool:
        """Check if system is under memory pressure"""
        
        process = psutil.Process()
        current_memory_mb = process.memory_info().rss / (1024 * 1024)
        
        return current_memory_mb > threshold_mb


# Global cluster manager instance
_cluster_manager: Optional[RayClusterManager] = None


def get_cluster_manager() -> RayClusterManager:
    """Get the global cluster manager instance"""
    global _cluster_manager
    
    if _cluster_manager is None:
        _cluster_manager = RayClusterManager()
    
    return _cluster_manager


def safe_ray_operation(operation_func):
    """Decorator to ensure Ray operations are memory-safe"""
    def wrapper(*args, **kwargs):
        manager = get_cluster_manager()
        
        # Check memory pressure before operation
        if manager.check_memory_pressure():
            logger.warning("High memory pressure detected, restarting Ray cluster")
            manager.restart_cluster()
        
        try:
            return operation_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Ray operation failed: {e}")
            # Restart cluster on critical errors
            manager.restart_cluster()
            raise
    
    return wrapper


if __name__ == "__main__":
    # Test the cluster manager
    manager = RayClusterManager()
    
    print("Testing Ray Cluster Manager")
    print("=" * 40)
    
    # Start cluster
    if manager.start_cluster(num_cpus=4, object_store_memory=512*1024*1024):
        
        # Show status
        status = manager.get_memory_status()
        print(f"Ray running: {status['ray_running']}")
        print(f"Memory usage: {status['system_memory_mb']:.1f}MB")
        print(f"Memory growth: {status['memory_growth_mb']:.1f}MB")
        
        # Test restart
        time.sleep(2)
        manager.restart_cluster(num_cpus=4, object_store_memory=512*1024*1024)
        
        # Final status
        final_status = manager.get_memory_status()
        print(f"After restart memory: {final_status['system_memory_mb']:.1f}MB")
        
        # Shutdown
        manager.shutdown_cluster()
        
        print("✅ Ray Cluster Manager test completed")
    else:
        print("❌ Failed to start Ray cluster")