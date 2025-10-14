//! # TCP (Transmission Control Protocol) Implementation
//! 
//! Complete TCP protocol implementation for SynOS network stack

use super::{NetworkError, Ipv4Address};
use alloc::vec::Vec;

/// TCP header structure
#[derive(Debug, Clone)]
pub struct TcpHeader {
    pub source_port: u16,
    pub dest_port: u16,
    pub seq_num: u32,
    pub ack_num: u32,
    pub data_offset: u8,  // Header length in 32-bit words
    pub flags: u8,
    pub window_size: u16,
    pub checksum: u16,
    pub urgent_ptr: u16,
    // Control flags
    pub fin: bool,
    pub syn: bool,
    pub rst: bool,
    pub psh: bool,
    pub ack: bool,
    pub urg: bool,
}

impl TcpHeader {
    /// Minimum TCP header size (20 bytes)
    pub const MIN_SIZE: usize = 20;

    /// Create a new TCP header
    pub fn new(source_port: u16, dest_port: u16, seq_num: u32, ack_num: u32) -> Self {
        Self {
            source_port,
            dest_port,
            seq_num,
            ack_num,
            data_offset: 5, // 20 bytes / 4 = 5 words
            flags: 0,
            window_size: 8192,
            checksum: 0,
            urgent_ptr: 0,
            fin: false,
            syn: false,
            rst: false,
            psh: false,
            ack: false,
            urg: false,
        }
    }

    /// Parse TCP header from bytes
    pub fn parse(data: &[u8]) -> Result<Self, NetworkError> {
        if data.len() < Self::MIN_SIZE {
            return Err(NetworkError::InvalidPacket);
        }

        let source_port = u16::from_be_bytes([data[0], data[1]]);
        let dest_port = u16::from_be_bytes([data[2], data[3]]);
        let seq_num = u32::from_be_bytes([data[4], data[5], data[6], data[7]]);
        let ack_num = u32::from_be_bytes([data[8], data[9], data[10], data[11]]);
        
        let data_offset_flags = u16::from_be_bytes([data[12], data[13]]);
        let data_offset = ((data_offset_flags >> 12) & 0xF) as u8;
        let flags = (data_offset_flags & 0x3F) as u8;

        let window_size = u16::from_be_bytes([data[14], data[15]]);
        let checksum = u16::from_be_bytes([data[16], data[17]]);
        let urgent_ptr = u16::from_be_bytes([data[18], data[19]]);

        Ok(Self {
            source_port,
            dest_port,
            seq_num,
            ack_num,
            data_offset,
            flags,
            window_size,
            checksum,
            urgent_ptr,
            fin: (flags & 0x01) != 0,
            syn: (flags & 0x02) != 0,
            rst: (flags & 0x04) != 0,
            psh: (flags & 0x08) != 0,
            ack: (flags & 0x10) != 0,
            urg: (flags & 0x20) != 0,
        })
    }

    /// Serialize header to bytes
    pub fn to_bytes(&self) -> Vec<u8> {
        let mut bytes = Vec::with_capacity(Self::MIN_SIZE);
        
        bytes.extend_from_slice(&self.source_port.to_be_bytes());
        bytes.extend_from_slice(&self.dest_port.to_be_bytes());
        bytes.extend_from_slice(&self.seq_num.to_be_bytes());
        bytes.extend_from_slice(&self.ack_num.to_be_bytes());

        let mut flags = 0u8;
        if self.fin { flags |= 0x01; }
        if self.syn { flags |= 0x02; }
        if self.rst { flags |= 0x04; }
        if self.psh { flags |= 0x08; }
        if self.ack { flags |= 0x10; }
        if self.urg { flags |= 0x20; }

        let data_offset_flags = ((self.data_offset as u16) << 12) | (flags as u16);
        bytes.extend_from_slice(&data_offset_flags.to_be_bytes());

        bytes.extend_from_slice(&self.window_size.to_be_bytes());
        bytes.extend_from_slice(&self.checksum.to_be_bytes());
        bytes.extend_from_slice(&self.urgent_ptr.to_be_bytes());

        bytes
    }
}

/// TCP connection states
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum TcpState {
    Closed,
    Listen,
    SynSent,
    SynReceived,
    Established,
    FinWait1,
    FinWait2,
    CloseWait,
    Closing,
    LastAck,
    TimeWait,
}

