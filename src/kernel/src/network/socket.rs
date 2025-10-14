//! # Socket Interface Implementation
//!
//! POSIX-compatible socket API for SynOS network stack

use super::{NetworkError, Ipv4Address, tcp, udp};
use super::tcp::TcpLayer;
use super::udp::UdpLayer;
use alloc::vec::Vec;
use alloc::collections::BTreeMap;

/// Socket domain/family
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum SocketDomain {
    Inet,    // IPv4
    Inet6,   // IPv6 (future)
    Unix,    // Unix domain sockets (future)
}

/// Socket type
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum SocketType {
    Stream,  // TCP
    Dgram,   // UDP
    Raw,     // Raw sockets (future)
}

/// Socket protocol
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum SocketProtocol {
    Tcp,
    Udp,
    Icmp,    // Future
    Raw(u8), // Future
}

/// Socket address structure
#[derive(Debug, Clone, PartialEq)]
pub struct SocketAddr {
    pub ip: Ipv4Address,
    pub port: u16,
}

impl SocketAddr {
    /// Create a new socket address
    pub fn new(ip: Ipv4Address, port: u16) -> Self {
        Self { ip, port }
    }

    /// Create address for any IP (0.0.0.0)
    pub fn any(port: u16) -> Self {
        Self {
            ip: Ipv4Address::new(0, 0, 0, 0),
            port,
        }
    }

    /// Create localhost address
    pub fn localhost(port: u16) -> Self {
        Self {
            ip: Ipv4Address::new(127, 0, 0, 1),
            port,
        }
    }
}

/// Socket state
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum SocketState {
    Closed,
    Bound,
    Listening,
    Connecting,
    Connected,
    Disconnecting,
}

/// Socket structure
#[derive(Debug)]
pub struct Socket {
    pub id: SocketId,
    pub domain: SocketDomain,
    pub socket_type: SocketType,
    pub protocol: SocketProtocol,
    pub state: SocketState,
    pub local_addr: Option<SocketAddr>,
    pub remote_addr: Option<SocketAddr>,
    pub protocol_handle: Option<usize>, // Handle to TCP/UDP layer
    /// Receive buffer for incoming data
    pub recv_buffer: Vec<u8>,
    /// Send buffer for outgoing data
    pub send_buffer: Vec<u8>,
}

impl Socket {
    /// Create a new socket
    pub fn new(id: SocketId, domain: SocketDomain, socket_type: SocketType, protocol: SocketProtocol) -> Self {
        Self {
            id,
            domain,
            socket_type,
            protocol,
            state: SocketState::Closed,
            local_addr: None,
            remote_addr: None,
            protocol_handle: None,
            recv_buffer: Vec::with_capacity(65536), // 64KB receive buffer
            send_buffer: Vec::with_capacity(65536), // 64KB send buffer
        }
    }

    /// Check if socket is bound
    pub fn is_bound(&self) -> bool {
        self.local_addr.is_some()
    }

    /// Check if socket is connected
    pub fn is_connected(&self) -> bool {
        matches!(self.state, SocketState::Connected)
    }

    /// Check if socket is listening
    pub fn is_listening(&self) -> bool {
        matches!(self.state, SocketState::Listening)
    }
}

/// Socket ID type
pub type SocketId = usize;

/// Socket layer managing all sockets
#[derive(Debug)]
pub struct SocketLayer {
    sockets: BTreeMap<SocketId, Socket>,
    next_id: SocketId,
    tcp_layer: TcpLayer,
    udp_layer: UdpLayer,
}

impl SocketLayer {
    /// Create a new socket layer
    pub fn new() -> Self {
        Self {
            sockets: BTreeMap::new(),
            next_id: 1,
            tcp_layer: TcpLayer::new(),
            udp_layer: UdpLayer::new(),
        }
    }

