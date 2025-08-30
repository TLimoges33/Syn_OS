#!/usr/bin/env python3
"""
Hybrid Deployment Resource Manager for Syn_OS
Provides intelligent resource allocation and management for bare metal, VM, and cloud deployments
"""

import asyncio
import logging
import time
import os
import psutil
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor
import subprocess

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    logging.warning("Docker not available. Install with: pip install docker")

try:
    import kubernetes
    from kubernetes import client, config
    K8S_AVAILABLE = True
except ImportError:
    K8S_AVAILABLE = False
    logging.warning("Kubernetes client not available. Install with: pip install kubernetes")

from src.consciousness_v2.consciousness_bus import ConsciousnessBus, ConsciousnessState
from src.hardware_acceleration.gpu_acceleration_engine import GPUAccelerationEngine
from src.hardware_security.tpm_security_engine import TPMSecurityEngine
from src.security.audit_logger import AuditLogger


class DeploymentType(Enum):
    """Types of deployment environments"""
    BARE_METAL = "bare_metal"
    VIRTUAL_MACHINE = "virtual_machine"
    DOCKER_CONTAINER = "docker_container"
    KUBERNETES_POD = "kubernetes_pod"
    CLOUD_INSTANCE = "cloud_instance"
    HYBRID = "hybrid"


