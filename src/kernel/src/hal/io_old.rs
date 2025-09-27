/// I/O controller for hardware abstraction layer
/// Manages I/O ports, memory-mapped I/O, and interrupt controllers

use crate::hal::{
    IoController, IoPort, IoWidth, IoDeviceType, MemoryMappedRegion, 
    InterruptController, InterruptControllerType, InterruptMode
};
use alloc::collections::BTreeMap;
use alloc::vec::Vec;

impl IoController {
    /// Create a new I/O controller
    pub fn new() -> Self {
        Self {
            port_map: BTreeMap::new(),
            memory_mapped_regions: Vec::new(),
            interrupt_controllers: Vec::new(),
        }
    }

    /// Register standard I/O ports
    pub fn register_standard_ports(&mut self) {
        // Legacy PC I/O ports
        self.register_port(IoPort {
            port: 0x20,
            width: IoWidth::Byte,
            device_type: IoDeviceType::PIC,
            description: "Master PIC Command",
        });

        self.register_port(IoPort {
            port: 0x21,
            width: IoWidth::Byte,
            device_type: IoDeviceType::PIC,
            description: "Master PIC Data",
        });

        self.register_port(IoPort {
            port: 0xA0,
            width: IoWidth::Byte,
            device_type: IoDeviceType::PIC,
            description: "Slave PIC Command",
        });

        self.register_port(IoPort {
            port: 0xA1,
            width: IoWidth::Byte,
            device_type: IoDeviceType::PIC,
            description: "Slave PIC Data",
        });

        // Programmable Interval Timer
        self.register_port(IoPort {
            port: 0x40,
            width: IoWidth::Byte,
            device_type: IoDeviceType::PIT,
            description: "PIT Channel 0",
        });

        self.register_port(IoPort {
            port: 0x41,
            width: IoWidth::Byte,
            device_type: IoDeviceType::PIT,
            description: "PIT Channel 1",
        });

        self.register_port(IoPort {
            port: 0x42,
            width: IoWidth::Byte,
            device_type: IoDeviceType::PIT,
            description: "PIT Channel 2",
        });

        self.register_port(IoPort {
            port: 0x43,
            width: IoWidth::Byte,
            device_type: IoDeviceType::PIT,
            description: "PIT Command",
        });

        // Real-Time Clock
        self.register_port(IoPort {
            port: 0x70,
            width: IoWidth::Byte,
            device_type: IoDeviceType::RTC,
            description: "RTC Index",
        });

        self.register_port(IoPort {
            port: 0x71,
            width: IoWidth::Byte,
            device_type: IoDeviceType::RTC,
            description: "RTC Data",
        });

        // Keyboard Controller
        self.register_port(IoPort {
            port: 0x60,
            width: IoWidth::Byte,
            device_type: IoDeviceType::Keyboard,
            description: "Keyboard Data",
        });

        self.register_port(IoPort {
            port: 0x64,
            width: IoWidth::Byte,
            device_type: IoDeviceType::Keyboard,
            description: "Keyboard Status/Command",
        });

        // Serial ports
        for i in 0..4 {
            let base_port = match i {
                0 => 0x3F8, // COM1
                1 => 0x2F8, // COM2
                2 => 0x3E8, // COM3
                3 => 0x2E8, // COM4
                _ => continue,
            };

            for offset in 0..8 {
                self.register_port(IoPort {
                    port: base_port + offset,
                    width: IoWidth::Byte,
                    device_type: IoDeviceType::Serial,
                    description: "Serial Port",
                });
            }
        }

        // Parallel ports
        self.register_port(IoPort {
            port: 0x378,
            width: IoWidth::Byte,
            device_type: IoDeviceType::Parallel,
            description: "LPT1 Data",
        });

        self.register_port(IoPort {
            port: 0x379,
            width: IoWidth::Byte,
            device_type: IoDeviceType::Parallel,
            description: "LPT1 Status",
        });

        self.register_port(IoPort {
            port: 0x37A,
            width: IoWidth::Byte,
            device_type: IoDeviceType::Parallel,
            description: "LPT1 Control",
        });

        // VGA ports
        self.register_port(IoPort {
            port: 0x3C0,
            width: IoWidth::Byte,
            device_type: IoDeviceType::Graphics,
            description: "VGA Attribute Controller",
        });

        self.register_port(IoPort {
            port: 0x3D4,
            width: IoWidth::Byte,
            device_type: IoDeviceType::Graphics,
            description: "VGA CRT Controller Index",
        });

        self.register_port(IoPort {
            port: 0x3D5,
            width: IoWidth::Byte,
            device_type: IoDeviceType::Graphics,
            description: "VGA CRT Controller Data",
        });
    }

