### **Cybersecurity Study Plan: Phase 3 \- Penetration Testing Specialization**

**Goal:** Develop the specialized knowledge, practical skills, and mindset required for a career in penetration testing. Focus on offensive techniques, methodologies, and industry-standard tools and certifications.

**Approximate Duration:** 6-12+ Months (highly dependent on prior experience and dedication)

#### **Topics to Study:**

1. **Penetration Testing Methodology:**  
   * **Frameworks:** Understand common frameworks like PTES (Penetration Testing Execution Standard) and OSSTMM (Open Source Security Testing Methodology Manual) – focus on the phases.  
   * **Phases:**  
     * **Planning & Scoping:** Defining objectives, rules of engagement.  
     * **Reconnaissance/Information Gathering:** Passive (OSINT, Shodan) and Active (DNS enumeration, Nmap scanning).  
     * **Scanning & Vulnerability Analysis:** Identifying live hosts, open ports, services, and potential vulnerabilities (Nmap scripts, Nessus).  
     * **Exploitation:** Gaining initial access by leveraging vulnerabilities (Metasploit, manual exploits).  
     * **Post-Exploitation:** Privilege escalation, lateral movement, maintaining access, gathering data/flags.  
     * **Reporting:** Documenting findings, impact, and remediation steps clearly.  
2. **Advanced Web Application Security:**  
   * **Deep Dive into OWASP Top 10:** Move beyond awareness to understanding *how* to find and exploit these vulnerabilities (SQL Injection, Cross-Site Scripting (XSS), Server-Side Request Forgery (SSRF), Insecure Deserialization, etc.).  
   * **Burp Suite Mastery:** Utilize advanced features like Intruder for fuzzing/brute-forcing, Repeater for manual request manipulation, Sequencer for analyzing session token randomness, Decoder for data transformation.  
   * **API Testing:** Learn techniques for testing REST and GraphQL APIs.  
3. **Exploitation Techniques:**  
   * **Metasploit Framework:** Understand the architecture (modules, payloads, encoders), using msfconsole, searching for exploits (search), setting options (set RHOSTS, set LHOST, set PAYLOAD), running exploits (exploit, run), basic Meterpreter usage (sysinfo, getuid, ps, migrate, shell).  
   * **Manual Exploitation:** Learn to find, modify, and use public exploits (e.g., from Exploit-DB). Understand basic buffer overflow concepts (stack, registers, shellcode) – crucial for OSCP.  
   * **Password Attacks:** Offline cracking (John the Ripper, Hashcat), Online brute-forcing/password spraying (Hydra, Medusa).  
4. **Active Directory (AD) Security:**  
   * **Core Concepts:** Domains, Forests, Kerberos authentication, NTLM, LDAP.  
   * **Enumeration:** Finding domain controllers, users, groups, trusts (PowerShell tools like PowerView, BloodHound).  
   * **Common Attacks:** Pass-the-Hash (PtH), Pass-the-Ticket (PtT), Kerberoasting, AS-REP Roasting, LLMNR/NBT-NS poisoning.  
   * **Tools:** Mimikatz, BloodHound, Impacket suite, PowerSploit/PowerView.  
   * *Relevance:* Crucial for internal network penetration tests and certifications like PNPT.  
5. **Kali Linux Mastery:**  
   * **Environment:** Become highly proficient navigating and using the Kali Linux environment.  
   * **Tool Familiarity:** Know *which* tool to use for specific tasks during a pentest (e.g., gobuster/dirb for web directory brute-forcing, sqlmap for SQL injection, searchsploit for finding exploits, enum4linux for Windows/Samba enumeration).  
   * **Customization & Updates:** Keep the system updated (sudo apt update && sudo apt full-upgrade \-y), potentially customize with personal scripts/tools.  
6. **Reporting:**  
   * **Structure:** Executive Summary, Technical Details (Vulnerability, Steps to Reproduce, Evidence), Risk Rating (CVSS), Remediation Recommendations.  
   * **Clarity & Actionability:** Write reports that are easy for both technical and non-technical audiences to understand and act upon. (Remember: "Customers pay for the report, not the pentest itself.")

#### **Tool Guides & How to Use Them:**

