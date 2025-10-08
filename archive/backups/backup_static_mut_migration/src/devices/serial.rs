use super::{DeviceDriver, DeviceError, DeviceFlags, DeviceInfo, DeviceResult, DeviceType};
/// Serial device driver for UART communication
/// Provides basic serial port functionality
use core::arch::asm;

/// Serial port driver for UART communication
pub struct SerialDriver {
    info: DeviceInfo,
    base_port: u16,
    baud_rate: u32,
    initialized: bool,
}

impl SerialDriver {
    /// Create a new serial driver for COM1 (default)
    pub fn new() -> Self {
        SerialDriver::new_with_port(0x3F8) // COM1
    }

    /// Create a new serial driver with specific port
    pub fn new_with_port(base_port: u16) -> Self {
        SerialDriver {
            info: DeviceInfo {
                id: 0, // Will be set by device manager
                name: "uart_serial",
                device_type: DeviceType::CharacterDevice,
                vendor_id: 0x0000,
                device_id: 0x0003,
                version: 1,
                flags: DeviceFlags::READABLE | DeviceFlags::WRITABLE,
            },
            base_port,
            baud_rate: 115200,
            initialized: false,
        }
    }

    /// Initialize the serial port with specified baud rate
    fn init_port(&mut self, baud_rate: u32) -> DeviceResult<()> {
        // Calculate divisor for baud rate
        let divisor = (115200 / baud_rate) as u16;

        unsafe {
            // Disable interrupts
            self.outb(self.base_port + 1, 0x00);

            // Enable DLAB (set baud rate divisor)
            self.outb(self.base_port + 3, 0x80);

            // Set divisor (low byte)
            self.outb(self.base_port + 0, (divisor & 0xFF) as u8);

            // Set divisor (high byte)
            self.outb(self.base_port + 1, (divisor >> 8) as u8);

            // 8 bits, no parity, one stop bit
            self.outb(self.base_port + 3, 0x03);

            // Enable FIFO, clear them, with 14-byte threshold
            self.outb(self.base_port + 2, 0xC7);

            // IRQs enabled, RTS/DSR set
            self.outb(self.base_port + 4, 0x0B);

            // Set in loopback mode, test the serial chip
            self.outb(self.base_port + 4, 0x1E);

            // Test serial chip (send byte 0xAE and check if we get the same byte back)
            self.outb(self.base_port + 0, 0xAE);

            // Check if serial is faulty (i.e: not same byte as sent)
            if self.inb(self.base_port + 0) != 0xAE {
                return Err(DeviceError::HardwareError);
            }

            // If serial is not faulty set it in normal operation mode
            // (not-loopback with IRQs enabled and OUT#1 and OUT#2 bits enabled)
            self.outb(self.base_port + 4, 0x0F);
        }

        self.baud_rate = baud_rate;
        self.initialized = true;
        Ok(())
    }

    /// Read byte from port
    unsafe fn inb(&self, port: u16) -> u8 {
        let mut result: u8;
        asm!("in al, dx", out("al") result, in("dx") port, options(nomem, nostack));
        result
    }

    /// Write byte to port
    unsafe fn outb(&self, port: u16, value: u8) {
        asm!("out dx, al", in("dx") port, in("al") value, options(nomem, nostack));
    }

    /// Check if transmit buffer is empty
    fn is_transmit_empty(&self) -> bool {
        unsafe { self.inb(self.base_port + 5) & 0x20 != 0 }
    }

    /// Check if data is available to read
    fn data_available(&self) -> bool {
        unsafe { self.inb(self.base_port + 5) & 0x01 != 0 }
    }

    /// Send a single byte
    fn send_byte(&self, byte: u8) -> DeviceResult<()> {
        if !self.initialized {
            return Err(DeviceError::NotInitialized);
        }

        // Wait for transmit buffer to be empty
        let mut timeout = 1000;
        while !self.is_transmit_empty() && timeout > 0 {
            timeout -= 1;
        }

        if timeout == 0 {
            return Err(DeviceError::Timeout);
        }

        unsafe {
            self.outb(self.base_port, byte);
        }

        Ok(())
    }

