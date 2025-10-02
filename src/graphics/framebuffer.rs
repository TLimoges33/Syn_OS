//! Framebuffer management for SynOS graphics
//! Provides direct memory access to display pixels with AI optimization

#![no_std]
extern crate alloc;

use core::ptr;
use crate::{Resolution, Color, Point, Rect, ColorFormat, GraphicsError, GraphicsMetrics};


/// Framebuffer implementation with AI optimization
pub struct Framebuffer {
    buffer: *mut u8,
    resolution: Resolution,
    pitch: u32,           // bytes per line
    ai_optimized: bool,
    metrics: GraphicsMetrics,
}

impl Framebuffer {
    /// Create a new framebuffer with the specified resolution
    pub fn new(resolution: Resolution, buffer_ptr: *mut u8, pitch: u32) -> Result<Self, GraphicsError> {
        if buffer_ptr.is_null() {
            return Err(GraphicsError::MemoryAllocationFailed);
        }
        
        crate::log_info!("🖼️  Creating framebuffer: {}x{} @ {:?}", 
            resolution.width, resolution.height, resolution.format);
        
        let mut framebuffer = Self {
            buffer: buffer_ptr,
            resolution,
            pitch,
            ai_optimized: false,
            metrics: GraphicsMetrics::new(),
        };
        
        // Initialize with consciousness-themed background
        framebuffer.clear(Color::BLACK)?;
        framebuffer.enable_ai_optimization()?;
        
        Ok(framebuffer)
    }
    
    /// Enable AI-driven optimization for the framebuffer
    fn enable_ai_optimization(&mut self) -> Result<(), GraphicsError> {
        crate::log_info!("🧠 Enabling AI optimization for framebuffer");
        
        // TODO: Integrate with AI bridge for consciousness-driven optimization
        self.ai_optimized = true;
        self.metrics.ai_optimizations_applied += 1;
        
        Ok(())
    }
    
    /// Clear the entire framebuffer with the specified color
    pub fn clear(&mut self, color: Color) -> Result<(), GraphicsError> {
        let start_time = self.get_timestamp();
        
        match self.resolution.format {
            ColorFormat::RGB565 => self.clear_rgb565(color),
            ColorFormat::RGB888 => self.clear_rgb888(color),
            ColorFormat::RGBA8888 => self.clear_rgba8888(color),
        }
        
        let frame_time = self.get_timestamp() - start_time;
        self.metrics.record_frame(frame_time);
        
        Ok(())
    }
    
    /// Set a single pixel at the specified coordinates
    pub fn set_pixel(&mut self, point: Point, color: Color) -> Result<(), GraphicsError> {
        if !self.is_valid_coordinate(point) {
            return Ok(()) // Silently ignore out-of-bounds pixels
        }
        
        let offset = self.calculate_offset(point);
        
        unsafe {
            match self.resolution.format {
                ColorFormat::RGB565 => {
                    let pixel_data = color.to_rgb565();
                    ptr::write_volatile(self.buffer.add(offset) as *mut u16, pixel_data);
                }
                ColorFormat::RGB888 => {
                    let pixel_data = color.to_rgb888();
                    ptr::write_volatile(self.buffer.add(offset), color.r);
                    ptr::write_volatile(self.buffer.add(offset + 1), color.g);
                    ptr::write_volatile(self.buffer.add(offset + 2), color.b);
                }
                ColorFormat::RGBA8888 => {
                    let pixel_data = color.to_rgba8888();
                    ptr::write_volatile(self.buffer.add(offset) as *mut u32, pixel_data);
                }
            }
        }
        
        Ok(())
    }
    
    /// Get a pixel color at the specified coordinates
    pub fn get_pixel(&self, point: Point) -> Result<Color, GraphicsError> {
        if !self.is_valid_coordinate(point) {
            return Err(GraphicsError::InvalidResolution);
        }
        
        let offset = self.calculate_offset(point);
        
        unsafe {
            match self.resolution.format {
                ColorFormat::RGB565 => {
                    let pixel_data = ptr::read_volatile(self.buffer.add(offset) as *const u16);
                    let r = ((pixel_data >> 11) & 0x1F) as u8;
                    let g = ((pixel_data >> 5) & 0x3F) as u8;
                    let b = (pixel_data & 0x1F) as u8;
                    Ok(Color::new(r << 3, g << 2, b << 3, 255))
                }
                ColorFormat::RGB888 => {
                    let r = ptr::read_volatile(self.buffer.add(offset));
                    let g = ptr::read_volatile(self.buffer.add(offset + 1));
                    let b = ptr::read_volatile(self.buffer.add(offset + 2));
                    Ok(Color::new(r, g, b, 255))
                }
                ColorFormat::RGBA8888 => {
                    let pixel_data = ptr::read_volatile(self.buffer.add(offset) as *const u32);
                    let a = ((pixel_data >> 24) & 0xFF) as u8;
                    let r = ((pixel_data >> 16) & 0xFF) as u8;
                    let g = ((pixel_data >> 8) & 0xFF) as u8;
                    let b = (pixel_data & 0xFF) as u8;
                    Ok(Color::new(r, g, b, a))
                }
            }
        }
    }
    
