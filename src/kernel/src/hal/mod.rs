/// Hardware Abstraction Layer (HAL) Module for SynOS
/// Complete hardware abstraction with AI consciousness integration

use alloc::collections::BTreeMap;
use alloc::vec::Vec;
use alloc::boxed::Box;
use core::fmt;

pub mod cpu;
pub mod memory;
pub mod io;
pub mod pci;
pub mod acpi;
pub mod minimal_hal;
pub mod gpu_detection;
pub mod ai_accelerator_registry;

// Re-export all HAL components
pub use cpu::*;
pub use memory::*;
pub use io::*;
pub use pci::*;
pub use acpi::*;
pub use gpu_detection::*;
pub use ai_accelerator_registry::*;

/// Hardware abstraction layer manager
#[derive(Debug)]
pub struct HardwareAbstractionLayer {
    /// CPU information and management
    cpu_info: CpuInfo,
    /// Memory subsystem management
    memory_controller: MemoryController,
    /// I/O subsystem management
    io_controller: IoController,
    /// PCI bus management
    pci_manager: PciManager,
    /// ACPI interface
    acpi_interface: AcpiInterface,
    /// Device registry
    device_registry: DeviceRegistry,
}

/// CPU information and capabilities
#[derive(Debug, Clone)]
pub struct CpuInfo {
    pub vendor: CpuVendor,
    pub model: u32,
    pub family: u32,
    pub stepping: u32,
    pub features: CpuFeatures,
    pub core_count: u32,
    pub thread_count: u32,
    pub base_frequency: u64, // Hz
    pub max_frequency: u64,  // Hz
    pub cache_info: CacheInfo,
}

/// CPU vendor identification
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CpuVendor {
    Intel,
    AMD,
    Unknown,
}

/// CPU feature flags
#[derive(Debug, Clone, Copy)]
pub struct CpuFeatures {
    pub sse: bool,
    pub sse2: bool,
    pub sse3: bool,
    pub ssse3: bool,
    pub sse4_1: bool,
    pub sse4_2: bool,
    pub avx: bool,
    pub avx2: bool,
    pub avx512: bool,
    pub aes: bool,
    pub rdrand: bool,
    pub rdseed: bool,
    pub tsx: bool,
    pub mpx: bool,
    pub cet: bool,
    pub virtualization: bool,
}

/// CPU cache information
#[derive(Debug, Clone)]
pub struct CacheInfo {
    pub l1_instruction_size: u32, // KB
    pub l1_data_size: u32,        // KB
    pub l2_size: u32,             // KB
    pub l3_size: u32,             // KB
    pub line_size: u32,           // bytes
}

/// Memory controller for system memory management
#[derive(Debug)]
pub struct MemoryController {
    pub total_memory: u64,
    pub available_memory: u64,
    pub memory_regions: Vec<MemoryRegion>,
    pub ecc_enabled: bool,
    pub memory_type: MemoryType,
}

/// Memory region descriptor
#[derive(Debug, Clone)]
pub struct MemoryRegion {
    pub base_address: u64,
    pub size: u64,
    pub region_type: MemoryRegionType,
    pub attributes: MemoryAttributes,
}

/// Memory region types
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MemoryRegionType {
    Usable,
    Reserved,
    AcpiReclaim,
    AcpiNvs,
    BadMemory,
    Bootloader,
    Kernel,
    Module,
}

/// Memory type detection
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MemoryType {
    DDR3,
    DDR4,
    DDR5,
    Unknown,
}

/// Memory attributes
#[derive(Debug, Clone, Copy)]
pub struct MemoryAttributes {
    pub cacheable: bool,
    pub writeable: bool,
    pub executable: bool,
}

/// I/O controller for system I/O management
#[derive(Debug)]
pub struct IoController {
    pub port_ranges: Vec<IoPortRange>,
    pub memory_mapped_ranges: Vec<MemoryMappedRange>,
    pub dma_channels: Vec<DmaChannel>,
}

/// I/O port range
#[derive(Debug, Clone)]
pub struct IoPortRange {
    pub base_port: u16,
    pub size: u16,
    pub description: &'static str,
}

