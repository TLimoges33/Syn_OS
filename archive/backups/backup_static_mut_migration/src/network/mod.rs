//! # Network Stack Module
//!
//! Comprehensive networking implementation for SynOS Phase 7
//! Provides TCP/IP stack, socket interface, and network device management
//!
//! ## Architecture
//!
//! ```
//! Application Layer    │ User Space Applications
//! ─────────────────────┼─────────────────────────
//! Socket API           │ socket(), bind(), listen(), accept(), connect()
//! Transport Layer      │ TCP (reliable) / UDP (unreliable)
//! Network Layer        │ IP (routing, fragmentation)
//! Data Link Layer      │ Ethernet (frame processing)
//! Physical Layer       │ Network Device Drivers
//! ```

use crate::drivers::{Device, DeviceId, DeviceType, DriverError};
use alloc::{boxed::Box, string::String, vec::Vec};
use core::fmt;

pub mod arp;
pub mod buffer;
pub mod device;
pub mod ethernet;
pub mod ip;
pub mod socket;
pub mod tcp;
pub mod tcp_complete;
pub mod udp;

// Phase 6c: AI-Powered Deep Packet Inspection
pub mod ai_dpi;

pub use device::*;
pub use ethernet::*;
pub use socket::*;

/// Network-specific error types
#[derive(Debug, Clone, PartialEq)]
pub enum NetworkError {
    DeviceNotFound,
    InvalidPacket,
    BufferFull,
    ConnectionClosed,
    ConnectionRefused,
    AddressInUse,
    NetworkUnreachable,
    Timeout,
    InvalidAddress,
    PermissionDenied,
    ResourceBusy,
    NoRoute,
    WouldBlock,
    FragmentationNeeded,
}

impl fmt::Display for NetworkError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            NetworkError::DeviceNotFound => write!(f, "Network device not found"),
            NetworkError::InvalidPacket => write!(f, "Invalid network packet"),
            NetworkError::BufferFull => write!(f, "Network buffer full"),
            NetworkError::ConnectionClosed => write!(f, "Network connection closed"),
            NetworkError::ConnectionRefused => write!(f, "Connection refused"),
            NetworkError::AddressInUse => write!(f, "Address already in use"),
            NetworkError::NetworkUnreachable => write!(f, "Network unreachable"),
            NetworkError::Timeout => write!(f, "Network operation timeout"),
            NetworkError::InvalidAddress => write!(f, "Invalid network address"),
            NetworkError::PermissionDenied => write!(f, "Network permission denied"),
            NetworkError::ResourceBusy => write!(f, "Network resource busy"),
            NetworkError::NoRoute => write!(f, "No route to destination"),
            NetworkError::FragmentationNeeded => write!(f, "IP fragmentation needed"),
            NetworkError::WouldBlock => write!(f, "Operation would block"),
        }
    }
}

/// MAC Address representation
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct MacAddress([u8; 6]);

impl MacAddress {
    pub fn new(bytes: [u8; 6]) -> Self {
        Self(bytes)
    }

    pub fn broadcast() -> Self {
        Self([0xFF; 6])
    }

    pub fn zero() -> Self {
        Self([0; 6])
    }

    pub fn from_bytes(bytes: &[u8]) -> Result<Self, NetworkError> {
        if bytes.len() < 6 {
            return Err(NetworkError::InvalidPacket);
        }
        let mut addr = [0u8; 6];
        addr.copy_from_slice(&bytes[0..6]);
        Ok(Self(addr))
    }

    pub fn to_bytes(&self) -> [u8; 6] {
        self.0
    }

    pub fn bytes(&self) -> &[u8; 6] {
        &self.0
    }

    pub fn is_broadcast(&self) -> bool {
        self.0 == [0xFF; 6]
    }

    pub fn is_unicast(&self) -> bool {
        (self.0[0] & 0x01) == 0
    }

    pub fn is_multicast(&self) -> bool {
        (self.0[0] & 0x01) == 1 && !self.is_broadcast()
    }
}

impl fmt::Display for MacAddress {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}",
            self.0[0], self.0[1], self.0[2], self.0[3], self.0[4], self.0[5]
        )
    }
}

/// IPv4 Address representation
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct Ipv4Address([u8; 4]);

impl Ipv4Address {
    pub fn new(a: u8, b: u8, c: u8, d: u8) -> Self {
        Self([a, b, c, d])
    }

    pub fn from_array(bytes: [u8; 4]) -> Self {
        Self(bytes)
    }

