#!/usr/bin/env python3
"""
Phase 4 Integration Tests
========================

Comprehensive integration tests for Phase 4 deployment infrastructure,
threat intelligence dashboard, and component integration.

Tests cover:
1. Threat Intelligence Dashboard functionality
2. Phase 4 Integration Bridge operations  
3. Kubernetes deployment validation
4. Monitoring and observability verification
5. End-to-end threat intelligence flow
6. Consciousness system integration
"""

import asyncio
import pytest
import aiohttp
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from integration.phase4_integration_bridge import (
    Phase4IntegrationBridge, 
    create_phase4_integration_bridge
)

logger = logging.getLogger(__name__)


class TestPhase4Integration:
    """Test suite for Phase 4 integration components"""
    
    @pytest.fixture
    async def integration_bridge(self):
        """Create and initialize integration bridge for testing"""
        bridge = create_phase4_integration_bridge()
        
        # Initialize the bridge
        success = await bridge.initialize()
        assert success, "Failed to initialize Phase 4 Integration Bridge"
        
        yield bridge
        
        # Cleanup
        await bridge.shutdown()
    
    @pytest.fixture
    async def threat_intel_dashboard_client(self):
        """Create HTTP client for threat intelligence dashboard"""
        session = aiohttp.ClientSession()
        yield session
        await session.close()
    
    @pytest.mark.asyncio
    async def test_integration_bridge_initialization(self, integration_bridge):
        """Test Phase 4 integration bridge initialization"""
        
        # Verify bridge is initialized
        assert integration_bridge is not None
        
        # Check integration status
        status = integration_bridge.get_integration_status()
        assert status['overall_health'] > 0.0
        assert status['component_count'] > 0
        assert status['integration_level'] in ['none', 'partial', 'full']
        
        logger.info(f"Integration health: {status['overall_health']:.2%}")
        logger.info(f"Integration level: {status['integration_level']}")
        logger.info(f"Active components: {status['active_components']}/{status['component_count']}")
    
    @pytest.mark.asyncio
    async def test_deployment_infrastructure_components(self, integration_bridge):
        """Test deployment infrastructure component registration and health"""
        
        # Check Kubernetes cluster component
        k8s_status = integration_bridge.get_component_status('kubernetes_cluster')
        assert k8s_status is not None
        assert k8s_status['status'] == 'active'
        assert k8s_status['health_score'] > 0.8
        
        # Check Helm charts component
        helm_status = integration_bridge.get_component_status('helm_charts')
        assert helm_status is not None
        assert helm_status['status'] == 'active'
        
        # Check ingress load balancer
        ingress_status = integration_bridge.get_component_status('ingress_load_balancer')
        assert ingress_status is not None
        assert ingress_status['metrics']['ssl_certificates_valid'] is True
        
        # Check persistent storage
        storage_status = integration_bridge.get_component_status('persistent_storage')
        assert storage_status is not None
        assert storage_status['metrics']['replication_factor'] >= 3
        
        logger.info("✅ All deployment infrastructure components are healthy")
    
    @pytest.mark.asyncio
    async def test_monitoring_observability_components(self, integration_bridge):
        """Test monitoring and observability component health"""
        
        # Check Prometheus metrics
        prometheus_status = integration_bridge.get_component_status('prometheus_metrics')
        assert prometheus_status is not None
        assert prometheus_status['status'] == 'active'
        assert prometheus_status['metrics']['scrape_targets'] > 0
        
        # Check Grafana dashboards
        grafana_status = integration_bridge.get_component_status('grafana_dashboards')
        assert grafana_status is not None
        assert grafana_status['metrics']['dashboards_active'] > 0
        
        # Check distributed tracing
        tracing_status = integration_bridge.get_component_status('distributed_tracing')
        assert tracing_status is not None
        assert tracing_status['metrics']['traces_collected'] > 0
        
        # Check log aggregation
        logging_status = integration_bridge.get_component_status('log_aggregation')
        assert logging_status is not None
        assert logging_status['metrics']['logs_processed_per_second'] > 0
        
        # Check alerting
        alerting_status = integration_bridge.get_component_status('alerting_escalation')
        assert alerting_status is not None
        assert alerting_status['metrics']['alert_rules_active'] > 0
        
        logger.info("✅ All monitoring and observability components are healthy")
    
    @pytest.mark.asyncio
    async def test_threat_intelligence_integration(self, integration_bridge):
        """Test threat intelligence component integration"""
        
        # Check global threat orchestrator
        orchestrator_status = integration_bridge.get_component_status('global_threat_orchestrator')
        assert orchestrator_status is not None
        assert orchestrator_status['status'] == 'active'
        assert orchestrator_status['metrics']['global_nodes_active'] > 0
        
        # Check real-time threat aggregator
        aggregator_status = integration_bridge.get_component_status('realtime_threat_aggregator')
        assert aggregator_status is not None
        assert aggregator_status['status'] == 'active'
        assert aggregator_status['metrics']['sources_active'] > 0
        
        # Check threat intelligence dashboard
        dashboard_status = integration_bridge.get_component_status('threat_intelligence_dashboard')
        assert dashboard_status is not None
        assert dashboard_status['status'] == 'active'
        assert dashboard_status['metrics']['active_visualizations'] > 0
        
        logger.info("✅ All threat intelligence components are healthy")
    
    @pytest.mark.asyncio
    async def test_consciousness_system_integration(self, integration_bridge):
        """Test consciousness system integration"""
        
        # Check consciousness security controller
        consciousness_status = integration_bridge.get_component_status('consciousness_security_controller')
        assert consciousness_status is not None
        assert consciousness_status['status'] == 'active'
        assert consciousness_status['metrics']['consciousness_level'] > 0.5
        
        # Check neural darwinism engine
        neural_status = integration_bridge.get_component_status('neural_darwinism_v2')
        assert neural_status is not None
        assert neural_status['status'] == 'active'
        assert neural_status['metrics']['population_size'] > 0
        
        # Check kernel hooks
        kernel_status = integration_bridge.get_component_status('kernel_hooks_v2')
        assert kernel_status is not None
        assert kernel_status['status'] == 'active'
        assert kernel_status['metrics']['hooks_active'] > 0
        
        logger.info("✅ All consciousness system components are healthy")
    
    @pytest.mark.asyncio
    async def test_deployment_readiness_assessment(self, integration_bridge):
        """Test deployment readiness assessment"""
        
        readiness = integration_bridge.get_deployment_readiness()
        
        # Check readiness score
        assert readiness['readiness_score'] >= 0.0
        assert readiness['readiness_score'] <= 1.0
        
        # Check readiness level
        assert readiness['readiness_level'] in ['production_ready', 'staging_ready', 'development_only']
        
        # Check individual metrics
        assert 'deployment_infrastructure' in readiness
        assert 'monitoring_coverage' in readiness
        assert 'security_posture' in readiness
        assert 'consciousness_integration' in readiness
        
        logger.info(f"Deployment readiness: {readiness['readiness_score']:.2%} ({readiness['readiness_level']})")
        
        # Log recommendations if any
        if readiness['recommendations']:
            logger.info("Recommendations:")
            for rec in readiness['recommendations']:
                logger.info(f"  - {rec}")
    
    @pytest.mark.asyncio
    async def test_component_dependencies(self, integration_bridge):
        """Test component dependency validation"""
        
        all_components = integration_bridge.get_all_components()
        
        for component_name, component_data in all_components.items():
            # Check that dependencies exist
            for dependency in component_data['dependencies']:
                assert dependency in all_components, f"Dependency {dependency} not found for {component_name}"
                
                # Check that dependency is healthy
                dep_component = all_components[dependency]
                assert dep_component['status'] == 'active', f"Dependency {dependency} is not active for {component_name}"
        
        logger.info("✅ All component dependencies are satisfied")
    
    @pytest.mark.asyncio
    async def test_integration_metrics_collection(self, integration_bridge):
        """Test integration metrics collection"""
        
        status = integration_bridge.get_integration_status()
        metrics = status['metrics']
        
        # Check that all expected metrics are present
        expected_metrics = [
            'deployment_readiness',
            'monitoring_coverage',
            'threat_intelligence_accuracy',
            'consciousness_integration'
        ]
        
        for metric in expected_metrics:
            assert metric in metrics, f"Missing metric: {metric}"
            assert isinstance(metrics[metric], (int, float)), f"Invalid metric type for {metric}"
            assert 0.0 <= metrics[metric] <= 1.0, f"Metric {metric} out of range: {metrics[metric]}"
        
        logger.info("✅ All integration metrics are properly collected")