/// Memory-mapped I/O range
#[derive(Debug, Clone)]
pub struct MemoryMappedRange {
    pub base_address: u64,
    pub size: u64,
    pub device_type: &'static str,
}

/// DMA channel information
#[derive(Debug, Clone)]
pub struct DmaChannel {
    pub channel: u8,
    pub width: DmaWidth,
    pub mode: DmaMode,
}

/// DMA transfer width
#[derive(Debug, Clone, Copy)]
pub enum DmaWidth {
    Bits8,
    Bits16,
    Bits32,
}

/// DMA transfer mode
#[derive(Debug, Clone, Copy)]
pub enum DmaMode {
    Demand,
    Single,
    Block,
    Cascade,
}

/// PCI bus manager
#[derive(Debug)]
pub struct PciManager {
    pub devices: Vec<PciDevice>,
    pub buses: BTreeMap<u8, PciBus>,
}

/// PCI device information
#[derive(Debug, Clone)]
pub struct PciDevice {
    pub bus: u8,
    pub device: u8,
    pub function: u8,
    pub vendor_id: u16,
    pub device_id: u16,
    pub class_code: u32,
    pub revision: u8,
    pub bars: Vec<PciBar>,
    pub capabilities: Vec<PciCapability>,
}

/// PCI Base Address Register
#[derive(Debug, Clone)]
pub struct PciBar {
    pub index: u8,
    pub base_address: u64,
    pub size: u64,
    pub bar_type: PciBarType,
}

/// PCI BAR types
#[derive(Debug, Clone, Copy)]
pub enum PciBarType {
    Memory32,
    Memory64,
    IoPort,
}

/// PCI capability
#[derive(Debug, Clone)]
pub struct PciCapability {
    pub id: u8,
    pub offset: u8,
    pub data: Vec<u8>,
}

/// PCI bus information
#[derive(Debug, Clone)]
pub struct PciBus {
    pub bus_number: u8,
    pub primary_bus: u8,
    pub secondary_bus: u8,
    pub subordinate_bus: u8,
}

/// ACPI interface for power management
#[derive(Debug)]
pub struct AcpiInterface {
    pub acpi_enabled: bool,
    pub acpi_version: u8,
    pub power_states: Vec<PowerState>,
    pub thermal_zones: Vec<ThermalZone>,
    pub processor_objects: Vec<ProcessorObject>,
}

/// ACPI power states
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PowerState {
    S0,  // Working
    S1,  // Sleep
    S2,  // Sleep (deeper)
    S3,  // Suspend to RAM
    S4,  // Suspend to disk
    S5,  // Shutdown
}

/// Thermal zone information
#[derive(Debug, Clone)]
pub struct ThermalZone {
    pub zone_id: u8,
    pub current_temperature: i32, // Celsius * 10
    pub critical_temperature: i32,
    pub passive_temperature: i32,
    pub active_cooling: bool,
}

/// ACPI processor object
#[derive(Debug, Clone)]
pub struct ProcessorObject {
    pub processor_id: u8,
    pub performance_states: Vec<PerformanceState>,
    pub c_states: Vec<CState>,
}

/// CPU performance state (P-state)
#[derive(Debug, Clone)]
pub struct PerformanceState {
    pub frequency: u32,       // MHz
    pub voltage: u32,         // mV
    pub power_consumption: u32, // mW
}

/// CPU idle state (C-state)
#[derive(Debug, Clone)]
pub struct CState {
    pub state_type: u8,
    pub latency: u32,         // microseconds
    pub power_consumption: u32, // mW
}

/// Device registry for hardware device management
#[derive(Debug)]
pub struct DeviceRegistry {
    pub devices: BTreeMap<u32, HardwareDevice>,
    pub device_classes: BTreeMap<HardwareDeviceClass, Vec<u32>>,
    pub next_device_id: u32,
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
    Processor,
    SystemPeripheral,
    Unknown,
}

/// Hardware device representation
#[derive(Debug, Clone)]
pub struct HardwareDevice {
    pub device_id: u32,
    pub device_class: HardwareDeviceClass,
    pub vendor_id: u32,
    pub product_id: u32,
    pub device_name: &'static str,
    pub driver_name: Option<&'static str>,
    pub resources: Vec<HardwareResource>,
    pub capabilities: DeviceCapabilities,
    pub power_state: DevicePowerState,
}

