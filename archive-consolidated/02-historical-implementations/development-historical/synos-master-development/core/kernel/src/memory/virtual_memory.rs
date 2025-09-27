/// Virtual memory management for SynOS kernel
/// Handles virtual address space and page table management
use crate::memory::physical::{Frame, PhysicalAddress};
use core::arch::asm;

/// Size of a page (same as frame size on x86_64)
pub const PAGE_SIZE: usize = 4096;

/// Virtual address wrapper
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct VirtualAddress(pub usize);

/// Page structure
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Page {
    pub address: VirtualAddress,
}

/// Page table entry flags
#[derive(Debug, Clone, Copy)]
pub struct PageTableFlags {
    bits: u64,
}

impl PageTableFlags {
    pub const PRESENT: PageTableFlags = PageTableFlags { bits: 1 << 0 };
    pub const WRITABLE: PageTableFlags = PageTableFlags { bits: 1 << 1 };
    pub const USER_ACCESSIBLE: PageTableFlags = PageTableFlags { bits: 1 << 2 };
    pub const WRITE_THROUGH: PageTableFlags = PageTableFlags { bits: 1 << 3 };
    pub const NO_CACHE: PageTableFlags = PageTableFlags { bits: 1 << 4 };
    pub const ACCESSED: PageTableFlags = PageTableFlags { bits: 1 << 5 };
    pub const DIRTY: PageTableFlags = PageTableFlags { bits: 1 << 6 };
    pub const HUGE_PAGE: PageTableFlags = PageTableFlags { bits: 1 << 7 };
    pub const NO_EXECUTE: PageTableFlags = PageTableFlags { bits: 1 << 63 };

    pub fn empty() -> Self {
        PageTableFlags { bits: 0 }
    }

    pub fn contains(&self, other: PageTableFlags) -> bool {
        (self.bits & other.bits) == other.bits
    }
}

impl core::ops::BitOr for PageTableFlags {
    type Output = Self;

    fn bitor(self, rhs: Self) -> Self::Output {
        PageTableFlags {
            bits: self.bits | rhs.bits,
        }
    }
}

/// Page table entry
#[derive(Debug, Clone, Copy)]
pub struct PageTableEntry {
    entry: u64,
}

impl PageTableEntry {
    /// Create a new page table entry
    pub fn new() -> Self {
        PageTableEntry { entry: 0 }
    }

    /// Check if the entry is present
    pub fn is_present(&self) -> bool {
        self.flags().contains(PageTableFlags::PRESENT)
    }

    /// Get the flags of this entry
    pub fn flags(&self) -> PageTableFlags {
        PageTableFlags {
            bits: self.entry & 0xfff,
        }
    }

    /// Get the physical frame this entry points to
    pub fn frame(&self) -> Option<Frame> {
        if self.is_present() {
            Some(Frame {
                address: PhysicalAddress(self.entry as usize & 0x000fffff_fffff000),
            })
        } else {
            None
        }
    }

    /// Set the frame and flags for this entry
    pub fn set(&mut self, frame: Frame, flags: PageTableFlags) {
        self.entry = (frame.start_address().0 as u64) | flags.bits;
    }

    /// Clear this entry
    pub fn clear(&mut self) {
        self.entry = 0;
    }
}

/// Page table with 512 entries
#[repr(align(4096))]
pub struct PageTable {
    entries: [PageTableEntry; 512],
}

impl PageTable {
    /// Create a new empty page table
    pub fn new() -> Self {
        PageTable {
            entries: [PageTableEntry::new(); 512],
        }
    }

    /// Get a reference to the entry at the given index
    pub fn entry(&self, index: usize) -> &PageTableEntry {
        &self.entries[index]
    }

    /// Get a mutable reference to the entry at the given index
    pub fn entry_mut(&mut self, index: usize) -> &mut PageTableEntry {
        &mut self.entries[index]
    }

    /// Clear all entries in this page table
    pub fn clear(&mut self) {
        for entry in self.entries.iter_mut() {
            entry.clear();
        }
    }
}

impl VirtualAddress {
    /// Create a new virtual address
    pub fn new(addr: usize) -> Self {
        VirtualAddress(addr)
    }

    /// Get the page containing this address
    pub fn containing_page(&self) -> Page {
        Page {
            address: VirtualAddress(self.0 & !(PAGE_SIZE - 1)),
        }
    }

    /// Get the page table indices for this address (4-level paging)
    pub fn page_table_indices(&self) -> [usize; 4] {
        let addr = self.0;
        [
            (addr >> 39) & 0x1ff, // PML4 index
            (addr >> 30) & 0x1ff, // PDP index
            (addr >> 21) & 0x1ff, // PD index
            (addr >> 12) & 0x1ff, // PT index
        ]
    }

    /// Get the offset within the page
    pub fn page_offset(&self) -> usize {
        self.0 & 0xfff
    }
}

impl Page {
    /// Get the starting address of this page
    pub fn start_address(&self) -> VirtualAddress {
        self.address
    }

