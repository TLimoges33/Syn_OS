// Virtual File System (VFS) Core Implementation
// Provides abstraction layer for multiple file systems

use alloc::collections::BTreeMap;
use alloc::string::{String, ToString};
use alloc::sync::Arc;
use alloc::vec::Vec;
use core::sync::atomic::{AtomicU64, Ordering};
use spin::Mutex;

/// File system error types
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum FsError {
    NotFound,
    PermissionDenied,
    AlreadyExists,
    InvalidPath,
    NotADirectory,
    IsADirectory,
    NotEmpty,
    NoSpace,
    ReadOnly,
    InvalidHandle,
    IoError,
    NotSupported,
}

/// File open flags
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct OpenFlags {
    pub read: bool,
    pub write: bool,
    pub create: bool,
    pub truncate: bool,
    pub append: bool,
    pub exclusive: bool,
}

impl OpenFlags {
    pub const READ: Self = Self {
        read: true,
        write: false,
        create: false,
        truncate: false,
        append: false,
        exclusive: false,
    };

    pub const WRITE: Self = Self {
        read: false,
        write: true,
        create: false,
        truncate: false,
        append: false,
        exclusive: false,
    };

    pub const READ_WRITE: Self = Self {
        read: true,
        write: true,
        create: false,
        truncate: false,
        append: false,
        exclusive: false,
    };

    pub const CREATE: Self = Self {
        read: false,
        write: false,
        create: true,
        truncate: false,
        append: false,
        exclusive: false,
    };

    pub const TRUNCATE: Self = Self {
        read: false,
        write: false,
        create: false,
        truncate: true,
        append: false,
        exclusive: false,
    };

    // Convert OpenFlags to u32 for storage
    pub fn to_u32(self) -> u32 {
        let mut flags = 0u32;
        if self.read {
            flags |= 0x01;
        }
        if self.write {
            flags |= 0x02;
        }
        if self.create {
            flags |= 0x04;
        }
        if self.truncate {
            flags |= 0x08;
        }
        if self.append {
            flags |= 0x10;
        }
        if self.exclusive {
            flags |= 0x20;
        }
        flags
    }

    // Convert u32 back to OpenFlags
    pub fn from_u32(flags: u32) -> Self {
        Self {
            read: (flags & 0x01) != 0,
            write: (flags & 0x02) != 0,
            create: (flags & 0x04) != 0,
            truncate: (flags & 0x08) != 0,
            append: (flags & 0x10) != 0,
            exclusive: (flags & 0x20) != 0,
        }
    }
}

impl core::ops::BitOr for OpenFlags {
    type Output = Self;

    fn bitor(self, rhs: Self) -> Self::Output {
        Self {
            read: self.read || rhs.read,
            write: self.write || rhs.write,
            create: self.create || rhs.create,
            truncate: self.truncate || rhs.truncate,
            append: self.append || rhs.append,
            exclusive: self.exclusive || rhs.exclusive,
        }
    }
}

/// File permissions
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Permissions {
    pub user_read: bool,
    pub user_write: bool,
    pub user_execute: bool,
    pub group_read: bool,
    pub group_write: bool,
    pub group_execute: bool,
    pub other_read: bool,
    pub other_write: bool,
    pub other_execute: bool,
}

impl Permissions {
    pub const fn new(mode: u16) -> Self {
        Self {
            user_read: (mode & 0o400) != 0,
            user_write: (mode & 0o200) != 0,
            user_execute: (mode & 0o100) != 0,
            group_read: (mode & 0o040) != 0,
            group_write: (mode & 0o020) != 0,
            group_execute: (mode & 0o010) != 0,
            other_read: (mode & 0o004) != 0,
            other_write: (mode & 0o002) != 0,
            other_execute: (mode & 0o001) != 0,
        }
    }

