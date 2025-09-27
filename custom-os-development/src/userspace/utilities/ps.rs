//! # PS Command Implementation
//! 
//! Process status utility for SynOS

use alloc::{vec::Vec, string::String, format};

/// Process information structure
#[derive(Debug, Clone)]
pub struct ProcessInfo {
    pub pid: u32,
    pub ppid: u32,
    pub name: String,
    pub state: ProcessState,
    pub cpu_usage: f32,
    pub memory_usage: u64,
    pub user_id: u32,
    pub group_id: u32,
    pub priority: i8,
    pub nice: i8,
    pub start_time: u64,
    pub cpu_time: u64,
    pub command_line: String,
}

/// Process states
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ProcessState {
    Running,
    Sleeping,
    Stopped,
    Zombie,
    Dead,
    Uninterruptible,
}

impl ProcessState {
    fn to_char(&self) -> char {
        match self {
            ProcessState::Running => 'R',
            ProcessState::Sleeping => 'S',
            ProcessState::Stopped => 'T',
            ProcessState::Zombie => 'Z',
            ProcessState::Dead => 'X',
            ProcessState::Uninterruptible => 'D',
        }
    }
}

/// PS command implementation
pub struct PsCommand;

impl PsCommand {
    /// Create new PS command
    pub fn new() -> Self {
        Self
    }

    /// Execute PS command with given arguments
    pub fn execute(&self, args: &[String]) -> Result<String, String> {
        let options = self.parse_args(args)?;
        let processes = self.get_processes(&options)?;
        self.format_output(&processes, &options)
    }

    /// Parse command line arguments
    fn parse_args(&self, args: &[String]) -> Result<PsOptions, String> {
        let mut options = PsOptions::default();

        for arg in args {
            match arg.as_str() {
                "aux" | "-aux" => {
                    options.show_all_users = true;
                    options.show_detailed = true;
                    options.show_processes_without_tty = true;
                },
                "-ef" | "ef" => {
                    options.show_all_users = true;
                    options.show_full_format = true;
                },
                "-e" | "e" => {
                    options.show_all_users = true;
                },
                "-f" | "f" => {
                    options.show_full_format = true;
                },
                "-u" | "u" => {
                    options.show_detailed = true;
                },
                "-x" | "x" => {
                    options.show_processes_without_tty = true;
                },
                "-a" | "a" => {
                    options.show_all_terminals = true;
                },
                "-l" | "l" => {
                    options.show_long_format = true;
                },
                "--help" | "-h" => {
                    return Ok(PsOptions { show_help: true, ..Default::default() });
                },
                _ if arg.starts_with('-') => {
                    return Err(format!("Unknown option: {}", arg));
                },
                _ => {
                    // Assume it's a process name or PID filter
                    options.filter = Some(arg.clone());
                }
            }
        }

        Ok(options)
    }

    /// Get process list based on options
    fn get_processes(&self, options: &PsOptions) -> Result<Vec<ProcessInfo>, String> {
        // In a real implementation, this would read from /proc or call kernel APIs
        // For now, we'll simulate some processes
        
        let mut processes = Vec::new();

        // System processes
        processes.push(ProcessInfo {
            pid: 1,
            ppid: 0,
            name: "init".to_string(),
            state: ProcessState::Sleeping,
            cpu_usage: 0.0,
            memory_usage: 2048,
            user_id: 0,
            group_id: 0,
            priority: 20,
            nice: 0,
            start_time: 0,
            cpu_time: 100,
            command_line: "/sbin/init".to_string(),
        });

        processes.push(ProcessInfo {
            pid: 2,
            ppid: 0,
            name: "kthreadd".to_string(),
            state: ProcessState::Sleeping,
            cpu_usage: 0.0,
            memory_usage: 0,
            user_id: 0,
            group_id: 0,
            priority: 20,
            nice: 0,
            start_time: 1,
            cpu_time: 50,
            command_line: "[kthreadd]".to_string(),
        });

        // Network stack processes
        processes.push(ProcessInfo {
            pid: 100,
            ppid: 1,
            name: "network_stack".to_string(),
            state: ProcessState::Sleeping,
            cpu_usage: 0.1,
            memory_usage: 8192,
            user_id: 0,
            group_id: 0,
            priority: 20,
            nice: 0,
            start_time: 10,
            cpu_time: 200,
            command_line: "/kernel/network_stack".to_string(),
        });

        // Security monitor
        processes.push(ProcessInfo {
            pid: 101,
            ppid: 1,
            name: "security_monitor".to_string(),
            state: ProcessState::Running,
            cpu_usage: 0.5,
            memory_usage: 4096,
            user_id: 0,
            group_id: 0,
            priority: 10,
            nice: -10,
            start_time: 11,
            cpu_time: 500,
            command_line: "/kernel/security_monitor".to_string(),
        });

        // Shell processes
        processes.push(ProcessInfo {
            pid: 1000,
            ppid: 1,
            name: "synshell".to_string(),
            state: ProcessState::Sleeping,
            cpu_usage: 0.0,
            memory_usage: 1024,
            user_id: 1000,
            group_id: 1000,
            priority: 20,
            nice: 0,
            start_time: 100,
            cpu_time: 50,
            command_line: "/bin/synshell".to_string(),
        });

        // Filter processes based on options
        if let Some(ref filter) = options.filter {
            if let Ok(pid) = filter.parse::<u32>() {
                processes.retain(|p| p.pid == pid);
            } else {
                processes.retain(|p| p.name.contains(filter) || p.command_line.contains(filter));
            }
        }

        // Filter by user permissions
        if !options.show_all_users {
            // In a real implementation, we would get the current user ID
            let current_user_id = 1000;
            processes.retain(|p| p.user_id == current_user_id);
        }

        Ok(processes)
    }

