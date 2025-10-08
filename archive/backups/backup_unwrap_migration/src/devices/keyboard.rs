use super::{DeviceDriver, DeviceError, DeviceFlags, DeviceInfo, DeviceResult, DeviceType};
/// Keyboard device driver for PS/2 keyboard input
/// Provides basic keyboard input functionality
use core::arch::asm;

/// PS/2 keyboard driver
pub struct KeyboardDriver {
    info: DeviceInfo,
    buffer: [u8; 256], // Circular buffer for key presses
    buffer_head: usize,
    buffer_tail: usize,
    buffer_count: usize,
    shift_pressed: bool,
    ctrl_pressed: bool,
    alt_pressed: bool,
    caps_lock: bool,
}

impl KeyboardDriver {
    /// Create a new keyboard driver
    pub fn new() -> Self {
        KeyboardDriver {
            info: DeviceInfo {
                id: 0, // Will be set by device manager
                name: "ps2_keyboard",
                device_type: DeviceType::CharacterDevice,
                vendor_id: 0x0000,
                device_id: 0x0002,
                version: 1,
                flags: DeviceFlags::READABLE,
            },
            buffer: [0; 256],
            buffer_head: 0,
            buffer_tail: 0,
            buffer_count: 0,
            shift_pressed: false,
            ctrl_pressed: false,
            alt_pressed: false,
            caps_lock: false,
        }
    }

    /// Handle keyboard interrupt (called from IRQ handler)
    pub fn handle_interrupt(&mut self) {
        let scancode = self.read_scancode();
        if let Some(key) = self.process_scancode(scancode) {
            self.add_to_buffer(key);
        }
    }

    /// Read scancode from keyboard controller
    fn read_scancode(&self) -> u8 {
        unsafe {
            // Read from PS/2 data port (0x60)
            let mut result: u8;
            asm!("in al, dx", out("al") result, in("dx") 0x60u16, options(nomem, nostack));
            result
        }
    }

    /// Process scancode and return ASCII character if available
    fn process_scancode(&mut self, scancode: u8) -> Option<u8> {
        // Handle special keys first
        match scancode {
            0x2A | 0x36 => {
                // Left/Right Shift pressed
                self.shift_pressed = true;
                return None;
            }
            0xAA | 0xB6 => {
                // Left/Right Shift released
                self.shift_pressed = false;
                return None;
            }
            0x1D => {
                // Ctrl pressed
                self.ctrl_pressed = true;
                return None;
            }
            0x9D => {
                // Ctrl released
                self.ctrl_pressed = false;
                return None;
            }
            0x38 => {
                // Alt pressed
                self.alt_pressed = true;
                return None;
            }
            0xB8 => {
                // Alt released
                self.alt_pressed = false;
                return None;
            }
            0x3A => {
                // Caps Lock
                self.caps_lock = !self.caps_lock;
                return None;
            }
            _ => {}
        }

        // Only process key press events (not releases)
        if scancode & 0x80 != 0 {
            return None;
        }

        // Convert scancode to ASCII
        self.scancode_to_ascii(scancode)
    }

    /// Convert scancode to ASCII character
    fn scancode_to_ascii(&self, scancode: u8) -> Option<u8> {
        let base_char = match scancode {
            0x02..=0x0B => b'1' + (scancode - 0x02), // 1-9, 0
            0x10 => b'q',
            0x11 => b'w',
            0x12 => b'e',
            0x13 => b'r',
            0x14 => b't',
            0x15 => b'y',
            0x16 => b'u',
            0x17 => b'i',
            0x18 => b'o',
            0x19 => b'p',
            0x1E => b'a',
            0x1F => b's',
            0x20 => b'd',
            0x21 => b'f',
            0x22 => b'g',
            0x23 => b'h',
            0x24 => b'j',
            0x25 => b'k',
            0x26 => b'l',
            0x2C => b'z',
            0x2D => b'x',
            0x2E => b'c',
            0x2F => b'v',
            0x30 => b'b',
            0x31 => b'n',
            0x32 => b'm',
            0x39 => b' ',    // Space
            0x1C => b'\n',   // Enter
            0x0E => b'\x08', // Backspace
            0x0F => b'\t',   // Tab
            0x01 => 0x1B,    // Escape
            _ => return None,
        };

        // Handle special number row characters with shift
        if self.shift_pressed {
            let shifted_char = match scancode {
                0x02 => b'!', // 1
                0x03 => b'@', // 2
                0x04 => b'#', // 3
                0x05 => b'$', // 4
                0x06 => b'%', // 5
                0x07 => b'^', // 6
                0x08 => b'&', // 7
                0x09 => b'*', // 8
                0x0A => b'(', // 9
                0x0B => b')', // 0
                0x0C => b'_', // -
                0x0D => b'+', // =
                0x1A => b'{', // [
                0x1B => b'}', // ]
                0x27 => b':', // ;
                0x28 => b'"', // '
                0x29 => b'~', // `
                0x2B => b'|', // \
                0x33 => b'<', // ,
                0x34 => b'>', // .
                0x35 => b'?', // /
                _ => {
                    // For letters, handle caps lock and shift
                    if base_char >= b'a' && base_char <= b'z' {
                        if self.caps_lock {
                            base_char // Shift cancels caps lock
                        } else {
                            base_char - 32 // Convert to uppercase
                        }
                    } else {
                        base_char
                    }
                }
            };
            Some(shifted_char)
        } else {
            // Handle caps lock for letters
            if base_char >= b'a' && base_char <= b'z' && self.caps_lock {
                Some(base_char - 32) // Convert to uppercase
            } else {
                Some(base_char)
            }
        }
    }

