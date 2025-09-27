//! Shared Memory Implementation for Inter-Process Communication
//! 
//! Provides consciousness-aware shared memory segments with intelligent
//! access patterns and memory optimization.

use alloc::collections::BTreeMap;
use alloc::vec::Vec;
use alloc::string::String;
use core::sync::atomic::{AtomicU64, Ordering};
use core::ptr::NonNull;
use spin::Mutex;

use super::{IPCError, IPCId, IPCPermissions};

/// Shared memory segment metadata
#[derive(Debug, Clone)]
pub struct SharedMemoryInfo {
    pub id: IPCId,
    pub size: usize,
    pub key: Option<String>,
    pub creator_pid: u64,
    pub attached_processes: usize,
    pub created_at: u64,
    pub last_accessed: u64,
    pub access_count: u64,
    pub permissions: IPCPermissions,
    pub consciousness_priority: u8,
}

/// Shared memory access record
#[derive(Debug, Clone)]
pub struct MemoryAccess {
    pub pid: u64,
    pub access_type: AccessType,
    pub timestamp: u64,
    pub offset: usize,
    pub size: usize,
}

/// Memory access type
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AccessType {
    Read,
    Write,
    Map,
    Unmap,
}

/// Thread-safe memory pointer wrapper
#[derive(Debug)]
struct SafeMemoryPtr {
    ptr: NonNull<u8>,
}

unsafe impl Send for SafeMemoryPtr {}
unsafe impl Sync for SafeMemoryPtr {}

impl SafeMemoryPtr {
    fn new(ptr: NonNull<u8>) -> Self {
        Self { ptr }
    }
    
    fn as_ptr(&self) -> *mut u8 {
        self.ptr.as_ptr()
    }
}

/// Consciousness-aware shared memory segment
pub struct SharedMemorySegment {
    info: SharedMemoryInfo,
    memory: SafeMemoryPtr,
    attached_processes: Mutex<BTreeMap<u64, MemoryAttachment>>,
    access_history: Mutex<Vec<MemoryAccess>>,
    
    // Consciousness features
    consciousness_enabled: bool,
    auto_optimize: bool,
    hot_regions: Mutex<Vec<MemoryRegion>>,
    
    // Statistics
    total_reads: AtomicU64,
    total_writes: AtomicU64,
    total_maps: AtomicU64,
    consciousness_optimizations: AtomicU64,
}

/// Memory attachment information
#[derive(Debug, Clone)]
pub struct MemoryAttachment {
    pub pid: u64,
    pub virtual_address: usize,
    pub permissions: IPCPermissions,
    pub attached_at: u64,
    pub access_count: u64,
}

/// Hot memory region for consciousness optimization
#[derive(Debug, Clone)]
pub struct MemoryRegion {
    pub offset: usize,
    pub size: usize,
    pub access_count: u64,
    pub last_accessed: u64,
    pub priority: u8,
}

impl SharedMemorySegment {
    /// Create a new shared memory segment
    pub fn new(size: usize, key: Option<String>) -> Result<Self, IPCError> {
        if size == 0 {
            return Err(IPCError::InvalidArgument);
        }

        // Allocate memory (simplified - in real implementation would use proper memory allocation)
        let memory_ptr = NonNull::new(
            unsafe { alloc::alloc::alloc_zeroed(
                alloc::alloc::Layout::from_size_align(size, 8)
                    .map_err(|_| IPCError::OutOfMemory)?
            ) }
        ).ok_or(IPCError::OutOfMemory)?;

        let memory = SafeMemoryPtr::new(memory_ptr);

        let info = SharedMemoryInfo {
            id: 0, // Will be set by manager
            size,
            key,
            creator_pid: 0, // Will be set by manager
            attached_processes: 0,
            created_at: Self::get_current_time(),
            last_accessed: Self::get_current_time(),
            access_count: 0,
            permissions: IPCPermissions::default(),
            consciousness_priority: 5, // Default medium priority
        };

        Ok(Self {
            info,
            memory,
            attached_processes: Mutex::new(BTreeMap::new()),
            access_history: Mutex::new(Vec::new()),
            consciousness_enabled: true,
            auto_optimize: true,
            hot_regions: Mutex::new(Vec::new()),
            total_reads: AtomicU64::new(0),
            total_writes: AtomicU64::new(0),
            total_maps: AtomicU64::new(0),
            consciousness_optimizations: AtomicU64::new(0),
        })
    }

    /// Attach a process to this shared memory segment
    pub fn attach(&self, pid: u64, virtual_address: usize, permissions: IPCPermissions) -> Result<(), IPCError> {
        let mut attached = self.attached_processes.lock();
        
        if attached.contains_key(&pid) {
            return Err(IPCError::ResourceBusy);
        }

        let attachment = MemoryAttachment {
            pid,
            virtual_address,
            permissions,
            attached_at: Self::get_current_time(),
            access_count: 0,
        };

        attached.insert(pid, attachment);
        self.total_maps.fetch_add(1, Ordering::SeqCst);

        // Record access
        self.record_access(pid, AccessType::Map, 0, self.info.size);

        Ok(())
    }

