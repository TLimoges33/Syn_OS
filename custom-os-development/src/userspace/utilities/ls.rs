//! # LS Command Implementation
//!
//! File listing utility for SynOS with security-aware file system access

use alloc::{format, string::String, vec::Vec};

/// File information structure
#[derive(Debug, Clone)]
pub struct FileInfo {
    pub name: String,
    pub size: u64,
    pub permissions: u32,
    pub owner_uid: u32,
    pub group_gid: u32,
    pub modified_time: u64,
    pub is_directory: bool,
    pub is_symlink: bool,
    pub link_target: Option<String>,
}

/// File type classification
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum FileType {
    Regular,
    Directory,
    Symlink,
    Block,
    Character,
    Fifo,
    Socket,
}

/// LS command implementation
pub struct LsCommand;

impl LsCommand {
    /// Create new LS command
    pub fn new() -> Self {
        Self
    }

    /// Execute LS command with given arguments
    pub fn execute(&self, args: &[String]) -> Result<String, String> {
        let options = self.parse_args(args)?;
        let path = options.path.as_deref().unwrap_or(".");
        let files = self.list_directory(path, &options)?;
        self.format_output(&files, &options)
    }

    /// Parse command line arguments
    fn parse_args(&self, args: &[String]) -> Result<LsOptions, String> {
        let mut options = LsOptions::default();

        for arg in args {
            match arg.as_str() {
                "-l" => options.long_format = true,
                "-a" => options.show_hidden = true,
                "-A" => options.show_almost_all = true,
                "-h" => options.human_readable = true,
                "-R" => options.recursive = true,
                "-t" => options.sort_by_time = true,
                "-S" => options.sort_by_size = true,
                "-r" => options.reverse_order = true,
                "-1" => options.one_per_line = true,
                "-F" => options.classify = true,
                "-i" => options.show_inode = true,
                "-d" => options.directory_only = true,
                "--color" => options.use_color = true,
                "--help" => {
                    return Ok(LsOptions {
                        show_help: true,
                        ..Default::default()
                    })
                }
                _ if arg.starts_with('-') => {
                    return Err(format!("Unknown option: {}", arg));
                }
                _ => {
                    options.path = Some(arg.clone());
                }
            }
        }

        Ok(options)
    }

    /// List directory contents
    fn list_directory(&self, path: &str, options: &LsOptions) -> Result<Vec<FileInfo>, String> {
        // In a real implementation, this would read the actual filesystem
        // For now, we'll simulate some files

        let mut files = Vec::new();

        // Simulated file system entries
        if path == "." || path == "/" {
            files.push(FileInfo {
                name: ".".to_string(),
                size: 4096,
                permissions: 0o755,
                owner_uid: 1000,
                group_gid: 1000,
                modified_time: 1704067200, // 2024-01-01
                is_directory: true,
                is_symlink: false,
                link_target: None,
            });

            files.push(FileInfo {
                name: "..".to_string(),
                size: 4096,
                permissions: 0o755,
                owner_uid: 0,
                group_gid: 0,
                modified_time: 1704067200,
                is_directory: true,
                is_symlink: false,
                link_target: None,
            });

            files.push(FileInfo {
                name: "Documents".to_string(),
                size: 4096,
                permissions: 0o755,
                owner_uid: 1000,
                group_gid: 1000,
                modified_time: 1704067200,
                is_directory: true,
                is_symlink: false,
                link_target: None,
            });

            files.push(FileInfo {
                name: "Downloads".to_string(),
                size: 4096,
                permissions: 0o755,
                owner_uid: 1000,
                group_gid: 1000,
                modified_time: 1704067200,
                is_directory: true,
                is_symlink: false,
                link_target: None,
            });

            files.push(FileInfo {
                name: ".bashrc".to_string(),
                size: 220,
                permissions: 0o644,
                owner_uid: 1000,
                group_gid: 1000,
                modified_time: 1704067200,
                is_directory: false,
                is_symlink: false,
                link_target: None,
            });

            files.push(FileInfo {
                name: "synos_config.yaml".to_string(),
                size: 1024,
                permissions: 0o600,
                owner_uid: 1000,
                group_gid: 1000,
                modified_time: 1704067200,
                is_directory: false,
                is_symlink: false,
                link_target: None,
            });

            files.push(FileInfo {
                name: "network_logs".to_string(),
                size: 8192,
                permissions: 0o644,
                owner_uid: 1000,
                group_gid: 1000,
                modified_time: 1704067200,
                is_directory: false,
                is_symlink: false,
                link_target: None,
            });
        }

        // Filter hidden files
        if !options.show_hidden && !options.show_almost_all {
            files.retain(|f| !f.name.starts_with('.') || f.name == "." || f.name == "..");
        }

        if options.show_almost_all && !options.show_hidden {
            files.retain(|f| f.name != "." && f.name != "..");
        }

        // Sort files
        self.sort_files(&mut files, options);

        Ok(files)
    }

