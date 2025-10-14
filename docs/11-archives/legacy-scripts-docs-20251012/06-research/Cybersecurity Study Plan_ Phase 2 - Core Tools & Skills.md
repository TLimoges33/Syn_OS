### **Cybersecurity Study Plan: Phase 2 \- Core Tools & Skills**

**Goal:** Gain practical, hands-on experience with essential cybersecurity tools used for network analysis, scanning, log management, and automation. Develop foundational scripting skills.

**Approximate Duration:** 3-6 Months

#### **Topics to Study:**

1. **Network Analysis (Wireshark):**  
   * **Capturing Traffic:** Learn how to select interfaces and start packet captures.  
   * **Filtering:** Master display filters to isolate specific traffic (e.g., by IP, port, protocol).  
   * **Protocol Analysis:** Understand how to examine headers and data for common protocols (HTTP, DNS, TCP, UDP, ICMP).  
   * **Stream Following:** Learn to reconstruct TCP/UDP conversations to understand application flows.  
2. **Scanning & Enumeration (Nmap, Nessus):**  
   * **Nmap:**  
     * **Scan Types:** Understand different scan techniques (TCP SYN \-sS, Connect \-sT, UDP \-sU).  
     * **Target Specification:** Learn how to define single targets, ranges, and lists.  
     * **Service & Version Detection (-sV):** Identify services running on open ports.  
     * **OS Detection (-O):** Attempt to identify the target operating system.  
     * **Scripting Engine (-sC, \--script):** Use Nmap scripts for basic vulnerability checks and further enumeration.  
     * **Output Formats:** Save scan results (-oN, \-oX, \-oG).  
   * **Nessus:**  
     * **Concept:** Understand its role as a comprehensive vulnerability scanner.  
     * **Setup:** Install Nessus Essentials (free version for limited IPs).  
     * **Scan Policies:** Learn about different scan templates (e.g., Basic Network Scan).  
     * **Running Scans:** Configure and launch scans against target IPs.  
     * **Interpreting Results:** Understand vulnerability ratings (CVSS scores), descriptions, and remediation advice.  
3. **Security Information & Event Management (SIEM):**  
   * **Core Concepts:** Log aggregation, normalization, correlation rules, alerting, dashboarding.  
   * **Security Onion:**  
     * **Setup:** Build a home lab environment (as suggested in the source doc).  
     * **Components:** Understand the roles of tools within the suite (e.g., Wazuh/Suricata for alerts, Elasticsearch/Logstash for logs, Kibana for visualization).  
     * **Usage:** Practice navigating dashboards, searching logs, investigating alerts.  
   * **Splunk (Optional/If Accessible):**  
     * **Concept:** Powerful platform for searching, monitoring, and analyzing machine data.  
     * **Basic SPL (Search Processing Language):** Learn fundamental search commands (index=, sourcetype=, | table, | stats count by \<field\>).  
     * **Data Onboarding:** Understand how data gets into Splunk (e.g., via forwarders).  
4. **Scripting (Python & PowerShell):**  
   * **Goal:** Automate repetitive tasks, parse logs, interact with APIs.  
   * **Python:**  
     * **Basics:** Syntax, data types, loops, functions, file I/O.  
     * **Relevant Libraries:** os (interacting with OS), sys (system parameters), requests (HTTP requests), socket (networking), re (regular expressions).  
     * **Use Cases:** Write simple port scanners, automate file checks, parse log data.  
   * **PowerShell (Windows):**  
     * **Cmdlets:** Learn basic commands for system administration (e.g., Get-Process, Get-Service, Get-EventLog, Invoke-WebRequest).  
     * **Scripting:** Combine cmdlets into scripts (.ps1 files) for automation.  
     * **Use Cases:** Query system information, manage Windows services/processes, automate user tasks.  
5. **Web Application Security Basics:**  
   * **OWASP Top 10:** Become familiar with the most common web vulnerabilities (e.g., Injection, Broken Authentication, XSS).  
   * **Proxy Tools (Burp Suite Community / OWASP ZAP):**  
     * **Proxy Setup:** Configure your browser to route traffic through the tool.  
     * **Spidering/Crawling:** Automatically discover website content.  
     * **Basic Scanning:** Run automated scans to identify potential vulnerabilities.  
     * **Intercepting:** View and modify HTTP requests/responses manually.

#### **Tool Guides & How to Use Them:**

