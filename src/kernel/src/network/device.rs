//! # Network Device Framework
//!
//! Provides network device abstraction and management for SynOS
//! Integrates with the existing device driver framework

use super::{MacAddress, NetworkError, NetworkPacket, NetworkStats};
use crate::drivers::{Device, DriverError, DeviceId, DeviceType};
use crate::devices::DeviceError;
use alloc::{boxed::Box, collections::BTreeMap, string::String, vec::Vec};
use core::sync::atomic::{AtomicU32, Ordering};
use spin::Mutex;

/// Network device trait extending the base Device trait
pub trait NetworkDevice: Device {
    /// Send a network packet
    fn send_packet(&mut self, packet: &NetworkPacket) -> Result<(), NetworkError>;

    /// Receive a network packet (non-blocking)
    fn receive_packet(&mut self) -> Result<Option<NetworkPacket>, NetworkError>;

    /// Get the device's MAC address
    fn get_mac_address(&self) -> MacAddress;

    /// Set the device's MAC address
    fn set_mac_address(&mut self, mac: MacAddress) -> Result<(), NetworkError>;

    /// Enable/disable promiscuous mode
    fn set_promiscuous_mode(&mut self, enabled: bool) -> Result<(), NetworkError>;

    /// Check if the device is up and running
    fn is_up(&self) -> bool;

    /// Bring the device up or down
    fn set_up(&mut self, up: bool) -> Result<(), NetworkError>;

    /// Get network statistics for this device
    fn get_stats(&self) -> NetworkStats;

    /// Get the maximum transmission unit (MTU)
    fn get_mtu(&self) -> usize;

    /// Set the maximum transmission unit (MTU)
    fn set_mtu(&mut self, mtu: usize) -> Result<(), NetworkError>;

    /// Check if multicast is supported
    fn supports_multicast(&self) -> bool;

    /// Add a multicast address
    fn add_multicast(&mut self, mac: MacAddress) -> Result<(), NetworkError>;

    /// Remove a multicast address
    fn remove_multicast(&mut self, mac: MacAddress) -> Result<(), NetworkError>;
}

/// Network device capability flags
#[derive(Debug, Clone, Copy)]
pub struct NetworkCapabilities {
    pub checksum_offload: bool,
    pub scatter_gather: bool,
    pub multicast: bool,
    pub promiscuous: bool,
    pub vlan_support: bool,
    pub jumbo_frames: bool,
}

impl Default for NetworkCapabilities {
    fn default() -> Self {
        Self {
            checksum_offload: false,
            scatter_gather: false,
            multicast: true,
            promiscuous: true,
            vlan_support: false,
            jumbo_frames: false,
        }
    }
}

/// Network device configuration
#[derive(Debug, Clone)]
pub struct NetworkConfig {
    pub mac_address: MacAddress,
    pub mtu: usize,
    pub promiscuous: bool,
    pub multicast_addresses: Vec<MacAddress>,
    pub capabilities: NetworkCapabilities,
}

