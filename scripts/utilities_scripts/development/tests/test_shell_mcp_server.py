"""
Unit tests for the Shell MCP Server.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from mcp_servers.shell_mcp_server import SecureShellExecutor, CommandResult

class TestSecureShellExecutor:
    """Test the SecureShellExecutor class."""
    
    @pytest.fixture
    async def executor(self):
        """Create a SecureShellExecutor instance for testing."""
        executor = SecureShellExecutor()
        await executor.initialize()
        yield executor
        await executor.shutdown()
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test executor initialization."""
        executor = SecureShellExecutor()
        assert not executor.initialized
        
        await executor.initialize()
        assert executor.initialized
        
        await executor.shutdown()
        assert not executor.initialized
    
    @pytest.mark.asyncio
    async def test_safe_command_execution(self, executor, sample_commands):
        """Test execution of safe commands."""
        for command in sample_commands:
            result = await executor.execute_command(command)
            assert isinstance(result, CommandResult)
            assert result.command == command
            assert result.success is True
            assert result.exit_code == 0
    
    @pytest.mark.asyncio
    async def test_restricted_command_blocking(self, executor, restricted_commands):
        """Test that restricted commands are blocked."""
        for command in restricted_commands:
            result = await executor.execute_command(command)
            assert isinstance(result, CommandResult)
            assert result.command == command
            assert result.success is False
            assert "Security violation" in result.error
    
    @pytest.mark.asyncio
    async def test_command_timeout(self, executor):
        """Test command timeout functionality."""
        # Test with a command that would run longer than timeout
        long_command = "sleep 10"
        
        with patch.object(executor, 'command_timeout', 1):
            result = await executor.execute_command(long_command)
            assert result.success is False
            assert "timeout" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_command_validation(self, executor):
        """Test command validation logic."""
        # Test empty command
        result = await executor.execute_command("")
        assert result.success is False
        assert "empty" in result.error.lower()
        
        # Test None command
        result = await executor.execute_command(None)
        assert result.success is False
        
        # Test very long command
        long_command = "a" * 10000
        result = await executor.execute_command(long_command)
        assert result.success is False
        assert "too long" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_concurrent_execution(self, executor):
        """Test concurrent command execution."""
        commands = ["echo 'test1'", "echo 'test2'", "echo 'test3'"]
        
        # Execute commands concurrently
        tasks = [executor.execute_command(cmd) for cmd in commands]
        results = await asyncio.gather(*tasks)
        
        # Verify all commands executed successfully
        for result in results:
            assert result.success is True
            assert result.exit_code == 0
    
    @pytest.mark.asyncio
    async def test_security_audit_logging(self, executor):
        """Test that security violations are properly logged."""
        with patch('mcp_servers.shell_mcp_server.logger') as mock_logger:
            result = await executor.execute_command("rm -rf /")
            
            assert result.success is False
            mock_logger.warning.assert_called()
    
    @pytest.mark.asyncio
    async def test_command_result_serialization(self, executor):
        """Test CommandResult serialization."""
        result = await executor.execute_command("echo 'test'")
        
        # Test dict conversion
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert 'command' in result_dict
        assert 'success' in result_dict
        assert 'stdout' in result_dict
        
        # Test JSON serialization
        import json
        json_str = json.dumps(result_dict)
        assert isinstance(json_str, str)
        
        # Test deserialization
        restored_dict = json.loads(json_str)
        assert restored_dict == result_dict

class TestMCPIntegration:
    """Test MCP protocol integration."""
    
    @pytest.mark.asyncio
    async def test_mcp_server_startup(self):
        """Test MCP server can start up properly."""
        from mcp_servers.shell_mcp_server import main
        
        # Mock the server run to avoid actually starting it
        with patch('fastmcp.Server.run') as mock_run:
            with patch('sys.argv', ['shell_mcp_server.py']):
                # This should not raise an exception
                try:
                    main()
                except SystemExit:
                    pass  # Expected when mocking
                
                mock_run.assert_called_once()
    
    @pytest.mark.asyncio 
    async def test_tool_registration(self):
        """Test that MCP tools are properly registered."""
        from mcp_servers.shell_mcp_server import app
        
        # Check that tools are registered
        tools = app.list_tools()
        tool_names = [tool.name for tool in tools]
        
        assert 'execute_shell_command' in tool_names
        assert 'list_safe_commands' in tool_names
    
    @pytest.mark.asyncio
    async def test_tool_execution(self):
        """Test MCP tool execution."""
        from mcp_servers.shell_mcp_server import execute_shell_command
        
        # Test safe command execution through MCP
        result = await execute_shell_command("echo 'Hello MCP'")
        assert "Hello MCP" in result
        
        # Test restricted command through MCP
        result = await execute_shell_command("rm -rf /")
        assert "Security violation" in result