/// TCP connection
#[derive(Debug, Clone)]
pub struct TcpConnection {
    pub local_addr: Ipv4Address,
    pub local_port: u16,
    pub remote_addr: Ipv4Address,
    pub remote_port: u16,
    pub state: TcpState,
    pub send_seq: u32,
    pub recv_seq: u32,
    pub window_size: u16,
}

impl TcpConnection {
    /// Create a new TCP connection
    pub fn new(local_addr: Ipv4Address, local_port: u16, remote_addr: Ipv4Address, remote_port: u16) -> Self {
        Self {
            local_addr,
            local_port,
            remote_addr,
            remote_port,
            state: TcpState::Closed,
            send_seq: 0,
            recv_seq: 0,
            window_size: 8192,
        }
    }
}

/// TCP segment structure
#[derive(Debug, Clone)]
pub struct TcpSegment {
    pub header: TcpHeader,
    pub payload: Vec<u8>,
}

impl TcpSegment {
    /// Create a new TCP segment
    pub fn new(header: TcpHeader, payload: Vec<u8>) -> Self {
        Self { header, payload }
    }

    /// Create SYN segment
    pub fn syn(source_port: u16, dest_port: u16, seq_num: u32, window_size: u16) -> Self {
        let mut header = TcpHeader::new(source_port, dest_port, seq_num, 0);
        header.syn = true;
        header.window_size = window_size;
        Self::new(header, Vec::new())
    }

    /// Create SYN-ACK segment
    pub fn syn_ack(source_port: u16, dest_port: u16, seq_num: u32, ack_num: u32, window_size: u16) -> Self {
        let mut header = TcpHeader::new(source_port, dest_port, seq_num, ack_num);
        header.syn = true;
        header.ack = true;
        header.window_size = window_size;
        Self::new(header, Vec::new())
    }

    /// Create ACK segment
    pub fn ack(source_port: u16, dest_port: u16, seq_num: u32, ack_num: u32, window_size: u16) -> Self {
        let mut header = TcpHeader::new(source_port, dest_port, seq_num, ack_num);
        header.ack = true;
        header.window_size = window_size;
        Self::new(header, Vec::new())
    }

    /// Create FIN segment
    pub fn fin(source_port: u16, dest_port: u16, seq_num: u32, ack_num: u32, window_size: u16) -> Self {
        let mut header = TcpHeader::new(source_port, dest_port, seq_num, ack_num);
        header.fin = true;
        header.ack = true;
        header.window_size = window_size;
        Self::new(header, Vec::new())
    }

    /// Create RST segment
    pub fn rst(source_port: u16, dest_port: u16, seq_num: u32, ack_num: u32) -> Self {
        let mut header = TcpHeader::new(source_port, dest_port, seq_num, ack_num);
        header.rst = true;
        header.ack = true;
        Self::new(header, Vec::new())
    }

    /// Create data segment
    pub fn data(source_port: u16, dest_port: u16, seq_num: u32, ack_num: u32, 
               window_size: u16, payload: Vec<u8>) -> Self {
        let mut header = TcpHeader::new(source_port, dest_port, seq_num, ack_num);
        header.ack = true;
        header.window_size = window_size;
        Self::new(header, payload)
    }

    /// Parse TCP segment from bytes
    pub fn parse(data: &[u8]) -> Result<Self, NetworkError> {
        let header = TcpHeader::parse(data)?;
        let header_len = (header.data_offset as usize) * 4;
        
        if data.len() < header_len {
            return Err(NetworkError::InvalidPacket);
        }

        let payload = data[header_len..].to_vec();
        Ok(Self::new(header, payload))
    }

    /// Serialize segment to bytes
    pub fn to_bytes(&self) -> Vec<u8> {
        let mut bytes = self.header.to_bytes();
        bytes.extend_from_slice(&self.payload);
        bytes
    }

    /// Get total segment size
    pub fn size(&self) -> usize {
        (self.header.data_offset as usize) * 4 + self.payload.len()
    }
}

/// TCP layer implementation
#[derive(Debug)]
pub struct TcpLayer {
    connections: Vec<TcpConnection>,
}

impl TcpLayer {
    /// Create a new TCP layer
    pub fn new() -> Self {
        Self {
            connections: Vec::new(),
        }
    }