    /// Register an I/O port
    pub fn register_port(&mut self, port: IoPort) {
        self.port_map.insert(port.port, port);
    }

    /// Register a memory-mapped I/O region
    pub fn register_mmio_region(&mut self, region: MemoryMappedRegion) {
        self.memory_mapped_regions.push(region);
    }

    /// Register an interrupt controller
    pub fn register_interrupt_controller(&mut self, controller: InterruptController) {
        self.interrupt_controllers.push(controller);
    }

    /// Read from an I/O port
    pub fn read_port(&self, port: u16, width: IoWidth) -> Result<u32, IoError> {
        if !self.port_map.contains_key(&port) {
            return Err(IoError::UnregisteredPort);
        }

        unsafe {
            match width {
                IoWidth::Byte => Ok(inb(port) as u32),
                IoWidth::Word => Ok(inw(port) as u32),
                IoWidth::DWord => Ok(inl(port)),
            }
        }
    }

    /// Write to an I/O port
    pub fn write_port(&self, port: u16, value: u32, width: IoWidth) -> Result<(), IoError> {
        if !self.port_map.contains_key(&port) {
            return Err(IoError::UnregisteredPort);
        }

        unsafe {
            match width {
                IoWidth::Byte => outb(port, value as u8),
                IoWidth::Word => outw(port, value as u16),
                IoWidth::DWord => outl(port, value),
            }
        }

        Ok(())
    }

    /// Read from memory-mapped I/O
    pub fn read_mmio(&self, address: u64, width: IoWidth) -> Result<u32, IoError> {
        // Check if address is in a registered MMIO region
        if !self.is_mmio_region(address) {
            return Err(IoError::InvalidMmioAddress);
        }

        unsafe {
            match width {
                IoWidth::Byte => Ok(core::ptr::read_volatile(address as *const u8) as u32),
                IoWidth::Word => Ok(core::ptr::read_volatile(address as *const u16) as u32),
                IoWidth::DWord => Ok(core::ptr::read_volatile(address as *const u32)),
            }
        }
    }

    /// Write to memory-mapped I/O
    pub fn write_mmio(&self, address: u64, value: u32, width: IoWidth) -> Result<(), IoError> {
        // Check if address is in a registered MMIO region
        if !self.is_mmio_region(address) {
            return Err(IoError::InvalidMmioAddress);
        }

        // Check if region is writable
        if !self.is_mmio_writable(address) {
            return Err(IoError::ReadOnlyRegion);
        }

        unsafe {
            match width {
                IoWidth::Byte => core::ptr::write_volatile(address as *mut u8, value as u8),
                IoWidth::Word => core::ptr::write_volatile(address as *mut u16, value as u16),
                IoWidth::DWord => core::ptr::write_volatile(address as *mut u32, value),
            }
        }

        Ok(())
    }

    /// Check if address is in a registered MMIO region
    fn is_mmio_region(&self, address: u64) -> bool {
        self.memory_mapped_regions.iter().any(|region| {
            address >= region.base_address && address < region.base_address + region.size
        })
    }

    /// Check if MMIO region is writable
    fn is_mmio_writable(&self, address: u64) -> bool {
        self.memory_mapped_regions.iter()
            .find(|region| {
                address >= region.base_address && address < region.base_address + region.size
            })
            .map(|region| region.writable)
            .unwrap_or(false)
    }

    /// Get I/O port information
    pub fn get_port_info(&self, port: u16) -> Option<&IoPort> {
        self.port_map.get(&port)
    }

    /// List all registered ports
    pub fn list_ports(&self) -> Vec<&IoPort> {
        self.port_map.values().collect()
    }

    /// List all MMIO regions
    pub fn list_mmio_regions(&self) -> &[MemoryMappedRegion] {
        &self.memory_mapped_regions
    }

    /// List all interrupt controllers
    pub fn list_interrupt_controllers(&self) -> &[InterruptController] {
        &self.interrupt_controllers
    }

