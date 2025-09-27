#!/usr/bin/env python3
"""
SynOS Container Security Scanner
Comprehensive security scanning for container images and deployments
"""

import subprocess
import json
import logging
from typing import Dict, List
from pathlib import Path

class SecurityScanner:
    def __init__(self):
        self.logger = logging.getLogger("synos.security.scanner")
        
    def scan_image_vulnerabilities(self, image_name: str) -> Dict:
        """Scan container image for vulnerabilities using Trivy"""
        try:
            cmd = [
                "trivy", "image", 
                "--format", "json",
                "--severity", "HIGH,CRITICAL",
                image_name
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "image": image_name,
                    "vulnerabilities": json.loads(result.stdout),
                    "scan_time": "$(date -Iseconds)"
                }
            else:
                return {
                    "status": "error",
                    "image": image_name,
                    "error": result.stderr
                }
        except Exception as e:
            return {
                "status": "error",
                "image": image_name,
                "error": str(e)
            }
    
    def scan_kubernetes_config(self, manifest_path: str) -> Dict:
        """Scan Kubernetes manifests for security issues using kube-score"""
        try:
            cmd = [
                "kube-score", "score",
                "--output-format", "json",
                manifest_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "manifest": manifest_path,
                    "score": json.loads(result.stdout)
                }
            else:
                return {
                    "status": "error",
                    "manifest": manifest_path,
                    "error": result.stderr
                }
        except Exception as e:
            return {
                "status": "error",
                "manifest": manifest_path,
                "error": str(e)
            }
    
    def scan_all_consciousness_images(self) -> List[Dict]:
        """Scan all SynOS consciousness images"""
        images = [
            "synos/consciousness:production",
            "synos/security:production",
            "synos/kernel:production",
            "synos/ui:production"
        ]
        
        results = []
        for image in images:
            self.logger.info(f"Scanning image: {image}")
            result = self.scan_image_vulnerabilities(image)
            results.append(result)
        
        return results
    
    def generate_security_report(self, scan_results: List[Dict]) -> str:
        """Generate comprehensive security report"""
        report = []
        report.append("# SynOS Container Security Report")
        report.append(f"Generated: $(date)")
        report.append("")
        
        total_vulnerabilities = 0
        critical_count = 0
        high_count = 0
        
        for result in scan_results:
            if result["status"] == "success":
                image = result["image"]
                vulns = result.get("vulnerabilities", [])
                
                report.append(f"## Image: {image}")
                
                if vulns:
                    for vuln in vulns:
                        severity = vuln.get("Severity", "Unknown")
                        if severity == "CRITICAL":
                            critical_count += 1
                        elif severity == "HIGH":
                            high_count += 1
                        total_vulnerabilities += 1
                        
                        report.append(f"- **{severity}**: {vuln.get('VulnerabilityID', 'Unknown')}")
                        report.append(f"  - Description: {vuln.get('Description', 'N/A')}")
                        report.append(f"  - Fixed Version: {vuln.get('FixedVersion', 'Not available')}")
                        report.append("")
                else:
                    report.append("✅ No vulnerabilities found")
                    report.append("")
            else:
                report.append(f"❌ Error scanning {result['image']}: {result['error']}")
                report.append("")
        
        # Summary
        report.insert(3, f"**Total Vulnerabilities**: {total_vulnerabilities}")
        report.insert(4, f"**Critical**: {critical_count}")
        report.insert(5, f"**High**: {high_count}")
        report.insert(6, "")
        
        return "\n".join(report)

if __name__ == "__main__":
    scanner = SecurityScanner()
    
    # Run comprehensive security scan
    scan_results = scanner.scan_all_consciousness_images()
    
    # Generate report
    report = scanner.generate_security_report(scan_results)
    
    # Save report
    report_path = Path("/app/security/reports")
    report_path.mkdir(parents=True, exist_ok=True)
    
    report_file = report_path / f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"Security report saved to: {report_file}")
    print(report)
