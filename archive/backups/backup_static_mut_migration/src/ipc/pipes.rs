//! Pipe Implementation for Inter-Process Communication
//! 
//! Provides anonymous and named pipes with consciousness-aware buffering
//! and intelligent data flow optimization.

use alloc::collections::{BTreeMap, VecDeque};
use alloc::vec::Vec;
use core::sync::atomic::{AtomicUsize, Ordering};
use spin::Mutex;

use super::{IPCError, IPCId};

/// Pipe types
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PipeType {
    Anonymous,
    Named(u64), // Named pipe with key
}

/// Pipe direction for half-duplex pipes
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PipeDirection {
    Read,
    Write,
    Bidirectional,
}

/// Pipe buffer with consciousness-aware optimization
pub struct PipeBuffer {
    data: VecDeque<u8>,
    capacity: usize,
    bytes_written: AtomicUsize,
    bytes_read: AtomicUsize,
    consciousness_priority: u8,
}

impl PipeBuffer {
    pub fn new(capacity: usize) -> Self {
        Self {
            data: VecDeque::with_capacity(capacity),
            capacity,
            bytes_written: AtomicUsize::new(0),
            bytes_read: AtomicUsize::new(0),
            consciousness_priority: 5, // Default medium priority
        }
    }

    pub fn write(&mut self, data: &[u8]) -> Result<usize, IPCError> {
        let available_space = self.capacity - self.data.len();
        let bytes_to_write = data.len().min(available_space);
        
        if bytes_to_write == 0 {
            return Err(IPCError::ResourceBusy);
        }
        
        for &byte in &data[..bytes_to_write] {
            self.data.push_back(byte);
        }
        
        self.bytes_written.fetch_add(bytes_to_write, Ordering::SeqCst);
        Ok(bytes_to_write)
    }

    pub fn read(&mut self, buffer: &mut [u8]) -> Result<usize, IPCError> {
        let bytes_to_read = buffer.len().min(self.data.len());
        
        if bytes_to_read == 0 {
            return Ok(0);
        }
        
        for i in 0..bytes_to_read {
            buffer[i] = self.data.pop_front().unwrap();
        }
        
        self.bytes_read.fetch_add(bytes_to_read, Ordering::SeqCst);
        Ok(bytes_to_read)
    }

    pub fn available_data(&self) -> usize {
        self.data.len()
    }

    pub fn available_space(&self) -> usize {
        self.capacity - self.data.len()
    }

    pub fn is_empty(&self) -> bool {
        self.data.is_empty()
    }

    pub fn is_full(&self) -> bool {
        self.data.len() >= self.capacity
    }

    pub fn get_stats(&self) -> (usize, usize) {
        (
            self.bytes_written.load(Ordering::SeqCst),
            self.bytes_read.load(Ordering::SeqCst),
        )
    }
}

/// Pipe implementation with consciousness integration
pub struct Pipe {
    pipe_type: PipeType,
    direction: PipeDirection,
    read_buffer: Mutex<PipeBuffer>,
    write_buffer: Mutex<PipeBuffer>,
    
    // Process connections
    readers: Mutex<Vec<u64>>, // PIDs of reader processes
    writers: Mutex<Vec<u64>>, // PIDs of writer processes
    
    // Consciousness features
    consciousness_enabled: bool,
    auto_optimize: bool,
    
    // Statistics
    total_bytes_transferred: AtomicUsize,
    connection_count: AtomicUsize,
    consciousness_optimizations: AtomicUsize,
}

impl Pipe {
    /// Create a new anonymous pipe
    pub fn new(buffer_size: usize) -> Result<Self, IPCError> {
        if buffer_size == 0 {
            return Err(IPCError::InvalidArgument);
        }

        Ok(Self {
            pipe_type: PipeType::Anonymous,
            direction: PipeDirection::Bidirectional,
            read_buffer: Mutex::new(PipeBuffer::new(buffer_size)),
            write_buffer: Mutex::new(PipeBuffer::new(buffer_size)),
            readers: Mutex::new(Vec::new()),
            writers: Mutex::new(Vec::new()),
            consciousness_enabled: true,
            auto_optimize: true,
            total_bytes_transferred: AtomicUsize::new(0),
            connection_count: AtomicUsize::new(0),
            consciousness_optimizations: AtomicUsize::new(0),
        })
    }

