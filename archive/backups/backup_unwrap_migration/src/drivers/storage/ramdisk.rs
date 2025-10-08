// RAM Disk Driver
// Simple block device that stores data in memory

use crate::drivers::{
    BlockDevice, Device, DeviceCapabilities, DeviceDriver, DeviceId, DeviceStatus, DeviceType,
    DriverError,
};
use alloc::boxed::Box;
use alloc::string::{String, ToString};
use alloc::vec::Vec;
use alloc::{format, vec};

/// RAM disk device
pub struct RamDisk {
    /// Device identification
    device_id: DeviceId,
    name: String,

    /// Storage
    data: Vec<u8>,
    block_size: u32,

    /// Status
    status: DeviceStatus,
    read_only: bool,
}

impl RamDisk {
    /// Create a new RAM disk with specified size
    pub fn new(device_id: DeviceId, size_mb: u32) -> Self {
        let block_size = 512; // Standard 512-byte blocks
        let total_size = (size_mb as usize) * 1024 * 1024;

        Self {
            device_id,
            name: format!("ramdisk{}", device_id.instance()),
            data: vec![0u8; total_size],
            block_size,
            status: DeviceStatus::Unknown,
            read_only: false,
        }
    }

    /// Create a read-only RAM disk from existing data
    pub fn new_readonly(device_id: DeviceId, data: Vec<u8>) -> Self {
        Self {
            device_id,
            name: format!("ramdisk{}", device_id.instance()),
            data,
            block_size: 512,
            status: DeviceStatus::Unknown,
            read_only: true,
        }
    }

    /// Get the underlying data (for testing)
    pub fn data(&self) -> &[u8] {
        &self.data
    }
}

impl Device for RamDisk {
    fn device_type(&self) -> DeviceType {
        DeviceType::BlockDevice
    }

    fn device_id(&self) -> DeviceId {
        self.device_id
    }

    fn name(&self) -> &str {
        &self.name
    }

    fn capabilities(&self) -> DeviceCapabilities {
        DeviceCapabilities {
            can_read: true,
            can_write: !self.read_only,
            can_seek: true,
            supports_dma: false,
            supports_interrupts: false,
            hot_pluggable: false,
        }
    }

    fn initialize(&mut self) -> Result<(), DriverError> {
        self.status = DeviceStatus::Ready;
        crate::println!(
            "[RamDisk] Initialized {} ({} blocks, {} bytes)",
            self.name,
            self.block_count(),
            self.capacity()
        );
        Ok(())
    }

    fn shutdown(&mut self) -> Result<(), DriverError> {
        self.status = DeviceStatus::Offline;
        crate::println!("[RamDisk] Shutdown {}", self.name);
        Ok(())
    }

    fn status(&self) -> DeviceStatus {
        self.status
    }
}

impl BlockDevice for RamDisk {
    fn block_size(&self) -> u32 {
        self.block_size
    }

    fn block_count(&self) -> u64 {
        (self.data.len() / self.block_size as usize) as u64
    }

    fn read_blocks(
        &mut self,
        start_block: u64,
        block_count: u32,
        buffer: &mut [u8],
    ) -> Result<(), DriverError> {
        if self.status != DeviceStatus::Ready {
            return Err(DriverError::HardwareError);
        }

        let start_byte = (start_block * self.block_size as u64) as usize;
        let bytes_to_read = (block_count * self.block_size) as usize;

        // Bounds checking
        if start_byte >= self.data.len() {
            return Err(DriverError::InvalidParameter);
        }

        if start_byte + bytes_to_read > self.data.len() {
            return Err(DriverError::InvalidParameter);
        }

        if buffer.len() < bytes_to_read {
            return Err(DriverError::InvalidParameter);
        }

        // Copy data
        buffer[..bytes_to_read].copy_from_slice(&self.data[start_byte..start_byte + bytes_to_read]);

        Ok(())
    }

    fn write_blocks(
        &mut self,
        start_block: u64,
        block_count: u32,
        data: &[u8],
    ) -> Result<(), DriverError> {
        if self.status != DeviceStatus::Ready {
            return Err(DriverError::HardwareError);
        }

        if self.read_only {
            return Err(DriverError::PermissionDenied);
        }

        let start_byte = (start_block * self.block_size as u64) as usize;
        let bytes_to_write = (block_count * self.block_size) as usize;

        // Bounds checking
        if start_byte >= self.data.len() {
            return Err(DriverError::InvalidParameter);
        }

        if start_byte + bytes_to_write > self.data.len() {
            return Err(DriverError::InvalidParameter);
        }

        if data.len() < bytes_to_write {
            return Err(DriverError::InvalidParameter);
        }

        // Copy data
        self.data[start_byte..start_byte + bytes_to_write].copy_from_slice(&data[..bytes_to_write]);

        Ok(())
    }

