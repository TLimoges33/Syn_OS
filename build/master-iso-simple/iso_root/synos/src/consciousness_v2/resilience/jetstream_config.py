"""
Enhanced NATS JetStream Configuration
====================================

Provides production-ready JetStream stream configuration, consumer management,
and advanced features for the consciousness system.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
try:
    import nats
    from nats.js.api import StreamConfig, ConsumerConfig, RetentionPolicy, StorageType, DiscardPolicy
    NATS_AVAILABLE = True
except ImportError:
    # Fallback for when nats-py is not available
    NATS_AVAILABLE = False
    nats = None
    StreamConfig = None
    ConsumerConfig = None
    RetentionPolicy = None
    StorageType = None
    DiscardPolicy = None


class StreamRetentionPolicy(Enum):
    """Stream retention policies"""
    LIMITS = "limits"
    INTEREST = "interest"
    WORK_QUEUE = "workqueue"


class StreamStorageType(Enum):
    """Stream storage types"""
    FILE = "file"
    MEMORY = "memory"


class StreamDiscardPolicy(Enum):
    """Stream discard policies"""
    OLD = "old"
    NEW = "new"


@dataclass
class ConsciousnessStreamConfig:
    """Configuration for consciousness-specific streams"""
    name: str
    subjects: List[str]
    description: str = ""
    
    # Retention settings
    retention: StreamRetentionPolicy = StreamRetentionPolicy.LIMITS
    max_consumers: int = -1
    max_msgs: int = 100000
    max_bytes: int = 1024 * 1024 * 1024  # 1GB
    max_age: int = 7 * 24 * 3600  # 7 days in seconds
    max_msgs_per_subject: int = 10000
    
    # Storage settings
    storage: StreamStorageType = StreamStorageType.FILE
    replicas: int = 1
    
    # Performance settings
    discard: StreamDiscardPolicy = StreamDiscardPolicy.OLD
    duplicate_window: int = 2 * 60  # 2 minutes
    
    # Advanced settings
    no_ack: bool = False
    template_owner: str = ""
    
    def to_nats_config(self) -> StreamConfig:
        """Convert to NATS StreamConfig"""
        return StreamConfig(
            name=self.name,
            subjects=self.subjects,
            retention=RetentionPolicy.LIMITS if self.retention == StreamRetentionPolicy.LIMITS else 
                     RetentionPolicy.INTEREST if self.retention == StreamRetentionPolicy.INTEREST else
                     RetentionPolicy.WORKQUEUE,
            max_consumers=self.max_consumers,
            max_msgs=self.max_msgs,
            max_bytes=self.max_bytes,
            max_age=self.max_age,
            max_msgs_per_subject=self.max_msgs_per_subject,
            storage=StorageType.FILE if self.storage == StreamStorageType.FILE else StorageType.MEMORY,
            replicas=self.replicas,
            discard=DiscardPolicy.OLD if self.discard == StreamDiscardPolicy.OLD else DiscardPolicy.NEW,
            duplicate_window=self.duplicate_window,
            no_ack=self.no_ack,
            template_owner=self.template_owner,
            description=self.description
        )


@dataclass
class ConsciousnessConsumerConfig:
    """Configuration for consciousness-specific consumers"""
    name: str
    stream_name: str
    description: str = ""
    
    # Delivery settings
    durable_name: Optional[str] = None
    deliver_subject: Optional[str] = None
    deliver_group: Optional[str] = None
    
    # Acknowledgment settings
    ack_policy: str = "explicit"  # explicit, none, all
    ack_wait: int = 30  # seconds
    max_deliver: int = 5
    
    # Replay settings
    replay_policy: str = "instant"  # instant, original
    
    # Rate limiting
    rate_limit_bps: int = 0  # bytes per second, 0 = unlimited
    max_ack_pending: int = 1000
    
    # Filtering
    filter_subject: str = ""
    
    def to_nats_config(self) -> ConsumerConfig:
        """Convert to NATS ConsumerConfig"""
        return ConsumerConfig(
            name=self.name,
            durable_name=self.durable_name or self.name,
            deliver_subject=self.deliver_subject,
            deliver_group=self.deliver_group,
            ack_policy=self.ack_policy,
            ack_wait=self.ack_wait,
            max_deliver=self.max_deliver,
            replay_policy=self.replay_policy,
            rate_limit_bps=self.rate_limit_bps,
            max_ack_pending=self.max_ack_pending,
            filter_subject=self.filter_subject,
            description=self.description
        )


class JetStreamManager:
    """
    Enhanced JetStream configuration and management
    """
    
    def __init__(self, nats_client: Optional[nats.NATS] = None):
        """
        Initialize JetStream manager
        
        Args:
            nats_client: NATS client instance
        """
        self.nats_client = nats_client
        self.js: Optional[nats.js.JetStreamContext] = None
        self.logger = logging.getLogger(__name__)
        
        # Stream and consumer configurations
        self.stream_configs: Dict[str, ConsciousnessStreamConfig] = {}
        self.consumer_configs: Dict[str, ConsciousnessConsumerConfig] = {}
        
        # Initialize default configurations
        self._create_default_configurations()
    
    def set_nats_client(self, nats_client: nats.NATS):
        """Set NATS client and initialize JetStream context"""
        self.nats_client = nats_client
        if nats_client:
            self.js = nats_client.jetstream()
    
    def _create_default_configurations(self):
        """Create default stream and consumer configurations"""
        
        # Consciousness Events Stream
        self.stream_configs['CONSCIOUSNESS_EVENTS'] = ConsciousnessStreamConfig(
            name='CONSCIOUSNESS_EVENTS',
            subjects=['consciousness.>'],
            description='Consciousness system events and state changes',
            max_msgs=50000,
            max_bytes=512 * 1024 * 1024,  # 512MB
            max_age=24 * 3600,  # 24 hours
            storage=StreamStorageType.FILE,
            replicas=1
        )
        
        # Orchestrator Events Stream
        self.stream_configs['ORCHESTRATOR_EVENTS'] = ConsciousnessStreamConfig(
            name='ORCHESTRATOR_EVENTS',
            subjects=['orchestrator.>'],
            description='Service orchestration events and commands',
            max_msgs=100000,
            max_bytes=1024 * 1024 * 1024,  # 1GB
            max_age=7 * 24 * 3600,  # 7 days
            storage=StreamStorageType.FILE,
            replicas=1
        )
        
        # Security Events Stream
        self.stream_configs['SECURITY_EVENTS'] = ConsciousnessStreamConfig(
            name='SECURITY_EVENTS',
            subjects=['security.>'],
            description='Security events, threats, and monitoring data',
            max_msgs=200000,
            max_bytes=2 * 1024 * 1024 * 1024,  # 2GB
            max_age=30 * 24 * 3600,  # 30 days
            storage=StreamStorageType.FILE,
            replicas=1
        )
        
        # Health and Metrics Stream
        self.stream_configs['HEALTH_METRICS'] = ConsciousnessStreamConfig(
            name='HEALTH_METRICS',
            subjects=['health.>', 'metrics.>'],
            description='System health checks and performance metrics',
            max_msgs=500000,
            max_bytes=1024 * 1024 * 1024,  # 1GB
            max_age=7 * 24 * 3600,  # 7 days
            storage=StreamStorageType.FILE,
            replicas=1
        )
        
        # High Priority Events Stream
        self.stream_configs['PRIORITY_EVENTS'] = ConsciousnessStreamConfig(
            name='PRIORITY_EVENTS',
            subjects=['priority.>', 'critical.>', 'alert.>'],
            description='High priority and critical system events',
            max_msgs=10000,
            max_bytes=100 * 1024 * 1024,  # 100MB
            max_age=30 * 24 * 3600,  # 30 days
            storage=StreamStorageType.MEMORY,  # Fast access for critical events
            replicas=1
        )
        
        # Create default consumers
        self._create_default_consumers()
    
    def _create_default_consumers(self):
        """Create default consumer configurations"""
        
        # Consciousness Bridge Consumer
        self.consumer_configs['consciousness_bridge'] = ConsciousnessConsumerConfig(
            name='consciousness_bridge',
            stream_name='ORCHESTRATOR_EVENTS',
            description='Consciousness bridge consumer for orchestrator events',
            durable_name='consciousness_bridge_durable',
            ack_policy='explicit',
            ack_wait=30,
            max_deliver=3,
            max_ack_pending=100
        )
        
        # Orchestrator Consumer
        self.consumer_configs['orchestrator_service'] = ConsciousnessConsumerConfig(
            name='orchestrator_service',
            stream_name='CONSCIOUSNESS_EVENTS',
            description='Orchestrator consumer for consciousness events',
            durable_name='orchestrator_service_durable',
            ack_policy='explicit',
            ack_wait=30,
            max_deliver=3,
            max_ack_pending=200
        )
        
        # Security Dashboard Consumer
        self.consumer_configs['security_dashboard'] = ConsciousnessConsumerConfig(
            name='security_dashboard',
            stream_name='SECURITY_EVENTS',
            description='Security dashboard consumer for security events',
            durable_name='security_dashboard_durable',
            ack_policy='explicit',
            ack_wait=60,
            max_deliver=5,
            max_ack_pending=500
        )
        
        # Health Monitor Consumer
        self.consumer_configs['health_monitor'] = ConsciousnessConsumerConfig(
            name='health_monitor',
            stream_name='HEALTH_METRICS',
            description='Health monitor consumer for metrics and health data',
            durable_name='health_monitor_durable',
            ack_policy='explicit',
            ack_wait=30,
            max_deliver=2,
            max_ack_pending=1000
        )
        
        # Priority Events Consumer
        self.consumer_configs['priority_handler'] = ConsciousnessConsumerConfig(
            name='priority_handler',
            stream_name='PRIORITY_EVENTS',
            description='Priority event handler for critical events',
            durable_name='priority_handler_durable',
            ack_policy='explicit',
            ack_wait=10,  # Fast acknowledgment for critical events
            max_deliver=5,
            max_ack_pending=50
        )
    
    async def create_all_streams(self) -> Dict[str, bool]:
        """Create all configured streams"""
        if not self.js:
            raise RuntimeError("JetStream context not available")
        
        results = {}
        
        for stream_name, config in self.stream_configs.items():
            try:
                # Check if stream already exists
                try:
                    await self.js.stream_info(stream_name)
                    self.logger.info(f"Stream {stream_name} already exists")
                    results[stream_name] = True
                    continue
                except:
                    pass
                
                # Create stream
                nats_config = config.to_nats_config()
                await self.js.add_stream(nats_config)
                
                self.logger.info(f"Created stream {stream_name}")
                results[stream_name] = True
                
            except Exception as e:
                self.logger.error(f"Failed to create stream {stream_name}: {e}")
                results[stream_name] = False
        
        return results
    
    async def create_all_consumers(self) -> Dict[str, bool]:
        """Create all configured consumers"""
        if not self.js:
            raise RuntimeError("JetStream context not available")
        
        results = {}
        
        for consumer_name, config in self.consumer_configs.items():
            try:
                # Check if consumer already exists
                try:
                    await self.js.consumer_info(config.stream_name, consumer_name)
                    self.logger.info(f"Consumer {consumer_name} already exists")
                    results[consumer_name] = True
                    continue
                except:
                    pass
                
                # Create consumer
                nats_config = config.to_nats_config()
                await self.js.add_consumer(config.stream_name, nats_config)
                
                self.logger.info(f"Created consumer {consumer_name} for stream {config.stream_name}")
                results[consumer_name] = True
                
            except Exception as e:
                self.logger.error(f"Failed to create consumer {consumer_name}: {e}")
                results[consumer_name] = False
        
        return results
    
    async def update_stream_config(self, stream_name: str, config: ConsciousnessStreamConfig) -> bool:
        """Update stream configuration"""
        if not self.js:
            raise RuntimeError("JetStream context not available")
        
        try:
            nats_config = config.to_nats_config()
            await self.js.update_stream(nats_config)
            
            self.stream_configs[stream_name] = config
            self.logger.info(f"Updated stream configuration for {stream_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update stream {stream_name}: {e}")
            return False
    
    async def delete_stream(self, stream_name: str) -> bool:
        """Delete a stream"""
        if not self.js:
            raise RuntimeError("JetStream context not available")
        
        try:
            await self.js.delete_stream(stream_name)
            
            if stream_name in self.stream_configs:
                del self.stream_configs[stream_name]
            
            self.logger.info(f"Deleted stream {stream_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete stream {stream_name}: {e}")
            return False
    
    async def get_stream_info(self, stream_name: str) -> Optional[Dict[str, Any]]:
        """Get stream information"""
        if not self.js:
            return None
        
        try:
            info = await self.js.stream_info(stream_name)
            return {
                'name': info.config.name,
                'subjects': info.config.subjects,
                'messages': info.state.messages,
                'bytes': info.state.bytes,
                'first_seq': info.state.first_seq,
                'last_seq': info.state.last_seq,
                'consumers': info.state.consumer_count,
                'created': info.created.isoformat() if info.created else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get stream info for {stream_name}: {e}")
            return None
    
    async def get_all_streams_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information for all streams"""
        results = {}
        
        for stream_name in self.stream_configs.keys():
            info = await self.get_stream_info(stream_name)
            if info:
                results[stream_name] = info
        
        return results
    
    async def get_consumer_info(self, stream_name: str, consumer_name: str) -> Optional[Dict[str, Any]]:
        """Get consumer information"""
        if not self.js:
            return None
        
        try:
            info = await self.js.consumer_info(stream_name, consumer_name)
            return {
                'name': info.name,
                'stream_name': info.stream_name,
                'created': info.created.isoformat() if info.created else None,
                'delivered': info.delivered.consumer_seq if info.delivered else 0,
                'ack_pending': info.ack_floor.consumer_seq if info.ack_floor else 0,
                'num_pending': info.num_pending,
                'num_redelivered': info.num_redelivered
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get consumer info for {consumer_name}: {e}")
            return None
    
    async def purge_stream(self, stream_name: str) -> bool:
        """Purge all messages from a stream"""
        if not self.js:
            raise RuntimeError("JetStream context not available")
        
        try:
            await self.js.purge_stream(stream_name)
            self.logger.info(f"Purged stream {stream_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to purge stream {stream_name}: {e}")
            return False
    
    async def get_jetstream_account_info(self) -> Optional[Dict[str, Any]]:
        """Get JetStream account information"""
        if not self.js:
            return None
        
        try:
            info = await self.js.account_info()
            return {
                'memory': info.memory,
                'storage': info.storage,
                'streams': info.streams,
                'consumers': info.consumers,
                'limits': {
                    'max_memory': info.limits.max_memory,
                    'max_storage': info.limits.max_storage,
                    'max_streams': info.limits.max_streams,
                    'max_consumers': info.limits.max_consumers
                } if info.limits else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get JetStream account info: {e}")
            return None
    
    def add_custom_stream(self, config: ConsciousnessStreamConfig):
        """Add a custom stream configuration"""
        self.stream_configs[config.name] = config
        self.logger.info(f"Added custom stream configuration: {config.name}")
    
    def add_custom_consumer(self, config: ConsciousnessConsumerConfig):
        """Add a custom consumer configuration"""
        self.consumer_configs[config.name] = config
        self.logger.info(f"Added custom consumer configuration: {config.name}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on JetStream"""
        if not self.js:
            return {'status': 'error', 'message': 'JetStream context not available'}
        
        try:
            # Get account info to verify JetStream is working
            account_info = await self.get_jetstream_account_info()
            if not account_info:
                return {'status': 'error', 'message': 'Failed to get account info'}
            
            # Check stream health
            streams_info = await self.get_all_streams_info()
            healthy_streams = len([s for s in streams_info.values() if s])
            total_streams = len(self.stream_configs)
            
            status = 'healthy' if healthy_streams == total_streams else 'degraded'
            
            return {
                'status': status,
                'jetstream_account': account_info,
                'streams': {
                    'total': total_streams,
                    'healthy': healthy_streams,
                    'details': streams_info
                }
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}


# Global JetStream manager instance
jetstream_manager = JetStreamManager()