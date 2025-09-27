"""
Unit tests for the Test Simple MCP Server.
"""
import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from mcp_servers.test_simple_mcp_server import TestRunner, TestResult

class TestTestRunner:
    """Test the TestRunner class."""
    
    @pytest.fixture
    async def test_runner(self):
        """Create a TestRunner instance for testing."""
        runner = TestRunner()
        await runner.initialize()
        yield runner
        await runner.shutdown()
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test runner initialization."""
        runner = TestRunner()
        assert not runner.initialized
        
        await runner.initialize()
        assert runner.initialized
        
        await runner.shutdown()
        assert not runner.initialized
    
    @pytest.mark.asyncio
    async def test_connectivity_test(self, test_runner):
        """Test basic connectivity functionality."""
        result = await test_runner.run_connectivity_test()
        
        assert isinstance(result, TestResult)
        assert result.test_name == "connectivity_test"
        assert result.success is True
        assert result.duration > 0
    
    @pytest.mark.asyncio
    async def test_performance_benchmark(self, test_runner):
        """Test performance benchmarking."""
        result = await test_runner.run_performance_test()
        
        assert isinstance(result, TestResult)
        assert result.test_name == "performance_test"
        assert result.success is True
        assert "operations_per_second" in result.metrics
        assert result.metrics["operations_per_second"] > 0
    
    @pytest.mark.asyncio
    async def test_system_validation(self, test_runner):
        """Test system validation functionality."""
        result = await test_runner.run_system_validation()
        
        assert isinstance(result, TestResult)
        assert result.test_name == "system_validation"
        assert result.success is True
        assert "system_info" in result.data
    
    @pytest.mark.asyncio
    async def test_json_validation(self, test_runner):
        """Test JSON validation functionality."""
        valid_json = {"test": "data", "number": 42}
        invalid_json = "invalid json string"
        
        # Test valid JSON
        result = await test_runner.validate_json_data(json.dumps(valid_json))
        assert result.success is True
        assert result.data == valid_json
        
        # Test invalid JSON
        result = await test_runner.validate_json_data(invalid_json)
        assert result.success is False
        assert "JSON parsing failed" in result.error
    
    @pytest.mark.asyncio
    async def test_stress_testing(self, test_runner):
        """Test stress testing functionality."""
        result = await test_runner.run_stress_test(iterations=10)
        
        assert isinstance(result, TestResult)
        assert result.test_name == "stress_test"
        assert result.success is True
        assert result.metrics["total_iterations"] == 10
        assert result.metrics["success_rate"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_concurrent_testing(self, test_runner):
        """Test concurrent test execution."""
        test_methods = [
            test_runner.run_connectivity_test,
            test_runner.run_performance_test,
            test_runner.run_system_validation
        ]
        
        # Execute tests concurrently
        tasks = [method() for method in test_methods]
        results = await asyncio.gather(*tasks)
        
        # Verify all tests completed successfully
        for result in results:
            assert isinstance(result, TestResult)
            assert result.success is True
    
    @pytest.mark.asyncio
    async def test_error_handling(self, test_runner):
        """Test error handling in various scenarios."""
        # Test with invalid test parameters
        with patch.object(test_runner, '_run_operations', side_effect=Exception("Test error")):
            result = await test_runner.run_performance_test()
            assert result.success is False
            assert "Test error" in result.error
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, test_runner):
        """Test metrics collection and calculation."""
        result = await test_runner.run_performance_test()
        
        required_metrics = [
            "operations_per_second",
            "average_response_time",
            "total_operations",
            "success_rate"
        ]
        
        for metric in required_metrics:
            assert metric in result.metrics
            assert isinstance(result.metrics[metric], (int, float))
    
    @pytest.mark.asyncio
    async def test_test_result_serialization(self, test_runner):
        """Test TestResult serialization."""
        result = await test_runner.run_connectivity_test()
        
        # Test dict conversion
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert 'test_name' in result_dict
        assert 'success' in result_dict
        assert 'duration' in result_dict
        
        # Test JSON serialization
        json_str = json.dumps(result_dict)
        assert isinstance(json_str, str)
        
        # Test deserialization
        restored_dict = json.loads(json_str)
        assert restored_dict == result_dict

class TestMCPTestIntegration:
    """Test MCP protocol integration for test server."""
    
    @pytest.mark.asyncio
    async def test_mcp_test_server_startup(self):
        """Test MCP test server can start up properly."""
        from mcp_servers.test_simple_mcp_server import main
        
        # Mock the server run to avoid actually starting it
        with patch('fastmcp.Server.run') as mock_run:
            with patch('sys.argv', ['test_simple_mcp_server.py']):
                try:
                    main()
                except SystemExit:
                    pass  # Expected when mocking
                
                mock_run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_test_tools_registration(self):
        """Test that test MCP tools are properly registered."""
        from mcp_servers.test_simple_mcp_server import app
        
        # Check that tools are registered
        tools = app.list_tools()
        tool_names = [tool.name for tool in tools]
        
        expected_tools = [
            'run_connectivity_test',
            'run_performance_test', 
            'run_system_validation',
            'run_stress_test',
            'validate_json_data'
        ]
        
        for tool in expected_tools:
            assert tool in tool_names
    
    @pytest.mark.asyncio
    async def test_mcp_tool_execution(self):
        """Test MCP tool execution through the interface."""
        from mcp_servers.test_simple_mcp_server import (
            run_connectivity_test,
            run_performance_test,
            validate_json_data
        )
        
        # Test connectivity through MCP
        result = await run_connectivity_test()
        assert "connectivity_test" in result
        assert "success" in result
        
        # Test performance testing through MCP
        result = await run_performance_test()
        assert "performance_test" in result
        assert "operations_per_second" in result
        
        # Test JSON validation through MCP
        result = await validate_json_data('{"test": "data"}')
        assert "success" in result

class TestPerformanceMetrics:
    """Test performance metrics and benchmarking."""
    
    @pytest.mark.asyncio
    async def test_performance_baseline(self, test_runner):
        """Test performance baseline measurements."""
        result = await test_runner.run_performance_test()
        
        # Basic performance assertions
        assert result.metrics["operations_per_second"] > 100  # Minimum expected OPS
        assert result.metrics["average_response_time"] < 1.0  # Max 1 second response
        assert result.metrics["success_rate"] >= 0.95  # 95% success rate minimum
    
    @pytest.mark.asyncio
    async def test_stress_test_limits(self, test_runner):
        """Test stress testing under load."""
        # Test with high iteration count
        result = await test_runner.run_stress_test(iterations=100)
        
        assert result.success is True
        assert result.metrics["total_iterations"] == 100
        assert result.metrics["success_rate"] > 0.9  # Should maintain high success rate
    
    @pytest.mark.asyncio
    async def test_memory_usage_tracking(self, test_runner):
        """Test memory usage during operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Run several tests
        for _ in range(10):
            await test_runner.run_connectivity_test()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024
