#!/bin/bash
# Network Segmentation Rules for SynapticsOS
# This script implements security zones using iptables

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Applying SynapticsOS Network Segmentation Rules${NC}"

# Flush existing rules
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X

# Default policies - Deny all
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

# Define network zones
ZONE1_CRITICAL="172.20.1.0/24"    # Vault, API Gateway, n8n
ZONE2_CORE="172.20.2.0/24"        # Context Engine, Knowledge DB
ZONE3_APP="172.20.3.0/24"         # JaceAI, Speechify, Descript
ZONE4_DMZ="172.20.4.0/24"         # External connectors

# Create custom chains for each zone
iptables -N ZONE1_IN
iptables -N ZONE1_OUT
iptables -N ZONE2_IN
iptables -N ZONE2_OUT
iptables -N ZONE3_IN
iptables -N ZONE3_OUT
iptables -N ZONE4_IN
iptables -N ZONE4_OUT

# Zone 1 (Critical) Rules
# Only allow specific services
iptables -A ZONE1_IN -p tcp --dport 8200 -j ACCEPT  # Vault
iptables -A ZONE1_IN -p tcp --dport 8000 -j ACCEPT  # Kong Proxy
iptables -A ZONE1_IN -p tcp --dport 8443 -j ACCEPT  # Kong Proxy SSL
iptables -A ZONE1_IN -p tcp --dport 5678 -j ACCEPT  # n8n
iptables -A ZONE1_IN -p tcp --dport 9090 -j ACCEPT  # Prometheus
iptables -A ZONE1_IN -p tcp --dport 3000 -j ACCEPT  # Grafana
iptables -A ZONE1_IN -p tcp --dport 3100 -j ACCEPT  # Loki
iptables -A ZONE1_IN -j LOG --log-prefix "ZONE1_DROP: "
iptables -A ZONE1_IN -j DROP

# Zone 1 can communicate with all zones (API Gateway)
iptables -A ZONE1_OUT -d $ZONE2_CORE -j ACCEPT
iptables -A ZONE1_OUT -d $ZONE3_APP -j ACCEPT
iptables -A ZONE1_OUT -d $ZONE4_DMZ -j ACCEPT

# Zone 2 (Core) Rules
# Accept from Zone 1 only
iptables -A ZONE2_IN -s $ZONE1_CRITICAL -j ACCEPT
iptables -A ZONE2_IN -j LOG --log-prefix "ZONE2_DROP: "
iptables -A ZONE2_IN -j DROP

# Zone 2 can respond to Zone 1 and communicate within zone
iptables -A ZONE2_OUT -d $ZONE1_CRITICAL -j ACCEPT
iptables -A ZONE2_OUT -d $ZONE2_CORE -j ACCEPT
iptables -A ZONE2_OUT -j LOG --log-prefix "ZONE2_OUT_DROP: "
iptables -A ZONE2_OUT -j DROP

# Zone 3 (App) Rules
# Accept from Zone 1 only
iptables -A ZONE3_IN -s $ZONE1_CRITICAL -j ACCEPT
iptables -A ZONE3_IN -j LOG --log-prefix "ZONE3_DROP: "
iptables -A ZONE3_IN -j DROP

# Zone 3 can respond to Zone 1 and communicate with Zone 2
iptables -A ZONE3_OUT -d $ZONE1_CRITICAL -j ACCEPT
iptables -A ZONE3_OUT -d $ZONE2_CORE -j ACCEPT
iptables -A ZONE3_OUT -j LOG --log-prefix "ZONE3_OUT_DROP: "
iptables -A ZONE3_OUT -j DROP

# Zone 4 (DMZ) Rules
# Accept from Zone 1 only, allow outbound to internet
iptables -A ZONE4_IN -s $ZONE1_CRITICAL -j ACCEPT
iptables -A ZONE4_IN -j LOG --log-prefix "ZONE4_DROP: "
iptables -A ZONE4_IN -j DROP

