//! # CAT Command Implementation
//! 
//! File concatenation and display utility for SynOS

use alloc::{vec::Vec, string::String, format};

/// CAT command implementation
pub struct CatCommand;

impl CatCommand {
    /// Create new CAT command
    pub fn new() -> Self {
        Self
    }

    /// Execute CAT command with given arguments
    pub fn execute(&self, args: &[String]) -> Result<String, String> {
        let options = self.parse_args(args)?;
        
        if options.show_help {
            return Ok(self.get_help_text());
        }

        if options.files.is_empty() {
            return Err("No files specified. Use --help for usage information.".to_string());
        }

        let mut output = String::new();
        let mut line_number = 1;

        for file_path in &options.files {
            let content = self.read_file(file_path)?;
            let formatted_content = self.format_content(&content, &options, &mut line_number);
            output.push_str(&formatted_content);
        }

        Ok(output)
    }

    /// Parse command line arguments
    fn parse_args(&self, args: &[String]) -> Result<CatOptions, String> {
        let mut options = CatOptions::default();

        for arg in args {
            match arg.as_str() {
                "-n" | "--number" => options.number_lines = true,
                "-b" | "--number-nonblank" => options.number_nonblank = true,
                "-s" | "--squeeze-blank" => options.squeeze_blank = true,
                "-T" | "--show-tabs" => options.show_tabs = true,
                "-E" | "--show-ends" => options.show_ends = true,
                "-A" | "--show-all" => {
                    options.show_tabs = true;
                    options.show_ends = true;
                    options.show_nonprinting = true;
                },
                "-v" | "--show-nonprinting" => options.show_nonprinting = true,
                "--help" => options.show_help = true,
                _ if arg.starts_with('-') => {
                    return Err(format!("Unknown option: {}", arg));
                },
                _ => {
                    options.files.push(arg.clone());
                }
            }
        }

        Ok(options)
    }

