//! Bridge between SynShell (no_std) and UniversalCommand (std)
//!
//! This module provides a compatibility layer that allows the no_std shell
//! to communicate with the std-based universal command system through
//! message passing or system calls.

use alloc::{string::{String, ToString}, vec::Vec, format};
use crate::shell::ShellError;

/// Universal Command execution request
#[derive(Debug, Clone)]
pub struct UniversalCommandRequest {
    pub natural_language_input: String,
    pub context: CommandContext,
}

/// Execution context for universal commands
#[derive(Debug, Clone)]
pub struct CommandContext {
    pub current_directory: String,
    pub user_id: u32,
    pub privilege_level: String,
}

/// Result from universal command execution
#[derive(Debug, Clone)]
pub struct UniversalCommandResponse {
    pub success: bool,
    pub output: String,
    pub tools_used: Vec<String>,
    pub execution_time_ms: u64,
}

/// Bridge interface for Universal Command integration
///
/// In a full implementation, this would:
/// 1. Serialize the request
/// 2. Send to userspace daemon via IPC/syscall
/// 3. Receive response
/// 4. Deserialize and return
#[derive(Debug)]
pub struct UniversalCommandBridge {
    /// Track if the universal command daemon is available
    daemon_available: bool,
}

impl UniversalCommandBridge {
    /// Create a new bridge instance
    pub fn new() -> Self {
        Self {
            daemon_available: false, // Will be true when daemon is running
        }
    }

    /// Check if universal command system is available
    pub fn is_available(&self) -> bool {
        self.daemon_available
    }

    /// Execute a natural language command through the universal command system
    ///
    /// This is a no_std-compatible interface that would communicate with
    /// the std-based universal command daemon in userspace.
    pub fn execute_natural_language(
        &self,
        input: &str,
        context: CommandContext,
    ) -> Result<UniversalCommandResponse, ShellError> {
        if !self.daemon_available {
            return Err(ShellError::SystemError(
                "Universal Command daemon not available".to_string()
            ));
        }

        // In a full implementation:
        // 1. Create request structure
        // 2. Serialize to bytes
        // 3. Send via syscall/IPC to userspace daemon
        // 4. Wait for response
        // 5. Deserialize response
        // 6. Return result

        // For now, return a stub response indicating the integration point
        Ok(UniversalCommandResponse {
            success: true,
            output: format!(
                "Universal Command would process: {}\n\
                (Integration point established - daemon implementation pending)",
                input
            ),
            tools_used: Vec::new(),
            execution_time_ms: 0,
        })
    }

    /// Try to activate the universal command daemon
    pub fn activate_daemon(&mut self) -> Result<(), ShellError> {
        // In a full implementation, this would:
        // 1. Check if daemon is already running
        // 2. If not, spawn the daemon process
        // 3. Establish IPC connection
        // 4. Verify daemon is responsive

        self.daemon_available = true;
        Ok(())
    }

    /// Parse natural language intent (local, no daemon needed)
    pub fn parse_intent(&self, input: &str) -> Result<ParsedIntent, ShellError> {
        // Basic keyword matching for common intents
        let input_lower = input.to_lowercase();

        if input_lower.contains("scan") {
            Ok(ParsedIntent::Scan {
                target: extract_target(&input_lower),
                scan_type: ScanType::Port,
            })
        } else if input_lower.contains("enumerate") {
            Ok(ParsedIntent::Enumerate {
                target: extract_target(&input_lower),
            })
        } else if input_lower.contains("exploit") {
            Ok(ParsedIntent::Exploit {
                target: extract_target(&input_lower),
                vulnerability: None,
            })
        } else if input_lower.contains("report") {
            Ok(ParsedIntent::GenerateReport {
                format: ReportFormat::Markdown,
            })
        } else {
            Ok(ParsedIntent::Unknown {
                raw_input: input.to_string(),
            })
        }
    }

    /// Suggest tools based on intent
    pub fn suggest_tools(&self, intent: &ParsedIntent) -> Vec<String> {
        match intent {
            ParsedIntent::Scan { scan_type, .. } => match scan_type {
                ScanType::Port => alloc::vec!["nmap".to_string(), "masscan".to_string()],
                ScanType::Vulnerability => alloc::vec!["nessus".to_string(), "openvas".to_string()],
                ScanType::Network => alloc::vec!["nmap".to_string(), "netdiscover".to_string()],
            },
            ParsedIntent::Enumerate { .. } => {
                alloc::vec!["enum4linux".to_string(), "gobuster".to_string(), "ffuf".to_string()]
            }
            ParsedIntent::Exploit { .. } => {
                alloc::vec!["metasploit".to_string(), "searchsploit".to_string()]
            }
            ParsedIntent::GenerateReport { .. } => {
                alloc::vec!["faraday".to_string(), "dradis".to_string()]
            }
            ParsedIntent::Unknown { .. } => Vec::new(),
        }
    }
}

/// Parsed intent from natural language
#[derive(Debug, Clone)]
pub enum ParsedIntent {
    Scan {
        target: Option<String>,
        scan_type: ScanType,
    },
    Enumerate {
        target: Option<String>,
    },
    Exploit {
        target: Option<String>,
        vulnerability: Option<String>,
    },
    GenerateReport {
        format: ReportFormat,
    },
    Unknown {
        raw_input: String,
    },
}

/// Type of scan to perform
#[derive(Debug, Clone, Copy)]
pub enum ScanType {
    Port,
    Vulnerability,
    Network,
}

/// Report format options
#[derive(Debug, Clone, Copy)]
pub enum ReportFormat {
    Markdown,
    Html,
    Pdf,
    Json,
}

/// Helper function to extract target from input
fn extract_target(input: &str) -> Option<String> {
    // Simple regex-like extraction for IP addresses or hostnames
    let words: Vec<&str> = input.split_whitespace().collect();

    for word in words {
        // Check if looks like an IP address
        if word.contains('.') && word.split('.').count() == 4 {
            return Some(word.to_string());
        }
        // Check if looks like a hostname
        if word.contains('.') && word.len() > 3 {
            return Some(word.to_string());
        }
    }

    None
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_intent_parsing() {
        let bridge = UniversalCommandBridge::new();

        let intent = bridge.parse_intent("scan 192.168.1.1").unwrap();
        match intent {
            ParsedIntent::Scan { target, .. } => {
                assert_eq!(target, Some("192.168.1.1".to_string()));
            }
            _ => panic!("Expected Scan intent"),
        }
    }

    #[test]
    fn test_tool_suggestions() {
        let bridge = UniversalCommandBridge::new();
        let intent = ParsedIntent::Scan {
            target: Some("192.168.1.1".to_string()),
            scan_type: ScanType::Port,
        };

        let tools = bridge.suggest_tools(&intent);
        assert!(tools.contains(&"nmap".to_string()));
    }
}
