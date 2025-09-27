// SynFS - Native File System for SynOS
// A simple but efficient file system designed for modern storage

use crate::fs::vfs::{FileSystem, FsError, OpenFlags, Permissions, FileStats, FileType, DirectoryEntry, FileHandle};
use crate::drivers::{BlockDevice, DriverError};
use alloc::collections::BTreeMap;
use alloc::vec::Vec;
use alloc::vec;
use alloc::string::{String, ToString};
use alloc::sync::Arc;
use spin::Mutex;
use core::mem;

/// SynFS magic number
const SYNFS_MAGIC: u32 = 0x53594E46; // "SYNF"

/// SynFS version
const SYNFS_VERSION: u32 = 1;

/// Block size (4KB)
const BLOCK_SIZE: u32 = 4096;

/// Direct block pointers per inode
const DIRECT_BLOCKS: usize = 12;

/// Maximum filename length
const MAX_FILENAME_LEN: usize = 255;

/// Superblock structure
#[repr(C, packed)]
#[derive(Debug, Clone, Copy)]
pub struct SuperBlock {
    /// Magic number for identification
    pub magic: u32,
    
    /// File system version
    pub version: u32,
    
    /// Block size in bytes
    pub block_size: u32,
    
    /// Total blocks on device
    pub total_blocks: u64,
    
    /// Free blocks available
    pub free_blocks: u64,
    
    /// Total inodes
    pub total_inodes: u64,
    
    /// Free inodes available
    pub free_inodes: u64,
    
    /// Root directory inode number
    pub root_inode: u64,
    
    /// First data block
    pub first_data_block: u64,
    
    /// Inode table start block
    pub inode_table_start: u64,
    
    /// Block bitmap start block
    pub block_bitmap_start: u64,
    
    /// Inode bitmap start block
    pub inode_bitmap_start: u64,
    
    /// Creation timestamp
    pub created: u64,
    
    /// Last mount timestamp
    pub last_mount: u64,
    
    /// Mount count
    pub mount_count: u32,
    
    /// Clean flag (1 = clean, 0 = dirty)
    pub clean: u32,
}

impl SuperBlock {
    pub fn new(total_blocks: u64) -> Self {
        let total_inodes = total_blocks / 8; // Reasonable ratio
        
        Self {
            magic: SYNFS_MAGIC,
            version: SYNFS_VERSION,
            block_size: BLOCK_SIZE,
            total_blocks,
            free_blocks: total_blocks - 10, // Reserve some blocks for metadata
            total_inodes,
            free_inodes: total_inodes - 1, // Root inode is used
            root_inode: 1,
            first_data_block: 10, // First 10 blocks for metadata
            inode_table_start: 2,
            block_bitmap_start: 1,
            inode_bitmap_start: 1,
            created: 0, // TODO: Get actual timestamp
            last_mount: 0,
            mount_count: 0,
            clean: 1,
        }
    }
}

/// Inode structure
#[repr(C, packed)]
#[derive(Debug, Clone, Copy)]
pub struct Inode {
    /// Inode number
    pub number: u64,
    
    /// File type and permissions
    pub mode: u32,
    
    /// User ID
    pub uid: u32,
    
    /// Group ID
    pub gid: u32,
    
    /// File size in bytes
    pub size: u64,
    
    /// Creation time
    pub created: u64,
    
    /// Last modification time
    pub modified: u64,
    
    /// Last access time
    pub accessed: u64,
    
    /// Number of hard links
    pub links: u32,
    
    /// Number of 512-byte blocks allocated
    pub blocks: u32,
    
    /// Direct block pointers
    pub direct: [u64; DIRECT_BLOCKS],
    
    /// Single indirect block pointer
    pub indirect: u64,
    
    /// Double indirect block pointer
    pub double_indirect: u64,
    
    /// Triple indirect block pointer
    pub triple_indirect: u64,
}

