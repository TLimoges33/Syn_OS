use alloc::boxed::Box;
use alloc::collections::BTreeMap;
/// Device driver framework for SynOS kernel
/// Handles hardware abstraction and device management
use core::fmt;

/// Device types supported by the kernel
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DeviceType {
    CharacterDevice,
    BlockDevice,
    NetworkDevice,
    InputDevice,
}

/// Device operation results
pub type DeviceResult<T> = Result<T, DeviceError>;

/// Device operation errors
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DeviceError {
    NotFound,
    PermissionDenied,
    InvalidOperation,
    HardwareError,
    BufferTooSmall,
    DeviceBusy,
    DeviceNotFound,
    NotInitialized,
    Timeout,
    WouldBlock,
}

impl fmt::Display for DeviceError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            DeviceError::NotFound => write!(f, "Device not found"),
            DeviceError::PermissionDenied => write!(f, "Permission denied"),
            DeviceError::InvalidOperation => write!(f, "Invalid operation"),
            DeviceError::HardwareError => write!(f, "Hardware error"),
            DeviceError::BufferTooSmall => write!(f, "Buffer too small"),
            DeviceError::DeviceBusy => write!(f, "Device busy"),
            DeviceError::DeviceNotFound => write!(f, "Device not found"),
            DeviceError::NotInitialized => write!(f, "Device not initialized"),
            DeviceError::Timeout => write!(f, "Operation timed out"),
            DeviceError::WouldBlock => write!(f, "Operation would block"),
        }
    }
}

/// Device identifier
pub type DeviceId = u32;

/// Device management system for SynOS kernel
/// Provides hardware abstraction and device driver framework
extern crate alloc;
use alloc::vec::Vec;

pub mod console;
pub mod keyboard;
pub mod serial;

pub use console::ConsoleDriver;
pub use keyboard::KeyboardDriver;
pub use serial::SerialDriver;

/// Device driver trait that all device drivers must implement
pub trait DeviceDriver {
    /// Get device information
    fn device_info(&self) -> DeviceInfo;

    /// Initialize the device
    fn init(&mut self) -> DeviceResult<()>;

    /// Read data from device
    fn read(&mut self, buffer: &mut [u8]) -> DeviceResult<usize>;

    /// Write data to device
    fn write(&mut self, buffer: &[u8]) -> DeviceResult<usize>;

    /// Control device operations
    fn ioctl(&mut self, cmd: u32, arg: usize) -> DeviceResult<usize>;

    /// Cleanup device resources
    fn cleanup(&mut self) -> DeviceResult<()>;
}

/// Device information structure
#[derive(Debug, Clone)]
pub struct DeviceInfo {
    pub id: DeviceId,
    pub name: &'static str,
    pub device_type: DeviceType,
    pub vendor_id: u16,
    pub device_id: u16,
    pub version: u8,
    pub flags: DeviceFlags,
}

/// Device capability flags
#[derive(Debug, Clone, Copy)]
pub struct DeviceFlags {
    pub bits: u32,
}

impl DeviceFlags {
    pub const READABLE: Self = Self { bits: 1 << 0 };
    pub const WRITABLE: Self = Self { bits: 1 << 1 };
    pub const SEEKABLE: Self = Self { bits: 1 << 2 };
    pub const INTERRUPT_DRIVEN: Self = Self { bits: 1 << 3 };
    pub const DMA_CAPABLE: Self = Self { bits: 1 << 4 };

    pub fn contains(self, other: Self) -> bool {
        (self.bits & other.bits) == other.bits
    }
}

use core::ops::BitOr;

impl BitOr for DeviceFlags {
    type Output = Self;

    fn bitor(self, rhs: Self) -> Self::Output {
        DeviceFlags {
            bits: self.bits | rhs.bits,
        }
    }
}

/// Device manager for managing all system devices
pub struct DeviceManager {
    devices: BTreeMap<u32, Box<dyn DeviceDriver>>,
    next_id: u32,
}

/// Standard device IDs for easy access to common devices
#[derive(Debug, Clone)]
pub struct StandardDevices {
    pub console_id: u32,
    pub keyboard_id: u32,
    pub serial_id: u32,
}

impl DeviceManager {
    /// Create a new device manager
    pub fn new() -> Self {
        DeviceManager {
            devices: BTreeMap::new(),
            next_id: 1,
        }
    }

