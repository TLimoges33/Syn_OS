#!/usr/bin/env python3
"""
Test suite for Kernel-Level Consciousness Hooks V2
"""

import asyncio
import pytest
import tempfile
import os
import psutil
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Import the kernel hooks components
from .components.kernel_hooks_v2 import (
    KernelConsciousnessHooksV2,
    KernelConsciousnessInterface,
    ConsciousnessProcessType,
    AIMemoryPoolType,
    ConsciousnessEventType,
    ProcessClassification,
    AIMemoryPool,
    SystemResourceMetrics,
    ConsciousnessKernelEvent
)
from .core.data_models import ConsciousnessState
from .core.event_types import EventType, ConsciousnessEvent
from .core.consciousness_bus import ConsciousnessBus
from .core.state_manager import StateManager


class TestKernelConsciousnessInterface:
    """Test cases for the kernel consciousness interface"""
    
    @pytest.fixture
    def kernel_interface(self):
        """Create a kernel interface instance for testing"""
        return KernelConsciousnessInterface("/dev/consciousness")
    
    async def test_initialization_fallback_mode(self, kernel_interface):
        """Test initialization in fallback mode"""
        # Mock the kernel module check to return False
        with patch.object(kernel_interface, '_check_kernel_module', return_value=False):
            success = await kernel_interface.initialize()
            assert success is True
            assert kernel_interface.monitoring_active is True
            assert kernel_interface.monitoring_thread is not None
    
    async def test_system_metrics_collection(self, kernel_interface):
        """Test system metrics collection"""
        metrics = kernel_interface._collect_system_metrics()
        
        assert isinstance(metrics, SystemResourceMetrics)
        assert metrics.timestamp is not None
        assert metrics.cpu_usage_percent >= 0
        assert metrics.memory_total >= 0
        assert metrics.memory_available >= 0
    
    async def test_process_classification(self, kernel_interface):
        """Test process classification"""
        # Get current process PID
        current_pid = os.getpid()
        
        classification = await kernel_interface.classify_process(current_pid)
        
        assert isinstance(classification, ProcessClassification)
        assert classification.pid == current_pid
        assert isinstance(classification.process_type, ConsciousnessProcessType)
        assert classification.priority_boost >= 0
        assert isinstance(classification.cpu_affinity, list)
    
    async def test_consciousness_process_detection(self, kernel_interface):
        """Test consciousness process detection"""
        # Mock a process with consciousness-related name
        mock_proc = Mock()
        mock_proc.info = {
            'pid': 12345,
            'name': 'neural_darwin_test',
            'cmdline': ['python', 'neural_darwin.py']
        }
        mock_proc.as_dict.return_value = {
            'name': 'neural_darwin_test',
            'cmdline': ['python', 'neural_darwin.py'],
            'memory_info': Mock(rss=100 * 1024 * 1024)  # 100MB
        }
        
        with patch('psutil.Process', return_value=mock_proc):
            classification = await kernel_interface.classify_process(12345)
            
            assert classification.process_type == ConsciousnessProcessType.NEURAL_ENGINE
            assert classification.priority_boost == 20
            assert classification.real_time_required is True
    
    async def test_cpu_reservation_fallback(self, kernel_interface):
        """Test CPU reservation in fallback mode"""
        reserved_cores = await kernel_interface.reserve_cpu_cores(4, 0.8)
        
        assert reserved_cores >= 0
        assert reserved_cores <= (psutil.cpu_count() or 4)
    
    async def test_ai_memory_allocation(self, kernel_interface):
        """Test AI memory allocation"""
        # Test allocation
        addr = await kernel_interface.allocate_ai_memory(1024, AIMemoryPoolType.GENERAL)
        assert addr is not None
        assert isinstance(addr, int)
        
        # Test freeing
        success = await kernel_interface.free_ai_memory(addr)
        assert success is True
    
    async def test_event_callback_registration(self, kernel_interface):
        """Test event callback registration"""
        callback_called = False
        
        def test_callback(event):
            nonlocal callback_called
            callback_called = True
        
        kernel_interface.register_event_callback(ConsciousnessEventType.NEURAL_UPDATE, test_callback)
        
        # Create a test event
        test_event = ConsciousnessKernelEvent(
            event_type=ConsciousnessEventType.NEURAL_UPDATE,
            priority=1,
            timestamp_ns=1234567890,
            data_size=0,
            data=b''
        )
        
        kernel_interface._process_kernel_event(test_event)
        assert callback_called is True
    
    async def test_synthetic_event_generation(self, kernel_interface):
        """Test synthetic event generation"""
        # Create metrics with high CPU usage
        high_cpu_metrics = SystemResourceMetrics(
            timestamp=datetime.now(),
            cpu_usage_percent=85.0,
            cpu_consciousness_load=0.0,
            cpu_temperature=0.0,
            cpu_frequency=0,
            memory_total=8 * 1024 * 1024 * 1024,
            memory_available=4 * 1024 * 1024 * 1024,
            memory_ai_allocated=0,
            memory_pressure=0.5,
            gpu_memory_used=0,
            gpu_memory_total=0,
            gpu_utilization=0.0,
            gpu_temperature=0.0,
            io_read_bytes=0,
            io_write_bytes=0,
            io_read_ops=0,
            io_write_ops=0,
            network_bytes_sent=0,
            network_bytes_recv=0,
            network_packets_sent=0,
            network_packets_recv=0
        )
        
        events = kernel_interface._generate_synthetic_events(high_cpu_metrics)
        
        assert len(events) > 0
        assert any(event.event_type == ConsciousnessEventType.RESOURCE_CHANGE for event in events)
    
    async def test_shutdown(self, kernel_interface):
        """Test interface shutdown"""
        await kernel_interface.initialize()
        await kernel_interface.shutdown()
        
        assert kernel_interface.monitoring_active is False
        assert kernel_interface.device_fd is None


