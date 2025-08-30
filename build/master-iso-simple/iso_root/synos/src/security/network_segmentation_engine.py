#!/usr/bin/env python3
"""
Network Segmentation Engine for SynapticOS Zero Trust Implementation
Provides micro-segmentation and network zone enforcement
"""

import asyncio
import logging
import json
import subprocess
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from ipaddress import IPv4Network, IPv6Network, ip_network, ip_address
import iptables
import netfilterqueue
from datetime import datetime

class NetworkZone(Enum):
    """Network zones for micro-segmentation"""
    CONSCIOUSNESS = "consciousness"      # AI consciousness modules
    PRIVILEGED = "privileged"           # High-privilege services
    INTERNAL = "internal"               # Internal services
    DMZ = "dmz"                        # Demilitarized zone
    EXTERNAL = "external"              # External access
    QUARANTINE = "quarantine"          # Isolated/suspicious entities
    MANAGEMENT = "management"          # Management interfaces

class TrafficAction(Enum):
    """Actions for network traffic"""
    ALLOW = "allow"
    DENY = "deny"
    LOG = "log"
    QUARANTINE = "quarantine"
    INSPECT = "inspect"

class ConnectionState(Enum):
    """Connection state tracking"""
    NEW = "new"
    ESTABLISHED = "established"
    RELATED = "related"
    INVALID = "invalid"

@dataclass
class NetworkRule:
    """Network segmentation rule"""
    rule_id: str
    name: str
    source_zone: NetworkZone
    destination_zone: NetworkZone
    protocol: str  # tcp, udp, icmp, any
    source_ports: List[int]
    destination_ports: List[int]
    action: TrafficAction
    priority: int
    conditions: Dict[str, Any]
    enabled: bool = True
    created_at: str = ""
    last_matched: str = ""
    match_count: int = 0

@dataclass
class NetworkInterface:
    """Network interface configuration"""
    interface_id: str
    name: str
    zone: NetworkZone
    ip_networks: List[str]
    vlan_id: Optional[int]
    mtu: int
    enabled: bool = True

@dataclass
class TrafficFlow:
    """Network traffic flow"""
    flow_id: str
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: str
    source_zone: NetworkZone
    destination_zone: NetworkZone
    state: ConnectionState
    bytes_transferred: int
    packets_transferred: int
    start_time: str
    last_seen: str
    risk_score: float

