/// PCI bus management for hardware abstraction layer
/// Provides PCI device discovery and configuration

use crate::hal::{
    PciManager, PciDevice, PciBar, PciBarType, PciCapability, PciBus, HalError
};
use alloc::collections::BTreeMap;
use alloc::vec::Vec;

impl PciManager {
    /// Create new PCI manager
    pub fn new() -> Self {
        Self {
            devices: Vec::new(),
            buses: BTreeMap::new(),
        }
    }

    /// Scan PCI buses for devices
    pub fn scan_buses(&mut self) -> Result<(), HalError> {
        // Scan all possible PCI buses (0-255)
        for bus in 0..=255 {
            if self.scan_bus(bus)? {
                // Bus exists, create bus structure
                self.buses.insert(bus, PciBus {
                    bus_number: bus,
                    primary_bus: bus,
                    secondary_bus: 0,
                    subordinate_bus: bus,
                });
            }
        }

        // Detect PCI-to-PCI bridges and update bus topology
        self.detect_bridges()?;
        
        Ok(())
    }

    /// Scan a specific PCI bus
    fn scan_bus(&mut self, bus: u8) -> Result<bool, HalError> {
        let mut found_devices = false;

        // Scan all devices on the bus (0-31)
        for device in 0..32 {
            // Check function 0 first
            if let Some(pci_device) = self.probe_device(bus, device, 0)? {
                found_devices = true;
                let is_multifunction = (pci_device.class_code & 0x800000) != 0;
                
                self.devices.push(pci_device);

                // If multifunction device, scan other functions
                if is_multifunction {
                    for function in 1..8 {
                        if let Some(func_device) = self.probe_device(bus, device, function)? {
                            self.devices.push(func_device);
                        }
                    }
                }
            }
        }

        Ok(found_devices)
    }

    /// Probe a specific PCI device
    fn probe_device(&self, bus: u8, device: u8, function: u8) -> Result<Option<PciDevice>, HalError> {
        let vendor_id = self.read_config_word(bus, device, function, 0x00)?;
        
        // Check if device exists (vendor ID 0xFFFF means no device)
        if vendor_id == 0xFFFF {
            return Ok(None);
        }

        let device_id = self.read_config_word(bus, device, function, 0x02)?;
        let class_code = self.read_config_dword(bus, device, function, 0x08)?;
        let revision = (class_code & 0xFF) as u8;
        let class_code = class_code >> 8;

        // Read BARs (Base Address Registers)
        let mut bars = Vec::new();
        for bar_index in 0..6 {
            let bar_offset = 0x10 + (bar_index * 4);
            let bar_value = self.read_config_dword(bus, device, function, bar_offset)?;
            
            if bar_value != 0 {
                bars.push(self.parse_bar(bar_index as u8, bar_value)?);
            }
        }

        // Read capabilities
        let capabilities = self.read_capabilities(bus, device, function)?;

        Ok(Some(PciDevice {
            bus,
            device,
            function,
            vendor_id,
            device_id,
            class_code,
            revision,
            bars,
            capabilities,
        }))
    }

    /// Read PCI configuration word
    fn read_config_word(&self, bus: u8, device: u8, function: u8, offset: u8) -> Result<u16, HalError> {
        let dword = self.read_config_dword(bus, device, function, offset & 0xFC)?;
        let shift = (offset & 0x03) * 8;
        Ok((dword >> shift) as u16)
    }

    /// Read PCI configuration dword
    fn read_config_dword(&self, bus: u8, device: u8, function: u8, offset: u8) -> Result<u32, HalError> {
        // Construct configuration address
        let address = 0x80000000u32
            | ((bus as u32) << 16)
            | ((device as u32) << 11)
            | ((function as u32) << 8)
            | ((offset & 0xFC) as u32);

        unsafe {
            // Write address to CONFIG_ADDRESS (0xCF8)
            core::arch::asm!(
                "out dx, eax",
                in("dx") 0xCF8u16,
                in("eax") address,
                options(nomem, nostack, preserves_flags)
            );

            // Read data from CONFIG_DATA (0xCFC)
            let data: u32;
            core::arch::asm!(
                "in eax, dx",
                out("eax") data,
                in("dx") 0xCFCu16,
                options(nomem, nostack, preserves_flags)
            );

            Ok(data)
        }
    }

