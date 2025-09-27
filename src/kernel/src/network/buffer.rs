//! # Network Buffer Management
//!
//! Provides efficient packet buffer allocation and management for the network stack

use super::{NetworkError, NetworkPacket};
use alloc::{collections::VecDeque, vec::Vec};
use core::sync::atomic::{AtomicUsize, Ordering};
use spin::Mutex;

/// Network buffer pool configuration
const DEFAULT_BUFFER_SIZE: usize = 2048; // 2KB per buffer
const DEFAULT_BUFFER_COUNT: usize = 1024; // 1024 buffers total
const MIN_BUFFER_COUNT: usize = 64; // Minimum number of buffers
const MAX_BUFFER_COUNT: usize = 8192; // Maximum number of buffers

/// Network buffer statistics
#[derive(Debug, Default, Clone)]
pub struct BufferStats {
    pub total_buffers: usize,
    pub free_buffers: usize,
    pub allocated_buffers: usize,
    pub allocation_failures: usize,
    pub peak_usage: usize,
}

/// Network buffer pool
pub struct NetworkBufferPool {
    free_buffers: VecDeque<Vec<u8>>,
    buffer_size: usize,
    total_count: usize,
    allocated_count: AtomicUsize,
    stats: BufferStats,
}

impl NetworkBufferPool {
    /// Create a new buffer pool with specified parameters
    pub fn new(buffer_size: usize, buffer_count: usize) -> Result<Self, NetworkError> {
        let count = buffer_count.clamp(MIN_BUFFER_COUNT, MAX_BUFFER_COUNT);
        let mut free_buffers = VecDeque::with_capacity(count);

        // Pre-allocate all buffers
        for _ in 0..count {
            let buffer = vec![0u8; buffer_size];
            free_buffers.push_back(buffer);
        }

        Ok(Self {
            free_buffers,
            buffer_size,
            total_count: count,
            allocated_count: AtomicUsize::new(0),
            stats: BufferStats {
                total_buffers: count,
                free_buffers: count,
                allocated_buffers: 0,
                allocation_failures: 0,
                peak_usage: 0,
            },
        })
    }

    /// Create a default buffer pool
    pub fn default() -> Result<Self, NetworkError> {
        Self::new(DEFAULT_BUFFER_SIZE, DEFAULT_BUFFER_COUNT)
    }

    /// Allocate a buffer from the pool
    pub fn allocate(&mut self) -> Result<Vec<u8>, NetworkError> {
        if let Some(buffer) = self.free_buffers.pop_front() {
            let allocated = self.allocated_count.fetch_add(1, Ordering::SeqCst) + 1;
            self.stats.allocated_buffers = allocated;
            self.stats.free_buffers = self.free_buffers.len();

            if allocated > self.stats.peak_usage {
                self.stats.peak_usage = allocated;
            }

            Ok(buffer)
        } else {
            self.stats.allocation_failures += 1;
            Err(NetworkError::BufferFull)
        }
    }

    /// Return a buffer to the pool
    pub fn deallocate(&mut self, mut buffer: Vec<u8>) {
        // Ensure buffer is the right size and clear it
        buffer.clear();
        buffer.resize(self.buffer_size, 0);

        self.free_buffers.push_back(buffer);
        self.allocated_count.fetch_sub(1, Ordering::SeqCst);
        self.stats.allocated_buffers = self.allocated_count.load(Ordering::SeqCst);
        self.stats.free_buffers = self.free_buffers.len();
    }

    /// Get buffer pool statistics
    pub fn get_stats(&self) -> BufferStats {
        let mut stats = self.stats.clone();
        stats.allocated_buffers = self.allocated_count.load(Ordering::SeqCst);
        stats.free_buffers = self.free_buffers.len();
        stats
    }

    /// Get buffer size
    pub fn buffer_size(&self) -> usize {
        self.buffer_size
    }

    /// Get total buffer count
    pub fn total_count(&self) -> usize {
        self.total_count
    }

    /// Get available buffer count
    pub fn available_count(&self) -> usize {
        self.free_buffers.len()
    }

    /// Check if pool has available buffers
    pub fn has_available(&self) -> bool {
        !self.free_buffers.is_empty()
    }

    /// Get pool utilization as a percentage
    pub fn utilization(&self) -> f32 {
        let allocated = self.allocated_count.load(Ordering::SeqCst);
        (allocated as f32 / self.total_count as f32) * 100.0
    }
}

/// Packet buffer manager for different packet sizes
pub struct PacketBufferManager {
    small_pool: NetworkBufferPool,  // 512B buffers for small packets
    medium_pool: NetworkBufferPool, // 1500B buffers for standard Ethernet
    large_pool: NetworkBufferPool,  // 9000B buffers for jumbo frames
}

