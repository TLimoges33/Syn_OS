//! # TCP (Transmission Control Protocol) Implementation
//!
//! Basic TCP protocol implementation for SynOS network stack

use super::{Ipv4Address, NetworkError};
use alloc::vec::Vec;

/// TCP header structure (simplified)
#[derive(Debug, Clone)]
pub struct TcpHeader {
    pub source_port: u16,
    pub destination_port: u16,
    pub sequence_number: u32,
    pub acknowledgment_number: u32,
    pub flags: u8,
    pub window_size: u16,
    pub checksum: u16,
    pub urgent_pointer: u16,
}

impl TcpHeader {
    /// Minimum TCP header size (20 bytes)
    pub const MIN_SIZE: usize = 20;

    /// TCP flag constants
    pub const FLAG_FIN: u8 = 0x01;
    pub const FLAG_SYN: u8 = 0x02;
    pub const FLAG_RST: u8 = 0x04;
    pub const FLAG_PSH: u8 = 0x08;
    pub const FLAG_ACK: u8 = 0x10;
    pub const FLAG_URG: u8 = 0x20;

    /// Create a new TCP header
    pub fn new(source_port: u16, dest_port: u16) -> Self {
        Self {
            source_port,
            destination_port: dest_port,
            sequence_number: 0,
            acknowledgment_number: 0,
            flags: 0,
            window_size: 8192,
            checksum: 0,
            urgent_pointer: 0,
        }
    }
}

/// TCP connection state
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
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
#[derive(Debug)]
pub struct TcpConnection {
    pub local_addr: Ipv4Address,
    pub local_port: u16,
    pub remote_addr: Ipv4Address,
    pub remote_port: u16,
    pub state: TcpState,
    pub send_sequence: u32,
    pub recv_sequence: u32,
    pub send_window: u16,
    pub recv_window: u16,
}

impl TcpConnection {
    /// Create a new TCP connection
    pub fn new(
        local_addr: Ipv4Address,
        local_port: u16,
        remote_addr: Ipv4Address,
        remote_port: u16,
    ) -> Self {
        Self {
            local_addr,
            local_port,
            remote_addr,
            remote_port,
            state: TcpState::Closed,
            send_sequence: 0,
            recv_sequence: 0,
            send_window: 8192,
            recv_window: 8192,
        }
    }
}

/// TCP layer implementation (basic stub)
#[derive(Debug)]
pub struct TcpLayer {
    pub connections: Vec<TcpConnection>,
}

impl TcpLayer {
    /// Create a new TCP layer
    pub fn new() -> Self {
        Self {
            connections: Vec::new(),
        }
    }

    /// Process incoming TCP packet
    pub fn process_packet(
        &mut self,
        source: Ipv4Address,
        dest: Ipv4Address,
        data: &[u8],
    ) -> Result<(), NetworkError> {
        if data.len() < TcpHeader::MIN_SIZE {
            return Err(NetworkError::InvalidPacket);
        }

        // Parse TCP header
        let header = self.parse_header(data)?;

        // Find matching connection
        let conn_idx =
            self.find_connection(dest, header.destination_port, source, header.source_port);

        if let Some(idx) = conn_idx {
            // Process packet for existing connection
            self.process_connection_packet(idx, &header, &data[TcpHeader::MIN_SIZE..])?;
        } else {
            // Check for SYN to listening socket
            if header.flags & TcpHeader::FLAG_SYN != 0 {
                self.handle_incoming_syn(
                    dest,
                    header.destination_port,
                    source,
                    header.source_port,
                    &header,
                )?;
            }
            // Else: No matching connection, send RST
        }

        Ok(())
    }

    /// Parse TCP header from bytes
    fn parse_header(&self, data: &[u8]) -> Result<TcpHeader, NetworkError> {
        if data.len() < TcpHeader::MIN_SIZE {
            return Err(NetworkError::InvalidPacket);
        }

        Ok(TcpHeader {
            source_port: u16::from_be_bytes([data[0], data[1]]),
            destination_port: u16::from_be_bytes([data[2], data[3]]),
            sequence_number: u32::from_be_bytes([data[4], data[5], data[6], data[7]]),
            acknowledgment_number: u32::from_be_bytes([data[8], data[9], data[10], data[11]]),
            flags: data[13],
            window_size: u16::from_be_bytes([data[14], data[15]]),
            checksum: u16::from_be_bytes([data[16], data[17]]),
            urgent_pointer: u16::from_be_bytes([data[18], data[19]]),
        })
    }

    /// Find connection matching the packet
    fn find_connection(
        &self,
        local_addr: Ipv4Address,
        local_port: u16,
        remote_addr: Ipv4Address,
        remote_port: u16,
    ) -> Option<usize> {
        self.connections.iter().position(|c| {
            c.local_addr == local_addr
                && c.local_port == local_port
                && (c.state == TcpState::Listen
                    || (c.remote_addr == remote_addr && c.remote_port == remote_port))
        })
    }