1. **Wireshark:**  
   * **Installation:** Download from [wireshark.org](https://www.wireshark.org/).  
   * **Getting Started:** Select your network interface (Ethernet/Wi-Fi) and click Start. Observe traffic.  
   * **Filtering Practice:** Use the display filter bar. Try: ip.addr \== \<some\_ip\>, tcp.port \== 80, dns, http. Combine filters with && (and) or || (or).  
   * **Analysis:** Right-click a packet and choose "Follow \> TCP Stream" (or UDP/TLS Stream) to see the conversation.  
   * **Resources:** [Wireshark User's Guide](https://www.wireshark.org/docs/wsug_html_chunked/), numerous online tutorials, sample PCAPs from sites like [PacketTotal](https://packettotal.com/).  
2. **Nmap/Zenmap:**  
   * **Installation:** Download from [nmap.org](https://nmap.org/) (Nmap is command-line, Zenmap is the GUI). Often pre-installed on Kali Linux.  
   * **Basic Scans (Command Line):**  
     * nmap \<target\_ip\> (Basic port scan)  
     * nmap \-sS \<target\_ip\> (SYN Scan \- often faster/stealthier)  
     * nmap \-sV \-O \<target\_ip\> (Service/Version and OS detection)  
     * nmap \-A \<target\_ip\> (Aggressive scan \- includes \-sV, \-O, \-sC, traceroute)  
     * nmap \-p 1-100 \<target\_ip\> (Scan specific ports)  
     * nmap \-iL targets.txt \-oN output.txt (Scan targets from file, save output)  
   * **Zenmap:** Provides a GUI to build commands and view results visually. Good for beginners.  
   * **Resources:** [Nmap Official Documentation](https://nmap.org/docs.html).  
3. **Nessus Essentials:**  
   * **Installation:** Register and download from [Tenable](https://www.tenable.com/products/nessus/nessus-essentials). Follow installation instructions.  
   * **Usage:** Access via web browser. Create a "New Scan" \-\> "Basic Network Scan". Enter target IPs, save, and launch. Review completed scans under "My Scans". Click vulnerabilities for details.  
   * **Resources:** [Nessus Essentials Documentation](https://docs.tenable.com/nessus/Essentials/).  
4. **Security Onion:**  
   * **Setup:** Requires dedicated hardware or a powerful VM. Follow the official [Security Onion Documentation](https://docs.securityonion.net/en/latest/) carefully for installation.  
   * **Exploration:** Once running, access the web interface. Explore Kibana dashboards, look at Suricata/Wazuh alerts, try basic searches in the "Hunt" interface.  
   * **Goal:** Understand how logs and alerts are centralized and visualized in a SIEM-like environment.  
5. **Splunk Free/Trial:**  
   * **Installation:** Download from [splunk.com](https://www.splunk.com/).  
   * **Adding Data:** Configure a Universal Forwarder on another machine or use "Add Data" in the UI to upload files/monitor local logs.  
   * **Searching:** Use the Search & Reporting app. Try basic searches like index=\* | stats count by sourcetype.  
   * **Resources:** [Splunk Tutorials](https://docs.splunk.com/Documentation/Splunk/latest/SearchTutorial/WelcometotheSearchTutorial).  
6. **Python/PowerShell:**  
   * **Setup:** Python is usually pre-installed on Linux/macOS; download from [python.org](https://www.python.org/) for Windows. PowerShell is built into modern Windows. Use an IDE like VS Code for easier scripting.  
   * **Learning:** Focus on practical tasks. Find beginner scripting tutorials related to cybersecurity (e.g., "Python for Cybersecurity", "PowerShell for Pentesters"). Start small (e.g., script to ping a list of hosts).  
   * **Resources:** [Automate the Boring Stuff with Python](https://automatetheboringstuff.com/), [Microsoft Learn PowerShell](https://docs.microsoft.com/en-us/powershell/scripting/learn/ps101/00-introduction?view=powershell-7.2).  
7. **OWASP ZAP / Burp Suite Community:**  
   * **Installation:** Download ZAP from [owasp.org](https://www.zaproxy.org/) or Burp Community from [portswigger.net](https://portswigger.net/burp/communitydownload).  
   * **Proxy Setup:** Configure your browser's proxy settings (e.g., FoxyProxy extension) to point to the tool (usually 127.0.0.1 port 8080). Install the tool's CA certificate in your browser.  
   * **Basic Usage:** Manually browse a target web application. Observe the traffic in the tool's HTTP History tab. Try the "Attack" \-\> "Spider" function (ZAP) or Target \-\> Site map (Burp). Run an "Active Scan" (ZAP) or select host \-\> "Scan" (Burp) on a test site.  
   * **Resources:** [OWASP ZAP Documentation](https://www.zaproxy.org/documentation/), [PortSwigger Web Security Academy](https://portswigger.net/web-security).

#### **Recommended Resources:**

* Tool Documentation (linked above).  
* [TryHackMe](https://tryhackme.com/): Rooms dedicated to Wireshark, Nmap, Nessus, Burp Suite, Python, Powershell.  
* [HackTheBox](https://www.hackthebox.com/): Labs often require proficiency with these tools.  
* [Security Onion Documentation](https://docs.securityonion.net/en/latest/)  
* [PortSwigger Web Security Academy](https://portswigger.net/web-security)

#### **Big Picture Tie-back:**

This phase is about getting your hands dirty. You're moving from theoretical knowledge to practical application. Proficiency with these core tools is essential for many cybersecurity roles, including SOC analysts, vulnerability analysts, and is a prerequisite for penetration testing. Scripting skills learned here will significantly boost your efficiency.