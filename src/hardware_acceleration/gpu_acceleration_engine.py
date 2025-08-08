#!/usr/bin/env python3
"""
GPU Acceleration Engine for Syn_OS
Provides hardware-accelerated AI processing with consciousness-aware resource management
"""

import asyncio
import logging
import time
import os
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import threading
from concurrent.futures import ThreadPoolExecutor

try:
    import torch
    import torch.cuda as cuda
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available. Install with: pip install torch")

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False
    logging.warning("CuPy not available. Install with: pip install cupy-cuda12x")

try:
    import pyopencl as cl
    OPENCL_AVAILABLE = True
except ImportError:
    OPENCL_AVAILABLE = False
    logging.warning("PyOpenCL not available. Install with: pip install pyopencl")

from src.consciousness_v2.consciousness_bus import ConsciousnessBus, ConsciousnessState
from src.security.audit_logger import AuditLogger


class AccelerationType(Enum):
    """Types of GPU acceleration"""
    CUDA = "cuda"
    OPENCL = "opencl"
    METAL = "metal"
    CPU_FALLBACK = "cpu_fallback"


class WorkloadType(Enum):
    """Types of AI workloads"""
    NEURAL_DARWINISM = "neural_darwinism"
    CONSCIOUSNESS_PROCESSING = "consciousness_processing"
    AI_INFERENCE = "ai_inference"
    SECURITY_ANALYSIS = "security_analysis"
    THREAT_DETECTION = "threat_detection"
    PATTERN_RECOGNITION = "pattern_recognition"
    CRYPTOGRAPHIC_OPERATIONS = "cryptographic_operations"


@dataclass
class GPUDevice:
    """GPU device information"""
    device_id: int
    name: str
    memory_total: int
    memory_free: int
    compute_capability: Optional[Tuple[int, int]]
    acceleration_type: AccelerationType
    is_available: bool
    performance_score: float


@dataclass
class AccelerationRequest:
    """GPU acceleration request"""
    workload_type: WorkloadType
    consciousness_level: float
    data_size: int
    priority: int = 5  # 1-10, 10 being highest
    preferred_device: Optional[int] = None
    memory_requirement: Optional[int] = None
    compute_requirement: Optional[float] = None


@dataclass
class AccelerationResult:
    """GPU acceleration result"""
    success: bool
    device_used: Optional[GPUDevice]
    processing_time: float
    memory_used: int
    compute_utilization: float
    performance_gain: float  # Speedup compared to CPU
    error_message: Optional[str] = None


