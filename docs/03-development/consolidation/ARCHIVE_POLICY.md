# 📚 Archive Policy and Standards

**Document Version**: 1.0  
**Date**: September 17, 2025  
**Purpose**: Establish standards for archive directory management and configuration cleanup

## 🎯 Archive Directory Purpose

Archive directories serve as **documentation and historical reference repositories**. They should contain:

✅ **APPROPRIATE CONTENT**:

- Historical documentation
- Legacy project references
- Backup configurations for reference
- Discontinued workflow examples
- Research and development artifacts
- Version history snapshots

❌ **INAPPROPRIATE CONTENT**:

- Active configuration files
- Build system configurations (`.cargo/config.toml`, `Makefile`)
- Environment-specific settings
- API keys or credentials
- Active deployment configurations
- Current development dependencies

## 🔍 Configuration File Classification

### 🟢 Archive-Appropriate Files

- **Historical CI/CD workflows** (`.github/workflows/*.yml` from past versions)
- **Legacy Docker configurations** (old `docker-compose.yml` for reference)
- **Deprecated project files** (old `Cargo.toml` from previous versions)
- **Backup dashboard configs** (historical JSON configuration snapshots)
- **Research configurations** (experimental setups for reference)

### 🔴 Must be Relocated Files

- **Active security configs** (`enterprise_mssp.yaml`, `security.conf`)
- **Build system configs** (`.cargo/config.toml`, `rust-toolchain.toml`)
- **Environment configurations** (`development.env`, `production.yaml`)
- **API configurations** (service endpoints, integration configs)
- **Database configurations** (connection strings, schema configs)

## 🛠 Archive Cleanup Procedures

### 1. Discovery Phase

```bash
# Find configuration files in archives
find /path/to/archives -type f \( -name "*.toml" -o -name "*.yaml" -o -name "*.yml" -o -name "*.json" -o -name "*.conf" \)
```

### 2. Analysis Phase

For each configuration file:

1. **Assess Purpose**: Active vs. historical
2. **Check Dependencies**: Are any systems using this?
3. **Evaluate Content**: Contains active settings or just reference?
4. **Document Decision**: Why keep, move, or remove

### 3. Action Phase

- **RELOCATE**: Move active configs to appropriate directories
- **DOCUMENT**: Create analysis documentation for moved files
- **UPDATE**: Modify references and documentation
- **VALIDATE**: Test that systems still work after changes

## 📂 Recommended Directory Structure

```
/config/
├── active/           # Current configurations
├── security/         # Security-related configurations
├── templates/        # Configuration templates
└── archive/          # Historical references only

/docs/
├── archive/          # Archived documentation
└── configuration/    # Configuration documentation

/archive/
├── historical/       # Complete historical snapshots
└── deprecated/       # Deprecated but reference-worthy projects
```

## 🚨 Critical Rules

### Build System Protection

- **NEVER** keep `.cargo/config.toml` in archives
- **NEVER** keep active `Makefile` or build scripts in archives
- **NEVER** keep environment-specific toolchain configs in archives

### Security Protection

- **NEVER** keep active security configurations in archives
- **NEVER** keep API keys or credentials in archives
- **ALWAYS** sanitize configurations before archiving

### Documentation Requirements

- **ALWAYS** document why something is archived
- **ALWAYS** create relocation documentation for moved configs
- **ALWAYS** update references when moving configurations

## 🔄 Maintenance Schedule

### Monthly Review

- Scan for new configuration files in archives
- Verify no active configs have been accidentally archived
- Update documentation for any changes

### Quarterly Audit

- Full archive structure review
- Validate archive policy compliance
- Update policy based on lessons learned

### Annual Cleanup

- Remove truly obsolete archived content
- Consolidate redundant archive directories
- Archive current configurations as new historical references

## 📋 Archive Audit Checklist

- [ ] No `.cargo/config.toml` files in any archive directory
- [ ] No active security configurations in archives
- [ ] All archived configurations have documentation explaining purpose
- [ ] Archive directories contain only historical references
- [ ] All active configurations are in appropriate non-archive locations
- [ ] Archive README files accurately reflect contents
- [ ] No build system interference from archived configurations

## 🔧 Automation Opportunities

### Automated Validation

```bash
# Check for problematic files in archives
find /archives -name ".cargo" -type d -exec echo "WARNING: .cargo found in archive: {}" \;
find /archives -name "*.env" -exec echo "WARNING: Environment file in archive: {}" \;
```

### Automated Documentation

- Generate archive manifests
- Create configuration relocation reports
- Track archive policy compliance

## 📞 Escalation Procedures

### When in Doubt

1. **Document the finding** with full analysis
2. **Assess impact** of potential relocation
3. **Create backup** before making changes
4. **Test thoroughly** after any modifications
5. **Update documentation** to reflect decisions

### Review Required For

- Large configuration files (>100 lines)
- Files with external dependencies
- Configurations with security implications
- Build system or deployment configurations

---

**Policy Owner**: Development Team  
**Review Cycle**: Quarterly  
**Last Updated**: September 17, 2025  
**Next Review**: December 17, 2025
