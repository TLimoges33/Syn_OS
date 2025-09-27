#!/usr/bin/env python3
"""
Enterprise Security Assessment Runner
Automated execution of comprehensive security assessments using the Enterprise MSSP Platform
"""

import asyncio
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from src.security.enterprise_mssp_platform import (
    EnterpriseMSSPPlatform, 
    SecurityFramework,
    SecurityAssessment
)


class EnterpriseAssessmentRunner:
    """Enterprise security assessment execution and reporting"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/enterprise_mssp.yaml"
        self.mssp_platform = EnterpriseMSSPPlatform(self.config_path)
        self.results_dir = Path("results/security_assessments")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    async def run_assessment_suite(self, target: str, 
                                 profile: str = "comprehensive") -> Dict[str, any]:
        """Run comprehensive security assessment suite"""
        
        print(f"🔍 Starting Enterprise Security Assessment for: {target}")
        print(f"📋 Assessment Profile: {profile}")
        print("=" * 60)
        
        assessment_results = {
            "target": target,
            "profile": profile,
            "timestamp": datetime.now().isoformat(),
            "assessments": {},
            "summary": {},
            "recommendations": []
        }
        
        # Define assessment frameworks based on profile
        frameworks = self._get_frameworks_for_profile(profile)
        
        # Run assessments for each framework
        for framework in frameworks:
            print(f"\n🛡️  Running {framework.value.upper()} Assessment...")
            
            try:
                assessment = await self.mssp_platform.run_security_assessment(
                    target=target,
                    framework=framework
                )
                
                assessment_results["assessments"][framework.value] = {
                    "assessment_id": assessment.assessment_id,
                    "status": assessment.status,
                    "risk_score": assessment.risk_score,
                    "findings_count": len(assessment.findings),
                    "tools_used": assessment.tools_used,
                    "compliance_status": assessment.compliance_status,
                    "findings": assessment.findings,
                    "recommendations": assessment.recommendations,
                    "duration": self._calculate_duration(assessment)
                }
                
                print(f"   ✅ {framework.value}: Risk Score {assessment.risk_score}/100")
                print(f"   📊 Findings: {len(assessment.findings)}")
                print(f"   ⏱️  Duration: {self._calculate_duration(assessment)}")
                
            except Exception as e:
                print(f"   ❌ {framework.value}: Failed - {e}")
                assessment_results["assessments"][framework.value] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        # Generate summary and recommendations
        assessment_results["summary"] = self._generate_assessment_summary(
            assessment_results["assessments"]
        )
        assessment_results["recommendations"] = self._generate_enterprise_recommendations(
            assessment_results["assessments"]
        )
        
        # Save results
        await self._save_assessment_results(assessment_results)
        
        return assessment_results
    
    def _get_frameworks_for_profile(self, profile: str) -> List[SecurityFramework]:
        """Get security frameworks based on assessment profile"""
        
        profiles = {
            "rapid": [
                SecurityFramework.PENETRATION_TESTING
            ],
            "comprehensive": [
                SecurityFramework.DEVSECOPS,
                SecurityFramework.PENETRATION_TESTING,
                SecurityFramework.VULNERABILITY_MANAGEMENT
            ],
            "compliance": [
                SecurityFramework.DEVSECOPS,
                SecurityFramework.VULNERABILITY_MANAGEMENT,
                SecurityFramework.COMPLIANCE
            ],
            "incident_response": [
                SecurityFramework.INCIDENT_RESPONSE,
                SecurityFramework.FORENSICS,
                SecurityFramework.THREAT_INTELLIGENCE
            ],
            "full_enterprise": [
                SecurityFramework.DEVSECOPS,
                SecurityFramework.PENETRATION_TESTING,
                SecurityFramework.THREAT_INTELLIGENCE,
                SecurityFramework.VULNERABILITY_MANAGEMENT,
                SecurityFramework.INCIDENT_RESPONSE,
                SecurityFramework.FORENSICS
            ]
        }
        
        return profiles.get(profile, profiles["comprehensive"])
    
    def _calculate_duration(self, assessment: SecurityAssessment) -> str:
        """Calculate assessment duration"""
        if assessment.end_time and assessment.start_time:
            duration = assessment.end_time - assessment.start_time
            minutes = int(duration.total_seconds() / 60)
            seconds = int(duration.total_seconds() % 60)
            return f"{minutes}m {seconds}s"
        return "Unknown"
    
    def _generate_assessment_summary(self, assessments: Dict[str, any]) -> Dict[str, any]:
        """Generate comprehensive assessment summary"""
        
        summary = {
            "overall_risk_score": 0.0,
            "total_findings": 0,
            "critical_findings": 0,
            "high_findings": 0,
            "medium_findings": 0,
            "low_findings": 0,
            "successful_assessments": 0,
            "failed_assessments": 0,
            "compliance_overview": {},
            "risk_category": "unknown"
        }
        
        successful_assessments = []
        total_risk_score = 0.0
        
        for framework, result in assessments.items():
            if result.get("status") == "completed":
                summary["successful_assessments"] += 1
                successful_assessments.append(result)
                total_risk_score += result.get("risk_score", 0)
                
                # Count findings by severity
                for finding in result.get("findings", []):
                    severity = finding.get("severity", "info").lower()
                    summary["total_findings"] += 1
                    
                    if severity == "critical":
                        summary["critical_findings"] += 1
                    elif severity == "high":
                        summary["high_findings"] += 1
                    elif severity == "medium":
                        summary["medium_findings"] += 1
                    elif severity == "low":
                        summary["low_findings"] += 1
                
                # Aggregate compliance status
                compliance = result.get("compliance_status", {})
                for framework_name, status in compliance.items():
                    if framework_name not in summary["compliance_overview"]:
                        summary["compliance_overview"][framework_name] = []
                    summary["compliance_overview"][framework_name].append(status)
            else:
                summary["failed_assessments"] += 1
        
        # Calculate overall risk score
        if successful_assessments:
            summary["overall_risk_score"] = round(total_risk_score / len(successful_assessments), 2)
        
        # Determine risk category
        if summary["overall_risk_score"] >= 80:
            summary["risk_category"] = "critical"
        elif summary["overall_risk_score"] >= 60:
            summary["risk_category"] = "high"
        elif summary["overall_risk_score"] >= 40:
            summary["risk_category"] = "medium"
        elif summary["overall_risk_score"] >= 20:
            summary["risk_category"] = "low"
        else:
            summary["risk_category"] = "minimal"
        
        return summary
    
    def _generate_enterprise_recommendations(self, assessments: Dict[str, any]) -> List[str]:
        """Generate enterprise-level security recommendations"""
        
        recommendations = []
        
        # Calculate overall metrics
        total_critical = sum(result.get("findings", []) for result in assessments.values() 
                           if result.get("status") == "completed")
        critical_count = sum(1 for findings in total_critical 
                           for finding in findings 
                           if finding.get("severity") == "critical")
        
        high_count = sum(1 for findings in total_critical 
                        for finding in findings 
                        if finding.get("severity") == "high")
        
        # Critical priority recommendations
        if critical_count > 0:
            recommendations.extend([
                f"🚨 CRITICAL: Immediately address {critical_count} critical vulnerabilities",
                "🔒 Implement emergency incident response procedures",
                "📞 Notify CISO and security team leadership",
                "🚫 Consider isolating affected systems until remediation"
            ])
        
        if high_count > 5:
            recommendations.extend([
                f"⚠️  HIGH PRIORITY: Address {high_count} high-severity findings within 72 hours",
                "🔍 Conduct comprehensive threat hunting activities",
                "📋 Review and update security policies and procedures"
            ])
        
        # Framework-specific recommendations
        failed_frameworks = [fw for fw, result in assessments.items() 
                           if result.get("status") == "failed"]
        
        if failed_frameworks:
            recommendations.append(
                f"🔧 INFRASTRUCTURE: Fix assessment failures in {', '.join(failed_frameworks)}"
            )
        
        # Compliance recommendations
        compliance_issues = []
        for framework, result in assessments.items():
            compliance = result.get("compliance_status", {})
            for comp_framework, status in compliance.items():
                if "NON_COMPLIANT" in status:
                    compliance_issues.append(comp_framework)
        
        if compliance_issues:
            unique_issues = list(set(compliance_issues))
            recommendations.append(
                f"📋 COMPLIANCE: Address non-compliance in {', '.join(unique_issues)}"
            )
        
        # General enterprise recommendations
        recommendations.extend([
            "🛡️  Implement continuous security monitoring",
            "📚 Conduct security awareness training for all personnel",
            "🔄 Establish regular vulnerability assessment schedule",
            "📊 Integrate security metrics into executive dashboards",
            "🤝 Review and test incident response procedures",
            "🔐 Implement zero-trust architecture principles"
        ])
        
        return recommendations
    
    async def _save_assessment_results(self, results: Dict[str, any]):
        """Save assessment results to file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_safe = results["target"].replace("://", "_").replace("/", "_").replace(":", "_")
        filename = f"enterprise_assessment_{target_safe}_{timestamp}.json"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {filepath}")
    
    def print_assessment_report(self, results: Dict[str, any]):
        """Print comprehensive assessment report"""
        
        print("\n" + "=" * 80)
        print("🏢 ENTERPRISE SECURITY ASSESSMENT REPORT")
        print("=" * 80)
        
        # Header information
        print(f"🎯 Target: {results['target']}")
        print(f"📋 Profile: {results['profile']}")
        print(f"⏰ Timestamp: {results['timestamp']}")
        
        # Summary
        summary = results["summary"]
        print(f"\n📊 ASSESSMENT SUMMARY")
        print("-" * 40)
        print(f"Overall Risk Score: {summary['overall_risk_score']}/100 ({summary['risk_category'].upper()})")
        print(f"Total Findings: {summary['total_findings']}")
        print(f"  • Critical: {summary['critical_findings']}")
        print(f"  • High: {summary['high_findings']}")
        print(f"  • Medium: {summary['medium_findings']}")
        print(f"  • Low: {summary['low_findings']}")
        print(f"Successful Assessments: {summary['successful_assessments']}")
        print(f"Failed Assessments: {summary['failed_assessments']}")
        
        # Framework Results
        print(f"\n🛡️  FRAMEWORK RESULTS")
        print("-" * 40)
        for framework, result in results["assessments"].items():
            status_icon = "✅" if result.get("status") == "completed" else "❌"
            print(f"{status_icon} {framework.upper()}")
            
            if result.get("status") == "completed":
                print(f"    Risk Score: {result['risk_score']}/100")
                print(f"    Findings: {result['findings_count']}")
                print(f"    Tools: {', '.join(result['tools_used'])}")
                print(f"    Duration: {result['duration']}")
            else:
                print(f"    Error: {result.get('error', 'Unknown')}")
            print()
        
        # Compliance Status
        if summary["compliance_overview"]:
            print(f"📋 COMPLIANCE STATUS")
            print("-" * 40)
            for framework, statuses in summary["compliance_overview"].items():
                compliant_count = sum(1 for s in statuses if "COMPLIANT" in s and "NON_" not in s)
                total_count = len(statuses)
                status_icon = "✅" if compliant_count == total_count else "⚠️"
                print(f"{status_icon} {framework}: {compliant_count}/{total_count} compliant")
        
        # Recommendations
        print(f"\n🎯 ENTERPRISE RECOMMENDATIONS")
        print("-" * 40)
        for i, recommendation in enumerate(results["recommendations"], 1):
            print(f"{i:2d}. {recommendation}")
        
        print("\n" + "=" * 80)


