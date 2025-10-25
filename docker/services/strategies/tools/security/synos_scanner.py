#!/usr/bin/env python3
"""
SynOS-Scanner: AI-Enhanced Network Scanner
Enhanced Nmap with consciousness integration and educational features
"""

import subprocess
import json
import threading
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ScanResult:
    target: str
    timestamp: float
    ports: List[Dict]
    services: List[Dict]
    vulnerabilities: List[Dict]
    consciousness_score: float
    educational_notes: List[str]

class SynOSScanner:
    def __init__(self):
        self.consciousness_interface = "/proc/synos_consciousness"
        self.results_cache = {}
        self.learning_patterns = []
        self.educational_mode = True

    def scan_network(self, target: str, scan_type: str = "comprehensive") -> ScanResult:
        """AI-enhanced network scanning with consciousness integration"""
        print(f"🔍 SynOS-Scanner: Starting {scan_type} scan of {target}")

        # Update consciousness system about scan activity
        self._update_consciousness("network_scan_start", target)

        start_time = time.time()

        # Perform enhanced nmap scan with AI optimization
        scan_commands = self._generate_scan_commands(target, scan_type)
        raw_results = {}

        for cmd_name, cmd in scan_commands.items():
            print(f"  📡 Running {cmd_name} scan...")
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
                raw_results[cmd_name] = {
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }
            except subprocess.TimeoutExpired:
                raw_results[cmd_name] = {'error': 'timeout', 'stdout': '', 'stderr': ''}

        # AI-enhanced result processing
        processed_results = self._process_scan_results(raw_results, target)

        # Calculate consciousness-informed risk assessment
        consciousness_score = self._calculate_consciousness_score(processed_results)

        # Generate educational insights
        educational_notes = self._generate_educational_notes(processed_results, target)

        scan_result = ScanResult(
            target=target,
            timestamp=start_time,
            ports=processed_results.get('ports', []),
            services=processed_results.get('services', []),
            vulnerabilities=processed_results.get('vulnerabilities', []),
            consciousness_score=consciousness_score,
            educational_notes=educational_notes
        )

        # Cache results and update learning patterns
        self.results_cache[target] = scan_result
        self._update_learning_patterns(scan_result)

        # Update consciousness with scan completion
        self._update_consciousness("network_scan_complete", target, consciousness_score)

        print(f"✅ Scan complete! Consciousness score: {consciousness_score:.2f}")
        return scan_result

    def _generate_scan_commands(self, target: str, scan_type: str) -> Dict[str, str]:
        """Generate AI-optimized scan commands based on target and type"""
        base_nmap = "nmap -sS -O -sV --script=vuln"

        commands = {
            "port_discovery": f"{base_nmap} -p- {target}",
            "service_detection": f"{base_nmap} -sC -sV {target}",
            "vulnerability_scan": f"{base_nmap} --script=vuln,exploit {target}",
        }

        if scan_type == "comprehensive":
            commands.update({
                "udp_scan": f"nmap -sU --top-ports 1000 {target}",
                "aggressive_scan": f"nmap -A -T4 {target}",
                "script_scan": f"nmap --script=default,discovery,safe {target}"
            })

        return commands

    def _process_scan_results(self, raw_results: Dict, target: str) -> Dict:
        """AI-enhanced processing of scan results"""
        processed = {
            'ports': [],
            'services': [],
            'vulnerabilities': []
        }

        # Process port discovery
        for scan_type, result in raw_results.items():
            if result.get('stdout'):
                lines = result['stdout'].split('\n')
                for line in lines:
                    if '/tcp' in line or '/udp' in line:
                        port_info = self._parse_port_line(line)
                        if port_info:
                            processed['ports'].append(port_info)

                    elif 'VULNERABLE' in line.upper():
                        vuln_info = self._parse_vulnerability_line(line)
                        if vuln_info:
                            processed['vulnerabilities'].append(vuln_info)

        return processed

    def _parse_port_line(self, line: str) -> Optional[Dict]:
        """Parse nmap port information line"""
        try:
            parts = line.strip().split()
            if len(parts) >= 3:
                port_proto = parts[0]
                state = parts[1]
                service = parts[2] if len(parts) > 2 else "unknown"

                port_num = port_proto.split('/')[0]
                protocol = port_proto.split('/')[1] if '/' in port_proto else 'tcp'

                return {
                    'port': int(port_num),
                    'protocol': protocol,
                    'state': state,
                    'service': service,
                    'risk_level': self._assess_port_risk(int(port_num), service, state)
                }
        except (ValueError, IndexError):
            pass
        return None

    def _parse_vulnerability_line(self, line: str) -> Optional[Dict]:
        """Parse vulnerability information from scan output"""
        if 'CVE-' in line:
            return {
                'type': 'CVE',
                'description': line.strip(),
                'severity': 'high' if 'CRITICAL' in line.upper() else 'medium'
            }
        return None

    def _assess_port_risk(self, port: int, service: str, state: str) -> str:
        """AI-based risk assessment for discovered ports"""
        high_risk_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 445, 993, 995, 1433, 3389]
        medium_risk_ports = [20, 69, 161, 162, 389, 636, 989, 990]

        if state != 'open':
            return 'low'
        elif port in high_risk_ports:
            return 'high'
        elif port in medium_risk_ports:
            return 'medium'
        elif port < 1024:
            return 'medium'
        else:
            return 'low'

    def _calculate_consciousness_score(self, results: Dict) -> float:
        """Calculate consciousness-informed security score"""
        base_score = 0.5

        # Factor in open ports
        open_ports = len([p for p in results.get('ports', []) if p.get('state') == 'open'])
        port_penalty = min(open_ports * 0.02, 0.3)

        # Factor in vulnerabilities
        vuln_penalty = len(results.get('vulnerabilities', [])) * 0.1

        # Factor in high-risk services
        high_risk_services = ['ftp', 'telnet', 'ssh', 'http', 'https', 'smb']
        risk_penalty = 0
        for port in results.get('ports', []):
            if port.get('service', '').lower() in high_risk_services:
                risk_penalty += 0.05

        consciousness_score = max(0.0, base_score - port_penalty - vuln_penalty - risk_penalty)
        return min(1.0, consciousness_score)

    def _generate_educational_notes(self, results: Dict, target: str) -> List[str]:
        """Generate educational insights about scan results"""
        notes = []

        open_ports = [p for p in results.get('ports', []) if p.get('state') == 'open']

        if len(open_ports) > 10:
            notes.append(f"🎓 High port exposure detected ({len(open_ports)} open ports). Consider firewall hardening.")

        for port in open_ports:
            if port.get('port') == 22:
                notes.append("🎓 SSH service detected. Ensure key-based authentication and disable root login.")
            elif port.get('port') == 21:
                notes.append("🎓 FTP service detected. Consider SFTP/FTPS for secure file transfer.")
            elif port.get('port') in [80, 443]:
                notes.append("🎓 Web services detected. Ensure SSL/TLS configuration and security headers.")

        vuln_count = len(results.get('vulnerabilities', []))
        if vuln_count > 0:
            notes.append(f"🎓 {vuln_count} potential vulnerabilities found. Prioritize patching critical issues.")

        return notes

    def _update_consciousness(self, event: str, target: str, score: Optional[float] = None):
        """Update consciousness system with scan activity"""
        try:
            consciousness_data = {
                'component': 'synos_scanner',
                'event': event,
                'target': target,
                'timestamp': time.time()
            }
            if score:
                consciousness_data['consciousness_score'] = score

            # Try to write to consciousness interface
            if Path(self.consciousness_interface).exists():
                with open(self.consciousness_interface, 'w') as f:
                    f.write(json.dumps(consciousness_data) + '\n')
        except Exception as e:
            print(f"  ⚠️ Consciousness update failed: {e}")

    def _update_learning_patterns(self, scan_result: ScanResult):
        """Update AI learning patterns based on scan results"""
        pattern = {
            'target_type': self._classify_target(scan_result.target),
            'port_count': len(scan_result.ports),
            'service_types': [p.get('service', 'unknown') for p in scan_result.ports],
            'risk_level': 'high' if scan_result.consciousness_score < 0.3 else 'medium' if scan_result.consciousness_score < 0.7 else 'low'
        }

        self.learning_patterns.append(pattern)

        # Keep only recent patterns for AI learning
        if len(self.learning_patterns) > 100:
            self.learning_patterns = self.learning_patterns[-100:]

    def _classify_target(self, target: str) -> str:
        """Classify target type for AI learning"""
        if any(word in target.lower() for word in ['192.168', '10.', '172.']):
            return 'internal'
        elif any(word in target.lower() for word in ['localhost', '127.0.0.1']):
            return 'local'
        else:
            return 'external'

    def generate_report(self, scan_result: ScanResult) -> str:
        """Generate comprehensive scan report"""
        report = f"""
🔍 SynOS-Scanner Report
======================
Target: {scan_result.target}
Scan Time: {time.ctime(scan_result.timestamp)}
Consciousness Score: {scan_result.consciousness_score:.2f}/1.0

📊 Summary:
- Open Ports: {len([p for p in scan_result.ports if p.get('state') == 'open'])}
- Services Detected: {len(scan_result.services)}
- Vulnerabilities: {len(scan_result.vulnerabilities)}

🔓 Open Ports:
"""

        for port in scan_result.ports:
            if port.get('state') == 'open':
                risk_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(port.get('risk_level', 'low'), '⚪')
                report += f"  {risk_emoji} {port['port']}/{port['protocol']} - {port.get('service', 'unknown')} ({port.get('risk_level', 'unknown')} risk)\n"

        if scan_result.vulnerabilities:
            report += "\n🚨 Vulnerabilities:\n"
            for vuln in scan_result.vulnerabilities:
                report += f"  ⚠️ {vuln.get('description', 'Unknown vulnerability')}\n"

        if scan_result.educational_notes:
            report += "\n🎓 Educational Insights:\n"
            for note in scan_result.educational_notes:
                report += f"  {note}\n"

        return report

def main():
    """Main scanner interface"""
    import argparse

    parser = argparse.ArgumentParser(description='SynOS-Scanner: AI-Enhanced Network Scanner')
    parser.add_argument('target', help='Target IP address or hostname')
    parser.add_argument('--type', choices=['quick', 'comprehensive'], default='comprehensive', help='Scan type')
    parser.add_argument('--output', help='Output file for results')

    args = parser.parse_args()

    scanner = SynOSScanner()
    print(f"🧠 SynOS-Scanner v1.0.0 - AI-Enhanced Network Security Scanner")
    print(f"🎯 Target: {args.target}")
    print(f"📊 Scan Type: {args.type}")
    print()

    try:
        result = scanner.scan_network(args.target, args.type)
        report = scanner.generate_report(result)

        print(report)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"📁 Report saved to: {args.output}")

    except KeyboardInterrupt:
        print("\n🛑 Scan interrupted by user")
    except Exception as e:
        print(f"❌ Scan failed: {e}")

if __name__ == "__main__":
    main()