    /// Sort files based on options
    fn sort_files(&self, files: &mut Vec<FileInfo>, options: &LsOptions) {
        if options.sort_by_time {
            files.sort_by(|a, b| b.modified_time.cmp(&a.modified_time));
        } else if options.sort_by_size {
            files.sort_by(|a, b| b.size.cmp(&a.size));
        } else {
            files.sort_by(|a, b| a.name.to_lowercase().cmp(&b.name.to_lowercase()));
        }

        if options.reverse_order {
            files.reverse();
        }
    }

    /// Format output based on options
    fn format_output(&self, files: &[FileInfo], options: &LsOptions) -> Result<String, String> {
        if options.show_help {
            return Ok(self.get_help_text());
        }

        let mut output = String::new();

        if options.long_format {
            // Long format listing
            for file in files {
                let permissions = self.format_permissions(file.permissions, file.is_directory);
                let size = if options.human_readable {
                    self.format_human_size(file.size)
                } else {
                    file.size.to_string()
                };
                let time = self.format_time(file.modified_time);
                let owner = self.get_username(file.owner_uid);
                let group = self.get_groupname(file.group_gid);

                let mut name = file.name.clone();
                if options.classify {
                    name = self.add_classification(&name, file);
                }

                if options.use_color {
                    name = self.colorize_name(&name, file);
                }

                if options.show_inode {
                    output.push_str(&format!(
                        "{:>7} {} {:>3} {:<8} {:<8} {:>8} {} {}\n",
                        1000, // Simulated inode
                        permissions,
                        1, // Link count
                        owner,
                        group,
                        size,
                        time,
                        name
                    ));
                } else {
                    output.push_str(&format!(
                        "{} {:>3} {:<8} {:<8} {:>8} {} {}\n",
                        permissions,
                        1, // Link count
                        owner,
                        group,
                        size,
                        time,
                        name
                    ));
                }
            }
        } else if options.one_per_line {
            // One file per line
            for file in files {
                let mut name = file.name.clone();
                if options.classify {
                    name = self.add_classification(&name, file);
                }
                if options.use_color {
                    name = self.colorize_name(&name, file);
                }
                output.push_str(&format!("{}\n", name));
            }
        } else {
            // Simple multi-column format
            let names: Vec<String> = files
                .iter()
                .map(|f| {
                    let mut name = f.name.clone();
                    if options.classify {
                        name = self.add_classification(&name, f);
                    }
                    if options.use_color {
                        name = self.colorize_name(&name, f);
                    }
                    name
                })
                .collect();

            // Simple formatting - just space-separated for now
            output = names.join("  ");
            output.push('\n');
        }

        Ok(output)
    }

    /// Format file permissions
    fn format_permissions(&self, perms: u32, is_dir: bool) -> String {
        let file_type = if is_dir { 'd' } else { '-' };
        let owner = self.format_permission_trio((perms >> 6) & 7);
        let group = self.format_permission_trio((perms >> 3) & 7);
        let other = self.format_permission_trio(perms & 7);

        format!("{}{}{}{}", file_type, owner, group, other)
    }

    /// Format permission trio (rwx)
    fn format_permission_trio(&self, perm: u32) -> String {
        let r = if perm & 4 != 0 { 'r' } else { '-' };
        let w = if perm & 2 != 0 { 'w' } else { '-' };
        let x = if perm & 1 != 0 { 'x' } else { '-' };
        format!("{}{}{}", r, w, x)
    }

    /// Format file size in human-readable format
    fn format_human_size(&self, size: u64) -> String {
        const UNITS: &[&str] = &["B", "K", "M", "G", "T"];
        let mut size = size as f64;
        let mut unit_index = 0;

        while size >= 1024.0 && unit_index < UNITS.len() - 1 {
            size /= 1024.0;
            unit_index += 1;
        }

        if unit_index == 0 {
            format!("{}", size as u64)
        } else {
            format!("{:.1}{}", size, UNITS[unit_index])
        }
    }

