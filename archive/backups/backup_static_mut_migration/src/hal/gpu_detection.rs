/// GPU Detection and AI Accelerator Enumeration
///
/// Implements hardware detection for:
/// - NVIDIA GPUs (CUDA capability)
/// - AMD GPUs (ROCm capability)
/// - Intel GPUs (oneAPI capability)
/// - NPUs (Intel VPU, Qualcomm)
/// - TPUs (Google Cloud TPU)

use alloc::vec::Vec;
use alloc::string::String;
use crate::hal::{PciDevice, PciManager, HalError};

/// PCI Class Code for Display Controllers
const PCI_CLASS_DISPLAY: u32 = 0x030000;
const PCI_CLASS_DISPLAY_VGA: u32 = 0x030000;
const PCI_CLASS_DISPLAY_3D: u32 = 0x030200;

/// GPU Vendor IDs
pub const VENDOR_NVIDIA: u16 = 0x10DE;
pub const VENDOR_AMD: u16 = 0x1002;
pub const VENDOR_INTEL: u16 = 0x8086;

/// NPU Vendor IDs
pub const VENDOR_QUALCOMM: u16 = 0x17CB;
pub const VENDOR_APPLE: u16 = 0x106B;

/// GPU Capabilities extracted from hardware
#[derive(Debug, Clone)]
pub struct GpuCapabilities {
    pub vendor: GpuVendor,
    pub device_name: String,
    pub memory_mb: u64,
    pub pci_device_id: u16,
    pub pci_revision: u8,
    pub supports_compute: bool,
    pub compute_capability: Option<ComputeCapability>,
    pub bar_addresses: Vec<u64>,
}

/// GPU Vendor enumeration
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum GpuVendor {
    Nvidia,
    Amd,
    Intel,
    Unknown,
}

/// Compute capability for different vendors
#[derive(Debug, Clone)]
pub enum ComputeCapability {
    Cuda { major: u8, minor: u8 },        // NVIDIA CUDA
    Rocm { gcn_arch: String },            // AMD ROCm
    OneApi { xe_version: String },        // Intel oneAPI
}

/// AI Accelerator type
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AcceleratorType {
    GPU,
    NPU,
    TPU,
    VPU,  // Vision Processing Unit
    DSP,  // Digital Signal Processor
}

/// Detected AI Accelerator device
#[derive(Debug, Clone)]
pub struct AiAccelerator {
    pub accelerator_type: AcceleratorType,
    pub vendor: String,
    pub device_name: String,
    pub capabilities: AcceleratorCapabilities,
    pub pci_location: PciLocation,
}

#[derive(Debug, Clone)]
pub struct PciLocation {
    pub bus: u8,
    pub device: u8,
    pub function: u8,
}

/// Accelerator-specific capabilities
#[derive(Debug, Clone)]
pub enum AcceleratorCapabilities {
    Gpu(GpuCapabilities),
    Npu(NpuCapabilities),
    Tpu(TpuCapabilities),
}

/// NPU-specific capabilities
#[derive(Debug, Clone)]
pub struct NpuCapabilities {
    pub tops: f32,  // Tera Operations Per Second
    pub power_efficiency: f32,  // TOPS/W
    pub supported_frameworks: Vec<String>,
}

/// TPU-specific capabilities
#[derive(Debug, Clone)]
pub struct TpuCapabilities {
    pub version: String,
    pub memory_gb: f32,
    pub peak_performance_tflops: f32,
}

/// GPU Detection Manager
pub struct GpuDetector;

impl GpuDetector {
    /// Detect all GPUs in the system
    pub fn detect_all_gpus(pci_manager: &PciManager) -> Vec<GpuCapabilities> {
        let mut gpus = Vec::new();

        // Find all display controller devices
        let display_devices = pci_manager.find_devices_by_class(PCI_CLASS_DISPLAY);

        for device in display_devices {
            if let Some(gpu_caps) = Self::probe_gpu(device) {
                gpus.push(gpu_caps);
            }
        }

        gpus
    }