impl PacketBufferManager {
    /// Create a new packet buffer manager
    pub fn new() -> Result<Self, NetworkError> {
        Ok(Self {
            small_pool: NetworkBufferPool::new(512, 512)?,
            medium_pool: NetworkBufferPool::new(1500, 1024)?,
            large_pool: NetworkBufferPool::new(9000, 256)?,
        })
    }

    /// Allocate a packet buffer of appropriate size
    pub fn allocate_packet(&mut self, size: usize) -> Result<NetworkPacket, NetworkError> {
        let buffer = if size <= 512 {
            self.small_pool.allocate()?
        } else if size <= 1500 {
            self.medium_pool.allocate()?
        } else if size <= 9000 {
            self.large_pool.allocate()?
        } else {
            return Err(NetworkError::InvalidPacket);
        };

        Ok(NetworkPacket::new(buffer))
    }

    /// Allocate a packet buffer with specific capacity
    pub fn allocate_with_capacity(
        &mut self,
        capacity: usize,
    ) -> Result<NetworkPacket, NetworkError> {
        self.allocate_packet(capacity)
    }

    /// Deallocate a packet buffer back to the appropriate pool
    pub fn deallocate_packet(&mut self, packet: NetworkPacket) {
        let buffer = packet.data().to_vec();
        let capacity = buffer.capacity();

        if capacity <= 512 {
            self.small_pool.deallocate(buffer);
        } else if capacity <= 1500 {
            self.medium_pool.deallocate(buffer);
        } else if capacity <= 9000 {
            self.large_pool.deallocate(buffer);
        }
        // If buffer is larger than 9000 bytes, just let it be dropped
    }

    /// Get combined statistics from all pools
    pub fn get_stats(&self) -> (BufferStats, BufferStats, BufferStats) {
        (
            self.small_pool.get_stats(),
            self.medium_pool.get_stats(),
            self.large_pool.get_stats(),
        )
    }

    /// Get total utilization across all pools
    pub fn total_utilization(&self) -> f32 {
        let small_util = self.small_pool.utilization();
        let medium_util = self.medium_pool.utilization();
        let large_util = self.large_pool.utilization();

        (small_util + medium_util + large_util) / 3.0
    }

    /// Check if any pool has available buffers
    pub fn has_available_buffers(&self) -> bool {
        self.small_pool.has_available()
            || self.medium_pool.has_available()
            || self.large_pool.has_available()
    }
}

/// Global packet buffer manager
static PACKET_BUFFER_MANAGER: Mutex<Option<PacketBufferManager>> = Mutex::new(None);

/// Initialize the network buffer system
pub fn init_network_buffers() -> Result<(), NetworkError> {
    let mut manager = PACKET_BUFFER_MANAGER.lock();
    if manager.is_none() {
        *manager = Some(PacketBufferManager::new()?);
    }
    Ok(())
}

/// Allocate a network packet buffer
pub fn allocate_network_packet(size: usize) -> Result<NetworkPacket, NetworkError> {
    let mut manager_guard = PACKET_BUFFER_MANAGER.lock();
    if let Some(ref mut manager) = manager_guard.as_mut() {
        manager.allocate_packet(size)
    } else {
        Err(NetworkError::DeviceNotFound)
    }
}

/// Allocate a network packet buffer with specific capacity
pub fn allocate_network_packet_with_capacity(
    capacity: usize,
) -> Result<NetworkPacket, NetworkError> {
    let mut manager_guard = PACKET_BUFFER_MANAGER.lock();
    if let Some(ref mut manager) = manager_guard.as_mut() {
        manager.allocate_with_capacity(capacity)
    } else {
        Err(NetworkError::DeviceNotFound)
    }
}

/// Deallocate a network packet buffer
pub fn deallocate_network_packet(packet: NetworkPacket) {
    let mut manager_guard = PACKET_BUFFER_MANAGER.lock();
    if let Some(ref mut manager) = manager_guard.as_mut() {
        manager.deallocate_packet(packet);
    }
}

/// Get network buffer statistics
pub fn get_network_buffer_stats() -> Result<(BufferStats, BufferStats, BufferStats), NetworkError> {
    let manager_guard = PACKET_BUFFER_MANAGER.lock();
    if let Some(ref manager) = manager_guard.as_ref() {
        Ok(manager.get_stats())
    } else {
        Err(NetworkError::DeviceNotFound)
    }
}

/// Get total buffer utilization
pub fn get_total_buffer_utilization() -> Result<f32, NetworkError> {
    let manager_guard = PACKET_BUFFER_MANAGER.lock();
    if let Some(ref manager) = manager_guard.as_ref() {
        Ok(manager.total_utilization())
    } else {
        Err(NetworkError::DeviceNotFound)
    }
}
