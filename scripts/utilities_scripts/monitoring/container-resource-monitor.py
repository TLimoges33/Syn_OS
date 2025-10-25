#!/usr/bin/env python3
"""
SynOS Container Resource Monitor - Production Optimization
Real-time monitoring without Docker API dependency
"""

import json
import psutil
import time
import logging
from datetime import datetime
from typing import Dict, List
from pathlib import Path

class ContainerResourceMonitor:
    def __init__(self):
        self.logger = logging.getLogger("synos.monitor")
        self.data_path = Path("/app/monitoring/data")
        self.data_path.mkdir(parents=True, exist_ok=True)
        
    def get_system_stats(self) -> Dict:
        """Get system resource statistics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network = psutil.net_io_counters()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'per_cpu': psutil.cpu_percent(percpu=True)
                },
                'memory': {
                    'total_gb': round(memory.total / 1024**3, 2),
                    'available_gb': round(memory.available / 1024**3, 2),
                    'used_gb': round(memory.used / 1024**3, 2),
                    'percent': memory.percent
                },
                'disk': {
                    'total_gb': round(disk.total / 1024**3, 2),
                    'used_gb': round(disk.used / 1024**3, 2),
                    'free_gb': round(disk.free / 1024**3, 2),
                    'percent': round((disk.used / disk.total) * 100, 2)
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting system stats: {e}")
            return {}
    
    def monitor_consciousness_processes(self) -> List[Dict]:
        """Monitor consciousness-related processes"""
        consciousness_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'cmdline']):
            try:
                if any(keyword in str(proc.info['cmdline']) for keyword in ['consciousness', 'synos', 'neural']):
                    consciousness_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_mb': round(proc.info['memory_info'].rss / 1024 / 1024, 2),
                        'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return consciousness_processes
    
    def check_resource_thresholds(self, stats: Dict) -> List[Dict]:
        """Check for resource threshold violations"""
        alerts = []
        thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0
        }
        
        if stats.get('cpu', {}).get('percent', 0) > thresholds['cpu_percent']:
            alerts.append({
                'metric': 'cpu_percent',
                'value': stats['cpu']['percent'],
                'threshold': thresholds['cpu_percent'],
                'severity': 'warning',
                'timestamp': stats['timestamp']
            })
        
        if stats.get('memory', {}).get('percent', 0) > thresholds['memory_percent']:
            alerts.append({
                'metric': 'memory_percent',
                'value': stats['memory']['percent'],
                'threshold': thresholds['memory_percent'],
                'severity': 'critical',
                'timestamp': stats['timestamp']
            })
        
        if stats.get('disk', {}).get('percent', 0) > thresholds['disk_percent']:
            alerts.append({
                'metric': 'disk_percent',
                'value': stats['disk']['percent'],
                'threshold': thresholds['disk_percent'],
                'severity': 'critical',
                'timestamp': stats['timestamp']
            })
        
        return alerts
    
    def save_metrics(self, stats: Dict, processes: List[Dict]):
        """Save metrics to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metrics_file = self.data_path / f"metrics_{timestamp}.json"
        
        data = {
            'system_stats': stats,
            'consciousness_processes': processes,
            'timestamp': timestamp
        }
        
        with open(metrics_file, 'w') as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    monitor = ContainerResourceMonitor()
    
    # Monitor continuously
    while True:
        stats = monitor.get_system_stats()
        processes = monitor.monitor_consciousness_processes()
        alerts = monitor.check_resource_thresholds(stats)
        
        # Save metrics
        monitor.save_metrics(stats, processes)
        
        # Log stats and alerts
        print(f"[{datetime.now()}] System Stats:")
        print(json.dumps(stats, indent=2))
        
        if processes:
            print("Consciousness Processes:")
            print(json.dumps(processes, indent=2))
        
        if alerts:
            print("ALERTS:")
            print(json.dumps(alerts, indent=2))
        
        time.sleep(30)  # Monitor every 30 seconds
