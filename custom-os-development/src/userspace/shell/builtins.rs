//! # Built-in Commands for SynShell
//!
//! Core shell commands with security context awareness

use alloc::format;
use alloc::{string::String, string::ToString, vec::Vec};

use super::{Environment, ParsedCommand, PrivilegeLevel, SecurityContext, ShellError, ShellResult};

/// Built-in command handler
#[derive(Debug)]
pub struct BuiltinCommands;

impl BuiltinCommands {
    /// Create new builtin commands handler
    pub fn new() -> Self {
        Self
    }

    /// Execute a built-in command
    pub fn execute(
        &mut self,
        command: ParsedCommand,
        environment: &mut Environment,
        current_directory: &mut String,
        security_context: &SecurityContext,
    ) -> Result<ShellResult, ShellError> {
        match command.name.as_str() {
            "help" => self.cmd_help(command.args),
            "exit" => self.cmd_exit(command.args),
            "cd" => self.cmd_cd(command.args, current_directory),
            "pwd" => self.cmd_pwd(),
            "echo" => self.cmd_echo(command.args),
            "env" => self.cmd_env(environment),
            "export" => self.cmd_export(command.args, environment),
            "unset" => self.cmd_unset(command.args, environment),
            "history" => self.cmd_history(command.args),
            "clear" => self.cmd_clear(),
            "which" => self.cmd_which(command.args, environment),
            "type" => self.cmd_type(command.args),
            "set" => self.cmd_set(command.args, environment),
            "whoami" => self.cmd_whoami(security_context),
            "id" => self.cmd_id(security_context),
            "umask" => self.cmd_umask(command.args),
            "alias" => self.cmd_alias(command.args),
            "unalias" => self.cmd_unalias(command.args),
            "jobs" => self.cmd_jobs(),
            "bg" => self.cmd_bg(command.args),
            "fg" => self.cmd_fg(command.args),
            "kill" => self.cmd_kill(command.args, security_context),
            _ => Err(ShellError::CommandNotFound(command.name)),
        }
    }

    /// Help command - show available commands
    fn cmd_help(&self, args: Vec<String>) -> Result<ShellResult, ShellError> {
        if args.is_empty() {
            let help_text = r#"🔒 SynShell - Security-Focused Command Interpreter

BUILT-IN COMMANDS:
  help [command]    - Show help information
  exit [code]       - Exit the shell
  cd [directory]    - Change directory
  pwd               - Print working directory
  echo [text...]    - Display text
  env               - Show environment variables
  export VAR=value  - Set environment variable
  unset VAR         - Remove environment variable
  history           - Show command history
  clear             - Clear the screen
  which [command]   - Locate a command
  type [command]    - Display command type
  set               - Show/set shell options
  whoami            - Show current user
  id                - Show user and group IDs
  umask [mode]      - Set file creation mask
  alias [name=cmd]  - Create command alias
  unalias [name]    - Remove command alias
  jobs              - Show active jobs
  bg [job]          - Put job in background
  fg [job]          - Bring job to foreground
  kill [pid]        - Terminate process

NETWORK COMMANDS:
  ping [host]       - Send ICMP ping packets
  netstat [opts]    - Display network connections
  ifconfig [iface]  - Configure network interface
  tcpdump [opts]    - Capture network packets
  wget [url]        - Download files from web
  curl [url]        - Transfer data from/to servers
  nmap [target]     - Network port scanner

SECURITY COMMANDS:
  portscan [host]   - Scan for open ports
  netmon [opts]     - Monitor network traffic
  integrity [path]  - Check file integrity
  loganalyze [log]  - Analyze log files
  secaudit          - Perform security audit
  firewall [rule]   - Manage firewall rules
  vulnscan [target] - Vulnerability scanner
  hashcheck [file]  - Verify file hashes
  encrypt [file]    - Encrypt files
  decrypt [file]    - Decrypt files

Use 'help [command]' for detailed information about specific commands.
Type 'man [command]' for comprehensive documentation."#;

            Ok(ShellResult::Success(help_text.to_string()))
        } else {
            self.cmd_help_specific(&args[0])
        }
    }

    /// Specific command help
    fn cmd_help_specific(&self, command: &str) -> Result<ShellResult, ShellError> {
        let help_text = match command {
            "cd" => "cd [directory] - Change current working directory",
            "pwd" => "pwd - Print current working directory",
            "echo" => "echo [text...] - Display text to output",
            "export" => "export VAR=value - Set environment variable",
            "ping" => "ping [host] - Send ICMP ping packets to host",
            "netstat" => "netstat [options] - Display network connections and routing tables",
            "portscan" => "portscan [host] [port-range] - Scan for open ports on target host",
            _ => "No detailed help available for this command",
        };

        Ok(ShellResult::Success(help_text.to_string()))
    }

