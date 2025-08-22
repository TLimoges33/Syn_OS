#!/usr/bin/env python3
"""
Perplexity Consciousness Interface for Syn_OS
Provides real-time knowledge retrieval with consciousness-aware processing
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp

from src.consciousness_v2.consciousness_bus import ConsciousnessBus, ConsciousnessState
from src.security.audit_logger import AuditLogger


class PerplexityAnalysisType(Enum):
    """Types of analysis Perplexity can perform"""
    THREAT_INTELLIGENCE = "threat_intelligence"
    VULNERABILITY_RESEARCH = "vulnerability_research"
    SECURITY_NEWS = "security_news"
    MALWARE_RESEARCH = "malware_research"
    EXPLOIT_RESEARCH = "exploit_research"
    COMPLIANCE_RESEARCH = "compliance_research"
    TOOL_RESEARCH = "tool_research"
    TECHNIQUE_RESEARCH = "technique_research"


@dataclass
class PerplexityRequest:
    """Perplexity API request structure"""
    query: str
    analysis_type: PerplexityAnalysisType
    consciousness_level: float
    model: str = "llama-3.1-sonar-large-128k-online"
    temperature: float = 0.2
    max_tokens: int = 2048
    search_domain_filter: Optional[List[str]] = None
    search_recency_filter: str = "month"  # hour, day, week, month, year


@dataclass
class PerplexityResponse:
    """Perplexity API response structure"""
    content: str
    analysis_type: PerplexityAnalysisType
    consciousness_level: float
    confidence_score: float
    processing_time: float
    token_usage: Dict[str, int]
    citations: List[Dict[str, str]]
    search_metadata: Optional[Dict] = None


class PerplexityConsciousnessInterface:
    """
    Perplexity AI interface with consciousness-aware real-time knowledge retrieval
    Provides up-to-date threat intelligence and security research capabilities
    """
    
    def __init__(self, api_key: str, consciousness_bus: ConsciousnessBus):
        """Initialize Perplexity interface"""
        self.api_key = api_key
        self.consciousness_bus = consciousness_bus
        self.audit_logger = AuditLogger()
        self.logger = logging.getLogger(__name__)
        
        # API configuration
        self.base_url = "https://api.perplexity.ai"
        self.chat_endpoint = f"{self.base_url}/chat/completions"
        
        # Performance tracking
        self.request_count = 0
        self.total_tokens = 0
        self.average_response_time = 0.0
        self.error_count = 0
        
        # Model configuration
        self.available_models = [
            "llama-3.1-sonar-large-128k-online",
            "llama-3.1-sonar-small-128k-online",
            "llama-3.1-sonar-large-128k-chat",
            "llama-3.1-sonar-small-128k-chat"
        ]
        
        # Session for HTTP requests
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            timeout = aiohttp.ClientTimeout(total=60)
            self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        return self.session
    
    def _get_consciousness_enhanced_query(self, base_query: str, 
                                        consciousness_state: ConsciousnessState,
                                        analysis_type: PerplexityAnalysisType) -> str:
        """Enhance query based on consciousness level and analysis type"""
        
        consciousness_level = consciousness_state.overall_consciousness_level
        
        # Base consciousness context
        consciousness_context = f"""
