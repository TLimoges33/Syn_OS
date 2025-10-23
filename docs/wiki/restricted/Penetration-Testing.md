# 🔍 Penetration Testing Guide

**Methodology**: Industry-standard pentesting  
**Frameworks**: OWASP, PTES, OSSTMM  
**Compliance**: PCI DSS, HIPAA ready

---

## Pentest Phases

### 1. Planning & Scoping
- Define objectives
- Rules of engagement
- Legal authorization
- Timeline and deliverables

### 2. Reconnaissance
- Passive information gathering
- Active scanning
- Service enumeration
- Vulnerability identification

### 3. Exploitation
- Attempt exploitation
- Gain initial access
- Capture evidence
- Document findings

### 4. Post-Exploitation
- Privilege escalation
- Lateral movement
- Data access
- Persistence

### 5. Reporting
- Executive summary
- Technical findings
- Risk ratings
- Remediation recommendations

---

## Report Template

```markdown
# Penetration Test Report

## Executive Summary
Company X penetration test identified:
- 5 Critical vulnerabilities
- 12 High-risk issues
- 20 Medium-risk findings

Overall risk: HIGH

## Methodology
- Black box testing
- External/Internal
- No credentials provided

## Findings

### 1. SQL Injection - CRITICAL
**Risk**: 10/10  
**Description**: Login form vulnerable  
**Impact**: Database compromise  
**Evidence**: [Screenshots]  
**Remediation**: Use prepared statements

[Continue for all findings...]

## Recommendations
1. Immediate: Patch SQL injection
2. Short-term: Implement WAF
3. Long-term: Security training
```

---

## Tool Workflow

```bash
# 1. Reconnaissance
nmap -sV -sC -oA recon target.com

# 2. Vulnerability scanning
nmap --script vuln target.com

# 3. Exploitation
msfconsole
use exploit/...

# 4. Post-exploitation
run post/...

# 5. Report generation
synos-report generate \
  --workspace pentest-acme \
  --template professional \
  --format pdf
```

---

**Certifications Aligned**:
- OSCP (Offensive Security Certified Professional)
- CEH (Certified Ethical Hacker)
- GPEN (GIAC Penetration Tester)
