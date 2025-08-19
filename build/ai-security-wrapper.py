#!/usr/bin/env python3
"""
AI Security Tool Wrapper System
Creates consciousness-enhanced versions of all security tools
"""

import asyncio
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import shlex
import yaml

# Import consciousness interface
import sys
sys.path.append('/home/diablorain/Syn_OS/src/consciousness_v2')
from core.consciousness_bus import ConsciousnessBus
from components.neural_darwinism_v2 import NeuralDarwinismEngine

@dataclass
class ToolExecution:
    """Tool execution context"""
    tool_name: str
    command: List[str]
    target: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    exit_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    ai_suggestions: List[str] = None
    learning_context: str = "operational"

class AISecurityWrapper:
    """AI wrapper for security tools"""
    
    def __init__(self, tool_name: str, original_binary: str):
        self.tool_name = tool_name
        self.original_binary = original_binary
        self.consciousness = None
        self.logger = logging.getLogger(f"ai_wrapper.{tool_name}")
        
        # Tool-specific configurations
        self.tool_configs = self._load_tool_configs()
        
        # Initialize consciousness connection
        asyncio.create_task(self._init_consciousness())
    
    async def _init_consciousness(self):
        """Initialize connection to consciousness engine"""
        try:
            self.consciousness = NeuralDarwinismEngine(
                component_id=f"tool_wrapper_{self.tool_name}",
                population_size=30,
                learning_rate=0.02
            )
            await self.consciousness.start()
            self.logger.info("Connected to consciousness engine")
        except Exception as e:
            self.logger.warning(f"Could not connect to consciousness: {e}")
    
    def _load_tool_configs(self) -> Dict[str, Any]:
        """Load AI enhancement configurations for security tools"""
        return {
            'nmap': {
                'ai_enhancements': ['target_discovery', 'port_prioritization', 'scan_optimization'],
                'output_analysis': ['service_identification', 'vulnerability_hints', 'next_steps'],
                'learning_opportunities': ['network_topology', 'service_fingerprinting', 'stealth_techniques']
            },
            'burpsuite': {
                'ai_enhancements': ['request_analysis', 'payload_generation', 'response_interpretation'],
                'output_analysis': ['vulnerability_detection', 'attack_vectors', 'exploitation_path'],
                'learning_opportunities': ['web_application_security', 'http_protocols', 'injection_techniques']
            },
            'metasploit': {
                'ai_enhancements': ['exploit_selection', 'payload_optimization', 'post_exploitation'],
                'output_analysis': ['success_probability', 'stealth_rating', 'persistence_options'],
                'learning_opportunities': ['exploit_development', 'payload_techniques', 'lateral_movement']
            },
            'wireshark': {
                'ai_enhancements': ['traffic_analysis', 'anomaly_detection', 'protocol_insights'],
                'output_analysis': ['threat_indicators', 'communication_patterns', 'data_exfiltration'],
                'learning_opportunities': ['network_protocols', 'traffic_analysis', 'forensics_techniques']
            },
            'sqlmap': {
                'ai_enhancements': ['injection_point_discovery', 'payload_customization', 'database_enumeration'],
                'output_analysis': ['injection_success_rate', 'data_extraction_efficiency', 'detection_avoidance'],
                'learning_opportunities': ['sql_injection', 'database_security', 'web_application_testing']
            },
            'hydra': {
                'ai_enhancements': ['wordlist_optimization', 'timing_adjustment', 'protocol_adaptation'],
                'output_analysis': ['success_probability', 'account_lockout_risk', 'credential_patterns'],
                'learning_opportunities': ['password_attacks', 'authentication_mechanisms', 'bruteforce_techniques']
            },
            'hashcat': {
                'ai_enhancements': ['hash_identification', 'rule_optimization', 'wordlist_selection'],
                'output_analysis': ['crack_probability', 'time_estimation', 'pattern_recognition'],
                'learning_opportunities': ['cryptographic_attacks', 'password_patterns', 'hash_algorithms']
            },
            'nikto': {
                'ai_enhancements': ['scan_customization', 'false_positive_reduction', 'vulnerability_prioritization'],
                'output_analysis': ['risk_assessment', 'exploit_availability', 'remediation_suggestions'],
                'learning_opportunities': ['web_vulnerabilities', 'security_scanning', 'risk_assessment']
            },
            'aircrack-ng': {
                'ai_enhancements': ['attack_vector_selection', 'capture_optimization', 'key_recovery'],
                'output_analysis': ['success_likelihood', 'time_estimation', 'signal_quality'],
                'learning_opportunities': ['wireless_security', '802.11_protocols', 'cryptographic_attacks']
            },
            'john': {
                'ai_enhancements': ['rule_generation', 'wordlist_mutation', 'attack_mode_selection'],
                'output_analysis': ['password_patterns', 'complexity_analysis', 'policy_compliance'],
                'learning_opportunities': ['password_cracking', 'authentication_security', 'policy_analysis']
            }
        }
    
    async def execute(self, args: List[str], context: str = "operational") -> ToolExecution:
        """Execute tool with AI enhancements"""
        execution = ToolExecution(
            tool_name=self.tool_name,
            command=[self.original_binary] + args,
            start_time=datetime.now(),
            learning_context=context
        )
        
        # Pre-execution AI analysis
        await self._pre_execution_analysis(execution, args)
        
        # Execute the tool
        await self._execute_tool(execution)
        
        # Post-execution AI analysis
        await self._post_execution_analysis(execution)
        
        # Log for learning
        await self._log_execution(execution)
        
        return execution
    
    async def _pre_execution_analysis(self, execution: ToolExecution, args: List[str]):
        """AI analysis before tool execution"""
        if not self.consciousness:
            return
        
        try:
            # Extract target from arguments
            target = self._extract_target(args)
            execution.target = target
            
            # Get AI suggestions for tool optimization
            suggestions = await self._get_ai_suggestions(execution.tool_name, args, target)
            execution.ai_suggestions = suggestions
            
            if suggestions:
                self.logger.info(f"AI Suggestions for {execution.tool_name}:")
                for suggestion in suggestions[:3]:  # Show top 3
                    self.logger.info(f"  • {suggestion}")
                    
        except Exception as e:
            self.logger.warning(f"Pre-execution analysis failed: {e}")
    
    async def _execute_tool(self, execution: ToolExecution):
        """Execute the actual security tool"""
        try:
            # Create environment with AI enhancements
            env = self._create_enhanced_environment()
            
            # Execute with timeout and monitoring
            process = await asyncio.create_subprocess_exec(
                *execution.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            # Monitor execution with AI
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=self._get_tool_timeout(execution.tool_name)
            )
            
            execution.stdout = stdout.decode('utf-8', errors='ignore')
            execution.stderr = stderr.decode('utf-8', errors='ignore')
            execution.exit_code = process.returncode
            execution.end_time = datetime.now()
            
        except asyncio.TimeoutError:
            self.logger.warning(f"{execution.tool_name} execution timed out")
            execution.exit_code = -1
            execution.stderr = "Execution timed out"
            execution.end_time = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}")
            execution.exit_code = -2
            execution.stderr = f"Execution error: {e}"
            execution.end_time = datetime.now()
    
    async def _post_execution_analysis(self, execution: ToolExecution):
        """AI analysis of tool output"""
        if not self.consciousness or not execution.stdout:
            return
        
        try:
            # Analyze output based on tool type
            analysis = await self._analyze_tool_output(execution)
            
            # Generate learning insights
            insights = await self._generate_learning_insights(execution, analysis)
            
            # Display AI analysis
            if analysis:
                self.logger.info(f"\n🧠 AI Analysis for {execution.tool_name}:")
                for key, value in analysis.items():
                    self.logger.info(f"  {key}: {value}")
            
            if insights and execution.learning_context != "silent":
                self.logger.info(f"\n📚 Learning Insights:")
                for insight in insights[:3]:
                    self.logger.info(f"  • {insight}")
                    
        except Exception as e:
            self.logger.warning(f"Post-execution analysis failed: {e}")
    
    async def _get_ai_suggestions(self, tool_name: str, args: List[str], target: Optional[str]) -> List[str]:
        """Get AI suggestions for tool execution"""
        suggestions = []
        
        # Tool-specific AI suggestions
        if tool_name == "nmap" and target:
            suggestions = [
                f"Consider adding -sV for service version detection on {target}",
                f"Use -O for OS fingerprinting if permitted",
                f"Add --script vuln for vulnerability detection",
                f"Consider stealth options like -sS -T2 for quiet scanning"
            ]
        elif tool_name == "burpsuite":
            suggestions = [
                "Enable active scanning for comprehensive vulnerability detection",
                "Use intruder for automated parameter fuzzing", 
                "Review proxy history for manual testing opportunities",
                "Configure spider for thorough site mapping"
            ]
        elif tool_name == "metasploit":
            suggestions = [
                "Use search command to find relevant exploits",
                "Verify target compatibility before exploitation",
                "Consider payload restrictions and evasion techniques",
                "Plan post-exploitation activities and persistence"
            ]
        elif tool_name == "sqlmap" and target:
            suggestions = [
                f"Test all parameters on {target} for injection points",
                "Use --level=3 --risk=2 for comprehensive testing",
                "Consider --tamper scripts for WAF bypass",
                "Enable --batch for automated decision making"
            ]
        elif tool_name == "hydra" and target:
            suggestions = [
                f"Use common username lists against {target}",
                "Implement delays to avoid account lockouts",
                "Try password spraying before brute force",
                "Monitor for defensive responses and IP blocking"
            ]
        
        return suggestions
    
    async def _analyze_tool_output(self, execution: ToolExecution) -> Dict[str, str]:
        """Analyze tool output with AI"""
        analysis = {}
        
        # Tool-specific output analysis
        if execution.tool_name == "nmap":
            analysis = self._analyze_nmap_output(execution.stdout)
        elif execution.tool_name == "burpsuite":
            analysis = self._analyze_burp_output(execution.stdout)
        elif execution.tool_name == "sqlmap":
            analysis = self._analyze_sqlmap_output(execution.stdout)
        elif execution.tool_name == "hydra":
            analysis = self._analyze_hydra_output(execution.stdout)
        elif execution.tool_name == "nikto":
            analysis = self._analyze_nikto_output(execution.stdout)
        
        return analysis
    
    def _analyze_nmap_output(self, output: str) -> Dict[str, str]:
        """Analyze nmap output"""
        analysis = {}
        
        # Parse open ports
        open_ports = []
        for line in output.split('\n'):
            if '/tcp' in line and 'open' in line:
                port_info = line.strip()
                open_ports.append(port_info)
        
        if open_ports:
            analysis['Open Ports'] = f"Found {len(open_ports)} open ports"
            analysis['High Priority'] = "SSH (22), HTTP (80), HTTPS (443), RDP (3389)" if any(port in str(open_ports) for port in ['22/', '80/', '443/', '3389/']) else "Review all open services"
            analysis['Next Steps'] = "Service enumeration, version detection, vulnerability scanning"
        else:
            analysis['Status'] = "No open ports detected"
            analysis['Recommendation'] = "Try different scan types or check host availability"
        
        return analysis
    
    def _analyze_sqlmap_output(self, output: str) -> Dict[str, str]:
        """Analyze sqlmap output"""
        analysis = {}
        
        if 'vulnerable' in output.lower():
            analysis['Vulnerability'] = "SQL injection vulnerability detected"
            analysis['Risk Level'] = "HIGH - Immediate attention required"
            analysis['Next Steps'] = "Enumerate database, extract sensitive data, test privilege escalation"
        elif 'not vulnerable' in output.lower():
            analysis['Status'] = "No SQL injection vulnerabilities found"
            analysis['Recommendation'] = "Try different injection techniques or parameters"
        elif 'error' in output.lower():
            analysis['Status'] = "Errors detected during testing"
            analysis['Recommendation'] = "Review target accessibility and parameter syntax"
        
        return analysis
    
    def _analyze_hydra_output(self, output: str) -> Dict[str, str]:
        """Analyze hydra output"""
        analysis = {}
        
        # Look for successful logins
        success_lines = [line for line in output.split('\n') if 'login:' in line and 'password:' in line]
        
        if success_lines:
            analysis['Success'] = f"Found {len(success_lines)} valid credentials"
            analysis['Risk Level'] = "HIGH - Weak authentication detected"
            analysis['Next Steps'] = "Test credential reuse, privilege escalation, lateral movement"
        else:
            if 'completed' in output.lower():
                analysis['Status'] = "No valid credentials found"
                analysis['Recommendation'] = "Try different wordlists or password policies"
            else:
                analysis['Status'] = "Attack in progress or interrupted"
                analysis['Recommendation'] = "Monitor for defensive responses, adjust timing"
        
        return analysis
    
    def _analyze_nikto_output(self, output: str) -> Dict[str, str]:
        """Analyze nikto output"""
        analysis = {}
        
        # Count findings
        finding_lines = [line for line in output.split('\n') if '+ ' in line and 'OSVDB' in line]
        
        if finding_lines:
            analysis['Findings'] = f"Discovered {len(finding_lines)} potential vulnerabilities"
            analysis['Priority'] = "Review findings for false positives and exploitability"
            analysis['Next Steps'] = "Manual verification, exploit research, remediation planning"
        else:
            analysis['Status'] = "Scan completed with minimal findings"
            analysis['Recommendation'] = "Consider additional testing methods"
        
        return analysis
    
    def _analyze_burp_output(self, output: str) -> Dict[str, str]:
        """Analyze burp suite output"""
        # Burp Suite typically doesn't output to stdout in command line mode
        return {'Status': 'Interactive tool - check GUI for results'}
    
    async def _generate_learning_insights(self, execution: ToolExecution, analysis: Dict[str, str]) -> List[str]:
        """Generate educational insights from tool execution"""
        insights = []
        tool_config = self.tool_configs.get(execution.tool_name, {})
        learning_opps = tool_config.get('learning_opportunities', [])
        
        # Generate insights based on tool and results
        if execution.tool_name == "nmap" and 'Open Ports' in analysis:
            insights = [
                "Service enumeration is crucial for finding attack vectors",
                "Different scan types reveal different information about targets",
                "Port state filtering can indicate firewall or IDS presence",
                "Version detection helps identify specific vulnerabilities"
            ]
        elif execution.tool_name == "sqlmap" and 'Vulnerability' in analysis:
            insights = [
                "SQL injection can lead to complete database compromise",
                "Always test with different injection techniques and payloads",
                "Understanding database structure aids in privilege escalation",
                "Use tamper scripts to bypass web application firewalls"
            ]
        elif execution.tool_name == "hydra" and 'Success' in analysis:
            insights = [
                "Weak passwords are still a major attack vector",
                "Account lockout policies can be bypassed with password spraying",
                "Valid credentials often work across multiple services",
                "Monitor for defensive responses during authentication attacks"
            ]
        
        # Add general learning opportunities
        for opp in learning_opps[:2]:
            insights.append(f"Study {opp.replace('_', ' ')} for deeper understanding")
        
        return insights
    
    def _extract_target(self, args: List[str]) -> Optional[str]:
        """Extract target from command line arguments"""
        # Common patterns for target specification
        for i, arg in enumerate(args):
            # IP addresses and domains
            if any(char in arg for char in ['.', ':']):
                if not arg.startswith('-') and not arg.startswith('/'):
                    return arg
            # URL targets
            if arg.startswith(('http://', 'https://')):
                return arg
            # -t or --target flags
            if arg in ['-t', '--target'] and i + 1 < len(args):
                return args[i + 1]
        
        return None
    
    def _create_enhanced_environment(self) -> Dict[str, str]:
        """Create environment variables with AI enhancements"""
        import os
        env = os.environ.copy()
        
        # Add AI-specific environment variables
        env['SYNOS_AI_ENHANCED'] = '1'
        env['SYNOS_CONSCIOUSNESS_ENDPOINT'] = 'http://localhost:8080/consciousness'
        env['SYNOS_TOOL_LOGGING'] = '1'
        
        return env
    
    def _get_tool_timeout(self, tool_name: str) -> float:
        """Get appropriate timeout for tool execution"""
        timeouts = {
            'nmap': 300.0,      # 5 minutes
            'burpsuite': 1800.0, # 30 minutes
            'sqlmap': 600.0,    # 10 minutes
            'hydra': 900.0,     # 15 minutes
            'nikto': 300.0,     # 5 minutes
            'hashcat': 3600.0,  # 1 hour
            'john': 3600.0,     # 1 hour
        }
        
        return timeouts.get(tool_name, 180.0)  # Default 3 minutes
    
    async def _log_execution(self, execution: ToolExecution):
        """Log execution for consciousness learning"""
        if not self.consciousness:
            return
        
        try:
            # Prepare learning data
            learning_data = {
                'tool': execution.tool_name,
                'target': execution.target,
                'success': execution.exit_code == 0,
                'duration': (execution.end_time - execution.start_time).total_seconds() if execution.end_time else 0,
                'output_length': len(execution.stdout) if execution.stdout else 0,
                'context': execution.learning_context,
                'timestamp': execution.start_time.isoformat()
            }
            
            # Feed to consciousness for learning
            # This would integrate with the neural darwinism engine
            # to improve future tool suggestions and analysis
            
        except Exception as e:
            self.logger.warning(f"Failed to log execution: {e}")

