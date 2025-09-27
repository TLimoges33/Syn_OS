//! # Stub implementation of command history

use alloc::{string::String, vec::Vec};

#[derive(Debug)]
pub struct CommandHistory {
    commands: Vec<String>,
}

impl CommandHistory {
    pub fn new() -> Self {
        Self {
            commands: Vec::new(),
        }
    }

    pub fn add(&mut self, command: String) {
        self.commands.push(command);
    }

    pub fn add_command(&mut self, command: String) {
        self.add(command);
    }

    pub fn get_all(&self) -> &Vec<String> {
        &self.commands
    }

    pub fn get_last(&self) -> Option<&String> {
        self.commands.last()
    }
}
