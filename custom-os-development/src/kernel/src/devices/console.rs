/// Console device driver for text output
/// Provides basic text console functionality

use super::{DeviceDriver, DeviceInfo, DeviceType, DeviceFlags, DeviceResult, DeviceError};

/// VGA text mode console driver
pub struct ConsoleDriver {
    info: DeviceInfo,
    buffer: *mut u8,
    width: usize,
    height: usize,
    cursor_x: usize,
    cursor_y: usize,
    color: u8,
}

impl ConsoleDriver {
    /// Create a new console driver for VGA text mode
    pub fn new() -> Self {
        ConsoleDriver {
            info: DeviceInfo {
                id: 0, // Will be set by device manager
                name: "vga_console",
                device_type: DeviceType::CharacterDevice,
                vendor_id: 0x0000,
                device_id: 0x0001,
                version: 1,
                flags: DeviceFlags::WRITABLE,
            },
            buffer: 0xb8000 as *mut u8, // VGA text buffer
            width: 80,
            height: 25,
            cursor_x: 0,
            cursor_y: 0,
            color: 0x07, // Light gray on black
        }
    }
    
    /// Clear the screen
    pub fn clear(&mut self) {
        for y in 0..self.height {
            for x in 0..self.width {
                self.write_char_at(x, y, b' ', self.color);
            }
        }
        self.cursor_x = 0;
        self.cursor_y = 0;
    }
    
    /// Write a character at specific position
    fn write_char_at(&mut self, x: usize, y: usize, ch: u8, color: u8) {
        if x < self.width && y < self.height {
            let offset = (y * self.width + x) * 2;
            unsafe {
                *self.buffer.add(offset) = ch;
                *self.buffer.add(offset + 1) = color;
            }
        }
    }
    
    /// Write a character at current cursor position
    fn write_char(&mut self, ch: u8) {
        match ch {
            b'\n' => {
                self.cursor_x = 0;
                self.cursor_y += 1;
            }
            b'\r' => {
                self.cursor_x = 0;
            }
            b'\t' => {
                self.cursor_x = (self.cursor_x + 8) & !7; // Align to 8
            }
            ch => {
                self.write_char_at(self.cursor_x, self.cursor_y, ch, self.color);
                self.cursor_x += 1;
            }
        }
        
        // Handle line wrapping
        if self.cursor_x >= self.width {
            self.cursor_x = 0;
            self.cursor_y += 1;
        }
        
        // Handle scrolling
        if self.cursor_y >= self.height {
            self.scroll_up();
            self.cursor_y = self.height - 1;
        }
    }
    
    /// Scroll the screen up by one line
    fn scroll_up(&mut self) {
        // Move all lines up by one
        for y in 1..self.height {
            for x in 0..self.width {
                let src_offset = (y * self.width + x) * 2;
                let dst_offset = ((y - 1) * self.width + x) * 2;
                unsafe {
                    let ch = *self.buffer.add(src_offset);
                    let color = *self.buffer.add(src_offset + 1);
                    *self.buffer.add(dst_offset) = ch;
                    *self.buffer.add(dst_offset + 1) = color;
                }
            }
        }
        
        // Clear the bottom line
        for x in 0..self.width {
            self.write_char_at(x, self.height - 1, b' ', self.color);
        }
    }
    
    /// Set text color
    pub fn set_color(&mut self, foreground: u8, background: u8) {
        self.color = (background << 4) | (foreground & 0x0f);
    }
    
    /// Get cursor position
    pub fn cursor_position(&self) -> (usize, usize) {
        (self.cursor_x, self.cursor_y)
    }
    
    /// Set cursor position
    pub fn set_cursor_position(&mut self, x: usize, y: usize) {
        if x < self.width && y < self.height {
            self.cursor_x = x;
            self.cursor_y = y;
        }
    }
}

impl DeviceDriver for ConsoleDriver {
    fn device_info(&self) -> DeviceInfo {
        self.info.clone()
    }
    
    fn init(&mut self) -> DeviceResult<()> {
        // Clear screen on initialization
        self.clear();
        Ok(())
    }
    
    fn read(&mut self, _buffer: &mut [u8]) -> DeviceResult<usize> {
        // Console is write-only
        Err(DeviceError::InvalidOperation)
    }
    
    fn write(&mut self, buffer: &[u8]) -> DeviceResult<usize> {
        for &byte in buffer {
            self.write_char(byte);
        }
        Ok(buffer.len())
    }
    
    fn ioctl(&mut self, cmd: u32, arg: usize) -> DeviceResult<usize> {
        match cmd {
            0x01 => { // Clear screen
                self.clear();
                Ok(0)
            }
            0x02 => { // Set color
                let foreground = (arg & 0xff) as u8;
                let background = ((arg >> 8) & 0xff) as u8;
                self.set_color(foreground, background);
                Ok(0)
            }
            0x03 => { // Set cursor position
                let x = arg & 0xffff;
                let y = (arg >> 16) & 0xffff;
                self.set_cursor_position(x, y);
                Ok(0)
            }
            0x04 => { // Get cursor position
                let (x, y) = self.cursor_position();
                Ok(y << 16 | x)
            }
            _ => Err(DeviceError::InvalidOperation)
        }
    }
    
    fn cleanup(&mut self) -> DeviceResult<()> {
        // Nothing to cleanup for VGA console
        Ok(())
    }
}

/// Console commands for ioctl
pub mod console_commands {
    pub const CLEAR_SCREEN: u32 = 0x01;
    pub const SET_COLOR: u32 = 0x02;
    pub const SET_CURSOR: u32 = 0x03;
    pub const GET_CURSOR: u32 = 0x04;
}

/// VGA color constants
pub mod vga_colors {
    pub const BLACK: u8 = 0;
    pub const BLUE: u8 = 1;
    pub const GREEN: u8 = 2;
    pub const CYAN: u8 = 3;
    pub const RED: u8 = 4;
    pub const MAGENTA: u8 = 5;
    pub const BROWN: u8 = 6;
    pub const LIGHT_GRAY: u8 = 7;
    pub const DARK_GRAY: u8 = 8;
    pub const LIGHT_BLUE: u8 = 9;
    pub const LIGHT_GREEN: u8 = 10;
    pub const LIGHT_CYAN: u8 = 11;
    pub const LIGHT_RED: u8 = 12;
    pub const LIGHT_MAGENTA: u8 = 13;
    pub const YELLOW: u8 = 14;
    pub const WHITE: u8 = 15;
}
