/// PCI bus management for hardware abstraction layer
/// Provides PCI device discovery and configuration

use crate::hal::{PciManager, PciDevice, PciBus, HalError};
use alloc::collections::BTreeMap;
use alloc::vec::Vec;

impl PciManager {
    /// Create a new PCI manager
    pub fn new() -> Self {
        Self {
            devices: Vec::new(),
            buses: BTreeMap::new(),
        }
    }

    /// Scan all PCI buses for devices
    pub fn scan_buses(&mut self) -> Result<(), HalError> {
        crate::println!("Scanning PCI buses...");
        
        // Scan all possible buses (0-255)
        for bus in 0..=255 {
            if self.scan_bus(bus)? {
                // If we found devices on this bus, add it to our bus map
                self.buses.insert(bus, PciBus {
                    bus_number: bus,
                    primary_bus: bus,
                    secondary_bus: 0,
                    subordinate_bus: 0,
                    devices: Vec::new(),
                });
            }
        }

        crate::println!("PCI scan complete: {} devices found on {} buses", 
            self.devices.len(), self.buses.len());
        
        Ok(())
    }

    /// Scan a specific PCI bus
    fn scan_bus(&mut self, bus: u8) -> Result<bool, HalError> {
        let mut found_devices = false;

        // Scan all devices on this bus (0-31)
        for device in 0..32 {
            if self.scan_device(bus, device)? {
                found_devices = true;
            }
        }

        Ok(found_devices)
    }

    /// Scan a specific PCI device
    fn scan_device(&mut self, bus: u8, device: u8) -> Result<bool, HalError> {
        // Check function 0 first
        if let Some(pci_device) = self.probe_function(bus, device, 0)? {
            self.devices.push(pci_device.clone());
            
            // Update bus device list
            if let Some(bus_info) = self.buses.get_mut(&bus) {
                bus_info.devices.push(device);
            }

            // Check if this is a multi-function device
            if (pci_device.header_type & 0x80) != 0 {
                // Scan additional functions (1-7)
                for function in 1..8 {
                    if let Some(func_device) = self.probe_function(bus, device, function)? {
                        self.devices.push(func_device);
                    }
                }
            }

            return Ok(true);
        }

        Ok(false)
    }

    /// Probe a specific PCI function
    fn probe_function(&self, bus: u8, device: u8, function: u8) -> Result<Option<PciDevice>, HalError> {
        let vendor_id = self.read_config_word(bus, device, function, 0x00)?;
        
        // Check if device exists (vendor ID of 0xFFFF means no device)
        if vendor_id == 0xFFFF {
            return Ok(None);
        }

        let device_id = self.read_config_word(bus, device, function, 0x02)?;
        let class_rev = self.read_config_dword(bus, device, function, 0x08)?;
        let header_bist = self.read_config_dword(bus, device, function, 0x0C)?;
        let subsystem = self.read_config_dword(bus, device, function, 0x2C)?;
        let interrupt = self.read_config_dword(bus, device, function, 0x3C)?;

        // Read Base Address Registers (BARs)
        let mut base_addresses = [0u32; 6];
        for i in 0..6 {
            base_addresses[i] = self.read_config_dword(bus, device, function, 0x10 + (i as u8 * 4))?;
        }

        let pci_device = PciDevice {
            bus,
            device,
            function,
            vendor_id,
            device_id,
            class_code: ((class_rev >> 24) & 0xFF) as u8,
            subclass: ((class_rev >> 16) & 0xFF) as u8,
            prog_interface: ((class_rev >> 8) & 0xFF) as u8,
            revision: (class_rev & 0xFF) as u8,
            header_type: ((header_bist >> 16) & 0xFF) as u8,
            subsystem_vendor: (subsystem & 0xFFFF) as u16,
            subsystem_device: ((subsystem >> 16) & 0xFFFF) as u16,
            base_addresses,
            interrupt_line: (interrupt & 0xFF) as u8,
            interrupt_pin: ((interrupt >> 8) & 0xFF) as u8,
        };

        Ok(Some(pci_device))
    }

