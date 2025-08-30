# Branch archive and cleanup summary (2025-08-28)

This document records the branch cleanup performed to adopt a simple 3-branch model while keeping pull requests targeting main.

Scope
- Keep PR base as main
- Baseline branches to keep: main, develop, staging
- Archive historical pointers and prune redundant heads that equal main
- Keep all active PR heads intact

Archived/removed
- cleaned-history-20250828: removed from origin (historical pointer) — matched main at time of cleanup
- pre-rewrite-main: removed from origin (historical pointer) — matched main at time of cleanup
- extract/src-4850b78a: removed (identical to main; no PR)
- extract/docs-4850b78a: removed (identical to main; no PR)

Remaining origin branches (snapshot)
- main
- develop
- staging
- dev-team
- master
- audit/cleaned-history-docs
- chore/devcontainer-image
- chore/restore-protection-and-audit
- pr/devcontainer-image
- pr/restore-protection-and-audit
- pr/wip-manual-edits
- extract/devcontainer-dockerfile
- extract/protection-jsons
- extract/scripts-4850b78a

Open PRs (heads preserved)
- #25 master → main
- #26 audit/cleaned-history-docs → main
- #27 pr/restore-protection-and-audit → main
- #28 pr/devcontainer-image → main
- #29 pr/wip-manual-edits → main
- #30 extract/devcontainer-dockerfile → main
- #31 extract/protection-jsons → main
- #32 extract/scripts-4850b78a → main

Notes
- develop and staging exist for future workflows, but PRs are currently based on main per instruction.
- If you want archive tags created (e.g., `archive/cleaned-history-20250828`, `archive/pre-rewrite-main`) pointing to the last known SHAs, say “create archive tags” and they’ll be added.

Archive tags created (2025-08-28)
- archive/cleaned-history-20250828
	- tag object: be136e0a59b62babe38067587094b5e5cb3edd02
	- peeled commit (^{}): 441266a6a3f1c51336200adaa90b6b34ef7749a9 (matches origin/main at cleanup time)
- archive/pre-rewrite-main
	- tag object: 4b2b906827c5ec40c4b66a7f97935eb07ad20031
	- peeled commit (^{}): 441266a6a3f1c51336200adaa90b6b34ef7749a9 (matches origin/main at cleanup time)