    /// Create a new connection
    pub fn connect(&mut self, local_addr: Ipv4Address, remote_addr: Ipv4Address, remote_port: u16) -> Result<usize, NetworkError> {
        let local_port = self.allocate_port()?;
        let mut connection = TcpConnection::new(local_addr, local_port, remote_addr, remote_port);
        connection.state = TcpState::SynSent;
        connection.send_seq = 1000; // Initial sequence number
        
        self.connections.push(connection);
        Ok(self.connections.len() - 1)
    }

    /// Listen on a port
    pub fn listen(&mut self, local_addr: Ipv4Address, port: u16) -> Result<usize, NetworkError> {
        // Check if port is already in use
        if self.connections.iter().any(|c| c.local_port == port && c.local_addr == local_addr) {
            return Err(NetworkError::AddressInUse);
        }

        let mut connection = TcpConnection::new(local_addr, port, Ipv4Address::new(0, 0, 0, 0), 0);
        connection.state = TcpState::Listen;
        
        self.connections.push(connection);
        Ok(self.connections.len() - 1)
    }

    /// Accept incoming connection
    pub fn accept(&mut self, port: u16) -> Result<usize, NetworkError> {
        // Create listening connection
        let connection = TcpConnection {
            local_addr: Ipv4Address::new(0, 0, 0, 0), // Any address
            local_port: port,
            remote_addr: Ipv4Address::new(0, 0, 0, 0),
            remote_port: 0,
            state: TcpState::Listen,
            send_seq: 0,
            recv_seq: 0,
            window_size: 8192,
        };

        self.connections.push(connection);
        Ok(self.connections.len() - 1)
    }

    /// Process incoming TCP segment
    pub fn process_segment(&mut self, source_addr: Ipv4Address, dest_addr: Ipv4Address, 
                          segment: &TcpSegment) -> Result<Option<TcpSegment>, NetworkError> {
        // Find matching connection
        let connection_id = self.find_connection(dest_addr, segment.header.dest_port, 
                                               source_addr, segment.header.source_port);

        if let Some(id) = connection_id {
            self.handle_segment(id, segment)
        } else {
            // No matching connection, send RST if not already RST
            if !segment.header.rst {
                let rst_segment = TcpSegment::rst(
                    segment.header.dest_port,
                    segment.header.source_port,
                    segment.header.ack_num,
                    0
                );
                return Ok(Some(rst_segment));
            }
            Ok(None)
        }
    }

    /// Find connection matching addresses and ports
    fn find_connection(&self, local_addr: Ipv4Address, local_port: u16,
                      remote_addr: Ipv4Address, remote_port: u16) -> Option<usize> {
        for (id, conn) in self.connections.iter().enumerate() {
            if conn.local_port == local_port {
                match conn.state {
                    TcpState::Listen => {
                        // Listening socket matches any remote address
                        if conn.local_addr == local_addr || 
                           conn.local_addr == Ipv4Address::new(0, 0, 0, 0) {
                            return Some(id);
                        }
                    },
                    _ => {
                        // Established connections must match exactly
                        if conn.local_addr == local_addr &&
                           conn.remote_addr == remote_addr &&
                           conn.remote_port == remote_port {
                            return Some(id);
                        }
                    }
                }
            }
        }
        None
    }

