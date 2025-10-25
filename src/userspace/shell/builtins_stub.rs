//! # Stub implementation of built-in commands

use alloc::{string::{String, ToString}, format};
use crate::shell::{ShellResult, ShellError, SecurityContext};
use crate::parser_stub::ParsedCommand;

#[derive(Debug)]
pub struct BuiltinCommands;

impl BuiltinCommands {
    pub fn new() -> Self {
        Self
    }

    pub fn execute(
        &mut self,
        command: ParsedCommand,
        _environment: &mut crate::Environment,
        current_directory: &mut String,
        _security_context: &SecurityContext,
    ) -> Result<ShellResult, ShellError> {
        match command.name.as_str() {
            "help" => Ok(ShellResult::Success("Help: Available commands: help, exit, ls, cd, pwd".to_string())),
            "exit" => Ok(ShellResult::Exit(0)),
            "ls" => Ok(ShellResult::Success("Directory listing not implemented".to_string())),
            "cd" => {
                if let Some(path) = command.args.first() {
                    *current_directory = path.clone();
                    Ok(ShellResult::Success(format!("Changed directory to: {}", path)))
                } else {
                    Ok(ShellResult::Success("Changed to home directory".to_string()))
                }
            },
            "pwd" => Ok(ShellResult::Success(current_directory.clone())),
            _ => Err(ShellError::CommandNotFound(command.name))
        }
    }
}
