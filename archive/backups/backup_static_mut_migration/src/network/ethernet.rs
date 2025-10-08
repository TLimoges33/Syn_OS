//! # Ethernet Protocol Implementation
//!
//! Provides Ethernet frame processing and basic Ethernet device support

use alloc::string::ToString;
use super::{NetworkError, MacAddress, NetworkPacket, NetworkStats, NetworkDevice};
use crate::drivers::{Device, DriverError, DeviceType, DeviceId};
use crate::devices::DeviceError;
use alloc::{vec::Vec, boxed::Box, string::String};
use core::fmt;

/// Ethernet frame header size (14 bytes)
pub const ETHERNET_HEADER_SIZE: usize = 14;

/// Ethernet frame minimum size (64 bytes)
pub const ETHERNET_MIN_FRAME_SIZE: usize = 64;

/// Ethernet frame maximum size (1518 bytes)
pub const ETHERNET_MAX_FRAME_SIZE: usize = 1518;

/// Common Ethernet types
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(u16)]
pub enum EtherType {
    IPv4 = 0x0800,
    ARP = 0x0806,
    IPv6 = 0x86DD,
    VLAN = 0x8100,
    Unknown(u16),
}

impl From<u16> for EtherType {
    fn from(value: u16) -> Self {
        match value {
            0x0800 => EtherType::IPv4,
            0x0806 => EtherType::ARP,
            0x86DD => EtherType::IPv6,
            0x8100 => EtherType::VLAN,
            other => EtherType::Unknown(other),
        }
    }
}

impl From<EtherType> for u16 {
    fn from(ether_type: EtherType) -> Self {
        match ether_type {
            EtherType::IPv4 => 0x0800,
            EtherType::ARP => 0x0806,
            EtherType::IPv6 => 0x86DD,
            EtherType::VLAN => 0x8100,
            EtherType::Unknown(value) => value,
        }
    }
}

impl fmt::Display for EtherType {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            EtherType::IPv4 => write!(f, "IPv4"),
            EtherType::ARP => write!(f, "ARP"),
            EtherType::IPv6 => write!(f, "IPv6"),
            EtherType::VLAN => write!(f, "VLAN"),
            EtherType::Unknown(value) => write!(f, "Unknown(0x{:04X})", value),
        }
    }
}

/// Ethernet frame header
#[derive(Debug, Clone)]
pub struct EthernetHeader {
    pub destination: MacAddress,
    pub source: MacAddress,
    pub ether_type: EtherType,
}

impl EthernetHeader {
    /// Create a new Ethernet header
    pub fn new(destination: MacAddress, source: MacAddress, ether_type: EtherType) -> Self {
        Self {
            destination,
            source,
            ether_type,
        }
    }

    /// Parse an Ethernet header from bytes
    pub fn parse(data: &[u8]) -> Result<Self, NetworkError> {
        if data.len() < ETHERNET_HEADER_SIZE {
            return Err(NetworkError::InvalidPacket);
        }

        let destination = MacAddress::new([
            data[0], data[1], data[2], data[3], data[4], data[5]
        ]);
        
        let source = MacAddress::new([
            data[6], data[7], data[8], data[9], data[10], data[11]
        ]);
        
        let ether_type = EtherType::from(
            u16::from_be_bytes([data[12], data[13]])
        );

        Ok(Self {
            destination,
            source,
            ether_type,
        })
    }

    /// Serialize the header to bytes
    pub fn to_bytes(&self) -> [u8; ETHERNET_HEADER_SIZE] {
        let mut bytes = [0u8; ETHERNET_HEADER_SIZE];
        
        // Destination MAC
        bytes[0..6].copy_from_slice(self.destination.bytes());
        
        // Source MAC
        bytes[6..12].copy_from_slice(self.source.bytes());
        
        // EtherType
        let ether_type_bytes = u16::to_be_bytes(self.ether_type.into());
        bytes[12..14].copy_from_slice(&ether_type_bytes);
        
        bytes
    }

    /// Get the header size in bytes
    pub fn size(&self) -> usize {
        ETHERNET_HEADER_SIZE
    }
}