    pub fn to_mode(&self) -> u16 {
        let mut mode = 0u16;
        if self.user_read {
            mode |= 0o400;
        }
        if self.user_write {
            mode |= 0o200;
        }
        if self.user_execute {
            mode |= 0o100;
        }
        if self.group_read {
            mode |= 0o040;
        }
        if self.group_write {
            mode |= 0o020;
        }
        if self.group_execute {
            mode |= 0o010;
        }
        if self.other_read {
            mode |= 0o004;
        }
        if self.other_write {
            mode |= 0o002;
        }
        if self.other_execute {
            mode |= 0o001;
        }
        mode
    }
}

/// File types
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum FileType {
    RegularFile,
    Directory,
    SymbolicLink,
    BlockDevice,
    CharacterDevice,
    Fifo,
    Socket,
}

/// File handle type
pub type FileHandle = u64;

/// Timestamp type (Unix timestamp)
pub type Timestamp = u64;

/// File statistics
#[derive(Debug, Clone, Copy)]
/// POSIX-compliant file metadata
pub struct FileStats {
    pub size: u64,           // st_size
    pub created: Timestamp,  // st_ctime
    pub modified: Timestamp, // st_mtime
    pub accessed: Timestamp, // st_atime
    pub permissions: Permissions, // st_mode (lower bits)
    pub file_type: FileType,     // st_mode (upper bits)
    pub inode: u64,             // st_ino
    pub device: u64,            // st_dev
    pub links: u32,             // st_nlink
    pub uid: u32,               // st_uid
    pub gid: u32,               // st_gid
    pub blocks: u64,            // st_blocks - 512-byte blocks allocated
    pub block_size: u32,        // st_blksize - preferred block size for I/O
    pub rdev: u64,              // st_rdev - device ID (if special file)
}

/// File descriptor structure
#[derive(Debug)]
pub struct FileDescriptor {
    pub fd: u32,
    pub path: String,
    pub flags: u32,
    pub position: AtomicU64,
}

impl FileDescriptor {
    pub fn new(fd: u32, path: String, flags: u32) -> Self {
        Self {
            fd,
            path,
            flags,
            position: AtomicU64::new(0),
        }
    }

    pub fn seek(&self, offset: u64) {
        self.position.store(offset, Ordering::SeqCst);
    }

    pub fn position(&self) -> u64 {
        self.position.load(Ordering::SeqCst)
    }

    pub fn advance(&self, bytes: u64) {
        self.position.fetch_add(bytes, Ordering::SeqCst);
    }
}

/// Directory entry
#[derive(Debug, Clone)]
pub struct DirectoryEntry {
    pub name: String,
    pub file_type: FileType,
    pub inode: u64,
    pub size: u64,
}

/// File system trait - must be implemented by all file systems
pub trait FileSystem: Send + Sync {
    /// Get file system name
    fn name(&self) -> &str;

    /// Mount the file system
    fn mount(&mut self, device_path: &str) -> Result<(), FsError>;

    /// Unmount the file system
    fn unmount(&mut self) -> Result<(), FsError>;

    /// Open a file
    fn open(&self, path: &str, flags: OpenFlags) -> Result<FileHandle, FsError>;

    /// Close a file
    fn close(&self, handle: FileHandle) -> Result<(), FsError>;

    /// Read from a file
    fn read(&self, handle: FileHandle, buffer: &mut [u8]) -> Result<usize, FsError>;

    /// Write to a file
    fn write(&self, handle: FileHandle, data: &[u8]) -> Result<usize, FsError>;

    /// Seek to position in file
    fn seek(&self, handle: FileHandle, offset: u64) -> Result<u64, FsError>;

    /// Create a new file
    fn create(&self, path: &str, permissions: Permissions) -> Result<(), FsError>;

    /// Create a directory
    fn mkdir(&self, path: &str, permissions: Permissions) -> Result<(), FsError>;

    /// Delete a file
    fn unlink(&self, path: &str) -> Result<(), FsError>;

    /// Remove a directory
    fn rmdir(&self, path: &str) -> Result<(), FsError>;

    /// Rename/move a file
    fn rename(&self, old_path: &str, new_path: &str) -> Result<(), FsError>;

