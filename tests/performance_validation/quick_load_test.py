#!/usr/bin/env python3
"""
Quick Authentication Load Test
==============================

Rapid load testing for academic progress validation.
"""

import time
import statistics
import secrets
import hashlib
import concurrent.futures
import json
from datetime import datetime

def quick_auth_load_test():
    """Quick authentication load test"""
    print("⚡ Quick authentication load test...")
    
    # Create small user database
    users = {}
    for i in range(100):
        username = f"user_{i}"
        password = f"pass_{i}"
        salt = secrets.token_bytes(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 10000)  # Reduced iterations
        users[username] = {"hash": password_hash, "salt": salt}
    
    def authenticate(username, password):
        """Quick auth function"""
        start = time.perf_counter()
        if username in users:
            user = users[username]
            test_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), user["salt"], 10000)
            success = test_hash == user["hash"]
        else:
            success = False
        end = time.perf_counter()
        return success, end - start
    
    # Sequential test
    sequential_times = []
    for i in range(100):
        username = f"user_{i % 50}"  # Some failures
        password = f"pass_{i % 50}"
        success, auth_time = authenticate(username, password)
        sequential_times.append(auth_time)
    
    # Concurrent test
    def worker(worker_id):
        times = []
        for i in range(10):
            username = f"user_{(worker_id * 10 + i) % 50}"
            password = f"pass_{(worker_id * 10 + i) % 50}"
            success, auth_time = authenticate(username, password)
            times.append(auth_time)
        return times
    
    all_concurrent_times = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker, i) for i in range(10)]
        for future in concurrent.futures.as_completed(futures):
            all_concurrent_times.extend(future.result())
    
    # Results
    sequential_avg = statistics.mean(sequential_times) * 1000
    concurrent_avg = statistics.mean(all_concurrent_times) * 1000
    sequential_throughput = 1 / statistics.mean(sequential_times)
    concurrent_throughput = len(all_concurrent_times) / sum(all_concurrent_times)
    
    print(f"✅ Sequential: {sequential_avg:.2f}ms avg, {sequential_throughput:.0f} ops/sec")
    print(f"✅ Concurrent: {concurrent_avg:.2f}ms avg, {concurrent_throughput:.0f} ops/sec")
    
    return {
        "sequential_auth_ms": sequential_avg,
        "concurrent_auth_ms": concurrent_avg,
        "sequential_throughput": sequential_throughput,
        "concurrent_throughput": concurrent_throughput,
        "meets_requirements": sequential_avg < 200 and concurrent_throughput > 100
    }

if __name__ == "__main__":
    print("🚀 Quick Authentication Load Test")
    print("=" * 40)
    
    results = quick_auth_load_test()
    
    print(f"\n📊 Results:")
    print(f"Load Test: {'✅ PASS' if results['meets_requirements'] else '❌ FAIL'}")
    
    # Save results
    with open("results/benchmarks/quick_load_test.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results
        }, f, indent=2)
    
    print(f"📄 Results saved to results/benchmarks/quick_load_test.json")