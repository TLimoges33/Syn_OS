//! # External Command Manager for SynShell
//! 
//! Execute external commands with security controls and sandboxing

use alloc::{vec::Vec, string::String, string::ToString};
use alloc::format;

use super::{ShellResult, ShellError, ParsedCommand, Environment, SecurityContext, PrivilegeLevel, Capability};

/// External command execution manager
#[derive(Debug)]
pub struct ExternalCommandManager {
    allowed_paths: Vec<String>,
    blocked_commands: Vec<String>,
    sandbox_enabled: bool,
}

impl ExternalCommandManager {
    /// Create a new external command manager
    pub fn new() -> Self {
        Self {
            allowed_paths: vec![
                "/bin".to_string(),
                "/usr/bin".to_string(),
                "/usr/local/bin".to_string(),
                "/sbin".to_string(),
                "/usr/sbin".to_string(),
            ],
            blocked_commands: vec![
                "rm".to_string(),       // Dangerous file operations
                "dd".to_string(),       // Direct disk access
                "mkfs".to_string(),     // Filesystem formatting
                "fdisk".to_string(),    // Disk partitioning
                "mount".to_string(),    // Mount filesystems
                "umount".to_string(),   // Unmount filesystems
                "insmod".to_string(),   // Insert kernel modules
                "rmmod".to_string(),    // Remove kernel modules
                "reboot".to_string(),   // System reboot
                "shutdown".to_string(), // System shutdown
                "halt".to_string(),     // System halt
            ],
            sandbox_enabled: true,
        }
    }

    /// Execute an external command
    pub fn execute(
        &self,
        command: ParsedCommand,
        environment: &Environment,
        security_context: &SecurityContext,
    ) -> Result<ShellResult, ShellError> {
        // Security checks
        self.check_command_allowed(&command.name, security_context)?;
        self.check_path_allowed(&command.name)?;

        // Find command in PATH
        let command_path = self.find_command_in_path(&command.name, environment)?;

        // Execute with appropriate security context
        self.execute_with_security(&command_path, &command.args, environment, security_context)
    }

    /// Check if command is allowed based on security policy
    fn check_command_allowed(&self, command: &str, security_context: &SecurityContext) -> Result<(), ShellError> {
        // Check blocked commands
        if self.blocked_commands.contains(&command.to_string()) {
            if security_context.privilege_level != PrivilegeLevel::Root {
                return Err(ShellError::PermissionDenied(
                    format!("Command '{}' is blocked for security reasons", command)
                ));
            }
        }

        // Check specific command permissions
        match command {
            "iptables" | "netfilter" => {
                if !security_context.capabilities.contains(&Capability::NetAdmin) {
                    return Err(ShellError::PermissionDenied(
                        "Network administration privileges required".to_string()
                    ));
                }
            },
            "tcpdump" | "wireshark" => {
                if !security_context.capabilities.contains(&Capability::NetRaw) {
                    return Err(ShellError::PermissionDenied(
                        "Raw network access privileges required".to_string()
                    ));
                }
            },
            "mount" | "umount" | "fsck" => {
                if !security_context.capabilities.contains(&Capability::SysAdmin) {
                    return Err(ShellError::PermissionDenied(
                        "System administration privileges required".to_string()
                    ));
                }
            },
            _ => {}
        }

        Ok(())
    }

    /// Check if command path is allowed
    fn check_path_allowed(&self, command: &str) -> Result<(), ShellError> {
        // Prevent execution of absolute paths outside allowed directories
        if command.starts_with('/') {
            let allowed = self.allowed_paths.iter().any(|path| command.starts_with(path));
            if !allowed {
                return Err(ShellError::PermissionDenied(
                    format!("Execution from path '{}' is not allowed", command)
                ));
            }
        }

        // Prevent relative paths with directory traversal
        if command.contains("..") || command.contains("./") {
            return Err(ShellError::PermissionDenied(
                "Directory traversal in command path is not allowed".to_string()
            ));
        }

        Ok(())
    }

    /// Find command in PATH
    fn find_command_in_path(&self, command: &str, environment: &Environment) -> Result<String, ShellError> {
        // If it's an absolute path, check if it exists and is allowed
        if command.starts_with('/') {
            self.check_path_allowed(command)?;
            return Ok(command.to_string());
        }

        // Search in PATH directories
        if let Some(path_var) = environment.get("PATH") {
            for dir in path_var.split(':') {
                if self.allowed_paths.contains(&dir.to_string()) {
                    let full_path = format!("{}/{}", dir, command);
                    
                    // In a real implementation, we would check if the file exists and is executable
                    // For demo purposes, assume certain commands exist
                    if self.is_known_command(command) {
                        return Ok(full_path);
                    }
                }
            }
        }

        Err(ShellError::CommandNotFound(format!("Command '{}' not found", command)))
    }

