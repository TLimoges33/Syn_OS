#!/usr/bin/env python3
"""
Syn_OS Shell MCP Server
Provides secure shell command execution and system interaction capabilities
for development and testing environments.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent, Resource

# Security logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('syn-os-shell-mcp')

# Initialize MCP server
mcp = FastMCP("SynOS Shell MCP Server")

# Security configuration
ALLOWED_COMMANDS = {
    'ls', 'cat', 'grep', 'find', 'echo', 'pwd', 'whoami', 'date',
    'ps', 'top', 'df', 'du', 'free', 'uname', 'which', 'head', 'tail',
    'wc', 'sort', 'uniq', 'awk', 'sed', 'cut', 'tr', 'curl', 'wget',
    'git', 'cargo', 'python3', 'pip3', 'node', 'npm', 'make', 'cmake'
}

FORBIDDEN_COMMANDS = {
    'rm', 'rmdir', 'mv', 'cp', 'chmod', 'chown', 'sudo', 'su',
    'passwd', 'useradd', 'userdel', 'groupadd', 'groupdel',
    'systemctl', 'service', 'killall', 'pkill', 'kill'
}

MAX_OUTPUT_SIZE = 10000  # Maximum output size in characters
TIMEOUT_SECONDS = 30     # Command timeout

class SecureShellExecutor:
    """Secure shell command executor with safety restrictions"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.command_history = []
        
    def is_command_allowed(self, command: str) -> tuple[bool, str]:
        """Check if command is allowed for execution"""
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return False, "Empty command"
            
        base_cmd = cmd_parts[0]
        
        # Check forbidden commands
        if base_cmd in FORBIDDEN_COMMANDS:
            return False, f"Command '{base_cmd}' is forbidden for security reasons"
            
        # Check allowed commands
        if base_cmd not in ALLOWED_COMMANDS:
            return False, f"Command '{base_cmd}' is not in allowed list"
            
        # Check for dangerous patterns
        dangerous_patterns = ['>', '>>', '|', '&', ';', '$(', '`']
        for pattern in dangerous_patterns:
            if pattern in command:
                return False, f"Command contains dangerous pattern: {pattern}"
                
        return True, "Command allowed"
    
    async def execute_command(self, command: str, working_dir: str = None) -> Dict[str, Any]:
        """Execute shell command safely"""
        # Validate command
        allowed, reason = self.is_command_allowed(command)
        if not allowed:
            return {
                'success': False,
                'error': reason,
                'output': '',
                'stderr': '',
                'exit_code': -1,
                'timestamp': datetime.now().isoformat()
            }
        
        # Set working directory
        if working_dir:
            work_path = Path(working_dir)
            if not work_path.is_absolute():
                work_path = self.base_dir / work_path
        else:
            work_path = self.base_dir
            
        # Ensure we stay within allowed directories
        try:
            work_path = work_path.resolve()
            if not str(work_path).startswith(str(self.base_dir.resolve())):
                return {
                    'success': False,
                    'error': 'Working directory outside allowed base directory',
                    'output': '',
                    'stderr': '',
                    'exit_code': -1,
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Invalid working directory: {e}',
                'output': '',
                'stderr': '',
                'exit_code': -1,
                'timestamp': datetime.now().isoformat()
            }
        
        # Execute command
        try:
            logger.info(f"Executing command: {command} in {work_path}")
            
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=work_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=os.environ.copy()
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=TIMEOUT_SECONDS
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    'success': False,
                    'error': f'Command timed out after {TIMEOUT_SECONDS} seconds',
                    'output': '',
                    'stderr': '',
                    'exit_code': -1,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Decode output
            stdout_text = stdout.decode('utf-8', errors='replace')
            stderr_text = stderr.decode('utf-8', errors='replace')
            
            # Truncate output if too large
            if len(stdout_text) > MAX_OUTPUT_SIZE:
                stdout_text = stdout_text[:MAX_OUTPUT_SIZE] + "\n... (output truncated)"
            if len(stderr_text) > MAX_OUTPUT_SIZE:
                stderr_text = stderr_text[:MAX_OUTPUT_SIZE] + "\n... (error output truncated)"
            
            result = {
                'success': process.returncode == 0,
                'output': stdout_text,
                'stderr': stderr_text,
                'exit_code': process.returncode,
                'command': command,
                'working_dir': str(work_path),
                'timestamp': datetime.now().isoformat()
            }
            
            # Log execution
            self.command_history.append(result)
            logger.info(f"Command completed with exit code: {process.returncode}")
            
            return result
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': f'Execution error: {str(e)}',
                'output': '',
                'stderr': '',
                'exit_code': -1,
                'command': command,
                'working_dir': str(work_path),
                'timestamp': datetime.now().isoformat()
            }
            
            self.command_history.append(error_result)
            logger.error(f"Command execution failed: {e}")
            
            return error_result

