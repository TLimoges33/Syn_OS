#!/usr/bin/env python3
"""
Quick Performance Assessment
============================

Rapid performance validation for academic progress tracking.
"""

import time
import statistics
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json
from datetime import datetime

def quick_auth_benchmark():
    """Quick authentication performance test"""
    print("🔐 Quick authentication benchmark...")
    
    # Quick password hashing test
    password = "test_password_123"
    salt = secrets.token_bytes(32)
    
    hash_times = []
    for _ in range(100):  # Reduced iterations
        start = time.perf_counter()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password.encode())
        end = time.perf_counter()
        hash_times.append(end - start)
    
    avg_hash_time = statistics.mean(hash_times) * 1000
    print(f"✅ Password hashing: {avg_hash_time:.2f}ms average")
    
    # Quick encryption test
    cipher = Fernet.generate_key()
    fernet = Fernet(cipher)
    test_data = b"x" * 1024  # 1KB
    
    encrypt_times = []
    for _ in range(1000):
        start = time.perf_counter()
        encrypted = fernet.encrypt(test_data)
        end = time.perf_counter()
        encrypt_times.append(end - start)
    
    avg_encrypt_time = statistics.mean(encrypt_times) * 1000
    throughput = (1024 / statistics.mean(encrypt_times)) / (1024**2)  # MB/s
    print(f"✅ Encryption: {avg_encrypt_time:.2f}ms average, {throughput:.1f} MB/s")
    
    return {
        "password_hashing_ms": avg_hash_time,
        "encryption_ms": avg_encrypt_time,
        "encryption_throughput_mbps": throughput,
        "meets_requirements": avg_hash_time < 200 and throughput > 10
    }

def quick_system_benchmark():
    """Quick system performance test"""
    print("💻 Quick system benchmark...")
    
    # CPU performance test
    start = time.perf_counter()
    for _ in range(100000):
        hashlib.sha256(b"test").hexdigest()
    end = time.perf_counter()
    
    cpu_ops_per_sec = 100000 / (end - start)
    print(f"✅ CPU: {cpu_ops_per_sec:.0f} hash ops/sec")
    
    # Memory test
    start = time.perf_counter()
    large_data = bytearray(10 * 1024 * 1024)  # 10MB
    end = time.perf_counter()
    
    memory_alloc_mbps = 10 / (end - start)
    print(f"✅ Memory allocation: {memory_alloc_mbps:.0f} MB/s")
    
    return {
        "cpu_ops_per_sec": cpu_ops_per_sec,
        "memory_alloc_mbps": memory_alloc_mbps,
        "meets_requirements": cpu_ops_per_sec > 50000 and memory_alloc_mbps > 100
    }

if __name__ == "__main__":
    print("🚀 Quick Performance Assessment")
    print("=" * 40)
    
    auth_results = quick_auth_benchmark()
    system_results = quick_system_benchmark()
    
    print("\n📊 Quick Assessment Results:")
    print(f"Auth Performance: {'✅ PASS' if auth_results['meets_requirements'] else '❌ FAIL'}")
    print(f"System Performance: {'✅ PASS' if system_results['meets_requirements'] else '❌ FAIL'}")
    
    # Save quick results
    results = {
        "timestamp": datetime.now().isoformat(),
        "auth": auth_results,
        "system": system_results,
        "overall_pass": auth_results['meets_requirements'] and system_results['meets_requirements']
    }
    
    with open("results/benchmarks/quick_assessment.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to results/benchmarks/quick_assessment.json")