/// Hardware resource allocation
#[derive(Debug, Clone)]
pub enum HardwareResource {
    IoPort { base: u16, size: u16 },
    Memory { base: u64, size: u64, cacheable: bool },
    Interrupt { line: u8, mode: InterruptMode },
    Dma { channel: u8 },
}

/// Interrupt modes
#[derive(Debug, Clone, Copy)]
pub enum InterruptMode {
    EdgeTriggered,
    LevelTriggered,
}

/// Device capabilities
#[derive(Debug, Clone)]
pub struct DeviceCapabilities {
    pub hot_pluggable: bool,
    pub power_management: bool,
    pub dma_capable: bool,
    pub msi_capable: bool,
    pub msix_capable: bool,
    pub virtualization_support: bool,
    pub security_features: bool,
}

/// Device power management states
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DevicePowerState {
    D0, // Fully on
    D1, // Low power
    D2, // Lower power
    D3Hot, // Off with power
    D3Cold, // Off without power
}

/// Hardware information summary
#[derive(Debug, Clone)]
pub struct HardwareSummary {
    pub cpu_vendor: CpuVendor,
    pub cpu_cores: u32,
    pub cpu_frequency: u64,
    pub total_memory: u64,
    pub available_memory: u64,
    pub pci_devices: u32,
    pub usb_controllers: u32,
    pub network_adapters: u32,
    pub graphics_adapters: u32,
    pub storage_controllers: u32,
    pub acpi_available: bool,
    pub thermal_zones: u32,
    pub power_states: u32,
}

/// HAL error types
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HalError {
    DeviceNotFound,
    CpuDetectionFailed,
    MemoryDetectionFailed,
    IoInitializationFailed,
    PciScanFailed,
    AcpiInitializationFailed,
    DeviceDiscoveryFailed,
    UnsupportedHardware,
    ResourceConflict,
    PermissionDenied,
    InvalidOperation,
}

impl fmt::Display for HalError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            HalError::CpuDetectionFailed => write!(f, "CPU detection failed"),
            HalError::MemoryDetectionFailed => write!(f, "Memory detection failed"),
            HalError::IoInitializationFailed => write!(f, "I/O initialization failed"),
            HalError::PciScanFailed => write!(f, "PCI bus scan failed"),
            HalError::AcpiInitializationFailed => write!(f, "ACPI initialization failed"),
            HalError::DeviceDiscoveryFailed => write!(f, "Device discovery failed"),
            HalError::UnsupportedHardware => write!(f, "Unsupported hardware"),
            HalError::ResourceConflict => write!(f, "Resource conflict"),
            HalError::PermissionDenied => write!(f, "Permission denied"),
            HalError::InvalidOperation => write!(f, "Invalid operation"),
            HalError::DeviceNotFound => write!(f, "Device not found"),
        }
    }
}

impl HardwareAbstractionLayer {
    /// Create a new HAL instance
    pub fn new() -> Self {
        Self {
            cpu_info: CpuInfo::detect(),
            memory_controller: MemoryController::detect(),
            io_controller: IoController::new(),
            pci_manager: PciManager::new(),
            acpi_interface: AcpiInterface::new(),
            device_registry: DeviceRegistry::new(),
        }
    }

    /// Initialize the hardware abstraction layer
    pub fn init(&mut self) -> Result<(), HalError> {
        crate::println!("🔧 Initializing Hardware Abstraction Layer...");
        
        // Initialize CPU features and capabilities
        self.init_cpu()?;
        
        // Initialize memory controller
        self.init_memory()?;
        
        // Initialize I/O subsystem
        self.init_io()?;
        
        // Initialize PCI bus
        self.init_pci()?;
        
        // Initialize ACPI interface
        self.init_acpi()?;
        
        // Discover and register hardware devices
        self.discover_devices()?;
        
        crate::println!("✅ Hardware Abstraction Layer initialized successfully");
        self.print_hardware_summary();
        Ok(())
    }