    /// Check if this is a known command (stub implementation)
    fn is_known_command(&self, command: &str) -> bool {
        let known_commands = [
            "ls", "cat", "grep", "sed", "awk", "sort", "uniq", "wc", "head", "tail",
            "ps", "top", "kill", "killall", "jobs", "nohup",
            "cp", "mv", "chmod", "chown", "find", "locate",
            "tar", "gzip", "gunzip", "zip", "unzip",
            "man", "info", "which", "whereis", "file",
            "date", "uptime", "uname", "whoami", "id", "groups",
        ];

        known_commands.contains(&command)
    }

    /// Execute command with security context
    fn execute_with_security(
        &self,
        command_path: &str,
        args: &[String],
        environment: &Environment,
        security_context: &SecurityContext,
    ) -> Result<ShellResult, ShellError> {
        // In a real implementation, this would:
        // 1. Set up a sandbox if enabled
        // 2. Drop privileges if necessary
        // 3. Set up resource limits
        // 4. Execute the command
        // 5. Monitor and log execution

        // For now, simulate execution
        let command_name = command_path.split('/').last().unwrap_or(command_path);
        
        match command_name {
            "ls" => self.simulate_ls(args),
            "cat" => self.simulate_cat(args),
            "ps" => self.simulate_ps(args, security_context),
            "grep" => self.simulate_grep(args),
            "ping" => self.simulate_ping(args, security_context),
            "whoami" => self.simulate_whoami(security_context),
            "id" => self.simulate_id(security_context),
            "uname" => self.simulate_uname(args),
            "uptime" => self.simulate_uptime(),
            "date" => self.simulate_date(),
            _ => {
                // For other commands, return a generic message
                Ok(ShellResult::Success(format!(
                    "Executed '{}' with args: [{}]",
                    command_name,
                    args.join(", ")
                )))
            }
        }
    }

    /// Simulate ls command
    fn simulate_ls(&self, args: &[String]) -> Result<ShellResult, ShellError> {
        let mut output = String::new();
        
        if args.contains(&"-l".to_string()) || args.contains(&"-la".to_string()) {
            output.push_str("total 42\n");
            output.push_str("drwxr-xr-x  2 user user 4096 Jan  1 12:00 .\n");
            output.push_str("drwxr-xr-x  3 root root 4096 Jan  1 12:00 ..\n");
            output.push_str("-rw-r--r--  1 user user  220 Jan  1 12:00 .bashrc\n");
            output.push_str("-rw-r--r--  1 user user  807 Jan  1 12:00 .profile\n");
            output.push_str("drwxr-xr-x  2 user user 4096 Jan  1 12:00 Documents\n");
            output.push_str("drwxr-xr-x  2 user user 4096 Jan  1 12:00 Downloads\n");
        } else {
            output.push_str("Documents  Downloads  .bashrc  .profile\n");
        }
        
        Ok(ShellResult::Success(output))
    }

    /// Simulate cat command
    fn simulate_cat(&self, args: &[String]) -> Result<ShellResult, ShellError> {
        if args.is_empty() {
            return Err(ShellError::InvalidArgument("No file specified".to_string()));
        }

        let filename = &args[0];
        let content = match filename.as_str() {
            "/etc/passwd" => "root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000:User:/home/user:/bin/bash\n",
            "/proc/version" => "Linux version 5.15.0-synos (synos@localhost) (gcc version 11.2.0) #1 SMP Mon Jan 1 12:00:00 UTC 2024\n",
            "/proc/cpuinfo" => "processor\t: 0\nvendor_id\t: SynOS\nmodel name\t: SynOS Virtual CPU\n",
            _ => "File content simulation - this would be the actual file content\n",
        };

        Ok(ShellResult::Success(content.to_string()))
    }

    /// Simulate ps command
    fn simulate_ps(&self, args: &[String], security_context: &SecurityContext) -> Result<ShellResult, ShellError> {
        let mut output = String::new();
        
        if args.contains(&"aux".to_string()) || args.contains(&"-ef".to_string()) {
            output.push_str("  PID TTY      STAT   TIME COMMAND\n");
            output.push_str("    1 ?        Ss     0:01 /sbin/init\n");
            output.push_str("    2 ?        S      0:00 [kthreadd]\n");
            output.push_str("  100 ?        Ss     0:00 /bin/synshell\n");
            
            if security_context.privilege_level == PrivilegeLevel::Root {
                output.push_str("  101 ?        S      0:00 [kernel_worker]\n");
                output.push_str("  102 ?        S      0:00 [security_monitor]\n");
            }
        } else {
            output.push_str("  PID TTY      TIME CMD\n");
            output.push_str("  100 pts/0    00:00:01 synshell\n");
        }
        
        Ok(ShellResult::Success(output))
    }

    /// Simulate grep command
    fn simulate_grep(&self, args: &[String]) -> Result<ShellResult, ShellError> {
        if args.is_empty() {
            return Err(ShellError::InvalidArgument("No pattern specified".to_string()));
        }

        let pattern = &args[0];
        let output = format!("Lines matching '{}' would appear here\n", pattern);
        
        Ok(ShellResult::Success(output))
    }

