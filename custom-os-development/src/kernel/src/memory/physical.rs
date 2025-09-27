/// Physical memory management for SynOS kernel
/// Handles physical frame allocation and memory mapping

/// Size of a memory frame (4KB on x86_64)
pub const FRAME_SIZE: usize = 4096;

/// Trait for frame allocation
pub trait FrameAllocator {
    /// Allocate a frame and return it
    fn allocate_frame(&mut self) -> Option<Frame>;
    
    /// Deallocate a frame
    fn deallocate_frame(&mut self, frame: Frame);
}

/// Physical frame allocator using a bitmap
/// Note: This is a simplified allocator for demonstration purposes
/// In a real kernel, proper synchronization would be required
pub struct BitmapFrameAllocator {
    memory_map: &'static mut [u8],
    next_free_frame: usize,
    max_frame: usize,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct PhysicalAddress(pub usize);

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Frame {
    pub address: PhysicalAddress,
}

impl PhysicalAddress {
    /// Create a new physical address
    pub fn new(addr: usize) -> Self {
        PhysicalAddress(addr)
    }
    
    /// Convert to u64 for compatibility
    pub fn as_u64(&self) -> u64 {
        self.0 as u64
    }

    /// Get the frame containing this address
    pub fn containing_frame(&self) -> Frame {
        Frame {
            address: PhysicalAddress(self.0 & !(FRAME_SIZE - 1)),
        }
    }
}

impl Frame {
    /// Get the starting address of this frame
    pub fn start_address(&self) -> PhysicalAddress {
        self.address
    }

    /// Get the frame number
    pub fn number(&self) -> usize {
        self.address.0 / FRAME_SIZE
    }
}

impl BitmapFrameAllocator {
    /// Create a new frame allocator
    /// SAFETY: The caller must ensure the memory map is valid and mutable
    pub unsafe fn new(memory_map: &'static mut [u8], max_frame: usize) -> Self {
        BitmapFrameAllocator {
            memory_map,
            next_free_frame: 0,
            max_frame,
        }
    }

    /// Allocate a free frame (internal implementation)
    fn allocate_frame_internal(&mut self) -> Option<Frame> {
        // First try from the cached next_free_frame position for efficiency
        for frame_num in self.next_free_frame..self.max_frame {
            if self.is_frame_free(frame_num) {
                self.set_frame_used(frame_num);
                self.next_free_frame = frame_num + 1;
                return Some(Frame {
                    address: PhysicalAddress(frame_num * FRAME_SIZE),
                });
            }
        }
        None
    }

    /// Deallocate a frame (internal implementation)
    fn deallocate_frame_internal(&mut self, frame: Frame) {
        let frame_num = frame.number();
        self.set_frame_free(frame_num);
        if frame_num < self.next_free_frame {
            self.next_free_frame = frame_num;
        }
    }

    /// Check if a frame is free
    fn is_frame_free(&self, frame_num: usize) -> bool {
        let byte_index = frame_num / 8;
        let bit_index = frame_num % 8;
        if byte_index >= self.memory_map.len() {
            return false;
        }
        (self.memory_map[byte_index] & (1 << bit_index)) == 0
    }

    /// Mark a frame as used
    fn set_frame_used(&mut self, frame_num: usize) {
        let byte_index = frame_num / 8;
        let bit_index = frame_num % 8;
        if byte_index < self.memory_map.len() {
            self.memory_map[byte_index] |= 1 << bit_index;
        }
    }

    /// Mark a frame as free
    fn set_frame_free(&mut self, frame_num: usize) {
        let byte_index = frame_num / 8;
        let bit_index = frame_num % 8;
        if byte_index < self.memory_map.len() {
            self.memory_map[byte_index] &= !(1 << bit_index);
        }
    }

    /// Get total number of frames
    pub fn total_frames(&self) -> usize {
        self.max_frame
    }

    /// Get number of free frames (approximate)
    pub fn free_frames(&self) -> usize {
        let mut count = 0;
        for frame_num in 0..self.max_frame {
            if self.is_frame_free(frame_num) {
                count += 1;
            }
        }
        count
    }
}

/// Implement the FrameAllocator trait for BitmapFrameAllocator
impl FrameAllocator for BitmapFrameAllocator {
    fn allocate_frame(&mut self) -> Option<Frame> {
        self.allocate_frame_internal()
    }
    
    fn deallocate_frame(&mut self, frame: Frame) {
        self.deallocate_frame_internal(frame)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_physical_address_frame() {
        let addr = PhysicalAddress::new(0x1000);
        let frame = addr.containing_frame();
        assert_eq!(frame.start_address().0, 0x1000);
    }

    #[test]
    fn test_frame_number() {
        let frame = Frame {
            address: PhysicalAddress::new(0x2000),
        };
        assert_eq!(frame.number(), 2);
    }
}
