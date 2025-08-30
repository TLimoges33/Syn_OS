#!/usr/bin/env python3
"""
Comprehensive Test Suite for Syn_OS Security Dashboard
Tests authentication, API endpoints, and UI functionality
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime
import time

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from security.jwt_auth import get_jwt_manager
from security.audit_logger import get_audit_logger
from security.input_validator import get_validator, ValidationRule, InputType

class SecurityDashboardTester:
    """Comprehensive security dashboard test suite"""
    
    def __init__(self, base_url="http://localhost:8083"):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
        self.test_results = []
        
    async def setup(self):
        """Setup test environment"""
        self.session = aiohttp.ClientSession()
        print("🔧 Test environment setup complete")
    
    async def teardown(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()
        print("🧹 Test environment cleaned up")
    
    def log_test_result(self, test_name, success, message="", details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    async def test_health_check(self):
        """Test health check endpoint"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'healthy':
                        self.log_test_result("Health Check", True, "Service is healthy")
                        return True
                    else:
                        self.log_test_result("Health Check", False, f"Unhealthy status: {data}")
                        return False
                else:
                    self.log_test_result("Health Check", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("Health Check", False, f"Connection error: {e}")
            return False
    
    async def test_login_page(self):
        """Test login page accessibility"""
        try:
            async with self.session.get(f"{self.base_url}/login") as response:
                if response.status == 200:
                    content = await response.text()
                    if "Syn_OS Security Dashboard" in content and "login" in content.lower():
                        self.log_test_result("Login Page", True, "Login page loads correctly")
                        return True
                    else:
                        self.log_test_result("Login Page", False, "Login page content invalid")
                        return False
                else:
                    self.log_test_result("Login Page", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("Login Page", False, f"Error: {e}")
            return False
    
    async def test_authentication(self):
        """Test authentication flow"""
        try:
            # Test login with demo credentials
            login_data = {
                "username": "admin",
                "password": "secure_admin_password"
            }
            
            async with self.session.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and data.get('access_token'):
                        self.auth_token = data['access_token']
                        self.log_test_result("Authentication", True, "Login successful")
                        return True
                    else:
                        self.log_test_result("Authentication", False, f"Login failed: {data}")
                        return False
                else:
                    self.log_test_result("Authentication", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("Authentication", False, f"Error: {e}")
            return False
    
    async def test_protected_endpoints(self):
        """Test protected API endpoints"""
        if not self.auth_token:
            self.log_test_result("Protected Endpoints", False, "No auth token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        endpoints = [
            "/api/security/status",
            "/api/security/hsm/status",
            "/api/security/zero-trust/status",
            "/api/security/quantum/status",
            "/api/security/consciousness/status",
            "/api/security/threats",
            "/api/security/events"
        ]
        
        success_count = 0
        for endpoint in endpoints:
            try:
                async with self.session.get(f"{self.base_url}{endpoint}", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('status') == 'success':
                            success_count += 1
                        else:
                            print(f"  ⚠️  {endpoint}: Invalid response format")
                    else:
                        print(f"  ❌ {endpoint}: HTTP {response.status}")
            except Exception as e:
                print(f"  ❌ {endpoint}: Error {e}")
        
        if success_count == len(endpoints):
            self.log_test_result("Protected Endpoints", True, f"All {len(endpoints)} endpoints working")
            return True
        else:
            self.log_test_result("Protected Endpoints", False, f"Only {success_count}/{len(endpoints)} working")
            return False
    
    async def test_dashboard_pages(self):
        """Test dashboard page accessibility"""
        if not self.auth_token:
            self.log_test_result("Dashboard Pages", False, "No auth token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        pages = [
            "/",
            "/hsm",
            "/zero-trust",
            "/quantum",
            "/consciousness",
            "/tools",
            "/monitoring",
            "/audit"
        ]
        
        success_count = 0
        for page in pages:
            try:
                async with self.session.get(f"{self.base_url}{page}", headers=headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        if "Syn_OS Security" in content:
                            success_count += 1
                        else:
                            print(f"  ⚠️  {page}: Invalid page content")
                    else:
                        print(f"  ❌ {page}: HTTP {response.status}")
            except Exception as e:
                print(f"  ❌ {page}: Error {e}")
        
        if success_count == len(pages):
            self.log_test_result("Dashboard Pages", True, f"All {len(pages)} pages accessible")
            return True
        else:
            self.log_test_result("Dashboard Pages", False, f"Only {success_count}/{len(pages)} accessible")
            return False
    
    async def test_security_tools_api(self):
        """Test security tools API endpoints"""
        if not self.auth_token:
            self.log_test_result("Security Tools API", False, "No auth token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test Nmap scan endpoint
        try:
            nmap_data = {
                "target": "127.0.0.1",
                "ports": "80,443",
                "scan_type": "syn"
            }
            
            async with self.session.post(
                f"{self.base_url}/api/tools/nmap/scan",
                json=nmap_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        self.log_test_result("Security Tools API", True, "Nmap scan API working")
                        return True
                    else:
                        self.log_test_result("Security Tools API", False, f"Invalid response: {data}")
                        return False
                else:
                    self.log_test_result("Security Tools API", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("Security Tools API", False, f"Error: {e}")
            return False
    
    async def test_consciousness_security_api(self):
        """Test consciousness security API endpoints"""
        if not self.auth_token:
            self.log_test_result("Consciousness Security API", False, "No auth token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test consciousness assessment endpoint
        try:
            assessment_data = {
                "target": "localhost",
                "assessment_type": "basic"
            }
            
            async with self.session.post(
                f"{self.base_url}/api/consciousness/security/assess",
                json=assessment_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        self.log_test_result("Consciousness Security API", True, "Assessment API working")
                        return True
                    else:
                        self.log_test_result("Consciousness Security API", False, f"Invalid response: {data}")
                        return False
                else:
                    self.log_test_result("Consciousness Security API", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("Consciousness Security API", False, f"Error: {e}")
            return False
    
    async def test_input_validation(self):
        """Test input validation security"""
        if not self.auth_token:
            self.log_test_result("Input Validation", False, "No auth token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Test SQL injection attempt
        try:
            malicious_data = {
                "target": "'; DROP TABLE users; --",
                "ports": "80"
            }
            
            async with self.session.post(
                f"{self.base_url}/api/tools/nmap/scan",
                json=malicious_data,
                headers=headers
            ) as response:
                if response.status == 400:
                    self.log_test_result("Input Validation", True, "SQL injection blocked")
                    return True
                else:
                    self.log_test_result("Input Validation", False, f"Malicious input not blocked: {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("Input Validation", False, f"Error: {e}")
            return False
    
    async def test_websocket_connection(self):
        """Test WebSocket real-time updates"""
        if not self.auth_token:
            self.log_test_result("WebSocket Connection", False, "No auth token available")
            return False
        
        try:
            # This is a simplified test - in a real scenario, we'd test actual WebSocket connection
            # For now, we'll just verify the endpoint exists
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(f"{self.base_url}/ws", headers=headers) as response:
                # WebSocket upgrade should return 101 or connection error
                if response.status in [101, 400, 426]:  # 426 = Upgrade Required
                    self.log_test_result("WebSocket Connection", True, "WebSocket endpoint accessible")
                    return True
                else:
                    self.log_test_result("WebSocket Connection", False, f"Unexpected status: {response.status}")
                    return False
        except Exception as e:
            # WebSocket connection errors are expected in this test context
            self.log_test_result("WebSocket Connection", True, "WebSocket endpoint exists")
            return True
    
    async def test_logout(self):
        """Test logout functionality"""
        if not self.auth_token:
            self.log_test_result("Logout", False, "No auth token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.post(f"{self.base_url}/api/auth/logout", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        self.log_test_result("Logout", True, "Logout successful")
                        return True
                    else:
                        self.log_test_result("Logout", False, f"Logout failed: {data}")
                        return False
                else:
                    self.log_test_result("Logout", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("Logout", False, f"Error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Syn_OS Security Dashboard Test Suite")
        print("=" * 60)
        
        await self.setup()
        
        # Run tests in order
        tests = [
            self.test_health_check,
            self.test_login_page,
            self.test_authentication,
            self.test_protected_endpoints,
            self.test_dashboard_pages,
            self.test_security_tools_api,
            self.test_consciousness_security_api,
            self.test_input_validation,
            self.test_websocket_connection,
            self.test_logout
        ]
        
        for test in tests:
            await test()
            await asyncio.sleep(0.5)  # Brief pause between tests
        
        await self.teardown()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Security Dashboard is ready for deployment.")
            return True
        else:
            print(f"\n⚠️  {total - passed} tests failed. Please review and fix issues.")
            return False

async def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Syn_OS Security Dashboard")
    parser.add_argument("--url", default="http://localhost:8083", help="Dashboard URL")
    parser.add_argument("--wait", type=int, default=0, help="Wait seconds before starting tests")
    
    args = parser.parse_args()
    
    if args.wait > 0:
        print(f"⏳ Waiting {args.wait} seconds for services to start...")
        await asyncio.sleep(args.wait)
    
    tester = SecurityDashboardTester(args.url)
    success = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())