    /// Create a new socket
    pub fn socket(&mut self, domain: SocketDomain, socket_type: SocketType, protocol: SocketProtocol) -> Result<SocketId, NetworkError> {
        // Validate combination
        match (domain, socket_type, protocol) {
            (SocketDomain::Inet, SocketType::Stream, SocketProtocol::Tcp) => {},
            (SocketDomain::Inet, SocketType::Dgram, SocketProtocol::Udp) => {},
            _ => return Err(NetworkError::InvalidAddress),
        }

        let id = self.next_id;
        self.next_id += 1;

        let socket = Socket::new(id, domain, socket_type, protocol);
        self.sockets.insert(id, socket);

        Ok(id)
    }

    /// Bind socket to address
    pub fn bind(&mut self, socket_id: SocketId, addr: SocketAddr) -> Result<(), NetworkError> {
        // First check socket state
        if let Some(socket) = self.sockets.get(&socket_id) {
            if socket.state != SocketState::Closed {
                return Err(NetworkError::InvalidAddress);
            }
        } else {
            return Err(NetworkError::InvalidAddress);
        }

        // Check if address is already in use
        for (_, other_socket) in &self.sockets {
            if let Some(other_addr) = &other_socket.local_addr {
                if other_addr.port == addr.port &&
                   (other_addr.ip == addr.ip ||
                    addr.ip == Ipv4Address::new(0, 0, 0, 0) ||
                    other_addr.ip == Ipv4Address::new(0, 0, 0, 0)) {
                    return Err(NetworkError::AddressInUse);
                }
            }
        }

        // Now bind the socket
        if let Some(socket) = self.sockets.get_mut(&socket_id) {
            socket.local_addr = Some(addr);
            socket.state = SocketState::Bound;
            Ok(())
        } else {
            Err(NetworkError::InvalidAddress)
        }
    }

    /// Listen for connections (TCP only)
    pub fn listen(&mut self, socket_id: SocketId, backlog: usize) -> Result<(), NetworkError> {
        if let Some(socket) = self.sockets.get_mut(&socket_id) {
            if socket.protocol != SocketProtocol::Tcp {
                return Err(NetworkError::InvalidAddress);
            }

            if socket.state != SocketState::Bound {
                return Err(NetworkError::InvalidAddress);
            }

            if let Some(addr) = &socket.local_addr {
                let handle = self.tcp_layer.listen(addr.ip, addr.port)?;
                socket.protocol_handle = Some(handle);
                socket.state = SocketState::Listening;
                Ok(())
            } else {
                Err(NetworkError::InvalidAddress)
            }
        } else {
            Err(NetworkError::InvalidAddress)
        }
    }

    /// Connect to remote address
    pub fn connect(&mut self, socket_id: SocketId, addr: SocketAddr) -> Result<(), NetworkError> {
        if let Some(socket) = self.sockets.get_mut(&socket_id) {
            if socket.state != SocketState::Bound && socket.state != SocketState::Closed {
                return Err(NetworkError::InvalidAddress);
            }

            // Auto-bind if not bound
            if socket.local_addr.is_none() {
                let local_port = match socket.protocol {
                    SocketProtocol::Tcp => self.tcp_layer.allocate_port()?,
                    SocketProtocol::Udp => self.udp_layer.allocate_port()?,
                    _ => return Err(NetworkError::InvalidAddress),
                };
                socket.local_addr = Some(SocketAddr::any(local_port));
                socket.state = SocketState::Bound;
            }

            let local_addr = socket.local_addr.as_ref().unwrap();

            match socket.protocol {
                SocketProtocol::Tcp => {
                    let handle = self.tcp_layer.connect(local_addr.ip, addr.ip, addr.port)?;
                    socket.protocol_handle = Some(handle);

                    // Send SYN packet to initiate 3-way handshake
                    let _syn_packet = self.tcp_layer.send_syn(handle)?;
                    // Packet transmission handled by network layer
                    // (device layer integration would go here in future)

                    socket.state = SocketState::Connecting;
                    // Will transition to Connected when SYN-ACK is received
                },
                SocketProtocol::Udp => {
                    let handle = self.udp_layer.bind(local_addr.ip, local_addr.port)?;
                    if let Some(binding) = self.udp_layer.get_binding_mut(handle) {
                        binding.connect(addr.ip, addr.port);
                    }
                    socket.protocol_handle = Some(handle);
                    socket.state = SocketState::Connected;
                },
                _ => return Err(NetworkError::InvalidAddress),
            }

            socket.remote_addr = Some(addr);
            Ok(())
        } else {
            Err(NetworkError::InvalidAddress)
        }
    }

