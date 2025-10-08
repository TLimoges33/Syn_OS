use crate::hal::{
    AcceleratorType, AiAccelerator, GpuCapabilities, GpuDetector, HalError, NpuDetector,
    PciManager, TpuDetector,
};
use alloc::boxed::Box;
use alloc::collections::BTreeMap;
use alloc::string::String;
/// AI Accelerator Registry
///
/// Central registry for all AI-capable hardware detected in the system.
/// Integrates with HAL to provide unified access to GPUs, NPUs, TPUs for
/// the AI runtime layer.
use alloc::vec::Vec;

/// AI Accelerator Registry
///
/// Maintains a registry of all AI-capable hardware in the system,
/// tracking capabilities, availability, and optimal usage strategies.
#[derive(Debug)]
pub struct AiAcceleratorRegistry {
    /// Registered GPU devices
    gpus: Vec<RegisteredGpu>,

    /// Registered NPU devices
    npus: Vec<RegisteredNpu>,

    /// Registered TPU devices
    tpus: Vec<RegisteredTpu>,

    /// Optimal execution strategy
    optimal_strategy: ExecutionStrategy,

    /// Next device ID
    next_device_id: u32,
}

/// Registered GPU with runtime state
#[derive(Debug, Clone)]
pub struct RegisteredGpu {
    pub device_id: u32,
    pub capabilities: GpuCapabilities,
    pub current_utilization: f32,
    pub available: bool,
    pub allocated_to: Option<u64>, // Process ID
}

/// Registered NPU with runtime state
#[derive(Debug, Clone)]
pub struct RegisteredNpu {
    pub device_id: u32,
    pub accelerator: AiAccelerator,
    pub current_utilization: f32,
    pub available: bool,
    pub allocated_to: Option<u64>,
}

/// Registered TPU with runtime state
#[derive(Debug, Clone)]
pub struct RegisteredTpu {
    pub device_id: u32,
    pub accelerator: AiAccelerator,
    pub current_utilization: f32,
    pub available: bool,
    pub allocated_to: Option<u64>,
}

/// Execution strategy for AI workloads
#[derive(Debug, Clone)]
pub enum ExecutionStrategy {
    /// Pure CPU execution (fallback)
    CpuOnly { thread_count: u8 },

    /// Single GPU acceleration
    GpuAccelerated {
        gpu_id: u32,
        fallback: Option<Box<ExecutionStrategy>>,
    },

    /// NPU-optimized execution
    NpuOptimized {
        npu_id: u32,
        fallback: Option<Box<ExecutionStrategy>>,
    },

    /// TPU-accelerated execution
    TpuAccelerated {
        tpu_id: u32,
        fallback: Option<Box<ExecutionStrategy>>,
    },

    /// Multi-GPU execution (data parallelism)
    MultiGpu {
        gpu_ids: Vec<u32>,
        load_balancing: LoadBalancingStrategy,
    },

    /// Hybrid execution (GPU + NPU)
    Hybrid {
        primary: Box<ExecutionStrategy>,
        secondary: Box<ExecutionStrategy>,
    },
}

/// Load balancing strategy for multi-device execution
#[derive(Debug, Clone, Copy)]
pub enum LoadBalancingStrategy {
    RoundRobin,
    LeastUtilized,
    PerformanceWeighted,
}

impl AiAcceleratorRegistry {
    /// Create a new AI accelerator registry
    pub fn new() -> Self {
        Self {
            gpus: Vec::new(),
            npus: Vec::new(),
            tpus: Vec::new(),
            optimal_strategy: ExecutionStrategy::CpuOnly { thread_count: 4 },
            next_device_id: 1,
        }
    }

    /// Detect and register all AI accelerators in the system
    pub fn detect_all_accelerators(&mut self, pci_manager: &PciManager) -> Result<(), HalError> {
        crate::println!("🤖 Detecting AI Accelerators...");

        // Detect GPUs
        let detected_gpus = GpuDetector::detect_all_gpus(pci_manager);
        crate::println!("  🎮 Found {} GPU(s)", detected_gpus.len());

        for gpu_caps in detected_gpus {
            self.register_gpu(gpu_caps);
        }

        // Detect NPUs
        let detected_npus = NpuDetector::detect_all_npus(pci_manager);
        crate::println!("  🧠 Found {} NPU(s)", detected_npus.len());

        for npu in detected_npus {
            self.register_npu(npu);
        }

        // Detect TPUs
        let detected_tpus = TpuDetector::detect_all_tpus(pci_manager);
        if !detected_tpus.is_empty() {
            crate::println!("  ⚡ Found {} TPU(s)", detected_tpus.len());

            for tpu in detected_tpus {
                self.register_tpu(tpu);
            }
        }

        // Determine optimal execution strategy
        self.optimal_strategy = self.determine_optimal_strategy();

        // Print summary
        self.print_accelerator_summary();

        Ok(())
    }