    /// Format output based on options
    fn format_output(&self, processes: &[ProcessInfo], options: &PsOptions) -> Result<String, String> {
        if options.show_help {
            return Ok(self.get_help_text());
        }

        let mut output = String::new();

        if options.show_detailed || options.show_full_format {
            // Detailed format (ps aux style)
            output.push_str("USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\n");
            
            for process in processes {
                let user = self.get_username(process.user_id);
                let vsz = process.memory_usage / 1024; // Convert to KB
                let rss = process.memory_usage / 1024;
                let time = self.format_time(process.cpu_time);
                let start = self.format_start_time(process.start_time);
                
                output.push_str(&format!(
                    "{:<10} {:>5} {:>4.1} {:>4.1} {:>7} {:>5} {:>8} {:>4} {:>5} {:>7} {}\n",
                    user,
                    process.pid,
                    process.cpu_usage,
                    self.calculate_memory_percentage(process.memory_usage),
                    vsz,
                    rss,
                    "?",  // TTY - would need to be determined
                    process.state.to_char(),
                    start,
                    time,
                    process.command_line
                ));
            }
        } else if options.show_long_format {
            // Long format (ps -l style)
            output.push_str("F   UID   PID  PPID PRI  NI    VSZ   RSS WCHAN  STAT TTY        TIME CMD\n");
            
            for process in processes {
                let vsz = process.memory_usage / 1024;
                let rss = process.memory_usage / 1024;
                let time = self.format_time(process.cpu_time);
                
                output.push_str(&format!(
                    "{} {:>5} {:>5} {:>5} {:>3} {:>3} {:>6} {:>5} {:>6} {:>4} {:>10} {:>7} {}\n",
                    0, // Flags
                    process.user_id,
                    process.pid,
                    process.ppid,
                    process.priority,
                    process.nice,
                    vsz,
                    rss,
                    "-", // WCHAN
                    process.state.to_char(),
                    "?", // TTY
                    time,
                    process.name
                ));
            }
        } else {
            // Simple format
            output.push_str("  PID TTY          TIME CMD\n");
            
            for process in processes {
                let time = self.format_time(process.cpu_time);
                output.push_str(&format!(
                    "{:>5} {:>12} {:>7} {}\n",
                    process.pid,
                    "?", // TTY
                    time,
                    process.name
                ));
            }
        }

        Ok(output)
    }

    /// Get username from user ID
    fn get_username(&self, uid: u32) -> String {
        match uid {
            0 => "root".to_string(),
            1000 => "user".to_string(),
            _ => format!("uid{}", uid),
        }
    }

    /// Calculate memory usage percentage
    fn calculate_memory_percentage(&self, memory_usage: u64) -> f32 {
        // Assume 1GB total memory for calculation
        let total_memory = 1024 * 1024 * 1024_u64;
        (memory_usage as f32 / total_memory as f32) * 100.0
    }

    /// Format CPU time
    fn format_time(&self, cpu_time: u64) -> String {
        let seconds = cpu_time / 1000;
        let minutes = seconds / 60;
        let hours = minutes / 60;
        
        if hours > 0 {
            format!("{}:{:02}:{:02}", hours, minutes % 60, seconds % 60)
        } else {
            format!("{}:{:02}", minutes, seconds % 60)
        }
    }

    /// Format start time
    fn format_start_time(&self, start_time: u64) -> String {
        // In a real implementation, this would format the actual start time
        if start_time < 60 {
            format!("{}s", start_time)
        } else if start_time < 3600 {
            format!("{}m", start_time / 60)
        } else {
            format!("{}h", start_time / 3600)
        }
    }

    /// Get help text
    fn get_help_text(&self) -> String {
        r#"Usage: ps [options]

DESCRIPTION:
    Display information about running processes.

OPTIONS:
    a       Show processes for all users
    u       Display user-oriented format
    x       Show processes without controlling terminals
    aux     Show all processes in user format
    -e      Show all processes
    -f      Show full format listing
    -ef     Show all processes in full format
    -l      Show long format
    -h      Show this help message

EXAMPLES:
    ps          Show processes for current user
    ps aux      Show all processes with detailed info
    ps -ef      Show all processes in full format
    ps -l       Show processes in long format

"#.to_string()
    }
}

/// PS command options
#[derive(Debug, Default)]
struct PsOptions {
    show_all_users: bool,
    show_detailed: bool,
    show_full_format: bool,
    show_long_format: bool,
    show_processes_without_tty: bool,
    show_all_terminals: bool,
    show_help: bool,
    filter: Option<String>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ps_basic() {
        let ps = PsCommand::new();
        let result = ps.execute(&[]);
        assert!(result.is_ok());
        
        let output = result.unwrap();
        assert!(output.contains("PID"));
        assert!(output.contains("CMD"));
    }

    #[test]
    fn test_ps_aux() {
        let ps = PsCommand::new();
        let result = ps.execute(&["aux".to_string()]);
        assert!(result.is_ok());
        
        let output = result.unwrap();
        assert!(output.contains("USER"));
        assert!(output.contains("%CPU"));
        assert!(output.contains("%MEM"));
    }

    #[test]
    fn test_ps_help() {
        let ps = PsCommand::new();
        let result = ps.execute(&["--help".to_string()]);
        assert!(result.is_ok());
        
        let output = result.unwrap();
        assert!(output.contains("Usage:"));
        assert!(output.contains("OPTIONS:"));
    }

    #[test]
    fn test_process_state_char() {
        assert_eq!(ProcessState::Running.to_char(), 'R');
        assert_eq!(ProcessState::Sleeping.to_char(), 'S');
        assert_eq!(ProcessState::Zombie.to_char(), 'Z');
    }
}
