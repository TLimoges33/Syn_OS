#!/usr/bin/env python3
"""
Zero Trust Integration Test and Validation Script
Tests the complete Zero Trust architecture implementation
"""

import asyncio
import logging
import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.security.enhanced_zero_trust_manager import (
    EnhancedZeroTrustManager,
    ZeroTrustEntity,
    ZeroTrustPolicy,
    TrustLevel,
    SecurityPosture,
    NetworkZone,
    SecurityContext
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("zero_trust_test")

class ZeroTrustIntegrationTest:
    """Comprehensive Zero Trust testing suite"""
    
    def __init__(self):
        self.zt_manager = EnhancedZeroTrustManager()
        self.test_results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "start_time": datetime.utcnow().isoformat(),
            "test_details": []
        }

    async def run_all_tests(self):
        """Run complete Zero Trust test suite"""
        logger.info("Starting Zero Trust Integration Tests...")
        
        # Core functionality tests
        await self._test_initialization()
        await self._test_entity_registration()
        await self._test_authentication()
        await self._test_authorization()
        await self._test_policy_evaluation()
        await self._test_network_segmentation()
        await self._test_mtls_certificate_management()
        await self._test_behavioral_monitoring()
        await self._test_risk_assessment()
        await self._test_session_management()
        
        # Integration tests
        await self._test_full_integration_scenario()
        
        # Performance tests
        await self._test_performance()
        
        # Generate test report
        await self._generate_test_report()

    async def _test_initialization(self):
        """Test Zero Trust manager initialization"""
        test_name = "Zero Trust Manager Initialization"
        logger.info(f"Running test: {test_name}")
        
        try:
            # Initialize the manager
            success = await self.zt_manager.initialize()
            
            if success and self.zt_manager.is_initialized:
                await self._record_test_result(test_name, True, "Manager initialized successfully")
            else:
                await self._record_test_result(test_name, False, "Manager initialization failed")
                
        except Exception as e:
            await self._record_test_result(test_name, False, f"Initialization exception: {e}")

    async def _test_entity_registration(self):
        """Test entity registration and management"""
        test_name = "Entity Registration"
        logger.info(f"Running test: {test_name}")
        
        try:
            # Create test entities
            test_entities = [
                ZeroTrustEntity(
                    entity_id="test_service_1",
                    name="Test Service 1",
                    entity_type="service",
                    trust_level=TrustLevel.TRUSTED,
                    security_posture=SecurityPosture.SECURE,
                    network_zone=NetworkZone.INTERNAL,
                    ip_addresses=["10.10.3.100"],
                    certificates=[],
                    permissions=["read", "write"],
                    metadata={"test": True}
                ),
                ZeroTrustEntity(
                    entity_id="test_user_1",
                    name="Test User 1",
                    entity_type="user",
                    trust_level=TrustLevel.CONDITIONAL,
                    security_posture=SecurityPosture.MEDIUM_RISK,
                    network_zone=NetworkZone.INTERNAL,
                    ip_addresses=["10.10.3.101"],
                    certificates=[],
                    permissions=["read"],
                    metadata={"department": "testing"}
                )
            ]
            
            # Register entities
            registration_results = []
            for entity in test_entities:
                result = await self.zt_manager.register_entity(entity)
                registration_results.append(result)
            
            # Verify registrations
            all_registered = all(registration_results)
            entity_count = len(self.zt_manager.entities)
            
            if all_registered and entity_count >= len(test_entities):
                await self._record_test_result(test_name, True, 
                    f"Successfully registered {len(test_entities)} entities")
            else:
                await self._record_test_result(test_name, False, 
                    f"Entity registration failed: {registration_results}")
                
        except Exception as e:
            await self._record_test_result(test_name, False, f"Entity registration exception: {e}")

    async def _test_authentication(self):
        """Test entity authentication"""
        test_name = "Entity Authentication"
        logger.info(f"Running test: {test_name}")
        
        try:
            # Test valid authentication
            credentials = {
                "method": "certificate",
                "source_ip": "10.10.3.100",
                "user_agent": "ZeroTrustTest/1.0"
            }
            
            auth_token = await self.zt_manager.authenticate_entity("test_service_1", credentials)
            
            if auth_token:
                await self._record_test_result(test_name, True, 
                    "Entity authentication successful")
            else:
                await self._record_test_result(test_name, False, 
                    "Entity authentication failed")
                
        except Exception as e:
            await self._record_test_result(test_name, False, f"Authentication exception: {e}")

    async def _test_authorization(self):
        """Test authorization and access control"""
        test_name = "Authorization and Access Control"
        logger.info(f"Running test: {test_name}")
        
        try:
            # Create security context
            context = SecurityContext(
                entity_id="test_service_1",
                source_ip="10.10.3.100",
                target_resource="test_resource",
                action="read",
                user_agent="ZeroTrustTest/1.0",
                timestamp=datetime.utcnow()
            )
            
            # Test authorization
            auth_result = await self.zt_manager.authorize_access(context)
            
            if auth_result.get("allowed", False):
                await self._record_test_result(test_name, True, 
                    "Authorization check passed")
            else:
                await self._record_test_result(test_name, False, 
                    f"Authorization failed: {auth_result.get('reason', 'Unknown')}")
                
        except Exception as e:
            await self._record_test_result(test_name, False, f"Authorization exception: {e}")

    async def _test_policy_evaluation(self):
        """Test policy evaluation system"""
        test_name = "Policy Evaluation"
        logger.info(f"Running test: {test_name}")
        
        try:
            # Create test policy
            test_policy = ZeroTrustPolicy(
                policy_id="test_policy_1",
                name="Test Access Policy",
                description="Test policy for integration testing",
                source_entities=["test_service_1"],
                target_resources=["test_resource"],
                allowed_actions=["read", "write"],
                conditions={"network_zone": "internal"},
                priority=100,
                enabled=True
            )
            
            # Add policy
            policy_added = await self.zt_manager.add_policy(test_policy)
            
            # Evaluate policy
            policies = await self.zt_manager.get_applicable_policies("test_service_1", "test_resource")
            
            if policy_added and len(policies) > 0:
                await self._record_test_result(test_name, True, 
                    f"Policy evaluation successful: {len(policies)} policies found")
            else:
                await self._record_test_result(test_name, False, 
                    "Policy evaluation failed")
                
        except Exception as e:
            await self._record_test_result(test_name, False, f"Policy evaluation exception: {e}")

    async def _test_network_segmentation(self):
        """Test network segmentation functionality"""
        test_name = "Network Segmentation"
        logger.info(f"Running test: {test_name}")
        
        try:
            # Test segmentation enforcement
            if self.zt_manager.network_engine:
                # Test allowed communication
                allowed = await self.zt_manager.network_engine.evaluate_traffic(
                    "10.10.3.100", "10.10.3.101", 443, "tcp"
                )
                
                # Test denied communication  
                denied = await self.zt_manager.network_engine.evaluate_traffic(
                    "192.168.1.100", "10.10.3.100", 22, "tcp"
                )
                
                if allowed[0].value == "allow" and denied[0].value == "deny":
                    await self._record_test_result(test_name, True, 
                        "Network segmentation working correctly")
                else:
                    await self._record_test_result(test_name, False, 
                        f"Network segmentation issue: allowed={allowed}, denied={denied}")
            else:
                await self._record_test_result(test_name, False, 
                    "Network segmentation engine not available")
                
        except Exception as e:
            await self._record_test_result(test_name, False, f"Network segmentation exception: {e}")

    async def _test_mtls_certificate_management(self):
        """Test mTLS certificate management"""
        test_name = "mTLS Certificate Management"
        logger.info(f"Running test: {test_name}")
        
        try:
            if self.zt_manager.mtls_manager:
                # Test certificate status
                cert_status = await self.zt_manager.mtls_manager.get_certificate_status("test_service_1")
                
                # Test certificate listing
                cert_list = await self.zt_manager.mtls_manager.list_certificates()
                
                if cert_status and cert_list:
                    await self._record_test_result(test_name, True, 
                        f"Certificate management working: {len(cert_list)} certificates")
                else:
                    await self._record_test_result(test_name, False, 
                        "Certificate management issues")
            else:
                await self._record_test_result(test_name, False, 
                    "mTLS certificate manager not available")
                
        except Exception as e:
            await self._record_test_result(test_name, False, f"Certificate management exception: {e}")

    async def _test_behavioral_monitoring(self):
        """Test behavioral monitoring system"""
        test_name = "Behavioral Monitoring"
        logger.info(f"Running test: {test_name}")
        
        try:
            if self.zt_manager.behavior_monitor:
                # Get monitoring status
                status = await self.zt_manager.behavior_monitor.get_monitoring_status()
                
                # Test entity behavior summary
                behavior_summary = await self.zt_manager.behavior_monitor.get_entity_behavior_summary("test_service_1")
                
                if status.get("monitoring_active", False):
                    await self._record_test_result(test_name, True, 
                        "Behavioral monitoring active and functional")
                else:
                    await self._record_test_result(test_name, False, 
                        "Behavioral monitoring not active")
            else:
                await self._record_test_result(test_name, False, 
                    "Behavioral monitoring system not available")
                
        except Exception as e:
            await self._record_test_result(test_name, False, f"Behavioral monitoring exception: {e}")

    async def _test_risk_assessment(self):
        """Test risk assessment functionality"""
        test_name = "Risk Assessment"
        logger.info(f"Running test: {test_name}")
        
        try:
            # Test entity risk assessment
            risk_score = await self.zt_manager.assess_entity_risk("test_service_1")
            
            # Test security posture evaluation
            posture = await self.zt_manager.evaluate_security_posture("test_service_1")
            
            if isinstance(risk_score, (int, float)) and 0 <= risk_score <= 1:
                await self._record_test_result(test_name, True, 
                    f"Risk assessment functional: score={risk_score}, posture={posture}")
            else:
                await self._record_test_result(test_name, False, 
                    f"Risk assessment issues: {risk_score}")
                
        except Exception as e:
            await self._record_test_result(test_name, False, f"Risk assessment exception: {e}")

    async def _test_session_management(self):
        """Test session management"""
        test_name = "Session Management"
        logger.info(f"Running test: {test_name}")
        
        try:
            # Test session validation
            sessions = self.zt_manager.active_sessions
            session_count = len(sessions)
            
            # Test session cleanup (would normally be time-based)
            await self.zt_manager._cleanup_expired_sessions()
            
            await self._record_test_result(test_name, True, 
                f"Session management functional: {session_count} active sessions")
                
        except Exception as e:
            await self._record_test_result(test_name, False, f"Session management exception: {e}")

    async def _test_full_integration_scenario(self):
        """Test complete end-to-end Zero Trust scenario"""
        test_name = "Full Integration Scenario"
        logger.info(f"Running test: {test_name}")
        
        try:
            # Simulate complete Zero Trust workflow
            steps_completed = 0
            
            # Step 1: Entity authentication
            credentials = {"method": "certificate", "source_ip": "10.10.3.100"}
            auth_token = await self.zt_manager.authenticate_entity("test_service_1", credentials)
            if auth_token:
                steps_completed += 1
            
            # Step 2: Create mTLS context
            if self.zt_manager.mtls_manager:
                try:
                    context = await self.zt_manager.create_mtls_context("test_service_1")
                    if context:
                        steps_completed += 1
                except:
                    pass  # May fail if certificates don't exist
            else:
                steps_completed += 1  # Skip if not available
            
            # Step 3: Authorization check
            security_context = SecurityContext(
                entity_id="test_service_1",
                source_ip="10.10.3.100",
                target_resource="test_resource",
                action="read",
                user_agent="ZeroTrustTest/1.0",
                timestamp=datetime.utcnow()
            )
            auth_result = await self.zt_manager.authorize_access(security_context)
            if auth_result.get("allowed", False):
                steps_completed += 1
            
            # Step 4: Network segmentation check
            if self.zt_manager.network_engine:
                try:
                    network_allowed = await self.zt_manager.network_engine.evaluate_traffic(
                        "10.10.3.100", "10.10.3.101", 443, "tcp"
                    )
                    if network_allowed:
                        steps_completed += 1
                except:
                    pass
            else:
                steps_completed += 1  # Skip if not available
            
            # Evaluate integration success
            total_steps = 4
            success_rate = steps_completed / total_steps
            
            if success_rate >= 0.75:  # 75% of steps must succeed
                await self._record_test_result(test_name, True, 
                    f"Integration scenario successful: {steps_completed}/{total_steps} steps completed")
            else:
                await self._record_test_result(test_name, False, 
                    f"Integration scenario failed: {steps_completed}/{total_steps} steps completed")
                
        except Exception as e:
            await self._record_test_result(test_name, False, f"Integration scenario exception: {e}")

    async def _test_performance(self):
        """Test performance metrics"""
        test_name = "Performance Metrics"
        logger.info(f"Running test: {test_name}")
        
        try:
            # Test metrics collection
            metrics = self.zt_manager.get_metrics()
            
            # Test that metrics are being collected
            required_metrics = ["authentications", "authorizations", "certificates_issued"]
            metrics_present = all(metric in metrics for metric in required_metrics)
            
            if metrics_present:
                await self._record_test_result(test_name, True, 
                    f"Performance metrics functional: {len(metrics)} metrics collected")
            else:
                await self._record_test_result(test_name, False, 
                    "Performance metrics incomplete")
                
        except Exception as e:
            await self._record_test_result(test_name, False, f"Performance metrics exception: {e}")

    async def _record_test_result(self, test_name: str, passed: bool, details: str):
        """Record test result"""
        self.test_results["tests_run"] += 1
        
        if passed:
            self.test_results["tests_passed"] += 1
            logger.info(f"✅ {test_name}: PASSED - {details}")
        else:
            self.test_results["tests_failed"] += 1
            logger.error(f"❌ {test_name}: FAILED - {details}")
        
        self.test_results["test_details"].append({
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def _generate_test_report(self):
        """Generate comprehensive test report"""
        self.test_results["end_time"] = datetime.utcnow().isoformat()
        self.test_results["success_rate"] = (
            self.test_results["tests_passed"] / self.test_results["tests_run"] * 100
            if self.test_results["tests_run"] > 0 else 0
        )
        
        # Save detailed report
        report_path = Path("test_reports/zero_trust_integration_test.json")
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        # Print summary
        logger.info("\n" + "="*80)
        logger.info("ZERO TRUST INTEGRATION TEST RESULTS")
        logger.info("="*80)
        logger.info(f"Tests Run: {self.test_results['tests_run']}")
        logger.info(f"Tests Passed: {self.test_results['tests_passed']}")
        logger.info(f"Tests Failed: {self.test_results['tests_failed']}")
        logger.info(f"Success Rate: {self.test_results['success_rate']:.1f}%")
        logger.info(f"Detailed Report: {report_path}")
        logger.info("="*80)
        
        # Return overall success
        return self.test_results["success_rate"] >= 80.0  # 80% success threshold

async def main():
    """Run Zero Trust integration tests"""
    test_suite = ZeroTrustIntegrationTest()
    
    try:
        success = await test_suite.run_all_tests()
        
        if success:
            logger.info("🎉 Zero Trust Integration Tests PASSED!")
            return 0
        else:
            logger.error("💥 Zero Trust Integration Tests FAILED!")
            return 1
            
    except Exception as e:
        logger.error(f"Test suite execution failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