    /// Exit command
    fn cmd_exit(&self, args: Vec<String>) -> Result<ShellResult, ShellError> {
        let exit_code = if args.is_empty() {
            0
        } else {
            args[0]
                .parse::<i32>()
                .map_err(|_| ShellError::InvalidArgument("Invalid exit code".to_string()))?
        };

        Ok(ShellResult::Exit(exit_code))
    }

    /// Change directory command
    fn cmd_cd(
        &self,
        args: Vec<String>,
        current_directory: &mut String,
    ) -> Result<ShellResult, ShellError> {
        let target_dir = if args.is_empty() {
            "/home/user".to_string() // Default to home directory
        } else {
            args[0].clone()
        };

        // In a real implementation, we would check if the directory exists
        // and update the actual working directory
        *current_directory = target_dir.clone();

        Ok(ShellResult::Success(format!(
            "Changed directory to: {}",
            target_dir
        )))
    }

    /// Print working directory command
    fn cmd_pwd(&self) -> Result<ShellResult, ShellError> {
        // In a real implementation, this would get the actual current directory
        Ok(ShellResult::Success("/current/directory".to_string()))
    }

    /// Echo command
    fn cmd_echo(&self, args: Vec<String>) -> Result<ShellResult, ShellError> {
        let output = args.join(" ");
        Ok(ShellResult::Success(output))
    }

    /// Environment variables command
    fn cmd_env(&self, environment: &Environment) -> Result<ShellResult, ShellError> {
        let mut output = String::new();
        for (key, value) in environment.iter() {
            output.push_str(&format!("{}={}\n", key, value));
        }
        Ok(ShellResult::Success(output))
    }

    /// Export environment variable
    fn cmd_export(
        &self,
        args: Vec<String>,
        environment: &mut Environment,
    ) -> Result<ShellResult, ShellError> {
        if args.is_empty() {
            return self.cmd_env(environment);
        }

        for arg in args {
            if let Some(eq_pos) = arg.find('=') {
                let key = arg[..eq_pos].to_string();
                let value = arg[eq_pos + 1..].to_string();
                environment.set(key, value);
            } else {
                return Err(ShellError::InvalidArgument(
                    "Invalid export syntax. Use: export VAR=value".to_string(),
                ));
            }
        }

        Ok(ShellResult::Success(
            "Environment variable(s) exported".to_string(),
        ))
    }

    /// Unset environment variable
    fn cmd_unset(
        &self,
        args: Vec<String>,
        environment: &mut Environment,
    ) -> Result<ShellResult, ShellError> {
        if args.is_empty() {
            return Err(ShellError::InvalidArgument(
                "Variable name required".to_string(),
            ));
        }

        for var_name in args {
            environment.unset(&var_name);
        }

        Ok(ShellResult::Success(
            "Environment variable(s) removed".to_string(),
        ))
    }

    /// History command
    fn cmd_history(&self, _args: Vec<String>) -> Result<ShellResult, ShellError> {
        // In a real implementation, this would show command history
        Ok(ShellResult::Success(
            "Command history functionality not yet implemented".to_string(),
        ))
    }

    /// Clear screen command
    fn cmd_clear(&self) -> Result<ShellResult, ShellError> {
        // In a real implementation, this would clear the terminal screen
        Ok(ShellResult::Success(
            "\n\n\n=== Screen Cleared ===\n".to_string(),
        ))
    }

    /// Which command - locate a command
    fn cmd_which(
        &self,
        args: Vec<String>,
        environment: &Environment,
    ) -> Result<ShellResult, ShellError> {
        if args.is_empty() {
            return Err(ShellError::InvalidArgument(
                "Command name required".to_string(),
            ));
        }

        let command = &args[0];
        if let Some(path) = environment.get("PATH") {
            for dir in path.split(':') {
                // In a real implementation, we would check if the file exists
                let full_path = format!("{}/{}", dir, command);
                // For demo purposes, assume common commands exist in /bin
                if dir == "/bin" && ["ls", "cat", "ps", "kill"].contains(&command.as_str()) {
                    return Ok(ShellResult::Success(full_path));
                }
            }
        }

        Err(ShellError::CommandNotFound(format!(
            "{}: command not found",
            command
        )))
    }

