#!/usr/bin/env python3
"""
Syn_OS Test Runner
Comprehensive test execution with coverage reporting and metrics
"""

import subprocess
import sys
import json
import time
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
log_dir = Path("${PROJECT_ROOT}/logs/tests")
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "test_runner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestRunner:
    """Comprehensive test runner for Syn_OS"""
    
    def __init__(self):
        self.test_dir = Path("${PROJECT_ROOT}/tests")
        self.results = {}
        self.start_time = None
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
        # Test files to run
        self.test_files = [
            "comprehensive_test_framework.py",
            "test_error_handling.py", 
            "test_consciousness.py",
            "test_security_comprehensive.py"
        ]
        
        # Coverage targets
        self.coverage_targets = {
            "overall": 95.0,
            "error_handling": 100.0,
            "consciousness": 90.0,
            "security": 95.0,
            "integration": 85.0
        }
    
    def check_test_environment(self):
        """Check if test environment is properly set up"""
        logger.info("🔍 Checking test environment...")
        
        # Check if test directory exists
        if not self.test_dir.exists():
            logger.error(f"❌ Test directory not found: {self.test_dir}")
            return False
        
        # Check if test files exist
        missing_files = []
        for test_file in self.test_files:
            test_path = self.test_dir / test_file
            if not test_path.exists():
                missing_files.append(test_file)
        
        if missing_files:
            logger.warning(f"⚠️  Missing test files: {missing_files}")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or python_version.minor < 8:
            logger.error(f"❌ Python 3.8+ required, found {python_version.major}.{python_version.minor}")
            return False
        
        logger.info("✅ Test environment check passed")
        return True
    
    def run_single_test_file(self, test_file):
        """Run a single test file"""
        test_path = self.test_dir / test_file
        logger.info(f"🧪 Running {test_file}...")
        
        start_time = time.time()
        
        try:
            # Run the test file
            result = subprocess.run(
                [sys.executable, str(test_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            # Parse output for test counts (basic parsing)
            output_lines = result.stdout.split('\n') + result.stderr.split('\n')
            tests_run = 0
            failures = 0
            errors = 0
            
            for line in output_lines:
                if 'tests run' in line.lower() or 'ran' in line.lower():
                    # Try to extract numbers from lines like "Ran 25 tests"
                    words = line.split()
                    for i, word in enumerate(words):
                        if word.lower() in ['ran', 'tests'] and i > 0:
                            try:
                                tests_run = int(words[i-1])
                            except (ValueError, IndexError):
                                pass
                
                if 'failed' in line.lower() or 'failures' in line.lower():
                    words = line.split()
                    for word in words:
                        if word.isdigit():
                            failures += int(word)
                            break
            
            test_result = {
                "file": test_file,
                "success": success,
                "duration": duration,
                "tests_run": tests_run,
                "failures": failures,
                "errors": errors,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
            if success:
                logger.info(f"✅ {test_file} passed ({duration:.2f}s)")
            else:
                logger.error(f"❌ {test_file} failed ({duration:.2f}s)")
                if result.stderr:
                    logger.error(f"Error output: {result.stderr[:500]}...")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ {test_file} timed out after 5 minutes")
            return {
                "file": test_file,
                "success": False,
                "duration": 300,
                "tests_run": 0,
                "failures": 0,
                "errors": 1,
                "stdout": "",
                "stderr": "Test timed out",
                "return_code": -1
            }
        except Exception as e:
            logger.error(f"💥 Error running {test_file}: {str(e)}")
            return {
                "file": test_file,
                "success": False,
                "duration": 0,
                "tests_run": 0,
                "failures": 0,
                "errors": 1,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1
            }
    
    def run_all_tests(self):
        """Run all test files"""
        logger.info("🚀 Starting comprehensive test suite...")
        self.start_time = time.time()
        
        if not self.check_test_environment():
            return False
        
        # Run each test file
        for test_file in self.test_files:
            test_path = self.test_dir / test_file
            if test_path.exists():
                result = self.run_single_test_file(test_file)
                self.results[test_file] = result
                
                # Update totals
                self.total_tests += result["tests_run"]
                if result["success"]:
                    self.passed_tests += result["tests_run"]
                else:
                    self.failed_tests += result["tests_run"]
            else:
                logger.warning(f"⚠️  Test file not found: {test_file}")
        
        total_duration = time.time() - self.start_time
        
        # Calculate overall success rate
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        # Generate summary
        self.generate_test_report(total_duration, success_rate)
        
        # Check if we met targets
        overall_success = success_rate >= self.coverage_targets["overall"]
        
        if overall_success:
            logger.info("🎉 All tests completed successfully!")
        else:
            logger.warning(f"⚠️  Test coverage below target: {success_rate:.1f}% < {self.coverage_targets['overall']}%")
        
        return overall_success
    
    def generate_test_report(self, total_duration, success_rate):
        """Generate comprehensive test report"""
        logger.info("📊 Generating test report...")
        
        # Create detailed report
        report = {
            "test_run_info": {
                "timestamp": datetime.now().isoformat(),
                "total_duration": total_duration,
                "environment": {
                    "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                    "platform": sys.platform,
                    "test_directory": str(self.test_dir)
                }
            },
            "summary": {
                "total_test_files": len(self.test_files),
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "success_rate": success_rate,
                "coverage_targets": self.coverage_targets,
                "targets_met": success_rate >= self.coverage_targets["overall"]
            },
            "test_file_results": {}
        }
        
        # Add individual test file results
        for test_file, result in self.results.items():
            report["test_file_results"][test_file] = {
                "success": result["success"],
                "duration": result["duration"],
                "tests_run": result["tests_run"],
                "failures": result["failures"],
                "errors": result["errors"],
                "return_code": result["return_code"]
            }
        
        # Write report to file
        report_file = log_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Write human-readable summary
        summary_file = log_dir / f"test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(summary_file, 'w') as f:
            f.write("Syn_OS Comprehensive Test Suite Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Test Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Duration: {total_duration:.2f} seconds\n")
            f.write(f"Python Version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}\n\n")
            
            f.write("SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total Test Files: {len(self.test_files)}\n")
            f.write(f"Total Tests: {self.total_tests}\n")
            f.write(f"Passed Tests: {self.passed_tests}\n")
            f.write(f"Failed Tests: {self.failed_tests}\n")
            f.write(f"Success Rate: {success_rate:.1f}%\n")
            f.write(f"Coverage Target: {self.coverage_targets['overall']}%\n")
            f.write(f"Target Met: {'✅ YES' if success_rate >= self.coverage_targets['overall'] else '❌ NO'}\n\n")
            
            f.write("INDIVIDUAL TEST FILES\n")
            f.write("-" * 30 + "\n")
            for test_file, result in self.results.items():
                status = "✅ PASS" if result["success"] else "❌ FAIL"
                f.write(f"{test_file:<40} {status} ({result['duration']:.2f}s)\n")
                if result["tests_run"] > 0:
                    f.write(f"  Tests: {result['tests_run']}, Failures: {result['failures']}, Errors: {result['errors']}\n")
                if not result["success"] and result["stderr"]:
                    f.write(f"  Error: {result['stderr'][:200]}...\n")
                f.write("\n")
        
        # Log summary
        logger.info(f"📊 Test Report Generated")
        logger.info(f"   Total Tests: {self.total_tests}")
        logger.info(f"   Passed: {self.passed_tests}")
        logger.info(f"   Failed: {self.failed_tests}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        logger.info(f"   Duration: {total_duration:.2f}s")
        logger.info(f"   Report: {report_file}")
        logger.info(f"   Summary: {summary_file}")
    
    def run_specific_test_category(self, category):
        """Run tests for a specific category"""
        category_files = {
            "error_handling": ["test_error_handling.py"],
            "consciousness": ["test_consciousness.py"],
            "security": ["test_security_comprehensive.py"],
            "comprehensive": ["comprehensive_test_framework.py"],
            "all": self.test_files
        }
        
        if category not in category_files:
            logger.error(f"❌ Unknown test category: {category}")
            logger.info(f"Available categories: {list(category_files.keys())}")
            return False
        
        logger.info(f"🧪 Running {category} tests...")
        
        # Temporarily set test files to category files
        original_test_files = self.test_files
        self.test_files = category_files[category]
        
        try:
            result = self.run_all_tests()
            return result
        finally:
            # Restore original test files
            self.test_files = original_test_files

def main():
    """Main test runner entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Syn_OS Comprehensive Test Runner")
    parser.add_argument(
        "--category",
        choices=["error_handling", "consciousness", "security", "comprehensive", "all"],
        default="all",
        help="Test category to run"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create test runner
    runner = TestRunner()
    
    # Run tests
    if args.category == "all":
        success = runner.run_all_tests()
    else:
        success = runner.run_specific_test_category(args.category)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
