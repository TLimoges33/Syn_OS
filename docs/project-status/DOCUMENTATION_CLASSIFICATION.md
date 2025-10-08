# 📋 Documentation Classification Guide

**Last Updated**: October 4, 2025  
**Purpose**: Define what documentation is internal-only vs. public-facing

---

## 🔐 Classification Levels

### 🔴 **INTERNAL ONLY** (Company Confidential)

Documentation containing proprietary business information, pricing, internal processes, or competitive advantages.

**Distribution**: Internal employees, contractors under NDA only  
**Wiki Location**: `/wiki/internal/` (to be created)  
**Public Beta**: ❌ **EXCLUDED**

### 🟡 **PARTNER/CLIENT ACCESS** (Restricted)

Documentation for paying customers, partners, or those under commercial agreements.

**Distribution**: Licensed users, enterprise clients, certified partners  
**Wiki Location**: `/wiki/restricted/` (to be created)  
**Public Beta**: ❌ **EXCLUDED**

### 🟢 **PUBLIC** (Open Source)

Documentation suitable for public release, community building, and open-source contributions.

**Distribution**: Everyone  
**Wiki Location**: `/wiki/public/` or root `/wiki/`  
**Public Beta**: ✅ **INCLUDED** (WaterLands public beta)

---

## 📂 Current Wiki Classification

### 🔴 INTERNAL ONLY (11 pages)

**Business & Operations** (4 pages):

1. ❌ **MSSP-Guide.md** - Contains:

    - Pricing tiers ($500, $2,000, custom)
    - Multi-tenant architecture (competitive advantage)
    - Client onboarding process
    - SLA management strategies
    - Revenue models

2. ❌ **Red-Team-Operations.md** - Contains:

    - Internal red team methodologies
    - Attack techniques we use internally
    - Infrastructure penetration strategies
    - Could be used against us

3. ❌ **Production-Deployment.md** - Contains:

    - Internal infrastructure details
    - Security hardening specifics
    - Database configurations
    - Could reveal attack surface

4. ❌ **Cloud-Deployment.md** - Contains:
    - Our cloud architecture
    - Terraform configurations
    - Infrastructure patterns
    - Cost optimization (business intelligence)

**Advanced Technical** (7 pages): 5. ❌ **Advanced-Exploitation.md** - Contains:

-   ro-day development process
-   vanced exploitation techniques
-   rnel exploitation methods
-   uld be weaponized

6. ❌ **Kernel-Development.md** - Contains:

    - Custom kernel internals
    - Driver development secrets
    - Kernel security mechanisms
    - Reverse engineering aid

7. ❌ **AI-Model-Training.md** - Contains:

    - Proprietary AI training methods
    - Model architectures
    - Training datasets
    - Competitive advantage

8. ❌ **Custom-Tool-Development.md** - Contains:

    - Tool development framework
    - Integration APIs (internal)
    - Plugin architecture
    - Extensibility secrets

9. ❌ **AI-Consciousness-Engine.md** - Contains:

    - Proprietary AI architecture (54,218 lines)
    - Neural network designs
    - Core competitive technology
    - Patent-pending innovations

10. ❌ **Custom-Kernel.md** - Contains:

    - Kernel architecture internals
    - Security implementation details
    - Performance optimizations
    - Core technology

11. ❌ **Security-Framework.md** - Contains:
    - MAC/RBAC implementation details
    - Threat detection algorithms
    - ML security models
    - Core security architecture

### 🟡 PARTNER/CLIENT ACCESS (8 pages)

**For Licensed Users & Enterprise Clients**:

1. ⚠️ **Docker-Guide.md** - Enterprise deployment
2. ⚠️ **Kubernetes-Deployment.md** - Production orchestration
3. ⚠️ **Penetration-Testing.md** - Professional pentesting guide
4. ⚠️ **Security-Tools.md** - Full 500+ tool catalog
5. ⚠️ **Testing-Guide.md** - Internal testing frameworks
6. ⚠️ **Build-System.md** - Build system internals
7. ⚠️ **Syscall-Reference.md** - System call documentation
8. ⚠️ **Error-Codes.md** - Error code internals

### 🟢 PUBLIC (19 pages)

**User Guides** (4 pages):

1. ✅ **Quick-Start.md**
2. ✅ **Installation.md**
3. ✅ **First-Steps.md**
4. ✅ **Getting-Started.md**

**Developer Documentation** (3 pages): 5. ✅ **Development-Guide.md** 6. ✅ **Contributing.md** 7. ✅ **API-Reference.md** (public APIs only)

**Educational Content** (7 pages): 8. ✅ **Educational-Features.md** 9. ✅ **Curriculum-Integration.md** 10. ✅ **Lab-Exercises.md** (basic labs only) 11. ✅ **Learning-Path-Network-Security.md** 12. ✅ **Learning-Path-Web-Security.md** 13. ✅ **Learning-Path-AI-Security.md** 14. ✅ **Learning-Path-Malware-Analysis.md**

**General** (5 pages): 15. ✅ **Home.md** 16. ✅ **Architecture-Overview.md** (high-level only) 17. ✅ **ROADMAP.md** 18. ✅ **README.md** 19. ✅ **Linux-Distribution.md** (user-facing info only)

---

## 🎯 Recommendations

### Immediate Actions

1. **Create Directory Structure**:

```bash
wiki/
├── public/          # Public beta content (WaterLands)
├── restricted/      # Client/partner access
├── internal/        # Company confidential
└── README.md        # Public landing page
```

2. **Move Internal Docs**:

