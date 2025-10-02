//! SynOS Graphics Framework
//! Phase 5.1: Core Graphics Implementation with AI Integration
//!
//! This module provides the foundational graphics system for SynOS,
//! including framebuffer management, display drivers, and AI-enhanced
//! graphics optimization.

#![no_std]
extern crate alloc;

// Exported logging macro for graphics modules
#[macro_export]
macro_rules! log_info {
    ($($arg:tt)*) => {
        // TODO: Integrate with kernel logging system
        // For now, this is a placeholder
    };
}

/// Graphics error types
#[derive(Debug, Clone)]
pub enum GraphicsError {
    InvalidResolution,
    UnsupportedFormat,
    HardwareError,
    AIOptimizationFailed,
    MemoryAllocationFailed,
    InvalidParameters,
}

/// Color depth formats supported by the graphics system
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ColorFormat {
    RGB565,   // 16-bit color
    RGB888,   // 24-bit color
    RGBA8888, // 32-bit color with alpha
}

/// Screen resolution configuration
#[derive(Debug, Clone, Copy)]
pub struct Resolution {
    pub width: u32,
    pub height: u32,
    pub format: ColorFormat,
}

impl Resolution {
    pub fn new(width: u32, height: u32, format: ColorFormat) -> Self {
        Self { width, height, format }
    }
    
    pub fn bytes_per_pixel(&self) -> u32 {
        match self.format {
            ColorFormat::RGB565 => 2,
            ColorFormat::RGB888 => 3,
            ColorFormat::RGBA8888 => 4,
        }
    }
    
    pub fn buffer_size(&self) -> usize {
        (self.width * self.height * self.bytes_per_pixel()) as usize
    }
}

/// Basic color representation
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Color {
    pub r: u8,
    pub g: u8,
    pub b: u8,
    pub a: u8,
}

impl Color {
    pub const BLACK: Color = Color { r: 0, g: 0, b: 0, a: 255 };
    pub const WHITE: Color = Color { r: 255, g: 255, b: 255, a: 255 };
    pub const RED: Color = Color { r: 255, g: 0, b: 0, a: 255 };
    pub const GREEN: Color = Color { r: 0, g: 255, b: 0, a: 255 };
    pub const BLUE: Color = Color { r: 0, g: 0, b: 255, a: 255 };
    pub const CYAN: Color = Color { r: 0, g: 255, b: 255, a: 255 };
    pub const MAGENTA: Color = Color { r: 255, g: 0, b: 255, a: 255 };
    pub const YELLOW: Color = Color { r: 255, g: 255, b: 0, a: 255 };
    
    /// SynOS consciousness theme colors
    pub const CONSCIOUSNESS_BLUE: Color = Color { r: 0, g: 123, b: 255, a: 255 };
    pub const AI_GREEN: Color = Color { r: 40, g: 167, b: 69, a: 255 };
    pub const EDUCATION_ORANGE: Color = Color { r: 253, g: 126, b: 20, a: 255 };
    
    pub fn new(r: u8, g: u8, b: u8, a: u8) -> Self {
        Self { r, g, b, a }
    }
    
    pub fn to_rgb565(&self) -> u16 {
        let r = (self.r >> 3) as u16;
        let g = (self.g >> 2) as u16;
        let b = (self.b >> 3) as u16;
        (r << 11) | (g << 5) | b
    }
    
    pub fn to_rgb888(&self) -> u32 {
        ((self.r as u32) << 16) | ((self.g as u32) << 8) | (self.b as u32)
    }
    
    pub fn to_rgba8888(&self) -> u32 {
        ((self.a as u32) << 24) | ((self.r as u32) << 16) | ((self.g as u32) << 8) | (self.b as u32)
    }
}

/// Point in 2D space
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Point {
    pub x: i32,
    pub y: i32,
}

impl Point {
    pub fn new(x: i32, y: i32) -> Self {
        Self { x, y }
    }
}

/// Rectangle area
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Rect {
    pub x: i32,
    pub y: i32,
    pub width: u32,
    pub height: u32,
}

impl Rect {
    pub fn new(x: i32, y: i32, width: u32, height: u32) -> Self {
        Self { x, y, width, height }
    }
    
    pub fn contains(&self, point: Point) -> bool {
        point.x >= self.x 
            && point.x < self.x + self.width as i32
            && point.y >= self.y 
            && point.y < self.y + self.height as i32
    }
    
