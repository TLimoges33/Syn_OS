//! # ARP (Address Resolution Protocol) Implementation
//! 
//! ARP protocol for resolving IP addresses to MAC addresses

use super::{NetworkError, Ipv4Address, MacAddress};
use alloc::vec::Vec;
use alloc::collections::BTreeMap;

/// ARP operation codes
#[derive(Debug, Clone, Copy)]
#[repr(u16)]
pub enum ArpOperation {
    Request = 1,
    Reply = 2,
}

impl ArpOperation {
    /// Convert from u16
    pub fn from_u16(value: u16) -> Result<Self, NetworkError> {
        match value {
            1 => Ok(ArpOperation::Request),
            2 => Ok(ArpOperation::Reply),
            _ => Err(NetworkError::InvalidPacket),
        }
    }
}

/// ARP hardware types
#[derive(Debug, Clone, Copy)]
#[repr(u16)]
pub enum ArpHardwareType {
    Ethernet = 1,
}

/// ARP protocol types
#[derive(Debug, Clone, Copy)]
#[repr(u16)]
pub enum ArpProtocolType {
    IPv4 = 0x0800,
}

/// ARP packet structure
#[derive(Debug, Clone)]
pub struct ArpPacket {
    pub hardware_type: ArpHardwareType,
    pub protocol_type: ArpProtocolType,
    pub hardware_len: u8,
    pub protocol_len: u8,
    pub operation: ArpOperation,
    pub sender_hw_addr: MacAddress,
    pub sender_proto_addr: Ipv4Address,
    pub target_hw_addr: MacAddress,
    pub target_proto_addr: Ipv4Address,
}

impl ArpPacket {
    /// ARP packet size for Ethernet/IPv4
    pub const SIZE: usize = 28;

    /// Create a new ARP request
    pub fn request(sender_hw: MacAddress, sender_ip: Ipv4Address, target_ip: Ipv4Address) -> Self {
        Self {
            hardware_type: ArpHardwareType::Ethernet,
            protocol_type: ArpProtocolType::IPv4,
            hardware_len: 6,
            protocol_len: 4,
            operation: ArpOperation::Request,
            sender_hw_addr: sender_hw,
            sender_proto_addr: sender_ip,
            target_hw_addr: MacAddress::broadcast(), // Unknown for requests
            target_proto_addr: target_ip,
        }
    }

    /// Create a new ARP reply
    pub fn reply(sender_hw: MacAddress, sender_ip: Ipv4Address, target_hw: MacAddress, target_ip: Ipv4Address) -> Self {
        Self {
            hardware_type: ArpHardwareType::Ethernet,
            protocol_type: ArpProtocolType::IPv4,
            hardware_len: 6,
            protocol_len: 4,
            operation: ArpOperation::Reply,
            sender_hw_addr: sender_hw,
            sender_proto_addr: sender_ip,
            target_hw_addr: target_hw,
            target_proto_addr: target_ip,
        }
    }

    /// Parse ARP packet from bytes
    pub fn parse(data: &[u8]) -> Result<Self, NetworkError> {
        if data.len() < Self::SIZE {
            return Err(NetworkError::InvalidPacket);
        }

        let hardware_type = match u16::from_be_bytes([data[0], data[1]]) {
            1 => ArpHardwareType::Ethernet,
            _ => return Err(NetworkError::InvalidPacket),
        };

        let protocol_type = match u16::from_be_bytes([data[2], data[3]]) {
            0x0800 => ArpProtocolType::IPv4,
            _ => return Err(NetworkError::InvalidPacket),
        };

        let hardware_len = data[4];
        let protocol_len = data[5];
        
        if hardware_len != 6 || protocol_len != 4 {
            return Err(NetworkError::InvalidPacket);
        }

        let operation = ArpOperation::from_u16(u16::from_be_bytes([data[6], data[7]]))?;

        let sender_hw_addr = MacAddress::from_bytes(&data[8..14])?;
        let sender_proto_addr = Ipv4Address::from_bytes(&data[14..18])?;
        let target_hw_addr = MacAddress::from_bytes(&data[18..24])?;
        let target_proto_addr = Ipv4Address::from_bytes(&data[24..28])?;

        Ok(Self {
            hardware_type,
            protocol_type,
            hardware_len,
            protocol_len,
            operation,
            sender_hw_addr,
            sender_proto_addr,
            target_hw_addr,
            target_proto_addr,
        })
    }

    /// Serialize ARP packet to bytes
    pub fn to_bytes(&self) -> Vec<u8> {
        let mut bytes = Vec::with_capacity(Self::SIZE);
        
        bytes.extend_from_slice(&(self.hardware_type as u16).to_be_bytes());
        bytes.extend_from_slice(&(self.protocol_type as u16).to_be_bytes());
        bytes.push(self.hardware_len);
        bytes.push(self.protocol_len);
        bytes.extend_from_slice(&(self.operation as u16).to_be_bytes());
        bytes.extend_from_slice(&self.sender_hw_addr.to_bytes());
        bytes.extend_from_slice(&self.sender_proto_addr.to_bytes());
        bytes.extend_from_slice(&self.target_hw_addr.to_bytes());
        bytes.extend_from_slice(&self.target_proto_addr.to_bytes());
        
        bytes
    }
}

/// ARP cache entry
#[derive(Debug, Clone)]
pub struct ArpCacheEntry {
    pub mac_addr: MacAddress,
    pub timestamp: u64,
    pub is_static: bool,
}

