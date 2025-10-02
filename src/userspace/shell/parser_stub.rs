//! # Stub implementation of command parser

use alloc::{string::{String, ToString}, vec::Vec};
use crate::shell::{ShellError};

#[derive(Debug, Clone)]
pub struct ParsedCommand {
    pub name: String,
    pub args: Vec<String>,
    pub command_type: ShellCommandType,
}

#[derive(Debug, Clone)]
pub enum ShellCommandType {
    Builtin,
    External,
    Network,
    Security,
}

#[derive(Debug)]
pub struct CommandParser;

impl CommandParser {
    pub fn new() -> Self {
        Self
    }

    pub fn parse(&self, input: &str) -> Result<ParsedCommand, ShellError> {
        let parts: Vec<&str> = input.split_whitespace().collect();
        if parts.is_empty() {
            return Err(ShellError::InvalidCommand("Empty command".to_string()));
        }

        let name = parts[0].to_string();
        let args = parts[1..].iter().map(|s| s.to_string()).collect();

        let command_type = match name.as_str() {
            "help" | "exit" | "ls" | "cd" | "pwd" => ShellCommandType::Builtin,
            "ping" | "netstat" | "ifconfig" | "tcpdump" | "portscan" | "netmon" => ShellCommandType::Network,
            "integrity" | "loganalyze" => ShellCommandType::Security,
            _ => ShellCommandType::External,
        };

        Ok(ParsedCommand {
            name,
            args,
            command_type,
        })
    }
}