class AIToolOrchestrator:
    """Orchestrates AI-enhanced security tools"""
    
    def __init__(self):
        self.tools: Dict[str, AISecurityWrapper] = {}
        self.logger = logging.getLogger("ai_orchestrator")
        self.consciousness = None
        
        # Initialize consciousness
        asyncio.create_task(self._init_consciousness())
    
    async def _init_consciousness(self):
        """Initialize orchestrator consciousness connection"""
        try:
            self.consciousness = NeuralDarwinismEngine(
                component_id="tool_orchestrator",
                population_size=50,
                learning_rate=0.01
            )
            await self.consciousness.start()
            self.logger.info("Orchestrator connected to consciousness")
        except Exception as e:
            self.logger.warning(f"Could not connect to consciousness: {e}")
    
    def register_tool(self, tool_name: str, binary_path: str):
        """Register a security tool with AI enhancement"""
        wrapper = AISecurityWrapper(tool_name, binary_path)
        self.tools[tool_name] = wrapper
        self.logger.info(f"Registered AI-enhanced tool: {tool_name}")
    
    async def execute_tool(self, tool_name: str, args: List[str], context: str = "operational") -> ToolExecution:
        """Execute AI-enhanced security tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not registered")
        
        wrapper = self.tools[tool_name]
        return await wrapper.execute(args, context)
    
    async def suggest_tools(self, objective: str, target: Optional[str] = None) -> List[str]:
        """AI-powered tool suggestion for security objectives"""
        if not self.consciousness:
            return self._heuristic_tool_suggestion(objective)
        
        # This would use consciousness to suggest optimal tool chains
        # based on the objective and previous learning
        
        suggestions = []
        
        if "reconnaissance" in objective.lower():
            suggestions = ["nmap", "nikto", "gobuster", "theharvester"]
        elif "web" in objective.lower():
            suggestions = ["burpsuite", "sqlmap", "nikto", "gobuster"]
        elif "wireless" in objective.lower():
            suggestions = ["aircrack-ng", "kismet", "wifite"]
        elif "password" in objective.lower():
            suggestions = ["hashcat", "john", "hydra"]
        elif "forensics" in objective.lower():
            suggestions = ["volatility", "autopsy", "foremost", "binwalk"]
        else:
            suggestions = ["nmap", "burpsuite", "metasploit", "wireshark"]
        
        return suggestions
    
    def _heuristic_tool_suggestion(self, objective: str) -> List[str]:
        """Fallback heuristic tool suggestions"""
        objective_lower = objective.lower()
        
        if any(word in objective_lower for word in ["scan", "discover", "reconnaissance", "recon"]):
            return ["nmap", "masscan", "nikto", "gobuster"]
        elif any(word in objective_lower for word in ["web", "application", "webapp"]):
            return ["burpsuite", "zaproxy", "sqlmap", "nikto"]
        elif any(word in objective_lower for word in ["exploit", "attack", "penetrate"]):
            return ["metasploit", "searchsploit", "exploit-db"]
        elif any(word in objective_lower for word in ["password", "crack", "brute"]):
            return ["hashcat", "john", "hydra", "crunch"]
        elif any(word in objective_lower for word in ["wireless", "wifi", "802.11"]):
            return ["aircrack-ng", "wifite", "kismet"]
        elif any(word in objective_lower for word in ["forensic", "analysis", "investigate"]):
            return ["volatility", "autopsy", "sleuthkit", "binwalk"]
        else:
            return ["nmap", "burpsuite", "wireshark", "metasploit"]

# Tool wrapper generation script
async def generate_tool_wrappers():
    """Generate AI wrappers for all security tools"""
    
    # Common security tools to wrap
    tools_to_wrap = [
        ('nmap', '/usr/bin/nmap'),
        ('burpsuite', '/usr/bin/burpsuite'),
        ('sqlmap', '/usr/bin/sqlmap'),
        ('hydra', '/usr/bin/hydra'),
        ('hashcat', '/usr/bin/hashcat'),
        ('john', '/usr/bin/john'),
        ('nikto', '/usr/bin/nikto'),
        ('gobuster', '/usr/bin/gobuster'),
        ('dirb', '/usr/bin/dirb'),
        ('wireshark', '/usr/bin/wireshark'),
        ('aircrack-ng', '/usr/bin/aircrack-ng'),
        ('metasploit', '/usr/bin/msfconsole'),
        ('zaproxy', '/usr/bin/zaproxy'),
        ('volatility', '/usr/bin/volatility'),
        ('autopsy', '/usr/bin/autopsy'),
        ('binwalk', '/usr/bin/binwalk'),
        ('foremost', '/usr/bin/foremost'),
        ('theharvester', '/usr/bin/theharvester'),
        ('searchsploit', '/usr/bin/searchsploit'),
        ('masscan', '/usr/bin/masscan'),
        ('kismet', '/usr/bin/kismet'),
        ('wifite', '/usr/bin/wifite'),
        ('crunch', '/usr/bin/crunch')
    ]
    
    orchestrator = AIToolOrchestrator()
    
    for tool_name, binary_path in tools_to_wrap:
        orchestrator.register_tool(tool_name, binary_path)
        
        # Create wrapper script
        wrapper_script = f"""#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

sys.path.append('/opt/synos/ai-wrapper')
from ai_security_wrapper import AISecurityWrapper

async def main():
    wrapper = AISecurityWrapper('{tool_name}', '{binary_path}')
    execution = await wrapper.execute(sys.argv[1:])
    
    # Print original output
    print(execution.stdout, end='')
    if execution.stderr:
        print(execution.stderr, file=sys.stderr, end='')
    
    sys.exit(execution.exit_code or 0)

if __name__ == "__main__":
    asyncio.run(main())
"""
        
        # Write wrapper script
        wrapper_path = Path(f"/usr/local/bin/ai-{tool_name}")
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_script)
        
        # Make executable
        wrapper_path.chmod(0o755)
        
        print(f"Created AI wrapper: {wrapper_path}")

if __name__ == "__main__":
    asyncio.run(generate_tool_wrappers())