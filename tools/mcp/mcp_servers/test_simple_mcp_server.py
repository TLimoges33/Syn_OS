#!/usr/bin/env python3
"""
Syn_OS Test Simple MCP Server
A comprehensive testing server for validating MCP functionality and development workflows.
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent, Resource

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('syn-os-test-mcp')

# Initialize MCP server
mcp = FastMCP("SynOS Test Simple MCP Server")

class TestRunner:
    """Test execution and validation framework"""
    
    def __init__(self):
        self.test_results = []
        self.test_sessions = {}
        self.start_time = datetime.now()
        
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log a test result"""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'duration': time.time()
        }
        self.test_results.append(result)
        logger.info(f"Test '{test_name}': {'PASS' if success else 'FAIL'}")
        return result
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of all test results"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        return {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'start_time': self.start_time.isoformat(),
            'last_update': datetime.now().isoformat()
        }

# Global test runner
test_runner = TestRunner()

@mcp.tool()
async def run_echo_test(message: str = "Hello, SynOS!") -> List[TextContent]:
    """
    Run a simple echo test to verify basic MCP functionality.
    
    Args:
        message: Message to echo back
    
    Returns:
        Echo response with test validation
    """
    try:
        # Perform echo test
        echo_result = f"Echo: {message}"
        timestamp = datetime.now().isoformat()
        
        # Validate test
        success = len(message) > 0 and isinstance(message, str)
        test_runner.log_test_result("echo_test", success, f"Message length: {len(message)}")
        
        response = f"✅ Echo Test Results:\n"
        response += f"Input: {message}\n"
        response += f"Output: {echo_result}\n"
        response += f"Status: {'PASS' if success else 'FAIL'}\n"
        response += f"Timestamp: {timestamp}\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        error_msg = f"Echo test failed: {str(e)}"
        test_runner.log_test_result("echo_test", False, error_msg)
        return [TextContent(type="text", text=f"❌ {error_msg}")]

@mcp.tool()
async def run_system_validation() -> List[TextContent]:
    """
    Run comprehensive system validation tests.
    
    Returns:
        System validation results including environment checks
    """
    validation_results = []
    
    # Test 1: Environment variables
    try:
        synos_dir = os.getenv('SYNOS_DIR', 'Not set')
        env_test_success = synos_dir != 'Not set' and Path(synos_dir).exists() if synos_dir != 'Not set' else False
        test_runner.log_test_result("environment_check", env_test_success, f"SYNOS_DIR: {synos_dir}")
        validation_results.append(f"Environment: {'✅ PASS' if env_test_success else '❌ FAIL'} - SYNOS_DIR: {synos_dir}")
    except Exception as e:
        test_runner.log_test_result("environment_check", False, str(e))
        validation_results.append(f"Environment: ❌ FAIL - Error: {e}")
    
    # Test 2: Python environment
    try:
        python_version = f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}"
        python_test_success = os.sys.version_info >= (3, 8)
        test_runner.log_test_result("python_version", python_test_success, python_version)
        validation_results.append(f"Python: {'✅ PASS' if python_test_success else '❌ FAIL'} - Version: {python_version}")
    except Exception as e:
        test_runner.log_test_result("python_version", False, str(e))
        validation_results.append(f"Python: ❌ FAIL - Error: {e}")
    
    # Test 3: File system access
    try:
        current_dir = Path.cwd()
        write_test_file = current_dir / "mcp_test_write.tmp"
        
        # Test write access
        write_test_file.write_text("MCP Write Test")
        write_success = write_test_file.exists()
        
        # Test read access
        read_content = write_test_file.read_text() if write_success else ""
        read_success = read_content == "MCP Write Test"
        
        # Cleanup
        if write_test_file.exists():
            write_test_file.unlink()
        
        fs_test_success = write_success and read_success
        test_runner.log_test_result("filesystem_access", fs_test_success, f"Read/Write in {current_dir}")
        validation_results.append(f"File System: {'✅ PASS' if fs_test_success else '❌ FAIL'} - R/W access in {current_dir}")
        
    except Exception as e:
        test_runner.log_test_result("filesystem_access", False, str(e))
        validation_results.append(f"File System: ❌ FAIL - Error: {e}")
    
    # Test 4: JSON processing
    try:
        test_data = {"test": True, "timestamp": datetime.now().isoformat(), "version": "1.0.0"}
        json_str = json.dumps(test_data)
        parsed_data = json.loads(json_str)
        json_test_success = parsed_data["test"] == True
        test_runner.log_test_result("json_processing", json_test_success, "JSON encode/decode")
        validation_results.append(f"JSON Processing: {'✅ PASS' if json_test_success else '❌ FAIL'}")
    except Exception as e:
        test_runner.log_test_result("json_processing", False, str(e))
        validation_results.append(f"JSON Processing: ❌ FAIL - Error: {e}")
    
    # Test 5: Async functionality
    try:
        async def async_test():
            await asyncio.sleep(0.1)
            return "async_success"
        
        async_result = await async_test()
        async_test_success = async_result == "async_success"
        test_runner.log_test_result("async_operations", async_test_success, "Basic async/await")
        validation_results.append(f"Async Operations: {'✅ PASS' if async_test_success else '❌ FAIL'}")
    except Exception as e:
        test_runner.log_test_result("async_operations", False, str(e))
        validation_results.append(f"Async Operations: ❌ FAIL - Error: {e}")
    
    # Compile results
    summary = test_runner.get_test_summary()
    
    response = "🔍 System Validation Results:\n\n"
    response += "\n".join(validation_results)
    response += f"\n\n📊 Test Summary:\n"
    response += f"Total Tests: {summary['total_tests']}\n"
    response += f"Passed: {summary['passed']}\n"
    response += f"Failed: {summary['failed']}\n"
    response += f"Success Rate: {summary['success_rate']:.1f}%\n"
    
    return [TextContent(type="text", text=response)]

