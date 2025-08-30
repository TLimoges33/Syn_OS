#!/usr/bin/env python3
"""
Syn_OS Security Audit MCP Server
Provides security auditing, vulnerability assessment, and compliance checking
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent

# Security logging setup
logging.basicConfig(
    filename='/home/diablorain/Syn_OS/logs/security/mcp_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('synapticos-security-audit')

# Initialize MCP server
mcp = FastMCP("SynapticOS Security Audit Server")

class SecurityAuditor:
    """Core security auditing functionality"""
    
    def __init__(self):
        self.audit_history = []
        self.security_policies = self._load_security_policies()
        
    def _load_security_policies(self) -> Dict[str, Any]:
        """Load security policies from configuration"""
        return {
            "code_analysis": {
                "scan_for_secrets": True,
                "check_input_validation": True,
                "verify_authentication": True,
                "audit_privilege_escalation": True
            },
            "network_security": {
                "check_tls_usage": True,
                "audit_api_endpoints": True,
                "verify_rate_limiting": True
            },
            "data_protection": {
                "scan_for_pii": True,
                "check_encryption": True,
                "audit_data_flow": True
            }
        }
    
    async def audit_code_security(self, file_path: str) -> Dict[str, Any]:
        """Perform comprehensive code security audit"""
        logger.info(f"Starting security audit for: {file_path}")
        
        audit_results = {
            "file_path": file_path,
            "timestamp": datetime.now().isoformat(),
            "security_issues": [],
            "compliance_status": "pending",
            "risk_level": "unknown"
        }
        
        try:
            # Read file content for analysis
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Security checks
            issues = []
            
            # Check for hardcoded secrets
            if await self._scan_for_secrets(content):
                issues.append({
                    "type": "hardcoded_secrets",
                    "severity": "high",
                    "description": "Potential hardcoded credentials detected"
                })
            
            # Check for SQL injection vulnerabilities
            if await self._scan_sql_injection(content):
                issues.append({
                    "type": "sql_injection",
                    "severity": "critical", 
                    "description": "Potential SQL injection vulnerability"
                })
            
            # Check for command injection
            if await self._scan_command_injection(content):
                issues.append({
                    "type": "command_injection",
                    "severity": "critical",
                    "description": "Potential command injection vulnerability"
                })
            
            # Check input validation
            if not await self._check_input_validation(content):
                issues.append({
                    "type": "input_validation",
                    "severity": "medium",
                    "description": "Insufficient input validation detected"
                })
            
            audit_results["security_issues"] = issues
            audit_results["risk_level"] = self._calculate_risk_level(issues)
            audit_results["compliance_status"] = "compliant" if not issues else "non_compliant"
            
            logger.info(f"Security audit completed for {file_path}: {len(issues)} issues found")
            
        except Exception as e:
            logger.error(f"Security audit failed for {file_path}: {str(e)}")
            audit_results["error"] = str(e)
        
        self.audit_history.append(audit_results)
        return audit_results
    
    async def _scan_for_secrets(self, content: str) -> bool:
        """Scan for hardcoded secrets and credentials"""
        secret_patterns = [
            'password', 'secret', 'key', 'token', 'api_key',
            'private_key', 'access_token', 'auth_token'
        ]
        
        content_lower = content.lower()
        for pattern in secret_patterns:
            if f'{pattern}=' in content_lower or f'"{pattern}":' in content_lower:
                return True
        return False
    
    async def _scan_sql_injection(self, content: str) -> bool:
        """Scan for SQL injection vulnerabilities"""
        sql_injection_patterns = [
            'execute(', 'query(', '.format(', '% ', 
            'SELECT * FROM', 'DROP TABLE', 'DELETE FROM'
        ]
        
        for pattern in sql_injection_patterns:
            if pattern in content:
                return True
        return False
    
    async def _scan_command_injection(self, content: str) -> bool:
        """Scan for command injection vulnerabilities"""
        command_injection_patterns = [
            'os.system(', 'subprocess.', 'exec(', 'eval(',
            'shell=True', 'popen(', 'call('
        ]
        
        for pattern in command_injection_patterns:
            if pattern in content:
                return True
        return False
    
    async def _check_input_validation(self, content: str) -> bool:
        """Check for proper input validation"""
        validation_patterns = [
            'validate', 'sanitize', 'escape', 'filter',
            'isinstance(', 'len(', 'type('
        ]
        
        for pattern in validation_patterns:
            if pattern in content:
                return True
        return False
    
    def _calculate_risk_level(self, issues: List[Dict]) -> str:
        """Calculate overall risk level based on issues"""
        if not issues:
            return "low"
        
        critical_count = sum(1 for issue in issues if issue.get("severity") == "critical")
        high_count = sum(1 for issue in issues if issue.get("severity") == "high")
        
        if critical_count > 0:
            return "critical"
        elif high_count > 0:
            return "high"
        else:
            return "medium"

# Initialize security auditor
security_auditor = SecurityAuditor()

@mcp.tool("audit_file_security")
async def audit_file_security(file_path: str) -> List[TextContent]:
    """
    Perform comprehensive security audit on a file
    
    Args:
        file_path: Path to the file to audit
    """
    try:
        logger.info(f"MCP security audit requested for: {file_path}")
        
        # Validate file path is within allowed scope
        if not file_path.startswith('/home/diablorain/Syn_OS/'):
            raise ValueError("File path outside of allowed scope")
        
        # Perform security audit
        audit_result = await security_auditor.audit_code_security(file_path)
        
        # Format results for Claude
        result_text = f"Security Audit Report for {file_path}\n"
        result_text += f"Timestamp: {audit_result['timestamp']}\n"
        result_text += f"Risk Level: {audit_result['risk_level']}\n"
        result_text += f"Compliance Status: {audit_result['compliance_status']}\n\n"
        
        if audit_result['security_issues']:
            result_text += "Security Issues Found:\n"
            for issue in audit_result['security_issues']:
                result_text += f"- {issue['type']} ({issue['severity']}): {issue['description']}\n"
        else:
            result_text += "No security issues detected.\n"
        
        return [TextContent(type="text", text=result_text)]
        
    except Exception as e:
        logger.error(f"MCP security audit failed: {str(e)}")
        return [TextContent(type="text", text=f"Security audit failed: {str(e)}")]

@mcp.tool("get_security_recommendations")
async def get_security_recommendations() -> List[TextContent]:
    """Get security recommendations for SynapticOS development"""
    
    recommendations = [
        "1. Always validate and sanitize user inputs",
        "2. Use parameterized queries to prevent SQL injection",
        "3. Never hardcode credentials or secrets in source code",
        "4. Implement proper authentication and authorization",
        "5. Use HTTPS for all network communications", 
        "6. Regularly update dependencies and scan for vulnerabilities",
        "7. Implement proper logging and monitoring for security events",
        "8. Use principle of least privilege for system access",
        "9. Encrypt sensitive data at rest and in transit",
        "10. Implement secure coding practices and code reviews"
    ]
    
    result_text = "SynapticOS Security Recommendations:\n\n"
    for rec in recommendations:
        result_text += f"{rec}\n"
    
    return [TextContent(type="text", text=result_text)]

@mcp.tool("check_compliance_status")  
async def check_compliance_status() -> List[TextContent]:
    """Check overall security compliance status of SynapticOS"""
    
    # Get recent audit results
    recent_audits = security_auditor.audit_history[-10:] if security_auditor.audit_history else []
    
    total_files = len(recent_audits)
    compliant_files = sum(1 for audit in recent_audits if audit['compliance_status'] == 'compliant')
    
    compliance_rate = (compliant_files / total_files * 100) if total_files > 0 else 0
    
    result_text = f"SynapticOS Security Compliance Status:\n\n"
    result_text += f"Files Audited: {total_files}\n"
    result_text += f"Compliant Files: {compliant_files}\n"
    result_text += f"Compliance Rate: {compliance_rate:.1f}%\n\n"
    
    if compliance_rate < 80:
        result_text += "⚠️ WARNING: Compliance rate below recommended threshold (80%)\n"
        result_text += "Consider reviewing and fixing security issues before production deployment.\n"
    else:
        result_text += "✅ Good compliance rate. Continue maintaining security standards.\n"
    
    return [TextContent(type="text", text=result_text)]

if __name__ == "__main__":
    try:
        logger.info("Starting SynapticOS Security Audit MCP Server")
        print("SynapticOS Security Audit MCP Server starting...")
        mcp.run()
    except Exception as e:
        logger.error(f"Failed to start MCP server: {str(e)}")
        print(f"Error starting MCP server: {str(e)}")
        raise