    /// Process packet for an existing connection (TCP state machine)
    fn process_connection_packet(
        &mut self,
        idx: usize,
        header: &TcpHeader,
        payload: &[u8],
    ) -> Result<(), NetworkError> {
        let connection = &mut self.connections[idx];

        match connection.state {
            TcpState::Listen => {
                if header.flags & TcpHeader::FLAG_SYN != 0 {
                    // SYN received: LISTEN -> SYN_RECEIVED
                    connection.recv_sequence = header.sequence_number.wrapping_add(1);
                    connection.state = TcpState::SynReceived;
                    // Should send SYN-ACK here
                }
            }
            TcpState::SynSent => {
                if header.flags & (TcpHeader::FLAG_SYN | TcpHeader::FLAG_ACK)
                    == (TcpHeader::FLAG_SYN | TcpHeader::FLAG_ACK)
                {
                    // SYN-ACK received: SYN_SENT -> ESTABLISHED
                    connection.recv_sequence = header.sequence_number.wrapping_add(1);
                    connection.state = TcpState::Established;
                    // Should send ACK here
                } else if header.flags & TcpHeader::FLAG_SYN != 0 {
                    // Simultaneous open: SYN_SENT -> SYN_RECEIVED
                    connection.recv_sequence = header.sequence_number.wrapping_add(1);
                    connection.state = TcpState::SynReceived;
                }
            }
            TcpState::SynReceived => {
                if header.flags & TcpHeader::FLAG_ACK != 0 {
                    // ACK received: SYN_RECEIVED -> ESTABLISHED
                    connection.state = TcpState::Established;
                }
            }
            TcpState::Established => {
                if header.flags & TcpHeader::FLAG_FIN != 0 {
                    // FIN received: ESTABLISHED -> CLOSE_WAIT
                    connection.recv_sequence = header.sequence_number.wrapping_add(1);
                    connection.state = TcpState::CloseWait;
                    // Should send ACK here
                } else if header.flags & TcpHeader::FLAG_ACK != 0 && payload.len() > 0 {
                    // Data packet: update sequence number
                    connection.recv_sequence =
                        connection.recv_sequence.wrapping_add(payload.len() as u32);
                    // Should deliver data to application
                }
            }
            TcpState::FinWait1 => {
                if header.flags & TcpHeader::FLAG_FIN != 0
                    && header.flags & TcpHeader::FLAG_ACK != 0
                {
                    // FIN-ACK received: FIN_WAIT_1 -> TIME_WAIT
                    connection.state = TcpState::TimeWait;
                } else if header.flags & TcpHeader::FLAG_ACK != 0 {
                    // ACK received: FIN_WAIT_1 -> FIN_WAIT_2
                    connection.state = TcpState::FinWait2;
                } else if header.flags & TcpHeader::FLAG_FIN != 0 {
                    // FIN received: FIN_WAIT_1 -> CLOSING
                    connection.state = TcpState::Closing;
                }
            }
            TcpState::FinWait2 => {
                if header.flags & TcpHeader::FLAG_FIN != 0 {
                    // FIN received: FIN_WAIT_2 -> TIME_WAIT
                    connection.state = TcpState::TimeWait;
                }
            }
            TcpState::CloseWait => {
                // Waiting for application to close
            }
            TcpState::Closing => {
                if header.flags & TcpHeader::FLAG_ACK != 0 {
                    // ACK received: CLOSING -> TIME_WAIT
                    connection.state = TcpState::TimeWait;
                }
            }
            TcpState::LastAck => {
                if header.flags & TcpHeader::FLAG_ACK != 0 {
                    // ACK received: LAST_ACK -> CLOSED
                    connection.state = TcpState::Closed;
                }
            }
            TcpState::TimeWait => {
                // Wait for 2*MSL, then close
                // In real implementation, use timer
            }
            TcpState::Closed => {
                // Should not receive packets in closed state
            }
        }

        Ok(())
    }

    /// Handle incoming SYN packet to listening socket
    fn handle_incoming_syn(
        &mut self,
        local_addr: Ipv4Address,
        local_port: u16,
        remote_addr: Ipv4Address,
        remote_port: u16,
        header: &TcpHeader,
    ) -> Result<(), NetworkError> {
        // Create new connection for incoming SYN
        let mut connection = TcpConnection::new(local_addr, local_port, remote_addr, remote_port);
        connection.recv_sequence = header.sequence_number.wrapping_add(1);
        connection.state = TcpState::SynReceived;
        self.connections.push(connection);
        // Should send SYN-ACK here
        Ok(())
    }

    /// Create a new connection
    pub fn connect(
        &mut self,
        local_addr: Ipv4Address,
        remote_addr: Ipv4Address,
        remote_port: u16,
    ) -> Result<usize, NetworkError> {
        let local_port = self.allocate_port()?;
        let connection = TcpConnection::new(local_addr, local_port, remote_addr, remote_port);
        self.connections.push(connection);
        Ok(self.connections.len() - 1)
    }

