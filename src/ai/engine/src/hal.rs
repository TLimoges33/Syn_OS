//! Hardware Abstraction Layer for AI accelerators and runtime optimization

use anyhow::Result;
use serde::{Deserialize, Serialize};
use tracing::info;

/// Hardware capabilities discovered on the system
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HardwareCapabilities {
    pub cpu_cores: usize,
    pub memory_gb: f64,
    pub gpu_devices: Vec<GpuDevice>,
    pub npu_devices: Vec<NpuDevice>,
    pub tpu_devices: Vec<TpuDevice>,
    pub ai_accelerators: Vec<AiAccelerator>,
}

/// GPU device information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GpuDevice {
    pub name: String,
    pub vendor: String,
    pub memory_mb: u64,
    pub compute_capability: Option<String>,
    pub supports_cuda: bool,
    pub supports_opencl: bool,
}

/// Neural Processing Unit device information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NpuDevice {
    pub name: String,
    pub vendor: String,
    pub tops: f64, // Tera Operations Per Second
    pub power_efficiency: f64,
    pub supported_frameworks: Vec<String>,
}

/// Tensor Processing Unit device information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TpuDevice {
    pub name: String,
    pub version: String,
    pub memory_gb: f64,
    pub peak_performance: f64,
}

/// Generic AI accelerator device
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AiAccelerator {
    pub name: String,
    pub device_type: String,
    pub capabilities: Vec<String>,
    pub power_consumption: f64,
}

/// Hardware abstraction layer managing AI accelerators
#[derive(Debug)]
pub struct HardwareAbstractionLayer {
    capabilities: HardwareCapabilities,
    optimal_execution_strategy: ExecutionStrategy,
}

/// Strategy for optimal AI model execution
#[derive(Debug, Clone)]
pub enum ExecutionStrategy {
    CpuOnly,
    CpuOptimized,
    GpuAccelerated { device_id: usize },
    NpuOptimized { device_id: usize },
    TpuAccelerated { device_id: usize },
    HybridExecution { primary: Box<ExecutionStrategy>, fallback: Box<ExecutionStrategy> },
}

impl HardwareAbstractionLayer {
    /// Detect available hardware and create HAL
    pub async fn detect_hardware() -> Result<Self> {
        info!("Detecting AI-capable hardware...");
        
        let capabilities = Self::probe_hardware().await?;
        let optimal_strategy = Self::determine_optimal_strategy(&capabilities).await?;
        
        info!("Hardware detection complete: {} GPU(s), {} NPU(s), {} TPU(s)", 
              capabilities.gpu_devices.len(),
              capabilities.npu_devices.len(), 
              capabilities.tpu_devices.len());
        
        Ok(Self {
            capabilities,
            optimal_execution_strategy: optimal_strategy,
        })
    }

    /// Get hardware capabilities
    pub fn get_capabilities(&self) -> HardwareCapabilities {
        self.capabilities.clone()
    }

    /// Get optimal execution strategy for current hardware
    pub fn get_optimal_strategy(&self) -> &ExecutionStrategy {
        &self.optimal_execution_strategy
    }

    /// Probe system for AI-capable hardware
    async fn probe_hardware() -> Result<HardwareCapabilities> {
        let mut capabilities = HardwareCapabilities {
            cpu_cores: num_cpus::get(),
            memory_gb: Self::get_system_memory().await?,
            gpu_devices: Vec::new(),
            npu_devices: Vec::new(),
            tpu_devices: Vec::new(),
            ai_accelerators: Vec::new(),
        };

        // Detect NVIDIA GPUs
        capabilities.gpu_devices.extend(Self::detect_nvidia_gpus().await?);
        
        // Detect AMD GPUs
        capabilities.gpu_devices.extend(Self::detect_amd_gpus().await?);
        
        // Detect Intel GPUs
        capabilities.gpu_devices.extend(Self::detect_intel_gpus().await?);
        
        // Detect NPUs (Intel Meteor Lake, Qualcomm, etc.)
        capabilities.npu_devices.extend(Self::detect_npus().await?);
        
        // Detect Google TPUs
        capabilities.tpu_devices.extend(Self::detect_tpus().await?);
        
        // Detect other AI accelerators
        capabilities.ai_accelerators.extend(Self::detect_ai_accelerators().await?);

        Ok(capabilities)
    }

    /// Determine optimal execution strategy based on available hardware
    async fn determine_optimal_strategy(capabilities: &HardwareCapabilities) -> Result<ExecutionStrategy> {
        // Priority: TPU > NPU > High-end GPU > Mid-range GPU > CPU
        
        if !capabilities.tpu_devices.is_empty() {
            info!("Using TPU acceleration for optimal performance");
            return Ok(ExecutionStrategy::TpuAccelerated { device_id: 0 });
        }
        
        if !capabilities.npu_devices.is_empty() {
            info!("Using NPU acceleration for power-efficient inference");
            return Ok(ExecutionStrategy::NpuOptimized { device_id: 0 });
        }
        
        if let Some(best_gpu) = Self::find_best_gpu(&capabilities.gpu_devices) {
            info!("Using GPU acceleration: {}", best_gpu.name);
            return Ok(ExecutionStrategy::GpuAccelerated { device_id: 0 });
        }
        
        info!("Falling back to CPU execution");
        Ok(ExecutionStrategy::CpuOnly)
    }

    async fn get_system_memory() -> Result<f64> {
        // Read from /proc/meminfo
        Ok(8.0) // Placeholder
    }

    async fn detect_nvidia_gpus() -> Result<Vec<GpuDevice>> {
        // Use nvidia-ml-py or direct CUDA detection
        Ok(vec![])
    }

    async fn detect_amd_gpus() -> Result<Vec<GpuDevice>> {
        // Use ROCm detection
        Ok(vec![])
    }

    async fn detect_intel_gpus() -> Result<Vec<GpuDevice>> {
        // Use Intel GPU detection
        Ok(vec![])
    }

    async fn detect_npus() -> Result<Vec<NpuDevice>> {
        // Detect Intel VPU, Qualcomm NPU, etc.
        Ok(vec![])
    }

    async fn detect_tpus() -> Result<Vec<TpuDevice>> {
        // Detect Google Cloud TPUs
        Ok(vec![])
    }

    async fn detect_ai_accelerators() -> Result<Vec<AiAccelerator>> {
        // Detect Hailo, Movidius, etc.
        Ok(vec![])
    }

    fn find_best_gpu(gpus: &[GpuDevice]) -> Option<&GpuDevice> {
        gpus.iter()
            .max_by_key(|gpu| gpu.memory_mb)
    }
}