async def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(
        description="Enterprise Security Assessment Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Assessment Profiles:
  rapid           - Quick penetration testing assessment
  comprehensive   - DevSecOps + PenTest + VulnMgmt (default)
  compliance      - Compliance-focused assessment
  incident_response - IR + Forensics + Threat Intel
  full_enterprise - All security frameworks

Examples:
  python enterprise_assessment_runner.py -t https://example.com
  python enterprise_assessment_runner.py -t 192.168.1.100 -p compliance
  python enterprise_assessment_runner.py -t example-app -p full_enterprise
        """
    )
    
    parser.add_argument(
        "-t", "--target",
        required=True,
        help="Target for security assessment (URL, IP, or application name)"
    )
    
    parser.add_argument(
        "-p", "--profile",
        default="comprehensive",
        choices=["rapid", "comprehensive", "compliance", "incident_response", "full_enterprise"],
        help="Assessment profile (default: comprehensive)"
    )
    
    parser.add_argument(
        "-c", "--config",
        help="Path to enterprise configuration file"
    )
    
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip printing detailed report"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize assessment runner
        runner = EnterpriseAssessmentRunner(config_path=args.config)
        
        # Run assessment suite
        results = await runner.run_assessment_suite(
            target=args.target,
            profile=args.profile
        )
        
        # Print report unless disabled
        if not args.no_report:
            runner.print_assessment_report(results)
        
        # Return appropriate exit code based on risk score
        risk_score = results["summary"]["overall_risk_score"]
        if risk_score >= 80:
            print(f"\n🚨 CRITICAL RISK DETECTED: {risk_score}/100")
            return 2
        elif risk_score >= 60:
            print(f"\n⚠️  HIGH RISK DETECTED: {risk_score}/100")
            return 1
        else:
            print(f"\n✅ Assessment completed successfully: {risk_score}/100")
            return 0
            
    except KeyboardInterrupt:
        print("\n❌ Assessment interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Assessment failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
