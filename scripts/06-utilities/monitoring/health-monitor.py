#!/usr/bin/env python3
"""
SynOS Automated Health Monitoring System
Comprehensive health checks for consciousness infrastructure
"""

import json
import time
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class HealthMonitor:
    def __init__(self):
        self.logger = logging.getLogger("synos.health")
        self.health_data_path = Path("/app/monitoring/health")
        self.health_data_path.mkdir(parents=True, exist_ok=True)
        
        # Health check endpoints
        self.endpoints = {
            "consciousness_api": "http://localhost:9090/health",
            "security_api": "http://localhost:8080/health",
            "database": "http://localhost:5432",
            "cache": "http://localhost:6379"
        }
    
    def check_consciousness_health(self) -> Dict:
        """Check consciousness engine health"""
        try:
            response = requests.get(self.endpoints["consciousness_api"], timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "details": data,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def check_system_health(self) -> Dict:
        """Check overall system health"""
        health_checks = {
            "consciousness": self.check_consciousness_health(),
            "system_resources": self.check_system_resources(),
            "network_connectivity": self.check_network_connectivity(),
            "storage_health": self.check_storage_health()
        }
        
        # Determine overall health
        overall_status = "healthy"
        for service, health in health_checks.items():
            if health.get("status") != "healthy":
                overall_status = "degraded" if overall_status == "healthy" else "critical"
        
        return {
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "services": health_checks
        }
    
    def check_system_resources(self) -> Dict:
        """Check system resource health"""
        import psutil
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine health based on thresholds
            status = "healthy"
            if cpu_percent > 90 or memory.percent > 90 or (disk.used / disk.total) > 0.95:
                status = "critical"
            elif cpu_percent > 75 or memory.percent > 80 or (disk.used / disk.total) > 0.85:
                status = "warning"
            
            return {
                "status": status,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": round((disk.used / disk.total) * 100, 2),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def check_network_connectivity(self) -> Dict:
        """Check network connectivity"""
        try:
            # Simple connectivity test
            response = requests.get("http://httpbin.org/status/200", timeout=5)
            
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def check_storage_health(self) -> Dict:
        """Check storage health"""
        try:
            import psutil
            
            disk = psutil.disk_usage('/')
            
            status = "healthy"
            if (disk.used / disk.total) > 0.95:
                status = "critical"
            elif (disk.used / disk.total) > 0.85:
                status = "warning"
            
            return {
                "status": status,
                "total_gb": round(disk.total / 1024**3, 2),
                "used_gb": round(disk.used / 1024**3, 2),
                "free_gb": round(disk.free / 1024**3, 2),
                "usage_percent": round((disk.used / disk.total) * 100, 2),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def save_health_report(self, health_data: Dict):
        """Save health report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.health_data_path / f"health_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(health_data, f, indent=2)
    
    def generate_health_summary(self) -> Dict:
        """Generate health summary for the last 24 hours"""
        # This would analyze health data from the last 24 hours
        # For now, return current health status
        return self.check_system_health()

if __name__ == "__main__":
    monitor = HealthMonitor()
    
    # Continuous health monitoring
    while True:
        health_data = monitor.check_system_health()
        monitor.save_health_report(health_data)
        
        print(f"[{datetime.now()}] Health Status: {health_data['overall_status']}")
        print(json.dumps(health_data, indent=2))
        
        # Alert on critical issues
        if health_data['overall_status'] == 'critical':
            print("🚨 CRITICAL HEALTH ISSUE DETECTED 🚨")
        
        time.sleep(60)  # Check every minute
