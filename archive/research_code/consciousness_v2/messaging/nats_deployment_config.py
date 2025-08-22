"""
NATS JetStream Configuration and Deployment
Priority 4: NATS Message Bus Enhancement

Production-ready NATS JetStream configuration with:
- High-availability clustering
- Performance optimization
- Monitoring and alerting
- Security configuration
- Auto-scaling configuration
"""

import yaml
import json
from typing import Dict, Any, List
from pathlib import Path


class NATSClusterConfig:
    """NATS cluster configuration generator"""
    
    def __init__(self):
        self.base_config = {
            'server_name': 'synaptic-nats',
            'port': 4222,
            'http_port': 8222,
            'monitor_port': 8222,
            'jetstream': {
                'enabled': True,
                'max_memory_store': '1GB',
                'max_file_store': '10GB',
                'store_dir': '/data/jetstream'
            },
            'cluster': {
                'name': 'synaptic-cluster',
                'port': 6222
            },
            'gateway': {
                'name': 'synaptic-gateway',
                'port': 7222
            }
        }
    
    def generate_server_config(self, node_id: int, cluster_nodes: List[str]) -> Dict[str, Any]:
        """Generate NATS server configuration"""
        
        config = {
            'server_name': f'synaptic-nats-{node_id}',
            'port': 4222,
            'http_port': 8222,
            
            # Logging configuration
            'logtime': True,
            'log_file': '/var/log/nats/nats-server.log',
            'log_size_limit': '100MB',
            'max_traced_msg_len': 32768,
            
            # Client connection limits
            'max_connections': 10000,
            'max_control_line': 4096,
            'max_payload': '8MB',
            'max_pending': '256MB',
            'write_deadline': '10s',
            
            # JetStream configuration
            'jetstream': {
                'max_memory_store': '2GB',
                'max_file_store': '50GB',
                'store_dir': '/data/jetstream',
                'sync_interval': '2m',
                'sync_always': False,
                'domain': 'synaptic'
            },
            
            # Cluster configuration
            'cluster': {
                'name': 'synaptic-cluster',
                'listen': f'0.0.0.0:6222',
                'routes': [f'nats://{node}:6222' for node in cluster_nodes if node != f'nats-{node_id}']
            },
            
            # Gateway configuration for multi-cluster
            'gateway': {
                'name': 'synaptic-gateway',
                'listen': '0.0.0.0:7222',
                'gateways': [
                    {
                        'name': 'primary',
                        'urls': [f'nats://{node}:7222' for node in cluster_nodes]
                    }
                ]
            },
            
            # Authentication
            'authorization': {
                'users': [
                    {
                        'user': 'consciousness',
                        'password': '$CONSCIOUSNESS_PASSWORD',
                        'permissions': {
                            'publish': ['consciousness.>', 'system.>'],
                            'subscribe': ['consciousness.>', 'system.>', 'security.>']
                        }
                    },
                    {
                        'user': 'security',
                        'password': '$SECURITY_PASSWORD', 
                        'permissions': {
                            'publish': ['security.>', 'system.>'],
                            'subscribe': ['security.>', 'consciousness.>', 'system.>']
                        }
                    },
                    {
                        'user': 'orchestrator',
                        'password': '$ORCHESTRATOR_PASSWORD',
                        'permissions': {
                            'publish': ['orchestrator.>', 'system.>'],
                            'subscribe': ['>', '_INBOX.>']  # Full access for orchestrator
                        }
                    }
                ]
            },
            
            # TLS configuration
            'tls': {
                'cert_file': '/certs/server-cert.pem',
                'key_file': '/certs/server-key.pem',
                'ca_file': '/certs/ca.pem',
                'verify': True,
                'timeout': 5
            },
            
            # Monitoring
            'system_account': 'SYS',
            'accounts': {
                'SYS': {
                    'users': [
                        {
                            'user': 'admin',
                            'password': '$ADMIN_PASSWORD'
                        }
                    ]
                }
            }
        }
        
        return config
    
    def generate_docker_compose(self, num_nodes: int = 3) -> Dict[str, Any]:
        """Generate Docker Compose for NATS cluster"""
        
        services = {}
        
        for i in range(num_nodes):
            services[f'nats-{i}'] = {
                'image': 'nats:2.10-alpine',
                'container_name': f'synaptic-nats-{i}',
                'hostname': f'nats-{i}',
                'ports': [
                    f'{4222 + i}:4222',  # Client port
                    f'{8222 + i}:8222',  # Monitoring port
                ],
                'volumes': [
                    f'./config/nats-{i}.conf:/etc/nats/nats-server.conf',
                    f'nats-jetstream-{i}:/data/jetstream',
                    './certs:/certs:ro',
                    f'nats-logs-{i}:/var/log/nats'
                ],
                'command': ['-c', '/etc/nats/nats-server.conf'],
                'environment': {
                    'CONSCIOUSNESS_PASSWORD': '${CONSCIOUSNESS_PASSWORD}',
                    'SECURITY_PASSWORD': '${SECURITY_PASSWORD}',
                    'ORCHESTRATOR_PASSWORD': '${ORCHESTRATOR_PASSWORD}',
                    'ADMIN_PASSWORD': '${ADMIN_PASSWORD}'
                },
                'networks': ['synaptic-network'],
                'restart': 'unless-stopped',
                'healthcheck': {
                    'test': ['CMD', 'wget', '--quiet', '--tries=1', '--spider', 'http://localhost:8222/healthz'],
                    'interval': '30s',
                    'timeout': '10s',
                    'retries': 3,
                    'start_period': '40s'
                },
                'logging': {
                    'driver': 'json-file',
                    'options': {
                        'max-size': '100m',
                        'max-file': '5'
                    }
                }
            }
        
        # Add NATS monitoring service
        services['nats-surveyor'] = {
            'image': 'natsio/nats-surveyor:latest',
            'container_name': 'synaptic-nats-surveyor',
            'ports': ['7777:7777'],
            'command': [
                '-s', 'nats://nats-0:4222,nats://nats-1:4222,nats://nats-2:4222',
                '-c', '5s',
                '--accounts'
            ],
            'networks': ['synaptic-network'],
            'restart': 'unless-stopped',
            'depends_on': [f'nats-{i}' for i in range(num_nodes)]
        }
        
        compose_config = {
            'version': '3.8',
            'services': services,
            'networks': {
                'synaptic-network': {
                    'external': True
                }
            },
            'volumes': {
                **{f'nats-jetstream-{i}': None for i in range(num_nodes)},
                **{f'nats-logs-{i}': None for i in range(num_nodes)}
            }
        }
        
        return compose_config
    
    def generate_kubernetes_manifests(self) -> List[Dict[str, Any]]:
        """Generate Kubernetes manifests for NATS cluster"""
        
        manifests = []
        
        # ConfigMap for NATS configuration
        configmap = {
            'apiVersion': 'v1',
            'kind': 'ConfigMap',
            'metadata': {
                'name': 'nats-config',
                'namespace': 'synaptic-os'
            },
            'data': {
                'nats.conf': '''
                server_name: $POD_NAME
                port: 4222
                http_port: 8222
                
                jetstream {
                    max_memory_store: 2GB
                    max_file_store: 50GB
                    store_dir: /data/jetstream
                }
                
                cluster {
                    name: synaptic-cluster
                    listen: 0.0.0.0:6222
                    routes = [
                        nats://nats-0.nats:6222
                        nats://nats-1.nats:6222
                        nats://nats-2.nats:6222
                    ]
                }
                '''
            }
        }
        manifests.append(configmap)
        
        # StatefulSet for NATS cluster
        statefulset = {
            'apiVersion': 'apps/v1',
            'kind': 'StatefulSet',
            'metadata': {
                'name': 'nats',
                'namespace': 'synaptic-os'
            },
            'spec': {
                'serviceName': 'nats',
                'replicas': 3,
                'selector': {
                    'matchLabels': {
                        'app': 'nats'
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': 'nats'
                        }
                    },
                    'spec': {
                        'containers': [
                            {
                                'name': 'nats',
                                'image': 'nats:2.10-alpine',
                                'ports': [
                                    {'containerPort': 4222, 'name': 'client'},
                                    {'containerPort': 6222, 'name': 'cluster'},
                                    {'containerPort': 8222, 'name': 'monitor'}
                                ],
                                'env': [
                                    {
                                        'name': 'POD_NAME',
                                        'valueFrom': {
                                            'fieldRef': {
                                                'fieldPath': 'metadata.name'
                                            }
                                        }
                                    }
                                ],
                                'volumeMounts': [
                                    {
                                        'name': 'config-volume',
                                        'mountPath': '/etc/nats'
                                    },
                                    {
                                        'name': 'jetstream-storage',
                                        'mountPath': '/data/jetstream'
                                    }
                                ],
                                'livenessProbe': {
                                    'httpGet': {
                                        'path': '/healthz',
                                        'port': 8222
                                    },
                                    'initialDelaySeconds': 10,
                                    'timeoutSeconds': 5
                                },
                                'readinessProbe': {
                                    'httpGet': {
                                        'path': '/healthz',
                                        'port': 8222
                                    },
                                    'initialDelaySeconds': 10,
                                    'timeoutSeconds': 5
                                },
                                'resources': {
                                    'requests': {
                                        'memory': '512Mi',
                                        'cpu': '200m'
                                    },
                                    'limits': {
                                        'memory': '4Gi',
                                        'cpu': '2000m'
                                    }
                                }
                            }
                        ],
                        'volumes': [
                            {
                                'name': 'config-volume',
                                'configMap': {
                                    'name': 'nats-config'
                                }
                            }
                        ]
                    }
                },
                'volumeClaimTemplates': [
                    {
                        'metadata': {
                            'name': 'jetstream-storage'
                        },
                        'spec': {
                            'accessModes': ['ReadWriteOnce'],
                            'resources': {
                                'requests': {
                                    'storage': '50Gi'
                                }
                            },
                            'storageClassName': 'fast-ssd'
                        }
                    }
                ]
            }
        }
        manifests.append(statefulset)
        
        # Service for NATS
        service = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': 'nats',
                'namespace': 'synaptic-os'
            },
            'spec': {
                'clusterIP': 'None',
                'selector': {
                    'app': 'nats'
                },
                'ports': [
                    {'name': 'client', 'port': 4222},
                    {'name': 'cluster', 'port': 6222},
                    {'name': 'monitor', 'port': 8222}
                ]
            }
        }
        manifests.append(service)
        
        return manifests


