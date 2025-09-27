/// Minimal Hardware Abstraction Layer for SynOS Phase 5
/// Simplified version to get kernel building while we focus on user space

use alloc::collections::BTreeMap;
use alloc::vec::Vec;
use core::fmt;

/// HAL errors
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum HalError {
    InitializationFailed,
    DeviceNotFound,
    InvalidOperation,
    HardwareError,
}

impl fmt::Display for HalError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            HalError::InitializationFailed => write!(f, "HAL initialization failed"),
            HalError::DeviceNotFound => write!(f, "Device not found"),
            HalError::InvalidOperation => write!(f, "Invalid operation"),
            HalError::HardwareError => write!(f, "Hardware error"),
        }
    }
}

/// Minimal CPU information
#[derive(Debug, Clone)]
pub struct CpuInfo {
    pub vendor: &'static str,
    pub model: &'static str,
    pub cores: u32,
    pub threads: u32,
}

impl CpuInfo {
    pub fn detect() -> Self {
        Self {
            vendor: "Unknown",
            model: "Unknown",
            cores: 4,
            threads: 8,
        }
    }
}

/// Hardware device classes
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum HardwareDeviceClass {
    Storage,
    Network,
    Graphics,
    Audio,
    Input,
    Output,
    Memory,
    Bridge,
    Unknown,
}

/// Hardware device
#[derive(Debug, Clone)]
pub struct HardwareDevice {
    pub id: u32,
    pub name: alloc::string::String,
    pub device_class: HardwareDeviceClass,
    pub vendor_id: u16,
    pub device_id: u16,
}

/// Hardware summary
#[derive(Debug, Clone)]
pub struct HardwareSummary {
    pub cpu_vendor: &'static str,
    pub cpu_cores: u32,
    pub total_memory: u64,
    pub pci_devices: usize,
    pub registered_devices: usize,
    pub acpi_available: bool,
}

/// Minimal Hardware Abstraction Layer
pub struct HardwareAbstractionLayer {
    cpu_info: CpuInfo,
    devices: BTreeMap<u32, HardwareDevice>,
    device_classes: BTreeMap<HardwareDeviceClass, Vec<u32>>,
    next_device_id: u32,
}

impl HardwareAbstractionLayer {
    /// Create a new HAL instance
    pub fn new() -> Self {
        Self {
            cpu_info: CpuInfo::detect(),
            devices: BTreeMap::new(),
            device_classes: BTreeMap::new(),
            next_device_id: 1,
        }
    }

    /// Initialize the HAL
    pub fn init(&mut self) -> Result<(), HalError> {
        // Minimal initialization
        Ok(())
    }

    /// Get CPU information
    pub fn get_cpu_info(&self) -> &CpuInfo {
        &self.cpu_info
    }

    /// Get hardware summary
    pub fn get_hardware_summary(&self) -> HardwareSummary {
        HardwareSummary {
            cpu_vendor: self.cpu_info.vendor,
            cpu_cores: self.cpu_info.cores,
            total_memory: 1024 * 1024 * 1024, // 1GB default
            pci_devices: 0,
            registered_devices: self.devices.len(),
            acpi_available: false,
        }
    }

    /// Register a hardware device
    pub fn register_device(&mut self, mut device: HardwareDevice) -> u32 {
        let id = self.next_device_id;
        self.next_device_id += 1;
        
        device.id = id;
        let device_class = device.device_class;
        
        self.devices.insert(id, device);
        self.device_classes
            .entry(device_class)
            .or_insert_with(Vec::new)
            .push(id);
        
        id
    }

    /// Get device by ID
    pub fn get_device(&self, id: u32) -> Option<&HardwareDevice> {
        self.devices.get(&id)
    }

    /// Get devices by class
    pub fn get_devices_by_class(&self, device_class: HardwareDeviceClass) -> Vec<&HardwareDevice> {
        self.device_classes
            .get(&device_class)
            .map(|device_ids| {
                device_ids
                    .iter()
                    .filter_map(|&id| self.devices.get(&id))
                    .collect()
            })
            .unwrap_or_default()
    }
}

/// Global HAL instance
static mut HARDWARE_ABSTRACTION_LAYER: Option<HardwareAbstractionLayer> = None;

/// Initialize the global HAL
pub fn init_hal() -> Result<(), HalError> {
    unsafe {
        HARDWARE_ABSTRACTION_LAYER = Some(HardwareAbstractionLayer::new());
        if let Some(ref mut hal) = HARDWARE_ABSTRACTION_LAYER {
            hal.init()?;
        }
    }
    Ok(())
}

/// Get the global HAL instance
pub fn get_hal() -> &'static mut HardwareAbstractionLayer {
    unsafe {
        HARDWARE_ABSTRACTION_LAYER
            .as_mut()
            .expect("Hardware abstraction layer not initialized")
    }
}