    /// Listen on a port
    pub fn listen(&mut self, local_addr: Ipv4Address, port: u16) -> Result<usize, NetworkError> {
        let mut connection = TcpConnection::new(local_addr, port, Ipv4Address::new(0, 0, 0, 0), 0);
        connection.state = TcpState::Listen;
        self.connections.push(connection);
        Ok(self.connections.len() - 1)
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

    /// Send a TCP packet with specified flags
    pub fn send_packet(
        &mut self,
        conn_idx: usize,
        flags: u8,
        payload: &[u8],
    ) -> Result<Vec<u8>, NetworkError> {
        if conn_idx >= self.connections.len() {
            return Err(NetworkError::InvalidAddress);
        }

        let conn = &mut self.connections[conn_idx];

        // Create TCP header
        let mut header = TcpHeader::new(conn.local_port, conn.remote_port);
        header.sequence_number = conn.send_sequence;
        header.acknowledgment_number = conn.recv_sequence;
        header.flags = flags;
        header.window_size = conn.send_window;

        // Serialize header
        let mut packet = Vec::with_capacity(TcpHeader::MIN_SIZE + payload.len());
        packet.extend_from_slice(&conn.local_port.to_be_bytes());
        packet.extend_from_slice(&conn.remote_port.to_be_bytes());
        packet.extend_from_slice(&header.sequence_number.to_be_bytes());
        packet.extend_from_slice(&header.acknowledgment_number.to_be_bytes());

        // Data offset (5 = 20 bytes, no options) and flags
        packet.push((5 << 4) | 0);  // Data offset in upper 4 bits
        packet.push(flags);
        packet.extend_from_slice(&header.window_size.to_be_bytes());
        packet.extend_from_slice(&[0, 0]); // Checksum placeholder
        packet.extend_from_slice(&header.urgent_pointer.to_be_bytes());

        // Add payload
        packet.extend_from_slice(payload);

        // Update sequence number
        if payload.len() > 0 {
            conn.send_sequence = conn.send_sequence.wrapping_add(payload.len() as u32);
        }
        if flags & TcpHeader::FLAG_SYN != 0 || flags & TcpHeader::FLAG_FIN != 0 {
            conn.send_sequence = conn.send_sequence.wrapping_add(1);
        }

        Ok(packet)
    }

    /// Send SYN packet to initiate connection
    pub fn send_syn(&mut self, conn_idx: usize) -> Result<Vec<u8>, NetworkError> {
        self.send_packet(conn_idx, TcpHeader::FLAG_SYN, &[])
    }

    /// Send SYN-ACK packet for listening socket
    pub fn send_syn_ack(&mut self, conn_idx: usize) -> Result<Vec<u8>, NetworkError> {
        self.send_packet(conn_idx, TcpHeader::FLAG_SYN | TcpHeader::FLAG_ACK, &[])
    }

    /// Send ACK packet
    pub fn send_ack(&mut self, conn_idx: usize) -> Result<Vec<u8>, NetworkError> {
        self.send_packet(conn_idx, TcpHeader::FLAG_ACK, &[])
    }

    /// Send FIN packet to close connection
    pub fn send_fin(&mut self, conn_idx: usize) -> Result<Vec<u8>, NetworkError> {
        self.send_packet(conn_idx, TcpHeader::FLAG_FIN | TcpHeader::FLAG_ACK, &[])
    }

    /// Send data packet
    pub fn send_data(&mut self, conn_idx: usize, data: &[u8]) -> Result<Vec<u8>, NetworkError> {
        if data.is_empty() {
            return Err(NetworkError::InvalidPacket);
        }
        self.send_packet(conn_idx, TcpHeader::FLAG_ACK | TcpHeader::FLAG_PSH, data)
    }

    /// Calculate TCP checksum
    pub fn calculate_checksum(
        &self,
        source_addr: Ipv4Address,
        dest_addr: Ipv4Address,
        tcp_packet: &[u8],
    ) -> u16 {
        let mut sum: u32 = 0;

        // Pseudo-header
        for &byte in source_addr.bytes() {
            sum += byte as u32;
        }
        for &byte in dest_addr.bytes() {
            sum += byte as u32;
        }
        sum += 6; // TCP protocol number
        sum += tcp_packet.len() as u32;

        // TCP packet
        for i in (0..tcp_packet.len()).step_by(2) {
            let word = if i + 1 < tcp_packet.len() {
                ((tcp_packet[i] as u16) << 8) | (tcp_packet[i + 1] as u16)
            } else {
                (tcp_packet[i] as u16) << 8
            };
            sum += word as u32;
        }

        // Fold 32-bit sum to 16 bits
        while sum >> 16 != 0 {
            sum = (sum & 0xFFFF) + (sum >> 16);
        }

        !sum as u16
    }
}
