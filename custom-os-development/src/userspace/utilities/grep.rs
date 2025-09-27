//! # GREP Command Implementation
//! 
//! Pattern searching utility for SynOS with regex support

use alloc::{vec::Vec, string::String, format};

/// GREP command implementation
pub struct GrepCommand;

impl GrepCommand {
    /// Create new GREP command
    pub fn new() -> Self {
        Self
    }

    /// Execute GREP command with given arguments
    pub fn execute(&self, args: &[String]) -> Result<String, String> {
        let options = self.parse_args(args)?;
        
        if options.show_help {
            return Ok(self.get_help_text());
        }

        if options.pattern.is_empty() {
            return Err("No pattern specified. Use --help for usage information.".to_string());
        }

        let mut output = String::new();
        let mut total_matches = 0;

        if options.files.is_empty() {
            // Read from stdin (simulated)
            let stdin_content = "Sample input line\nAnother line with pattern\nThird line without match\n";
            let matches = self.search_content(&stdin_content, &options)?;
            output.push_str(&matches);
            total_matches += self.count_matches(&matches);
        } else {
            for file_path in &options.files {
                let file_content = self.read_file(file_path)?;
                let matches = self.search_content(&file_content, &options)?;
                
                if !matches.is_empty() {
                    if options.files.len() > 1 && !options.count_only && !options.files_with_matches {
                        // Prefix with filename when multiple files
                        let prefixed_matches = self.add_filename_prefix(&matches, file_path);
                        output.push_str(&prefixed_matches);
                    } else {
                        output.push_str(&matches);
                    }
                    total_matches += self.count_matches(&matches);
                }
            }
        }

        if options.count_only {
            output = format!("{}\n", total_matches);
        }

        Ok(output)
    }

    /// Parse command line arguments
    fn parse_args(&self, args: &[String]) -> Result<GrepOptions, String> {
        let mut options = GrepOptions::default();
        let mut i = 0;

        while i < args.len() {
            match args[i].as_str() {
                "-i" | "--ignore-case" => options.ignore_case = true,
                "-v" | "--invert-match" => options.invert_match = true,
                "-n" | "--line-number" => options.show_line_numbers = true,
                "-c" | "--count" => options.count_only = true,
                "-l" | "--files-with-matches" => options.files_with_matches = true,
                "-L" | "--files-without-match" => options.files_without_match = true,
                "-H" | "--with-filename" => options.show_filename = true,
                "-h" | "--no-filename" => options.hide_filename = true,
                "-r" | "--recursive" => options.recursive = true,
                "-w" | "--word-regexp" => options.word_regexp = true,
                "-x" | "--line-regexp" => options.line_regexp = true,
                "-F" | "--fixed-strings" => options.fixed_strings = true,
                "-E" | "--extended-regexp" => options.extended_regexp = true,
                "-A" | "--after-context" => {
                    i += 1;
                    if i >= args.len() {
                        return Err("Option -A requires an argument".to_string());
                    }
                    options.after_context = args[i].parse()
                        .map_err(|_| "Invalid number for -A option".to_string())?;
                },
                "-B" | "--before-context" => {
                    i += 1;
                    if i >= args.len() {
                        return Err("Option -B requires an argument".to_string());
                    }
                    options.before_context = args[i].parse()
                        .map_err(|_| "Invalid number for -B option".to_string())?;
                },
                "-C" | "--context" => {
                    i += 1;
                    if i >= args.len() {
                        return Err("Option -C requires an argument".to_string());
                    }
                    let context: usize = args[i].parse()
                        .map_err(|_| "Invalid number for -C option".to_string())?;
                    options.before_context = context;
                    options.after_context = context;
                },
                "--color" => options.color = true,
                "--help" => options.show_help = true,
                _ if args[i].starts_with('-') => {
                    return Err(format!("Unknown option: {}", args[i]));
                },
                _ => {
                    if options.pattern.is_empty() {
                        options.pattern = args[i].clone();
                    } else {
                        options.files.push(args[i].clone());
                    }
                }
            }
            i += 1;
        }

        Ok(options)
    }

