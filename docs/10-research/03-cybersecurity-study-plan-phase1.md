### **Cybersecurity Study Plan: Phase 1 \- Foundations**

**Goal:** Build a strong base in IT fundamentals, networking concepts, general security principles, and basic operating system knowledge (Windows & Linux). This foundation is crucial before diving into specialized security tools and techniques.

**Approximate Duration:** 1-3 Months

#### **Topics to Study:**

1. **Basic IT Fundamentals:**  
   **Hardware:** Understand components like:  
   * CPU,   
   * RAM,   
   * Hard Drives (HDD/SSD),   
   * Network Interface Cards (NICs).  
   * **Software:** Differentiate between Operating Systems (OS), applications, drivers, and firmware.

   **Operating System Concepts:** Learn about 

   * processes,   
   * threads,   
   * memory management,   
   * file systems (NTFS, FAT32, ext4), permissions,  
   * user accounts.

2. **Networking Fundamentals:**  
   * **OSI & TCP/IP Models:** Understand the layers and how data travels across networks.

   **IP Addressing:** Learn 

   * IPv4,   
   * IPv6,   
   * subnetting,   
   * private vs. public IP ranges.

   **Core Protocols:** Grasp the function of 

   * TCP,   
   * UDP,   
   * HTTP,   
   * HTTPS,   
   * DNS,   
   * DHCP,   
   * ICMP,   
   * FTP,   
   * SSH.

   **Network Devices:** Know the roles of 

   * routers,   
   * switches,   
   * firewalls,   
   * access points.  
   * *Resource Focus:* CompTIA Network+ 

3. **General Security Principles:**  
   * **CIA Triad:**   
   * Confidentiality,   
   * Integrity,   
   * Availability.  
   * **Threats & Vulnerabilities:** Understand malware types (viruses, worms, ransomware), social engineering, phishing, common software flaws.

**Risk Management:** Concepts of 

* risk,   
  * threat,   
  * vulnerability,   
  * likelihood,   
  * impact,   
  * basic mitigation strategies.

  **Authentication & Authorization:** Passwords, 

  Multi-Factor Authentication (MFA), Access Control models.

  * *Resource Focus:* CompTIA Security+ 

4. **Windows Fundamentals:**  
   * **Core Concepts:** Understand the   
   * Windows Registry,   
   * Event Logs,   
   * Services,   
   * Processes, and   
   * basic command prompt/PowerShell 

   **Monitoring Tools (Introduction):**

     * **Sysmon:** Learn its purpose – detailed system activity logging beyond standard Windows logs.  
     * **Procmon (Process Monitor):** Understand its use – real-time monitoring of file system, registry, and process/thread activity.

5. **Linux Fundamentals:**  
   * **Why Linux?** Many security tools (Kali Linux, Security Onion) and servers run on Linux. Command-line proficiency is essential.  
   * **Distributions:** Be aware of major families (Debian/Ubuntu, Red Hat/Fedora/CentOS). Start with a user-friendly one like Ubuntu for learning.

   **File System Hierarchy:** Understand the layout (/, /etc, /home, /var, /tmp, etc.).

   **Basic Commands:** Practice essential commands

   **Permissions:** Learn about 

   * read (r),   
   * write (w),   
   * execute (x)   
   * permissions for user, group, and others (chmod, chown).  
   * **Package Management:** Understand apt (Debian/Ubuntu) or yum/dnf (Red Hat based) for installing/updating software.  
   * **Users & Groups:** Basic user management (adduser, userdel, passwd).

#### **Tool Guides & How to Use Them:**

1. **Sysmon & Procmon (Windows):**  
   * **Approach:** Don't aim to master them yet. Understand *what* they show.  
   * **Sysmon:** Install it (requires configuration). Observe the types of events it logs to the Windows Event Viewer (e.g., process creation, network connections). Official Docs: [Sysinternals Sysmon](https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon)  
   * **Procmon:** Download and run it. Observe the sheer volume of activity. Try filtering by process name or operation type (e.g., Registry activity). Official Docs: [Sysinternals Process Monitor](https://docs.microsoft.com/en-us/sysinternals/downloads/procmon)  
   * **Goal:** Appreciate the level of detail available for system monitoring on Windows.  
2. **Linux Command Line:**  
   * **Setup:** Install a Linux distribution (like Ubuntu) in a Virtual Machine (VM) using VirtualBox (free) or VMware Player/Workstation. This provides a safe environment to practice.  
   * **Practice:** Open the terminal and work through these commands:  
     * pwd: Print working directory (shows where you are).  
     * ls, ls \-la: List directory contents (long format shows permissions).  
     * cd \<directory\>: Change directory (cd .. goes up one level).  
     * mkdir \<name\>: Create a directory.  
     * rmdir \<name\>: Remove an empty directory.  
     * touch \<filename\>: Create an empty file.  
     * cp \<source\> \<destination\>: Copy files/directories.  
     * mv \<source\> \<destination\>: Move or rename files/directories.  
     * rm \<filename\>: Remove a file (rm \-r \<directory\> removes directory and contents \- **use with caution\!**).  
     * cat \<filename\>: Display file content.  
     * less \<filename\>: View file content page by page (press 'q' to quit).  
     * head/tail \<filename\>: View beginning/end of a file.  
     * grep \<pattern\> \<filename\>: Search for text within a file.  
     * find \<directory\> \-name \<filename\>: Search for files.  
     * man \<command\>: View the manual page for a command.  
     * sudo \<command\>: Run a command with administrator privileges.  
     * apt update, apt upgrade, apt install \<package\>: Manage software (Ubuntu/Debian).  
     * chmod \<permissions\> \<filename\>: Change file permissions (e.g., chmod 755 script.sh).  
   * **Goal:** Become comfortable navigating and managing files/directories via the command line.

#### **Recommended Resources:**

* **Certifications (Study Material):**  
  * CompTIA A+, Network+, Security+ Official Study Guides or reputable video courses (e.g., Professor Messer on YouTube \- free, Jason Dion Training, Mike Meyers).  
  * ISC2 Certified in Cybersecurity (CC): Check the [ISC2 website](https://www.isc2.org/Certifications/CC) for free training offers.  
* **Hands-on Practice:**  
  * [TryHackMe](https://tryhackme.com/): Start with introductory learning paths like "Pre Security" and Linux fundamentals rooms.  
* **Virtualization:**  
  * [Oracle VirtualBox](https://www.virtualbox.org/)  
  * [VMware Workstation Player](https://www.vmware.com/products/workstation-player.html)  
* **Linux Learning:**  
  * [Linux Journey](https://linuxjourney.com/)  
  * [The Linux Command Line](http://linuxcommand.org/tlcl.php) (Free book)

#### **Big Picture Tie-back:**

This phase is about building the bedrock. Without understanding how computers, networks, and operating systems function, you cannot effectively secure them. Mastering these fundamentals will make learning the tools and techniques in later phases much easier and more meaningful.