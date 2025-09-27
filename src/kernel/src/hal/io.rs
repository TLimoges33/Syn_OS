/// I/O controller for hardware abstraction layer
/// Manages I/O ports, memory-mapped I/O, and DMA channels

use crate::hal::{
    IoController, IoPortRange, MemoryMappedRange, DmaChannel, DmaWidth, DmaMode, HalError
};
use alloc::vec::Vec;

impl IoController {
    /// Create a new I/O controller
    pub fn new() -> Self {
        let mut controller = Self {
            port_ranges: Vec::new(),
            memory_mapped_ranges: Vec::new(),
            dma_channels: Vec::new(),
        };

        // Initialize standard I/O ports and devices
        controller.init_standard_ports();
        controller.init_dma_channels();
        controller.init_mmio_regions();

        controller
    }

    /// Initialize standard I/O port ranges
    fn init_standard_ports(&mut self) {
        // Legacy PC I/O ports
        self.port_ranges.extend_from_slice(&[
            IoPortRange {
                base_port: 0x20,
                size: 2,
                description: "Master PIC (8259A)",
            },
            IoPortRange {
                base_port: 0xA0,
                size: 2,
                description: "Slave PIC (8259A)",
            },
            IoPortRange {
                base_port: 0x40,
                size: 4,
                description: "System Timer (8254)",
            },
            IoPortRange {
                base_port: 0x60,
                size: 1,
                description: "Keyboard Controller",
            },
            IoPortRange {
                base_port: 0x64,
                size: 1,
                description: "Keyboard Status",
            },
            IoPortRange {
                base_port: 0x70,
                size: 2,
                description: "CMOS/RTC",
            },
            IoPortRange {
                base_port: 0x80,
                size: 1,
                description: "POST Diagnostic",
            },
            IoPortRange {
                base_port: 0x92,
                size: 1,
                description: "System Control Port A",
            },
            IoPortRange {
                base_port: 0x3F8,
                size: 8,
                description: "Serial Port COM1",
            },
            IoPortRange {
                base_port: 0x2F8,
                size: 8,
                description: "Serial Port COM2",
            },
            IoPortRange {
                base_port: 0x378,
                size: 8,
                description: "Parallel Port LPT1",
            },
            IoPortRange {
                base_port: 0x1F0,
                size: 8,
                description: "Primary ATA/IDE",
            },
            IoPortRange {
                base_port: 0x170,
                size: 8,
                description: "Secondary ATA/IDE",
            },
            IoPortRange {
                base_port: 0x3F6,
                size: 1,
                description: "Primary ATA Control",
            },
            IoPortRange {
                base_port: 0x376,
                size: 1,
                description: "Secondary ATA Control",
            },
        ]);
    }

    /// Initialize DMA channels
    fn init_dma_channels(&mut self) {
        // Standard ISA DMA channels
        for i in 0..8 {
            let width = if i < 4 { DmaWidth::Bits8 } else { DmaWidth::Bits16 };
            
            self.dma_channels.push(DmaChannel {
                channel: i,
                width,
                mode: DmaMode::Single,
            });
        }
    }

    /// Initialize memory-mapped I/O regions
    fn init_mmio_regions(&mut self) {
        // Common MMIO regions
        self.memory_mapped_ranges.extend_from_slice(&[
            MemoryMappedRange {
                base_address: 0xA0000,
                size: 0x20000,
                device_type: "VGA Graphics Memory",
            },
            MemoryMappedRange {
                base_address: 0xB0000,
                size: 0x8000,
                device_type: "VGA Monochrome Text",
            },
            MemoryMappedRange {
                base_address: 0xB8000,
                size: 0x8000,
                device_type: "VGA Color Text",
            },
            MemoryMappedRange {
                base_address: 0xC0000,
                size: 0x40000,
                device_type: "ROM BIOS",
            },
            MemoryMappedRange {
                base_address: 0xFEC00000,
                size: 0x1000,
                device_type: "I/O APIC",
            },
            MemoryMappedRange {
                base_address: 0xFED00000,
                size: 0x1000,
                device_type: "HPET",
            },
            MemoryMappedRange {
                base_address: 0xFEE00000,
                size: 0x1000,
                device_type: "Local APIC",
            },
        ]);
    }

    /// Read from I/O port (8-bit)
    pub unsafe fn inb(&self, port: u16) -> u8 {
        let value: u8;
        core::arch::asm!(
            "in al, dx",
            out("al") value,
            in("dx") port,
            options(nomem, nostack, preserves_flags)
        );
        value
    }

    /// Read from I/O port (16-bit)
    pub unsafe fn inw(&self, port: u16) -> u16 {
        let value: u16;
        core::arch::asm!(
            "in ax, dx",
            out("ax") value,
            in("dx") port,
            options(nomem, nostack, preserves_flags)
        );
        value
    }

    /// Read from I/O port (32-bit)
    pub unsafe fn inl(&self, port: u16) -> u32 {
        let value: u32;
        core::arch::asm!(
            "in eax, dx",
            out("eax") value,
            in("dx") port,
            options(nomem, nostack, preserves_flags)
        );
        value
    }

    /// Write to I/O port (8-bit)
    pub unsafe fn outb(&self, port: u16, value: u8) {
        core::arch::asm!(
            "out dx, al",
            in("dx") port,
            in("al") value,
            options(nomem, nostack, preserves_flags)
        );
    }

    /// Write to I/O port (16-bit)
    pub unsafe fn outw(&self, port: u16, value: u16) {
        core::arch::asm!(
            "out dx, ax",
            in("dx") port,
            in("ax") value,
            options(nomem, nostack, preserves_flags)
        );
    }