class NetworkSegmentationEngine:
    """Manages network micro-segmentation for Zero Trust"""
    
    def __init__(self, config_path: str = "config/security/network_segmentation.yaml"):
        """Initialize Network Segmentation Engine"""
        self.logger = logging.getLogger("security.zero_trust.network")
        self.config_path = config_path
        
        # Network configuration
        self.zone_networks: Dict[NetworkZone, List[str]] = {}
        self.interfaces: Dict[str, NetworkInterface] = {}
        self.rules: Dict[str, NetworkRule] = {}
        self.active_flows: Dict[str, TrafficFlow] = {}
        
        # Default zone networks
        self._initialize_default_zones()
        
        # Monitoring
        self.traffic_stats = {
            "packets_processed": 0,
            "packets_allowed": 0,
            "packets_denied": 0,
            "packets_logged": 0,
            "last_update": datetime.utcnow().isoformat()
        }

    def _initialize_default_zones(self):
        """Initialize default network zones"""
        self.zone_networks = {
            NetworkZone.CONSCIOUSNESS: ["10.10.1.0/24"],      # AI modules
            NetworkZone.PRIVILEGED: ["10.10.2.0/24"],        # High-privilege
            NetworkZone.INTERNAL: ["10.10.3.0/24"],          # Internal services
            NetworkZone.DMZ: ["10.10.4.0/24"],               # DMZ
            NetworkZone.EXTERNAL: ["0.0.0.0/0"],             # External
            NetworkZone.QUARANTINE: ["10.10.5.0/24"],        # Quarantine
            NetworkZone.MANAGEMENT: ["10.10.10.0/24"]        # Management
        }

    async def initialize(self) -> bool:
        """Initialize the network segmentation engine"""
        try:
            self.logger.info("Initializing Network Segmentation Engine...")
            
            # Load configuration
            await self._load_configuration()
            
            # Initialize default rules
            await self._create_default_rules()
            
            # Setup network interfaces
            await self._setup_network_interfaces()
            
            # Configure iptables rules
            await self._configure_firewall_rules()
            
            # Start traffic monitoring
            asyncio.create_task(self._start_traffic_monitoring())
            
            self.logger.info("Network Segmentation Engine initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Network segmentation initialization failed: {e}")
            return False

    async def _create_default_rules(self):
        """Create default segmentation rules"""
        default_rules = [
            # Consciousness zone rules
            NetworkRule(
                rule_id="consciousness_internal",
                name="Consciousness to Internal Services",
                source_zone=NetworkZone.CONSCIOUSNESS,
                destination_zone=NetworkZone.INTERNAL,
                protocol="tcp",
                source_ports=[],
                destination_ports=[80, 443, 5432, 6379],  # HTTP, HTTPS, PostgreSQL, Redis
                action=TrafficAction.ALLOW,
                priority=100,
                conditions={"require_mtls": True}
            ),
            
            # Management access rules
            NetworkRule(
                rule_id="management_all",
                name="Management Zone Access",
                source_zone=NetworkZone.MANAGEMENT,
                destination_zone=NetworkZone.INTERNAL,
                protocol="tcp",
                source_ports=[],
                destination_ports=[22, 80, 443],  # SSH, HTTP, HTTPS
                action=TrafficAction.ALLOW,
                priority=50,
                conditions={"require_auth": True}
            ),
            
            # DMZ rules
            NetworkRule(
                rule_id="external_dmz",
                name="External to DMZ",
                source_zone=NetworkZone.EXTERNAL,
                destination_zone=NetworkZone.DMZ,
                protocol="tcp",
                source_ports=[],
                destination_ports=[80, 443],  # HTTP, HTTPS only
                action=TrafficAction.ALLOW,
                priority=75,
                conditions={"rate_limit": 1000}
            ),
            
            # Default deny rules
            NetworkRule(
                rule_id="external_internal_deny",
                name="External to Internal Deny",
                source_zone=NetworkZone.EXTERNAL,
                destination_zone=NetworkZone.INTERNAL,
                protocol="any",
                source_ports=[],
                destination_ports=[],
                action=TrafficAction.DENY,
                priority=1000,
                conditions={}
            ),
            
            # Quarantine isolation
            NetworkRule(
                rule_id="quarantine_isolation",
                name="Quarantine Isolation",
                source_zone=NetworkZone.QUARANTINE,
                destination_zone=NetworkZone.INTERNAL,
                protocol="any",
                source_ports=[],
                destination_ports=[],
                action=TrafficAction.DENY,
                priority=10,
                conditions={}
            ),
            
            # Internal communication
            NetworkRule(
                rule_id="internal_communication",
                name="Internal Service Communication",
                source_zone=NetworkZone.INTERNAL,
                destination_zone=NetworkZone.INTERNAL,
                protocol="tcp",
                source_ports=[],
                destination_ports=[80, 443, 5432, 6379, 4222],  # Include NATS
                action=TrafficAction.ALLOW,
                priority=200,
                conditions={"require_mtls": True}
            )
        ]
        
        for rule in default_rules:
            rule.created_at = datetime.utcnow().isoformat()
            self.rules[rule.rule_id] = rule

    async def add_segmentation_rule(self, rule: NetworkRule) -> bool:
        """Add a new network segmentation rule"""
        try:
            rule.created_at = datetime.utcnow().isoformat()
            self.rules[rule.rule_id] = rule
            
            # Apply rule to firewall
            await self._apply_firewall_rule(rule)
            
            self.logger.info(f"Added segmentation rule: {rule.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add segmentation rule: {e}")
            return False

    async def _apply_firewall_rule(self, rule: NetworkRule):
        """Apply a rule to the firewall (iptables)"""
        try:
            # Convert rule to iptables command
            iptables_cmd = await self._rule_to_iptables(rule)
            
            # Execute iptables command
            process = await asyncio.create_subprocess_shell(
                iptables_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"iptables command failed: {stderr.decode()}")
            else:
                self.logger.debug(f"Applied iptables rule: {iptables_cmd}")
                
        except Exception as e:
            self.logger.error(f"Failed to apply firewall rule: {e}")

    async def _rule_to_iptables(self, rule: NetworkRule) -> str:
        """Convert a segmentation rule to iptables command"""
        # Get source and destination networks
        source_networks = self.zone_networks.get(rule.source_zone, [])
        dest_networks = self.zone_networks.get(rule.destination_zone, [])
        
        cmd_parts = ["iptables", "-A", "FORWARD"]
        
        # Source network
        if source_networks and source_networks[0] != "0.0.0.0/0":
            cmd_parts.extend(["-s", source_networks[0]])
        
        # Destination network
        if dest_networks and dest_networks[0] != "0.0.0.0/0":
            cmd_parts.extend(["-d", dest_networks[0]])
        
        # Protocol
        if rule.protocol != "any":
            cmd_parts.extend(["-p", rule.protocol])
        
        # Destination ports
        if rule.destination_ports:
            if rule.protocol in ["tcp", "udp"]:
                ports = ",".join(map(str, rule.destination_ports))
                cmd_parts.extend(["--dport", ports])
        
        # Action
        if rule.action == TrafficAction.ALLOW:
            cmd_parts.extend(["-j", "ACCEPT"])
        elif rule.action == TrafficAction.DENY:
            cmd_parts.extend(["-j", "DROP"])
        elif rule.action == TrafficAction.LOG:
            cmd_parts.extend(["-j", "LOG", "--log-prefix", f"[{rule.rule_id}] "])
        
        # Add comment
        cmd_parts.extend(["-m", "comment", "--comment", f"{rule.name}"])
        
        return " ".join(cmd_parts)

    async def _configure_firewall_rules(self):
        """Configure base firewall rules"""
        try:
            # Clear existing rules
            await self._execute_command("iptables -F FORWARD")
            await self._execute_command("iptables -F INPUT")
            await self._execute_command("iptables -F OUTPUT")
            
            # Set default policies
            await self._execute_command("iptables -P FORWARD DROP")
            await self._execute_command("iptables -P INPUT DROP")
            await self._execute_command("iptables -P OUTPUT ACCEPT")
            
            # Allow loopback
            await self._execute_command("iptables -A INPUT -i lo -j ACCEPT")
            await self._execute_command("iptables -A OUTPUT -o lo -j ACCEPT")
            
            # Allow established connections
            await self._execute_command("iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT")
            await self._execute_command("iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT")
            
            # Apply all segmentation rules
            for rule in self.rules.values():
                if rule.enabled:
                    await self._apply_firewall_rule(rule)
            
            self.logger.info("Firewall rules configured successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to configure firewall rules: {e}")

    async def _execute_command(self, command: str):
        """Execute a shell command"""
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            self.logger.warning(f"Command failed: {command} - {stderr.decode()}")
        
        return stdout.decode(), stderr.decode(), process.returncode

    def get_zone_for_ip(self, ip_address: str) -> NetworkZone:
        """Get the network zone for an IP address"""
        try:
            ip = ip_network(ip_address, strict=False)
            
            for zone, networks in self.zone_networks.items():
                for network_str in networks:
                    network = ip_network(network_str, strict=False)
                    if ip.subnet_of(network) or ip == network:
                        return zone
            
            return NetworkZone.EXTERNAL
            
        except Exception:
            return NetworkZone.EXTERNAL

    async def evaluate_traffic(self, source_ip: str, dest_ip: str, 
                             dest_port: int, protocol: str) -> Tuple[TrafficAction, str]:
        """Evaluate traffic against segmentation rules"""
        try:
            source_zone = self.get_zone_for_ip(source_ip)
            dest_zone = self.get_zone_for_ip(dest_ip)
            
            # Find matching rules (sorted by priority)
            matching_rules = []
            for rule in self.rules.values():
                if not rule.enabled:
                    continue
                
                # Check zone matching
                if (rule.source_zone != source_zone and 
                    rule.source_zone != NetworkZone.EXTERNAL):
                    continue
                
                if (rule.destination_zone != dest_zone and 
                    rule.destination_zone != NetworkZone.EXTERNAL):
                    continue
                
                # Check protocol
                if rule.protocol != "any" and rule.protocol != protocol:
                    continue
                
                # Check destination port
                if rule.destination_ports and dest_port not in rule.destination_ports:
                    continue
                
                matching_rules.append(rule)
            
            # Sort by priority (lower number = higher priority)
            matching_rules.sort(key=lambda r: r.priority)
            
            if matching_rules:
                rule = matching_rules[0]
                rule.match_count += 1
                rule.last_matched = datetime.utcnow().isoformat()
                
                self.logger.debug(f"Traffic {source_ip}:{dest_port} -> {dest_ip}:{dest_port} "
                                f"matched rule {rule.name}: {rule.action}")
                
                return rule.action, rule.rule_id
            
            # Default deny
            self.logger.warning(f"No rule matched for {source_ip} -> {dest_ip}:{dest_port}, denying")
            return TrafficAction.DENY, "default_deny"
            
        except Exception as e:
            self.logger.error(f"Traffic evaluation failed: {e}")
            return TrafficAction.DENY, "error"

    async def _start_traffic_monitoring(self):
        """Start monitoring network traffic"""
        self.logger.info("Starting traffic monitoring...")
        
        # This would integrate with netfilterqueue for real packet inspection
        # For now, we'll simulate monitoring
        while True:
            try:
                await asyncio.sleep(10)  # Monitor every 10 seconds
                await self._update_traffic_stats()
                
            except Exception as e:
                self.logger.error(f"Traffic monitoring error: {e}")
                await asyncio.sleep(30)

    async def _update_traffic_stats(self):
        """Update traffic statistics"""
        self.traffic_stats["last_update"] = datetime.utcnow().isoformat()
        
        # Clean up old flows
        current_time = datetime.utcnow()
        old_flows = []
        
        for flow_id, flow in self.active_flows.items():
            last_seen = datetime.fromisoformat(flow.last_seen)
            if (current_time - last_seen).seconds > 300:  # 5 minutes timeout
                old_flows.append(flow_id)
        
        for flow_id in old_flows:
            del self.active_flows[flow_id]

    async def quarantine_ip(self, ip_address: str, reason: str) -> bool:
        """Move an IP address to quarantine zone"""
        try:
            # Add IP to quarantine zone
            quarantine_networks = self.zone_networks.get(NetworkZone.QUARANTINE, [])
            if ip_address not in quarantine_networks:
                quarantine_networks.append(f"{ip_address}/32")
                self.zone_networks[NetworkZone.QUARANTINE] = quarantine_networks
            
            # Add deny rule for this IP
            quarantine_rule = NetworkRule(
                rule_id=f"quarantine_{ip_address.replace('.', '_')}",
                name=f"Quarantine {ip_address}",
                source_zone=NetworkZone.QUARANTINE,
                destination_zone=NetworkZone.INTERNAL,
                protocol="any",
                source_ports=[],
                destination_ports=[],
                action=TrafficAction.DENY,
                priority=5,
                conditions={"reason": reason}
            )
            
            await self.add_segmentation_rule(quarantine_rule)
            
            self.logger.warning(f"IP {ip_address} quarantined: {reason}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to quarantine IP {ip_address}: {e}")
            return False

    async def remove_from_quarantine(self, ip_address: str) -> bool:
        """Remove an IP address from quarantine"""
        try:
            # Remove from quarantine zone
            quarantine_networks = self.zone_networks.get(NetworkZone.QUARANTINE, [])
            ip_cidr = f"{ip_address}/32"
            if ip_cidr in quarantine_networks:
                quarantine_networks.remove(ip_cidr)
                self.zone_networks[NetworkZone.QUARANTINE] = quarantine_networks
            
            # Remove quarantine rule
            rule_id = f"quarantine_{ip_address.replace('.', '_')}"
            if rule_id in self.rules:
                del self.rules[rule_id]
                
                # Remove from iptables
                await self._execute_command(f"iptables -D FORWARD -s {ip_address} -j DROP")
            
            self.logger.info(f"IP {ip_address} removed from quarantine")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove {ip_address} from quarantine: {e}")
            return False

    async def get_segmentation_status(self) -> Dict[str, Any]:
        """Get current segmentation status"""
        return {
            "zones": {zone.value: networks for zone, networks in self.zone_networks.items()},
            "rules": {rule_id: asdict(rule) for rule_id, rule in self.rules.items()},
            "active_flows": len(self.active_flows),
            "traffic_stats": self.traffic_stats,
            "interfaces": {iface_id: asdict(iface) for iface_id, iface in self.interfaces.items()}
        }

    async def _setup_network_interfaces(self):
        """Setup network interfaces for each zone"""
        try:
            # This would configure actual network interfaces
            # For now, we'll create logical interface mappings
            
            default_interfaces = [
                NetworkInterface(
                    interface_id="consciousness_if",
                    name="br-consciousness",
                    zone=NetworkZone.CONSCIOUSNESS,
                    ip_networks=self.zone_networks[NetworkZone.CONSCIOUSNESS],
                    vlan_id=101,
                    mtu=1500
                ),
                NetworkInterface(
                    interface_id="internal_if",
                    name="br-internal",
                    zone=NetworkZone.INTERNAL,
                    ip_networks=self.zone_networks[NetworkZone.INTERNAL],
                    vlan_id=103,
                    mtu=1500
                ),
                NetworkInterface(
                    interface_id="dmz_if",
                    name="br-dmz",
                    zone=NetworkZone.DMZ,
                    ip_networks=self.zone_networks[NetworkZone.DMZ],
                    vlan_id=104,
                    mtu=1500
                )
            ]
            
            for interface in default_interfaces:
                self.interfaces[interface.interface_id] = interface
            
            self.logger.info("Network interfaces configured")
            
        except Exception as e:
            self.logger.error(f"Failed to setup network interfaces: {e}")

    async def _load_configuration(self):
        """Load configuration from file"""
        try:
            # Load from YAML configuration file if it exists
            # For now, use defaults
            self.logger.info("Using default network segmentation configuration")
            
        except Exception as e:
            self.logger.warning(f"Failed to load configuration: {e}")

    def get_traffic_flows(self) -> Dict[str, Dict[str, Any]]:
        """Get current active traffic flows"""
        return {flow_id: asdict(flow) for flow_id, flow in self.active_flows.items()}