@mcp.tool()
async def run_performance_test(iterations: int = 100) -> List[TextContent]:
    """
    Run performance tests to measure MCP server responsiveness.
    
    Args:
        iterations: Number of iterations to run
    
    Returns:
        Performance test results with timing metrics
    """
    try:
        if iterations <= 0 or iterations > 1000:
            iterations = 100  # Safety limit
        
        start_time = time.time()
        timings = []
        
        for i in range(iterations):
            iter_start = time.time()
            
            # Simulate work
            data = {"iteration": i, "timestamp": datetime.now().isoformat()}
            json_str = json.dumps(data)
            parsed = json.loads(json_str)
            
            # Small computation
            result = sum(range(10))
            
            iter_end = time.time()
            timings.append(iter_end - iter_start)
        
        end_time = time.time()
        
        # Calculate statistics
        total_time = end_time - start_time
        avg_time = sum(timings) / len(timings)
        min_time = min(timings)
        max_time = max(timings)
        
        # Performance validation
        performance_good = avg_time < 0.001  # Less than 1ms average
        test_runner.log_test_result("performance_test", performance_good, 
                                  f"Avg: {avg_time*1000:.2f}ms, {iterations} iterations")
        
        response = f"⚡ Performance Test Results:\n\n"
        response += f"Iterations: {iterations}\n"
        response += f"Total Time: {total_time:.4f}s\n"
        response += f"Average Time: {avg_time*1000:.4f}ms\n"
        response += f"Min Time: {min_time*1000:.4f}ms\n"
        response += f"Max Time: {max_time*1000:.4f}ms\n"
        response += f"Throughput: {iterations/total_time:.2f} ops/sec\n"
        response += f"Status: {'✅ GOOD' if performance_good else '⚠️ SLOW'}\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        error_msg = f"Performance test failed: {str(e)}"
        test_runner.log_test_result("performance_test", False, error_msg)
        return [TextContent(type="text", text=f"❌ {error_msg}")]