    /// Get file statistics
    fn stat(&self, path: &str) -> Result<FileStats, FsError>;

    /// List directory contents
    fn readdir(&self, path: &str) -> Result<Vec<DirectoryEntry>, FsError>;

    /// Synchronize file system
    fn sync(&self) -> Result<(), FsError>;
}

/// Mount point structure
#[derive(Debug, Clone)]
pub struct MountPoint {
    pub path: String,
    pub filesystem: String,
    pub device: String,
    pub flags: MountFlags,
}

/// Mount flags
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct MountFlags {
    pub read_only: bool,
    pub no_exec: bool,
    pub no_suid: bool,
    pub no_dev: bool,
}

impl Default for MountFlags {
    fn default() -> Self {
        Self {
            read_only: false,
            no_exec: false,
            no_suid: false,
            no_dev: false,
        }
    }
}

/// Virtual File System manager
pub struct VirtualFileSystem {
    /// Mounted file systems
    mount_table: BTreeMap<String, Arc<Mutex<dyn FileSystem>>>,

    /// Open file descriptors
    open_files: BTreeMap<FileHandle, FileDescriptor>,

    /// Next available file handle
    next_handle: AtomicU64,

    /// Mount points
    mount_points: Vec<MountPoint>,

    /// Root file system
    root_fs: Option<Arc<Mutex<dyn FileSystem>>>,
}

impl VirtualFileSystem {
    /// Create a new VFS instance
    pub fn new() -> Self {
        Self {
            mount_table: BTreeMap::new(),
            open_files: BTreeMap::new(),
            next_handle: AtomicU64::new(1),
            mount_points: Vec::new(),
            root_fs: None,
        }
    }

    /// Mount a file system at the specified mount point
    pub fn mount(
        &mut self,
        filesystem: Arc<Mutex<dyn FileSystem>>,
        mount_point: &str,
        device: &str,
        flags: MountFlags,
    ) -> Result<(), FsError> {
        // Validate mount point
        if mount_point.is_empty() || !mount_point.starts_with('/') {
            return Err(FsError::InvalidPath);
        }

        // Check if already mounted
        if self.mount_table.contains_key(mount_point) {
            return Err(FsError::AlreadyExists);
        }

        // Mount the file system
        {
            let mut fs = filesystem.lock();
            fs.mount(device)?;
        }

        // Add to mount table
        let fs_name = {
            let fs = filesystem.lock();
            fs.name().to_string()
        };

        self.mount_table
            .insert(mount_point.to_string(), filesystem.clone());

        // Add mount point
        self.mount_points.push(MountPoint {
            path: mount_point.to_string(),
            filesystem: fs_name,
            device: device.to_string(),
            flags,
        });

        // Set as root if mounting at /
        if mount_point == "/" {
            self.root_fs = Some(filesystem);
        }

        Ok(())
    }

    /// Unmount a file system
    pub fn unmount(&mut self, mount_point: &str) -> Result<(), FsError> {
        // Find and remove from mount table
        let filesystem = self
            .mount_table
            .remove(mount_point)
            .ok_or(FsError::NotFound)?;

        // Unmount the file system
        {
            let mut fs = filesystem.lock();
            fs.unmount()?;
        }

        // Remove mount point
        self.mount_points.retain(|mp| mp.path != mount_point);

        // Clear root if unmounting /
        if mount_point == "/" {
            self.root_fs = None;
        }

        Ok(())
    }

    /// Find the file system for a given path
    fn find_filesystem(&self, path: &str) -> Result<(Arc<Mutex<dyn FileSystem>>, String), FsError> {
        // Find the longest matching mount point
        let mut best_match = "";
        let mut best_fs = None;

        for mount_point in self.mount_table.keys() {
            if path.starts_with(mount_point) && mount_point.len() > best_match.len() {
                best_match = mount_point;
                best_fs = self.mount_table.get(mount_point);
            }
        }

        match best_fs {
            Some(fs) => {
                // Calculate relative path
                let relative_path = if best_match == "/" {
                    path.to_string()
                } else {
                    path[best_match.len()..].to_string()
                };
                Ok((fs.clone(), relative_path))
            }
            None => Err(FsError::NotFound),
        }
    }

