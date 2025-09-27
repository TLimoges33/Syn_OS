//! # Command Parser for SynShell
//!
//! Advanced command parsing with support for pipes, redirection, and security context

use alloc::string::ToString;
use alloc::{string::String, vec::Vec};

/// Parsed command structure
#[derive(Debug, Clone)]
pub struct ParsedCommand {
    pub name: String,
    pub args: Vec<String>,
    pub command_type: CommandType,
    pub input_redirect: Option<String>,
    pub output_redirect: Option<String>,
    pub append_output: bool,
    pub background: bool,
    pub pipes: Vec<ParsedCommand>,
}

/// Command type classification
#[derive(Debug, Clone, PartialEq)]
pub enum CommandType {
    Builtin,  // Built-in shell commands
    External, // External executable commands
    Network,  // Network-specific commands
    Security, // Security-related commands
}

/// Command parser
#[derive(Debug)]
pub struct CommandParser {
    builtin_commands: Vec<&'static str>,
    network_commands: Vec<&'static str>,
    security_commands: Vec<&'static str>,
}

impl CommandParser {
    /// Create a new command parser
    pub fn new() -> Self {
        Self {
            builtin_commands: vec![
                "help", "exit", "cd", "pwd", "echo", "env", "export", "unset", "history", "clear",
                "which", "type", "alias", "unalias", "jobs", "bg", "fg", "kill", "set", "unset",
            ],
            network_commands: vec![
                "ping", "netstat", "ifconfig", "route", "tcpdump", "wget", "curl", "ssh", "scp",
                "ftp", "telnet", "nc", "nmap",
            ],
            security_commands: vec![
                "portscan",
                "netmon",
                "integrity",
                "loganalyze",
                "secaudit",
                "firewall",
                "ipscan",
                "vulnscan",
                "hashcheck",
                "encrypt",
                "decrypt",
                "keymanage",
                "certcheck",
            ],
        }
    }

    /// Parse a command line input
    pub fn parse(&self, input: &str) -> Result<ParsedCommand, super::ShellError> {
        let input = input.trim();
        if input.is_empty() {
            return Err(super::ShellError::ParseError("Empty command".to_string()));
        }

        // Handle pipes first
        if input.contains('|') {
            return self.parse_piped_command(input);
        }

        // Parse single command
        let mut tokens = self.tokenize(input)?;
        if tokens.is_empty() {
            return Err(super::ShellError::ParseError(
                "No command specified".to_string(),
            ));
        }

        let command_name = tokens.remove(0);
        let mut args = Vec::new();
        let mut input_redirect = None;
        let mut output_redirect = None;
        let mut append_output = false;
        let mut background = false;

        // Process remaining tokens
        let mut i = 0;
        while i < tokens.len() {
            match tokens[i].as_str() {
                "<" => {
                    // Input redirection
                    if i + 1 >= tokens.len() {
                        return Err(super::ShellError::ParseError(
                            "Missing input file for redirection".to_string(),
                        ));
                    }
                    input_redirect = Some(tokens[i + 1].clone());
                    i += 2;
                }
                ">" => {
                    // Output redirection (overwrite)
                    if i + 1 >= tokens.len() {
                        return Err(super::ShellError::ParseError(
                            "Missing output file for redirection".to_string(),
                        ));
                    }
                    output_redirect = Some(tokens[i + 1].clone());
                    append_output = false;
                    i += 2;
                }
                ">>" => {
                    // Output redirection (append)
                    if i + 1 >= tokens.len() {
                        return Err(super::ShellError::ParseError(
                            "Missing output file for redirection".to_string(),
                        ));
                    }
                    output_redirect = Some(tokens[i + 1].clone());
                    append_output = true;
                    i += 2;
                }
                "&" => {
                    // Background execution
                    background = true;
                    i += 1;
                }
                _ => {
                    // Regular argument
                    args.push(tokens[i].clone());
                    i += 1;
                }
            }
        }

        let command_type = self.classify_command(&command_name);

        Ok(ParsedCommand {
            name: command_name,
            args,
            command_type,
            input_redirect,
            output_redirect,
            append_output,
            background,
            pipes: Vec::new(),
        })
    }

    /// Parse piped commands
    fn parse_piped_command(&self, input: &str) -> Result<ParsedCommand, super::ShellError> {
        let pipe_parts: Vec<&str> = input.split('|').collect();
        if pipe_parts.len() < 2 {
            return Err(super::ShellError::ParseError(
                "Invalid pipe syntax".to_string(),
            ));
        }

        // Parse the first command
        let mut main_command = self.parse(pipe_parts[0].trim())?;

        // Parse remaining commands as pipes
        for part in &pipe_parts[1..] {
            let pipe_command = self.parse(part.trim())?;
            main_command.pipes.push(pipe_command);
        }

        Ok(main_command)
    }

