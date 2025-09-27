// File System Module
// Contains VFS and all file system implementations

pub mod vfs;
pub mod synfs;

// Re-export common types
pub use vfs::{
    VirtualFileSystem, FileSystem, FsError, OpenFlags, Permissions, 
    FileType, FileStats, DirectoryEntry, FileHandle, Timestamp,
    init_vfs, get_vfs, vfs_mount, vfs_open, vfs_close, vfs_read, vfs_write
};

pub use synfs::{SynFS, create_synfs};

use crate::drivers::{get_device_manager, DeviceType, BlockDevice};
use alloc::sync::Arc;
use alloc::format;
use alloc::vec::Vec;
use alloc::string::{String, ToString};
use alloc::vec;
use spin::Mutex;

/// Initialize the file system subsystem
pub fn init_filesystem() -> Result<(), FsError> {
    crate::println!("[FS] Initializing file system subsystem");
    
    // Initialize VFS
    init_vfs();
    
    // Try to mount a root file system
    if let Err(e) = setup_root_filesystem() {
        crate::println!("[FS] Warning: Could not set up root filesystem: {:?}", e);
    }
    
    crate::println!("[FS] File system subsystem initialized");
    Ok(())
}

/// Set up the root file system
fn setup_root_filesystem() -> Result<(), FsError> {
    // Get device manager
    let dm_lock = get_device_manager().lock();
    if let Some(dm) = dm_lock.as_ref() {
        // Find a block device to use as root
        let block_devices = dm.get_devices_by_type(DeviceType::BlockDevice);
        
        if let Some((device_id, device)) = block_devices.first() {
            crate::println!("[FS] Found block device for root: {}", device_id);
            
            // Create a SynFS instance
            let synfs = create_synfs();
            
            // Try to format the device first (for testing)
            if let Some(block_dev) = device.try_lock() {
                // Cast to BlockDevice trait
                // This is a simplified approach - in a real implementation,
                // we'd have proper device abstraction
                drop(block_dev); // Release the lock
                
                // Format and mount
                let fs = Arc::new(Mutex::new(synfs));
                
                // Mount at root
                drop(dm_lock); // Release device manager lock
                vfs_mount(fs, "/", &format!("device:{}", device_id), vfs::MountFlags::default())?;
                
                crate::println!("[FS] Root file system mounted successfully");
                return Ok(());
            }
        }
    }
    
    Err(FsError::NotFound)
}

/// Mount a device at the specified mount point
pub fn mount_device(device_path: &str, mount_point: &str, fs_type: &str) -> Result<(), FsError> {
    match fs_type {
        "synfs" => {
            let synfs = create_synfs();
            let fs = Arc::new(Mutex::new(synfs));
            vfs_mount(fs, mount_point, device_path, vfs::MountFlags::default())
        }
        _ => Err(FsError::NotSupported)
    }
}

/// Unmount a file system
pub fn unmount_device(mount_point: &str) -> Result<(), FsError> {
    let mut vfs_lock = get_vfs().lock();
    if let Some(vfs) = vfs_lock.as_mut() {
        vfs.unmount(mount_point)
    } else {
        Err(FsError::NotSupported)
    }
}

/// Get file system statistics
pub fn get_fs_stats() -> Result<FileSystemStats, FsError> {
    let vfs_lock = get_vfs().lock();
    if let Some(vfs) = vfs_lock.as_ref() {
        let mount_points = vfs.mount_points();
        
        Ok(FileSystemStats {
            mounted_filesystems: mount_points.len(),
            total_mounts: mount_points.iter()
                .map(|mp| format!("{} on {} ({})", mp.filesystem, mp.path, mp.device))
                .collect(),
        })
    } else {
        Err(FsError::NotSupported)
    }
}

/// File system statistics
#[derive(Debug)]
pub struct FileSystemStats {
    pub mounted_filesystems: usize,
    pub total_mounts: alloc::vec::Vec<alloc::string::String>,
}

/// File system utilities
pub mod utils {
    use super::*;
    use alloc::string::String;
    use alloc::vec::{self, Vec};
    
    /// Read entire file into a vector
    pub fn read_file_to_vec(path: &str) -> Result<Vec<u8>, FsError> {
        let handle = vfs_open(path, OpenFlags::READ)?;
        
        // Get file size first
        let vfs_lock = get_vfs().lock();
        if let Some(vfs) = vfs_lock.as_ref() {
            let stats = vfs.stat(path)?;
            let mut buffer = vec![0u8; stats.size as usize];
            
            let bytes_read = vfs.read(handle, &mut buffer)?;
            buffer.truncate(bytes_read);
            
            drop(vfs_lock);
            vfs_close(handle)?;
            
            Ok(buffer)
        } else {
            Err(FsError::NotSupported)
        }
    }
    
    /// Write data to a file
    pub fn write_file_from_vec(path: &str, data: &[u8]) -> Result<(), FsError> {
        let handle = vfs_open(path, OpenFlags::WRITE | OpenFlags::CREATE | OpenFlags::TRUNCATE)?;
        
        let bytes_written = vfs_write(handle, data)?;
        if bytes_written != data.len() {
            vfs_close(handle)?;
            return Err(FsError::IoError);
        }
        
        vfs_close(handle)
    }
    
    /// List directory contents as strings
    pub fn list_directory(path: &str) -> Result<Vec<String>, FsError> {
        let vfs_lock = get_vfs().lock();
        if let Some(vfs) = vfs_lock.as_ref() {
            let entries = vfs.readdir(path)?;
            Ok(entries.into_iter().map(|entry| entry.name).collect())
        } else {
            Err(FsError::NotSupported)
        }
    }
    
    /// Check if a path exists
    pub fn path_exists(path: &str) -> bool {
        let vfs_lock = get_vfs().lock();
        if let Some(vfs) = vfs_lock.as_ref() {
            vfs.stat(path).is_ok()
        } else {
            false
        }
    }
    
    /// Get file type
    pub fn get_file_type(path: &str) -> Result<FileType, FsError> {
        let vfs_lock = get_vfs().lock();
        if let Some(vfs) = vfs_lock.as_ref() {
            let stats = vfs.stat(path)?;
            Ok(stats.file_type)
        } else {
            Err(FsError::NotSupported)
        }
    }
    
    /// Create directory recursively
    pub fn mkdir_recursive(path: &str, permissions: Permissions) -> Result<(), FsError> {
        if path == "/" {
            return Ok(()); // Root already exists
        }
        
        // Check if already exists
        if path_exists(path) {
            return Ok(());
        }
        
        // Find parent directory
        if let Some(parent_end) = path.rfind('/') {
            if parent_end > 0 {
                let parent = &path[..parent_end];
                mkdir_recursive(parent, permissions)?;
            }
        }
        
        // Create this directory
        let vfs_lock = get_vfs().lock();
        if let Some(vfs) = vfs_lock.as_ref() {
            vfs.mkdir(path, permissions)
        } else {
            Err(FsError::NotSupported)
        }
    }
}
