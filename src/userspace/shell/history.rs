//! # Command History Management for SynShell
//! 
//! Command history with security auditing and analysis features

use alloc::{vec::Vec, string::String, collections::VecDeque};
use core::fmt;

/// Command history entry
#[derive(Debug, Clone)]
pub struct HistoryEntry {
    pub command: String,
    pub timestamp: u64,  // Unix timestamp
    pub execution_time: u32,  // Execution time in milliseconds
    pub exit_code: Option<i32>,
    pub working_directory: String,
    pub user_id: u32,
    pub security_level: String,
}

impl HistoryEntry {
    /// Create a new history entry
    pub fn new(command: String, user_id: u32, working_directory: String, security_level: String) -> Self {
        Self {
            command,
            timestamp: Self::current_timestamp(),
            execution_time: 0,
            exit_code: None,
            working_directory,
            user_id,
            security_level,
        }
    }

    /// Get current timestamp (stub implementation)
    fn current_timestamp() -> u64 {
        // In a real implementation, this would get the actual system time
        12345678900_u64
    }

    /// Mark command as completed with exit code
    pub fn complete(&mut self, exit_code: i32, execution_time: u32) {
        self.exit_code = Some(exit_code);
        self.execution_time = execution_time;
    }

    /// Check if this was a sensitive command
    pub fn is_sensitive(&self) -> bool {
        let sensitive_commands = [
            "sudo", "su", "passwd", "ssh", "scp", "ftp", "telnet",
            "portscan", "netmon", "tcpdump", "nmap", "vulnerability",
            "firewall", "iptables", "encrypt", "decrypt", "keymanage"
        ];

        let command_name = self.command.split_whitespace().next().unwrap_or("");
        sensitive_commands.contains(&command_name)
    }

    /// Check if this was a network command
    pub fn is_network_command(&self) -> bool {
        let network_commands = [
            "ping", "netstat", "ifconfig", "route", "tcpdump", "wget",
            "curl", "ssh", "scp", "ftp", "telnet", "nc", "nmap"
        ];

        let command_name = self.command.split_whitespace().next().unwrap_or("");
        network_commands.contains(&command_name)
    }

    /// Get command category for analysis
    pub fn get_category(&self) -> CommandCategory {
        let command_name = self.command.split_whitespace().next().unwrap_or("");
        
        match command_name {
            "cd" | "pwd" | "ls" | "cat" | "echo" | "cp" | "mv" | "rm" => CommandCategory::FileSystem,
            "ping" | "netstat" | "ifconfig" | "wget" | "curl" => CommandCategory::Network,
            "portscan" | "netmon" | "encrypt" | "firewall" => CommandCategory::Security,
            "ps" | "kill" | "top" | "jobs" | "bg" | "fg" => CommandCategory::Process,
            "help" | "history" | "which" | "type" => CommandCategory::Information,
            _ => CommandCategory::Other,
        }
    }
}

impl fmt::Display for HistoryEntry {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "[{}] {} ({}ms) -> {:?}", 
               self.timestamp, 
               self.command, 
               self.execution_time,
               self.exit_code.unwrap_or(-1))
    }
}

/// Command categories for analysis
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum CommandCategory {
    FileSystem,
    Network,
    Security,
    Process,
    Information,
    Other,
}

/// Command history manager
#[derive(Debug)]
pub struct CommandHistory {
    entries: VecDeque<HistoryEntry>,
    max_entries: usize,
    audit_enabled: bool,
    session_id: u32,
}

impl CommandHistory {
    /// Create a new command history
    pub fn new() -> Self {
        Self {
            entries: VecDeque::new(),
            max_entries: 1000,
            audit_enabled: true,
            session_id: Self::generate_session_id(),
        }
    }

    /// Create history with custom capacity
    pub fn with_capacity(max_entries: usize) -> Self {
        Self {
            entries: VecDeque::with_capacity(max_entries),
            max_entries,
            audit_enabled: true,
            session_id: Self::generate_session_id(),
        }
    }

    /// Generate a session ID
    fn generate_session_id() -> u32 {
        // In a real implementation, this would generate a unique session ID
        12345
    }