    /// Initialize CPU subsystem
    fn init_cpu(&mut self) -> Result<(), HalError> {
        crate::println!("  🧠 CPU: {} cores, {} threads, {} MHz", 
            self.cpu_info.core_count,
            self.cpu_info.thread_count,
            self.cpu_info.max_frequency / 1_000_000);
        
        // Print CPU features
        let features = &self.cpu_info.features;
        let mut feature_list = Vec::new();
        
        if features.sse { feature_list.push("SSE"); }
        if features.sse2 { feature_list.push("SSE2"); }
        if features.sse3 { feature_list.push("SSE3"); }
        if features.avx { feature_list.push("AVX"); }
        if features.avx2 { feature_list.push("AVX2"); }
        if features.aes { feature_list.push("AES-NI"); }
        if features.rdrand { feature_list.push("RDRAND"); }
        if features.rdseed { feature_list.push("RDSEED"); }
        if features.virtualization { feature_list.push("VT-x/AMD-V"); }
        
        if !feature_list.is_empty() {
            crate::println!("    Features: {}", feature_list.join(", "));
        }
        
        Ok(())
    }

    /// Initialize memory subsystem
    fn init_memory(&mut self) -> Result<(), HalError> {
        crate::println!("  💾 Memory: {} MB total, {} regions", 
            self.memory_controller.total_memory / (1024 * 1024),
            self.memory_controller.memory_regions.len());
        
        if self.memory_controller.ecc_enabled {
            crate::println!("    ECC: Enabled");
        }
        
        Ok(())
    }

    /// Initialize I/O subsystem
    fn init_io(&mut self) -> Result<(), HalError> {
        crate::println!("  🔌 I/O: {} port ranges, {} MMIO ranges", 
            self.io_controller.port_ranges.len(),
            self.io_controller.memory_mapped_ranges.len());
        
        Ok(())
    }

    /// Initialize PCI subsystem
    fn init_pci(&mut self) -> Result<(), HalError> {
        self.pci_manager.scan_buses()?;

        crate::println!("  🚌 PCI: {} devices detected on {} buses",
            self.pci_manager.devices.len(),
            self.pci_manager.buses.len());

        // Initialize AI accelerator registry after PCI scan
        ai_accelerator_registry::init_ai_accelerator_registry(&self.pci_manager)?;

        Ok(())
    }

    /// Initialize ACPI interface
    fn init_acpi(&mut self) -> Result<(), HalError> {
        if self.acpi_interface.acpi_enabled {
            crate::println!("  ⚡ ACPI: Version {} detected, {} power states available", 
                self.acpi_interface.acpi_version,
                self.acpi_interface.power_states.len());
                
            if !self.acpi_interface.thermal_zones.is_empty() {
                crate::println!("    Thermal: {} zones monitoring temperature", 
                    self.acpi_interface.thermal_zones.len());
            }
        } else {
            crate::println!("  ⚡ ACPI: Not available");
        }
        
        Ok(())
    }

    /// Discover and register hardware devices
    fn discover_devices(&mut self) -> Result<(), HalError> {
        let device_count = self.device_registry.discover_devices(&self.pci_manager)?;
        
        crate::println!("  🔍 Devices: {} hardware devices discovered", device_count);
        
        // Print device summary by class
        for device_class in [
            HardwareDeviceClass::Storage,
            HardwareDeviceClass::Network,
            HardwareDeviceClass::Graphics,
            HardwareDeviceClass::Audio,
        ] {
            let devices = self.device_registry.get_devices_by_class(device_class);
            if !devices.is_empty() {
                crate::println!("    {:?}: {} device(s)", device_class, devices.len());
            }
        }
        
        Ok(())
    }