    /// Simulate ping command
    fn simulate_ping(&self, args: &[String], security_context: &SecurityContext) -> Result<ShellResult, ShellError> {
        if !security_context.network_permissions.can_send_raw_packets {
            return Err(ShellError::PermissionDenied(
                "Raw packet sending not permitted".to_string()
            ));
        }

        if args.is_empty() {
            return Err(ShellError::InvalidArgument("No host specified".to_string()));
        }

        let host = &args[0];
        let output = format!(
            "PING {} (127.0.0.1) 56(84) bytes of data.\n\
             64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.123 ms\n\
             64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.156 ms\n\
             \n\
             --- {} ping statistics ---\n\
             2 packets transmitted, 2 received, 0% packet loss\n",
            host, host
        );
        
        Ok(ShellResult::Success(output))
    }

    /// Simulate whoami command
    fn simulate_whoami(&self, security_context: &SecurityContext) -> Result<ShellResult, ShellError> {
        let username = match security_context.privilege_level {
            PrivilegeLevel::Root => "root",
            _ => "user",
        };
        
        Ok(ShellResult::Success(username.to_string()))
    }

    /// Simulate id command
    fn simulate_id(&self, security_context: &SecurityContext) -> Result<ShellResult, ShellError> {
        let output = format!(
            "uid={}({}) gid={}({})",
            security_context.user_id,
            if security_context.privilege_level == PrivilegeLevel::Root { "root" } else { "user" },
            security_context.group_id,
            if security_context.privilege_level == PrivilegeLevel::Root { "root" } else { "user" }
        );
        
        Ok(ShellResult::Success(output))
    }

    /// Simulate uname command
    fn simulate_uname(&self, args: &[String]) -> Result<ShellResult, ShellError> {
        let output = if args.contains(&"-a".to_string()) {
            "SynOS synos-host 1.0.0 #1 SMP Mon Jan 1 12:00:00 UTC 2024 x86_64 GNU/Linux"
        } else if args.contains(&"-r".to_string()) {
            "1.0.0"
        } else {
            "SynOS"
        };
        
        Ok(ShellResult::Success(output.to_string()))
    }

    /// Simulate uptime command
    fn simulate_uptime(&self) -> Result<ShellResult, ShellError> {
        Ok(ShellResult::Success(
            " 12:34:56 up  1:23,  1 user,  load average: 0.15, 0.10, 0.05".to_string()
        ))
    }

    /// Simulate date command
    fn simulate_date(&self) -> Result<ShellResult, ShellError> {
        Ok(ShellResult::Success(
            "Mon Jan  1 12:34:56 UTC 2024".to_string()
        ))
    }

    /// Set allowed paths for command execution
    pub fn set_allowed_paths(&mut self, paths: Vec<String>) {
        self.allowed_paths = paths;
    }

    /// Add blocked command
    pub fn add_blocked_command(&mut self, command: String) {
        if !self.blocked_commands.contains(&command) {
            self.blocked_commands.push(command);
        }
    }

    /// Remove blocked command
    pub fn remove_blocked_command(&mut self, command: &str) {
        self.blocked_commands.retain(|cmd| cmd != command);
    }

    /// Enable/disable sandbox
    pub fn set_sandbox_enabled(&mut self, enabled: bool) {
        self.sandbox_enabled = enabled;
    }

    /// Get blocked commands list
    pub fn get_blocked_commands(&self) -> &[String] {
        &self.blocked_commands
    }

    /// Get allowed paths list
    pub fn get_allowed_paths(&self) -> &[String] {
        &self.allowed_paths
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::userspace::shell::{SecurityContext, PrivilegeLevel, NetworkPermissions};

    #[test]
    fn test_command_blocking() {
        let manager = ExternalCommandManager::new();
        let security_context = SecurityContext {
            user_id: 1000,
            group_id: 1000,
            privilege_level: PrivilegeLevel::User,
            capabilities: Vec::new(),
            network_permissions: NetworkPermissions::default(),
        };

        let result = manager.check_command_allowed("rm", &security_context);
        assert!(result.is_err());
    }

    #[test]
    fn test_path_validation() {
        let manager = ExternalCommandManager::new();
        
        assert!(manager.check_path_allowed("/bin/ls").is_ok());
        assert!(manager.check_path_allowed("../etc/passwd").is_err());
        assert!(manager.check_path_allowed("./malicious").is_err());
    }

    #[test]
    fn test_ls_simulation() {
        let manager = ExternalCommandManager::new();
        let result = manager.simulate_ls(&vec!["-l".to_string()]);
        
        assert!(result.is_ok());
        if let Ok(ShellResult::Success(output)) = result {
            assert!(output.contains("total"));
            assert!(output.contains("drwxr-xr-x"));
        }
    }
}