    /// Register a new device and return its assigned ID
    pub fn register_device(&mut self, mut driver: Box<dyn DeviceDriver>) -> DeviceResult<u32> {
        let device_id = self.next_id;
        self.next_id += 1;

        // Initialize the device
        driver.init()?;

        // Update device info with assigned ID
        let mut info = driver.device_info();
        info.id = device_id;

        self.devices.insert(device_id, driver);
        Ok(device_id)
    }

    /// Get a device by ID
    pub fn get_device(&mut self, device_id: u32) -> Option<&mut Box<dyn DeviceDriver>> {
        self.devices.get_mut(&device_id)
    }

    /// Remove a device
    pub fn unregister_device(&mut self, device_id: u32) -> DeviceResult<()> {
        if let Some(mut device) = self.devices.remove(&device_id) {
            device.cleanup()?;
            Ok(())
        } else {
            Err(DeviceError::DeviceNotFound)
        }
    }

    /// List all registered devices
    pub fn list_devices(&self) -> Vec<DeviceInfo> {
        self.devices
            .values()
            .map(|device| device.device_info())
            .collect()
    }

    /// Initialize standard system devices
    pub fn init_standard_devices(&mut self) -> DeviceResult<StandardDevices> {
        // Register console driver
        let console_driver = Box::new(ConsoleDriver::new());
        let console_id = self.register_device(console_driver)?;

        // Register keyboard driver
        let keyboard_driver = Box::new(KeyboardDriver::new());
        let keyboard_id = self.register_device(keyboard_driver)?;

        // Register serial driver (COM1)
        let serial_driver = Box::new(SerialDriver::new());
        let serial_id = self.register_device(serial_driver)?;

        Ok(StandardDevices {
            console_id,
            keyboard_id,
            serial_id,
        })
    }

    /// Write to a device
    pub fn device_write(&mut self, device_id: u32, buffer: &[u8]) -> DeviceResult<usize> {
        if let Some(device) = self.get_device(device_id) {
            device.write(buffer)
        } else {
            Err(DeviceError::DeviceNotFound)
        }
    }

    /// Read from a device
    pub fn device_read(&mut self, device_id: u32, buffer: &mut [u8]) -> DeviceResult<usize> {
        if let Some(device) = self.get_device(device_id) {
            device.read(buffer)
        } else {
            Err(DeviceError::DeviceNotFound)
        }
    }

    /// Send ioctl command to a device
    pub fn device_ioctl(&mut self, device_id: u32, cmd: u32, arg: usize) -> DeviceResult<usize> {
        if let Some(device) = self.get_device(device_id) {
            device.ioctl(cmd, arg)
        } else {
            Err(DeviceError::DeviceNotFound)
        }
    }
}

/// Global device manager instance
static mut DEVICE_MANAGER: Option<DeviceManager> = None;

/// Initialize the device management system
pub fn init() {
    unsafe {
        DEVICE_MANAGER = Some(DeviceManager::new());
    }
}

/// Get the global device manager
pub fn device_manager() -> &'static mut DeviceManager {
    unsafe {
        DEVICE_MANAGER
            .as_mut()
            .expect("Device manager not initialized")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    struct MockDevice {
        info: DeviceInfo,
    }

    impl DeviceDriver for MockDevice {
        fn device_info(&self) -> DeviceInfo {
            self.info.clone()
        }

        fn init(&mut self) -> DeviceResult<()> {
            Ok(())
        }

        fn read(&mut self, _buffer: &mut [u8]) -> DeviceResult<usize> {
            Ok(0)
        }

        fn write(&mut self, buffer: &[u8]) -> DeviceResult<usize> {
            Ok(buffer.len())
        }

        fn ioctl(&mut self, _cmd: u32, _arg: usize) -> DeviceResult<usize> {
            Ok(0)
        }

        fn cleanup(&mut self) -> DeviceResult<()> {
            Ok(())
        }
    }

    #[test]
    fn test_device_manager() {
        let mut manager = DeviceManager::new();

        let mock_device = MockDevice {
            info: DeviceInfo {
                id: 1,
                name: "mock_device",
                device_type: DeviceType::CharacterDevice,
                vendor_id: 0x1234,
                device_id: 0x5678,
                version: 1,
                flags: DeviceFlags::READABLE | DeviceFlags::WRITABLE,
            },
        };

        let device_id = manager.register_device(Box::new(mock_device)).unwrap();
        assert_eq!(device_id, 1);

        let devices = manager.list_devices();
        assert_eq!(devices.len(), 1);
        assert_eq!(devices[0].name, "mock_device");
    }
}
