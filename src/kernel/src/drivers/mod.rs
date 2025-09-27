// Device Driver Framework
// Provides abstraction for all hardware devices

use alloc::boxed::Box;
use alloc::collections::BTreeMap;
use alloc::string::{String, ToString};
use alloc::sync::Arc;
use alloc::vec::Vec;
use core::fmt;
use spin::Mutex;

pub mod storage;

/// Device identifier
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct DeviceId(pub u64);

impl DeviceId {
    pub fn new(vendor: u16, device: u16, instance: u32) -> Self {
        let id = ((vendor as u64) << 48) | ((device as u64) << 32) | (instance as u64);
        Self(id)
    }

    pub fn vendor(&self) -> u16 {
        (self.0 >> 48) as u16
    }

    pub fn device(&self) -> u16 {
        (self.0 >> 32) as u16
    }

    pub fn instance(&self) -> u32 {
        self.0 as u32
    }
}

impl fmt::Display for DeviceId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "{:04x}:{:04x}:{:08x}",
            self.vendor(),
            self.device(),
            self.instance()
        )
    }
}

/// Device types
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum DeviceType {
    BlockDevice,
    CharacterDevice,
    NetworkDevice,
    InputDevice,
    AudioDevice,
    VideoDevice,
    Other,
}

/// Device errors
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum DriverError {
    NotFound,
    AlreadyExists,
    NotSupported,
    InvalidParameter,
    HardwareError,
    TimeoutError,
    BusyError,
    NoMemory,
    PermissionDenied,
    IoError,
}

impl fmt::Display for DriverError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            DriverError::NotFound => write!(f, "Device not found"),
            DriverError::AlreadyExists => write!(f, "Device already exists"),
            DriverError::NotSupported => write!(f, "Operation not supported"),
            DriverError::InvalidParameter => write!(f, "Invalid parameter"),
            DriverError::HardwareError => write!(f, "Hardware error"),
            DriverError::TimeoutError => write!(f, "Operation timed out"),
            DriverError::BusyError => write!(f, "Device busy"),
            DriverError::NoMemory => write!(f, "Insufficient memory"),
            DriverError::PermissionDenied => write!(f, "Permission denied"),
            DriverError::IoError => write!(f, "I/O error"),
        }
    }
}

/// Device capabilities
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct DeviceCapabilities {
    pub can_read: bool,
    pub can_write: bool,
    pub can_seek: bool,
    pub supports_dma: bool,
    pub supports_interrupts: bool,
    pub hot_pluggable: bool,
}

impl Default for DeviceCapabilities {
    fn default() -> Self {
        Self {
            can_read: false,
            can_write: false,
            can_seek: false,
            supports_dma: false,
            supports_interrupts: false,
            hot_pluggable: false,
        }
    }
}

/// Base device trait - all devices must implement this
pub trait Device: Send + Sync {
    /// Get device type
    fn device_type(&self) -> DeviceType;

    /// Get device ID
    fn device_id(&self) -> DeviceId;

    /// Get device name
    fn name(&self) -> &str;

    /// Get device capabilities
    fn capabilities(&self) -> DeviceCapabilities;

    /// Initialize the device
    fn initialize(&mut self) -> Result<(), DriverError>;

    /// Shutdown the device
    fn shutdown(&mut self) -> Result<(), DriverError>;

    /// Reset the device
    fn reset(&mut self) -> Result<(), DriverError> {
        self.shutdown()?;
        self.initialize()
    }

    /// Get device status
    fn status(&self) -> DeviceStatus;

    /// Handle device interrupt
    fn handle_interrupt(&mut self) -> Result<(), DriverError> {
        Ok(())
    }
}

/// Device status
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum DeviceStatus {
    Unknown,
    Initializing,
    Ready,
    Busy,
    Error,
    Offline,
}

/// Block device trait for storage devices
pub trait BlockDevice: Device {
    /// Get block size in bytes
    fn block_size(&self) -> u32;

    /// Get total number of blocks
    fn block_count(&self) -> u64;

    /// Get device capacity in bytes
    fn capacity(&self) -> u64 {
        self.block_count() * self.block_size() as u64
    }

    /// Read blocks from the device
    fn read_blocks(
        &mut self,
        start_block: u64,
        block_count: u32,
        buffer: &mut [u8],
    ) -> Result<(), DriverError>;

    /// Write blocks to the device
    fn write_blocks(
        &mut self,
        start_block: u64,
        block_count: u32,
        data: &[u8],
    ) -> Result<(), DriverError>;

    /// Flush any cached writes
    fn flush(&mut self) -> Result<(), DriverError>;

    /// Check if device is read-only
    fn is_read_only(&self) -> bool;

    /// Get device geometry (for compatibility)
    fn geometry(&self) -> BlockGeometry {
        let total_blocks = self.block_count();
        let block_size = self.block_size();

        // Calculate reasonable geometry
        let sectors_per_track = 63;
        let heads = 255;
        let cylinders = total_blocks / (sectors_per_track * heads);

        BlockGeometry {
            cylinders: cylinders as u32,
            heads: heads as u32,
            sectors_per_track: sectors_per_track as u32,
            sector_size: block_size,
        }
    }
}