    pub fn from_bytes(bytes: &[u8]) -> Result<Self, NetworkError> {
        if bytes.len() < 4 {
            return Err(NetworkError::InvalidPacket);
        }
        Ok(Self([bytes[0], bytes[1], bytes[2], bytes[3]]))
    }

    pub fn to_bytes(&self) -> [u8; 4] {
        self.0
    }

    pub fn bytes(&self) -> &[u8; 4] {
        &self.0
    }

    pub fn as_u32(&self) -> u32 {
        u32::from_be_bytes(self.0)
    }

    pub fn is_loopback(&self) -> bool {
        self.0[0] == 127
    }

    pub fn is_private(&self) -> bool {
        match self.0[0] {
            10 => true,
            172 => self.0[1] >= 16 && self.0[1] <= 31,
            192 => self.0[1] == 168,
            _ => false,
        }
    }

    pub fn is_broadcast(&self) -> bool {
        self.0 == [255, 255, 255, 255]
    }

    pub fn octets(&self) -> &[u8; 4] {
        &self.0
    }
}

impl fmt::Display for Ipv4Address {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}.{}.{}.{}", self.0[0], self.0[1], self.0[2], self.0[3])
    }
}

/// Network packet abstraction
#[derive(Debug, Clone)]
pub struct NetworkPacket {
    data: Vec<u8>,
    length: usize,
}

impl NetworkPacket {
    pub fn new(data: Vec<u8>) -> Self {
        let length = data.len();
        Self { data, length }
    }

    pub fn with_capacity(capacity: usize) -> Self {
        Self {
            data: Vec::with_capacity(capacity),
            length: 0,
        }
    }

    pub fn data(&self) -> &[u8] {
        &self.data[..self.length]
    }

    pub fn data_mut(&mut self) -> &mut [u8] {
        &mut self.data[..self.length]
    }

    pub fn len(&self) -> usize {
        self.length
    }

    pub fn capacity(&self) -> usize {
        self.data.capacity()
    }

    pub fn is_empty(&self) -> bool {
        self.length == 0
    }

    pub fn push(&mut self, byte: u8) -> Result<(), NetworkError> {
        if self.length >= self.data.capacity() {
            return Err(NetworkError::BufferFull);
        }
        if self.length >= self.data.len() {
            self.data.push(byte);
        } else {
            self.data[self.length] = byte;
        }
        self.length += 1;
        Ok(())
    }

    pub fn extend_from_slice(&mut self, slice: &[u8]) -> Result<(), NetworkError> {
        if self.length + slice.len() > self.data.capacity() {
            return Err(NetworkError::BufferFull);
        }
        for &byte in slice {
            self.push(byte)?;
        }
        Ok(())
    }

    pub fn truncate(&mut self, len: usize) {
        if len < self.length {
            self.length = len;
        }
    }

    pub fn clear(&mut self) {
        self.length = 0;
    }
}

/// Network statistics
#[derive(Debug, Default, Clone)]
pub struct NetworkStats {
    pub packets_sent: u64,
    pub packets_received: u64,
    pub bytes_sent: u64,
    pub bytes_received: u64,
    pub errors: u64,
    pub dropped: u64,
}

impl NetworkStats {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn record_send(&mut self, bytes: usize) {
        self.packets_sent += 1;
        self.bytes_sent += bytes as u64;
    }

    pub fn record_receive(&mut self, bytes: usize) {
        self.packets_received += 1;
        self.bytes_received += bytes as u64;
    }

    pub fn record_error(&mut self) {
        self.errors += 1;
    }

    pub fn record_drop(&mut self) {
        self.dropped += 1;
    }
}

/// Initialize the network stack
pub fn init_network_stack() -> Result<(), NetworkError> {
    // Initialize network subsystems
    buffer::init_network_buffers()?;
    device::init_network_devices()?;

    Ok(())
}

/// Get network stack statistics
pub fn get_network_stats() -> NetworkStats {
    // TODO: Aggregate stats from all network components
    NetworkStats::new()
}

// Syscall support functions - Global socket layer
use spin::Mutex;
use lazy_static::lazy_static;

lazy_static! {
    static ref GLOBAL_SOCKET_LAYER: Mutex<SocketLayer> = Mutex::new(SocketLayer::new());
}

/// Create a network socket
pub fn create_socket(socket_type: u32) -> Result<u32, NetworkError> {
    let mut layer = GLOBAL_SOCKET_LAYER.lock();

    let (domain, sock_type, protocol) = match socket_type {
        0 => (SocketDomain::Inet, SocketType::Stream, SocketProtocol::Tcp), // TCP
        1 => (SocketDomain::Inet, SocketType::Dgram, SocketProtocol::Udp),  // UDP
        _ => return Err(NetworkError::InvalidAddress),
    };

    layer.socket(domain, sock_type, protocol).map(|id| id as u32)
}