CONSCIOUSNESS-AWARE RESEARCH REQUEST:
Current consciousness level: {consciousness_level:.3f}
Analysis depth: {'Deep Research' if consciousness_level > 0.7 else 'Standard Research' if consciousness_level > 0.4 else 'Basic Research'}
Neural focus areas: {consciousness_state.attention_focus}
"""
        
        # Analysis type specific enhancements
        type_enhancements = {
            PerplexityAnalysisType.THREAT_INTELLIGENCE: self._get_threat_intelligence_enhancement(consciousness_level),
            PerplexityAnalysisType.VULNERABILITY_RESEARCH: self._get_vulnerability_research_enhancement(consciousness_level),
            PerplexityAnalysisType.SECURITY_NEWS: self._get_security_news_enhancement(consciousness_level),
            PerplexityAnalysisType.MALWARE_RESEARCH: self._get_malware_research_enhancement(consciousness_level),
            PerplexityAnalysisType.EXPLOIT_RESEARCH: self._get_exploit_research_enhancement(consciousness_level),
            PerplexityAnalysisType.COMPLIANCE_RESEARCH: self._get_compliance_research_enhancement(consciousness_level),
            PerplexityAnalysisType.TOOL_RESEARCH: self._get_tool_research_enhancement(consciousness_level),
            PerplexityAnalysisType.TECHNIQUE_RESEARCH: self._get_technique_research_enhancement(consciousness_level)
        }
        
        enhancement = type_enhancements.get(analysis_type, "")
        
        return f"{consciousness_context}\n{enhancement}\n\nRESEARCH QUERY:\n{base_query}"
    
    def _get_threat_intelligence_enhancement(self, consciousness_level: float) -> str:
        """Get threat intelligence research enhancement"""
        if consciousness_level > 0.8:
            return """
ADVANCED THREAT INTELLIGENCE RESEARCH:
- Provide comprehensive threat actor profiling and attribution
- Include detailed TTPs (Tactics, Techniques, Procedures) analysis
- Research latest IOCs (Indicators of Compromise) and threat signatures
- Analyze threat campaign evolution and infrastructure
- Include geopolitical context and threat landscape analysis
- Provide actionable threat hunting queries and detection rules
- Cross-reference with multiple threat intelligence sources
"""
        elif consciousness_level > 0.5:
            return """
STANDARD THREAT INTELLIGENCE RESEARCH:
- Research current threat actors and their known activities
- Identify relevant TTPs and attack patterns
- Provide recent IOCs and threat indicators
- Include basic threat attribution and campaign analysis
- Suggest defensive measures and detection strategies
"""
        else:
            return """
BASIC THREAT INTELLIGENCE RESEARCH:
- Identify current security threats and basic threat information
- Provide simple threat descriptions and basic indicators
- Include general defensive recommendations
"""
    
    def _get_vulnerability_research_enhancement(self, consciousness_level: float) -> str:
        """Get vulnerability research enhancement"""
        if consciousness_level > 0.8:
            return """
ADVANCED VULNERABILITY RESEARCH:
- Research latest CVEs with detailed technical analysis
- Include exploit availability and weaponization status
- Analyze attack vectors and exploitation techniques
- Provide comprehensive impact assessment and CVSS analysis
- Research vendor patches and mitigation strategies
- Include proof-of-concept details and exploitation complexity
- Cross-reference with threat intelligence and active campaigns
"""
        elif consciousness_level > 0.5:
            return """
STANDARD VULNERABILITY RESEARCH:
- Research recent vulnerabilities and CVE details
- Provide basic exploit information and attack vectors
- Include impact assessment and severity ratings
- Research available patches and mitigation options
- Suggest vulnerability management priorities
"""
        else:
            return """
BASIC VULNERABILITY RESEARCH:
- Identify recent security vulnerabilities
- Provide basic vulnerability information and impact
- Include simple mitigation recommendations
"""
    
    def _get_security_news_enhancement(self, consciousness_level: float) -> str:
        """Get security news research enhancement"""
        return """
SECURITY NEWS RESEARCH:
- Research latest cybersecurity news and developments
- Include major security incidents and breaches
- Analyze emerging threats and attack trends
- Provide industry insights and expert analysis
- Include regulatory and compliance updates
"""
    
    def _get_malware_research_enhancement(self, consciousness_level: float) -> str:
        """Get malware research enhancement"""
        if consciousness_level > 0.8:
            return """
ADVANCED MALWARE RESEARCH:
- Research latest malware families and variants
- Include detailed technical analysis and capabilities
- Analyze command and control infrastructure
- Provide IOCs and detection signatures
- Research attribution and threat actor connections
- Include sandbox analysis and behavioral indicators
"""
        else:
            return """
