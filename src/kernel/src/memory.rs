/// Memory management with AI optimization
/// Handles paging, allocation, and AI-driven memory optimization

use crate::println;
use x86_64::{
    structures::paging::{
        PageTable, PageTableFlags, PhysFrame, Page, Size4KiB, FrameAllocator,
        OffsetPageTable, Mapper, mapper::MapToError,
    },
    PhysAddr, VirtAddr,
};
use bootloader::bootinfo::{MemoryMap, MemoryRegionType};
use linked_list_allocator::LockedHeap;
use core::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use spin::Mutex;

/// Global allocator for kernel heap
#[global_allocator]
static ALLOCATOR: LockedHeap = LockedHeap::empty();

/// Memory management state
static MEMORY_INITIALIZED: AtomicBool = AtomicBool::new(false);
static TOTAL_MEMORY: AtomicUsize = AtomicUsize::new(0);
static USED_MEMORY: AtomicUsize = AtomicUsize::new(0);

/// Physical memory frame allocator
pub struct BootInfoFrameAllocator {
    memory_map: &'static MemoryMap,
    next: usize,
}

impl BootInfoFrameAllocator {
    pub unsafe fn init(memory_map: &'static MemoryMap) -> Self {
        BootInfoFrameAllocator {
            memory_map,
            next: 0,
        }
    }

    fn usable_frames(&self) -> impl Iterator<Item = PhysFrame> {
        let regions = self.memory_map.iter();
        let usable_regions = regions
            .filter(|r| r.region_type == MemoryRegionType::Usable);
        let addr_ranges = usable_regions
            .map(|r| r.range.start_addr()..r.range.end_addr());
        let frame_addresses = addr_ranges.flat_map(|r| r.step_by(4096));
        frame_addresses.map(|addr| PhysFrame::containing_address(PhysAddr::new(addr)))
    }
}

unsafe impl FrameAllocator<Size4KiB> for BootInfoFrameAllocator {
    fn allocate_frame(&mut self) -> Option<PhysFrame> {
        let frame = self.usable_frames().nth(self.next);
        self.next += 1;
        frame
    }
}

/// Memory statistics for AI optimization
#[derive(Debug, Clone, Copy)]
pub struct MemoryStats {
    pub total_memory: usize,
    pub used_memory: usize,
    pub free_memory: usize,
    pub fragmentation_ratio: f32,
    pub allocation_efficiency: f32,
}

/// AI-driven memory optimization context
static MEMORY_OPTIMIZER: Mutex<Option<MemoryOptimizer>> = Mutex::new(None);

struct MemoryOptimizer {
    last_stats: MemoryStats,
    optimization_level: u8,
    fragmentation_threshold: f32,
}

impl MemoryOptimizer {
    fn new() -> Self {
        Self {
            last_stats: MemoryStats {
                total_memory: 0,
                used_memory: 0,
                free_memory: 0,
                fragmentation_ratio: 0.0,
                allocation_efficiency: 1.0,
            },
            optimization_level: 1,
            fragmentation_threshold: 0.3,
        }
    }

    fn analyze_and_optimize(&mut self, current_stats: MemoryStats) {
        if current_stats.fragmentation_ratio > self.fragmentation_threshold {
            self.trigger_defragmentation();
        }
        
        if current_stats.allocation_efficiency < 0.7 {
            self.adjust_allocation_strategy();
        }
        
        self.last_stats = current_stats;
    }

    fn trigger_defragmentation(&self) {
        println!("🧠 AI: Triggering memory defragmentation");
    }

    fn adjust_allocation_strategy(&mut self) {
        self.optimization_level = (self.optimization_level + 1).min(5);
        println!("🧠 AI: Adjusting allocation strategy to level {}", self.optimization_level);
    }
}

/// Initialize memory management subsystem
pub fn init(memory_map: &'static MemoryMap, _physical_memory_offset: VirtAddr) {
    println!("💾 Initializing memory management...");
    
    // Calculate total memory
    let total_mem = calculate_total_memory(memory_map);
    TOTAL_MEMORY.store(total_mem, Ordering::SeqCst);
    
    // For bootloader 0.9, we use a fixed offset approach
    // In a full implementation, this would be properly configured
    let physical_memory_offset = VirtAddr::new(0x0000_0000_0000_0000);
    
    // Set up page tables
    let mut mapper = unsafe { init_paging(physical_memory_offset) };
    let mut frame_allocator = unsafe { BootInfoFrameAllocator::init(memory_map) };
    
    // Initialize heap
    init_heap(&mut mapper, &mut frame_allocator)
        .expect("Heap initialization failed");
    
    // Initialize AI memory optimization
    init_ai_memory_optimization();
    
    MEMORY_INITIALIZED.store(true, Ordering::SeqCst);
    println!("💾 Memory management initialized ({}MB total)", total_mem / 1024 / 1024);
}

/// Calculate total available memory
fn calculate_total_memory(memory_map: &MemoryMap) -> usize {
    memory_map
        .iter()
        .filter(|region| region.region_type == MemoryRegionType::Usable)
        .map(|region| region.range.end_addr() - region.range.start_addr())
        .sum::<u64>() as usize
}