    /// Type command - display command type
    fn cmd_type(&self, args: Vec<String>) -> Result<ShellResult, ShellError> {
        if args.is_empty() {
            return Err(ShellError::InvalidArgument(
                "Command name required".to_string(),
            ));
        }

        let command = &args[0];
        let builtin_commands = [
            "help", "exit", "cd", "pwd", "echo", "env", "export", "unset", "history", "clear",
            "which", "type", "set", "whoami", "id",
        ];

        if builtin_commands.contains(&command.as_str()) {
            Ok(ShellResult::Success(format!(
                "{} is a shell builtin",
                command
            )))
        } else {
            Ok(ShellResult::Success(format!(
                "{} is an external command",
                command
            )))
        }
    }

    /// Set command - show/set shell options
    fn cmd_set(
        &self,
        args: Vec<String>,
        environment: &mut Environment,
    ) -> Result<ShellResult, ShellError> {
        if args.is_empty() {
            return self.cmd_env(environment);
        }

        // In a real implementation, this would handle shell options
        Ok(ShellResult::Success(
            "Set functionality not yet implemented".to_string(),
        ))
    }

    /// Who am I command
    fn cmd_whoami(&self, security_context: &SecurityContext) -> Result<ShellResult, ShellError> {
        let username = match security_context.privilege_level {
            PrivilegeLevel::Root => "root",
            _ => "user",
        };
        Ok(ShellResult::Success(username.to_string()))
    }

    /// ID command - show user and group IDs
    fn cmd_id(&self, security_context: &SecurityContext) -> Result<ShellResult, ShellError> {
        let output = format!(
            "uid={}({}) gid={}({})",
            security_context.user_id,
            if security_context.privilege_level == PrivilegeLevel::Root {
                "root"
            } else {
                "user"
            },
            security_context.group_id,
            if security_context.privilege_level == PrivilegeLevel::Root {
                "root"
            } else {
                "user"
            }
        );
        Ok(ShellResult::Success(output))
    }

    /// Umask command
    fn cmd_umask(&self, _args: Vec<String>) -> Result<ShellResult, ShellError> {
        // In a real implementation, this would show/set file creation mask
        Ok(ShellResult::Success("0022".to_string()))
    }

    /// Alias command
    fn cmd_alias(&self, _args: Vec<String>) -> Result<ShellResult, ShellError> {
        // In a real implementation, this would manage command aliases
        Ok(ShellResult::Success(
            "Alias functionality not yet implemented".to_string(),
        ))
    }

    /// Unalias command
    fn cmd_unalias(&self, _args: Vec<String>) -> Result<ShellResult, ShellError> {
        // In a real implementation, this would remove command aliases
        Ok(ShellResult::Success(
            "Unalias functionality not yet implemented".to_string(),
        ))
    }

    /// Jobs command
    fn cmd_jobs(&self) -> Result<ShellResult, ShellError> {
        // In a real implementation, this would show background jobs
        Ok(ShellResult::Success("No active jobs".to_string()))
    }

    /// Background command
    fn cmd_bg(&self, _args: Vec<String>) -> Result<ShellResult, ShellError> {
        // In a real implementation, this would put jobs in background
        Ok(ShellResult::Success(
            "Background job functionality not yet implemented".to_string(),
        ))
    }

    /// Foreground command
    fn cmd_fg(&self, _args: Vec<String>) -> Result<ShellResult, ShellError> {
        // In a real implementation, this would bring jobs to foreground
        Ok(ShellResult::Success(
            "Foreground job functionality not yet implemented".to_string(),
        ))
    }

    /// Kill command
    fn cmd_kill(
        &self,
        args: Vec<String>,
        security_context: &SecurityContext,
    ) -> Result<ShellResult, ShellError> {
        if args.is_empty() {
            return Err(ShellError::InvalidArgument(
                "Process ID required".to_string(),
            ));
        }

        // Check if user has permission to kill processes
        if security_context.privilege_level == PrivilegeLevel::User {
            return Err(ShellError::PermissionDenied(
                "Insufficient privileges to kill processes".to_string(),
            ));
        }

        let pid = args[0]
            .parse::<u32>()
            .map_err(|_| ShellError::InvalidArgument("Invalid process ID".to_string()))?;

        // In a real implementation, this would send a signal to the process
        Ok(ShellResult::Success(format!(
            "Signal sent to process {}",
            pid
        )))
    }
}