    /// Add character to input buffer
    fn add_to_buffer(&mut self, key: u8) {
        if self.buffer_count < self.buffer.len() {
            self.buffer[self.buffer_head] = key;
            self.buffer_head = (self.buffer_head + 1) % self.buffer.len();
            self.buffer_count += 1;
        }
    }

    /// Read character from buffer
    fn read_from_buffer(&mut self) -> Option<u8> {
        if self.buffer_count > 0 {
            let key = self.buffer[self.buffer_tail];
            self.buffer_tail = (self.buffer_tail + 1) % self.buffer.len();
            self.buffer_count -= 1;
            Some(key)
        } else {
            None
        }
    }

    /// Check if data is available
    pub fn data_available(&self) -> bool {
        self.buffer_count > 0
    }

    /// Get modifier key states
    pub fn modifier_states(&self) -> (bool, bool, bool, bool) {
        (
            self.shift_pressed,
            self.ctrl_pressed,
            self.alt_pressed,
            self.caps_lock,
        )
    }
}

impl DeviceDriver for KeyboardDriver {
    fn device_info(&self) -> DeviceInfo {
        self.info.clone()
    }

    fn init(&mut self) -> DeviceResult<()> {
        // Initialize PS/2 keyboard controller
        // This would normally involve setting up the keyboard controller
        // For now, we'll just clear our internal state
        self.buffer = [0; 256];
        self.buffer_head = 0;
        self.buffer_tail = 0;
        self.buffer_count = 0;
        self.shift_pressed = false;
        self.ctrl_pressed = false;
        self.alt_pressed = false;
        self.caps_lock = false;

        Ok(())
    }

    fn read(&mut self, buffer: &mut [u8]) -> DeviceResult<usize> {
        let mut bytes_read = 0;

        for i in 0..buffer.len() {
            if let Some(key) = self.read_from_buffer() {
                buffer[i] = key;
                bytes_read += 1;
            } else {
                break;
            }
        }

        Ok(bytes_read)
    }

    fn write(&mut self, _buffer: &[u8]) -> DeviceResult<usize> {
        // Keyboard is read-only
        Err(DeviceError::InvalidOperation)
    }

    fn ioctl(&mut self, cmd: u32, _arg: usize) -> DeviceResult<usize> {
        match cmd {
            0x01 => {
                // Check data available
                Ok(if self.data_available() { 1 } else { 0 })
            }
            0x02 => {
                // Get modifier states
                let (shift, ctrl, alt, caps) = self.modifier_states();
                let state = (caps as usize) << 3
                    | (alt as usize) << 2
                    | (ctrl as usize) << 1
                    | (shift as usize);
                Ok(state)
            }
            0x03 => {
                // Clear buffer
                self.buffer_count = 0;
                self.buffer_head = 0;
                self.buffer_tail = 0;
                Ok(0)
            }
            _ => Err(DeviceError::InvalidOperation),
        }
    }

    fn cleanup(&mut self) -> DeviceResult<()> {
        // Clear buffer and reset state
        self.buffer_count = 0;
        self.buffer_head = 0;
        self.buffer_tail = 0;
        Ok(())
    }
}

/// Keyboard commands for ioctl
pub mod keyboard_commands {
    pub const DATA_AVAILABLE: u32 = 0x01;
    pub const GET_MODIFIERS: u32 = 0x02;
    pub const CLEAR_BUFFER: u32 = 0x03;
}

/// Modifier key bit flags
pub mod modifier_flags {
    pub const SHIFT: usize = 0x01;
    pub const CTRL: usize = 0x02;
    pub const ALT: usize = 0x04;
    pub const CAPS_LOCK: usize = 0x08;
}
