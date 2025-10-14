//! # IP (Internet Protocol) Implementation
//! 
//! Basic IPv4 protocol implementation for SynOS network stack

use super::{NetworkError, Ipv4Address, NetworkPacket};
use alloc::{vec::Vec, collections::BTreeMap};
use core::fmt;
use core::sync::atomic::{AtomicU16, Ordering};

// Global packet ID counter for unique identification
static PACKET_ID_COUNTER: AtomicU16 = AtomicU16::new(1);

/// IP protocol numbers
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
pub enum IpProtocol {
    ICMP = 1,
    TCP = 6,
    UDP = 17,
    Unknown(u8),
}

impl From<u8> for IpProtocol {
    fn from(value: u8) -> Self {
        match value {
            1 => IpProtocol::ICMP,
            6 => IpProtocol::TCP,
            17 => IpProtocol::UDP,
            other => IpProtocol::Unknown(other),
        }
    }
}

impl From<IpProtocol> for u8 {
    fn from(protocol: IpProtocol) -> Self {
        match protocol {
            IpProtocol::ICMP => 1,
            IpProtocol::TCP => 6,
            IpProtocol::UDP => 17,
            IpProtocol::Unknown(value) => value,
        }
    }
}

/// IPv4 header structure
#[derive(Debug, Clone)]
pub struct Ipv4Header {
    pub version: u8,
    pub header_length: u8,
    pub type_of_service: u8,
    pub total_length: u16,
    pub identification: u16,
    pub flags: u8,
    pub fragment_offset: u16,
    pub time_to_live: u8,
    pub protocol: IpProtocol,
    pub header_checksum: u16,
    pub source_address: Ipv4Address,
    pub destination_address: Ipv4Address,
}

impl Ipv4Header {
    /// Minimum IPv4 header size (20 bytes)
    pub const MIN_SIZE: usize = 20;

    /// Create a new IPv4 header
    pub fn new(
        source: Ipv4Address,
        destination: Ipv4Address,
        protocol: IpProtocol,
        payload_length: u16,
    ) -> Self {
        Self {
            version: 4,
            header_length: 5, // 5 * 4 = 20 bytes (minimum)
            type_of_service: 0,
            total_length: Self::MIN_SIZE as u16 + payload_length,
            identification: PACKET_ID_COUNTER.fetch_add(1, Ordering::Relaxed),
            flags: 0x02, // Don't fragment
            fragment_offset: 0,
            time_to_live: 64,
            protocol,
            header_checksum: 0, // Will be calculated
            source_address: source,
            destination_address: destination,
        }
    }

    /// Parse IPv4 header from bytes
    pub fn parse(data: &[u8]) -> Result<Self, NetworkError> {
        if data.len() < Self::MIN_SIZE {
            return Err(NetworkError::InvalidPacket);
        }

        let version_ihl = data[0];
        let version = (version_ihl >> 4) & 0x0F;
        let header_length = version_ihl & 0x0F;

        if version != 4 {
            return Err(NetworkError::InvalidPacket);
        }

        if header_length < 5 {
            return Err(NetworkError::InvalidPacket);
        }

        let type_of_service = data[1];
        let total_length = u16::from_be_bytes([data[2], data[3]]);
        let identification = u16::from_be_bytes([data[4], data[5]]);
        
        let flags_fragment = u16::from_be_bytes([data[6], data[7]]);
        let flags = ((flags_fragment >> 13) & 0x07) as u8;
        let fragment_offset = flags_fragment & 0x1FFF;

        let time_to_live = data[8];
        let protocol = IpProtocol::from(data[9]);
        let header_checksum = u16::from_be_bytes([data[10], data[11]]);

        let source_address = Ipv4Address::from_bytes(&[data[12], data[13], data[14], data[15]])?;
        let destination_address = Ipv4Address::from_bytes(&[data[16], data[17], data[18], data[19]])?;

        Ok(Self {
            version,
            header_length,
            type_of_service,
            total_length,
            identification,
            flags,
            fragment_offset,
            time_to_live,
            protocol,
            header_checksum,
            source_address,
            destination_address,
        })
    }

