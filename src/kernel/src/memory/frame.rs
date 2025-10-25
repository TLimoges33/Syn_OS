//! Frame Allocator Module
//!
//! Implements physical memory frame allocation

use bootloader::boot_info::{MemoryRegions, MemoryRegionKind};
use x86_64::{
    structures::paging::{FrameAllocator, PhysFrame, Size4KiB},
    PhysAddr,
};
use core::sync::atomic::{AtomicUsize, Ordering};
use crate::println;

/// Frame allocator that uses the bootloader's memory map
pub struct BootInfoFrameAllocator {
    memory_regions: &'static MemoryRegions,
    next: AtomicUsize,
}

impl BootInfoFrameAllocator {
    /// Create a new BootInfoFrameAllocator
    pub unsafe fn init(memory_regions: &'static MemoryRegions) -> Self {
        BootInfoFrameAllocator {
            memory_regions,
            next: AtomicUsize::new(0),
        }
    }
    
    /// Returns an iterator over the usable frames
    fn usable_frames(&self) -> impl Iterator<Item = PhysFrame> {
        // Get usable regions from memory map
        let regions = self.memory_regions
            .iter()
            .filter(|r| r.kind == MemoryRegionKind::Usable);
            
        // Map each region to its address range
        let addr_ranges = regions.map(|r| r.start..r.end);
        
        // Transform to an iterator of frame start addresses
        let frame_addresses = addr_ranges.flat_map(|r| r.step_by(4096));
        
        // Create PhysFrame objects from the start addresses
        frame_addresses.map(|addr| PhysFrame::containing_address(PhysAddr::new(addr)))
    }
}

unsafe impl FrameAllocator<Size4KiB> for BootInfoFrameAllocator {
    fn allocate_frame(&mut self) -> Option<PhysFrame> {
        // Get all usable frames
        let mut frames = self.usable_frames();
        
        // Get the index of the next available frame
        let current_next = self.next.fetch_add(1, Ordering::SeqCst);
        
        // Find the frame at that index
        frames.nth(current_next)
    }
}

/// Consciousness-enhanced frame allocator for quantum and GPU operations
pub struct ConsciousnessFrameAllocator {
    inner: BootInfoFrameAllocator,
    quantum_frames: usize,
    gpu_frames: usize,
}

impl ConsciousnessFrameAllocator {
    pub fn init(memory_regions: &'static MemoryRegions) -> Self {
        ConsciousnessFrameAllocator {
            inner: unsafe { BootInfoFrameAllocator::init(memory_regions) },
            quantum_frames: 0,
            gpu_frames: 0,
        }
    }
    
    /// Allocate a frame specifically for quantum operations
    pub fn allocate_quantum_frame(&mut self) -> Option<PhysFrame> {
        // Allocate a normal frame
        let frame = self.inner.allocate_frame();
        
        // If allocation succeeded, mark it as a quantum frame
        if frame.is_some() {
            self.quantum_frames += 1;
            crate::println!("  • Allocated quantum frame (total: {})", self.quantum_frames);
        }
        
        frame
    }
    
    /// Allocate a frame specifically for GPU operations
    pub fn allocate_gpu_frame(&mut self) -> Option<PhysFrame> {
        // Allocate a normal frame for GPU memory mapping
        let frame = self.inner.allocate_frame();
        
        // If allocation succeeded, mark it as a GPU frame
        if frame.is_some() {
            self.gpu_frames += 1;
            crate::println!("  • Allocated GPU frame (total: {})", self.gpu_frames);
        }
        
        frame
    }
}

unsafe impl FrameAllocator<Size4KiB> for ConsciousnessFrameAllocator {
    fn allocate_frame(&mut self) -> Option<PhysFrame> {
        self.inner.allocate_frame()
    }
}