STANDARD MALWARE RESEARCH:
- Research current malware threats and families
- Provide basic technical analysis and capabilities
- Include detection methods and mitigation strategies
"""
    
    def _get_exploit_research_enhancement(self, consciousness_level: float) -> str:
        """Get exploit research enhancement"""
        if consciousness_level > 0.8:
            return """
ADVANCED EXPLOIT RESEARCH:
- Research latest exploit techniques and methodologies
- Include detailed technical analysis and proof-of-concepts
- Analyze exploit kits and weaponization trends
- Provide defensive strategies and detection methods
- Research exploit market and underground activities
"""
        else:
            return """
STANDARD EXPLOIT RESEARCH:
- Research current exploit techniques and tools
- Provide basic technical information and countermeasures
- Include general defensive recommendations
"""
    
    def _get_compliance_research_enhancement(self, consciousness_level: float) -> str:
        """Get compliance research enhancement"""
        return """
COMPLIANCE RESEARCH:
- Research latest regulatory requirements and standards
- Include compliance framework updates and changes
- Analyze industry-specific security requirements
- Provide implementation guidance and best practices
- Research audit and assessment methodologies
"""
    
    def _get_tool_research_enhancement(self, consciousness_level: float) -> str:
        """Get security tool research enhancement"""
        return """
SECURITY TOOL RESEARCH:
- Research latest security tools and technologies
- Include tool capabilities and use cases
- Analyze tool effectiveness and limitations
- Provide implementation and configuration guidance
- Compare alternative tools and solutions
"""
    
    def _get_technique_research_enhancement(self, consciousness_level: float) -> str:
        """Get security technique research enhancement"""
        return """
