# 🌐 SynOS Wiki - Documentation Hub

**Welcome to SynOS Documentation!**

This wiki contains comprehensive documentation organized by access level to protect proprietary business information while providing valuable public resources.

---

## 🔐 Documentation Structure

### 🟢 **Public Documentation** (You Are Here)

The files in this directory are **publicly available** and free for everyone:

-   **User Guides**: Quick start, installation, first steps
-   **Educational Content**: Learning paths, basic labs, curriculum integration
-   **Developer Docs**: Development guide, contributing, public APIs
-   **General Info**: Architecture overview, roadmap, distribution info

**Total**: 19 public pages • Perfect for beginners, students, and community members

👉 **[View Public Documentation Index](public/README.md)**

---

### 🟡 **Restricted Documentation** (Licensed Users)

Documentation for **paying customers** and **enterprise clients**:

-   **Deployment Guides**: Docker, Kubernetes
-   **Security Tools**: Complete 500+ tool catalog
-   **Professional Guides**: Penetration testing, advanced tutorials
-   **Technical References**: Build system, syscalls, error codes

**Total**: 9 restricted pages (~30KB) • Requires Professional or Enterprise license

📂 **Location**: `wiki/restricted/` (Git-crypt encryption + Unix permissions)  
🔐 **Security**: 4-layer protection (Unix permissions, Git-crypt, GPG keys, .gitattributes)  
📖 **Access Guide**: See [SECURITY.md](SECURITY.md) for setup and access instructions

---

### 🔴 **Internal Documentation** (Company Confidential)

Documentation for **internal employees** and **contractors** (NDA required):

-   **Business Operations**: MSSP guide, pricing, client management
-   **Proprietary Technology**: AI engine, custom kernel, security framework
-   **Advanced Techniques**: Exploitation, kernel development, red team ops
-   **Infrastructure**: Production deployment, cloud architecture

**Total**: 13 internal pages (~187KB) • Contains competitive advantages and trade secrets

🔒 **Location**: `wiki/internal/` (Git-crypt encryption + Unix permissions)  
🔐 **Security**: 4-layer protection (Unix permissions, Git-crypt, GPG keys, .gitattributes)  
📖 **Access Guide**: See [SECURITY.md](SECURITY.md) for setup and access instructions

---

## 📚 Available Public Pages

### 🚀 Getting Started (4 pages)

1. **[Quick-Start.md](Quick-Start.md)** - 5-minute quick start guide
2. **[Installation.md](Installation.md)** - Complete installation guide
3. **[First-Steps.md](First-Steps.md)** - Tutorial-style first steps
4. **[Getting-Started.md](Getting-Started.md)** - Comprehensive getting started (coming soon)

### 🎓 Educational Content

5. **[Educational Features](education/Educational-Features.md)** - Educational platform overview
6. **[Curriculum Integration](education/Curriculum-Integration.md)** - School integration guide
7. **[Lab Exercises](education/Lab-Exercises.md)** - 50+ hands-on labs
8. **[Certification & CTF Integration](education/Certification-CTF-Integration-Master.md)** - Complete certification roadmap
9. **[Learning Paths](education/learning-paths/)** - 4 structured specialization tracks
   - [Network Security](education/learning-paths/Network-Security.md)
   - [Web Security](education/learning-paths/Web-Security.md)
   - [AI Security](education/learning-paths/AI-Security.md)
   - [Malware Analysis](education/learning-paths/Malware-Analysis.md)

### 👨‍💻 Developer Documentation (3 pages)

12. **[Development-Guide.md](Development-Guide.md)** - Development environment setup
13. **[Contributing.md](Contributing.md)** - How to contribute to SynOS
14. **[API-Reference.md](API-Reference.md)** - Public API documentation

### 📖 General Information & Technical

10. **[Home.md](Home.md)** - Wiki homepage
11. **[Recent Updates](RECENT_UPDATES.md)** - Latest changes and improvements
12. **[Linux Distribution](technical/Linux-Distribution.md)** - Distribution information
13. **[Technical Documentation](technical/)** - Architecture and systems
14. **[Development Guides](guides/)** - How-to guides and tutorials
15. **[Security Documentation](security/)** - Access control and encryption

---

## 🎯 Quick Navigation by Role

