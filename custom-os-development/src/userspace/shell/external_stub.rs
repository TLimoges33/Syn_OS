//! # Stub implementation of external command manager

use alloc::{string::String, vec::Vec};
use crate::shell::{ShellResult, ShellError, SecurityContext};
use crate::parser_stub::ParsedCommand;

#[derive(Debug)]
pub struct ExternalCommandManager;

impl ExternalCommandManager {
    pub fn new() -> Self {
        Self
    }

    pub fn execute(
        &self,
        command: ParsedCommand,
        _environment: &crate::Environment,
        _security_context: &SecurityContext,
    ) -> Result<ShellResult, ShellError> {
        // Stub implementation - just report that external commands are not implemented
        Err(ShellError::CommandNotFound(command.name))
    }
}