    pub fn intersects(&self, other: &Rect) -> bool {
        self.x < other.x + other.width as i32
            && self.x + self.width as i32 > other.x
            && self.y < other.y + other.height as i32
            && self.y + self.height as i32 > other.y
    }
}

/// AI-enhanced graphics optimization metrics
#[derive(Debug, Clone)]
pub struct GraphicsMetrics {
    pub frames_rendered: u64,
    pub average_frame_time: u64, // microseconds
    pub memory_usage: usize,     // bytes
    pub ai_optimizations_applied: u32,
    pub consciousness_level: f32, // 0.0 to 1.0
}

impl GraphicsMetrics {
    pub fn new() -> Self {
        Self {
            frames_rendered: 0,
            average_frame_time: 0,
            memory_usage: 0,
            ai_optimizations_applied: 0,
            consciousness_level: 0.0,
        }
    }
    
    pub fn update_consciousness(&mut self, level: f32) {
        self.consciousness_level = level.clamp(0.0, 1.0);
    }
    
    pub fn record_frame(&mut self, frame_time: u64) {
        self.frames_rendered += 1;
        
        // Calculate rolling average
        if self.frames_rendered == 1 {
            self.average_frame_time = frame_time;
        } else {
            self.average_frame_time = (self.average_frame_time * 9 + frame_time) / 10;
        }
    }
}

/// Graphics subsystem modules
pub mod framebuffer;
pub mod primitives;
pub mod drivers;
pub mod window_manager;

// Re-export commonly used types
pub use framebuffer::Framebuffer;
pub use primitives::GraphicsPrimitives;
pub use drivers::DisplayDriver;
pub use window_manager::{WindowManager, WindowId, Window, WindowCreateInfo};

/// Initialize the graphics subsystem with AI integration
pub fn initialize_graphics() -> Result<(), GraphicsError> {
    crate::log_info!("🎨 Initializing SynOS Graphics Framework");
    
    // Initialize display driver detection
    drivers::initialize_display_drivers()?;
    
    // Set up AI-enhanced graphics optimization
    setup_ai_graphics_optimization()?;
    
    crate::log_info!("✅ Graphics framework initialized successfully");
    Ok(())
}

/// Set up AI-enhanced graphics optimization
fn setup_ai_graphics_optimization() -> Result<(), GraphicsError> {
    // Initialize consciousness monitoring for graphics
    // This will be integrated with the main AI bridge
    
    crate::log_info!("🧠 Setting up AI graphics optimization");
    
    // Register graphics performance callbacks with AI system
    // TODO: Integrate with core/ai module
    
    Ok(())
}

/// Get current graphics performance metrics
pub fn get_graphics_metrics() -> GraphicsMetrics {
    // This would typically read from a global metrics collector
    GraphicsMetrics::new()
}

/// Educational graphics function for demonstrating concepts
pub fn demonstrate_graphics_concepts() {
    crate::log_info!("🎓 Graphics Educational Demo:");
    crate::log_info!("  - Framebuffer: Direct memory access to display");
    crate::log_info!("  - Color formats: RGB565, RGB888, RGBA8888");
    crate::log_info!("  - Primitives: Points, lines, rectangles, text");
    crate::log_info!("  - AI optimization: Consciousness-driven rendering");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_color_conversions() {
        let color = Color::new(255, 128, 64, 255);
        
        // Test RGB565 conversion
        let rgb565 = color.to_rgb565();
        assert!(rgb565 > 0);
        
        // Test RGB888 conversion
        let rgb888 = color.to_rgb888();
        assert_eq!(rgb888, 0xFF8040);
        
        // Test RGBA8888 conversion
        let rgba8888 = color.to_rgba8888();
        assert_eq!(rgba8888, 0xFFFF8040);
    }

    #[test]
    fn test_resolution() {
        let res = Resolution::new(1920, 1080, ColorFormat::RGBA8888);
        assert_eq!(res.bytes_per_pixel(), 4);
        assert_eq!(res.buffer_size(), 1920 * 1080 * 4);
    }

    #[test]
    fn test_rect_operations() {
        let rect1 = Rect::new(10, 10, 50, 50);
        let rect2 = Rect::new(30, 30, 50, 50);
        
        assert!(rect1.contains(Point::new(20, 20)));
        assert!(!rect1.contains(Point::new(70, 70)));
        assert!(rect1.intersects(&rect2));
    }
}