    /// Read a word from PCI configuration space
    fn read_config_word(&self, bus: u8, device: u8, function: u8, offset: u8) -> Result<u16, HalError> {
        let dword = self.read_config_dword(bus, device, function, offset & 0xFC)?;
        let shift = (offset & 2) * 8;
        Ok(((dword >> shift) & 0xFFFF) as u16)
    }

    /// Read a dword from PCI configuration space
    fn read_config_dword(&self, bus: u8, device: u8, function: u8, offset: u8) -> Result<u32, HalError> {
        // Create configuration address
        let address = 0x80000000u32
            | ((bus as u32) << 16)
            | ((device as u32) << 11)
            | ((function as u32) << 8)
            | ((offset as u32) & 0xFC);

        unsafe {
            // Write address to CONFIG_ADDRESS (0xCF8)
            core::arch::asm!(
                "out dx, eax",
                in("dx") 0xCF8u16,
                in("eax") address,
                options(nostack, preserves_flags)
            );

            // Read data from CONFIG_DATA (0xCFC)
            let mut data: u32;
            core::arch::asm!(
                "in eax, dx",
                out("eax") data,
                in("dx") 0xCFCu16,
                options(nostack, preserves_flags)
            );

            Ok(data)
        }
    }

    /// Write a dword to PCI configuration space
    fn write_config_dword(&self, bus: u8, device: u8, function: u8, offset: u8, value: u32) -> Result<(), HalError> {
        // Create configuration address
        let address = 0x80000000u32
            | ((bus as u32) << 16)
            | ((device as u32) << 11)
            | ((function as u32) << 8)
            | ((offset as u32) & 0xFC);

        unsafe {
            // Write address to CONFIG_ADDRESS (0xCF8)
            core::arch::asm!(
                "out dx, eax",
                in("dx") 0xCF8u16,
                in("eax") address,
                options(nostack, preserves_flags)
            );

            // Write data to CONFIG_DATA (0xCFC)
            core::arch::asm!(
                "out dx, eax",
                in("dx") 0xCFCu16,
                in("eax") value,
                options(nostack, preserves_flags)
            );
        }

        Ok(())
    }

    /// Find devices by vendor and device ID
    pub fn find_devices(&self, vendor_id: u16, device_id: u16) -> Vec<&PciDevice> {
        self.devices
            .iter()
            .filter(|device| device.vendor_id == vendor_id && device.device_id == device_id)
            .collect()
    }

    /// Find devices by class code
    pub fn find_devices_by_class(&self, class_code: u8, subclass: Option<u8>) -> Vec<&PciDevice> {
        self.devices
            .iter()
            .filter(|device| {
                device.class_code == class_code
                    && subclass.map_or(true, |sc| device.subclass == sc)
            })
            .collect()
    }