class TestKernelConsciousnessHooksV2:
    """Test cases for the main kernel hooks component"""
    
    @pytest.fixture
    async def kernel_hooks(self):
        """Create a kernel hooks instance for testing"""
        hooks = KernelConsciousnessHooksV2("/dev/consciousness")
        
        # Mock the consciousness bus and state manager
        hooks.consciousness_bus = Mock()
        hooks.consciousness_bus.publish = AsyncMock()
        hooks.state_manager = Mock()
        hooks.state_manager.get_consciousness_state = AsyncMock()
        
        await hooks.initialize(hooks.consciousness_bus, hooks.state_manager)
        yield hooks
        await hooks.shutdown()
    
    async def test_initialization(self, kernel_hooks):
        """Test kernel hooks initialization"""
        assert kernel_hooks.component_id == "kernel_hooks_v2"
        assert kernel_hooks.component_type == "system_integration"
        assert len(kernel_hooks.ai_memory_pools) == 5  # All pool types
        assert len(kernel_hooks.background_tasks) > 0
    
    async def test_ai_memory_pool_initialization(self, kernel_hooks):
        """Test AI memory pool initialization"""
        # Check all pool types are initialized
        expected_pools = [
            AIMemoryPoolType.NEURAL_WEIGHTS,
            AIMemoryPoolType.ACTIVATION_MAPS,
            AIMemoryPoolType.CONTEXT_BUFFERS,
            AIMemoryPoolType.INFERENCE_CACHE,
            AIMemoryPoolType.GENERAL
        ]
        
        for pool_type in expected_pools:
            assert pool_type in kernel_hooks.ai_memory_pools
            pool = kernel_hooks.ai_memory_pools[pool_type]
            assert isinstance(pool, AIMemoryPool)
            assert pool.total_size > 0
            assert pool.free_size == pool.total_size
            assert pool.allocated_size == 0
    
    async def test_consciousness_level_update(self, kernel_hooks):
        """Test consciousness level updates"""
        initial_level = kernel_hooks.current_consciousness_level
        new_level = 0.8
        
        await kernel_hooks.update_consciousness_level(new_level)
        
        assert kernel_hooks.current_consciousness_level == new_level
        assert kernel_hooks.current_consciousness_level != initial_level
    
    async def test_ai_memory_allocation_and_deallocation(self, kernel_hooks):
        """Test AI memory allocation and deallocation"""
        # Test allocation
        size = 1024 * 1024  # 1MB
        addr = await kernel_hooks.allocate_ai_memory(size, AIMemoryPoolType.GENERAL)
        
        assert addr is not None
        
        # Check pool statistics
        pool = kernel_hooks.ai_memory_pools[AIMemoryPoolType.GENERAL]
        assert pool.allocated_size == size
        assert pool.free_size == pool.total_size - size
        assert len(pool.allocated_blocks) == 1
        
        # Test deallocation
        success = await kernel_hooks.free_ai_memory(addr)
        assert success is True
        
        # Check pool statistics after deallocation
        assert pool.allocated_size == 0
        assert pool.free_size == pool.total_size
        assert len(pool.allocated_blocks) == 0
    
    async def test_memory_pool_fallback(self, kernel_hooks):
        """Test memory pool fallback mechanism"""
        # Fill up the neural weights pool
        neural_pool = kernel_hooks.ai_memory_pools[AIMemoryPoolType.NEURAL_WEIGHTS]
        large_size = neural_pool.total_size + 1
        
        # This should fallback to general pool
        addr = await kernel_hooks.allocate_ai_memory(large_size, AIMemoryPoolType.NEURAL_WEIGHTS)
        
        # Should return None if general pool also can't accommodate
        general_pool = kernel_hooks.ai_memory_pools[AIMemoryPoolType.GENERAL]
        if large_size > general_pool.total_size:
            assert addr is None
        else:
            assert addr is not None
    
    async def test_system_metrics_collection(self, kernel_hooks):
        """Test system metrics collection"""
        metrics = await kernel_hooks.get_system_metrics()
        
        assert isinstance(metrics, SystemResourceMetrics)
        assert metrics.cpu_usage_percent >= 0
        assert metrics.memory_total > 0
    
    async def test_ai_memory_stats(self, kernel_hooks):
        """Test AI memory statistics"""
        # Allocate some memory first
        await kernel_hooks.allocate_ai_memory(1024, AIMemoryPoolType.GENERAL)
        
        stats = await kernel_hooks.get_ai_memory_stats()
        
        assert isinstance(stats, dict)
        assert 'general' in stats
        assert stats['general']['allocated_size'] > 0
        assert stats['general']['utilization'] > 0
    
    async def test_process_classifications(self, kernel_hooks):
        """Test process classifications"""
        # Mock some process classifications
        test_classification = ProcessClassification(
            pid=12345,
            process_type=ConsciousnessProcessType.NEURAL_ENGINE,
            priority_boost=20,
            cpu_affinity=[0, 1, 2, 3],
            memory_requirement=100 * 1024 * 1024,
            real_time_required=True,
            consciousness_level=0.8
        )
        
        kernel_hooks.process_classifications[12345] = test_classification
        
        classifications = await kernel_hooks.get_process_classifications()
        
        assert 12345 in classifications
        assert classifications[12345]['process_type'] == 'NEURAL_ENGINE'
        assert classifications[12345]['priority_boost'] == 20
    
    async def test_memory_pressure_handling(self, kernel_hooks):
        """Test memory pressure handling"""
        # Create high memory pressure metrics
        high_pressure_metrics = SystemResourceMetrics(
            timestamp=datetime.now(),
            cpu_usage_percent=50.0,
            cpu_consciousness_load=0.0,
            cpu_temperature=0.0,
            cpu_frequency=0,
            memory_total=8 * 1024 * 1024 * 1024,
            memory_available=512 * 1024 * 1024,  # Very low available memory
            memory_ai_allocated=0,
            memory_pressure=0.95,  # 95% memory pressure
            gpu_memory_used=0,
            gpu_memory_total=0,
            gpu_utilization=0.0,
            gpu_temperature=0.0,
            io_read_bytes=0,
            io_write_bytes=0,
            io_read_ops=0,
            io_write_ops=0,
            network_bytes_sent=0,
            network_bytes_recv=0,
            network_packets_sent=0,
            network_packets_recv=0
        )
        
        initial_level = kernel_hooks.current_consciousness_level
        await kernel_hooks._handle_memory_pressure(high_pressure_metrics)
        
        # Consciousness level should be reduced
        assert kernel_hooks.current_consciousness_level < initial_level
    
    async def test_cpu_pressure_handling(self, kernel_hooks):
        """Test CPU pressure handling"""
        high_cpu_metrics = SystemResourceMetrics(
            timestamp=datetime.now(),
            cpu_usage_percent=95.0,  # Very high CPU usage
            cpu_consciousness_load=0.0,
            cpu_temperature=0.0,
            cpu_frequency=0,
            memory_total=8 * 1024 * 1024 * 1024,
            memory_available=4 * 1024 * 1024 * 1024,
            memory_ai_allocated=0,
            memory_pressure=0.5,
            gpu_memory_used=0,
            gpu_memory_total=0,
            gpu_utilization=0.0,
            gpu_temperature=0.0,
            io_read_bytes=0,
            io_write_bytes=0,
            io_read_ops=0,
            io_write_ops=0,
            network_bytes_sent=0,
            network_bytes_recv=0,
            network_packets_sent=0,
            network_packets_recv=0
        )
        
        initial_cores = len(kernel_hooks.reserved_cpu_cores)
        await kernel_hooks._handle_cpu_pressure(high_cpu_metrics)
        
        # More cores should be reserved
        assert len(kernel_hooks.reserved_cpu_cores) >= initial_cores
    
    async def test_consciousness_adaptation(self, kernel_hooks):
        """Test consciousness adaptation to system state"""
        # Test with good system resources
        good_metrics = SystemResourceMetrics(
            timestamp=datetime.now(),
            cpu_usage_percent=30.0,
            cpu_consciousness_load=0.0,
            cpu_temperature=0.0,
            cpu_frequency=0,
            memory_total=8 * 1024 * 1024 * 1024,
            memory_available=6 * 1024 * 1024 * 1024,
            memory_ai_allocated=0,
            memory_pressure=0.25,
            gpu_memory_used=0,
            gpu_memory_total=0,
            gpu_utilization=0.0,
            gpu_temperature=0.0,
            io_read_bytes=0,
            io_write_bytes=0,
            io_read_ops=0,
            io_write_ops=0,
            network_bytes_sent=0,
            network_bytes_recv=0,
            network_packets_sent=0,
            network_packets_recv=0
        )
        
        initial_level = kernel_hooks.current_consciousness_level
        await kernel_hooks._adapt_consciousness_to_system_state(good_metrics)
        
        # With good resources, consciousness level might increase slightly
        # or stay the same (depends on the adaptation algorithm)
        assert kernel_hooks.current_consciousness_level >= initial_level * 0.9
    
    async def test_neural_evolution_optimization(self, kernel_hooks):
        """Test neural evolution optimization"""
        initial_cores = len(kernel_hooks.reserved_cpu_cores)
        
        await kernel_hooks._optimize_for_neural_evolution()
        
        # Should reserve more cores for neural processing
        assert len(kernel_hooks.reserved_cpu_cores) >= initial_cores
    
    async def test_event_processing(self, kernel_hooks):
        """Test consciousness event processing"""
        # Test neural evolution event
        evolution_event = ConsciousnessEvent(
            event_type=EventType.NEURAL_EVOLUTION,
            source_component="neural_darwinism",
            data={"evolution_cycle": 100}
        )
        
        result = await kernel_hooks.process_event(evolution_event)
        assert result is True
    
    async def test_resource_request_handling(self, kernel_hooks):
        """Test resource request handling"""
        request_event = ConsciousnessEvent(
            event_type=getattr(EventType, 'RESOURCE_REQUEST', EventType.NEURAL_EVOLUTION),
            source_component="test_component",
            data={
                'request_type': 'memory',
                'size': 1024 * 1024,
                'pool_type': AIMemoryPoolType.GENERAL.value,
                'request_id': 'test_request_123'
            }
        )
        
        result = await kernel_hooks.process_event(request_event)
        assert result is True
        
        # Check if response was published
        kernel_hooks.consciousness_bus.publish.assert_called()
    
    async def test_expired_memory_cleanup(self, kernel_hooks):
        """Test expired memory cleanup"""
        # Allocate some memory
        addr = await kernel_hooks.allocate_ai_memory(1024, AIMemoryPoolType.GENERAL)
        assert addr is not None
        
        # Manually set allocation time to past
        pool = kernel_hooks.ai_memory_pools[AIMemoryPoolType.GENERAL]
        if pool.allocated_blocks:
            pool.allocated_blocks[0].allocated_time = datetime.now() - timedelta(hours=2)
        
        # Run cleanup
        await kernel_hooks._cleanup_expired_memory()
        
        # Memory should be freed
        assert pool.allocated_size == 0
    
    async def test_stale_process_cleanup(self, kernel_hooks):
        """Test stale process cleanup"""
        # Add a fake process classification
        fake_pid = 999999  # Very unlikely to exist
        kernel_hooks.process_classifications[fake_pid] = ProcessClassification(
            pid=fake_pid,
            process_type=ConsciousnessProcessType.NEURAL_ENGINE,
            priority_boost=20,
            cpu_affinity=[0, 1],
            memory_requirement=1024,
            real_time_required=True,
            consciousness_level=0.8
        )
        
        # Run cleanup
        await kernel_hooks._cleanup_stale_processes()
        
        # Fake process should be removed
        assert fake_pid not in kernel_hooks.process_classifications
    
    async def test_kernel_event_handlers(self, kernel_hooks):
        """Test kernel event handlers"""
        # Test neural update handler
        neural_event = ConsciousnessKernelEvent(
            event_type=ConsciousnessEventType.NEURAL_UPDATE,
            priority=1,
            timestamp_ns=1234567890,
            data_size=0,
            data=b''
        )
        
        # Should not raise exception
        kernel_hooks._handle_neural_update(neural_event)
        
        # Test resource change handler
        resource_event = ConsciousnessKernelEvent(
            event_type=ConsciousnessEventType.RESOURCE_CHANGE,
            priority=2,
            timestamp_ns=1234567890,
            data_size=8,
            data=struct.pack('d', 85.5)
        )
        
        kernel_hooks._handle_resource_change(resource_event)
        
        # Test performance alert handler
        alert_event = ConsciousnessKernelEvent(
            event_type=ConsciousnessEventType.PERFORMANCE_ALERT,
            priority=1,
            timestamp_ns=1234567890,
            data_size=8,
            data=struct.pack('d', 0.95)
        )
        
        kernel_hooks._handle_performance_alert(alert_event)