class NATSMonitoringConfig:
    """NATS monitoring and alerting configuration"""
    
    def generate_prometheus_config(self) -> Dict[str, Any]:
        """Generate Prometheus configuration for NATS monitoring"""
        
        return {
            'global': {
                'scrape_interval': '15s',
                'evaluation_interval': '15s'
            },
            'rule_files': [
                'nats-alerts.yml'
            ],
            'scrape_configs': [
                {
                    'job_name': 'nats-servers',
                    'static_configs': [
                        {
                            'targets': [
                                'nats-0:8222',
                                'nats-1:8222', 
                                'nats-2:8222'
                            ]
                        }
                    ],
                    'metrics_path': '/varz',
                    'scrape_interval': '10s'
                },
                {
                    'job_name': 'nats-jetstream',
                    'static_configs': [
                        {
                            'targets': [
                                'nats-0:8222',
                                'nats-1:8222',
                                'nats-2:8222'
                            ]
                        }
                    ],
                    'metrics_path': '/jsz',
                    'scrape_interval': '15s'
                },
                {
                    'job_name': 'nats-surveyor',
                    'static_configs': [
                        {
                            'targets': ['nats-surveyor:7777']
                        }
                    ],
                    'scrape_interval': '30s'
                }
            ],
            'alerting': {
                'alertmanagers': [
                    {
                        'static_configs': [
                            {
                                'targets': ['alertmanager:9093']
                            }
                        ]
                    }
                ]
            }
        }
    
    def generate_alert_rules(self) -> Dict[str, Any]:
        """Generate Prometheus alert rules for NATS"""
        
        return {
            'groups': [
                {
                    'name': 'nats-alerts',
                    'rules': [
                        {
                            'alert': 'NATSServerDown',
                            'expr': 'up{job="nats-servers"} == 0',
                            'for': '1m',
                            'labels': {
                                'severity': 'critical'
                            },
                            'annotations': {
                                'summary': 'NATS server is down',
                                'description': 'NATS server {{ $labels.instance }} has been down for more than 1 minute.'
                            }
                        },
                        {
                            'alert': 'NATSHighMemoryUsage',
                            'expr': 'nats_core_mem_bytes / (1024*1024*1024) > 1.5',
                            'for': '5m',
                            'labels': {
                                'severity': 'warning'
                            },
                            'annotations': {
                                'summary': 'NATS server high memory usage',
                                'description': 'NATS server {{ $labels.instance }} memory usage is above 1.5GB for more than 5 minutes.'
                            }
                        },
                        {
                            'alert': 'NATSJetStreamHighStorage',
                            'expr': 'nats_jetstream_stats_store_bytes / (1024*1024*1024) > 40',
                            'for': '2m',
                            'labels': {
                                'severity': 'warning'
                            },
                            'annotations': {
                                'summary': 'NATS JetStream high storage usage',
                                'description': 'NATS JetStream storage usage is above 40GB on {{ $labels.instance }}.'
                            }
                        },
                        {
                            'alert': 'NATSHighLatency',
                            'expr': 'nats_core_rtt_nanoseconds / 1000000 > 100',
                            'for': '3m',
                            'labels': {
                                'severity': 'warning'
                            },
                            'annotations': {
                                'summary': 'NATS high latency detected',
                                'description': 'NATS server {{ $labels.instance }} latency is above 100ms for more than 3 minutes.'
                            }
                        },
                        {
                            'alert': 'NATSClusterSplit',
                            'expr': 'nats_core_route_count < 2',
                            'for': '1m',
                            'labels': {
                                'severity': 'critical'
                            },
                            'annotations': {
                                'summary': 'NATS cluster split detected',
                                'description': 'NATS server {{ $labels.instance }} has fewer than 2 cluster routes.'
                            }
                        }
                    ]
                }
            ]
        }
    
    def generate_grafana_dashboard(self) -> Dict[str, Any]:
        """Generate Grafana dashboard for NATS monitoring"""
        
        return {
            'dashboard': {
                'id': None,
                'title': 'SynapticOS NATS Monitoring',
                'tags': ['nats', 'synaptic-os', 'messaging'],
                'timezone': 'browser',
                'panels': [
                    {
                        'id': 1,
                        'title': 'NATS Server Status',
                        'type': 'stat',
                        'targets': [
                            {
                                'expr': 'up{job="nats-servers"}',
                                'legendFormat': '{{ instance }}'
                            }
                        ],
                        'gridPos': {'h': 8, 'w': 12, 'x': 0, 'y': 0}
                    },
                    {
                        'id': 2,
                        'title': 'Messages per Second',
                        'type': 'graph',
                        'targets': [
                            {
                                'expr': 'rate(nats_core_in_msgs[1m])',
                                'legendFormat': 'Incoming - {{ instance }}'
                            },
                            {
                                'expr': 'rate(nats_core_out_msgs[1m])',
                                'legendFormat': 'Outgoing - {{ instance }}'
                            }
                        ],
                        'gridPos': {'h': 8, 'w': 12, 'x': 12, 'y': 0}
                    },
                    {
                        'id': 3,
                        'title': 'Memory Usage',
                        'type': 'graph',
                        'targets': [
                            {
                                'expr': 'nats_core_mem_bytes / (1024*1024)',
                                'legendFormat': 'Memory MB - {{ instance }}'
                            }
                        ],
                        'gridPos': {'h': 8, 'w': 12, 'x': 0, 'y': 8}
                    },
                    {
                        'id': 4,
                        'title': 'JetStream Storage',
                        'type': 'graph',
                        'targets': [
                            {
                                'expr': 'nats_jetstream_stats_store_bytes / (1024*1024*1024)',
                                'legendFormat': 'Storage GB - {{ instance }}'
                            }
                        ],
                        'gridPos': {'h': 8, 'w': 12, 'x': 12, 'y': 8}
                    },
                    {
                        'id': 5,
                        'title': 'Connection Count',
                        'type': 'graph',
                        'targets': [
                            {
                                'expr': 'nats_core_total_connections',
                                'legendFormat': 'Connections - {{ instance }}'
                            }
                        ],
                        'gridPos': {'h': 8, 'w': 12, 'x': 0, 'y': 16}
                    },
                    {
                        'id': 6,
                        'title': 'Cluster Routes',
                        'type': 'graph',
                        'targets': [
                            {
                                'expr': 'nats_core_route_count',
                                'legendFormat': 'Routes - {{ instance }}'
                            }
                        ],
                        'gridPos': {'h': 8, 'w': 12, 'x': 12, 'y': 16}
                    }
                ],
                'time': {
                    'from': 'now-1h',
                    'to': 'now'
                },
                'refresh': '10s'
            }
        }