    /// Register a GPU device
    fn register_gpu(&mut self, capabilities: GpuCapabilities) {
        let device_id = self.next_device_id;
        self.next_device_id += 1;

        crate::println!(
            "    ✓ GPU #{}: {} ({:?})",
            device_id,
            capabilities.device_name,
            capabilities.vendor
        );

        if capabilities.supports_compute {
            if let Some(ref compute_cap) = capabilities.compute_capability {
                match compute_cap {
                    crate::hal::ComputeCapability::Cuda { major, minor } => {
                        crate::println!("      CUDA: {}.{}", major, minor);
                    }
                    crate::hal::ComputeCapability::Rocm { gcn_arch } => {
                        crate::println!("      ROCm: {}", gcn_arch);
                    }
                    crate::hal::ComputeCapability::OneApi { xe_version } => {
                        crate::println!("      oneAPI: {}", xe_version);
                    }
                }
            }
        }

        if capabilities.memory_mb > 0 {
            crate::println!("      VRAM: {} MB", capabilities.memory_mb);
        }

        let registered_gpu = RegisteredGpu {
            device_id,
            capabilities,
            current_utilization: 0.0,
            available: true,
            allocated_to: None,
        };

        self.gpus.push(registered_gpu);
    }

    /// Register an NPU device
    fn register_npu(&mut self, accelerator: AiAccelerator) {
        let device_id = self.next_device_id;
        self.next_device_id += 1;

        crate::println!("    ✓ NPU #{}: {}", device_id, accelerator.device_name);

        let registered_npu = RegisteredNpu {
            device_id,
            accelerator,
            current_utilization: 0.0,
            available: true,
            allocated_to: None,
        };

        self.npus.push(registered_npu);
    }

    /// Register a TPU device
    fn register_tpu(&mut self, accelerator: AiAccelerator) {
        let device_id = self.next_device_id;
        self.next_device_id += 1;

        crate::println!("    ✓ TPU #{}: {}", device_id, accelerator.device_name);

        let registered_tpu = RegisteredTpu {
            device_id,
            accelerator,
            current_utilization: 0.0,
            available: true,
            allocated_to: None,
        };

        self.tpus.push(registered_tpu);
    }

    /// Determine the optimal execution strategy based on available hardware
    fn determine_optimal_strategy(&self) -> ExecutionStrategy {
        // Priority: TPU > NPU > High-end GPU > Multi-GPU > Low-end GPU > CPU

        // Check for TPUs
        if let Some(tpu) = self.tpus.first() {
            return ExecutionStrategy::TpuAccelerated {
                tpu_id: tpu.device_id,
                fallback: Some(Box::new(self.determine_gpu_strategy())),
            };
        }

        // Check for NPUs
        if let Some(npu) = self.npus.first() {
            return ExecutionStrategy::NpuOptimized {
                npu_id: npu.device_id,
                fallback: Some(Box::new(self.determine_gpu_strategy())),
            };
        }

        // Determine GPU strategy
        self.determine_gpu_strategy()
    }

    /// Determine GPU-based execution strategy
    fn determine_gpu_strategy(&self) -> ExecutionStrategy {
        match self.gpus.len() {
            0 => {
                // No GPUs, fall back to CPU
                ExecutionStrategy::CpuOnly { thread_count: 4 }
            }
            1 => {
                // Single GPU
                ExecutionStrategy::GpuAccelerated {
                    gpu_id: self.gpus[0].device_id,
                    fallback: Some(Box::new(ExecutionStrategy::CpuOnly { thread_count: 4 })),
                }
            }
            _ => {
                // Multiple GPUs
                let gpu_ids: Vec<u32> = self.gpus.iter().map(|gpu| gpu.device_id).collect();

                ExecutionStrategy::MultiGpu {
                    gpu_ids,
                    load_balancing: LoadBalancingStrategy::LeastUtilized,
                }
            }
        }
    }

    /// Get the optimal execution strategy
    pub fn get_optimal_strategy(&self) -> &ExecutionStrategy {
        &self.optimal_strategy
    }

    /// Get all registered GPUs
    pub fn get_gpus(&self) -> &[RegisteredGpu] {
        &self.gpus
    }

    /// Get all registered NPUs
    pub fn get_npus(&self) -> &[RegisteredNpu] {
        &self.npus
    }

    /// Get all registered TPUs
    pub fn get_tpus(&self) -> &[RegisteredTpu] {
        &self.tpus
    }