    /// Add a command to history
    pub fn add_command(&mut self, command: String) {
        // Don't add empty commands or commands starting with space (for privacy)
        if command.trim().is_empty() || command.starts_with(' ') {
            return;
        }

        let entry = HistoryEntry::new(
            command,
            1000, // Default user ID
            "/current/directory".to_string(),
            "USER".to_string(),
        );

        // Remove oldest entry if at capacity
        if self.entries.len() >= self.max_entries {
            self.entries.pop_front();
        }

        self.entries.push_back(entry);

        // Log sensitive commands if auditing is enabled
        if self.audit_enabled && self.entries.back().unwrap().is_sensitive() {
            self.log_security_event();
        }
    }

    /// Complete a command execution
    pub fn complete_last_command(&mut self, exit_code: i32, execution_time: u32) {
        if let Some(entry) = self.entries.back_mut() {
            entry.complete(exit_code, execution_time);
        }
    }

    /// Get command by index (0 = most recent)
    pub fn get_command(&self, index: usize) -> Option<&HistoryEntry> {
        if index < self.entries.len() {
            self.entries.get(self.entries.len() - 1 - index)
        } else {
            None
        }
    }

    /// Get all commands
    pub fn get_all_commands(&self) -> Vec<&HistoryEntry> {
        self.entries.iter().collect()
    }

    /// Search history by pattern
    pub fn search(&self, pattern: &str) -> Vec<&HistoryEntry> {
        self.entries.iter()
            .filter(|entry| entry.command.contains(pattern))
            .collect()
    }

    /// Get commands by category
    pub fn get_by_category(&self, category: CommandCategory) -> Vec<&HistoryEntry> {
        self.entries.iter()
            .filter(|entry| entry.get_category() == category)
            .collect()
    }

    /// Get recent commands (last n)
    pub fn get_recent(&self, count: usize) -> Vec<&HistoryEntry> {
        let start = if self.entries.len() > count {
            self.entries.len() - count
        } else {
            0
        };
        
        self.entries.range(start..).collect()
    }

    /// Get statistics about command usage
    pub fn get_statistics(&self) -> HistoryStatistics {
        let mut stats = HistoryStatistics::new();
        
        for entry in &self.entries {
            stats.total_commands += 1;
            
            if entry.is_sensitive() {
                stats.sensitive_commands += 1;
            }
            
            if entry.is_network_command() {
                stats.network_commands += 1;
            }
            
            if let Some(exit_code) = entry.exit_code {
                if exit_code == 0 {
                    stats.successful_commands += 1;
                } else {
                    stats.failed_commands += 1;
                }
            }
            
            stats.total_execution_time += entry.execution_time as u64;
            
            // Track command frequency
            let command_name = entry.command.split_whitespace().next().unwrap_or("").to_string();
            *stats.command_frequency.entry(command_name).or_insert(0) += 1;
        }
        
        stats
    }

    /// Clear all history
    pub fn clear(&mut self) {
        self.entries.clear();
        if self.audit_enabled {
            self.log_history_cleared();
        }
    }

    /// Export history to string format
    pub fn export_to_string(&self) -> String {
        let mut result = String::new();
        result.push_str(&format!("# SynShell History Export - Session {}\n", self.session_id));
        result.push_str("# Format: [timestamp] command (execution_time_ms) -> exit_code\n\n");
        
        for entry in &self.entries {
            result.push_str(&format!("{}\n", entry));
        }
        
        result
    }

    /// Import history from string format
    pub fn import_from_string(&mut self, data: &str) -> Result<usize, String> {
        let mut imported_count = 0;
        
        for line in data.lines() {
            if line.starts_with('#') || line.trim().is_empty() {
                continue;
            }
            
            // Simple parsing - in a real implementation, this would be more robust
            if let Some(bracket_end) = line.find(']') {
                if let Some(command_start) = line[bracket_end..].find(' ') {
                    let command_part = &line[bracket_end + command_start + 1..];
                    if let Some(paren_pos) = command_part.find(" (") {
                        let command = command_part[..paren_pos].to_string();
                        self.add_command(command);
                        imported_count += 1;
                    }
                }
            }
        }
        
        Ok(imported_count)
    }

    /// Enable/disable security auditing
    pub fn set_audit_enabled(&mut self, enabled: bool) {
        self.audit_enabled = enabled;
    }

    /// Log security event (stub implementation)
    fn log_security_event(&self) {
        // In a real implementation, this would log to security audit system
        println!("SECURITY AUDIT: Sensitive command executed in session {}", self.session_id);
    }

    /// Log history cleared event (stub implementation)
    fn log_history_cleared(&self) {
        // In a real implementation, this would log to security audit system
        println!("SECURITY AUDIT: Command history cleared in session {}", self.session_id);
    }

