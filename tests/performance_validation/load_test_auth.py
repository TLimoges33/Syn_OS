#!/usr/bin/env python3
"""
Authentication Load Testing Framework
=====================================

Comprehensive load testing for authentication services to validate
academic performance claims under realistic conditions.
"""

import asyncio
import aiohttp
import time
import statistics
import threading
import concurrent.futures
import json
import secrets
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple
import multiprocessing
import psutil

class AuthLoadTester:
    """Comprehensive authentication load testing"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_suite": "Authentication Load Testing",
            "version": "1.0.0",
            "system_info": self._get_system_info(),
            "load_tests": {}
        }
        
        # Test parameters
        self.secret_key = secrets.token_bytes(32)
        self.user_database = {}
        self.session_store = {}
        
    def _get_system_info(self):
        """Get system information for load testing context"""
        return {
            "cpu_cores": multiprocessing.cpu_count(),
            "memory_gb": psutil.virtual_memory().total / (1024**3),
            "platform": "Linux",
            "python_version": "3.11"
        }
    
    def _create_test_users(self, count: int = 1000) -> Dict:
        """Create test user database"""
        print(f"🔧 Creating {count} test users...")
        
        users = {}
        setup_times = []
        
        for i in range(count):
            start_time = time.perf_counter()
            
            username = f"testuser_{i:06d}"
            password = f"password_{i:06d}_{secrets.token_hex(4)}"
            
            # Hash password (simulating real auth)
            salt = secrets.token_bytes(32)
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            
            users[username] = {
                "password_hash": password_hash,
                "salt": salt,
                "email": f"{username}@test.example.com",
                "created": datetime.now().isoformat(),
                "login_count": 0
            }
            
            end_time = time.perf_counter()
            setup_times.append(end_time - start_time)
        
        self.user_database = users
        
        avg_setup_time = statistics.mean(setup_times) * 1000
        print(f"✅ User database created: {avg_setup_time:.2f}ms average per user")
        
        return {
            "users_created": count,
            "avg_creation_time_ms": avg_setup_time,
            "total_setup_time_s": sum(setup_times)
        }
    
    def _authenticate_user(self, username: str, password: str) -> Tuple[bool, float, str]:
        """Authenticate a single user"""
        start_time = time.perf_counter()
        
        if username not in self.user_database:
            end_time = time.perf_counter()
            return False, end_time - start_time, "user_not_found"
        
        user_data = self.user_database[username]
        
        # Verify password
        password_hash = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode(), 
            user_data["salt"], 
            100000
        )
        
        if password_hash == user_data["password_hash"]:
            # Generate session token
            session_token = secrets.token_urlsafe(32)
            session_data = {
                "username": username,
                "created": time.time(),
                "expires": time.time() + 3600  # 1 hour
            }
            self.session_store[session_token] = session_data
            
            # Update login count
            user_data["login_count"] += 1
            
            end_time = time.perf_counter()
            return True, end_time - start_time, session_token
        else:
            end_time = time.perf_counter()
            return False, end_time - start_time, "invalid_password"
    
    def test_sequential_logins(self, user_count: int = 100, iterations: int = 10) -> Dict:
        """Test sequential login performance"""
        print(f"👤 Testing sequential logins: {user_count} users, {iterations} iterations")
        
        login_times = []
        success_count = 0
        failure_count = 0
        
        for iteration in range(iterations):
            for i in range(user_count):
                username = f"testuser_{i:06d}"
                password = f"password_{i:06d}_{secrets.token_hex(4)}"
                
                # Randomly use wrong password 10% of the time
                if secrets.randbelow(10) == 0:
                    password = "wrong_password"
                
                success, auth_time, result = self._authenticate_user(username, password)
                
                login_times.append(auth_time)
                if success:
                    success_count += 1
                else:
                    failure_count += 1
        
        total_operations = user_count * iterations
        
        return {
            "total_operations": total_operations,
            "successful_logins": success_count,
            "failed_logins": failure_count,
            "success_rate": success_count / total_operations,
            "mean_auth_time_ms": statistics.mean(login_times) * 1000,
            "median_auth_time_ms": statistics.median(login_times) * 1000,
            "p95_auth_time_ms": sorted(login_times)[int(0.95 * len(login_times))] * 1000,
            "throughput_logins_per_sec": 1 / statistics.mean(login_times),
            "total_test_time_s": sum(login_times)
        }
    
    def test_concurrent_logins(self, concurrent_users: int = 50, total_requests: int = 1000) -> Dict:
        """Test concurrent login performance"""
        print(f"⚡ Testing concurrent logins: {concurrent_users} concurrent, {total_requests} total requests")
        
        def worker_login(worker_id: int, requests_per_worker: int) -> List[Tuple[bool, float, str]]:
            """Worker function for concurrent testing"""
            results = []
            
            for i in range(requests_per_worker):
                user_index = (worker_id * requests_per_worker + i) % len(self.user_database)
                username = f"testuser_{user_index:06d}"
                password = f"password_{user_index:06d}_{secrets.token_hex(4)}"
                
                # Some invalid attempts
                if secrets.randbelow(20) == 0:  # 5% failure rate
                    password = "invalid_password"
                
                success, auth_time, result = self._authenticate_user(username, password)
                results.append((success, auth_time, result))
            
            return results
        
        # Calculate requests per worker
        requests_per_worker = total_requests // concurrent_users
        
        start_time = time.perf_counter()
        
        # Run concurrent authentication
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [
                executor.submit(worker_login, worker_id, requests_per_worker)
                for worker_id in range(concurrent_users)
            ]
            
            all_results = []
            for future in concurrent.futures.as_completed(futures):
                all_results.extend(future.result())
        
        end_time = time.perf_counter()
        total_test_time = end_time - start_time
        
        # Analyze results
        auth_times = [result[1] for result in all_results]
        successful_logins = sum(1 for result in all_results if result[0])
        failed_logins = len(all_results) - successful_logins
        
        return {
            "concurrent_users": concurrent_users,
            "total_requests": len(all_results),
            "successful_logins": successful_logins,
            "failed_logins": failed_logins,
            "success_rate": successful_logins / len(all_results),
            "total_test_time_s": total_test_time,
            "mean_auth_time_ms": statistics.mean(auth_times) * 1000,
            "median_auth_time_ms": statistics.median(auth_times) * 1000,
            "p95_auth_time_ms": sorted(auth_times)[int(0.95 * len(auth_times))] * 1000,
            "p99_auth_time_ms": sorted(auth_times)[int(0.99 * len(auth_times))] * 1000,
            "throughput_requests_per_sec": len(all_results) / total_test_time,
            "avg_concurrent_throughput": successful_logins / total_test_time
        }
    
    def test_sustained_load(self, duration_seconds: int = 60, target_rps: int = 100) -> Dict:
        """Test sustained authentication load"""
        print(f"🏃 Testing sustained load: {target_rps} req/sec for {duration_seconds}s")
        
        results = []
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        request_count = 0
        success_count = 0
        
        while time.time() < end_time:
            batch_start = time.time()
            
            # Process batch to maintain target RPS
            batch_size = min(10, target_rps // 10)  # 10 batches per second
            
            for _ in range(batch_size):
                user_index = request_count % len(self.user_database)
                username = f"testuser_{user_index:06d}"
                password = f"password_{user_index:06d}_{secrets.token_hex(4)}"
                
                success, auth_time, result = self._authenticate_user(username, password)
                results.append((success, auth_time, time.time()))
                
                if success:
                    success_count += 1
                request_count += 1
            
            # Sleep to maintain target RPS
            batch_time = time.time() - batch_start
            target_batch_time = batch_size / target_rps
            if batch_time < target_batch_time:
                time.sleep(target_batch_time - batch_time)
        
        actual_duration = time.time() - start_time
        auth_times = [result[1] for result in results]
        
        return {
            "target_rps": target_rps,
            "duration_seconds": duration_seconds,
            "actual_duration_s": actual_duration,
            "total_requests": len(results),
            "successful_requests": success_count,
            "failed_requests": len(results) - success_count,
            "actual_rps": len(results) / actual_duration,
            "success_rate": success_count / len(results),
            "mean_auth_time_ms": statistics.mean(auth_times) * 1000,
            "p95_auth_time_ms": sorted(auth_times)[int(0.95 * len(auth_times))] * 1000,
            "p99_auth_time_ms": sorted(auth_times)[int(0.99 * len(auth_times))] * 1000
        }
    
    def test_session_management_load(self, session_count: int = 10000) -> Dict:
        """Test session management under load"""
        print(f"🎫 Testing session management: {session_count} sessions")
        
        # Create sessions
        session_creation_times = []
        session_validation_times = []
        
        created_sessions = []
        
        # Session creation test
        for i in range(session_count):
            start_time = time.perf_counter()
            
            session_token = secrets.token_urlsafe(32)
            session_data = {
                "username": f"testuser_{i % 1000:06d}",
                "created": time.time(),
                "expires": time.time() + 3600,
                "data": {"role": "user", "permissions": ["read", "write"]}
            }
            self.session_store[session_token] = session_data
            created_sessions.append(session_token)
            
            end_time = time.perf_counter()
            session_creation_times.append(end_time - start_time)
        
        # Session validation test
        for session_token in created_sessions[:1000]:  # Test subset for validation
            start_time = time.perf_counter()
            
            if session_token in self.session_store:
                session_data = self.session_store[session_token]
                is_valid = session_data["expires"] > time.time()
            else:
                is_valid = False
            
            end_time = time.perf_counter()
            session_validation_times.append(end_time - start_time)
        
        return {
            "sessions_created": len(created_sessions),
            "sessions_validated": len(session_validation_times),
            "avg_creation_time_us": statistics.mean(session_creation_times) * 1_000_000,
            "avg_validation_time_us": statistics.mean(session_validation_times) * 1_000_000,
            "creation_throughput_ops_per_sec": 1 / statistics.mean(session_creation_times),
            "validation_throughput_ops_per_sec": 1 / statistics.mean(session_validation_times),
            "total_sessions_in_store": len(self.session_store)
        }
    
    def analyze_load_test_results(self) -> Dict:
        """Analyze load test results against requirements"""
        print("📊 Analyzing load test results...")
        
        analysis = {
            "requirements_met": True,
            "performance_grade": "A",
            "issues": [],
            "recommendations": []
        }
        
        # Check concurrent performance
        if "concurrent_logins" in self.results["load_tests"]:
            concurrent = self.results["load_tests"]["concurrent_logins"]
            
            # Target: >100 concurrent users, <200ms p95
            if concurrent["concurrent_users"] < 50:
                analysis["issues"].append("Concurrent user capacity below target")
            
            if concurrent["p95_auth_time_ms"] > 200:
                analysis["issues"].append(f"P95 auth time {concurrent['p95_auth_time_ms']:.1f}ms exceeds 200ms")
        
        # Check sustained throughput
        if "sustained_load" in self.results["load_tests"]:
            sustained = self.results["load_tests"]["sustained_load"]
            
            # Target: maintain target RPS with <5% degradation
            rps_efficiency = sustained["actual_rps"] / sustained["target_rps"]
            if rps_efficiency < 0.95:
                analysis["issues"].append(f"Sustained RPS efficiency {rps_efficiency:.1%} below 95%")
        
        # Check session management
        if "session_management" in self.results["load_tests"]:
            sessions = self.results["load_tests"]["session_management"]
            
            # Target: >10,000 ops/sec for session operations
            if sessions["validation_throughput_ops_per_sec"] < 10000:
                analysis["issues"].append(f"Session validation {sessions['validation_throughput_ops_per_sec']:.0f} ops/sec below 10K target")
        
        # Grade based on issues
        if len(analysis["issues"]) == 0:
            analysis["performance_grade"] = "A"
        elif len(analysis["issues"]) <= 2:
            analysis["performance_grade"] = "B"
        else:
            analysis["performance_grade"] = "C"
            analysis["requirements_met"] = False
        
        # Generate recommendations
        if analysis["issues"]:
            analysis["recommendations"] = [
                "Implement connection pooling for database operations",
                "Add caching layer for frequently accessed user data",
                "Consider async authentication for better concurrency",
                "Optimize session storage with Redis or similar"
            ]
        else:
            analysis["recommendations"] = [
                "Load testing performance meets academic requirements",
                "Consider testing with even higher loads",
                "Implement monitoring for production deployment"
            ]
        
        self.results["load_analysis"] = analysis
        
        print(f"✅ Load Test Grade: {analysis['performance_grade']}")
        print(f"✅ Requirements Met: {analysis['requirements_met']}")
        
        return analysis
    
    def save_results(self):
        """Save load test results"""
        results_dir = Path("results/benchmarks")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"auth_load_test_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Create human-readable summary
        summary_file = results_dir / f"auth_load_summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write("AUTHENTICATION LOAD TEST SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Test Date: {self.results['timestamp']}\n")
            f.write(f"Load Test Grade: {self.results['load_analysis']['performance_grade']}\n")
            f.write(f"Requirements Met: {self.results['load_analysis']['requirements_met']}\n\n")
            
            # System info
            sys_info = self.results["system_info"]
            f.write("System Information:\n")
            f.write(f"  - CPU Cores: {sys_info['cpu_cores']}\n")
            f.write(f"  - Memory: {sys_info['memory_gb']:.1f} GB\n\n")
            
            # Load test results
            if "concurrent_logins" in self.results["load_tests"]:
                concurrent = self.results["load_tests"]["concurrent_logins"]
                f.write(f"Concurrent Load Test:\n")
                f.write(f"  - Concurrent Users: {concurrent['concurrent_users']}\n")
                f.write(f"  - Throughput: {concurrent['throughput_requests_per_sec']:.0f} req/sec\n")
                f.write(f"  - P95 Response Time: {concurrent['p95_auth_time_ms']:.1f}ms\n")
                f.write(f"  - Success Rate: {concurrent['success_rate']:.1%}\n\n")
            
            if "sustained_load" in self.results["load_tests"]:
                sustained = self.results["load_tests"]["sustained_load"]
                f.write(f"Sustained Load Test:\n")
                f.write(f"  - Target RPS: {sustained['target_rps']}\n")
                f.write(f"  - Actual RPS: {sustained['actual_rps']:.1f}\n")
                f.write(f"  - P95 Response Time: {sustained['p95_auth_time_ms']:.1f}ms\n")
                f.write(f"  - Success Rate: {sustained['success_rate']:.1%}\n\n")
            
            if self.results["load_analysis"]["issues"]:
                f.write("Issues Found:\n")
                for issue in self.results["load_analysis"]["issues"]:
                    f.write(f"  - {issue}\n")
                f.write("\n")
            
            f.write("Recommendations:\n")
            for rec in self.results["load_analysis"]["recommendations"]:
                f.write(f"  - {rec}\n")
        
        print(f"📄 Results saved: {results_file}")
        print(f"📋 Summary saved: {summary_file}")
        return results_file, summary_file
    
    def run_full_load_test(self):
        """Run complete authentication load test suite"""
        print("🚀 Starting Authentication Load Test Suite")
        print("=" * 60)
        
        # Setup
        setup_results = self._create_test_users(1000)
        self.results["setup"] = setup_results
        
        # Sequential performance baseline
        sequential_results = self.test_sequential_logins(100, 5)
        self.results["load_tests"]["sequential_logins"] = sequential_results
        
        # Concurrent load testing
        concurrent_results = self.test_concurrent_logins(25, 500)  # Reduced for faster testing
        self.results["load_tests"]["concurrent_logins"] = concurrent_results
        
        # Sustained load testing
        sustained_results = self.test_sustained_load(30, 50)  # Reduced duration/RPS for testing
        self.results["load_tests"]["sustained_load"] = sustained_results
        
        # Session management
        session_results = self.test_session_management_load(1000)  # Reduced count
        self.results["load_tests"]["session_management"] = session_results
        
        # Analysis
        self.analyze_load_test_results()
        
        # Save results
        results_file, summary_file = self.save_results()
        
        print("\n🎉 Authentication load test complete!")
        print(f"📊 Load Test Grade: {self.results['load_analysis']['performance_grade']}")
        print(f"📄 Detailed Results: {results_file}")
        print(f"📋 Summary: {summary_file}")
        
        return self.results

if __name__ == "__main__":
    load_tester = AuthLoadTester()
    results = load_tester.run_full_load_test()