    /// Get the page number
    pub fn number(&self) -> usize {
        self.address.0 / PAGE_SIZE
    }

    /// Create a range of pages
    pub fn range(start: Page, end: Page) -> PageRange {
        PageRange { start, end }
    }
}

/// Range of pages
pub struct PageRange {
    start: Page,
    end: Page,
}

impl Iterator for PageRange {
    type Item = Page;

    fn next(&mut self) -> Option<Self::Item> {
        if self.start.number() < self.end.number() {
            let page = self.start;
            self.start.address.0 += PAGE_SIZE;
            Some(page)
        } else {
            None
        }
    }
}

/// Memory mapper for managing virtual to physical address translation
pub struct MemoryMapper<'a> {
    p4_table: &'a mut PageTable,
    frame_allocator: &'a mut dyn FrameAllocator,
}

impl<'a> MemoryMapper<'a> {
    /// Create a new memory mapper
    /// SAFETY: The caller must ensure the page table is valid
    pub unsafe fn new(
        p4_table: &'a mut PageTable,
        frame_allocator: &'a mut dyn FrameAllocator,
    ) -> Self {
        MemoryMapper {
            p4_table,
            frame_allocator,
        }
    }

    /// Map a page to a frame with the given flags
    pub fn map_page(
        &mut self,
        page: Page,
        frame: Frame,
        flags: PageTableFlags,
    ) -> Result<(), &'static str> {
        let indices = page.start_address().page_table_indices();

        // Navigate through 4-level page table hierarchy
        let current_table = &mut *self.p4_table;

        // Traverse PML4 -> PDP -> PD -> PT
        for (level, &index) in indices.iter().take(3).enumerate() {
            let entry = current_table.entry_mut(index);

            if !entry.is_present() {
                // Allocate new page table for next level
                if let Some(new_frame) = self.frame_allocator.allocate_frame() {
                    entry.set(
                        new_frame,
                        PageTableFlags::PRESENT | PageTableFlags::WRITABLE,
                    );
                    // TODO: Zero out the new page table
                } else {
                    return Err("Failed to allocate frame for page table");
                }
            }

            // For levels 0-2, we need to get the next page table
            // This is simplified - in real implementation would use virtual addressing
            if level < 2 {
                // In a real kernel, we'd map the physical frame to virtual space
                // For now, this is a placeholder
                // current_table = unsafe { &mut *(entry.frame().unwrap().start_address().0 as *mut PageTable) };

                // TODO: Implement proper page table traversal with virtual addressing
                // For now, just handle direct mappings
                break;
            }
        }

        // Set the final page table entry
        let pt_index = indices[3];
        current_table
            .entry_mut(pt_index)
            .set(frame, flags | PageTableFlags::PRESENT);

        // Flush TLB for this page
        unsafe {
            asm!("invlpg [{}]", in(reg) page.start_address().0, options(nostack, preserves_flags));
        }

        Ok(())
    }

    /// Unmap a page
    pub fn unmap_page(&mut self, page: Page) -> Result<Frame, &'static str> {
        let indices = page.start_address().page_table_indices();
        let p4_index = indices[0];

        let entry = self.p4_table.entry_mut(p4_index);
        if let Some(frame) = entry.frame() {
            entry.clear();
            Ok(frame)
        } else {
            Err("Page not mapped")
        }
    }

    /// Translate a virtual address to a physical address
    pub fn translate(&self, addr: VirtualAddress) -> Option<PhysicalAddress> {
        let _page = addr.containing_page();
        let indices = addr.page_table_indices();
        let p4_index = indices[0];

        // Simplified translation - in reality would traverse full page table hierarchy
        if let Some(frame) = self.p4_table.entry(p4_index).frame() {
            Some(PhysicalAddress::new(
                frame.start_address().0 + addr.page_offset(),
            ))
        } else {
            None
        }
    }
}

// Trait for frame allocators to work with memory mapper
pub trait FrameAllocator {
    fn allocate_frame(&mut self) -> Option<Frame>;
    fn deallocate_frame(&mut self, frame: Frame);
}

// Implement the trait for our physical frame allocator
impl FrameAllocator for crate::memory::physical::FrameAllocator {
    fn allocate_frame(&mut self) -> Option<Frame> {
        crate::memory::physical::FrameAllocator::allocate_frame(self)
    }

    fn deallocate_frame(&mut self, frame: Frame) {
        crate::memory::physical::FrameAllocator::deallocate_frame(self, frame)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_virtual_address_page() {
        let addr = VirtualAddress::new(0x1000);
        let page = addr.containing_page();
        assert_eq!(page.start_address().0, 0x1000);
    }

    #[test]
    fn test_page_table_indices() {
        let addr = VirtualAddress::new(0x1ff_1ff_1ff_1ff_000);
        let indices = addr.page_table_indices();
        assert_eq!(indices, [0x1ff, 0x1ff, 0x1ff, 0x1ff]);
    }
}
