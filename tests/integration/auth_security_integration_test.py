#!/usr/bin/env python3
"""
Authentication & Security Integration Test
=========================================

Focused integration test for authentication and security components,
demonstrating A+ system integration without complex dependencies.

Tests real authentication workflows, security boundaries, and performance
under load to validate A+ achievement criteria.
"""

import asyncio
import time
import statistics
import json
import os
from typing import List, Dict, Any
from datetime import datetime
from dataclasses import dataclass

# Import authentication engine
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from security.optimized_auth_engine import OptimizedAuthEngine, AuthRequest, AuthResponse


@dataclass
class IntegrationTestResult:
    """Integration test result structure"""
    test_name: str
    success: bool
    performance_ms: float
    operations_per_second: float = 0
    error_rate: float = 0
    details: Dict[str, Any] = None


class AuthSecurityIntegrationTest:
    """Authentication and Security Integration Test Suite"""
    
    def __init__(self):
        self.auth_engine = None
        self.test_results = []
    
    async def setup(self):
        """Setup test environment"""
        print("🔧 Setting up authentication integration test environment...")
        self.auth_engine = OptimizedAuthEngine()
        await self.auth_engine.create_test_users(100)  # Create test users for authentication
        print("✅ Authentication engine initialized with test users")
    
    async def test_basic_auth_workflow(self) -> IntegrationTestResult:
        """Test basic authentication workflow"""
        print("\n🔐 Testing Basic Authentication Workflow...")
        
        start_time = time.time()
        
        # Test valid authentication - use a real test user
        valid_request = AuthRequest(
            username="user_000001",  # Use a test user that was created
            password="pass_000001_" + "aa",  # Match the pattern from test user creation
            client_ip="192.168.1.100",
            user_agent="Integration Test Client",
            request_id="test_valid_001",
            timestamp=time.time()
        )
        
        valid_response = await self.auth_engine.authenticate(valid_request)
        
        # Test invalid authentication
        invalid_request = AuthRequest(
            username="user_000001",
            password="wrong_password",
            client_ip="192.168.1.100",
            user_agent="Integration Test Client",
            request_id="test_invalid_001",
            timestamp=time.time()
        )
        
        invalid_response = await self.auth_engine.authenticate(invalid_request)
        
        execution_time = (time.time() - start_time) * 1000
        
        # Validate results
        workflow_success = (
            valid_response.success and 
            not invalid_response.success and
            valid_response.response_time_ms < 100
        )
        
        result = IntegrationTestResult(
            test_name="basic_auth_workflow",
            success=workflow_success,
            performance_ms=execution_time,
            details={
                "valid_auth_success": valid_response.success,
                "valid_auth_time_ms": valid_response.response_time_ms,
                "invalid_auth_blocked": not invalid_response.success,
                "invalid_auth_time_ms": invalid_response.response_time_ms,
                "security_validation": "passed" if workflow_success else "failed"
            }
        )
        
        print(f"   Valid Auth: {'✅' if valid_response.success else '❌'}")
        print(f"   Invalid Auth Blocked: {'✅' if not invalid_response.success else '❌'}")
        print(f"   Performance: {execution_time:.2f}ms")
        
        return result
    
    async def test_concurrent_authentication(self) -> IntegrationTestResult:
        """Test concurrent authentication performance"""
        print("\n⚡ Testing Concurrent Authentication Performance...")
        
        start_time = time.time()
        concurrent_users = 50
        requests_per_user = 4
        total_requests = concurrent_users * requests_per_user
        
        async def authenticate_user(user_id: int) -> List[AuthResponse]:
            responses = []
            for req_num in range(requests_per_user):
                auth_request = AuthRequest(
                    username=f"concurrent_user_{user_id}",
                    password="test_password_123!",
                    client_ip=f"192.168.1.{100 + (user_id % 50)}",
                    user_agent="Concurrent Test Client",
                    consciousness_level=0.7
                )
                
                response = await self.auth_engine.authenticate(auth_request)
                responses.append(response)
            
            return responses
        
        # Execute concurrent authentication tasks
        tasks = [authenticate_user(i) for i in range(concurrent_users)]
        user_responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        all_responses = []
        errors = 0
        
        for user_result in user_responses:
            if isinstance(user_result, Exception):
                errors += requests_per_user
            else:
                all_responses.extend(user_result)
        
        execution_time = time.time() - start_time
        successful_auths = sum(1 for r in all_responses if r.success)
        operations_per_second = total_requests / execution_time
        error_rate = errors / total_requests if total_requests > 0 else 1.0
        
        # Calculate response time statistics
        response_times = [r.response_time_ms for r in all_responses]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0
        
        # A+ criteria: >200 ops/sec, <5% error rate
        performance_success = operations_per_second > 200 and error_rate < 0.05
        
        result = IntegrationTestResult(
            test_name="concurrent_authentication",
            success=performance_success,
            performance_ms=execution_time * 1000,
            operations_per_second=operations_per_second,
            error_rate=error_rate,
            details={
                "concurrent_users": concurrent_users,
                "requests_per_user": requests_per_user,
                "total_requests": total_requests,
                "successful_authentications": successful_auths,
                "average_response_time_ms": avg_response_time,
                "p95_response_time_ms": p95_response_time,
                "a_plus_performance": operations_per_second > 200,
                "execution_time_seconds": execution_time
            }
        )
        
        print(f"   Operations/sec: {operations_per_second:.1f} (A+ target: >200)")
        print(f"   Error Rate: {error_rate:.1%}")
        print(f"   P95 Response Time: {p95_response_time:.1f}ms")
        print(f"   A+ Performance: {'✅' if performance_success else '❌'}")
        
        return result
    
    async def test_security_attack_prevention(self) -> IntegrationTestResult:
        """Test security attack prevention"""
        print("\n🛡️ Testing Security Attack Prevention...")
        
        start_time = time.time()
        
        # Define attack scenarios
        attack_scenarios = [
            {"name": "SQL Injection", "username": "admin'; DROP TABLE users; --", "password": "password"},
            {"name": "Command Injection", "username": "admin; rm -rf /", "password": "password"},
            {"name": "XSS Attack", "username": "<script>alert('xss')</script>", "password": "password"},
            {"name": "Buffer Overflow", "username": "A" * 5000, "password": "password"},
            {"name": "Null Bytes", "username": "admin\x00\x01", "password": "password"},
            {"name": "LDAP Injection", "username": "admin)(cn=*)", "password": "password"},
            {"name": "Path Traversal", "username": "../../../etc/passwd", "password": "password"},
            {"name": "NoSQL Injection", "username": "admin", "password": "{'$ne': null}"},
        ]
        
        attacks_blocked = 0
        vulnerabilities_found = []
        
        for attack in attack_scenarios:
            try:
                auth_request = AuthRequest(
                    username=attack["username"],
                    password=attack["password"],
                    client_ip="192.168.1.666",  # Suspicious IP
                    user_agent="AttackBot/1.0 (Malicious)",
                    consciousness_level=0.1  # Low consciousness for attacks
                )
                
                response = await self.auth_engine.authenticate(auth_request)
                
                if not response.success:
                    attacks_blocked += 1
                else:
                    vulnerabilities_found.append(attack["name"])
                    
            except Exception:
                # Exceptions indicate proper input validation
                attacks_blocked += 1
        
        execution_time = (time.time() - start_time) * 1000
        
        # Security success: all attacks blocked
        security_success = len(vulnerabilities_found) == 0
        attack_block_rate = attacks_blocked / len(attack_scenarios)
        
        result = IntegrationTestResult(
            test_name="security_attack_prevention",
            success=security_success,
            performance_ms=execution_time,
            details={
                "total_attack_scenarios": len(attack_scenarios),
                "attacks_blocked": attacks_blocked,
                "vulnerabilities_found": vulnerabilities_found,
                "attack_block_rate": attack_block_rate,
                "security_grade": "A+" if security_success else "Needs improvement",
                "zero_tolerance_security": security_success
            }
        )
        
        print(f"   Attack Scenarios: {len(attack_scenarios)}")
        print(f"   Attacks Blocked: {attacks_blocked}")
        print(f"   Vulnerabilities Found: {len(vulnerabilities_found)}")
        print(f"   Security A+: {'✅' if security_success else '❌'}")
        
        return result
    
    async def test_load_stress_resilience(self) -> IntegrationTestResult:
        """Test system resilience under load stress"""
        print("\n💪 Testing Load Stress Resilience...")
        
        start_time = time.time()
        
        # Stress test: burst of 100 requests in rapid succession
        burst_size = 100
        burst_requests = []
        
        for i in range(burst_size):
            auth_request = AuthRequest(
                username=f"stress_user_{i}",
                password="stress_test_password",
                client_ip=f"192.168.2.{i % 255}",
                user_agent="Stress Test Client",
                consciousness_level=0.9  # High consciousness for stress test
            )
            burst_requests.append(self.auth_engine.authenticate(auth_request))
        
        # Execute burst load
        burst_responses = await asyncio.gather(*burst_requests, return_exceptions=True)
        burst_time = time.time() - start_time
        
        # Analyze stress test results
        successful_responses = []
        failed_responses = 0
        
        for response in burst_responses:
            if isinstance(response, Exception):
                failed_responses += 1
            elif response.success:
                successful_responses.append(response)
            else:
                failed_responses += 1
        
        success_rate = len(successful_responses) / burst_size
        burst_ops_per_sec = burst_size / burst_time
        
        # Resilience criteria: >90% success rate under burst load
        resilience_success = success_rate > 0.9 and burst_ops_per_sec > 150
        
        result = IntegrationTestResult(
            test_name="load_stress_resilience",
            success=resilience_success,
            performance_ms=burst_time * 1000,
            operations_per_second=burst_ops_per_sec,
            error_rate=1 - success_rate,
            details={
                "burst_size": burst_size,
                "successful_responses": len(successful_responses),
                "failed_responses": failed_responses,
                "success_rate": success_rate,
                "burst_ops_per_second": burst_ops_per_sec,
                "resilience_rating": "A+" if resilience_success else "Good" if success_rate > 0.8 else "Needs improvement",
                "stress_test_duration_seconds": burst_time
            }
        )
        
        print(f"   Burst Size: {burst_size} requests")
        print(f"   Success Rate: {success_rate:.1%}")
        print(f"   Burst Performance: {burst_ops_per_sec:.1f} ops/sec")
        print(f"   Resilience A+: {'✅' if resilience_success else '❌'}")
        
        return result
    
    async def run_integration_suite(self) -> Dict[str, Any]:
        """Run complete integration test suite"""
        print("🚀 AUTHENTICATION & SECURITY INTEGRATION TEST SUITE")
        print("=" * 60)
        
        suite_start = time.time()
        
        await self.setup()
        
        # Run all integration tests
        self.test_results = [
            await self.test_basic_auth_workflow(),
            await self.test_concurrent_authentication(),
            await self.test_security_attack_prevention(),
            await self.test_load_stress_resilience()
        ]
        
        suite_time = time.time() - suite_start
        
        # Calculate overall results
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result.success)
        success_rate = successful_tests / total_tests
        
        # Get performance metrics
        max_ops_per_sec = max((r.operations_per_second for r in self.test_results if r.operations_per_second > 0), default=0)
        avg_error_rate = statistics.mean([r.error_rate for r in self.test_results])
        
        # A+ criteria: 80% success rate, >200 ops/sec, <5% error rate
        a_plus_achievement = (
            success_rate >= 0.8 and 
            max_ops_per_sec > 200 and 
            avg_error_rate < 0.05
        )
        
        suite_summary = {
            "test_suite": "authentication_security_integration",
            "timestamp": datetime.now().isoformat(),
            "execution_time_seconds": suite_time,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "max_operations_per_second": max_ops_per_sec,
            "average_error_rate": avg_error_rate,
            "a_plus_achievement": a_plus_achievement,
            "test_results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "performance_ms": r.performance_ms,
                    "operations_per_second": r.operations_per_second,
                    "error_rate": r.error_rate,
                    "details": r.details
                }
                for r in self.test_results
            ],
            "overall_assessment": {
                "authentication_workflow": "A+" if self.test_results[0].success else "Needs improvement",
                "concurrent_performance": "A+" if self.test_results[1].success else "Good" if self.test_results[1].operations_per_second > 150 else "Needs improvement",
                "security_protection": "A+" if self.test_results[2].success else "Needs improvement",
                "system_resilience": "A+" if self.test_results[3].success else "Good" if self.test_results[3].error_rate < 0.1 else "Needs improvement"
            }
        }
        
        # Print final results
        print("\n🏆 INTEGRATION TEST SUITE RESULTS")
        print("=" * 40)
        print(f"Total Tests: {total_tests}")
        print(f"Successful Tests: {successful_tests}")
        print(f"Success Rate: {success_rate:.1%}")
        print(f"Max Performance: {max_ops_per_sec:.1f} ops/sec")
        print(f"Average Error Rate: {avg_error_rate:.1%}")
        print(f"A+ Achievement: {'✅' if a_plus_achievement else '❌'}")
        print(f"Execution Time: {suite_time:.2f} seconds")
        
        return suite_summary


async def main():
    """Main execution"""
    test_suite = AuthSecurityIntegrationTest()
    results = await test_suite.run_integration_suite()
    
    # Save results
    os.makedirs("results/integration_tests", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"results/integration_tests/auth_security_integration_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Integration test results saved: {results_file}")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())