# Initialize shell executor
shell_executor = SecureShellExecutor(base_dir=os.getenv('SYNOS_DIR', '/home/diablorain/Syn_OS'))

@mcp.tool()
async def execute_shell_command(command: str, working_directory: str = None) -> List[TextContent]:
    """
    Execute a shell command safely with security restrictions.
    
    Args:
        command: The shell command to execute
        working_directory: Optional working directory (relative to SYNOS_DIR)
    
    Returns:
        Command execution result with output, errors, and metadata
    """
    result = await shell_executor.execute_command(command, working_directory)
    
    # Format response
    if result['success']:
        response = f"✅ Command executed successfully\n"
        response += f"Command: {result['command']}\n"
        response += f"Working Directory: {result['working_dir']}\n"
        response += f"Exit Code: {result['exit_code']}\n\n"
        
        if result['output']:
            response += f"Output:\n{result['output']}\n"
        else:
            response += "No output\n"
            
        if result['stderr']:
            response += f"\nStderr:\n{result['stderr']}\n"
    else:
        response = f"❌ Command execution failed\n"
        response += f"Command: {command}\n"
        response += f"Error: {result.get('error', 'Unknown error')}\n"
        
        if result.get('stderr'):
            response += f"Stderr: {result['stderr']}\n"
    
    return [TextContent(type="text", text=response)]

@mcp.tool()
async def get_command_history() -> List[TextContent]:
    """
    Get the history of executed commands in this session.
    
    Returns:
        List of previously executed commands with their results
    """
    if not shell_executor.command_history:
        return [TextContent(type="text", text="No commands executed in this session.")]
    
    history_text = "📜 Command History:\n\n"
    for i, cmd in enumerate(shell_executor.command_history[-10:], 1):  # Last 10 commands
        status = "✅" if cmd['success'] else "❌"
        history_text += f"{i}. {status} {cmd['command']}\n"
        history_text += f"   Exit Code: {cmd['exit_code']}\n"
        history_text += f"   Time: {cmd['timestamp']}\n\n"
    
    return [TextContent(type="text", text=history_text)]

@mcp.tool()
async def get_allowed_commands() -> List[TextContent]:
    """
    Get the list of allowed shell commands for security reference.
    
    Returns:
        List of commands that are allowed for execution
    """
    allowed_text = "🔒 Security Policy - Allowed Commands:\n\n"
    allowed_text += "Allowed commands:\n"
    for cmd in sorted(ALLOWED_COMMANDS):
        allowed_text += f"  • {cmd}\n"
    
    allowed_text += "\nForbidden commands (for security):\n"
    for cmd in sorted(FORBIDDEN_COMMANDS):
        allowed_text += f"  ❌ {cmd}\n"
    
    allowed_text += f"\nAdditional restrictions:\n"
    allowed_text += f"  • Command timeout: {TIMEOUT_SECONDS} seconds\n"
    allowed_text += f"  • Maximum output size: {MAX_OUTPUT_SIZE} characters\n"
    allowed_text += f"  • No shell operators (>, |, &, ;, etc.)\n"
    allowed_text += f"  • Commands must stay within SYNOS_DIR\n"
    
    return [TextContent(type="text", text=allowed_text)]

@mcp.tool()
async def get_system_info() -> List[TextContent]:
    """
    Get basic system information safely.
    
    Returns:
        System information including OS, architecture, and environment details
    """
    info_commands = [
        ('Operating System', 'uname -a'),
        ('Current Directory', 'pwd'),
        ('Current User', 'whoami'),
        ('Date/Time', 'date'),
        ('Python Version', 'python3 --version'),
        ('Available Space', 'df -h .')
    ]
    
    info_text = "🖥️ System Information:\n\n"
    
    for label, cmd in info_commands:
        result = await shell_executor.execute_command(cmd)
        if result['success']:
            info_text += f"{label}: {result['output'].strip()}\n"
        else:
            info_text += f"{label}: (unavailable)\n"
    
    return [TextContent(type="text", text=info_text)]

if __name__ == "__main__":
    import mcp.server.stdio
    
    async def main():
        logger.info("Starting SynOS Shell MCP Server...")
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await mcp.run(read_stream, write_stream, mcp.create_initialization_options())
    
    asyncio.run(main())