    /// Open a file
    pub fn open(&mut self, path: &str, flags: OpenFlags) -> Result<FileHandle, FsError> {
        let (filesystem, relative_path) = self.find_filesystem(path)?;

        // Open file in the appropriate file system
        let handle = {
            let fs = filesystem.lock();
            fs.open(&relative_path, flags)?
        };

        // Create file descriptor
        let fs_name = {
            let fs = filesystem.lock();
            fs.name().to_string()
        };

        let stat = {
            let fs = filesystem.lock();
            fs.stat(&relative_path)?
        };

        // Generate new handle
        let new_handle = self.next_handle.fetch_add(1, Ordering::SeqCst);

        let fd = FileDescriptor::new(new_handle as u32, path.to_string(), flags.to_u32());

        self.open_files.insert(new_handle, fd);

        Ok(new_handle)
    }

    /// Close a file
    pub fn close(&mut self, handle: FileHandle) -> Result<(), FsError> {
        let fd = self
            .open_files
            .remove(&handle)
            .ok_or(FsError::InvalidHandle)?;

        let (filesystem, relative_path) = self.find_filesystem(&fd.path)?;
        let fs = filesystem.lock();
        fs.close(handle)
    }

    /// Read from a file
    pub fn read(&self, handle: FileHandle, buffer: &mut [u8]) -> Result<usize, FsError> {
        let fd = self.open_files.get(&handle).ok_or(FsError::InvalidHandle)?;

        let flags = OpenFlags::from_u32(fd.flags);
        if !flags.read {
            return Err(FsError::PermissionDenied);
        }

        let (filesystem, _) = self.find_filesystem(&fd.path)?;
        let fs = filesystem.lock();
        let bytes_read = fs.read(handle, buffer)?;

        // Update position
        fd.advance(bytes_read as u64);

        Ok(bytes_read)
    }

    /// Write to a file
    pub fn write(&self, handle: FileHandle, data: &[u8]) -> Result<usize, FsError> {
        let fd = self.open_files.get(&handle).ok_or(FsError::InvalidHandle)?;

        let flags = OpenFlags::from_u32(fd.flags);
        if !flags.write {
            return Err(FsError::PermissionDenied);
        }

        let (filesystem, _) = self.find_filesystem(&fd.path)?;
        let fs = filesystem.lock();
        let bytes_written = fs.write(handle, data)?;

        // Update position
        fd.advance(bytes_written as u64);

        Ok(bytes_written)
    }

    /// Seek in a file
    pub fn seek(&self, handle: FileHandle, offset: u64) -> Result<u64, FsError> {
        let fd = self.open_files.get(&handle).ok_or(FsError::InvalidHandle)?;

        let (filesystem, _) = self.find_filesystem(&fd.path)?;
        let fs = filesystem.lock();
        let new_position = fs.seek(handle, offset)?;

        // Update position
        fd.seek(new_position);

        Ok(new_position)
    }

    /// Create a file
    pub fn create(&self, path: &str, permissions: Permissions) -> Result<(), FsError> {
        let (filesystem, relative_path) = self.find_filesystem(path)?;
        let fs = filesystem.lock();
        fs.create(&relative_path, permissions)
    }

    /// Create a directory
    pub fn mkdir(&self, path: &str, permissions: Permissions) -> Result<(), FsError> {
        let (filesystem, relative_path) = self.find_filesystem(path)?;
        let fs = filesystem.lock();
        fs.mkdir(&relative_path, permissions)
    }

    /// Delete a file
    pub fn unlink(&self, path: &str) -> Result<(), FsError> {
        let (filesystem, relative_path) = self.find_filesystem(path)?;
        let fs = filesystem.lock();
        fs.unlink(&relative_path)
    }