/// Complete Ethernet frame
#[derive(Debug, Clone)]
pub struct EthernetFrame {
    pub header: EthernetHeader,
    pub payload: Vec<u8>,
}

impl EthernetFrame {
    /// Create a new Ethernet frame
    pub fn new(header: EthernetHeader, payload: Vec<u8>) -> Self {
        Self { header, payload }
    }

    /// Parse an Ethernet frame from a packet
    pub fn parse(packet: &NetworkPacket) -> Result<Self, NetworkError> {
        let data = packet.data();
        
        if data.len() < ETHERNET_HEADER_SIZE {
            return Err(NetworkError::InvalidPacket);
        }

        let header = EthernetHeader::parse(data)?;
        let payload = data[ETHERNET_HEADER_SIZE..].to_vec();

        Ok(Self { header, payload })
    }

    /// Convert the frame to a network packet
    pub fn to_packet(&self) -> NetworkPacket {
        let mut data = Vec::with_capacity(ETHERNET_HEADER_SIZE + self.payload.len());
        
        // Add header
        data.extend_from_slice(&self.header.to_bytes());
        
        // Add payload
        data.extend_from_slice(&self.payload);
        
        NetworkPacket::new(data)
    }

    /// Get the total frame size
    pub fn size(&self) -> usize {
        ETHERNET_HEADER_SIZE + self.payload.len()
    }

    /// Check if the frame is valid
    pub fn is_valid(&self) -> bool {
        let total_size = self.size();
        total_size >= ETHERNET_MIN_FRAME_SIZE && total_size <= ETHERNET_MAX_FRAME_SIZE
    }

    /// Check if this frame is addressed to the given MAC address
    pub fn is_for_address(&self, mac: MacAddress) -> bool {
        self.header.destination == mac || 
        self.header.destination.is_broadcast() ||
        (self.header.destination.is_multicast() && self.should_accept_multicast(mac))
    }

    /// Check if we should accept this multicast frame
    fn should_accept_multicast(&self, _our_mac: MacAddress) -> bool {
        // For now, accept all multicast frames
        // In a real implementation, this would check against a multicast filter list
        true
    }

    /// Create a broadcast frame
    pub fn broadcast(source: MacAddress, ether_type: EtherType, payload: Vec<u8>) -> Self {
        let header = EthernetHeader::new(
            MacAddress::new([0xFF; 6]), // Broadcast address
            source,
            ether_type,
        );
        Self::new(header, payload)
    }
}

/// Simple Ethernet device implementation for testing
pub struct SimpleEthernetDevice {
    id: DeviceId,
    name: String,
    mac_address: MacAddress,
    is_up: bool,
    promiscuous: bool,
    mtu: usize,
    stats: NetworkStats,
    rx_buffer: Vec<NetworkPacket>,
    multicast_addresses: Vec<MacAddress>,
}

impl SimpleEthernetDevice {
    /// Create a new simple Ethernet device
    pub fn new(name: String, mac_address: MacAddress) -> Self {
        Self {
            id: DeviceId(0), // Will be set by device manager
            name,
            mac_address,
            is_up: false,
            promiscuous: false,
            mtu: 1500,
            stats: NetworkStats::new(),
            rx_buffer: Vec::new(),
            multicast_addresses: Vec::new(),
        }
    }

    /// Simulate receiving a packet (for testing)
    pub fn simulate_receive(&mut self, packet: NetworkPacket) {
        let packet_len = packet.len();
        self.rx_buffer.push(packet);
        self.stats.record_receive(packet_len);
    }

    /// Check if we should accept this frame
    fn should_accept_frame(&self, frame: &EthernetFrame) -> bool {
        if self.promiscuous {
            return true;
        }

        frame.is_for_address(self.mac_address) ||
        self.multicast_addresses.iter().any(|&addr| frame.header.destination == addr)
    }
}

impl Device for SimpleEthernetDevice {
    fn device_type(&self) -> DeviceType {
        DeviceType::NetworkDevice
    }