    /// Detach a process from this shared memory segment
    pub fn detach(&self, pid: u64) -> Result<(), IPCError> {
        let mut attached = self.attached_processes.lock();
        
        attached.remove(&pid).ok_or(IPCError::ResourceNotFound)?;

        // Record access
        self.record_access(pid, AccessType::Unmap, 0, self.info.size);

        Ok(())
    }

    /// Read data from shared memory
    pub fn read(&self, pid: u64, offset: usize, buffer: &mut [u8]) -> Result<usize, IPCError> {
        // Check if process is attached and has read permissions
        let attached = self.attached_processes.lock();
        let attachment = attached.get(&pid).ok_or(IPCError::PermissionDenied)?;
        
        if !attachment.permissions.read {
            return Err(IPCError::PermissionDenied);
        }

        if offset + buffer.len() > self.info.size {
            return Err(IPCError::InvalidArgument);
        }

        // Copy data from shared memory
        unsafe {
            let src = self.memory.as_ptr().add(offset);
            core::ptr::copy_nonoverlapping(src, buffer.as_mut_ptr(), buffer.len());
        }

        self.total_reads.fetch_add(1, Ordering::SeqCst);
        self.record_access(pid, AccessType::Read, offset, buffer.len());

        // Update hot regions
        if self.consciousness_enabled {
            self.update_hot_regions(offset, buffer.len());
        }

        Ok(buffer.len())
    }

    /// Write data to shared memory
    pub fn write(&self, pid: u64, offset: usize, data: &[u8]) -> Result<usize, IPCError> {
        // Check if process is attached and has write permissions
        let attached = self.attached_processes.lock();
        let attachment = attached.get(&pid).ok_or(IPCError::PermissionDenied)?;
        
        if !attachment.permissions.write {
            return Err(IPCError::PermissionDenied);
        }

        if offset + data.len() > self.info.size {
            return Err(IPCError::InvalidArgument);
        }

        // Copy data to shared memory
        unsafe {
            let dst = self.memory.as_ptr().add(offset);
            core::ptr::copy_nonoverlapping(data.as_ptr(), dst, data.len());
        }

        self.total_writes.fetch_add(1, Ordering::SeqCst);
        self.record_access(pid, AccessType::Write, offset, data.len());

        // Update hot regions
        if self.consciousness_enabled {
            self.update_hot_regions(offset, data.len());
        }

        Ok(data.len())
    }

    /// Get raw memory pointer (for direct access)
    pub fn get_memory_ptr(&self) -> *mut u8 {
        self.memory.as_ptr()
    }

    /// Get segment information
    pub fn get_info(&self) -> &SharedMemoryInfo {
        &self.info
    }

    /// Get attached process count
    pub fn get_attached_count(&self) -> usize {
        self.attached_processes.lock().len()
    }

    /// Record memory access for consciousness analysis
    fn record_access(&self, pid: u64, access_type: AccessType, offset: usize, size: usize) {
        let mut history = self.access_history.lock();
        
        let access = MemoryAccess {
            pid,
            access_type,
            timestamp: Self::get_current_time(),
            offset,
            size,
        };

        history.push(access);

        // Limit history size to prevent memory bloat
        if history.len() > 1000 {
            history.remove(0);
        }
    }

    /// Update hot memory regions for consciousness optimization
    fn update_hot_regions(&self, offset: usize, size: usize) {
        let mut hot_regions = self.hot_regions.lock();
        let current_time = Self::get_current_time();

        // Find existing region or create new one
        let mut found = false;
        for region in hot_regions.iter_mut() {
            if offset >= region.offset && offset < region.offset + region.size {
                region.access_count += 1;
                region.last_accessed = current_time;
                found = true;
                break;
            }
        }

        if !found {
            hot_regions.push(MemoryRegion {
                offset,
                size,
                access_count: 1,
                last_accessed: current_time,
                priority: 5,
            });
        }

        // Consciousness optimization trigger
        if hot_regions.len() > 10 && self.auto_optimize {
            self.optimize_hot_regions(&mut hot_regions);
        }
    }

    /// Optimize hot regions using consciousness algorithms
    fn optimize_hot_regions(&self, hot_regions: &mut Vec<MemoryRegion>) {
        // Sort by access count and recency
        hot_regions.sort_by(|a, b| {
            b.access_count.cmp(&a.access_count)
                .then(b.last_accessed.cmp(&a.last_accessed))
        });

        // Keep only top regions
        hot_regions.truncate(5);

        // Update priorities based on consciousness analysis
        for (i, region) in hot_regions.iter_mut().enumerate() {
            region.priority = (10 - i) as u8;
        }

        self.consciousness_optimizations.fetch_add(1, Ordering::SeqCst);
    }

    /// Get current time (simplified)
    fn get_current_time() -> u64 {
        // In a real implementation, this would get system time
        0
    }