    /// Probe a specific PCI device for GPU capabilities
    fn probe_gpu(device: &PciDevice) -> Option<GpuCapabilities> {
        let vendor = Self::identify_vendor(device.vendor_id);

        // Only process known GPU vendors
        if vendor == GpuVendor::Unknown {
            return None;
        }

        let device_name = Self::get_device_name(device.vendor_id, device.device_id);
        let memory_mb = Self::estimate_vram_from_bars(device);
        let supports_compute = Self::check_compute_support(vendor, device.device_id);
        let compute_capability = Self::detect_compute_capability(vendor, device);

        let bar_addresses = device.bars.iter()
            .map(|bar| bar.base_address)
            .collect();

        Some(GpuCapabilities {
            vendor,
            device_name,
            memory_mb,
            pci_device_id: device.device_id,
            pci_revision: device.revision,
            supports_compute,
            compute_capability,
            bar_addresses,
        })
    }

    /// Identify GPU vendor from vendor ID
    fn identify_vendor(vendor_id: u16) -> GpuVendor {
        match vendor_id {
            VENDOR_NVIDIA => GpuVendor::Nvidia,
            VENDOR_AMD => GpuVendor::Amd,
            VENDOR_INTEL => GpuVendor::Intel,
            _ => GpuVendor::Unknown,
        }
    }

    /// Get human-readable device name
    fn get_device_name(vendor_id: u16, device_id: u16) -> String {
        match (vendor_id, device_id) {
            // NVIDIA GPUs
            (VENDOR_NVIDIA, 0x1E04) => "NVIDIA GeForce RTX 2080 Ti".into(),
            (VENDOR_NVIDIA, 0x1E07) => "NVIDIA GeForce RTX 2080 SUPER".into(),
            (VENDOR_NVIDIA, 0x2182) => "NVIDIA GeForce GTX 1660 Ti".into(),
            (VENDOR_NVIDIA, 0x2184) => "NVIDIA GeForce GTX 1660".into(),
            (VENDOR_NVIDIA, 0x2204) => "NVIDIA GeForce RTX 3090".into(),
            (VENDOR_NVIDIA, 0x2206) => "NVIDIA GeForce RTX 3080".into(),
            (VENDOR_NVIDIA, 0x2208) => "NVIDIA GeForce RTX 3070 Ti".into(),
            (VENDOR_NVIDIA, 0x2482) => "NVIDIA GeForce RTX 3070".into(),
            (VENDOR_NVIDIA, 0x2484) => "NVIDIA GeForce RTX 3060 Ti".into(),
            (VENDOR_NVIDIA, 0x2486) => "NVIDIA GeForce RTX 3060".into(),
            (VENDOR_NVIDIA, 0x2702) => "NVIDIA GeForce RTX 4090".into(),
            (VENDOR_NVIDIA, 0x2704) => "NVIDIA GeForce RTX 4080".into(),
            (VENDOR_NVIDIA, 0x2782) => "NVIDIA GeForce RTX 4070 Ti".into(),

            // AMD GPUs
            (VENDOR_AMD, 0x67DF) => "AMD Radeon RX 580".into(),
            (VENDOR_AMD, 0x67FF) => "AMD Radeon RX 560".into(),
            (VENDOR_AMD, 0x7340) => "AMD Radeon RX 5500 XT".into(),
            (VENDOR_AMD, 0x731F) => "AMD Radeon RX 5600 XT".into(),
            (VENDOR_AMD, 0x73BF) => "AMD Radeon RX 6900 XT".into(),
            (VENDOR_AMD, 0x73DF) => "AMD Radeon RX 6800 XT".into(),
            (VENDOR_AMD, 0x73EF) => "AMD Radeon RX 6800".into(),
            (VENDOR_AMD, 0x73FF) => "AMD Radeon RX 6700 XT".into(),
            (VENDOR_AMD, 0x744C) => "AMD Radeon RX 7900 XTX".into(),

            // Intel GPUs
            (VENDOR_INTEL, 0x4680) => "Intel Arc A380".into(),
            (VENDOR_INTEL, 0x4682) => "Intel Arc A750".into(),
            (VENDOR_INTEL, 0x4690) => "Intel Arc A770".into(),
            (VENDOR_INTEL, 0x5690) => "Intel Arc A580".into(),
            (VENDOR_INTEL, 0x9A49) => "Intel Iris Xe Graphics".into(),
            (VENDOR_INTEL, 0x4C8A) => "Intel Iris Xe Graphics (Meteor Lake)".into(),

            _ => format!("GPU Device {:04X}:{:04X}", vendor_id, device_id),
        }
    }

