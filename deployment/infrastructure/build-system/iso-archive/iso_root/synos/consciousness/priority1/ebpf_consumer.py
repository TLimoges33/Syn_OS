#!/usr/bin/env python3
"""
Syn_OS eBPF Event Consumer
Consciousness integration for kernel eBPF monitoring programs

This service receives events from eBPF programs and feeds them into the
consciousness system for behavioral analysis and threat detection.
"""

import asyncio
import logging
import struct
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
from pathlib import Path
import json

# eBPF and BPF libraries
try:
    from bcc import BPF
    import ctypes as ct
except ImportError:
    print("Warning: BCC not installed. Install with: pip install bcc")
    BPF = None

# Consciousness integration
import sys
sys.path.append('${PROJECT_ROOT}/src')
try:
    from consciousness.realtime_consciousness import RealTimeConsciousnessProcessor
    from consciousness.core.agent_ecosystem.neural_darwinism import NeuralDarwinismEngine
except ImportError:
    print("Warning: Consciousness components not available - using mock implementations")
    RealTimeConsciousnessProcessor = None
    NeuralDarwinismEngine = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ebpf_consumer')

# Event structures matching eBPF programs
@dataclass
class NetworkEvent:
    timestamp: int
    src_ip: int
    dst_ip: int
    src_port: int
    dst_port: int
    protocol: int
    flags: int
    payload_size: int
    threat_level: int
    consciousness_score: int

@dataclass
class ProcessEvent:
    timestamp: int
    pid: int
    ppid: int
    uid: int
    gid: int
    event_type: int
    flags: int
    comm: str
    syscall_nr: int
    behavior_score: int
    threat_level: int
    consciousness_score: int

@dataclass
class MemoryEvent:
    timestamp: int
    pid: int
    ppid: int
    uid: int
    event_type: int
    flags: int
    address: int
    size: int
    prot_flags: int
    comm: str
    pattern_score: int
    threat_level: int
    consciousness_score: int

@dataclass
class SyscallEvent:
    timestamp: int
    pid: int
    ppid: int
    uid: int
    syscall_nr: int
    args: List[int]
    ret_value: int
    flags: int
    comm: str
    pattern_score: int
    threat_level: int
    consciousness_score: int