    /// Create a named pipe
    pub fn new_named(buffer_size: usize, key: u64) -> Result<Self, IPCError> {
        if buffer_size == 0 {
            return Err(IPCError::InvalidArgument);
        }

        Ok(Self {
            pipe_type: PipeType::Named(key),
            direction: PipeDirection::Bidirectional,
            read_buffer: Mutex::new(PipeBuffer::new(buffer_size)),
            write_buffer: Mutex::new(PipeBuffer::new(buffer_size)),
            readers: Mutex::new(Vec::new()),
            writers: Mutex::new(Vec::new()),
            consciousness_enabled: true,
            auto_optimize: true,
            total_bytes_transferred: AtomicUsize::new(0),
            connection_count: AtomicUsize::new(0),
            consciousness_optimizations: AtomicUsize::new(0),
        })
    }

    /// Write data to the pipe
    pub fn write(&self, data: &[u8], writer_pid: u64) -> Result<usize, IPCError> {
        // Check if process is authorized to write
        if !self.can_write(writer_pid) {
            return Err(IPCError::PermissionDenied);
        }

        let mut buffer = self.write_buffer.lock();
        let bytes_written = buffer.write(data)?;
        
        self.total_bytes_transferred.fetch_add(bytes_written, Ordering::SeqCst);
        
        // Consciousness-driven optimization
        if self.consciousness_enabled && self.auto_optimize {
            self.optimize_buffer_priority(&mut buffer, writer_pid);
        }

        Ok(bytes_written)
    }

    /// Read data from the pipe
    pub fn read(&self, buffer: &mut [u8], reader_pid: u64) -> Result<usize, IPCError> {
        // Check if process is authorized to read
        if !self.can_read(reader_pid) {
            return Err(IPCError::PermissionDenied);
        }

        let mut pipe_buffer = self.read_buffer.lock();
        let bytes_read = pipe_buffer.read(buffer)?;
        
        self.total_bytes_transferred.fetch_add(bytes_read, Ordering::SeqCst);

        Ok(bytes_read)
    }

    /// Connect a reader process
    pub fn connect_reader(&self, pid: u64) -> Result<(), IPCError> {
        let mut readers = self.readers.lock();
        if !readers.contains(&pid) {
            readers.push(pid);
            self.connection_count.fetch_add(1, Ordering::SeqCst);
        }
        Ok(())
    }

    /// Connect a writer process
    pub fn connect_writer(&self, pid: u64) -> Result<(), IPCError> {
        let mut writers = self.writers.lock();
        if !writers.contains(&pid) {
            writers.push(pid);
            self.connection_count.fetch_add(1, Ordering::SeqCst);
        }
        Ok(())
    }

    /// Disconnect a reader process
    pub fn disconnect_reader(&self, pid: u64) -> Result<(), IPCError> {
        let mut readers = self.readers.lock();
        if let Some(pos) = readers.iter().position(|&x| x == pid) {
            readers.remove(pos);
        }
        Ok(())
    }

    /// Disconnect a writer process
    pub fn disconnect_writer(&self, pid: u64) -> Result<(), IPCError> {
        let mut writers = self.writers.lock();
        if let Some(pos) = writers.iter().position(|&x| x == pid) {
            writers.remove(pos);
        }
        Ok(())
    }

    /// Check if a process can read from this pipe
    fn can_read(&self, pid: u64) -> bool {
        let readers = self.readers.lock();
        readers.contains(&pid) || readers.is_empty() // Allow if no specific readers or if authorized
    }

    /// Check if a process can write to this pipe
    fn can_write(&self, pid: u64) -> bool {
        let writers = self.writers.lock();
        writers.contains(&pid) || writers.is_empty() // Allow if no specific writers or if authorized
    }

    /// Optimize buffer priority based on consciousness
    fn optimize_buffer_priority(&self, buffer: &mut PipeBuffer, pid: u64) {
        // Calculate consciousness priority based on process characteristics
        let new_priority = self.calculate_consciousness_priority(pid);
        buffer.consciousness_priority = new_priority;
        
        self.consciousness_optimizations.fetch_add(1, Ordering::SeqCst);
    }

    /// Calculate consciousness priority for a process
    fn calculate_consciousness_priority(&self, pid: u64) -> u8 {
        // Simple consciousness priority calculation
        // In a real implementation, this would integrate with the consciousness engine
        ((pid % 10) + 1) as u8
    }