    /// Tokenize input string
    fn tokenize(&self, input: &str) -> Result<Vec<String>, super::ShellError> {
        let mut tokens = Vec::new();
        let mut current_token = String::new();
        let mut in_quotes = false;
        let mut escape_next = false;
        let mut quote_char = '"';

        for ch in input.chars() {
            if escape_next {
                current_token.push(ch);
                escape_next = false;
                continue;
            }

            match ch {
                '\\' if in_quotes => {
                    escape_next = true;
                }
                '"' | '\'' => {
                    if !in_quotes {
                        in_quotes = true;
                        quote_char = ch;
                    } else if ch == quote_char {
                        in_quotes = false;
                    } else {
                        current_token.push(ch);
                    }
                }
                ' ' | '\t' => {
                    if in_quotes {
                        current_token.push(ch);
                    } else if !current_token.is_empty() {
                        tokens.push(current_token.clone());
                        current_token.clear();
                    }
                }
                '>' | '<' | '|' | '&' => {
                    if in_quotes {
                        current_token.push(ch);
                    } else {
                        // Handle special characters
                        if !current_token.is_empty() {
                            tokens.push(current_token.clone());
                            current_token.clear();
                        }

                        // Handle multi-character operators
                        if ch == '>' && tokens.last() == Some(&">".to_string()) {
                            tokens.pop();
                            tokens.push(">>".to_string());
                        } else {
                            tokens.push(ch.to_string());
                        }
                    }
                }
                _ => {
                    current_token.push(ch);
                }
            }
        }

        if in_quotes {
            return Err(super::ShellError::ParseError(
                "Unterminated quote".to_string(),
            ));
        }

        if !current_token.is_empty() {
            tokens.push(current_token);
        }

        Ok(tokens)
    }

    /// Classify command type
    fn classify_command(&self, command: &str) -> CommandType {
        if self.builtin_commands.contains(&command) {
            CommandType::Builtin
        } else if self.network_commands.contains(&command) {
            CommandType::Network
        } else if self.security_commands.contains(&command) {
            CommandType::Security
        } else {
            CommandType::External
        }
    }

    /// Expand variables in arguments
    pub fn expand_variables(
        &self,
        args: &[String],
        environment: &super::Environment,
    ) -> Vec<String> {
        args.iter()
            .map(|arg| self.expand_variable(arg, environment))
            .collect()
    }

    /// Expand a single variable
    fn expand_variable(&self, arg: &str, environment: &super::Environment) -> String {
        if arg.starts_with('$') {
            let var_name = &arg[1..];
            environment.get(var_name).unwrap_or_else(|| arg.to_string())
        } else {
            arg.to_string()
        }
    }

    /// Expand glob patterns (basic implementation)
    pub fn expand_globs(&self, args: &[String]) -> Vec<String> {
        let mut expanded = Vec::new();

        for arg in args {
            if arg.contains('*') || arg.contains('?') {
                // In a real implementation, we would scan the filesystem
                // For now, just return the pattern as-is
                expanded.push(arg.clone());
            } else {
                expanded.push(arg.clone());
            }
        }

        expanded
    }

    /// Validate command syntax
    pub fn validate_syntax(&self, command: &ParsedCommand) -> Result<(), super::ShellError> {
        // Check for invalid combinations
        if command.background && !command.pipes.is_empty() {
            return Err(super::ShellError::ParseError(
                "Cannot run piped commands in background".to_string(),
            ));
        }

        // Check redirection validity
        if let Some(ref input_file) = command.input_redirect {
            if input_file.is_empty() {
                return Err(super::ShellError::ParseError(
                    "Empty input redirection file".to_string(),
                ));
            }
        }

        if let Some(ref output_file) = command.output_redirect {
            if output_file.is_empty() {
                return Err(super::ShellError::ParseError(
                    "Empty output redirection file".to_string(),
                ));
            }
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_command_parsing() {
        let parser = CommandParser::new();
        let result = parser.parse("ls -la /tmp").unwrap();

        assert_eq!(result.name, "ls");
        assert_eq!(result.args, vec!["-la", "/tmp"]);
        assert_eq!(result.command_type, CommandType::External);
    }

    #[test]
    fn test_builtin_command_parsing() {
        let parser = CommandParser::new();
        let result = parser.parse("help").unwrap();

        assert_eq!(result.name, "help");
        assert_eq!(result.command_type, CommandType::Builtin);
    }

    #[test]
    fn test_network_command_parsing() {
        let parser = CommandParser::new();
        let result = parser.parse("ping 8.8.8.8").unwrap();

        assert_eq!(result.name, "ping");
        assert_eq!(result.args, vec!["8.8.8.8"]);
        assert_eq!(result.command_type, CommandType::Network);
    }

    #[test]
    fn test_redirection_parsing() {
        let parser = CommandParser::new();
        let result = parser.parse("ls > output.txt").unwrap();

        assert_eq!(result.name, "ls");
        assert_eq!(result.output_redirect, Some("output.txt".to_string()));
        assert!(!result.append_output);
    }

    #[test]
    fn test_pipe_parsing() {
        let parser = CommandParser::new();
        let result = parser.parse("ls -la | grep txt").unwrap();

        assert_eq!(result.name, "ls");
        assert_eq!(result.args, vec!["-la"]);
        assert_eq!(result.pipes.len(), 1);
        assert_eq!(result.pipes[0].name, "grep");
        assert_eq!(result.pipes[0].args, vec!["txt"]);
    }

    #[test]
    fn test_quoted_arguments() {
        let parser = CommandParser::new();
        let result = parser.parse(r#"echo "hello world" 'test string'"#).unwrap();

        assert_eq!(result.name, "echo");
        assert_eq!(result.args, vec!["hello world", "test string"]);
    }
}
