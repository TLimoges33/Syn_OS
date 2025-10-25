#!/usr/bin/env python3
"""
SynOS-NetAnalyzer: AI-Enhanced Network Traffic Analyzer
AI-powered Wireshark with consciousness integration and educational features
"""

import subprocess
import json
import threading
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import re

@dataclass
class PacketAnalysis:
    timestamp: float
    source_ip: str
    dest_ip: str
    protocol: str
    length: int
    info: str
    anomaly_score: float
    threat_level: str
    educational_note: str

@dataclass
class NetworkSession:
    session_id: str
    start_time: float
    packets: List[PacketAnalysis]
    total_bytes: int
    protocols_seen: List[str]
    consciousness_score: float
    security_events: List[Dict]

class SynOSNetAnalyzer:
    def __init__(self):
        self.consciousness_interface = "/proc/synos_consciousness"
        self.active_sessions = {}
        self.ai_patterns = {}
        self.threat_signatures = self._load_threat_signatures()
        self.educational_mode = True
        self.analysis_thread = None
        self.capturing = False

    def start_capture(self, interface: str = "eth0", duration: int = 60) -> NetworkSession:
        """Start AI-enhanced network capture and analysis"""
        print(f"📡 SynOS-NetAnalyzer: Starting capture on {interface}")

        session_id = f"session_{int(time.time())}"
        session = NetworkSession(
            session_id=session_id,
            start_time=time.time(),
            packets=[],
            total_bytes=0,
            protocols_seen=[],
            consciousness_score=0.5,
            security_events=[]
        )

        self.active_sessions[session_id] = session
        self._update_consciousness("capture_start", interface)

        # Start packet capture with AI analysis
        self.capturing = True
        self.analysis_thread = threading.Thread(
            target=self._capture_and_analyze,
            args=(interface, duration, session)
        )
        self.analysis_thread.start()

        return session

    def stop_capture(self, session_id: str) -> NetworkSession:
        """Stop capture and finalize analysis"""
        print(f"🛑 Stopping capture for session {session_id}")
        self.capturing = False

        if self.analysis_thread:
            self.analysis_thread.join(timeout=5)

        session = self.active_sessions.get(session_id)
        if session:
            session.consciousness_score = self._calculate_session_consciousness_score(session)
            self._update_consciousness("capture_complete", session_id, session.consciousness_score)

        return session

    def _capture_and_analyze(self, interface: str, duration: int, session: NetworkSession):
        """Capture packets and perform real-time AI analysis"""
        try:
            # Use tshark for packet capture (more reliable than scapy in containers)
            cmd = f"timeout {duration} tshark -i {interface} -T json"
            print(f"  🔍 Running capture command: {cmd}")

            process = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            packet_count = 0
            while self.capturing and packet_count < 1000:  # Limit for educational purposes
                line = process.stdout.readline()
                if not line:
                    break

                try:
                    packet_data = json.loads(line.strip())
                    analysis = self._analyze_packet(packet_data)
                    if analysis:
                        session.packets.append(analysis)
                        session.total_bytes += analysis.length

                        if analysis.protocol not in session.protocols_seen:
                            session.protocols_seen.append(analysis.protocol)

                        # Check for security events
                        if analysis.anomaly_score > 0.7:
                            security_event = {
                                'timestamp': analysis.timestamp,
                                'type': 'anomaly',
                                'description': f"High anomaly score for {analysis.protocol} traffic",
                                'severity': analysis.threat_level
                            }
                            session.security_events.append(security_event)

                        packet_count += 1

                        # Update consciousness periodically
                        if packet_count % 100 == 0:
                            self._update_consciousness("packet_analysis", f"Analyzed {packet_count} packets")

                except json.JSONDecodeError:
                    continue

            process.terminate()

        except Exception as e:
            print(f"  ⚠️ Capture error: {e}")

    def _analyze_packet(self, packet_data: Dict) -> Optional[PacketAnalysis]:
        """AI-enhanced packet analysis"""
        try:
            # Extract basic packet information
            layers = packet_data.get('_source', {}).get('layers', {})

            # Frame layer
            frame = layers.get('frame', {})
            timestamp = float(frame.get('frame.time_epoch', time.time()))
            length = int(frame.get('frame.len', 0))

            # IP layer
            ip_layer = layers.get('ip', {})
            source_ip = ip_layer.get('ip.src', 'unknown')
            dest_ip = ip_layer.get('ip.dst', 'unknown')
            protocol = ip_layer.get('ip.proto', 'unknown')

            # Protocol-specific analysis
            protocol_name = self._identify_protocol(layers)
            info = self._extract_packet_info(layers, protocol_name)

            # AI-based anomaly detection
            anomaly_score = self._calculate_anomaly_score(
                source_ip, dest_ip, protocol_name, length, layers
            )

            # Threat assessment
            threat_level = self._assess_threat_level(anomaly_score, protocol_name, layers)

            # Educational insights
            educational_note = self._generate_packet_education(protocol_name, layers, anomaly_score)

            return PacketAnalysis(
                timestamp=timestamp,
                source_ip=source_ip,
                dest_ip=dest_ip,
                protocol=protocol_name,
                length=length,
                info=info,
                anomaly_score=anomaly_score,
                threat_level=threat_level,
                educational_note=educational_note
            )

        except Exception as e:
            return None

    def _identify_protocol(self, layers: Dict) -> str:
        """Identify the highest-level protocol in the packet"""
        # Check for application layer protocols first
        if 'http' in layers:
            return 'HTTP'
        elif 'https' in layers or 'tls' in layers:
            return 'HTTPS/TLS'
        elif 'dns' in layers:
            return 'DNS'
        elif 'ssh' in layers:
            return 'SSH'
        elif 'ftp' in layers:
            return 'FTP'
        elif 'smtp' in layers:
            return 'SMTP'
        elif 'tcp' in layers:
            return 'TCP'
        elif 'udp' in layers:
            return 'UDP'
        elif 'icmp' in layers:
            return 'ICMP'
        else:
            return 'Unknown'

    def _extract_packet_info(self, layers: Dict, protocol: str) -> str:
        """Extract relevant information based on protocol"""
        if protocol == 'HTTP':
            http = layers.get('http', {})
            method = http.get('http.request.method', '')
            uri = http.get('http.request.uri', '')
            return f"{method} {uri}" if method else "HTTP Response"

        elif protocol == 'DNS':
            dns = layers.get('dns', {})
            query = dns.get('dns.qry.name', '')
            return f"DNS Query: {query}" if query else "DNS Response"

        elif protocol == 'TCP':
            tcp = layers.get('tcp', {})
            src_port = tcp.get('tcp.srcport', '')
            dst_port = tcp.get('tcp.dstport', '')
            flags = tcp.get('tcp.flags', '')
            return f"Port {src_port} → {dst_port} [Flags: {flags}]"

        elif protocol == 'UDP':
            udp = layers.get('udp', {})
            src_port = udp.get('udp.srcport', '')
            dst_port = udp.get('udp.dstport', '')
            return f"Port {src_port} → {dst_port}"

        else:
            return f"{protocol} packet"

    def _calculate_anomaly_score(self, src_ip: str, dst_ip: str, protocol: str, length: int, layers: Dict) -> float:
        """AI-based anomaly detection"""
        anomaly_score = 0.0

        # Size-based anomalies
        if length > 9000:  # Jumbo frames
            anomaly_score += 0.3
        elif length < 64:  # Too small
            anomaly_score += 0.2

        # Protocol-based anomalies
        if protocol in ['FTP', 'TELNET']:  # Insecure protocols
            anomaly_score += 0.4

        # Port-based anomalies
        if 'tcp' in layers:
            tcp = layers['tcp']
            dst_port = int(tcp.get('tcp.dstport', 0))
            if dst_port in [666, 1337, 31337]:  # Common backdoor ports
                anomaly_score += 0.6

        # IP-based anomalies
        if self._is_suspicious_ip(src_ip) or self._is_suspicious_ip(dst_ip):
            anomaly_score += 0.4

        # Pattern-based anomalies
        if protocol == 'DNS' and self._is_dns_tunneling(layers):
            anomaly_score += 0.7

        return min(1.0, anomaly_score)

    def _is_suspicious_ip(self, ip: str) -> bool:
        """Check if IP address is suspicious"""
        # Check for known malicious patterns
        suspicious_patterns = [
            r'0\.0\.0\.0',
            r'255\.255\.255\.255',
            r'127\.0\.0\.1',  # Unexpected localhost traffic
        ]

        for pattern in suspicious_patterns:
            if re.match(pattern, ip):
                return True

        return False

    def _is_dns_tunneling(self, layers: Dict) -> bool:
        """Detect potential DNS tunneling"""
        dns = layers.get('dns', {})
        query = dns.get('dns.qry.name', '').lower()

        # Check for suspicious DNS query patterns
        if len(query) > 100:  # Unusually long DNS query
            return True
        if re.search(r'[0-9a-f]{20,}', query):  # Hex-encoded data
            return True
        if query.count('.') > 10:  # Too many subdomains
            return True

        return False

    def _assess_threat_level(self, anomaly_score: float, protocol: str, layers: Dict) -> str:
        """Assess threat level based on analysis"""
        if anomaly_score > 0.8:
            return 'critical'
        elif anomaly_score > 0.6:
            return 'high'
        elif anomaly_score > 0.4:
            return 'medium'
        elif anomaly_score > 0.2:
            return 'low'
        else:
            return 'normal'

    def _generate_packet_education(self, protocol: str, layers: Dict, anomaly_score: float) -> str:
        """Generate educational insights about the packet"""
        if protocol == 'HTTP':
            return "🎓 HTTP traffic is unencrypted. Consider HTTPS for security."
        elif protocol == 'DNS':
            return "🎓 DNS queries reveal browsing patterns. Consider DNS over HTTPS (DoH)."
        elif protocol == 'ICMP':
            return "🎓 ICMP is used for network diagnostics but can be exploited for reconnaissance."
        elif anomaly_score > 0.6:
            return "🎓 High anomaly detected! This packet exhibits suspicious characteristics."
        elif protocol == 'SSH':
            return "🎓 SSH provides encrypted remote access. Monitor for brute force attempts."
        else:
            return f"🎓 {protocol} protocol analysis complete."

    def _calculate_session_consciousness_score(self, session: NetworkSession) -> float:
        """Calculate overall consciousness score for the session"""
        if not session.packets:
            return 0.5

        # Base score
        base_score = 0.7

        # Factor in anomalies
        anomaly_avg = sum(p.anomaly_score for p in session.packets) / len(session.packets)
        anomaly_penalty = anomaly_avg * 0.3

        # Factor in security events
        security_penalty = len(session.security_events) * 0.1

        # Factor in protocol diversity (good sign)
        protocol_bonus = min(len(session.protocols_seen) * 0.05, 0.2)

        consciousness_score = max(0.0, base_score - anomaly_penalty - security_penalty + protocol_bonus)
        return min(1.0, consciousness_score)

    def _load_threat_signatures(self) -> Dict:
        """Load threat detection signatures"""
        return {
            'port_scan': {
                'pattern': 'multiple_connections_short_time',
                'threshold': 10
            },
            'dns_tunneling': {
                'pattern': 'suspicious_dns_queries',
                'threshold': 5
            },
            'data_exfiltration': {
                'pattern': 'large_outbound_transfers',
                'threshold': 10485760  # 10MB
            }
        }

    def _update_consciousness(self, event: str, details: str, score: Optional[float] = None):
        """Update consciousness system with network analysis"""
        try:
            consciousness_data = {
                'component': 'synos_netanalyzer',
                'event': event,
                'details': details,
                'timestamp': time.time()
            }
            if score:
                consciousness_data['consciousness_score'] = score

            if Path(self.consciousness_interface).exists():
                with open(self.consciousness_interface, 'w') as f:
                    f.write(json.dumps(consciousness_data) + '\n')
        except Exception as e:
            print(f"  ⚠️ Consciousness update failed: {e}")

    def generate_session_report(self, session: NetworkSession) -> str:
        """Generate comprehensive session analysis report"""
        duration = time.time() - session.start_time if session.packets else 0

        # Traffic summary
        protocol_counts = {}
        for packet in session.packets:
            protocol_counts[packet.protocol] = protocol_counts.get(packet.protocol, 0) + 1

        # Threat summary
        threat_counts = {}
        for packet in session.packets:
            threat_counts[packet.threat_level] = threat_counts.get(packet.threat_level, 0) + 1

        report = f"""
📡 SynOS-NetAnalyzer Session Report
==================================
Session ID: {session.session_id}
Duration: {duration:.1f} seconds
Total Packets: {len(session.packets)}
Total Bytes: {session.total_bytes:,}
Consciousness Score: {session.consciousness_score:.2f}/1.0

📊 Protocol Distribution:
"""
        for protocol, count in sorted(protocol_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(session.packets)) * 100
            report += f"  {protocol}: {count} packets ({percentage:.1f}%)\n"

        report += f"\n🚨 Threat Level Distribution:\n"
        for level, count in sorted(threat_counts.items()):
            report += f"  {level.title()}: {count} packets\n"

        if session.security_events:
            report += f"\n⚠️ Security Events ({len(session.security_events)}):\n"
            for event in session.security_events[:5]:  # Show top 5
                report += f"  {event['type'].title()}: {event['description']}\n"

        # Educational insights
        report += f"\n🎓 Educational Insights:\n"
        if 'HTTP' in protocol_counts:
            report += f"  📈 {protocol_counts['HTTP']} unencrypted HTTP requests detected\n"
        if 'DNS' in protocol_counts:
            report += f"  🔍 {protocol_counts['DNS']} DNS queries monitored\n"
        if session.consciousness_score < 0.5:
            report += f"  🚨 Low consciousness score indicates potential security concerns\n"

        return report