/// Send packet through socket
pub fn send_packet(socket_id: u32, data: &[u8]) -> Result<usize, NetworkError> {
    if data.is_empty() {
        return Err(NetworkError::InvalidPacket);
    }

    let mut layer = GLOBAL_SOCKET_LAYER.lock();
    layer.send(socket_id as usize, data.to_vec())
}

/// Receive packet from socket
pub fn receive_packet(socket_id: u32, buffer: &mut [u8]) -> Result<usize, NetworkError> {
    if buffer.is_empty() {
        return Err(NetworkError::BufferFull);
    }

    let mut layer = GLOBAL_SOCKET_LAYER.lock();
    layer.recv(socket_id as usize, buffer)
}

/// Create TCP connection
pub fn create_tcp_connection(addr: &[u8], port: u16) -> Result<u32, NetworkError> {
    if addr.len() != 4 || port == 0 {
        return Err(NetworkError::InvalidAddress);
    }

    let mut layer = GLOBAL_SOCKET_LAYER.lock();
    let ip = Ipv4Address::from_bytes(addr)?;
    let socket_addr = SocketAddr::new(ip, port);

    // Create TCP socket
    let socket_id = layer.socket(SocketDomain::Inet, SocketType::Stream, SocketProtocol::Tcp)?;

    // Connect to remote address
    layer.connect(socket_id, socket_addr)?;

    Ok(socket_id as u32)
}

/// Send TCP packet
pub fn send_tcp_packet(conn_id: u32, data: &[u8]) -> Result<usize, NetworkError> {
    if conn_id == 0 {
        return Err(NetworkError::ConnectionClosed);
    }

    if data.is_empty() {
        return Err(NetworkError::InvalidPacket);
    }

    let mut layer = GLOBAL_SOCKET_LAYER.lock();
    layer.send(conn_id as usize, data.to_vec())
}

/// Route packet with AI hints
pub fn route_packet(dest_addr: &[u8]) -> Result<bool, NetworkError> {
    if dest_addr.len() != 4 {
        return Err(NetworkError::InvalidAddress);
    }

    // Check routing table (placeholder - would use actual routing logic)
    let ip = Ipv4Address::from_bytes(dest_addr)?;

    // Simple routing check: local network vs external
    if ip.octets()[0] == 127 {
        return Ok(true); // Loopback always routable
    }

    Ok(true) // Assume routable for now
}

/// Create consciousness-enhanced connection
pub fn create_consciousness_connection(
    addr: &[u8],
    port: u16,
    consciousness_level: u64,
) -> Result<u32, NetworkError> {
    if addr.len() != 4 || port == 0 {
        return Err(NetworkError::InvalidAddress);
    }

    let mut layer = GLOBAL_SOCKET_LAYER.lock();
    let ip = Ipv4Address::from_bytes(addr)?;
    let socket_addr = SocketAddr::new(ip, port);

    // Create consciousness-optimized socket
    let socket_id = layer.socket(SocketDomain::Inet, SocketType::Stream, SocketProtocol::Tcp)?;

    // Apply consciousness optimization (placeholder for AI-enhanced connection)
    let _ = consciousness_level; // Would use for priority/QoS

    layer.connect(socket_id, socket_addr)?;

    Ok(socket_id as u32)
}

/// Analyze network patterns
pub fn analyze_patterns() -> usize {
    let mut layer = GLOBAL_SOCKET_LAYER.lock();

    // Count active connections and detect patterns
    let tcp_conns = layer.tcp_layer().connections.len();
    let udp_bindings = layer.udp_layer().bindings.len();

    tcp_conns + udp_bindings
}

/// Get connection quality metrics
pub fn get_connection_quality(conn_id: u32) -> Result<u8, NetworkError> {
    if conn_id == 0 {
        return Err(NetworkError::ConnectionClosed);
    }

    let layer = GLOBAL_SOCKET_LAYER.lock();

    if let Some(socket) = layer.get_socket(conn_id as usize) {
        // Calculate quality based on socket state
        let quality = match socket.state {
            SocketState::Connected => 90,
            SocketState::Listening => 80,
            SocketState::Bound => 60,
            SocketState::Connecting => 40,
            SocketState::Disconnecting => 20,
            SocketState::Closed => 0,
        };
        Ok(quality)
    } else {
        Err(NetworkError::ConnectionClosed)
    }
}
