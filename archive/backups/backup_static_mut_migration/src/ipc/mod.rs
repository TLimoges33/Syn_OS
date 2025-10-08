//! Inter-Process Communication (IPC) Framework
//! 
//! Provides consciousness-integrated IPC mechanisms including:
//! - Pipes (anonymous and named)
//! - Shared memory segments
//! - Message queues
//! - Semaphores and mutexes
//! - Consciousness-aware resource management

use alloc::collections::BTreeMap;
use alloc::string::String;
use alloc::vec::Vec;
use alloc::vec;
use core::sync::atomic::{AtomicU64, Ordering};
use spin::Mutex;

pub mod pipes;
pub mod shared_memory;
pub mod message_queue;
pub mod semaphore;
pub mod deadlock;

use pipes::{Pipe, PipeManager};
use shared_memory::{SharedMemorySegment, SharedMemoryManager};
use semaphore::{Semaphore, SemaphoreManager};
use message_queue::{MessageQueueManager, MessageQueueConfig, MessagePriority, MessageFlags};

/// Global IPC manager instance
pub static IPC_MANAGER: Mutex<Option<IPCManager>> = Mutex::new(None);

/// IPC resource identifier
pub type IPCId = u64;

/// IPC Channel for communication
#[derive(Debug, Clone)]
pub struct IPCChannel {
    pub id: IPCId,
    pub channel_type: IPCResourceType,
    pub buffer_size: usize,
    pub permissions: IPCPermissions,
}

impl IPCChannel {
    pub fn new(id: IPCId, channel_type: IPCResourceType, buffer_size: usize) -> Self {
        Self {
            id,
            channel_type,
            buffer_size,
            permissions: IPCPermissions::default(),
        }
    }

    /// Create a new IPC channel with a name
    pub fn create(name: &str) -> Result<Self, &'static str> {
        let id = name.len() as IPCId; // Simple ID generation
        Ok(Self::new(id, IPCResourceType::Pipe, 4096))
    }

    /// Send a message through the channel
    pub async fn send(&mut self, _message: IPCMessage) -> Result<(), &'static str> {
        // TODO: Implement actual message sending
        Ok(())
    }
}

/// IPC Message structure
#[derive(Debug, Clone)]
pub struct IPCMessage {
    pub sender_pid: u64,
    pub receiver_pid: u64,
    pub message_type: MessageType,
    pub data: Vec<u8>,
    pub timestamp: u64,
    pub priority: MessagePriority,
}

/// Message types for IPC communication
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MessageType {
    Data,
    Control,
    Signal,
    Notification,
    Emergency,
}

impl IPCMessage {
    pub fn new(sender_pid: u64, receiver_pid: u64, data: Vec<u8>) -> Self {
        Self {
            sender_pid,
            receiver_pid,
            message_type: MessageType::Data,
            data,
            timestamp: 0, // TODO: Get actual timestamp
            priority: MessagePriority::Normal,
        }
    }
}

/// IPC error types
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum IPCError {
    ResourceNotFound,
    PermissionDenied,
    ResourceBusy,
    InvalidArgument,
    OutOfMemory,
    DeadlockDetected,
    Timeout,
    ConsciousnessOptimizationFailed,
}

/// IPC resource types
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum IPCResourceType {
    Pipe,
    SharedMemory,
    MessageQueue,
    Semaphore,
}

/// IPC resource metadata
#[derive(Debug, Clone)]
pub struct IPCResource {
    pub id: IPCId,
    pub resource_type: IPCResourceType,
    pub owner_pid: u64,
    pub permissions: IPCPermissions,
    pub created_at: u64,
    pub last_accessed: u64,
    pub access_count: u64,
    pub consciousness_priority: u8,
}

/// IPC permissions structure
#[derive(Debug, Clone, Copy)]
pub struct IPCPermissions {
    pub read: bool,
    pub write: bool,
    pub execute: bool,
    pub delete: bool,
}

impl Default for IPCPermissions {
    fn default() -> Self {
        Self {
            read: true,
            write: true,
            execute: false,
            delete: true,
        }
    }
}