impl Inode {
    pub fn new(number: u64, file_type: FileType, permissions: Permissions) -> Self {
        let mode = Self::make_mode(file_type, permissions);
        
        Self {
            number,
            mode,
            uid: 0,
            gid: 0,
            size: 0,
            created: 0, // TODO: Get actual timestamp
            modified: 0,
            accessed: 0,
            links: 1,
            blocks: 0,
            direct: [0; DIRECT_BLOCKS],
            indirect: 0,
            double_indirect: 0,
            triple_indirect: 0,
        }
    }
    
    fn make_mode(file_type: FileType, permissions: Permissions) -> u32 {
        let type_bits = match file_type {
            FileType::RegularFile => 0o100000,
            FileType::Directory => 0o040000,
            FileType::SymbolicLink => 0o120000,
            FileType::BlockDevice => 0o060000,
            FileType::CharacterDevice => 0o020000,
            FileType::Fifo => 0o010000,
            FileType::Socket => 0o140000,
        };
        
        type_bits | permissions.to_mode() as u32
    }
    
    pub fn file_type(&self) -> FileType {
        match self.mode & 0o170000 {
            0o040000 => FileType::Directory,
            0o120000 => FileType::SymbolicLink,
            0o060000 => FileType::BlockDevice,
            0o020000 => FileType::CharacterDevice,
            0o010000 => FileType::Fifo,
            0o140000 => FileType::Socket,
            _ => FileType::RegularFile,
        }
    }
    
    pub fn permissions(&self) -> Permissions {
        Permissions::new((self.mode & 0o777) as u16)
    }
}

/// Directory entry structure
#[repr(C, packed)]
#[derive(Debug, Clone, Copy)]
pub struct DirEntry {
    /// Inode number
    pub inode: u64,
    
    /// Entry length in bytes
    pub length: u16,
    
    /// Filename length
    pub name_len: u8,
    
    /// File type
    pub file_type: u8,
    
    // Filename follows this structure
}

/// SynFS implementation
pub struct SynFS {
    /// File system name
    name: String,
    
    /// Block device
    device: Option<Arc<Mutex<dyn BlockDevice>>>,
    
    /// Superblock
    superblock: SuperBlock,
    
    /// Open files
    open_files: BTreeMap<FileHandle, OpenFile>,
    
    /// Next file handle
    next_handle: u64,
    
    /// Inode cache
    inode_cache: BTreeMap<u64, Inode>,
    
    /// Block cache
    block_cache: BTreeMap<u64, Vec<u8>>,
    
    /// Dirty blocks
    dirty_blocks: BTreeMap<u64, Vec<u8>>,
}

/// Open file structure
#[derive(Debug, Clone)]
struct OpenFile {
    inode_number: u64,
    flags: OpenFlags,
    position: u64,
}

impl SynFS {
    /// Create a new SynFS instance
    pub fn new() -> Self {
        Self {
            name: "synfs".to_string(),
            device: None,
            superblock: SuperBlock::new(0),
            open_files: BTreeMap::new(),
            next_handle: 1,
            inode_cache: BTreeMap::new(),
            block_cache: BTreeMap::new(),
            dirty_blocks: BTreeMap::new(),
        }
    }
    