    /// Detect and initialize interrupt controllers
    pub fn detect_interrupt_controllers(&mut self) -> Result<(), IoError> {
        // Detect legacy PIC
        if self.detect_pic() {
            self.register_interrupt_controller(InterruptController {
                controller_type: InterruptControllerType::PIC8259,
                base_address: 0x20, // Master PIC
                interrupt_count: 8,
                supported_modes: vec![InterruptMode::Fixed, InterruptMode::ExtINT],
            });

            self.register_interrupt_controller(InterruptController {
                controller_type: InterruptControllerType::PIC8259,
                base_address: 0xA0, // Slave PIC
                interrupt_count: 8,
                supported_modes: vec![InterruptMode::Fixed, InterruptMode::ExtINT],
            });
        }

        // Detect APIC
        if self.detect_apic() {
            self.register_interrupt_controller(InterruptController {
                controller_type: InterruptControllerType::APIC,
                base_address: 0xFEE00000, // Default APIC base
                interrupt_count: 256,
                supported_modes: vec![
                    InterruptMode::Fixed,
                    InterruptMode::LowestPriority,
                    InterruptMode::SMI,
                    InterruptMode::NMI,
                    InterruptMode::INIT,
                    InterruptMode::Startup,
                ],
            });
        }

        // Detect I/O APIC
        if self.detect_ioapic() {
            self.register_interrupt_controller(InterruptController {
                controller_type: InterruptControllerType::IOAPIC,
                base_address: 0xFEC00000, // Default I/O APIC base
                interrupt_count: 24, // Typical I/O APIC
                supported_modes: vec![
                    InterruptMode::Fixed,
                    InterruptMode::LowestPriority,
                    InterruptMode::NMI,
                    InterruptMode::ExtINT,
                ],
            });
        }

        Ok(())
    }

    /// Detect legacy PIC
    fn detect_pic(&self) -> bool {
        // Try to read from PIC registers
        unsafe {
            let master_imr = inb(0x21);
            let slave_imr = inb(0xA1);
            
            // If we can read meaningful values, PIC is present
            master_imr != 0xFF || slave_imr != 0xFF
        }
    }

    /// Detect APIC
    fn detect_apic(&self) -> bool {
        // Check CPUID for APIC support
        let cpuid_result = super::cpu::cpuid(1);
        (cpuid_result.edx & (1 << 9)) != 0
    }

    /// Detect I/O APIC
    fn detect_ioapic(&self) -> bool {
        // I/O APIC detection typically requires ACPI tables
        // For now, assume present if APIC is present
        self.detect_apic()
    }
}

/// I/O-related errors
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum IoError {
    UnregisteredPort,
    InvalidMmioAddress,
    ReadOnlyRegion,
    PermissionDenied,
    DeviceNotFound,
    DeviceBusy,
    TimeoutError,
    InvalidWidth,
}

impl core::fmt::Display for IoError {
    fn fmt(&self, f: &mut core::fmt::Formatter) -> core::fmt::Result {
        match self {
            IoError::UnregisteredPort => write!(f, "Unregistered I/O port"),
            IoError::InvalidMmioAddress => write!(f, "Invalid MMIO address"),
            IoError::ReadOnlyRegion => write!(f, "Read-only memory region"),
            IoError::PermissionDenied => write!(f, "I/O permission denied"),
            IoError::DeviceNotFound => write!(f, "Device not found"),
            IoError::DeviceBusy => write!(f, "Device busy"),
            IoError::TimeoutError => write!(f, "I/O timeout"),
            IoError::InvalidWidth => write!(f, "Invalid I/O width"),
        }
    }
}

/// Low-level I/O port functions
unsafe fn inb(port: u16) -> u8 {
    let result: u8;
    core::arch::asm!(
        "in al, dx",
        out("al") result,
        in("dx") port,
        options(nostack, preserves_flags)
    );
    result
}

unsafe fn inw(port: u16) -> u16 {
    let result: u16;
    core::arch::asm!(
        "in ax, dx",
        out("ax") result,
        in("dx") port,
        options(nostack, preserves_flags)
    );
    result
}

unsafe fn inl(port: u16) -> u32 {
    let result: u32;
    core::arch::asm!(
        "in eax, dx",
        out("eax") result,
        in("dx") port,
        options(nostack, preserves_flags)
    );
    result
}

unsafe fn outb(port: u16, value: u8) {
    core::arch::asm!(
        "out dx, al",
        in("dx") port,
        in("al") value,
        options(nostack, preserves_flags)
    );
}

unsafe fn outw(port: u16, value: u16) {
    core::arch::asm!(
        "out dx, ax",
        in("dx") port,
        in("ax") value,
        options(nostack, preserves_flags)
    );
}

unsafe fn outl(port: u16, value: u32) {
    core::arch::asm!(
        "out dx, eax",
        in("dx") port,
        in("eax") value,
        options(nostack, preserves_flags)
    );
}

/// I/O port access with timing delays
pub mod delayed_io {
    use super::*;

    /// Read with I/O delay
    pub fn inb_delay(port: u16) -> u8 {
        unsafe {
            let result = inb(port);
            io_delay();
            result
        }
    }

