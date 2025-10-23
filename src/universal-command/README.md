# SynOS Universal Command

AI-powered security tool orchestrator for SynOS.

## Features

-   **AI Tool Selection**: Intelligent tool recommendation based on target and scan mode
-   **Parallel Execution**: Run multiple security tools simultaneously
-   **Result Aggregation**: Combine and deduplicate findings from multiple tools
-   **Multiple Scan Modes**: Quick, Standard, Full, and Stealth scanning options

## Usage

```bash
# Quick scan
synos-universal scan 192.168.1.1 quick

# Full enumeration
synos-universal enumerate example.com

# Generate report
synos-universal report

# Show help
synos-universal help
```

## Scan Modes

-   **Quick**: Fast ping sweep + top ports
-   **Standard**: Common ports + service detection
-   **Full**: All ports + aggressive scanning
-   **Stealth**: Slow, evade IDS

## Integration

The universal command integrates with 500+ security tools from:

-   Kali Linux
-   ParrotOS
-   BlackArch
-   Custom SynOS tools

## License

MIT License - See LICENSE file for details.