    /// Estimate VRAM size from BAR registers
    fn estimate_vram_from_bars(device: &PciDevice) -> u64 {
        // Find the largest memory BAR (usually BAR0 or BAR1 for GPUs)
        let mut max_bar_size = 0u64;

        for bar in &device.bars {
            if bar.size > max_bar_size {
                max_bar_size = bar.size;
            }
        }

        // Convert to MB
        max_bar_size / (1024 * 1024)
    }

    /// Check if GPU supports compute workloads
    fn check_compute_support(vendor: GpuVendor, device_id: u16) -> bool {
        match vendor {
            GpuVendor::Nvidia => {
                // Most NVIDIA GPUs support CUDA
                // Exclude very old cards (pre-Fermi, before 2010)
                device_id >= 0x0400
            }
            GpuVendor::Amd => {
                // AMD GCN architecture and later support ROCm
                // GCN started with Radeon HD 7000 series (2011)
                device_id >= 0x6700
            }
            GpuVendor::Intel => {
                // Intel Gen9 and later support oneAPI
                // Gen9 started with Skylake (2015)
                device_id >= 0x1900
            }
            GpuVendor::Unknown => false,
        }
    }

    /// Detect compute capability for a GPU
    fn detect_compute_capability(vendor: GpuVendor, device: &PciDevice) -> Option<ComputeCapability> {
        match vendor {
            GpuVendor::Nvidia => {
                // Estimate CUDA compute capability from device ID
                let (major, minor) = Self::estimate_cuda_capability(device.device_id);
                Some(ComputeCapability::Cuda { major, minor })
            }
            GpuVendor::Amd => {
                let gcn_arch = Self::estimate_gcn_architecture(device.device_id);
                Some(ComputeCapability::Rocm { gcn_arch })
            }
            GpuVendor::Intel => {
                let xe_version = Self::estimate_xe_version(device.device_id);
                Some(ComputeCapability::OneApi { xe_version })
            }
            GpuVendor::Unknown => None,
        }
    }

    /// Estimate NVIDIA CUDA compute capability from device ID
    fn estimate_cuda_capability(device_id: u16) -> (u8, u8) {
        match device_id {
            // RTX 40 series (Ada Lovelace) - Compute 8.9
            0x2700..=0x27FF => (8, 9),

            // RTX 30 series (Ampere) - Compute 8.6
            0x2200..=0x24FF => (8, 6),

            // RTX 20 series (Turing) - Compute 7.5
            0x1E00..=0x1FFF => (7, 5),

            // GTX 16 series (Turing without RT cores) - Compute 7.5
            0x2180..=0x21FF => (7, 5),

            // GTX 10 series (Pascal) - Compute 6.1
            0x1B00..=0x1DFF => (6, 1),

            // GTX 900 series (Maxwell) - Compute 5.2
            0x1300..=0x13FF => (5, 2),

            // Default for unknown/older cards
            _ => (5, 0),
        }
    }