    /// Write PCI configuration dword
    fn write_config_dword(&self, bus: u8, device: u8, function: u8, offset: u8, value: u32) -> Result<(), HalError> {
        // Construct configuration address
        let address = 0x80000000u32
            | ((bus as u32) << 16)
            | ((device as u32) << 11)
            | ((function as u32) << 8)
            | ((offset & 0xFC) as u32);

        unsafe {
            // Write address to CONFIG_ADDRESS (0xCF8)
            core::arch::asm!(
                "out dx, eax",
                in("dx") 0xCF8u16,
                in("eax") address,
                options(nomem, nostack, preserves_flags)
            );

            // Write data to CONFIG_DATA (0xCFC)
            core::arch::asm!(
                "out dx, eax",
                in("dx") 0xCFCu16,
                in("eax") value,
                options(nomem, nostack, preserves_flags)
            );
        }

        Ok(())
    }

    /// Parse a BAR (Base Address Register)
    fn parse_bar(&self, index: u8, bar_value: u32) -> Result<PciBar, HalError> {
        if bar_value & 0x01 != 0 {
            // I/O Space BAR
            Ok(PciBar {
                index,
                base_address: (bar_value & 0xFFFFFFFC) as u64,
                size: 0, // TODO: Determine size by writing all 1s and reading back
                bar_type: PciBarType::IoPort,
            })
        } else {
            // Memory Space BAR
            let is_64bit = (bar_value & 0x06) == 0x04;
            let bar_type = if is_64bit {
                PciBarType::Memory64
            } else {
                PciBarType::Memory32
            };

            Ok(PciBar {
                index,
                base_address: (bar_value & 0xFFFFFFF0) as u64,
                size: 0, // TODO: Determine size
                bar_type,
            })
        }
    }

    /// Read PCI capabilities
    fn read_capabilities(&self, bus: u8, device: u8, function: u8) -> Result<Vec<PciCapability>, HalError> {
        let mut capabilities = Vec::new();
        
        // Check if device has capabilities
        let status = self.read_config_word(bus, device, function, 0x06)?;
        if (status & 0x10) == 0 {
            return Ok(capabilities); // No capabilities
        }

        // Read capabilities pointer
        let mut cap_ptr = self.read_config_word(bus, device, function, 0x34)? as u8;
        cap_ptr &= 0xFC; // Align to dword boundary

        // Walk the capabilities list
        while cap_ptr != 0 && cap_ptr != 0xFF {
            let cap_header = self.read_config_word(bus, device, function, cap_ptr)?;
            let cap_id = (cap_header & 0xFF) as u8;
            let next_ptr = (cap_header >> 8) as u8;

            // Read capability data (simplified - would need per-capability parsing)
            let mut data = Vec::new();
            data.push(cap_header as u8);
            data.push((cap_header >> 8) as u8);

            capabilities.push(PciCapability {
                id: cap_id,
                offset: cap_ptr,
                data,
            });

            cap_ptr = next_ptr;
        }

        Ok(capabilities)
    }

    /// Detect PCI-to-PCI bridges
    fn detect_bridges(&mut self) -> Result<(), HalError> {
        for device in &self.devices {
            // Check if device is a PCI-to-PCI bridge (class code 0x0604)
            if device.class_code == 0x0604 {
                // Read bridge configuration
                let bridge_config = self.read_config_dword(
                    device.bus, device.device, device.function, 0x18
                )?;
                
                let primary_bus = (bridge_config & 0xFF) as u8;
                let secondary_bus = ((bridge_config >> 8) & 0xFF) as u8;
                let subordinate_bus = ((bridge_config >> 16) & 0xFF) as u8;

                // Update bus information
                if let Some(bus) = self.buses.get_mut(&device.bus) {
                    bus.primary_bus = primary_bus;
                    bus.secondary_bus = secondary_bus;
                    bus.subordinate_bus = subordinate_bus;
                }
            }
        }

        Ok(())
    }

    /// Get device by vendor and device ID
    pub fn find_device(&self, vendor_id: u16, device_id: u16) -> Option<&PciDevice> {
        self.devices.iter()
            .find(|device| device.vendor_id == vendor_id && device.device_id == device_id)
    }

    /// Get devices by class code
    pub fn find_devices_by_class(&self, class_code: u32) -> Vec<&PciDevice> {
        self.devices.iter()
            .filter(|device| device.class_code == class_code)
            .collect()
    }