    /// Write with I/O delay
    pub fn outb_delay(port: u16, value: u8) {
        unsafe {
            outb(port, value);
            io_delay();
        }
    }

    /// I/O delay using port 0x80
    fn io_delay() {
        unsafe {
            outb(0x80, 0);
        }
    }
}

/// DMA (Direct Memory Access) support
pub mod dma {
    use super::*;

    /// DMA channel information
    #[derive(Debug, Clone)]
    pub struct DmaChannel {
        pub channel: u8,
        pub mode: DmaMode,
        pub buffer_address: u64,
        pub buffer_size: u32,
        pub transfer_count: u32,
    }

    /// DMA transfer modes
    #[derive(Debug, Clone, Copy, PartialEq, Eq)]
    pub enum DmaMode {
        Read,
        Write,
        Verify,
        Invalid,
    }

    /// Initialize DMA controller
    pub fn init_dma_controller() -> Result<(), IoError> {
        // Reset DMA controllers
        unsafe {
            outb(0x0D, 0); // Master clear DMA 1
            outb(0xDA, 0); // Master clear DMA 2
        }

        // Unmask all DMA channels
        unsafe {
            outb(0x0A, 0); // Unmask DMA channels 0-3
            outb(0xD4, 0); // Unmask DMA channels 4-7
        }

        Ok(())
    }

    /// Set up DMA transfer
    pub fn setup_dma_transfer(channel: &DmaChannel) -> Result<(), IoError> {
        if channel.channel > 7 {
            return Err(IoError::InvalidWidth);
        }

        // Disable the DMA channel
        mask_dma_channel(channel.channel);

        // Set transfer mode
        set_dma_mode(channel.channel, channel.mode);

        // Set buffer address and size
        set_dma_address(channel.channel, channel.buffer_address as u32);
        set_dma_count(channel.channel, channel.transfer_count - 1);

        // Enable the DMA channel
        unmask_dma_channel(channel.channel);

        Ok(())
    }

    /// Mask (disable) a DMA channel
    fn mask_dma_channel(channel: u8) {
        let (mask_port, mask_value) = if channel < 4 {
            (0x0A, 0x04 | channel)
        } else {
            (0xD4, 0x04 | (channel - 4))
        };

        unsafe {
            outb(mask_port, mask_value);
        }
    }

    /// Unmask (enable) a DMA channel
    fn unmask_dma_channel(channel: u8) {
        let (mask_port, mask_value) = if channel < 4 {
            (0x0A, channel)
        } else {
            (0xD4, channel - 4)
        };

        unsafe {
            outb(mask_port, mask_value);
        }
    }

    /// Set DMA transfer mode
    fn set_dma_mode(channel: u8, mode: DmaMode) {
        let mode_value = match mode {
            DmaMode::Read => 0x44,   // Single transfer, increment, memory to I/O
            DmaMode::Write => 0x48,  // Single transfer, increment, I/O to memory
            DmaMode::Verify => 0x40, // Verify transfer
            DmaMode::Invalid => 0x00,
        };

        let (mode_port, final_mode) = if channel < 4 {
            (0x0B, mode_value | channel)
        } else {
            (0xD6, mode_value | (channel - 4))
        };

        unsafe {
            outb(mode_port, final_mode);
        }
    }

    /// Set DMA buffer address
    fn set_dma_address(channel: u8, address: u32) {
        let (addr_port, page_port) = match channel {
            0 => (0x00, 0x87),
            1 => (0x02, 0x83),
            2 => (0x04, 0x81),
            3 => (0x06, 0x82),
            4 => (0xC0, 0x8F),
            5 => (0xC4, 0x8B),
            6 => (0xC8, 0x89),
            7 => (0xCC, 0x8A),
            _ => return,
        };

        unsafe {
            // Set low and high address bytes
            outb(addr_port, (address & 0xFF) as u8);
            outb(addr_port, ((address >> 8) & 0xFF) as u8);
            
            // Set page register
            outb(page_port, ((address >> 16) & 0xFF) as u8);
        }
    }

    /// Set DMA transfer count
    fn set_dma_count(channel: u8, count: u32) {
        let count_port = match channel {
            0 => 0x01,
            1 => 0x03,
            2 => 0x05,
            3 => 0x07,
            4 => 0xC2,
            5 => 0xC6,
            6 => 0xCA,
            7 => 0xCE,
            _ => return,
        };

        unsafe {
            outb(count_port, (count & 0xFF) as u8);
            outb(count_port, ((count >> 8) & 0xFF) as u8);
        }
    }
}