    fn flush(&mut self) -> Result<(), DriverError> {
        // RAM disk doesn't need flushing
        Ok(())
    }

    fn is_read_only(&self) -> bool {
        self.read_only
    }
}

/// RAM disk driver
pub struct RamDiskDriver {
    name: String,
}

impl RamDiskDriver {
    pub fn new() -> Self {
        Self {
            name: "ramdisk".to_string(),
        }
    }
}

impl DeviceDriver for RamDiskDriver {
    fn name(&self) -> &str {
        &self.name
    }

    fn supported_devices(&self) -> alloc::vec::Vec<(u16, u16)> {
        vec![(0x0000, 0x0001)] // Vendor ID 0, Device ID 1 for RAM disk
    }

    fn probe(&self, device_id: DeviceId) -> Result<Box<dyn Device>, DriverError> {
        // Check if this is a RAM disk device
        if device_id.vendor() == 0x0000 && device_id.device() == 0x0001 {
            // Create a 16MB RAM disk
            let ramdisk = RamDisk::new(device_id, 16);
            Ok(Box::new(ramdisk))
        } else {
            Err(DriverError::NotSupported)
        }
    }

    fn version(&self) -> (u32, u32, u32) {
        (1, 0, 0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ramdisk_creation() {
        let device_id = DeviceId::new(0x0000, 0x0001, 0);
        let mut ramdisk = RamDisk::new(device_id, 1); // 1MB

        assert_eq!(ramdisk.device_type(), DeviceType::BlockDevice);
        assert_eq!(ramdisk.device_id(), device_id);
        assert_eq!(ramdisk.block_size(), 512);
        assert_eq!(ramdisk.capacity(), 1024 * 1024);
        assert!(!ramdisk.is_read_only());

        // Initialize
        assert!(ramdisk.initialize().is_ok());
        assert_eq!(ramdisk.status(), DeviceStatus::Ready);
    }

    #[test]
    fn test_ramdisk_read_write() {
        let device_id = DeviceId::new(0x0000, 0x0001, 0);
        let mut ramdisk = RamDisk::new(device_id, 1); // 1MB
        ramdisk.initialize().unwrap();

        // Test data
        let test_data = [0x42; 512];
        let mut read_buffer = [0u8; 512];

        // Write one block
        assert!(ramdisk.write_blocks(0, 1, &test_data).is_ok());

        // Read it back
        assert!(ramdisk.read_blocks(0, 1, &mut read_buffer).is_ok());
        assert_eq!(read_buffer, test_data);

        // Test bounds checking
        let large_buffer = [0u8; 1024];
        assert!(ramdisk.write_blocks(1000000, 1, &large_buffer).is_err());
    }

    #[test]
    fn test_ramdisk_readonly() {
        let device_id = DeviceId::new(0x0000, 0x0001, 0);
        let data = vec![0x55; 1024];
        let mut ramdisk = RamDisk::new_readonly(device_id, data);
        ramdisk.initialize().unwrap();

        assert!(ramdisk.is_read_only());

        // Should be able to read
        let mut read_buffer = [0u8; 512];
        assert!(ramdisk.read_blocks(0, 1, &mut read_buffer).is_ok());
        assert_eq!(read_buffer, [0x55; 512]);

        // Should not be able to write
        let write_data = [0x42; 512];
        assert_eq!(
            ramdisk.write_blocks(0, 1, &write_data),
            Err(DriverError::PermissionDenied)
        );
    }

    #[test]
    fn test_ramdisk_driver() {
        let driver = RamDiskDriver::new();
        assert_eq!(driver.name(), "ramdisk");
        assert_eq!(driver.version(), (1, 0, 0));

        let device_id = DeviceId::new(0x0000, 0x0001, 0);
        let device = driver.probe(device_id).unwrap();
        assert_eq!(device.device_type(), DeviceType::BlockDevice);
        assert_eq!(device.device_id(), device_id);

        // Test unsupported device
        let bad_id = DeviceId::new(0x1234, 0x5678, 0);
        assert!(driver.probe(bad_id).is_err());
    }
}

/// Initialize the RAM disk driver
pub fn init_ramdisk_driver() {
    use crate::drivers::register_driver;

    let driver = Box::new(RamDiskDriver::new());
    if let Err(e) = register_driver(driver) {
        crate::println!("[RamDisk] Failed to register driver: {:?}", e);
    } else {
        crate::println!("[RamDisk] Driver registered successfully");
    }
}
