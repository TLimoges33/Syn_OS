#!/usr/bin/env python3
"""
Documentation Organization Script
Organizes loose documentation files in docs/ into appropriate subdirectories
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# Base paths
DOCS_DIR = Path(__file__).parent.parent.parent / "docs"
SCRIPT_DIR = Path(__file__).parent

# Organization rules
ORGANIZATION_MAP = {
    # 03-build: Build system documentation
    "03-build": [
        "BUILD_SCRIPT_V2.2_DEBUG_FIXES.md",
        "BUILD_SCRIPT_V2.2_ENHANCEMENTS.md",
        "BUILD_SCRIPT_V2.2_TEST_RESULTS.md",
        "BUILD_SYSTEM_V2.2_COMPLETE.md",
        "ISO_BUILD_QUICK_REFERENCE.md",
        "ISO_BUILD_READINESS_AUDIT_2025-10-23.md",
        "NMAP_FIX_AND_BUILD_READY.md",
        "PIPE_EXIT_CODE_FIX.md",
        "SET_E_PIPELINE_FIX.md",
        "TIMEOUT_REMOVAL_COMPLETE.md",
        "ULTIMATE_BUILDS_ANALYSIS.md",
    ],
    # 01-getting-started: Quick reference and start guides
    "01-getting-started": [
        "QUICK_REFERENCE.md",
        "QUICK_REFERENCE_2025-10-23.md",
        "QUICK_START.md",
    ],
    # 06-project-status/build-reports: Build-related completion reports
    "06-project-status/build-reports": [
        "COMPREHENSIVE_BUILD_AUDIT_COMPLETE.md",
        "FINAL_10X_AUDIT_ALL_BUGS_ELIMINATED.md",
        "ULTIMATE_ENHANCEMENT_SUMMARY.md",
    ],
    # 06-project-status/recent: Phase completion summaries
    "06-project-status/recent": [
        "PHASE2_COMPLETION_SUMMARY.md",
        "PHASE3_COMPLETION_SUMMARY.md",
        "PHASE4_COMPLETION_SUMMARY.md",
        "PHASE5_COMPLETION_SUMMARY.md",
        "PHASE6_ARCHIVAL_PROGRESS.md",
        "PHASE6_COMPLETION_SUMMARY.md",
        "PHASE6_FINAL_COMPLETION_REPORT.md",
        "PHASE6_NEXT_STEPS_EXECUTION_REPORT.md",
        "PHASE6_SESSION_SUMMARY.md",
        "PHASE6_STAGE4_5_COMPLETION.md",
        "STAGE6_INTEGRATION_TEST_REPORT.md",
        "STAGE7_PERFORMANCE_BENCHMARKS.md",
        "STAGE8_FINAL_CLEANUP_CHECKLIST.md",
        "STAGE9_RELEASE_PREPARATION.md",
        "RELEASE_v2.0.0_SUMMARY.md",
        "V2.0.0_RELEASE_COMPLETE.md",
    ],
    # 07-audits: All audit and analysis documents
    "07-audits": [
        "ENVIRONMENT_AUDIT_2025-10-23.md",
        "ENVIRONMENT_FIX_SUMMARY_2025-10-23.md",
        "PERFORMANCE_BENCHMARKS_2025-10-23.md",
        "REORGANIZATION_SUMMARY_2025-10-23.md",
        "SCRIPTS_ARCHITECTURE_ANALYSIS.md",
        "WARNING_FIXES_2025-10-23.md",
    ],
    # 04-development: Development process and fixes
    "04-development": [
        "CONSOLIDATION_CHECKLIST.md",
        "KERNEL_REORGANIZATION_2025-10-23.md",
        "KERNEL_REORGANIZATION_STATUS.txt",
        "LEGACY_SCRIPTS_CATALOG.md",
        "OPTIMIZATION_CHEAT_SHEET.txt",
        "OPTIMIZATION_SUMMARY.txt",
        "ROOT_CAUSE_FIX_REPOSITORY_CONFLICTS.md",
        "SCRIPT_CONSOLIDATION_PROGRESS.md",
        "SCRIPTS_OPTIMIZATION_READY.md",
        "SCRIPTS_ORGANIZATION_COMPLETE.md",
        "SMART_PACKAGE_INSTALLATION.md",
        "V1.5-V1.8_COMPILATION_FIXES_OCT22_2025.md",
    ],
}

# Files to keep in root
KEEP_IN_ROOT = ["README.md"]


def create_report_header():
    """Create header for organization report"""
    return f"""# Documentation Organization Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
