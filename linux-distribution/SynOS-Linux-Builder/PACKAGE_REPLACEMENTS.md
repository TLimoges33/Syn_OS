# SynOS Package Replacement Strategy

## Missing Packages Analysis & Viable Replacements

### Category 1: Firmware (Debian 12 non-free-firmware)
| Missing Package | Replacement | Status |
|----------------|-------------|---------|
| firmware-bnx2x | firmware-bnx2 | Available in non-free-firmware |
| firmware-brcm80211 | firmware-brcm80211 | Available in non-free-firmware |
| firmware-ipw2x00 | firmware-ipw2x00 | Available in non-free-firmware |
| firmware-iwlwifi | firmware-iwlwifi | Available in non-free-firmware |
| firmware-libertas | firmware-libertas | Available in non-free-firmware |
| firmware-ralink | firmware-ralink | Available in non-free-firmware |
| firmware-zd1211 | zd1211-firmware | Available in non-free-firmware |

**Fix:** All firmware packages exist, just need non-free-firmware enabled (already done)

### Category 2: Tools in Debian (Wrong names or need research)
| Missing Package | Debian Replacement | Notes |
|----------------|-------------------|-------|
| nikto | nikto | **Available in Debian** - web vulnerability scanner |
| kismet | kismet | **Available in Debian** - wireless sniffer |
| volatility | volatility3 | **Available in Debian** - memory forensics |
| radare2 | radare2 | **Available in Debian** - reverse engineering |
| ghidra | ghidra | **Available in Debian backports** - NSA reverse engineering |
| zenmap | nmap | Zenmap removed from Debian, use nmap CLI |
| awk | gawk (or mawk) | Already installed, wrong package name |
| unrar | unrar-free | Available in Debian |
| rar | rar | Available in non-free |

### Category 3: ParrotOS/Kali-Specific Tools (Need ParrotOS repos)
| Missing Package | ParrotOS Package | Alternative |
|----------------|-----------------|-------------|
| metasploit-framework | metasploit-framework | **Only in Parrot/Kali repos** - penetration testing framework |
| set | set | **Only in Kali/Parrot** - Social Engineering Toolkit |
| theharvester | theharvester | **Only in Kali/Parrot** - OSINT tool |
| maltego | maltego | **Proprietary** - Use maltego-ce (community edition) |

### Category 4: Not Packaged (Need Alternative Approach)
| Missing Package | Viable Alternative | Installation Method |
|----------------|-------------------|-------------------|
| mimikatz | pypykatz | Python alternative: `pip install pypykatz` |
| powersploit | empire | PowerShell Empire framework in Parrot repos |
| spiderfoot | spiderfoot | Python tool: `pip install spiderfoot` |
| cuckoo | cuckoo3 | Manual install: Docker or pip |
| remnux | N/A | REMnux is a distro, not a package - skip |

## Recommended Strategy

### Phase 1: Use ParrotOS Debootstrap (HYBRID SOLUTION)
Instead of vanilla Debian, use ParrotOS as the debootstrap base:

```bash
lb config \
    --mode debian \
    --distribution parrot \
    --parent-mirror-bootstrap "http://deb.parrot.sh/parrot/" \
    --parent-mirror-binary "http://deb.parrot.sh/parrot/" \
    --archive-areas "main contrib non-free non-free-firmware"
```

This gives us:
- ✅ All ParrotOS security tools pre-configured
- ✅ metasploit-framework, set, theharvester work out of box
- ✅ Firmware packages available
- ✅ Proper security tool versions

### Phase 2: Clean Package Lists
Remove packages that are:
1. **Not packaged anywhere:** remnux
2. **Windows-only:** mimikatz, powersploit (use alternatives)
3. **Already included in base:** awk
4. **Deprecated:** zenmap (use nmap)

### Phase 3: Add Python-Based Alternatives
Create post-install hook to install Python tools:
```bash
pip3 install pypykatz spiderfoot volatility3
```

## Implementation Plan

1. **Modify build script** to use ParrotOS debootstrap
2. **Update package lists** with correct names
3. **Create pip-install hook** for Python tools
4. **Test build** with hybrid approach