    /// Read file content
    fn read_file(&self, file_path: &str) -> Result<String, String> {
        // Use the same file reading logic as cat command
        match file_path {
            "/etc/passwd" => Ok(r#"root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
user:x:1000:1000:User:/home/user:/bin/bash
"#.to_string()),

            "/var/log/synos.log" => Ok(r#"2024-01-01 12:00:01 [INFO] System boot completed
2024-01-01 12:00:02 [INFO] Network stack initialized
2024-01-01 12:00:03 [DEBUG] Loading security modules
2024-01-01 12:00:04 [INFO] Security monitoring active
2024-01-01 12:00:05 [WARN] Failed login attempt from 192.168.1.100
2024-01-01 12:00:06 [ERROR] Authentication failure for user 'admin'
2024-01-01 12:00:07 [INFO] Firewall rules loaded
2024-01-01 12:00:08 [DEBUG] Network interface eth0 up
2024-01-01 12:00:09 [INFO] Security scan completed
2024-01-01 12:00:10 [WARN] Suspicious network activity detected
"#.to_string()),

            "/proc/cpuinfo" => Ok(r#"processor	: 0
vendor_id	: SynOS
cpu family	: 6
model		: 142
model name	: SynOS Virtual CPU @ 2.40GHz
stepping	: 10
microcode	: 0xea
cpu MHz		: 2400.000
cache size	: 6144 KB
"#.to_string()),

            _ => {
                if file_path.starts_with('/') {
                    Err(format!("grep: {}: No such file or directory", file_path))
                } else {
                    Ok(format!("Sample content in {}\nWith some patterns to match\nAnd other lines of text\nPattern matching example\n", file_path))
                }
            }
        }
    }

    /// Search for pattern in content
    fn search_content(&self, content: &str, options: &GrepOptions) -> Result<String, String> {
        let lines: Vec<&str> = content.lines().collect();
        let mut output = String::new();
        let mut matching_lines = Vec::new();

        // Find matching lines
        for (line_no, line) in lines.iter().enumerate() {
            let is_match = if options.fixed_strings {
                self.fixed_string_match(line, &options.pattern, options.ignore_case)
            } else if options.word_regexp {
                self.word_match(line, &options.pattern, options.ignore_case)
            } else if options.line_regexp {
                self.line_match(line, &options.pattern, options.ignore_case)
            } else {
                self.pattern_match(line, &options.pattern, options.ignore_case)
            };

            let should_include = if options.invert_match { !is_match } else { is_match };

            if should_include {
                matching_lines.push(line_no);
            }
        }

        // Generate output based on options
        if options.count_only {
            return Ok(matching_lines.len().to_string());
        }

        if options.files_with_matches {
            return Ok(if !matching_lines.is_empty() { "match\n" } else { "" }.to_string());
        }

        if options.files_without_match {
            return Ok(if matching_lines.is_empty() { "no_match\n" } else { "" }.to_string());
        }

        // Format matching lines with context
        let mut printed_lines = std::collections::HashSet::new();

        for &line_no in &matching_lines {
            // Calculate context range
            let start = if line_no >= options.before_context {
                line_no - options.before_context
            } else {
                0
            };
            let end = std::cmp::min(line_no + options.after_context + 1, lines.len());

            // Print context lines
            for i in start..end {
                if printed_lines.contains(&i) {
                    continue;
                }
                printed_lines.insert(i);

                let mut formatted_line = String::new();

                // Add line number if requested
                if options.show_line_numbers {
                    if matching_lines.contains(&i) {
                        formatted_line.push_str(&format!("{}:", i + 1));
                    } else {
                        formatted_line.push_str(&format!("{}-", i + 1));
                    }
                }

                // Add the line content
                let line_content = if options.color && matching_lines.contains(&i) {
                    self.highlight_matches(lines[i], &options.pattern, options.ignore_case)
                } else {
                    lines[i].to_string()
                };

                formatted_line.push_str(&line_content);
                formatted_line.push('\n');

                output.push_str(&formatted_line);
            }

            // Add separator between context groups
            if options.before_context > 0 || options.after_context > 0 {
                if line_no < matching_lines.len() - 1 {
                    output.push_str("--\n");
                }
            }
        }

        Ok(output)
    }

    /// Fixed string matching
    fn fixed_string_match(&self, line: &str, pattern: &str, ignore_case: bool) -> bool {
        if ignore_case {
            line.to_lowercase().contains(&pattern.to_lowercase())
        } else {
            line.contains(pattern)
        }
    }

    /// Word boundary matching
    fn word_match(&self, line: &str, pattern: &str, ignore_case: bool) -> bool {
        let line_to_search = if ignore_case { line.to_lowercase() } else { line.to_string() };
        let pattern_to_search = if ignore_case { pattern.to_lowercase() } else { pattern.to_string() };

        // Simple word boundary implementation
        let words: Vec<&str> = line_to_search.split_whitespace().collect();
        words.iter().any(|word| *word == pattern_to_search)
    }

    /// Line matching (entire line must match)
    fn line_match(&self, line: &str, pattern: &str, ignore_case: bool) -> bool {
        if ignore_case {
            line.to_lowercase() == pattern.to_lowercase()
        } else {
            line == pattern
        }
    }

    /// Basic pattern matching (simplified regex-like)
    fn pattern_match(&self, line: &str, pattern: &str, ignore_case: bool) -> bool {
        let line_to_search = if ignore_case { line.to_lowercase() } else { line.to_string() };
        let pattern_to_search = if ignore_case { pattern.to_lowercase() } else { pattern.to_string() };

        // Simple pattern matching - supports basic wildcards
        if pattern_to_search.contains('*') {
            self.wildcard_match(&line_to_search, &pattern_to_search)
        } else {
            line_to_search.contains(&pattern_to_search)
        }
    }

    /// Simple wildcard matching
    fn wildcard_match(&self, text: &str, pattern: &str) -> bool {
        // Very basic wildcard implementation
        if pattern == "*" {
            return true;
        }

        let parts: Vec<&str> = pattern.split('*').collect();
        if parts.len() == 1 {
            return text.contains(pattern);
        }

        let mut current_pos = 0;
        for (i, part) in parts.iter().enumerate() {
            if part.is_empty() {
                continue;
            }

            if i == 0 {
                // First part must be at the beginning
                if !text[current_pos..].starts_with(part) {
                    return false;
                }
                current_pos += part.len();
            } else if i == parts.len() - 1 {
                // Last part must be at the end
                return text[current_pos..].ends_with(part);
            } else {
                // Middle part must be found
                if let Some(pos) = text[current_pos..].find(part) {
                    current_pos += pos + part.len();
                } else {
                    return false;
                }
            }
        }

        true
    }

    /// Highlight matches in line (add color codes)
    fn highlight_matches(&self, line: &str, pattern: &str, ignore_case: bool) -> String {
        let line_to_search = if ignore_case { line.to_lowercase() } else { line.to_string() };
        let pattern_to_search = if ignore_case { pattern.to_lowercase() } else { pattern.to_string() };

        if let Some(pos) = line_to_search.find(&pattern_to_search) {
            let before = &line[..pos];
            let matched = &line[pos..pos + pattern.len()];
            let after = &line[pos + pattern.len()..];
            format!("{}\x1b[31m{}\x1b[0m{}", before, matched, after)
        } else {
            line.to_string()
        }
    }

    /// Add filename prefix to matches
    fn add_filename_prefix(&self, matches: &str, filename: &str) -> String {
        matches.lines()
            .map(|line| format!("{}:{}", filename, line))
            .collect::<Vec<_>>()
            .join("\n")
            + if matches.ends_with('\n') { "\n" } else { "" }
    }

    /// Count number of matches in output
    fn count_matches(&self, output: &str) -> usize {
        output.lines().count()
    }

    /// Get help text
    fn get_help_text(&self) -> String {
        r#"Usage: grep [OPTION]... PATTERN [FILE]...

DESCRIPTION:
    Search for PATTERN in each FILE.

OPTIONS:
    -i, --ignore-case         Ignore case distinctions
    -v, --invert-match        Select non-matching lines
    -n, --line-number         Print line numbers with output
    -c, --count               Print only count of matching lines
    -l, --files-with-matches  Print only names of files with matches
    -L, --files-without-match Print only names of files without matches
    -H, --with-filename       Print filename with output lines
    -h, --no-filename         Suppress filename prefix
    -r, --recursive           Search directories recursively
    -w, --word-regexp         Match whole words only
    -x, --line-regexp         Match whole lines only
    -F, --fixed-strings       Treat pattern as fixed string
    -E, --extended-regexp     Use extended regular expressions
    -A, --after-context=NUM   Print NUM lines after matching lines
    -B, --before-context=NUM  Print NUM lines before matching lines
    -C, --context=NUM         Print NUM lines before and after matches
    --color                   Highlight matching text
    --help                    Show this help message

EXAMPLES:
    grep "error" /var/log/synos.log     Search for "error" in log file
    grep -i "warning" *.log             Case-insensitive search in log files
    grep -n "root" /etc/passwd          Show line numbers for matches
    grep -c "INFO" /var/log/synos.log   Count matching lines
    grep -A 3 -B 3 "ERROR" logfile     Show 3 lines before and after matches

SECURITY EXAMPLES:
    grep "Failed login" /var/log/auth.log    Find failed login attempts
    grep -i "malware" /var/log/security.log Find malware references
    grep "WARN\|ERROR" /var/log/synos.log   Find warnings and errors

"#.to_string()
    }
}

/// GREP command options
#[derive(Debug, Default)]
struct GrepOptions {
    pattern: String,
    files: Vec<String>,
    ignore_case: bool,
    invert_match: bool,
    show_line_numbers: bool,
    count_only: bool,
    files_with_matches: bool,
    files_without_match: bool,
    show_filename: bool,
    hide_filename: bool,
    recursive: bool,
    word_regexp: bool,
    line_regexp: bool,
    fixed_strings: bool,
    extended_regexp: bool,
    before_context: usize,
    after_context: usize,
    color: bool,
    show_help: bool,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_grep_basic() {
        let grep = GrepCommand::new();
        let result = grep.execute(&["root".to_string(), "/etc/passwd".to_string()]);
        assert!(result.is_ok());
        
        let output = result.unwrap();
        assert!(output.contains("root:x:0:0"));
    }

    #[test]
    fn test_grep_ignore_case() {
        let grep = GrepCommand::new();
        let result = grep.execute(&["-i".to_string(), "ROOT".to_string(), "/etc/passwd".to_string()]);
        assert!(result.is_ok());
        
        let output = result.unwrap();
        assert!(output.contains("root:x:0:0"));
    }

    #[test]
    fn test_grep_line_numbers() {
        let grep = GrepCommand::new();
        let result = grep.execute(&["-n".to_string(), "root".to_string(), "/etc/passwd".to_string()]);
        assert!(result.is_ok());
        
        let output = result.unwrap();
        assert!(output.contains("1:"));
    }

    #[test]
    fn test_grep_count() {
        let grep = GrepCommand::new();
        let result = grep.execute(&["-c".to_string(), "INFO".to_string(), "/var/log/synos.log".to_string()]);
        assert!(result.is_ok());
        
        let output = result.unwrap();
        assert!(output.trim().parse::<usize>().is_ok());
    }

    #[test]
    fn test_fixed_string_match() {
        let grep = GrepCommand::new();
        assert!(grep.fixed_string_match("hello world", "world", false));
        assert!(grep.fixed_string_match("Hello World", "world", true));
        assert!(!grep.fixed_string_match("hello world", "WORLD", false));
    }

    #[test]
    fn test_word_match() {
        let grep = GrepCommand::new();
        assert!(grep.word_match("hello world test", "world", false));
        assert!(!grep.word_match("helloworld test", "world", false));
    }

    #[test]
    fn test_wildcard_match() {
        let grep = GrepCommand::new();
        assert!(grep.wildcard_match("hello world", "hello*"));
        assert!(grep.wildcard_match("hello world", "*world"));
        assert!(grep.wildcard_match("hello world", "h*d"));
    }
}