/// Block device geometry
#[derive(Debug, Clone, Copy)]
pub struct BlockGeometry {
    pub cylinders: u32,
    pub heads: u32,
    pub sectors_per_track: u32,
    pub sector_size: u32,
}

/// Character device trait for stream-based devices
pub trait CharacterDevice: Device {
    /// Read data from the device
    fn read(&mut self, buffer: &mut [u8]) -> Result<usize, DriverError>;

    /// Write data to the device
    fn write(&mut self, data: &[u8]) -> Result<usize, DriverError>;

    /// Check if data is available for reading
    fn available(&self) -> bool;

    /// Device-specific I/O control
    fn ioctl(&mut self, request: u32, arg: usize) -> Result<usize, DriverError>;
}

/// Network device trait
pub trait NetworkDevice: Device {
    /// Get MAC address
    fn mac_address(&self) -> [u8; 6];

    /// Set MAC address
    fn set_mac_address(&mut self, mac: [u8; 6]) -> Result<(), DriverError>;

    /// Send a network packet
    fn send_packet(&mut self, packet: &[u8]) -> Result<(), DriverError>;

    /// Receive a network packet
    fn receive_packet(&mut self, buffer: &mut [u8]) -> Result<usize, DriverError>;

    /// Get link status
    fn link_status(&self) -> LinkStatus;

    /// Get/Set link speed
    fn link_speed(&self) -> u32;
    fn set_link_speed(&mut self, speed: u32) -> Result<(), DriverError>;
}

/// Network link status
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum LinkStatus {
    Down,
    Up,
    Unknown,
}

/// Device driver trait
pub trait DeviceDriver: Send + Sync {
    /// Get driver name
    fn name(&self) -> &str;

    /// Get supported device types
    fn supported_devices(&self) -> Vec<(u16, u16)>; // (vendor_id, device_id) pairs

    /// Probe for devices this driver can handle
    fn probe(&self, device_id: DeviceId) -> Result<Box<dyn Device>, DriverError>;

    /// Get driver version
    fn version(&self) -> (u32, u32, u32); // (major, minor, patch)
}

/// Device manager
pub struct DeviceManager {
    /// Registered devices
    devices: BTreeMap<DeviceId, Arc<Mutex<Box<dyn Device>>>>,

    /// Registered drivers
    drivers: Vec<Box<dyn DeviceDriver>>,

    /// Device tree
    device_tree: DeviceTree,

    /// Next device instance number
    next_instance: u32,
}

impl DeviceManager {
    /// Create a new device manager
    pub fn new() -> Self {
        Self {
            devices: BTreeMap::new(),
            drivers: Vec::new(),
            device_tree: DeviceTree::new(),
            next_instance: 0,
        }
    }

    /// Register a device driver
    pub fn register_driver(&mut self, driver: Box<dyn DeviceDriver>) -> Result<(), DriverError> {
        crate::println!("[DeviceManager] Registering driver: {}", driver.name());
        self.drivers.push(driver);
        Ok(())
    }

    /// Probe for devices
    pub fn probe_devices(&mut self) -> Result<Vec<DeviceId>, DriverError> {
        let mut found_devices = Vec::new();

        // Probe PCI devices
        if let Ok(pci_devices) = self.probe_pci_devices() {
            found_devices.extend(pci_devices);
        }

        // Probe platform devices
        if let Ok(platform_devices) = self.probe_platform_devices() {
            found_devices.extend(platform_devices);
        }

        crate::println!("[DeviceManager] Found {} devices", found_devices.len());
        Ok(found_devices)
    }

    /// Probe PCI devices
    fn probe_pci_devices(&mut self) -> Result<Vec<DeviceId>, DriverError> {
        let mut devices = Vec::new();

        // This would integrate with the PCI bus manager from Phase 4
        // For now, we'll simulate some common devices

        // Simulate finding a storage controller
        let storage_id = DeviceId::new(0x8086, 0x2922, self.next_instance); // Intel ICH9 SATA
        self.next_instance += 1;

        // Try to find a driver for this device
        for driver in &self.drivers {
            if driver
                .supported_devices()
                .iter()
                .any(|(v, d)| *v == 0x8086 && *d == 0x2922)
            {
                match driver.probe(storage_id) {
                    Ok(device) => {
                        crate::println!(
                            "[DeviceManager] Found device: {} ({})",
                            device.name(),
                            storage_id
                        );
                        self.devices
                            .insert(storage_id, Arc::new(Mutex::new(device)));
                        devices.push(storage_id);
                        break;
                    }
                    Err(e) => {
                        crate::println!("[DeviceManager] Driver probe failed: {:?}", e);
                    }
                }
            }
        }

        Ok(devices)
    }