    /// Remove a directory
    pub fn rmdir(&self, path: &str) -> Result<(), FsError> {
        let (filesystem, relative_path) = self.find_filesystem(path)?;
        let fs = filesystem.lock();
        fs.rmdir(&relative_path)
    }

    /// Rename a file
    pub fn rename(&self, old_path: &str, new_path: &str) -> Result<(), FsError> {
        // For now, require both paths to be on same file system
        let (old_fs, old_relative) = self.find_filesystem(old_path)?;
        let (new_fs, new_relative) = self.find_filesystem(new_path)?;

        // Check if same file system
        let old_name = {
            let fs = old_fs.lock();
            fs.name().to_string()
        };
        let new_name = {
            let fs = new_fs.lock();
            fs.name().to_string()
        };

        if old_name != new_name {
            return Err(FsError::NotSupported);
        }

        let fs = old_fs.lock();
        fs.rename(&old_relative, &new_relative)
    }

    /// Get file statistics
    pub fn stat(&self, path: &str) -> Result<FileStats, FsError> {
        let (filesystem, relative_path) = self.find_filesystem(path)?;
        let fs = filesystem.lock();
        fs.stat(&relative_path)
    }

    /// List directory contents
    pub fn readdir(&self, path: &str) -> Result<Vec<DirectoryEntry>, FsError> {
        let (filesystem, relative_path) = self.find_filesystem(path)?;
        let fs = filesystem.lock();
        fs.readdir(&relative_path)
    }

    /// Get mount points
    pub fn mount_points(&self) -> &[MountPoint] {
        &self.mount_points
    }

    /// Sync all mounted file systems
    pub fn sync_all(&self) -> Result<(), FsError> {
        for filesystem in self.mount_table.values() {
            let fs = filesystem.lock();
            fs.sync()?;
        }
        Ok(())
    }
}

/// Global VFS instance
static VFS: Mutex<Option<VirtualFileSystem>> = Mutex::new(None);

/// Initialize the VFS
pub fn init_vfs() {
    let mut vfs_lock = VFS.lock();
    *vfs_lock = Some(VirtualFileSystem::new());
}

/// Get a reference to the global VFS
pub fn get_vfs() -> &'static Mutex<Option<VirtualFileSystem>> {
    &VFS
}

/// VFS convenience functions
pub fn vfs_mount(
    filesystem: Arc<Mutex<dyn FileSystem>>,
    mount_point: &str,
    device: &str,
    flags: MountFlags,
) -> Result<(), FsError> {
    let mut vfs_lock = VFS.lock();
    if let Some(vfs) = vfs_lock.as_mut() {
        vfs.mount(filesystem, mount_point, device, flags)
    } else {
        Err(FsError::NotSupported)
    }
}

pub fn vfs_open(path: &str, flags: OpenFlags) -> Result<FileHandle, FsError> {
    let mut vfs_lock = VFS.lock();
    if let Some(vfs) = vfs_lock.as_mut() {
        vfs.open(path, flags)
    } else {
        Err(FsError::NotSupported)
    }
}

pub fn vfs_close(handle: FileHandle) -> Result<(), FsError> {
    let mut vfs_lock = VFS.lock();
    if let Some(vfs) = vfs_lock.as_mut() {
        vfs.close(handle)
    } else {
        Err(FsError::NotSupported)
    }
}

pub fn vfs_read(handle: FileHandle, buffer: &mut [u8]) -> Result<usize, FsError> {
    let vfs_lock = VFS.lock();
    if let Some(vfs) = vfs_lock.as_ref() {
        vfs.read(handle, buffer)
    } else {
        Err(FsError::NotSupported)
    }
}

pub fn vfs_write(handle: FileHandle, data: &[u8]) -> Result<usize, FsError> {
    let vfs_lock = VFS.lock();
    if let Some(vfs) = vfs_lock.as_ref() {
        vfs.write(handle, data)
    } else {
        Err(FsError::NotSupported)
    }
}