    /// Get shared memory statistics
    pub fn get_stats(&self) -> SharedMemoryStats {
        let attached = self.attached_processes.lock();
        let hot_regions = self.hot_regions.lock();

        SharedMemoryStats {
            size: self.info.size,
            attached_processes: attached.len(),
            total_reads: self.total_reads.load(Ordering::SeqCst),
            total_writes: self.total_writes.load(Ordering::SeqCst),
            total_maps: self.total_maps.load(Ordering::SeqCst),
            hot_regions_count: hot_regions.len(),
            consciousness_optimizations: self.consciousness_optimizations.load(Ordering::SeqCst),
            access_history_size: self.access_history.lock().len(),
        }
    }
}

impl Drop for SharedMemorySegment {
    fn drop(&mut self) {
        // Free allocated memory
        unsafe {
            alloc::alloc::dealloc(
                self.memory.as_ptr(),
                alloc::alloc::Layout::from_size_align(self.info.size, 8).unwrap()
            );
        }
    }
}

/// Shared memory statistics
#[derive(Debug)]
pub struct SharedMemoryStats {
    pub size: usize,
    pub attached_processes: usize,
    pub total_reads: u64,
    pub total_writes: u64,
    pub total_maps: u64,
    pub hot_regions_count: usize,
    pub consciousness_optimizations: u64,
    pub access_history_size: usize,
}

/// Shared memory manager
pub struct SharedMemoryManager {
    segments: BTreeMap<IPCId, SharedMemorySegment>,
    keyed_segments: BTreeMap<String, IPCId>,
}

impl SharedMemoryManager {
    pub fn new() -> Self {
        Self {
            segments: BTreeMap::new(),
            keyed_segments: BTreeMap::new(),
        }
    }

    pub fn add_segment(&mut self, id: IPCId, mut segment: SharedMemorySegment) -> Result<(), IPCError> {
        // Set the ID in the segment info
        segment.info.id = id;

        // Handle keyed segments
        if let Some(ref key) = segment.info.key {
            if self.keyed_segments.contains_key(key) {
                return Err(IPCError::ResourceBusy);
            }
            self.keyed_segments.insert(key.clone(), id);
        }

        self.segments.insert(id, segment);
        Ok(())
    }

    pub fn remove_segment(&mut self, id: IPCId) -> Result<(), IPCError> {
        if let Some(segment) = self.segments.remove(&id) {
            // Remove from keyed segments if applicable
            if let Some(ref key) = segment.info.key {
                self.keyed_segments.remove(key);
            }
            Ok(())
        } else {
            Err(IPCError::ResourceNotFound)
        }
    }

    pub fn get_segment(&self, id: IPCId) -> Option<&SharedMemorySegment> {
        self.segments.get(&id)
    }

    pub fn get_segment_mut(&mut self, id: IPCId) -> Option<&mut SharedMemorySegment> {
        self.segments.get_mut(&id)
    }

    pub fn find_keyed_segment(&self, key: &str) -> Option<IPCId> {
        self.keyed_segments.get(key).copied()
    }

    pub fn get_segment_count(&self) -> usize {
        self.segments.len()
    }

    pub fn get_total_memory_usage(&self) -> usize {
        self.segments.values().map(|s| s.info.size).sum()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_shared_memory_creation() {
        let segment = SharedMemorySegment::new(4096, None).unwrap();
        assert_eq!(segment.info.size, 4096);
        assert_eq!(segment.get_attached_count(), 0);
    }

    #[test]
    fn test_shared_memory_attach_detach() {
        let segment = SharedMemorySegment::new(4096, None).unwrap();
        let pid = 1;
        let permissions = IPCPermissions::default();

        segment.attach(pid, 0x1000, permissions).unwrap();
        assert_eq!(segment.get_attached_count(), 1);

        segment.detach(pid).unwrap();
        assert_eq!(segment.get_attached_count(), 0);
    }

    #[test]
    fn test_shared_memory_read_write() {
        let segment = SharedMemorySegment::new(4096, None).unwrap();
        let pid = 1;
        let permissions = IPCPermissions::default();

        segment.attach(pid, 0x1000, permissions).unwrap();

        // Write data
        let data = b"Consciousness-aware shared memory!";
        let bytes_written = segment.write(pid, 0, data).unwrap();
        assert_eq!(bytes_written, data.len());

        // Read data
        let mut buffer = [0u8; 64];
        let bytes_read = segment.read(pid, 0, &mut buffer).unwrap();
        assert_eq!(bytes_read, data.len());
        assert_eq!(&buffer[..bytes_read], data);
    }

    #[test]
    fn test_shared_memory_manager() {
        let mut manager = SharedMemoryManager::new();
        let segment = SharedMemorySegment::new(4096, None).unwrap();

        manager.add_segment(1, segment).unwrap();
        assert_eq!(manager.get_segment_count(), 1);
        assert_eq!(manager.get_total_memory_usage(), 4096);

        manager.remove_segment(1).unwrap();
        assert_eq!(manager.get_segment_count(), 0);
    }
}