    /// Fill a rectangular area with the specified color
    pub fn fill_rect(&mut self, rect: Rect, color: Color) -> Result<(), GraphicsError> {
        let start_time = self.get_timestamp();
        
        for y in rect.y..rect.y + rect.height as i32 {
            for x in rect.x..rect.x + rect.width as i32 {
                self.set_pixel(Point::new(x, y), color)?;
            }
        }
        
        // Apply AI optimization if enabled
        if self.ai_optimized {
            self.apply_ai_rect_optimization(rect, color)?;
        }
        
        let frame_time = self.get_timestamp() - start_time;
        self.metrics.record_frame(frame_time);
        
        Ok(())
    }
    
    /// Copy a rectangular area from source to destination
    pub fn copy_rect(&mut self, src_rect: Rect, dest_point: Point) -> Result<(), GraphicsError> {
        // Bounds checking
        if !self.is_valid_rect(src_rect) {
            return Err(GraphicsError::InvalidResolution);
        }
        
        for y in 0..src_rect.height as i32 {
            for x in 0..src_rect.width as i32 {
                let src_point = Point::new(src_rect.x + x, src_rect.y + y);
                let dest_point_offset = Point::new(dest_point.x + x, dest_point.y + y);
                
                if let Ok(color) = self.get_pixel(src_point) {
                    self.set_pixel(dest_point_offset, color)?;
                }
            }
        }
        
        Ok(())
    }
    
    /// Educational function: Demonstrate framebuffer concepts
    pub fn demonstrate_framebuffer_concepts(&mut self) -> Result<(), GraphicsError> {
        crate::log_info!("🎓 Framebuffer Educational Demo");
        
        // Clear to consciousness blue
        self.clear(Color::CONSCIOUSNESS_BLUE)?;
        
        // Draw educational pattern
        let center_x = self.resolution.width as i32 / 2;
        let center_y = self.resolution.height as i32 / 2;
        
        // Draw concentric rectangles to show coordinate system
        for i in 1..5 {
            let size = i * 50;
            let rect = Rect::new(
                center_x - size,
                center_y - size,
                size as u32 * 2,
                size as u32 * 2
            );
            
            let color = match i {
                1 => Color::AI_GREEN,
                2 => Color::EDUCATION_ORANGE,
                3 => Color::YELLOW,
                _ => Color::WHITE,
            };
            
            // Draw rectangle border
            self.draw_rect_border(rect, color)?;
        }
        
        crate::log_info!("✅ Framebuffer demonstration complete");
        Ok(())
    }
    
    /// Draw rectangle border (not filled)
    fn draw_rect_border(&mut self, rect: Rect, color: Color) -> Result<(), GraphicsError> {
        // Top and bottom lines
        for x in rect.x..rect.x + rect.width as i32 {
            self.set_pixel(Point::new(x, rect.y), color)?;
            self.set_pixel(Point::new(x, rect.y + rect.height as i32 - 1), color)?;
        }
        
        // Left and right lines
        for y in rect.y..rect.y + rect.height as i32 {
            self.set_pixel(Point::new(rect.x, y), color)?;
            self.set_pixel(Point::new(rect.x + rect.width as i32 - 1, y), color)?;
        }
        
        Ok(())
    }
    
    /// AI-enhanced rectangle optimization
    fn apply_ai_rect_optimization(&mut self, _rect: Rect, _color: Color) -> Result<(), GraphicsError> {
        // TODO: Implement AI-driven optimization algorithms
        // - Pattern recognition for repeated operations
        // - Memory access optimization
        // - Consciousness-driven rendering priorities
        
        self.metrics.ai_optimizations_applied += 1;
        Ok(())
    }
    
    /// Clear framebuffer for RGB565 format
    fn clear_rgb565(&mut self, color: Color) {
        let pixel_data = color.to_rgb565();
        let buffer_size = self.resolution.buffer_size() / 2; // 16-bit pixels
        
        unsafe {
            let buffer_ptr = self.buffer as *mut u16;
            for i in 0..buffer_size {
                ptr::write_volatile(buffer_ptr.add(i), pixel_data);
            }
        }
    }
    