/// Consciousness-aware IPC statistics
#[derive(Debug, Default)]
pub struct IPCStats {
    pub total_resources: u64,
    pub active_pipes: u64,
    pub active_shared_memory: u64,
    pub active_message_queues: u64,
    pub active_semaphores: u64,
    pub bytes_transferred: u64,
    pub messages_sent: u64,
    pub consciousness_optimizations: u64,
    pub deadlocks_prevented: u64,
}

/// Main IPC manager with consciousness integration
pub struct IPCManager {
    pipe_manager: PipeManager,
    shared_memory_manager: SharedMemoryManager,
    semaphore_manager: SemaphoreManager,
    message_queue_manager: MessageQueueManager,
    
    resources: BTreeMap<IPCId, IPCResource>,
    next_id: AtomicU64,
    stats: IPCStats,
    
    // Consciousness integration
    consciousness_enabled: bool,
    optimization_threshold: u64,
}

impl IPCManager {
    /// Create a new IPC manager
    pub fn new() -> Self {
        Self {
            pipe_manager: PipeManager::new(),
            shared_memory_manager: SharedMemoryManager::new(),
            semaphore_manager: SemaphoreManager::new(),
            message_queue_manager: MessageQueueManager::new(),
            
            resources: BTreeMap::new(),
            next_id: AtomicU64::new(1),
            stats: IPCStats::default(),
            
            consciousness_enabled: true,
            optimization_threshold: 100,
        }
    }

    /// Generate next unique IPC ID
    fn next_id(&self) -> IPCId {
        self.next_id.fetch_add(1, Ordering::SeqCst)
    }

    /// Create a new pipe
    pub fn create_pipe(&mut self, owner_pid: u64, buffer_size: usize) -> Result<IPCId, IPCError> {
        let id = self.next_id();
        let pipe = Pipe::new(buffer_size)?;

        self.pipe_manager.add_pipe(id, pipe)?;

        let resource = IPCResource {
            id,
            resource_type: IPCResourceType::Pipe,
            owner_pid,
            permissions: IPCPermissions::default(),
            created_at: self.get_current_time(),
            last_accessed: self.get_current_time(),
            access_count: 0,
            consciousness_priority: self.calculate_consciousness_priority(owner_pid),
        };

        self.resources.insert(id, resource);
        self.stats.active_pipes += 1;
        self.stats.total_resources += 1;

        // Register with deadlock detector
        deadlock::register_ipc_resource(id);

        if self.consciousness_enabled {
            self.optimize_ipc_resources();
        }

        Ok(id)
    }

    /// Create shared memory segment
    pub fn create_shared_memory(&mut self, owner_pid: u64, size: usize, key: Option<String>) -> Result<IPCId, IPCError> {
        let id = self.next_id();
        let segment = SharedMemorySegment::new(size, key)?;
        
        self.shared_memory_manager.add_segment(id, segment)?;
        
        let resource = IPCResource {
            id,
            resource_type: IPCResourceType::SharedMemory,
            owner_pid,
            permissions: IPCPermissions::default(),
            created_at: self.get_current_time(),
            last_accessed: self.get_current_time(),
            access_count: 0,
            consciousness_priority: self.calculate_consciousness_priority(owner_pid),
        };
        
        self.resources.insert(id, resource);
        self.stats.active_shared_memory += 1;
        self.stats.total_resources += 1;
        
        Ok(id)
    }