def generate_nats_deployment():
    """Generate complete NATS deployment configuration"""
    
    config_gen = NATSClusterConfig()
    monitoring_gen = NATSMonitoringConfig()
    
    # Create output directory
    output_dir = Path('/home/diablorain/Syn_OS/deploy/nats')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate cluster nodes list
    cluster_nodes = ['nats-0', 'nats-1', 'nats-2']
    
    # Generate NATS server configurations
    for i, node in enumerate(cluster_nodes):
        server_config = config_gen.generate_server_config(i, cluster_nodes)
        config_file = output_dir / f'nats-{i}.conf'
        
        # Convert config to NATS format
        nats_config = convert_to_nats_format(server_config)
        with open(config_file, 'w') as f:
            f.write(nats_config)
    
    # Generate Docker Compose
    docker_compose = config_gen.generate_docker_compose()
    with open(output_dir / 'docker-compose.yml', 'w') as f:
        yaml.dump(docker_compose, f, default_flow_style=False)
    
    # Generate Kubernetes manifests
    k8s_manifests = config_gen.generate_kubernetes_manifests()
    with open(output_dir / 'kubernetes.yml', 'w') as f:
        for manifest in k8s_manifests:
            yaml.dump(manifest, f, default_flow_style=False)
            f.write('---\n')
    
    # Generate monitoring configurations
    prometheus_config = monitoring_gen.generate_prometheus_config()
    with open(output_dir / 'prometheus.yml', 'w') as f:
        yaml.dump(prometheus_config, f, default_flow_style=False)
    
    alert_rules = monitoring_gen.generate_alert_rules()
    with open(output_dir / 'nats-alerts.yml', 'w') as f:
        yaml.dump(alert_rules, f, default_flow_style=False)
    
    grafana_dashboard = monitoring_gen.generate_grafana_dashboard()
    with open(output_dir / 'grafana-dashboard.json', 'w') as f:
        json.dump(grafana_dashboard, f, indent=2)
    
    # Generate environment file template
    env_template = '''# NATS Authentication
CONSCIOUSNESS_PASSWORD=change_me_consciousness_secure_password
SECURITY_PASSWORD=change_me_security_secure_password
ORCHESTRATOR_PASSWORD=change_me_orchestrator_secure_password
ADMIN_PASSWORD=change_me_admin_secure_password

# TLS Configuration
TLS_ENABLED=true
CERT_PATH=/certs
'''
    
    with open(output_dir / '.env.template', 'w') as f:
        f.write(env_template)
    
    print(f"NATS deployment configuration generated in: {output_dir}")
    return output_dir


def convert_to_nats_format(config: Dict[str, Any]) -> str:
    """Convert Python dict config to NATS server format"""
    
    def format_value(value):
        if isinstance(value, str):
            if value.startswith('$'):
                return value  # Environment variable
            return f'"{value}"'
        elif isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, list):
            items = [format_value(item) for item in value]
            return '[' + ', '.join(items) + ']'
        elif isinstance(value, dict):
            return format_dict(value)
        return str(value)
    
    def format_dict(d, indent=0):
        lines = []
        indent_str = '  ' * indent
        
        for key, value in d.items():
            if isinstance(value, dict):
                lines.append(f'{indent_str}{key} {{')
                lines.append(format_dict(value, indent + 1))
                lines.append(f'{indent_str}}}')
            else:
                lines.append(f'{indent_str}{key}: {format_value(value)}')
        
        return '\n'.join(lines)
    
    return format_dict(config)


if __name__ == "__main__":
    generate_nats_deployment()