### 👶 **New Users** (Start Here!)

1. Read [Quick-Start.md](Quick-Start.md) (5 minutes)
2. Follow [Installation.md](Installation.md) (30 minutes)
3. Complete [First-Steps.md](First-Steps.md) (1 hour)
4. Try a lab from [Lab-Exercises.md](Lab-Exercises.md)

### 🎓 **Students**

1. Review [Educational-Features.md](Educational-Features.md)
2. Choose a [learning path](#-educational-content-7-pages)
3. Work through basic labs systematically
4. Join the community (Discord/Forum coming soon)

### 👨‍🏫 **Educators**

1. Read [Curriculum-Integration.md](Curriculum-Integration.md)
2. Review available labs and learning paths
3. Contact education@synos.com for academic licenses
4. Get free licenses for educational institutions

### 👨‍💻 **Developers**

1. Setup: [Development-Guide.md](Development-Guide.md)
2. Contribute: [Contributing.md](Contributing.md)
3. APIs: [API-Reference.md](API-Reference.md)
4. Join us on GitHub: https://github.com/TLimoges33/Syn_OS

### 🔒 **Security Professionals** (Upgrade Required)

1. See what's available in public docs
2. Upgrade to **Professional** ($2,000/year) for:
    - 250 security tools
    - Advanced labs
    - Docker deployment
    - Email support
3. Or **Enterprise** (custom pricing) for full access

---

## � Recent Updates

**October 22, 2025** - Major architecture and security improvements:

-   ✅ AI subsystem reorganized into unified `src/ai/` structure
-   ✅ Root configuration files optimized (.editorconfig, .gitattributes, .gitignore)
-   ✅ Wiki security implemented (4-layer protection with Git-crypt + GPG)
-   ✅ Comprehensive security documentation added (SECURITY.md, SECURITY-QUICK-REF.md)
-   ✅ Automated setup and backup scripts created

**[See Full Update Details →](RECENT_UPDATES.md)**

---

## �📊 Documentation Statistics

### Public (Free)

-   **Pages**: 19
-   **Lines**: ~7,700
-   **Size**: ~200 KB
-   **Labs**: 15 beginner labs
-   **Learning Paths**: 4 complete tracks
-   **Tools**: ~50 common security tools

### Restricted (Licensed Users)

-   **Pages**: 8
-   **Lines**: ~4,500
-   **Size**: ~140 KB
-   **Tools**: 250-500 (tier dependent)
-   **Advanced Labs**: 35 additional labs
-   **Support**: Email or 24/7 phone

### Internal (Employees Only)

-   **Pages**: 11
-   **Lines**: ~8,000
-   **Size**: ~250 KB
-   **Classification**: Company Confidential
-   **Contains**: Pricing, proprietary tech, business ops

### **Total Documentation**: 38 pages • 20,200 lines • 590 KB

---

## 🌟 Why This Structure?

### Protecting Competitive Advantages

We've structured our documentation to:

✅ **Provide value** to the community (free, public docs)
✅ **Reward customers** (advanced docs for licensed users)
✅ **Protect trade secrets** (internal docs for employees)

This ensures:

-   Community members get great learning resources
-   Paying customers get professional-grade documentation
-   Our business IP and competitive advantages remain secure

### What's Public vs. Private

**Public (🟢)**:

-   Basic tutorials, educational content, contribution guides
-   Enough to learn and get started
-   Community building focus

**Restricted (🟡)**:

-   Advanced features, professional tools, deployment guides
-   Value for paying customers
-   Professional use cases

**Internal (🔴)**:

-   Pricing, business processes, MSSP operations
-   Proprietary technology (AI engine, kernel internals)
-   Advanced exploitation techniques that could be weaponized

---

## 🎁 Free vs. Paid Content

### ✅ Free Tier (Current)

-   ✅ 19 public documentation pages
-   ✅ Basic tutorials and 15 labs
-   ✅ 4 complete learning paths
-   ✅ ~50 common security tools
-   ✅ Community support
-   ✅ Public API documentation

### 💰 Professional Tier ($2,000/year)

-   ✅ **Everything in Free**
-   ✅ 250 security tools (+200)
-   ✅ 50 total labs (+35 advanced)
-   ✅ Docker deployment guide
-   ✅ Professional pentesting guide
-   ✅ Email support (24-48h response)
-   ✅ Quarterly documentation updates

### 🏢 Enterprise Tier (Custom Pricing)

-   ✅ **Everything in Professional**
-   ✅ 500+ security tools (full catalog)
-   ✅ Kubernetes deployment
-   ✅ Build system access
-   ✅ System call reference
-   ✅ Error code database
-   ✅ 24/7 phone + email support
-   ✅ Dedicated account manager
-   ✅ Custom integrations
-   ✅ Early access to features

**Upgrade**: https://synos.com/pricing or contact sales@synos.com

---

## 🤝 Community & Contribution

### Get Involved

-   **GitHub**: https://github.com/TLimoges33/Syn_OS
-   **Issues**: Report bugs and request features
-   **Pull Requests**: Contribute code and documentation
-   **Discussions**: Share ideas and ask questions

### Contribution Areas

We welcome contributions in:

-   📝 Documentation improvements
-   🐛 Bug reports and fixes
-   ✨ Feature suggestions
-   🔧 Code contributions
-   🎨 UI/UX improvements
-   🌍 Translations
-   🎓 Educational content

**Start Contributing**: [Contributing.md](Contributing.md)

---

## 📞 Contact & Support

### General Inquiries

-   **Website**: https://synos.com
-   **Email**: info@synos.com
-   **Community**: community@synos.com

### Specific Departments

-   **Sales/Licensing**: sales@synos.com
-   **Education**: education@synos.com
-   **Technical Support**: support@synos.com (paid tiers)
-   **Documentation**: docs@synos.com

### Customer Portal

-   **Login**: https://portal.synos.com (licensed users)
-   **Status**: https://status.synos.com
-   **Knowledge Base**: https://kb.synos.com

---

## ❓ Frequently Asked Questions

**Q: Why is some documentation not public?**
A: We need to protect our competitive advantages, proprietary technology, and business operations while still providing valuable free resources to the community.

**Q: What is WaterLands?**
A: WaterLands is the codename for our public beta. It represents publicly accessible content (water) vs. deeper licensed features (ocean).

**Q: Can I access restricted docs?**
A: Yes! Upgrade to Professional or Enterprise tier at https://synos.com/pricing

**Q: How do I get employee access to internal docs?**
A: Internal docs are only for SynOS employees and contractors. Contact HR if you need access.

**Q: Is the public documentation enough to use SynOS?**
A: Absolutely! The public docs provide everything you need to install, use, and learn SynOS basics. Licensed tiers add advanced features and professional tools.

**Q: Can I contribute to documentation?**
A: Yes! Public documentation accepts community contributions. See [Contributing.md](Contributing.md)

**Q: What's the difference between this and Kali Linux?**
A: SynOS is an independent project with unique features like AI-powered security, custom kernel, and educational integration. Our documentation structure also protects business IP while serving the community.

---

## 🎉 Get Started Now!

**New to SynOS?** Start here: [Quick-Start.md](Quick-Start.md)

**Ready to learn?** Choose a learning path: [Educational Content](#-educational-content-7-pages)

**Want to contribute?** Read this: [Contributing.md](Contributing.md)

**Need advanced features?** Upgrade: https://synos.com/pricing

---

## 📋 Documentation Versions

| Version             | Date        | Status      | Notes                        |
| ------------------- | ----------- | ----------- | ---------------------------- |
| **WaterLands v1.0** | Oct 4, 2025 | 🟢 Current  | Public beta, 19 public pages |
| Internal v1.0       | Oct 4, 2025 | 🔴 Internal | 11 confidential pages        |
| Restricted v1.0     | Oct 4, 2025 | 🟡 Licensed | 8 restricted pages           |

---

**Last Updated**: October 22, 2025
**Version**: WaterLands Public Beta v1.0
**Classification**: 🟢 PUBLIC
**Total Pages**: 44 (19 public, 9 restricted, 13 internal, 3 security docs)

---

## 📰 What's New?

See [RECENT_UPDATES.md](RECENT_UPDATES.md) for the latest improvements to SynOS wiki and documentation.

---

**🌊 Welcome to WaterLands - The Surface of SynOS Documentation 🌊**

_Dive deeper with a license, or explore the depths with an employee badge._