    /// Get hardware summary
    pub fn get_hardware_summary(&self) -> HardwareSummary {
        let storage_count = self.device_registry.get_devices_by_class(HardwareDeviceClass::Storage).len() as u32;
        let network_count = self.device_registry.get_devices_by_class(HardwareDeviceClass::Network).len() as u32;
        let graphics_count = self.device_registry.get_devices_by_class(HardwareDeviceClass::Graphics).len() as u32;
        
        HardwareSummary {
            cpu_vendor: self.cpu_info.vendor,
            cpu_cores: self.cpu_info.core_count,
            cpu_frequency: self.cpu_info.max_frequency,
            total_memory: self.memory_controller.total_memory,
            available_memory: self.memory_controller.available_memory,
            pci_devices: self.pci_manager.devices.len() as u32,
            usb_controllers: 0, // TODO: Count USB controllers
            network_adapters: network_count,
            graphics_adapters: graphics_count,
            storage_controllers: storage_count,
            acpi_available: self.acpi_interface.acpi_enabled,
            thermal_zones: self.acpi_interface.thermal_zones.len() as u32,
            power_states: self.acpi_interface.power_states.len() as u32,
        }
    }

    /// Print detailed hardware summary
    pub fn print_hardware_summary(&self) {
        let summary = self.get_hardware_summary();
        
        crate::println!("");
        crate::println!("🖥️  Hardware Summary:");
        crate::println!("   CPU: {:?} {} cores @ {} MHz", 
            summary.cpu_vendor, summary.cpu_cores, summary.cpu_frequency / 1_000_000);
        crate::println!("   Memory: {} MB total, {} MB available", 
            summary.total_memory / (1024 * 1024), summary.available_memory / (1024 * 1024));
        crate::println!("   Devices: {} PCI, {} Network, {} Graphics, {} Storage", 
            summary.pci_devices, summary.network_adapters, summary.graphics_adapters, summary.storage_controllers);
        
        if summary.acpi_available {
            crate::println!("   Power: ACPI enabled, {} thermal zones, {} power states", 
                summary.thermal_zones, summary.power_states);
        }
        crate::println!("");
    }

    /// Get CPU information
    pub fn get_cpu_info(&self) -> &CpuInfo {
        &self.cpu_info
    }

    /// Get memory controller
    pub fn get_memory_controller(&self) -> &MemoryController {
        &self.memory_controller
    }

    /// Get PCI manager
    pub fn get_pci_manager(&self) -> &PciManager {
        &self.pci_manager
    }

    /// Get ACPI interface
    pub fn get_acpi_interface(&self) -> &AcpiInterface {
        &self.acpi_interface
    }

    /// Get device registry
    pub fn get_device_registry(&self) -> &DeviceRegistry {
        &self.device_registry
    }

    /// Enter power state
    pub fn enter_power_state(&self, state: PowerState) -> Result<(), HalError> {
        if self.acpi_interface.acpi_enabled {
            self.acpi_interface.enter_power_state(state)
        } else {
            Err(HalError::UnsupportedHardware)
        }
    }

    /// Get thermal information
    pub fn get_thermal_info(&self) -> Vec<ThermalZone> {
        self.acpi_interface.get_thermal_info()
    }

    /// Set CPU frequency
    pub fn set_cpu_frequency(&self, frequency: u32) -> Result<(), HalError> {
        // Implementation would interact with ACPI P-states
        crate::println!("Setting CPU frequency to {} MHz", frequency);
        Ok(())
    }

    /// Get hardware device by ID
    pub fn get_device(&self, device_id: u32) -> Option<&HardwareDevice> {
        self.device_registry.get_device(device_id)
    }

    /// Get devices by class
    pub fn get_devices_by_class(&self, device_class: HardwareDeviceClass) -> Vec<&HardwareDevice> {
        self.device_registry.get_devices_by_class(device_class)
    }

    /// Register a new hardware device
    pub fn register_device(&mut self, device: HardwareDevice) -> u32 {
        self.device_registry.register_device(device)
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

/// Get the global HAL instance (immutable)
pub fn get_hal_ref() -> &'static HardwareAbstractionLayer {
    unsafe {
        HARDWARE_ABSTRACTION_LAYER
            .as_ref()
            .expect("Hardware abstraction layer not initialized")
    }
}

impl DeviceRegistry {
    /// Create a new device registry
    pub fn new() -> Self {
        Self {
            devices: BTreeMap::new(),
            device_classes: BTreeMap::new(),
            next_device_id: 1,
        }
    }