impl ArpCacheEntry {
    /// Create a new cache entry
    pub fn new(mac_addr: MacAddress, timestamp: u64, is_static: bool) -> Self {
        Self {
            mac_addr,
            timestamp,
            is_static,
        }
    }

    /// Check if entry is expired (5 minutes for dynamic entries)
    pub fn is_expired(&self, current_time: u64) -> bool {
        if self.is_static {
            false
        } else {
            current_time > self.timestamp + 300 // 5 minutes
        }
    }
}

/// ARP table for IP to MAC address resolution
#[derive(Debug)]
pub struct ArpTable {
    entries: BTreeMap<Ipv4Address, ArpCacheEntry>,
    pending_requests: BTreeMap<Ipv4Address, u64>,
}

impl ArpTable {
    /// Create a new ARP table
    pub fn new() -> Self {
        Self {
            entries: BTreeMap::new(),
            pending_requests: BTreeMap::new(),
        }
    }

    /// Add an entry to the ARP table
    pub fn add_entry(&mut self, ip: Ipv4Address, mac: MacAddress, timestamp: u64, is_static: bool) {
        let entry = ArpCacheEntry::new(mac, timestamp, is_static);
        self.entries.insert(ip, entry);
        self.pending_requests.remove(&ip);
    }

    /// Look up MAC address for IP
    pub fn lookup(&self, ip: Ipv4Address, current_time: u64) -> Option<MacAddress> {
        if let Some(entry) = self.entries.get(&ip) {
            if !entry.is_expired(current_time) {
                return Some(entry.mac_addr);
            }
        }
        None
    }

    /// Check if an ARP request is pending
    pub fn is_request_pending(&self, ip: Ipv4Address, current_time: u64) -> bool {
        if let Some(&timestamp) = self.pending_requests.get(&ip) {
            current_time < timestamp + 5 // Wait 5 seconds between requests
        } else {
            false
        }
    }

    /// Mark an ARP request as pending
    pub fn mark_request_pending(&mut self, ip: Ipv4Address, timestamp: u64) {
        self.pending_requests.insert(ip, timestamp);
    }

    /// Clean expired entries
    pub fn cleanup(&mut self, current_time: u64) {
        self.entries.retain(|_, entry| !entry.is_expired(current_time));
        self.pending_requests.retain(|_, &mut timestamp| current_time < timestamp + 5);
    }

    /// Get all entries
    pub fn entries(&self) -> &BTreeMap<Ipv4Address, ArpCacheEntry> {
        &self.entries
    }
}

/// ARP protocol handler
#[derive(Debug)]
pub struct ArpLayer {
    table: ArpTable,
    local_ip: Option<Ipv4Address>,
    local_mac: Option<MacAddress>,
}

impl ArpLayer {
    /// Create a new ARP layer
    pub fn new() -> Self {
        Self {
            table: ArpTable::new(),
            local_ip: None,
            local_mac: None,
        }
    }

    /// Set local IP and MAC addresses
    pub fn set_local_addresses(&mut self, ip: Ipv4Address, mac: MacAddress) {
        self.local_ip = Some(ip);
        self.local_mac = Some(mac);
        // Add ourselves to the table
        self.table.add_entry(ip, mac, 0, true);
    }

    /// Process incoming ARP packet
    pub fn process_packet(&mut self, packet: &ArpPacket, timestamp: u64) -> Result<Option<ArpPacket>, NetworkError> {
        // Update our cache with sender information
        self.table.add_entry(packet.sender_proto_addr, packet.sender_hw_addr, timestamp, false);

        match packet.operation {
            ArpOperation::Request => {
                // Check if the request is for our IP
                if let Some(local_ip) = self.local_ip {
                    if packet.target_proto_addr == local_ip {
                        if let Some(local_mac) = self.local_mac {
                            // Send ARP reply
                            let reply = ArpPacket::reply(
                                local_mac,
                                local_ip,
                                packet.sender_hw_addr,
                                packet.sender_proto_addr
                            );
                            return Ok(Some(reply));
                        }
                    }
                }
                Ok(None)
            },
            ArpOperation::Reply => {
                // Reply processed by adding to cache above
                Ok(None)
            }
        }
    }

    /// Resolve IP address to MAC address
    pub fn resolve(&mut self, ip: Ipv4Address, timestamp: u64) -> Result<Option<MacAddress>, NetworkError> {
        // Check cache first
        if let Some(mac) = self.table.lookup(ip, timestamp) {
            return Ok(Some(mac));
        }

        // Don't send duplicate requests
        if self.table.is_request_pending(ip, timestamp) {
            return Ok(None);
        }

        // Mark request as pending
        self.table.mark_request_pending(ip, timestamp);
        Ok(None)
    }

    /// Create ARP request for IP address
    pub fn create_request(&self, target_ip: Ipv4Address) -> Result<ArpPacket, NetworkError> {
        if let (Some(local_ip), Some(local_mac)) = (self.local_ip, self.local_mac) {
            Ok(ArpPacket::request(local_mac, local_ip, target_ip))
        } else {
            Err(NetworkError::InvalidAddress)
        }
    }

    /// Get ARP table
    pub fn table(&self) -> &ArpTable {
        &self.table
    }

    /// Clean expired entries
    pub fn cleanup(&mut self, timestamp: u64) {
        self.table.cleanup(timestamp);
    }
}