    /// Create message queue (comprehensive implementation)
    pub fn create_message_queue(&mut self, owner_pid: u64, max_messages: usize, max_message_size: usize) -> Result<IPCId, IPCError> {
        let config = MessageQueueConfig {
            max_messages,
            max_message_size,
            enable_consciousness: self.consciousness_enabled,
            persistence: false,
            timeout_ms: 5000,
        };
        
        let id = self.message_queue_manager.create_queue(owner_pid, config)?;
        
        let resource = IPCResource {
            id,
            resource_type: IPCResourceType::MessageQueue,
            owner_pid,
            permissions: IPCPermissions::default(),
            created_at: self.get_current_time(),
            last_accessed: self.get_current_time(),
            access_count: 0,
            consciousness_priority: self.calculate_consciousness_priority(owner_pid),
        };
        
        self.resources.insert(id, resource);
        self.stats.active_message_queues += 1;
        self.stats.total_resources += 1;

        Ok(id)
    }    /// Create semaphore
    pub fn create_semaphore(&mut self, owner_pid: u64, initial_value: i32, max_value: i32) -> Result<IPCId, IPCError> {
        let id = self.next_id();
        let semaphore = Semaphore::new(initial_value, max_value)?;
        
        self.semaphore_manager.add_semaphore(id, semaphore)?;
        
        let resource = IPCResource {
            id,
            resource_type: IPCResourceType::Semaphore,
            owner_pid,
            permissions: IPCPermissions::default(),
            created_at: self.get_current_time(),
            last_accessed: self.get_current_time(),
            access_count: 0,
            consciousness_priority: self.calculate_consciousness_priority(owner_pid),
        };
        
        self.resources.insert(id, resource);
        self.stats.active_semaphores += 1;
        self.stats.total_resources += 1;
        
        Ok(id)
    }

    /// Remove IPC resource
    pub fn remove_resource(&mut self, id: IPCId, requesting_pid: u64) -> Result<(), IPCError> {
        let resource = self.resources.get(&id).ok_or(IPCError::ResourceNotFound)?;
        
        // Check permissions
        if resource.owner_pid != requesting_pid && !self.has_admin_privileges(requesting_pid) {
            return Err(IPCError::PermissionDenied);
        }
        
        match resource.resource_type {
            IPCResourceType::Pipe => {
                self.pipe_manager.remove_pipe(id)?;
                self.stats.active_pipes -= 1;
            }
            IPCResourceType::SharedMemory => {
                self.shared_memory_manager.remove_segment(id)?;
                self.stats.active_shared_memory -= 1;
            }
            IPCResourceType::MessageQueue => {
                self.message_queue_manager.remove_queue(id)?;
                self.stats.active_message_queues -= 1;
            }
            IPCResourceType::Semaphore => {
                self.semaphore_manager.remove_semaphore(id)?;
                self.stats.active_semaphores -= 1;
            }
        }
        
        self.resources.remove(&id);
        self.stats.total_resources -= 1;
        
        Ok(())
    }

    /// Get IPC statistics
    pub fn get_stats(&self) -> &IPCStats {
        &self.stats
    }

    /// Attach to shared memory segment
    pub fn attach_shared_memory(&mut self, shm_id: IPCId, _pid: u64) -> Result<u64, IPCError> {
        let resource = self.resources.get(&shm_id).ok_or(IPCError::ResourceNotFound)?;

        if resource.resource_type != IPCResourceType::SharedMemory {
            return Err(IPCError::InvalidArgument);
        }

        // Update access tracking
        self.update_resource_access(shm_id);

        // Return a mock virtual address (in real implementation, would map memory)
        Ok(0x10000000 + shm_id * 0x1000)
    }

    /// Inter-process communication: Send message
    pub fn send_message(&mut self, queue_id: IPCId, sender_pid: u64, data: Vec<u8>, priority: MessagePriority) -> Result<(), IPCError> {
        let resource = self.resources.get(&queue_id).ok_or(IPCError::ResourceNotFound)?;

        if resource.resource_type != IPCResourceType::MessageQueue {
            return Err(IPCError::InvalidArgument);
        }

        if !resource.permissions.write {
            return Err(IPCError::PermissionDenied);
        }

        // Simplified implementation - would call with proper parameters
        // self.message_queue_manager.send_message(queue_id, 0, data, sender_pid, priority, MessageFlags::default())?;
        self.update_resource_access(queue_id);
        self.stats.messages_sent += 1;
        self.stats.bytes_transferred += data.len() as u64;

        Ok(())
    }

    /// Inter-process communication: Receive message
    pub fn receive_message(&mut self, queue_id: IPCId, receiver_pid: u64, flags: MessageFlags) -> Result<(Vec<u8>, u64), IPCError> {
        let resource = self.resources.get(&queue_id).ok_or(IPCError::ResourceNotFound)?;

        if resource.resource_type != IPCResourceType::MessageQueue {
            return Err(IPCError::InvalidArgument);
        }

        if !resource.permissions.read {
            return Err(IPCError::PermissionDenied);
        }

        // Simplified implementation - would receive message properly
        let message = (vec![0u8; 0], 0u64); // Placeholder
        self.update_resource_access(queue_id);

        Ok(message)
    }