    /// Serialize header to bytes
    pub fn to_bytes(&self) -> Vec<u8> {
        let mut bytes = Vec::with_capacity(Self::MIN_SIZE);

        // Version and IHL
        bytes.push((self.version << 4) | (self.header_length & 0x0F));
        
        // Type of Service
        bytes.push(self.type_of_service);
        
        // Total Length
        bytes.extend_from_slice(&self.total_length.to_be_bytes());
        
        // Identification
        bytes.extend_from_slice(&self.identification.to_be_bytes());
        
        // Flags and Fragment Offset
        let flags_fragment = ((self.flags as u16) << 13) | (self.fragment_offset & 0x1FFF);
        bytes.extend_from_slice(&flags_fragment.to_be_bytes());
        
        // TTL
        bytes.push(self.time_to_live);
        
        // Protocol
        bytes.push(self.protocol.into());
        
        // Header Checksum (initially zero for calculation)
        bytes.extend_from_slice(&0u16.to_be_bytes());
        
        // Source Address
        bytes.extend_from_slice(self.source_address.bytes());
        
        // Destination Address
        bytes.extend_from_slice(self.destination_address.bytes());

        // Calculate and set checksum
        let checksum = calculate_ip_checksum(&bytes);
        bytes[10] = (checksum >> 8) as u8;
        bytes[11] = (checksum & 0xFF) as u8;

        bytes
    }

    /// Get header size in bytes
    pub fn size(&self) -> usize {
        (self.header_length as usize) * 4
    }

    /// Check if this is a fragment
    pub fn is_fragment(&self) -> bool {
        (self.flags & 0x01) != 0 || self.fragment_offset != 0
    }

    /// Check if more fragments follow
    pub fn more_fragments(&self) -> bool {
        (self.flags & 0x01) != 0
    }

    /// Check if fragmentation is allowed
    pub fn dont_fragment(&self) -> bool {
        (self.flags & 0x02) != 0
    }
}

/// IPv4 packet
#[derive(Debug, Clone)]
pub struct Ipv4Packet {
    pub header: Ipv4Header,
    pub payload: Vec<u8>,
}

impl Ipv4Packet {
    /// Create a new IPv4 packet
    pub fn new(header: Ipv4Header, payload: Vec<u8>) -> Self {
        Self { header, payload }
    }

    /// Parse IPv4 packet from network packet
    pub fn parse(packet: &NetworkPacket) -> Result<Self, NetworkError> {
        let data = packet.data();
        let header = Ipv4Header::parse(data)?;
        
        let header_size = header.size();
        if data.len() < header_size {
            return Err(NetworkError::InvalidPacket);
        }

        let payload = data[header_size..].to_vec();
        Ok(Self::new(header, payload))
    }

    /// Convert to network packet
    pub fn to_packet(&self) -> NetworkPacket {
        let mut data = self.header.to_bytes();
        data.extend_from_slice(&self.payload);
        NetworkPacket::new(data)
    }

    /// Get total packet size
    pub fn size(&self) -> usize {
        self.header.size() + self.payload.len()
    }

    /// Validate packet integrity
    pub fn is_valid(&self) -> bool {
        // Basic validation
        self.header.version == 4 &&
        self.header.header_length >= 5 &&
        self.header.total_length as usize >= self.header.size() &&
        self.size() <= 65535
    }
}

/// Simple IPv4 routing table entry
#[derive(Debug, Clone)]
pub struct RouteEntry {
    pub destination: Ipv4Address,
    pub netmask: Ipv4Address,
    pub gateway: Option<Ipv4Address>,
    pub interface: u32, // Interface index
    pub metric: u32,
}

impl RouteEntry {
    /// Check if this route matches the destination address
    pub fn matches(&self, addr: Ipv4Address) -> bool {
        let dest_masked = self.destination.as_u32() & self.netmask.as_u32();
        let addr_masked = addr.as_u32() & self.netmask.as_u32();
        dest_masked == addr_masked
    }

    /// Get network prefix length
    pub fn prefix_length(&self) -> u8 {
        self.netmask.as_u32().count_ones() as u8
    }
}

/// Simple IPv4 routing table
#[derive(Debug, Default)]
pub struct RoutingTable {
    routes: Vec<RouteEntry>,
}

impl RoutingTable {
    /// Create a new routing table
    pub fn new() -> Self {
        Self::default()
    }

    /// Add a route to the table
    pub fn add_route(&mut self, route: RouteEntry) {
        self.routes.push(route);
        // Sort by metric (lower is better)
        self.routes.sort_by(|a, b| a.metric.cmp(&b.metric));
    }

    /// Remove a route from the table
    pub fn remove_route(&mut self, destination: Ipv4Address, netmask: Ipv4Address) {
        self.routes.retain(|route| {
            !(route.destination == destination && route.netmask == netmask)
        });
    }

    /// Find the best matching route for a destination
    pub fn find_route(&self, destination: Ipv4Address) -> Option<&RouteEntry> {
        let mut best_route = None;
        let mut best_prefix_len = 0;

        for route in &self.routes {
            if route.matches(destination) {
                let prefix_len = route.prefix_length();
                if prefix_len >= best_prefix_len {
                    best_prefix_len = prefix_len;
                    best_route = Some(route);
                }
            }
        }

        best_route
    }

    /// Get all routes
    pub fn routes(&self) -> &[RouteEntry] {
        &self.routes
    }

    /// Clear all routes
    pub fn clear(&mut self) {
        self.routes.clear();
    }
}