    /// Probe platform devices
    fn probe_platform_devices(&mut self) -> Result<Vec<DeviceId>, DriverError> {
        let mut devices = Vec::new();

        // Simulate platform devices like RAM disk, null device, etc.

        // RAM disk device
        let ramdisk_id = DeviceId::new(0x0000, 0x0001, self.next_instance);
        self.next_instance += 1;

        for driver in &self.drivers {
            if driver
                .supported_devices()
                .iter()
                .any(|(v, d)| *v == 0x0000 && *d == 0x0001)
            {
                match driver.probe(ramdisk_id) {
                    Ok(device) => {
                        crate::println!(
                            "[DeviceManager] Found platform device: {} ({})",
                            device.name(),
                            ramdisk_id
                        );
                        self.devices
                            .insert(ramdisk_id, Arc::new(Mutex::new(device)));
                        devices.push(ramdisk_id);
                        break;
                    }
                    Err(_) => {}
                }
            }
        }

        Ok(devices)
    }

    /// Get a device by ID
    pub fn get_device(&self, id: DeviceId) -> Option<Arc<Mutex<Box<dyn Device>>>> {
        self.devices.get(&id).cloned()
    }

    /// Get all devices of a specific type
    pub fn get_devices_by_type(
        &self,
        device_type: DeviceType,
    ) -> Vec<(DeviceId, Arc<Mutex<Box<dyn Device>>>)> {
        self.devices
            .iter()
            .filter(|(_, device)| {
                let dev = device.lock();
                dev.device_type() == device_type
            })
            .map(|(id, device)| (*id, device.clone()))
            .collect()
    }

    /// Initialize all devices
    pub fn initialize_all(&mut self) -> Result<(), DriverError> {
        for (id, device) in &self.devices {
            crate::println!("[DeviceManager] Initializing device: {}", id);
            let mut dev = device.lock();
            if let Err(e) = dev.initialize() {
                crate::println!(
                    "[DeviceManager] Failed to initialize device {}: {:?}",
                    id,
                    e
                );
                return Err(e);
            }
        }
        Ok(())
    }

    /// Shutdown all devices
    pub fn shutdown_all(&mut self) -> Result<(), DriverError> {
        for (id, device) in &self.devices {
            crate::println!("[DeviceManager] Shutting down device: {}", id);
            let mut dev = device.lock();
            if let Err(e) = dev.shutdown() {
                crate::println!("[DeviceManager] Failed to shutdown device {}: {:?}", id, e);
            }
        }
        Ok(())
    }

    /// Get device statistics
    pub fn device_count(&self) -> usize {
        self.devices.len()
    }

    /// List all devices
    pub fn list_devices(&self) -> Vec<(DeviceId, String, DeviceType, DeviceStatus)> {
        self.devices
            .iter()
            .map(|(id, device)| {
                let dev = device.lock();
                (*id, dev.name().to_string(), dev.device_type(), dev.status())
            })
            .collect()
    }
}

/// Device tree structure for organizing devices
pub struct DeviceTree {
    root: Option<DeviceNode>,
}

impl DeviceTree {
    pub fn new() -> Self {
        Self { root: None }
    }

    // Device tree implementation would go here
    // For now, keeping it simple
}

/// Device tree node
pub struct DeviceNode {
    pub name: String,
    pub device_id: Option<DeviceId>,
    pub children: Vec<DeviceNode>,
}

/// Global device manager instance
static DEVICE_MANAGER: Mutex<Option<DeviceManager>> = Mutex::new(None);

/// Initialize the device manager
pub fn init_device_manager() {
    let mut dm_lock = DEVICE_MANAGER.lock();
    *dm_lock = Some(DeviceManager::new());
    crate::println!("[DeviceManager] Device manager initialized");
}

/// Simple init function for drivers
pub fn init() {
    crate::println!("🔧 Initializing drivers...");
    init_device_manager();
    crate::println!("  ✅ Device drivers initialized");
}

/// Get a reference to the global device manager
pub fn get_device_manager() -> &'static Mutex<Option<DeviceManager>> {
    &DEVICE_MANAGER
}

/// Register a device driver
pub fn register_driver(driver: Box<dyn DeviceDriver>) -> Result<(), DriverError> {
    let mut dm_lock = DEVICE_MANAGER.lock();
    if let Some(dm) = dm_lock.as_mut() {
        dm.register_driver(driver)
    } else {
        Err(DriverError::NotSupported)
    }
}

/// Probe for devices
pub fn probe_devices() -> Result<Vec<DeviceId>, DriverError> {
    let mut dm_lock = DEVICE_MANAGER.lock();
    if let Some(dm) = dm_lock.as_mut() {
        dm.probe_devices()
    } else {
        Err(DriverError::NotSupported)
    }
}

/// Get a device by ID
pub fn get_device(id: DeviceId) -> Option<Arc<Mutex<Box<dyn Device>>>> {
    let dm_lock = DEVICE_MANAGER.lock();
    if let Some(dm) = dm_lock.as_ref() {
        dm.get_device(id)
    } else {
        None
    }
}

/// Initialize all devices
pub fn initialize_all_devices() -> Result<(), DriverError> {
    let mut dm_lock = DEVICE_MANAGER.lock();
    if let Some(dm) = dm_lock.as_mut() {
        dm.initialize_all()
    } else {
        Err(DriverError::NotSupported)
    }
}