    /// Format timestamp
    fn format_time(&self, timestamp: u64) -> String {
        // In a real implementation, this would format the actual timestamp
        "Jan  1 12:00".to_string()
    }

    /// Get username from UID
    fn get_username(&self, uid: u32) -> String {
        match uid {
            0 => "root".to_string(),
            1000 => "user".to_string(),
            _ => format!("{}", uid),
        }
    }

    /// Get group name from GID
    fn get_groupname(&self, gid: u32) -> String {
        match gid {
            0 => "root".to_string(),
            1000 => "user".to_string(),
            _ => format!("{}", gid),
        }
    }

    /// Add file type classification
    fn add_classification(&self, name: &str, file: &FileInfo) -> String {
        if file.is_directory {
            format!("{}/", name)
        } else if file.permissions & 0o111 != 0 {
            format!("{}*", name)
        } else if file.is_symlink {
            format!("{}@", name)
        } else {
            name.to_string()
        }
    }

    /// Add color codes for different file types
    fn colorize_name(&self, name: &str, file: &FileInfo) -> String {
        if file.is_directory {
            format!("\x1b[34m{}\x1b[0m", name) // Blue
        } else if file.permissions & 0o111 != 0 {
            format!("\x1b[32m{}\x1b[0m", name) // Green
        } else if file.is_symlink {
            format!("\x1b[36m{}\x1b[0m", name) // Cyan
        } else {
            name.to_string()
        }
    }

    /// Get help text
    fn get_help_text(&self) -> String {
        r#"Usage: ls [OPTION]... [FILE]...

DESCRIPTION:
    List information about files and directories.

OPTIONS:
    -l      Use long listing format
    -a      Show all files including hidden (starting with .)
    -A      Show all files except . and ..
    -h      Print human readable sizes (1K 234M 2G)
    -R      List subdirectories recursively
    -t      Sort by modification time
    -S      Sort by file size
    -r      Reverse order while sorting
    -1      List one file per line
    -F      Append indicator (*/=>@|) to entries
    -i      Print index number of each file
    -d      List directories themselves, not their contents
    --color Use colors to distinguish file types
    --help  Show this help message

EXAMPLES:
    ls              List current directory
    ls -la          List all files in long format
    ls -lh          List with human-readable sizes
    ls -lt          List sorted by modification time

"#
        .to_string()
    }
}

/// LS command options
#[derive(Debug, Default)]
struct LsOptions {
    long_format: bool,
    show_hidden: bool,
    show_almost_all: bool,
    human_readable: bool,
    recursive: bool,
    sort_by_time: bool,
    sort_by_size: bool,
    reverse_order: bool,
    one_per_line: bool,
    classify: bool,
    show_inode: bool,
    directory_only: bool,
    use_color: bool,
    show_help: bool,
    path: Option<String>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ls_basic() {
        let ls = LsCommand::new();
        let result = ls.execute(&[]);
        assert!(result.is_ok());

        let output = result.unwrap();
        assert!(output.contains("Documents"));
        assert!(output.contains("Downloads"));
    }

    #[test]
    fn test_ls_long_format() {
        let ls = LsCommand::new();
        let result = ls.execute(&["-l".to_string()]);
        assert!(result.is_ok());

        let output = result.unwrap();
        assert!(output.contains("drwxr-xr-x"));
        assert!(output.contains("user"));
    }

    #[test]
    fn test_ls_all_files() {
        let ls = LsCommand::new();
        let result = ls.execute(&["-a".to_string()]);
        assert!(result.is_ok());

        let output = result.unwrap();
        assert!(output.contains(".bashrc"));
    }

    #[test]
    fn test_permission_formatting() {
        let ls = LsCommand::new();
        assert_eq!(ls.format_permissions(0o755, true), "drwxr-xr-x");
        assert_eq!(ls.format_permissions(0o644, false), "-rw-r--r--");
    }

    #[test]
    fn test_human_size_formatting() {
        let ls = LsCommand::new();
        assert_eq!(ls.format_human_size(1024), "1.0K");
        assert_eq!(ls.format_human_size(1048576), "1.0M");
        assert_eq!(ls.format_human_size(512), "512");
    }
}