1. **Burp Suite (Community/Pro):**  
   * **Focus:** Go beyond basic scanning. Use Repeater extensively to manually test parameters and payloads. Learn Intruder attack types (Sniper, Battering Ram, Pitchfork, Cluster Bomb) for targeted fuzzing. Explore extensions in the BApp Store.  
   * **Resource:** [PortSwigger Web Security Academy](https://portswigger.net/web-security) is essential.  
2. **Metasploit Framework (msfconsole):**  
   * **Workflow:** use \<exploit\_module\>, show options, set \<option\> \<value\>, show payloads, set PAYLOAD \<payload\_name\>, exploit.  
   * **Meterpreter:** Practice basic commands (help, sysinfo, getuid, ps, migrate \<pid\>, upload, download, execute, shell).  
   * **Resources:** [Metasploit Unleashed](https://www.offensive-security.com/metasploit-unleashed/) (Free course by Offensive Security), TryHackMe rooms.  
3. **Kali Linux Tools:**  
   * **Approach:** Learn tools contextually within the pentesting phases.  
   * **Recon:** nmap, dnsenum, theHarvester, sublist3r.  
   * **Scanning/Enumeration:** nmap (advanced scripts), enum4linux, smbclient, gobuster, dirsearch, nikto.  
   * **Exploitation:** metasploit-framework, searchsploit, sqlmap, hydra, john, hashcat.  
   * **Post-Exploitation:** mimikatz (on Windows target), linpeas.sh/winPEAS.bat, PowerSploit.  
   * **Practice:** Use these tools in CTFs and lab environments like TryHackMe and HackTheBox.  
4. **Active Directory Tools:**  
   * **BloodHound:** Install collector (SharpHound.ps1/.exe) on a compromised Windows host, run it, import data into BloodHound GUI on Kali. Analyze attack paths.  
   * **Impacket:** Collection of Python scripts (psexec.py, smbclient.py, GetNPUsers.py, GetUserSPNs.py). Learn their command-line usage.  
   * **PowerView/PowerSploit:** Load PowerShell modules on a compromised Windows host (Import-Module .\\PowerView.ps1) and use functions (Get-NetUser, Get-NetGroup, Invoke-Kerberoast).  
5. **Reporting Tools (Dradis, Ghostwriter, Serpico, etc.):**  
   * **Purpose:** These tools help organize findings, manage evidence, and generate report templates.  
   * **Focus:** While tools help, prioritize learning *what* constitutes a good report. Practice writing detailed findings for lab machines.  
   * **Resources:** Explore documentation for tools like [Dradis Framework](https://dradisframework.com/), [Ghostwriter](https://www.ghostwriter.wiki/).

#### **Recommended Resources:**

* **Hands-on Labs (Essential):**  
  * [TryHackMe](https://tryhackme.com/): Offensive Pentesting Path, specific pathways (Jr Penetration Tester, Red Teaming), various rooms/networks.  
  * [HackTheBox](https://www.hackthebox.com/): Main labs (Active/Retired Machines), Academy (CPTS path), Pro Labs.  
  * [Offensive Security Proving Grounds (PG)](https://www.offensive-security.com/labs/): Practice labs similar to OSCP exam machines.  
* **Certifications & Training:**  
  * **eJPT (INE):** Good entry-level practical cert.  
  * **PenTest+ (CompTIA):** Theory \+ practical questions, good HR filter.  
  * **PNPT (TCM Security):** Practical, AD-focused, well-regarded.  
  * **CPTS (Hack The Box Academy):** Comprehensive practical training and exam.  
  * **OSCP (Offensive Security):** The industry standard, very challenging, requires significant lab time ("Try Harder" mindset).  
* **Web Security:**  
  * [PortSwigger Web Security Academy](https://portswigger.net/web-security) (Crucial).  
* **Exploit Development (for OSCP/Advanced):**  
  * [Tib3rius' PEH Course (Udemy)](https://www.udemy.com/course/windows-privilege-escalation/) (Privilege Escalation focus)  
  * Basic Buffer Overflow tutorials (many available online, e.g., TryHackMe Buffer Overflow Prep room).  
* **Portfolio:**  
  * GitHub: Share scripts, notes, tool configurations.  
  * Blog/Website: Write detailed write-ups for retired CTF machines (respect platform rules).

#### **Big Picture Tie-back:**

This phase is about adopting an offensive mindset and mastering the practical skills to simulate real-world attacks. Success requires significant dedication, hands-on practice (labs are non-negotiable), and often pursuing challenging certifications like the OSCP, PNPT, or CPTS. Building a portfolio showcasing your skills is vital for breaking into this competitive field. Networking and report writing are also critical soft skills.