    /// Read file content (simulated)
    fn read_file(&self, file_path: &str) -> Result<String, String> {
        // In a real implementation, this would read from the actual filesystem
        // For now, we'll simulate some common file contents
        
        match file_path {
            "/etc/passwd" => Ok(r#"root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
user:x:1000:1000:User:/home/user:/bin/bash
"#.to_string()),

            "/etc/hosts" => Ok(r#"127.0.0.1	localhost
127.0.1.1	synos-host
::1		localhost ip6-localhost ip6-loopback
ff02::1		ip6-allnodes
ff02::2		ip6-allrouters
"#.to_string()),

            "/proc/version" => Ok("Linux version 5.15.0-synos (synos@localhost) (gcc version 11.2.0) #1 SMP Mon Jan 1 12:00:00 UTC 2024\n".to_string()),

            "/proc/cpuinfo" => Ok(r#"processor	: 0
vendor_id	: SynOS
cpu family	: 6
model		: 142
model name	: SynOS Virtual CPU @ 2.40GHz
stepping	: 10
microcode	: 0xea
cpu MHz		: 2400.000
cache size	: 6144 KB
physical id	: 0
siblings	: 1
core id		: 0
cpu cores	: 1
apicid		: 0
initial apicid	: 0
fpu		: yes
fpu_exception	: yes
cpuid level	: 22
wp		: yes
"#.to_string()),

            "/proc/meminfo" => Ok(r#"MemTotal:        1048576 kB
MemFree:          524288 kB
MemAvailable:     786432 kB
Buffers:           65536 kB
Cached:           196608 kB
SwapCached:            0 kB
Active:           262144 kB
Inactive:         131072 kB
Active(anon):      98304 kB
Inactive(anon):    32768 kB
Active(file):     163840 kB
Inactive(file):    98304 kB
"#.to_string()),

            ".bashrc" => Ok(r#"# ~/.bashrc: executed by bash(1) for non-login shells.

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

# SynOS specific aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias grep='grep --color=auto'
alias synos-status='cat /proc/synos/status'
alias network-monitor='netstat -tulpn'

# Security aliases
alias portscan='synos-portscan'
alias netmon='synos-netmon'
alias secaudit='synos-security-audit'

export PATH="/bin:/usr/bin:/usr/local/bin:/sbin:/usr/sbin"
export SYNOS_SECURITY_LEVEL="HIGH"
"#.to_string()),

            "synos_config.yaml" => Ok(r#"# SynOS Configuration File
system:
  name: "SynOS"
  version: "1.0.0"
  build_date: "2024-01-01"

security:
  level: "HIGH"
  audit_enabled: true
  network_monitoring: true
  encryption_required: true

network:
  interfaces:
    - name: "lo"
      type: "loopback"
    - name: "eth0"
      type: "ethernet"
  
  firewall:
    enabled: true
    default_policy: "DROP"

logging:
  level: "INFO"
  output: "/var/log/synos.log"
  max_size: "100MB"
  rotation: true
"#.to_string()),

            "network_logs" => Ok(r#"2024-01-01 12:00:01 [INFO] Network stack initialized
2024-01-01 12:00:02 [INFO] Ethernet interface eth0 up
2024-01-01 12:00:03 [INFO] IPv4 stack ready
2024-01-01 12:00:04 [INFO] TCP/UDP sockets available
2024-01-01 12:00:05 [DEBUG] ARP cache initialized
2024-01-01 12:00:10 [INFO] Incoming connection on port 22
2024-01-01 12:00:11 [WARN] Failed login attempt from 192.168.1.100
2024-01-01 12:00:15 [INFO] Network monitor active
2024-01-01 12:00:20 [DEBUG] Packet filter rules loaded
2024-01-01 12:00:25 [INFO] Security scan completed - no threats detected
"#.to_string()),

            _ => {
                if file_path.starts_with('/') {
                    Err(format!("cat: {}: No such file or directory", file_path))
                } else {
                    Ok(format!("This is the content of file: {}\nA sample text file for demonstration.\nWith multiple lines of content.\n", file_path))
                }
            }
        }
    }

    /// Format content based on options
    fn format_content(&self, content: &str, options: &CatOptions, line_number: &mut usize) -> String {
        let mut output = String::new();
        let lines: Vec<&str> = content.lines().collect();
        let mut blank_line_count = 0;

        for line in lines {
            let is_blank = line.trim().is_empty();

            // Handle squeeze blank lines
            if options.squeeze_blank && is_blank {
                blank_line_count += 1;
                if blank_line_count > 1 {
                    continue;
                }
            } else {
                blank_line_count = 0;
            }

            let mut formatted_line = String::new();

            // Add line numbers
            if options.number_lines || (options.number_nonblank && !is_blank) {
                formatted_line.push_str(&format!("{:6}\t", line_number));
                *line_number += 1;
            }

            // Process line content
            let mut processed_line = line.to_string();

            // Show tabs
            if options.show_tabs {
                processed_line = processed_line.replace('\t', "^I");
            }

            // Show non-printing characters
            if options.show_nonprinting {
                processed_line = self.show_nonprinting_chars(&processed_line);
            }

            formatted_line.push_str(&processed_line);

            // Show line endings
            if options.show_ends {
                formatted_line.push('$');
            }

            formatted_line.push('\n');
            output.push_str(&formatted_line);
        }

        output
    }

    /// Convert non-printing characters to visible form
    fn show_nonprinting_chars(&self, line: &str) -> String {
        let mut result = String::new();
        
        for ch in line.chars() {
            match ch {
                '\x00'..='\x08' | '\x0B'..='\x1F' => {
                    result.push('^');
                    result.push((ch as u8 + b'@') as char);
                },
                '\x7F' => result.push_str("^?"),
                '\x80'..='\xFF' => {
                    result.push('M');
                    result.push('-');
                    let printable = ch as u8 & 0x7F;
                    if printable < 0x20 {
                        result.push('^');
                        result.push((printable + b'@') as char);
                    } else if printable == 0x7F {
                        result.push_str("^?");
                    } else {
                        result.push(printable as char);
                    }
                },
                _ => result.push(ch),
            }
        }
        
        result
    }

    /// Get help text
    fn get_help_text(&self) -> String {
        r#"Usage: cat [OPTION]... [FILE]...

DESCRIPTION:
    Concatenate and display file contents.

OPTIONS:
    -n, --number           Number all output lines
    -b, --number-nonblank  Number nonempty output lines
    -s, --squeeze-blank    Suppress repeated empty output lines
    -T, --show-tabs        Display TAB characters as ^I
    -E, --show-ends        Display $ at end of each line
    -A, --show-all         Equivalent to -vET
    -v, --show-nonprinting Display non-printing characters
    --help                 Show this help message

EXAMPLES:
    cat file.txt                Display file contents
    cat -n file.txt            Display with line numbers
    cat file1.txt file2.txt    Concatenate multiple files
    cat -A file.txt            Show all special characters

SECURITY FILES:
    /etc/passwd             System user accounts
    /proc/version           Kernel version information
    /proc/cpuinfo           CPU information
    /proc/meminfo           Memory usage information
    synos_config.yaml       SynOS configuration
    network_logs            Network activity logs

"#.to_string()
    }
}

/// CAT command options
#[derive(Debug, Default)]
struct CatOptions {
    number_lines: bool,
    number_nonblank: bool,
    squeeze_blank: bool,
    show_tabs: bool,
    show_ends: bool,
    show_nonprinting: bool,
    show_help: bool,
    files: Vec<String>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cat_basic() {
        let cat = CatCommand::new();
        let result = cat.execute(&["/etc/passwd".to_string()]);
        assert!(result.is_ok());
        
        let output = result.unwrap();
        assert!(output.contains("root:x:0:0"));
        assert!(output.contains("user:x:1000:1000"));
    }

    #[test]
    fn test_cat_with_line_numbers() {
        let cat = CatCommand::new();
        let result = cat.execute(&["-n".to_string(), "/etc/hosts".to_string()]);
        assert!(result.is_ok());
        
        let output = result.unwrap();
        assert!(output.contains("     1\t"));
        assert!(output.contains("127.0.0.1"));
    }

    #[test]
    fn test_cat_show_tabs() {
        let cat = CatCommand::new();
        // Test with show tabs option
        let result = cat.execute(&["-T".to_string(), "/etc/passwd".to_string()]);
        assert!(result.is_ok());
    }

    #[test]
    fn test_cat_nonexistent_file() {
        let cat = CatCommand::new();
        let result = cat.execute(&["/nonexistent/file".to_string()]);
        assert!(result.is_err());
        
        let error = result.unwrap_err();
        assert!(error.contains("No such file or directory"));
    }

    #[test]
    fn test_cat_multiple_files() {
        let cat = CatCommand::new();
        let result = cat.execute(&["/etc/passwd".to_string(), "/etc/hosts".to_string()]);
        assert!(result.is_ok());
        
        let output = result.unwrap();
        assert!(output.contains("root:x:0:0"));
        assert!(output.contains("127.0.0.1"));
    }

    #[test]
    fn test_nonprinting_chars() {
        let cat = CatCommand::new();
        let test_input = "hello\x01world\x7F";
        let result = cat.show_nonprinting_chars(test_input);
        assert_eq!(result, "hello^Aworld^?");
    }
}