    /// Write to pipe
    pub fn write_pipe(&mut self, pipe_id: IPCId, writer_pid: u64, data: &[u8]) -> Result<usize, IPCError> {
        let resource = self.resources.get(&pipe_id).ok_or(IPCError::ResourceNotFound)?;

        if resource.resource_type != IPCResourceType::Pipe {
            return Err(IPCError::InvalidArgument);
        }

        if !resource.permissions.write {
            return Err(IPCError::PermissionDenied);
        }

        // Get the pipe and write to it
        if let Some(pipe) = self.pipe_manager.get_pipe(pipe_id) {
            let bytes_written = pipe.write(data, writer_pid)?;
            self.update_resource_access(pipe_id);
            self.stats.bytes_transferred += bytes_written as u64;
            Ok(bytes_written)
        } else {
            Err(IPCError::ResourceNotFound)
        }
    }

    /// Read from pipe
    pub fn read_pipe(&mut self, pipe_id: IPCId, reader_pid: u64, buffer_size: usize) -> Result<Vec<u8>, IPCError> {
        let resource = self.resources.get(&pipe_id).ok_or(IPCError::ResourceNotFound)?;

        if resource.resource_type != IPCResourceType::Pipe {
            return Err(IPCError::InvalidArgument);
        }

        if !resource.permissions.read {
            return Err(IPCError::PermissionDenied);
        }

        // Get the pipe and read from it
        if let Some(pipe) = self.pipe_manager.get_pipe(pipe_id) {
            let mut buffer = vec![0u8; buffer_size];
            let bytes_read = pipe.read(&mut buffer, reader_pid)?;
            buffer.truncate(bytes_read);
            self.update_resource_access(pipe_id);
            Ok(buffer)
        } else {
            Err(IPCError::ResourceNotFound)
        }
    }

    /// Acquire semaphore
    pub fn acquire_semaphore(&mut self, sem_id: IPCId, pid: u64, timeout_ms: Option<u64>) -> Result<(), IPCError> {
        let resource = self.resources.get(&sem_id).ok_or(IPCError::ResourceNotFound)?;

        if resource.resource_type != IPCResourceType::Semaphore {
            return Err(IPCError::InvalidArgument);
        }

        // For now, simplified implementation - would call semaphore_manager.acquire_semaphore
        self.update_resource_access(sem_id);

        Ok(())
    }

    /// Release semaphore
    pub fn release_semaphore(&mut self, sem_id: IPCId, pid: u64) -> Result<(), IPCError> {
        let resource = self.resources.get(&sem_id).ok_or(IPCError::ResourceNotFound)?;

        if resource.resource_type != IPCResourceType::Semaphore {
            return Err(IPCError::InvalidArgument);
        }

        // For now, simplified implementation - would call semaphore_manager.release_semaphore
        self.update_resource_access(sem_id);

        Ok(())
    }

    /// Grant access to IPC resource for another process
    pub fn grant_access(&mut self, resource_id: IPCId, owner_pid: u64, _target_pid: u64, permissions: IPCPermissions) -> Result<(), IPCError> {
        // Check admin privileges first to avoid borrowing conflicts
        let has_admin = self.has_admin_privileges(owner_pid);

        let resource = self.resources.get_mut(&resource_id).ok_or(IPCError::ResourceNotFound)?;

        if resource.owner_pid != owner_pid && !has_admin {
            return Err(IPCError::PermissionDenied);
        }

        // In a real implementation, would maintain per-process permission table
        // For now, update the global permissions
        resource.permissions = permissions;

        Ok(())
    }

    /// List IPC resources owned by a process
    pub fn list_process_resources(&self, pid: u64) -> Vec<IPCId> {
        self.resources
            .iter()
            .filter(|(_, resource)| resource.owner_pid == pid)
            .map(|(id, _)| *id)
            .collect()
    }

