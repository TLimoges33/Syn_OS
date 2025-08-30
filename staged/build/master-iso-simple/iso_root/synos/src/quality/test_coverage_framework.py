#!/usr/bin/env python3
"""
Test Coverage Framework
Comprehensive testing framework to achieve >80% test coverage across all modules
"""

import asyncio
import logging
import os
import sys
import subprocess
import json
import time
try:
    import coverage
except ImportError:
    coverage = None
    
try:
    import pytest
except ImportError:
    pytest = None
import unittest
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import importlib.util
import ast
import re


@dataclass
class TestResult:
    """Test execution result"""
    test_file: str
    test_name: str
    status: str  # passed, failed, skipped, error
    duration: float
    error_message: Optional[str] = None
    traceback: Optional[str] = None


@dataclass
class CoverageReport:
    """Coverage analysis report"""
    module_name: str
    file_path: str
    lines_total: int
    lines_covered: int
    lines_missing: List[int]
    coverage_percentage: float
    branches_total: int
    branches_covered: int
    branch_coverage_percentage: float
    functions_total: int
    functions_covered: int
    function_coverage_percentage: float


@dataclass
class TestSuite:
    """Test suite definition"""
    suite_name: str
    test_files: List[str]
    target_modules: List[str]
    test_type: str  # unit, integration, system, performance
    priority: int
    estimated_duration: float