    /// Get pipe statistics
    pub fn get_stats(&self) -> PipeStats {
        let read_buffer = self.read_buffer.lock();
        let write_buffer = self.write_buffer.lock();
        let readers = self.readers.lock();
        let writers = self.writers.lock();

        let (read_bytes_written, read_bytes_read) = read_buffer.get_stats();
        let (write_bytes_written, write_bytes_read) = write_buffer.get_stats();

        PipeStats {
            pipe_type: self.pipe_type,
            direction: self.direction,
            total_bytes_transferred: self.total_bytes_transferred.load(Ordering::SeqCst),
            active_readers: readers.len(),
            active_writers: writers.len(),
            read_buffer_utilization: if read_buffer.capacity > 0 {
                (read_buffer.available_data() * 100) / read_buffer.capacity
            } else { 0 },
            write_buffer_utilization: if write_buffer.capacity > 0 {
                (write_buffer.available_data() * 100) / write_buffer.capacity
            } else { 0 },
            consciousness_optimizations: self.consciousness_optimizations.load(Ordering::SeqCst),
            connection_count: self.connection_count.load(Ordering::SeqCst),
        }
    }
}

/// Pipe statistics structure
#[derive(Debug)]
pub struct PipeStats {
    pub pipe_type: PipeType,
    pub direction: PipeDirection,
    pub total_bytes_transferred: usize,
    pub active_readers: usize,
    pub active_writers: usize,
    pub read_buffer_utilization: usize, // Percentage
    pub write_buffer_utilization: usize, // Percentage
    pub consciousness_optimizations: usize,
    pub connection_count: usize,
}

/// Pipe manager for handling multiple pipes
pub struct PipeManager {
    pipes: BTreeMap<IPCId, Pipe>,
    named_pipes: BTreeMap<u64, IPCId>, // key -> pipe_id mapping
}

impl PipeManager {
    pub fn new() -> Self {
        Self {
            pipes: BTreeMap::new(),
            named_pipes: BTreeMap::new(),
        }
    }

    pub fn add_pipe(&mut self, id: IPCId, pipe: Pipe) -> Result<(), IPCError> {
        if let PipeType::Named(key) = pipe.pipe_type {
            if self.named_pipes.contains_key(&key) {
                return Err(IPCError::ResourceBusy);
            }
            self.named_pipes.insert(key, id);
        }
        
        self.pipes.insert(id, pipe);
        Ok(())
    }

    pub fn remove_pipe(&mut self, id: IPCId) -> Result<(), IPCError> {
        if let Some(pipe) = self.pipes.remove(&id) {
            if let PipeType::Named(key) = pipe.pipe_type {
                self.named_pipes.remove(&key);
            }
            Ok(())
        } else {
            Err(IPCError::ResourceNotFound)
        }
    }

    pub fn get_pipe(&self, id: IPCId) -> Option<&Pipe> {
        self.pipes.get(&id)
    }

    pub fn get_pipe_mut(&mut self, id: IPCId) -> Option<&mut Pipe> {
        self.pipes.get_mut(&id)
    }

    pub fn find_named_pipe(&self, key: u64) -> Option<IPCId> {
        self.named_pipes.get(&key).copied()
    }

    pub fn get_pipe_count(&self) -> usize {
        self.pipes.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pipe_creation() {
        let pipe = Pipe::new(1024).unwrap();
        let stats = pipe.get_stats();
        assert_eq!(stats.total_bytes_transferred, 0);
        assert_eq!(stats.active_readers, 0);
        assert_eq!(stats.active_writers, 0);
    }

    #[test]
    fn test_pipe_write_read() {
        let pipe = Pipe::new(1024).unwrap();
        let writer_pid = 1;
        let reader_pid = 2;

        // Connect processes
        pipe.connect_writer(writer_pid).unwrap();
        pipe.connect_reader(reader_pid).unwrap();

        // Write data
        let data = b"Hello, consciousness!";
        let bytes_written = pipe.write(data, writer_pid).unwrap();
        assert_eq!(bytes_written, data.len());

        // Read data
        let mut buffer = [0u8; 1024];
        let bytes_read = pipe.read(&mut buffer, reader_pid).unwrap();
        assert_eq!(bytes_read, data.len());
        assert_eq!(&buffer[..bytes_read], data);
    }

    #[test]
    fn test_pipe_manager() {
        let mut manager = PipeManager::new();
        let pipe = Pipe::new(1024).unwrap();
        
        manager.add_pipe(1, pipe).unwrap();
        assert_eq!(manager.get_pipe_count(), 1);
        
        manager.remove_pipe(1).unwrap();
        assert_eq!(manager.get_pipe_count(), 0);
    }
}