This report shows the reorganization of loose documentation files in docs/
into the existing subdirectory structure.

"""


def organize_files(dry_run=False):
    """
    Organize documentation files according to ORGANIZATION_MAP

    Args:
        dry_run: If True, only show what would be done without moving files
    """
    report_lines = [create_report_header()]
    total_moved = 0
    errors = []

    # Process each category
    for target_dir, files in ORGANIZATION_MAP.items():
        moved_in_category = 0
        target_path = DOCS_DIR / target_dir

        report_lines.append(f"## {target_dir}/")
        report_lines.append("")

        for filename in files:
            source_path = DOCS_DIR / filename

            if not source_path.exists():
                errors.append(f"⚠ File not found: {filename}")
                continue

            if source_path.is_dir():
                errors.append(f"⚠ Skipping directory: {filename}")
                continue

            # Create target directory if needed
            if not dry_run:
                target_path.mkdir(parents=True, exist_ok=True)

            dest_path = target_path / filename

            # Check for existing file
            if dest_path.exists():
                errors.append(
                    f"⚠ File already exists at destination: {target_dir}/{filename}"
                )
                continue

            # Move the file
            action = "Would move" if dry_run else "Moved"
            report_lines.append(f"- ✓ {action}: `{filename}`")

            if not dry_run:
                try:
                    shutil.move(str(source_path), str(dest_path))
                    moved_in_category += 1
                    total_moved += 1
                except Exception as e:
                    errors.append(f"✗ Error moving {filename}: {e}")
            else:
                moved_in_category += 1
                total_moved += 1

        report_lines.append(f"\n**Files in category: {moved_in_category}**\n")

    # Add errors section if any
    if errors:
        report_lines.append("\n## Warnings and Errors\n")
        for error in errors:
            report_lines.append(error)
        report_lines.append("")

    # Add summary
    report_lines.insert(3, f"**Total files organized: {total_moved}**")
    report_lines.insert(4, f"**Total errors: {len(errors)}**")
    report_lines.insert(5, f"**Mode: {'DRY RUN' if dry_run else 'LIVE'}**\n")

    # Files remaining in root
    report_lines.append("\n## Files Remaining in Root\n")
    remaining = []
    for item in DOCS_DIR.iterdir():
        if item.is_file() and (item.suffix in [".md", ".txt"]):
            if item.name not in KEEP_IN_ROOT:
                remaining.append(item.name)

    if not dry_run:
        for filename in remaining:
            report_lines.append(f"- ⚠ {filename}")
    report_lines.append(f"\n**Total remaining: {len(remaining)}**\n")

    return "\n".join(report_lines), total_moved, len(errors)


def main():
    """Main execution"""
    import sys

    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    print("=" * 70)
    print("Documentation Organization Script")
    print("=" * 70)

    if dry_run:
        print("\n🔍 DRY RUN MODE - No files will be moved\n")
    else:
        print("\n⚠ LIVE MODE - Files will be moved\n")
        response = input("Continue? (yes/no): ").strip().lower()
        if response not in ["yes", "y"]:
            print("Aborted.")
            return

    print("\nOrganizing documentation files...\n")

    # Run organization
    report, total_moved, total_errors = organize_files(dry_run=dry_run)

    # Save report
    report_filename = f"DOCS_ORGANIZATION_REPORT_{'DRY_RUN_' if dry_run else ''}{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path = DOCS_DIR / report_filename

    with open(report_path, "w") as f:
        f.write(report)

    # Print summary
    print("\n" + "=" * 70)
    print(f"✓ Organization {'simulation' if dry_run else 'complete'}!")
    print("=" * 70)
    print(f"Files organized: {total_moved}")
    print(f"Errors: {total_errors}")
    print(f"Report saved: docs/{report_filename}")

    if dry_run:
        print("\nRun without --dry-run to execute the organization.")

    print("\n")


if __name__ == "__main__":
    main()