def main():
    """Main network analyzer interface"""
    import argparse

    parser = argparse.ArgumentParser(description='SynOS-NetAnalyzer: AI-Enhanced Network Traffic Analyzer')
    parser.add_argument('--interface', default='eth0', help='Network interface to monitor')
    parser.add_argument('--duration', type=int, default=60, help='Capture duration in seconds')
    parser.add_argument('--output', help='Output file for analysis report')

    args = parser.parse_args()

    analyzer = SynOSNetAnalyzer()
    print(f"🧠 SynOS-NetAnalyzer v1.0.0 - AI-Enhanced Network Traffic Analyzer")
    print(f"🌐 Interface: {args.interface}")
    print(f"⏱️ Duration: {args.duration} seconds")
    print()

    try:
        # Start capture
        session = analyzer.start_capture(args.interface, args.duration)

        print(f"📡 Capturing traffic... (Press Ctrl+C to stop early)")
        time.sleep(args.duration)

        # Stop and analyze
        final_session = analyzer.stop_capture(session.session_id)
        report = analyzer.generate_session_report(final_session)

        print(report)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"📁 Report saved to: {args.output}")

    except KeyboardInterrupt:
        print("\n🛑 Capture interrupted by user")
        if 'session' in locals():
            final_session = analyzer.stop_capture(session.session_id)
            report = analyzer.generate_session_report(final_session)
            print(report)
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    main()