    /// Accept incoming connection (TCP only)
    pub fn accept(&mut self, socket_id: SocketId) -> Result<(SocketId, SocketAddr), NetworkError> {
        if let Some(socket) = self.sockets.get(&socket_id) {
            if socket.protocol != SocketProtocol::Tcp || socket.state != SocketState::Listening {
                return Err(NetworkError::InvalidAddress);
            }

            // Create new socket for connection
            let new_id = self.next_id;
            self.next_id += 1;

            let mut new_socket = Socket::new(new_id, socket.domain, socket.socket_type, socket.protocol);
            new_socket.local_addr = socket.local_addr.clone();

            // Accept connection from TCP layer
            // Find first SYN_RECEIVED connection on this listening port
            if let Some(local_addr) = &socket.local_addr {
                let conn_idx = self.tcp_layer.connections.iter()
                    .position(|c| c.state == tcp::TcpState::SynReceived && c.local_port == local_addr.port);

                if let Some(idx) = conn_idx {
                    let conn = &self.tcp_layer.connections[idx];
                    let remote_addr = SocketAddr::new(conn.remote_addr, conn.remote_port);

                    // Send SYN-ACK packet
                    let _syn_ack_packet = self.tcp_layer.send_syn_ack(idx)?;
                    // Packet transmission handled by network layer
                    // (device layer integration would go here in future)

                    // Update connection state (will move to Established on receiving ACK)
                    new_socket.remote_addr = Some(remote_addr.clone());
                    new_socket.protocol_handle = Some(idx);
                    new_socket.state = SocketState::Connected;

                    self.sockets.insert(new_id, new_socket);
                    return Ok((new_id, remote_addr));
                }
            }

            // No pending connection found
            Err(NetworkError::WouldBlock)
        } else {
            Err(NetworkError::InvalidAddress)
        }
    }

    /// Send data on socket
    pub fn send(&mut self, socket_id: SocketId, data: Vec<u8>) -> Result<usize, NetworkError> {
        if let Some(socket) = self.sockets.get_mut(&socket_id) {
            if socket.state != SocketState::Connected {
                return Err(NetworkError::InvalidAddress);
            }

            // Add data to send buffer
            socket.send_buffer.extend_from_slice(&data);
            let bytes_to_send = data.len();

            if let Some(handle) = socket.protocol_handle {
                match socket.protocol {
                    SocketProtocol::Tcp => {
                        // TCP: Actually send data through TCP layer
                        let _tcp_packet = self.tcp_layer.send_data(handle, &data)?;
                        // In a real implementation, would pass packet to network device
                        socket.send_buffer.clear();
                        Ok(bytes_to_send)
                    },
                    SocketProtocol::Udp => {
                        if let Some(remote_addr) = &socket.remote_addr {
                            let _datagram = self.udp_layer.send(handle, remote_addr.ip, remote_addr.port, data.clone())?;
                            socket.send_buffer.clear();
                            Ok(bytes_to_send)
                        } else {
                            Err(NetworkError::InvalidAddress)
                        }
                    },
                    _ => Err(NetworkError::InvalidAddress),
                }
            } else {
                Err(NetworkError::InvalidAddress)
            }
        } else {
            Err(NetworkError::InvalidAddress)
        }
    }

    /// Receive data from socket
    pub fn recv(&mut self, socket_id: SocketId, buffer: &mut [u8]) -> Result<usize, NetworkError> {
        if let Some(socket) = self.sockets.get_mut(&socket_id) {
            if socket.recv_buffer.is_empty() {
                // No data available
                return Ok(0);
            }

            // Copy data from recv buffer to user buffer
            let bytes_to_copy = core::cmp::min(buffer.len(), socket.recv_buffer.len());
            buffer[..bytes_to_copy].copy_from_slice(&socket.recv_buffer[..bytes_to_copy]);

            // Remove copied data from recv buffer
            socket.recv_buffer.drain(..bytes_to_copy);

            Ok(bytes_to_copy)
        } else {
            Err(NetworkError::InvalidAddress)
        }
    }

