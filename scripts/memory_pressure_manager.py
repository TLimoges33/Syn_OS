#!/usr/bin/env python3
"""
Memory Pressure Manager - User-space memory overflow protection
Alternative to system swap for better memory management
"""

import os
import time
import psutil
import logging
import threading
import gc
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import deque
import pickle
import zlib
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MemoryPressureConfig:
    """Configuration for memory pressure management"""
    # Memory thresholds
    warning_threshold: float = 0.75  # 75% memory usage
    critical_threshold: float = 0.85  # 85% memory usage
    emergency_threshold: float = 0.95  # 95% memory usage
    
    # Swap simulation
    virtual_swap_dir: str = "/tmp/synapticos_virtual_swap"
    virtual_swap_size_mb: int = 2048  # 2GB virtual swap
    
    # Monitoring
    check_interval: float = 5.0  # seconds
    enable_compression: bool = True
    
    # Process management
    process_kill_threshold: float = 0.92  # Kill processes at 92%
    protected_processes: List[str] = None


class VirtualSwapManager:
    """User-space virtual swap implementation"""
    
    def __init__(self, config: MemoryPressureConfig):
        self.config = config
        self.swap_dir = Path(config.virtual_swap_dir)
        self.swap_dir.mkdir(exist_ok=True)
        
        # Swap tracking
        self.swapped_objects: Dict[str, str] = {}  # object_id -> file_path
        self.object_metadata: Dict[str, Dict] = {}
        self.swap_counter = 0
        
        logger.info(f"Virtual swap initialized: {config.virtual_swap_dir}")
    
    def swap_out_object(self, obj_id: str, obj_data: any) -> bool:
        """Swap object to disk storage"""
        try:
            # Serialize and optionally compress
            serialized_data = pickle.dumps(obj_data)
            
            if self.config.enable_compression:
                compressed_data = zlib.compress(serialized_data)
                if len(compressed_data) < len(serialized_data) * 0.8:
                    serialized_data = compressed_data
                    compressed = True
                else:
                    compressed = False
            else:
                compressed = False
            
            # Write to swap file
            swap_file = self.swap_dir / f"swap_{self.swap_counter}.dat"
            self.swap_counter += 1
            
            with open(swap_file, 'wb') as f:
                f.write(serialized_data)
            
            # Track metadata
            self.swapped_objects[obj_id] = str(swap_file)
            self.object_metadata[obj_id] = {
                'file_path': str(swap_file),
                'original_size': len(pickle.dumps(obj_data)),
                'compressed_size': len(serialized_data),
                'compressed': compressed,
                'swap_time': time.time()
            }
            
            logger.debug(f"Swapped object {obj_id} to {swap_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to swap object {obj_id}: {e}")
            return False
    
    def swap_in_object(self, obj_id: str) -> Optional[any]:
        """Swap object back from disk storage"""
        try:
            if obj_id not in self.swapped_objects:
                return None
            
            swap_file = Path(self.swapped_objects[obj_id])
            metadata = self.object_metadata[obj_id]
            
            # Read from swap file
            with open(swap_file, 'rb') as f:
                serialized_data = f.read()
            
            # Decompress if needed
            if metadata['compressed']:
                try:
                    serialized_data = zlib.decompress(serialized_data)
                except Exception:
                    pass  # Data might not be compressed
            
            # Deserialize
            obj_data = pickle.loads(serialized_data)
            
            # Cleanup
            swap_file.unlink(missing_ok=True)
            del self.swapped_objects[obj_id]
            del self.object_metadata[obj_id]
            
            logger.debug(f"Swapped in object {obj_id}")
            return obj_data
            
        except Exception as e:
            logger.error(f"Failed to swap in object {obj_id}: {e}")
            return None
    
    def cleanup_swap_files(self):
        """Clean up all swap files"""
        try:
            for swap_file in self.swap_dir.glob("swap_*.dat"):
                swap_file.unlink(missing_ok=True)
            
            self.swapped_objects.clear()
            self.object_metadata.clear()
            
            logger.info("Virtual swap cleanup completed")
            
        except Exception as e:
            logger.error(f"Swap cleanup failed: {e}")
    
    def get_swap_stats(self) -> Dict:
        """Get swap usage statistics"""
        total_swapped = len(self.swapped_objects)
        total_size = sum(
            meta['compressed_size'] for meta in self.object_metadata.values()
        )
        
        return {
            'objects_swapped': total_swapped,
            'total_swap_size_mb': total_size / (1024 * 1024),
            'compression_ratio': sum(
                meta['compressed_size'] / meta['original_size']
                for meta in self.object_metadata.values()
            ) / max(total_swapped, 1)
        }