impl Default for NetworkConfig {
    fn default() -> Self {
        Self {
            mac_address: MacAddress::new([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
            mtu: 1500, // Standard Ethernet MTU
            promiscuous: false,
            multicast_addresses: Vec::new(),
            capabilities: NetworkCapabilities::default(),
        }
    }
}

/// Network device manager
pub struct NetworkDeviceManager {
    devices: BTreeMap<DeviceId, Box<dyn NetworkDevice>>,
    next_id: AtomicU32,
    default_device: Option<DeviceId>,
}

impl NetworkDeviceManager {
    pub fn new() -> Self {
        Self {
            devices: BTreeMap::new(),
            next_id: AtomicU32::new(1),
            default_device: None,
        }
    }

    /// Register a new network device
    pub fn register_device(
        &mut self,
        mut device: Box<dyn NetworkDevice>,
    ) -> Result<DeviceId, NetworkError> {
        let device_id = DeviceId(self.next_id.fetch_add(1, Ordering::SeqCst) as u64);

        // Initialize the device
        // probe() not in NetworkDevice trait
        // init() not in NetworkDevice trait

        // If this is the first device, make it the default
        if self.devices.is_empty() {
            self.default_device = Some(device_id);
        }

        self.devices.insert(device_id, device);
        Ok(device_id)
    }

    /// Unregister a network device
    pub fn unregister_device(&mut self, device_id: DeviceId) -> Result<(), NetworkError> {
        if let Some(mut device) = self.devices.remove(&device_id) {
            device
                .shutdown()
                .map_err(|_| NetworkError::DeviceNotFound)?;

            // If this was the default device, pick a new one
            if self.default_device == Some(device_id) {
                self.default_device = self.devices.keys().next().copied();
            }

            Ok(())
        } else {
            Err(NetworkError::DeviceNotFound)
        }
    }

    /// Get a reference to a network device
    pub fn get_device(&self, device_id: DeviceId) -> Option<&dyn NetworkDevice> {
        self.devices.get(&device_id).map(|d| d.as_ref())
    }

    /// Get a mutable reference to a network device
    /// TODO: Fix lifetime issues
    // pub fn get_device_mut(&mut self, device_id: DeviceId) -> Option<&mut dyn NetworkDevice> {
    //     if let Some(device) = self.devices.get_mut(&device_id) {
    //         Some(&mut **device)
    //     } else {
    //         None
    //     }
    // }

    /// Get the default network device
    pub fn get_default_device(&self) -> Option<&dyn NetworkDevice> {
        self.default_device.and_then(|id| self.get_device(id))
    }

    /// Get the default network device (mutable)
    /// TODO: Fix after get_device_mut is fixed
    // pub fn get_default_device_mut(&mut self) -> Option<&mut dyn NetworkDevice> {
    //     self.default_device.and_then(|id| self.get_device_mut(id))
    // }

    /// Set the default network device
    pub fn set_default_device(&mut self, device_id: DeviceId) -> Result<(), NetworkError> {
        if self.devices.contains_key(&device_id) {
            self.default_device = Some(device_id);
            Ok(())
        } else {
            Err(NetworkError::DeviceNotFound)
        }
    }

    /// List all registered network devices
    pub fn list_devices(&self) -> Vec<DeviceId> {
        self.devices.keys().copied().collect()
    }

    /// Get network statistics for all devices
    pub fn get_all_stats(&self) -> BTreeMap<DeviceId, NetworkStats> {
        self.devices
            .iter()
            .map(|(&id, device)| (id, device.get_stats()))
            .collect()
    }

    /// Send a packet using the default device
    /// TODO: Fix after get_device_mut is fixed
    pub fn send_packet(&mut self, _packet: &NetworkPacket) -> Result<(), NetworkError> {
        // Temporary stub until lifetime issues are resolved
        Err(NetworkError::DeviceNotFound)
    }

    /// Receive a packet from any device
    pub fn receive_packet(&mut self) -> Result<Option<(DeviceId, NetworkPacket)>, NetworkError> {
        for (&device_id, device) in &mut self.devices {
            if let Some(packet) = device.receive_packet()? {
                return Ok(Some((device_id, packet)));
            }
        }
        Ok(None)
    }

    /// Broadcast a packet to all devices
    pub fn broadcast_packet(&mut self, packet: &NetworkPacket) -> Result<(), NetworkError> {
        let mut errors = Vec::new();

        for device in self.devices.values_mut() {
            if let Err(e) = device.send_packet(packet) {
                errors.push(e);
            }
        }

        if errors.is_empty() {
            Ok(())
        } else {
            // Return the first error encountered
            Err(errors.into_iter().next().unwrap())
        }
    }

    /// Get device count
    pub fn device_count(&self) -> usize {
        self.devices.len()
    }

    /// Check if any devices are available
    pub fn has_devices(&self) -> bool {
        !self.devices.is_empty()
    }
}

/// Global network device manager instance
static NETWORK_DEVICE_MANAGER: Mutex<Option<NetworkDeviceManager>> = Mutex::new(None);

/// Initialize the network device manager
pub fn init_network_devices() -> Result<(), NetworkError> {
    let mut manager = NETWORK_DEVICE_MANAGER.lock();
    if manager.is_none() {
        *manager = Some(NetworkDeviceManager::new());
    }
    Ok(())
}

/// Get a reference to the global network device manager
pub fn get_network_device_manager(
) -> Result<spin::MutexGuard<'static, Option<NetworkDeviceManager>>, NetworkError> {
    Ok(NETWORK_DEVICE_MANAGER.lock())
}

/// Register a network device globally
pub fn register_network_device(device: Box<dyn NetworkDevice>) -> Result<DeviceId, NetworkError> {
    let mut manager_guard = get_network_device_manager()?;
    if let Some(ref mut manager) = manager_guard.as_mut() {
        manager.register_device(device)
    } else {
        Err(NetworkError::DeviceNotFound)
    }
}

/// Send a packet using the default network device
pub fn send_network_packet(packet: &NetworkPacket) -> Result<(), NetworkError> {
    let mut manager_guard = get_network_device_manager()?;
    if let Some(ref mut manager) = manager_guard.as_mut() {
        manager.send_packet(packet)
    } else {
        Err(NetworkError::DeviceNotFound)
    }
}

/// Receive a packet from any network device
pub fn receive_network_packet() -> Result<Option<(DeviceId, NetworkPacket)>, NetworkError> {
    let mut manager_guard = get_network_device_manager()?;
    if let Some(ref mut manager) = manager_guard.as_mut() {
        manager.receive_packet()
    } else {
        Err(NetworkError::DeviceNotFound)
    }
}

/// Get network device statistics
pub fn get_network_device_stats() -> Result<BTreeMap<DeviceId, NetworkStats>, NetworkError> {
    let manager_guard = get_network_device_manager()?;
    if let Some(ref manager) = manager_guard.as_ref() {
        Ok(manager.get_all_stats())
    } else {
        Err(NetworkError::DeviceNotFound)
    }
}
