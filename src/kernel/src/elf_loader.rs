/// ELF Binary Loader for SynOS Userspace Programs
/// Implements complete ELF64 parsing and loading with virtual memory setup

use alloc::vec::Vec;
use alloc::string::String;
use core::mem;

/// ELF64 Header structure
#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct Elf64Header {
    pub e_ident: [u8; 16],      // ELF identification
    pub e_type: u16,            // Object file type
    pub e_machine: u16,         // Machine type
    pub e_version: u32,         // Object file version
    pub e_entry: u64,           // Entry point address
    pub e_phoff: u64,           // Program header offset
    pub e_shoff: u64,           // Section header offset
    pub e_flags: u32,           // Processor-specific flags
    pub e_ehsize: u16,          // ELF header size
    pub e_phentsize: u16,       // Program header entry size
    pub e_phnum: u16,           // Number of program header entries
    pub e_shentsize: u16,       // Section header entry size
    pub e_shnum: u16,           // Number of section header entries
    pub e_shstrndx: u16,        // Section name string table index
}

/// ELF64 Program Header
#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct Elf64ProgramHeader {
    pub p_type: u32,            // Segment type
    pub p_flags: u32,           // Segment flags
    pub p_offset: u64,          // Segment file offset
    pub p_vaddr: u64,           // Segment virtual address
    pub p_paddr: u64,           // Segment physical address
    pub p_filesz: u64,          // Segment size in file
    pub p_memsz: u64,           // Segment size in memory
    pub p_align: u64,           // Segment alignment
}

/// Program header types
const PT_NULL: u32 = 0;
const PT_LOAD: u32 = 1;
const PT_DYNAMIC: u32 = 2;
const PT_INTERP: u32 = 3;
const PT_NOTE: u32 = 4;
const PT_SHLIB: u32 = 5;
const PT_PHDR: u32 = 6;
const PT_TLS: u32 = 7;

/// Segment flags
const PF_X: u32 = 1;  // Execute
const PF_W: u32 = 2;  // Write
const PF_R: u32 = 4;  // Read

/// ELF magic number
const ELF_MAGIC: [u8; 4] = [0x7f, b'E', b'L', b'F'];

/// ELF class
const ELFCLASS64: u8 = 2;

/// ELF data encoding
const ELFDATA2LSB: u8 = 1;  // Little endian

/// ELF machine types
const EM_X86_64: u16 = 62;

/// Memory protection flags (converted from ELF flags)
#[derive(Debug, Clone, Copy)]
pub struct MemoryProtection {
    pub read: bool,
    pub write: bool,
    pub execute: bool,
}

impl MemoryProtection {
    pub fn from_elf_flags(flags: u32) -> Self {
        Self {
            read: (flags & PF_R) != 0,
            write: (flags & PF_W) != 0,
            execute: (flags & PF_X) != 0,
        }
    }

    pub fn to_flags(&self) -> u32 {
        let mut flags = 0;
        if self.read { flags |= PF_R; }
        if self.write { flags |= PF_W; }
        if self.execute { flags |= PF_X; }
        flags
    }
}

/// Loaded segment information
#[derive(Debug, Clone)]
pub struct LoadedSegment {
    pub virt_addr: u64,
    pub size: u64,
    pub protection: MemoryProtection,
    pub data: Vec<u8>,
}

/// ELF loader result
pub struct ElfLoadResult {
    pub entry_point: u64,
    pub segments: Vec<LoadedSegment>,
    pub stack_addr: u64,
    pub heap_addr: u64,
}

/// ELF Loader errors
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ElfError {
    InvalidMagic,
    InvalidClass,
    InvalidEncoding,
    InvalidMachine,
    InvalidHeaderSize,
    InvalidProgramHeader,
    TooSmall,
    UnsupportedType,
    NoLoadableSegments,
    SegmentTooLarge,
}

pub type ElfResult<T> = Result<T, ElfError>;

/// ELF Loader
pub struct ElfLoader {
    data: Vec<u8>,
}

impl ElfLoader {
    /// Create a new ELF loader
    pub fn new(data: Vec<u8>) -> Self {
        Self { data }
    }

    /// Parse and validate ELF header
    pub fn parse_header(&self) -> ElfResult<Elf64Header> {
        if self.data.len() < mem::size_of::<Elf64Header>() {
            return Err(ElfError::TooSmall);
        }

        let header = unsafe {
            core::ptr::read(self.data.as_ptr() as *const Elf64Header)
        };

        // Validate magic number
        if &header.e_ident[0..4] != &ELF_MAGIC {
            return Err(ElfError::InvalidMagic);
        }

        // Validate class (64-bit)
        if header.e_ident[4] != ELFCLASS64 {
            return Err(ElfError::InvalidClass);
        }

        // Validate encoding (little endian)
        if header.e_ident[5] != ELFDATA2LSB {
            return Err(ElfError::InvalidEncoding);
        }

        // Validate machine type (x86-64)
        if header.e_machine != EM_X86_64 {
            return Err(ElfError::InvalidMachine);
        }

        // Validate header size
        if header.e_ehsize != mem::size_of::<Elf64Header>() as u16 {
            return Err(ElfError::InvalidHeaderSize);
        }

        Ok(header)
    }