class EBPFEventConsumer:
    """Consume and process eBPF events for consciousness integration"""
    
    def __init__(self):
        self.consciousness_processor = None
        self.neural_darwinism = None
        self.event_handlers = {}
        self.stats = {
            'network_events': 0,
            'process_events': 0,
            'memory_events': 0,
            'syscall_events': 0,
            'total_consciousness_score': 0,
            'high_threat_events': 0
        }
        self.running = False
        self.ebpf_programs = {}
        
    async def initialize(self):
        """Initialize consciousness components and eBPF consumers"""
        logger.info("Initializing eBPF Event Consumer...")
        
        # Initialize consciousness components
        try:
            if RealTimeConsciousnessProcessor:
                # Create a basic config for the processor
                config = {
                    'workers': 4,
                    'queue_size': 1000,
                    'timeout': 5.0
                }
                self.consciousness_processor = RealTimeConsciousnessProcessor(config)
                await self.consciousness_processor.initialize()
                logger.info("Real-time consciousness processor initialized")
            else:
                logger.warning("Using mock consciousness processor")
            
            if NeuralDarwinismEngine:
                self.neural_darwinism = NeuralDarwinismEngine()
                await self.neural_darwinism.initialize()
                await self.neural_darwinism.start_evolution()
                logger.info("Neural Darwinism engine initialized")
            else:
                logger.warning("Using mock neural darwinism engine")
            
        except Exception as e:
            logger.error(f"Failed to initialize consciousness components: {e}")
            # Continue with mocks for testing
            logger.warning("Continuing with mock implementations")
        
        # Register event handlers
        self.event_handlers.update({
            'network': self._handle_network_event,
            'process': self._handle_process_event,
            'memory': self._handle_memory_event,
            'syscall': self._handle_syscall_event
        })
        
        logger.info("eBPF Event Consumer initialized successfully")
    
    def _parse_network_event(self, data) -> NetworkEvent:
        """Parse network event from eBPF ringbuf"""
        # Unpack binary data (adjust struct format based on eBPF struct)
        values = struct.unpack('QIIHHHIIII', data[:44])
        return NetworkEvent(
            timestamp=values[0],
            src_ip=values[1],
            dst_ip=values[2],
            src_port=values[3],
            dst_port=values[4],
            protocol=values[5],
            flags=values[6],
            payload_size=values[7],
            threat_level=values[8],
            consciousness_score=values[9]
        )
    
    def _parse_process_event(self, data) -> ProcessEvent:
        """Parse process event from eBPF ringbuf"""
        # Unpack binary data
        values = struct.unpack('QIIIIBB16sIQIQ', data[:64])
        return ProcessEvent(
            timestamp=values[0],
            pid=values[1],
            ppid=values[2],
            uid=values[3],
            gid=values[4],
            event_type=values[5],
            flags=values[6],
            comm=values[7].decode('utf-8', errors='ignore').rstrip('\x00'),
            syscall_nr=values[8],
            behavior_score=values[9],
            threat_level=values[10],
            consciousness_score=values[11]
        )
    
    def _parse_memory_event(self, data) -> MemoryEvent:
        """Parse memory event from eBPF ringbuf"""
        # Unpack binary data
        values = struct.unpack('QIIIBBQQI16sIIQ', data[:80])
        return MemoryEvent(
            timestamp=values[0],
            pid=values[1],
            ppid=values[2],
            uid=values[3],
            event_type=values[4],
            flags=values[5],
            address=values[6],
            size=values[7],
            prot_flags=values[8],
            comm=values[9].decode('utf-8', errors='ignore').rstrip('\x00'),
            pattern_score=values[10],
            threat_level=values[11],
            consciousness_score=values[12]
        )
    
    async def _handle_network_event(self, event: NetworkEvent):
        """Process network event with consciousness analysis"""
        self.stats['network_events'] += 1
        self.stats['total_consciousness_score'] += event.consciousness_score
        
        if event.threat_level > 50:
            self.stats['high_threat_events'] += 1
            logger.warning(
                f"High threat network event: "
                f"src={self._ip_to_str(event.src_ip)}:{event.src_port} -> "
                f"dst={self._ip_to_str(event.dst_ip)}:{event.dst_port} "
                f"threat={event.threat_level}"
            )
        
        # Send to consciousness for analysis
        consciousness_data = {
            'event_type': 'network',
            'timestamp': event.timestamp,
            'source_ip': self._ip_to_str(event.src_ip),
            'dest_ip': self._ip_to_str(event.dst_ip),
            'protocol': event.protocol,
            'threat_level': event.threat_level,
            'consciousness_score': event.consciousness_score,
            'payload_size': event.payload_size
        }
        
        if self.consciousness_processor:
            await self.consciousness_processor.process_consciousness_request(consciousness_data)
    
    async def _handle_process_event(self, event: ProcessEvent):
        """Process process event with consciousness analysis"""
        self.stats['process_events'] += 1
        self.stats['total_consciousness_score'] += event.consciousness_score
        
        if event.threat_level > 50:
            self.stats['high_threat_events'] += 1
            logger.warning(
                f"High threat process event: "
                f"pid={event.pid} comm={event.comm} "
                f"threat={event.threat_level}"
            )
        
        # Send to consciousness for analysis
        consciousness_data = {
            'event_type': 'process',
            'timestamp': event.timestamp,
            'pid': event.pid,
            'ppid': event.ppid,
            'process_name': event.comm,
            'event_type_id': event.event_type,
            'threat_level': event.threat_level,
            'consciousness_score': event.consciousness_score,
            'behavior_score': event.behavior_score
        }
        
        if self.consciousness_processor:
            await self.consciousness_processor.process_consciousness_request(consciousness_data)
    
    async def _handle_memory_event(self, event: MemoryEvent):
        """Process memory event with consciousness analysis"""
        self.stats['memory_events'] += 1
        self.stats['total_consciousness_score'] += event.consciousness_score
        
        if event.threat_level > 50:
            self.stats['high_threat_events'] += 1
            logger.warning(
                f"High threat memory event: "
                f"pid={event.pid} comm={event.comm} "
                f"size={event.size} threat={event.threat_level}"
            )
        
        # Send to consciousness for analysis
        consciousness_data = {
            'event_type': 'memory',
            'timestamp': event.timestamp,
            'pid': event.pid,
            'process_name': event.comm,
            'memory_size': event.size,
            'memory_address': hex(event.address),
            'protection_flags': event.prot_flags,
            'threat_level': event.threat_level,
            'consciousness_score': event.consciousness_score,
            'pattern_score': event.pattern_score
        }
        
        if self.consciousness_processor:
            await self.consciousness_processor.process_consciousness_request(consciousness_data)
    
    async def _handle_syscall_event(self, event: SyscallEvent):
        """Process syscall event with consciousness analysis"""
        self.stats['syscall_events'] += 1
        self.stats['total_consciousness_score'] += event.consciousness_score
        
        if event.threat_level > 50:
            self.stats['high_threat_events'] += 1
            logger.warning(
                f"High threat syscall event: "
                f"pid={event.pid} comm={event.comm} "
                f"syscall={event.syscall_nr} threat={event.threat_level}"
            )
        
        # Send to consciousness for analysis
        consciousness_data = {
            'event_type': 'syscall',
            'timestamp': event.timestamp,
            'pid': event.pid,
            'process_name': event.comm,
            'syscall_number': event.syscall_nr,
            'arguments': event.args,
            'return_value': event.ret_value,
            'threat_level': event.threat_level,
            'consciousness_score': event.consciousness_score,
            'pattern_score': event.pattern_score
        }
        
        if self.consciousness_processor:
            await self.consciousness_processor.process_consciousness_request(consciousness_data)
    
    def _ip_to_str(self, ip: int) -> str:
        """Convert integer IP to string"""
        return f"{ip & 0xFF}.{(ip >> 8) & 0xFF}.{(ip >> 16) & 0xFF}.{(ip >> 24) & 0xFF}"
    
    async def start_monitoring(self):
        """Start eBPF event monitoring"""
        if not BPF:
            logger.error("BCC not available - cannot start eBPF monitoring")
            return
        
        self.running = True
        logger.info("Starting eBPF event monitoring...")
        
        # This is a simplified version - in a real implementation,
        # we would load the eBPF programs and set up ringbuf consumers
        # For now, we'll simulate some events for testing
        
        while self.running:
            try:
                # Simulate processing eBPF events
                await self._simulate_events()
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _simulate_events(self):
        """Simulate eBPF events for testing (remove in production)"""
        import random
        
        # Simulate a network event
        if random.random() < 0.3:
            event = NetworkEvent(
                timestamp=int(time.time() * 1e9),
                src_ip=random.randint(0, 0xFFFFFFFF),
                dst_ip=random.randint(0, 0xFFFFFFFF),
                src_port=random.randint(1024, 65535),
                dst_port=random.choice([22, 80, 443, 3389, 1433]),
                protocol=6,  # TCP
                flags=0,
                payload_size=random.randint(64, 1500),
                threat_level=random.randint(0, 100),
                consciousness_score=random.randint(50, 300)
            )
            await self._handle_network_event(event)
        
        # Simulate a process event
        if random.random() < 0.2:
            event = ProcessEvent(
                timestamp=int(time.time() * 1e9),
                pid=random.randint(1000, 9999),
                ppid=random.randint(1, 1000),
                uid=random.choice([0, 1000, 1001]),
                gid=random.choice([0, 1000, 1001]),
                event_type=random.randint(0, 3),
                flags=0,
                comm=random.choice(['bash', 'python3', 'gcc', 'ssh', 'netcat']),
                syscall_nr=random.choice([2, 59, 62, 175]),
                behavior_score=random.randint(20, 200),
                threat_level=random.randint(0, 100),
                consciousness_score=random.randint(40, 400)
            )
            await self._handle_process_event(event)
    
    async def stop_monitoring(self):
        """Stop eBPF event monitoring"""
        logger.info("Stopping eBPF event monitoring...")
        self.running = False
        
        if self.consciousness_processor:
            await self.consciousness_processor.shutdown()
        
        if self.neural_darwinism:
            await self.neural_darwinism.stop_evolution()
    
    def get_statistics(self) -> Dict:
        """Get monitoring statistics"""
        return {
            **self.stats,
            'avg_consciousness_score': (
                self.stats['total_consciousness_score'] / 
                max(1, sum(self.stats[k] for k in ['network_events', 'process_events', 'memory_events', 'syscall_events']))
            ),
            'high_threat_percentage': (
                (self.stats['high_threat_events'] / 
                 max(1, sum(self.stats[k] for k in ['network_events', 'process_events', 'memory_events', 'syscall_events']))) * 100
            )
        }

async def main():
    """Main entry point for eBPF event consumer"""
    consumer = EBPFEventConsumer()
    
    try:
        await consumer.initialize()
        
        # Start monitoring in background
        monitoring_task = asyncio.create_task(consumer.start_monitoring())
        
        # Print statistics periodically
        while True:
            await asyncio.sleep(10)
            stats = consumer.get_statistics()
            logger.info(f"eBPF Event Statistics: {json.dumps(stats, indent=2)}")
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await consumer.stop_monitoring()
        if 'monitoring_task' in locals():
            monitoring_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