```bash
# Move MSSP guide and other sensitive docs
mv wiki/MSSP-Guide.md wiki/internal/
mv wiki/Advanced-Exploitation.md wiki/internal/
mv wiki/AI-Consciousness-Engine.md wiki/internal/
# ... etc
```

3. **Create Public Versions**:
    - Create sanitized versions of key docs
    - Remove pricing, internal processes, proprietary tech
    - Keep educational/community value

### WaterLands Public Beta Content

For the public beta, include ONLY:

**Core User Documentation**:

-   Quick start guide
-   Installation instructions
-   Basic usage tutorials
-   Community contribution guide

**Educational Content** (sanitized):

-   Basic learning paths
-   Introductory labs (10-15 beginner labs)
-   Educational feature overview
-   Curriculum integration (high-level)

**Developer Docs** (limited):

-   Public API reference only
-   Plugin development basics
-   Community contribution guide
-   Internal build system
-   Core architecture internals

**What to EXCLUDE from Public Beta**:

-   MSSP business operations
-   Pricing information
-   Advanced exploitation techniques
-   Proprietary AI architecture
-   Custom kernel internals
-   Security framework details
-   Production deployment specifics
-   Enterprise features
-   Red team methodologies
-   Advanced pentesting guides
-   500+ tool catalog (show 50-100 basic tools)

---

## 📝 Access Control Matrix

| Document Type    | Public Beta   | Registered Users | Enterprise     | Internal |
| ---------------- | ------------- | ---------------- | -------------- | -------- |
| Quick Start      | ✅            | ✅               | ✅             | ✅       |
| Basic Labs       | ✅            | ✅               | ✅             | ✅       |
| Learning Paths   | ✅ (basic)    | ✅ (full)        | ✅             | ✅       |
| Advanced Labs    | ❌            | ✅               | ✅             | ✅       |
| Security Tools   | ❌ (50 tools) | ✅ (250 tools)   | ✅ (500 tools) | ✅       |
| Pentesting       | ❌            | ⚠️ (basic)       | ✅             | ✅       |
| Red Team         | ❌            | ❌               | ⚠️ (limited)   | ✅       |
| MSSP Guide       | ❌            | ❌               | ❌             | ✅       |
| AI Engine        | ❌            | ❌               | ⚠️ (usage)     | ✅       |
| Kernel Internals | ❌            | ❌               | ⚠️ (limited)   | ✅       |
| Deployment       | ❌            | ⚠️ (basic)       | ✅             | ✅       |
| Pricing          | ❌            | ❌               | ❌             | ✅       |

---

## 🔒 Security Measures

### Document Protection

1. **Internal Wiki** (internal employees only):

    - Requires VPN access
    - Employee authentication
    - Audit logging of access
    - Watermarked PDFs for prints

2. **Partner Portal** (licensed users):

    - Login required
    - License validation
    - Terms of service acceptance
    - NDA enforcement

3. **Public Wiki** (WaterLands beta):
    - No authentication
    - Limited content
    - Community-focused
    - No sensitive information

### Information Sanitization

When creating public versions:

**Remove**:

-   Specific pricing numbers
-   Client names/examples
-   Internal tool names
-   Infrastructure details
-   Performance metrics
-   Proprietary algorithms
-   Business processes
-   Revenue models

**Replace with**:

-   "Contact sales for pricing"
-   Generic examples
-   Public tool names
-   High-level architecture
-   General capabilities
-   Algorithm descriptions
-   User workflows
-   Value propositions

---

## 📊 Content Strategy

### Internal Wiki (Current)

**Audience**: Employees, contractors (NDA)  
**Purpose**: Complete technical documentation  
**Content**: Everything (38 pages, 16,178 lines)  
**Status**: ✅ Complete

### Partner/Client Portal (To Create)

**Audience**: Paying customers, enterprise licenses  
**Purpose**: Full product documentation for users  
**Content**: ~25 pages (exclude internal business/R&D)  
**Status**: ⏳ To be created

### Public Wiki (WaterLands Beta)

**Audience**: General public, community, students  
**Purpose**: Onboarding, education, community building  
**Content**: ~15-20 sanitized pages  
**Status**: ⏳ To be created from internal docs

---

## ✅ Action Items

### Phase 1: Immediate (This Week)

-   ] Create directory structure (`public/`, `restricted/`, `internal/`)
-   ] Move sensitive docs to `internal/`
-   ] Add classification headers to all documents
-   ] Update README with access information

### Phase 2: Short Term (Next 2 Weeks)

-   ] Create sanitized public versions of key docs
-   ] Review each document for sensitive info
-   ] Set up access controls (VPN, authentication)
-   ] Create WaterLands public beta wiki

### Phase 3: Long Term (Next Month)

-   ] Create partner portal documentation
-   ] Implement watermarking for sensitive docs
-   ] Set up audit logging
-   ] Create documentation governance policy

---

## 🎓 Guidelines for Future Docs

When creating new documentation, ask:

1. **Does this contain pricing?** → Internal only
2. **Does this reveal competitive advantage?** → Internal only
3. **Does this contain client information?** → Internal only
4. **Could this be weaponized against us?** → Internal only
5. **Does this help the community learn?** → Can be public
6. **Does this help users use the product?** → Partner/client access
7. **Is this general education content?** → Can be public

**Default classification**: 🔴 **INTERNAL ONLY** (can always open up later)

---

## 📞 Questions?

For classification questions, contact:

-   Security Team\*\*: <security@synos.com>
-   Legal Team\*\*: <legal@synos.com>
-   Documentation Lead\*\*: <docs@synos.com>

**Remember**: It's easier to keep something private than to un-publish it!

---

**Classification Guide Version**: 1.0  
**Last Review**: October 4, 2025  
**Next Review**: November 4, 2025