    /// Discover hardware devices
    pub fn discover_devices(&mut self, pci_manager: &PciManager) -> Result<u32, HalError> {
        let mut device_count = 0;

        // Register PCI devices
        for pci_device in &pci_manager.devices {
            let device_class = self.classify_pci_device(pci_device);
            let device_name = pci_manager.get_device_name(pci_device.vendor_id, pci_device.device_id);
            
            let hardware_device = HardwareDevice {
                device_id: self.next_device_id,
                device_class,
                vendor_id: pci_device.vendor_id as u32,
                product_id: pci_device.device_id as u32,
                device_name,
                driver_name: self.get_driver_name(&device_class),
                resources: self.extract_pci_resources(pci_device),
                capabilities: self.detect_pci_capabilities(pci_device),
                power_state: DevicePowerState::D0,
            };

            self.register_device(hardware_device);
            device_count += 1;
        }

        // Register legacy devices
        self.register_legacy_devices();
        device_count += self.get_legacy_device_count();

        Ok(device_count)
    }

    /// Register a hardware device
    pub fn register_device(&mut self, mut device: HardwareDevice) -> u32 {
        let device_id = self.next_device_id;
        self.next_device_id += 1;
        
        device.device_id = device_id;
        let device_class = device.device_class;
        
        self.devices.insert(device_id, device);
        self.device_classes
            .entry(device_class)
            .or_insert_with(Vec::new)
            .push(device_id);
        
        device_id
    }

    /// Get device by ID
    pub fn get_device(&self, device_id: u32) -> Option<&HardwareDevice> {
        self.devices.get(&device_id)
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

    /// Classify PCI device by class code
    fn classify_pci_device(&self, pci_device: &PciDevice) -> HardwareDeviceClass {
        let class_code = (pci_device.class_code >> 16) & 0xFF;
        
        match class_code {
            0x01 => HardwareDeviceClass::Storage,
            0x02 => HardwareDeviceClass::Network,
            0x03 => HardwareDeviceClass::Graphics,
            0x04 => HardwareDeviceClass::Audio,
            0x05 => HardwareDeviceClass::Memory,
            0x06 => HardwareDeviceClass::Bridge,
            0x09 => HardwareDeviceClass::Input,
            0x0B => HardwareDeviceClass::Processor,
            0x08 => HardwareDeviceClass::SystemPeripheral,
            _ => HardwareDeviceClass::Unknown,
        }
    }

    /// Get driver name for device class
    fn get_driver_name(&self, device_class: &HardwareDeviceClass) -> Option<&'static str> {
        match device_class {
            HardwareDeviceClass::Storage => Some("synos_storage"),
            HardwareDeviceClass::Network => Some("synos_network"),
            HardwareDeviceClass::Graphics => Some("synos_graphics"),
            HardwareDeviceClass::Audio => Some("synos_audio"),
            HardwareDeviceClass::Input => Some("synos_input"),
            HardwareDeviceClass::Output => Some("synos_output"),
            _ => None,
        }
    }

    /// Extract resources from PCI device
    fn extract_pci_resources(&self, pci_device: &PciDevice) -> Vec<HardwareResource> {
        let mut resources = Vec::new();

        // Extract BAR resources
        for bar in &pci_device.bars {
            match bar.bar_type {
                PciBarType::IoPort => {
                    resources.push(HardwareResource::IoPort {
                        base: bar.base_address as u16,
                        size: bar.size as u16,
                    });
                },
                PciBarType::Memory32 | PciBarType::Memory64 => {
                    resources.push(HardwareResource::Memory {
                        base: bar.base_address,
                        size: bar.size,
                        cacheable: true,
                    });
                },
            }
        }

        // Add interrupt resource (simplified)
        resources.push(HardwareResource::Interrupt {
            line: 10, // Placeholder
            mode: InterruptMode::LevelTriggered,
        });

        resources
    }