    /// Format a device with SynFS
    pub fn format(device: Arc<Mutex<dyn BlockDevice>>) -> Result<(), FsError> {
        let (total_blocks, block_size) = {
            let dev = device.lock();
            (dev.block_count(), dev.block_size())
        };
        
        if block_size != BLOCK_SIZE {
            return Err(FsError::NotSupported);
        }
        
        let superblock = SuperBlock::new(total_blocks);
        
        // Write superblock
        let sb_bytes = unsafe {
            core::slice::from_raw_parts(
                &superblock as *const SuperBlock as *const u8,
                mem::size_of::<SuperBlock>()
            )
        };
        
        let mut block_buffer = vec![0u8; BLOCK_SIZE as usize];
        block_buffer[..sb_bytes.len()].copy_from_slice(sb_bytes);
        
        {
            let mut dev = device.lock();
            dev.write_blocks(0, 1, &block_buffer)
                .map_err(|_| FsError::IoError)?;
        }
        
        // Create root directory inode
        let mut root_inode = Inode::new(1, FileType::Directory, Permissions::new(0o755));
        root_inode.size = BLOCK_SIZE as u64; // Directory has one block
        root_inode.direct[0] = superblock.first_data_block;
        
        // Write root inode (simplified - would normally go in inode table)
        let inode_bytes = unsafe {
            core::slice::from_raw_parts(
                &root_inode as *const Inode as *const u8,
                mem::size_of::<Inode>()
            )
        };
        
        block_buffer.fill(0);
        block_buffer[..inode_bytes.len()].copy_from_slice(inode_bytes);
        
        {
            let mut dev = device.lock();
            dev.write_blocks(superblock.inode_table_start, 1, &block_buffer)
                .map_err(|_| FsError::IoError)?;
        }
        
        // Create empty root directory
        block_buffer.fill(0);
        {
            let mut dev = device.lock();
            dev.write_blocks(superblock.first_data_block, 1, &block_buffer)
                .map_err(|_| FsError::IoError)?;
            dev.flush().map_err(|_| FsError::IoError)?;
        }
        
        crate::println!("[SynFS] Formatted device with {} blocks", total_blocks);
        Ok(())
    }
    
    /// Read a block from the device
    fn read_block(&mut self, block_num: u64) -> Result<Vec<u8>, FsError> {
        // Check cache first
        if let Some(block) = self.block_cache.get(&block_num) {
            return Ok(block.clone());
        }
        
        // Read from device
        if let Some(device) = &self.device {
            let mut buffer = vec![0u8; BLOCK_SIZE as usize];
            {
                let mut dev = device.lock();
                dev.read_blocks(block_num, 1, &mut buffer)
                    .map_err(|_| FsError::IoError)?;
            }
            
            // Cache the block
            self.block_cache.insert(block_num, buffer.clone());
            Ok(buffer)
        } else {
            Err(FsError::IoError)
        }
    }
    
    /// Write a block to the device
    fn write_block(&mut self, block_num: u64, data: &[u8]) -> Result<(), FsError> {
        if data.len() != BLOCK_SIZE as usize {
            return Err(FsError::InvalidPath);
        }
        
        // Update cache
        self.block_cache.insert(block_num, data.to_vec());
        self.dirty_blocks.insert(block_num, data.to_vec());
        
        Ok(())
    }
    
    /// Flush dirty blocks to device
    fn sync_blocks(&mut self) -> Result<(), FsError> {
        if let Some(device) = &self.device {
            let mut dev = device.lock();
            
            for (block_num, data) in &self.dirty_blocks {
                dev.write_blocks(*block_num, 1, data)
                    .map_err(|_| FsError::IoError)?;
            }
            
            dev.flush().map_err(|_| FsError::IoError)?;
            self.dirty_blocks.clear();
            Ok(())
        } else {
            Err(FsError::IoError)
        }
    }
    
    /// Read an inode
    fn read_inode(&mut self, inode_num: u64) -> Result<Inode, FsError> {
        // Check cache first
        if let Some(inode) = self.inode_cache.get(&inode_num) {
            return Ok(*inode);
        }
        
        // For simplicity, assume one inode per block starting at inode_table_start
        let block_num = self.superblock.inode_table_start + inode_num - 1;
        let block = self.read_block(block_num)?;
        
        if block.len() < mem::size_of::<Inode>() {
            return Err(FsError::NotFound);
        }
        
        let inode = unsafe {
            *(block.as_ptr() as *const Inode)
        };
        
        // Cache the inode
        self.inode_cache.insert(inode_num, inode);
        Ok(inode)
    }
    
    /// Write an inode
    fn write_inode(&mut self, inode: &Inode) -> Result<(), FsError> {
        let block_num = self.superblock.inode_table_start + inode.number - 1;
        
        let inode_bytes = unsafe {
            core::slice::from_raw_parts(
                inode as *const Inode as *const u8,
                mem::size_of::<Inode>()
            )
        };
        
        let mut block = vec![0u8; BLOCK_SIZE as usize];
        block[..inode_bytes.len()].copy_from_slice(inode_bytes);
        
        self.write_block(block_num, &block)?;
        self.inode_cache.insert(inode.number, *inode);
        
        Ok(())
    }
}