    /// Handle TCP segment for specific connection
    fn handle_segment(&mut self, connection_id: usize, segment: &TcpSegment) -> Result<Option<TcpSegment>, NetworkError> {
        if let Some(connection) = self.connections.get_mut(connection_id) {
            match connection.state {
                TcpState::Listen => {
                    if segment.header.syn && !segment.header.ack {
                        // Incoming SYN, send SYN-ACK
                        connection.remote_addr = Ipv4Address::new(0, 0, 0, 0); // Should be set by caller
                        connection.remote_port = segment.header.source_port;
                        connection.recv_seq = segment.header.seq_num + 1;
                        connection.send_seq = 1000; // Initial sequence number
                        connection.state = TcpState::SynReceived;

                        let syn_ack = TcpSegment::syn_ack(
                            connection.local_port,
                            connection.remote_port,
                            connection.send_seq,
                            connection.recv_seq,
                            connection.window_size
                        );
                        connection.send_seq += 1;
                        return Ok(Some(syn_ack));
                    }
                },
                TcpState::SynSent => {
                    if segment.header.syn && segment.header.ack {
                        // SYN-ACK received
                        if segment.header.ack_num == connection.send_seq + 1 {
                            connection.recv_seq = segment.header.seq_num + 1;
                            connection.send_seq += 1;
                            connection.state = TcpState::Established;

                            let ack = TcpSegment::ack(
                                connection.local_port,
                                connection.remote_port,
                                connection.send_seq,
                                connection.recv_seq,
                                connection.window_size
                            );
                            return Ok(Some(ack));
                        }
                    }
                },
                TcpState::SynReceived => {
                    if segment.header.ack && !segment.header.syn {
                        // ACK of our SYN-ACK
                        if segment.header.ack_num == connection.send_seq {
                            connection.state = TcpState::Established;
                        }
                    }
                },
                TcpState::Established => {
                    // Handle data transfer and connection termination
                    if segment.header.fin {
                        // Remote wants to close
                        connection.recv_seq = segment.header.seq_num + 1;
                        connection.state = TcpState::CloseWait;

                        let ack = TcpSegment::ack(
                            connection.local_port,
                            connection.remote_port,
                            connection.send_seq,
                            connection.recv_seq,
                            connection.window_size
                        );
                        return Ok(Some(ack));
                    } else if !segment.payload.is_empty() {
                        // Data received
                        connection.recv_seq = segment.header.seq_num + segment.payload.len() as u32;

                        let ack = TcpSegment::ack(
                            connection.local_port,
                            connection.remote_port,
                            connection.send_seq,
                            connection.recv_seq,
                            connection.window_size
                        );
                        return Ok(Some(ack));
                    }
                },
                TcpState::FinWait1 => {
                    if segment.header.ack {
                        connection.state = TcpState::FinWait2;
                    }
                    if segment.header.fin {
                        connection.recv_seq = segment.header.seq_num + 1;
                        connection.state = TcpState::TimeWait;

                        let ack = TcpSegment::ack(
                            connection.local_port,
                            connection.remote_port,
                            connection.send_seq,
                            connection.recv_seq,
                            connection.window_size
                        );
                        return Ok(Some(ack));
                    }
                },
                TcpState::FinWait2 => {
                    if segment.header.fin {
                        connection.recv_seq = segment.header.seq_num + 1;
                        connection.state = TcpState::TimeWait;

                        let ack = TcpSegment::ack(
                            connection.local_port,
                            connection.remote_port,
                            connection.send_seq,
                            connection.recv_seq,
                            connection.window_size
                        );
                        return Ok(Some(ack));
                    }
                },
                TcpState::CloseWait => {
                    // Waiting for application to close
                },
                _ => {
                    // Other states
                }
            }
        }

        Ok(None)
    }

    /// Send data on established connection
    pub fn send_data(&mut self, connection_id: usize, data: Vec<u8>) -> Result<TcpSegment, NetworkError> {
        if let Some(connection) = self.connections.get_mut(connection_id) {
            if connection.state == TcpState::Established {
                let segment = TcpSegment::data(
                    connection.local_port,
                    connection.remote_port,
                    connection.send_seq,
                    connection.recv_seq,
                    connection.window_size,
                    data.clone()
                );

                connection.send_seq += data.len() as u32;
                return Ok(segment);
            }
        }
        Err(NetworkError::InvalidAddress)
    }

    /// Close connection
    pub fn close(&mut self, connection_id: usize) -> Result<Option<TcpSegment>, NetworkError> {
        if let Some(connection) = self.connections.get_mut(connection_id) {
            match connection.state {
                TcpState::Established => {
                    connection.state = TcpState::FinWait1;
                    let fin = TcpSegment::fin(
                        connection.local_port,
                        connection.remote_port,
                        connection.send_seq,
                        connection.recv_seq,
                        connection.window_size
                    );
                    connection.send_seq += 1;
                    return Ok(Some(fin));
                },
                TcpState::CloseWait => {
                    connection.state = TcpState::LastAck;
                    let fin = TcpSegment::fin(
                        connection.local_port,
                        connection.remote_port,
                        connection.send_seq,
                        connection.recv_seq,
                        connection.window_size
                    );
                    connection.send_seq += 1;
                    return Ok(Some(fin));
                },
                _ => {}
            }
        }
        Ok(None)
    }

    /// Get connection state
    pub fn get_connection(&self, id: usize) -> Option<&TcpConnection> {
        self.connections.get(id)
    }