    /// Get device name from vendor and device IDs
    pub fn get_device_name(&self, vendor_id: u16, device_id: u16) -> &'static str {
        match vendor_id {
            0x8086 => match device_id {
                0x1237 => "Intel 440FX PCI Host Bridge",
                0x7000 => "Intel PIIX3 PCI-to-ISA Bridge",
                0x7010 => "Intel PIIX3 IDE Controller",
                0x7113 => "Intel PIIX4 Power Management Controller",
                0x100E => "Intel 82540EM Gigabit Ethernet",
                _ => "Intel Device",
            },
            0x1022 => "AMD Device",
            0x10DE => "NVIDIA Device",
            0x1002 => "ATI/AMD Graphics Device",
            0x8086 => "Intel Device",
            _ => "Unknown Device",
        }
    }

    /// Get class name from class code
    pub fn get_class_name(&self, class_code: u8, subclass: u8) -> &'static str {
        match class_code {
            0x00 => "Unclassified",
            0x01 => match subclass {
                0x00 => "SCSI Controller",
                0x01 => "IDE Controller",
                0x02 => "Floppy Disk Controller",
                0x03 => "IPI Bus Controller",
                0x04 => "RAID Controller",
                0x05 => "ATA Controller",
                0x06 => "SATA Controller",
                0x07 => "SAS Controller",
                _ => "Mass Storage Controller",
            },
            0x02 => match subclass {
                0x00 => "Ethernet Controller",
                0x01 => "Token Ring Controller",
                0x02 => "FDDI Controller",
                0x03 => "ATM Controller",
                0x04 => "ISDN Controller",
                0x80 => "Other Network Controller",
                _ => "Network Controller",
            },
            0x03 => match subclass {
                0x00 => "VGA Display Controller",
                0x01 => "XGA Display Controller",
                0x02 => "3D Display Controller",
                _ => "Display Controller",
            },
            0x04 => "Multimedia Controller",
            0x05 => "Memory Controller",
            0x06 => match subclass {
                0x00 => "Host Bridge",
                0x01 => "ISA Bridge",
                0x02 => "EISA Bridge",
                0x03 => "MCA Bridge",
                0x04 => "PCI-to-PCI Bridge",
                0x05 => "PCMCIA Bridge",
                0x06 => "NuBus Bridge",
                0x07 => "CardBus Bridge",
                0x08 => "RACEway Bridge",
                _ => "Bridge Device",
            },
            0x07 => "Communication Controller",
            0x08 => "System Peripheral",
            0x09 => "Input Device",
            0x0A => "Docking Station",
            0x0B => "Processor",
            0x0C => match subclass {
                0x00 => "FireWire Controller",
                0x01 => "ACCESS Bus Controller",
                0x02 => "SSA Controller",
                0x03 => "USB Controller",
                0x04 => "Fibre Channel Controller",
                0x05 => "SMBus Controller",
                _ => "Serial Bus Controller",
            },
            0x0D => "Wireless Controller",
            0x0E => "Intelligent I/O Controller",
            0x0F => "Satellite Communication Controller",
            0x10 => "Encryption/Decryption Controller",
            0x11 => "Data Acquisition Controller",
            _ => "Unknown Class",
        }
    }

    /// Enable PCI device
    pub fn enable_device(&self, device: &PciDevice) -> Result<(), HalError> {
        // Read current command register
        let command = self.read_config_word(device.bus, device.device, device.function, 0x04)?;
        
        // Enable I/O space, memory space, and bus mastering
        let new_command = command | 0x07;
        
        // Write back to command register
        let command_dword = (new_command as u32) | ((command as u32) << 16);
        self.write_config_dword(device.bus, device.device, device.function, 0x04, command_dword)?;
        
        Ok(())
    }

    /// Disable PCI device
    pub fn disable_device(&self, device: &PciDevice) -> Result<(), HalError> {
        // Read current command register
        let command = self.read_config_word(device.bus, device.device, device.function, 0x04)?;
        
        // Disable I/O space, memory space, and bus mastering
        let new_command = command & !0x07;
        
        // Write back to command register
        let command_dword = (new_command as u32) | ((command as u32) << 16);
        self.write_config_dword(device.bus, device.device, device.function, 0x04, command_dword)?;
        
        Ok(())
    }

    /// Get BAR (Base Address Register) information
    pub fn get_bar_info(&self, device: &PciDevice, bar_index: usize) -> Option<BarInfo> {
        if bar_index >= 6 {
            return None;
        }

        let bar_value = device.base_addresses[bar_index];
        if bar_value == 0 {
            return None;
        }

        if (bar_value & 1) != 0 {
            // I/O space BAR
            Some(BarInfo {
                address: (bar_value & !3) as u64,
                size: 0, // Would need to be determined by writing to BAR
                bar_type: BarType::IoSpace,
                prefetchable: false,
            })
        } else {
            // Memory space BAR
            let prefetchable = (bar_value & 8) != 0;
            let bar_type = match (bar_value >> 1) & 3 {
                0 => BarType::Memory32,
                2 => BarType::Memory64,
                _ => BarType::Reserved,
            };

            Some(BarInfo {
                address: (bar_value & !0xF) as u64,
                size: 0, // Would need to be determined by writing to BAR
                bar_type,
                prefetchable,
            })
        }
    }
}

/// BAR (Base Address Register) information
#[derive(Debug, Clone)]
pub struct BarInfo {
    pub address: u64,
    pub size: u64,
    pub bar_type: BarType,
    pub prefetchable: bool,
}

/// BAR types
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BarType {
    IoSpace,
    Memory32,
    Memory64,
    Reserved,
}