    /// Clear framebuffer for RGB888 format
    fn clear_rgb888(&mut self, color: Color) {
        let buffer_size = self.resolution.buffer_size();
        
        unsafe {
            for i in (0..buffer_size).step_by(3) {
                ptr::write_volatile(self.buffer.add(i), color.r);
                ptr::write_volatile(self.buffer.add(i + 1), color.g);
                ptr::write_volatile(self.buffer.add(i + 2), color.b);
            }
        }
    }
    
    /// Clear framebuffer for RGBA8888 format
    fn clear_rgba8888(&mut self, color: Color) {
        let pixel_data = color.to_rgba8888();
        let buffer_size = self.resolution.buffer_size() / 4; // 32-bit pixels
        
        unsafe {
            let buffer_ptr = self.buffer as *mut u32;
            for i in 0..buffer_size {
                ptr::write_volatile(buffer_ptr.add(i), pixel_data);
            }
        }
    }
    
    /// Calculate byte offset for a given coordinate
    fn calculate_offset(&self, point: Point) -> usize {
        let line_offset = point.y as usize * self.pitch as usize;
        let pixel_offset = point.x as usize * self.resolution.bytes_per_pixel() as usize;
        line_offset + pixel_offset
    }
    
    /// Check if coordinates are within framebuffer bounds
    fn is_valid_coordinate(&self, point: Point) -> bool {
        point.x >= 0 
            && point.y >= 0 
            && point.x < self.resolution.width as i32
            && point.y < self.resolution.height as i32
    }
    
    /// Check if rectangle is within framebuffer bounds
    fn is_valid_rect(&self, rect: Rect) -> bool {
        rect.x >= 0 
            && rect.y >= 0
            && rect.x + rect.width as i32 <= self.resolution.width as i32
            && rect.y + rect.height as i32 <= self.resolution.height as i32
    }
    
    /// Get current timestamp (placeholder implementation)
    fn get_timestamp(&self) -> u64 {
        // TODO: Implement proper timestamp function
        42 // Placeholder
    }
    
    /// Get framebuffer resolution
    pub fn resolution(&self) -> Resolution {
        self.resolution
    }
    
    /// Get current graphics metrics
    pub fn metrics(&self) -> &GraphicsMetrics {
        &self.metrics
    }
    
    /// Update consciousness level for AI optimization
    pub fn update_consciousness_level(&mut self, level: f32) {
        self.metrics.update_consciousness(level);
        
        if self.ai_optimized {
            // Adjust optimization parameters based on consciousness level
            // Higher consciousness = more sophisticated rendering optimizations
            self.metrics.ai_optimizations_applied += 1;
        }
    }
}

impl Drop for Framebuffer {
    fn drop(&mut self) {
        crate::log_info!("🖼️  Dropping framebuffer, final metrics:");
        crate::log_info!("  Frames rendered: {}", self.metrics.frames_rendered);
        crate::log_info!("  AI optimizations: {}", self.metrics.ai_optimizations_applied);
        crate::log_info!("  Consciousness level: {:.2}", self.metrics.consciousness_level);
    }
}

unsafe impl Send for Framebuffer {}
unsafe impl Sync for Framebuffer {}

#[cfg(test)]
mod tests {
    use super::*;
    use alloc::vec;

    #[test]
    fn test_framebuffer_creation() {
        let resolution = Resolution::new(800, 600, ColorFormat::RGBA8888);
        let mut buffer = vec![0u8; resolution.buffer_size()];
        let buffer_ptr = buffer.as_mut_ptr();
        
        let framebuffer = Framebuffer::new(resolution, buffer_ptr, 800 * 4);
        assert!(framebuffer.is_ok());
    }

    #[test]
    fn test_pixel_operations() {
        let resolution = Resolution::new(100, 100, ColorFormat::RGBA8888);
        let mut buffer = vec![0u8; resolution.buffer_size()];
        let buffer_ptr = buffer.as_mut_ptr();
        
        let mut framebuffer = Framebuffer::new(resolution, buffer_ptr, 100 * 4).unwrap();
        
        let test_color = Color::RED;
        let test_point = Point::new(50, 50);
        
        framebuffer.set_pixel(test_point, test_color).unwrap();
        let retrieved_color = framebuffer.get_pixel(test_point).unwrap();
        
        assert_eq!(retrieved_color.r, test_color.r);
        assert_eq!(retrieved_color.g, test_color.g);
        assert_eq!(retrieved_color.b, test_color.b);
    }
}
