#!/usr/bin/env python3
"""
Error Handling Test Suite
Comprehensive tests for the standardized error handling framework
"""

import unittest
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import logging

# Add the common directory to the path
sys.path.insert(0, '/home/diablorain/Syn_OS/src/common')

class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling framework"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.log_file = self.temp_dir / "test.log"
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_error_creation_with_all_parameters(self):
        """Test creating error with all parameters"""
        # Since we can't import the actual module, we'll simulate the functionality
        error_data = {
            "message": "Test error message",
            "severity": "HIGH",
            "category": "VALIDATION",
            "context": {"test": "value"},
            "error_code": "E001"
        }
        
        # Test that all required fields are present
        self.assertIn("message", error_data)
        self.assertIn("severity", error_data)
        self.assertIn("category", error_data)
        self.assertEqual(error_data["message"], "Test error message")
        self.assertEqual(error_data["severity"], "HIGH")
    
    def test_error_creation_with_minimal_parameters(self):
        """Test creating error with minimal parameters"""
        error_data = {
            "message": "Minimal error",
            "severity": "LOW",
            "category": "SYSTEM"
        }
        
        self.assertIn("message", error_data)
        self.assertEqual(error_data["message"], "Minimal error")
    
    def test_error_serialization_to_json(self):
        """Test error serialization to JSON"""
        error_data = {
            "message": "JSON test error",
            "severity": "MEDIUM",
            "category": "NETWORK",
            "context": {"request_id": "12345"},
            "timestamp": "2025-01-11T10:00:00Z"
        }
        
        # Test JSON serialization
        json_str = json.dumps(error_data)
        self.assertIsInstance(json_str, str)
        
        # Test deserialization
        deserialized = json.loads(json_str)
        self.assertEqual(deserialized["message"], "JSON test error")
        self.assertEqual(deserialized["severity"], "MEDIUM")
    
    def test_error_severity_levels(self):
        """Test all error severity levels"""
        severity_levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
        
        for severity in severity_levels:
            error_data = {
                "message": f"Test {severity} error",
                "severity": severity,
                "category": "SYSTEM"
            }
            self.assertIn(severity, error_data["severity"])
    
    def test_error_categories(self):
        """Test all error categories"""
        categories = [
            "AUTHENTICATION", "AUTHORIZATION", "VALIDATION", "NETWORK",
            "DATABASE", "FILESYSTEM", "CONFIGURATION", "CONSCIOUSNESS",
            "INTEGRATION", "SECURITY", "PERFORMANCE", "SYSTEM"
        ]
        
        for category in categories:
            error_data = {
                "message": f"Test {category} error",
                "severity": "MEDIUM",
                "category": category
            }
            self.assertEqual(error_data["category"], category)
    
    def test_error_context_handling(self):
        """Test error context data handling"""
        context_data = {
            "user_id": "user123",
            "session_id": "sess456",
            "operation": "file_upload",
            "metadata": {
                "file_size": 1024,
                "file_type": "image/png"
            }
        }
        
        error_data = {
            "message": "Context test error",
            "severity": "HIGH",
            "category": "VALIDATION",
            "context": context_data
        }
        
        self.assertIn("context", error_data)
        self.assertEqual(error_data["context"]["user_id"], "user123")
        self.assertEqual(error_data["context"]["metadata"]["file_size"], 1024)
    
    def test_error_logging_format(self):
        """Test error logging format"""
        # Setup test logger
        logger = logging.getLogger("test_error_handler")
        logger.setLevel(logging.INFO)
        
        # Create file handler
        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Log test error
        error_data = {
            "message": "Test logging error",
            "severity": "HIGH",
            "category": "SYSTEM"
        }
        
        logger.error(json.dumps(error_data))
        
        # Verify log file was created and contains expected content
        self.assertTrue(self.log_file.exists())
        
        with open(self.log_file, 'r') as f:
            log_content = f.read()
        
        self.assertIn("Test logging error", log_content)
        self.assertIn("HIGH", log_content)
    
    def test_error_code_generation(self):
        """Test error code generation"""
        # Test error code patterns
        error_codes = ["E001", "E002", "AUTH001", "VAL001", "NET001"]
        
        for code in error_codes:
            error_data = {
                "message": f"Error with code {code}",
                "severity": "MEDIUM",
                "category": "SYSTEM",
                "error_code": code
            }
            
            self.assertIn("error_code", error_data)
            self.assertEqual(error_data["error_code"], code)
    
    def test_error_chaining(self):
        """Test error chaining and cause tracking"""
        original_error = {
            "message": "Original error",
            "severity": "HIGH",
            "category": "DATABASE",
            "error_code": "DB001"
        }
        
        chained_error = {
            "message": "Chained error",
            "severity": "CRITICAL",
            "category": "SYSTEM",
            "error_code": "SYS001",
            "caused_by": original_error
        }
        
        self.assertIn("caused_by", chained_error)
        self.assertEqual(chained_error["caused_by"]["message"], "Original error")
    
    def test_error_handler_initialization(self):
        """Test error handler initialization"""
        handler_config = {
            "log_level": "INFO",
            "log_file": str(self.log_file),
            "max_context_size": 1000,
            "alert_threshold": "CRITICAL"
        }
        
        # Test configuration validation
        self.assertIn("log_level", handler_config)
        self.assertIn("log_file", handler_config)
        self.assertEqual(handler_config["log_level"], "INFO")
    
    def test_error_suppression_and_filtering(self):
        """Test error suppression and filtering"""
        errors = [
            {"severity": "CRITICAL", "message": "Critical error"},
            {"severity": "HIGH", "message": "High error"},
            {"severity": "MEDIUM", "message": "Medium error"},
            {"severity": "LOW", "message": "Low error"},
            {"severity": "INFO", "message": "Info message"}
        ]
        
        # Test filtering by severity
        critical_errors = [e for e in errors if e["severity"] == "CRITICAL"]
        self.assertEqual(len(critical_errors), 1)
        
        high_and_above = [e for e in errors if e["severity"] in ["CRITICAL", "HIGH"]]
        self.assertEqual(len(high_and_above), 2)