    /// Receive a single byte
    fn receive_byte(&self) -> DeviceResult<u8> {
        if !self.initialized {
            return Err(DeviceError::NotInitialized);
        }

        if !self.data_available() {
            return Err(DeviceError::WouldBlock);
        }

        unsafe { Ok(self.inb(self.base_port)) }
    }

    /// Send a string
    pub fn send_string(&self, s: &str) -> DeviceResult<()> {
        for byte in s.bytes() {
            self.send_byte(byte)?;
        }
        Ok(())
    }

    /// Get current baud rate
    pub fn baud_rate(&self) -> u32 {
        self.baud_rate
    }

    /// Set new baud rate
    pub fn set_baud_rate(&mut self, baud_rate: u32) -> DeviceResult<()> {
        self.init_port(baud_rate)
    }

    /// Get base port address
    pub fn base_port(&self) -> u16 {
        self.base_port
    }
}

impl DeviceDriver for SerialDriver {
    fn device_info(&self) -> DeviceInfo {
        self.info.clone()
    }

    fn init(&mut self) -> DeviceResult<()> {
        self.init_port(self.baud_rate)
    }

    fn read(&mut self, buffer: &mut [u8]) -> DeviceResult<usize> {
        let mut bytes_read = 0;

        for i in 0..buffer.len() {
            match self.receive_byte() {
                Ok(byte) => {
                    buffer[i] = byte;
                    bytes_read += 1;
                }
                Err(DeviceError::WouldBlock) => break,
                Err(e) => return Err(e),
            }
        }

        Ok(bytes_read)
    }

    fn write(&mut self, buffer: &[u8]) -> DeviceResult<usize> {
        for &byte in buffer {
            self.send_byte(byte)?;
        }
        Ok(buffer.len())
    }

    fn ioctl(&mut self, cmd: u32, arg: usize) -> DeviceResult<usize> {
        match cmd {
            0x01 => {
                // Set baud rate
                let baud_rate = arg as u32;
                self.set_baud_rate(baud_rate)?;
                Ok(0)
            }
            0x02 => {
                // Get baud rate
                Ok(self.baud_rate() as usize)
            }
            0x03 => {
                // Check data available
                Ok(if self.data_available() { 1 } else { 0 })
            }
            0x04 => {
                // Check transmit ready
                Ok(if self.is_transmit_empty() { 1 } else { 0 })
            }
            0x05 => {
                // Get base port
                Ok(self.base_port() as usize)
            }
            _ => Err(DeviceError::InvalidOperation),
        }
    }

    fn cleanup(&mut self) -> DeviceResult<()> {
        if self.initialized {
            unsafe {
                // Disable interrupts
                self.outb(self.base_port + 1, 0x00);
                // Reset to safe state
                self.outb(self.base_port + 4, 0x00);
            }
            self.initialized = false;
        }
        Ok(())
    }
}

/// Serial commands for ioctl
pub mod serial_commands {
    pub const SET_BAUD_RATE: u32 = 0x01;
    pub const GET_BAUD_RATE: u32 = 0x02;
    pub const DATA_AVAILABLE: u32 = 0x03;
    pub const TRANSMIT_READY: u32 = 0x04;
    pub const GET_BASE_PORT: u32 = 0x05;
}

/// Common baud rates
pub mod baud_rates {
    pub const BAUD_9600: u32 = 9600;
    pub const BAUD_19200: u32 = 19200;
    pub const BAUD_38400: u32 = 38400;
    pub const BAUD_57600: u32 = 57600;
    pub const BAUD_115200: u32 = 115200;
}

/// Serial port addresses
pub mod serial_ports {
    pub const COM1: u16 = 0x3F8;
    pub const COM2: u16 = 0x2F8;
    pub const COM3: u16 = 0x3E8;
    pub const COM4: u16 = 0x2E8;
}