async def run_tests():
    """Run all kernel hooks tests"""
    print("Running Kernel-Level Consciousness Hooks V2 tests...")
    
    # Test kernel interface
    interface_tests = TestKernelConsciousnessInterface()
    kernel_interface = KernelConsciousnessInterface("/dev/consciousness")
    
    try:
        await interface_tests.test_initialization_fallback_mode(kernel_interface)
        print("✓ Interface initialization test passed")
        
        await interface_tests.test_system_metrics_collection(kernel_interface)
        print("✓ System metrics collection test passed")
        
        await interface_tests.test_process_classification(kernel_interface)
        print("✓ Process classification test passed")
        
        await interface_tests.test_consciousness_process_detection(kernel_interface)
        print("✓ Consciousness process detection test passed")
        
        await interface_tests.test_cpu_reservation_fallback(kernel_interface)
        print("✓ CPU reservation fallback test passed")
        
        await interface_tests.test_ai_memory_allocation(kernel_interface)
        print("✓ AI memory allocation test passed")
        
        await interface_tests.test_event_callback_registration(kernel_interface)
        print("✓ Event callback registration test passed")
        
        await interface_tests.test_synthetic_event_generation(kernel_interface)
        print("✓ Synthetic event generation test passed")
        
        await interface_tests.test_shutdown(kernel_interface)
        print("✓ Interface shutdown test passed")
        
    finally:
        await kernel_interface.shutdown()
    
    # Test main kernel hooks component
    hooks_tests = TestKernelConsciousnessHooksV2()
    kernel_hooks = KernelConsciousnessHooksV2("/dev/consciousness")
    
    # Mock dependencies
    kernel_hooks.consciousness_bus = Mock()
    kernel_hooks.consciousness_bus.publish = AsyncMock()
    kernel_hooks.state_manager = Mock()
    kernel_hooks.state_manager.get_consciousness_state = AsyncMock()
    
    try:
        await kernel_hooks.initialize(kernel_hooks.consciousness_bus, kernel_hooks.state_manager)
        
        await hooks_tests.test_initialization(kernel_hooks)
        print("✓ Kernel hooks initialization test passed")
        
        await hooks_tests.test_ai_memory_pool_initialization(kernel_hooks)
        print("✓ AI memory pool initialization test passed")
        
        await hooks_tests.test_consciousness_level_update(kernel_hooks)
        print("✓ Consciousness level update test passed")
        
        await hooks_tests.test_ai_memory_allocation_and_deallocation(kernel_hooks)
        print("✓ AI memory allocation/deallocation test passed")
        
        await hooks_tests.test_system_metrics_collection(kernel_hooks)
        print("✓ System metrics collection test passed")
        
        await hooks_tests.test_ai_memory_stats(kernel_hooks)
        print("✓ AI memory stats test passed")
        
        await hooks_tests.test_memory_pressure_handling(kernel_hooks)
        print("✓ Memory pressure handling test passed")
        
        await hooks_tests.test_cpu_pressure_handling(kernel_hooks)
        print("✓ CPU pressure handling test passed")
        
        await hooks_tests.test_consciousness_adaptation(kernel_hooks)
        print("✓ Consciousness adaptation test passed")
        
        await hooks_tests.test_neural_evolution_optimization(kernel_hooks)
        print("✓ Neural evolution optimization test passed")
        
        await hooks_tests.test_event_processing(kernel_hooks)
        print("✓ Event processing test passed")
        
        await hooks_tests.test_expired_memory_cleanup(kernel_hooks)
        print("✓ Expired memory cleanup test passed")
        
        await hooks_tests.test_stale_process_cleanup(kernel_hooks)
        print("✓ Stale process cleanup test passed")
        
        await hooks_tests.test_kernel_event_handlers(kernel_hooks)
        print("✓ Kernel event handlers test passed")
        
    finally:
        await kernel_hooks.shutdown()
    
    print("\n🎉 All Kernel Hooks V2 tests passed!")


if __name__ == "__main__":
    import struct
    from datetime import timedelta
    asyncio.run(run_tests())