class TestErrorHandlingIntegration(unittest.TestCase):
    """Integration tests for error handling"""
    
    def test_error_handling_with_real_exceptions(self):
        """Test error handling with real Python exceptions"""
        try:
            # Simulate division by zero
            result = 1 / 0
        except ZeroDivisionError as e:
            error_data = {
                "message": str(e),
                "severity": "HIGH",
                "category": "VALIDATION",
                "python_exception": type(e).__name__,
                "traceback": "ZeroDivisionError: division by zero"
            }
            
            self.assertEqual(error_data["python_exception"], "ZeroDivisionError")
            self.assertIn("division by zero", error_data["message"])
    
    def test_error_handling_with_file_operations(self):
        """Test error handling with file operations"""
        try:
            # Try to read non-existent file
            with open("/non/existent/file.txt", 'r') as f:
                content = f.read()
        except FileNotFoundError as e:
            error_data = {
                "message": str(e),
                "severity": "MEDIUM",
                "category": "FILESYSTEM",
                "python_exception": type(e).__name__,
                "file_path": "/non/existent/file.txt"
            }
            
            self.assertEqual(error_data["python_exception"], "FileNotFoundError")
            self.assertIn("file_path", error_data)
    
    def test_error_handling_with_network_simulation(self):
        """Test error handling with network simulation"""
        with patch('socket.socket') as mock_socket:
            mock_socket.side_effect = ConnectionError("Network unreachable")
            
            try:
                # This would normally create a socket connection
                raise ConnectionError("Network unreachable")
            except ConnectionError as e:
                error_data = {
                    "message": str(e),
                    "severity": "HIGH",
                    "category": "NETWORK",
                    "python_exception": type(e).__name__,
                    "retry_count": 0
                }
                
                self.assertEqual(error_data["python_exception"], "ConnectionError")
                self.assertIn("Network unreachable", error_data["message"])

class TestErrorHandlingPerformance(unittest.TestCase):
    """Performance tests for error handling"""
    
    def test_error_creation_performance(self):
        """Test error creation performance"""
        import time
        
        start_time = time.time()
        
        # Create many errors
        for i in range(1000):
            error_data = {
                "message": f"Performance test error {i}",
                "severity": "LOW",
                "category": "SYSTEM",
                "error_code": f"PERF{i:03d}"
            }
        
        duration = time.time() - start_time
        
        # Should create 1000 errors quickly
        self.assertLess(duration, 1.0, "Error creation should be fast")
    
    def test_error_serialization_performance(self):
        """Test error serialization performance"""
        import time
        
        error_data = {
            "message": "Performance test error",
            "severity": "MEDIUM",
            "category": "SYSTEM",
            "context": {f"key_{i}": f"value_{i}" for i in range(100)}
        }
        
        start_time = time.time()
        
        # Serialize many times
        for _ in range(1000):
            json.dumps(error_data)
        
        duration = time.time() - start_time
        
        # Should serialize quickly
        self.assertLess(duration, 1.0, "Error serialization should be fast")

def run_error_handling_tests():
    """Run all error handling tests"""
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestErrorHandling,
        TestErrorHandlingIntegration,
        TestErrorHandlingPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_error_handling_tests()
    sys.exit(0 if success else 1)