    /// Parse program headers
    pub fn parse_program_headers(&self, header: &Elf64Header) -> ElfResult<Vec<Elf64ProgramHeader>> {
        let mut program_headers = Vec::new();

        for i in 0..header.e_phnum {
            let offset = header.e_phoff + (i as u64 * header.e_phentsize as u64);

            if offset as usize + mem::size_of::<Elf64ProgramHeader>() > self.data.len() {
                return Err(ElfError::InvalidProgramHeader);
            }

            let ph = unsafe {
                core::ptr::read(self.data.as_ptr().add(offset as usize) as *const Elf64ProgramHeader)
            };

            program_headers.push(ph);
        }

        Ok(program_headers)
    }

    /// Load ELF binary into memory
    pub fn load(&self) -> ElfResult<ElfLoadResult> {
        // Parse header
        let header = self.parse_header()?;

        // Parse program headers
        let program_headers = self.parse_program_headers(&header)?;

        // Load segments
        let mut segments = Vec::new();
        let mut has_loadable = false;

        for ph in program_headers {
            if ph.p_type == PT_LOAD {
                has_loadable = true;

                // Validate segment
                if ph.p_filesz > ph.p_memsz {
                    return Err(ElfError::SegmentTooLarge);
                }

                if ph.p_offset as usize + ph.p_filesz as usize > self.data.len() {
                    return Err(ElfError::SegmentTooLarge);
                }

                // Create segment data
                let mut segment_data = vec![0u8; ph.p_memsz as usize];

                // Copy file data
                segment_data[..ph.p_filesz as usize].copy_from_slice(
                    &self.data[ph.p_offset as usize..(ph.p_offset + ph.p_filesz) as usize]
                );

                // Zero-fill BSS (p_memsz > p_filesz)
                // Already done by vec initialization

                segments.push(LoadedSegment {
                    virt_addr: ph.p_vaddr,
                    size: ph.p_memsz,
                    protection: MemoryProtection::from_elf_flags(ph.p_flags),
                    data: segment_data,
                });
            }
        }

        if !has_loadable {
            return Err(ElfError::NoLoadableSegments);
        }

        // Calculate stack and heap addresses
        // Stack grows down from high address
        let stack_addr = 0x7fff_ffff_f000;
        // Heap starts after last segment
        let heap_addr = segments.iter()
            .map(|s| s.virt_addr + s.size)
            .max()
            .unwrap_or(0x600000);

        Ok(ElfLoadResult {
            entry_point: header.e_entry,
            segments,
            stack_addr,
            heap_addr,
        })
    }
}

/// Process memory layout manager
pub struct ProcessMemoryLayout {
    pub entry_point: u64,
    pub stack_top: u64,
    pub stack_bottom: u64,
    pub heap_start: u64,
    pub heap_end: u64,
    pub segments: Vec<LoadedSegment>,
}

impl ProcessMemoryLayout {
    /// Create process memory layout from ELF
    pub fn from_elf(elf_data: &[u8]) -> ElfResult<Self> {
        let loader = ElfLoader::new(elf_data.to_vec());
        let result = loader.load()?;

        Ok(Self {
            entry_point: result.entry_point,
            stack_top: result.stack_addr,
            stack_bottom: result.stack_addr - 0x100000, // 1MB stack
            heap_start: result.heap_addr,
            heap_end: result.heap_addr,
            segments: result.segments,
        })
    }

    /// Get total memory size
    pub fn total_size(&self) -> u64 {
        let segments_size: u64 = self.segments.iter().map(|s| s.size).sum();
        let stack_size = self.stack_top - self.stack_bottom;
        segments_size + stack_size
    }

    /// Check if address is in valid range
    pub fn is_valid_address(&self, addr: u64) -> bool {
        // Check segments
        for segment in &self.segments {
            if addr >= segment.virt_addr && addr < segment.virt_addr + segment.size {
                return true;
            }
        }

        // Check stack
        if addr >= self.stack_bottom && addr <= self.stack_top {
            return true;
        }

        // Check heap
        if addr >= self.heap_start && addr < self.heap_end {
            return true;
        }

        false
    }

    /// Get protection for address
    pub fn get_protection(&self, addr: u64) -> Option<MemoryProtection> {
        for segment in &self.segments {
            if addr >= segment.virt_addr && addr < segment.virt_addr + segment.size {
                return Some(segment.protection);
            }
        }

        // Stack is read-write
        if addr >= self.stack_bottom && addr <= self.stack_top {
            return Some(MemoryProtection {
                read: true,
                write: true,
                execute: false,
            });
        }

        // Heap is read-write
        if addr >= self.heap_start && addr < self.heap_end {
            return Some(MemoryProtection {
                read: true,
                write: true,
                execute: false,
            });
        }

        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_elf_magic_validation() {
        let mut data = vec![0u8; 64];
        data[0..4].copy_from_slice(&ELF_MAGIC);
        data[4] = ELFCLASS64;
        data[5] = ELFDATA2LSB;

        let loader = ElfLoader::new(data);
        let header = loader.parse_header();
        assert!(header.is_ok() || matches!(header, Err(ElfError::InvalidMachine)));
    }

    #[test]
    fn test_invalid_magic() {
        let data = vec![0u8; 64];
        let loader = ElfLoader::new(data);
        assert_eq!(loader.parse_header(), Err(ElfError::InvalidMagic));
    }

    #[test]
    fn test_memory_protection() {
        let prot = MemoryProtection::from_elf_flags(PF_R | PF_X);
        assert!(prot.read);
        assert!(!prot.write);
        assert!(prot.execute);
    }
}