impl FileSystem for SynFS {
    fn name(&self) -> &str {
        &self.name
    }
    
    fn mount(&mut self, _device_path: &str) -> Result<(), FsError> {
        // For now, we expect the device to be passed differently
        // This is a simplified implementation
        crate::println!("[SynFS] Mounting device: {}", _device_path);
        Ok(())
    }
    
    fn unmount(&mut self) -> Result<(), FsError> {
        // Sync all dirty data
        self.sync_blocks()?;
        
        // Mark superblock as clean
        self.superblock.clean = 1;
        let sb_bytes = unsafe {
            core::slice::from_raw_parts(
                &self.superblock as *const SuperBlock as *const u8,
                mem::size_of::<SuperBlock>()
            )
        };
        
        let mut block = vec![0u8; BLOCK_SIZE as usize];
        block[..sb_bytes.len()].copy_from_slice(sb_bytes);
        self.write_block(0, &block)?;
        self.sync_blocks()?;
        
        self.device = None;
        crate::println!("[SynFS] Unmounted file system");
        Ok(())
    }
    
    fn open(&self, path: &str, _flags: OpenFlags) -> Result<FileHandle, FsError> {
        // For now, only support root directory
        if path == "/" {
            Ok(1) // Return root inode number as handle
        } else {
            Err(FsError::NotFound)
        }
    }
    
    fn close(&self, _handle: FileHandle) -> Result<(), FsError> {
        Ok(())
    }
    
    fn read(&self, _handle: FileHandle, _buffer: &mut [u8]) -> Result<usize, FsError> {
        // Simplified implementation
        Ok(0)
    }
    
    fn write(&self, _handle: FileHandle, _data: &[u8]) -> Result<usize, FsError> {
        // Simplified implementation
        Ok(0)
    }
    
    fn seek(&self, _handle: FileHandle, offset: u64) -> Result<u64, FsError> {
        Ok(offset)
    }
    
    fn create(&self, _path: &str, _permissions: Permissions) -> Result<(), FsError> {
        Err(FsError::NotSupported)
    }
    
    fn mkdir(&self, _path: &str, _permissions: Permissions) -> Result<(), FsError> {
        Err(FsError::NotSupported)
    }
    
    fn unlink(&self, _path: &str) -> Result<(), FsError> {
        Err(FsError::NotSupported)
    }
    
    fn rmdir(&self, _path: &str) -> Result<(), FsError> {
        Err(FsError::NotSupported)
    }
    
    fn rename(&self, _old_path: &str, _new_path: &str) -> Result<(), FsError> {
        Err(FsError::NotSupported)
    }
    
    fn stat(&self, path: &str) -> Result<FileStats, FsError> {
        if path == "/" {
            Ok(FileStats {
                size: BLOCK_SIZE as u64,
                created: 0,
                modified: 0,
                accessed: 0,
                permissions: Permissions::new(0o755),
                file_type: FileType::Directory,
                inode: 1,
                device: 0,
                links: 1,
                uid: 0,
                gid: 0,
            })
        } else {
            Err(FsError::NotFound)
        }
    }
    
    fn readdir(&self, path: &str) -> Result<Vec<DirectoryEntry>, FsError> {
        if path == "/" {
            // Return empty directory for now
            Ok(Vec::new())
        } else {
            Err(FsError::NotFound)
        }
    }
    
    fn sync(&self) -> Result<(), FsError> {
        // Would flush dirty blocks in a full implementation
        Ok(())
    }
}

/// Create a new SynFS instance
pub fn create_synfs() -> SynFS {
    SynFS::new()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::drivers::storage::RamDisk;
    
    #[test]
    fn test_synfs_creation() {
        let fs = SynFS::new();
        assert_eq!(fs.name(), "synfs");
    }
}