class ResourceType(Enum):
    """Types of system resources"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    GPU = "gpu"
    TPM = "tpm"
    CONSCIOUSNESS = "consciousness"


class AllocationStrategy(Enum):
    """Resource allocation strategies"""
    BALANCED = "balanced"
    PERFORMANCE = "performance"
    EFFICIENCY = "efficiency"
    CONSCIOUSNESS_OPTIMIZED = "consciousness_optimized"
    SECURITY_FOCUSED = "security_focused"
    ADAPTIVE = "adaptive"


@dataclass
class ResourceSpec:
    """Resource specification"""
    resource_type: ResourceType
    total_capacity: float
    allocated: float
    available: float
    reserved: float
    unit: str
    priority: int = 5


@dataclass
class DeploymentEnvironment:
    """Deployment environment specification"""
    environment_id: str
    deployment_type: DeploymentType
    name: str
    description: str
    resources: Dict[ResourceType, ResourceSpec]
    capabilities: List[str]
    consciousness_compatible: bool
    security_level: int
    performance_score: float


@dataclass
class AllocationRequest:
    """Resource allocation request"""
    request_id: str
    requester: str
    resource_requirements: Dict[ResourceType, float]
    consciousness_level_required: float
    priority: int = 5
    duration: Optional[int] = None  # seconds
    deployment_preferences: List[DeploymentType] = None


@dataclass
class AllocationResult:
    """Resource allocation result"""
    request_id: str
    success: bool
    allocated_resources: Dict[ResourceType, float]
    deployment_environment: Optional[DeploymentEnvironment]
    allocation_time: float
    estimated_performance: float
    consciousness_compatibility: float
    error_message: Optional[str] = None


class HybridDeploymentManager:
    """
    Intelligent resource management for hybrid deployments
    Manages resources across bare metal, VM, and cloud environments
    """
    
    def __init__(self, consciousness_bus: ConsciousnessBus, 
                 gpu_engine: GPUAccelerationEngine, 
                 tpm_engine: TPMSecurityEngine):
        """Initialize hybrid deployment manager"""
        self.consciousness_bus = consciousness_bus
        self.gpu_engine = gpu_engine
        self.tpm_engine = tmp_engine
        self.audit_logger = AuditLogger()
        self.logger = logging.getLogger(__name__)
        
        # Deployment environments
        self.environments: Dict[str, DeploymentEnvironment] = {}
        self.active_allocations: Dict[str, AllocationResult] = {}
        
        # Resource monitoring
        self.resource_monitor_interval = 30  # seconds
        self.monitor_task: Optional[asyncio.Task] = None
        
        # Allocation strategy
        self.default_strategy = AllocationStrategy.CONSCIOUSNESS_OPTIMIZED
        
        # Performance tracking
        self.allocation_count = 0
        self.successful_allocations = 0
        self.total_allocation_time = 0.0
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.allocation_lock = threading.Lock()
        
        # Initialize manager
        asyncio.create_task(self._initialize_manager())
    
    async def _initialize_manager(self):
        """Initialize the deployment manager"""
        try:
            self.logger.info("Initializing hybrid deployment manager...")
            
            # Detect deployment environments
            await self._detect_environments()
            
            # Start resource monitoring
            self.monitor_task = asyncio.create_task(self._monitor_resources())
            
            self.logger.info(f"Initialized {len(self.environments)} deployment environments")
            
        except Exception as e:
            self.logger.error(f"Error initializing deployment manager: {e}")
    
    async def _detect_environments(self):
        """Detect available deployment environments"""
        try:
            # Detect bare metal environment
            await self._detect_bare_metal()
            
            # Detect virtual machine environment
            await self._detect_virtual_machine()
            
            # Detect Docker environment
            await self._detect_docker()
            
            # Detect Kubernetes environment
            await self._detect_kubernetes()
            
            # Detect cloud environment
            await self._detect_cloud()
            
        except Exception as e:
            self.logger.error(f"Error detecting environments: {e}")
    
    async def _detect_bare_metal(self):
        """Detect bare metal environment"""
        try:
            # Check if running on bare metal (simplified detection)
            is_bare_metal = not self._is_virtualized()
            
            if is_bare_metal:
                resources = await self._get_system_resources()
                
                environment = DeploymentEnvironment(
                    environment_id="bare_metal_primary",
                    deployment_type=DeploymentType.BARE_METAL,
                    name="Bare Metal Primary",
                    description="Primary bare metal deployment environment",
                    resources=resources,
                    capabilities=["full_hardware_access", "tpm", "gpu", "consciousness"],
                    consciousness_compatible=True,
                    security_level=10,
                    performance_score=10.0
                )
                
                self.environments[environment.environment_id] = environment
                self.logger.info("Detected bare metal environment")
                
        except Exception as e:
            self.logger.error(f"Error detecting bare metal: {e}")
    
    async def _detect_virtual_machine(self):
        """Detect virtual machine environment"""
        try:
            is_vm = self._is_virtualized()
            
            if is_vm:
                resources = await self._get_system_resources()
                
                # Adjust resources for VM limitations
                if ResourceType.GPU in resources:
                    resources[ResourceType.GPU].total_capacity *= 0.8  # VM GPU penalty
                if ResourceType.TPM in resources:
                    resources[ResourceType.TPM].total_capacity *= 0.5  # Limited TPM access
                
                environment = DeploymentEnvironment(
                    environment_id="vm_primary",
                    deployment_type=DeploymentType.VIRTUAL_MACHINE,
                    name="Virtual Machine Primary",
                    description="Primary virtual machine deployment environment",
                    resources=resources,
                    capabilities=["limited_hardware_access", "consciousness"],
                    consciousness_compatible=True,
                    security_level=7,
                    performance_score=7.0
                )
                
                self.environments[environment.environment_id] = environment
                self.logger.info("Detected virtual machine environment")
                
        except Exception as e:
            self.logger.error(f"Error detecting virtual machine: {e}")
    
    async def _detect_docker(self):
        """Detect Docker environment"""
        try:
            if DOCKER_AVAILABLE:
                try:
                    docker_client = docker.from_env()
                    docker_client.ping()
                    
                    # Get Docker system info
                    system_info = docker_client.info()
                    
                    # Create Docker environment
                    resources = {
                        ResourceType.CPU: ResourceSpec(
                            resource_type=ResourceType.CPU,
                            total_capacity=system_info.get('NCPU', 1),
                            allocated=0.0,
                            available=system_info.get('NCPU', 1),
                            reserved=0.0,
                            unit="cores"
                        ),
                        ResourceType.MEMORY: ResourceSpec(
                            resource_type=ResourceType.MEMORY,
                            total_capacity=system_info.get('MemTotal', 0) / (1024**3),
                            allocated=0.0,
                            available=system_info.get('MemTotal', 0) / (1024**3),
                            reserved=0.0,
                            unit="GB"
                        )
                    }
                    
                    environment = DeploymentEnvironment(
                        environment_id="docker_primary",
                        deployment_type=DeploymentType.DOCKER_CONTAINER,
                        name="Docker Primary",
                        description="Primary Docker container environment",
                        resources=resources,
                        capabilities=["containerized", "scalable", "consciousness"],
                        consciousness_compatible=True,
                        security_level=6,
                        performance_score=6.0
                    )
                    
                    self.environments[environment.environment_id] = environment
                    self.logger.info("Detected Docker environment")
                    
                except Exception as e:
                    self.logger.debug(f"Docker not available: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error detecting Docker: {e}")
    
    async def _detect_kubernetes(self):
        """Detect Kubernetes environment"""
        try:
            if K8S_AVAILABLE:
                try:
                    # Try to load Kubernetes config
                    config.load_incluster_config()  # For in-cluster
                except:
                    try:
                        config.load_kube_config()  # For local kubectl
                    except:
                        return  # No Kubernetes available
                
                # Create Kubernetes client
                v1 = client.CoreV1Api()
                
                # Get cluster info
                nodes = v1.list_node()
                
                if nodes.items:
                    # Calculate cluster resources
                    total_cpu = 0
                    total_memory = 0
                    
                    for node in nodes.items:
                        if node.status.capacity:
                            cpu_str = node.status.capacity.get('cpu', '0')
                            memory_str = node.status.capacity.get('memory', '0Ki')
                            
                            # Parse CPU (can be in millicores)
                            if 'm' in cpu_str:
                                total_cpu += int(cpu_str.replace('m', '')) / 1000.0
                            else:
                                total_cpu += int(cpu_str)
                            
                            # Parse memory
                            if 'Ki' in memory_str:
                                total_memory += int(memory_str.replace('Ki', '')) / (1024**2)
                            elif 'Mi' in memory_str:
                                total_memory += int(memory_str.replace('Mi', '')) / 1024
                            elif 'Gi' in memory_str:
                                total_memory += int(memory_str.replace('Gi', ''))
                    
                    resources = {
                        ResourceType.CPU: ResourceSpec(
                            resource_type=ResourceType.CPU,
                            total_capacity=total_cpu,
                            allocated=0.0,
                            available=total_cpu,
                            reserved=0.0,
                            unit="cores"
                        ),
                        ResourceType.MEMORY: ResourceSpec(
                            resource_type=ResourceType.MEMORY,
                            total_capacity=total_memory,
                            allocated=0.0,
                            available=total_memory,
                            reserved=0.0,
                            unit="GB"
                        )
                    }
                    
                    environment = DeploymentEnvironment(
                        environment_id="k8s_primary",
                        deployment_type=DeploymentType.KUBERNETES_POD,
                        name="Kubernetes Primary",
                        description="Primary Kubernetes cluster environment",
                        resources=resources,
                        capabilities=["orchestrated", "scalable", "resilient", "consciousness"],
                        consciousness_compatible=True,
                        security_level=8,
                        performance_score=8.0
                    )
                    
                    self.environments[environment.environment_id] = environment
                    self.logger.info(f"Detected Kubernetes environment with {len(nodes.items)} nodes")
                    
        except Exception as e:
            self.logger.error(f"Error detecting Kubernetes: {e}")
    
    async def _detect_cloud(self):
        """Detect cloud environment"""
        try:
            # Detect cloud provider (simplified)
            cloud_provider = None
            
            # Check for AWS
            try:
                result = subprocess.run(
                    ["curl", "-s", "--max-time", "2", "http://169.254.169.254/latest/meta-data/instance-id"],
                    capture_output=True, text=True
                )
                if result.returncode == 0 and result.stdout:
                    cloud_provider = "AWS"
            except:
                pass
            
            # Check for GCP
            if not cloud_provider:
                try:
                    result = subprocess.run(
                        ["curl", "-s", "--max-time", "2", "-H", "Metadata-Flavor: Google", 
                         "http://metadata.google.internal/computeMetadata/v1/instance/id"],
                        capture_output=True, text=True
                    )
                    if result.returncode == 0 and result.stdout:
                        cloud_provider = "GCP"
                except:
                    pass
            
            # Check for Azure
            if not cloud_provider:
                try:
                    result = subprocess.run(
                        ["curl", "-s", "--max-time", "2", "-H", "Metadata: true",
                         "http://169.254.169.254/metadata/instance/compute/vmId?api-version=2021-02-01&format=text"],
                        capture_output=True, text=True
                    )
                    if result.returncode == 0 and result.stdout:
                        cloud_provider = "Azure"
                except:
                    pass
            
            if cloud_provider:
                resources = await self._get_system_resources()
                
                environment = DeploymentEnvironment(
                    environment_id=f"cloud_{cloud_provider.lower()}",
                    deployment_type=DeploymentType.CLOUD_INSTANCE,
                    name=f"{cloud_provider} Cloud Instance",
                    description=f"Primary {cloud_provider} cloud deployment environment",
                    resources=resources,
                    capabilities=["cloud_native", "scalable", "managed", "consciousness"],
                    consciousness_compatible=True,
                    security_level=8,
                    performance_score=8.0
                )
                
                self.environments[environment.environment_id] = environment
                self.logger.info(f"Detected {cloud_provider} cloud environment")
                
        except Exception as e:
            self.logger.error(f"Error detecting cloud: {e}")
    
    def _is_virtualized(self) -> bool:
        """Check if running in a virtualized environment"""
        try:
            # Check for common virtualization indicators
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read().lower()
                if any(virt in cpuinfo for virt in ['vmware', 'virtualbox', 'kvm', 'xen', 'hyperv']):
                    return True
            
            # Check DMI information
            try:
                result = subprocess.run(['dmidecode', '-s', 'system-manufacturer'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    manufacturer = result.stdout.strip().lower()
                    if any(virt in manufacturer for virt in ['vmware', 'virtualbox', 'microsoft', 'xen']):
                        return True
            except:
                pass
            
            return False
            
        except:
            return False
    
    async def _get_system_resources(self) -> Dict[ResourceType, ResourceSpec]:
        """Get current system resource specifications"""
        resources = {}
        
        try:
            # CPU resources
            cpu_count = psutil.cpu_count(logical=True)
            resources[ResourceType.CPU] = ResourceSpec(
                resource_type=ResourceType.CPU,
                total_capacity=cpu_count,
                allocated=0.0,
                available=cpu_count,
                reserved=1.0,  # Reserve 1 core for system
                unit="cores"
            )
            
            # Memory resources
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            resources[ResourceType.MEMORY] = ResourceSpec(
                resource_type=ResourceType.MEMORY,
                total_capacity=memory_gb,
                allocated=0.0,
                available=memory_gb,
                reserved=1.0,  # Reserve 1GB for system
                unit="GB"
            )
            
            # Storage resources
            disk = psutil.disk_usage('/')
            storage_gb = disk.total / (1024**3)
            resources[ResourceType.STORAGE] = ResourceSpec(
                resource_type=ResourceType.STORAGE,
                total_capacity=storage_gb,
                allocated=disk.used / (1024**3),
                available=disk.free / (1024**3),
                reserved=5.0,  # Reserve 5GB for system
                unit="GB"
            )
            
            # Network resources (simplified)
            resources[ResourceType.NETWORK] = ResourceSpec(
                resource_type=ResourceType.NETWORK,
                total_capacity=1000.0,  # Assume 1Gbps
                allocated=0.0,
                available=1000.0,
                reserved=0.0,
                unit="Mbps"
            )
            
            # GPU resources
            gpu_devices = self.gpu_engine.get_device_status()
            if gpu_devices:
                gpu_memory = sum(device.get('memory_total', 0) for device in gpu_devices) / (1024**3)
                resources[ResourceType.GPU] = ResourceSpec(
                    resource_type=ResourceType.GPU,
                    total_capacity=gpu_memory,
                    allocated=0.0,
                    available=gpu_memory,
                    reserved=0.0,
                    unit="GB"
                )
            
            # TPM resources
            tpm_status = self.tpm_engine.get_tpm_status()
            if tpm_status.get('initialized', False):
                resources[ResourceType.TPM] = ResourceSpec(
                    resource_type=ResourceType.TPM,
                    total_capacity=1.0,
                    allocated=0.0,
                    available=1.0,
                    reserved=0.0,
                    unit="device"
                )
            
            # Consciousness resources (abstract)
            resources[ResourceType.CONSCIOUSNESS] = ResourceSpec(
                resource_type=ResourceType.CONSCIOUSNESS,
                total_capacity=1.0,
                allocated=0.0,
                available=1.0,
                reserved=0.0,
                unit="level"
            )
            
        except Exception as e:
            self.logger.error(f"Error getting system resources: {e}")
        
        return resources
    
    async def _monitor_resources(self):
        """Monitor resource usage across all environments"""
        while True:
            try:
                await asyncio.sleep(self.resource_monitor_interval)
                
                for environment in self.environments.values():
                    await self._update_environment_resources(environment)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error monitoring resources: {e}")
    
    async def _update_environment_resources(self, environment: DeploymentEnvironment):
        """Update resource usage for an environment"""
        try:
            if environment.deployment_type == DeploymentType.BARE_METAL:
                # Update bare metal resources
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                if ResourceType.CPU in environment.resources:
                    cpu_resource = environment.resources[ResourceType.CPU]
                    cpu_resource.allocated = (cpu_percent / 100.0) * cpu_resource.total_capacity
                    cpu_resource.available = cpu_resource.total_capacity - cpu_resource.allocated - cpu_resource.reserved
                
                if ResourceType.MEMORY in environment.resources:
                    memory_resource = environment.resources[ResourceType.MEMORY]
                    memory_resource.allocated = memory.used / (1024**3)
                    memory_resource.available = memory.available / (1024**3)
            
            # Update other environment types as needed
            
        except Exception as e:
            self.logger.error(f"Error updating environment resources: {e}")
    
    async def allocate_resources(self, request: AllocationRequest, 
                               strategy: AllocationStrategy = None) -> AllocationResult:
        """Allocate resources based on request and strategy"""
        
        start_time = time.time()
        self.allocation_count += 1
        
        if strategy is None:
            strategy = self.default_strategy
        
        try:
            with self.allocation_lock:
                # Get current consciousness state
                consciousness_state = await self.consciousness_bus.get_consciousness_state()
                current_consciousness = consciousness_state.overall_consciousness_level
                
                # Check consciousness level requirement
                if request.consciousness_level_required > current_consciousness:
                    return AllocationResult(
                        request_id=request.request_id,
                        success=False,
                        allocated_resources={},
                        deployment_environment=None,
                        allocation_time=time.time() - start_time,
                        estimated_performance=0.0,
                        consciousness_compatibility=0.0,
                        error_message=f"Insufficient consciousness level: {current_consciousness} < {request.consciousness_level_required}"
                    )
                
                # Select optimal environment
                selected_environment = self._select_environment(request, strategy, current_consciousness)
                
                if not selected_environment:
                    return AllocationResult(
                        request_id=request.request_id,
                        success=False,
                        allocated_resources={},
                        deployment_environment=None,
                        allocation_time=time.time() - start_time,
                        estimated_performance=0.0,
                        consciousness_compatibility=0.0,
                        error_message="No suitable environment found"
                    )
                
                # Perform allocation
                allocated_resources = self._perform_allocation(selected_environment, request)
                
                if not allocated_resources:
                    return AllocationResult(
                        request_id=request.request_id,
                        success=False,
                        allocated_resources={},
                        deployment_environment=selected_environment,
                        allocation_time=time.time() - start_time,
                        estimated_performance=0.0,
                        consciousness_compatibility=0.0,
                        error_message="Resource allocation failed"
                    )
                
                # Calculate performance metrics
                estimated_performance = self._estimate_performance(selected_environment, allocated_resources)
                consciousness_compatibility = self._calculate_consciousness_compatibility(
                    selected_environment, request.consciousness_level_required
                )
                
                allocation_time = time.time() - start_time
                
                # Create successful result
                result = AllocationResult(
                    request_id=request.request_id,
                    success=True,
                    allocated_resources=allocated_resources,
                    deployment_environment=selected_environment,
                    allocation_time=allocation_time,
                    estimated_performance=estimated_performance,
                    consciousness_compatibility=consciousness_compatibility
                )
                
                # Store active allocation
                self.active_allocations[request.request_id] = result
                
                # Update performance metrics
                self.successful_allocations += 1
                self.total_allocation_time += allocation_time
                
                # Log allocation
                await self.audit_logger.log_system_event(
                    event_type="resource_allocation",
                    details={
                        "request_id": request.request_id,
                        "requester": request.requester,
                        "environment": selected_environment.environment_id,
                        "strategy": strategy.value,
                        "allocated_resources": {k.value: v for k, v in allocated_resources.items()},
                        "allocation_time": allocation_time,
                        "consciousness_level": current_consciousness
                    }
                )
                
                return result
                
        except Exception as e:
            self.logger.error(f"Resource allocation error: {e}")
            return AllocationResult(
                request_id=request.request_id,
                success=False,
                allocated_resources={},
                deployment_environment=None,
                allocation_time=time.time() - start_time,
                estimated_performance=0.0,
                consciousness_compatibility=0.0,
                error_message=str(e)
            )
    
    def _select_environment(self, request: AllocationRequest, 
                          strategy: AllocationStrategy, 
                          consciousness_level: float) -> Optional[DeploymentEnvironment]:
        """Select optimal environment based on request and strategy"""
        
        suitable_environments = []
        
        for environment in self.environments.values():
            # Check deployment preferences
            if request.deployment_preferences:
                if environment.deployment_type not in request.deployment_preferences:
                    continue
            
            # Check consciousness compatibility
            if not environment.consciousness_compatible and request.consciousness_level_required > 0.5:
                continue
            
            # Check resource availability
            can_satisfy = True
            for resource_type, required_amount in request.resource_requirements.items():
                if resource_type not in environment.resources:
                    can_satisfy = False
                    break
                
                resource = environment.resources[resource_type]
                if resource.available < required_amount:
                    can_satisfy = False
                    break
            
            if can_satisfy:
                suitable_environments.append(environment)
        
        if not suitable_environments:
            return None
        
        # Select based on strategy
        if strategy == AllocationStrategy.PERFORMANCE:
            return max(suitable_environments, key=lambda e: e.performance_score)
        elif strategy == AllocationStrategy.SECURITY_FOCUSED:
            return max(suitable_environments, key=lambda e: e.security_level)
        elif strategy == AllocationStrategy.CONSCIOUSNESS_OPTIMIZED:
            return max(suitable_environments, key=lambda e: 
                      e.performance_score * (1.0 if e.consciousness_compatible else 0.5))
        elif strategy == AllocationStrategy.EFFICIENCY:
            # Select environment with least resource waste
            def efficiency_score(env):
                total_utilization = 0
                for resource in env.resources.values():
                    if resource.total_capacity > 0:
                        utilization = (resource.allocated + resource.reserved) / resource.total_capacity
                        total_utilization += utilization
                return total_utilization / len(env.resources)
            
            return max(suitable_environments, key=efficiency_score)
        else:  # BALANCED or ADAPTIVE
            # Weighted scoring
            def balanced_score(env):
                return (env.performance_score * 0.4 + 
                       env.security_level * 0.3 + 
                       (10.0 if env.consciousness_compatible else 5.0) * 0.3)
            
            return max(suitable_environments, key=balanced_score)
    
    def _perform_allocation(self, environment: DeploymentEnvironment, 
                          request: AllocationRequest) -> Optional[Dict[ResourceType, float]]:
        """Perform actual resource allocation"""
        
        allocated_resources = {}
        
        try:
            for resource_type, required_amount in request.resource_requirements.items():
                if resource_type not in environment.resources:
                    continue
                
                resource = environment.resources[resource_type]
                
                if resource.available >= required_amount:
                    # Allocate the resource
                    resource.allocated += required_amount
                    resource.available -= required_amount
                    allocated_resources[resource_type] = required_amount
                else:
                    # Allocation failed - rollback
                    for rollback_type, rollback_amount in allocated_resources.items():
                        rollback_resource = environment.resources[rollback_type]
                        rollback_resource.allocated -= rollback_amount
                        rollback_resource.available += rollback_amount
                    return None
            
            return allocated_resources
            
        except Exception as e:
            self.logger.error(f"Error performing allocation: {e}")
            return None
    
    def _estimate_performance(self, environment: DeploymentEnvironment, 
                            allocated_resources: Dict[ResourceType, float]) -> float:
        """Estimate performance for the allocation"""
        
        base_performance = environment.performance_score
        
        # Adjust based on allocated resources
        resource_factor = 1.0
        for resource_type, amount in allocated_resources.items():
            if resource_type in environment.resources:
                resource = environment.resources[resource_type]
                utilization = amount / max(resource.total_capacity, 0.001)
                resource_factor *= (1.0 + utilization * 0.5)  # More resources = better performance
        
        return min(10.0, base_performance * resource_factor)
    
    def _calculate_consciousness_compatibility(self, environment: DeploymentEnvironment, 
                                             required_level: float) -> float:
        """Calculate consciousness compatibility score"""
        
        if not environment.consciousness_compatible:
            return 0.0
        
        # Base compatibility
        base_compatibility = 0.8
        
        # Adjust based on environment capabilities
        if "tpm" in environment.capabilities:
            base_compatibility += 0.1
        if "gpu" in environment.capabilities:
            base_compatibility += 0.1
        if "full_hardware_access" in environment.capabilities:
            base_compatibility += 0.1
        
        return min(1.0, base_compatibility)
    
    async def deallocate_resources(self, request_id: str) -> bool:
        """Deallocate resources for a request"""
        
        try:
            if request_id not in self.active_allocations:
                return False
            
            allocation = self.active_allocations[request_id]
            environment = allocation.deployment_environment
            
            if environment:
                # Return resources to environment
                for resource_type, amount in allocation.allocated_resources.items():
                    if resource_type in environment.resources:
                        resource = environment.resources[resource_type]
                        resource.allocated -= amount
                        resource.available += amount
            
            # Remove from active allocations
            del self.active_allocations[request_id]
            
            # Log deallocation
            await self.audit_logger.log_system_event(
                event_type="resource_deallocation",
                details={
                    "request_id": request_id,
                    "environment": environment.environment_id if environment else None,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deallocating resources for {request_id}: {e}")
            return False