    /// Send data to specific address (UDP only)
    pub fn sendto(&mut self, socket_id: SocketId, data: Vec<u8>, addr: SocketAddr) -> Result<usize, NetworkError> {
        if let Some(socket) = self.sockets.get(&socket_id) {
            if socket.protocol != SocketProtocol::Udp {
                return Err(NetworkError::InvalidAddress);
            }

            if let Some(handle) = socket.protocol_handle {
                let _datagram = self.udp_layer.send(handle, addr.ip, addr.port, data.clone())?;
                // Packet transmission handled by network layer
                // (device layer integration would go here in future)
                Ok(data.len())
            } else {
                Err(NetworkError::InvalidAddress)
            }
        } else {
            Err(NetworkError::InvalidAddress)
        }
    }

    /// Receive data with sender address (UDP only)
    pub fn recvfrom(&mut self, socket_id: SocketId, buffer: &mut [u8]) -> Result<(usize, SocketAddr), NetworkError> {
        if let Some(socket) = self.sockets.get_mut(&socket_id) {
            if socket.recv_buffer.is_empty() {
                // No data available - return placeholder for now
                let addr = SocketAddr::new(Ipv4Address::new(0, 0, 0, 0), 0);
                return Ok((0, addr));
            }

            // In a real implementation, would need to store source address with data
            // For now, use remote_addr if available
            let source_addr = socket.remote_addr.clone()
                .unwrap_or(SocketAddr::new(Ipv4Address::new(0, 0, 0, 0), 0));

            // Copy data from recv buffer
            let bytes_to_copy = core::cmp::min(buffer.len(), socket.recv_buffer.len());
            buffer[..bytes_to_copy].copy_from_slice(&socket.recv_buffer[..bytes_to_copy]);
            socket.recv_buffer.drain(..bytes_to_copy);

            Ok((bytes_to_copy, source_addr))
        } else {
            Err(NetworkError::InvalidAddress)
        }
    }

    /// Close socket
    pub fn close(&mut self, socket_id: SocketId) -> Result<(), NetworkError> {
        if let Some(socket) = self.sockets.remove(&socket_id) {
            if let Some(_handle) = socket.protocol_handle {
                match socket.protocol {
                    SocketProtocol::Tcp => {
                        // Find TCP connection and initiate close
                        if let Some(remote_addr) = &socket.remote_addr {
                            if let Some(local_addr) = &socket.local_addr {
                                if let Some(conn) = self.tcp_layer.connections.iter_mut()
                                    .find(|c| c.local_port == local_addr.port &&
                                              c.remote_addr == remote_addr.ip &&
                                              c.remote_port == remote_addr.port) {
                                    // Transition to appropriate close state
                                    match conn.state {
                                        tcp::TcpState::Established => {
                                            conn.state = tcp::TcpState::FinWait1;
                                            // Should send FIN here
                                        },
                                        tcp::TcpState::CloseWait => {
                                            conn.state = tcp::TcpState::LastAck;
                                            // Should send FIN here
                                        },
                                        _ => {
                                            conn.state = tcp::TcpState::Closed;
                                        }
                                    }
                                }
                            }
                        }
                    },
                    SocketProtocol::Udp => {
                        self.udp_layer.unbind(_handle)?;
                    },
                    _ => {}
                }
            }
            Ok(())
        } else {
            Err(NetworkError::InvalidAddress)
        }
    }

    /// Get socket information
    pub fn get_socket(&self, socket_id: SocketId) -> Option<&Socket> {
        self.sockets.get(&socket_id)
    }

    /// Get TCP layer
    pub fn tcp_layer(&mut self) -> &mut TcpLayer {
        &mut self.tcp_layer
    }

    /// Get UDP layer
    pub fn udp_layer(&mut self) -> &mut UdpLayer {
        &mut self.udp_layer
    }
}