    /// Get history size
    pub fn len(&self) -> usize {
        self.entries.len()
    }

    /// Check if history is empty
    pub fn is_empty(&self) -> bool {
        self.entries.is_empty()
    }
}

/// History statistics for analysis
#[derive(Debug)]
pub struct HistoryStatistics {
    pub total_commands: usize,
    pub successful_commands: usize,
    pub failed_commands: usize,
    pub sensitive_commands: usize,
    pub network_commands: usize,
    pub total_execution_time: u64,
    pub command_frequency: alloc::collections::BTreeMap<String, usize>,
}

impl HistoryStatistics {
    fn new() -> Self {
        Self {
            total_commands: 0,
            successful_commands: 0,
            failed_commands: 0,
            sensitive_commands: 0,
            network_commands: 0,
            total_execution_time: 0,
            command_frequency: alloc::collections::BTreeMap::new(),
        }
    }

    /// Get average execution time
    pub fn average_execution_time(&self) -> f64 {
        if self.total_commands > 0 {
            self.total_execution_time as f64 / self.total_commands as f64
        } else {
            0.0
        }
    }

    /// Get success rate
    pub fn success_rate(&self) -> f64 {
        let total_completed = self.successful_commands + self.failed_commands;
        if total_completed > 0 {
            self.successful_commands as f64 / total_completed as f64 * 100.0
        } else {
            0.0
        }
    }

    /// Get most used commands
    pub fn most_used_commands(&self, limit: usize) -> Vec<(String, usize)> {
        let mut commands: Vec<_> = self.command_frequency.iter()
            .map(|(cmd, count)| (cmd.clone(), *count))
            .collect();
        
        commands.sort_by(|a, b| b.1.cmp(&a.1));
        commands.truncate(limit);
        commands
    }
}

impl fmt::Display for HistoryStatistics {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        writeln!(f, "📊 Command History Statistics")?;
        writeln!(f, "┌─────────────────────────────────────────┐")?;
        writeln!(f, "│ Total Commands:        {:8} │", self.total_commands)?;
        writeln!(f, "│ Successful:            {:8} │", self.successful_commands)?;
        writeln!(f, "│ Failed:                {:8} │", self.failed_commands)?;
        writeln!(f, "│ Sensitive:             {:8} │", self.sensitive_commands)?;
        writeln!(f, "│ Network:               {:8} │", self.network_commands)?;
        writeln!(f, "│ Success Rate:          {:7.1}% │", self.success_rate())?;
        writeln!(f, "│ Avg Execution Time:    {:7.1}ms │", self.average_execution_time())?;
        writeln!(f, "└─────────────────────────────────────────┘")?;
        
        if !self.command_frequency.is_empty() {
            writeln!(f, "\n🔝 Most Used Commands:")?;
            for (i, (cmd, count)) in self.most_used_commands(5).iter().enumerate() {
                writeln!(f, "   {}. {} ({})", i + 1, cmd, count)?;
            }
        }
        
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_history_basic_operations() {
        let mut history = CommandHistory::new();
        
        history.add_command("ls -la".to_string());
        history.add_command("cd /tmp".to_string());
        
        assert_eq!(history.len(), 2);
        assert_eq!(history.get_command(0).unwrap().command, "cd /tmp");
        assert_eq!(history.get_command(1).unwrap().command, "ls -la");
    }

    #[test]
    fn test_sensitive_command_detection() {
        let entry = HistoryEntry::new(
            "sudo rm -rf /".to_string(),
            1000,
            "/".to_string(),
            "ROOT".to_string(),
        );
        
        assert!(entry.is_sensitive());
    }

    #[test]
    fn test_history_search() {
        let mut history = CommandHistory::new();
        
        history.add_command("ls -la".to_string());
        history.add_command("cd /tmp".to_string());
        history.add_command("ls /home".to_string());
        
        let results = history.search("ls");
        assert_eq!(results.len(), 2);
    }

    #[test]
    fn test_command_categorization() {
        let fs_entry = HistoryEntry::new("ls -la".to_string(), 1000, "/".to_string(), "USER".to_string());
        let net_entry = HistoryEntry::new("ping 8.8.8.8".to_string(), 1000, "/".to_string(), "USER".to_string());
        
        assert_eq!(fs_entry.get_category(), CommandCategory::FileSystem);
        assert_eq!(net_entry.get_category(), CommandCategory::Network);
    }
}
