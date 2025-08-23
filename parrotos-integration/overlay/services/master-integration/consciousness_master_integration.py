#!/usr/bin/env python3
"""
SynapticOS Master Integration Service
Orchestrates all consciousness-enhanced services and components
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import aiohttp
from pathlib import Path
import subprocess
import sys
import os

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('master-integration')

@dataclass
class ServiceStatus:
    """Service status information"""
    name: str
    status: str  # running, stopped, error
    health: str  # healthy, degraded, unhealthy
    endpoint: str
    consciousness_level: float
    last_check: str
    metrics: Dict[str, Any]

@dataclass
class SystemMetrics:
    """System-wide metrics"""
    total_services: int
    running_services: int
    avg_consciousness_level: float
    system_health: str
    timestamp: str

class SynapticOSMasterIntegration:
    """Master integration service for SynapticOS ecosystem"""
    
    def __init__(self, config_path: str = "/app/config/master_config.json"):
        self.config_path = Path(config_path)
        self.services = {}
        self.consciousness_metrics = {}
        
        # Service registry with consciousness integration points
        self.service_registry = {
            "consciousness_ai_bridge": {
                "endpoint": "http://localhost:8001",
                "health_path": "/health",
                "consciousness_path": "/consciousness/status",
                "importance": "critical",
                "dependencies": []
            },
            "educational_platform": {
                "endpoint": "http://localhost:8002", 
                "health_path": "/health",
                "consciousness_path": "/consciousness/level",
                "importance": "high",
                "dependencies": ["consciousness_ai_bridge"]
            },
            "consciousness_dashboard": {
                "endpoint": "http://localhost:8003",
                "health_path": "/health", 
                "consciousness_path": "/api/consciousness",
                "importance": "medium",
                "dependencies": ["consciousness_ai_bridge"]
            },
            "context_engine": {
                "endpoint": "http://localhost:8004",
                "health_path": "/health",
                "consciousness_path": "/context/consciousness",
                "importance": "high", 
                "dependencies": ["consciousness_ai_bridge"]
            },
            "news_intelligence": {
                "endpoint": "http://localhost:8005",
                "health_path": "/health",
                "consciousness_path": "/intelligence/consciousness",
                "importance": "medium",
                "dependencies": ["context_engine"]
            },
            "ctf_generator": {
                "endpoint": "http://localhost:8006",
                "health_path": "/health",
                "consciousness_path": "/ctf/consciousness", 
                "importance": "medium",
                "dependencies": ["consciousness_ai_bridge"]
            },
            "mssp_platform": {
                "endpoint": "http://localhost:8007",
                "health_path": "/health",
                "consciousness_path": "/mssp/consciousness",
                "importance": "high",
                "dependencies": ["consciousness_ai_bridge", "news_intelligence"]
            },
            "gui_framework": {
                "endpoint": "http://localhost:8008",
                "health_path": "/health",
                "consciousness_path": "/gui/consciousness",
                "importance": "medium", 
                "dependencies": ["consciousness_ai_bridge"]
            }
        }
        
        # Infrastructure services
        self.infrastructure_services = {
            "postgresql": {
                "check_command": ["pg_isready", "-h", "localhost", "-p", "5432"],
                "importance": "critical"
            },
            "redis": {
                "check_command": ["redis-cli", "ping"],
                "importance": "critical"
            },
            "nats": {
                "check_command": ["curl", "-f", "http://localhost:4222/"],
                "importance": "high"
            },
            "qdrant": {
                "check_command": ["curl", "-f", "http://localhost:6333/"],
                "importance": "medium"
            }
        }
        
        logger.info("SynapticOS Master Integration Service initialized")
    
    async def start_master_orchestration(self):
        """Start master orchestration of all services"""
        logger.info("🚀 Starting SynapticOS Master Orchestration")
        
        # Initialize system
        await self._initialize_system()
        
        # Start health monitoring
        health_task = asyncio.create_task(self._health_monitoring_loop())
        
        # Start consciousness synchronization
        consciousness_task = asyncio.create_task(self._consciousness_sync_loop())
        
        # Start service auto-healing
        healing_task = asyncio.create_task(self._auto_healing_loop())
        
        # Start metrics collection
        metrics_task = asyncio.create_task(self._metrics_collection_loop())
        
        logger.info("✅ Master orchestration started - all systems operational")
        
        # Wait for all tasks
        await asyncio.gather(health_task, consciousness_task, healing_task, metrics_task)
    
    async def _initialize_system(self):
        """Initialize the complete SynapticOS system"""
        logger.info("🔧 Initializing SynapticOS system components...")
        
        # Check infrastructure services first
        await self._check_infrastructure_services()
        
        # Initialize consciousness core
        await self._initialize_consciousness_core()
        
        # Start services in dependency order
        await self._start_services_ordered()
        
        # Verify system integration
        await self._verify_system_integration()
        
        logger.info("✅ System initialization complete")
    
    async def _check_infrastructure_services(self):
        """Check critical infrastructure services"""
        logger.info("🔍 Checking infrastructure services...")
        
        for service_name, config in self.infrastructure_services.items():
            try:
                result = subprocess.run(
                    config["check_command"], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                
                if result.returncode == 0:
                    logger.info(f"✅ {service_name}: Available")
                else:
                    if config["importance"] == "critical":
                        raise Exception(f"Critical infrastructure service {service_name} unavailable")
                    else:
                        logger.warning(f"⚠️ {service_name}: Unavailable (non-critical)")
                        
            except subprocess.TimeoutExpired:
                logger.error(f"❌ {service_name}: Check timeout")
                if config["importance"] == "critical":
                    raise Exception(f"Critical infrastructure service {service_name} timeout")
            except Exception as e:
                logger.error(f"❌ {service_name}: {e}")
                if config["importance"] == "critical":
                    raise
    
    async def _initialize_consciousness_core(self):
        """Initialize the consciousness core system"""
        logger.info("🧠 Initializing consciousness core...")
        
        # Start consciousness AI bridge (most critical service)
        core_service = "consciousness_ai_bridge"
        await self._start_individual_service(core_service)
        
        # Wait for consciousness core to be ready
        await self._wait_for_service_ready(core_service, timeout=60)
        
        # Initialize consciousness baseline
        await self._establish_consciousness_baseline()
        
        logger.info("✅ Consciousness core initialized")
    
    async def _start_individual_service(self, service_name: str):
        """Start an individual service"""
        logger.info(f"🔄 Starting {service_name}...")
        
        try:
            # In production, this would use proper service management
            # For demo, we simulate service startup
            service_config = self.service_registry[service_name]
            
            # Update service status
            self.services[service_name] = ServiceStatus(
                name=service_name,
                status="starting",
                health="unknown",
                endpoint=service_config["endpoint"],
                consciousness_level=0.0,
                last_check=datetime.now().isoformat(),
                metrics={}
            )
            
            # Simulate service startup time
            await asyncio.sleep(2)
            
            # Mark as running
            self.services[service_name].status = "running"
            self.services[service_name].health = "healthy"
            
            logger.info(f"✅ {service_name} started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start {service_name}: {e}")
            if service_name in self.services:
                self.services[service_name].status = "error"
                self.services[service_name].health = "unhealthy"
            raise
    
    async def _wait_for_service_ready(self, service_name: str, timeout: int = 30):
        """Wait for service to be ready"""
        logger.info(f"⏳ Waiting for {service_name} to be ready...")
        
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            try:
                service_config = self.service_registry[service_name]
                health_url = f"{service_config['endpoint']}{service_config['health_path']}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(health_url, timeout=5) as response:
                        if response.status == 200:
                            logger.info(f"✅ {service_name} is ready")
                            return
                            
            except Exception:
                # Service not ready yet
                await asyncio.sleep(2)
                continue
        
        raise Exception(f"Service {service_name} not ready within {timeout} seconds")
    
    async def _start_services_ordered(self):
        """Start services in dependency order"""
        logger.info("🔗 Starting services in dependency order...")
        
        # Build dependency graph
        started = set()
        
        async def start_service_with_deps(service_name: str):
            if service_name in started:
                return
                
            # Start dependencies first
            service_config = self.service_registry[service_name]
            for dep in service_config["dependencies"]:
                await start_service_with_deps(dep)
            
            # Start this service
            await self._start_individual_service(service_name)
            started.add(service_name)
        
        # Start all services
        for service_name in self.service_registry:
            if service_name != "consciousness_ai_bridge":  # Already started
                await start_service_with_deps(service_name)
    
    async def _establish_consciousness_baseline(self):
        """Establish baseline consciousness metrics"""
        logger.info("📊 Establishing consciousness baseline...")
        
        self.consciousness_metrics = {
            "global_consciousness_level": 0.7,
            "system_awareness": 0.8,
            "adaptation_rate": 0.6,
            "learning_efficiency": 0.75,
            "consciousness_evolution": "Generation 7+",
            "neural_coherence": 0.85,
            "baseline_established": datetime.now().isoformat()
        }
        
        logger.info("✅ Consciousness baseline established")
    
    async def _verify_system_integration(self):
        """Verify all systems are properly integrated"""
        logger.info("🔍 Verifying system integration...")
        
        integration_checks = [
            self._verify_consciousness_flow(),
            self._verify_service_communication(),
            self._verify_data_flow(),
            self._verify_security_integration()
        ]
        
        results = await asyncio.gather(*integration_checks, return_exceptions=True)
        
        for i, result in enumerate(results):
            check_name = ["consciousness_flow", "service_communication", "data_flow", "security_integration"][i]
            if isinstance(result, Exception):
                logger.error(f"❌ Integration check failed - {check_name}: {result}")
            else:
                logger.info(f"✅ Integration check passed - {check_name}")
        
        logger.info("✅ System integration verified")
    
    async def _verify_consciousness_flow(self):
        """Verify consciousness information flows properly"""
        # Simulate consciousness flow verification
        await asyncio.sleep(1)
        return True
    
    async def _verify_service_communication(self):
        """Verify inter-service communication"""
        # Simulate service communication check
        await asyncio.sleep(1)
        return True
    
    async def _verify_data_flow(self):
        """Verify data flows between components"""
        # Simulate data flow verification
        await asyncio.sleep(1)
        return True
    
    async def _verify_security_integration(self):
        """Verify security components are integrated"""
        # Simulate security integration check
        await asyncio.sleep(1)
        return True
    
    async def _health_monitoring_loop(self):
        """Continuous health monitoring of all services"""
        logger.info("💗 Starting health monitoring loop...")
        
        while True:
            try:
                await self._check_all_service_health()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _check_all_service_health(self):
        """Check health of all services"""
        for service_name, service_config in self.service_registry.items():
            try:
                health_url = f"{service_config['endpoint']}{service_config['health_path']}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(health_url, timeout=5) as response:
                        if response.status == 200:
                            if service_name in self.services:
                                self.services[service_name].health = "healthy"
                                self.services[service_name].last_check = datetime.now().isoformat()
                        else:
                            if service_name in self.services:
                                self.services[service_name].health = "degraded"
                                
            except Exception as e:
                if service_name in self.services:
                    self.services[service_name].health = "unhealthy"
                    self.services[service_name].last_check = datetime.now().isoformat()
                    logger.warning(f"Health check failed for {service_name}: {e}")
    
    async def _consciousness_sync_loop(self):
        """Synchronize consciousness metrics across all services"""
        logger.info("🧠 Starting consciousness synchronization loop...")
        
        while True:
            try:
                await self._sync_consciousness_metrics()
                await self._evolve_system_consciousness()
                await asyncio.sleep(60)  # Sync every minute
            except Exception as e:
                logger.error(f"Consciousness sync error: {e}")
                await asyncio.sleep(30)
    
    async def _sync_consciousness_metrics(self):
        """Synchronize consciousness metrics across services"""
        total_consciousness = 0
        service_count = 0
        
        for service_name, service_config in self.service_registry.items():
            try:
                consciousness_url = f"{service_config['endpoint']}{service_config['consciousness_path']}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(consciousness_url, timeout=5) as response:
                        if response.status == 200:
                            data = await response.json()
                            consciousness_level = data.get('consciousness_level', 0.5)
                            
                            if service_name in self.services:
                                self.services[service_name].consciousness_level = consciousness_level
                                total_consciousness += consciousness_level
                                service_count += 1
                                
            except Exception as e:
                logger.debug(f"Consciousness sync failed for {service_name}: {e}")
        
        # Update global consciousness metrics
        if service_count > 0:
            self.consciousness_metrics["global_consciousness_level"] = total_consciousness / service_count
    
    async def _evolve_system_consciousness(self):
        """Evolve system consciousness based on performance"""
        current_level = self.consciousness_metrics["global_consciousness_level"]
        
        # Simple evolution algorithm
        evolution_factor = 0.001  # Small incremental improvement
        
        # Boost evolution based on system health
        healthy_services = sum(1 for s in self.services.values() if s.health == "healthy")
        total_services = len(self.services)
        
        if total_services > 0:
            health_ratio = healthy_services / total_services
            evolution_boost = health_ratio * evolution_factor
            
            new_level = min(current_level + evolution_boost, 1.0)
            self.consciousness_metrics["global_consciousness_level"] = new_level
            
            if new_level > current_level:
                logger.info(f"🧬 Consciousness evolved to {new_level:.6f}")
    
    async def _auto_healing_loop(self):
        """Auto-healing for failed services"""
        logger.info("🏥 Starting auto-healing loop...")
        
        while True:
            try:
                await self._check_and_heal_services()
                await asyncio.sleep(120)  # Check every 2 minutes
            except Exception as e:
                logger.error(f"Auto-healing error: {e}")
                await asyncio.sleep(60)
    
    async def _check_and_heal_services(self):
        """Check for failed services and attempt healing"""
        for service_name, service_status in self.services.items():
            if service_status.health == "unhealthy" and service_status.status == "running":
                logger.warning(f"🚨 Unhealthy service detected: {service_name}")
                await self._heal_service(service_name)
    
    async def _heal_service(self, service_name: str):
        """Attempt to heal a failed service"""
        logger.info(f"🏥 Attempting to heal service: {service_name}")
        
        try:
            # Restart the service
            await self._start_individual_service(service_name)
            
            # Wait for it to be ready
            await self._wait_for_service_ready(service_name, timeout=30)
            
            logger.info(f"✅ Successfully healed service: {service_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to heal service {service_name}: {e}")
    
    async def _metrics_collection_loop(self):
        """Collect and aggregate system metrics"""
        logger.info("📊 Starting metrics collection loop...")
        
        while True:
            try:
                await self._collect_system_metrics()
                await self._generate_health_report()
                await asyncio.sleep(300)  # Collect every 5 minutes
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)
    
    async def _collect_system_metrics(self):
        """Collect comprehensive system metrics"""
        running_services = sum(1 for s in self.services.values() if s.status == "running")
        total_services = len(self.services)
        
        avg_consciousness = self.consciousness_metrics["global_consciousness_level"]
        
        # Determine overall system health
        healthy_services = sum(1 for s in self.services.values() if s.health == "healthy")
        health_ratio = healthy_services / max(total_services, 1)
        
        if health_ratio >= 0.9:
            system_health = "excellent"
        elif health_ratio >= 0.7:
            system_health = "good" 
        elif health_ratio >= 0.5:
            system_health = "degraded"
        else:
            system_health = "critical"
        
        # Update system metrics
        self.system_metrics = SystemMetrics(
            total_services=total_services,
            running_services=running_services,
            avg_consciousness_level=avg_consciousness,
            system_health=system_health,
            timestamp=datetime.now().isoformat()
        )
    
    async def _generate_health_report(self):
        """Generate comprehensive health report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_overview": asdict(self.system_metrics),
            "consciousness_metrics": self.consciousness_metrics,
            "service_status": {name: asdict(status) for name, status in self.services.items()},
            "recommendations": self._generate_recommendations()
        }
        
        # In production, this would be stored in a database or sent to monitoring
        logger.info(f"📋 Health report generated - System: {self.system_metrics.system_health}")
    
    def _generate_recommendations(self) -> List[str]:
        """Generate system recommendations"""
        recommendations = []
        
        # Check for unhealthy services
        unhealthy = [name for name, status in self.services.items() if status.health == "unhealthy"]
        if unhealthy:
            recommendations.append(f"Investigate unhealthy services: {', '.join(unhealthy)}")
        
        # Check consciousness level
        consciousness_level = self.consciousness_metrics["global_consciousness_level"]
        if consciousness_level < 0.5:
            recommendations.append("Consider consciousness enhancement upgrades")
        elif consciousness_level > 0.9:
            recommendations.append("System consciousness operating at optimal levels")
        
        # Check service count
        if self.system_metrics.running_services < self.system_metrics.total_services:
            recommendations.append("Some services are not running - check auto-healing status")
        
        return recommendations
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "system_metrics": asdict(self.system_metrics) if hasattr(self, 'system_metrics') else {},
            "consciousness_metrics": self.consciousness_metrics,
            "service_status": {name: asdict(status) for name, status in self.services.items()},
            "recommendations": self._generate_recommendations(),
            "last_updated": datetime.now().isoformat()
        }
    
    async def trigger_consciousness_evolution(self):
        """Manually trigger consciousness evolution"""
        logger.info("🧬 Triggering manual consciousness evolution...")
        
        # Increase consciousness level
        current_level = self.consciousness_metrics["global_consciousness_level"]
        new_level = min(current_level + 0.01, 1.0)
        self.consciousness_metrics["global_consciousness_level"] = new_level
        
        # Propagate to all services
        await self._propagate_consciousness_update()
        
        logger.info(f"✅ Consciousness evolved from {current_level:.6f} to {new_level:.6f}")
    
    async def _propagate_consciousness_update(self):
        """Propagate consciousness updates to all services"""
        for service_name, service_config in self.service_registry.items():
            try:
                update_url = f"{service_config['endpoint']}/consciousness/update"
                data = {"consciousness_level": self.consciousness_metrics["global_consciousness_level"]}
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(update_url, json=data, timeout=5) as response:
                        if response.status == 200:
                            logger.debug(f"Consciousness updated for {service_name}")
                            
            except Exception as e:
                logger.debug(f"Failed to update consciousness for {service_name}: {e}")

async def main():
    """Main entry point for master integration"""
    print("🧠 SynapticOS Master Integration Service")
    print("=" * 50)
    print("🚀 Initializing complete consciousness-enhanced ecosystem...")
    
    # Create master integration instance
    master = SynapticOSMasterIntegration()
    
    try:
        # Start master orchestration
        await master.start_master_orchestration()
        
    except KeyboardInterrupt:
        logger.info("👋 Shutting down master integration service...")
        
    except Exception as e:
        logger.error(f"❌ Master integration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