    /// Allocate an accelerator for a process
    pub fn allocate_accelerator(
        &mut self,
        process_id: u64,
        preferred_type: AcceleratorType,
    ) -> Option<u32> {
        match preferred_type {
            AcceleratorType::GPU => {
                for gpu in &mut self.gpus {
                    if gpu.available {
                        gpu.available = false;
                        gpu.allocated_to = Some(process_id);
                        return Some(gpu.device_id);
                    }
                }
            }
            AcceleratorType::NPU => {
                for npu in &mut self.npus {
                    if npu.available {
                        npu.available = false;
                        npu.allocated_to = Some(process_id);
                        return Some(npu.device_id);
                    }
                }
            }
            AcceleratorType::TPU => {
                for tpu in &mut self.tpus {
                    if tpu.available {
                        tpu.available = false;
                        tpu.allocated_to = Some(process_id);
                        return Some(tpu.device_id);
                    }
                }
            }
            _ => {}
        }

        None
    }

    /// Release an accelerator
    pub fn release_accelerator(&mut self, device_id: u32) {
        // Try to find in GPUs
        for gpu in &mut self.gpus {
            if gpu.device_id == device_id {
                gpu.available = true;
                gpu.allocated_to = None;
                gpu.current_utilization = 0.0;
                return;
            }
        }

        // Try to find in NPUs
        for npu in &mut self.npus {
            if npu.device_id == device_id {
                npu.available = true;
                npu.allocated_to = None;
                npu.current_utilization = 0.0;
                return;
            }
        }

        // Try to find in TPUs
        for tpu in &mut self.tpus {
            if tpu.device_id == device_id {
                tpu.available = true;
                tpu.allocated_to = None;
                tpu.current_utilization = 0.0;
                return;
            }
        }
    }

    /// Update accelerator utilization
    pub fn update_utilization(&mut self, device_id: u32, utilization: f32) {
        for gpu in &mut self.gpus {
            if gpu.device_id == device_id {
                gpu.current_utilization = utilization.clamp(0.0, 100.0);
                return;
            }
        }

        for npu in &mut self.npus {
            if npu.device_id == device_id {
                npu.current_utilization = utilization.clamp(0.0, 100.0);
                return;
            }
        }

        for tpu in &mut self.tpus {
            if tpu.device_id == device_id {
                tpu.current_utilization = utilization.clamp(0.0, 100.0);
                return;
            }
        }
    }

    /// Print accelerator summary
    pub fn print_accelerator_summary(&self) {
        crate::println!("");
        crate::println!("🤖 AI Accelerator Summary:");
        crate::println!(
            "   Total Devices: {} GPU(s), {} NPU(s), {} TPU(s)",
            self.gpus.len(),
            self.npus.len(),
            self.tpus.len()
        );

        if !self.gpus.is_empty() {
            let total_vram: u64 = self.gpus.iter().map(|gpu| gpu.capabilities.memory_mb).sum();
            crate::println!("   Total VRAM: {} MB", total_vram);
        }

        crate::println!("   Optimal Strategy: {}", self.strategy_description());
        crate::println!("");
    }

    /// Get human-readable strategy description
    fn strategy_description(&self) -> &'static str {
        match &self.optimal_strategy {
            ExecutionStrategy::CpuOnly { .. } => "CPU-only execution",
            ExecutionStrategy::GpuAccelerated { .. } => "Single GPU acceleration",
            ExecutionStrategy::NpuOptimized { .. } => "NPU-optimized inference",
            ExecutionStrategy::TpuAccelerated { .. } => "TPU-accelerated execution",
            ExecutionStrategy::MultiGpu { .. } => "Multi-GPU parallel execution",
            ExecutionStrategy::Hybrid { .. } => "Hybrid GPU+NPU execution",
        }
    }

    /// Get total accelerator count
    pub fn get_total_accelerator_count(&self) -> usize {
        self.gpus.len() + self.npus.len() + self.tpus.len()
    }

    /// Check if any AI accelerators are available
    pub fn has_ai_hardware(&self) -> bool {
        self.get_total_accelerator_count() > 0
    }
}

/// Global AI Accelerator Registry
static mut AI_ACCELERATOR_REGISTRY: Option<AiAcceleratorRegistry> = None;

/// Initialize the global AI accelerator registry
pub fn init_ai_accelerator_registry(pci_manager: &PciManager) -> Result<(), HalError> {
    unsafe {
        AI_ACCELERATOR_REGISTRY = Some(AiAcceleratorRegistry::new());
        if let Some(ref mut registry) = AI_ACCELERATOR_REGISTRY {
            registry.detect_all_accelerators(pci_manager)?;
        }
    }
    Ok(())
}

/// Get the global AI accelerator registry
pub fn get_ai_accelerator_registry() -> &'static mut AiAcceleratorRegistry {
    unsafe {
        (*(&raw mut AI_ACCELERATOR_REGISTRY))
            .as_mut()
            .expect("AI accelerator registry not initialized")
    }
}

/// Get the global AI accelerator registry (immutable)
pub fn get_ai_accelerator_registry_ref() -> &'static AiAcceleratorRegistry {
    unsafe {
        (*(&raw const AI_ACCELERATOR_REGISTRY))
            .as_ref()
            .expect("AI accelerator registry not initialized")
    }
}