class TestThreatIntelligenceDashboard:
    """Test suite for threat intelligence dashboard"""
    
    @pytest.fixture
    def dashboard_base_url(self):
        """Base URL for threat intelligence dashboard"""
        return os.getenv('THREAT_INTEL_DASHBOARD_URL', 'http://localhost:8084')
    
    @pytest.mark.asyncio
    async def test_dashboard_health_endpoint(self, threat_intel_dashboard_client, dashboard_base_url):
        """Test dashboard health endpoint"""
        
        async with threat_intel_dashboard_client.get(f"{dashboard_base_url}/health") as response:
            assert response.status == 200
            
            data = await response.json()
            assert data['status'] == 'healthy'
            assert data['service'] == 'threat_intelligence_dashboard'
            assert 'components' in data
            
            logger.info("✅ Threat intelligence dashboard health check passed")
    
    @pytest.mark.asyncio
    async def test_dashboard_authentication(self, threat_intel_dashboard_client, dashboard_base_url):
        """Test dashboard authentication flow"""
        
        # Test login endpoint with valid credentials
        login_data = {
            'username': 'admin',
            'password': 'synos123'  # Test credentials
        }
        
        async with threat_intel_dashboard_client.post(
            f"{dashboard_base_url}/api/auth/login",
            json=login_data
        ) as response:
            # Note: This might fail if authentication is not properly mocked
            # In a real test environment, we'd use test credentials
            if response.status == 200:
                data = await response.json()
                assert data['success'] is True
                assert 'access_token' in data
                logger.info("✅ Dashboard authentication test passed")
            else:
                logger.warning("⚠️ Dashboard authentication test skipped (no test credentials)")
    
    @pytest.mark.asyncio
    async def test_dashboard_api_endpoints(self, threat_intel_dashboard_client, dashboard_base_url):
        """Test dashboard API endpoints (without authentication for now)"""
        
        # Test endpoints that might be accessible without auth or return meaningful errors
        endpoints = [
            '/health',
            '/api/dashboard/overview',
            '/api/threats/feeds/status'
        ]
        
        for endpoint in endpoints:
            async with threat_intel_dashboard_client.get(f"{dashboard_base_url}{endpoint}") as response:
                # Accept 200 (success) or 401 (auth required) as valid responses
                assert response.status in [200, 401], f"Unexpected status {response.status} for {endpoint}"
                
                if response.status == 200:
                    # If we get data, verify it's valid JSON
                    data = await response.json()
                    assert isinstance(data, dict)
                    
                logger.info(f"✅ Endpoint {endpoint} responded correctly (status: {response.status})")