    /// Clean up IPC resources for terminated process
    pub fn cleanup_process_resources(&mut self, pid: u64) -> Result<(), IPCError> {
        let resources_to_remove: Vec<IPCId> = self.list_process_resources(pid);

        for id in resources_to_remove {
            self.remove_resource(id, pid)?;
        }

        Ok(())
    }

    /// Detect and prevent deadlocks
    pub fn detect_deadlock(&mut self, pid: u64, requested_resource: IPCId) -> bool {
        // Use wait-for graph based deadlock detection
        match deadlock::check_deadlock_before_acquire(pid, requested_resource) {
            Ok(_) => false,
            Err(_) => {
                self.stats.deadlocks_prevented += 1;
                true
            }
        }
    }

    /// Register resource acquisition for deadlock tracking
    fn register_acquire(&self, pid: u64, resource_id: IPCId) {
        deadlock::register_resource_acquire(pid, resource_id);
    }

    /// Register resource release for deadlock tracking
    fn register_release(&self, pid: u64, resource_id: IPCId) {
        deadlock::register_resource_release(pid, resource_id);
    }

    /// Detach from shared memory segment
    pub fn detach_shared_memory(&mut self, _address: u64) -> Result<(), IPCError> {
        // In real implementation, would unmap memory
        // For now, just return success
        Ok(())
    }



    /// Update resource access
    fn update_resource_access(&mut self, id: IPCId) {
        let current_time = self.get_current_time();
        if let Some(resource) = self.resources.get_mut(&id) {
            resource.last_accessed = current_time;
            resource.access_count += 1;
        }
    }

    /// Calculate consciousness priority for a process
    fn calculate_consciousness_priority(&self, pid: u64) -> u8 {
        // Simple consciousness priority calculation
        // In a real implementation, this would integrate with the consciousness engine
        ((pid % 10) + 1) as u8
    }

    /// Check if process has admin privileges
    fn has_admin_privileges(&self, _pid: u64) -> bool {
        // Simplified privilege check
        // In a real implementation, this would check process capabilities
        false
    }

    /// Get current time (simplified)
    fn get_current_time(&self) -> u64 {
        // In a real implementation, this would get system time
        0
    }

    /// Consciousness-aware IPC optimization
    fn optimize_ipc_resources(&mut self) {
        if self.stats.total_resources > self.optimization_threshold {
            // Implement consciousness-driven optimization
            self.stats.consciousness_optimizations += 1;
            
            // Example optimizations:
            // - Merge underutilized resources
            // - Prioritize high-consciousness processes
            // - Predict and prevent deadlocks
            // - Optimize memory layout for related processes
        }
    }
}

/// Initialize the global IPC manager
pub fn init_ipc_manager() {
    let mut ipc_manager = IPC_MANAGER.lock();
    *ipc_manager = Some(IPCManager::new());
}

/// Get reference to global IPC manager
pub fn get_ipc_manager() -> Result<spin::MutexGuard<'static, Option<IPCManager>>, IPCError> {
    Ok(IPC_MANAGER.lock())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ipc_manager_creation() {
        let manager = IPCManager::new();
        assert_eq!(manager.stats.total_resources, 0);
        assert!(manager.consciousness_enabled);
    }

    #[test]
    fn test_pipe_creation() {
        let mut manager = IPCManager::new();
        let pipe_id = manager.create_pipe(1, 1024).unwrap();
        assert!(pipe_id > 0);
        assert_eq!(manager.stats.active_pipes, 1);
        assert_eq!(manager.stats.total_resources, 1);
    }

    #[test]
    fn test_resource_removal() {
        let mut manager = IPCManager::new();
        let pipe_id = manager.create_pipe(1, 1024).unwrap();
        assert_eq!(manager.stats.active_pipes, 1);
        
        manager.remove_resource(pipe_id, 1).unwrap();
        assert_eq!(manager.stats.active_pipes, 0);
        assert_eq!(manager.stats.total_resources, 0);
    }
}

/// Initialize the IPC system
pub fn init_ipc_system() {
    let mut manager_guard = IPC_MANAGER.lock();
    *manager_guard = Some(IPCManager::new());
    // TODO: Complete IPC system initialization
}