    /// Estimate AMD GCN architecture from device ID
    fn estimate_gcn_architecture(device_id: u16) -> String {
        match device_id {
            // RDNA 3 (Radeon RX 7000 series)
            0x7400..=0x74FF => "RDNA 3".into(),

            // RDNA 2 (Radeon RX 6000 series)
            0x7300..=0x73FF => "RDNA 2".into(),

            // RDNA 1 (Radeon RX 5000 series)
            0x7310..=0x73FF => "RDNA".into(),

            // GCN 5 (Vega)
            0x6860..=0x68FF => "GCN 5 (Vega)".into(),

            // GCN 4 (Polaris)
            0x67C0..=0x67FF => "GCN 4 (Polaris)".into(),

            // Default
            _ => "GCN".into(),
        }
    }

    /// Estimate Intel Xe version from device ID
    fn estimate_xe_version(device_id: u16) -> String {
        match device_id {
            // Arc Alchemist (Xe-HPG)
            0x4680..=0x5690 => "Xe-HPG".into(),

            // Meteor Lake (Xe-LPG)
            0x4C00..=0x4CFF => "Xe-LPG".into(),

            // Iris Xe (Xe-LP)
            0x9A00..=0x9AFF => "Xe-LP".into(),

            // Default
            _ => "Xe".into(),
        }
    }
}

/// NPU Detection Manager
pub struct NpuDetector;

impl NpuDetector {
    /// Detect all NPUs in the system
    pub fn detect_all_npus(pci_manager: &PciManager) -> Vec<AiAccelerator> {
        let mut npus = Vec::new();

        // Intel VPU detection (Meteor Lake and later)
        npus.extend(Self::detect_intel_vpu(pci_manager));

        // Qualcomm NPU detection (ARM platforms)
        npus.extend(Self::detect_qualcomm_npu(pci_manager));

        npus
    }

    /// Detect Intel VPU (Visual Processing Unit)
    fn detect_intel_vpu(pci_manager: &PciManager) -> Vec<AiAccelerator> {
        let mut vpus = Vec::new();

        // Intel VPU class code: 0x048000 (Multimedia Controller, Other)
        for device in &pci_manager.devices {
            if device.vendor_id == VENDOR_INTEL &&
               (device.class_code & 0xFF0000) == 0x040000 {
                // Check device ID for VPU
                if Self::is_intel_vpu(device.device_id) {
                    vpus.push(AiAccelerator {
                        accelerator_type: AcceleratorType::VPU,
                        vendor: "Intel Corporation".into(),
                        device_name: "Intel VPU".into(),
                        capabilities: AcceleratorCapabilities::Npu(NpuCapabilities {
                            tops: 13.0,  // Meteor Lake VPU = 13 TOPS
                            power_efficiency: 6.5,  // ~2W for 13 TOPS
                            supported_frameworks: alloc::vec![
                                "OpenVINO".into(),
                                "ONNX Runtime".into(),
                            ],
                        }),
                        pci_location: PciLocation {
                            bus: device.bus,
                            device: device.device,
                            function: device.function,
                        },
                    });
                }
            }
        }

        vpus
    }

    /// Check if device ID matches Intel VPU
    fn is_intel_vpu(device_id: u16) -> bool {
        matches!(device_id,
            0x7D19 |  // Meteor Lake VPU
            0x643E |  // Lunar Lake VPU
            0x9A19    // Tiger Lake VPU variant
        )
    }

    /// Detect Qualcomm NPU (typically on ARM platforms)
    fn detect_qualcomm_npu(_pci_manager: &PciManager) -> Vec<AiAccelerator> {
        // On x86 systems, Qualcomm NPUs are rare
        // This would be more relevant for ARM SoCs
        Vec::new()
    }
}

/// TPU Detection Manager
pub struct TpuDetector;

impl TpuDetector {
    /// Detect Google Cloud TPUs
    pub fn detect_all_tpus(_pci_manager: &PciManager) -> Vec<AiAccelerator> {
        // TPUs are typically not PCI devices, but accessed via network
        // This is a placeholder for future expansion
        Vec::new()
    }
}
