# 📁 Wiki Reorganization Plan

**Created:** October 22, 2025  
**Status:** Proposed → Implementation

## 🎯 Goals

1. **Better organization** - Group related content together
2. **Easier navigation** - Clear hierarchical structure
3. **Accurate information** - Fact-checked against codebase
4. **Eliminate duplicates** - Remove redundant files

---

## 📊 Current Structure Analysis

### Current Files (23 markdown files + 4 directories)

**Root Level (17 files):**

-   Certification-CTF-Integration-Master.md
-   Curriculum-Integration.md
-   Educational-Curriculum-Master.md
-   Educational-Features.md
-   Home.md
-   Lab-Exercises.md
-   Learning-Path-AI-Security.md
-   Learning-Path-Malware-Analysis.md
-   Learning-Path-Network-Security.md
-   Learning-Path-Web-Security.md
-   Linux-Distribution.md
-   README.md
-   README2.md (DUPLICATE - TO DELETE)
-   RECENT_UPDATES.md
-   SECURITY-QUICK-REF.md
-   SECURITY.md
-   SECURITY_QUICK_REFERENCE.md (DUPLICATE - TO DELETE)

**Directories:**

-   internal/ (13 files - encrypted)
-   restricted/ (9 files - encrypted)
-   public/ (1 README)
-   security/ (1 file)
-   wiki-updates/ (2 files)

### Issues Identified

1. **Duplicates:**

    - `README2.md` (temporary file)
    - `SECURITY_QUICK_REFERENCE.md` vs `SECURITY-QUICK-REF.md`

2. **Poor Organization:**

    - Educational files scattered (4 files at root)
    - Learning paths not grouped (4 separate files)
    - Security docs mixed with content

3. **Missing Structure:**
    - No guides/ directory
    - No getting-started/ directory
    - No technical/ directory

---

## 🎨 Proposed New Structure

```
docs/wiki/
├── README.md                          # Main wiki index
├── Home.md                            # Wiki homepage
├── RECENT_UPDATES.md                  # Change log
│
├── getting-started/                   # 🟢 PUBLIC - New users
│   ├── README.md
│   ├── Quick-Start.md
│   ├── Installation.md
│   ├── First-Steps.md
│   └── FAQ.md
│
├── education/                         # 🟢 PUBLIC - Learning content
│   ├── README.md
│   ├── Educational-Features.md
│   ├── Educational-Curriculum-Master.md
│   ├── Curriculum-Integration.md
│   ├── Lab-Exercises.md
│   ├── Certification-CTF-Integration-Master.md
│   └── learning-paths/
│       ├── README.md
│       ├── Network-Security.md
│       ├── Web-Security.md
│       ├── AI-Security.md
│       └── Malware-Analysis.md
│
├── technical/                         # 🟢 PUBLIC - Technical docs
│   ├── README.md
│   ├── Architecture-Overview.md
│   ├── Linux-Distribution.md
│   ├── AI-Architecture.md (NEW)
│   └── Build-System-Overview.md (NEW)
│
├── guides/                            # 🟢 PUBLIC - How-to guides
│   ├── README.md
│   ├── Development-Guide.md
│   ├── Contributing.md
│   └── API-Reference.md
│
├── security/                          # 🔐 SECURITY - Access control docs
│   ├── README.md
│   ├── SECURITY.md
│   ├── SECURITY-QUICK-REF.md
│   └── Access-Control-Guide.md (NEW)
│
├── internal/                          # 🔴 HIGHLY RESTRICTED
│   ├── README.md
│   ├── .gitattributes
│   └── [13 encrypted files...]
│
├── restricted/                        # 🟡 LICENSED
│   ├── README.md
│   ├── .gitattributes
│   └── [9 encrypted files...]
│
└── public/                            # 🟢 PUBLIC (optional subdirectory)
    └── README.md
```

---

## ✅ Implementation Checklist

### Phase 1: Cleanup (Immediate)

-   [ ] Delete `README2.md` (duplicate/temp file)
-   [ ] Delete `SECURITY_QUICK_REFERENCE.md` (duplicate)
-   [ ] Delete empty/outdated directories

### Phase 2: Create New Structure

-   [ ] Create `getting-started/` directory
-   [ ] Create `education/` directory
-   [ ] Create `education/learning-paths/` subdirectory
-   [ ] Create `technical/` directory
-   [ ] Create `guides/` directory

