#!/usr/bin/env python3
"""
Authentication Performance Benchmarking
========================================

Measures actual authentication performance with real metrics
to validate security claims made in academic documentation.
"""

import time
import asyncio
import statistics
import json
from pathlib import Path
from datetime import datetime
import hashlib
import hmac
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class AuthBenchmarker:
    """Benchmarks authentication and encryption performance"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_suite": "Authentication Performance",
            "version": "1.0.0",
            "benchmarks": {}
        }
        
        # Create test data
        self.test_passwords = [
            "simple_password",
            "complex_P@ssw0rd_123!",
            "very_long_password_with_many_characters_and_symbols_!@#$%^&*()",
            "unicode_пароль_密码_कूटशब्द"
        ]
        
        self.test_data_sizes = [1024, 4096, 16384, 65536]  # 1KB to 64KB
        
    def benchmark_password_hashing(self, iterations=1000):
        """Benchmark password hashing operations"""
        print("🔐 Benchmarking password hashing...")
        
        results = {}
        
        for password in self.test_passwords:
            times = []
            
            for _ in range(iterations):
                start_time = time.perf_counter()
                
                # PBKDF2 with SHA-256 (standard secure hashing)
                salt = secrets.token_bytes(32)
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,  # OWASP recommended minimum
                )
                key = kdf.derive(password.encode())
                
                end_time = time.perf_counter()
                times.append(end_time - start_time)
            
            results[f"password_len_{len(password)}"] = {
                "mean_time_ms": statistics.mean(times) * 1000,
                "median_time_ms": statistics.median(times) * 1000,
                "std_dev_ms": statistics.stdev(times) * 1000,
                "min_time_ms": min(times) * 1000,
                "max_time_ms": max(times) * 1000,
                "iterations": iterations
            }
        
        self.results["benchmarks"]["password_hashing"] = results
        
        avg_time = statistics.mean([r["mean_time_ms"] for r in results.values()])
        print(f"✅ Password hashing: {avg_time:.2f}ms average")
        
    def benchmark_jwt_operations(self, iterations=10000):
        """Benchmark JWT-like token operations"""
        print("🎫 Benchmarking JWT operations...")
        
        # Simple JWT-like token simulation
        secret_key = secrets.token_bytes(32)
        
        create_times = []
        verify_times = []
        
        for _ in range(iterations):
            # Token creation benchmark
            start_time = time.perf_counter()
            
            header = base64.b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode()
            payload = base64.b64encode(json.dumps({
                "user_id": "test_user",
                "exp": int(time.time()) + 3600,
                "iat": int(time.time())
            }).encode()).decode()
            
            signature = hmac.new(
                secret_key,
                f"{header}.{payload}".encode(),
                hashlib.sha256
            ).hexdigest()
            
            token = f"{header}.{payload}.{signature}"
            
            end_time = time.perf_counter()
            create_times.append(end_time - start_time)
            
            # Token verification benchmark
            start_time = time.perf_counter()
            
            header_b64, payload_b64, signature_received = token.split('.')
            expected_signature = hmac.new(
                secret_key,
                f"{header_b64}.{payload_b64}".encode(),
                hashlib.sha256
            ).hexdigest()
            
            is_valid = hmac.compare_digest(signature_received, expected_signature)
            
            end_time = time.perf_counter()
            verify_times.append(end_time - start_time)
        
        self.results["benchmarks"]["jwt_operations"] = {
            "create": {
                "mean_time_us": statistics.mean(create_times) * 1_000_000,
                "median_time_us": statistics.median(create_times) * 1_000_000,
                "std_dev_us": statistics.stdev(create_times) * 1_000_000,
                "throughput_ops_per_sec": 1 / statistics.mean(create_times)
            },
            "verify": {
                "mean_time_us": statistics.mean(verify_times) * 1_000_000,
                "median_time_us": statistics.median(verify_times) * 1_000_000,
                "std_dev_us": statistics.stdev(verify_times) * 1_000_000,
                "throughput_ops_per_sec": 1 / statistics.mean(verify_times)
            },
            "iterations": iterations
        }
        
        create_avg = statistics.mean(create_times) * 1_000_000
        verify_avg = statistics.mean(verify_times) * 1_000_000
        print(f"✅ JWT create: {create_avg:.2f}μs, verify: {verify_avg:.2f}μs")
    
    def benchmark_encryption_operations(self, iterations=1000):
        """Benchmark symmetric encryption operations"""
        print("🔒 Benchmarking encryption operations...")
        
        # Generate encryption key
        key = Fernet.generate_key()
        cipher = Fernet(key)
        
        results = {}
        
        for data_size in self.test_data_sizes:
            test_data = secrets.token_bytes(data_size)
            
            encrypt_times = []
            decrypt_times = []
            
            for _ in range(iterations):
                # Encryption benchmark
                start_time = time.perf_counter()
                encrypted_data = cipher.encrypt(test_data)
                end_time = time.perf_counter()
                encrypt_times.append(end_time - start_time)
                
                # Decryption benchmark
                start_time = time.perf_counter()
                decrypted_data = cipher.decrypt(encrypted_data)
                end_time = time.perf_counter()
                decrypt_times.append(end_time - start_time)
                
                # Verify data integrity
                assert decrypted_data == test_data
            
            results[f"data_size_{data_size}_bytes"] = {
                "encrypt": {
                    "mean_time_ms": statistics.mean(encrypt_times) * 1000,
                    "throughput_mb_per_sec": (data_size / statistics.mean(encrypt_times)) / (1024 * 1024)
                },
                "decrypt": {
                    "mean_time_ms": statistics.mean(decrypt_times) * 1000,
                    "throughput_mb_per_sec": (data_size / statistics.mean(decrypt_times)) / (1024 * 1024)
                }
            }
        
        self.results["benchmarks"]["encryption"] = results
        
        # Calculate average throughput
        avg_encrypt_throughput = statistics.mean([
            r["encrypt"]["throughput_mb_per_sec"] for r in results.values()
        ])
        avg_decrypt_throughput = statistics.mean([
            r["decrypt"]["throughput_mb_per_sec"] for r in results.values()
        ])
        
        print(f"✅ Encryption: {avg_encrypt_throughput:.2f} MB/s")
        print(f"✅ Decryption: {avg_decrypt_throughput:.2f} MB/s")
    
    def benchmark_login_simulation(self, iterations=1000):
        """Simulate complete login flow performance"""
        print("👤 Benchmarking complete login flow...")
        
        # Simulate user database with pre-hashed passwords
        user_db = {}
        setup_times = []
        
        # Setup phase - create test users
        for i in range(100):
            start_time = time.perf_counter()
            
            username = f"user_{i}"
            password = f"password_{i}"
            salt = secrets.token_bytes(32)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            password_hash = kdf.derive(password.encode())
            
            user_db[username] = {
                "password_hash": password_hash,
                "salt": salt
            }
            
            end_time = time.perf_counter()
            setup_times.append(end_time - start_time)
        
        # Login simulation
        login_times = []
        successful_logins = 0
        
        for _ in range(iterations):
            # Random user login attempt
            username = f"user_{secrets.randbelow(100)}"
            password = f"password_{secrets.randbelow(100)}"  # Sometimes wrong password
            
            start_time = time.perf_counter()
            
            if username in user_db:
                user_data = user_db[username]
                
                # Verify password
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=user_data["salt"],
                    iterations=100000,
                )
                
                try:
                    kdf.verify(password.encode(), user_data["password_hash"])
                    successful_logins += 1
                    
                    # Generate session token on successful login
                    session_token = secrets.token_urlsafe(32)
                    
                except Exception:
                    pass  # Invalid password
            
            end_time = time.perf_counter()
            login_times.append(end_time - start_time)
        
        self.results["benchmarks"]["login_simulation"] = {
            "setup_phase": {
                "users_created": len(user_db),
                "avg_user_creation_ms": statistics.mean(setup_times) * 1000
            },
            "login_attempts": {
                "total_attempts": iterations,
                "successful_logins": successful_logins,
                "success_rate": successful_logins / iterations,
                "mean_login_time_ms": statistics.mean(login_times) * 1000,
                "median_login_time_ms": statistics.median(login_times) * 1000,
                "throughput_logins_per_sec": 1 / statistics.mean(login_times)
            }
        }
        
        avg_login_time = statistics.mean(login_times) * 1000
        throughput = 1 / statistics.mean(login_times)
        print(f"✅ Login flow: {avg_login_time:.2f}ms average, {throughput:.0f} logins/sec")
    
    def analyze_performance_requirements(self):
        """Analyze if performance meets academic requirements"""
        print("📊 Analyzing performance against requirements...")
        
        analysis = {
            "requirements_met": True,
            "performance_grade": "A",
            "issues": [],
            "recommendations": []
        }
        
        # Check authentication requirements (< 100ms per CLAUDE.md)
        if "login_simulation" in self.results["benchmarks"]:
            login_time = self.results["benchmarks"]["login_simulation"]["login_attempts"]["mean_login_time_ms"]
            if login_time > 100:
                analysis["requirements_met"] = False
                analysis["issues"].append(f"Login time {login_time:.1f}ms exceeds 100ms requirement")
                analysis["performance_grade"] = "C"
        
        # Check JWT performance (should be < 1ms for creation/verification)
        if "jwt_operations" in self.results["benchmarks"]:
            jwt_create = self.results["benchmarks"]["jwt_operations"]["create"]["mean_time_us"] / 1000
            jwt_verify = self.results["benchmarks"]["jwt_operations"]["verify"]["mean_time_us"] / 1000
            
            if jwt_create > 1 or jwt_verify > 1:
                analysis["issues"].append(f"JWT operations too slow: create {jwt_create:.2f}ms, verify {jwt_verify:.2f}ms")
        
        # Check encryption throughput (should be > 10 MB/s)
        if "encryption" in self.results["benchmarks"]:
            for size_key, data in self.results["benchmarks"]["encryption"].items():
                if data["encrypt"]["throughput_mb_per_sec"] < 10:
                    analysis["issues"].append(f"Encryption throughput too low: {data['encrypt']['throughput_mb_per_sec']:.1f} MB/s")
        
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
                "Consider optimizing hash iteration counts for development",
                "Implement connection pooling for better throughput",
                "Add caching layer for frequently accessed user data",
                "Profile and optimize cryptographic operations"
            ]
        else:
            analysis["recommendations"] = [
                "Performance meets academic requirements",
                "Consider load testing with concurrent users",
                "Implement monitoring for production deployment"
            ]
        
        self.results["performance_analysis"] = analysis
        
        print(f"✅ Performance Grade: {analysis['performance_grade']}")
        print(f"✅ Requirements Met: {analysis['requirements_met']}")
        
    def save_results(self):
        """Save benchmark results"""
        results_dir = Path("results/benchmarks")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"auth_benchmark_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Create human-readable summary
        summary_file = results_dir / f"auth_summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write("AUTHENTICATION PERFORMANCE BENCHMARK\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Test Date: {self.results['timestamp']}\n")
            f.write(f"Performance Grade: {self.results['performance_analysis']['performance_grade']}\n")
            f.write(f"Requirements Met: {self.results['performance_analysis']['requirements_met']}\n\n")
            
            # Summary metrics
            if "login_simulation" in self.results["benchmarks"]:
                login_data = self.results["benchmarks"]["login_simulation"]["login_attempts"]
                f.write(f"Login Performance:\n")
                f.write(f"  - Average Time: {login_data['mean_login_time_ms']:.2f}ms\n")
                f.write(f"  - Throughput: {login_data['throughput_logins_per_sec']:.0f} logins/sec\n")
                f.write(f"  - Success Rate: {login_data['success_rate']:.1%}\n\n")
            
            if "jwt_operations" in self.results["benchmarks"]:
                jwt_data = self.results["benchmarks"]["jwt_operations"]
                f.write(f"JWT Performance:\n")
                f.write(f"  - Create: {jwt_data['create']['mean_time_us']:.1f}μs\n")
                f.write(f"  - Verify: {jwt_data['verify']['mean_time_us']:.1f}μs\n\n")
            
            if self.results["performance_analysis"]["issues"]:
                f.write("Issues Found:\n")
                for issue in self.results["performance_analysis"]["issues"]:
                    f.write(f"  - {issue}\n")
                f.write("\n")
            
            f.write("Recommendations:\n")
            for rec in self.results["performance_analysis"]["recommendations"]:
                f.write(f"  - {rec}\n")
        
        print(f"📄 Results saved: {results_file}")
        print(f"📋 Summary saved: {summary_file}")
        return results_file, summary_file
    
    def run_full_benchmark(self):
        """Run complete authentication benchmark suite"""
        print("🚀 Starting Authentication Performance Benchmark")
        print("=" * 60)
        
        self.benchmark_password_hashing()
        self.benchmark_jwt_operations()
        self.benchmark_encryption_operations()
        self.benchmark_login_simulation()
        self.analyze_performance_requirements()
        
        results_file, summary_file = self.save_results()
        
        print("\n🎉 Authentication benchmark complete!")
        print(f"📊 Performance Grade: {self.results['performance_analysis']['performance_grade']}")
        print(f"📄 Detailed Results: {results_file}")
        print(f"📋 Summary: {summary_file}")
        
        return self.results

if __name__ == "__main__":
    benchmarker = AuthBenchmarker()
    results = benchmarker.run_full_benchmark()