class GPUAccelerationEngine:
    """
    GPU Acceleration Engine with consciousness-aware resource management
    Provides hardware acceleration for AI workloads with intelligent device selection
    """
    
    def __init__(self, consciousness_bus: ConsciousnessBus):
        """Initialize GPU acceleration engine"""
        self.consciousness_bus = consciousness_bus
        self.audit_logger = AuditLogger()
        self.logger = logging.getLogger(__name__)
        
        # Device management
        self.available_devices: List[GPUDevice] = []
        self.device_usage: Dict[int, float] = {}  # Device utilization tracking
        self.device_locks: Dict[int, threading.Lock] = {}
        
        # Performance tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.total_processing_time = 0.0
        self.total_performance_gain = 0.0
        
        # Resource management
        self.max_concurrent_jobs = 4
        self.memory_threshold = 0.8  # Use up to 80% of GPU memory
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent_jobs)
        
        # Initialize devices
        self._initialize_devices()
    
    def _initialize_devices(self):
        """Initialize and detect available GPU devices"""
        self.logger.info("Initializing GPU acceleration devices...")
        
        # Detect CUDA devices
        if TORCH_AVAILABLE and torch.cuda.is_available():
            self._detect_cuda_devices()
        
        # Detect OpenCL devices
        if OPENCL_AVAILABLE:
            self._detect_opencl_devices()
        
        # Always have CPU fallback
        self._add_cpu_fallback()
        
        # Initialize device locks
        for device in self.available_devices:
            self.device_locks[device.device_id] = threading.Lock()
            self.device_usage[device.device_id] = 0.0
        
        self.logger.info(f"Initialized {len(self.available_devices)} acceleration devices")
    
    def _detect_cuda_devices(self):
        """Detect CUDA-capable devices"""
        try:
            device_count = torch.cuda.device_count()
            for i in range(device_count):
                props = torch.cuda.get_device_properties(i)
                memory_total = props.total_memory
                memory_free = memory_total - torch.cuda.memory_allocated(i)
                
                # Calculate performance score based on compute capability and memory
                compute_capability = (props.major, props.minor)
                performance_score = (props.major * 10 + props.minor) * (memory_total / 1e9)
                
                device = GPUDevice(
                    device_id=len(self.available_devices),
                    name=f"CUDA:{i} {props.name}",
                    memory_total=memory_total,
                    memory_free=memory_free,
                    compute_capability=compute_capability,
                    acceleration_type=AccelerationType.CUDA,
                    is_available=True,
                    performance_score=performance_score
                )
                
                self.available_devices.append(device)
                self.logger.info(f"Detected CUDA device: {device.name}")
                
        except Exception as e:
            self.logger.error(f"Error detecting CUDA devices: {e}")
    
    def _detect_opencl_devices(self):
        """Detect OpenCL-capable devices"""
        try:
            platforms = cl.get_platforms()
            for platform in platforms:
                devices = platform.get_devices()
                for device in devices:
                    if device.type & cl.device_type.GPU:
                        memory_total = device.global_mem_size
                        
                        # Estimate performance score
                        compute_units = device.max_compute_units
                        max_clock = device.max_clock_frequency
                        performance_score = compute_units * max_clock * (memory_total / 1e9) / 1000
                        
                        gpu_device = GPUDevice(
                            device_id=len(self.available_devices),
                            name=f"OpenCL: {device.name.strip()}",
                            memory_total=memory_total,
                            memory_free=memory_total,  # Approximate
                            compute_capability=None,
                            acceleration_type=AccelerationType.OPENCL,
                            is_available=True,
                            performance_score=performance_score
                        )
                        
                        self.available_devices.append(gpu_device)
                        self.logger.info(f"Detected OpenCL device: {gpu_device.name}")
                        
        except Exception as e:
            self.logger.error(f"Error detecting OpenCL devices: {e}")
    
    def _add_cpu_fallback(self):
        """Add CPU fallback device"""
        try:
            # Get CPU information
            cpu_count = os.cpu_count() or 4
            
            # Estimate memory (this is approximate)
            try:
                import psutil
                memory_total = psutil.virtual_memory().total
                memory_free = psutil.virtual_memory().available
            except ImportError:
                memory_total = 8 * 1024**3  # Assume 8GB
                memory_free = 4 * 1024**3   # Assume 4GB free
            
            # CPU performance score (much lower than GPU)
            performance_score = cpu_count * 0.1
            
            cpu_device = GPUDevice(
                device_id=len(self.available_devices),
                name=f"CPU Fallback ({cpu_count} cores)",
                memory_total=memory_total,
                memory_free=memory_free,
                compute_capability=None,
                acceleration_type=AccelerationType.CPU_FALLBACK,
                is_available=True,
                performance_score=performance_score
            )
            
            self.available_devices.append(cpu_device)
            self.logger.info(f"Added CPU fallback device: {cpu_device.name}")
            
        except Exception as e:
            self.logger.error(f"Error adding CPU fallback: {e}")
    
    def _select_optimal_device(self, request: AccelerationRequest, 
                             consciousness_state: ConsciousnessState) -> Optional[GPUDevice]:
        """Select optimal device based on request and consciousness state"""
        
        # Filter available devices
        suitable_devices = []
        for device in self.available_devices:
            if not device.is_available:
                continue
            
            # Check memory requirements
            if request.memory_requirement and device.memory_free < request.memory_requirement:
                continue
            
            # Check if device is not overloaded
            if self.device_usage.get(device.device_id, 0) > 0.9:
                continue
            
            suitable_devices.append(device)
        
        if not suitable_devices:
            return None
        
        # Consciousness-aware device selection
        consciousness_level = consciousness_state.overall_consciousness_level
        
        if consciousness_level > 0.8:
            # High consciousness: Use best available device
            return max(suitable_devices, key=lambda d: d.performance_score)
        elif consciousness_level > 0.5:
            # Medium consciousness: Balance performance and availability
            return max(suitable_devices, key=lambda d: d.performance_score * (1 - self.device_usage.get(d.device_id, 0)))
        else:
            # Low consciousness: Use least loaded device
            return min(suitable_devices, key=lambda d: self.device_usage.get(d.device_id, 0))
    
    def _estimate_performance_gain(self, workload_type: WorkloadType, 
                                 device: GPUDevice) -> float:
        """Estimate performance gain for workload on device"""
        
        # Base performance gains by workload type and device type
        base_gains = {
            WorkloadType.NEURAL_DARWINISM: {
                AccelerationType.CUDA: 15.0,
                AccelerationType.OPENCL: 8.0,
                AccelerationType.CPU_FALLBACK: 1.0
            },
            WorkloadType.CONSCIOUSNESS_PROCESSING: {
                AccelerationType.CUDA: 12.0,
                AccelerationType.OPENCL: 6.0,
                AccelerationType.CPU_FALLBACK: 1.0
            },
            WorkloadType.AI_INFERENCE: {
                AccelerationType.CUDA: 20.0,
                AccelerationType.OPENCL: 10.0,
                AccelerationType.CPU_FALLBACK: 1.0
            },
            WorkloadType.SECURITY_ANALYSIS: {
                AccelerationType.CUDA: 8.0,
                AccelerationType.OPENCL: 4.0,
                AccelerationType.CPU_FALLBACK: 1.0
            },
            WorkloadType.THREAT_DETECTION: {
                AccelerationType.CUDA: 10.0,
                AccelerationType.OPENCL: 5.0,
                AccelerationType.CPU_FALLBACK: 1.0
            },
            WorkloadType.PATTERN_RECOGNITION: {
                AccelerationType.CUDA: 25.0,
                AccelerationType.OPENCL: 12.0,
                AccelerationType.CPU_FALLBACK: 1.0
            },
            WorkloadType.CRYPTOGRAPHIC_OPERATIONS: {
                AccelerationType.CUDA: 30.0,
                AccelerationType.OPENCL: 15.0,
                AccelerationType.CPU_FALLBACK: 1.0
            }
        }
        
        base_gain = base_gains.get(workload_type, {}).get(device.acceleration_type, 1.0)
        
        # Adjust based on device performance score
        if device.acceleration_type != AccelerationType.CPU_FALLBACK:
            performance_multiplier = min(2.0, device.performance_score / 100.0)
            return base_gain * performance_multiplier
        
        return base_gain
    
    async def accelerate_workload(self, request: AccelerationRequest) -> AccelerationResult:
        """Accelerate AI workload with consciousness-aware device selection"""
        start_time = time.time()
        self.total_requests += 1
        
        try:
            # Get consciousness state
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            
            # Select optimal device
            selected_device = self._select_optimal_device(request, consciousness_state)
            if not selected_device:
                return AccelerationResult(
                    success=False,
                    device_used=None,
                    processing_time=time.time() - start_time,
                    memory_used=0,
                    compute_utilization=0.0,
                    performance_gain=1.0,
                    error_message="No suitable device available"
                )
            
            # Acquire device lock
            with self.device_locks[selected_device.device_id]:
                # Update device usage
                self.device_usage[selected_device.device_id] += 0.1
                
                try:
                    # Execute workload based on device type
                    if selected_device.acceleration_type == AccelerationType.CUDA:
                        result = await self._execute_cuda_workload(request, selected_device)
                    elif selected_device.acceleration_type == AccelerationType.OPENCL:
                        result = await self._execute_opencl_workload(request, selected_device)
                    else:
                        result = await self._execute_cpu_workload(request, selected_device)
                    
                    # Calculate performance metrics
                    processing_time = time.time() - start_time
                    estimated_gain = self._estimate_performance_gain(request.workload_type, selected_device)
                    
                    # Update performance tracking
                    self.successful_requests += 1
                    self.total_processing_time += processing_time
                    self.total_performance_gain += estimated_gain
                    
                    # Log the acceleration
                    await self.audit_logger.log_system_event(
                        event_type="gpu_acceleration",
                        details={
                            "workload_type": request.workload_type.value,
                            "device_used": selected_device.name,
                            "processing_time": processing_time,
                            "performance_gain": estimated_gain,
                            "consciousness_level": request.consciousness_level
                        }
                    )
                    
                    return AccelerationResult(
                        success=True,
                        device_used=selected_device,
                        processing_time=processing_time,
                        memory_used=result.get("memory_used", 0),
                        compute_utilization=result.get("compute_utilization", 0.0),
                        performance_gain=estimated_gain
                    )
                    
                finally:
                    # Release device usage
                    self.device_usage[selected_device.device_id] = max(0.0, 
                        self.device_usage[selected_device.device_id] - 0.1)
        
        except Exception as e:
            self.logger.error(f"GPU acceleration error: {e}")
            
            return AccelerationResult(
                success=False,
                device_used=selected_device if 'selected_device' in locals() else None,
                processing_time=time.time() - start_time,
                memory_used=0,
                compute_utilization=0.0,
                performance_gain=1.0,
                error_message=str(e)
            )
    
    async def _execute_cuda_workload(self, request: AccelerationRequest, 
                                   device: GPUDevice) -> Dict[str, Any]:
        """Execute workload on CUDA device"""
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch not available for CUDA execution")
        
        # Extract device index from device_id (assuming CUDA devices are first)
        cuda_device_idx = 0
        for i, dev in enumerate(self.available_devices):
            if dev.device_id == device.device_id:
                if dev.acceleration_type == AccelerationType.CUDA:
                    cuda_device_idx = i
                break
        
        # Set CUDA device
        torch.cuda.set_device(cuda_device_idx)
        
        # Simulate workload execution (replace with actual workload)
        memory_before = torch.cuda.memory_allocated()
        
        # Example: Matrix operations for different workload types
        if request.workload_type == WorkloadType.NEURAL_DARWINISM:
            # Simulate neural population evolution
            population_size = min(1000, request.data_size)
            weights = torch.randn(population_size, 512, device=f'cuda:{cuda_device_idx}')
            evolved_weights = torch.matmul(weights, weights.T)
            result = torch.sum(evolved_weights)
            
        elif request.workload_type == WorkloadType.AI_INFERENCE:
            # Simulate AI model inference
            batch_size = min(32, request.data_size)
            input_tensor = torch.randn(batch_size, 768, device=f'cuda:{cuda_device_idx}')
            weight_matrix = torch.randn(768, 256, device=f'cuda:{cuda_device_idx}')
            result = torch.matmul(input_tensor, weight_matrix)
            
        else:
            # Generic computation
            size = min(1024, request.data_size)
            tensor_a = torch.randn(size, size, device=f'cuda:{cuda_device_idx}')
            tensor_b = torch.randn(size, size, device=f'cuda:{cuda_device_idx}')
            result = torch.matmul(tensor_a, tensor_b)
        
        # Synchronize to ensure completion
        torch.cuda.synchronize()
        
        memory_after = torch.cuda.memory_allocated()
        memory_used = memory_after - memory_before
        
        # Estimate compute utilization (simplified)
        compute_utilization = min(1.0, request.data_size / 10000.0)
        
        return {
            "memory_used": memory_used,
            "compute_utilization": compute_utilization,
            "result_shape": result.shape if hasattr(result, 'shape') else None
        }
    
    async def _execute_opencl_workload(self, request: AccelerationRequest, 
                                     device: GPUDevice) -> Dict[str, Any]:
        """Execute workload on OpenCL device"""
        if not OPENCL_AVAILABLE:
            raise RuntimeError("PyOpenCL not available for OpenCL execution")
        
        # Simplified OpenCL execution
        # In a real implementation, you would write OpenCL kernels
        
        # Estimate memory usage and compute utilization
        estimated_memory = request.data_size * 4  # Assume 4 bytes per element
        compute_utilization = min(1.0, request.data_size / 5000.0)
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        return {
            "memory_used": estimated_memory,
            "compute_utilization": compute_utilization
        }
    
    async def _execute_cpu_workload(self, request: AccelerationRequest, 
                                  device: GPUDevice) -> Dict[str, Any]:
        """Execute workload on CPU (fallback)"""
        
        # Simulate CPU processing
        if TORCH_AVAILABLE:
            # Use PyTorch CPU operations
            if request.workload_type == WorkloadType.NEURAL_DARWINISM:
                size = min(500, request.data_size)  # Smaller for CPU
                tensor_a = torch.randn(size, size)
                tensor_b = torch.randn(size, size)
                result = torch.matmul(tensor_a, tensor_b)
            else:
                size = min(256, request.data_size)
                tensor = torch.randn(size, size)
                result = torch.sum(tensor)
        else:
            # Pure Python fallback
            import random
            data = [random.random() for _ in range(min(1000, request.data_size))]
            result = sum(data)
        
        # Estimate resource usage
        estimated_memory = request.data_size * 8  # Assume 8 bytes per element for CPU
        compute_utilization = min(1.0, request.data_size / 1000.0)
        
        return {
            "memory_used": estimated_memory,
            "compute_utilization": compute_utilization
        }
    
    def get_device_status(self) -> List[Dict[str, Any]]:
        """Get status of all acceleration devices"""
        status = []
        for device in self.available_devices:
            device_status = {
                "device_id": device.device_id,
                "name": device.name,
                "acceleration_type": device.acceleration_type.value,
                "memory_total": device.memory_total,
                "memory_free": device.memory_free,
                "performance_score": device.performance_score,
                "is_available": device.is_available,
                "current_usage": self.device_usage.get(device.device_id, 0.0)
            }
            
            # Add CUDA-specific information
            if device.acceleration_type == AccelerationType.CUDA and TORCH_AVAILABLE:
                try:
                    cuda_idx = 0  # Simplified mapping
                    device_status.update({
                        "cuda_memory_allocated": torch.cuda.memory_allocated(cuda_idx),
                        "cuda_memory_reserved": torch.cuda.memory_reserved(cuda_idx),
                        "cuda_temperature": "N/A"  # Would need nvidia-ml-py for this
                    })
                except:
                    pass
            
            status.append(device_status)
        
        return status
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the acceleration engine"""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "success_rate": self.successful_requests / max(1, self.total_requests),
            "average_processing_time": self.total_processing_time / max(1, self.successful_requests),
            "average_performance_gain": self.total_performance_gain / max(1, self.successful_requests),
            "available_devices": len(self.available_devices),
            "cuda_devices": len([d for d in self.available_devices if d.acceleration_type == AccelerationType.CUDA]),
            "opencl_devices": len([d for d in self.available_devices if d.acceleration_type == AccelerationType.OPENCL])
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on GPU acceleration engine"""
        try:
            # Test basic acceleration
            test_request = AccelerationRequest(
                workload_type=WorkloadType.AI_INFERENCE,
                consciousness_level=0.5,
                data_size=100,
                priority=1
            )
            
            result = await self.accelerate_workload(test_request)
            
            return {
                "status": "healthy" if result.success else "degraded",
                "available_devices": len(self.available_devices),
                "test_result": {
                    "success": result.success,
                    "processing_time": result.processing_time,
                    "performance_gain": result.performance_gain,
                    "device_used": result.device_used.name if result.device_used else None
                },
                "performance_metrics": self.get_performance_metrics()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "available_devices": len(self.available_devices)
            }
    
    async def shutdown(self):
        """Shutdown GPU acceleration engine"""
        self.logger.info("Shutting down GPU acceleration engine...")
        
        # Shutdown thread pool
        self.executor.shutdown(wait=True)
        
        # Clear CUDA cache if available
        if TORCH_AVAILABLE and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.logger.info("GPU acceleration engine shutdown complete")


