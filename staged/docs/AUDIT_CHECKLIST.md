# Regular Audit Checklist for SynapticOS

## Weekly/Monthly Review
- [ ] Check for secrets/credentials in codebase
- [ ] Run `scripts/security_audit.sh` and review results
- [ ] Update all dependencies and re-run audits
- [ ] Review `.gitignore` and `.env.example` for drift
- [ ] Review access controls and branch protection
- [ ] Review CI logs for failed security checks
- [ ] Review Dockerfiles and devcontainer for hardening
- [ ] Remove unused dependencies and extensions
- [ ] Document any exceptions or waivers

## Before Release
- [ ] All of the above
- [ ] All code and scripts signed
- [ ] All security scans pass
- [ ] All dependencies pinned
- [ ] All secrets managed via environment/secret manager
