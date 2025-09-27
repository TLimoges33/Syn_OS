//! # UDP (User Datagram Protocol) Implementation
//! 
//! Basic UDP protocol implementation for SynOS network stack

use super::{NetworkError, Ipv4Address};
use alloc::vec::Vec;

/// UDP header structure
#[derive(Debug, Clone)]
pub struct UdpHeader {
    pub source_port: u16,
    pub destination_port: u16,
    pub length: u16,
    pub checksum: u16,
}

impl UdpHeader {
    /// UDP header size (8 bytes)
    pub const SIZE: usize = 8;

    /// Create a new UDP header
    pub fn new(source_port: u16, dest_port: u16, payload_length: u16) -> Self {
        Self {
            source_port,
            destination_port: dest_port,
            length: Self::SIZE as u16 + payload_length,
            checksum: 0,
        }
    }

    /// Parse UDP header from bytes
    pub fn parse(data: &[u8]) -> Result<Self, NetworkError> {
        if data.len() < Self::SIZE {
            return Err(NetworkError::InvalidPacket);
        }

        Ok(Self {
            source_port: u16::from_be_bytes([data[0], data[1]]),
            destination_port: u16::from_be_bytes([data[2], data[3]]),
            length: u16::from_be_bytes([data[4], data[5]]),
            checksum: u16::from_be_bytes([data[6], data[7]]),
        })
    }

    /// Serialize header to bytes
    pub fn to_bytes(&self) -> [u8; Self::SIZE] {
        let mut bytes = [0u8; Self::SIZE];
        
        bytes[0..2].copy_from_slice(&self.source_port.to_be_bytes());
        bytes[2..4].copy_from_slice(&self.destination_port.to_be_bytes());
        bytes[4..6].copy_from_slice(&self.length.to_be_bytes());
        bytes[6..8].copy_from_slice(&self.checksum.to_be_bytes());
        
        bytes
    }
}

/// UDP datagram
#[derive(Debug, Clone)]
pub struct UdpDatagram {
    pub header: UdpHeader,
    pub payload: Vec<u8>,
}

impl UdpDatagram {
    /// Create a new UDP datagram
    pub fn new(source_port: u16, dest_port: u16, payload: Vec<u8>) -> Self {
        let header = UdpHeader::new(source_port, dest_port, payload.len() as u16);
        Self { header, payload }
    }

    /// Parse UDP datagram from bytes
    pub fn parse(data: &[u8]) -> Result<Self, NetworkError> {
        let header = UdpHeader::parse(data)?;
        
        if data.len() < header.length as usize {
            return Err(NetworkError::InvalidPacket);
        }

        let payload = data[UdpHeader::SIZE..header.length as usize].to_vec();
        Ok(Self { header, payload })
    }

    /// Serialize datagram to bytes
    pub fn to_bytes(&self) -> Vec<u8> {
        let mut bytes = Vec::with_capacity(UdpHeader::SIZE + self.payload.len());
        bytes.extend_from_slice(&self.header.to_bytes());
        bytes.extend_from_slice(&self.payload);
        bytes
    }

    /// Get total datagram size
    pub fn size(&self) -> usize {
        UdpHeader::SIZE + self.payload.len()
    }
}

/// UDP socket binding
#[derive(Debug, Clone)]
pub struct UdpBinding {
    pub local_addr: Ipv4Address,
    pub local_port: u16,
    pub remote_addr: Option<Ipv4Address>,
    pub remote_port: Option<u16>,
}

impl UdpBinding {
    /// Create a new UDP binding
    pub fn new(local_addr: Ipv4Address, local_port: u16) -> Self {
        Self {
            local_addr,
            local_port,
            remote_addr: None,
            remote_port: None,
        }
    }

    /// Connect to a remote address
    pub fn connect(&mut self, remote_addr: Ipv4Address, remote_port: u16) {
        self.remote_addr = Some(remote_addr);
        self.remote_port = Some(remote_port);
    }

    /// Check if this binding matches the address and port
    pub fn matches(&self, addr: Ipv4Address, port: u16) -> bool {
        (self.local_addr == addr || self.local_addr == Ipv4Address::new(0, 0, 0, 0)) &&
        self.local_port == port
    }
}

/// UDP layer implementation
#[derive(Debug)]
pub struct UdpLayer {
    bindings: Vec<UdpBinding>,
}

impl UdpLayer {
    /// Create a new UDP layer
    pub fn new() -> Self {
        Self {
            bindings: Vec::new(),
        }
    }

    /// Bind to a local address and port
    pub fn bind(&mut self, local_addr: Ipv4Address, port: u16) -> Result<usize, NetworkError> {
        // Check if port is already in use
        if self.bindings.iter().any(|b| b.local_port == port && b.local_addr == local_addr) {
            return Err(NetworkError::AddressInUse);
        }

        let binding = UdpBinding::new(local_addr, port);
        self.bindings.push(binding);
        Ok(self.bindings.len() - 1)
    }

    /// Send a UDP datagram
    pub fn send(&self, binding_id: usize, dest_addr: Ipv4Address, dest_port: u16, data: Vec<u8>) -> Result<UdpDatagram, NetworkError> {
        if let Some(binding) = self.bindings.get(binding_id) {
            let datagram = UdpDatagram::new(binding.local_port, dest_port, data);
            Ok(datagram)
        } else {
            Err(NetworkError::InvalidAddress)
        }
    }

    /// Process incoming UDP datagram
    pub fn process_datagram(&self, source_addr: Ipv4Address, dest_addr: Ipv4Address, datagram: &UdpDatagram) -> Result<Option<usize>, NetworkError> {
        // Find matching binding
        for (id, binding) in self.bindings.iter().enumerate() {
            if binding.matches(dest_addr, datagram.header.destination_port) {
                // Check if connected and source matches
                if let (Some(remote_addr), Some(remote_port)) = (binding.remote_addr, binding.remote_port) {
                    if source_addr == remote_addr && datagram.header.source_port == remote_port {
                        return Ok(Some(id));
                    }
                } else {
                    // Unconnected socket, accept from any source
                    return Ok(Some(id));
                }
            }
        }

        Ok(None)
    }

    /// Get binding by ID
    pub fn get_binding(&self, id: usize) -> Option<&UdpBinding> {
        self.bindings.get(id)
    }

    /// Get mutable binding by ID
    pub fn get_binding_mut(&mut self, id: usize) -> Option<&mut UdpBinding> {
        self.bindings.get_mut(id)
    }

    /// Remove binding
    pub fn unbind(&mut self, id: usize) -> Result<(), NetworkError> {
        if id < self.bindings.len() {
            self.bindings.remove(id);
            Ok(())
        } else {
            Err(NetworkError::InvalidAddress)
        }
    }

    /// Allocate an available port
    pub fn allocate_port(&self) -> Result<u16, NetworkError> {
        // Simple port allocation starting from 32768
        for port in 32768..65536 {
            if !self.bindings.iter().any(|b| b.local_port == port) {
                return Ok(port);
            }
        }
        Err(NetworkError::AddressInUse)
    }
}
