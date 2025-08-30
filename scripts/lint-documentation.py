#!/usr/bin/env python3
"""
Documentation Linter and Fixer
Checks and fixes markdown lint issues across all documentation files
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Tuple

# Setup logging
log_dir = Path("/home/diablorain/Syn_OS/logs/docs")
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "documentation_linter.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DocumentationLinter:
    """Comprehensive documentation linter and fixer"""
    
    def __init__(self, base_dir: str = "/home/diablorain/Syn_OS"):
        self.base_dir = Path(base_dir)
        self.issues_found = 0
        self.issues_fixed = 0
        self.files_processed = 0
        
        # Markdown lint rules
        self.lint_rules = {
            "MD041": self.fix_missing_h1,
            "MD022": self.fix_headers_spacing,
            "MD032": self.fix_list_spacing,
            "MD036": self.fix_emphasis_instead_of_header,
            "MD009": self.fix_trailing_whitespace,
            "MD031": self.fix_fenced_code_blocks,
            "MD025": self.fix_multiple_h1,
            "MD012": self.fix_multiple_blank_lines,
            "MD013": self.fix_line_length,
            "MD029": self.fix_ordered_list_prefix,
            "MD030": self.fix_list_marker_space,
            "MD033": self.fix_inline_html,
            "MD040": self.fix_fenced_code_language
        }
    
    def find_markdown_files(self) -> List[Path]:
        """Find all markdown files in the project"""
        markdown_files = []
        
        # Search for .md files
        for md_file in self.base_dir.rglob("*.md"):
            # Skip some directories
            skip_dirs = [".git", "node_modules", "__pycache__", ".pytest_cache"]
            if not any(skip_dir in str(md_file) for skip_dir in skip_dirs):
                markdown_files.append(md_file)
        
        logger.info(f"Found {len(markdown_files)} markdown files")
        return markdown_files
    
    def fix_missing_h1(self, content: str, file_path: Path) -> str:
        """Fix MD041: First line in file should be a top level header"""
        lines = content.split('\n')
        
        if not lines or not lines[0].strip():
            return content
        
        # Check if first non-empty line is already an H1
        for i, line in enumerate(lines):
            if line.strip():
                if line.startswith('# '):
                    return content  # Already has H1
                
                # Add H1 based on filename
                filename = file_path.stem.replace('_', ' ').replace('-', ' ').title()
                lines.insert(i, f"# {filename}")
                lines.insert(i + 1, "")
                self.issues_fixed += 1
                return '\n'.join(lines)
        
        return content
    
    def fix_headers_spacing(self, content: str, file_path: Path) -> str:
        """Fix MD022: Headers should be surrounded by blank lines"""
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            if re.match(r'^#{1,6}\s+', line):
                # This is a header
                prev_line = lines[i - 1] if i > 0 else ""
                next_line = lines[i + 1] if i < len(lines) - 1 else ""
                
                # Add blank line before header if needed
                if i > 0 and prev_line.strip() and not prev_line.startswith('#'):
                    new_lines.append("")
                
                new_lines.append(line)
                
                # Add blank line after header if needed
                if next_line.strip() and not next_line.startswith('#'):
                    new_lines.append("")
                    self.issues_fixed += 1
            else:
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def fix_list_spacing(self, content: str, file_path: Path) -> str:
        """Fix MD032: Lists should be surrounded by blank lines"""
        lines = content.split('\n')
        new_lines = []
        in_list = False
        
        for i, line in enumerate(lines):
            is_list_item = bool(re.match(r'^[\s]*[-*+]\s+|^[\s]*\d+\.\s+', line))
            
            if is_list_item and not in_list:
                # Starting a list - add blank line before if needed
                prev_line = lines[i - 1] if i > 0 else ""
                if prev_line.strip() and not re.match(r'^[\s]*[-*+]\s+|^[\s]*\d+\.\s+', prev_line):
                    new_lines.append("")
                in_list = True
                self.issues_fixed += 1
            elif not is_list_item and in_list:
                # Ending a list - add blank line after previous item
                if line.strip():
                    new_lines.append("")
                in_list = False
                self.issues_fixed += 1
            
            new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def fix_emphasis_instead_of_header(self, content: str, file_path: Path) -> str:
        """Fix MD036: Emphasis used instead of a header"""
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            # Look for lines that are only bold/italic and might be headers
            if re.match(r'^\*\*[^*]+\*\*$|^__[^_]+__$', line.strip()):
                # Convert to header
                text = re.sub(r'^\*\*([^*]+)\*\*$|^__([^_]+)__$', r'\1\2', line.strip())
                new_lines.append(f"## {text}")
                self.issues_fixed += 1
            else:
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def fix_trailing_whitespace(self, content: str, file_path: Path) -> str:
        """Fix MD009: Trailing spaces"""
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            stripped_line = line.rstrip()
            if len(stripped_line) != len(line):
                self.issues_fixed += 1
            new_lines.append(stripped_line)
        
        return '\n'.join(new_lines)
    
    def fix_fenced_code_blocks(self, content: str, file_path: Path) -> str:
        """Fix MD031: Fenced code blocks should be surrounded by blank lines"""
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            if line.strip().startswith('```'):
                # Add blank line before code block
                prev_line = lines[i - 1] if i > 0 else ""
                if prev_line.strip() and i > 0:
                    new_lines.append("")
                
                new_lines.append(line)
                
                # Find end of code block
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith('```'):
                    j += 1
                
                # Add the code content
                for k in range(i + 1, min(j + 1, len(lines))):
                    new_lines.append(lines[k])
                
                # Add blank line after code block
                next_line = lines[j + 1] if j + 1 < len(lines) else ""
                if next_line.strip():
                    new_lines.append("")
                
                self.issues_fixed += 1
                # Skip processed lines
                i = j
            elif not any(line.strip().startswith('```') for line in lines[max(0, i-5):i]):
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def fix_multiple_h1(self, content: str, file_path: Path) -> str:
        """Fix MD025: Multiple top level headers in the same document"""
        lines = content.split('\n')
        h1_count = 0
        new_lines = []
        
        for line in lines:
            if re.match(r'^#\s+', line):
                h1_count += 1
                if h1_count > 1:
                    # Convert additional H1s to H2s
                    new_lines.append(line.replace('# ', '## ', 1))
                    self.issues_fixed += 1
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def fix_multiple_blank_lines(self, content: str, file_path: Path) -> str:
        """Fix MD012: Multiple consecutive blank lines"""
        # Replace multiple consecutive blank lines with single blank line
        fixed_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        if fixed_content != content:
            self.issues_fixed += 1
        return fixed_content
    
    def fix_line_length(self, content: str, file_path: Path) -> str:
        """Fix MD013: Line length (simplified - only for very long lines)"""
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            # Only break extremely long lines (>200 chars)
            if len(line) > 200 and not line.strip().startswith('http'):
                # Simple word wrap
                words = line.split()
                current_line = ""
                
                for word in words:
                    if len(current_line + " " + word) > 120:
                        new_lines.append(current_line.strip())
                        current_line = word
                    else:
                        current_line += " " + word if current_line else word
                
                if current_line:
                    new_lines.append(current_line.strip())
                
                self.issues_fixed += 1
            else:
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def fix_ordered_list_prefix(self, content: str, file_path: Path) -> str:
        """Fix MD029: Ordered list item prefix"""
        lines = content.split('\n')
        new_lines = []
        list_counter = 1
        
        for line in lines:
            if re.match(r'^[\s]*\d+\.\s+', line):
                # Fix ordered list numbering
                indent = len(line) - len(line.lstrip())
                content_part = re.sub(r'^\d+\.\s+', '', line.strip())
                new_lines.append(' ' * indent + f"{list_counter}. {content_part}")
                list_counter += 1
                self.issues_fixed += 1
            else:
                if not re.match(r'^[\s]*[-*+]\s+', line) and line.strip():
                    list_counter = 1  # Reset counter when not in list
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def fix_list_marker_space(self, content: str, file_path: Path) -> str:
        """Fix MD030: Spaces after list markers"""
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            # Fix unordered lists
            if re.match(r'^[\s]*[-*+][\s]*[^\s]', line):
                fixed_line = re.sub(r'^([\s]*[-*+])[\s]*', r'\1 ', line)
                if fixed_line != line:
                    self.issues_fixed += 1
                new_lines.append(fixed_line)
            # Fix ordered lists
            elif re.match(r'^[\s]*\d+\.[\s]*[^\s]', line):
                fixed_line = re.sub(r'^([\s]*\d+\.)[\s]*', r'\1 ', line)
                if fixed_line != line:
                    self.issues_fixed += 1
                new_lines.append(fixed_line)
            else:
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def fix_inline_html(self, content: str, file_path: Path) -> str:
        """Fix MD033: Inline HTML (simplified - only common cases)"""
        # Convert common HTML tags to markdown
        replacements = [
            (r'<br\s*/?>', '\n'),
            (r'<strong>(.*?)</strong>', r'**\1**'),
            (r'<b>(.*?)</b>', r'**\1**'),
            (r'<em>(.*?)</em>', r'*\1*'),
            (r'<i>(.*?)</i>', r'*\1*'),
        ]
        
        fixed_content = content
        for pattern, replacement in replacements:
            new_content = re.sub(pattern, replacement, fixed_content, flags=re.IGNORECASE)
            if new_content != fixed_content:
                self.issues_fixed += 1
            fixed_content = new_content
        
        return fixed_content
    
    def fix_fenced_code_language(self, content: str, file_path: Path) -> str:
        """Fix MD040: Fenced code blocks should have a language specified"""
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            if line.strip() == '```':
                # Add a default language based on context
                new_lines.append('```text')
                self.issues_fixed += 1
            else:
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def lint_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Lint and fix a single markdown file"""
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply all lint rules
            for rule_name, rule_func in self.lint_rules.items():
                content = rule_func(content, file_path)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"✅ Fixed issues in {file_path.relative_to(self.base_dir)}")
                return True, []
            
            return False, []
            
        except Exception as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            logger.error(error_msg)
            return False, [error_msg]
    
    def lint_all_files(self) -> Dict[str, any]:
        """Lint all markdown files in the project"""
        logger.info("🔍 Starting documentation linting...")
        
        markdown_files = self.find_markdown_files()
        files_with_fixes = []
        errors = []
        
        for file_path in markdown_files:
            self.files_processed += 1
            has_fixes, file_errors = self.lint_file(file_path)
            
            if has_fixes:
                files_with_fixes.append(str(file_path.relative_to(self.base_dir)))
            
            if file_errors:
                errors.extend(file_errors)
        
        # Generate report
        report = {
            "files_processed": self.files_processed,
            "files_with_fixes": len(files_with_fixes),
            "issues_fixed": self.issues_fixed,
            "files_fixed": files_with_fixes,
            "errors": errors,
            "success_rate": (self.files_processed - len(errors)) / self.files_processed * 100 if self.files_processed > 0 else 0
        }
        
        logger.info(f"📊 Documentation Linting Complete")
        logger.info(f"   Files Processed: {self.files_processed}")
        logger.info(f"   Files Fixed: {len(files_with_fixes)}")
        logger.info(f"   Issues Fixed: {self.issues_fixed}")
        logger.info(f"   Success Rate: {report['success_rate']:.1f}%")
        
        return report

def main():
    """Main documentation linter entry point"""
    linter = DocumentationLinter()
    report = linter.lint_all_files()
    
    # Write report
    report_file = Path("/home/diablorain/Syn_OS/logs/docs/documentation_lint_report.json")
    import json
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"📄 Report saved to: {report_file}")
    
    # Return success if no errors
    return len(report['errors']) == 0

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