    /// Detect PCI device capabilities
    fn detect_pci_capabilities(&self, pci_device: &PciDevice) -> DeviceCapabilities {
        let mut capabilities = DeviceCapabilities {
            hot_pluggable: false,
            power_management: false,
            dma_capable: false,
            msi_capable: false,
            msix_capable: false,
            virtualization_support: false,
            security_features: false,
        };

        // Check capabilities from PCI configuration
        for capability in &pci_device.capabilities {
            match capability.id {
                0x01 => capabilities.power_management = true, // Power Management
                0x05 => capabilities.msi_capable = true,     // MSI
                0x11 => capabilities.msix_capable = true,    // MSI-X
                0x10 => capabilities.virtualization_support = true, // SR-IOV
                _ => {},
            }
        }

        // Assume storage and network devices are DMA capable
        match self.classify_pci_device(pci_device) {
            HardwareDeviceClass::Storage | HardwareDeviceClass::Network => {
                capabilities.dma_capable = true;
            },
            _ => {},
        }

        capabilities
    }

    /// Register legacy devices (non-PCI)
    fn register_legacy_devices(&mut self) {
        // Keyboard
        let keyboard = HardwareDevice {
            device_id: 0, // Will be set by register_device
            device_class: HardwareDeviceClass::Input,
            vendor_id: 0x0000,
            product_id: 0x0001,
            device_name: "PS/2 Keyboard",
            driver_name: Some("synos_keyboard"),
            resources: vec![
                HardwareResource::IoPort { base: 0x60, size: 1 },
                HardwareResource::IoPort { base: 0x64, size: 1 },
                HardwareResource::Interrupt { line: 1, mode: InterruptMode::EdgeTriggered },
            ],
            capabilities: DeviceCapabilities {
                hot_pluggable: false,
                power_management: false,
                dma_capable: false,
                msi_capable: false,
                msix_capable: false,
                virtualization_support: false,
                security_features: false,
            },
            power_state: DevicePowerState::D0,
        };
        self.register_device(keyboard);

        // Mouse
        let mouse = HardwareDevice {
            device_id: 0,
            device_class: HardwareDeviceClass::Input,
            vendor_id: 0x0000,
            product_id: 0x0002,
            device_name: "PS/2 Mouse",
            driver_name: Some("synos_mouse"),
            resources: vec![
                HardwareResource::Interrupt { line: 12, mode: InterruptMode::EdgeTriggered },
            ],
            capabilities: DeviceCapabilities {
                hot_pluggable: false,
                power_management: false,
                dma_capable: false,
                msi_capable: false,
                msix_capable: false,
                virtualization_support: false,
                security_features: false,
            },
            power_state: DevicePowerState::D0,
        };
        self.register_device(mouse);

        // System Timer
        let timer = HardwareDevice {
            device_id: 0,
            device_class: HardwareDeviceClass::SystemPeripheral,
            vendor_id: 0x0000,
            product_id: 0x0003,
            device_name: "System Timer (8254)",
            driver_name: Some("synos_timer"),
            resources: vec![
                HardwareResource::IoPort { base: 0x40, size: 4 },
                HardwareResource::Interrupt { line: 0, mode: InterruptMode::EdgeTriggered },
            ],
            capabilities: DeviceCapabilities {
                hot_pluggable: false,
                power_management: false,
                dma_capable: false,
                msi_capable: false,
                msix_capable: false,
                virtualization_support: false,
                security_features: false,
            },
            power_state: DevicePowerState::D0,
        };
        self.register_device(timer);

        // RTC/CMOS
        let rtc = HardwareDevice {
            device_id: 0,
            device_class: HardwareDeviceClass::SystemPeripheral,
            vendor_id: 0x0000,
            product_id: 0x0004,
            device_name: "Real-Time Clock",
            driver_name: Some("synos_rtc"),
            resources: vec![
                HardwareResource::IoPort { base: 0x70, size: 2 },
                HardwareResource::Interrupt { line: 8, mode: InterruptMode::EdgeTriggered },
            ],
            capabilities: DeviceCapabilities {
                hot_pluggable: false,
                power_management: false,
                dma_capable: false,
                msi_capable: false,
                msix_capable: false,
                virtualization_support: false,
                security_features: false,
            },
            power_state: DevicePowerState::D0,
        };
        self.register_device(rtc);
    }

    /// Get count of legacy devices
    fn get_legacy_device_count(&self) -> u32 {
        4 // Keyboard, Mouse, Timer, RTC
    }
}