# Zone 4 can respond to Zone 1 and access internet
iptables -A ZONE4_OUT -d $ZONE1_CRITICAL -j ACCEPT
iptables -A ZONE4_OUT -j ACCEPT  # Allow internet access

# Apply zone rules to interfaces
# Assuming Docker bridge interfaces follow pattern br_zone*
iptables -A INPUT -i br_zone1 -s $ZONE1_CRITICAL -j ZONE1_IN
iptables -A OUTPUT -o br_zone1 -d $ZONE1_CRITICAL -j ZONE1_OUT
iptables -A FORWARD -i br_zone1 -s $ZONE1_CRITICAL -j ZONE1_OUT
iptables -A FORWARD -o br_zone1 -d $ZONE1_CRITICAL -j ZONE1_IN

iptables -A INPUT -i br_zone2 -s $ZONE2_CORE -j ZONE2_IN
iptables -A OUTPUT -o br_zone2 -d $ZONE2_CORE -j ZONE2_OUT
iptables -A FORWARD -i br_zone2 -s $ZONE2_CORE -j ZONE2_OUT
iptables -A FORWARD -o br_zone2 -d $ZONE2_CORE -j ZONE2_IN

iptables -A INPUT -i br_zone3 -s $ZONE3_APP -j ZONE3_IN
iptables -A OUTPUT -o br_zone3 -d $ZONE3_APP -j ZONE3_OUT
iptables -A FORWARD -i br_zone3 -s $ZONE3_APP -j ZONE3_OUT
iptables -A FORWARD -o br_zone3 -d $ZONE3_APP -j ZONE3_IN

iptables -A INPUT -i br_zone4 -s $ZONE4_DMZ -j ZONE4_IN
iptables -A OUTPUT -o br_zone4 -d $ZONE4_DMZ -j ZONE4_OUT
iptables -A FORWARD -i br_zone4 -s $ZONE4_DMZ -j ZONE4_OUT
iptables -A FORWARD -o br_zone4 -d $ZONE4_DMZ -j ZONE4_IN

# Rate limiting rules
iptables -A INPUT -p tcp --dport 8000 -m limit --limit 100/second --limit-burst 200 -j ACCEPT
iptables -A INPUT -p tcp --dport 8443 -m limit --limit 100/second --limit-burst 200 -j ACCEPT

# DDoS protection
iptables -A INPUT -p tcp --syn -m limit --limit 1/s --limit-burst 3 -j ACCEPT
iptables -A INPUT -p tcp --syn -j DROP

# Port scanning protection
iptables -N PORT_SCAN
iptables -A PORT_SCAN -p tcp --tcp-flags SYN,ACK,FIN,RST RST -m limit --limit 1/s --limit-burst 2 -j RETURN
iptables -A PORT_SCAN -j DROP

# Log all dropped packets (rate limited)
iptables -A INPUT -m limit --limit 5/min -j LOG --log-prefix "IPT_INPUT_DROP: " --log-level 4
iptables -A FORWARD -m limit --limit 5/min -j LOG --log-prefix "IPT_FORWARD_DROP: " --log-level 4

# Save rules
if command -v iptables-save >/dev/null 2>&1; then
    iptables-save > /etc/iptables/rules.v4
    echo -e "${GREEN}Rules saved to /etc/iptables/rules.v4${NC}"
fi

# Enable IP forwarding for Docker
echo 1 > /proc/sys/net/ipv4/ip_forward

# Enable SYN cookies
echo 1 > /proc/sys/net/ipv4/tcp_syncookies

# Disable ICMP redirects
echo 0 > /proc/sys/net/ipv4/conf/all/accept_redirects
echo 0 > /proc/sys/net/ipv6/conf/all/accept_redirects

# Enable reverse path filtering
echo 1 > /proc/sys/net/ipv4/conf/all/rp_filter

echo -e "${GREEN}Network segmentation rules applied successfully!${NC}"
echo -e "${YELLOW}Note: These rules will be lost on reboot unless persisted${NC}"