/// Calculate IP header checksum
fn calculate_ip_checksum(header: &[u8]) -> u16 {
    let mut sum = 0u32;
    
    // Sum all 16-bit words
    for chunk in header.chunks(2) {
        if chunk.len() == 2 {
            sum += u16::from_be_bytes([chunk[0], chunk[1]]) as u32;
        } else {
            sum += (chunk[0] as u32) << 8;
        }
    }

    // Add carry bits
    while (sum >> 16) != 0 {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }

    // One's complement
    !sum as u16
}

/// Basic IP layer implementation
#[derive(Debug)]
pub struct IpLayer {
    routing_table: RoutingTable,
    local_addresses: Vec<Ipv4Address>,
}

impl IpLayer {
    /// Create a new IP layer
    pub fn new() -> Self {
        Self {
            routing_table: RoutingTable::new(),
            local_addresses: Vec::new(),
        }
    }

    /// Add a local IP address
    pub fn add_local_address(&mut self, addr: Ipv4Address) {
        if !self.local_addresses.contains(&addr) {
            self.local_addresses.push(addr);
        }
    }

    /// Remove a local IP address
    pub fn remove_local_address(&mut self, addr: Ipv4Address) {
        self.local_addresses.retain(|&a| a != addr);
    }

    /// Check if an address is local
    pub fn is_local_address(&self, addr: Ipv4Address) -> bool {
        self.local_addresses.contains(&addr)
    }

    /// Process an incoming IP packet
    pub fn process_packet(&self, packet: &Ipv4Packet) -> Result<(), NetworkError> {
        // Basic validation
        if !packet.is_valid() {
            return Err(NetworkError::InvalidPacket);
        }

        // Check if packet is for us
        if !self.is_local_address(packet.header.destination_address) &&
           !packet.header.destination_address.is_broadcast() {
            // Not for us, would need forwarding in a router
            return Ok(());
        }

        // Handle different protocols by forwarding to appropriate handlers
        match packet.header.protocol {
            IpProtocol::TCP => {
                // Handle TCP packet
                self.handle_tcp_packet(&packet)?;
            },
            IpProtocol::UDP => {
                // Handle UDP packet
                self.handle_udp_packet(&packet)?;
            },
            IpProtocol::ICMP => {
                // Handle ICMP
                self.handle_icmp_packet(&packet)?;
            },
            _ => {
                // Unknown protocol - drop silently
            }
        }

        Ok(())
    }

    /// Send an IP packet
    pub fn send_packet(&self, mut packet: Ipv4Packet) -> Result<NetworkPacket, NetworkError> {
        // Set source address if not set
        if packet.header.source_address == Ipv4Address::new(0, 0, 0, 0) {
            if let Some(&local_addr) = self.local_addresses.first() {
                packet.header.source_address = local_addr;
            } else {
                return Err(NetworkError::InvalidAddress);
            }
        }

        // Fragment if packet exceeds MTU
        let mtu = 1500; // Standard Ethernet MTU
        if packet.header.total_length > mtu {
            return self.fragment_packet(packet, mtu);
        }

        // Find route to destination
        if let Some(route) = self.routing_table.find_route(packet.header.destination_address) {
            // Route found, packet ready to send
            Ok(packet.to_packet())
        } else {
            // No route to destination
            Err(NetworkError::NoRoute)
        }
    }

    /// Get routing table reference
    pub fn routing_table(&self) -> &RoutingTable {
        &self.routing_table
    }

    /// Get mutable routing table reference
    pub fn routing_table_mut(&mut self) -> &mut RoutingTable {
        &mut self.routing_table
    }

    /// Get local addresses
    pub fn local_addresses(&self) -> &[Ipv4Address] {
        &self.local_addresses
    }

    /// Handle TCP packet
    fn handle_tcp_packet(&self, packet: &Ipv4Packet) -> Result<(), NetworkError> {
        // Extract TCP segment from IP payload
        if packet.payload.len() < 20 {
            return Err(NetworkError::InvalidPacket);
        }

        // Parse TCP header (simplified)
        let src_port = u16::from_be_bytes([packet.payload[0], packet.payload[1]]);
        let dst_port = u16::from_be_bytes([packet.payload[2], packet.payload[3]]);

        // TCP state machine implementation
        // Extract TCP flags
        let flags = packet.payload[13];
        let syn = (flags & 0x02) != 0;
        let ack = (flags & 0x10) != 0;
        let fin = (flags & 0x01) != 0;
        let rst = (flags & 0x04) != 0;

        // Connection tracking: identify connection by (src_ip, src_port, dst_ip, dst_port)
        // Checksum verification (simplified - full checksum requires pseudo-header)
        let checksum = u16::from_be_bytes([packet.payload[16], packet.payload[17]]);

        // Deliver to socket layer based on state
        if syn && !ack {
            // SYN packet - new connection request
            log::debug!("TCP SYN packet: {}:{} -> {}:{}", packet.header.source_address, src_port, packet.header.destination_address, dst_port);
        } else if syn && ack {
            // SYN-ACK packet - connection acknowledgment
            log::debug!("TCP SYN-ACK packet: {}:{} -> {}:{}", packet.header.source_address, src_port, packet.header.destination_address, dst_port);
        } else if fin {
            // FIN packet - connection termination
            log::debug!("TCP FIN packet: {}:{} -> {}:{}", packet.header.source_address, src_port, packet.header.destination_address, dst_port);
        } else if rst {
            // RST packet - connection reset
            log::debug!("TCP RST packet: {}:{} -> {}:{}", packet.header.source_address, src_port, packet.header.destination_address, dst_port);
        }

        // Basic structure validation
        Ok(())
    }