class MemoryPressureManager:
    """Comprehensive memory pressure management system"""
    
    def __init__(self, config: MemoryPressureConfig = None):
        self.config = config or MemoryPressureConfig()
        self.virtual_swap = VirtualSwapManager(self.config)
        
        # Monitoring state
        self.monitoring_active = True
        self.memory_history = deque(maxlen=100)
        self.pressure_events = deque(maxlen=50)
        
        # Actions taken
        self.gc_collections = 0
        self.processes_killed = 0
        self.objects_swapped = 0
        
        # Start monitoring
        self.monitor_thread = threading.Thread(target=self._monitor_memory, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Memory Pressure Manager initialized")
    
    def _monitor_memory(self):
        """Background memory monitoring"""
        while self.monitoring_active:
            try:
                # Get memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent / 100.0
                
                # Record history
                self.memory_history.append({
                    'timestamp': time.time(),
                    'usage_percent': memory_percent,
                    'available_mb': memory.available / (1024 * 1024),
                    'used_mb': memory.used / (1024 * 1024)
                })
                
                # Check thresholds and take actions
                if memory_percent >= self.config.emergency_threshold:
                    self._handle_emergency_pressure(memory_percent)
                elif memory_percent >= self.config.critical_threshold:
                    self._handle_critical_pressure(memory_percent)
                elif memory_percent >= self.config.warning_threshold:
                    self._handle_warning_pressure(memory_percent)
                
                # Sleep until next check
                time.sleep(self.config.check_interval)
                
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
                time.sleep(self.config.check_interval * 2)
    
    def _handle_warning_pressure(self, memory_percent: float):
        """Handle warning level memory pressure"""
        logger.info(f"Memory pressure warning: {memory_percent*100:.1f}% usage")
        
        # Gentle garbage collection
        collected = gc.collect()
        self.gc_collections += 1
        
        if collected > 0:
            logger.info(f"GC collected {collected} objects")
    
    def _handle_critical_pressure(self, memory_percent: float):
        """Handle critical level memory pressure"""
        logger.warning(f"Critical memory pressure: {memory_percent*100:.1f}% usage")
        
        self.pressure_events.append({
            'timestamp': time.time(),
            'level': 'critical',
            'memory_percent': memory_percent
        })
        
        # Aggressive garbage collection
        for generation in range(3):
            collected = gc.collect(generation)
            self.gc_collections += 1
            
        # Clear Python object caches
        try:
            import sys
            sys.intern.clear() if hasattr(sys.intern, 'clear') else None
        except:
            pass
        
        logger.info("Aggressive memory cleanup completed")
    
    def _handle_emergency_pressure(self, memory_percent: float):
        """Handle emergency level memory pressure"""
        logger.critical(f"EMERGENCY memory pressure: {memory_percent*100:.1f}% usage")
        
        self.pressure_events.append({
            'timestamp': time.time(),
            'level': 'emergency',
            'memory_percent': memory_percent
        })
        
        # Emergency actions
        self._emergency_cleanup()
        
        # Consider killing high-memory processes
        if memory_percent >= self.config.process_kill_threshold:
            self._kill_high_memory_processes()
    
    def _emergency_cleanup(self):
        """Emergency memory cleanup procedures"""
        # Full garbage collection
        for _ in range(5):
            collected = gc.collect()
            self.gc_collections += 1
        
        # Clear all possible caches
        try:
            # Clear import cache
            if hasattr(sys, 'modules'):
                modules_to_clear = [
                    mod for name, mod in sys.modules.items()
                    if name.startswith('ray') or name.startswith('numpy')
                ]
                for mod in modules_to_clear:
                    if hasattr(mod, '__dict__'):
                        mod.__dict__.clear()
        except:
            pass
        
        logger.critical("Emergency memory cleanup completed")
    
    def _kill_high_memory_processes(self):
        """Kill high-memory consuming processes as last resort"""
        try:
            # Get processes sorted by memory usage
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by memory usage (highest first)
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            
            protected = set(self.config.protected_processes or ['systemd', 'kernel', 'claude'])
            
            # Kill top memory consuming processes
            killed_count = 0
            for proc_info in processes[:3]:  # Top 3 consumers
                if proc_info['name'] not in protected and proc_info['memory_percent'] > 5.0:
                    try:
                        proc = psutil.Process(proc_info['pid'])
                        proc.terminate()
                        killed_count += 1
                        logger.warning(f"Terminated process: {proc_info['name']} (PID: {proc_info['pid']})")
                        
                        if killed_count >= 2:  # Limit kills
                            break
                            
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            
            self.processes_killed += killed_count
            
        except Exception as e:
            logger.error(f"Process termination failed: {e}")
    
    def get_memory_report(self) -> Dict:
        """Get comprehensive memory status report"""
        # Current memory status
        memory = psutil.virtual_memory()
        
        # Calculate trends
        if len(self.memory_history) >= 2:
            recent_usage = [h['usage_percent'] for h in list(self.memory_history)[-10:]]
            memory_trend = (recent_usage[-1] - recent_usage[0]) if len(recent_usage) > 1 else 0
        else:
            memory_trend = 0
        
        # Pressure event summary
        recent_events = [
            e for e in self.pressure_events
            if time.time() - e['timestamp'] < 300  # Last 5 minutes
        ]
        
        return {
            'current_memory': {
                'usage_percent': memory.percent,
                'available_mb': memory.available / (1024 * 1024),
                'used_mb': memory.used / (1024 * 1024),
                'trend_percent': memory_trend * 100
            },
            'thresholds': {
                'warning': self.config.warning_threshold * 100,
                'critical': self.config.critical_threshold * 100,
                'emergency': self.config.emergency_threshold * 100
            },
            'actions_taken': {
                'gc_collections': self.gc_collections,
                'processes_killed': self.processes_killed,
                'objects_swapped': self.objects_swapped
            },
            'virtual_swap': self.virtual_swap.get_swap_stats(),
            'recent_pressure_events': len(recent_events),
            'monitoring_active': self.monitoring_active
        }
    
    def shutdown(self):
        """Shutdown memory pressure manager"""
        logger.info("Shutting down Memory Pressure Manager")
        
        self.monitoring_active = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
        
        self.virtual_swap.cleanup_swap_files()
        logger.info("Memory Pressure Manager shutdown complete")


# Global instance
_memory_pressure_manager: Optional[MemoryPressureManager] = None


def get_memory_pressure_manager() -> MemoryPressureManager:
    """Get global memory pressure manager instance"""
    global _memory_pressure_manager
    
    if _memory_pressure_manager is None:
        _memory_pressure_manager = MemoryPressureManager()
    
    return _memory_pressure_manager


if __name__ == "__main__":
    # Test memory pressure manager
    print("Testing Memory Pressure Manager")
    print("=" * 40)
    
    manager = MemoryPressureManager()
    
    try:
        # Show initial status
        report = manager.get_memory_report()
        print(f"Current memory usage: {report['current_memory']['usage_percent']:.1f}%")
        print(f"Available memory: {report['current_memory']['available_mb']:.1f}MB")
        
        # Run for 30 seconds
        print("Monitoring memory for 30 seconds...")
        time.sleep(30)
        
        # Final report
        final_report = manager.get_memory_report()
        print("\nFinal Report:")
        print(f"GC collections: {final_report['actions_taken']['gc_collections']}")
        print(f"Pressure events: {final_report['recent_pressure_events']}")
        print(f"Memory trend: {final_report['current_memory']['trend_percent']:+.2f}%")
        
        print("✅ Memory Pressure Manager test completed")
        
    finally:
        manager.shutdown()