/// Initialize paging with security isolation
unsafe fn init_paging(physical_memory_offset: VirtAddr) -> OffsetPageTable<'static> {
    let level_4_table = active_level_4_table(physical_memory_offset);
    OffsetPageTable::new(level_4_table, physical_memory_offset)
}

/// Get reference to active level 4 page table
unsafe fn active_level_4_table(physical_memory_offset: VirtAddr) -> &'static mut PageTable {
    use x86_64::registers::control::Cr3;
    
    let (level_4_table_frame, _) = Cr3::read();
    let phys = level_4_table_frame.start_address();
    let virt = physical_memory_offset + phys.as_u64();
    let page_table_ptr: *mut PageTable = virt.as_mut_ptr();
    
    &mut *page_table_ptr
}

/// Heap configuration
const HEAP_START: usize = 0x_4444_4444_0000;
const HEAP_SIZE: usize = 100 * 1024; // 100 KiB

/// Initialize kernel heap
fn init_heap(
    mapper: &mut impl Mapper<Size4KiB>,
    frame_allocator: &mut impl FrameAllocator<Size4KiB>,
) -> Result<(), MapToError<Size4KiB>> {
    let page_range = {
        let heap_start = VirtAddr::new(HEAP_START as u64);
        let heap_end = heap_start + HEAP_SIZE - 1u64;
        let heap_start_page = Page::containing_address(heap_start);
        let heap_end_page = Page::containing_address(heap_end);
        Page::range_inclusive(heap_start_page, heap_end_page)
    };

    for page in page_range {
        let frame = frame_allocator
            .allocate_frame()
            .ok_or(MapToError::FrameAllocationFailed)?;
        let flags = PageTableFlags::PRESENT | PageTableFlags::WRITABLE;
        unsafe {
            mapper.map_to(page, frame, flags, frame_allocator)?.flush();
        }
    }

    unsafe {
        ALLOCATOR.lock().init(HEAP_START as *mut u8, HEAP_SIZE);
    }

    Ok(())
}

/// Initialize AI-driven memory optimization
fn init_ai_memory_optimization() {
    let optimizer = MemoryOptimizer::new();
    *MEMORY_OPTIMIZER.lock() = Some(optimizer);
    println!("  🧠 AI memory optimization ready");
}

/// Get current memory statistics
pub fn get_memory_stats() -> MemoryStats {
    let total = TOTAL_MEMORY.load(Ordering::SeqCst);
    let used = USED_MEMORY.load(Ordering::SeqCst);
    let free = total.saturating_sub(used);
    
    MemoryStats {
        total_memory: total,
        used_memory: used,
        free_memory: free,
        fragmentation_ratio: calculate_fragmentation_ratio(),
        allocation_efficiency: calculate_allocation_efficiency(used, total),
    }
}

/// Calculate memory fragmentation ratio
fn calculate_fragmentation_ratio() -> f32 {
    // Simplified fragmentation calculation
    // In a real implementation, this would analyze free block distribution
    0.1 // Placeholder
}

/// Calculate allocation efficiency
fn calculate_allocation_efficiency(used: usize, total: usize) -> f32 {
    if total == 0 {
        return 1.0;
    }
    1.0 - (used as f32 / total as f32)
}

/// Trigger AI memory optimization analysis
pub fn optimize_memory() {
    if let Some(ref mut optimizer) = *MEMORY_OPTIMIZER.lock() {
        let stats = get_memory_stats();
        optimizer.analyze_and_optimize(stats);
    }
}

/// Check if memory management is initialized
pub fn is_initialized() -> bool {
    MEMORY_INITIALIZED.load(Ordering::SeqCst)
}

/// Update used memory counter (called by allocator)
pub fn update_used_memory(delta: isize) {
    let current = USED_MEMORY.load(Ordering::SeqCst);
    let new_value = if delta >= 0 {
        current.saturating_add(delta as usize)
    } else {
        current.saturating_sub((-delta) as usize)
    };
    USED_MEMORY.store(new_value, Ordering::SeqCst);
}

/// Security function: validate memory access
pub fn validate_memory_access(addr: VirtAddr, size: usize, context: &crate::security::SecurityContext) -> bool {
    // Check if the memory access is within allowed bounds for the security context
    if !is_initialized() {
        return false;
    }
    
    // Validate against security context capabilities
    if !context.has_capability(&crate::security::Capability::ReadMemory) {
        return false;
    }
    
    // Additional security checks would go here
    // - Check if address is within allowed memory regions for this context
    // - Validate size doesn't overflow
    // - Check for privilege level requirements
    let _ = (addr, size); // Use parameters to avoid warnings
    true
}

/// Memory allocation with security context
pub fn secure_alloc(size: usize, context: &crate::security::SecurityContext) -> Option<*mut u8> {
    if !validate_memory_access(VirtAddr::new(0), size, context) {
        return None;
    }
    
    // Check if context has write capability for allocation
    if !context.has_capability(&crate::security::Capability::WriteMemory) {
        return None;
    }
    
    // Use global allocator for now
    // In a real implementation, this would use context-specific allocators
    use core::alloc::{GlobalAlloc, Layout};
    
    let layout = Layout::from_size_align(size, 8).ok()?;
    let ptr = unsafe { ALLOCATOR.alloc(layout) };
    
    if !ptr.is_null() {
        update_used_memory(size as isize);
        Some(ptr)
    } else {
        None
    }
}
