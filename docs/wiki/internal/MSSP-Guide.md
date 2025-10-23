# 🏢 MSSP Operations Guide

**For**: Managed Security Service Providers  
**Features**: Multi-tenant management, client portals, automation

---

## MSSP Features

### Multi-Tenant Architecture

```bash
# Create client tenant
synos-mssp tenant create \
  --name "Acme Corp" \
  --tier enterprise \
  --seats 50

# Assign users
synos-mssp user assign \
  --tenant acme-corp \
  --email user@acme.com \
  --role admin

# List tenants
synos-mssp tenant list
```

### Client Portal

Each client gets dedicated portal with:
- Dashboard with metrics
- Scan results
- Vulnerability reports
- Ticket system
- Billing integration

### Automated Scanning

```yaml
# /etc/synos/mssp/scan-schedule.yml
schedules:
  - tenant: acme-corp
    scan_type: full
    frequency: weekly
    day: sunday
    time: "02:00"
    
  - tenant: acme-corp
    scan_type: critical
    frequency: daily
    time: "03:00"
```

### Report Generation

```bash
# Generate monthly report
synos-mssp report generate \
  --tenant acme-corp \
  --month 2025-09 \
  --type executive \
  --format pdf \
  --email ceo@acme.com

# Automated delivery
synos-mssp report schedule \
  --tenant all \
  --frequency monthly \
  --day 1 \
  --template executive-summary
```

---

## Business Operations

### Client Onboarding

1. **Discovery Call**: Understand needs
2. **Proposal**: Scope and pricing
3. **Contract**: MSA and SOW
4. **Setup**: Create tenant, configure scans
5. **Kickoff**: Training and handoff

### Pricing Tiers

| Tier | Assets | Scans/Month | Support | Price |
|------|--------|-------------|---------|-------|
| **Starter** | 10 | 4 | Email | $500 |
| **Professional** | 50 | 8 | Phone | $2,000 |
| **Enterprise** | Unlimited | Unlimited | 24/7 | Custom |

### SLA Management

```bash
# Configure SLA
synos-mssp sla set \
  --tenant acme-corp \
  --response-time 2h \
  --resolution-time 24h \
  --uptime 99.9%

# Monitor compliance
synos-mssp sla status --tenant acme-corp
```

---

## Staff Management

```bash
# Assign analyst to tenant
synos-mssp staff assign \
  --analyst john.doe \
  --tenant acme-corp \
  --role primary

# Workload balancing
synos-mssp workload balance --auto
```

---

**For more**: contact mssp@synos.dev