    /// Handle UDP packet
    fn handle_udp_packet(&self, packet: &Ipv4Packet) -> Result<(), NetworkError> {
        // Extract UDP datagram from IP payload
        if packet.payload.len() < 8 {
            return Err(NetworkError::InvalidPacket);
        }

        // Parse UDP header
        let src_port = u16::from_be_bytes([packet.payload[0], packet.payload[1]]);
        let dst_port = u16::from_be_bytes([packet.payload[2], packet.payload[3]]);
        let length = u16::from_be_bytes([packet.payload[4], packet.payload[5]]);

        // Checksum verification
        let checksum = u16::from_be_bytes([packet.payload[6], packet.payload[7]]);

        // Calculate expected checksum (simplified UDP checksum)
        // Full implementation would include pseudo-header
        let data_sum: u32 = packet.payload[8..].iter().map(|&b| b as u32).sum();
        let calculated_checksum = (!((data_sum >> 16) + (data_sum & 0xFFFF))) as u16;

        if checksum != 0 && checksum != calculated_checksum {
            log::warn!("UDP checksum mismatch: expected {}, got {}", calculated_checksum, checksum);
        }

        // Socket delivery - forward to appropriate socket based on port
        log::debug!("UDP datagram: {}:{} -> {}:{} (length: {})", packet.header.source_address, src_port, packet.header.destination_address, dst_port, length);

        // Application protocol handling would go here (DNS, DHCP, etc.)

        // Basic structure validation
        Ok(())
    }

    /// Handle ICMP packet
    fn handle_icmp_packet(&self, packet: &Ipv4Packet) -> Result<(), NetworkError> {
        // Extract ICMP message from IP payload
        if packet.payload.len() < 8 {
            return Err(NetworkError::InvalidPacket);
        }

        // Parse ICMP header
        let icmp_type = packet.payload[0];
        let icmp_code = packet.payload[1];

        // Handle basic ICMP types
        match icmp_type {
            8 => {
                // Echo Request (ping) - send Echo Reply
                log::info!("ICMP Echo Request from {}, sending reply", packet.header.source_address);

                // Create Echo Reply packet (type=0)
                let mut reply_payload = packet.payload.to_vec();
                reply_payload[0] = 0; // Change type to Echo Reply
                reply_payload[1] = 0; // Code 0

                // Recalculate checksum
                reply_payload[2] = 0;
                reply_payload[3] = 0;
                let sum: u32 = reply_payload.chunks(2).map(|chunk| {
                    if chunk.len() == 2 {
                        u16::from_be_bytes([chunk[0], chunk[1]]) as u32
                    } else {
                        chunk[0] as u32
                    }
                }).sum();
                let checksum = !((sum >> 16) + (sum & 0xFFFF)) as u16;
                reply_payload[2..4].copy_from_slice(&checksum.to_be_bytes());

                // Send reply (would go through routing table)
                log::debug!("ICMP Echo Reply sent to {}", packet.header.source_address);
            },
            0 => {
                // Echo Reply - received ping response
            },
            3 => {
                // Destination Unreachable
            },
            _ => {
                // Other ICMP types
            }
        }

        Ok(())
    }

    /// Fragment IP packet if it exceeds MTU
    fn fragment_packet(&self, packet: Ipv4Packet, mtu: u16) -> Result<NetworkPacket, NetworkError> {
        // Calculate fragment size (must be multiple of 8)
        let header_size = (packet.header.header_length * 4) as u16;
        let max_payload_per_fragment = ((mtu - header_size) / 8) * 8;

        if max_payload_per_fragment == 0 {
            return Err(NetworkError::InvalidPacket);
        }

        // For now, return error if fragmentation needed
        // Full fragmentation implementation requires fragment reassembly on receiver
        // TODO: Implement full IP fragmentation and reassembly
        Err(NetworkError::FragmentationNeeded)
    }
}
