// Storage Device Drivers Module
// Contains all storage-related device drivers

pub mod ramdisk;

// Re-export common types
pub use ramdisk::RamDiskDriver;

use crate::drivers::{DeviceDriver, DriverError};
use alloc::boxed::Box;
use alloc::vec::Vec;

/// Initialize all storage drivers
pub fn init_storage_drivers() -> Result<Vec<Box<dyn DeviceDriver>>, DriverError> {
    let mut drivers = Vec::new();

    // Register RAM disk driver
    drivers.push(Box::new(RamDiskDriver::new()) as Box<dyn DeviceDriver>);

    crate::println!("[Storage] Initialized {} storage drivers", drivers.len());
    Ok(drivers)
}

/// Storage device utilities
pub mod utils {
    use crate::drivers::{BlockDevice, DriverError};
    use alloc::vec;
    use alloc::vec::Vec;

    /// Read entire disk to buffer (for small disks)
    pub fn read_entire_disk(
        device: &mut dyn BlockDevice,
        buffer: &mut Vec<u8>,
    ) -> Result<(), DriverError> {
        let total_blocks = device.block_count();
        let block_size = device.block_size() as usize;
        let total_size = total_blocks as usize * block_size;

        if buffer.len() < total_size {
            buffer.resize(total_size, 0);
        }

        let mut current_block = 0u64;
        let mut buffer_offset = 0usize;

        while current_block < total_blocks {
            let blocks_remaining = total_blocks - current_block;
            let blocks_to_read = core::cmp::min(blocks_remaining, 256) as u32; // Read in 128KB chunks

            device.read_blocks(
                current_block,
                blocks_to_read,
                &mut buffer[buffer_offset..buffer_offset + (blocks_to_read as usize * block_size)],
            )?;

            current_block += blocks_to_read as u64;
            buffer_offset += blocks_to_read as usize * block_size;
        }

        Ok(())
    }

    /// Write buffer to entire disk (for small disks)
    pub fn write_entire_disk(device: &mut dyn BlockDevice, data: &[u8]) -> Result<(), DriverError> {
        let total_blocks = device.block_count();
        let block_size = device.block_size() as usize;
        let total_size = total_blocks as usize * block_size;

        if data.len() != total_size {
            return Err(DriverError::InvalidParameter);
        }

        let mut current_block = 0u64;
        let mut data_offset = 0usize;

        while current_block < total_blocks {
            let blocks_remaining = total_blocks - current_block;
            let blocks_to_write = core::cmp::min(blocks_remaining, 256) as u32; // Write in 128KB chunks

            device.write_blocks(
                current_block,
                blocks_to_write,
                &data[data_offset..data_offset + (blocks_to_write as usize * block_size)],
            )?;

            current_block += blocks_to_write as u64;
            data_offset += blocks_to_write as usize * block_size;
        }

        device.flush()?;
        Ok(())
    }

    /// Zero out a range of blocks
    pub fn zero_blocks(
        device: &mut dyn BlockDevice,
        start_block: u64,
        block_count: u64,
    ) -> Result<(), DriverError> {
        let block_size = device.block_size() as usize;
        let zero_buffer = vec![0u8; block_size * 256]; // 128KB zero buffer

        let mut current_block = start_block;
        let end_block = start_block + block_count;

        while current_block < end_block {
            let blocks_remaining = end_block - current_block;
            let blocks_to_zero = core::cmp::min(blocks_remaining, 256) as u32;

            device.write_blocks(
                current_block,
                blocks_to_zero,
                &zero_buffer[..blocks_to_zero as usize * block_size],
            )?;

            current_block += blocks_to_zero as u64;
        }

        Ok(())
    }

    /// Verify disk integrity by writing and reading test patterns
    pub fn test_disk_integrity(device: &mut dyn BlockDevice) -> Result<bool, DriverError> {
        if device.is_read_only() {
            return Ok(true); // Can't test read-only devices
        }

        let block_size = device.block_size() as usize;
        let test_patterns = [
            vec![0x00; block_size], // All zeros
            vec![0xFF; block_size], // All ones
            vec![0xAA; block_size], // Alternating pattern
            vec![0x55; block_size], // Inverse alternating
        ];

        let mut read_buffer = vec![0u8; block_size];

        // Test first block only (to avoid destroying data)
        for (i, pattern) in test_patterns.iter().enumerate() {
            // Write pattern
            device.write_blocks(0, 1, pattern)?;
            device.flush()?;

            // Read back
            device.read_blocks(0, 1, &mut read_buffer)?;

            // Verify
            if read_buffer != *pattern {
                crate::println!("[Storage] Integrity test failed at pattern {}", i);
                return Ok(false);
            }
        }

        crate::println!("[Storage] Disk integrity test passed");
        Ok(true)
    }
}