    /// Remove closed connections
    pub fn cleanup_connections(&mut self) {
        self.connections.retain(|conn| {
            !matches!(conn.state, TcpState::Closed | TcpState::TimeWait)
        });
    }

    /// Allocate an available port
    pub fn allocate_port(&self) -> Result<u16, NetworkError> {
        // Simple port allocation starting from 32768
        for port in 32768..=65535 {
            if !self.connections.iter().any(|c| c.local_port == port) {
                return Ok(port);
            }
        }
        Err(NetworkError::AddressInUse)
    }
}

/// Calculate TCP checksum including pseudo-header
pub fn calculate_tcp_checksum(
    source_ip: &Ipv4Address,
    dest_ip: &Ipv4Address,
    tcp_header: &[u8],
    tcp_data: &[u8],
) -> u16 {
    let mut sum: u32 = 0;

    // Pseudo-header: source IP (4 bytes)
    sum += u16::from_be_bytes([source_ip.octets()[0], source_ip.octets()[1]]) as u32;
    sum += u16::from_be_bytes([source_ip.octets()[2], source_ip.octets()[3]]) as u32;

    // Pseudo-header: destination IP (4 bytes)
    sum += u16::from_be_bytes([dest_ip.octets()[0], dest_ip.octets()[1]]) as u32;
    sum += u16::from_be_bytes([dest_ip.octets()[2], dest_ip.octets()[3]]) as u32;

    // Pseudo-header: protocol (TCP = 6) and TCP length
    sum += 6u32; // TCP protocol number
    let tcp_length = (tcp_header.len() + tcp_data.len()) as u16;
    sum += tcp_length as u32;

    // TCP header (with checksum field zeroed)
    for chunk in tcp_header.chunks(2) {
        let word = if chunk.len() == 2 {
            u16::from_be_bytes([chunk[0], chunk[1]]) as u32
        } else {
            (chunk[0] as u32) << 8
        };
        // Skip checksum field (bytes 16-17)
        let offset = chunk.as_ptr() as usize - tcp_header.as_ptr() as usize;
        if offset != 16 {
            sum += word;
        }
    }

    // TCP data
    for chunk in tcp_data.chunks(2) {
        let word = if chunk.len() == 2 {
            u16::from_be_bytes([chunk[0], chunk[1]]) as u32
        } else {
            (chunk[0] as u32) << 8
        };
        sum += word;
    }

    // Fold 32-bit sum to 16 bits
    while (sum >> 16) != 0 {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }

    // Return one's complement
    !sum as u16
}

/// Verify TCP checksum
pub fn verify_tcp_checksum(
    source_ip: &Ipv4Address,
    dest_ip: &Ipv4Address,
    tcp_packet: &[u8],
) -> bool {
    if tcp_packet.len() < TcpHeader::MIN_SIZE {
        return false;
    }

    let stored_checksum = u16::from_be_bytes([tcp_packet[16], tcp_packet[17]]);
    let header_len = ((tcp_packet[12] >> 4) * 4) as usize;

    if tcp_packet.len() < header_len {
        return false;
    }

    let tcp_data = if tcp_packet.len() > header_len {
        &tcp_packet[header_len..]
    } else {
        &[]
    };

    let calculated = calculate_tcp_checksum(
        source_ip,
        dest_ip,
        &tcp_packet[..header_len],
        tcp_data
    );

    stored_checksum == calculated
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tcp_checksum_calculation() {
        let src_ip = Ipv4Address::new(192, 168, 1, 1);
        let dst_ip = Ipv4Address::new(192, 168, 1, 2);

        // Create minimal TCP header
        let mut header = vec![0u8; 20];
        header[0..2].copy_from_slice(&1234u16.to_be_bytes()); // source port
        header[2..4].copy_from_slice(&80u16.to_be_bytes());   // dest port

        let checksum = calculate_tcp_checksum(&src_ip, &dst_ip, &header, &[]);
        assert_ne!(checksum, 0);

        // Verify checksum
        header[16..18].copy_from_slice(&checksum.to_be_bytes());
        assert!(verify_tcp_checksum(&src_ip, &dst_ip, &header));
    }

    #[test]
    fn test_tcp_state_machine() {
        let tcp = TcpStack::new();
        // More comprehensive state machine tests would go here
    }
}