# Example usage and testing
async def main():
    """Example usage of GPU Acceleration Engine"""
    from src.consciousness_v2.consciousness_bus import ConsciousnessBus
    
    # Initialize consciousness bus
    consciousness_bus = ConsciousnessBus()
    
    # Initialize GPU acceleration engine
    gpu_engine = GPUAccelerationEngine(consciousness_bus)
    
    # Health check
    health = await gpu_engine.health_check()
    print(f"Health check: {health}")
    
    # Test different workloads
    workloads = [
        (WorkloadType.NEURAL_DARWINISM, 1000),
        (WorkloadType.AI_INFERENCE, 500),
        (WorkloadType.PATTERN_RECOGNITION, 2000)
    ]
    
    for workload_type, data_size in workloads:
        request = AccelerationRequest(
            workload_type=workload_type,
            consciousness_level=0.8,
            data_size=data_size,
            priority=7
        )
        
        result = await gpu_engine.accelerate_workload(request)
        print(f"\nWorkload: {workload_type.value}")
        print(f"Success: {result.success}")
        print(f"Device: {result.device_used.name if result.device_used else 'None'}")
        print(f"Processing time: {result.processing_time:.3f}s")
        print(f"Performance gain: {result.performance_gain:.1f}x")
    
    # Show device status
    print(f"\nDevice Status:")
    for device_status in gpu_engine.get_device_status():
        print(f"  {device_status['name']}: {device_status['current_usage']:.1%} usage")
    
    # Shutdown
    await gpu_engine.shutdown()


if __name__ == "__main__":
    asyncio.run(main())