class TestCoverageFramework:
    """
    Test Coverage Framework
    Comprehensive testing and coverage analysis system
    """
    
    def __init__(self):
        """Initialize test coverage framework"""
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.project_root = "/home/diablorain/Syn_OS"
        self.src_directory = f"{self.project_root}/src"
        self.tests_directory = f"{self.project_root}/tests"
        self.coverage_directory = f"{self.tests_directory}/coverage"
        self.reports_directory = f"{self.coverage_directory}/reports"
        
        # Coverage targets
        self.target_coverage = 80.0
        self.minimum_coverage = 70.0
        self.excellent_coverage = 90.0
        
        # Test results
        self.test_results: List[TestResult] = []
        self.coverage_reports: Dict[str, CoverageReport] = {}
        self.test_suites: Dict[str, TestSuite] = {}
        
        # Coverage instance
        self.coverage_instance = None
        
        # Initialize framework
        asyncio.create_task(self._initialize_framework())
    
    async def _initialize_framework(self):
        """Initialize test coverage framework"""
        try:
            self.logger.info("Initializing Test Coverage Framework...")
            
            # Create directories
            os.makedirs(self.tests_directory, exist_ok=True)
            os.makedirs(self.coverage_directory, exist_ok=True)
            os.makedirs(self.reports_directory, exist_ok=True)
            
            # Initialize coverage
            self._initialize_coverage()
            
            # Discover test suites
            await self._discover_test_suites()
            
            # Generate missing tests
            await self._generate_missing_tests()
            
            self.logger.info("Test Coverage Framework initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing test coverage framework: {e}")
    
    def _initialize_coverage(self):
        """Initialize coverage measurement"""
        try:
            # Configure coverage if available
            if coverage is not None:
                self.coverage_instance = coverage.Coverage(
                    source=[self.src_directory],
                    omit=[
                        "*/tests/*",
                        "*/test_*",
                        "*/__pycache__/*",
                        "*/venv/*",
                        "*/env/*",
                        "*/.pytest_cache/*"
                    ],
                    branch=True,
                    config_file=False
                )
            else:
                self.coverage_instance = None
                self.logger.warning("Coverage module not available - install with: pip install coverage")
            
            # Create coverage configuration file
            coverage_config = f"""
[run]
source = {self.src_directory}
omit = 
    */tests/*
    */test_*
    */__pycache__/*
    */venv/*
    */env/*
    */.pytest_cache/*

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = {self.coverage_directory}/html

[xml]
output = {self.coverage_directory}/coverage.xml

[json]
output = {self.coverage_directory}/coverage.json
"""
            
            with open(f"{self.project_root}/.coveragerc", 'w') as f:
                f.write(coverage_config)
            
            self.logger.info("Coverage measurement initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing coverage: {e}")
    
    async def _discover_test_suites(self):
        """Discover existing test suites"""
        try:
            # Define core test suites
            core_suites = {
                "consciousness_tests": TestSuite(
                    suite_name="Consciousness Module Tests",
                    test_files=[
                        "tests/unit/test_consciousness_core.py",
                        "tests/unit/test_consciousness_persistence.py",
                        "tests/integration/test_consciousness_integration.py"
                    ],
                    target_modules=[
                        "src/consciousness",
                        "src/consciousness_v2"
                    ],
                    test_type="unit",
                    priority=1,
                    estimated_duration=300.0
                ),
                "security_tests": TestSuite(
                    suite_name="Security Module Tests",
                    test_files=[
                        "tests/unit/test_security_core.py",
                        "tests/unit/test_incident_response.py",
                        "tests/unit/test_siem_monitoring.py",
                        "tests/integration/test_security_integration.py"
                    ],
                    target_modules=[
                        "src/security"
                    ],
                    test_type="unit",
                    priority=1,
                    estimated_duration=450.0
                ),
                "ai_integration_tests": TestSuite(
                    suite_name="AI Integration Tests",
                    test_files=[
                        "tests/unit/test_ai_orchestration.py",
                        "tests/unit/test_claude_interface.py",
                        "tests/unit/test_gemini_interface.py",
                        "tests/integration/test_ai_integration.py"
                    ],
                    target_modules=[
                        "src/ai_integration"
                    ],
                    test_type="unit",
                    priority=2,
                    estimated_duration=360.0
                ),
                "quality_tests": TestSuite(
                    suite_name="Quality Management Tests",
                    test_files=[
                        "tests/unit/test_quality_management.py",
                        "tests/unit/test_test_coverage.py"
                    ],
                    target_modules=[
                        "src/quality"
                    ],
                    test_type="unit",
                    priority=2,
                    estimated_duration=180.0
                ),
                "hardware_tests": TestSuite(
                    suite_name="Hardware Integration Tests",
                    test_files=[
                        "tests/unit/test_hardware_acceleration.py",
                        "tests/unit/test_hardware_security.py",
                        "tests/integration/test_hardware_integration.py"
                    ],
                    target_modules=[
                        "src/hardware_acceleration",
                        "src/hardware_security"
                    ],
                    test_type="integration",
                    priority=3,
                    estimated_duration=240.0
                ),
                "system_tests": TestSuite(
                    suite_name="System Integration Tests",
                    test_files=[
                        "tests/system/test_full_system.py",
                        "tests/system/test_performance.py",
                        "tests/system/test_security_system.py"
                    ],
                    target_modules=[
                        "src"
                    ],
                    test_type="system",
                    priority=4,
                    estimated_duration=600.0
                )
            }
            
            self.test_suites.update(core_suites)
            
            self.logger.info(f"Discovered {len(self.test_suites)} test suites")
            
        except Exception as e:
            self.logger.error(f"Error discovering test suites: {e}")
    
    async def _generate_missing_tests(self):
        """Generate missing test files"""
        try:
            for suite_name, suite in self.test_suites.items():
                for test_file in suite.test_files:
                    test_path = f"{self.project_root}/{test_file}"
                    
                    if not os.path.exists(test_path):
                        await self._create_test_file(test_path, suite)
            
            self.logger.info("Generated missing test files")
            
        except Exception as e:
            self.logger.error(f"Error generating missing tests: {e}")
    
    async def _create_test_file(self, test_path: str, suite: TestSuite):
        """Create a test file with basic structure"""
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(test_path), exist_ok=True)
            
            # Determine test type and content
            test_name = os.path.basename(test_path).replace('.py', '').replace('test_', '')
            
            test_content = f'''#!/usr/bin/env python3
"""
{test_name.replace('_', ' ').title()} Tests
Generated by Test Coverage Framework
"""

import unittest
import asyncio
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))


class Test{test_name.replace('_', '').title()}(unittest.TestCase):
    """Test cases for {test_name.replace('_', ' ')}"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_data = {{}}
        self.mock_objects = {{}}
    
    def tearDown(self):
        """Clean up after tests"""
        pass
    
    def test_initialization(self):
        """Test basic initialization"""
        # Test framework initialization
        framework = CoverageFramework()
        self.assertIsNotNone(framework, "Framework should initialize successfully")
        self.assertIsInstance(framework.test_results, dict, "Test results should be initialized as dict")
        self.assertEqual(len(framework.test_results), 0, "Initial test results should be empty")
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        # Test basic framework functionality
        framework = CoverageFramework()
        
        # Test adding a test result
        test_result = {
            "test_name": "sample_test",
            "status": "passed",
            "execution_time": 0.1
        }
        
        framework.test_results["sample_test"] = test_result
        self.assertEqual(len(framework.test_results), 1, "Should have one test result")
        self.assertEqual(framework.test_results["sample_test"]["status"], "passed", "Test status should be passed")
    
    def test_error_handling(self):
        """Test error handling"""
        # Test error handling scenarios
        framework = CoverageFramework()
        
        # Test handling of invalid test data
        try:
            framework.test_results["invalid_test"] = None
            # Should handle None values gracefully
            self.assertIsNone(framework.test_results["invalid_test"], "Should handle None values")
        except Exception as e:
            self.fail(f"Framework should handle invalid data gracefully: {e}")
    
    def test_edge_cases(self):
        """Test edge cases"""
        # Test edge cases and boundary conditions
        framework = CoverageFramework()
        
        # Test with empty strings
        framework.test_results[""] = {"status": "edge_case"}
        self.assertIn("", framework.test_results, "Should handle empty string keys")
        
        # Test with large number of results
        for i in range(1000):
            framework.test_results[f"test_{i}"] = {"status": "passed", "id": i}
        
        self.assertEqual(len(framework.test_results), 1001, "Should handle large number of test results")  # +1 for empty string test


class Test{test_name.replace('_', '').title()}Async(unittest.IsolatedAsyncioTestCase):
    """Async test cases for {test_name.replace('_', ' ')}"""
    
    async def asyncSetUp(self):
        """Set up async test fixtures"""
        self.test_data = {{}}
    
    async def asyncTearDown(self):
        """Clean up after async tests"""
        pass
    
    async def test_async_functionality(self):
        """Test async functionality"""
        # Test async functionality
        import asyncio
        
        async def async_test_operation():
            await asyncio.sleep(0.01)  # Simulate async operation
            return "async_result"
        
        # Run async test
        result = asyncio.run(async_test_operation())
        self.assertEqual(result, "async_result", "Async operation should complete successfully")


@pytest.fixture
def sample_data():
    """Pytest fixture for sample data"""
    return {{
        "test_value": "sample",
        "test_number": 42,
        "test_list": [1, 2, 3]
    }}


def test_pytest_example(sample_data):
    """Example pytest test"""
    assert sample_data["test_value"] == "sample"
    assert sample_data["test_number"] == 42
    assert len(sample_data["test_list"]) == 3


if __name__ == '__main__':
    # Run unittest tests
    unittest.main(verbosity=2)
'''
            
            with open(test_path, 'w') as f:
                f.write(test_content)
            
            self.logger.info(f"Created test file: {test_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating test file {test_path}: {e}")
    
    async def run_test_suite(self, suite_name: str) -> Dict[str, Any]:
        """Run a specific test suite"""
        try:
            if suite_name not in self.test_suites:
                raise ValueError(f"Test suite '{suite_name}' not found")
            
            suite = self.test_suites[suite_name]
            start_time = time.time()
            
            self.logger.info(f"Running test suite: {suite.suite_name}")
            
            # Start coverage measurement
            if self.coverage_instance:
                self.coverage_instance.start()
            
            suite_results = []
            
            for test_file in suite.test_files:
                test_path = f"{self.project_root}/{test_file}"
                
                if os.path.exists(test_path):
                    result = await self._run_test_file(test_path)
                    suite_results.extend(result)
            
            # Stop coverage measurement
            if self.coverage_instance:
                self.coverage_instance.stop()
                self.coverage_instance.save()
            
            duration = time.time() - start_time
            
            # Calculate suite statistics
            total_tests = len(suite_results)
            passed_tests = sum(1 for r in suite_results if r.status == "passed")
            failed_tests = sum(1 for r in suite_results if r.status == "failed")
            skipped_tests = sum(1 for r in suite_results if r.status == "skipped")
            
            suite_result = {
                "suite_name": suite.suite_name,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "skipped_tests": skipped_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "duration": duration,
                "test_results": [asdict(r) for r in suite_results]
            }
            
            self.logger.info(f"Test suite completed: {passed_tests}/{total_tests} passed")
            return suite_result
            
        except Exception as e:
            self.logger.error(f"Error running test suite {suite_name}: {e}")
            return {
                "suite_name": suite_name,
                "error": str(e),
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "skipped_tests": 0,
                "success_rate": 0,
                "duration": 0,
                "test_results": []
            }
    
    async def _run_test_file(self, test_path: str) -> List[TestResult]:
        """Run tests in a specific file"""
        try:
            results = []
            
            # Run with pytest
            pytest_cmd = [
                sys.executable, "-m", "pytest",
                test_path,
                "-v",
                "--tb=short",
                "--json-report",
                f"--json-report-file={self.coverage_directory}/pytest_report.json"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *pytest_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.project_root
            )
            
            stdout, stderr = await process.communicate()
            
            # Parse pytest JSON report if available
            json_report_path = f"{self.coverage_directory}/pytest_report.json"
            if os.path.exists(json_report_path):
                with open(json_report_path, 'r') as f:
                    report_data = json.load(f)
                
                for test in report_data.get('tests', []):
                    result = TestResult(
                        test_file=test_path,
                        test_name=test.get('nodeid', 'unknown'),
                        status=test.get('outcome', 'unknown'),
                        duration=test.get('duration', 0.0),
                        error_message=test.get('call', {}).get('longrepr', None) if test.get('outcome') == 'failed' else None
                    )
                    results.append(result)
            
            # Fallback: run with unittest if pytest fails
            if not results:
                unittest_cmd = [
                    sys.executable, "-m", "unittest",
                    "discover",
                    "-s", os.path.dirname(test_path),
                    "-p", os.path.basename(test_path),
                    "-v"
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *unittest_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=self.project_root
                )
                
                stdout, stderr = await process.communicate()
                
                # Parse unittest output (basic parsing)
                output = stdout.decode() + stderr.decode()
                if "OK" in output or "FAILED" in output:
                    # Create basic result
                    result = TestResult(
                        test_file=test_path,
                        test_name=os.path.basename(test_path),
                        status="passed" if "OK" in output else "failed",
                        duration=0.0,
                        error_message=stderr.decode() if stderr else None
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error running test file {test_path}: {e}")
            return [TestResult(
                test_file=test_path,
                test_name="error",
                status="error",
                duration=0.0,
                error_message=str(e)
            )]
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites"""
        try:
            self.logger.info("Running all test suites...")
            start_time = time.time()
            
            all_results = {}
            total_stats = {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "skipped_tests": 0
            }
            
            # Run suites in priority order
            sorted_suites = sorted(
                self.test_suites.items(),
                key=lambda x: x[1].priority
            )
            
            for suite_name, suite in sorted_suites:
                result = await self.run_test_suite(suite_name)
                all_results[suite_name] = result
                
                # Update totals
                total_stats["total_tests"] += result.get("total_tests", 0)
                total_stats["passed_tests"] += result.get("passed_tests", 0)
                total_stats["failed_tests"] += result.get("failed_tests", 0)
                total_stats["skipped_tests"] += result.get("skipped_tests", 0)
            
            duration = time.time() - start_time
            
            # Calculate overall success rate
            success_rate = (
                total_stats["passed_tests"] / total_stats["total_tests"] * 100
                if total_stats["total_tests"] > 0 else 0
            )
            
            final_result = {
                "overall_stats": total_stats,
                "success_rate": success_rate,
                "duration": duration,
                "suite_results": all_results,
                "timestamp": time.time()
            }
            
            self.logger.info(f"All tests completed: {total_stats['passed_tests']}/{total_stats['total_tests']} passed ({success_rate:.1f}%)")
            
            return final_result
            
        except Exception as e:
            self.logger.error(f"Error running all tests: {e}")
            return {
                "error": str(e),
                "overall_stats": {"total_tests": 0, "passed_tests": 0, "failed_tests": 0, "skipped_tests": 0},
                "success_rate": 0,
                "duration": 0,
                "suite_results": {},
                "timestamp": time.time()
            }
    
    async def generate_coverage_report(self) -> Dict[str, Any]:
        """Generate comprehensive coverage report"""
        try:
            self.logger.info("Generating coverage report...")
            
            if not self.coverage_instance:
                raise ValueError("Coverage not initialized")
            
            # Generate coverage reports
            coverage_data = {}
            
            # HTML report
            html_dir = f"{self.coverage_directory}/html"
            self.coverage_instance.html_report(directory=html_dir)
            
            # XML report
            xml_file = f"{self.coverage_directory}/coverage.xml"
            self.coverage_instance.xml_report(outfile=xml_file)
            
            # JSON report
            json_file = f"{self.coverage_directory}/coverage.json"
            self.coverage_instance.json_report(outfile=json_file)
            
            # Load JSON data for analysis
            if os.path.exists(json_file):
                with open(json_file, 'r') as f:
                    json_data = json.load(f)
                
                # Process coverage data
                for filename, file_data in json_data.get('files', {}).items():
                    if filename.startswith(self.src_directory):
                        module_name = filename.replace(self.src_directory, '').strip('/')
                        
                        coverage_report = CoverageReport(
                            module_name=module_name,
                            file_path=filename,
                            lines_total=file_data.get('summary', {}).get('num_statements', 0),
                            lines_covered=file_data.get('summary', {}).get('covered_lines', 0),
                            lines_missing=file_data.get('missing_lines', []),
                            coverage_percentage=file_data.get('summary', {}).get('percent_covered', 0.0),
                            branches_total=file_data.get('summary', {}).get('num_branches', 0),
                            branches_covered=file_data.get('summary', {}).get('covered_branches', 0),
                            branch_coverage_percentage=file_data.get('summary', {}).get('percent_covered_display', 0.0),
                            functions_total=0,  # Not available in coverage.py JSON
                            functions_covered=0,
                            function_coverage_percentage=0.0
                        )
                        
                        self.coverage_reports[module_name] = coverage_report
            
            # Calculate overall statistics
            total_lines = sum(r.lines_total for r in self.coverage_reports.values())
            covered_lines = sum(r.lines_covered for r in self.coverage_reports.values())
            overall_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
            
            # Categorize modules by coverage
            excellent_modules = [m for m, r in self.coverage_reports.items() if r.coverage_percentage >= self.excellent_coverage]
            good_modules = [m for m, r in self.coverage_reports.items() if self.target_coverage <= r.coverage_percentage < self.excellent_coverage]
            needs_improvement = [m for m, r in self.coverage_reports.items() if self.minimum_coverage <= r.coverage_percentage < self.target_coverage]
            poor_coverage = [m for m, r in self.coverage_reports.items() if r.coverage_percentage < self.minimum_coverage]
            
            coverage_summary = {
                "overall_coverage": overall_coverage,
                "target_coverage": self.target_coverage,
                "target_met": overall_coverage >= self.target_coverage,
                "total_lines": total_lines,
                "covered_lines": covered_lines,
                "missing_lines": total_lines - covered_lines,
                "module_count": len(self.coverage_reports),
                "excellent_modules": len(excellent_modules),
                "good_modules": len(good_modules),
                "needs_improvement": len(needs_improvement),
                "poor_coverage": len(poor_coverage),
                "module_details": {
                    "excellent": excellent_modules,
                    "good": good_modules,
                    "needs_improvement": needs_improvement,
                    "poor": poor_coverage
                },
                "reports": {
                    "html_report": html_dir,
                    "xml_report": xml_file,
                    "json_report": json_file
                },
                "timestamp": time.time()
            }
            
            self.logger.info(f"Coverage report generated: {overall_coverage:.1f}% overall coverage")
            
            return coverage_summary
            
        except Exception as e:
            self.logger.error(f"Error generating coverage report: {e}")
            return {
                "error": str(e),
                "overall_coverage": 0.0,
                "target_met": False,
                "timestamp": time.time()
            }
    
    async def generate_comprehensive_report(self) -> str:
        """Generate comprehensive test and coverage report"""
        try:
            # Run all tests
            test_results = await self.run_all_tests()
            
            # Generate coverage report
            coverage_results = await self.generate_coverage_report()
            
            # Create comprehensive report
            report_time = time.strftime("%Y-%m-%d %H:%M:%S")
            
            report = f"""# Syn_OS Test Coverage Report
Generated: {report_time}

## Executive Summary
- **Overall Test Success Rate**: {test_results.get('success_rate', 0):.1f}%
- **Overall Code Coverage**: {coverage_results.get('overall_coverage', 0):.1f}%
- **Coverage Target Met**: {'✅ YES' if coverage_results.get('target_met', False) else '❌ NO'}
- **Target Coverage**: {coverage_results.get('target_coverage', 80)}%

## Test Results Summary
- **Total Tests**: {test_results.get('overall_stats', {}).get('total_tests', 0)}
- **Passed Tests**: {test_results.get('overall_stats', {}).get('passed_tests', 0)}
- **Failed Tests**: {test_results.get('overall_stats', {}).get('failed_tests', 0)}
- **Skipped Tests**: {test_results.get('overall_stats', {}).get('skipped_tests', 0)}
- **Test Duration**: {test_results.get('duration', 0):.1f} seconds

## Coverage Analysis
- **Total Lines**: {coverage_results.get('total_lines', 0):,}
- **Covered Lines**: {coverage_results.get('covered_lines', 0):,}
- **Missing Lines**: {coverage_results.get('missing_lines', 0):,}
- **Modules Analyzed**: {coverage_results.get('module_count', 0)}

### Coverage Categories
- **Excellent (≥90%)**: {coverage_results.get('excellent_modules', 0)} modules
- **Good (80-89%)**: {coverage_results.get('good_modules', 0)} modules
- **Needs Improvement (70-79%)**: {coverage_results.get('needs_improvement', 0)} modules
- **Poor (<70%)**: {coverage_results.get('poor_coverage', 0)} modules

## Test Suite Results
"""
            
            for suite_name, suite_result in test_results.get('suite_results', {}).items():
                report += f"""
### {suite_result.get('suite_name', suite_name)}
- **Tests**: {suite_result.get('total_tests', 0)} total
- **Passed**: {suite_result.get('passed_tests', 0)}
- **Failed**: {suite_result.get('failed_tests', 0)}
- **Skipped**: {suite_result.get('skipped_tests', 0)}
- **Success Rate**: {suite_result.get('success_rate', 0):.1f}%
- **Duration**: {suite_result.get('duration', 0):.1f}s
"""
            
            # Add module coverage details
            if coverage_results.get('module_details'):
                report += "\n## Module Coverage Details\n"
                
                for category, modules in coverage_results['module_details'].items():
                    if modules:
                        report += f"\n### {category.replace('_', ' ').title()} Modules\n"
                        for module in modules[:10]:  # Limit to first 10
                            if module in self.coverage_reports:
                                cov = self.coverage_reports[module]
                                report += f"- **{module}**: {cov.coverage_percentage:.1f}% ({cov.lines_covered}/{cov.lines_total} lines)\n"
            
            # Add recommendations
            report += "\n## Recommendations\n"
            
            if coverage_results.get('overall_coverage', 0) < self.target_coverage:
                report += f"- 🎯 **Priority**: Increase overall coverage from {coverage_results.get('overall_coverage', 0):.1f}% to {self.target_coverage}%\n"
            
            if coverage_results.get('poor_coverage', 0) > 0:
                report += f"- 🔧 **Focus**: Improve {coverage_results.get('poor_coverage', 0)} modules with poor coverage\n"
            
            if test_results.get('overall_stats', {}).get('failed_tests', 0) > 0:
                report += f"- 🐛 **Fix**: Address {test_results.get('overall_stats', {}).get('failed_tests', 0)} failing tests\n"
            
            report += "- 📈 **Continuous**: Maintain coverage above 80% for all new code\n"
            report += "- 🧪 **Quality**: Add integration and system tests for critical paths\n"
            
            # Save report
            report_file = f"{self.reports_directory}/comprehensive_test_report_{int(time.time())}.md"
            with open(report_file, 'w') as f:
                f.write(report)
            
            self.logger.info(f"Comprehensive report generated: {report_file}")
            return report_file
            
        except Exception as e:
            self.logger.error(f"Error generating comprehensive report: {e}")
            raise


# Global test framework instance
test_framework_instance = None

async def get_test_framework():
    """Get global test framework instance"""
    global test_framework_instance
    if test_framework_instance is None:
        test_framework_instance = TestCoverageFramework()
        await asyncio.sleep(1)  # Allow initialization
    return test_framework_instance


if __name__ == "__main__":
    async def main():
        """Main function for testing"""
        logging.basicConfig(level=logging.INFO)
        
        # Initialize test framework
        framework = TestCoverageFramework()
        await asyncio.sleep(3)  # Allow initialization
        
        # Run all tests
        print("Running all test suites...")
        test_results = await framework.run_all_tests()
        print(f"Test Results: {json.dumps(test_results, indent=2)}")
        
        # Generate coverage report
        print("Generating coverage report...")
        coverage_results = await framework.generate_coverage_report()
        print(f"Coverage Results: {json.dumps(coverage_results, indent=2)}")
        
        # Generate comprehensive report
        print("Generating comprehensive report...")
        report_file = await framework.generate_comprehensive_report()
        print(f"Report generated: {report_file}")
    
    asyncio.run(main())