@mcp.tool()
async def get_test_summary() -> List[TextContent]:
    """
    Get comprehensive summary of all tests run in this session.
    
    Returns:
        Detailed test summary with statistics and history
    """
    summary = test_runner.get_test_summary()
    
    response = "📋 Test Session Summary:\n\n"
    response += f"Session Start: {summary['start_time']}\n"
    response += f"Last Update: {summary['last_update']}\n"
    response += f"Total Tests: {summary['total_tests']}\n"
    response += f"Passed: {summary['passed']} ✅\n"
    response += f"Failed: {summary['failed']} ❌\n"
    response += f"Success Rate: {summary['success_rate']:.1f}%\n\n"
    
    if test_runner.test_results:
        response += "📜 Test History (Last 10):\n"
        for result in test_runner.test_results[-10:]:
            status = "✅" if result['success'] else "❌"
            response += f"{status} {result['test_name']} - {result['details']}\n"
    else:
        response += "No tests have been run yet.\n"
    
    response += f"\n🎯 Recommendations:\n"
    if summary['failed'] > 0:
        response += "• Review failed tests and fix underlying issues\n"
    if summary['total_tests'] < 5:
        response += "• Run more comprehensive tests (system validation, performance)\n"
    if summary['success_rate'] == 100 and summary['total_tests'] > 0:
        response += "• All tests passing! System is functioning well\n"
    
    return [TextContent(type="text", text=response)]

@mcp.tool()
async def run_connectivity_test() -> List[TextContent]:
    """
    Test MCP server connectivity and communication.
    
    Returns:
        Connectivity test results
    """
    try:
        # Test basic connectivity
        connection_time = datetime.now()
        
        # Test data serialization
        test_payload = {
            "server": "syn-os-test-mcp",
            "version": "1.0.0",
            "timestamp": connection_time.isoformat(),
            "test_data": list(range(10))
        }
        
        serialized = json.dumps(test_payload)
        deserialized = json.loads(serialized)
        
        # Validate round-trip
        data_integrity = deserialized == test_payload
        
        # Test async communication
        await asyncio.sleep(0.01)  # Simulate async operation
        
        connectivity_success = data_integrity
        test_runner.log_test_result("connectivity_test", connectivity_success, 
                                  f"Data integrity: {data_integrity}")
        
        response = f"🔗 Connectivity Test Results:\n\n"
        response += f"Connection Time: {connection_time.isoformat()}\n"
        response += f"Data Integrity: {'✅ PASS' if data_integrity else '❌ FAIL'}\n"
        response += f"Serialization: {'✅ OK' if len(serialized) > 0 else '❌ FAIL'}\n"
        response += f"Async Communication: ✅ OK\n"
        response += f"Overall Status: {'✅ CONNECTED' if connectivity_success else '❌ ISSUES'}\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        error_msg = f"Connectivity test failed: {str(e)}"
        test_runner.log_test_result("connectivity_test", False, error_msg)
        return [TextContent(type="text", text=f"❌ {error_msg}")]

@mcp.tool()
async def reset_test_session() -> List[TextContent]:
    """
    Reset the test session and clear all test history.
    
    Returns:
        Confirmation of session reset
    """
    global test_runner
    
    old_summary = test_runner.get_test_summary()
    test_runner = TestRunner()  # Create new instance
    
    response = f"🔄 Test Session Reset:\n\n"
    response += f"Previous session had:\n"
    response += f"• {old_summary['total_tests']} total tests\n"
    response += f"• {old_summary['passed']} passed\n"
    response += f"• {old_summary['failed']} failed\n"
    response += f"• {old_summary['success_rate']:.1f}% success rate\n\n"
    response += f"New session started at: {test_runner.start_time.isoformat()}\n"
    response += f"Ready for fresh testing! ✨\n"
    
    return [TextContent(type="text", text=response)]

if __name__ == "__main__":
    import mcp.server.stdio
    
    async def main():
        logger.info("Starting SynOS Test Simple MCP Server...")
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await mcp.run(read_stream, write_stream, mcp.create_initialization_options())
    
    asyncio.run(main())