    /// Get device name from vendor/device ID
    pub fn get_device_name(&self, vendor_id: u16, device_id: u16) -> &'static str {
        match (vendor_id, device_id) {
            // Intel devices
            (0x8086, 0x1237) => "Intel 440FX - PMC",
            (0x8086, 0x7000) => "Intel PIIX3 ISA Bridge",
            (0x8086, 0x7010) => "Intel PIIX3 IDE Controller",
            (0x8086, 0x7113) => "Intel PIIX4/4E/4M Power Management",
            (0x8086, 0x1234) => "Intel Graphics Device",
            
            // AMD devices
            (0x1022, 0x2000) => "AMD 79c970 PCnet32 LANCE",
            (0x1022, 0x1100) => "AMD K8 HyperTransport",
            
            // VirtualBox devices
            (0x80EE, 0xBEEF) => "VirtualBox Graphics Adapter",
            (0x80EE, 0xCAFE) => "VirtualBox Guest Service",
            
            // QEMU devices
            (0x1AF4, 0x1000) => "QEMU Virtual Network Device",
            (0x1AF4, 0x1001) => "QEMU Virtual Block Device",
            (0x1AF4, 0x1050) => "QEMU Virtual GPU",
            
            // VMware devices
            (0x15AD, 0x0405) => "VMware SVGA II Adapter",
            (0x15AD, 0x0770) => "VMware USB2 EHCI Controller",
            
            // Generic classes
            _ => match (vendor_id, (device_id >> 8) & 0xFF) {
                (_, 0x01) => "Mass Storage Controller",
                (_, 0x02) => "Network Controller",
                (_, 0x03) => "Display Controller",
                (_, 0x04) => "Multimedia Device",
                (_, 0x05) => "Memory Controller",
                (_, 0x06) => "Bridge Device",
                (_, 0x07) => "Communication Controller",
                (_, 0x08) => "System Peripheral",
                (_, 0x09) => "Input Device",
                (_, 0x0A) => "Docking Station",
                (_, 0x0B) => "Processor",
                (_, 0x0C) => "Serial Bus Controller",
                _ => "Unknown Device",
            }
        }
    }

    /// Get vendor name from vendor ID
    pub fn get_vendor_name(&self, vendor_id: u16) -> &'static str {
        match vendor_id {
            0x8086 => "Intel Corporation",
            0x1022 => "Advanced Micro Devices",
            0x10DE => "NVIDIA Corporation",
            0x1002 => "AMD/ATI",
            0x80EE => "VirtualBox",
            0x1AF4 => "Red Hat (QEMU)",
            0x15AD => "VMware",
            0x1234 => "Technical Corporation",
            0x1013 => "Cirrus Logic",
            0x5333 => "S3 Graphics",
            _ => "Unknown Vendor",
        }
    }

    /// Enable bus mastering for a device
    pub fn enable_bus_mastering(&self, device: &PciDevice) -> Result<(), HalError> {
        let command = self.read_config_word(device.bus, device.device, device.function, 0x04)?;
        let new_command = command | 0x04; // Set bus master bit
        
        self.write_config_dword(
            device.bus, device.device, device.function, 0x04,
            new_command as u32
        )?;
        
        Ok(())
    }

    /// Enable memory space for a device
    pub fn enable_memory_space(&self, device: &PciDevice) -> Result<(), HalError> {
        let command = self.read_config_word(device.bus, device.device, device.function, 0x04)?;
        let new_command = command | 0x02; // Set memory space bit
        
        self.write_config_dword(
            device.bus, device.device, device.function, 0x04,
            new_command as u32
        )?;
        
        Ok(())
    }

    /// Enable I/O space for a device
    pub fn enable_io_space(&self, device: &PciDevice) -> Result<(), HalError> {
        let command = self.read_config_word(device.bus, device.device, device.function, 0x04)?;
        let new_command = command | 0x01; // Set I/O space bit
        
        self.write_config_dword(
            device.bus, device.device, device.function, 0x04,
            new_command as u32
        )?;
        
        Ok(())
    }

    /// Get PCI statistics
    pub fn get_pci_stats(&self) -> PciStats {
        let mut device_classes = BTreeMap::new();
        
        for device in &self.devices {
            let class = (device.class_code >> 16) & 0xFF;
            *device_classes.entry(class as u8).or_insert(0) += 1;
        }

        PciStats {
            total_devices: self.devices.len() as u16,
            total_buses: self.buses.len() as u8,
            device_classes,
        }
    }
}

/// PCI statistics
#[derive(Debug, Clone)]
pub struct PciStats {
    pub total_devices: u16,
    pub total_buses: u8,
    pub device_classes: BTreeMap<u8, u16>,
}