### Phase 3: Move Files

-   [ ] Move 4 learning path files → `education/learning-paths/`
-   [ ] Move 3 educational files → `education/`
-   [ ] Move `Linux-Distribution.md` → `technical/`
-   [ ] Move security docs → `security/` (consolidate)

### Phase 4: Create New Files

-   [ ] Create `getting-started/README.md`
-   [ ] Create `education/README.md`
-   [ ] Create `education/learning-paths/README.md`
-   [ ] Create `technical/README.md`
-   [ ] Create `technical/AI-Architecture.md` (link to src/ai/README.md)
-   [ ] Create `guides/README.md`

### Phase 5: Update References

-   [ ] Update `README.md` with new structure
-   [ ] Update `Home.md` navigation links
-   [ ] Update internal file cross-references
-   [ ] Update security documentation

### Phase 6: Fact-Check Content

-   [ ] Verify ALFRED status (314 lines, foundation complete)
-   [ ] Verify AI runtime status (3094 lines total)
-   [ ] Verify TFLite status (no stubs remaining)
-   [ ] Update completion percentages
-   [ ] Verify file paths in documentation

---

## 📝 Fact-Check Corrections Needed

### ALFRED Voice Assistant

**Current Claims:**

-   "90% complete" (in RECENT_UPDATES.md)
-   "v1.1 In Progress" (in Home.md)

**Actual Status (from codebase):**

-   314 lines of Python code
-   Foundation complete (v1.0)
-   Basic wake word, STT, TTS working
-   Command execution functional
-   **Accurate:** ~30% complete (foundation only)

**Correction:**

-   ALFRED is at v1.0 Foundation (30% complete)
-   v1.4 goal: Full audio experience
-   v1.1 targeting: Voice enhancements

### AI Runtime

**Current Claims:**

-   "75% complete" for TFLite (in RECENT_UPDATES.md)
-   "30% complete" for ONNX
-   "25% complete" for PyTorch

**Actual Status (from codebase):**

-   3094 total lines across runtime
-   TFLite: NO STUBS (production FFI implementation)
-   ONNX: 4 stubs remaining
-   PyTorch: 3 stubs remaining
-   **Accurate:** TFLite is 100% functional (no stubs)

**Correction:**

-   TFLite: 100% complete (production ready)
-   ONNX: ~85% complete (4 stubs)
-   PyTorch: ~75% complete (3 stubs)

### Security Status

**Current Claims:**

-   4-layer wiki security implemented ✅
-   13 internal files, 9 restricted files ✅
-   Git-crypt encryption setup ✅

**Actual Status:**

-   All security claims are accurate!
-   Scripts created and functional

---

## 🚀 Benefits of Reorganization

### For Users

-   **Faster navigation** - Find what you need quickly
-   **Clear learning paths** - Education content together
-   **Better onboarding** - Dedicated getting-started section

### For Developers

-   **Logical grouping** - Related content together
-   **Easier maintenance** - Clear file locations
-   **Better scalability** - Room to grow

### For Documentation

-   **Reduced duplication** - Single source of truth
-   **Better cross-referencing** - Clear hierarchy
-   **Accurate information** - Fact-checked against code

---

## 📅 Timeline

**Phase 1 (Cleanup):** 10 minutes  
**Phase 2 (Create Structure):** 15 minutes  
**Phase 3 (Move Files):** 20 minutes  
**Phase 4 (Create New Files):** 30 minutes  
**Phase 5 (Update References):** 30 minutes  
**Phase 6 (Fact-Check):** 20 minutes

**Total Estimated Time:** ~2 hours

---

## ⚠️ Considerations

### Git History

-   Use `git mv` to preserve file history
-   Commit each phase separately
-   Document all moves in commit messages

### Encryption

-   Do NOT move internal/ or restricted/ files
-   Maintain .gitattributes encryption rules
-   Keep security structure intact

### Links

-   Update all relative paths
-   Test all internal links
-   Verify external references

---

## 📞 Approval Required

This reorganization will:

-   ✅ Improve wiki usability
-   ✅ Fix inaccurate completion percentages
-   ✅ Remove duplicate files
-   ✅ Create better structure

**Proceed with implementation?** (Y/N)