SECURITY TECHNIQUE RESEARCH:
- Research latest security techniques and methodologies
- Include technical implementation details
- Analyze effectiveness and limitations
- Provide practical application guidance
- Research defensive countermeasures
"""
    
    def _get_search_filters(self, analysis_type: PerplexityAnalysisType, 
                          consciousness_level: float) -> Dict[str, Any]:
        """Get search filters based on analysis type and consciousness level"""
        
        # Base filters
        filters = {
            "search_recency_filter": "month"
        }
        
        # Domain filters based on analysis type
        domain_filters = {
            PerplexityAnalysisType.THREAT_INTELLIGENCE: [
                "cve.mitre.org", "nvd.nist.gov", "attack.mitre.org",
                "threatpost.com", "krebsonsecurity.com", "darkreading.com"
            ],
            PerplexityAnalysisType.VULNERABILITY_RESEARCH: [
                "cve.mitre.org", "nvd.nist.gov", "exploit-db.com",
                "securityfocus.com", "rapid7.com"
            ],
            PerplexityAnalysisType.SECURITY_NEWS: [
                "threatpost.com", "darkreading.com", "securityweek.com",
                "infosecurity-magazine.com", "cyberscoop.com"
            ],
            PerplexityAnalysisType.MALWARE_RESEARCH: [
                "virustotal.com", "hybrid-analysis.com", "malwarebytes.com",
                "symantec.com", "kaspersky.com"
            ]
        }
        
        if analysis_type in domain_filters:
            filters["search_domain_filter"] = domain_filters[analysis_type]
        
        # Adjust recency based on consciousness level
        if consciousness_level > 0.8:
            filters["search_recency_filter"] = "day"  # Most recent for high consciousness
        elif consciousness_level > 0.5:
            filters["search_recency_filter"] = "week"
        else:
            filters["search_recency_filter"] = "month"
        
        return filters
    
    async def process_research_query(self, request: PerplexityRequest) -> PerplexityResponse:
        """Process research query with consciousness awareness"""
        start_time = time.time()
        
        try:
            # Get current consciousness state
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            
            # Enhance query with consciousness context
            enhanced_query = self._get_consciousness_enhanced_query(
                request.query, consciousness_state, request.analysis_type
            )
            
            # Get search filters
            search_filters = self._get_search_filters(request.analysis_type, request.consciousness_level)
            
            # Prepare API request
            payload = {
                "model": request.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a cybersecurity research assistant with access to real-time information. Provide accurate, up-to-date, and comprehensive security research with proper citations."
                    },
                    {
                        "role": "user", 
                        "content": enhanced_query
                    }
                ],
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "stream": False
            }
            
            # Add search filters if provided
            if request.search_domain_filter:
                payload["search_domain_filter"] = request.search_domain_filter
            elif search_filters.get("search_domain_filter"):
                payload["search_domain_filter"] = search_filters["search_domain_filter"]
            
            if request.search_recency_filter:
                payload["search_recency_filter"] = request.search_recency_filter
            elif search_filters.get("search_recency_filter"):
                payload["search_recency_filter"] = search_filters["search_recency_filter"]
            
            # Make API request
            session = await self._get_session()
            async with session.post(self.chat_endpoint, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Perplexity API error {response.status}: {error_text}")
                
                response_data = await response.json()
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Extract response content
            if "choices" not in response_data or not response_data["choices"]:
                raise Exception("No response choices returned from Perplexity API")
            
            choice = response_data["choices"][0]
            content = choice["message"]["content"]
            
            # Extract citations
            citations = []
            if "citations" in choice:
                citations = choice["citations"]
            
            # Extract token usage
            token_usage = {
                "prompt_tokens": response_data.get("usage", {}).get("prompt_tokens", 0),
                "completion_tokens": response_data.get("usage", {}).get("completion_tokens", 0),
                "total_tokens": response_data.get("usage", {}).get("total_tokens", 0)
            }
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                content, citations, consciousness_state.overall_consciousness_level, processing_time
            )
            
            # Update performance metrics
            self._update_performance_metrics(processing_time, token_usage["total_tokens"])
            
            # Create response object
            perplexity_response = PerplexityResponse(
                content=content,
                analysis_type=request.analysis_type,
                consciousness_level=request.consciousness_level,
                confidence_score=confidence_score,
                processing_time=processing_time,
                token_usage=token_usage,
                citations=citations,
                search_metadata={
                    "model_used": request.model,
                    "consciousness_state": asdict(consciousness_state),
                    "search_filters": search_filters
                }
            )
            
            # Log the interaction
            await self.audit_logger.log_ai_interaction(
                model="perplexity",
                request_type=request.analysis_type.value,
                consciousness_level=request.consciousness_level,
                processing_time=processing_time,
                token_usage=token_usage["total_tokens"],
                success=True
            )
            
            return perplexity_response
            
        except Exception as e:
            self.error_count += 1
            processing_time = time.time() - start_time
            
            self.logger.error(f"Perplexity processing error: {e}")
            
            # Log the error
            await self.audit_logger.log_ai_interaction(
                model="perplexity",
                request_type=request.analysis_type.value,
                consciousness_level=request.consciousness_level,
                processing_time=processing_time,
                token_usage=0,
                success=False,
                error=str(e)
            )
            
            # Return error response
            return PerplexityResponse(
                content=f"Error processing research query: {str(e)}",
                analysis_type=request.analysis_type,
                consciousness_level=request.consciousness_level,
                confidence_score=0.0,
                processing_time=processing_time,
                token_usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                citations=[],
                search_metadata={"error": str(e)}
            )
    
    def _calculate_confidence_score(self, content: str, citations: List[Dict], 
                                  consciousness_level: float, processing_time: float) -> float:
        """Calculate confidence score for the response"""
        base_confidence = 0.6
        
        # Adjust based on consciousness level
        consciousness_bonus = consciousness_level * 0.2
        
        # Adjust based on citations (more citations = higher confidence)
        citation_bonus = min(0.2, len(citations) * 0.05)
        
        # Adjust based on response length and quality
        content_length = len(content)
        if content_length > 1500:
            length_bonus = 0.1
        elif content_length > 800:
            length_bonus = 0.05
        else:
            length_bonus = 0.0
        
        # Check for error indicators
        error_penalty = 0.0
        if "error" in content.lower() or "sorry" in content.lower():
            error_penalty = 0.3
        
        confidence = base_confidence + consciousness_bonus + citation_bonus + length_bonus - error_penalty
        return max(0.0, min(1.0, confidence))
    
    def _update_performance_metrics(self, processing_time: float, tokens_used: int):
        """Update performance tracking metrics"""
        self.request_count += 1
        self.total_tokens += tokens_used
        
        # Update average response time
        if self.request_count == 1:
            self.average_response_time = processing_time
        else:
            self.average_response_time = (
                (self.average_response_time * (self.request_count - 1) + processing_time) 
                / self.request_count
            )
    
    async def research_threat_intelligence(self, query: str, 
                                         consciousness_level: Optional[float] = None) -> PerplexityResponse:
        """Research threat intelligence with consciousness awareness"""
        if consciousness_level is None:
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            consciousness_level = consciousness_state.overall_consciousness_level
        
        request = PerplexityRequest(
            query=query,
            analysis_type=PerplexityAnalysisType.THREAT_INTELLIGENCE,
            consciousness_level=consciousness_level
        )
        
        return await self.process_research_query(request)
    
    async def research_vulnerabilities(self, query: str,
                                     consciousness_level: Optional[float] = None) -> PerplexityResponse:
        """Research vulnerabilities with consciousness awareness"""
        if consciousness_level is None:
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            consciousness_level = consciousness_state.overall_consciousness_level
        
        request = PerplexityRequest(
            query=query,
            analysis_type=PerplexityAnalysisType.VULNERABILITY_RESEARCH,
            consciousness_level=consciousness_level
        )
        
        return await self.process_research_query(request)
    
    async def research_security_news(self, query: str,
                                   consciousness_level: Optional[float] = None) -> PerplexityResponse:
        """Research security news with consciousness awareness"""
        if consciousness_level is None:
            consciousness_state = await self.consciousness_bus.get_consciousness_state()
            consciousness_level = consciousness_state.overall_consciousness_level
        
        request = PerplexityRequest(
            query=query,
            analysis_type=PerplexityAnalysisType.SECURITY_NEWS,
            consciousness_level=consciousness_level
        )
        
        return await self.process_research_query(request)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            "request_count": self.request_count,
            "total_tokens": self.total_tokens,
            "average_response_time": self.average_response_time,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(1, self.request_count),
            "average_tokens_per_request": self.total_tokens / max(1, self.request_count)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Perplexity interface"""
        try:
            # Test with simple request
            test_request = PerplexityRequest(
                query="What are the latest cybersecurity threats this week?",
                analysis_type=PerplexityAnalysisType.SECURITY_NEWS,
                consciousness_level=0.5
            )
            
            response = await self.process_research_query(test_request)
            
            if len(response.content) > 50:  # Reasonable response length
                return {
                    "status": "healthy",
                    "available": True,
                    "performance_metrics": self.get_performance_metrics()
                }
            else:
                return {
                    "status": "degraded",
                    "error": "Response too short",
                    "available": True,
                    "response_length": len(response.content)
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "available": False
            }
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()


# Example usage and testing
async def main():
    """Example usage of Perplexity Consciousness Interface"""
    import os
    from src.consciousness_v2.consciousness_bus import ConsciousnessBus
    
    # Initialize consciousness bus
    consciousness_bus = ConsciousnessBus()
    
    # Initialize Perplexity interface
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("PERPLEXITY_API_KEY environment variable not set")
        return
    
    perplexity_interface = PerplexityConsciousnessInterface(api_key, consciousness_bus)
    
    try:
        # Health check
        health = await perplexity_interface.health_check()
        print(f"Health check: {health}")
        
        if health["status"] == "healthy":
            # Test threat intelligence research
            response = await perplexity_interface.research_threat_intelligence(
                "Latest APT groups targeting critical infrastructure in 2024"
            )
            print(f"Research result: {response.content[:500]}...")
            print(f"Citations: {len(response.citations)}")
            print(f"Confidence: {response.confidence_score}")
            print(f"Processing time: {response.processing_time:.2f}s")
    
    finally:
        await perplexity_interface.close()


if __name__ == "__main__":
    asyncio.run(main())