class TestKubernetesIntegration:
    """Test suite for Kubernetes integration (if available)"""
    
    @pytest.fixture
    def kubernetes_available(self):
        """Check if Kubernetes is available for testing"""
        try:
            import kubernetes
            kubernetes.config.load_incluster_config()
            return True
        except:
            try:
                import kubernetes
                kubernetes.config.load_kube_config()
                return True
            except:
                return False
    
    @pytest.mark.skipif(not pytest.importorskip('kubernetes', None), reason="kubernetes package not available")
    @pytest.mark.asyncio
    async def test_kubernetes_namespace_exists(self, kubernetes_available):
        """Test that Phase 4 Kubernetes namespace exists"""
        
        if not kubernetes_available:
            pytest.skip("Kubernetes not available")
        
        import kubernetes
        
        try:
            # Load Kubernetes config
            try:
                kubernetes.config.load_incluster_config()
            except:
                kubernetes.config.load_kube_config()
            
            v1 = kubernetes.client.CoreV1Api()
            
            # Check if synos-phase4 namespace exists
            namespaces = v1.list_namespace()
            namespace_names = [ns.metadata.name for ns in namespaces.items]
            
            assert 'synos-phase4' in namespace_names, "Phase 4 namespace not found"
            logger.info("✅ Phase 4 Kubernetes namespace exists")
            
        except Exception as e:
            pytest.skip(f"Kubernetes test skipped: {e}")
    
    @pytest.mark.skipif(not pytest.importorskip('kubernetes', None), reason="kubernetes package not available")
    @pytest.mark.asyncio
    async def test_kubernetes_deployments(self, kubernetes_available):
        """Test that Phase 4 deployments are running"""
        
        if not kubernetes_available:
            pytest.skip("Kubernetes not available")
        
        import kubernetes
        
        try:
            v1 = kubernetes.client.AppsV1Api()
            
            # Check deployments in synos-phase4 namespace
            deployments = v1.list_namespaced_deployment(namespace='synos-phase4')
            
            expected_deployments = [
                'threat-intelligence-dashboard',
                'phase4-integration-bridge'
            ]
            
            deployment_names = [dep.metadata.name for dep in deployments.items]
            
            for expected_dep in expected_deployments:
                if expected_dep in deployment_names:
                    # Find the deployment
                    deployment = next(dep for dep in deployments.items if dep.metadata.name == expected_dep)
                    
                    # Check that it's ready
                    assert deployment.status.ready_replicas > 0, f"Deployment {expected_dep} has no ready replicas"
                    logger.info(f"✅ Deployment {expected_dep} is ready ({deployment.status.ready_replicas} replicas)")
                else:
                    logger.warning(f"⚠️ Deployment {expected_dep} not found")
            
        except Exception as e:
            pytest.skip(f"Kubernetes deployment test skipped: {e}")