    /// Write to I/O port (32-bit)
    pub unsafe fn outl(&self, port: u16, value: u32) {
        core::arch::asm!(
            "out dx, eax",
            in("dx") port,
            in("eax") value,
            options(nomem, nostack, preserves_flags)
        );
    }

    /// Check if port is registered
    pub fn is_port_registered(&self, port: u16) -> bool {
        self.port_ranges.iter().any(|range| {
            port >= range.base_port && port < range.base_port + range.size
        })
    }

    /// Get port range description
    pub fn get_port_description(&self, port: u16) -> Option<&'static str> {
        self.port_ranges.iter()
            .find(|range| port >= range.base_port && port < range.base_port + range.size)
            .map(|range| range.description)
    }

    /// Get DMA channel info
    pub fn get_dma_channel(&self, channel: u8) -> Option<&DmaChannel> {
        self.dma_channels.iter().find(|dma| dma.channel == channel)
    }

    /// Configure DMA channel
    pub fn configure_dma(&mut self, channel: u8, mode: DmaMode) -> Result<(), HalError> {
        if let Some(dma) = self.dma_channels.iter_mut().find(|dma| dma.channel == channel) {
            dma.mode = mode;
            Ok(())
        } else {
            Err(HalError::InvalidOperation)
        }
    }

    /// Get memory-mapped region info
    pub fn get_mmio_region(&self, address: u64) -> Option<&MemoryMappedRange> {
        self.memory_mapped_ranges.iter()
            .find(|range| address >= range.base_address && address < range.base_address + range.size)
    }

    /// Initialize interrupt controllers
    pub fn init_interrupt_controllers(&mut self) -> Result<(), HalError> {
        // Initialize PIC (8259A) - Legacy interrupt controller
        self.init_pic()?;
        
        // TODO: Initialize APIC if available
        // self.init_apic()?;
        
        Ok(())
    }

    /// Initialize PIC (8259A)
    fn init_pic(&self) -> Result<(), HalError> {
        unsafe {
            // Initialize master PIC
            self.outb(0x20, 0x11); // ICW1: Initialize
            self.outb(0x21, 0x20); // ICW2: Master PIC vector offset (32)
            self.outb(0x21, 0x04); // ICW3: Tell master PIC there's a slave at IRQ2
            self.outb(0x21, 0x01); // ICW4: 8086 mode

            // Initialize slave PIC
            self.outb(0xA0, 0x11); // ICW1: Initialize
            self.outb(0xA1, 0x28); // ICW2: Slave PIC vector offset (40)
            self.outb(0xA1, 0x02); // ICW3: Tell slave PIC its cascade identity
            self.outb(0xA1, 0x01); // ICW4: 8086 mode

            // Mask all interrupts initially
            self.outb(0x21, 0xFF);
            self.outb(0xA1, 0xFF);
        }
        
        Ok(())
    }

    /// Enable interrupt on PIC
    pub fn enable_irq(&self, irq: u8) -> Result<(), HalError> {
        if irq >= 16 {
            return Err(HalError::InvalidOperation);
        }

        unsafe {
            let port = if irq < 8 { 0x21 } else { 0xA1 };
            let irq_bit = if irq < 8 { irq } else { irq - 8 };
            
            let mask = self.inb(port);
            self.outb(port, mask & !(1 << irq_bit));
        }

        Ok(())
    }

    /// Disable interrupt on PIC
    pub fn disable_irq(&self, irq: u8) -> Result<(), HalError> {
        if irq >= 16 {
            return Err(HalError::InvalidOperation);
        }

        unsafe {
            let port = if irq < 8 { 0x21 } else { 0xA1 };
            let irq_bit = if irq < 8 { irq } else { irq - 8 };
            
            let mask = self.inb(port);
            self.outb(port, mask | (1 << irq_bit));
        }

        Ok(())
    }

    /// Send End of Interrupt (EOI) to PIC
    pub fn send_eoi(&self, irq: u8) {
        unsafe {
            if irq >= 8 {
                // Send EOI to slave PIC
                self.outb(0xA0, 0x20);
            }
            // Always send EOI to master PIC
            self.outb(0x20, 0x20);
        }
    }

    /// Get I/O statistics
    pub fn get_io_stats(&self) -> IoStats {
        IoStats {
            port_ranges: self.port_ranges.len() as u16,
            mmio_regions: self.memory_mapped_ranges.len() as u16,
            dma_channels: self.dma_channels.len() as u8,
        }
    }
}

/// I/O statistics
#[derive(Debug, Clone)]
pub struct IoStats {
    pub port_ranges: u16,
    pub mmio_regions: u16,
    pub dma_channels: u8,
}

/// I/O port utilities
pub mod port_utils {
    use super::*;

    /// Wait for I/O operation to complete
    pub fn io_wait() {
        unsafe {
            // Write to unused port 0x80 to introduce delay
            core::arch::asm!(
                "out 0x80, al",
                in("al") 0u8,
                options(nomem, nostack, preserves_flags)
            );
        }
    }

    /// Check if port is safe to access
    pub fn is_port_safe(port: u16) -> bool {
        // Define unsafe port ranges
        const UNSAFE_RANGES: &[(u16, u16)] = &[
            (0x00, 0x1F),   // DMA controller
            (0xF0, 0xFF),   // Math coprocessor
        ];

        !UNSAFE_RANGES.iter().any(|(start, end)| port >= *start && port <= *end)
    }
}