    fn device_id(&self) -> DeviceId {
        self.id
    }

    fn name(&self) -> &str {
        &self.name
    }

    fn capabilities(&self) -> crate::drivers::DeviceCapabilities {
        crate::drivers::DeviceCapabilities {
            can_read: true,
            can_write: true,
            can_seek: false,
            supports_dma: false,
            supports_interrupts: true,
            hot_pluggable: false,
        }
    }

    fn initialize(&mut self) -> Result<(), DriverError> {
        self.is_up = false; // Start in down state
        Ok(())
    }

    fn shutdown(&mut self) -> Result<(), DriverError> {
        self.is_up = false;
        self.rx_buffer.clear();
        Ok(())
    }

    fn reset(&mut self) -> Result<(), DriverError> {
        self.is_up = false;
        self.promiscuous = false;
        self.rx_buffer.clear();
        self.stats = NetworkStats::new();
        Ok(())
    }

    fn status(&self) -> crate::drivers::DeviceStatus {
        if self.is_up {
            crate::drivers::DeviceStatus::Active
        } else {
            crate::drivers::DeviceStatus::Inactive
        }
    }
}

impl NetworkDevice for SimpleEthernetDevice {
    fn send_packet(&mut self, packet: &NetworkPacket) -> Result<(), NetworkError> {
        if !self.is_up {
            return Err(NetworkError::DeviceNotFound);
        }

        if packet.len() > self.mtu + ETHERNET_HEADER_SIZE {
            return Err(NetworkError::InvalidPacket);
        }

        // For a simple device, we just record the send statistics
        self.stats.record_send(packet.len());
        Ok(())
    }

    fn receive_packet(&mut self) -> Result<Option<NetworkPacket>, NetworkError> {
        if !self.is_up {
            return Ok(None);
        }

        if let Some(packet) = self.rx_buffer.pop() {
            // Check if we should accept this packet
            if let Ok(frame) = EthernetFrame::parse(&packet) {
                if self.should_accept_frame(&frame) {
                    return Ok(Some(packet));
                }
            }
        }

        Ok(None)
    }

    fn get_mac_address(&self) -> MacAddress {
        self.mac_address
    }

    fn set_mac_address(&mut self, mac: MacAddress) -> Result<(), NetworkError> {
        self.mac_address = mac;
        Ok(())
    }

    fn set_promiscuous_mode(&mut self, enabled: bool) -> Result<(), NetworkError> {
        self.promiscuous = enabled;
        Ok(())
    }

    fn is_up(&self) -> bool {
        self.is_up
    }

    fn set_up(&mut self, up: bool) -> Result<(), NetworkError> {
        self.is_up = up;
        Ok(())
    }

    fn get_stats(&self) -> NetworkStats {
        self.stats.clone()
    }

    fn get_mtu(&self) -> usize {
        self.mtu
    }

    fn set_mtu(&mut self, mtu: usize) -> Result<(), NetworkError> {
        if mtu < 68 || mtu > 9000 {
            return Err(NetworkError::InvalidAddress);
        }
        self.mtu = mtu;
        Ok(())
    }

    fn supports_multicast(&self) -> bool {
        true
    }

    fn add_multicast(&mut self, mac: MacAddress) -> Result<(), NetworkError> {
        if !mac.is_multicast() {
            return Err(NetworkError::InvalidAddress);
        }
        
        if !self.multicast_addresses.contains(&mac) {
            self.multicast_addresses.push(mac);
        }
        Ok(())
    }

    fn remove_multicast(&mut self, mac: MacAddress) -> Result<(), NetworkError> {
        self.multicast_addresses.retain(|&addr| addr != mac);
        Ok(())
    }
}

/// Create a simple Ethernet device for testing
pub fn create_simple_ethernet_device(name: &str) -> Box<dyn NetworkDevice> {
    // Generate a random-ish MAC address for testing
    let mac = MacAddress::new([0x02, 0x00, 0x00, 0x12, 0x34, 0x56]);
    Box::new(SimpleEthernetDevice::new(name.to_string(), mac))
}