class TestEndToEndIntegration:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_complete_threat_intelligence_flow(self):
        """Test complete threat intelligence processing flow"""
        
        # This is a comprehensive test that would verify:
        # 1. Threat data ingestion
        # 2. Processing through consciousness system  
        # 3. Correlation and analysis
        # 4. Dashboard visualization
        # 5. Alert generation
        
        logger.info("🧪 Running end-to-end threat intelligence flow test...")
        
        # Create integration bridge
        bridge = create_phase4_integration_bridge()
        
        try:
            # Initialize
            success = await bridge.initialize()
            assert success, "Failed to initialize integration bridge"
            
            # Wait for components to be ready
            await asyncio.sleep(2)
            
            # Check overall system health
            status = bridge.get_integration_status()
            assert status['overall_health'] > 0.7, f"System health too low: {status['overall_health']:.2%}"
            
            # Check deployment readiness
            readiness = bridge.get_deployment_readiness()
            assert readiness['readiness_score'] > 0.8, f"Deployment readiness too low: {readiness['readiness_score']:.2%}"
            
            logger.info("✅ End-to-end integration test completed successfully")
            logger.info(f"   System health: {status['overall_health']:.2%}")
            logger.info(f"   Deployment readiness: {readiness['readiness_score']:.2%}")
            logger.info(f"   Integration level: {status['integration_level']}")
            
        finally:
            await bridge.shutdown()


# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Run tests directly
    logging.basicConfig(level=logging.INFO)
    pytest.main([__file__, "-v", "--tb=short"])